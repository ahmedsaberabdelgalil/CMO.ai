"""Export endpoints — download agent output (plans, reports) as Word files."""

import asyncio
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_db, get_current_user_async
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.marketing_strategy import MarketingStrategy
from app.models.user import User
from app.services.export_service import build_docx

router = APIRouter(prefix="/export", tags=["Export"])

_DOCX_MEDIA = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def _safe_filename(name: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "document"
    return f"{base}.docx"


def _docx_response(data: bytes, filename: str) -> StreamingResponse:
    safe = _safe_filename(filename)
    return StreamingResponse(
        iter([data]),
        media_type=_DOCX_MEDIA,
        headers={
            "Content-Disposition": f"attachment; filename={safe}; filename*=UTF-8''{quote(safe)}"
        },
    )


class ExportDocxRequest(BaseModel):
    title: str
    content: str
    subtitle: str | None = None
    filename: str | None = None


@router.post("/docx")
async def export_docx(
    data: ExportDocxRequest,
    current_user: User = Depends(get_current_user_async),
):
    """Generic export: turn any title + text into a downloadable Word file."""
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Nothing to export.")
    document = await asyncio.to_thread(
        build_docx,
        title=data.title,
        content=data.content,
        subtitle=data.subtitle,
    )
    return _docx_response(document, data.filename or data.title or "document")


@router.get("/marketing-plan/{campaign_id}")
async def export_marketing_plan(
    campaign_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db),
):
    """Export the campaign's linked marketing plan as a Word document."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand_result = await db.execute(select(Brand).where(Brand.id == campaign.brand_id))
    brand = brand_result.scalar_one_or_none()
    if brand and brand.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this campaign")

    if not campaign.strategy_id:
        raise HTTPException(
            status_code=404, detail="No marketing plan linked to this campaign yet."
        )

    strategy = await db.get(MarketingStrategy, campaign.strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Linked strategy not found.")

    sections = [f"## {strategy.title}"]
    if strategy.platform_focus:
        sections.append(f"**Platforms:** {strategy.platform_focus}")
    if strategy.objectives:
        sections.append("\n## Strategy\n")
        sections.append(strategy.objectives)
    if strategy.messaging_themes:
        sections.append("\n## Messaging\n")
        sections.append(strategy.messaging_themes)

    document = await asyncio.to_thread(
        build_docx,
        title=f"Marketing Plan — {campaign.name}",
        content="\n".join(sections),
        subtitle=brand.brand_name if brand else None,
    )
    return _docx_response(document, f"marketing_plan_{campaign.name}")
