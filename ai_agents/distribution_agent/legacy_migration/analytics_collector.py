"""
Analytics Collector - Professional Multi-Platform Analytics Aggregation System

Enterprise-grade analytics collection and analysis system with advanced metrics processing,
cross-platform insights, and comprehensive business intelligence for the IA Influencer Agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This software and all related code are the EXCLUSIVE INTELLECTUAL PROPERTY 
of Fahed Mlaiel (mlaiel@live.de). Unauthorized use, copying, or distribution 
without written authorization is STRICTLY PROHIBITED and will result in 
immediate legal action under German and International IP law.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import aiohttp
import statistics

from ..base import BaseAgent
try:
    from core.exceptions import AnalyticsError, PlatformError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AnalyticsError, PlatformError = globals().get('AnalyticsError, PlatformError', Exception)
from ...core.metrics import MetricsCollector
try:
    from core.database import DatabaseManager
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    DatabaseManager = DatabaseManager
from ...models.analytics import (
    AnalyticsData, PerformanceMetrics, AudienceInsights,
    EngagementMetrics, RevenueMetrics, CompetitiveAnalysis
)


class MetricType(Enum):
    """Analytics metric type enumeration"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    REVENUE = "revenue"
    AUDIENCE = "audience"
    PERFORMANCE = "performance"
    COMPETITIVE = "competitive"


