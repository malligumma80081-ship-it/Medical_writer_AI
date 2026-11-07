from app.prompts.medical_summary import (
    SYSTEM_PROMPT,
    build_summary_prompt,
)


def test_prompt_contains_evidence_restrictions():
    assert "Do not invent" in SYSTEM_PROMPT
    assert "source evidence" in SYSTEM_PROMPT


def test_summary_prompt_includes_question():
    prompt = build_summary_prompt(
        question="Summarize primary efficacy outcomes",
        context="[S1] The primary endpoint was...",
    )

    assert "primary efficacy outcomes" in prompt
    assert "[S1]" in prompt


def test_prompt_mentions_missing_evidence():
    prompt = build_summary_prompt(
        question="Summarize safety",
        context="",
    )

    assert "Not reported in the retrieved evidence" in prompt