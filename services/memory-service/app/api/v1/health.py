from fastapi import APIRouter
from app.core.database import db
from app.core.redis_client import redis_client
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Returns operational health status across DB, Redis, and Model components."""
    db_healthy = await db.check_health()
    
    return {
        "status": "UP" if db_healthy else "DEGRADED",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_connected": db_healthy,
        "redis_connected": redis_client.is_connected,
        "model_runtime": {
            "provider": settings.LLM_PROVIDER,
            "llm": settings.LLM_MODEL_NAME,
            "embeddings": settings.EMBEDDING_MODEL_NAME,
            "guard": settings.GUARD_MODEL_NAME
        }
    }

