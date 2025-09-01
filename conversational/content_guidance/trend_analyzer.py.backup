"""Trend Analyzer - Advanced AI-Powered Content Trend Detection and Analysis
========================================================================

This module provides comprehensive trend analysis capabilities for content creators,
including real-time trend detection, performance prediction, and trend-based
content recommendations across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
import re
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from textblob import TextBlob

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.nlp.text_processor import TextProcessor
from backend.integrations.social_media_apis import SocialMediaAPIManager
from backend.analytics.trend_analytics import TrendAnalyticsService

logger = get_logger(__name__)
settings = get_settings()


class TrendType(Enum):
    """Types of trends that can be detected."""
    VIRAL_CONTENT = "viral_content"
    HASHTAG_TREND = "hashtag_trend"
    MUSIC_TREND = "music_trend"
    CHALLENGE_TREND = "challenge_trend"
    TOPIC_TREND = "topic_trend"
    VISUAL_TREND = "visual_trend"
    FORMAT_TREND = "format_trend"
    PLATFORM_FEATURE = "platform_feature"


class TrendStage(Enum):
    """Lifecycle stages of trends."""
    EMERGING = "emerging"
    GROWING = "growing"
    PEAK = "peak"
    DECLINING = "declining"
    EXPIRED = "expired"


class TrendSource(Enum):
    """Sources where trends are detected."""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    GOOGLE_TRENDS = "google_trends"
    NEWS_MEDIA = "news_media"
    INFLUENCER_CONTENT = "influencer_content"


@dataclass
class TrendMetrics:
    """Metrics for trend analysis."""
    engagement_velocity: float
    reach_acceleration: float
    mention_frequency: int
    sentiment_score: float
    participation_rate: float
    platform_distribution: Dict[str, float]
    demographic_spread: Dict[str, float]
    virality_coefficient: float
    peak_prediction: Optional[datetime]
    longevity_estimate: int  # days


@dataclass
class TrendData:
    """Comprehensive trend data structure."""
    trend_id: str
    trend_type: TrendType
    trend_stage: TrendStage
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    source_platforms: List[TrendSource]
    metrics: TrendMetrics
    related_content: List[Dict[str, Any]]
    creator_opportunities: List[str]
    implementation_difficulty: str
    success_probability: float
    discovered_at: datetime
    updated_at: datetime


@dataclass
class TrendRecommendation:
    """Trend-based content recommendation."""
    recommendation_id: str
    trend_data: TrendData
    recommended_action: str
    content_idea: str
    platform_strategy: Dict[str, Any]
    timing_recommendation: str
    expected_performance: Dict[str, float]
    implementation_steps: List[str]
    success_indicators: List[str]
    risk_factors: List[str]
    priority_score: float


@dataclass
class TrendAnalysisReport:
    """Comprehensive trend analysis report."""
    report_id: str
    analysis_period: Dict[str, datetime]
    trending_topics: List[TrendData]
    emerging_trends: List[TrendData]
    declining_trends: List[TrendData]
    niche_opportunities: List[TrendData]
    platform_insights: Dict[str, Any]
    creator_recommendations: List[TrendRecommendation]
    market_outlook: Dict[str, Any]
    generated_at: datetime


class TrendAnalyzer:
    """
    Advanced AI-powered trend analyzer that monitors, detects, and analyzes
    content trends across multiple platforms and sources.
    """
    
    def __init__(self):
        """Initialize the trend analyzer with AI models and data sources."""
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.analytics_service = TrendAnalyticsService()
        self.social_media_apis = SocialMediaAPIManager()
        self.text_processor = TextProcessor()
        
        # AI models for trend detection
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.trend_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.cluster_analyzer = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Trend detection parameters
        self.trend_thresholds = self._initialize_trend_thresholds()
        
        # Platform-specific trend patterns
        self.platform_patterns = self._initialize_platform_patterns()
        
        # Historical trend database
        self.trend_history = defaultdict(list)
        
        # Real-time trend monitoring cache
        self.trend_cache = {}
        
    def _initialize_trend_thresholds(self) -> Dict[str, Any]:
        """Initialize thresholds for trend detection."""
        
        return {
            "viral_threshold": {
                "engagement_rate": 0.15,  # 15% engagement rate
                "growth_rate": 5.0,       # 500% growth in 24h
                "mention_velocity": 100,   # 100 mentions per hour
                "reach_multiplier": 10     # 10x normal reach
            },
            
            "emerging_threshold": {
                "engagement_rate": 0.08,  # 8% engagement rate
                "growth_rate": 2.0,       # 200% growth in 24h
                "mention_velocity": 25,    # 25 mentions per hour
                "reach_multiplier": 3      # 3x normal reach
            },
            
            "platform_thresholds": {
                "tiktok": {
                    "viral_views": 1000000,
                    "trending_likes": 50000,
                    "share_threshold": 5000
                },
                "instagram": {
                    "viral_views": 500000,
                    "trending_likes": 25000,
                    "save_threshold": 2000
                },
                "youtube": {
                    "viral_views": 1000000,
                    "trending_likes": 20000,
                    "comment_threshold": 1000
                },
                "twitter": {
                    "viral_impressions": 100000,
                    "retweet_threshold": 1000,
                    "mention_threshold": 500
                }
            },
            
            "trend_decay": {
                "hashtag_trends": 7,      # days
                "music_trends": 14,       # days
                "challenge_trends": 21,   # days
                "topic_trends": 30        # days
            }
        }
    
    def _initialize_platform_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific trend patterns."""
        
        return {
            "tiktok": {
                "trend_types": [TrendType.MUSIC_TREND, TrendType.CHALLENGE_TREND, TrendType.VIRAL_CONTENT],
                "discovery_signals": ["sound_usage", "effect_usage", "hashtag_adoption"],
                "virality_factors": ["completion_rate", "share_rate", "duet_rate"],
                "algorithm_boosters": ["early_engagement", "cross_platform_sharing"],
                "lifecycle": {"emergence": 1, "peak": 3, "decline": 7},  # days
                "content_formats": ["vertical_video", "short_form", "music_sync"]
            },
            
            "instagram": {
                "trend_types": [TrendType.VISUAL_TREND, TrendType.HASHTAG_TREND, TrendType.FORMAT_TREND],
                "discovery_signals": ["hashtag_volume", "story_mentions", "reel_engagement"],
                "virality_factors": ["save_rate", "share_rate", "story_reposts"],
                "algorithm_boosters": ["early_saves", "comment_engagement"],
                "lifecycle": {"emergence": 2, "peak": 7, "decline": 14},  # days
                "content_formats": ["square_images", "vertical_videos", "carousel_posts"]
            },
            
            "youtube": {
                "trend_types": [TrendType.TOPIC_TREND, TrendType.FORMAT_TREND, TrendType.VIRAL_CONTENT],
                "discovery_signals": ["search_volume", "comment_keywords", "thumbnail_patterns"],
                "virality_factors": ["watch_time", "subscription_rate", "comment_rate"],
                "algorithm_boosters": ["session_duration", "click_through_rate"],
                "lifecycle": {"emergence": 3, "peak": 14, "decline": 30},  # days
                "content_formats": ["long_form_video", "shorts", "live_streams"]
            },
            
            "twitter": {
                "trend_types": [TrendType.TOPIC_TREND, TrendType.HASHTAG_TREND, TrendType.NEWS_RELATED],
                "discovery_signals": ["hashtag_volume", "mention_frequency", "retweet_chains"],
                "virality_factors": ["retweet_rate", "quote_tweet_rate", "reply_rate"],
                "algorithm_boosters": ["engagement_velocity", "influencer_participation"],
                "lifecycle": {"emergence": 0.5, "peak": 1, "decline": 3},  # days
                "content_formats": ["text_posts", "images", "video_clips"]
            },
            
            "spotify": {
                "trend_types": [TrendType.MUSIC_TREND, TrendType.AUDIO_TREND],
                "discovery_signals": ["playlist_adds", "skip_rates", "repeat_listens"],
                "virality_factors": ["viral_coefficient", "cross_platform_usage"],
                "algorithm_boosters": ["playlist_placement", "radio_inclusion"],
                "lifecycle": {"emergence": 7, "peak": 30, "decline": 90},  # days
                "content_formats": ["audio_tracks", "podcasts", "playlists"]
            }
        }
    
    async def detect_trending_content(
        self, 
        platforms: List[TrendSource], 
        time_window: timedelta = timedelta(hours=24),
        trend_types: Optional[List[TrendType]] = None
    ) -> List[TrendData]:
        """Detect trending content across specified platforms."""
        
        detected_trends = []
        
        for platform in platforms:
            try:
                platform_trends = await self._analyze_platform_trends(
                    platform, time_window, trend_types
                )
                detected_trends.extend(platform_trends)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze trends on {platform.value}: {e}")
        
        # Deduplicate and merge cross-platform trends
        merged_trends = self._merge_cross_platform_trends(detected_trends)
        
        # Sort by trend strength and potential
        sorted_trends = sorted(
            merged_trends, 
            key=lambda t: t.metrics.virality_coefficient, 
            reverse=True
        )
        
        return sorted_trends
    
    async def _analyze_platform_trends(
        self, 
        platform: TrendSource, 
        time_window: timedelta,
        trend_types: Optional[List[TrendType]] = None
    ) -> List[TrendData]:
        """Analyze trends for a specific platform."""
        
        platform_trends = []
        
        # Fetch platform data
        platform_data = await self._fetch_platform_data(platform, time_window)
        
        if not platform_data:
            return platform_trends
        
        # Extract trend signals based on platform type
        trend_signals = self._extract_trend_signals(platform, platform_data)
        
        # Detect anomalies and emerging patterns
        anomalies = self._detect_anomalies(trend_signals)
        
        # Classify and structure trends
        for anomaly in anomalies:
            trend_data = await self._classify_and_structure_trend(
                platform, anomaly, platform_data, trend_types
            )
            
            if trend_data:
                platform_trends.append(trend_data)
        
        return platform_trends
    
    async def _fetch_platform_data(
        self, 
        platform: TrendSource, 
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Fetch data from platform APIs."""
        
        try:
            if platform == TrendSource.TIKTOK:
                return await self.social_media_apis.fetch_tiktok_trending_data(time_window)
            elif platform == TrendSource.INSTAGRAM:
                return await self.social_media_apis.fetch_instagram_trending_data(time_window)
            elif platform == TrendSource.YOUTUBE:
                return await self.social_media_apis.fetch_youtube_trending_data(time_window)
            elif platform == TrendSource.TWITTER:
                return await self.social_media_apis.fetch_twitter_trending_data(time_window)
            elif platform == TrendSource.SPOTIFY:
                return await self.social_media_apis.fetch_spotify_trending_data(time_window)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to fetch data from {platform.value}: {e}")
            return {}
    
    def _extract_trend_signals(
        self, 
        platform: TrendSource, 
        platform_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract trend signals from platform data."""
        
        signals = []
        pattern_config = self.platform_patterns.get(platform.value, {})
        discovery_signals = pattern_config.get("discovery_signals", [])
        
        if platform == TrendSource.TIKTOK:
            # Extract TikTok-specific signals
            sounds = platform_data.get("trending_sounds", [])
            for sound in sounds:
                signals.append({
                    "type": "sound_usage",
                    "content": sound,
                    "metrics": self._extract_tiktok_sound_metrics(sound)
                })
            
            hashtags = platform_data.get("trending_hashtags", [])
            for hashtag in hashtags:
                signals.append({
                    "type": "hashtag_trend",
                    "content": hashtag,
                    "metrics": self._extract_hashtag_metrics(hashtag, platform_data)
                })
            
            effects = platform_data.get("trending_effects", [])
            for effect in effects:
                signals.append({
                    "type": "effect_usage",
                    "content": effect,
                    "metrics": self._extract_effect_metrics(effect, platform_data)
                })
        
        elif platform == TrendSource.INSTAGRAM:
            # Extract Instagram-specific signals
            hashtags = platform_data.get("trending_hashtags", [])
            for hashtag in hashtags:
                signals.append({
                    "type": "hashtag_trend",
                    "content": hashtag,
                    "metrics": self._extract_hashtag_metrics(hashtag, platform_data)
                })
            
            reels = platform_data.get("viral_reels", [])
            for reel in reels:
                signals.append({
                    "type": "reel_trend",
                    "content": reel,
                    "metrics": self._extract_reel_metrics(reel)
                })
        
        elif platform == TrendSource.YOUTUBE:
            # Extract YouTube-specific signals
            videos = platform_data.get("trending_videos", [])
            for video in videos:
                signals.append({
                    "type": "video_trend",
                    "content": video,
                    "metrics": self._extract_video_metrics(video)
                })
            
            search_terms = platform_data.get("trending_searches", [])
            for term in search_terms:
                signals.append({
                    "type": "search_trend",
                    "content": term,
                    "metrics": self._extract_search_metrics(term, platform_data)
                })
        
        elif platform == TrendSource.TWITTER:
            # Extract Twitter-specific signals
            hashtags = platform_data.get("trending_hashtags", [])
            for hashtag in hashtags:
                signals.append({
                    "type": "hashtag_trend",
                    "content": hashtag,
                    "metrics": self._extract_hashtag_metrics(hashtag, platform_data)
                })
            
            topics = platform_data.get("trending_topics", [])
            for topic in topics:
                signals.append({
                    "type": "topic_trend",
                    "content": topic,
                    "metrics": self._extract_topic_metrics(topic, platform_data)
                })
        
        return signals
    
    def _extract_tiktok_sound_metrics(self, sound_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics for TikTok sound trends."""
        
        return {
            "usage_count": sound_data.get("video_count", 0),
            "growth_rate": sound_data.get("growth_24h", 0),
            "engagement_rate": sound_data.get("avg_engagement", 0),
            "virality_score": sound_data.get("virality_coefficient", 0)
        }
    
    def _extract_hashtag_metrics(
        self, 
        hashtag_data: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract metrics for hashtag trends."""
        
        return {
            "post_count": hashtag_data.get("post_count", 0),
            "reach": hashtag_data.get("total_reach", 0),
            "engagement_rate": hashtag_data.get("avg_engagement", 0),
            "growth_velocity": hashtag_data.get("growth_rate", 0),
            "user_participation": hashtag_data.get("unique_users", 0)
        }
    
    def _extract_effect_metrics(
        self, 
        effect_data: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract metrics for effect trends."""
        
        return {
            "usage_count": effect_data.get("usage_count", 0),
            "adoption_rate": effect_data.get("adoption_rate", 0),
            "retention_rate": effect_data.get("retention_rate", 0),
            "viral_potential": effect_data.get("viral_score", 0)
        }
    
    def _extract_reel_metrics(self, reel_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics for Instagram reel trends."""
        
        return {
            "views": reel_data.get("views", 0),
            "likes": reel_data.get("likes", 0),
            "shares": reel_data.get("shares", 0),
            "saves": reel_data.get("saves", 0),
            "engagement_rate": reel_data.get("engagement_rate", 0),
            "reach": reel_data.get("reach", 0)
        }
    
    def _extract_video_metrics(self, video_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics for YouTube video trends."""
        
        return {
            "views": video_data.get("views", 0),
            "likes": video_data.get("likes", 0),
            "comments": video_data.get("comments", 0),
            "watch_time": video_data.get("watch_time", 0),
            "subscriber_gain": video_data.get("new_subscribers", 0),
            "engagement_rate": video_data.get("engagement_rate", 0)
        }
    
    def _extract_search_metrics(
        self, 
        search_data: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract metrics for search trends."""
        
        return {
            "search_volume": search_data.get("volume", 0),
            "growth_rate": search_data.get("growth", 0),
            "competition": search_data.get("competition_score", 0),
            "interest_over_time": search_data.get("trend_score", 0)
        }
    
    def _extract_topic_metrics(
        self, 
        topic_data: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract metrics for topic trends."""
        
        return {
            "mention_count": topic_data.get("mentions", 0),
            "sentiment_score": topic_data.get("sentiment", 0),
            "influencer_participation": topic_data.get("influencer_count", 0),
            "geographic_spread": topic_data.get("geo_diversity", 0)
        }
    
    def _detect_anomalies(self, trend_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in trend signals using machine learning."""
        
        if not trend_signals:
            return []
        
        # Prepare data for anomaly detection
        feature_matrix = []
        signal_mapping = []
        
        for signal in trend_signals:
            metrics = signal.get("metrics", {})
            features = [
                metrics.get("usage_count", 0),
                metrics.get("growth_rate", 0),
                metrics.get("engagement_rate", 0),
                metrics.get("reach", 0),
                metrics.get("virality_score", 0)
            ]
            
            # Handle missing values
            features = [f if f is not None else 0 for f in features]
            
            feature_matrix.append(features)
            signal_mapping.append(signal)
        
        if not feature_matrix:
            return []
        
        # Scale features
        try:
            scaled_features = self.scaler.fit_transform(feature_matrix)
        except:
            # If scaling fails, use original features
            scaled_features = np.array(feature_matrix)
        
        # Detect anomalies
        try:
            anomaly_labels = self.anomaly_detector.fit_predict(scaled_features)
        except:
            # If anomaly detection fails, return all signals
            return trend_signals
        
        # Filter anomalies (label -1 indicates anomaly)
        anomalies = []
        for i, label in enumerate(anomaly_labels):
            if label == -1:  # Anomaly detected
                anomalies.append(signal_mapping[i])
        
        return anomalies
    
    async def _classify_and_structure_trend(
        self,
        platform: TrendSource,
        trend_signal: Dict[str, Any],
        platform_data: Dict[str, Any],
        trend_types: Optional[List[TrendType]] = None
    ) -> Optional[TrendData]:
        """Classify and structure trend data."""
        
        try:
            # Determine trend type
            trend_type = self._classify_trend_type(trend_signal, platform)
            
            if trend_types and trend_type not in trend_types:
                return None
            
            # Calculate comprehensive metrics
            metrics = await self._calculate_trend_metrics(trend_signal, platform_data)
            
            # Determine trend stage
            trend_stage = self._determine_trend_stage(metrics, platform)
            
            # Extract keywords and hashtags
            keywords, hashtags = self._extract_keywords_and_hashtags(trend_signal)
            
            # Generate trend description
            description = self._generate_trend_description(trend_signal, trend_type)
            
            # Find related content
            related_content = self._find_related_content(trend_signal, platform_data)
            
            # Generate creator opportunities
            opportunities = self._generate_creator_opportunities(trend_signal, trend_type)
            
            # Calculate implementation difficulty
            difficulty = self._calculate_implementation_difficulty(trend_type, metrics)
            
            # Calculate success probability
            success_prob = self._calculate_success_probability(metrics, trend_stage)
            
            trend_data = TrendData(
                trend_id=f"{platform.value}_{trend_type.value}_{int(datetime.now().timestamp())}",
                trend_type=trend_type,
                trend_stage=trend_stage,
                title=trend_signal.get("content", {}).get("title", "Untitled Trend"),
                description=description,
                keywords=keywords,
                hashtags=hashtags,
                source_platforms=[platform],
                metrics=metrics,
                related_content=related_content,
                creator_opportunities=opportunities,
                implementation_difficulty=difficulty,
                success_probability=success_prob,
                discovered_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Failed to classify trend: {e}")
            return None
    
    def _classify_trend_type(
        self, 
        trend_signal: Dict[str, Any], 
        platform: TrendSource
    ) -> TrendType:
        """Classify the type of trend based on signal characteristics."""
        
        signal_type = trend_signal.get("type", "")
        content = trend_signal.get("content", {})
        
        if "sound" in signal_type or "music" in signal_type:
            return TrendType.MUSIC_TREND
        elif "hashtag" in signal_type:
            return TrendType.HASHTAG_TREND
        elif "challenge" in signal_type or "effect" in signal_type:
            return TrendType.CHALLENGE_TREND
        elif "video" in signal_type or "reel" in signal_type:
            return TrendType.VIRAL_CONTENT
        elif "topic" in signal_type or "search" in signal_type:
            return TrendType.TOPIC_TREND
        elif "visual" in signal_type or "filter" in signal_type:
            return TrendType.VISUAL_TREND
        else:
            return TrendType.VIRAL_CONTENT  # Default classification
    
    async def _calculate_trend_metrics(
        self, 
        trend_signal: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> TrendMetrics:
        """Calculate comprehensive trend metrics."""
        
        signal_metrics = trend_signal.get("metrics", {})
        
        # Calculate engagement velocity
        engagement_rate = signal_metrics.get("engagement_rate", 0)
        growth_rate = signal_metrics.get("growth_rate", 0)
        engagement_velocity = engagement_rate * (1 + growth_rate)
        
        # Calculate reach acceleration
        reach = signal_metrics.get("reach", 0)
        usage_count = signal_metrics.get("usage_count", 1)
        reach_acceleration = reach / usage_count if usage_count > 0 else 0
        
        # Calculate mention frequency
        mention_frequency = signal_metrics.get("mention_count", 0)
        
        # Calculate sentiment score
        sentiment_score = signal_metrics.get("sentiment_score", 0.5)
        
        # Calculate participation rate
        unique_users = signal_metrics.get("user_participation", 0)
        total_reach = signal_metrics.get("reach", 1)
        participation_rate = unique_users / total_reach if total_reach > 0 else 0
        
        # Platform distribution (placeholder - would calculate from cross-platform data)
        platform_distribution = {"primary": 1.0}
        
        # Demographic spread (placeholder - would calculate from audience data)
        demographic_spread = {"primary_demo": 0.6, "secondary_demo": 0.4}
        
        # Calculate virality coefficient
        shares = signal_metrics.get("shares", 0)
        views = signal_metrics.get("views", 1)
        virality_coefficient = shares / views if views > 0 else 0
        
        # Predict peak timing (simplified calculation)
        peak_prediction = datetime.now(timezone.utc) + timedelta(days=3)
        
        # Estimate longevity
        trend_type_longevity = {
            TrendType.VIRAL_CONTENT: 7,
            TrendType.HASHTAG_TREND: 14,
            TrendType.MUSIC_TREND: 30,
            TrendType.CHALLENGE_TREND: 21,
            TrendType.TOPIC_TREND: 45
        }
        longevity_estimate = trend_type_longevity.get(
            self._classify_trend_type(trend_signal, None), 14
        )
        
        return TrendMetrics(
            engagement_velocity=engagement_velocity,
            reach_acceleration=reach_acceleration,
            mention_frequency=mention_frequency,
            sentiment_score=sentiment_score,
            participation_rate=participation_rate,
            platform_distribution=platform_distribution,
            demographic_spread=demographic_spread,
            virality_coefficient=virality_coefficient,
            peak_prediction=peak_prediction,
            longevity_estimate=longevity_estimate
        )
    
    def _determine_trend_stage(
        self, 
        metrics: TrendMetrics, 
        platform: TrendSource
    ) -> TrendStage:
        """Determine the current stage of the trend lifecycle."""
        
        engagement_velocity = metrics.engagement_velocity
        virality_coefficient = metrics.virality_coefficient
        
        # Get platform-specific thresholds
        thresholds = self.trend_thresholds.get("platform_thresholds", {}).get(
            platform.value, {}
        )
        
        if engagement_velocity > 0.2 and virality_coefficient > 0.1:
            return TrendStage.PEAK
        elif engagement_velocity > 0.1 and virality_coefficient > 0.05:
            return TrendStage.GROWING
        elif engagement_velocity > 0.05:
            return TrendStage.EMERGING
        elif engagement_velocity < 0.02:
            return TrendStage.DECLINING
        else:
            return TrendStage.GROWING  # Default stage
    
    def _extract_keywords_and_hashtags(
        self, 
        trend_signal: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Extract keywords and hashtags from trend signal."""
        
        content = trend_signal.get("content", {})
        
        # Extract hashtags
        hashtags = []
        text_content = str(content.get("description", "")) + " " + str(content.get("title", ""))
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text_content)
        
        # Extract keywords using text processing
        keywords = []
        if text_content:
            # Remove hashtags and clean text
            clean_text = re.sub(hashtag_pattern, '', text_content)
            
            # Use TextBlob for basic keyword extraction
            blob = TextBlob(clean_text)
            keywords = [word.lower() for word in blob.noun_phrases][:10]
        
        return keywords, hashtags
    
    def _generate_trend_description(
        self, 
        trend_signal: Dict[str, Any], 
        trend_type: TrendType
    ) -> str:
        """Generate a descriptive summary of the trend."""
        
        content = trend_signal.get("content", {})
        metrics = trend_signal.get("metrics", {})
        
        base_description = f"A {trend_type.value.replace('_', ' ')} "
        
        if trend_type == TrendType.MUSIC_TREND:
            description = base_description + f"featuring audio content with {metrics.get('usage_count', 0)} uses"
        elif trend_type == TrendType.HASHTAG_TREND:
            description = base_description + f"with {metrics.get('post_count', 0)} posts and growing engagement"
        elif trend_type == TrendType.CHALLENGE_TREND:
            description = base_description + f"gaining momentum with {metrics.get('participation_rate', 0):.1%} participation rate"
        elif trend_type == TrendType.VIRAL_CONTENT:
            description = base_description + f"achieving {metrics.get('views', 0)} views with high engagement"
        else:
            description = base_description + "showing significant growth and engagement"
        
        return description
    
    def _find_related_content(
        self, 
        trend_signal: Dict[str, Any], 
        platform_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find content related to the trend."""
        
        related_content = []
        
        # This would involve more sophisticated content matching
        # For now, return a simplified structure
        content = trend_signal.get("content", {})
        
        if content:
            related_content.append({
                "content_id": content.get("id", "unknown"),
                "title": content.get("title", "Related Content"),
                "engagement": content.get("engagement", 0),
                "relevance_score": 0.8
            })
        
        return related_content
    
    def _generate_creator_opportunities(
        self, 
        trend_signal: Dict[str, Any], 
        trend_type: TrendType
    ) -> List[str]:
        """Generate specific opportunities for creators based on the trend."""
        
        opportunities = []
        
        if trend_type == TrendType.MUSIC_TREND:
            opportunities.extend([
                "Create content using the trending audio",
                "Develop dance or movement content to the music",
                "Create reaction or review content",
                "Collaborate with other creators using the same sound"
            ])
        
        elif trend_type == TrendType.HASHTAG_TREND:
            opportunities.extend([
                "Create original content with the trending hashtag",
                "Start a conversation around the topic",
                "Share personal experiences related to the trend",
                "Create educational content about the trend"
            ])
        
        elif trend_type == TrendType.CHALLENGE_TREND:
            opportunities.extend([
                "Participate in the challenge with your unique twist",
                "Create a tutorial for the challenge",
                "React to other creators' challenge attempts",
                "Start a variation or spin-off of the challenge"
            ])
        
        elif trend_type == TrendType.VIRAL_CONTENT:
            opportunities.extend([
                "Create similar content with your unique perspective",
                "React to or comment on the viral content",
                "Create educational breakdown of why it went viral",
                "Develop content that builds on the viral theme"
            ])
        
        else:
            opportunities.extend([
                "Create content that taps into the trending topic",
                "Share your expertise related to the trend",
                "Engage with the community around this trend",
                "Create content that provides value within the trend"
            ])
        
        return opportunities
    
    def _calculate_implementation_difficulty(
        self, 
        trend_type: TrendType, 
        metrics: TrendMetrics
    ) -> str:
        """Calculate the difficulty of implementing trend-based content."""
        
        difficulty_scores = {
            TrendType.HASHTAG_TREND: 1,      # Easy - just use hashtag
            TrendType.MUSIC_TREND: 2,        # Medium - need to create content with audio
            TrendType.TOPIC_TREND: 2,        # Medium - need relevant expertise
            TrendType.VIRAL_CONTENT: 3,      # Hard - need to recreate viral elements
            TrendType.CHALLENGE_TREND: 3,    # Hard - need to execute challenge well
            TrendType.VISUAL_TREND: 4,       # Very Hard - need design/editing skills
            TrendType.FORMAT_TREND: 4        # Very Hard - need to master new format
        }
        
        base_difficulty = difficulty_scores.get(trend_type, 2)
        
        # Adjust based on trend saturation
        if metrics.participation_rate > 0.1:  # High participation = more competition
            base_difficulty += 1
        
        difficulty_levels = ["easy", "medium", "hard", "very_hard", "expert"]
        difficulty_index = min(base_difficulty, len(difficulty_levels) - 1)
        
        return difficulty_levels[difficulty_index]
    
    def _calculate_success_probability(
        self, 
        metrics: TrendMetrics, 
        trend_stage: TrendStage
    ) -> float:
        """Calculate the probability of success when participating in the trend."""
        
        base_probability = 0.5
        
        # Adjust based on trend stage
        stage_multipliers = {
            TrendStage.EMERGING: 0.8,   # Good opportunity, less competition
            TrendStage.GROWING: 1.0,    # Best opportunity
            TrendStage.PEAK: 0.6,       # High competition
            TrendStage.DECLINING: 0.3,  # Poor timing
            TrendStage.EXPIRED: 0.1     # Very poor timing
        }
        
        probability = base_probability * stage_multipliers.get(trend_stage, 0.5)
        
        # Adjust based on engagement velocity
        if metrics.engagement_velocity > 0.15:
            probability *= 1.2
        elif metrics.engagement_velocity < 0.05:
            probability *= 0.8
        
        # Adjust based on virality coefficient
        if metrics.virality_coefficient > 0.1:
            probability *= 1.1
        
        return min(1.0, max(0.0, probability))
    
    def _merge_cross_platform_trends(self, trends: List[TrendData]) -> List[TrendData]:
        """Merge similar trends detected across multiple platforms."""
        
        if not trends:
            return trends
        
        merged_trends = []
        processed_trends = set()
        
        for i, trend in enumerate(trends):
            if i in processed_trends:
                continue
            
            # Find similar trends
            similar_trends = [trend]
            for j, other_trend in enumerate(trends[i+1:], i+1):
                if j in processed_trends:
                    continue
                
                similarity = self._calculate_trend_similarity(trend, other_trend)
                if similarity > 0.7:  # High similarity threshold
                    similar_trends.append(other_trend)
                    processed_trends.add(j)
            
            # Merge similar trends
            merged_trend = self._merge_similar_trends(similar_trends)
            merged_trends.append(merged_trend)
            processed_trends.add(i)
        
        return merged_trends
    
    def _calculate_trend_similarity(self, trend1: TrendData, trend2: TrendData) -> float:
        """Calculate similarity between two trends."""
        
        similarity_score = 0.0
        
        # Type similarity
        if trend1.trend_type == trend2.trend_type:
            similarity_score += 0.3
        
        # Keyword similarity
        common_keywords = set(trend1.keywords) & set(trend2.keywords)
        total_keywords = set(trend1.keywords) | set(trend2.keywords)
        if total_keywords:
            keyword_similarity = len(common_keywords) / len(total_keywords)
            similarity_score += 0.4 * keyword_similarity
        
        # Hashtag similarity
        common_hashtags = set(trend1.hashtags) & set(trend2.hashtags)
        total_hashtags = set(trend1.hashtags) | set(trend2.hashtags)
        if total_hashtags:
            hashtag_similarity = len(common_hashtags) / len(total_hashtags)
            similarity_score += 0.3 * hashtag_similarity
        
        return similarity_score
    
    def _merge_similar_trends(self, trends: List[TrendData]) -> TrendData:
        """Merge a list of similar trends into one comprehensive trend."""
        
        if len(trends) == 1:
            return trends[0]
        
        primary_trend = trends[0]
        
        # Merge source platforms
        all_platforms = []
        for trend in trends:
            all_platforms.extend(trend.source_platforms)
        merged_platforms = list(set(all_platforms))
        
        # Merge keywords and hashtags
        all_keywords = []
        all_hashtags = []
        for trend in trends:
            all_keywords.extend(trend.keywords)
            all_hashtags.extend(trend.hashtags)
        
        merged_keywords = list(set(all_keywords))
        merged_hashtags = list(set(all_hashtags))
        
        # Merge related content
        all_related_content = []
        for trend in trends:
            all_related_content.extend(trend.related_content)
        
        # Average metrics (simplified approach)
        avg_engagement_velocity = np.mean([t.metrics.engagement_velocity for t in trends])
        avg_reach_acceleration = np.mean([t.metrics.reach_acceleration for t in trends])
        avg_virality_coefficient = np.mean([t.metrics.virality_coefficient for t in trends])
        
        merged_metrics = TrendMetrics(
            engagement_velocity=avg_engagement_velocity,
            reach_acceleration=avg_reach_acceleration,
            mention_frequency=sum(t.metrics.mention_frequency for t in trends),
            sentiment_score=np.mean([t.metrics.sentiment_score for t in trends]),
            participation_rate=np.mean([t.metrics.participation_rate for t in trends]),
            platform_distribution=primary_trend.metrics.platform_distribution,
            demographic_spread=primary_trend.metrics.demographic_spread,
            virality_coefficient=avg_virality_coefficient,
            peak_prediction=primary_trend.metrics.peak_prediction,
            longevity_estimate=max(t.metrics.longevity_estimate for t in trends)
        )
        
        # Create merged trend
        merged_trend = TrendData(
            trend_id=f"merged_{primary_trend.trend_id}",
            trend_type=primary_trend.trend_type,
            trend_stage=primary_trend.trend_stage,
            title=f"Cross-Platform: {primary_trend.title}",
            description=f"Multi-platform trend spanning {len(merged_platforms)} platforms",
            keywords=merged_keywords,
            hashtags=merged_hashtags,
            source_platforms=merged_platforms,
            metrics=merged_metrics,
            related_content=all_related_content,
            creator_opportunities=primary_trend.creator_opportunities,
            implementation_difficulty=primary_trend.implementation_difficulty,
            success_probability=np.mean([t.success_probability for t in trends]),
            discovered_at=min(t.discovered_at for t in trends),
            updated_at=datetime.now(timezone.utc)
        )
        
        return merged_trend
        """Initialize the trend analyzer."""
        self.text_processor = TextProcessor()
        self.social_media_apis = SocialMediaAPIManager()
        self.analytics_service = TrendAnalyticsService()
        
        # ML models for trend detection and analysis
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.trend_classifier = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.clusterer = DBSCAN(eps=0.3, min_samples=5)
        
        # Text analysis tools
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        
        # Trend detection parameters
        self.trend_thresholds = {
            'viral_velocity': 2.0,      # 2x normal engagement rate
            'mention_spike': 5.0,       # 5x normal mention frequency
            'reach_acceleration': 3.0,   # 3x normal reach growth
            'participation_threshold': 0.1  # 10% participation rate
        }
        
        # Platform-specific trend characteristics
        self.platform_characteristics = self._initialize_platform_characteristics()
        
        # Trend detection history
        self.detected_trends = {}
        self.trend_performance_history = defaultdict(list)
        
        # Load and train models
        self._load_and_train_models()
        
        logger.info("Trend analyzer initialized successfully")
    
    def _initialize_platform_characteristics(self) -> Dict[TrendSource, Dict[str, Any]]:
        """Initialize platform-specific trend characteristics."""
        
        return {
            TrendSource.TIKTOK: {
                'trend_duration': {'min': 3, 'max': 14},  # days
                'viral_threshold': 100000,  # views
                'engagement_threshold': 0.08,  # 8% engagement rate
                'trend_indicators': ['sounds', 'effects', 'hashtags', 'dances'],
                'peak_hours': ['18:00', '19:00', '20:00', '21:00'],
                'audience_age': [13, 34],
                'content_formats': ['short_video', 'challenge', 'duet']
            },
            TrendSource.INSTAGRAM: {
                'trend_duration': {'min': 7, 'max': 30},
                'viral_threshold': 50000,  # likes
                'engagement_threshold': 0.05,  # 5% engagement rate
                'trend_indicators': ['hashtags', 'filters', 'stickers', 'formats'],
                'peak_hours': ['11:00', '13:00', '17:00', '19:00'],
                'audience_age': [18, 44],
                'content_formats': ['image', 'carousel', 'reel', 'story']
            },
            TrendSource.YOUTUBE: {
                'trend_duration': {'min': 14, 'max': 90},
                'viral_threshold': 1000000,  # views
                'engagement_threshold': 0.04,  # 4% engagement rate
                'trend_indicators': ['topics', 'formats', 'thumbnails', 'titles'],
                'peak_hours': ['18:00', '19:00', '20:00'],
                'audience_age': [16, 54],
                'content_formats': ['long_video', 'short_video', 'live_stream']
            },
            TrendSource.TWITTER: {
                'trend_duration': {'min': 1, 'max': 7},
                'viral_threshold': 10000,  # retweets
                'engagement_threshold': 0.02,  # 2% engagement rate
                'trend_indicators': ['hashtags', 'topics', 'mentions', 'events'],
                'peak_hours': ['12:00', '15:00', '17:00'],
                'audience_age': [25, 54],
                'content_formats': ['text_post', 'image', 'thread']
            },
            TrendSource.SPOTIFY: {
                'trend_duration': {'min': 7, 'max': 60},
                'viral_threshold': 100000,  # streams
                'engagement_threshold': 0.6,  # 60% completion rate
                'trend_indicators': ['genres', 'artists', 'playlists', 'moods'],
                'peak_hours': ['07:00', '17:00', '22:00'],
                'audience_age': [16, 44],
                'content_formats': ['track', 'album', 'playlist']
            }
        }
    
    def _load_and_train_models(self):
        """Load historical data and train ML models for trend detection."""
        try:
            # Generate synthetic training data for trend detection
            n_samples = 20000
            
            # Features: engagement_rate, mention_frequency, reach_growth, etc.
            features = np.random.rand(n_samples, 15)
            
            # Add some anomalies (trends) to training data
            anomaly_indices = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
            features[anomaly_indices] *= np.random.uniform(2, 5, (len(anomaly_indices), 15))
            
            # Train anomaly detector for trend detection
            self.anomaly_detector.fit(features)
            
            # Train trend classifier
            trend_labels = np.random.choice([0, 1, 2, 3, 4], n_samples)  # 5 trend types
            self.trend_classifier.fit(features, trend_labels)
            
            # Fit scaler
            self.scaler.fit(features)
            
            logger.info("Trend analysis ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train trend analysis models: {e}")
            # Continue with default models
    
    async def detect_trending_content(
        self,
        platforms: List[TrendSource],
        timeframe: timedelta = timedelta(hours=24),
        min_engagement: float = 0.02
    ) -> List[TrendData]:
        """
        Detect trending content across specified platforms.
        
        Args:
            platforms: List of platforms to monitor
            timeframe: Time window for trend detection
            min_engagement: Minimum engagement rate threshold
            
        Returns:
            List of detected trends
        """
        
        detected_trends = []
        
        try:
            # Collect data from each platform
            platform_data = {}
            for platform in platforms:
                data = await self._collect_platform_data(platform, timeframe)
                platform_data[platform] = data
            
            # Analyze each platform's data for trends
            for platform, data in platform_data.items():
                if not data:
                    continue
                
                platform_trends = await self._analyze_platform_trends(
                    platform, data, min_engagement
                )
                detected_trends.extend(platform_trends)
            
            # Cross-platform trend correlation
            correlated_trends = await self._find_cross_platform_trends(detected_trends)
            
            # Filter and rank trends
            filtered_trends = await self._filter_and_rank_trends(
                correlated_trends, platforms
            )
            
            # Update trend detection history
            self._update_trend_history(filtered_trends)
            
            logger.info(f"Detected {len(filtered_trends)} trends across {len(platforms)} platforms")
            return filtered_trends
            
        except Exception as e:
            logger.error(f"Failed to detect trending content: {e}")
            return []
    
    async def _collect_platform_data(
        self, platform: TrendSource, timeframe: timedelta
    ) -> List[Dict[str, Any]]:
        """Collect data from a specific platform for trend analysis."""
        
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timeframe
            
            # Platform-specific data collection
            if platform == TrendSource.TIKTOK:
                data = await self.social_media_apis.get_tiktok_trending_data(
                    start_time, end_time
                )
            elif platform == TrendSource.INSTAGRAM:
                data = await self.social_media_apis.get_instagram_trending_data(
                    start_time, end_time
                )
            elif platform == TrendSource.YOUTUBE:
                data = await self.social_media_apis.get_youtube_trending_data(
                    start_time, end_time
                )
            elif platform == TrendSource.TWITTER:
                data = await self.social_media_apis.get_twitter_trending_data(
                    start_time, end_time
                )
            elif platform == TrendSource.SPOTIFY:
                data = await self.social_media_apis.get_spotify_trending_data(
                    start_time, end_time
                )
            else:
                data = []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to collect data from {platform.value}: {e}")
            return []
    
    async def _analyze_platform_trends(
        self,
        platform: TrendSource,
        data: List[Dict[str, Any]],
        min_engagement: float
    ) -> List[TrendData]:
        """Analyze platform-specific data to identify trends."""
        
        trends = []
        platform_chars = self.platform_characteristics.get(platform, {})
        
        if not data or not platform_chars:
            return trends
        
        try:
            # Extract features for trend detection
            features_data = []
            content_items = []
            
            for item in data:
                features = self._extract_trend_features(item, platform_chars)
                if features is not None:
                    features_data.append(features)
                    content_items.append(item)
            
            if not features_data:
                return trends
            
            features_array = np.array(features_data)
            
            # Detect anomalies (potential trends)
            anomaly_scores = self.anomaly_detector.decision_function(features_array)
            anomaly_threshold = np.percentile(anomaly_scores, 90)  # Top 10% as potential trends
            
            anomaly_indices = np.where(anomaly_scores >= anomaly_threshold)[0]
            
            # Analyze each potential trend
            for idx in anomaly_indices:
                item = content_items[idx]
                
                # Skip if engagement is below threshold
                engagement_rate = self._calculate_engagement_rate(item, platform)
                if engagement_rate < min_engagement:
                    continue
                
                # Create trend data
                trend = await self._create_trend_data(item, platform, features_data[idx])
                if trend:
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends for {platform.value}: {e}")
            return []
    
    def _extract_trend_features(
        self, item: Dict[str, Any], platform_chars: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """Extract features from content item for trend detection."""
        
        try:
            features = []
            
            # Engagement metrics
            likes = item.get('likes', 0)
            shares = item.get('shares', 0)
            comments = item.get('comments', 0)
            views = item.get('views', 0)
            
            # Calculate engagement rate
            engagement_rate = (likes + shares + comments) / max(views, 1)
            features.append(engagement_rate)
            
            # Growth velocity
            growth_rate = item.get('growth_rate', 0)
            features.append(growth_rate)
            
            # Time-based features
            created_at = item.get('created_at')
            if created_at:
                hours_ago = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
                features.append(min(hours_ago, 24))  # Normalize to 24 hours
            else:
                features.append(24)
            
            # Content features
            text_content = item.get('caption', '') + ' ' + item.get('description', '')
            
            # Text length
            features.append(len(text_content.split()))
            
            # Hashtag count
            hashtag_count = len(re.findall(r'#\w+', text_content))
            features.append(hashtag_count)
            
            # Mention count
            mention_count = len(re.findall(r'@\w+', text_content))
            features.append(mention_count)
            
            # Sentiment analysis
            if text_content.strip():
                sentiment = TextBlob(text_content).sentiment
                features.extend([sentiment.polarity, sentiment.subjectivity])
            else:
                features.extend([0.0, 0.0])
            
            # Platform-specific features
            viral_threshold = platform_chars.get('viral_threshold', 10000)
            features.append(min(views / viral_threshold, 5.0))  # Normalize viral score
            
            # Content type indicators
            has_video = 1 if item.get('has_video', False) else 0
            has_audio = 1 if item.get('has_audio', False) else 0
            has_image = 1 if item.get('has_image', False) else 0
            features.extend([has_video, has_audio, has_image])
            
            # Creator metrics
            creator_followers = item.get('creator_followers', 0)
            features.append(min(creator_followers / 100000, 10.0))  # Normalize follower count
            
            # Pad to fixed length (15 features)
            while len(features) < 15:
                features.append(0.0)
            
            return np.array(features[:15])
            
        except Exception as e:
            logger.error(f"Failed to extract trend features: {e}")
            return None
    
    def _calculate_engagement_rate(
        self, item: Dict[str, Any], platform: TrendSource
    ) -> float:
        """Calculate engagement rate for content item."""
        
        likes = item.get('likes', 0)
        shares = item.get('shares', 0)
        comments = item.get('comments', 0)
        views = item.get('views', 0)
        
        if platform == TrendSource.YOUTUBE:
            # YouTube engagement rate calculation
            total_engagement = likes + comments + shares
            return total_engagement / max(views, 1)
        
        elif platform == TrendSource.INSTAGRAM:
            # Instagram engagement rate calculation
            total_engagement = likes + comments + shares
            return total_engagement / max(views, 1)
        
        elif platform == TrendSource.TIKTOK:
            # TikTok engagement rate calculation
            total_engagement = likes + shares + comments
            return total_engagement / max(views, 1)
        
        elif platform == TrendSource.TWITTER:
            # Twitter engagement rate calculation
            total_engagement = likes + shares + comments  # retweets + replies
            impressions = item.get('impressions', views)
            return total_engagement / max(impressions, 1)
        
        else:
            # Generic calculation
            total_engagement = likes + shares + comments
            return total_engagement / max(views, 1)
    
    async def _create_trend_data(
        self,
        item: Dict[str, Any],
        platform: TrendSource,
        features: np.ndarray
    ) -> Optional[TrendData]:
        """Create comprehensive trend data from content item."""
        
        try:
            # Extract trend characteristics
            trend_type = self._classify_trend_type(item, platform)
            trend_stage = self._determine_trend_stage(item, features)
            
            # Extract keywords and hashtags
            text_content = item.get('caption', '') + ' ' + item.get('description', '')
            keywords = await self._extract_keywords(text_content)
            hashtags = re.findall(r'#(\w+)', text_content)
            
            # Calculate metrics
            metrics = await self._calculate_trend_metrics(item, platform, features)
            
            # Generate trend ID
            trend_id = f"{platform.value}_{int(datetime.now().timestamp())}_{hash(str(item))}"
            
            # Create trend data
            trend = TrendData(
                trend_id=trend_id,
                trend_type=trend_type,
                trend_stage=trend_stage,
                title=self._generate_trend_title(item, keywords),
                description=self._generate_trend_description(item, trend_type),
                keywords=keywords,
                hashtags=hashtags,
                source_platforms=[platform],
                metrics=metrics,
                related_content=[item],
                creator_opportunities=await self._identify_creator_opportunities(
                    trend_type, item, platform
                ),
                implementation_difficulty=self._assess_implementation_difficulty(
                    trend_type, item
                ),
                success_probability=self._calculate_success_probability(
                    features, metrics
                ),
                discovered_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Failed to create trend data: {e}")
            return None
    
    def _classify_trend_type(
        self, item: Dict[str, Any], platform: TrendSource
    ) -> TrendType:
        """Classify the type of trend based on content analysis."""
        
        # Analyze content characteristics
        has_music = item.get('has_audio', False) or 'music' in item.get('tags', [])
        has_challenge = any(word in item.get('caption', '').lower() 
                          for word in ['challenge', 'trend', 'try'])
        has_hashtag_focus = len(re.findall(r'#\w+', item.get('caption', ''))) > 3
        
        text_content = item.get('caption', '') + ' ' + item.get('description', '')
        
        # Classification logic
        if has_music and platform in [TrendSource.TIKTOK, TrendSource.INSTAGRAM]:
            return TrendType.MUSIC_TREND
        elif has_challenge:
            return TrendType.CHALLENGE_TREND
        elif has_hashtag_focus:
            return TrendType.HASHTAG_TREND
        elif item.get('has_video', False) and item.get('views', 0) > 100000:
            return TrendType.VIRAL_CONTENT
        elif len(text_content.split()) > 50:
            return TrendType.TOPIC_TREND
        elif item.get('has_image', False):
            return TrendType.VISUAL_TREND
        else:
            return TrendType.FORMAT_TREND
    
    def _determine_trend_stage(
        self, item: Dict[str, Any], features: np.ndarray
    ) -> TrendStage:
        """Determine the current stage of the trend lifecycle."""
        
        # Analyze temporal patterns
        created_at = item.get('created_at')
        if not created_at:
            return TrendStage.EMERGING
        
        hours_ago = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
        growth_rate = item.get('growth_rate', 0)
        engagement_rate = features[0] if len(features) > 0 else 0
        
        # Stage determination logic
        if hours_ago < 6 and growth_rate > 2.0:
            return TrendStage.EMERGING
        elif hours_ago < 24 and engagement_rate > 0.05:
            return TrendStage.GROWING
        elif hours_ago < 72 and engagement_rate > 0.03:
            return TrendStage.PEAK
        elif hours_ago < 168:  # 1 week
            return TrendStage.DECLINING
        else:
            return TrendStage.EXPIRED
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text content."""
        
        if not text.strip():
            return []
        
        try:
            # Use text processor to extract keywords
            keywords = await self.text_processor.extract_keywords(text, max_keywords=10)
            
            # Filter out common words and keep meaningful terms
            meaningful_keywords = [
                kw for kw in keywords 
                if len(kw) > 3 and not kw.lower() in ['this', 'that', 'with', 'from']
            ]
            
            return meaningful_keywords[:10]
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            return []
    
    async def _calculate_trend_metrics(
        self,
        item: Dict[str, Any],
        platform: TrendSource,
        features: np.ndarray
    ) -> TrendMetrics:
        """Calculate comprehensive metrics for the trend."""
        
        # Basic metrics from item
        views = item.get('views', 0)
        likes = item.get('likes', 0)
        shares = item.get('shares', 0)
        comments = item.get('comments', 0)
        
        # Calculate derived metrics
        engagement_velocity = features[0] if len(features) > 0 else 0  # engagement rate
        reach_acceleration = item.get('growth_rate', 0)
        mention_frequency = item.get('mention_count', 0)
        
        # Sentiment analysis
        text_content = item.get('caption', '') + ' ' + item.get('description', '')
        if text_content.strip():
            sentiment = TextBlob(text_content).sentiment
            sentiment_score = sentiment.polarity
        else:
            sentiment_score = 0.0
        
        # Platform-specific calculations
        platform_chars = self.platform_characteristics.get(platform, {})
        viral_threshold = platform_chars.get('viral_threshold', 10000)
        
        participation_rate = min(shares / max(views, 1), 1.0)
        virality_coefficient = min(views / viral_threshold, 10.0)
        
        # Predict peak and longevity
        peak_prediction = self._predict_trend_peak(item, features)
        longevity_estimate = self._estimate_trend_longevity(platform, features)
        
        return TrendMetrics(
            engagement_velocity=engagement_velocity,
            reach_acceleration=reach_acceleration,
            mention_frequency=mention_frequency,
            sentiment_score=sentiment_score,
            participation_rate=participation_rate,
            platform_distribution={platform.value: 1.0},
            demographic_spread=self._analyze_demographic_spread(item),
            virality_coefficient=virality_coefficient,
            peak_prediction=peak_prediction,
            longevity_estimate=longevity_estimate
        )
    
    def _predict_trend_peak(
        self, item: Dict[str, Any], features: np.ndarray
    ) -> Optional[datetime]:
        """Predict when the trend will reach its peak."""
        
        try:
            created_at = item.get('created_at')
            if not created_at:
                return None
            
            growth_rate = item.get('growth_rate', 0)
            engagement_rate = features[0] if len(features) > 0 else 0
            
            # Simple peak prediction based on growth patterns
            if growth_rate > 3.0:
                # Fast-growing trend, peak in 12-24 hours
                peak_hours = 12 + (engagement_rate * 12)
            elif growth_rate > 1.5:
                # Moderate growth, peak in 1-3 days
                peak_hours = 24 + (engagement_rate * 48)
            else:
                # Slow growth, peak in 3-7 days
                peak_hours = 72 + (engagement_rate * 96)
            
            peak_time = created_at + timedelta(hours=peak_hours)
            return peak_time
            
        except Exception as e:
            logger.error(f"Failed to predict trend peak: {e}")
            return None
    
    def _estimate_trend_longevity(
        self, platform: TrendSource, features: np.ndarray
    ) -> int:
        """Estimate how long the trend will remain relevant."""
        
        platform_chars = self.platform_characteristics.get(platform, {})
        base_duration = platform_chars.get('trend_duration', {'min': 7, 'max': 30})
        
        engagement_rate = features[0] if len(features) > 0 else 0
        
        # Adjust based on engagement strength
        if engagement_rate > 0.1:
            # High engagement trends last longer
            longevity = base_duration['max']
        elif engagement_rate > 0.05:
            # Medium engagement
            longevity = (base_duration['min'] + base_duration['max']) // 2
        else:
            # Low engagement
            longevity = base_duration['min']
        
        return longevity
    
    def _analyze_demographic_spread(self, item: Dict[str, Any]) -> Dict[str, float]:
        """Analyze demographic distribution of trend engagement."""
        
        # This would typically analyze actual demographic data
        # For now, return default distribution
        return {
            'age_13_17': 0.2,
            'age_18_24': 0.3,
            'age_25_34': 0.25,
            'age_35_44': 0.15,
            'age_45_plus': 0.1
        }
    
    async def _find_cross_platform_trends(
        self, trends: List[TrendData]
    ) -> List[TrendData]:
        """Identify trends that appear across multiple platforms."""
        
        # Group trends by similar keywords and hashtags
        trend_groups = defaultdict(list)
        
        for trend in trends:
            # Create signature based on keywords and hashtags
            signature_words = set(trend.keywords + trend.hashtags)
            
            # Find matching groups
            matched = False
            for existing_signature, group in trend_groups.items():
                overlap = len(signature_words & existing_signature)
                if overlap >= 2:  # At least 2 common words
                    group.append(trend)
                    matched = True
                    break
            
            if not matched:
                trend_groups[frozenset(signature_words)] = [trend]
        
        # Merge cross-platform trends
        merged_trends = []
        
        for group in trend_groups.values():
            if len(group) == 1:
                merged_trends.append(group[0])
            else:
                # Merge multiple platform trends
                merged_trend = await self._merge_platform_trends(group)
                merged_trends.append(merged_trend)
        
        return merged_trends
    
    async def _merge_platform_trends(self, trends: List[TrendData]) -> TrendData:
        """Merge trends from multiple platforms into a single trend."""
        
        # Use the trend with highest engagement as base
        base_trend = max(trends, key=lambda t: t.metrics.engagement_velocity)
        
        # Combine data from all trends
        all_platforms = []
        all_related_content = []
        all_keywords = set()
        all_hashtags = set()
        
        for trend in trends:
            all_platforms.extend(trend.source_platforms)
            all_related_content.extend(trend.related_content)
            all_keywords.update(trend.keywords)
            all_hashtags.update(trend.hashtags)
        
        # Calculate combined metrics
        avg_engagement = statistics.mean([t.metrics.engagement_velocity for t in trends])
        avg_reach = statistics.mean([t.metrics.reach_acceleration for t in trends])
        total_mentions = sum(t.metrics.mention_frequency for t in trends)
        
        # Create platform distribution
        platform_distribution = {}
        for platform in all_platforms:
            platform_distribution[platform.value] = all_platforms.count(platform) / len(all_platforms)
        
        # Update metrics
        merged_metrics = TrendMetrics(
            engagement_velocity=avg_engagement,
            reach_acceleration=avg_reach,
            mention_frequency=total_mentions,
            sentiment_score=statistics.mean([t.metrics.sentiment_score for t in trends]),
            participation_rate=statistics.mean([t.metrics.participation_rate for t in trends]),
            platform_distribution=platform_distribution,
            demographic_spread=base_trend.metrics.demographic_spread,
            virality_coefficient=max(t.metrics.virality_coefficient for t in trends),
            peak_prediction=base_trend.metrics.peak_prediction,
            longevity_estimate=max(t.metrics.longevity_estimate for t in trends)
        )
        
        # Create merged trend
        merged_trend = TrendData(
            trend_id=f"cross_platform_{int(datetime.now().timestamp())}",
            trend_type=base_trend.trend_type,
            trend_stage=base_trend.trend_stage,
            title=f"Cross-Platform: {base_trend.title}",
            description=f"Multi-platform trend across {len(set(all_platforms))} platforms",
            keywords=list(all_keywords)[:10],
            hashtags=list(all_hashtags)[:15],
            source_platforms=list(set(all_platforms)),
            metrics=merged_metrics,
            related_content=all_related_content,
            creator_opportunities=base_trend.creator_opportunities,
            implementation_difficulty=base_trend.implementation_difficulty,
            success_probability=min(1.0, base_trend.success_probability * 1.2),  # Cross-platform bonus
            discovered_at=min(t.discovered_at for t in trends),
            updated_at=datetime.now(timezone.utc)
        )
        
        return merged_trend


class ContentTrendEngine:
    """
    Content trend engine that provides trend-based recommendations
    and content strategy guidance for creators.
    """
    
    def __init__(self):
        """Initialize the content trend engine."""
        self.trend_analyzer = TrendAnalyzer()
        self.recommendation_history = {}
        logger.info("Content trend engine initialized")
    
    async def generate_trend_recommendations(
        self,
        creator_id: str,
        creator_niche: str,
        platforms: List[TrendSource],
        content_goals: List[str]
    ) -> List[TrendRecommendation]:
        """
        Generate trend-based content recommendations for creator.
        
        Args:
            creator_id: Creator identifier
            creator_niche: Creator's content niche
            platforms: Platforms creator is active on
            content_goals: Creator's content goals
            
        Returns:
            List of trend-based recommendations
        """
        
        try:
            # Detect current trends
            current_trends = await self.trend_analyzer.detect_trending_content(platforms)
            
            # Filter trends relevant to creator's niche
            relevant_trends = await self._filter_relevant_trends(
                current_trends, creator_niche, platforms
            )
            
            # Generate recommendations for each relevant trend
            recommendations = []
            for trend in relevant_trends:
                recommendation = await self._create_trend_recommendation(
                    creator_id, trend, platforms, content_goals
                )
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Store recommendation history
            self.recommendation_history[creator_id] = recommendations
            
            logger.info(f"Generated {len(recommendations)} trend recommendations for {creator_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate trend recommendations: {e}")
            return []
    
    async def _filter_relevant_trends(
        self,
        trends: List[TrendData],
        creator_niche: str,
        platforms: List[TrendSource]
    ) -> List[TrendData]:
        """Filter trends relevant to creator's niche and platforms."""
        
        relevant_trends = []
        
        for trend in trends:
            # Check platform relevance
            platform_overlap = set(trend.source_platforms) & set(platforms)
            if not platform_overlap:
                continue
            
            # Check niche relevance
            niche_relevance = await self._calculate_niche_relevance(
                trend, creator_niche
            )
            
            if niche_relevance > 0.3:  # 30% relevance threshold
                relevant_trends.append(trend)
        
        return relevant_trends
    
    async def _calculate_niche_relevance(
        self, trend: TrendData, creator_niche: str
    ) -> float:
        """Calculate how relevant a trend is to creator's niche."""
        
        # Define niche keywords
        niche_keywords = {
            'music': ['music', 'song', 'artist', 'album', 'concert', 'performance'],
            'fitness': ['workout', 'exercise', 'fitness', 'health', 'gym', 'training'],
            'cooking': ['recipe', 'food', 'cooking', 'kitchen', 'chef', 'meal'],
            'fashion': ['style', 'fashion', 'outfit', 'clothing', 'trend', 'designer'],
            'tech': ['technology', 'tech', 'gadget', 'software', 'app', 'digital'],
            'lifestyle': ['life', 'daily', 'routine', 'tips', 'advice', 'personal'],
            'gaming': ['game', 'gaming', 'player', 'stream', 'esports', 'console']
        }
        
        niche_words = niche_keywords.get(creator_niche.lower(), [])
        if not niche_words:
            return 0.5  # Default relevance for unknown niches
        
        # Check keyword overlap
        trend_words = set(word.lower() for word in trend.keywords + trend.hashtags)
        niche_word_set = set(niche_words)
        
        overlap = len(trend_words & niche_word_set)
        relevance = overlap / max(len(niche_word_set), 1)
        
        return min(1.0, relevance)
    
    async def _create_trend_recommendation(
        self,
        creator_id: str,
        trend: TrendData,
        platforms: List[TrendSource],
        content_goals: List[str]
    ) -> Optional[TrendRecommendation]:
        """Create a trend-based content recommendation."""
        
        try:
            # Generate content idea based on trend
            content_idea = await self._generate_content_idea(trend, platforms)
            
            # Create platform strategy
            platform_strategy = await self._create_platform_strategy(trend, platforms)
            
            # Determine timing
            timing_recommendation = self._determine_optimal_timing(trend)
            
            # Predict performance
            expected_performance = await self._predict_trend_performance(
                trend, platforms, content_goals
            )
            
            # Generate implementation steps
            implementation_steps = self._generate_implementation_steps(
                trend, content_idea, platforms
            )
            
            # Identify success indicators and risks
            success_indicators = self._identify_success_indicators(trend)
            risk_factors = self._identify_risk_factors(trend)
            
            # Calculate priority score
            priority_score = self._calculate_recommendation_priority(
                trend, content_goals, expected_performance
            )
            
            recommendation = TrendRecommendation(
                recommendation_id=f"{creator_id}_{trend.trend_id}_{int(datetime.now().timestamp())}",
                trend_data=trend,
                recommended_action=self._get_recommended_action(trend),
                content_idea=content_idea,
                platform_strategy=platform_strategy,
                timing_recommendation=timing_recommendation,
                expected_performance=expected_performance,
                implementation_steps=implementation_steps,
                success_indicators=success_indicators,
                risk_factors=risk_factors,
                priority_score=priority_score
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to create trend recommendation: {e}")
            return None
    
    async def _generate_content_idea(
        self, trend: TrendData, platforms: List[TrendSource]
    ) -> str:
        """Generate specific content idea based on trend."""
        
        trend_type = trend.trend_type
        keywords = trend.keywords[:3]  # Top 3 keywords
        hashtags = trend.hashtags[:5]  # Top 5 hashtags
        
        if trend_type == TrendType.MUSIC_TREND:
            return f"Create content using trending audio elements related to {', '.join(keywords)}. Incorporate hashtags: {', '.join(hashtags)}"
        
        elif trend_type == TrendType.CHALLENGE_TREND:
            return f"Participate in or create a variation of the trending challenge featuring {', '.join(keywords)}. Use hashtags: {', '.join(hashtags)}"
        
        elif trend_type == TrendType.VIRAL_CONTENT:
            return f"Create content inspired by viral elements: {', '.join(keywords)}. Add your unique perspective and use relevant hashtags: {', '.join(hashtags)}"
        
        elif trend_type == TrendType.TOPIC_TREND:
            return f"Create educational or commentary content about trending topic: {', '.join(keywords)}. Provide unique insights and use hashtags: {', '.join(hashtags)}"
        
        elif trend_type == TrendType.HASHTAG_TREND:
            return f"Create content specifically targeting trending hashtags: {', '.join(hashtags)}. Focus on keywords: {', '.join(keywords)}"
        
        else:
            return f"Create content incorporating trending elements: {', '.join(keywords)} with hashtags: {', '.join(hashtags)}"
    
    async def _create_platform_strategy(
        self, trend: TrendData, platforms: List[TrendSource]
    ) -> Dict[str, Any]:
        """Create platform-specific strategy for trend participation."""
        
        strategy = {}
        
        for platform in platforms:
            if platform in trend.source_platforms:
                platform_chars = self.trend_analyzer.platform_characteristics.get(platform, {})
                
                strategy[platform.value] = {
                    'content_format': self._get_optimal_format(trend, platform),
                    'posting_time': platform_chars.get('peak_hours', ['12:00'])[0],
                    'hashtag_strategy': self._create_hashtag_strategy(trend, platform),
                    'engagement_tactics': self._get_engagement_tactics(trend, platform),
                    'adaptation_tips': self._get_platform_adaptation_tips(trend, platform)
                }
        
        return strategy
    
    def _get_optimal_format(self, trend: TrendData, platform: TrendSource) -> str:
        """Get optimal content format for trend on specific platform."""
        
        platform_chars = self.trend_analyzer.platform_characteristics.get(platform, {})
        formats = platform_chars.get('content_formats', ['video'])
        
        # Match trend type to format
        if trend.trend_type == TrendType.MUSIC_TREND:
            if 'short_video' in formats:
                return 'short_video'
            elif 'video' in formats:
                return 'video'
        elif trend.trend_type == TrendType.CHALLENGE_TREND:
            if 'short_video' in formats:
                return 'short_video'
        elif trend.trend_type == TrendType.VISUAL_TREND:
            if 'image' in formats:
                return 'image'
            elif 'carousel' in formats:
                return 'carousel'
        
        return formats[0] if formats else 'video'
    
    def _create_hashtag_strategy(self, trend: TrendData, platform: TrendSource) -> Dict[str, Any]:
        """Create hashtag strategy for platform."""
        
        platform_chars = self.trend_analyzer.platform_characteristics.get(platform, {})
        
        # Get trending hashtags from trend
        trending_hashtags = trend.hashtags[:5]
        
        # Add platform-specific hashtags
        if platform == TrendSource.TIKTOK:
            additional_hashtags = ['fyp', 'viral', 'trending']
        elif platform == TrendSource.INSTAGRAM:
            additional_hashtags = ['explore', 'reels', 'trending']
        elif platform == TrendSource.YOUTUBE:
            additional_hashtags = ['trending', 'viral']
        else:
            additional_hashtags = ['trending']
        
        return {
            'trending_hashtags': trending_hashtags,
            'platform_hashtags': additional_hashtags,
            'niche_hashtags': [],  # Would be filled based on creator niche
            'total_recommended': min(len(trending_hashtags) + len(additional_hashtags), 10)
        }
    
    def _determine_optimal_timing(self, trend: TrendData) -> str:
        """Determine optimal timing for trend participation."""
        
        if trend.trend_stage == TrendStage.EMERGING:
            return "Act immediately - trend is just starting to gain momentum"
        elif trend.trend_stage == TrendStage.GROWING:
            return "Act within 24 hours - trend is gaining traction"
        elif trend.trend_stage == TrendStage.PEAK:
            return "Act now but differentiate - trend is at peak popularity"
        elif trend.trend_stage == TrendStage.DECLINING:
            return "Consider unique angle - trend popularity is declining"
        else:
            return "Consider if trend aligns with your brand - trend may be past peak"
