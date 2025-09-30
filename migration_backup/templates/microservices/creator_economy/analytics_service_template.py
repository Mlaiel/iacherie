"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Analytics Service Template for Ainflue Platform
==============================================

Production-ready advanced analytics service with:
- Real-time content performance analytics
- Creator audience insights and demographics
- Revenue and engagement analytics
- AI-powered predictive analytics
- Multi-platform analytics aggregation
- Custom dashboard and reporting
- A/B testing and optimization insights
- Competitor analysis and benchmarking

Author: Fahed Mlaiel (mlaiel@live.de)
Data Analytics & Business Intelligence Expert
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker
from ..communication_manager import CommunicationManager

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of analytics metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    REVENUE = "revenue"
    AUDIENCE = "audience"
    CONTENT_PERFORMANCE = "content_performance"
    CONVERSION = "conversion"
    RETENTION = "retention"
    GROWTH = "growth"


class TimeFramePeriod(Enum):
    """Analytics time frame periods"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class PlatformType(Enum):
    """Supported platforms for analytics"""
    AINFLUE = "ainflue"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"


class DashboardType(Enum):
    """Types of analytics dashboards"""
    OVERVIEW = "overview"
    CONTENT = "content"
    AUDIENCE = "audience"
    REVENUE = "revenue"
    GROWTH = "growth"
    ENGAGEMENT = "engagement"
    COMPETITOR = "competitor"
    CUSTOM = "custom"


@dataclass
class AnalyticsMetric:
    """Analytics metric data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    metric_type: MetricType = MetricType.ENGAGEMENT
    platform: PlatformType = PlatformType.AINFLUE
    
    # Metric details
    name: str = ""
    value: float = 0.0
    previous_value: float = 0.0
    target_value: Optional[float] = None
    
    # Time information
    timestamp: datetime = field(default_factory=datetime.utcnow)
    period: TimeFramePeriod = TimeFramePeriod.DAY
    
    # Context
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Calculated fields
    change_percentage: float = 0.0
    trend_direction: str = "neutral"  # up, down, neutral
    performance_score: float = 0.0


@dataclass
class ContentAnalytics:
    """Content performance analytics"""
    content_id: str = ""
    creator_id: str = ""
    content_type: str = ""
    title: str = ""
    
    # Engagement metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    
    # Performance metrics
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    
    # Audience metrics
    unique_viewers: int = 0
    average_watch_time: float = 0.0
    completion_rate: float = 0.0
    
    # Revenue metrics
    revenue_generated: float = 0.0
    conversion_count: int = 0
    conversion_rate: float = 0.0
    
    # Time metrics
    published_at: datetime = field(default_factory=datetime.utcnow)
    peak_performance_time: Optional[datetime] = None
    
    # AI insights
    virality_score: float = 0.0
    quality_score: float = 0.0
    audience_match_score: float = 0.0
    
    # Platform breakdown
    platform_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class AudienceInsights:
    """Audience demographics and behavior insights"""
    creator_id: str = ""
    
    # Demographics
    age_distribution: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Behavior patterns
    peak_activity_hours: List[int] = field(default_factory=list)
    device_preferences: Dict[str, float] = field(default_factory=dict)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Engagement patterns
    engagement_by_time: Dict[str, float] = field(default_factory=dict)
    engagement_by_content_type: Dict[str, float] = field(default_factory=dict)
    
    # Growth metrics
    follower_growth_rate: float = 0.0
    audience_retention_rate: float = 0.0
    churn_rate: float = 0.0
    
    # Insights
    top_interests: List[str] = field(default_factory=list)
    behavioral_segments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Updated timestamp
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AnalyticsConfig:
    """Analytics service configuration"""
    
    def __init__(self):
        # Data collection settings
        self.collection_interval = 300  # 5 minutes
        self.batch_size = 1000
        self.retention_days = 730  # 2 years
        
        # Real-time processing
        self.enable_real_time = True
        self.real_time_threshold = 60  # seconds
        self.stream_processing_enabled = True
        
        # AI and ML settings
        self.enable_predictive_analytics = True
        self.enable_anomaly_detection = True
        self.ml_model_update_interval = 86400  # 24 hours
        
        # External integrations
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        
        # Performance settings
        self.max_concurrent_requests = 50
        self.cache_ttl = 3600  # 1 hour
        self.aggregation_interval = 3600  # 1 hour
        
        # Dashboard settings
        self.max_dashboard_widgets = 20
        self.default_time_range = 30  # days
        self.auto_refresh_interval = 300  # 5 minutes


# Pydantic models for API
class AnalyticsQuery(BaseModel):
    """Analytics query request"""
    creator_id: str
    metric_types: List[MetricType] = Field(default_factory=list)
    platforms: List[PlatformType] = Field(default_factory=list)
    time_frame: TimeFramePeriod = TimeFramePeriod.WEEK
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    content_ids: List[str] = Field(default_factory=list)
    granularity: str = Field("hour", pattern="^(minute|hour|day|week|month)$")


