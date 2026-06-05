'use client'
import Link from 'next/link'
import { useState } from 'react'
import styles from './page.module.css'

const QUICK_QUESTIONS = [
  "Tell me about your tech stack",
  "What projects have you built?",
  "What's your experience with AI/ML?",
  "Describe your E-Commerce project",
  "Can we schedule an interview?",
]

export default function HomePage() {
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null)

  const skills = [
    { name: 'React / Next.js', icon: '⚛️', color: '#61DAFB' },
    { name: 'Node.js', icon: '🟢', color: '#68A063' },
    { name: 'Python / FastAPI', icon: '🐍', color: '#3776AB' },
    { name: 'Machine Learning', icon: '🧠', color: '#FF6B6B' },
    { name: 'React Native', icon: '📱', color: '#61DAFB' },
    { name: 'MongoDB', icon: '🍃', color: '#47A248' },
    { name: 'TypeScript', icon: '🔷', color: '#3178C6' },
    { name: 'Docker', icon: '🐳', color: '#2496ED' },
  ]

  return (
    <main className={styles.main}>
      {/* Background */}
      <div className={styles.bgGradient} />
      <div className={styles.bgGrid} />

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          AI Persona · Live
        </div>

        <h1 className={styles.heroTitle}>
          Hi, I'm{' '}
          <span className={styles.gradientText}>Rajnish Kumar</span>
        </h1>
        <p className={styles.heroSub}>
          Full-Stack & AI Engineer · MERN · Next.js · FastAPI · ML/DL
        </p>
        <p className={styles.heroDesc}>
          Ask my AI Persona anything about my projects, skills, or experience.
          Or jump on a voice call — it'll feel like you're talking to me directly.
        </p>

        <div className={styles.heroCta}>
          <Link href="/chat" className={styles.btnPrimary}>
            💬 Chat with my AI
          </Link>
          <Link href="/voice" className={styles.btnGhost}>
            🎙️ Voice Call
          </Link>
          <a
            href="https://github.com/Rajnish5821Kumar"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.btnGhost}
          >
            💻 GitHub
          </a>
        </div>

        {/* Quick Questions */}
        <div className={styles.quickQuestions}>
          <p className={styles.quickLabel}>Try asking:</p>
          <div className={styles.quickChips}>
            {QUICK_QUESTIONS.map((q) => (
              <Link key={q} href={`/chat?q=${encodeURIComponent(q)}`} className={styles.chip}>
                {q}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Skills Grid */}
      <section className={styles.skillsSection}>
        <h2 className={styles.sectionTitle}>Tech Stack</h2>
        <div className={styles.skillsGrid}>
          {skills.map((skill) => (
            <div
              key={skill.name}
              className={styles.skillCard}
              onMouseEnter={() => setHoveredSkill(skill.name)}
              onMouseLeave={() => setHoveredSkill(null)}
              style={{
                borderColor: hoveredSkill === skill.name ? skill.color + '60' : undefined,
                boxShadow: hoveredSkill === skill.name ? `0 0 20px ${skill.color}30` : undefined,
              }}
            >
              <span className={styles.skillIcon}>{skill.icon}</span>
              <span className={styles.skillName}>{skill.name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className={styles.statsSection}>
        {[
          { label: 'Projects Built', value: '6+' },
          { label: 'Tech Stack Items', value: '15+' },
          { label: 'Response Latency', value: '<2s' },
          { label: 'RAG Precision', value: '88%' },
        ].map((stat) => (
          <div key={stat.label} className={styles.statCard}>
            <div className={styles.statValue}>{stat.value}</div>
            <div className={styles.statLabel}>{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <p>
          Built by Rajnish Kumar ·{' '}
          <a href="mailto:rk2452003@gmail.com">rk2452003@gmail.com</a> ·{' '}
          <a href="https://www.linkedin.com/in/rajnish-kumar-5b480a255/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        </p>
      </footer>
    </main>
  )
}
