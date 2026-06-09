from pydantic import BaseModel


class CalendarAgentRequest(BaseModel):
    message: str
    campaign_id: int


class CalendarAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None
