"""
Brand Coaching Agent.

Ported from the reference `brand_coaching.py` (originally Gemini) onto the
project's Groq stack. Provides:
  - run_brand_coaching: an interactive, multi-turn coaching conversation
  - generate_brand_report: a full Brand Strategy Report from the conversation
  - extract_brand_profile: structured brand fields extracted from the chat so
    they can be persisted to the brand record
"""

import json
import re

from app.services.agent_llm import run_chat

BRAND_COACHING_SYSTEM = """You are a Brand Coaching AI Agent — part of CMO.AI, a virtual Chief Marketing Officer system.

Your role is to interview startup founders and business owners to understand their business and build a strong brand from the ground up.

You must DISCOVER the following about the business, one focused question at a time:
1. What the business does — the core idea, product, or service
2. The target audience and customer personas
3. The unique value proposition (what makes it different)
4. The desired brand voice and tone
5. Brand positioning (the promise in one sentence)
6. Preferred marketing channels

Guidelines:
- Open by briefly introducing yourself, then ask the FIRST discovery question.
- Ask only ONE focused question per message and wait for the answer before moving on.
- Acknowledge each answer in one short sentence, then ask the next missing piece.
- Do not produce a voice guide, report, or recommendations until you have gathered
  the business idea, audience, value proposition, and desired tone.
- When you have enough information, briefly confirm what you learned and tell the user
  they can save the brand profile or generate a full brand report.
- Be encouraging, strategic, and specific.
- Write in clear plain text with simple section labels; avoid markdown symbols like # or **

If campaign and brand context is provided below, use it to avoid re-asking what you already know.
{context}"""

REPORT_SYSTEM = "You are a senior brand strategist producing a polished Brand Strategy Report."

EXTRACT_SYSTEM = """You extract a structured brand profile from a brand coaching conversation.

Return ONLY a single JSON object with EXACTLY these string keys:
{
  "brand_name": "",
  "industry": "",
  "target_audience": "",
  "value_proposition": "",
  "tone_of_voice": "",
  "positioning": ""
}

Rules:
- Fill each field using what the user described in the conversation.
- If a field was never discussed and no reasonable value exists, use an empty string "".
- Keep each value concise (one short phrase or sentence). No markdown."""


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


def _format_context(
    *,
    brand_name: str,
    industry: str,
    audience: str,
    campaign_name: str,
    campaign_notes: str,
) -> str:
    return (
        "\n\nKnown context:\n"
        f"- Brand: {brand_name}\n"
        f"- Industry: {industry}\n"
        f"- Audience: {audience}\n"
        f"- Campaign: {campaign_name}\n"
        f"- Campaign notes: {campaign_notes}"
    )


def run_brand_coaching(
    *,
    history: list[dict],
    brand_name: str = "Brand",
    industry: str = "General",
    audience: str = "General audience",
    campaign_name: str = "Campaign",
    campaign_notes: str = "None",
) -> dict:
    """Get the next coaching response given the conversation history."""
    context = _format_context(
        brand_name=brand_name,
        industry=industry,
        audience=audience,
        campaign_name=campaign_name,
        campaign_notes=campaign_notes,
    )
    system = BRAND_COACHING_SYSTEM.format(context=context)

    if not history:
        history = [
            {
                "role": "user",
                "content": "Greet me and start coaching me on building my brand.",
            }
        ]

    try:
        text = run_chat(system, history, temperature=0.6)
        if text is None:
            return {
                "status": "error",
                "response": None,
                "error_message": "GROQ_API_KEY is not configured.",
            }
        return {"status": "success", "response": text.strip(), "error_message": None}
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}


def generate_brand_report(
    *,
    history: list[dict],
    brand_name: str = "Brand",
    industry: str = "General",
    audience: str = "General audience",
    campaign_name: str = "Campaign",
    campaign_notes: str = "None",
) -> dict:
    """Generate a full Brand Strategy Report from the coaching conversation."""
    conversation_text = "\n".join(
        f"{turn.get('role', 'user').upper()}: {turn.get('content', '')}"
        for turn in history
        if turn.get("content")
    )

    context = _format_context(
        brand_name=brand_name,
        industry=industry,
        audience=audience,
        campaign_name=campaign_name,
        campaign_notes=campaign_notes,
    )

    prompt = (
        "Based on this brand coaching conversation and the known context, generate a "
        "comprehensive Brand Strategy Report.\n"
        f"{context}\n\n"
        "CONVERSATION:\n"
        f"{conversation_text or 'No conversation yet — use the known context.'}\n\n"
        "Generate a detailed Brand Strategy Report with these sections:\n"
        "1. Business Overview\n"
        "2. Target Audience & Customer Personas\n"
        "3. Unique Value Proposition\n"
        "4. Brand Voice & Tone\n"
        "5. Recommended Marketing Channels\n"
        "6. Key Brand Messages\n"
        "7. 30-Day Quick Start Action Plan\n\n"
        "Make it professional, actionable, and specific to this business. "
        "Use clear plain text with simple section labels; avoid markdown symbols like # or **."
    )

    try:
        text = run_chat(
            REPORT_SYSTEM,
            [{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        if text is None:
            return {
                "status": "error",
                "response": None,
                "error_message": "GROQ_API_KEY is not configured.",
            }
        return {"status": "success", "response": text.strip(), "error_message": None}
    except Exception as e:
        return {"status": "error", "response": None, "error_message": str(e)}


BRAND_FIELDS = (
    "brand_name",
    "industry",
    "target_audience",
    "value_proposition",
    "tone_of_voice",
    "positioning",
)


def suggest_brand_prompts(
    *,
    brand_name: str = "your brand",
    audience: str = "your audience",
) -> list[str]:
    """
    Return ready-to-run prompt options the user can send to the agents after
    saving their brand profile. Static + personalized for instant, reliable UX.
    """
    name = (brand_name or "your brand").strip() or "your brand"
    aud = (audience or "your audience").strip() or "your audience"
    return [
        f"Create a brand voice guide for {name}.",
        f"Write 3 key brand messages for {name} aimed at {aud}.",
        f"List the main objections {aud} may have and how to answer them.",
        f"Draft a one-sentence positioning statement for {name}.",
        f"Suggest the best marketing channels for {name} to reach {aud}.",
    ]


def extract_brand_profile(*, history: list[dict]) -> dict:
    """
    Extract structured brand fields from the coaching conversation.

    Returns {"status", "profile": {field: value}, "error_message"} where profile
    only contains non-empty fields the model was able to determine.
    """
    conversation_text = "\n".join(
        f"{turn.get('role', 'user').upper()}: {turn.get('content', '')}"
        for turn in history
        if turn.get("content")
    )

    if not conversation_text.strip():
        return {
            "status": "error",
            "profile": {},
            "error_message": "There is no conversation to build a brand profile from yet.",
        }

    prompt = (
        "Extract the brand profile from this conversation:\n\n" + conversation_text
    )

    try:
        text = run_chat(
            EXTRACT_SYSTEM,
            [{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        if text is None:
            return {
                "status": "error",
                "profile": {},
                "error_message": "GROQ_API_KEY is not configured.",
            }

        parsed = _extract_json(text) or {}
        profile = {
            field: str(parsed.get(field, "")).strip()
            for field in BRAND_FIELDS
            if str(parsed.get(field, "")).strip()
        }
        return {"status": "success", "profile": profile, "error_message": None}
    except Exception as e:
        return {"status": "error", "profile": {}, "error_message": str(e)}
