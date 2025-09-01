"""🔗 External Integrations Configuration Manager - IA-Influencer-Agent
==================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentante de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade external integrations configuration for unified platform management.
==================================================================
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml
import os
from pathlib import Path
import requests
from urllib.parse import urlparse

# Initialize logger
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Types of external integrations"""
    SOCIAL_PLATFORM = "social_platform"
    STREAMING_SERVICE = "streaming_service"
    PAYMENT_GATEWAY = "payment_gateway"
    CLOUD_STORAGE = "cloud_storage"
    CDN_SERVICE = "cdn_service"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    ANALYTICS_SERVICE = "analytics_service"
    LEGAL_SERVICE = "legal_service"
    AI_SERVICE = "ai_service"
    BLOCKCHAIN_SERVICE = "blockchain_service"
    MONITORING_SERVICE = "monitoring_service"

class AuthenticationMethod(Enum):
    """Authentication methods for integrations"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM_HEADER = "custom_header"
    WEBHOOK_SECRET = "webhook_secret"
    CERTIFICATE = "certificate"

class IntegrationStatus(Enum):
    """Integration connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CONNECTING = "connecting"
    ERROR = "error"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"

@dataclass
class PlatformIntegrationConfig:
    """Configuration for platform integrations"""
    platform_name: str
    integration_type: IntegrationType
    enabled: bool = True
    
    # Authentication
    auth_method: AuthenticationMethod = AuthenticationMethod.API_KEY
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # API Configuration
    api_base_url: Optional[str] = None
    api_version: str = "v1"
    api_timeout_seconds: int = 30
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Feature support
    upload_support: bool = False
    download_support: bool = False
    analytics_support: bool = False
    monetization_support: bool = False
    live_streaming_support: bool = False
    
    # Content format support
    supported_audio_formats: List[str] = field(default_factory=list)
    supported_video_formats: List[str] = field(default_factory=list)
    supported_image_formats: List[str] = field(default_factory=list)
    
    # Quality and performance
    max_file_size_mb: int = 100
    max_resolution: str = "1920x1080"
    compression_enabled: bool = True
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    webhook_events: List[str] = field(default_factory=list)
    
    # Retry and error handling
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    exponential_backoff: bool = True
    error_notification: bool = True
    
    # Monitoring
    health_check_url: Optional[str] = None
    health_check_interval_minutes: int = 5
    performance_monitoring: bool = True
    
    # Custom headers and parameters
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StreamingPlatformsConfig:
    """Configuration for streaming platforms"""
    # Music streaming platforms
    spotify: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Spotify",
        integration_type=IntegrationType.STREAMING_SERVICE,
        api_base_url="https://api.spotify.com/v1",
        auth_method=AuthenticationMethod.OAUTH2,
        supported_audio_formats=["mp3", "ogg", "flac"],
        analytics_support=True,
        monetization_support=True
    ))
    
    apple_music: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Apple Music",
        integration_type=IntegrationType.STREAMING_SERVICE,
        api_base_url="https://api.music.apple.com/v1",
        auth_method=AuthenticationMethod.JWT,
        supported_audio_formats=["aac", "mp3"],
        analytics_support=True,
        monetization_support=True
    ))
    
    youtube_music: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="YouTube Music",
        integration_type=IntegrationType.STREAMING_SERVICE,
        api_base_url="https://www.googleapis.com/youtube/v3",
        auth_method=AuthenticationMethod.OAUTH2,
        supported_audio_formats=["mp3", "aac", "ogg"],
        supported_video_formats=["mp4", "webm"],
        analytics_support=True,
        monetization_support=True
    ))

