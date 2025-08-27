"""
Revenue Tracking Configuration Module
====================================

Professional revenue tracking and monitoring configuration for multi-platform content monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class RevenueSource(str, Enum):
    """Revenue source types for content monetization."""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TWITCH = "twitch"
    PATREON = "patreon"
    BANDCAMP = "bandcamp"
    SOUNDCLOUD = "soundcloud"
    LICENSING = "licensing"
    SYNC_RIGHTS = "sync_rights"
    MERCHANDISE = "merchandise"
    LIVE_STREAMING = "live_streaming"
    NFT_SALES = "nft_sales"
    BRAND_PARTNERSHIPS = "brand_partnerships"


class RevenueType(str, Enum):
    """Revenue type classification."""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    TIPS = "tips"
    SPONSORSHIP = "sponsorship"
    ROYALTIES = "royalties"
    COMMISSION = "commission"


class CurrencyCode(str, Enum):
    """Supported currency codes."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    CNY = "CNY"
    BRL = "BRL"
    INR = "INR"


@dataclass
class RevenueThreshold:
    """Revenue threshold configuration for notifications and payouts."""
    minimum_payout: Decimal
    notification_threshold: Decimal
    tax_threshold: Decimal
    currency: CurrencyCode
    enabled: bool = True


@dataclass
class PlatformRevenueConfig:
    """Platform-specific revenue configuration."""
    platform: RevenueSource
    commission_rate: Decimal  # Platform commission percentage
    minimum_threshold: Decimal
    payout_frequency: str  # daily, weekly, monthly, quarterly
    currency: CurrencyCode
    api_endpoint: Optional[str] = None
    api_credentials: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    real_time_tracking: bool = False


