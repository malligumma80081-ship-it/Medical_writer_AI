from app.chunking.tokenizer import count_tokens


class ContextBuilder:

    def __init__(self, max_tokens: int = 3000):
        self.max_tokens = max_tokens

    def build(self, evidence: list[dict]) -> dict:

        selected = []
        seen = set()
        current_tokens = 0

        for index, item in enumerate(evidence, start=1):

            content = (item.get("content") or "").strip()

            if not content:
                continue

            # Avoid duplicate passages.
            if content in seen:
                continue

            token_count = count_tokens(content)

            if current_tokens + token_count > self.max_tokens:
                continue

            seen.add(content)
            current_tokens += token_count

            source = {
                "citation_id": f"S{len(selected) + 1}",
                "document_id": item.get("document_id"),
                "file_name": item.get("file_name"),
                "section": item.get("section"),
                "page_number": item.get("page_number"),
                "chunk_id": item.get("chunk_id"),
                "content": content,
                "retrieval_score": item.get("score"),
                "rerank_score": item.get("rerank_score"),
            }

            selected.append(source)

        context_parts = []

        for source in selected:
            context_parts.append(
                f"[{source['citation_id']}]\n"
                f"Document: {source['file_name']}\n"
                f"Section: {source['section']}\n"
                f"Page: {source['page_number']}\n"
                f"Evidence: {source['content']}"
            )

        return {
            "context": "\n\n".join(context_parts),
            "sources": selected,
            "total_tokens": current_tokens,
        }