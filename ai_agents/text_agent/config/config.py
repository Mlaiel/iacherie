"""Text Agent Configuration

Default configuration settings for the Text Agent module.
Can be overridden through environment variables or config files.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import List, Dict, Any

# Text Processing Configuration
DEFAULT_MAX_TEXT_LENGTH = int(os.getenv("TEXT_AGENT_MAX_LENGTH", "10000"))
DEFAULT_MIN_TEXT_LENGTH = int(os.getenv("TEXT_AGENT_MIN_LENGTH", "10"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("TEXT_AGENT_SIMILARITY_THRESHOLD", "0.85"))

# Language Support
DEFAULT_SUPPORTED_LANGUAGES = [
    'en', 'fr', 'de', 'es', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn',
    'ar', 'hi', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'hu'
]

# Model Configuration
DEFAULT_SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
DEFAULT_GPT2_MODEL = "gpt2-medium"
DEFAULT_T5_MODEL = "t5-small"
DEFAULT_BART_MODEL = "facebook/bart-large"

# Performance Settings
DEFAULT_BATCH_SIZE = int(os.getenv("TEXT_AGENT_BATCH_SIZE", "32"))
DEFAULT_NUM_AGENTS = int(os.getenv("TEXT_AGENT_NUM_AGENTS", "3"))
DEFAULT_CACHE_SIZE = int(os.getenv("TEXT_AGENT_CACHE_SIZE", "1000"))

# Quality Thresholds
DEFAULT_MIN_QUALITY_SCORE = float(os.getenv("TEXT_AGENT_MIN_QUALITY", "0.6"))
DEFAULT_MIN_RELEVANCE_SCORE = float(os.getenv("TEXT_AGENT_MIN_RELEVANCE", "0.7"))
DEFAULT_MAX_REPETITION_RATE = float(os.getenv("TEXT_AGENT_MAX_REPETITION", "0.3"))

# Security Settings
DEFAULT_RATE_LIMIT_PER_MINUTE = int(os.getenv("TEXT_AGENT_RATE_LIMIT", "100"))
DEFAULT_ENABLE_CONTENT_ENCRYPTION = os.getenv("TEXT_AGENT_ENCRYPTION", "true").lower() == "true"

# Database Configuration
DEFAULT_DB_POOL_SIZE = int(os.getenv("TEXT_AGENT_DB_POOL_SIZE", "10"))
DEFAULT_REDIS_TTL = int(os.getenv("TEXT_AGENT_REDIS_TTL", "3600"))

# Logging Configuration
DEFAULT_LOG_LEVEL = os.getenv("TEXT_AGENT_LOG_LEVEL", "INFO")
DEFAULT_ENABLE_PERFORMANCE_LOGGING = os.getenv("TEXT_AGENT_PERF_LOG", "true").lower() == "true"

# Generation Settings
DEFAULT_GENERATION_TEMPERATURE = float(os.getenv("TEXT_AGENT_TEMPERATURE", "0.7"))
DEFAULT_GENERATION_TOP_P = float(os.getenv("TEXT_AGENT_TOP_P", "0.9"))
DEFAULT_GENERATION_TOP_K = int(os.getenv("TEXT_AGENT_TOP_K", "50"))

# Text Processing Defaults
DEFAULT_PROCESSING_CONFIG = {
    "max_length": DEFAULT_MAX_TEXT_LENGTH,
    "min_length": DEFAULT_MIN_TEXT_LENGTH,
    "enable_preprocessing": True,
    "enable_sentiment_analysis": True,
    "enable_entity_extraction": True,
    "enable_topic_modeling": True,
    "enable_quality_assessment": True,
    "languages_supported": DEFAULT_SUPPORTED_LANGUAGES,
    "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLD,
    "fingerprint_algorithm": "sha256"
}

# NLP Engine Configuration
NLP_ENGINE_CONFIG = {
    "enable_ensemble_sentiment": True,
    "enable_emotion_analysis": True,
    "enable_advanced_entities": True,
    "confidence_threshold": 0.7,
    "max_topics": 10,
    "cache_embeddings": True
}

# Translation Configuration
TRANSLATION_CONFIG = {
    "default_service": "google",
    "enable_quality_assessment": True,
    "enable_alternatives": True,
    "max_alternatives": 3,
    "quality_threshold": 0.6
}

# Content Generation Configuration
GENERATION_CONFIG = {
    "default_max_length": 500,
    "default_min_length": 50,
    "default_temperature": DEFAULT_GENERATION_TEMPERATURE,
    "default_top_p": DEFAULT_GENERATION_TOP_P,
    "default_top_k": DEFAULT_GENERATION_TOP_K,
    "enable_quality_control": True,
    "enable_style_adaptation": True,
    "min_quality_threshold": DEFAULT_MIN_QUALITY_SCORE
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "enable_prometheus_metrics": True,
    "enable_performance_tracking": DEFAULT_ENABLE_PERFORMANCE_LOGGING,
    "enable_usage_analytics": True,
    "metrics_port": int(os.getenv("TEXT_AGENT_METRICS_PORT", "9090")),
    "health_check_interval": int(os.getenv("TEXT_AGENT_HEALTH_INTERVAL", "60"))
}

# Security Configuration
SECURITY_CONFIG = {
    "enable_rate_limiting": True,
    "rate_limit_per_minute": DEFAULT_RATE_LIMIT_PER_MINUTE,
    "enable_content_encryption": DEFAULT_ENABLE_CONTENT_ENCRYPTION,
    "enable_audit_logging": True,
    "enable_input_validation": True,
    "max_concurrent_requests": int(os.getenv("TEXT_AGENT_MAX_CONCURRENT", "100"))
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        "processing": DEFAULT_PROCESSING_CONFIG,
        "nlp_engine": NLP_ENGINE_CONFIG,
        "translation": TRANSLATION_CONFIG,
        "generation": GENERATION_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "security": SECURITY_CONFIG,
        "models": {
            "sentence_transformer": DEFAULT_SENTENCE_TRANSFORMER_MODEL,
            "gpt2": DEFAULT_GPT2_MODEL,
            "t5": DEFAULT_T5_MODEL,
            "bart": DEFAULT_BART_MODEL
        },
        "performance": {
            "batch_size": DEFAULT_BATCH_SIZE,
            "num_agents": DEFAULT_NUM_AGENTS,
            "cache_size": DEFAULT_CACHE_SIZE,
            "db_pool_size": DEFAULT_DB_POOL_SIZE,
            "redis_ttl": DEFAULT_REDIS_TTL
        }
    }

def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file"""
    import json
    from pathlib import Path
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if config_file.suffix.lower() == '.json':
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif config_file.suffix.lower() in ['.yml', '.yaml']:
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML is required to load YAML configuration files")
    else:
        raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge configuration dictionaries"""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged

# Export default configuration
DEFAULT_CONFIG = get_config()
