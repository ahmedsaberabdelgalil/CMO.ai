import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.video_agent import (
    ReasoningOut,
    ScriptOut,
    VideoAgentRequest,
    VideoAgentResponse,
    VideoPlanOut,
)
from app.services.video_agent.video_agent import build_prompt, run_video_agent

router = APIRouter(prefix="/agents/video", tags=["Video Agent"])


def _map_output(output: dict[str, Any]) -> VideoAgentResponse:
    plan_raw = output.get("video_plan") or {}
    reasoning_raw = output.get("reasoning") or {}
    script_raw = plan_raw.get("script") if isinstance(plan_raw, dict) else {}

    video_plan = None
    if isinstance(plan_raw, dict) and plan_raw:
        video_plan = VideoPlanOut(
            concept=plan_raw.get("concept"),
            script=(
                ScriptOut(
                    hook=script_raw.get("hook") if isinstance(script_raw, dict) else None,
                    body=script_raw.get("body") if isinstance(script_raw, dict) else None,
                    cta=script_raw.get("cta") if isinstance(script_raw, dict) else None,
                )
                if script_raw
                else None
            ),
            scenes=plan_raw.get("scenes") or [],
            visual_style=plan_raw.get("visual_style"),
            audio_style=plan_raw.get("audio_style"),
        )

    reasoning = None
    if isinstance(reasoning_raw, dict) and reasoning_raw:
        reasoning = ReasoningOut(
            psychological_trigger=reasoning_raw.get("psychological_trigger"),
            content_angle=reasoning_raw.get("content_angle"),
            hook_rationale=reasoning_raw.get("hook_rationale"),
            why_this_works=reasoning_raw.get("why_this_works"),
        )

    return VideoAgentResponse(
        status=output.get("status", "error"),
        video_plan=video_plan,
        reasoning=reasoning,
        video_prompt=output.get("video_prompt"),
        video_url=output.get("video_url") or None,
        error_message=output.get("error_message"),
    )


@router.post("/generate", response_model=VideoAgentResponse)
async def generate_video(
    data: VideoAgentRequest,
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

    prompt = build_prompt(
        brand={
            "brand_name": brand.brand_name if brand else "",
            "industry": brand.industry if brand else "",
            "target_audience": brand.target_audience if brand else "",
            "tone_of_voice": brand.tone_of_voice if brand else "professional",
        },
        campaign={
            "name": campaign.name,
            "description": campaign.description,
        },
        user_message=data.message,
    )

    try:
        output = await asyncio.to_thread(
            run_video_agent,
            prompt,
            brand={
                "brand_name": brand.brand_name if brand else "",
                "industry": brand.industry if brand else "",
                "target_audience": brand.target_audience if brand else "",
                "tone_of_voice": brand.tone_of_voice if brand else "professional",
            },
            campaign={
                "name": campaign.name,
                "description": campaign.description,
            },
            user_message=data.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video agent error: {str(e)}",
        ) from e

    return _map_output(output)


@router.post("/generate-async")
async def generate_video_async(
    data: VideoAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    """Start video generation in the background; poll GET /jobs/{job_id}."""
    from app.services.jobs import job_manager

    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    brand_dict = {
        "brand_name": brand.brand_name if brand else "",
        "industry": brand.industry if brand else "",
        "target_audience": brand.target_audience if brand else "",
        "tone_of_voice": brand.tone_of_voice if brand else "professional",
    }
    campaign_dict = {"name": campaign.name, "description": campaign.description}
    prompt = build_prompt(
        brand=brand_dict, campaign=campaign_dict, user_message=data.message
    )

    async def _work():
        output = await asyncio.to_thread(
            run_video_agent,
            prompt,
            brand=brand_dict,
            campaign=campaign_dict,
            user_message=data.message,
        )
        return _map_output(output).model_dump()

    job = job_manager.create("video", _work, owner_id=current_user.id)
    return {"job_id": job.id, "status": job.status}
