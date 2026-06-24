"""Performance analytics + AI reports."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import reports
from app.backtest.metrics import summarise_trades
from app.database import get_db
from app.deps import get_current_user
from app.models.trade import Trade
from app.models.user import User
from app.schemas.trading import PerformanceOut

router = APIRouter()


@router.get("/", response_model=PerformanceOut)
def performance(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PerformanceOut:
    since = datetime.now(UTC) - timedelta(days=days)
    trades = list(
        db.execute(
            select(Trade).where(Trade.status == "closed", Trade.closed_at >= since)
            .order_by(Trade.closed_at.asc())
        ).scalars()
    )
    stats = summarise_trades([t.pnl for t in trades])
    return PerformanceOut(
        total_trades=stats["total_trades"],
        win_rate=round(stats["win_rate"], 4),
        total_pnl=round(stats["total_pnl"], 2),
        avg_win=round(stats["avg_win"], 2),
        avg_loss=round(stats["avg_loss"], 2),
        profit_factor=round(stats["profit_factor"], 2) if stats["profit_factor"] != float("inf") else 999.0,
        sharpe_ratio=round(stats["sharpe_ratio"], 3),
        max_drawdown_pct=round(stats["max_drawdown_pct"], 2),
        period_start=trades[0].closed_at if trades else None,
        period_end=trades[-1].closed_at if trades else None,
    )


@router.get("/report/daily")
def daily(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    return {"report": reports.daily_report(db)}


@router.get("/report/weekly")
def weekly(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    return {"report": reports.weekly_report(db)}
