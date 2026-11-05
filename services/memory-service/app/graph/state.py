from typing import Annotated, Sequence, TypedDict, Literal, Optional, Dict, Any, List
from langchain_core.messages import BaseMessage
import operator

class RetrievedDocument(TypedDict):
    id: str
    kind: Literal["episodic", "semantic", "procedural", "working"]
    content: str
    source_reference: str
    confidence: float
    rrf_score: float
    relevance_verdict: Optional[Literal["relevant", "irrelevant"]]

class CognitionState(TypedDict):
    # Execution, Multi-Tenancy & Distributed Tracing Identifiers
    trace_id: str
    traceparent: Optional[str]
    span_id: Optional[str]
    tenant_id: str
    user_id: str
    user_roles: List[str]
    clearance_level: int
    thread_id: str
    
    # Message History & Prompts
    messages: Annotated[Sequence[BaseMessage], operator.add]
    raw_query: str
    sanitized_query: str
    transformed_query: Optional[str]
    
    # Cognitive Context
    working_memory: Dict[str, Any]
    retrieved_documents: List[RetrievedDocument]
    
    # Agentic Evaluation & Control Flow
    loop_step: int
    max_retries: int
    retrieval_grade: Literal["sufficient", "insufficient", "empty"]
    generated_answer: Optional[str]
    grounding_score: float
    is_grounded: bool
    final_response: Optional[Dict[str, Any]]

