import re


class QueryProcessor:

    def process(self, query: str) -> str:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        query = query.strip()

        if len(query) > 2000:
            raise ValueError("Query is too long")

        # Normalize repeated whitespace.
        query = re.sub(r"\s+", " ", query)

        return query