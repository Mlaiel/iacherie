"""Base Models and Core Components for AI Models
Foundational classes and interfaces for all AI model implementations

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json

from .exceptions import ModelError, ValidationError


class ModelType(Enum):
    """Enumeration of supported AI model types"""
    AUDIO_MODEL = "audio_model"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_MODEL = "video_model"
    VIDEO_ANALYSIS = "video_analysis"
    IMAGE_MODEL = "image_model"
    IMAGE_RECOGNITION = "image_recognition"
    TEXT_MODEL = "text_model"
    TEXT_GENERATION = "text_generation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_PROTECTION = "content_protection"
    COPYRIGHT_DETECTION = "copyright_detection"
    WATERMARK_DETECTION = "watermark_detection"
    PROTECTION_MODEL = "protection_model"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    TREND_ANALYSIS = "trend_analysis"
    COLLABORATION_MATCHING = "collaboration_matching"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    MULTIMODAL = "multimodal"
    MULTIMODAL_FUSION = "multimodal_fusion"
    CROSS_MODAL_SEARCH = "cross_modal_search"


class ModelProvider(Enum):
    """Enumeration of model providers"""
    LOCAL = "local"
    CLOUD = "cloud"
    GPU = "gpu"
    EDGE = "edge"
    HYBRID = "hybrid"


class ModelStatus(Enum):
    """Model status enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    LOADING = "loading"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ModelConfig:
    """Configuration for AI models"""
    name: str
    provider: ModelProvider
    model_type: ModelType
    version: str = "1.0.0"
    timeout: int = 30
    max_memory_mb: int = 1024
    priority: int = 1
    gpu_enabled: bool = False
    batch_size: int = 1
    config_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.name:
            raise ValidationError("Model name cannot be empty")
        if self.timeout <= 0:
            raise ValidationError("Timeout must be positive")
        if self.max_memory_mb <= 0:
            raise ValidationError("Memory limit must be positive")


@dataclass
class ModelMetrics:
    """Model performance and usage metrics"""
    model_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_used: Optional[datetime] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    error_rate: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass
class ProcessingResult:
    """Standard result structure for AI model processing"""
    success: bool
    data: Any
    confidence: float = 0.0
    processing_time: float = 0.0
    model_version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    fingerprint: Optional[str] = None


class BaseAIModel(ABC):
    """Abstract base class for all AI models"""
    
    def __init__(self, config: ModelConfig):
        """Initialize base model with configuration"""
        self.config = config
        self.model_type = config.model_type
        self.provider = config.provider
        self.status = ModelStatus.INITIALIZING
        self.metrics = ModelMetrics(model_name=config.name)
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self._is_connected = False
        self._model_instance = None
        
    @property
    def is_connected(self) -> bool:
        """Check if model is connected and ready"""
        return self._is_connected
    
    @property
    def model_name(self) -> str:
        """Get model name"""
        return self.config.name
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect and initialize the model"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect and cleanup the model"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources and disconnect"""
        await self.disconnect()
    
    @abstractmethod
    async def process(self, input_data: Any, **kwargs) -> Any:
        """Process input data and return results"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the model"""
        try:
            # Basic health check
            health_status = {
                "model_name": self.model_name,
                "status": self.status.value,
                "is_connected": self.is_connected,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "success_rate": self.metrics.success_rate,
                "timestamp": datetime.now().isoformat()
            }
            
            # Additional checks can be implemented by subclasses
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "model_name": self.model_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def update_metrics(self, success: bool, response_time: float):
        """Update model performance metrics"""
        self.metrics.total_requests += 1
        self.metrics.last_used = datetime.now()
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Update average response time
        if self.metrics.total_requests == 1:
            self.metrics.average_response_time = response_time
        else:
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time) 
                / self.metrics.total_requests
            )
        
        # Update error rate
        self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
    
    async def get_metrics(self) -> ModelMetrics:
        """Get current model metrics"""
        return self.metrics
    
    async def reset_metrics(self) -> None:
        """Reset model metrics"""
        self.metrics = ModelMetrics(model_name=self.config.name)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.model_name}, type={self.model_type.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class AudioModel(BaseAIModel):
    """Base class for audio processing models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type != ModelType.AUDIO_MODEL:
            raise ValidationError("AudioModel requires AUDIO_MODEL type")


class VideoModel(BaseAIModel):
    """Base class for video processing models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type != ModelType.VIDEO_MODEL:
            raise ValidationError("VideoModel requires VIDEO_MODEL type")


class ImageModel(BaseAIModel):
    """Base class for image processing models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type != ModelType.IMAGE_MODEL:
            raise ValidationError("ImageModel requires IMAGE_MODEL type")


class TextModel(BaseAIModel):
    """Base class for text processing models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type not in [ModelType.TEXT_MODEL, ModelType.TEXT_GENERATION]:
            raise ValidationError("TextModel requires TEXT_MODEL or TEXT_GENERATION type")


class ProtectionModel(BaseAIModel):
    """Base class for content protection models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type != ModelType.PROTECTION_MODEL:
            raise ValidationError("ProtectionModel requires PROTECTION_MODEL type")


class BusinessIntelligenceModel(BaseAIModel):
    """Base class for business intelligence models"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if config.model_type != ModelType.BUSINESS_INTELLIGENCE:
            raise ValidationError("BusinessIntelligenceModel requires BUSINESS_INTELLIGENCE type")


# Factory functions for creating models
def create_audio_model(config: ModelConfig) -> AudioModel:
    """Factory function to create audio models"""
    return AudioModel(config)


def create_video_model(config: ModelConfig) -> VideoModel:
    """Factory function to create video models"""
    return VideoModel(config)


def create_image_model(config: ModelConfig) -> ImageModel:
    """Factory function to create image models"""
    return ImageModel(config)


def create_text_model(config: ModelConfig) -> TextModel:
    """Factory function to create text models"""
    return TextModel(config)


def create_protection_model(config: ModelConfig) -> ProtectionModel:
    """Factory function to create protection models"""
    return ProtectionModel(config)


def create_business_intelligence_model(config: ModelConfig) -> BusinessIntelligenceModel:
    """Factory function to create business intelligence models"""
    return BusinessIntelligenceModel(config)


# Model registry for tracking available models
MODEL_REGISTRY = {
    ModelType.AUDIO_MODEL: create_audio_model,
    ModelType.VIDEO_MODEL: create_video_model,
    ModelType.IMAGE_MODEL: create_image_model,
    ModelType.TEXT_MODEL: create_text_model,
    ModelType.TEXT_GENERATION: create_text_model,
    ModelType.PROTECTION_MODEL: create_protection_model,
    ModelType.BUSINESS_INTELLIGENCE: create_business_intelligence_model,
}


async def create_model(config: ModelConfig) -> BaseAIModel:
    """Create a model instance based on configuration"""
    if config.model_type not in MODEL_REGISTRY:
        raise ModelError(f"Unsupported model type: {config.model_type}")
    
    factory_func = MODEL_REGISTRY[config.model_type]
    model = factory_func(config)
    
    return model


__all__ = [
    "BaseAIModel",
    "AudioModel", 
    "VideoModel",
    "ImageModel",
    "TextModel",
    "ProtectionModel",
    "BusinessIntelligenceModel",
    "ModelConfig",
    "ModelType",
    "ModelProvider", 
    "ModelStatus",
    "ModelMetrics",
    "ProcessingResult",
    "create_model",
    "create_audio_model",
    "create_video_model", 
    "create_image_model",
    "create_text_model",
    "create_protection_model",
    "create_business_intelligence_model",
    "MODEL_REGISTRY"
]
