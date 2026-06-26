"""
Agent 4: Prompt Engineer
Optimizes prompts for image and video generation (DALL-E 3, Stable Diffusion, Kling, Runway, Pika).
"""
import json
from openai import AsyncOpenAI
from loguru import logger
from app.config import settings


IMAGE_STYLE_PRESETS = {
    "dental_professional": "clean, modern dental clinic, professional healthcare setting, warm lighting, "
                           "soft white and blue tones, minimalist aesthetic",
    "educational": "clean infographic style, professional typography, dental illustration, "
                   "medical accuracy, educational poster design",
    "smile_focus": "close-up of beautiful healthy teeth, perfect smile, "
                   "natural lighting, high-end dental photography style",
    "kids_friendly": "bright colors, friendly cartoon-like dental illustration, "
                     "child-friendly, warm and inviting, safe and clean",
    "before_after": "professional dental photography, clinical setting, "
                    "neutral background, clinical documentation style",
    "festive": "Indian festival colors, celebration mood, dental health theme, "
               "vibrant but professional, culturally relevant",
}

VIDEO_STYLE_PRESETS = {
    "kling": "Cinematic 4K, smooth motion, professional healthcare setting, "
             "doctor explaining with confident gestures, clean background, warm lighting",
    "runway": "Stable motion, professional B-roll footage, dental clinic environment, "
              "medical professional, documentary style",
    "pika": "Smooth animation, modern dental illustration, clean motion graphics, "
            "professional medical content",
    "hailuo": "High quality video generation, realistic medical setting, "
              "professional doctor presenting information",
}


class PromptEngineerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_image_prompt(self, post_data: dict) -> dict:
        """Generate optimized image prompt for DALL-E 3 / Stable Diffusion."""
        category = str(post_data.get("category", ""))
        suggested_visual = post_data.get("suggested_image_description", "")
        topic = post_data.get("topic", post_data.get("title", ""))
        platform = post_data.get("platform", "instagram_post")

        # Determine aspect ratio by platform
        aspect_ratios = {
            "instagram_post": "1:1 square",
            "facebook_post": "1.91:1 landscape",
            "linkedin_post": "1.91:1 landscape",
            "instagram_reel": "9:16 vertical",
            "youtube_short": "9:16 vertical",
        }
        aspect = aspect_ratios.get(platform, "1:1 square")

        style_key = "dental_professional"
        if "kids" in category.lower():
            style_key = "kids_friendly"
        elif "smile" in category.lower() or "before_after" in category.lower():
            style_key = "smile_focus"
        elif "education" in category.lower() or "awareness" in category.lower():
            style_key = "educational"
        elif "festival" in category.lower():
            style_key = "festive"

        base_style = IMAGE_STYLE_PRESETS[style_key]

        if not self.client:
            return {
                "dalle3_prompt": f"Professional dental image for {topic}. {base_style}. {aspect}, no text overlay.",
                "stable_diffusion_prompt": f"dental clinic professional {topic}, {base_style}",
                "negative_prompt": "ugly, blurry, cartoon, anime, text, watermark, logo",
                "aspect_ratio": aspect,
                "style": style_key,
            }

        user_prompt = f"""Generate an optimized image prompt for dental social media content.

Topic: {topic}
Category: {category}
Platform: {platform}
Aspect Ratio: {aspect}
Suggested Visual: {suggested_visual}
Base Style: {base_style}

Create:
1. A detailed DALL-E 3 prompt (max 4000 chars)
2. A Stable Diffusion prompt (concise, tag-based)
3. A negative prompt for Stable Diffusion

Rules:
- No real identifiable people (use "a professional dentist" not specific names)
- Professional healthcare aesthetic
- No text in image (text will be added as overlay)
- Appropriate for Indian audience
- High quality, photorealistic style

Return JSON:
{{
  "dalle3_prompt": "...",
  "stable_diffusion_prompt": "...",
  "negative_prompt": "...",
  "aspect_ratio": "{aspect}",
  "style": "{style_key}"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Prompt engineer image error: {e}")
            return {
                "dalle3_prompt": f"Professional dental clinic, {topic}, {base_style}, {aspect}",
                "stable_diffusion_prompt": f"dental clinic, professional, {topic}",
                "negative_prompt": "ugly, blurry, text, watermark",
                "aspect_ratio": aspect,
                "style": style_key,
            }

    async def generate_video_prompt(self, script: dict, generator: str = "kling") -> dict:
        """Generate optimized video prompts for different video generators."""
        topic = script.get("title", "dental health")
        video_type = script.get("video_type", "educational")
        base_style = VIDEO_STYLE_PRESETS.get(generator, VIDEO_STYLE_PRESETS["kling"])

        existing_prompt = script.get("video_prompt", "")

        if not self.client:
            return {
                "generator": generator,
                "main_prompt": f"{base_style}. Topic: {topic}. {existing_prompt}",
                "style_prompt": base_style,
                "negative_prompt": "shaky camera, poor quality, unprofessional",
                "duration": script.get("duration_seconds", 30),
                "aspect_ratio": "9:16",
                "fps": 24,
            }

        user_prompt = f"""Optimize this video generation prompt for {generator.upper()} video AI.

Topic: {topic}
Video Type: {video_type}
Duration: {script.get('duration_seconds', 30)} seconds
Base Style: {base_style}
Initial Prompt: {existing_prompt}

Scenes Summary:
{json.dumps(script.get('scenes', [])[:3], indent=2)}

Create an optimized prompt for {generator} that will generate professional dental healthcare video content.

Return JSON:
{{
  "generator": "{generator}",
  "main_prompt": "Detailed scene-by-scene or overall prompt",
  "style_prompt": "Style and quality descriptors",
  "negative_prompt": "What to avoid",
  "duration": {script.get('duration_seconds', 30)},
  "aspect_ratio": "9:16",
  "fps": 24,
  "scene_prompts": ["prompt for scene 1", "prompt for scene 2"]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Prompt engineer video error: {e}")
            return {
                "generator": generator,
                "main_prompt": f"{base_style}. {topic}",
                "style_prompt": base_style,
                "negative_prompt": "shaky, poor quality, unprofessional",
                "duration": script.get("duration_seconds", 30),
                "aspect_ratio": "9:16",
                "fps": 24,
            }

    async def run(self, posts: list[dict], scripts: list[dict]) -> dict:
        """Generate all prompts for posts and scripts."""
        image_prompts = []
        for post in posts:
            prompt = await self.generate_image_prompt(post)
            image_prompts.append({**post, "image_generation": prompt})

        video_prompts = []
        generators = ["kling", "runway", "pika"]
        for i, script in enumerate(scripts):
            generator = generators[i % len(generators)]
            prompt = await self.generate_video_prompt(script, generator)
            video_prompts.append({**script, "video_generation": prompt})

        logger.info(f"Generated {len(image_prompts)} image prompts and {len(video_prompts)} video prompts")
        return {"posts_with_prompts": image_prompts, "scripts_with_prompts": video_prompts}
