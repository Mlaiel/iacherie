"""
Advanced AI Performance Monitoring Module

Enterprise-grade AI model and engine performance monitoring for industrial content platform.
Supports real-time tracking of AI processing pipelines for multi-format content creators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import statistics
import psutil
import numpy as np
from enum import Enum
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.performance import PerformanceMonitor
from ..core.exceptions import MonitoringError, PerformanceError
# from ...database.session import get_async_session  # Optional import

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """Types of AI models in the platform"""
    CONTENT_GENERATOR = "content_generator"
    CONTENT_PROTECTOR = "content_protector"
    SEO_OPTIMIZER = "seo_optimizer"
    COLLABORATION_MATCHER = "collaboration_matcher"
    REVENUE_PREDICTOR = "revenue_predictor"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    FRAUD_DETECTOR = "fraud_detector"
    QUALITY_ASSESSOR = "quality_assessor"
    TREND_ANALYZER = "trend_analyzer"


class ProcessingStage(Enum):
    """Content processing pipeline stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    AI_ANALYSIS = "ai_analysis"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"


@dataclass
class AIModelMetrics:
    """Comprehensive AI model performance metrics"""
    model_id: str
    model_type: AIModelType
    inference_time: float
    accuracy_score: float
    confidence_score: float
    resource_usage: Dict[str, float]
    error_rate: float
    throughput: float
    queue_length: int
    processing_stage: ProcessingStage
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineMetrics:
    """Content processing pipeline metrics"""
    pipeline_id: str
    stage: ProcessingStage
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    input_size: int = 0
    output_size: int = 0
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    ai_models_used: List[str] = field(default_factory=list)
    resource_consumption: Dict[str, float] = field(default_factory=dict)


