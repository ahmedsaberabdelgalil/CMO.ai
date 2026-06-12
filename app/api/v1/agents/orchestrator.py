import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.content_agent import ContentRequest
from app.schemas.agents.orchestrator_agent import (
    OrchestratorAgentRequest,
    OrchestratorAgentResponse,
)
from app.services.orchestrator_agent import route_intent

router = APIRouter(prefix="/agents/orchestrator", tags=["Orchestrator Agent"])

AGENT_LABELS = {
    "content": "Text Generation",
    "image": "Image Generation",
    "video": "Video Generation",
    "marketing": "Market Planner",
    "calendar": "Market Calendar",
    "analytics": "Performance Analytics",
    "brand": "Brand Coaching",
    "chatbot": "Support Chatbot",
}


def _brand_context(brand: Brand | None, campaign: Campaign) -> dict:
    return {
        "brand_name": brand.brand_name if brand else "Brand",
        "industry": brand.industry if brand and brand.industry else "General",
        "audience": (
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        "campaign_name": campaign.name,
        "campaign_notes": campaign.description or "None",
    }


@router.post("/generate", response_model=OrchestratorAgentResponse)
async def orchestrate(
    data: OrchestratorAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    message = data.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()
    ctx = _brand_context(brand, campaign)

    history = [turn.model_dump() for turn in data.messages]
    recent_context = _recent_context(history)

    routing = await asyncio.to_thread(route_intent, message, recent_context)
    agent = routing["agent"]
    reason = routing.get("reason", "")

    output = await _dispatch(
        agent, message, history, campaign, brand, ctx, current_user.id, db
    )

    return OrchestratorAgentResponse(
        status=output.get("status", "success"),
        agent=agent,
        agent_label=AGENT_LABELS.get(agent, agent.title()),
        reason=reason,
        response=output.get("response"),
        error_message=output.get("error_message"),
        image_result=output.get("image_result"),
        video_result=output.get("video_result"),
    )


def _recent_context(history: list[dict], limit: int = 6) -> str:
    """Build a short plain-text transcript of the last few turns."""
    turns = [t for t in history if t.get("content")][-limit:]
    return "\n".join(f"{t.get('role', 'user')}: {t.get('content')}" for t in turns)


def _enrich(message: str, history: list[dict]) -> str:
    """Fold recent conversation into the request for single-shot chain agents."""
    context = _recent_context(history)
    if not context:
        return message
    return (
        "Conversation so far:\n"
        f"{context}\n\n"
        f"Latest request: {message}"
    )


async def _dispatch(
    agent: str,
    message: str,
    history: list[dict],
    campaign: Campaign,
    brand: Brand | None,
    ctx: dict,
    user_id: int,
    db: AsyncSession,
) -> dict:
    # Full multi-turn conversation including the latest user message.
    full_history = [*history, {"role": "user", "content": message}]

    if agent == "analytics":
        from app.api.v1.agents.analytics_agent import _build_metrics_context
        from app.services.analytics_agent.analytics_agent import run_analytics_agent

        metrics_context = await _build_metrics_context(user_id, db)
        return await asyncio.to_thread(
            run_analytics_agent,
            message=_enrich(message, history),
            brand_name=ctx["brand_name"],
            industry=ctx["industry"],
            audience=ctx["audience"],
            campaign_name=ctx["campaign_name"],
            metrics_context=metrics_context,
        )

    if agent == "calendar":
        from app.api.v1.agents.calendar import _build_schedule_context
        from app.services.calendar_agent.calendar_agent import run_calendar_agent

        schedule_context = await _build_schedule_context(
            db, campaign.strategy_id, user_id
        )
        return await asyncio.to_thread(
            run_calendar_agent,
            message=_enrich(message, history),
            brand_name=ctx["brand_name"],
            industry=ctx["industry"],
            audience=ctx["audience"],
            campaign_name=ctx["campaign_name"],
            campaign_notes=ctx["campaign_notes"],
            schedule_context=schedule_context,
        )

    if agent == "brand":
        from app.services.brand_agent import run_brand_coaching

        return await asyncio.to_thread(
            run_brand_coaching,
            history=full_history,
            **ctx,
        )

    if agent == "content":
        from app.api.v1.agents.content import _map_tone
        from app.services.content_agent import run_content_agent

        request = ContentRequest(
            content_type="social_media_post",
            brand_name=ctx["brand_name"],
            industry=ctx["industry"],
            target_audience=ctx["audience"],
            tone=_map_tone(brand.tone_of_voice if brand else None),
            platform=None,
            topic_or_offer=_enrich(message, history),
            cta="Learn more",
            extra_notes=campaign.description,
        )
        try:
            content = await asyncio.to_thread(run_content_agent, request)
            data = content.model_dump()
            text = data.get("generated_content") or ""
            hashtags = data.get("hashtags") or []
            if hashtags:
                text = f"{text}\n\nHashtags: {' '.join(hashtags)}"
            return {"status": "success", "response": text, "error_message": None}
        except Exception as e:
            return {"status": "error", "response": None, "error_message": str(e)}

    if agent == "image":
        return await _run_image(message, campaign, brand)

    if agent == "video":
        return await _run_video(message, campaign, brand)

    if agent == "marketing":
        return await _run_marketing(message, campaign, brand, ctx)

    # any general request: handle conversationally via the support chatbot.
    from app.services.chatbot_agent import run_chatbot

    return await asyncio.to_thread(run_chatbot, history=full_history)


async def _run_image(message: str, campaign: Campaign, brand: Brand | None) -> dict:
    from app.api.v1.agents.image import (
        _PLATFORM_MAP,
        _SIZE_MAP,
        _build_brand_profile,
        _result_to_response,
    )
    from app.services.image_agent import (
        AdPlatform,
        ImageGenerationError,
        ImageRequest,
        ImageSize,
        LogoConfig,
        LogoPosition,
        run_image_agent,
    )

    campaign_goal = message.strip()
    if campaign.description and campaign.description not in campaign_goal:
        campaign_goal = f"{campaign_goal}. Context: {campaign.description}"

    agent_request = ImageRequest(
        brand=_build_brand_profile(brand),
        campaign_goal=campaign_goal,
        platform=_PLATFORM_MAP.get("instagram", AdPlatform.INSTAGRAM),
        image_size=_SIZE_MAP.get("512x512", ImageSize.SQUARE),
        num_variations=1,
        ad_copy="",
        logo=LogoConfig(enabled=False, position=LogoPosition.BOTTOM_RIGHT),
    )

    try:
        output = await asyncio.to_thread(run_image_agent, agent_request)
        image_result = _result_to_response(output)
        count = len(image_result.images)
        ad_copy = image_result.images[0].ad_copy if image_result.images else ""
        text = (
            f"Generated {count} image(s) for your brand in "
            f"{image_result.generation_time_sec:.1f}s. Opening the Image Generation tab "
            f"so you can review and download them."
        )
        if ad_copy:
            text = f"{text}\n\nSuggested ad copy: {ad_copy}"
        return {
            "status": "success",
            "response": text,
            "error_message": None,
            "image_result": image_result,
        }
    except ImageGenerationError as e:
        return {"status": "error", "response": None, "error_message": str(e)}
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}


async def _run_video(message: str, campaign: Campaign, brand: Brand | None) -> dict:
    from app.api.v1.agents.video import _map_output
    from app.services.video_agent.video_agent import build_prompt, run_video_agent

    brand_dict = {
        "brand_name": brand.brand_name if brand else "",
        "industry": brand.industry if brand else "",
        "target_audience": brand.target_audience if brand else "",
        "tone_of_voice": brand.tone_of_voice if brand else "professional",
    }
    campaign_dict = {"name": campaign.name, "description": campaign.description}

    try:
        prompt = build_prompt(
            brand=brand_dict, campaign=campaign_dict, user_message=message
        )
        output = await asyncio.to_thread(
            run_video_agent,
            prompt,
            brand=brand_dict,
            campaign=campaign_dict,
            user_message=message,
        )
        video_result = _map_output(output)
        if video_result.video_url:
            text = (
                "Your video is ready. Opening the Video Generation tab so you can "
                "preview and download it."
            )
        else:
            text = (
                "I built a full video plan and script. Opening the Video Generation tab "
                "so you can review it and render the final video."
            )
        return {
            "status": video_result.status or "success",
            "response": text,
            "error_message": video_result.error_message,
            "video_result": video_result,
        }
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}


async def _run_marketing(
    message: str, campaign: Campaign, brand: Brand | None, ctx: dict
) -> dict:
    from app.services.marketing_agent.marketing_agent import run_marketing_agent

    try:
        output = await asyncio.to_thread(
            run_marketing_agent,
            brand=ctx["brand_name"],
            industry=ctx["industry"],
            product=campaign.name,
            audience=ctx["audience"],
            goal=message,
            budget=1000.0,
            platforms=["Instagram", "Facebook", "LinkedIn"],
        )
        strategy = output.get("strategy") or "No strategy was produced."
        return {"status": "success", "response": strategy, "error_message": None}
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}
