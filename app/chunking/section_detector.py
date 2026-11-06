import re

SECTION_PATTERNS = {
    "abstract": r"^\s*abstract\s*$",
    "introduction": r"^\s*\d*\.?\s*introduction\s*$",
    "methods": (
        r"^\s*(materials and methods|"
        r"methods|methodology|study design)\s*$"
    ),
    "results": r"^\s*\d*\.?\s*results\s*$",
    "discussion": r"^\s*\d*\.?\s*discussion\s*$",
    "conclusion": r"^\s*(conclusion|conclusions)\s*$",
    "references": r"^\s*references\s*$",
}


def detect_section(text: str) -> str:
    """Return the section name if text is a recognized heading."""

    normalized = text.strip()

    for section, pattern in SECTION_PATTERNS.items():
        if re.match(pattern, normalized, re.IGNORECASE):
            return section

    return "general"