"""
Agent 5: Video Generator
Integrates with Kling, Runway, Pika, Hailuo, Google Veo for video generation.
"""
import asyncio
import httpx
from loguru import logger
from app.config import settings


class VideoGeneratorAgent:
    """Orchestrates video generation across multiple AI video platforms."""

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
