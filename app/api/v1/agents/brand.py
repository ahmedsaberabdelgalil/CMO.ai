import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.brand_agent import (
    BrandAgentRequest,
    BrandAgentResponse,
    BrandSaveResponse,
)
from app.services.brand_agent import (
    extract_brand_profile,
    generate_brand_report,
    run_brand_coaching,
)

router = APIRouter(prefix="/agents/brand", tags=["Brand Agent"])

FIELD_LABELS = {
    "brand_name": "Brand name",
    "industry": "Industry",
    "target_audience": "Target audience",
    "value_proposition": "Value proposition",
    "tone_of_voice": "Tone of voice",
    "positioning": "Positioning",
}


async def _load_context(data: BrandAgentRequest, db: AsyncSession) -> dict:
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    return {
        "brand_name": brand.brand_name if brand else "Brand",
        "industry": brand.industry if brand and brand.industry else "General",
        "audience": (
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        "campaign_name": campaign.name,
        "campaign_notes": campaign.description or "None",
    }


@router.post("/generate", response_model=BrandAgentResponse)
async def generate_brand_coaching(
    data: BrandAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    context = await _load_context(data, db)
    history = [turn.model_dump() for turn in data.messages]

    output = await asyncio.to_thread(run_brand_coaching, history=history, **context)
    return BrandAgentResponse(**output)


@router.post("/report", response_model=BrandAgentResponse)
async def generate_report(
    data: BrandAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    context = await _load_context(data, db)
    history = [turn.model_dump() for turn in data.messages]

    output = await asyncio.to_thread(generate_brand_report, history=history, **context)
    return BrandAgentResponse(**output)


@router.post("/save", response_model=BrandSaveResponse)
async def save_brand_profile(
    data: BrandAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found for this campaign")
    if brand.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this brand")

    history = [turn.model_dump() for turn in data.messages]
    extraction = await asyncio.to_thread(extract_brand_profile, history=history)

    if extraction["status"] != "success":
        return BrandSaveResponse(
            status="error",
            response=None,
            saved_fields={},
            error_message=extraction.get("error_message"),
        )

    profile: dict[str, str] = extraction["profile"]
    if not profile:
        return BrandSaveResponse(
            status="error",
            response=None,
            saved_fields={},
            error_message=(
                "I couldn't find enough brand details yet. Answer a few more questions "
                "about your business, audience, and value proposition first."
            ),
        )

    saved: dict[str, str] = {}
    for field, value in profile.items():
        setattr(brand, field, value)
        saved[field] = value

    await db.commit()
    await db.refresh(brand)

    summary_lines = [f"{FIELD_LABELS.get(k, k)}: {v}" for k, v in saved.items()]
    summary = "Saved your brand profile:\n" + "\n".join(summary_lines)

    return BrandSaveResponse(
        status="success",
        response=summary,
        saved_fields=saved,
        error_message=None,
    )
