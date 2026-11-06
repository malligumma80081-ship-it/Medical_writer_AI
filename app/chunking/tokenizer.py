import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))


def split_by_tokens(
    text: str,
    max_tokens: int,
    overlap: int,
) -> list[str]:
    tokens = encoding.encode(text)

    if not tokens:
        return []

    if overlap >= max_tokens:
        raise ValueError("Overlap must be smaller than max_tokens.")

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))

        chunk = encoding.decode(tokens[start:end])
        chunks.append(chunk)

        if end == len(tokens):
            break

        start = end - overlap

    return chunks