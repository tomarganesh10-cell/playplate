"""Order execution service.

This is the single chokepoint through which *every* order flows. It enforces,
in order:
  1. Circuit breaker / risk validation (RiskManager).
  2. Live-trading safety gate (mode armed + per-order confirmation token).
  3. Broker routing (paper/sim/live via the broker factory).
  4. Trade persistence, position update, audit log and notification.
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.config import settings
from app.logging_config import get_logger
from app.metrics import open_positions, orders_total
from app.models.trade import Position, Trade
from app.notifications import telegram
from app.risk.manager import RiskManager
from app.schemas.trading import OrderRequest, OrderResult
from app.services import audit

log = get_logger("services.trading")

# In-memory store of confirmation tokens issued for pending live orders.
_pending_confirmations: dict[str, dict] = {}


def request_confirmation(req: OrderRequest) -> str:
    """Issue a one-time token the client must echo back to execute a live order."""
    token = secrets.token_urlsafe(16)
    _pending_confirmations[token] = {
        "symbol": req.symbol,
        "side": req.side,
        "quantity": req.quantity,
        "issued_at": datetime.now(UTC),
    }
    return token


def _confirmation_valid(req: OrderRequest) -> bool:
    if not req.confirm_token:
        return False
    record = _pending_confirmations.get(req.confirm_token)
    if not record:
        return False
    matches = (
        record["symbol"] == req.symbol
        and record["side"] == req.side
        and record["quantity"] == req.quantity
    )
    if matches:
        _pending_confirmations.pop(req.confirm_token, None)  # one-time use
    return matches


def _update_position(db: Session, trade: Trade, fill_price: float) -> None:
    pos = db.execute(select(Position).where(Position.symbol == trade.symbol)).scalar_one_or_none()
    signed = trade.quantity if trade.side == "BUY" else -trade.quantity
    if pos is None:
        pos = Position(symbol=trade.symbol, quantity=0, avg_price=0.0)
        db.add(pos)
    # Weighted average price when increasing exposure in the same direction.
    new_qty = pos.quantity + signed
    if pos.quantity == 0 or (pos.quantity > 0) == (signed > 0):
        total_cost = pos.avg_price * abs(pos.quantity) + fill_price * abs(signed)
        pos.avg_price = total_cost / abs(new_qty) if new_qty != 0 else 0.0
    pos.quantity = new_qty
    pos.last_price = fill_price
    pos.updated_at = datetime.now(UTC)
    db.flush()
    open_positions.set(
        db.execute(select(Position).where(Position.quantity != 0)).scalars().all().__len__()
    )


def execute_order(
    db: Session,
    broker: BrokerBase,
    req: OrderRequest,
    *,
    actor_id: int | None = None,
    actor_email: str | None = None,
    ip: str | None = None,
) -> OrderResult:
    mode = settings.trading_mode.value
    rm = RiskManager(db)

    quote = broker.get_quote(req.symbol)
    entry = req.limit_price or quote.last_price

    decision = rm.validate_order(req.symbol, req.side, req.quantity, entry, req.stop_loss)
    if not decision.approved:
        orders_total.labels(mode=mode, side=req.side, status="rejected_risk").inc()
        audit.record(
            db, "order_rejected", actor_id=actor_id, actor_email=actor_email, ip_address=ip,
            target=req.symbol, detail={"reason": decision.reason, "req": req.model_dump()},
        )
        return OrderResult(
            accepted=False, mode=mode,
            message=f"Risk check failed: {decision.reason}"
            + (f" (suggested qty {decision.suggested_quantity})" if decision.suggested_quantity else ""),
        )

    # Live safety gate.
    if broker.is_live:
        if not settings.live_trading_armed:
            return OrderResult(accepted=False, mode=mode, message="Live trading not armed.")
        if settings.require_order_confirmation and not _confirmation_valid(req):
            token = request_confirmation(req)
            return OrderResult(
                accepted=False, mode=mode,
                message=(
                    "Confirmation required for live order. Re-submit with this "
                    f"confirm_token within the session: {token}"
                ),
            )

    ack = broker.place_order(
        req.symbol, req.side, req.quantity, req.order_type, req.limit_price
    )
    if not ack.accepted:
        orders_total.labels(mode=mode, side=req.side, status="rejected_broker").inc()
        return OrderResult(accepted=False, mode=mode, message=ack.message)

    fill = ack.avg_price or entry
    trade = Trade(
        signal_id=req.signal_id,
        symbol=req.symbol,
        side=req.side,
        mode=mode,
        quantity=req.quantity,
        entry_price=fill,
        stop_loss=req.stop_loss,
        target=req.target,
        status="open",
        broker_order_id=ack.broker_order_id,
    )
    db.add(trade)
    db.flush()
    _update_position(db, trade, fill)
    db.commit()
    db.refresh(trade)

    orders_total.labels(mode=mode, side=req.side, status="filled").inc()
    audit.record(
        db, "order_filled", actor_id=actor_id, actor_email=actor_email, ip_address=ip,
        target=req.symbol,
        detail={"trade_id": trade.id, "fill": fill, "qty": req.quantity, "mode": mode},
    )
    telegram.notify_entry(req.symbol, req.side, req.quantity, fill, mode)

    return OrderResult(
        accepted=True, mode=mode, broker_order_id=ack.broker_order_id,
        message=ack.message, trade_id=trade.id,
    )
