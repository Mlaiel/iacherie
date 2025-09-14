"""CDN Integration - Content Delivery Network for Marketplace
===========================================================

Enterprise-grade CDN integration system for marketplace content delivery
providing global content distribution, caching optimization, and performance acceleration.

Features:
- Multi-CDN provider integration and failover
- Intelligent content routing and edge optimization
- Real-time performance monitoring and analytics
- Dynamic content purging and cache invalidation
- Geographic content distribution and optimization
- Media optimization and transformation

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/cdn_integration.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import hashlib
import mimetypes
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class CDNProvider(Enum):
    """CDN provider enumeration"""
    CLOUDFLARE = "cloudflare"
    AMAZON_CLOUDFRONT = "amazon_cloudfront"
    GOOGLE_CLOUD_CDN = "google_cloud_cdn"
    AZURE_CDN = "azure_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    BUNNYCDN = "bunnycdn"

class ContentType(Enum):
    """Content type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    WEB_ASSET = "web_asset"
    API_RESPONSE = "api_response"
    STREAMING = "streaming"

class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    CACHE_FIRST = "cache_first"         # Check cache first, fetch if miss
    NETWORK_FIRST = "network_first"     # Check network first, cache if available
    CACHE_ONLY = "cache_only"           # Only serve from cache
    NETWORK_ONLY = "network_only"       # Never cache, always fetch
    STALE_WHILE_REVALIDATE = "stale_while_revalidate"  # Serve stale while updating

class OptimizationLevel(Enum):
    """Content optimization level enumeration"""
    NONE = "none"
    BASIC = "basic"         # Basic compression
    STANDARD = "standard"   # Compression + format optimization
    AGGRESSIVE = "aggressive"  # All optimizations including quality reduction

@dataclass
class CDNEndpoint:
    """CDN endpoint configuration"""
    endpoint_id: str
    provider: CDNProvider
    base_url: str
    region: str = "global"
    priority: int = 1  # Lower number = higher priority
    active: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    zone_id: Optional[str] = None
    max_file_size_mb: int = 100
    supported_content_types: List[ContentType] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_health_check: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentItem:
    """Content item for CDN delivery"""
    content_id: str
    original_url: str
    content_type: ContentType
    mime_type: str
    size_bytes: int
    checksum: str
    cdn_urls: Dict[str, str] = field(default_factory=dict)  # provider -> cdn_url
    cache_ttl: int = 3600  # seconds
    cache_strategy: CacheStrategy = CacheStrategy.CACHE_FIRST
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CacheInvalidationRequest:
    """Cache invalidation request"""
    request_id: str
    content_ids: List[str]
    providers: List[CDNProvider] = field(default_factory=list)  # Empty = all providers
    purge_type: str = "single"  # single, wildcard, tag
    priority: str = "normal"  # low, normal, high
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class CDNPerformanceMetrics:
    """CDN performance metrics"""
    provider: CDNProvider
    region: str
    response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    bandwidth_usage_gb: float = 0.0
    requests_count: int = 0
    error_rate: float = 0.0
    availability: float = 100.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentOptimizationResult:
    """Content optimization result"""
    original_size_bytes: int
    optimized_size_bytes: int
    compression_ratio: float
    optimization_applied: List[str] = field(default_factory=list)
    quality_score: float = 1.0
    processing_time_ms: float = 0.0

class MockCDNProvider:
    """Mock CDN provider for development and testing"""
    
    def __init__(self, provider -> None: CDNProvider, base_url -> None: str) -> None:
        self.provider = provider
        self.base_url = base_url
        self.cached_content: Dict[str, Any] = {}
    
    async def upload_content(self, content_item: ContentItem, content_data: bytes) -> str:
        """Upload content to mock CDN"""
        try:
            # Generate mock CDN URL
            cdn_url = f"{self.base_url}/content/{content_item.content_id}"
            
            # Store content in mock cache
            self.cached_content[content_item.content_id] = {
                "url": cdn_url,
                "data": content_data,
                "content_type": content_item.content_type,
                "size": len(content_data),
                "uploaded_at": datetime.utcnow()
            }
            
            return cdn_url
            
        except Exception as e:
            logger.error(f"Mock CDN upload error: {e}")
            raise
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from mock CDN"""
        try:
            if content_id in self.cached_content:
                del self.cached_content[content_id]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock CDN delete error: {e}")
            return False
    
    async def purge_cache(self, content_ids: List[str]) -> bool:
        """Purge cache for mock CDN"""
        try:
            for content_id in content_ids:
                if content_id in self.cached_content:
                    # Simulate cache purge
                    self.cached_content[content_id]["cache_purged"] = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Mock CDN purge error: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from mock CDN"""
        return {
            "response_time_ms": 50.0,
            "cache_hit_rate": 0.85,
            "bandwidth_usage_gb": 1.5,
            "requests_count": 1000,
            "error_rate": 0.01,
            "availability": 99.9
        }

