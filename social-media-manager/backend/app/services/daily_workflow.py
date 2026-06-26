"""
Daily Content Workflow Service
Orchestrates all agents to generate daily content at 9:00 AM.
"""
import uuid
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.config import settings
from app.models.content import Content, ContentType, ContentStatus, ContentCategory
from app.models.topic_history import TopicHistory
from app.models.approval import Approval, ApprovalStatus
from app.models.notification import Notification, NotificationType
from app.agents import (
    ContentResearchAgent,
    ContentWriterAgent,
    VideoScriptWriterAgent,
    PromptEngineerAgent,
    VideoGeneratorAgent,
)
from app.services.notification_service import NotificationService


class DailyWorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.batch_id = uuid.uuid4()

    async def run(self) -> dict:
        """Main daily workflow — 9:00 AM trigger."""
        logger.info(f"=== Daily Workflow Starting — Batch {self.batch_id} ===")
        results = {
            "batch_id": str(self.batch_id),
            "started_at": datetime.utcnow().isoformat(),
            "posts_generated": 0,
            "videos_generated": 0,
            "errors": [],
        }

        try:
            # Agent 1: Research topics
            logger.info("Step 1: Content Research Agent")
            research_agent = ContentResearchAgent(self.db)
            topics = await research_agent.run(count=settings.DAILY_POSTS_COUNT)
            logger.info(f"Researched {len(topics)} topics")

            # Agent 2: Write posts
            logger.info("Step 2: Content Writer Agent")
            writer_agent = ContentWriterAgent()
            platforms = [
                ContentType.INSTAGRAM_POST,
                ContentType.FACEBOOK_POST,
                ContentType.LINKEDIN_POST,
            ]
            posts = await writer_agent.run(topics, platforms)
            logger.info(f"Written {len(posts)} posts")

            # Agent 3: Write video scripts
            logger.info("Step 3: Video Script Writer Agent")
            script_agent = VideoScriptWriterAgent()
            scripts = await script_agent.run(topics, duration_key="reel_30")
            logger.info(f"Written {len(scripts)} scripts")

            # Agent 4: Generate prompts
            logger.info("Step 4: Prompt Engineer Agent")
            prompt_agent = PromptEngineerAgent()
            prompted = await prompt_agent.run(posts, scripts)
            posts_with_prompts = prompted["posts_with_prompts"]
            scripts_with_prompts = prompted["scripts_with_prompts"]

            # Agent 5: Generate videos (async, don't wait for completion)
            logger.info("Step 5: Video Generator Agent (async)")
            video_agent = VideoGeneratorAgent()
            video_jobs = await video_agent.run(scripts_with_prompts)

            # Save all content to database
            logger.info("Step 6: Saving to database")
            content_ids = await self._save_content(posts_with_prompts, scripts_with_prompts, video_jobs)
            results["posts_generated"] = len(content_ids["posts"])
            results["videos_generated"] = len(content_ids["videos"])

            # Update topic history
            await self._update_topic_history(topics)

            # Send approval notifications
            logger.info("Step 7: Sending approval notifications")
            notification_service = NotificationService()
            await notification_service.send_daily_approval_notification(
                batch_id=str(self.batch_id),
                post_count=results["posts_generated"],
                video_count=results["videos_generated"],
            )

            results["completed_at"] = datetime.utcnow().isoformat()
            results["status"] = "success"
            logger.info(f"=== Daily Workflow Complete — {results} ===")

        except Exception as e:
            logger.error(f"Daily workflow error: {e}")
            results["errors"].append(str(e))
            results["status"] = "failed"

        return results

    async def _save_content(self, posts: list, scripts: list, video_jobs: list) -> dict:
        """Save all generated content to database."""
        post_ids = []
        video_ids = []

        for post in posts:
            image_gen = post.get("image_generation", {})
            content = Content(
                batch_id=self.batch_id,
                content_type=ContentType(post.get("platform", ContentType.INSTAGRAM_POST)),
                category=ContentCategory(post.get("category", ContentCategory.DENTAL_AWARENESS)),
                status=ContentStatus.PENDING_APPROVAL,
                title=post.get("title", "")[:500],
                body_text=post.get("body_text", ""),
                caption=post.get("caption", ""),
                hashtags=post.get("hashtags", []),
                cta=post.get("cta", ""),
                image_prompt=image_gen.get("dalle3_prompt", ""),
                generation_prompt=post.get("video_prompt", ""),
                topic_key=post.get("topic_key"),
                generation_batch=str(self.batch_id),
            )
            self.db.add(content)
            await self.db.flush()

            # Create approval record
            approval = Approval(
                content_id=content.id,
                status=ApprovalStatus.PENDING,
            )
            self.db.add(approval)

            # Create notification
            notification = Notification(
                notification_type=NotificationType.APPROVAL_NEEDED,
                title="New Content Ready for Approval",
                message=f"'{post.get('title', 'New post')}' is ready for your review.",
                action_url=f"{settings.CLIENT_URL}/approval",
                related_content_id=content.id,
            )
            self.db.add(notification)

            post_ids.append(str(content.id))

        for script in scripts:
            video_content = Content(
                batch_id=self.batch_id,
                content_type=ContentType.INSTAGRAM_REEL,
                category=ContentCategory(script.get("category", ContentCategory.DENTAL_AWARENESS)),
                status=ContentStatus.PENDING_APPROVAL,
                title=script.get("title", "")[:500],
                body_text=script.get("voiceover_full", ""),
                caption=script.get("caption_for_post", ""),
                video_script=script.get("scenes", []),
                video_prompt=str(script.get("video_generation", {})),
                topic_key=script.get("topic_key"),
                generation_batch=str(self.batch_id),
            )
            self.db.add(video_content)
            await self.db.flush()

            approval = Approval(content_id=video_content.id, status=ApprovalStatus.PENDING)
            self.db.add(approval)
            video_ids.append(str(video_content.id))

        await self.db.commit()
        return {"posts": post_ids, "videos": video_ids}

    async def _update_topic_history(self, topics: list) -> None:
        """Mark topics as used."""
        from sqlalchemy import select
        for topic in topics:
            topic_key = topic.get("topic_key", "")
            if not topic_key:
                continue

            from app.models.topic_history import TopicHistory
            result = await self.db.execute(
                select(TopicHistory).where(TopicHistory.topic_key == topic_key)
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.last_used = datetime.utcnow()
                existing.use_count = (existing.use_count or 0) + 1
            else:
                history = TopicHistory(
                    topic_key=topic_key,
                    topic_name=topic.get("topic", ""),
                    category=str(topic.get("category", "")),
                    use_count=1,
                )
                self.db.add(history)

        await self.db.commit()