@dataclass
class SocialPlatformsConfig:
    """Configuration for social media platforms"""
    # Major social platforms
    instagram: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Instagram",
        integration_type=IntegrationType.SOCIAL_PLATFORM,
        api_base_url="https://graph.instagram.com",
        auth_method=AuthenticationMethod.OAUTH2,
        supported_image_formats=["jpg", "png"],
        supported_video_formats=["mp4"],
        upload_support=True,
        analytics_support=True
    ))
    
    tiktok: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="TikTok",
        integration_type=IntegrationType.SOCIAL_PLATFORM,
        api_base_url="https://open-api.tiktok.com",
        auth_method=AuthenticationMethod.OAUTH2,
        supported_video_formats=["mp4"],
        supported_audio_formats=["mp3", "aac"],
        upload_support=True,
        analytics_support=True
    ))
    
    twitter: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Twitter",
        integration_type=IntegrationType.SOCIAL_PLATFORM,
        api_base_url="https://api.twitter.com/2",
        auth_method=AuthenticationMethod.OAUTH2,
        supported_image_formats=["jpg", "png", "gif"],
        supported_video_formats=["mp4"],
        upload_support=True,
        analytics_support=True
    ))

@dataclass
class PaymentGatewaysConfig:
    """Configuration for payment gateways"""
    stripe: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Stripe",
        integration_type=IntegrationType.PAYMENT_GATEWAY,
        api_base_url="https://api.stripe.com/v1",
        auth_method=AuthenticationMethod.BEARER_TOKEN,
        monetization_support=True
    ))
    
    paypal: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="PayPal",
        integration_type=IntegrationType.PAYMENT_GATEWAY,
        api_base_url="https://api.paypal.com/v1",
        auth_method=AuthenticationMethod.OAUTH2,
        monetization_support=True
    ))
    
    wise: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Wise",
        integration_type=IntegrationType.PAYMENT_GATEWAY,
        api_base_url="https://api.transferwise.com/v1",
        auth_method=AuthenticationMethod.BEARER_TOKEN,
        monetization_support=True
    ))

@dataclass
class CloudServicesConfig:
    """Configuration for cloud services"""
    aws_s3: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="AWS S3",
        integration_type=IntegrationType.CLOUD_STORAGE,
        api_base_url="https://s3.amazonaws.com",
        auth_method=AuthenticationMethod.API_KEY,
        upload_support=True,
        download_support=True
    ))
    
    google_cloud: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Google Cloud Storage",
        integration_type=IntegrationType.CLOUD_STORAGE,
        api_base_url="https://storage.googleapis.com/storage/v1",
        auth_method=AuthenticationMethod.OAUTH2,
        upload_support=True,
        download_support=True
    ))
    
    azure_blob: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Azure Blob Storage",
        integration_type=IntegrationType.CLOUD_STORAGE,
        api_base_url="https://{account}.blob.core.windows.net",
        auth_method=AuthenticationMethod.API_KEY,
        upload_support=True,
        download_support=True
    ))

@dataclass
class AIServicesConfig:
    """Configuration for AI and ML services"""
    openai: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="OpenAI",
        integration_type=IntegrationType.AI_SERVICE,
        api_base_url="https://api.openai.com/v1",
        auth_method=AuthenticationMethod.BEARER_TOKEN
    ))
    
    hugging_face: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Hugging Face",
        integration_type=IntegrationType.AI_SERVICE,
        api_base_url="https://api-inference.huggingface.co",
        auth_method=AuthenticationMethod.BEARER_TOKEN
    ))
    
    google_vision: PlatformIntegrationConfig = field(default_factory=lambda: PlatformIntegrationConfig(
        platform_name="Google Vision AI",
        integration_type=IntegrationType.AI_SERVICE,
        api_base_url="https://vision.googleapis.com/v1",
        auth_method=AuthenticationMethod.OAUTH2
    ))

