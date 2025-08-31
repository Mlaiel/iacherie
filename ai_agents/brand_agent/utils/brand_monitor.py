"""
Brand Monitor - Advanced Brand Reputation & Monitoring System

Real-time brand monitoring across multiple platforms and channels.
Tracks brand mentions, sentiment analysis, and reputation management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import hashlib

from textblob import TextBlob
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.text_analysis import SentimentAnalyzer, LanguageDetector
from ...utils.web_scraper import WebScraper
from ...utils.social_media_api import SocialMediaAPI
from ...utils.notification_service import NotificationService

logger = logging.getLogger(__name__)

class MonitoringSource(Enum):
    """Sources for brand monitoring"""
    GOOGLE_NEWS = "google_news"
    SOCIAL_MEDIA = "social_media"
    WEB_SEARCH = "web_search"
    MARKETPLACES = "marketplaces"
    FORUMS = "forums"
    BLOGS = "blogs"
    REVIEW_SITES = "review_sites"
    PATENT_DATABASES = "patent_databases"
    TRADEMARK_OFFICES = "trademark_offices"
    STREAMING_PLATFORMS = "streaming_platforms"
    APP_STORES = "app_stores"
    DOMAIN_REGISTRIES = "domain_registries"

class SentimentType(Enum):
    """Sentiment analysis categories"""
    HIGHLY_POSITIVE = "highly_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    HIGHLY_NEGATIVE = "highly_negative"
    
class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class BrandMention:
    """Single brand mention with analysis"""
    mention_id: str
    brand_id: str
    source: MonitoringSource
    platform: str
    url: str
    content: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    sentiment: SentimentType = SentimentType.NEUTRAL
    sentiment_score: float = 0.0
    reach_estimate: int = 0
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    context_keywords: List[str] = field(default_factory=list)
    threat_indicators: List[str] = field(default_factory=list)
    language: str = "en"
    location: Optional[str] = None
    verified_account: bool = False

@dataclass
class ReputationMetrics:
    """Brand reputation metrics and trends"""
    brand_id: str
    period_start: datetime
    period_end: datetime
    total_mentions: int = 0
    positive_mentions: int = 0
    negative_mentions: int = 0
    neutral_mentions: int = 0
    average_sentiment: float = 0.0
    sentiment_trend: float = 0.0
    reach_total: int = 0
    engagement_total: int = 0
    crisis_indicators: List[str] = field(default_factory=list)
    competitive_comparison: Dict[str, float] = field(default_factory=dict)
    reputation_score: float = 0.0
    trust_index: float = 0.0
    viral_risk_score: float = 0.0
    FORUMS = "forums"
    REVIEW_SITES = "review_sites"
    MARKETPLACES = "marketplaces"
    BLOGS = "blogs"
    NEWS_SITES = "news_sites"
    VIDEO_PLATFORMS = "video_platforms"

class SentimentScore(Enum):
    """Sentiment classification levels"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BrandMention:
    """Individual brand mention data"""
    mention_id: str
    brand_id: str
    source: MonitoringSource
    platform: str
    url: str
    title: str
    content: str
    author: Optional[str]
    published_at: datetime
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    sentiment_score: float = 0.0
    sentiment_label: SentimentScore = SentimentScore.NEUTRAL
    reach_estimate: int = 0
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    keywords_matched: List[str] = field(default_factory=list)
    context_category: Optional[str] = None
    influence_score: float = 0.0
    credibility_score: float = 0.0

@dataclass
class ReputationMetrics:
    """Brand reputation aggregated metrics"""
    brand_id: str
    time_period: str
    total_mentions: int = 0
    positive_mentions: int = 0
    negative_mentions: int = 0
    neutral_mentions: int = 0
    average_sentiment: float = 0.0
    sentiment_trend: str = "stable"  # improving, declining, stable
    reach_total: int = 0
    engagement_total: int = 0
    top_keywords: List[str] = field(default_factory=list)
    top_platforms: List[str] = field(default_factory=list)
    reputation_score: float = 0.0
    crisis_indicators: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MonitoringAlert:
    """Brand monitoring alert"""
    alert_id: str
    brand_id: str
    alert_level: AlertLevel
    alert_type: str
    message: str
    triggers: List[str]
    mention_ids: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)

