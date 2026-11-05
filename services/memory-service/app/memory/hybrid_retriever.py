import structlog
from typing import List, Optional
from uuid import UUID
from app.core.database import db
from app.core.model_client import model_client
from app.schemas.memory import MemorySearchResult
from app.config import settings

logger = structlog.get_logger(__name__)

RRF_QUERY_SQL = """
WITH vector_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> $1) AS rank
    FROM memories
    WHERE tenant_id = $2
      AND status = 'active'
      AND required_clearance_level <= $3
      AND (allowed_roles && $4 OR 'ALL' = ANY(allowed_roles))
    LIMIT 25
),
text_search AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('english', $5)) DESC) AS rank
    FROM memories
    WHERE tenant_id = $2
      AND status = 'active'
      AND required_clearance_level <= $3
      AND (allowed_roles && $4 OR 'ALL' = ANY(allowed_roles))
      AND content_tsv @@ plainto_tsquery('english', $5)
    LIMIT 25
)
SELECT 
    m.id,
    m.kind,
    m.content,
    m.source_reference,
    m.confidence,
    COALESCE(1.0 / ($6 + v.rank), 0.0) + COALESCE(1.0 / ($6 + t.rank), 0.0) AS rrf_score
FROM memories m
LEFT JOIN vector_search v ON m.id = v.id
LEFT JOIN text_search t ON m.id = t.id
WHERE v.id IS NOT NULL OR t.id IS NOT NULL
ORDER BY rrf_score DESC
LIMIT $7;
"""

class HybridRetriever:
    """Executes high-performance Reciprocal Rank Fusion (pgvector HNSW + PostgreSQL BM25)."""

    async def search(
        self,
        tenant_id: str,
        query_text: str,
        clearance_level: int = 1,
        user_roles: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[MemorySearchResult]:
        if user_roles is None:
            user_roles = ["ALL"]

        # 1. Generate query embedding via nomic-embed-text:v1.5
        query_embedding = await model_client.get_embedding(query_text)

        if not db.pool:
            logger.warn("database_offline_mock_retrieval")
            return []

        async with db.pool.acquire() as conn:
            try:
                rows = await conn.fetch(
                    RRF_QUERY_SQL,
                    query_embedding,               # $1: embedding vector
                    tenant_id,                     # $2: tenant_id
                    clearance_level,               # $3: clearance_level
                    user_roles,                    # $4: allowed_roles array
                    query_text,                    # $5: full-text tsquery
                    settings.RRF_K_CONSTANT,       # $6: 60 constant
                    top_k                          # $7: limit
                )

                results = [
                    MemorySearchResult(
                        id=row["id"],
                        kind=row["kind"],
                        content=row["content"],
                        source_reference=row["source_reference"],
                        confidence=float(row["confidence"]),
                        rrf_score=float(row["rrf_score"])
                    )
                    for row in rows
                ]

                logger.info(
                    "hybrid_retrieval_executed",
                    tenant_id=tenant_id,
                    query_length=len(query_text),
                    matches_found=len(results)
                )
                return results

            except Exception as e:
                logger.error("hybrid_search_query_error", error=str(e))
                return []


hybrid_retriever = HybridRetriever()

