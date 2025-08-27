"""
Enterprise Cache Metrics Collector

Comprehensive metrics collection and analysis system specifically designed for
the IA Influencer Agent platform's cache operations with real-time monitoring,
AI-powered analytics, content-aware insights, and business intelligence.

This module provides:
- Real-time performance metrics collection with creator-specific insights
- Advanced analytics and trend analysis for content patterns
- AI-powered anomaly detection and predictive alerting
- Business intelligence dashboards for monetization metrics
- Content-type-specific performance analysis
- Creator behavior analytics and optimization insights
- Revenue-impact monitoring and SLA tracking
- Compliance reporting for data protection regulations

Business Logic Metrics Integration:
- Content creator engagement metrics (upload patterns, content popularity)
- AI processing performance metrics (fingerprinting speed, accuracy)
- Protection system metrics (detection rates, false positives)
- Monetization metrics (revenue tracking, platform performance)
- Collaboration metrics (creator discovery, partnership success rates)
- Multi-platform distribution performance metrics
- Content lifecycle analytics (creation to monetization pipeline)

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 Fahed Mlaiel - All Rights Reserved
License: Proprietary - Unauthorized use strictly prohibited

Key Performance Indicators:
- Content processing time: <30 seconds for audio, <2 minutes for video
- Cache hit ratio: >95% for frequently accessed creator content
- Revenue analytics latency: <5 seconds for real-time insights
- Creator dashboard response time: <2 seconds for all interactions
- AI model inference time: <10 seconds for content analysis
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import numpy as np
import redis.asyncio as redis
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    CollectorRegistry, generate_latest,
    start_http_server, CONTENT_TYPE_LATEST
)
import psutil
import asyncpg
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import aiohttp


class MetricType(Enum):
    """Types of cache metrics for different content operations"""
    COUNTER = "counter"              # Request counts, upload counts
    GAUGE = "gauge"                 # Current values, active users
    HISTOGRAM = "histogram"         # Response times, content sizes
    TIMER = "timer"                 # Processing durations
    RATE = "rate"                   # Operations per second
    BUSINESS_KPI = "business_kpi"   # Revenue, creator growth
    CONTENT_METRIC = "content_metric"  # Content-specific measurements


class AlertSeverity(Enum):
    """Alert severity levels for operational monitoring"""
    INFO = "info"                   # Informational alerts
    WARNING = "warning"             # Performance degradation
    ERROR = "error"                 # System errors
    CRITICAL = "critical"           # Service interruption
    EMERGENCY = "emergency"         # Complete system failure


class ContentCategory(Enum):
    """Content categories for specialized metrics"""
    AUDIO_MUSIC = "audio_music"
    AUDIO_PODCAST = "audio_podcast"
    VIDEO_ENTERTAINMENT = "video_entertainment"
    VIDEO_EDUCATIONAL = "video_educational"
    IMAGE_PHOTOGRAPHY = "image_photography"
    IMAGE_ARTWORK = "image_artwork"
    TEXT_BLOG = "text_blog"
    TEXT_SCRIPT = "text_script"
    METADATA = "metadata"
    ANALYTICS = "analytics"


class CreatorTier(Enum):
    """Creator tier levels for performance tracking"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class MetricDefinition:
    """Definition of a cache metric"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: List[str] = field(default_factory=list)
    content_categories: List[ContentCategory] = field(default_factory=list)
    creator_tiers: List[CreatorTier] = field(default_factory=list)
    business_impact: str = "low"  # low, medium, high, critical
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    metric_name: str
    condition: str  # >, <, ==, !=
    threshold: float
    severity: AlertSeverity
    duration_minutes: int
    description: str
    actions: List[str] = field(default_factory=list)
    content_specific: bool = False
    creator_tier_specific: bool = False


@dataclass
class BusinessMetric:
    """Business intelligence metric"""
    name: str
    value: float
    trend: float  # Percentage change
    target: Optional[float] = None
    category: str = "general"
    impact_level: str = "medium"
    related_metrics: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentAnalytics:
    """Content-specific analytics data"""
    content_id: str
    content_type: str
    creator_id: str
    creator_tier: CreatorTier
    upload_timestamp: datetime
    processing_time_seconds: float
    cache_hits: int
    cache_misses: int
    geographic_distribution: Dict[str, int]
    platform_distribution: Dict[str, int]
    revenue_generated: float
    engagement_score: float
    ai_confidence_score: float


class PrometheusMetricsManager:
    """Prometheus metrics management for enterprise monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        
        # Initialize core metrics
        self._initialize_core_metrics()
        
        # Start Prometheus server
        if config.get("prometheus_enabled", True):
            port = config.get("prometheus_port", 8000)
            start_http_server(port, registry=self.registry)
            logging.info(f"Prometheus metrics server started on port {port}")
    
    def _initialize_core_metrics(self):
        """Initialize core Prometheus metrics"""
        
        # Cache performance metrics
        self.metrics["cache_operations"] = Counter(
            "cache_operations_total",
            "Total cache operations",
            ["operation", "content_type", "creator_tier"],
            registry=self.registry
        )
        
        self.metrics["cache_response_time"] = Histogram(
            "cache_response_time_seconds",
            "Cache response time in seconds",
            ["operation", "content_type"],
            registry=self.registry
        )
        
        self.metrics["cache_hit_ratio"] = Gauge(
            "cache_hit_ratio",
            "Cache hit ratio percentage",
            ["content_type", "creator_tier"],
            registry=self.registry
        )
        
        # Content processing metrics
        self.metrics["content_processing_time"] = Histogram(
            "content_processing_time_seconds",
            "Content processing time in seconds",
            ["content_type", "processing_stage"],
            registry=self.registry
        )
        
        self.metrics["ai_inference_time"] = Histogram(
            "ai_inference_time_seconds",
            "AI model inference time",
            ["model_type", "content_type"],
            registry=self.registry
        )
        
        # Business metrics
        self.metrics["revenue_generated"] = Counter(
            "revenue_generated_total",
            "Total revenue generated",
            ["creator_tier", "content_type", "platform"],
            registry=self.registry
        )
        
        self.metrics["active_creators"] = Gauge(
            "active_creators_total",
            "Number of active creators",
            ["tier", "region"],
            registry=self.registry
        )
        
        # System metrics
        self.metrics["memory_usage"] = Gauge(
            "memory_usage_bytes",
            "Memory usage in bytes",
            ["component"],
            registry=self.registry
        )
        
        self.metrics["cpu_usage"] = Gauge(
            "cpu_usage_percentage",
            "CPU usage percentage",
            ["component"],
            registry=self.registry
        )
        
        # Error metrics
        self.metrics["error_rate"] = Counter(
            "errors_total",
            "Total errors",
            ["error_type", "component", "severity"],
            registry=self.registry
        )
        
        # Quality metrics
        self.metrics["content_quality_score"] = Histogram(
            "content_quality_score",
            "Content quality score from AI analysis",
            ["content_type", "creator_tier"],
            registry=self.registry
        )


