"""
AI Model Configuration - Enterprise Configuration Management
Enterprise configuration for AI model management and deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

try:
    try:
    from pydantic_settings import BaseSettings
    from pydantic import validator, Field
except ImportError:
    # Fallback for environments without pydantic_settings
    from pydantic import BaseModel as BaseSettings, validator, Field
except ImportError:
    # Fallback for environments without pydantic
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def validator(field_name) -> None:
        def decorator(func) -> None:
            return func
        return decorator
    
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()


class ModelType(str, Enum):
    """AI Model types"""
    LANGUAGE_MODEL = "language_model"
    VISION_MODEL = "vision_model"
    AUDIO_MODEL = "audio_model"
    MULTIMODAL_MODEL = "multimodal_model"
    CUSTOM_MODEL = "custom_model"


class ModelProvider(str, Enum):
    """AI Model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    HUGGING_FACE = "hugging_face"
    CUSTOM = "custom"
    LOCAL = "local"


class ModelStatus(str, Enum):
    """Model deployment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ERROR = "error"


class ModelTier(str, Enum):
    """Model performance tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ULTRA = "ultra"


class DeploymentMode(str, Enum):
    """Model deployment modes"""
    CLOUD = "cloud"
    EDGE = "edge"
    HYBRID = "hybrid"
    ON_PREMISE = "on_premise"


@dataclass
class ModelEndpoint:
    """Model endpoint configuration"""
    url: str
    api_key: Optional[str]
    headers: Dict[str, str]
    timeout_seconds: int
    max_retries: int
    rate_limit_per_minute: int


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    latency_ms: float
    throughput_rps: float
    error_rate: float
    cost_per_request: float
    last_updated: datetime


@dataclass
class ModelConfiguration:
    """Complete AI model configuration"""
    model_id: str
    model_name: str
    model_version: str
    model_type: ModelType
    provider: ModelProvider
    status: ModelStatus
    tier: ModelTier
    deployment_mode: DeploymentMode
    endpoint: ModelEndpoint
    metrics: ModelMetrics
    context_window: int
    max_tokens: int
    temperature: float
    capabilities: List[str]
    supported_formats: List[str]
    pricing: Dict[str, float]
    resource_requirements: Dict[str, Any]


