"""
Enterprise Metrics Collector - Ainflue Platform
==============================================
Multi-expert implementation combining DevOps + Backend Senior + ML Engineer +
DBA expertise for real-time API metrics collection, performance analytics,
and business intelligence with Ainflue creator economy insights.

Architecture Features:
- Real-Time Metrics Collection (latency + throughput + error rates)
- Business Metrics Tracking (creator engagement + revenue + conversions)
- Performance Analytics (response times + resource utilization)
- Creator Performance Metrics (content upload + engagement analytics)
- Platform Integration Metrics (65+ platforms performance tracking)
- AI Model Performance Metrics (inference latency + accuracy tracking)

Author: Fahed Mlaiel (mlaiel@live.de)
IP Protection: Exclusive intellectual property - All rights reserved
Business Logic: Ainflue creator metrics and platform analytics optimization
"""

import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import logging
from collections import defaultdict, deque
import json
import hashlib
from pathlib import Path

# Core dependencies
from pydantic import BaseModel, Field, validator
import httpx


class MetricType(str, Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"


class MetricSeverity(str, Enum):
    """Metric alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CreatorMetricCategory(str, Enum):
    """Creator-specific metric categories"""
    CONTENT_UPLOAD = "content_upload"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    AI_PROCESSING = "ai_processing"
    PLATFORM_SYNC = "platform_sync"
    ANALYTICS_VIEWS = "analytics_views"


class PlatformMetricCategory(str, Enum):
    """Platform integration metric categories"""
    API_CALLS = "api_calls"
    AUTHENTICATION = "authentication"
    CONTENT_DISTRIBUTION = "content_distribution"
    DATA_SYNC = "data_sync"
    ERROR_RATES = "error_rates"
    RATE_LIMITING = "rate_limiting"


@dataclass
class MetricData:
    """Individual metric data point"""
    metric_name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Creator economy context
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    
    # Performance context
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    
    # Business context
    revenue_impact: Optional[float] = None
    user_engagement_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary format"""
        return {
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'creator_id': self.creator_id,
            'platform': self.platform,
            'content_type': self.content_type,
            'request_id': self.request_id,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'revenue_impact': self.revenue_impact,
            'user_engagement_score': self.user_engagement_score
        }


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    metric_name: str
    condition: str  # gt, lt, eq, etc.
    threshold: float
    severity: MetricSeverity
    duration_seconds: int = 300  # 5 minutes
    cooldown_seconds: int = 900  # 15 minutes
    enabled: bool = True
    
    # Creator-specific alerting
    creator_filter: Optional[str] = None
    platform_filter: Optional[str] = None
    
    # Business impact alerting
    revenue_impact_threshold: Optional[float] = None
    engagement_impact_threshold: Optional[float] = None


@dataclass
class MetricSummary:
    """Aggregated metric summary"""
    metric_name: str
    count: int
    sum_value: float
    avg_value: float
    min_value: float
    max_value: float
    percentile_95: float
    percentile_99: float
    timestamp_range: tuple[datetime, datetime]
    
    # Business metrics
    total_revenue_impact: float = 0.0
    avg_engagement_score: float = 0.0
    
    # Creator breakdown
    creator_breakdown: Dict[str, float] = field(default_factory=dict)
    platform_breakdown: Dict[str, float] = field(default_factory=dict)


class BusinessMetrics(BaseModel):
    """Business-specific metrics model"""
    daily_active_creators: int = 0
    total_content_uploads: int = 0
    successful_platform_syncs: int = 0
    ai_processing_requests: int = 0
    revenue_generated: float = 0.0
    engagement_score_avg: float = 0.0
    
    # Platform-specific metrics
    platform_api_calls: Dict[str, int] = Field(default_factory=dict)
    platform_success_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Creator-specific metrics
    creator_activity: Dict[str, int] = Field(default_factory=dict)
    content_type_distribution: Dict[str, int] = Field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance-specific metrics model"""
    avg_response_time_ms: float = 0.0
    request_throughput_per_second: float = 0.0
    error_rate_percent: float = 0.0
    availability_percent: float = 100.0
    
    # Resource utilization
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    
    # API-specific metrics
    endpoint_performance: Dict[str, float] = Field(default_factory=dict)
    status_code_distribution: Dict[str, int] = Field(default_factory=dict)


class EnterpriseMetricsCollector:
    """
    Enterprise Metrics Collector with multi-expert implementation
    
    Expert Contributions:
    - DevOps: Infrastructure monitoring + alerting automation
    - Backend Senior: API performance tracking + optimization insights
    - ML Engineer: Predictive analytics + anomaly detection
    - DBA: Metrics storage optimization + query performance
    - Security: Security metrics + threat detection indicators
    - Lead Dev IA: Creator behavior analytics + business intelligence
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize enterprise metrics collector"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EnterpriseMetricsCollector")
        
        # Collection configuration
        self.collection_interval_seconds = config.get('collection_interval', 10)
        self.retention_days = config.get('retention_days', 30)
        self.batch_size = config.get('batch_size', 1000)
        
        # Storage configuration
        self.enable_real_time_storage = config.get('enable_real_time_storage', True)
        self.enable_time_series_storage = config.get('enable_time_series_storage', True)
        self.storage_backend = config.get('storage_backend', 'memory')  # memory, redis, influxdb
        
        # In-memory metric storage (for demo - production would use time-series DB)
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.aggregated_metrics: Dict[str, List[MetricData]] = defaultdict(list)
        self.real_time_metrics: Dict[str, MetricData] = {}
        
        # Creator economy specific metrics storage
        self.creator_metrics: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                'total_uploads': 0,
                'total_engagement': 0.0,
                'total_revenue': 0.0,
                'platform_distribution': defaultdict(int),
                'content_type_distribution': defaultdict(int),
                'ai_processing_usage': defaultdict(int)
            }
        )
        
        # Platform integration metrics
        self.platform_metrics: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                'api_calls_total': 0,
                'success_count': 0,
                'error_count': 0,
                'avg_response_time': 0.0,
                'rate_limit_hits': 0,
                'auth_failures': 0
            }
        )
        
        # Alert configuration
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.business_metrics_history: deque = deque(maxlen=1000)
        
        # Initialize default alert rules
        self._initialize_default_alerts()
        
        # Start collection tasks
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._alert_monitoring_loop())
        
        self.logger.info("Enterprise Metrics Collector initialized")
    
    def _initialize_default_alerts(self):
        """Initialize default alert rules for Ainflue platform"""
        default_alerts = [
            AlertRule(
                rule_id="high_api_latency",
                metric_name="api_response_time_ms",
                condition="gt",
                threshold=1000.0,  # > 1 second
                severity=MetricSeverity.WARNING,
                duration_seconds=300
            ),
            AlertRule(
                rule_id="critical_api_latency",
                metric_name="api_response_time_ms",
                condition="gt",
                threshold=5000.0,  # > 5 seconds
                severity=MetricSeverity.CRITICAL,
                duration_seconds=60
            ),
            AlertRule(
                rule_id="high_error_rate",
                metric_name="api_error_rate_percent",
                condition="gt",
                threshold=5.0,  # > 5% error rate
                severity=MetricSeverity.WARNING,
                duration_seconds=180
            ),
            AlertRule(
                rule_id="creator_upload_failure",
                metric_name="creator_upload_failure_rate",
                condition="gt",
                threshold=10.0,  # > 10% failure rate
                severity=MetricSeverity.CRITICAL,
                duration_seconds=120
            ),
            AlertRule(
                rule_id="ai_processing_latency",
                metric_name="ai_processing_time_ms",
                condition="gt",
                threshold=30000.0,  # > 30 seconds
                severity=MetricSeverity.WARNING,
                duration_seconds=300
            ),
            AlertRule(
                rule_id="platform_sync_failure",
                metric_name="platform_sync_failure_rate",
                condition="gt",
                threshold=15.0,  # > 15% failure rate
                severity=MetricSeverity.CRITICAL,
                duration_seconds=240
            )
        ]
        
        for alert in default_alerts:
            self.alert_rules[alert.rule_id] = alert
    
    async def collect_metric(self, metric: MetricData):
        """
        Collect individual metric with real-time processing
        
        Expert Implementation:
        - DevOps: Real-time metric ingestion + buffering
        - ML Engineer: Anomaly detection + trend analysis
        - Backend Senior: Performance impact analysis
        """
        try:
            # Add timestamp if not provided
            if not metric.timestamp:
                metric.timestamp = datetime.utcnow()
            
            # Store in buffer
            self.metrics_buffer.append(metric)
            
            # Store in aggregated metrics
            self.aggregated_metrics[metric.metric_name].append(metric)
            
            # Update real-time metrics
            self.real_time_metrics[metric.metric_name] = metric
            
            # Update creator-specific metrics
            if metric.creator_id:
                await self._update_creator_metrics(metric)
            
            # Update platform-specific metrics
            if metric.platform:
                await self._update_platform_metrics(metric)
            
            # Check alert conditions
            await self._check_alert_conditions(metric)
            
            # Perform real-time analysis
            await self._perform_real_time_analysis(metric)
            
        except Exception as e:
            self.logger.error(f"Error collecting metric {metric.metric_name}: {str(e)}")
    
    async def collect_api_request_metric(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        request_id: str,
        creator_id: Optional[str] = None,
        platform: Optional[str] = None
    ):
        """Collect API request metrics with detailed context"""
        
        # Basic API metrics
        await self.collect_metric(MetricData(
            metric_name="api_requests_total",
            metric_type=MetricType.COUNTER,
            value=1,
            timestamp=datetime.utcnow(),
            tags={'endpoint': endpoint, 'method': method, 'status': str(status_code)},
            creator_id=creator_id,
            platform=platform,
            request_id=request_id,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms
        ))
        
        # Response time metric
        await self.collect_metric(MetricData(
            metric_name="api_response_time_ms",
            metric_type=MetricType.TIMER,
            value=response_time_ms,
            timestamp=datetime.utcnow(),
            tags={'endpoint': endpoint, 'method': method},
            creator_id=creator_id,
            platform=platform,
            request_id=request_id,
            endpoint=endpoint,
            response_time_ms=response_time_ms
        ))
        
        # Error tracking
        if status_code >= 400:
            await self.collect_metric(MetricData(
                metric_name="api_errors_total",
                metric_type=MetricType.COUNTER,
                value=1,
                timestamp=datetime.utcnow(),
                tags={'endpoint': endpoint, 'status': str(status_code)},
                creator_id=creator_id,
                platform=platform,
                request_id=request_id,
                status_code=status_code
            ))
    
    async def collect_creator_metric(
        self,
        creator_id: str,
        metric_category: CreatorMetricCategory,
        value: Union[int, float],
        content_type: Optional[str] = None,
        platform: Optional[str] = None,
        revenue_impact: Optional[float] = None,
        engagement_score: Optional[float] = None
    ):
        """Collect creator-specific metrics"""
        
        metric_name = f"creator_{metric_category.value}"
        
        await self.collect_metric(MetricData(
            metric_name=metric_name,
            metric_type=MetricType.COUNTER if metric_category in [
                CreatorMetricCategory.CONTENT_UPLOAD,
                CreatorMetricCategory.PLATFORM_SYNC
            ] else MetricType.GAUGE,
            value=value,
            timestamp=datetime.utcnow(),
            tags={
                'category': metric_category.value,
                'content_type': content_type or 'unknown',
                'platform': platform or 'unknown'
            },
            creator_id=creator_id,
            platform=platform,
            content_type=content_type,
            revenue_impact=revenue_impact,
            user_engagement_score=engagement_score
        ))
    
    async def collect_platform_metric(
        self,
        platform: str,
        metric_category: PlatformMetricCategory,
        value: Union[int, float],
        success: bool = True,
        response_time_ms: Optional[float] = None
    ):
        """Collect platform integration metrics"""
        
        metric_name = f"platform_{metric_category.value}"
        
        await self.collect_metric(MetricData(
            metric_name=metric_name,
            metric_type=MetricType.COUNTER if metric_category in [
                PlatformMetricCategory.API_CALLS,
                PlatformMetricCategory.ERROR_RATES
            ] else MetricType.GAUGE,
            value=value,
            timestamp=datetime.utcnow(),
            tags={
                'platform': platform,
                'category': metric_category.value,
                'success': str(success)
            },
            platform=platform,
            response_time_ms=response_time_ms
        ))
    
    async def collect_ai_processing_metric(
        self,
        model_name: str,
        processing_time_ms: float,
        accuracy_score: Optional[float] = None,
        creator_id: Optional[str] = None,
        content_type: Optional[str] = None
    ):
        """Collect AI model performance metrics"""
        
        # Processing time metric
        await self.collect_metric(MetricData(
            metric_name="ai_processing_time_ms",
            metric_type=MetricType.TIMER,
            value=processing_time_ms,
            timestamp=datetime.utcnow(),
            tags={'model': model_name, 'content_type': content_type or 'unknown'},
            creator_id=creator_id,
            content_type=content_type
        ))
        
        # Accuracy metric
        if accuracy_score is not None:
            await self.collect_metric(MetricData(
                metric_name="ai_model_accuracy",
                metric_type=MetricType.GAUGE,
                value=accuracy_score,
                timestamp=datetime.utcnow(),
                tags={'model': model_name},
                creator_id=creator_id
            ))
    
    async def _update_creator_metrics(self, metric: MetricData):
        """Update creator-specific aggregated metrics"""
        creator_id = metric.creator_id
        creator_data = self.creator_metrics[creator_id]
        
        # Update based on metric type
        if 'upload' in metric.metric_name:
            creator_data['total_uploads'] += metric.value
            
            if metric.content_type:
                creator_data['content_type_distribution'][metric.content_type] += metric.value
        
        if 'engagement' in metric.metric_name and metric.user_engagement_score:
            creator_data['total_engagement'] += metric.user_engagement_score
        
        if metric.revenue_impact:
            creator_data['total_revenue'] += metric.revenue_impact
        
        if metric.platform:
            creator_data['platform_distribution'][metric.platform] += metric.value
        
        if 'ai_processing' in metric.metric_name:
            creator_data['ai_processing_usage'][metric.metric_name] += metric.value
    
    async def _update_platform_metrics(self, metric: MetricData):
        """Update platform-specific aggregated metrics"""
        platform = metric.platform
        platform_data = self.platform_metrics[platform]
        
        # Update based on metric name
        if 'api_calls' in metric.metric_name:
            platform_data['api_calls_total'] += metric.value
        
        if 'error' in metric.metric_name:
            platform_data['error_count'] += metric.value
        elif metric.status_code and metric.status_code < 400:
            platform_data['success_count'] += metric.value
        
        if metric.response_time_ms:
            # Update rolling average
            current_avg = platform_data['avg_response_time']
            total_calls = platform_data['api_calls_total']
            
            if total_calls > 0:
                platform_data['avg_response_time'] = (
                    (current_avg * (total_calls - 1) + metric.response_time_ms) / total_calls
                )
    
    async def _check_alert_conditions(self, metric: MetricData):
        """Check if metric triggers any alert conditions"""
        current_time = datetime.utcnow()
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule applies to this metric
            if rule.metric_name != metric.metric_name:
                continue
            
            # Check creator filter
            if rule.creator_filter and metric.creator_id != rule.creator_filter:
                continue
            
            # Check platform filter
            if rule.platform_filter and metric.platform != rule.platform_filter:
                continue
            
            # Check cooldown
            if rule_id in self.alert_cooldowns:
                if current_time < self.alert_cooldowns[rule_id]:
                    continue
            
            # Evaluate condition
            triggered = self._evaluate_alert_condition(rule, metric.value)
            
            if triggered:
                await self._trigger_alert(rule, metric)
    
    def _evaluate_alert_condition(self, rule: AlertRule, value: float) -> bool:
        """Evaluate alert condition"""
        if rule.condition == "gt":
            return value > rule.threshold
        elif rule.condition == "lt":
            return value < rule.threshold
        elif rule.condition == "eq":
            return value == rule.threshold
        elif rule.condition == "gte":
            return value >= rule.threshold
        elif rule.condition == "lte":
            return value <= rule.threshold
        
        return False
    
    async def _trigger_alert(self, rule: AlertRule, metric: MetricData):
        """Trigger alert and handle notifications"""
        alert_id = f"{rule.rule_id}_{int(time.time())}"
        
        alert_data = {
            'alert_id': alert_id,
            'rule_id': rule.rule_id,
            'severity': rule.severity.value,
            'metric_name': metric.metric_name,
            'metric_value': metric.value,
            'threshold': rule.threshold,
            'triggered_at': datetime.utcnow().isoformat(),
            'creator_id': metric.creator_id,
            'platform': metric.platform,
            'tags': metric.tags
        }
        
        self.active_alerts[alert_id] = alert_data
        
        # Set cooldown
        cooldown_until = datetime.utcnow() + timedelta(seconds=rule.cooldown_seconds)
        self.alert_cooldowns[rule.rule_id] = cooldown_until
        
        self.logger.warning(
            f"Alert triggered: {rule.rule_id} - {metric.metric_name} = {metric.value} "
            f"(threshold: {rule.threshold})"
        )
        
        # In production: send to alerting system (PagerDuty, Slack, etc.)
        await self._send_alert_notification(alert_data)
    
    async def _send_alert_notification(self, alert_data: Dict[str, Any]):
        """Send alert notification (placeholder implementation)"""
        # In production: integrate with alerting systems
        self.logger.info(f"Alert notification sent: {alert_data['alert_id']}")
    
    async def _perform_real_time_analysis(self, metric: MetricData):
        """Perform real-time analysis on incoming metrics"""
        
        # Anomaly detection (simplified)
        if metric.metric_type == MetricType.TIMER:
            await self._detect_performance_anomalies(metric)
        
        # Business impact analysis
        if metric.revenue_impact:
            await self._analyze_revenue_impact(metric)
        
        # Creator behavior analysis
        if metric.creator_id:
            await self._analyze_creator_behavior(metric)
    
    async def _detect_performance_anomalies(self, metric: MetricData):
        """Detect performance anomalies using statistical analysis"""
        metric_name = metric.metric_name
        recent_metrics = self.aggregated_metrics[metric_name][-100:]  # Last 100 data points
        
        if len(recent_metrics) < 10:
            return  # Not enough data
        
        values = [m.value for m in recent_metrics]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Z-score anomaly detection
        if std_dev > 0:
            z_score = abs((metric.value - mean_value) / std_dev)
            
            if z_score > 3:  # 3 standard deviations
                await self.collect_metric(MetricData(
                    metric_name="performance_anomaly_detected",
                    metric_type=MetricType.COUNTER,
                    value=1,
                    timestamp=datetime.utcnow(),
                    tags={
                        'original_metric': metric_name,
                        'z_score': str(round(z_score, 2)),
                        'severity': 'high' if z_score > 4 else 'medium'
                    },
                    creator_id=metric.creator_id,
                    platform=metric.platform
                ))
    
    async def _analyze_revenue_impact(self, metric: MetricData):
        """Analyze revenue impact of metrics"""
        if metric.revenue_impact and metric.revenue_impact < 0:
            # Negative revenue impact detected
            await self.collect_metric(MetricData(
                metric_name="revenue_loss_detected",
                metric_type=MetricType.COUNTER,
                value=abs(metric.revenue_impact),
                timestamp=datetime.utcnow(),
                tags={'source_metric': metric.metric_name},
                creator_id=metric.creator_id,
                platform=metric.platform,
                revenue_impact=metric.revenue_impact
            ))
    
    async def _analyze_creator_behavior(self, metric: MetricData):
        """Analyze creator behavior patterns"""
        creator_data = self.creator_metrics[metric.creator_id]
        
        # Check for unusual activity patterns
        if 'upload' in metric.metric_name:
            recent_uploads = creator_data['total_uploads']
            
            # Check for upload spikes (simplified heuristic)
            if recent_uploads > 0 and metric.value > recent_uploads * 0.5:
                await self.collect_metric(MetricData(
                    metric_name="creator_activity_spike",
                    metric_type=MetricType.COUNTER,
                    value=1,
                    timestamp=datetime.utcnow(),
                    tags={'activity_type': 'upload_spike'},
                    creator_id=metric.creator_id
                ))
    
    async def _metrics_collection_loop(self):
        """Background task for periodic metrics collection"""
        while True:
            try:
                await self._collect_system_metrics()
                await self._aggregate_business_metrics()
                await self._cleanup_old_metrics()
                
                await asyncio.sleep(self.collection_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Metrics collection loop error: {str(e)}")
                await asyncio.sleep(30)  # Error backoff
    
    async def _alert_monitoring_loop(self):
        """Background task for alert monitoring"""
        while True:
            try:
                await self._process_alert_conditions()
                await self._cleanup_expired_alerts()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Alert monitoring loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        # In production: collect from system monitoring
        current_time = datetime.utcnow()
        
        # Simulate system metrics
        await self.collect_metric(MetricData(
            metric_name="system_cpu_usage_percent",
            metric_type=MetricType.GAUGE,
            value=25.0 + (time.time() % 10),  # Simulated CPU usage
            timestamp=current_time,
            tags={'instance': 'api-server-1'}
        ))
        
        await self.collect_metric(MetricData(
            metric_name="system_memory_usage_percent",
            metric_type=MetricType.GAUGE,
            value=60.0 + (time.time() % 20),  # Simulated memory usage
            timestamp=current_time,
            tags={'instance': 'api-server-1'}
        ))
    
    async def _aggregate_business_metrics(self):
        """Aggregate business metrics for reporting"""
        current_time = datetime.utcnow()
        
        # Calculate daily active creators
        unique_creators = len(self.creator_metrics)
        
        await self.collect_metric(MetricData(
            metric_name="daily_active_creators",
            metric_type=MetricType.GAUGE,
            value=unique_creators,
            timestamp=current_time
        ))
        
        # Calculate total revenue
        total_revenue = sum(
            data['total_revenue'] for data in self.creator_metrics.values()
        )
        
        await self.collect_metric(MetricData(
            metric_name="total_revenue_generated",
            metric_type=MetricType.GAUGE,
            value=total_revenue,
            timestamp=current_time
        ))
    
    async def _cleanup_old_metrics(self):
        """Cleanup old metrics based on retention policy"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Clean up aggregated metrics
        for metric_name in list(self.aggregated_metrics.keys()):
            self.aggregated_metrics[metric_name] = [
                metric for metric in self.aggregated_metrics[metric_name]
                if metric.timestamp > cutoff_time
            ]
    
    async def _process_alert_conditions(self):
        """Process complex alert conditions that require aggregation"""
        # Calculate error rates
        await self._calculate_error_rates()
        
        # Calculate availability metrics
        await self._calculate_availability_metrics()
    
    async def _calculate_error_rates(self):
        """Calculate error rates for alerting"""
        current_time = datetime.utcnow()
        lookback_time = current_time - timedelta(minutes=5)
        
        # Get recent API request metrics
        api_requests = [
            m for m in self.aggregated_metrics.get('api_requests_total', [])
            if m.timestamp > lookback_time
        ]
        
        api_errors = [
            m for m in self.aggregated_metrics.get('api_errors_total', [])
            if m.timestamp > lookback_time
        ]
        
        if api_requests:
            total_requests = sum(m.value for m in api_requests)
            total_errors = sum(m.value for m in api_errors)
            
            error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0
            
            await self.collect_metric(MetricData(
                metric_name="api_error_rate_percent",
                metric_type=MetricType.PERCENTAGE,
                value=error_rate,
                timestamp=current_time
            ))
    
    async def _calculate_availability_metrics(self):
        """Calculate availability metrics"""
        # In production: calculate based on health check results
        availability = 99.9  # Simulated availability
        
        await self.collect_metric(MetricData(
            metric_name="service_availability_percent",
            metric_type=MetricType.PERCENTAGE,
            value=availability,
            timestamp=datetime.utcnow()
        ))
    
    async def _cleanup_expired_alerts(self):
        """Cleanup expired alerts"""
        current_time = datetime.utcnow()
        
        # Remove old alerts (keep for 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        
        expired_alerts = [
            alert_id for alert_id, alert_data in self.active_alerts.items()
            if datetime.fromisoformat(alert_data['triggered_at']) < cutoff_time
        ]
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
    
    def get_metric_summary(
        self,
        metric_name: str,
        time_range_minutes: int = 60
    ) -> Optional[MetricSummary]:
        """Get aggregated summary for specific metric"""
        if metric_name not in self.aggregated_metrics:
            return None
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        recent_metrics = [
            m for m in self.aggregated_metrics[metric_name]
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return None
        
        values = [m.value for m in recent_metrics]
        
        # Calculate percentiles
        sorted_values = sorted(values)
        p95_index = int(0.95 * len(sorted_values))
        p99_index = int(0.99 * len(sorted_values))
        
        return MetricSummary(
            metric_name=metric_name,
            count=len(values),
            sum_value=sum(values),
            avg_value=statistics.mean(values),
            min_value=min(values),
            max_value=max(values),
            percentile_95=sorted_values[p95_index] if p95_index < len(sorted_values) else max(values),
            percentile_99=sorted_values[p99_index] if p99_index < len(sorted_values) else max(values),
            timestamp_range=(min(m.timestamp for m in recent_metrics),
                           max(m.timestamp for m in recent_metrics)),
            total_revenue_impact=sum(m.revenue_impact or 0 for m in recent_metrics),
            avg_engagement_score=statistics.mean([
                m.user_engagement_score for m in recent_metrics 
                if m.user_engagement_score is not None
            ]) if any(m.user_engagement_score for m in recent_metrics) else 0.0
        )
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics overview"""
        current_time = datetime.utcnow()
        
        # Business metrics
        business_metrics = BusinessMetrics(
            daily_active_creators=len(self.creator_metrics),
            total_content_uploads=sum(
                data['total_uploads'] for data in self.creator_metrics.values()
            ),
            revenue_generated=sum(
                data['total_revenue'] for data in self.creator_metrics.values()
            ),
            platform_api_calls={
                platform: data['api_calls_total']
                for platform, data in self.platform_metrics.items()
            },
            platform_success_rates={
                platform: (data['success_count'] / max(data['api_calls_total'], 1)) * 100
                for platform, data in self.platform_metrics.items()
            }
        )
        
        # Performance metrics
        recent_response_times = [
            m.response_time_ms for m in self.metrics_buffer
            if m.response_time_ms is not None and
               m.timestamp > current_time - timedelta(minutes=5)
        ]
        
        performance_metrics = PerformanceMetrics(
            avg_response_time_ms=statistics.mean(recent_response_times) if recent_response_times else 0.0,
            endpoint_performance={
                endpoint: statistics.mean([
                    m.response_time_ms for m in self.metrics_buffer
                    if m.endpoint == endpoint and m.response_time_ms is not None
                ]) for endpoint in set(m.endpoint for m in self.metrics_buffer if m.endpoint)
            }
        )
        
        return {
            'timestamp': current_time.isoformat(),
            'business_metrics': business_metrics.dict(),
            'performance_metrics': performance_metrics.dict(),
            'creator_metrics': dict(self.creator_metrics),
            'platform_metrics': dict(self.platform_metrics),
            'active_alerts': list(self.active_alerts.values()),
            'total_metrics_collected': len(self.metrics_buffer),
            'metrics_collection_rate': len(self.metrics_buffer) / max(
                (current_time - datetime.utcnow().replace(hour=0, minute=0, second=0)).total_seconds(),
                1
            )
        }


# Ainflue Business Logic Integration Constants
AINFLUE_METRICS_CONFIGURATION = {
    'creator_economy_metrics': {
        'content_metrics': ['uploads', 'views', 'engagement', 'shares'],
        'monetization_metrics': ['revenue', 'conversions', 'cpm', 'ctr'],
        'collaboration_metrics': ['projects', 'partnerships', 'cross_promotion'],
        'ai_usage_metrics': ['enhancement_requests', 'generation_time', 'quality_scores']
    },
    'platform_integration_metrics': {
        'api_performance': ['latency', 'throughput', 'error_rates', 'rate_limits'],
        'content_distribution': ['sync_success', 'format_compatibility', 'delivery_time'],
        'authentication': ['oauth_success', 'token_refresh', 'auth_failures'],
        'data_quality': ['schema_validation', 'data_completeness', 'sync_accuracy']
    },
    'business_intelligence': {
        'kpis': ['dau', 'mau', 'revenue_per_creator', 'platform_adoption'],
        'growth_metrics': ['user_acquisition', 'retention_rate', 'feature_adoption'],
        'operational_metrics': ['system_uptime', 'processing_efficiency', 'cost_per_request']
    }
}

CREATOR_ANALYTICS_PATTERNS = {
    'workflow': 'metric_collection→real_time_analysis→anomaly_detection→business_intelligence→actionable_insights',
    'intelligence_features': {
        'predictive_analytics': 'forecast_creator_performance + platform_optimization',
        'anomaly_detection': 'identify_unusual_patterns + performance_degradation',
        'business_insights': 'revenue_optimization + creator_success_patterns',
        'real_time_monitoring': 'instant_alerting + performance_tracking'
    }
}