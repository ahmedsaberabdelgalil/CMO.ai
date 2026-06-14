"""Persist marketing agent output as a linked strategy + calendar items."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import (
    ContentStatus,
    ContentType,
    PlanType,
    PlatformType,
    StrategyStatus,
)
from app.models.campaign import Campaign
from app.models.content_item import ContentItem
from app.models.content_schedule import ContentSchedule
from app.models.marketing_strategy import MarketingStrategy

_PLATFORM_MAP = {
    "instagram": PlatformType.Instagram,
    "tiktok": PlatformType.TikTok,
    "linkedin": PlatformType.LinkedIn,
    "youtube": PlatformType.YouTube,
    "email": PlatformType.Email,
    "twitter": PlatformType.Twitter,
    "facebook": PlatformType.Instagram,
}

_CALENDAR_THEMES = [
    "Awareness post",
    "Educational tip",
    "Social proof",
    "Product spotlight",
    "Community question",
    "Offer reminder",
    "Behind the scenes",
    "User story",
    "How-to snippet",
    "Trend tie-in",
    "Testimonial",
    "FAQ answer",
    "Launch teaser",
    "Week recap",
]


def _map_platform(name: str) -> PlatformType:
    return _PLATFORM_MAP.get(name.lower().strip(), PlatformType.Instagram)


async def link_marketing_plan_to_campaign(
    db: AsyncSession,
    *,
    campaign: Campaign,
    brand_id: int,
    campaign_name: str,
    goal: str,
    platforms: list[str],
    strategy_text: str,
    platform_insight: str | None = None,
    decision: str | None = None,
    days: int = 14,
) -> tuple[int, int]:
    """
    Create or update a marketing strategy, link it to the campaign,
    and seed calendar content items for the next `days` days.

    Returns (strategy_id, items_created).
    """
    title = f"{campaign_name} — {goal}"
    objectives = (strategy_text or "").strip()[:8000]
    messaging = "\n\n".join(
        part for part in [platform_insight, decision] if part
    )[:4000]
    platform_focus = ", ".join(platforms) if platforms else "Instagram, TikTok"

    strategy: MarketingStrategy | None = None
    if campaign.strategy_id:
        result = await db.execute(
            select(MarketingStrategy).where(
                MarketingStrategy.id == campaign.strategy_id,
                MarketingStrategy.brand_id == brand_id,
            )
        )
        strategy = result.scalar_one_or_none()

    if strategy is None:
        strategy = MarketingStrategy(
            title=title,
            objectives=objectives,
            messaging_themes=messaging or None,
            platform_focus=platform_focus,
            brand_id=brand_id,
            status=StrategyStatus.active,
        )
        db.add(strategy)
        await db.flush()
        campaign.strategy_id = strategy.id
    else:
        strategy.title = title
        strategy.objectives = objectives
        strategy.messaging_themes = messaging or strategy.messaging_themes
        strategy.platform_focus = platform_focus
        strategy.status = StrategyStatus.active

    start = date.today()
    end = start + timedelta(days=days - 1)

    schedule_result = await db.execute(
        select(ContentSchedule)
        .where(ContentSchedule.strategy_id == strategy.id)
        .order_by(ContentSchedule.created_at.desc())
        .limit(1)
    )
    schedule = schedule_result.scalar_one_or_none()
    if schedule is None:
        schedule = ContentSchedule(
            plan_type=PlanType.weekly,
            start_date=start,
            end_date=end,
            strategy_id=strategy.id,
        )
        db.add(schedule)
        await db.flush()
    else:
        schedule.start_date = start
        schedule.end_date = end

    await db.execute(
        delete(ContentItem).where(
            ContentItem.schedule_id == schedule.id,
            ContentItem.scheduled_date >= start,
            ContentItem.scheduled_date <= end,
        )
    )

    platform_cycle = [_map_platform(p) for p in platforms] or [PlatformType.Instagram]
    snippet = (platform_insight or decision or strategy_text or goal)[:500]

    items_created = 0
    for offset in range(days):
        scheduled = start + timedelta(days=offset)
        platform = platform_cycle[offset % len(platform_cycle)]
        theme = _CALENDAR_THEMES[offset % len(_CALENDAR_THEMES)]
        db.add(
            ContentItem(
                title=f"{theme} — {campaign_name}",
                content_type=ContentType.post,
                platform=platform,
                objective=goal,
                body_text=snippet,
                scheduled_date=scheduled,
                scheduled_time="10:00",
                status=ContentStatus.Draft,
                schedule_id=schedule.id,
            )
        )
        items_created += 1

    await db.commit()
    await db.refresh(campaign)
    await db.refresh(strategy)
    return strategy.id, items_created


async def apply_calendar_items(
    db: AsyncSession,
    *,
    strategy_id: int,
    brand_id: int,
    goal: str,
    items: list[dict],
    days: int = 14,
) -> int:
    """
    Persist agent-generated calendar items into the strategy's schedule,
    replacing items in the affected date window. Returns the count created.
    """
    result = await db.execute(
        select(MarketingStrategy).where(
            MarketingStrategy.id == strategy_id,
            MarketingStrategy.brand_id == brand_id,
        )
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise ValueError("Strategy not found for this brand.")

    start = date.today()
    end = start + timedelta(days=days - 1)

    schedule_result = await db.execute(
        select(ContentSchedule)
        .where(ContentSchedule.strategy_id == strategy.id)
        .order_by(ContentSchedule.created_at.desc())
        .limit(1)
    )
    schedule = schedule_result.scalar_one_or_none()
    if schedule is None:
        schedule = ContentSchedule(
            plan_type=PlanType.weekly,
            start_date=start,
            end_date=end,
            strategy_id=strategy.id,
        )
        db.add(schedule)
        await db.flush()
    else:
        schedule.start_date = start
        schedule.end_date = end

    await db.execute(
        delete(ContentItem).where(
            ContentItem.schedule_id == schedule.id,
            ContentItem.scheduled_date >= start,
            ContentItem.scheduled_date <= end,
        )
    )

    items_created = 0
    for raw in items:
        try:
            offset = int(raw.get("day_offset", items_created))
        except (TypeError, ValueError):
            offset = items_created
        offset = max(0, min(offset, days - 1))
        scheduled = start + timedelta(days=offset)
        platform = _map_platform(str(raw.get("platform", "Instagram")))
        title = (str(raw.get("title", "")).strip() or "Content post")[:300]
        objective = (str(raw.get("objective", goal)).strip() or goal)[:300]
        caption = str(raw.get("caption", "")).strip()[:2000]

        db.add(
            ContentItem(
                title=title,
                content_type=ContentType.post,
                platform=platform,
                objective=objective,
                body_text=caption,
                scheduled_date=scheduled,
                scheduled_time="10:00",
                status=ContentStatus.Draft,
                schedule_id=schedule.id,
            )
        )
        items_created += 1

    await db.commit()
    return items_created
