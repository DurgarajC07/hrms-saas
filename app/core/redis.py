import redis.asyncio as redis
from app.core.config import settings
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self):
        self.redis_pool = None
    
    async def init_redis(self):
        """Initialize Redis connection pool"""
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=100  # For high load
            )
            logger.info("Redis connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis connection"""
        if not self.redis_pool:
            await self.init_redis()
        return redis.Redis(connection_pool=self.redis_pool)
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600):
        """Set cache with expiration"""
        redis_client = await self.get_redis()
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
        finally:
            await redis_client.close()
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        redis_client = await self.get_redis()
        try:
            value = await redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
        finally:
            await redis_client.close()
    
    async def delete_cache(self, key: str):
        """Delete cache key"""
        redis_client = await self.get_redis()
        try:
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
        finally:
            await redis_client.close()
    
    async def set_session(self, session_id: str, data: dict, expire: int = 86400):
        """Set session data"""
        redis_client = await self.get_redis()
        try:
            await redis_client.select(settings.REDIS_SESSION_DB)
            await redis_client.set(f"session:{session_id}", json.dumps(data), ex=expire)
        except Exception as e:
            logger.error(f"Session set error: {e}")
        finally:
            await redis_client.close()
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        redis_client = await self.get_redis()
        try:
            await redis_client.select(settings.REDIS_SESSION_DB)
            data = await redis_client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Session get error: {e}")
            return None
        finally:
            await redis_client.close()


# Global Redis manager instance
redis_manager = RedisManager()
