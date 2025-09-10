#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue CDN Configuration Module
==================================

Enterprise-grade Content Delivery Network (CDN) configuration for the Ainflue platform.
Comprehensive CDN management with multi-provider support, edge optimization,
global distribution, caching strategies, and intelligent routing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib

class CDNProvider(str, Enum):
    """CDN providers"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    MAXCDN = "maxcdn"
    BUNNYCDN = "bunnycdn"
    CLOUDINARY = "cloudinary"
    IMAGEKIT = "imagekit"
    CUSTOM = "custom"

class CDNTier(str, Enum):
    """CDN service tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class CacheStrategy(str, Enum):
    """Cache strategies"""
    NO_CACHE = "no_cache"
    BROWSER_CACHE = "browser_cache"
    EDGE_CACHE = "edge_cache"
    ORIGIN_CACHE = "origin_cache"
    SMART_CACHE = "smart_cache"
    AGGRESSIVE_CACHE = "aggressive_cache"
    BYPASS_CACHE = "bypass_cache"

class ContentType(str, Enum):
    """Content types for CDN optimization"""
    STATIC_ASSETS = "static_assets"    # CSS, JS, fonts
    IMAGES = "images"                  # JPEG, PNG, WebP, AVIF
    VIDEOS = "videos"                  # MP4, WebM, HLS, DASH
    AUDIO = "audio"                    # MP3, AAC, OGG
    DOCUMENTS = "documents"            # PDF, DOC, ZIP
    API_RESPONSES = "api_responses"    # JSON, XML responses
    DYNAMIC_CONTENT = "dynamic_content"  # Server-rendered pages
    LIVE_STREAMS = "live_streams"      # Live video/audio streams

class OptimizationLevel(str, Enum):
    """Content optimization levels"""
    NONE = "none"                      # No optimization
    BASIC = "basic"                    # Basic compression
    STANDARD = "standard"              # Standard optimization
    AGGRESSIVE = "aggressive"          # Aggressive optimization
    LOSSLESS = "lossless"             # Lossless optimization
    ADAPTIVE = "adaptive"              # Adaptive based on device/connection

class RoutingStrategy(str, Enum):
    """CDN routing strategies"""
    GEOGRAPHIC = "geographic"          # Route by geographic location
    LATENCY_BASED = "latency_based"   # Route by lowest latency
    LOAD_BALANCED = "load_balanced"    # Route by server load
    FAILOVER = "failover"             # Primary/backup routing
    WEIGHTED = "weighted"             # Weighted routing
    PERFORMANCE = "performance"        # Performance-based routing
    COST_OPTIMIZED = "cost_optimized" # Cost-optimized routing

