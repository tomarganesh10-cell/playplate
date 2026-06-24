"""Order placement and trade history."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.core.rate_limit import rate_limit
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.metrics import orders_total
from app.models.trade import Position, Trade
from app.models.user import User
from app.notifications import telegram
from app.schemas.trading import OrderRequest, OrderResult, TradeOut
from app.services import audit
from app.services.trading import execute_order

router = APIRouter()


@router.post("/order", response_model=OrderResult)
def place_order(
    req: OrderRequest,
    request: Request,
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    user: User = Depends(get_current_user),
    _: None = Depends(rate_limit),
) -> OrderResult:
    return execute_order(
        db, broker, req,
        actor_id=user.id, actor_email=user.email,
        ip=request.client.host if request.client else None,
    )


@router.post("/{trade_id}/close", response_model=OrderResult)
def close_trade(
    trade_id: int,
    request: Request,
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    user: User = Depends(get_current_user),
) -> OrderResult:
    trade = db.get(Trade, trade_id)
    if not trade or trade.status != "open":
        raise HTTPException(status_code=404, detail="Open trade not found")

    exit_side = "SELL" if trade.side == "BUY" else "BUY"
    ack = broker.place_order(trade.symbol, exit_side, trade.quantity)
    if not ack.accepted:
        return OrderResult(accepted=False, mode=trade.mode, message=ack.message)

    fill = ack.avg_price or trade.entry_price
    direction = 1 if trade.side == "BUY" else -1
    trade.exit_price = fill
    trade.pnl = round((fill - trade.entry_price) * direction * trade.quantity - trade.fees, 2)
    trade.status = "closed"
    trade.closed_at = datetime.now(UTC)

    pos = db.execute(select(Position).where(Position.symbol == trade.symbol)).scalar_one_or_none()
    if pos:
        pos.quantity += trade.quantity if exit_side == "BUY" else -trade.quantity
        pos.last_price = fill
    db.commit()

    orders_total.labels(mode=trade.mode, side=exit_side, status="filled").inc()
    audit.record(
        db, "trade_closed", actor_id=user.id, actor_email=user.email,
        target=trade.symbol, detail={"trade_id": trade.id, "pnl": trade.pnl},
    )
    telegram.notify_exit(trade.symbol, trade.quantity, fill, trade.pnl, trade.mode)
    return OrderResult(
        accepted=True, mode=trade.mode, broker_order_id=ack.broker_order_id,
        message="closed", trade_id=trade.id,
    )


@router.get("/", response_model=list[TradeOut])
def list_trades(
    status: str = Query("all"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Trade]:
    stmt = select(Trade)
    if status != "all":
        stmt = stmt.where(Trade.status == status)
    stmt = stmt.order_by(Trade.opened_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars())
