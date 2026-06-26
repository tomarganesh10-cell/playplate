from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Playplate Social Media Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://smm:smm_pass@postgres:5432/smm_db"
    DATABASE_URL_SYNC: str = "postgresql://smm:smm_pass@postgres:5432/smm_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # AI APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Image Generation
    STABILITY_API_KEY: Optional[str] = None

    # Video Generation
    KLING_API_KEY: Optional[str] = None
    RUNWAY_API_KEY: Optional[str] = None
    PIKA_API_KEY: Optional[str] = None
    HAILUO_API_KEY: Optional[str] = None
    GOOGLE_VEO_API_KEY: Optional[str] = None

    # Google APIs
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
    GOOGLE_SHEETS_ID: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # Meta (Facebook/Instagram)
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_BUSINESS_ID: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None

    # LinkedIn
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_PERSON_ID: Optional[str] = None

    # YouTube
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_CHANNEL_ID: Optional[str] = None

    # Google Business Profile
    GBP_ACCOUNT_ID: Optional[str] = None
    GBP_LOCATION_ID: Optional[str] = None

    # WhatsApp
    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_PHONE_NUMBER: Optional[str] = None
    DOCTOR_WHATSAPP: str = "+919876543210"

    # Email (SMTP / SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@social.playplate.in"
    DOCTOR_EMAIL: str = "dr.anshu@chandigarhdentist.com"

    # MinIO / Storage
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_IMAGES: str = "smm-images"
    MINIO_BUCKET_VIDEOS: str = "smm-videos"

    # n8n
    N8N_WEBHOOK_URL: str = "http://n8n:5678"
    N8N_API_KEY: Optional[str] = None

    # Client
    CLIENT_WEBSITE: str = "https://www.chandigarhdentist.com"
    CLIENT_NAME: str = "Dr. Anshu Gupta"
    CLIENT_LOCATION: str = "Chandigarh, India"
    CLIENT_SPECIALTY: str = "Cosmetic Dentist, Aesthetic Dentist, Implantologist, Pediatric Dentist"

    # Dashboard
    FRONTEND_URL: str = "https://social.playplate.in"
    ADMIN_URL: str = "https://social.playplate.in/admin"
    CLIENT_URL: str = "https://social.playplate.in/client"

    # Content Settings
    DAILY_POSTS_COUNT: int = 5
    DAILY_REELS_COUNT: int = 5
    DAILY_VIDEOS_COUNT: int = 5
    TOPIC_COOLDOWN_DAYS: int = 30
    POST_ALTERNATE_DAYS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
