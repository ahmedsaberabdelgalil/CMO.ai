import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a content calendar strategist for marketing campaigns. "
            "Use the campaign context and any schedule data provided. "
            "Answer the user's task in plain text — no markdown headers, tables, or bullet symbols like # or **. "
            "Be specific, actionable, and concise.",
        ),
        (
            "human",
            "{shared_context}\n\n"
            "Campaign: {campaign_name}\n"
            "Brand: {brand_name}\n"
            "Industry: {industry}\n"
            "Audience: {audience}\n"
            "Campaign notes: {campaign_notes}\n\n"
            "Current schedule context:\n{schedule_context}\n\n"
            "Task: {message}",
        ),
    ]
)


def _plain_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def _build_llm():
    if not settings.GROQ_API_KEY:
        return None
    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=0.5,
        groq_api_key=settings.GROQ_API_KEY,
    )


def run_calendar_agent(
    *,
    message: str,
    brand_name: str,
    industry: str,
    audience: str,
    campaign_name: str,
    campaign_notes: str,
    schedule_context: str,
    shared_context: str = "",
) -> dict:
    llm = _build_llm()
    if llm is None:
        return {
            "status": "error",
            "response": None,
            "error_message": "GROQ_API_KEY is not configured.",
        }

    try:
        chain = PROMPT | llm
        result = chain.invoke(
            {
                "message": message,
                "brand_name": brand_name or "Brand",
                "industry": industry or "General",
                "audience": audience or "General audience",
                "campaign_name": campaign_name or "Campaign",
                "campaign_notes": campaign_notes or "None",
                "schedule_context": schedule_context or "No schedule loaded yet.",
                "shared_context": shared_context or "No additional campaign context.",
            }
        )
        return {
            "status": "success",
            "response": _plain_text(result.content),
            "error_message": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "response": None,
            "error_message": str(e),
        }


_ITEMS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a content calendar planner. Produce a concrete posting schedule "
            "as STRICT JSON only — no prose, no markdown. "
            'Return: {{"items": [{{"day_offset": <int 0-based>, "platform": "<one of '
            "Instagram, TikTok, Facebook, LinkedIn, YouTube, Twitter, Email>\", "
            '"title": "<short post title>", "objective": "<goal>", '
            '"caption": "<1-2 sentence caption>"}}]}}. '
            "Generate exactly {days} items, one per day starting at day_offset 0, "
            "rotating platforms sensibly for the audience.",
        ),
        (
            "human",
            "{shared_context}\n\n"
            "Campaign: {campaign_name}\n"
            "Brand: {brand_name}\n"
            "Audience: {audience}\n"
            "Platforms to use: {platforms}\n"
            "Extra direction: {message}\n\n"
            "Return the JSON now.",
        ),
    ]
)


def _extract_json(text: str) -> dict | None:
    if not text:
        return None
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except (ValueError, TypeError):
        return None


def generate_calendar_items(
    *,
    message: str,
    brand_name: str,
    audience: str,
    campaign_name: str,
    platforms: list[str],
    shared_context: str = "",
    days: int = 14,
) -> dict:
    """Generate a structured list of calendar items (for persistence)."""
    llm = _build_llm()
    if llm is None:
        return {
            "status": "error",
            "items": [],
            "error_message": "GROQ_API_KEY is not configured.",
        }

    try:
        chain = _ITEMS_PROMPT | llm
        result = chain.invoke(
            {
                "message": message or "Balanced awareness-to-conversion mix.",
                "brand_name": brand_name or "Brand",
                "audience": audience or "General audience",
                "campaign_name": campaign_name or "Campaign",
                "platforms": ", ".join(platforms) if platforms else "Instagram, TikTok",
                "shared_context": shared_context or "No additional campaign context.",
                "days": days,
            }
        )
        parsed = _extract_json(result.content)
        items = parsed.get("items") if parsed else None
        if not isinstance(items, list) or not items:
            return {
                "status": "error",
                "items": [],
                "error_message": "The agent did not return a valid schedule.",
            }
        return {"status": "success", "items": items[:days], "error_message": None}
    except Exception as e:
        return {"status": "error", "items": [], "error_message": str(e)}
