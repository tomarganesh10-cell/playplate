from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.models.user import User
from app.agents.video_generator import VIDEO_PRICING, MONTHLY_COST_ESTIMATE

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/video-generators")
async def get_video_pricing(current_user: User = Depends(get_current_user)):
    """Return full pricing for all video and image generators."""
    return {
        "generators": VIDEO_PRICING,
        "monthly_estimate": MONTHLY_COST_ESTIMATE,
        "exchange_rate": {"usd_to_inr": 83, "note": "Approximate rate — verify before billing"},
        "recommendation": {
            "starter":  {"generators": ["kling_basic", "dalle3_standard"], "monthly_usd": 20,  "monthly_inr": 1665},
            "growth":   {"generators": ["kling_standard", "dalle3_hd"],    "monthly_usd": 40,  "monthly_inr": 3330},
            "premium":  {"generators": ["runway_pro", "pika_standard"],    "monthly_usd": 55,  "monthly_inr": 4565},
        },
    }


@router.get("/video-generators/{generator}")
async def get_generator_pricing(
    generator: str,
    current_user: User = Depends(get_current_user),
):
    """Return pricing for a specific generator."""
    pricing = VIDEO_PRICING.get(generator)
    if not pricing:
        from fastapi import HTTPException
        raise HTTPException(404, f"Generator '{generator}' not found. Available: {list(VIDEO_PRICING.keys())}")
    return pricing


@router.get("/estimate")
async def cost_estimate(
    generator: str = "kling",
    duration_seconds: int = 10,
    videos_per_month: int = 150,
    current_user: User = Depends(get_current_user),
):
    """Estimate monthly cost for a generator given usage."""
    from app.agents.video_generator import VideoGeneratorAgent
    agent = VideoGeneratorAgent()
    per_video = agent.get_cost_estimate(generator, duration_seconds)
    price_per_video = per_video.get("price_usd", 0)

    return {
        "generator": generator,
        "per_video_usd": price_per_video,
        "per_video_inr": round(price_per_video * 83, 2),
        "videos_per_month": videos_per_month,
        "monthly_total_usd": round(price_per_video * videos_per_month, 2),
        "monthly_total_inr": round(price_per_video * 83 * videos_per_month, 2),
        "annual_total_usd": round(price_per_video * videos_per_month * 12, 2),
        "annual_total_inr": round(price_per_video * 83 * videos_per_month * 12, 2),
        "plan_detail": per_video.get("estimated_plan", {}),
        "tip": "Subscribe to monthly plan for better rates vs pay-per-video",
    }
