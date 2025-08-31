"""
Distribution Analytics Engine
============================

Advanced distribution analytics for multi-platform content performance tracking.
Monitors content distribution effectiveness, platform optimization, and reach analytics.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices 
- Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized copying, distribution, or modification without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from redis import Redis
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from ..models.content_model import ContentModel
from ..models.analytics_model import AnalyticsModel
from ..storage.storage_manager import StorageManager
from ..vector_db.vector_db_manager import VectorDBManager


class DistributionPlatform(Enum):
    """Distribution platforms"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    PODCAST_PLATFORMS = "podcast_platforms"


class DistributionStatus(Enum):
    """Distribution status types"""
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    REMOVED = "removed"
    RESTRICTED = "restricted"


class ContentFormat(Enum):
    """Content format types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class PerformanceMetric(Enum):
    """Distribution performance metrics"""
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT = "engagement"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    VIEWS = "views"
    DOWNLOADS = "downloads"
    STREAMING_TIME = "streaming_time"
    CONVERSION_RATE = "conversion_rate"


@dataclass
class PlatformMetrics:
    """Platform-specific performance metrics"""
    platform: DistributionPlatform
    content_id: str
    reach: int
    impressions: int
    engagement_rate: float
    shares: int
    saves: int
    clicks: int
    views: int
    downloads: int
    streaming_time: int  # seconds
    conversion_rate: float
    revenue: float
    audience_demographics: Dict[str, Any]
    best_posting_times: List[Dict]
    hashtag_performance: Dict[str, float]
    timestamp: datetime


@dataclass
class DistributionSchedule:
    """Content distribution schedule"""
    content_id: str
    platform_schedule: Dict[DistributionPlatform, datetime]
    optimal_timing: Dict[DistributionPlatform, datetime]
    timezone_adjustments: Dict[str, datetime]
    priority_platforms: List[DistributionPlatform]
    content_adaptations: Dict[DistributionPlatform, Dict[str, Any]]
    expected_performance: Dict[DistributionPlatform, Dict[str, float]]


@dataclass
class CrossPlatformAnalysis:
    """Cross-platform performance analysis"""
    content_id: str
    total_reach: int
    total_engagement: float
    platform_breakdown: Dict[DistributionPlatform, PlatformMetrics]
    audience_overlap: Dict[Tuple[DistributionPlatform, DistributionPlatform], float]
    best_performing_platform: DistributionPlatform
    underperforming_platforms: List[DistributionPlatform]
    cross_platform_synergy_score: float
    distribution_effectiveness: float


@dataclass
class DistributionOptimization:
    """Distribution optimization recommendations"""
    content_id: str
    recommended_platforms: List[DistributionPlatform]
    optimal_schedule: DistributionSchedule
    content_adaptations: Dict[DistributionPlatform, List[str]]
    audience_targeting: Dict[DistributionPlatform, Dict[str, Any]]
    budget_allocation: Dict[DistributionPlatform, float]
    expected_roi: Dict[DistributionPlatform, float]
    risk_assessment: Dict[DistributionPlatform, List[str]]


@dataclass
class DistributionReport:
    """Comprehensive distribution analytics report"""
    user_id: str
    analysis_period: Dict[str, datetime]
    total_content_distributed: int
    total_reach: int
    total_engagement: float
    platform_performance: Dict[DistributionPlatform, Dict[str, Any]]
    cross_platform_analysis: List[CrossPlatformAnalysis]
    distribution_trends: Dict[str, Any]
    optimization_opportunities: List[DistributionOptimization]
    roi_analysis: Dict[str, float]
    recommendations: List[str]


class DistributionAnalytics:
    """
    Professional distribution analytics engine for IA Influencer Agent platform.
    
    Provides comprehensive analytics for content distribution across multiple platforms,
    optimization recommendations, and cross-platform performance tracking.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 storage_manager: StorageManager, vector_db: VectorDBManager):
        """
        Initialize DistributionAnalytics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            storage_manager: Storage management service
            vector_db: Vector database manager
        """
        self.db_session = db_session
        self.redis = redis_client
        self.storage = storage_manager
        self.vector_db = vector_db
        self.logger = logging.getLogger(__name__)
        
        # Caching configuration
        self.cache_ttl = 1800  # 30 minutes
        self.distribution_cache_key = "distribution_analytics:{}"
        self.platform_cache_key = "platform_metrics:{}"
    
    async def track_platform_performance(self, content_id: str, 
                                       platform: DistributionPlatform) -> PlatformMetrics:
        """
        Track performance metrics for content on specific platform.
        
        Args:
            content_id: Content identifier
            platform: Distribution platform
            
        Returns:
            PlatformMetrics: Platform-specific performance data
        """



        try:
            cache_key = self.platform_cache_key.format(f"{content_id}_{platform.value}")
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                return PlatformMetrics(**cached_data)
            
            # Fetch platform-specific metrics
            metrics = await self._fetch_platform_metrics(content_id, platform)
            
            # Enhance with analytics
            enhanced_metrics = await self._enhance_platform_metrics(metrics, platform)
            
            # Cache results
            await self._cache_data(cache_key, enhanced_metrics.__dict__, self.cache_ttl)
            
            return enhanced_metrics
            
        except Exception as e:
            self.logger.error(f"Error tracking platform performance: {str(e)}")
            raise
    
    async def analyze_cross_platform_performance(self, content_id: str) -> CrossPlatformAnalysis:
        """
        Analyze content performance across all distribution platforms.
        
        Args:
            content_id: Content identifier
            
        Returns:
            CrossPlatformAnalysis: Cross-platform performance analysis
        """



        try:
            cache_key = self.distribution_cache_key.format(f"cross_platform_{content_id}")
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                return CrossPlatformAnalysis(**cached_data)
            
            # Get metrics from all platforms
            platform_metrics = {}
            total_reach = 0
            total_engagement = 0
            
            for platform in DistributionPlatform:
                try:
                    metrics = await self.track_platform_performance(content_id, platform)
                    platform_metrics[platform] = metrics
                    total_reach += metrics.reach
                    total_engagement += metrics.engagement_rate
                except Exception as e:
                    self.logger.warning(f"Failed to get metrics for {platform}: {str(e)}")
                    continue
            
            # Calculate audience overlap
            audience_overlap = await self._calculate_audience_overlap(content_id, platform_metrics)
            
            # Identify best and worst performing platforms
            best_platform = max(platform_metrics.keys(), 
                              key=lambda p: platform_metrics[p].engagement_rate)
            underperforming = await self._identify_underperforming_platforms(platform_metrics)
            
            # Calculate synergy score
            synergy_score = await self._calculate_cross_platform_synergy(platform_metrics)
            
            # Calculate distribution effectiveness
            effectiveness = await self._calculate_distribution_effectiveness(platform_metrics)
            
            analysis = CrossPlatformAnalysis(
                content_id=content_id,
                total_reach=total_reach,
                total_engagement=total_engagement / len(platform_metrics) if platform_metrics else 0,
                platform_breakdown=platform_metrics,
                audience_overlap=audience_overlap,
                best_performing_platform=best_platform,
                underperforming_platforms=underperforming,
                cross_platform_synergy_score=synergy_score,
                distribution_effectiveness=effectiveness
            )
            
            # Cache results
            await self._cache_data(cache_key, analysis.__dict__, self.cache_ttl)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing cross-platform performance: {str(e)}")
            raise
    
    async def optimize_distribution_strategy(self, content_id: str, 
                                           target_metrics: Dict[str, float] = None) -> DistributionOptimization:
        """
        Generate distribution optimization recommendations.
        
        Args:
            content_id: Content identifier
            target_metrics: Target performance metrics (optional)
            
        Returns:
            DistributionOptimization: Optimization recommendations
        """



        try:
            # Analyze current performance
            current_analysis = await self.analyze_cross_platform_performance(content_id)
            
            # Get content characteristics
            content_data = await self._fetch_content_data(content_id)
            
            # Analyze historical performance patterns
            historical_patterns = await self._analyze_historical_patterns(content_data)
            
            # Identify optimal platforms
            recommended_platforms = await self._recommend_optimal_platforms(
                content_data, current_analysis, historical_patterns
            )
            
            # Generate optimal schedule
            optimal_schedule = await self._generate_optimal_schedule(
                content_id, recommended_platforms
            )
            
            # Generate content adaptations
            content_adaptations = await self._generate_content_adaptations(
                content_data, recommended_platforms
            )
            
            # Calculate audience targeting
            audience_targeting = await self._calculate_audience_targeting(
                content_data, recommended_platforms
            )
            
            # Calculate budget allocation
            budget_allocation = await self._calculate_budget_allocation(
                recommended_platforms, target_metrics
            )
            
            # Calculate expected ROI
            expected_roi = await self._calculate_expected_roi(
                content_data, recommended_platforms, budget_allocation
            )
            
            # Assess risks
            risk_assessment = await self._assess_distribution_risks(
                content_data, recommended_platforms
            )
            
            optimization = DistributionOptimization(
                content_id=content_id,
                recommended_platforms=recommended_platforms,
                optimal_schedule=optimal_schedule,
                content_adaptations=content_adaptations,
                audience_targeting=audience_targeting,
                budget_allocation=budget_allocation,
                expected_roi=expected_roi,
                risk_assessment=risk_assessment
            )
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Error optimizing distribution strategy: {str(e)}")
            raise
    
    async def generate_distribution_report(self, user_id: str, 
                                         period_days: int = 30) -> DistributionReport:
        """
        Generate comprehensive distribution analytics report.
        
        Args:
            user_id: User identifier
            period_days: Analysis period in days
            
        Returns:
            DistributionReport: Comprehensive distribution report
        """



        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get user content in period
            content_ids = await self._get_user_content_in_period(user_id, start_date, end_date)
            
            # Analyze each content's distribution
            cross_platform_analyses = []
            total_reach = 0
            total_engagement = 0
            
            for content_id in content_ids:
                analysis = await self.analyze_cross_platform_performance(content_id)
                cross_platform_analyses.append(analysis)
                total_reach += analysis.total_reach
                total_engagement += analysis.total_engagement
            
            # Calculate platform performance summary
            platform_performance = await self._calculate_platform_performance_summary(
                cross_platform_analyses
            )
            
            # Analyze distribution trends
            distribution_trends = await self._analyze_distribution_trends(
                user_id, start_date, end_date
            )
            
            # Generate optimization opportunities
            optimization_opportunities = []
            for content_id in content_ids:
                optimization = await self.optimize_distribution_strategy(content_id)
                optimization_opportunities.append(optimization)
            
            # Calculate ROI analysis
            roi_analysis = await self._calculate_distribution_roi(
                user_id, start_date, end_date
            )
            
            # Generate recommendations
            recommendations = await self._generate_distribution_recommendations(
                platform_performance, distribution_trends, optimization_opportunities
            )
            
            report = DistributionReport(
                user_id=user_id,
                analysis_period={
                    'start_date': start_date,
                    'end_date': end_date
                },
                total_content_distributed=len(content_ids),
                total_reach=total_reach,
                total_engagement=total_engagement / len(cross_platform_analyses) if cross_platform_analyses else 0,
                platform_performance=platform_performance,
                cross_platform_analysis=cross_platform_analyses,
                distribution_trends=distribution_trends,
                optimization_opportunities=optimization_opportunities,
                roi_analysis=roi_analysis,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating distribution report: {str(e)}")
            raise
    
    async def predict_platform_performance(self, content_data: Dict, 
                                         platform: DistributionPlatform) -> Dict[str, float]:
        """
        Predict performance metrics for content on specific platform.
        
        Args:
            content_data: Content characteristics
            platform: Target platform
            
        Returns:
            Dict[str, float]: Predicted performance metrics
        """



        try:
            # Get historical data for similar content
            similar_content = await self._find_similar_content(content_data)
            
            # Extract platform-specific features
            platform_features = await self._extract_platform_features(content_data, platform)
            
            # Apply ML model for prediction
            predictions = await self._apply_performance_prediction_model(
                platform_features, similar_content, platform
            )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting platform performance: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _fetch_platform_metrics(self, content_id: str, 
                                     platform: DistributionPlatform) -> PlatformMetrics:
        """Fetch platform-specific metrics from database"""



        try:
            query = select(AnalyticsModel).where(
                AnalyticsModel.entity_id == content_id,
                AnalyticsModel.entity_type == f"platform_{platform.value}"
            )
            result = await self.db_session.execute(query)
            metrics_data = result.scalar_one_or_none()
            
            if metrics_data and metrics_data.metadata:
                data = json.loads(metrics_data.metadata)
                return PlatformMetrics(
                    platform=platform,
                    content_id=content_id,
                    reach=data.get('reach', 0),
                    impressions=data.get('impressions', 0),
                    engagement_rate=data.get('engagement_rate', 0.0),
                    shares=data.get('shares', 0),
                    saves=data.get('saves', 0),
                    clicks=data.get('clicks', 0),
                    views=data.get('views', 0),
                    downloads=data.get('downloads', 0),
                    streaming_time=data.get('streaming_time', 0),
                    conversion_rate=data.get('conversion_rate', 0.0),
                    revenue=data.get('revenue', 0.0),
                    audience_demographics=data.get('audience_demographics', {}),
                    best_posting_times=data.get('best_posting_times', []),
                    hashtag_performance=data.get('hashtag_performance', {}),
                    timestamp=datetime.utcnow()
                )
            
            # Return default metrics if no data found
            return PlatformMetrics(
                platform=platform,
                content_id=content_id,
                reach=0,
                impressions=0,
                engagement_rate=0.0,
                shares=0,
                saves=0,
                clicks=0,
                views=0,
                downloads=0,
                streaming_time=0,
                conversion_rate=0.0,
                revenue=0.0,
                audience_demographics={},
                best_posting_times=[],
                hashtag_performance={},
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching platform metrics: {str(e)}")
            raise
    
    async def _enhance_platform_metrics(self, metrics: PlatformMetrics, 
                                      platform: DistributionPlatform) -> PlatformMetrics:
        """Enhance metrics with additional analytics"""
        # Enhanced metrics calculation logic
        return metrics
    
    async def _calculate_audience_overlap(self, content_id: str, 
                                        platform_metrics: Dict) -> Dict[Tuple[DistributionPlatform, DistributionPlatform], float]:
        """Calculate audience overlap between platforms"""
        # Audience overlap calculation
        return {}
    
    async def _identify_underperforming_platforms(self, platform_metrics: Dict) -> List[DistributionPlatform]:
        """Identify underperforming platforms"""
        # Performance analysis logic
        return []
    
    async def _calculate_cross_platform_synergy(self, platform_metrics: Dict) -> float:
        """Calculate cross-platform synergy score"""
        # Synergy calculation logic
        return 0.75
    
    async def _calculate_distribution_effectiveness(self, platform_metrics: Dict) -> float:
        """Calculate distribution effectiveness score"""
        # Effectiveness calculation logic
        return 0.80
    
    async def _fetch_content_data(self, content_id: str) -> Dict:
        """Fetch content data from database"""



        try:
            query = select(ContentModel).where(ContentModel.id == content_id)
            result = await self.db_session.execute(query)
            content = result.scalar_one_or_none()
            
            if content:
                return {
                    'id': content.id,
                    'title': content.title,
                    'description': content.description,
                    'content_type': content.content_type,
                    'metadata': json.loads(content.metadata) if content.metadata else {}
                }
            return {}
            
        except Exception as e:
            self.logger.error(f"Error fetching content data: {str(e)}")
            return {}
    
    async def _analyze_historical_patterns(self, content_data: Dict) -> Dict:
        """Analyze historical performance patterns"""
        # Historical analysis logic
        return {}
    
    async def _recommend_optimal_platforms(self, content_data: Dict, 
                                         current_analysis: CrossPlatformAnalysis,
                                         historical_patterns: Dict) -> List[DistributionPlatform]:
        """Recommend optimal distribution platforms"""
        # Platform recommendation logic
        return [DistributionPlatform.SPOTIFY, DistributionPlatform.YOUTUBE]
    
    async def _generate_optimal_schedule(self, content_id: str, 
                                       platforms: List[DistributionPlatform]) -> DistributionSchedule:
        """Generate optimal distribution schedule"""
        # Schedule optimization logic
        return DistributionSchedule(
            content_id=content_id,
            platform_schedule={},
            optimal_timing={},
            timezone_adjustments={},
            priority_platforms=platforms,
            content_adaptations={},
            expected_performance={}
        )
    
    async def _generate_content_adaptations(self, content_data: Dict, 
                                          platforms: List[DistributionPlatform]) -> Dict[DistributionPlatform, List[str]]:
        """Generate content adaptations for each platform"""
        # Content adaptation logic
        return {}
    
    async def _calculate_audience_targeting(self, content_data: Dict, 
                                          platforms: List[DistributionPlatform]) -> Dict[DistributionPlatform, Dict[str, Any]]:
        """Calculate audience targeting strategies"""
        # Audience targeting logic
        return {}
    
    async def _calculate_budget_allocation(self, platforms: List[DistributionPlatform], 
                                         target_metrics: Dict = None) -> Dict[DistributionPlatform, float]:
        """Calculate optimal budget allocation"""
        # Budget allocation logic
        return {}
    
    async def _calculate_expected_roi(self, content_data: Dict, 
                                    platforms: List[DistributionPlatform],
                                    budget_allocation: Dict) -> Dict[DistributionPlatform, float]:
        """Calculate expected ROI for each platform"""
        # ROI calculation logic
        return {}
    
    async def _assess_distribution_risks(self, content_data: Dict, 
                                       platforms: List[DistributionPlatform]) -> Dict[DistributionPlatform, List[str]]:
        """Assess distribution risks for each platform"""
        # Risk assessment logic
        return {}
    
    async def _get_user_content_in_period(self, user_id: str, start_date: datetime, 
                                        end_date: datetime) -> List[str]:
        """Get user content IDs in specified period"""



        try:
            query = select(ContentModel.id).where(
                ContentModel.user_id == user_id,
                ContentModel.created_at >= start_date,
                ContentModel.created_at <= end_date
            )
            result = await self.db_session.execute(query)
            return [row[0] for row in result.fetchall()]
            
        except Exception as e:
            self.logger.error(f"Error fetching user content: {str(e)}")
            return []
    
    async def _calculate_platform_performance_summary(self, analyses: List[CrossPlatformAnalysis]) -> Dict[DistributionPlatform, Dict[str, Any]]:
        """Calculate platform performance summary"""
        # Performance summary calculation
        return {}
    
    async def _analyze_distribution_trends(self, user_id: str, start_date: datetime, 
                                         end_date: datetime) -> Dict[str, Any]:
        """Analyze distribution trends"""
        # Trend analysis logic
        return {}
    
    async def _calculate_distribution_roi(self, user_id: str, start_date: datetime, 
                                        end_date: datetime) -> Dict[str, float]:
        """Calculate distribution ROI"""
        # ROI calculation logic
        return {}
    
    async def _generate_distribution_recommendations(self, platform_performance: Dict,
                                                   trends: Dict,
                                                   opportunities: List[DistributionOptimization]) -> List[str]:
        """Generate distribution recommendations"""
        # Recommendation generation logic
        return []
    
    async def _find_similar_content(self, content_data: Dict) -> List[Dict]:
        """Find similar content for prediction"""
        # Similar content finding logic
        return []
    
    async def _extract_platform_features(self, content_data: Dict, 
                                       platform: DistributionPlatform) -> Dict:
        """Extract platform-specific features"""
        # Feature extraction logic
        return {}
    
    async def _apply_performance_prediction_model(self, features: Dict, similar_content: List[Dict], 
                                                platform: DistributionPlatform) -> Dict[str, float]:
        """Apply ML model for performance prediction"""
        # ML prediction logic
        return {}
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from Redis cache"""



        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    
    async def _cache_data(self, key: str, data: Any, ttl: int):
        """Cache data in Redis"""



        try:
            self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Failed to cache data: {str(e)}")
