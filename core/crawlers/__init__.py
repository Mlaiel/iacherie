"""Advanced Crawlers Module - Professional Content Surveillance & Protection
========================================================================

Comprehensive module for advanced web crawling, content monitoring, and 
rights protection across multiple platforms and websites. Features 
enterprise-grade surveillance, real-time violation detection, and 
intelligent content fingerprinting.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineering & Data Science: Advanced AI/ML Pipeline Architecture
- Database Architecture: Multi-tenant PostgreSQL + Redis + Vector DB
- Security Engineering: Enterprise-grade encryption & protection
- Microservices Architecture: Scalable distributed systems
- Audio Processing: Advanced spectral analysis & fingerprinting
- DevOps & Infrastructure: Kubernetes orchestration & monitoring
- Prompt Engineering: Sophisticated AI model optimization
"""# Core crawler infrastructure
from .base import BaseCrawler, CrawlResult
from .config import CrawlerConfig, PlatformConfig, CrawlerType, ContentType

# Advanced platform-specific crawlers
from .youtube_api import (
    YouTubeCrawler, YouTubeAPIManager, YouTubeContentExtractor,
    YouTubeVideoData, YouTubeChannelData
)
from .tiktok_scraper import (
    TikTokCrawler, TikTokAPIManager, TikTokWebScraper,
    TikTokVideoData, TikTokUserData
)
from .instagram_api import (
    InstagramCrawler, InstagramAPIManager, InstagramWebScraper,
    InstagramMediaData, InstagramUserData
)
from .twitter_api import (
    TwitterCrawler, TwitterAPIManager, TwitterWebScraper,
    TwitterTweetData, TwitterUserData
)
from .universal_web import (
    UniversalWebCrawler, ContentExtractor, ScrapyWebCrawler,
    WebsiteData, CrawlingTarget
)

# Orchestration and monitoring
from .orchestrator import (
    CrawlerOrchestrator, CrawlingTask, CrawlingJobResult,
    MonitoringMode
)
from .realtime_monitor import (
    RealTimeMonitor, CrawlerMetrics, ViolationTrend, SystemHealth
)

# Legacy components (existing)
from .web_monitor import WebContentMonitor, MonitoringTarget, ViolationReport
from .content_scanner import ContentViolationScanner, SimilarityResult, ViolationAssessment
from .social_tracker import SocialMediaTracker, PlatformData, TakedownRequest
from .seo_crawler import SEOAnalyticsCrawler, SEOMetrics, CompetitorAnalysis
from .piracy_detector import PiracyDetectionEngine, PiracyThreat, EvidencePackage
from .copyright_guardian import CopyrightGuardian, CopyrightRegistration, LegalAction
from .platform_monitor import PlatformMonitoringService, MonitoringTarget as PlatformTarget, PlatformAlert
from .data_harvester import DataHarvester, HarvestingTarget, HarvestResult, ExtractionRule

__all__ = [
    # Core infrastructure
    'BaseCrawler',
    'CrawlResult',
    'CrawlerConfig',
    'PlatformConfig',
    'CrawlerType',
    'ContentType',
    
    # Advanced platform crawlers
    'YouTubeCrawler',
    'YouTubeAPIManager',
    'YouTubeContentExtractor',
    'YouTubeVideoData',
    'YouTubeChannelData',
    'TikTokCrawler',
    'TikTokAPIManager',
    'TikTokWebScraper',
    'TikTokVideoData',
    'TikTokUserData',
    'InstagramCrawler',
    'InstagramAPIManager',
    'InstagramWebScraper',
    'InstagramMediaData',
    'InstagramUserData',
    'TwitterCrawler',
    'TwitterAPIManager',
    'TwitterWebScraper',
    'TwitterTweetData',
    'TwitterUserData',
    'UniversalWebCrawler',
    'ContentExtractor',
    'ScrapyWebCrawler',
    'WebsiteData',
    'CrawlingTarget',
    
    # Orchestration system
    'CrawlerOrchestrator',
    'CrawlingTask',
    'CrawlingJobResult',
    'MonitoringMode',
    'RealTimeMonitor',
    'CrawlerMetrics',
    'ViolationTrend',
    'SystemHealth',
    
    # Legacy components
    'WebContentMonitor',
    'ContentViolationScanner', 
    'SocialMediaTracker',
    'SEOAnalyticsCrawler',
    'PiracyDetectionEngine',
    'CopyrightGuardian',
    'PlatformMonitoringService',
    'DataHarvester',
    
    # Legacy data types
    'MonitoringTarget',
    'ViolationReport',
    'SimilarityResult',
    'ViolationAssessment',
    'PlatformData',
    'TakedownRequest',
    'SEOMetrics',
    'CompetitorAnalysis',
    'PiracyThreat',
    'EvidencePackage',
    'CopyrightRegistration',
    'LegalAction',
    'PlatformTarget',
    'PlatformAlert',
    'HarvestingTarget',
    'HarvestResult',
    'ExtractionRule'
]

from .web_monitor import WebContentMonitor
from .content_scanner import ContentViolationScanner
from .social_tracker import SocialMediaTracker
from .seo_crawler import SEOAnalyticsCrawler
from .piracy_detector import PiracyDetectionEngine
from .copyright_guardian import CopyrightGuardian
from .platform_monitor import PlatformMonitoringService
from .competitor_tracker import CompetitorAnalysisTracker

__all__ = [
    'WebContentMonitor',
    'ContentViolationScanner',
    'SocialMediaTracker',
    'SEOAnalyticsCrawler',
    'PiracyDetectionEngine',
    'CopyrightGuardian',
    'PlatformMonitoringService',
    'CompetitorAnalysisTracker'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."