@dataclass
class CDNEndpoint:
    """CDN endpoint configuration"""
    endpoint_id: str
    name: str
    domain: str
    provider: CDNProvider
    
    # Geographic configuration
    regions: List[str] = field(default_factory=list)  # us-east-1, eu-west-1, etc.
    edge_locations: List[str] = field(default_factory=list)
    primary_region: str = "us-east-1"
    
    # SSL/TLS configuration
    ssl_enabled: bool = True
    ssl_certificate_id: str = ""
    ssl_protocols: List[str] = field(default_factory=lambda: ["TLSv1.2", "TLSv1.3"])
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    
    # Performance settings
    http2_enabled: bool = True
    http3_enabled: bool = True
    brotli_compression: bool = True
    gzip_compression: bool = True
    compression_level: int = 6
    
    # Cache settings
    default_ttl: int = 3600  # 1 hour
    max_ttl: int = 31536000  # 1 year
    browser_cache_ttl: int = 86400  # 1 day
    
    # Security settings
    hotlink_protection: bool = True
    allowed_referers: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    allowed_countries: List[str] = field(default_factory=list)
    ddos_protection: bool = True
    
    # Bandwidth and limits
    bandwidth_limit_mbps: Optional[int] = None
    request_limit_per_second: Optional[int] = None
    burst_limit: Optional[int] = None
    
    # Monitoring
    health_check_enabled: bool = True
    health_check_path: str = "/health"
    health_check_interval: int = 60  # seconds
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    priority: int = 5  # 1-10, higher = more important
    
    def get_full_url(self, path: str = "") -> str:
        """Get full CDN URL"""
        protocol = "https" if self.ssl_enabled else "http"
        return f"{protocol}://{self.domain}{path}"
    
    def is_available_in_region(self, region: str) -> bool:
        """Check if endpoint is available in region"""
        return region in self.regions or not self.regions  # Empty list means all regions
    
    def calculate_priority_score(self, user_region: str, content_type: ContentType) -> float:
        """Calculate priority score for endpoint selection"""
        score = float(self.priority)
        
        # Region proximity bonus
        if user_region == self.primary_region:
            score += 3.0
        elif user_region in self.regions:
            score += 1.0
        
        # Performance features bonus
        if self.http3_enabled:
            score += 0.5
        if self.brotli_compression:
            score += 0.3
        
        # Security features bonus
        if self.ddos_protection:
            score += 0.2
        
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "endpoint_id": self.endpoint_id,
            "name": self.name,
            "domain": self.domain,
            "provider": self.provider.value,
            "regions": self.regions,
            "edge_locations": self.edge_locations,
            "primary_region": self.primary_region,
            "ssl_enabled": self.ssl_enabled,
            "ssl_certificate_id": self.ssl_certificate_id,
            "ssl_protocols": self.ssl_protocols,
            "hsts_enabled": self.hsts_enabled,
            "hsts_max_age": self.hsts_max_age,
            "http2_enabled": self.http2_enabled,
            "http3_enabled": self.http3_enabled,
            "brotli_compression": self.brotli_compression,
            "gzip_compression": self.gzip_compression,
            "compression_level": self.compression_level,
            "default_ttl": self.default_ttl,
            "max_ttl": self.max_ttl,
            "browser_cache_ttl": self.browser_cache_ttl,
            "hotlink_protection": self.hotlink_protection,
            "allowed_referers": self.allowed_referers,
            "blocked_countries": self.blocked_countries,
            "allowed_countries": self.allowed_countries,
            "ddos_protection": self.ddos_protection,
            "bandwidth_limit_mbps": self.bandwidth_limit_mbps,
            "request_limit_per_second": self.request_limit_per_second,
            "burst_limit": self.burst_limit,
            "health_check_enabled": self.health_check_enabled,
            "health_check_path": self.health_check_path,
            "health_check_interval": self.health_check_interval,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "enabled": self.enabled,
            "priority": self.priority
        }

