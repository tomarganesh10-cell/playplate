"""Daily and weekly performance reports + watchlist generation."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.client import get_ai
from app.backtest.metrics import summarise_trades
from app.engine.scanner import ScanResult
from app.models.trade import Trade

_SYSTEM = (
    "You are a trading performance analyst. Summarise results factually and "
    "highlight process improvements. Never guarantee future returns. Always "
    "include a brief risk note."
)
_CAVEAT = "⚠️ Past performance does not guarantee future results."


def _closed_trades(db: Session, since: datetime) -> list[Trade]:
    return list(
        db.execute(
            select(Trade).where(Trade.status == "closed", Trade.closed_at >= since)
        ).scalars()
    )


def _report(db: Session, since: datetime, label: str) -> str:
    trades = _closed_trades(db, since)
    stats = summarise_trades([t.pnl for t in trades])
    base = (
        f"{label} report ({since.date()} → {datetime.now(UTC).date()}):\n"
        f"Trades: {stats['total_trades']}, Win rate: {stats['win_rate']:.0%}, "
        f"Net PnL: ₹{stats['total_pnl']:.0f}, Profit factor: {stats['profit_factor']:.2f}, "
        f"Max drawdown: {stats['max_drawdown_pct']:.1f}%."
    )
    ai = get_ai()
    if not ai.enabled or not trades:
        return f"{base}\n{_CAVEAT}"
    detail = "\n".join(
        f"{t.symbol} {t.side} pnl={t.pnl:.0f}" for t in trades[:40]
    )
    out = ai.complete(_SYSTEM, f"{base}\nTrade log:\n{detail}\n\nWrite a 4-6 sentence review.", 500)
    return f"{out}\n\n{_CAVEAT}" if out else f"{base}\n{_CAVEAT}"


def daily_report(db: Session) -> str:
    since = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    return _report(db, since, "Daily")


def weekly_report(db: Session) -> str:
    since = datetime.now(UTC) - timedelta(days=7)
    return _report(db, since, "Weekly")


def generate_watchlist(ranked: list[tuple[int, ScanResult, float]], limit: int = 10) -> list[dict]:
    """Distil ranked signals into a compact watchlist payload for the UI/alerts."""
    watch = []
    for rank, r, conf in ranked[:limit]:
        watch.append(
            {
                "rank": rank,
                "symbol": r.symbol,
                "side": r.side,
                "entry": r.entry,
                "stop_loss": r.stop_loss,
                "target": r.target,
                "risk_reward": r.risk_reward,
                "confidence": conf,
            }
        )
    return watch
