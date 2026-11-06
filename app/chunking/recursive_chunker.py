import re

from app.chunking.tokenizer import (
    count_tokens,
    split_by_tokens,
)


def split_into_units(text: str) -> list[str]:
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    units = []

    for paragraph in paragraphs:
        if count_tokens(paragraph) <= 500:
            units.append(paragraph)
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )

        units.extend(
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        )

    return units


def recursive_chunk(
    text: str,
    max_tokens: int = 500,
    overlap: int = 75,
) -> list[str]:

    units = split_into_units(text)

    chunks = []
    current_units = []

    for unit in units:
        candidate = " ".join(current_units + [unit])

        if count_tokens(candidate) <= max_tokens:
            current_units.append(unit)
            continue

        if current_units:
            chunks.append(" ".join(current_units))

        # A single sentence may itself exceed the limit.
        if count_tokens(unit) > max_tokens:
            chunks.extend(
                split_by_tokens(
                    unit,
                    max_tokens=max_tokens,
                    overlap=overlap,
                )
            )
            current_units = []
        else:
            current_units = [unit]

    if current_units:
        chunks.append(" ".join(current_units))

    return chunks