"""
Agent 5: Video Generator
Integrates with Kling, Runway, Pika, Hailuo, Google Veo for video generation.
"""
import asyncio
import httpx
from loguru import logger
from app.config import settings


# ── Pricing Reference (per video, approximate as of 2025) ─────────────────────
VIDEO_PRICING = {
    "kling": {
        "name": "Kling AI",
        "currency": "USD",
        "plans": {
            "standard_5s":  {"price_usd": 0.14, "price_inr": 12,  "duration": "5s",  "quality": "Standard", "resolution": "720p"},
            "standard_10s": {"price_usd": 0.28, "price_inr": 23,  "duration": "10s", "quality": "Standard", "resolution": "720p"},
            "pro_5s":       {"price_usd": 0.35, "price_inr": 29,  "duration": "5s",  "quality": "Pro",      "resolution": "1080p"},
            "pro_10s":      {"price_usd": 0.70, "price_inr": 58,  "duration": "10s", "quality": "Pro",      "resolution": "1080p"},
        },
        "monthly_subscriptions": {
            "basic":    {"price_usd": 8,   "price_inr": 665,  "credits": 660,  "videos_approx": 47},
            "standard": {"price_usd": 22,  "price_inr": 1830, "credits": 3000, "videos_approx": 214},
            "pro":      {"price_usd": 66,  "price_inr": 5500, "credits": 8000, "videos_approx": 571},
        },
        "recommended_plan": "standard",
        "api_available": True,
        "website": "https://klingai.com",
    },
    "runway": {
        "name": "Runway ML",
        "currency": "USD",
        "plans": {
            "gen4_5s":  {"price_usd": 0.50,  "price_inr": 42,  "duration": "5s",  "quality": "Gen4 Turbo", "resolution": "1080p"},
            "gen4_10s": {"price_usd": 1.00,  "price_inr": 83,  "duration": "10s", "quality": "Gen4 Turbo", "resolution": "1080p"},
        },
        "monthly_subscriptions": {
            "standard": {"price_usd": 15,  "price_inr": 1250, "credits": 625,  "videos_approx": 62},
            "pro":      {"price_usd": 35,  "price_inr": 2915, "credits": 2250, "videos_approx": 225},
            "unlimited":{"price_usd": 95,  "price_inr": 7900, "credits": "unlimited", "videos_approx": "unlimited"},
        },
        "recommended_plan": "standard",
        "api_available": True,
        "website": "https://runwayml.com",
    },
    "pika": {
        "name": "Pika Labs",
        "currency": "USD",
        "plans": {
            "pika_3s":  {"price_usd": 0.05, "price_inr": 4,   "duration": "3s",  "quality": "Standard", "resolution": "1080p"},
            "pika_5s":  {"price_usd": 0.08, "price_inr": 7,   "duration": "5s",  "quality": "Standard", "resolution": "1080p"},
            "pika_10s": {"price_usd": 0.16, "price_inr": 13,  "duration": "10s", "quality": "Standard", "resolution": "1080p"},
        },
        "monthly_subscriptions": {
            "basic":   {"price_usd": 8,   "price_inr": 665,  "credits": 150,  "videos_approx": 30},
            "standard":{"price_usd": 20,  "price_inr": 1665, "credits": 700,  "videos_approx": 140},
            "unlimited":{"price_usd": 70, "price_inr": 5830, "credits": "unlimited", "videos_approx": "unlimited"},
        },
        "recommended_plan": "standard",
        "api_available": True,
        "website": "https://pika.art",
    },
    "hailuo": {
        "name": "Hailuo AI (MiniMax)",
        "currency": "USD",
        "plans": {
            "video_01_6s":  {"price_usd": 0.22, "price_inr": 18, "duration": "6s",  "quality": "Standard", "resolution": "1080p"},
            "video_01_pro": {"price_usd": 0.55, "price_inr": 46, "duration": "6s",  "quality": "Pro",      "resolution": "4K"},
        },
        "monthly_subscriptions": {
            "basic":   {"price_usd": 10,  "price_inr": 830,  "credits": 100,  "videos_approx": 45},
            "pro":     {"price_usd": 30,  "price_inr": 2500, "credits": 350,  "videos_approx": 159},
        },
        "recommended_plan": "basic",
        "api_available": True,
        "website": "https://hailuoai.video",
    },
    "google_veo": {
        "name": "Google Veo 3",
        "currency": "USD",
        "plans": {
            "veo3_8s":  {"price_usd": 0.75, "price_inr": 62, "duration": "8s",  "quality": "Veo3", "resolution": "1080p"},
            "veo3_16s": {"price_usd": 1.50, "price_inr": 125, "duration": "16s", "quality": "Veo3", "resolution": "1080p"},
        },
        "monthly_subscriptions": {
            "vertex_ai": {"price_usd": "pay-as-you-go", "price_inr": "pay-as-you-go", "note": "Via Google Vertex AI only"},
        },
        "recommended_plan": "pay_as_you_go",
        "api_available": True,
        "website": "https://deepmind.google/technologies/veo",
    },
    "dalle3": {
        "name": "DALL-E 3 (Images)",
        "currency": "USD",
        "plans": {
            "standard_1024": {"price_usd": 0.040, "price_inr": 3.3, "size": "1024x1024", "quality": "Standard"},
            "hd_1024":       {"price_usd": 0.080, "price_inr": 6.7, "size": "1024x1024", "quality": "HD"},
            "hd_wide":       {"price_usd": 0.120, "price_inr": 10,  "size": "1792x1024", "quality": "HD"},
            "hd_vertical":   {"price_usd": 0.120, "price_inr": 10,  "size": "1024x1792", "quality": "HD"},
        },
        "monthly_subscriptions": {
            "openai_api": {"price_usd": "pay-as-you-go", "note": "Part of OpenAI API billing"},
        },
        "recommended_plan": "hd_1024",
        "api_available": True,
        "website": "https://openai.com/dall-e-3",
    },
}

