"""
Redis cache service for performance optimization
"""
import json
import hashlib
import logging
from typing import Optional, List, Dict, Any
from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for embeddings and search results"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        enabled: bool = True,
        ttl: int = 3600  # 1 hour default
    ):
        """
        Initialize cache service
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            enabled: Whether caching is enabled
            ttl: Time to live in seconds
        """
        self.enabled = enabled
        self.ttl = ttl
        self.client: Optional[Redis] = None
        
        if self.enabled:
            try:
                # Connect to Redis (password=None if not set)
                redis_kwargs = {
                    "host": host,
                    "port": port,
                    "db": db,
                    "decode_responses": False,  # We'll handle encoding
                    "socket_connect_timeout": 2,
                    "socket_timeout": 2
                }
                
                # Only add password if provided
                if password:
                    redis_kwargs["password"] = password
                
                self.client = Redis(**redis_kwargs)
                
                # Test connection
                self.client.ping()
                logger.info(f"Redis cache connected at {host}:{port}")
            except RedisError as e:
                logger.warning(f"Redis connection failed: {e}. Cache disabled.")
                self.enabled = False
                self.client = None
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create cache key from prefix and arguments"""
        # Create hash from arguments for consistent key length
        key_data = ":".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding for text
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding or None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            key = self._make_key("emb", text)
            cached = self.client.get(key)
            
            if cached:
                logger.debug(f"Cache HIT: embedding for '{text[:50]}...'")
                return json.loads(cached)
            
            logger.debug(f"Cache MISS: embedding for '{text[:50]}...'")
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set_embedding(self, text: str, embedding: List[float]) -> bool:
        """
        Cache embedding for text
        
        Args:
            text: Text
            embedding: Embedding vector
            
        Returns:
            Success status
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            key = self._make_key("emb", text)
            self.client.setex(
                key,
                self.ttl,
                json.dumps(embedding)
            )
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def get_search_results(
        self,
        query: str,
        product_code: str,
        tenant_id: str,
        limit: int,
        **kwargs
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached search results
        
        Args:
            query: Search query
            product_code: Product code
            tenant_id: Tenant ID
            limit: Result limit
            **kwargs: Additional search parameters
            
        Returns:
            Cached results or None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            # Include all parameters in cache key
            key = self._make_key(
                "search",
                query,
                product_code,
                tenant_id,
                limit,
                *sorted(kwargs.items())
            )
            cached = self.client.get(key)
            
            if cached:
                logger.debug(f"Cache HIT: search '{query}' in {product_code}")
                return json.loads(cached)
            
            logger.debug(f"Cache MISS: search '{query}' in {product_code}")
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set_search_results(
        self,
        query: str,
        product_code: str,
        tenant_id: str,
        limit: int,
        results: List[Dict[str, Any]],
        **kwargs
    ) -> bool:
        """
        Cache search results
        
        Args:
            query: Search query
            product_code: Product code
            tenant_id: Tenant ID
            limit: Result limit
            results: Search results to cache
            **kwargs: Additional search parameters
            
        Returns:
            Success status
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            key = self._make_key(
                "search",
                query,
                product_code,
                tenant_id,
                limit,
                *sorted(kwargs.items())
            )
            self.client.setex(
                key,
                self.ttl,
                json.dumps(results)
            )
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def invalidate_collection(self, product_code: str) -> bool:
        """
        Invalidate all cache for a collection
        
        Args:
            product_code: Product code
            
        Returns:
            Success status
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            # Find all keys for this collection
            pattern = f"search:*{product_code}*"
            keys = self.client.keys(pattern)
            
            if keys:
                self.client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for {product_code}")
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.flushdb()
            logger.info("Cleared all cache")
            return True
            
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.client:
            return {"enabled": False}
        
        try:
            info = self.client.info()
            return {
                "enabled": True,
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "total_keys": self.client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"enabled": True, "connected": False, "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round(hits / total * 100, 2)


# Global cache instance (will be initialized in main.py)
cache_service: Optional[CacheService] = None


def get_cache() -> Optional[CacheService]:
    """Get global cache instance"""
    return cache_service

