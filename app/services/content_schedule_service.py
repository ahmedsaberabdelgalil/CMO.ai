from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.content_schedule import ContentSchedule
from app.models.content_item import ContentItem
from app.models.marketing_strategy import MarketingStrategy
from app.models.brand import Brand
from app.schemas.content_schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from app.schemas.content_item import ContentItemCreate, ContentItemUpdate, PostStatusUpdate, ContentItemOut
from app.schemas.common import MessageResponse
from datetime import date, datetime
from collections import defaultdict

async def verify_strategy_access(db: AsyncSession, strategy_id: int, user_id: int) -> MarketingStrategy:
    stmt = select(MarketingStrategy).join(Brand).where(
        MarketingStrategy.id == strategy_id,
        Brand.user_id == user_id
    )
    result = await db.execute(stmt)
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found or access denied")
    return strategy

async def verify_schedule_access(db: AsyncSession, schedule_id: int, user_id: int) -> ContentSchedule:
    stmt = select(ContentSchedule).join(MarketingStrategy).join(Brand).where(
        ContentSchedule.id == schedule_id,
        Brand.user_id == user_id
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found or access denied")
    return schedule

async def verify_content_item_access(db: AsyncSession, item_id: int, user_id: int) -> ContentItem:
    stmt = select(ContentItem).join(ContentSchedule).join(MarketingStrategy).join(Brand).where(
        ContentItem.id == item_id,
        Brand.user_id == user_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found or access denied")
    return item

async def create_schedule(data: ScheduleCreate, user_id: int, db: AsyncSession) -> ContentSchedule:
    await verify_strategy_access(db, data.strategy_id, user_id)
    
    new_schedule = ContentSchedule(**data.model_dump())
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

async def get_schedule(schedule_id: int, user_id: int, db: AsyncSession) -> ContentSchedule:
    return await verify_schedule_access(db, schedule_id, user_id)

async def list_schedules(strategy_id: int, user_id: int, db: AsyncSession) -> List[ContentSchedule]:
    await verify_strategy_access(db, strategy_id, user_id)
    
    stmt = select(ContentSchedule).where(ContentSchedule.strategy_id == strategy_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_schedule(schedule_id: int, data: ScheduleUpdate, user_id: int, db: AsyncSession) -> ContentSchedule:
    schedule = await verify_schedule_access(db, schedule_id, user_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)
        
    await db.commit()
    await db.refresh(schedule)
    return schedule

async def delete_schedule(schedule_id: int, user_id: int, db: AsyncSession) -> MessageResponse:
    schedule = await verify_schedule_access(db, schedule_id, user_id)
    await db.delete(schedule)
    await db.commit()
    return MessageResponse(message="Content schedule deleted successfully")

async def get_calendar_by_month(strategy_id: int, month: int, year: int, user_id: int, db: AsyncSession) -> Dict[str, List[ContentItem]]:
    await verify_strategy_access(db, strategy_id, user_id)
    
    stmt = select(ContentItem).join(ContentSchedule).where(
        ContentSchedule.strategy_id == strategy_id,
        extract('month', ContentItem.scheduled_date) == month,
        extract('year', ContentItem.scheduled_date) == year
    ).order_by(ContentItem.scheduled_time.asc())
    
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    calendar = defaultdict(list)
    for item in items:
        date_str = item.scheduled_date.isoformat()
        calendar[date_str].append(item)
        
    return dict(calendar)

async def create_content_item(data: ContentItemCreate, user_id: int, db: AsyncSession) -> ContentItem:
    await verify_schedule_access(db, data.schedule_id, user_id)
    
    new_item = ContentItem(**data.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

async def get_content_item(item_id: int, user_id: int, db: AsyncSession) -> ContentItem:
    return await verify_content_item_access(db, item_id, user_id)

async def update_content_item(item_id: int, data: ContentItemUpdate, user_id: int, db: AsyncSession) -> ContentItem:
    item = await verify_content_item_access(db, item_id, user_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    await db.commit()
    await db.refresh(item)
    return item

async def delete_content_item(item_id: int, user_id: int, db: AsyncSession) -> MessageResponse:
    item = await verify_content_item_access(db, item_id, user_id)
    await db.delete(item)
    await db.commit()
    return MessageResponse(message="Content item deleted successfully")

async def update_content_status(item_id: int, data: PostStatusUpdate, user_id: int, db: AsyncSession) -> ContentItem:
    item = await verify_content_item_access(db, item_id, user_id)
    item.status = data.status
    await db.commit()
    await db.refresh(item)
    return item
