import structlog
from typing import Dict, Any, Optional
from uuid import uuid4
from app.core.database import db
from app.core.model_client import model_client

logger = structlog.get_logger(__name__)

class MemoryConsolidationWorker:
    """Asynchronous worker that distills conversation scratchpads into durable cognitive memories."""

    @staticmethod
    async def consolidate_session_facts(
        tenant_id: str,
        user_id: str,
        department_id: str,
        clearance_level: int,
        conversation_summary: str,
        extracted_facts: list[str]
    ) -> int:
        """Persists newly observed facts, resolving conflicts with existing records."""
        if not db.pool or not extracted_facts:
            return 0

        saved_count = 0
        async with db.pool.acquire() as conn:
            for fact in extracted_facts:
                if len(fact.strip()) < 10:
                    continue

                # Generate embedding
                fact_embedding = await model_client.get_embedding(fact)

                # Check if an existing memory is semantically identical or in conflict
                existing = await conn.fetchrow(
                    """
                    SELECT id, content, revision
                    FROM memories
                    WHERE tenant_id = $1 AND user_id = $2 AND status = 'active'
                    ORDER BY embedding <=> $3
                    LIMIT 1;
                    """,
                    tenant_id,
                    user_id,
                    fact_embedding
                )

                if existing:
                    # Mark existing memory as superseded if revision update
                    old_id = existing["id"]
                    new_revision = existing["revision"] + 1

                    new_id = await conn.fetchval(
                        """
                        INSERT INTO memories (
                            tenant_id, user_id, department_id, required_clearance_level,
                            kind, content, embedding, source_type, source_reference,
                            confidence, revision
                        ) VALUES (
                            $1, $2, $3, $4, 'episodic', $5, $6, 'conversation',
                            'session_distillation', 0.95, $7
                        ) RETURNING id;
                        """,
                        tenant_id, user_id, department_id, clearance_level,
                        fact, fact_embedding, new_revision
                    )

                    await conn.execute(
                        """
                        UPDATE memories
                        SET status = 'superseded', superseded_by = $1, updated_at = now()
                        WHERE id = $2;
                        """,
                        new_id, old_id
                    )
                    saved_count += 1
                else:
                    # Fresh memory entry
                    await conn.execute(
                        """
                        INSERT INTO memories (
                            tenant_id, user_id, department_id, required_clearance_level,
                            kind, content, embedding, source_type, source_reference,
                            confidence, revision
                        ) VALUES (
                            $1, $2, $3, $4, 'episodic', $5, $6, 'conversation',
                            'session_distillation', 0.90, 1
                        );
                        """,
                        tenant_id, user_id, department_id, clearance_level,
                        fact, fact_embedding
                    )
                    saved_count += 1

        logger.info("memory_consolidation_completed", tenant_id=tenant_id, user_id=user_id, saved_facts=saved_count)
        return saved_count


memory_consolidator = MemoryConsolidationWorker()

