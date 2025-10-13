"""
Model Cache
Caches AI model responses to reduce API calls and costs
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ModelCache:
    """Cache AI model responses"""
    
    def __init__(self):
        self.enabled = os.getenv('AI_CACHE_ENABLED', 'true').lower() == 'true'
        self.ttl = int(os.getenv('AI_CACHE_TTL', '3600'))  # 1 hour default
        
        # In production, use Redis for caching
        # import redis
        # self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        
        # For now, use in-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_cache_key(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_message: Optional[str] = None
    ) -> str:
        """Generate cache key from request parameters"""
        key_data = {
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'system_message': system_message
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature setting
            max_tokens: Max tokens
            system_message: System message
            
        Returns:
            Cached response or None
        """
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key(
            prompt, model, temperature, max_tokens, system_message
        )
        
        # In production with Redis:
        # cached_data = self.redis_client.get(cache_key)
        # if cached_data:
        #     return json.loads(cached_data)
        
        # In-memory cache
        cached_entry = self._cache.get(cache_key)
        if cached_entry:
            # Check if expired
            expires_at = cached_entry.get('expires_at')
            if expires_at and datetime.fromisoformat(expires_at) > datetime.utcnow():
                print(f"[AI Cache] Hit for key: {cache_key[:16]}...")
                return cached_entry['response']
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        
        return None
    
    async def set(
        self,
        prompt: str,
        model: str,
        response: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache AI response
        
        Args:
            prompt: User prompt
            model: Model name
            response: AI response to cache
            temperature: Temperature setting
            max_tokens: Max tokens
            system_message: System message
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False
        
        cache_key = self._generate_cache_key(
            prompt, model, temperature, max_tokens, system_message
        )
        
        ttl = ttl or self.ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        # In production with Redis:
        # self.redis_client.setex(
        #     cache_key,
        #     ttl,
        #     json.dumps(response)
        # )
        
        # In-memory cache
        self._cache[cache_key] = {
            'response': response,
            'expires_at': expires_at.isoformat(),
            'cached_at': datetime.utcnow().isoformat()
        }
        
        print(f"[AI Cache] Set for key: {cache_key[:16]}... (TTL: {ttl}s)")
        return True
    
    async def invalidate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None
    ) -> bool:
        """
        Invalidate cached response
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature setting
            max_tokens: Max tokens
            system_message: System message
            
        Returns:
            True if invalidated
        """
        if not self.enabled:
            return False
        
        cache_key = self._generate_cache_key(
            prompt, model, temperature, max_tokens, system_message
        )
        
        # In production with Redis:
        # self.redis_client.delete(cache_key)
        
        # In-memory cache
        if cache_key in self._cache:
            del self._cache[cache_key]
            print(f"[AI Cache] Invalidated key: {cache_key[:16]}...")
            return True
        
        return False
    
    async def clear_all(self) -> bool:
        """Clear all cached responses"""
        if not self.enabled:
            return False
        
        # In production with Redis:
        # self.redis_client.flushdb()
        
        # In-memory cache
        self._cache.clear()
        print("[AI Cache] Cleared all cache")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'enabled': self.enabled,
            'ttl': self.ttl,
            'entries_count': len(self._cache),
            'cache_type': 'in-memory'  # or 'redis' in production
        }
