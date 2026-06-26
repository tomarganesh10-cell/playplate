"""
Website Scraper — crawls chandigarhdentist.com and builds knowledge base.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from loguru import logger
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.config import settings
from app.models.knowledge_base import KnowledgeBase


CRAWL_URLS = [
    "https://www.chandigarhdentist.com",
    "https://www.chandigarhdentist.com/about",
    "https://www.chandigarhdentist.com/services",
    "https://www.chandigarhdentist.com/treatments",
    "https://www.chandigarhdentist.com/testimonials",
    "https://www.chandigarhdentist.com/contact",
    "https://www.chandigarhdentist.com/blog",
    "https://www.chandigarhdentist.com/gallery",
    "https://www.chandigarhdentist.com/faq",
]

PAGE_CATEGORY_MAP = {
    "about": "about_doctor",
    "services": "services",
    "treatments": "treatments",
    "procedures": "procedures",
    "testimonials": "testimonials",
    "contact": "clinic_info",
    "faq": "faqs",
    "blog": "blog",
    "gallery": "gallery",
    "team": "about_doctor",
    "technology": "technology",
}

HARDCODED_KB = [
    {
        "category": "about_doctor",
        "title": "Dr. Anshu Gupta — Profile",
        "content": """Dr. Anshu Gupta is a highly experienced Cosmetic Dentist, Aesthetic Dentist,
Implantologist, and Pediatric Dentist based in Chandigarh, India, with over 27 years of clinical experience.

She is known for her gentle approach, precision work, and exceptional patient care. Dr. Gupta has
completed advanced training in cosmetic and implant dentistry from prestigious international institutions.

