from pydantic import BaseModel
from typing import List
from datetime import datetime, date
from decimal import Decimal


class DashboardSummary(BaseModel):
    active_campaigns: int
    total_reach: int
    avg_engagement_rate: float
    scheduled_posts: int


class RecentActivityItem(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_name: str
    timestamp: datetime


class RecentActivity(BaseModel):
    items: List[RecentActivityItem]


class AIInsight(BaseModel):
    message: str


class PlanUsage(BaseModel):
    plan_name: str
    ai_generation_limit: int
    ai_generations_used: int
    active_campaign_limit: int
    active_campaigns_count: int
    storage_limit_gb: float
    storage_used_gb: float
