from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    CONTENT_READY = "content_ready"
    APPROVAL_NEEDED = "approval_needed"
    PUBLISHED = "published"
    FAILED = "failed"
    ANALYTICS_REPORT = "analytics_report"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    action_url = Column(String(1000), nullable=True)
    related_content_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
