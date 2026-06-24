"""Live signals: trigger a scan and list stored signals."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.models.signal import Signal
from app.models.user import User
from app.schemas.trading import SignalOut
from app.services.scanner_service import run_scan

router = APIRouter()


@router.post("/scan")
def scan(
    timeframe: str = Query("15m"),
    symbols: str | None = Query(None, description="Comma-separated; default universe if omitted"),
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    _: User = Depends(get_current_user),
) -> dict:
    sym_list = [s.strip().upper() for s in symbols.split(",")] if symbols else None
    return run_scan(db, broker, symbols=sym_list, timeframe=timeframe)


@router.get("/", response_model=list[SignalOut])
def list_signals(
    status: str = Query("active"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Signal]:
    stmt = select(Signal)
    if status != "all":
        stmt = stmt.where(Signal.status == status)
    stmt = stmt.order_by(Signal.created_at.desc(), Signal.rank.asc()).limit(limit)
    return list(db.execute(stmt).scalars())


@router.get("/{signal_id}", response_model=SignalOut)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Signal:
    from fastapi import HTTPException

    sig = db.get(Signal, signal_id)
    if not sig:
        raise HTTPException(status_code=404, detail="Signal not found")
    return sig