@dataclass
class RevenueTrackingConfig:
    """Main revenue tracking configuration class."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "REVENUE_DB_URL", 
        "postgresql://user:pass@localhost:5432/revenue_db"
    )
    
    # Redis Configuration for Caching
    REDIS_URL: str = os.getenv(
        "REVENUE_REDIS_URL", 
        "redis://localhost:6379/5"
    )
    
    # Default Currency
    DEFAULT_CURRENCY: CurrencyCode = CurrencyCode.EUR
    
    # Revenue Tracking Settings
    ENABLE_REAL_TIME_TRACKING: bool = True
    TRACKING_INTERVAL_SECONDS: int = 300  # 5 minutes
    BATCH_PROCESSING_SIZE: int = 1000
    
    # Revenue Thresholds by Currency
    REVENUE_THRESHOLDS: Dict[CurrencyCode, RevenueThreshold] = field(
        default_factory=lambda: {
            CurrencyCode.EUR: RevenueThreshold(
                minimum_payout=Decimal("50.00"),
                notification_threshold=Decimal("10.00"),
                tax_threshold=Decimal("600.00"),
                currency=CurrencyCode.EUR
            ),
            CurrencyCode.USD: RevenueThreshold(
                minimum_payout=Decimal("50.00"),
                notification_threshold=Decimal("10.00"),
                tax_threshold=Decimal("600.00"),
                currency=CurrencyCode.USD
            ),
            CurrencyCode.GBP: RevenueThreshold(
                minimum_payout=Decimal("40.00"),
                notification_threshold=Decimal("8.00"),
                tax_threshold=Decimal("500.00"),
                currency=CurrencyCode.GBP
            )
        }
    )
    
    # Platform Configurations
    PLATFORM_CONFIGS: Dict[RevenueSource, PlatformRevenueConfig] = field(
        default_factory=lambda: {
            RevenueSource.SPOTIFY: PlatformRevenueConfig(
                platform=RevenueSource.SPOTIFY,
                commission_rate=Decimal("15.0"),
                minimum_threshold=Decimal("5.00"),
                payout_frequency="monthly",
                currency=CurrencyCode.EUR,
                api_endpoint="https://api.spotify.com/v1",
                real_time_tracking=True
            ),
            RevenueSource.YOUTUBE: PlatformRevenueConfig(
                platform=RevenueSource.YOUTUBE,
                commission_rate=Decimal("45.0"),  # YouTube's cut
                minimum_threshold=Decimal("10.00"),
                payout_frequency="monthly",
                currency=CurrencyCode.USD,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                real_time_tracking=True
            ),
            RevenueSource.APPLE_MUSIC: PlatformRevenueConfig(
                platform=RevenueSource.APPLE_MUSIC,
                commission_rate=Decimal("30.0"),
                minimum_threshold=Decimal("10.00"),
                payout_frequency="monthly",
                currency=CurrencyCode.USD,
                real_time_tracking=False
            ),
            RevenueSource.INSTAGRAM: PlatformRevenueConfig(
                platform=RevenueSource.INSTAGRAM,
                commission_rate=Decimal("30.0"),
                minimum_threshold=Decimal("5.00"),
                payout_frequency="weekly",
                currency=CurrencyCode.USD,
                real_time_tracking=True
            ),
            RevenueSource.TIKTOK: PlatformRevenueConfig(
                platform=RevenueSource.TIKTOK,
                commission_rate=Decimal("50.0"),
                minimum_threshold=Decimal("5.00"),
                payout_frequency="monthly",
                currency=CurrencyCode.USD,
                real_time_tracking=True
            ),
            RevenueSource.PATREON: PlatformRevenueConfig(
                platform=RevenueSource.PATREON,
                commission_rate=Decimal("5.0"),
                minimum_threshold=Decimal("1.00"),
                payout_frequency="monthly",
                currency=CurrencyCode.USD,
                api_endpoint="https://www.patreon.com/api",
                real_time_tracking=True
            )
        }
    )
    
    # Revenue Categories and Types Mapping
    REVENUE_TYPE_MAPPING: Dict[RevenueSource, List[RevenueType]] = field(
        default_factory=lambda: {
            RevenueSource.SPOTIFY: [RevenueType.STREAMING, RevenueType.ROYALTIES],
            RevenueSource.YOUTUBE: [
                RevenueType.STREAMING, 
                RevenueType.ADVERTISING, 
                RevenueType.SUBSCRIPTION
            ],
            RevenueSource.APPLE_MUSIC: [RevenueType.STREAMING, RevenueType.DOWNLOADS],
            RevenueSource.INSTAGRAM: [
                RevenueType.ADVERTISING, 
                RevenueType.SPONSORSHIP, 
                RevenueType.TIPS
            ],
            RevenueSource.TIKTOK: [
                RevenueType.TIPS, 
                RevenueType.ADVERTISING, 
                RevenueType.SPONSORSHIP
            ],
            RevenueSource.PATREON: [RevenueType.SUBSCRIPTION, RevenueType.TIPS],
            RevenueSource.LICENSING: [RevenueType.LICENSING, RevenueType.ROYALTIES],
            RevenueSource.MERCHANDISE: [RevenueType.MERCHANDISE],
            RevenueSource.BRAND_PARTNERSHIPS: [
                RevenueType.SPONSORSHIP, 
                RevenueType.COMMISSION
            ]
        }
    )
    
    # Notification Configuration
    NOTIFICATION_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "email_notifications": True,
        "push_notifications": True,
        "webhook_notifications": True,
        "daily_summary": True,
        "weekly_report": True,
        "monthly_report": True,
        "threshold_alerts": True,
        "payout_notifications": True
    })
    
    # Analytics Configuration
    ANALYTICS_RETENTION_DAYS: int = 2555  # 7 years for tax purposes
    ENABLE_PREDICTIVE_ANALYTICS: bool = True
    ML_MODEL_REFRESH_HOURS: int = 24
    
    # Tax Configuration
    TAX_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "enable_tax_calculation": True,
        "default_tax_rate": Decimal("19.0"),  # German VAT
        "tax_jurisdictions": ["DE", "US", "GB", "FR", "IT", "ES"],
        "quarterly_tax_reports": True,
        "automatic_tax_withholding": False
    })
    
    # Exchange Rate Configuration
    EXCHANGE_RATE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "auto_update_rates": True,
        "update_frequency_hours": 1,
        "rate_provider": "fixer.io",
        "fallback_provider": "exchangerate-api.com",
        "cache_rates_hours": 6
    })
    
    # Performance Settings
    PERFORMANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "max_concurrent_api_calls": 50,
        "api_timeout_seconds": 30,
        "retry_attempts": 3,
        "backoff_multiplier": 2,
        "circuit_breaker_threshold": 5
    })
    
    # Security Settings
    SECURITY_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "encrypt_revenue_data": True,
        "encryption_key_rotation_days": 90,
        "audit_all_transactions": True,
        "require_2fa_for_payouts": True,
        "fraud_detection_enabled": True,
        "suspicious_activity_threshold": Decimal("1000.00")
    })
    
    def get_platform_config(self, platform: RevenueSource) -> Optional[PlatformRevenueConfig]:
        """Get configuration for a specific platform."""
        return self.PLATFORM_CONFIGS.get(platform)
    
    def get_revenue_threshold(self, currency: CurrencyCode) -> Optional[RevenueThreshold]:
        """Get revenue threshold for a specific currency."""
        return self.REVENUE_THRESHOLDS.get(currency, 
                                         self.REVENUE_THRESHOLDS.get(self.DEFAULT_CURRENCY))
    
    def is_platform_enabled(self, platform: RevenueSource) -> bool:
        """Check if a platform is enabled for revenue tracking."""
        config = self.get_platform_config(platform)
        return config.enabled if config else False
    
    def get_supported_revenue_types(self, platform: RevenueSource) -> List[RevenueType]:
        """Get supported revenue types for a platform."""
        return self.REVENUE_TYPE_MAPPING.get(platform, [])


# Global configuration instance
revenue_config = RevenueTrackingConfig()
