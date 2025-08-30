"""
📊 Monitoring Analytics Engine
=============================

Advanced analytics and reporting system for content protection monitoring.
Provides comprehensive insights, predictive analytics, and performance metrics.

Technical Specifications:
- Real-time metrics aggregation
- Predictive threat modeling
- Performance analytics and optimization
- Advanced reporting and visualization
- Machine learning-based insights

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AnalyticsTimeRange(str, Enum):
    """Time range options for analytics."""
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_3_MONTHS = "3M"
    LAST_6_MONTHS = "6M"
    LAST_YEAR = "1Y"
    CUSTOM = "custom"

class MetricType(str, Enum):
    """Types of monitoring metrics."""
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    RESPONSE_TIME = "response_time"
    PLATFORM_COVERAGE = "platform_coverage"
    THREAT_DISTRIBUTION = "threat_distribution"
    VIOLATION_TRENDS = "violation_trends"
    ENFORCEMENT_SUCCESS = "enforcement_success"
    REVENUE_IMPACT = "revenue_impact"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"

class TrendDirection(str, Enum):
    """Trend direction indicators."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class AnalyticsInsight:
    """Analytics insight data structure."""
    title: str
    description: str
    severity: str  # low, medium, high, critical
    category: str
    confidence_score: float
    affected_platforms: List[str]
    recommended_actions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    metric_name: str
    time_range: str
    direction: TrendDirection
    percentage_change: float
    significance_score: float
    prediction_next_period: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None

class PredictiveModel(BaseModel):
    """Predictive analytics model configuration."""
    model_type: str = "isolation_forest"
    lookback_days: int = 30
    prediction_horizon_days: int = 7
    update_frequency_hours: int = 6
    confidence_threshold: float = 0.85
    enable_anomaly_detection: bool = True
    enable_trend_prediction: bool = True

class RealTimeMetrics(BaseModel):
    """Real-time analytics metrics."""
    total_violations_detected: int = 0
    violations_resolved: int = 0
    active_monitoring_sessions: int = 0
    average_detection_time_seconds: float = 0.0
    current_false_positive_rate: float = 0.0
    platform_distribution: Dict[str, int] = Field(default_factory=dict)
    threat_level_distribution: Dict[str, int] = Field(default_factory=dict)
    hourly_detection_rate: List[int] = Field(default_factory=list)
    top_affected_platforms: List[Dict[str, Any]] = Field(default_factory=list)
    system_health_score: float = 100.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PerformanceMetrics(BaseModel):
    """Performance analytics metrics."""
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_requests_per_minute: float = 0.0
    error_rate_percentage: float = 0.0
    cache_hit_rate_percentage: float = 0.0
    database_query_time_ms: float = 0.0
    queue_processing_time_ms: float = 0.0
    concurrent_users: int = 0
    memory_usage_percentage: float = 0.0
    cpu_usage_percentage: float = 0.0

