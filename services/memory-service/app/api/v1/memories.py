from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.memory import MemoryRecordCreate, MemoryRecordResponse, MemorySearchQuery, MemorySearchResult
from app.memory.hybrid_retriever import hybrid_retriever
from app.core.database import db
from app.core.model_client import model_client
import json

router = APIRouter(prefix="/v1/memories", tags=["Memories"])

@router.post("", response_model=MemoryRecordResponse, status_code=201)
async def create_memory(record: MemoryRecordCreate):
    """Ingests and indexes a new cognitive memory record."""
    if not db.pool:
        raise HTTPException(status_code=503, detail="Database pool unavailable")

    embedding = await model_client.get_embedding(record.content)

    async with db.pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO memories (
                    tenant_id, user_id, department_id, required_clearance_level,
                    allowed_roles, kind, content, embedding, source_type,
                    source_reference, confidence, relevance, retention, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                ) RETURNING 
                    id, tenant_id, user_id, department_id, required_clearance_level,
                    allowed_roles, kind, content, source_type, source_reference,
                    confidence, relevance, retention, status, revision, metadata,
                    created_at, updated_at;
                """,
                record.tenant_id,
                record.user_id,
                record.department_id,
                record.required_clearance_level,
                record.allowed_roles,
                record.kind,
                record.content,
                embedding,
                record.source_type,
                record.source_reference,
                record.confidence,
                record.relevance,
                record.retention,
                json.dumps(record.metadata)
            )

            return MemoryRecordResponse(
                id=row["id"],
                tenant_id=row["tenant_id"],
                user_id=row["user_id"],
                department_id=row["department_id"],
                required_clearance_level=row["required_clearance_level"],
                allowed_roles=row["allowed_roles"],
                kind=row["kind"],
                content=row["content"],
                source_type=row["source_type"],
                source_reference=row["source_reference"],
                confidence=float(row["confidence"]),
                relevance=float(row["relevance"]),
                retention=row["retention"],
                status=row["status"],
                revision=row["revision"],
                metadata=json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to insert memory: {str(e)}")

@router.post("/search", response_model=List[MemorySearchResult])
async def search_memories(search_params: MemorySearchQuery):
    """Executes parameterized Reciprocal Rank Fusion (pgvector + BM25) hybrid search."""
    return await hybrid_retriever.search(
        tenant_id=search_params.tenant_id,
        query_text=search_params.query_text,
        clearance_level=search_params.clearance_level,
        user_roles=search_params.user_roles,
        top_k=search_params.top_k
    )

