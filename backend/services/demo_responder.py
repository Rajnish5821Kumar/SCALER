"""
Smart Demo Responder — Gives real answers from resume data without OpenAI
Used when OPENAI_API_KEY is not configured
"""

from typing import List, Dict

# Rajnish's complete knowledge base for demo responses
DEMO_KNOWLEDGE = {
    "about|yourself|who are you|introduce|background|tell me": """
I'm **Rajnish Kumar**, a passionate Full-Stack & AI Engineer! 🚀

Here's a quick snapshot:
- 💻 **Tech Stack**: MERN, Next.js, FastAPI, Python, React Native, TypeScript, Java/Spring Boot
- 🧠 **AI/ML**: Machine Learning, Deep Learning, LangChain, OpenAI API, RAG systems
- 📱 **Mobile**: Cross-platform apps with Expo & React Native
- 🛠️ **Projects**: Built 6+ production-ready applications

I love building end-to-end products that blend clean engineering with AI capabilities.

📧 rk2452003@gmail.com | 🔗 [LinkedIn](https://linkedin.com/in/rajnish-kumar-5b480a255/) | 💻 [GitHub](https://github.com/Rajnish5821Kumar)

*(Source: Resume — Personal Summary)*
""",

    "tech stack|technologies|skills|languages|tools|frameworks": """
Here's my full tech stack breakdown:

**Frontend**
- React, Next.js 14, TypeScript, Tailwind CSS, Redux

**Backend**
- Node.js, Express.js, FastAPI (Python), Spring Boot (Java), GraphQL

**Mobile**
- React Native + Expo, TypeScript

**Databases**
- MongoDB, PostgreSQL, MySQL, SQL Server, Redis

**AI/ML**
- Python, Machine Learning, Deep Learning, LangChain, OpenAI API, RAG

**DevOps & Tools**
- Docker, Git, GitHub Actions, Vercel, Railway, Render
- Razorpay, JWT, REST APIs, Postman

*(Source: Resume — Technical Skills)*
""",

    "project|ecommerce|e-commerce|shop|razorpay|redux": """
**E-Commerce Website** 🛒

One of my flagship projects — a full-featured MERN stack e-commerce platform.

**Tech**: MongoDB + Express + React + Node.js + Redux + Razorpay + Tailwind CSS

**Key Features:**
- 🔐 JWT authentication & role-based authorization
- 🛍️ Product catalog with search and category filters
- 🛒 Shopping cart with Redux state management
- 💳 Razorpay payment gateway integration
- 📊 Admin dashboard for orders & inventory
- 📱 Fully responsive Tailwind CSS design

**Main Challenge**: Real-time inventory sync and handling Razorpay webhooks reliably.

**Future Plan**: Add ML-based product recommendation engine using collaborative filtering.

*(Source: Resume — Projects)*
""",

    "campus|smart campus|attendance|timetable": """
**Smart Campus Management System** 🏫

A comprehensive university management platform.

**Tech**: React + Node.js + Express + MongoDB

**Features:**
- 👨‍🎓 Role-based access control (Student / Faculty / Admin)
- 📋 Automated attendance tracking system
- 📅 Timetable and schedule management
- 🔔 Real-time notification system
- 🏛️ Resource & classroom booking

This project taught me a lot about designing multi-role systems with clean permission boundaries.

*(Source: Resume — Projects)*
""",

    "medical|appointment|doctor|healthcare|hospital": """
**Medical Appointment Booking System** 🏥

A healthcare platform connecting patients with doctors.

**Tech**: React + Node.js + Express + MongoDB

**Features:**
- 👩‍⚕️ Doctor profiles with specialization listing
- 📅 Real-time appointment slot availability
- 📧 Automated email/SMS reminders
- 📁 Patient medical history tracking
- 🖥️ Admin panel for doctor management

*(Source: Resume — Projects)*
""",

    "policy|flask|sql server|hr": """
**Policy Clarification Portal** 📋

An enterprise HR portal for policy Q&A.

**Tech**: Python Flask + SQL Server + HTML/CSS

**Purpose**: Employees can search and clarify company HR policies using NLP-based search with a structured SQL Server backend.

This project was my first deep dive into building search systems on enterprise data.

*(Source: Resume — Projects)*
""",

    "react native|mobile|expo|app|cross-platform": """
**Expo React Native Applications** 📱

I've built cross-platform mobile apps using the Expo ecosystem.

**Tech**: React Native + Expo + TypeScript

**Capabilities:**
- Native UI components
- Camera & media integration
- Push notifications
- Cross-platform (iOS + Android from a single codebase)
- OTA updates via Expo

*(Source: Resume — Projects)*
""",

    "ai|machine learning|deep learning|ml|llm|langchain|openai": """
**AI & Machine Learning Experience** 🧠

I've worked on multiple AI/ML projects including:

- 🤖 **LLM Applications**: Chatbots and document Q&A using LangChain + OpenAI API
- 🔍 **RAG Systems**: Retrieval-Augmented Generation pipelines (like this very AI Persona!)
- ⚙️ **Automation**: AI-powered workflow automation tools
- 🐍 **FastAPI ML APIs**: Serving ML models via production-grade REST APIs
- 📊 **Deep Learning**: Neural network implementations in Python

This AI Persona you're talking to right now is itself one of my AI engineering projects!

*(Source: Resume — AI Projects)*
""",

    "contact|email|linkedin|github|portfolio|reach": """
Here's how to reach Rajnish:

| Channel | Link |
|---------|------|
| 📧 **Email** | rk2452003@gmail.com |
| 🔗 **LinkedIn** | [rajnish-kumar-5b480a255](https://linkedin.com/in/rajnish-kumar-5b480a255/) |
| 💻 **GitHub** | [Rajnish5821Kumar](https://github.com/Rajnish5821Kumar) |
| 🌐 **Portfolio** | [portfolio-website-jet-delta-77.vercel.app](https://portfolio-website-jet-delta-77.vercel.app/) |

*(Source: Resume — Contact)*
""",

    "schedule|interview|book|meeting|call|hire": """
I'd love to connect for an interview! 🎯

You can book a slot directly — just tell me:
1. **Your preferred date** (e.g., "next Tuesday")
2. **Time** (e.g., "2 PM")
3. **Timezone** (e.g., IST, PST)

Or reach out directly:
- 📧 **rk2452003@gmail.com**
- 🔗 **[LinkedIn](https://linkedin.com/in/rajnish-kumar-5b480a255/)**

I'm available for **video calls, phone screens, or in-person** interviews. My usual availability is **weekdays 10 AM – 7 PM IST**.

Would you like me to check available slots on my calendar?
""",

    "experience|work|job|company|intern|fresher": """
I'm a fresh graduate and **actively seeking full-time opportunities** in Full-Stack or AI Engineering roles.

Here's what I bring to the table:
- ✅ 6+ production-ready projects built end-to-end
- ✅ Hands-on with both traditional web dev AND modern AI/LLM tools
- ✅ Experience across the full stack: frontend, backend, mobile, AI
- ✅ Real payment gateway (Razorpay) integration experience
- ✅ Cross-platform mobile development

For the latest work history, please check my [LinkedIn](https://linkedin.com/in/rajnish-kumar-5b480a255/).

*(Source: Resume — Experience)*
""",

    "education|college|university|degree|btech|graduation": """
I hold a **B.Tech in Computer Science / Engineering**.

For full education details including institution name and graduation year, please check my [LinkedIn profile](https://linkedin.com/in/rajnish-kumar-5b480a255/) or [Portfolio](https://portfolio-website-jet-delta-77.vercel.app/).

*(Source: Resume — Education)*
""",

    "strength|achievement|proud|best": """
Some highlights I'm proud of:

🏆 **Technical Achievements:**
- Built 6+ full-stack production apps from scratch
- Integrated real payment gateways (Razorpay) in live projects
- Built an end-to-end AI Persona with RAG, Voice, and Calendar integration
- Mastered both AI/ML engineering AND traditional web development

🚀 **What sets me apart:**
- I'm a rare **full-stack + AI hybrid** — I can build the frontend, backend, AND the ML pipeline
- Fast learner: picked up FastAPI, LangChain, and Pinecone for this Scaler assignment in days
- I ship working products, not just toy demos

*(Source: Resume — Achievements)*
""",
}

DEFAULT_RESPONSE = """
That's an interesting question! Let me be transparent — I'm currently running in **demo mode** (no OpenAI key configured).

I can confidently answer questions about:
- 👤 Rajnish's background and skills
- 💼 His projects (E-Commerce, Smart Campus, Medical Booking, etc.)
- 🧠 AI/ML experience
- 📞 Contact information
- 📅 Scheduling an interview

Try asking: *"Tell me about your projects"* or *"What is your tech stack?"*

*(Add OPENAI_API_KEY to backend/.env for full AI-powered responses)*
"""


def get_demo_response(query: str) -> str:
    """
    Match query against knowledge base keywords and return best answer.
    Simple keyword matching for demo mode.
    """
    query_lower = query.lower()

    best_match = None
    best_score = 0

    for keywords, response in DEMO_KNOWLEDGE.items():
        keyword_list = keywords.split("|")
        score = sum(1 for kw in keyword_list if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = response

    if best_score == 0:
        return DEFAULT_RESPONSE

    return best_match.strip()
