#!/usr/bin/env python3
"""
Ainflue Platform - AI Processing Monitoring Controller
====================================================

Enterprise-grade monitoring controller for AI processing pipelines including
ML model inference, GPU utilization, model drift detection, and AI feature
usage analytics for Creator Economy optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import json
import time
import psutil
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """AI model types for Creator Economy"""
    CONTENT_GENERATION = "content_generation"
    QUALITY_ASSESSMENT = "quality_assessment"
    CONTENT_RECOMMENDATION = "content_recommendation"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_OPTIMIZATION = "image_optimization"
    TEXT_ANALYSIS = "text_analysis"
    CREATOR_MATCHING = "creator_matching" 
    SEO_OPTIMIZATION = "seo_optimization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    FRAUD_DETECTION = "fraud_detection"
    CONTENT_MODERATION = "content_moderation"

class ProcessingStage(Enum):
    """AI processing pipeline stages"""
    INPUT_VALIDATION = "input_validation"
    PREPROCESSING = "preprocessing"
    MODEL_INFERENCE = "model_inference" 
    POSTPROCESSING = "postprocessing"
    RESULT_VALIDATION = "result_validation"
    OUTPUT_FORMATTING = "output_formatting"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceType(Enum):
    """Compute resource types"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"

@dataclass
class AIModelConfig:
    """AI model configuration"""
    model_id: str
    model_type: AIModelType
    model_name: str
    version: str
    framework: str  # tensorflow, pytorch, onnx, etc.
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    parameters_count: int
    model_size_mb: float
    gpu_required: bool = True
    min_memory_gb: float = 1.0
    max_batch_size: int = 32
    target_latency_ms: float = 100.0
    accuracy_threshold: float = 0.9

@dataclass
class InferenceRequest:
    """AI inference request tracking"""
    request_id: str
    model_id: str
    creator_id: str
    content_id: Optional[str] = None
    input_size_bytes: int = 0
    batch_size: int = 1
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    timestamp: datetime = field(default_factory=datetime.now)
    processing_stage: ProcessingStage = ProcessingStage.INPUT_VALIDATION

@dataclass
class InferenceMetrics:
    """AI inference performance metrics"""
    request_id: str
    model_id: str
    stage: ProcessingStage
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    gpu_memory_mb: float = 0.0
    throughput_requests_per_second: float = 0.0
    accuracy_score: Optional[float] = None
    confidence_score: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class ModelDriftMetrics:
    """Model drift detection metrics"""
    model_id: str
    timestamp: datetime
    data_drift_score: float
    concept_drift_score: float
    performance_drift_score: float
    feature_importance_drift: Dict[str, float]
    accuracy_degradation: float
    recommendation: str  # retrain, fine_tune, monitor, urgent_action

@dataclass
class GPUUtilization:
    """GPU utilization metrics"""
    gpu_id: int
    gpu_name: str
    timestamp: datetime
    utilization_percent: float
    memory_used_mb: float
    memory_total_mb: float
    temperature_celsius: float
    power_usage_watts: float
    active_processes: List[str]

@dataclass
class AIProcessingInsights:
    """AI processing insights and recommendations"""
    overall_performance_score: float
    model_performance_rankings: List[Dict[str, Any]]
    resource_optimization_opportunities: List[str]
    model_drift_alerts: List[Dict[str, Any]]
    scaling_recommendations: List[str]
    cost_optimization_suggestions: List[str]
    creator_ai_usage_patterns: Dict[str, Any]

