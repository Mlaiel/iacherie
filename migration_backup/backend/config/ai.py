"""AI Configuration Module - Consolidated AI Configs
==================================================

Consolidates all AI-related configurations from:
- config/ai/ (21 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os

# ===== AI MODEL CONFIGURATION =====

class ModelType(str, Enum):
    """AI model types"""
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    LSTM = "lstm"
    GAN = "gan"
    AUTOENCODER = "autoencoder"
    RESNET = "resnet"
    BERT = "bert"
    GPT = "gpt"
    DIFFUSION = "diffusion"

class ModelFormat(str, Enum):
    """Model file formats"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    HUGGINGFACE = "huggingface"
    PICKLE = "pickle"

class InferenceBackend(str, Enum):
    """Inference backends"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX_RUNTIME = "onnx_runtime"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    TRITON = "triton"

@dataclass
class AIModelConfig:
    """Core AI model configuration"""
    model_name: str
    model_type: ModelType
    model_format: ModelFormat
    model_path: str
    version: str = "1.0.0"
    inference_backend: InferenceBackend = InferenceBackend.PYTORCH
    batch_size: int = 32
    max_sequence_length: int = 512
    device: str = "cuda"  # cuda, cpu, mps
    precision: str = "float32"  # float16, float32, bfloat16
    cache_model: bool = True
    warm_up_iterations: int = 3

# ===== FINGERPRINT AI CONFIGURATION =====

class FingerprintAlgorithm(str, Enum):
    """Fingerprint algorithms"""
    PERCEPTUAL_HASH = "perceptual_hash"
    WAVELET_HASH = "wavelet_hash"
    DCT_HASH = "dct_hash"
    SIFT = "sift"
    ORB = "orb"
    SURF = "surf"
    CHROMAPRINT = "chromaprint"
    AUDIO_FINGERPRINT = "audio_fingerprint"

@dataclass
class FingerprintAIConfig:
    """AI-powered fingerprinting configuration"""
    enabled: bool = True
    algorithms: List[FingerprintAlgorithm] = field(default_factory=lambda: [
        FingerprintAlgorithm.PERCEPTUAL_HASH,
        FingerprintAlgorithm.DCT_HASH
    ])
    similarity_threshold: float = 0.85
    max_fingerprints_per_content: int = 5
    cache_fingerprints: bool = True
    background_processing: bool = True
    batch_processing_size: int = 100

# ===== NLP CONFIGURATION =====

@dataclass
class NLPConfig:
    """Natural Language Processing configuration"""
    model_name: str = "bert-base-uncased"
    tokenizer_name: str = "bert-base-uncased"
    max_sequence_length: int = 512
    batch_size: int = 16
    languages: List[str] = field(default_factory=lambda: ["en", "es", "fr", "de"])
    tasks: List[str] = field(default_factory=lambda: [
        "sentiment_analysis",
        "content_classification", 
        "toxicity_detection",
        "language_detection"
    ])
    cache_predictions: bool = True
    model_cache_size: int = 3  # Number of models to keep in memory

# ===== COMPUTER VISION CONFIGURATION =====

@dataclass
class ComputerVisionConfig:
    """Computer vision configuration"""
    model_name: str = "resnet50"
    input_size: tuple = (224, 224)
    batch_size: int = 32
    channels: int = 3
    normalization_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalization_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    tasks: List[str] = field(default_factory=lambda: [
        "image_classification",
        "object_detection",
        "face_recognition",
        "content_similarity"
    ])
    detection_threshold: float = 0.5
    nms_threshold: float = 0.4

# ===== AUDIO ANALYSIS CONFIGURATION =====

@dataclass
class AudioAnalysisConfig:
    """Audio analysis configuration"""
    sample_rate: int = 44100
    n_fft: int = 2048
    hop_length: int = 512
    n_mels: int = 128
    n_mfcc: int = 13
    models: Dict[str, str] = field(default_factory=lambda: {
        "genre_classifier": "audio_genre_cnn",
        "music_classifier": "music_speech_classifier",
        "fingerprinting": "audio_fingerprint_model"
    })
    batch_size: int = 16
    segment_duration: float = 30.0  # seconds
    overlap_ratio: float = 0.5

# ===== TRAINING CONFIGURATION =====

@dataclass
class ModelTrainingConfig:
    """Model training configuration"""
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    optimizer: str = "adam"
    loss_function: str = "cross_entropy"
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    checkpoint_frequency: int = 5
    mixed_precision: bool = True
    gradient_clipping: float = 1.0
    weight_decay: float = 0.01
    warmup_steps: int = 1000

# ===== INFERENCE CONFIGURATION =====

@dataclass
class InferenceConfig:
    """Model inference configuration"""
    max_batch_size: int = 64
    max_sequence_length: int = 512
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_predictions: bool = True
    prediction_cache_ttl: int = 3600  # 1 hour
    enable_batching: bool = True
    batching_timeout_ms: int = 10
    model_parallel: bool = False
    tensor_parallel_size: int = 1

# ===== VECTOR STORE CONFIGURATION =====

class VectorStoreType(str, Enum):
    """Vector store types"""
    FAISS = "faiss"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    CHROMA = "chroma"
    MILVUS = "milvus"

@dataclass
class VectorStoreConfig:
    """Vector store configuration"""
    store_type: VectorStoreType = VectorStoreType.FAISS
    dimension: int = 768
    index_type: str = "IVF"
    metric: str = "cosine"  # cosine, euclidean, dot_product
    nlist: int = 1024
    nprobe: int = 10
    max_vectors: int = 1000000
    batch_size: int = 1000
    persistent: bool = True
    index_path: str = "data/vector_index"

# ===== CONTENT ANALYSIS CONFIGURATION =====

@dataclass
class ContentAnalysisConfig:
    """Content analysis AI configuration"""
    enabled: bool = True
    supported_formats: List[str] = field(default_factory=lambda: [
        "image", "video", "audio", "text", "document"
    ])
    analysis_depth: str = "comprehensive"  # basic, standard, comprehensive
    parallel_processing: bool = True
    max_concurrent_analyses: int = 10
    cache_analysis_results: bool = True
    result_cache_ttl: int = 3600  # 1 hour

# ===== CONTENT PROTECTION CONFIGURATION =====

@dataclass
class ContentProtectionConfig:
    """Content protection AI configuration"""
    enabled: bool = True
    protection_algorithms: List[str] = field(default_factory=lambda: [
        "watermarking", "fingerprinting", "hash_matching", "similarity_detection"
    ])
    detection_sensitivity: float = 0.8
    false_positive_threshold: float = 0.1
    batch_processing: bool = True
    real_time_monitoring: bool = True
    alert_on_infringement: bool = True

# ===== MONETIZATION AI CONFIGURATION =====

@dataclass
class MonetizationAIConfig:
    """AI-powered monetization configuration"""
    enabled: bool = True
    revenue_prediction_model: str = "revenue_predictor_v2"
    pricing_optimization_model: str = "pricing_optimizer_v1"
    market_analysis_model: str = "market_analyzer_v1"
    prediction_horizon_days: int = 30
    retraining_frequency_days: int = 7
    confidence_threshold: float = 0.7

# ===== COLLABORATION AI CONFIGURATION =====

@dataclass
class CollaborationAIConfig:
    """AI-powered collaboration configuration"""
    enabled: bool = True
    matching_algorithm: str = "deep_content_similarity"
    creator_compatibility_model: str = "creator_compatibility_v2"
    content_synergy_model: str = "content_synergy_v1"
    matching_threshold: float = 0.75
    max_suggestions_per_creator: int = 10
    update_frequency_hours: int = 24

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_ai_config() -> Dict[str, Any]:
    """Get development AI configuration"""
    return {
        "ai_model": AIModelConfig(
            model_name="distilbert-base-uncased",
            model_type=ModelType.TRANSFORMER,
            model_format=ModelFormat.HUGGINGFACE,
            model_path="models/dev/",
            batch_size=8,
            device="cpu"
        ),
        "fingerprint": FingerprintAIConfig(
            batch_processing_size=10,
            cache_fingerprints=False
        ),
        "nlp": NLPConfig(
            model_name="distilbert-base-uncased",
            batch_size=4,
            model_cache_size=1
        ),
        "computer_vision": ComputerVisionConfig(
            model_name="mobilenet_v2",
            batch_size=4
        ),
        "vector_store": VectorStoreConfig(
            store_type=VectorStoreType.FAISS,
            max_vectors=10000,
            persistent=False
        )
    }

def get_production_ai_config() -> Dict[str, Any]:
    """Get production AI configuration"""
    return {
        "ai_model": AIModelConfig(
            model_name="bert-large-uncased",
            model_type=ModelType.TRANSFORMER,
            model_format=ModelFormat.HUGGINGFACE,
            model_path="models/prod/",
            batch_size=32,
            device="cuda"
        ),
        "fingerprint": FingerprintAIConfig(
            batch_processing_size=1000,
            cache_fingerprints=True
        ),
        "nlp": NLPConfig(
            model_name="bert-large-uncased",
            batch_size=32,
            model_cache_size=5
        ),
        "computer_vision": ComputerVisionConfig(
            model_name="efficientnet-b7",
            batch_size=64
        ),
        "vector_store": VectorStoreConfig(
            store_type=VectorStoreType.PINECONE,
            max_vectors=10000000,
            persistent=True
        )
    }

def get_testing_ai_config() -> Dict[str, Any]:
    """Get testing AI configuration"""
    return {
        "ai_model": AIModelConfig(
            model_name="distilbert-base-uncased",
            model_type=ModelType.TRANSFORMER,
            model_format=ModelFormat.HUGGINGFACE,
            model_path="models/test/",
            batch_size=2,
            device="cpu"
        ),
        "fingerprint": FingerprintAIConfig(
            batch_processing_size=5,
            cache_fingerprints=False
        ),
        "nlp": NLPConfig(
            model_name="distilbert-base-uncased",
            batch_size=2,
            model_cache_size=1
        ),
        "computer_vision": ComputerVisionConfig(
            model_name="mobilenet_v2",
            batch_size=2
        ),
        "vector_store": VectorStoreConfig(
            store_type=VectorStoreType.FAISS,
            max_vectors=1000,
            persistent=False
        )
    }

# ===== AI CONFIGURATION FACTORY =====

class AIConfigurationFactory:
    """Factory for creating AI configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create AI configuration for environment"""
        if environment.lower() == "production":
            return get_production_ai_config()
        elif environment.lower() == "testing":
            return get_testing_ai_config()
        else:
            return get_development_ai_config()
    
    @staticmethod
    def create_model_config(model_type: str, environment: str = "development") -> AIModelConfig:
        """Create specific model configuration"""
        base_config = AIConfigurationFactory.create_config(environment)
        return base_config.get("ai_model", AIModelConfig(
            model_name=f"{model_type}_default",
            model_type=ModelType.TRANSFORMER,
            model_format=ModelFormat.HUGGINGFACE,
            model_path=f"models/{environment}/{model_type}/"
        ))

# Export all AI configurations
__all__ = [
    # Enums
    "ModelType",
    "ModelFormat", 
    "InferenceBackend",
    "FingerprintAlgorithm",
    "VectorStoreType",
    
    # Core Configuration Classes
    "AIModelConfig",
    "FingerprintAIConfig",
    "NLPConfig",
    "ComputerVisionConfig",
    "AudioAnalysisConfig",
    "ModelTrainingConfig",
    "InferenceConfig",
    "VectorStoreConfig",
    
    # Advanced Configuration Classes
    "ContentAnalysisConfig",
    "ContentProtectionConfig",
    "MonetizationAIConfig",
    "CollaborationAIConfig",
    
    # Factory and Functions
    "AIConfigurationFactory",
    "get_development_ai_config",
    "get_production_ai_config", 
    "get_testing_ai_config"
]