class AIAnomalyDetector:
    """AI-powered anomaly detection for cache metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.baseline_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_threshold = config.get("anomaly_threshold", 0.1)
        
        # Initialize anomaly detection models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize anomaly detection models for different metric types"""
        
        model_configs = {
            "performance": {
                "contamination": 0.1,
                "random_state": 42
            },
            "business": {
                "contamination": 0.05,
                "random_state": 42
            },
            "content": {
                "contamination": 0.15,
                "random_state": 42
            }
        }
        
        for model_name, config in model_configs.items():
            self.models[model_name] = IsolationForest(**config)
            self.scalers[model_name] = StandardScaler()
    
    async def detect_anomalies(
        self,
        metrics_data: Dict[str, List[float]],
        metric_category: str = "performance"
    ) -> Dict[str, Any]:
        """Detect anomalies in metrics data"""
        
        try:
            if metric_category not in self.models:
                return {"anomalies_detected": False, "details": []}
            
            model = self.models[metric_category]
            scaler = self.scalers[metric_category]
            
            # Prepare data for anomaly detection
            feature_matrix = self._prepare_feature_matrix(metrics_data)
            
            if len(feature_matrix) < 10:  # Need sufficient data for detection
                return {"anomalies_detected": False, "details": "Insufficient data"}
            
            # Scale features
            scaled_features = scaler.fit_transform(feature_matrix)
            
            # Detect anomalies
            anomaly_predictions = model.fit_predict(scaled_features)
            anomaly_scores = model.decision_function(scaled_features)
            
            # Identify anomalous points
            anomalies = []
            for i, (prediction, score) in enumerate(zip(anomaly_predictions, anomaly_scores)):
                if prediction == -1:  # Anomaly detected
                    anomalies.append({
                        "index": i,
                        "score": float(score),
                        "severity": self._classify_anomaly_severity(score),
                        "metrics": {k: v[i] if i < len(v) else None for k, v in metrics_data.items()}
                    })
            
            return {
                "anomalies_detected": len(anomalies) > 0,
                "anomaly_count": len(anomalies),
                "details": anomalies,
                "model_accuracy": self._calculate_model_accuracy(anomaly_predictions)
            }
            
        except Exception as e:
            logging.error(f"Anomaly detection failed: {e}")
            return {"anomalies_detected": False, "error": str(e)}
    
    def _prepare_feature_matrix(self, metrics_data: Dict[str, List[float]]) -> np.ndarray:
        """Prepare feature matrix for anomaly detection"""
        
        # Ensure all metric lists have the same length
        min_length = min(len(values) for values in metrics_data.values())
        
        feature_matrix = []
        for i in range(min_length):
            features = [values[i] for values in metrics_data.values()]
            feature_matrix.append(features)
        
        return np.array(feature_matrix)
    
    def _classify_anomaly_severity(self, anomaly_score: float) -> str:
        """Classify anomaly severity based on score"""
        
        if anomaly_score < -0.3:
            return "critical"
        elif anomaly_score < -0.2:
            return "high"
        elif anomaly_score < -0.1:
            return "medium"
        else:
            return "low"
    
    def _calculate_model_accuracy(self, predictions: np.ndarray) -> float:
        """Calculate model accuracy (placeholder implementation)"""
        
        # In a real implementation, this would compare against known ground truth
        normal_predictions = np.sum(predictions == 1)
        total_predictions = len(predictions)
        
        return float(normal_predictions / total_predictions) if total_predictions > 0 else 0.0