class AIPerformanceMonitor:
    """
    Advanced AI Performance Monitor
    
    Monitors AI model performance, pipeline efficiency, and resource usage
    for the IA Influencer Agent platform.
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        redis_client: Optional[aioredis.Redis] = None,
        sampling_rate: float = 1.0,
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.redis_client = redis_client
        self.sampling_rate = sampling_rate
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Performance thresholds for alerting
        self.alert_thresholds = alert_thresholds or {
            "max_inference_time": 5.0,  # seconds
            "min_accuracy_score": 0.85,
            "max_error_rate": 0.05,
            "max_queue_length": 100,
            "min_throughput": 10.0,  # requests per second
            "max_memory_usage": 0.8,  # 80% of available memory
            "max_cpu_usage": 0.9  # 90% CPU usage
        }
        
        # Real-time metrics storage
        self.model_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.pipeline_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Statistics tracking
        self.stats = {
            "total_inferences": 0,
            "successful_inferences": 0,
            "failed_inferences": 0,
            "total_processing_time": 0.0,
            "average_accuracy": 0.0,
            "peak_throughput": 0.0
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
    async def start_monitoring(self) -> None:
        """Start the AI performance monitoring system"""
        async with self._lock:
            if self.is_monitoring:
                logger.warning("AI performance monitoring is already running")
                return
                
            self.is_monitoring = True
            self._monitor_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("AI performance monitoring started successfully")
            
    async def stop_monitoring(self) -> None:
        """Stop the AI performance monitoring system"""
        async with self._lock:
            if not self.is_monitoring:
                return
                
            self.is_monitoring = False
            
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info("AI performance monitoring stopped")
            
    async def track_model_inference(
        self,
        model_id: str,
        model_type: AIModelType,
        inference_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, AIModelMetrics]:
        """
        Track AI model inference performance
        
        Args:
            model_id: Unique identifier for the AI model
            model_type: Type of AI model being tracked
            inference_func: The inference function to execute
            *args, **kwargs: Arguments for the inference function
            
        Returns:
            Tuple of (inference_result, metrics)
        """
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Execute inference
            if asyncio.iscoroutinefunction(inference_func):
                result = await inference_func(*args, **kwargs)
            else:
                result = inference_func(*args, **kwargs)
                
            # Calculate metrics
            inference_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss
            memory_usage = end_memory - start_memory
            
            # Extract performance data from result
            accuracy_score = self._extract_accuracy(result)
            confidence_score = self._extract_confidence(result)
            
            # Create metrics object
            metrics = AIModelMetrics(
                model_id=model_id,
                model_type=model_type,
                inference_time=inference_time,
                accuracy_score=accuracy_score,
                confidence_score=confidence_score,
                resource_usage={
                    "memory_delta": memory_usage,
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent
                },
                error_rate=0.0,
                throughput=1.0 / inference_time if inference_time > 0 else 0.0,
                queue_length=self._get_queue_length(model_id),
                processing_stage=self._infer_processing_stage(model_type),
                user_id=kwargs.get("user_id"),
                content_type=kwargs.get("content_type"),
                metadata=kwargs.get("metadata", {})
            )
            
            # Store metrics
            await self._store_model_metrics(metrics)
            
            # Update statistics
            self._update_statistics(metrics, success=True)
            
            # Check for alerts
            await self._check_performance_alerts(metrics)
            
            return result, metrics
            
        except Exception as e:
            inference_time = time.time() - start_time
            
            # Create error metrics
            metrics = AIModelMetrics(
                model_id=model_id,
                model_type=model_type,
                inference_time=inference_time,
                accuracy_score=0.0,
                confidence_score=0.0,
                resource_usage={
                    "memory_delta": 0,
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent
                },
                error_rate=1.0,
                throughput=0.0,
                queue_length=self._get_queue_length(model_id),
                processing_stage=self._infer_processing_stage(model_type),
                user_id=kwargs.get("user_id"),
                content_type=kwargs.get("content_type"),
                metadata={"error": str(e)}
            )
            
            await self._store_model_metrics(metrics)
            self._update_statistics(metrics, success=False)
            
            logger.error(f"AI model inference failed: {e}")
            raise PerformanceError(f"Model {model_id} inference failed: {e}")
            
    async def track_pipeline_stage(
        self,
        pipeline_id: str,
        stage: ProcessingStage,
        stage_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, PipelineMetrics]:
        """
        Track content processing pipeline stage performance
        
        Args:
            pipeline_id: Unique identifier for the processing pipeline
            stage: Current processing stage
            stage_func: Function to execute for this stage
            *args, **kwargs: Arguments for the stage function
            
        Returns:
            Tuple of (stage_result, metrics)
        """
        start_time = datetime.utcnow()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Execute stage
            if asyncio.iscoroutinefunction(stage_func):
                result = await stage_func(*args, **kwargs)
            else:
                result = stage_func(*args, **kwargs)
                
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            end_memory = psutil.Process().memory_info().rss
            
            # Create metrics
            metrics = PipelineMetrics(
                pipeline_id=pipeline_id,
                stage=stage,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                input_size=kwargs.get("input_size", 0),
                output_size=self._calculate_output_size(result),
                user_id=kwargs.get("user_id"),
                content_id=kwargs.get("content_id"),
                ai_models_used=kwargs.get("ai_models_used", []),
                resource_consumption={
                    "memory_delta": end_memory - start_memory,
                    "cpu_percent": psutil.cpu_percent(),
                    "duration": duration
                }
            )
            
            # Store metrics
            await self._store_pipeline_metrics(metrics)
            
            return result, metrics
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            metrics = PipelineMetrics(
                pipeline_id=pipeline_id,
                stage=stage,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=False,
                error_message=str(e),
                user_id=kwargs.get("user_id"),
                content_id=kwargs.get("content_id")
            )
            
            await self._store_pipeline_metrics(metrics)
            
            logger.error(f"Pipeline stage {stage} failed: {e}")
            raise PerformanceError(f"Pipeline {pipeline_id} stage {stage} failed: {e}")
            
    async def get_model_performance_summary(
        self,
        model_id: str,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Get performance summary for a specific AI model"""
        cutoff_time = datetime.utcnow() - time_window
        
        # Get recent metrics
        recent_metrics = [
            metric for metric in self.model_metrics[model_id]
            if metric.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
            
        # Calculate statistics
        inference_times = [m.inference_time for m in recent_metrics]
        accuracy_scores = [m.accuracy_score for m in recent_metrics]
        error_rates = [m.error_rate for m in recent_metrics]
        
        return {
            "model_id": model_id,
            "time_window": str(time_window),
            "total_inferences": len(recent_metrics),
            "successful_inferences": sum(1 for m in recent_metrics if m.error_rate == 0),
            "average_inference_time": statistics.mean(inference_times),
            "median_inference_time": statistics.median(inference_times),
            "p95_inference_time": np.percentile(inference_times, 95),
            "average_accuracy": statistics.mean(accuracy_scores),
            "overall_error_rate": statistics.mean(error_rates),
            "peak_throughput": max(m.throughput for m in recent_metrics),
            "resource_usage": {
                "avg_memory_usage": statistics.mean(
                    m.resource_usage.get("memory_percent", 0) for m in recent_metrics
                ),
                "avg_cpu_usage": statistics.mean(
                    m.resource_usage.get("cpu_percent", 0) for m in recent_metrics
                )
            }
        }
        
    async def get_pipeline_performance_summary(
        self,
        pipeline_id: str,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Get performance summary for a processing pipeline"""
        cutoff_time = datetime.utcnow() - time_window
        
        recent_metrics = [
            metric for metric in self.pipeline_metrics[pipeline_id]
            if metric.start_time >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent pipeline metrics available"}
            
        # Group by stage
        stage_metrics = defaultdict(list)
        for metric in recent_metrics:
            stage_metrics[metric.stage].append(metric)
            
        summary = {
            "pipeline_id": pipeline_id,
            "time_window": str(time_window),
            "total_executions": len(recent_metrics),
            "successful_executions": sum(1 for m in recent_metrics if m.success),
            "stages": {}
        }
        
        for stage, metrics in stage_metrics.items():
            durations = [m.duration for m in metrics if m.duration]
            
            summary["stages"][stage.value] = {
                "executions": len(metrics),
                "success_rate": sum(1 for m in metrics if m.success) / len(metrics),
                "average_duration": statistics.mean(durations) if durations else 0,
                "median_duration": statistics.median(durations) if durations else 0,
                "p95_duration": np.percentile(durations, 95) if durations else 0
            }
            
        return summary
        
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback function for performance alerts"""
        self.alert_callbacks.append(callback)
        
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for continuous performance tracking"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Update performance trends
                await self._update_performance_trends()
                
                # Check for anomalies
                await self._detect_performance_anomalies()
                
                # Clean old metrics
                await self._cleanup_old_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
                
    async def _store_model_metrics(self, metrics: AIModelMetrics) -> None:
        """Store AI model metrics"""
        # Store in memory
        self.model_metrics[metrics.model_id].append(metrics)
        
        # Store in metrics collector
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name=f"ai_model_inference_time",
                value=metrics.inference_time,
                metric_type=MetricType.TIMER,
                tags={
                    "model_id": metrics.model_id,
                    "model_type": metrics.model_type.value,
                    "stage": metrics.processing_stage.value
                },
                metadata=metrics.metadata,
                user_id=metrics.user_id
            )
        )
        
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name=f"ai_model_accuracy",
                value=metrics.accuracy_score,
                metric_type=MetricType.GAUGE,
                tags={
                    "model_id": metrics.model_id,
                    "model_type": metrics.model_type.value
                },
                user_id=metrics.user_id
            )
        )
        
        # Store in Redis if available
        if self.redis_client:
            try:
                key = f"ai_metrics:{metrics.model_id}:{int(metrics.timestamp.timestamp())}"
                await self.redis_client.setex(
                    key,
                    3600,  # 1 hour TTL
                    json.dumps({
                        "inference_time": metrics.inference_time,
                        "accuracy_score": metrics.accuracy_score,
                        "confidence_score": metrics.confidence_score,
                        "error_rate": metrics.error_rate,
                        "throughput": metrics.throughput,
                        "resource_usage": metrics.resource_usage
                    })
                )
            except Exception as e:
                logger.warning(f"Failed to store metrics in Redis: {e}")
                
    async def _store_pipeline_metrics(self, metrics: PipelineMetrics) -> None:
        """Store pipeline processing metrics"""
        # Store in memory
        self.pipeline_metrics[metrics.pipeline_id].append(metrics)
        
        # Store in metrics collector
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name=f"pipeline_stage_duration",
                value=metrics.duration or 0,
                metric_type=MetricType.TIMER,
                tags={
                    "pipeline_id": metrics.pipeline_id,
                    "stage": metrics.stage.value,
                    "success": str(metrics.success)
                },
                metadata={
                    "input_size": metrics.input_size,
                    "output_size": metrics.output_size,
                    "ai_models_used": metrics.ai_models_used
                },
                user_id=metrics.user_id
            )
        )
        
    def _extract_accuracy(self, result: Any) -> float:
        """Extract accuracy score from inference result"""
        if isinstance(result, dict):
            return result.get("accuracy", result.get("confidence", 0.0))
        elif hasattr(result, "accuracy"):
            return result.accuracy
        elif hasattr(result, "confidence"):
            return result.confidence
        return 0.0
        
    def _extract_confidence(self, result: Any) -> float:
        """Extract confidence score from inference result"""
        if isinstance(result, dict):
            return result.get("confidence", result.get("score", 0.0))
        elif hasattr(result, "confidence"):
            return result.confidence
        elif hasattr(result, "score"):
            return result.score
        return 0.0
        
    def _get_queue_length(self, model_id: str) -> int:
        """Get current queue length for a model"""
        # This would integrate with actual queue monitoring
        return 0
        
    def _infer_processing_stage(self, model_type: AIModelType) -> ProcessingStage:
        """Infer processing stage from model type"""
        stage_mapping = {
            AIModelType.CONTENT_GENERATOR: ProcessingStage.AI_ANALYSIS,
            AIModelType.CONTENT_PROTECTOR: ProcessingStage.PROTECTION,
            AIModelType.SEO_OPTIMIZER: ProcessingStage.SEO_OPTIMIZATION,
            AIModelType.COLLABORATION_MATCHER: ProcessingStage.COLLABORATION_MATCHING,
            AIModelType.REVENUE_PREDICTOR: ProcessingStage.MONETIZATION,
        }
        return stage_mapping.get(model_type, ProcessingStage.AI_ANALYSIS)
        
    def _calculate_output_size(self, result: Any) -> int:
        """Calculate output size from result"""
        if isinstance(result, (str, bytes)):
            return len(result)
        elif isinstance(result, dict):
            return len(json.dumps(result))
        return 0
        
    def _update_statistics(self, metrics: AIModelMetrics, success: bool) -> None:
        """Update global statistics"""
        self.stats["total_inferences"] += 1
        
        if success:
            self.stats["successful_inferences"] += 1
            self.stats["total_processing_time"] += metrics.inference_time
            self.stats["average_accuracy"] = (
                (self.stats["average_accuracy"] * (self.stats["successful_inferences"] - 1) + 
                 metrics.accuracy_score) / self.stats["successful_inferences"]
            )
            
            if metrics.throughput > self.stats["peak_throughput"]:
                self.stats["peak_throughput"] = metrics.throughput
        else:
            self.stats["failed_inferences"] += 1
            
    async def _check_performance_alerts(self, metrics: AIModelMetrics) -> None:
        """Check for performance alerts and trigger callbacks"""
        alerts = []
        
        if metrics.inference_time > self.alert_thresholds["max_inference_time"]:
            alerts.append({
                "type": "high_inference_time",
                "model_id": metrics.model_id,
                "value": metrics.inference_time,
                "threshold": self.alert_thresholds["max_inference_time"]
            })
            
        if metrics.accuracy_score < self.alert_thresholds["min_accuracy_score"]:
            alerts.append({
                "type": "low_accuracy",
                "model_id": metrics.model_id,
                "value": metrics.accuracy_score,
                "threshold": self.alert_thresholds["min_accuracy_score"]
            })
            
        if metrics.error_rate > self.alert_thresholds["max_error_rate"]:
            alerts.append({
                "type": "high_error_rate",
                "model_id": metrics.model_id,
                "value": metrics.error_rate,
                "threshold": self.alert_thresholds["max_error_rate"]
            })
            
        # Trigger alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert) if asyncio.iscoroutinefunction(callback) else callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
                    
    async def _collect_system_metrics(self) -> None:
        """Collect system-wide metrics"""
        # Collect CPU, memory, disk usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="system_cpu_usage",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                tags={"component": "ai_monitoring"}
            )
        )
        
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="system_memory_usage",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                tags={"component": "ai_monitoring"}
            )
        )
        
    async def _update_performance_trends(self) -> None:
        """Update performance trend analysis"""
        for model_id, metrics_queue in self.model_metrics.items():
            if len(metrics_queue) >= 10:  # Minimum data points for trend
                recent_times = [m.inference_time for m in list(metrics_queue)[-10:]]
                self.performance_trends[f"{model_id}_inference_time"] = recent_times
                
    async def _detect_performance_anomalies(self) -> None:
        """Detect performance anomalies using statistical analysis"""
        for model_id, trend_data in self.performance_trends.items():
            if len(trend_data) >= 20:  # Need sufficient data for anomaly detection
                mean_val = statistics.mean(trend_data)
                std_val = statistics.stdev(trend_data)
                latest_val = trend_data[-1]
                
                # Z-score based anomaly detection
                if abs(latest_val - mean_val) > 3 * std_val:
                    logger.warning(f"Performance anomaly detected for {model_id}: {latest_val}")
                    
    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory buildup"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for model_id, metrics_queue in self.model_metrics.items():
            # Remove old metrics
            while metrics_queue and metrics_queue[0].timestamp < cutoff_time:
                metrics_queue.popleft()
                
        for pipeline_id, metrics_queue in self.pipeline_metrics.items():
            while metrics_queue and metrics_queue[0].start_time < cutoff_time:
                metrics_queue.popleft()


