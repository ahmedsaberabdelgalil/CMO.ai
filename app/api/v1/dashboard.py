from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.user import User
from app.schemas.dashboard import (
    AIInsight,
    DashboardSummary,
    PlanUsage,
    RecentActivityItem,
)
from app.services import dashboard_service as service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    return await service.get_summary(current_user.id, db)


@router.get("/recent-activity", response_model=List[RecentActivityItem])
async def dashboard_recent_activity(
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    return await service.get_recent_activity(current_user.id, db)


@router.get("/insights", response_model=List[AIInsight])
async def dashboard_insights(
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    return await service.get_ai_insights(current_user.id, db)


@router.get("/usage", response_model=PlanUsage)
async def dashboard_usage(
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    return await service.get_plan_usage(current_user.id, db)
