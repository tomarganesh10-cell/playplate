from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service = Column(String(100), nullable=False, unique=True, index=True)
    label = Column(String(200), nullable=False)
    key_name = Column(String(200), nullable=False)
    encrypted_value = Column(Text, nullable=True)
    is_configured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_verified = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
