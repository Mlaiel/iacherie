"""CDN Configuration Module for IA-Influencer Agent Platform
========================================================

Professional Content Delivery Network configuration and edge caching
for multi-format content protection and AI-powered creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class CDNProvider(Enum):
    """CDN provider types"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    MAXCDN = "maxcdn"


class CachePolicy(Enum):
    """CDN cache policies"""
    NO_CACHE = "no_cache"
    SHORT_CACHE = "short_cache"  # 5 minutes
    MEDIUM_CACHE = "medium_cache"  # 1 hour
    LONG_CACHE = "long_cache"  # 1 day
    PERMANENT_CACHE = "permanent_cache"  # 1 year
    CUSTOM = "custom"


@dataclass
class CacheRule:
    """CDN cache rule configuration"""
    path_pattern: str
    cache_policy: CachePolicy
    ttl_seconds: int = 0
    browser_cache_ttl: Optional[int] = None
    edge_cache_ttl: Optional[int] = None
    bypass_cache_on_cookie: bool = False
    cache_key_include_query_string: bool = True
    cache_key_include_headers: List[str] = field(default_factory=list)
    origin_request_headers: Dict[str, str] = field(default_factory=dict)
    response_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class OriginConfig:
    """CDN origin server configuration"""
    domain_name: str
    origin_path: str = ""
    protocol: str = "HTTPS"
    port: int = 443
    connection_timeout: int = 10
    response_timeout: int = 30
    connection_attempts: int = 3
    custom_headers: Dict[str, str] = field(default_factory=dict)
    origin_shield: bool = True
    origin_shield_region: str = "eu-central-1"


@dataclass
class SecurityConfig:
    """CDN security configuration"""
    geo_blocking: Dict[str, List[str]] = field(default_factory=dict)  # {"allow": ["DE", "US"], "block": ["CN"]}
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    rate_limiting: Dict[str, int] = field(default_factory=dict)  # {"requests_per_second": 100}
    waf_enabled: bool = True
    ddos_protection: bool = True
    bot_management: bool = True
    hotlink_protection: bool = True
    secure_token: bool = False


