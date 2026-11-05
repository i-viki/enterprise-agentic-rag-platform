from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID

class AgentCognitionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    trace_id: str
    thread_id: Optional[str] = "default-thread"
    tenant_id: str
    user_id: str
    clearance_level: int = 1
    user_roles: List[str] = ["ALL"]
    sanitized_prompt: str
    traceparent: Optional[str] = None

class Citation(BaseModel):
    memory_id: UUID
    source_reference: str
    confidence: float
    rrf_score: float

class AgentCognitionResponse(BaseModel):
    trace_id: str
    thread_id: str
    generated_answer: str
    citations: List[Citation]
    grounding_score: float
    is_grounded: bool
    loop_step: int
    retrieval_grade: str

