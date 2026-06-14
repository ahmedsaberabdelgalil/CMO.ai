import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.analytics_agent import AnalyticsAgentRequest, AnalyticsAgentResponse
from app.services.analytics_agent.analytics_agent import run_analytics_agent
from app.services import performance_service
from app.services.campaign_context import build_campaign_context

router = APIRouter(prefix="/agents/analytics", tags=["Analytics Agent"])

FOCUS_PROMPTS = {
    "overall": "Summarize overall marketing performance for this campaign and the top priorities.",
    "funnel": "Find the weakest step in the marketing funnel and explain why, with a fix.",
    "budget": "Recommend how to reallocate budget across channels based on current performance.",
    "channels": "Compare channel performance and say which channels to scale or cut.",
    "audience": "Analyze how well the content is reaching and converting the target audience.",
}


async def _build_metrics_context(user_id: int, db: AsyncSession) -> str:
    overview = await performance_service.get_analytics_overview(user_id, db)
    channels = await performance_service.get_channel_breakdown(user_id, db)

    lines = [
        f"Total reach: {overview.total_reach}",
        f"Total impressions: {overview.total_impressions}",
        f"Average engagement rate: {overview.avg_engagement_rate}%",
        f"Total clicks: {overview.total_clicks}",
        f"Total conversions: {overview.total_conversions}",
    ]

    if channels:
        lines.append("By channel:")
        for row in channels:
            lines.append(
                f"  {row.platform}: reach {row.total_reach}, clicks {row.total_clicks}, "
                f"engagement {row.total_engagement}"
            )
    else:
        lines.append("No channel breakdown data yet.")

    return "\n".join(lines)


def _manual_metrics_context(metrics: dict[str, float]) -> str:
    lines = ["Manually provided metrics:"]
    for key, value in metrics.items():
        label = key.replace("_", " ").capitalize()
        lines.append(f"  {label}: {value}")
    return "\n".join(lines)


@router.post("/generate", response_model=AnalyticsAgentResponse)
async def generate_analytics_insight(
    data: AnalyticsAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    # Build the analysis task from a preset focus and/or a free-text question.
    message = (data.message or "").strip()
    if data.focus:
        focus_prompt = FOCUS_PROMPTS.get(data.focus.strip().lower())
        if focus_prompt:
            message = f"{focus_prompt} {message}".strip()
    if not message:
        message = FOCUS_PROMPTS["overall"]

    # Use manually entered metrics when provided, else the stored campaign metrics.
    if data.metrics:
        metrics_context = _manual_metrics_context(data.metrics)
    else:
        metrics_context = await _build_metrics_context(current_user.id, db)

    shared_context = await build_campaign_context(db, campaign, brand)

    output = await asyncio.to_thread(
        run_analytics_agent,
        message=message,
        brand_name=brand.brand_name if brand else "Brand",
        industry=brand.industry if brand and brand.industry else "General",
        audience=(
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        campaign_name=campaign.name,
        metrics_context=metrics_context,
        shared_context=shared_context,
    )

    return AnalyticsAgentResponse(**output)
