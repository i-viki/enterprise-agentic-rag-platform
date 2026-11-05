from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.config import settings
from app.core.database import db
from app.core.redis_client import redis_client
from app.core.telemetry import setup_telemetry
from app.api.v1.health import router as health_router
from app.api.v1.memories import router as memories_router
from app.api.v1.cognition import router as cognition_router

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("service_starting", app=settings.APP_NAME, port=settings.PORT)
    await db.connect()
    await redis_client.connect()
    yield
    # Shutdown
    logger.info("service_shutting_down")
    await db.disconnect()
    await redis_client.disconnect()

app = FastAPI(
    title="Hybrid Retrieval & Memory Engine",
    description="Enterprise Agentic RAG Cognitive Memory, pgvector HNSW + BM25 RRF, and LangGraph Engine",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup OpenTelemetry & Prometheus
setup_telemetry(app)

# Include API Routers
app.include_router(health_router)
app.include_router(memories_router)
app.include_router(cognition_router)

@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics"
    }

