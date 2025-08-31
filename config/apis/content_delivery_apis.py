"""Content Delivery APIs Configuration - IA-Influencer Agent Platform
=================================================================
Professional CDN and content delivery APIs configuration for
multi-format content distribution and streaming.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️ PROPRIÉTÉ EXCLUSIVE DE FAHED MLAIEL
Toute tentative de copie, vol ou réutilisation sans autorisation écrite
de Fahed Mlaiel (mlaiel@live.de) sera poursuivie en justice selon la loi allemande.
"""from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
from decimal import Decimal


class CDNProvider(Enum):
    """Content Delivery Network providers enumeration."""    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"


class ContentType(Enum):
    """Content types for delivery optimization."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    STREAM = "stream"
    API_RESPONSE = "api_response"


@dataclass
class CDNEndpointConfig:
    """CDN endpoint configuration."""    provider: CDNProvider
    endpoint_url: str
    distribution_id: str
    cache_policies: Dict[str, Any]
    compression_enabled: bool
    brotli_enabled: bool
    gzip_enabled: bool
    security_headers: Dict[str, str]
    custom_headers: Dict[str, str]
    ssl_certificate: str
    http2_enabled: bool
    http3_enabled: bool
    edge_locations: List[str]
    bandwidth_limit: Optional[str] = None
    rate_limit: Optional[int] = None


@dataclass
class StreamingConfig:
    """Streaming configuration for audio/video content."""    adaptive_bitrate: bool
    protocols: List[str]  # HLS, DASH, WebRTC
    quality_levels: List[Dict[str, Any]]
    buffer_size: int
    segment_duration: int
    live_streaming: bool
    recording_enabled: bool
    transcoding_presets: List[Dict[str, Any]]
    drm_protection: bool
    watermarking: bool


class ContentDeliveryAPIsConfig:
    """Professional content delivery APIs configuration."""    
    def __init__(self):
        """Initialize content delivery configuration."""        self.environments = {
            'development': self._get_development_config(),
            'staging': self._get_staging_config(),
            'production': self._get_production_config()
        }
        
        self.cdn_configs = self._get_cdn_configurations()
        self.streaming_configs = self._get_streaming_configurations()
        self.caching_strategies = self._get_caching_strategies()
        self.optimization_settings = self._get_optimization_settings()
    
    def _get_development_config(self) -> Dict[str, Any]:
        """Development environment CDN configuration."""        return {
            'primary_cdn': CDNProvider.CLOUDFLARE,
            'fallback_cdn': CDNProvider.AWS_CLOUDFRONT,
            'cache_ttl': 300,  # 5 minutes
            'purge_on_update': True,
            'debug_headers': True,
            'performance_monitoring': True,
            'cost_optimization': False
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """Staging environment CDN configuration."""        return {
            'primary_cdn': CDNProvider.AWS_CLOUDFRONT,
            'fallback_cdn': CDNProvider.AZURE_CDN,
            'cache_ttl': 3600,  # 1 hour
            'purge_on_update': True,
            'debug_headers': False,
            'performance_monitoring': True,
            'cost_optimization': True
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Production environment CDN configuration."""        return {
            'primary_cdn': CDNProvider.CLOUDFLARE,
            'fallback_cdn': CDNProvider.FASTLY,
            'backup_cdn': CDNProvider.AWS_CLOUDFRONT,
            'cache_ttl': 86400,  # 24 hours
            'purge_on_update': False,
            'debug_headers': False,
            'performance_monitoring': True,
            'cost_optimization': True,
            'geo_restrictions': True,
            'ddos_protection': True
        }
    
    def _get_cdn_configurations(self) -> Dict[CDNProvider, CDNEndpointConfig]:
        """Get CDN provider configurations."""        return {
            CDNProvider.CLOUDFLARE: CDNEndpointConfig(
                provider=CDNProvider.CLOUDFLARE,
                endpoint_url=os.getenv("CLOUDFLARE_CDN_URL", ""),
                distribution_id=os.getenv("CLOUDFLARE_ZONE_ID", ""),
                cache_policies={
                    'audio': {'ttl': 86400, 'browser_ttl': 3600},
                    'video': {'ttl': 604800, 'browser_ttl': 7200},
                    'image': {'ttl': 2592000, 'browser_ttl': 86400},
                    'api': {'ttl': 300, 'browser_ttl': 0}
                },
                compression_enabled=True,
                brotli_enabled=True,
                gzip_enabled=True,
                security_headers={
                    'X-Frame-Options': 'DENY',
                    'X-Content-Type-Options': 'nosniff',
                    'Referrer-Policy': 'strict-origin-when-cross-origin',
                    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
                },
                custom_headers={
                    'X-IA-Platform': 'IA-Influencer-Agent',
                    'X-Content-Protection': 'Active'
                },
                ssl_certificate="cloudflare_universal",
                http2_enabled=True,
                http3_enabled=True,
                edge_locations=['global'],
                bandwidth_limit="unlimited",
                rate_limit=10000
            ),
            
            CDNProvider.AWS_CLOUDFRONT: CDNEndpointConfig(
                provider=CDNProvider.AWS_CLOUDFRONT,
                endpoint_url=os.getenv("AWS_CLOUDFRONT_URL", ""),
                distribution_id=os.getenv("AWS_CLOUDFRONT_DISTRIBUTION_ID", ""),
                cache_policies={
                    'audio': {'ttl': 86400, 'browser_ttl': 3600},
                    'video': {'ttl': 604800, 'browser_ttl': 7200},
                    'image': {'ttl': 2592000, 'browser_ttl': 86400},
                    'stream': {'ttl': 0, 'browser_ttl': 0}
                },
                compression_enabled=True,
                brotli_enabled=True,
                gzip_enabled=True,
                security_headers={
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                    'X-Frame-Options': 'SAMEORIGIN',
                    'X-XSS-Protection': '1; mode=block'
                },
                custom_headers={
                    'X-AWS-Request-ID': '${request_id}',
                    'X-Cache-Status': '${cache_status}'
                },
                ssl_certificate="aws_acm",
                http2_enabled=True,
                http3_enabled=False,
                edge_locations=['us-east-1', 'eu-west-1', 'ap-southeast-1'],
                bandwidth_limit="1TB",
                rate_limit=5000
            )
        }
    
    def _get_streaming_configurations(self) -> Dict[str, StreamingConfig]:
        """Get streaming configurations for different content types."""        return {
            'audio_stream': StreamingConfig(
                adaptive_bitrate=True,
                protocols=['HLS', 'DASH'],
                quality_levels=[
                    {'bitrate': 128, 'sample_rate': 44100, 'format': 'aac'},
                    {'bitrate': 256, 'sample_rate': 48000, 'format': 'aac'},
                    {'bitrate': 320, 'sample_rate': 48000, 'format': 'aac'}
                ],
                buffer_size=4096,
                segment_duration=6,
                live_streaming=True,
                recording_enabled=True,
                transcoding_presets=[
                    {'codec': 'aac', 'bitrate': 128, 'channels': 2},
                    {'codec': 'aac', 'bitrate': 256, 'channels': 2},
                    {'codec': 'aac', 'bitrate': 320, 'channels': 2}
                ],
                drm_protection=True,
                watermarking=True
            ),
            
            'video_stream': StreamingConfig(
                adaptive_bitrate=True,
                protocols=['HLS', 'DASH', 'WebRTC'],
                quality_levels=[
                    {'resolution': '480p', 'bitrate': 1000, 'fps': 30},
                    {'resolution': '720p', 'bitrate': 2500, 'fps': 30},
                    {'resolution': '1080p', 'bitrate': 5000, 'fps': 60},
                    {'resolution': '4K', 'bitrate': 15000, 'fps': 60}
                ],
                buffer_size=8192,
                segment_duration=4,
                live_streaming=True,
                recording_enabled=True,
                transcoding_presets=[
                    {'codec': 'h264', 'profile': 'baseline', 'level': '3.1'},
                    {'codec': 'h264', 'profile': 'main', 'level': '4.0'},
                    {'codec': 'h265', 'profile': 'main', 'level': '5.0'}
                ],
                drm_protection=True,
                watermarking=True
            )
        }
    
    def _get_caching_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get caching strategies for different content types."""        return {
            'static_assets': {
                'strategy': 'aggressive',
                'ttl': 2592000,  # 30 days
                'browser_cache': 86400,  # 1 day
                'vary_headers': ['Accept-Encoding'],
                'cache_control': 'public, max-age=86400, immutable'
            },
            
            'dynamic_content': {
                'strategy': 'conservative',
                'ttl': 300,  # 5 minutes
                'browser_cache': 0,
                'vary_headers': ['Accept', 'Authorization'],
                'cache_control': 'private, no-cache, must-revalidate'
            },
            
            'api_responses': {
                'strategy': 'selective',
                'ttl': 60,  # 1 minute
                'browser_cache': 0,
                'vary_headers': ['Accept', 'Authorization', 'Content-Type'],
                'cache_control': 'private, max-age=60'
            },
            
            'media_content': {
                'strategy': 'long_term',
                'ttl': 604800,  # 7 days
                'browser_cache': 3600,  # 1 hour
                'vary_headers': ['Accept-Encoding', 'Range'],
                'cache_control': 'public, max-age=3600'
            }
        }
    
    def _get_optimization_settings(self) -> Dict[str, Any]:
        """Get CDN optimization settings."""        return {
            'image_optimization': {
                'webp_conversion': True,
                'avif_conversion': True,
                'progressive_jpeg': True,
                'quality_compression': 85,
                'responsive_images': True,
                'lazy_loading': True
            },
            
            'video_optimization': {
                'adaptive_streaming': True,
                'thumbnail_generation': True,
                'preview_generation': True,
                'codec_optimization': True,
                'resolution_optimization': True
            },
            
            'audio_optimization': {
                'codec_conversion': True,
                'bitrate_optimization': True,
                'normalization': True,
                'silence_detection': True,
                'fade_in_out': True
            },
            
            'compression': {
                'gzip_level': 6,
                'brotli_level': 6,
                'minification': True,
                'tree_shaking': True,
                'code_splitting': True
            }
        }
    
    def get_cdn_config(self, provider: CDNProvider) -> Optional[CDNEndpointConfig]:
        """Get CDN configuration for specific provider."""        return self.cdn_configs.get(provider)
    
    def get_streaming_config(self, content_type: str) -> Optional[StreamingConfig]:
        """Get streaming configuration for content type."""        return self.streaming_configs.get(content_type)
    
    def get_cache_strategy(self, content_category: str) -> Optional[Dict[str, Any]]:
        """Get caching strategy for content category."""        return self.caching_strategies.get(content_category)


# Global configuration instance
content_delivery_apis_config = ContentDeliveryAPIsConfig()


def get_content_delivery_config(environment: str = 'production') -> Dict[str, Any]:
    """Get content delivery configuration for environment."""    return content_delivery_apis_config.environments.get(environment, {})


def get_cdn_endpoint(provider: CDNProvider) -> Optional[CDNEndpointConfig]:
    """Get CDN endpoint configuration."""    return content_delivery_apis_config.get_cdn_config(provider)


def get_streaming_settings(content_type: str) -> Optional[StreamingConfig]:
    """Get streaming settings for content type."""    return content_delivery_apis_config.get_streaming_config(content_type)
