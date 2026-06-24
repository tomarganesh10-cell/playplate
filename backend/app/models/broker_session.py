from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class BrokerSession(Base):
    """Stores the encrypted daily Kite access token and session metadata.

    Kite access tokens expire every trading day (~6 AM IST next day), so this
    row is refreshed through the broker login workflow.
    """

    __tablename__ = "broker_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    broker: Mapped[str] = mapped_column(String(32), default="zerodha", index=True)
    api_key: Mapped[str] = mapped_column(String(255))
    # Encrypted at rest (Fernet). Never logged or returned via the API.
    encrypted_access_token: Mapped[str] = mapped_column(Text)
    user_id: Mapped[str | None] = mapped_column(String(64))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
