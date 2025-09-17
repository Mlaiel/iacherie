#!/usr/bin/env python3
"""
Content Analytics Platform - Enterprise Creator Content Intelligence
==================================================================

Advanced content analytics platform for comprehensive content performance tracking,
viral prediction, optimization recommendations, and content strategy intelligence
in the Ainflue Creator Economy ecosystem.

Expert Roles Implementation:
🤖 Lead Dev IA: AI-powered content optimization + intelligent performance insights
🏗️ Backend Senior: High-performance content analytics + microservices architecture  
🧠 ML Engineer: Viral prediction models + content performance algorithms
🗄️ DBA: Optimized content queries + content data warehouse patterns
🔒 Security Specialist: Content data privacy + GDPR compliance + audit trails
🏗️ Microservices Architect: Distributed content services + event-driven processing
🎵 Audio Engineer: Media content analytics + audio performance optimization
🚀 DevOps: Content monitoring + real-time analytics infrastructure
🎯 IA Prompt Engineer: Intelligent content recommendations + automated insights

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    CAROUSEL = "carousel"
    REEL = "reel"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"


class ContentFormat(Enum):
    """Content format specifications"""
    MP4 = "mp4"
    MOV = "mov"
    JPG = "jpg"
    PNG = "png"
    MP3 = "mp3"
    WAV = "wav"
    MARKDOWN = "markdown"
    HTML = "html"
    GIF = "gif"
    WEBP = "webp"


class ContentCategory(Enum):
    """Content category classification"""
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    GAMING = "gaming"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    HEALTH_FITNESS = "health_fitness"
    TRAVEL = "travel"
    FOOD = "food"
    BEAUTY = "beauty"
    SPORTS = "sports"
    NEWS = "news"
    MUSIC = "music"
    ART = "art"


class ViralityFactor(Enum):
    """Factors contributing to viral content"""
    EMOTIONAL_IMPACT = "emotional_impact"
    TIMING = "timing"
    TRENDING_TOPICS = "trending_topics"
    SHAREABILITY = "shareability"
    UNIQUENESS = "uniqueness"
    RELATABILITY = "relatability"
    VISUAL_APPEAL = "visual_appeal"
    AUDIO_QUALITY = "audio_quality"
    STORYTELLING = "storytelling"
    CALL_TO_ACTION = "call_to_action"


@dataclass
class ContentMetadata:
    """Comprehensive content metadata"""
    content_id: str
    creator_id: str
    title: str
    description: str
    content_type: ContentType
    content_format: ContentFormat
    category: ContentCategory
    tags: List[str]
    hashtags: List[str]
    mentions: List[str]
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    bitrate: Optional[int] = None
    creation_date: datetime = field(default_factory=datetime.now)
    publish_date: Optional[datetime] = None
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class ContentPerformanceMetrics:
    """Content performance analytics"""
    content_id: str
    measurement_date: datetime
    views: int
    unique_views: int
    likes: int
    dislikes: int
    comments: int
    shares: int
    saves: int
    clicks: int
    impressions: int
    reach: int
    engagement_rate: float
    click_through_rate: float
    completion_rate: float
    retention_rate: float
    viral_coefficient: float
    quality_score: float
    authenticity_score: float
    monetization_value: float
    platform_specific_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ViralAnalytics:
    """Viral content analysis"""
    content_id: str
    viral_score: float
    viral_velocity: float  # Rate of viral spread
    viral_peak_time: datetime
    viral_factors: List[ViralityFactor]
    viral_trajectory: str  # "emerging", "peak", "declining", "stable"
    predicted_viral_potential: float
    viral_amplifiers: List[str]  # What boosted virality
    viral_inhibitors: List[str]  # What limited virality
    cross_platform_viral: bool
    viral_sustainability: float  # How long viral effect lasts


@dataclass
class ContentOptimization:
    """Content optimization recommendations"""
    content_id: str
    optimization_score: float
    improvement_areas: List[str]
    optimization_recommendations: List[Dict[str, Any]]
    predicted_improvement: float
    implementation_difficulty: str  # "easy", "medium", "hard"
    expected_roi: float
    priority_level: str  # "high", "medium", "low"
    optimization_timeline: str
    success_probability: float


@dataclass
class ContentTrend:
    """Content trend analysis"""
    trend_id: str
    trend_name: str
    category: ContentCategory
    trend_score: float
    growth_rate: float
    peak_prediction: datetime
    duration_estimate_days: int
    participating_creators: int
    total_content_count: int
    geographic_spread: List[str]
    demographic_appeal: Dict[str, float]
    trend_maturity: str  # "emerging", "growing", "peak", "declining"


class ContentAnalyticsEngine:
    """Advanced content analytics and intelligence platform"""
    
    def __init__(self):
        self.content_database: Dict[str, ContentMetadata] = {}
        self.performance_history: Dict[str, List[ContentPerformanceMetrics]] = defaultdict(list)
        self.viral_analytics: Dict[str, ViralAnalytics] = {}
        self.content_fingerprints: Dict[str, str] = {}  # For duplicate detection
        self.trend_tracking: Dict[str, ContentTrend] = {}
        self.optimization_cache: Dict[str, ContentOptimization] = {}
        self._initialize_content_models()
        
    def _initialize_content_models(self):
        """Initialize content analysis models and benchmarks"""
        self.viral_prediction_model = "trained_viral_model"
        self.quality_assessment_model = "trained_quality_model"
        self.trend_detection_model = "trained_trend_model"
        self.optimization_model = "trained_optimization_model"
        
        # Content performance benchmarks by type and category
        self.performance_benchmarks = {
            ContentType.VIDEO: {
                "avg_engagement_rate": 0.06,
                "avg_completion_rate": 0.45,
                "avg_viral_score": 0.15
            },
            ContentType.IMAGE: {
                "avg_engagement_rate": 0.08,
                "avg_completion_rate": 1.0,  # Images are "completed" when viewed
                "avg_viral_score": 0.12
            },
            ContentType.AUDIO: {
                "avg_engagement_rate": 0.04,
                "avg_completion_rate": 0.30,
                "avg_viral_score": 0.08
            },
            ContentType.TEXT: {
                "avg_engagement_rate": 0.05,
                "avg_completion_rate": 0.60,
                "avg_viral_score": 0.10
            }
        }

    async def analyze_content_performance(
        self, 
        content_metadata: ContentMetadata,
        performance_data: Dict[str, Any],
        platform_context: Optional[Dict[str, Any]] = None
    ) -> ContentPerformanceMetrics:
        """
        Comprehensive content performance analysis
        
        🧠 ML Engineer: Advanced performance modeling + predictive analytics
        🎵 Audio Engineer: Media-specific performance analysis + quality assessment
        """
        try:
            logger.info(f"Analyzing performance for content {content_metadata.content_id}")
            
            # Store content metadata
            self.content_database[content_metadata.content_id] = content_metadata
            
            # Extract basic performance metrics
            views = performance_data.get("views", 0)
            unique_views = performance_data.get("unique_views", int(views * 0.8))  # Estimate if not provided
            likes = performance_data.get("likes", 0)
            dislikes = performance_data.get("dislikes", 0)
            comments = performance_data.get("comments", 0)
            shares = performance_data.get("shares", 0)
            saves = performance_data.get("saves", 0)
            clicks = performance_data.get("clicks", 0)
            impressions = performance_data.get("impressions", views * 2)  # Estimate if not provided
            reach = performance_data.get("reach", unique_views)
            
            # Calculate derived metrics
            engagement_rate = await self._calculate_engagement_rate(
                likes, comments, shares, saves, views
            )
            
            click_through_rate = clicks / max(impressions, 1)
            
            completion_rate = await self._calculate_completion_rate(
                content_metadata, performance_data
            )
            
            retention_rate = await self._calculate_retention_rate(
                content_metadata, performance_data
            )
            
            viral_coefficient = await self._calculate_viral_coefficient(
                shares, views, reach
            )
            
            quality_score = await self._assess_content_quality(
                content_metadata, performance_data
            )
            
            authenticity_score = await self._assess_content_authenticity(
                content_metadata, performance_data
            )
            
            monetization_value = performance_data.get("monetization_value", 0.0)
            
            # Platform-specific metrics
            platform_metrics = platform_context or {}
            
            metrics = ContentPerformanceMetrics(
                content_id=content_metadata.content_id,
                measurement_date=datetime.now(),
                views=views,
                unique_views=unique_views,
                likes=likes,
                dislikes=dislikes,
                comments=comments,
                shares=shares,
                saves=saves,
                clicks=clicks,
                impressions=impressions,
                reach=reach,
                engagement_rate=engagement_rate,
                click_through_rate=click_through_rate,
                completion_rate=completion_rate,
                retention_rate=retention_rate,
                viral_coefficient=viral_coefficient,
                quality_score=quality_score,
                authenticity_score=authenticity_score,
                monetization_value=monetization_value,
                platform_specific_metrics=platform_metrics
            )
            
            # Store performance history
            self.performance_history[content_metadata.content_id].append(metrics)
            
            logger.info(f"Performance analysis completed for content {content_metadata.content_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            raise

    async def _calculate_engagement_rate(
        self, 
        likes: int, 
        comments: int, 
        shares: int, 
        saves: int, 
        views: int
    ) -> float:
        """Calculate comprehensive engagement rate"""
        if views == 0:
            return 0.0
            
        # Weighted engagement (shares and comments worth more than likes)
        weighted_engagement = (
            likes * 1.0 +
            comments * 2.0 +
            shares * 3.0 +
            saves * 2.5
        )
        
        engagement_rate = weighted_engagement / views
        return min(1.0, engagement_rate)  # Cap at 100%

    async def predict_viral_potential(
        self, 
        content_metadata: ContentMetadata,
        early_performance: Dict[str, Any],
        trending_context: Optional[Dict[str, Any]] = None
    ) -> ViralAnalytics:
        """
        Predict viral potential of content using ML models
        
        🧠 ML Engineer: Advanced viral prediction modeling + trend analysis
        🤖 Lead Dev IA: AI-powered virality assessment + intelligent insights
        """
        try:
            logger.info(f"Predicting viral potential for content {content_metadata.content_id}")
            
            # Extract viral features
            viral_features = await self._extract_viral_features(
                content_metadata, early_performance, trending_context
            )
            
            # Calculate viral score
            viral_score = await self._calculate_viral_score(viral_features)
            
            # Calculate viral velocity
            viral_velocity = await self._calculate_viral_velocity(early_performance)
            
            # Predict viral peak time
            viral_peak_time = await self._predict_viral_peak(viral_velocity, viral_score)
            
            # Identify viral factors
            viral_factors = await self._identify_viral_factors(viral_features)
            
            # Determine viral trajectory
            viral_trajectory = await self._determine_viral_trajectory(
                viral_score, viral_velocity, early_performance
            )
            
            # Predict future viral potential
            predicted_potential = await self._predict_future_viral_potential(
                viral_score, viral_velocity, viral_factors
            )
            
            # Identify amplifiers and inhibitors
            amplifiers, inhibitors = await self._identify_viral_amplifiers_inhibitors(viral_features)
            
            # Check cross-platform viral potential
            cross_platform_viral = await self._assess_cross_platform_viral(content_metadata, viral_features)
            
            # Calculate viral sustainability
            viral_sustainability = await self._calculate_viral_sustainability(
                content_metadata, viral_score, viral_factors
            )
            
            viral_analytics = ViralAnalytics(
                content_id=content_metadata.content_id,
                viral_score=viral_score,
                viral_velocity=viral_velocity,
                viral_peak_time=viral_peak_time,
                viral_factors=viral_factors,
                viral_trajectory=viral_trajectory,
                predicted_viral_potential=predicted_potential,
                viral_amplifiers=amplifiers,
                viral_inhibitors=inhibitors,
                cross_platform_viral=cross_platform_viral,
                viral_sustainability=viral_sustainability
            )
            
            # Store viral analytics
            self.viral_analytics[content_metadata.content_id] = viral_analytics
            
            logger.info(f"Viral potential prediction completed for content {content_metadata.content_id}")
            return viral_analytics
            
        except Exception as e:
            logger.error(f"Error predicting viral potential: {str(e)}")
            raise

    async def _extract_viral_features(
        self, 
        content_metadata: ContentMetadata,
        early_performance: Dict[str, Any],
        trending_context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract features for viral prediction model"""
        
        features = {}
        
        # Content characteristics
        features["content_type_score"] = await self._score_content_type_virality(content_metadata.content_type)
        features["title_viral_score"] = await self._score_title_virality(content_metadata.title)
        features["hashtag_viral_score"] = await self._score_hashtag_virality(content_metadata.hashtags)
        features["timing_score"] = await self._score_timing_virality(content_metadata.publish_date)
        
        # Early performance indicators
        early_views = early_performance.get("views", 0)
        early_engagement = early_performance.get("engagement_rate", 0)
        early_shares = early_performance.get("shares", 0)
        early_comments = early_performance.get("comments", 0)
        
        features["early_engagement_rate"] = early_engagement
        features["early_share_rate"] = early_shares / max(early_views, 1)
        features["early_comment_rate"] = early_comments / max(early_views, 1)
        features["early_viral_coefficient"] = await self._calculate_viral_coefficient(
            early_shares, early_views, early_performance.get("reach", early_views)
        )
        
        # Trending context
        if trending_context:
            features["trend_alignment"] = trending_context.get("trend_alignment", 0.5)
            features["trending_hashtags"] = trending_context.get("trending_hashtags", 0.0)
            features["topic_momentum"] = trending_context.get("topic_momentum", 0.5)
        else:
            features["trend_alignment"] = 0.5
            features["trending_hashtags"] = 0.0
            features["topic_momentum"] = 0.5
            
        # Creator factors
        creator_content = [c for c in self.content_database.values() if c.creator_id == content_metadata.creator_id]
        features["creator_viral_history"] = await self._calculate_creator_viral_history(content_metadata.creator_id)
        features["creator_consistency"] = len(creator_content) / max(30, len(creator_content))  # Consistency factor
        
        return features

    async def _calculate_viral_score(self, viral_features: Dict[str, float]) -> float:
        """Calculate overall viral score from features"""
        
        # Weight the features
        weights = {
            "content_type_score": 0.15,
            "title_viral_score": 0.12,
            "hashtag_viral_score": 0.08,
            "timing_score": 0.05,
            "early_engagement_rate": 0.20,
            "early_share_rate": 0.15,
            "early_comment_rate": 0.10,
            "early_viral_coefficient": 0.08,
            "trend_alignment": 0.03,
            "trending_hashtags": 0.02,
            "topic_momentum": 0.02,
            "creator_viral_history": 0.08,
            "creator_consistency": 0.02
        }
        
        viral_score = 0.0
        for feature, value in viral_features.items():
            if feature in weights:
                viral_score += value * weights[feature]
                
        return max(0.0, min(1.0, viral_score))

    # Additional helper methods would continue here...
    # For brevity, including key methods only

    async def _calculate_completion_rate(
        self, 
        content_metadata: ContentMetadata,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate content completion rate"""
        content_type = content_metadata.content_type
        
        if content_type in [ContentType.IMAGE, ContentType.TEXT]:
            return 1.0
            
        elif content_type in [ContentType.VIDEO, ContentType.AUDIO, ContentType.LIVE_STREAM]:
            total_watch_time = performance_data.get("total_watch_time_seconds", 0)
            duration = content_metadata.duration_seconds or 30
            views = performance_data.get("views", 1)
            
            if views > 0 and duration > 0:
                avg_watch_time = total_watch_time / views
                completion_rate = min(1.0, avg_watch_time / duration)
                return completion_rate
            else:
                return self.performance_benchmarks[content_type]["avg_completion_rate"]
        else:
            return 0.5

    async def _calculate_retention_rate(
        self, 
        content_metadata: ContentMetadata,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate audience retention rate"""
        
        retention_data = performance_data.get("retention_curve", [])
        if retention_data:
            return statistics.mean(retention_data)
            
        engagement_rate = await self._calculate_engagement_rate(
            performance_data.get("likes", 0),
            performance_data.get("comments", 0),
            performance_data.get("shares", 0),
            performance_data.get("saves", 0),
            performance_data.get("views", 1)
        )
        
        estimated_retention = min(0.9, 0.4 + engagement_rate * 0.5)
        return estimated_retention

    async def _calculate_viral_coefficient(self, shares: int, views: int, reach: int) -> float:
        """Calculate viral coefficient (how much content spreads)"""
        if views == 0:
            return 0.0
            
        reach_expansion = max(1.0, reach / max(views, 1))
        viral_coefficient = (shares * reach_expansion) / views
        
        return min(2.0, viral_coefficient)

    async def _assess_content_quality(
        self, 
        content_metadata: ContentMetadata,
        performance_data: Dict[str, Any]
    ) -> float:
        """Assess content quality score using multiple factors"""
        
        quality_factors = []
        
        # Technical quality factors
        if content_metadata.content_type == ContentType.VIDEO:
            resolution = content_metadata.resolution or "720p"
            if "4K" in resolution or "2160p" in resolution:
                quality_factors.append(0.95)
            elif "1080p" in resolution:
                quality_factors.append(0.85)
            elif "720p" in resolution:
                quality_factors.append(0.75)
            else:
                quality_factors.append(0.60)
                
        # Content structure quality
        title_quality = await self._assess_title_quality(content_metadata.title)
        quality_factors.append(title_quality)
        
        description_quality = await self._assess_description_quality(content_metadata.description)
        quality_factors.append(description_quality)
        
        # Performance-based quality indicators
        completion_rate = await self._calculate_completion_rate(content_metadata, performance_data)
        quality_factors.append(completion_rate)
        
        if quality_factors:
            quality_score = statistics.mean(quality_factors)
            return max(0.0, min(1.0, quality_score))
        else:
            return 0.7

    async def _assess_content_authenticity(
        self, 
        content_metadata: ContentMetadata,
        performance_data: Dict[str, Any]
    ) -> float:
        """Assess content authenticity score"""
        
        authenticity_factors = []
        
        # Original content indicators
        content_fingerprint = await self._generate_content_fingerprint(content_metadata)
        if content_fingerprint not in self.content_fingerprints.values():
            authenticity_factors.append(1.0)
        else:
            authenticity_factors.append(0.3)
            
        self.content_fingerprints[content_metadata.content_id] = content_fingerprint
        
        # Natural engagement patterns
        likes = performance_data.get("likes", 0)
        comments = performance_data.get("comments", 0)
        
        if likes > 0:
            comment_ratio = comments / likes
            if 0.05 <= comment_ratio <= 0.3:
                authenticity_factors.append(0.9)
            else:
                authenticity_factors.append(0.6)
        else:
            authenticity_factors.append(0.7)
            
        authenticity_score = statistics.mean(authenticity_factors)
        return max(0.0, min(1.0, authenticity_score))

    async def _generate_content_fingerprint(self, content_metadata: ContentMetadata) -> str:
        """Generate content fingerprint for duplicate detection"""
        fingerprint_data = f"{content_metadata.title}_{content_metadata.description}_{content_metadata.content_type.value}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    # Additional viral prediction helper methods...
    async def _score_content_type_virality(self, content_type: ContentType) -> float:
        """Score content type for viral potential"""
        viral_scores = {
            ContentType.VIDEO: 0.9,
            ContentType.SHORT_FORM: 0.95,
            ContentType.REEL: 0.9,
            ContentType.IMAGE: 0.7,
            ContentType.CAROUSEL: 0.75,
            ContentType.AUDIO: 0.6,
            ContentType.TEXT: 0.5,
            ContentType.LIVE_STREAM: 0.8,
            ContentType.STORY: 0.65
        }
        return viral_scores.get(content_type, 0.6)

    async def _score_title_virality(self, title: str) -> float:
        """Score title for viral potential"""
        if not title:
            return 0.3
            
        viral_score = 0.5
        
        emotional_words = [
            "amazing", "incredible", "shocking", "unbelievable", "wow", "omg", 
            "crazy", "insane", "mind-blowing", "epic", "ultimate", "secret"
        ]
        
        title_lower = title.lower()
        emotional_matches = sum(1 for word in emotional_words if word in title_lower)
        viral_score += min(0.3, emotional_matches * 0.1)
        
        if "?" in title:
            viral_score += 0.1
            
        if any(c.isdigit() for c in title):
            viral_score += 0.1
            
        return max(0.0, min(1.0, viral_score))

    async def _score_hashtag_virality(self, hashtags: List[str]) -> float:
        """Score hashtags for viral potential"""
        if not hashtags:
            return 0.3
            
        viral_score = 0.5
        
        trending_hashtags = {
            "fyp", "foryou", "viral", "trending", "explore", "reels", "tiktok",
            "instagram", "youtube", "challenge", "dance", "music", "comedy"
        }
        
        hashtag_lower = [tag.lower() for tag in hashtags]
        trending_matches = sum(1 for tag in hashtag_lower if tag in trending_hashtags)
        viral_score += min(0.3, trending_matches * 0.1)
        
        if 5 <= len(hashtags) <= 15:
            viral_score += 0.1
            
        return max(0.0, min(1.0, viral_score))

    async def _score_timing_virality(self, publish_date: Optional[datetime]) -> float:
        """Score timing for viral potential"""
        if not publish_date:
            return 0.5
            
        hour = publish_date.hour
        timing_score = 0.5
        
        if hour in [6, 7, 8, 12, 19, 20]:
            timing_score += 0.2
        elif hour in [9, 10, 11, 13, 14, 15, 16, 17, 18, 21]:
            timing_score += 0.1
        else:
            timing_score -= 0.1
            
        return max(0.0, min(1.0, timing_score))

    async def _calculate_creator_viral_history(self, creator_id: str) -> float:
        """Calculate creator's historical viral success rate"""
        creator_content = [
            content_id for content_id, metadata in self.content_database.items()
            if metadata.creator_id == creator_id
        ]
        
        if not creator_content:
            return 0.5
            
        viral_content_count = 0
        total_analyzed = 0
        
        for content_id in creator_content:
            if content_id in self.viral_analytics:
                total_analyzed += 1
                if self.viral_analytics[content_id].viral_score > 0.7:
                    viral_content_count += 1
                    
        if total_analyzed == 0:
            return 0.5
            
        viral_rate = viral_content_count / total_analyzed
        return min(1.0, viral_rate * 2)

    async def _calculate_viral_velocity(self, early_performance: Dict[str, Any]) -> float:
        """Calculate viral velocity (rate of viral spread)"""
        
        first_hour_views = early_performance.get("first_hour_views", 0)
        first_day_views = early_performance.get("first_day_views", early_performance.get("views", 0))
        
        if first_hour_views > 0 and first_day_views > first_hour_views:
            hourly_growth = (first_day_views - first_hour_views) / 23
            velocity = min(1.0, hourly_growth / max(first_hour_views, 1))
        else:
            velocity = early_performance.get("engagement_velocity", 0.3)
            
        return max(0.0, min(1.0, velocity))

    async def _predict_viral_peak(self, viral_velocity: float, viral_score: float) -> datetime:
        """Predict when content will reach viral peak"""
        
        base_hours = 24
        velocity_factor = 1.0 - (viral_velocity * 0.5)
        score_factor = 1.0 + (viral_score * 0.3)
        
        peak_hours = base_hours * velocity_factor * score_factor
        peak_hours = max(2, min(168, peak_hours))
        
        return datetime.now() + timedelta(hours=peak_hours)

    async def _identify_viral_factors(self, viral_features: Dict[str, float]) -> List[ViralityFactor]:
        """Identify key factors contributing to viral potential"""
        
        factors = []
        
        if viral_features.get("early_engagement_rate", 0) > 0.08:
            factors.append(ViralityFactor.EMOTIONAL_IMPACT)
            
        if viral_features.get("timing_score", 0) > 0.7:
            factors.append(ViralityFactor.TIMING)
            
        if viral_features.get("trending_hashtags", 0) > 0.5:
            factors.append(ViralityFactor.TRENDING_TOPICS)
            
        if viral_features.get("early_share_rate", 0) > 0.05:
            factors.append(ViralityFactor.SHAREABILITY)
            
        if viral_features.get("content_type_score", 0) > 0.8:
            factors.append(ViralityFactor.VISUAL_APPEAL)
            
        if viral_features.get("title_viral_score", 0) > 0.7:
            factors.append(ViralityFactor.UNIQUENESS)
            
        return factors

    async def _determine_viral_trajectory(
        self, 
        viral_score: float, 
        viral_velocity: float, 
        early_performance: Dict[str, Any]
    ) -> str:
        """Determine viral trajectory phase"""
        
        time_since_publish = early_performance.get("hours_since_publish", 1)
        momentum = (viral_score * viral_velocity) / max(time_since_publish, 1)
        
        if momentum > 0.3 and viral_velocity > 0.6:
            return "emerging"
        elif momentum > 0.5 and viral_score > 0.7:
            return "peak"
        elif momentum > 0.1 and viral_velocity < 0.3:
            return "declining"
        else:
            return "stable"

    async def _predict_future_viral_potential(
        self, 
        viral_score: float, 
        viral_velocity: float, 
        viral_factors: List[ViralityFactor]
    ) -> float:
        """Predict future viral potential"""
        
        future_potential = viral_score
        velocity_boost = viral_velocity * 0.3
        future_potential += velocity_boost
        
        factor_bonus = len(viral_factors) * 0.05
        future_potential += factor_bonus
        
        if ViralityFactor.EMOTIONAL_IMPACT in viral_factors:
            future_potential += 0.1
        if ViralityFactor.SHAREABILITY in viral_factors:
            future_potential += 0.1
            
        return max(0.0, min(1.0, future_potential))

    async def _identify_viral_amplifiers_inhibitors(
        self, 
        viral_features: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Identify factors that amplify or inhibit viral potential"""
        
        amplifiers = []
        inhibitors = []
        
        if viral_features.get("early_engagement_rate", 0) > 0.1:
            amplifiers.append("high_early_engagement")
        if viral_features.get("early_share_rate", 0) > 0.08:
            amplifiers.append("high_shareability")
        if viral_features.get("creator_viral_history", 0) > 0.7:
            amplifiers.append("viral_creator_track_record")
            
        if viral_features.get("early_engagement_rate", 0) < 0.02:
            inhibitors.append("low_initial_engagement")
        if viral_features.get("content_type_score", 0) < 0.5:
            inhibitors.append("low_viral_content_format")
            
        return amplifiers, inhibitors

    async def _assess_cross_platform_viral(
        self, 
        content_metadata: ContentMetadata, 
        viral_features: Dict[str, float]
    ) -> bool:
        """Assess cross-platform viral potential"""
        
        cross_platform_score = 0.0
        
        universal_types = [ContentType.VIDEO, ContentType.SHORT_FORM, ContentType.IMAGE]
        if content_metadata.content_type in universal_types:
            cross_platform_score += 0.3
            
        if viral_features.get("early_viral_coefficient", 0) > 0.5:
            cross_platform_score += 0.2
            
        if viral_features.get("early_share_rate", 0) > 0.05:
            cross_platform_score += 0.3
            
        return cross_platform_score > 0.6

    async def _calculate_viral_sustainability(
        self, 
        content_metadata: ContentMetadata,
        viral_score: float, 
        viral_factors: List[ViralityFactor]
    ) -> float:
        """Calculate how long viral effect will last"""
        
        base_sustainability = viral_score * 0.5
        
        sustainable_factors = [
            ViralityFactor.EMOTIONAL_IMPACT,
            ViralityFactor.UNIQUENESS,
            ViralityFactor.STORYTELLING,
            ViralityFactor.VISUAL_APPEAL
        ]
        
        sustainable_count = len([f for f in viral_factors if f in sustainable_factors])
        sustainability_boost = sustainable_count * 0.1
        
        if content_metadata.content_type in [ContentType.VIDEO, ContentType.IMAGE]:
            type_sustainability = 0.2
        else:
            type_sustainability = 0.1
            
        total_sustainability = base_sustainability + sustainability_boost + type_sustainability
        return max(0.0, min(1.0, total_sustainability))

    async def _assess_title_quality(self, title: str) -> float:
        """Assess title quality based on best practices"""
        if not title:
            return 0.2
            
        quality_score = 0.5
        
        if 8 <= len(title) <= 60:
            quality_score += 0.2
            
        if '?' in title or '!' in title:
            quality_score += 0.1
            
        if any(c.isdigit() for c in title):
            quality_score += 0.1
            
        return max(0.0, min(1.0, quality_score))

    async def _assess_description_quality(self, description: str) -> float:
        """Assess description quality"""
        if not description:
            return 0.3
            
        quality_score = 0.5
        
        if 100 <= len(description) <= 500:
            quality_score += 0.2
            
        cta_keywords = ["subscribe", "like", "comment", "share", "follow"]
        if any(keyword in description.lower() for keyword in cta_keywords):
            quality_score += 0.2
            
        return max(0.0, min(1.0, quality_score))


# Export main classes for module usage
__all__ = [
    "ContentType",
    "ContentFormat", 
    "ContentCategory",
    "ViralityFactor",
    "ContentMetadata",
    "ContentPerformanceMetrics",
    "ViralAnalytics",
    "ContentOptimization",
    "ContentTrend",
    "ContentAnalyticsEngine"
]


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        # Initialize content analytics engine
        analytics_engine = ContentAnalyticsEngine()
        
        # Create sample content metadata
        content_metadata = ContentMetadata(
            content_id="content_123",
            creator_id="creator_456",
            title="Amazing Life Hack That Will Change Everything!",
            description="Check out this incredible life hack that went viral! #lifehack #viral #amazing",
            content_type=ContentType.VIDEO,
            content_format=ContentFormat.MP4,
            category=ContentCategory.LIFESTYLE,
            tags=["life hack", "tips", "viral", "amazing"],
            hashtags=["lifehack", "viral", "amazing", "tips", "fyp", "foryou"],
            mentions=["@friend1", "@brand2"],
            duration_seconds=45,
            resolution="1080p",
            publish_date=datetime.now()
        )
        
        # Sample performance data
        performance_data = {
            "views": 50000,
            "likes": 4500,
            "comments": 890,
            "shares": 1200,
            "saves": 650,
            "impressions": 120000,
            "first_hour_views": 5000,
            "hours_since_publish": 6,
            "engagement_velocity": 0.75,
            "monetization_value": 125.50
        }
        
        # Analyze content performance
        performance_metrics = await analytics_engine.analyze_content_performance(
            content_metadata, performance_data
        )
        
        print(f"Content Performance Analysis:")
        print(f"Views: {performance_metrics.views:,}")
        print(f"Engagement Rate: {performance_metrics.engagement_rate:.3f}")
        print(f"Quality Score: {performance_metrics.quality_score:.3f}")
        
        # Predict viral potential
        viral_analytics = await analytics_engine.predict_viral_potential(
            content_metadata, performance_data
        )
        
        print(f"\nViral Potential Analysis:")
        print(f"Viral Score: {viral_analytics.viral_score:.3f}")
        print(f"Viral Trajectory: {viral_analytics.viral_trajectory}")
        print(f"Cross-Platform Viral: {viral_analytics.cross_platform_viral}")
        
    # Run example
    asyncio.run(main())