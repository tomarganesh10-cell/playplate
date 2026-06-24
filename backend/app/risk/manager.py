"""Risk management: position sizing, exposure/loss limits, trade validation.

Every order must pass `RiskManager.validate_order` before it can be routed to
any broker (paper or live). The manager is deliberately conservative: when in
doubt, it rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.logging_config import get_logger
from app.models.trade import Position, Trade
from app.risk.circuit_breaker import breaker

log = get_logger("risk.manager")


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    suggested_quantity: int | None = None


class RiskManager:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.capital = settings.account_capital
        self.max_daily_loss = settings.risk_max_daily_loss
        self.max_open_positions = settings.risk_max_open_positions
        self.max_exposure = settings.risk_max_exposure
        self.per_trade_pct = settings.risk_per_trade_pct
        self.max_drawdown_pct = settings.risk_max_drawdown_pct

    # ---- sizing ----------------------------------------------------------
    def position_size(self, entry: float, stop_loss: float) -> int:
        """Risk a fixed % of capital on the distance to stop. Returns qty (>=0)."""
        risk_per_share = abs(entry - stop_loss)
        if risk_per_share <= 0:
            return 0
        capital_at_risk = self.capital * (self.per_trade_pct / 100.0)
        qty = int(capital_at_risk // risk_per_share)
        # Never let a single position exceed the exposure cap.
        max_by_exposure = int(self.max_exposure // entry) if entry > 0 else 0
        return max(min(qty, max_by_exposure), 0)

    # ---- aggregates ------------------------------------------------------
    def realised_pnl_today(self) -> float:
        from datetime import datetime

        start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        total = self.db.execute(
            select(func.coalesce(func.sum(Trade.pnl), 0.0)).where(
                Trade.status == "closed", Trade.closed_at >= start
            )
        ).scalar_one()
        return float(total)

    def open_position_count(self) -> int:
        return int(
            self.db.execute(
                select(func.count()).select_from(Position).where(Position.quantity != 0)
            ).scalar_one()
        )

    def current_exposure(self) -> float:
        total = self.db.execute(
            select(
                func.coalesce(func.sum(func.abs(Position.quantity) * Position.last_price), 0.0)
            )
        ).scalar_one()
        return float(total)

    # ---- gatekeeper ------------------------------------------------------
    def check_circuit(self) -> RiskDecision | None:
        """Evaluate loss/drawdown thresholds and trip the breaker if needed."""
        pnl = self.realised_pnl_today()
        if pnl <= -abs(self.max_daily_loss):
            breaker.trip(f"Daily loss limit hit ({pnl:.0f} <= -{self.max_daily_loss:.0f})")
        drawdown_pct = (-pnl / self.capital * 100.0) if self.capital else 0.0
        if drawdown_pct >= self.max_drawdown_pct:
            breaker.trip(f"Max drawdown breached ({drawdown_pct:.1f}%)")
        if breaker.tripped:
            return RiskDecision(False, f"Circuit breaker active: {breaker.reason}")
        return None

    def validate_order(
        self, symbol: str, side: str, quantity: int, entry: float, stop_loss: float | None
    ) -> RiskDecision:
        tripped = self.check_circuit()
        if tripped:
            return tripped

        if quantity <= 0:
            return RiskDecision(False, "Quantity must be positive")

        if self.open_position_count() >= self.max_open_positions:
            return RiskDecision(
                False, f"Max open positions reached ({self.max_open_positions})"
            )

        order_value = quantity * entry
        if self.current_exposure() + order_value > self.max_exposure:
            suggested = self.position_size(entry, stop_loss) if stop_loss else None
            return RiskDecision(
                False,
                f"Exposure cap exceeded (cap {self.max_exposure:.0f})",
                suggested_quantity=suggested,
            )

        if stop_loss is not None:
            sized = self.position_size(entry, stop_loss)
            if quantity > sized and sized > 0:
                return RiskDecision(
                    False,
                    f"Quantity {quantity} exceeds risk-based size {sized}",
                    suggested_quantity=sized,
                )

        return RiskDecision(True, "approved")
