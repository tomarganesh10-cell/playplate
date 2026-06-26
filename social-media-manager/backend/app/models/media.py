from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    THUMBNAIL = "thumbnail"


class MediaStatus(str, enum.Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class Media(Base):
    __tablename__ = "media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True)
    media_type = Column(SAEnum(MediaType), nullable=False)
    status = Column(SAEnum(MediaStatus), default=MediaStatus.GENERATING)

    filename = Column(String(500), nullable=False)
    original_url = Column(String(1000), nullable=True)
    storage_url = Column(String(1000), nullable=True)
    drive_url = Column(String(1000), nullable=True)
    cdn_url = Column(String(1000), nullable=True)

    # Generation metadata
    generator = Column(String(100), nullable=True)  # kling, runway, pika, dalle3
    generation_prompt = Column(Text, nullable=True)
    generation_job_id = Column(String(200), nullable=True)

    # File info
    file_size_bytes = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    format = Column(String(20), nullable=True)
    aspect_ratio = Column(String(20), nullable=True)

    extra_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