class CDNConfig:
    """
    Professional CDN configuration manager for IA-Influencer Agent Platform.
    
    Manages content delivery and edge caching for:
    - Static assets (JS, CSS, images, fonts)
    - User-generated content (uploads, media files)
    - AI-processed content (fingerprints, thumbnails)
    - API responses (with intelligent caching)
    - Real-time content protection assets
    - Revenue analytics dashboards
    - Multi-region content distribution
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.base_domain = self._get_base_domain()
        self.cdn_provider = self._get_cdn_provider()
        
    def _get_base_domain(self) -> str:
        """Get base domain based on environment"""
        domains = {
            "development": "dev.ia-influencer.com",
            "staging": "staging.ia-influencer.com",
            "production": "ia-influencer.com"
        }
        return domains.get(self.environment, "localhost")
    
    def _get_cdn_provider(self) -> CDNProvider:
        """Get CDN provider based on environment"""
        providers = {
            "development": CDNProvider.CLOUDFLARE,
            "staging": CDNProvider.CLOUDFLARE,
            "production": CDNProvider.AWS_CLOUDFRONT
        }
        return providers.get(self.environment, CDNProvider.CLOUDFLARE)
    
    def get_cache_rules(self) -> List[CacheRule]:
        """Get CDN cache rules for different content types"""
        return [
            # Static assets - long cache
            CacheRule(
                path_pattern="/static/*",
                cache_policy=CachePolicy.PERMANENT_CACHE,
                ttl_seconds=31536000,  # 1 year
                browser_cache_ttl=31536000,
                edge_cache_ttl=31536000,
                cache_key_include_query_string=False,
                response_headers={
                    "Cache-Control": "public, max-age=31536000, immutable",
                    "Access-Control-Allow-Origin": "*"
                }
            ),
            
            # Media files - long cache
            CacheRule(
                path_pattern="/media/*",
                cache_policy=CachePolicy.LONG_CACHE,
                ttl_seconds=2592000,  # 30 days
                browser_cache_ttl=2592000,
                edge_cache_ttl=2592000,
                response_headers={
                    "Cache-Control": "public, max-age=2592000",
                    "Access-Control-Allow-Origin": "*"
                }
            ),
            
            # User uploads - medium cache
            CacheRule(
                path_pattern="/uploads/*",
                cache_policy=CachePolicy.MEDIUM_CACHE,
                ttl_seconds=86400,  # 1 day
                browser_cache_ttl=86400,
                edge_cache_ttl=86400,
                cache_key_include_headers=["Authorization"],
                response_headers={
                    "Cache-Control": "private, max-age=86400",
                    "Vary": "Authorization"
                }
            ),
            
            # AI-processed thumbnails - long cache
            CacheRule(
                path_pattern="/ai/thumbnails/*",
                cache_policy=CachePolicy.LONG_CACHE,
                ttl_seconds=604800,  # 7 days
                browser_cache_ttl=604800,
                edge_cache_ttl=604800,
                cache_key_include_query_string=True,
                response_headers={
                    "Cache-Control": "public, max-age=604800"
                }
            ),
            
            # API responses - short cache for specific endpoints
            CacheRule(
                path_pattern="/api/v1/public/*",
                cache_policy=CachePolicy.SHORT_CACHE,
                ttl_seconds=300,  # 5 minutes
                browser_cache_ttl=300,
                edge_cache_ttl=300,
                cache_key_include_headers=["Accept", "Accept-Language"],
                bypass_cache_on_cookie=True,
                response_headers={
                    "Cache-Control": "public, max-age=300",
                    "Vary": "Accept, Accept-Language"
                }
            ),
            
            # Analytics data - medium cache
            CacheRule(
                path_pattern="/api/v1/analytics/public/*",
                cache_policy=CachePolicy.MEDIUM_CACHE,
                ttl_seconds=1800,  # 30 minutes
                browser_cache_ttl=1800,
                edge_cache_ttl=1800,
                cache_key_include_query_string=True,
                response_headers={
                    "Cache-Control": "public, max-age=1800"
                }
            ),
            
            # Content protection reports - short cache
            CacheRule(
                path_pattern="/api/v1/protection/reports/*",
                cache_policy=CachePolicy.SHORT_CACHE,
                ttl_seconds=600,  # 10 minutes
                browser_cache_ttl=600,
                edge_cache_ttl=600,
                cache_key_include_headers=["Authorization"],
                response_headers={
                    "Cache-Control": "private, max-age=600",
                    "Vary": "Authorization"
                }
            ),
            
            # WebSocket connections - no cache
            CacheRule(
                path_pattern="/ws/*",
                cache_policy=CachePolicy.NO_CACHE,
                ttl_seconds=0,
                browser_cache_ttl=0,
                edge_cache_ttl=0,
                response_headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            ),
            
            # Authentication endpoints - no cache
            CacheRule(
                path_pattern="/api/v1/auth/*",
                cache_policy=CachePolicy.NO_CACHE,
                ttl_seconds=0,
                browser_cache_ttl=0,
                edge_cache_ttl=0,
                response_headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                }
            ),
            
            # Payment endpoints - no cache
            CacheRule(
                path_pattern="/api/v1/payments/*",
                cache_policy=CachePolicy.NO_CACHE,
                ttl_seconds=0,
                browser_cache_ttl=0,
                edge_cache_ttl=0,
                response_headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                }
            ),
            
            # Admin panel - no cache
            CacheRule(
                path_pattern="/admin/*",
                cache_policy=CachePolicy.NO_CACHE,
                ttl_seconds=0,
                browser_cache_ttl=0,
                edge_cache_ttl=0,
                response_headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                }
            )
        ]
    
    def get_origin_configs(self) -> Dict[str, OriginConfig]:
        """Get origin server configurations"""
        return {
            # Main API origin
            "api": OriginConfig(
                domain_name=f"api.{self.base_domain}",
                protocol="HTTPS",
                port=443,
                connection_timeout=10,
                response_timeout=30,
                custom_headers={
                    "X-Forwarded-Proto": "https",
                    "X-CDN-Request": "true",
                    "X-Real-IP": "${remote_addr}"
                },
                origin_shield=True,
                origin_shield_region="eu-central-1"
            ),
            
            # Static assets origin
            "static": OriginConfig(
                domain_name=f"static.{self.base_domain}",
                protocol="HTTPS",
                port=443,
                connection_timeout=5,
                response_timeout=15,
                custom_headers={
                    "X-CDN-Request": "true"
                },
                origin_shield=True
            ),
            
            # Media files origin
            "media": OriginConfig(
                domain_name=f"media.{self.base_domain}",
                protocol="HTTPS",
                port=443,
                connection_timeout=10,
                response_timeout=60,
                custom_headers={
                    "X-CDN-Request": "true"
                },
                origin_shield=True
            ),
            
            # User uploads origin
            "uploads": OriginConfig(
                domain_name=f"uploads.{self.base_domain}",
                protocol="HTTPS",
                port=443,
                connection_timeout=15,
                response_timeout=120,
                custom_headers={
                    "X-CDN-Request": "true",
                    "X-Content-Protection": "active"
                },
                origin_shield=True
            ),
            
            # AI services origin
            "ai": OriginConfig(
                domain_name=f"ai.{self.base_domain}",
                protocol="HTTPS",
                port=443,
                connection_timeout=30,
                response_timeout=300,
                custom_headers={
                    "X-CDN-Request": "true",
                    "X-AI-Service": "true"
                },
                origin_shield=False  # AI processing shouldn't be cached at origin
            )
        }
    
    def get_security_config(self) -> SecurityConfig:
        """Get CDN security configuration"""
        if self.environment == "production":
            return SecurityConfig(
                geo_blocking={
                    "allow": ["DE", "US", "GB", "FR", "CA", "AU", "NL", "CH", "AT", "SE"],
                    "block": ["CN", "RU", "KP", "IR"]
                },
                ip_whitelist=[],  # Add specific IP ranges if needed
                ip_blacklist=[
                    "0.0.0.0/8",
                    "10.0.0.0/8", 
                    "127.0.0.0/8",
                    "169.254.0.0/16",
                    "172.16.0.0/12",
                    "192.168.0.0/16",
                    "224.0.0.0/4",
                    "240.0.0.0/4"
                ],
                rate_limiting={
                    "requests_per_second": 100,
                    "burst_size": 200,
                    "window_size_seconds": 60
                },
                waf_enabled=True,
                ddos_protection=True,
                bot_management=True,
                hotlink_protection=True,
                secure_token=True
            )
        else:
            return SecurityConfig(
                geo_blocking={},
                rate_limiting={
                    "requests_per_second": 50,
                    "burst_size": 100
                },
                waf_enabled=False,
                ddos_protection=True,
                bot_management=False,
                hotlink_protection=False,
                secure_token=False
            )
    
    def get_cloudflare_config(self) -> Dict[str, Any]:
        """Get Cloudflare CDN configuration"""
        cache_rules = self.get_cache_rules()
        origins = self.get_origin_configs()
        security = self.get_security_config()
        
        return {
            "zone": {
                "name": self.base_domain,
                "plan": {
                    "id": "pro" if self.environment == "production" else "free"
                },
                "type": "full"
            },
            "dns_records": [
                {
                    "type": "CNAME",
                    "name": "cdn",
                    "content": f"cdn.{self.base_domain}.cdn.cloudflare.net",
                    "proxied": True,
                    "ttl": 1
                },
                {
                    "type": "CNAME", 
                    "name": "static",
                    "content": f"static.{self.base_domain}",
                    "proxied": True,
                    "ttl": 1
                },
                {
                    "type": "CNAME",
                    "name": "media",
                    "content": f"media.{self.base_domain}",
                    "proxied": True,
                    "ttl": 1
                }
            ],
            "page_rules": [
                {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": f"static.{self.base_domain}/*"}}],
                    "actions": [
                        {"id": "cache_level", "value": "cache_everything"},
                        {"id": "edge_cache_ttl", "value": 31536000},
                        {"id": "browser_cache_ttl", "value": 31536000}
                    ],
                    "priority": 1,
                    "status": "active"
                },
                {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": f"media.{self.base_domain}/*"}}],
                    "actions": [
                        {"id": "cache_level", "value": "cache_everything"},
                        {"id": "edge_cache_ttl", "value": 2592000},
                        {"id": "browser_cache_ttl", "value": 2592000}
                    ],
                    "priority": 2,
                    "status": "active"
                },
                {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": f"api.{self.base_domain}/api/v1/auth/*"}}],
                    "actions": [
                        {"id": "cache_level", "value": "bypass"}
                    ],
                    "priority": 3,
                    "status": "active"
                }
            ],
            "security_settings": {
                "security_level": "high" if self.environment == "production" else "medium",
                "ssl": "full_strict" if self.environment == "production" else "full",
                "min_tls_version": "1.2",
                "always_use_https": True,
                "automatic_https_rewrites": True,
                "opportunistic_encryption": True,
                "ip_geolocation": True,
                "email_obfuscation": True,
                "server_side_exclude": True,
                "hotlink_protection": security.hotlink_protection,
                "rate_limiting": {
                    "enabled": True,
                    "threshold": security.rate_limiting.get("requests_per_second", 100),
                    "period": 60,
                    "action": "challenge"
                }
            },
            "performance_settings": {
                "minify": {
                    "css": True,
                    "js": True,
                    "html": True
                },
                "brotli": True,
                "early_hints": True,
                "http2": True,
                "http3": True,
                "zero_rtt": True,
                "ipv6": True,
                "websockets": True,
                "pseudo_ipv4": True
            },
            "caching_settings": {
                "caching_level": "aggressive",
                "browser_cache_ttl": 14400,  # 4 hours
                "challenge_ttl": 1800,
                "purge_everything": False,
                "development_mode": self.environment == "development",
                "query_string_sort": True,
                "respect_strong_etags": True
            }
        }
    
    def get_aws_cloudfront_config(self) -> Dict[str, Any]:
        """Get AWS CloudFront CDN configuration"""
        cache_rules = self.get_cache_rules()
        origins = self.get_origin_configs()
        security = self.get_security_config()
        
        # Convert cache rules to CloudFront cache behaviors
        cache_behaviors = []
        for rule in cache_rules:
            behavior = {
                "path_pattern": rule.path_pattern,
                "target_origin_id": self._get_origin_id_for_path(rule.path_pattern),
                "viewer_protocol_policy": "redirect-to-https",
                "allowed_methods": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
                "cached_methods": ["GET", "HEAD", "OPTIONS"],
                "compress": True,
                "field_level_encryption_id": None,
                "forwarded_values": {
                    "query_string": rule.cache_key_include_query_string,
                    "cookies": {"forward": "none"},
                    "headers": rule.cache_key_include_headers
                },
                "min_ttl": 0,
                "default_ttl": rule.ttl_seconds,
                "max_ttl": rule.ttl_seconds * 2 if rule.ttl_seconds > 0 else 31536000,
                "smooth_streaming": False,
                "trusted_signers": ["self"] if security.secure_token else []
            }
            cache_behaviors.append(behavior)
        
        return {
            "distribution_config": {
                "caller_reference": f"{self.project_name}-{self.environment}-{self._get_timestamp()}",
                "comment": f"IA-Influencer Agent CDN Distribution - {self.environment}",
                "enabled": True,
                "price_class": "PriceClass_100" if self.environment != "production" else "PriceClass_All",
                "aliases": [
                    f"cdn.{self.base_domain}",
                    f"static.{self.base_domain}",
                    f"media.{self.base_domain}",
                    f"uploads.{self.base_domain}"
                ],
                "origins": [
                    {
                        "id": f"{name}_origin",
                        "domain_name": config.domain_name,
                        "origin_path": config.origin_path,
                        "custom_origin_config": {
                            "http_port": 80,
                            "https_port": config.port,
                            "origin_protocol_policy": "https-only",
                            "origin_ssl_protocols": ["TLSv1.2"],
                            "origin_read_timeout": config.response_timeout,
                            "origin_keepalive_timeout": 5
                        },
                        "custom_headers": [
                            {"header_name": k, "header_value": v}
                            for k, v in config.custom_headers.items()
                        ]
                    }
                    for name, config in origins.items()
                ],
                "default_cache_behavior": {
                    "target_origin_id": "api_origin",
                    "viewer_protocol_policy": "redirect-to-https",
                    "min_ttl": 0,
                    "default_ttl": 86400,
                    "max_ttl": 31536000,
                    "compress": True,
                    "forwarded_values": {
                        "query_string": True,
                        "cookies": {"forward": "all"},
                        "headers": ["*"]
                    },
                    "allowed_methods": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
                    "cached_methods": ["GET", "HEAD"]
                },
                "cache_behaviors": cache_behaviors,
                "custom_error_responses": [
                    {
                        "error_code": 403,
                        "response_page_path": "/errors/403.html",
                        "response_code": "403",
                        "error_caching_min_ttl": 300
                    },
                    {
                        "error_code": 404,
                        "response_page_path": "/errors/404.html", 
                        "response_code": "404",
                        "error_caching_min_ttl": 300
                    },
                    {
                        "error_code": 500,
                        "response_page_path": "/errors/500.html",
                        "response_code": "500",
                        "error_caching_min_ttl": 0
                    }
                ],
                "web_acl_id": f"arn:aws:wafv2:us-east-1:123456789012:global/webacl/{self.project_name}-{self.environment}/12345678-1234-1234-1234-123456789012" if security.waf_enabled else None,
                "viewer_certificate": {
                    "acm_certificate_arn": f"arn:aws:acm:us-east-1:123456789012:certificate/{self.project_name}-{self.environment}",
                    "ssl_support_method": "sni-only",
                    "minimum_protocol_version": "TLSv1.2_2021"
                },
                "restrictions": {
                    "geo_restriction": {
                        "restriction_type": "whitelist" if security.geo_blocking.get("allow") else "none",
                        "locations": security.geo_blocking.get("allow", [])
                    }
                },
                "http_version": "http2",
                "is_ipv6_enabled": True,
                "default_root_object": "index.html",
                "logging": {
                    "enabled": True,
                    "include_cookies": False,
                    "bucket": f"{self.project_name}-{self.environment}-cloudfront-logs.s3.amazonaws.com",
                    "prefix": "cloudfront-logs/"
                }
            }
        }
    
    def get_azure_cdn_config(self) -> Dict[str, Any]:
        """Get Azure CDN configuration"""
        return {
            "profile": {
                "name": f"{self.project_name}-{self.environment}-cdn-profile",
                "location": "Global",
                "sku": {
                    "name": "Standard_Microsoft" if self.environment != "production" else "Premium_Verizon"
                },
                "tags": {
                    "Environment": self.environment,
                    "Project": self.project_name,
                    "Owner": "mlaiel@live.de"
                }
            },
            "endpoints": [
                {
                    "name": f"{self.project_name}-{self.environment}-endpoint",
                    "location": "Global",
                    "origin": {
                        "name": "primary",
                        "host_name": f"api.{self.base_domain}",
                        "http_port": 80,
                        "https_port": 443,
                        "protocol": "HTTPS"
                    },
                    "origin_host_header": f"api.{self.base_domain}",
                    "is_http_allowed": False,
                    "is_https_allowed": True,
                    "query_string_caching_behavior": "BypassCaching",
                    "is_compression_enabled": True,
                    "content_types_to_compress": [
                        "text/plain",
                        "text/html",
                        "text/css",
                        "text/javascript",
                        "application/javascript",
                        "application/json",
                        "application/xml"
                    ],
                    "optimization_type": "GeneralWebDelivery",
                    "probePath": "/health",
                    "geo_filters": [],
                    "delivery_rules": []
                }
            ]
        }
    
    def get_google_cdn_config(self) -> Dict[str, Any]:
        """Get Google Cloud CDN configuration"""
        return {
            "backend_service": {
                "name": f"{self.project_name}-{self.environment}-backend",
                "description": f"Backend service for {self.project_name} {self.environment}",
                "protocol": "HTTPS",
                "port_name": "https",
                "timeout_sec": 30,
                "enable_cdn": True,
                "cdn_policy": {
                    "cache_key_policy": {
                        "include_host": True,
                        "include_protocol": True,
                        "include_query_string": True,
                        "query_string_whitelist": [],
                        "include_http_headers": [],
                        "include_named_cookies": []
                    },
                    "signed_url_cache_max_age_sec": 7200,
                    "default_ttl": 3600,
                    "max_ttl": 86400,
                    "client_ttl": 3600,
                    "negative_caching": True,
                    "negative_caching_policy": [
                        {"code": 404, "ttl": 120},
                        {"code": 403, "ttl": 120}
                    ],
                    "cache_mode": "CACHE_ALL_STATIC",
                    "serve_while_stale": 86400
                },
                "backend": {
                    "group": f"projects/{self._get_project_id()}/zones/europe-west3-a/instanceGroups/{self.project_name}-{self.environment}-ig",
                    "balancing_mode": "UTILIZATION",
                    "capacity_scaler": 1.0,
                    "max_utilization": 0.8
                },
                "health_checks": [
                    f"projects/{self._get_project_id()}/global/healthChecks/{self.project_name}-{self.environment}-hc"
                ],
                "load_balancing_scheme": "EXTERNAL",
                "locality_lb_policy": "ROUND_ROBIN"
            },
            "url_map": {
                "name": f"{self.project_name}-{self.environment}-url-map",
                "default_service": f"projects/{self._get_project_id()}/global/backendServices/{self.project_name}-{self.environment}-backend",
                "path_matchers": [
                    {
                        "name": "static-matcher",
                        "default_service": f"projects/{self._get_project_id()}/global/backendBuckets/{self.project_name}-{self.environment}-static-bucket",
                        "path_rules": [
                            {
                                "paths": ["/static/*", "/media/*"],
                                "service": f"projects/{self._get_project_id()}/global/backendBuckets/{self.project_name}-{self.environment}-static-bucket"
                            }
                        ]
                    }
                ],
                "host_rules": [
                    {
                        "hosts": [f"cdn.{self.base_domain}", f"static.{self.base_domain}"],
                        "path_matcher": "static-matcher"
                    }
                ]
            },
            "target_https_proxy": {
                "name": f"{self.project_name}-{self.environment}-https-proxy",
                "url_map": f"projects/{self._get_project_id()}/global/urlMaps/{self.project_name}-{self.environment}-url-map",
                "ssl_certificates": [
                    f"projects/{self._get_project_id()}/global/sslCertificates/{self.project_name}-{self.environment}-ssl-cert"
                ]
            },
            "global_forwarding_rule": {
                "name": f"{self.project_name}-{self.environment}-https-rule",
                "target": f"projects/{self._get_project_id()}/global/targetHttpsProxies/{self.project_name}-{self.environment}-https-proxy",
                "port_range": "443",
                "ip_protocol": "TCP",
                "load_balancing_scheme": "EXTERNAL"
            }
        }
    
    def _get_origin_id_for_path(self, path_pattern: str) -> str:
        """Get appropriate origin ID for a given path pattern"""
        if path_pattern.startswith("/static"):
            return "static_origin"
        elif path_pattern.startswith("/media"):
            return "media_origin"
        elif path_pattern.startswith("/uploads"):
            return "uploads_origin"
        elif path_pattern.startswith("/ai"):
            return "ai_origin"
        else:
            return "api_origin"
    
    def _get_project_id(self) -> str:
        """Get Google Cloud project ID"""
        return f"{self.project_name}-{self.environment}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for unique identifiers"""
        import time
        return str(int(time.time()))
    
    def generate_cache_purge_script(self) -> str:
        """Generate cache purging script for different CDN providers"""
        script = f"""#!/bin/bash
# CDN Cache Purging Script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
BASE_DOMAIN="{self.base_domain}"
CDN_PROVIDER="{self.cdn_provider.value}"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}}

# Cloudflare cache purge
purge_cloudflare() {{
    log "Purging Cloudflare cache..."
    
    # Purge all cache
    curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/purge_cache" \\
         -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \\
         -H "Content-Type: application/json" \\
         --data '{{"purge_everything":true}}'
    
    # Selective purge for specific paths
    curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/purge_cache" \\
         -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \\
         -H "Content-Type: application/json" \\
         --data '{{
             "files": [
                 "https://static.{self.base_domain}/*",
                 "https://media.{self.base_domain}/*",
                 "https://api.{self.base_domain}/api/v1/public/*"
             ]
         }}'
}}

# AWS CloudFront cache purge
purge_cloudfront() {{
    log "Purging AWS CloudFront cache..."
    
    aws cloudfront create-invalidation \\
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \\
        --paths "/*" \\
        --query "Invalidation.Id" \\
        --output text
}}

# Azure CDN cache purge
purge_azure() {{
    log "Purging Azure CDN cache..."
    
    az cdn endpoint purge \\
        --resource-group $AZURE_RESOURCE_GROUP \\
        --name "{self.project_name}-{self.environment}-endpoint" \\
        --profile-name "{self.project_name}-{self.environment}-cdn-profile" \\
        --content-paths "/*"
}}

# Google Cloud CDN cache purge
purge_google() {{
    log "Purging Google Cloud CDN cache..."
    
    gcloud compute url-maps invalidate-cdn-cache {self.project_name}-{self.environment}-url-map \\
        --path "/*" \\
        --async
}}

# Main purge logic
case "$CDN_PROVIDER" in
    "cloudflare")
        purge_cloudflare
        ;;
    "aws_cloudfront")
        purge_cloudfront
        ;;
    "azure_cdn")
        purge_azure
        ;;
    "google_cdn")
        purge_google
        ;;
    *)
        log "ERROR: Unknown CDN provider: $CDN_PROVIDER"
        exit 1
        ;;
esac

log "Cache purging completed for $CDN_PROVIDER"
"""
        return script
    
    def export_configurations(self, output_dir: str = "./cdn-configs") -> Dict[str, str]:
        """Export all CDN configurations to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        
        # Cloudflare configuration
        cloudflare_config = self.get_cloudflare_config()
        cloudflare_path = os.path.join(output_dir, f"cloudflare-{self.environment}.json")
        with open(cloudflare_path, 'w') as f:
            json.dump(cloudflare_config, f, indent=2)
        configs['cloudflare'] = cloudflare_path
        
        # AWS CloudFront configuration
        cloudfront_config = self.get_aws_cloudfront_config()
        cloudfront_path = os.path.join(output_dir, f"aws-cloudfront-{self.environment}.json")
        with open(cloudfront_path, 'w') as f:
            json.dump(cloudfront_config, f, indent=2)
        configs['aws_cloudfront'] = cloudfront_path
        
        # Azure CDN configuration
        azure_config = self.get_azure_cdn_config()
        azure_path = os.path.join(output_dir, f"azure-cdn-{self.environment}.json")
        with open(azure_path, 'w') as f:
            json.dump(azure_config, f, indent=2)
        configs['azure_cdn'] = azure_path
        
        # Google CDN configuration
        google_config = self.get_google_cdn_config()
        google_path = os.path.join(output_dir, f"google-cdn-{self.environment}.json")
        with open(google_path, 'w') as f:
            json.dump(google_config, f, indent=2)
        configs['google_cdn'] = google_path
        
        # Cache purge script
        purge_script = self.generate_cache_purge_script()
        purge_path = os.path.join(output_dir, f"purge-cache-{self.environment}.sh")
        with open(purge_path, 'w') as f:
            f.write(purge_script)
        os.chmod(purge_path, 0o755)
        configs['purge_script'] = purge_path
        
        return configs
