"""Configuration Manager - Deployment Automation

Advanced configuration management system for the IA Influencer Agent platform,
handling environment-specific configurations, secrets management, and
dynamic configuration updates across deployment environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import yaml
import base64
import hashlib
from pathlib import Path
import jinja2

from ..core.base import BaseComponent
from ..security.encryption_manager import EncryptionManager
from ..kubernetes.config_map_manager import ConfigMapManager
from ..kubernetes.secret_manager import SecretManager
from ..cloud.parameter_store import ParameterStore
from ..vault.vault_manager import VaultManager


class ConfigType(Enum):
    """Configuration types"""    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    MONITORING = "monitoring"
    SECURITY = "security"
    AI_MODEL = "ai_model"
    API_GATEWAY = "api_gateway"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"


class SecretType(Enum):
    """Secret types"""    DATABASE_PASSWORD = "database_password"
    API_KEY = "api_key"
    JWT_SECRET = "jwt_secret"
    ENCRYPTION_KEY = "encryption_key"
    CERTIFICATE = "certificate"
    OAUTH_TOKEN = "oauth_token"
    WEBHOOK_SECRET = "webhook_secret"


@dataclass
class ConfigurationTemplate:
    """Configuration template definition"""    name: str
    config_type: ConfigType
    template_path: str
    variables: Dict[str, Any] = field(default_factory=dict)
    required_secrets: List[str] = field(default_factory=list)
    validation_schema: Optional[Dict[str, Any]] = None
    encryption_required: bool = False
    environment_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class SecretDefinition:
    """Secret definition"""    name: str
    secret_type: SecretType
    description: str
    required: bool = True
    auto_generate: bool = False
    rotation_interval: Optional[int] = None  # days
    environments: List[str] = field(default_factory=lambda: ["development", "staging", "production"])


class ConfigurationManager(BaseComponent):
    """    Enterprise-grade configuration management system.
    
    Manages application configurations, secrets, and environment-specific
    settings across multiple deployment environments with encryption,
    templating, and dynamic updates.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.encryption_manager = EncryptionManager(config.get('encryption', {}))
        self.config_map_manager = ConfigMapManager(config.get('configmaps', {}))
        self.secret_manager = SecretManager(config.get('secrets', {}))
        self.parameter_store = ParameterStore(config.get('parameter_store', {}))
        self.vault_manager = VaultManager(config.get('vault', {}))
        
        # Template engine
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(config.get('template_path', 'templates')),
            autoescape=True
        )
        
        # Configuration state
        self.active_configurations: Dict[str, Dict[str, Any]] = {}
        self.secret_cache: Dict[str, Dict[str, Any]] = {}
        
        # Configuration templates
        self.configuration_templates = self._load_configuration_templates()
        self.secret_definitions = self._load_secret_definitions()

    def _load_configuration_templates(self) -> Dict[str, ConfigurationTemplate]:
        """Load configuration templates"""        templates = {}
        
        # Content Protection Configuration Template
        templates['content_protection'] = ConfigurationTemplate(
            name="content_protection_config",
            config_type=ConfigType.CONTENT_PROTECTION,
            template_path="content_protection/config.yaml.j2",
            variables={
                "fingerprinting_engines": {
                    "audio": {
                        "chromaprint_quality": "high",
                        "spectral_analysis_window": 2048,
                        "fingerprint_duration": 30,
                        "similarity_threshold": 0.85
                    },
                    "video": {
                        "frame_sampling_rate": 1.0,
                        "perceptual_hash_size": 64,
                        "motion_vectors_analysis": True,
                        "scene_detection_threshold": 0.3
                    },
                    "image": {
                        "hash_algorithms": ["phash", "dhash", "whash"],
                        "clip_model": "ViT-L/14",
                        "feature_extraction_layers": ["conv4", "conv5"],
                        "similarity_threshold": 0.92
                    },
                    "text": {
                        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                        "chunk_size": 512,
                        "overlap_ratio": 0.1,
                        "plagiarism_threshold": 0.75
                    }
                },
                "vector_database": {
                    "faiss_index_type": "IndexHNSWFlat",
                    "dimension": 768,
                    "ef_construction": 200,
                    "m_links": 16,
                    "batch_size": 1000
                },
                "crawling_engines": {
                    "youtube": {
                        "api_quota_per_day": 10000,
                        "search_depth": 100,
                        "video_quality_check": True,
                        "metadata_extraction": True
                    },
                    "instagram": {
                        "posts_per_scan": 500,
                        "story_monitoring": True,
                        "reels_analysis": True,
                        "hashtag_tracking": True
                    },
                    "tiktok": {
                        "trending_analysis": True,
                        "sound_matching": True,
                        "effect_detection": True,
                        "duet_original_tracking": True
                    },
                    "twitter": {
                        "tweet_monitoring": True,
                        "media_analysis": True,
                        "thread_tracking": True,
                        "real_time_streaming": True
                    }
                }
            },
            required_secrets=[
                "youtube_api_key", "instagram_api_token", "tiktok_api_key",
                "twitter_api_token", "faiss_storage_bucket", "vector_db_password"
            ],
            dependencies=["ai_agent", "database"]
        )

        # Monetization Configuration Template
        templates['monetization'] = ConfigurationTemplate(
            name="monetization_config",
            config_type=ConfigType.MONETIZATION,
            template_path="monetization/config.yaml.j2",
            variables={
                "revenue_tracking": {
                    "platforms": {
                        "spotify": {
                            "api_version": "v1",
                            "data_refresh_interval": 3600,
                            "metrics": ["streams", "followers", "monthly_listeners", "royalties"]
                        },
                        "youtube": {
                            "analytics_api": "v2",
                            "creator_studio_integration": True,
                            "metrics": ["views", "watch_time", "subscribers", "ad_revenue", "super_chat"]
                        },
                        "instagram": {
                            "creator_api": True,
                            "insights_depth": "detailed",
                            "metrics": ["reach", "impressions", "engagement", "branded_content_revenue"]
                        },
                        "tiktok": {
                            "creator_fund_api": True,
                            "live_gifts_tracking": True,
                            "metrics": ["views", "likes", "shares", "creator_fund_earnings"]
                        }
                    }
                },
                "payment_processing": {
                    "stripe": {
                        "webhook_timeout": 30,
                        "payout_schedule": "weekly",
                        "fee_structure": "platform_fee",
                        "supported_currencies": ["USD", "EUR", "GBP", "CAD"]
                    },
                    "wise": {
                        "international_transfers": True,
                        "multi_currency_support": True,
                        "fee_optimization": True
                    },
                    "paypal": {
                        "mass_payments": True,
                        "currency_conversion": True,
                        "dispute_handling": True
                    }
                },
                "licensing_engine": {
                    "automated_licensing": True,
                    "license_templates": ["standard", "premium", "exclusive"],
                    "pricing_models": ["fixed", "percentage", "hybrid"],
                    "contract_generation": True,
                    "digital_signatures": True
                },
                "collaboration_matching": {
                    "ai_matching_algorithm": "advanced_neural_network",
                    "compatibility_scoring": True,
                    "genre_matching": True,
                    "audience_overlap_analysis": True,
                    "success_prediction": True
                }
            },
            required_secrets=[
                "stripe_api_key", "stripe_webhook_secret", "wise_api_key", 
                "paypal_client_id", "paypal_client_secret", "platform_apis_bundle"
            ],
            dependencies=["ai_agent", "content_protection"]
        )

        # Audio Processing Configuration Template
        templates['audio_processing'] = ConfigurationTemplate(
            name="audio_processing_config",
            config_type=ConfigType.AI_MODEL,
            template_path="audio/config.yaml.j2",
            variables={
                "audio_analysis": {
                    "sample_rate": 44100,
                    "bit_depth": 24,
                    "supported_formats": ["wav", "flac", "mp3", "aac", "ogg"],
                    "spectral_analysis": {
                        "fft_size": 2048,
                        "hop_length": 512,
                        "window": "hann",
                        "mel_bands": 128
                    },
                    "feature_extraction": {
                        "mfcc": True,
                        "chroma": True,
                        "spectral_contrast": True,
                        "tonnetz": True,
                        "zero_crossing_rate": True,
                        "tempo": True,
                        "beat_tracking": True
                    }
                },
                "genre_classification": {
                    "model_type": "ensemble_cnn_lstm",
                    "confidence_threshold": 0.8,
                    "supported_genres": [
                        "pop", "rock", "hip-hop", "electronic", "classical",
                        "jazz", "blues", "reggae", "country", "folk"
                    ]
                },
                "mood_detection": {
                    "valence_arousal_model": True,
                    "emotion_categories": [
                        "happy", "sad", "energetic", "calm", "aggressive",
                        "romantic", "melancholic", "euphoric"
                    ]
                },
                "music_generation": {
                    "model_architecture": "transformer_xl",
                    "max_sequence_length": 2048,
                    "temperature": 0.8,
                    "top_k": 40,
                    "style_transfer": True
                }
            },
            required_secrets=[
                "audio_models_bucket", "music_generation_api_key",
                "spotify_web_api_key", "audio_processing_gpu_cluster"
            ],
            dependencies=["ai_agent"]
        )
            environment_overrides={
                "development": {
                    "log_level": "debug",
                    "max_concurrent_requests": 10,
                    "gpu_memory_fraction": 0.5
                },
                "staging": {
                    "log_level": "info",
                    "max_concurrent_requests": 50,
                    "gpu_memory_fraction": 0.7
                },
                "production": {
                    "log_level": "warning",
                    "max_concurrent_requests": 200,
                    "gpu_memory_fraction": 0.9
                }
            }
        )
        
        # Content Protection Configuration Template
        templates['content_protection'] = ConfigurationTemplate(
            name="content_protection_config",
            config_type=ConfigType.CONTENT_PROTECTION,
            template_path="content_protection/config.yaml.j2",
            variables={
                "fingerprinting_engines": {
                    "audio": {
                        "engine": "chromaprint",
                        "sample_rate": 22050,
                        "quality": "high",
                        "chunk_size": 30
                    },
                    "video": {
                        "engine": "opencv",
                        "frame_rate": 1,
                        "quality": "medium",
                        "hash_algorithm": "phash"
                    },
                    "image": {
                        "engine": "clip",
                        "resolution": "512x512",
                        "quality": "high",
                        "feature_extraction": "deep"
                    },
                    "text": {
                        "engine": "bert",
                        "model": "bert-large-uncased",
                        "max_length": 512,
                        "similarity_threshold": 0.85
                    }
                },
                "vector_database": {
                    "engine": "faiss",
                    "index_type": "IVF",
                    "nlist": 1000,
                    "nprobe": 10,
                    "similarity_metric": "cosine"
                },
                "processing_config": {
                    "batch_size": 32,
                    "max_file_size": "100MB",
                    "supported_formats": {
                        "audio": ["mp3", "wav", "flac", "aac"],
                        "video": ["mp4", "avi", "mov", "mkv"],
                        "image": ["jpg", "png", "gif", "webp"],
                        "text": ["txt", "doc", "pdf", "md"]
                    }
                }
            },
            required_secrets=["vector_db_url", "storage_access_key", "processing_queue_url"],
            environment_overrides={
                "development": {
                    "fingerprinting_engines.audio.quality": "medium",
                    "fingerprinting_engines.video.quality": "low",
                    "processing_config.batch_size": 8
                },
                "production": {
                    "fingerprinting_engines.audio.quality": "ultra",
                    "fingerprinting_engines.video.quality": "high",
                    "processing_config.batch_size": 64
                }
            }
        )
        
        # Monetization Configuration Template
        templates['monetization'] = ConfigurationTemplate(
            name="monetization_config",
            config_type=ConfigType.MONETIZATION,
            template_path="monetization/config.yaml.j2",
            variables={
                "payment_processors": {
                    "stripe": {
                        "enabled": True,
                        "webhook_tolerance": 300,
                        "retry_attempts": 3
                    },
                    "paypal": {
                        "enabled": True,
                        "sandbox": False
                    },
                    "wise": {
                        "enabled": True,
                        "currency": "USD"
                    }
                },
                "blockchain_config": {
                    "ethereum": {
                        "network": "mainnet",
                        "gas_limit": 21000,
                        "gas_price": "auto"
                    },
                    "polygon": {
                        "network": "mainnet",
                        "gas_limit": 21000
                    }
                },
                "revenue_sharing": {
                    "platform_fee": 0.05,
                    "processing_fee": 0.029,
                    "creator_percentage": 0.921,
                    "minimum_payout": 10.0
                },
                "analytics_config": {
                    "tracking_enabled": True,
                    "metrics_retention": 365,
                    "reporting_frequency": "daily"
                }
            },
            required_secrets=[
                "stripe_secret_key", "stripe_webhook_secret",
                "paypal_client_secret", "wise_api_key",
                "ethereum_private_key", "polygon_private_key"
            ],
            environment_overrides={
                "development": {
                    "payment_processors.stripe.enabled": False,
                    "payment_processors.paypal.sandbox": True,
                    "blockchain_config.ethereum.network": "sepolia"
                },
                "staging": {
                    "payment_processors.paypal.sandbox": True,
                    "blockchain_config.ethereum.network": "sepolia"
                }
            }
        )
        
        # Crawler Configuration Template
        templates['crawler'] = ConfigurationTemplate(
            name="crawler_config",
            config_type=ConfigType.APPLICATION,
            template_path="crawler/config.yaml.j2",
            variables={
                "crawling_targets": {
                    "youtube": {
                        "enabled": True,
                        "rate_limit": 1000,
                        "concurrent_requests": 10,
                        "retry_delay": 60
                    },
                    "tiktok": {
                        "enabled": True,
                        "rate_limit": 500,
                        "concurrent_requests": 5,
                        "retry_delay": 120
                    },
                    "instagram": {
                        "enabled": True,
                        "rate_limit": 200,
                        "concurrent_requests": 3,
                        "retry_delay": 180
                    },
                    "twitter": {
                        "enabled": True,
                        "rate_limit": 300,
                        "concurrent_requests": 5,
                        "retry_delay": 60
                    }
                },
                "user_agent_rotation": {
                    "enabled": True,
                    "rotation_interval": 100,
                    "user_agents": [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                    ]
                },
                "proxy_config": {
                    "enabled": True,
                    "rotation_enabled": True,
                    "timeout": 30
                },
                "storage_config": {
                    "cache_duration": 3600,
                    "max_cache_size": "50Gi",
                    "compression": True
                }
            },
            required_secrets=[
                "youtube_api_key", "tiktok_api_key", "instagram_api_key",
                "twitter_api_key", "proxy_credentials"
            ],
            environment_overrides={
                "development": {
                    "crawling_targets.youtube.rate_limit": 100,
                    "crawling_targets.tiktok.rate_limit": 50,
                    "storage_config.max_cache_size": "5Gi"
                }
            }
        )
        
        # API Gateway Configuration Template
        templates['api_gateway'] = ConfigurationTemplate(
            name="api_gateway_config",
            config_type=ConfigType.API_GATEWAY,
            template_path="api_gateway/config.yaml.j2",
            variables={
                "rate_limiting": {
                    "enabled": True,
                    "default_rate": "1000/hour",
                    "burst_size": 100,
                    "premium_rate": "10000/hour"
                },
                "cors_config": {
                    "enabled": True,
                    "allowed_origins": ["*"],
                    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                    "allowed_headers": ["*"],
                    "max_age": 3600
                },
                "authentication": {
                    "jwt_enabled": True,
                    "oauth2_enabled": True,
                    "api_key_enabled": True,
                    "session_timeout": 3600
                },
                "service_discovery": {
                    "enabled": True,
                    "health_check_interval": 30,
                    "failure_threshold": 3
                },
                "load_balancing": {
                    "algorithm": "round_robin",
                    "health_check": True,
                    "circuit_breaker": True
                },
                "logging": {
                    "access_logs": True,
                    "error_logs": True,
                    "debug_logs": False,
                    "log_format": "json"
                }
            },
            required_secrets=["jwt_secret", "oauth2_client_secret", "tls_certificate"],
            environment_overrides={
                "development": {
                    "rate_limiting.default_rate": "100/hour",
                    "logging.debug_logs": True
                },
                "production": {
                    "cors_config.allowed_origins": ["https://app.ia-influencer.com"],
                    "rate_limiting.default_rate": "5000/hour"
                }
            }
        )
        
        # Database Configuration Template
        templates['database'] = ConfigurationTemplate(
            name="database_config",
            config_type=ConfigType.DATABASE,
            template_path="database/config.yaml.j2",
            variables={
                "postgresql": {
                    "max_connections": 100,
                    "shared_buffers": "256MB",
                    "effective_cache_size": "1GB",
                    "work_mem": "4MB",
                    "maintenance_work_mem": "64MB",
                    "checkpoint_completion_target": 0.9,
                    "wal_buffers": "16MB",
                    "default_statistics_target": 100
                },
                "connection_pooling": {
                    "enabled": True,
                    "pool_size": 20,
                    "max_overflow": 30,
                    "pool_timeout": 30,
                    "pool_recycle": 3600
                },
                "backup_config": {
                    "enabled": True,
                    "schedule": "0 2 * * *",  # Daily at 2 AM
                    "retention_days": 30,
                    "compression": True
                },
                "monitoring": {
                    "slow_query_log": True,
                    "slow_query_time": 1.0,
                    "log_connections": True,
                    "log_disconnections": True
                }
            },
            required_secrets=["database_password", "backup_encryption_key"],
            environment_overrides={
                "development": {
                    "postgresql.max_connections": 20,
                    "connection_pooling.pool_size": 5,
                    "backup_config.retention_days": 7
                },
                "production": {
                    "postgresql.max_connections": 200,
                    "postgresql.shared_buffers": "1GB",
                    "postgresql.effective_cache_size": "4GB",
                    "connection_pooling.pool_size": 50,
                    "backup_config.retention_days": 90
                }
            }
        )
        
        return templates

    def _load_secret_definitions(self) -> Dict[str, SecretDefinition]:
        """Load secret definitions"""        secrets = {}
        
        # Database secrets
        secrets['database_url'] = SecretDefinition(
            name="database_url",
            secret_type=SecretType.DATABASE_PASSWORD,
            description="Database connection URL with credentials",
            rotation_interval=90
        )
        
        secrets['database_password'] = SecretDefinition(
            name="database_password",
            secret_type=SecretType.DATABASE_PASSWORD,
            description="Database user password",
            auto_generate=True,
            rotation_interval=90
        )
        
        # API Keys
        secrets['openai_api_key'] = SecretDefinition(
            name="openai_api_key",
            secret_type=SecretType.API_KEY,
            description="OpenAI API key for AI services"
        )
        
        secrets['youtube_api_key'] = SecretDefinition(
            name="youtube_api_key",
            secret_type=SecretType.API_KEY,
            description="YouTube Data API key"
        )
        
        secrets['stripe_secret_key'] = SecretDefinition(
            name="stripe_secret_key",
            secret_type=SecretType.API_KEY,
            description="Stripe payment processor secret key"
        )
        
        # JWT and authentication
        secrets['jwt_secret'] = SecretDefinition(
            name="jwt_secret",
            secret_type=SecretType.JWT_SECRET,
            description="JWT signing secret",
            auto_generate=True,
            rotation_interval=30
        )
        
        secrets['oauth2_client_secret'] = SecretDefinition(
            name="oauth2_client_secret",
            secret_type=SecretType.OAUTH_TOKEN,
            description="OAuth2 client secret for third-party integrations"
        )
        
        # Encryption keys
        secrets['content_encryption_key'] = SecretDefinition(
            name="content_encryption_key",
            secret_type=SecretType.ENCRYPTION_KEY,
            description="Encryption key for content protection",
            auto_generate=True,
            rotation_interval=30
        )
        
        secrets['backup_encryption_key'] = SecretDefinition(
            name="backup_encryption_key",
            secret_type=SecretType.ENCRYPTION_KEY,
            description="Encryption key for backup data",
            auto_generate=True,
            rotation_interval=90
        )
        
        # Certificates
        secrets['tls_certificate'] = SecretDefinition(
            name="tls_certificate",
            secret_type=SecretType.CERTIFICATE,
            description="TLS certificate for HTTPS endpoints",
            rotation_interval=365
        )
        
        # Webhook secrets
        secrets['stripe_webhook_secret'] = SecretDefinition(
            name="stripe_webhook_secret",
            secret_type=SecretType.WEBHOOK_SECRET,
            description="Stripe webhook endpoint secret"
        )
        
        return secrets

    async def prepare_configurations(
        self,
        environment: str,
        services: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Prepare configurations for all services in the environment.
        
        Args:
            environment: Target environment
            services: List of services to configure
            context: Configuration context
            
        Returns:
            Configuration preparation results
        """        self.logger.info(f"Preparing configurations for {len(services)} services in {environment}")
        
        preparation_results = {
            'environment': environment,
            'services': services,
            'configs_created': {},
            'secrets_created': {},
            'errors': []
        }
        
        try:
            # Prepare namespace
            namespace = context.get('namespace', f"ia-influencer-{environment}")
            
            # Ensure required secrets exist
            await self._ensure_secrets_exist(environment, services, context)
            
            # Generate configurations for each service
            for service_name in services:
                if service_name in self.configuration_templates:
                    config_result = await self._generate_service_configuration(
                        service_name, environment, namespace, context
                    )
                    preparation_results['configs_created'][service_name] = config_result
                else:
                    self.logger.warning(f"No configuration template found for service: {service_name}")
            
            # Create Kubernetes ConfigMaps and Secrets
            k8s_results = await self._create_kubernetes_resources(
                environment, namespace, preparation_results['configs_created'], context
            )
            preparation_results['kubernetes_resources'] = k8s_results
            
        except Exception as e:
            self.logger.error(f"Configuration preparation failed: {str(e)}", exc_info=True)
            preparation_results['errors'].append(str(e))
            raise
        
        return preparation_results

    async def _ensure_secrets_exist(
        self,
        environment: str,
        services: List[str],
        context: Dict[str, Any]
    ) -> None:
        """Ensure all required secrets exist for the services"""        
        required_secrets = set()
        
        # Collect all required secrets
        for service_name in services:
            if service_name in self.configuration_templates:
                template = self.configuration_templates[service_name]
                required_secrets.update(template.required_secrets)
        
        # Check and create missing secrets
        for secret_name in required_secrets:
            if secret_name in self.secret_definitions:
                secret_def = self.secret_definitions[secret_name]
                
                # Check if secret exists
                secret_exists = await self._check_secret_exists(secret_name, environment)
                
                if not secret_exists:
                    if secret_def.auto_generate:
                        # Generate secret automatically
                        secret_value = await self._generate_secret_value(secret_def)
                    else:
                        # Use provided value or raise error
                        secret_value = context.get('secrets', {}).get(secret_name)
                        if not secret_value:
                            raise ValueError(f"Required secret not provided: {secret_name}")
                    
                    # Store secret
                    await self._store_secret(secret_name, secret_value, environment, secret_def)

    async def _generate_service_configuration(
        self,
        service_name: str,
        environment: str,
        namespace: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate configuration for a specific service"""        
        template = self.configuration_templates[service_name]
        
        # Start with base template variables
        config_vars = template.variables.copy()
        
        # Apply environment-specific overrides
        if environment in template.environment_overrides:
            overrides = template.environment_overrides[environment]
            config_vars = self._deep_merge_dicts(config_vars, overrides)
        
        # Apply context overrides
        if 'config_overrides' in context and service_name in context['config_overrides']:
            service_overrides = context['config_overrides'][service_name]
            config_vars = self._deep_merge_dicts(config_vars, service_overrides)
        
        # Add environment metadata
        config_vars.update({
            'environment': environment,
            'namespace': namespace,
            'service_name': service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_id': context.get('deployment_id', 'unknown')
        })
        
        # Render template
        try:
            template_obj = self.template_env.get_template(template.template_path)
            rendered_config = template_obj.render(**config_vars)
            
            # Parse rendered configuration
            if template.template_path.endswith('.yaml.j2'):
                config_data = yaml.safe_load(rendered_config)
            elif template.template_path.endswith('.json.j2'):
                config_data = json.loads(rendered_config)
            else:
                config_data = rendered_config
            
            # Validate configuration if schema provided
            if template.validation_schema:
                await self._validate_configuration(config_data, template.validation_schema)
            
            # Encrypt sensitive data if required
            if template.encryption_required:
                config_data = await self._encrypt_sensitive_data(config_data)
            
            return {
                'config_data': config_data,
                'template_used': template.template_path,
                'variables_applied': config_vars,
                'size': len(json.dumps(config_data)),
                'checksum': hashlib.md5(json.dumps(config_data, sort_keys=True).encode()).hexdigest()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate configuration for {service_name}: {str(e)}")
            raise

    async def _create_kubernetes_resources(
        self,
        environment: str,
        namespace: str,
        service_configs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create Kubernetes ConfigMaps and Secrets"""        
        results = {
            'configmaps': {},
            'secrets': {},
            'errors': []
        }
        
        # Create ConfigMaps for each service
        for service_name, config_result in service_configs.items():
            try:
                configmap_name = f"{service_name}-config"
                
                configmap_result = await self.config_map_manager.create_or_update_configmap(
                    name=configmap_name,
                    namespace=namespace,
                    data={
                        'config.yaml': yaml.dump(config_result['config_data']),
                        'metadata.json': json.dumps({
                            'template_used': config_result['template_used'],
                            'checksum': config_result['checksum'],
                            'created_at': datetime.utcnow().isoformat(),
                            'environment': environment
                        })
                    },
                    labels={
                        'app': service_name,
                        'environment': environment,
                        'managed-by': 'ia-influencer-config-manager'
                    }
                )
                
                results['configmaps'][service_name] = configmap_result
                
            except Exception as e:
                error_msg = f"Failed to create ConfigMap for {service_name}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Create Secrets
        try:
            secret_data = {}
            
            # Collect secrets for all services
            for service_name in service_configs.keys():
                if service_name in self.configuration_templates:
                    template = self.configuration_templates[service_name]
                    for secret_name in template.required_secrets:
                        secret_value = await self._retrieve_secret(secret_name, environment)
                        if secret_value:
                            secret_data[secret_name] = base64.b64encode(secret_value.encode()).decode()
            
            if secret_data:
                secret_result = await self.secret_manager.create_or_update_secret(
                    name=f"ia-influencer-secrets",
                    namespace=namespace,
                    data=secret_data,
                    secret_type="Opaque",
                    labels={
                        'environment': environment,
                        'managed-by': 'ia-influencer-config-manager'
                    }
                )
                
                results['secrets']['ia-influencer-secrets'] = secret_result
                
        except Exception as e:
            error_msg = f"Failed to create secrets: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

    async def _check_secret_exists(self, secret_name: str, environment: str) -> bool:
        """Check if a secret exists in the environment"""        
        # Check in Vault first
        vault_exists = await self.vault_manager.secret_exists(
            f"ia-influencer/{environment}/{secret_name}"
        )
        
        if vault_exists:
            return True
        
        # Check in cloud parameter store
        param_exists = await self.parameter_store.parameter_exists(
            f"/ia-influencer/{environment}/{secret_name}"
        )
        
        return param_exists

    async def _generate_secret_value(self, secret_def: SecretDefinition) -> str:
        """Generate a secret value based on secret type"""        
        if secret_def.secret_type == SecretType.DATABASE_PASSWORD:
            return self._generate_secure_password(32)
        elif secret_def.secret_type == SecretType.JWT_SECRET:
            return self._generate_jwt_secret()
        elif secret_def.secret_type == SecretType.ENCRYPTION_KEY:
            return self._generate_encryption_key()
        elif secret_def.secret_type == SecretType.API_KEY:
            return self._generate_api_key()
        elif secret_def.secret_type == SecretType.WEBHOOK_SECRET:
            return self._generate_webhook_secret()
        else:
            return self._generate_secure_password(64)

    async def _store_secret(
        self,
        secret_name: str,
        secret_value: str,
        environment: str,
        secret_def: SecretDefinition
    ) -> None:
        """Store secret in secure storage"""        
        # Encrypt secret value
        encrypted_value = await self.encryption_manager.encrypt(secret_value)
        
        # Store in Vault
        await self.vault_manager.store_secret(
            path=f"ia-influencer/{environment}/{secret_name}",
            secret_data={
                'value': encrypted_value,
                'type': secret_def.secret_type.value,
                'description': secret_def.description,
                'created_at': datetime.utcnow().isoformat(),
                'rotation_interval': secret_def.rotation_interval,
                'auto_generated': secret_def.auto_generate
            }
        )
        
        # Also store in cloud parameter store for redundancy
        await self.parameter_store.put_parameter(
            name=f"/ia-influencer/{environment}/{secret_name}",
            value=encrypted_value,
            parameter_type="SecureString",
            description=secret_def.description,
            tags={
                'Environment': environment,
                'SecretType': secret_def.secret_type.value,
                'ManagedBy': 'ia-influencer-config-manager'
            }
        )

    async def _retrieve_secret(self, secret_name: str, environment: str) -> Optional[str]:
        """Retrieve and decrypt secret value"""        
        # Check cache first
        cache_key = f"{environment}:{secret_name}"
        if cache_key in self.secret_cache:
            return self.secret_cache[cache_key]['value']
        
        # Retrieve from Vault
        try:
            secret_data = await self.vault_manager.get_secret(
                f"ia-influencer/{environment}/{secret_name}"
            )
            
            if secret_data:
                encrypted_value = secret_data['value']
                decrypted_value = await self.encryption_manager.decrypt(encrypted_value)
                
                # Cache with TTL
                self.secret_cache[cache_key] = {
                    'value': decrypted_value,
                    'cached_at': datetime.utcnow(),
                    'ttl': 300  # 5 minutes
                }
                
                return decrypted_value
                
        except Exception as e:
            self.logger.warning(f"Failed to retrieve secret from Vault: {secret_name}", exc_info=True)
        
        # Fallback to parameter store
        try:
            parameter = await self.parameter_store.get_parameter(
                f"/ia-influencer/{environment}/{secret_name}",
                with_decryption=True
            )
            
            if parameter:
                encrypted_value = parameter['Value']
                decrypted_value = await self.encryption_manager.decrypt(encrypted_value)
                
                # Cache with TTL
                self.secret_cache[cache_key] = {
                    'value': decrypted_value,
                    'cached_at': datetime.utcnow(),
                    'ttl': 300
                }
                
                return decrypted_value
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret: {secret_name}", exc_info=True)
        
        return None

    def _deep_merge_dicts(self, base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""        result = base.copy()
        
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result

    async def _validate_configuration(
        self,
        config_data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> None:
        """Validate configuration against schema"""        
        # Implement schema validation logic
        # This could use jsonschema library for validation
        pass

    async def _encrypt_sensitive_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration data"""        
        # Identify and encrypt sensitive fields
        # This would implement field-level encryption for sensitive data
        return config_data

    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password"""        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret"""        import secrets
        return secrets.token_urlsafe(64)

    def _generate_encryption_key(self) -> str:
        """Generate encryption key"""        import secrets
        return secrets.token_hex(32)

    def _generate_api_key(self) -> str:
        """Generate API key"""        import secrets
        return f"ia_influencer_{secrets.token_urlsafe(48)}"

    def _generate_webhook_secret(self) -> str:
        """Generate webhook secret"""        import secrets
        return secrets.token_hex(32)

    async def update_configuration(
        self,
        service_name: str,
        environment: str,
        updates: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update service configuration"""        
        target_namespace = namespace or f"ia-influencer-{environment}"
        
        # Get current configuration
        current_config = await self.config_map_manager.get_configmap(
            f"{service_name}-config", target_namespace
        )
        
        if not current_config:
            raise ValueError(f"Configuration not found for service: {service_name}")
        
        # Apply updates
        config_data = yaml.safe_load(current_config['data']['config.yaml'])
        updated_config = self._deep_merge_dicts(config_data, updates)
        
        # Update ConfigMap
        update_result = await self.config_map_manager.create_or_update_configmap(
            name=f"{service_name}-config",
            namespace=target_namespace,
            data={
                'config.yaml': yaml.dump(updated_config),
                'metadata.json': json.dumps({
                    'updated_at': datetime.utcnow().isoformat(),
                    'environment': environment,
                    'update_source': 'configuration_manager'
                })
            },
            labels={
                'app': service_name,
                'environment': environment,
                'managed-by': 'ia-influencer-config-manager'
            }
        )
        
        return update_result

    async def rotate_secrets(self, environment: str, secret_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Rotate secrets for the environment"""        
        if secret_names is None:
            # Rotate all auto-rotatable secrets
            secret_names = [
                name for name, definition in self.secret_definitions.items()
                if definition.auto_generate and definition.rotation_interval
            ]
        
        rotation_results = {}
        
        for secret_name in secret_names:
            if secret_name not in self.secret_definitions:
                continue
            
            secret_def = self.secret_definitions[secret_name]
            
            try:
                # Generate new secret value
                new_value = await self._generate_secret_value(secret_def)
                
                # Store new secret
                await self._store_secret(secret_name, new_value, environment, secret_def)
                
                # Clear cache
                cache_key = f"{environment}:{secret_name}"
                if cache_key in self.secret_cache:
                    del self.secret_cache[cache_key]
                
                rotation_results[secret_name] = {
                    'status': 'success',
                    'rotated_at': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Failed to rotate secret {secret_name}: {str(e)}")
                rotation_results[secret_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return rotation_results

    async def cleanup_cache(self) -> int:
        """Cleanup expired cache entries"""        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, cached_data in self.secret_cache.items():
            cached_at = cached_data['cached_at']
            ttl = cached_data['ttl']
            
            if (current_time - cached_at).total_seconds() > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.secret_cache[key]
        
        return len(expired_keys)