class BrandMonitor:
    """
    Advanced Brand Reputation & Monitoring System
    
    Provides comprehensive brand monitoring including:
    - Multi-platform brand mention tracking
    - Real-time sentiment analysis
    - Reputation scoring and trends
    - Crisis detection and alerts
    - Competitive intelligence
    - Automated reporting
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.monitoring_active = False
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.language_detector = LanguageDetector()
        self.web_scraper = WebScraper()
        self.social_media_api = SocialMediaAPI()
        self.notification_service = NotificationService()
        
        # Data storage
        self.mentions: List[BrandMention] = []
        self.alerts: List[MonitoringAlert] = []
        self.reputation_history: List[ReputationMetrics] = []
        
        # Monitoring configuration
        self.monitoring_keywords = []
        self.excluded_keywords = []
        self.monitoring_sources = list(MonitoringSource)
        self.alert_thresholds = self._default_alert_thresholds()
        
        logger.info(f"Brand monitor initialized for brand: {brand_id}")

    def _default_alert_thresholds(self) -> Dict[str, Any]:
        """Default alert threshold configuration"""



        return {
            "negative_sentiment_spike": {
                "threshold": 0.3,
                "time_window": 3600,  # 1 hour
                "min_mentions": 5
            },
            "mention_volume_spike": {
                "threshold": 200,  # % increase
                "time_window": 7200,  # 2 hours
                "min_mentions": 10
            },
            "crisis_keywords": [
                "scandal", "controversy", "lawsuit", "fraud", "scam",
                "boycott", "protest", "fake", "counterfeit", "illegal"
            ],
            "reputation_drop": {
                "threshold": 0.2,  # 20% drop
                "time_window": 86400  # 24 hours
            }
        }

    async def configure_monitoring(self, config: Dict[str, Any]) -> None:
        """Configure brand monitoring parameters"""



        try:
            self.monitoring_keywords = config.get("keywords", [])
            self.excluded_keywords = config.get("excluded_keywords", [])
            
            # Update monitoring sources
            source_names = config.get("sources", [])
            if source_names:
                self.monitoring_sources = [
                    MonitoringSource(source) for source in source_names
                    if source in [s.value for s in MonitoringSource]
                ]
            
            # Update alert thresholds
            custom_thresholds = config.get("alert_thresholds", {})
            self.alert_thresholds.update(custom_thresholds)
            
            logger.info(f"Brand monitoring configured: {len(self.monitoring_keywords)} keywords, {len(self.monitoring_sources)} sources")
            
        except Exception as e:
            logger.error(f"Monitoring configuration failed: {str(e)}")
            raise

    async def start_monitoring(self) -> None:
        """Start continuous brand monitoring"""



        try:
            if self.monitoring_active:
                logger.warning("Brand monitoring already active")
                return
            
            self.monitoring_active = True
            
            # Start monitoring tasks for each source
            for source in self.monitoring_sources:
                task = asyncio.create_task(self._monitor_source(source))
                self.monitoring_tasks[source.value] = task
            
            # Start analysis tasks
            self.monitoring_tasks["sentiment_analysis"] = asyncio.create_task(self._continuous_sentiment_analysis())
            self.monitoring_tasks["alert_monitoring"] = asyncio.create_task(self._continuous_alert_monitoring())
            self.monitoring_tasks["reputation_calculation"] = asyncio.create_task(self._continuous_reputation_calculation())
            
            logger.info(f"Brand monitoring started for {len(self.monitoring_sources)} sources")
            
        except Exception as e:
            logger.error(f"Brand monitoring startup failed: {str(e)}")
            self.monitoring_active = False
            raise

    async def stop_monitoring(self) -> None:
        """Stop brand monitoring"""



        try:
            self.monitoring_active = False
            
            # Cancel all monitoring tasks
            for task_name, task in self.monitoring_tasks.items():
                task.cancel()
                logger.info(f"Cancelled monitoring task: {task_name}")
            
            self.monitoring_tasks.clear()
            logger.info("Brand monitoring stopped")
            
        except Exception as e:
            logger.error(f"Brand monitoring stop failed: {str(e)}")

    async def _monitor_source(self, source: MonitoringSource) -> None:
        """Monitor specific source for brand mentions"""



        try:
            while self.monitoring_active:
                try:
                    new_mentions = []
                    
                    if source == MonitoringSource.GOOGLE_NEWS:
                        new_mentions = await self._monitor_google_news()
                    elif source == MonitoringSource.SOCIAL_MEDIA:
                        new_mentions = await self._monitor_social_media()
                    elif source == MonitoringSource.FORUMS:
                        new_mentions = await self._monitor_forums()
                    elif source == MonitoringSource.REVIEW_SITES:
                        new_mentions = await self._monitor_review_sites()
                    elif source == MonitoringSource.MARKETPLACES:
                        new_mentions = await self._monitor_marketplaces()
                    elif source == MonitoringSource.BLOGS:
                        new_mentions = await self._monitor_blogs()
                    elif source == MonitoringSource.NEWS_SITES:
                        new_mentions = await self._monitor_news_sites()
                    elif source == MonitoringSource.VIDEO_PLATFORMS:
                        new_mentions = await self._monitor_video_platforms()
                    
                    # Process new mentions
                    for mention in new_mentions:
                        await self._process_new_mention(mention)
                    
                    if new_mentions:
                        logger.info(f"Found {len(new_mentions)} new mentions from {source.value}")
                    
                    # Wait before next scan (vary by source)
                    wait_time = self._get_source_scan_interval(source)
                    await asyncio.sleep(wait_time)
                    
                except asyncio.CancelledError:
                    logger.info(f"Source monitoring cancelled: {source.value}")
                    break
                except Exception as e:
                    logger.error(f"Source monitoring error ({source.value}): {str(e)}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
                    
        except Exception as e:
            logger.error(f"Source monitoring task failed ({source.value}): {str(e)}")

    def _get_source_scan_interval(self, source: MonitoringSource) -> int:
        """Get scan interval for different sources"""
        intervals = {
            MonitoringSource.GOOGLE_NEWS: 1800,      # 30 minutes
            MonitoringSource.SOCIAL_MEDIA: 900,      # 15 minutes
            MonitoringSource.FORUMS: 3600,           # 1 hour
            MonitoringSource.REVIEW_SITES: 7200,     # 2 hours
            MonitoringSource.MARKETPLACES: 14400,    # 4 hours
            MonitoringSource.BLOGS: 7200,            # 2 hours
            MonitoringSource.NEWS_SITES: 1800,       # 30 minutes
            MonitoringSource.VIDEO_PLATFORMS: 3600   # 1 hour
        }
        return intervals.get(source, 3600)

    async def _monitor_google_news(self) -> List[BrandMention]:
        """Monitor Google News for brand mentions"""
        mentions = []
        
        try:
            for keyword in self.monitoring_keywords:
                # Use Google News API or RSS feeds
                news_results = await self._search_google_news(keyword)
                
                for result in news_results:
                    if self._should_include_mention(result.get("title", ""), result.get("content", "")):
                        mention = await self._create_mention_from_news(result, keyword)
                        mentions.append(mention)
                        
        except Exception as e:
            logger.error(f"Google News monitoring failed: {str(e)}")
            
        return mentions

    async def _monitor_social_media(self) -> List[BrandMention]:
        """Monitor social media platforms for brand mentions"""
        mentions = []
        
        try:
            platforms = ["twitter", "facebook", "instagram", "linkedin", "tiktok"]
            
            for platform in platforms:
                for keyword in self.monitoring_keywords:
                    platform_mentions = await self._search_social_platform(platform, keyword)
                    
                    for mention_data in platform_mentions:
                        if self._should_include_mention(mention_data.get("content", "")):
                            mention = await self._create_mention_from_social(mention_data, platform, keyword)
                            mentions.append(mention)
                            
        except Exception as e:
            logger.error(f"Social media monitoring failed: {str(e)}")
            
        return mentions

    async def _monitor_forums(self) -> List[BrandMention]:
        """Monitor forums and discussion boards"""
        mentions = []
        
        try:
            forum_sites = [
                "reddit.com", "quora.com", "stackexchange.com",
                "disqus.com", "producthunt.com"
            ]
            
            for site in forum_sites:
                for keyword in self.monitoring_keywords:
                    forum_mentions = await self._search_forum_site(site, keyword)
                    mentions.extend(forum_mentions)
                    
        except Exception as e:
            logger.error(f"Forum monitoring failed: {str(e)}")
            
        return mentions

    async def _monitor_review_sites(self) -> List[BrandMention]:
        """Monitor review sites and rating platforms"""
        mentions = []
        
        try:
            review_sites = [
                "trustpilot.com", "yelp.com", "glassdoor.com",
                "tripadvisor.com", "google.com/reviews"
            ]
            
            for site in review_sites:
                for keyword in self.monitoring_keywords:
                    reviews = await self._search_review_site(site, keyword)
                    mentions.extend(reviews)
                    
        except Exception as e:
            logger.error(f"Review site monitoring failed: {str(e)}")
            
        return mentions

    async def _search_google_news(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Google News for keyword mentions"""



        try:
            # This would integrate with Google News API
            # For now, return placeholder data
            return [
                {
                    "title": f"News article about {keyword}",
                    "content": f"Content mentioning {keyword} in news context",
                    "url": f"https://news.example.com/article-{keyword}",
                    "published_at": datetime.utcnow(),
                    "author": "News Author"
                }
            ]
        except Exception as e:
            logger.error(f"Google News search failed: {str(e)}")
            return []

    async def _search_social_platform(self, platform: str, keyword: str) -> List[Dict[str, Any]]:
        """Search social media platform for mentions"""



        try:
            # This would integrate with platform APIs (Twitter API, Facebook Graph API, etc.)
            return await self.social_media_api.search_mentions(platform, keyword)
        except Exception as e:
            logger.error(f"Social platform search failed ({platform}): {str(e)}")
            return []

    async def _search_forum_site(self, site: str, keyword: str) -> List[BrandMention]:
        """Search forum site for brand mentions"""
        mentions = []
        
        try:
            # Use web scraping or site-specific APIs
            search_results = await self.web_scraper.search_site(site, keyword)
            
            for result in search_results:
                if self._should_include_mention(result.get("content", "")):
                    mention = await self._create_mention_from_forum(result, site, keyword)
                    mentions.append(mention)
                    
        except Exception as e:
            logger.error(f"Forum search failed ({site}): {str(e)}")
            
        return mentions

    async def _search_review_site(self, site: str, keyword: str) -> List[BrandMention]:
        """Search review site for brand mentions"""
        mentions = []
        
        try:
            reviews = await self.web_scraper.search_reviews(site, keyword)
            
            for review in reviews:
                if self._should_include_mention(review.get("content", "")):
                    mention = await self._create_mention_from_review(review, site, keyword)
                    mentions.append(mention)
                    
        except Exception as e:
            logger.error(f"Review search failed ({site}): {str(e)}")
            
        return mentions

    def _should_include_mention(self, title: str, content: str = "") -> bool:
        """Check if mention should be included based on filters"""



        try:
            full_text = f"{title} {content}".lower()
            
            # Check excluded keywords
            for excluded in self.excluded_keywords:
                if excluded.lower() in full_text:
                    return False
            
            # Check if any monitoring keyword is present
            keyword_found = False
            for keyword in self.monitoring_keywords:
                if keyword.lower() in full_text:
                    keyword_found = True
                    break
            
            return keyword_found
            
        except Exception:
            return False

    async def _create_mention_from_news(self, result: Dict[str, Any], keyword: str) -> BrandMention:
        """Create BrandMention from news result"""
        mention_id = f"news_{hashlib.md5(result.get('url', '').encode()).hexdigest()[:12]}"
        
        mention = BrandMention(
            mention_id=mention_id,
            brand_id=self.brand_id,
            source=MonitoringSource.GOOGLE_NEWS,
            platform="google_news",
            url=result.get("url", ""),
            title=result.get("title", ""),
            content=result.get("content", ""),
            author=result.get("author"),
            published_at=result.get("published_at", datetime.utcnow()),
            keywords_matched=[keyword],
            context_category="news"
        )
        
        return mention

    async def _create_mention_from_social(self, result: Dict[str, Any], platform: str, keyword: str) -> BrandMention:
        """Create BrandMention from social media result"""
        mention_id = f"social_{platform}_{hashlib.md5(result.get('id', '').encode()).hexdigest()[:12]}"
        
        mention = BrandMention(
            mention_id=mention_id,
            brand_id=self.brand_id,
            source=MonitoringSource.SOCIAL_MEDIA,
            platform=platform,
            url=result.get("url", ""),
            title=result.get("title", ""),
            content=result.get("content", ""),
            author=result.get("author"),
            published_at=result.get("created_at", datetime.utcnow()),
            engagement_metrics=result.get("engagement", {}),
            reach_estimate=result.get("reach", 0),
            keywords_matched=[keyword],
            context_category="social_media"
        )
        
        return mention

    async def _create_mention_from_forum(self, result: Dict[str, Any], site: str, keyword: str) -> BrandMention:
        """Create BrandMention from forum result"""
        mention_id = f"forum_{site}_{hashlib.md5(result.get('url', '').encode()).hexdigest()[:12]}"
        
        mention = BrandMention(
            mention_id=mention_id,
            brand_id=self.brand_id,
            source=MonitoringSource.FORUMS,
            platform=site,
            url=result.get("url", ""),
            title=result.get("title", ""),
            content=result.get("content", ""),
            author=result.get("author"),
            published_at=result.get("published_at", datetime.utcnow()),
            keywords_matched=[keyword],
            context_category="forum_discussion"
        )
        
        return mention

    async def _create_mention_from_review(self, result: Dict[str, Any], site: str, keyword: str) -> BrandMention:
        """Create BrandMention from review result"""
        mention_id = f"review_{site}_{hashlib.md5(result.get('url', '').encode()).hexdigest()[:12]}"
        
        mention = BrandMention(
            mention_id=mention_id,
            brand_id=self.brand_id,
            source=MonitoringSource.REVIEW_SITES,
            platform=site,
            url=result.get("url", ""),
            title=result.get("title", ""),
            content=result.get("content", ""),
            author=result.get("author"),
            published_at=result.get("published_at", datetime.utcnow()),
            keywords_matched=[keyword],
            context_category="review",
            engagement_metrics={"rating": result.get("rating", 0)}
        )
        
        return mention

    async def _process_new_mention(self, mention: BrandMention) -> None:
        """Process a new brand mention"""



        try:
            # Analyze sentiment
            await self._analyze_mention_sentiment(mention)
            
            # Detect language
            mention.language = await self.language_detector.detect_language(mention.content)
            
            # Calculate influence and credibility scores
            mention.influence_score = await self._calculate_influence_score(mention)
            mention.credibility_score = await self._calculate_credibility_score(mention)
            
            # Store mention
            self.mentions.append(mention)
            
            # Check for immediate alerts
            await self._check_mention_alerts(mention)
            
            logger.debug(f"Processed new mention: {mention.mention_id}")
            
        except Exception as e:
            logger.error(f"Mention processing failed: {str(e)}")

    async def _analyze_mention_sentiment(self, mention: BrandMention) -> None:
        """Analyze sentiment of brand mention"""



        try:
            # Combine title and content for analysis
            text = f"{mention.title} {mention.content}"
            
            # Get sentiment score
            sentiment_result = await self.sentiment_analyzer.analyze_sentiment(text)
            mention.sentiment_score = sentiment_result.get("compound", 0.0)
            
            # Convert to sentiment label
            if mention.sentiment_score >= 0.5:
                mention.sentiment_label = SentimentScore.VERY_POSITIVE
            elif mention.sentiment_score >= 0.1:
                mention.sentiment_label = SentimentScore.POSITIVE
            elif mention.sentiment_score >= -0.1:
                mention.sentiment_label = SentimentScore.NEUTRAL
            elif mention.sentiment_score >= -0.5:
                mention.sentiment_label = SentimentScore.NEGATIVE
            else:
                mention.sentiment_label = SentimentScore.VERY_NEGATIVE
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            mention.sentiment_score = 0.0
            mention.sentiment_label = SentimentScore.NEUTRAL

    async def _calculate_influence_score(self, mention: BrandMention) -> float:
        """Calculate influence score of mention source"""



        try:
            base_score = 0.5
            
            # Platform influence multipliers
            platform_multipliers = {
                "twitter": 1.2,
                "facebook": 1.1,
                "instagram": 1.0,
                "linkedin": 1.3,
                "youtube": 1.4,
                "tiktok": 1.1,
                "reddit": 1.2,
                "google_news": 1.5
            }
            
            multiplier = platform_multipliers.get(mention.platform, 1.0)
            
            # Engagement boost
            engagement = mention.engagement_metrics
            if engagement:
                likes = engagement.get("likes", 0)
                shares = engagement.get("shares", 0)
                comments = engagement.get("comments", 0)
                
                engagement_boost = min((likes + shares * 2 + comments * 3) / 1000, 0.5)
                base_score += engagement_boost
            
            # Reach boost
            reach_boost = min(mention.reach_estimate / 100000, 0.3)  # Max 0.3 for 100k+ reach
            base_score += reach_boost
            
            return min(base_score * multiplier, 1.0)
            
        except Exception as e:
            logger.error(f"Influence score calculation failed: {str(e)}")
            return 0.5

    async def _calculate_credibility_score(self, mention: BrandMention) -> float:
        """Calculate credibility score of mention source"""



        try:
            base_score = 0.5
            
            # Source credibility ratings
            source_credibility = {
                MonitoringSource.GOOGLE_NEWS: 0.8,
                MonitoringSource.SOCIAL_MEDIA: 0.4,
                MonitoringSource.FORUMS: 0.6,
                MonitoringSource.REVIEW_SITES: 0.7,
                MonitoringSource.MARKETPLACES: 0.6,
                MonitoringSource.BLOGS: 0.5,
                MonitoringSource.NEWS_SITES: 0.8,
                MonitoringSource.VIDEO_PLATFORMS: 0.5
            }
            
            base_score = source_credibility.get(mention.source, 0.5)
            
            # Author credibility (if verifiable)
            if mention.author:
                # This would check author verification, follower count, etc.
                author_boost = 0.1  # Simplified
                base_score += author_boost
            
            # Content quality indicators
            content_length = len(mention.content)
            if content_length > 100:  # Substantial content
                base_score += 0.1
            if content_length > 500:  # Long-form content
                base_score += 0.1
                
            return min(base_score, 1.0)
            
        except Exception as e:
            logger.error(f"Credibility score calculation failed: {str(e)}")
            return 0.5

    async def _check_mention_alerts(self, mention: BrandMention) -> None:
        """Check if mention triggers any alerts"""



        try:
            alerts_triggered = []
            
            # Crisis keyword detection
            crisis_keywords = self.alert_thresholds.get("crisis_keywords", [])
            content_lower = mention.content.lower()
            
            for keyword in crisis_keywords:
                if keyword in content_lower:
                    alert = await self._create_crisis_alert(mention, keyword)
                    alerts_triggered.append(alert)
                    break
            
            # Very negative sentiment alert
            if mention.sentiment_score <= -0.7 and mention.influence_score >= 0.6:
                alert = await self._create_negative_sentiment_alert(mention)
                alerts_triggered.append(alert)
            
            # High influence negative mention
            if (mention.sentiment_score <= -0.3 and 
                mention.influence_score >= 0.8 and 
                mention.credibility_score >= 0.7):
                alert = await self._create_high_impact_alert(mention)
                alerts_triggered.append(alert)
            
            # Store and send alerts
            for alert in alerts_triggered:
                self.alerts.append(alert)
                await self._send_alert(alert)
                
        except Exception as e:
            logger.error(f"Mention alert checking failed: {str(e)}")

    async def _create_crisis_alert(self, mention: BrandMention, crisis_keyword: str) -> MonitoringAlert:
        """Create crisis-level alert"""
        alert_id = f"crisis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{mention.mention_id[:8]}"
        
        return MonitoringAlert(
            alert_id=alert_id,
            brand_id=self.brand_id,
            alert_level=AlertLevel.CRITICAL,
            alert_type="crisis_detection",
            message=f"Crisis keyword '{crisis_keyword}' detected in high-visibility mention",
            triggers=[f"crisis_keyword:{crisis_keyword}"],
            mention_ids=[mention.mention_id]
        )

    async def _create_negative_sentiment_alert(self, mention: BrandMention) -> MonitoringAlert:
        """Create negative sentiment alert"""
        alert_id = f"sentiment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{mention.mention_id[:8]}"
        
        return MonitoringAlert(
            alert_id=alert_id,
            brand_id=self.brand_id,
            alert_level=AlertLevel.HIGH,
            alert_type="negative_sentiment",
            message=f"Very negative sentiment detected (score: {mention.sentiment_score:.2f})",
            triggers=[f"sentiment_score:{mention.sentiment_score}"],
            mention_ids=[mention.mention_id]
        )

    async def _create_high_impact_alert(self, mention: BrandMention) -> MonitoringAlert:
        """Create high impact mention alert"""
        alert_id = f"impact_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{mention.mention_id[:8]}"
        
        return MonitoringAlert(
            alert_id=alert_id,
            brand_id=self.brand_id,
            alert_level=AlertLevel.MEDIUM,
            alert_type="high_impact_negative",
            message=f"High-impact negative mention detected (influence: {mention.influence_score:.2f})",
            triggers=[f"influence_score:{mention.influence_score}", f"sentiment_score:{mention.sentiment_score}"],
            mention_ids=[mention.mention_id]
        )

    async def _send_alert(self, alert: MonitoringAlert) -> None:
        """Send alert through notification service"""



        try:
            await self.notification_service.send_alert(
                alert_level=alert.alert_level.value,
                message=alert.message,
                alert_data=alert.__dict__
            )
            
            logger.info(f"Alert sent: {alert.alert_id} ({alert.alert_level.value})")
            
        except Exception as e:
            logger.error(f"Alert sending failed: {str(e)}")

    async def _continuous_sentiment_analysis(self) -> None:
        """Continuous sentiment analysis task"""



        try:
            while self.monitoring_active:
                try:
                    # Analyze recent mentions that haven't been analyzed
                    recent_mentions = [
                        m for m in self.mentions[-100:]  # Last 100 mentions
                        if m.sentiment_score == 0.0  # Not yet analyzed
                    ]
                    
                    for mention in recent_mentions:
                        await self._analyze_mention_sentiment(mention)
                    
                    await asyncio.sleep(300)  # Check every 5 minutes
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Sentiment analysis task error: {str(e)}")
                    await asyncio.sleep(60)
                    
        except Exception as e:
            logger.error(f"Continuous sentiment analysis failed: {str(e)}")

    async def _continuous_alert_monitoring(self) -> None:
        """Continuous alert monitoring task"""



        try:
            while self.monitoring_active:
                try:
                    # Check for volume spikes
                    await self._check_volume_spike_alerts()
                    
                    # Check for sentiment trend alerts
                    await self._check_sentiment_trend_alerts()
                    
                    # Check for reputation drop alerts
                    await self._check_reputation_drop_alerts()
                    
                    await asyncio.sleep(900)  # Check every 15 minutes
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Alert monitoring task error: {str(e)}")
                    await asyncio.sleep(300)
                    
        except Exception as e:
            logger.error(f"Continuous alert monitoring failed: {str(e)}")

    async def _continuous_reputation_calculation(self) -> None:
        """Continuous reputation score calculation task"""



        try:
            while self.monitoring_active:
                try:
                    # Calculate hourly reputation metrics
                    await self._calculate_hourly_reputation()
                    
                    # Calculate daily reputation metrics
                    await self._calculate_daily_reputation()
                    
                    await asyncio.sleep(3600)  # Calculate every hour
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Reputation calculation task error: {str(e)}")
                    await asyncio.sleep(300)
                    
        except Exception as e:
            logger.error(f"Continuous reputation calculation failed: {str(e)}")

    async def get_reputation_metrics(self, time_period: str = "24h") -> ReputationMetrics:
        """Get current reputation metrics"""



        try:
            cutoff_time = self._get_cutoff_time(time_period)
            relevant_mentions = [
                m for m in self.mentions
                if m.discovered_at >= cutoff_time
            ]
            
            if not relevant_mentions:
                return ReputationMetrics(
                    brand_id=self.brand_id,
                    time_period=time_period
                )
            
            # Calculate metrics
            total_mentions = len(relevant_mentions)
            positive_mentions = len([m for m in relevant_mentions if m.sentiment_score > 0.1])
            negative_mentions = len([m for m in relevant_mentions if m.sentiment_score < -0.1])
            neutral_mentions = total_mentions - positive_mentions - negative_mentions
            
            average_sentiment = sum(m.sentiment_score for m in relevant_mentions) / total_mentions
            reach_total = sum(m.reach_estimate for m in relevant_mentions)
            engagement_total = sum(
                sum(m.engagement_metrics.values()) if isinstance(m.engagement_metrics, dict) else 0
                for m in relevant_mentions
            )
            
            # Calculate reputation score (0-1)
            reputation_score = self._calculate_reputation_score(relevant_mentions)
            
            # Get top keywords and platforms
            top_keywords = self._get_top_keywords(relevant_mentions)
            top_platforms = self._get_top_platforms(relevant_mentions)
            
            # Detect crisis indicators
            crisis_indicators = await self._detect_crisis_indicators(relevant_mentions)
            
            return ReputationMetrics(
                brand_id=self.brand_id,
                time_period=time_period,
                total_mentions=total_mentions,
                positive_mentions=positive_mentions,
                negative_mentions=negative_mentions,
                neutral_mentions=neutral_mentions,
                average_sentiment=average_sentiment,
                reach_total=reach_total,
                engagement_total=engagement_total,
                reputation_score=reputation_score,
                top_keywords=top_keywords,
                top_platforms=top_platforms,
                crisis_indicators=crisis_indicators
            )
            
        except Exception as e:
            logger.error(f"Reputation metrics calculation failed: {str(e)}")
            return ReputationMetrics(brand_id=self.brand_id, time_period=time_period)

    def _get_cutoff_time(self, time_period: str) -> datetime:
        """Get cutoff time for time period"""
        now = datetime.utcnow()
        
        if time_period == "1h":
            return now - timedelta(hours=1)
        elif time_period == "24h":
            return now - timedelta(hours=24)
        elif time_period == "7d":
            return now - timedelta(days=7)
        elif time_period == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default to 24h

    def _calculate_reputation_score(self, mentions: List[BrandMention]) -> float:
        """Calculate overall reputation score"""
        if not mentions:
            return 0.5  # Neutral score
        
        try:
            # Weighted sentiment calculation
            weighted_sentiment = 0.0
            total_weight = 0.0
            
            for mention in mentions:
                weight = mention.influence_score * mention.credibility_score
                weighted_sentiment += mention.sentiment_score * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.5
            
            avg_weighted_sentiment = weighted_sentiment / total_weight
            
            # Convert sentiment (-1 to 1) to reputation score (0 to 1)
            reputation_score = (avg_weighted_sentiment + 1) / 2
            
            return min(max(reputation_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Reputation score calculation failed: {str(e)}")
            return 0.5

    def _get_top_keywords(self, mentions: List[BrandMention], top_n: int = 10) -> List[str]:
        """Get most frequently mentioned keywords"""



        try:
            all_keywords = []
            for mention in mentions:
                all_keywords.extend(mention.keywords_matched)
            
            # Count keyword frequency
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Return top keywords
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            return [keyword for keyword, count in sorted_keywords[:top_n]]
            
        except Exception as e:
            logger.error(f"Top keywords extraction failed: {str(e)}")
            return []

    def _get_top_platforms(self, mentions: List[BrandMention], top_n: int = 10) -> List[str]:
        """Get platforms with most mentions"""



        try:
            platform_counts = {}
            for mention in mentions:
                platform_counts[mention.platform] = platform_counts.get(mention.platform, 0) + 1
            
            sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
            return [platform for platform, count in sorted_platforms[:top_n]]
            
        except Exception as e:
            logger.error(f"Top platforms extraction failed: {str(e)}")
            return []

    async def _detect_crisis_indicators(self, mentions: List[BrandMention]) -> List[str]:
        """Detect potential crisis indicators"""
        indicators = []
        
        try:
            # High volume of negative mentions
            negative_mentions = [m for m in mentions if m.sentiment_score <= -0.3]
            if len(negative_mentions) > len(mentions) * 0.4:  # > 40% negative
                indicators.append("high_negative_sentiment_ratio")
            
            # Rapid mention volume increase
            if len(mentions) > 0:
                # This would compare with historical data
                indicators.append("potential_volume_spike")
            
            # Crisis keywords present
            crisis_keywords = self.alert_thresholds.get("crisis_keywords", [])
            for mention in mentions:
                content_lower = mention.content.lower()
                for keyword in crisis_keywords:
                    if keyword in content_lower:
                        indicators.append(f"crisis_keyword_detected:{keyword}")
                        break
            
            # Influential negative mentions
            high_impact_negative = [
                m for m in mentions
                if m.sentiment_score <= -0.5 and m.influence_score >= 0.7
            ]
            if high_impact_negative:
                indicators.append("influential_negative_mentions")
                
        except Exception as e:
            logger.error(f"Crisis indicator detection failed: {str(e)}")
        
        return list(set(indicators))  # Remove duplicates


class ReputationTracker:
    """
    Brand Reputation Tracking & Historical Analysis
    
    Tracks reputation changes over time and provides insights into brand health trends.
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.reputation_history: List[ReputationMetrics] = []
        
        logger.info(f"Reputation tracker initialized for brand: {brand_id}")

    async def track_reputation_change(self, current_metrics: ReputationMetrics, previous_metrics: Optional[ReputationMetrics] = None) -> Dict[str, Any]:
        """Track reputation changes between time periods"""



        try:
            if not previous_metrics:
                # Get previous metrics from history
                if len(self.reputation_history) >= 2:
                    previous_metrics = self.reputation_history[-2]
                else:
                    return {"trend": "insufficient_data"}
            
            # Calculate changes
            reputation_change = current_metrics.reputation_score - previous_metrics.reputation_score
            sentiment_change = current_metrics.average_sentiment - previous_metrics.average_sentiment
            mention_volume_change = current_metrics.total_mentions - previous_metrics.total_mentions
            
            # Determine trend
            trend = self._determine_reputation_trend(reputation_change, sentiment_change)
            
            # Calculate change percentages
            reputation_pct_change = (reputation_change / max(previous_metrics.reputation_score, 0.01)) * 100
            mention_pct_change = (mention_volume_change / max(previous_metrics.total_mentions, 1)) * 100
            
            return {
                "trend": trend,
                "reputation_change": reputation_change,
                "reputation_pct_change": reputation_pct_change,
                "sentiment_change": sentiment_change,
                "mention_volume_change": mention_volume_change,
                "mention_pct_change": mention_pct_change,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reputation change tracking failed: {str(e)}")
            return {"trend": "error", "error": str(e)}

    def _determine_reputation_trend(self, reputation_change: float, sentiment_change: float) -> str:
        """Determine overall reputation trend"""
        if reputation_change > 0.05 and sentiment_change > 0.1:
            return "strongly_improving"
        elif reputation_change > 0.02 or sentiment_change > 0.05:
            return "improving"
        elif abs(reputation_change) <= 0.02 and abs(sentiment_change) <= 0.05:
            return "stable"
        elif reputation_change < -0.02 or sentiment_change < -0.05:
            return "declining"
        elif reputation_change < -0.05 and sentiment_change < -0.1:
            return "strongly_declining"
        else:
            return "stable"

    async def generate_reputation_report(self, time_period: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive reputation analysis report"""



        try:
            if not self.reputation_history:
                return {"error": "No reputation data available"}
            
            # Get metrics for the time period
            cutoff_time = datetime.utcnow() - timedelta(days=30 if time_period == "30d" else 7)
            relevant_metrics = [
                m for m in self.reputation_history
                if m.generated_at >= cutoff_time
            ]
            
            if not relevant_metrics:
                return {"error": "No data for specified time period"}
            
            # Calculate report data
            report = {
                "brand_id": self.brand_id,
                "time_period": time_period,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": await self._generate_reputation_summary(relevant_metrics),
                "trends": await self._analyze_reputation_trends(relevant_metrics),
                "top_insights": await self._generate_reputation_insights(relevant_metrics),
                "recommendations": await self._generate_reputation_recommendations(relevant_metrics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Reputation report generation failed: {str(e)}")
            return {"error": str(e)}

    async def _generate_reputation_summary(self, metrics: List[ReputationMetrics]) -> Dict[str, Any]:
        """Generate reputation summary statistics"""
        if not metrics:
            return {}
        
        latest = metrics[-1]
        earliest = metrics[0]
        
        return {
            "current_reputation_score": latest.reputation_score,
            "reputation_change": latest.reputation_score - earliest.reputation_score,
            "average_sentiment": latest.average_sentiment,
            "total_mentions_period": sum(m.total_mentions for m in metrics),
            "average_mentions_per_day": sum(m.total_mentions for m in metrics) / len(metrics),
            "positive_mention_ratio": latest.positive_mentions / max(latest.total_mentions, 1),
            "negative_mention_ratio": latest.negative_mentions / max(latest.total_mentions, 1),
            "total_reach": sum(m.reach_total for m in metrics),
            "crisis_incidents": sum(1 for m in metrics if m.crisis_indicators)
        }

    async def _analyze_reputation_trends(self, metrics: List[ReputationMetrics]) -> Dict[str, Any]:
        """Analyze reputation trends over time"""
        if len(metrics) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Extract time series data
        reputation_scores = [m.reputation_score for m in metrics]
        sentiment_scores = [m.average_sentiment for m in metrics]
        mention_volumes = [m.total_mentions for m in metrics]
        
        return {
            "reputation_trend": self._calculate_trend(reputation_scores),
            "sentiment_trend": self._calculate_trend(sentiment_scores),
            "volume_trend": self._calculate_trend(mention_volumes),
            "volatility": {
                "reputation": np.std(reputation_scores),
                "sentiment": np.std(sentiment_scores),
                "volume": np.std(mention_volumes)
            },
            "peak_reputation": max(reputation_scores),
            "lowest_reputation": min(reputation_scores),
            "peak_mentions": max(mention_volumes)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from time series values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    async def _generate_reputation_insights(self, metrics: List[ReputationMetrics]) -> List[str]:
        """Generate key insights from reputation data"""
        insights = []
        
        try:
            if not metrics:
                return insights
            
            latest = metrics[-1]
            
            # Reputation score insights
            if latest.reputation_score >= 0.8:
                insights.append("Brand maintains excellent reputation with high positive sentiment")
            elif latest.reputation_score >= 0.6:
                insights.append("Brand has good reputation with room for improvement")
            elif latest.reputation_score >= 0.4:
                insights.append("Brand reputation is neutral, requiring attention")
            else:
                insights.append("Brand reputation needs immediate improvement")
            
            # Mention volume insights
            avg_mentions = sum(m.total_mentions for m in metrics) / len(metrics)
            if latest.total_mentions > avg_mentions * 1.5:
                insights.append("Brand mentions significantly above average - monitor for causes")
            elif latest.total_mentions < avg_mentions * 0.5:
                insights.append("Brand mentions below average - may need visibility boost")
            
            # Sentiment insights
            if latest.average_sentiment > 0.3:
                insights.append("Strong positive sentiment across brand mentions")
            elif latest.average_sentiment < -0.3:
                insights.append("Concerning negative sentiment requires immediate attention")
            
            # Platform insights
            if latest.top_platforms:
                top_platform = latest.top_platforms[0]
                insights.append(f"Most active brand discussions occur on {top_platform}")
            
            # Crisis insights
            if latest.crisis_indicators:
                insights.append(f"Active crisis indicators detected: {', '.join(latest.crisis_indicators[:3])}")
                
        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
        
        return insights

    async def _generate_reputation_recommendations(self, metrics: List[ReputationMetrics]) -> List[str]:
        """Generate actionable recommendations for reputation improvement"""
        recommendations = []
        
        try:
            if not metrics:
                return recommendations
            
            latest = metrics[-1]
            
            # Based on reputation score
            if latest.reputation_score < 0.5:
                recommendations.extend([
                    "Implement comprehensive reputation recovery strategy",
                    "Increase positive content creation and engagement",
                    "Address negative mentions proactively with customer service",
                    "Consider PR campaign to improve brand perception"
                ])
            
            # Based on sentiment
            if latest.average_sentiment < -0.2:
                recommendations.extend([
                    "Analyze root causes of negative sentiment",
                    "Improve customer service response times and quality",
                    "Create positive content to balance negative mentions",
                    "Engage directly with dissatisfied customers"
                ])
            
            # Based on mention volume
            avg_mentions = sum(m.total_mentions for m in metrics) / len(metrics)
            if latest.total_mentions < avg_mentions * 0.7:
                recommendations.extend([
                    "Increase brand visibility through marketing campaigns",
                    "Engage more actively on social media platforms",
                    "Create newsworthy content to generate organic mentions"
                ])
            
            # Based on crisis indicators
            if latest.crisis_indicators:
                recommendations.extend([
                    "Activate crisis management protocols",
                    "Issue official statements addressing concerns",
                    "Monitor situation closely with increased frequency",
                    "Prepare legal responses if necessary"
                ])
            
            # Platform-specific recommendations
            if latest.top_platforms:
                for platform in latest.top_platforms[:3]:
                    if platform in ["twitter", "facebook", "instagram"]:
                        recommendations.append(f"Increase engagement and response rate on {platform}")
                        
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
        
        return recommendations
