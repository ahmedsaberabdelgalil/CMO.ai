"""
Shared campaign context builder.

Assembles a single plain-text snapshot of the brand profile, campaign, and the
linked marketing plan so that every agent (brand, content, calendar, analytics,
image, video, orchestrator) works from the same source of truth — i.e. they all
"know what the brand is and what the plan is".
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.marketing_strategy import MarketingStrategy


async def build_campaign_context(
    db: AsyncSession,
    campaign: Campaign,
    brand: Brand | None,
) -> str:
    """Return a compact, agent-ready context block for the campaign."""
    lines: list[str] = []

    if brand:
        lines.append("BRAND PROFILE")
        lines.append(f"- Name: {brand.brand_name}")
        if brand.industry:
            lines.append(f"- Industry: {brand.industry}")
        if brand.target_audience:
            lines.append(f"- Target audience: {brand.target_audience}")
        if brand.value_proposition:
            lines.append(f"- Value proposition: {brand.value_proposition}")
        if brand.tone_of_voice:
            lines.append(f"- Tone of voice: {brand.tone_of_voice}")
        if brand.positioning:
            lines.append(f"- Positioning: {brand.positioning}")
    else:
        lines.append("BRAND PROFILE: not defined yet.")

    lines.append("")
    lines.append("CAMPAIGN")
    lines.append(f"- Name: {campaign.name}")
    if campaign.description:
        lines.append(f"- Description: {campaign.description}")

    lines.append("")
    if campaign.strategy_id:
        strategy = await db.get(MarketingStrategy, campaign.strategy_id)
        if strategy:
            lines.append("MARKETING PLAN")
            lines.append(f"- Title: {strategy.title}")
            if strategy.platform_focus:
                lines.append(f"- Platforms: {strategy.platform_focus}")
            if strategy.objectives:
                lines.append(f"- Objectives: {strategy.objectives.strip()[:1200]}")
            if strategy.messaging_themes:
                lines.append(
                    f"- Messaging themes: {strategy.messaging_themes.strip()[:600]}"
                )
        else:
            lines.append("MARKETING PLAN: none linked yet.")
    else:
        lines.append("MARKETING PLAN: none linked yet.")

    return "\n".join(lines)
