"""Ainflue AI Inference Configuration - Enterprise Real-Time AI Model Serving
============================================================================

Advanced AI inference configuration for enterprise-grade real-time model
serving, multi-model orchestration, auto-scaling, performance optimization,
and business logic integration for Ainflue's content intelligence platform.

Business Logic Integration:
- Real-time content analysis and recommendation
- Creator performance prediction and optimization
- Revenue forecasting and dynamic pricing
- Content moderation and safety scoring
- Multi-modal content understanding and generation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import asyncio
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """AI model types for inference"""
    LANGUAGE_MODEL = "language_model"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"
    MULTIMODAL = "multimodal"
    RECOMMENDATION = "recommendation"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class InferenceMode(str, Enum):
    """Inference execution modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    ASYNC = "async"
    EDGE = "edge"
    FEDERATED = "federated"

class ModelFramework(str, Enum):
    """Supported AI frameworks"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    TRITON = "triton"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    COREML = "coreml"

class ScalingStrategy(str, Enum):
    """Auto-scaling strategies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_BASED = "request_based"
    LATENCY_BASED = "latency_based"
    QUEUE_BASED = "queue_based"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"

class ModelStatus(str, Enum):
    """Model deployment status"""
    LOADING = "loading"
    READY = "ready"
    SCALING = "scaling"
    ERROR = "error"
    UPDATING = "updating"
    DISABLED = "disabled"

@dataclass
class ModelConfiguration:
    """Individual model configuration"""
    model_id: str
    model_name: str
    model_version: str
    model_type: ModelType
    framework: ModelFramework
    inference_mode: InferenceMode
    
    # Model artifacts
    model_path: str
    config_path: Optional[str] = None
    weights_path: Optional[str] = None
    tokenizer_path: Optional[str] = None
    
    # Resource requirements
    cpu_cores: float = 2.0
    memory_gb: float = 8.0
    gpu_memory_gb: float = 0.0
    storage_gb: float = 10.0
    
    # Performance settings
    batch_size: int = 1
    max_sequence_length: int = 512
    precision: str = "fp16"  # "fp32", "fp16", "int8", "int4"
    optimization_enabled: bool = True
    
    # Scaling configuration
    min_replicas: int = 1
    max_replicas: int = 10
    scaling_strategy: ScalingStrategy = ScalingStrategy.REQUEST_BASED
    scale_up_threshold: float = 0.7
    scale_down_threshold: float = 0.3
    
    # Business logic settings
    business_use_cases: List[str] = field(default_factory=list)
    creator_types: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    priority_level: int = 1  # 1=highest, 5=lowest
    
    # Monitoring and health
    health_check_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: ModelStatus = ModelStatus.LOADING

@dataclass
class InferenceRequest:
    """AI inference request"""
    request_id: str
    model_id: str
    input_data: Dict[str, Any]
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout_seconds: int = 30
    callback_url: Optional[str] = None
    
    # Business context
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    # Request metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "processing", "completed", "failed"

@dataclass
class InferenceResult:
    """AI inference result"""
    request_id: str
    model_id: str
    predictions: Any
    confidence_scores: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    inference_time_ms: float = 0.0
    queue_time_ms: float = 0.0
    preprocessing_time_ms: float = 0.0
    postprocessing_time_ms: float = 0.0
    
    # Quality metrics
    prediction_quality: Optional[float] = None
    uncertainty_score: Optional[float] = None
    explanation: Optional[Dict[str, Any]] = None
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

