"""Admin: user management, circuit-breaker control, audit log."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import get_db
from app.deps import require_admin
from app.models.audit import AuditLog
from app.models.user import User
from app.risk.circuit_breaker import breaker
from app.schemas.auth import UserCreate, UserOut
from app.services import audit

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[User]:
    return list(db.execute(select(User).order_by(User.id)).scalars())


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> User:
    if db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit.record(
        db, "user_created", actor_id=admin.id, actor_email=admin.email,
        ip_address=request.client.host if request.client else None,
        target=payload.email, detail={"role": payload.role},
    )
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/circuit-breaker")
def circuit_status(_: User = Depends(require_admin)) -> dict:
    return {"tripped": breaker.tripped, "reason": breaker.reason}


@router.post("/circuit-breaker/reset")
def reset_breaker(
    request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict:
    breaker.reset(f"manual by {admin.email}")
    audit.record(
        db, "circuit_breaker_reset", actor_id=admin.id, actor_email=admin.email,
        ip_address=request.client.host if request.client else None,
    )
    return {"tripped": breaker.tripped}


@router.post("/circuit-breaker/trip")
def trip_breaker(
    reason: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict:
    """Manual kill-switch — immediately halt new order entry."""
    breaker.trip(f"manual: {reason} (by {admin.email})")
    return {"tripped": breaker.tripped, "reason": breaker.reason}


@router.get("/audit")
def audit_log(
    limit: int = 100, db: Session = Depends(get_db), _: User = Depends(require_admin)
) -> list[dict]:
    rows = db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(limit, 500))
    ).scalars()
    return [
        {
            "id": r.id, "action": r.action, "actor_email": r.actor_email,
            "target": r.target, "ip": r.ip_address, "detail": r.detail,
            "at": r.created_at.isoformat(),
        }
        for r in rows
    ]
