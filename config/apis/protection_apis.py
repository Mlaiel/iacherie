"""
Protection APIs Configuration - AI Content Protection & Copyright Services
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures AI-powered content protection services including fingerprinting,
DMCA takedown services, copyright verification, and content monitoring platforms.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class ProtectionServiceType(Enum):
    """Content protection service types"""
    FINGERPRINTING = "fingerprinting"
    COPYRIGHT_DETECTION = "copyright_detection"
    DMCA_TAKEDOWN = "dmca_takedown"
    CONTENT_MONITORING = "content_monitoring"
    WATERMARKING = "watermarking"
    BLOCKCHAIN_PROTECTION = "blockchain_protection"

class ContentType(Enum):
    """Supported content types for protection"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"

@dataclass
class ProtectionAPIConfig:
    """Configuration class for content protection APIs"""
    service_name: str
    service_type: ProtectionServiceType
    base_url: str
    api_version: str
    
    # API Credentials (from environment)
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    client_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Supported content types
    supported_content_types: List[ContentType] = field(default_factory=list)
    
    # Detection capabilities
    detection_accuracy: float = 0.95  # Minimum accuracy percentage
    processing_time_seconds: int = 30  # Average processing time
    supports_real_time: bool = False
    supports_batch_processing: bool = True
    
    # File size limits
    max_file_size_mb: int = 100
    max_batch_size: int = 100
    supported_formats: List[str] = field(default_factory=list)
    
    # Monitoring capabilities
    supports_web_monitoring: bool = False
    monitoring_frequency_hours: int = 24
    supported_platforms: List[str] = field(default_factory=list)
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 3600
    timeout_seconds: int = 60
    
    # Cost structure
    cost_per_fingerprint: float = 0.01
    cost_per_scan: float = 0.05
    monthly_quota: int = 10000
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""
        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# Chromaprint Audio Fingerprinting
CHROMAPRINT_CONFIG = ProtectionAPIConfig(
    service_name="chromaprint",
    service_type=ProtectionServiceType.FINGERPRINTING,
    base_url="https://api.acoustid.org",
    api_version="v2",
    api_key=os.getenv("ACOUSTID_API_KEY"),
    supported_content_types=[ContentType.AUDIO],
    detection_accuracy=0.97,
    processing_time_seconds=5,
    supports_real_time=True,
    supported_formats=["mp3", "wav", "flac", "aac", "ogg", "m4a"],
    max_file_size_mb=50,
    rate_limit_per_minute=100,
    cost_per_fingerprint=0.001,
    monthly_quota=100000
)

# Content ID (YouTube-style content identification)
CONTENT_ID_CONFIG = ProtectionAPIConfig(
    service_name="content_id",
    service_type=ProtectionServiceType.COPYRIGHT_DETECTION,
    base_url="https://api.content-id.googleapis.com",
    api_version="v1",
    api_key=os.getenv("CONTENT_ID_API_KEY"),
    client_id=os.getenv("CONTENT_ID_CLIENT_ID"),
    secret_key=os.getenv("CONTENT_ID_CLIENT_SECRET"),
    supported_content_types=[ContentType.AUDIO, ContentType.VIDEO],
    detection_accuracy=0.95,
    processing_time_seconds=120,
    supports_batch_processing=True,
    supported_formats=["mp4", "avi", "mov", "wmv", "mp3", "wav", "aac"],
    max_file_size_mb=2000,
    supports_web_monitoring=True,
    monitoring_frequency_hours=1,
    supported_platforms=["youtube", "facebook", "instagram", "tiktok"],
    rate_limit_per_minute=20,
    cost_per_scan=0.10,
    monthly_quota=10000
)

# Audible Magic Audio/Video Recognition
AUDIBLE_MAGIC_CONFIG = ProtectionAPIConfig(
    service_name="audible_magic",
    service_type=ProtectionServiceType.COPYRIGHT_DETECTION,
    base_url="https://api.audiblemagic.com",
    api_version="v3",
    api_key=os.getenv("AUDIBLE_MAGIC_API_KEY"),
    supported_content_types=[ContentType.AUDIO, ContentType.VIDEO],
    detection_accuracy=0.98,
    processing_time_seconds=30,
    supports_batch_processing=True,
    supported_formats=["mp3", "wav", "aac", "flac", "mp4", "avi", "mov"],
    max_file_size_mb=500,
    supports_web_monitoring=True,
    monitoring_frequency_hours=2,
    supported_platforms=["youtube", "facebook", "instagram", "tiktok", "soundcloud"],
    rate_limit_per_minute=50,
    cost_per_scan=0.05,
    monthly_quota=20000
)

