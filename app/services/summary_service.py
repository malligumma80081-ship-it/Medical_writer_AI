from app.retrieval.chroma_retrieval import ChromaRetrievalService
from app.rag.reranker import MedicalReranker
from app.rag.context_builder import ContextBuilder
from app.rag.query_processor import QueryProcessor

from app.llm.llm_gateway import LLMGateway
from app.prompts.medical_summary import (
    SYSTEM_PROMPT,
    build_summary_prompt,
)


class MedicalSummaryService:

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.retriever = ChromaRetrievalService()
        self.reranker = MedicalReranker()
        self.context_builder = ContextBuilder(
            max_tokens=3000
        )
        self.llm = LLMGateway()

    def generate_summary(
        self,
        question: str,
        project_id: str,
    ) -> dict:

        processed_question = (
            self.query_processor.process(question)
        )

        # Step 1: Retrieve evidence from ChromaDB.
        candidates = self.retriever.retrieve(
            query=processed_question,
            project_id=project_id,
            limit=15,
        )

        if not candidates:
            raise ValueError(
                "No relevant evidence found in this project."
            )

        # Step 2: Rerank retrieved evidence.
        ranked = self.reranker.rerank(
            query=processed_question,
            evidence=candidates,
            top_k=5,
        )

        # Step 3: Build evidence context.
        evidence_package = self.context_builder.build(
            ranked
        )

        if not evidence_package["sources"]:
            raise ValueError(
                "No evidence could be prepared for generation."
            )

        # Step 4: Build medical writing prompt.
        user_prompt = build_summary_prompt(
            question=processed_question,
            context=evidence_package["context"],
        )

        # Step 5: Generate using Ollama.
        generated = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        # Step 6: Return generated text and source mapping.
        return {
            "question": processed_question,
            "summary": generated["content"],
            "model": generated["model"],
            "provider": generated["provider"],
            "retrieved_count": len(candidates),
            "evidence_count": len(evidence_package["sources"]),
            "sources": evidence_package["sources"],
            "human_review_required": True,
            "review_status": "PENDING_REVIEW",
        }