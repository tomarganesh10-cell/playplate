"""Market data: live index rates (NIFTY, SENSEX, BANKNIFTY, FINNIFTY).

Real values require a valid Zerodha session; in simulation/paper-without-
session mode the response is clearly flagged as synthetic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.config import TradingMode, settings
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.engine import market_hours
from app.logging_config import get_logger
from app.models.user import User
from app.services.news import get_market_news
from app.services.scanner_service import DEFAULT_UNIVERSE

log = get_logger("api.market")

router = APIRouter()

DEFAULT_INDICES = ["NIFTY", "SENSEX", "BANKNIFTY"]


def _is_synthetic(broker: BrokerBase) -> bool:
    """True unless a real Zerodha data source is actually behind the broker."""
    if settings.trading_mode == TradingMode.SIMULATION:
        return True
    if settings.trading_mode == TradingMode.PAPER:
        from app.broker.paper import PaperBroker

        return not (isinstance(broker, PaperBroker) and broker._data is not None)
    return not broker.is_session_valid()


@router.get("/indices")
def indices(
    broker: BrokerBase = Depends(get_broker_dep),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    # Data is "real" only when a live Zerodha data source is actually behind
    # the active broker (live mode, or paper mode with a valid Kite session).
    synthetic = _is_synthetic(broker)

    rates = []
    for name in DEFAULT_INDICES:
        try:
            q = broker.get_index_quote(name)
            rates.append({
                "index": name,
                "last_price": round(q.last_price, 2),
                "as_of": q.timestamp.isoformat(),
            })
        except Exception as exc:  # noqa: BLE001 — degrade per-index, never 500
            # Kite SDK raises its own exception types (token/permission/network),
            # not just BrokerError. Surface the reason instead of failing the page.
            log.warning("index quote failed for %s: %s", name, exc)
            rates.append({"index": name, "error": str(exc)})
    if all("error" in r for r in rates) and not synthetic:
        # Real source configured but every quote failed (expired token, missing
        # data permission, network) — make the degradation explicit.
        synthetic = True

    return {
        "market_session": market_hours.session_state(),
        "data_source": "synthetic (NOT real market data)" if synthetic else "zerodha",
        "rates": rates,
    }


@router.get("/movers")
def movers(
    broker: BrokerBase = Depends(get_broker_dep),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """Top gainers/losers across the default NSE universe (Zerodha-style board)."""
    synthetic = _is_synthetic(broker)
    try:
        rows = broker.quotes_with_change(DEFAULT_UNIVERSE)
    except Exception:  # noqa: BLE001 — degrade to synthetic instead of erroring
        from app.broker.paper import SimulationBroker

        rows = SimulationBroker().quotes_with_change(DEFAULT_UNIVERSE)
        synthetic = True

    rows.sort(key=lambda r: r["change_pct"], reverse=True)
    return {
        "market_session": market_hours.session_state(),
        "data_source": "synthetic (NOT real market data)" if synthetic else "zerodha",
        "gainers": rows[:6],
        "losers": rows[-6:][::-1],
    }


@router.get("/news")
def news(_: User = Depends(get_current_user)) -> dict:
    """Latest market headlines from public RSS feeds (informational only)."""
    return {
        "note": "Headlines from public RSS feeds. Informational only — not investment advice.",
        "items": get_market_news(limit=24),
    }
