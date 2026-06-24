"""Broker session management (Zerodha Kite login flow)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.broker import session as broker_session
from app.broker.base import BrokerError
from app.config import settings
from app.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.services import audit

router = APIRouter()


class RequestTokenIn(BaseModel):
    request_token: str


@router.get("/login-url")
def login_url(_: User = Depends(require_admin)) -> dict:
    """Return the Kite login URL the admin must visit to obtain a request_token."""
    if not settings.kite_api_key:
        raise HTTPException(status_code=400, detail="KITE_API_KEY is not configured")
    return {
        "login_url": f"https://kite.zerodha.com/connect/login?v=3&api_key={settings.kite_api_key}",
        "note": "After login, Kite redirects to your registered URL with ?request_token=...",
    }


@router.post("/session")
def create_session(
    payload: RequestTokenIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """Exchange a request_token for an access token and store it encrypted."""
    try:
        result = broker_session.exchange_request_token(payload.request_token)
        sess = broker_session.store_session(db, result["access_token"], result.get("user_id"))
    except BrokerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit.record(
        db, "broker_session_created", actor_id=admin.id, actor_email=admin.email,
        ip_address=request.client.host if request.client else None,
        detail={"broker": "zerodha", "kite_user_id": result.get("user_id")},
    )
    return {"status": "ok", "issued_at": sess.issued_at.isoformat(), "valid": sess.is_valid}


@router.get("/status")
def status(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    token = broker_session.load_access_token(db)
    return {
        "trading_mode": settings.trading_mode.value,
        "live_trading_armed": settings.live_trading_armed,
        "session_present": token is not None,
    }