# Global AI performance monitor instance
ai_performance_monitor = AIPerformanceMonitor()


@asynccontextmanager
async def track_ai_inference(
    model_id: str,
    model_type: AIModelType,
    user_id: Optional[str] = None,
    content_type: Optional[str] = None
):
    """Context manager for tracking AI inference performance"""
    start_time = time.time()
    
    try:
        yield
    finally:
        inference_time = time.time() - start_time
        
        # Create simplified metrics for context manager usage
        metrics = AIModelMetrics(
            model_id=model_id,
            model_type=model_type,
            inference_time=inference_time,
            accuracy_score=0.0,  # Would need to be set by caller
            confidence_score=0.0,
            resource_usage={"cpu_percent": psutil.cpu_percent()},
            error_rate=0.0,
            throughput=1.0 / inference_time if inference_time > 0 else 0.0,
            queue_length=0,
            processing_stage=ai_performance_monitor._infer_processing_stage(model_type),
            user_id=user_id,
            content_type=content_type
        )
        
        await ai_performance_monitor._store_model_metrics(metrics)


# Decorator for automatic AI model monitoring
def monitor_ai_model(
    model_id: str,
    model_type: AIModelType,
    extract_accuracy: Optional[Callable] = None,
    extract_confidence: Optional[Callable] = None
):
    """Decorator for automatic AI model performance monitoring"""
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            return await ai_performance_monitor.track_model_inference(
                model_id=model_id,
                model_type=model_type,
                inference_func=func,
                *args,
                **kwargs
            )
            
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(
                ai_performance_monitor.track_model_inference(
                    model_id=model_id,
                    model_type=model_type,
                    inference_func=func,
                    *args,
                    **kwargs
                )
            )
            
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator
