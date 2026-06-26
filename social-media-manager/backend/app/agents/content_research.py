"""
Agent 1: Content Research Agent
Pulls relevant topics from knowledge base, checks topic history,
identifies what's trending in dental health, and prepares research brief.
"""
import json
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from openai import AsyncOpenAI
from loguru import logger

from app.config import settings
from app.models.knowledge_base import KnowledgeBase
from app.models.topic_history import TopicHistory
from app.models.content import ContentCategory


CONTENT_CATEGORIES = [
    ContentCategory.DENTAL_AWARENESS,
    ContentCategory.MYTH_VS_FACT,
    ContentCategory.PATIENT_EDUCATION,
    ContentCategory.SMILE_MAKEOVER,
    ContentCategory.KIDS_DENTISTRY,
    ContentCategory.DENTAL_IMPLANTS,
    ContentCategory.BRACES,
    ContentCategory.TEETH_WHITENING,
    ContentCategory.ORAL_HYGIENE,
    ContentCategory.PATIENT_JOURNEY,
    ContentCategory.DOCTOR_INTRO,
    ContentCategory.CLINIC_TOUR,
    ContentCategory.FAQ,
    ContentCategory.FESTIVAL,
    ContentCategory.LOCAL_CONTENT,
    ContentCategory.BEFORE_AFTER,
]

DENTAL_TOPICS_POOL = {
    ContentCategory.DENTAL_AWARENESS: [
        "World Oral Health Day awareness",
        "Importance of 6-month dental checkups",
        "Early signs of gum disease",
        "Dental anxiety tips",
        "Fluoride and dental health",
        "The link between oral and overall health",
    ],
    ContentCategory.MYTH_VS_FACT: [
        "Myth: Sugar is the only cause of cavities",
        "Myth: Baby teeth don't matter",
        "Myth: Whitening damages enamel",
        "Myth: You only need a dentist when in pain",
        "Myth: Bleeding gums is normal",
        "Myth: Electric toothbrushes are too harsh",
    ],
    ContentCategory.SMILE_MAKEOVER: [
        "Smile makeover transformation journey",
        "Veneers vs Bonding — which is right for you?",
        "Complete smile redesign process",
        "Digital smile design technology",
        "What a smile makeover can fix",
    ],
    ContentCategory.KIDS_DENTISTRY: [
        "First dental visit — what to expect",
        "Protecting kids' teeth during sports",
        "Thumb sucking and dental effects",
        "Space maintainers for children",
        "Making brushing fun for kids",
        "When do kids need braces?",
    ],
    ContentCategory.DENTAL_IMPLANTS: [
        "Dental implants — the permanent tooth solution",
        "Implant vs bridge — pros and cons",
        "Implant procedure step by step",
        "Are you a candidate for implants?",
        "How long do implants last?",
        "All-on-4 implants explained",
    ],
    ContentCategory.TEETH_WHITENING: [
        "Professional whitening vs store-bought kits",
        "Laser teeth whitening explained",
        "Foods that stain teeth",
        "Whitening for sensitive teeth",
        "How long does whitening last?",
    ],
    ContentCategory.ORAL_HYGIENE: [
        "Correct brushing technique",
        "Importance of flossing daily",
        "Tongue cleaning benefits",
        "Mouthwash — do you really need it?",
        "Water flosser vs string floss",
        "Best time to brush — before or after breakfast?",
    ],
    ContentCategory.BRACES: [
        "Invisalign vs traditional braces",
        "Adult braces — it's never too late",
        "How braces work",
        "Life with braces — tips",
        "Retainers after braces",
        "Clear aligners for teens",
    ],
    ContentCategory.PATIENT_EDUCATION: [
        "Root canal — demystifying the procedure",
        "Crown vs filling — when do you need which?",
        "Sealants for cavity prevention",
        "Understanding dental X-rays",
        "Bone grafting explained simply",
    ],
    ContentCategory.LOCAL_CONTENT: [
        "Best dental care in Chandigarh",
        "Why Chandigarh patients choose Dr. Anshu Gupta",
        "Dental tourism in Chandigarh",
        "State-of-the-art dental clinic in Sector 9",
        "Serving Chandigarh for 27+ years",
    ],
    ContentCategory.FESTIVAL: [
        "Diwali special smile offer",
        "New Year smile resolution",
        "Navratri — smile makeover offer",
        "Raksha Bandhan — gift of a healthy smile",
        "Children's Day — free dental camp",
    ],
    ContentCategory.BEFORE_AFTER: [
        "Veneer transformation — before and after",
        "Implant restoration — patient story",
        "Invisalign journey — 6 months transformation",
        "Smile redesign reveal",
        "Gum treatment — gummy smile correction",
    ],
    ContentCategory.DOCTOR_INTRO: [
        "Meet Dr. Anshu Gupta — 27 years of expertise",
        "Why choose a cosmetic specialist?",
        "Dr. Gupta's approach to pain-free dentistry",
        "International training and certifications",
        "A day at Chandigarh Dentist clinic",
    ],
    ContentCategory.CLINIC_TOUR: [
        "Our state-of-the-art sterilization process",
        "CEREC technology — same-day crowns",
        "3D cone beam CT scanner",
        "Digital X-ray technology",
        "Laser dentistry at our clinic",
    ],
    ContentCategory.FAQ: [
        "How painful is a root canal?",
        "How much do implants cost?",
        "How long does a veneer last?",
        "Is teeth whitening safe during pregnancy?",
        "How often should kids visit the dentist?",
    ],
    ContentCategory.PATIENT_JOURNEY: [
        "From fear to confidence — patient story",
        "Complete smile transformation in 2 weeks",
        "Patient flew from abroad for treatment",
        "How Invisalign changed my life",
        "My implant journey — 6 months follow-up",
    ],
}


class ContentResearchAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.cooldown_days = settings.TOPIC_COOLDOWN_DAYS

    async def get_available_topics(self, count: int = 5) -> list[dict]:
        """Get topics not used in the last COOLDOWN_DAYS days."""
        cooldown_date = datetime.utcnow() - timedelta(days=self.cooldown_days)

        # Get recently used topic keys
        result = await self.db.execute(
            select(TopicHistory.topic_key).where(
                TopicHistory.last_used >= cooldown_date
            )
        )
        used_keys = {row[0] for row in result.fetchall()}

        # Build available topics list
        available = []
        for category, topics in DENTAL_TOPICS_POOL.items():
            for topic in topics:
                topic_key = f"{category}::{topic.lower().replace(' ', '_')[:50]}"
                if topic_key not in used_keys:
                    available.append({
                        "category": category,
                        "topic": topic,
                        "topic_key": topic_key,
                    })

        # Mix categories for variety
        import random
        random.shuffle(available)

        # Try to get variety across categories
        selected = []
        seen_categories = set()
        for item in available:
            if item["category"] not in seen_categories or len(selected) < count:
                selected.append(item)
                seen_categories.add(item["category"])
            if len(selected) >= count:
                break

        return selected[:count]

    async def get_knowledge_base_context(self, category: str) -> str:
        """Pull relevant knowledge base entries for a topic category."""
        result = await self.db.execute(
            select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.is_active == True,
                    KnowledgeBase.category == category
                )
            ).limit(5)
        )
        entries = result.scalars().all()
        if not entries:
            return ""
        return "\n\n".join([f"## {e.title}\n{e.content[:800]}" for e in entries])

    async def research_topic(self, topic: dict, kb_context: str) -> dict:
        """Use GPT-4o to research and expand on a topic."""
        if not self.client:
            return {**topic, "research": topic["topic"], "key_points": [], "angle": topic["topic"]}

        system_prompt = """You are a dental content research expert for Dr. Anshu Gupta,
        a 27-year experienced Cosmetic Dentist, Aesthetic Dentist, Implantologist, and Pediatric Dentist
        based in Chandigarh, India. Your role is to research dental topics and provide content angles
        that will resonate with Indian patients, specifically in Chandigarh and Punjab region.

        Always keep the tone professional yet warm and educational.
        Incorporate local cultural context where relevant."""

        user_prompt = f"""Research the following dental topic for social media content:

Topic: {topic['topic']}
Category: {topic['category']}

Clinic Knowledge Base Context:
{kb_context if kb_context else 'Not available - use general dental knowledge'}

Dr. Anshu Gupta's specialties: Cosmetic Dentistry, Aesthetic Dentistry, Implantology, Pediatric Dentistry
Location: Chandigarh, India
Experience: 27+ years
Website: https://www.chandigarhdentist.com

Provide a JSON response with:
{{
  "angle": "The specific content angle to take",
  "key_points": ["point 1", "point 2", "point 3"],
  "target_audience": "Who this content is for",
  "emotional_hook": "What emotion/pain point this addresses",
  "local_relevance": "How this is relevant to Chandigarh patients",
  "cta_suggestion": "What action to prompt",
  "trending_hashtags": ["#hashtag1", "#hashtag2"]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            research_data = json.loads(response.choices[0].message.content)
            return {**topic, **research_data}
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            return {**topic, "angle": topic["topic"], "key_points": [], "emotional_hook": ""}

    async def run(self, count: int = 5) -> list[dict]:
        """Main agent runner — returns researched topics."""
        logger.info(f"Content Research Agent starting — selecting {count} topics")
        topics = await self.get_available_topics(count)

        researched = []
        for topic in topics:
            kb_context = await self.get_knowledge_base_context(topic["category"])
            research = await self.research_topic(topic, kb_context)
            researched.append(research)
            logger.info(f"Researched topic: {topic['topic']}")

        return researched
