"""
Entity Extraction Configuration - IA Influencer Agent

Advanced configuration system for entity extraction module with environment-specific
settings, model configurations, and performance optimization parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EntityExtractionConfig:
    """Comprehensive configuration for entity extraction system"""
    
    # Model Configuration
    MODEL_CACHE_DIR: str = "/tmp/entity_models"
    PRIMARY_NER_MODEL: str = "bert-base-multilingual-cased"
    CREATIVE_MODEL_PATH: Optional[str] = None
    SPACY_MODEL: str = "en_core_web_trf"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    
    # Performance Configuration
    MAX_CONCURRENT_EXTRACTIONS: int = 10
    EXTRACTION_TIMEOUT: int = 300  # 5 minutes
    CACHE_TTL: int = 3600  # 1 hour
    BATCH_SIZE: int = 32
    USE_GPU: bool = True
    GPU_MEMORY_FRACTION: float = 0.7
    
    # Quality Configuration
    MIN_CONFIDENCE_THRESHOLD: float = 0.5
    ENTITY_VALIDATION_ENABLED: bool = True
    DUPLICATE_DETECTION_ENABLED: bool = True
    RELATIONSHIP_INFERENCE_ENABLED: bool = True
    
    # External API Configuration
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    DISCOGS_API_KEY: Optional[str] = None
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR: str = "/data/knowledge_bases"
    VECTOR_INDEX_DIR: str = "/data/vector_indexes"
    AUTO_UPDATE_KB: bool = True
    KB_UPDATE_INTERVAL: int = 86400  # 24 hours
    
    # Security Configuration
    CONTENT_MODERATION_ENABLED: bool = True
    PII_DETECTION_ENABLED: bool = True
    SECURITY_SCAN_ENABLED: bool = True
    
    # Monitoring Configuration
    METRICS_ENABLED: bool = True
    PERFORMANCE_MONITORING: bool = True
    ERROR_TRACKING: bool = True
    DETAILED_LOGGING: bool = False
    
    # Feature Flags
    ENABLE_REALTIME_PROCESSING: bool = True
    ENABLE_COLLABORATION_TRACKING: bool = True
    ENABLE_BUSINESS_ANALYSIS: bool = True
    ENABLE_MONETIZATION_ANALYSIS: bool = True
    ENABLE_SEO_OPTIMIZATION: bool = True
    ENABLE_TREND_DETECTION: bool = True
    
    @classmethod
    def from_env(cls) -> 'EntityExtractionConfig':
        """Create configuration from environment variables"""



        return cls(
            MODEL_CACHE_DIR=os.getenv('ENTITY_MODEL_CACHE_DIR', '/tmp/entity_models'),
            PRIMARY_NER_MODEL=os.getenv('PRIMARY_NER_MODEL', 'bert-base-multilingual-cased'),
            CREATIVE_MODEL_PATH=os.getenv('CREATIVE_MODEL_PATH'),
            SPACY_MODEL=os.getenv('SPACY_MODEL', 'en_core_web_trf'),
            SENTENCE_TRANSFORMER_MODEL=os.getenv('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2'),
            
            MAX_CONCURRENT_EXTRACTIONS=int(os.getenv('MAX_CONCURRENT_EXTRACTIONS', '10')),
            EXTRACTION_TIMEOUT=int(os.getenv('EXTRACTION_TIMEOUT', '300')),
            CACHE_TTL=int(os.getenv('CACHE_TTL', '3600')),
            BATCH_SIZE=int(os.getenv('BATCH_SIZE', '32')),
            USE_GPU=os.getenv('USE_GPU', 'true').lower() == 'true',
            GPU_MEMORY_FRACTION=float(os.getenv('GPU_MEMORY_FRACTION', '0.7')),
            
            MIN_CONFIDENCE_THRESHOLD=float(os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.5')),
            ENTITY_VALIDATION_ENABLED=os.getenv('ENTITY_VALIDATION_ENABLED', 'true').lower() == 'true',
            DUPLICATE_DETECTION_ENABLED=os.getenv('DUPLICATE_DETECTION_ENABLED', 'true').lower() == 'true',
            RELATIONSHIP_INFERENCE_ENABLED=os.getenv('RELATIONSHIP_INFERENCE_ENABLED', 'true').lower() == 'true',
            
            SPOTIFY_CLIENT_ID=os.getenv('SPOTIFY_CLIENT_ID'),
            SPOTIFY_CLIENT_SECRET=os.getenv('SPOTIFY_CLIENT_SECRET'),
            YOUTUBE_API_KEY=os.getenv('YOUTUBE_API_KEY'),
            INSTAGRAM_ACCESS_TOKEN=os.getenv('INSTAGRAM_ACCESS_TOKEN'),
            DISCOGS_API_KEY=os.getenv('DISCOGS_API_KEY'),
            
            KNOWLEDGE_BASE_DIR=os.getenv('KNOWLEDGE_BASE_DIR', '/data/knowledge_bases'),
            VECTOR_INDEX_DIR=os.getenv('VECTOR_INDEX_DIR', '/data/vector_indexes'),
            AUTO_UPDATE_KB=os.getenv('AUTO_UPDATE_KB', 'true').lower() == 'true',
            KB_UPDATE_INTERVAL=int(os.getenv('KB_UPDATE_INTERVAL', '86400')),
            
            CONTENT_MODERATION_ENABLED=os.getenv('CONTENT_MODERATION_ENABLED', 'true').lower() == 'true',
            PII_DETECTION_ENABLED=os.getenv('PII_DETECTION_ENABLED', 'true').lower() == 'true',
            SECURITY_SCAN_ENABLED=os.getenv('SECURITY_SCAN_ENABLED', 'true').lower() == 'true',
            
            METRICS_ENABLED=os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
            PERFORMANCE_MONITORING=os.getenv('PERFORMANCE_MONITORING', 'true').lower() == 'true',
            ERROR_TRACKING=os.getenv('ERROR_TRACKING', 'true').lower() == 'true',
            DETAILED_LOGGING=os.getenv('DETAILED_LOGGING', 'false').lower() == 'true',
            
            ENABLE_REALTIME_PROCESSING=os.getenv('ENABLE_REALTIME_PROCESSING', 'true').lower() == 'true',
            ENABLE_COLLABORATION_TRACKING=os.getenv('ENABLE_COLLABORATION_TRACKING', 'true').lower() == 'true',
            ENABLE_BUSINESS_ANALYSIS=os.getenv('ENABLE_BUSINESS_ANALYSIS', 'true').lower() == 'true',
            ENABLE_MONETIZATION_ANALYSIS=os.getenv('ENABLE_MONETIZATION_ANALYSIS', 'true').lower() == 'true',
            ENABLE_SEO_OPTIMIZATION=os.getenv('ENABLE_SEO_OPTIMIZATION', 'true').lower() == 'true',
            ENABLE_TREND_DETECTION=os.getenv('ENABLE_TREND_DETECTION', 'true').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""



        return {
            'model_config': {
                'cache_dir': self.MODEL_CACHE_DIR,
                'primary_ner_model': self.PRIMARY_NER_MODEL,
                'creative_model_path': self.CREATIVE_MODEL_PATH,
                'spacy_model': self.SPACY_MODEL,
                'sentence_transformer_model': self.SENTENCE_TRANSFORMER_MODEL
            },
            'performance_config': {
                'max_concurrent_extractions': self.MAX_CONCURRENT_EXTRACTIONS,
                'extraction_timeout': self.EXTRACTION_TIMEOUT,
                'cache_ttl': self.CACHE_TTL,
                'batch_size': self.BATCH_SIZE,
                'use_gpu': self.USE_GPU,
                'gpu_memory_fraction': self.GPU_MEMORY_FRACTION
            },
            'quality_config': {
                'min_confidence_threshold': self.MIN_CONFIDENCE_THRESHOLD,
                'entity_validation_enabled': self.ENTITY_VALIDATION_ENABLED,
                'duplicate_detection_enabled': self.DUPLICATE_DETECTION_ENABLED,
                'relationship_inference_enabled': self.RELATIONSHIP_INFERENCE_ENABLED
            },
            'api_config': {
                'spotify_client_id': self.SPOTIFY_CLIENT_ID,
                'spotify_client_secret': self.SPOTIFY_CLIENT_SECRET,
                'youtube_api_key': self.YOUTUBE_API_KEY,
                'instagram_access_token': self.INSTAGRAM_ACCESS_TOKEN,
                'discogs_api_key': self.DISCOGS_API_KEY
            },
            'knowledge_base_config': {
                'knowledge_base_dir': self.KNOWLEDGE_BASE_DIR,
                'vector_index_dir': self.VECTOR_INDEX_DIR,
                'auto_update_kb': self.AUTO_UPDATE_KB,
                'kb_update_interval': self.KB_UPDATE_INTERVAL
            },
            'security_config': {
                'content_moderation_enabled': self.CONTENT_MODERATION_ENABLED,
                'pii_detection_enabled': self.PII_DETECTION_ENABLED,
                'security_scan_enabled': self.SECURITY_SCAN_ENABLED
            },
            'monitoring_config': {
                'metrics_enabled': self.METRICS_ENABLED,
                'performance_monitoring': self.PERFORMANCE_MONITORING,
                'error_tracking': self.ERROR_TRACKING,
                'detailed_logging': self.DETAILED_LOGGING
            },
            'feature_flags': {
                'enable_realtime_processing': self.ENABLE_REALTIME_PROCESSING,
                'enable_collaboration_tracking': self.ENABLE_COLLABORATION_TRACKING,
                'enable_business_analysis': self.ENABLE_BUSINESS_ANALYSIS,
                'enable_monetization_analysis': self.ENABLE_MONETIZATION_ANALYSIS,
                'enable_seo_optimization': self.ENABLE_SEO_OPTIMIZATION,
                'enable_trend_detection': self.ENABLE_TREND_DETECTION
            }
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""



        try:
            # Validate paths
            Path(self.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
            Path(self.KNOWLEDGE_BASE_DIR).mkdir(parents=True, exist_ok=True)
            Path(self.VECTOR_INDEX_DIR).mkdir(parents=True, exist_ok=True)
            
            # Validate numeric ranges
            assert 0 < self.MAX_CONCURRENT_EXTRACTIONS <= 100, "MAX_CONCURRENT_EXTRACTIONS must be between 1 and 100"
            assert 0 < self.EXTRACTION_TIMEOUT <= 3600, "EXTRACTION_TIMEOUT must be between 1 and 3600 seconds"
            assert 0 < self.CACHE_TTL <= 86400, "CACHE_TTL must be between 1 and 86400 seconds"
            assert 0 < self.BATCH_SIZE <= 1000, "BATCH_SIZE must be between 1 and 1000"
            assert 0.0 <= self.MIN_CONFIDENCE_THRESHOLD <= 1.0, "MIN_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0"
            assert 0.1 <= self.GPU_MEMORY_FRACTION <= 1.0, "GPU_MEMORY_FRACTION must be between 0.1 and 1.0"
            
            return True
            
        except (AssertionError, OSError) as e:
            raise ValueError(f"Configuration validation failed: {e}")


# Default configuration instances
DEFAULT_CONFIG = EntityExtractionConfig()
PRODUCTION_CONFIG = EntityExtractionConfig(
    DETAILED_LOGGING=False,
    MAX_CONCURRENT_EXTRACTIONS=20,
    CACHE_TTL=7200,
    USE_GPU=True,
    METRICS_ENABLED=True,
    PERFORMANCE_MONITORING=True
)

DEVELOPMENT_CONFIG = EntityExtractionConfig(
    DETAILED_LOGGING=True,
    MAX_CONCURRENT_EXTRACTIONS=5,
    CACHE_TTL=300,
    USE_GPU=False,
    METRICS_ENABLED=True,
    PERFORMANCE_MONITORING=True
)

# Configuration factory
def get_config(environment: str = "development") -> EntityExtractionConfig:
    """Get configuration based on environment"""
    if environment.lower() == "production":
        return PRODUCTION_CONFIG
    elif environment.lower() == "development":
        return DEVELOPMENT_CONFIG
    else:
        return DEFAULT_CONFIG
