"""
Central API router — registers all v1 sub-routers under /api/v1.

Import this object in app/main.py and mount it with:
    app.include_router(api_router, prefix="/api/v1")
"""

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    assets,
    auth,
    billing,
    brands,
    campaigns,
    content_calendar,
    dashboard,
    export,
    jobs,
    notifications,
    quick_actions,
    strategies,
    users,
)
from app.api.v1.agents import (
    analytics_agent,
    brand,
    calendar,
    chatbot,
    content,
    image,
    marketing,
    orchestrator,
    video,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(brands.router)
api_router.include_router(strategies.router)
api_router.include_router(content_calendar.router, prefix="/content-calendar", tags=["Content Calendar"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(analytics.router)
api_router.include_router(dashboard.router)
api_router.include_router(notifications.router)
api_router.include_router(billing.router)
api_router.include_router(quick_actions.router) 
api_router.include_router(content.router)
api_router.include_router(image.router)
api_router.include_router(video.router)
api_router.include_router(marketing.router)
api_router.include_router(calendar.router)
api_router.include_router(analytics_agent.router)
api_router.include_router(brand.router)
api_router.include_router(chatbot.router)
api_router.include_router(orchestrator.router)
api_router.include_router(export.router)
api_router.include_router(jobs.router)

