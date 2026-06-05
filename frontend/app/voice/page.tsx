'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import styles from './voice.module.css'

declare global {
  interface Window {
    Vapi: any
  }
}

type CallStatus = 'idle' | 'connecting' | 'active' | 'ended'

export default function VoicePage() {
  const [status, setStatus] = useState<CallStatus>('idle')
  const [transcript, setTranscript] = useState<Array<{ role: string; text: string }>>([])
  const [vapi, setVapi] = useState<any>(null)
  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    // Dynamically load Vapi SDK
    const init = async () => {
      try {
        const { default: Vapi } = await import('@vapi-ai/web')
        const vapiInstance = new Vapi(process.env.NEXT_PUBLIC_VAPI_API_KEY || '')

        vapiInstance.on('call-start', () => setStatus('active'))
        vapiInstance.on('call-end', () => setStatus('ended'))
        vapiInstance.on('speech-start', () => {})
        vapiInstance.on('speech-end', () => {})

        vapiInstance.on('message', (msg: any) => {
          if (msg.type === 'transcript' && msg.transcriptType === 'final') {
            setTranscript((prev) => [...prev, { role: msg.role, text: msg.transcript }])
          }
        })

        vapiInstance.on('error', (err: any) => {
          console.error('Vapi error:', err)
          setStatus('ended')
        })

        setVapi(vapiInstance)
      } catch (err) {
        console.log('Vapi SDK not available in demo mode')
      }
    }

    init()
  }, [])

  const startCall = async () => {
    if (!vapi) {
      // Demo mode — simulate a call
      setStatus('active')
      setTranscript([
        { role: 'assistant', text: "Hi there! I'm Rajnish Kumar's AI assistant. What would you like to know about my background?" }
      ])
      return
    }

    setStatus('connecting')
    setTranscript([])

    try {
      await vapi.start({
        name: "Rajnish Kumar AI Persona",
        firstMessage: "Hi there! I'm Rajnish Kumar's AI assistant. What would you like to know about my background, projects, or skills?",
        model: {
          provider: "openai",
          model: "gpt-4o",
          temperature: 0.2,
          systemPrompt: "You are Rajnish Kumar's AI voice assistant. Keep responses concise and conversational. You can help book interviews too.",
          maxTokens: 200,
        },
        voice: {
          provider: "elevenlabs",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
        transcriber: {
          provider: "deepgram",
          model: "nova-2",
          language: "en",
        },
      })
    } catch (err) {
      console.error('Failed to start call:', err)
      setStatus('idle')
    }
  }

  const endCall = () => {
    vapi?.stop()
    setStatus('ended')
  }

  const toggleMute = () => {
    if (vapi) {
      vapi.setMuted(!isMuted)
      setIsMuted(!isMuted)
    }
  }

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
          Powered by Vapi + ElevenLabs + Deepgram · First response &lt;2s · Barge-in supported
        </p>

        {/* Voice Visualizer */}
        <div className={styles.visualizer}>
          <div className={`${styles.orb} ${status === 'active' ? styles.orbActive : ''}`}>
            <div className={styles.orbInner}>
              {status === 'idle' && <span className={styles.orbIcon}>🎙️</span>}
              {status === 'connecting' && <span className={styles.orbIcon}>⏳</span>}
              {status === 'active' && (
                <div className={styles.waveBars}>
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className={styles.waveBar} />
                  ))}
                </div>
              )}
              {status === 'ended' && <span className={styles.orbIcon}>✅</span>}
            </div>
          </div>

          <p className={styles.statusText}>
            {status === 'idle' && 'Ready to connect'}
            {status === 'connecting' && 'Connecting...'}
            {status === 'active' && 'Call active — speak naturally'}
            {status === 'ended' && 'Call ended'}
          </p>
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          {status === 'idle' && (
            <button className={styles.startBtn} onClick={startCall} id="start-voice-call">
              Start Voice Call
            </button>
          )}
          {status === 'connecting' && (
            <button className={styles.startBtn} disabled>
              Connecting...
            </button>
          )}
          {status === 'active' && (
            <>
              <button className={styles.muteBtn} onClick={toggleMute} id="mute-btn">
                {isMuted ? '🔇 Unmute' : '🎙️ Mute'}
              </button>
              <button className={styles.endBtn} onClick={endCall} id="end-call-btn">
                End Call
              </button>
            </>
          )}
          {status === 'ended' && (
            <button className={styles.startBtn} onClick={() => { setStatus('idle'); setTranscript([]) }}>
              Start New Call
            </button>
          )}
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className={styles.transcript}>
            <h3 className={styles.transcriptTitle}>Live Transcript</h3>
            {transcript.map((t, i) => (
              <div key={i} className={`${styles.transcriptLine} ${t.role === 'user' ? styles.userLine : styles.aiLine}`}>
                <span className={styles.transcriptRole}>{t.role === 'user' ? 'You' : 'Rajnish AI'}</span>
                <span className={styles.transcriptText}>{t.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Features */}
        <div className={styles.features}>
          {[
            { icon: '⚡', label: '<2s first response' },
            { icon: '🔄', label: 'Barge-in supported' },
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
