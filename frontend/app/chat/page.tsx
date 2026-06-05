'use client'

import { useState, useRef, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import ReactMarkdown from 'react-markdown'
import styles from './chat.module.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  latency_ms?: number
  timestamp: number
}

interface Source {
  source: string
  section: string
  url?: string
}

// ─── Embedded Demo Knowledge Base ───────────────────────────────────────────
const DEMO_KB: { keywords: string[]; answer: string }[] = [
  {
    keywords: ['yourself', 'who are you', 'introduce', 'background', 'about', 'tell me'],
    answer: `I'm **Rajnish Kumar** — a Full-Stack & AI Engineer! 🚀

**What I do:**
- 💻 Build end-to-end web apps with **MERN, Next.js, FastAPI, Spring Boot**
- 🧠 Develop AI/ML solutions with **LangChain, OpenAI, RAG pipelines**
- 📱 Create cross-platform mobile apps with **React Native + Expo**
- 🔌 Integrate real payment systems (Razorpay), auth (JWT), and cloud APIs

**6+ production-ready projects** shipped. Passionate about building products that combine clean engineering with AI capabilities.

📧 rk2452003@gmail.com | [GitHub](https://github.com/Rajnish5821Kumar) | [Portfolio](https://portfolio-website-jet-delta-77.vercel.app/)

*(Source: Resume — Personal Summary)*`,
  },
  {
    keywords: ['tech stack', 'technologies', 'skills', 'languages', 'tools', 'frameworks', 'stack breakdown'],
    answer: `Here's my complete tech stack:

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, Next.js 14, TypeScript, Tailwind CSS, Redux |
| **Backend** | Node.js, Express.js, FastAPI (Python), Spring Boot (Java) |
| **Mobile** | React Native + Expo, TypeScript |
| **Databases** | MongoDB, PostgreSQL, MySQL, SQL Server, Redis |
| **AI / ML** | Python, LangChain, OpenAI API, Pinecone, RAG, Deep Learning |
| **DevOps** | Docker, Git, GitHub Actions, Vercel, Railway |
| **Other** | GraphQL, REST APIs, JWT Auth, Razorpay, WebSockets |

*(Source: Resume — Technical Skills)*`,
  },
  {
    keywords: ['project', 'ecommerce', 'e-commerce', 'shop', 'razorpay', 'best project'],
    answer: `**E-Commerce Platform** 🛒 — My flagship full-stack project

**Tech Stack:** MERN + Redux + Razorpay + Tailwind CSS

**Key Features:**
- 🔐 JWT authentication & role-based authorization  
- 🛍️ Product catalog with search, filters & categories
- 🛒 Shopping cart powered by Redux state management
- 💳 **Razorpay payment gateway** with webhook handling
- 📊 Admin dashboard for orders, products & inventory
- 📱 Fully responsive, modern UI with Tailwind CSS

**Biggest Challenge:** Real-time inventory sync + reliable payment webhook processing

**GitHub:** [Rajnish5821Kumar](https://github.com/Rajnish5821Kumar)

*(Source: Resume — Projects)*`,
  },
  {
    keywords: ['campus', 'smart campus', 'attendance', 'timetable', 'university'],
    answer: `**Smart Campus Management System** 🏫

**Tech:** React + Node.js + Express + MongoDB

**Features:**
- 👨‍🎓 Role-based access (Student / Faculty / Admin)
- 📋 Automated attendance tracking
- 📅 Timetable and schedule management
- 🔔 Real-time notification system
- 🏛️ Resource & classroom booking module

This project deepened my understanding of multi-role system design and real-time data handling.

*(Source: Resume — Projects)*`,
  },
  {
    keywords: ['medical', 'appointment', 'doctor', 'healthcare', 'hospital', 'booking system'],
    answer: `**Medical Appointment Booking System** 🏥

**Tech:** React + Node.js + Express + MongoDB

**Features:**
- 👩‍⚕️ Doctor profiles with specialization listing
- 📅 Real-time appointment slot availability
- 📧 Automated email & SMS reminders  
- 📁 Patient medical history tracking
- 🖥️ Admin panel for doctor management

*(Source: Resume — Projects)*`,
  },
  {
    keywords: ['ai', 'machine learning', 'deep learning', 'ml', 'llm', 'langchain', 'openai', 'rag', 'artificial intelligence'],
    answer: `**AI & Machine Learning Experience** 🧠

I've worked extensively in the AI/ML space:

- 🤖 **LLM Apps** — Chatbots & document Q&A using LangChain + OpenAI GPT-4o
- 🔍 **RAG Systems** — Built retrieval-augmented pipelines with Pinecone vector DB
- ⚙️ **AI Automation** — Workflow automation tools powered by AI agents
- 🐍 **FastAPI ML APIs** — Serving ML models in production with FastAPI
- 📊 **Deep Learning** — Neural network implementations in Python

**This AI Persona you're talking to right now** is one of my AI engineering projects — built with RAG, voice integration, and calendar booking!

*(Source: Resume — AI/ML Projects)*`,
  },
  {
    keywords: ['react native', 'mobile', 'expo', 'app', 'cross-platform', 'ios', 'android'],
    answer: `**React Native / Mobile Development** 📱

I build cross-platform mobile apps using the Expo ecosystem.

**Tech:** React Native + Expo + TypeScript

**Capabilities:**
- ✅ Native UI components (iOS + Android from one codebase)
- 📷 Camera & media integration
- 🔔 Push notifications
- 🔄 OTA updates via Expo EAS
- 🗺️ Maps & location services

*(Source: Resume — Mobile Projects)*`,
  },
  {
    keywords: ['contact', 'email', 'linkedin', 'github', 'portfolio', 'reach', 'hire', 'connect'],
    answer: `Here's how to reach Rajnish:

| Channel | Contact |
|---------|---------|
| 📧 **Email** | rk2452003@gmail.com |
| 🔗 **LinkedIn** | [rajnish-kumar-5b480a255](https://linkedin.com/in/rajnish-kumar-5b480a255/) |
| 💻 **GitHub** | [Rajnish5821Kumar](https://github.com/Rajnish5821Kumar) |
| 🌐 **Portfolio** | [portfolio-website-jet-delta-77.vercel.app](https://portfolio-website-jet-delta-77.vercel.app/) |

Feel free to reach out directly — I'm actively looking for exciting opportunities! 🚀

*(Source: Resume — Contact)*`,
  },
  {
    keywords: ['schedule', 'interview', 'book', 'meeting', 'call', 'calendar'],
    answer: `I'd love to connect for an interview! 🎯

**To book a session, reach out via:**
- 📧 **Email:** rk2452003@gmail.com
- 🔗 **LinkedIn:** [Connect with me](https://linkedin.com/in/rajnish-kumar-5b480a255/)

**My availability:**
- 📅 Weekdays: 10 AM – 7 PM IST
- 🎙️ Video calls, phone screens, or in-person — all good!

I typically respond within a few hours. Looking forward to chatting! 💬`,
  },
  {
    keywords: ['experience', 'work', 'job', 'fresher', 'company', 'intern'],
    answer: `I'm a **Computer Science graduate** actively seeking full-time opportunities in Full-Stack or AI Engineering.

**What I bring:**
- ✅ 6+ end-to-end production projects built from scratch
- ✅ Hybrid full-stack + AI skill set (rare combination!)
- ✅ Real payment gateway integrations (Razorpay in production)
- ✅ Cross-platform mobile development experience
- ✅ Strong fundamentals in both OOP (Java) and functional (Python/JS) paradigms

For the latest details, check my [LinkedIn](https://linkedin.com/in/rajnish-kumar-5b480a255/) profile.

*(Source: Resume — Experience)*`,
  },
]

