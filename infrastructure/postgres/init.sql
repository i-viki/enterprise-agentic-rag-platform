-- Ensure extensions are loaded
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Ensure default postgres role exists alongside rag_admin
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
        CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'rag_secure_password_2026';
    END IF;
END $$;

-- 1. Tenants & Security Clearances
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    max_memory_retention_days INTEGER DEFAULT 365,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed Default Enterprise Tenant
INSERT INTO tenants (id, name, max_memory_retention_days)
VALUES ('tenant-enterprise-prod', 'Enterprise Global Corp', 730)
ON CONFLICT (id) DO NOTHING;

-- 2. Cognitive Memory with Multi-Tenant RBAC & Partitioning
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    department_id VARCHAR(64) NOT NULL,
    required_clearance_level INTEGER NOT NULL DEFAULT 1, -- 1=Public, 2=Internal, 3=Confidential, 4=Restricted
    allowed_roles TEXT[] NOT NULL DEFAULT '{"ALL"}',
    
    kind TEXT NOT NULL CHECK (kind IN ('episodic', 'semantic', 'procedural', 'working')),
    content TEXT NOT NULL,
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding vector(768), -- Matches nomic-embed-text:v1.5
    
    source_type TEXT NOT NULL CHECK (source_type IN ('conversation', 'document', 'system_observation', 'user_explicit')),
    source_reference TEXT NOT NULL,
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    relevance NUMERIC(3,2) NOT NULL DEFAULT 1.0 CHECK (relevance >= 0.0 AND relevance <= 1.0),
    retention TEXT NOT NULL CHECK (retention IN ('session', 'review_required', 'long_term')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'superseded', 'retracted')),
    superseded_by UUID REFERENCES memories(id) ON DELETE SET NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indices for Production Multi-Tenant Query Performance
CREATE INDEX IF NOT EXISTS memories_tenant_rbac_idx 
    ON memories (tenant_id, required_clearance_level, status);
CREATE INDEX IF NOT EXISTS memories_user_idx 
    ON memories (user_id);
CREATE INDEX IF NOT EXISTS memories_tsv_idx 
    ON memories USING GIN(content_tsv);
CREATE INDEX IF NOT EXISTS memories_embedding_hnsw_idx 
    ON memories USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 3. LangGraph Thread Checkpoint Ledger
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- 4. Immutable Enterprise Audit Trail
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    event_type TEXT NOT NULL,
    prompt_raw_length INTEGER NOT NULL,
    prompt_sanitized_length INTEGER NOT NULL,
    pii_entities_detected TEXT[] DEFAULT '{}',
    guardrail_status TEXT NOT NULL CHECK (guardrail_status IN ('CLEAN', 'SANITIZED', 'BLOCKED')),
    guardrail_verdict_notes JSONB DEFAULT '[]'::jsonb,
    retrieved_memory_ids UUID[] DEFAULT '{}',
    evaluation_scores JSONB DEFAULT '{}'::jsonb, -- Context relevance, faithfulness, etc.
    execution_time_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_logs_trace_idx ON audit_logs(trace_id);
CREATE INDEX IF NOT EXISTS audit_logs_tenant_created_idx ON audit_logs(tenant_id, created_at DESC);

-- 5. Fallback Reversible PII Vault (for environments operating without Redis)
CREATE TABLE IF NOT EXISTS pii_token_vault (
    token_key VARCHAR(128) PRIMARY KEY,
    raw_value TEXT NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '15 minutes'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS pii_token_vault_expires_idx ON pii_token_vault(expires_at);

