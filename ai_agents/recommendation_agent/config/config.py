"""Enterprise Configuration Template for Recommendation Agent

This file provides production-ready configuration templates for different
deployment scenarios of the IA Influencer Recommendation Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL NOTICE: Configuration parameters are proprietary intellectual property.
Unauthorized modification or redistribution is prohibited.
"""
from typing import Dict, Any

"""Enterprise Configuration Template for Recommendation Agent

This file provides production-ready configuration templates for different
deployment scenarios of the IA Influencer Recommendation Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL NOTICE: Configuration parameters are proprietary intellectual property.
Unauthorized modification or redistribution is prohibited.
"""
from typing import Dict, Any
import os

# Development Environment Configuration
DEVELOPMENT_CONFIG: Dict[str, Any] = {
    "recommendation_models": {
        "collaborative_filtering": {
            "algorithm": "matrix_factorization",
            "factors": 50,
            "regularization": 0.01,
            "learning_rate": 0.005,
            "iterations": 100,
            "use_bias": True,
            "random_state": 42
        },
        "content_based": {
            "similarity_metric": "cosine",
            "feature_weights": {
                "genre": 0.3,
                "mood": 0.2,
                "tempo": 0.15,
                "artist_style": 0.25,
                "language": 0.1
            },
            "min_similarity_threshold": 0.1,
            "max_features": 10000,
            "ngram_range": (1, 2)
        },
        "hybrid": {
            "cf_weight": 0.6,
            "content_weight": 0.4,
            "diversity_weight": 0.1,
            "novelty_weight": 0.05,
            "popularity_weight": 0.05
        },
        "deep_learning": {
            "model_type": "neural_collaborative_filtering",
            "embedding_size": 32,
            "hidden_layers": [64, 32],
            "dropout_rate": 0.2,
            "activation": "relu",
            "optimizer": "adam",
            "learning_rate": 0.001,
            "batch_size": 256,
            "epochs": 50
        },
        "graph_based": {
            "node_embedding_dim": 64,
            "walk_length": 10,
            "num_walks": 40,
            "window_size": 5,
            "min_count": 1,
            "workers": 4
        }
    },
    "embedding_configs": {
        "text_model": "all-MiniLM-L6-v2",
        "audio_model": "facebook/wav2vec2-base-960h",
        "image_model": "openai/clip-vit-base-patch32",
        "multimodal_model": "openai/clip-vit-base-patch32",
        "cache_embeddings": True,
        "embedding_batch_size": 32
    },
    "personalization_settings": {
        "learning_rate": 0.01,
        "decay_factor": 0.95,
        "min_interactions": 5,
        "cold_start_strategy": "popular_items",
        "warm_up_interactions": 10,
        "max_history_length": 1000,
        "temporal_decay": True,
        "context_weight": 0.2
    },
    "ab_testing_config": {
        "enabled": False,
        "test_duration_days": 7,
        "sample_size_ratio": 0.1,
        "significance_threshold": 0.05,
        "min_sample_size": 100,
        "max_concurrent_tests": 3
    },
    "caching": {
        "recommendation_ttl": 1800,  # 30 minutes
        "user_profile_ttl": 3600,   # 1 hour
        "model_cache_ttl": 86400,   # 24 hours
        "max_cache_size": 10000,
        "cache_strategy": "lru"
    },
    "performance": {
        "max_recommendations": 100,
        "default_recommendations": 20,
        "max_concurrent_requests": 50,
        "request_timeout": 30,
        "batch_size": 32,
        "worker_threads": 4
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_retention_days": 30,
        "alert_thresholds": {
            "response_time_ms": 2000,
            "error_rate_percent": 5.0,
            "cache_hit_rate_percent": 60.0
        },
        "log_level": "DEBUG"
    }
}

