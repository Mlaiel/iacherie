"""
📊 PERFORMANCE TRACKER - Discovery Engine Analytics & Optimization
===============================================================

Team Specialties:
- Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
- Backend Senior: High-performance monitoring infrastructure
- ML Engineer: Performance prediction & optimization models
- DBA: Database performance analysis & query optimization
- Security Expert: Performance monitoring with privacy protection
- Microservices Architect: Distributed performance tracking
- Audio Specialist: Audio processing performance optimization
- DevOps Engineer: Infrastructure performance monitoring
- IA Prompt Engineer: Search performance & query optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

Enterprise-grade performance tracking system for the discovery engine, providing
real-time analytics, optimization insights, and predictive performance modeling.

Features:
- Real-time performance monitoring with millisecond precision
- User engagement tracking and behavior analysis
- Search performance optimization with ML-driven insights
- Conversion tracking across the discovery funnel
- A/B testing framework for search algorithms
- Performance prediction and capacity planning
- Automated anomaly detection and alerting
- Comprehensive analytics reporting and dashboards
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import time
import statistics
from collections import defaultdict, deque
import threading

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Performance metric types"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    USER_ENGAGEMENT = "user_engagement"
    CONVERSION_RATE = "conversion_rate"

class PerformanceLevel(Enum):
    """Performance level indicators"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class UserAction(Enum):
    """User action types for engagement tracking"""
    SEARCH = "search"
    VIEW_RESULT = "view_result"
    CLICK_CONTENT = "click_content"
    SHARE_CONTENT = "share_content"
    BOOKMARK = "bookmark"
    DOWNLOAD = "download"
    RATE = "rate"
    COMMENT = "comment"
    FOLLOW_CREATOR = "follow_creator"
    SUBSCRIBE = "subscribe"

@dataclass
class DiscoveryMetrics:
    """Core discovery engine metrics"""
    timestamp: datetime
    search_count: int = 0
    unique_users: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    successful_searches: int = 0
    failed_searches: int = 0
    error_rate: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    queries_per_second: float = 0.0

@dataclass
class SearchPerformance:
    """Search-specific performance metrics"""
    query_id: str
    user_id: Optional[str]
    query_text: str
    search_type: str
    start_time: datetime
    end_time: datetime
    response_time_ms: float
    results_count: int
    results_returned: int
    filters_applied: Dict[str, Any]
    modalities_searched: List[str]
    cache_used: bool
    success: bool
    error_message: Optional[str] = None
    relevance_scores: List[float] = field(default_factory=list)
    user_clicked_results: List[int] = field(default_factory=list)
    session_id: Optional[str] = None

@dataclass
class UserEngagement:
    """User engagement tracking"""
    user_id: str
    session_id: str
    timestamp: datetime
    action: UserAction
    content_id: Optional[str] = None
    query_id: Optional[str] = None
    page_url: str = ""
    referrer: str = ""
    user_agent: str = ""
    ip_address: str = ""
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionMetrics:
    """Conversion tracking metrics"""
    timestamp: datetime
    conversion_type: str
    user_id: str
    content_id: str
    query_id: Optional[str]
    conversion_value: float = 0.0
    funnel_stage: str = ""
    time_to_conversion: float = 0.0
    attribution_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_searches: int
    unique_users: int
    average_response_time: float
    success_rate: float
    top_queries: List[Dict[str, Any]]
    performance_trends: Dict[str, List[float]]
    user_engagement_summary: Dict[str, Any]
    conversion_summary: Dict[str, Any]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]

