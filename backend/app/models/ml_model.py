from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class MLModel(Base):
    """A trained (experimental) prediction model with its validation metrics."""

    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), default="15m")
    horizon: Mapped[int] = mapped_column(Integer, default=4)
    feature_names: Mapped[list] = mapped_column(JSON, default=list)
    weights: Mapped[list] = mapped_column(JSON, default=list)
    mu: Mapped[list] = mapped_column(JSON, default=list)
    sigma: Mapped[list] = mapped_column(JSON, default=list)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
