"""
Agent 3: Video Script Writer
Creates structured video scripts with scenes, voiceover, CTA for reels/shorts.
"""
import json
from openai import AsyncOpenAI
from loguru import logger
from app.config import settings


VIDEO_DURATIONS = {
    "reel_15": {"duration": 15, "scenes": 3, "words_per_second": 2.5},
    "reel_30": {"duration": 30, "scenes": 5, "words_per_second": 2.5},
    "reel_60": {"duration": 60, "scenes": 8, "words_per_second": 2.5},
    "short_60": {"duration": 60, "scenes": 8, "words_per_second": 2.5},
}

VIDEO_TYPES = {
    "educational": {
        "style": "Clean, professional, text overlays with doctor or clinic visuals",
        "music": "Calm, professional background music",
        "opening": "Bold fact or question hook",
    },
    "myth_vs_fact": {
        "style": "Split screen, bold text, animated reveals",
        "music": "Energetic but professional",
        "opening": "❌ MYTH: [statement] reveal → ✅ FACT: [truth]",
    },
    "before_after": {
        "style": "Side-by-side comparison with smooth transition",
        "music": "Uplifting, inspiring",
        "opening": "The transformation that changed everything...",
    },
    "tips": {
        "style": "Quick cuts, numbered text overlays, clean background",
        "music": "Upbeat, light",
        "opening": "5 things your dentist wants you to know",
    },
    "faq": {
        "style": "Question card → Doctor explains → Answer revealed",
        "music": "Neutral, professional",
        "opening": "The #1 question I get asked every day...",
    },
    "patient_story": {
        "style": "Story-driven, emotional, testimonial style",
        "music": "Heartwarming, gentle",
        "opening": "She was too afraid to smile. Until...",
    },
}


class VideoScriptWriterAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def _get_video_type(self, category: str) -> str:
        mapping = {
            "myth_vs_fact": "myth_vs_fact",
            "before_after": "before_after",
            "oral_hygiene": "tips",
            "dental_awareness": "tips",
            "patient_education": "educational",
            "faq": "faq",
            "patient_journey": "patient_story",
        }
        for key, vtype in mapping.items():
            if key in str(category).lower():
                return vtype
        return "educational"

    async def write_script(self, research: dict, duration_key: str = "reel_30") -> dict:
        """Write a complete video script."""
        duration_config = VIDEO_DURATIONS.get(duration_key, VIDEO_DURATIONS["reel_30"])
        video_type = self._get_video_type(str(research.get('category', '')))
        video_style = VIDEO_TYPES.get(video_type, VIDEO_TYPES["educational"])

        if not self.client:
            return self._mock_script(research, duration_config, video_type)

        system_prompt = """You are an expert video script writer for dental healthcare content.
You create compelling, educational short-form video scripts for social media.
Scripts must be clear, concise, and optimized for the Indian dental healthcare audience.
Dr. Anshu Gupta is a 27-year experienced dentist in Chandigarh — scripts should reflect expertise and warmth."""

        user_prompt = f"""Write a complete video script for Dr. Anshu Gupta's dental clinic.

Topic: {research.get('topic', '')}
Category: {research.get('category', '')}
Content Angle: {research.get('angle', '')}
Key Points: {json.dumps(research.get('key_points', []))}
Video Type: {video_type}
Duration: {duration_config['duration']} seconds
Number of Scenes: {duration_config['scenes']}
Video Style: {video_style['style']}
Music: {video_style['music']}
Opening Hook Style: {video_style['opening']}

Return a JSON with this exact structure:
{{
  "title": "Video title",
  "hook_text": "Opening text shown in first 3 seconds",
  "voiceover_full": "Complete voiceover script (natural speaking pace)",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 5,
      "visual_description": "What appears on screen",
      "text_overlay": "Text shown on screen",
      "voiceover": "What is said during this scene",
      "transition": "cut/fade/zoom/slide"
    }}
  ],
  "background_music": "Music description/mood",
  "cta_scene": {{
    "text": "CTA text on screen",
    "voiceover": "CTA voiceover",
    "visual": "CTA visual description"
  }},
  "caption_for_post": "Instagram/YouTube caption for this video",
  "thumbnail_description": "What the thumbnail should look like",
  "video_prompt": "Prompt for AI video generator (Kling/Runway/Pika style)"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
            )
            script = json.loads(response.choices[0].message.content)
            script["duration_seconds"] = duration_config["duration"]
            script["video_type"] = video_type
            script["category"] = research.get("category")
            script["topic_key"] = research.get("topic_key")
            return script
        except Exception as e:
            logger.error(f"Video script writer error: {e}")
            return self._mock_script(research, duration_config, video_type)

    def _mock_script(self, research: dict, duration_config: dict, video_type: str) -> dict:
        topic = research.get('topic', 'Dental Health')
        return {
            "title": f"Video: {topic}",
            "hook_text": f"Did you know? {topic}",
            "voiceover_full": f"Hi, I'm Dr. Anshu Gupta from Chandigarh. Today we talk about {topic}.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 5,
                    "visual_description": "Doctor at clinic desk",
                    "text_overlay": topic,
                    "voiceover": f"Welcome! Today: {topic}",
                    "transition": "fade"
                }
            ],
            "background_music": "Calm professional",
            "cta_scene": {
                "text": "Book your consultation",
                "voiceover": "Call us or visit chandigarhdentist.com",
                "visual": "Clinic logo and contact"
            },
            "caption_for_post": f"{topic} | Dr. Anshu Gupta | Chandigarh #DentalHealth",
            "thumbnail_description": "Professional dental clinic image with text overlay",
            "video_prompt": f"Professional dental clinic, {topic}, clean modern healthcare setting",
            "duration_seconds": duration_config["duration"],
            "video_type": video_type,
            "category": research.get("category"),
            "topic_key": research.get("topic_key"),
        }

    async def run(self, researched_topics: list[dict], duration_key: str = "reel_30") -> list[dict]:
        """Write video scripts for all topics."""
        scripts = []
        for research in researched_topics:
            script = await self.write_script(research, duration_key)
            scripts.append(script)
            logger.info(f"Written video script for: {research.get('topic', 'unknown')}")
        return scripts
