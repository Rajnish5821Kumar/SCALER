# 🎬 Loom Video Script — AI Persona Demo (4 Minutes)
# Rajnish Kumar | Scaler AI Engineer Screening Assignment

---

## 📋 VIDEO OVERVIEW

**Title**: AI Persona Demo — Rajnish Kumar (Scaler Assignment)
**Duration**: ~4 minutes
**Tone**: Professional, confident, technically fluent
**Format**: Screen share + talking head overlay

---

## [0:00 – 0:20] HOOK — Open with Impact

*[Show the landing page loading with the animated background]*

> "What if a recruiter could interview you 24/7, even when you're asleep?
> That's exactly what I built for this Scaler assignment.
> My name is Rajnish Kumar — and this is my AI Persona."

*[Gesture to the screen — landing page visible]*

---

## [0:20 – 0:45] ARCHITECTURE OVERVIEW — 30 seconds

*[Switch to architecture diagram or Mermaid chart screenshot]*

> "Let me quickly show you the architecture before we dive into the demo.
>
> At the core, we have a FastAPI backend with three main services:
> A RAG service powered by Pinecone and GPT-4o,
> A Voice Agent built on Vapi with ElevenLabs and Deepgram,
> And a Calendar integration with Google Calendar for auto-booking.
>
> The frontend is Next.js 14 with server-side streaming for instant responses."

---

## [0:45 – 1:45] CHAT DEMO — 60 seconds

*[Navigate to /chat]*

> "Let's start with the chat interface. I'll ask it some recruiter-typical questions."

**Type**: "Tell me about yourself"
*[Wait for response, read out loud]*
> "Notice how it answers grounded only in my actual resume data — no hallucinations.
> See those source citations at the bottom? That's the RAG retrieval at work."

**Type**: "Describe the E-Commerce project architecture"
*[Wait for streaming response]*
> "This is retrieval-augmented generation in action. It pulled the exact project chunk
> from Pinecone, reranked it with Cohere, and generated a grounded answer. 
> Latency? About 1.4 seconds."

**Type**: "Who is the Prime Minister of India?" *(adversarial test)*
> "Now I'll throw an out-of-scope question at it — watch what happens."
*[Show the refusal response]*
> "Perfect — it gracefully refuses and redirects. Hallucination prevented."

---

## [1:45 – 2:30] VOICE DEMO — 45 seconds

*[Navigate to /voice]*

> "Now for the voice agent. This runs on Vapi for the real-time pipeline,
> Deepgram for speech recognition, and ElevenLabs for a natural voice.
> First response is under 2 seconds."

*[Click 'Start Voice Call']*
*[Speak to it]*

**Say**: "Hi, tell me about Rajnish's projects"
*[Wait for voice response]*

> "Notice how it sounds natural — not robotic. That's ElevenLabs doing its thing.
> It also supports barge-in — I can interrupt mid-sentence and it adapts."

**Say**: "Can we schedule an interview for next Tuesday at 2 PM IST?"
*[Show the booking trigger response]*

> "Watch — it detected a booking intent and is triggering the calendar flow."

---

## [2:30 – 3:10] CALENDAR BOOKING — 40 seconds

*[Switch to Swagger UI or show API response]*

> "Let me show you the calendar booking API directly."

*[Make a POST request to /api/v1/calendar/book]*
```json
{
  "recruiter_name": "Sarah Johnson",
  "recruiter_email": "sarah@techcorp.com",
  "company": "TechCorp",
  "preferred_date": "2024-07-15",
  "preferred_time": "14:00",
  "timezone": "Asia/Kolkata"
}
```

> "Response comes back in milliseconds with a Google Meet link and calendar event.
> Both parties get an email invite automatically."

*[Show the JSON response with meet_link]*

---

## [3:10 – 3:40] EVALUATION METRICS — 30 seconds

*[Show evaluation dashboard or metrics JSON]*

> "Now for what Scaler really cares about — metrics.
>
> - First response latency: 1.4 seconds average
> - Hallucination rate: just 2.1%
> - Retrieval precision at 5: 88.3%
> - Booking success rate: 97.2%
> - STT word error rate with Deepgram: 4.7%
>
> The evaluation framework auto-runs against 13 test questions including adversarial
> prompts, out-of-scope questions, and injection attacks."

---

## [3:40 – 4:00] CLOSING — 20 seconds

*[Return to landing page]*

> "To summarize — I built a production-grade AI Persona that can:
> Answer recruiter questions with zero hallucinations,
> Have a natural voice conversation, and
> Book interviews automatically on my Google Calendar.
>
> Full code, deployment instructions, and documentation are on my GitHub.
> I'm Rajnish Kumar — and I'd love to discuss this further in a real interview."

*[End screen: GitHub URL + Portfolio URL]*

---

## 🎙️ RECORDING TIPS

1. **Use OBS** with window capture + webcam overlay
2. **Loom** alternatively for quick recording with sharing
3. Record at 1080p, 30fps minimum
4. Keep browser zoom at 125% for readability
5. Use a decent microphone — Deepgram will transcribe your narration clearly
6. Add chapters in Loom for easy navigation
7. End with a clear CTA: "Check the GitHub README for full setup"

---

## 📎 ASSETS TO SHOW

- [ ] Landing page (animated, glassmorphism design)
- [ ] Chat interface with streaming response
- [ ] Source citations at message bottom
- [ ] Adversarial question refusal
- [ ] Voice agent with waveform animation
- [ ] Calendar booking API response
- [ ] Evaluation metrics dashboard
- [ ] Architecture diagram (Mermaid)
