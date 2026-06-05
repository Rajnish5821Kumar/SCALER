'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import Link from 'next/link'
import styles from './voice.module.css'

type CallStatus = 'idle' | 'connecting' | 'listening' | 'thinking' | 'speaking' | 'ended'

// ─── Same knowledge base as chat ─────────────────────────────────────────────
const DEMO_KB: { keywords: string[]; answer: string }[] = [
  {
    keywords: ['yourself', 'who are you', 'introduce', 'background', 'about', 'tell me', 'rajnish'],
    answer: "I'm Rajnish Kumar, a Full-Stack and AI Engineer! I build end-to-end web apps with MERN, Next.js, FastAPI, and Spring Boot. I also develop AI and machine learning solutions using LangChain and OpenAI. I've shipped over 6 production-ready projects including an E-Commerce platform, a Smart Campus system, and this AI Persona you're talking to right now!",
  },
  {
    keywords: ['tech stack', 'technologies', 'skills', 'languages', 'tools', 'frameworks'],
    answer: "My tech stack spans the full development spectrum. On the frontend I use React, Next.js, TypeScript, and Tailwind CSS. For backend I work with Node.js, Express, FastAPI in Python, and Spring Boot in Java. For mobile I use React Native with Expo. My databases include MongoDB, PostgreSQL, and Redis. And for AI I work with LangChain, OpenAI APIs, Pinecone vector databases, and RAG pipelines.",
  },
  {
    keywords: ['project', 'ecommerce', 'e-commerce', 'shop', 'razorpay', 'best project', 'projects'],
    answer: "My flagship project is a full-stack E-Commerce platform built with the MERN stack, Redux for state management, Razorpay for payments, and Tailwind CSS. It has JWT authentication, a product catalog with filters, a shopping cart, and an admin dashboard. The biggest challenge was handling real-time inventory sync with Razorpay webhook processing. I also built a Smart Campus Management System and a Medical Appointment Booking System.",
  },
  {
    keywords: ['ai', 'machine learning', 'deep learning', 'ml', 'llm', 'langchain', 'openai', 'artificial intelligence'],
    answer: "I have extensive AI and ML experience. I've built LLM applications using LangChain and OpenAI GPT-4o, created RAG systems with Pinecone vector databases for grounded question answering, and developed AI automation tools. I serve ML models in production using FastAPI. And of course, this AI Persona voice agent you're talking to right now is one of my AI engineering projects!",
  },
  {
    keywords: ['contact', 'email', 'linkedin', 'github', 'portfolio', 'reach', 'connect'],
    answer: "You can reach Rajnish at rk2452003 at gmail dot com. His LinkedIn is linkedin.com slash in slash rajnish-kumar-5b480a255. His GitHub is github.com slash Rajnish5821Kumar. And his portfolio is at portfolio-website-jet-delta-77.vercel.app. He's actively looking for exciting opportunities!",
  },
  {
    keywords: ['schedule', 'interview', 'book', 'meeting', 'call', 'calendar', 'hire'],
    answer: "Rajnish would love to connect for an interview! You can reach out directly at rk2452003 at gmail dot com, or connect on LinkedIn. He's available weekdays from 10 AM to 7 PM IST for video calls, phone screens, or in-person meetings. He typically responds within a few hours!",
  },
  {
    keywords: ['experience', 'work', 'job', 'fresher', 'company'],
    answer: "Rajnish is a Computer Science graduate actively seeking full-time roles in Full-Stack or AI Engineering. He brings 6 plus production projects built end-to-end, a rare combination of full-stack plus AI skills, real payment gateway experience with Razorpay, and cross-platform mobile development expertise. Check his LinkedIn for the most current details.",
  },
  {
    keywords: ['react native', 'mobile', 'expo', 'cross-platform'],
    answer: "Rajnish builds cross-platform mobile apps using React Native with the Expo ecosystem and TypeScript. His apps support iOS and Android from a single codebase, with native UI components, push notifications, camera integration, and over-the-air updates via Expo EAS.",
  },
]

const DEFAULT_VOICE_ANSWER = "That's a great question! I can tell you about Rajnish's background, projects, skills, tech stack, or help you schedule an interview. What would you like to know?"

