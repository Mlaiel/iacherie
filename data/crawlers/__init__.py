"""
IA Influencer Agent - Data Crawlers Module
==========================================

Advanced multi-platform web crawling system for content protection and discovery.
Implements AI-powered detection, anti-bot measures, and comprehensive data aggregation.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

# Platform crawlers
from .platform_crawler import PlatformCrawler
from .youtube_crawler import YouTubeCrawler
from .instagram_crawler import InstagramCrawler
from .tiktok_crawler import TikTokCrawler
from .twitter_crawler import TwitterCrawler
from .facebook_crawler import FacebookCrawler
from .spotify_crawler import SpotifyCrawler

# Generic web crawler
from .generic_web_crawler import GenericWebCrawler

# Management systems
from .crawler_manager import CrawlerManager, CrawlerTask, CrawlerMetrics

# Content detection and fingerprinting
from .content_detector import ContentDetector, ContentFingerprint, MatchResult, MultiModalAnalysis

# Anti-detection systems
from .anti_detection import AntiDetectionSystem, ProxyManager, BrowserProfile

# Result aggregation and analysis
from .result_aggregator import ResultAggregator, AggregatedResult, MatchScore, EvidenceCorrelation

# API quota management
from .api_quota_manager import APIQuotaManager, PlatformQuotas, QuotaStatus, QuotaAlert, UsageMetrics

# Advanced scheduling system
from .crawl_scheduler import CrawlScheduler, TaskConfiguration, TaskExecution, SchedulerMetrics, TaskStatus, TaskPriority, ScheduleType

from .platform_crawler import (
    PlatformCrawler, 
    CrawlerConfig, 
    ContentMatch, 
    ContentMatchType,
    CrawlerStatus,
    CrawlerResult
)
from .youtube_crawler import YouTubeCrawler
from .instagram_crawler import InstagramCrawler
from .tiktok_crawler import TikTokCrawler
from .generic_web_crawler import GenericWebCrawler, CrawlTarget, WebContent
from .crawler_manager import (
    CrawlerManager, 
    CrawlerTask, 
    CrawlerPriority, 
    ScheduleType,
    CrawlerMetrics
)
from .twitter_crawler import TwitterCrawler
from .facebook_crawler import FacebookCrawler
from .linkedin_crawler import LinkedInCrawler
from .twitch_crawler import TwitchCrawler
from .soundcloud_crawler import SoundCloudCrawler
from .discord_crawler import DiscordCrawler
from .reddit_crawler import RedditCrawler
from .spotify_crawler import SpotifyCrawler
from .vimeo_crawler import VimeoCrawler
from .dailymotion_crawler import DailymotionCrawler
from .snapchat_crawler import SnapchatCrawler
from .pinterest_crawler import PinterestCrawler
from .telegram_crawler import TelegramCrawler
from .whatsapp_business_crawler import WhatsAppBusinessCrawler
from .content_detector import ContentDetector, DetectionResult, DetectionType
from .anti_detection import AntiDetectionSystem, BrowserProfile, ProxyManager
from .crawl_scheduler import CrawlScheduler, ScheduledTask, RecurrencePattern
from .result_aggregator import ResultAggregator, AggregatedResult, MatchScore
from .api_quota_manager import APIQuotaManager, QuotaStatus, PlatformQuotas

__all__ = [
    # Core crawler infrastructure
    "PlatformCrawler",
    "CrawlerConfig", 
    "ContentMatch", 
    "ContentMatchType",
    "CrawlerStatus",
    "CrawlerResult",
    
    # Platform-specific crawlers
    "YouTubeCrawler",
    "InstagramCrawler",
    "TikTokCrawler", 
    "GenericWebCrawler",
    "TwitterCrawler",
    "FacebookCrawler",
    "LinkedInCrawler",
    "TwitchCrawler",
    "SoundCloudCrawler",
    "DiscordCrawler",
    "RedditCrawler",
    "SpotifyCrawler",
    "VimeoCrawler",
    "DailymotionCrawler",
    "SnapchatCrawler",
    "PinterestCrawler",
    "TelegramCrawler",
    "WhatsAppBusinessCrawler",
    
    # Generic web crawler components
    "CrawlTarget",
    "WebContent",
    
    # Crawler management system
    "CrawlerManager",
    "CrawlerTask", 
    "CrawlerPriority", 
    "ScheduleType",
    "CrawlerMetrics",
    
    # Advanced components
    "ContentDetector",
    "DetectionResult", 
    "DetectionType",
    "AntiDetectionSystem",
    "BrowserProfile",
    "ProxyManager",
    "CrawlScheduler",
    "ScheduledTask",
    "RecurrencePattern",
    "ResultAggregator",
    "AggregatedResult",
    "MatchScore",
    "APIQuotaManager",
    "QuotaStatus",
    "PlatformQuotas"
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"
