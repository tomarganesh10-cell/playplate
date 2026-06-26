"""
Agent 7: Publishing Manager
Posts approved content to Instagram, Facebook, LinkedIn, YouTube, Google Business Profile.
"""
import httpx
from loguru import logger
from app.config import settings


class PublishingManagerAgent:

    async def post_to_instagram(self, content: dict, image_url: str) -> dict:
        """Post to Instagram via Meta Graph API."""
        if not settings.META_ACCESS_TOKEN or not settings.INSTAGRAM_BUSINESS_ID:
            return {"status": "skipped", "platform": "instagram", "reason": "Not configured"}

        caption = content.get("edited_caption") or content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", [])[:30])
        full_caption = f"{caption}\n\n{hashtags}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                # Step 1: Create media container
                container_response = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_BUSINESS_ID}/media",
                    params={
                        "image_url": image_url,
                        "caption": full_caption[:2200],
                        "access_token": settings.META_ACCESS_TOKEN,
                    }
                )
                container_data = container_response.json()
                container_id = container_data.get("id")

                if not container_id:
                    return {"status": "failed", "platform": "instagram", "error": container_data}

                # Step 2: Publish
                publish_response = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_BUSINESS_ID}/media_publish",
                    params={
                        "creation_id": container_id,
                        "access_token": settings.META_ACCESS_TOKEN,
                    }
                )
                pub_data = publish_response.json()
                post_id = pub_data.get("id")

                return {
                    "status": "published",
                    "platform": "instagram",
                    "post_id": post_id,
                    "url": f"https://www.instagram.com/p/{post_id}/",
                }
            except Exception as e:
                logger.error(f"Instagram posting error: {e}")
                return {"status": "failed", "platform": "instagram", "error": str(e)}

    async def post_to_facebook(self, content: dict, image_url: str) -> dict:
        """Post to Facebook Page via Graph API."""
        if not settings.META_ACCESS_TOKEN or not settings.FACEBOOK_PAGE_ID:
            return {"status": "skipped", "platform": "facebook", "reason": "Not configured"}

        caption = content.get("edited_caption") or content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", [])[:10])
        message = f"{caption}\n\n{hashtags}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    f"https://graph.facebook.com/v19.0/{settings.FACEBOOK_PAGE_ID}/photos",
                    data={
                        "url": image_url,
                        "message": message[:63000],
                        "access_token": settings.META_ACCESS_TOKEN,
                    }
                )
                data = response.json()
                return {
                    "status": "published",
                    "platform": "facebook",
                    "post_id": data.get("id"),
                    "url": f"https://www.facebook.com/{data.get('post_id', '')}",
                }
            except Exception as e:
                logger.error(f"Facebook posting error: {e}")
                return {"status": "failed", "platform": "facebook", "error": str(e)}

    async def post_to_linkedin(self, content: dict, image_url: str = None) -> dict:
        """Post to LinkedIn via LinkedIn API v2."""
        if not settings.LINKEDIN_ACCESS_TOKEN or not settings.LINKEDIN_PERSON_ID:
            return {"status": "skipped", "platform": "linkedin", "reason": "Not configured"}

        caption = content.get("edited_caption") or content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", [])[:5])
        text = f"{caption}\n\n{hashtags}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                post_data = {
                    "author": f"urn:li:person:{settings.LINKEDIN_PERSON_ID}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text[:3000]},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                }

                response = await client.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    json=post_data,
                    headers={
                        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0",
                    }
                )
                data = response.json()
                post_id = data.get("id", "")

                return {
                    "status": "published",
                    "platform": "linkedin",
                    "post_id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                }
            except Exception as e:
                logger.error(f"LinkedIn posting error: {e}")
                return {"status": "failed", "platform": "linkedin", "error": str(e)}

    async def post_to_google_business(self, content: dict, image_url: str = None) -> dict:
        """Post to Google Business Profile."""
        if not settings.GBP_ACCOUNT_ID or not settings.GBP_LOCATION_ID:
            return {"status": "skipped", "platform": "google_business", "reason": "Not configured"}

        caption = content.get("edited_caption") or content.get("caption", "")

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                post_data = {
                    "languageCode": "en-US",
                    "summary": caption[:1500],
                    "callToAction": {
                        "actionType": "BOOK",
                        "url": "https://www.chandigarhdentist.com/contact",
                    },
                }

                if image_url:
                    post_data["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": image_url}]

                response = await client.post(
                    f"https://mybusiness.googleapis.com/v4/accounts/{settings.GBP_ACCOUNT_ID}/locations/{settings.GBP_LOCATION_ID}/localPosts",
                    json=post_data,
                    headers={
                        "Authorization": f"Bearer {settings.GOOGLE_CLIENT_ID}",
                        "Content-Type": "application/json",
                    }
                )
                data = response.json()
                return {
                    "status": "published",
                    "platform": "google_business",
                    "post_id": data.get("name", ""),
                }
            except Exception as e:
                logger.error(f"Google Business posting error: {e}")
                return {"status": "failed", "platform": "google_business", "error": str(e)}

    async def publish_content(self, content: dict, image_url: str = None) -> dict:
        """Publish content to all configured platforms."""
        platforms = content.get("target_platforms", ["instagram", "facebook", "linkedin"])
        results = {}

        for platform in platforms:
            if platform == "instagram":
                results["instagram"] = await self.post_to_instagram(content, image_url)
            elif platform == "facebook":
                results["facebook"] = await self.post_to_facebook(content, image_url)
            elif platform == "linkedin":
                results["linkedin"] = await self.post_to_linkedin(content, image_url)
            elif platform == "google_business":
                results["google_business"] = await self.post_to_google_business(content, image_url)

        return results
