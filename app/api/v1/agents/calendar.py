import asyncio
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.agents.calendar_agent import (
    CalendarAgentRequest,
    CalendarAgentResponse,
    CalendarApplyRequest,
    CalendarApplyResponse,
)
from app.services.calendar_agent.calendar_agent import (
    generate_calendar_items,
    run_calendar_agent,
)
from app.services import content_schedule_service as calendar_service
from app.services.campaign_context import build_campaign_context
from app.services.marketing_agent.calendar_sync import apply_calendar_items

router = APIRouter(prefix="/agents/calendar", tags=["Calendar Agent"])


async def _build_schedule_context(
    db: AsyncSession, strategy_id: int | None, user_id: int
) -> str:
    if not strategy_id:
        return "No marketing strategy linked to this campaign yet."

    now = date.today()
    try:
        calendar = await calendar_service.get_calendar_by_month(
            strategy_id, now.month, now.year, user_id, db
        )
    except HTTPException:
        return "No schedule data available for this strategy."

    if not calendar:
        return "Strategy exists but no posts are scheduled for the current month."

    lines: list[str] = []
    for day in sorted(calendar.keys()):
        for item in calendar[day]:
            lines.append(
                f"{day}: {item.title} ({item.platform.value if hasattr(item.platform, 'value') else item.platform})"
            )
    return "\n".join(lines[:40]) or "No scheduled posts found."


@router.post("/generate", response_model=CalendarAgentResponse)
async def generate_calendar_insight(
    data: CalendarAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    schedule_context = await _build_schedule_context(
        db, campaign.strategy_id, current_user.id
    )
    shared_context = await build_campaign_context(db, campaign, brand)

    output = await asyncio.to_thread(
        run_calendar_agent,
        message=data.message,
        brand_name=brand.brand_name if brand else "Brand",
        industry=brand.industry if brand and brand.industry else "General",
        audience=(
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        campaign_name=campaign.name,
        campaign_notes=campaign.description or "",
        schedule_context=schedule_context,
        shared_context=shared_context,
    )

    return CalendarAgentResponse(**output)


@router.post("/apply", response_model=CalendarApplyResponse)
async def apply_calendar_plan(
    data: CalendarApplyRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    """Generate a concrete schedule and persist it to the campaign calendar."""
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()
    if brand and brand.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this campaign")

    if not campaign.strategy_id:
        return CalendarApplyResponse(
            status="error",
            items_created=0,
            error_message=(
                "Generate a marketing plan first so the calendar has a strategy to fill."
            ),
        )

    platform_focus = []
    shared_context = await build_campaign_context(db, campaign, brand)

    generated = await asyncio.to_thread(
        generate_calendar_items,
        message=data.message,
        brand_name=brand.brand_name if brand else "Brand",
        audience=(
            brand.target_audience if brand and brand.target_audience else "General audience"
        ),
        campaign_name=campaign.name,
        platforms=platform_focus or ["Instagram", "TikTok", "LinkedIn"],
        shared_context=shared_context,
        days=max(1, min(data.days, 30)),
    )

    if generated["status"] != "success":
        return CalendarApplyResponse(
            status="error",
            items_created=0,
            error_message=generated.get("error_message"),
        )

    try:
        items_created = await apply_calendar_items(
            db,
            strategy_id=campaign.strategy_id,
            brand_id=campaign.brand_id,
            goal=campaign.name,
            items=generated["items"],
            days=max(1, min(data.days, 30)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save calendar: {e}") from e

    return CalendarApplyResponse(
        status="success",
        items_created=items_created,
        response=(
            f"Scheduled {items_created} posts on your calendar for the next "
            f"{max(1, min(data.days, 30))} days."
        ),
    )
