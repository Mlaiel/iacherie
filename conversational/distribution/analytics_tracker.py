"""
Analytics Tracker

Enterprise-grade analytics tracking and intelligence system for multi-platform content distribution.
Provides comprehensive performance monitoring, predictive analytics, and business intelligence.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
from sklearn.decomposition import PCA
import joblib
import aiohttp
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text, desc
from pydantic import BaseModel, Field, validator
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....core.exceptions import AnalyticsError, APIError, ValidationError
from ....utils.encryption import encrypt_data, decrypt_data
from ....utils.monitoring import MetricsCollector, track_performance
from ....utils.data_processing import DataProcessor, StatisticalAnalyzer
from ....models.content import ContentModel, ContentPerformanceModel
from ....models.user import UserModel
from ....models.analytics import (
    AnalyticsModel,
    PlatformAnalyticsModel,
    AudienceInsightsModel,
    EngagementMetricsModel,
    ReachMetricsModel,
    ConversionMetricsModel
)
from .platform_manager import PlatformType


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.analytics_tracker")


class MetricType(str, Enum):
    """Analytics metric types"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    GROWTH = "growth"
    RETENTION = "retention"
    SHARE_RATE = "share_rate"
    SAVE_RATE = "save_rate"
    COMMENT_RATE = "comment_rate"
    LIKE_RATE = "like_rate"
    FOLLOWER_GROWTH = "follower_growth"
    AUDIENCE_QUALITY = "audience_quality"
    VIRAL_COEFFICIENT = "viral_coefficient"
    BRAND_MENTIONS = "brand_mentions"
    SENTIMENT_SCORE = "sentiment_score"
    INFLUENCE_SCORE = "influence_score"


