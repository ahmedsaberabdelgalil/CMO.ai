import pytest
from pydantic import ValidationError

from app.schemas.agents.analytics_agent import AnalyticsAgentRequest
from app.schemas.agents.brand_agent import BrandProfileRequest
from app.schemas.agents.orchestrator_agent import OrchestratorAgentRequest


def test_analytics_request_defaults():
    req = AnalyticsAgentRequest(campaign_id=1)
    assert req.message == ""
    assert req.focus is None
    assert req.metrics is None


def test_analytics_request_with_metrics():
    req = AnalyticsAgentRequest(
        campaign_id=1, focus="funnel", metrics={"clicks": 10, "spend": 50.5}
    )
    assert req.focus == "funnel"
    assert req.metrics["clicks"] == 10


def test_brand_profile_request_minimal():
    req = BrandProfileRequest(campaign_id=2, brand_name="Acme")
    assert req.brand_name == "Acme"
    assert req.industry == ""


def test_orchestrator_request_requires_message():
    with pytest.raises(ValidationError):
        OrchestratorAgentRequest(campaign_id=1)


def test_orchestrator_force_agent_optional():
    req = OrchestratorAgentRequest(campaign_id=1, message="hi", force_agent="image")
    assert req.force_agent == "image"
