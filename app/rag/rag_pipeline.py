from app.rag.query_processor import QueryProcessor
from app.rag.reranker import MedicalReranker
from app.rag.context_builder import ContextBuilder
from app.retrieval.retrieval_service import RetrievalService


class MedicalRAGPipeline:

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.retrieval_service = RetrievalService()
        self.reranker = MedicalReranker()
        self.context_builder = ContextBuilder(
            max_tokens=3000
        )

    def run(
        self,
        query: str,
        project_id: str,
        retrieval_limit: int = 15,
        final_limit: int = 5,
    ) -> dict:

        processed_query = self.query_processor.process(query)

        # Stage 1: Retrieve candidate evidence.
        candidates = self.retrieval_service.retrieve(
            query=processed_query,
            project_id=project_id,
            limit=retrieval_limit,
        )

        # Stage 2: Rerank candidates.
        ranked_evidence = self.reranker.rerank(
            query=processed_query,
            evidence=candidates,
            top_k=final_limit,
        )

        # Stage 3: Build context and citations.
        context_package = self.context_builder.build(
            ranked_evidence
        )

        return {
            "query": processed_query,
            "retrieved_count": len(candidates),
            "reranked_count": len(ranked_evidence),
            "evidence_count": len(context_package["sources"]),
            "context": context_package["context"],
            "sources": context_package["sources"],
            "context_tokens": context_package["total_tokens"],
        }