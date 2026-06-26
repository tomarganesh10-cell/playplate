from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDIT_REQUESTED = "edit_requested"
    REGENERATE_REQUESTED = "regenerate_requested"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    notes = Column(Text, nullable=True)
    edited_caption = Column(Text, nullable=True)
    edited_hashtags = Column(Text, nullable=True)
    regenerate_instructions = Column(Text, nullable=True)
    notified_email = Column(DateTime(timezone=True), nullable=True)
    notified_whatsapp = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
