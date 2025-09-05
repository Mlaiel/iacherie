"""AI Processing Metrics
=====================

Advanced AI processing performance analytics and optimization system.
Monitors and analyzes AI algorithm performance across all content formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import time
import psutil
import threading
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import redis


class AITaskType(Enum):
    """Types of AI processing tasks"""
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_ENHANCEMENT = "image_enhancement"
    TEXT_OPTIMIZATION = "text_optimization"
    CONTENT_ANALYSIS = "content_analysis"
    COPYRIGHT_DETECTION = "copyright_detection"
    QUALITY_ASSESSMENT = "quality_assessment"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TREND_PREDICTION = "trend_prediction"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    WATERMARK_GENERATION = "watermark_generation"
    COMPRESSION_OPTIMIZATION = "compression_optimization"


class ProcessingStatus(Enum):
    """AI processing status states"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class AIProcessingTask:
    """Individual AI processing task metrics"""
    task_id: str
    task_type: AITaskType
    content_id: str
    input_size: float  # MB
    output_size: float  # MB
    processing_time: float  # seconds
    queue_time: float  # seconds
    cpu_usage: float  # percentage
    memory_usage: float  # MB
    gpu_usage: float  # percentage
    status: ProcessingStatus
    quality_score: float  # 0-10 scale
    accuracy_score: float  # 0-1 scale
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AIProcessingMetrics:
    """Aggregate AI processing performance metrics"""
    time_period: Tuple[datetime, datetime]
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    average_queue_time: float = 0.0
    throughput_per_hour: float = 0.0
    success_rate: float = 0.0
    average_quality_score: float = 0.0
    average_accuracy: float = 0.0
    
    # Resource utilization
    average_cpu_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    peak_memory_usage: float = 0.0
    average_gpu_usage: float = 0.0
    peak_gpu_usage: float = 0.0
    
    # Task type breakdown
    task_type_breakdown: Dict[str, int] = field(default_factory=dict)
    processing_time_by_type: Dict[str, float] = field(default_factory=dict)
    quality_by_type: Dict[str, float] = field(default_factory=dict)
    
    # Performance trends
    hourly_throughput: List[float] = field(default_factory=list)
    error_patterns: Dict[str, int] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)


@dataclass
class PerformanceAlert:
    """AI processing performance alert"""
    alert_id: str
    alert_type: str
    severity: str  # critical, warning, info
    message: str
    affected_tasks: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False


