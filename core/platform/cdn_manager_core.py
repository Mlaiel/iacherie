"""
CDN Manager Core - Advanced Content Delivery Network Management System
======================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for CDN management, content distribution,
edge caching, and performance optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
import hashlib
from abc import ABC, abstractmethod

# Get logger
logger = logging.getLogger(__name__)

class CDNProvider(Enum):
    """CDN providers"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    MAXCDN = "maxcdn"
    KEYCDN = "keycdn"

class CacheStrategy(Enum):
    """Cache strategies"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    TIME_BASED = "time_based"
    CONTENT_BASED = "content_based"

class ContentType(Enum):
    """Content types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    API_RESPONSE = "api_response"
    STATIC_ASSET = "static_asset"
    DYNAMIC_CONTENT = "dynamic_content"

@dataclass
class CDNEndpoint:
    """CDN endpoint configuration"""
    endpoint_id: str
    provider: CDNProvider
    domain: str
    origin_server: str
    cache_strategy: CacheStrategy
    ttl_seconds: int
    enabled: bool
    ssl_enabled: bool
    compression_enabled: bool
    created_at: datetime
    regions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheRule:
    """Cache rule configuration"""
    rule_id: str
    endpoint_id: str
    path_pattern: str
    content_type: ContentType
    cache_strategy: CacheStrategy
    ttl_seconds: int
    headers_to_cache: List[str]
    query_params_to_ignore: List[str]
    priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CDNMetrics:
    """CDN performance metrics"""
    endpoint_id: str
    timestamp: datetime
    requests_count: int
    cache_hit_ratio: float
    bandwidth_mb: float
    response_time_ms: float
    error_rate: float
    geographical_distribution: Dict[str, int]
    content_type_distribution: Dict[str, int]

