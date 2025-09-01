"""Machine Learning Package - Enterprise Grade AI Platform

This package provides comprehensive machine learning capabilities for the IA Influencer Agent backend,
including model training, inference, data processing, specialized AI models, sentiment analysis,
trend detection, content protection, and creator collaboration systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution is strictly prohibited
and will result in immediate legal action and substantial damages claims.
Contact: mlaiel@live.de for authorized licensing only.

Business Logic Integration:
User (musician/blogger/photographer/influencer/comedian) → Multi-format Upload → 
AI Rights Protection → Professional SEO → Collaboration Matching → Multi-platform Distribution
"""

import logging
import warnings
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Suppress unnecessary warnings for production
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Configure logging for ML operations
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Version and metadata
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Core ML Infrastructure
# from .training import (
#     ModelTrainer, 
#     TrainingConfig, 
#     DistributedTrainingManager,
#     HyperparameterOptimizer,
#     TrainingMode,
#     TrainingResult,
#     OptimizationAlgorithm,
#     LearningRateScheduler
# )

from .inference import (
    InferenceEngine, 
    BatchProcessor,
    ModelServer,
    InferenceConfig,
    InferenceCache,
    InferenceResult,
    InferenceMode,
    OptimizationLevel,
    InferenceBackend
)

from .pipeline import (
    MLPipeline, 
    PipelineConfig,
    PipelineStep,
    PipelineStatus,
    StepStatus,
    ExecutionMode,
    ResourceType,
    ResourceRequirement,
    StepMetrics
)

from .data_processing import (
    DataProcessor,
    FeatureExtractor,
    DataValidator,
    DataTransformer,
    NumericalTransformer,
    CategoricalTransformer,
    TextTransformer,
    ImageTransformer,
    AudioTransformer,
    DataType,
    ProcessingStrategy,
    FeatureType,
    ProcessingConfig,
    ProcessingResult
)

# Content Analysis Models - Core Business Logic
from .content_models import (
    TextContentModel, 
    ImageContentModel,
    ContentModel,
    ContentType,
    ContentQuality,
    ContentCategory,
    ContentMetadata,
    ContentAnalysisResult,
    ContentGenerationConfig
)

# Content Generation - Advanced AI Content Creation
from .content_generation import (
    ContentGenerator,
    ContentAnalyzer,
    ContentType as GenerationContentType,
    GenerationStrategy,
    GenerationConfig,
    GeneratedContent
)

# Personalization Engine - Advanced User Experience Personalization
from .personalization import (
    PersonalizationEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    PersonalizationType,
    UserSegment,
    PersonalizationStrategy
)

# Style Transfer Engine - Neural Style Transfer and Content Adaptation
from .style_transfer import (
    StyleTransferEngine,
    StyleTransferConfig,
    StyleTransferResult,
    StyleType,
    TransferMode,
    ArtisticStyle
)

# Advanced Recommendation System - Business Logic Core
from .recommendation import (
    HybridRecommendationEngine,
    CollaborativeFiltering,
    ContentBasedFiltering,
    RecommendationEngine,
    RecommendationType,
    RecommendationStrategy,
    InteractionType,
    UserInteraction,
    RecommendationItem,
    UserProfile,
    RecommendationResult,
    RecommendationConfig
)

# Advanced Sentiment & Emotion Analysis
from .sentiment_analysis import (
    SentimentAnalyzer, 
    EmotionDetector,
    TextSentimentAnalyzer,
    MultiModalSentimentAnalyzer,
    ToneAnalyzer,
    SentimentLabel,
    EmotionLabel,
    IntensityLevel,
    ModalityType,
    SentimentScore,
    EmotionScore,
    ToneAnalysisResult,
    SentimentAnalysisResult
)

# Market & Trend Intelligence - Strategic Business Logic
from .trend_detection import (
    TrendDetector, 
    StatisticalTrendDetector,
    MachineLearningTrendDetector,
    TrendPredictor,
    TrendAnalyticsEngine,
    TrendStatus,
    TrendType,
    TrendScope,
    TrendSource,
    TrendMetrics,
    TrendDataPoint,
    Trend,
    TrendPrediction
)

