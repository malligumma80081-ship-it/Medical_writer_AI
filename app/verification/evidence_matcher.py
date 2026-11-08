class EvidenceMatcher:

    def match(
        self,
        citation_ids: list[str],
        sources: list[dict],
    ) -> list[dict]:

        source_map = {
            source["citation_id"]: source
            for source in sources
        }

        matched = []

        for citation_id in citation_ids:

            source = source_map.get(citation_id)

            if source:
                matched.append({
                    "citation_id": citation_id,
                    "document_id": source.get("document_id"),
                    "file_name": source.get("file_name"),
                    "section": source.get("section"),
                    "page_number": source.get("page_number"),
                    "content": source.get("content", ""),
                })

        return matched