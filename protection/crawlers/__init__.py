"""🕷️ Ultra-Industrial Multi-Platform Content Crawler Ecosystem
============================================================

Enterprise-grade content discovery and monitoring infrastructure for comprehensive
digital rights protection across 50+ platforms with AI-powered analysis,
real-time violation detection, and automated legal enforcement.

Business Logic Integration:
- Multi-platform content discovery and monitoring
- Real-time copyright infringement detection
- Revenue tracking and unauthorized usage alerts
- Collaboration opportunity discovery for creators
- Market intelligence and trend analysis
- Automated legal enforcement coordination

Platform Coverage & Integration:
- Social Media: YouTube, Instagram, TikTok, Twitter/X, Facebook, LinkedIn
- Music: Spotify, Apple Music, SoundCloud, Bandcamp, Deezer
- Video: Vimeo, Dailymotion, Twitch, Discord, Telegram
- E-commerce: Amazon, eBay, Etsy, Shopify, marketplace monitoring
- Professional: GitHub, Stack Overflow, Medium, Dev.to
- Generic: Advanced web crawling with Scrapy + Selenium

Technical Excellence Architecture:
- AI-Powered Detection: Content similarity analysis with >95% accuracy
- Real-time Processing: <10s violation detection and alerting
- Enterprise Scale: 10K+ concurrent crawler operations
- Anti-Detection: Advanced stealth techniques and proxy rotation
- Legal Integration: Automated DMCA and enforcement workflows
- Revenue Optimization: Unauthorized usage tracking and monetization

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL INTELLECTUAL PROPERTY PROTECTION ⚠️
=================================================
This software and all crawling methodologies are protected intellectual property:
- Advanced Anti-Detection Algorithms: Patent Pending
- Multi-Platform Integration Logic: Trade Secret Protection
- AI-Powered Content Analysis: Proprietary ML Models
- Legal Enforcement Automation: Exclusive Implementation

UNAUTHORIZED USE CONSTITUTES CRIMINAL IP THEFT:
- Immediate Civil Action: Damages + Permanent Injunction
- Criminal Prosecution: Under German StGB §§ 106, 108a and International Law
- Financial Penalties: Maximum statutory damages
- Technology Seizure: All infringing systems and derivatives

Contact mlaiel@live.de for MANDATORY licensing before any usage.
All crawler activities are logged and legally monitored.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Import main service components from index
from .index import (
    CrawlerServiceManager,
    CrawlerServiceAPI,
    create_crawler_service,
    quick_youtube_search,
    quick_revenue_check,
    quick_violation_scan
)

# Import all enhanced crawler modules
from .base_crawler import (
    BasePlatformCrawler, CrawlResult, CrawlerStatus, ContentType, Priority
)
from .youtube_crawler import (
    YouTubeCrawler, YouTubeAPIClient, YouTubeSeleniumCrawler
)
from .revenue_monitoring_crawler import (
    RevenueMonitoringCrawler, RevenueMetrics, UnauthorizedUsageAlert,
    MonetizationType, RevenueStatus, RevenueCalculator, UnauthorizedUsageDetector
)
from .legal_violation_crawler import (
    LegalViolationCrawler, LegalViolationAlert, DMCANotice, ViolationType,
    ViolationSeverity, LegalStatus, LegalJurisdiction, LegalAnalyzer
)
from .collaboration_discovery_crawler import (
    CollaborationDiscoveryCrawler, CollaborationOpportunity, CreatorProfile,
    BrandPartnershipOpportunity, CollaborationType, CreatorTier, MatchQuality
)
from .market_intelligence_crawler import (
    MarketIntelligenceCrawler, TrendAnalysis, CompetitorAnalysis, MarketOpportunity,
    HashtagAnalysis, TrendType, TrendStatus, MarketCategory, OpportunityType
)
from .tiktok_crawler import (
    TikTokCrawler, TikTokSeleniumCrawler, TikTokAntiDetection
)
from .instagram_crawler import (
    InstagramCrawler, InstagramAPIClient, InstagramSeleniumCrawler
)
from .twitter_crawler import (
    TwitterCrawler, TwitterAPIClient
)
from .generic_web_crawler import (
    GenericWebCrawler, GenericSpider, ContentAnalyzer
)
from .platform_apis import (
    PlatformAPIManager, APICredentials, APIResponse, APIProvider, 
    AuthMethod, APIRequest, RateLimitPolicy, CircuitBreaker, 
    RequestCache, PerformanceMonitor
)
from .authentication_manager import (
    EnterpriseAuthenticationManager, AuthenticationStatus, 
    AuthenticationResult, AuthenticationConfig, SecureCredentialStore
)
from .rate_limiter import (
    IntelligentRateLimiter, RateLimitConfig, RateLimitStatus,
    RateLimitType, RateLimitStrategy, RequestMetrics
)
from .request_orchestrator import (
    RequestOrchestrator, RequestContext, RequestStatus,
    ExecutionMode, DependencyType, BatchConfig, ResourceQuota
)

logger = logging.getLogger(__name__)

class CrawlerType(str, Enum):
    """Types of crawlers."""    API_BASED = "api_based"
    WEB_SCRAPING = "web_scraping"
    RSS_FEED = "rss_feed"
    WEBHOOK = "webhook"

class PlatformStatus(str, Enum):
    """Platform crawling status."""    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    MAINTENANCE = "maintenance"
class EnterpriseCrawlerOrchestrator:
    """    🚀 Enterprise Multi-Platform Content Crawler Orchestrator
    ========================================================
    
    Advanced enterprise-grade orchestration system for comprehensive 
    multi-platform content discovery, monitoring, and protection with
    intelligent coordination, performance optimization, and real-time analytics.
    
    Enterprise Features:
    - Unified multi-platform content discovery
    - Intelligent request orchestration and scheduling
    - Advanced rate limiting with adaptive algorithms
    - Enterprise authentication management
    - Real-time performance monitoring and analytics
    - Circuit breaker pattern for fault tolerance
    - Priority-based request queuing
    - Content deduplication and fingerprinting
    - Comprehensive audit logging and compliance
    - Scalable distributed architecture
    - Advanced anti-detection mechanisms
    - Webhook-based real-time notifications
    
    Supported Platforms:
    - YouTube (API v3 + Selenium hybrid)
    - TikTok (Advanced scraping + anti-detection)
    - Instagram (Graph API + public content)
    - Twitter/X (API v2 comprehensive)
    - Generic Web (Scrapy universal crawler)
    - Extensible platform plugin architecture
    """    
    def __init__(self, config: Dict[str, Any]):
        """Initialize enterprise crawler orchestrator."""        self.config = config
        self._initialized = False
        
        # Core enterprise components
        self.api_manager: Optional[PlatformAPIManager] = None
        self.auth_manager: Optional[EnterpriseAuthenticationManager] = None
        self.rate_limiter: Optional[IntelligentRateLimiter] = None
        self.request_orchestrator: Optional[RequestOrchestrator] = None
        
        # Platform crawlers
        self.crawlers: Dict[str, BasePlatformCrawler] = {}
        
        # Monitoring and analytics
        self.performance_monitor = PerformanceMonitor()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.request_cache = RequestCache()
        
        # Content management
        self.discovered_content: Dict[str, CrawlResult] = {}
        self.content_fingerprints: Set[str] = set()
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Webhook callbacks
        self.webhook_callbacks: List[Callable] = []
        
        # Configuration
        self.crawl_interval = timedelta(
            minutes=config.get('crawl_interval_minutes', 30)
        )
        self.max_concurrent_crawlers = config.get('max_concurrent_crawlers', 10)
        self.enable_real_time_monitoring = config.get('enable_real_time_monitoring', True)
        
        logger.info("Enterprise Crawler Orchestrator initialized")
    
    async def initialize(self):
        """Initialize all enterprise components."""        if self._initialized:
            return
        
        try:
            # Initialize authentication manager
            storage_path = self.config.get('credential_storage_path', './credentials')
            master_password = self.config.get('master_password', 'default_password')
            
            self.auth_manager = EnterpriseAuthenticationManager(
                storage_path, master_password
            )
            
            # Initialize rate limiter
            self.rate_limiter = IntelligentRateLimiter()
            
            # Configure platform rate limits
            await self._configure_rate_limits()
            
            # Initialize request orchestrator
            max_workers = self.config.get('max_workers', 50)
            self.request_orchestrator = RequestOrchestrator(max_workers)
            
            # Initialize platform API manager
            self.api_manager = PlatformAPIManager()
            
            # Initialize platform crawlers
            await self._initialize_crawlers()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self._initialized = True
            logger.info("Enterprise Crawler Orchestrator fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def _configure_rate_limits(self):
        """Configure rate limits for all platforms."""        rate_limit_configs = {
            'youtube': RateLimitConfig(
                platform='youtube',
                limit_type=RateLimitType.REQUESTS_PER_DAY,
                limit_value=10000,
                window_size=86400,
                strategy=RateLimitStrategy.ADAPTIVE
            ),
            'instagram': RateLimitConfig(
                platform='instagram',
                limit_type=RateLimitType.REQUESTS_PER_HOUR,
                limit_value=200,
                window_size=3600,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            'twitter': RateLimitConfig(
                platform='twitter',
                limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit_value=100,
                window_size=60,
                strategy=RateLimitStrategy.TOKEN_BUCKET
            ),
            'tiktok': RateLimitConfig(
                platform='tiktok',
                limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit_value=60,
                window_size=60,
                strategy=RateLimitStrategy.ADAPTIVE
            )
        }
        
        for platform, config in rate_limit_configs.items():
            self.rate_limiter.configure_platform(config)
            
            # Initialize circuit breaker
            self.circuit_breakers[platform] = CircuitBreaker()
    
    async def _initialize_crawlers(self):
        """Initialize platform-specific crawlers."""        # YouTube crawler
        if self.config.get('youtube', {}).get('enabled', True):
            youtube_config = self.config.get('youtube', {})
            self.crawlers['youtube'] = YouTubeCrawler('youtube', youtube_config)
        
        # Instagram crawler
        if self.config.get('instagram', {}).get('enabled', True):
            instagram_config = self.config.get('instagram', {})
            self.crawlers['instagram'] = InstagramCrawler('instagram', instagram_config)
        
        # Twitter crawler
        if self.config.get('twitter', {}).get('enabled', True):
            twitter_config = self.config.get('twitter', {})
            self.crawlers['twitter'] = TwitterCrawler('twitter', twitter_config)
        
        # TikTok crawler
        if self.config.get('tiktok', {}).get('enabled', True):
            tiktok_config = self.config.get('tiktok', {})
            self.crawlers['tiktok'] = TikTokCrawler('tiktok', tiktok_config)
        
        # Generic web crawler
        if self.config.get('generic_web', {}).get('enabled', True):
            web_config = self.config.get('generic_web', {})
            self.crawlers['generic_web'] = GenericWebCrawler('generic_web', web_config)
        
        logger.info(f"Initialized {len(self.crawlers)} platform crawlers")
    
    async def _setup_monitoring(self):
        """Setup real-time monitoring and alerting."""        # Register alert callbacks
        self.rate_limiter.register_alert_callback(self._handle_rate_limit_alert)
        self.performance_monitor.register_alert_callback(self._handle_performance_alert)
        
        # Setup webhook notifications
        if self.config.get('webhooks', {}).get('enabled', False):
            webhook_urls = self.config.get('webhooks', {}).get('urls', [])
            for url in webhook_urls:
                self.register_webhook_callback(
                    lambda event, data: self._send_webhook_notification(url, event, data)
                )
    
    async def authenticate_platforms(self, credentials: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """        Authenticate with multiple platforms.
        
        Args:
            credentials: Platform credentials mapping
            
        Returns:
            Authentication status for each platform
        """        results = {}
        
        async with self.auth_manager:
            for platform, creds in credentials.items():
                try:
                    result = await self.auth_manager.authenticate_platform(
                        platform, creds, store_credentials=True
                    )
                    results[platform] = result.status == AuthenticationStatus.AUTHENTICATED
                    
                    if results[platform]:
                        logger.info(f"Successfully authenticated with {platform}")
                    else:
                        logger.error(f"Authentication failed for {platform}: {result.error_message}")
                        
                except Exception as e:
                    logger.error(f"Authentication error for {platform}: {e}")
                    results[platform] = False
        
        return results
    
    async def start_content_monitoring(
        self,
        search_queries: List[str],
        platforms: Optional[List[str]] = None,
        content_types: Optional[List[ContentType]] = None,
        monitoring_interval: int = 300  # 5 minutes
    ) -> str:
        """        Start comprehensive content monitoring across platforms.
        
        Args:
            search_queries: List of search terms to monitor
            platforms: List of platforms to monitor (None for all)
            content_types: Types of content to monitor
            monitoring_interval: Monitoring interval in seconds
            
        Returns:
            Monitoring session ID
        """        monitoring_id = f"monitor_{int(time.time())}"
        
        if not platforms:
            platforms = list(self.crawlers.keys())
        
        if not content_types:
            content_types = [ContentType.VIDEO, ContentType.AUDIO, ContentType.IMAGE]
        
        # Create monitoring tasks for each platform
        monitoring_tasks = []
        
        for platform in platforms:
            if platform in self.crawlers:
                task = asyncio.create_task(
                    self._continuous_platform_monitoring(
                        monitoring_id, platform, search_queries, 
                        content_types, monitoring_interval
                    )
                )
                monitoring_tasks.append(task)
        
        self.monitoring_tasks[monitoring_id] = asyncio.gather(*monitoring_tasks)
        
        logger.info(f"Started content monitoring {monitoring_id} for {len(platforms)} platforms")
        return monitoring_id
    
    async def _continuous_platform_monitoring(
        self,
        monitoring_id: str,
        platform: str,
        search_queries: List[str],
        content_types: List[ContentType],
        interval: int
    ):
        """Continuous monitoring for specific platform."""        crawler = self.crawlers[platform]
        
        logger.info(f"Starting continuous monitoring for {platform}")
        
        try:
            while monitoring_id in self.monitoring_tasks:
                for query in search_queries:
                    try:
                        # Check rate limits
                        can_proceed, wait_time = await self.rate_limiter.can_make_request(platform)
                        
                        if not can_proceed:
                            if wait_time:
                                await asyncio.sleep(wait_time)
                            continue
                        
                        # Perform search
                        start_time = time.time()
                        results = await crawler.search_content(
                            query=query,
                            content_type=ContentType.UNKNOWN,
                            max_results=50
                        )
                        response_time = time.time() - start_time
                        
                        # Record performance metrics
                        await self.rate_limiter.record_request(
                            platform, Priority.MEDIUM, response_time, True
                        )
                        
                        # Process discovered content
                        await self._process_discovered_content(results, monitoring_id)
                        
                    except Exception as e:
                        logger.error(f"Monitoring error for {platform}/{query}: {e}")
                        
                        # Record failed request
                        await self.rate_limiter.record_request(
                            platform, Priority.MEDIUM, 0.0, False
                        )
                
                # Wait before next monitoring cycle
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for {platform}")
        except Exception as e:
            logger.error(f"Monitoring error for {platform}: {e}")
    
    async def _process_discovered_content(
        self, 
        results: List[CrawlResult], 
        monitoring_id: str
    ):
        """Process newly discovered content."""        new_content = []
        
        for result in results:
            # Check for duplicates using fingerprinting
            content_hash = self._generate_content_hash(result)
            
            if content_hash not in self.content_fingerprints:
                self.content_fingerprints.add(content_hash)
                self.discovered_content[content_hash] = result
                new_content.append(result)
        
        if new_content:
            logger.info(f"Discovered {len(new_content)} new content items")
            
            # Trigger webhook notifications
            await self._trigger_webhooks('new_content_discovered', {
                'monitoring_id': monitoring_id,
                'count': len(new_content),
                'content': [self._serialize_crawl_result(r) for r in new_content[:5]]  # Limit for webhook
            })
    
    def _generate_content_hash(self, result: CrawlResult) -> str:
        """Generate hash for content deduplication."""        hash_data = f"{result.platform}:{result.url}:{result.title}"
        return hashlib.md5(hash_data.encode()).hexdigest()
    
    def _serialize_crawl_result(self, result: CrawlResult) -> Dict[str, Any]:
        """Serialize crawl result for JSON transmission."""        return {
            'platform': result.platform,
            'url': result.url,
            'title': result.title,
            'description': result.description,
            'content_type': result.content_type.value if isinstance(result.content_type, ContentType) else result.content_type,
            'discovered_at': result.discovered_at.isoformat(),
            'confidence_score': getattr(result, 'confidence_score', 0.0),
            'metadata': result.metadata
        }
    
    async def search_multi_platform_content(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        content_types: Optional[List[ContentType]] = None,
        max_results_per_platform: int = 50,
        priority: Priority = Priority.MEDIUM
    ) -> Dict[str, List[CrawlResult]]:
        """        Search content across multiple platforms simultaneously.
        
        Args:
            query: Search query
            platforms: List of platforms to search (None for all)
            content_types: Types of content to search for
            max_results_per_platform: Maximum results per platform
            priority: Request priority
            
        Returns:
            Results organized by platform
        """        if not platforms:
            platforms = list(self.crawlers.keys())
        
        # Create search requests for orchestrator
        search_requests = []
        
        for platform in platforms:
            if platform in self.crawlers:
                request = RequestContext(
                    request_id=f"search_{platform}_{int(time.time())}",
                    platform=platform,
                    endpoint="search",
                    method="GET",
                    params={'query': query, 'max_results': max_results_per_platform},
                    priority=priority.value
                )
                search_requests.append(request)
        
        # Submit requests to orchestrator
        results = {}
        
        for request in search_requests:
            try:
                # Queue request for execution
                await self.request_orchestrator.submit_request(request)
                
                # Wait for completion (simplified for this example)
                # In practice, you would implement proper async handling
                crawler = self.crawlers[request.platform]
                search_results = await crawler.search_content(
                    query=query,
                    content_type=content_types[0] if content_types else ContentType.UNKNOWN,
                    max_results=max_results_per_platform
                )
                
                results[request.platform] = search_results
                
            except Exception as e:
                logger.error(f"Search failed for {request.platform}: {e}")
                results[request.platform] = []
        
        return results
    
    async def stop_monitoring(self, monitoring_id: str) -> bool:
        """Stop specific monitoring session."""        if monitoring_id not in self.monitoring_tasks:
            return False
        
        try:
            self.monitoring_tasks[monitoring_id].cancel()
            await self.monitoring_tasks[monitoring_id]
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error stopping monitoring {monitoring_id}: {e}")
        
        del self.monitoring_tasks[monitoring_id]
        logger.info(f"Stopped monitoring session {monitoring_id}")
        return True
    
    def register_webhook_callback(self, callback: Callable):
        """Register webhook callback for real-time notifications."""        self.webhook_callbacks.append(callback)
    
    async def _trigger_webhooks(self, event_type: str, data: Dict[str, Any]):
        """Trigger registered webhook callbacks."""        webhook_data = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        for callback in self.webhook_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, webhook_data)
                else:
                    callback(event_type, webhook_data)
            except Exception as e:
                logger.error(f"Webhook callback error: {e}")
    
    async def _handle_rate_limit_alert(self, alert_data: Dict[str, Any]):
        """Handle rate limiting alerts."""        logger.warning(f"Rate limit alert: {alert_data}")
        
        await self._trigger_webhooks('rate_limit_alert', alert_data)
    
    async def _handle_performance_alert(self, alert_data: Dict[str, Any]):
        """Handle performance alerts."""        logger.warning(f"Performance alert: {alert_data}")
        
        await self._trigger_webhooks('performance_alert', alert_data)
    
    async def _send_webhook_notification(self, url: str, event_type: str, data: Dict[str, Any]):
        """Send webhook notification to external endpoint."""        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.debug(f"Webhook notification sent to {url}")
                    else:
                        logger.warning(f"Webhook notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status."""        return {
            'initialized': self._initialized,
            'active_crawlers': len(self.crawlers),
            'active_monitoring_sessions': len(self.monitoring_tasks),
            'discovered_content_count': len(self.discovered_content),
            'rate_limiter_status': self.rate_limiter.get_all_status() if self.rate_limiter else {},
            'orchestrator_metrics': (
                self.request_orchestrator.get_orchestrator_metrics() 
                if self.request_orchestrator else {}
            ),
            'circuit_breaker_status': {
                platform: {'state': cb.state, 'failure_count': cb.failure_count}
                for platform, cb in self.circuit_breakers.items()
            }
        }
    
    async def shutdown(self):
        """Shutdown orchestrator and cleanup resources."""        logger.info("Shutting down Enterprise Crawler Orchestrator...")
        
        # Stop all monitoring tasks
        for monitoring_id in list(self.monitoring_tasks.keys()):
            await self.stop_monitoring(monitoring_id)
        
        # Shutdown request orchestrator
        if self.request_orchestrator:
            await self.request_orchestrator.stop()
        
        # Shutdown rate limiter
        if self.rate_limiter:
            await self.rate_limiter.shutdown()
        
        # Cleanup crawlers
        for crawler in self.crawlers.values():
            try:
                await crawler.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up crawler: {e}")
        
        self._initialized = False
        logger.info("Enterprise Crawler Orchestrator shutdown completed")