class CDNManagerCore:
    """Advanced CDN Manager Core System"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.version = "2.1.0"
        self.level = level
        self.endpoints = {}
        self.cache_rules = {}
        self.metrics_history = {}
        self.providers_config = {}
        self.cache_storage = {}
        
        # Initialize provider configurations
        self._initialize_providers()
        
        logger.info(f"CDN Manager Core initialized - Level: {level}")

    def _initialize_providers(self) -> None:
        """Initialize CDN provider configurations"""
        self.providers_config = {
            CDNProvider.CLOUDFLARE: {
                "api_endpoint": "https://api.cloudflare.com/client/v4",
                "features": ["ddos_protection", "web_application_firewall", "ssl", "compression"],
                "global_pops": 275,
                "pricing_model": "pay_per_request"
            },
            CDNProvider.AWS_CLOUDFRONT: {
                "api_endpoint": "https://cloudfront.amazonaws.com",
                "features": ["lambda_edge", "real_time_logs", "ssl", "compression"],
                "global_pops": 450,
                "pricing_model": "pay_per_usage"
            },
            CDNProvider.AZURE_CDN: {
                "api_endpoint": "https://management.azure.com",
                "features": ["dynamic_site_acceleration", "ssl", "compression"],
                "global_pops": 120,
                "pricing_model": "pay_per_gb"
            },
            CDNProvider.GOOGLE_CDN: {
                "api_endpoint": "https://www.googleapis.com/compute/v1",
                "features": ["cloud_armor", "ssl", "compression", "http2"],
                "global_pops": 146,
                "pricing_model": "pay_per_usage"
            }
        }

    async def create_cdn_endpoint(self, endpoint_config: Dict[str, Any]) -> str:
        """Create CDN endpoint"""
        try:
            endpoint_id = f"cdn_{uuid.uuid4().hex[:12]}"
            
            endpoint = CDNEndpoint(
                endpoint_id=endpoint_id,
                provider=CDNProvider(endpoint_config.get("provider", "cloudflare")),
                domain=endpoint_config.get("domain", ""),
                origin_server=endpoint_config.get("origin_server", ""),
                cache_strategy=CacheStrategy(endpoint_config.get("cache_strategy", "adaptive")),
                ttl_seconds=endpoint_config.get("ttl_seconds", 3600),
                enabled=endpoint_config.get("enabled", True),
                ssl_enabled=endpoint_config.get("ssl_enabled", True),
                compression_enabled=endpoint_config.get("compression_enabled", True),
                created_at=datetime.now(),
                regions=endpoint_config.get("regions", ["us-east", "eu-west", "asia-pacific"]),
                metadata=endpoint_config.get("metadata", {})
            )
            
            self.endpoints[endpoint_id] = endpoint
            
            # Create default cache rules
            await self._create_default_cache_rules(endpoint_id)
            
            logger.info(f"CDN endpoint created: {endpoint_id}")
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create CDN endpoint: {str(e)}")
            return ""

    async def _create_default_cache_rules(self, endpoint_id -> None: str) -> None:
        """Create default cache rules for endpoint"""
        default_rules = [
            {
                "path_pattern": "*.jpg,*.png,*.gif,*.webp",
                "content_type": ContentType.IMAGE,
                "cache_strategy": CacheStrategy.STATIC,
                "ttl_seconds": 86400,  # 24 hours
                "priority": 100
            },
            {
                "path_pattern": "*.mp4,*.webm,*.mov",
                "content_type": ContentType.VIDEO,
                "cache_strategy": CacheStrategy.STATIC,
                "ttl_seconds": 604800,  # 7 days
                "priority": 90
            },
            {
                "path_pattern": "*.css,*.js",
                "content_type": ContentType.STATIC_ASSET,
                "cache_strategy": CacheStrategy.STATIC,
                "ttl_seconds": 86400,  # 24 hours
                "priority": 80
            },
            {
                "path_pattern": "/api/*",
                "content_type": ContentType.API_RESPONSE,
                "cache_strategy": CacheStrategy.DYNAMIC,
                "ttl_seconds": 300,  # 5 minutes
                "priority": 50
            }
        ]
        
        for rule_config in default_rules:
            await self.create_cache_rule(endpoint_id, rule_config)

    async def create_cache_rule(self, endpoint_id: str, rule_config: Dict[str, Any]) -> str:
        """Create cache rule for endpoint"""
        try:
            if endpoint_id not in self.endpoints:
                return ""
            
            rule_id = f"rule_{uuid.uuid4().hex[:8]}"
            
            rule = CacheRule(
                rule_id=rule_id,
                endpoint_id=endpoint_id,
                path_pattern=rule_config.get("path_pattern", "*"),
                content_type=ContentType(rule_config.get("content_type", "static_asset")),
                cache_strategy=CacheStrategy(rule_config.get("cache_strategy", "static")),
                ttl_seconds=rule_config.get("ttl_seconds", 3600),
                headers_to_cache=rule_config.get("headers_to_cache", ["content-type", "cache-control"]),
                query_params_to_ignore=rule_config.get("query_params_to_ignore", ["utm_source", "utm_medium"]),
                priority=rule_config.get("priority", 50),
                metadata=rule_config.get("metadata", {})
            )
            
            # Store rule by endpoint
            if endpoint_id not in self.cache_rules:
                self.cache_rules[endpoint_id] = {}
            self.cache_rules[endpoint_id][rule_id] = rule
            
            logger.info(f"Cache rule created: {rule_id} for endpoint {endpoint_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to create cache rule: {str(e)}")
            return ""

    async def cache_content(self, endpoint_id: str, content_path: str, content_data: bytes, 
                           content_type: ContentType = ContentType.STATIC_ASSET) -> bool:
        """Cache content at CDN edge locations"""
        try:
            if endpoint_id not in self.endpoints:
                return False
            
            endpoint = self.endpoints[endpoint_id]
            
            # Find applicable cache rule
            cache_rule = self._find_applicable_cache_rule(endpoint_id, content_path, content_type)
            
            if not cache_rule:
                logger.warning(f"No cache rule found for {content_path}")
                return False
            
            # Generate cache key
            cache_key = self._generate_cache_key(endpoint_id, content_path, content_type)
            
            # Store content with metadata
            cache_entry = {
                "content_data": content_data,
                "content_type": content_type.value,
                "cached_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=cache_rule.ttl_seconds),
                "cache_rule_id": cache_rule.rule_id,
                "access_count": 0,
                "last_accessed": datetime.now(),
                "content_hash": hashlib.md5(content_data).hexdigest(),
                "content_size": len(content_data)
            }
            
            # Initialize cache storage for endpoint if needed
            if endpoint_id not in self.cache_storage:
                self.cache_storage[endpoint_id] = {}
            
            self.cache_storage[endpoint_id][cache_key] = cache_entry
            
            logger.info(f"Content cached: {content_path} at endpoint {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Content caching failed: {str(e)}")
            return False

    def _find_applicable_cache_rule(self, endpoint_id: str, content_path: str, 
                                   content_type: ContentType) -> Optional[CacheRule]:
        """Find applicable cache rule for content"""
        endpoint_rules = self.cache_rules.get(endpoint_id, {})
        
        if not endpoint_rules:
            return None
        
        # Find matching rules
        matching_rules = []
        for rule in endpoint_rules.values():
            if self._path_matches_pattern(content_path, rule.path_pattern):
                if rule.content_type == content_type or rule.content_type == ContentType.STATIC_ASSET:
                    matching_rules.append(rule)
        
        if not matching_rules:
            return None
        
        # Return rule with highest priority
        return max(matching_rules, key=lambda r: r.priority)

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern"""
        # Simple pattern matching (supports * wildcard)
        if pattern == "*":
            return True
        
        if "," in pattern:
            # Multiple patterns separated by comma
            patterns = [p.strip() for p in pattern.split(",")]
            return any(self._path_matches_pattern(path, p) for p in patterns)
        
        if pattern.startswith("*"):
            return path.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        else:
            return path == pattern

    def _generate_cache_key(self, endpoint_id: str, content_path: str, content_type: ContentType) -> str:
        """Generate cache key"""
        key_data = f"{endpoint_id}:{content_path}:{content_type.value}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def get_cached_content(self, endpoint_id: str, content_path: str, 
                                content_type: ContentType = ContentType.STATIC_ASSET) -> Optional[bytes]:
        """Get cached content"""
        try:
            cache_key = self._generate_cache_key(endpoint_id, content_path, content_type)
            
            endpoint_cache = self.cache_storage.get(endpoint_id, {})
            cache_entry = endpoint_cache.get(cache_key)
            
            if not cache_entry:
                return None
            
            # Check if cache entry has expired
            if datetime.now() > cache_entry["expires_at"]:
                # Remove expired entry
                del endpoint_cache[cache_key]
                return None
            
            # Update access statistics
            cache_entry["access_count"] += 1
            cache_entry["last_accessed"] = datetime.now()
            
            return cache_entry["content_data"]
            
        except Exception as e:
            logger.error(f"Failed to get cached content: {str(e)}")
            return None

    async def invalidate_cache(self, endpoint_id: str, content_paths: List[str] = None) -> bool:
        """Invalidate cached content"""
        try:
            if endpoint_id not in self.cache_storage:
                return True
            
            endpoint_cache = self.cache_storage[endpoint_id]
            
            if content_paths is None:
                # Invalidate all cache for endpoint
                endpoint_cache.clear()
                logger.info(f"All cache invalidated for endpoint {endpoint_id}")
            else:
                # Invalidate specific paths
                invalidated_count = 0
                for content_path in content_paths:
                    # Find and remove matching cache keys
                    keys_to_remove = []
                    for cache_key, cache_entry in endpoint_cache.items():
                        # Check if cache entry matches any of the paths
                        if any(self._path_matches_pattern(content_path, path) for path in content_paths):
                            keys_to_remove.append(cache_key)
                    
                    for key in keys_to_remove:
                        del endpoint_cache[key]
                        invalidated_count += 1
                
                logger.info(f"Cache invalidated: {invalidated_count} entries for endpoint {endpoint_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Cache invalidation failed: {str(e)}")
            return False

    async def collect_metrics(self, endpoint_id: str) -> CDNMetrics:
        """Collect CDN metrics for endpoint"""
        try:
            if endpoint_id not in self.endpoints:
                return None
            
            endpoint_cache = self.cache_storage.get(endpoint_id, {})
            
            # Calculate metrics
            total_requests = sum(entry["access_count"] for entry in endpoint_cache.values())
            cache_hits = len([entry for entry in endpoint_cache.values() if entry["access_count"] > 0])
            cache_hit_ratio = (cache_hits / max(1, len(endpoint_cache))) * 100
            
            total_bandwidth = sum(entry["content_size"] * entry["access_count"] for entry in endpoint_cache.values())
            bandwidth_mb = total_bandwidth / (1024 * 1024)
            
            # Mock additional metrics
            response_time_ms = 50.0 + (100 - cache_hit_ratio) * 2  # Better cache hit = better response time
            error_rate = max(0, 5 - cache_hit_ratio / 10)  # Better cache hit = lower error rate
            
            metrics = CDNMetrics(
                endpoint_id=endpoint_id,
                timestamp=datetime.now(),
                requests_count=total_requests,
                cache_hit_ratio=cache_hit_ratio,
                bandwidth_mb=bandwidth_mb,
                response_time_ms=response_time_ms,
                error_rate=error_rate,
                geographical_distribution={
                    "us-east": 40,
                    "eu-west": 35,
                    "asia-pacific": 25
                },
                content_type_distribution={
                    "image": 45,
                    "video": 30,
                    "static_asset": 20,
                    "api_response": 5
                }
            )
            
            # Store metrics
            if endpoint_id not in self.metrics_history:
                self.metrics_history[endpoint_id] = []
            self.metrics_history[endpoint_id].append(metrics)
            
            # Keep only last 100 metrics
            if len(self.metrics_history[endpoint_id]) > 100:
                self.metrics_history[endpoint_id] = self.metrics_history[endpoint_id][-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
            return None

    async def get_performance_report(self, endpoint_id: str, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get performance report for endpoint"""
        try:
            if endpoint_id not in self.metrics_history:
                return {}
            
            # Filter metrics by time range
            relevant_metrics = [
                m for m in self.metrics_history[endpoint_id]
                if time_range[0] <= m.timestamp <= time_range[1]
            ]
            
            if not relevant_metrics:
                return {}
            
            # Calculate aggregated metrics
            avg_cache_hit_ratio = sum(m.cache_hit_ratio for m in relevant_metrics) / len(relevant_metrics)
            avg_response_time = sum(m.response_time_ms for m in relevant_metrics) / len(relevant_metrics)
            total_bandwidth = sum(m.bandwidth_mb for m in relevant_metrics)
            avg_error_rate = sum(m.error_rate for m in relevant_metrics) / len(relevant_metrics)
            total_requests = sum(m.requests_count for m in relevant_metrics)
            
            report = {
                "endpoint_id": endpoint_id,
                "report_period": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat()
                },
                "performance_summary": {
                    "average_cache_hit_ratio": round(avg_cache_hit_ratio, 2),
                    "average_response_time_ms": round(avg_response_time, 2),
                    "total_bandwidth_mb": round(total_bandwidth, 2),
                    "average_error_rate": round(avg_error_rate, 2),
                    "total_requests": total_requests
                },
                "cache_efficiency": "excellent" if avg_cache_hit_ratio > 90 else "good" if avg_cache_hit_ratio > 70 else "needs_improvement",
                "recommendations": self._generate_performance_recommendations(avg_cache_hit_ratio, avg_response_time, avg_error_rate),
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            return {}

    def _generate_performance_recommendations(self, cache_hit_ratio: float, response_time: float, error_rate: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if cache_hit_ratio < 70:
            recommendations.extend([
                "Optimize cache rules for better hit ratio",
                "Increase TTL for static content",
                "Review cache invalidation patterns"
            ])
        
        if response_time > 200:
            recommendations.extend([
                "Consider edge location optimization",
                "Enable compression for all content types",
                "Optimize origin server response time"
            ])
        
        if error_rate > 5:
            recommendations.extend([
                "Investigate origin server health",
                "Review cache rule configuration",
                "Monitor DNS resolution issues"
            ])
        
        if not recommendations:
            recommendations.append("Performance is optimal - maintain current configuration")
        
        return recommendations

# Module exports
__all__ = [
    "CDNManagerCore",
    "CDNProvider",
    "CacheStrategy",
    "ContentType",
    "CDNEndpoint",
    "CacheRule",
    "CDNMetrics"
]

logger.info("🌐 CDN Manager Core module loaded")