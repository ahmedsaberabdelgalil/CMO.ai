from app.services.brand_agent import suggest_brand_prompts


def test_suggest_brand_prompts_personalized():
    prompts = suggest_brand_prompts(brand_name="GreenBean", audience="founders")

    assert len(prompts) >= 3
    assert any("GreenBean" in p for p in prompts)
    assert any("founders" in p for p in prompts)


def test_suggest_brand_prompts_defaults():
    prompts = suggest_brand_prompts()

    assert len(prompts) >= 3
    assert all(isinstance(p, str) and p for p in prompts)
