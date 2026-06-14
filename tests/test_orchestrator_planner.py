from app.services.orchestrator_agent import orchestrator_agent


def test_plan_steps_parses_multi_step(monkeypatch):
    payload = (
        '{"steps": [{"agent": "marketing", "task": "make a plan"}, '
        '{"agent": "image", "task": "make an image"}]}'
    )
    monkeypatch.setattr(orchestrator_agent, "run_chat", lambda *a, **k: payload)

    steps = orchestrator_agent.plan_steps("plan and image")

    assert len(steps) == 2
    assert steps[0]["agent"] == "marketing"
    assert steps[1]["agent"] == "image"


def test_plan_steps_drops_invalid_agents(monkeypatch):
    payload = '{"steps": [{"agent": "bogus", "task": "x"}, {"agent": "content", "task": "y"}]}'
    monkeypatch.setattr(orchestrator_agent, "run_chat", lambda *a, **k: payload)

    steps = orchestrator_agent.plan_steps("write something")

    assert [s["agent"] for s in steps] == ["content"]


def test_plan_steps_falls_back_to_chatbot_when_unavailable(monkeypatch):
    monkeypatch.setattr(orchestrator_agent, "run_chat", lambda *a, **k: None)

    steps = orchestrator_agent.plan_steps("hello there")

    assert len(steps) == 1
    assert steps[0]["agent"] in orchestrator_agent.VALID_AGENTS


def test_route_intent_valid(monkeypatch):
    monkeypatch.setattr(
        orchestrator_agent,
        "run_chat",
        lambda *a, **k: '{"agent": "analytics", "reason": "metrics question"}',
    )

    result = orchestrator_agent.route_intent("how did we perform?")

    assert result["agent"] == "analytics"