class BusinessIntelligenceAnalyzer:
    """Business intelligence analyzer for content and revenue metrics"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis_client = redis_client
        self.db_pool = db_pool
        self.kpi_cache_ttl = 300  # 5 minutes
    
    async def calculate_business_kpis(self) -> Dict[str, BusinessMetric]:
        """Calculate key business performance indicators"""
        
        try:
            kpis = {}
            
            # Revenue KPIs
            kpis["total_revenue"] = await self._calculate_revenue_kpi()
            kpis["revenue_per_creator"] = await self._calculate_revenue_per_creator()
            kpis["revenue_growth_rate"] = await self._calculate_revenue_growth()
            
            # Creator KPIs
            kpis["active_creators"] = await self._calculate_active_creators()
            kpis["creator_retention_rate"] = await self._calculate_creator_retention()
            kpis["new_creator_acquisition"] = await self._calculate_new_creators()
            
            # Content KPIs
            kpis["content_upload_rate"] = await self._calculate_content_upload_rate()
            kpis["content_processing_efficiency"] = await self._calculate_processing_efficiency()
            kpis["content_monetization_rate"] = await self._calculate_monetization_rate()
            
            # Platform KPIs
            kpis["platform_performance"] = await self._calculate_platform_performance()
            kpis["user_engagement"] = await self._calculate_user_engagement()
            kpis["system_reliability"] = await self._calculate_system_reliability()
            
            # Cache KPIs for future use
            await self._cache_kpis(kpis)
            
            return kpis
            
        except Exception as e:
            logging.error(f"Business KPI calculation failed: {e}")
            return {}
    
    async def _calculate_revenue_kpi(self) -> BusinessMetric:
        """Calculate total revenue KPI"""
        
        try:
            # Query revenue data from database
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT COALESCE(SUM(amount), 0) as total_revenue
                    FROM revenue_transactions 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                """
                result = await conn.fetchrow(query)
                current_revenue = float(result["total_revenue"])
                
                # Calculate previous day revenue for trend
                prev_query = """
                    SELECT COALESCE(SUM(amount), 0) as prev_revenue
                    FROM revenue_transactions 
                    WHERE created_at >= NOW() - INTERVAL '48 hours'
                    AND created_at < NOW() - INTERVAL '24 hours'
                """
                prev_result = await conn.fetchrow(prev_query)
                previous_revenue = float(prev_result["prev_revenue"])
                
                # Calculate trend
                trend = 0.0
                if previous_revenue > 0:
                    trend = ((current_revenue - previous_revenue) / previous_revenue) * 100
                
                return BusinessMetric(
                    name="total_revenue",
                    value=current_revenue,
                    trend=trend,
                    target=10000.0,  # Daily target
                    category="revenue",
                    impact_level="critical"
                )
                
        except Exception as e:
            logging.error(f"Revenue KPI calculation failed: {e}")
            return BusinessMetric(name="total_revenue", value=0.0, trend=0.0)
    
    async def _calculate_active_creators(self) -> BusinessMetric:
        """Calculate active creators KPI"""
        
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT COUNT(DISTINCT creator_id) as active_creators
                    FROM content_uploads 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                """
                result = await conn.fetchrow(query)
                active_creators = int(result["active_creators"])
                
                return BusinessMetric(
                    name="active_creators",
                    value=float(active_creators),
                    trend=0.0,  # Would calculate trend with historical data
                    target=1000.0,
                    category="creators",
                    impact_level="high"
                )
                
        except Exception as e:
            logging.error(f"Active creators KPI calculation failed: {e}")
            return BusinessMetric(name="active_creators", value=0.0, trend=0.0)
    
    async def _calculate_content_upload_rate(self) -> BusinessMetric:
        """Calculate content upload rate KPI"""
        
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT COUNT(*) as upload_count
                    FROM content_uploads 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """
                result = await conn.fetchrow(query)
                hourly_uploads = int(result["upload_count"])
                
                return BusinessMetric(
                    name="content_upload_rate",
                    value=float(hourly_uploads),
                    trend=0.0,
                    target=500.0,  # Hourly target
                    category="content",
                    impact_level="medium"
                )
                
        except Exception as e:
            logging.error(f"Upload rate KPI calculation failed: {e}")
            return BusinessMetric(name="content_upload_rate", value=0.0, trend=0.0)
    
    async def _calculate_processing_efficiency(self) -> BusinessMetric:
        """Calculate content processing efficiency KPI"""
        
        try:
            # Get processing time statistics from Redis
            processing_times = await self.redis_client.lrange("processing_times", 0, -1)
            
            if processing_times:
                times = [float(t) for t in processing_times]
                avg_processing_time = statistics.mean(times)
                efficiency = max(0, (60 - avg_processing_time) / 60 * 100)  # Target: 60 seconds
                
                return BusinessMetric(
                    name="content_processing_efficiency",
                    value=efficiency,
                    trend=0.0,
                    target=90.0,  # 90% efficiency target
                    category="performance",
                    impact_level="medium"
                )
            
            return BusinessMetric(name="content_processing_efficiency", value=0.0, trend=0.0)
            
        except Exception as e:
            logging.error(f"Processing efficiency KPI calculation failed: {e}")
            return BusinessMetric(name="content_processing_efficiency", value=0.0, trend=0.0)
    
    async def _cache_kpis(self, kpis: Dict[str, BusinessMetric]):
        """Cache KPIs for quick access"""
        
        try:
            for kpi_name, kpi_data in kpis.items():
                cache_key = f"kpi:{kpi_name}"
                kpi_json = json.dumps({
                    "value": kpi_data.value,
                    "trend": kpi_data.trend,
                    "target": kpi_data.target,
                    "timestamp": kpi_data.timestamp.isoformat()
                })
                
                await self.redis_client.setex(cache_key, self.kpi_cache_ttl, kpi_json)
                
        except Exception as e:
            logging.error(f"KPI caching failed: {e}")
    
    # Placeholder methods for other KPIs
    async def _calculate_revenue_per_creator(self) -> BusinessMetric:
        return BusinessMetric(name="revenue_per_creator", value=0.0, trend=0.0)
    
    async def _calculate_revenue_growth(self) -> BusinessMetric:
        return BusinessMetric(name="revenue_growth_rate", value=0.0, trend=0.0)
    
    async def _calculate_creator_retention(self) -> BusinessMetric:
        return BusinessMetric(name="creator_retention_rate", value=0.0, trend=0.0)
    
    async def _calculate_new_creators(self) -> BusinessMetric:
        return BusinessMetric(name="new_creator_acquisition", value=0.0, trend=0.0)
    
    async def _calculate_monetization_rate(self) -> BusinessMetric:
        return BusinessMetric(name="content_monetization_rate", value=0.0, trend=0.0)
    
    async def _calculate_platform_performance(self) -> BusinessMetric:
        return BusinessMetric(name="platform_performance", value=0.0, trend=0.0)
    
    async def _calculate_user_engagement(self) -> BusinessMetric:
        return BusinessMetric(name="user_engagement", value=0.0, trend=0.0)
    
    async def _calculate_system_reliability(self) -> BusinessMetric:
        return BusinessMetric(name="system_reliability", value=0.0, trend=0.0)


