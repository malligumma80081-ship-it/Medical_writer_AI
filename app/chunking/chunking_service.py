from app.chunking.section_detector import detect_section
from app.chunking.recursive_chunker import recursive_chunk
from app.chunking.tokenizer import count_tokens


class MedicalChunkingService:

    def __init__(
        self,
        max_tokens: int = 500,
        overlap: int = 75,
    ):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk_segments(
        self,
        segments: list[dict],
    ) -> list[dict]:

        output = []
        chunk_index = 0
        current_section = "general"

        for segment in segments:
            page_number = segment.get("page_number")
            text = segment.get("text", "")

            if not text.strip():
                continue

            # Detect section headings line by line.
            content_lines = []

            for line in text.splitlines():
                detected = detect_section(line)

                if detected != "general":
                    current_section = detected
                else:
                    content_lines.append(line)

            content = "\n".join(content_lines).strip()

            if not content:
                continue

            chunks = recursive_chunk(
                content,
                max_tokens=self.max_tokens,
                overlap=self.overlap,
            )

            for chunk in chunks:
                if not chunk.strip():
                    continue

                output.append({
                    "chunk_index": chunk_index,
                    "section": current_section,
                    "page_number": page_number,
                    "content": chunk,
                    "token_count": count_tokens(chunk),
                })

                chunk_index += 1

        return output