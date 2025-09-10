"""
Copyright Fingerprinting Configuration - Enterprise Configuration Management
Enterprise configuration for copyright management and fingerprinting systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class FingerprintAlgorithm(str, Enum):
    """Fingerprinting algorithms"""
    CHROMAPRINT = "chromaprint"
    SIFT = "sift"
    PERCEPTUAL_HASH = "perceptual_hash"
    SPECTRAL_HASH = "spectral_hash"
    DEEP_LEARNING_HASH = "deep_learning_hash"
    CUSTOM_FINGERPRINTING = "custom_fingerprinting"
    WAVELET_HASH = "wavelet_hash"
    FOURIER_HASH = "fourier_hash"


class ContentType(str, Enum):
    """Content types for fingerprinting"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMEDIA = "multimedia"


class MatchingThreshold(str, Enum):
    """Matching threshold levels"""
    STRICT = "strict"      # >0.98
    HIGH = "high"          # >0.95
    MEDIUM = "medium"      # >0.90
    LOW = "low"           # >0.80
    PERMISSIVE = "permissive" # >0.70


class FingerprintDatabase(str, Enum):
    """Fingerprint database types"""
    INTERNAL = "internal"
    EXTERNAL_PARTNER = "external_partner"
    PUBLIC_API = "public_api"
    BLOCKCHAIN = "blockchain"
    DISTRIBUTED = "distributed"


@dataclass
class AlgorithmConfiguration:
    """Fingerprinting algorithm configuration"""
    algorithm_name: str
    content_types: List[ContentType]
    accuracy: float
    processing_speed_ms: int
    memory_requirements_mb: int
    scalability_factor: float
    parameters: Dict[str, Any]


@dataclass
class MatchingConfiguration:
    """Content matching configuration"""
    threshold: float
    false_positive_rate: float
    false_negative_rate: float
    processing_timeout_ms: int
    batch_size: int
    parallel_processing: bool


@dataclass
class DatabaseConfiguration:
    """Fingerprint database configuration"""
    database_type: FingerprintDatabase
    connection_config: Dict[str, Any]
    backup_enabled: bool
    replication_factor: int
    sharding_enabled: bool
    encryption_enabled: bool