@dataclass
class ExternalIntegrationsConfiguration:
    """Master external integrations configuration"""
    # Platform configurations
    streaming_platforms: StreamingPlatformsConfig = field(default_factory=StreamingPlatformsConfig)
    social_platforms: SocialPlatformsConfig = field(default_factory=SocialPlatformsConfig)
    payment_gateways: PaymentGatewaysConfig = field(default_factory=PaymentGatewaysConfig)
    cloud_services: CloudServicesConfig = field(default_factory=CloudServicesConfig)
    ai_services: AIServicesConfig = field(default_factory=AIServicesConfig)
    
    # Global integration settings
    global_timeout_seconds: int = 30
    global_retry_attempts: int = 3
    global_rate_limiting: bool = True
    global_error_handling: bool = True
    global_monitoring: bool = True
    
    # Security settings
    ssl_verification: bool = True
    certificate_validation: bool = True
    token_encryption: bool = True
    webhook_signature_validation: bool = True
    
    # Performance settings
    connection_pooling: bool = True
    async_requests: bool = True
    batch_operations: bool = True
    caching_enabled: bool = True
    compression_enabled: bool = True
    
    # Monitoring and analytics
    integration_analytics: bool = True
    performance_metrics: bool = True
    error_tracking: bool = True
    usage_statistics: bool = True
    
    # Custom integrations
    custom_integrations: Dict[str, PlatformIntegrationConfig] = field(default_factory=dict)
    
    # Metadata
    version: str = "2.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "Fahed Mlaiel"
    contact_email: str = "mlaiel@live.de"