# Production Environment Configuration
PRODUCTION_CONFIG: Dict[str, Any] = {
    "recommendation_models": {
        "collaborative_filtering": {
            "algorithm": "matrix_factorization",
            "factors": 200,
            "regularization": 0.005,
            "learning_rate": 0.001,
            "iterations": 500,
            "use_bias": True,
            "random_state": 42,
            "use_gpu": True
        },
        "content_based": {
            "similarity_metric": "cosine",
            "feature_weights": {
                "genre": 0.3,
                "mood": 0.2,
                "tempo": 0.15,
                "artist_style": 0.25,
                "language": 0.1
            },
            "min_similarity_threshold": 0.15,
            "max_features": 50000,
            "ngram_range": (1, 3),
            "use_tfidf": True,
            "sublinear_tf": True
        },
        "hybrid": {
            "cf_weight": 0.65,
            "content_weight": 0.35,
            "diversity_weight": 0.15,
            "novelty_weight": 0.08,
            "popularity_weight": 0.05,
            "temporal_weight": 0.1
        },
        "deep_learning": {
            "model_type": "neural_collaborative_filtering",
            "embedding_size": 128,
            "hidden_layers": [256, 128, 64],
            "dropout_rate": 0.3,
            "activation": "relu",
            "optimizer": "adam",
            "learning_rate": 0.0005,
            "batch_size": 512,
            "epochs": 200,
            "use_batch_norm": True,
            "early_stopping_patience": 20
        },
        "graph_based": {
            "node_embedding_dim": 128,
            "walk_length": 20,
            "num_walks": 80,
            "window_size": 10,
            "min_count": 2,
            "workers": 8,
            "use_skipgram": True
        },
        "reinforcement_learning": {
            "algorithm": "deep_q_network",
            "state_dim": 128,
            "action_dim": 1000,
            "hidden_layers": [256, 128],
            "learning_rate": 0.001,
            "epsilon": 0.1,
            "epsilon_decay": 0.995,
            "replay_buffer_size": 100000,
            "batch_size": 64,
            "target_update_freq": 1000
        }
    },
    "embedding_configs": {
        "text_model": "sentence-transformers/all-mpnet-base-v2",
        "audio_model": "facebook/wav2vec2-large-960h",
        "image_model": "openai/clip-vit-large-patch14",
        "multimodal_model": "openai/clip-vit-large-patch14",
        "cache_embeddings": True,
        "embedding_batch_size": 64,
        "use_gpu": True,
        "embedding_dim": 768
    },
    "personalization_settings": {
        "learning_rate": 0.005,
        "decay_factor": 0.98,
        "min_interactions": 3,
        "cold_start_strategy": "demographic_similarity",
        "warm_up_interactions": 20,
        "max_history_length": 5000,
        "temporal_decay": True,
        "context_weight": 0.25,
        "seasonal_adjustment": True,
        "location_weight": 0.1
    },
    "ab_testing_config": {
        "enabled": True,
        "test_duration_days": 14,
        "sample_size_ratio": 0.2,
        "significance_threshold": 0.01,
        "min_sample_size": 1000,
        "max_concurrent_tests": 5,
        "auto_winner_promotion": True,
        "statistical_power": 0.8
    },
    "caching": {
        "recommendation_ttl": 3600,    # 1 hour
        "user_profile_ttl": 7200,     # 2 hours
        "model_cache_ttl": 43200,     # 12 hours
        "max_cache_size": 100000,
        "cache_strategy": "lfu",
        "distributed_cache": True,
        "cache_warm_up": True
    },
    "performance": {
        "max_recommendations": 200,
        "default_recommendations": 50,
        "max_concurrent_requests": 500,
        "request_timeout": 10,
        "batch_size": 128,
        "worker_threads": 16,
        "use_async": True,
        "connection_pool_size": 20
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_retention_days": 90,
        "alert_thresholds": {
            "response_time_ms": 500,
            "error_rate_percent": 1.0,
            "cache_hit_rate_percent": 85.0,
            "memory_usage_percent": 80.0,
            "cpu_usage_percent": 70.0
        },
        "log_level": "INFO",
        "enable_distributed_tracing": True,
        "metrics_export_interval": 60
    },
    "security": {
        "enable_rate_limiting": True,
        "rate_limit_per_minute": 1000,
        "enable_api_key_auth": True,
        "enable_request_signing": True,
        "max_request_size_mb": 10,
        "enable_cors": True,
        "allowed_origins": ["https://app.ia-influencer.com"],
        "enable_encryption_at_rest": True
    },
    "data_privacy": {
        "enable_gdpr_compliance": True,
        "data_retention_days": 730,
        "enable_data_anonymization": True,
        "enable_user_data_export": True,
        "enable_user_data_deletion": True,
        "audit_log_retention_days": 365
    }
}

# Enterprise Environment Configuration
ENTERPRISE_CONFIG: Dict[str, Any] = {
    "recommendation_models": {
        "collaborative_filtering": {
            "algorithm": "advanced_matrix_factorization",
            "factors": 500,
            "regularization": 0.001,
            "learning_rate": 0.0005,
            "iterations": 1000,
            "use_bias": True,
            "use_implicit_feedback": True,
            "confidence_weight": 40,
            "random_state": 42,
            "use_gpu": True,
            "distributed_training": True
        },
        "content_based": {
            "similarity_metric": "advanced_cosine",
            "feature_weights": {
                "genre": 0.25,
                "mood": 0.2,
                "tempo": 0.15,
                "artist_style": 0.25,
                "language": 0.1,
                "audio_features": 0.3,
                "lyrical_content": 0.15,
                "production_quality": 0.1
            },
            "min_similarity_threshold": 0.2,
            "max_features": 100000,
            "ngram_range": (1, 4),
            "use_tfidf": True,
            "sublinear_tf": True,
            "use_semantic_similarity": True,
            "semantic_model": "sentence-transformers/all-mpnet-base-v2"
        },
        "hybrid": {
            "cf_weight": 0.4,
            "content_weight": 0.3,
            "deep_learning_weight": 0.25,
            "diversity_weight": 0.2,
            "novelty_weight": 0.1,
            "popularity_weight": 0.05,
            "temporal_weight": 0.15,
            "context_weight": 0.1,
            "ensemble_method": "weighted_average"
        },
        "deep_learning": {
            "model_type": "transformer_recommendation",
            "embedding_size": 256,
            "hidden_layers": [512, 256, 128, 64],
            "dropout_rate": 0.4,
            "activation": "gelu",
            "optimizer": "adamw",
            "learning_rate": 0.0001,
            "batch_size": 1024,
            "epochs": 500,
            "use_batch_norm": True,
            "use_layer_norm": True,
            "early_stopping_patience": 50,
            "gradient_clipping": 1.0,
            "weight_decay": 0.01,
            "attention_heads": 8,
            "transformer_layers": 6
        },
        "graph_based": {
            "node_embedding_dim": 256,
            "walk_length": 40,
            "num_walks": 200,
            "window_size": 20,
            "min_count": 5,
            "workers": 16,
            "use_skipgram": True,
            "hierarchical_softmax": True,
            "negative_sampling": 20,
            "graph_convolution_layers": 3
        },
        "reinforcement_learning": {
            "algorithm": "dueling_double_dqn",
            "state_dim": 256,
            "action_dim": 5000,
            "hidden_layers": [512, 256, 128],
            "learning_rate": 0.0005,
            "epsilon": 0.05,
            "epsilon_decay": 0.999,
            "replay_buffer_size": 1000000,
            "batch_size": 128,
            "target_update_freq": 2000,
            "priority_replay": True,
            "distributional_rl": True
        }
    },
    "embedding_configs": {
        "text_model": "sentence-transformers/all-mpnet-base-v2",
        "audio_model": "microsoft/unispeech-large",
        "image_model": "openai/clip-vit-large-patch14-336",
        "multimodal_model": "openai/clip-vit-large-patch14-336",
        "video_model": "microsoft/xclip-base-patch16",
        "cache_embeddings": True,
        "embedding_batch_size": 128,
        "use_gpu": True,
        "embedding_dim": 1024,
        "use_mixed_precision": True,
        "model_parallelism": True
    },
    "personalization_settings": {
        "learning_rate": 0.001,
        "decay_factor": 0.99,
        "min_interactions": 1,
        "cold_start_strategy": "multi_armed_bandit",
        "warm_up_interactions": 50,
        "max_history_length": 10000,
        "temporal_decay": True,
        "context_weight": 0.3,
        "seasonal_adjustment": True,
        "location_weight": 0.15,
        "social_influence_weight": 0.1,
        "trend_sensitivity": 0.2,
        "exploration_rate": 0.15
    },
    "ab_testing_config": {
        "enabled": True,
        "test_duration_days": 30,
        "sample_size_ratio": 0.3,
        "significance_threshold": 0.001,
        "min_sample_size": 10000,
        "max_concurrent_tests": 10,
        "auto_winner_promotion": True,
        "statistical_power": 0.95,
        "bayesian_optimization": True,
        "multi_armed_bandit": True,
        "contextual_bandits": True
    },
    "caching": {
        "recommendation_ttl": 7200,     # 2 hours
        "user_profile_ttl": 14400,     # 4 hours
        "model_cache_ttl": 86400,      # 24 hours
        "max_cache_size": 1000000,
        "cache_strategy": "adaptive_lfu",
        "distributed_cache": True,
        "cache_warm_up": True,
        "cache_partitioning": True,
        "cache_compression": True,
        "predictive_caching": True
    },
    "performance": {
        "max_recommendations": 500,
        "default_recommendations": 100,
        "max_concurrent_requests": 2000,
        "request_timeout": 5,
        "batch_size": 256,
        "worker_threads": 32,
        "use_async": True,
        "connection_pool_size": 50,
        "auto_scaling": True,
        "load_balancing": True,
        "circuit_breaker": True,
        "request_queuing": True
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_retention_days": 365,
        "alert_thresholds": {
            "response_time_ms": 100,
            "error_rate_percent": 0.1,
            "cache_hit_rate_percent": 90.0,
            "memory_usage_percent": 75.0,
            "cpu_usage_percent": 60.0,
            "disk_usage_percent": 80.0,
            "network_latency_ms": 50
        },
        "log_level": "INFO",
        "enable_distributed_tracing": True,
        "metrics_export_interval": 30,
        "real_time_dashboards": True,
        "anomaly_detection": True,
        "predictive_alerts": True,
        "custom_metrics": True
    },
    "security": {
        "enable_rate_limiting": True,
        "rate_limit_per_minute": 10000,
        "enable_api_key_auth": True,
        "enable_oauth2": True,
        "enable_request_signing": True,
        "enable_jwt_auth": True,
        "max_request_size_mb": 50,
        "enable_cors": True,
        "allowed_origins": [
            "https://app.ia-influencer.com",
            "https://admin.ia-influencer.com",
            "https://api.ia-influencer.com"
        ],
        "enable_encryption_at_rest": True,
        "enable_encryption_in_transit": True,
        "enable_field_level_encryption": True,
        "enable_audit_logging": True,
        "enable_intrusion_detection": True,
        "security_scanning": True,
        "vulnerability_monitoring": True
    },
    "data_privacy": {
        "enable_gdpr_compliance": True,
        "enable_ccpa_compliance": True,
        "data_retention_days": 2555,  # 7 years
        "enable_data_anonymization": True,
        "enable_pseudonymization": True,
        "enable_user_data_export": True,
        "enable_user_data_deletion": True,
        "enable_consent_management": True,
        "audit_log_retention_days": 2555,
        "data_lineage_tracking": True,
        "privacy_impact_assessment": True,
        "data_minimization": True
    },
    "scalability": {
        "horizontal_scaling": True,
        "auto_scaling_metrics": ["cpu", "memory", "request_rate"],
        "min_replicas": 3,
        "max_replicas": 100,
        "scale_up_threshold": 70,
        "scale_down_threshold": 30,
        "cool_down_period": 300,
        "distributed_computing": True,
        "microservices_architecture": True,
        "api_gateway": True,
        "service_mesh": True
    },
    "disaster_recovery": {
        "backup_frequency_hours": 6,
        "backup_retention_days": 90,
        "cross_region_replication": True,
        "automated_failover": True,
        "recovery_time_objective": 300,  # 5 minutes
        "recovery_point_objective": 3600,  # 1 hour
        "backup_encryption": True,
        "backup_compression": True,
        "disaster_recovery_testing": True
    }
}