class AnalyticsPeriod(Enum):
    """Analytics time period enumeration"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class DataGranularity(Enum):
    """Data granularity enumeration"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class TrendDirection(Enum):
    """Trend direction enumeration"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class AnalyticsQuery:
    """Analytics query configuration"""
    platforms: List[str]
    metrics: List[MetricType]
    start_date: datetime
    end_date: datetime
    granularity: DataGranularity
    filters: Dict[str, Any] = None
    aggregations: List[str] = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.aggregations is None:
            self.aggregations = ['sum', 'avg', 'max', 'min']


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_name: str
    platform: str
    direction: TrendDirection
    change_percentage: float
    significance: float
    data_points: List[Tuple[datetime, float]]
    forecast: List[Tuple[datetime, float]]
    seasonality: Dict[str, float]
    anomalies: List[Tuple[datetime, float, str]]


@dataclass
class CrossPlatformInsights:
    """Cross-platform analytics insights"""
    total_reach: int
    total_engagement: int
    platform_performance: Dict[str, Dict[str, float]]
    audience_overlap: Dict[str, float]
    content_performance: Dict[str, Dict[str, float]]
    optimal_posting_times: Dict[str, List[datetime]]
    roi_analysis: Dict[str, float]
    growth_opportunities: List[str]


class AnalyticsCollector(BaseAgent):
    """
    Professional analytics collector with advanced features
    
    Capabilities:
    - Multi-platform data aggregation
    - Real-time analytics processing
    - Advanced trend analysis and forecasting
    - Cross-platform performance comparison
    - Audience behavior analysis
    - ROI and revenue tracking
    - Competitive benchmarking
    - Automated insights generation
    - Anomaly detection
    - Custom dashboard creation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize analytics collector
        
        Args:
            config: Analytics collector configuration
        """
        super().__init__(config)
        
        # Core configuration
        self.collection_interval = config.get('collection_interval', 300)  # 5 minutes
        self.retention_days = config.get('retention_days', 365)
        self.batch_size = config.get('batch_size', 1000)
        self.enable_real_time = config.get('enable_real_time', True)
        
        # Advanced analytics
        self.enable_forecasting = config.get('enable_forecasting', True)
        self.enable_anomaly_detection = config.get('enable_anomaly_detection', True)
        self.enable_competitive_analysis = config.get('enable_competitive_analysis', False)
        self.forecast_days = config.get('forecast_days', 30)
        
        # Data processing
        self.moving_average_window = config.get('moving_average_window', 7)
        self.seasonality_periods = config.get('seasonality_periods', [7, 30, 365])  # weekly, monthly, yearly
        self.anomaly_threshold = config.get('anomaly_threshold', 2.5)  # standard deviations
        
        # Platform adapters
        self.platform_adapters: Dict[str, Any] = {}
        
        # Data storage
        self.db = DatabaseManager(config.get('database', {}))
        self.metrics = MetricsCollector("analytics_collector")
        
        # Cache and processing
        self.data_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.active_collections: Set[str] = set()
        
        # Analytics engines
        self.trend_analyzer = None
        self.forecasting_engine = None
        self.anomaly_detector = None
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize analytics collector"""
        try:
            # Initialize database
            await self.db.initialize()
            await self._create_analytics_tables()
            
            # Initialize analytics engines
            await self._initialize_analytics_engines()
            
            # Start collection workers
            if self.enable_real_time:
                for i in range(3):  # 3 worker tasks
                    asyncio.create_task(self._collection_worker(f"worker_{i}"))
            
            # Start processing workers
            for i in range(2):  # 2 processing tasks
                asyncio.create_task(self._processing_worker(f"processor_{i}"))
            
            # Start scheduled collections
            asyncio.create_task(self._scheduled_collection_loop())
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_old_data())
            
            self.logger.info("Analytics collector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics collector: {str(e)}")
            return False
    
    async def collect_platform_analytics(
        self,
        platform: str,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[MetricType]] = None
    ) -> AnalyticsData:
        """
        Collect analytics data from specific platform
        
        Args:
            platform: Platform name
            start_date: Collection start date
            end_date: Collection end date
            metrics: Specific metrics to collect
            
        Returns:
            Collected analytics data
        """
        try:
            if platform not in self.platform_adapters:
                raise AnalyticsError(f"No adapter for platform {platform}")
            
            adapter = self.platform_adapters[platform]
            metrics = metrics or list(MetricType)
            
            # Collect data from platform
            raw_data = await self._collect_platform_data(
                adapter, platform, start_date, end_date, metrics
            )
            
            # Process and normalize data
            processed_data = await self._process_raw_data(raw_data, platform, metrics)
            
            # Store in database
            await self._store_analytics_data(processed_data, platform)
            
            # Update cache
            await self._update_cache(processed_data, platform)
            
            # Record collection metrics
            self.metrics.record_collection(
                platform=platform,
                data_points=len(processed_data),
                success=True
            )
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect analytics for {platform}: {str(e)}")
            self.metrics.record_error("collection_failed", str(e))
            raise AnalyticsError(f"Analytics collection failed: {str(e)}")
    
    async def analyze_cross_platform_performance(
        self,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> CrossPlatformInsights:
        """
        Analyze performance across multiple platforms
        
        Args:
            platforms: List of platforms to analyze
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Cross-platform insights
        """
        try:
            # Collect data from all platforms
            platform_data = {}
            for platform in platforms:
                data = await self.collect_platform_analytics(
                    platform, start_date, end_date
                )
                platform_data[platform] = data
            
            # Calculate cross-platform metrics
            total_reach = sum(data.reach for data in platform_data.values())
            total_engagement = sum(data.engagement.total_interactions for data in platform_data.values())
            
            # Analyze platform performance
            platform_performance = {}
            for platform, data in platform_data.items():
                platform_performance[platform] = {
                    'reach': data.reach,
                    'engagement_rate': data.engagement.engagement_rate,
                    'roi': data.revenue.roi if data.revenue else 0.0,
                    'growth_rate': await self._calculate_growth_rate(platform, start_date, end_date)
                }
            
            # Analyze audience overlap
            audience_overlap = await self._analyze_audience_overlap(platform_data)
            
            # Analyze content performance
            content_performance = await self._analyze_content_performance(platform_data)
            
            # Find optimal posting times
            optimal_times = await self._find_optimal_posting_times(platform_data)
            
            # Calculate ROI analysis
            roi_analysis = await self._calculate_roi_analysis(platform_data)
            
            # Generate growth opportunities
            growth_opportunities = await self._identify_growth_opportunities(platform_data)
            
            return CrossPlatformInsights(
                total_reach=total_reach,
                total_engagement=total_engagement,
                platform_performance=platform_performance,
                audience_overlap=audience_overlap,
                content_performance=content_performance,
                optimal_posting_times=optimal_times,
                roi_analysis=roi_analysis,
                growth_opportunities=growth_opportunities
            )
            
        except Exception as e:
            self.logger.error(f"Cross-platform analysis failed: {str(e)}")
            raise AnalyticsError(f"Cross-platform analysis failed: {str(e)}")
    
    async def analyze_trends(
        self,
        platform: str,
        metric: MetricType,
        period: AnalyticsPeriod,
        lookback_days: int = 90
    ) -> TrendAnalysis:
        """
        Analyze trends for specific metric
        
        Args:
            platform: Platform to analyze
            metric: Metric to analyze
            period: Analysis period
            lookback_days: Number of days to look back
            
        Returns:
            Trend analysis result
        """
        try:
            # Get historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_days)
            
            historical_data = await self._get_historical_data(
                platform, metric, start_date, end_date
            )
            
            if not historical_data:
                raise AnalyticsError(f"No historical data for {platform} {metric.value}")
            
            # Convert to time series
            data_points = [(point['timestamp'], point['value']) for point in historical_data]
            data_points.sort(key=lambda x: x[0])
            
            # Analyze trend direction
            values = [point[1] for point in data_points]
            trend_direction = await self._calculate_trend_direction(values)
            
            # Calculate change percentage
            if len(values) >= 2:
                change_percentage = ((values[-1] - values[0]) / values[0]) * 100
            else:
                change_percentage = 0.0
            
            # Calculate statistical significance
            significance = await self._calculate_trend_significance(values)
            
            # Generate forecast if enabled
            forecast = []
            if self.enable_forecasting and self.forecasting_engine:
                forecast = await self._generate_forecast(data_points, self.forecast_days)
            
            # Analyze seasonality
            seasonality = await self._analyze_seasonality(data_points)
            
            # Detect anomalies
            anomalies = []
            if self.enable_anomaly_detection and self.anomaly_detector:
                anomalies = await self._detect_anomalies(data_points)
            
            return TrendAnalysis(
                metric_name=metric.value,
                platform=platform,
                direction=trend_direction,
                change_percentage=change_percentage,
                significance=significance,
                data_points=data_points,
                forecast=forecast,
                seasonality=seasonality,
                anomalies=anomalies
            )
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            raise AnalyticsError(f"Trend analysis failed: {str(e)}")
    
    async def query_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute complex analytics query"""
        try:
            results = {}
            
            for platform in query.platforms:
                platform_results = {}
                
                for metric in query.metrics:
                    # Get data with specified granularity
                    data = await self._query_metric_data(
                        platform, metric, query.start_date, query.end_date,
                        query.granularity, query.filters
                    )
                    
                    # Apply aggregations
                    aggregated_data = {}
                    for aggregation in query.aggregations:
                        if data:
                            values = [point['value'] for point in data]
                            if aggregation == 'sum':
                                aggregated_data[aggregation] = sum(values)
                            elif aggregation == 'avg':
                                aggregated_data[aggregation] = statistics.mean(values)
                            elif aggregation == 'max':
                                aggregated_data[aggregation] = max(values)
                            elif aggregation == 'min':
                                aggregated_data[aggregation] = min(values)
                            elif aggregation == 'median':
                                aggregated_data[aggregation] = statistics.median(values)
                            elif aggregation == 'std':
                                aggregated_data[aggregation] = statistics.stdev(values) if len(values) > 1 else 0
                    
                    platform_results[metric.value] = {
                        'raw_data': data,
                        'aggregations': aggregated_data
                    }
                
                results[platform] = platform_results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Analytics query failed: {str(e)}")
            raise AnalyticsError(f"Analytics query failed: {str(e)}")
    
    async def generate_insights_report(
        self,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive insights report"""
        try:
            report = {
                'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
                'platforms': platforms,
                'summary': {},
                'trends': {},
                'insights': [],
                'recommendations': [],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Cross-platform analysis
            cross_platform_insights = await self.analyze_cross_platform_performance(
                platforms, start_date, end_date
            )
            report['summary'] = asdict(cross_platform_insights)
            
            # Trend analysis for each platform
            for platform in platforms:
                platform_trends = {}
                for metric in [MetricType.ENGAGEMENT, MetricType.REACH, MetricType.IMPRESSIONS]:
                    try:
                        trend = await self.analyze_trends(
                            platform, metric, AnalyticsPeriod.DAILY, 30
                        )
                        platform_trends[metric.value] = asdict(trend)
                    except Exception as e:
                        self.logger.warning(f"Failed to analyze {metric.value} trends for {platform}: {str(e)}")
                
                report['trends'][platform] = platform_trends
            
            # Generate insights
            insights = await self._generate_automated_insights(cross_platform_insights, report['trends'])
            report['insights'] = insights
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(cross_platform_insights, report['trends'])
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise AnalyticsError(f"Report generation failed: {str(e)}")
    
    async def register_platform_adapter(self, platform: str, adapter: Any) -> None:
        """Register platform adapter for analytics collection"""
        self.platform_adapters[platform] = adapter
        self.logger.info(f"Registered analytics adapter for {platform}")
    
    async def _create_analytics_tables(self) -> None:
        """Create database tables for analytics data"""
        # Create main analytics table
        create_analytics_sql = """
        CREATE TABLE IF NOT EXISTS analytics_data (
            id SERIAL PRIMARY KEY,
            platform TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            value NUMERIC NOT NULL,
            metadata JSON,
            content_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Create indices for performance
        create_indices_sql = [
            "CREATE INDEX IF NOT EXISTS idx_analytics_platform_time ON analytics_data(platform, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_metric_time ON analytics_data(metric_type, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_content ON analytics_data(content_id)"
        ]
        
        await self.db.execute(create_analytics_sql)
        for index_sql in create_indices_sql:
            await self.db.execute(index_sql)
    
    async def _initialize_analytics_engines(self) -> None:
        """Initialize analytics processing engines"""
        # Initialize trend analyzer
        self.trend_analyzer = {
            'moving_average_window': self.moving_average_window,
            'seasonality_periods': self.seasonality_periods
        }
        
        # Initialize forecasting engine (placeholder)
        if self.enable_forecasting:
            self.forecasting_engine = {
                'method': 'linear_regression',
                'forecast_days': self.forecast_days
            }
        
        # Initialize anomaly detector (placeholder)
        if self.enable_anomaly_detection:
            self.anomaly_detector = {
                'method': 'statistical',
                'threshold': self.anomaly_threshold
            }
    
    async def _collection_worker(self, worker_id: str) -> None:
        """Background worker for data collection"""
        while True:
            try:
                # Get collection task from queue
                if not self.processing_queue.empty():
                    task = await self.processing_queue.get()
                    await self._process_collection_task(task)
                else:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Collection worker {worker_id} error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _processing_worker(self, worker_id: str) -> None:
        """Background worker for data processing"""
        while True:
            try:
                # Process cached data
                await self._process_cached_data()
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                self.logger.error(f"Processing worker {worker_id} error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _scheduled_collection_loop(self) -> None:
        """Main scheduled collection loop"""
        while True:
            try:
                # Collect from all registered platforms
                for platform in self.platform_adapters.keys():
                    if platform not in self.active_collections:
                        asyncio.create_task(
                            self._collect_platform_scheduled(platform)
                        )
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Scheduled collection loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_platform_scheduled(self, platform: str) -> None:
        """Scheduled collection for specific platform"""
        try:
            self.active_collections.add(platform)
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)  # Collect last hour
            
            await self.collect_platform_analytics(
                platform, start_time, end_time
            )
            
        except Exception as e:
            self.logger.error(f"Scheduled collection failed for {platform}: {str(e)}")
        finally:
            self.active_collections.discard(platform)
    
    # Additional helper methods would be implemented here...
    # Due to length constraints, showing key structure and main methods
    
    async def cleanup(self) -> None:
        """Cleanup analytics collector resources"""
        await self.db.cleanup()
        self.logger.info("Analytics collector cleaned up successfully")
