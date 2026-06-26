from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.config import settings
from app.database import init_db
from app.routers import auth, content, knowledge_base, credentials, analytics, pricing


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Playplate Social Media Manager API")
    await init_db()
    await _seed_initial_data()
    yield
    logger.info("Shutting down API")


async def _seed_initial_data():
    """Create default admin user and seed knowledge base on first run."""
    from app.database import AsyncSessionLocal
    from app.models.user import User, UserRole
    from app.routers.auth import get_password_hash
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(select(User).where(User.role == UserRole.SUPER_ADMIN))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@social.playplate.in",
                hashed_password=get_password_hash("admin123"),
                full_name="Playplate Admin",
                role=UserRole.SUPER_ADMIN,
            )
            db.add(admin)

            # Create doctor client account
            doctor = User(
                email=settings.DOCTOR_EMAIL,
                hashed_password=get_password_hash("doctor123"),
                full_name=settings.CLIENT_NAME,
                role=UserRole.CLIENT,
                phone=settings.DOCTOR_WHATSAPP,
                notification_email=True,
                notification_whatsapp=True,
            )
            db.add(doctor)
            await db.commit()
            logger.info("Default users created: admin + doctor")

        # Seed knowledge base
        from app.scrapers.website_scraper import WebsiteScraper
        scraper = WebsiteScraper(db)
        seeded = await scraper.seed_hardcoded_knowledge()
        if seeded > 0:
            logger.info(f"Knowledge base seeded with {seeded} entries")


app = FastAPI(
    title="Playplate Social Media Manager",
    description="AI-powered social media automation for Dr. Anshu Gupta — Chandigarh Dentist",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api")
app.include_router(credentials.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(pricing.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/api/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "client": settings.CLIENT_NAME,
        "docs": "/api/docs",
    }