# Digimarc Watermarking & Protection
DIGIMARC_CONFIG = ProtectionAPIConfig(
    service_name="digimarc",
    service_type=ProtectionServiceType.WATERMARKING,
    base_url="https://api.digimarc.com",
    api_version="v2",
    api_key=os.getenv("DIGIMARC_API_KEY"),
    supported_content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO],
    detection_accuracy=0.96,
    processing_time_seconds=15,
    supports_real_time=False,
    supports_batch_processing=True,
    supported_formats=["jpg", "png", "tiff", "mp4", "mov", "mp3", "wav"],
    max_file_size_mb=200,
    supports_web_monitoring=True,
    rate_limit_per_minute=30,
    cost_per_fingerprint=0.02,
    monthly_quota=50000
)

# TinEye Reverse Image Search
TINEYE_CONFIG = ProtectionAPIConfig(
    service_name="tineye",
    service_type=ProtectionServiceType.COPYRIGHT_DETECTION,
    base_url="https://api.tineye.com",
    api_version="v1",
    api_key=os.getenv("TINEYE_API_KEY"),
    supported_content_types=[ContentType.IMAGE],
    detection_accuracy=0.94,
    processing_time_seconds=10,
    supports_real_time=True,
    supported_formats=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
    max_file_size_mb=20,
    supports_web_monitoring=False,
    rate_limit_per_minute=150,
    cost_per_scan=0.02,
    monthly_quota=25000
)

# Plagiarism Detection for Text Content
COPYLEAKS_CONFIG = ProtectionAPIConfig(
    service_name="copyleaks",
    service_type=ProtectionServiceType.COPYRIGHT_DETECTION,
    base_url="https://api.copyleaks.com",
    api_version="v3",
    api_key=os.getenv("COPYLEAKS_API_KEY"),
    supported_content_types=[ContentType.TEXT, ContentType.DOCUMENT],
    detection_accuracy=0.93,
    processing_time_seconds=45,
    supports_batch_processing=True,
    supported_formats=["txt", "pdf", "docx", "html", "rtf"],
    max_file_size_mb=10,
    supports_web_monitoring=True,
    monitoring_frequency_hours=24,
    rate_limit_per_minute=40,
    cost_per_scan=0.03,
    monthly_quota=15000
)

# DMCA Takedown Service
DMCA_FORCE_CONFIG = ProtectionAPIConfig(
    service_name="dmca_force",
    service_type=ProtectionServiceType.DMCA_TAKEDOWN,
    base_url="https://api.dmca.com",
    api_version="v1",
    api_key=os.getenv("DMCA_FORCE_API_KEY"),
    supported_content_types=[
        ContentType.AUDIO, ContentType.VIDEO, 
        ContentType.IMAGE, ContentType.TEXT
    ],
    processing_time_seconds=86400,  # 24 hours average
    supports_batch_processing=True,
    supported_platforms=[
        "youtube", "facebook", "instagram", "tiktok", "twitter", "linkedin",
        "pinterest", "reddit", "tumblr", "snapchat", "discord"
    ],
    rate_limit_per_minute=10,  # Lower due to legal nature
    cost_per_scan=5.00,  # Higher cost for legal services
    monthly_quota=1000
)

# Blockchain-based Copyright Protection
KODAK_ONE_CONFIG = ProtectionAPIConfig(
    service_name="kodak_one",
    service_type=ProtectionServiceType.BLOCKCHAIN_PROTECTION,
    base_url="https://api.kodakone.com",
    api_version="v1",
    api_key=os.getenv("KODAK_ONE_API_KEY"),
    supported_content_types=[
        ContentType.IMAGE, ContentType.VIDEO, 
        ContentType.AUDIO, ContentType.DOCUMENT
    ],
    detection_accuracy=0.99,  # Blockchain immutability
    processing_time_seconds=300,  # Blockchain confirmation time
    supports_web_monitoring=True,
    monitoring_frequency_hours=6,
    supported_formats=["jpg", "png", "mp4", "mov", "mp3", "pdf"],
    max_file_size_mb=1000,
    rate_limit_per_minute=20,
    cost_per_fingerprint=0.50,  # Higher for blockchain storage
    monthly_quota=5000
)