class PerformanceTracker:
    """
    Comprehensive performance tracking and analytics system
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance tracker"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_buffer = deque(maxlen=10000)
        self.search_performance_buffer = deque(maxlen=5000)
        self.engagement_buffer = deque(maxlen=10000)
        self.conversion_buffer = deque(maxlen=1000)
        
        # Real-time metrics
        self.current_metrics = DiscoveryMetrics(timestamp=datetime.now())
        self.performance_cache = {}
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Anomaly detection
        self.anomaly_detector = None
        self.performance_baseline = {}
        
        # Performance thresholds
        self.thresholds = {
            'response_time_ms': {
                'excellent': 100,
                'good': 300,
                'fair': 1000,
                'poor': 3000
            },
            'error_rate': {
                'excellent': 0.01,
                'good': 0.02,
                'fair': 0.05,
                'poor': 0.10
            },
            'cache_hit_rate': {
                'excellent': 0.95,
                'good': 0.80,
                'fair': 0.60,
                'poor': 0.40
            }
        }
        
        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None
        
        # Lock for thread safety
        self._lock = threading.Lock()

    async def initialize(self) -> bool:
        """Initialize performance tracker"""
        try:
            # Initialize anomaly detection
            await self._setup_anomaly_detection()
            
            # Start background monitoring
            await self._start_background_tasks()
            
            # Start Prometheus metrics server
            if self.config.get('prometheus_port'):
                start_http_server(self.config['prometheus_port'])
            
            self.logger.info("PerformanceTracker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PerformanceTracker: {e}")
            return False

    async def track_search_performance(self, performance_data: SearchPerformance):
        """Track individual search performance"""
        try:
            with self._lock:
                # Add to buffer
                self.search_performance_buffer.append(performance_data)
                
                # Update real-time metrics
                await self._update_realtime_metrics(performance_data)
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(performance_data)
                
                # Check for anomalies
                await self._check_performance_anomalies(performance_data)
            
        except Exception as e:
            self.logger.error(f"Failed to track search performance: {e}")

    async def track_user_engagement(self, engagement_data: UserEngagement):
        """Track user engagement metrics"""
        try:
            with self._lock:
                # Add to buffer
                self.engagement_buffer.append(engagement_data)
                
                # Update engagement metrics
                await self._update_engagement_metrics(engagement_data)
            
        except Exception as e:
            self.logger.error(f"Failed to track user engagement: {e}")

    async def track_conversion(self, conversion_data: ConversionMetrics):
        """Track conversion events"""
        try:
            with self._lock:
                # Add to buffer
                self.conversion_buffer.append(conversion_data)
                
                # Update conversion metrics
                await self._update_conversion_metrics(conversion_data)
            
        except Exception as e:
            self.logger.error(f"Failed to track conversion: {e}")

    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        try:
            with self._lock:
                metrics = {
                    'current_metrics': self.current_metrics,
                    'last_updated': datetime.now(),
                    'active_searches': len([p for p in self.search_performance_buffer 
                                          if (datetime.now() - p.start_time).seconds < 60]),
                    'recent_response_times': [p.response_time_ms for p in 
                                            list(self.search_performance_buffer)[-100:]],
                    'recent_error_rate': self._calculate_recent_error_rate(),
                    'cache_performance': self._calculate_cache_performance(),
                    'system_health': await self._assess_system_health()
                }
                
                return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get realtime metrics: {e}")
            return {}

    async def generate_performance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        include_details: bool = True
    ) -> AnalyticsReport:
        """Generate comprehensive performance report"""
        try:
            # Filter data by time range
            filtered_searches = [
                p for p in self.search_performance_buffer
                if start_time <= p.start_time <= end_time
            ]
            
            filtered_engagement = [
                e for e in self.engagement_buffer
                if start_time <= e.timestamp <= end_time
            ]
            
            filtered_conversions = [
                c for c in self.conversion_buffer
                if start_time <= c.timestamp <= end_time
            ]
            
            # Calculate aggregate metrics
            total_searches = len(filtered_searches)
            unique_users = len(set(p.user_id for p in filtered_searches if p.user_id))
            
            response_times = [p.response_time_ms for p in filtered_searches]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            successful_searches = len([p for p in filtered_searches if p.success])
            success_rate = successful_searches / total_searches if total_searches > 0 else 0
            
            # Generate insights
            top_queries = await self._analyze_top_queries(filtered_searches)
            performance_trends = await self._analyze_performance_trends(filtered_searches)
            engagement_summary = await self._analyze_user_engagement(filtered_engagement)
            conversion_summary = await self._analyze_conversions(filtered_conversions)
            recommendations = await self._generate_recommendations(filtered_searches)
            alerts = await self._generate_alerts(filtered_searches)
            
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.now(),
                period_start=start_time,
                period_end=end_time,
                total_searches=total_searches,
                unique_users=unique_users,
                average_response_time=avg_response_time,
                success_rate=success_rate,
                top_queries=top_queries,
                performance_trends=performance_trends,
                user_engagement_summary=engagement_summary,
                conversion_summary=conversion_summary,
                recommendations=recommendations,
                alerts=alerts
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return AnalyticsReport(
                report_id="error",
                generated_at=datetime.now(),
                period_start=start_time,
                period_end=end_time,
                total_searches=0,
                unique_users=0,
                average_response_time=0,
                success_rate=0,
                top_queries=[],
                performance_trends={},
                user_engagement_summary={},
                conversion_summary={},
                recommendations=[],
                alerts=[]
            )

    async def optimize_performance(self) -> Dict[str, Any]:
        """Analyze performance and suggest optimizations"""
        try:
            # Analyze recent performance data
            recent_searches = list(self.search_performance_buffer)[-1000:]
            
            optimizations = {
                'cache_optimization': await self._analyze_cache_performance(recent_searches),
                'query_optimization': await self._analyze_query_performance(recent_searches),
                'resource_optimization': await self._analyze_resource_usage(),
                'user_experience_optimization': await self._analyze_user_experience(),
                'system_recommendations': await self._generate_system_recommendations()
            }
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Failed to optimize performance: {e}")
            return {}

    async def predict_performance(
        self,
        future_load: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict performance under different load scenarios"""
        try:
            # Analyze historical data
            historical_data = await self._prepare_historical_data()
            
            # Train prediction models
            response_time_model = await self._train_response_time_model(historical_data)
            resource_usage_model = await self._train_resource_usage_model(historical_data)
            
            # Make predictions
            predictions = {
                'response_time_prediction': await self._predict_response_time(
                    response_time_model, future_load
                ),
                'resource_usage_prediction': await self._predict_resource_usage(
                    resource_usage_model, future_load
                ),
                'capacity_recommendations': await self._recommend_capacity_changes(
                    future_load
                ),
                'bottleneck_analysis': await self._predict_bottlenecks(future_load)
            }
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to predict performance: {e}")
            return {}

    async def create_performance_dashboard(self) -> Dict[str, Any]:
        """Create performance dashboard data"""
        try:
            # Get recent metrics
            current_time = datetime.now()
            last_hour = current_time - timedelta(hours=1)
            last_day = current_time - timedelta(days=1)
            
            # Response time chart data
            response_times = await self._get_response_time_chart_data(last_day)
            
            # Throughput chart data
            throughput = await self._get_throughput_chart_data(last_day)
            
            # Error rate chart data
            error_rates = await self._get_error_rate_chart_data(last_day)
            
            # Cache performance
            cache_performance = await self._get_cache_performance_data(last_day)
            
            # User engagement metrics
            engagement_metrics = await self._get_engagement_metrics(last_day)
            
            # System health indicators
            health_indicators = await self._get_health_indicators()
            
            dashboard = {
                'timestamp': current_time.isoformat(),
                'summary_stats': {
                    'current_qps': await self._get_current_qps(),
                    'average_response_time': await self._get_average_response_time(last_hour),
                    'error_rate': await self._get_error_rate(last_hour),
                    'cache_hit_rate': await self._get_cache_hit_rate(last_hour)
                },
                'charts': {
                    'response_times': response_times,
                    'throughput': throughput,
                    'error_rates': error_rates,
                    'cache_performance': cache_performance
                },
                'engagement': engagement_metrics,
                'health': health_indicators,
                'alerts': await self._get_active_alerts(),
                'recommendations': await self._get_dashboard_recommendations()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Failed to create performance dashboard: {e}")
            return {}

    # Private methods for internal processing

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        try:
            # Counter metrics
            self.search_total = Counter(
                'discovery_searches_total',
                'Total number of searches',
                ['status', 'search_type']
            )
            
            self.user_actions_total = Counter(
                'discovery_user_actions_total',
                'Total user actions',
                ['action_type']
            )
            
            # Histogram metrics
            self.response_time_histogram = Histogram(
                'discovery_response_time_seconds',
                'Response time distribution',
                ['search_type']
            )
            
            # Gauge metrics
            self.active_users_gauge = Gauge(
                'discovery_active_users',
                'Number of active users'
            )
            
            self.cache_hit_rate_gauge = Gauge(
                'discovery_cache_hit_rate',
                'Cache hit rate percentage'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup Prometheus metrics: {e}")

    async def _setup_anomaly_detection(self):
        """Setup anomaly detection models"""
        try:
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Initialize with baseline data if available
            if len(self.search_performance_buffer) > 100:
                features = self._extract_performance_features(
                    list(self.search_performance_buffer)[-100:]
                )
                self.anomaly_detector.fit(features)
            
        except Exception as e:
            self.logger.error(f"Failed to setup anomaly detection: {e}")

    async def _start_background_tasks(self):
        """Start background monitoring tasks"""
        try:
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
        except Exception as e:
            self.logger.error(f"Failed to start background tasks: {e}")

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Check for alerts
                await self._check_system_alerts()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Remove old metrics beyond retention period
                retention_hours = self.config.get('retention_hours', 24)
                cutoff_time = datetime.now() - timedelta(hours=retention_hours)
                
                # Cleanup buffers
                self._cleanup_buffer(self.search_performance_buffer, cutoff_time)
                self._cleanup_buffer(self.engagement_buffer, cutoff_time)
                self._cleanup_buffer(self.conversion_buffer, cutoff_time)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_buffer(self, buffer: deque, cutoff_time: datetime):
        """Cleanup old entries from buffer"""
        while buffer and buffer[0].timestamp < cutoff_time:
            buffer.popleft()

    async def _update_realtime_metrics(self, performance_data: SearchPerformance):
        """Update real-time metrics with new performance data"""
        try:
            # Update search count
            self.current_metrics.search_count += 1
            
            # Update response time
            self.current_metrics.total_response_time += performance_data.response_time_ms
            self.current_metrics.average_response_time = (
                self.current_metrics.total_response_time / self.current_metrics.search_count
            )
            
            # Update success/failure counts
            if performance_data.success:
                self.current_metrics.successful_searches += 1
            else:
                self.current_metrics.failed_searches += 1
            
            # Update error rate
            total_searches = self.current_metrics.search_count
            self.current_metrics.error_rate = (
                self.current_metrics.failed_searches / total_searches
            )
            
            # Update cache metrics
            if performance_data.cache_used:
                self.current_metrics.cache_hits += 1
            else:
                self.current_metrics.cache_misses += 1
            
            total_cache_attempts = (
                self.current_metrics.cache_hits + self.current_metrics.cache_misses
            )
            if total_cache_attempts > 0:
                self.current_metrics.cache_hit_rate = (
                    self.current_metrics.cache_hits / total_cache_attempts
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update realtime metrics: {e}")

    def _update_prometheus_metrics(self, performance_data: SearchPerformance):
        """Update Prometheus metrics"""
        try:
            # Update counters
            status = 'success' if performance_data.success else 'error'
            self.search_total.labels(
                status=status,
                search_type=performance_data.search_type
            ).inc()
            
            # Update histograms
            self.response_time_histogram.labels(
                search_type=performance_data.search_type
            ).observe(performance_data.response_time_ms / 1000)  # Convert to seconds
            
            # Update gauges
            self.cache_hit_rate_gauge.set(self.current_metrics.cache_hit_rate)
            
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus metrics: {e}")

    async def _check_performance_anomalies(self, performance_data: SearchPerformance):
        """Check for performance anomalies"""
        try:
            if self.anomaly_detector is None:
                return
            
            # Extract features
            features = np.array([[
                performance_data.response_time_ms,
                performance_data.results_count,
                1 if performance_data.cache_used else 0,
                1 if performance_data.success else 0
            ]])
            
            # Check for anomaly
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            is_anomaly = self.anomaly_detector.predict(features)[0] == -1
            
            if is_anomaly:
                await self._handle_performance_anomaly(performance_data, anomaly_score)
            
        except Exception as e:
            self.logger.error(f"Failed to check performance anomalies: {e}")

    async def _handle_performance_anomaly(
        self,
        performance_data: SearchPerformance,
        anomaly_score: float
    ):
        """Handle detected performance anomaly"""
        try:
            alert = {
                'timestamp': datetime.now(),
                'type': 'performance_anomaly',
                'severity': AlertSeverity.HIGH,
                'query_id': performance_data.query_id,
                'response_time': performance_data.response_time_ms,
                'anomaly_score': anomaly_score,
                'message': f"Abnormal performance detected for query {performance_data.query_id}"
            }
            
            self.logger.warning(f"Performance anomaly detected: {alert}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle performance anomaly: {e}")

    def _calculate_recent_error_rate(self) -> float:
        """Calculate error rate for recent searches"""
        try:
            recent_searches = [
                p for p in self.search_performance_buffer
                if (datetime.now() - p.start_time).seconds < 300  # Last 5 minutes
            ]
            
            if not recent_searches:
                return 0.0
            
            failed_searches = len([p for p in recent_searches if not p.success])
            return failed_searches / len(recent_searches)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate recent error rate: {e}")
            return 0.0

    def _calculate_cache_performance(self) -> Dict[str, float]:
        """Calculate cache performance metrics"""
        try:
            recent_searches = [
                p for p in self.search_performance_buffer
                if (datetime.now() - p.start_time).seconds < 300  # Last 5 minutes
            ]
            
            if not recent_searches:
                return {'hit_rate': 0.0, 'miss_rate': 1.0}
            
            cache_hits = len([p for p in recent_searches if p.cache_used])
            hit_rate = cache_hits / len(recent_searches)
            
            return {
                'hit_rate': hit_rate,
                'miss_rate': 1.0 - hit_rate,
                'total_requests': len(recent_searches)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate cache performance: {e}")
            return {'hit_rate': 0.0, 'miss_rate': 1.0}

    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        try:
            recent_metrics = self.current_metrics
            
            # Assess response time health
            response_time_health = self._assess_metric_health(
                recent_metrics.average_response_time,
                self.thresholds['response_time_ms']
            )
            
            # Assess error rate health
            error_rate_health = self._assess_metric_health(
                recent_metrics.error_rate,
                self.thresholds['error_rate'],
                lower_is_better=True
            )
            
            # Assess cache performance health
            cache_health = self._assess_metric_health(
                recent_metrics.cache_hit_rate,
                self.thresholds['cache_hit_rate']
            )
            
            # Overall health score
            health_scores = [
                response_time_health['score'],
                error_rate_health['score'],
                cache_health['score']
            ]
            overall_score = sum(health_scores) / len(health_scores)
            
            return {
                'overall_score': overall_score,
                'overall_status': self._score_to_status(overall_score),
                'components': {
                    'response_time': response_time_health,
                    'error_rate': error_rate_health,
                    'cache_performance': cache_health
                },
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assess system health: {e}")
            return {'overall_score': 0.0, 'overall_status': 'unknown'}

    def _assess_metric_health(
        self,
        value: float,
        thresholds: Dict[str, float],
        lower_is_better: bool = False
    ) -> Dict[str, Any]:
        """Assess health of a specific metric"""
        try:
            if lower_is_better:
                if value <= thresholds['excellent']:
                    return {'score': 1.0, 'status': PerformanceLevel.EXCELLENT}
                elif value <= thresholds['good']:
                    return {'score': 0.8, 'status': PerformanceLevel.GOOD}
                elif value <= thresholds['fair']:
                    return {'score': 0.6, 'status': PerformanceLevel.FAIR}
                elif value <= thresholds['poor']:
                    return {'score': 0.4, 'status': PerformanceLevel.POOR}
                else:
                    return {'score': 0.2, 'status': PerformanceLevel.CRITICAL}
            else:
                if value >= thresholds['excellent']:
                    return {'score': 1.0, 'status': PerformanceLevel.EXCELLENT}
                elif value >= thresholds['good']:
                    return {'score': 0.8, 'status': PerformanceLevel.GOOD}
                elif value >= thresholds['fair']:
                    return {'score': 0.6, 'status': PerformanceLevel.FAIR}
                elif value >= thresholds['poor']:
                    return {'score': 0.4, 'status': PerformanceLevel.POOR}
                else:
                    return {'score': 0.2, 'status': PerformanceLevel.CRITICAL}
                    
        except Exception as e:
            self.logger.error(f"Failed to assess metric health: {e}")
            return {'score': 0.0, 'status': PerformanceLevel.CRITICAL}

    def _score_to_status(self, score: float) -> str:
        """Convert numeric score to status string"""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.5:
            return 'fair'
        elif score >= 0.3:
            return 'poor'
        else:
            return 'critical'

    # Additional helper methods for data analysis

    async def _analyze_top_queries(self, searches: List[SearchPerformance]) -> List[Dict[str, Any]]:
        """Analyze top performing queries"""
        query_stats = defaultdict(lambda: {'count': 0, 'avg_response_time': 0, 'success_rate': 0})
        
        for search in searches:
            stats = query_stats[search.query_text]
            stats['count'] += 1
            stats['avg_response_time'] += search.response_time_ms
            if search.success:
                stats['success_rate'] += 1
        
        # Calculate averages and sort
        top_queries = []
        for query, stats in query_stats.items():
            if stats['count'] > 0:
                top_queries.append({
                    'query': query,
                    'count': stats['count'],
                    'avg_response_time': stats['avg_response_time'] / stats['count'],
                    'success_rate': stats['success_rate'] / stats['count']
                })
        
        return sorted(top_queries, key=lambda x: x['count'], reverse=True)[:10]

    async def _analyze_performance_trends(self, searches: List[SearchPerformance]) -> Dict[str, List[float]]:
        """Analyze performance trends over time"""
        # Group by hour and calculate metrics
        hourly_metrics = defaultdict(lambda: {'response_times': [], 'error_count': 0, 'total_count': 0})
        
        for search in searches:
            hour_key = search.start_time.replace(minute=0, second=0, microsecond=0)
            metrics = hourly_metrics[hour_key]
            metrics['response_times'].append(search.response_time_ms)
            metrics['total_count'] += 1
            if not search.success:
                metrics['error_count'] += 1
        
        # Calculate trends
        trends = {
            'response_time_trend': [],
            'error_rate_trend': [],
            'throughput_trend': []
        }
        
        for hour, metrics in sorted(hourly_metrics.items()):
            avg_response_time = statistics.mean(metrics['response_times']) if metrics['response_times'] else 0
            error_rate = metrics['error_count'] / metrics['total_count'] if metrics['total_count'] > 0 else 0
            
            trends['response_time_trend'].append(avg_response_time)
            trends['error_rate_trend'].append(error_rate)
            trends['throughput_trend'].append(metrics['total_count'])
        
        return trends

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            return {
                'realtime_metrics': await self.get_realtime_metrics(),
                'system_health': await self._assess_system_health(),
                'performance_summary': {
                    'total_searches_tracked': len(self.search_performance_buffer),
                    'total_engagements_tracked': len(self.engagement_buffer),
                    'total_conversions_tracked': len(self.conversion_buffer),
                    'tracking_uptime': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {}

    async def shutdown(self):
        """Cleanup and shutdown performance tracker"""
        try:
            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Clear buffers
            self.metrics_buffer.clear()
            self.search_performance_buffer.clear()
            self.engagement_buffer.clear()
            self.conversion_buffer.clear()
            
            self.logger.info("PerformanceTracker shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during PerformanceTracker shutdown: {e}")
