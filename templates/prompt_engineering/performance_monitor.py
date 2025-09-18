"""
🎯 Performance Monitor - Real-Time Performance Tracking System
============================================================

Enterprise-grade performance monitoring for AI prompts with real-time metrics,
anomaly detection, and creator economy optimization tracking.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Expert + Backend Senior + ML Engineer
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from pydantic import BaseModel, Field
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

from core.config import get_settings
from utils.exceptions import MonitoringError, ValidationError
from monitoring.prompt_metrics import PromptMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class MetricType(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    SUCCESS_RATE = "success_rate"
    COST = "cost"
    TOKEN_USAGE = "token_usage"
    ERROR_RATE = "error_rate"
    QUALITY_SCORE = "quality_score"
    CREATOR_SATISFACTION = "creator_satisfaction"
    REVENUE_IMPACT = "revenue_impact"
    COLLABORATION_SCORE = "collaboration_score"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PerformanceThreshold(Enum):
    """Performance threshold levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    template_id: str
    model_name: str
    creator_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    threshold_status: PerformanceThreshold = PerformanceThreshold.AVERAGE


@dataclass
class PerformanceAlert:
    """Performance alert structure"""
    alert_id: str
    severity: AlertSeverity
    metric_type: MetricType
    message: str
    template_id: str
    model_name: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    action_taken: Optional[str] = None


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    report_id: str
    generated_at: datetime
    time_range: Tuple[datetime, datetime]
    total_requests: int
    avg_latency_ms: float
    success_rate: float
    avg_cost: float
    error_count: int
    top_performing_templates: List[str]
    underperforming_templates: List[str]
    creator_economy_metrics: Dict[str, float]
    recommendations: List[str]
    anomalies_detected: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]


class PerformanceMonitorConfig(BaseModel):
    """Performance monitoring configuration"""
    latency_threshold_ms: float = Field(default=5000, ge=100, le=30000)
    error_rate_threshold: float = Field(default=0.05, ge=0.0, le=1.0)
    cost_threshold_daily: float = Field(default=100.0, ge=0.0)
    quality_score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    monitoring_interval_seconds: int = Field(default=60, ge=10, le=3600)
    alert_cooldown_minutes: int = Field(default=15, ge=1, le=1440)
    enable_anomaly_detection: bool = True
    enable_real_time_alerts: bool = True
    enable_trend_analysis: bool = True
    retention_days: int = Field(default=90, ge=1, le=365)
    creator_economy_weight: float = Field(default=0.3, ge=0.0, le=1.0)


