from typing import Literal

from pydantic import BaseModel


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class BrandAgentRequest(BaseModel):
    campaign_id: int
    messages: list[ChatTurn] = []


class BrandAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None


class BrandSaveResponse(BaseModel):
    status: str
    response: str | None = None
    saved_fields: dict[str, str] = {}
    error_message: str | None = None


class BrandProfileRequest(BaseModel):
    campaign_id: int
    brand_name: str = ""
    industry: str = ""
    target_audience: str = ""
    value_proposition: str = ""
    tone_of_voice: str = ""
    positioning: str = ""


class BrandProfileResponse(BaseModel):
    status: str
    response: str | None = None
    saved_fields: dict[str, str] = {}
    suggestions: list[str] = []
    error_message: str | None = None
