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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

    try {
      const history = messages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.role, content: m.content }))

      const res = await fetch(`${API_URL}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          history,
        }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      if (!sessionId) setSessionId(data.session_id)

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        latency_ms: data.latency_ms,
        timestamp: Date.now(),
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "⚠️ Sorry, I'm having trouble connecting right now. Please try again.",
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, errorMsg])
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
