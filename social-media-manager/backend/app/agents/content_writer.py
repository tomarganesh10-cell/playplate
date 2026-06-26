"""
Agent 2: Content Writer Agent
Writes posts, captions, hashtags for all platforms.
"""
import json
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from loguru import logger

from app.config import settings
from app.models.content import ContentType


PLATFORM_SPECS = {
    ContentType.INSTAGRAM_POST: {
        "max_caption": 2200,
        "max_hashtags": 30,
        "tone": "engaging, visual-first, conversational",
        "format": "Hook → Value → CTA → Hashtags",
    },
    ContentType.FACEBOOK_POST: {
        "max_caption": 63206,
        "max_hashtags": 10,
        "tone": "informative, community-oriented, shareable",
        "format": "Story → Education → Discussion prompt → CTA",
    },
    ContentType.LINKEDIN_POST: {
        "max_caption": 3000,
        "max_hashtags": 5,
        "tone": "professional, authoritative, expert",
        "format": "Insight → Data/Experience → Takeaway → CTA",
    },
    ContentType.YOUTUBE_SHORT: {
        "max_caption": 5000,
        "max_hashtags": 15,
        "tone": "educational, direct, high-energy",
        "format": "Hook (3s) → Main content → CTA → Subscribe",
    },
    ContentType.INSTAGRAM_REEL: {
        "max_caption": 2200,
        "max_hashtags": 30,
        "tone": "trendy, fun, educational, relatable",
        "format": "Hook → Quick tips → CTA → Hashtags",
    },
}

HASHTAG_SETS = {
    "dental_general": [
        "#DentalHealth", "#OralCare", "#DentistLife", "#TeethCare",
        "#DentalTips", "#HealthySmile", "#ToothCare",
    ],
    "cosmetic": [
        "#CosmeticDentistry", "#SmileMakeover", "#BeautifulSmile",
        "#DentalAesthetics", "#PerfectSmile", "#SmileDesign",
    ],
    "chandigarh": [
        "#ChandigarhDentist", "#ChandigarhSmile", "#DrAnshuGupta",
        "#ChandigarhDentalClinic", "#BestDentistChandigarh",
        "#Chandigarh", "#ChandigarhHealthcare",
    ],
    "implants": [
        "#DentalImplants", "#ImplantDentistry", "#MissingTeeth",
        "#DentalImplantIndia", "#ToothReplacement",
    ],
    "kids": [
        "#KidsDentistry", "#PediatricDentist", "#ChildrenDental",
        "#BabysFirstTooth", "#KidsOralHealth",
    ],
    "braces": [
        "#Invisalign", "#Braces", "#OrthodonticTreatment",
        "#ClearAligners", "#StraightTeeth", "#OrthoLife",
    ],
    "india": [
        "#IndianDentist", "#DentistInIndia", "#HealthcareIndia",
        "#IndiaHealth", "#MakeInIndia",
    ],
}