class AIProcessingMonitoringController:
    """
    Enterprise monitoring controller for AI processing infrastructure.
    
    Monitors ML model inference performance, GPU utilization, model drift,
    and provides comprehensive analytics for Creator Economy AI optimization.
    """
    
    def __init__(self):
        """Initialize AI processing monitoring controller"""
        self.start_time = datetime.now()
        self.active = False
        
        # Model registry and tracking
        self.registered_models: Dict[str, AIModelConfig] = {}
        self.inference_requests: Dict[str, InferenceRequest] = {}
        self.inference_metrics: Dict[str, List[InferenceMetrics]] = defaultdict(list)
        
        # Model performance tracking
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.model_drift_history: Dict[str, List[ModelDriftMetrics]] = defaultdict(list)
        
        # Resource utilization tracking
        self.gpu_utilization_history: List[GPUUtilization] = []
        self.resource_usage_stats: Dict[ResourceType, deque] = {
            resource_type: deque(maxlen=1000) for resource_type in ResourceType
        }
        
        # Creator AI usage tracking
        self.creator_ai_usage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "favorite_models": defaultdict(int),
            "avg_processing_time": 0.0,
            "success_rate": 1.0,
            "cost_consumed": 0.0
        })
        
        # Performance thresholds
        self.performance_thresholds = {
            "max_latency_ms": 1000.0,
            "min_accuracy": 0.85,
            "max_gpu_utilization": 90.0,
            "max_memory_usage": 85.0,
            "max_drift_score": 0.3
        }
        
        # Model load balancing
        self.model_instances: Dict[str, int] = defaultdict(int)  # Active instances per model
        self.request_queue: Dict[str, deque] = defaultdict(deque)
        
        logger.info("AIProcessingMonitoringController initialized")
    
    async def start_monitoring(self):
        """Start AI processing monitoring"""
        try:
            self.active = True
            
            # Initialize GPU monitoring
            await self._initialize_gpu_monitoring()
            
            # Start continuous monitoring tasks
            asyncio.create_task(self._continuous_inference_monitoring())
            asyncio.create_task(self._continuous_resource_monitoring())
            asyncio.create_task(self._continuous_model_drift_monitoring())
            asyncio.create_task(self._continuous_performance_optimization())
            
            logger.info("AI processing monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start AI processing monitoring: {e}")
            raise
    
    async def register_model(self, model_config: Dict[str, Any]) -> str:
        """Register AI model for monitoring"""
        try:
            model_id = model_config.get("model_id") or str(uuid.uuid4())
            
            config = AIModelConfig(
                model_id=model_id,
                model_type=AIModelType(model_config["model_type"]),
                model_name=model_config["model_name"],
                version=model_config.get("version", "1.0.0"),
                framework=model_config.get("framework", "pytorch"),
                input_shape=tuple(model_config.get("input_shape", (1, 224, 224, 3))),
                output_shape=tuple(model_config.get("output_shape", (1, 1000))),
                parameters_count=model_config.get("parameters_count", 1000000),
                model_size_mb=model_config.get("model_size_mb", 100.0),
                gpu_required=model_config.get("gpu_required", True),
                min_memory_gb=model_config.get("min_memory_gb", 2.0),
                max_batch_size=model_config.get("max_batch_size", 16),
                target_latency_ms=model_config.get("target_latency_ms", 200.0),
                accuracy_threshold=model_config.get("accuracy_threshold", 0.9)
            )
            
            self.registered_models[model_id] = config
            
            # Initialize performance tracking
            self.model_performance[model_id] = {
                "avg_latency_ms": 0.0,
                "success_rate": 1.0,
                "avg_accuracy": 0.0,
                "throughput_rps": 0.0,
                "cost_per_inference": 0.0
            }
            
            logger.info(f"Model registered: {model_id} ({config.model_name})")
            return model_id
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            raise
    
    async def track_inference_request(self, request_data: Dict[str, Any]) -> str:
        """Track AI inference request"""
        try:
            request_id = request_data.get("request_id") or str(uuid.uuid4())
            
            if request_data["model_id"] not in self.registered_models:
                raise ValueError(f"Model {request_data['model_id']} not registered")
            
            request = InferenceRequest(
                request_id=request_id,
                model_id=request_data["model_id"],
                creator_id=request_data["creator_id"],
                content_id=request_data.get("content_id"),
                input_size_bytes=request_data.get("input_size_bytes", 0),
                batch_size=request_data.get("batch_size", 1),
                priority=request_data.get("priority", 1)
            )
            
            self.inference_requests[request_id] = request
            
            # Update creator usage stats
            creator_stats = self.creator_ai_usage[request.creator_id]
            creator_stats["total_requests"] += 1
            creator_stats["favorite_models"][request.model_id] += 1
            
            logger.info(f"Inference request tracked: {request_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to track inference request: {e}")
            raise
    
    async def track_inference_metrics(self, request_id: str, metrics_data: Dict[str, Any]):
        """Track inference performance metrics"""
        try:
            if request_id not in self.inference_requests:
                logger.warning(f"Inference request {request_id} not found")
                return
            
            request = self.inference_requests[request_id]
            stage = ProcessingStage(metrics_data["stage"])
            
            metrics = InferenceMetrics(
                request_id=request_id,
                model_id=request.model_id,
                stage=stage,
                start_time=datetime.fromisoformat(metrics_data["start_time"]),
                end_time=datetime.fromisoformat(metrics_data["end_time"]) if "end_time" in metrics_data else None,
                duration_ms=metrics_data.get("duration_ms"),
                cpu_usage_percent=metrics_data.get("cpu_usage", 0.0),
                memory_usage_mb=metrics_data.get("memory_usage", 0.0),
                gpu_usage_percent=metrics_data.get("gpu_usage", 0.0),
                gpu_memory_mb=metrics_data.get("gpu_memory", 0.0),
                throughput_requests_per_second=metrics_data.get("throughput", 0.0),
                accuracy_score=metrics_data.get("accuracy_score"),
                confidence_score=metrics_data.get("confidence_score"),
                success=metrics_data.get("success", True),
                error_message=metrics_data.get("error_message")
            )
            
            # Store metrics (keep last 10000 per model)
            self.inference_metrics[request.model_id].append(metrics)
            if len(self.inference_metrics[request.model_id]) > 10000:
                self.inference_metrics[request.model_id] = self.inference_metrics[request.model_id][-10000:]
            
            # Update request stage
            request.processing_stage = stage
            
            # Update model performance metrics
            await self._update_model_performance(request.model_id, metrics)
            
            # Update creator usage stats
            await self._update_creator_usage_stats(request.creator_id, metrics)
            
            logger.info(f"Inference metrics tracked: {request_id} -> {stage.value}")
            
        except Exception as e:
            logger.error(f"Failed to track inference metrics: {e}")
    
    async def detect_model_drift(self, model_id: str, drift_data: Dict[str, Any]):
        """Detect and track model drift"""
        try:
            if model_id not in self.registered_models:
                logger.warning(f"Model {model_id} not registered")
                return
            
            drift_metrics = ModelDriftMetrics(
                model_id=model_id,
                timestamp=datetime.now(),
                data_drift_score=drift_data.get("data_drift_score", 0.0),
                concept_drift_score=drift_data.get("concept_drift_score", 0.0),
                performance_drift_score=drift_data.get("performance_drift_score", 0.0),
                feature_importance_drift=drift_data.get("feature_importance_drift", {}),
                accuracy_degradation=drift_data.get("accuracy_degradation", 0.0),
                recommendation=drift_data.get("recommendation", "monitor")
            )
            
            # Store drift metrics (keep last 1000 per model)
            self.model_drift_history[model_id].append(drift_metrics)
            if len(self.model_drift_history[model_id]) > 1000:
                self.model_drift_history[model_id] = self.model_drift_history[model_id][-1000:]
            
            # Check drift thresholds and generate alerts
            if drift_metrics.data_drift_score > self.performance_thresholds["max_drift_score"]:
                logger.warning(f"Data drift detected for model {model_id}: {drift_metrics.data_drift_score}")
            
            if drift_metrics.performance_drift_score > self.performance_thresholds["max_drift_score"]:
                logger.warning(f"Performance drift detected for model {model_id}: {drift_metrics.performance_drift_score}")
            
            logger.info(f"Model drift tracked: {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to detect model drift: {e}")
    
    async def track_gpu_utilization(self, gpu_data: Dict[str, Any]):
        """Track GPU utilization metrics"""
        try:
            gpu_metrics = GPUUtilization(
                gpu_id=gpu_data["gpu_id"],
                gpu_name=gpu_data.get("gpu_name", f"GPU_{gpu_data['gpu_id']}"),
                timestamp=datetime.now(),
                utilization_percent=gpu_data.get("utilization_percent", 0.0),
                memory_used_mb=gpu_data.get("memory_used_mb", 0.0),
                memory_total_mb=gpu_data.get("memory_total_mb", 8192.0),
                temperature_celsius=gpu_data.get("temperature", 0.0),
                power_usage_watts=gpu_data.get("power_usage", 0.0),
                active_processes=gpu_data.get("active_processes", [])
            )
            
            # Store GPU utilization (keep last 10000 entries)
            self.gpu_utilization_history.append(gpu_metrics)
            if len(self.gpu_utilization_history) > 10000:
                self.gpu_utilization_history = self.gpu_utilization_history[-10000:]
            
            # Check utilization thresholds
            if gpu_metrics.utilization_percent > self.performance_thresholds["max_gpu_utilization"]:
                logger.warning(f"High GPU utilization: {gpu_metrics.utilization_percent}% on GPU {gpu_metrics.gpu_id}")
            
            memory_usage_percent = (gpu_metrics.memory_used_mb / gpu_metrics.memory_total_mb) * 100
            if memory_usage_percent > self.performance_thresholds["max_memory_usage"]:
                logger.warning(f"High GPU memory usage: {memory_usage_percent:.1f}% on GPU {gpu_metrics.gpu_id}")
            
        except Exception as e:
            logger.error(f"Failed to track GPU utilization: {e}")
    
    async def get_ai_processing_health(self) -> Dict[str, Any]:
        """Get comprehensive AI processing health status"""
        try:
            total_models = len(self.registered_models)
            total_requests = len(self.inference_requests)
            
            # Calculate overall performance metrics
            all_metrics = []
            for model_metrics in self.inference_metrics.values():
                all_metrics.extend(model_metrics)
            
            if all_metrics:
                successful_requests = len([m for m in all_metrics if m.success])
                success_rate = successful_requests / len(all_metrics)
                
                latencies = [m.duration_ms for m in all_metrics if m.duration_ms]
                avg_latency = statistics.mean(latencies) if latencies else 0.0
                p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0.0
                
                accuracies = [m.accuracy_score for m in all_metrics if m.accuracy_score]
                avg_accuracy = statistics.mean(accuracies) if accuracies else 0.0
            else:
                success_rate = 1.0
                avg_latency = 0.0
                p95_latency = 0.0
                avg_accuracy = 0.0
            
            # GPU utilization summary
            gpu_summary = await self._get_gpu_utilization_summary()
            
            # Model performance summary
            model_performance_summary = {}
            for model_id, config in self.registered_models.items():
                model_metrics = self.inference_metrics.get(model_id, [])
                if model_metrics:
                    recent_metrics = model_metrics[-100:]  # Last 100 requests
                    model_success_rate = len([m for m in recent_metrics if m.success]) / len(recent_metrics)
                    model_avg_latency = statistics.mean([m.duration_ms for m in recent_metrics if m.duration_ms]) if recent_metrics else 0.0
                    
                    model_performance_summary[model_id] = {
                        "name": config.model_name,
                        "type": config.model_type.value,
                        "success_rate": model_success_rate,
                        "avg_latency_ms": model_avg_latency,
                        "total_requests": len(model_metrics)
                    }
            
            # Creator usage summary
            creator_usage_summary = {
                "total_creators": len(self.creator_ai_usage),
                "most_active_creators": sorted(
                    self.creator_ai_usage.items(),
                    key=lambda x: x[1]["total_requests"],
                    reverse=True
                )[:10]
            }
            
            # Calculate health score
            health_factors = [
                min(success_rate * 100, 25),
                max(0, 25 - (avg_latency / 40)),  # Latency penalty
                min(avg_accuracy * 25, 25) if avg_accuracy > 0 else 20,
                min(gpu_summary.get("efficiency_score", 0.8) * 25, 25)
            ]
            health_score = sum(health_factors)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "total_models": total_models,
                "total_requests": total_requests,
                "performance_metrics": {
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency,
                    "p95_latency_ms": p95_latency,
                    "avg_accuracy": avg_accuracy
                },
                "gpu_utilization": gpu_summary,
                "model_performance": model_performance_summary,
                "creator_usage": creator_usage_summary,
                "drift_alerts": await self._get_active_drift_alerts(),
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI processing health: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    async def get_model_analytics(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive analytics for specific model"""
        try:
            if model_id not in self.registered_models:
                return {"error": f"Model {model_id} not found"}
            
            config = self.registered_models[model_id]
            model_metrics = self.inference_metrics.get(model_id, [])
            
            # Filter recent metrics
            cutoff_time = datetime.now() - timedelta(days=days)
            recent_metrics = [m for m in model_metrics if m.start_time >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No recent metrics available"}
            
            # Performance analysis
            successful_requests = [m for m in recent_metrics if m.success]
            success_rate = len(successful_requests) / len(recent_metrics)
            
            latencies = [m.duration_ms for m in recent_metrics if m.duration_ms]
            avg_latency = statistics.mean(latencies) if latencies else 0.0
            min_latency = min(latencies) if latencies else 0.0
            max_latency = max(latencies) if latencies else 0.0
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0.0
            
            # Accuracy analysis
            accuracies = [m.accuracy_score for m in recent_metrics if m.accuracy_score]
            avg_accuracy = statistics.mean(accuracies) if accuracies else 0.0
            
            # Resource usage analysis
            cpu_usage = [m.cpu_usage_percent for m in recent_metrics]
            memory_usage = [m.memory_usage_mb for m in recent_metrics]
            gpu_usage = [m.gpu_usage_percent for m in recent_metrics if m.gpu_usage_percent > 0]
            
            avg_cpu = statistics.mean(cpu_usage) if cpu_usage else 0.0
            avg_memory = statistics.mean(memory_usage) if memory_usage else 0.0
            avg_gpu = statistics.mean(gpu_usage) if gpu_usage else 0.0
            
            # Throughput analysis
            hourly_requests = defaultdict(int)
            for metric in recent_metrics:
                hour_key = metric.start_time.strftime("%Y-%m-%d %H")
                hourly_requests[hour_key] += 1
            
            peak_hourly_requests = max(hourly_requests.values()) if hourly_requests else 0
            avg_hourly_requests = statistics.mean(hourly_requests.values()) if hourly_requests else 0
            
            # Model drift analysis
            drift_history = self.model_drift_history.get(model_id, [])
            recent_drift = [d for d in drift_history if d.timestamp >= cutoff_time]
            
            drift_analysis = {}
            if recent_drift:
                latest_drift = recent_drift[-1]
                drift_analysis = {
                    "data_drift_score": latest_drift.data_drift_score,
                    "concept_drift_score": latest_drift.concept_drift_score,
                    "performance_drift_score": latest_drift.performance_drift_score,
                    "recommendation": latest_drift.recommendation
                }
            
            # Cost analysis (simulated)
            estimated_cost_per_request = self._calculate_model_cost_per_request(config)
            total_estimated_cost = len(recent_metrics) * estimated_cost_per_request
            
            return {
                "model_id": model_id,
                "model_name": config.model_name,
                "model_type": config.model_type.value,
                "analysis_period_days": days,
                "total_requests": len(recent_metrics),
                "performance_metrics": {
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency,
                    "min_latency_ms": min_latency,
                    "max_latency_ms": max_latency,
                    "p95_latency_ms": p95_latency,
                    "avg_accuracy": avg_accuracy
                },
                "resource_usage": {
                    "avg_cpu_percent": avg_cpu,
                    "avg_memory_mb": avg_memory,
                    "avg_gpu_percent": avg_gpu
                },
                "throughput_analysis": {
                    "peak_hourly_requests": peak_hourly_requests,
                    "avg_hourly_requests": avg_hourly_requests,
                    "total_requests": len(recent_metrics)
                },
                "drift_analysis": drift_analysis,
                "cost_analysis": {
                    "estimated_cost_per_request": estimated_cost_per_request,
                    "total_estimated_cost": total_estimated_cost
                },
                "recommendations": await self._generate_model_recommendations(model_id, recent_metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model analytics: {e}")
            return {"error": str(e)}
    
    async def get_creator_ai_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get AI usage insights for specific creator"""
        try:
            if creator_id not in self.creator_ai_usage:
                return {"error": f"No AI usage data for creator {creator_id}"}
            
            usage_stats = self.creator_ai_usage[creator_id]
            
            # Get creator's inference requests
            creator_requests = [r for r in self.inference_requests.values() if r.creator_id == creator_id]
            
            # Analyze usage patterns
            model_usage = dict(usage_stats["favorite_models"])
            most_used_model = max(model_usage, key=model_usage.get) if model_usage else None
            
            # Calculate efficiency metrics
            total_processing_time = 0.0
            successful_requests = 0
            
            for request in creator_requests:
                request_metrics = [m for metrics_list in self.inference_metrics.values() 
                                for m in metrics_list if m.request_id == request.request_id]
                
                for metric in request_metrics:
                    if metric.duration_ms:
                        total_processing_time += metric.duration_ms
                    if metric.success:
                        successful_requests += 1
            
            avg_processing_time = total_processing_time / max(len(creator_requests), 1)
            success_rate = successful_requests / max(len(creator_requests), 1)
            
            # Usage recommendations
            recommendations = await self._generate_creator_ai_recommendations(creator_id, usage_stats)
            
            return {
                "creator_id": creator_id,
                "total_ai_requests": usage_stats["total_requests"],
                "model_usage_distribution": model_usage,
                "most_used_model": most_used_model,
                "performance_metrics": {
                    "avg_processing_time_ms": avg_processing_time,
                    "success_rate": success_rate,
                    "total_cost_consumed": usage_stats["cost_consumed"]
                },
                "usage_patterns": {
                    "requests_per_day": usage_stats["total_requests"] / max(30, 1),  # Approximate
                    "preferred_ai_features": list(model_usage.keys())[:5]
                },
                "recommendations": recommendations,
                "optimization_opportunities": await self._identify_creator_optimization_opportunities(creator_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get creator AI insights: {e}")
            return {"error": str(e)}
    
    async def generate_processing_insights(self) -> AIProcessingInsights:
        """Generate comprehensive AI processing insights"""
        try:
            # Calculate overall performance score
            health_data = await self.get_ai_processing_health()
            overall_performance_score = health_data.get("health_score", 0.0)
            
            # Model performance rankings
            model_rankings = []
            for model_id, config in self.registered_models.items():
                performance = self.model_performance.get(model_id, {})
                model_rankings.append({
                    "model_id": model_id,
                    "model_name": config.model_name,
                    "model_type": config.model_type.value,
                    "performance_score": (
                        performance.get("success_rate", 0.8) * 40 +
                        max(0, 40 - performance.get("avg_latency_ms", 200) / 10) +
                        performance.get("avg_accuracy", 0.8) * 20
                    ),
                    "success_rate": performance.get("success_rate", 0.8),
                    "avg_latency_ms": performance.get("avg_latency_ms", 200),
                    "throughput_rps": performance.get("throughput_rps", 1.0)
                })
            
            model_rankings.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Resource optimization opportunities
            resource_opportunities = await self._identify_resource_optimization_opportunities()
            
            # Model drift alerts
            drift_alerts = await self._get_active_drift_alerts()
            
            # Scaling recommendations
            scaling_recommendations = await self._generate_scaling_recommendations()
            
            # Cost optimization suggestions
            cost_suggestions = await self._generate_cost_optimization_suggestions()
            
            # Creator AI usage patterns
            creator_patterns = await self._analyze_creator_usage_patterns()
            
            return AIProcessingInsights(
                overall_performance_score=overall_performance_score,
                model_performance_rankings=model_rankings,
                resource_optimization_opportunities=resource_opportunities,
                model_drift_alerts=drift_alerts,
                scaling_recommendations=scaling_recommendations,
                cost_optimization_suggestions=cost_suggestions,
                creator_ai_usage_patterns=creator_patterns
            )
            
        except Exception as e:
            logger.error(f"Failed to generate processing insights: {e}")
            return AIProcessingInsights(
                overall_performance_score=0.0,
                model_performance_rankings=[],
                resource_optimization_opportunities=["Error generating insights"],
                model_drift_alerts=[],
                scaling_recommendations=[],
                cost_optimization_suggestions=[],
                creator_ai_usage_patterns={}
            )
    
    # Private helper methods
    
    async def _initialize_gpu_monitoring(self):
        """Initialize GPU monitoring"""
        try:
            # Check for available GPUs
            logger.info("GPU monitoring initialized")
        except Exception as e:
            logger.warning(f"GPU monitoring initialization failed: {e}")
    
    async def _update_model_performance(self, model_id: str, metrics: InferenceMetrics):
        """Update model performance metrics"""
        performance = self.model_performance[model_id]
        
        # Update with exponential moving average
        if metrics.duration_ms:
            performance["avg_latency_ms"] = (
                performance["avg_latency_ms"] * 0.9 + metrics.duration_ms * 0.1
            )
        
        performance["success_rate"] = (
            performance["success_rate"] * 0.9 + (1.0 if metrics.success else 0.0) * 0.1
        )
        
        if metrics.accuracy_score:
            performance["avg_accuracy"] = (
                performance["avg_accuracy"] * 0.9 + metrics.accuracy_score * 0.1
            )
        
        if metrics.throughput_requests_per_second:
            performance["throughput_rps"] = (
                performance["throughput_rps"] * 0.9 + metrics.throughput_requests_per_second * 0.1
            )
    
    async def _update_creator_usage_stats(self, creator_id: str, metrics: InferenceMetrics):
        """Update creator AI usage statistics"""
        stats = self.creator_ai_usage[creator_id]
        
        if metrics.duration_ms:
            stats["avg_processing_time"] = (
                stats["avg_processing_time"] * 0.9 + metrics.duration_ms * 0.1
            )
        
        stats["success_rate"] = (
            stats["success_rate"] * 0.9 + (1.0 if metrics.success else 0.0) * 0.1
        )
        
        # Estimate cost (simplified)
        config = self.registered_models.get(metrics.model_id)
        if config:
            cost = self._calculate_model_cost_per_request(config)
            stats["cost_consumed"] += cost
    
    async def _get_gpu_utilization_summary(self) -> Dict[str, Any]:
        """Get GPU utilization summary"""
        if not self.gpu_utilization_history:
            return {"efficiency_score": 0.8, "avg_utilization": 0.0}
        
        recent_gpu_data = self.gpu_utilization_history[-100:]  # Last 100 entries
        
        avg_utilization = statistics.mean([g.utilization_percent for g in recent_gpu_data])
        avg_memory_usage = statistics.mean([
            (g.memory_used_mb / g.memory_total_mb) * 100 for g in recent_gpu_data
        ])
        
        # Calculate efficiency score
        efficiency_score = min(1.0, avg_utilization / 80.0)  # Optimal at 80% utilization
        
        return {
            "efficiency_score": efficiency_score,
            "avg_utilization": avg_utilization,
            "avg_memory_usage_percent": avg_memory_usage,
            "total_gpus": len(set(g.gpu_id for g in recent_gpu_data))
        }
    
    async def _get_active_drift_alerts(self) -> List[Dict[str, Any]]:
        """Get active model drift alerts"""
        alerts = []
        
        for model_id, drift_history in self.model_drift_history.items():
            if not drift_history:
                continue
            
            latest_drift = drift_history[-1]
            
            # Check if any drift score exceeds threshold
            max_drift_score = max(
                latest_drift.data_drift_score,
                latest_drift.concept_drift_score,
                latest_drift.performance_drift_score
            )
            
            if max_drift_score > self.performance_thresholds["max_drift_score"]:
                config = self.registered_models.get(model_id)
                alerts.append({
                    "model_id": model_id,
                    "model_name": config.model_name if config else "Unknown",
                    "drift_score": max_drift_score,
                    "drift_type": self._get_primary_drift_type(latest_drift),
                    "recommendation": latest_drift.recommendation,
                    "timestamp": latest_drift.timestamp.isoformat()
                })
        
        return alerts
    
    def _get_primary_drift_type(self, drift_metrics: ModelDriftMetrics) -> str:
        """Get primary drift type for model"""
        scores = {
            "data": drift_metrics.data_drift_score,
            "concept": drift_metrics.concept_drift_score,
            "performance": drift_metrics.performance_drift_score
        }
        return max(scores, key=scores.get)
    
    def _calculate_model_cost_per_request(self, config: AIModelConfig) -> float:
        """Calculate estimated cost per request for model"""
        # Simplified cost calculation based on model size and GPU usage
        base_cost = 0.001  # $0.001 base cost
        size_multiplier = config.model_size_mb / 100.0  # Normalize by 100MB
        gpu_multiplier = 2.0 if config.gpu_required else 1.0
        
        return base_cost * size_multiplier * gpu_multiplier
    
    async def _generate_model_recommendations(self, model_id: str, recent_metrics: List[InferenceMetrics]) -> List[str]:
        """Generate recommendations for specific model"""
        recommendations = []
        config = self.registered_models[model_id]
        
        # Latency recommendations
        latencies = [m.duration_ms for m in recent_metrics if m.duration_ms]
        if latencies:
            avg_latency = statistics.mean(latencies)
            if avg_latency > config.target_latency_ms * 1.5:
                recommendations.append("Consider model optimization or quantization to reduce latency")
            
            if max(latencies) > avg_latency * 3:
                recommendations.append("Investigate latency spikes and consider request batching")
        
        # Accuracy recommendations
        accuracies = [m.accuracy_score for m in recent_metrics if m.accuracy_score]
        if accuracies:
            avg_accuracy = statistics.mean(accuracies)
            if avg_accuracy < config.accuracy_threshold:
                recommendations.append("Model accuracy below threshold - consider retraining or fine-tuning")
        
        # Resource usage recommendations
        gpu_usage = [m.gpu_usage_percent for m in recent_metrics if m.gpu_usage_percent > 0]
        if gpu_usage:
            avg_gpu = statistics.mean(gpu_usage)
            if avg_gpu < 30:
                recommendations.append("Low GPU utilization - consider batch size optimization")
            elif avg_gpu > 90:
                recommendations.append("High GPU utilization - consider load balancing or scaling")
        
        return recommendations[:5]
    
    async def _generate_creator_ai_recommendations(self, creator_id: str, usage_stats: Dict[str, Any]) -> List[str]:
        """Generate AI usage recommendations for creator"""
        recommendations = []
        
        # Usage efficiency recommendations
        if usage_stats["avg_processing_time"] > 5000:  # 5 seconds
            recommendations.append("Consider using faster AI models for real-time content processing")
        
        if usage_stats["success_rate"] < 0.9:
            recommendations.append("Review input data quality to improve AI processing success rate")
        
        # Cost optimization recommendations
        if usage_stats["cost_consumed"] > 100:  # $100
            recommendations.append("Explore batch processing to reduce AI processing costs")
        
        # Feature recommendations
        favorite_models = usage_stats["favorite_models"]
        if len(favorite_models) < 3:
            recommendations.append("Explore additional AI features to enhance content quality")
        
        return recommendations
    
    async def _identify_creator_optimization_opportunities(self, creator_id: str) -> List[str]:
        """Identify optimization opportunities for creator"""
        opportunities = []
        
        creator_requests = [r for r in self.inference_requests.values() if r.creator_id == creator_id]
        
        # Batch processing opportunities
        single_batch_requests = [r for r in creator_requests if r.batch_size == 1]
        if len(single_batch_requests) > len(creator_requests) * 0.8:
            opportunities.append("Implement batch processing to improve efficiency")
        
        # Model selection opportunities
        usage_stats = self.creator_ai_usage[creator_id]
        if usage_stats["avg_processing_time"] > 2000:
            opportunities.append("Consider using lighter AI models for faster processing")
        
        return opportunities
    
    async def _identify_resource_optimization_opportunities(self) -> List[str]:
        """Identify resource optimization opportunities"""
        opportunities = []
        
        # GPU utilization analysis
        if self.gpu_utilization_history:
            recent_gpu = self.gpu_utilization_history[-100:]
            avg_utilization = statistics.mean([g.utilization_percent for g in recent_gpu])
            
            if avg_utilization < 40:
                opportunities.append("Low GPU utilization - consider consolidating workloads")
            elif avg_utilization > 85:
                opportunities.append("High GPU utilization - consider adding more GPU capacity")
        
        # Model instance optimization
        for model_id, instance_count in self.model_instances.items():
            model_metrics = self.inference_metrics.get(model_id, [])
            if model_metrics:
                recent_requests = len([m for m in model_metrics[-1000:] if m.success])
                if recent_requests / instance_count < 100:  # Low requests per instance
                    opportunities.append(f"Consider reducing instances for model {model_id}")
        
        return opportunities
    
    async def _generate_scaling_recommendations(self) -> List[str]:
        """Generate scaling recommendations"""
        recommendations = []
        
        # Analyze request patterns
        total_requests = sum(len(metrics) for metrics in self.inference_metrics.values())
        if total_requests > 10000:
            recommendations.append("Consider implementing auto-scaling based on request load")
        
        # Model-specific scaling
        for model_id, metrics in self.inference_metrics.items():
            if len(metrics) > 5000:  # High volume model
                config = self.registered_models[model_id]
                recommendations.append(f"Consider horizontal scaling for {config.model_name}")
        
        return recommendations
    
    async def _generate_cost_optimization_suggestions(self) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        # Model efficiency analysis
        inefficient_models = []
        for model_id, performance in self.model_performance.items():
            if performance.get("cost_per_inference", 0) > 0.01:  # High cost threshold
                config = self.registered_models[model_id]
                inefficient_models.append(config.model_name)
        
        if inefficient_models:
            suggestions.append(f"Optimize high-cost models: {', '.join(inefficient_models[:3])}")
        
        # Resource optimization
        suggestions.extend([
            "Implement request batching to reduce per-request overhead",
            "Consider model quantization for cost-effective inference",
            "Use spot instances for non-critical AI workloads"
        ])
        
        return suggestions
    
    async def _analyze_creator_usage_patterns(self) -> Dict[str, Any]:
        """Analyze creator AI usage patterns"""
        patterns = {
            "total_active_creators": len(self.creator_ai_usage),
            "avg_requests_per_creator": 0.0,
            "most_popular_ai_features": {},
            "usage_distribution": {"light": 0, "medium": 0, "heavy": 0}
        }
        
        if self.creator_ai_usage:
            total_requests = sum(stats["total_requests"] for stats in self.creator_ai_usage.values())
            patterns["avg_requests_per_creator"] = total_requests / len(self.creator_ai_usage)
            
            # Analyze popular AI features
            feature_usage = defaultdict(int)
            for stats in self.creator_ai_usage.values():
                for model_id, count in stats["favorite_models"].items():
                    if model_id in self.registered_models:
                        model_type = self.registered_models[model_id].model_type.value
                        feature_usage[model_type] += count
            
            patterns["most_popular_ai_features"] = dict(sorted(
                feature_usage.items(), key=lambda x: x[1], reverse=True
            )[:5])
            
            # Usage distribution
            for stats in self.creator_ai_usage.values():
                requests = stats["total_requests"]
                if requests < 10:
                    patterns["usage_distribution"]["light"] += 1
                elif requests < 100:
                    patterns["usage_distribution"]["medium"] += 1
                else:
                    patterns["usage_distribution"]["heavy"] += 1
        
        return patterns
    
    async def _continuous_inference_monitoring(self):
        """Continuous monitoring of inference performance"""
        while self.active:
            try:
                # Update model performance metrics
                for model_id in self.registered_models:
                    recent_metrics = self.inference_metrics[model_id][-100:] if self.inference_metrics[model_id] else []
                    
                    if recent_metrics:
                        # Update performance scores
                        success_rate = len([m for m in recent_metrics if m.success]) / len(recent_metrics)
                        avg_latency = statistics.mean([m.duration_ms for m in recent_metrics if m.duration_ms]) if recent_metrics else 0.0
                        
                        self.model_performance[model_id]["success_rate"] = success_rate
                        self.model_performance[model_id]["avg_latency_ms"] = avg_latency
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in continuous inference monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _continuous_resource_monitoring(self):
        """Continuous monitoring of resource usage"""
        while self.active:
            try:
                # Monitor system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                self.resource_usage_stats[ResourceType.CPU].append(cpu_percent)
                self.resource_usage_stats[ResourceType.MEMORY].append(memory.percent)
                
                # Log high resource usage
                if cpu_percent > 90:
                    logger.warning(f"High CPU usage: {cpu_percent}%")
                if memory.percent > 90:
                    logger.warning(f"High memory usage: {memory.percent}%")
                
                await asyncio.sleep(60)  # 1 minute
                
            except Exception as e:
                logger.error(f"Error in continuous resource monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _continuous_model_drift_monitoring(self):
        """Continuous monitoring of model drift"""
        while self.active:
            try:
                # Check for drift alerts
                drift_alerts = await self._get_active_drift_alerts()
                
                for alert in drift_alerts:
                    if alert["drift_score"] > 0.5:  # Critical drift
                        logger.critical(f"Critical model drift detected: {alert['model_name']} ({alert['drift_score']:.3f})")
                
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Error in continuous model drift monitoring: {e}")
                await asyncio.sleep(600)
    
    async def _continuous_performance_optimization(self):
        """Continuous performance optimization"""
        while self.active:
            try:
                # Optimize model instances based on load
                for model_id, metrics in self.inference_metrics.items():
                    recent_requests = len([m for m in metrics[-1000:] if m.success])
                    current_instances = self.model_instances[model_id]
                    
                    # Simple scaling logic
                    if recent_requests > current_instances * 200:  # Scale up
                        self.model_instances[model_id] += 1
                        logger.info(f"Scaled up model {model_id} to {self.model_instances[model_id]} instances")
                    elif recent_requests < current_instances * 50 and current_instances > 1:  # Scale down
                        self.model_instances[model_id] -= 1
                        logger.info(f"Scaled down model {model_id} to {self.model_instances[model_id]} instances")
                
                await asyncio.sleep(1800)  # 30 minutes
                
            except Exception as e:
                logger.error(f"Error in continuous performance optimization: {e}")
                await asyncio.sleep(600)
    
    async def stop_monitoring(self):
        """Stop AI processing monitoring"""
        self.active = False
        logger.info("AI processing monitoring stopped")

# Global controller instance
ai_processing_controller = AIProcessingMonitoringController()

# Convenience functions for external access
async def start_ai_processing_monitoring():
    """Start AI processing monitoring"""
    return await ai_processing_controller.start_monitoring()

async def register_model(model_config: Dict[str, Any]) -> str:
    """Register AI model for monitoring"""
    return await ai_processing_controller.register_model(model_config)

async def track_inference_request(request_data: Dict[str, Any]) -> str:
    """Track AI inference request"""
    return await ai_processing_controller.track_inference_request(request_data)

async def track_inference_metrics(request_id: str, metrics_data: Dict[str, Any]):
    """Track inference metrics"""
    return await ai_processing_controller.track_inference_metrics(request_id, metrics_data)

async def get_ai_processing_health():
    """Get AI processing health"""
    return await ai_processing_controller.get_ai_processing_health()

async def get_model_analytics(model_id: str, days: int = 7):
    """Get model analytics"""
    return await ai_processing_controller.get_model_analytics(model_id, days)

async def get_creator_ai_insights(creator_id: str):
    """Get creator AI insights"""
    return await ai_processing_controller.get_creator_ai_insights(creator_id)

async def generate_processing_insights():
    """Generate AI processing insights"""
    return await ai_processing_controller.generate_processing_insights()