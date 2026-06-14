import asyncio
from types import SimpleNamespace

from app.services.campaign_context import build_campaign_context


def _brand(**kwargs):
    defaults = dict(
        brand_name="GreenBean",
        industry="Coffee",
        target_audience="young pros",
        value_proposition="ethical energy",
        tone_of_voice="bold",
        positioning="guilt-free fuel",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_context_includes_brand_and_campaign():
    campaign = SimpleNamespace(name="Launch", description="eco coffee", strategy_id=None)
    text = asyncio.run(build_campaign_context(None, campaign, _brand()))

    assert "BRAND PROFILE" in text
    assert "GreenBean" in text
    assert "Launch" in text
    assert "MARKETING PLAN: none linked yet." in text


def test_context_handles_missing_brand():
    campaign = SimpleNamespace(name="Launch", description=None, strategy_id=None)
    text = asyncio.run(build_campaign_context(None, campaign, None))

    assert "BRAND PROFILE: not defined yet." in text
    assert "Launch" in text
