from pydantic import ValidationError

from app.schemas.structured_summary import (
    StructuredMedicalSummary,
)


class SummaryValidator:

    def validate(self, raw_output: str):

        try:
            summary = (
                StructuredMedicalSummary
                .model_validate_json(raw_output)
            )

            return {
                "is_valid": True,
                "summary": summary,
                "errors": [],
            }

        except ValidationError as exc:

            return {
                "is_valid": False,
                "summary": None,
                "errors": exc.errors(),
            }