class TimeGranularity(str, Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    REAL_TIME = "real_time"


class AnalysisType(str, Enum):
    """Types of analytics analysis"""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    COMPARATIVE = "comparative"
    COHORT = "cohort"
    TREND = "trend"
    ANOMALY = "anomaly"
    ATTRIBUTION = "attribution"
    SEGMENTATION = "segmentation"


class AudienceSegment(str, Enum):
    """Audience segmentation types"""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    ENGAGEMENT_LEVEL = "engagement_level"
    CONVERSION_PROPENSITY = "conversion_propensity"
    LIFECYCLE_STAGE = "lifecycle_stage"
    PLATFORM_PREFERENCE = "platform_preference"
    CONTENT_AFFINITY = "content_affinity"


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    views: int = 0
    impressions: int = 0
    reach: int = 0
    unique_views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    watch_time: float = 0.0  # seconds
    average_view_duration: float = 0.0  # seconds
    bounce_rate: float = 0.0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    cost_per_click: float = 0.0
    cost_per_conversion: float = 0.0
    return_on_ad_spend: float = 0.0
    brand_mentions: int = 0
    sentiment_score: float = 0.0
    viral_coefficient: float = 0.0
    influence_score: float = 0.0
    
    def calculate_derived_metrics(self):
        """Calculate derived performance metrics"""
        if self.impressions > 0:
            self.engagement_rate = (self.likes + self.comments + self.shares) / self.impressions
            self.click_through_rate = self.clicks / self.impressions
        
        if self.clicks > 0:
            self.conversion_rate = self.conversions / self.clicks
        
        if self.views > 0:
            self.reach_rate = self.reach / self.views
        
        # Calculate viral coefficient
        if self.views > 0:
            self.viral_coefficient = (self.shares + self.comments * 0.5) / self.views


@dataclass
class AudienceInsights:
    """Comprehensive audience insights"""
    total_followers: int = 0
    active_followers: int = 0
    new_followers: int = 0
    unfollows: int = 0
    follower_growth_rate: float = 0.0
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    device_breakdown: Dict[str, int] = field(default_factory=dict)
    platform_breakdown: Dict[str, int] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    peak_activity_times: List[datetime] = field(default_factory=list)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    behavioral_segments: Dict[str, int] = field(default_factory=dict)
    conversion_funnels: Dict[str, List[float]] = field(default_factory=dict)
    lifetime_value: Dict[str, float] = field(default_factory=dict)
    churn_risk: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContentAnalytics:
    """Comprehensive content analytics"""
    content_id: int
    platform: PlatformType
    published_at: datetime
    performance_metrics: PerformanceMetrics
    audience_insights: AudienceInsights
    comparative_analysis: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    attribution_data: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    virality_potential: float = 0.0
    monetization_potential: float = 0.0


class AnalyticsReport(BaseModel):
    """Comprehensive analytics report"""
    user_id: int
    report_type: AnalysisType
    time_period: Tuple[datetime, datetime]
    platforms: List[PlatformType]
    overall_performance: PerformanceMetrics
    platform_breakdown: Dict[PlatformType, PerformanceMetrics]
    content_performance: List[ContentAnalytics]
    audience_insights: AudienceInsights
    trend_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    growth_opportunities: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    forecasts: Dict[str, Any]
    roi_analysis: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class AdvancedAnalyticsTracker:
    """
    Enterprise-grade analytics tracking system with AI-powered insights and intelligence.
    
    Features:
    - Real-time performance monitoring across all platforms
    - Advanced statistical analysis and machine learning insights
    - Predictive analytics for content performance and audience behavior
    - Comprehensive audience segmentation and profiling
    - Competitive intelligence and benchmarking
    - Attribution modeling and conversion tracking
    - Automated anomaly detection and alerting
    - Custom dashboard generation and visualization
    - ROI analysis and business intelligence
    - Data privacy and compliance management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self.data_processor = DataProcessor()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # Load ML models for analytics
        self.analytics_models = self._load_analytics_models()
        self.prediction_models = self._load_prediction_models()
        self.segmentation_models = self._load_segmentation_models()
        
        # Initialize platform API configurations
        self.platform_apis = self._initialize_platform_apis()
        
        # Real-time monitoring
        self.streaming_processors = self._initialize_streaming_processors()
        
        # Cache for performance optimization
        self.cache_configs = self._initialize_cache_configs()
        
        # Data quality and validation
        self.data_validators = self._initialize_data_validators()
        
        # Visualization engines
        self.visualization_engine = self._initialize_visualization_engine()
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=20)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.redis_client = await aioredis.from_url(settings.REDIS_URL)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.redis_client:
            await self.redis_client.close()
        self.executor.shutdown(wait=True)
    
    def _load_analytics_models(self) -> Dict[str, Any]:
        """Load ML models for analytics processing"""
        models = {}
        
        try:
            # Performance prediction models
            models["engagement_predictor"] = joblib.load("models/engagement_predictor.pkl")
            models["reach_predictor"] = joblib.load("models/reach_predictor.pkl")
            models["viral_predictor"] = joblib.load("models/viral_predictor.pkl")
            models["conversion_predictor"] = joblib.load("models/conversion_predictor.pkl")
            
            # Audience analysis models
            models["audience_segmenter"] = joblib.load("models/audience_segmenter.pkl")
            models["behavior_analyzer"] = joblib.load("models/behavior_analyzer.pkl")
            models["churn_predictor"] = joblib.load("models/churn_predictor.pkl")
            models["ltv_predictor"] = joblib.load("models/ltv_predictor.pkl")
            
            # Content analysis models
            models["content_quality_scorer"] = joblib.load("models/content_quality_scorer.pkl")
            models["trending_detector"] = joblib.load("models/trending_detector.pkl")
            models["sentiment_analyzer"] = joblib.load("models/sentiment_analyzer.pkl")
            models["topic_classifier"] = joblib.load("models/topic_classifier.pkl")
            
            # Anomaly detection models
            models["anomaly_detector"] = joblib.load("models/anomaly_detector.pkl")
            models["fraud_detector"] = joblib.load("models/fraud_detector.pkl")
            
            logger.info("Successfully loaded analytics ML models")
            
        except FileNotFoundError:
            logger.warning("Analytics ML models not found, using fallback algorithms")
            models = self._create_fallback_analytics_models()
        
        return models
    
    def _create_fallback_analytics_models(self) -> Dict[str, Any]:
        """Create fallback analytics models"""
        return {
            "engagement_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
            "reach_predictor": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "viral_predictor": RandomForestRegressor(n_estimators=50, random_state=42),
            "conversion_predictor": LogisticRegression(random_state=42),
            "audience_segmenter": KMeans(n_clusters=8, random_state=42),
            "behavior_analyzer": DBSCAN(eps=0.5, min_samples=5),
            "churn_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
            "ltv_predictor": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "content_quality_scorer": RandomForestRegressor(n_estimators=50, random_state=42),
            "trending_detector": IsolationForest(contamination=0.1, random_state=42),
            "sentiment_analyzer": LogisticRegression(random_state=42),
            "topic_classifier": RandomForestRegressor(n_estimators=50, random_state=42),
            "anomaly_detector": IsolationForest(contamination=0.1, random_state=42),
            "fraud_detector": IsolationForest(contamination=0.05, random_state=42)
        }
    
    def _load_prediction_models(self) -> Dict[str, Any]:
        """Load prediction models for forecasting"""
        models = {}
        
        try:
            models["performance_forecaster"] = joblib.load("models/performance_forecaster.pkl")
            models["audience_growth_predictor"] = joblib.load("models/audience_growth_predictor.pkl")
            models["revenue_forecaster"] = joblib.load("models/revenue_forecaster.pkl")
            models["trend_predictor"] = joblib.load("models/trend_predictor.pkl")
            models["seasonal_analyzer"] = joblib.load("models/seasonal_analyzer.pkl")
            
        except FileNotFoundError:
            logger.warning("Prediction models not found, using statistical methods")
            models = self._create_fallback_prediction_models()
        
        return models
    
    def _create_fallback_prediction_models(self) -> Dict[str, Any]:
        """Create fallback prediction models"""
        return {
            "performance_forecaster": RandomForestRegressor(n_estimators=100, random_state=42),
            "audience_growth_predictor": LinearRegression(),
            "revenue_forecaster": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "trend_predictor": RandomForestRegressor(n_estimators=50, random_state=42),
            "seasonal_analyzer": RandomForestRegressor(n_estimators=30, random_state=42)
        }
    
    def _load_segmentation_models(self) -> Dict[str, Any]:
        """Load audience segmentation models"""
        models = {}
        
        try:
            models["demographic_segmenter"] = joblib.load("models/demographic_segmenter.pkl")
            models["behavioral_segmenter"] = joblib.load("models/behavioral_segmenter.pkl")
            models["engagement_segmenter"] = joblib.load("models/engagement_segmenter.pkl")
            models["value_segmenter"] = joblib.load("models/value_segmenter.pkl")
            models["lifecycle_segmenter"] = joblib.load("models/lifecycle_segmenter.pkl")
            
        except FileNotFoundError:
            logger.warning("Segmentation models not found, using clustering algorithms")
            models = self._create_fallback_segmentation_models()
        
        return models
    
    def _create_fallback_segmentation_models(self) -> Dict[str, Any]:
        """Create fallback segmentation models"""
        return {
            "demographic_segmenter": KMeans(n_clusters=5, random_state=42),
            "behavioral_segmenter": KMeans(n_clusters=8, random_state=42),
            "engagement_segmenter": KMeans(n_clusters=6, random_state=42),
            "value_segmenter": KMeans(n_clusters=4, random_state=42),
            "lifecycle_segmenter": KMeans(n_clusters=7, random_state=42)
        }
    
    def _initialize_platform_apis(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform API configurations for analytics"""
        return {
            PlatformType.YOUTUBE: {
                "analytics_api": "https://youtubeanalytics.googleapis.com/v2/reports",
                "metrics": [
                    "views", "likes", "dislikes", "comments", "shares", "subscribersGained",
                    "subscribersLost", "estimatedMinutesWatched", "averageViewDuration",
                    "impressions", "impressionClickThroughRate", "estimatedRevenue"
                ],
                "dimensions": ["day", "country", "deviceCategory", "ageGroup", "gender"],
                "real_time_endpoint": "https://youtube.googleapis.com/youtube/v3/videos",
                "rate_limit": 100
            },
            PlatformType.INSTAGRAM: {
                "analytics_api": "https://graph.facebook.com/v18.0/insights",
                "metrics": [
                    "reach", "impressions", "likes", "comments", "shares", "saves",
                    "profile_views", "website_clicks", "video_views", "story_replies"
                ],
                "dimensions": ["lifetime", "day", "week", "days_28"],
                "real_time_endpoint": "https://graph.facebook.com/v18.0/me/media",
                "rate_limit": 200
            },
            PlatformType.TIKTOK: {
                "analytics_api": "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                "metrics": [
                    "impressions", "clicks", "spend", "conversions", "video_views",
                    "profile_visits", "likes", "comments", "shares"
                ],
                "dimensions": ["stat_time_day", "campaign_id", "adgroup_id"],
                "real_time_endpoint": "https://open-api.tiktok.com/platform/oauth/token/",
                "rate_limit": 60
            },
            PlatformType.TWITTER: {
                "analytics_api": "https://ads-api.twitter.com/11/stats/accounts",
                "metrics": [
                    "impressions", "engagements", "retweets", "likes", "replies",
                    "url_clicks", "hashtag_clicks", "profile_clicks", "media_views"
                ],
                "dimensions": ["DAY", "HOUR", "TOTAL"],
                "real_time_endpoint": "https://api.twitter.com/2/tweets/search/stream",
                "rate_limit": 300
            },
            PlatformType.SPOTIFY: {
                "analytics_api": "https://api.spotify.com/v1/artists/{id}/analytics",
                "metrics": [
                    "streams", "listeners", "followers", "playlist_adds",
                    "saves", "skip_rate", "completion_rate"
                ],
                "dimensions": ["day", "country", "age", "gender"],
                "real_time_endpoint": "https://api.spotify.com/v1/me/player/currently-playing",
                "rate_limit": 100
            }
        }
    
    def _initialize_streaming_processors(self) -> Dict[str, Any]:
        """Initialize real-time streaming processors"""
        return {
            "kafka_config": {
                "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group_id": "analytics_tracker",
                "auto_offset_reset": "latest"
            },
            "stream_topics": {
                "engagement_events": "platform_engagement",
                "conversion_events": "platform_conversions",
                "audience_events": "audience_activity",
                "content_events": "content_interactions"
            },
            "batch_size": 1000,
            "processing_interval": 30  # seconds
        }
    
    def _initialize_cache_configs(self) -> Dict[str, Any]:
        """Initialize caching configurations"""
        return {
            "analytics_cache_ttl": 300,  # 5 minutes
            "real_time_cache_ttl": 60,   # 1 minute
            "dashboard_cache_ttl": 900,  # 15 minutes
            "report_cache_ttl": 3600,    # 1 hour
            "max_cache_size": 10000,
            "cache_compression": True
        }
    
    def _initialize_data_validators(self) -> Dict[str, Any]:
        """Initialize data quality validators"""
        return {
            "metric_ranges": {
                "engagement_rate": (0.0, 1.0),
                "click_through_rate": (0.0, 1.0),
                "conversion_rate": (0.0, 1.0),
                "bounce_rate": (0.0, 1.0),
                "sentiment_score": (-1.0, 1.0)
            },
            "required_fields": [
                "user_id", "content_id", "platform", "timestamp"
            ],
            "data_freshness_threshold": timedelta(hours=6),
            "anomaly_thresholds": {
                "engagement_spike": 5.0,  # 5x normal
                "traffic_drop": 0.2,      # 80% decrease
                "conversion_anomaly": 3.0  # 3x normal
            }
        }
    
    def _initialize_visualization_engine(self) -> Dict[str, Any]:
        """Initialize visualization and dashboard engine"""
        return {
            "chart_types": [
                "line", "bar", "pie", "scatter", "heatmap", "treemap",
                "funnel", "gauge", "candlestick", "violin", "box"
            ],
            "color_schemes": {
                "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "engagement": ["#2E8B57", "#32CD32", "#90EE90", "#98FB98"],
                "revenue": ["#B8860B", "#DAA520", "#FFD700", "#FFFF00"],
                "audience": ["#4682B4", "#87CEEB", "#B0C4DE", "#E6E6FA"]
            },
            "dashboard_templates": [
                "executive_summary", "content_performance", "audience_insights",
                "revenue_analytics", "competitive_analysis", "growth_tracking"
            ]
        }

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from ....core.database import get_db
from ....models.content import ContentModel
from ....models.user import UserModel
from ....models.analytics import AnalyticsModel, PlatformAnalyticsModel
from ....models.distribution_analytics import DistributionAnalyticsModel
from .platform_manager import PlatformType


logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of distribution metrics"""
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT = "engagement"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    SAVES = "saves"
    CONVERSION = "conversion"
    REVENUE = "revenue"
    CPM = "cpm"
    CTR = "ctr"
    ENGAGEMENT_RATE = "engagement_rate"


class TimeRange(str, Enum):
    """Time range options for analytics"""
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


@dataclass
class PlatformMetrics:
    """Platform-specific performance metrics"""
    platform: PlatformType
    reach: int
    impressions: int
    engagement: int
    clicks: int
    shares: int
    comments: int
    likes: int
    saves: int
    revenue: float
    cpm: float
    ctr: float
    engagement_rate: float
    best_performing_content: Optional[str] = None
    trending_hashtags: List[str] = None


@dataclass
class CrossPlatformInsights:
    """Cross-platform distribution insights"""
    total_reach: int
    total_engagement: int
    total_revenue: float
    platform_performance: Dict[PlatformType, PlatformMetrics]
    audience_overlap: Dict[str, float]
    content_amplification: Dict[str, float]
    optimal_posting_times: Dict[PlatformType, List[int]]
    seasonal_trends: Dict[str, float]


class AnalyticsRequest(BaseModel):
    """Analytics request model"""
    user_id: int
    content_id: Optional[int] = None
    platforms: Optional[List[PlatformType]] = None
    time_range: TimeRange = TimeRange.LAST_7D
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metrics: List[MetricType] = Field(default_factory=lambda: [
        MetricType.REACH, MetricType.ENGAGEMENT, MetricType.REVENUE
    ])
    include_predictions: bool = False
    granularity: str = "daily"  # hourly, daily, weekly


class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    user_id: int
    time_range: str
    total_metrics: Dict[str, Any]
    platform_breakdown: Dict[str, Dict[str, Any]]
    trend_data: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    cross_platform_insights: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None


class DistributionAnalyticsTracker:
    """
    Advanced analytics tracker for distribution performance monitoring
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.metric_calculators = self._initialize_metric_calculators()
        self.insight_generators = self._initialize_insight_generators()
        
    def _initialize_metric_calculators(self) -> Dict[MetricType, callable]:
        """Initialize metric calculation functions"""
        return {
            MetricType.REACH: self._calculate_reach,
            MetricType.IMPRESSIONS: self._calculate_impressions,
            MetricType.ENGAGEMENT: self._calculate_engagement,
            MetricType.CLICKS: self._calculate_clicks,
            MetricType.SHARES: self._calculate_shares,
            MetricType.COMMENTS: self._calculate_comments,
            MetricType.LIKES: self._calculate_likes,
            MetricType.SAVES: self._calculate_saves,
            MetricType.CONVERSION: self._calculate_conversion,
            MetricType.REVENUE: self._calculate_revenue,
            MetricType.CPM: self._calculate_cpm,
            MetricType.CTR: self._calculate_ctr,
            MetricType.ENGAGEMENT_RATE: self._calculate_engagement_rate
        }
    
    def _initialize_insight_generators(self) -> Dict[str, callable]:
        """Initialize insight generation functions"""
        return {
            "performance_trends": self._generate_performance_trends,
            "platform_comparison": self._generate_platform_comparison,
            "audience_insights": self._generate_audience_insights,
            "content_optimization": self._generate_content_optimization,
            "timing_optimization": self._generate_timing_optimization,
            "revenue_optimization": self._generate_revenue_optimization
        }
    
    async def get_distribution_analytics(
        self, request: AnalyticsRequest
    ) -> AnalyticsResponse:
        """
        Get comprehensive distribution analytics
        
        Args:
            request: Analytics request parameters
            
        Returns:
            Detailed analytics response with insights
        """
        try:
            # Validate request
            await self._validate_analytics_request(request)
            
            # Calculate time range
            start_date, end_date = self._calculate_time_range(request)
            
            # Get analytics data
            analytics_data = await self._fetch_analytics_data(
                request, start_date, end_date
            )
            
            # Calculate metrics
            total_metrics = await self._calculate_total_metrics(
                analytics_data, request.metrics
            )
            
            # Platform breakdown
            platform_breakdown = await self._calculate_platform_breakdown(
                analytics_data, request.metrics
            )
            
            # Trend data
            trend_data = await self._calculate_trend_data(
                analytics_data, request.granularity, start_date, end_date
            )
            
            # Generate insights
            insights = await self._generate_insights(
                analytics_data, total_metrics, platform_breakdown
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                analytics_data, total_metrics, platform_breakdown
            )
            
            # Cross-platform insights
            cross_platform_insights = None
            if len(request.platforms or []) > 1:
                cross_platform_insights = await self._generate_cross_platform_insights(
                    analytics_data
                )
            
            # Predictions
            predictions = None
            if request.include_predictions:
                predictions = await self._generate_predictions(
                    analytics_data, request
                )
            
            return AnalyticsResponse(
                user_id=request.user_id,
                time_range=f"{start_date.isoformat()} - {end_date.isoformat()}",
                total_metrics=total_metrics,
                platform_breakdown=platform_breakdown,
                trend_data=trend_data,
                insights=insights,
                recommendations=recommendations,
                cross_platform_insights=cross_platform_insights,
                predictions=predictions
            )
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            raise
    
    async def _validate_analytics_request(self, request: AnalyticsRequest) -> None:
        """Validate analytics request parameters"""
        # Check user exists
        user = self.db.query(UserModel).filter(UserModel.id == request.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Validate content if specified
        if request.content_id:
            content = self.db.query(ContentModel).filter(
                ContentModel.id == request.content_id,
                ContentModel.user_id == request.user_id
            ).first()
            if not content:
                raise ValueError("Content not found or access denied")
        
        # Validate custom time range
        if request.time_range == TimeRange.CUSTOM:
            if not request.start_date or not request.end_date:
                raise ValueError("Start and end dates required for custom time range")
            
            if request.start_date >= request.end_date:
                raise ValueError("Start date must be before end date")
    
    def _calculate_time_range(self, request: AnalyticsRequest) -> Tuple[datetime, datetime]:
        """Calculate start and end dates for analytics"""
        end_date = datetime.utcnow()
        
        if request.time_range == TimeRange.CUSTOM:
            return request.start_date, request.end_date
        
        time_deltas = {
            TimeRange.LAST_24H: timedelta(hours=24),
            TimeRange.LAST_7D: timedelta(days=7),
            TimeRange.LAST_30D: timedelta(days=30),
            TimeRange.LAST_90D: timedelta(days=90),
            TimeRange.LAST_YEAR: timedelta(days=365)
        }
        
        delta = time_deltas.get(request.time_range, timedelta(days=7))
        start_date = end_date - delta
        
        return start_date, end_date
    
    async def _fetch_analytics_data(
        self,
        request: AnalyticsRequest,
        start_date: datetime,
        end_date: datetime
    ) -> List[DistributionAnalyticsModel]:
        """Fetch analytics data from database"""
        query = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == request.user_id,
            DistributionAnalyticsModel.created_at >= start_date,
            DistributionAnalyticsModel.created_at <= end_date
        )
        
        if request.content_id:
            query = query.filter(
                DistributionAnalyticsModel.content_id == request.content_id
            )
        
        if request.platforms:
            platform_values = [p.value for p in request.platforms]
            query = query.filter(
                DistributionAnalyticsModel.platform.in_(platform_values)
            )
        
        return query.all()
    
    async def _calculate_total_metrics(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        requested_metrics: List[MetricType]
    ) -> Dict[str, Any]:
        """Calculate total metrics across all data"""
        total_metrics = {}
        
        for metric in requested_metrics:
            calculator = self.metric_calculators.get(metric)
            if calculator:
                total_metrics[metric.value] = await calculator(analytics_data)
        
        return total_metrics
    
    async def _calculate_platform_breakdown(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        requested_metrics: List[MetricType]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate metrics broken down by platform"""
        platform_breakdown = {}
        
        # Group data by platform
        platform_data = {}
        for record in analytics_data:
            platform = record.platform
            if platform not in platform_data:
                platform_data[platform] = []
            platform_data[platform].append(record)
        
        # Calculate metrics for each platform
        for platform, data in platform_data.items():
            platform_metrics = {}
            
            for metric in requested_metrics:
                calculator = self.metric_calculators.get(metric)
                if calculator:
                    platform_metrics[metric.value] = await calculator(data)
            
            platform_breakdown[platform] = platform_metrics
        
        return platform_breakdown
    
    async def _calculate_trend_data(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        granularity: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate trend data over time"""
        trend_data = []
        
        # Determine time intervals based on granularity
        if granularity == "hourly":
            interval = timedelta(hours=1)
        elif granularity == "daily":
            interval = timedelta(days=1)
        elif granularity == "weekly":
            interval = timedelta(weeks=1)
        else:
            interval = timedelta(days=1)
        
        # Generate time buckets
        current_time = start_date
        while current_time < end_date:
            bucket_end = min(current_time + interval, end_date)
            
            # Filter data for this time bucket
            bucket_data = [
                record for record in analytics_data
                if current_time <= record.created_at < bucket_end
            ]
            
            # Calculate metrics for this bucket
            bucket_metrics = {
                "timestamp": current_time.isoformat(),
                "reach": await self._calculate_reach(bucket_data),
                "engagement": await self._calculate_engagement(bucket_data),
                "revenue": await self._calculate_revenue(bucket_data),
                "posts_count": len(bucket_data)
            }
            
            trend_data.append(bucket_metrics)
            current_time = bucket_end
        
        return trend_data
    
    async def _generate_insights(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        total_metrics: Dict[str, Any],
        platform_breakdown: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable insights from analytics data"""
        insights = []
        
        # Best performing platform
        if platform_breakdown:
            best_platform = max(
                platform_breakdown.items(),
                key=lambda x: x[1].get("reach", 0)
            )
            insights.append(
                f"{best_platform[0]} is your best performing platform with "
                f"{best_platform[1].get('reach', 0):,} total reach."
            )
        
        # Engagement rate insights
        if "engagement_rate" in total_metrics:
            rate = total_metrics["engagement_rate"]
            if rate > 0.05:
                insights.append(
                    f"Your content has an excellent engagement rate of {rate:.2%}, "
                    "which is above industry average."
                )
            elif rate < 0.02:
                insights.append(
                    f"Your engagement rate of {rate:.2%} could be improved. "
                    "Consider optimizing your content format and posting times."
                )
        
        # Revenue insights
        if "revenue" in total_metrics:
            revenue = total_metrics["revenue"]
            if revenue > 0:
                insights.append(
                    f"Your content generated ${revenue:.2f} in revenue. "
                    "Focus on high-performing content types to maximize earnings."
                )
        
        # Platform comparison insights
        if len(platform_breakdown) > 1:
            engagement_rates = {
                platform: metrics.get("engagement_rate", 0)
                for platform, metrics in platform_breakdown.items()
            }
            
            highest_engagement = max(engagement_rates.items(), key=lambda x: x[1])
            insights.append(
                f"{highest_engagement[0]} has your highest engagement rate at "
                f"{highest_engagement[1]:.2%}. Consider posting more frequently there."
            )
        
        return insights
    
    async def _generate_recommendations(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        total_metrics: Dict[str, Any],
        platform_breakdown: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Platform optimization
        if platform_breakdown:
            underperforming_platforms = [
                platform for platform, metrics in platform_breakdown.items()
                if metrics.get("engagement_rate", 0) < 0.02
            ]
            
            if underperforming_platforms:
                recommendations.append(
                    f"Consider optimizing content for {', '.join(underperforming_platforms)} "
                    "by adjusting format, timing, or messaging."
                )
        
        # Content optimization
        if "engagement_rate" in total_metrics:
            rate = total_metrics["engagement_rate"]
            if rate < 0.03:
                recommendations.append(
                    "Try experimenting with different content formats like short videos, "
                    "stories, or interactive posts to boost engagement."
                )
        
        # Posting frequency
        if len(analytics_data) > 0:
            days_active = len(set(record.created_at.date() for record in analytics_data))
            posts_per_day = len(analytics_data) / max(days_active, 1)
            
            if posts_per_day < 1:
                recommendations.append(
                    "Increase your posting frequency to at least once per day "
                    "to maintain audience engagement."
                )
            elif posts_per_day > 5:
                recommendations.append(
                    "Consider reducing posting frequency slightly to avoid "
                    "overwhelming your audience."
                )
        
        # Revenue optimization
        if "revenue" in total_metrics and total_metrics["revenue"] == 0:
            recommendations.append(
                "Enable monetization features on your best-performing platforms "
                "to start generating revenue from your content."
            )
        
        return recommendations
    
    async def _generate_cross_platform_insights(
        self, analytics_data: List[DistributionAnalyticsModel]
    ) -> Dict[str, Any]:
        """Generate cross-platform distribution insights"""
        
        # Platform performance comparison
        platform_reach = {}
        platform_engagement = {}
        
        for record in analytics_data:
            platform = record.platform
            reach = record.metrics.get("reach", 0) if record.metrics else 0
            engagement = record.metrics.get("engagement", 0) if record.metrics else 0
            
            if platform not in platform_reach:
                platform_reach[platform] = 0
                platform_engagement[platform] = 0
            
            platform_reach[platform] += reach
            platform_engagement[platform] += engagement
        
        # Calculate audience overlap (simplified)
        audience_overlap = {}
        platforms = list(platform_reach.keys())
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                # Estimated overlap based on relative performance
                overlap = min(
                    platform_reach[platform1],
                    platform_reach[platform2]
                ) / max(
                    platform_reach[platform1],
                    platform_reach[platform2]
                ) if max(platform_reach[platform1], platform_reach[platform2]) > 0 else 0
                
                audience_overlap[f"{platform1}-{platform2}"] = overlap * 0.3  # Estimated 30% max overlap
        
        # Content amplification
        total_reach = sum(platform_reach.values())
        content_amplification = {}
        for platform, reach in platform_reach.items():
            if total_reach > 0:
                content_amplification[platform] = reach / total_reach
        
        return {
            "total_reach": total_reach,
            "platform_reach": platform_reach,
            "platform_engagement": platform_engagement,
            "audience_overlap": audience_overlap,
            "content_amplification": content_amplification,
            "cross_platform_engagement_rate": (
                sum(platform_engagement.values()) / total_reach
                if total_reach > 0 else 0
            )
        }
    
    async def _generate_predictions(
        self,
        analytics_data: List[DistributionAnalyticsModel],
        request: AnalyticsRequest
    ) -> Dict[str, Any]:
        """Generate performance predictions"""
        if len(analytics_data) < 7:  # Need at least 7 data points
            return {"error": "Insufficient data for predictions"}
        
        # Simple trend-based predictions
        dates = [record.created_at for record in analytics_data]
        reaches = [record.metrics.get("reach", 0) if record.metrics else 0 for record in analytics_data]
        engagements = [record.metrics.get("engagement", 0) if record.metrics else 0 for record in analytics_data]
        
        # Calculate trends
        if len(reaches) > 1:
            reach_trend = np.polyfit(range(len(reaches)), reaches, 1)[0]
            engagement_trend = np.polyfit(range(len(engagements)), engagements, 1)[0]
            
            # Predict next 7 days
            current_reach = reaches[-1] if reaches else 0
            current_engagement = engagements[-1] if engagements else 0
            
            predicted_reach = max(0, current_reach + (reach_trend * 7))
            predicted_engagement = max(0, current_engagement + (engagement_trend * 7))
            
            return {
                "next_7_days": {
                    "predicted_reach": round(predicted_reach),
                    "predicted_engagement": round(predicted_engagement),
                    "reach_trend": "increasing" if reach_trend > 0 else "decreasing",
                    "engagement_trend": "increasing" if engagement_trend > 0 else "decreasing",
                    "confidence": min(0.8, len(analytics_data) / 30)  # Higher confidence with more data
                }
            }
        
        return {"error": "Unable to generate predictions"}
    
    # Metric calculation methods
    async def _calculate_reach(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total reach"""
        return sum(
            record.metrics.get("reach", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_impressions(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total impressions"""
        return sum(
            record.metrics.get("impressions", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_engagement(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total engagement"""
        return sum(
            record.metrics.get("engagement", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_clicks(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total clicks"""
        return sum(
            record.metrics.get("clicks", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_shares(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total shares"""
        return sum(
            record.metrics.get("shares", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_comments(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total comments"""
        return sum(
            record.metrics.get("comments", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_likes(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total likes"""
        return sum(
            record.metrics.get("likes", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_saves(self, data: List[DistributionAnalyticsModel]) -> int:
        """Calculate total saves"""
        return sum(
            record.metrics.get("saves", 0) if record.metrics else 0
            for record in data
        )
    
    async def _calculate_conversion(self, data: List[DistributionAnalyticsModel]) -> float:
        """Calculate conversion rate"""
        total_clicks = await self._calculate_clicks(data)
        total_reach = await self._calculate_reach(data)
        
        return total_clicks / total_reach if total_reach > 0 else 0
    
    async def _calculate_revenue(self, data: List[DistributionAnalyticsModel]) -> float:
        """Calculate total revenue"""
        return sum(
            record.metrics.get("revenue", 0.0) if record.metrics else 0.0
            for record in data
        )
    
    async def _calculate_cpm(self, data: List[DistributionAnalyticsModel]) -> float:
        """Calculate cost per mille (CPM)"""
        total_revenue = await self._calculate_revenue(data)
        total_impressions = await self._calculate_impressions(data)
        
        return (total_revenue / total_impressions * 1000) if total_impressions > 0 else 0
    
    async def _calculate_ctr(self, data: List[DistributionAnalyticsModel]) -> float:
        """Calculate click-through rate"""
        total_clicks = await self._calculate_clicks(data)
        total_impressions = await self._calculate_impressions(data)
        
        return total_clicks / total_impressions if total_impressions > 0 else 0
    
    async def _calculate_engagement_rate(self, data: List[DistributionAnalyticsModel]) -> float:
        """Calculate engagement rate"""
        total_engagement = await self._calculate_engagement(data)
        total_reach = await self._calculate_reach(data)
        
        return total_engagement / total_reach if total_reach > 0 else 0
    
    async def track_real_time_metrics(
        self,
        user_id: int,
        content_id: int,
        platform: PlatformType,
        metrics: Dict[str, Any]
    ) -> None:
        """Track real-time metrics for a piece of content"""
        try:
            # Create or update analytics record
            existing = self.db.query(DistributionAnalyticsModel).filter(
                DistributionAnalyticsModel.user_id == user_id,
                DistributionAnalyticsModel.content_id == content_id,
                DistributionAnalyticsModel.platform == platform.value,
                DistributionAnalyticsModel.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).first()
            
            if existing:
                # Update existing record
                if existing.metrics:
                    existing.metrics.update(metrics)
                else:
                    existing.metrics = metrics
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                new_record = DistributionAnalyticsModel(
                    user_id=user_id,
                    content_id=content_id,
                    platform=platform.value,
                    success=True,
                    metrics=metrics
                )
                self.db.add(new_record)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to track real-time metrics: {e}")
    
    async def get_platform_comparison(
        self, user_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """Get platform performance comparison"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics_data = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == user_id,
            DistributionAnalyticsModel.created_at >= start_date
        ).all()
        
        platform_comparison = {}
        
        # Group by platform
        platform_data = {}
        for record in analytics_data:
            platform = record.platform
            if platform not in platform_data:
                platform_data[platform] = []
            platform_data[platform].append(record)
        
        # Calculate comparison metrics
        for platform, data in platform_data.items():
            total_reach = await self._calculate_reach(data)
            total_engagement = await self._calculate_engagement(data)
            total_revenue = await self._calculate_revenue(data)
            post_count = len(data)
            
            platform_comparison[platform] = {
                "total_reach": total_reach,
                "total_engagement": total_engagement,
                "total_revenue": total_revenue,
                "post_count": post_count,
                "avg_reach_per_post": total_reach / post_count if post_count > 0 else 0,
                "engagement_rate": total_engagement / total_reach if total_reach > 0 else 0,
                "revenue_per_post": total_revenue / post_count if post_count > 0 else 0
            }
        
        return platform_comparison
    
    async def export_analytics_data(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        format: str = "csv"
    ) -> bytes:
        """Export analytics data in specified format"""
        analytics_data = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == user_id,
            DistributionAnalyticsModel.created_at >= start_date,
            DistributionAnalyticsModel.created_at <= end_date
        ).all()
        
        # Convert to DataFrame
        data_rows = []
        for record in analytics_data:
            row = {
                "date": record.created_at.isoformat(),
                "content_id": record.content_id,
                "platform": record.platform,
                "success": record.success,
                "post_id": record.post_id,
                "url": record.url
            }
            
            # Add metrics
            if record.metrics:
                row.update(record.metrics)
            
            data_rows.append(row)
        
        df = pd.DataFrame(data_rows)
        
        if format.lower() == "csv":
            return df.to_csv(index=False).encode('utf-8')
        elif format.lower() == "json":
            return df.to_json(orient='records').encode('utf-8')
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def cleanup_old_analytics(self, days_old: int = 365) -> int:
        """Cleanup old analytics data"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_records = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.created_at < cutoff_date
        ).all()
        
        count = len(old_records)
        
        for record in old_records:
            self.db.delete(record)
        
        self.db.commit()
        
        logger.info(f"Cleaned up {count} old analytics records")
        return count
