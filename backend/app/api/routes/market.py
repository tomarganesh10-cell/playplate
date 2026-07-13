"""Market data: live index rates (NIFTY, SENSEX, BANKNIFTY, FINNIFTY).

Real values require a valid Zerodha session; in simulation/paper-without-
session mode the response is clearly flagged as synthetic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase, BrokerError
from app.config import TradingMode, settings
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.engine import market_hours
from app.models.user import User

router = APIRouter()

DEFAULT_INDICES = ["NIFTY", "SENSEX", "BANKNIFTY"]


@router.get("/indices")
def indices(
    broker: BrokerBase = Depends(get_broker_dep),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    # Data is "real" only when a live Zerodha data source is actually behind
    # the active broker (live mode, or paper mode with a valid Kite session).
    synthetic = settings.trading_mode == TradingMode.SIMULATION or not broker.is_session_valid()
    if settings.trading_mode == TradingMode.PAPER:
        from app.broker.paper import PaperBroker

        synthetic = not (isinstance(broker, PaperBroker) and broker._data is not None)

    rates = []
    for name in DEFAULT_INDICES:
        try:
            q = broker.get_index_quote(name)
            rates.append({
                "index": name,
                "last_price": round(q.last_price, 2),
                "as_of": q.timestamp.isoformat(),
            })
        except BrokerError as exc:
            rates.append({"index": name, "error": str(exc)})

    return {
        "market_session": market_hours.session_state(),
        "data_source": "synthetic (NOT real market data)" if synthetic else "zerodha",
        "rates": rates,
    }
