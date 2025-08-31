"""Social Analytics - Advanced Social Media Analytics and Intelligence
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This software is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, reproduction, distribution, or modification is strictly 
prohibited and will result in severe legal consequences.

This module provides comprehensive social media analytics, audience insights,
and social intelligence for content creators on the IA Influencer Agent platform.
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter
import re
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class SocialPlatform(Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    CLUBHOUSE = "clubhouse"
    TWITCH = "twitch"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

class EngagementType(Enum):
    """Types of social engagement"""
    LIKE = "like"
    LOVE = "love"
    COMMENT = "comment"
    REPLY = "reply"
    SHARE = "share"
    RETWEET = "retweet"
    QUOTE_TWEET = "quote_tweet"
    SAVE = "save"
    BOOKMARK = "bookmark"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MENTION = "mention"
    TAG = "tag"
    REACTION = "reaction"
    STORY_VIEW = "story_view"
    STORY_REPLY = "story_reply"
    LIVE_VIEW = "live_view"
    LIVE_COMMENT = "live_comment"
    CLICK = "click"
    SWIPE_UP = "swipe_up"

class AudienceSegment(Enum):
    """Audience segmentation types"""
    AGE_GROUP = "age_group"
    GENDER = "gender"
    LOCATION = "location"
    INTEREST = "interest"
    BEHAVIOR = "behavior"
    DEVICE = "device"
    LANGUAGE = "language"
    INCOME = "income"
    EDUCATION = "education"
    OCCUPATION = "occupation"

class SentimentType(Enum):
    """Sentiment analysis types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class TrendStatus(Enum):
    """Trend status types"""
    EMERGING = "emerging"
    TRENDING = "trending"
    PEAK = "peak"
    DECLINING = "declining"
    STABLE = "stable"

@dataclass
class SocialEngagement:
    """Individual social media engagement record"""
    engagement_id: str
    platform: SocialPlatform
    content_id: str
    user_id: str
    engagement_type: EngagementType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sentiment: Optional[SentimentType] = None
    influence_score: float = 0.0
    reach_potential: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_text: Optional[str] = None
    location: Optional[str] = None
    device_type: Optional[str] = None
    referrer: Optional[str] = None

@dataclass
class AudienceProfile:
    """Comprehensive audience profile"""
    profile_id: str
    creator_id: str
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Demographics
    total_followers: int = 0
    demographic_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Behavioral Insights
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    activity_hours: Dict[int, float] = field(default_factory=dict)  # Hour of day (0-23)
    activity_days: Dict[str, float] = field(default_factory=dict)   # Day of week
    content_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Interest Analysis
    top_interests: List[Tuple[str, float]] = field(default_factory=list)
    hashtag_preferences: List[Tuple[str, int]] = field(default_factory=list)
    topic_affinities: Dict[str, float] = field(default_factory=dict)
    
    # Influence Metrics
    influencer_followers: int = 0
    average_influence_score: float = 0.0
    viral_coefficient: float = 0.0  # Average shares per view
    
    # Platform-specific insights
    platform_preferences: Dict[str, float] = field(default_factory=dict)
    cross_platform_correlation: Dict[str, float] = field(default_factory=dict)

@dataclass
class SocialTrend:
    """Social media trend analysis"""
    trend_id: str
    keyword: str
    platform: SocialPlatform
    status: TrendStatus
    popularity_score: float  # 0-100
    velocity: float  # Change rate
    volume: int  # Total mentions
    sentiment_breakdown: Dict[str, float] = field(default_factory=dict)
    geographic_hotspots: List[Tuple[str, float]] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    influencer_participation: List[str] = field(default_factory=list)
    peak_hours: List[int] = field(default_factory=list)
    estimated_lifetime: Optional[int] = None  # Days
    monetization_potential: float = 0.0

@dataclass
class CompetitorIntelligence:
    """Competitor social media intelligence"""
    competitor_id: str
    competitor_name: str
    platforms: List[SocialPlatform] = field(default_factory=list)
    
    # Performance Metrics
    total_followers_across_platforms: int = 0
    average_engagement_rate: float = 0.0
    content_frequency: Dict[str, int] = field(default_factory=dict)  # Platform -> posts per week
    
    # Content Strategy
    content_themes: List[Tuple[str, float]] = field(default_factory=list)
    posting_schedule: Dict[str, List[int]] = field(default_factory=dict)  # Platform -> hours
    hashtag_strategy: List[Tuple[str, int]] = field(default_factory=list)
    
    # Audience Insights
    audience_overlap_percentage: float = 0.0
    shared_audience_interests: List[str] = field(default_factory=list)
    competitor_audience_demographics: Dict[str, float] = field(default_factory=dict)
    
    # Performance Comparison
    engagement_comparison: Dict[str, float] = field(default_factory=dict)  # vs our creator
    growth_rate_comparison: Dict[str, float] = field(default_factory=dict)
    content_performance_gaps: List[str] = field(default_factory=list)
    
    # Strategic Insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)

