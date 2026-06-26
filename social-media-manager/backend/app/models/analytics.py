from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True)
    platform = Column(String(50), nullable=False)
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())

    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    views = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    follower_count = Column(Integer, nullable=True)

    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
