# Enterprise Agentic RAG Platform

[![Java](https://img.shields.io/badge/Java-21%20LTS-18181b?logo=openjdk&logoColor=ED8B00&labelColor=101012)](https://adoptium.net)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.4.1-18181b?logo=springboot&logoColor=6DB33F&labelColor=101012)](https://spring.io)
[![Python](https://img.shields.io/badge/Python-3.12.16-18181b?logo=python&logoColor=3776AB&labelColor=101012)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-18181b?logo=fastapi&logoColor=009688&labelColor=101012)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-18181b?logo=langgraph&logoColor=7FC8FF&labelColor=101012)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20pgvector-18181b?logo=postgresql&logoColor=4169E1&labelColor=101012)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-7%20Alpine-18181b?logo=redis&logoColor=FF4438&labelColor=101012)](https://redis.io)
[![React](https://img.shields.io/badge/React-19-18181b?logo=react&logoColor=61DAFB&labelColor=101012)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.0-18181b?logo=vite&logoColor=9135FF&labelColor=101012)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-18181b?logo=docker&logoColor=2496ED&labelColor=101012)](https://www.docker.com)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Collector-18181b?logo=opentelemetry&logoColor=F5A800&labelColor=101012)](https://opentelemetry.io)
[![Jaeger](https://img.shields.io/badge/Jaeger-APM-18181b?logo=jaeger&logoColor=66CFE3&labelColor=101012)](https://www.jaegertracing.io)
[![Langfuse](https://img.shields.io/badge/Langfuse-Traces-18181b?labelColor=101012)](https://langfuse.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-TSDB-18181b?logo=prometheus&logoColor=E6522C&labelColor=101012)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-Operations-18181b?logo=grafana&logoColor=F46800&labelColor=101012)](https://grafana.com)
[![Maven](https://img.shields.io/badge/Maven-3.9-18181b?logo=apachemaven&logoColor=C71A36&labelColor=101012)](https://maven.apache.org)
[![Ollama](https://img.shields.io/badge/Ollama-Air--Gapped-18181b?logo=ollama&logoColor=FFFFFF&labelColor=101012)](https://ollama.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, **zero-data-egress cognitive intelligence platform** pairing a deterministic **Java 21 LTS Spring Boot governance perimeter** with an asynchronous **Python 3.12 LangGraph StateGraph engine**. Built for regulated environments (finance, defense, healthcare), the architecture enforces multi-tenant clearance RBAC, format-preserving reversible PII vaulting, heuristic prompt injection protection, dense + lexical hybrid retrieval with Reciprocal Rank Fusion (RRF), Self-RAG groundedness audits, and full-spectrum distributed observability.

---

## Key Architecture Pillars

- **Deterministic Java 21 Control Plane (`services/core-api`):**
  High-throughput reactive gateway (WebFlux, Bucket4j, Resilience4j) enforcing format-preserving PII tokenization, prompt injection heuristics, clearance-tier validation, and `llama-guard3:1b` safety evaluation before prompts touch the reasoning substrate.
- **Adaptive Corrective RAG (CRAG) Substrate (`services/memory-service`):**
  LangGraph state machine dynamically scoring candidate document relevance, triggering autonomous query reformulation loops, and auditing candidate responses through a Self-RAG token overlap auditor.
- **Hybrid Multi-Index Retrieval (Dense HNSW + Lexical BM25 RRF):**
  Single-trip PostgreSQL CTE executing 768-dimensional vector cosine similarity alongside `ts_rank_cd` full-text search, fused via Reciprocal Rank Fusion ($k = 60$).
- **Zero Data Egress (100% Air-Gapped Local Inference):**
  Direct hardware-accelerated local Ollama runtime hosting `llama3.2:3b`, `llama-guard3:1b`, and `nomic-embed-text:v1.5`. No customer prompts, tokens, or embeddings ever leave the host machine.
- **Full-Spectrum Observability & APM:**
  Out-of-the-box integration with Jaeger APM (distributed traces), Langfuse (agent state trees & generation logs), Prometheus (5s metric scrapes), and Grafana (pre-provisioned operations dashboard).
- **Refined Dark-Canvas Studio (`frontend`):**
  High-craft React 19 interface engineered around a four-step surface ladder (`#010102` canvas, `#0f1011` panels), hairline borders, and restrained lavender accenting.

---

## System Architecture

```mermaid
flowchart TB
    subgraph CLIENT["Consumer & Client Tier"]
        UI["React 19 Studio<br/>Vite Dev Server<br/>Port: 5173"]
    end

    subgraph GATEWAY["Control Plane & Governance (Java 21 LTS / Spring Boot)"]
        direction TB
        GW["Cognition Gateway Controller<br/>Port: 8080"]
        RL["Bucket4j Token Bucket Rate Limiter"]
        PII["Reversible PII Token Vault<br/>(Format-Preserving <PII:TOKEN:...>)"]
        INJ["Prompt Injection Heuristics Detector"]
        LG["Local Model Guard Client<br/>(llama-guard3:1b)"]
        AUDIT["HMAC SHA-256 Audit Ledger Service"]
        
        GW --> RL --> PII --> INJ --> LG --> AUDIT
    end

    subgraph ENGINE["Cognitive AI & Memory Engine (Python 3.12 / FastAPI)"]
        direction TB
        API["Memory Engine API<br/>Port: 8000"]
        
        subgraph LANGGRAPH["LangGraph Adaptive CRAG State Machine"]
            Router["1. Router Node (Redis Scratchpad)"]
            Retriever["2. Hybrid Search (Dense HNSW + BM25 RRF)"]
            Grader["3. Corrective RAG Doc Grader"]
            Rewriter["4. Semantic Query Rewriter"]
            Synthesizer["5. Grounded Synthesizer (llama3.2)"]
            Auditor["6. Self-RAG Faithfulness Auditor"]
            Consolidator["7. Memory Distiller & Writeback"]
            Fallback["8. Governed Fallback Node"]
        end
        API --> LANGGRAPH
    end

    subgraph PERSISTENCE["Storage & Working Memory (Docker)"]
        PG[("PostgreSQL 16 + pgvector<br/>Port: 5432<br/>• DB: enterprise_rag<br/>• DB: langfuse")]
        REDIS[("Redis 7 Alpine<br/>Port: 6379<br/>• Checkpoints & Working Memory")]
    end

    subgraph MODELS["Private Air-Gapped Model Runtime (Local Ollama)"]
        M1["llama-guard3:1b<br/>(Safety Classification)"]
        M2["nomic-embed-text:v1.5<br/>(768-dim Vector Embeddings)"]
        M3["llama3.2:3b<br/>(Reasoning & Synthesis)"]
    end

    subgraph TELEMETRY["Unified Observability Infrastructure (Docker)"]
        OTEL["OpenTelemetry Collector<br/>Ports: 4317 / 4318 / 8889"]
        JAEGER["Jaeger APM Traces<br/>Port: 16686"]
        PROM["Prometheus Time-Series<br/>Port: 9090"]
        GRAFANA["Grafana Operations Hub<br/>Port: 3000"]
        LANGFUSE["Langfuse Agent Tracing<br/>Port: 3100"]
    end

    UI -->|REST / SSE Tokens| GW
    GW -->|Guarded Context + Traceparent| API
    LG -->|Safety Classification| M1
    Retriever <-->|Dense & BM25 Queries| PG
    LANGGRAPH <-->|Session State| REDIS
    LANGGRAPH -->|Embeddings| M2
    LANGGRAPH -->|Synthesis| M3
    GATEWAY -.->|OTel Spans| OTEL
    ENGINE -.->|OTel Spans| OTEL
    ENGINE -->|Execution Trees & Scores| LANGFUSE
    OTEL --> JAEGER
    PROM -.->|Scrapes :8080 & :8000| GATEWAY
    PROM -.->|Scrapes :8000| ENGINE
    GRAFANA -->|Queries Metrics| PROM
    LANGFUSE -->|Persists Traces| PG
```

---

## Private Model Allocations

| Model | Footprint | Assigned Platform Role |
| :--- | :---: | :--- |
| **`llama-guard3:1b`** | ~1.2 GB VRAM | **Tier-1.5 Semantic Guardrail Classifier** — Evaluates unsafe content categories and cyberattack payloads in < 150ms. |
| **`nomic-embed-text:v1.5`** | ~0.5 GB VRAM | **Dense Semantic Embeddings** — Produces 768-dimensional embeddings aligned with PostgreSQL `vector(768)` HNSW cosine indexes. |
| **`llama3.2:3b`** | ~2.2 GB VRAM | **LangGraph Agent Reasoning & Synthesis** — Executes iterative query rewriting, document relevance grading, and grounded context synthesis with `[Source: <ref>]` citations. |

---

## Hybrid Retrieval: Dense HNSW + Lexical BM25 RRF

The platform eliminates retrieval blindspots by querying dense semantic vectors and lexical inverted indexes in a single transactional SQL CTE:

$$\operatorname{RRF}(d) = \frac{1}{60 + \operatorname{rank}_{\text{dense}}(d)} + \frac{1}{60 + \operatorname{rank}_{\text{lexical}}(d)}$$

```sql
WITH dense_search AS (
    SELECT id, kind, content, source_reference, confidence,
           ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) as dense_rank
    FROM memories
    WHERE tenant_id = $2 AND (clearance_level <= $3 OR $3 = 'TOP_SECRET')
    LIMIT 20
),
lexical_search AS (
    SELECT id, kind, content, source_reference, confidence,
           ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv_content, plainto_tsquery('english', $4)) DESC) as lex_rank
    FROM memories
    WHERE tenant_id = $2 AND (clearance_level <= $3 OR $3 = 'TOP_SECRET')
      AND tsv_content @@ plainto_tsquery('english', $4)
    LIMIT 20
)
SELECT 
    COALESCE(d.id, l.id) as id,
    COALESCE(d.kind, l.kind) as kind,
    COALESCE(d.content, l.content) as content,
    COALESCE(d.source_reference, l.source_reference) as source_reference,
    (COALESCE(1.0 / (60 + d.dense_rank), 0.0) + COALESCE(1.0 / (60 + l.lex_rank), 0.0)) as rrf_score
FROM dense_search d
FULL OUTER JOIN lexical_search l ON d.id = l.id
ORDER BY rrf_score DESC
LIMIT $5;
```

---

## Quickstart & Platform Orchestration

### Prerequisites
- Docker Desktop (with WSL2 or Windows containers)
- Ollama installed on host (`llama3.2:3b`, `llama-guard3:1b`, `nomic-embed-text:v1.5`)
- Java 21 LTS & Maven 3.9+
- Python 3.12.16
- Node.js 20+ & npm

---

### Option A: Automated PowerShell Orchestrator (Recommended)

Launch all 10 services, datastores, model runtimes, and telemetry hubs in a single command:
```powershell
.\start-all.ps1
```
*Automatically starts PostgreSQL 16 (pgvector), Redis 7, Jaeger APM, Prometheus, Grafana, Langfuse, OTel Collector, Python FastAPI (`:8000`), Java Spring Boot (`:8080`), and React Studio (`:5173`).*

To cleanly shut down all containers and background services:
```powershell
.\stop-all.ps1
```

---

### Option B: Step-by-Step Manual Launch

#### Step 1: Start Storage & Cache Containers
```bash
docker compose up -d
```
*Initializes PostgreSQL 16 (`pgvector:pg16` on `:5432`) and Redis 7 (`redis:7-alpine` on `:6379`).*

#### Step 2: Start Observability Stack
```bash
docker compose -f infrastructure/telemetry/docker-compose.telemetry.yml up -d
```
*Brings up Jaeger APM (`:16686`), OTel Collector (`:4317`), Prometheus (`:9090`), Grafana Hub (`:3000`), and Langfuse (`:3100`).*

#### Step 3: Pull Local Private Models
```bash
ollama pull llama-guard3:1b
ollama pull nomic-embed-text:v1.5
ollama pull llama3.2:3b
```

#### Step 4: Launch Python 3.12 AI Memory Engine
```bash
cd services/memory-service
python -m venv .venv
# Activate venv: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Linux/macOS)
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Step 5: Launch Java 21 Governance Gateway
```bash
cd services/core-api
mvn clean spring-boot:run
```

#### Step 6: Launch React Studio
```bash
cd frontend
npm install
npm run dev
# Studio active at: http://localhost:5173
```

---

## Decoupled Environment Strategy

All services extract hostnames, ports, and inter-service routing into environment files with resilient local fallbacks:

| Service / Layer | Config File | Template Reference | Key Variables |
| :--- | :--- | :--- | :--- |
| **Frontend Studio** | `frontend/src/config/appConfig.js` | [`frontend/.env.example`](frontend/.env.example) | `VITE_API_BASE_URL`, `VITE_JAEGER_URL`, `VITE_LANGFUSE_URL`, `VITE_PROMETHEUS_URL`, `VITE_GRAFANA_URL` |
| **Governance Gateway** | `application.yml` | [`services/core-api/.env.example`](services/core-api/.env.example) | `CORE_API_PORT`, `MEMORY_SERVICE_URL`, `LLM_BASE_URL`, `GUARD_MODEL_NAME`, `POSTGRES_*`, `REDIS_*` |
| **Cognitive Engine** | `app/config.py` | [`services/memory-service/.env.example`](services/memory-service/.env.example) | `PORT`, `LLM_BASE_URL`, `EMBEDDING_BASE_URL`, `POSTGRES_*`, `REDIS_*`, `LANGFUSE_*` |
| **Platform Root** | Consolidated Master | [`.env.example`](.env.example) | Complete master catalog for docker, datastores, models, and telemetry |

---

## Live Telemetry & Observability Hubs

| Hub | Port | URL | Role & Live Features |
| :--- | :--- | :--- | :--- |
| **React Studio** | `5173` | [http://localhost:5173](http://localhost:5173) | Governed Chat Studio, Guardrail Inspector & Knowledge Vault. |
| **Grafana SLA Hub** | `3000` | [http://localhost:3000](http://localhost:3000) | Pre-provisioned Operations Dashboard (p95 latency, QPS, Self-RAG score, JVM). |
| **Langfuse UI** | `3100` | [http://localhost:3100](http://localhost:3100) | Full LangGraph StateGraph trace execution trees, prompts, token counts. |
| **Jaeger APM** | `16686` | [http://localhost:16686](http://localhost:16686) | Distributed OpenTelemetry trace waterfall across Java -> Python -> DB. |
| **Prometheus** | `9090` | [http://localhost:9090](http://localhost:9090) | Time-series scraper querying Spring Boot Actuator & FastAPI `:metrics`. |
| **Core API Actuator** | `8080` | [http://localhost:8080/actuator/health](http://localhost:8080/actuator/health) | Java gateway health and Micrometer metrics. |
| **Audit Ledger API** | `8080` | [http://localhost:8080/api/v1/cognition/audit-logs](http://localhost:8080/api/v1/cognition/audit-logs) | Live immutable PostgreSQL compliance records & PII detection trails. |
| **Memory Engine Docs** | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI Swagger specification for Python engine. |

---

## Testing & Quality Assurance Suite

### Java Guardrail & PII Tokenization Tests
```bash
cd services/core-api
mvn test
# Runs 7 test suites validating regex PII vaulting, injection filters, and gateway routing.
```

### Python RAG Triad Faithfulness Benchmarks
```bash
cd services/memory-service
pytest tests/evals/test_rag_triad.py -v -s
# Evaluates context relevance, faithfulness (1.0000), and answer groundedness.
```

### End-to-End Governance Curl Test
```bash
curl -X POST http://localhost:8080/api/v1/cognition/query \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant-enterprise-prod" \
  -H "X-Clearance-Level: TOP_SECRET" \
  -d '{"prompt": "What is the domestic flight reimbursement limit under corporate travel policy?", "userId": "admin-01"}'
```

---

## Author

**Jayavignesh**
- **Website:** [jayavignesh.dev](https://jayavignesh.dev)
- **GitHub:** [@i-viki](https://github.com/i-viki)
- **Email:** [hello@jayavignesh.dev](mailto:hello@jayavignesh.dev)

---

## License

This platform is distributed under the **MIT License**. See the [`LICENSE`](LICENSE) file for complete terms.
