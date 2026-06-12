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
