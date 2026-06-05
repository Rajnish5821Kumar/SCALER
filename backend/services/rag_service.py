"""
RAG Service — Core Retrieval-Augmented Generation
Handles: Retrieval, Reranking, Context Building
"""

import asyncio
import os
import logging
from typing import List, Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class RagService:
    """
    Production RAG pipeline:
    1. Query → Dense Embedding (text-embedding-3-large)
    2. Pinecone ANN search (top_k=10)
    3. Cohere Reranker (top_n=3)
    4. Context assembly with citations
    """

    def __init__(self):
        self.pinecone_client = None
        self.embed_client = None
        self.reranker = None
        self._initialized = False

    async def initialize(self):
        """Lazy init — called on app startup."""
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info("✅ Pinecone connected")
        except Exception as e:
            logger.warning(f"Pinecone not configured: {e}. Running in mock mode.")
            self.index = None

        try:
            from openai import AsyncOpenAI
            self.embed_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.warning(f"OpenAI not configured: {e}")
            self.embed_client = None

        self._initialized = True
        logger.info("✅ RAG Service initialized")

    async def embed_query(self, text: str) -> List[float]:
        """Generate dense embedding for a query string."""
        if not self.embed_client:
            # Return mock vector for demo mode
            return [0.0] * 3072
        resp = await self.embed_client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return resp.data[0].embedding

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        rerank: bool = True,
        filter: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Full retrieval pipeline:
        Query → Embed → ANN Search → Rerank → Return docs
        Falls back to built-in resume data if Pinecone not configured.
        """
        # If Pinecone not configured, use built-in resume fallback
        if not self.index:
            return self._fallback_retrieve(query, top_k)

        # 1. Embed query
        query_vector = await self.embed_query(query)

        # 2. Pinecone search
        search_kwargs = {
            "vector": query_vector,
            "top_k": top_k * 2 if rerank else top_k,
            "include_metadata": True,
        }
        if filter:
            search_kwargs["filter"] = filter

        results = self.index.query(**search_kwargs)

        # 3. Format docs
        docs = []
        for match in results.matches:
            docs.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "metadata": {
                    "source": match.metadata.get("source", "unknown"),
                    "doc_type": match.metadata.get("doc_type", "resume"),
                    "section": match.metadata.get("section", ""),
                    "url": match.metadata.get("url", ""),
                },
            })

        # 4. Rerank with Cohere (optional)
        if rerank and len(docs) > 0:
            docs = await self._rerank(query, docs, top_n=top_k)

        return docs[:top_k]

    def _fallback_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Built-in fallback using Rajnish's resume data.
        Used when Pinecone is not configured (demo/dev mode).
        """
        from rag_service.ingestion.resume_loader import RESUME_STRUCTURED, chunk_resume
        chunks = chunk_resume(RESUME_STRUCTURED)
        query_lower = query.lower()
        # Simple keyword scoring
        scored = []
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            score = sum(1 for word in query_lower.split() if word in text_lower)
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, chunk in scored[:top_k]:
            results.append({
                "id": chunk["metadata"]["section"],
                "score": float(score) / 10,
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            })
        return results

    async def _rerank(
        self, query: str, docs: List[Dict], top_n: int = 3
    ) -> List[Dict]:
        """
        Rerank using Cohere rerank-english-v3.0.
        Falls back to score-based sorting if Cohere unavailable.
        """
        try:
            import cohere
            co = cohere.Client(api_key=settings.COHERE_API_KEY)
            texts = [d["text"] for d in docs]
            rerank_result = co.rerank(
                query=query,
                documents=texts,
                model="rerank-english-v3.0",
                top_n=top_n,
            )
            reranked = []
            for r in rerank_result.results:
                doc = docs[r.index].copy()
                doc["rerank_score"] = r.relevance_score
                reranked.append(doc)
            return reranked
        except Exception as e:
            logger.warning(f"Reranker unavailable, using score order: {e}")
            return sorted(docs, key=lambda x: x["score"], reverse=True)[:top_n]

    def build_context_string(self, docs: List[Dict]) -> str:
        """Format retrieved docs into context block for the prompt."""
        parts = []
        for i, doc in enumerate(docs, 1):
            meta = doc.get("metadata", {})
            source = meta.get("source", "resume")
            section = meta.get("section", "")
            url = meta.get("url", "")

            header = f"[SOURCE {i}: {source.upper()}"
            if section:
                header += f" — {section}"
            if url:
                header += f" | {url}"
            header += "]"

            parts.append(f"{header}\n{doc['text']}\n")

        return "\n---\n".join(parts)
