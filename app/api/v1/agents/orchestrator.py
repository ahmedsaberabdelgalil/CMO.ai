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
from app.services.orchestrator_agent import VALID_AGENTS, plan_steps
from app.services.campaign_context import build_campaign_context

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
    shared_context = await build_campaign_context(db, campaign, brand)

    # Decide the step plan: a forced agent, or an LLM-planned 1–4 step sequence.
    if data.force_agent and data.force_agent.strip().lower() in VALID_AGENTS:
        steps = [{"agent": data.force_agent.strip().lower(), "task": message}]
    else:
        steps = await asyncio.to_thread(plan_steps, message, recent_context)

    parts: list[str] = []
    agents_used: list[str] = []
    image_result = None
    video_result = None
    marketing_result = None
    overall_status = "success"
    first_error: str | None = None
    running_history = list(history)
    multi = len(steps) > 1

    for step in steps:
        step_agent = step["agent"]
        task = step["task"]
        out = await _dispatch(
            step_agent,
            task,
            running_history,
            campaign,
            brand,
            ctx,
            shared_context,
            current_user.id,
            db,
        )
        agents_used.append(step_agent)

        text = out.get("response") or out.get("error_message") or ""
        if out.get("status") == "error":
            overall_status = "error"
            first_error = first_error or out.get("error_message")
        if out.get("image_result"):
            image_result = out["image_result"]
        if out.get("video_result"):
            video_result = out["video_result"]
        if out.get("marketing_result"):
            marketing_result = out["marketing_result"]

        label = AGENT_LABELS.get(step_agent, step_agent.title())
        parts.append(f"### {label}\n{text}" if multi else text)

        running_history = [
            *running_history,
            {"role": "user", "content": task},
            {"role": "assistant", "content": text},
        ]

    combined = "\n\n".join(p for p in parts if p.strip())
    primary_agent = agents_used[0] if not multi else "orchestrator"
    if multi:
        agent_label = "Multiple agents (" + ", ".join(
            AGENT_LABELS.get(a, a.title()) for a in agents_used
        ) + ")"
        reason = f"Ran {len(agents_used)} agents in sequence to fulfill the request."
    else:
        agent_label = AGENT_LABELS.get(primary_agent, primary_agent.title())
        reason = f"Routed to {agent_label}."

    return OrchestratorAgentResponse(
        status=overall_status,
        agent=primary_agent,
        agent_label=agent_label,
        reason=reason,
        response=combined or None,
        error_message=first_error,
        agents=agents_used,
        suggestions=_followups(agents_used),
        image_result=image_result,
        video_result=video_result,
        marketing_result=marketing_result,
    )


_FOLLOWUPS = {
    "content": [
        "Generate an image to go with this",
        "Turn this into a short video script",
        "Schedule these posts on the calendar",
    ],
    "image": [
        "Write a caption for this image",
        "Create a video version",
        "Generate 3 more variations",
    ],
    "video": [
        "Write a caption for this video",
        "Plan where and when to post it",
        "Generate a thumbnail image",
    ],
    "marketing": [
        "Open the calendar and review the schedule",
        "Generate the first launch post",
        "Create on-brand launch images",
    ],
    "calendar": [
        "Generate content for these calendar slots",
        "Rebalance the channel mix",
        "Predict performance for this schedule",
    ],
    "analytics": [
        "Suggest a budget reallocation",
        "Find the weakest funnel step",
        "Draft fixes for the gaps you found",
    ],
    "brand": [
        "Create a brand voice guide",
        "Generate on-brand images",
        "Write 3 key brand messages",
    ],
    "chatbot": [
        "Create a marketing plan",
        "Generate a social post",
        "Analyze campaign performance",
    ],
}


def _followups(agents_used: list[str]) -> list[str]:
    """Suggest next prompts based on the last agent that ran."""
    last = agents_used[-1] if agents_used else "chatbot"
    return _FOLLOWUPS.get(last, _FOLLOWUPS["chatbot"])


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
    shared_context: str,
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
            shared_context=shared_context,
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
            shared_context=shared_context,
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

        extra_notes = "\n\n".join(
            part for part in [campaign.description, shared_context] if part
        )
        request = ContentRequest(
            content_type="social_media_post",
            brand_name=ctx["brand_name"],
            industry=ctx["industry"],
            target_audience=ctx["audience"],
            tone=_map_tone(brand.tone_of_voice if brand else None),
            platform=None,
            topic_or_offer=_enrich(message, history),
            cta="Learn more",
            extra_notes=extra_notes,
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
        return await _run_marketing(message, campaign, brand, ctx, db)

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
    message: str,
    campaign: Campaign,
    brand: Brand | None,
    ctx: dict,
    db: AsyncSession,
) -> dict:
    from app.schemas.agents.marketing_agent import MarketingAgentResponse
    from app.services.marketing_agent.calendar_sync import (
        link_marketing_plan_to_campaign,
    )
    from app.services.marketing_agent.marketing_agent import run_marketing_agent

    platforms = ["Instagram", "Facebook", "LinkedIn"]
    goal = message
    try:
        output = await asyncio.to_thread(
            run_marketing_agent,
            brand=ctx["brand_name"],
            industry=ctx["industry"],
            product=campaign.name,
            audience=ctx["audience"],
            goal=goal,
            budget=1000.0,
            platforms=platforms,
        )
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}

    strategy_text = output.get("strategy") or ""
    # Persist + seed the calendar, exactly like the dedicated marketing endpoint.
    if (
        output.get("status") == "success"
        and strategy_text
        and not strategy_text.startswith("Strategy generation failed:")
    ):
        try:
            strategy_id, items_created = await link_marketing_plan_to_campaign(
                db,
                campaign=campaign,
                brand_id=campaign.brand_id,
                campaign_name=campaign.name,
                goal=goal,
                platforms=platforms,
                strategy_text=strategy_text,
                platform_insight=output.get("platform_insight"),
                decision=output.get("decision"),
            )
            output["strategy_id"] = strategy_id
            output["calendar_items_created"] = items_created
            output["calendar_ready"] = items_created > 0
        except Exception as e:
            output["error_message"] = f"Strategy saved but calendar link failed: {str(e)}"

    marketing_result = MarketingAgentResponse(**output)
    response_text = strategy_text or "No strategy was produced."
    if marketing_result.calendar_ready:
        response_text = (
            f"{response_text}\n\nI scheduled "
            f"{marketing_result.calendar_items_created or 14} posts on your calendar. "
            "Open Market Calendar to review them."
        )
    return {
        "status": output.get("status", "success"),
        "response": response_text,
        "error_message": output.get("error_message"),
        "marketing_result": marketing_result,
    }
