"""
Resume Loader — Ingests PDF resume into Pinecone
Chunks by section, adds rich metadata for citation
"""

import asyncio
import logging
import hashlib
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


# ─── Rajnish's Resume Data (Structured) ────────────────────────────────────────
RESUME_STRUCTURED = {
    "personal": {
        "name": "Rajnish Kumar",
        "email": "rk2452003@gmail.com",
        "linkedin": "https://www.linkedin.com/in/rajnish-kumar-5b480a255/",
        "github": "https://github.com/Rajnish5821Kumar",
        "portfolio": "https://portfolio-website-jet-delta-77.vercel.app/",
    },
    "summary": (
        "Passionate Full-Stack and AI Engineer with hands-on experience in MERN Stack, "
        "Next.js, FastAPI, Python, Machine Learning, and React Native. "
        "I build end-to-end web and mobile applications with a strong focus on clean code, "
        "scalable architecture, and AI integration. Enthusiastic about solving real-world "
        "problems with modern technology."
    ),
    "skills": {
        "frontend": ["React", "Next.js", "TypeScript", "React Native", "Expo", "Tailwind CSS", "Redux"],
        "backend": ["Node.js", "Express.js", "FastAPI", "Spring Boot", "GraphQL"],
        "languages": ["JavaScript", "TypeScript", "Python", "Java", "SQL"],
        "databases": ["MongoDB", "PostgreSQL", "MySQL", "SQL Server", "Redis"],
        "ai_ml": ["Machine Learning", "Deep Learning", "LLMs", "RAG", "LangChain", "OpenAI API"],
        "devops": ["Docker", "Git", "GitHub Actions", "Vercel", "Railway", "Render"],
        "tools": ["Razorpay", "Stripe", "JWT", "REST APIs", "Postman"],
    },
    "projects": [
        {
            "name": "E-Commerce Website",
            "tech": ["MERN Stack", "Redux", "Razorpay", "Tailwind CSS"],
            "description": (
                "Full-featured e-commerce platform with product catalog, cart management, "
                "user authentication with JWT, admin dashboard, and Razorpay payment gateway integration. "
                "Uses Redux for state management and MongoDB for product/order persistence."
            ),
            "features": [
                "User authentication & authorization (JWT)",
                "Product catalog with search and filters",
                "Shopping cart with Redux state management",
                "Razorpay payment gateway integration",
                "Admin dashboard for order/product management",
                "Responsive Tailwind CSS design",
            ],
            "challenges": "Implementing real-time inventory updates and payment webhook handling",
            "future": "Add recommendation engine using collaborative filtering",
        },
        {
            "name": "Smart Campus Management System",
            "tech": ["React", "Node.js", "MongoDB", "Express.js"],
            "description": (
                "Comprehensive campus management platform for students, faculty, and administrators. "
                "Features attendance tracking, timetable management, notifications, and resource booking."
            ),
            "features": [
                "Role-based access control (Student, Faculty, Admin)",
                "Automated attendance tracking",
                "Timetable and schedule management",
                "Resource booking system",
                "Real-time notifications",
            ],
        },
        {
            "name": "Medical Appointment Booking System",
            "tech": ["React", "Node.js", "MongoDB", "Express.js"],
            "description": (
                "Healthcare platform enabling patients to book doctor appointments, "
                "view medical history, and receive automated reminders."
            ),
            "features": [
                "Doctor profile and specialization listing",
                "Real-time appointment slot availability",
                "Automated email/SMS reminders",
                "Patient medical history tracking",
                "Admin panel for doctor management",
            ],
        },
        {
            "name": "Policy Clarification Portal",
            "tech": ["Flask", "SQL Server", "Python", "HTML/CSS"],
            "description": (
                "Enterprise portal for HR policy Q&A using NLP-based search. "
                "Employees can search and clarify company policies with structured SQL Server backend."
            ),
        },
        {
            "name": "AI Applications and Automation Projects",
            "tech": ["Python", "LangChain", "OpenAI", "FastAPI"],
            "description": (
                "Various AI automation projects including chatbots, document Q&A systems, "
                "and workflow automation tools built with LangChain and OpenAI APIs."
            ),
        },
        {
            "name": "Expo React Native Applications",
            "tech": ["React Native", "Expo", "TypeScript"],
            "description": (
                "Cross-platform mobile applications built with Expo and React Native. "
                "Features native UI components, camera integration, and push notifications."
            ),
        },
    ],
    "education": {
        "degree": "B.Tech / Bachelor's in Computer Science / Engineering",
        "note": "Check LinkedIn or portfolio for exact institution details",
    },
    "achievements": [
        "Built 6+ production-ready full-stack projects",
        "Proficient in both AI/ML and traditional full-stack development",
        "Experience with payment gateway integrations (Razorpay)",
        "Cross-platform mobile development with Expo/React Native",
    ],
}


