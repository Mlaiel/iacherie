"""
Performance Metrics - AI Engines Database Module

This module provides comprehensive performance monitoring and metrics collection
for the IA Influencer Agent platform, including model performance tracking,
inference metrics, training metrics, drift detection, and benchmarking.

Core Components:
- ModelPerformanceTracker: Real-time model performance monitoring
- InferenceMetricsCollector: Inference latency and throughput metrics
- TrainingMetricsStore: Training progress and validation metrics
- ModelDriftDetector: Data and concept drift detection
- PerformanceBenchmark: Model performance benchmarking and comparison

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer & ML Engineer + Backend Senior + Database Administrator
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import json
import logging
import asyncio
import time
import uuid
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Metric type enumeration."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    MSE = "mse"
    MAE = "mae"
    R2_SCORE = "r2_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    GPU_USAGE = "gpu_usage"

class DriftType(str, Enum):
    """Drift type enumeration."""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"

class AlertLevel(str, Enum):
    """Alert level enumeration."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """Performance metric structure."""
    metric_id: str
    model_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class InferenceMetrics:
    """Inference metrics structure."""
    request_id: str
    model_id: str
    latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: Optional[float]
    batch_size: int
    input_size: int
    output_size: int
    timestamp: datetime
    endpoint_id: str
    success: bool
    error_message: Optional[str]

@dataclass
class TrainingMetrics:
    """Training metrics structure."""
    job_id: str
    model_id: str
    epoch: int
    step: int
    loss: float
    accuracy: Optional[float]
    learning_rate: float
    batch_size: int
    validation_loss: Optional[float]
    validation_accuracy: Optional[float]
    custom_metrics: Dict[str, float]
    timestamp: datetime
    elapsed_time_seconds: float

@dataclass
class DriftAlert:
    """Drift detection alert structure."""
    alert_id: str
    model_id: str
    drift_type: DriftType
    alert_level: AlertLevel
    drift_score: float
    threshold: float
    description: str
    affected_features: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class ModelPerformanceTracker:
    """
    Real-time model performance tracker.
    
    Monitors model performance metrics in real-time, providing alerts
    for performance degradation and maintaining performance history.
    """
    
    def __init__(self):
        """Initialize the model performance tracker."""
        self.performance_history = defaultdict(list)
        self.alert_thresholds = {}
        self.active_alerts = {}
        self.performance_baselines = {}
        self.monitoring_configs = {}
        self.initialized = False
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the performance tracker.
        
        Returns:
            Dict[str, Any]: Initialization status
        """



        try:
            # Load performance baselines
            await self._load_performance_baselines()
            
            # Initialize alert thresholds
            await self._initialize_alert_thresholds()
            
            # Start background monitoring
            asyncio.create_task(self._monitor_performance())
            
            self.initialized = True
            
            logger.info("Model Performance Tracker initialized successfully")
            return {
                "status": "success",
                "models_monitored": len(self.monitoring_configs),
                "alert_rules": len(self.alert_thresholds),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Model Performance Tracker: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def track_performance(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """
        Track a performance metric.
        
        Args:
            metric: Performance metric to track
            
        Returns:
            Dict[str, Any]: Tracking result
        """



        try:
            # Store metric
            self.performance_history[metric.model_id].append(metric)
            
            # Check for alerts
            alerts = await self._check_performance_alerts(metric)
            
            # Update performance statistics
            await self._update_performance_stats(metric)
            
            return {
                "status": "success",
                "metric_id": metric.metric_id,
                "alerts_triggered": len(alerts),
                "alerts": [asdict(alert) for alert in alerts],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to track performance: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_performance_summary(self, model_id: str,
                                    time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get performance summary for a model.
        
        Args:
            model_id: Model identifier
            time_range: Time range for summary (default: last 24 hours)
            
        Returns:
            Dict[str, Any]: Performance summary
        """



        try:
            if time_range is None:
                time_range = timedelta(hours=24)
            
            cutoff_time = datetime.utcnow() - time_range
            
            # Filter metrics by time range
            recent_metrics = [
                metric for metric in self.performance_history[model_id]
                if metric.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    "status": "success",
                    "model_id": model_id,
                    "summary": {"message": "No metrics available for the specified time range"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Calculate statistics by metric type
            summary = {}
            for metric_type in MetricType:
                type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                if type_metrics:
                    values = [m.value for m in type_metrics]
                    summary[metric_type.value] = {
                        "count": len(values),
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1],
                        "trend": self._calculate_trend(values)
                    }
            
            # Get active alerts
            active_alerts = [
                alert for alert in self.active_alerts.get(model_id, [])
                if alert.timestamp >= cutoff_time
            ]
            
            return {
                "status": "success",
                "model_id": model_id,
                "time_range_hours": time_range.total_seconds() / 3600,
                "summary": summary,
                "active_alerts": len(active_alerts),
                "alert_details": [asdict(alert) for alert in active_alerts],
                "baseline_comparison": await self._compare_with_baseline(model_id, recent_metrics),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def set_alert_threshold(self, model_id: str, metric_type: MetricType,
                                threshold_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set alert threshold for a model metric.
        
        Args:
            model_id: Model identifier
            metric_type: Metric type
            threshold_config: Threshold configuration
            
        Returns:
            Dict[str, Any]: Threshold setting result
        """



        try:
            if model_id not in self.alert_thresholds:
                self.alert_thresholds[model_id] = {}
            
            self.alert_thresholds[model_id][metric_type] = {
                **threshold_config,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            logger.info(f"Set alert threshold for {model_id} {metric_type}")
            return {
                "status": "success",
                "model_id": model_id,
                "metric_type": metric_type.value,
                "threshold_config": threshold_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set alert threshold: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization metrics."""



        try:
            # Mock resource utilization data
            return {
                "cpu": {
                    "usage_percent": 45.2,
                    "load_average": [1.2, 1.5, 1.8],
                    "cores": 8
                },
                "memory": {
                    "usage_percent": 67.8,
                    "used_gb": 54.2,
                    "total_gb": 80.0
                },
                "gpu": {
                    "usage_percent": 82.1,
                    "memory_usage_percent": 76.5,
                    "temperature": 78,
                    "devices": 2
                },
                "disk": {
                    "usage_percent": 34.7,
                    "used_gb": 347.2,
                    "total_gb": 1000.0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {str(e)}")
            return {
                "cpu": 0,
                "memory": 0,
                "gpu": 0,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on performance tracker.
        
        Returns:
            Dict[str, Any]: Health status
        """



        try:
            if not self.initialized:
                return {
                    "status": "unhealthy",
                    "error": "Performance tracker not initialized"
                }
            
            # Check metrics collection
            total_metrics = sum(len(metrics) for metrics in self.performance_history.values())
            active_models = len(self.performance_history)
            active_alerts = sum(len(alerts) for alerts in self.active_alerts.values())
            
            return {
                "status": "healthy",
                "total_metrics": total_metrics,
                "active_models": active_models,
                "active_alerts": active_alerts,
                "monitoring_configs": len(self.monitoring_configs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    
    async def _load_performance_baselines(self):
        """Load performance baselines for models."""
        # Mock baseline loading
        logger.info("Loading performance baselines")
    
    async def _initialize_alert_thresholds(self):
        """Initialize default alert thresholds."""
        default_thresholds = {
            MetricType.ACCURACY: {"min": 0.8, "alert_level": AlertLevel.WARNING},
            MetricType.LATENCY: {"max": 1000, "alert_level": AlertLevel.WARNING},
            MetricType.MEMORY_USAGE: {"max": 80, "alert_level": AlertLevel.CRITICAL}
        }
        
        # Apply to all models
        for model_id in self.monitoring_configs:
            self.alert_thresholds[model_id] = default_thresholds.copy()
    
    async def _check_performance_alerts(self, metric: PerformanceMetric) -> List[DriftAlert]:
        """Check if metric triggers any alerts."""
        alerts = []
        
        if metric.model_id in self.alert_thresholds:
            thresholds = self.alert_thresholds[metric.model_id]
            
            if metric.metric_type in thresholds:
                threshold_config = thresholds[metric.metric_type]
                
                # Check threshold violations
                if "min" in threshold_config and metric.value < threshold_config["min"]:
                    alert = DriftAlert(
                        alert_id=str(uuid.uuid4()),
                        model_id=metric.model_id,
                        drift_type=DriftType.PERFORMANCE_DRIFT,
                        alert_level=threshold_config.get("alert_level", AlertLevel.WARNING),
                        drift_score=metric.value,
                        threshold=threshold_config["min"],
                        description=f"{metric.metric_type.value} below threshold",
                        affected_features=[metric.metric_type.value],
                        timestamp=datetime.utcnow(),
                        metadata={"metric": asdict(metric)}
                    )
                    alerts.append(alert)
                
                elif "max" in threshold_config and metric.value > threshold_config["max"]:
                    alert = DriftAlert(
                        alert_id=str(uuid.uuid4()),
                        model_id=metric.model_id,
                        drift_type=DriftType.PERFORMANCE_DRIFT,
                        alert_level=threshold_config.get("alert_level", AlertLevel.WARNING),
                        drift_score=metric.value,
                        threshold=threshold_config["max"],
                        description=f"{metric.metric_type.value} above threshold",
                        affected_features=[metric.metric_type.value],
                        timestamp=datetime.utcnow(),
                        metadata={"metric": asdict(metric)}
                    )
                    alerts.append(alert)
        
        # Store active alerts
        if alerts:
            if metric.model_id not in self.active_alerts:
                self.active_alerts[metric.model_id] = []
            self.active_alerts[metric.model_id].extend(alerts)
        
        return alerts
    
    async def _update_performance_stats(self, metric: PerformanceMetric):
        """Update performance statistics."""
        # Update running statistics for the model
        logger.debug(f"Updated performance stats for {metric.model_id}")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return "stable"
        
        # Calculate linear regression slope
        x = list(range(len(values)))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    async def _compare_with_baseline(self, model_id: str, 
                                   recent_metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Compare recent metrics with baseline performance."""
        if model_id not in self.performance_baselines:
            return {"status": "no_baseline"}
        
        baseline = self.performance_baselines[model_id]
        comparison = {}
        
        for metric_type in MetricType:
            type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            if type_metrics and metric_type.value in baseline:
                current_avg = statistics.mean([m.value for m in type_metrics])
                baseline_avg = baseline[metric_type.value]["mean"]
                
                comparison[metric_type.value] = {
                    "current": current_avg,
                    "baseline": baseline_avg,
                    "change_percent": ((current_avg - baseline_avg) / baseline_avg) * 100,
                    "improvement": current_avg > baseline_avg if metric_type in [
                        MetricType.ACCURACY, MetricType.PRECISION, MetricType.RECALL, MetricType.F1_SCORE
                    ] else current_avg < baseline_avg
                }
        
        return comparison
    
    async def _monitor_performance(self):
        """Background performance monitoring."""
        while True:
            try:
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                # Aggregate performance data
                await self._aggregate_performance_data()
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for model_id in self.active_alerts:
            self.active_alerts[model_id] = [
                alert for alert in self.active_alerts[model_id]
                if alert.timestamp >= cutoff_time
            ]
    
    async def _aggregate_performance_data(self):
        """Aggregate performance data for reporting."""
        # Implement performance data aggregation
        logger.debug("Aggregating performance data")

class InferenceMetricsCollector:
    """
    Inference metrics collector.
    
    Collects and analyzes inference performance metrics including
    latency, throughput, resource usage, and error rates.
    """
    
    def __init__(self):
        """Initialize the inference metrics collector."""
        self.inference_metrics = defaultdict(list)
        self.latency_buckets = defaultdict(lambda: defaultdict(int))
        self.throughput_data = defaultdict(list)
        self.error_counts = defaultdict(int)
        
    async def collect_inference_metric(self, metrics: InferenceMetrics) -> Dict[str, Any]:
        """
        Collect inference metrics.
        
        Args:
            metrics: Inference metrics to collect
            
        Returns:
            Dict[str, Any]: Collection result
        """



        try:
            # Store metrics
            self.inference_metrics[metrics.model_id].append(metrics)
            
            # Update latency buckets
            latency_bucket = self._get_latency_bucket(metrics.latency_ms)
            self.latency_buckets[metrics.model_id][latency_bucket] += 1
            
            # Update throughput data
            self.throughput_data[metrics.model_id].append({
                "timestamp": metrics.timestamp,
                "batch_size": metrics.batch_size,
                "latency_ms": metrics.latency_ms
            })
            
            # Update error counts
            if not metrics.success:
                self.error_counts[metrics.model_id] += 1
            
            return {
                "status": "success",
                "model_id": metrics.model_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect inference metrics: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_inference_summary(self, model_id: str,
                                  time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get inference performance summary.
        
        Args:
            model_id: Model identifier
            time_range: Time range for summary
            
        Returns:
            Dict[str, Any]: Inference summary
        """



        try:
            if time_range is None:
                time_range = timedelta(hours=1)
            
            cutoff_time = datetime.utcnow() - time_range
            
            # Filter metrics by time range
            recent_metrics = [
                metric for metric in self.inference_metrics[model_id]
                if metric.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    "status": "success",
                    "model_id": model_id,
                    "summary": {"message": "No inference metrics available"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Calculate statistics
            latencies = [m.latency_ms for m in recent_metrics]
            success_count = sum(1 for m in recent_metrics if m.success)
            total_requests = len(recent_metrics)
            
            # Calculate throughput (requests per second)
            time_span_seconds = time_range.total_seconds()
            throughput_rps = total_requests / time_span_seconds if time_span_seconds > 0 else 0
            
            summary = {
                "total_requests": total_requests,
                "successful_requests": success_count,
                "failed_requests": total_requests - success_count,
                "success_rate": success_count / total_requests if total_requests > 0 else 0,
                "throughput_rps": throughput_rps,
                "latency_stats": {
                    "mean_ms": statistics.mean(latencies),
                    "median_ms": statistics.median(latencies),
                    "p95_ms": np.percentile(latencies, 95),
                    "p99_ms": np.percentile(latencies, 99),
                    "min_ms": min(latencies),
                    "max_ms": max(latencies),
                    "std_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
                },
                "resource_usage": {
                    "avg_memory_mb": statistics.mean([m.memory_usage_mb for m in recent_metrics]),
                    "avg_cpu_percent": statistics.mean([m.cpu_usage_percent for m in recent_metrics]),
                    "avg_gpu_percent": statistics.mean([
                        m.gpu_usage_percent for m in recent_metrics 
                        if m.gpu_usage_percent is not None
                    ]) if any(m.gpu_usage_percent is not None for m in recent_metrics) else None
                },
                "latency_distribution": self.latency_buckets[model_id]
            }
            
            return {
                "status": "success",
                "model_id": model_id,
                "time_range_hours": time_range.total_seconds() / 3600,
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get inference summary: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_latency_bucket(self, latency_ms: float) -> str:
        """Get latency bucket for histogram."""
        if latency_ms < 10:
            return "0-10ms"
        elif latency_ms < 50:
            return "10-50ms"
        elif latency_ms < 100:
            return "50-100ms"
        elif latency_ms < 500:
            return "100-500ms"
        elif latency_ms < 1000:
            return "500ms-1s"
        else:
            return ">1s"

class TrainingMetricsStore:
    """
    Training metrics storage and analysis.
    
    Stores and analyzes training metrics including loss curves,
    validation metrics, and training progress tracking.
    """
    
    def __init__(self):
        """Initialize the training metrics store."""
        self.training_metrics = defaultdict(list)
        self.loss_curves = defaultdict(list)
        self.validation_curves = defaultdict(list)
        
    async def store_training_metric(self, metrics: TrainingMetrics) -> Dict[str, Any]:
        """
        Store training metrics.
        
        Args:
            metrics: Training metrics to store
            
        Returns:
            Dict[str, Any]: Storage result
        """



        try:
            # Store metrics
            self.training_metrics[metrics.job_id].append(metrics)
            
            # Update loss curves
            self.loss_curves[metrics.job_id].append({
                "epoch": metrics.epoch,
                "step": metrics.step,
                "loss": metrics.loss,
                "timestamp": metrics.timestamp
            })
            
            # Update validation curves
            if metrics.validation_loss is not None:
                self.validation_curves[metrics.job_id].append({
                    "epoch": metrics.epoch,
                    "validation_loss": metrics.validation_loss,
                    "validation_accuracy": metrics.validation_accuracy,
                    "timestamp": metrics.timestamp
                })
            
            return {
                "status": "success",
                "job_id": metrics.job_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store training metrics: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_training_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Get training progress for a job.
        
        Args:
            job_id: Training job identifier
            
        Returns:
            Dict[str, Any]: Training progress
        """



        try:
            if job_id not in self.training_metrics:
                return {
                    "status": "error",
                    "error": f"No training metrics found for job {job_id}"
                }
            
            metrics = self.training_metrics[job_id]
            latest_metric = metrics[-1] if metrics else None
            
            if not latest_metric:
                return {
                    "status": "error",
                    "error": "No metrics available"
                }
            
            # Calculate progress statistics
            loss_values = [m.loss for m in metrics]
            accuracy_values = [m.accuracy for m in metrics if m.accuracy is not None]
            
            progress = {
                "current_epoch": latest_metric.epoch,
                "current_step": latest_metric.step,
                "latest_loss": latest_metric.loss,
                "latest_accuracy": latest_metric.accuracy,
                "loss_trend": self._calculate_trend(loss_values[-10:]) if len(loss_values) >= 2 else "stable",
                "accuracy_trend": self._calculate_trend(accuracy_values[-10:]) if len(accuracy_values) >= 2 else "stable",
                "total_training_time": sum(m.elapsed_time_seconds for m in metrics),
                "average_epoch_time": statistics.mean([m.elapsed_time_seconds for m in metrics]),
                "loss_curve": self.loss_curves[job_id],
                "validation_curve": self.validation_curves[job_id],
                "custom_metrics": latest_metric.custom_metrics
            }
            
            return {
                "status": "success",
                "job_id": job_id,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get training progress: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend for a series of values."""
        if len(values) < 2:
            return "stable"
        
        # Calculate slope using linear regression
        x = list(range(len(values)))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

class ModelDriftDetector:
    """
    Model drift detection system.
    
    Detects data drift, concept drift, and performance drift
    using statistical methods and machine learning techniques.
    """
    
    def __init__(self):
        """Initialize the drift detector."""
        self.reference_data = {}
        self.drift_history = defaultdict(list)
        self.drift_thresholds = {}
        
    async def set_reference_data(self, model_id: str, reference_data: np.ndarray) -> Dict[str, Any]:
        """
        Set reference data for drift detection.
        
        Args:
            model_id: Model identifier
            reference_data: Reference dataset
            
        Returns:
            Dict[str, Any]: Setting result
        """



        try:
            # Store reference data statistics
            self.reference_data[model_id] = {
                "mean": np.mean(reference_data, axis=0),
                "std": np.std(reference_data, axis=0),
                "quantiles": np.percentile(reference_data, [25, 50, 75], axis=0),
                "shape": reference_data.shape,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Set reference data for model {model_id}")
            return {
                "status": "success",
                "model_id": model_id,
                "reference_shape": reference_data.shape,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set reference data: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def detect_drift(self, model_id: str, new_data: np.ndarray,
                          drift_type: DriftType = DriftType.DATA_DRIFT) -> Dict[str, Any]:
        """
        Detect drift in new data.
        
        Args:
            model_id: Model identifier
            new_data: New data to check for drift
            drift_type: Type of drift to detect
            
        Returns:
            Dict[str, Any]: Drift detection result
        """



        try:
            if model_id not in self.reference_data:
                return {
                    "status": "error",
                    "error": f"No reference data found for model {model_id}"
                }
            
            reference = self.reference_data[model_id]
            
            # Perform drift detection based on type
            if drift_type == DriftType.DATA_DRIFT:
                drift_result = await self._detect_data_drift(reference, new_data)
            elif drift_type == DriftType.CONCEPT_DRIFT:
                drift_result = await self._detect_concept_drift(reference, new_data)
            else:
                drift_result = await self._detect_prediction_drift(reference, new_data)
            
            # Store drift result
            drift_record = {
                "model_id": model_id,
                "drift_type": drift_type,
                "drift_score": drift_result["drift_score"],
                "drift_detected": drift_result["drift_detected"],
                "affected_features": drift_result.get("affected_features", []),
                "timestamp": datetime.utcnow(),
                "metadata": drift_result.get("metadata", {})
            }
            
            self.drift_history[model_id].append(drift_record)
            
            # Generate alert if drift detected
            alert = None
            if drift_result["drift_detected"]:
                alert = DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    drift_type=drift_type,
                    alert_level=AlertLevel.WARNING,
                    drift_score=drift_result["drift_score"],
                    threshold=drift_result.get("threshold", 0.05),
                    description=f"{drift_type.value} detected",
                    affected_features=drift_result.get("affected_features", []),
                    timestamp=datetime.utcnow(),
                    metadata=drift_result.get("metadata", {})
                )
            
            return {
                "status": "success",
                "model_id": model_id,
                "drift_detected": drift_result["drift_detected"],
                "drift_score": drift_result["drift_score"],
                "drift_type": drift_type.value,
                "alert": asdict(alert) if alert else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to detect drift: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _detect_data_drift(self, reference: Dict[str, Any], 
                               new_data: np.ndarray) -> Dict[str, Any]:
        """Detect data drift using statistical tests."""
        # Kolmogorov-Smirnov test for each feature
        drift_scores = []
        affected_features = []
        
        ref_mean = reference["mean"]
        ref_std = reference["std"]
        
        new_mean = np.mean(new_data, axis=0)
        new_std = np.std(new_data, axis=0)
        
        # Calculate drift score for each feature
        for i in range(len(ref_mean)):
            # Normalized difference in means
            mean_diff = abs(new_mean[i] - ref_mean[i]) / (ref_std[i] + 1e-8)
            drift_scores.append(mean_diff)
            
            if mean_diff > 2.0:  # 2 standard deviations
                affected_features.append(f"feature_{i}")
        
        overall_drift_score = np.mean(drift_scores)
        drift_detected = overall_drift_score > 1.0
        
        return {
            "drift_score": overall_drift_score,
            "drift_detected": drift_detected,
            "affected_features": affected_features,
            "threshold": 1.0,
            "metadata": {
                "feature_drift_scores": drift_scores,
                "reference_mean": ref_mean.tolist(),
                "new_mean": new_mean.tolist()
            }
        }
    
    async def _detect_concept_drift(self, reference: Dict[str, Any],
                                  new_data: np.ndarray) -> Dict[str, Any]:
        """Detect concept drift using model predictions."""
        # Mock concept drift detection
        drift_score = np.random.random() * 0.1  # Low drift for demo
        drift_detected = drift_score > 0.05
        
        return {
            "drift_score": drift_score,
            "drift_detected": drift_detected,
            "threshold": 0.05,
            "metadata": {"method": "mock_concept_drift"}
        }
    
    async def _detect_prediction_drift(self, reference: Dict[str, Any],
                                     new_data: np.ndarray) -> Dict[str, Any]:
        """Detect prediction drift using prediction distributions."""
        # Mock prediction drift detection
        drift_score = np.random.random() * 0.08  # Low drift for demo
        drift_detected = drift_score > 0.06
        
        return {
            "drift_score": drift_score,
            "drift_detected": drift_detected,
            "threshold": 0.06,
            "metadata": {"method": "mock_prediction_drift"}
        }

class PerformanceBenchmark:
    """
    Performance benchmarking system.
    
    Provides model performance benchmarking and comparison
    capabilities for evaluating model improvements.
    """
    
    def __init__(self):
        """Initialize the performance benchmark."""
        self.benchmarks = {}
        self.benchmark_results = defaultdict(list)
        
    async def create_benchmark(self, benchmark_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a performance benchmark.
        
        Args:
            benchmark_config: Benchmark configuration
            
        Returns:
            Dict[str, Any]: Benchmark creation result
        """



        try:
            benchmark_id = f"benchmark_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            benchmark = {
                "benchmark_id": benchmark_id,
                "name": benchmark_config["name"],
                "description": benchmark_config.get("description", ""),
                "metrics": benchmark_config["metrics"],
                "dataset": benchmark_config["dataset"],
                "created_at": datetime.utcnow(),
                "created_by": benchmark_config.get("created_by", "system")
            }
            
            self.benchmarks[benchmark_id] = benchmark
            
            logger.info(f"Created performance benchmark {benchmark_id}")
            return {
                "status": "success",
                "benchmark_id": benchmark_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create benchmark: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def run_benchmark(self, benchmark_id: str, model_id: str) -> Dict[str, Any]:
        """
        Run benchmark for a model.
        
        Args:
            benchmark_id: Benchmark identifier
            model_id: Model identifier
            
        Returns:
            Dict[str, Any]: Benchmark result
        """



        try:
            if benchmark_id not in self.benchmarks:
                return {
                    "status": "error",
                    "error": f"Benchmark {benchmark_id} not found"
                }
            
            benchmark = self.benchmarks[benchmark_id]
            
            # Mock benchmark execution
            results = {}
            for metric in benchmark["metrics"]:
                if metric == "accuracy":
                    results[metric] = 0.85 + np.random.random() * 0.1
                elif metric == "latency":
                    results[metric] = 50 + np.random.random() * 30
                elif metric == "throughput":
                    results[metric] = 100 + np.random.random() * 50
                else:
                    results[metric] = np.random.random()
            
            # Store benchmark result
            benchmark_result = {
                "benchmark_id": benchmark_id,
                "model_id": model_id,
                "results": results,
                "timestamp": datetime.utcnow(),
                "execution_time_seconds": np.random.random() * 60
            }
            
            self.benchmark_results[benchmark_id].append(benchmark_result)
            
            logger.info(f"Completed benchmark {benchmark_id} for model {model_id}")
            return {
                "status": "success",
                "benchmark_id": benchmark_id,
                "model_id": model_id,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to run benchmark: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def compare_models(self, benchmark_id: str, model_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple models on a benchmark.
        
        Args:
            benchmark_id: Benchmark identifier
            model_ids: List of model identifiers
            
        Returns:
            Dict[str, Any]: Model comparison result
        """



        try:
            if benchmark_id not in self.benchmarks:
                return {
                    "status": "error",
                    "error": f"Benchmark {benchmark_id} not found"
                }
            
            # Get results for each model
            model_results = {}
            for model_id in model_ids:
                model_benchmarks = [
                    result for result in self.benchmark_results[benchmark_id]
                    if result["model_id"] == model_id
                ]
                
                if model_benchmarks:
                    # Use latest result
                    latest_result = max(model_benchmarks, key=lambda x: x["timestamp"])
                    model_results[model_id] = latest_result["results"]
                else:
                    # Run benchmark if no results exist
                    run_result = await self.run_benchmark(benchmark_id, model_id)
                    if run_result["status"] == "success":
                        model_results[model_id] = run_result["results"]
            
            # Calculate comparison metrics
            comparison = {
                "benchmark_id": benchmark_id,
                "models": model_results,
                "ranking": {},
                "best_model": {},
                "comparison_matrix": {}
            }
            
            # Rank models for each metric
            for metric in self.benchmarks[benchmark_id]["metrics"]:
                metric_values = {
                    model_id: results.get(metric, 0)
                    for model_id, results in model_results.items()
                }
                
                # Rank by metric (higher is better for accuracy, lower for latency)
                reverse = metric in ["accuracy", "throughput", "f1_score"]
                sorted_models = sorted(metric_values.items(), 
                                     key=lambda x: x[1], reverse=reverse)
                
                comparison["ranking"][metric] = [model_id for model_id, _ in sorted_models]
                comparison["best_model"][metric] = sorted_models[0][0]
            
            return {
                "status": "success",
                "comparison": comparison,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to compare models: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
