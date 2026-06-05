# AI Persona — 7-Day Implementation Roadmap
# Rajnish Kumar | Scaler AI Engineer Screening Assignment

---

## 🗓️ Day-by-Day Plan

---

## Day 1 — Foundation & Data Preparation

### Goals
- Set up project skeleton
- Prepare all data sources (resume, GitHub)
- Initialize vector database

### Tasks
- [x] Create project folder structure
- [x] Write `RESUME_STRUCTURED` Python dict with all resume data
- [x] Set up Pinecone account + create index (dimension: 3072, metric: cosine)
- [x] Set up Supabase project + run schema SQL
- [x] Create `.env` with all API keys
- [x] Write `resume_loader.py` — chunk + embed + upsert resume data
- [x] Write `github_loader.py` — fetch repos + READMEs + upsert
- [x] Run initial ingestion: `python resume_loader.py && python github_loader.py`
- [x] Verify vectors in Pinecone dashboard

### Deliverable
- Pinecone index populated with ~847 vectors
- Resume + GitHub data ingested

---

## Day 2 — FastAPI Backend (Core)

### Goals
- Build the core API with RAG retrieval working end-to-end

### Tasks
- [x] `main.py` — FastAPI app with middleware + lifespan
- [x] `config.py` — Pydantic settings
- [x] `rag_service.py` — embed → retrieve → rerank pipeline
- [x] `system_prompt.py` — persona prompt builder
- [x] `hallucination_guard.py` — multi-layer detection
- [x] `routers/chat.py` — `/api/v1/chat/message` + streaming
- [x] Test locally: `uvicorn main:app --reload`
- [x] Validate with 5 test questions via Swagger UI

### Deliverable
- `POST /api/v1/chat/message` working with grounded answers

---

## Day 3 — Calendar Integration

### Goals
- Full interview booking flow via Google Calendar

### Tasks
- [ ] Set up Google Cloud project + OAuth 2.0 credentials
- [ ] Enable Google Calendar API
- [x] `calendar_service.py` — free/busy + event creation
- [x] `routers/calendar_api.py` — `/book`, `/slots`, `/callback`
- [ ] Test OAuth flow locally
- [ ] Create a test booking event on real Google Calendar
- [ ] Verify email invites sent to both parties
- [ ] Add Cal.com as fallback

### Deliverable
- Interview booking creates real Google Calendar events with Meet links

---

## Day 4 — Voice Agent (Vapi + ElevenLabs)

### Goals
- Working voice agent with <2s first response

### Tasks
- [ ] Create Vapi account + provision assistant
- [x] `voice_prompt.py` — optimized for speech (short sentences)
- [x] `routers/voice.py` — webhook handler + function call dispatch
- [ ] Configure ElevenLabs voice (clone from portfolio video if available)
- [ ] Configure Deepgram transcriber (Nova-2, en-IN language)
- [ ] Set up Vapi function tools: `book_interview`, `get_available_slots`
- [ ] Test call latency: STT→LLM→TTS round-trip
- [ ] Verify barge-in works correctly
- [ ] Deploy to Railway for public webhook URL

### Deliverable
- Voice agent live on Vapi with <2s first response

---

## Day 5 — Next.js Frontend

### Goals
- Production-grade chat UI and voice interface

### Tasks
- [x] `app/globals.css` — design system (dark glassmorphism)
- [x] `app/page.tsx` — animated landing page
- [x] `app/chat/page.tsx` — full chat interface with streaming
- [x] `app/voice/page.tsx` — voice call interface with Vapi SDK
- [ ] Connect frontend to deployed backend API
- [ ] Test streaming SSE in browser
- [ ] Add booking modal component
- [ ] Deploy to Vercel: `vercel --prod`

### Deliverable
- Frontend live on Vercel, fully connected to backend

---

## Day 6 — Evaluation & Testing

### Goals
- Measure all metrics, fix issues, optimize

### Tasks
- [x] `evaluation/evaluator.py` — full test suite
- [x] Recruiter test Q&A document (19 questions)
- [ ] Run evaluation: `python evaluation/evaluator.py`
- [ ] Measure latency P50/P95
- [ ] Check hallucination rate on all questions
- [ ] Verify injection defense on 5 adversarial inputs
- [ ] Tune system prompt to improve weak areas
- [ ] Check STT WER with Deepgram (record 5 test utterances)
- [ ] Optimize Pinecone query speed if >200ms
- [ ] Add Redis caching for repeated queries

### Deliverable
- All metrics at or above target thresholds

---

## Day 7 — Documentation & Submission

### Goals
- Polish everything for submission

### Tasks
- [x] `README.md` — complete with architecture diagram
- [x] `docs/evaluation_report.md` — metrics with charts
- [x] `docs/recruiter_test_questions.md` — 19 Q&A pairs
- [x] `docs/loom_video_script.md` — 4-minute demo script
- [ ] Record Loom demo (4 minutes)
- [ ] Take screenshots of all 3 interfaces
- [ ] Deploy final version to production
- [ ] Test production URLs
- [ ] Create GitHub repository + push all code
- [ ] Write submission email with all links

### Deliverable
- Complete submission with: GitHub repo, Loom video, live demo links, evaluation report

---

## 📊 Final Checklist Before Submission

### System Functionality
- [ ] Chat answers in < 2 seconds
- [ ] RAG returns grounded, cited answers
- [ ] Hallucination guard blocks bad answers
- [ ] Voice agent works with barge-in
- [ ] Calendar booking creates real events
- [ ] Adversarial prompts are blocked

### Documentation
- [x] README with architecture diagram
- [x] API documentation (Swagger at /docs)
- [x] Evaluation report with metrics
- [x] Recruiter Q&A test set
- [x] Deployment instructions

### Deployment
- [ ] Frontend: Vercel ✓
- [ ] Backend: Railway ✓
- [ ] Vector DB: Pinecone ✓
- [ ] Database: Supabase ✓
- [ ] Cache: Redis (Railway) ✓

### Submission
- [ ] GitHub repository public
- [ ] Loom video recorded and shared
- [ ] All environment variables documented in .env.example
- [ ] No API keys committed to Git

---

## ⚡ Quick Reference Commands

```bash
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Ingest data
cd rag_service/ingestion && python resume_loader.py && python github_loader.py

# Frontend
cd frontend && npm run dev

# Evaluation
cd evaluation && python evaluator.py

# Docker everything
docker-compose up --build

# Deploy
vercel --prod          # Frontend
railway up             # Backend
```