class AIModelSettings(BaseSettings):
    """AI Model configuration settings"""
    
    # Language Models Configuration
    language_models: Dict[str, ModelConfiguration] = Field(
        default_factory=lambda: {
            "gpt-4-turbo": ModelConfiguration(
                model_id="gpt-4-turbo-2024-01",
                model_name="GPT-4 Turbo",
                model_version="2024-01",
                model_type=ModelType.LANGUAGE_MODEL,
                provider=ModelProvider.OPENAI,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.PROFESSIONAL,
                deployment_mode=DeploymentMode.CLOUD,
                endpoint=ModelEndpoint(
                    url="https://api.openai.com/v1/chat/completions",
                    api_key=None,
                    headers={"Content-Type": "application/json"},
                    timeout_seconds=30,
                    max_retries=3,
                    rate_limit_per_minute=1000
                ),
                metrics=ModelMetrics(
                    accuracy=0.96,
                    latency_ms=2500,
                    throughput_rps=10,
                    error_rate=0.01,
                    cost_per_request=0.03,
                    last_updated=datetime.now()
                ),
                context_window=128000,
                max_tokens=4096,
                temperature=0.7,
                capabilities=["text_generation", "code_generation", "analysis", "translation"],
                supported_formats=["text", "json", "markdown"],
                pricing={"input_per_1k_tokens": 0.01, "output_per_1k_tokens": 0.03},
                resource_requirements={"cpu_cores": 0, "memory_gb": 0, "gpu_memory_gb": 0}
            ),
            "claude-3.5-sonnet": ModelConfiguration(
                model_id="claude-3-5-sonnet-20241022",
                model_name="Claude 3.5 Sonnet",
                model_version="20241022",
                model_type=ModelType.LANGUAGE_MODEL,
                provider=ModelProvider.ANTHROPIC,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.ENTERPRISE,
                deployment_mode=DeploymentMode.CLOUD,
                endpoint=ModelEndpoint(
                    url="https://api.anthropic.com/v1/messages",
                    api_key=None,
                    headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
                    timeout_seconds=30,
                    max_retries=3,
                    rate_limit_per_minute=800
                ),
                metrics=ModelMetrics(
                    accuracy=0.97,
                    latency_ms=3000,
                    throughput_rps=8,
                    error_rate=0.005,
                    cost_per_request=0.015,
                    last_updated=datetime.now()
                ),
                context_window=200000,
                max_tokens=8192,
                temperature=0.7,
                capabilities=["text_generation", "analysis", "reasoning", "code_generation"],
                supported_formats=["text", "json", "markdown"],
                pricing={"input_per_1k_tokens": 0.003, "output_per_1k_tokens": 0.015},
                resource_requirements={"cpu_cores": 0, "memory_gb": 0, "gpu_memory_gb": 0}
            )
        }
    )
    
    # Vision Models Configuration
    vision_models: Dict[str, ModelConfiguration] = Field(
        default_factory=lambda: {
            "gpt-4-vision": ModelConfiguration(
                model_id="gpt-4-vision-preview",
                model_name="GPT-4 Vision",
                model_version="preview",
                model_type=ModelType.VISION_MODEL,
                provider=ModelProvider.OPENAI,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.PROFESSIONAL,
                deployment_mode=DeploymentMode.CLOUD,
                endpoint=ModelEndpoint(
                    url="https://api.openai.com/v1/chat/completions",
                    api_key=None,
                    headers={"Content-Type": "application/json"},
                    timeout_seconds=45,
                    max_retries=3,
                    rate_limit_per_minute=500
                ),
                metrics=ModelMetrics(
                    accuracy=0.92,
                    latency_ms=4000,
                    throughput_rps=5,
                    error_rate=0.02,
                    cost_per_request=0.05,
                    last_updated=datetime.now()
                ),
                context_window=128000,
                max_tokens=4096,
                temperature=0.7,
                capabilities=["image_analysis", "ocr", "object_detection", "image_description"],
                supported_formats=["jpeg", "png", "gif", "webp"],
                pricing={"input_per_1k_tokens": 0.01, "output_per_1k_tokens": 0.03},
                resource_requirements={"cpu_cores": 0, "memory_gb": 0, "gpu_memory_gb": 0}
            ),
            "claude-3-vision": ModelConfiguration(
                model_id="claude-3-sonnet-20240229",
                model_name="Claude 3 Sonnet Vision",
                model_version="20240229",
                model_type=ModelType.VISION_MODEL,
                provider=ModelProvider.ANTHROPIC,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.PROFESSIONAL,
                deployment_mode=DeploymentMode.CLOUD,
                endpoint=ModelEndpoint(
                    url="https://api.anthropic.com/v1/messages",
                    api_key=None,
                    headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
                    timeout_seconds=45,
                    max_retries=3,
                    rate_limit_per_minute=400
                ),
                metrics=ModelMetrics(
                    accuracy=0.94,
                    latency_ms=3500,
                    throughput_rps=6,
                    error_rate=0.015,
                    cost_per_request=0.04,
                    last_updated=datetime.now()
                ),
                context_window=200000,
                max_tokens=4096,
                temperature=0.7,
                capabilities=["image_analysis", "document_analysis", "chart_reading", "visual_reasoning"],
                supported_formats=["jpeg", "png", "gif", "webp", "pdf"],
                pricing={"input_per_1k_tokens": 0.003, "output_per_1k_tokens": 0.015},
                resource_requirements={"cpu_cores": 0, "memory_gb": 0, "gpu_memory_gb": 0}
            )
        }
    )
    
    # Audio Models Configuration
    audio_models: Dict[str, ModelConfiguration] = Field(
        default_factory=lambda: {
            "whisper-large": ModelConfiguration(
                model_id="whisper-large-v3",
                model_name="Whisper Large V3",
                model_version="v3",
                model_type=ModelType.AUDIO_MODEL,
                provider=ModelProvider.OPENAI,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.PROFESSIONAL,
                deployment_mode=DeploymentMode.CLOUD,
                endpoint=ModelEndpoint(
                    url="https://api.openai.com/v1/audio/transcriptions",
                    api_key=None,
                    headers={},
                    timeout_seconds=120,
                    max_retries=3,
                    rate_limit_per_minute=50
                ),
                metrics=ModelMetrics(
                    accuracy=0.96,
                    latency_ms=8000,
                    throughput_rps=2,
                    error_rate=0.01,
                    cost_per_request=0.006,
                    last_updated=datetime.now()
                ),
                context_window=0,
                max_tokens=0,
                temperature=0.0,
                capabilities=["speech_to_text", "translation", "language_detection"],
                supported_formats=["mp3", "wav", "flac", "m4a", "ogg"],
                pricing={"per_minute": 0.006},
                resource_requirements={"cpu_cores": 0, "memory_gb": 0, "gpu_memory_gb": 0}
            )
        }
    )
    
    # Custom Models Configuration
    custom_models: Dict[str, ModelConfiguration] = Field(
        default_factory=lambda: {
            "content_analyzer": ModelConfiguration(
                model_id="custom-content-analyzer-v2",
                model_name="Custom Content Analyzer",
                model_version="v2.1",
                model_type=ModelType.CUSTOM_MODEL,
                provider=ModelProvider.CUSTOM,
                status=ModelStatus.ACTIVE,
                tier=ModelTier.ENTERPRISE,
                deployment_mode=DeploymentMode.HYBRID,
                endpoint=ModelEndpoint(
                    url="http://internal-ai-service:8080/analyze",
                    api_key=None,
                    headers={"Content-Type": "application/json"},
                    timeout_seconds=60,
                    max_retries=3,
                    rate_limit_per_minute=200
                ),
                metrics=ModelMetrics(
                    accuracy=0.95,
                    latency_ms=1500,
                    throughput_rps=15,
                    error_rate=0.008,
                    cost_per_request=0.001,
                    last_updated=datetime.now()
                ),
                context_window=4096,
                max_tokens=2048,
                temperature=0.3,
                capabilities=["content_classification", "sentiment_analysis", "keyword_extraction"],
                supported_formats=["text", "json"],
                pricing={"per_request": 0.001},
                resource_requirements={"cpu_cores": 4, "memory_gb": 8, "gpu_memory_gb": 2}
            )
        }
    )
    
    # Model Management Settings
    model_management: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_model_selection": True,
            "load_balancing": True,
            "failover_enabled": True,
            "health_checks": True,
            "performance_monitoring": True,
            "cost_optimization": True,
            "a_b_testing": True,
            "version_control": True
        }
    )
    
    # Performance Optimization
    performance_optimization: Dict[str, Any] = Field(
        default_factory=lambda: {
            "request_caching": True,
            "response_caching": True,
            "batch_processing": True,
            "connection_pooling": True,
            "request_queuing": True,
            "rate_limiting": True,
            "circuit_breaker": True
        }
    )
    
    # Quality Control
    quality_control: Dict[str, Any] = Field(
        default_factory=lambda: {
            "response_validation": True,
            "confidence_scoring": True,
            "output_filtering": True,
            "bias_detection": True,
            "safety_checks": True,
            "content_moderation": True
        }
    )
    
    # Security Settings
    security_settings: Dict[str, bool] = Field(
        default_factory=lambda: {
            "api_key_rotation": True,
            "request_encryption": True,
            "response_encryption": True,
            "audit_logging": True,
            "access_control": True,
            "rate_limiting": True,
            "ddos_protection": True
        }
    )
    
    # Monitoring and Alerting
    monitoring_enabled: bool = True
    metrics_collection_interval_seconds: int = 60
    alert_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "error_rate_threshold": 0.05,
            "latency_threshold_ms": 10000,
            "cost_threshold_per_hour": 100.0,
            "availability_threshold": 0.99
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "AI_MODEL_"
        case_sensitive = False
        extra = "allow"
    
    def get_model_by_capability(self, capability: str) -> List[ModelConfiguration]:
        """Get all models that support a specific capability"""
        models = []
        all_models = {**self.language_models, **self.vision_models, 
                     **self.audio_models, **self.custom_models}
        
        for model in all_models.values():
            if capability in model.capabilities:
                models.append(model)
        
        return models
    
    def get_best_model_for_task(self, task_type: str, requirements: Dict[str, Any]) -> Optional[ModelConfiguration]:
        """Get the best model for a specific task based on requirements"""
        candidates = self.get_model_by_capability(task_type)
        
        if not candidates:
            return None
        
        # Filter by requirements
        filtered = []
        for model in candidates:
            if model.status != ModelStatus.ACTIVE:
                continue
            
            if requirements.get("max_latency_ms") and model.metrics.latency_ms > requirements["max_latency_ms"]:
                continue
            
            if requirements.get("min_accuracy") and model.metrics.accuracy < requirements["min_accuracy"]:
                continue
            
            if requirements.get("max_cost") and model.metrics.cost_per_request > requirements["max_cost"]:
                continue
            
            filtered.append(model)
        
        if not filtered:
            return None
        
        # Sort by performance score (accuracy / latency * cost factor)
        def score_model(model) -> None:
            return model.metrics.accuracy / (model.metrics.latency_ms / 1000) / max(model.metrics.cost_per_request, 0.001)
        
        return max(filtered, key=score_model)
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfiguration]:
        """Get model configuration by ID"""
        all_models = {**self.language_models, **self.vision_models, 
                     **self.audio_models, **self.custom_models}
        
        for model in all_models.values():
            if model.model_id == model_id:
                return model
        
        return None
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if a model is available and active"""
        model = self.get_model_by_id(model_id)
        return model is not None and model.status == ModelStatus.ACTIVE
    
    def get_active_models(self) -> List[ModelConfiguration]:
        """Get all active models"""
        active_models = []
        all_models = {**self.language_models, **self.vision_models, 
                     **self.audio_models, **self.custom_models}
        
        for model in all_models.values():
            if model.status == ModelStatus.ACTIVE:
                active_models.append(model)
        
        return active_models
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete AI model configuration"""
        errors = []
        
        # Validate that each model category has at least one active model
        categories = {
            "language_models": self.language_models,
            "vision_models": self.vision_models,
            "audio_models": self.audio_models
        }
        
        for category, models in categories.items():
            active_models = [m for m in models.values() if m.status == ModelStatus.ACTIVE]
            if not active_models:
                errors.append(f"No active models in category: {category}")
        
        # Validate model configurations
        all_models = {**self.language_models, **self.vision_models, 
                     **self.audio_models, **self.custom_models}
        
        for model_name, model in all_models.items():
            if not model.model_id:
                errors.append(f"Model '{model_name}' missing model_id")
            
            if not model.endpoint.url:
                errors.append(f"Model '{model_name}' missing endpoint URL")
            
            if model.metrics.accuracy < 0 or model.metrics.accuracy > 1:
                errors.append(f"Model '{model_name}' has invalid accuracy: {model.metrics.accuracy}")
            
            if model.endpoint.timeout_seconds <= 0:
                errors.append(f"Model '{model_name}' has invalid timeout: {model.endpoint.timeout_seconds}")
        
        return errors


# Global AI model settings instance
ai_model_settings = AIModelSettings()

__all__ = [
    "AIModelSettings",
    "ai_model_settings",
    "ModelType",
    "ModelProvider",
    "ModelStatus",
    "ModelTier",
    "DeploymentMode",
    "ModelEndpoint",
    "ModelMetrics",
    "ModelConfiguration"
]

# File has syntax issues - needs manual review