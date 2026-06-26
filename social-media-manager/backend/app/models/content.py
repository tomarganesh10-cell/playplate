from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class ContentType(str, enum.Enum):
    INSTAGRAM_POST = "instagram_post"
    FACEBOOK_POST = "facebook_post"
    LINKEDIN_POST = "linkedin_post"
    YOUTUBE_SHORT = "youtube_short"
    INSTAGRAM_REEL = "instagram_reel"
    EDUCATIONAL_VIDEO = "educational_video"
    GOOGLE_BUSINESS = "google_business"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentCategory(str, enum.Enum):
    DENTAL_AWARENESS = "dental_awareness"
    MYTH_VS_FACT = "myth_vs_fact"
    PATIENT_EDUCATION = "patient_education"
    SMILE_MAKEOVER = "smile_makeover"
    KIDS_DENTISTRY = "kids_dentistry"
    DENTAL_IMPLANTS = "dental_implants"
    BRACES = "braces"
    TEETH_WHITENING = "teeth_whitening"
    ORAL_HYGIENE = "oral_hygiene"
    PATIENT_JOURNEY = "patient_journey"
    DOCTOR_INTRO = "doctor_intro"
    CLINIC_TOUR = "clinic_tour"
    FAQ = "faq"
    FESTIVAL = "festival"
    LOCAL_CONTENT = "local_content"
    BEFORE_AFTER = "before_after"


class Content(Base):
    __tablename__ = "content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(SAEnum(ContentType), nullable=False, index=True)
    category = Column(SAEnum(ContentCategory), nullable=False, index=True)
    status = Column(SAEnum(ContentStatus), default=ContentStatus.DRAFT, index=True)

    title = Column(String(500), nullable=False)
    body_text = Column(Text, nullable=False)
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, default=list)
    cta = Column(String(500), nullable=True)

    # AI Generation metadata
    ai_model_used = Column(String(100), nullable=True)
    generation_prompt = Column(Text, nullable=True)
    image_prompt = Column(Text, nullable=True)
    video_prompt = Column(Text, nullable=True)
    video_script = Column(JSON, nullable=True)  # structured script

    # Media references
    image_url = Column(String(1000), nullable=True)
    video_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)

    # Publishing
    platform_post_ids = Column(JSON, default=dict)  # {instagram: "id", facebook: "id"}
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Approval
    approval_notes = Column(Text, nullable=True)
    edited_caption = Column(Text, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Analytics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)

    # Topic tracking
    topic_key = Column(String(200), nullable=True, index=True)
    batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    generation_batch = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
