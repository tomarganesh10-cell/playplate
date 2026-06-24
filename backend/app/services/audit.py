"""Audit-log helper."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def record(
    db: Session,
    action: str,
    *,
    actor_id: int | None = None,
    actor_email: str | None = None,
    target: str | None = None,
    ip_address: str | None = None,
    detail: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            target=target,
            ip_address=ip_address,
            detail=detail or {},
        )
    )
    db.commit()
