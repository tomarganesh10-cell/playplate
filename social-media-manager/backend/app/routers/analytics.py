from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from app.database import get_db
from app.models.analytics import Analytics
from app.models.content import Content, ContentStatus
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)

    # Platform breakdown
    platform_result = await db.execute(
        select(Analytics.platform, func.sum(Analytics.likes), func.sum(Analytics.comments),
               func.sum(Analytics.shares), func.sum(Analytics.views), func.sum(Analytics.reach))
        .where(Analytics.date_recorded >= since)
        .group_by(Analytics.platform)
    )
    platforms = {}
    for row in platform_result.fetchall():
        platforms[row[0]] = {
            "likes": row[1] or 0,
            "comments": row[2] or 0,
            "shares": row[3] or 0,
            "views": row[4] or 0,
            "reach": row[5] or 0,
        }

    # Published content count
    pub_result = await db.execute(
        select(func.count(Content.id))
        .where(Content.status == ContentStatus.PUBLISHED)
        .where(Content.published_at >= since)
    )
    published_count = pub_result.scalar() or 0

    # Total engagement
    total_result = await db.execute(
        select(
            func.sum(Analytics.likes),
            func.sum(Analytics.comments),
            func.sum(Analytics.shares),
            func.sum(Analytics.views),
            func.sum(Analytics.reach),
        ).where(Analytics.date_recorded >= since)
    )
    totals = total_result.fetchone()

    return {
        "period_days": days,
        "published_posts": published_count,
        "total_likes": totals[0] or 0,
        "total_comments": totals[1] or 0,
        "total_shares": totals[2] or 0,
        "total_views": totals[3] or 0,
        "total_reach": totals[4] or 0,
        "platforms": platforms,
    }


@router.get("/top-content")
async def top_content(
    limit: int = Query(10, ge=1, le=50),
    metric: str = Query("likes", enum=["likes", "views", "comments", "shares", "reach"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    metric_col = getattr(Content, metric, Content.likes)
    result = await db.execute(
        select(Content)
        .where(Content.status == ContentStatus.PUBLISHED)
        .order_by(desc(metric_col))
        .limit(limit)
    )
    contents = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "platform": c.content_type,
            "category": c.category,
            "likes": c.likes,
            "views": c.views,
            "comments": c.comments,
            "shares": c.shares,
            "published_at": c.published_at.isoformat() if c.published_at else None,
            "image_url": c.image_url,
        }
        for c in contents
    ]


@router.get("/calendar")
async def content_calendar(
    year: int = Query(datetime.utcnow().year),
    month: int = Query(datetime.utcnow().month),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from calendar import monthrange
    _, days_in_month = monthrange(year, month)
    start = datetime(year, month, 1)
    end = datetime(year, month, days_in_month, 23, 59, 59)

    result = await db.execute(
        select(Content)
        .where(Content.scheduled_for.between(start, end))
        .order_by(Content.scheduled_for)
    )
    contents = result.scalars().all()

    calendar_data = {}
    for c in contents:
        day = c.scheduled_for.day
        if day not in calendar_data:
            calendar_data[day] = []
        calendar_data[day].append({
            "id": str(c.id),
            "title": c.title,
            "platform": c.content_type,
            "status": c.status,
            "time": c.scheduled_for.strftime("%H:%M"),
        })

    return {"year": year, "month": month, "days": calendar_data}
