# Enterprise Cognitive Studio

[![React](https://img.shields.io/badge/React-19-18181b?logo=react&logoColor=61DAFB&labelColor=101012)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3-18181b?logo=vite&logoColor=9135FF&labelColor=101012)](https://vitejs.dev)
[![Lucide](https://img.shields.io/badge/Lucide-React-18181b?labelColor=101012)](https://lucide.dev)
[![Oxlint](https://img.shields.io/badge/Oxlint-Clean-18181b?labelColor=101012)](https://oxc.rs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

A precision dark-canvas web interface engineered for the **Enterprise Agentic RAG Platform**. It provides interactive conversational reasoning, real-time LangGraph agent traversal monitoring, Self-RAG groundedness verification, RBAC clearance controls, and an operations hub connecting distributed telemetry spans.

---

## Architecture & Modules

The studio interface is divided into three purpose-built operational surfaces:

### 1. Cognition Studio (`src/components/CognitionStudio.jsx`)
- **Conversational Interface:** Full-duplex interaction with the deterministic Java 21 governance gateway (`:8080`) routing through the Python LangGraph engine (`:8000`).
- **Prompt Preset Chips:** One-click enterprise test cases covering policy inquiries, SOP compliance, PII token vault validation, and prompt injection defense.
- **Guardrail Status Tracking:** Live policy badges (`CLEAN`, `SANITIZED`, `BLOCKED`) displaying PII redaction and heuristic interception verdicts.
- **LangGraph State Lifecycle Tracker:** Visualizes the 6-stage cognitive state machine traversal:
  1. `01 Router & Memory Scratchpad` (Redis working memory)
  2. `02 Dense & Lexical Hybrid Search` (pgvector HNSW + BM25 RRF, $k = 60$)
  3. `03 CRAG Document Grader` (Relevance scoring & filtering)
  4. `04 Context Synthesizer` (Grounded local LLM inference)
  5. `05 Self-RAG Faithfulness Auditor` (Citation token overlap audit)
  6. `06 Memory Consolidator` (Thread writeback & checkpointing)
- **Self-RAG Groundedness Bar:** Real-time percentage indicator tracking token claim faithfulness against retrieved context chunks.
- **Source Context Inspector:** Inspects source references, memory IDs, and Reciprocal Rank Fusion (RRF) scores for cited chunks.

### 2. Observability & APM Hub (`src/components/ObservabilityHub.jsx`)
- **Direct APM Access Panels:** Single-click external launch cards for the telemetry infrastructure:
  - **Jaeger APM (`:16686`):** Distributed W3C trace visualization.
  - **Langfuse UI (`:3100`):** Agent execution DAGs, prompt histories, and token consumption metrics.
  - **Prometheus (`:9090`):** Time-series metrics and scrape targets.
  - **Grafana Hub (`:3000`):** Production SLA operations dashboards.
- **RAG Triad KPI Strip:** Displays real-time quality scores against enterprise SLAs:
  - Context Relevance (Target: >= 88%)
  - Faithfulness / Groundedness (Target: >= 92%)
  - Answer Relevance (Target: >= 90%)
  - p95 Latency SLA (< 1500ms)
  - Zero-Data-Egress Guarantee (100% air-gapped local inference)
- **Cryptographic Audit Ledger:** Tabular view of HMAC SHA-256 verified request events, trace references, detected PII entities, and latency benchmarks.

### 3. Knowledge Vault (`src/components/KnowledgeVault.jsx`)
- **Enterprise Memory Browser:** Browse and filter vectorized corporate knowledge by memory kind (`Semantic`, `Episodic`, `Procedural`) and clearance level.
- **Clearance Filtering:** Dynamic display enforcing security clearance tiers (Level 1: Internal, Level 2: Confidential, Level 3: Secret, Level 5: Top Secret).
- **Manual Ingestion Modal:** Interface to ingest new knowledge chunks with source references, category tags, and required clearance levels.

---

## Design System Tokens

The studio is built on a software-craft dark-canvas design system defined in `src/index.css`:

```css
/* Surface Elevation Ladder */
--canvas: #010102;        /* Pure baseline canvas */
--surface-1: #0f1011;      /* Cards, panels, input bars */
--surface-2: #141517;      /* Hover states, secondary pills */
--surface-3: #18191b;      /* Nested containers, active toggles */
--surface-4: #1d1e21;      /* Elevated dropdowns, modals */

/* Hairline Borders */
--hairline: #23252a;       /* Standard structural border */
--hairline-strong: #2e3036;/* Focus rings, active cards */

/* Accent & Ink */
--primary: #5e6ad2;        /* Lavender brand accent */
--ink: #f7f8f8;            /* Primary display text */
--ink-muted: #d0d3d8;      /* Secondary reading text */
--ink-subtle: #8a8f98;     /* Metadata, placeholders, labels */
--ink-tertiary: #62666d;   /* Disabled states, micro hints */

/* Semantic Status */
--semantic-success: #27a644;
--semantic-warning: #f5a800;
--semantic-danger: #e6522c;
```

---

## Getting Started

### Prerequisites
- **Node.js:** v20.0+ (v24 LTS recommended)
- **npm:** v10.0+

### Installation
```bash
cd frontend
npm install
```

### Environment Configuration
Configure client-side endpoints in `.env` (derived from `.env.example`):
```env
# Java 21 Governance Gateway Base URL
VITE_API_BASE_URL=http://localhost:8080

# Distributed APM & Telemetry Dashboards
VITE_JAEGER_URL=http://localhost:16686
VITE_LANGFUSE_URL=http://localhost:3100
VITE_PROMETHEUS_URL=http://localhost:9090
VITE_GRAFANA_URL=http://localhost:3000
```

### Development Server
```bash
npm run dev
# Starts local development server on http://localhost:5173
```

### Quality Verification (Linting & Production Build)
```bash
# Run Oxlint static analysis
npm run lint

# Compile production-ready bundle
npm run build

# Preview production build locally
npm run preview
```

---

## API Gateway Contract

The frontend connects directly to the Java 21 Spring Boot Governance Gateway:

- **Target Endpoints:**
  - `POST http://localhost:8080/api/v1/cognition/query` (Authoritative guarded query execution)
  - `POST http://localhost:8080/api/v1/cognition/stream` (Real-time SSE token stream)
  - `GET http://localhost:8080/api/v1/cognition/audit-logs?limit=15` (Live cryptographic audit trail)
- **Query Request Headers:**
  - `Content-Type: application/json`
  - `X-Tenant-Id: <tenant-identifier>`
  - `X-Clearance-Level: <INTERNAL | CONFIDENTIAL | TOP_SECRET>`
- **Request Payload:**
  ```json
  {
    "prompt": "What is the domestic flight reimbursement limit?",
    "threadId": "thread-web-user",
    "userId": "enterprise-web-client"
  }
  ```
- **Response Format:**
  ```json
  {
    "answer": "Domestic flights are reimbursed up to $500 per round-trip flight...",
    "traceId": "013fa746ecf54713b71358b96d37326a",
    "guardrailStatus": "CLEAN",
    "groundingScore": 1.0,
    "latencyMs": 842,
    "citations": [
      {
        "sourceReference": "Corporate Travel Policy Section 4.1",
        "confidence": 0.98,
        "rrfScore": 0.0333,
        "memoryId": "mem-001"
      }
    ]
  }
  ```

---

## Author

**Jayavignesh**
- Website: [jayavignesh.dev](https://jayavignesh.dev)
- GitHub: [@i-viki](https://github.com/i-viki)
- Email: [hello@jayavignesh.dev](mailto:hello@jayavignesh.dev)

---

## License

Distributed under the **MIT License**. See the root [`LICENSE`](../LICENSE) file for complete terms.
