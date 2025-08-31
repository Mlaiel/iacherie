"""Crawler Utils Index
===================

Central index and factory module for crawler utilities.
Provides convenient access to all crawler utility components.

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
import asyncio
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import redis

from . import (
    # Rate Limiting
    create_rate_limiter,
    RateLimiter,
    YouTubeRateLimiter,
    InstagramRateLimiter,
    TikTokRateLimiter,
    TwitterRateLimiter,
    FacebookRateLimiter,
    SpotifyRateLimiter,
    SubstackRateLimiter,
    AdaptiveRateLimiter,
    
    # Proxy Management
    ProxyManager,
    
    # User Agent Management
    UserAgentRotator,
    
    # Content Extraction
    ContentExtractor,
    extract_content_from_url,
    
    # URL Validation
    URLValidator,
    quick_validate_url,
    
    # Session Management
    SessionManager,
    
    # Cookie Management
    CookieManager,
    
    # CAPTCHA Solving
    setup_default_captcha_solver,
    CaptchaSolver,
)

logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """Configuration for crawler utilities."""
    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_strategy: str = "platform_specific"  # platform_specific, adaptive, conservative
    
    # Proxy settings
    enable_proxy_rotation: bool = False
    proxy_rotation_interval: int = 100  # requests
    proxy_validation_interval: int = 300  # seconds
    
    # User agent settings
    enable_user_agent_rotation: bool = True
    user_agent_strategy: str = "weighted_random"
    mobile_traffic_ratio: float = 0.3
    
    # Session settings
    enable_session_persistence: bool = True
    max_sessions: int = 50
    session_timeout: int = 3600  # seconds
    max_requests_per_session: int = 1000
    
    # Content extraction
    enable_content_analysis: bool = True
    extract_multimedia: bool = True
    extract_structured_data: bool = True
    
    # Security settings
    enable_url_validation: bool = True
    security_threshold: float = 0.5
    
    # CAPTCHA solving
    enable_captcha_solving: bool = False
    captcha_api_keys: Dict[str, str] = None
    
    # Storage
    redis_url: Optional[str] = None
    enable_persistence: bool = True
    data_directory: str = "./data/crawler"
    
    def __post_init__(self):
        if self.captcha_api_keys is None:
            self.captcha_api_keys = {}

class CrawlerUtilsManager:
    """
    Central manager for all crawler utilities.
    
    Provides a unified interface to access and configure all crawler utilities
    with intelligent defaults and automatic setup.
    """
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """Initialize crawler utilities manager."""
        self.config = config or CrawlerConfig()
        
        # Initialize components
        self.redis_client = None
        self.proxy_manager = None
        self.user_agent_rotator = None
        self.content_extractor = None
        self.url_validator = None
        self.session_manager = None
        self.cookie_manager = None
        self.captcha_solver = None
        self.rate_limiters = {}
        
        # Setup components
        self._setup_redis()
        self._setup_proxy_manager()
        self._setup_user_agent_rotator()
        self._setup_content_extractor()
        self._setup_url_validator()
        self._setup_cookie_manager()
        self._setup_captcha_solver()
        self._setup_session_manager()
        self._setup_rate_limiters()
        
        logger.info("Crawler utilities manager initialized")
    
    def _setup_redis(self) -> None:
        """Setup Redis connection."""
        if self.config.redis_url:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
                self.redis_client.ping()  # Test connection
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
    
    def _setup_proxy_manager(self) -> None:
        """Setup proxy manager."""
        if self.config.enable_proxy_rotation:
            self.proxy_manager = ProxyManager()
            logger.info("Proxy manager initialized")
    
    def _setup_user_agent_rotator(self) -> None:
        """Setup user agent rotator."""
        if self.config.enable_user_agent_rotation:
            self.user_agent_rotator = UserAgentRotator()
            self.user_agent_rotator.set_rotation_strategy(self.config.user_agent_strategy)
            self.user_agent_rotator.set_mobile_ratio(self.config.mobile_traffic_ratio)
            logger.info("User agent rotator initialized")
    
    def _setup_content_extractor(self) -> None:
        """Setup content extractor."""
        self.content_extractor = ContentExtractor()
        logger.info("Content extractor initialized")
    
    def _setup_url_validator(self) -> None:
        """Setup URL validator."""
        if self.config.enable_url_validation:
            self.url_validator = URLValidator()
            logger.info("URL validator initialized")
    
    def _setup_cookie_manager(self) -> None:
        """Setup cookie manager."""
        self.cookie_manager = CookieManager(
            redis_client=self.redis_client,
            enable_encryption=True
        )
        logger.info("Cookie manager initialized")
    
    def _setup_captcha_solver(self) -> None:
        """Setup CAPTCHA solver."""
        if self.config.enable_captcha_solving and self.config.captcha_api_keys:
            self.captcha_solver = setup_default_captcha_solver(
                self.config.captcha_api_keys
            )
            logger.info("CAPTCHA solver initialized")
    
    def _setup_session_manager(self) -> None:
        """Setup session manager."""
        self.session_manager = SessionManager(
            proxy_manager=self.proxy_manager,
            user_agent_rotator=self.user_agent_rotator
        )
        self.session_manager.max_sessions = self.config.max_sessions
        self.session_manager.session_timeout = self.config.session_timeout
        self.session_manager.max_requests_per_session = self.config.max_requests_per_session
        self.session_manager.persist_sessions = self.config.enable_session_persistence
        logger.info("Session manager initialized")
    
    def _setup_rate_limiters(self) -> None:
        """Setup rate limiters for different platforms."""
        if not self.config.enable_rate_limiting:
            return
        
        platforms = [
            'youtube', 'instagram', 'tiktok', 'twitter', 
            'facebook', 'spotify', 'substack', 'generic'
        ]
        
        for platform in platforms:
            if self.config.rate_limit_strategy == "adaptive":
                limiter = AdaptiveRateLimiter(redis_client=self.redis_client)
            else:
                limiter = create_rate_limiter(platform)
                if hasattr(limiter, 'redis_client'):
                    limiter.redis_client = self.redis_client
            
            self.rate_limiters[platform] = limiter
        
        logger.info(f"Rate limiters initialized for {len(platforms)} platforms")
    
    def get_rate_limiter(self, platform: str) -> Optional[RateLimiter]:
        """Get rate limiter for specific platform."""
        return self.rate_limiters.get(platform.lower(), self.rate_limiters.get('generic'))
    
    async def create_crawler_session(
        self, 
        platform: str,
        domain: Optional[str] = None,
        mobile: Optional[bool] = None,
        country: Optional[str] = None
    ) -> str:
        """Create a new crawler session with all utilities configured."""
        session_id = await self.session_manager.create_session(
            platform=platform,
            domain=domain,
            mobile=mobile,
            country=country
        )
        
        logger.info(f"Created crawler session {session_id} for platform: {platform}")
        return session_id
    
    async def crawl_url(
        self,
        url: str,
        session_id: Optional[str] = None,
        validate_url: bool = True,
        extract_content: bool = True,
        solve_captcha: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive URL crawling with all utilities.
        
        Args:
            url: URL to crawl
            session_id: Optional session ID to use
            validate_url: Whether to validate URL first
            extract_content: Whether to extract content
            solve_captcha: Whether to solve CAPTCHAs
            
        Returns:
            Dictionary with crawling results
        """
        result = {
            'url': url,
            'success': False,
            'validation': None,
            'content': None,
            'captcha_solutions': [],
            'session_id': session_id,
            'errors': []
        }
        
        try:
            # Step 1: URL Validation
            if validate_url and self.url_validator:
                validation_result = await self.url_validator.validate_url(url)
                result['validation'] = validation_result
                
                if not validation_result.is_valid:
                    result['errors'].append("URL validation failed")
                    return result
                
                if validation_result.security_score < self.config.security_threshold:
                    result['errors'].append("URL failed security check")
                    return result
            
            # Step 2: Create session if needed
            if not session_id:
                platform = validation_result.platform if validate_url else 'generic'
                session_id = await self.create_crawler_session(platform)
                result['session_id'] = session_id
            
            # Step 3: Make request
            session = await self.session_manager.get_session(session_id)
            if not session:
                result['errors'].append("Failed to get session")
                return result
            
            # Apply rate limiting
            if self.config.enable_rate_limiting:
                platform = validation_result.platform if validate_url else 'generic'
                rate_limiter = self.get_rate_limiter(platform)
                if rate_limiter:
                    await rate_limiter.wait_if_needed(session_id)
            
            # Make the request
            response = await self.session_manager.make_request(
                session_id, 'GET', url
            )
            
            if not response:
                result['errors'].append("Request failed")
                return result
            
            html_content = await response.text()
            
            # Step 4: CAPTCHA Detection and Solving
            if solve_captcha and self.captcha_solver:
                captcha_solutions = await self.captcha_solver.detect_and_solve(
                    html_content, url
                )
                result['captcha_solutions'] = [
                    {
                        'success': sol.success,
                        'solution': sol.solution,
                        'solver_used': sol.solver_used,
                        'solving_time': sol.solving_time
                    }
                    for sol in captcha_solutions
                ]
            
            # Step 5: Content Extraction
            if extract_content and self.content_extractor:
                content = await self.content_extractor.extract_content(
                    html_content, url
                )
                
                # Convert to dictionary for serialization
                result['content'] = {
                    'title': content.title,
                    'description': content.description,
                    'clean_text': content.clean_text,
                    'word_count': content.word_count,
                    'reading_time_minutes': content.reading_time_minutes,
                    'readability_score': content.readability_score,
                    'sentiment_score': content.sentiment_score,
                    'content_quality_score': content.content_quality_score,
                    'language': content.language,
                    'keywords': content.keywords,
                    'author': content.author,
                    'publish_date': content.publish_date.isoformat() if content.publish_date else None,
                    'links_count': len(content.links),
                    'images_count': len(content.images),
                    'videos_count': len(content.videos),
                    'social_media_links_count': len(content.social_media_links),
                    'content_type': content.content_type,
                    'extracted_entities': content.extracted_entities,
                    'topic_categories': content.topic_categories,
                    'fingerprint_hash': content.fingerprint_hash
                }
            
            # Update rate limiter
            if self.config.enable_rate_limiting:
                platform = validation_result.platform if validate_url else 'generic'
                rate_limiter = self.get_rate_limiter(platform)
                if rate_limiter:
                    await rate_limiter.update_usage(session_id)
            
            result['success'] = True
            logger.info(f"Successfully crawled {url}")
            
        except Exception as e:
            result['errors'].append(str(e))
            logger.error(f"Crawling failed for {url}: {e}")
        
        return result
    
    async def batch_crawl_urls(
        self,
        urls: List[str],
        max_concurrent: int = 5,
        **crawl_kwargs
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs concurrently.
        
        Args:
            urls: List of URLs to crawl
            max_concurrent: Maximum concurrent requests
            **crawl_kwargs: Additional arguments for crawl_url
            
        Returns:
            List of crawling results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.crawl_url(url, **crawl_kwargs)
        
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    'url': urls[i],
                    'success': False,
                    'errors': [str(result)]
                })
            else:
                final_results.append(result)
        
        logger.info(f"Batch crawled {len(urls)} URLs with {max_concurrent} concurrent requests")
        return final_results
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all utilities."""
        stats = {
            'config': {
                'rate_limiting_enabled': self.config.enable_rate_limiting,
                'proxy_rotation_enabled': self.config.enable_proxy_rotation,
                'user_agent_rotation_enabled': self.config.enable_user_agent_rotation,
                'session_persistence_enabled': self.config.enable_session_persistence,
                'captcha_solving_enabled': self.config.enable_captcha_solving,
            }
        }
        
        # Rate limiter stats
        if self.rate_limiters:
            rate_limiter_stats = {}
            for platform, limiter in self.rate_limiters.items():
                rate_limiter_stats[platform] = limiter.get_rate_limit_info()
            stats['rate_limiters'] = rate_limiter_stats
        
        # Proxy manager stats
        if self.proxy_manager:
            stats['proxy_manager'] = self.proxy_manager.get_proxy_statistics()
        
        # User agent rotator stats
        if self.user_agent_rotator:
            stats['user_agent_rotator'] = self.user_agent_rotator.get_usage_statistics()
        
        # Session manager stats
        if self.session_manager:
            stats['session_manager'] = await self.session_manager.get_session_statistics()
        
        # Cookie manager stats
        if self.cookie_manager:
            stats['cookie_manager'] = await self.cookie_manager.get_cookie_statistics()
        
        # CAPTCHA solver stats
        if self.captcha_solver:
            stats['captcha_solver'] = self.captcha_solver.get_solver_statistics()
        
        return stats
    
    async def cleanup(self) -> None:
        """Cleanup all resources."""
        if self.session_manager:
            await self.session_manager.close_all_sessions()
        
        if self.cookie_manager:
            await self.cookie_manager.save_cookies()
        
        logger.info("Crawler utilities manager cleaned up")

# Factory functions for easy setup
def create_crawler_manager(config: Optional[CrawlerConfig] = None) -> CrawlerUtilsManager:
    """Create crawler utilities manager with configuration."""
    return CrawlerUtilsManager(config)

def create_basic_crawler_config(
    enable_proxy: bool = False,
    enable_captcha: bool = False,
    redis_url: Optional[str] = None
) -> CrawlerConfig:
    """Create basic crawler configuration."""
    return CrawlerConfig(
        enable_proxy_rotation=enable_proxy,
        enable_captcha_solving=enable_captcha,
        redis_url=redis_url
    )

def create_advanced_crawler_config(
    redis_url: str,
    proxy_enabled: bool = True,
    captcha_api_keys: Optional[Dict[str, str]] = None
) -> CrawlerConfig:
    """Create advanced crawler configuration."""
    return CrawlerConfig(
        enable_rate_limiting=True,
        rate_limit_strategy="adaptive",
        enable_proxy_rotation=proxy_enabled,
        enable_user_agent_rotation=True,
        user_agent_strategy="performance_based",
        enable_session_persistence=True,
        enable_content_analysis=True,
        extract_multimedia=True,
        extract_structured_data=True,
        enable_url_validation=True,
        security_threshold=0.7,
        enable_captcha_solving=bool(captcha_api_keys),
        captcha_api_keys=captcha_api_keys or {},
        redis_url=redis_url,
        enable_persistence=True
    )

# Quick access functions
async def quick_crawl(url: str, **kwargs) -> Dict[str, Any]:
    """Quick crawl a single URL with default settings."""
    manager = create_crawler_manager()
    try:
        result = await manager.crawl_url(url, **kwargs)
        return result
    finally:
        await manager.cleanup()

async def quick_extract_content(url: str) -> Optional[Dict[str, Any]]:
    """Quick content extraction from URL."""
    result = await quick_crawl(url, extract_content=True)
    return result.get('content') if result.get('success') else None

# Export main components
__all__ = [
    'CrawlerConfig',
    'CrawlerUtilsManager',
    'create_crawler_manager',
    'create_basic_crawler_config',
    'create_advanced_crawler_config',
    'quick_crawl',
    'quick_extract_content',
]
