"""
Chat Router — Core Q&A over RAG
POST /api/v1/chat/message
POST /api/v1/chat/stream
GET  /api/v1/chat/history/{session_id}
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import json
import asyncio
import logging

from services.rag_service import RagService
from services.evaluation_service import log_query
from prompts.system_prompt import build_system_prompt
from prompts.hallucination_guard import HallucinationGuard

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Models ───────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []
    stream: bool = False


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[dict]
    latency_ms: float
    grounded: bool


class BookingIntent(BaseModel):
    detected: bool
    message: str


# ─── Dependency ───────────────────────────────────────────────────────────────
async def get_rag(request: Request) -> RagService:
    return request.app.state.rag


# ─── Routes ───────────────────────────────────────────────────────────────────
@router.post("/message", response_model=ChatResponse)
async def chat_message(req: ChatRequest, rag: RagService = Depends(get_rag)):
    """
    Main chat endpoint. Retrieves context from vector DB, calls GPT-4o,
    and returns grounded answer with citations.
    """
    import time
    start = time.time()

    session_id = req.session_id or str(uuid.uuid4())

    try:
        # 1. Retrieve relevant context
        context_docs = await rag.retrieve(
            query=req.message,
            top_k=5,
            rerank=True,
        )

        # 2. Build system prompt with retrieved context
        system_prompt = build_system_prompt(context_docs)

        # 3. Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in (req.history or [])[-6:]:  # last 3 turns
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": req.message})

        # 4. Call OpenAI — or use smart demo responder if no key configured
        if not settings.OPENAI_API_KEY:
            from services.demo_responder import get_demo_response
            answer = get_demo_response(req.message)
            grounded = True
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=800,
            )

            answer = response.choices[0].message.content

            # 5. Hallucination check
            guard = HallucinationGuard()
            grounded = await guard.check(answer, context_docs)

            if not grounded:
                answer = (
                    "I can only answer questions based on Rajnish's resume and GitHub data. "
                    "Could you rephrase your question or ask something specific about his background?"
                )


        latency_ms = (time.time() - start) * 1000

        # 6. Log for evaluation
        await log_query(
            session_id=session_id,
            query=req.message,
            answer=answer,
            latency_ms=latency_ms,
            grounded=grounded,
            sources=[d["metadata"] for d in context_docs],
        )

        return ChatResponse(
            session_id=session_id,
            answer=answer,
            sources=[d["metadata"] for d in context_docs[:3]],
            latency_ms=round(latency_ms, 2),
            grounded=grounded,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(req: ChatRequest, rag: RagService = Depends(get_rag)):
    """
    Streaming chat endpoint using SSE. Useful for real-time typewriter effect.
    """
    session_id = req.session_id or str(uuid.uuid4())

    context_docs = await rag.retrieve(query=req.message, top_k=5, rerank=True)
    system_prompt = build_system_prompt(context_docs)

    messages = [{"role": "system", "content": system_prompt}]
    for msg in (req.history or [])[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    async def event_generator():
        from openai import AsyncOpenAI
        from config import settings
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Send metadata first
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"

        # Send sources at end
        sources = [d["metadata"] for d in context_docs[:3]]
        yield f"data: {json.dumps({'type': 'done', 'sources': sources})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve conversation history for a session."""
    from services.session_service import get_session
    history = await get_session(session_id)
    return {"session_id": session_id, "history": history}
