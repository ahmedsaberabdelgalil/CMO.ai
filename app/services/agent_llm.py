"""
Shared Groq chat helper for the conversational agents.

These agents (Brand Coaching, Support Chatbot, Orchestrator) follow the
multi-turn pattern from the reference implementation but run on the project's
existing Groq infrastructure instead of Gemini, so no extra API key is needed.
"""

import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import settings


def build_chat_llm(temperature: float = 0.6):
    """Return a configured ChatGroq instance, or None if Groq is not configured."""
    if not settings.GROQ_API_KEY:
        return None
    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=temperature,
        groq_api_key=settings.GROQ_API_KEY,
    )


def run_chat(
    system_prompt: str,
    history: list[dict],
    *,
    temperature: float = 0.6,
) -> str | None:
    """
    Run a chat completion with a system prompt and a conversation history.

    history items are dicts shaped like {"role": "user"|"assistant", "content": str}.
    Returns the assistant text, or None if Groq is not configured.
    """
    llm = build_chat_llm(temperature)
    if llm is None:
        return None

    messages: list = [SystemMessage(content=system_prompt)]
    for turn in history:
        role = turn.get("role")
        content = turn.get("content") or ""
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    response = llm.invoke(messages)
    return response.content


def to_plain_text(text: str) -> str:
    """Strip markdown headers, bold markers, and bullet symbols for clean display."""
    if not text:
        return ""
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    return text.strip()