class AIProcessingMetricsEngine:
    """
    Advanced AI processing metrics and performance analytics engine.
    
    Monitors AI algorithm performance, resource utilization, and quality metrics
    across all content processing tasks in real-time.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Task storage and monitoring
        self.active_tasks: Dict[str, AIProcessingTask] = {}
        self.completed_tasks = deque(maxlen=10000)
        self.metrics_history = deque(maxlen=1000)
        self.alerts = deque(maxlen=500)
        
        # Performance thresholds
        self.thresholds = {
            "max_processing_time": 300,  # 5 minutes
            "max_queue_time": 60,        # 1 minute
            "min_success_rate": 0.95,    # 95%
            "max_cpu_usage": 85,         # 85%
            "max_memory_usage": 8192,    # 8GB
            "min_quality_score": 7.0     # 7/10
        }
        
        # Redis for real-time metrics
        self.redis_client = None
        self._initialize_redis()
        
        # Monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # ML models for optimization
        self.performance_predictor = None
        self.bottleneck_detector = None
        
        # Initialize ML models (will be initialized on first use)
        self._ml_models_initialized = False
    
    def _initialize_redis(self):
        """Initialize Redis connection for real-time metrics"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for performance optimization"""
        try:
            # Performance prediction model (would be trained on historical data)
            # self.performance_predictor = load_trained_model("performance_predictor.pkl")
            
            # Bottleneck detection model
            # self.bottleneck_detector = load_trained_model("bottleneck_detector.pkl")
            
            self.logger.info("ML models initialized for AI processing optimization")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    def _monitor_system_resources(self):
        """Background thread to monitor system resources"""
        while self.monitoring_active:
            try:
                # Get current system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Store current metrics
                current_metrics = {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.used / (1024**2),  # MB
                    "memory_percent": memory.percent,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cache in Redis
                if self.redis_client:
                    self.redis_client.lpush("system_metrics", json.dumps(current_metrics))
                    self.redis_client.ltrim("system_metrics", 0, 1000)  # Keep last 1000 entries
                
                # Check for alerts
                asyncio.run(self._check_system_alerts(current_metrics))
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring system resources: {e}")
                time.sleep(10)  # Wait longer on error
    
    async def start_task_tracking(
        self,
        task_id: str,
        task_type: AITaskType,
        content_id: str,
        input_size: float
    ) -> AIProcessingTask:
        """Start tracking a new AI processing task"""
        try:
            task = AIProcessingTask(
                task_id=task_id,
                task_type=task_type,
                content_id=content_id,
                input_size=input_size,
                output_size=0.0,
                processing_time=0.0,
                queue_time=0.0,
                cpu_usage=0.0,
                memory_usage=0.0,
                gpu_usage=0.0,
                status=ProcessingStatus.QUEUED,
                quality_score=0.0,
                accuracy_score=0.0,
                created_at=datetime.now()
            )
            
            self.active_tasks[task_id] = task
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_task_redis(task)
            
            self.logger.info(f"Started tracking task {task_id} of type {task_type.value}")
            return task
            
        except Exception as e:
            self.logger.error(f"Error starting task tracking: {e}")
            raise
    
    async def update_task_status(
        self,
        task_id: str,
        status: ProcessingStatus,
        **kwargs
    ) -> bool:
        """Update task status and metrics"""
        try:
            if task_id not in self.active_tasks:
                self.logger.warning(f"Task {task_id} not found in active tasks")
                return False
            
            task = self.active_tasks[task_id]
            task.status = status
            
            # Update specific metrics
            if "output_size" in kwargs:
                task.output_size = kwargs["output_size"]
            if "quality_score" in kwargs:
                task.quality_score = kwargs["quality_score"]
            if "accuracy_score" in kwargs:
                task.accuracy_score = kwargs["accuracy_score"]
            if "error_message" in kwargs:
                task.error_message = kwargs["error_message"]
            
            # Update timestamps
            if status == ProcessingStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.now()
                task.queue_time = (task.started_at - task.created_at).total_seconds()
            elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                task.completed_at = datetime.now()
                if task.started_at:
                    task.processing_time = (task.completed_at - task.started_at).total_seconds()
                
                # Move to completed tasks
                self.completed_tasks.append(task)
                del self.active_tasks[task_id]
            
            # Update resource usage
            task.cpu_usage = psutil.cpu_percent()
            task.memory_usage = psutil.virtual_memory().used / (1024**2)
            
            # Cache updated task
            if self.redis_client:
                await self._cache_task_redis(task)
            
            # Check for performance alerts
            await self._check_task_alerts(task)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            return False
    
    async def calculate_processing_metrics(
        self,
        time_range: Tuple[datetime, datetime],
        task_types: Optional[List[AITaskType]] = None
    ) -> AIProcessingMetrics:
        """Calculate comprehensive AI processing metrics for a time period"""
        try:
            start_time, end_time = time_range
            
            # Filter tasks by time range and type
            filtered_tasks = [
                task for task in self.completed_tasks
                if start_time <= task.created_at <= end_time
                and (not task_types or task.task_type in task_types)
            ]
            
            if not filtered_tasks:
                return AIProcessingMetrics(time_period=time_range)
            
            # Calculate basic metrics
            total_tasks = len(filtered_tasks)
            completed_tasks = len([t for t in filtered_tasks if t.status == ProcessingStatus.COMPLETED])
            failed_tasks = len([t for t in filtered_tasks if t.status == ProcessingStatus.FAILED])
            
            # Calculate averages
            processing_times = [t.processing_time for t in filtered_tasks if t.processing_time > 0]
            queue_times = [t.queue_time for t in filtered_tasks if t.queue_time > 0]
            quality_scores = [t.quality_score for t in filtered_tasks if t.quality_score > 0]
            accuracy_scores = [t.accuracy_score for t in filtered_tasks if t.accuracy_score > 0]
            
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0.0
            avg_queue_time = statistics.mean(queue_times) if queue_times else 0.0
            avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0
            avg_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
            
            # Calculate throughput
            time_hours = (end_time - start_time).total_seconds() / 3600
            throughput = completed_tasks / time_hours if time_hours > 0 else 0.0
            
            # Calculate success rate
            success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            
            # Resource utilization
            cpu_usages = [t.cpu_usage for t in filtered_tasks if t.cpu_usage > 0]
            memory_usages = [t.memory_usage for t in filtered_tasks if t.memory_usage > 0]
            gpu_usages = [t.gpu_usage for t in filtered_tasks if t.gpu_usage > 0]
            
            avg_cpu = statistics.mean(cpu_usages) if cpu_usages else 0.0
            peak_cpu = max(cpu_usages) if cpu_usages else 0.0
            avg_memory = statistics.mean(memory_usages) if memory_usages else 0.0
            peak_memory = max(memory_usages) if memory_usages else 0.0
            avg_gpu = statistics.mean(gpu_usages) if gpu_usages else 0.0
            peak_gpu = max(gpu_usages) if gpu_usages else 0.0
            
            # Task type breakdown
            task_type_breakdown = {}
            processing_time_by_type = {}
            quality_by_type = {}
            
            for task_type in AITaskType:
                type_tasks = [t for t in filtered_tasks if t.task_type == task_type]
                if type_tasks:
                    task_type_breakdown[task_type.value] = len(type_tasks)
                    
                    type_processing_times = [t.processing_time for t in type_tasks if t.processing_time > 0]
                    if type_processing_times:
                        processing_time_by_type[task_type.value] = statistics.mean(type_processing_times)
                    
                    type_quality_scores = [t.quality_score for t in type_tasks if t.quality_score > 0]
                    if type_quality_scores:
                        quality_by_type[task_type.value] = statistics.mean(type_quality_scores)
            
            # Error patterns
            error_patterns = {}
            for task in filtered_tasks:
                if task.status == ProcessingStatus.FAILED and task.error_message:
                    error_type = task.error_message.split(":")[0] if ":" in task.error_message else "Unknown"
                    error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(filtered_tasks)
            
            # Create metrics object
            metrics = AIProcessingMetrics(
                time_period=time_range,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                average_processing_time=avg_processing_time,
                average_queue_time=avg_queue_time,
                throughput_per_hour=throughput,
                success_rate=success_rate,
                average_quality_score=avg_quality,
                average_accuracy=avg_accuracy,
                average_cpu_usage=avg_cpu,
                peak_cpu_usage=peak_cpu,
                average_memory_usage=avg_memory,
                peak_memory_usage=peak_memory,
                average_gpu_usage=avg_gpu,
                peak_gpu_usage=peak_gpu,
                task_type_breakdown=task_type_breakdown,
                processing_time_by_type=processing_time_by_type,
                quality_by_type=quality_by_type,
                error_patterns=error_patterns,
                bottlenecks=bottlenecks
            )
            
            # Cache metrics
            self.metrics_history.append(metrics)
            
            # Store in Redis
            if self.redis_client:
                await self._cache_metrics_redis(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating processing metrics: {e}")
            return AIProcessingMetrics(time_period=time_range)
    
    async def _identify_bottlenecks(self, tasks: List[AIProcessingTask]) -> List[str]:
        """Identify system bottlenecks from task data"""
        bottlenecks = []
        
        try:
            if not tasks:
                return bottlenecks
            
            # Check for high queue times
            queue_times = [t.queue_time for t in tasks if t.queue_time > 0]
            if queue_times and statistics.mean(queue_times) > self.thresholds["max_queue_time"]:
                bottlenecks.append("High queue times detected - processing capacity insufficient")
            
            # Check for high processing times
            processing_times = [t.processing_time for t in tasks if t.processing_time > 0]
            if processing_times and statistics.mean(processing_times) > self.thresholds["max_processing_time"]:
                bottlenecks.append("High processing times - algorithm optimization needed")
            
            # Check for resource constraints
            cpu_usages = [t.cpu_usage for t in tasks if t.cpu_usage > 0]
            if cpu_usages and statistics.mean(cpu_usages) > self.thresholds["max_cpu_usage"]:
                bottlenecks.append("High CPU utilization - consider scaling up")
            
            memory_usages = [t.memory_usage for t in tasks if t.memory_usage > 0]
            if memory_usages and statistics.mean(memory_usages) > self.thresholds["max_memory_usage"]:
                bottlenecks.append("High memory usage - memory optimization needed")
            
            # Check for task type imbalances
            task_type_counts = {}
            for task in tasks:
                task_type_counts[task.task_type.value] = task_type_counts.get(task.task_type.value, 0) + 1
            
            total_tasks = len(tasks)
            for task_type, count in task_type_counts.items():
                if count / total_tasks > 0.4:  # More than 40% of one type
                    bottlenecks.append(f"High concentration of {task_type} tasks - load balancing needed")
            
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Error identifying bottlenecks: {e}")
            return []
    
    async def _check_task_alerts(self, task: AIProcessingTask):
        """Check for task-specific performance alerts"""
        try:
            alerts = []
            
            # Processing time alert
            if task.processing_time > self.thresholds["max_processing_time"]:
                alerts.append(PerformanceAlert(
                    alert_id=f"proc_time_{task.task_id}_{int(datetime.now().timestamp())}",
                    alert_type="processing_time_exceeded",
                    severity="warning",
                    message=f"Task {task.task_id} exceeded maximum processing time",
                    affected_tasks=[task.task_id],
                    metrics={"processing_time": task.processing_time, "threshold": self.thresholds["max_processing_time"]},
                    timestamp=datetime.now()
                ))
            
            # Queue time alert
            if task.queue_time > self.thresholds["max_queue_time"]:
                alerts.append(PerformanceAlert(
                    alert_id=f"queue_time_{task.task_id}_{int(datetime.now().timestamp())}",
                    alert_type="queue_time_exceeded",
                    severity="warning",
                    message=f"Task {task.task_id} exceeded maximum queue time",
                    affected_tasks=[task.task_id],
                    metrics={"queue_time": task.queue_time, "threshold": self.thresholds["max_queue_time"]},
                    timestamp=datetime.now()
                ))
            
            # Quality score alert
            if task.quality_score > 0 and task.quality_score < self.thresholds["min_quality_score"]:
                alerts.append(PerformanceAlert(
                    alert_id=f"quality_{task.task_id}_{int(datetime.now().timestamp())}",
                    alert_type="low_quality_output",
                    severity="critical",
                    message=f"Task {task.task_id} produced low quality output",
                    affected_tasks=[task.task_id],
                    metrics={"quality_score": task.quality_score, "threshold": self.thresholds["min_quality_score"]},
                    timestamp=datetime.now()
                ))
            
            # Add alerts to queue
            for alert in alerts:
                self.alerts.append(alert)
                self.logger.warning(f"Performance alert: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error checking task alerts: {e}")
    
    async def _check_system_alerts(self, metrics: Dict[str, Any]):
        """Check for system-wide performance alerts"""
        try:
            # CPU usage alert
            if metrics["cpu_usage"] > self.thresholds["max_cpu_usage"]:
                alert = PerformanceAlert(
                    alert_id=f"cpu_{int(datetime.now().timestamp())}",
                    alert_type="high_cpu_usage",
                    severity="critical",
                    message="System CPU usage is critically high",
                    affected_tasks=list(self.active_tasks.keys()),
                    metrics={"cpu_usage": metrics["cpu_usage"], "threshold": self.thresholds["max_cpu_usage"]},
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
            
            # Memory usage alert
            if metrics["memory_usage"] > self.thresholds["max_memory_usage"]:
                alert = PerformanceAlert(
                    alert_id=f"memory_{int(datetime.now().timestamp())}",
                    alert_type="high_memory_usage",
                    severity="critical",
                    message="System memory usage is critically high",
                    affected_tasks=list(self.active_tasks.keys()),
                    metrics={"memory_usage": metrics["memory_usage"], "threshold": self.thresholds["max_memory_usage"]},
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
            
        except Exception as e:
            self.logger.error(f"Error checking system alerts: {e}")
    
    async def predict_processing_time(
        self,
        task_type: AITaskType,
        input_size: float,
        current_load: Optional[float] = None
    ) -> Dict[str, Any]:
        """Predict processing time for a new task using ML"""
        try:
            # Get historical data for this task type
            historical_tasks = [
                task for task in self.completed_tasks
                if task.task_type == task_type and task.processing_time > 0
            ]
            
            if len(historical_tasks) < 10:
                # Not enough data for prediction
                return {
                    "predicted_time": 30.0,  # Default estimate
                    "confidence": 0.3,
                    "method": "default_estimate",
                    "note": "Insufficient historical data for accurate prediction"
                }
            
            # Simple linear correlation with input size
            sizes = [t.input_size for t in historical_tasks]
            times = [t.processing_time for t in historical_tasks]
            
            # Calculate correlation coefficient
            if len(sizes) > 1:
                correlation = np.corrcoef(sizes, times)[0, 1]
                
                # Simple linear prediction
                avg_time_per_mb = statistics.mean([t/s for t, s in zip(times, sizes) if s > 0])
                predicted_time = avg_time_per_mb * input_size
                
                # Adjust for current system load
                if current_load:
                    load_factor = 1 + (current_load / 100)
                    predicted_time *= load_factor
                
                return {
                    "predicted_time": predicted_time,
                    "confidence": abs(correlation),
                    "method": "linear_correlation",
                    "correlation": correlation,
                    "historical_samples": len(historical_tasks)
                }
            
            return {
                "predicted_time": statistics.mean(times),
                "confidence": 0.5,
                "method": "historical_average",
                "historical_samples": len(historical_tasks)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting processing time: {e}")
            return {
                "predicted_time": 60.0,
                "confidence": 0.1,
                "method": "error_fallback",
                "error": str(e)
            }
    
    async def optimize_processing_queue(self) -> Dict[str, Any]:
        """Optimize the processing queue for better performance"""
        try:
            if not self.active_tasks:
                return {"message": "No active tasks to optimize"}
            
            optimization_suggestions = []
            
            # Analyze current queue
            queued_tasks = [t for t in self.active_tasks.values() if t.status == ProcessingStatus.QUEUED]
            processing_tasks = [t for t in self.active_tasks.values() if t.status == ProcessingStatus.PROCESSING]
            
            # Check for task type imbalances
            task_type_counts = {}
            for task in queued_tasks:
                task_type_counts[task.task_type.value] = task_type_counts.get(task.task_type.value, 0) + 1
            
            # Suggest priority reordering
            if len(task_type_counts) > 1:
                # Prioritize smaller tasks first for better throughput
                small_tasks = [t for t in queued_tasks if t.input_size < 10.0]  # < 10MB
                if small_tasks:
                    optimization_suggestions.append(
                        "Prioritize smaller tasks first to improve overall throughput"
                    )
                
                # Balance task types
                max_type_count = max(task_type_counts.values())
                total_queued = len(queued_tasks)
                if max_type_count / total_queued > 0.6:
                    optimization_suggestions.append(
                        "Consider load balancing across different task types"
                    )
            
            # Check resource utilization
            current_cpu = psutil.cpu_percent()
            current_memory = psutil.virtual_memory().percent
            
            if current_cpu < 50 and len(processing_tasks) < 4:
                optimization_suggestions.append(
                    "CPU utilization is low - consider increasing parallel processing"
                )
            
            if current_memory > 80:
                optimization_suggestions.append(
                    "Memory usage is high - consider reducing batch sizes"
                )
            
            return {
                "current_queue_size": len(queued_tasks),
                "processing_tasks": len(processing_tasks),
                "cpu_usage": current_cpu,
                "memory_usage": current_memory,
                "optimization_suggestions": optimization_suggestions,
                "task_type_distribution": task_type_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing processing queue: {e}")
            return {"error": str(e)}
    
    async def get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time processing status and metrics"""
        try:
            # Current task status
            active_count = len(self.active_tasks)
            queued_count = len([t for t in self.active_tasks.values() if t.status == ProcessingStatus.QUEUED])
            processing_count = len([t for t in self.active_tasks.values() if t.status == ProcessingStatus.PROCESSING])
            
            # Recent completion metrics
            recent_tasks = [t for t in self.completed_tasks if (datetime.now() - t.completed_at).seconds < 3600]  # Last hour
            recent_completions = len([t for t in recent_tasks if t.status == ProcessingStatus.COMPLETED])
            recent_failures = len([t for t in recent_tasks if t.status == ProcessingStatus.FAILED])
            
            # System resources
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            # Active alerts
            active_alerts = [a for a in self.alerts if not a.resolved and (datetime.now() - a.timestamp).seconds < 3600]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "active_tasks": {
                    "total": active_count,
                    "queued": queued_count,
                    "processing": processing_count
                },
                "recent_performance": {
                    "completions_last_hour": recent_completions,
                    "failures_last_hour": recent_failures,
                    "success_rate": recent_completions / (recent_completions + recent_failures) if (recent_completions + recent_failures) > 0 else 0.0
                },
                "system_resources": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "memory_available_gb": memory.available / (1024**3)
                },
                "alerts": {
                    "active_count": len(active_alerts),
                    "critical_count": len([a for a in active_alerts if a.severity == "critical"]),
                    "warning_count": len([a for a in active_alerts if a.severity == "warning"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time status: {e}")
            return {"error": str(e)}
    
    async def generate_performance_report(
        self,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Generate comprehensive AI processing performance report"""
        try:
            # Calculate metrics for the period
            metrics = await self.calculate_processing_metrics(time_range)
            
            # Get alerts for the period
            period_alerts = [
                a for a in self.alerts
                if time_range[0] <= a.timestamp <= time_range[1]
            ]
            
            # Performance analysis
            performance_score = self._calculate_performance_score(metrics)
            bottleneck_analysis = await self._analyze_bottlenecks(metrics)
            recommendations = await self._generate_recommendations(metrics)
            
            return {
                "report_period": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat(),
                    "duration_hours": (time_range[1] - time_range[0]).total_seconds() / 3600
                },
                "performance_metrics": {
                    "total_tasks": metrics.total_tasks,
                    "success_rate": round(metrics.success_rate * 100, 2),
                    "average_processing_time": round(metrics.average_processing_time, 2),
                    "throughput_per_hour": round(metrics.throughput_per_hour, 2),
                    "average_quality_score": round(metrics.average_quality_score, 2)
                },
                "resource_utilization": {
                    "average_cpu": round(metrics.average_cpu_usage, 2),
                    "peak_cpu": round(metrics.peak_cpu_usage, 2),
                    "average_memory_mb": round(metrics.average_memory_usage, 2),
                    "peak_memory_mb": round(metrics.peak_memory_usage, 2)
                },
                "task_breakdown": metrics.task_type_breakdown,
                "performance_by_type": metrics.processing_time_by_type,
                "quality_by_type": metrics.quality_by_type,
                "alerts_summary": {
                    "total_alerts": len(period_alerts),
                    "critical_alerts": len([a for a in period_alerts if a.severity == "critical"]),
                    "warning_alerts": len([a for a in period_alerts if a.severity == "warning"]),
                    "most_common_alert_types": self._get_common_alert_types(period_alerts)
                },
                "bottlenecks": metrics.bottlenecks,
                "performance_score": performance_score,
                "bottleneck_analysis": bottleneck_analysis,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_score(self, metrics: AIProcessingMetrics) -> Dict[str, Any]:
        """Calculate overall performance score (0-100)"""
        try:
            scores = []
            
            # Success rate score (0-30 points)
            success_score = min(30, metrics.success_rate * 30)
            scores.append(("success_rate", success_score))
            
            # Processing time score (0-25 points)
            if metrics.average_processing_time > 0:
                time_score = max(0, 25 - (metrics.average_processing_time / 60) * 5)  # Penalty per minute
                scores.append(("processing_time", time_score))
            
            # Quality score (0-25 points)
            if metrics.average_quality_score > 0:
                quality_score = (metrics.average_quality_score / 10) * 25
                scores.append(("quality", quality_score))
            
            # Resource efficiency score (0-20 points)
            cpu_efficiency = max(0, 20 - (metrics.average_cpu_usage / 100) * 20)
            scores.append(("resource_efficiency", cpu_efficiency))
            
            total_score = sum(score for _, score in scores)
            
            return {
                "total_score": round(total_score, 1),
                "breakdown": {name: round(score, 1) for name, score in scores},
                "grade": self._get_performance_grade(total_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return {"total_score": 0, "breakdown": {}, "grade": "F"}
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    async def _analyze_bottlenecks(self, metrics: AIProcessingMetrics) -> Dict[str, Any]:
        """Detailed bottleneck analysis"""
        analysis = {
            "identified_bottlenecks": metrics.bottlenecks,
            "severity_assessment": {},
            "impact_analysis": {},
            "resolution_priority": []
        }
        
        # Analyze each bottleneck
        for bottleneck in metrics.bottlenecks:
            if "queue time" in bottleneck.lower():
                analysis["severity_assessment"]["queue_time"] = "high"
                analysis["impact_analysis"]["queue_time"] = "Affects user experience and throughput"
            elif "cpu" in bottleneck.lower():
                analysis["severity_assessment"]["cpu"] = "critical"
                analysis["impact_analysis"]["cpu"] = "System performance degradation"
            elif "memory" in bottleneck.lower():
                analysis["severity_assessment"]["memory"] = "critical"
                analysis["impact_analysis"]["memory"] = "Risk of system instability"
        
        return analysis
    
    async def _generate_recommendations(self, metrics: AIProcessingMetrics) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Success rate recommendations
        if metrics.success_rate < 0.95:
            recommendations.append({
                "category": "reliability",
                "priority": "high",
                "title": "Improve Task Success Rate",
                "description": "Success rate is below target of 95%",
                "actions": [
                    "Review and fix common failure patterns",
                    "Implement better error handling",
                    "Add input validation",
                    "Increase retry mechanisms"
                ]
            })
        
        # Performance recommendations
        if metrics.average_processing_time > 120:  # 2 minutes
            recommendations.append({
                "category": "performance",
                "priority": "medium",
                "title": "Optimize Processing Speed",
                "description": "Average processing time is high",
                "actions": [
                    "Profile algorithm performance",
                    "Optimize computational complexity",
                    "Consider algorithm alternatives",
                    "Implement caching for repeated operations"
                ]
            })
        
        # Resource recommendations
        if metrics.average_cpu_usage > 80:
            recommendations.append({
                "category": "resources",
                "priority": "high",
                "title": "Scale Processing Capacity",
                "description": "CPU utilization is consistently high",
                "actions": [
                    "Add more processing nodes",
                    "Implement horizontal scaling",
                    "Optimize resource allocation",
                    "Consider task scheduling improvements"
                ]
            })
        
        return recommendations
    
    def _get_common_alert_types(self, alerts: List[PerformanceAlert]) -> Dict[str, int]:
        """Get most common alert types"""
        alert_counts = {}
        for alert in alerts:
            alert_counts[alert.alert_type] = alert_counts.get(alert.alert_type, 0) + 1
        
        # Sort by count and return top 5
        sorted_alerts = sorted(alert_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_alerts[:5])
    
    async def _cache_task_redis(self, task: AIProcessingTask):
        """Cache task data in Redis"""
        if self.redis_client:
            try:
                key = f"ai_task:{task.task_id}"
                data = {
                    "task_type": task.task_type.value,
                    "status": task.status.value,
                    "processing_time": task.processing_time,
                    "quality_score": task.quality_score,
                    "created_at": task.created_at.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis task cache error: {e}")
    
    async def _cache_metrics_redis(self, metrics: AIProcessingMetrics):
        """Cache metrics in Redis"""
        if self.redis_client:
            try:
                key = f"ai_metrics:{int(metrics.time_period[1].timestamp())}"
                data = {
                    "total_tasks": metrics.total_tasks,
                    "success_rate": metrics.success_rate,
                    "avg_processing_time": metrics.average_processing_time,
                    "throughput": metrics.throughput_per_hour,
                    "avg_quality": metrics.average_quality_score
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis metrics cache error: {e}")
    
    def shutdown(self):
        """Gracefully shutdown the metrics engine"""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        self.logger.info("AI Processing Metrics Engine shutdown complete")