import asyncpg
from pgvector.asyncpg import register_vector
import structlog
from typing import Optional
from app.config import settings

logger = structlog.get_logger(__name__)

class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initializes the asyncpg connection pool with pgvector type codecs."""
        try:
            async def init_connection(conn):
                # Register pgvector type codec for every connection in the pool
                await register_vector(conn)

            self.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                init=init_connection,
                timeout=2.0,
            )
            logger.info(
                "postgres_pool_initialized",
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
            )
        except Exception as e:
            logger.error("postgres_connection_failed", error=str(e))
            self.pool = None

    async def disconnect(self):
        """Gracefully closes all pool connections."""
        if self.pool:
            await self.pool.close()
            logger.info("postgres_pool_closed")

    async def get_connection(self) -> asyncpg.Connection:
        if not self.pool:
            raise RuntimeError("Database connection pool is not initialized.")
        return await self.pool.acquire()

    async def release_connection(self, connection: asyncpg.Connection):
        if self.pool and connection:
            await self.pool.release(connection)

    async def check_health(self) -> bool:
        """Runs a quick SELECT 1 health check."""
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT 1;")
                return val == 1
        except Exception:
            return False


db = DatabasePool()

