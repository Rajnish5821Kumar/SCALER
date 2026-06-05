"""
Retrieval Router — RAG Search & Context API
POST /api/v1/retrieval/search
POST /api/v1/retrieval/ingest
GET  /api/v1/retrieval/stats
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    rerank: bool = True
    filter_source: Optional[str] = None  # "resume" | "github" | "portfolio"


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    source: str
    section: str
    url: Optional[str]


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
    latency_ms: float


class IngestRequest(BaseModel):
    source: str  # "resume" | "github" | "portfolio"
    force_refresh: bool = False


async def get_rag(request: Request):
    return request.app.state.rag


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest, rag=Depends(get_rag)):
    """
    Search the vector DB for relevant context chunks.
    Useful for debugging what the RAG pipeline retrieves.
    """
    import time
    start = time.time()

    filter_dict = None
    if req.filter_source:
        filter_dict = {"doc_type": {"$eq": req.filter_source}}

    try:
        docs = await rag.retrieve(
            query=req.query,
            top_k=req.top_k,
            rerank=req.rerank,
            filter=filter_dict,
        )

        results = [
            SearchResult(
                id=d["id"],
                text=d["text"],
                score=d.get("rerank_score", d["score"]),
                source=d["metadata"].get("source", "unknown"),
                section=d["metadata"].get("section", ""),
                url=d["metadata"].get("url"),
            )
            for d in docs
        ]

        return SearchResponse(
            query=req.query,
            results=results,
            total_found=len(results),
            latency_ms=round((time.time() - start) * 1000, 2),
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def trigger_ingestion(req: IngestRequest):
    """
    Trigger document ingestion pipeline.
    Re-processes source data and updates Pinecone index.
    """
    import asyncio

    async def run_ingestion(source: str):
        if source == "resume":
            from rag_service.ingestion.resume_loader import ResumeLoader
            loader = ResumeLoader()
            await loader.run()
        elif source == "github":
            from rag_service.ingestion.github_loader import GitHubLoader
            loader = GitHubLoader()
            await loader.run()
        elif source == "portfolio":
            from rag_service.ingestion.portfolio_loader import PortfolioLoader
            loader = PortfolioLoader()
            await loader.run()
        elif source == "all":
            pass  # Trigger all

    # Run in background
    asyncio.create_task(run_ingestion(req.source))

    return {
        "status": "ingestion_started",
        "source": req.source,
        "message": f"Ingestion started for {req.source}. Check /stats for progress.",
    }


@router.get("/stats")
async def get_index_stats():
    """Return Pinecone index statistics."""
    try:
        from pinecone import Pinecone
        from config import settings
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness,
            "namespaces": dict(stats.namespaces),
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
