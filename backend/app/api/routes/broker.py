"""Broker session management (Zerodha Kite login flow)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.broker import session as broker_session
from app.broker.base import BrokerError, describe_error
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


@router.get("/diagnostics")
def diagnostics(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    """Probe each Kite capability separately so a failure is actionable.

    A stored session only proves login worked. Quotes and historical candles
    are separately entitled on the Kite side, so each is checked on its own and
    reported with the exception type Kite returned (e.g. PermissionException
    when the app has no market-data subscription).
    """
    token = broker_session.load_access_token(db)
    checks: dict[str, dict] = {}
    if not token:
        return {
            "session_present": False,
            "checks": {},
            "hint": "No Kite session stored. Connect Zerodha from the Broker page first.",
        }

    from app.broker.zerodha import ZerodhaBroker

    zb = ZerodhaBroker(settings.kite_api_key, token)

    def probe(name: str, fn) -> None:
        try:
            fn()
            checks[name] = {"ok": True}
        except Exception as exc:  # noqa: BLE001 — the failure type is the answer
            checks[name] = {"ok": False, "error": describe_error(exc)}

    probe("profile", lambda: zb._kite.profile())
    probe("quote_index", lambda: zb.get_index_quote("NIFTY"))
    probe("quote_equity", lambda: zb.get_quote("RELIANCE"))
    probe("historical_candles", lambda: zb.historical_ohlcv("RELIANCE", "15m", 5))

    failed = {k: v for k, v in checks.items() if not v["ok"]}
    if not failed:
        hint = "All Kite data capabilities are working."
    elif any("PermissionException" in v.get("error", "") for v in failed.values()):
        hint = (
            "Kite returned PermissionException. Login works, but this app is not "
            "entitled to that data. Activate the Kite Connect app subscription at "
            "developers.kite.trade; historical candles additionally require the "
            "Historical Data add-on."
        )
    elif any("TokenException" in v.get("error", "") for v in failed.values()):
        hint = "Kite access token is invalid or expired. Reconnect from the Broker page."
    else:
        hint = "Kite data calls are failing; see the per-check errors above."

    return {"session_present": True, "checks": checks, "hint": hint}
