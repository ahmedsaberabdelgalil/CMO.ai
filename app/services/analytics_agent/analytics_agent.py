import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a Performance Analytics AI Agent — part of CMO.AI. "
            "Your role is to analyze business and marketing data and provide actionable insights. "
            "When given data you: identify top performers, spot trends and patterns, highlight "
            "underperformers, give concrete prioritized recommendations, and suggest next steps "
            "with estimated impact.\n\n"
            "Always structure your analysis with these labelled sections, each on its own line:\n"
            "Key Findings (top 3-5 insights)\n"
            "Areas of Concern\n"
            "What's Working Well\n"
            "Recommendations (prioritized)\n"
            "Predicted Impact (if recommendations are followed)\n\n"
            "Be data-driven, specific, and business-focused. Use clear plain text — "
            "no markdown headers, tables, or bullet symbols like # or **.",
        ),
        (
            "human",
            "{shared_context}\n\n"
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
                "metrics_context": metrics_context or "No metrics recorded yet.",
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
