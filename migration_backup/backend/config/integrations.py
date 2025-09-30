"""Integrations Configuration Module - Consolidated Integration Configs
====================================================================

Consolidates all integration-related configurations from:
- config/integrations/ (17 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# ===== PLATFORM INTEGRATIONS =====

class PlatformType(str, Enum):
    """Platform types"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    TWITCH = "twitch"

@dataclass
class PlatformConfig:
    """Individual platform configuration"""
    platform: PlatformType
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit_per_hour: int = 1000
    timeout_seconds: int = 30
    retry_attempts: int = 3

@dataclass
class PlatformIntegrationsConfig:
    """Platform integrations configuration"""
    enabled: bool = True
    platforms: List[PlatformConfig] = field(default_factory=list)
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 60
    batch_operations_enabled: bool = True
    error_handling_strategy: str = "retry_with_backoff"

# ===== PAYMENT INTEGRATIONS =====

class PaymentProvider(str, Enum):
    """Payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    BRAINTREE = "braintree"
    RAZORPAY = "razorpay"

@dataclass
class PaymentIntegrationConfig:
    """Payment integration configuration"""
    provider: PaymentProvider
    enabled: bool = True
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    environment: str = "sandbox"  # sandbox, production
    currency: str = "USD"
    auto_capture: bool = True
    webhook_endpoints: List[str] = field(default_factory=list)

# ===== EMAIL INTEGRATIONS =====

class EmailProvider(str, Enum):
    """Email service providers"""
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    SES = "ses"
    SMTP = "smtp"
    POSTMARK = "postmark"
    MAILCHIMP = "mailchimp"

@dataclass
class EmailIntegrationConfig:
    """Email integration configuration"""
    provider: EmailProvider
    enabled: bool = True
    api_key: Optional[str] = None
    domain: Optional[str] = None
    from_email: str = "noreply@ia-influencer.com"
    from_name: str = "IA Influencer Agent"
    template_engine: str = "jinja2"
    tracking_enabled: bool = True
    unsubscribe_handling: bool = True

# ===== ANALYTICS INTEGRATIONS =====

class AnalyticsProvider(str, Enum):
    """Analytics providers"""
    GOOGLE_ANALYTICS = "google_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    SEGMENT = "segment"
    HOTJAR = "hotjar"
    INTERCOM = "intercom"

@dataclass
class AnalyticsIntegrationConfig:
    """Analytics integration configuration"""
    provider: AnalyticsProvider
    enabled: bool = True
    tracking_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    custom_events: List[str] = field(default_factory=list)
    user_properties: List[str] = field(default_factory=list)
    gdpr_compliant: bool = True

# ===== CLOUD STORAGE INTEGRATIONS =====

class CloudProvider(str, Enum):
    """Cloud storage providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    LINODE = "linode"
    VULTR = "vultr"

@dataclass
class CloudIntegrationConfig:
    """Cloud integration configuration"""
    provider: CloudProvider
    enabled: bool = True
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: str = "us-east-1"
    services: List[str] = field(default_factory=list)
    auto_scaling: bool = False
    monitoring_enabled: bool = True

# ===== AI/ML SERVICE INTEGRATIONS =====

class AIProvider(str, Enum):
    """AI/ML service providers"""
    OPENAI = "openai"
    HUGGING_FACE = "hugging_face"
    GOOGLE_AI = "google_ai"
    AZURE_AI = "azure_ai"
    AWS_AI = "aws_ai"
    ANTHROPIC = "anthropic"

@dataclass
class AIIntegrationConfig:
    """AI service integration configuration"""
    provider: AIProvider
    enabled: bool = True
    api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    rate_limit_per_minute: int = 60
    cache_responses: bool = True

# ===== BLOCKCHAIN INTEGRATIONS =====

