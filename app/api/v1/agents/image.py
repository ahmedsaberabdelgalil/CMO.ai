import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.image_agent import (
    GeneratedImageOut,
    ImageAgentRequest,
    ImageAgentResponse,
    ImageAgentStatus,
)
from app.services.image_agent import (
    AdPlatform,
    BrandProfile,
    ImageGenerationError,
    ImageRequest,
    ImageSize,
    LogoConfig,
    LogoPosition,
    OUTPUT_DIR,
    _resolve_image_backend,
    run_image_agent,
)

router = APIRouter(prefix="/agents/image", tags=["Image Agent"])

_PLATFORM_MAP = {
    "instagram": AdPlatform.INSTAGRAM,
    "facebook": AdPlatform.FACEBOOK,
    "tiktok": AdPlatform.TIKTOK,
    "linkedin": AdPlatform.LINKEDIN,
    "general": AdPlatform.GENERAL,
}

_SIZE_MAP = {
    "512x512": ImageSize.SQUARE,
    "768x768": ImageSize.MEDIUM,
    "1024x1024": ImageSize.HD,
}


def _map_brand_voice(tone_of_voice: str | None) -> str:
    if not tone_of_voice:
        return "professional"
    lower = tone_of_voice.lower()
    if "playful" in lower or "fun" in lower:
        return "playful"
    if "luxury" in lower or "premium" in lower:
        return "luxury"
    if "warm" in lower or "friendly" in lower:
        return "warm"
    if "bold" in lower or "energetic" in lower:
        return "bold"
    if "natural" in lower or "organic" in lower:
        return "natural"
    return "professional"


def _build_brand_profile(brand: Brand | None) -> BrandProfile:
    return BrandProfile(
        brand_name=brand.brand_name if brand else "Brand",
        industry=brand.industry or "General",
        target_audience=brand.target_audience or "General audience",
        brand_voice=_map_brand_voice(brand.tone_of_voice if brand else None),
        primary_colors=["#2563EB", "#7C3AED"],
        style_keywords=["modern", "professional", "clean"],
        extra_guidelines=(brand.positioning or "") if brand else "",
    )


def _local_path_to_url(local_path: str) -> str:
    """Turn stored path into a URL served by StaticFiles at /uploads."""
    p = Path(local_path)
    try:
        rel = p.relative_to(Path("uploads"))
        return f"/uploads/{rel.as_posix()}"
    except ValueError:
        if p.name:
            return f"/uploads/images/{p.name}"
        return local_path


def _result_to_response(result) -> ImageAgentResponse:
    images_out = [
        GeneratedImageOut(
            image_id=img.image_id,
            request_id=img.request_id,
            local_path=img.local_path,
            image_url=_local_path_to_url(img.local_path),
            prompt_used=img.prompt_used,
            ad_copy=img.ad_copy,
            platform=img.platform,
            size=img.size,
            model_used=img.model_used,
            logo_applied=img.logo_applied,
            metadata=img.metadata or {},
        )
        for img in result.images
    ]
    return ImageAgentResponse(
        request_id=result.request_id,
        brand_name=result.brand_name,
        campaign_goal=result.campaign_goal,
        images=images_out,
        ab_test_ready=result.ab_test_ready,
        generation_time_sec=result.generation_time_sec,
        knowledge_context=result.knowledge_context,
    )


@router.get("/status", response_model=ImageAgentStatus)
async def image_agent_status():
    backend = _resolve_image_backend()
    configured = bool(
        settings.RUNWAY_API_KEY
        if backend == "runway"
        else settings.POLLINATIONS_API_KEY
        if backend == "pollinations"
        else True
    )
    return ImageAgentStatus(
        provider="groq",
        model=settings.GROQ_MODEL,
        image_backend=backend,
        groq_configured=bool(settings.GROQ_API_KEY),
        image_backend_configured=configured,
        output_dir=str(OUTPUT_DIR.resolve()),
    )


@router.post("/generate", response_model=ImageAgentResponse)
async def generate_image(
    data: ImageAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == data.campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(
        select(Brand).where(Brand.id == campaign.brand_id)
    )
    brand = brand_result.scalar_one_or_none()

    campaign_goal = data.message.strip()
    if campaign.description and campaign.description not in campaign_goal:
        campaign_goal = f"{campaign_goal}. Context: {campaign.description}"

    agent_request = ImageRequest(
        brand=_build_brand_profile(brand),
        campaign_goal=campaign_goal,
        platform=_PLATFORM_MAP.get(data.platform, AdPlatform.INSTAGRAM),
        image_size=_SIZE_MAP.get(data.image_size, ImageSize.SQUARE),
        num_variations=data.num_variations,
        ad_copy=data.ad_copy or "",
        logo=LogoConfig(
            enabled=data.logo_enabled,
            position=LogoPosition.BOTTOM_RIGHT,
        ),
    )

    try:
        output = await asyncio.to_thread(run_image_agent, agent_request)
    except ImageGenerationError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image agent error: {str(e)}",
        ) from e

    return _result_to_response(output)


@router.post("/generate-async")
async def generate_image_async(
    data: ImageAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    """Start image generation in the background; poll GET /jobs/{job_id}."""
    from app.services.jobs import job_manager

    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    campaign_goal = data.message.strip()
    if campaign.description and campaign.description not in campaign_goal:
        campaign_goal = f"{campaign_goal}. Context: {campaign.description}"

    agent_request = ImageRequest(
        brand=_build_brand_profile(brand),
        campaign_goal=campaign_goal,
        platform=_PLATFORM_MAP.get(data.platform, AdPlatform.INSTAGRAM),
        image_size=_SIZE_MAP.get(data.image_size, ImageSize.SQUARE),
        num_variations=data.num_variations,
        ad_copy=data.ad_copy or "",
        logo=LogoConfig(enabled=data.logo_enabled, position=LogoPosition.BOTTOM_RIGHT),
    )

    async def _work():
        output = await asyncio.to_thread(run_image_agent, agent_request)
        return _result_to_response(output).model_dump()

    job = job_manager.create("image", _work, owner_id=current_user.id)
    return {"job_id": job.id, "status": job.status}