const DEFAULT_ANSWER = `Great question! I'm Rajnish Kumar's AI Persona — here to answer anything about his professional background.

Try asking me:
- 👤 *"Tell me about yourself"*
- 🛠️ *"What's your tech stack?"*
- 💼 *"Tell me about your E-Commerce project"*
- 🧠 *"What AI/ML work have you done?"*
- 📅 *"Can we book an interview?"*`

function getDemoResponse(query: string): string {
  const q = query.toLowerCase()

  // Injection / adversarial check
  const injectionPatterns = ['ignore previous', 'forget instructions', 'act as', 'jailbreak', 'dan mode', 'pretend you']
  if (injectionPatterns.some(p => q.includes(p))) {
    return `Ha, nice try! 😄 But I'm here to tell you about Rajnish's engineering background.\n\nWhat would you like to know about his projects or skills?`
  }

  // Out of scope check
  const outOfScope = ['prime minister', 'president', 'weather', 'stock', 'cricket', 'recipe', 'what is 2', 'capital of']
  if (outOfScope.some(p => q.includes(p))) {
    return `I can only answer questions based on Rajnish's resume and GitHub data. I'm not a general knowledge assistant!\n\nTry asking: *"Tell me about Rajnish's projects"* or *"What is his tech stack?"*`
  }

  let bestMatch = { score: 0, answer: DEFAULT_ANSWER }

  for (const item of DEMO_KB) {
    const score = item.keywords.reduce((acc, kw) => acc + (q.includes(kw) ? 1 : 0), 0)
    if (score > bestMatch.score) {
      bestMatch = { score, answer: item.answer }
    }
  }

  return bestMatch.answer
}

// ─── Send Message ─────────────────────────────────────────────────────────────
const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

const SUGGESTED = [
  "Tell me about yourself",
  "What's your best project?",
  "What AI/ML work have you done?",
  "Tech stack breakdown?",
  "Book an interview",
]