class BlockchainNetwork(str, Enum):
    """Blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"

@dataclass
class BlockchainIntegrationConfig:
    """Blockchain integration configuration"""
    network: BlockchainNetwork
    enabled: bool = False
    rpc_url: Optional[str] = None
    private_key: Optional[str] = None
    contract_address: Optional[str] = None
    gas_limit: int = 21000
    gas_price: str = "auto"
    confirmation_blocks: int = 12

# ===== COMMUNICATION INTEGRATIONS =====

class CommunicationProvider(str, Enum):
    """Communication service providers"""
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    SMS = "sms"

@dataclass
class CommunicationIntegrationConfig:
    """Communication integration configuration"""
    provider: CommunicationProvider
    enabled: bool = True
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    channel_id: Optional[str] = None
    bot_token: Optional[str] = None
    notification_types: List[str] = field(default_factory=list)

# ===== MAIN INTEGRATIONS CONFIGURATION =====

@dataclass
class IntegrationsConfig:
    """Main integrations configuration"""
    platforms: PlatformIntegrationsConfig = field(default_factory=PlatformIntegrationsConfig)
    payments: List[PaymentIntegrationConfig] = field(default_factory=list)
    email: List[EmailIntegrationConfig] = field(default_factory=list)
    analytics: List[AnalyticsIntegrationConfig] = field(default_factory=list)
    cloud: List[CloudIntegrationConfig] = field(default_factory=list)
    ai: List[AIIntegrationConfig] = field(default_factory=list)
    blockchain: List[BlockchainIntegrationConfig] = field(default_factory=list)
    communication: List[CommunicationIntegrationConfig] = field(default_factory=list)
    global_timeout: int = 30
    global_retry_attempts: int = 3
    circuit_breaker_enabled: bool = True

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_integrations_config() -> IntegrationsConfig:
    """Get development integrations configuration"""
    return IntegrationsConfig(
        platforms=PlatformIntegrationsConfig(
            enabled=False,  # Disable in dev
            auto_sync_enabled=False
        ),
        payments=[
            PaymentIntegrationConfig(
                provider=PaymentProvider.STRIPE,
                environment="sandbox"
            )
        ],
        email=[
            EmailIntegrationConfig(
                provider=EmailProvider.SMTP,
                from_email="dev@localhost"
            )
        ],
        analytics=[],  # No analytics in dev
        ai=[
            AIIntegrationConfig(
                provider=AIProvider.OPENAI,
                enabled=False  # Disable AI in dev to save costs
            )
        ]
    )

def get_production_integrations_config() -> IntegrationsConfig:
    """Get production integrations configuration"""
    return IntegrationsConfig(
        platforms=PlatformIntegrationsConfig(
            enabled=True,
            platforms=[
                PlatformConfig(platform=PlatformType.SPOTIFY),
                PlatformConfig(platform=PlatformType.YOUTUBE),
                PlatformConfig(platform=PlatformType.INSTAGRAM)
            ]
        ),
        payments=[
            PaymentIntegrationConfig(
                provider=PaymentProvider.STRIPE,
                environment="production"
            )
        ],
        email=[
            EmailIntegrationConfig(
                provider=EmailProvider.SENDGRID
            )
        ],
        analytics=[
            AnalyticsIntegrationConfig(
                provider=AnalyticsProvider.GOOGLE_ANALYTICS
            )
        ],
        ai=[
            AIIntegrationConfig(
                provider=AIProvider.OPENAI,
                enabled=True
            )
        ]
    )

def get_testing_integrations_config() -> IntegrationsConfig:
    """Get testing integrations configuration"""
    return IntegrationsConfig(
        platforms=PlatformIntegrationsConfig(
            enabled=False
        ),
        payments=[],  # No payments in testing
        email=[],     # No email in testing
        analytics=[], # No analytics in testing
        ai=[
            AIIntegrationConfig(
                provider=AIProvider.OPENAI,
                enabled=False
            )
        ]
    )

# ===== INTEGRATIONS CONFIGURATION FACTORY =====

class IntegrationsConfigurationFactory:
    """Factory for creating integrations configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> IntegrationsConfig:
        """Create integrations configuration for environment"""
        if environment.lower() == "production":
            return get_production_integrations_config()
        elif environment.lower() == "testing":
            return get_testing_integrations_config()
        else:
            return get_development_integrations_config()

# Export all integrations configurations
__all__ = [
    # Enums
    "PlatformType",
    "PaymentProvider",
    "EmailProvider",
    "AnalyticsProvider",
    "CloudProvider",
    "AIProvider",
    "BlockchainNetwork",
    "CommunicationProvider",
    
    # Configuration Classes
    "PlatformConfig",
    "PlatformIntegrationsConfig",
    "PaymentIntegrationConfig",
    "EmailIntegrationConfig",
    "AnalyticsIntegrationConfig",
    "CloudIntegrationConfig",
    "AIIntegrationConfig",
    "BlockchainIntegrationConfig",
    "CommunicationIntegrationConfig",
    "IntegrationsConfig",
    
    # Factory and Functions
    "IntegrationsConfigurationFactory",
    "get_development_integrations_config",
    "get_production_integrations_config",
    "get_testing_integrations_config"
]