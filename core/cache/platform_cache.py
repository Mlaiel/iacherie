"""Platform Cache for IA Influencer Agent Platform
Specialized caching for external platform APIs and rate limiting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .redis_cache import RedisCache, RedisConfig
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"

class APIEndpoint(Enum):
    """API endpoint types"""    USER_PROFILE = "user_profile"
    CONTENT_LIST = "content_list"
    ANALYTICS = "analytics"
    UPLOAD = "upload"
    SEARCH = "search"
    TRENDS = "trends"
    RECOMMENDATIONS = "recommendations"

@dataclass
class APIResponse:
    """Cached API response structure"""    platform: Platform
    endpoint: APIEndpoint
    request_params: Dict[str, Any]
    response_data: Dict[str, Any]
    status_code: int
    cached_at: datetime
    expires_at: datetime
    response_time: float
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['platform'] = self.platform.value
        data['endpoint'] = self.endpoint.value
        data['cached_at'] = self.cached_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIResponse':
        """Create from dictionary"""        data['platform'] = Platform(data['platform'])
        data['endpoint'] = APIEndpoint(data['endpoint'])
        data['cached_at'] = datetime.fromisoformat(data['cached_at'])
        data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    @property
    def is_expired(self) -> bool:
        """Check if response is expired"""        return datetime.utcnow() > self.expires_at

@dataclass
class RateLimitInfo:
    """Rate limiting information"""    platform: Platform
    endpoint: APIEndpoint
    requests_made: int
    requests_limit: int
    window_start: datetime
    window_duration: timedelta
    reset_at: datetime
    
    @property
    def requests_remaining(self) -> int:
        """Get remaining requests in current window"""        return max(0, self.requests_limit - self.requests_made)
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if rate limited"""        return self.requests_made >= self.requests_limit and datetime.utcnow() < self.reset_at

