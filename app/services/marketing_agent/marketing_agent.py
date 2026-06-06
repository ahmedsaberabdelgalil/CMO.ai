from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import re


def _get_llm():
    return ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.4,
        groq_api_key=settings.GROQ_API_KEY,
    )


def budget_allocator(budget, platforms):
    if not platforms:
        return "No platforms selected"

    allocation = {}
    per_platform = budget / len(platforms)

    for p in platforms:
        allocation[p] = {
            "ads": round(per_platform * 0.7, 2),
            "content": round(per_platform * 0.3, 2)
        }

    return allocation


def platform_strategy(audience):
    audience = audience.lower()

    if "18" in audience or "young" in audience:
        return "Focus on TikTok & Instagram (short-form video, trends, influencers)."
    elif "professional" in audience:
        return "Focus on LinkedIn & YouTube (educational + authority content)."
    else:
        return "Balanced mix of Instagram, Facebook, and YouTube."


def financial_model(budget):
    """
    REAL calculations (not LLM guessing)
    """
    ctr = 0.02
    conversion_rate = 0.03
    avg_order_value = 30

    clicks = int(budget / 0.5)  # assume $0.5 CPC
    sales = int(clicks * conversion_rate)
    revenue = sales * avg_order_value

    cpa = budget / sales if sales > 0 else 0
    roas = revenue / budget if budget > 0 else 0

    return {
        "Estimated Clicks": clicks,
        "Estimated Sales": sales,
        "Estimated Revenue": revenue,
        "CPA": round(cpa, 2),
        "ROAS": round(roas, 2)
    }


def decision_logic(budget):
    if budget < 500:
        return "Low budget → Focus on organic content + 1 platform only. Avoid paid ads."
    elif budget < 1500:
        return "Medium budget → Mix organic + small paid ads + micro-influencers."
    else:
        return "High budget → Scale paid ads, influencers, and content production."


def competitor_insight(industry):
    return f"In the {industry} industry, many competitors focus on generic messaging. A strong opportunity is to differentiate through authenticity, niche targeting, and community-driven branding."


template = """
You are a senior Chief Marketing Officer (CMO).

Use ALL the structured insights below to create a REALISTIC, data-driven marketing strategy.

BUSINESS:
Brand: {brand}
Industry: {industry}
Product: {product}
Audience: {audience}
Goal: {goal}

PLATFORM INSIGHT:
{platform_insight}

DECISION STRATEGY:
{decision}

COMPETITOR INSIGHT:
{competitor}

BUDGET BREAKDOWN:
{budget_plan}

FINANCIAL PROJECTIONS:
{financials}

Instructions:
- Think step-by-step
- Justify decisions using the numbers
- Be realistic (not overly optimistic)
- Write in PLAIN TEXT only — no markdown
- Do NOT use # headers, ** bold, | tables, --- dividers, or HTML
- Use numbered section titles on their own line (e.g. "1. Target Audience Analysis")
- Use simple dashes (-) for bullet lists
- Keep paragraphs short and scannable

Generate:

1. Target Audience Analysis
2. Positioning & Differentiation
3. Content Strategy
4. Campaign Plan
5. Weekly Posting Schedule
6. Budget Justification (BASED ON NUMBERS)
7. Expected Results & KPIs (USE financial projections)

Be professional and specific.
"""

prompt = ChatPromptTemplate.from_template(template)


def _plain_text(text: str) -> str:
    """Normalize LLM output to readable plain text without markdown artifacts."""
    cleaned = (text or "").replace("\r\n", "\n")
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"^---+$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\|", " · ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def run_marketing_agent(
    brand: str,
    industry: str,
    product: str,
    audience: str,
    goal: str,
    budget: float,
    platforms: list,
) -> dict:
    """Called via asyncio.to_thread from the FastAPI endpoint."""

    budget_plan = budget_allocator(budget, platforms)
    platform_insight = platform_strategy(audience)
    financials = financial_model(budget)
    decision = decision_logic(budget)
    competitor = competitor_insight(industry)

    try:
        llm = _get_llm()
        chain = prompt | llm
        response = chain.invoke({
            "brand": brand,
            "industry": industry,
            "product": product,
            "audience": audience,
            "goal": goal,
            "platform_insight": platform_insight,
            "decision": decision,
            "competitor": competitor,
            "budget_plan": str(budget_plan),
            "financials": str(financials),
        })
        strategy_text = _plain_text(response.content)
    except Exception as e:
        strategy_text = f"Strategy generation failed: {str(e)}"

    return {
        "status": "success",
        "strategy": strategy_text,
        "financial_model": financials,
        "budget_allocation": budget_plan,
        "platform_insight": platform_insight,
        "decision": decision,
        "competitor_insight": competitor,
    }
