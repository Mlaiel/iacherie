#!/usr/bin/env python3
"""
Enhanced CDN Caching Rules Implementation
Comprehensive CDN cache configuration with intelligent rules and geographic optimization
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CDNProvider(Enum):
    """CDN provider types"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    CUSTOM = "custom"

class CachePolicy(Enum):
    """CDN cache policies"""
    NO_CACHE = "no_cache"
    SHORT_CACHE = "short_cache"      # 5 minutes
    MEDIUM_CACHE = "medium_cache"    # 1 hour  
    LONG_CACHE = "long_cache"        # 1 day
    PERMANENT_CACHE = "permanent_cache"  # 1 year
    DYNAMIC = "dynamic"              # Based on content analysis

class ContentType(Enum):
    """Content types for caching rules"""
    STATIC_ASSETS = "static_assets"
    MEDIA_FILES = "media_files"
    API_RESPONSES = "api_responses"
    USER_CONTENT = "user_content"
    AI_GENERATED = "ai_generated"
    THUMBNAILS = "thumbnails"
    AUDIO_FILES = "audio_files"
    DOCUMENTS = "documents"
    FONTS = "fonts"
    SCRIPTS = "scripts"
    STYLESHEETS = "stylesheets"

class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    BROTLI = "brotli"
    AUTO = "auto"

@dataclass
class CacheRule:
    """CDN cache rule definition"""
    name: str
    path_pattern: str
    content_type: ContentType
    cache_policy: CachePolicy
    ttl_seconds: int
    browser_cache_ttl: Optional[int] = None
    edge_cache_ttl: Optional[int] = None
    origin_cache_ttl: Optional[int] = None
    
    # Advanced options
    compression: CompressionType = CompressionType.AUTO
    cache_key_include_query_string: bool = False
    cache_key_include_headers: List[str] = field(default_factory=list)
    vary_headers: List[str] = field(default_factory=list)
    ignore_headers: List[str] = field(default_factory=list)
    
    # Geographic caching
    geographic_regions: List[str] = field(default_factory=list)
    regional_ttl_overrides: Dict[str, int] = field(default_factory=dict)
    
    # Security and access
    require_authentication: bool = False
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)
    
    # Response modification
    response_headers: Dict[str, str] = field(default_factory=dict)
    strip_headers: List[str] = field(default_factory=list)
    
    # Optimization
    optimization_rules: List[str] = field(default_factory=list)
    minification_enabled: bool = False
    image_optimization: bool = False
    
    # Conditions
    cache_conditions: List[str] = field(default_factory=list)
    bypass_conditions: List[str] = field(default_factory=list)

@dataclass
class CDNConfig:
    """CDN configuration"""
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    domain: str = "cdn.ainflue.com"
    origin_domain: str = "api.ainflue.com"
    ssl_enabled: bool = True
    http2_enabled: bool = True
    ipv6_enabled: bool = True
    
    # Global settings
    global_ttl: int = 3600
    browser_cache_ttl: int = 86400
    negative_cache_ttl: int = 300
    
    # Security
    security_headers_enabled: bool = True
    rate_limiting_enabled: bool = True
    ddos_protection_enabled: bool = True
    
    # Analytics
    analytics_enabled: bool = True
    real_user_monitoring: bool = True
    
    # Geographic
    geographic_distribution: bool = True
    edge_locations: List[str] = field(default_factory=lambda: ["US", "EU", "AP"])