class EnterpriseAIInferenceConfiguration:
    """Enterprise-grade AI inference configuration management"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize AI inference configuration"""
        self.level = level
        self.model_configurations: Dict[str, ModelConfiguration] = {}
        self.active_models: Dict[str, Dict[str, Any]] = {}
        self.inference_queue: List[InferenceRequest] = []
        self.inference_history: List[InferenceResult] = []
        
        # Configuration settings
        self.config = self._load_configuration()
        self._initialize_model_configurations()
        self._setup_inference_pipeline()
        self._configure_monitoring_systems()
        
        logger.info(f"🧠 Enterprise AI Inference Configuration initialized - Level: {self.level}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load AI inference configuration settings"""
        return {
            "global_settings": {
                "max_concurrent_requests": 1000,
                "default_timeout_seconds": 30,
                "queue_size_limit": 10000,
                "auto_scaling_enabled": True,
                "model_warming_enabled": True,
                "request_batching_enabled": True,
                "caching_enabled": True,
                "monitoring_enabled": True
            },
            
            "infrastructure": {
                "deployment_platform": "kubernetes",
                "model_serving_framework": "triton",
                "load_balancer": "nginx",
                "service_mesh": "istio",
                "container_registry": "harbor",
                "artifact_storage": "s3",
                "metrics_backend": "prometheus",
                "logging_backend": "elasticsearch"
            },
            
            "performance_optimization": {
                "tensor_parallelism": True,
                "pipeline_parallelism": True,
                "dynamic_batching": True,
                "request_padding": True,
                "model_quantization": True,
                "graph_optimization": True,
                "kernel_fusion": True,
                "memory_pooling": True
            },
            
            "business_models": {
                "content_recommender": {
                    "model_type": ModelType.RECOMMENDATION,
                    "framework": ModelFramework.PYTORCH,
                    "use_cases": ["content_discovery", "creator_matching", "personalization"],
                    "priority": 1,
                    "sla_ms": 100,
                    "availability": 99.9
                },
                
                "content_analyzer": {
                    "model_type": ModelType.MULTIMODAL,
                    "framework": ModelFramework.HUGGINGFACE,
                    "use_cases": ["content_tagging", "quality_scoring", "trend_detection"],
                    "priority": 1,
                    "sla_ms": 200,
                    "availability": 99.9
                },
                
                "revenue_optimizer": {
                    "model_type": ModelType.REINFORCEMENT_LEARNING,
                    "framework": ModelFramework.PYTORCH,
                    "use_cases": ["pricing_optimization", "monetization_strategy", "revenue_forecasting"],
                    "priority": 2,
                    "sla_ms": 500,
                    "availability": 99.5
                },
                
                "content_moderator": {
                    "model_type": ModelType.CLASSIFICATION,
                    "framework": ModelFramework.ONNX,
                    "use_cases": ["safety_scoring", "compliance_check", "violation_detection"],
                    "priority": 1,
                    "sla_ms": 150,
                    "availability": 99.95
                },
                
                "creator_performance_predictor": {
                    "model_type": ModelType.REGRESSION,
                    "framework": ModelFramework.TENSORFLOW,
                    "use_cases": ["performance_forecasting", "growth_prediction", "engagement_estimation"],
                    "priority": 2,
                    "sla_ms": 300,
                    "availability": 99.0
                },
                
                "audio_enhancer": {
                    "model_type": ModelType.AUDIO_PROCESSING,
                    "framework": ModelFramework.PYTORCH,
                    "use_cases": ["noise_reduction", "quality_enhancement", "mastering"],
                    "priority": 2,
                    "sla_ms": 1000,
                    "availability": 99.0
                },
                
                "video_analyzer": {
                    "model_type": ModelType.COMPUTER_VISION,
                    "framework": ModelFramework.TENSORRT,
                    "use_cases": ["scene_detection", "object_recognition", "quality_assessment"],
                    "priority": 2,
                    "sla_ms": 800,
                    "availability": 99.0
                },
                
                "text_generator": {
                    "model_type": ModelType.LANGUAGE_MODEL,
                    "framework": ModelFramework.HUGGINGFACE,
                    "use_cases": ["content_generation", "title_optimization", "description_enhancement"],
                    "priority": 3,
                    "sla_ms": 2000,
                    "availability": 98.0
                }
            },
            
            "scaling_policies": {
                "high_priority_models": {
                    "min_replicas": 3,
                    "max_replicas": 50,
                    "target_cpu_utilization": 60,
                    "scale_up_cooldown": 30,  # seconds
                    "scale_down_cooldown": 180
                },
                "medium_priority_models": {
                    "min_replicas": 2,
                    "max_replicas": 20,
                    "target_cpu_utilization": 70,
                    "scale_up_cooldown": 60,
                    "scale_down_cooldown": 300
                },
                "low_priority_models": {
                    "min_replicas": 1,
                    "max_replicas": 10,
                    "target_cpu_utilization": 80,
                    "scale_up_cooldown": 120,
                    "scale_down_cooldown": 600
                }
            },
            
            "caching_configuration": {
                "result_caching": {
                    "enabled": True,
                    "ttl_seconds": 3600,
                    "max_cache_size": "10GB",
                    "cache_key_strategy": "input_hash"
                },
                "model_caching": {
                    "enabled": True,
                    "warm_models": ["content_recommender", "content_moderator"],
                    "cache_memory_limit": "50GB"
                },
                "request_deduplication": {
                    "enabled": True,
                    "dedup_window_seconds": 60,
                    "similarity_threshold": 0.95
                }
            },
            
            "monitoring_configuration": {
                "performance_metrics": [
                    "request_rate", "latency_p50", "latency_p95", "latency_p99",
                    "error_rate", "throughput", "queue_length", "cache_hit_ratio"
                ],
                "business_metrics": [
                    "recommendation_quality", "content_safety_score", 
                    "revenue_optimization_impact", "creator_satisfaction"
                ],
                "alerting_rules": {
                    "high_latency": {"threshold": 1000, "duration": "5m"},
                    "high_error_rate": {"threshold": 0.05, "duration": "2m"},
                    "queue_overflow": {"threshold": 5000, "duration": "1m"},
                    "model_unavailable": {"threshold": 1, "duration": "30s"}
                }
            },
            
            "security_configuration": {
                "input_validation": True,
                "output_sanitization": True,
                "rate_limiting": {
                    "requests_per_minute": 1000,
                    "burst_size": 100
                },
                "authentication": {
                    "api_key_required": True,
                    "jwt_validation": True,
                    "rbac_enabled": True
                },
                "data_privacy": {
                    "pii_detection": True,
                    "data_anonymization": True,
                    "audit_logging": True
                }
            }
        }
    
    def _initialize_model_configurations(self) -> None:
        """Initialize model configurations for Ainflue business logic"""
        
        # Content Recommendation Model
        content_recommender = ModelConfiguration(
            model_id="ainflue_content_recommender_v2",
            model_name="Ainflue Content Recommender",
            model_version="2.1.0",
            model_type=ModelType.RECOMMENDATION,
            framework=ModelFramework.PYTORCH,
            inference_mode=InferenceMode.REAL_TIME,
            model_path="/models/content_recommender/model.pt",
            config_path="/models/content_recommender/config.json",
            cpu_cores=4.0,
            memory_gb=16.0,
            gpu_memory_gb=8.0,
            batch_size=32,
            max_sequence_length=1024,
            precision="fp16",
            min_replicas=3,
            max_replicas=50,
            scaling_strategy=ScalingStrategy.REQUEST_BASED,
            business_use_cases=["content_discovery", "creator_matching", "personalization"],
            creator_types=["blogger", "musician", "photographer", "videographer", "influencer"],
            content_types=["text", "audio", "video", "image"],
            priority_level=1,
            timeout_seconds=10
        )
        
        # Content Safety Moderator
        content_moderator = ModelConfiguration(
            model_id="ainflue_content_moderator_v1",
            model_name="Ainflue Content Safety Moderator",
            model_version="1.3.0",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.ONNX,
            inference_mode=InferenceMode.REAL_TIME,
            model_path="/models/content_moderator/model.onnx",
            cpu_cores=2.0,
            memory_gb=8.0,
            batch_size=16,
            precision="fp16",
            min_replicas=2,
            max_replicas=30,
            business_use_cases=["safety_scoring", "compliance_check", "violation_detection"],
            creator_types=["all"],
            content_types=["text", "audio", "video", "image"],
            priority_level=1,
            timeout_seconds=5
        )
        
        # Revenue Optimization Engine
        revenue_optimizer = ModelConfiguration(
            model_id="ainflue_revenue_optimizer_v1",
            model_name="Ainflue Revenue Optimization Engine",
            model_version="1.0.0",
            model_type=ModelType.REINFORCEMENT_LEARNING,
            framework=ModelFramework.PYTORCH,
            inference_mode=InferenceMode.ASYNC,
            model_path="/models/revenue_optimizer/model.pt",
            cpu_cores=6.0,
            memory_gb=24.0,
            gpu_memory_gb=12.0,
            batch_size=64,
            min_replicas=2,
            max_replicas=15,
            business_use_cases=["pricing_optimization", "monetization_strategy", "revenue_forecasting"],
            creator_types=["creator", "pro", "enterprise"],
            priority_level=2,
            timeout_seconds=30
        )
        
        # Multimodal Content Analyzer
        content_analyzer = ModelConfiguration(
            model_id="ainflue_multimodal_analyzer_v2",
            model_name="Ainflue Multimodal Content Analyzer",
            model_version="2.0.0",
            model_type=ModelType.MULTIMODAL,
            framework=ModelFramework.HUGGINGFACE,
            inference_mode=InferenceMode.BATCH,
            model_path="/models/multimodal_analyzer/",
            tokenizer_path="/models/multimodal_analyzer/tokenizer/",
            cpu_cores=8.0,
            memory_gb=32.0,
            gpu_memory_gb=16.0,
            batch_size=8,
            max_sequence_length=2048,
            min_replicas=1,
            max_replicas=20,
            business_use_cases=["content_tagging", "quality_scoring", "trend_detection"],
            creator_types=["all"],
            content_types=["multimodal"],
            priority_level=2,
            timeout_seconds=60
        )
        
        # Creator Performance Predictor
        performance_predictor = ModelConfiguration(
            model_id="ainflue_performance_predictor_v1",
            model_name="Ainflue Creator Performance Predictor",
            model_version="1.2.0",
            model_type=ModelType.REGRESSION,
            framework=ModelFramework.TENSORFLOW,
            inference_mode=InferenceMode.BATCH,
            model_path="/models/performance_predictor/saved_model",
            cpu_cores=4.0,
            memory_gb=16.0,
            batch_size=128,
            min_replicas=1,
            max_replicas=10,
            business_use_cases=["performance_forecasting", "growth_prediction", "engagement_estimation"],
            creator_types=["all"],
            priority_level=3,
            timeout_seconds=120
        )
        
        # Store model configurations
        models = [
            content_recommender, content_moderator, revenue_optimizer,
            content_analyzer, performance_predictor
        ]
        
        for model in models:
            self.model_configurations[model.model_id] = model
        
        logger.info(f"✅ Initialized {len(models)} model configurations")
    
    def _setup_inference_pipeline(self) -> None:
        """Setup inference pipeline configuration"""
        self.pipeline_config = {
            "preprocessing": {
                "text": ["tokenization", "normalization", "encoding"],
                "audio": ["resampling", "feature_extraction", "normalization"],
                "video": ["frame_extraction", "resizing", "normalization"],
                "image": ["resizing", "normalization", "augmentation"],
                "multimodal": ["modality_alignment", "feature_fusion"]
            },
            
            "postprocessing": {
                "recommendations": ["ranking", "filtering", "diversity_boost"],
                "classifications": ["probability_calibration", "threshold_application"],
                "regressions": ["scaling", "uncertainty_estimation"],
                "generations": ["safety_filtering", "quality_scoring"]
            },
            
            "request_routing": {
                "strategy": "round_robin",  # "round_robin", "least_connections", "weighted"
                "health_check_enabled": True,
                "circuit_breaker_enabled": True,
                "retry_policy": {
                    "max_retries": 3,
                    "retry_delay_ms": 100,
                    "exponential_backoff": True
                }
            },
            
            "batch_processing": {
                "enabled": True,
                "max_batch_size": 64,
                "batch_timeout_ms": 50,
                "batch_padding": True
            }
        }
        
        logger.info("🔄 Inference pipeline configured")
    
    def _configure_monitoring_systems(self) -> None:
        """Configure monitoring and observability systems"""
        self.monitoring_config = {
            "metrics_collection": {
                "enabled": True,
                "collection_interval_seconds": 10,
                "retention_days": 90,
                "custom_metrics": [
                    "business_value_generated",
                    "creator_satisfaction_score",
                    "revenue_optimization_impact"
                ]
            },
            
            "distributed_tracing": {
                "enabled": True,
                "sampling_rate": 0.1,
                "trace_headers": ["request-id", "user-id", "creator-id"]
            },
            
            "health_monitoring": {
                "model_health_checks": True,
                "infrastructure_monitoring": True,
                "business_kpi_tracking": True,
                "anomaly_detection": True
            }
        }
        
        logger.info("📊 Monitoring systems configured")
    
    async def submit_inference_request(self, request: InferenceRequest) -> str:
        """Submit an inference request to the queue"""
        try:
            # Validate request
            if request.model_id not in self.model_configurations:
                raise ValueError(f"Model '{request.model_id}' not found")
            
            # Add to queue
            self.inference_queue.append(request)
            request.status = "queued"
            
            # Process request based on mode
            model_config = self.model_configurations[request.model_id]
            
            if model_config.inference_mode == InferenceMode.REAL_TIME:
                # Process immediately
                result = await self._process_inference_request(request)
                return result.request_id
            else:
                # Queue for batch processing
                logger.info(f"📥 Queued inference request: {request.request_id}")
                return request.request_id
                
        except Exception as e:
            logger.error(f"❌ Failed to submit inference request: {str(e)}")
            raise
    
    async def _process_inference_request(self, request: InferenceRequest) -> InferenceResult:
        """Process an individual inference request"""
        start_time = datetime.utcnow()
        request.started_at = start_time
        request.status = "processing"
        
        try:
            model_config = self.model_configurations[request.model_id]
            
            # Simulate inference processing
            # In production, this would call the actual model serving infrastructure
            await asyncio.sleep(0.1)  # Simulated inference time
            
            # Generate mock result based on model type
            result = self._generate_mock_result(request, model_config)
            
            # Calculate performance metrics
            end_time = datetime.utcnow()
            inference_time = (end_time - start_time).total_seconds() * 1000
            
            result.inference_time_ms = inference_time
            request.completed_at = end_time
            request.status = "completed"
            
            # Store result
            self.inference_history.append(result)
            
            logger.info(f"✅ Completed inference: {request.request_id} in {inference_time:.2f}ms")
            return result
            
        except Exception as e:
            request.status = "failed"
            logger.error(f"❌ Inference failed for request {request.request_id}: {str(e)}")
            raise
    
    def _generate_mock_result(self, request: InferenceRequest, model_config: ModelConfiguration) -> InferenceResult:
        """Generate mock inference result for testing"""
        result = InferenceResult(
            request_id=request.request_id,
            model_id=request.model_id
        )
        
        # Generate appropriate mock predictions based on model type
        if model_config.model_type == ModelType.RECOMMENDATION:
            result.predictions = [
                {"content_id": f"content_{i}", "score": 0.9 - i * 0.1}
                for i in range(10)
            ]
            result.confidence_scores = [0.95, 0.92, 0.88, 0.85, 0.82, 0.78, 0.75, 0.71, 0.68, 0.65]
            
        elif model_config.model_type == ModelType.CLASSIFICATION:
            result.predictions = {
                "safe": 0.92,
                "unsafe": 0.08,
                "categories": ["appropriate_content", "educational"]
            }
            result.confidence_scores = [0.92]
            
        elif model_config.model_type == ModelType.REGRESSION:
            result.predictions = {
                "predicted_engagement": 0.75,
                "predicted_revenue": 1250.50,
                "confidence_interval": [1100.0, 1400.0]
            }
            result.uncertainty_score = 0.15
            
        elif model_config.model_type == ModelType.MULTIMODAL:
            result.predictions = {
                "content_tags": ["music", "electronic", "energetic"],
                "quality_score": 0.87,
                "sentiment": "positive",
                "trending_probability": 0.64
            }
            result.confidence_scores = [0.92, 0.87, 0.89, 0.64]
            
        # Add metadata
        result.metadata = {
            "model_version": model_config.model_version,
            "inference_mode": model_config.inference_mode.value,
            "business_context": request.business_context
        }
        
        # Add explanation for transparency
        result.explanation = {
            "feature_importance": {"content_quality": 0.4, "creator_reputation": 0.3, "trending_factors": 0.3},
            "decision_factors": ["High content quality score", "Strong creator engagement history"]
        }
        
        return result
    
    def get_model_status(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a deployed model"""
        if model_id not in self.model_configurations:
            return None
        
        config = self.model_configurations[model_id]
        
        # Calculate recent performance metrics
        recent_requests = [
            r for r in self.inference_history
            if r.model_id == model_id and r.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        avg_latency = (
            sum(r.inference_time_ms for r in recent_requests) / len(recent_requests)
            if recent_requests else 0
        )
        
        return {
            "model_id": config.model_id,
            "model_name": config.model_name,
            "version": config.model_version,
            "status": config.status.value,
            "framework": config.framework.value,
            "inference_mode": config.inference_mode.value,
            "current_replicas": config.min_replicas,  # Simplified
            "resource_usage": {
                "cpu_cores": config.cpu_cores,
                "memory_gb": config.memory_gb,
                "gpu_memory_gb": config.gpu_memory_gb
            },
            "performance_metrics": {
                "recent_requests": len(recent_requests),
                "average_latency_ms": round(avg_latency, 2),
                "success_rate": 0.99,  # Mock value
                "throughput_rps": 150   # Mock value
            },
            "business_metrics": {
                "use_cases": config.business_use_cases,
                "creator_types": config.creator_types,
                "priority_level": config.priority_level
            },
            "last_updated": config.updated_at.isoformat()
        }
    
    def get_inference_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive inference analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_results = [
            r for r in self.inference_history
            if r.timestamp > cutoff_time
        ]
        
        if not recent_results:
            return {"error": "No inference data found for the specified period"}
        
        # Calculate analytics
        total_requests = len(recent_results)
        avg_latency = sum(r.inference_time_ms for r in recent_results) / total_requests
        
        # Group by model
        model_stats = {}
        for result in recent_results:
            model_id = result.model_id
            if model_id not in model_stats:
                model_stats[model_id] = {"count": 0, "total_latency": 0}
            model_stats[model_id]["count"] += 1
            model_stats[model_id]["total_latency"] += result.inference_time_ms
        
        # Calculate per-model averages
        for model_id, stats in model_stats.items():
            stats["avg_latency"] = stats["total_latency"] / stats["count"]
        
        return {
            "period_hours": hours,
            "summary": {
                "total_requests": total_requests,
                "average_latency_ms": round(avg_latency, 2),
                "requests_per_hour": round(total_requests / hours, 2),
                "unique_models_used": len(model_stats)
            },
            "model_performance": {
                model_id: {
                    "requests": stats["count"],
                    "avg_latency_ms": round(stats["avg_latency"], 2),
                    "percentage_of_total": round(stats["count"] / total_requests * 100, 2)
                }
                for model_id, stats in model_stats.items()
            },
            "business_impact": {
                "content_recommendations_served": model_stats.get("ainflue_content_recommender_v2", {}).get("count", 0),
                "safety_checks_performed": model_stats.get("ainflue_content_moderator_v1", {}).get("count", 0),
                "revenue_optimizations": model_stats.get("ainflue_revenue_optimizer_v1", {}).get("count", 0)
            },
            "quality_metrics": {
                "average_confidence": round(
                    sum(
                        sum(r.confidence_scores) / len(r.confidence_scores)
                        for r in recent_results if r.confidence_scores
                    ) / len([r for r in recent_results if r.confidence_scores]), 3
                ) if any(r.confidence_scores for r in recent_results) else None
            }
        }
    
    def update_model_configuration(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """Update model configuration"""
        try:
            if model_id not in self.model_configurations:
                logger.error(f"❌ Model '{model_id}' not found")
                return False
            
            config = self.model_configurations[model_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.utcnow()
            logger.info(f"✅ Updated model configuration: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update model configuration: {str(e)}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get comprehensive inference configuration summary"""
        active_models = [m for m in self.model_configurations.values() if m.status == ModelStatus.READY]
        
        return {
            "configuration_level": self.level,
            "total_models": len(self.model_configurations),
            "active_models": len(active_models),
            "queue_length": len(self.inference_queue),
            "total_inference_history": len(self.inference_history),
            "models_by_type": {
                model_type.value: len([m for m in self.model_configurations.values() if m.model_type == model_type])
                for model_type in ModelType
            },
            "models_by_framework": {
                framework.value: len([m for m in self.model_configurations.values() if m.framework == framework])
                for framework in ModelFramework
            },
            "business_coverage": {
                "recommendation_models": len([m for m in active_models if "recommendation" in m.business_use_cases]),
                "safety_models": len([m for m in active_models if "safety" in " ".join(m.business_use_cases)]),
                "revenue_models": len([m for m in active_models if "revenue" in " ".join(m.business_use_cases)]),
                "content_analysis_models": len([m for m in active_models if "content" in " ".join(m.business_use_cases)])
            },
            "infrastructure": {
                "auto_scaling_enabled": self.config["global_settings"]["auto_scaling_enabled"],
                "caching_enabled": self.config["global_settings"]["caching_enabled"],
                "monitoring_enabled": self.config["global_settings"]["monitoring_enabled"],
                "max_concurrent_requests": self.config["global_settings"]["max_concurrent_requests"]
            },
            "last_updated": datetime.utcnow().isoformat()
        }

# Global AI inference configuration instance
ai_inference_config = EnterpriseAIInferenceConfiguration("enterprise")

# Export main configuration
__all__ = ["EnterpriseAIInferenceConfiguration", "ModelType", "InferenceMode", 
           "ModelFramework", "ScalingStrategy", "ModelStatus", "ModelConfiguration",
           "InferenceRequest", "InferenceResult", "ai_inference_config"]

logger.info("🧠 Enterprise AI Inference Configuration loaded successfully")
logger.info(f"📊 Total models configured: {len(ai_inference_config.model_configurations)}")
logger.info(f"🎯 Business models: {len([m for m in ai_inference_config.model_configurations.values() if m.business_use_cases])}")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
