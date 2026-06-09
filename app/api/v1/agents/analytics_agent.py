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

router = APIRouter(prefix="/agents/analytics", tags=["Analytics Agent"])


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

    metrics_context = await _build_metrics_context(current_user.id, db)

    output = await asyncio.to_thread(
        run_analytics_agent,
        message=data.message,
        brand_name=brand.brand_name if brand else "Brand",
        industry=brand.industry if brand and brand.industry else "General",
        audience=(
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        campaign_name=campaign.name,
        metrics_context=metrics_context,
    )

    return AnalyticsAgentResponse(**output)
