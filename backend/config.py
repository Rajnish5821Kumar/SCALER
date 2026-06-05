"""
Configuration & Environment Settings
All fields optional with defaults — server starts even without .env
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "rajnish-persona"
    PINECONE_ENVIRONMENT: str = "gcp-starter"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_USERNAME: str = "Rajnish5821Kumar"

    # Vapi
    VAPI_API_KEY: str = ""
    VAPI_PHONE_NUMBER_ID: str = ""

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Deepgram
    DEEPGRAM_API_KEY: str = ""

    # Google Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/calendar/callback"
    GOOGLE_CALENDAR_ID: str = "primary"
    GOOGLE_CALENDAR_EMAIL: str = "rk2452003@gmail.com"

    # Cal.com
    CALCOM_API_KEY: str = ""

    # Cohere (reranker)
    COHERE_API_KEY: str = ""

    # App
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://portfolio-website-jet-delta-77.vercel.app"]
    SECRET_KEY: str = "dev-secret-key"
    DEBUG: bool = True

    # RAG
    TOP_K_RETRIEVAL: int = 5
    RERANK_TOP_N: int = 3
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

