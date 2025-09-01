"""Crawler Utilities Module
========================

Professional utility functions and classes for web crawlers.
Implements advanced rate limiting, proxy management, and user agent rotation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

from .rate_limiter import (
    RateLimiter,
    YouTubeRateLimiter,
    InstagramRateLimiter,
    TikTokRateLimiter,
    TwitterRateLimiter,
    FacebookRateLimiter,
    SpotifyRateLimiter,
    SubstackRateLimiter,
    GenericRateLimiter,
    AdaptiveRateLimiter
)
from .proxy_manager import ProxyManager
from .user_agent_rotator import UserAgentRotator
from .content_extractor import (
    ContentExtractor,
    ExtractedContent,
    SocialMediaContent,
    extract_content_from_url,
    clean_extracted_text,
    extract_domain_info
)
from .url_validator import (
    URLValidator,
    URLValidationResult,
    URLType,
    URLNormalizer,
    quick_validate_url,
    extract_domain,
    is_same_domain,
    clean_url_parameters
)
from .session_manager import SessionManager
from .cookie_manager import (
    CookieManager,
    CookieJar,
    CookieData,
    CookiePolicy,
    parse_cookie_string,
    format_cookie_header,
    is_secure_cookie,
    get_cookie_domain_level,
    extract_domain_from_url
)
from .captcha_solver import (
    CaptchaSolver,
    CaptchaChallenge,
    CaptchaSolution,
    CaptchaType,
    CaptchaDetector,
    ImageCaptchaSolver,
    ExternalCaptchaSolver,
    create_image_captcha_solver,
    create_2captcha_solver,
    create_anticaptcha_solver,
    setup_default_captcha_solver
)
from .fingerprint_utils import (
    ContentFingerprint,
    SimilarityResult,
    ContentFingerprintGenerator,
    SimilarityAnalyzer,
    create_fingerprint_generator,
    create_similarity_analyzer,
    generate_content_fingerprint,
    calculate_content_similarity
)
from .surveillance_utils import (
    SurveillanceStatus,
    ThreatLevel,
    AlertType,
    MonitoringFrequency,
    SurveillanceTarget,
    SurveillanceAlert,
    ThreatAssessment,
    MonitoringMetrics,
    SurveillanceEngine,
    AlertNotificationManager,
    create_surveillance_engine,
    create_surveillance_target,
    create_alert_notification_manager
)
from .security_utils import (
    SecurityLevel,
    ThreatType,
    EncryptionMethod,
    SecurityAssessment,
    EncryptedData,
    SecurityScanner,
    ContentEncryption,
    AccessControl,
    create_security_scanner,
    create_content_encryption,
    create_access_control,
    quick_security_scan,
    quick_encrypt_content
)
from .performance_utils import (
    CacheStrategy,
    MetricType,
    PerformanceMetric,
    CacheEntry,
    PerformanceReport,
    AdvancedCache,
    PerformanceMonitor,
    ConnectionPool,
    ResourceOptimizer,
    create_advanced_cache,
    create_performance_monitor,
    create_connection_pool,
    create_resource_optimizer,
    monitor_performance
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Rate Limiting
    "RateLimiter",
    "YouTubeRateLimiter",
    "InstagramRateLimiter", 
    "TikTokRateLimiter",
    "TwitterRateLimiter",
    "FacebookRateLimiter",
    "SpotifyRateLimiter",
    "SubstackRateLimiter",
    "GenericRateLimiter",
    "AdaptiveRateLimiter",
    
    # Proxy and User Agent Management
    "ProxyManager",
    "UserAgentRotator",
    
    # Content Extraction
    "ContentExtractor",
    "ExtractedContent",
    "SocialMediaContent",
    "extract_content_from_url",
    "clean_extracted_text",
    "extract_domain_info",
    
    # URL Validation
    "URLValidator",
    "URLValidationResult",
    "URLType",
    "URLNormalizer",
    "quick_validate_url",
    "extract_domain",
    "is_same_domain",
    "clean_url_parameters",
    
    # Session Management
    "SessionManager",
    
    # Cookie Management
    "CookieManager",
    "CookieJar",
    "CookieData",
    "CookiePolicy",
    "parse_cookie_string",
    "format_cookie_header",
    "is_secure_cookie",
    "get_cookie_domain_level",
    "extract_domain_from_url",
    
    # CAPTCHA Solving
    "CaptchaSolver",
    "CaptchaChallenge",
    "CaptchaSolution",
    "CaptchaType",
    "CaptchaDetector",
    "ImageCaptchaSolver",
    "ExternalCaptchaSolver",
    "create_image_captcha_solver",
    "create_2captcha_solver",
    "create_anticaptcha_solver",
    "setup_default_captcha_solver",
    
    # Content Fingerprinting
    "ContentFingerprint",
    "SimilarityResult",
    "ContentFingerprintGenerator",
    "SimilarityAnalyzer",
    "create_fingerprint_generator",
    "create_similarity_analyzer",
    "generate_content_fingerprint",
    "calculate_content_similarity",
    
    # Surveillance and Monitoring
    "SurveillanceStatus",
    "ThreatLevel",
    "AlertType",
    "MonitoringFrequency",
    "SurveillanceTarget",
    "SurveillanceAlert",
    "ThreatAssessment",
    "MonitoringMetrics",
    "SurveillanceEngine",
    "AlertNotificationManager",
    "create_surveillance_engine",
    "create_surveillance_target",
    "create_alert_notification_manager",
    
    # Security and Encryption
    "SecurityLevel",
    "ThreatType",
    "EncryptionMethod",
    "SecurityAssessment",
    "EncryptedData",
    "SecurityScanner",
    "ContentEncryption",
    "AccessControl",
    "create_security_scanner",
    "create_content_encryption",
    "create_access_control",
    "quick_security_scan",
    "quick_encrypt_content",
    
    # Performance Optimization
    "CacheStrategy",
    "MetricType",
    "PerformanceMetric",
    "CacheEntry",
    "PerformanceReport",
    "AdvancedCache",
    "PerformanceMonitor",
    "ConnectionPool",
    "ResourceOptimizer",
    "create_advanced_cache",
    "create_performance_monitor",
    "create_connection_pool",
    "create_resource_optimizer",
    "monitor_performance",
]

# Utility constants
DEFAULT_REQUEST_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BACKOFF_FACTOR = 1.5
MAX_CONCURRENT_REQUESTS = 10

# User agent collections
BROWSER_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
]

# Platform-specific configurations
PLATFORM_CONFIGS = {
    "youtube": {
        "base_delay": 1.0,
        "max_requests_per_minute": 100,
        "burst_limit": 10,
        "retry_after_rate_limit": 60
    },
    "instagram": {
        "base_delay": 2.0,
        "max_requests_per_minute": 60,
        "burst_limit": 5,
        "retry_after_rate_limit": 300
    },
    "tiktok": {
        "base_delay": 3.0,
        "max_requests_per_minute": 30,
        "burst_limit": 3,
        "retry_after_rate_limit": 600
    },
    "twitter": {
        "base_delay": 1.5,
        "max_requests_per_minute": 180,
        "burst_limit": 15,
        "retry_after_rate_limit": 900
    },
    "facebook": {
        "base_delay": 2.5,
        "max_requests_per_minute": 200,
        "burst_limit": 20,
        "retry_after_rate_limit": 300
    },
    "spotify": {
        "base_delay": 0.5,
        "max_requests_per_minute": 100,
        "burst_limit": 10,
        "retry_after_rate_limit": 60
    }
}

def get_platform_config(platform: str) -> dict:
    """Get configuration for specific platform."""
    return PLATFORM_CONFIGS.get(platform, {
        "base_delay": 1.0,
        "max_requests_per_minute": 60,
        "burst_limit": 5,
        "retry_after_rate_limit": 300
    })

def create_rate_limiter(platform: str):
    """Factory function to create appropriate rate limiter."""
    rate_limiter_map = {
        "youtube": YouTubeRateLimiter,
        "instagram": InstagramRateLimiter,
        "tiktok": TikTokRateLimiter,
        "twitter": TwitterRateLimiter,
        "facebook": FacebookRateLimiter,
        "spotify": SpotifyRateLimiter,
        "substack": SubstackRateLimiter,
        "adaptive": AdaptiveRateLimiter,
        "generic": GenericRateLimiter
    }
    
    limiter_class = rate_limiter_map.get(platform.lower(), GenericRateLimiter)
    return limiter_class()

def validate_crawler_config(config: dict) -> bool:
    """Validate crawler configuration."""
    required_fields = ['platform', 'max_results', 'check_interval']
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate ranges
    if config.get('max_results', 0) <= 0:
        return False
    
    if config.get('check_interval', 0) < 60:  # Minimum 1 minute
        return False
    
    return True

async def test_platform_connectivity(platform: str) -> bool:
    """
Test connectivity to specific platform."""
    test_urls = {
        "youtube": "https://www.youtube.com",
        "instagram": "https://www.instagram.com",
        "tiktok": "https://www.tiktok.com",
        "twitter": "https://twitter.com",
        "facebook": "https://www.facebook.com",
        "spotify": "https://open.spotify.com"
    }
    
    url = test_urls.get(platform)
    if not url:
        return False
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=10) as response:
                return response.status == 200
    except:
        return False