def get_config(environment: str = "development") -> Dict[str, Any]:
    """
    Get configuration based on environment
    
    Args:
        environment: Environment name ('development', 'production', 'enterprise')
        
    Returns:
        Configuration dictionary
    """
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "enterprise": ENTERPRISE_CONFIG
    }
    
    if environment not in configs:
        raise ValueError(f"Unknown environment: {environment}")
    
    return configs[environment].copy()

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration parameters
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = [
        "recommendation_models",
        "embedding_configs", 
        "personalization_settings",
        "performance"
    ]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate recommendation models
    if "collaborative_filtering" not in config["recommendation_models"]:
        raise ValueError("Collaborative filtering model configuration required")
    
    if "content_based" not in config["recommendation_models"]:
        raise ValueError("Content-based model configuration required")
    
    # Validate embedding configs
    if "text_model" not in config["embedding_configs"]:
        raise ValueError("Text model configuration required")
    
    # Validate performance settings
    performance = config["performance"]
    if performance.get("max_recommendations", 0) <= 0:
        raise ValueError("max_recommendations must be positive")
    
    if performance.get("request_timeout", 0) <= 0:
        raise ValueError("request_timeout must be positive")
    
    return True

def get_environment_config() -> Dict[str, Any]:
    """
    Get configuration based on environment variables
    
    Returns:
        Configuration dictionary based on environment
    """
    env = os.getenv("RECOMMENDATION_ENVIRONMENT", "development").lower()
    config = get_config(env)
    
    # Override with environment-specific settings
    if os.getenv("RECOMMENDATION_DEBUG"):
        config["monitoring"]["log_level"] = "DEBUG"
    
    if os.getenv("RECOMMENDATION_CACHE_TTL"):
        config["caching"]["recommendation_ttl"] = int(os.getenv("RECOMMENDATION_CACHE_TTL"))
    
    if os.getenv("RECOMMENDATION_MAX_REQUESTS"):
        config["performance"]["max_concurrent_requests"] = int(os.getenv("RECOMMENDATION_MAX_REQUESTS"))
    
    return config

