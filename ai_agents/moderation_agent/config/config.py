"""Moderation Agent Configuration

Enterprise-grade configuration for ultra-advanced content moderation system.
Provides comprehensive safety filtering and automated compliance enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This configuration and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""
from typing import Dict, Any, List
from enum import Enum
import os

class ModerationLevel(Enum):
    """Content moderation strictness levels"""    PERMISSIVE = "permissive"
    STANDARD = "standard"
    STRICT = "strict"
    ULTRA_STRICT = "ultra_strict"

class RegionalCompliance(Enum):
    """Regional compliance frameworks"""    GDPR_EU = "gdpr_eu"
    COPPA_US = "coppa_us"
    PIPEDA_CA = "pipeda_ca"
    LGPD_BR = "lgpd_br"
    PDPA_SG = "pdpa_sg"

# Default configuration
DEFAULT_MODERATION_CONFIG = {
    "agent_settings": {
        "version": "2.1.0",
        "processing_timeout_seconds": 30,
        "max_concurrent_requests": 100,
        "enable_model_caching": True,
        "cache_ttl_minutes": 60
    },
    
    "moderation_thresholds": {
        "auto_approve": 0.1,
        "auto_flag": 0.6,
        "auto_block": 0.85,
        "human_review": 0.75,
        "emergency_stop": 0.95
    },
    
    "confidence_thresholds": {
        # Toxicity detection thresholds
        "toxicity_general": 0.7,
        "toxicity_severe": 0.6,
        "toxicity_obscene": 0.7,
        "toxicity_threat": 0.6,
        "toxicity_insult": 0.7,
        "toxicity_identity_attack": 0.6,
        
        # Content type specific thresholds
        "nsfw_general": 0.8,
        "nsfw_explicit": 0.9,
        "violence_graphic": 0.7,
        "violence_mild": 0.8,
        "hate_speech": 0.7,
        "harassment": 0.6,
        "spam_detection": 0.8,
        "self_harm": 0.5,  # Lower threshold for safety
        "child_safety": 0.4,  # Very low threshold
        "terrorism": 0.5,
        "drug_abuse": 0.7,
        "misinformation": 0.75
    },
    
    "model_configs": {
        "text_models": {
            "toxicity_model": "multilingual",
            "hate_speech_model": "unitary/toxic-bert",
            "sentiment_model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "spam_detection_model": "custom/spam-classifier-v2"
        },
        
        "image_models": {
            "nsfw_model": "Falconsai/nsfw_image_detection",
            "nudity_detector": "nudenet",
            "violence_detector": "custom/violence-detector-v1.3",
            "explicit_content_model": "custom/explicit-classifier"
        },
        
        "audio_models": {
            "speech_to_text": "whisper-base",
            "audio_classifier": "custom/audio-content-classifier",
            "music_analysis": "custom/music-content-analyzer"
        },
        
        "video_models": {
            "frame_analyzer": "combined/image-models",
            "motion_detector": "custom/motion-analysis",
            "deepfake_detector": "custom/deepfake-detection-v2"
        }
    },
    
    "processing_settings": {
        "text_processing": {
            "max_length": 10000,
            "enable_preprocessing": True,
            "language_detection": True,
            "supported_languages": ["en", "de", "fr", "es", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh"]
        },
        
        "image_processing": {
            "max_file_size_mb": 50,
            "supported_formats": ["jpg", "jpeg", "png", "gif", "webp", "bmp"],
            "resize_for_analysis": True,
            "max_resolution": [2048, 2048]
        },
        
        "video_processing": {
            "max_file_size_mb": 500,
            "supported_formats": ["mp4", "avi", "mov", "mkv", "webm"],
            "max_duration_minutes": 60,
            "frame_sampling_rate": 1,  # Extract 1 frame per second
            "audio_extraction": True
        },
        
        "audio_processing": {
            "max_file_size_mb": 100,
            "supported_formats": ["mp3", "wav", "flac", "ogg", "m4a"],
            "max_duration_minutes": 30,
            "sample_rate": 16000,
            "transcription_enabled": True
        },
        
        "live_stream": {
            "monitoring_interval_seconds": 5,
            "frame_capture_quality": "medium",
            "audio_analysis_enabled": True,
            "real_time_alerts": True
        }
    },
    
    "violation_weights": {
        "hate_speech": 1.0,
        "violence": 0.9,
        "sexual_content": 0.8,
        "nudity": 0.7,
        "harassment": 0.7,
        "self_harm": 1.0,
        "child_safety": 1.0,
        "terrorism": 1.0,
        "drug_abuse": 0.6,
        "spam": 0.3,
        "misinformation": 0.8,
        "copyright": 0.5,
        "illegal_activity": 0.9
    },
    
    "review_workflow": {
        "enable_human_review": True,
        "auto_escalate_critical": True,
        "reviewer_assignment": "round_robin",  # round_robin, random, skill_based
        "max_review_time_hours": 24,
        "appeal_window_hours": 72,
        "appeal_levels": 3,
        "reviewer_consensus_required": 2,  # Number of reviewers for consensus
        "priority_queue_enabled": True
    },
    
    "compliance_settings": {
        "regional_frameworks": [
            RegionalCompliance.GDPR_EU.value,
            RegionalCompliance.COPPA_US.value,
            RegionalCompliance.PIPEDA_CA.value
        ],
        
        "data_retention": {
            "moderation_logs_days": 90,
            "audit_logs_days": 365,
            "user_data_retention_days": 30,
            "violation_evidence_days": 180
        },
        
        "privacy_settings": {
            "anonymize_logs": True,
            "encrypt_sensitive_data": True,
            "zero_retention_content": True,  # Don't store actual content
            "gdpr_compliance": True,
            "right_to_be_forgotten": True
        },
        
        "reporting_requirements": {
            "transparency_reports": True,
            "government_reporting": True,
            "user_appeal_reports": True,
            "bias_assessment_reports": True
        }
    },
    
    "performance_settings": {
        "caching": {
            "enable_result_caching": True,
            "cache_ttl_minutes": 60,
            "max_cache_size_mb": 1000,
            "cache_backend": "redis"
        },
        
        "optimization": {
            "batch_processing": True,
            "parallel_analysis": True,
            "gpu_acceleration": True,
            "model_quantization": True,
            "inference_optimization": True
        },
        
        "scaling": {
            "auto_scaling": True,
            "max_instances": 10,
            "min_instances": 2,
            "scale_up_threshold": 0.8,
            "scale_down_threshold": 0.3,
            "health_check_enabled": True
        }
    },
    
    "monitoring_and_alerting": {
        "metrics": {
            "enable_detailed_metrics": True,
            "performance_tracking": True,
            "accuracy_monitoring": True,
            "bias_detection": True,
            "drift_detection": True
        },
        
        "alerts": {
            "high_violation_rate": {
                "threshold": 0.5,
                "time_window_minutes": 15,
                "notification_channels": ["email", "slack", "webhook"]
            },
            
            "model_performance_degradation": {
                "accuracy_drop_threshold": 0.05,
                "time_window_hours": 6,
                "notification_channels": ["email", "pagerduty"]
            },
            
            "system_overload": {
                "cpu_threshold": 0.9,
                "memory_threshold": 0.9,
                "queue_size_threshold": 1000,
                "notification_channels": ["pagerduty"]
            }
        },
        
        "dashboards": {
            "real_time_dashboard": True,
            "executive_dashboard": True,
            "operational_dashboard": True,
            "compliance_dashboard": True
        }
    },
    
    "security_settings": {
        "authentication": {
            "api_key_required": True,
            "jwt_validation": True,
            "rate_limiting": True,
            "ip_whitelisting": False
        },
        
        "data_security": {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "secure_key_management": True,
            "audit_logging": True
        },
        
        "access_control": {
            "rbac_enabled": True,
            "admin_approval_required": True,
            "two_factor_auth": True,
            "session_timeout_minutes": 30
        }
    }
}

def get_moderation_config(level: ModerationLevel = ModerationLevel.STANDARD) -> Dict[str, Any]:
    """    Get moderation configuration based on strictness level
    
    Args:
        level: Moderation strictness level
        
    Returns:
        Configuration dictionary
    """    config = DEFAULT_MODERATION_CONFIG.copy()
    
    if level == ModerationLevel.PERMISSIVE:
        # More lenient thresholds
        config["moderation_thresholds"].update({
            "auto_approve": 0.3,
            "auto_flag": 0.8,
            "auto_block": 0.9,
            "human_review": 0.85
        })
        
        # Higher confidence thresholds (less sensitive)
        for key in config["confidence_thresholds"]:
            if key not in ["self_harm", "child_safety", "terrorism"]:
                config["confidence_thresholds"][key] += 0.1
    
    elif level == ModerationLevel.STRICT:
        # More strict thresholds
        config["moderation_thresholds"].update({
            "auto_approve": 0.05,
            "auto_flag": 0.4,
            "auto_block": 0.7,
            "human_review": 0.6
        })
        
        # Lower confidence thresholds (more sensitive)
        for key in config["confidence_thresholds"]:
            config["confidence_thresholds"][key] = max(0.1, config["confidence_thresholds"][key] - 0.1)
    
    elif level == ModerationLevel.ULTRA_STRICT:
        # Maximum strictness
        config["moderation_thresholds"].update({
            "auto_approve": 0.02,
            "auto_flag": 0.2,
            "auto_block": 0.5,
            "human_review": 0.3
        })
        
        # Very low confidence thresholds (maximum sensitivity)
        for key in config["confidence_thresholds"]:
            config["confidence_thresholds"][key] = max(0.05, config["confidence_thresholds"][key] - 0.2)
    
    return config

def get_regional_config(regions: List[RegionalCompliance]) -> Dict[str, Any]:
    """    Get configuration adapted for specific regional compliance requirements
    
    Args:
        regions: List of regional compliance frameworks
        
    Returns:
        Regional configuration adjustments
    """    regional_config = {}
    
    if RegionalCompliance.GDPR_EU in regions:
        regional_config.update({
            "data_retention_days": 30,  # Minimize data retention
            "explicit_consent_required": True,
            "right_to_be_forgotten": True,
            "data_portability": True,
            "privacy_by_design": True
        })
    
    if RegionalCompliance.COPPA_US in regions:
        regional_config.update({
            "child_content_detection": True,
            "parental_consent_required": True,
            "age_verification_strict": True,
            "child_safety_threshold": 0.1  # Very low threshold
        })
    
    if RegionalCompliance.PIPEDA_CA in regions:
        regional_config.update({
            "explicit_consent_tracking": True,
            "purpose_limitation": True,
            "accuracy_requirements": True
        })
    
    return regional_config

# Environment-specific configurations
DEVELOPMENT_CONFIG_OVERRIDES = {
    "agent_settings": {
        "processing_timeout_seconds": 60,  # Longer timeout for debugging
        "max_concurrent_requests": 10
    },
    "model_configs": {
        "enable_model_downloads": True,
        "use_lightweight_models": True
    },
    "monitoring_and_alerting": {
        "alerts": {
            "enable_test_alerts": True,
            "notification_channels": ["console"]
        }
    }
}

PRODUCTION_CONFIG_OVERRIDES = {
    "agent_settings": {
        "processing_timeout_seconds": 15,  # Faster timeout in production
        "max_concurrent_requests": 500
    },
    "performance_settings": {
        "optimization": {
            "aggressive_optimization": True,
            "preload_models": True
        },
        "scaling": {
            "auto_scaling": True,
            "max_instances": 50
        }
    },
    "security_settings": {
        "authentication": {
            "strict_validation": True,
            "rate_limiting_strict": True
        }
    }
}

def get_environment_config(environment: str = "development") -> Dict[str, Any]:
    """    Get environment-specific configuration
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        Environment configuration overrides
    """    if environment == "production":
        return PRODUCTION_CONFIG_OVERRIDES
    elif environment == "development":
        return DEVELOPMENT_CONFIG_OVERRIDES
    else:
        return {}