class PerformanceMonitor:
    """
    🎯 Enterprise Performance Monitoring System
    
    Real-time performance tracking with:
    - Multi-dimensional metrics collection
    - Intelligent anomaly detection
    - Creator economy performance optimization
    - Real-time alerting and notifications
    - Comprehensive performance reporting
    - Prometheus metrics integration
    """
    
    def __init__(self, config: Optional[PerformanceMonitorConfig] = None):
        self.config = config or PerformanceMonitorConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.metrics_collector = PromptMetricsCollector()
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        self._active_alerts: Dict[str, PerformanceAlert] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics"""
        self.latency_histogram = Histogram(
            'prompt_latency_seconds',
            'Prompt processing latency',
            ['template_id', 'model_name', 'creator_type'],
            registry=self.registry
        )
        
        self.request_counter = Counter(
            'prompt_requests_total',
            'Total prompt requests',
            ['template_id', 'model_name', 'status'],
            registry=self.registry
        )
        
        self.cost_gauge = Gauge(
            'prompt_cost_total',
            'Total prompt processing cost',
            ['template_id', 'model_name'],
            registry=self.registry
        )
        
        self.quality_gauge = Gauge(
            'prompt_quality_score',
            'Prompt quality score',
            ['template_id', 'model_name'],
            registry=self.registry
        )
        
        self.creator_satisfaction_gauge = Gauge(
            'creator_satisfaction_score',
            'Creator satisfaction score',
            ['creator_type', 'content_category'],
            registry=self.registry
        )
    
    async def initialize(self) -> None:
        """Initialize performance monitoring system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Initialize MongoDB connection
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Create database tables
            await self._create_tables()
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self._initialized = True
            logger.info("Performance Monitor initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Performance Monitor: {e}")
            raise MonitoringError(f"Performance Monitor initialization failed: {e}")
    
    async def _create_tables(self) -> None:
        """Create database tables for performance data"""
        create_metrics_table = """
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id SERIAL PRIMARY KEY,
            metric_type VARCHAR(50) NOT NULL,
            value FLOAT NOT NULL,
            template_id VARCHAR(255),
            model_name VARCHAR(255),
            creator_context JSONB,
            metadata JSONB,
            threshold_status VARCHAR(50),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (template_id, recorded_at),
            INDEX (model_name, recorded_at),
            INDEX (metric_type, recorded_at)
        );
        """
        
        create_alerts_table = """
        CREATE TABLE IF NOT EXISTS performance_alerts (
            id SERIAL PRIMARY KEY,
            alert_id VARCHAR(255) UNIQUE NOT NULL,
            severity VARCHAR(20) NOT NULL,
            metric_type VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            template_id VARCHAR(255),
            model_name VARCHAR(255),
            threshold_value FLOAT,
            actual_value FLOAT,
            resolved BOOLEAN DEFAULT FALSE,
            resolution_time TIMESTAMP,
            action_taken TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_reports_table = """
        CREATE TABLE IF NOT EXISTS performance_reports (
            id SERIAL PRIMARY KEY,
            report_id VARCHAR(255) UNIQUE NOT NULL,
            report_data JSONB NOT NULL,
            time_range_start TIMESTAMP NOT NULL,
            time_range_end TIMESTAMP NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_metrics_table)
            await conn.execute(create_alerts_table)
            await conn.execute(create_reports_table)
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        template_id: str,
        model_name: str,
        creator_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric"""
        try:
            # Create metric object
            metric = PerformanceMetric(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                template_id=template_id,
                model_name=model_name,
                creator_context=creator_context or {},
                metadata=metadata or {},
                threshold_status=self._calculate_threshold_status(metric_type, value)
            )
            
            # Store in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO performance_metrics 
                    (metric_type, value, template_id, model_name, creator_context, 
                     metadata, threshold_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, metric_type.value, value, template_id, model_name,
                    json.dumps(creator_context or {}), json.dumps(metadata or {}),
                    metric.threshold_status.value)
            
            # Update Prometheus metrics
            await self._update_prometheus_metrics(metric)
            
            # Cache recent metrics in Redis
            await self._cache_metric(metric)
            
            # Check thresholds for alerting
            await self._check_alert_thresholds(metric)
            
            logger.debug(f"Recorded metric {metric_type.value}: {value}")
        
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def _calculate_threshold_status(self, metric_type: MetricType, value: float) -> PerformanceThreshold:
        """Calculate threshold status based on metric type and value"""
        if metric_type == MetricType.LATENCY:
            if value < 1000:  # < 1 second
                return PerformanceThreshold.EXCELLENT
            elif value < 3000:  # < 3 seconds
                return PerformanceThreshold.GOOD
            elif value < 5000:  # < 5 seconds
                return PerformanceThreshold.AVERAGE
            elif value < 10000:  # < 10 seconds
                return PerformanceThreshold.POOR
            else:
                return PerformanceThreshold.CRITICAL
        
        elif metric_type == MetricType.SUCCESS_RATE:
            if value >= 0.98:
                return PerformanceThreshold.EXCELLENT
            elif value >= 0.95:
                return PerformanceThreshold.GOOD
            elif value >= 0.90:
                return PerformanceThreshold.AVERAGE
            elif value >= 0.80:
                return PerformanceThreshold.POOR
            else:
                return PerformanceThreshold.CRITICAL
        
        elif metric_type == MetricType.QUALITY_SCORE:
            if value >= 0.90:
                return PerformanceThreshold.EXCELLENT
            elif value >= 0.80:
                return PerformanceThreshold.GOOD
            elif value >= 0.70:
                return PerformanceThreshold.AVERAGE
            elif value >= 0.60:
                return PerformanceThreshold.POOR
            else:
                return PerformanceThreshold.CRITICAL
        
        elif metric_type == MetricType.COST:
            # Lower cost is better
            if value < 0.01:
                return PerformanceThreshold.EXCELLENT
            elif value < 0.05:
                return PerformanceThreshold.GOOD
            elif value < 0.10:
                return PerformanceThreshold.AVERAGE
            elif value < 0.20:
                return PerformanceThreshold.POOR
            else:
                return PerformanceThreshold.CRITICAL
        
        else:
            return PerformanceThreshold.AVERAGE
    
    async def _update_prometheus_metrics(self, metric: PerformanceMetric) -> None:
        """Update Prometheus metrics"""
        try:
            creator_type = metric.creator_context.get('creator_type', 'unknown')
            
            if metric.metric_type == MetricType.LATENCY:
                self.latency_histogram.labels(
                    template_id=metric.template_id,
                    model_name=metric.model_name,
                    creator_type=creator_type
                ).observe(metric.value / 1000)  # Convert to seconds
            
            elif metric.metric_type == MetricType.COST:
                self.cost_gauge.labels(
                    template_id=metric.template_id,
                    model_name=metric.model_name
                ).set(metric.value)
            
            elif metric.metric_type == MetricType.QUALITY_SCORE:
                self.quality_gauge.labels(
                    template_id=metric.template_id,
                    model_name=metric.model_name
                ).set(metric.value)
            
            elif metric.metric_type == MetricType.CREATOR_SATISFACTION:
                content_category = metric.creator_context.get('content_category', 'general')
                self.creator_satisfaction_gauge.labels(
                    creator_type=creator_type,
                    content_category=content_category
                ).set(metric.value)
            
            # Always update request counter
            status = "success" if metric.threshold_status != PerformanceThreshold.CRITICAL else "error"
            self.request_counter.labels(
                template_id=metric.template_id,
                model_name=metric.model_name,
                status=status
            ).inc()
        
        except Exception as e:
            logger.warning(f"Failed to update Prometheus metrics: {e}")
    
    async def _cache_metric(self, metric: PerformanceMetric) -> None:
        """Cache recent metrics in Redis for fast access"""
        try:
            # Cache key for recent metrics
            cache_key = f"metrics:{metric.template_id}:{metric.model_name}:{metric.metric_type.value}"
            
            # Store metric with TTL
            metric_data = {
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "threshold_status": metric.threshold_status.value
            }
            
            await self.redis_client.lpush(cache_key, json.dumps(metric_data))
            await self.redis_client.ltrim(cache_key, 0, 99)  # Keep last 100 metrics
            await self.redis_client.expire(cache_key, 3600)  # 1 hour TTL
        
        except Exception as e:
            logger.warning(f"Failed to cache metric: {e}")
    
    async def _check_alert_thresholds(self, metric: PerformanceMetric) -> None:
        """Check if metric exceeds alert thresholds"""
        try:
            alert_needed = False
            alert_message = ""
            severity = AlertSeverity.INFO
            
            if metric.metric_type == MetricType.LATENCY:
                if metric.value > self.config.latency_threshold_ms:
                    alert_needed = True
                    severity = AlertSeverity.WARNING if metric.value < self.config.latency_threshold_ms * 2 else AlertSeverity.ERROR
                    alert_message = f"High latency detected: {metric.value}ms (threshold: {self.config.latency_threshold_ms}ms)"
            
            elif metric.metric_type == MetricType.ERROR_RATE:
                if metric.value > self.config.error_rate_threshold:
                    alert_needed = True
                    severity = AlertSeverity.ERROR if metric.value > self.config.error_rate_threshold * 2 else AlertSeverity.WARNING
                    alert_message = f"High error rate detected: {metric.value:.2%} (threshold: {self.config.error_rate_threshold:.2%})"
            
            elif metric.metric_type == MetricType.QUALITY_SCORE:
                if metric.value < self.config.quality_score_threshold:
                    alert_needed = True
                    severity = AlertSeverity.WARNING
                    alert_message = f"Low quality score detected: {metric.value:.2f} (threshold: {self.config.quality_score_threshold:.2f})"
            
            if alert_needed and self.config.enable_real_time_alerts:
                await self._create_alert(
                    severity=severity,
                    metric_type=metric.metric_type,
                    message=alert_message,
                    template_id=metric.template_id,
                    model_name=metric.model_name,
                    threshold_value=self._get_threshold_value(metric.metric_type),
                    actual_value=metric.value
                )
        
        except Exception as e:
            logger.error(f"Failed to check alert thresholds: {e}")
    
    def _get_threshold_value(self, metric_type: MetricType) -> float:
        """Get threshold value for metric type"""
        thresholds = {
            MetricType.LATENCY: self.config.latency_threshold_ms,
            MetricType.ERROR_RATE: self.config.error_rate_threshold,
            MetricType.QUALITY_SCORE: self.config.quality_score_threshold
        }
        return thresholds.get(metric_type, 0.0)
    
    async def _create_alert(
        self,
        severity: AlertSeverity,
        metric_type: MetricType,
        message: str,
        template_id: str,
        model_name: str,
        threshold_value: float,
        actual_value: float
    ) -> None:
        """Create a performance alert"""
        try:
            alert_id = f"alert_{int(time.time())}_{template_id}_{metric_type.value}"
            
            # Check if similar alert exists recently (cooldown)
            recent_alert_key = f"alert_cooldown:{template_id}:{metric_type.value}"
            if await self.redis_client.exists(recent_alert_key):
                return  # Skip alert due to cooldown
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                metric_type=metric_type,
                message=message,
                template_id=template_id,
                model_name=model_name,
                threshold_value=threshold_value,
                actual_value=actual_value,
                timestamp=datetime.utcnow()
            )
            
            # Store alert in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO performance_alerts 
                    (alert_id, severity, metric_type, message, template_id, 
                     model_name, threshold_value, actual_value)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, alert.alert_id, alert.severity.value, alert.metric_type.value,
                    alert.message, alert.template_id, alert.model_name,
                    alert.threshold_value, alert.actual_value)
            
            # Cache alert
            self._active_alerts[alert_id] = alert
            
            # Set cooldown
            await self.redis_client.setex(
                recent_alert_key,
                self.config.alert_cooldown_minutes * 60,
                "1"
            )
            
            # Send notification (if configured)
            await self._send_alert_notification(alert)
            
            logger.warning(f"Created alert {alert_id}: {message}")
        
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def _send_alert_notification(self, alert: PerformanceAlert) -> None:
        """Send alert notification (placeholder for integration)"""
        # This would integrate with notification systems like:
        # - Slack webhooks
        # - Email notifications
        # - Discord notifications
        # - PagerDuty alerts
        # - Microsoft Teams
        logger.info(f"Alert notification: {alert.severity.value} - {alert.message}")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for continuous performance tracking"""
        try:
            while True:
                await asyncio.sleep(self.config.monitoring_interval_seconds)
                
                if not self._initialized:
                    continue
                
                try:
                    # Perform anomaly detection
                    if self.config.enable_anomaly_detection:
                        await self._detect_anomalies()
                    
                    # Clean old data
                    await self._cleanup_old_data()
                    
                    # Update performance summaries
                    await self._update_performance_summaries()
                
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop failed: {e}")
    
    async def _detect_anomalies(self) -> None:
        """Detect performance anomalies using machine learning"""
        try:
            # Get recent metrics for analysis
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT metric_type, value, template_id, model_name, recorded_at
                    FROM performance_metrics 
                    WHERE recorded_at >= $1
                    ORDER BY recorded_at
                """, cutoff_time)
            
            if len(rows) < 50:  # Need minimum data for anomaly detection
                return
            
            # Group by metric type for analysis
            metrics_by_type = {}
            for row in rows:
                metric_type = row['metric_type']
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = []
                metrics_by_type[metric_type].append({
                    'value': row['value'],
                    'template_id': row['template_id'],
                    'model_name': row['model_name'],
                    'timestamp': row['recorded_at']
                })
            
            # Run anomaly detection for each metric type
            for metric_type, data in metrics_by_type.items():
                if len(data) < 20:  # Minimum data points
                    continue
                
                values = np.array([d['value'] for d in data]).reshape(-1, 1)
                
                # Use Isolation Forest for anomaly detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomalies = iso_forest.fit_predict(values)
                
                # Process detected anomalies
                for i, is_anomaly in enumerate(anomalies):
                    if is_anomaly == -1:  # Anomaly detected
                        anomaly_data = data[i]
                        await self._handle_anomaly(metric_type, anomaly_data)
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
    
    async def _handle_anomaly(self, metric_type: str, anomaly_data: Dict[str, Any]) -> None:
        """Handle detected performance anomaly"""
        try:
            message = f"Performance anomaly detected in {metric_type}: {anomaly_data['value']}"
            
            await self._create_alert(
                severity=AlertSeverity.WARNING,
                metric_type=MetricType(metric_type),
                message=message,
                template_id=anomaly_data['template_id'],
                model_name=anomaly_data['model_name'],
                threshold_value=0.0,
                actual_value=anomaly_data['value']
            )
        
        except Exception as e:
            logger.error(f"Failed to handle anomaly: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old performance data based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
            
            async with self.db_pool.acquire() as conn:
                # Clean old metrics
                await conn.execute("""
                    DELETE FROM performance_metrics WHERE recorded_at < $1
                """, cutoff_date)
                
                # Clean resolved alerts older than 30 days
                alert_cutoff = datetime.utcnow() - timedelta(days=30)
                await conn.execute("""
                    DELETE FROM performance_alerts 
                    WHERE resolved = true AND resolution_time < $1
                """, alert_cutoff)
            
            logger.debug("Cleaned up old performance data")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def _update_performance_summaries(self) -> None:
        """Update performance summary statistics"""
        try:
            # This would update summary tables or cache aggregated metrics
            # for faster dashboard queries
            current_time = datetime.utcnow()
            summary_key = f"performance_summary:{current_time.strftime('%Y%m%d%H')}"
            
            # Calculate hourly summaries and cache them
            async with self.db_pool.acquire() as conn:
                summary_data = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_requests,
                        AVG(CASE WHEN metric_type = 'latency' THEN value END) as avg_latency,
                        AVG(CASE WHEN metric_type = 'cost' THEN value END) as avg_cost,
                        AVG(CASE WHEN metric_type = 'quality_score' THEN value END) as avg_quality
                    FROM performance_metrics 
                    WHERE recorded_at >= $1
                """, current_time - timedelta(hours=1))
                
                if summary_data and summary_data['total_requests']:
                    await self.redis_client.setex(
                        summary_key,
                        7200,  # 2 hours TTL
                        json.dumps(dict(summary_data))
                    )
        
        except Exception as e:
            logger.error(f"Failed to update performance summaries: {e}")
    
    async def generate_performance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        template_ids: Optional[List[str]] = None
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            # Generate report ID
            report_id = f"report_{int(time.time())}"
            
            # Query performance data
            conditions = ["recorded_at BETWEEN $1 AND $2"]
            params = [start_time, end_time]
            
            if template_ids:
                conditions.append(f"template_id = ANY(${len(params) + 1})")
                params.append(template_ids)
            
            query = f"""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(CASE WHEN metric_type = 'latency' THEN value END) as avg_latency,
                    AVG(CASE WHEN metric_type = 'success_rate' THEN value END) as success_rate,
                    AVG(CASE WHEN metric_type = 'cost' THEN value END) as avg_cost,
                    COUNT(CASE WHEN threshold_status = 'critical' THEN 1 END) as error_count,
                    template_id,
                    model_name
                FROM performance_metrics 
                WHERE {' AND '.join(conditions)}
                GROUP BY template_id, model_name
                ORDER BY total_requests DESC
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
            
            # Process results
            total_requests = sum(row['total_requests'] for row in rows)
            avg_latency = statistics.mean(row['avg_latency'] for row in rows if row['avg_latency'])
            success_rate = statistics.mean(row['success_rate'] for row in rows if row['success_rate'])
            avg_cost = statistics.mean(row['avg_cost'] for row in rows if row['avg_cost'])
            error_count = sum(row['error_count'] for row in rows)
            
            # Identify top and underperforming templates
            top_performing = [row['template_id'] for row in rows[:5]]
            underperforming = [row['template_id'] for row in rows if row['success_rate'] and row['success_rate'] < 0.8]
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(rows)
            
            report = PerformanceReport(
                report_id=report_id,
                generated_at=datetime.utcnow(),
                time_range=(start_time, end_time),
                total_requests=total_requests,
                avg_latency_ms=avg_latency,
                success_rate=success_rate,
                avg_cost=avg_cost,
                error_count=error_count,
                top_performing_templates=top_performing,
                underperforming_templates=underperforming,
                creator_economy_metrics={},  # Would be populated from creator-specific metrics
                recommendations=recommendations,
                anomalies_detected=[],  # Would be populated from anomaly detection
                trend_analysis={}  # Would be populated from trend analysis
            )
            
            # Store report
            await self._store_report(report)
            
            return report
        
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise MonitoringError(f"Report generation failed: {e}")
    
    async def _generate_recommendations(self, performance_data: List[Dict]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Analyze performance patterns
        high_latency_templates = [
            row['template_id'] for row in performance_data 
            if row['avg_latency'] and row['avg_latency'] > self.config.latency_threshold_ms
        ]
        
        if high_latency_templates:
            recommendations.append(
                f"Consider optimizing templates with high latency: {', '.join(high_latency_templates[:3])}"
            )
        
        high_cost_templates = [
            row['template_id'] for row in performance_data
            if row['avg_cost'] and row['avg_cost'] > 0.1
        ]
        
        if high_cost_templates:
            recommendations.append(
                f"Review cost optimization for expensive templates: {', '.join(high_cost_templates[:3])}"
            )
        
        low_success_rate = [
            row['template_id'] for row in performance_data
            if row['success_rate'] and row['success_rate'] < 0.9
        ]
        
        if low_success_rate:
            recommendations.append(
                f"Investigate reliability issues in templates: {', '.join(low_success_rate[:3])}"
            )
        
        return recommendations
    
    async def _store_report(self, report: PerformanceReport) -> None:
        """Store performance report in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO performance_reports 
                    (report_id, report_data, time_range_start, time_range_end)
                    VALUES ($1, $2, $3, $4)
                """, report.report_id, json.dumps(report.__dict__, default=str),
                    report.time_range[0], report.time_range[1])
        
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
    
    async def get_real_time_metrics(self, template_id: str) -> Dict[str, Any]:
        """Get real-time metrics for a template"""
        try:
            metrics = {}
            
            # Get cached metrics from Redis
            for metric_type in MetricType:
                cache_key = f"metrics:{template_id}:*:{metric_type.value}"
                keys = await self.redis_client.keys(cache_key)
                
                if keys:
                    recent_values = []
                    for key in keys:
                        values = await self.redis_client.lrange(key, 0, 9)  # Last 10 values
                        for value_json in values:
                            try:
                                value_data = json.loads(value_json)
                                recent_values.append(value_data['value'])
                            except:
                                continue
                    
                    if recent_values:
                        metrics[metric_type.value] = {
                            'current': recent_values[0] if recent_values else 0,
                            'average': statistics.mean(recent_values),
                            'trend': 'improving' if len(recent_values) > 1 and recent_values[0] > recent_values[-1] else 'stable'
                        }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}
    
    async def get_creator_economy_metrics(self, creator_type: str) -> Dict[str, Any]:
        """Get creator economy specific metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        AVG(CASE WHEN metric_type = 'creator_satisfaction' THEN value END) as avg_satisfaction,
                        AVG(CASE WHEN metric_type = 'revenue_impact' THEN value END) as avg_revenue_impact,
                        AVG(CASE WHEN metric_type = 'collaboration_score' THEN value END) as avg_collaboration,
                        COUNT(*) as total_interactions
                    FROM performance_metrics 
                    WHERE creator_context->>'creator_type' = $1
                    AND recorded_at >= NOW() - INTERVAL '7 days'
                """, creator_type)
                
                return dict(row) if row else {}
        
        except Exception as e:
            logger.error(f"Failed to get creator economy metrics: {e}")
            return {}
    
    async def cleanup(self) -> None:
        """Cleanup performance monitor resources"""
        try:
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            if self.mongo_client:
                self.mongo_client.close()
            
            logger.info("Performance Monitor cleanup completed")
        
        except Exception as e:
            logger.error(f"Performance Monitor cleanup failed: {e}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()