import json

from app.rag.query_processor import QueryProcessor
from app.rag.context_builder import ContextBuilder
from app.rag.reranker import MedicalReranker

from app.retrieval.chroma_retrieval import (
    ChromaRetrievalService,
)

from app.llm.ollama_client import OllamaClient

from app.prompts.base import BASE_SYSTEM_PROMPT
from app.prompts.prompt_registry import get_prompt

from app.schemas.structured_summary import (
    StructuredMedicalSummary,
)

from app.validation.citation_validator import (
    CitationValidator,
)


class StructuredSummaryService:

    PROMPT_VERSION = "medical_summary_v2"

    def __init__(self):

        self.query_processor = QueryProcessor()
        self.retriever = ChromaRetrievalService()
        self.reranker = MedicalReranker()
        self.context_builder = ContextBuilder(
            max_tokens=3000
        )

        self.llm = OllamaClient()
        self.citation_validator = CitationValidator()

    def generate(
        self,
        question: str,
        project_id: str,
        document_type: str,
    ) -> dict:

        # Step 1: Process the question.
        question = self.query_processor.process(question)

        # Step 2: Select the prompt template.
        task_prompt = get_prompt(document_type)

        # Step 3: Retrieve evidence.
        candidates = self.retriever.retrieve(
            query=question,
            project_id=project_id,
            limit=15,
        )

        if not candidates:
            raise ValueError(
                "No relevant evidence found."
            )

        # Step 4: Rerank.
        ranked = self.reranker.rerank(
            query=question,
            evidence=candidates,
            top_k=5,
        )

        # Step 5: Assemble context.
        evidence_package = self.context_builder.build(
            ranked
        )

        sources = evidence_package["sources"]

        if not sources:
            raise ValueError(
                "Unable to prepare evidence context."
            )

        # Step 6: Prepare prompt.
        system_prompt = (
            BASE_SYSTEM_PROMPT + "\n\n" + task_prompt
        )

        user_prompt = f"""
USER REQUEST:
{question}

SOURCE EVIDENCE:
{evidence_package["context"]}

OUTPUT REQUIREMENTS:
Return a JSON object matching the supplied schema.

Every factual finding must include the source IDs
that support it.

Do not invent citation identifiers.
If evidence is missing, use the evidence_gaps field.
"""

        # Step 7: Generate structured JSON.
        raw_output = self.llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=(
                StructuredMedicalSummary.model_json_schema()
            ),
        )

        # Step 8: Validate JSON using Pydantic.
        summary = (
            StructuredMedicalSummary.model_validate_json(
                raw_output
            )
        )

        # Step 9: Validate citation IDs.
        citation_result = (
            self.citation_validator.validate(
                summary=summary,
                sources=sources,
            )
        )

        return {
            "question": question,
            "document_type": document_type,
            "prompt_version": self.PROMPT_VERSION,
            "model": self.llm.model,
            "summary": summary.model_dump(),
            "sources": sources,
            "citation_validation": citation_result,
            "human_review_required": True,
            "review_status": "PENDING_REVIEW",
        }