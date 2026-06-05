"""
Database Schema — Supabase PostgreSQL
Run this in Supabase SQL Editor to initialize the database
"""

SQL_SCHEMA = """
-- ══════════════════════════════════════════════════════════════
-- AI Persona Database Schema — Rajnish Kumar
-- Platform: Supabase (PostgreSQL 15)
-- ══════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ──────────────────────────────────────────────────────────────
-- 1. SESSIONS — Chat conversation tracking
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      TEXT UNIQUE NOT NULL,
    user_agent      TEXT,
    ip_address      TEXT,
    referrer        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ DEFAULT NOW(),
    total_messages  INTEGER DEFAULT 0,
    booking_intent  BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);

-- ──────────────────────────────────────────────────────────────
-- 2. MESSAGES — Individual chat messages
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      TEXT REFERENCES sessions(session_id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    retrieved_docs  JSONB DEFAULT '[]',
    grounded        BOOLEAN DEFAULT TRUE,
    latency_ms      NUMERIC(10, 2),
    token_count     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- ──────────────────────────────────────────────────────────────
-- 3. EVALUATION_LOGS — Query evaluation for metrics
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evaluation_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id          TEXT,
    query               TEXT NOT NULL,
    answer              TEXT,
    latency_ms          NUMERIC(10, 2),
    grounded            BOOLEAN DEFAULT TRUE,
    retrieved_chunks    INTEGER DEFAULT 0,
    sources             JSONB DEFAULT '[]',
    hallucination_score NUMERIC(4, 3) DEFAULT 0,
    context_relevance   NUMERIC(4, 3) DEFAULT 0,
    answer_faithfulness NUMERIC(4, 3) DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_eval_logs_created_at ON evaluation_logs(created_at DESC);
CREATE INDEX idx_eval_logs_grounded ON evaluation_logs(grounded);

-- ──────────────────────────────────────────────────────────────
-- 4. BOOKINGS — Interview bookings
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id      TEXT UNIQUE NOT NULL,
    session_id      TEXT,
    recruiter_name  TEXT NOT NULL,
    recruiter_email TEXT NOT NULL,
    company         TEXT NOT NULL,
    event_start     TIMESTAMPTZ NOT NULL,
    event_end       TIMESTAMPTZ NOT NULL,
    timezone        TEXT DEFAULT 'Asia/Kolkata',
    duration_min    INTEGER DEFAULT 30,
    meeting_type    TEXT DEFAULT 'video',
    calendar_link   TEXT,
    meet_link       TEXT,
    google_event_id TEXT,
    status          TEXT DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'rescheduled')),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bookings_email ON bookings(recruiter_email);
CREATE INDEX idx_bookings_event_start ON bookings(event_start);

-- ──────────────────────────────────────────────────────────────
-- 5. VOICE_CALLS — Vapi call logs
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS voice_calls (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vapi_call_id    TEXT UNIQUE,
    caller_phone    TEXT,
    duration_sec    INTEGER,
    transcript      JSONB DEFAULT '[]',
    booking_created BOOLEAN DEFAULT FALSE,
    stt_wer         NUMERIC(4, 3),
    first_resp_ms   NUMERIC(10, 2),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    ended_at        TIMESTAMPTZ
);

-- ──────────────────────────────────────────────────────────────
-- 6. DOCUMENT_INDEX — Track ingested documents
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_index (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,     -- 'resume' | 'github' | 'portfolio'
    doc_type        TEXT NOT NULL,
    section         TEXT,
    url             TEXT,
    chunk_hash      TEXT UNIQUE NOT NULL,
    pinecone_id     TEXT,
    char_count      INTEGER,
    token_count     INTEGER,
    ingested_at     TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_doc_index_source ON document_index(source);
CREATE INDEX idx_doc_index_chunk_hash ON document_index(chunk_hash);

-- ──────────────────────────────────────────────────────────────
-- VIEWS — Analytics
-- ──────────────────────────────────────────────────────────────

-- Daily metrics view
CREATE OR REPLACE VIEW daily_metrics AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS total_queries,
    AVG(latency_ms) AS avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency_ms,
    SUM(CASE WHEN grounded = FALSE THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) AS hallucination_rate,
    AVG(context_relevance) AS avg_context_relevance,
    AVG(answer_faithfulness) AS avg_faithfulness
FROM evaluation_logs
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Booking summary view
CREATE OR REPLACE VIEW booking_summary AS
SELECT
    COUNT(*) AS total_bookings,
    COUNT(DISTINCT recruiter_email) AS unique_recruiters,
    COUNT(DISTINCT company) AS unique_companies,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM bookings;
"""

if __name__ == "__main__":
    print("Copy the SQL_SCHEMA string above and run it in Supabase SQL Editor")
    print(SQL_SCHEMA)