class CopyrightFingerprintingSettings:
    """Copyright fingerprinting configuration settings"""
    
    def __init__(self):
        # Algorithm Configurations
        self.algorithms = {
            "chromaprint_audio": AlgorithmConfiguration(
                algorithm_name="chromaprint_audio",
                content_types=[ContentType.AUDIO],
                accuracy=0.98,
                processing_speed_ms=500,
                memory_requirements_mb=256,
                scalability_factor=0.95,
                parameters={
                    "sample_rate": 11025,
                    "frame_size": 4096,
                    "overlap": 0.5,
                    "hash_length": 120
                }
            ),
            
            "sift_image": AlgorithmConfiguration(
                algorithm_name="sift_image",
                content_types=[ContentType.IMAGE],
                accuracy=0.96,
                processing_speed_ms=800,
                memory_requirements_mb=512,
                scalability_factor=0.90,
                parameters={
                    "num_features": 500,
                    "contrast_threshold": 0.04,
                    "edge_threshold": 10,
                    "sigma": 1.6
                }
            ),
            
            "perceptual_hash_video": AlgorithmConfiguration(
                algorithm_name="perceptual_hash_video",
                content_types=[ContentType.VIDEO],
                accuracy=0.94,
                processing_speed_ms=2000,
                memory_requirements_mb=1024,
                scalability_factor=0.85,
                parameters={
                    "frame_sampling_rate": 1,
                    "hash_size": 64,
                    "temporal_segments": 10,
                    "spatial_grid": [8, 8]
                }
            ),
            
            "spectral_hash_audio": AlgorithmConfiguration(
                algorithm_name="spectral_hash_audio",
                content_types=[ContentType.AUDIO],
                accuracy=0.97,
                processing_speed_ms=600,
                memory_requirements_mb=384,
                scalability_factor=0.92,
                parameters={
                    "fft_size": 2048,
                    "hop_length": 512,
                    "mel_bands": 128,
                    "time_frames": 32
                }
            ),
            
            "deep_learning_multimedia": AlgorithmConfiguration(
                algorithm_name="deep_learning_multimedia",
                content_types=[ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE],
                accuracy=0.99,
                processing_speed_ms=1500,
                memory_requirements_mb=2048,
                scalability_factor=0.88,
                parameters={
                    "model_architecture": "resnet50",
                    "embedding_dimension": 512,
                    "batch_size": 32,
                    "preprocessing": "standardization"
                }
            ),
            
            "text_fingerprint": AlgorithmConfiguration(
                algorithm_name="text_fingerprint",
                content_types=[ContentType.TEXT],
                accuracy=0.95,
                processing_speed_ms=200,
                memory_requirements_mb=128,
                scalability_factor=0.98,
                parameters={
                    "ngram_size": 3,
                    "vocabulary_size": 10000,
                    "hash_functions": 64,
                    "similarity_metric": "jaccard"
                }
            )
        }
        
        # Matching Configurations by Content Type
        self.matching_configurations = {
            ContentType.AUDIO: MatchingConfiguration(
                threshold=0.95,
                false_positive_rate=0.001,
                false_negative_rate=0.02,
                processing_timeout_ms=5000,
                batch_size=100,
                parallel_processing=True
            ),
            ContentType.VIDEO: MatchingConfiguration(
                threshold=0.92,
                false_positive_rate=0.002,
                false_negative_rate=0.03,
                processing_timeout_ms=10000,
                batch_size=50,
                parallel_processing=True
            ),
            ContentType.IMAGE: MatchingConfiguration(
                threshold=0.96,
                false_positive_rate=0.001,
                false_negative_rate=0.015,
                processing_timeout_ms=3000,
                batch_size=200,
                parallel_processing=True
            ),
            ContentType.TEXT: MatchingConfiguration(
                threshold=0.98,
                false_positive_rate=0.0005,
                false_negative_rate=0.01,
                processing_timeout_ms=1000,
                batch_size=500,
                parallel_processing=True
            )
        }
        
        # Database Configurations
        self.databases = {
            "primary_fingerprint_db": DatabaseConfiguration(
                database_type=FingerprintDatabase.INTERNAL,
                connection_config={
                    "host": "localhost",
                    "port": 5432,
                    "database": "fingerprints",
                    "pool_size": 20,
                    "max_overflow": 50
                },
                backup_enabled=True,
                replication_factor=3,
                sharding_enabled=True,
                encryption_enabled=True
            ),
            
            "blockchain_registry": DatabaseConfiguration(
                database_type=FingerprintDatabase.BLOCKCHAIN,
                connection_config={
                    "network": "ethereum",
                    "contract_address": "0x...",
                    "gas_limit": 100000,
                    "confirmation_blocks": 6
                },
                backup_enabled=False,
                replication_factor=0,
                sharding_enabled=False,
                encryption_enabled=True
            ),
            
            "external_partner_db": DatabaseConfiguration(
                database_type=FingerprintDatabase.EXTERNAL_PARTNER,
                connection_config={
                    "api_endpoint": "https://partner-api.example.com",
                    "api_key": "${PARTNER_API_KEY}",
                    "rate_limit": 1000,
                    "timeout_seconds": 30
                },
                backup_enabled=False,
                replication_factor=0,
                sharding_enabled=False,
                encryption_enabled=True
            )
        }
        
        # Detection Performance Settings
        self.performance_settings = {
            "real_time_detection": True,
            "batch_processing_enabled": True,
            "max_concurrent_scans": 100,
            "scan_queue_priority": True,
            "result_caching_enabled": True,
            "cache_duration_hours": 168,  # 1 week
            "distributed_processing": True
        }
        
        # Content Monitoring Settings
        self.monitoring_settings = {
            "continuous_monitoring": True,
            "platform_integrations": [
                "youtube",
                "facebook",
                "instagram", 
                "tiktok",
                "twitter",
                "spotify",
                "soundcloud"
            ],
            "monitoring_frequency_hours": 6,
            "alert_threshold_matches": 1,
            "automated_takedown_enabled": False,  # Requires manual review
            "escalation_enabled": True
        }
        
        # Rights Management Integration
        self.rights_management = {
            "ownership_verification": True,
            "license_checking": True,
            "usage_tracking": True,
            "revenue_calculation": True,
            "automatic_attribution": True,
            "dispute_resolution": True
        }
        
        # API Configuration
        self.api_configuration = {
            "public_api_enabled": True,
            "rate_limiting": {
                "requests_per_minute": 100,
                "concurrent_requests": 10,
                "burst_allowance": 200
            },
            "authentication_required": True,
            "webhook_notifications": True,
            "batch_api_enabled": True,
            "streaming_api_enabled": True
        }
        
        # Security Settings
        self.security_settings = {
            "fingerprint_encryption": True,
            "secure_transmission": True,
            "access_logging": True,
            "audit_trail": True,
            "data_anonymization": True,
            "secure_key_management": True
        }
        
        # Compliance Settings
        self.compliance_settings = {
            "gdpr_compliance": True,
            "dmca_compliance": True,
            "international_copyright": True,
            "data_retention_days": 2555,  # 7 years
            "right_to_deletion": True,
            "consent_management": True
        }
        
        # Business Logic Settings
        self.business_logic = {
            "automated_claiming": False,  # Requires manual review
            "revenue_distribution": True,
            "license_negotiation": True,
            "fair_use_detection": True,
            "parody_detection": True,
            "educational_use_detection": True
        }
        
        # Quality Assurance
        self.quality_assurance = {
            "accuracy_monitoring": True,
            "false_positive_tracking": True,
            "algorithm_performance_testing": True,
            "continuous_improvement": True,
            "human_verification": True,
            "feedback_loop_enabled": True
        }
    
    def get_algorithm_config(self, algorithm_name: str) -> Optional[AlgorithmConfiguration]:
        """Get algorithm configuration by name"""
        return self.algorithms.get(algorithm_name)
    
    def get_matching_config(self, content_type: ContentType) -> Optional[MatchingConfiguration]:
        """Get matching configuration for content type"""
        return self.matching_configurations.get(content_type)
    
    def get_database_config(self, database_name: str) -> Optional[DatabaseConfiguration]:
        """Get database configuration by name"""
        return self.databases.get(database_name)
    
    def get_algorithms_for_content_type(self, content_type: ContentType) -> List[str]:
        """Get available algorithms for content type"""
        algorithms = []
        for alg_name, alg_config in self.algorithms.items():
            if content_type in alg_config.content_types:
                algorithms.append(alg_name)
        return algorithms
    
    def get_threshold_for_level(self, threshold_level: MatchingThreshold) -> float:
        """Get numeric threshold for threshold level"""
        threshold_mapping = {
            MatchingThreshold.STRICT: 0.98,
            MatchingThreshold.HIGH: 0.95,
            MatchingThreshold.MEDIUM: 0.90,
            MatchingThreshold.LOW: 0.80,
            MatchingThreshold.PERMISSIVE: 0.70
        }
        return threshold_mapping.get(threshold_level, 0.95)
    
    def is_algorithm_suitable(self, algorithm_name: str, content_type: ContentType, 
                             accuracy_requirement: float) -> bool:
        """Check if algorithm is suitable for requirements"""
        config = self.get_algorithm_config(algorithm_name)
        if not config:
            return False
        
        return (content_type in config.content_types and 
                config.accuracy >= accuracy_requirement)
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete fingerprinting configuration"""
        errors = []
        
        # Validate algorithms
        for alg_name, alg_config in self.algorithms.items():
            if alg_config.accuracy < 0.5 or alg_config.accuracy > 1.0:
                errors.append(f"Invalid accuracy for algorithm '{alg_name}'")
            if alg_config.processing_speed_ms <= 0:
                errors.append(f"Invalid processing speed for algorithm '{alg_name}'")
        
        # Validate matching configurations
        for content_type, match_config in self.matching_configurations.items():
            if match_config.threshold < 0.5 or match_config.threshold > 1.0:
                errors.append(f"Invalid threshold for content type '{content_type}'")
            if match_config.false_positive_rate >= 0.1:
                errors.append(f"High false positive rate for content type '{content_type}'")
        
        # Validate databases
        for db_name, db_config in self.databases.items():
            if not db_config.connection_config:
                errors.append(f"Missing connection config for database '{db_name}'")
        
        # Check for at least one algorithm per content type
        for content_type in ContentType:
            algorithms = self.get_algorithms_for_content_type(content_type)
            if not algorithms:
                errors.append(f"No algorithms configured for content type '{content_type}'")
        
        return errors


# Global copyright fingerprinting settings instance
copyright_fingerprinting_settings = CopyrightFingerprintingSettings()

__all__ = [
    "CopyrightFingerprintingSettings",
    "copyright_fingerprinting_settings",
    "FingerprintAlgorithm",
    "ContentType",
    "MatchingThreshold",
    "FingerprintDatabase",
    "AlgorithmConfiguration",
    "MatchingConfiguration",
    "DatabaseConfiguration"
]