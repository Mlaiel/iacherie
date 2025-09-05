"""Edge CDN Integration
====================

Advanced Content Delivery Network integration for edge computing,
providing intelligent content caching, distribution, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import aiohttp
import aiofiles
import json
import os

logger = logging.getLogger(__name__)


class CDNStrategy(str, Enum):
    """CDN caching strategies."""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"
    CONTENT_AWARE = "content_aware"
    USER_BEHAVIOR = "user_behavior"


class CachePolicy(str, Enum):
    """Cache policies for content."""
    NO_CACHE = "no_cache"
    CACHE_ALWAYS = "cache_always"
    CACHE_CONDITIONAL = "cache_conditional"
    CACHE_PRIVATE = "cache_private"
    CACHE_PUBLIC = "cache_public"


class ContentType(str, Enum):
    """Content types for CDN."""
    HTML = "text/html"
    CSS = "text/css"
    JAVASCRIPT = "application/javascript"
    IMAGE = "image/*"
    VIDEO = "video/*"
    AUDIO = "audio/*"
    JSON = "application/json"
    BINARY = "application/octet-stream"


@dataclass
class ContentOrigin:
    """Content origin configuration."""
    origin_id: str
    host: str
    port: int = 443
    protocol: str = "https"
    backup_origins: List[str] = field(default_factory=list)
    health_check_path: str = "/health"
    timeout: int = 30


@dataclass
class CDNConfig:
    """CDN configuration."""
    cdn_id: str
    name: str
    strategy: CDNStrategy
    origins: List[ContentOrigin]
    cache_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    ttl_default: int = 3600  # 1 hour
    ttl_by_type: Dict[ContentType, int] = field(default_factory=dict)
    compression_enabled: bool = True
    prefetch_enabled: bool = True


class EdgeCDN:
    """Advanced edge CDN with intelligent caching and optimization."""
    
    def __init__(self, config: CDNConfig):
        self.config = config
        
        # Content storage
        self.cache_dir = f"/tmp/edge_cdn_{config.cdn_id}"
        self.content_index: Dict[str, Dict[str, Any]] = {}
        self.content_stats: Dict[str, Dict[str, int]] = {}
        
        # Cache management
        self.cache_size_used = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Request routing
        self.origin_health: Dict[str, bool] = {}
        self.origin_response_times: Dict[str, List[float]] = {}
        
        # Background tasks
        self.prefetch_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Analytics
        self.request_analytics: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        
        # Control flags
        self.running = False
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"EdgeCDN initialized: {config.name}")
    
    async def start(self):
        """Start the edge CDN system."""
        if self.running:
            logger.warning("Edge CDN already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if self.config.prefetch_enabled:
            self.prefetch_task = asyncio.create_task(self._prefetch_loop())
        
        # Initialize origin health
        await self._check_origin_health()
        
        logger.info("Edge CDN started")
    
    async def stop(self):
        """Stop the edge CDN system."""
        self.running = False
        
        # Cancel background tasks
        tasks = [self.health_check_task, self.cleanup_task, self.prefetch_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge CDN stopped")
    
    async def get_content(self, path: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Get content from CDN cache or origin."""
        
        content_key = self._generate_content_key(path, headers)
        start_time = time.time()
        
        try:
            # Check cache first
            cached_content = await self._get_from_cache(content_key)
            if cached_content:
                self.cache_hits += 1
                self._update_content_stats(path, "hit")
                
                response_time = time.time() - start_time
                self._update_performance_metrics("cache_response_time", response_time)
                
                return cached_content
            
            # Cache miss - fetch from origin
            self.cache_misses += 1
            self._update_content_stats(path, "miss")
            
            content = await self._fetch_from_origin(path, headers)
            if content:
                # Cache the content
                await self._store_in_cache(content_key, content, path)
                
                response_time = time.time() - start_time
                self._update_performance_metrics("origin_response_time", response_time)
                
                return content
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get content {path}: {e}")
            return None
    
    async def invalidate_content(self, path: str, pattern: Optional[str] = None) -> int:
        """Invalidate cached content."""
        
        invalidated_count = 0
        
        try:
            if pattern:
                # Invalidate by pattern
                keys_to_invalidate = [
                    key for key in self.content_index.keys()
                    if pattern in key or path in self.content_index[key].get('original_path', '')
                ]
            else:
                # Invalidate specific path
                content_key = self._generate_content_key(path)
                keys_to_invalidate = [content_key] if content_key in self.content_index else []
            
            for key in keys_to_invalidate:
                if await self._remove_from_cache(key):
                    invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} cached items for path: {path}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate content {path}: {e}")
            return 0
    
    async def prefetch_content(self, paths: List[str], priority: int = 1) -> int:
        """Prefetch content to cache."""
        
        prefetched_count = 0
        
        for path in paths:
            try:
                content_key = self._generate_content_key(path)
                
                # Skip if already cached
                if content_key in self.content_index:
                    continue
                
                # Fetch and cache
                content = await self._fetch_from_origin(path)
                if content:
                    await self._store_in_cache(content_key, content, path)
                    prefetched_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to prefetch content {path}: {e}")
        
        logger.info(f"Prefetched {prefetched_count} content items")
        return prefetched_count
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get CDN analytics and performance metrics."""
        
        total_requests = self.cache_hits + self.cache_misses
        hit_ratio = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        analytics = {
            'cache_performance': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_ratio': hit_ratio,
                'cache_size_used': self.cache_size_used,
                'cache_size_limit': self.config.cache_size,
                'utilization': (self.cache_size_used / self.config.cache_size * 100)
            },
            'origin_health': self.origin_health.copy(),
            'performance_metrics': self.performance_metrics.copy(),
            'content_stats': self._get_top_content_stats(),
            'bandwidth_saved': self._calculate_bandwidth_saved()
        }
        
        return analytics
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache based on usage patterns."""
        
        optimization_results = {
            'actions_taken': [],
            'cache_freed': 0,
            'performance_improvement': 0
        }
        
        try:
            # Remove least recently used content if cache is full
            if self.cache_size_used > self.config.cache_size * 0.9:
                freed_space = await self._evict_lru_content()
                optimization_results['cache_freed'] = freed_space
                optimization_results['actions_taken'].append(f"Freed {freed_space} bytes from cache")
            
            # Prefetch popular content
            if self.config.prefetch_enabled:
                popular_paths = self._get_popular_content_paths()
                prefetched = await self.prefetch_content(popular_paths[:10])
                if prefetched > 0:
                    optimization_results['actions_taken'].append(f"Prefetched {prefetched} popular items")
            
            # Update TTL based on content popularity
            await self._update_dynamic_ttl()
            optimization_results['actions_taken'].append("Updated dynamic TTL")
            
            logger.info(f"Cache optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return optimization_results
    
    # Private methods
    
    def _generate_content_key(self, path: str, headers: Optional[Dict[str, str]] = None) -> str:
        """Generate cache key for content."""
        
        key_data = path
        
        # Include relevant headers in key
        if headers:
            relevant_headers = ['accept-encoding', 'accept', 'user-agent']
            header_parts = []
            for header in relevant_headers:
                if header in headers:
                    header_parts.append(f"{header}:{headers[header]}")
            
            if header_parts:
                key_data += "?" + "&".join(header_parts)
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_from_cache(self, content_key: str) -> Optional[Dict[str, Any]]:
        """Get content from cache."""
        
        try:
            if content_key not in self.content_index:
                return None
            
            cache_info = self.content_index[content_key]
            
            # Check if expired
            if cache_info['expires_at'] < datetime.now():
                await self._remove_from_cache(content_key)
                return None
            
            # Read content from disk
            file_path = cache_info['file_path']
            
            if not os.path.exists(file_path):
                # File missing, remove from index
                await self._remove_from_cache(content_key)
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                content_data = await f.read()
            
            # Update access time
            cache_info['last_accessed'] = datetime.now()
            cache_info['access_count'] += 1
            
            return {
                'content': content_data,
                'content_type': cache_info['content_type'],
                'headers': cache_info.get('headers', {}),
                'from_cache': True
            }
            
        except Exception as e:
            logger.error(f"Failed to get content from cache: {e}")
            return None
    
    async def _fetch_from_origin(self, path: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch content from origin server."""
        
        # Select best origin
        origin = await self._select_best_origin()
        if not origin:
            logger.error("No healthy origin available")
            return None
        
        try:
            url = f"{origin.protocol}://{origin.host}:{origin.port}{path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=origin.timeout)) as response:
                    if response.status == 200:
                        content_data = await response.read()
                        
                        return {
                            'content': content_data,
                            'content_type': response.headers.get('content-type', 'application/octet-stream'),
                            'headers': dict(response.headers),
                            'from_cache': False,
                            'origin_id': origin.origin_id
                        }
                    else:
                        logger.warning(f"Origin returned status {response.status} for {path}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to fetch from origin {origin.host}: {e}")
            
            # Mark origin as unhealthy
            self.origin_health[origin.origin_id] = False
            
            return None
    
    async def _store_in_cache(self, content_key: str, content: Dict[str, Any], original_path: str):
        """Store content in cache."""
        
        try:
            content_data = content['content']
            content_size = len(content_data)
            
            # Check if we have space
            if self.cache_size_used + content_size > self.config.cache_size:
                # Try to free some space
                await self._evict_lru_content(content_size)
            
            # Still no space?
            if self.cache_size_used + content_size > self.config.cache_size:
                logger.warning(f"Cannot cache content, insufficient space: {content_size} bytes")
                return
            
            # Store content to disk
            file_path = os.path.join(self.cache_dir, content_key)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content_data)
            
            # Determine TTL
            ttl = self._get_content_ttl(content['content_type'], original_path)
            
            # Add to index
            self.content_index[content_key] = {
                'file_path': file_path,
                'content_type': content['content_type'],
                'headers': content.get('headers', {}),
                'size': content_size,
                'created_at': datetime.now(),
                'last_accessed': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl),
                'access_count': 1,
                'original_path': original_path
            }
            
            self.cache_size_used += content_size
            
            logger.debug(f"Cached content: {original_path} ({content_size} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to store content in cache: {e}")
    
    async def _remove_from_cache(self, content_key: str) -> bool:
        """Remove content from cache."""
        
        try:
            if content_key not in self.content_index:
                return False
            
            cache_info = self.content_index[content_key]
            
            # Remove file
            if os.path.exists(cache_info['file_path']):
                os.remove(cache_info['file_path'])
            
            # Update size
            self.cache_size_used -= cache_info['size']
            
            # Remove from index
            del self.content_index[content_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove content from cache: {e}")
            return False
    
    async def _select_best_origin(self) -> Optional[ContentOrigin]:
        """Select the best available origin server."""
        
        healthy_origins = [
            origin for origin in self.config.origins
            if self.origin_health.get(origin.origin_id, True)
        ]
        
        if not healthy_origins:
            # Try backup origins
            for origin in self.config.origins:
                if origin.backup_origins:
                    # Create temporary origin from backup
                    backup_host = origin.backup_origins[0]
                    return ContentOrigin(
                        origin_id=f"{origin.origin_id}_backup",
                        host=backup_host,
                        port=origin.port,
                        protocol=origin.protocol
                    )
            return None
        
        # Select origin with best response time
        best_origin = healthy_origins[0]
        best_response_time = float('inf')
        
        for origin in healthy_origins:
            response_times = self.origin_response_times.get(origin.origin_id, [])
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time < best_response_time:
                    best_response_time = avg_response_time
                    best_origin = origin
        
        return best_origin
    
    def _get_content_ttl(self, content_type: str, path: str) -> int:
        """Get TTL for content based on type and path."""
        
        # Check type-specific TTL
        for ctype, ttl in self.config.ttl_by_type.items():
            if ctype.value in content_type:
                return ttl
        
        # Check path-based rules
        if path.endswith(('.js', '.css')):
            return 86400  # 24 hours for static assets
        elif path.endswith(('.jpg', '.png', '.gif', '.ico')):
            return 604800  # 1 week for images
        elif path.endswith('.html'):
            return 300  # 5 minutes for HTML
        
        return self.config.ttl_default
    
    async def _evict_lru_content(self, space_needed: Optional[int] = None) -> int:
        """Evict least recently used content."""
        
        space_needed = space_needed or (self.config.cache_size * 0.1)  # Free 10% by default
        space_freed = 0
        
        # Sort by last accessed time
        sorted_content = sorted(
            self.content_index.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        for content_key, cache_info in sorted_content:
            if space_freed >= space_needed:
                break
            
            if await self._remove_from_cache(content_key):
                space_freed += cache_info['size']
        
        logger.info(f"Evicted LRU content, freed {space_freed} bytes")
        return space_freed
    
    def _update_content_stats(self, path: str, event_type: str):
        """Update content access statistics."""
        
        if path not in self.content_stats:
            self.content_stats[path] = {'hits': 0, 'misses': 0, 'requests': 0}
        
        self.content_stats[path][event_type + 's'] += 1
        self.content_stats[path]['requests'] += 1
    
    def _update_performance_metrics(self, metric_name: str, value: float):
        """Update performance metrics."""
        
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = value
        else:
            # Calculate moving average
            self.performance_metrics[metric_name] = (
                self.performance_metrics[metric_name] * 0.9 + value * 0.1
            )
    
    def _get_top_content_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top content by request count."""
        
        sorted_stats = sorted(
            self.content_stats.items(),
            key=lambda x: x[1]['requests'],
            reverse=True
        )
        
        return [
            {
                'path': path,
                'requests': stats['requests'],
                'hits': stats['hits'],
                'misses': stats['misses'],
                'hit_ratio': (stats['hits'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
            }
            for path, stats in sorted_stats[:limit]
        ]
    
    def _get_popular_content_paths(self, limit: int = 20) -> List[str]:
        """Get paths of popular content for prefetching."""
        
        popular_paths = []
        
        sorted_stats = sorted(
            self.content_stats.items(),
            key=lambda x: x[1]['requests'],
            reverse=True
        )
        
        for path, stats in sorted_stats[:limit]:
            # Only include if not already cached
            content_key = self._generate_content_key(path)
            if content_key not in self.content_index:
                popular_paths.append(path)
        
        return popular_paths
    
    def _calculate_bandwidth_saved(self) -> int:
        """Calculate bandwidth saved by caching."""
        
        bandwidth_saved = 0
        
        for content_key, cache_info in self.content_index.items():
            # Bandwidth saved = size * (access_count - 1)
            bandwidth_saved += cache_info['size'] * (cache_info['access_count'] - 1)
        
        return bandwidth_saved
    
    async def _update_dynamic_ttl(self):
        """Update TTL based on content popularity."""
        
        for content_key, cache_info in self.content_index.items():
            access_count = cache_info['access_count']
            
            # Increase TTL for popular content
            if access_count > 10:
                new_ttl = min(86400, self.config.ttl_default * 2)  # Max 24 hours
                cache_info['expires_at'] = cache_info['created_at'] + timedelta(seconds=new_ttl)
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while self.running:
            try:
                await self._check_origin_health()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self.running:
            try:
                await self._cleanup_expired_content()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _prefetch_loop(self):
        """Background prefetch loop."""
        while self.running:
            try:
                # Prefetch popular content
                popular_paths = self._get_popular_content_paths(5)
                if popular_paths:
                    await self.prefetch_content(popular_paths)
                
                await asyncio.sleep(600)  # Prefetch every 10 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in prefetch loop: {e}")
                await asyncio.sleep(600)
    
    async def _check_origin_health(self):
        """Check health of all origin servers."""
        
        for origin in self.config.origins:
            try:
                health_url = f"{origin.protocol}://{origin.host}:{origin.port}{origin.health_check_path}"
                
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            self.origin_health[origin.origin_id] = True
                            
                            # Update response time tracking
                            if origin.origin_id not in self.origin_response_times:
                                self.origin_response_times[origin.origin_id] = []
                            
                            self.origin_response_times[origin.origin_id].append(response_time)
                            
                            # Keep only recent response times
                            if len(self.origin_response_times[origin.origin_id]) > 10:
                                self.origin_response_times[origin.origin_id] = self.origin_response_times[origin.origin_id][-10:]
                        else:
                            self.origin_health[origin.origin_id] = False
                            
            except Exception as e:
                logger.warning(f"Health check failed for origin {origin.host}: {e}")
                self.origin_health[origin.origin_id] = False
    
    async def _cleanup_expired_content(self):
        """Clean up expired content from cache."""
        
        expired_keys = []
        current_time = datetime.now()
        
        for content_key, cache_info in self.content_index.items():
            if cache_info['expires_at'] < current_time:
                expired_keys.append(content_key)
        
        for key in expired_keys:
            await self._remove_from_cache(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired content items")


def create_edge_cdn(config: CDNConfig) -> EdgeCDN:
    """Create and configure an edge CDN instance."""
    return EdgeCDN(config)


# Example usage and testing
if __name__ == "__main__":
    async def test_edge_cdn():
        """Test the edge CDN."""
        
        # Create origins
        origins = [
            ContentOrigin(
                origin_id="primary",
                host="example.com",
                port=443,
                protocol="https"
            )
        ]
        
        # Create CDN config
        config = CDNConfig(
            cdn_id="test_cdn",
            name="Test Edge CDN",
            strategy=CDNStrategy.ADAPTIVE,
            origins=origins,
            cache_size=100 * 1024 * 1024  # 100MB
        )
        
        # Create and start CDN
        cdn = create_edge_cdn(config)
        await cdn.start()
        
        # Test content retrieval (would normally fetch from real origin)
        print("CDN test completed - would need real origin for full test")
        
        # Get analytics
        analytics = await cdn.get_analytics()
        print(f"CDN analytics: {analytics}")
        
        # Stop CDN
        await cdn.stop()
    
    # Run test
    asyncio.run(test_edge_cdn())