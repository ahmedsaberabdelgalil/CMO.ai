from pydantic import BaseModel


class CalendarAgentRequest(BaseModel):
    message: str
    campaign_id: int


class CalendarAgentResponse(BaseModel):
    status: str
    response: str | None = None
    error_message: str | None = None


class CalendarApplyRequest(BaseModel):
    campaign_id: int
    message: str = ""
    days: int = 14


class CalendarApplyResponse(BaseModel):
    status: str
    items_created: int = 0
    response: str | None = None
    error_message: str | None = None
