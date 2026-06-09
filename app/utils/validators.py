from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException, status


def validate_date_range(start_date: date, end_date: date) -> None:
    """Validate that a date range is logically correct.

    Rules:
    - end_date must not be before start_date
    - start_date must not be more than 1 year in the past
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date",
        )

    one_year_ago = date.today() - timedelta(days=365)
    if start_date < one_year_ago:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be more than 1 year in the past",
        )


def validate_password_strength(password: str) -> None:
    """Validate password meets minimum strength requirements."""
    password = password or ""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )
    if not any(ch.isdigit() for ch in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number",
        )
    if not any(ch.isalpha() for ch in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one letter",
        )


def validate_brand_name(brand_name: str) -> None:
    """Validate brand name length and non-whitespace content."""
    name = (brand_name or "").strip()
    if len(name) < 2 or len(name) > 150:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand name must be between 2 and 150 characters",
        )


def validate_platform(platform: str) -> None:
    """Validate platform is one of the supported values (case-sensitive)."""
    allowed = {"Instagram", "TikTok", "LinkedIn", "YouTube", "Email", "Twitter"}
    if platform not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform: {platform}",
        )


def validate_strategy_status(status_value: str) -> None:
    """Validate strategy status is one of: draft, active, archived."""
    allowed = {"draft", "active", "archived"}
    if status_value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_value}. Must be draft, active, or archived",
        )


def validate_asset_type(asset_type: str) -> None:
    """Validate asset type is one of: image, video, copy."""
    allowed = {"image", "video", "copy"}
    if asset_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid asset type: {asset_type}",
        )


def validate_pagination(page: int, page_size: int) -> None:
    """Validate pagination values."""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be 1 or greater",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100",
        )