class PlatformCache:
    """    Advanced platform cache for external API responses and rate limiting
    Handles caching for multiple platforms with intelligent TTL management
    """    
    def __init__(self,
                 redis_config: RedisConfig,
                 default_ttl: int = 3600,  # 1 hour
                 rate_limit_window: int = 3600):  # 1 hour
        
        self.default_ttl = default_ttl
        self.rate_limit_window = rate_limit_window
        
        # Initialize caches
        self.redis_cache = RedisCache(redis_config)
        self.memory_cache = MemoryCache(
            max_size=5000,
            default_ttl=300  # 5 minutes for memory cache
        )
        
        # Cache key prefixes
        self.API_RESPONSE_PREFIX = "platform:api"
        self.RATE_LIMIT_PREFIX = "platform:rate_limit"
        self.USER_TOKEN_PREFIX = "platform:token"
        self.TRENDS_PREFIX = "platform:trends"
        self.SEARCH_PREFIX = "platform:search"
        
        # Platform-specific TTL configurations
        self.platform_ttls = {
            Platform.SPOTIFY: {
                APIEndpoint.USER_PROFILE: 3600,       # 1 hour
                APIEndpoint.CONTENT_LIST: 1800,       # 30 minutes
                APIEndpoint.ANALYTICS: 3600,          # 1 hour
                APIEndpoint.SEARCH: 1800,             # 30 minutes
                APIEndpoint.TRENDS: 7200,             # 2 hours
                APIEndpoint.RECOMMENDATIONS: 3600,    # 1 hour
            },
            Platform.YOUTUBE: {
                APIEndpoint.USER_PROFILE: 1800,       # 30 minutes
                APIEndpoint.CONTENT_LIST: 900,        # 15 minutes
                APIEndpoint.ANALYTICS: 1800,          # 30 minutes
                APIEndpoint.SEARCH: 1800,             # 30 minutes
                APIEndpoint.TRENDS: 3600,             # 1 hour
            },
            Platform.INSTAGRAM: {
                APIEndpoint.USER_PROFILE: 1800,       # 30 minutes
                APIEndpoint.CONTENT_LIST: 600,        # 10 minutes
                APIEndpoint.ANALYTICS: 3600,          # 1 hour
                APIEndpoint.SEARCH: 1800,             # 30 minutes
            },
            Platform.TIKTOK: {
                APIEndpoint.USER_PROFILE: 1800,       # 30 minutes
                APIEndpoint.CONTENT_LIST: 300,        # 5 minutes
                APIEndpoint.ANALYTICS: 3600,          # 1 hour
                APIEndpoint.TRENDS: 1800,             # 30 minutes
            }
        }
        
        # Rate limit configurations per platform
        self.rate_limits = {
            Platform.SPOTIFY: {
                APIEndpoint.USER_PROFILE: (100, 3600),      # 100 requests per hour
                APIEndpoint.CONTENT_LIST: (200, 3600),      # 200 requests per hour
                APIEndpoint.ANALYTICS: (50, 3600),          # 50 requests per hour
                APIEndpoint.SEARCH: (1000, 3600),           # 1000 requests per hour
            },
            Platform.YOUTUBE: {
                APIEndpoint.USER_PROFILE: (10000, 86400),   # 10k requests per day
                APIEndpoint.CONTENT_LIST: (10000, 86400),   # 10k requests per day
                APIEndpoint.ANALYTICS: (10000, 86400),      # 10k requests per day
                APIEndpoint.SEARCH: (10000, 86400),         # 10k requests per day
            },
            Platform.INSTAGRAM: {
                APIEndpoint.USER_PROFILE: (200, 3600),      # 200 requests per hour
                APIEndpoint.CONTENT_LIST: (200, 3600),      # 200 requests per hour
                APIEndpoint.ANALYTICS: (200, 3600),         # 200 requests per hour
            },
            Platform.TIKTOK: {
                APIEndpoint.USER_PROFILE: (100, 3600),      # 100 requests per hour
                APIEndpoint.CONTENT_LIST: (100, 3600),      # 100 requests per hour
                APIEndpoint.ANALYTICS: (100, 3600),         # 100 requests per hour
            }
        }
        
        # Statistics
        self._stats = {
            'api_requests_cached': 0,
            'api_requests_served': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'rate_limit_hits': 0,
            'expired_responses_cleaned': 0
        }
        
        logger.info("PlatformCache initialized")
    
    async def initialize(self):
        """Initialize cache connections"""        await self.redis_cache.connect()
    
    def _generate_cache_key(self,
                          platform: Platform,
                          endpoint: APIEndpoint,
                          params: Dict[str, Any],
                          user_id: Optional[str] = None) -> str:
        """Generate cache key for API request"""        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(sorted_params.encode()).hexdigest()
        
        key_parts = [
            self.API_RESPONSE_PREFIX,
            platform.value,
            endpoint.value,
            params_hash
        ]
        
        if user_id:
            key_parts.append(user_id)
        
        return ":".join(key_parts)
    
    def _get_ttl(self, platform: Platform, endpoint: APIEndpoint) -> int:
        """Get TTL for platform/endpoint combination"""        platform_config = self.platform_ttls.get(platform, {})
        return platform_config.get(endpoint, self.default_ttl)
    
    async def cache_api_response(self,
                               platform: Platform,
                               endpoint: APIEndpoint,
                               request_params: Dict[str, Any],
                               response_data: Dict[str, Any],
                               status_code: int,
                               response_time: float,
                               user_id: Optional[str] = None,
                               custom_ttl: Optional[int] = None) -> bool:
        """Cache API response"""        
        try:
            ttl = custom_ttl or self._get_ttl(platform, endpoint)
            cache_key = self._generate_cache_key(platform, endpoint, request_params, user_id)
            
            # Create API response object
            api_response = APIResponse(
                platform=platform,
                endpoint=endpoint,
                request_params=request_params,
                response_data=response_data,
                status_code=status_code,
                cached_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                response_time=response_time
            )
            
            # Store in Redis
            await self.redis_cache.set(
                cache_key,
                json.dumps(api_response.to_dict()),
                ttl=ttl
            )
            
            # Store in memory cache for faster access
            memory_ttl = min(ttl, 300)  # Max 5 minutes in memory
            self.memory_cache.set(cache_key, api_response, ttl=memory_ttl)
            
            self._stats['api_requests_cached'] += 1
            
            logger.debug(f"Cached API response: {platform.value}/{endpoint.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache API response: {e}")
            return False
    
    async def get_cached_response(self,
                                platform: Platform,
                                endpoint: APIEndpoint,
                                request_params: Dict[str, Any],
                                user_id: Optional[str] = None) -> Optional[APIResponse]:
        """Get cached API response"""        
        cache_key = self._generate_cache_key(platform, endpoint, request_params, user_id)
        
        # Try memory cache first
        cached_response = self.memory_cache.get(cache_key)
        if cached_response and not cached_response.is_expired:
            self._stats['cache_hits'] += 1
            self._stats['api_requests_served'] += 1
            return cached_response
        
        # Try Redis cache
        cached_data = await self.redis_cache.get(cache_key)
        if cached_data:
            try:
                response_dict = json.loads(cached_data)
                api_response = APIResponse.from_dict(response_dict)
                
                if not api_response.is_expired:
                    # Cache in memory for faster future access
                    self.memory_cache.set(cache_key, api_response, ttl=300)
                    
                    self._stats['cache_hits'] += 1
                    self._stats['api_requests_served'] += 1
                    return api_response
                else:
                    # Remove expired response
                    await self.redis_cache.delete(cache_key)
                    self._stats['expired_responses_cleaned'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to deserialize cached response: {e}")
        
        self._stats['cache_misses'] += 1
        return None
    
    async def check_rate_limit(self,
                             platform: Platform,
                             endpoint: APIEndpoint,
                             user_id: Optional[str] = None) -> RateLimitInfo:
        """Check rate limit for platform/endpoint"""        
        # Get rate limit configuration
        platform_limits = self.rate_limits.get(platform, {})
        if endpoint not in platform_limits:
            # Default rate limit
            requests_limit, window_duration = (1000, 3600)
        else:
            requests_limit, window_duration = platform_limits[endpoint]
        
        # Generate rate limit key
        rate_limit_key = f"{self.RATE_LIMIT_PREFIX}:{platform.value}:{endpoint.value}"
        if user_id:
            rate_limit_key += f":{user_id}"
        
        # Get current rate limit info
        rate_limit_data = await self.redis_cache.get(rate_limit_key)
        
        current_time = datetime.utcnow()
        
        if rate_limit_data:
            rate_limit_dict = json.loads(rate_limit_data)
            window_start = datetime.fromisoformat(rate_limit_dict['window_start'])
            requests_made = rate_limit_dict['requests_made']
            
            # Check if window has expired
            if current_time - window_start > timedelta(seconds=window_duration):
                # Reset window
                window_start = current_time
                requests_made = 0
        else:
            # First request in window
            window_start = current_time
            requests_made = 0
        
        # Create rate limit info
        rate_limit_info = RateLimitInfo(
            platform=platform,
            endpoint=endpoint,
            requests_made=requests_made,
            requests_limit=requests_limit,
            window_start=window_start,
            window_duration=timedelta(seconds=window_duration),
            reset_at=window_start + timedelta(seconds=window_duration)
        )
        
        return rate_limit_info
    
    async def increment_rate_limit(self,
                                 platform: Platform,
                                 endpoint: APIEndpoint,
                                 user_id: Optional[str] = None) -> bool:
        """Increment rate limit counter"""        
        try:
            rate_limit_info = await self.check_rate_limit(platform, endpoint, user_id)
            
            if rate_limit_info.is_rate_limited:
                self._stats['rate_limit_hits'] += 1
                return False
            
            # Generate rate limit key
            rate_limit_key = f"{self.RATE_LIMIT_PREFIX}:{platform.value}:{endpoint.value}"
            if user_id:
                rate_limit_key += f":{user_id}"
            
            # Update rate limit counter
            updated_data = {
                'platform': platform.value,
                'endpoint': endpoint.value,
                'requests_made': rate_limit_info.requests_made + 1,
                'requests_limit': rate_limit_info.requests_limit,
                'window_start': rate_limit_info.window_start.isoformat(),
                'user_id': user_id
            }
            
            window_remaining = int(rate_limit_info.window_duration.total_seconds())
            await self.redis_cache.set(
                rate_limit_key,
                json.dumps(updated_data),
                ttl=window_remaining
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment rate limit: {e}")
            return False
    
    async def store_user_token(self,
                             platform: Platform,
                             user_id: str,
                             token_data: Dict[str, Any],
                             expires_in: Optional[int] = None) -> bool:
        """Store user authentication token for platform"""        
        try:
            token_key = f"{self.USER_TOKEN_PREFIX}:{platform.value}:{user_id}"
            
            token_info = {
                'platform': platform.value,
                'user_id': user_id,
                'token_data': token_data,
                'stored_at': datetime.utcnow().isoformat(),
                'expires_in': expires_in
            }
            
            ttl = expires_in or 86400  # Default 24 hours
            await self.redis_cache.set(token_key, json.dumps(token_info), ttl=ttl)
            
            logger.info(f"Stored user token for {platform.value}: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store user token: {e}")
            return False
    
    async def get_user_token(self, platform: Platform, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user authentication token for platform"""        
        token_key = f"{self.USER_TOKEN_PREFIX}:{platform.value}:{user_id}"
        token_data = await self.redis_cache.get(token_key)
        
        if token_data:
            token_info = json.loads(token_data)
            return token_info['token_data']
        
        return None
    
    async def revoke_user_token(self, platform: Platform, user_id: str) -> bool:
        """Revoke user authentication token"""        
        token_key = f"{self.USER_TOKEN_PREFIX}:{platform.value}:{user_id}"
        return await self.redis_cache.delete(token_key)
    
    async def cache_trends_data(self,
                              platform: Platform,
                              trends_data: Dict[str, Any],
                              region: Optional[str] = None,
                              category: Optional[str] = None) -> bool:
        """Cache trending content data"""        
        try:
            trends_key = f"{self.TRENDS_PREFIX}:{platform.value}"
            if region:
                trends_key += f":{region}"
            if category:
                trends_key += f":{category}"
            
            trends_info = {
                'platform': platform.value,
                'data': trends_data,
                'region': region,
                'category': category,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            # Trends typically change less frequently
            ttl = self._get_ttl(platform, APIEndpoint.TRENDS)
            await self.redis_cache.set(trends_key, json.dumps(trends_info), ttl=ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache trends data: {e}")
            return False
    
    async def get_trends_data(self,
                            platform: Platform,
                            region: Optional[str] = None,
                            category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached trending content data"""        
        trends_key = f"{self.TRENDS_PREFIX}:{platform.value}"
        if region:
            trends_key += f":{region}"
        if category:
            trends_key += f":{category}"
        
        trends_data = await self.redis_cache.get(trends_key)
        
        if trends_data:
            trends_info = json.loads(trends_data)
            return trends_info['data']
        
        return None
    
    async def cache_search_results(self,
                                 platform: Platform,
                                 query: str,
                                 results: Dict[str, Any],
                                 search_type: Optional[str] = None) -> bool:
        """Cache search results"""        
        try:
            # Generate search key
            query_hash = hashlib.md5(query.encode()).hexdigest()
            search_key = f"{self.SEARCH_PREFIX}:{platform.value}:{query_hash}"
            if search_type:
                search_key += f":{search_type}"
            
            search_info = {
                'platform': platform.value,
                'query': query,
                'search_type': search_type,
                'results': results,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            ttl = self._get_ttl(platform, APIEndpoint.SEARCH)
            await self.redis_cache.set(search_key, json.dumps(search_info), ttl=ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache search results: {e}")
            return False
    
    async def get_search_results(self,
                               platform: Platform,
                               query: str,
                               search_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached search results"""        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        search_key = f"{self.SEARCH_PREFIX}:{platform.value}:{query_hash}"
        if search_type:
            search_key += f":{search_type}"
        
        search_data = await self.redis_cache.get(search_key)
        
        if search_data:
            search_info = json.loads(search_data)
            return search_info['results']
        
        return None
    
    async def invalidate_user_cache(self, platform: Platform, user_id: str):
        """Invalidate all cached data for a user on a platform"""        
        try:
            # Get all keys for this user/platform combination
            pattern = f"{self.API_RESPONSE_PREFIX}:{platform.value}:*:{user_id}"
            keys = await self.redis_cache.keys(pattern)
            
            # Delete all matching keys
            for key in keys:
                await self.redis_cache.delete(key)
                # Also remove from memory cache
                self.memory_cache.delete(key)
            
            logger.info(f"Invalidated cache for user {user_id} on {platform.value}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {e}")
    
    async def invalidate_platform_cache(self, platform: Platform):
        """Invalidate all cached data for a platform"""        
        try:
            # Get all keys for this platform
            pattern = f"{self.API_RESPONSE_PREFIX}:{platform.value}:*"
            keys = await self.redis_cache.keys(pattern)
            
            # Delete all matching keys
            for key in keys:
                await self.redis_cache.delete(key)
                self.memory_cache.delete(key)
            
            # Also clear trends and search cache
            trends_pattern = f"{self.TRENDS_PREFIX}:{platform.value}:*"
            trends_keys = await self.redis_cache.keys(trends_pattern)
            for key in trends_keys:
                await self.redis_cache.delete(key)
            
            search_pattern = f"{self.SEARCH_PREFIX}:{platform.value}:*"
            search_keys = await self.redis_cache.keys(search_pattern)
            for key in search_keys:
                await self.redis_cache.delete(key)
            
            logger.info(f"Invalidated all cache for platform {platform.value}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate platform cache: {e}")
    
    async def get_rate_limit_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limit status for all platforms"""        
        status = {}
        
        for platform in Platform:
            platform_status = {}
            
            for endpoint in APIEndpoint:
                if platform in self.rate_limits and endpoint in self.rate_limits[platform]:
                    rate_limit_info = await self.check_rate_limit(platform, endpoint, user_id)
                    platform_status[endpoint.value] = {
                        'requests_made': rate_limit_info.requests_made,
                        'requests_limit': rate_limit_info.requests_limit,
                        'requests_remaining': rate_limit_info.requests_remaining,
                        'reset_at': rate_limit_info.reset_at.isoformat(),
                        'is_rate_limited': rate_limit_info.is_rate_limited
                    }
            
            if platform_status:
                status[platform.value] = platform_status
        
        return status
    
    async def cleanup_expired_responses(self) -> int:
        """Clean up expired API responses"""        
        try:
            # Get all API response keys
            pattern = f"{self.API_RESPONSE_PREFIX}:*"
            keys = await self.redis_cache.keys(pattern)
            
            cleaned_count = 0
            
            for key in keys:
                cached_data = await self.redis_cache.get(key)
                if cached_data:
                    try:
                        response_dict = json.loads(cached_data)
                        api_response = APIResponse.from_dict(response_dict)
                        
                        if api_response.is_expired:
                            await self.redis_cache.delete(key)
                            self.memory_cache.delete(key)
                            cleaned_count += 1
                            
                    except Exception:
                        # Invalid data, remove it
                        await self.redis_cache.delete(key)
                        cleaned_count += 1
            
            self._stats['expired_responses_cleaned'] += cleaned_count
            logger.info(f"Cleaned up {cleaned_count} expired API responses")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired responses: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        
        return {
            'platform_stats': self._stats,
            'redis_stats': redis_stats,
            'memory_stats': memory_stats,
            'supported_platforms': [p.value for p in Platform],
            'rate_limit_windows': {
                p.value: {
                    e.value: f"{limit} requests per {window}s"
                    for e, (limit, window) in endpoints.items()
                }
                for p, endpoints in self.rate_limits.items()
            }
        }
    
    async def close(self):
        """Close cache connections"""        await self.redis_cache.close()
        self.memory_cache.close()

class APIResponseCache(PlatformCache):
    """    Simplified API response cache for general external API caching
    """    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def cache_response(self,
                           endpoint_url: str,
                           response_data: Dict[str, Any],
                           ttl: Optional[int] = None) -> bool:
        """Cache arbitrary API response"""        
        try:
            url_hash = hashlib.md5(endpoint_url.encode()).hexdigest()
            cache_key = f"api_response:{url_hash}"
            
            response_info = {
                'endpoint_url': endpoint_url,
                'response_data': response_data,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            cache_ttl = ttl or self.default_ttl
            await self.redis_cache.set(cache_key, json.dumps(response_info), ttl=cache_ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache API response: {e}")
            return False
    
    async def get_response(self, endpoint_url: str) -> Optional[Dict[str, Any]]:
        """Get cached API response"""        
        url_hash = hashlib.md5(endpoint_url.encode()).hexdigest()
        cache_key = f"api_response:{url_hash}"
        
        cached_data = await self.redis_cache.get(cache_key)
        
        if cached_data:
            response_info = json.loads(cached_data)
            return response_info['response_data']
        
        return None