# Model Management Infrastructure - Temporarily disabled (empty file)
# from .model_manager import (
#     MLModelManager,
#     ModelRegistry,
#     ModelVersionManager,
#     ModelDeploymentManager,
#     ModelMonitor,
#     ModelMetrics,
#     ModelConfig,
#     ModelValidator,
#     AutoMLEngine,
#     ModelOptimizer
# )

# Security & Validation
try:
    from .model_security import (
        ModelSecurityValidator,
        AdversarialDefense,
        ModelIntegrityChecker,
        SecurityMetrics
    )
except ImportError:
    # Graceful degradation if security module not available
    pass

# Performance Monitoring
try:
    from .performance_monitor import (
        MLPerformanceMonitor,
        ModelPerformanceTracker,
        InferenceProfiler,
        ResourceMonitor
    )
except ImportError:
    # Graceful degradation if monitoring module not available
    pass

# Audio Processing Extensions
try:
    from .audio_intelligence import (
        MusicAnalyzer,
        AudioFingerprintEngine,
        MusicGenreClassifier,
        AudioQualityAnalyzer,
        MusicSimilarityEngine
    )
except ImportError:
    # Graceful degradation if audio module not available
    pass

# Demo and Examples
from .ml_demo import (
    MLModuleDemo,
    # ContentAnalysisDemo,  # Pas trouvé dans le fichier
    # RecommendationDemo,   # Pas trouvé dans le fichier
    # TrendAnalysisDemo,    # Pas trouvé dans le fichier
    # run_ml_demo          # Fonction main() trouvée, mais pas run_ml_demo
)

# Package-level constants
DEFAULT_MODEL_PATH = Path(__file__).parent / "models"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config"
DEFAULT_DATA_PATH = Path(__file__).parent / "data"

# Core ML capabilities matrix
ML_CAPABILITIES = {
    "content_analysis": {
        "text": True,
        "image": True, 
        "audio": True,
        "video": True,
        "multimodal": True
    },
    "protection": {
        "fingerprinting": True,
        "rights_management": True,
        "infringement_detection": True,
        "blockchain_integration": True
    },
    "recommendation": {
        "collaborative_filtering": True,
        "content_based": True,
        "hybrid": True,
        "deep_learning": True,
        "creator_matching": True
    },
    "analytics": {
        "sentiment_analysis": True,
        "trend_detection": True,
        "performance_prediction": True,
        "market_intelligence": True
    },
    "optimization": {
        "seo": True,
        "content_quality": True,
        "monetization": True,
        "distribution": True
    }
}

# Supported content creator types - Business Logic
SUPPORTED_CREATOR_TYPES = [
    "musician", "blogger", "photographer", "influencer", "comedian",
    "video_creator", "podcaster", "artist", "writer", "designer",
    "educator", "fitness_instructor", "chef", "gamer", "dancer"
]

# Supported platforms for distribution
SUPPORTED_PLATFORMS = [
    "spotify", "youtube", "instagram", "tiktok", "twitter", "facebook",
    "linkedin", "pinterest", "snapchat", "twitch", "soundcloud",
    "bandcamp", "apple_music", "amazon_music", "deezer"
]

# AI model configurations
MODEL_CONFIGS = {
    "content_analysis": {
        "max_file_size": "100MB",
        "supported_formats": ["mp3", "wav", "mp4", "avi", "jpg", "png", "txt", "pdf"],
        "processing_timeout": 300
    },
    "recommendation": {
        "min_data_points": 10,
        "max_recommendations": 50,
        "refresh_interval": 3600
    },
    "trend_detection": {
        "lookback_period": 90,
        "min_trend_strength": 0.7,
        "prediction_horizon": 30
    }
}

