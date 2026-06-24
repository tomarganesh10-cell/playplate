from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Signal(Base):
    """A generated trade idea. Stored for audit and performance attribution."""

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)  # BUY | SELL
    timeframe: Mapped[str] = mapped_column(String(8), default="15m")

    entry: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    target: Mapped[float] = mapped_column(Float, nullable=False)
    risk_reward: Mapped[float] = mapped_column(Float, default=0.0)

    # Scoring
    score: Mapped[float] = mapped_column(Float, default=0.0)          # raw engine score
    confidence: Mapped[float] = mapped_column(Float, default=0.0)     # 0..1 AI confidence
    rank: Mapped[int | None] = mapped_column(Integer)

    indicators: Mapped[dict] = mapped_column(JSON, default=dict)      # snapshot of indicator values
    explanation: Mapped[str | None] = mapped_column(String(4000))    # AI NL explanation

    status: Mapped[str] = mapped_column(String(16), default="active")  # active|expired|executed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
