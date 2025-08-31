"""CDN Configuration for IA-Influencer Agent Platform
==================================================

Professional Content Delivery Network configuration for global content distribution.

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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class CDNProvider(Enum):
    """Supported CDN providers."""    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    BUNNY_CDN = "bunny_cdn"

@dataclass
class CDNEndpointConfig:
    """CDN endpoint configuration for specific content types."""    
    name: str
    provider: CDNProvider
    domain: str
    origin_url: str
    cache_behaviors: Dict[str, Any]
    security_settings: Dict[str, Any]
    compression_enabled: bool = True
    gzip_enabled: bool = True
    brotli_enabled: bool = True

@dataclass
class CloudflareCDNConfig:
    """Cloudflare CDN specific configuration."""    
    zone_id: str = os.getenv('CLOUDFLARE_ZONE_ID', '')
    api_token: str = os.getenv('CLOUDFLARE_API_TOKEN', '')
    email: str = os.getenv('CLOUDFLARE_EMAIL', '')
    api_key: str = os.getenv('CLOUDFLARE_API_KEY', '')
    
    # Security settings
    security_level: str = 'medium'  # off, essentially_off, low, medium, high, under_attack
    ssl_mode: str = 'flexible'  # off, flexible, full, strict
    min_tls_version: str = '1.2'
    
    # Performance settings
    cache_level: str = 'aggressive'  # basic, simplified, aggressive
    browser_cache_ttl: int = 31536000  # 1 year
    edge_cache_ttl: int = 7776000  # 90 days
    
    # Optimization
    minify_css: bool = True
    minify_js: bool = True
    minify_html: bool = True
    auto_minify: bool = True
    rocket_loader: bool = True
    polish: str = 'lossy'  # off, lossless, lossy

@dataclass
class AWSCloudFrontConfig:
    """AWS CloudFront CDN specific configuration."""    
    access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID', '')
    secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    region: str = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    # Distribution settings
    price_class: str = 'PriceClass_All'  # PriceClass_100, PriceClass_200, PriceClass_All
    http_version: str = 'http2'
    ipv6_enabled: bool = True
    
    # Cache behaviors
    default_cache_behavior: Dict[str, Any] = None
    cache_behaviors: List[Dict[str, Any]] = None
    
    # Security
    viewer_protocol_policy: str = 'redirect-to-https'
    ssl_support_method: str = 'sni-only'
    minimum_protocol_version: str = 'TLSv1.2_2021'
    
    def __post_init__(self):
        if self.default_cache_behavior is None:
            self.default_cache_behavior = {
                'target_origin_id': 'default',
                'viewer_protocol_policy': self.viewer_protocol_policy,
                'allowed_methods': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                'cached_methods': ['GET', 'HEAD'],
                'compress': True,
                'query_string': False,
                'forward_cookies': 'none',
                'min_ttl': 0,
                'default_ttl': 86400,  # 1 day
                'max_ttl': 31536000   # 1 year
            }

@dataclass
class CDNConfig:
    """    Comprehensive CDN configuration for IA-Influencer Agent platform.
    Provides enterprise-grade content delivery with multiple provider support.
    """    
    # Primary CDN provider
    primary_provider: CDNProvider = CDNProvider.CLOUDFLARE
    
    # Fallback CDN provider
    fallback_provider: Optional[CDNProvider] = CDNProvider.AWS_CLOUDFRONT
    
    # CDN endpoints for different content types
    endpoints: Dict[str, CDNEndpointConfig] = None
    
    # Provider-specific configurations
    cloudflare_config: CloudflareCDNConfig = None
    aws_cloudfront_config: AWSCloudFrontConfig = None
    
    # Global CDN settings
    enable_compression: bool = True
    enable_http2: bool = True
    enable_http3: bool = True
    enable_brotli: bool = True
    
    # Security settings
    enable_ddos_protection: bool = True
    enable_waf: bool = True
    enable_rate_limiting: bool = True
    
    # Performance settings
    edge_caching: bool = True
    prefetch_enabled: bool = True
    preload_enabled: bool = True
    
    # Monitoring
    enable_analytics: bool = True
    enable_real_user_monitoring: bool = True
    
    def __post_init__(self):
        """Initialize configurations if not provided."""        if self.endpoints is None:
            self.endpoints = self._get_default_endpoints()
        
        if self.cloudflare_config is None:
            self.cloudflare_config = CloudflareCDNConfig()
        
        if self.aws_cloudfront_config is None:
            self.aws_cloudfront_config = AWSCloudFrontConfig()
    
    def _get_default_endpoints(self) -> Dict[str, CDNEndpointConfig]:
        """Default CDN endpoint configuration for different content types."""        env = os.getenv('ENVIRONMENT', 'development')
        base_domain = os.getenv('CDN_BASE_DOMAIN', 'cdn.ia-influencer.com')
        origin_domain = os.getenv('ORIGIN_DOMAIN', 'api.ia-influencer.com')
        
        return {
            'images': CDNEndpointConfig(
                name=f"images-{env}",
                provider=self.primary_provider,
                domain=f"images.{base_domain}",
                origin_url=f"https://{origin_domain}/storage/images",
                cache_behaviors={
                    'default_ttl': 86400,  # 1 day
                    'max_ttl': 31536000,   # 1 year
                    'min_ttl': 3600,       # 1 hour
                    'query_string_forwarding': False,
                    'cookie_forwarding': 'none',
                    'headers_forwarding': ['Accept', 'Accept-Encoding']
                },
                security_settings={
                    'allowed_methods': ['GET', 'HEAD'],
                    'restrict_viewer_access': False,
                    'trusted_signers': [],
                    'origin_access_identity': True
                },
                compression_enabled=True,
                gzip_enabled=True,
                brotli_enabled=True
            ),
            'audio': CDNEndpointConfig(
                name=f"audio-{env}",
                provider=self.primary_provider,
                domain=f"audio.{base_domain}",
                origin_url=f"https://{origin_domain}/storage/audio",
                cache_behaviors={
                    'default_ttl': 3600,   # 1 hour
                    'max_ttl': 86400,      # 1 day
                    'min_ttl': 0,
                    'query_string_forwarding': True,  # For streaming parameters
                    'cookie_forwarding': 'none',
                    'headers_forwarding': ['Range', 'Accept-Ranges', 'Content-Type']
                },
                security_settings={
                    'allowed_methods': ['GET', 'HEAD'],
                    'restrict_viewer_access': True,  # Protected content
                    'trusted_signers': ['self'],
                    'origin_access_identity': True
                },
                compression_enabled=False,  # Audio files are already compressed
                gzip_enabled=False,
                brotli_enabled=False
            ),
            'video': CDNEndpointConfig(
                name=f"video-{env}",
                provider=self.primary_provider,
                domain=f"video.{base_domain}",
                origin_url=f"https://{origin_domain}/storage/video",
                cache_behaviors={
                    'default_ttl': 7200,   # 2 hours
                    'max_ttl': 86400,      # 1 day
                    'min_ttl': 0,
                    'query_string_forwarding': True,  # For streaming parameters
                    'cookie_forwarding': 'none',
                    'headers_forwarding': ['Range', 'Accept-Ranges', 'Content-Type']
                },
                security_settings={
                    'allowed_methods': ['GET', 'HEAD'],
                    'restrict_viewer_access': True,  # Protected content
                    'trusted_signers': ['self'],
                    'origin_access_identity': True
                },
                compression_enabled=False,  # Video files are already compressed
                gzip_enabled=False,
                brotli_enabled=False
            ),
            'documents': CDNEndpointConfig(
                name=f"documents-{env}",
                provider=self.primary_provider,
                domain=f"docs.{base_domain}",
                origin_url=f"https://{origin_domain}/storage/documents",
                cache_behaviors={
                    'default_ttl': 3600,   # 1 hour
                    'max_ttl': 86400,      # 1 day
                    'min_ttl': 0,
                    'query_string_forwarding': False,
                    'cookie_forwarding': 'none',
                    'headers_forwarding': ['Accept', 'Accept-Encoding']
                },
                security_settings={
                    'allowed_methods': ['GET', 'HEAD'],
                    'restrict_viewer_access': True,  # Private documents
                    'trusted_signers': ['self'],
                    'origin_access_identity': True
                },
                compression_enabled=True,
                gzip_enabled=True,
                brotli_enabled=True
            ),
            'static': CDNEndpointConfig(
                name=f"static-{env}",
                provider=self.primary_provider,
                domain=f"static.{base_domain}",
                origin_url=f"https://{origin_domain}/static",
                cache_behaviors={
                    'default_ttl': 86400,  # 1 day
                    'max_ttl': 31536000,   # 1 year
                    'min_ttl': 3600,       # 1 hour
                    'query_string_forwarding': False,
                    'cookie_forwarding': 'none',
                    'headers_forwarding': ['Accept', 'Accept-Encoding']
                },
                security_settings={
                    'allowed_methods': ['GET', 'HEAD'],
                    'restrict_viewer_access': False,  # Public static assets
                    'trusted_signers': [],
                    'origin_access_identity': False
                },
                compression_enabled=True,
                gzip_enabled=True,
                brotli_enabled=True
            )
        }
    
    def get_endpoint_url(self, content_type: str, file_path: str = '') -> str:
        """Get CDN URL for specific content type and file."""        if content_type not in self.endpoints:
            content_type = 'static'  # Fallback
        
        endpoint = self.endpoints[content_type]
        base_url = f"https://{endpoint.domain}"
        
        if file_path:
            return f"{base_url}/{file_path.lstrip('/')}"
        return base_url
    
    def get_content_types(self) -> List[str]:
        """Get list of supported content types."""        return list(self.endpoints.keys())
    
    def validate_configuration(self) -> bool:
        """Validate CDN configuration."""        try:
            # Validate primary provider configuration
            if self.primary_provider == CDNProvider.CLOUDFLARE:
                if not self.cloudflare_config.zone_id or not self.cloudflare_config.api_token:
                    print("Cloudflare configuration incomplete")
                    return False
            
            elif self.primary_provider == CDNProvider.AWS_CLOUDFRONT:
                if not self.aws_cloudfront_config.access_key_id or not self.aws_cloudfront_config.secret_access_key:
                    print("AWS CloudFront configuration incomplete")
                    return False
            
            # Validate endpoints
            for name, endpoint in self.endpoints.items():
                if not endpoint.domain or not endpoint.origin_url:
                    print(f"Endpoint {name} configuration incomplete")
                    return False
            
            return True
        except Exception as e:
            print(f"CDN configuration validation failed: {e}")
            return False
    
    def get_cache_control_headers(self, content_type: str) -> Dict[str, str]:
        """Get appropriate cache control headers for content type."""        if content_type not in self.endpoints:
            content_type = 'static'
        
        endpoint = self.endpoints[content_type]
        cache_behaviors = endpoint.cache_behaviors
        
        headers = {}
        
        if cache_behaviors.get('default_ttl'):
            headers['Cache-Control'] = f"public, max-age={cache_behaviors['default_ttl']}"
        
        if endpoint.compression_enabled:
            headers['Vary'] = 'Accept-Encoding'
        
        # Content-specific headers
        if content_type in ['audio', 'video']:
            headers['Accept-Ranges'] = 'bytes'
        
        return headers
    
    def get_purge_urls(self, content_type: str, file_paths: List[str]) -> List[str]:
        """Get URLs to purge from CDN cache."""        urls = []
        for file_path in file_paths:
            url = self.get_endpoint_url(content_type, file_path)
            urls.append(url)
        return urls
    
    def get_provider_specific_config(self, provider: CDNProvider) -> Dict[str, Any]:
        """Get provider-specific configuration."""        if provider == CDNProvider.CLOUDFLARE:
            return {
                'zone_id': self.cloudflare_config.zone_id,
                'api_token': self.cloudflare_config.api_token,
                'security_level': self.cloudflare_config.security_level,
                'ssl_mode': self.cloudflare_config.ssl_mode,
                'cache_level': self.cloudflare_config.cache_level
            }
        
        elif provider == CDNProvider.AWS_CLOUDFRONT:
            return {
                'access_key_id': self.aws_cloudfront_config.access_key_id,
                'secret_access_key': self.aws_cloudfront_config.secret_access_key,
                'region': self.aws_cloudfront_config.region,
                'price_class': self.aws_cloudfront_config.price_class
            }
        
        return {}
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export CDN configuration to JSON-serializable format."""        return {
            'primary_provider': self.primary_provider.value,
            'fallback_provider': self.fallback_provider.value if self.fallback_provider else None,
            'enable_compression': self.enable_compression,
            'enable_http2': self.enable_http2,
            'enable_http3': self.enable_http3,
            'enable_brotli': self.enable_brotli,
            'enable_ddos_protection': self.enable_ddos_protection,
            'enable_waf': self.enable_waf,
            'endpoints': {
                name: {
                    'name': config.name,
                    'provider': config.provider.value,
                    'domain': config.domain,
                    'origin_url': config.origin_url,
                    'compression_enabled': config.compression_enabled
                }
                for name, config in self.endpoints.items()
            }
        }

# Global CDN configuration instance
cdn_config = CDNConfig()
