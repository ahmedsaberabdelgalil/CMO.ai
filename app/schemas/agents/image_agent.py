from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ImageAgentRequest(BaseModel):
    """HTTP body for POST /agents/image/generate."""

    message: str = Field(..., description="Campaign goal or creative brief for the image")
    campaign_id: int
    platform: Literal[
        "instagram", "facebook", "tiktok", "linkedin", "general"
    ] = "instagram"
    image_size: Literal["512x512", "768x768", "1024x1024"] = "512x512"
    num_variations: int = Field(default=1, ge=1, le=4)
    logo_enabled: bool = False
    ad_copy: Optional[str] = None


class GeneratedImageOut(BaseModel):
    image_id: str
    request_id: str
    local_path: str
    image_url: str
    prompt_used: str
    ad_copy: str
    platform: str
    size: str
    model_used: str
    logo_applied: bool
    metadata: dict[str, Any] = Field(default_factory=dict)


class ImageAgentResponse(BaseModel):
    request_id: str
    brand_name: str
    campaign_goal: str
    images: list[GeneratedImageOut]
    ab_test_ready: bool
    generation_time_sec: float
    knowledge_context: str


class ImageAgentStatus(BaseModel):
    provider: str
    model: str
    image_backend: str
    groq_configured: bool
    image_backend_configured: bool
    output_dir: str
