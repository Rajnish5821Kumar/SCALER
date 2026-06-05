import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Rajnish Kumar — AI Persona | Full-Stack & AI Engineer',
  description:
    'Chat with Rajnish Kumar\'s AI Persona. Get instant answers about his skills, projects, GitHub repos, and book an interview. Built with RAG + GPT-4o.',
  keywords: 'Rajnish Kumar, AI Engineer, Full-Stack Developer, MERN, Next.js, FastAPI, Machine Learning',
  openGraph: {
    title: 'Rajnish Kumar — AI Persona',
    description: 'Interact with an AI version of Rajnish Kumar. Ask about his skills, projects, and experience.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
