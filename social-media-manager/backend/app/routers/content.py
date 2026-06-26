from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Optional, List
from uuid import UUID
import uuid

from app.database import get_db
from app.models.content import Content, ContentStatus, ContentType
from app.models.approval import Approval, ApprovalStatus
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.daily_workflow import DailyWorkflowService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/content", tags=["content"])


class ApprovalAction(BaseModel):
    action: str  # approve | reject | edit | regenerate
    notes: Optional[str] = None
    edited_caption: Optional[str] = None
    edited_hashtags: Optional[List[str]] = None
    regenerate_instructions: Optional[str] = None


@router.get("/")
async def list_content(
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    batch_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Content).order_by(desc(Content.created_at))

    if status:
        query = query.where(Content.status == status)
    if content_type:
        query = query.where(Content.content_type == content_type)
    if category:
        query = query.where(Content.category == category)
    if batch_id:
        try:
            query = query.where(Content.batch_id == uuid.UUID(batch_id))
        except ValueError:
            pass

    # Pagination
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    contents = result.scalars().all()

    return {
        "items": [_serialize_content(c) for c in contents],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/pending-approval")
async def pending_approval(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Content)
        .where(Content.status == ContentStatus.PENDING_APPROVAL)
        .order_by(desc(Content.created_at))
    )
    contents = result.scalars().all()
    return [_serialize_content(c) for c in contents]


@router.get("/{content_id}")
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(404, "Content not found")
    return _serialize_content(content)


@router.post("/{content_id}/approve")
async def approve_content(
    content_id: UUID,
    action: ApprovalAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(404, "Content not found")

    # Update approval record
    approval_result = await db.execute(
        select(Approval).where(Approval.content_id == content_id)
    )
    approval = approval_result.scalar_one_or_none()

    if action.action == "approve":
        content.status = ContentStatus.APPROVED
        content.approved_by = current_user.id
        content.approved_at = datetime.utcnow()
        if action.edited_caption:
            content.caption = action.edited_caption
        if action.edited_hashtags:
            content.hashtags = action.edited_hashtags
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.reviewed_by = current_user.id
            approval.reviewed_at = datetime.utcnow()

    elif action.action == "reject":
        content.status = ContentStatus.REJECTED
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.notes = action.notes
            approval.reviewed_by = current_user.id
            approval.reviewed_at = datetime.utcnow()

    elif action.action == "edit":
        if action.edited_caption:
            content.caption = action.edited_caption
        if action.edited_hashtags:
            content.hashtags = action.edited_hashtags
        # Keep pending approval status until explicitly approved
        if approval:
            approval.edited_caption = action.edited_caption
            approval.status = ApprovalStatus.EDIT_REQUESTED

    elif action.action == "regenerate":
        content.status = ContentStatus.DRAFT
        if approval:
            approval.status = ApprovalStatus.REGENERATE_REQUESTED
            approval.regenerate_instructions = action.regenerate_instructions

    await db.commit()
    return {"message": f"Content {action.action}d successfully", "status": content.status}


@router.post("/generate/daily")
async def trigger_daily_generation(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger the daily content generation workflow."""
    async def run_workflow():
        workflow = DailyWorkflowService(db)
        await workflow.run()

    background_tasks.add_task(run_workflow)
    return {"message": "Daily content generation started", "status": "running"}


@router.get("/stats/overview")
async def content_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statuses = [s.value for s in ContentStatus]
    stats = {}
    for status in statuses:
        result = await db.execute(
            select(func.count(Content.id)).where(Content.status == status)
        )
        stats[status] = result.scalar()

    total = await db.execute(select(func.count(Content.id)))
    stats["total"] = total.scalar()
    return stats


def _serialize_content(c: Content) -> dict:
    return {
        "id": str(c.id),
        "content_type": c.content_type,
        "category": c.category,
        "status": c.status,
        "title": c.title,
        "body_text": c.body_text,
        "caption": c.caption,
        "hashtags": c.hashtags or [],
        "cta": c.cta,
        "image_url": c.image_url,
        "video_url": c.video_url,
        "thumbnail_url": c.thumbnail_url,
        "scheduled_for": c.scheduled_for.isoformat() if c.scheduled_for else None,
        "published_at": c.published_at.isoformat() if c.published_at else None,
        "topic_key": c.topic_key,
        "batch_id": str(c.batch_id) if c.batch_id else None,
        "likes": c.likes,
        "comments": c.comments,
        "shares": c.shares,
        "views": c.views,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
