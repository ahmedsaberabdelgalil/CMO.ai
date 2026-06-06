import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.user import User
from app.models.campaign import Campaign
from app.models.brand import Brand
from app.schemas.agents.marketing_agent import MarketingAgentRequest, MarketingAgentResponse
from app.services.marketing_agent.calendar_sync import link_marketing_plan_to_campaign
from app.services.marketing_agent.marketing_agent import run_marketing_agent

router = APIRouter(prefix="/agents/marketing", tags=["Marketing Agent"])


@router.post("/generate", response_model=MarketingAgentResponse)
async def generate_marketing_strategy(
    data: MarketingAgentRequest,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()

    try:
        output = await asyncio.to_thread(
            run_marketing_agent,
            brand=data.brand_name or (brand.brand_name if brand else ""),
            industry=data.industry or (brand.industry if brand else ""),
            product=data.product or campaign.name,
            audience=data.audience or (brand.target_audience if brand else ""),
            goal=data.goal,
            budget=data.budget,
            platforms=data.platforms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketing agent error: {str(e)}") from e

    strategy_text = output.get("strategy") or ""
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
                goal=data.goal,
                platforms=data.platforms,
                strategy_text=strategy_text,
                platform_insight=output.get("platform_insight"),
                decision=output.get("decision"),
            )
            output["strategy_id"] = strategy_id
            output["calendar_items_created"] = items_created
            output["calendar_ready"] = items_created > 0
        except Exception as e:
            output["error_message"] = f"Strategy saved but calendar link failed: {str(e)}"

    return MarketingAgentResponse(**output)