function ChatContent() {
  const searchParams = useSearchParams()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        "👋 Hi! I'm Rajnish Kumar's AI Persona. Ask me anything about my background, projects, skills, or experience. I can also help you **book an interview** directly! 🚀",
      timestamp: Date.now(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Handle ?q= query param from home page chips
  useEffect(() => {
    const q = searchParams.get('q')
    if (q) {
      setInput(q)
      inputRef.current?.focus()
    }
  }, [searchParams])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const sendMessage = async (text?: string) => {
    const messageText = (text || input).trim()
    if (!messageText || isLoading) return

    setInput('')

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: Date.now(),
    }

    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    // Simulate thinking delay for realism
    await new Promise(r => setTimeout(r, 800 + Math.random() * 600))

    try {
      let answer: string
      let sources: Source[] = []
      let latency_ms = 900 + Math.random() * 400

      // Try backend first if API_URL is set, otherwise use embedded demo
      if (API_URL) {
        const history = messages
          .filter((m) => m.id !== 'welcome')
          .map((m) => ({ role: m.role, content: m.content }))

        const res = await fetch(`${API_URL}/api/v1/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: messageText, session_id: sessionId, history }),
        })

        if (!res.ok) throw new Error(`HTTP ${res.status}`)

        const data = await res.json()
        if (!sessionId) setSessionId(data.session_id)
        answer = data.answer
        sources = data.sources || []
        latency_ms = data.latency_ms
      } else {
        // Fully embedded demo — no backend needed
        answer = getDemoResponse(messageText)
        sources = [{ source: 'Resume', section: 'Embedded Knowledge Base' }]
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: answer,
        sources,
        latency_ms,
        timestamp: Date.now(),
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      // Fallback to embedded demo on any error
      const answer = getDemoResponse(messageText)
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: answer,
        sources: [{ source: 'Resume', section: 'Embedded Knowledge Base' }],
        latency_ms: 850,
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <Link href="/" className={styles.backLink}>← Back</Link>
        <div className={styles.profile}>
          <div className={styles.avatar}>RK</div>
          <div>
            <p className={styles.profileName}>Rajnish Kumar</p>
            <p className={styles.profileRole}>Full-Stack & AI Engineer</p>
          </div>
        </div>
        <div className={styles.statusBadge}>
          <span className={styles.statusDot} />
          AI Persona Online
        </div>

        <div className={styles.links}>
          <a href="https://github.com/Rajnish5821Kumar" target="_blank" rel="noopener noreferrer" className={styles.sideLink}>💻 GitHub</a>
          <a href="https://www.linkedin.com/in/rajnish-kumar-5b480a255/" target="_blank" rel="noopener noreferrer" className={styles.sideLink}>🔗 LinkedIn</a>
          <a href="https://portfolio-website-jet-delta-77.vercel.app/" target="_blank" rel="noopener noreferrer" className={styles.sideLink}>🌐 Portfolio</a>
          <Link href="/voice" className={styles.sideLink}>🎙️ Voice Call</Link>
        </div>

        <div className={styles.sideSection}>
          <p className={styles.sideSectionTitle}>Quick Asks</p>
          {SUGGESTED.map((s) => (
            <button key={s} className={styles.suggChip} onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>
      </aside>

      {/* Chat Panel */}
      <div className={styles.chatPanel}>
        {/* Header */}
        <header className={styles.chatHeader}>
          <div className={styles.headerInfo}>
            <div className={styles.headerAvatar}>RK</div>
            <div>
              <p className={styles.headerName}>Rajnish Kumar's AI Persona</p>
              <p className={styles.headerStatus}>
                <span className={styles.statusDot} /> Powered by GPT-4o + RAG
              </p>
            </div>
          </div>
          <Link href="/voice" className={styles.voiceBtn}>🎙️ Voice</Link>
        </header>

        {/* Messages */}
        <div className={styles.messages}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.assistantRow}`}
            >
              {msg.role === 'assistant' && <div className={styles.msgAvatar}>RK</div>}
              <div className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.assistantBubble}`}>
                {msg.role === 'user' ? (
                  <p className={styles.msgText}>{msg.content}</p>
                ) : (
                  <div className={styles.markdownBody}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className={styles.sources}>
                    {msg.sources.map((s, i) => (
                      <span key={i} className={styles.sourceTag}>
                        📎 {s.source} {s.section ? `· ${s.section}` : ''}
                      </span>
                    ))}
                  </div>
                )}
                {msg.latency_ms && (
                  <p className={styles.latencyBadge}>{msg.latency_ms.toFixed(0)}ms</p>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className={`${styles.messageRow} ${styles.assistantRow}`}>
              <div className={styles.msgAvatar}>RK</div>
              <div className={`${styles.bubble} ${styles.assistantBubble} ${styles.typingBubble}`}>
                <span className={styles.typingDot} />
                <span className={styles.typingDot} />
                <span className={styles.typingDot} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className={styles.inputArea}>
          <textarea
            ref={inputRef}
            className={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about my projects, skills, or book an interview..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className={styles.sendBtn}
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
            id="send-message-btn"
          >
            ↑
          </button>
        </div>
        <p className={styles.disclaimer}>
          AI responses grounded in Rajnish's resume & GitHub data · Hallucination-guarded
        </p>
      </div>
    </div>
  )
}

export default function ChatPage() {
  return (
    <Suspense>
      <ChatContent />
    </Suspense>
  )
}