# Configuration validation on import
try:
    validate_config(DEVELOPMENT_CONFIG)
    validate_config(PRODUCTION_CONFIG) 
    validate_config(ENTERPRISE_CONFIG)
except Exception as e:
    print(f"Configuration validation error: {e}")
    raise
        "text_model": "all-MiniLM-L6-v2",
        "audio_model": "wav2vec2-base",
        "image_model": "clip-vit-base-patch32",
        "embedding_dimension": 384,
        "batch_size": 32
    },
    "personalization_settings": {
        "learning_rate": 0.01,
        "decay_factor": 0.95,
        "min_interactions": 3,
        "cold_start_strategy": "popular_items",
        "update_frequency_hours": 24,
        "context_weight": 0.2
    },
    "performance_monitoring": {
        "enabled": True,
        "metrics_collection_interval": 300,  # 5 minutes
        "alert_thresholds": {
            "response_time_ms": 2000,
            "error_rate_percent": 10.0,
            "memory_usage_percent": 80.0
        }
    },
    "ab_testing_config": {
        "enabled": True,
        "test_duration_days": 7,
        "sample_size_ratio": 0.2,
        "significance_threshold": 0.05,
        "max_concurrent_tests": 3
    },
    "caching": {
        "enabled": True,
        "cache_size": 1000,
        "ttl_seconds": 1800,  # 30 minutes
        "cache_strategy": "lru"
    }
}