@dataclass
class ContentRule:
    """Content-specific CDN rules"""
    rule_id: str
    name: str
    description: str
    content_type: ContentType
    
    # Matching criteria
    path_patterns: List[str] = field(default_factory=list)  # /images/*, *.jpg, etc.
    file_extensions: List[str] = field(default_factory=list)  # .jpg, .png, .mp4
    mime_types: List[str] = field(default_factory=list)  # image/jpeg, video/mp4
    size_min_bytes: Optional[int] = None
    size_max_bytes: Optional[int] = None
    
    # Cache settings
    cache_strategy: CacheStrategy = CacheStrategy.SMART_CACHE
    cache_ttl: int = 3600
    browser_cache_ttl: int = 86400
    edge_cache_ttl: int = 3600
    stale_while_revalidate: int = 86400
    stale_if_error: int = 259200  # 3 days
    
    # Optimization settings
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    auto_webp: bool = True
    auto_avif: bool = True
    auto_format: bool = True
    quality_settings: Dict[str, int] = field(default_factory=lambda: {"high": 85, "medium": 70, "low": 50})
    
    # Compression settings
    compression_enabled: bool = True
    compression_types: List[str] = field(default_factory=lambda: ["gzip", "brotli"])
    compression_level: int = 6
    min_compression_size: int = 1024  # Don't compress files smaller than 1KB
    
    # Security settings
    require_auth: bool = False
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD"])
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)
    
    # Custom headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    cache_control_headers: Dict[str, str] = field(default_factory=dict)
    
    # Performance settings
    prefetch_enabled: bool = False
    preload_enabled: bool = False
    lazy_loading: bool = True
    adaptive_streaming: bool = False
    
    # Metadata
    priority: int = 5  # 1-10, higher priority rules are applied first
    enabled: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    
    def matches_content(self, path: str, mime_type: str = "", file_size: int = 0) -> bool:
        """Check if rule matches content"""
        
        # Check path patterns
        if self.path_patterns:
            import fnmatch
            path_match = any(fnmatch.fnmatch(path, pattern) for pattern in self.path_patterns)
            if not path_match:
                return False
        
        # Check file extensions
        if self.file_extensions:
            import os
            file_ext = os.path.splitext(path)[1].lower()
            if file_ext not in [ext.lower() for ext in self.file_extensions]:
                return False
        
        # Check MIME types
        if self.mime_types and mime_type:
            if mime_type not in self.mime_types:
                return False
        
        # Check file size
        if self.size_min_bytes is not None and file_size < self.size_min_bytes:
            return False
        
        if self.size_max_bytes is not None and file_size > self.size_max_bytes:
            return False
        
        return True
    
    def get_cache_headers(self) -> Dict[str, str]:
        """Get cache control headers"""
        
        headers = {}
        
        if self.cache_strategy == CacheStrategy.NO_CACHE:
            headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
        
        elif self.cache_strategy == CacheStrategy.BROWSER_CACHE:
            headers["Cache-Control"] = f"public, max-age={self.browser_cache_ttl}"
        
        elif self.cache_strategy == CacheStrategy.EDGE_CACHE:
            headers["Cache-Control"] = f"public, max-age={self.cache_ttl}, s-maxage={self.edge_cache_ttl}"
        
        elif self.cache_strategy == CacheStrategy.SMART_CACHE:
            cache_control = f"public, max-age={self.browser_cache_ttl}, s-maxage={self.edge_cache_ttl}"
            if self.stale_while_revalidate > 0:
                cache_control += f", stale-while-revalidate={self.stale_while_revalidate}"
            if self.stale_if_error > 0:
                cache_control += f", stale-if-error={self.stale_if_error}"
            headers["Cache-Control"] = cache_control
        
        # Add custom cache headers
        headers.update(self.cache_control_headers)
        
        return headers
    
    def get_optimization_params(self, user_agent: str = "", connection_type: str = "") -> Dict[str, Any]:
        """Get optimization parameters based on request context"""
        
        params = {
            "format": "auto" if self.auto_format else "original",
            "quality": self.quality_settings["medium"],
            "compression": self.compression_enabled
        }
        
        # Adaptive quality based on connection
        if self.optimization_level == OptimizationLevel.ADAPTIVE:
            if "slow" in connection_type.lower():
                params["quality"] = self.quality_settings["low"]
            elif "fast" in connection_type.lower():
                params["quality"] = self.quality_settings["high"]
        
        # Format selection
        if self.auto_webp and "webp" in user_agent.lower():
            params["format"] = "webp"
        
        if self.auto_avif and "avif" in user_agent.lower():
            params["format"] = "avif"
        
        return params
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type.value,
            "path_patterns": self.path_patterns,
            "file_extensions": self.file_extensions,
            "mime_types": self.mime_types,
            "size_min_bytes": self.size_min_bytes,
            "size_max_bytes": self.size_max_bytes,
            "cache_strategy": self.cache_strategy.value,
            "cache_ttl": self.cache_ttl,
            "browser_cache_ttl": self.browser_cache_ttl,
            "edge_cache_ttl": self.edge_cache_ttl,
            "stale_while_revalidate": self.stale_while_revalidate,
            "stale_if_error": self.stale_if_error,
            "optimization_level": self.optimization_level.value,
            "auto_webp": self.auto_webp,
            "auto_avif": self.auto_avif,
            "auto_format": self.auto_format,
            "quality_settings": self.quality_settings,
            "compression_enabled": self.compression_enabled,
            "compression_types": self.compression_types,
            "compression_level": self.compression_level,
            "min_compression_size": self.min_compression_size,
            "require_auth": self.require_auth,
            "allowed_methods": self.allowed_methods,
            "cors_enabled": self.cors_enabled,
            "cors_origins": self.cors_origins,
            "custom_headers": self.custom_headers,
            "cache_control_headers": self.cache_control_headers,
            "prefetch_enabled": self.prefetch_enabled,
            "preload_enabled": self.preload_enabled,
            "lazy_loading": self.lazy_loading,
            "adaptive_streaming": self.adaptive_streaming,
            "priority": self.priority,
            "enabled": self.enabled,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class CDNDistribution:
    """CDN distribution configuration"""
    distribution_id: str
    name: str
    description: str
    origin_domain: str
    
    # Endpoints
    endpoints: List[CDNEndpoint] = field(default_factory=list)
    primary_endpoint_id: str = ""
    
    # Content rules
    content_rules: List[ContentRule] = field(default_factory=list)
    
    # Routing configuration
    routing_strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE
    failover_enabled: bool = True
    load_balancing_enabled: bool = True
    
    # Global settings
    default_root_object: str = "index.html"
    custom_error_pages: Dict[str, str] = field(default_factory=dict)  # {404: "/404.html"}
    
    # Analytics and monitoring
    analytics_enabled: bool = True
    real_time_logs: bool = True
    detailed_metrics: bool = True
    
    # Security
    waf_enabled: bool = True
    rate_limiting: bool = True
    bot_protection: bool = True
    
    # Cost optimization
    cost_optimization: bool = True
    tier_pricing: CDNTier = CDNTier.PROFESSIONAL
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    
    def get_best_endpoint(self, user_region: str, content_type: ContentType) -> Optional[CDNEndpoint]:
        """Get best endpoint for user and content type"""
        
        available_endpoints = [ep for ep in self.endpoints if ep.enabled and ep.is_available_in_region(user_region)]
        
        if not available_endpoints:
            return None
        
        # Calculate scores for each endpoint
        endpoint_scores = []
        for endpoint in available_endpoints:
            score = endpoint.calculate_priority_score(user_region, content_type)
            endpoint_scores.append((endpoint, score))
        
        # Sort by score (highest first)
        endpoint_scores.sort(key=lambda x: x[1], reverse=True)
        
        return endpoint_scores[0][0] if endpoint_scores else None
    
    def get_matching_rules(self, path: str, mime_type: str = "", file_size: int = 0) -> List[ContentRule]:
        """Get matching content rules"""
        
        matching_rules = []
        
        for rule in self.content_rules:
            if rule.enabled and rule.matches_content(path, mime_type, file_size):
                matching_rules.append(rule)
        
        # Sort by priority (highest first)
        matching_rules.sort(key=lambda x: x.priority, reverse=True)
        
        return matching_rules
    
    def generate_cdn_url(self, path: str, user_region: str = "", 
                        optimization_params: Dict[str, Any] = None) -> str:
        """Generate optimized CDN URL"""
        
        # Determine content type
        content_type = self._detect_content_type(path)
        
        # Get best endpoint
        endpoint = self.get_best_endpoint(user_region, content_type)
        if not endpoint:
            return f"https://{self.origin_domain}{path}"
        
        # Get matching rules
        rules = self.get_matching_rules(path)
        
        # Build URL with optimizations
        base_url = endpoint.get_full_url(path)
        
        # Add optimization parameters
        if optimization_params or rules:
            query_params = []
            
            # Apply rule-based optimizations
            if rules:
                rule_params = rules[0].get_optimization_params()
                for key, value in rule_params.items():
                    query_params.append(f"{key}={value}")
            
            # Apply custom optimizations
            if optimization_params:
                for key, value in optimization_params.items():
                    query_params.append(f"{key}={value}")
            
            if query_params:
                base_url += "?" + "&".join(query_params)
        
        return base_url
    
    def purge_cache(self, paths: List[str] = None) -> Dict[str, Any]:
        """Purge CDN cache"""
        
        result = {
            "success": False,
            "purged_paths": [],
            "failed_paths": [],
            "total_endpoints": len(self.endpoints),
            "purge_id": f"purge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            # If no paths specified, purge all
            if not paths:
                paths = ["/*"]
            
            # Purge from all endpoints
            for endpoint in self.endpoints:
                if endpoint.enabled:
                    # Simulate purge operation
                    result["purged_paths"].extend(paths)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _detect_content_type(self, path: str) -> ContentType:
        """Detect content type from path"""
        
        import os
        
        file_ext = os.path.splitext(path)[1].lower()
        
        # Image extensions
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg']:
            return ContentType.IMAGES
        
        # Video extensions
        elif file_ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.m3u8', '.mpd']:
            return ContentType.VIDEOS
        
        # Audio extensions
        elif file_ext in ['.mp3', '.aac', '.ogg', '.wav', '.flac']:
            return ContentType.AUDIO
        
        # Document extensions
        elif file_ext in ['.pdf', '.doc', '.docx', '.zip', '.tar', '.gz']:
            return ContentType.DOCUMENTS
        
        # Static assets
        elif file_ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot']:
            return ContentType.STATIC_ASSETS
        
        # API paths
        elif '/api/' in path:
            return ContentType.API_RESPONSES
        
        # Default to dynamic content
        else:
            return ContentType.DYNAMIC_CONTENT
    
    def get_analytics_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get CDN analytics data"""
        
        # Simulate analytics data
        analytics_data = {
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "requests": {
                "total": 1500000,
                "cached": 1200000,
                "origin": 300000,
                "cache_hit_ratio": 80.0
            },
            "bandwidth": {
                "total_gb": 5000.0,
                "cached_gb": 4000.0,
                "origin_gb": 1000.0,
                "savings_gb": 4000.0
            },
            "performance": {
                "avg_response_time_ms": 45,
                "p95_response_time_ms": 120,
                "p99_response_time_ms": 250
            },
            "geographic_distribution": {
                "us-east-1": 45.0,
                "eu-west-1": 30.0,
                "ap-southeast-1": 15.0,
                "other": 10.0
            },
            "content_type_breakdown": {
                "images": 40.0,
                "videos": 25.0,
                "static_assets": 20.0,
                "api_responses": 10.0,
                "other": 5.0
            },
            "top_content": [
                {"path": "/images/hero.jpg", "requests": 50000},
                {"path": "/videos/intro.mp4", "requests": 25000},
                {"path": "/api/v1/content", "requests": 20000}
            ],
            "errors": {
                "4xx_errors": 1500,
                "5xx_errors": 300,
                "error_rate": 0.12
            }
        }
        
        return analytics_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "distribution_id": self.distribution_id,
            "name": self.name,
            "description": self.description,
            "origin_domain": self.origin_domain,
            "endpoints": [ep.to_dict() for ep in self.endpoints],
            "primary_endpoint_id": self.primary_endpoint_id,
            "content_rules": [rule.to_dict() for rule in self.content_rules],
            "routing_strategy": self.routing_strategy.value,
            "failover_enabled": self.failover_enabled,
            "load_balancing_enabled": self.load_balancing_enabled,
            "default_root_object": self.default_root_object,
            "custom_error_pages": self.custom_error_pages,
            "analytics_enabled": self.analytics_enabled,
            "real_time_logs": self.real_time_logs,
            "detailed_metrics": self.detailed_metrics,
            "waf_enabled": self.waf_enabled,
            "rate_limiting": self.rate_limiting,
            "bot_protection": self.bot_protection,
            "cost_optimization": self.cost_optimization,
            "tier_pricing": self.tier_pricing.value,
            "total_endpoints": len(self.endpoints),
            "total_rules": len(self.content_rules),
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "enabled": self.enabled
        }

class CDNConfiguration:
    """Main CDN configuration manager"""
    
    def __init__(self):
        """Initialize CDN configuration"""
        # Data storage
        self.distributions: Dict[str, CDNDistribution] = {}
        self.global_endpoints: Dict[str, CDNEndpoint] = {}
        
        # Global settings
        self.cdn_enabled = True
        self.auto_optimization = True
        self.smart_routing = True
        self.global_load_balancing = True
        
        # Default settings
        self.default_settings = {
            "cache_ttl": 3600,
            "browser_cache_ttl": 86400,
            "compression_enabled": True,
            "ssl_enabled": True,
            "ddos_protection": True,
            "analytics_enabled": True
        }
        
        # Performance settings
        self.performance_settings = {
            "http2_enabled": True,
            "http3_enabled": True,
            "brotli_compression": True,
            "gzip_compression": True,
            "image_optimization": True,
            "video_optimization": True,
            "adaptive_streaming": True,
            "edge_side_includes": True,
            "prefetch_enabled": True,
            "preload_enabled": True
        }
        
        # Security settings
        self.security_settings = {
            "waf_enabled": True,
            "ddos_protection": True,
            "bot_protection": True,
            "hotlink_protection": True,
            "geo_blocking": True,
            "rate_limiting": True,
            "ssl_enforcement": True,
            "hsts_enabled": True
        }
        
        # Cost optimization
        self.cost_settings = {
            "tiered_pricing": True,
            "regional_optimization": True,
            "bandwidth_optimization": True,
            "cache_optimization": True,
            "origin_shield": True,
            "compression_optimization": True
        }
        
        # Monitoring settings
        self.monitoring_settings = {
            "real_time_analytics": True,
            "detailed_logs": True,
            "performance_monitoring": True,
            "uptime_monitoring": True,
            "alert_threshold_cpu": 80,
            "alert_threshold_bandwidth": 90,
            "alert_threshold_errors": 5
        }
        
        # Initialize default distributions
        self._initialize_default_distributions()
    
    def _initialize_default_distributions(self):
        """Initialize default CDN distributions"""
        
        # Main content distribution
        main_endpoints = [
            CDNEndpoint(
                endpoint_id="cf_main",
                name="Cloudflare Main",
                domain="cdn.ainflue.com",
                provider=CDNProvider.CLOUDFLARE,
                regions=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                primary_region="us-east-1",
                priority=9
            ),
            CDNEndpoint(
                endpoint_id="aws_backup",
                name="AWS CloudFront Backup",
                domain="d123456789.cloudfront.net",
                provider=CDNProvider.AWS_CLOUDFRONT,
                regions=["us-east-1", "eu-west-1"],
                primary_region="us-east-1",
                priority=7
            )
        ]
        
        # Content rules for main distribution
        content_rules = [
            ContentRule(
                rule_id="images_rule",
                name="Image Optimization",
                description="Optimized delivery for images",
                content_type=ContentType.IMAGES,
                file_extensions=[".jpg", ".jpeg", ".png", ".webp", ".avif"],
                cache_strategy=CacheStrategy.AGGRESSIVE_CACHE,
                cache_ttl=86400,  # 1 day
                browser_cache_ttl=604800,  # 1 week
                optimization_level=OptimizationLevel.ADAPTIVE,
                auto_webp=True,
                auto_avif=True,
                priority=9
            ),
            ContentRule(
                rule_id="videos_rule",
                name="Video Streaming",
                description="Optimized delivery for videos",
                content_type=ContentType.VIDEOS,
                file_extensions=[".mp4", ".webm", ".m3u8", ".mpd"],
                cache_strategy=CacheStrategy.SMART_CACHE,
                cache_ttl=3600,  # 1 hour
                browser_cache_ttl=86400,  # 1 day
                optimization_level=OptimizationLevel.STANDARD,
                adaptive_streaming=True,
                priority=8
            ),
            ContentRule(
                rule_id="static_rule",
                name="Static Assets",
                description="Aggressive caching for static assets",
                content_type=ContentType.STATIC_ASSETS,
                file_extensions=[".css", ".js", ".woff", ".woff2"],
                cache_strategy=CacheStrategy.AGGRESSIVE_CACHE,
                cache_ttl=604800,  # 1 week
                browser_cache_ttl=2592000,  # 1 month
                optimization_level=OptimizationLevel.AGGRESSIVE,
                priority=7
            ),
            ContentRule(
                rule_id="api_rule",
                name="API Responses",
                description="Smart caching for API responses",
                content_type=ContentType.API_RESPONSES,
                path_patterns=["/api/*"],
                cache_strategy=CacheStrategy.SMART_CACHE,
                cache_ttl=300,  # 5 minutes
                browser_cache_ttl=0,  # No browser cache
                stale_while_revalidate=600,  # 10 minutes
                priority=6
            )
        ]
        
        main_distribution = CDNDistribution(
            distribution_id="main_cdn",
            name="Main Content Distribution",
            description="Primary CDN distribution for all content",
            origin_domain="origin.ainflue.com",
            endpoints=main_endpoints,
            primary_endpoint_id="cf_main",
            content_rules=content_rules,
            routing_strategy=RoutingStrategy.PERFORMANCE
        )
        
        self.distributions[main_distribution.distribution_id] = main_distribution
        
        # Store endpoints globally
        for endpoint in main_endpoints:
            self.global_endpoints[endpoint.endpoint_id] = endpoint
        
        # Media-specific distribution for heavy content
        media_endpoints = [
            CDNEndpoint(
                endpoint_id="bunny_media",
                name="BunnyCDN Media",
                domain="media.ainflue.b-cdn.net",
                provider=CDNProvider.BUNNYCDN,
                regions=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                primary_region="us-east-1",
                bandwidth_limit_mbps=10000,  # 10 Gbps
                priority=8
            )
        ]
        
        media_rules = [
            ContentRule(
                rule_id="large_videos",
                name="Large Video Files",
                description="Optimized for large video content",
                content_type=ContentType.VIDEOS,
                size_min_bytes=100 * 1024 * 1024,  # 100MB+
                cache_strategy=CacheStrategy.AGGRESSIVE_CACHE,
                cache_ttl=86400,  # 1 day
                optimization_level=OptimizationLevel.STANDARD,
                adaptive_streaming=True,
                priority=9
            )
        ]
        
        media_distribution = CDNDistribution(
            distribution_id="media_cdn",
            name="Media Content Distribution",
            description="Specialized CDN for large media files",
            origin_domain="media-origin.ainflue.com",
            endpoints=media_endpoints,
            primary_endpoint_id="bunny_media",
            content_rules=media_rules,
            routing_strategy=RoutingStrategy.LOAD_BALANCED
        )
        
        self.distributions[media_distribution.distribution_id] = media_distribution
        
        # Store media endpoints
        for endpoint in media_endpoints:
            self.global_endpoints[endpoint.endpoint_id] = endpoint
    
    def create_distribution(self, distribution_data: Dict[str, Any]) -> CDNDistribution:
        """Create new CDN distribution"""
        
        distribution = CDNDistribution(
            distribution_id=distribution_data.get("distribution_id", f"cdn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=distribution_data["name"],
            description=distribution_data.get("description", ""),
            origin_domain=distribution_data["origin_domain"],
            routing_strategy=RoutingStrategy(distribution_data.get("routing_strategy", "performance")),
            tier_pricing=CDNTier(distribution_data.get("tier_pricing", "professional"))
        )
        
        # Add endpoints
        if "endpoints" in distribution_data:
            for endpoint_data in distribution_data["endpoints"]:
                endpoint = CDNEndpoint(**endpoint_data)
                distribution.endpoints.append(endpoint)
                self.global_endpoints[endpoint.endpoint_id] = endpoint
        
        # Add content rules
        if "content_rules" in distribution_data:
            for rule_data in distribution_data["content_rules"]:
                rule = ContentRule(**rule_data)
                distribution.content_rules.append(rule)
        
        self.distributions[distribution.distribution_id] = distribution
        return distribution
    
    def get_optimal_cdn_url(self, path: str, user_region: str = "", 
                           distribution_id: str = "main_cdn",
                           optimization_params: Dict[str, Any] = None) -> str:
        """Get optimal CDN URL for content"""
        
        if distribution_id not in self.distributions:
            return f"https://default.ainflue.com{path}"
        
        distribution = self.distributions[distribution_id]
        return distribution.generate_cdn_url(path, user_region, optimization_params)
    
    def purge_content(self, paths: List[str], distribution_ids: List[str] = None) -> Dict[str, Any]:
        """Purge content from CDN cache"""
        
        if distribution_ids is None:
            distribution_ids = list(self.distributions.keys())
        
        results = {}
        
        for dist_id in distribution_ids:
            if dist_id in self.distributions:
                distribution = self.distributions[dist_id]
                result = distribution.purge_cache(paths)
                results[dist_id] = result
        
        return {
            "success": True,
            "distributions_purged": len(results),
            "results": results,
            "purge_timestamp": datetime.now().isoformat()
        }
    
    def get_performance_metrics(self, distribution_id: str = None, 
                               time_range: int = 24) -> Dict[str, Any]:
        """Get CDN performance metrics"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range)
        
        if distribution_id and distribution_id in self.distributions:
            distributions = [self.distributions[distribution_id]]
        else:
            distributions = list(self.distributions.values())
        
        # Aggregate metrics from all distributions
        total_requests = 0
        total_bandwidth = 0.0
        total_cache_hits = 0
        response_times = []
        
        distribution_metrics = {}
        
        for distribution in distributions:
            analytics = distribution.get_analytics_data(start_time, end_time)
            
            total_requests += analytics["requests"]["total"]
            total_bandwidth += analytics["bandwidth"]["total_gb"]
            total_cache_hits += analytics["requests"]["cached"]
            response_times.append(analytics["performance"]["avg_response_time_ms"])
            
            distribution_metrics[distribution.distribution_id] = analytics
        
        # Calculate aggregated metrics
        cache_hit_ratio = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "summary": {
                "total_requests": total_requests,
                "total_bandwidth_gb": total_bandwidth,
                "cache_hit_ratio": cache_hit_ratio,
                "avg_response_time_ms": avg_response_time,
                "distributions_count": len(distributions),
                "endpoints_count": len(self.global_endpoints)
            },
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": time_range
            },
            "distribution_metrics": distribution_metrics
        }
    
    def optimize_content_delivery(self, path: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized content delivery recommendations"""
        
        # Extract user context
        user_region = user_context.get("region", "us-east-1")
        device_type = user_context.get("device_type", "desktop")
        connection_speed = user_context.get("connection_speed", "fast")
        user_agent = user_context.get("user_agent", "")
        
        # Detect content type
        content_type = self._detect_content_type_from_path(path)
        
        # Find best distribution
        best_distribution = None
        best_score = 0
        
        for distribution in self.distributions.values():
            if not distribution.enabled:
                continue
            
            # Score distribution based on content type and user context
            score = self._score_distribution(distribution, content_type, user_region)
            
            if score > best_score:
                best_score = score
                best_distribution = distribution
        
        if not best_distribution:
            return {"error": "No suitable CDN distribution found"}
        
        # Get optimization parameters
        optimization_params = {}
        
        if content_type == ContentType.IMAGES:
            optimization_params = {
                "format": "auto",
                "quality": 80 if connection_speed == "slow" else 85,
                "resize": "auto" if device_type == "mobile" else "none"
            }
        
        elif content_type == ContentType.VIDEOS:
            optimization_params = {
                "quality": "720p" if connection_speed == "slow" else "1080p",
                "adaptive": "true"
            }
        
        # Generate optimized URL
        optimized_url = best_distribution.generate_cdn_url(path, user_region, optimization_params)
        
        return {
            "optimized_url": optimized_url,
            "distribution_id": best_distribution.distribution_id,
            "content_type": content_type.value,
            "optimization_params": optimization_params,
            "estimated_performance": {
                "cache_hit_probability": 0.85,
                "estimated_load_time_ms": 150,
                "bandwidth_savings": "40%"
            }
        }
    
    def _detect_content_type_from_path(self, path: str) -> ContentType:
        """Detect content type from file path"""
        
        import os
        
        file_ext = os.path.splitext(path)[1].lower()
        
        # Use the same logic as CDNDistribution
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg']:
            return ContentType.IMAGES
        elif file_ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.m3u8', '.mpd']:
            return ContentType.VIDEOS
        elif file_ext in ['.mp3', '.aac', '.ogg', '.wav', '.flac']:
            return ContentType.AUDIO
        elif file_ext in ['.pdf', '.doc', '.docx', '.zip', '.tar', '.gz']:
            return ContentType.DOCUMENTS
        elif file_ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot']:
            return ContentType.STATIC_ASSETS
        elif '/api/' in path:
            return ContentType.API_RESPONSES
        else:
            return ContentType.DYNAMIC_CONTENT
    
    def _score_distribution(self, distribution: CDNDistribution, 
                           content_type: ContentType, user_region: str) -> float:
        """Score distribution for content and user context"""
        
        score = 0.0
        
        # Check if distribution has suitable endpoints
        suitable_endpoints = [ep for ep in distribution.endpoints 
                            if ep.enabled and ep.is_available_in_region(user_region)]
        
        if not suitable_endpoints:
            return 0.0
        
        # Base score from endpoints
        score += len(suitable_endpoints) * 2.0
        
        # Score from content rules
        matching_rules = [rule for rule in distribution.content_rules 
                         if rule.enabled and rule.content_type == content_type]
        
        score += len(matching_rules) * 3.0
        
        # Performance features bonus
        if distribution.analytics_enabled:
            score += 1.0
        
        if distribution.load_balancing_enabled:
            score += 1.0
        
        if distribution.failover_enabled:
            score += 1.0
        
        return score
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get CDN cache statistics"""
        
        total_distributions = len(self.distributions)
        total_endpoints = len(self.global_endpoints)
        enabled_distributions = len([d for d in self.distributions.values() if d.enabled])
        enabled_endpoints = len([e for e in self.global_endpoints.values() if e.enabled])
        
        # Provider distribution
        provider_count = {}
        for endpoint in self.global_endpoints.values():
            provider = endpoint.provider.value
            provider_count[provider] = provider_count.get(provider, 0) + 1
        
        # Content rules count
        total_rules = sum(len(d.content_rules) for d in self.distributions.values())
        
        return {
            "distributions": {
                "total": total_distributions,
                "enabled": enabled_distributions,
                "disabled": total_distributions - enabled_distributions
            },
            "endpoints": {
                "total": total_endpoints,
                "enabled": enabled_endpoints,
                "disabled": total_endpoints - enabled_endpoints,
                "by_provider": provider_count
            },
            "content_rules": {
                "total": total_rules,
                "avg_per_distribution": total_rules / total_distributions if total_distributions > 0 else 0
            },
            "global_settings": {
                "cdn_enabled": self.cdn_enabled,
                "auto_optimization": self.auto_optimization,
                "smart_routing": self.smart_routing,
                "global_load_balancing": self.global_load_balancing
            }
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete CDN configuration"""
        return {
            "cache_statistics": self.get_cache_statistics(),
            "distributions": {dist_id: dist.to_dict() for dist_id, dist in self.distributions.items()},
            "global_endpoints": {ep_id: ep.to_dict() for ep_id, ep in self.global_endpoints.items()},
            "global_settings": {
                "cdn_enabled": self.cdn_enabled,
                "auto_optimization": self.auto_optimization,
                "smart_routing": self.smart_routing,
                "global_load_balancing": self.global_load_balancing
            },
            "default_settings": self.default_settings,
            "performance_settings": self.performance_settings,
            "security_settings": self.security_settings,
            "cost_settings": self.cost_settings,
            "monitoring_settings": self.monitoring_settings
        }

# Global CDN configuration instance
cdn_config = CDNConfiguration()

# Export main classes
__all__ = [
    "CDNConfiguration",
    "CDNProvider",
    "CDNTier",
    "CacheStrategy",
    "ContentType",
    "OptimizationLevel",
    "RoutingStrategy",
    "CDNEndpoint",
    "ContentRule",
    "CDNDistribution",
    "cdn_config"
]
