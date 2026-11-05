from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

@dataclass
class MemoryRecord:
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

