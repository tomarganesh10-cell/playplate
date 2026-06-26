from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class TopicHistory(Base):
    __tablename__ = "topic_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_key = Column(String(200), nullable=False, unique=True, index=True)
    topic_name = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    use_count = Column(JSON, default=0)
    platforms_used = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