class AlertManager:
    """Advanced alerting system for cache and business metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.notification_channels = config.get("notification_channels", [])
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules for critical metrics"""
        
        self.alert_rules = [
            AlertRule(
                metric_name="cache_hit_ratio",
                condition="<",
                threshold=0.85,
                severity=AlertSeverity.WARNING,
                duration_minutes=5,
                description="Cache hit ratio below 85%",
                actions=["optimize_cache", "alert_team"]
            ),
            AlertRule(
                metric_name="response_time",
                condition=">",
                threshold=100.0,  # 100ms
                severity=AlertSeverity.ERROR,
                duration_minutes=2,
                description="Cache response time above 100ms",
                actions=["scale_resources", "alert_team"]
            ),
            AlertRule(
                metric_name="memory_usage",
                condition=">",
                threshold=0.90,
                severity=AlertSeverity.CRITICAL,
                duration_minutes=1,
                description="Memory usage above 90%",
                actions=["emergency_scale", "alert_oncall"]
            ),
            AlertRule(
                metric_name="error_rate",
                condition=">",
                threshold=0.05,
                severity=AlertSeverity.ERROR,
                duration_minutes=3,
                description="Error rate above 5%",
                actions=["investigate_errors", "alert_team"]
            )
        ]
    
    async def evaluate_alerts(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Evaluate current metrics against alert rules"""
        
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if rule.metric_name in current_metrics:
                metric_value = current_metrics[rule.metric_name]
                
                # Evaluate condition
                if self._evaluate_condition(metric_value, rule.condition, rule.threshold):
                    alert_key = f"{rule.metric_name}_{rule.condition}_{rule.threshold}"
                    
                    # Check if alert is already active
                    if alert_key in self.active_alerts:
                        # Update existing alert
                        self.active_alerts[alert_key]["last_seen"] = datetime.utcnow()
                        self.active_alerts[alert_key]["occurrences"] += 1
                    else:
                        # Create new alert
                        alert = {
                            "rule": rule,
                            "metric_value": metric_value,
                            "triggered_at": datetime.utcnow(),
                            "last_seen": datetime.utcnow(),
                            "occurrences": 1,
                            "acknowledged": False
                        }
                        
                        self.active_alerts[alert_key] = alert
                        triggered_alerts.append(alert)
                        
                        # Add to history
                        self.alert_history.append(alert.copy())
                        
                        # Send notifications
                        await self._send_alert_notifications(alert)
                else:
                    # Remove resolved alert
                    alert_key = f"{rule.metric_name}_{rule.condition}_{rule.threshold}"
                    if alert_key in self.active_alerts:
                        resolved_alert = self.active_alerts.pop(alert_key)
                        await self._send_resolution_notification(resolved_alert)
        
        return triggered_alerts
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001
        elif condition == "!=":
            return abs(value - threshold) >= 0.001
        
        return False
    
    async def _send_alert_notifications(self, alert: Dict[str, Any]):
        """Send alert notifications to configured channels"""
        
        try:
            rule = alert["rule"]
            
            notification_message = {
                "severity": rule.severity.value,
                "metric": rule.metric_name,
                "description": rule.description,
                "current_value": alert["metric_value"],
                "threshold": rule.threshold,
                "timestamp": alert["triggered_at"].isoformat(),
                "actions": rule.actions
            }
            
            # Send to each configured channel
            for channel in self.notification_channels:
                if channel["type"] == "webhook":
                    await self._send_webhook_notification(channel["url"], notification_message)
                elif channel["type"] == "email":
                    await self._send_email_notification(channel["address"], notification_message)
                elif channel["type"] == "slack":
                    await self._send_slack_notification(channel["webhook"], notification_message)
            
        except Exception as e:
            logging.error(f"Failed to send alert notifications: {e}")
    
    async def _send_webhook_notification(self, url: str, message: Dict[str, Any]):
        """Send webhook notification"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message) as response:
                    if response.status == 200:
                        logging.info(f"Alert webhook sent successfully to {url}")
                    else:
                        logging.error(f"Webhook notification failed: {response.status}")
                        
        except Exception as e:
            logging.error(f"Webhook notification error: {e}")
    
    async def _send_resolution_notification(self, resolved_alert: Dict[str, Any]):
        """Send alert resolution notification"""
        
        try:
            rule = resolved_alert["rule"]
            
            message = {
                "type": "resolution",
                "metric": rule.metric_name,
                "description": f"Resolved: {rule.description}",
                "resolved_at": datetime.utcnow().isoformat(),
                "duration": (datetime.utcnow() - resolved_alert["triggered_at"]).total_seconds()
            }
            
            for channel in self.notification_channels:
                if channel["type"] == "webhook":
                    await self._send_webhook_notification(channel["url"], message)
            
        except Exception as e:
            logging.error(f"Failed to send resolution notification: {e}")
    
    async def _send_email_notification(self, email: str, message: Dict[str, Any]):
        """Send email notification (placeholder)"""
        logging.info(f"Email notification would be sent to {email}: {message}")
    
    async def _send_slack_notification(self, webhook: str, message: Dict[str, Any]):
        """Send Slack notification (placeholder)"""
        logging.info(f"Slack notification would be sent to {webhook}: {message}")


class CacheMetricsCollector:


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series of metric data points"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=10000))
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    metric_name: str
    condition: str  # e.g., "> 0.95", "< 0.1"
    threshold: float
    duration_seconds: int
    severity: AlertSeverity
    enabled: bool = True
    description: str = ""
    actions: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Active alert instance"""
    alert_id: str
    rule_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    current_value: float
    threshold: float
    status: str = "active"  # active, resolved, suppressed
    metadata: Dict[str, Any] = field(default_factory=dict)


class CacheMetricsCollector:
    """
    Enterprise cache metrics collector with real-time monitoring,
    analytics, and intelligent alerting capabilities.
    """

    def __init__(self, config: CacheConfiguration):
        """
        Initialize cache metrics collector.
        
        Args:
            config: Cache configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self._metrics: Dict[str, MetricSeries] = {}
        self._metric_aggregations: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Alerting system
        self._alert_rules: Dict[str, AlertRule] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: deque = deque(maxlen=1000)
        
        # Performance tracking
        self._collection_stats = {
            "total_metrics_collected": 0,
            "collection_errors": 0,
            "avg_collection_time_ms": 0.0,
            "last_collection_time": None
        }
        
        # Background tasks
        self._collection_task: Optional[asyncio.Task] = None
        self._aggregation_task: Optional[asyncio.Task] = None
        self._alerting_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Initialize default metrics and alert rules
        self._initialize_default_metrics()
        self._initialize_default_alert_rules()

    async def initialize(self) -> None:
        """Initialize the metrics collector"""
        try:
            # Start background tasks
            self._collection_task = asyncio.create_task(self._collection_loop())
            self._aggregation_task = asyncio.create_task(self._aggregation_loop())
            self._alerting_task = asyncio.create_task(self._alerting_loop())
            
            self.logger.info("Cache metrics collector initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing metrics collector: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the metrics collector"""
        try:
            self._shutdown_event.set()
            
            # Stop background tasks
            if self._collection_task:
                self._collection_task.cancel()
            if self._aggregation_task:
                self._aggregation_task.cancel()
            if self._alerting_task:
                self._alerting_task.cancel()
            
            self.logger.info("Cache metrics collector shutdown")
            
        except Exception as e:
            self.logger.error(f"Error shutting down metrics collector: {str(e)}")

    async def record_cache_operation(
        self,
        operation: str,
        content_type: str = "unknown",
        size_bytes: Optional[int] = None,
        processing_time: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Record cache operation metrics.
        
        Args:
            operation: Operation type (read, write, delete, etc.)
            content_type: Type of content
            size_bytes: Size of content in bytes
            processing_time: Processing time in seconds
            success: Whether operation was successful
            error: Error message if operation failed
            **kwargs: Additional metadata
        """
        try:
            labels = {
                "operation": operation,
                "content_type": content_type,
                "success": str(success)
            }
            
            # Record operation count
            await self._record_metric(
                "cache_operations_total",
                1.0,
                labels=labels
            )
            
            # Record operation timing
            if processing_time is not None:
                await self._record_metric(
                    "cache_operation_duration_seconds",
                    processing_time,
                    labels=labels
                )
            
            # Record content size
            if size_bytes is not None:
                await self._record_metric(
                    "cache_content_size_bytes",
                    float(size_bytes),
                    labels=labels
                )
            
            # Record errors
            if not success and error:
                await self._record_metric(
                    "cache_errors_total",
                    1.0,
                    labels={**labels, "error_type": error}
                )
            
        except Exception as e:
            self.logger.error(f"Error recording cache operation metrics: {str(e)}")

    async def record_security_operation(
        self,
        operation: str,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        success: bool = True,
        processing_time: Optional[float] = None,
        security_level: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Record security operation metrics.
        
        Args:
            operation: Security operation type
            user_id: User ID if applicable
            content_id: Content ID if applicable
            success: Whether operation was successful
            processing_time: Processing time in seconds
            security_level: Security level applied
            **kwargs: Additional metadata
        """
        try:
            labels = {
                "operation": operation,
                "success": str(success)
            }
            
            if security_level:
                labels["security_level"] = security_level
            
            # Record security operation count
            await self._record_metric(
                "security_operations_total",
                1.0,
                labels=labels
            )
            
            # Record operation timing
            if processing_time is not None:
                await self._record_metric(
                    "security_operation_duration_seconds",
                    processing_time,
                    labels=labels
                )
            
        except Exception as e:
            self.logger.error(f"Error recording security operation metrics: {str(e)}")

    async def record_distributed_operation(
        self,
        operation: str,
        content_id: str,
        consistency_model: str = "eventual",
        processing_time: Optional[float] = None,
        success: bool = True,
        **kwargs
    ) -> None:
        """
        Record distributed cache operation metrics.
        
        Args:
            operation: Distributed operation type
            content_id: Content identifier
            consistency_model: Consistency model used
            processing_time: Processing time in seconds
            success: Whether operation was successful
            **kwargs: Additional metadata
        """
        try:
            labels = {
                "operation": operation,
                "consistency_model": consistency_model,
                "success": str(success)
            }
            
            # Record distributed operation count
            await self._record_metric(
                "distributed_operations_total",
                1.0,
                labels=labels
            )
            
            # Record operation timing
            if processing_time is not None:
                await self._record_metric(
                    "distributed_operation_duration_seconds",
                    processing_time,
                    labels=labels
                )
            
        except Exception as e:
            self.logger.error(f"Error recording distributed operation metrics: {str(e)}")

    async def record_custom_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
        unit: str = ""
    ) -> None:
        """
        Record custom metric.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Additional labels
            description: Metric description
            unit: Metric unit
        """
        try:
            # Ensure metric exists
            if name not in self._metrics:
                self._metrics[name] = MetricSeries(
                    name=name,
                    metric_type=metric_type,
                    description=description,
                    unit=unit
                )
            
            await self._record_metric(name, value, labels or {})
            
        except Exception as e:
            self.logger.error(f"Error recording custom metric {name}: {str(e)}")

    async def get_metric_value(
        self,
        name: str,
        aggregation: str = "latest",
        time_range_minutes: int = 60,
        labels: Optional[Dict[str, str]] = None
    ) -> Optional[float]:
        """
        Get metric value with specified aggregation.
        
        Args:
            name: Metric name
            aggregation: Aggregation type (latest, avg, min, max, sum)
            time_range_minutes: Time range for aggregation
            labels: Label filters
            
        Returns:
            Metric value or None if not found
        """
        try:
            if name not in self._metrics:
                return None
            
            metric = self._metrics[name]
            cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
            
            # Filter data points by time and labels
            filtered_points = [
                dp for dp in metric.data_points
                if dp.timestamp >= cutoff_time and
                (not labels or all(dp.labels.get(k) == v for k, v in labels.items()))
            ]
            
            if not filtered_points:
                return None
            
            values = [dp.value for dp in filtered_points]
            
            if aggregation == "latest":
                return values[-1]
            elif aggregation == "avg":
                return statistics.mean(values)
            elif aggregation == "min":
                return min(values)
            elif aggregation == "max":
                return max(values)
            elif aggregation == "sum":
                return sum(values)
            else:
                return values[-1]
            
        except Exception as e:
            self.logger.error(f"Error getting metric value for {name}: {str(e)}")
            return None

    async def get_metrics_summary(
        self,
        time_range_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.
        
        Args:
            time_range_minutes: Time range for summary
            
        Returns:
            Dict containing metrics summary
        """
        try:
            summary = {
                "timestamp": datetime.now(),
                "time_range_minutes": time_range_minutes,
                "metrics": {},
                "alerts": {
                    "active_count": len(self._active_alerts),
                    "recent_alerts": len([
                        alert for alert in self._alert_history
                        if alert.triggered_at >= datetime.now() - timedelta(minutes=time_range_minutes)
                    ])
                },
                "collection_stats": self._collection_stats.copy()
            }
            
            # Summarize each metric
            for metric_name, metric in self._metrics.items():
                metric_summary = await self._summarize_metric(metric, time_range_minutes)
                summary["metrics"][metric_name] = metric_summary
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {str(e)}")
            return {}

    async def add_alert_rule(self, alert_rule: AlertRule) -> bool:
        """
        Add custom alert rule.
        
        Args:
            alert_rule: Alert rule to add
            
        Returns:
            bool: True if rule added successfully
        """
        try:
            self._alert_rules[alert_rule.rule_id] = alert_rule
            self.logger.info(f"Added alert rule: {alert_rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding alert rule: {str(e)}")
            return False

    async def remove_alert_rule(self, rule_id: str) -> bool:
        """
        Remove alert rule.
        
        Args:
            rule_id: ID of rule to remove
            
        Returns:
            bool: True if rule removed successfully
        """
        try:
            if rule_id in self._alert_rules:
                del self._alert_rules[rule_id]
                self.logger.info(f"Removed alert rule: {rule_id}")
                return True
            else:
                self.logger.warning(f"Alert rule not found: {rule_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing alert rule: {str(e)}")
            return False

    async def get_active_alerts(self) -> List[Alert]:
        """
        Get list of active alerts.
        
        Returns:
            List of active alerts
        """
        return list(self._active_alerts.values())

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge active alert.
        
        Args:
            alert_id: Alert ID to acknowledge
            
        Returns:
            bool: True if alert acknowledged successfully
        """
        try:
            if alert_id in self._active_alerts:
                self._active_alerts[alert_id].status = "acknowledged"
                self.logger.info(f"Acknowledged alert: {alert_id}")
                return True
            else:
                self.logger.warning(f"Alert not found: {alert_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {str(e)}")
            return False

    # Private helper methods
    
    def _initialize_default_metrics(self) -> None:
        """Initialize default cache metrics"""
        default_metrics = [
            ("cache_operations_total", MetricType.COUNTER, "Total cache operations", "operations"),
            ("cache_operation_duration_seconds", MetricType.HISTOGRAM, "Cache operation duration", "seconds"),
            ("cache_content_size_bytes", MetricType.HISTOGRAM, "Cache content size", "bytes"),
            ("cache_errors_total", MetricType.COUNTER, "Total cache errors", "errors"),
            ("cache_hit_rate", MetricType.GAUGE, "Cache hit rate", "ratio"),
            ("cache_memory_usage_bytes", MetricType.GAUGE, "Cache memory usage", "bytes"),
            ("security_operations_total", MetricType.COUNTER, "Total security operations", "operations"),
            ("security_operation_duration_seconds", MetricType.HISTOGRAM, "Security operation duration", "seconds"),
            ("distributed_operations_total", MetricType.COUNTER, "Total distributed operations", "operations"),
            ("distributed_operation_duration_seconds", MetricType.HISTOGRAM, "Distributed operation duration", "seconds")
        ]
        
        for name, metric_type, description, unit in default_metrics:
            self._metrics[name] = MetricSeries(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit
            )

    def _initialize_default_alert_rules(self) -> None:
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="cache_hit_rate_low",
                name="Low Cache Hit Rate",
                metric_name="cache_hit_rate",
                condition="<",
                threshold=0.9,
                duration_seconds=300,
                severity=AlertSeverity.WARNING,
                description="Cache hit rate is below 90%",
                actions=["log", "email"]
            ),
            AlertRule(
                rule_id="cache_errors_high",
                name="High Cache Error Rate",
                metric_name="cache_errors_total",
                condition=">",
                threshold=10.0,
                duration_seconds=60,
                severity=AlertSeverity.ERROR,
                description="Cache error rate is high",
                actions=["log", "email", "pager"]
            ),
            AlertRule(
                rule_id="memory_usage_high",
                name="High Memory Usage",
                metric_name="cache_memory_usage_bytes",
                condition=">",
                threshold=0.85,  # 85% of max memory
                duration_seconds=300,
                severity=AlertSeverity.WARNING,
                description="Cache memory usage is above 85%",
                actions=["log", "email"]
            )
        ]
        
        for rule in default_rules:
            self._alert_rules[rule.rule_id] = rule

    async def _record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record metric data point"""
        try:
            if name not in self._metrics:
                self._metrics[name] = MetricSeries(
                    name=name,
                    metric_type=MetricType.GAUGE,
                    description="",
                    unit=""
                )
            
            data_point = MetricDataPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {}
            )
            
            self._metrics[name].data_points.append(data_point)
            self._collection_stats["total_metrics_collected"] += 1
            
        except Exception as e:
            self.logger.error(f"Error recording metric {name}: {str(e)}")
            self._collection_stats["collection_errors"] += 1

    async def _collection_loop(self) -> None:
        """Background metric collection loop"""
        while not self._shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Update collection stats
                collection_time = (time.time() - start_time) * 1000
                self._collection_stats["avg_collection_time_ms"] = (
                    (self._collection_stats["avg_collection_time_ms"] + collection_time) / 2
                )
                self._collection_stats["last_collection_time"] = datetime.now()
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in collection loop: {str(e)}")
                await asyncio.sleep(60)

    async def _aggregation_loop(self) -> None:
        """Background metric aggregation loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._compute_aggregations()
                await asyncio.sleep(60)  # Aggregate every minute
                
            except Exception as e:
                self.logger.error(f"Error in aggregation loop: {str(e)}")
                await asyncio.sleep(120)

    async def _alerting_loop(self) -> None:
        """Background alerting loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._check_alert_rules()
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in alerting loop: {str(e)}")
                await asyncio.sleep(60)

    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        # This would integrate with actual system monitoring
        # For now, we'll simulate some metrics
        import psutil
        import random
        
        try:
            # Memory usage
            memory_percent = psutil.virtual_memory().percent
            await self._record_metric("system_memory_usage_percent", memory_percent)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            await self._record_metric("system_cpu_usage_percent", cpu_percent)
            
            # Simulate cache-specific metrics
            await self._record_metric("cache_hit_rate", random.uniform(0.85, 0.98))
            await self._record_metric("cache_memory_usage_bytes", random.uniform(1e9, 5e9))
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")

    async def _compute_aggregations(self) -> None:
        """Compute metric aggregations"""
        try:
            for metric_name, metric in self._metrics.items():
                if not metric.data_points:
                    continue
                
                # Compute aggregations for last hour
                cutoff_time = datetime.now() - timedelta(hours=1)
                recent_points = [
                    dp for dp in metric.data_points
                    if dp.timestamp >= cutoff_time
                ]
                
                if recent_points:
                    values = [dp.value for dp in recent_points]
                    self._metric_aggregations[metric_name] = {
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
                    
                    if len(values) > 1:
                        self._metric_aggregations[metric_name]["stddev"] = statistics.stdev(values)
            
        except Exception as e:
            self.logger.error(f"Error computing aggregations: {str(e)}")

    async def _check_alert_rules(self) -> None:
        """Check alert rules and trigger alerts"""
        try:
            for rule in self._alert_rules.values():
                if not rule.enabled:
                    continue
                
                # Get current metric value
                current_value = await self.get_metric_value(
                    rule.metric_name,
                    aggregation="avg",
                    time_range_minutes=rule.duration_seconds // 60
                )
                
                if current_value is None:
                    continue
                
                # Check condition
                should_alert = False
                if rule.condition == ">" and current_value > rule.threshold:
                    should_alert = True
                elif rule.condition == "<" and current_value < rule.threshold:
                    should_alert = True
                elif rule.condition == "==" and abs(current_value - rule.threshold) < 0.001:
                    should_alert = True
                
                # Handle alert
                if should_alert:
                    await self._trigger_alert(rule, current_value)
                else:
                    await self._resolve_alert(rule.rule_id)
            
        except Exception as e:
            self.logger.error(f"Error checking alert rules: {str(e)}")

    async def _trigger_alert(self, rule: AlertRule, current_value: float) -> None:
        """Trigger alert for rule"""
        try:
            alert_id = f"{rule.rule_id}_{int(time.time())}"
            
            # Check if alert already exists
            existing_alert = None
            for alert in self._active_alerts.values():
                if alert.rule_id == rule.rule_id and alert.status == "active":
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.current_value = current_value
                return
            
            # Create new alert
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                metric_name=rule.metric_name,
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric_name} = {current_value:.3f} (threshold: {rule.threshold})",
                triggered_at=datetime.now(),
                current_value=current_value,
                threshold=rule.threshold
            )
            
            self._active_alerts[alert_id] = alert
            self._alert_history.append(alert)
            
            # Execute alert actions
            await self._execute_alert_actions(alert, rule.actions)
            
            self.logger.warning(f"Alert triggered: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")

    async def _resolve_alert(self, rule_id: str) -> None:
        """Resolve active alert for rule"""
        try:
            alerts_to_resolve = [
                alert for alert in self._active_alerts.values()
                if alert.rule_id == rule_id and alert.status == "active"
            ]
            
            for alert in alerts_to_resolve:
                alert.status = "resolved"
                self.logger.info(f"Alert resolved: {alert.message}")
                
                # Remove from active alerts
                if alert.alert_id in self._active_alerts:
                    del self._active_alerts[alert.alert_id]
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")

    async def _execute_alert_actions(self, alert: Alert, actions: List[str]) -> None:
        """Execute alert actions"""
        try:
            for action in actions:
                if action == "log":
                    self.logger.warning(f"ALERT: {alert.message}")
                elif action == "email":
                    # Would send email notification
                    self.logger.info(f"Would send email for alert: {alert.alert_id}")
                elif action == "pager":
                    # Would send pager notification
                    self.logger.warning(f"Would page for critical alert: {alert.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing alert actions: {str(e)}")

    async def _summarize_metric(
        self,
        metric: MetricSeries,
        time_range_minutes: int
    ) -> Dict[str, Any]:
        """Summarize metric for the given time range"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
            recent_points = [
                dp for dp in metric.data_points
                if dp.timestamp >= cutoff_time
            ]
            
            if not recent_points:
                return {
                    "name": metric.name,
                    "type": metric.metric_type.value,
                    "description": metric.description,
                    "unit": metric.unit,
                    "data_points": 0,
                    "value": None
                }
            
            values = [dp.value for dp in recent_points]
            
            summary = {
                "name": metric.name,
                "type": metric.metric_type.value,
                "description": metric.description,
                "unit": metric.unit,
                "data_points": len(recent_points),
                "latest_value": values[-1],
                "avg_value": statistics.mean(values),
                "min_value": min(values),
                "max_value": max(values)
            }
            
            if len(values) > 1:
                summary["stddev"] = statistics.stdev(values)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing metric {metric.name}: {str(e)}")
            return {}
