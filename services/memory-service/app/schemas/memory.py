from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID, uuid4
from datetime import datetime

class MemoryRecordCreate(BaseModel):
    tenant_id: str = Field(..., example="tenant-enterprise-prod")
    user_id: str = Field(..., example="emp-7890")
    department_id: str = Field(..., example="FINANCE")
    required_clearance_level: int = Field(default=1, ge=1, le=4)
    allowed_roles: List[str] = Field(default=["ALL"])
    kind: Literal["episodic", "semantic", "procedural", "working"]
    content: str
    source_type: Literal["conversation", "document", "system_observation", "user_explicit"]
    source_reference: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    relevance: float = Field(default=1.0, ge=0.0, le=1.0)
    retention: Literal["session", "review_required", "long_term"] = "long_term"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemoryRecordResponse(BaseModel):
    id: UUID
    tenant_id: str
    user_id: str
    department_id: str
    required_clearance_level: int
    allowed_roles: List[str]
    kind: str
    content: str
    source_type: str
    source_reference: str
    confidence: float
    relevance: float
    retention: str
    status: str
    revision: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class MemorySearchQuery(BaseModel):
    tenant_id: str
    query_text: str
    user_id: Optional[str] = None
    clearance_level: int = 1
    user_roles: List[str] = ["ALL"]
    top_k: int = 5
    kind_filter: Optional[Literal["episodic", "semantic", "procedural", "working"]] = None

class MemorySearchResult(BaseModel):
    id: UUID
    kind: str
    content: str
    source_reference: str
    confidence: float
    rrf_score: float