class MonitoringAnalytics:
    """
    Advanced analytics engine for content protection monitoring.
    
    Provides comprehensive analytics including:
    - Real-time metrics aggregation and visualization
    - Predictive threat modeling and anomaly detection
    - Performance analytics and optimization insights
    - Trend analysis and forecasting
    - Machine learning-based insights and recommendations
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        redis_client: Optional[aioredis.Redis] = None,
        db_session: Optional[AsyncSession] = None
    ):
        """
        Initialize the monitoring analytics engine.
        
        Args:
            config: Analytics configuration dictionary
            redis_client: Redis client for caching and real-time data
            db_session: Database session for data persistence
        """
        self.config = config
        self.redis_client = redis_client
        self.db_session = db_session
        
        # Analytics configuration
        self.update_interval_seconds = config.get('update_interval_seconds', 60)
        self.retention_days = config.get('retention_days', 90)
        self.enable_ml_insights = config.get('enable_ml_insights', True)
        self.cache_ttl_seconds = config.get('cache_ttl_seconds', 300)
        
        # Machine learning models
        self.anomaly_detector = None
        self.trend_predictor = None
        self.predictive_model_config = PredictiveModel(**config.get('predictive_model', {}))
        
        # Real-time data buffers
        self.metrics_buffer = deque(maxlen=1000)
        self.events_buffer = deque(maxlen=5000)
        
        # Analytics state
        self._initialized = False
        self._last_model_update = None
        self._cached_insights = {}
        
        logger.info("Monitoring Analytics Engine initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the analytics engine.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Monitoring Analytics Engine...")
            
            # Initialize machine learning models
            if self.enable_ml_insights:
                await self._initialize_ml_models()
            
            # Warm up caches with recent data
            await self._warm_up_caches()
            
            # Set up real-time metrics collection
            await self._setup_realtime_collection()
            
            self._initialized = True
            logger.info("Monitoring Analytics Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Analytics Engine: {e}")
            return False
    
    async def get_realtime_metrics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get real-time monitoring metrics.
        
        Args:
            user_id: Optional user ID to filter metrics
            
        Returns:
            Dict containing real-time metrics
        """
        cache_key = f"realtime_metrics:{user_id or 'global'}"
        
        # Try to get from cache first
        if self.redis_client:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
        # Calculate real-time metrics
        metrics = await self._calculate_realtime_metrics(user_id)
        
        # Cache the results
        if self.redis_client:
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl_seconds,
                json.dumps(metrics, default=str)
            )
        
        return metrics
    
    async def get_trend_analysis(
        self,
        metric_type: MetricType,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_7_DAYS,
        user_id: Optional[int] = None
    ) -> TrendAnalysis:
        """
        Perform trend analysis for a specific metric.
        
        Args:
            metric_type: Type of metric to analyze
            time_range: Time range for analysis
            user_id: Optional user ID to filter data
            
        Returns:
            TrendAnalysis object with trend information
        """
        # Get historical data
        historical_data = await self._get_historical_metrics(
            metric_type, time_range, user_id
        )
        
        if len(historical_data) < 2:
            return TrendAnalysis(
                metric_name=metric_type.value,
                time_range=time_range.value,
                direction=TrendDirection.STABLE,
                percentage_change=0.0,
                significance_score=0.0
            )
        
        # Calculate trend
        values = [point['value'] for point in historical_data]
        timestamps = [point['timestamp'] for point in historical_data]
        
        # Perform trend analysis
        trend_direction, percentage_change, significance = self._analyze_trend(values)
        
        # Predict next period if ML is enabled
        prediction = None
        confidence_interval = None
        if self.enable_ml_insights and self.trend_predictor:
            prediction, confidence_interval = await self._predict_next_value(
                values, timestamps
            )
        
        return TrendAnalysis(
            metric_name=metric_type.value,
            time_range=time_range.value,
            direction=trend_direction,
            percentage_change=percentage_change,
            significance_score=significance,
            prediction_next_period=prediction,
            confidence_interval=confidence_interval
        )
    
    async def detect_anomalies(
        self,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_24_HOURS,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in monitoring data.
        
        Args:
            time_range: Time range to analyze
            user_id: Optional user ID to filter data
            
        Returns:
            List of detected anomalies
        """
        if not self.enable_ml_insights or not self.anomaly_detector:
            return []
        
        # Get metrics data for analysis
        metrics_data = await self._get_metrics_for_anomaly_detection(
            time_range, user_id
        )
        
        if len(metrics_data) < 10:  # Need minimum data points
            return []
        
        # Prepare data for anomaly detection
        feature_matrix = self._prepare_anomaly_features(metrics_data)
        
        # Detect anomalies
        anomaly_scores = self.anomaly_detector.decision_function(feature_matrix)
        anomaly_predictions = self.anomaly_detector.predict(feature_matrix)
        
        # Process anomaly results
        anomalies = []
        for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
            if prediction == -1:  # Anomaly detected
                anomaly_data = metrics_data[i]
                anomalies.append({
                    'timestamp': anomaly_data['timestamp'],
                    'metric_type': anomaly_data['metric_type'],
                    'value': anomaly_data['value'],
                    'expected_range': anomaly_data.get('expected_range'),
                    'anomaly_score': float(score),
                    'severity': self._calculate_anomaly_severity(score),
                    'platform': anomaly_data.get('platform'),
                    'description': self._generate_anomaly_description(anomaly_data, score)
                })
        
        # Sort by severity and timestamp
        anomalies.sort(key=lambda x: (x['severity'], x['timestamp']), reverse=True)
        
        return anomalies
    
    async def generate_insights(
        self,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_7_DAYS,
        user_id: Optional[int] = None
    ) -> List[AnalyticsInsight]:
        """
        Generate AI-powered insights based on monitoring data.
        
        Args:
            time_range: Time range for analysis
            user_id: Optional user ID to filter data
            
        Returns:
            List of analytics insights
        """
        insights = []
        
        # Performance insights
        performance_insights = await self._generate_performance_insights(time_range, user_id)
        insights.extend(performance_insights)
        
        # Threat pattern insights
        threat_insights = await self._generate_threat_insights(time_range, user_id)
        insights.extend(threat_insights)
        
        # Platform coverage insights
        platform_insights = await self._generate_platform_insights(time_range, user_id)
        insights.extend(platform_insights)
        
        # Efficiency insights
        efficiency_insights = await self._generate_efficiency_insights(time_range, user_id)
        insights.extend(efficiency_insights)
        
        # Sort by severity and confidence
        insights.sort(
            key=lambda x: (self._severity_weight(x.severity), x.confidence_score),
            reverse=True
        )
        
        return insights[:20]  # Return top 20 insights
    
    async def get_performance_analytics(
        self,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_24_HOURS,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """
        Get comprehensive performance analytics.
        
        Args:
            time_range: Time range for analysis
            user_id: Optional user ID to filter data
            
        Returns:
            PerformanceMetrics object with performance data
        """
        # Get performance data from database
        performance_data = await self._get_performance_data(time_range, user_id)
        
        if not performance_data:
            return PerformanceMetrics()
        
        # Calculate performance metrics
        response_times = [d['response_time_ms'] for d in performance_data if d.get('response_time_ms')]
        
        metrics = PerformanceMetrics()
        
        if response_times:
            metrics.average_response_time_ms = np.mean(response_times)
            metrics.p95_response_time_ms = np.percentile(response_times, 95)
            metrics.p99_response_time_ms = np.percentile(response_times, 99)
        
        # Calculate other metrics
        total_requests = len(performance_data)
        error_count = sum(1 for d in performance_data if d.get('error', False))
        
        if total_requests > 0:
            metrics.error_rate_percentage = (error_count / total_requests) * 100
        
        # Get latest system metrics
        latest_system_metrics = await self._get_latest_system_metrics()
        if latest_system_metrics:
            metrics.memory_usage_percentage = latest_system_metrics.get('memory_usage_percent', 0)
            metrics.cpu_usage_percentage = latest_system_metrics.get('cpu_usage_percent', 0)
            metrics.concurrent_users = latest_system_metrics.get('active_connections', 0)
        
        return metrics
    
    async def get_platform_analytics(
        self,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_7_DAYS,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get platform-specific analytics.
        
        Args:
            time_range: Time range for analysis
            user_id: Optional user ID to filter data
            
        Returns:
            Dict containing platform analytics
        """
        platform_data = await self._get_platform_analytics_data(time_range, user_id)
        
        analytics = {
            'platform_coverage': {},
            'detection_rates': {},
            'false_positive_rates': {},
            'response_times': {},
            'threat_distributions': {},
            'enforcement_success_rates': {},
            'total_violations_by_platform': {},
            'trend_analysis': {}
        }
        
        # Process platform data
        for platform, data in platform_data.items():
            analytics['platform_coverage'][platform] = {
                'active_sessions': data.get('active_sessions', 0),
                'total_scans': data.get('total_scans', 0),
                'scan_frequency': data.get('scan_frequency', 0)
            }
            
            analytics['detection_rates'][platform] = data.get('detection_rate', 0.0)
            analytics['false_positive_rates'][platform] = data.get('false_positive_rate', 0.0)
            analytics['response_times'][platform] = data.get('avg_response_time', 0.0)
            analytics['enforcement_success_rates'][platform] = data.get('enforcement_success_rate', 0.0)
            analytics['total_violations_by_platform'][platform] = data.get('total_violations', 0)
            
            # Threat distribution
            analytics['threat_distributions'][platform] = data.get('threat_distribution', {})
            
            # Trend analysis for this platform
            trend = await self.get_trend_analysis(
                MetricType.DETECTION_RATE, time_range, user_id
            )
            analytics['trend_analysis'][platform] = {
                'direction': trend.direction.value,
                'percentage_change': trend.percentage_change,
                'significance': trend.significance_score
            }
        
        return analytics
    
    async def export_analytics_data(
        self,
        export_format: str = "json",
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_7_DAYS,
        user_id: Optional[int] = None,
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """
        Export analytics data in specified format.
        
        Args:
            export_format: Export format (json, csv, excel)
            time_range: Time range for export
            user_id: Optional user ID to filter data
            include_raw_data: Whether to include raw metrics data
            
        Returns:
            Dict containing exported data and metadata
        """
        export_data = {
            'metadata': {
                'export_format': export_format,
                'time_range': time_range.value,
                'user_id': user_id,
                'exported_at': datetime.utcnow().isoformat(),
                'total_records': 0
            },
            'summary': {},
            'analytics': {},
            'raw_data': [] if include_raw_data else None
        }
        
        # Get summary metrics
        export_data['summary'] = await self.get_realtime_metrics(user_id)
        
        # Get analytics
        export_data['analytics'] = {
            'performance': (await self.get_performance_analytics(time_range, user_id)).dict(),
            'platform_analytics': await self.get_platform_analytics(time_range, user_id),
            'insights': [insight.__dict__ for insight in await self.generate_insights(time_range, user_id)],
            'anomalies': await self.detect_anomalies(time_range, user_id)
        }
        
        # Get raw data if requested
        if include_raw_data:
            raw_data = await self._get_raw_metrics_data(time_range, user_id)
            export_data['raw_data'] = raw_data
            export_data['metadata']['total_records'] = len(raw_data)
        
        return export_data
    
    # Private helper methods
    
    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for analytics."""
        try:
            # Initialize anomaly detector
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            # Initialize clustering model for pattern detection
            self.cluster_model = DBSCAN(eps=0.5, min_samples=5)
            
            # Initialize scaler for feature normalization
            self.scaler = StandardScaler()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            self.enable_ml_insights = False
    
    async def _warm_up_caches(self) -> None:
        """Warm up caches with recent data."""
        if not self.redis_client:
            return
        
        try:
            # Pre-calculate common metrics
            await self.get_realtime_metrics()
            await self.get_performance_analytics()
            
            logger.info("Analytics caches warmed up")
            
        except Exception as e:
            logger.error(f"Failed to warm up caches: {e}")
    
    async def _setup_realtime_collection(self) -> None:
        """Set up real-time metrics collection."""
        try:
            logger.info("Setting up real-time metrics collection")
            
            # Initialize real-time collection components
            self.realtime_collectors = {
                'infringement_detector': None,
                'performance_monitor': None,
                'user_activity_tracker': None,
                'system_health_monitor': None,
                'security_event_collector': None
            }
            
            # Set up infringement detection pipeline
            self.realtime_collectors['infringement_detector'] = await self._setup_infringement_detector()
            
            # Set up performance monitoring
            self.realtime_collectors['performance_monitor'] = await self._setup_performance_monitor()
            
            # Set up user activity tracking
            self.realtime_collectors['user_activity_tracker'] = await self._setup_activity_tracker()
            
            # Set up system health monitoring
            self.realtime_collectors['system_health_monitor'] = await self._setup_health_monitor()
            
            # Set up security event collection
            self.realtime_collectors['security_event_collector'] = await self._setup_security_collector()
            
            # Start background collection tasks
            self.collection_tasks = []
            
            for collector_name, collector in self.realtime_collectors.items():
                if collector:
                    task = asyncio.create_task(self._run_collector(collector_name, collector))
                    self.collection_tasks.append(task)
                    logger.debug(f"Started real-time collector: {collector_name}")
            
            # Set up data aggregation pipeline
            self.aggregation_task = asyncio.create_task(self._run_data_aggregation())
            self.collection_tasks.append(self.aggregation_task)
            
            # Set up alert processing
            self.alert_task = asyncio.create_task(self._run_alert_processing())
            self.collection_tasks.append(self.alert_task)
            
            logger.info(f"Real-time collection setup completed with {len(self.collection_tasks)} active tasks")
            
        except Exception as e:
            logger.error(f"Failed to setup real-time collection: {str(e)}")
            raise
    
    async def _setup_infringement_detector(self):
        """Setup real-time infringement detection"""
        return {
            'type': 'infringement_detector',
            'interval': 30,  # seconds
            'enabled': True,
            'sources': ['youtube', 'instagram', 'tiktok', 'spotify'],
            'fingerprint_threshold': 0.85,
            'alert_threshold': 0.95
        }
    
    async def _setup_performance_monitor(self):
        """Setup performance monitoring"""
        return {
            'type': 'performance_monitor',
            'interval': 60,
            'enabled': True,
            'metrics': ['response_time', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage'],
            'thresholds': {
                'response_time_ms': 1000,
                'error_rate_percent': 5,
                'cpu_percent': 80,
                'memory_percent': 85
            }
        }
    
    async def _setup_activity_tracker(self):
        """Setup user activity tracking"""
        return {
            'type': 'activity_tracker',
            'interval': 10,
            'enabled': True,
            'events': ['login', 'logout', 'upload', 'download', 'share', 'report'],
            'anomaly_detection': True,
            'session_tracking': True
        }
    
    async def _setup_health_monitor(self):
        """Setup system health monitoring"""
        return {
            'type': 'health_monitor',
            'interval': 30,
            'enabled': True,
            'components': ['database', 'cache', 'storage', 'apis', 'background_jobs'],
            'auto_recovery': True,
            'escalation_rules': {
                'critical': 'immediate',
                'high': '5_minutes',
                'medium': '15_minutes'
            }
        }
    
    async def _setup_security_collector(self):
        """Setup security event collection"""
        return {
            'type': 'security_collector',
            'interval': 5,
            'enabled': True,
            'events': ['failed_login', 'privilege_escalation', 'suspicious_activity', 'data_breach'],
            'threat_detection': True,
            'auto_blocking': True,
            'severity_levels': ['low', 'medium', 'high', 'critical']
        }
    
    async def _run_collector(self, collector_name: str, collector_config: dict):
        """Run individual collector in background"""
        try:
            while True:
                if not collector_config.get('enabled', True):
                    await asyncio.sleep(collector_config.get('interval', 60))
                    continue
                
                # Collect metrics based on collector type
                if collector_config['type'] == 'infringement_detector':
                    await self._collect_infringement_metrics()
                elif collector_config['type'] == 'performance_monitor':
                    await self._collect_performance_metrics()
                elif collector_config['type'] == 'activity_tracker':
                    await self._collect_activity_metrics()
                elif collector_config['type'] == 'health_monitor':
                    await self._collect_health_metrics()
                elif collector_config['type'] == 'security_collector':
                    await self._collect_security_metrics()
                
                await asyncio.sleep(collector_config.get('interval', 60))
                
        except asyncio.CancelledError:
            logger.info(f"Collector {collector_name} was cancelled")
        except Exception as e:
            logger.error(f"Error in collector {collector_name}: {str(e)}")
    
    async def _collect_infringement_metrics(self):
        """Collect real-time infringement detection metrics"""
        # Implementation for infringement detection
        pass
    
    async def _collect_performance_metrics(self):
        """Collect real-time performance metrics"""
        # Implementation for performance metrics
        pass
    
    async def _collect_activity_metrics(self):
        """Collect real-time user activity metrics"""
        # Implementation for activity tracking
        pass
    
    async def _collect_health_metrics(self):
        """Collect real-time system health metrics"""
        # Implementation for health monitoring
        pass
    
    async def _collect_security_metrics(self):
        """Collect real-time security metrics"""
        # Implementation for security monitoring
        pass
    
    async def _run_data_aggregation(self):
        """Run data aggregation pipeline"""
        try:
            while True:
                # Aggregate collected metrics every minute
                await self._aggregate_realtime_data()
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Data aggregation task was cancelled")
        except Exception as e:
            logger.error(f"Error in data aggregation: {str(e)}")
    
    async def _run_alert_processing(self):
        """Run alert processing pipeline"""
        try:
            while True:
                # Process alerts every 10 seconds
                await self._process_pending_alerts()
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            logger.info("Alert processing task was cancelled")
        except Exception as e:
            logger.error(f"Error in alert processing: {str(e)}")
    
    async def _calculate_realtime_metrics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate real-time monitoring metrics."""
        try:
            # Base query conditions
            conditions = []
            params = {}
            
            if user_id:
                conditions.append("user_id = :user_id")
                params["user_id"] = user_id
            
            # Get violation counts
            violations_query = f"""
                SELECT COUNT(*) as total_violations,
                       COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_violations,
                       COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_violations,
                       platform,
                       threat_level
                FROM violation_detections 
                WHERE detected_at >= NOW() - INTERVAL '24 hours'
                {' AND ' + ' AND '.join(conditions) if conditions else ''}
                GROUP BY platform, threat_level
            """
            
            if self.db_session:
                result = await self.db_session.execute(text(violations_query), params)
                violation_data = result.fetchall()
            else:
                violation_data = []
            
            # Process violation data
            platform_distribution = defaultdict(int)
            threat_distribution = defaultdict(int)
            total_violations = 0
            resolved_violations = 0
            
            for row in violation_data:
                platform_distribution[row.platform] += row.total_violations
                threat_distribution[row.threat_level] += row.total_violations
                total_violations += row.total_violations
                resolved_violations += row.resolved_violations
            
            # Get active monitoring sessions
            sessions_query = f"""
                SELECT COUNT(*) as active_sessions,
                       AVG(EXTRACT(EPOCH FROM (NOW() - last_scan_at))) as avg_response_time
                FROM monitoring_sessions 
                WHERE status = 'active'
                {' AND ' + ' AND '.join(conditions) if conditions else ''}
            """
            
            if self.db_session:
                result = await self.db_session.execute(text(sessions_query), params)
                session_data = result.fetchone()
                active_sessions = session_data.active_sessions if session_data else 0
                avg_response_time = session_data.avg_response_time if session_data else 0.0
            else:
                active_sessions = 0
                avg_response_time = 0.0
            
            # Calculate derived metrics
            detection_rate = resolved_violations / total_violations if total_violations > 0 else 0.0
            false_positive_rate = await self._calculate_false_positive_rate(user_id)
            
            return {
                'total_violations_detected': total_violations,
                'violations_resolved': resolved_violations,
                'active_monitoring_sessions': active_sessions,
                'average_detection_time_seconds': avg_response_time,
                'current_false_positive_rate': false_positive_rate,
                'platform_distribution': dict(platform_distribution),
                'threat_level_distribution': dict(threat_distribution),
                'detection_rate': detection_rate,
                'system_health_score': await self._calculate_system_health_score(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate real-time metrics: {e}")
            return {}
    
    async def _get_historical_metrics(
        self,
        metric_type: MetricType,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get historical metrics data for trend analysis."""
        try:
            # Convert time range to datetime
            end_time = datetime.utcnow()
            time_delta_map = {
                AnalyticsTimeRange.LAST_HOUR: timedelta(hours=1),
                AnalyticsTimeRange.LAST_6_HOURS: timedelta(hours=6),
                AnalyticsTimeRange.LAST_24_HOURS: timedelta(days=1),
                AnalyticsTimeRange.LAST_7_DAYS: timedelta(days=7),
                AnalyticsTimeRange.LAST_30_DAYS: timedelta(days=30),
                AnalyticsTimeRange.LAST_3_MONTHS: timedelta(days=90),
                AnalyticsTimeRange.LAST_6_MONTHS: timedelta(days=180),
                AnalyticsTimeRange.LAST_YEAR: timedelta(days=365)
            }
            
            start_time = end_time - time_delta_map.get(time_range, timedelta(days=7))
            
            # Query historical metrics
            conditions = ["recorded_at >= :start_time", "recorded_at <= :end_time"]
            params = {"start_time": start_time, "end_time": end_time}
            
            if user_id:
                # Join with monitoring sessions to filter by user
                query = f"""
                    SELECT mm.value, mm.recorded_at as timestamp, mm.metadata
                    FROM monitoring_metrics mm
                    JOIN monitoring_sessions ms ON mm.session_id = ms.id
                    WHERE mm.metric_type = :metric_type
                      AND ms.user_id = :user_id
                      AND {' AND '.join(conditions)}
                    ORDER BY mm.recorded_at
                """
                params["user_id"] = user_id
            else:
                query = f"""
                    SELECT value, recorded_at as timestamp, metadata
                    FROM monitoring_metrics
                    WHERE metric_type = :metric_type
                      AND {' AND '.join(conditions)}
                    ORDER BY recorded_at
                """
            
            params["metric_type"] = metric_type.value
            
            if self.db_session:
                result = await self.db_session.execute(text(query), params)
                data = [
                    {
                        'value': row.value,
                        'timestamp': row.timestamp,
                        'metadata': row.metadata or {}
                    }
                    for row in result.fetchall()
                ]
            else:
                data = []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return []
    
    def _analyze_trend(self, values: List[float]) -> Tuple[TrendDirection, float, float]:
        """Analyze trend direction and significance."""
        if len(values) < 2:
            return TrendDirection.STABLE, 0.0, 0.0
        
        # Calculate linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Remove any NaN or infinite values
        mask = np.isfinite(y)
        if not mask.any():
            return TrendDirection.STABLE, 0.0, 0.0
        
        x_clean = x[mask]
        y_clean = y[mask]
        
        if len(y_clean) < 2:
            return TrendDirection.STABLE, 0.0, 0.0
        
        # Calculate slope
        slope, intercept = np.polyfit(x_clean, y_clean, 1)
        
        # Calculate percentage change
        first_value = y_clean[0]
        last_value = y_clean[-1]
        percentage_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0.0
        
        # Calculate significance (R-squared)
        y_pred = slope * x_clean + intercept
        ss_res = np.sum((y_clean - y_pred) ** 2)
        ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
        significance = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        # Determine trend direction
        if abs(percentage_change) < 5:  # Less than 5% change
            direction = TrendDirection.STABLE
        elif np.std(y_clean) / np.mean(y_clean) > 0.3:  # High volatility
            direction = TrendDirection.VOLATILE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        return direction, percentage_change, significance
    
    async def _predict_next_value(
        self,
        values: List[float],
        timestamps: List[datetime]
    ) -> Tuple[Optional[float], Optional[Tuple[float, float]]]:
        """Predict next value using simple trend extrapolation."""
        try:
            if len(values) < 3:
                return None, None
            
            # Use simple linear extrapolation
            x = np.arange(len(values))
            y = np.array(values)
            
            # Fit linear model
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict next value
            next_x = len(values)
            prediction = slope * next_x + intercept
            
            # Calculate confidence interval (simple approach)
            residuals = y - (slope * x + intercept)
            mse = np.mean(residuals ** 2)
            std_error = np.sqrt(mse)
            
            confidence_interval = (
                prediction - 1.96 * std_error,
                prediction + 1.96 * std_error
            )
            
            return float(prediction), confidence_interval
            
        except Exception as e:
            logger.error(f"Failed to predict next value: {e}")
            return None, None
    
    async def _get_metrics_for_anomaly_detection(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics data for anomaly detection."""
        try:
            # Get data for multiple metric types
            all_metrics_data = []
            
            for metric_type in [MetricType.DETECTION_RATE, MetricType.RESPONSE_TIME, 
                              MetricType.FALSE_POSITIVE_RATE]:
                metrics_data = await self._get_historical_metrics(metric_type, time_range, user_id)
                
                for data_point in metrics_data:
                    all_metrics_data.append({
                        'timestamp': data_point['timestamp'],
                        'metric_type': metric_type.value,
                        'value': data_point['value'],
                        'metadata': data_point.get('metadata', {}),
                        'platform': data_point.get('metadata', {}).get('platform')
                    })
            
            return all_metrics_data
            
        except Exception as e:
            logger.error(f"Failed to get metrics for anomaly detection: {e}")
            return []
    
    def _prepare_anomaly_features(self, metrics_data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare feature matrix for anomaly detection."""
        try:
            # Create feature matrix with multiple metrics
            features = []
            
            # Group by timestamp
            timestamp_groups = defaultdict(dict)
            for data_point in metrics_data:
                timestamp = data_point['timestamp']
                metric_type = data_point['metric_type']
                timestamp_groups[timestamp][metric_type] = data_point['value']
            
            # Create feature vectors
            metric_types = [MetricType.DETECTION_RATE.value, MetricType.RESPONSE_TIME.value, 
                          MetricType.FALSE_POSITIVE_RATE.value]
            
            for timestamp, metrics in timestamp_groups.items():
                feature_vector = []
                for metric_type in metric_types:
                    feature_vector.append(metrics.get(metric_type, 0.0))
                features.append(feature_vector)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Failed to prepare anomaly features: {e}")
            return np.array([])
    
    def _calculate_anomaly_severity(self, anomaly_score: float) -> str:
        """Calculate anomaly severity based on score."""
        # Lower scores indicate higher anomaly (isolation forest)
        if anomaly_score < -0.5:
            return "critical"
        elif anomaly_score < -0.3:
            return "high"
        elif anomaly_score < -0.1:
            return "medium"
        else:
            return "low"
    
    def _generate_anomaly_description(
        self,
        anomaly_data: Dict[str, Any],
        score: float
    ) -> str:
        """Generate human-readable anomaly description."""
        metric_type = anomaly_data['metric_type']
        value = anomaly_data['value']
        platform = anomaly_data.get('platform', 'Unknown')
        
        severity = self._calculate_anomaly_severity(score)
        
        descriptions = {
            MetricType.DETECTION_RATE.value: f"{severity.title()} anomaly detected in detection rate ({value:.2%}) on {platform}",
            MetricType.RESPONSE_TIME.value: f"{severity.title()} anomaly detected in response time ({value:.2f}ms) on {platform}",
            MetricType.FALSE_POSITIVE_RATE.value: f"{severity.title()} anomaly detected in false positive rate ({value:.2%}) on {platform}"
        }
        
        return descriptions.get(metric_type, f"{severity.title()} anomaly detected in {metric_type}")
    
    async def _generate_performance_insights(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[AnalyticsInsight]:
        """Generate performance-related insights."""
        insights = []
        
        try:
            # Get performance metrics
            perf_metrics = await self.get_performance_analytics(time_range, user_id)
            
            # High response time insight
            if perf_metrics.average_response_time_ms > 2000:
                insights.append(AnalyticsInsight(
                    title="High Response Time Detected",
                    description=f"Average response time is {perf_metrics.average_response_time_ms:.0f}ms, exceeding optimal threshold",
                    severity="high",
                    category="performance",
                    confidence_score=0.9,
                    affected_platforms=[],
                    recommended_actions=[
                        "Review database query performance",
                        "Check server resource utilization",
                        "Consider implementing response caching"
                    ],
                    created_at=datetime.utcnow()
                ))
            
            # High error rate insight
            if perf_metrics.error_rate_percentage > 5:
                insights.append(AnalyticsInsight(
                    title="Elevated Error Rate",
                    description=f"Error rate is {perf_metrics.error_rate_percentage:.1f}%, above acceptable threshold",
                    severity="medium",
                    category="reliability",
                    confidence_score=0.85,
                    affected_platforms=[],
                    recommended_actions=[
                        "Investigate error logs",
                        "Check external API dependencies",
                        "Review recent deployments"
                    ],
                    created_at=datetime.utcnow()
                ))
            
            # Resource utilization insights
            if perf_metrics.memory_usage_percentage > 80:
                insights.append(AnalyticsInsight(
                    title="High Memory Usage",
                    description=f"Memory usage is {perf_metrics.memory_usage_percentage:.1f}%, consider optimization",
                    severity="medium",
                    category="resources",
                    confidence_score=0.8,
                    affected_platforms=[],
                    recommended_actions=[
                        "Review memory-intensive operations",
                        "Implement data cleanup processes",
                        "Consider scaling resources"
                    ],
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {e}")
        
        return insights
    
    async def _generate_threat_insights(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[AnalyticsInsight]:
        """Generate threat-related insights."""
        insights = []
        
        try:
            # Get threat distribution data
            threat_data = await self._get_threat_distribution_data(time_range, user_id)
            
            # Analyze threat patterns
            total_threats = sum(threat_data.values())
            
            if total_threats > 0:
                critical_percentage = threat_data.get('critical', 0) / total_threats
                
                if critical_percentage > 0.1:  # More than 10% critical threats
                    insights.append(AnalyticsInsight(
                        title="High Critical Threat Activity",
                        description=f"{critical_percentage:.1%} of detected threats are critical severity",
                        severity="high",
                        category="security",
                        confidence_score=0.9,
                        affected_platforms=[],
                        recommended_actions=[
                            "Review critical threat cases",
                            "Enhance monitoring for high-value content",
                            "Consider automated enforcement for critical threats"
                        ],
                        created_at=datetime.utcnow()
                    ))
            
        except Exception as e:
            logger.error(f"Failed to generate threat insights: {e}")
        
        return insights
    
    async def _generate_platform_insights(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[AnalyticsInsight]:
        """Generate platform-specific insights."""
        insights = []
        
        try:
            platform_analytics = await self.get_platform_analytics(time_range, user_id)
            
            # Analyze platform performance
            detection_rates = platform_analytics.get('detection_rates', {})
            
            for platform, rate in detection_rates.items():
                if rate < 0.7:  # Less than 70% detection rate
                    insights.append(AnalyticsInsight(
                        title=f"Low Detection Rate on {platform}",
                        description=f"Detection rate on {platform} is {rate:.1%}, below optimal threshold",
                        severity="medium",
                        category="platform_performance",
                        confidence_score=0.8,
                        affected_platforms=[platform],
                        recommended_actions=[
                            f"Review {platform} monitoring configuration",
                            f"Check {platform} API connectivity",
                            f"Verify {platform} scan frequency"
                        ],
                        created_at=datetime.utcnow()
                    ))
            
        except Exception as e:
            logger.error(f"Failed to generate platform insights: {e}")
        
        return insights
    
    async def _generate_efficiency_insights(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[AnalyticsInsight]:
        """Generate efficiency-related insights."""
        insights = []
        
        try:
            # Analyze false positive rates
            realtime_metrics = await self.get_realtime_metrics(user_id)
            fp_rate = realtime_metrics.get('current_false_positive_rate', 0.0)
            
            if fp_rate > 0.15:  # More than 15% false positives
                insights.append(AnalyticsInsight(
                    title="High False Positive Rate",
                    description=f"False positive rate is {fp_rate:.1%}, reducing efficiency",
                    severity="medium",
                    category="efficiency",
                    confidence_score=0.85,
                    affected_platforms=[],
                    recommended_actions=[
                        "Review detection thresholds",
                        "Implement machine learning improvements",
                        "Enhance fingerprinting accuracy"
                    ],
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            logger.error(f"Failed to generate efficiency insights: {e}")
        
        return insights
    
    def _severity_weight(self, severity: str) -> int:
        """Get numeric weight for severity sorting."""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(severity.lower(), 0)
    
    async def _get_performance_data(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get performance data from database."""
        try:
            # This would query system performance metrics
            # Implementation depends on your specific metrics storage
            return []
        except Exception as e:
            logger.error(f"Failed to get performance data: {e}")
            return []
    
    async def _get_latest_system_metrics(self) -> Optional[Dict[str, Any]]:
        """Get latest system performance metrics."""
        try:
            if not self.db_session:
                return None
            
            query = """
                SELECT cpu_usage_percent, memory_usage_percent, active_connections
                FROM system_performance_metrics 
                ORDER BY recorded_at DESC 
                LIMIT 1
            """
            
            result = await self.db_session.execute(text(query))
            row = result.fetchone()
            
            if row:
                return {
                    'cpu_usage_percent': row.cpu_usage_percent,
                    'memory_usage_percent': row.memory_usage_percent,
                    'active_connections': row.active_connections
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest system metrics: {e}")
            return None
    
    async def _get_platform_analytics_data(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get platform-specific analytics data."""
        try:
            # This would aggregate data by platform
            # Implementation depends on your data structure
            return {}
        except Exception as e:
            logger.error(f"Failed to get platform analytics data: {e}")
            return {}
    
    async def _get_raw_metrics_data(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get raw metrics data for export."""
        try:
            # This would return raw metrics data
            # Implementation depends on your data structure
            return []
        except Exception as e:
            logger.error(f"Failed to get raw metrics data: {e}")
            return []
    
    async def _calculate_false_positive_rate(self, user_id: Optional[int] = None) -> float:
        """Calculate current false positive rate."""
        try:
            conditions = ["detected_at >= NOW() - INTERVAL '24 hours'"]
            params = {}
            
            if user_id:
                conditions.append("fingerprint_id IN (SELECT id FROM content_fingerprints WHERE user_id = :user_id)")
                params["user_id"] = user_id
            
            query = f"""
                SELECT 
                    COUNT(CASE WHEN status = 'false_positive' THEN 1 END) as false_positives,
                    COUNT(*) as total_detections
                FROM violation_detections 
                WHERE {' AND '.join(conditions)}
            """
            
            if self.db_session:
                result = await self.db_session.execute(text(query), params)
                row = result.fetchone()
                
                if row and row.total_detections > 0:
                    return row.false_positives / row.total_detections
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate false positive rate: {e}")
            return 0.0
    
    async def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score."""
        try:
            health_factors = []
            
            # Check error rate
            latest_metrics = await self._get_latest_system_metrics()
            if latest_metrics:
                cpu_usage = latest_metrics.get('cpu_usage_percent', 0)
                memory_usage = latest_metrics.get('memory_usage_percent', 0)
                
                # CPU health (100% - usage%)
                cpu_health = max(0, 100 - cpu_usage)
                health_factors.append(cpu_health)
                
                # Memory health
                memory_health = max(0, 100 - memory_usage)
                health_factors.append(memory_health)
            
            # Check recent error rates
            fp_rate = await self._calculate_false_positive_rate()
            error_health = max(0, 100 - (fp_rate * 100))
            health_factors.append(error_health)
            
            # Calculate overall score
            if health_factors:
                return sum(health_factors) / len(health_factors)
            
            return 100.0
            
        except Exception as e:
            logger.error(f"Failed to calculate system health score: {e}")
            return 100.0
    
    async def _get_threat_distribution_data(
        self,
        time_range: AnalyticsTimeRange,
        user_id: Optional[int] = None
    ) -> Dict[str, int]:
        """Get threat distribution data."""
        try:
            conditions = []
            params = {}
            
            # Add time range condition
            time_deltas = {
                AnalyticsTimeRange.LAST_HOUR: "1 hour",
                AnalyticsTimeRange.LAST_6_HOURS: "6 hours",
                AnalyticsTimeRange.LAST_24_HOURS: "24 hours",
                AnalyticsTimeRange.LAST_7_DAYS: "7 days",
                AnalyticsTimeRange.LAST_30_DAYS: "30 days"
            }
            
            time_condition = time_deltas.get(time_range, "7 days")
            conditions.append(f"detected_at >= NOW() - INTERVAL '{time_condition}'")
            
            if user_id:
                conditions.append("fingerprint_id IN (SELECT id FROM content_fingerprints WHERE user_id = :user_id)")
                params["user_id"] = user_id
            
            query = f"""
                SELECT threat_level, COUNT(*) as count
                FROM violation_detections 
                WHERE {' AND '.join(conditions)}
                GROUP BY threat_level
            """
            
            if self.db_session:
                result = await self.db_session.execute(text(query), params)
                return {row.threat_level: row.count for row in result.fetchall()}
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get threat distribution data: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Gracefully shutdown analytics engine."""
        logger.info("Shutting down Monitoring Analytics Engine...")
        
        # Clear buffers
        self.metrics_buffer.clear()
        self.events_buffer.clear()
        
        # Clear caches
        self._cached_insights.clear()
        
        self._initialized = False
        logger.info("Monitoring Analytics Engine shutdown complete")
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    CUSTOM = "custom"

class MetricType(str, Enum):
    """Types of metrics tracked."""
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    RESPONSE_TIME = "response_time"
    PLATFORM_COVERAGE = "platform_coverage"
    THREAT_DISTRIBUTION = "threat_distribution"
    USER_ACTIVITY = "user_activity"
    SYSTEM_PERFORMANCE = "system_performance"

class TrendDirection(str, Enum):
    """Trend direction indicators."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class MetricPoint:
    """Individual metric data point."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = None

class TrendAnalysis(BaseModel):
    """Trend analysis result."""
    metric_type: MetricType
    direction: TrendDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    rate_of_change: float
    significance: str  # low, medium, high, critical
    prediction_next_24h: Optional[float] = None
    recommendation: str = ""

class PlatformPerformance(BaseModel):
    """Platform-specific performance metrics."""
    platform_name: str
    detection_count: int = 0
    false_positive_count: int = 0
    average_response_time: float = 0.0
    uptime_percentage: float = 100.0
    efficiency_score: float = 0.0
    last_scan: Optional[datetime] = None
    threat_levels: Dict[str, int] = Field(default_factory=dict)

class UserEngagementMetrics(BaseModel):
    """User engagement and activity metrics."""
    user_id: int
    total_content_protected: int = 0
    violations_detected: int = 0
    enforcement_actions: int = 0
    last_activity: Optional[datetime] = None
    engagement_score: float = 0.0
    risk_profile: str = "low"  # low, medium, high

class SystemHealthMetrics(BaseModel):
    """Overall system health indicators."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_throughput: float = 0.0
    active_connections: int = 0
    queue_depth: int = 0
    error_rate: float = 0.0
    availability: float = 100.0

class AnalyticsReport(BaseModel):
    """Comprehensive analytics report."""
    report_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_range: AnalyticsTimeRange
    start_date: datetime
    end_date: datetime
    
    # Summary metrics
    total_detections: int = 0
    total_violations: int = 0
    detection_accuracy: float = 0.0
    average_response_time: float = 0.0
    
    # Platform performance
    platform_performance: List[PlatformPerformance] = Field(default_factory=list)
    
    # Trend analysis
    trends: List[TrendAnalysis] = Field(default_factory=list)
    
    # User metrics
    user_metrics: List[UserEngagementMetrics] = Field(default_factory=list)
    
    # System health
    system_health: SystemHealthMetrics = Field(default_factory=SystemHealthMetrics)
    
    # Insights and recommendations
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class MonitoringAnalytics:
    """
    Advanced analytics engine for monitoring system.
    
    Features:
    - Real-time metrics aggregation and analysis
    - Predictive threat modeling using ML
    - Performance optimization recommendations
    - Comprehensive reporting and visualization
    - Anomaly detection and alerting
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        redis_client: Optional[aioredis.Redis] = None,
        db_session: Optional[AsyncSession] = None
    ):
        """Initialize monitoring analytics."""
        self.config = config
        self.redis_client = redis_client
        self.db_session = db_session
        
        # Analytics configuration
        self.metrics_retention_days = config.get('metrics_retention_days', 90)
        self.aggregation_interval = config.get('aggregation_interval_minutes', 5)
        self.anomaly_detection_window = config.get('anomaly_detection_window_hours', 24)
        self.trend_analysis_window = config.get('trend_analysis_window_hours', 168)  # 7 days
        
        # In-memory metric storage for real-time processing
        self._metric_buffers: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=1000) for metric_type in MetricType
        }
        
        # ML models for anomaly detection
        self._anomaly_detectors: Dict[MetricType, IsolationForest] = {}
        self._scalers: Dict[MetricType, StandardScaler] = {}
        
        # Cache for frequently accessed data
        self._analytics_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._cache_ttl = timedelta(minutes=config.get('cache_ttl_minutes', 5))
        
        # Background tasks
        self._running = False
        self._analytics_tasks: List[asyncio.Task] = []
        
        logger.info("Monitoring Analytics initialized")

    async def initialize(self) -> bool:
        """Initialize the analytics engine."""
        try:
            logger.info("Initializing Monitoring Analytics...")
            
            # Initialize Redis connection if not provided
            if not self.redis_client:
                self.redis_client = await aioredis.from_url(
                    self.config.get('redis_url', 'redis://localhost:6379'),
                    decode_responses=True
                )
            
            # Initialize ML models
            await self._initialize_anomaly_detectors()
            
            # Start background analytics tasks
            await self._start_analytics_tasks()
            
            # Load historical data for warm-up
            await self._load_historical_metrics()
            
            self._running = True
            logger.info("Monitoring Analytics initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Analytics: {e}")
            return False

    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record a metric data point."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        metric_point = MetricPoint(
            timestamp=timestamp,
            value=value,
            metadata=metadata or {}
        )
        
        # Add to in-memory buffer
        self._metric_buffers[metric_type].append(metric_point)
        
        # Store in Redis for persistence
        metric_key = f"metric:{metric_type.value}:{int(timestamp.timestamp())}"
        metric_data = {
            'timestamp': timestamp.isoformat(),
            'value': str(value),
            'metadata': json.dumps(metadata or {})
        }
        
        await self.redis_client.hset(metric_key, mapping=metric_data)
        await self.redis_client.expire(
            metric_key, 
            self.metrics_retention_days * 24 * 3600
        )
        
        # Trigger real-time anomaly detection
        if len(self._metric_buffers[metric_type]) >= 10:
            await self._check_anomaly(metric_type, value)

    async def generate_analytics_report(
        self,
        time_range: AnalyticsTimeRange,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_predictions: bool = True
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report."""
        # Determine time range
        if time_range == AnalyticsTimeRange.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("Custom time range requires start_date and end_date")
        else:
            end_date = datetime.utcnow()
            start_date = self._get_start_date_for_range(time_range, end_date)
        
        report_id = f"report_{int(datetime.utcnow().timestamp())}"
        
        # Check cache first
        cache_key = f"report_{time_range.value}_{int(start_date.timestamp())}_{int(end_date.timestamp())}"
        cached_report = await self._get_cached_data(cache_key)
        if cached_report:
            return AnalyticsReport(**cached_report)
        
        logger.info(f"Generating analytics report for {time_range.value}")
        
        # Gather metrics data
        metrics_data = await self._gather_metrics_data(start_date, end_date)
        
        # Generate report
        report = AnalyticsReport(
            report_id=report_id,
            time_range=time_range,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate summary metrics
        await self._calculate_summary_metrics(report, metrics_data)
        
        # Analyze platform performance
        await self._analyze_platform_performance(report, metrics_data)
        
        # Perform trend analysis
        await self._perform_trend_analysis(report, metrics_data)
        
        # Analyze user engagement
        await self._analyze_user_engagement(report, start_date, end_date)
        
        # Check system health
        await self._assess_system_health(report)
        
        # Generate insights and recommendations
        await self._generate_insights_and_recommendations(report)
        
        # Add predictions if requested
        if include_predictions:
            await self._add_predictions(report)
        
        # Cache the report
        await self._cache_data(cache_key, report.dict())
        
        logger.info(f"Analytics report generated: {report_id}")
        return report

    async def get_realtime_metrics(self) -> Dict[MetricType, float]:
        """Get current real-time metric values."""
        realtime_metrics = {}
        
        for metric_type in MetricType:
            buffer = self._metric_buffers[metric_type]
            if buffer:
                # Get average of last 5 minutes
                recent_points = [
                    point for point in buffer
                    if (datetime.utcnow() - point.timestamp).total_seconds() <= 300
                ]
                if recent_points:
                    values = [point.value for point in recent_points]
                    realtime_metrics[metric_type] = np.mean(values)
                else:
                    realtime_metrics[metric_type] = buffer[-1].value
            else:
                realtime_metrics[metric_type] = 0.0
        
        return realtime_metrics

    async def detect_anomalies(
        self,
        metric_type: MetricType,
        lookback_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics data."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        # Get metrics data
        metrics_data = await self._get_metrics_data(metric_type, start_time, end_time)
        
        if len(metrics_data) < 10:
            return []  # Not enough data for anomaly detection
        
        # Prepare data for ML model
        values = np.array([[point['value']] for point in metrics_data])
        
        # Use or train anomaly detector
        if metric_type not in self._anomaly_detectors:
            await self._train_anomaly_detector(metric_type, values)
        
        detector = self._anomaly_detectors[metric_type]
        scaler = self._scalers[metric_type]
        
        # Scale data and detect anomalies
        scaled_values = scaler.transform(values)
        anomaly_labels = detector.predict(scaled_values)
        anomaly_scores = detector.decision_function(scaled_values)
        
        # Identify anomalies
        anomalies = []
        for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
            if label == -1:  # Anomaly detected
                anomalies.append({
                    'timestamp': metrics_data[i]['timestamp'],
                    'value': metrics_data[i]['value'],
                    'anomaly_score': float(score),
                    'severity': self._calculate_anomaly_severity(score),
                    'metadata': metrics_data[i].get('metadata', {})
                })
        
        return anomalies

    async def get_performance_insights(
        self,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance insights and optimization recommendations."""
        insights = {
            'overall_performance': {},
            'platform_specific': {},
            'optimization_recommendations': [],
            'trend_insights': []
        }
        
        # Overall performance analysis
        realtime_metrics = await self.get_realtime_metrics()
        
        insights['overall_performance'] = {
            'detection_efficiency': realtime_metrics.get(MetricType.DETECTION_RATE, 0.0),
            'response_time_ms': realtime_metrics.get(MetricType.RESPONSE_TIME, 0.0),
            'false_positive_rate': realtime_metrics.get(MetricType.FALSE_POSITIVE_RATE, 0.0),
            'system_load': realtime_metrics.get(MetricType.SYSTEM_PERFORMANCE, 0.0)
        }
        
        # Platform-specific insights
        if platform:
            platform_data = await self._get_platform_performance_data(platform)
            insights['platform_specific'][platform] = platform_data
        else:
            # Get data for all platforms
            platforms = await self._get_active_platforms()
            for plat in platforms:
                platform_data = await self._get_platform_performance_data(plat)
                insights['platform_specific'][plat] = platform_data
        
        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations(insights)
        insights['optimization_recommendations'] = recommendations
        
        # Add trend insights
        trend_insights = await self._generate_trend_insights()
        insights['trend_insights'] = trend_insights
        
        return insights

    async def _initialize_anomaly_detectors(self) -> None:
        """Initialize machine learning models for anomaly detection."""
        for metric_type in MetricType:
            # Initialize isolation forest for anomaly detection
            self._anomaly_detectors[metric_type] = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            
            # Initialize scaler
            self._scalers[metric_type] = StandardScaler()

    async def _train_anomaly_detector(
        self,
        metric_type: MetricType,
        training_data: np.ndarray
    ) -> None:
        """Train anomaly detector for a specific metric type."""
        if len(training_data) < 10:
            return  # Not enough data to train
        
        scaler = self._scalers[metric_type]
        detector = self._anomaly_detectors[metric_type]
        
        # Scale training data
        scaled_data = scaler.fit_transform(training_data)
        
        # Train detector
        detector.fit(scaled_data)
        
        logger.debug(f"Trained anomaly detector for {metric_type.value}")

    async def _check_anomaly(self, metric_type: MetricType, value: float) -> None:
        """Check if a new metric value is anomalous."""
        if metric_type not in self._anomaly_detectors:
            return
        
        try:
            detector = self._anomaly_detectors[metric_type]
            scaler = self._scalers[metric_type]
            
            # Scale the value
            scaled_value = scaler.transform([[value]])
            
            # Check for anomaly
            prediction = detector.predict(scaled_value)
            score = detector.decision_function(scaled_value)[0]
            
            if prediction[0] == -1:  # Anomaly detected
                severity = self._calculate_anomaly_severity(score)
                
                # Log anomaly
                logger.warning(
                    f"Anomaly detected in {metric_type.value}: "
                    f"value={value}, score={score:.3f}, severity={severity}"
                )
                
                # Store anomaly in Redis for alerting
                anomaly_data = {
                    'metric_type': metric_type.value,
                    'value': str(value),
                    'anomaly_score': str(score),
                    'severity': severity,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self.redis_client.lpush(
                    "anomalies:detected",
                    json.dumps(anomaly_data)
                )
                await self.redis_client.ltrim("anomalies:detected", 0, 999)  # Keep last 1000
                
        except Exception as e:
            logger.error(f"Error checking anomaly for {metric_type.value}: {e}")

    def _calculate_anomaly_severity(self, score: float) -> str:
        """Calculate anomaly severity based on score."""
        if score < -0.5:
            return "critical"
        elif score < -0.3:
            return "high"
        elif score < -0.1:
            return "medium"
        else:
            return "low"

    async def _start_analytics_tasks(self) -> None:
        """Start background analytics tasks."""
        # Metrics aggregation task
        aggregation_task = asyncio.create_task(self._metrics_aggregation_loop())
        self._analytics_tasks.append(aggregation_task)
        
        # Anomaly detection task
        anomaly_task = asyncio.create_task(self._anomaly_detection_loop())
        self._analytics_tasks.append(anomaly_task)
        
        # Cache cleanup task
        cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        self._analytics_tasks.append(cleanup_task)
        
        logger.info("Started background analytics tasks")

    async def _metrics_aggregation_loop(self) -> None:
        """Background task for metrics aggregation."""
        try:
            while self._running:
                await self._aggregate_metrics()
                await asyncio.sleep(self.aggregation_interval * 60)
        except asyncio.CancelledError:
            logger.debug("Metrics aggregation loop cancelled")

    async def _anomaly_detection_loop(self) -> None:
        """Background task for periodic anomaly detection."""
        try:
            while self._running:
                for metric_type in MetricType:
                    await self._periodic_anomaly_check(metric_type)
                await asyncio.sleep(300)  # Check every 5 minutes
        except asyncio.CancelledError:
            logger.debug("Anomaly detection loop cancelled")

    async def _cache_cleanup_loop(self) -> None:
        """Background task for cache cleanup."""
        try:
            while self._running:
                await self._cleanup_expired_cache()
                await asyncio.sleep(3600)  # Cleanup every hour
        except asyncio.CancelledError:
            logger.debug("Cache cleanup loop cancelled")

    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics for time-series analysis."""
        try:
            current_time = datetime.utcnow()
            
            for metric_type in MetricType:
                buffer = self._metric_buffers[metric_type]
                if not buffer:
                    continue
                
                # Get points from last aggregation interval
                cutoff_time = current_time - timedelta(minutes=self.aggregation_interval)
                recent_points = [
                    point for point in buffer
                    if point.timestamp >= cutoff_time
                ]
                
                if recent_points:
                    values = [point.value for point in recent_points]
                    
                    # Calculate aggregated metrics
                    aggregated_data = {
                        'timestamp': current_time.isoformat(),
                        'count': len(values),
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'percentile_95': np.percentile(values, 95)
                    }
                    
                    # Store aggregated data
                    agg_key = f"aggregated:{metric_type.value}:{int(current_time.timestamp())}"
                    await self.redis_client.hset(
                        agg_key,
                        mapping={k: str(v) for k, v in aggregated_data.items()}
                    )
                    await self.redis_client.expire(agg_key, self.metrics_retention_days * 24 * 3600)
                    
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")

    async def _periodic_anomaly_check(self, metric_type: MetricType) -> None:
        """Perform periodic anomaly detection."""
        try:
            # Get recent data for training/updating the model
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=self.anomaly_detection_window)
            
            metrics_data = await self._get_metrics_data(metric_type, start_time, end_time)
            
            if len(metrics_data) >= 50:  # Enough data to retrain
                values = np.array([[point['value']] for point in metrics_data])
                await self._train_anomaly_detector(metric_type, values)
                
        except Exception as e:
            logger.error(f"Error in periodic anomaly check for {metric_type.value}: {e}")

    async def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        if cache_key in self._analytics_cache:
            timestamp, data = self._analytics_cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                return data
            else:
                del self._analytics_cache[cache_key]
        return None

    async def _cache_data(self, cache_key: str, data: Any) -> None:
        """Cache data with timestamp."""
        self._analytics_cache[cache_key] = (datetime.utcnow(), data)

    async def _cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries."""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, (timestamp, _) in self._analytics_cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._analytics_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _get_start_date_for_range(
        self,
        time_range: AnalyticsTimeRange,
        end_date: datetime
    ) -> datetime:
        """Get start date for a given time range."""
        if time_range == AnalyticsTimeRange.LAST_HOUR:
            return end_date - timedelta(hours=1)
        elif time_range == AnalyticsTimeRange.LAST_6_HOURS:
            return end_date - timedelta(hours=6)
        elif time_range == AnalyticsTimeRange.LAST_24_HOURS:
            return end_date - timedelta(hours=24)
        elif time_range == AnalyticsTimeRange.LAST_7_DAYS:
            return end_date - timedelta(days=7)
        elif time_range == AnalyticsTimeRange.LAST_30_DAYS:
            return end_date - timedelta(days=30)
        elif time_range == AnalyticsTimeRange.LAST_90_DAYS:
            return end_date - timedelta(days=90)
        else:
            raise ValueError(f"Unsupported time range: {time_range}")

    async def _gather_metrics_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[MetricType, List[Dict[str, Any]]]:
        """Gather metrics data for the specified time range."""
        metrics_data = {}
        
        for metric_type in MetricType:
            data = await self._get_metrics_data(metric_type, start_date, end_date)
            metrics_data[metric_type] = data
        
        return metrics_data

    async def _get_metrics_data(
        self,
        metric_type: MetricType,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get metrics data for a specific type and time range."""
        # Get data from Redis
        pattern = f"metric:{metric_type.value}:*"
        data_points = []
        
        async for key in self.redis_client.scan_iter(match=pattern):
            # Extract timestamp from key
            try:
                timestamp_str = key.split(':')[-1]
                timestamp = datetime.fromtimestamp(int(timestamp_str))
                
                if start_date <= timestamp <= end_date:
                    metric_data = await self.redis_client.hgetall(key)
                    if metric_data:
                        data_points.append({
                            'timestamp': timestamp.isoformat(),
                            'value': float(metric_data['value']),
                            'metadata': json.loads(metric_data.get('metadata', '{}'))
                        })
            except (ValueError, KeyError, json.JSONDecodeError):
                continue  # Skip invalid entries
        
        # Sort by timestamp
        data_points.sort(key=lambda x: x['timestamp'])
        return data_points

    async def _calculate_summary_metrics(
        self,
        report: AnalyticsReport,
        metrics_data: Dict[MetricType, List[Dict[str, Any]]]
    ) -> None:
        """Calculate summary metrics for the report."""
        # Total detections
        detection_data = metrics_data.get(MetricType.DETECTION_RATE, [])
        if detection_data:
            report.total_detections = int(sum(point['value'] for point in detection_data))
        
        # Detection accuracy
        false_positive_data = metrics_data.get(MetricType.FALSE_POSITIVE_RATE, [])
        if false_positive_data:
            avg_fp_rate = np.mean([point['value'] for point in false_positive_data])
            report.detection_accuracy = max(0.0, 100.0 - avg_fp_rate)
        
        # Average response time
        response_time_data = metrics_data.get(MetricType.RESPONSE_TIME, [])
        if response_time_data:
            report.average_response_time = np.mean([point['value'] for point in response_time_data])

    async def _analyze_platform_performance(
        self,
        report: AnalyticsReport,
        metrics_data: Dict[MetricType, List[Dict[str, Any]]]
    ) -> None:
        """Analyze platform-specific performance."""
        platforms = await self._get_active_platforms()
        
        for platform in platforms:
            performance = await self._get_platform_performance_data(platform)
            report.platform_performance.append(performance)

    async def _perform_trend_analysis(
        self,
        report: AnalyticsReport,
        metrics_data: Dict[MetricType, List[Dict[str, Any]]]
    ) -> None:
        """Perform trend analysis on metrics."""
        for metric_type, data in metrics_data.items():
            if len(data) < 10:
                continue  # Not enough data for trend analysis
            
            values = [point['value'] for point in data]
            trend = await self._calculate_trend(values)
            report.trends.append(trend)

    async def _calculate_trend(self, values: List[float]) -> TrendAnalysis:
        """Calculate trend analysis for a series of values."""
        if len(values) < 2:
            return TrendAnalysis(
                metric_type=MetricType.DETECTION_RATE,
                direction=TrendDirection.STABLE,
                confidence=0.0,
                rate_of_change=0.0,
                significance="low"
            )
        
        # Calculate linear regression slope
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Calculate volatility
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        if volatility > 0.5:
            direction = TrendDirection.VOLATILE
        
        # Calculate confidence
        correlation = np.corrcoef(x, values)[0, 1]
        confidence = abs(correlation) if not np.isnan(correlation) else 0.0
        
        # Determine significance
        if abs(slope) > 1.0 and confidence > 0.8:
            significance = "critical"
        elif abs(slope) > 0.5 and confidence > 0.6:
            significance = "high"
        elif abs(slope) > 0.1 and confidence > 0.4:
            significance = "medium"
        else:
            significance = "low"
        
        return TrendAnalysis(
            metric_type=MetricType.DETECTION_RATE,  # Would be passed as parameter
            direction=direction,
            confidence=confidence,
            rate_of_change=slope,
            significance=significance,
            recommendation=f"Monitor {direction.value} trend with {significance} significance"
        )

    async def _get_active_platforms(self) -> List[str]:
        """Get list of active platforms."""
        # This would query the database or Redis for active platforms
        # For now, return mock platforms
        return ["youtube", "spotify", "soundcloud", "instagram", "tiktok"]

    async def _get_platform_performance_data(self, platform: str) -> PlatformPerformance:
        """Get performance data for a specific platform."""
        # This would query actual platform metrics
        # For now, return mock data
        return PlatformPerformance(
            platform_name=platform,
            detection_count=np.random.randint(100, 1000),
            false_positive_count=np.random.randint(5, 50),
            average_response_time=np.random.uniform(500, 2000),
            uptime_percentage=np.random.uniform(95, 100),
            efficiency_score=np.random.uniform(0.8, 0.95),
            last_scan=datetime.utcnow() - timedelta(minutes=np.random.randint(1, 60))
        )

    async def shutdown(self) -> None:
        """Shutdown the analytics engine."""
        logger.info("Shutting down Monitoring Analytics...")
        
        self._running = False
        
        # Cancel analytics tasks
        for task in self._analytics_tasks:
            task.cancel()
        
        if self._analytics_tasks:
            await asyncio.gather(*self._analytics_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Monitoring Analytics shutdown complete")
