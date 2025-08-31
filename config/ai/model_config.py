"""AI Model Configuration for IA-Influencer Agent Platform
======================================================

Professional AI/ML model configuration and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseSettings, validator
import torch
import os
from enum import Enum
from dataclasses import dataclass


class ModelType(str, Enum):
    """Supported AI model types for content processing."""
    
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    AUDIO_ANALYSIS = "audio_analysis"
    MULTIMODAL = "multimodal"
    FINGERPRINTING = "fingerprinting"
    RECOMMENDATION = "recommendation"
    GENERATION = "generation"
    CLASSIFICATION = "classification"


class ModelProvider(str, Enum):
    """AI model providers and sources."""
    
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PYTORCH_HUB = "pytorch_hub"
    TENSORFLOW_HUB = "tensorflow_hub"
    CUSTOM = "custom"
    LOCAL = "local"


@dataclass
class ModelSpec:
    """Specification for AI model configuration."""
    
    name: str
    provider: ModelProvider
    model_type: ModelType
    model_path: str
    input_size: Optional[Union[int, tuple]] = None
    num_classes: Optional[int] = None
    pretrained: bool = True
    device: str = "auto"
    precision: str = "float32"
    batch_size: int = 32
    max_sequence_length: Optional[int] = None
    requires_gpu: bool = False
    memory_requirement_mb: int = 1024
    api_key_required: bool = False
    custom_config: Optional[Dict[str, Any]] = None


class AIModelConfig(BaseSettings):
    """
    Professional AI Model Configuration for IA-Influencer Agent.
    
    Manages all AI/ML models used across the platform for content processing,
    protection, analysis, and recommendation systems.
    """
    
    # Model Registry Configuration
    MODEL_REGISTRY_URL: str = "https://huggingface.co/"
    MODEL_CACHE_DIR: str = "/tmp/ia_influencer_models"
    MODEL_AUTO_UPDATE: bool = False
    MODEL_FALLBACK_ENABLED: bool = True
    
    # Device and Hardware Configuration
    DEFAULT_DEVICE: str = "auto"  # auto, cpu, cuda, mps
    CUDA_VISIBLE_DEVICES: Optional[str] = None
    MODEL_PARALLEL_ENABLED: bool = False
    MIXED_PRECISION_ENABLED: bool = True
    
    # Performance Configuration
    MAX_BATCH_SIZE: int = 64
    MODEL_WARMUP_ENABLED: bool = True
    MODEL_CACHING_ENABLED: bool = True
    INFERENCE_OPTIMIZATION: bool = True
    
    # Audio Analysis Models
    AUDIO_FINGERPRINT_MODEL: str = "facebook/wav2vec2-base"
    MUSIC_GENRE_CLASSIFIER: str = "facebook/wav2vec2-base-960h"
    AUDIO_SIMILARITY_MODEL: str = "openai/whisper-base"
    BEAT_TRACKING_MODEL: str = "librosa/beat_tracker"
    
    # Computer Vision Models
    IMAGE_FINGERPRINT_MODEL: str = "openai/clip-vit-base-patch32"
    VIDEO_FRAME_ANALYZER: str = "google/vit-base-patch16-224"
    OBJECT_DETECTION_MODEL: str = "facebook/detr-resnet-50"
    IMAGE_SIMILARITY_MODEL: str = "sentence-transformers/clip-ViT-B-32"
    
    # NLP Models
    TEXT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CONTENT_CLASSIFIER: str = "facebook/bart-large-mnli"
    LANGUAGE_DETECTION: str = "papluca/xlm-roberta-base-language-detection"
    SENTIMENT_ANALYSIS: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    TEXT_SIMILARITY_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    # Multimodal Models
    MULTIMODAL_EMBEDDING: str = "openai/clip-vit-large-patch14"
    CONTENT_UNDERSTANDING: str = "microsoft/DialoGPT-medium"
    CROSS_MODAL_SEARCH: str = "sentence-transformers/clip-ViT-B-32-multilingual-v1"
    
    # Recommendation Models
    CONTENT_RECOMMENDER: str = "microsoft/DialoGPT-medium"
    COLLABORATION_MATCHER: str = "sentence-transformers/all-MiniLM-L12-v2"
    TREND_PREDICTOR: str = "facebook/prophet"
    
    # Generation Models
    CONTENT_GENERATOR: str = "gpt-3.5-turbo"
    MUSIC_GENERATOR: str = "facebook/musicgen-small"
    IMAGE_GENERATOR: str = "runwayml/stable-diffusion-v1-5"
    TEXT_GENERATOR: str = "microsoft/DialoGPT-large"
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    
    class Config:
        env_prefix = "AI_MODEL_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("DEFAULT_DEVICE")
    def validate_device(cls, v):
        """Validate and auto-detect optimal device."""
        if v == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return v
    
    @validator("MODEL_CACHE_DIR")
    def create_cache_dir(cls, v):
        """Ensure model cache directory exists."""
        os.makedirs(v, exist_ok=True)
        return v
    
    def get_model_spec(self, model_name: str) -> Optional[ModelSpec]:
        """Get model specification by name."""
        model_specs = {
            # Audio Models
            "audio_fingerprint": ModelSpec(
                name="audio_fingerprint",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.AUDIO_ANALYSIS,
                model_path=self.AUDIO_FINGERPRINT_MODEL,
                max_sequence_length=16000,
                requires_gpu=False,
                memory_requirement_mb=512
            ),
            "music_genre_classifier": ModelSpec(
                name="music_genre_classifier",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.CLASSIFICATION,
                model_path=self.MUSIC_GENRE_CLASSIFIER,
                num_classes=10,
                requires_gpu=False,
                memory_requirement_mb=768
            ),
            
            # Vision Models
            "image_fingerprint": ModelSpec(
                name="image_fingerprint",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.COMPUTER_VISION,
                model_path=self.IMAGE_FINGERPRINT_MODEL,
                input_size=(224, 224, 3),
                requires_gpu=True,
                memory_requirement_mb=1024
            ),
            "video_frame_analyzer": ModelSpec(
                name="video_frame_analyzer",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.COMPUTER_VISION,
                model_path=self.VIDEO_FRAME_ANALYZER,
                input_size=(224, 224, 3),
                requires_gpu=True,
                memory_requirement_mb=1536
            ),
            
            # NLP Models
            "text_embedding": ModelSpec(
                name="text_embedding",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.NLP,
                model_path=self.TEXT_EMBEDDING_MODEL,
                max_sequence_length=512,
                requires_gpu=False,
                memory_requirement_mb=384
            ),
            "content_classifier": ModelSpec(
                name="content_classifier",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.CLASSIFICATION,
                model_path=self.CONTENT_CLASSIFIER,
                max_sequence_length=1024,
                requires_gpu=False,
                memory_requirement_mb=512
            ),
            
            # Multimodal Models
            "multimodal_embedding": ModelSpec(
                name="multimodal_embedding",
                provider=ModelProvider.HUGGINGFACE,
                model_type=ModelType.MULTIMODAL,
                model_path=self.MULTIMODAL_EMBEDDING,
                input_size=(224, 224, 3),
                max_sequence_length=77,
                requires_gpu=True,
                memory_requirement_mb=2048
            ),
            
            # Generation Models
            "content_generator": ModelSpec(
                name="content_generator",
                provider=ModelProvider.OPENAI,
                model_type=ModelType.GENERATION,
                model_path=self.CONTENT_GENERATOR,
                max_sequence_length=4096,
                api_key_required=True,
                requires_gpu=False,
                memory_requirement_mb=256
            ),
        }
        
        return model_specs.get(model_name)
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelSpec]:
        """Get all models of specific type."""
        all_models = []
        for model_name in [
            "audio_fingerprint", "music_genre_classifier", "image_fingerprint",
            "video_frame_analyzer", "text_embedding", "content_classifier",
            "multimodal_embedding", "content_generator"
        ]:
            spec = self.get_model_spec(model_name)
            if spec and spec.model_type == model_type:
                all_models.append(spec)
        return all_models
    
    def get_device_optimal_models(self, available_memory_gb: float = 4.0) -> List[str]:
        """Get models that can run on current device with available memory."""
        optimal_models = []
        available_memory_mb = available_memory_gb * 1024
        
        for model_name in [
            "audio_fingerprint", "music_genre_classifier", "image_fingerprint",
            "video_frame_analyzer", "text_embedding", "content_classifier",
            "multimodal_embedding", "content_generator"
        ]:
            spec = self.get_model_spec(model_name)
            if spec and spec.memory_requirement_mb <= available_memory_mb:
                # Check GPU requirement
                if spec.requires_gpu and self.DEFAULT_DEVICE == "cpu":
                    continue
                optimal_models.append(model_name)
        
        return optimal_models
    
    def get_model_config_dict(self) -> Dict[str, Any]:
        """Export complete model configuration as dictionary."""
        return {
            "registry": {
                "url": self.MODEL_REGISTRY_URL,
                "cache_dir": self.MODEL_CACHE_DIR,
                "auto_update": self.MODEL_AUTO_UPDATE,
                "fallback_enabled": self.MODEL_FALLBACK_ENABLED,
            },
            "hardware": {
                "default_device": self.DEFAULT_DEVICE,
                "cuda_devices": self.CUDA_VISIBLE_DEVICES,
                "model_parallel": self.MODEL_PARALLEL_ENABLED,
                "mixed_precision": self.MIXED_PRECISION_ENABLED,
            },
            "performance": {
                "max_batch_size": self.MAX_BATCH_SIZE,
                "warmup_enabled": self.MODEL_WARMUP_ENABLED,
                "caching_enabled": self.MODEL_CACHING_ENABLED,
                "optimization": self.INFERENCE_OPTIMIZATION,
            },
            "models": {
                "audio": {
                    "fingerprint": self.AUDIO_FINGERPRINT_MODEL,
                    "genre_classifier": self.MUSIC_GENRE_CLASSIFIER,
                    "similarity": self.AUDIO_SIMILARITY_MODEL,
                    "beat_tracker": self.BEAT_TRACKING_MODEL,
                },
                "vision": {
                    "fingerprint": self.IMAGE_FINGERPRINT_MODEL,
                    "frame_analyzer": self.VIDEO_FRAME_ANALYZER,
                    "object_detection": self.OBJECT_DETECTION_MODEL,
                    "similarity": self.IMAGE_SIMILARITY_MODEL,
                },
                "nlp": {
                    "embedding": self.TEXT_EMBEDDING_MODEL,
                    "classifier": self.CONTENT_CLASSIFIER,
                    "language_detection": self.LANGUAGE_DETECTION,
                    "sentiment": self.SENTIMENT_ANALYSIS,
                    "similarity": self.TEXT_SIMILARITY_MODEL,
                },
                "multimodal": {
                    "embedding": self.MULTIMODAL_EMBEDDING,
                    "understanding": self.CONTENT_UNDERSTANDING,
                    "cross_modal_search": self.CROSS_MODAL_SEARCH,
                },
                "recommendation": {
                    "content": self.CONTENT_RECOMMENDER,
                    "collaboration": self.COLLABORATION_MATCHER,
                    "trend_predictor": self.TREND_PREDICTOR,
                },
                "generation": {
                    "content": self.CONTENT_GENERATOR,
                    "music": self.MUSIC_GENERATOR,
                    "image": self.IMAGE_GENERATOR,
                    "text": self.TEXT_GENERATOR,
                }
            },
            "api_keys": {
                "openai": bool(self.OPENAI_API_KEY),
                "anthropic": bool(self.ANTHROPIC_API_KEY),
                "google": bool(self.GOOGLE_API_KEY),
                "huggingface": bool(self.HUGGINGFACE_API_TOKEN),
            }
        }


# Global model configuration instance
ai_model_config = AIModelConfig()
