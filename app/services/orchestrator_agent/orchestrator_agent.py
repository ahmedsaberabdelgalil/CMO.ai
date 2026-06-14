"""
Orchestrator Agent.

Acts as the campaign command center: given a free-form prompt it decides which
specialist agent should handle the request. The API layer then dispatches to
that agent (with database-backed context) and returns the combined result.

The orchestrator itself only performs routing — keeping it fast and side-effect
free. Dispatch/execution lives in the API route so it can access the DB and the
other agent services.
"""

import json
import re

from app.services.agent_llm import run_chat

VALID_AGENTS = {
    "content",
    "image",
    "video",
    "marketing",
    "calendar",
    "analytics",
    "brand",
    "chatbot",
}

ROUTER_SYSTEM = """You are the Orchestrator router for CMO.AI, a virtual Chief Marketing Officer system.

Given a user request, choose EXACTLY ONE specialist agent best suited to handle it.

Available agents:
- content: writing social media posts, ads, emails, captions, or any marketing copy
- image: image/visual generation, creative briefs, or visual asset ideas
- video: video scripts, storyboards, reels, or creator briefs
- marketing: full marketing strategy, content pillars, budget plans, go-to-market
- calendar: content calendar planning, scheduling, posting cadence, timing
- analytics: performance analysis, metrics, funnel diagnosis, budget reallocation
- brand: brand positioning, identity, voice, audience definition, brand strategy
- chatbot: general marketing questions, platform help, or anything that does not fit the others

Respond ONLY with a single line of valid JSON in this exact format:
{"agent": "<one agent name from the list>", "reason": "<short reason>"}"""


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


PLANNER_SYSTEM = """You are the Orchestrator planner for CMO.AI, a virtual Chief Marketing Officer system.

Break the user's request into an ORDERED list of 1 to 4 steps. Each step assigns ONE specialist agent a concrete sub-task written as a clear instruction.

Use MULTIPLE steps ONLY when the request clearly asks for more than one deliverable
(e.g. "create a plan and then design an image", "write a caption and a video script").
For a single deliverable, return EXACTLY ONE step.

Available agents:
- content: social posts, ads, emails, captions, marketing copy
- image: image/visual generation, creative briefs
- video: video scripts, storyboards, reels, creator briefs
- marketing: full marketing strategy, content pillars, budget plans, go-to-market
- calendar: content calendar planning, scheduling, posting cadence
- analytics: performance analysis, metrics, funnel diagnosis, budget reallocation
- brand: brand positioning, identity, voice, audience definition
- chatbot: general marketing questions, platform help, anything else

Respond ONLY with a single line of valid JSON in this exact format:
{"steps": [{"agent": "<agent name>", "task": "<sub-task instruction>"}]}"""


def plan_steps(message: str, recent_context: str = "") -> list[dict]:
    """
    Decompose a request into an ordered list of {"agent", "task"} steps.

    Returns a single-step plan for simple requests and a multi-step plan only
    when the request clearly needs several deliverables. Falls back to one
    routing decision (or the chatbot) when planning is unavailable.
    """
    if recent_context.strip():
        user_content = (
            "Recent conversation:\n"
            f"{recent_context}\n\n"
            f"Latest user message: {message}\n\n"
            "Plan the steps needed to fulfill the latest user message."
        )
    else:
        user_content = message

    text = run_chat(
        PLANNER_SYSTEM,
        [{"role": "user", "content": user_content}],
        temperature=0.0,
    )

    parsed = _extract_json(text) if text else None
    steps: list[dict] = []
    if parsed and isinstance(parsed.get("steps"), list):
        for raw in parsed["steps"][:4]:
            agent = str(raw.get("agent", "")).strip().lower()
            task = str(raw.get("task", "")).strip() or message
            if agent in VALID_AGENTS:
                steps.append({"agent": agent, "task": task})

    if steps:
        return steps

    # Fall back to single-intent routing, then to the chatbot.
    routed = route_intent(message, recent_context)
    return [{"agent": routed["agent"], "task": message}]


def route_intent(message: str, recent_context: str = "") -> dict:
    """
    Decide which agent should handle the latest message.

    `recent_context` is an optional plain-text transcript of the last few turns
    so that short follow-ups ("make it shorter", "why?") route consistently.

    Returns {"agent": <name>, "reason": <str>}. Falls back to the chatbot agent
    when routing is unavailable or ambiguous.
    """
    fallback = {"agent": "chatbot", "reason": "General request routed to support chatbot."}

    if recent_context.strip():
        user_content = (
            "Recent conversation:\n"
            f"{recent_context}\n\n"
            f"Latest user message: {message}\n\n"
            "Choose the best agent for the latest user message."
        )
    else:
        user_content = message

    text = run_chat(
        ROUTER_SYSTEM,
        [{"role": "user", "content": user_content}],
        temperature=0.0,
    )
    if text is None:
        return {"agent": "chatbot", "reason": "GROQ_API_KEY is not configured."}

    parsed = _extract_json(text)
    if not parsed:
        return fallback

    agent = str(parsed.get("agent", "")).strip().lower()
    if agent not in VALID_AGENTS:
        return fallback

    reason = str(parsed.get("reason", "")).strip() or f"Routed to {agent} agent."
    return {"agent": agent, "reason": reason}
