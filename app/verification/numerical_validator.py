import re
from decimal import Decimal


NUMBER_PATTERN = re.compile(
    r"(?<!\w)"
    r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?"
    r"\s*%?"
)


def extract_numbers(text: str) -> list[str]:

    return [
        match.group(0).strip().replace(",", "")
        for match in NUMBER_PATTERN.finditer(text)
    ]


class NumericalValidator:

    def validate(
        self,
        claim: str,
        evidence: str,
    ) -> dict:

        claim_numbers = extract_numbers(claim)
        evidence_numbers = extract_numbers(evidence)

        if not claim_numbers:
            return {
                "applicable": False,
                "passed": None,
                "claim_numbers": [],
                "evidence_numbers": evidence_numbers,
            }

        missing = []

        for number in claim_numbers:

            if number not in evidence_numbers:
                missing.append(number)

        return {
            "applicable": True,
            "passed": not missing,
            "claim_numbers": claim_numbers,
            "evidence_numbers": evidence_numbers,
            "missing_numbers": missing,
        }