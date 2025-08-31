"""Content Protection AI Configuration for IA-Influencer Agent Platform
====================================================================

Professional content protection and rights management AI configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class ProtectionLevel(str, Enum):
    """Content protection security levels."""    
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    FORENSIC = "forensic"


class MonitoringScope(str, Enum):
    """Monitoring scope for content protection."""    
    PLATFORM_SPECIFIC = "platform_specific"
    CROSS_PLATFORM = "cross_platform"
    GLOBAL_WEB = "global_web"
    DEEP_WEB = "deep_web"
    SOCIAL_MEDIA = "social_media"


class ActionType(str, Enum):
    """Automated protection actions."""    
    MONITOR_ONLY = "monitor_only"
    NOTIFY_OWNER = "notify_owner"
    SEND_TAKEDOWN = "send_takedown"
    CLAIM_REVENUE = "claim_revenue"
    LEGAL_ACTION = "legal_action"
    BLOCK_ACCESS = "block_access"


class PlatformType(str, Enum):
    """Supported platforms for content monitoring."""    
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    GENERIC_WEB = "generic_web"


@dataclass
class ProtectionRule:
    """Content protection rule configuration."""    
    rule_id: str
    rule_name: str
    protection_level: ProtectionLevel
    monitoring_scope: MonitoringScope
    target_platforms: List[PlatformType]
    similarity_threshold: float
    action_type: ActionType
    automated_response: bool = True
    notification_enabled: bool = True
    revenue_claiming: bool = False
    legal_escalation: bool = False
    custom_parameters: Optional[Dict[str, Any]] = None


class ContentProtectionConfig(BaseSettings):
    """    Professional Content Protection AI Configuration.
    
    Manages comprehensive content protection including monitoring,
    detection, and automated response systems for rights management.
    """    
    # Core Protection Configuration
    PROTECTION_STORAGE_PATH: str = "/data/protection"
    MONITORING_INTERVAL_SECONDS: int = 3600  # 1 hour
    SCAN_FREQUENCY_HOURS: int = 24
    ENABLE_REAL_TIME_MONITORING: bool = True
    ENABLE_PROACTIVE_SCANNING: bool = True
    
    # Detection Thresholds
    SIMILARITY_THRESHOLD_GLOBAL: float = 0.85
    AUDIO_SIMILARITY_THRESHOLD: float = 0.90
    VIDEO_SIMILARITY_THRESHOLD: float = 0.85
    IMAGE_SIMILARITY_THRESHOLD: float = 0.88
    TEXT_SIMILARITY_THRESHOLD: float = 0.82
    
    # Platform Monitoring
    YOUTUBE_MONITORING_ENABLED: bool = True
    TIKTOK_MONITORING_ENABLED: bool = True
    INSTAGRAM_MONITORING_ENABLED: bool = True
    FACEBOOK_MONITORING_ENABLED: bool = True
    TWITTER_MONITORING_ENABLED: bool = True
    SPOTIFY_MONITORING_ENABLED: bool = True
    SOUNDCLOUD_MONITORING_ENABLED: bool = True
    GENERIC_WEB_MONITORING_ENABLED: bool = True
    
    # Automated Response Configuration
    AUTO_TAKEDOWN_ENABLED: bool = True
    AUTO_REVENUE_CLAIM_ENABLED: bool = True
    AUTO_NOTIFICATION_ENABLED: bool = True
    AUTO_LEGAL_ESCALATION_ENABLED: bool = False
    
    # Processing Limits
    MAX_CONCURRENT_SCANS: int = 16
    MAX_SCAN_DEPTH: int = 5
    MAX_RESULTS_PER_SCAN: int = 1000
    SCAN_TIMEOUT_SECONDS: int = 7200  # 2 hours
    
    # Fingerprint Matching
    FINGERPRINT_INDEX_TYPE: str = "faiss_ivf"
    VECTOR_SIMILARITY_METRIC: str = "cosine"
    INDEX_SHARDS: int = 4
    SEARCH_CANDIDATES: int = 1000
    RERANK_TOP_K: int = 100
    
    # Copyright Detection Models
    AUDIO_COPYRIGHT_MODEL: str = "custom/audio-copyright-detector-v3"
    VIDEO_COPYRIGHT_MODEL: str = "custom/video-copyright-detector-v2"
    IMAGE_COPYRIGHT_MODEL: str = "custom/image-copyright-detector-v2"
    TEXT_COPYRIGHT_MODEL: str = "transformers/copyright-detector-bert"
    MULTIMODAL_COPYRIGHT_MODEL: str = "custom/multimodal-copyright-v1"
    
    # Web Crawling Configuration
    CRAWLER_USER_AGENT: str = "IA-Influencer-Protection-Bot/2.0"
    CRAWLER_RATE_LIMIT_DELAY: float = 1.0  # seconds
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_TIMEOUT_SECONDS: int = 30
    RESPECT_ROBOTS_TXT: bool = True
    USE_PROXY_ROTATION: bool = True
    
    # API Integration Configuration
    YOUTUBE_API_ENABLED: bool = True
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_CONTENT_ID_ENABLED: bool = True
    
    TIKTOK_API_ENABLED: bool = True
    TIKTOK_API_KEY: Optional[str] = None
    
    INSTAGRAM_API_ENABLED: bool = True
    INSTAGRAM_API_KEY: Optional[str] = None
    
    SPOTIFY_API_ENABLED: bool = True
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    
    # Notification Configuration
    EMAIL_NOTIFICATIONS: bool = True
    SMS_NOTIFICATIONS: bool = True
    PUSH_NOTIFICATIONS: bool = True
    WEBHOOK_NOTIFICATIONS: bool = True
    SLACK_NOTIFICATIONS: bool = False
    DISCORD_NOTIFICATIONS: bool = False
    
    # Legal and Compliance
    DMCA_TAKEDOWN_ENABLED: bool = True
    DMCA_TEMPLATE_PATH: str = "/templates/dmca_takedown.txt"
    COPYRIGHT_NOTICE_TEMPLATE: str = "/templates/copyright_notice.txt"
    LEGAL_CONTACT_EMAIL: str = "legal@ia-influencer.com"
    JURISDICTION: str = "Germany"
    
    # Revenue Protection
    REVENUE_CLAIMING_ENABLED: bool = True
    REVENUE_SPLIT_PERCENTAGE: float = 100.0  # 100% to original owner
    MINIMUM_REVENUE_THRESHOLD: float = 1.0  # €1 minimum
    PAYMENT_PROCESSOR: str = "stripe"
    ESCROW_ENABLED: bool = True
    
    # Data Retention and Privacy
    SCAN_RESULTS_RETENTION_DAYS: int = 365
    PERSONAL_DATA_ANONYMIZATION: bool = True
    GDPR_COMPLIANCE_ENABLED: bool = True
    DATA_ENCRYPTION_ENABLED: bool = True
    SECURE_DATA_DELETION: bool = True
    
    # Performance and Scaling
    USE_GPU_ACCELERATION: bool = True
    GPU_MEMORY_FRACTION: float = 0.6
    ENABLE_MODEL_QUANTIZATION: bool = True
    BATCH_PROCESSING_SIZE: int = 32
    ASYNC_PROCESSING_ENABLED: bool = True
    DISTRIBUTED_PROCESSING: bool = True
    
    # Monitoring and Analytics
    PROTECTION_ANALYTICS_ENABLED: bool = True
    GENERATE_PROTECTION_REPORTS: bool = True
    REPORT_FREQUENCY_HOURS: int = 24
    TRACK_INFRINGEMENT_TRENDS: bool = True
    MEASURE_RESPONSE_EFFECTIVENESS: bool = True
    
    # Security Configuration
    API_RATE_LIMITING_ENABLED: bool = True
    PROTECTION_API_KEY_REQUIRED: bool = True
    SECURE_COMMUNICATION_TLS: bool = True
    ACCESS_LOGGING_ENABLED: bool = True
    INTRUSION_DETECTION_ENABLED: bool = True
    
    @validator("SIMILARITY_THRESHOLD_GLOBAL")
    def validate_similarity_threshold(cls, v):
        if v < 0.5 or v > 1.0:
            raise ValueError("Similarity threshold must be between 0.5 and 1.0")
        return v
    
    @validator("MAX_CONCURRENT_SCANS")
    def validate_concurrent_scans(cls, v):
        if v <= 0 or v > 64:
            raise ValueError("Concurrent scans must be between 1 and 64")
        return v
    
    @validator("REVENUE_SPLIT_PERCENTAGE")
    def validate_revenue_split(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError("Revenue split must be between 0% and 100%")
        return v
    
    def get_protection_rule(
        self, 
        content_type: str, 
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    ) -> ProtectionRule:
        """Get protection rule for content type and level."""        
        if protection_level == ProtectionLevel.ENTERPRISE:
            return ProtectionRule(
                rule_id=f"enterprise_{content_type}",
                rule_name=f"Enterprise Protection - {content_type}",
                protection_level=protection_level,
                monitoring_scope=MonitoringScope.GLOBAL_WEB,
                target_platforms=[p for p in PlatformType],
                similarity_threshold=0.82,
                action_type=ActionType.CLAIM_REVENUE,
                automated_response=True,
                notification_enabled=True,
                revenue_claiming=True,
                legal_escalation=True
            )
        elif protection_level == ProtectionLevel.ADVANCED:
            return ProtectionRule(
                rule_id=f"advanced_{content_type}",
                rule_name=f"Advanced Protection - {content_type}",
                protection_level=protection_level,
                monitoring_scope=MonitoringScope.CROSS_PLATFORM,
                target_platforms=[
                    PlatformType.YOUTUBE,
                    PlatformType.TIKTOK,
                    PlatformType.INSTAGRAM,
                    PlatformType.FACEBOOK,
                    PlatformType.SPOTIFY
                ],
                similarity_threshold=0.85,
                action_type=ActionType.SEND_TAKEDOWN,
                automated_response=True,
                notification_enabled=True,
                revenue_claiming=True,
                legal_escalation=False
            )
        else:  # STANDARD or BASIC
            return ProtectionRule(
                rule_id=f"standard_{content_type}",
                rule_name=f"Standard Protection - {content_type}",
                protection_level=protection_level,
                monitoring_scope=MonitoringScope.SOCIAL_MEDIA,
                target_platforms=[
                    PlatformType.YOUTUBE,
                    PlatformType.TIKTOK,
                    PlatformType.INSTAGRAM
                ],
                similarity_threshold=0.88,
                action_type=ActionType.NOTIFY_OWNER,
                automated_response=False,
                notification_enabled=True,
                revenue_claiming=False,
                legal_escalation=False
            )
    
    def get_platform_config(self, platform: PlatformType) -> Dict[str, Any]:
        """Get platform-specific configuration."""        
        platform_configs = {
            PlatformType.YOUTUBE: {
                "api_enabled": self.YOUTUBE_API_ENABLED,
                "api_key": self.YOUTUBE_API_KEY,
                "content_id": self.YOUTUBE_CONTENT_ID_ENABLED,
                "rate_limit": 100,  # requests per hour
                "batch_size": 10,
                "supported_formats": ["mp4", "mp3", "wav"],
                "max_file_size_mb": 2048
            },
            PlatformType.TIKTOK: {
                "api_enabled": self.TIKTOK_API_ENABLED,
                "api_key": self.TIKTOK_API_KEY,
                "rate_limit": 200,
                "batch_size": 20,
                "supported_formats": ["mp4"],
                "max_file_size_mb": 100
            },
            PlatformType.SPOTIFY: {
                "api_enabled": self.SPOTIFY_API_ENABLED,
                "client_id": self.SPOTIFY_CLIENT_ID,
                "client_secret": self.SPOTIFY_CLIENT_SECRET,
                "rate_limit": 300,
                "batch_size": 50,
                "supported_formats": ["mp3", "wav", "flac"],
                "max_file_size_mb": 50
            }
        }
        
        return platform_configs.get(platform, {
            "api_enabled": False,
            "rate_limit": 50,
            "batch_size": 5,
            "supported_formats": [],
            "max_file_size_mb": 100
        })
    
    class Config:
        env_prefix = "CONTENT_PROTECTION_"
        case_sensitive = True


# Global instance for easy import
content_protection_config = ContentProtectionConfig()
