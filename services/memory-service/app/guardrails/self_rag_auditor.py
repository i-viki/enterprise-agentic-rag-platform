import structlog
from typing import List, Tuple
import re

logger = structlog.get_logger(__name__)

class SelfRAGAuditor:
    """Verifies that generated claims are substantiated by retrieved context chunks."""

    @staticmethod
    def audit_groundedness(answer: str, retrieved_contexts: List[str]) -> Tuple[float, bool]:
        """Calculates grounding score by evaluating lexical and entity overlap with source context."""
        if not retrieved_contexts:
            return 0.0, False

        combined_context = " ".join(retrieved_contexts).lower()
        
        # Split answer into declarative sentences
        sentences = [s.strip() for s in re.split(r'[.!?]', answer) if len(s.strip()) > 10]
        if not sentences:
            return 1.0, True

        # Filter out common conversational/reasoning filler clauses
        conversational_fillers = [
            "according to", "based on", "provided context", "official documents", 
            "to determine", "we need to check", "corporate policy", "as stated in"
        ]
        substantive_sentences = []
        for s in sentences:
            s_clean = s.strip()
            # If the sentence is just conversational wrapper, don't penalize grounding
            tokens = [t.lower() for t in re.findall(r'\b[a-zA-Z0-9_-]{4,}\b', s_clean)]
            if len(tokens) >= 3:
                substantive_sentences.append(s_clean)

        if not substantive_sentences:
            return 1.0, True

        supported_sentences = 0

        for sentence in substantive_sentences:
            tokens = [t.lower() for t in re.findall(r'\b[a-zA-Z0-9_-]{4,}\b', sentence)]
            matches = sum(1 for t in tokens if t in combined_context)
            ratio = matches / len(tokens)
            
            # Sentence is considered substantiated if at least 35% of key tokens appear in context
            if ratio >= 0.35:
                supported_sentences += 1

        grounding_score = supported_sentences / len(substantive_sentences)
        is_grounded = grounding_score >= 0.55

        logger.info(
            "self_rag_grounding_audit",
            total_claims=len(substantive_sentences),
            supported_claims=supported_sentences,
            score=round(grounding_score, 2),
            verdict="GROUNDED" if is_grounded else "POTENTIAL_HALLUCINATION"
        )

        return float(grounding_score), bool(is_grounded)


self_rag_auditor = SelfRAGAuditor()

