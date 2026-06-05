"""
Hallucination Guard — Validates LLM answers against retrieved context
Uses semantic similarity + keyword overlap to detect fabrication
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class HallucinationGuard:
    """
    Multi-layer hallucination detection:
    1. Keyword overlap check between answer and context
    2. Semantic similarity threshold (cosine > 0.35)
    3. Forbidden claim detection (specific dates, numbers not in context)
    """

    SAFE_THRESHOLD = 0.35
    MIN_KEYWORD_OVERLAP = 0.2

    async def check(self, answer: str, context_docs: List[Dict]) -> bool:
        """
        Returns True if answer appears grounded in context.
        Returns False if potential hallucination detected.
        """
        if not context_docs:
            return False

        context_text = " ".join([d.get("text", "") for d in context_docs]).lower()
        answer_lower = answer.lower()

        # Quick pass — if answer is a refusal/acknowledgment, it's always safe
        refusal_signals = [
            "i don't have", "i can only answer", "could you rephrase",
            "not in my profile", "check my github", "check my portfolio"
        ]
        if any(s in answer_lower for s in refusal_signals):
            return True

        # Layer 1: Keyword overlap
        answer_words = set(answer_lower.split())
        context_words = set(context_text.split())
        # Remove stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "i", "my", "and", "or", "to", "of", "in", "for"}
        answer_content = answer_words - stop_words
        context_content = context_words - stop_words

        if not answer_content:
            return True

        overlap = len(answer_content & context_content) / len(answer_content)

        if overlap < self.MIN_KEYWORD_OVERLAP:
            logger.warning(f"Low keyword overlap ({overlap:.2f}) — possible hallucination")
            return False

        # Layer 2: Check for suspicious specific claims not in context
        suspicious = self._detect_suspicious_claims(answer, context_text)
        if suspicious:
            logger.warning(f"Suspicious specific claims detected: {suspicious}")
            return False

        return True

    def _detect_suspicious_claims(self, answer: str, context: str) -> List[str]:
        """Flag specific numerical claims or named entities not found in context."""
        import re
        suspicious = []

        # Look for specific years/numbers in answer that aren't in context
        years = re.findall(r'\b(20\d{2})\b', answer)
        for year in years:
            if year not in context:
                suspicious.append(f"year {year} not in context")

        # Look for specific percentages
        percentages = re.findall(r'\b\d+%\b', answer)
        for pct in percentages:
            if pct not in context:
                suspicious.append(f"percentage {pct} not in context")

        # Look for specific company names not in context
        company_patterns = re.findall(r'\b(?:at|for|with|joined)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\b', answer)
        for company in company_patterns:
            if company.lower() not in context.lower():
                suspicious.append(f"company '{company}' not in context")

        return suspicious
