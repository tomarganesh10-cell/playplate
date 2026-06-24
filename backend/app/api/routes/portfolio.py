"""Portfolio snapshot: positions, exposure, PnL."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.config import settings
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.metrics import daily_pnl
from app.models.trade import Position
from app.models.user import User
from app.risk.manager import RiskManager
from app.schemas.trading import PortfolioOut, PositionOut

router = APIRouter()


@router.get("/", response_model=PortfolioOut)
def portfolio(
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    _: User = Depends(get_current_user),
) -> PortfolioOut:
    positions = list(
        db.execute(select(Position).where(Position.quantity != 0)).scalars()
    )
    # Refresh last price + unrealised PnL from the broker quote.
    unrealised = 0.0
    invested = 0.0
    for pos in positions:
        try:
            pos.last_price = broker.get_quote(pos.symbol).last_price
        except Exception:  # noqa: BLE001
            pass
        direction = 1 if pos.quantity > 0 else -1
        pos.unrealised_pnl = round(
            (pos.last_price - pos.avg_price) * direction * abs(pos.quantity), 2
        )
        unrealised += pos.unrealised_pnl
        invested += abs(pos.quantity) * pos.avg_price
    db.commit()

    rm = RiskManager(db)
    realised = rm.realised_pnl_today()
    daily_pnl.set(realised + unrealised)

    return PortfolioOut(
        capital=settings.account_capital,
        cash=round(settings.account_capital - invested, 2),
        invested=round(invested, 2),
        open_positions=[PositionOut.model_validate(p) for p in positions],
        realised_pnl_today=round(realised, 2),
        unrealised_pnl=round(unrealised, 2),
        exposure=round(rm.current_exposure(), 2),
    )
