"""AI Model Monitoring and Performance Tracking
==============================================

Advanced AI model monitoring system for tracking model performance, drift detection,
and automated model health assessments in production environments.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTATION:
- Lead Dev IA: Advanced AI monitoring architecture
- ML Engineer: Model performance and drift detection algorithms
- DevOps: Production monitoring and alerting integration
- Backend Senior: High-performance data processing pipelines
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class ModelHealthStatus(Enum):
    """Model health status indicators."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class ModelMetrics:
    """Model performance metrics container."""
    model_id: str
    timestamp: datetime
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    latency_ms: Optional[float] = None
    throughput_rps: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    error_rate: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class DriftAlert:
    """Model drift alert information."""
    model_id: str
    alert_id: str
    severity: AlertSeverity
    drift_type: str
    drift_score: float
    threshold: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False

class ModelMonitoring:
    """Enterprise-grade AI model monitoring and performance tracking system."""
    
    def __init__(self, database_connection=None, alert_thresholds=None) -> None:
        """Initialize model monitoring system.
        
        Args:
            database_connection: MongoDB connection for storing metrics
            alert_thresholds: Custom alert thresholds configuration
        """
        self.db = database_connection
        self.logger = logger
        self._metrics_history: Dict[str, List[ModelMetrics]] = {}
        self._alerts: List[DriftAlert] = []
        self._baseline_metrics: Dict[str, ModelMetrics] = {}
        
        # Default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            'accuracy_drop': 0.05,  # 5% accuracy drop
            'latency_increase': 2.0,  # 2x latency increase
            'error_rate_spike': 0.10,  # 10% error rate
            'drift_threshold': 0.15,  # 15% data drift
            'memory_usage': 1000,  # 1GB memory usage
            'cpu_usage': 80  # 80% CPU usage
        }
        
        # Performance tracking
        self._monitoring_active = False
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    async def register_model(self, model_id: str, baseline_metrics: ModelMetrics) -> bool:
        """Register a new model for monitoring.
        
        Args:
            model_id: Unique model identifier
            baseline_metrics: Initial baseline performance metrics
            
        Returns:
            bool: Success status
        """
        try:
            self._baseline_metrics[model_id] = baseline_metrics
            self._metrics_history[model_id] = [baseline_metrics]
            
            # Store in database if available
            if self.db:
                await self._store_baseline_metrics(model_id, baseline_metrics)
            
            self.logger.info(f"Model {model_id} registered for monitoring")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering model {model_id}: {e}")
            return False
    
    async def record_metrics(self, metrics: ModelMetrics) -> bool:
        """Record new model performance metrics.
        
        Args:
            metrics: Current model performance metrics
            
        Returns:
            bool: Success status
        """
        try:
            model_id = metrics.model_id
            
            # Add to history
            if model_id not in self._metrics_history:
                self._metrics_history[model_id] = []
            
            self._metrics_history[model_id].append(metrics)
            
            # Limit history size (keep last 1000 entries)
            if len(self._metrics_history[model_id]) > 1000:
                self._metrics_history[model_id] = self._metrics_history[model_id][-1000:]
            
            # Store in database
            if self.db:
                await self._store_metrics(metrics)
            
            # Check for alerts
            await self._check_alerts(metrics)
            
            self.logger.debug(f"Recorded metrics for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording metrics: {e}")
            return False
    
    async def detect_drift(self, model_id: str, current_metrics: ModelMetrics) -> Dict[str, Any]:
        """Detect model drift based on performance degradation.
        
        Args:
            model_id: Model identifier
            current_metrics: Current performance metrics
            
        Returns:
            dict: Drift detection results
        """
        try:
            if model_id not in self._baseline_metrics:
                return {"error": "Model not registered for monitoring"}
            
            baseline = self._baseline_metrics[model_id]
            drift_results = {
                "model_id": model_id,
                "timestamp": current_metrics.timestamp.isoformat(),
                "drift_detected": False,
                "drift_score": 0.0,
                "details": {}
            }
            
            # Calculate drift scores for different metrics
            drift_scores = {}
            
            if baseline.accuracy and current_metrics.accuracy:
                accuracy_drift = abs(baseline.accuracy - current_metrics.accuracy)
                drift_scores['accuracy'] = accuracy_drift / baseline.accuracy
            
            if baseline.latency_ms and current_metrics.latency_ms:
                latency_drift = abs(current_metrics.latency_ms - baseline.latency_ms)
                drift_scores['latency'] = latency_drift / baseline.latency_ms
            
            if baseline.error_rate and current_metrics.error_rate:
                error_drift = abs(current_metrics.error_rate - baseline.error_rate)
                drift_scores['error_rate'] = error_drift
            
            # Calculate overall drift score
            if drift_scores:
                overall_drift = statistics.mean(drift_scores.values())
                drift_results["drift_score"] = overall_drift
                drift_results["details"] = drift_scores
                
                # Check if drift exceeds threshold
                if overall_drift > self.alert_thresholds['drift_threshold']:
                    drift_results["drift_detected"] = True
                    
                    # Create drift alert
                    alert = DriftAlert(
                        model_id=model_id,
                        alert_id=f"drift_{model_id}_{int(time.time())}",
                        severity=AlertSeverity.WARNING if overall_drift < 0.3 else AlertSeverity.CRITICAL,
                        drift_type="performance_drift",
                        drift_score=overall_drift,
                        threshold=self.alert_thresholds['drift_threshold'],
                        timestamp=current_metrics.timestamp,
                        details=drift_scores
                    )
                    
                    self._alerts.append(alert)
                    await self._send_alert(alert)
            
            return drift_results
            
        except Exception as e:
            self.logger.error(f"Error detecting drift for model {model_id}: {e}")
            return {"error": str(e)}
    
    async def get_model_health(self, model_id: str) -> Dict[str, Any]:
        """Get current model health status.
        
        Args:
            model_id: Model identifier
            
        Returns:
            dict: Model health information
        """
        try:
            if model_id not in self._metrics_history:
                return {"error": "Model not found"}
            
            recent_metrics = self._metrics_history[model_id][-10:]  # Last 10 entries
            
            if not recent_metrics:
                return {"error": "No metrics available"}
            
            latest_metrics = recent_metrics[-1]
            
            # Calculate health score based on various factors
            health_score = 100.0
            health_factors = []
            
            # Check accuracy
            if latest_metrics.accuracy:
                if model_id in self._baseline_metrics and self._baseline_metrics[model_id].accuracy:
                    accuracy_ratio = latest_metrics.accuracy / self._baseline_metrics[model_id].accuracy
                    if accuracy_ratio < 0.9:
                        health_score -= 20
                        health_factors.append("accuracy_degradation")
            
            # Check latency
            if latest_metrics.latency_ms:
                if model_id in self._baseline_metrics and self._baseline_metrics[model_id].latency_ms:
                    latency_ratio = latest_metrics.latency_ms / self._baseline_metrics[model_id].latency_ms
                    if latency_ratio > 2.0:
                        health_score -= 15
                        health_factors.append("high_latency")
            
            # Check error rate
            if latest_metrics.error_rate and latest_metrics.error_rate > 0.1:
                health_score -= 25
                health_factors.append("high_error_rate")
            
            # Check resource usage
            if latest_metrics.memory_usage_mb and latest_metrics.memory_usage_mb > 1000:
                health_score -= 10
                health_factors.append("high_memory_usage")
            
            if latest_metrics.cpu_usage_percent and latest_metrics.cpu_usage_percent > 80:
                health_score -= 10
                health_factors.append("high_cpu_usage")
            
            # Determine health status
            if health_score >= 90:
                status = ModelHealthStatus.HEALTHY
            elif health_score >= 70:
                status = ModelHealthStatus.WARNING
            elif health_score >= 50:
                status = ModelHealthStatus.CRITICAL
            else:
                status = ModelHealthStatus.FAILED
            
            return {
                "model_id": model_id,
                "health_status": status.value,
                "health_score": max(0, health_score),
                "health_factors": health_factors,
                "latest_metrics": {
                    "timestamp": latest_metrics.timestamp.isoformat(),
                    "accuracy": latest_metrics.accuracy,
                    "latency_ms": latest_metrics.latency_ms,
                    "error_rate": latest_metrics.error_rate,
                    "memory_usage_mb": latest_metrics.memory_usage_mb,
                    "cpu_usage_percent": latest_metrics.cpu_usage_percent
                },
                "active_alerts": len([a for a in self._alerts if a.model_id == model_id and not a.resolved])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model health for {model_id}: {e}")
            return {"error": str(e)}
    
    async def get_performance_trends(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Get performance trends for a model over time.
        
        Args:
            model_id: Model identifier
            days: Number of days to analyze
            
        Returns:
            dict: Performance trend analysis
        """
        try:
            if model_id not in self._metrics_history:
                return {"error": "Model not found"}
            
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            recent_metrics = [
                m for m in self._metrics_history[model_id]
                if m.timestamp >= cutoff_time
            ]
            
            if len(recent_metrics) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            # Calculate trends
            trends = {}
            
            # Accuracy trend
            accuracy_values = [m.accuracy for m in recent_metrics if m.accuracy is not None]
            if len(accuracy_values) >= 2:
                trends['accuracy'] = self._calculate_trend(accuracy_values)
            
            # Latency trend
            latency_values = [m.latency_ms for m in recent_metrics if m.latency_ms is not None]
            if len(latency_values) >= 2:
                trends['latency'] = self._calculate_trend(latency_values)
            
            # Error rate trend
            error_values = [m.error_rate for m in recent_metrics if m.error_rate is not None]
            if len(error_values) >= 2:
                trends['error_rate'] = self._calculate_trend(error_values)
            
            # Throughput trend
            throughput_values = [m.throughput_rps for m in recent_metrics if m.throughput_rps is not None]
            if len(throughput_values) >= 2:
                trends['throughput'] = self._calculate_trend(throughput_values)
            
            return {
                "model_id": model_id,
                "analysis_period_days": days,
                "data_points": len(recent_metrics),
                "trends": trends,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating trends for model {model_id}: {e}")
            return {"error": str(e)}
    
    async def start_continuous_monitoring(self, model_id: str, interval_seconds: int = 300) -> bool:
        """Start continuous monitoring for a model.
        
        Args:
            model_id: Model identifier
            interval_seconds: Monitoring interval in seconds
            
        Returns:
            bool: Success status
        """
        try:
            if model_id in self._monitoring_tasks:
                self.logger.warning(f"Monitoring already active for model {model_id}")
                return True
            
            async def monitor_loop() -> None:
                while self._monitoring_active:
                    try:
                        # This would typically collect metrics from the model service
                        # For now, we'll just log that monitoring is active
                        self.logger.debug(f"Monitoring model {model_id}")
                        await asyncio.sleep(interval_seconds)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        self.logger.error(f"Error in monitoring loop for {model_id}: {e}")
                        await asyncio.sleep(interval_seconds)
            
            self._monitoring_active = True
            task = asyncio.create_task(monitor_loop())
            self._monitoring_tasks[model_id] = task
            
            self.logger.info(f"Started continuous monitoring for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring for model {model_id}: {e}")
            return False
    
    async def stop_continuous_monitoring(self, model_id: str) -> bool:
        """Stop continuous monitoring for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            bool: Success status
        """
        try:
            if model_id in self._monitoring_tasks:
                self._monitoring_tasks[model_id].cancel()
                del self._monitoring_tasks[model_id]
                self.logger.info(f"Stopped continuous monitoring for model {model_id}")
            
            if not self._monitoring_tasks:
                self._monitoring_active = False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring for model {model_id}: {e}")
            return False
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and magnitude for a series of values."""
        if len(values) < 2:
            return {"direction": "unknown", "magnitude": 0.0}
        
        # Simple linear trend calculation
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        change = (second_half - first_half) / first_half if first_half != 0 else 0
        
        if abs(change) < 0.05:  # Less than 5% change
            direction = "stable"
        elif change > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "magnitude": abs(change),
            "change_percent": change * 100
        }
    
    async def _check_alerts(self, metrics: ModelMetrics) -> None:
        """Check for alert conditions based on current metrics."""
        try:
            model_id = metrics.model_id
            
            # Check various alert conditions
            alerts_to_create = []
            
            # Accuracy drop alert
            if (model_id in self._baseline_metrics and 
                metrics.accuracy and self._baseline_metrics[model_id].accuracy):
                accuracy_drop = self._baseline_metrics[model_id].accuracy - metrics.accuracy
                if accuracy_drop > self.alert_thresholds['accuracy_drop']:
                    alerts_to_create.append({
                        "type": "accuracy_drop",
                        "severity": AlertSeverity.WARNING,
                        "details": {"drop": accuracy_drop, "current": metrics.accuracy}
                    })
            
            # High latency alert
            if metrics.latency_ms and metrics.latency_ms > 5000:  # 5 seconds
                alerts_to_create.append({
                    "type": "high_latency",
                    "severity": AlertSeverity.WARNING,
                    "details": {"latency_ms": metrics.latency_ms}
                })
            
            # High error rate alert
            if metrics.error_rate and metrics.error_rate > self.alert_thresholds['error_rate_spike']:
                alerts_to_create.append({
                    "type": "high_error_rate",
                    "severity": AlertSeverity.CRITICAL,
                    "details": {"error_rate": metrics.error_rate}
                })
            
            # Resource usage alerts
            if metrics.memory_usage_mb and metrics.memory_usage_mb > self.alert_thresholds['memory_usage']:
                alerts_to_create.append({
                    "type": "high_memory_usage",
                    "severity": AlertSeverity.WARNING,
                    "details": {"memory_mb": metrics.memory_usage_mb}
                })
            
            if metrics.cpu_usage_percent and metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage']:
                alerts_to_create.append({
                    "type": "high_cpu_usage",
                    "severity": AlertSeverity.WARNING,
                    "details": {"cpu_percent": metrics.cpu_usage_percent}
                })
            
            # Create alerts
            for alert_data in alerts_to_create:
                alert = DriftAlert(
                    model_id=model_id,
                    alert_id=f"{alert_data['type']}_{model_id}_{int(time.time())}",
                    severity=alert_data['severity'],
                    drift_type=alert_data['type'],
                    drift_score=0.0,  # Not applicable for these alerts
                    threshold=0.0,  # Not applicable for these alerts
                    timestamp=metrics.timestamp,
                    details=alert_data['details']
                )
                
                self._alerts.append(alert)
                await self._send_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    async def _send_alert(self, alert: DriftAlert) -> None:
        """Send alert notification."""
        try:
            # Log alert (in production, this would send to monitoring systems)
            self.logger.warning(
                f"MODEL ALERT [{alert.severity.value.upper()}] "
                f"Model: {alert.model_id}, Type: {alert.drift_type}, "
                f"Details: {alert.details}"
            )
            
            # Store alert in database if available
            if self.db:
                await self._store_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    async def _store_metrics(self, metrics: ModelMetrics) -> None:
        """Store metrics in database."""
        if not self.db:
            return
        
        try:
            # Convert to document format
            doc = {
                "model_id": metrics.model_id,
                "timestamp": metrics.timestamp,
                "metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "latency_ms": metrics.latency_ms,
                    "throughput_rps": metrics.throughput_rps,
                    "memory_usage_mb": metrics.memory_usage_mb,
                    "cpu_usage_percent": metrics.cpu_usage_percent,
                    "error_rate": metrics.error_rate,
                    "custom_metrics": metrics.custom_metrics
                }
            }
            
            # Store in metrics collection
            await self.db.model_metrics.insert_one(doc)
            
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    async def _store_baseline_metrics(self, model_id: str, metrics: ModelMetrics) -> None:
        """Store baseline metrics in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "model_id": model_id,
                "baseline_metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "latency_ms": metrics.latency_ms,
                    "throughput_rps": metrics.throughput_rps,
                    "memory_usage_mb": metrics.memory_usage_mb,
                    "cpu_usage_percent": metrics.cpu_usage_percent,
                    "error_rate": metrics.error_rate,
                    "custom_metrics": metrics.custom_metrics
                },
                "created_at": metrics.timestamp
            }
            
            # Upsert baseline
            await self.db.model_baselines.replace_one(
                {"model_id": model_id},
                doc,
                upsert=True
            )
            
        except Exception as e:
            self.logger.error(f"Error storing baseline metrics: {e}")
    
    async def _store_alert(self, alert: DriftAlert) -> None:
        """Store alert in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "alert_id": alert.alert_id,
                "model_id": alert.model_id,
                "severity": alert.severity.value,
                "drift_type": alert.drift_type,
                "drift_score": alert.drift_score,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp,
                "details": alert.details,
                "resolved": alert.resolved
            }
            
            await self.db.model_alerts.insert_one(doc)
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")

__all__ = ['ModelMonitoring', 'ModelMetrics', 'DriftAlert', 'ModelHealthStatus', 'AlertSeverity']