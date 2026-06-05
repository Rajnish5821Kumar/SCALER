"""
GitHub Loader — Fetches repos, READMEs, and code from GitHub
Ingests into Pinecone for RAG retrieval
"""

import asyncio
import logging
import hashlib
from typing import List, Dict, Optional
from config import settings

logger = logging.getLogger(__name__)

TARGET_REPOS = [
    "Rajnish5821Kumar",  # Fetch all public repos from this user
]


class GitHubLoader:
    """
    Fetches:
    - Public repos (name, description, stars, language, topics)
    - README.md for each repo
    - Key files (package.json, requirements.txt, main source)
    """

    def __init__(self):
        from github import Github
        self.gh = Github(settings.GITHUB_TOKEN)
        self.user = self.gh.get_user(settings.GITHUB_USERNAME)

    def fetch_repos(self) -> List[Dict]:
        """Get all public repos with metadata."""
        repos = []
        for repo in self.user.get_repos(type="public"):
            if repo.fork:
                continue  # Skip forks, focus on original work

            repo_data = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "",
                "url": repo.html_url,
                "language": repo.language or "Unknown",
                "stars": repo.stargazers_count,
                "topics": repo.get_topics(),
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "readme": self._get_readme(repo),
                "tech_stack": self._infer_tech(repo),
            }
            repos.append(repo_data)

        logger.info(f"  Fetched {len(repos)} repos from GitHub")
        return repos

    def _get_readme(self, repo) -> str:
        """Safely fetch README content."""
        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode("utf-8", errors="ignore")
            return content[:3000]  # Cap at 3000 chars per README
        except Exception:
            return ""

    def _infer_tech(self, repo) -> List[str]:
        """Infer tech stack from repo language and topics."""
        tech = []
        if repo.language:
            tech.append(repo.language)
        tech.extend(repo.get_topics())
        return list(set(tech))

    def chunk_repos(self, repos: List[Dict]) -> List[Dict]:
        """Convert repo data into retrieval chunks."""
        chunks = []

        # Overview chunk: all repos summarized
        repo_list = "\n".join([
            f"- {r['name']}: {r['description']} [{r['language']}]"
            for r in repos
        ])
        overview = f"Rajnish Kumar's GitHub Repositories ({len(repos)} public repos):\n{repo_list}"
        chunks.append({
            "text": overview,
            "metadata": {
                "source": "github",
                "doc_type": "github",
                "section": "repos_overview",
                "url": f"https://github.com/{settings.GITHUB_USERNAME}",
            }
        })

        # Individual repo chunks
        for repo in repos:
            # Main repo chunk
            repo_text = (
                f"Repository: {repo['name']}\n"
                f"URL: {repo['url']}\n"
                f"Description: {repo['description']}\n"
                f"Primary Language: {repo['language']}\n"
                f"Tech Stack: {', '.join(repo['tech_stack'])}\n"
                f"Stars: {repo['stars']}\n"
                f"Last Updated: {repo['updated_at'][:10]}\n"
            )
            if repo["readme"]:
                repo_text += f"\nREADME:\n{repo['readme'][:1500]}"

            chunks.append({
                "text": repo_text,
                "metadata": {
                    "source": "github",
                    "doc_type": "github",
                    "section": f"repo_{repo['name']}",
                    "repo_name": repo["name"],
                    "url": repo["url"],
                }
            })

        return chunks

    async def run(self):
        """Full ingestion pipeline."""
        from pinecone import Pinecone
        from openai import AsyncOpenAI

        logger.info("🐙 Starting GitHub ingestion...")

        repos = self.fetch_repos()
        chunks = self.chunk_repos(repos)
        logger.info(f"  Created {len(chunks)} chunks from {len(repos)} repos")

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        oai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        vectors = []
        for chunk in chunks:
            resp = await oai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=chunk["text"][:8000],  # OpenAI token limit
            )
            chunk_id = hashlib.md5(chunk["text"].encode()).hexdigest()
            vectors.append({
                "id": f"github_{chunk_id}",
                "values": resp.data[0].embedding,
                "metadata": {**chunk["metadata"], "text": chunk["text"][:1500]},
            })

        for i in range(0, len(vectors), 100):
            index.upsert(vectors=vectors[i:i+100], namespace="github")

        logger.info(f"✅ Ingested {len(vectors)} GitHub chunks into Pinecone")


if __name__ == "__main__":
    asyncio.run(GitHubLoader().run())
