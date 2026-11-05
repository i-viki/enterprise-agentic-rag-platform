from langfuse import Langfuse
import structlog
from typing import Optional, Dict, Any
from app.config import settings

logger = structlog.get_logger(__name__)


class LangfuseService:
    """Manages Langfuse telemetry tracing and generation monitoring."""

    def __init__(self):
        self._client: Optional[Langfuse] = None
        self._init_client()

    def _init_client(self):
        try:
            if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
                self._client = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
                logger.info("langfuse_initialized", host=settings.LANGFUSE_HOST)
        except Exception as e:
            logger.warning("langfuse_init_failed", error=str(e))
            self._client = None

    @property
    def client(self) -> Optional[Langfuse]:
        return self._client

    def create_trace(
        self,
        trace_id: str,
        name: str,
        user_id: str,
        session_id: str,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None
    ):
        if not self._client:
            return None
        try:
            return self._client.trace(
                id=trace_id,
                name=name,
                user_id=user_id,
                session_id=session_id,
                input=input_data,
                metadata=metadata or {},
                tags=tags or ["agentic-rag", "state-graph"]
            )
        except Exception as e:
            logger.warning("langfuse_trace_creation_failed", error=str(e))
            return None

    def flush(self):
        if self._client:
            try:
                self._client.flush()
            except Exception as e:
                logger.warning("langfuse_flush_failed", error=str(e))


langfuse_service = LangfuseService()

