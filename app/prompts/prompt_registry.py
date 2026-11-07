from app.prompts.clinical_summary import (
    CLINICAL_SUMMARY_PROMPT,
)
from app.prompts.efficacy_summary import (
    EFFICACY_SUMMARY_PROMPT,
)
from app.prompts.safety_summary import (
    SAFETY_SUMMARY_PROMPT,
)
from app.prompts.literature_review import (
    LITERATURE_REVIEW_PROMPT,
)


PROMPT_REGISTRY = {
    "clinical_summary": CLINICAL_SUMMARY_PROMPT,
    "efficacy_summary": EFFICACY_SUMMARY_PROMPT,
    "safety_summary": SAFETY_SUMMARY_PROMPT,
    "literature_review": LITERATURE_REVIEW_PROMPT,
}


def get_prompt(document_type: str) -> str:

    prompt = PROMPT_REGISTRY.get(document_type)

    if prompt is None:
        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    return prompt