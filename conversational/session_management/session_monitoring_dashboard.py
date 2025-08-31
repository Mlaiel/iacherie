"""Session Monitoring Dashboard - IA Influencer Agent

Enterprise-grade real-time session monitoring dashboard with advanced
analytics, intelligent alerting, and comprehensive performance tracking
for multi-format content creator sessions across all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copy, modification, or distribution without 
explicit written permission is strictly prohibited.
Contact: mlaiel@live.de

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Real-Time Monitoring Architecture
- ML Engineer: Predictive Analytics & Anomaly Detection
- DBA: Performance Metrics & Query Optimization
- Security Expert: Monitoring Security & Access Control
- Microservices Architect: Distributed Monitoring Systems
- DevOps: Infrastructure Monitoring & Scalability
- UI/UX Engineer: Dashboard Design & User Experience
- IA Prompt Engineer: Intelligent Monitoring Insights
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict, deque
import time
import statistics

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, insert, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, SessionMetricsModel
from ...models.user import UserModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher
from ...utils.websocket_manager import WebSocketManager
from ...utils.alert_manager import AlertManager

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT = "content"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DashboardViewType(Enum):
    """Dashboard view types"""    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT = "content"
    USER_ANALYTICS = "user_analytics"
    SYSTEM_HEALTH = "system_health"
    ALERTS = "alerts"
    CUSTOM = "custom"


class TimeRange(Enum):
    """Time range options"""    REAL_TIME = "real_time"
    LAST_5_MIN = "last_5_min"
    LAST_15_MIN = "last_15_min"
    LAST_30_MIN = "last_30_min"
    LAST_HOUR = "last_hour"
    LAST_6_HOURS = "last_6_hours"
    LAST_24_HOURS = "last_24_hours"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"


class SessionMetric(BaseModel):
    """Individual session metric"""    metric_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    metric_type: MetricType
    metric_name: str
    metric_value: float
    metric_unit: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionAlert(BaseModel):
    """Session monitoring alert"""    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    threshold_value: float
    actual_value: float
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""    widget_id: str = Field(default_factory=lambda: str(uuid4()))
    widget_type: str  # chart, table, metric, alert_list
    title: str
    metric_types: List[MetricType] = Field(default_factory=list)
    time_range: TimeRange = TimeRange.LAST_HOUR
    refresh_interval: int = 30  # seconds
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    configuration: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class DashboardView(BaseModel):
    """Dashboard view configuration"""    view_id: str = Field(default_factory=lambda: str(uuid4()))
    view_name: str
    view_type: DashboardViewType
    user_id: str
    widgets: List[DashboardWidget] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    auto_refresh: bool = True
    refresh_interval: int = 30  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionAnalytics(BaseModel):
    """Session analytics data"""    session_id: str
    user_id: str
    session_duration: float  # minutes
    engagement_score: float
    performance_score: float
    revenue_generated: float
    content_interactions: int
    error_count: int
    average_response_time: float  # milliseconds
    peak_concurrent_users: int
    bandwidth_usage: float  # MB
    cpu_usage_avg: float  # percentage
    memory_usage_avg: float  # percentage
    analytics_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class MonitoringConfig:
    """Monitoring dashboard configuration"""    enable_real_time_monitoring: bool = True
    metric_collection_interval: int = 5  # seconds
    alert_evaluation_interval: int = 10  # seconds
    dashboard_refresh_interval: int = 30  # seconds
    max_metrics_retention_hours: int = 168  # 7 days
    enable_anomaly_detection: bool = True
    anomaly_detection_sensitivity: float = 0.8
    enable_predictive_alerts: bool = True
    alert_cooldown_minutes: int = 15
    max_alerts_per_session: int = 50
    enable_dashboard_caching: bool = True
    dashboard_cache_ttl: int = 60  # seconds


class MetricsCollectionEngine:
    """Collects and processes session metrics"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # In-memory metric buffers for real-time processing
        self.metric_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.session_metrics: Dict[str, Dict[str, List[SessionMetric]]] = defaultdict(lambda: defaultdict(list))
    
    async def collect_session_metric(
        self,
        session_id: str,
        user_id: str,
        metric_type: MetricType,
        metric_name: str,
        metric_value: float,
        metric_unit: str = "",
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> SessionMetric:
        """Collect a session metric"""        
        try:
            metric = SessionMetric(
                session_id=session_id,
                user_id=user_id,
                metric_type=metric_type,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Add to in-memory buffers
            buffer_key = f"{session_id}:{metric_type.value}:{metric_name}"
            self.metric_buffers[buffer_key].append(metric)
            
            # Add to session metrics
            self.session_metrics[session_id][metric_name].append(metric)
            
            # Cache for real-time access
            await self._cache_metric(metric)
            
            # Publish metric event for real-time updates
            await self.event_publisher.publish(
                "monitoring.metric_collected",
                {
                    "metric_id": metric.metric_id,
                    "session_id": session_id,
                    "metric_type": metric_type.value,
                    "metric_name": metric_name,
                    "metric_value": metric_value,
                    "timestamp": metric.timestamp.isoformat()
                }
            )
            
            return metric
            
        except Exception as e:
            self.logger.error(f"Metric collection failed: {str(e)}")
            raise
    
    async def _cache_metric(self, metric: SessionMetric):
        """Cache metric for fast retrieval"""        
        try:
            # Cache individual metric
            cache_key = f"metric:{metric.metric_id}"
            await self.cache_manager.set(
                cache_key,
                metric.json(),
                ttl=3600
            )
            
            # Cache latest value for dashboard
            latest_key = f"latest_metric:{metric.session_id}:{metric.metric_name}"
            await self.cache_manager.set(
                latest_key,
                metric.json(),
                ttl=300
            )
            
        except Exception as e:
            self.logger.error(f"Metric caching failed: {str(e)}")
    
    async def get_session_metrics(
        self,
        session_id: str,
        metric_types: List[MetricType] = None,
        time_range: TimeRange = TimeRange.LAST_HOUR,
        metric_names: List[str] = None
    ) -> Dict[str, List[SessionMetric]]:
        """Get session metrics with filters"""        
        try:
            # Calculate time window
            end_time = datetime.utcnow()
            
            if time_range == TimeRange.REAL_TIME:
                start_time = end_time - timedelta(minutes=5)
            elif time_range == TimeRange.LAST_5_MIN:
                start_time = end_time - timedelta(minutes=5)
            elif time_range == TimeRange.LAST_15_MIN:
                start_time = end_time - timedelta(minutes=15)
            elif time_range == TimeRange.LAST_30_MIN:
                start_time = end_time - timedelta(minutes=30)
            elif time_range == TimeRange.LAST_HOUR:
                start_time = end_time - timedelta(hours=1)
            elif time_range == TimeRange.LAST_6_HOURS:
                start_time = end_time - timedelta(hours=6)
            elif time_range == TimeRange.LAST_24_HOURS:
                start_time = end_time - timedelta(hours=24)
            elif time_range == TimeRange.LAST_7_DAYS:
                start_time = end_time - timedelta(days=7)
            elif time_range == TimeRange.LAST_30_DAYS:
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Filter metrics from in-memory storage
            filtered_metrics = defaultdict(list)
            
            if session_id in self.session_metrics:
                session_data = self.session_metrics[session_id]
                
                for metric_name, metrics_list in session_data.items():
                    if metric_names and metric_name not in metric_names:
                        continue
                    
                    for metric in metrics_list:
                        # Time filter
                        if start_time <= metric.timestamp <= end_time:
                            # Type filter
                            if metric_types and metric.metric_type not in metric_types:
                                continue
                            
                            filtered_metrics[metric_name].append(metric)
            
            return dict(filtered_metrics)
            
        except Exception as e:
            self.logger.error(f"Session metrics retrieval failed: {str(e)}")
            return {}
    
    async def aggregate_metrics(
        self,
        session_id: str,
        metric_name: str,
        aggregation_type: str = "avg",  # avg, sum, min, max, count
        time_range: TimeRange = TimeRange.LAST_HOUR
    ) -> float:
        """Aggregate metrics over time range"""        
        try:
            metrics_data = await self.get_session_metrics(
                session_id,
                metric_names=[metric_name],
                time_range=time_range
            )
            
            if metric_name not in metrics_data:
                return 0.0
            
            values = [metric.metric_value for metric in metrics_data[metric_name]]
            
            if not values:
                return 0.0
            
            if aggregation_type == "avg":
                return statistics.mean(values)
            elif aggregation_type == "sum":
                return sum(values)
            elif aggregation_type == "min":
                return min(values)
            elif aggregation_type == "max":
                return max(values)
            elif aggregation_type == "count":
                return len(values)
            else:
                return statistics.mean(values)
                
        except Exception as e:
            self.logger.error(f"Metric aggregation failed: {str(e)}")
            return 0.0
    
    async def persist_metrics(self, session_id: str):
        """Persist metrics to database"""        
        try:
            if session_id not in self.session_metrics:
                return
            
            async with get_async_session() as session:
                for metric_name, metrics_list in self.session_metrics[session_id].items():
                    for metric in metrics_list:
                        metric_record = SessionMetricsModel(
                            metric_id=metric.metric_id,
                            session_id=metric.session_id,
                            user_id=metric.user_id,
                            metric_type=metric.metric_type.value,
                            metric_name=metric.metric_name,
                            metric_value=metric.metric_value,
                            metric_unit=metric.metric_unit,
                            tags=metric.tags,
                            metadata=metric.metadata,
                            timestamp=metric.timestamp
                        )
                        
                        session.add(metric_record)
                
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Metrics persistence failed: {str(e)}")


class AnomalyDetectionEngine:
    """Detects anomalies in session metrics"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.isolation_forest = IsolationForest(
            contamination=1.0 - self.config.anomaly_detection_sensitivity,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.logger = get_logger(self.__class__.__name__)
        
        # Store training data
        self.training_data: Dict[str, List[float]] = defaultdict(list)
        self.models_trained: Dict[str, bool] = {}
    
    async def detect_anomalies(
        self,
        session_id: str,
        metrics_data: Dict[str, List[SessionMetric]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in session metrics"""        
        try:
            anomalies = []
            
            for metric_name, metrics_list in metrics_data.items():
                if len(metrics_list) < 10:  # Need minimum data points
                    continue
                
                # Extract values
                values = [metric.metric_value for metric in metrics_list]
                timestamps = [metric.timestamp for metric in metrics_list]
                
                # Detect statistical anomalies
                stat_anomalies = await self._detect_statistical_anomalies(
                    metric_name, values, timestamps
                )
                anomalies.extend(stat_anomalies)
                
                # Detect ML-based anomalies
                if self.config.enable_anomaly_detection:
                    ml_anomalies = await self._detect_ml_anomalies(
                        session_id, metric_name, values, timestamps
                    )
                    anomalies.extend(ml_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return []
    
    async def _detect_statistical_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using z-score"""        
        try:
            anomalies = []
            
            if len(values) < 3:
                return anomalies
            
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values) if len(values) > 1 else 0
            
            if stdev_val == 0:
                return anomalies
            
            # Z-score threshold for anomaly detection
            z_threshold = 2.5
            
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                z_score = abs((value - mean_val) / stdev_val)
                
                if z_score > z_threshold:
                    anomalies.append({
                        "anomaly_type": "statistical",
                        "metric_name": metric_name,
                        "value": value,
                        "expected_range": [mean_val - 2*stdev_val, mean_val + 2*stdev_val],
                        "z_score": z_score,
                        "timestamp": timestamp.isoformat(),
                        "severity": "warning" if z_score < 3 else "error"
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {str(e)}")
            return []
    
    async def _detect_ml_anomalies(
        self,
        session_id: str,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using machine learning"""        
        try:
            anomalies = []
            
            # Check if we have enough training data
            model_key = f"{session_id}:{metric_name}"
            
            if len(values) < 50:  # Need more data for ML
                return anomalies
            
            # Prepare data
            X = np.array(values).reshape(-1, 1)
            
            # Train model if not already trained
            if model_key not in self.models_trained:
                self.isolation_forest.fit(X)
                self.models_trained[model_key] = True
            
            # Predict anomalies
            anomaly_predictions = self.isolation_forest.predict(X)
            anomaly_scores = self.isolation_forest.score_samples(X)
            
            # Extract anomalies
            for i, (prediction, score, value, timestamp) in enumerate(
                zip(anomaly_predictions, anomaly_scores, values, timestamps)
            ):
                if prediction == -1:  # Anomaly detected
                    anomalies.append({
                        "anomaly_type": "ml_based",
                        "metric_name": metric_name,
                        "value": value,
                        "anomaly_score": float(score),
                        "timestamp": timestamp.isoformat(),
                        "severity": "warning" if score > -0.5 else "error"
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"ML anomaly detection failed: {str(e)}")
            return []


class AlertingEngine:
    """Manages session monitoring alerts"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_manager = AlertManager()
        self.cache_manager = CacheManager()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Alert rules and thresholds
        self.alert_rules: Dict[str, Dict[str, Any]] = {
            "response_time_high": {
                "metric_name": "response_time",
                "threshold": 1000,  # ms
                "operator": ">",
                "severity": AlertSeverity.WARNING,
                "description": "High response time detected"
            },
            "error_rate_high": {
                "metric_name": "error_rate",
                "threshold": 0.05,  # 5%
                "operator": ">",
                "severity": AlertSeverity.ERROR,
                "description": "High error rate detected"
            },
            "memory_usage_high": {
                "metric_name": "memory_usage",
                "threshold": 0.85,  # 85%
                "operator": ">",
                "severity": AlertSeverity.WARNING,
                "description": "High memory usage detected"
            },
            "engagement_low": {
                "metric_name": "engagement_score",
                "threshold": 0.3,
                "operator": "<",
                "severity": AlertSeverity.INFO,
                "description": "Low engagement score detected"
            }
        }
        
        # Alert cooldown tracking
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        # Active alerts
        self.active_alerts: Dict[str, SessionAlert] = {}
    
    async def evaluate_alerts(
        self,
        session_id: str,
        user_id: str,
        metrics_data: Dict[str, List[SessionMetric]],
        anomalies: List[Dict[str, Any]] = None
    ) -> List[SessionAlert]:
        """Evaluate alert conditions"""        
        try:
            triggered_alerts = []
            
            # Evaluate metric-based alerts
            for rule_name, rule_config in self.alert_rules.items():
                alert = await self._evaluate_metric_alert(
                    session_id, user_id, rule_name, rule_config, metrics_data
                )
                
                if alert:
                    triggered_alerts.append(alert)
            
            # Evaluate anomaly-based alerts
            if anomalies:
                anomaly_alerts = await self._evaluate_anomaly_alerts(
                    session_id, user_id, anomalies
                )
                triggered_alerts.extend(anomaly_alerts)
            
            # Process triggered alerts
            for alert in triggered_alerts:
                await self._process_alert(alert)
            
            return triggered_alerts
            
        except Exception as e:
            self.logger.error(f"Alert evaluation failed: {str(e)}")
            return []
    
    async def _evaluate_metric_alert(
        self,
        session_id: str,
        user_id: str,
        rule_name: str,
        rule_config: Dict[str, Any],
        metrics_data: Dict[str, List[SessionMetric]]
    ) -> Optional[SessionAlert]:
        """Evaluate individual metric alert rule"""        
        try:
            metric_name = rule_config["metric_name"]
            threshold = rule_config["threshold"]
            operator = rule_config["operator"]
            severity = rule_config["severity"]
            
            if metric_name not in metrics_data:
                return None
            
            # Get latest metric value
            metrics_list = metrics_data[metric_name]
            if not metrics_list:
                return None
            
            latest_metric = metrics_list[-1]
            current_value = latest_metric.metric_value
            
            # Evaluate condition
            condition_met = False
            
            if operator == ">":
                condition_met = current_value > threshold
            elif operator == "<":
                condition_met = current_value < threshold
            elif operator == ">=":
                condition_met = current_value >= threshold
            elif operator == "<=":
                condition_met = current_value <= threshold
            elif operator == "==":
                condition_met = current_value == threshold
            elif operator == "!=":
                condition_met = current_value != threshold
            
            if not condition_met:
                return None
            
            # Check cooldown
            cooldown_key = f"{session_id}:{rule_name}"
            
            if cooldown_key in self.alert_cooldowns:
                cooldown_end = self.alert_cooldowns[cooldown_key]
                if datetime.utcnow() < cooldown_end:
                    return None  # Still in cooldown
            
            # Create alert
            alert = SessionAlert(
                session_id=session_id,
                user_id=user_id,
                alert_type=rule_name,
                severity=severity,
                title=f"{rule_config['description']} - {metric_name}",
                description=f"{metric_name} value {current_value} {operator} {threshold}",
                metric_name=metric_name,
                threshold_value=threshold,
                actual_value=current_value,
                metadata={
                    "rule_name": rule_name,
                    "metric_unit": latest_metric.metric_unit,
                    "metric_timestamp": latest_metric.timestamp.isoformat()
                }
            )
            
            # Set cooldown
            self.alert_cooldowns[cooldown_key] = (
                datetime.utcnow() + timedelta(minutes=self.config.alert_cooldown_minutes)
            )
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Metric alert evaluation failed: {str(e)}")
            return None
    
    async def _evaluate_anomaly_alerts(
        self,
        session_id: str,
        user_id: str,
        anomalies: List[Dict[str, Any]]
    ) -> List[SessionAlert]:
        """Evaluate anomaly-based alerts"""        
        try:
            alerts = []
            
            for anomaly in anomalies:
                # Map anomaly severity to alert severity
                severity_map = {
                    "info": AlertSeverity.INFO,
                    "warning": AlertSeverity.WARNING,
                    "error": AlertSeverity.ERROR,
                    "critical": AlertSeverity.CRITICAL
                }
                
                severity = severity_map.get(anomaly.get("severity", "warning"), AlertSeverity.WARNING)
                
                alert = SessionAlert(
                    session_id=session_id,
                    user_id=user_id,
                    alert_type="anomaly_detected",
                    severity=severity,
                    title=f"Anomaly detected in {anomaly['metric_name']}",
                    description=f"{anomaly['anomaly_type']} anomaly: {anomaly['value']}",
                    metric_name=anomaly["metric_name"],
                    threshold_value=0.0,  # Not applicable for anomalies
                    actual_value=anomaly["value"],
                    metadata=anomaly
                )
                
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Anomaly alert evaluation failed: {str(e)}")
            return []
    
    async def _process_alert(self, alert: SessionAlert):
        """Process triggered alert"""        
        try:
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Cache alert
            cache_key = f"alert:{alert.alert_id}"
            await self.cache_manager.set(
                cache_key,
                alert.json(),
                ttl=3600
            )
            
            # Send alert through alert manager
            await self.alert_manager.send_alert(
                alert.title,
                alert.description,
                alert.severity.value,
                {
                    "alert_id": alert.alert_id,
                    "session_id": alert.session_id,
                    "metric_name": alert.metric_name,
                    "actual_value": alert.actual_value
                }
            )
            
            # Publish alert event
            await self.event_publisher.publish(
                "monitoring.alert_triggered",
                {
                    "alert_id": alert.alert_id,
                    "session_id": alert.session_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "title": alert.title
                }
            )
            
            self.logger.info(f"Alert triggered: {alert.alert_id} - {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Alert processing failed: {str(e)}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""        
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            # Update cache
            cache_key = f"alert:{alert_id}"
            await self.cache_manager.set(
                cache_key,
                alert.json(),
                ttl=3600
            )
            
            # Publish acknowledgment event
            await self.event_publisher.publish(
                "monitoring.alert_acknowledged",
                {
                    "alert_id": alert_id,
                    "acknowledged_by": acknowledged_by,
                    "acknowledged_at": alert.acknowledged_at.isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Alert acknowledgment failed: {str(e)}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""        
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            # Update cache
            cache_key = f"alert:{alert_id}"
            await self.cache_manager.set(
                cache_key,
                alert.json(),
                ttl=3600
            )
            
            # Publish resolution event
            await self.event_publisher.publish(
                "monitoring.alert_resolved",
                {
                    "alert_id": alert_id,
                    "resolved_at": alert.resolved_at.isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Alert resolution failed: {str(e)}")
            return False


class DashboardDataProvider:
    """Provides data for dashboard widgets"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.logger = get_logger(self.__class__.__name__)
    
    async def get_widget_data(
        self,
        widget: DashboardWidget,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get data for dashboard widget"""        
        try:
            # Check cache first
            cache_key = f"widget_data:{widget.widget_id}:{session_id or 'all'}"
            
            if self.config.enable_dashboard_caching:
                cached_data = await self.cache_manager.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            
            # Generate widget data based on type
            if widget.widget_type == "metric":
                data = await self._get_metric_widget_data(widget, session_id, user_id)
            elif widget.widget_type == "chart":
                data = await self._get_chart_widget_data(widget, session_id, user_id)
            elif widget.widget_type == "table":
                data = await self._get_table_widget_data(widget, session_id, user_id)
            elif widget.widget_type == "alert_list":
                data = await self._get_alert_list_widget_data(widget, session_id, user_id)
            else:
                data = {"error": f"Unknown widget type: {widget.widget_type}"}
            
            # Cache result
            if self.config.enable_dashboard_caching:
                await self.cache_manager.set(
                    cache_key,
                    json.dumps(data, default=str),
                    ttl=self.config.dashboard_cache_ttl
                )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Widget data generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_metric_widget_data(
        self,
        widget: DashboardWidget,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get data for metric widget"""        
        try:
            # This would aggregate metrics from the metrics collection engine
            # For now, return sample data
            
            return {
                "widget_type": "metric",
                "title": widget.title,
                "value": 42.5,
                "unit": "ms",
                "trend": "up",
                "change_percentage": 5.2,
                "status": "normal",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Metric widget data generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_chart_widget_data(
        self,
        widget: DashboardWidget,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get data for chart widget"""        
        try:
            # Generate time series data
            current_time = datetime.utcnow()
            time_points = []
            values = []
            
            # Generate sample time series data
            for i in range(20):
                time_point = current_time - timedelta(minutes=i*5)
                time_points.append(time_point.isoformat())
                values.append(50 + (i % 10) + np.random.normal(0, 5))
            
            return {
                "widget_type": "chart",
                "title": widget.title,
                "chart_type": widget.configuration.get("chart_type", "line"),
                "data": {
                    "labels": list(reversed(time_points)),
                    "datasets": [{
                        "label": "Metric Value",
                        "data": list(reversed(values)),
                        "borderColor": "#007bff",
                        "backgroundColor": "#007bff20"
                    }]
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Chart widget data generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_table_widget_data(
        self,
        widget: DashboardWidget,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get data for table widget"""        
        try:
            # Generate sample table data
            return {
                "widget_type": "table",
                "title": widget.title,
                "columns": ["Session ID", "User ID", "Status", "Duration", "Score"],
                "rows": [
                    ["sess_001", "user_123", "Active", "45m", "8.5"],
                    ["sess_002", "user_456", "Active", "32m", "7.2"],
                    ["sess_003", "user_789", "Ended", "67m", "9.1"]
                ],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Table widget data generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _get_alert_list_widget_data(
        self,
        widget: DashboardWidget,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get data for alert list widget"""        
        try:
            # This would fetch active alerts
            # For now, return sample data
            
            return {
                "widget_type": "alert_list",
                "title": widget.title,
                "alerts": [
                    {
                        "id": "alert_001",
                        "severity": "warning",
                        "title": "High Response Time",
                        "description": "Response time exceeded threshold",
                        "timestamp": datetime.utcnow().isoformat(),
                        "acknowledged": False
                    },
                    {
                        "id": "alert_002",
                        "severity": "info",
                        "title": "Low Engagement",
                        "description": "Engagement score below average",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                        "acknowledged": True
                    }
                ],
                "total_alerts": 2,
                "unacknowledged_count": 1,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Alert list widget data generation failed: {str(e)}")
            return {"error": str(e)}


class SessionMonitoringDashboard:
    """Main session monitoring dashboard system"""    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.metrics_engine = MetricsCollectionEngine(self.config)
        self.anomaly_engine = AnomalyDetectionEngine(self.config)
        self.alerting_engine = AlertingEngine(self.config)
        self.data_provider = DashboardDataProvider(self.config)
        self.websocket_manager = WebSocketManager()
        self.cache_manager = CacheManager()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Dashboard views and widgets
        self.dashboard_views: Dict[str, DashboardView] = {}
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        """Start real-time monitoring"""        
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Session monitoring started")
            
        except Exception as e:
            self.logger.error(f"Monitoring start failed: {str(e)}")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""        
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Session monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Monitoring stop failed: {str(e)}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""        
        try:
            while self.monitoring_active:
                # Get all active sessions
                active_sessions = await self._get_active_sessions()
                
                for session_id in active_sessions:
                    try:
                        # Get session metrics
                        metrics_data = await self.metrics_engine.get_session_metrics(
                            session_id,
                            time_range=TimeRange.LAST_15_MIN
                        )
                        
                        # Detect anomalies
                        anomalies = []
                        if self.config.enable_anomaly_detection:
                            anomalies = await self.anomaly_engine.detect_anomalies(
                                session_id,
                                metrics_data
                            )
                        
                        # Evaluate alerts
                        user_id = await self._get_session_user_id(session_id)
                        alerts = await self.alerting_engine.evaluate_alerts(
                            session_id,
                            user_id,
                            metrics_data,
                            anomalies
                        )
                        
                        # Broadcast real-time updates
                        if metrics_data or alerts:
                            await self._broadcast_real_time_updates(
                                session_id,
                                metrics_data,
                                alerts,
                                anomalies
                            )
                            
                    except Exception as e:
                        self.logger.error(f"Session monitoring failed for {session_id}: {str(e)}")
                
                # Wait for next iteration
                await asyncio.sleep(self.config.alert_evaluation_interval)
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Monitoring loop failed: {str(e)}")
    
    async def _get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""        
        try:
            # This would query the database for active sessions
            # For now, return sessions that have metrics
            return list(self.metrics_engine.session_metrics.keys())
            
        except Exception as e:
            self.logger.error(f"Active sessions retrieval failed: {str(e)}")
            return []
    
    async def _get_session_user_id(self, session_id: str) -> str:
        """Get user ID for session"""        
        try:
            # This would query the database
            # For now, return a default value
            return "default_user"
            
        except Exception as e:
            self.logger.error(f"Session user ID retrieval failed: {str(e)}")
            return "unknown"
    
    async def _broadcast_real_time_updates(
        self,
        session_id: str,
        metrics_data: Dict[str, List[SessionMetric]],
        alerts: List[SessionAlert],
        anomalies: List[Dict[str, Any]]
    ):
        """Broadcast real-time updates to connected clients"""        
        try:
            update_data = {
                "type": "real_time_update",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {},
                "alerts": [alert.dict() for alert in alerts],
                "anomalies": anomalies
            }
            
            # Include latest metric values
            for metric_name, metrics_list in metrics_data.items():
                if metrics_list:
                    latest_metric = metrics_list[-1]
                    update_data["metrics"][metric_name] = {
                        "value": latest_metric.metric_value,
                        "unit": latest_metric.metric_unit,
                        "timestamp": latest_metric.timestamp.isoformat()
                    }
            
            # Broadcast to connected clients
            await self.websocket_manager.broadcast(
                f"monitoring:{session_id}",
                update_data
            )
            
        except Exception as e:
            self.logger.error(f"Real-time update broadcast failed: {str(e)}")
    
    async def create_dashboard_view(
        self,
        user_id: str,
        view_name: str,
        view_type: DashboardViewType,
        widgets: List[DashboardWidget] = None
    ) -> DashboardView:
        """Create new dashboard view"""        
        try:
            dashboard_view = DashboardView(
                view_name=view_name,
                view_type=view_type,
                user_id=user_id,
                widgets=widgets or []
            )
            
            self.dashboard_views[dashboard_view.view_id] = dashboard_view
            
            # Cache dashboard view
            cache_key = f"dashboard_view:{dashboard_view.view_id}"
            await self.cache_manager.set(
                cache_key,
                dashboard_view.json(),
                ttl=3600
            )
            
            self.logger.info(f"Dashboard view created: {dashboard_view.view_id}")
            
            return dashboard_view
            
        except Exception as e:
            self.logger.error(f"Dashboard view creation failed: {str(e)}")
            raise
    
    async def get_dashboard_data(
        self,
        view_id: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get complete dashboard data"""        
        try:
            if view_id not in self.dashboard_views:
                return {"error": "Dashboard view not found"}
            
            dashboard_view = self.dashboard_views[view_id]
            
            # Get data for each widget
            widgets_data = []
            
            for widget in dashboard_view.widgets:
                widget_data = await self.data_provider.get_widget_data(
                    widget,
                    session_id,
                    user_id
                )
                
                widgets_data.append({
                    "widget_id": widget.widget_id,
                    "widget_type": widget.widget_type,
                    "title": widget.title,
                    "position": widget.position,
                    "data": widget_data
                })
            
            return {
                "view_id": view_id,
                "view_name": dashboard_view.view_name,
                "view_type": dashboard_view.view_type.value,
                "layout": dashboard_view.layout,
                "widgets": widgets_data,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard data retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    async def record_session_metric(
        self,
        session_id: str,
        user_id: str,
        metric_type: MetricType,
        metric_name: str,
        metric_value: float,
        metric_unit: str = "",
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Record a session metric"""        
        try:
            metric = await self.metrics_engine.collect_session_metric(
                session_id,
                user_id,
                metric_type,
                metric_name,
                metric_value,
                metric_unit,
                tags,
                metadata
            )
            
            return metric is not None
            
        except Exception as e:
            self.logger.error(f"Session metric recording failed: {str(e)}")
            return False
    
    async def get_session_analytics(self, session_id: str) -> Optional[SessionAnalytics]:
        """Get comprehensive session analytics"""        
        try:
            # Get metrics data
            metrics_data = await self.metrics_engine.get_session_metrics(
                session_id,
                time_range=TimeRange.LAST_24_HOURS
            )
            
            if not metrics_data:
                return None
            
            # Calculate analytics
            analytics = SessionAnalytics(
                session_id=session_id,
                user_id=await self._get_session_user_id(session_id),
                session_duration=await self.metrics_engine.aggregate_metrics(
                    session_id, "session_duration", "max"
                ),
                engagement_score=await self.metrics_engine.aggregate_metrics(
                    session_id, "engagement_score", "avg"
                ),
                performance_score=await self.metrics_engine.aggregate_metrics(
                    session_id, "performance_score", "avg"
                ),
                revenue_generated=await self.metrics_engine.aggregate_metrics(
                    session_id, "revenue", "sum"
                ),
                content_interactions=int(await self.metrics_engine.aggregate_metrics(
                    session_id, "content_interactions", "sum"
                )),
                error_count=int(await self.metrics_engine.aggregate_metrics(
                    session_id, "error_count", "sum"
                )),
                average_response_time=await self.metrics_engine.aggregate_metrics(
                    session_id, "response_time", "avg"
                ),
                peak_concurrent_users=int(await self.metrics_engine.aggregate_metrics(
                    session_id, "concurrent_users", "max"
                )),
                bandwidth_usage=await self.metrics_engine.aggregate_metrics(
                    session_id, "bandwidth_usage", "sum"
                ),
                cpu_usage_avg=await self.metrics_engine.aggregate_metrics(
                    session_id, "cpu_usage", "avg"
                ),
                memory_usage_avg=await self.metrics_engine.aggregate_metrics(
                    session_id, "memory_usage", "avg"
                )
            )
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Session analytics calculation failed: {str(e)}")
            return None
    
    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard statistics"""        
        try:
            active_sessions_count = len(await self._get_active_sessions())
            total_metrics_count = sum(
                len(metrics) for session_metrics in self.metrics_engine.session_metrics.values()
                for metrics in session_metrics.values()
            )
            active_alerts_count = len(self.alerting_engine.active_alerts)
            dashboard_views_count = len(self.dashboard_views)
            
            return {
                "monitoring_active": self.monitoring_active,
                "active_sessions": active_sessions_count,
                "total_metrics": total_metrics_count,
                "active_alerts": active_alerts_count,
                "dashboard_views": dashboard_views_count,
                "configuration": {
                    "real_time_monitoring": self.config.enable_real_time_monitoring,
                    "anomaly_detection": self.config.enable_anomaly_detection,
                    "predictive_alerts": self.config.enable_predictive_alerts,
                    "collection_interval": self.config.metric_collection_interval,
                    "evaluation_interval": self.config.alert_evaluation_interval
                }
            }
            
        except Exception as e:
            self.logger.error(f"Monitoring statistics calculation failed: {str(e)}")
            return {}