Specializations:
- Cosmetic Dentistry (Veneers, Bonding, Smile Makeovers)
- Aesthetic Dentistry (Smile Design, Gum Contouring)
- Implantology (Single/Multiple Implants, All-on-4, All-on-6)
- Pediatric Dentistry (Children's Dental Care, Preventive Dentistry)

Clinic: Chandigarh Dentist
Website: https://www.chandigarhdentist.com
Location: Chandigarh, India""",
        "source_url": "https://www.chandigarhdentist.com/about",
        "tags": ["doctor", "experience", "cosmetic", "implant", "pediatric"],
    },
    {
        "category": "services",
        "title": "Dental Services — Chandigarh Dentist",
        "content": """Complete range of dental services offered at Chandigarh Dentist:

COSMETIC DENTISTRY:
- Smile Makeover (Complete transformation)
- Dental Veneers (Porcelain and Composite)
- Teeth Whitening (In-office Laser whitening)
- Dental Bonding
- Gum Contouring / Gummy Smile Correction
- Digital Smile Design

RESTORATIVE DENTISTRY:
- Dental Implants (Single tooth, Multiple teeth, Full mouth)
- All-on-4 / All-on-6 Implants
- Dental Crowns and Bridges
- Root Canal Treatment (Painless)
- Tooth Colored Fillings
- Dentures (Complete and Partial)

ORTHODONTICS:
- Invisalign Clear Aligners
- Metal Braces
- Ceramic Braces
- Lingual Braces
- Retainers

PEDIATRIC DENTISTRY:
- Child-friendly Dental Care
- Fluoride Treatment
- Dental Sealants
- Space Maintainers
- Habit Breaking Appliances

PREVENTIVE DENTISTRY:
- Teeth Cleaning (Scaling & Polishing)
- Oral Cancer Screening
- Digital X-rays
- Dental Checkups""",
        "source_url": "https://www.chandigarhdentist.com/services",
        "tags": ["services", "cosmetic", "implants", "orthodontics", "pediatric", "preventive"],
    },
    {
        "category": "technology",
        "title": "Advanced Technology at Chandigarh Dentist",
        "content": """State-of-the-art technology used at Chandigarh Dentist:

- CEREC Same-Day Crowns (CAD/CAM technology)
- 3D Cone Beam CT Scanner
- Digital X-ray (90% less radiation)
- Laser Dentistry (painless treatments)
- Digital Smile Design Software
- Intraoral Camera
- Air Abrasion Technology
- Piezo Surgery for Implants
- Magnification Loupes for precision

All procedures follow international sterilization protocols (ISO standards).""",
        "source_url": "https://www.chandigarhdentist.com",
        "tags": ["technology", "CEREC", "laser", "3D", "digital"],
    },
    {
        "category": "clinic_info",
        "title": "Clinic Location and Contact",
        "content": """Chandigarh Dentist Clinic Information:

Location: Chandigarh, India (Serving Chandigarh, Mohali, Panchkula, Punjab)
Website: https://www.chandigarhdentist.com

Appointment: Available by prior appointment
Timing: Monday to Saturday, 10 AM to 7 PM

Services Area: Chandigarh, Mohali, Panchkula, Punjab, Haryana

The clinic is equipped with modern facilities and follows strict hygiene and sterilization protocols.""",
        "source_url": "https://www.chandigarhdentist.com/contact",
        "tags": ["location", "contact", "hours", "chandigarh", "clinic"],
    },
    {
        "category": "treatments",
        "title": "Smile Makeover — Complete Guide",
        "content": """A Smile Makeover at Chandigarh Dentist can include:

1. Digital Smile Design (DSD) — Plan your smile digitally before treatment
2. Dental Veneers — Ultra-thin porcelain shells that transform teeth
3. Teeth Whitening — Professional grade whitening for dramatic results
4. Dental Implants — For missing teeth replacement
5. Orthodontics — Straightening teeth with Invisalign or braces
6. Gum Contouring — Perfect the shape of your gumline
7. Composite Bonding — Affordable cosmetic improvement

Results: Natural-looking, long-lasting, life-changing smile
Timeline: 1 visit to several weeks depending on complexity
Technology: Digital planning, CEREC same-day crowns available""",
        "source_url": "https://www.chandigarhdentist.com/treatments",
        "tags": ["smile makeover", "veneers", "whitening", "transform", "cosmetic"],
    },
    {
        "category": "faqs",
        "title": "Patient Frequently Asked Questions",
        "content": """Common patient questions at Chandigarh Dentist:

Q: Is a root canal painful?
A: With modern techniques and local anesthesia, root canal treatment is virtually painless. Most patients report it's no more uncomfortable than a regular filling.

Q: How long do dental implants last?
A: With proper care, dental implants can last a lifetime. The crown portion may need replacement after 15-20 years.

Q: Is teeth whitening safe?
A: Professional teeth whitening done under dental supervision is safe and effective. We customize treatment for sensitive teeth.

Q: At what age should children first visit the dentist?
A: Children should visit the dentist by their first birthday or within 6 months of their first tooth appearing.

Q: How long does Invisalign take?
A: Treatment time varies from 6-18 months depending on complexity. Mild cases may take as little as 3-6 months.

Q: Can adults get braces?
A: Absolutely! Adults can benefit from orthodontic treatment at any age. We offer discreet options like Invisalign and ceramic braces.

Q: How much do dental implants cost in Chandigarh?
A: Cost varies based on the number of implants and complexity. We offer consultation to provide personalized estimates.

Q: What is digital smile design?
A: DSD uses software to digitally plan your new smile before any treatment begins, allowing you to see your expected results in advance.""",
        "source_url": "https://www.chandigarhdentist.com/faq",
        "tags": ["faq", "questions", "answers", "root canal", "implants", "whitening", "children"],
    },
    {
        "category": "achievements",
        "title": "Dr. Anshu Gupta Achievements and Recognition",
        "content": """Dr. Anshu Gupta's achievements in dentistry:

- 27+ years of clinical excellence in Chandigarh
- Advanced training in cosmetic and implant dentistry
- Thousands of successful smile makeovers
- Expertise in complex implant cases
- Pioneer of digital smile design in the region
- International training and certifications
- Trusted by patients from across Punjab, Haryana, and beyond
- Known for gentle, patient-centered approach
- Regular continuing education and training updates""",
        "source_url": "https://www.chandigarhdentist.com/about",
        "tags": ["achievements", "recognition", "experience", "training", "expertise"],
    },
]


class WebsiteScraper:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.CLIENT_WEBSITE
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; PlayplateBot/1.0; +https://social.playplate.in)",
        }

    def _determine_category(self, url: str, page_title: str = "") -> str:
        """Determine KB category from URL and page title."""
        url_lower = url.lower()
        for keyword, category in PAGE_CATEGORY_MAP.items():
            if keyword in url_lower:
                return category
        if "implant" in url_lower or "implant" in page_title.lower():
            return "treatments"
        if "children" in url_lower or "kid" in url_lower:
            return "treatments"
        return "services"

    async def scrape_page(self, url: str) -> Optional[dict]:
        """Scrape a single page and extract content."""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=self.headers)
                if response.status_code != 200:
                    logger.warning(f"Failed to scrape {url}: {response.status_code}")
                    return None

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove nav, footer, scripts
                for tag in soup(["nav", "footer", "script", "style", "head", "header"]):
                    tag.decompose()

                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else url

                # Extract main content
                main = soup.find("main") or soup.find("article") or soup.find(id="content") or soup.find("body")
                if not main:
                    return None

                text = main.get_text(separator="\n", strip=True)
                lines = [line for line in text.split("\n") if len(line.strip()) > 30]
                content = "\n".join(lines[:100])

                if len(content) < 100:
                    return None

                category = self._determine_category(url, title_text)
                return {
                    "category": category,
                    "title": title_text[:500],
                    "content": content[:5000],
                    "source_url": url,
                    "tags": [],
                }
            except Exception as e:
                logger.error(f"Scraping error for {url}: {e}")
                return None

    async def save_to_kb(self, entry: dict) -> None:
        """Save or update a knowledge base entry."""
        result = await self.db.execute(
            select(KnowledgeBase).where(KnowledgeBase.source_url == entry.get("source_url"))
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.content = entry["content"]
            existing.title = entry["title"]
            existing.last_crawled = datetime.utcnow()
        else:
            kb_entry = KnowledgeBase(
                category=entry["category"],
                title=entry["title"],
                content=entry["content"],
                source_url=entry.get("source_url"),
                tags=entry.get("tags", []),
                last_crawled=datetime.utcnow(),
            )
            self.db.add(kb_entry)

        await self.db.commit()

    async def seed_hardcoded_knowledge(self) -> int:
        """Seed the database with hardcoded knowledge base entries."""
        count = 0
        for entry in HARDCODED_KB:
            result = await self.db.execute(
                select(KnowledgeBase).where(KnowledgeBase.title == entry["title"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                kb_entry = KnowledgeBase(**entry)
                self.db.add(kb_entry)
                count += 1

        await self.db.commit()
        logger.info(f"Seeded {count} hardcoded knowledge base entries")
        return count

    async def run(self, seed_hardcoded: bool = True) -> dict:
        """Full scraping run."""
        results = {"scraped": 0, "failed": 0, "seeded": 0}

        if seed_hardcoded:
            results["seeded"] = await self.seed_hardcoded_knowledge()

        for url in CRAWL_URLS:
            entry = await self.scrape_page(url)
            if entry:
                await self.save_to_kb(entry)
                results["scraped"] += 1
                logger.info(f"Scraped: {url}")
            else:
                results["failed"] += 1
            await asyncio.sleep(2)

        logger.info(f"Scraping complete: {results}")
        return results
