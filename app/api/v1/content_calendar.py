from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.core.dependencies import get_async_db, get_current_user_async
from app.models.user import User
from app.schemas.content_schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from app.schemas.content_item import ContentItemCreate, ContentItemUpdate, PostStatusUpdate, ContentItemOut
from app.schemas.common import MessageResponse
from app.services import content_schedule_service as service

router = APIRouter()

@router.post("/schedules", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.create_schedule(data, current_user.id, db)

@router.get("/schedules", response_model=List[ScheduleOut])
async def list_schedules(
    strategy_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.list_schedules(strategy_id, current_user.id, db)

@router.get("/schedules/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.get_schedule(schedule_id, current_user.id, db)

@router.put("/schedules/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.update_schedule(schedule_id, data, current_user.id, db)

@router.delete("/schedules/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.delete_schedule(schedule_id, current_user.id, db)

@router.get("/calendar", response_model=Dict[str, List[ContentItemOut]])
async def get_calendar_by_month(
    strategy_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.get_calendar_by_month(strategy_id, month, year, current_user.id, db)

@router.post("/posts", response_model=ContentItemOut, status_code=status.HTTP_201_CREATED)
async def create_content_item(
    data: ContentItemCreate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.create_content_item(data, current_user.id, db)

@router.get("/posts/{item_id}", response_model=ContentItemOut)
async def get_content_item(
    item_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.get_content_item(item_id, current_user.id, db)

@router.put("/posts/{item_id}", response_model=ContentItemOut)
async def update_content_item(
    item_id: int,
    data: ContentItemUpdate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.update_content_item(item_id, data, current_user.id, db)

@router.delete("/posts/{item_id}", response_model=MessageResponse)
async def delete_content_item(
    item_id: int,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.delete_content_item(item_id, current_user.id, db)

@router.patch("/posts/{item_id}/status", response_model=ContentItemOut)
async def update_content_status(
    item_id: int,
    data: PostStatusUpdate,
    current_user: User = Depends(get_current_user_async),
    db: AsyncSession = Depends(get_async_db)
):
    return await service.update_content_status(item_id, data, current_user.id, db)
