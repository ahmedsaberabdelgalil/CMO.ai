from typing import Literal

from pydantic import BaseModel


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatbotAgentRequest(BaseModel):
    messages: list[ChatTurn] = []


class ChatbotAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None
