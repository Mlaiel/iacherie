#!/usr/bin/env python3
"""🕷️ MULTI-PLATFORM CONTENT CRAWLER SERVICE - MAIN INDEX MODULE
================================================================

Enterprise-grade content discovery and monitoring system main entry point.
Provides unified interface for all crawler functionalities across platforms.

📧 Contact: mlaiel@live.de
👨‍💻 Developer: Fahed Mlaiel
🏢 Company: Independent Software Developer

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
==================================
UNAUTHORIZED USE ABSOLUTELY PROHIBITED - LEGAL CONSEQUENCES WILL FOLLOW

This entire codebase, algorithms, concepts, architecture, and implementation 
methodologies are the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.

STRICT PROHIBITIONS:
❌ NO COPYING of code, concepts, or architecture without written authorization
❌ NO DISTRIBUTION or sharing of any part of this system  
❌ NO REVERSE ENGINEERING or attempting to recreate similar systems
❌ NO COMMERCIAL USE without explicit licensing agreement
❌ NO ACADEMIC USE without proper attribution and permission

Any violation will result in IMMEDIATE LEGAL ACTION under:
- German Copyright Law (Urheberrechtsgesetz)
- European Union Intellectual Property Directive
- International Copyright Treaties
- Criminal prosecution for commercial theft

WE MONITOR FOR UNAUTHORIZED USE - YOU WILL BE CAUGHT AND PROSECUTED
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import os

# Core Platform Imports
from .base_crawler import (
    BasePlatformCrawler,
    CrawlerConfig,
    PlatformType,
    ContentType,
    CrawlResult,
    CrawlerMetrics,
    RateLimitConfig,
    SecurityConfig
)

from .youtube_crawler import (
    YouTubeCrawler,
    YouTubeConfig,
    YouTubeVideoData,
    YouTubeChannelData,
    YouTubeAnalytics,
    YouTubeContentType
)

# Specialized Service Imports
from .revenue_monitoring_crawler import (
    RevenueMonitoringCrawler,
    RevenueData,
    MonetizationType,
    UnauthorizedUsage,
    RevenueCalculator,
    PlatformRevenueAPI,
    FinancialAnalytics
)

from .legal_violation_crawler import (
    LegalViolationCrawler,
    LegalViolation,
    ViolationType,
    ViolationSeverity,
    DMCANotice,
    LegalAnalyzer,
    JurisdictionMapper,
    EvidenceCollector
)

from .collaboration_discovery_crawler import (
    CollaborationDiscoveryCrawler,
    CreatorProfile,
    CollaborationType,
    CollaborationOpportunity,
    MatchmakingEngine,
    BrandPartnership,
    InfluencerNetwork,
    ROIPredictionEngine
)

from .market_intelligence_crawler import (
    MarketIntelligenceCrawler,
    TrendAnalysis,
    CompetitorAnalysis,
    MarketOpportunity,
    HashtagAnalyzer,
    ViralityPredictor,
    MarketCategory,
    IndustryInsights
)

# Configuration and Utils
from ..config.crawler_config import (
    CrawlerServiceConfig,
    PlatformAPIConfig,
    DatabaseConfig,
    CacheConfig,
    SecuritySettings
)

from ..utils.logger import setup_crawler_logger
from ..utils.metrics import MetricsCollector
from ..utils.cache import CrawlerCache
from ..utils.rate_limiter import GlobalRateLimiter


class CrawlerServiceManager:
    """    🎯 ENTERPRISE CRAWLER SERVICE MANAGER
    ====================================
    
    Central orchestration service for all crawler operations.
    Manages platform crawlers, coordinates tasks, and provides unified API.
    
    Features:
    - Multi-platform crawler coordination
    - Intelligent load balancing and rate limiting
    - Real-time monitoring and analytics
    - Error recovery and fault tolerance
    - Performance optimization and caching
    """    
    def __init__(self, config: CrawlerServiceConfig):
        """Initialize the crawler service manager."""        self.config = config
        self.logger = setup_crawler_logger("crawler_service_manager")
        self.metrics = MetricsCollector()
        self.cache = CrawlerCache(config.cache_config)
        self.rate_limiter = GlobalRateLimiter(config.rate_limit_config)
        
        # Initialize platform crawlers
        self.crawlers: Dict[PlatformType, BasePlatformCrawler] = {}
        self.specialized_crawlers: Dict[str, Any] = {}
        
        # Performance tracking
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.crawler_status: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_crawlers()
        
    def _initialize_crawlers(self):
        """Initialize all platform and specialized crawlers."""        try:
            # Initialize platform-specific crawlers
            if self.config.platforms.youtube.enabled:
                self.crawlers[PlatformType.YOUTUBE] = YouTubeCrawler(
                    self.config.platforms.youtube
                )
                
            # Initialize specialized service crawlers
            self.specialized_crawlers['revenue_monitoring'] = RevenueMonitoringCrawler(
                self.config, self.config.platform_apis
            )
            
            self.specialized_crawlers['legal_violation'] = LegalViolationCrawler(
                self.config, self.config.platform_apis
            )
            
            self.specialized_crawlers['collaboration_discovery'] = CollaborationDiscoveryCrawler(
                self.config, self.config.platform_apis
            )
            
            self.specialized_crawlers['market_intelligence'] = MarketIntelligenceCrawler(
                self.config, self.config.platform_apis
            )
            
            self.logger.info(f"Initialized {len(self.crawlers)} platform crawlers and "
                           f"{len(self.specialized_crawlers)} specialized crawlers")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crawlers: {e}")
            raise
    
    async def start_service(self) -> bool:
        """        🚀 START CRAWLER SERVICE
        =======================
        
        Starts all crawler services and begins monitoring operations.
        
        Returns:
            bool: True if service started successfully
        """        try:
            self.logger.info("Starting Enterprise Crawler Service...")
            
            # Start all platform crawlers
            for platform, crawler in self.crawlers.items():
                await crawler.initialize()
                self.crawler_status[platform.value] = {
                    'status': 'active',
                    'started_at': datetime.utcnow().isoformat(),
                    'requests_count': 0,
                    'errors_count': 0
                }
                
            # Start specialized crawlers
            for service_name, crawler in self.specialized_crawlers.items():
                await crawler.initialize()
                self.crawler_status[service_name] = {
                    'status': 'active',
                    'started_at': datetime.utcnow().isoformat(),
                    'requests_count': 0,
                    'errors_count': 0
                }
            
            # Start background monitoring
            self.active_tasks['health_monitor'] = asyncio.create_task(
                self._health_monitoring_loop()
            )
            
            self.active_tasks['metrics_collector'] = asyncio.create_task(
                self._metrics_collection_loop()
            )
            
            self.logger.info("✅ Enterprise Crawler Service started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start crawler service: {e}")
            return False
    
    async def stop_service(self) -> bool:
        """        🛑 STOP CRAWLER SERVICE
        ======================
        
        Gracefully stops all crawler services and cleanup resources.
        
        Returns:
            bool: True if service stopped successfully
        """        try:
            self.logger.info("Stopping Enterprise Crawler Service...")
            
            # Cancel all active tasks
            for task_name, task in self.active_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    
            # Stop all crawlers
            for platform, crawler in self.crawlers.items():
                await crawler.cleanup()
                
            for service_name, crawler in self.specialized_crawlers.items():
                await crawler.cleanup()
                
            # Clear status
            self.crawler_status.clear()
            self.active_tasks.clear()
            
            self.logger.info("✅ Enterprise Crawler Service stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop crawler service: {e}")
            return False
    
    async def crawl_platform_content(
        self,
        platform: PlatformType,
        search_params: Dict[str, Any],
        content_types: Optional[List[ContentType]] = None
    ) -> List[CrawlResult]:
        """        🔍 CRAWL PLATFORM CONTENT
        ========================
        
        Performs content crawling on specified platform with given parameters.
        
        Args:
            platform: Target platform for crawling
            search_params: Platform-specific search parameters
            content_types: Types of content to crawl (optional)
            
        Returns:
            List[CrawlResult]: Crawling results with discovered content
        """        try:
            if platform not in self.crawlers:
                raise ValueError(f"Platform {platform.value} not supported or not enabled")
                
            crawler = self.crawlers[platform]
            
            # Apply rate limiting
            await self.rate_limiter.acquire(platform.value)
            
            # Perform crawling
            results = await crawler.crawl_content(
                search_params=search_params,
                content_types=content_types or [ContentType.ALL]
            )
            
            # Update metrics
            self.crawler_status[platform.value]['requests_count'] += 1
            self.metrics.record_crawl_request(platform.value, len(results))
            
            self.logger.info(f"Crawled {len(results)} items from {platform.value}")
            return results
            
        except Exception as e:
            self.crawler_status[platform.value]['errors_count'] += 1
            self.logger.error(f"Failed to crawl {platform.value}: {e}")
            raise
    
    async def monitor_creator_revenue(
        self,
        creator_id: str,
        platforms: List[PlatformType],
        time_range: Optional[timedelta] = None
    ) -> Dict[str, RevenueData]:
        """        💰 MONITOR CREATOR REVENUE
        =========================
        
        Monitors creator revenue across specified platforms.
        
        Args:
            creator_id: Unique creator identifier
            platforms: List of platforms to monitor
            time_range: Time range for revenue analysis
            
        Returns:
            Dict[str, RevenueData]: Revenue data per platform
        """        try:
            revenue_crawler = self.specialized_crawlers['revenue_monitoring']
            
            revenue_data = {}
            for platform in platforms:
                platform_revenue = await revenue_crawler.crawl_revenue_data(
                    creator_id=creator_id,
                    platforms=[platform],
                    date_range=time_range
                )
                revenue_data[platform.value] = platform_revenue
                
            self.metrics.record_revenue_monitoring(creator_id, len(platforms))
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Failed to monitor creator revenue: {e}")
            raise
    
    async def detect_content_violations(
        self,
        content_fingerprints: List[str],
        platforms: Optional[List[PlatformType]] = None
    ) -> List[LegalViolation]:
        """        ⚖️ DETECT CONTENT VIOLATIONS
        ===========================
        
        Detects legal violations of protected content across platforms.
        
        Args:
            content_fingerprints: List of content fingerprints to monitor
            platforms: Platforms to scan (default: all enabled)
            
        Returns:
            List[LegalViolation]: Detected violations with evidence
        """        try:
            legal_crawler = self.specialized_crawlers['legal_violation']
            
            scan_platforms = platforms or list(self.crawlers.keys())
            
            violations = await legal_crawler.scan_legal_violations(
                content_fingerprints=content_fingerprints,
                platforms=scan_platforms
            )
            
            self.metrics.record_violation_scan(len(content_fingerprints), len(violations))
            return violations
            
        except Exception as e:
            self.logger.error(f"Failed to detect content violations: {e}")
            raise
    
    async def discover_collaboration_opportunities(
        self,
        creator_profile: CreatorProfile,
        collaboration_types: List[CollaborationType],
        target_platforms: Optional[List[PlatformType]] = None
    ) -> List[CollaborationOpportunity]:
        """        🤝 DISCOVER COLLABORATION OPPORTUNITIES
        ======================================
        
        Discovers collaboration opportunities for creators.
        
        Args:
            creator_profile: Creator's profile and preferences
            collaboration_types: Types of collaborations to find
            target_platforms: Platforms to search (default: all)
            
        Returns:
            List[CollaborationOpportunity]: Found collaboration opportunities
        """        try:
            collab_crawler = self.specialized_crawlers['collaboration_discovery']
            
            opportunities = await collab_crawler.find_collaboration_opportunities(
                creator_profile=creator_profile,
                collaboration_types=collaboration_types,
                platforms=target_platforms
            )
            
            self.metrics.record_collaboration_discovery(
                creator_profile.creator_id, len(opportunities)
            )
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Failed to discover collaborations: {e}")
            raise
    
    async def analyze_market_trends(
        self,
        categories: List[MarketCategory],
        platforms: List[PlatformType],
        time_range: Optional[timedelta] = None
    ) -> List[TrendAnalysis]:
        """        📊 ANALYZE MARKET TRENDS
        =======================
        
        Analyzes market trends and opportunities across platforms.
        
        Args:
            categories: Market categories to analyze
            platforms: Platforms to analyze
            time_range: Analysis time range
            
        Returns:
            List[TrendAnalysis]: Market trend analysis results
        """        try:
            market_crawler = self.specialized_crawlers['market_intelligence']
            
            trends = await market_crawler.analyze_market_trends(
                categories=categories,
                platforms=platforms,
                time_range=time_range or timedelta(days=7)
            )
            
            self.metrics.record_market_analysis(len(categories), len(trends))
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to analyze market trends: {e}")
            raise
    
    async def get_service_status(self) -> Dict[str, Any]:
        """        📊 GET SERVICE STATUS
        ====================
        
        Returns comprehensive service status and health metrics.
        
        Returns:
            Dict[str, Any]: Service status and metrics
        """        try:
            return {
                'service_name': 'Enterprise Crawler Service',
                'version': '1.0.0',
                'status': 'active',
                'uptime': self._calculate_uptime(),
                'crawlers': self.crawler_status,
                'active_tasks': len(self.active_tasks),
                'metrics': await self.metrics.get_summary(),
                'cache_stats': await self.cache.get_stats(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get service status: {e}")
            return {'error': str(e)}
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop."""        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check crawler health
                for platform, crawler in self.crawlers.items():
                    if hasattr(crawler, 'health_check'):
                        healthy = await crawler.health_check()
                        if not healthy:
                            self.logger.warning(f"Health check failed for {platform.value}")
                            
                # Check specialized crawlers
                for service_name, crawler in self.specialized_crawlers.items():
                    if hasattr(crawler, 'health_check'):
                        healthy = await crawler.health_check()
                        if not healthy:
                            self.logger.warning(f"Health check failed for {service_name}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop."""        while True:
            try:
                await asyncio.sleep(300)  # Collect every 5 minutes
                
                # Collect and store metrics
                await self.metrics.collect_system_metrics()
                await self.metrics.flush_to_storage()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
    
    def _calculate_uptime(self) -> str:
        """Calculate service uptime."""        # This would be implemented based on service start time tracking
        return "Active"


class CrawlerServiceAPI:
    """    🌐 CRAWLER SERVICE API INTERFACE
    ===============================
    
    High-level API interface for external applications to interact 
    with the crawler service. Provides simplified methods for common operations.
    """    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the crawler service API."""        self.config = self._load_config(config_path)
        self.service_manager = CrawlerServiceManager(self.config)
        self.logger = setup_crawler_logger("crawler_api")
    
    def _load_config(self, config_path: Optional[str]) -> CrawlerServiceConfig:
        """Load configuration from file or environment."""        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return CrawlerServiceConfig.from_dict(config_data)
        else:
            return CrawlerServiceConfig.from_environment()
    
    async def start(self) -> bool:
        """Start the crawler service."""        return await self.service_manager.start_service()
    
    async def stop(self) -> bool:
        """Stop the crawler service."""        return await self.service_manager.stop_service()
    
    async def crawl_youtube(
        self,
        query: str,
        max_results: int = 50,
        content_type: str = 'video'
    ) -> List[Dict[str, Any]]:
        """        Simplified YouTube crawling interface.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            content_type: Type of content ('video', 'channel', 'playlist')
            
        Returns:
            List[Dict[str, Any]]: Crawled content data
        """        search_params = {
            'query': query,
            'max_results': max_results,
            'type': content_type
        }
        
        results = await self.service_manager.crawl_platform_content(
            platform=PlatformType.YOUTUBE,
            search_params=search_params
        )
        
        return [result.to_dict() for result in results]
    
    async def monitor_revenue(
        self,
        creator_id: str,
        platforms: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """        Simplified revenue monitoring interface.
        
        Args:
            creator_id: Creator identifier
            platforms: List of platform names
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Revenue monitoring results
        """        platform_types = [PlatformType(p) for p in platforms]
        time_range = timedelta(days=days)
        
        revenue_data = await self.service_manager.monitor_creator_revenue(
            creator_id=creator_id,
            platforms=platform_types,
            time_range=time_range
        )
        
        return {
            platform: data.to_dict() if hasattr(data, 'to_dict') else str(data)
            for platform, data in revenue_data.items()
        }
    
    async def check_violations(
        self,
        content_fingerprints: List[str],
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """        Simplified violation checking interface.
        
        Args:
            content_fingerprints: Content fingerprints to check
            platforms: Platforms to check (optional)
            
        Returns:
            List[Dict[str, Any]]: Detected violations
        """        platform_types = None
        if platforms:
            platform_types = [PlatformType(p) for p in platforms]
        
        violations = await self.service_manager.detect_content_violations(
            content_fingerprints=content_fingerprints,
            platforms=platform_types
        )
        
        return [violation.to_dict() for violation in violations]
    
    async def find_collaborators(
        self,
        creator_data: Dict[str, Any],
        collaboration_types: List[str],
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """        Simplified collaboration discovery interface.
        
        Args:
            creator_data: Creator profile data
            collaboration_types: Types of collaborations to find
            platforms: Target platforms (optional)
            
        Returns:
            List[Dict[str, Any]]: Collaboration opportunities
        """        creator_profile = CreatorProfile.from_dict(creator_data)
        collab_types = [CollaborationType(ct) for ct in collaboration_types]
        platform_types = None
        if platforms:
            platform_types = [PlatformType(p) for p in platforms]
        
        opportunities = await self.service_manager.discover_collaboration_opportunities(
            creator_profile=creator_profile,
            collaboration_types=collab_types,
            target_platforms=platform_types
        )
        
        return [opp.to_dict() for opp in opportunities]
    
    async def analyze_trends(
        self,
        categories: List[str],
        platforms: List[str],
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """        Simplified trend analysis interface.
        
        Args:
            categories: Market categories to analyze
            platforms: Platforms to analyze
            days: Analysis time range in days
            
        Returns:
            List[Dict[str, Any]]: Trend analysis results
        """        market_categories = [MarketCategory(cat) for cat in categories]
        platform_types = [PlatformType(p) for p in platforms]
        time_range = timedelta(days=days)
        
        trends = await self.service_manager.analyze_market_trends(
            categories=market_categories,
            platforms=platform_types,
            time_range=time_range
        )
        
        return [trend.to_dict() for trend in trends]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status."""        return await self.service_manager.get_service_status()


# Convenience functions for quick access
async def create_crawler_service(config_path: Optional[str] = None) -> CrawlerServiceAPI:
    """    🚀 CREATE CRAWLER SERVICE
    ========================
    
    Convenience function to create and start a crawler service instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        CrawlerServiceAPI: Started crawler service instance
    """    api = CrawlerServiceAPI(config_path)
    await api.start()
    return api


async def quick_youtube_search(
    query: str,
    max_results: int = 10,
    config_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """    🔍 QUICK YOUTUBE SEARCH
    ======================
    
    Convenience function for quick YouTube content search.
    
    Args:
        query: Search query
        max_results: Maximum results
        config_path: Optional config path
        
    Returns:
        List[Dict[str, Any]]: Search results
    """    api = await create_crawler_service(config_path)
    try:
        results = await api.crawl_youtube(query, max_results)
        return results
    finally:
        await api.stop()


async def quick_revenue_check(
    creator_id: str,
    platforms: List[str],
    days: int = 30,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """    💰 QUICK REVENUE CHECK
    =====================
    
    Convenience function for quick revenue monitoring.
    
    Args:
        creator_id: Creator identifier
        platforms: Platforms to check
        days: Analysis period
        config_path: Optional config path
        
    Returns:
        Dict[str, Any]: Revenue data
    """    api = await create_crawler_service(config_path)
    try:
        revenue_data = await api.monitor_revenue(creator_id, platforms, days)
        return revenue_data
    finally:
        await api.stop()


async def quick_violation_scan(
    content_fingerprints: List[str],
    platforms: Optional[List[str]] = None,
    config_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """    ⚖️ QUICK VIOLATION SCAN
    ======================
    
    Convenience function for quick violation detection.
    
    Args:
        content_fingerprints: Content to check
        platforms: Platforms to scan
        config_path: Optional config path
        
    Returns:
        List[Dict[str, Any]]: Detected violations
    """    api = await create_crawler_service(config_path)
    try:
        violations = await api.check_violations(content_fingerprints, platforms)
        return violations
    finally:
        await api.stop()


# Export main classes and functions
__all__ = [
    # Main Classes
    'CrawlerServiceManager',
    'CrawlerServiceAPI',
    
    # Platform Crawlers
    'BasePlatformCrawler',
    'YouTubeCrawler',
    
    # Specialized Crawlers
    'RevenueMonitoringCrawler',
    'LegalViolationCrawler',
    'CollaborationDiscoveryCrawler',
    'MarketIntelligenceCrawler',
    
    # Data Models
    'CrawlResult',
    'RevenueData',
    'LegalViolation',
    'CreatorProfile',
    'TrendAnalysis',
    
    # Enums
    'PlatformType',
    'ContentType',
    'MonetizationType',
    'ViolationType',
    'CollaborationType',
    'MarketCategory',
    
    # Convenience Functions
    'create_crawler_service',
    'quick_youtube_search',
    'quick_revenue_check',
    'quick_violation_scan'
]


if __name__ == "__main__":
    """    🎯 CRAWLER SERVICE ENTRY POINT
    ==============================
    
    Direct execution entry point for the crawler service.
    Supports command-line arguments for configuration and testing.
    """    import argparse
    import sys
    
    async def main():
        parser = argparse.ArgumentParser(
            description="Enterprise Multi-Platform Content Crawler Service"
        )
        parser.add_argument(
            '--config', 
            type=str, 
            help='Path to configuration file'
        )
        parser.add_argument(
            '--test-mode', 
            action='store_true',
            help='Run in test mode with limited functionality'
        )
        parser.add_argument(
            '--log-level', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Logging level'
        )
        
        args = parser.parse_args()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger("crawler_main")
        
        try:
            # Create and start service
            logger.info("🚀 Starting Enterprise Crawler Service...")
            api = await create_crawler_service(args.config)
            
            if args.test_mode:
                logger.info("🧪 Running in test mode")
                # Run basic health checks
                status = await api.get_status()
                logger.info(f"Service Status: {status}")
                
                # Stop service after test
                await api.stop()
                logger.info("✅ Test completed successfully")
            else:
                logger.info("🔄 Service running. Press Ctrl+C to stop...")
                try:
                    # Keep service running
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("🛑 Shutdown requested by user")
                finally:
                    await api.stop()
                    logger.info("✅ Service stopped gracefully")
                    
        except Exception as e:
            logger.error(f"❌ Service failed: {e}")
            sys.exit(1)
    
    # Run the service
    asyncio.run(main())
