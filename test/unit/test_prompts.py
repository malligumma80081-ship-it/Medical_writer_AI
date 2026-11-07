import pytest

from app.prompts.prompt_registry import get_prompt


def test_clinical_prompt():
    prompt = get_prompt("clinical_summary")

    assert "Study overview" in prompt


def test_efficacy_prompt():
    prompt = get_prompt("efficacy_summary")

    assert "Primary endpoint" in prompt


def test_safety_prompt():
    prompt = get_prompt("safety_summary")

    assert "Adverse events" in prompt


def test_unknown_prompt():
    with pytest.raises(ValueError):
        get_prompt("unknown_type")