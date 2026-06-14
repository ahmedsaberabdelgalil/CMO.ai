from pydantic import BaseModel


class AnalyticsAgentRequest(BaseModel):
    message: str = ""
    campaign_id: int
    # Question-driven analysis: a preset focus and/or manually entered metrics.
    focus: str | None = None
    metrics: dict[str, float] | None = None


class AnalyticsAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None