class ContentWriterAgent:
    def __init__(self):
        self.claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def _build_hashtags(self, category: str, platform_type: ContentType) -> list[str]:
        """Build relevant hashtag set for category and platform."""
        tags = list(HASHTAG_SETS["dental_general"])
        tags += HASHTAG_SETS["chandigarh"]
        tags += HASHTAG_SETS["india"]

        category_map = {
            "cosmetic": HASHTAG_SETS["cosmetic"],
            "smile": HASHTAG_SETS["cosmetic"],
            "implant": HASHTAG_SETS["implants"],
            "kids": HASHTAG_SETS["kids"],
            "brace": HASHTAG_SETS["braces"],
            "invisalign": HASHTAG_SETS["braces"],
        }

        for key, tag_list in category_map.items():
            if key in category.lower():
                tags += tag_list

        specs = PLATFORM_SPECS.get(platform_type, {})
        max_tags = specs.get("max_hashtags", 30)
        return list(dict.fromkeys(tags))[:max_tags]

    async def write_post(self, research: dict, platform: ContentType) -> dict:
        """Write a complete post for a specific platform."""
        specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS[ContentType.INSTAGRAM_POST])

        system_prompt = f"""You are an expert social media content writer specializing in dental healthcare content.
You write for Dr. Anshu Gupta — a 27-year experienced Cosmetic Dentist, Aesthetic Dentist, Implantologist,
and Pediatric Dentist based in Chandigarh, India.

Platform: {platform.value}
Tone: {specs['tone']}
Format: {specs['format']}
Max caption: {specs['max_caption']} characters

Dr. Anshu Gupta's expertise:
- Cosmetic & Aesthetic Dentistry (smile makeovers, veneers, bonding)
- Dental Implants (single, multiple, All-on-4)
- Pediatric Dentistry (children's dental care)
- 27+ years of experience
- Clinic: Chandigarh, India
- Website: chandigarhdentist.com

Write in English. Use simple, clear language. Be warm, professional, and educational.
For Indian audience — avoid overly western references. Include local cultural context where natural.
Never make specific price claims. Never make medical guarantees."""

        research_context = f"""
Topic: {research.get('topic', '')}
Category: {research.get('category', '')}
Content Angle: {research.get('angle', research.get('topic', ''))}
Key Points: {json.dumps(research.get('key_points', []))}
Target Audience: {research.get('target_audience', 'Chandigarh residents')}
Emotional Hook: {research.get('emotional_hook', '')}
Local Relevance: {research.get('local_relevance', 'Relevant to Chandigarh patients')}
Suggested CTA: {research.get('cta_suggestion', 'Book a consultation')}
"""

        user_prompt = f"""Write a complete {platform.value} post for Dr. Anshu Gupta's dental clinic.

Research Brief:
{research_context}

Return a JSON object with:
{{
  "title": "Short internal title for this post",
  "body_text": "Full post body text (within character limits)",
  "caption": "Social media caption with emojis",
  "cta": "Call to action line",
  "suggested_image_description": "What the image/visual should show"
}}

Make the caption compelling, educational, and action-oriented.
Include 2-3 relevant emojis. End with the CTA."""

        try:
            if self.claude:
                response = await self.claude.messages.create(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                )
                content_text = response.content[0].text
                # Extract JSON
                import re
                json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                if json_match:
                    post_data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            elif self.openai:
                response = await self.openai.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                )
                post_data = json.loads(response.choices[0].message.content)
            else:
                # Fallback mock data
                post_data = {
                    "title": research.get('topic', 'Dental Health Post'),
                    "body_text": f"Learn about {research.get('topic', 'dental health')} from Dr. Anshu Gupta.",
                    "caption": f"✨ {research.get('topic', 'Dental Health')} - Your smile matters! Book a consultation at chandigarhdentist.com",
                    "cta": "📅 Book your appointment today!",
                    "suggested_image_description": f"Professional dental image related to {research.get('topic', 'dental health')}",
                }

            hashtags = self._build_hashtags(str(research.get('category', '')), platform)
            trending = research.get('trending_hashtags', [])
            all_hashtags = list(dict.fromkeys(trending + hashtags))

            return {
                **post_data,
                "hashtags": all_hashtags[:30],
                "platform": platform.value,
                "category": research.get('category'),
                "topic_key": research.get('topic_key'),
                "research_data": research,
            }

        except Exception as e:
            logger.error(f"Content writer error for {platform}: {e}")
            return {
                "title": research.get('topic', 'Dental Post'),
                "body_text": research.get('topic', 'Dental health is important!'),
                "caption": f"Stay dental healthy! 😊 #DentalHealth #ChandigarhDentist",
                "cta": "Book your appointment at chandigarhdentist.com",
                "hashtags": self._build_hashtags(str(research.get('category', '')), platform),
                "platform": platform.value,
                "category": research.get('category'),
                "topic_key": research.get('topic_key'),
                "research_data": research,
                "suggested_image_description": "Professional dental clinic image",
            }

    async def run(self, researched_topics: list[dict], platforms: list[ContentType] = None) -> list[dict]:
        """Write content for all researched topics across platforms."""
        if platforms is None:
            platforms = [
                ContentType.INSTAGRAM_POST,
                ContentType.FACEBOOK_POST,
                ContentType.LINKEDIN_POST,
            ]

        all_posts = []
        for research in researched_topics:
            for platform in platforms:
                post = await self.write_post(research, platform)
                all_posts.append(post)
                logger.info(f"Written {platform.value} post for: {research.get('topic', 'unknown')}")

        return all_posts
