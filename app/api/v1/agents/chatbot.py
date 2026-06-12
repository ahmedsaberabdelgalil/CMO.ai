import asyncio

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user_async
from app.models.user import User
from app.schemas.agents.chatbot_agent import ChatbotAgentRequest, ChatbotAgentResponse
from app.services.chatbot_agent import run_chatbot

router = APIRouter(prefix="/agents/chatbot", tags=["Chatbot Agent"])


@router.post("/generate", response_model=ChatbotAgentResponse)
async def generate_chatbot_response(
    data: ChatbotAgentRequest,
    current_user: User = Depends(get_current_user_async),
):
    history = [turn.model_dump() for turn in data.messages]
    output = await asyncio.to_thread(run_chatbot, history=history)
    return ChatbotAgentResponse(**output)
