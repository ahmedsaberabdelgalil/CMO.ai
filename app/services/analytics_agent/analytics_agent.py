import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a marketing performance analyst. "
            "Use the metrics context provided and answer the user's task in plain text — "
            "no markdown headers, tables, or bullet symbols like # or **. "
            "Be specific, data-informed, and actionable.",
        ),
        (
            "human",
            "Campaign: {campaign_name}\n"
            "Brand: {brand_name}\n"
            "Industry: {industry}\n"
            "Audience: {audience}\n\n"
            "Performance metrics context:\n{metrics_context}\n\n"
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
        temperature=0.4,
        groq_api_key=settings.GROQ_API_KEY,
    )


def run_analytics_agent(
    *,
    message: str,
    brand_name: str,
    industry: str,
    audience: str,
    campaign_name: str,
    metrics_context: str,
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
                "metrics_context": metrics_context or "No metrics recorded yet.",
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
