"""Professional platform analysis system for content monitoring and competitor intelligence.

This module implements specialized analyzers for different content platforms,
providing comprehensive insights into platform-specific metrics, trends,
and content performance analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Platform Analytics Specialist: Multi-Platform Intelligence
- Content Intelligence Engineer: Advanced Metrics & KPIs
- Competitor Analysis Expert: Market Intelligence & Trends
- Business Intelligence Analyst: Strategic Data Insights
- Data Scientist: Predictive Analytics & ML Models

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""
from typing import Dict, Any, List, Optional, Union, Set, Tuple, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from collections import defaultdict, Counter

# HTTP and API clients
import aiohttp
import requests
from urllib.parse import urljoin, urlparse, parse_qs
import jwt

# Data processing and analysis
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# API clients for platforms
import tweepy
from instagrapi import Client as InstagramClient
import yt_dlp
from pytube import YouTube
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Content analysis
import cv2
import numpy as np
from PIL import Image
import imagehash
import librosa
from textblob import TextBlob
from transformers import pipeline

from . import WebCrawler, CrawlResult, CrawlTarget, ContentType, PlatformType
from ..core.exceptions import CrawlerException, ValidationException, PlatformException
from ..core.models import BaseModel
from ..security.encryption import EncryptionManager
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager


class PlatformAnalysisType(Enum):
    """Types of platform analysis."""    COMPETITOR_ANALYSIS = "competitor_analysis"
    TREND_ANALYSIS = "trend_analysis"
    CONTENT_PERFORMANCE = "content_performance"
    AUDIENCE_ANALYSIS = "audience_analysis"
    INFLUENCER_DISCOVERY = "influencer_discovery"
    MARKET_INTELLIGENCE = "market_intelligence"
    BRAND_MONITORING = "brand_monitoring"
    CONTENT_GAP_ANALYSIS = "content_gap_analysis"
    ENGAGEMENT_PATTERNS = "engagement_patterns"
    HASHTAG_ANALYSIS = "hashtag_analysis"


class AnalysisMetrics(Enum):
    """Key metrics for platform analysis."""    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    FOLLOWER_GROWTH = "follower_growth"
    CONTENT_FREQUENCY = "content_frequency"
    OPTIMAL_POSTING_TIME = "optimal_posting_time"
    HASHTAG_PERFORMANCE = "hashtag_performance"
    AUDIENCE_DEMOGRAPHICS = "audience_demographics"
    CONTENT_VIRALITY = "content_virality"
    SHARE_OF_VOICE = "share_of_voice"


class CompetitorTier(Enum):
    """Competitor classification tiers."""    DIRECT_COMPETITOR = "direct_competitor"
    INDIRECT_COMPETITOR = "indirect_competitor"
    MARKET_LEADER = "market_leader"
    EMERGING_PLAYER = "emerging_player"
    NICHE_SPECIALIST = "niche_specialist"
    INDUSTRY_INFLUENCER = "industry_influencer"


@dataclass
class PlatformMetrics:
    """Platform-specific metrics collection."""    platform: str
    account_id: str
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    engagement_rate: float = 0.0
    avg_likes: float = 0.0
    avg_comments: float = 0.0
    avg_shares: float = 0.0
    reach: int = 0
    impressions: int = 0
    video_views: int = 0
    story_views: int = 0
    profile_visits: int = 0
    website_clicks: int = 0
    growth_rate: float = 0.0
    posting_frequency: float = 0.0
    optimal_posting_times: List[str] = field(default_factory=list)
    top_hashtags: List[str] = field(default_factory=list)
    content_types: Dict[str, int] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, float] = field(default_factory=dict)
    performance_trend: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile."""    competitor_id: str
    name: str
    tier: CompetitorTier
    platforms: Dict[str, PlatformMetrics] = field(default_factory=dict)
    content_strategy: Dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    market_position: str = ""
    estimated_revenue: float = 0.0
    brand_collaborations: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    posting_patterns: Dict[str, Any] = field(default_factory=dict)
    audience_overlap: float = 0.0
    competitive_score: float = 0.0
    last_analyzed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendAnalysis:
    """Trend analysis results."""    trend_id: str
    trend_name: str
    platform: str
    category: str
    current_volume: int = 0
    growth_rate: float = 0.0
    engagement_rate: float = 0.0
    sentiment_score: float = 0.0
    geographic_spread: Dict[str, float] = field(default_factory=dict)
    key_influencers: List[str] = field(default_factory=list)
    related_hashtags: List[str] = field(default_factory=list)
    content_types: Dict[str, int] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    longevity_score: float = 0.0
    commercial_potential: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    opportunity_score: float = 0.0
    time_series_data: List[Dict[str, Any]] = field(default_factory=list)
    predictions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class PlatformAnalyzer:
    """    Advanced platform analysis engine for competitive intelligence.
    
    Provides comprehensive analysis capabilities including:
    - Multi-platform competitor monitoring
    - Trend detection and analysis
    - Content performance optimization
    - Audience insights and demographics
    - Market intelligence and opportunities
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("analyzer.platform")
        
        # Core components
        self.rate_limiter = RateLimiter(config.get("rate_limits", {}))
        self.cache_manager = CacheManager(config.get("cache_config", {}))
        self.encryption_manager = EncryptionManager()
        
        # Analysis settings
        self.analysis_depth = config.get("analysis_depth", "comprehensive")
        self.data_retention_days = config.get("data_retention_days", 30)
        self.min_confidence_score = config.get("min_confidence_score", 0.7)
        
        # Platform clients
        self._setup_platform_clients()
        
        # ML models
        self._setup_ml_models()
        
        # Analytics cache
        self.metrics_cache: Dict[str, PlatformMetrics] = {}
        self.competitor_profiles: Dict[str, CompetitorProfile] = {}
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        
    def _setup_platform_clients(self):
        """Setup platform API clients."""        try:
            # Instagram client
            if self.config.get("instagram_credentials"):
                self.instagram_client = InstagramClient()
                # Configure authentication
            
            # Twitter client
            if self.config.get("twitter_credentials"):
                auth = tweepy.OAuthHandler(
                    self.config["twitter_credentials"]["api_key"],
                    self.config["twitter_credentials"]["api_secret"]
                )
                auth.set_access_token(
                    self.config["twitter_credentials"]["access_token"],
                    self.config["twitter_credentials"]["access_secret"]
                )
                self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
            
            # YouTube client
            self.youtube_client = yt_dlp.YoutubeDL({
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            })
            
            # Spotify client
            if self.config.get("spotify_credentials"):
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.config["spotify_credentials"]["client_id"],
                    client_secret=self.config["spotify_credentials"]["client_secret"]
                )
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
            
            self.logger.info("Platform clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize platform clients: {e}")
            raise PlatformException(f"Platform client setup failed: {e}")
    
    def _setup_ml_models(self):
        """Setup machine learning models for analysis."""        try:
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Content classification
            self.content_classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Trend detection model
            self.trend_detector = KMeans(n_clusters=10, random_state=42)
            
            self.logger.info("ML models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load ML models: {e}")
            # Continue without ML models
    
    async def analyze_competitor(
        self,
        competitor_id: str,
        platforms: List[str],
        analysis_type: PlatformAnalysisType = PlatformAnalysisType.COMPETITOR_ANALYSIS
    ) -> CompetitorProfile:
        """        Comprehensive competitor analysis across platforms.
        
        Args:
            competitor_id: Unique competitor identifier
            platforms: List of platforms to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            CompetitorProfile: Complete competitor analysis
        """        try:
            self.logger.info(f"Starting competitor analysis: {competitor_id}")
            
            # Check cache first
            cache_key = f"competitor_{competitor_id}_{hash(tuple(platforms))}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result and self._is_fresh_analysis(cached_result):
                return CompetitorProfile(**cached_result)
            
            # Initialize competitor profile
            profile = CompetitorProfile(
                competitor_id=competitor_id,
                name=competitor_id,  # Will be updated with actual name
                tier=CompetitorTier.DIRECT_COMPETITOR
            )
            
            # Analyze each platform
            analysis_tasks = []
            for platform in platforms:
                task = self._analyze_platform_competitor(competitor_id, platform)
                analysis_tasks.append(task)
            
            # Execute platform analyses concurrently
            platform_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(platform_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Platform analysis failed for {platforms[i]}: {result}")
                    continue
                
                if result:
                    profile.platforms[platforms[i]] = result
            
            # Perform cross-platform analysis
            await self._cross_platform_analysis(profile)
            
            # Calculate competitive metrics
            profile.competitive_score = self._calculate_competitive_score(profile)
            profile.market_position = self._determine_market_position(profile)
            
            # Generate insights
            profile.strengths = self._identify_strengths(profile)
            profile.weaknesses = self._identify_weaknesses(profile)
            profile.opportunities = self._identify_opportunities(profile)
            profile.threats = self._identify_threats(profile)
            
            # Cache results
            await self.cache_manager.set(
                cache_key,
                profile.__dict__,
                ttl=3600  # 1 hour cache
            )
            
            # Store in memory cache
            self.competitor_profiles[competitor_id] = profile
            
            self.logger.info(f"Competitor analysis completed: {competitor_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Competitor analysis failed: {e}")
            raise CrawlerException(f"Failed to analyze competitor {competitor_id}: {e}")
    
    async def _analyze_platform_competitor(
        self,
        competitor_id: str,
        platform: str
    ) -> Optional[PlatformMetrics]:
        """Analyze competitor on specific platform."""        try:
            if platform == "instagram":
                return await self._analyze_instagram_competitor(competitor_id)
            elif platform == "twitter":
                return await self._analyze_twitter_competitor(competitor_id)
            elif platform == "youtube":
                return await self._analyze_youtube_competitor(competitor_id)
            elif platform == "tiktok":
                return await self._analyze_tiktok_competitor(competitor_id)
            elif platform == "spotify":
                return await self._analyze_spotify_competitor(competitor_id)
            else:
                self.logger.warning(f"Unsupported platform: {platform}")
                return None
                
        except Exception as e:
            self.logger.error(f"Platform analysis failed for {platform}: {e}")
            return None
    
    async def _analyze_instagram_competitor(self, competitor_id: str) -> PlatformMetrics:
        """Analyze Instagram competitor metrics."""        try:
            # Rate limiting
            await self.rate_limiter.acquire("instagram")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(competitor_id)
            
            # Get recent posts
            posts = self.instagram_client.user_medias(user_info.pk, amount=50)
            
            # Calculate metrics
            metrics = PlatformMetrics(
                platform="instagram",
                account_id=competitor_id,
                followers_count=user_info.follower_count,
                following_count=user_info.following_count,
                posts_count=user_info.media_count
            )
            
            # Analyze posts for engagement metrics
            if posts:
                likes = [post.like_count for post in posts if post.like_count]
                comments = [post.comment_count for post in posts if post.comment_count]
                
                metrics.avg_likes = statistics.mean(likes) if likes else 0
                metrics.avg_comments = statistics.mean(comments) if comments else 0
                metrics.engagement_rate = self._calculate_engagement_rate(
                    metrics.avg_likes + metrics.avg_comments,
                    metrics.followers_count
                )
                
                # Content type analysis
                content_types = defaultdict(int)
                for post in posts:
                    if post.media_type == 1:  # Image
                        content_types["image"] += 1
                    elif post.media_type == 2:  # Video
                        content_types["video"] += 1
                    elif post.media_type == 8:  # Carousel
                        content_types["carousel"] += 1
                
                metrics.content_types = dict(content_types)
                
                # Hashtag analysis
                hashtags = []
                for post in posts:
                    if post.caption_text:
                        hashtags.extend(re.findall(r'#\w+', post.caption_text))
                
                metrics.top_hashtags = [tag for tag, count in Counter(hashtags).most_common(10)]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Instagram analysis failed for {competitor_id}: {e}")
            return None
    
    async def _analyze_twitter_competitor(self, competitor_id: str) -> PlatformMetrics:
        """Analyze Twitter competitor metrics."""        try:
            # Rate limiting
            await self.rate_limiter.acquire("twitter")
            
            # Get user info
            user = self.twitter_client.get_user(screen_name=competitor_id)
            
            # Get recent tweets
            tweets = self.twitter_client.user_timeline(
                screen_name=competitor_id,
                count=200,
                include_rts=False,
                exclude_replies=True
            )
            
            # Calculate metrics
            metrics = PlatformMetrics(
                platform="twitter",
                account_id=competitor_id,
                followers_count=user.followers_count,
                following_count=user.friends_count,
                posts_count=user.statuses_count
            )
            
            # Analyze tweets for engagement
            if tweets:
                likes = [tweet.favorite_count for tweet in tweets]
                retweets = [tweet.retweet_count for tweet in tweets]
                replies = [tweet.reply_count for tweet in tweets if hasattr(tweet, 'reply_count')]
                
                metrics.avg_likes = statistics.mean(likes) if likes else 0
                metrics.avg_shares = statistics.mean(retweets) if retweets else 0
                metrics.avg_comments = statistics.mean(replies) if replies else 0
                
                metrics.engagement_rate = self._calculate_engagement_rate(
                    metrics.avg_likes + metrics.avg_shares + metrics.avg_comments,
                    metrics.followers_count
                )
                
                # Hashtag analysis
                hashtags = []
                for tweet in tweets:
                    hashtags.extend([tag['text'] for tag in tweet.entities['hashtags']])
                
                metrics.top_hashtags = [f"#{tag}" for tag, count in Counter(hashtags).most_common(10)]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Twitter analysis failed for {competitor_id}: {e}")
            return None
    
    async def _analyze_youtube_competitor(self, competitor_id: str) -> PlatformMetrics:
        """Analyze YouTube competitor metrics."""        try:
            # Rate limiting
            await self.rate_limiter.acquire("youtube")
            
            # Extract channel info
            channel_url = f"https://www.youtube.com/@{competitor_id}"
            channel_info = self.youtube_client.extract_info(
                channel_url,
                download=False
            )
            
            # Get recent videos
            videos = channel_info.get('entries', [])[:50] if channel_info else []
            
            # Calculate metrics
            metrics = PlatformMetrics(
                platform="youtube",
                account_id=competitor_id,
                followers_count=channel_info.get('subscriber_count', 0) if channel_info else 0,
                posts_count=len(videos)
            )
            
            # Analyze videos for engagement
            if videos:
                views = [video.get('view_count', 0) for video in videos if video.get('view_count')]
                likes = [video.get('like_count', 0) for video in videos if video.get('like_count')]
                comments = [video.get('comment_count', 0) for video in videos if video.get('comment_count')]
                
                metrics.video_views = sum(views) if views else 0
                metrics.avg_likes = statistics.mean(likes) if likes else 0
                metrics.avg_comments = statistics.mean(comments) if comments else 0
                
                if metrics.followers_count > 0:
                    metrics.engagement_rate = self._calculate_engagement_rate(
                        metrics.avg_likes + metrics.avg_comments,
                        metrics.followers_count
                    )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"YouTube analysis failed for {competitor_id}: {e}")
            return None
    
    async def _analyze_tiktok_competitor(self, competitor_id: str) -> PlatformMetrics:
        """Analyze TikTok competitor metrics using web scraping."""        try:
            # Rate limiting
            await self.rate_limiter.acquire("tiktok")
            
            # Use web scraping for TikTok (no official API)
            url = f"https://www.tiktok.com/@{competitor_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    html_content = await response.text()
            
            # Parse TikTok profile data from HTML (simplified)
            metrics = PlatformMetrics(
                platform="tiktok",
                account_id=competitor_id
            )
            
            # Extract follower count from HTML
            follower_match = re.search(r'"followerCount":(\d+)', html_content)
            if follower_match:
                metrics.followers_count = int(follower_match.group(1))
            
            # Extract following count
            following_match = re.search(r'"followingCount":(\d+)', html_content)
            if following_match:
                metrics.following_count = int(following_match.group(1))
            
            # Extract video count
            video_match = re.search(r'"videoCount":(\d+)', html_content)
            if video_match:
                metrics.posts_count = int(video_match.group(1))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"TikTok analysis failed for {competitor_id}: {e}")
            return None
    
    async def _analyze_spotify_competitor(self, competitor_id: str) -> PlatformMetrics:
        """Analyze Spotify artist metrics."""        try:
            # Rate limiting
            await self.rate_limiter.acquire("spotify")
            
            # Search for artist
            results = self.spotify_client.search(q=competitor_id, type='artist', limit=1)
            
            if not results['artists']['items']:
                return None
            
            artist = results['artists']['items'][0]
            
            # Get artist's albums and tracks
            albums = self.spotify_client.artist_albums(
                artist['id'],
                album_type='album,single',
                limit=50
            )
            
            # Get top tracks
            top_tracks = self.spotify_client.artist_top_tracks(artist['id'])
            
            # Calculate metrics
            metrics = PlatformMetrics(
                platform="spotify",
                account_id=competitor_id,
                followers_count=artist['followers']['total'],
                posts_count=albums['total']
            )
            
            # Analyze track popularity
            if top_tracks['tracks']:
                popularities = [track['popularity'] for track in top_tracks['tracks']]
                metrics.avg_likes = statistics.mean(popularities) if popularities else 0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Spotify analysis failed for {competitor_id}: {e}")
            return None
    
    def _calculate_engagement_rate(self, total_engagement: float, followers: int) -> float:
        """Calculate engagement rate percentage."""        if followers == 0:
            return 0.0
        return (total_engagement / followers) * 100
    
    async def _cross_platform_analysis(self, profile: CompetitorProfile):
        """Perform cross-platform analysis for competitor."""        try:
            # Calculate total reach across platforms
            total_followers = sum(
                metrics.followers_count for metrics in profile.platforms.values()
            )
            
            # Calculate average engagement rate
            engagement_rates = [
                metrics.engagement_rate for metrics in profile.platforms.values()
                if metrics.engagement_rate > 0
            ]
            avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0
            
            # Identify strongest platforms
            best_platform = max(
                profile.platforms.items(),
                key=lambda x: x[1].followers_count,
                default=("", None)
            )
            
            # Content strategy analysis
            all_hashtags = []
            content_types = defaultdict(int)
            
            for metrics in profile.platforms.values():
                all_hashtags.extend(metrics.top_hashtags)
                for content_type, count in metrics.content_types.items():
                    content_types[content_type] += count
            
            # Update profile with cross-platform insights
            profile.content_strategy = {
                "total_followers": total_followers,
                "avg_engagement_rate": avg_engagement,
                "strongest_platform": best_platform[0],
                "common_hashtags": [tag for tag, count in Counter(all_hashtags).most_common(10)],
                "content_distribution": dict(content_types)
            }
            
        except Exception as e:
            self.logger.error(f"Cross-platform analysis failed: {e}")
    
    def _calculate_competitive_score(self, profile: CompetitorProfile) -> float:
        """Calculate overall competitive score."""        try:
            score = 0.0
            total_weight = 0.0
            
            # Follower count score (30% weight)
            follower_weight = 0.3
            max_followers = max(
                (metrics.followers_count for metrics in profile.platforms.values()),
                default=1
            )
            follower_score = min(max_followers / 1000000, 1.0)  # Normalize to 1M followers
            score += follower_score * follower_weight
            total_weight += follower_weight
            
            # Engagement rate score (40% weight)
            engagement_weight = 0.4
            engagement_rates = [
                metrics.engagement_rate for metrics in profile.platforms.values()
                if metrics.engagement_rate > 0
            ]
            if engagement_rates:
                avg_engagement = statistics.mean(engagement_rates)
                engagement_score = min(avg_engagement / 10.0, 1.0)  # Normalize to 10% engagement
                score += engagement_score * engagement_weight
                total_weight += engagement_weight
            
            # Platform presence score (20% weight)
            presence_weight = 0.2
            platform_count = len(profile.platforms)
            presence_score = min(platform_count / 5.0, 1.0)  # Normalize to 5 platforms
            score += presence_score * presence_weight
            total_weight += presence_weight
            
            # Content consistency score (10% weight)
            consistency_weight = 0.1
            posting_frequencies = [
                metrics.posting_frequency for metrics in profile.platforms.values()
                if metrics.posting_frequency > 0
            ]
            if posting_frequencies:
                consistency_score = min(statistics.mean(posting_frequencies) / 7.0, 1.0)  # Daily posting
                score += consistency_score * consistency_weight
                total_weight += consistency_weight
            
            return (score / total_weight) * 100 if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Competitive score calculation failed: {e}")
            return 0.0
    
    def _determine_market_position(self, profile: CompetitorProfile) -> str:
        """Determine competitor's market position."""        try:
            score = profile.competitive_score
            
            if score >= 90:
                return "Market Leader"
            elif score >= 75:
                return "Strong Competitor"
            elif score >= 60:
                return "Established Player"
            elif score >= 45:
                return "Emerging Competitor"
            elif score >= 30:
                return "Niche Player"
            else:
                return "Startup/New Entrant"
                
        except Exception as e:
            self.logger.error(f"Market position determination failed: {e}")
            return "Unknown"
    
    def _identify_strengths(self, profile: CompetitorProfile) -> List[str]:
        """Identify competitor strengths."""        strengths = []
        
        try:
            # High engagement rate
            high_engagement_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.engagement_rate > 5.0
            ]
            if high_engagement_platforms:
                strengths.append(f"High engagement on {', '.join(high_engagement_platforms)}")
            
            # Large follower base
            large_following_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.followers_count > 100000
            ]
            if large_following_platforms:
                strengths.append(f"Large following on {', '.join(large_following_platforms)}")
            
            # Multi-platform presence
            if len(profile.platforms) >= 4:
                strengths.append("Strong multi-platform presence")
            
            # Consistent content creation
            consistent_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.posting_frequency > 3
            ]
            if consistent_platforms:
                strengths.append("Consistent content creation strategy")
            
        except Exception as e:
            self.logger.error(f"Strength identification failed: {e}")
        
        return strengths
    
    def _identify_weaknesses(self, profile: CompetitorProfile) -> List[str]:
        """Identify competitor weaknesses."""        weaknesses = []
        
        try:
            # Low engagement rate
            low_engagement_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.engagement_rate < 1.0
            ]
            if low_engagement_platforms:
                weaknesses.append(f"Low engagement on {', '.join(low_engagement_platforms)}")
            
            # Limited platform presence
            if len(profile.platforms) < 3:
                weaknesses.append("Limited platform presence")
            
            # Inconsistent posting
            inconsistent_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.posting_frequency < 1
            ]
            if inconsistent_platforms:
                weaknesses.append("Inconsistent posting schedule")
            
            # Imbalanced follower distribution
            follower_counts = [metrics.followers_count for metrics in profile.platforms.values()]
            if follower_counts and max(follower_counts) > 10 * min(follower_counts):
                weaknesses.append("Imbalanced audience across platforms")
            
        except Exception as e:
            self.logger.error(f"Weakness identification failed: {e}")
        
        return weaknesses
    
    def _identify_opportunities(self, profile: CompetitorProfile) -> List[str]:
        """Identify market opportunities."""        opportunities = []
        
        try:
            # Underutilized platforms
            major_platforms = {"instagram", "twitter", "youtube", "tiktok", "spotify"}
            missing_platforms = major_platforms - set(profile.platforms.keys())
            if missing_platforms:
                opportunities.append(f"Expand to {', '.join(missing_platforms)}")
            
            # Content gaps
            content_types = set()
            for metrics in profile.platforms.values():
                content_types.update(metrics.content_types.keys())
            
            all_content_types = {"image", "video", "carousel", "story", "reels", "live"}
            missing_content = all_content_types - content_types
            if missing_content:
                opportunities.append(f"Explore {', '.join(missing_content)} content")
            
            # Audience growth potential
            growth_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.growth_rate > 0 and metrics.followers_count < 50000
            ]
            if growth_platforms:
                opportunities.append(f"High growth potential on {', '.join(growth_platforms)}")
            
        except Exception as e:
            self.logger.error(f"Opportunity identification failed: {e}")
        
        return opportunities
    
    def _identify_threats(self, profile: CompetitorProfile) -> List[str]:
        """Identify competitive threats."""        threats = []
        
        try:
            # Declining engagement
            declining_platforms = [
                platform for platform, metrics in profile.platforms.items()
                if metrics.growth_rate < -5.0
            ]
            if declining_platforms:
                threats.append(f"Declining performance on {', '.join(declining_platforms)}")
            
            # High competition keywords
            common_hashtags = profile.content_strategy.get("common_hashtags", [])
            competitive_hashtags = [tag for tag in common_hashtags if len(tag) < 20]  # Generic tags
            if len(competitive_hashtags) > 5:
                threats.append("Heavy reliance on highly competitive hashtags")
            
            # Platform dependency
            if len(profile.platforms) == 1:
                threats.append("Over-dependence on single platform")
            
        except Exception as e:
            self.logger.error(f"Threat identification failed: {e}")
        
        return threats
    
    def _is_fresh_analysis(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached analysis is still fresh."""        try:
            last_analyzed = datetime.fromisoformat(cached_data.get("last_analyzed", ""))
            return (datetime.utcnow() - last_analyzed).total_seconds() < 3600  # 1 hour
        except:
            return False
    
    async def analyze_trends(
        self,
        platform: str,
        category: str,
        region: str = "global"
    ) -> List[TrendAnalysis]:
        """        Analyze trending topics and content for a platform and category.
        
        Args:
            platform: Target platform (instagram, twitter, tiktok, etc.)
            category: Content category (music, fashion, tech, etc.)
            region: Geographic region for trends
            
        Returns:
            List[TrendAnalysis]: Trending content analysis
        """        try:
            self.logger.info(f"Analyzing trends for {platform} in {category}")
            
            # Check cache
            cache_key = f"trends_{platform}_{category}_{region}"
            cached_trends = await self.cache_manager.get(cache_key)
            if cached_trends:
                return [TrendAnalysis(**trend) for trend in cached_trends]
            
            trends = []
            
            if platform == "twitter":
                trends = await self._analyze_twitter_trends(category, region)
            elif platform == "instagram":
                trends = await self._analyze_instagram_trends(category, region)
            elif platform == "youtube":
                trends = await self._analyze_youtube_trends(category, region)
            elif platform == "tiktok":
                trends = await self._analyze_tiktok_trends(category, region)
            
            # Cache results
            await self.cache_manager.set(
                cache_key,
                [trend.__dict__ for trend in trends],
                ttl=1800  # 30 minutes cache
            )
            
            self.logger.info(f"Found {len(trends)} trends for {platform}")
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            raise CrawlerException(f"Failed to analyze trends for {platform}: {e}")
    
    async def _analyze_twitter_trends(self, category: str, region: str) -> List[TrendAnalysis]:
        """Analyze Twitter trends."""        trends = []
        
        try:
            # Get trending topics
            woeid = 1 if region == "global" else 1  # World-wide or specific location
            trending = self.twitter_client.get_place_trends(woeid)[0]['trends']
            
            for trend_data in trending[:10]:  # Top 10 trends
                trend = TrendAnalysis(
                    trend_id=str(hash(trend_data['name'])),
                    trend_name=trend_data['name'],
                    platform="twitter",
                    category=category,
                    current_volume=trend_data.get('tweet_volume', 0) or 0
                )
                
                # Get sentiment analysis
                if hasattr(self, 'sentiment_analyzer'):
                    sentiment = self.sentiment_analyzer(trend_data['name'])
                    trend.sentiment_score = sentiment[0]['score'] if sentiment else 0.5
                
                trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Twitter trends analysis failed: {e}")
        
        return trends
    
    async def _analyze_instagram_trends(self, category: str, region: str) -> List[TrendAnalysis]:
        """Analyze Instagram trends using hashtag popularity."""        trends = []
        
        try:
            # Popular hashtags by category
            category_hashtags = {
                "music": ["music", "song", "artist", "concert", "album"],
                "fashion": ["fashion", "style", "outfit", "trend", "clothing"],
                "tech": ["tech", "technology", "innovation", "gadget", "ai"],
                "fitness": ["fitness", "workout", "health", "gym", "exercise"]
            }
            
            hashtags = category_hashtags.get(category, ["trending", "popular"])
            
            for hashtag in hashtags:
                try:
                    # Get hashtag info
                    hashtag_info = self.instagram_client.hashtag_info(hashtag)
                    
                    trend = TrendAnalysis(
                        trend_id=f"ig_{hashtag}",
                        trend_name=f"#{hashtag}",
                        platform="instagram",
                        category=category,
                        current_volume=hashtag_info.media_count
                    )
                    
                    trends.append(trend)
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze hashtag {hashtag}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Instagram trends analysis failed: {e}")
        
        return trends
    
    async def _analyze_youtube_trends(self, category: str, region: str) -> List[TrendAnalysis]:
        """Analyze YouTube trending videos."""        trends = []
        
        try:
            # Get trending videos by category
            trending_url = f"https://www.youtube.com/feed/trending"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(trending_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse trending video titles (simplified)
                        video_titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', content)
                        
                        for i, title in enumerate(video_titles[:10]):
                            trend = TrendAnalysis(
                                trend_id=f"yt_{i}_{hash(title)}",
                                trend_name=title,
                                platform="youtube",
                                category=category,
                                current_volume=1000  # Placeholder
                            )
                            trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"YouTube trends analysis failed: {e}")
        
        return trends
    
    async def _analyze_tiktok_trends(self, category: str, region: str) -> List[TrendAnalysis]:
        """Analyze TikTok trends using web scraping."""        trends = []
        
        try:
            # TikTok discover page
            discover_url = "https://www.tiktok.com/discover"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(discover_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse trending hashtags
                        hashtags = re.findall(r'#(\w+)', content)
                        hashtag_counts = Counter(hashtags)
                        
                        for hashtag, count in hashtag_counts.most_common(10):
                            trend = TrendAnalysis(
                                trend_id=f"tt_{hashtag}",
                                trend_name=f"#{hashtag}",
                                platform="tiktok",
                                category=category,
                                current_volume=count
                            )
                            trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"TikTok trends analysis failed: {e}")
        
        return trends
    
    async def generate_insights_report(
        self,
        competitor_ids: List[str],
        analysis_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """        Generate comprehensive insights report.
        
        Args:
            competitor_ids: List of competitor IDs to analyze
            analysis_period: Time period for analysis
            
        Returns:
            Dict containing comprehensive insights and recommendations
        """        try:
            self.logger.info("Generating comprehensive insights report")
            
            report = {
                "summary": {},
                "competitors": {},
                "market_analysis": {},
                "opportunities": [],
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Analyze all competitors
            competitor_profiles = []
            for competitor_id in competitor_ids:
                platforms = ["instagram", "twitter", "youtube", "tiktok", "spotify"]
                profile = await self.analyze_competitor(
                    competitor_id,
                    platforms,
                    PlatformAnalysisType.COMPETITOR_ANALYSIS
                )
                competitor_profiles.append(profile)
                report["competitors"][competitor_id] = profile.__dict__
            
            # Market analysis
            report["market_analysis"] = self._generate_market_analysis(competitor_profiles)
            
            # Identify opportunities
            report["opportunities"] = self._identify_market_opportunities(competitor_profiles)
            
            # Generate recommendations
            report["recommendations"] = self._generate_strategic_recommendations(competitor_profiles)
            
            # Executive summary
            report["summary"] = {
                "total_competitors": len(competitor_profiles),
                "average_competitive_score": statistics.mean([
                    p.competitive_score for p in competitor_profiles
                ]),
                "most_competitive_platform": self._identify_most_competitive_platform(competitor_profiles),
                "key_insights": self._extract_key_insights(competitor_profiles)
            }
            
            self.logger.info("Insights report generated successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Insights report generation failed: {e}")
            raise CrawlerException(f"Failed to generate insights report: {e}")
    
    def _generate_market_analysis(self, profiles: List[CompetitorProfile]) -> Dict[str, Any]:
        """Generate market analysis from competitor profiles."""        analysis = {
            "market_size": 0,
            "competition_level": "medium",
            "growth_potential": "medium",
            "platform_dominance": {},
            "content_trends": {},
            "engagement_benchmarks": {}
        }
        
        try:
            # Calculate total market size
            all_followers = []
            platform_followers = defaultdict(list)
            
            for profile in profiles:
                for platform, metrics in profile.platforms.items():
                    all_followers.append(metrics.followers_count)
                    platform_followers[platform].append(metrics.followers_count)
            
            analysis["market_size"] = sum(all_followers)
            
            # Platform dominance
            for platform, followers in platform_followers.items():
                analysis["platform_dominance"][platform] = {
                    "total_followers": sum(followers),
                    "average_followers": statistics.mean(followers),
                    "top_competitor_followers": max(followers) if followers else 0
                }
            
            # Competition level assessment
            competitive_scores = [p.competitive_score for p in profiles]
            avg_score = statistics.mean(competitive_scores) if competitive_scores else 0
            
            if avg_score > 75:
                analysis["competition_level"] = "high"
            elif avg_score > 50:
                analysis["competition_level"] = "medium"
            else:
                analysis["competition_level"] = "low"
            
            # Engagement benchmarks
            platform_engagement = defaultdict(list)
            for profile in profiles:
                for platform, metrics in profile.platforms.items():
                    if metrics.engagement_rate > 0:
                        platform_engagement[platform].append(metrics.engagement_rate)
            
            for platform, rates in platform_engagement.items():
                if rates:
                    analysis["engagement_benchmarks"][platform] = {
                        "average": statistics.mean(rates),
                        "median": statistics.median(rates),
                        "top_quartile": np.percentile(rates, 75)
                    }
            
        except Exception as e:
            self.logger.error(f"Market analysis generation failed: {e}")
        
        return analysis
    
    def _identify_market_opportunities(self, profiles: List[CompetitorProfile]) -> List[str]:
        """Identify market opportunities from competitor analysis."""        opportunities = []
        
        try:
            # Underutilized platforms
            all_platforms = set()
            platform_usage = defaultdict(int)
            
            for profile in profiles:
                all_platforms.update(profile.platforms.keys())
                for platform in profile.platforms.keys():
                    platform_usage[platform] += 1
            
            major_platforms = {"instagram", "twitter", "youtube", "tiktok", "spotify"}
            underused = major_platforms - all_platforms
            if underused:
                opportunities.append(f"Market gap in {', '.join(underused)} platforms")
            
            # Content type gaps
            all_content_types = set()
            for profile in profiles:
                for metrics in profile.platforms.values():
                    all_content_types.update(metrics.content_types.keys())
            
            content_opportunities = {"live", "podcast", "stories", "reels"} - all_content_types
            if content_opportunities:
                opportunities.append(f"Content opportunity in {', '.join(content_opportunities)}")
            
            # Low engagement niches
            low_engagement_platforms = []
            for profile in profiles:
                for platform, metrics in profile.platforms.items():
                    if metrics.engagement_rate < 2.0:
                        low_engagement_platforms.append(platform)
            
            if low_engagement_platforms:
                opportunities.append(f"Low engagement indicates opportunity on {', '.join(set(low_engagement_platforms))}")
            
        except Exception as e:
            self.logger.error(f"Opportunity identification failed: {e}")
        
        return opportunities
    
    def _generate_strategic_recommendations(self, profiles: List[CompetitorProfile]) -> List[str]:
        """Generate strategic recommendations based on analysis."""        recommendations = []
        
        try:
            # Platform strategy
            platform_performance = defaultdict(list)
            for profile in profiles:
                for platform, metrics in profile.platforms.items():
                    platform_performance[platform].append(metrics.engagement_rate)
            
            # Recommend best performing platforms
            best_platforms = sorted(
                platform_performance.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else 0,
                reverse=True
            )[:3]
            
            if best_platforms:
                platforms_str = ', '.join([p[0] for p in best_platforms])
                recommendations.append(f"Focus on {platforms_str} for highest engagement")
            
            # Content strategy
            all_hashtags = []
            for profile in profiles:
                for metrics in profile.platforms.values():
                    all_hashtags.extend(metrics.top_hashtags)
            
            top_hashtags = [tag for tag, count in Counter(all_hashtags).most_common(5)]
            if top_hashtags:
                recommendations.append(f"Leverage trending hashtags: {', '.join(top_hashtags)}")
            
            # Posting frequency
            posting_frequencies = []
            for profile in profiles:
                for metrics in profile.platforms.values():
                    if metrics.posting_frequency > 0:
                        posting_frequencies.append(metrics.posting_frequency)
            
            if posting_frequencies:
                avg_frequency = statistics.mean(posting_frequencies)
                recommendations.append(f"Maintain posting frequency of {avg_frequency:.1f} posts/week minimum")
            
            # Competitive positioning
            competitive_scores = [p.competitive_score for p in profiles]
            if competitive_scores:
                avg_score = statistics.mean(competitive_scores)
                if avg_score < 50:
                    recommendations.append("Market has low competition - opportunity for aggressive growth")
                else:
                    recommendations.append("High competition requires differentiated content strategy")
            
        except Exception as e:
            self.logger.error(f"Recommendations generation failed: {e}")
        
        return recommendations
    
    def _identify_most_competitive_platform(self, profiles: List[CompetitorProfile]) -> str:
        """Identify the most competitive platform."""        try:
            platform_scores = defaultdict(list)
            
            for profile in profiles:
                for platform, metrics in profile.platforms.items():
                    # Calculate platform competitiveness score
                    score = (
                        (metrics.followers_count / 1000000) * 0.3 +  # Follower weight
                        (metrics.engagement_rate / 10) * 0.4 +      # Engagement weight
                        (metrics.posting_frequency / 7) * 0.3       # Frequency weight
                    )
                    platform_scores[platform].append(score)
            
            # Find platform with highest average score
            best_platform = max(
                platform_scores.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else 0,
                default=("unknown", [])
            )
            
            return best_platform[0]
            
        except Exception as e:
            self.logger.error(f"Most competitive platform identification failed: {e}")
            return "unknown"
    
    def _extract_key_insights(self, profiles: List[CompetitorProfile]) -> List[str]:
        """Extract key insights from competitor analysis."""        insights = []
        
        try:
            # Top performers
            top_performer = max(profiles, key=lambda p: p.competitive_score, default=None)
            if top_performer:
                insights.append(f"Market leader: {top_performer.name} with score {top_performer.competitive_score:.1f}")
            
            # Platform distribution
            platform_counts = defaultdict(int)
            for profile in profiles:
                for platform in profile.platforms.keys():
                    platform_counts[platform] += 1
            
            most_popular = max(platform_counts.items(), key=lambda x: x[1], default=("none", 0))
            insights.append(f"Most popular platform: {most_popular[0]} ({most_popular[1]} competitors)")
            
            # Growth patterns
            high_growth = [p for p in profiles if any(
                m.growth_rate > 10 for m in p.platforms.values()
            )]
            if high_growth:
                insights.append(f"{len(high_growth)} competitors showing high growth")
            
        except Exception as e:
            self.logger.error(f"Key insights extraction failed: {e}")
        
        return insights


class PlatformRateLimiter:
    """Platform-specific rate limiting."""    
    def __init__(self):
        self.limits = {
            "instagram": {"requests": 200, "window": 3600},  # 200/hour
            "twitter": {"requests": 300, "window": 900},     # 300/15min
            "youtube": {"requests": 100, "window": 3600},    # 100/hour
            "tiktok": {"requests": 60, "window": 3600},      # 60/hour (web scraping)
            "spotify": {"requests": 100, "window": 3600}     # 100/hour
        }
        self.usage = defaultdict(list)
    
    async def can_make_request(self, platform: str) -> bool:
        """Check if request can be made within rate limits."""        now = datetime.utcnow()
        limit_config = self.limits.get(platform, {"requests": 60, "window": 3600})
        
        # Clean old requests
        cutoff = now - timedelta(seconds=limit_config["window"])
        self.usage[platform] = [
            req_time for req_time in self.usage[platform]
            if req_time > cutoff
        ]
        
        return len(self.usage[platform]) < limit_config["requests"]
    
    async def record_request(self, platform: str):
        """Record a request for rate limiting."""        self.usage[platform].append(datetime.utcnow())