class ExternalIntegrationsConfigManager:
    """
    Enterprise-grade external integrations configuration manager.
    
    Manages comprehensive integration with:
    - Streaming platforms (Spotify, Apple Music, YouTube Music)
    - Social media platforms (Instagram, TikTok, Twitter, Facebook)
    - Payment gateways (Stripe, PayPal, Wise)
    - Cloud storage services (AWS S3, Google Cloud, Azure)
    - AI/ML services (OpenAI, Hugging Face, Google Vision)
    - CDN services
    - Email and SMS services
    - Analytics and monitoring services
    - Blockchain and NFT platforms
    - Legal and compliance services
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize external integrations configuration manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration path
        self.config_path = config_path or os.getenv(
            "INTEGRATIONS_CONFIG_PATH",
            "/app/config/external_integrations.yaml"
        )
        
        # Initialize default configuration
        self._config = ExternalIntegrationsConfiguration()
        
        # Configuration state
        self.initialized = False
        self.last_updated = datetime.now()
        self.validation_errors = []
        self.connection_status = {}
        
        # Load configuration from file if exists
        self._load_configuration()
        
        self.logger.info("External integrations configuration manager initialized")
    
    def _load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update configuration with loaded data
                self._update_config_from_dict(config_data)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.info("No configuration file found, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._config.updated_at = datetime.now()
        self.last_updated = datetime.now()
    
    async def test_integration(self, platform_name: str) -> Dict[str, Any]:
        """Test connectivity to a specific platform integration"""
        try:
            integration_config = self.get_integration_config(platform_name)
            if not integration_config:
                return {
                    "success": False,
                    "error": f"Integration {platform_name} not found",
                    "timestamp": datetime.now()
                }
            
            if not integration_config.enabled:
                return {
                    "success": False,
                    "error": f"Integration {platform_name} is disabled",
                    "timestamp": datetime.now()
                }
            
            # Test health check endpoint if available
            if integration_config.health_check_url:
                test_url = integration_config.health_check_url
            else:
                test_url = integration_config.api_base_url
            
            if not test_url:
                return {
                    "success": False,
                    "error": f"No test URL available for {platform_name}",
                    "timestamp": datetime.now()
                }
            
            # Prepare headers
            headers = {}
            if integration_config.auth_method == AuthenticationMethod.API_KEY and integration_config.api_key:
                headers["Authorization"] = f"Bearer {integration_config.api_key}"
            elif integration_config.auth_method == AuthenticationMethod.BEARER_TOKEN and integration_config.access_token:
                headers["Authorization"] = f"Bearer {integration_config.access_token}"
            
            headers.update(integration_config.custom_headers)
            
            # Make test request
            start_time = datetime.now()
            try:
                response = requests.get(
                    test_url,
                    headers=headers,
                    timeout=integration_config.api_timeout_seconds,
                    verify=self._config.ssl_verification
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                test_result = {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "response_time_seconds": response_time,
                    "timestamp": datetime.now(),
                    "url_tested": test_url
                }
                
                if not test_result["success"]:
                    test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
                # Update connection status
                self.connection_status[platform_name] = {
                    "status": IntegrationStatus.ACTIVE if test_result["success"] else IntegrationStatus.ERROR,
                    "last_tested": datetime.now(),
                    "response_time": response_time,
                    "status_code": response.status_code
                }
                
                return test_result
                
            except requests.exceptions.Timeout:
                self.connection_status[platform_name] = {
                    "status": IntegrationStatus.ERROR,
                    "last_tested": datetime.now(),
                    "error": "Request timeout"
                }
                return {
                    "success": False,
                    "error": "Request timeout",
                    "timestamp": datetime.now()
                }
            
            except requests.exceptions.ConnectionError:
                self.connection_status[platform_name] = {
                    "status": IntegrationStatus.ERROR,
                    "last_tested": datetime.now(),
                    "error": "Connection error"
                }
                return {
                    "success": False,
                    "error": "Connection error",
                    "timestamp": datetime.now()
                }
        
        except Exception as e:
            self.logger.error(f"Integration test failed for {platform_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def test_all_integrations(self) -> Dict[str, Any]:
        """Test connectivity to all enabled integrations"""
        try:
            test_results = {}
            
            # Get all platform configurations
            all_platforms = self.get_all_platform_configs()
            
            # Test each enabled integration
            for platform_name, config in all_platforms.items():
                if config.enabled:
                    test_results[platform_name] = await self.test_integration(platform_name)
            
            # Summary statistics
            total_tested = len(test_results)
            successful = sum(1 for result in test_results.values() if result.get("success", False))
            failed = total_tested - successful
            
            return {
                "summary": {
                    "total_tested": total_tested,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / total_tested * 100) if total_tested > 0 else 0
                },
                "results": test_results,
                "timestamp": datetime.now()
            }
        
        except Exception as e:
            self.logger.error(f"Failed to test all integrations: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def get_integration_config(self, platform_name: str) -> Optional[PlatformIntegrationConfig]:
        """Get configuration for specific platform integration"""
        
        # Check in all platform categories
        platform_categories = [
            self._config.streaming_platforms,
            self._config.social_platforms,
            self._config.payment_gateways,
            self._config.cloud_services,
            self._config.ai_services
        ]
        
        for category in platform_categories:
            if hasattr(category, platform_name.lower().replace(" ", "_")):
                return getattr(category, platform_name.lower().replace(" ", "_"))
        
        # Check custom integrations
        if platform_name in self._config.custom_integrations:
            return self._config.custom_integrations[platform_name]
        
        return None
    
    def get_all_platform_configs(self) -> Dict[str, PlatformIntegrationConfig]:
        """Get all platform configurations"""
        all_configs = {}
        
        # Streaming platforms
        streaming_attrs = ["spotify", "apple_music", "youtube_music"]
        for attr in streaming_attrs:
            if hasattr(self._config.streaming_platforms, attr):
                config = getattr(self._config.streaming_platforms, attr)
                all_configs[config.platform_name] = config
        
        # Social platforms
        social_attrs = ["instagram", "tiktok", "twitter"]
        for attr in social_attrs:
            if hasattr(self._config.social_platforms, attr):
                config = getattr(self._config.social_platforms, attr)
                all_configs[config.platform_name] = config
        
        # Payment gateways
        payment_attrs = ["stripe", "paypal", "wise"]
        for attr in payment_attrs:
            if hasattr(self._config.payment_gateways, attr):
                config = getattr(self._config.payment_gateways, attr)
                all_configs[config.platform_name] = config
        
        # Cloud services
        cloud_attrs = ["aws_s3", "google_cloud", "azure_blob"]
        for attr in cloud_attrs:
            if hasattr(self._config.cloud_services, attr):
                config = getattr(self._config.cloud_services, attr)
                all_configs[config.platform_name] = config
        
        # AI services
        ai_attrs = ["openai", "hugging_face", "google_vision"]
        for attr in ai_attrs:
            if hasattr(self._config.ai_services, attr):
                config = getattr(self._config.ai_services, attr)
                all_configs[config.platform_name] = config
        
        # Custom integrations
        all_configs.update(self._config.custom_integrations)
        
        return all_configs
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platform names"""
        all_configs = self.get_all_platform_configs()
        return [name for name, config in all_configs.items() if config.enabled]
    
    def add_custom_integration(self, platform_name: str, config: PlatformIntegrationConfig) -> bool:
        """Add custom integration configuration"""
        try:
            self._config.custom_integrations[platform_name] = config
            self._config.updated_at = datetime.now()
            self.last_updated = datetime.now()
            self.logger.info(f"Custom integration {platform_name} added")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add custom integration {platform_name}: {e}")
            return False
    
    def validate_configuration(self) -> List[str]:
        """Validate external integrations configuration"""
        errors = []
        
        try:
            # Validate global settings
            if self._config.global_timeout_seconds <= 0:
                errors.append("Global timeout must be positive")
            
            if self._config.global_retry_attempts < 0:
                errors.append("Global retry attempts cannot be negative")
            
            # Validate each platform configuration
            all_configs = self.get_all_platform_configs()
            for platform_name, config in all_configs.items():
                if config.enabled:
                    if not config.api_base_url:
                        errors.append(f"Platform {platform_name} has no API base URL")
                    
                    if config.api_timeout_seconds <= 0:
                        errors.append(f"Platform {platform_name} timeout must be positive")
                    
                    if config.auth_method == AuthenticationMethod.API_KEY and not config.api_key:
                        errors.append(f"Platform {platform_name} requires API key but none configured")
                    
                    if config.auth_method == AuthenticationMethod.OAUTH2:
                        if not config.client_id or not config.client_secret:
                            errors.append(f"Platform {platform_name} OAuth2 requires client_id and client_secret")
                    
                    # Validate URLs
                    if config.api_base_url:
                        try:
                            parsed = urlparse(config.api_base_url)
                            if not parsed.scheme or not parsed.netloc:
                                errors.append(f"Platform {platform_name} has invalid API base URL")
                        except Exception:
                            errors.append(f"Platform {platform_name} has malformed API base URL")
            
            self.validation_errors = errors
            
            if not errors:
                self.logger.info("External integrations configuration validation passed")
            else:
                self.logger.warning(f"External integrations validation failed with {len(errors)} errors")
            
            return errors
        
        except Exception as e:
            error_msg = f"External integrations configuration validation error: {e}"
            self.logger.error(error_msg)
            return [error_msg]
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status and metadata"""
        all_configs = self.get_all_platform_configs()
        enabled_count = sum(1 for config in all_configs.values() if config.enabled)
        
        return {
            "initialized": self.initialized,
            "last_updated": self.last_updated,
            "config_path": self.config_path,
            "validation_errors": self.validation_errors,
            "version": self._config.version,
            "created_by": self._config.created_by,
            "contact_email": self._config.contact_email,
            "total_integrations": len(all_configs),
            "enabled_integrations": enabled_count,
            "disabled_integrations": len(all_configs) - enabled_count,
            "connection_status": self.connection_status,
            "categories": {
                "streaming_platforms": 3,
                "social_platforms": 3,
                "payment_gateways": 3,
                "cloud_services": 3,
                "ai_services": 3,
                "custom_integrations": len(self._config.custom_integrations)
            },
            "features_enabled": {
                "global_monitoring": self._config.global_monitoring,
                "ssl_verification": self._config.ssl_verification,
                "token_encryption": self._config.token_encryption,
                "connection_pooling": self._config.connection_pooling,
                "async_requests": self._config.async_requests,
                "caching": self._config.caching_enabled,
                "compression": self._config.compression_enabled
            }
        }

# Global instance
external_integrations_config_manager = ExternalIntegrationsConfigManager()

# Export public API
__all__ = [
    "ExternalIntegrationsConfigManager",
    "ExternalIntegrationsConfiguration",
    "PlatformIntegrationConfig",
    "StreamingPlatformsConfig",
    "SocialPlatformsConfig",
    "PaymentGatewaysConfig",
    "CloudServicesConfig",
    "AIServicesConfig",
    "IntegrationType",
    "AuthenticationMethod",
    "IntegrationStatus",
    "external_integrations_config_manager"
]
