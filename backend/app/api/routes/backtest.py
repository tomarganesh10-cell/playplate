"""Backtesting endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backtest.engine import BacktestConfig, run_backtest
from app.broker.base import BrokerBase
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/run")
def run(
    symbol: str = Query(..., description="NSE symbol, e.g. RELIANCE"),
    timeframe: str = Query("15m"),
    days: int = Query(120, ge=10, le=730),
    min_score: float = Query(60.0, ge=0, le=100),
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    _: User = Depends(get_current_user),
) -> dict:
    df = broker.historical_ohlcv(symbol.upper(), timeframe, days=days)
    config = BacktestConfig(timeframe=timeframe, min_score=min_score)
    result = run_backtest(symbol.upper(), df, config)
    return {
        "symbol": result.symbol,
        "timeframe": timeframe,
        "stats": result.stats,
        "trades": result.trades,
        "equity_curve": result.equity_curve,
        "disclaimer": (
            "Backtested results are hypothetical, computed on historical data, "
            "and do NOT guarantee or imply future performance."
        ),
    }
