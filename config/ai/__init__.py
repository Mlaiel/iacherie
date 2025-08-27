"""
AI Configuration Module for IA-Influencer Agent Platform
========================================================

Professional AI/ML model configuration for content analysis and protection.

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

# Core AI Configuration Imports
from .model_config import AIModelConfig, ai_model_config
from .fingerprint_config import FingerprintAIConfig, fingerprint_ai_config
from .nlp_config import NLPConfig, nlp_config
from .computer_vision_config import ComputerVisionConfig, computer_vision_config
from .audio_analysis_config import AudioAnalysisConfig, audio_analysis_config
from .training_config import ModelTrainingConfig, model_training_config
from .inference_config import InferenceConfig, inference_config
from .vector_store_config import VectorStoreConfig, vector_store_config

# Advanced AI Configuration Imports
from .content_analysis_config import ContentAnalysisConfig, content_analysis_config
from .content_protection_config import ContentProtectionConfig, content_protection_config
from .monetization_config import MonetizationConfig, monetization_config
from .collaboration_config import CollaborationConfig, collaboration_config
from .seo_marketing_config import SEOMarketingConfig, seo_marketing_config
from .platform_integration_config import PlatformIntegrationConfig, platform_integration_config

# Export configuration classes and instances
__all__ = [
    # Core Configuration Classes
    'AIModelConfig',
    'FingerprintAIConfig',
    'NLPConfig',
    'ComputerVisionConfig', 
    'AudioAnalysisConfig',
    'ModelTrainingConfig',
    'InferenceConfig',
    'VectorStoreConfig',
    
    # Advanced Configuration Classes
    'ContentAnalysisConfig',
    'ContentProtectionConfig',
    'MonetizationConfig',
    'CollaborationConfig',
    'SEOMarketingConfig',
    'PlatformIntegrationConfig',
    
    # Core Configuration Instances (ready to use)
    'ai_model_config',
    'fingerprint_ai_config',
    'nlp_config',
    'computer_vision_config',
    'audio_analysis_config',
    'model_training_config',
    'inference_config',
    'vector_store_config',
    
    # Advanced Configuration Instances (ready to use)
    'content_analysis_config',
    'content_protection_config',
    'monetization_config',
    'collaboration_config',
    'seo_marketing_config',
    'platform_integration_config',
]

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

def get_ai_config_summary():
    """
    Get a summary of all AI configuration modules.
    
    Returns:
        Dict[str, Any]: Summary of all AI configurations
    """
    return {
        "version": __version__,
        "author": __author__,
        "modules": {
            "model_config": {
                "description": "Core AI/ML model configuration and management",
                "models_configured": len([
                    "audio_fingerprint", "music_genre_classifier", "image_fingerprint",
                    "video_frame_analyzer", "text_embedding", "content_classifier",
                    "multimodal_embedding", "content_generator"
                ]),
                "device": ai_model_config.DEFAULT_DEVICE,
                "cache_dir": ai_model_config.MODEL_CACHE_DIR,
            },
            "fingerprint_config": {
                "description": "AI fingerprinting for content protection",
                "fingerprint_types": 8,
                "storage_path": fingerprint_ai_config.FINGERPRINT_STORAGE_PATH,
                "similarity_threshold": fingerprint_ai_config.SIMILARITY_THRESHOLD_GLOBAL,
            },
            "nlp_config": {
                "description": "Natural Language Processing configuration",
                "supported_languages": len(nlp_config.SUPPORTED_LANGUAGES),
                "default_language": nlp_config.DEFAULT_LANGUAGE,
                "multilingual_support": nlp_config.MULTILINGUAL_SUPPORT,
            },
            "computer_vision_config": {
                "description": "Computer Vision and Image Processing",
                "supported_formats": len(computer_vision_config.SUPPORTED_IMAGE_FORMATS),
                "gpu_acceleration": computer_vision_config.GPU_ACCELERATION,
                "max_image_size_mb": computer_vision_config.MAX_IMAGE_SIZE_MB,
            },
            "audio_analysis_config": {
                "description": "Audio Processing and Music Intelligence",
                "supported_formats": len(audio_analysis_config.SUPPORTED_AUDIO_FORMATS),
                "sample_rate": audio_analysis_config.DEFAULT_SAMPLE_RATE,
                "max_duration": audio_analysis_config.MAX_AUDIO_DURATION,
            },
            "training_config": {
                "description": "AI/ML Model Training and Fine-tuning",
                "gpu_training": model_training_config.GPU_TRAINING_ENABLED,
                "mixed_precision": model_training_config.MIXED_PRECISION_ENABLED,
                "data_dir": model_training_config.TRAINING_DATA_DIR,
            },
            "inference_config": {
                "description": "AI Model Inference and Deployment",
                "backend": inference_config.INFERENCE_BACKEND,
                "max_concurrent": inference_config.MAX_CONCURRENT_REQUESTS,
                "caching_strategy": inference_config.CACHING_STRATEGY,
            },
            "vector_store_config": {
                "description": "Vector Database and Similarity Search",
                "database": vector_store_config.DEFAULT_VECTOR_DB,
                "vector_dimension": vector_store_config.VECTOR_DIMENSION,
                "collections_configured": 5,
            },
            "content_analysis_config": {
                "description": "Multi-format Content Analysis and Processing",
                "supported_audio_formats": len(content_analysis_config.SUPPORTED_AUDIO_FORMATS),
                "supported_video_formats": len(content_analysis_config.SUPPORTED_VIDEO_FORMATS),
                "supported_image_formats": len(content_analysis_config.SUPPORTED_IMAGE_FORMATS),
                "max_file_size_mb": content_analysis_config.MAX_FILE_SIZE_MB,
            },
            "content_protection_config": {
                "description": "AI-Powered Content Protection and Rights Management",
                "monitoring_platforms": 11,
                "auto_takedown_enabled": content_protection_config.AUTO_TAKEDOWN_ENABLED,
                "similarity_threshold": content_protection_config.SIMILARITY_THRESHOLD_GLOBAL,
                "revenue_claiming": content_protection_config.REVENUE_CLAIMING_ENABLED,
            },
            "monetization_config": {
                "description": "Revenue Optimization and Payment Processing",
                "revenue_models": 10,
                "default_currency": monetization_config.DEFAULT_CURRENCY,
                "commission_rate": monetization_config.DEFAULT_COMMISSION_RATE,
                "supported_payments": 8,
            },
            "collaboration_config": {
                "description": "AI-Powered Creator Collaboration Matching",
                "collaboration_types": 10,
                "min_match_score": collaboration_config.MIN_MATCH_SCORE,
                "max_suggestions": collaboration_config.MAX_COLLABORATION_SUGGESTIONS,
                "automated_matching": True,
            },
            "seo_marketing_config": {
                "description": "SEO Optimization and Marketing Automation",
                "platforms_supported": 10,
                "keyword_research_enabled": seo_marketing_config.KEYWORD_RESEARCH_ENABLED,
                "ab_testing_enabled": seo_marketing_config.AB_TESTING_ENABLED,
                "target_reach_increase": seo_marketing_config.TARGET_ORGANIC_REACH_INCREASE,
            },
            "platform_integration_config": {
                "description": "Cross-Platform API Integration and Management",
                "active_platforms": len(platform_integration_config.get_active_platforms()),
                "webhook_enabled": platform_integration_config.WEBHOOK_SIGNATURE_VERIFICATION,
                "real_time_sync": platform_integration_config.REAL_TIME_SYNC_ENABLED,
                "parallel_uploads": platform_integration_config.PARALLEL_UPLOADS_ENABLED,
            }
        },
        "total_configurations": 14,
        "production_ready": True,
        "copyright": "© 2025 Fahed Mlaiel. All rights reserved.",
    }