# Custom AI Fingerprinting Service
CUSTOM_FINGERPRINT_CONFIG = ProtectionAPIConfig(
    service_name="custom_fingerprint",
    service_type=ProtectionServiceType.FINGERPRINTING,
    base_url="https://api.ia-influencer.com/fingerprint",
    api_version="v1",
    api_key=os.getenv("CUSTOM_FINGERPRINT_API_KEY"),
    supported_content_types=[
        ContentType.AUDIO, ContentType.VIDEO,
        ContentType.IMAGE, ContentType.TEXT
    ],
    detection_accuracy=0.97,
    processing_time_seconds=20,
    supports_real_time=True,
    supports_batch_processing=True,
    supported_formats=[
        "mp3", "wav", "flac", "aac", "ogg",  # Audio
        "mp4", "avi", "mov", "mkv", "webm",  # Video
        "jpg", "png", "gif", "webp", "svg",  # Image
        "txt", "md", "html", "pdf"           # Text
    ],
    max_file_size_mb=500,
    max_batch_size=50,
    supports_web_monitoring=True,
    monitoring_frequency_hours=1,
    supported_platforms=[
        "youtube", "instagram", "tiktok", "facebook", "twitter",
        "soundcloud", "spotify", "apple_music", "amazon_music"
    ],
    rate_limit_per_minute=200,
    cost_per_fingerprint=0.005,
    monthly_quota=1000000,
    environments={
        "development": {
            "base_url": "http://localhost:8000/api/fingerprint",
            "monthly_quota": 10000
        },
        "staging": {
            "base_url": "https://staging-api.ia-influencer.com/fingerprint",
            "monthly_quota": 50000
        }
    }
)

# Web Monitoring Service
WEB_MONITOR_CONFIG = ProtectionAPIConfig(
    service_name="web_monitor",
    service_type=ProtectionServiceType.CONTENT_MONITORING,
    base_url="https://api.ia-influencer.com/monitor",
    api_version="v1",
    api_key=os.getenv("WEB_MONITOR_API_KEY"),
    supported_content_types=[
        ContentType.AUDIO, ContentType.VIDEO,
        ContentType.IMAGE, ContentType.TEXT
    ],
    processing_time_seconds=600,  # 10 minutes scan cycle
    supports_real_time=True,
    supports_web_monitoring=True,
    monitoring_frequency_hours=1,
    supported_platforms=[
        "youtube", "instagram", "tiktok", "facebook", "twitter", "linkedin",
        "pinterest", "reddit", "tumblr", "soundcloud", "bandcamp", "spotify"
    ],
    rate_limit_per_minute=100,
    cost_per_scan=0.01,
    monthly_quota=500000,
    environments={
        "development": {
            "base_url": "http://localhost:8000/api/monitor",
            "monitoring_frequency_hours": 24,
            "monthly_quota": 1000
        },
        "staging": {
            "base_url": "https://staging-api.ia-influencer.com/monitor",
            "monitoring_frequency_hours": 6,
            "monthly_quota": 10000
        }
    }
)

# Protection configurations registry
PROTECTION_CONFIGS: Dict[str, ProtectionAPIConfig] = {
    "chromaprint": CHROMAPRINT_CONFIG,
    "content_id": CONTENT_ID_CONFIG,
    "audible_magic": AUDIBLE_MAGIC_CONFIG,
    "digimarc": DIGIMARC_CONFIG,
    "tineye": TINEYE_CONFIG,
    "copyleaks": COPYLEAKS_CONFIG,
    "dmca_force": DMCA_FORCE_CONFIG,
    "kodak_one": KODAK_ONE_CONFIG,
    "custom_fingerprint": CUSTOM_FINGERPRINT_CONFIG,
    "web_monitor": WEB_MONITOR_CONFIG
}

def get_protection_config(service: str) -> Optional[ProtectionAPIConfig]:
    """Get protection service configuration by name"""



    return PROTECTION_CONFIGS.get(service.lower())

def get_services_by_type(service_type: ProtectionServiceType) -> List[ProtectionAPIConfig]:
    """Get all protection services of specific type"""



    return [config for config in PROTECTION_CONFIGS.values() 
            if config.service_type == service_type]

def get_services_by_content_type(content_type: ContentType) -> List[ProtectionAPIConfig]:
    """Get protection services supporting specific content type"""



    return [config for config in PROTECTION_CONFIGS.values() 
            if content_type in config.supported_content_types]

def get_real_time_services() -> List[ProtectionAPIConfig]:
    """Get services that support real-time processing"""



    return [config for config in PROTECTION_CONFIGS.values() 
            if config.supports_real_time]

def get_monitoring_services() -> List[ProtectionAPIConfig]:
    """Get services that support web monitoring"""



    return [config for config in PROTECTION_CONFIGS.values() 
            if config.supports_web_monitoring]
