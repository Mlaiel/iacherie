"""⚙️ IP Protection Service Configuration Management
================================================

Professional configuration management for the IP Protection Service
providing comprehensive settings and environment-specific configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import os
from pathlib import Path

@dataclass
class APIConfig:
    """Configuration for plagiarism detection API"""
    max_requests_per_minute: int = 1000
    similarity_threshold: float = 0.85
    confidence_threshold: float = 0.90
    batch_size: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl_minutes: int = 60
    ai_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db_settings: Dict[str, Any] = field(default_factory=lambda: {
        "index_type": "HNSW",
        "metric": "cosine",
        "ef_construction": 200,
        "m": 16
    })

@dataclass
class MonitoringConfig:
    """Configuration for unauthorized usage monitoring"""
    default_monitoring_frequency: int = 300  # seconds
    max_concurrent_sessions: int = 1000
    platforms_enabled: List[str] = field(default_factory=lambda: [
        "youtube", "tiktok", "instagram", "facebook", "twitter",
        "spotify", "soundcloud", "bandcamp", "twitch", "discord"
    ])
    violation_threshold: float = 0.80
    alert_threshold: float = 0.90
    evidence_retention_days: int = 2555  # 7 years
    enable_real_time_alerts: bool = True
    enable_dark_web_monitoring: bool = False
    rate_limiting: Dict[str, int] = field(default_factory=lambda: {
        "requests_per_minute": 100,
        "requests_per_hour": 5000,
        "requests_per_day": 100000
    })

@dataclass
class DMCAConfig:
    """Configuration for automated DMCA system"""
    auto_submission_enabled: bool = True
    auto_submission_threshold: float = 0.95
    supported_jurisdictions: List[str] = field(default_factory=lambda: [
        "US", "EU", "UK", "CA", "AU", "DE", "FR", "JP"
    ])
    template_directory: str = "templates/legal"
    compliance_check_enabled: bool = True
    minimum_compliance_score: float = 0.90
    escalation_enabled: bool = True
    escalation_threshold_hours: int = 24
    legal_contact_info: Dict[str, str] = field(default_factory=lambda: {
        "name": "Legal Department",
        "email": "legal@ainflue.com",
        "phone": "+1-555-0123",
        "address": "123 Legal Street, Legal City, LC 12345"
    })

@dataclass
class AnalyzerConfig:
    """Configuration for multi-format analyzer"""
    ai_models: Dict[str, str] = field(default_factory=lambda: {
        "text": "sentence-transformers/all-MiniLM-L6-v2",
        "image": "openai/clip-vit-base-patch32",
        "audio": "facebook/wav2vec2-base-960h",
        "video": "microsoft/videomae-base"
    })
    feature_extraction_settings: Dict[str, Any] = field(default_factory=lambda: {
        "audio": {
            "sample_rate": 22050,
            "n_mfcc": 13,
            "hop_length": 512,
            "n_fft": 2048
        },
        "image": {
            "resize_dimensions": (224, 224),
            "normalize": True,
            "color_histogram_bins": 256
        },
        "video": {
            "frame_sample_rate": 1,  # 1 frame per second
            "max_frames": 100,
            "resize_dimensions": (224, 224)
        },
        "text": {
            "max_sequence_length": 512,
            "tokenizer_model": "bert-base-uncased",
            "include_preprocessing": True
        }
    })
    processing_settings: Dict[str, Any] = field(default_factory=lambda: {
        "batch_processing": True,
        "gpu_acceleration": True,
        "max_workers": 4,
        "memory_limit_gb": 8
    })

@dataclass
class EnforcementConfig:
    """Configuration for rights enforcement engine"""
    enforcement_levels: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "standard": {
            "response_time_hours": 24,
            "escalation_enabled": False,
            "legal_action_threshold": 10
        },
        "urgent": {
            "response_time_hours": 4,
            "escalation_enabled": True,
            "legal_action_threshold": 5
        },
        "immediate": {
            "response_time_hours": 1,
            "escalation_enabled": True,
            "legal_action_threshold": 1
        }
    })
    platform_priorities: Dict[str, int] = field(default_factory=lambda: {
        "youtube": 1,
        "spotify": 1,
        "tiktok": 2,
        "instagram": 2,
        "facebook": 3,
        "twitter": 3
    })
    legal_action_settings: Dict[str, Any] = field(default_factory=lambda: {
        "enable_automated_legal_action": False,
        "require_manual_approval": True,
        "maximum_automated_value": 1000.0,
        "legal_counsel_contact": "counsel@ainflue.com"
    })

@dataclass
class RevenueConfig:
    """Configuration for revenue protection service"""
    revenue_tracking_enabled: bool = True
    impact_calculation_method: str = "predictive_model"
    currency: str = "USD"
    revenue_models: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "streaming": {
            "per_play_value": 0.003,
            "premium_multiplier": 2.0,
            "geographic_multiplier": 1.0
        },
        "download": {
            "per_download_value": 0.99,
            "bulk_discount": 0.1,
            "platform_fee": 0.3
        },
        "licensing": {
            "base_license_value": 100.0,
            "commercial_multiplier": 5.0,
            "exclusive_multiplier": 10.0
        }
    })
    protection_value_calculation: Dict[str, float] = field(default_factory=lambda: {
        "base_protection_value": 100.0,
        "similarity_score_multiplier": 2.0,
        "platform_reach_multiplier": 1.5,
        "time_sensitivity_factor": 0.1
    })

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    api_key_rotation_days: int = 90
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    audit_logging_enabled: bool = True
    audit_retention_days: int = 2555  # 7 years
    mfa_enabled: bool = True
    password_requirements: Dict[str, Any] = field(default_factory=lambda: {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": True
    })

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    primary_db_url: str = "postgresql://localhost:5432/ainflue"
    vector_db_url: str = "faiss://localhost:8000/vectors"
    cache_db_url: str = "redis://localhost:6379/0"
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    enable_query_logging: bool = False
    backup_enabled: bool = True
    backup_frequency_hours: int = 6
    replication_enabled: bool = True

@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    enable_caching: bool = True
    cache_ttl_minutes: int = 60
    max_concurrent_requests: int = 1000
    request_timeout_seconds: int = 30
    enable_compression: bool = True
    compression_level: int = 6
    enable_cdn: bool = True
    cdn_cache_duration: int = 3600
    load_balancing_enabled: bool = True
    auto_scaling_enabled: bool = True
    performance_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        "enable_metrics": True,
        "metrics_retention_days": 30,
        "alert_thresholds": {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0
        }
    })

class IPProtectionConfig:
    """Main configuration class for IP Protection Service"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration from dictionary or environment variables.
        
        Args:
            config_dict: Optional configuration dictionary
        """
        config = config_dict or {}
        
        # Load environment variables with fallbacks
        self.environment = os.getenv("AINFLUE_ENV", "development")
        self.debug = os.getenv("AINFLUE_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("AINFLUE_LOG_LEVEL", "INFO")
        
        # Initialize component configurations
        self.api_config = APIConfig(**config.get("api", {}))
        self.monitoring_config = MonitoringConfig(**config.get("monitoring", {}))
        self.dmca_config = DMCAConfig(**config.get("dmca", {}))
        self.analyzer_config = AnalyzerConfig(**config.get("analyzer", {}))
        self.enforcement_config = EnforcementConfig(**config.get("enforcement", {}))
        self.revenue_config = RevenueConfig(**config.get("revenue", {}))
        self.security_config = SecurityConfig(**config.get("security", {}))
        self.database_config = DatabaseConfig(**config.get("database", {}))
        self.performance_config = PerformanceConfig(**config.get("performance", {}))
        
        # Load environment-specific overrides
        self._load_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_environment_overrides(self) -> None:
        """Load environment-specific configuration overrides"""
        # Database URLs from environment
        if os.getenv("DATABASE_URL"):
            self.database_config.primary_db_url = os.getenv("DATABASE_URL")
        if os.getenv("VECTOR_DB_URL"):
            self.database_config.vector_db_url = os.getenv("VECTOR_DB_URL")
        if os.getenv("REDIS_URL"):
            self.database_config.cache_db_url = os.getenv("REDIS_URL")
        
        # API configuration from environment
        if os.getenv("API_RATE_LIMIT"):
            self.api_config.max_requests_per_minute = int(os.getenv("API_RATE_LIMIT"))
        if os.getenv("SIMILARITY_THRESHOLD"):
            self.api_config.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD"))
        
        # Security configuration from environment
        if os.getenv("ENCRYPTION_KEY"):
            self.security_config.encryption_enabled = True
        if os.getenv("MFA_ENABLED"):
            self.security_config.mfa_enabled = os.getenv("MFA_ENABLED").lower() == "true"
        
        # Performance settings for production
        if self.environment == "production":
            self.performance_config.enable_caching = True
            self.performance_config.enable_compression = True
            self.performance_config.enable_cdn = True
            self.security_config.audit_logging_enabled = True
            self.api_config.enable_caching = True
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings"""
        # Validate similarity thresholds
        if not 0.0 <= self.api_config.similarity_threshold <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.api_config.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        
        # Validate monitoring frequency
        if self.monitoring_config.default_monitoring_frequency < 60:
            raise ValueError("Monitoring frequency must be at least 60 seconds")
        
        # Validate DMCA compliance score
        if not 0.0 <= self.dmca_config.minimum_compliance_score <= 1.0:
            raise ValueError("DMCA compliance score must be between 0.0 and 1.0")
        
        # Validate database URLs
        required_schemes = {
            "primary_db_url": ["postgresql", "mysql"],
            "vector_db_url": ["faiss", "pinecone", "weaviate"],
            "cache_db_url": ["redis", "memcached"]
        }
        
        for url_attr, schemes in required_schemes.items():
            url = getattr(self.database_config, url_attr)
            if not any(url.startswith(f"{scheme}://") for scheme in schemes):
                raise ValueError(f"Invalid {url_attr}: must start with one of {schemes}")
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        platform_configs = {
            "youtube": {
                "api_rate_limit": 10000,
                "submission_method": "api",
                "compliance_requirements": ["dmca_agent", "copyright_owner"]
            },
            "tiktok": {
                "api_rate_limit": 1000,
                "submission_method": "web_form",
                "compliance_requirements": ["copyright_owner"]
            },
            "instagram": {
                "api_rate_limit": 5000,
                "submission_method": "web_form",
                "compliance_requirements": ["copyright_owner", "good_faith_belief"]
            },
            "spotify": {
                "api_rate_limit": 2000,
                "submission_method": "email",
                "compliance_requirements": ["copyright_owner", "dmca_agent"]
            }
        }
        
        return platform_configs.get(platform, {
            "api_rate_limit": 1000,
            "submission_method": "manual",
            "compliance_requirements": ["copyright_owner"]
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "api": self.api_config.__dict__,
            "monitoring": self.monitoring_config.__dict__,
            "dmca": self.dmca_config.__dict__,
            "analyzer": self.analyzer_config.__dict__,
            "enforcement": self.enforcement_config.__dict__,
            "revenue": self.revenue_config.__dict__,
            "security": self.security_config.__dict__,
            "database": self.database_config.__dict__,
            "performance": self.performance_config.__dict__
        }
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "IPProtectionConfig":
        """Load configuration from file"""
        import json
        import yaml
        
        config_path = Path(config_path)
        
        if config_path.suffix == ".json":
            with open(config_path, "r") as f:
                config_dict = json.load(f)
        elif config_path.suffix in [".yml", ".yaml"]:
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls(config_dict)

# Export configuration classes
__all__ = [
    "IPProtectionConfig",
    "APIConfig",
    "MonitoringConfig",
    "DMCAConfig", 
    "AnalyzerConfig",
    "EnforcementConfig",
    "RevenueConfig",
    "SecurityConfig",
    "DatabaseConfig",
    "PerformanceConfig"
]