# Production Environment Configuration
PRODUCTION_CONFIG: Dict[str, Any] = {
    "recommendation_models": {
        "collaborative_filtering": {
            "algorithm": "matrix_factorization",
            "factors": 200,
            "regularization": 0.001,
            "learning_rate": 0.001,
            "iterations": 500,
            "use_gpu": True
        },
        "content_based": {
            "similarity_metric": "cosine",
            "feature_weights": {
                "genre": 0.3,
                "mood": 0.2,
                "tempo": 0.15,
                "artist_style": 0.25,
                "language": 0.1
            },
            "min_similarity_threshold": 0.05,
            "advanced_features": True
        },
        "hybrid": {
            "cf_weight": 0.65,
            "content_weight": 0.35,
            "diversity_weight": 0.15,
            "novelty_weight": 0.1
        },
        "deep_learning": {
            "model_type": "neural_collaborative_filtering",
            "embedding_size": 128,
            "hidden_layers": [256, 128, 64],
            "dropout_rate": 0.1,
            "activation": "relu",
            "use_attention": True,
            "use_gpu": True
        }
    },
    "embedding_configs": {
        "text_model": "all-MiniLM-L6-v2",
        "audio_model": "wav2vec2-large",
        "image_model": "clip-vit-large-patch14",
        "embedding_dimension": 512,
        "batch_size": 128,
        "use_gpu": True
    },
    "personalization_settings": {
        "learning_rate": 0.001,
        "decay_factor": 0.98,
        "min_interactions": 5,
        "cold_start_strategy": "popular_items_with_diversity",
        "update_frequency_hours": 6,
        "context_weight": 0.3,
        "real_time_updates": True
    },
    "performance_monitoring": {
        "enabled": True,
        "metrics_collection_interval": 60,  # 1 minute
        "alert_thresholds": {
            "response_time_ms": 500,
            "error_rate_percent": 1.0,
            "memory_usage_percent": 70.0,
            "cpu_usage_percent": 80.0
        },
        "detailed_logging": True
    },
    "ab_testing_config": {
        "enabled": True,
        "test_duration_days": 14,
        "sample_size_ratio": 0.1,
        "significance_threshold": 0.01,
        "max_concurrent_tests": 5,
        "automated_analysis": True
    },
    "caching": {
        "enabled": True,
        "cache_size": 50000,
        "ttl_seconds": 900,  # 15 minutes
        "cache_strategy": "lru_with_frequency",
        "distributed_cache": True
    },
    "security": {
        "encryption_enabled": True,
        "data_anonymization": True,
        "privacy_mode": "gdpr_compliant",
        "audit_logging": True
    },
    "scalability": {
        "auto_scaling": True,
        "max_workers": 10,
        "load_balancing": True,
        "horizontal_scaling": True
    }
}

