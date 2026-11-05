import redis.asyncio as aioredis
import structlog
from typing import Optional, Any
import json
from app.config import settings

logger = structlog.get_logger(__name__)

class RedisClientManager:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self.is_connected: bool = False

    async def connect(self):
        if not settings.REDIS_ENABLED:
            logger.info("redis_disabled_by_config")
            return

        try:
            import asyncio
            self.client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
            )
            # Test ping with strict 1s timeout
            await asyncio.wait_for(self.client.ping(), timeout=1.0)
            self.is_connected = True
            logger.info("redis_connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        except Exception as e:
            logger.warn("redis_connection_failed_fallback_mode", error=str(e))
            self.is_connected = False
            self.client = None

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("redis_disconnected")

    async def get_json(self, key: str) -> Optional[Any]:
        if not self.is_connected or not self.client:
            return None
        try:
            val = await self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 900) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            payload = json.dumps(value)
            await self.client.set(key, payload, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception:
            return False


redis_client = RedisClientManager()