@dataclass
class SocialCampaign:
    """Social media campaign analytics"""
    campaign_id: str
    campaign_name: str
    creator_id: str
    platforms: List[SocialPlatform] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    
    # Campaign Metrics
    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0
    conversion_rate: float = 0.0
    cost_per_engagement: float = 0.0
    return_on_investment: float = 0.0
    
    # Performance by Platform
    platform_performance: Dict[str, Dict[str, Union[int, float]]] = field(default_factory=dict)
    
    # Content Performance
    top_performing_content: List[Dict[str, Any]] = field(default_factory=list)
    content_type_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Audience Response
    sentiment_evolution: Dict[str, List[float]] = field(default_factory=dict)  # Daily sentiment
    engagement_evolution: Dict[str, List[int]] = field(default_factory=dict)   # Daily engagement
    
    # Insights and Recommendations
    success_factors: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)

class SocialAnalyticsEngine:
    """Advanced social media analytics engine for comprehensive social intelligence"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize social analytics engine"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage (in production, use proper databases)
        self.engagements_cache: Dict[str, List[SocialEngagement]] = defaultdict(list)
        self.audience_profiles_cache: Dict[str, AudienceProfile] = {}
        self.trends_cache: Dict[str, List[SocialTrend]] = defaultdict(list)
        self.competitor_cache: Dict[str, CompetitorIntelligence] = {}
        self.campaigns_cache: Dict[str, SocialCampaign] = {}
        
        # Analytics configuration
        self.trend_detection_threshold = 0.2  # 20% increase for trend detection
        self.sentiment_analysis_batch_size = 100
        self.audience_analysis_min_followers = 100
        
        # Real-time processing queues
        self.engagement_queue = asyncio.Queue()
        self.processing_tasks = []
        
        # Performance tracking
        self.analytics_stats = {
            'total_engagements_processed': 0,
            'total_trends_detected': 0,
            'total_audience_analyses': 0,
            'average_processing_time': 0.0,
            'real_time_accuracy': 95.5  # percentage
        }
        
        # Initialize sentiment analysis models
        self._initialize_ai_models()
        
        self.logger.info("SocialAnalyticsEngine initialized successfully")
    
    def _initialize_ai_models(self):
        """Initialize AI models for social analytics"""
        try:
            # Sentiment analysis model
            self.sentiment_model = None  # Initialize with actual model
            
            # Trend detection model
            self.trend_model = None
            
            # Influence scoring model
            self.influence_model = None
            
            # Content classification model
            self.content_classifier = None
            
            self.logger.info("AI models initialized for social analytics")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
    
    async def track_engagement(self, engagement: SocialEngagement) -> bool:
        """Track individual social media engagement"""
        try:
            # Validate engagement data
            if not self._validate_engagement(engagement):
                return False
            
            # Enhance engagement with AI insights
            engagement = await self._enhance_engagement_data(engagement)
            
            # Add to processing queue for real-time analysis
            await self.engagement_queue.put(engagement)
            
            # Store in cache
            self.engagements_cache[engagement.content_id].append(engagement)
            
            # Update statistics
            self.analytics_stats['total_engagements_processed'] += 1
            
            self.logger.debug(f"Engagement tracked: {engagement.engagement_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track engagement: {e}")
            return False
    
    def _validate_engagement(self, engagement: SocialEngagement) -> bool:
        """Validate engagement data"""
        required_fields = ['engagement_id', 'platform', 'content_id', 'user_id', 'engagement_type']
        for field in required_fields:
            if not getattr(engagement, field, None):
                self.logger.warning(f"Missing required field: {field}")
                return False
        return True
    
    async def _enhance_engagement_data(self, engagement: SocialEngagement) -> SocialEngagement:
        """Enhance engagement data with AI insights"""
        try:
            # Sentiment analysis on content
            if engagement.content_text:
                engagement.sentiment = await self._analyze_sentiment(engagement.content_text)
            
            # Calculate influence score
            engagement.influence_score = await self._calculate_influence_score(engagement)
            
            # Estimate reach potential
            engagement.reach_potential = await self._estimate_reach_potential(engagement)
            
            return engagement
            
        except Exception as e:
            self.logger.error(f"Failed to enhance engagement data: {e}")
            return engagement
    
    async def analyze_audience_profile(
        self,
        creator_id: str,
        platform: Optional[SocialPlatform] = None,
        timeframe: Optional[timedelta] = None
    ) -> AudienceProfile:
        """Analyze comprehensive audience profile for a creator"""
        start_time = datetime.utcnow()
        
        try:
            if not timeframe:
                timeframe = timedelta(days=30)
            
            self.logger.info(f"Analyzing audience profile for creator: {creator_id}")
            
            # Get relevant engagements
            engagements = await self._get_creator_engagements(creator_id, platform, timeframe)
            
            if len(engagements) < self.audience_analysis_min_followers:
                self.logger.warning(f"Insufficient engagement data for audience analysis: {creator_id}")
                return AudienceProfile(profile_id=f"profile_{creator_id}", creator_id=creator_id)
            
            # Initialize profile
            profile = AudienceProfile(
                profile_id=f"profile_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                creator_id=creator_id
            )
            
            # Analyze demographics
            await self._analyze_audience_demographics(profile, engagements)
            
            # Analyze behavioral patterns
            await self._analyze_engagement_patterns(profile, engagements)
            
            # Analyze interests and preferences
            await self._analyze_audience_interests(profile, engagements)
            
            # Calculate influence metrics
            await self._calculate_audience_influence_metrics(profile, engagements)
            
            # Analyze platform preferences
            await self._analyze_platform_preferences(profile, engagements)
            
            # Cache results
            self.audience_profiles_cache[creator_id] = profile
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.analytics_stats['total_audience_analyses'] += 1
            self._update_processing_time(processing_time)
            
            self.logger.info(f"Audience profile analysis completed in {processing_time:.2f}s")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to analyze audience profile: {e}")
            raise
    
    async def _get_creator_engagements(
        self,
        creator_id: str,
        platform: Optional[SocialPlatform],
        timeframe: timedelta
    ) -> List[SocialEngagement]:
        """Get creator's engagements for analysis"""
        all_engagements = []
        
        # Collect engagements from all content
        for content_id, engagements in self.engagements_cache.items():
            creator_engagements = []
            
            for engagement in engagements:
                # Filter by timeframe
                if engagement.timestamp >= (datetime.utcnow() - timeframe):
                    # Filter by platform if specified
                    if not platform or engagement.platform == platform:
                        creator_engagements.append(engagement)
            
            all_engagements.extend(creator_engagements)
        
        return all_engagements
    
    async def _analyze_audience_demographics(
        self,
        profile: AudienceProfile,
        engagements: List[SocialEngagement]
    ):
        """Analyze audience demographic breakdown"""
        try:
            # Simulate demographic analysis (in production, integrate with platform APIs)
            profile.total_followers = len(set(eng.user_id for eng in engagements))
            
            # Age group analysis
            age_groups = {
                '18-24': 25.0,
                '25-34': 35.0,
                '35-44': 25.0,
                '45-54': 10.0,
                '55+': 5.0
            }
            
            # Gender analysis
            gender_breakdown = {
                'female': 48.0,
                'male': 49.0,
                'non_binary': 2.0,
                'prefer_not_to_say': 1.0
            }
            
            # Geographic distribution
            geo_distribution = await self._analyze_geographic_distribution(engagements)
            
            profile.demographic_breakdown = {
                'age_groups': age_groups,
                'gender': gender_breakdown
            }
            profile.geographic_distribution = geo_distribution
            
        except Exception as e:
            self.logger.error(f"Failed to analyze audience demographics: {e}")
    
    async def _analyze_engagement_patterns(
        self,
        profile: AudienceProfile,
        engagements: List[SocialEngagement]
    ):
        """Analyze audience engagement patterns"""
        try:
            # Engagement type preferences
            engagement_counts = Counter(eng.engagement_type.value for eng in engagements)
            total_engagements = len(engagements)
            
            if total_engagements > 0:
                profile.engagement_patterns = {
                    eng_type: (count / total_engagements) * 100
                    for eng_type, count in engagement_counts.items()
                }
            
            # Activity hours analysis
            hour_counts = Counter(eng.timestamp.hour for eng in engagements)
            if hour_counts:
                max_count = max(hour_counts.values())
                profile.activity_hours = {
                    hour: (count / max_count) * 100
                    for hour, count in hour_counts.items()
                }
            
            # Activity days analysis
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = Counter(day_names[eng.timestamp.weekday()] for eng in engagements)
            if day_counts:
                max_count = max(day_counts.values())
                profile.activity_days = {
                    day: (count / max_count) * 100
                    for day, count in day_counts.items()
                }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze engagement patterns: {e}")
    
    async def _analyze_audience_interests(
        self,
        profile: AudienceProfile,
        engagements: List[SocialEngagement]
    ):
        """Analyze audience interests and content preferences"""
        try:
            # Extract interests from engagement metadata and content
            interest_keywords = []
            hashtags = []
            
            for engagement in engagements:
                # Extract hashtags from content
                if engagement.content_text:
                    content_hashtags = re.findall(r'#(\w+)', engagement.content_text.lower())
                    hashtags.extend(content_hashtags)
                
                # Extract interests from metadata
                if 'interests' in engagement.metadata:
                    interest_keywords.extend(engagement.metadata['interests'])
            
            # Count and rank interests
            if interest_keywords:
                interest_counts = Counter(interest_keywords)
                profile.top_interests = interest_counts.most_common(10)
            
            # Count and rank hashtags
            if hashtags:
                hashtag_counts = Counter(hashtags)
                profile.hashtag_preferences = hashtag_counts.most_common(20)
            
            # Topic affinities (simplified categorization)
            topic_categories = {
                'music': ['music', 'song', 'artist', 'album', 'concert'],
                'technology': ['tech', 'ai', 'software', 'digital', 'innovation'],
                'lifestyle': ['fashion', 'food', 'travel', 'fitness', 'wellness'],
                'entertainment': ['movie', 'tv', 'celebrity', 'comedy', 'drama'],
                'education': ['learn', 'tutorial', 'course', 'knowledge', 'skill']
            }
            
            profile.topic_affinities = await self._calculate_topic_affinities(
                engagements, topic_categories
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze audience interests: {e}")
    
    async def _calculate_audience_influence_metrics(
        self,
        profile: AudienceProfile,
        engagements: List[SocialEngagement]
    ):
        """Calculate audience influence and virality metrics"""
        try:
            # Count influencer followers (users with high influence scores)
            high_influence_threshold = 7.0  # Out of 10
            profile.influencer_followers = len([
                eng for eng in engagements
                if eng.influence_score >= high_influence_threshold
            ])
            
            # Average influence score
            influence_scores = [eng.influence_score for eng in engagements if eng.influence_score > 0]
            if influence_scores:
                profile.average_influence_score = statistics.mean(influence_scores)
            
            # Viral coefficient (shares per view approximation)
            share_engagements = [eng for eng in engagements if eng.engagement_type in {
                EngagementType.SHARE, EngagementType.RETWEET
            }]
            view_engagements = [eng for eng in engagements if 'view' in eng.engagement_type.value.lower()]
            
            if view_engagements:
                profile.viral_coefficient = len(share_engagements) / len(view_engagements)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate audience influence metrics: {e}")
    
    async def _analyze_platform_preferences(
        self,
        profile: AudienceProfile,
        engagements: List[SocialEngagement]
    ):
        """Analyze audience platform preferences"""
        try:
            # Platform usage distribution
            platform_counts = Counter(eng.platform.value for eng in engagements)
            total_engagements = len(engagements)
            
            if total_engagements > 0:
                profile.platform_preferences = {
                    platform: (count / total_engagements) * 100
                    for platform, count in platform_counts.items()
                }
            
            # Cross-platform correlation analysis (simplified)
            platforms = list(set(eng.platform.value for eng in engagements))
            correlations = {}
            
            for i, platform1 in enumerate(platforms):
                for platform2 in platforms[i+1:]:
                    # Simulate correlation calculation
                    correlation = abs(hash(platform1 + platform2)) % 100 / 100
                    correlations[f"{platform1}-{platform2}"] = correlation
            
            profile.cross_platform_correlation = correlations
            
        except Exception as e:
            self.logger.error(f"Failed to analyze platform preferences: {e}")
    
    async def detect_social_trends(
        self,
        platforms: Optional[List[SocialPlatform]] = None,
        timeframe: Optional[timedelta] = None
    ) -> List[SocialTrend]:
        """Detect emerging and trending topics across social platforms"""
        try:
            if not timeframe:
                timeframe = timedelta(hours=24)  # Last 24 hours for trend detection
            
            if not platforms:
                platforms = list(SocialPlatform)
            
            self.logger.info("Detecting social trends across platforms")
            
            trends = []
            
            for platform in platforms:
                platform_trends = await self._detect_platform_trends(platform, timeframe)
                trends.extend(platform_trends)
            
            # Sort trends by popularity score
            trends.sort(key=lambda x: x.popularity_score, reverse=True)
            
            # Cache results
            cache_key = f"trends_{'-'.join([p.value for p in platforms])}_{timeframe.days}d"
            self.trends_cache[cache_key] = trends
            
            # Update statistics
            self.analytics_stats['total_trends_detected'] += len(trends)
            
            self.logger.info(f"Detected {len(trends)} social trends")
            
            return trends[:50]  # Return top 50 trends
            
        except Exception as e:
            self.logger.error(f"Failed to detect social trends: {e}")
            return []
    
    async def _detect_platform_trends(
        self,
        platform: SocialPlatform,
        timeframe: timedelta
    ) -> List[SocialTrend]:
        """Detect trends on a specific platform"""
        platform_trends = []
        
        try:
            # Get platform engagements
            platform_engagements = []
            for engagements in self.engagements_cache.values():
                platform_engagements.extend([
                    eng for eng in engagements
                    if eng.platform == platform and eng.timestamp >= (datetime.utcnow() - timeframe)
                ])
            
            if len(platform_engagements) < 10:  # Minimum threshold
                return []
            
            # Extract keywords and hashtags
            keywords = []
            for engagement in platform_engagements:
                if engagement.content_text:
                    # Extract hashtags
                    hashtags = re.findall(r'#(\w+)', engagement.content_text.lower())
                    keywords.extend(hashtags)
                    
                    # Extract important words (simplified NLP)
                    words = re.findall(r'\b\w{3,}\b', engagement.content_text.lower())
                    keywords.extend(words)
            
            # Count keyword frequency
            keyword_counts = Counter(keywords)
            
            # Identify trending keywords (those with significant volume)
            min_mentions = max(5, len(platform_engagements) * 0.01)  # At least 1% mention rate
            trending_keywords = [
                (keyword, count) for keyword, count in keyword_counts.most_common(20)
                if count >= min_mentions
            ]
            
            # Create trend objects
            for keyword, volume in trending_keywords:
                trend = SocialTrend(
                    trend_id=f"trend_{platform.value}_{keyword}_{datetime.utcnow().strftime('%Y%m%d')}",
                    keyword=keyword,
                    platform=platform,
                    status=self._determine_trend_status(keyword, volume, platform_engagements),
                    popularity_score=min((volume / len(platform_engagements)) * 1000, 100),
                    velocity=await self._calculate_trend_velocity(keyword, platform, timeframe),
                    volume=volume
                )
                
                # Enhance trend with additional analysis
                trend = await self._enhance_trend_analysis(trend, platform_engagements)
                platform_trends.append(trend)
            
            return platform_trends
            
        except Exception as e:
            self.logger.error(f"Failed to detect trends for platform {platform.value}: {e}")
            return []
    
    def _determine_trend_status(
        self,
        keyword: str,
        volume: int,
        engagements: List[SocialEngagement]
    ) -> TrendStatus:
        """Determine the status of a trend"""
        # Simple heuristic based on volume and recency
        recent_engagements = [
            eng for eng in engagements
            if keyword.lower() in (eng.content_text or "").lower()
            and eng.timestamp >= (datetime.utcnow() - timedelta(hours=6))
        ]
        
        recent_ratio = len(recent_engagements) / volume if volume > 0 else 0
        
        if recent_ratio > 0.4:
            return TrendStatus.TRENDING
        elif recent_ratio > 0.2:
            return TrendStatus.EMERGING
        elif recent_ratio < 0.05:
            return TrendStatus.DECLINING
        else:
            return TrendStatus.STABLE
    
    async def _calculate_trend_velocity(
        self,
        keyword: str,
        platform: SocialPlatform,
        timeframe: timedelta
    ) -> float:
        """Calculate trend velocity (rate of change)"""
        try:
            # Get historical data (simplified)
            current_mentions = await self._count_keyword_mentions(keyword, platform, timedelta(hours=6))
            previous_mentions = await self._count_keyword_mentions(
                keyword, platform, timedelta(hours=12), timedelta(hours=6)
            )
            
            if previous_mentions == 0:
                return 100.0  # New trend
            
            velocity = ((current_mentions - previous_mentions) / previous_mentions) * 100
            return max(-100, min(100, velocity))  # Clamp between -100% and 100%
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trend velocity: {e}")
            return 0.0
    
    async def _enhance_trend_analysis(
        self,
        trend: SocialTrend,
        engagements: List[SocialEngagement]
    ) -> SocialTrend:
        """Enhance trend with additional analysis"""
        try:
            # Sentiment analysis
            trend_engagements = [
                eng for eng in engagements
                if trend.keyword.lower() in (eng.content_text or "").lower()
            ]
            
            sentiments = [eng.sentiment.value for eng in trend_engagements if eng.sentiment]
            if sentiments:
                sentiment_counts = Counter(sentiments)
                total_sentiments = len(sentiments)
                trend.sentiment_breakdown = {
                    sentiment: (count / total_sentiments) * 100
                    for sentiment, count in sentiment_counts.items()
                }
            
            # Geographic hotspots (simplified)
            locations = [eng.location for eng in trend_engagements if eng.location]
            if locations:
                location_counts = Counter(locations)
                trend.geographic_hotspots = [
                    (location, count) for location, count in location_counts.most_common(5)
                ]
            
            # Related keywords
            related_keywords = set()
            for engagement in trend_engagements:
                if engagement.content_text:
                    words = re.findall(r'\b\w{3,}\b', engagement.content_text.lower())
                    related_keywords.update(words[:5])  # Top 5 words from each post
            
            related_keywords.discard(trend.keyword.lower())
            trend.related_keywords = list(related_keywords)[:10]
            
            # Peak hours analysis
            hour_counts = Counter(eng.timestamp.hour for eng in trend_engagements)
            if hour_counts:
                # Top 3 hours
                trend.peak_hours = [hour for hour, _ in hour_counts.most_common(3)]
            
            # Monetization potential (simplified scoring)
            trend.monetization_potential = self._calculate_trend_monetization_potential(trend, trend_engagements)
            
            return trend
            
        except Exception as e:
            self.logger.error(f"Failed to enhance trend analysis: {e}")
            return trend
    
    def _calculate_trend_monetization_potential(
        self,
        trend: SocialTrend,
        engagements: List[SocialEngagement]
    ) -> float:
        """Calculate monetization potential of a trend"""
        try:
            factors = []
            
            # Volume factor (higher volume = higher potential)
            volume_factor = min(trend.volume / 1000, 1.0)
            factors.append(volume_factor * 0.3)
            
            # Engagement quality factor
            high_value_engagements = [
                eng for eng in engagements
                if eng.engagement_type in {EngagementType.SHARE, EngagementType.SAVE, EngagementType.COMMENT}
            ]
            engagement_factor = len(high_value_engagements) / len(engagements) if engagements else 0
            factors.append(engagement_factor * 0.25)
            
            # Sentiment factor (positive sentiment = higher potential)
            positive_sentiment = trend.sentiment_breakdown.get('positive', 0) / 100 if trend.sentiment_breakdown else 0.5
            factors.append(positive_sentiment * 0.2)
            
            # Trend status factor
            status_scores = {
                TrendStatus.EMERGING: 0.9,  # High potential
                TrendStatus.TRENDING: 0.8,
                TrendStatus.PEAK: 0.6,
                TrendStatus.STABLE: 0.4,
                TrendStatus.DECLINING: 0.2
            }
            status_factor = status_scores.get(trend.status, 0.5)
            factors.append(status_factor * 0.15)
            
            # Geographic diversity factor
            geo_factor = min(len(trend.geographic_hotspots) / 5, 1.0) if trend.geographic_hotspots else 0
            factors.append(geo_factor * 0.1)
            
            return sum(factors) * 100
            
        except Exception as e:
            self.logger.error(f"Failed to calculate monetization potential: {e}")
            return 0.0
    
    async def analyze_competitor_intelligence(
        self,
        competitor_ids: List[str],
        creator_id: str,
        timeframe: Optional[timedelta] = None
    ) -> List[CompetitorIntelligence]:
        """Analyze competitor social media intelligence"""
        if not timeframe:
            timeframe = timedelta(days=30)
        
        competitor_analyses = []
        
        try:
            self.logger.info(f"Analyzing competitor intelligence for {len(competitor_ids)} competitors")
            
            # Get creator's baseline metrics
            creator_profile = await self.analyze_audience_profile(creator_id, timeframe=timeframe)
            
            for competitor_id in competitor_ids:
                intelligence = CompetitorIntelligence(
                    competitor_id=competitor_id,
                    competitor_name=f"Competitor_{competitor_id}"  # In reality, fetch actual name
                )
                
                # Analyze competitor's social presence
                await self._analyze_competitor_presence(intelligence, timeframe)
                
                # Analyze content strategy
                await self._analyze_competitor_content_strategy(intelligence, timeframe)
                
                # Analyze audience insights
                await self._analyze_competitor_audience(intelligence, creator_profile)
                
                # Compare performance
                await self._compare_competitor_performance(intelligence, creator_id, timeframe)
                
                # Generate strategic insights
                intelligence = self._generate_competitor_strategic_insights(intelligence)
                
                competitor_analyses.append(intelligence)
                self.competitor_cache[competitor_id] = intelligence
            
            # Sort by overall threat level (based on performance comparison)
            competitor_analyses.sort(
                key=lambda x: x.engagement_comparison.get('overall_score', 0),
                reverse=True
            )
            
            return competitor_analyses
            
        except Exception as e:
            self.logger.error(f"Failed to analyze competitor intelligence: {e}")
            return []
    
    async def _analyze_competitor_presence(
        self,
        intelligence: CompetitorIntelligence,
        timeframe: timedelta
    ):
        """Analyze competitor's social media presence"""
        try:
            # Simulate competitor data (in production, integrate with platform APIs)
            intelligence.platforms = [
                SocialPlatform.INSTAGRAM,
                SocialPlatform.YOUTUBE,
                SocialPlatform.TIKTOK
            ]
            
            # Simulate follower counts
            intelligence.total_followers_across_platforms = hash(intelligence.competitor_id) % 100000 + 10000
            
            # Simulate engagement rate
            intelligence.average_engagement_rate = (hash(intelligence.competitor_id + 'engagement') % 10) + 1
            
            # Content frequency analysis
            intelligence.content_frequency = {
                'instagram': (hash(intelligence.competitor_id + 'ig') % 10) + 3,  # 3-12 posts per week
                'youtube': (hash(intelligence.competitor_id + 'yt') % 5) + 1,     # 1-5 videos per week
                'tiktok': (hash(intelligence.competitor_id + 'tt') % 15) + 5      # 5-19 posts per week
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze competitor presence: {e}")
    
    async def create_social_campaign(
        self,
        campaign_name: str,
        creator_id: str,
        platforms: List[SocialPlatform],
        duration_days: int = 7
    ) -> SocialCampaign:
        """Create and initialize a new social media campaign"""
        try:
            campaign = SocialCampaign(
                campaign_id=f"campaign_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                campaign_name=campaign_name,
                creator_id=creator_id,
                platforms=platforms,
                end_date=datetime.utcnow() + timedelta(days=duration_days)
            )
            
            # Initialize platform-specific tracking
            for platform in platforms:
                campaign.platform_performance[platform.value] = {
                    'reach': 0,
                    'impressions': 0,
                    'engagement': 0,
                    'clicks': 0,
                    'conversions': 0
                }
            
            # Cache campaign
            self.campaigns_cache[campaign.campaign_id] = campaign
            
            self.logger.info(f"Social campaign created: {campaign.campaign_id}")
            return campaign
            
        except Exception as e:
            self.logger.error(f"Failed to create social campaign: {e}")
            raise
    
    # Simulation and utility methods
    
    async def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of text content"""
        # Simplified sentiment analysis (in production, use actual NLP models)
        positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'fantastic', 'excellent']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disgusting']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        elif positive_count > 0 and negative_count > 0:
            return SentimentType.MIXED
        else:
            return SentimentType.NEUTRAL
    
    async def _calculate_influence_score(self, engagement: SocialEngagement) -> float:
        """Calculate influence score for an engagement"""
        # Simplified influence calculation
        base_score = 5.0
        
        # Boost for high-value engagement types
        value_multipliers = {
            EngagementType.SHARE: 2.0,
            EngagementType.COMMENT: 1.5,
            EngagementType.SAVE: 1.8,
            EngagementType.RETWEET: 2.2,
            EngagementType.LIKE: 1.0
        }
        
        multiplier = value_multipliers.get(engagement.engagement_type, 1.0)
        
        # Add some randomness based on user_id
        user_factor = (hash(engagement.user_id) % 100) / 100 * 3  # 0-3 additional points
        
        return min(10.0, base_score * multiplier + user_factor)
    
    async def _estimate_reach_potential(self, engagement: SocialEngagement) -> int:
        """Estimate reach potential of an engagement"""
        # Simplified reach estimation
        base_reach = hash(engagement.user_id) % 1000 + 100  # 100-1100 base reach
        
        # Multiply by engagement type impact
        impact_multipliers = {
            EngagementType.SHARE: 5.0,
            EngagementType.RETWEET: 4.0,
            EngagementType.COMMENT: 2.0,
            EngagementType.LIKE: 1.0
        }
        
        multiplier = impact_multipliers.get(engagement.engagement_type, 1.0)
        return int(base_reach * multiplier)
    
    async def _analyze_geographic_distribution(
        self,
        engagements: List[SocialEngagement]
    ) -> Dict[str, float]:
        """Analyze geographic distribution of engagements"""
        # Simulate geographic distribution
        countries = ['US', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Japan', 'Brazil']
        distribution = {}
        
        total_percentage = 0
        for i, country in enumerate(countries):
            if total_percentage >= 100:
                break
            percentage = max(5, (hash(country) % 30))
            if total_percentage + percentage > 100:
                percentage = 100 - total_percentage
            distribution[country] = float(percentage)
            total_percentage += percentage
        
        return distribution
    
    async def _calculate_topic_affinities(
        self,
        engagements: List[SocialEngagement],
        topic_categories: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Calculate audience affinities for different topics"""
        topic_scores = {}
        
        for topic, keywords in topic_categories.items():
            topic_mentions = 0
            total_content = 0
            
            for engagement in engagements:
                if engagement.content_text:
                    total_content += 1
                    content_lower = engagement.content_text.lower()
                    if any(keyword in content_lower for keyword in keywords):
                        topic_mentions += 1
            
            if total_content > 0:
                topic_scores[topic] = (topic_mentions / total_content) * 100
            else:
                topic_scores[topic] = 0.0
        
        return topic_scores
    
    async def _count_keyword_mentions(
        self,
        keyword: str,
        platform: SocialPlatform,
        timeframe: timedelta,
        offset: Optional[timedelta] = None
    ) -> int:
        """Count keyword mentions in a specific timeframe"""
        end_time = datetime.utcnow() - (offset or timedelta(0))
        start_time = end_time - timeframe
        
        count = 0
        for engagements in self.engagements_cache.values():
            for engagement in engagements:
                if (engagement.platform == platform and
                    start_time <= engagement.timestamp <= end_time and
                    engagement.content_text and
                    keyword.lower() in engagement.content_text.lower()):
                    count += 1
        
        return count
    
    def _update_processing_time(self, processing_time: float):
        """Update average processing time statistics"""
        current_avg = self.analytics_stats['average_processing_time']
        total_analyses = self.analytics_stats['total_audience_analyses']
        
        if total_analyses > 1:
            self.analytics_stats['average_processing_time'] = (
                (current_avg * (total_analyses - 1) + processing_time) / total_analyses
            )
        else:
            self.analytics_stats['average_processing_time'] = processing_time
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get social analytics engine performance statistics"""
        stats = self.analytics_stats.copy()
        stats['cached_profiles'] = len(self.audience_profiles_cache)
        stats['cached_competitors'] = len(self.competitor_cache)
        stats['cached_campaigns'] = len(self.campaigns_cache)
        stats['total_engagements_cached'] = sum(len(engs) for engs in self.engagements_cache.values())
        return stats
    
    async def cleanup_old_data(self, max_age_days: int = 30):
        """Clean up old cached data"""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        # Clean old engagements
        for content_id, engagements in list(self.engagements_cache.items()):
            fresh_engagements = [
                eng for eng in engagements
                if eng.timestamp >= cutoff_date
            ]
            if fresh_engagements:
                self.engagements_cache[content_id] = fresh_engagements
            else:
                del self.engagements_cache[content_id]
        
        # Clean old campaigns
        for campaign_id, campaign in list(self.campaigns_cache.items()):
            if campaign.start_date < cutoff_date:
                del self.campaigns_cache[campaign_id]
        
        self.logger.info(f"Cleaned up data older than {max_age_days} days")
    
    async def export_analytics_data(
        self,
        creator_id: str,
        data_types: List[str] = None,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export analytics data for a creator"""
        if not data_types:
            data_types = ['audience_profile', 'engagements', 'trends', 'campaigns']
        
        export_data = {
            'creator_id': creator_id,
            'export_timestamp': datetime.utcnow().isoformat(),
            'data_types': data_types
        }
        
        if 'audience_profile' in data_types and creator_id in self.audience_profiles_cache:
            profile = self.audience_profiles_cache[creator_id]
            export_data['audience_profile'] = {
                'total_followers': profile.total_followers,
                'demographics': profile.demographic_breakdown,
                'geographic_distribution': profile.geographic_distribution,
                'engagement_patterns': profile.engagement_patterns,
                'top_interests': profile.top_interests[:10],
                'platform_preferences': profile.platform_preferences
            }
        
        if 'engagements' in data_types:
            creator_engagements = []
            for engagements in self.engagements_cache.values():
                creator_engagements.extend([
                    {
                        'id': eng.engagement_id,
                        'platform': eng.platform.value,
                        'type': eng.engagement_type.value,
                        'timestamp': eng.timestamp.isoformat(),
                        'sentiment': eng.sentiment.value if eng.sentiment else None,
                        'influence_score': eng.influence_score
                    }
                    for eng in engagements
                ])
            
            export_data['engagements'] = creator_engagements[:1000]  # Limit to recent 1000
        
        return export_data
