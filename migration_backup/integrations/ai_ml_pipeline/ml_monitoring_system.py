"""📊 Enterprise ML Monitoring System - Ainflue AI/ML Pipeline
============================================================

Production ML monitoring with drift detection, performance tracking,
and real-time alerting for 53 AI agents serving global creators.

Expert Implementation:
📊 ML Engineer: Model performance monitoring + drift detection + metrics
🤖 Lead Dev IA: Monitoring orchestration + alerting workflows
🏗️ Backend Senior: Distributed monitoring + data collection + storage
⚙️ DevOps: Infrastructure monitoring + alerting + dashboard automation
🔒 Security: Monitoring security + anomaly detection + audit trails
🗄️ DBA: Metrics storage + time-series optimization + data retention
🔗 Microservices: Service monitoring + distributed tracing + observability

Author: Fahed Mlaiel (mlaiel@live.de)
Date: December 2025
Version: Enterprise 1.0

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import uuid
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from scipy import stats
import aiohttp
import psutil
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import websockets
import json as json_lib

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type classification"""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    DRIFT = "drift"
    RESOURCE_USAGE = "resource_usage"
    BUSINESS = "business"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DriftType(Enum):
    """Data drift types"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    FEATURE_DRIFT = "feature_drift"
    PREDICTION_DRIFT = "prediction_drift"


@dataclass
class MetricDefinition:
    """Metric definition container"""
    metric_id: str
    name: str
    metric_type: MetricType
    model_id: str
    description: str
    calculation_method: str
    thresholds: Dict[str, float]
    collection_interval_seconds: int
    retention_days: int
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Metric value container"""
    metric_id: str
    model_id: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert container"""
    alert_id: str
    metric_id: str
    model_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    creator_id: Optional[str] = None
    platform_context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftDetectionResult:
    """Data drift detection result"""
    drift_id: str
    model_id: str
    drift_type: DriftType
    feature_name: str
    drift_score: float
    threshold: float
    is_drift_detected: bool
    statistical_test: str
    p_value: float
    detected_at: datetime
    reference_period: tuple[datetime, datetime]
    current_period: tuple[datetime, datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnterpriseMLMonitoringSystem:
    """Enterprise ML monitoring with drift detection and alerting"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ML monitoring system"""
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.metrics_registry = {}
        self.alert_rules = {}
        self.drift_detectors = {}
        self.prometheus_metrics = {}
        self.alert_channels = {}
        self.executor = ThreadPoolExecutor(max_workers=30)
        
        # Monitoring configuration
        self.monitoring_config = {
            'metrics_collection_interval': 60,  # seconds
            'drift_detection_interval': 300,  # 5 minutes
            'alert_evaluation_interval': 30,  # seconds
            'metrics_retention_days': 90,
            'alert_retention_days': 365,
            'drift_detection_window_hours': 24,
            'reference_window_days': 7,
            'batch_size': 1000,
            'max_concurrent_monitors': 50
        }
        
        # Creator economy monitoring
        self.creator_monitoring_config = {
            'content_model_priority': 9,
            'monetization_model_priority': 10,  # Highest monitoring priority
            'platform_optimization_priority': 8,
            'seo_model_priority': 7,
            'collaboration_model_priority': 6,
            'creator_specific_dashboards': True,
            'platform_specific_metrics': True,
            'business_impact_tracking': True,
            'real_time_creator_alerts': True
        }
        
        # Initialize Prometheus metrics
        self._initialize_prometheus_metrics()
    
    async def initialize(self):
        """Initialize monitoring system connections and setup"""
        try:
            # Initialize database connection
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=10,
                max_size=30,
                command_timeout=30
            )
            
            # Initialize Redis for real-time metrics
            self.redis_client = await aioredis.from_url(
                self.config['redis_url'],
                encoding='utf-8',
                decode_responses=True
            )
            
            # Setup database schema
            await self._setup_database_schema()
            
            # Load metric definitions
            await self._load_metric_definitions()
            
            # Load alert rules
            await self._load_alert_rules()
            
            # Initialize alert channels
            await self._initialize_alert_channels()
            
            # Start background monitoring tasks
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._drift_detector())
            asyncio.create_task(self._alert_evaluator())
            asyncio.create_task(self._performance_aggregator())
            asyncio.create_task(self._health_checker())
            
            logger.info("Enterprise ML Monitoring System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML Monitoring System: {e}")
            raise
    
    async def register_metric(self, metric_def: MetricDefinition) -> bool:
        """Register new metric for monitoring"""
        try:
            # Store metric definition
            await self._store_metric_definition(metric_def)
            
            # Cache metric
            self.metrics_registry[metric_def.metric_id] = metric_def
            
            # Create Prometheus metric
            self._create_prometheus_metric(metric_def)
            
            # Log registration
            await self._log_monitoring_event(metric_def.model_id, 'METRIC_REGISTERED', {
                'metric_id': metric_def.metric_id,
                'metric_type': metric_def.metric_type.value,
                'collection_interval': metric_def.collection_interval_seconds
            })
            
            logger.info(f"Metric registered: {metric_def.metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register metric: {e}")
            raise
    
    async def record_metric(self, metric_value: MetricValue) -> bool:
        """Record metric value"""
        try:
            # Validate metric exists
            if metric_value.metric_id not in self.metrics_registry:
                logger.warning(f"Unknown metric: {metric_value.metric_id}")
                return False
            
            # Store in database
            await self._store_metric_value(metric_value)
            
            # Store in Redis for real-time access
            await self._cache_metric_value(metric_value)
            
            # Update Prometheus metric
            await self._update_prometheus_metric(metric_value)
            
            # Check for alerts
            await self._evaluate_alerts_for_metric(metric_value)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    async def detect_drift(
        self,
        model_id: str,
        feature_data: Dict[str, List[float]],
        reference_data: Optional[Dict[str, List[float]]] = None
    ) -> List[DriftDetectionResult]:
        """Detect data drift in model features"""
        try:
            drift_results = []
            
            # Get reference data if not provided
            if reference_data is None:
                reference_data = await self._get_reference_data(model_id)
            
            # Detect drift for each feature
            for feature_name, current_values in feature_data.items():
                if feature_name in reference_data:
                    reference_values = reference_data[feature_name]
                    
                    # Run statistical tests
                    drift_result = await self._run_drift_tests(
                        model_id,
                        feature_name,
                        reference_values,
                        current_values
                    )
                    
                    if drift_result:
                        drift_results.append(drift_result)
                        
                        # Store drift result
                        await self._store_drift_result(drift_result)
                        
                        # Trigger alert if drift detected
                        if drift_result.is_drift_detected:
                            await self._trigger_drift_alert(drift_result)
            
            return drift_results
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            raise
    
    async def create_alert_rule(
        self,
        metric_id: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        description: str,
        creator_id: Optional[str] = None
    ) -> str:
        """Create alert rule for metric"""
        try:
            rule_id = f"rule_{uuid.uuid4().hex[:12]}"
            
            alert_rule = {
                'rule_id': rule_id,
                'metric_id': metric_id,
                'condition': condition,  # gt, lt, eq, gte, lte
                'threshold': threshold,
                'severity': severity.value,
                'description': description,
                'creator_id': creator_id,
                'enabled': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Store alert rule
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO alert_rules (
                        rule_id, metric_id, condition, threshold, severity,
                        description, creator_id, enabled, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    rule_id,
                    metric_id,
                    condition,
                    threshold,
                    severity.value,
                    description,
                    creator_id,
                    True,
                    datetime.utcnow()
                )
            
            # Cache alert rule
            self.alert_rules[rule_id] = alert_rule
            
            logger.info(f"Alert rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            raise
    
    async def get_model_metrics(
        self,
        model_id: str,
        metric_types: Optional[List[MetricType]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: str = "avg"
    ) -> Dict[str, Any]:
        """Get metrics for a specific model"""
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.utcnow()
            
            # Build query conditions
            conditions = ["model_id = $1", "timestamp BETWEEN $2 AND $3"]
            params = [model_id, start_time, end_time]
            
            if metric_types:
                param_count = len(params) + 1
                type_conditions = []
                for metric_type in metric_types:
                    type_conditions.append(f"metric_type = ${param_count}")
                    params.append(metric_type.value)
                    param_count += 1
                conditions.append(f"({' OR '.join(type_conditions)})")
            
            where_clause = " AND ".join(conditions)
            
            # Get aggregated metrics
            async with self.db_pool.acquire() as connection:
                if aggregation == "avg":
                    agg_func = "AVG"
                elif aggregation == "max":
                    agg_func = "MAX"
                elif aggregation == "min":
                    agg_func = "MIN"
                else:
                    agg_func = "AVG"
                
                rows = await connection.fetch(
                    f"""
                    SELECT 
                        metric_id,
                        metric_type,
                        {agg_func}(value) as aggregated_value,
                        COUNT(*) as data_points,
                        MIN(timestamp) as first_timestamp,
                        MAX(timestamp) as last_timestamp
                    FROM model_metrics 
                    WHERE {where_clause}
                    GROUP BY metric_id, metric_type
                    """,
                    *params
                )
                
                # Get recent drift results
                drift_rows = await connection.fetch(
                    """
                    SELECT * FROM drift_detections 
                    WHERE model_id = $1 
                    AND detected_at BETWEEN $2 AND $3
                    ORDER BY detected_at DESC
                    """,
                    model_id, start_time, end_time
                )
                
                # Get recent alerts
                alert_rows = await connection.fetch(
                    """
                    SELECT * FROM alerts 
                    WHERE model_id = $1 
                    AND triggered_at BETWEEN $2 AND $3
                    ORDER BY triggered_at DESC
                    """,
                    model_id, start_time, end_time
                )
            
            # Format response
            metrics = {}
            for row in rows:
                metrics[row['metric_id']] = {
                    'metric_type': row['metric_type'],
                    'aggregated_value': float(row['aggregated_value']),
                    'data_points': row['data_points'],
                    'time_range': {
                        'start': row['first_timestamp'].isoformat(),
                        'end': row['last_timestamp'].isoformat()
                    }
                }
            
            drift_results = [
                {
                    'drift_id': row['drift_id'],
                    'drift_type': row['drift_type'],
                    'feature_name': row['feature_name'],
                    'drift_score': float(row['drift_score']),
                    'is_drift_detected': row['is_drift_detected'],
                    'detected_at': row['detected_at'].isoformat()
                }
                for row in drift_rows
            ]
            
            alerts = [
                {
                    'alert_id': row['alert_id'],
                    'alert_type': row['alert_type'],
                    'severity': row['severity'],
                    'message': row['message'],
                    'triggered_at': row['triggered_at'].isoformat(),
                    'resolved_at': row['resolved_at'].isoformat() if row['resolved_at'] else None
                }
                for row in alert_rows
            ]
            
            return {
                'model_id': model_id,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'aggregation': aggregation,
                'metrics': metrics,
                'drift_results': drift_results,
                'alerts': alerts,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get model metrics: {e}")
            raise
    
    async def get_creator_monitoring_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get creator-specific monitoring dashboard for Ainflue platform"""
        try:
            # Get time ranges
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            
            async with self.db_pool.acquire() as connection:
                # Get creator's models and their performance
                model_performance = await connection.fetch(
                    """
                    SELECT 
                        m.model_id,
                        m.metric_type,
                        AVG(m.value) as avg_value,
                        COUNT(*) as data_points,
                        MAX(m.timestamp) as last_update
                    FROM model_metrics m
                    JOIN model_registry mr ON m.model_id = mr.model_id
                    WHERE mr.creator_id = $1
                    AND m.timestamp > $2
                    GROUP BY m.model_id, m.metric_type
                    """,
                    creator_id, last_24h
                )
                
                # Get alert summary
                alert_summary = await connection.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_alerts,
                        COUNT(*) FILTER (WHERE severity = 'critical') as critical_alerts,
                        COUNT(*) FILTER (WHERE severity = 'warning') as warning_alerts,
                        COUNT(*) FILTER (WHERE resolved_at IS NULL) as active_alerts
                    FROM alerts a
                    JOIN model_registry mr ON a.model_id = mr.model_id
                    WHERE mr.creator_id = $1
                    AND a.triggered_at > $2
                    """,
                    creator_id, last_24h
                )
                
                # Get drift summary
                drift_summary = await connection.fetch(
                    """
                    SELECT 
                        d.model_id,
                        COUNT(*) as drift_count,
                        COUNT(*) FILTER (WHERE d.is_drift_detected = true) as detected_drifts
                    FROM drift_detections d
                    JOIN model_registry mr ON d.model_id = mr.model_id
                    WHERE mr.creator_id = $1
                    AND d.detected_at > $2
                    GROUP BY d.model_id
                    """,
                    creator_id, last_24h
                )
                
                # Get business impact metrics
                business_metrics = await connection.fetch(
                    """
                    SELECT 
                        m.model_id,
                        AVG(CASE WHEN m.metric_type = 'business' AND m.labels->>'metric_name' = 'revenue_impact' 
                             THEN m.value ELSE NULL END) as avg_revenue_impact,
                        AVG(CASE WHEN m.metric_type = 'business' AND m.labels->>'metric_name' = 'engagement_score' 
                             THEN m.value ELSE NULL END) as avg_engagement_score,
                        AVG(CASE WHEN m.metric_type = 'performance' AND m.labels->>'metric_name' = 'accuracy' 
                             THEN m.value ELSE NULL END) as avg_accuracy
                    FROM model_metrics m
                    JOIN model_registry mr ON m.model_id = mr.model_id
                    WHERE mr.creator_id = $1
                    AND m.timestamp > $2
                    GROUP BY m.model_id
                    """,
                    creator_id, last_7d
                )
                
                # Get platform-specific performance
                platform_performance = await connection.fetch(
                    """
                    SELECT 
                        m.labels->>'platform' as platform,
                        AVG(m.value) as avg_performance,
                        COUNT(*) as request_count
                    FROM model_metrics m
                    JOIN model_registry mr ON m.model_id = mr.model_id
                    WHERE mr.creator_id = $1
                    AND m.timestamp > $2
                    AND m.labels->>'platform' IS NOT NULL
                    GROUP BY m.labels->>'platform'
                    """,
                    creator_id, last_24h
                )
            
            # Organize performance data by model
            model_metrics = {}
            for row in model_performance:
                model_id = row['model_id']
                if model_id not in model_metrics:
                    model_metrics[model_id] = {}
                
                model_metrics[model_id][row['metric_type']] = {
                    'average_value': float(row['avg_value']),
                    'data_points': row['data_points'],
                    'last_update': row['last_update'].isoformat()
                }
            
            # Organize drift data
            drift_data = {
                row['model_id']: {
                    'total_drift_checks': row['drift_count'],
                    'detected_drifts': row['detected_drifts'],
                    'drift_rate': row['detected_drifts'] / max(row['drift_count'], 1)
                }
                for row in drift_summary
            }
            
            # Calculate overall health score
            total_models = len(model_metrics)
            healthy_models = sum(
                1 for model_data in model_metrics.values()
                if model_data.get('performance', {}).get('average_value', 0) > 0.8
            )
            overall_health_score = healthy_models / max(total_models, 1)
            
            return {
                'creator_id': creator_id,
                'dashboard_generated_at': now.isoformat(),
                'time_period': '24_hours',
                'overview': {
                    'total_models_monitored': total_models,
                    'overall_health_score': overall_health_score,
                    'total_alerts': int(alert_summary['total_alerts'] or 0),
                    'critical_alerts': int(alert_summary['critical_alerts'] or 0),
                    'active_alerts': int(alert_summary['active_alerts'] or 0)
                },
                'model_performance': model_metrics,
                'drift_monitoring': drift_data,
                'business_impact': {
                    row['model_id']: {
                        'revenue_impact': float(row['avg_revenue_impact'] or 0),
                        'engagement_score': float(row['avg_engagement_score'] or 0),
                        'accuracy': float(row['avg_accuracy'] or 0)
                    }
                    for row in business_metrics
                },
                'platform_performance': {
                    row['platform']: {
                        'average_performance': float(row['avg_performance']),
                        'request_count': row['request_count']
                    }
                    for row in platform_performance
                },
                'alerts_summary': {
                    'total': int(alert_summary['total_alerts'] or 0),
                    'critical': int(alert_summary['critical_alerts'] or 0),
                    'warning': int(alert_summary['warning_alerts'] or 0),
                    'active': int(alert_summary['active_alerts'] or 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get creator monitoring dashboard: {e}")
            raise
    
    # Private helper methods
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'model_accuracy': Gauge('model_accuracy', 'Model accuracy', ['model_id', 'creator_id']),
            'model_latency': Histogram('model_latency_seconds', 'Model inference latency', ['model_id', 'creator_id']),
            'model_throughput': Gauge('model_throughput_rps', 'Model throughput requests per second', ['model_id', 'creator_id']),
            'model_error_rate': Gauge('model_error_rate', 'Model error rate', ['model_id', 'creator_id']),
            'drift_detected': Counter('drift_detected_total', 'Total drift detections', ['model_id', 'feature_name', 'drift_type']),
            'alerts_triggered': Counter('alerts_triggered_total', 'Total alerts triggered', ['model_id', 'severity']),
            'business_revenue_impact': Gauge('business_revenue_impact', 'Business revenue impact', ['model_id', 'creator_id']),
            'platform_optimization_score': Gauge('platform_optimization_score', 'Platform optimization score', ['model_id', 'platform'])
        }
    
    async def _setup_database_schema(self):
        """Setup database schema for monitoring"""
        async with self.db_pool.acquire() as connection:
            # Metric definitions table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS metric_definitions (
                    metric_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    metric_type VARCHAR(50) NOT NULL,
                    model_id VARCHAR(50) NOT NULL,
                    description TEXT,
                    calculation_method VARCHAR(100),
                    thresholds JSONB,
                    collection_interval_seconds INTEGER DEFAULT 60,
                    retention_days INTEGER DEFAULT 90,
                    tags JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Model metrics table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS model_metrics (
                    metric_value_id VARCHAR(50) PRIMARY KEY,
                    metric_id VARCHAR(50) NOT NULL,
                    model_id VARCHAR(50) NOT NULL,
                    metric_type VARCHAR(50) NOT NULL,
                    value FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    labels JSONB,
                    metadata JSONB,
                    FOREIGN KEY (metric_id) REFERENCES metric_definitions(metric_id)
                )
            """)
            
            # Alert rules table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS alert_rules (
                    rule_id VARCHAR(50) PRIMARY KEY,
                    metric_id VARCHAR(50) NOT NULL,
                    condition VARCHAR(10) NOT NULL,
                    threshold FLOAT NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    description TEXT,
                    creator_id VARCHAR(100),
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (metric_id) REFERENCES metric_definitions(metric_id)
                )
            """)
            
            # Alerts table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id VARCHAR(50) PRIMARY KEY,
                    metric_id VARCHAR(50) NOT NULL,
                    model_id VARCHAR(50) NOT NULL,
                    alert_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    message TEXT NOT NULL,
                    current_value FLOAT NOT NULL,
                    threshold_value FLOAT NOT NULL,
                    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    resolved_at TIMESTAMP WITH TIME ZONE,
                    creator_id VARCHAR(100),
                    platform_context VARCHAR(100),
                    metadata JSONB
                )
            """)
            
            # Drift detections table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS drift_detections (
                    drift_id VARCHAR(50) PRIMARY KEY,
                    model_id VARCHAR(50) NOT NULL,
                    drift_type VARCHAR(50) NOT NULL,
                    feature_name VARCHAR(200) NOT NULL,
                    drift_score FLOAT NOT NULL,
                    threshold FLOAT NOT NULL,
                    is_drift_detected BOOLEAN NOT NULL,
                    statistical_test VARCHAR(100),
                    p_value FLOAT,
                    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    reference_period_start TIMESTAMP WITH TIME ZONE,
                    reference_period_end TIMESTAMP WITH TIME ZONE,
                    current_period_start TIMESTAMP WITH TIME ZONE,
                    current_period_end TIMESTAMP WITH TIME ZONE,
                    metadata JSONB
                )
            """)
            
            # Monitoring events table
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_events (
                    event_id VARCHAR(50) PRIMARY KEY,
                    model_id VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    event_data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_metrics_model_time ON model_metrics(model_id, timestamp)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type_time ON model_metrics(metric_type, timestamp)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_alerts_model ON alerts(model_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_drift_model ON drift_detections(model_id)")
            await connection.execute("CREATE INDEX IF NOT EXISTS idx_drift_detected ON drift_detections(detected_at)")
    
    async def _store_metric_definition(self, metric_def: MetricDefinition):
        """Store metric definition in database"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO metric_definitions (
                    metric_id, name, metric_type, model_id, description,
                    calculation_method, thresholds, collection_interval_seconds,
                    retention_days, tags, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                metric_def.metric_id,
                metric_def.name,
                metric_def.metric_type.value,
                metric_def.model_id,
                metric_def.description,
                metric_def.calculation_method,
                json.dumps(metric_def.thresholds),
                metric_def.collection_interval_seconds,
                metric_def.retention_days,
                json.dumps(metric_def.tags),
                json.dumps(metric_def.metadata)
            )
    
    async def _store_metric_value(self, metric_value: MetricValue):
        """Store metric value in database"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO model_metrics (
                    metric_value_id, metric_id, model_id, metric_type,
                    value, timestamp, labels, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                f"mv_{uuid.uuid4().hex[:12]}",
                metric_value.metric_id,
                metric_value.model_id,
                self.metrics_registry[metric_value.metric_id].metric_type.value,
                metric_value.value,
                metric_value.timestamp,
                json.dumps(metric_value.labels),
                json.dumps(metric_value.metadata)
            )
    
    async def _cache_metric_value(self, metric_value: MetricValue):
        """Cache metric value in Redis for real-time access"""
        cache_key = f"metric:{metric_value.model_id}:{metric_value.metric_id}"
        metric_data = {
            'value': metric_value.value,
            'timestamp': metric_value.timestamp.isoformat(),
            'labels': metric_value.labels,
            'metadata': metric_value.metadata
        }
        
        await self.redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(metric_data)
        )
    
    def _create_prometheus_metric(self, metric_def: MetricDefinition):
        """Create Prometheus metric for monitoring definition"""
        metric_name = f"ainflue_{metric_def.name.replace(' ', '_').lower()}"
        
        if metric_def.metric_type == MetricType.LATENCY:
            self.prometheus_metrics[metric_def.metric_id] = Histogram(
                metric_name,
                metric_def.description,
                ['model_id', 'creator_id']
            )
        elif metric_def.metric_type in [MetricType.ACCURACY, MetricType.THROUGHPUT, MetricType.BUSINESS]:
            self.prometheus_metrics[metric_def.metric_id] = Gauge(
                metric_name,
                metric_def.description,
                ['model_id', 'creator_id']
            )
        else:
            self.prometheus_metrics[metric_def.metric_id] = Counter(
                metric_name,
                metric_def.description,
                ['model_id', 'creator_id']
            )
    
    async def _update_prometheus_metric(self, metric_value: MetricValue):
        """Update Prometheus metric with new value"""
        if metric_value.metric_id in self.prometheus_metrics:
            metric = self.prometheus_metrics[metric_value.metric_id]
            labels = {
                'model_id': metric_value.model_id,
                'creator_id': metric_value.labels.get('creator_id', 'unknown')
            }
            
            if isinstance(metric, Gauge):
                metric.labels(**labels).set(metric_value.value)
            elif isinstance(metric, Counter):
                metric.labels(**labels).inc(metric_value.value)
            elif isinstance(metric, Histogram):
                metric.labels(**labels).observe(metric_value.value)
    
    async def _evaluate_alerts_for_metric(self, metric_value: MetricValue):
        """Evaluate alert rules for metric value"""
        try:
            # Find alert rules for this metric
            rules_for_metric = [
                rule for rule in self.alert_rules.values()
                if rule['metric_id'] == metric_value.metric_id and rule['enabled']
            ]
            
            for rule in rules_for_metric:
                condition = rule['condition']
                threshold = rule['threshold']
                current_value = metric_value.value
                
                # Evaluate condition
                triggered = False
                if condition == 'gt' and current_value > threshold:
                    triggered = True
                elif condition == 'lt' and current_value < threshold:
                    triggered = True
                elif condition == 'gte' and current_value >= threshold:
                    triggered = True
                elif condition == 'lte' and current_value <= threshold:
                    triggered = True
                elif condition == 'eq' and abs(current_value - threshold) < 0.001:
                    triggered = True
                
                if triggered:
                    alert = Alert(
                        alert_id=f"alert_{uuid.uuid4().hex[:12]}",
                        metric_id=metric_value.metric_id,
                        model_id=metric_value.model_id,
                        alert_type=f"threshold_{condition}",
                        severity=AlertSeverity(rule['severity']),
                        message=f"{rule['description']}: {current_value} {condition} {threshold}",
                        current_value=current_value,
                        threshold_value=threshold,
                        triggered_at=datetime.utcnow(),
                        creator_id=rule.get('creator_id')
                    )
                    
                    await self._trigger_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error evaluating alerts: {e}")
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger alert and send notifications"""
        try:
            # Store alert in database
            async with self.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO alerts (
                        alert_id, metric_id, model_id, alert_type, severity,
                        message, current_value, threshold_value, triggered_at,
                        creator_id, platform_context, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    """,
                    alert.alert_id,
                    alert.metric_id,
                    alert.model_id,
                    alert.alert_type,
                    alert.severity.value,
                    alert.message,
                    alert.current_value,
                    alert.threshold_value,
                    alert.triggered_at,
                    alert.creator_id,
                    alert.platform_context,
                    json.dumps(alert.metadata)
                )
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            # Update Prometheus counter
            self.prometheus_metrics['alerts_triggered'].labels(
                model_id=alert.model_id,
                severity=alert.severity.value
            ).inc()
            
            logger.warning(f"Alert triggered: {alert.alert_id} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    async def _run_drift_tests(
        self,
        model_id: str,
        feature_name: str,
        reference_data: List[float],
        current_data: List[float]
    ) -> Optional[DriftDetectionResult]:
        """Run statistical tests for drift detection"""
        try:
            # Kolmogorov-Smirnov test
            ks_statistic, p_value = stats.ks_2samp(reference_data, current_data)
            
            # Set threshold (can be configurable)
            threshold = 0.05  # p-value threshold
            drift_detected = p_value < threshold
            
            drift_result = DriftDetectionResult(
                drift_id=f"drift_{uuid.uuid4().hex[:12]}",
                model_id=model_id,
                drift_type=DriftType.DATA_DRIFT,
                feature_name=feature_name,
                drift_score=ks_statistic,
                threshold=threshold,
                is_drift_detected=drift_detected,
                statistical_test="kolmogorov_smirnov",
                p_value=p_value,
                detected_at=datetime.utcnow(),
                reference_period=(
                    datetime.utcnow() - timedelta(days=7),
                    datetime.utcnow() - timedelta(days=1)
                ),
                current_period=(
                    datetime.utcnow() - timedelta(hours=24),
                    datetime.utcnow()
                )
            )
            
            return drift_result
            
        except Exception as e:
            logger.error(f"Drift test failed: {e}")
            return None
    
    async def _store_drift_result(self, drift_result: DriftDetectionResult):
        """Store drift detection result"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO drift_detections (
                    drift_id, model_id, drift_type, feature_name, drift_score,
                    threshold, is_drift_detected, statistical_test, p_value,
                    detected_at, reference_period_start, reference_period_end,
                    current_period_start, current_period_end, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """,
                drift_result.drift_id,
                drift_result.model_id,
                drift_result.drift_type.value,
                drift_result.feature_name,
                drift_result.drift_score,
                drift_result.threshold,
                drift_result.is_drift_detected,
                drift_result.statistical_test,
                drift_result.p_value,
                drift_result.detected_at,
                drift_result.reference_period[0],
                drift_result.reference_period[1],
                drift_result.current_period[0],
                drift_result.current_period[1],
                json.dumps(drift_result.metadata)
            )
    
    async def _trigger_drift_alert(self, drift_result: DriftDetectionResult):
        """Trigger alert for detected drift"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            metric_id="drift_detection",
            model_id=drift_result.model_id,
            alert_type="data_drift",
            severity=AlertSeverity.WARNING,
            message=f"Data drift detected in feature '{drift_result.feature_name}' with score {drift_result.drift_score:.4f}",
            current_value=drift_result.drift_score,
            threshold_value=drift_result.threshold,
            triggered_at=drift_result.detected_at,
            metadata={'drift_id': drift_result.drift_id}
        )
        
        await self._trigger_alert(alert)
    
    async def _get_reference_data(self, model_id: str) -> Dict[str, List[float]]:
        """Get reference data for drift detection"""
        # This would implement actual reference data retrieval
        # For now, return empty dict
        return {}
    
    async def _load_metric_definitions(self):
        """Load metric definitions from database"""
        async with self.db_pool.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM metric_definitions")
            
            for row in rows:
                metric_def = MetricDefinition(
                    metric_id=row['metric_id'],
                    name=row['name'],
                    metric_type=MetricType(row['metric_type']),
                    model_id=row['model_id'],
                    description=row['description'],
                    calculation_method=row['calculation_method'],
                    thresholds=json.loads(row['thresholds']) if row['thresholds'] else {},
                    collection_interval_seconds=row['collection_interval_seconds'],
                    retention_days=row['retention_days'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                
                self.metrics_registry[metric_def.metric_id] = metric_def
                self._create_prometheus_metric(metric_def)
    
    async def _load_alert_rules(self):
        """Load alert rules from database"""
        async with self.db_pool.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM alert_rules WHERE enabled = true")
            
            for row in rows:
                rule = {
                    'rule_id': row['rule_id'],
                    'metric_id': row['metric_id'],
                    'condition': row['condition'],
                    'threshold': float(row['threshold']),
                    'severity': row['severity'],
                    'description': row['description'],
                    'creator_id': row['creator_id'],
                    'enabled': row['enabled'],
                    'created_at': row['created_at'].isoformat()
                }
                
                self.alert_rules[row['rule_id']] = rule
    
    async def _initialize_alert_channels(self):
        """Initialize alert notification channels"""
        self.alert_channels = {
            'email': self._send_email_alert,
            'webhook': self._send_webhook_alert,
            'websocket': self._send_websocket_alert
        }
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        try:
            # Send email notification
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                await self._send_email_alert(alert)
            
            # Send webhook notification
            await self._send_webhook_alert(alert)
            
            # Send real-time websocket notification
            await self._send_websocket_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to send alert notifications: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert notification"""
        try:
            if not self.config.get('smtp_server'):
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp_from']
            msg['To'] = self.config['alert_email']
            msg['Subject'] = f"Ainflue ML Alert - {alert.severity.value.upper()}"
            
            body = f"""
            Alert Details:
            - Alert ID: {alert.alert_id}
            - Model ID: {alert.model_id}
            - Severity: {alert.severity.value}
            - Message: {alert.message}
            - Current Value: {alert.current_value}
            - Threshold: {alert.threshold_value}
            - Triggered At: {alert.triggered_at}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_username'], self.config['smtp_password'])
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert notification"""
        try:
            if not self.config.get('alert_webhook_url'):
                return
            
            payload = {
                'alert_id': alert.alert_id,
                'model_id': alert.model_id,
                'severity': alert.severity.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'triggered_at': alert.triggered_at.isoformat(),
                'creator_id': alert.creator_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config['alert_webhook_url'],
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    async def _send_websocket_alert(self, alert: Alert):
        """Send real-time websocket alert notification"""
        try:
            # This would implement websocket alert broadcasting
            # For now, just log
            logger.info(f"WebSocket alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send websocket alert: {e}")
    
    # Background monitoring tasks
    
    async def _metrics_collector(self):
        """Background metrics collection"""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect model performance metrics
                await self._collect_model_metrics()
                
                await asyncio.sleep(self.monitoring_config['metrics_collection_interval'])
                
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(60)
    
    async def _drift_detector(self):
        """Background drift detection"""
        while True:
            try:
                # Run drift detection for all monitored models
                for model_id in self._get_monitored_models():
                    await self._check_model_drift(model_id)
                
                await asyncio.sleep(self.monitoring_config['drift_detection_interval'])
                
            except Exception as e:
                logger.error(f"Error in drift detector: {e}")
                await asyncio.sleep(300)
    
    async def _alert_evaluator(self):
        """Background alert evaluation"""
        while True:
            try:
                # This runs continuously but alerts are evaluated
                # in real-time when metrics are recorded
                await asyncio.sleep(self.monitoring_config['alert_evaluation_interval'])
                
            except Exception as e:
                logger.error(f"Error in alert evaluator: {e}")
                await asyncio.sleep(30)
    
    async def _performance_aggregator(self):
        """Background performance aggregation"""
        while True:
            try:
                # Aggregate metrics for performance dashboards
                await self._aggregate_performance_metrics()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance aggregator: {e}")
                await asyncio.sleep(300)
    
    async def _health_checker(self):
        """Background health checking"""
        while True:
            try:
                # Check system health
                system_health = await self._check_system_health()
                
                # Record health metrics
                health_metric = MetricValue(
                    metric_id="system_health",
                    model_id="system",
                    value=system_health,
                    timestamp=datetime.utcnow()
                )
                
                await self._cache_metric_value(health_metric)
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"Error in health checker: {e}")
                await asyncio.sleep(60)
    
    def _get_monitored_models(self) -> List[str]:
        """Get list of monitored model IDs"""
        return list(set(metric.model_id for metric in self.metrics_registry.values()))
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent()
            await self.record_metric(MetricValue(
                metric_id="system_cpu_usage",
                model_id="system",
                value=cpu_usage,
                timestamp=datetime.utcnow()
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric(MetricValue(
                metric_id="system_memory_usage",
                model_id="system",
                value=memory.percent,
                timestamp=datetime.utcnow()
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_model_metrics(self):
        """Collect model-specific metrics"""
        # This would implement actual model metric collection
        pass
    
    async def _check_model_drift(self, model_id: str):
        """Check drift for specific model"""
        # This would implement actual drift checking
        pass
    
    async def _aggregate_performance_metrics(self):
        """Aggregate performance metrics for dashboards"""
        # This would implement performance metric aggregation
        pass
    
    async def _check_system_health(self) -> float:
        """Check overall system health"""
        # Simple health score based on CPU and memory
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        # Health score (0-1, where 1 is healthiest)
        health_score = max(0, 1 - (cpu_usage + memory_usage) / 200)
        return health_score
    
    async def _log_monitoring_event(self, model_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log monitoring event"""
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO monitoring_events (event_id, model_id, event_type, event_data)
                VALUES ($1, $2, $3, $4)
                """,
                event_id,
                model_id,
                event_type,
                json.dumps(event_data)
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_pool:
            await self.db_pool.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.executor:
            self.executor.shutdown(wait=True)


# Factory function for easy initialization
async def create_ml_monitoring_system(config: Dict[str, Any]) -> EnterpriseMLMonitoringSystem:
    """Create and initialize ML monitoring system"""
    system = EnterpriseMLMonitoringSystem(config)
    await system.initialize()
    return system