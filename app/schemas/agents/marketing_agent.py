from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class MarketingAgentRequest(BaseModel):
    message: str
    campaign_id: int
    budget: float = 1000.0
    platforms: List[str] = ["Instagram", "TikTok"]
    goal: str = "Brand Awareness"
    brand_name: Optional[str] = None
    industry: Optional[str] = None
    audience: Optional[str] = None
    product: Optional[str] = None


class FinancialModel(BaseModel):
    estimated_clicks: Optional[int] = None
    estimated_sales: Optional[int] = None
    estimated_revenue: Optional[float] = None
    cpa: Optional[float] = None
    roas: Optional[float] = None


class MarketingAgentResponse(BaseModel):
    status: str
    strategy: Optional[str] = None
    financial_model: Optional[Dict[str, Any]] = None
    budget_allocation: Optional[Dict[str, Any]] = None
    platform_insight: Optional[str] = None
    decision: Optional[str] = None
    competitor_insight: Optional[str] = None
    error_message: Optional[str] = None
    strategy_id: Optional[int] = None
    calendar_items_created: Optional[int] = None
    calendar_ready: bool = False