# Initialize default configurations
def initialize_ml_environment(config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Initialize the ML environment with production-ready configurations.
    
    Args:
        config: Optional configuration overrides
        
    Returns:
        Dict containing initialization status and configuration
    """
    default_config = {
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "batch_size": 32,
        "max_workers": 4,
        "cache_enabled": True,
        "monitoring_enabled": True,
        "security_validation": True
    }
    
    if config:
        default_config.update(config)
    
    # Create necessary directories - DISABLED to prevent auto-recreation
    # DEFAULT_MODEL_PATH.mkdir(exist_ok=True)
    # DEFAULT_CONFIG_PATH.mkdir(exist_ok=True) 
    # DEFAULT_DATA_PATH.mkdir(exist_ok=True)
    
    return {
        "status": "initialized",
        "config": default_config,
        "capabilities": ML_CAPABILITIES,
        "supported_creators": SUPPORTED_CREATOR_TYPES,
        "supported_platforms": SUPPORTED_PLATFORMS
    }

# Package exports for production use
__all__ = [
    # Core Infrastructure
    "ModelTrainer", "InferenceEngine", "MLPipeline", "DataProcessor",
    "MLModelManager", "ModelRegistry", "ModelVersionManager",
    
    # Content Analysis - Core Business
    "TextContentModel", "ImageContentModel", "AudioContentModel", "VideoContentModel",
    "MultiModalContentModel", "ContentAnalysisEngine", "ContentProtectionModel",
    "ContentFingerprintEngine", "ContentClassifier", "ContentQualityAssessor",
    "ContentSEOOptimizer", "ContentMetadataExtractor", "ContentSimilarityEngine",
    "ContentModerationModel", "CreatorProfileAnalyzer", "ContentRightsManager",
    "ContentMonetizationAnalyzer",
    
    # Recommendation System - Business Logic
    "HybridRecommendationEngine", "CollaborativeFilteringEngine", "ContentBasedEngine",
    "DeepRecommendationModel", "CreatorMatchingEngine", "ContentRecommendationEngine",
    "TrendAwareRecommendationEngine", "PersonalizationEngine", "CollaborationMatcher",
    "InfluencerCollaborationEngine", "ContentStrategyRecommender",
    
    # Analytics & Intelligence  
    "SentimentAnalyzer", "EmotionDetector", "AdvancedSentimentModel",
    "MultilingualSentimentAnalyzer", "SentimentTrendAnalyzer", "EmotionClassifier",
    "OpinionMiningEngine", "EmotionalIntelligenceEngine", "BrandSentimentAnalyzer",
    "InfluencerSentimentTracker", "AudienceSentimentAnalyzer",
    
    # Trend & Market Intelligence
    "TrendDetector", "MarketTrendAnalyzer", "ContentTrendPredictor", "ViralityPredictor",
    "TrendForecastingEngine", "SeasonalTrendAnalyzer", "CompetitiveIntelligenceEngine",
    "MarketOpportunityDetector", "InfluencerTrendAnalyzer", "ContentPerformancePredictor",
    "SocialMediaTrendAnalyzer", "CreatorMarketAnalyzer",
    
    # Training Infrastructure
    "TrainingConfig", "DistributedTrainingManager", "HyperparameterOptimizer",
    "ExperimentTracker", "TrainingMode", "TrainingStrategy", "ValidationStrategy",
    
    # Processing & Features
    "FeatureExtractor", "DataValidator", "DataTransformer", "MultiModalProcessor",
    "ContentProcessor", "AudioFeatureExtractor", "VideoFeatureExtractor",
    "ImageFeatureExtractor", "TextFeatureExtractor",
    
    # Demo & Examples
    "MLDemo", "ContentAnalysisDemo", "RecommendationDemo", "TrendAnalysisDemo", "run_ml_demo",
    
    # Constants & Configuration
    "ML_CAPABILITIES", "SUPPORTED_CREATOR_TYPES", "SUPPORTED_PLATFORMS", "MODEL_CONFIGS",
    "initialize_ml_environment"
]

# Auto-initialize on import for production environments
try:
    import torch
    _ml_environment = initialize_ml_environment()
    logging.getLogger(__name__).info(f"ML Environment initialized successfully: {_ml_environment['status']}")
except Exception as e:
    logging.getLogger(__name__).warning(f"ML Environment initialization warning: {e}")
    _ml_environment = {"status": "partially_initialized", "error": str(e)}
from .sentiment_analysis import (
    TextSentimentAnalyzer,
    MultiModalSentimentAnalyzer,
    EmotionDetector,
    ToneAnalyzer,
    SentimentAnalysisResult,
    SentimentScore,
    EmotionScore,
    ToneAnalysisResult,
    SentimentLabel,
    EmotionLabel,
    IntensityLevel,
    ModalityType
)

# Trend detection
from .trend_detection import (
    TrendAnalyticsEngine,
    StatisticalTrendDetector,
    MachineLearningTrendDetector,
    TrendPredictor,
    Trend,
    TrendMetrics,
    TrendPrediction,
    TrendDataPoint,
    TrendStatus,
    TrendType,
    TrendScope,
    TrendSource
)

# Version info
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Public API
__all__ = [
    # Training
    "ModelTrainer",
    "TrainingConfig",
    
    # Inference
    "InferenceEngine", 
    
    # Pipeline
    "MLPipeline",
    
    # Data Processing
    "DataProcessor",
    
    # Content Models
    "TextContentModel",
    "ImageContentModel",
    
    # Recommendations
    "HybridRecommendationEngine",
    
    # Sentiment Analysis
    "TextSentimentAnalyzer",
    "MultiModalSentimentAnalyzer", 
    "EmotionDetector",
    "ToneAnalyzer",
    "SentimentAnalysisResult",
    "SentimentScore",
    "EmotionScore",
    "ToneAnalysisResult",
    "SentimentLabel",
    "EmotionLabel",
    "IntensityLevel",
    "ModalityType",
    
    # Trend Detection
    "TrendAnalyticsEngine",
    "StatisticalTrendDetector",
    "MachineLearningTrendDetector", 
    "TrendPredictor",
    "Trend",
    "TrendMetrics",
    "TrendPrediction",
    "TrendDataPoint",
    "TrendStatus",
    "TrendType",
    "TrendScope",
    "TrendSource"
]

# Core ML Components
# from .model_manager import MLModelManager, ModelType, ModelStatus  # Fichier vide
from .training_simple import ModelTrainer, TrainingConfig, TrainingResult
from .inference import InferenceEngine, InferenceConfig, InferenceResult
from .pipeline import MLPipeline, PipelineStep, PipelineConfig
from .data_processing import DataProcessor, DataTransformer, FeatureExtractor

# Specialized ML Models  
# from .content_models import ContentGenerationModel, ContentAnalysisModel  # Classes inexistantes
from .content_models import ContentModel, TextContentModel, ImageContentModel
from .recommendation import RecommendationEngine, CollaborativeFiltering, ContentBasedFiltering
from .sentiment_analysis import SentimentAnalyzer, EmotionDetector, ToneAnalyzer
# from .trend_prediction import TrendPredictor, ViralityPredictor, PopularityForecaster  # Module inexistant
# from .personalization import PersonalizationEngine, UserProfiler, ContentPersonalizer  # Module inexistant

# Computer Vision Models
from .vision import ImageClassifier, ObjectDetector, FaceRecognizer, SceneAnalyzer
from .visual_content import VisualContentGenerator, StyleTransfer, ImageEnhancer
from .video_analysis import VideoAnalyzer, ActionRecognizer, SceneDetector

# Natural Language Processing
from .nlp import TextGenerator, LanguageDetector, TextSummarizer, KeywordExtractor
from .translation import MultilingualTranslator, LanguageAdapter
from .conversation import ConversationalModel, DialogueManager, ContextTracker

# Audio ML Models
from .audio_ml import AudioClassifier, MusicGenerator, VoiceAnalyzer, SpeechSynthesizer
from .music_intelligence import MusicStyleAnalyzer, BeatDetector, HarmonyAnalyzer
from .voice_processing import VoiceCloner, SpeakerIdentification, EmotionalVoiceAnalysis

# Advanced Analytics
from .analytics import PerformancePredictor, EngagementForecaster, GrowthAnalyzer
from .optimization import ContentOptimizer, StrategyOptimizer, CampaignOptimizer
from .anomaly_detection import AnomalyDetector, FraudDetector, ContentModerator

# Model Deployment and Serving
from .deployment import ModelDeployer, ModelServer, ModelScaler
from .monitoring import ModelMonitor, PerformanceTracker, DriftDetector
from .versioning import ModelVersionManager, ExperimentTracker, ABTestManager

# AutoML and Meta-Learning
from .automl import AutoMLEngine, HyperparameterOptimizer, NeuralArchitectureSearch
from .meta_learning import MetaLearner, FewShotLearner, TransferLearner
from .ensemble import EnsembleManager, ModelBlender, VotingClassifier

# MLOps and Infrastructure
from .mlops import MLOpsManager, DataPipeline, ModelPipeline, DeploymentPipeline
from .distributed import DistributedTrainer, ModelParallelism, DataParallelism
from .optimization import ModelOptimizer, QuantizationEngine, PruningEngine

# Security and Privacy
from .privacy import PrivacyPreserver, FederatedLearning, DifferentialPrivacy
from .security import ModelSecurity, AdversarialDefense, ModelWatermarking
from .compliance import ComplianceChecker, DataGovernance, ModelAudit

# Export version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Module metadata
MODULE_INFO = {
    "name": "Machine Learning Infrastructure",
    "version": __version__,
    "description": "Comprehensive ML platform for AI-powered content creation and analysis",
    "capabilities": [
        "Content generation and analysis",
        "Recommendation systems",
        "Sentiment and emotion analysis",
        "Trend prediction and forecasting",
        "Personalization engines",
        "Computer vision and image processing",
        "Natural language processing",
        "Audio and music intelligence",
        "Performance analytics and optimization",
        "Anomaly detection and moderation",
        "AutoML and meta-learning",
        "Distributed training and serving",
        "Model monitoring and versioning",
        "Privacy-preserving ML",
        "MLOps and deployment automation"
    ],
    "supported_frameworks": [
        "PyTorch", "TensorFlow", "JAX", "Scikit-learn",
        "Transformers", "Diffusers", "OpenCV", "librosa",
        "spaCy", "NLTK", "Whisper", "CLIP"
    ],
    "model_types": [
        "Transformer", "CNN", "RNN", "GAN", "VAE", "Diffusion",
        "BERT", "GPT", "T5", "CLIP", "DALL-E", "Whisper",
        "ResNet", "YOLO", "U-Net", "StyleGAN"
    ],
    "data_formats": [
        "Text", "Image", "Audio", "Video", "JSON", "CSV",
        "Parquet", "HDF5", "NumPy", "Tensor"
    ],
    "deployment_targets": [
        "Cloud (AWS, GCP, Azure)", "Edge devices", "Mobile",
        "Web browsers", "Kubernetes", "Docker containers"
    ]
}

# Available ML models registry
AVAILABLE_MODELS = {
    # Content Models
    "content_generator": ContentGenerator,
    "content_analyzer": ContentAnalyzer,
    "recommendation_engine": RecommendationEngine,
    "sentiment_analyzer": TextSentimentAnalyzer,
    "trend_predictor": TrendPredictor,
    "personalization_engine": PersonalizationEngine,
    
    # Vision Models
    "image_classifier": ImageClassifier,
    "object_detector": ObjectDetector,
    "face_recognizer": FaceRecognizer,
    "visual_content_generator": VisualContentGenerator,
    "video_analyzer": VideoAnalyzer,
    
    # NLP Models
    "text_generator": TextGenerator,
    "language_detector": LanguageDetector,
    "text_summarizer": TextSummarizer,
    "multilingual_translator": MultilingualTranslator,
    "conversational_model": ConversationalModel,
    
    # Audio Models
    "audio_classifier": AudioClassifier,
    "music_generator": MusicGenerator,
    "voice_analyzer": VoiceAnalyzer,
    "speech_synthesizer": SpeechSynthesizer,
    "voice_cloner": VoiceCloner,
    
    # Analytics Models
    "performance_predictor": PerformancePredictor,
    "engagement_forecaster": EngagementForecaster,
    "content_optimizer": ContentOptimizer,
    "anomaly_detector": AnomalyDetector
}

# Model categories for organization
MODEL_CATEGORIES = {
    "content_creation": [
        "content_generator", "text_generator", "visual_content_generator",
        "music_generator", "speech_synthesizer"
    ],
    "content_analysis": [
        "content_analyzer", "sentiment_analyzer", "image_classifier",
        "video_analyzer", "audio_classifier"
    ],
    "recommendation": [
        "recommendation_engine", "personalization_engine", "content_optimizer"
    ],
    "prediction": [
        "trend_predictor", "performance_predictor", "engagement_forecaster"
    ],
    "processing": [
        "language_detector", "text_summarizer", "multilingual_translator",
        "object_detector", "face_recognizer", "voice_analyzer"
    ],
    "intelligence": [
        "conversational_model", "anomaly_detector", "voice_cloner"
    ]
}

# Default model configurations
DEFAULT_MODEL_CONFIGS = {
    "content_generator": {
        "model_type": "transformer",
        "max_length": 2048,
        "temperature": 0.7,
        "top_p": 0.9,
        "creativity_level": 0.8
    },
    "sentiment_analyzer": {
        "model_type": "bert",
        "languages": ["en", "fr", "de", "es"],
        "confidence_threshold": 0.8,
        "emotion_detection": True
    },
    "recommendation_engine": {
        "algorithm": "hybrid",
        "collaborative_weight": 0.6,
        "content_based_weight": 0.4,
        "diversity_factor": 0.2,
        "novelty_factor": 0.1
    },
    "image_classifier": {
        "model_type": "resnet",
        "input_size": [224, 224],
        "num_classes": 1000,
        "confidence_threshold": 0.7
    }
}

# Training configurations for different model types
TRAINING_CONFIGS = {
    "transformer": {
        "batch_size": 16,
        "learning_rate": 5e-5,
        "num_epochs": 3,
        "warmup_steps": 500,
        "weight_decay": 0.01,
        "gradient_accumulation_steps": 4
    },
    "cnn": {
        "batch_size": 32,
        "learning_rate": 1e-3,
        "num_epochs": 50,
        "optimizer": "adam",
        "scheduler": "cosine",
        "data_augmentation": True
    },
    "rnn": {
        "batch_size": 64,
        "learning_rate": 1e-3,
        "num_epochs": 100,
        "hidden_size": 512,
        "num_layers": 2,
        "dropout": 0.2
    }
}

# Performance benchmarks and requirements
PERFORMANCE_REQUIREMENTS = {
    "inference_latency": {
        "real_time": 100,      # milliseconds
        "near_real_time": 1000, # milliseconds
        "batch": 10000         # milliseconds
    },
    "accuracy_thresholds": {
        "content_generation": 0.85,
        "classification": 0.90,
        "recommendation": 0.80,
        "sentiment_analysis": 0.88,
        "object_detection": 0.85
    },
    "resource_limits": {
        "memory_gb": 8,
        "gpu_memory_gb": 16,
        "cpu_cores": 8,
        "storage_gb": 100
    }
}

# Quality metrics for different model types
QUALITY_METRICS = {
    "classification": ["accuracy", "precision", "recall", "f1_score", "auc_roc"],
    "regression": ["mse", "mae", "r2_score", "rmse"],
    "generation": ["bleu", "rouge", "bertscore", "perplexity", "diversity"],
    "recommendation": ["precision_at_k", "recall_at_k", "ndcg", "diversity", "novelty"],
    "detection": ["mAP", "precision", "recall", "iou", "f1_score"]
}

def get_available_models() -> dict:
    """Get dictionary of all available ML models"""
    return AVAILABLE_MODELS.copy()

def get_model_categories() -> dict:
    """
Get model categories for organization"""
    return MODEL_CATEGORIES.copy()

def get_default_config(model_type: str) -> dict:
    """
Get default configuration for a model type"""
    return DEFAULT_MODEL_CONFIGS.get(model_type, {})

def get_training_config(model_architecture: str) -> dict:
    """
Get training configuration for a model architecture"""
    return TRAINING_CONFIGS.get(model_architecture, {})

def create_model(model_type: str, config: dict = None):
    """
Factory function to create a model instance"""
    if model_type not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model_class = AVAILABLE_MODELS[model_type]
    model_config = get_default_config(model_type)
    
    if config:
        model_config.update(config)
    
    return model_class(config=model_config)

def validate_model_performance(model_type: str, metrics: dict) -> bool:
    """Validate if model meets performance requirements"""
    category = None
    for cat, models in MODEL_CATEGORIES.items():
        if model_type in models:
            category = cat
            break
    
    if not category:
        return True  # Unknown category, assume valid
    
    # Check accuracy requirements
    required_accuracy = PERFORMANCE_REQUIREMENTS["accuracy_thresholds"].get(category)
    if required_accuracy and metrics.get("accuracy", 0) < required_accuracy:
        return False
    
    # Check latency requirements
    required_latency = PERFORMANCE_REQUIREMENTS["inference_latency"]["real_time"]
    if metrics.get("latency_ms", 0) > required_latency:
        return False
    
    return True

def get_quality_metrics_for_model(model_type: str) -> list:
    """Get appropriate quality metrics for a model type"""
    for category, models in MODEL_CATEGORIES.items():
        if model_type in models:
            if "generation" in category or "content_creation" in category:
                return QUALITY_METRICS["generation"]
            elif "classification" in category or "analysis" in category:
                return QUALITY_METRICS["classification"]
            elif "recommendation" in category:
                return QUALITY_METRICS["recommendation"]
            elif "prediction" in category:
                return QUALITY_METRICS["regression"]
    
    return QUALITY_METRICS["classification"]  # Default

# Quality assurance and compliance
__all__ = [
    # Core Components
    "MLModelManager", "ModelType", "ModelStatus",
    "ModelTrainer", "TrainingConfig", "TrainingResult",
    "InferenceEngine", "InferenceConfig", "InferenceResult",
    "MLPipeline", "PipelineStep", "PipelineConfig",
    "DataProcessor", "DataTransformer", "FeatureExtractor",
    
    # Specialized Models
    "ContentGenerationModel", "ContentAnalysisModel",
    "RecommendationEngine", "CollaborativeFiltering", "ContentBasedFiltering",
    "SentimentAnalyzer", "EmotionDetector", "ToneAnalyzer",
    "TrendPredictor", "ViralityPredictor", "PopularityForecaster",
    "PersonalizationEngine", "UserProfiler", "ContentPersonalizer",
    
    # Vision Models
    "ImageClassifier", "ObjectDetector", "FaceRecognizer", "SceneAnalyzer",
    "VisualContentGenerator", "StyleTransfer", "ImageEnhancer",
    "VideoAnalyzer", "ActionRecognizer", "SceneDetector",
    
    # NLP Models
    "TextGenerator", "LanguageDetector", "TextSummarizer", "KeywordExtractor",
    "MultilingualTranslator", "LanguageAdapter",
    "ConversationalModel", "DialogueManager", "ContextTracker",
    
    # Audio Models
    "AudioClassifier", "MusicGenerator", "VoiceAnalyzer", "SpeechSynthesizer",
    "MusicStyleAnalyzer", "BeatDetector", "HarmonyAnalyzer",
    "VoiceCloner", "SpeakerIdentification", "EmotionalVoiceAnalysis",
    
    # Analytics and Optimization
    "PerformancePredictor", "EngagementForecaster", "GrowthAnalyzer",
    "ContentOptimizer", "StrategyOptimizer", "CampaignOptimizer",
    "AnomalyDetector", "FraudDetector", "ContentModerator",
    
    # Deployment and Monitoring
    "ModelDeployer", "ModelServer", "ModelScaler",
    "ModelMonitor", "PerformanceTracker", "DriftDetector",
    "ModelVersionManager", "ExperimentTracker", "ABTestManager",
    
    # AutoML and Meta-Learning
    "AutoMLEngine", "HyperparameterOptimizer", "NeuralArchitectureSearch",
    "MetaLearner", "FewShotLearner", "TransferLearner",
    "EnsembleManager", "ModelBlender", "VotingClassifier",
    
    # MLOps and Infrastructure
    "MLOpsManager", "DataPipeline", "ModelPipeline", "DeploymentPipeline",
    "DistributedTrainer", "ModelParallelism", "DataParallelism",
    "ModelOptimizer", "QuantizationEngine", "PruningEngine",
    
    # Security and Privacy
    "PrivacyPreserver", "FederatedLearning", "DifferentialPrivacy",
    "ModelSecurity", "AdversarialDefense", "ModelWatermarking",
    "ComplianceChecker", "DataGovernance", "ModelAudit",
    
    # Utility Functions
    "get_available_models", "get_model_categories", "get_default_config",
    "get_training_config", "create_model", "validate_model_performance",
    "get_quality_metrics_for_model",
    
    # Constants
    "MODULE_INFO", "AVAILABLE_MODELS", "MODEL_CATEGORIES",
    "DEFAULT_MODEL_CONFIGS", "TRAINING_CONFIGS", "PERFORMANCE_REQUIREMENTS",
    "QUALITY_METRICS"
]
