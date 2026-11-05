import structlog
from typing import Literal
from app.graph.state import CognitionState

logger = structlog.get_logger(__name__)

def evaluate_retrieval_adequacy(state: CognitionState) -> Literal["synthesize", "rewrite_query", "fallback"]:
    """Determines whether context is sufficient to synthesize, or if query rewriting is required."""
    grade = state.get("retrieval_grade", "sufficient")
    loop_step = state.get("loop_step", 1)
    max_retries = state.get("max_retries", 2)

    logger.info("edge_eval_retrieval_grade", grade=grade, loop_step=loop_step)

    if grade == "sufficient":
        return "synthesize"
    elif grade == "insufficient" and loop_step <= max_retries:
        return "rewrite_query"
    else:
        return "fallback"

def evaluate_groundedness_verdict(state: CognitionState) -> Literal["consolidate", "synthesize", "fallback"]:
    """Determines whether generated answer passed Self-RAG grounding check."""
    is_grounded = state.get("is_grounded", True)
    loop_step = state.get("loop_step", 1)
    max_retries = state.get("max_retries", 2)

    logger.info("edge_eval_groundedness", is_grounded=is_grounded, loop_step=loop_step)

    if is_grounded:
        return "consolidate"
    elif loop_step <= max_retries:
        return "synthesize"
    else:
        return "consolidate" if state.get("grounding_score", 0.0) >= 0.4 else "fallback"

