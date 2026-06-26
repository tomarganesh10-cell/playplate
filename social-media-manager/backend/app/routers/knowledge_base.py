from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.knowledge_base import KnowledgeBase
from app.routers.auth import get_current_user, require_admin
from app.models.user import User
from app.scrapers.website_scraper import WebsiteScraper

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.get("/")
async def list_knowledge_base(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(KnowledgeBase).where(KnowledgeBase.is_active == True)
    if category:
        query = query.where(KnowledgeBase.category == category)

    result = await db.execute(query)
    entries = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "category": e.category,
            "title": e.title,
            "content": e.content[:500] + "..." if len(e.content) > 500 else e.content,
            "source_url": e.source_url,
            "tags": e.tags,
            "last_crawled": e.last_crawled.isoformat() if e.last_crawled else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(KnowledgeBase.category, func.count(KnowledgeBase.id))
        .where(KnowledgeBase.is_active == True)
        .group_by(KnowledgeBase.category)
    )
    return {row[0]: row[1] for row in result.fetchall()}


@router.post("/crawl")
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Trigger website crawl to refresh knowledge base."""
    async def run_scraper():
        scraper = WebsiteScraper(db)
        await scraper.run(seed_hardcoded=True)

    background_tasks.add_task(run_scraper)
    return {"message": "Crawl started in background"}


@router.post("/seed")
async def seed_knowledge_base(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Seed the knowledge base with hardcoded dental knowledge."""
    scraper = WebsiteScraper(db)
    count = await scraper.seed_hardcoded_knowledge()
    return {"message": f"Seeded {count} knowledge base entries"}
