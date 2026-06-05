"""
AI Persona Backend - FastAPI Application
Rajnish Kumar | Scaler AI Engineer Screening Assignment
"""

import sys
import os

# Add project root to path so rag_service module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from routers import chat, retrieval, calendar_api, voice, evaluation
from config import settings

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Persona backend starting up...")
    # Initialize Pinecone, Redis, etc.
    from services.rag_service import RagService
    app.state.rag = RagService()
    await app.state.rag.initialize()
    logger.info("✅ RAG service initialized")
    yield
    logger.info("🛑 Shutting down...")


# ─── App Factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Persona API — Rajnish Kumar",
    description="Production-grade AI Persona backend with RAG, Voice, and Calendar integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latency logging middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    logger.info(f"{request.method} {request.url.path} → {response.status_code} [{process_time:.0f}ms]")
    return response


# ─── Exception Handler ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(chat.router,       prefix="/api/v1/chat",       tags=["Chat"])
app.include_router(retrieval.router,  prefix="/api/v1/retrieval",  tags=["RAG Retrieval"])
app.include_router(calendar_api.router, prefix="/api/v1/calendar", tags=["Calendar"])
app.include_router(voice.router,      prefix="/api/v1/voice",      tags=["Voice Agent"])
app.include_router(evaluation.router, prefix="/api/v1/eval",       tags=["Evaluation"])


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Persona — Rajnish Kumar",
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Persona API for Rajnish Kumar",
        "docs": "/docs",
        "health": "/health",
    }
