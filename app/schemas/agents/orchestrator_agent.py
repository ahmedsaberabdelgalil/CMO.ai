from typing import Literal

from pydantic import BaseModel

from app.schemas.agents.image_agent import ImageAgentResponse
from app.schemas.agents.marketing_agent import MarketingAgentResponse
from app.schemas.agents.video_agent import VideoAgentResponse


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class OrchestratorAgentRequest(BaseModel):
    campaign_id: int
    message: str
    messages: list[ChatTurn] = []
    # Optionally force a specific agent and skip automatic routing/planning.
    force_agent: str | None = None


class OrchestratorAgentResponse(BaseModel):
    status: str
    agent: str | None = None
    agent_label: str | None = None
    reason: str | None = None
    response: str | None = None
    error_message: str | None = None
    # Every agent that ran (in order) for this request.
    agents: list[str] = []
    # Suggested follow-up prompts the user can run next.
    suggestions: list[str] = []
    # Rich results when the orchestrator executes an asset/strategy agent.
    image_result: ImageAgentResponse | None = None
    video_result: VideoAgentResponse | None = None
    marketing_result: MarketingAgentResponse | None = None
