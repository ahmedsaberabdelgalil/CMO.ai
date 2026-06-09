from pydantic import BaseModel


class AnalyticsAgentRequest(BaseModel):
    message: str
    campaign_id: int


class AnalyticsAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None