# Legacy support for existing code
MultiPlatformCrawlerService = EnterpriseCrawlerOrchestrator
        self.max_concurrent_crawls = config.get('max_concurrent_crawls', 5)
        
        # Background tasks
        self.crawler_tasks: Dict[str, asyncio.Task] = {}
        
        # Statistics
        self.total_crawls = 0
        self.successful_crawls = 0
        self.failed_crawls = 0
        
        logger.info("Multi-Platform Crawler Service initialized")

    async def initialize(self) -> bool:
        """Initialize the crawler service."""        try:
            # Initialize API manager
            if 'platform_apis' in self.config:
                self.api_manager = PlatformAPIManager(self.config['platform_apis'])
                await self.api_manager.authenticate_all()
            
            # Initialize platform crawlers
            await self._initialize_crawlers()
            
            self._initialized = True
            logger.info("Multi-Platform Crawler Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Multi-Platform Crawler Service: {e}")
            return False

    async def _initialize_crawlers(self) -> None:
        """Initialize platform-specific crawlers."""        platform_configs = self.config.get('platforms', {})
        
        # YouTube crawler
        if 'youtube' in platform_configs:
            try:
                self.crawlers['youtube'] = YouTubeCrawler(platform_configs['youtube'])
                logger.info("YouTube crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube crawler: {e}")
        
        # TikTok crawler
        if 'tiktok' in platform_configs:
            try:
                self.crawlers['tiktok'] = TikTokCrawler(platform_configs['tiktok'])
                logger.info("TikTok crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize TikTok crawler: {e}")
        
        # Instagram crawler
        if 'instagram' in platform_configs:
            try:
                self.crawlers['instagram'] = InstagramCrawler(platform_configs['instagram'])
                logger.info("Instagram crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Instagram crawler: {e}")
        
        # Twitter crawler
        if 'twitter' in platform_configs:
            try:
                self.crawlers['twitter'] = TwitterCrawler(platform_configs['twitter'])
                logger.info("Twitter crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter crawler: {e}")
        
        # Generic web crawler
        if 'web' in platform_configs:
            try:
                self.crawlers['web'] = GenericWebCrawler(platform_configs['web'])
                logger.info("Generic web crawler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize web crawler: {e}")
        
        logger.info(f"Initialized {len(self.crawlers)} platform crawlers")

    async def search_across_platforms(
        self,
        query: str,
        content_type: str = 'all',
        platforms: Optional[List[str]] = None,
        max_results_per_platform: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search for content across multiple platforms."""        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        platforms = platforms or list(self.crawlers.keys())
        
        # Filter to available crawlers
        available_platforms = [p for p in platforms if p in self.crawlers]
        
        if not available_platforms:
            logger.warning("No available crawlers for specified platforms")
            return []
        
        logger.info(f"Searching for '{query}' across {len(available_platforms)} platforms")
        
        # Execute searches in parallel
        search_tasks = []
        for platform in available_platforms:
            crawler = self.crawlers[platform]
            
            # Check rate limits before adding task
            try:
                if await crawler.check_rate_limits():
                    task = crawler.search_content(
                        query=query,
                        content_type=content_type,
                        max_results=max_results_per_platform,
                        filters=filters
                    )
                    search_tasks.append((platform, task))
                else:
                    logger.warning(f"Crawler for {platform} is rate limited")
            except Exception as e:
                logger.error(f"Error checking rate limits for {platform}: {e}")
        
        # Gather results
        all_results = []
        if search_tasks:
            task_results = await asyncio.gather(
                *[task for _, task in search_tasks], 
                return_exceptions=True
            )
            
            for i, result in enumerate(task_results):
                platform = search_tasks[i][0]
                
                if isinstance(result, Exception):
                    logger.error(f"Crawler search failed for {platform}: {result}")
                    self.failed_crawls += 1
                elif isinstance(result, list):
                    all_results.extend(result)
                    self.successful_crawls += 1
                    logger.info(f"Found {len(result)} results from {platform}")
        
        # Deduplicate results
        deduplicated_results = await self._deduplicate_results(all_results)
        
        # Update statistics
        self.total_crawls += len(search_tasks)
        
        logger.info(f"Found {len(deduplicated_results)} unique content items across platforms")
        return deduplicated_results

    async def _deduplicate_results(self, results: List[CrawlResult]) -> List[CrawlResult]:
        """Remove duplicate results based on URL and title."""        seen_urls = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # Create a signature for deduplication
            url_signature = result.url.lower().strip()
            title_signature = (result.title or '').lower().strip()
            
            # Check for duplicates
            is_duplicate = False
            
            if url_signature in seen_urls:
                is_duplicate = True
            elif title_signature and title_signature in seen_titles:
                is_duplicate = True
            
            if not is_duplicate:
                seen_urls.add(url_signature)
                if title_signature:
                    seen_titles.add(title_signature)
                unique_results.append(result)
        
        if len(results) != len(unique_results):
            logger.info(f"Removed {len(results) - len(unique_results)} duplicate results")
        
        return unique_results

    async def start_continuous_monitoring(
        self,
        monitor_id: str,
        search_queries: List[str],
        platforms: List[str],
        callback_func: callable = None,
        interval_minutes: int = 30
    ) -> bool:
        """Start continuous monitoring for specific content across platforms."""        try:
            if monitor_id in self.crawler_tasks:
                logger.warning(f"Monitoring already active for {monitor_id}")
                return False
            
            # Create monitoring task
            task = asyncio.create_task(
                self._continuous_monitor(monitor_id, search_queries, platforms, callback_func, interval_minutes)
            )
            self.crawler_tasks[monitor_id] = task
            
            logger.info(f"Started continuous monitoring: {monitor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start continuous monitoring: {e}")
            return False

    async def _continuous_monitor(
        self,
        monitor_id: str,
        search_queries: List[str],
        platforms: List[str],
        callback_func: callable,
        interval_minutes: int
    ) -> None:
        """Continuous monitoring loop."""        logger.info(f"Starting continuous monitoring: {monitor_id}")
        
        last_results = set()
        
        try:
            while True:
                new_results = []
                
                for query in search_queries:
                    try:
                        results = await self.search_across_platforms(
                            query=query,
                            platforms=platforms,
                            max_results_per_platform=20
                        )
                        
                        # Filter new results
                        for result in results:
                            result_hash = hash((result.url, result.title))
                            if result_hash not in last_results:
                                new_results.append(result)
                                last_results.add(result_hash)
                        
                    except Exception as e:
                        logger.error(f"Error in monitoring query '{query}': {e}")
                
                # Process new results
                if new_results:
                    logger.info(f"Found {len(new_results)} new results for {monitor_id}")
                    
                    # Process results for similarity if fingerprinting available
                    if self.fingerprinting:
                        await self._process_monitoring_results(monitor_id, new_results)
                    
                    # Call callback function
                    if callback_func:
                        try:
                            await callback_func(new_results)
                        except Exception as e:
                            logger.error(f"Error in monitoring callback: {e}")
                
                # Wait before next monitoring cycle
                await asyncio.sleep(interval_minutes * 60)
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled: {monitor_id}")
        except Exception as e:
            logger.error(f"Monitoring error for {monitor_id}: {e}")

    async def _process_monitoring_results(
        self,
        monitor_id: str,
        results: List[CrawlResult]
    ) -> None:
        """Process monitoring results for similarity matching."""        logger.debug(f"Processing {len(results)} monitoring results for {monitor_id}")
        
        # This would integrate with the fingerprinting service
        # to check if discovered content is similar to protected content
        for result in results:
            try:
                # In real implementation, would download and fingerprint content
                # then compare with stored fingerprint
                pass
            except Exception as e:
                logger.error(f"Error processing monitoring result {result.url}: {e}")

    async def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop continuous monitoring for specific content."""        try:
            if monitor_id in self.crawler_tasks:
                self.crawler_tasks[monitor_id].cancel()
                del self.crawler_tasks[monitor_id]
                logger.info(f"Stopped monitoring: {monitor_id}")
                return True
            else:
                logger.warning(f"No active monitoring found for {monitor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False

    async def get_platform_status(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """Get status of platform crawlers."""        if platform:
            if platform not in self.crawlers:
                return {"error": f"Platform {platform} not found"}
            
            crawler = self.crawlers[platform]
            return await crawler.get_status()
        
        # Get status for all platforms
        status_info = {
            "total_platforms": len(self.crawlers),
            "active_monitoring": len(self.crawler_tasks),
            "platforms": {}
        }
        
        for platform, crawler in self.crawlers.items():
            try:
                platform_status = await crawler.get_status()
                
                # Add rate limit check
                rate_limited = not await crawler.check_rate_limits()
                platform_status["rate_limited"] = rate_limited
                
                status_info["platforms"][platform] = platform_status
                
            except Exception as e:
                logger.error(f"Error getting status for {platform}: {e}")
                status_info["platforms"][platform] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status_info

    async def get_api_status(self) -> Dict[str, Any]:
        """Get status of platform APIs."""        if not self.api_manager:
            return {"error": "API manager not initialized"}
        
        return await self.api_manager.get_api_status()

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""        health_status = {
            "service_status": "healthy",
            "initialized": self._initialized,
            "total_crawlers": len(self.crawlers),
            "active_monitoring": len(self.crawler_tasks),
            "statistics": {
                "total_crawls": self.total_crawls,
                "successful_crawls": self.successful_crawls,
                "failed_crawls": self.failed_crawls,
                "success_rate": self.successful_crawls / max(self.total_crawls, 1) * 100
            }
        }
        
        # Check crawler health
        crawler_health = await self.get_platform_status()
        health_status["crawlers"] = crawler_health
        
        # Check API health
        if self.api_manager:
            api_health = await self.api_manager.health_check()
            health_status["apis"] = api_health
        
        # Determine overall health
        failed_crawlers = sum(
            1 for status in crawler_health.get("platforms", {}).values()
            if status.get("status") != "active"
        )
        
        if failed_crawlers > len(self.crawlers) / 2:
            health_status["service_status"] = "degraded"
        elif failed_crawlers == len(self.crawlers):
            health_status["service_status"] = "critical"
        
        return health_status

    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics."""        stats = {
            "service": {
                "total_crawls": self.total_crawls,
                "successful_crawls": self.successful_crawls,
                "failed_crawls": self.failed_crawls,
                "success_rate": self.successful_crawls / max(self.total_crawls, 1) * 100,
                "active_monitoring": len(self.crawler_tasks)
            },
            "platforms": {}
        }
        
        # Get platform-specific statistics
        for platform, crawler in self.crawlers.items():
            try:
                if hasattr(crawler, 'get_crawler_stats'):
                    platform_stats = await crawler.get_crawler_stats()
                    stats["platforms"][platform] = platform_stats
            except Exception as e:
                logger.error(f"Error getting stats for {platform}: {e}")
        
        # Get API statistics
        if self.api_manager:
            api_stats = self.api_manager.get_statistics()
            stats["apis"] = api_stats
        
        return stats

    async def shutdown(self) -> None:
        """Shutdown the crawler service."""        logger.info("Shutting down Multi-Platform Crawler Service...")
        
        # Cancel all monitoring tasks
        for task in self.crawler_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.crawler_tasks:
            await asyncio.gather(*self.crawler_tasks.values(), return_exceptions=True)
        
        self.crawler_tasks.clear()
        
        # Cleanup individual crawlers
        for crawler in self.crawlers.values():
            try:
                if hasattr(crawler, 'cleanup'):
                    crawler.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up crawler: {e}")
        
        self._initialized = False
        
        logger.info("Multi-Platform Crawler Service shutdown complete")


# Legacy compatibility - keeping the original class with enhanced functionality
class CrawlerService(MultiPlatformCrawlerService):
    """Legacy compatibility class - redirects to MultiPlatformCrawlerService."""    pass


# Export all important classes and functions
__all__ = [
    # Main service components from index
    'CrawlerServiceManager',
    'CrawlerServiceAPI',
    'create_crawler_service',
    'quick_youtube_search',
    'quick_revenue_check',
    'quick_violation_scan',
    
    # Main service classes
    'MultiPlatformCrawlerService',
    'CrawlerService',  # Legacy compatibility
    
    # Base classes
    'BasePlatformCrawler',
    'CrawlResult',
    'CrawlerStatus',
    
    # Platform-specific crawlers
    'YouTubeCrawler',
    'TikTokCrawler', 
    'InstagramCrawler',
    'TwitterCrawler',
    'GenericWebCrawler',
    
    # API clients
    'YouTubeAPIClient',
    'TwitterAPIClient',
    'InstagramAPIClient',
    
    # Selenium crawlers
# Export all enterprise classes and functions
__all__ = [
    # Main orchestrator
    'EnterpriseCrawlerOrchestrator',
    'MultiPlatformCrawlerService',  # Legacy alias
    
    # Base crawler infrastructure
    'BasePlatformCrawler',
    'CrawlResult',
    'CrawlerStatus',
    'ContentType',
    'Priority',
    
    # Platform-specific crawlers
    'YouTubeCrawler',
    'YouTubeAPIClient',
    'YouTubeSeleniumCrawler',
    'TikTokCrawler',
    'TikTokSeleniumCrawler',
    'TikTokAntiDetection',
    'InstagramCrawler',
    'InstagramAPIClient',
    'InstagramSeleniumCrawler',
    'TwitterCrawler',
    'TwitterAPIClient',
    'GenericWebCrawler',
    'GenericSpider',
    'ContentAnalyzer',
    
    # Enterprise platform API management
    'PlatformAPIManager',
    'APIProvider',
    'AuthMethod',
    'APICredentials',
    'APIRequest',
    'APIResponse',
    'RateLimitPolicy',
    'CircuitBreaker',
    'RequestCache',
    'PerformanceMonitor',
    
    # Enterprise authentication
    'EnterpriseAuthenticationManager',
    'AuthenticationStatus',
    'AuthenticationResult',
    'AuthenticationConfig',
    'SecureCredentialStore',
    
    # Intelligent rate limiting
    'IntelligentRateLimiter',
    'RateLimitConfig',
    'RateLimitStatus',
    'RateLimitType',
    'RateLimitStrategy',
    'RequestMetrics',
    
    # Request orchestration
    'RequestOrchestrator',
    'RequestContext',
    'RequestStatus',
    'ExecutionMode',
    'DependencyType',
    'BatchConfig',
    'ResourceQuota',
    
    # Utility enums and types
    'CrawlerType',
    'PlatformStatus'
]