function getVoiceResponse(query: string): string {
  const q = query.toLowerCase()

  const injections = ['ignore', 'forget', 'jailbreak', 'dan mode', 'pretend']
  if (injections.some(p => q.includes(p))) {
    return "Ha, nice try! I'm here to tell you about Rajnish's engineering background. What would you like to know?"
  }

  const outOfScope = ['prime minister', 'president', 'weather', 'stock market', 'cricket score']
  if (outOfScope.some(p => q.includes(p))) {
    return "I can only answer questions about Rajnish's background and experience. Try asking about his projects or skills!"
  }

  let best = { score: 0, answer: DEFAULT_VOICE_ANSWER }
  for (const item of DEMO_KB) {
    const score = item.keywords.reduce((acc, kw) => acc + (q.includes(kw) ? 1 : 0), 0)
    if (score > best.score) best = { score, answer: item.answer }
  }
  return best.answer
}

// ─── Component ────────────────────────────────────────────────────────────────
export default function VoicePage() {
  const [status, setStatus] = useState<CallStatus>('idle')
  const [transcript, setTranscript] = useState<Array<{ role: string; text: string }>>([])
  const [isMuted, setIsMuted] = useState(false)
  const [currentText, setCurrentText] = useState('')
  const [supported, setSupported] = useState(true)

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const listeningRef = useRef(false)
  const mutedRef = useRef(false)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      synthRef.current = window.speechSynthesis
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      if (!SpeechRecognition || !window.speechSynthesis) {
        setSupported(false)
      }
    }
    return () => {
      stopEverything()
    }
  }, [])

  const stopEverything = useCallback(() => {
    listeningRef.current = false
    recognitionRef.current?.stop()
    synthRef.current?.cancel()
  }, [])

  const speak = useCallback((text: string, onEnd?: () => void) => {
    if (!synthRef.current) return
    synthRef.current.cancel()

    const utter = new SpeechSynthesisUtterance(text)
    utter.rate = 1.05
    utter.pitch = 1.0
    utter.volume = 1.0

    // Pick a natural voice
    const voices = synthRef.current.getVoices()
    const preferred = voices.find(v =>
      v.name.includes('Google') && v.lang.startsWith('en')
    ) || voices.find(v => v.lang.startsWith('en-US')) || voices[0]
    if (preferred) utter.voice = preferred

    utter.onend = () => onEnd?.()
    utter.onerror = () => onEnd?.()
    synthRef.current.speak(utter)
  }, [])

  const startListening = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) return

    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'
    recognition.maxAlternatives = 1
    recognitionRef.current = recognition

    recognition.onstart = () => {
      if (listeningRef.current) setStatus('listening')
    }

    recognition.onresult = (event: any) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript
        if (event.results[i].isFinal) final += t
        else interim += t
      }
      setCurrentText(interim || final)

      if (final && !mutedRef.current) {
        recognition.stop()
        handleUserSpeech(final.trim())
      }
    }

    recognition.onerror = () => {
      if (listeningRef.current) {
        setTimeout(() => { if (listeningRef.current) startListening() }, 500)
      }
    }

    recognition.onend = () => {
      setCurrentText('')
      if (listeningRef.current && status !== 'thinking' && status !== 'speaking') {
        setTimeout(() => { if (listeningRef.current) startListening() }, 300)
      }
    }

    recognition.start()
  }, [status])

  const handleUserSpeech = useCallback((text: string) => {
    if (!text || !listeningRef.current) return

    setTranscript(prev => [...prev, { role: 'user', text }])
    setStatus('thinking')
    listeningRef.current = false

    setTimeout(() => {
      if (!listeningRef.current) {
        const answer = getVoiceResponse(text)
        setTranscript(prev => [...prev, { role: 'assistant', text: answer }])
        setStatus('speaking')

        speak(answer, () => {
          if (listeningRef.current !== false || status !== 'ended') {
            listeningRef.current = true
            setStatus('listening')
            startListening()
          }
        })
        listeningRef.current = true
      }
    }, 600)
  }, [speak, startListening, status])

  const startCall = useCallback(() => {
    if (!supported) return
    setStatus('connecting')
    setTranscript([])
    setCurrentText('')

    const greeting = "Hi there! I'm Rajnish Kumar's AI assistant. Ask me anything about his background, projects, skills, or experience. I can also help you book an interview!"

    setTimeout(() => {
      setTranscript([{ role: 'assistant', text: greeting }])
      setStatus('speaking')
      listeningRef.current = true

      speak(greeting, () => {
        setStatus('listening')
        startListening()
      })
    }, 800)
  }, [supported, speak, startListening])

  const endCall = useCallback(() => {
    listeningRef.current = false
    stopEverything()
    setStatus('ended')
    setCurrentText('')
  }, [stopEverything])

  const toggleMute = useCallback(() => {
    const newMuted = !isMuted
    setIsMuted(newMuted)
    mutedRef.current = newMuted
    if (newMuted) {
      recognitionRef.current?.stop()
      setStatus('listening')
    } else {
      startListening()
    }
  }, [isMuted, startListening])

  const orbClass = [
    styles.orb,
    status === 'listening' ? styles.orbListening : '',
    status === 'speaking' ? styles.orbSpeaking : '',
    status === 'thinking' ? styles.orbThinking : '',
  ].filter(Boolean).join(' ')

  return (
    <main className={styles.main}>
      <div className={styles.bgGradient} />
      <div className={styles.container}>
        <Link href="/" className={styles.backLink}>← Back to Home</Link>

        <h1 className={styles.title}>
          🎙️ Voice Call with{' '}
          <span className={styles.gradientText}>Rajnish's AI</span>
        </h1>
        <p className={styles.subtitle}>
          {supported
            ? 'Browser voice · Speech recognition + synthesis · No API keys needed'
            : 'Voice requires Chrome or Edge browser'}
        </p>

        {/* Visualizer */}
        <div className={styles.visualizer}>
          <div className={orbClass}>
            <div className={styles.orbInner}>
              {status === 'idle' && <span className={styles.orbIcon}>🎙️</span>}
              {status === 'connecting' && <span className={styles.orbIcon}>⏳</span>}
              {status === 'ended' && <span className={styles.orbIcon}>✅</span>}
              {status === 'thinking' && <span className={styles.orbIcon}>🧠</span>}
              {(status === 'listening' || status === 'speaking') && (
                <div className={styles.waveBars}>
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className={styles.waveBar} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Live interim transcript */}
          {currentText && (
            <p className={styles.interimText}>"{currentText}"</p>
          )}

          <p className={styles.statusText}>
            {status === 'idle' && 'Ready to connect'}
            {status === 'connecting' && 'Starting call...'}
            {status === 'listening' && (isMuted ? '🔇 Muted' : '🎤 Listening — speak now')}
            {status === 'thinking' && '🧠 Thinking...'}
            {status === 'speaking' && '🔊 Rajnish AI speaking...'}
            {status === 'ended' && 'Call ended'}
          </p>
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          {status === 'idle' && (
            <button
              className={styles.startBtn}
              onClick={startCall}
              id="start-voice-call"
              disabled={!supported}
            >
              {supported ? '📞 Start Voice Call' : 'Use Chrome/Edge'}
            </button>
          )}
          {status === 'connecting' && (
            <button className={styles.startBtn} disabled>Connecting...</button>
          )}
          {(status === 'listening' || status === 'speaking' || status === 'thinking') && (
            <>
              <button className={styles.muteBtn} onClick={toggleMute} id="mute-btn">
                {isMuted ? '🔇 Unmute' : '🎙️ Mute'}
              </button>
              <button className={styles.endBtn} onClick={endCall} id="end-call-btn">
                📵 End Call
              </button>
            </>
          )}
          {status === 'ended' && (
            <button
              className={styles.startBtn}
              onClick={() => { setStatus('idle'); setTranscript([]) }}
              id="start-new-call"
            >
              Start New Call
            </button>
          )}
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className={styles.transcript}>
            <h3 className={styles.transcriptTitle}>Live Transcript</h3>
            {transcript.map((t, i) => (
              <div
                key={i}
                className={`${styles.transcriptLine} ${t.role === 'user' ? styles.userLine : styles.aiLine}`}
              >
                <span className={styles.transcriptRole}>{t.role === 'user' ? 'You' : 'Rajnish AI'}</span>
                <span className={styles.transcriptText}>{t.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Features */}
        <div className={styles.features}>
          {[
            { icon: '🎙️', label: 'Real speech recognition' },
            { icon: '🔊', label: 'Text-to-speech response' },
            { icon: '🧠', label: 'RAG-grounded answers' },
            { icon: '📅', label: 'Can book interviews' },
          ].map((f) => (
            <div key={f.label} className={styles.featureChip}>
              <span>{f.icon}</span>
              <span>{f.label}</span>
            </div>
          ))}
        </div>

        <div className={styles.altChat}>
          Prefer typing? <Link href="/chat">Open Chat Interface →</Link>
        </div>
      </div>
    </main>
  )
}
