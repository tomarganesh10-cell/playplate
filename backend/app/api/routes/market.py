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


def _data_status(broker: BrokerBase) -> dict:
    """Describe where the numbers came from, and why if they aren't real.

    Call this *after* fetching, so a data source that turned out to be
    unusable mid-request (expired token, missing Kite market-data
    subscription) is reported as synthetic rather than as live.
    """
    synthetic = True
    if settings.trading_mode == TradingMode.SIMULATION:
        reason = "simulation mode"
    elif settings.trading_mode == TradingMode.PAPER:
        from app.broker.paper import PaperBroker

        connected = isinstance(broker, PaperBroker) and broker._data is not None
        degraded = getattr(broker, "data_degraded", None)
        if not connected:
            reason = "Zerodha not connected — connect from the Broker page"
        elif degraded:
            reason = f"Zerodha connected but data unavailable ({degraded})"
        else:
            synthetic, reason = False, None
    else:
        synthetic = not broker.is_session_valid()
        reason = None if not synthetic else "no valid Zerodha session"

    return {
        "data_source": "synthetic (NOT real market data)" if synthetic else "zerodha",
        "data_source_reason": reason,
    }


@router.get("/indices")
def indices(
    broker: BrokerBase = Depends(get_broker_dep),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
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

    return {
        "market_session": market_hours.session_state(),
        **_data_status(broker),
        "rates": rates,
    }


@router.get("/movers")
def movers(
    broker: BrokerBase = Depends(get_broker_dep),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """Top gainers/losers across the default NSE universe (Zerodha-style board)."""
    try:
        rows = broker.quotes_with_change(DEFAULT_UNIVERSE)
    except Exception:  # noqa: BLE001 — degrade to synthetic instead of erroring
        from app.broker.paper import SimulationBroker

        rows = SimulationBroker().quotes_with_change(DEFAULT_UNIVERSE)

    rows.sort(key=lambda r: r["change_pct"], reverse=True)
    return {
        "market_session": market_hours.session_state(),
        **_data_status(broker),
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
