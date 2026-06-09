from __future__ import annotations

from datetime import date, datetime, timezone
from typing import List

from sqlalchemy import func, literal, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import CampaignStatus, ContentStatus, PlanName
from app.models.billing import Plan, Subscription, UsageRecord
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.content_item import ContentItem
from app.models.content_schedule import ContentSchedule
from app.models.marketing_strategy import MarketingStrategy
from app.models.performance_metric import PerformanceMetric
from app.schemas.dashboard import (
    AIInsight,
    DashboardSummary,
    PlanUsage,
    RecentActivityItem,
)


async def get_summary(user_id: int, db: AsyncSession) -> DashboardSummary:
    active_stmt = (
        select(func.count(Campaign.id))
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(
            Brand.user_id == user_id,
            Campaign.status == CampaignStatus.In_Progress,
        )
    )
    active_result = await db.execute(active_stmt)
    active_campaigns = int(active_result.scalar_one())

    reach_eng_stmt = (
        select(
            func.coalesce(func.sum(PerformanceMetric.reach), 0),
            func.coalesce(func.sum(PerformanceMetric.engagement), 0),
        )
        .select_from(PerformanceMetric)
        .join(ContentItem)
        .join(ContentSchedule)
        .join(MarketingStrategy)
        .join(Brand)
        .where(Brand.user_id == user_id)
    )
    re_result = await db.execute(reach_eng_stmt)
    total_reach, total_engagement = re_result.one()
    total_reach_i = int(total_reach)
    total_engagement_i = int(total_engagement)

    avg_engagement_rate = 0.0
    if total_reach_i > 0:
        avg_engagement_rate = (total_engagement_i / total_reach_i) * 100.0

    today = date.today()
    scheduled_stmt = (
        select(func.count(ContentItem.id))
        .join(ContentSchedule)
        .join(MarketingStrategy)
        .join(Brand)
        .where(
            Brand.user_id == user_id,
            ContentItem.scheduled_date >= today,
            ContentItem.status.in_([ContentStatus.Draft, ContentStatus.Ready]),
        )
    )
    sched_result = await db.execute(scheduled_stmt)
    scheduled_posts = int(sched_result.scalar_one())

    return DashboardSummary(
        active_campaigns=active_campaigns,
        total_reach=total_reach_i,
        avg_engagement_rate=avg_engagement_rate,
        scheduled_posts=scheduled_posts,
    )


async def get_recent_activity(user_id: int, db: AsyncSession) -> List[RecentActivityItem]:
    campaigns_q = (
        select(
            Campaign.id.label("id"),
            literal("Campaign created").label("action"),
            literal("campaign").label("entity_type"),
            Campaign.name.label("entity_name"),
            Campaign.created_at.label("timestamp"),
        )
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(Brand.user_id == user_id)
    )
    strategies_q = (
        select(
            MarketingStrategy.id.label("id"),
            literal("Strategy created").label("action"),
            literal("strategy").label("entity_type"),
            MarketingStrategy.title.label("entity_name"),
            MarketingStrategy.created_at.label("timestamp"),
        )
        .join(Brand, MarketingStrategy.brand_id == Brand.id)
        .where(Brand.user_id == user_id)
    )
    content_q = (
        select(
            ContentItem.id.label("id"),
            literal("Content published").label("action"),
            literal("content").label("entity_type"),
            ContentItem.title.label("entity_name"),
            ContentItem.created_at.label("timestamp"),
        )
        .join(ContentSchedule, ContentItem.schedule_id == ContentSchedule.id)
        .join(MarketingStrategy, ContentSchedule.strategy_id == MarketingStrategy.id)
        .join(Brand, MarketingStrategy.brand_id == Brand.id)
        .where(
            Brand.user_id == user_id,
            ContentItem.status == ContentStatus.Published,
        )
    )

    union_sub = union_all(campaigns_q, strategies_q, content_q).subquery()
    stmt = select(union_sub).order_by(union_sub.c.timestamp.desc()).limit(5)

    result = await db.execute(stmt)
    rows = result.all()
    return [
        RecentActivityItem(
            id=int(r.id),
            action=r.action,
            entity_type=r.entity_type,
            entity_name=r.entity_name,
            timestamp=r.timestamp,
        )
        for r in rows
    ]


async def get_ai_insights(user_id: int, db: AsyncSession) -> List[AIInsight]:
    summary = await get_summary(user_id, db)
    insights: List[AIInsight] = []

    if summary.active_campaigns == 0:
        insights.append(
            AIInsight(
                message="You have no active campaigns. Create one to start tracking performance."
            )
        )

    if summary.avg_engagement_rate < 2.0:
        insights.append(
            AIInsight(
                message="Your engagement is below average. Try posting more video content."
            )
        )

    insights.append(
        AIInsight(
            message="Best time to post on Instagram is between 6pm and 9pm on weekdays."
        )
    )

    return insights


async def get_plan_usage(user_id: int, db: AsyncSession) -> PlanUsage:
    sub_stmt = (
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            Subscription.user_id == user_id,
            Subscription.is_active.is_(True),
        )
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub_result = await db.execute(sub_stmt)
    subscription = sub_result.scalar_one_or_none()

    if subscription and subscription.plan:
        plan = subscription.plan
        plan_name = plan.name.value if hasattr(plan.name, "value") else str(plan.name)
        ai_limit = plan.ai_generation_limit
        campaign_limit = plan.active_campaign_limit
        storage_lim = float(plan.storage_limit_gb)
    else:
        p_stmt = select(Plan).where(Plan.name == PlanName.Starter).limit(1)
        p_res = await db.execute(p_stmt)
        plan = p_res.scalar_one_or_none()
        if plan is None:
            plan_name = PlanName.Starter.value
            ai_limit = 50
            campaign_limit = 1
            storage_lim = 5.0
        else:
            plan_name = plan.name.value if hasattr(plan.name, "value") else str(plan.name)
            ai_limit = plan.ai_generation_limit
            campaign_limit = plan.active_campaign_limit
            storage_lim = float(plan.storage_limit_gb)

    now = datetime.now(timezone.utc)
    u_stmt = select(UsageRecord).where(
        UsageRecord.user_id == user_id,
        UsageRecord.period_month == now.month,
        UsageRecord.period_year == now.year,
    )
    u_result = await db.execute(u_stmt)
    usage = u_result.scalar_one_or_none()

    if usage is None:
        ai_used = 0
        campaigns_used = 0
        storage_used = 0.0
    else:
        ai_used = usage.ai_generations_used
        campaigns_used = usage.active_campaigns_count
        storage_used = float(usage.storage_used_gb)

    return PlanUsage(
        plan_name=plan_name,
        ai_generation_limit=ai_limit,
        ai_generations_used=ai_used,
        active_campaign_limit=campaign_limit,
        active_campaigns_count=campaigns_used,
        storage_limit_gb=storage_lim,
        storage_used_gb=storage_used,
    )
