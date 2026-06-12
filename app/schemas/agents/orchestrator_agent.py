from typing import Literal

from pydantic import BaseModel

from app.schemas.agents.image_agent import ImageAgentResponse
from app.schemas.agents.video_agent import VideoAgentResponse


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class OrchestratorAgentRequest(BaseModel):
    campaign_id: int
    message: str
    messages: list[ChatTurn] = []


class OrchestratorAgentResponse(BaseModel):
    status: str
    agent: str | None = None
    agent_label: str | None = None
    reason: str | None = None
    response: str | None = None
    error_message: str | None = None
    # Rich results when the orchestrator executes an asset-producing agent.
    image_result: ImageAgentResponse | None = None
    video_result: VideoAgentResponse | None = None
