from sqlalchemy import Column, String, DateTime, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class ScheduleStatus(str, enum.Enum):
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(SAEnum(ScheduleStatus), default=ScheduleStatus.PENDING)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    platform_post_id = Column(String(500), nullable=True)
    platform_post_url = Column(String(1000), nullable=True)
    error_message = Column(String(2000), nullable=True)
    retry_count = Column(JSON, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