# High-Performance Configuration for Large Scale
ENTERPRISE_CONFIG: Dict[str, Any] = {
    "recommendation_models": {
        "collaborative_filtering": {
            "algorithm": "advanced_matrix_factorization",
            "factors": 500,
            "regularization": 0.0005,
            "learning_rate": 0.0005,
            "iterations": 1000,
            "use_gpu": True,
            "distributed_training": True
        },
        "content_based": {
            "similarity_metric": "learned_similarity",
            "feature_weights": "auto_learned",
            "min_similarity_threshold": 0.02,
            "advanced_features": True,
            "multi_modal_fusion": True
        },
        "hybrid": {
            "dynamic_weighting": True,
            "context_aware_fusion": True,
            "ensemble_methods": ["stacking", "voting"],
            "meta_learning": True
        },
        "deep_learning": {
            "model_type": "transformer_recommendation",
            "embedding_size": 256,
            "hidden_layers": [512, 256, 128, 64],
            "dropout_rate": 0.05,
            "activation": "gelu",
            "use_attention": True,
            "use_gpu": True,
            "multi_gpu": True
        },
        "reinforcement_learning": {
            "enabled": True,
            "algorithm": "deep_q_learning",
            "exploration_rate": 0.1,
            "reward_function": "user_satisfaction"
        }
    },
    "embedding_configs": {
        "text_model": "sentence-transformers/all-mpnet-base-v2",
        "audio_model": "facebook/wav2vec2-large-960h",
        "image_model": "openai/clip-vit-large-patch14",
        "multimodal_model": "flamingo-mini",
        "embedding_dimension": 768,
        "batch_size": 256,
        "use_gpu": True,
        "multi_gpu": True
    },
    "personalization_settings": {
        "learning_rate": 0.0005,
        "adaptive_learning_rate": True,
        "decay_factor": 0.99,
        "min_interactions": 10,
        "cold_start_strategy": "meta_learning",
        "update_frequency_hours": 1,
        "context_weight": 0.4,
        "real_time_updates": True,
        "continual_learning": True
    },
    "performance_monitoring": {
        "enabled": True,
        "metrics_collection_interval": 30,  # 30 seconds
        "alert_thresholds": {
            "response_time_ms": 200,
            "error_rate_percent": 0.1,
            "memory_usage_percent": 60.0,
            "cpu_usage_percent": 70.0,
            "gpu_usage_percent": 80.0
        },
        "detailed_logging": True,
        "ml_ops_integration": True
    },
    "ab_testing_config": {
        "enabled": True,
        "test_duration_days": 30,
        "sample_size_ratio": 0.05,
        "significance_threshold": 0.001,
        "max_concurrent_tests": 10,
        "automated_analysis": True,
        "bayesian_optimization": True
    },
    "caching": {
        "enabled": True,
        "cache_size": 200000,
        "ttl_seconds": 300,  # 5 minutes
        "cache_strategy": "intelligent_caching",
        "distributed_cache": True,
        "cache_warm_up": True
    },
    "security": {
        "encryption_enabled": True,
        "end_to_end_encryption": True,
        "data_anonymization": True,
        "differential_privacy": True,
        "privacy_mode": "enterprise_compliant",
        "audit_logging": True,
        "access_control": True
    },
    "scalability": {
        "auto_scaling": True,
        "max_workers": 50,
        "load_balancing": "intelligent",
        "horizontal_scaling": True,
        "kubernetes_integration": True,
        "microservices_architecture": True
    }
}

# Configuration selector function
def get_config(environment: str = "development") -> Dict[str, Any]:
    """
    Get configuration for specified environment
    
    Args:
        environment: "development", "production", or "enterprise"
    
    Returns:
        Configuration dictionary
    """
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG, 
        "enterprise": ENTERPRISE_CONFIG
    }
    
    if environment not in configs:
        raise ValueError(f"Unknown environment: {environment}")
    
    return configs[environment].copy()

# Configuration validation
def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and values"""
    required_sections = [
        "recommendation_models",
        "embedding_configs", 
        "personalization_settings",
        "performance_monitoring"
    ]
    
    for section in required_sections:
        if section not in config:
            return False
    
    return True

# Export configuration getter
__all__ = ["get_config", "validate_config", "DEVELOPMENT_CONFIG", "PRODUCTION_CONFIG", "ENTERPRISE_CONFIG"]
