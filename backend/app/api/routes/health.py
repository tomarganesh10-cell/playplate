"""Health, readiness and Prometheus metrics endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.engine import market_hours
from app.risk.circuit_breaker import breaker

router = APIRouter()


@router.get("/health/live")
def liveness() -> dict:
    """Process is up. Used by Docker/k8s liveness probe."""
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)) -> dict:
    """Dependencies reachable. Used by readiness probe and deploy validation."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "trading_mode": settings.trading_mode.value,
        "live_trading_armed": settings.live_trading_armed,
        "market_session": market_hours.session_state(),
        "circuit_breaker_tripped": breaker.tripped,
    }


@router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