def chunk_resume(resume: Dict, chunk_size: int = 512, overlap: int = 64) -> List[Dict]:
    """
    Convert structured resume into chunks with metadata.
    Uses semantic sectioning — keeps related content together.
    """
    chunks = []

    # Personal + Summary
    personal_text = (
        f"Name: {resume['personal']['name']}\n"
        f"Email: {resume['personal']['email']}\n"
        f"LinkedIn: {resume['personal']['linkedin']}\n"
        f"GitHub: {resume['personal']['github']}\n"
        f"Portfolio: {resume['personal']['portfolio']}\n\n"
        f"Summary: {resume['summary']}"
    )
    chunks.append({
        "text": personal_text,
        "metadata": {
            "source": "resume",
            "doc_type": "resume",
            "section": "personal_summary",
            "url": resume["personal"]["portfolio"],
        }
    })

    # Skills
    skills = resume["skills"]
    skills_text = "Technical Skills:\n"
    for category, items in skills.items():
        skills_text += f"  {category.replace('_', ' ').title()}: {', '.join(items)}\n"
    chunks.append({
        "text": skills_text,
        "metadata": {
            "source": "resume",
            "doc_type": "resume",
            "section": "skills",
            "url": resume["personal"]["portfolio"],
        }
    })

    # Projects — each project gets its own chunk
    for project in resume["projects"]:
        features_text = ""
        if "features" in project:
            features_text = "\nKey Features:\n" + "\n".join(f"  - {f}" for f in project["features"])

        challenges_text = ""
        if "challenges" in project:
            challenges_text = f"\nMain Challenge: {project['challenges']}"

        future_text = ""
        if "future" in project:
            future_text = f"\nFuture Plans: {project['future']}"

        project_text = (
            f"Project: {project['name']}\n"
            f"Technologies: {', '.join(project['tech'])}\n"
            f"Description: {project['description']}"
            f"{features_text}{challenges_text}{future_text}"
        )

        chunks.append({
            "text": project_text,
            "metadata": {
                "source": "resume",
                "doc_type": "resume",
                "section": f"project_{project['name'].lower().replace(' ', '_')}",
                "project_name": project["name"],
                "url": resume["personal"]["github"],
            }
        })

    # Achievements
    achv_text = "Achievements & Highlights:\n" + "\n".join(f"- {a}" for a in resume["achievements"])
    chunks.append({
        "text": achv_text,
        "metadata": {
            "source": "resume",
            "doc_type": "resume",
            "section": "achievements",
            "url": resume["personal"]["portfolio"],
        }
    })

    return chunks


class ResumeLoader:
    """Loads and ingests resume data into Pinecone."""

    async def run(self):
        """Main ingestion pipeline."""
        from config import settings
        from pinecone import Pinecone
        from openai import AsyncOpenAI

        logger.info("📄 Starting resume ingestion...")

        # 1. Chunk resume
        chunks = chunk_resume(RESUME_STRUCTURED)
        logger.info(f"  Created {len(chunks)} chunks from resume")

        # 2. Embed + upsert
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        oai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        vectors = []
        for chunk in chunks:
            resp = await oai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=chunk["text"],
            )
            embedding = resp.data[0].embedding
            chunk_id = hashlib.md5(chunk["text"].encode()).hexdigest()

            vectors.append({
                "id": f"resume_{chunk_id}",
                "values": embedding,
                "metadata": {**chunk["metadata"], "text": chunk["text"]},
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch, namespace="resume")

        logger.info(f"✅ Ingested {len(vectors)} resume chunks into Pinecone")


if __name__ == "__main__":
    asyncio.run(ResumeLoader().run())