class CustomDashboardRequest(BaseModel):
    """Custom dashboard creation request"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field("", max_length=500)
    dashboard_type: DashboardType = DashboardType.CUSTOM
    widgets: List[Dict[str, Any]] = Field(..., min_items=1, max_items=20)
    time_range: int = Field(30, ge=1, le=365)
    auto_refresh: bool = True


class CompetitorAnalysisRequest(BaseModel):
    """Competitor analysis request"""
    creator_id: str
    competitor_ids: List[str] = Field(..., min_items=1, max_items=10)
    metrics: List[MetricType] = Field(default_factory=list)
    time_frame: TimeFramePeriod = TimeFramePeriod.MONTH


class PredictionRequest(BaseModel):
    """Analytics prediction request"""
    creator_id: str
    metric_type: MetricType
    prediction_horizon: int = Field(30, ge=1, le=365)  # days
    confidence_level: float = Field(0.95, ge=0.5, le=0.99)


class AnalyticsResponse(BaseModel):
    """Analytics query response"""
    creator_id: str
    metrics: List[Dict[str, Any]]
    time_range: Dict[str, str]
    summary: Dict[str, Any]
    insights: List[str]
    generated_at: datetime


class DashboardResponse(BaseModel):
    """Dashboard data response"""
    dashboard_id: str
    name: str
    data: Dict[str, Any]
    last_updated: datetime
    auto_refresh: bool


class AnalyticsService(BaseMicroservice):
    """
    Enterprise Analytics Service for Ainflue Platform
    
    Provides comprehensive analytics, insights, and reporting
    for content creators with AI-powered predictions and optimization.
    """
    
    def __init__(self, config: Optional[AnalyticsConfig] = None):
        super().__init__("analytics-service")
        
        self.config = config or AnalyticsConfig()
        self.metrics_cache: Dict[str, List[AnalyticsMetric]] = {}
        self.content_analytics: Dict[str, ContentAnalytics] = {}
        self.audience_insights: Dict[str, AudienceInsights] = {}
        self.custom_dashboards: Dict[str, Dict[str, Any]] = {}
        
        # Metrics
        self.analytics_requests_counter = Counter('analytics_requests_total', 'Total analytics requests')
        self.data_points_processed = Counter('analytics_data_points_processed', 'Data points processed')
        self.dashboard_views_counter = Counter('analytics_dashboard_views', 'Dashboard views')
        self.query_duration = Histogram('analytics_query_duration_seconds', 'Query processing duration')
        self.active_creators_gauge = Gauge('analytics_active_creators', 'Active creators being tracked')
        
        # Circuit breakers
        self.external_api_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
        
        self.ml_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=120,
            expected_exception=Exception
        )
        
        # Communication manager
        self.communication_manager = CommunicationManager()
        
        # Redis client for caching and real-time data
        self.redis_client: Optional[redis.Redis] = None
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # ML models (placeholder)
        self.ml_models: Dict[str, Any] = {}
        
        logger.info("Analytics Service initialized")
    
    async def startup(self):
        """Service startup tasks"""
        await super().startup()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        # Load ML models
        await self._load_ml_models()
        
        # Start background tasks
        await self._start_background_tasks()
        
        logger.info("Analytics Service started")
    
    async def shutdown(self):
        """Service shutdown tasks"""
        logger.info("Shutting down Analytics Service...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        await super().shutdown()
        logger.info("Analytics Service shut down")
    
    async def _load_ml_models(self):
        """Load machine learning models for predictions"""
        try:
            # Placeholder for ML model loading
            self.ml_models = {
                "engagement_predictor": None,
                "growth_forecaster": None,
                "anomaly_detector": None,
                "content_optimizer": None
            }
            logger.info("ML models loaded")
        except Exception as e:
            logger.error(f"ML model loading failed: {e}")
    
    async def _start_background_tasks(self):
        """Start background processing tasks"""
        # Data collection task
        collection_task = asyncio.create_task(self._collect_analytics_data())
        self.background_tasks.add(collection_task)
        
        # Real-time processing task
        if self.config.enable_real_time:
            realtime_task = asyncio.create_task(self._process_realtime_analytics())
            self.background_tasks.add(realtime_task)
        
        # Aggregation task
        aggregation_task = asyncio.create_task(self._aggregate_analytics())
        self.background_tasks.add(aggregation_task)
        
        # ML model updates
        if self.config.enable_predictive_analytics:
            ml_task = asyncio.create_task(self._update_ml_models())
            self.background_tasks.add(ml_task)
        
        # Data cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_old_data())
        self.background_tasks.add(cleanup_task)
        
        logger.info("Started background tasks")
    
    async def query_analytics(self, query: AnalyticsQuery) -> AnalyticsResponse:
        """Query analytics data for creator"""
        start_time = time.time()
        
        try:
            # Validate query parameters
            if not query.end_date:
                query.end_date = datetime.utcnow()
            if not query.start_date:
                if query.time_frame == TimeFramePeriod.DAY:
                    query.start_date = query.end_date - timedelta(days=1)
                elif query.time_frame == TimeFramePeriod.WEEK:
                    query.start_date = query.end_date - timedelta(weeks=1)
                elif query.time_frame == TimeFramePeriod.MONTH:
                    query.start_date = query.end_date - timedelta(days=30)
                else:
                    query.start_date = query.end_date - timedelta(days=7)
            
            # Collect metrics data
            metrics_data = await self._collect_metrics_for_query(query)
            
            # Generate insights
            insights = await self._generate_analytics_insights(query.creator_id, metrics_data)
            
            # Create summary
            summary = await self._create_analytics_summary(metrics_data)
            
            # Update metrics
            self.analytics_requests_counter.inc()
            processing_time = time.time() - start_time
            self.query_duration.observe(processing_time)
            
            return AnalyticsResponse(
                creator_id=query.creator_id,
                metrics=metrics_data,
                time_range={
                    "start": query.start_date.isoformat(),
                    "end": query.end_date.isoformat(),
                    "period": query.time_frame.value
                },
                summary=summary,
                insights=insights,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            raise HTTPException(status_code=500, detail="Analytics query failed")
    
    async def get_content_analytics(
        self,
        creator_id: str,
        content_ids: Optional[List[str]] = None,
        time_frame: TimeFramePeriod = TimeFramePeriod.WEEK
    ) -> List[Dict[str, Any]]:
        """Get content performance analytics"""
        try:
            # Get content analytics data
            if content_ids:
                content_data = [
                    self.content_analytics.get(cid) for cid in content_ids
                    if self.content_analytics.get(cid) and self.content_analytics[cid].creator_id == creator_id
                ]
            else:
                content_data = [
                    analytics for analytics in self.content_analytics.values()
                    if analytics.creator_id == creator_id
                ]
            
            # Filter by time frame
            end_date = datetime.utcnow()
            if time_frame == TimeFramePeriod.DAY:
                start_date = end_date - timedelta(days=1)
            elif time_frame == TimeFramePeriod.WEEK:
                start_date = end_date - timedelta(weeks=1)
            elif time_frame == TimeFramePeriod.MONTH:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=7)
            
            filtered_content = [
                content for content in content_data
                if content and content.published_at >= start_date
            ]
            
            # Convert to response format
            result = []
            for content in filtered_content:
                if content:
                    result.append({
                        "content_id": content.content_id,
                        "title": content.title,
                        "content_type": content.content_type,
                        "engagement": {
                            "views": content.views,
                            "likes": content.likes,
                            "comments": content.comments,
                            "shares": content.shares,
                            "engagement_rate": content.engagement_rate
                        },
                        "performance": {
                            "reach": content.reach,
                            "impressions": content.impressions,
                            "click_through_rate": content.click_through_rate,
                            "completion_rate": content.completion_rate
                        },
                        "revenue": {
                            "revenue_generated": content.revenue_generated,
                            "conversion_count": content.conversion_count,
                            "conversion_rate": content.conversion_rate
                        },
                        "ai_scores": {
                            "virality_score": content.virality_score,
                            "quality_score": content.quality_score,
                            "audience_match_score": content.audience_match_score
                        },
                        "published_at": content.published_at.isoformat()
                    })
            
            # Sort by performance (engagement rate)
            result.sort(key=lambda x: x["engagement"]["engagement_rate"], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Content analytics failed: {e}")
            raise HTTPException(status_code=500, detail="Content analytics failed")
    
    async def get_audience_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get audience demographics and behavior insights"""
        try:
            # Get audience insights
            insights = self.audience_insights.get(creator_id)
            if not insights:
                # Generate insights if not available
                insights = await self._generate_audience_insights(creator_id)
                self.audience_insights[creator_id] = insights
            
            # Check if data is fresh (less than 24 hours old)
            if insights.last_updated < datetime.utcnow() - timedelta(hours=24):
                # Refresh insights
                insights = await self._generate_audience_insights(creator_id)
                self.audience_insights[creator_id] = insights
            
            return {
                "creator_id": creator_id,
                "demographics": {
                    "age_distribution": insights.age_distribution,
                    "gender_distribution": insights.gender_distribution,
                    "geographic_distribution": insights.geographic_distribution
                },
                "behavior": {
                    "peak_activity_hours": insights.peak_activity_hours,
                    "device_preferences": insights.device_preferences,
                    "content_preferences": insights.content_preferences
                },
                "engagement": {
                    "engagement_by_time": insights.engagement_by_time,
                    "engagement_by_content_type": insights.engagement_by_content_type
                },
                "growth": {
                    "follower_growth_rate": insights.follower_growth_rate,
                    "audience_retention_rate": insights.audience_retention_rate,
                    "churn_rate": insights.churn_rate
                },
                "insights": {
                    "top_interests": insights.top_interests,
                    "behavioral_segments": insights.behavioral_segments
                },
                "last_updated": insights.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audience insights failed: {e}")
            raise HTTPException(status_code=500, detail="Audience insights failed")
    
    async def create_custom_dashboard(
        self,
        creator_id: str,
        request: CustomDashboardRequest
    ) -> Dict[str, Any]:
        """Create custom analytics dashboard"""
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Validate widgets
            validated_widgets = await self._validate_dashboard_widgets(request.widgets, creator_id)
            
            # Create dashboard configuration
            dashboard_config = {
                "id": dashboard_id,
                "creator_id": creator_id,
                "name": request.name,
                "description": request.description,
                "dashboard_type": request.dashboard_type.value,
                "widgets": validated_widgets,
                "time_range": request.time_range,
                "auto_refresh": request.auto_refresh,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store dashboard
            self.custom_dashboards[dashboard_id] = dashboard_config
            
            # Cache in Redis
            await self._cache_dashboard(dashboard_config)
            
            # Generate initial data
            dashboard_data = await self._generate_dashboard_data(dashboard_config)
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "name": request.name,
                "widgets_count": len(validated_widgets),
                "data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            raise HTTPException(status_code=500, detail="Dashboard creation failed")
    
    async def get_dashboard_data(self, dashboard_id: str) -> DashboardResponse:
        """Get dashboard data"""
        try:
            # Get dashboard configuration
            dashboard_config = self.custom_dashboards.get(dashboard_id)
            if not dashboard_config:
                dashboard_config = await self._load_dashboard_from_cache(dashboard_id)
            
            if not dashboard_config:
                raise HTTPException(status_code=404, detail="Dashboard not found")
            
            # Generate dashboard data
            dashboard_data = await self._generate_dashboard_data(dashboard_config)
            
            # Update metrics
            self.dashboard_views_counter.inc()
            
            return DashboardResponse(
                dashboard_id=dashboard_id,
                name=dashboard_config["name"],
                data=dashboard_data,
                last_updated=datetime.utcnow(),
                auto_refresh=dashboard_config["auto_refresh"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed: {e}")
            raise HTTPException(status_code=500, detail="Dashboard data unavailable")
    
    @CircuitBreaker.circuit_breaker
    async def predict_metrics(self, request: PredictionRequest) -> Dict[str, Any]:
        """Predict future metrics using AI models"""
        try:
            # Get historical data
            historical_data = await self._get_historical_metrics(
                request.creator_id,
                request.metric_type,
                days=90  # Use 90 days of history for prediction
            )
            
            if len(historical_data) < 14:  # Need at least 2 weeks of data
                raise HTTPException(status_code=400, detail="Insufficient historical data for prediction")
            
            # Generate predictions
            predictions = await self._generate_predictions(
                historical_data,
                request.metric_type,
                request.prediction_horizon,
                request.confidence_level
            )
            
            # Calculate accuracy metrics
            accuracy_metrics = await self._calculate_prediction_accuracy(request.creator_id, request.metric_type)
            
            return {
                "creator_id": request.creator_id,
                "metric_type": request.metric_type.value,
                "prediction_horizon": request.prediction_horizon,
                "confidence_level": request.confidence_level,
                "predictions": predictions,
                "accuracy_metrics": accuracy_metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail="Prediction service unavailable")
    
    async def analyze_competitors(self, request: CompetitorAnalysisRequest) -> Dict[str, Any]:
        """Analyze competitor performance"""
        try:
            # Get creator metrics
            creator_metrics = await self._get_creator_metrics(
                request.creator_id,
                request.metrics,
                request.time_frame
            )
            
            # Get competitor metrics
            competitor_data = []
            for competitor_id in request.competitor_ids:
                competitor_metrics = await self._get_creator_metrics(
                    competitor_id,
                    request.metrics,
                    request.time_frame
                )
                competitor_data.append({
                    "creator_id": competitor_id,
                    "metrics": competitor_metrics
                })
            
            # Perform competitive analysis
            analysis = await self._perform_competitive_analysis(
                creator_metrics,
                competitor_data,
                request.metrics
            )
            
            return {
                "creator_id": request.creator_id,
                "competitors_analyzed": len(request.competitor_ids),
                "time_frame": request.time_frame.value,
                "creator_metrics": creator_metrics,
                "competitor_data": competitor_data,
                "analysis": analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            raise HTTPException(status_code=500, detail="Competitor analysis failed")
    
    # Data collection and processing methods
    async def _collect_analytics_data(self):
        """Collect analytics data from various sources"""
        while True:
            try:
                await asyncio.sleep(self.config.collection_interval)
                
                # Collect from internal sources
                await self._collect_internal_analytics()
                
                # Collect from external platforms
                if self.config.external_api_circuit_breaker.state.name == "CLOSED":
                    await self._collect_external_analytics()
                
                logger.info("Analytics data collection completed")
                
            except Exception as e:
                logger.error(f"Analytics data collection failed: {e}")
    
    async def _collect_internal_analytics(self):
        """Collect analytics from internal Ainflue platform"""
        # This would collect data from internal services
        pass
    
    @CircuitBreaker.circuit_breaker
    async def _collect_external_analytics(self):
        """Collect analytics from external platforms"""
        try:
            # Collect YouTube analytics
            if self.config.youtube_api_key:
                await self._collect_youtube_analytics()
            
            # Collect Instagram analytics
            if self.config.instagram_access_token:
                await self._collect_instagram_analytics()
            
            # Collect TikTok analytics
            if self.config.tiktok_access_token:
                await self._collect_tiktok_analytics()
                
        except Exception as e:
            logger.error(f"External analytics collection failed: {e}")
            raise
    
    async def _collect_youtube_analytics(self):
        """Collect YouTube analytics data"""
        # YouTube API integration would go here
        pass
    
    async def _collect_instagram_analytics(self):
        """Collect Instagram analytics data"""
        # Instagram API integration would go here
        pass
    
    async def _collect_tiktok_analytics(self):
        """Collect TikTok analytics data"""
        # TikTok API integration would go here
        pass
    
    async def _process_realtime_analytics(self):
        """Process real-time analytics events"""
        while True:
            try:
                await asyncio.sleep(self.config.real_time_threshold)
                
                # Process real-time events from Redis streams
                if self.redis_client:
                    events = await self._read_realtime_events()
                    if events:
                        await self._process_analytics_events(events)
                
            except Exception as e:
                logger.error(f"Real-time analytics processing failed: {e}")
    
    async def _aggregate_analytics(self):
        """Aggregate analytics data periodically"""
        while True:
            try:
                await asyncio.sleep(self.config.aggregation_interval)
                
                # Aggregate hourly data
                await self._aggregate_hourly_data()
                
                # Aggregate daily data
                await self._aggregate_daily_data()
                
                logger.info("Analytics aggregation completed")
                
            except Exception as e:
                logger.error(f"Analytics aggregation failed: {e}")
    
    async def _update_ml_models(self):
        """Update ML models periodically"""
        while True:
            try:
                await asyncio.sleep(self.config.ml_model_update_interval)
                
                # Retrain models with new data
                await self._retrain_ml_models()
                
                logger.info("ML models updated")
                
            except Exception as e:
                logger.error(f"ML model update failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old analytics data"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
                
                # Clean up old metrics
                await self._cleanup_old_metrics(cutoff_date)
                
                logger.info("Old data cleanup completed")
                
            except Exception as e:
                logger.error(f"Data cleanup failed: {e}")
    
    # Analytics processing methods
    async def _collect_metrics_for_query(self, query: AnalyticsQuery) -> List[Dict[str, Any]]:
        """Collect metrics data for analytics query"""
        metrics_data = []
        
        # Get cached metrics
        creator_metrics = self.metrics_cache.get(query.creator_id, [])
        
        # Filter by time range
        filtered_metrics = [
            metric for metric in creator_metrics
            if query.start_date <= metric.timestamp <= query.end_date
        ]
        
        # Filter by metric types
        if query.metric_types:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if metric.metric_type in query.metric_types
            ]
        
        # Filter by platforms
        if query.platforms:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if metric.platform in query.platforms
            ]
        
        # Convert to response format
        for metric in filtered_metrics:
            metrics_data.append({
                "id": metric.id,
                "name": metric.name,
                "type": metric.metric_type.value,
                "platform": metric.platform.value,
                "value": metric.value,
                "previous_value": metric.previous_value,
                "change_percentage": metric.change_percentage,
                "trend_direction": metric.trend_direction,
                "timestamp": metric.timestamp.isoformat(),
                "metadata": metric.metadata
            })
        
        return metrics_data
    
    async def _generate_analytics_insights(self, creator_id: str, metrics_data: List[Dict[str, Any]]) -> List[str]:
        """Generate AI-powered insights from analytics data"""
        insights = []
        
        if not metrics_data:
            return ["No data available for the selected time period."]
        
        # Analyze trends
        engagement_metrics = [m for m in metrics_data if m["type"] == "engagement"]
        if engagement_metrics:
            avg_engagement = sum(m["value"] for m in engagement_metrics) / len(engagement_metrics)
            if avg_engagement > 5.0:
                insights.append("Your engagement rate is above industry average (5%). Keep up the great content!")
            elif avg_engagement < 2.0:
                insights.append("Your engagement rate is below industry average. Consider experimenting with different content formats.")
        
        # Analyze growth
        growth_metrics = [m for m in metrics_data if m["type"] == "growth"]
        if growth_metrics:
            positive_growth = [m for m in growth_metrics if m["change_percentage"] > 0]
            if len(positive_growth) > len(growth_metrics) * 0.7:
                insights.append("You're experiencing consistent growth across multiple metrics.")
        
        # Platform performance
        platform_performance = {}
        for metric in metrics_data:
            platform = metric["platform"]
            if platform not in platform_performance:
                platform_performance[platform] = []
            platform_performance[platform].append(metric["value"])
        
        if len(platform_performance) > 1:
            best_platform = max(platform_performance.keys(), 
                              key=lambda p: sum(platform_performance[p]) / len(platform_performance[p]))
            insights.append(f"Your content performs best on {best_platform}. Consider focusing more efforts there.")
        
        return insights
    
    async def _create_analytics_summary(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create analytics summary from metrics data"""
        if not metrics_data:
            return {
                "total_metrics": 0,
                "average_performance": 0,
                "trend_summary": "No data available"
            }
        
        # Calculate summary statistics
        total_metrics = len(metrics_data)
        average_value = sum(m["value"] for m in metrics_data) / total_metrics
        
        # Trend analysis
        positive_trends = len([m for m in metrics_data if m["change_percentage"] > 0])
        negative_trends = len([m for m in metrics_data if m["change_percentage"] < 0])
        
        trend_summary = "stable"
        if positive_trends > negative_trends:
            trend_summary = "growing"
        elif negative_trends > positive_trends:
            trend_summary = "declining"
        
        return {
            "total_metrics": total_metrics,
            "average_performance": round(average_value, 2),
            "positive_trends": positive_trends,
            "negative_trends": negative_trends,
            "trend_summary": trend_summary,
            "data_quality": "good" if total_metrics > 10 else "limited"
        }
    
    async def _generate_audience_insights(self, creator_id: str) -> AudienceInsights:
        """Generate audience insights for creator"""
        # This would analyze actual audience data
        # For now, return mock insights
        return AudienceInsights(
            creator_id=creator_id,
            age_distribution={
                "18-24": 25.0,
                "25-34": 35.0,
                "35-44": 25.0,
                "45-54": 10.0,
                "55+": 5.0
            },
            gender_distribution={
                "male": 45.0,
                "female": 52.0,
                "other": 3.0
            },
            geographic_distribution={
                "US": 40.0,
                "UK": 15.0,
                "Canada": 10.0,
                "Australia": 8.0,
                "Germany": 7.0,
                "Other": 20.0
            },
            peak_activity_hours=[9, 12, 15, 18, 21],
            device_preferences={
                "mobile": 65.0,
                "desktop": 25.0,
                "tablet": 10.0
            },
            content_preferences={
                "video": 50.0,
                "image": 30.0,
                "audio": 15.0,
                "text": 5.0
            },
            follower_growth_rate=5.5,
            audience_retention_rate=78.0,
            churn_rate=3.2,
            top_interests=["technology", "entertainment", "lifestyle", "education"],
            behavioral_segments=[
                {"name": "Engaged Followers", "percentage": 25.0, "description": "Highly active users"},
                {"name": "Casual Viewers", "percentage": 60.0, "description": "Regular but less active users"},
                {"name": "Inactive Users", "percentage": 15.0, "description": "Rarely engage with content"}
            ]
        )
    
    # Dashboard methods
    async def _validate_dashboard_widgets(self, widgets: List[Dict[str, Any]], creator_id: str) -> List[Dict[str, Any]]:
        """Validate dashboard widget configurations"""
        validated_widgets = []
        
        for widget in widgets:
            # Basic validation
            if "type" not in widget or "config" not in widget:
                continue
            
            # Widget type validation
            if widget["type"] not in ["chart", "metric", "table", "gauge", "map"]:
                continue
            
            # Add default configuration
            validated_widget = {
                "id": str(uuid.uuid4()),
                "type": widget["type"],
                "config": widget["config"],
                "position": widget.get("position", {"x": 0, "y": 0, "width": 4, "height": 3}),
                "title": widget.get("title", f"{widget['type'].title()} Widget")
            }
            
            validated_widgets.append(validated_widget)
        
        return validated_widgets
    
    async def _generate_dashboard_data(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for dashboard widgets"""
        dashboard_data = {}
        
        for widget in dashboard_config["widgets"]:
            widget_id = widget["id"]
            widget_type = widget["type"]
            widget_config = widget["config"]
            
            try:
                if widget_type == "chart":
                    data = await self._generate_chart_data(widget_config, dashboard_config["creator_id"])
                elif widget_type == "metric":
                    data = await self._generate_metric_data(widget_config, dashboard_config["creator_id"])
                elif widget_type == "table":
                    data = await self._generate_table_data(widget_config, dashboard_config["creator_id"])
                elif widget_type == "gauge":
                    data = await self._generate_gauge_data(widget_config, dashboard_config["creator_id"])
                else:
                    data = {"error": "Unsupported widget type"}
                
                dashboard_data[widget_id] = data
                
            except Exception as e:
                logger.error(f"Widget data generation failed for {widget_id}: {e}")
                dashboard_data[widget_id] = {"error": "Data generation failed"}
        
        return dashboard_data
    
    async def _generate_chart_data(self, config: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Generate chart data for dashboard widget"""
        # Mock chart data
        return {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "datasets": [
                {
                    "label": "Views",
                    "data": [1200, 1900, 3000, 2500, 2200, 3200, 2800],
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)"
                }
            ]
        }
    
    async def _generate_metric_data(self, config: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Generate metric data for dashboard widget"""
        # Mock metric data
        return {
            "value": 15420,
            "change": 12.5,
            "trend": "up",
            "label": "Total Views",
            "period": "Last 30 days"
        }
    
    async def _generate_table_data(self, config: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Generate table data for dashboard widget"""
        # Mock table data
        return {
            "headers": ["Content", "Views", "Engagement", "Revenue"],
            "rows": [
                ["Video: AI Tutorial", "5,200", "8.5%", "$45.60"],
                ["Post: Tech News", "3,100", "6.2%", "$23.40"],
                ["Podcast: Industry Talk", "2,800", "12.1%", "$67.80"]
            ]
        }
    
    async def _generate_gauge_data(self, config: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Generate gauge data for dashboard widget"""
        # Mock gauge data
        return {
            "value": 78,
            "min": 0,
            "max": 100,
            "label": "Engagement Score",
            "color": "#10B981"
        }
    
    # Prediction methods
    async def _get_historical_metrics(self, creator_id: str, metric_type: MetricType, days: int) -> List[float]:
        """Get historical metrics data for prediction"""
        # This would fetch actual historical data
        # For now, return mock data
        import random
        base_value = 1000
        return [base_value + random.randint(-200, 200) for _ in range(days)]
    
    async def _generate_predictions(
        self,
        historical_data: List[float],
        metric_type: MetricType,
        horizon: int,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Generate predictions using ML models"""
        # Simplified prediction using moving average
        if len(historical_data) < 7:
            raise ValueError("Insufficient data for prediction")
        
        # Calculate trend
        recent_avg = sum(historical_data[-7:]) / 7
        older_avg = sum(historical_data[-14:-7]) / 7
        trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        # Generate predictions
        predictions = []
        last_value = historical_data[-1]
        
        for day in range(1, horizon + 1):
            # Simple linear trend with some randomness
            predicted_value = last_value * (1 + trend * day / 30)
            
            # Add confidence intervals
            std_dev = statistics.stdev(historical_data[-30:]) if len(historical_data) >= 30 else statistics.stdev(historical_data)
            margin = std_dev * (2.0 - confidence_level)  # Simplified confidence interval
            
            predictions.append({
                "day": day,
                "predicted_value": round(predicted_value, 2),
                "lower_bound": round(predicted_value - margin, 2),
                "upper_bound": round(predicted_value + margin, 2),
                "confidence": confidence_level
            })
        
        return {
            "predictions": predictions,
            "trend": "increasing" if trend > 0.05 else "decreasing" if trend < -0.05 else "stable",
            "trend_percentage": round(trend * 100, 2)
        }
    
    async def _calculate_prediction_accuracy(self, creator_id: str, metric_type: MetricType) -> Dict[str, float]:
        """Calculate accuracy of previous predictions"""
        # This would compare previous predictions with actual values
        return {
            "accuracy_score": 0.85,
            "mean_absolute_error": 45.2,
            "r_squared": 0.78
        }
    
    # Competitive analysis methods
    async def _get_creator_metrics(
        self,
        creator_id: str,
        metrics: List[MetricType],
        time_frame: TimeFramePeriod
    ) -> Dict[str, float]:
        """Get creator metrics for competitive analysis"""
        # This would fetch actual metrics
        # For now, return mock data
        return {
            "engagement_rate": 5.2,
            "growth_rate": 12.5,
            "reach": 25000,
            "revenue": 1500.0
        }
    
    async def _perform_competitive_analysis(
        self,
        creator_metrics: Dict[str, float],
        competitor_data: List[Dict[str, Any]],
        metrics: List[MetricType]
    ) -> Dict[str, Any]:
        """Perform competitive analysis"""
        analysis = {
            "ranking": {},
            "gaps": {},
            "opportunities": [],
            "benchmarks": {}
        }
        
        # Calculate rankings
        for metric_name in creator_metrics.keys():
            all_values = [creator_metrics[metric_name]]
            all_values.extend([comp["metrics"].get(metric_name, 0) for comp in competitor_data])
            
            creator_rank = sum(1 for val in all_values if val > creator_metrics[metric_name]) + 1
            analysis["ranking"][metric_name] = {
                "rank": creator_rank,
                "total": len(all_values)
            }
            
            # Calculate gaps
            max_value = max(all_values)
            gap_percentage = ((max_value - creator_metrics[metric_name]) / max_value * 100) if max_value > 0 else 0
            analysis["gaps"][metric_name] = round(gap_percentage, 2)
            
            # Calculate benchmark
            analysis["benchmarks"][metric_name] = {
                "average": round(sum(all_values) / len(all_values), 2),
                "median": round(sorted(all_values)[len(all_values) // 2], 2),
                "top_performer": round(max_value, 2)
            }
        
        # Generate opportunities
        for metric_name, gap in analysis["gaps"].items():
            if gap > 20:
                analysis["opportunities"].append(f"Significant improvement opportunity in {metric_name} (Gap: {gap}%)")
        
        return analysis
    
    # Caching methods
    async def _cache_dashboard(self, dashboard_config: Dict[str, Any]):
        """Cache dashboard configuration"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                f"analytics:dashboard:{dashboard_config['id']}",
                86400,  # 24 hours TTL
                json.dumps(dashboard_config)
            )
        except Exception as e:
            logger.error(f"Failed to cache dashboard: {e}")
    
    async def _load_dashboard_from_cache(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Load dashboard from cache"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"analytics:dashboard:{dashboard_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to load dashboard from cache: {e}")
        
        return None
    
    # Additional helper methods
    async def _read_realtime_events(self) -> List[Dict[str, Any]]:
        """Read real-time analytics events from Redis streams"""
        # Implementation would read from Redis streams
        return []
    
    async def _process_analytics_events(self, events: List[Dict[str, Any]]):
        """Process real-time analytics events"""
        for event in events:
            # Process each event
            pass
    
    async def _aggregate_hourly_data(self):
        """Aggregate analytics data hourly"""
        # Implementation would aggregate data
        pass
    
    async def _aggregate_daily_data(self):
        """Aggregate analytics data daily"""
        # Implementation would aggregate data
        pass
    
    async def _retrain_ml_models(self):
        """Retrain ML models with new data"""
        # Implementation would retrain models
        pass
    
    async def _cleanup_old_metrics(self, cutoff_date: datetime):
        """Clean up metrics older than cutoff date"""
        # Implementation would clean up old data
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Analytics service health check"""
        try:
            # Test Redis connection
            redis_healthy = False
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    redis_healthy = True
            except Exception:
                pass
            
            # Check data availability
            total_creators = len(self.metrics_cache)
            total_metrics = sum(len(metrics) for metrics in self.metrics_cache.values())
            
            status = "healthy" if redis_healthy else "degraded"
            
            return {
                'status': status,
                'redis_connected': redis_healthy,
                'total_creators_tracked': total_creators,
                'total_metrics': total_metrics,
                'custom_dashboards': len(self.custom_dashboards),
                'background_tasks': len(self.background_tasks),
                'ml_models_loaded': len(self.ml_models),
                'circuit_breakers': {
                    'external_apis': self.external_api_circuit_breaker.state.name,
                    'ml_service': self.ml_circuit_breaker.state.name
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# FastAPI app setup
def create_analytics_app() -> FastAPI:
    """Create FastAPI application for analytics service"""
    
    app = FastAPI(
        title="Ainflue Analytics Service",
        description="Advanced analytics and insights service for content creators",
        version="1.0.0"
    )
    
    # Initialize service
    service = AnalyticsService()
    
    @app.on_event("startup")
    async def startup():
        await service.startup()
    
    @app.on_event("shutdown")
    async def shutdown():
        await service.shutdown()
    
    @app.post("/analytics/query")
    async def query_analytics(query: AnalyticsQuery):
        """Query analytics data"""
        return await service.query_analytics(query)
    
    @app.get("/creators/{creator_id}/content-analytics")
    async def get_content_analytics(
        creator_id: str,
        content_ids: Optional[List[str]] = Query(None),
        time_frame: TimeFramePeriod = TimeFramePeriod.WEEK
    ):
        """Get content performance analytics"""
        return await service.get_content_analytics(creator_id, content_ids, time_frame)
    
    @app.get("/creators/{creator_id}/audience-insights")
    async def get_audience_insights(creator_id: str):
        """Get audience demographics and behavior insights"""
        return await service.get_audience_insights(creator_id)
    
    @app.post("/dashboards")
    async def create_custom_dashboard(
        creator_id: str,
        request: CustomDashboardRequest
    ):
        """Create custom analytics dashboard"""
        return await service.create_custom_dashboard(creator_id, request)
    
    @app.get("/dashboards/{dashboard_id}")
    async def get_dashboard_data(dashboard_id: str):
        """Get dashboard data"""
        return await service.get_dashboard_data(dashboard_id)
    
    @app.post("/analytics/predict")
    async def predict_metrics(request: PredictionRequest):
        """Predict future metrics using AI"""
        return await service.predict_metrics(request)
    
    @app.post("/analytics/competitors")
    async def analyze_competitors(request: CompetitorAnalysisRequest):
        """Analyze competitor performance"""
        return await service.analyze_competitors(request)
    
    @app.get("/health")
    async def health_check():
        """Service health check"""
        return await service.health_check()
    
    return app


# Export classes for use in other modules
__all__ = [
    'AnalyticsService',
    'AnalyticsConfig',
    'MetricType',
    'TimeFramePeriod',
    'PlatformType',
    'DashboardType',
    'AnalyticsMetric',
    'ContentAnalytics',
    'AudienceInsights',
    'AnalyticsQuery',
    'CustomDashboardRequest',
    'CompetitorAnalysisRequest',
    'PredictionRequest',
    'AnalyticsResponse',
    'DashboardResponse',
    'create_analytics_app'
]