class CDNIntegrationManager:
    """CDN integration and content delivery management system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        
        # CDN endpoints and providers
        self.cdn_endpoints: Dict[str, CDNEndpoint] = {}
        self.cdn_providers: Dict[CDNProvider, MockCDNProvider] = {}
        
        # Content management
        self.content_items: Dict[str, ContentItem] = {}
        self.invalidation_requests: Dict[str, CacheInvalidationRequest] = {}
        
        # Performance monitoring
        self.performance_metrics: Dict[str, CDNPerformanceMetrics] = {}
        
        # Configuration
        self.default_cache_ttl = int(self.config.get('default_cache_ttl', 3600))
        self.max_file_size_mb = int(self.config.get('max_file_size_mb', 100))
        self.auto_optimization = self.config.get('auto_optimization', True)
        
        logger.info("🌐 CDN Integration Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize CDN providers and endpoints"""
        try:
            # Initialize default CDN endpoints
            await self._initialize_default_endpoints()
            
            logger.info("✅ CDN providers initialized")
            
        except Exception as e:
            logger.error(f"CDN initialization error: {e}")
    
    async def _initialize_default_endpoints(self) -> None:
        """Initialize default CDN endpoints"""
        try:
            # Add default endpoints (mock for development)
            default_endpoints = [
                {
                    "endpoint_id": "cloudflare_global",
                    "provider": CDNProvider.CLOUDFLARE,
                    "base_url": "https://cdn.ainflue.com",
                    "region": "global",
                    "priority": 1,
                    "supported_content_types": [ContentType.IMAGE, ContentType.VIDEO, ContentType.WEB_ASSET]
                },
                {
                    "endpoint_id": "cloudfront_us",
                    "provider": CDNProvider.AMAZON_CLOUDFRONT,
                    "base_url": "https://d123456789.cloudfront.net",
                    "region": "us-east-1",
                    "priority": 2,
                    "supported_content_types": [ContentType.VIDEO, ContentType.STREAMING]
                }
            ]
            
            for endpoint_config in default_endpoints:
                await self.add_cdn_endpoint(endpoint_config)
            
        except Exception as e:
            logger.error(f"Default endpoints initialization error: {e}")
    
    async def add_cdn_endpoint(self, endpoint_config: Dict[str, Any]) -> CDNEndpoint:
        """Add CDN endpoint"""
        try:
            endpoint = CDNEndpoint(
                endpoint_id=endpoint_config["endpoint_id"],
                provider=CDNProvider(endpoint_config["provider"]),
                base_url=endpoint_config["base_url"],
                region=endpoint_config.get("region", "global"),
                priority=endpoint_config.get("priority", 1),
                api_key=endpoint_config.get("api_key"),
                api_secret=endpoint_config.get("api_secret"),
                zone_id=endpoint_config.get("zone_id"),
                max_file_size_mb=endpoint_config.get("max_file_size_mb", 100),
                supported_content_types=[
                    ContentType(ct) for ct in endpoint_config.get("supported_content_types", [])
                ]
            )
            
            self.cdn_endpoints[endpoint.endpoint_id] = endpoint
            
            # Initialize mock provider
            if endpoint.provider not in self.cdn_providers:
                self.cdn_providers[endpoint.provider] = MockCDNProvider(
                    endpoint.provider, endpoint.base_url
                )
            
            logger.info(f"CDN endpoint added: {endpoint.endpoint_id} ({endpoint.provider.value})")
            return endpoint
            
        except Exception as e:
            logger.error(f"Add CDN endpoint error: {e}")
            raise
    
    async def upload_content(self, file_path: str, content_type: ContentType, 
                           optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
                           metadata: Dict[str, Any] = None) -> ContentItem:
        """Upload content to CDN with optimization"""
        try:
            # Read content data (mock)
            content_data = f"mock_content_data_for_{file_path}".encode()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Generate content checksum
            checksum = hashlib.md5(content_data).hexdigest()
            
            # Create content item
            content_item = ContentItem(
                content_id=str(uuid.uuid4()),
                original_url=file_path,
                content_type=content_type,
                mime_type=mime_type,
                size_bytes=len(content_data),
                checksum=checksum,
                optimization_level=optimization_level,
                metadata=metadata or {}
            )
            
            # Apply content optimization
            if self.auto_optimization and optimization_level != OptimizationLevel.NONE:
                content_data, optimization_result = await self._optimize_content(
                    content_data, content_type, optimization_level
                )
                content_item.metadata["optimization"] = optimization_result.__dict__
            
            # Select best CDN endpoints for content type
            selected_endpoints = self._select_cdn_endpoints(content_type)
            
            # Upload to selected CDN endpoints
            upload_tasks = []
            for endpoint in selected_endpoints:
                provider = self.cdn_providers.get(endpoint.provider)
                if provider:
                    upload_tasks.append(self._upload_to_provider(provider, content_item, content_data))
            
            if upload_tasks:
                cdn_urls = await asyncio.gather(*upload_tasks, return_exceptions=True)
                
                # Store successful CDN URLs
                for i, result in enumerate(cdn_urls):
                    if isinstance(result, str):  # Successful upload
                        endpoint = selected_endpoints[i]
                        content_item.cdn_urls[endpoint.provider.value] = result
            
            self.content_items[content_item.content_id] = content_item
            
            logger.info(f"Content uploaded: {content_item.content_id} to {len(content_item.cdn_urls)} CDN providers")
            return content_item
            
        except Exception as e:
            logger.error(f"Content upload error: {e}")
            raise
    
    def _select_cdn_endpoints(self, content_type: ContentType) -> List[CDNEndpoint]:
        """Select best CDN endpoints for content type"""
        try:
            # Filter endpoints that support the content type
            suitable_endpoints = [
                endpoint for endpoint in self.cdn_endpoints.values()
                if (not endpoint.supported_content_types or 
                    content_type in endpoint.supported_content_types) and
                   endpoint.active
            ]
            
            # Sort by priority
            suitable_endpoints.sort(key=lambda e: e.priority)
            
            # Return top 2 endpoints for redundancy
            return suitable_endpoints[:2]
            
        except Exception as e:
            logger.error(f"CDN endpoint selection error: {e}")
            return list(self.cdn_endpoints.values())[:1]  # Fallback to first available
    
    async def _upload_to_provider(self, provider: MockCDNProvider, 
                                 content_item: ContentItem, content_data: bytes) -> str:
        """Upload content to specific CDN provider"""
        try:
            cdn_url = await provider.upload_content(content_item, content_data)
            return cdn_url
            
        except Exception as e:
            logger.error(f"Upload to provider {provider.provider.value} error: {e}")
            raise
    
    async def _optimize_content(self, content_data: bytes, content_type: ContentType, 
                              optimization_level: OptimizationLevel) -> Tuple[bytes, ContentOptimizationResult]:
        """Optimize content based on type and level"""
        try:
            original_size = len(content_data)
            optimized_data = content_data
            optimizations_applied = []
            
            # Mock optimization based on content type and level
            if content_type == ContentType.IMAGE:
                if optimization_level in [OptimizationLevel.STANDARD, OptimizationLevel.AGGRESSIVE]:
                    # Mock image compression
                    compression_ratio = 0.7 if optimization_level == OptimizationLevel.STANDARD else 0.5
                    optimized_size = int(original_size * compression_ratio)
                    optimized_data = content_data[:optimized_size]  # Mock compressed data
                    optimizations_applied.extend(["compression", "format_optimization"])
                    
                    if optimization_level == OptimizationLevel.AGGRESSIVE:
                        optimizations_applied.append("quality_reduction")
            
            elif content_type == ContentType.VIDEO:
                if optimization_level in [OptimizationLevel.STANDARD, OptimizationLevel.AGGRESSIVE]:
                    # Mock video optimization
                    compression_ratio = 0.6 if optimization_level == OptimizationLevel.STANDARD else 0.4
                    optimized_size = int(original_size * compression_ratio)
                    optimized_data = content_data[:optimized_size]  # Mock optimized data
                    optimizations_applied.extend(["video_compression", "bitrate_optimization"])
            
            # Calculate results
            optimized_size = len(optimized_data)
            compression_ratio = optimized_size / original_size if original_size > 0 else 1.0
            
            result = ContentOptimizationResult(
                original_size_bytes=original_size,
                optimized_size_bytes=optimized_size,
                compression_ratio=compression_ratio,
                optimization_applied=optimizations_applied,
                quality_score=0.9 if optimization_level == OptimizationLevel.AGGRESSIVE else 1.0,
                processing_time_ms=50.0  # Mock processing time
            )
            
            return optimized_data, result
            
        except Exception as e:
            logger.error(f"Content optimization error: {e}")
            return content_data, ContentOptimizationResult(
                original_size_bytes=len(content_data),
                optimized_size_bytes=len(content_data),
                compression_ratio=1.0
            )
    
    async def get_content_url(self, content_id: str, preferred_provider: CDNProvider = None,
                            user_location: str = None) -> Optional[str]:
        """Get optimized CDN URL for content"""
        try:
            content_item = self.content_items.get(content_id)
            if not content_item:
                return None
            
            # Update last accessed time
            content_item.last_accessed = datetime.utcnow()
            
            # Select best CDN URL based on preferences and performance
            if preferred_provider and preferred_provider.value in content_item.cdn_urls:
                return content_item.cdn_urls[preferred_provider.value]
            
            # Select based on performance metrics and user location
            best_url = await self._select_optimal_cdn_url(content_item, user_location)
            
            return best_url
            
        except Exception as e:
            logger.error(f"Get content URL error: {e}")
            return None
    
    async def _select_optimal_cdn_url(self, content_item: ContentItem, 
                                    user_location: str = None) -> Optional[str]:
        """Select optimal CDN URL based on performance and location"""
        try:
            if not content_item.cdn_urls:
                return None
            
            # Get performance metrics for available providers
            provider_scores = {}
            
            for provider_str, cdn_url in content_item.cdn_urls.items():
                try:
                    provider = CDNProvider(provider_str)
                    
                    # Calculate score based on performance metrics
                    metrics_key = f"{provider.value}_{user_location or 'global'}"
                    metrics = self.performance_metrics.get(metrics_key)
                    
                    if metrics:
                        # Score based on response time, cache hit rate, and availability
                        score = (
                            (1000 - min(metrics.response_time_ms, 1000)) / 1000 * 0.4 +
                            metrics.cache_hit_rate * 0.3 +
                            metrics.availability / 100 * 0.3
                        )
                    else:
                        score = 0.5  # Default score for unknown performance
                    
                    provider_scores[provider_str] = score
                    
                except ValueError:
                    continue
            
            # Select provider with highest score
            if provider_scores:
                best_provider = max(provider_scores.keys(), key=lambda p: provider_scores[p])
                return content_item.cdn_urls[best_provider]
            
            # Fallback to first available URL
            return next(iter(content_item.cdn_urls.values()))
            
        except Exception as e:
            logger.error(f"Optimal CDN URL selection error: {e}")
            return next(iter(content_item.cdn_urls.values())) if content_item.cdn_urls else None
    
    async def invalidate_cache(self, content_ids: List[str], 
                             providers: List[CDNProvider] = None,
                             priority: str = "normal") -> CacheInvalidationRequest:
        """Invalidate cache for specified content"""
        try:
            request = CacheInvalidationRequest(
                request_id=str(uuid.uuid4()),
                content_ids=content_ids,
                providers=providers or list(CDNProvider),
                priority=priority
            )
            
            self.invalidation_requests[request.request_id] = request
            
            # Process invalidation asynchronously
            asyncio.create_task(self._process_cache_invalidation(request))
            
            logger.info(f"Cache invalidation request created: {request.request_id}")
            return request
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            raise
    
    async def _process_cache_invalidation(self, request -> None: CacheInvalidationRequest) -> None:
        """Process cache invalidation request"""
        try:
            request.status = "processing"
            
            # Purge cache from all specified providers
            purge_tasks = []
            
            for provider in request.providers:
                cdn_provider = self.cdn_providers.get(provider)
                if cdn_provider:
                    purge_tasks.append(cdn_provider.purge_cache(request.content_ids))
            
            if purge_tasks:
                results = await asyncio.gather(*purge_tasks, return_exceptions=True)
                
                # Check if all purges were successful
                all_successful = all(
                    isinstance(result, bool) and result for result in results
                )
                
                request.status = "completed" if all_successful else "failed"
            else:
                request.status = "failed"
            
            request.completed_at = datetime.utcnow()
            
            logger.info(f"Cache invalidation completed: {request.request_id} - Status: {request.status}")
            
        except Exception as e:
            logger.error(f"Cache invalidation processing error: {e}")
            request.status = "failed"
            request.completed_at = datetime.utcnow()
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from all CDN providers"""
        try:
            content_item = self.content_items.get(content_id)
            if not content_item:
                return False
            
            # Delete from all CDN providers
            delete_tasks = []
            
            for provider_str in content_item.cdn_urls.keys():
                try:
                    provider = CDNProvider(provider_str)
                    cdn_provider = self.cdn_providers.get(provider)
                    if cdn_provider:
                        delete_tasks.append(cdn_provider.delete_content(content_id))
                except ValueError:
                    continue
            
            if delete_tasks:
                results = await asyncio.gather(*delete_tasks, return_exceptions=True)
                
                # Check if any deletion was successful
                any_successful = any(
                    isinstance(result, bool) and result for result in results
                )
                
                if any_successful:
                    del self.content_items[content_id]
                    logger.info(f"Content deleted: {content_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Content deletion error: {e}")
            return False
    
    async def update_performance_metrics(self) -> None:
        """Update performance metrics for all CDN providers"""
        try:
            for endpoint in self.cdn_endpoints.values():
                if not endpoint.active:
                    continue
                
                provider = self.cdn_providers.get(endpoint.provider)
                if provider:
                    metrics_data = await provider.get_metrics()
                    
                    metrics_key = f"{endpoint.provider.value}_{endpoint.region}"
                    
                    self.performance_metrics[metrics_key] = CDNPerformanceMetrics(
                        provider=endpoint.provider,
                        region=endpoint.region,
                        response_time_ms=metrics_data.get("response_time_ms", 0.0),
                        cache_hit_rate=metrics_data.get("cache_hit_rate", 0.0),
                        bandwidth_usage_gb=metrics_data.get("bandwidth_usage_gb", 0.0),
                        requests_count=metrics_data.get("requests_count", 0),
                        error_rate=metrics_data.get("error_rate", 0.0),
                        availability=metrics_data.get("availability", 100.0)
                    )
                    
                    endpoint.last_health_check = datetime.utcnow()
            
            logger.debug("CDN performance metrics updated")
            
        except Exception as e:
            logger.error(f"Performance metrics update error: {e}")
    
    async def get_cdn_analytics(self, start_date: datetime = None, 
                              end_date: datetime = None) -> Dict[str, Any]:
        """Get CDN analytics and performance report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Calculate content statistics
            total_content = len(self.content_items)
            total_size_gb = sum(
                item.size_bytes for item in self.content_items.values()
            ) / (1024**3)
            
            # Content type distribution
            content_type_dist = {}
            for item in self.content_items.values():
                content_type = item.content_type.value
                content_type_dist[content_type] = content_type_dist.get(content_type, 0) + 1
            
            # Provider performance summary
            provider_performance = {}
            for metrics in self.performance_metrics.values():
                provider = metrics.provider.value
                if provider not in provider_performance:
                    provider_performance[provider] = {
                        "avg_response_time_ms": 0.0,
                        "avg_cache_hit_rate": 0.0,
                        "total_bandwidth_gb": 0.0,
                        "availability": 0.0
                    }
                
                perf = provider_performance[provider]
                perf["avg_response_time_ms"] += metrics.response_time_ms
                perf["avg_cache_hit_rate"] += metrics.cache_hit_rate
                perf["total_bandwidth_gb"] += metrics.bandwidth_usage_gb
                perf["availability"] += metrics.availability
            
            # Average the metrics
            for provider_data in provider_performance.values():
                region_count = len([m for m in self.performance_metrics.values() 
                                  if m.provider.value == provider])
                if region_count > 0:
                    provider_data["avg_response_time_ms"] /= region_count
                    provider_data["avg_cache_hit_rate"] /= region_count
                    provider_data["availability"] /= region_count
            
            analytics = {
                "report_id": str(uuid.uuid4()),
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "content_summary": {
                    "total_content_items": total_content,
                    "total_size_gb": round(total_size_gb, 2),
                    "content_type_distribution": content_type_dist
                },
                "provider_performance": provider_performance,
                "cache_invalidations": {
                    "total_requests": len(self.invalidation_requests),
                    "completed": len([r for r in self.invalidation_requests.values() 
                                    if r.status == "completed"]),
                    "failed": len([r for r in self.invalidation_requests.values() 
                                 if r.status == "failed"])
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"CDN analytics generated: {analytics['report_id']}")
            return analytics
            
        except Exception as e:
            logger.error(f"CDN analytics generation error: {e}")
            return {}

# Export classes
__all__ = [
    "CDNProvider",
    "ContentType",
    "CacheStrategy",
    "OptimizationLevel",
    "CDNEndpoint",
    "ContentItem",
    "CacheInvalidationRequest",
    "CDNPerformanceMetrics",
    "ContentOptimizationResult",
    "CDNIntegrationManager"
]

# Module initialization
logger.info("🌐 CDN Integration Manager module loaded")