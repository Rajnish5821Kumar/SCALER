"""
Evaluation service — async log_query function
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


async def log_query(
    session_id: str,
    query: str,
    answer: str,
    latency_ms: float,
    grounded: bool,
    sources: List[Dict],
):
    """Log a query + answer to Supabase for evaluation tracking."""
    try:
        # TODO: Replace with actual Supabase client
        # from supabase import create_client
        # client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        # client.table("evaluation_logs").insert({
        #     "session_id": session_id,
        #     "query": query,
        #     "answer": answer,
        #     "latency_ms": latency_ms,
        #     "grounded": grounded,
        #     "sources": sources,
        # }).execute()

        logger.info(
            f"[EVAL] session={session_id[:8]} | "
            f"latency={latency_ms:.0f}ms | "
            f"grounded={grounded} | "
            f"sources={len(sources)}"
        )
    except Exception as e:
        logger.warning(f"Failed to log query to Supabase: {e}")