# ── Monthly Cost Estimate for Dr. Anshu Gupta (5 videos/day) ──────────────────
MONTHLY_COST_ESTIMATE = {
    "videos_per_month": 150,  # 5 videos/day × 30 days
    "images_per_month": 150,  # 5 images/day × 30 days
    "estimated_costs": {
        "budget":    {"kling_basic": 8,   "dalle3": 12, "total_usd": 20,  "total_inr": 1665},
        "standard":  {"kling_standard": 22, "dalle3": 18, "total_usd": 40, "total_inr": 3330},
        "premium":   {"runway_pro": 35,  "dalle3_hd": 18, "total_usd": 53, "total_inr": 4415},
    },
    "recommended": "standard",
    "note": "Costs vary based on video length and quality selected",
}


class VideoGeneratorAgent:
    """Orchestrates video generation across multiple AI video platforms."""

    def get_pricing_info(self, generator: str = None) -> dict:
        """Return pricing information for video generators."""
        if generator:
            return VIDEO_PRICING.get(generator, {})
        return {
            "generators": VIDEO_PRICING,
            "monthly_estimate": MONTHLY_COST_ESTIMATE,
            "exchange_rate_note": "INR prices approx at 1 USD = 83 INR",
        }

    def get_cost_estimate(self, generator: str, duration_seconds: int, quality: str = "standard") -> dict:
        """Estimate cost for a single video generation."""
        pricing = VIDEO_PRICING.get(generator, {})
        if not pricing:
            return {"error": f"Unknown generator: {generator}"}

        plans = pricing.get("plans", {})
        best_match = None

        for plan_key, plan in plans.items():
            plan_duration = int(plan.get("duration", "5s").replace("s", ""))
            plan_quality = plan.get("quality", "").lower()
            if plan_duration >= duration_seconds and quality.lower() in plan_quality:
                if best_match is None or plan.get("price_usd", 999) < best_match.get("price_usd", 999):
                    best_match = {**plan, "plan_key": plan_key}

        if not best_match:
            best_match = list(plans.values())[0] if plans else {}

        return {
            "generator": generator,
            "generator_name": pricing.get("name", generator),
            "duration_requested": f"{duration_seconds}s",
            "estimated_plan": best_match,
            "price_usd": best_match.get("price_usd", 0),
            "price_inr": best_match.get("price_inr", 0),
        }

    async def generate_with_kling(self, prompt: dict) -> dict:
        """Generate video using Kling AI API."""
        if not settings.KLING_API_KEY:
            return {"status": "skipped", "reason": "KLING_API_KEY not configured", "generator": "kling"}

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    "https://api.klingai.com/v1/videos/text2video",
                    headers={
                        "Authorization": f"Bearer {settings.KLING_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "kling-v1",
                        "prompt": prompt.get("main_prompt", ""),
                        "negative_prompt": prompt.get("negative_prompt", ""),
                        "duration": min(prompt.get("duration", 5), 10),
                        "aspect_ratio": prompt.get("aspect_ratio", "9:16"),
                        "mode": "standard",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "submitted",
                        "job_id": data.get("task_id"),
                        "generator": "kling",
                        "check_url": f"https://api.klingai.com/v1/videos/text2video/{data.get('task_id')}",
                    }
                else:
                    logger.error(f"Kling API error: {response.status_code} {response.text}")
                    return {"status": "failed", "generator": "kling", "error": response.text}
            except Exception as e:
                logger.error(f"Kling generation error: {e}")
                return {"status": "failed", "generator": "kling", "error": str(e)}

    async def generate_with_runway(self, prompt: dict) -> dict:
        """Generate video using Runway ML API."""
        if not settings.RUNWAY_API_KEY:
            return {"status": "skipped", "reason": "RUNWAY_API_KEY not configured", "generator": "runway"}

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    "https://api.dev.runwayml.com/v1/image_to_video",
                    headers={
                        "Authorization": f"Bearer {settings.RUNWAY_API_KEY}",
                        "X-Runway-Version": "2024-11-06",
                        "Content-Type": "application/json",
                    },
                    json={
                        "promptText": prompt.get("main_prompt", ""),
                        "model": "gen4_turbo",
                        "ratio": "768:1344",
                        "duration": min(prompt.get("duration", 5), 10),
                    },
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    return {
                        "status": "submitted",
                        "job_id": data.get("id"),
                        "generator": "runway",
                    }
                else:
                    return {"status": "failed", "generator": "runway", "error": response.text}
            except Exception as e:
                logger.error(f"Runway generation error: {e}")
                return {"status": "failed", "generator": "runway", "error": str(e)}

    async def generate_with_pika(self, prompt: dict) -> dict:
        """Generate video using Pika Labs API."""
        if not settings.PIKA_API_KEY:
            return {"status": "skipped", "reason": "PIKA_API_KEY not configured", "generator": "pika"}

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    "https://api.pika.art/v1/generate",
                    headers={
                        "Authorization": f"Bearer {settings.PIKA_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "prompt": prompt.get("main_prompt", ""),
                        "negative_prompt": prompt.get("negative_prompt", ""),
                        "frameRate": prompt.get("fps", 24),
                        "resolution": "1080p",
                        "aspectRatio": "9:16",
                        "duration": min(prompt.get("duration", 5), 10),
                    },
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    return {
                        "status": "submitted",
                        "job_id": data.get("id"),
                        "generator": "pika",
                    }
                else:
                    return {"status": "failed", "generator": "pika", "error": response.text}
            except Exception as e:
                logger.error(f"Pika generation error: {e}")
                return {"status": "failed", "generator": "pika", "error": str(e)}

    async def generate_with_hailuo(self, prompt: dict) -> dict:
        """Generate video using Hailuo AI."""
        if not settings.HAILUO_API_KEY:
            return {"status": "skipped", "reason": "HAILUO_API_KEY not configured", "generator": "hailuo"}

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    "https://api.minimaxi.chat/v1/video_generation",
                    headers={
                        "Authorization": f"Bearer {settings.HAILUO_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "video-01",
                        "prompt": prompt.get("main_prompt", ""),
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "submitted",
                        "job_id": data.get("task_id"),
                        "generator": "hailuo",
                    }
                else:
                    return {"status": "failed", "generator": "hailuo", "error": response.text}
            except Exception as e:
                logger.error(f"Hailuo generation error: {e}")
                return {"status": "failed", "generator": "hailuo", "error": str(e)}

    async def generate_image_with_dalle3(self, prompt: str, size: str = "1024x1024") -> dict:
        """Generate image using DALL-E 3."""
        if not settings.OPENAI_API_KEY:
            return {"status": "skipped", "reason": "OPENAI_API_KEY not configured"}

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        size_map = {
            "1:1": "1024x1024",
            "1.91:1": "1792x1024",
            "9:16": "1024x1792",
        }

        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt[:4000],
                size=size_map.get(size, "1024x1024"),
                quality="hd",
                n=1,
            )
            return {
                "status": "completed",
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "generator": "dalle3",
            }
        except Exception as e:
            logger.error(f"DALL-E 3 error: {e}")
            return {"status": "failed", "generator": "dalle3", "error": str(e)}

    async def generate_video(self, script_with_prompt: dict) -> dict:
        """Generate video using best available generator."""
        prompt = script_with_prompt.get("video_generation", {})
        generator = prompt.get("generator", "kling")

        generators = {
            "kling": self.generate_with_kling,
            "runway": self.generate_with_runway,
            "pika": self.generate_with_pika,
            "hailuo": self.generate_with_hailuo,
        }

        generate_fn = generators.get(generator, self.generate_with_kling)
        result = await generate_fn(prompt)

        return {
            **script_with_prompt,
            "generation_result": result,
        }

    async def run(self, scripts_with_prompts: list[dict]) -> list[dict]:
        """Generate videos for all scripts."""
        tasks = [self.generate_video(script) for script in scripts_with_prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        generated = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Video generation failed: {result}")
                generated.append({"status": "failed", "error": str(result)})
            else:
                generated.append(result)

        logger.info(f"Video generation complete: {len(generated)} videos")
        return generated