class EnhancedCDNCacheManager:
    """
    Enhanced CDN Cache Rules Manager
    
    Features:
    - Content-type specific caching
    - Geographic optimization
    - Dynamic TTL calculation
    - Intelligent compression
    - Performance monitoring
    - A/B testing support
    """
    
    def __init__(self, config: CDNConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EnhancedCDNCacheManager")
        self.cache_rules: List[CacheRule] = []
        
        # Performance metrics
        self.metrics = {
            "cache_hit_ratio": 0.0,
            "avg_response_time": 0.0,
            "bandwidth_saved": 0,
            "requests_served": 0
        }
    
    def initialize(self):
        """Initialize CDN cache manager with default rules"""
        self.logger.info("🔧 Initializing enhanced CDN cache manager...")
        
        # Load default cache rules
        self._load_default_cache_rules()
        
        # Apply geographic optimizations
        self._apply_geographic_optimizations()
        
        self.logger.info(f"✅ CDN cache manager initialized with {len(self.cache_rules)} rules")
    
    def _load_default_cache_rules(self):
        """Load comprehensive default cache rules"""
        
        # Static assets - very long cache
        self.add_cache_rule(CacheRule(
            name="static_assets_permanent",
            path_pattern="/static/*",
            content_type=ContentType.STATIC_ASSETS,
            cache_policy=CachePolicy.PERMANENT_CACHE,
            ttl_seconds=31536000,  # 1 year
            browser_cache_ttl=31536000,
            edge_cache_ttl=31536000,
            compression=CompressionType.BROTLI,
            cache_key_include_query_string=True,  # For versioning
            response_headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "Access-Control-Allow-Origin": "*"
            },
            optimization_rules=["minify", "combine"],
            minification_enabled=True
        ))
        
        # Font files - very long cache with CORS
        self.add_cache_rule(CacheRule(
            name="fonts_permanent",
            path_pattern="*.woff2,*.woff,*.ttf,*.eot",
            content_type=ContentType.FONTS,
            cache_policy=CachePolicy.PERMANENT_CACHE,
            ttl_seconds=31536000,  # 1 year
            browser_cache_ttl=31536000,
            compression=CompressionType.NONE,  # Already compressed
            cors_enabled=True,
            cors_origins=["*"],
            response_headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "Access-Control-Allow-Origin": "*"
            }
        ))
        
        # CSS/JS files - long cache with versioning
        self.add_cache_rule(CacheRule(
            name="scripts_stylesheets",
            path_pattern="*.css,*.js",
            content_type=ContentType.SCRIPTS,
            cache_policy=CachePolicy.PERMANENT_CACHE,
            ttl_seconds=31536000,  # 1 year
            browser_cache_ttl=31536000,
            compression=CompressionType.BROTLI,
            cache_key_include_query_string=True,
            optimization_rules=["minify", "combine", "gzip_precompression"],
            minification_enabled=True,
            response_headers={
                "Cache-Control": "public, max-age=31536000, immutable"
            }
        ))
        
        # Media files - long cache with optimization
        self.add_cache_rule(CacheRule(
            name="media_files",
            path_pattern="/media/*,*.jpg,*.jpeg,*.png,*.gif,*.webp,*.svg",
            content_type=ContentType.MEDIA_FILES,
            cache_policy=CachePolicy.LONG_CACHE,
            ttl_seconds=2592000,  # 30 days
            browser_cache_ttl=2592000,
            compression=CompressionType.AUTO,
            image_optimization=True,
            response_headers={
                "Cache-Control": "public, max-age=2592000",
                "Access-Control-Allow-Origin": "*"
            },
            optimization_rules=["image_optimization", "webp_conversion"]
        ))
        
        # AI-generated thumbnails - medium cache
        self.add_cache_rule(CacheRule(
            name="ai_thumbnails",
            path_pattern="/ai/thumbnails/*",
            content_type=ContentType.AI_GENERATED,
            cache_policy=CachePolicy.LONG_CACHE,
            ttl_seconds=604800,  # 7 days
            browser_cache_ttl=604800,
            image_optimization=True,
            cache_key_include_query_string=True,  # For parameters
            response_headers={
                "Cache-Control": "public, max-age=604800"
            }
        ))
        
        # User uploaded content - medium cache with auth
        self.add_cache_rule(CacheRule(
            name="user_uploads",
            path_pattern="/uploads/*",
            content_type=ContentType.USER_CONTENT,
            cache_policy=CachePolicy.MEDIUM_CACHE,
            ttl_seconds=86400,  # 1 day
            browser_cache_ttl=86400,
            require_authentication=True,
            cache_key_include_headers=["Authorization"],
            vary_headers=["Authorization"],
            response_headers={
                "Cache-Control": "private, max-age=86400"
            }
        ))
        
        # Audio files - long cache
        self.add_cache_rule(CacheRule(
            name="audio_files",
            path_pattern="*.mp3,*.wav,*.m4a,*.ogg,*.flac",
            content_type=ContentType.AUDIO_FILES,
            cache_policy=CachePolicy.LONG_CACHE,
            ttl_seconds=2592000,  # 30 days
            browser_cache_ttl=2592000,
            compression=CompressionType.NONE,  # Audio already compressed
            response_headers={
                "Cache-Control": "public, max-age=2592000",
                "Accept-Ranges": "bytes"  # Enable range requests
            }
        ))
        
        # API responses - short to medium cache
        self.add_cache_rule(CacheRule(
            name="api_responses_public",
            path_pattern="/api/v1/public/*",
            content_type=ContentType.API_RESPONSES,
            cache_policy=CachePolicy.MEDIUM_CACHE,
            ttl_seconds=1800,  # 30 minutes
            browser_cache_ttl=900,  # 15 minutes
            compression=CompressionType.BROTLI,
            cache_key_include_query_string=True,
            response_headers={
                "Cache-Control": "public, max-age=900, s-maxage=1800"
            }
        ))
        
        # API responses - authenticated content
        self.add_cache_rule(CacheRule(
            name="api_responses_private",
            path_pattern="/api/v1/user/*,/api/v1/dashboard/*",
            content_type=ContentType.API_RESPONSES,
            cache_policy=CachePolicy.SHORT_CACHE,
            ttl_seconds=300,  # 5 minutes
            browser_cache_ttl=60,  # 1 minute
            require_authentication=True,
            cache_key_include_headers=["Authorization"],
            vary_headers=["Authorization"],
            response_headers={
                "Cache-Control": "private, max-age=60, s-maxage=300"
            }
        ))
        
        # Documents - medium cache
        self.add_cache_rule(CacheRule(
            name="documents",
            path_pattern="*.pdf,*.doc,*.docx,*.txt",
            content_type=ContentType.DOCUMENTS,
            cache_policy=CachePolicy.MEDIUM_CACHE,
            ttl_seconds=86400,  # 1 day
            browser_cache_ttl=86400,
            compression=CompressionType.GZIP,
            response_headers={
                "Cache-Control": "public, max-age=86400"
            }
        ))
        
        # No cache for dynamic/sensitive content
        self.add_cache_rule(CacheRule(
            name="no_cache_dynamic",
            path_pattern="/api/v1/auth/*,/api/v1/payments/*,/admin/*",
            content_type=ContentType.API_RESPONSES,
            cache_policy=CachePolicy.NO_CACHE,
            ttl_seconds=0,
            response_headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        ))
    
    def _apply_geographic_optimizations(self):
        """Apply geographic caching optimizations"""
        if not self.config.geographic_distribution:
            return
        
        # Regional TTL overrides for different content types
        regional_overrides = {
            "US": {
                ContentType.MEDIA_FILES: 3600,      # Shorter for US (more updates)
                ContentType.API_RESPONSES: 900      # Shorter cache for dynamic content
            },
            "EU": {
                ContentType.MEDIA_FILES: 7200,      # Longer for EU (GDPR considerations)
                ContentType.API_RESPONSES: 1800
            },
            "AP": {
                ContentType.MEDIA_FILES: 10800,     # Longest for AP (bandwidth considerations)
                ContentType.API_RESPONSES: 2700
            }
        }
        
        # Apply regional overrides to existing rules
        for rule in self.cache_rules:
            if rule.content_type in regional_overrides.get("US", {}):
                rule.geographic_regions = list(regional_overrides.keys())
                rule.regional_ttl_overrides = {
                    region: overrides.get(rule.content_type, rule.ttl_seconds)
                    for region, overrides in regional_overrides.items()
                }
    
    def add_cache_rule(self, rule: CacheRule):
        """Add cache rule to the configuration"""
        self.cache_rules.append(rule)
        self.logger.debug(f"Added cache rule: {rule.name}")
    
    def get_cache_rules(self) -> List[CacheRule]:
        """Get all cache rules"""
        return self.cache_rules
    
    def get_rule_for_path(self, path: str) -> Optional[CacheRule]:
        """Get applicable cache rule for a specific path"""
        import fnmatch
        
        for rule in self.cache_rules:
            # Handle multiple patterns separated by commas
            patterns = rule.path_pattern.split(',')
            for pattern in patterns:
                pattern = pattern.strip()
                if fnmatch.fnmatch(path, pattern) or path.startswith(pattern.rstrip('*')):
                    return rule
        
        return None
    
    def calculate_dynamic_ttl(self, path: str, content_size: int, 
                            access_frequency: float) -> int:
        """Calculate dynamic TTL based on content characteristics"""
        try:
            rule = self.get_rule_for_path(path)
            if not rule or rule.cache_policy != CachePolicy.DYNAMIC:
                return rule.ttl_seconds if rule else self.config.global_ttl
            
            base_ttl = rule.ttl_seconds
            
            # Adjust based on content size (larger files cache longer)
            size_factor = min(2.0, max(0.5, content_size / 1048576))  # Based on MB
            
            # Adjust based on access frequency (popular content caches longer)
            frequency_factor = min(3.0, max(0.3, access_frequency))
            
            # Calculate dynamic TTL
            dynamic_ttl = int(base_ttl * size_factor * frequency_factor)
            
            # Apply reasonable bounds
            return min(max(dynamic_ttl, 300), 86400)  # Between 5 minutes and 1 day
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic TTL: {e}")
            return self.config.global_ttl
    
    def generate_cache_headers(self, rule: CacheRule, 
                             region: Optional[str] = None) -> Dict[str, str]:
        """Generate appropriate cache headers for a rule"""
        headers = {}
        
        # Get TTL (with regional override if applicable)
        ttl = rule.ttl_seconds
        if region and region in rule.regional_ttl_overrides:
            ttl = rule.regional_ttl_overrides[region]
        
        browser_ttl = rule.browser_cache_ttl or ttl
        
        # Cache-Control header
        if rule.cache_policy == CachePolicy.NO_CACHE:
            headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
        elif rule.require_authentication:
            headers["Cache-Control"] = f"private, max-age={browser_ttl}"
        else:
            cache_control_parts = [f"public", f"max-age={browser_ttl}"]
            if ttl != browser_ttl:
                cache_control_parts.append(f"s-maxage={ttl}")
            if rule.cache_policy == CachePolicy.PERMANENT_CACHE:
                cache_control_parts.append("immutable")
            
            headers["Cache-Control"] = ", ".join(cache_control_parts)
        
        # Vary header
        if rule.vary_headers:
            headers["Vary"] = ", ".join(rule.vary_headers)
        
        # CORS headers
        if rule.cors_enabled:
            headers["Access-Control-Allow-Origin"] = ", ".join(rule.cors_origins) or "*"
            headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
            headers["Access-Control-Max-Age"] = str(ttl)
        
        # Custom response headers
        headers.update(rule.response_headers)
        
        return headers
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate CDN cache configuration"""
        issues = []
        warnings = []
        
        # Check for conflicting rules
        path_patterns = {}
        for rule in self.cache_rules:
            patterns = rule.path_pattern.split(',')
            for pattern in patterns:
                pattern = pattern.strip()
                if pattern in path_patterns:
                    issues.append(f"Conflicting rules for pattern '{pattern}': {path_patterns[pattern]} and {rule.name}")
                else:
                    path_patterns[pattern] = rule.name
        
        # Check TTL values
        for rule in self.cache_rules:
            if rule.ttl_seconds < 0:
                issues.append(f"Rule '{rule.name}' has negative TTL: {rule.ttl_seconds}")
            elif rule.ttl_seconds > 31536000:  # 1 year
                warnings.append(f"Rule '{rule.name}' has very long TTL: {rule.ttl_seconds}")
        
        # Check compression settings
        for rule in self.cache_rules:
            if (rule.content_type in [ContentType.AUDIO_FILES, ContentType.MEDIA_FILES] and 
                rule.compression != CompressionType.NONE):
                warnings.append(f"Rule '{rule.name}' applies compression to already compressed content")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_rules": len(self.cache_rules)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get CDN performance metrics"""
        return {
            **self.metrics,
            "cache_rules_count": len(self.cache_rules),
            "geographic_regions": len(self.config.edge_locations),
            "compression_enabled": sum(1 for rule in self.cache_rules 
                                     if rule.compression != CompressionType.NONE),
            "optimization_rules": sum(len(rule.optimization_rules) for rule in self.cache_rules)
        }
    
    def export_configuration(self, format: str = "json") -> str:
        """Export cache configuration"""
        if format == "json":
            config_data = {
                "version": "1.0",
                "generated": datetime.now().isoformat(),
                "provider": self.config.provider.value,
                "domain": self.config.domain,
                "global_settings": {
                    "global_ttl": self.config.global_ttl,
                    "browser_cache_ttl": self.config.browser_cache_ttl,
                    "ssl_enabled": self.config.ssl_enabled,
                    "http2_enabled": self.config.http2_enabled
                },
                "cache_rules": [
                    {
                        "name": rule.name,
                        "path_pattern": rule.path_pattern,
                        "content_type": rule.content_type.value,
                        "cache_policy": rule.cache_policy.value,
                        "ttl_seconds": rule.ttl_seconds,
                        "compression": rule.compression.value,
                        "optimization_rules": rule.optimization_rules,
                        "response_headers": rule.response_headers
                    }
                    for rule in self.cache_rules
                ]
            }
            return json.dumps(config_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Factory function to create CDN manager with environment configuration
def create_cdn_manager_from_env() -> EnhancedCDNCacheManager:
    """Create CDN cache manager from environment variables"""
    
    config = CDNConfig(
        provider=CDNProvider(os.getenv("CDN_PROVIDER", "cloudflare")),
        domain=os.getenv("CDN_DOMAIN", "cdn.ainflue.com"),
        origin_domain=os.getenv("CDN_ORIGIN_DOMAIN", "api.ainflue.com"),
        ssl_enabled=os.getenv("CDN_SSL_ENABLED", "true").lower() == "true",
        http2_enabled=os.getenv("CDN_HTTP2_ENABLED", "true").lower() == "true",
        global_ttl=int(os.getenv("CDN_GLOBAL_TTL", "3600")),
        browser_cache_ttl=int(os.getenv("CDN_BROWSER_CACHE_TTL", "86400")),
        geographic_distribution=os.getenv("CDN_GEOGRAPHIC", "true").lower() == "true"
    )
    
    manager = EnhancedCDNCacheManager(config)
    manager.initialize()
    return manager

# Export main components
__all__ = [
    'EnhancedCDNCacheManager',
    'CacheRule',
    'CDNConfig',
    'ContentType',
    'CachePolicy',
    'CompressionType',
    'create_cdn_manager_from_env'
]