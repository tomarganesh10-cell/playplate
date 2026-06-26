from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000), nullable=True)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_crawled = Column(DateTime(timezone=True), nullable=True)


# Categories: services, treatments, procedures, testimonials, about_doctor,
# achievements, technology, clinic_info, location, faqs, blog
