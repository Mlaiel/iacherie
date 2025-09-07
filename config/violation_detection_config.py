"""
Violation Detection Configuration - Enterprise Configuration Management
Enterprise configuration for violation detection and DMCA compliance business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def Field(**kwargs):
        return kwargs.get('default_factory', kwargs.get('default'))()
    
    def validator(field_name):
        def decorator(func):
            return func
        return decorator


class ViolationType(str, Enum):
    """Types of content violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    PLAGIARISM = "plagiarism"
    FAIR_USE_ABUSE = "fair_use_abuse"
    DMCA_VIOLATION = "dmca_violation"
    LICENSING_BREACH = "licensing_breach"
    REVENUE_THEFT = "revenue_theft"


class MonitoringPlatform(str, Enum):
    """Platforms for violation monitoring"""
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class DetectionMethod(str, Enum):
    """Violation detection methods"""
    FINGERPRINT_MATCHING = "fingerprint_matching"
    HASH_COMPARISON = "hash_comparison"
    AI_CONTENT_ANALYSIS = "ai_content_analysis"
    METADATA_ANALYSIS = "metadata_analysis"
    VISUAL_RECOGNITION = "visual_recognition"
    AUDIO_RECOGNITION = "audio_recognition"
    TEXT_SIMILARITY = "text_similarity"
    PATTERN_RECOGNITION = "pattern_recognition"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    CROWDSOURCE_REPORTING = "crowdsource_reporting"


class ResponseAction(str, Enum):
    """Automated response actions"""
    AUTOMATED_TAKEDOWN = "automated_takedown"
    DMCA_NOTICE = "dmca_notice"
    CEASE_DESIST = "cease_desist"
    CONTENT_BLOCKING = "content_blocking"
    ACCOUNT_SUSPENSION = "account_suspension"
    REVENUE_CLAIM = "revenue_claim"
    LEGAL_NOTICE = "legal_notice"
    WARNING_MESSAGE = "warning_message"
    ESCALATION = "escalation"
    MANUAL_REVIEW = "manual_review"


class ViolationSeverity(str, Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DetectionFrequency(str, Enum):
    """Detection monitoring frequency"""
    REAL_TIME = "real_time"
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class PlatformMonitoringConfig:
    """Platform-specific monitoring configuration"""
    platform: MonitoringPlatform
    enabled: bool
    detection_methods: List[DetectionMethod]
    monitoring_frequency: DetectionFrequency
    api_credentials: Dict[str, str]
    rate_limits: Dict[str, int]
    automated_response: bool
    response_actions: List[ResponseAction]
    escalation_threshold: int


@dataclass
class DetectionAlgorithmConfig:
    """Detection algorithm configuration"""
    method: DetectionMethod
    accuracy_threshold: float
    false_positive_rate: float
    processing_speed_ms: int
    resource_requirements: Dict[str, Any]
    model_version: str
    enabled: bool
    fallback_methods: List[DetectionMethod]


@dataclass
class ViolationResponse:
    """Violation response configuration"""
    violation_type: ViolationType
    severity: ViolationSeverity
    automatic_response: bool
    response_actions: List[ResponseAction]
    escalation_timeline: List[int]  # Hours for escalation
    legal_review_required: bool
    notification_settings: Dict[str, bool]


@dataclass
class DMCAConfiguration:
    """DMCA-specific configuration"""
    auto_filing: bool
    counter_notification_handling: bool
    repeat_infringer_tracking: bool
    safe_harbor_compliance: bool
    takedown_processing_time_hours: int
    counter_claim_response_time_hours: int
    legal_review_threshold: ViolationSeverity
    automated_restoration: bool


class ViolationDetectionSettings(BaseSettings):
    """Violation detection configuration settings"""
    
    # Platform Monitoring Configuration
    platform_monitoring: Dict[str, PlatformMonitoringConfig] = Field(
        default_factory=lambda: {
            "youtube": PlatformMonitoringConfig(
                platform=MonitoringPlatform.YOUTUBE,
                enabled=True,
                detection_methods=[
                    DetectionMethod.FINGERPRINT_MATCHING,
                    DetectionMethod.AI_CONTENT_ANALYSIS,
                    DetectionMethod.AUDIO_RECOGNITION
                ],
                monitoring_frequency=DetectionFrequency.REAL_TIME,
                api_credentials={"api_key": "", "client_id": "", "client_secret": ""},
                rate_limits={"requests_per_minute": 100, "requests_per_day": 10000},
                automated_response=True,
                response_actions=[
                    ResponseAction.REVENUE_CLAIM,
                    ResponseAction.DMCA_NOTICE,
                    ResponseAction.AUTOMATED_TAKEDOWN
                ],
                escalation_threshold=3
            ),
            "facebook": PlatformMonitoringConfig(
                platform=MonitoringPlatform.FACEBOOK,
                enabled=True,
                detection_methods=[
                    DetectionMethod.VISUAL_RECOGNITION,
                    DetectionMethod.AI_CONTENT_ANALYSIS,
                    DetectionMethod.HASH_COMPARISON
                ],
                monitoring_frequency=DetectionFrequency.EVERY_5_MINUTES,
                api_credentials={"app_id": "", "app_secret": "", "access_token": ""},
                rate_limits={"requests_per_hour": 200, "requests_per_day": 5000},
                automated_response=True,
                response_actions=[
                    ResponseAction.CONTENT_BLOCKING,
                    ResponseAction.DMCA_NOTICE
                ],
                escalation_threshold=2
            ),
            "instagram": PlatformMonitoringConfig(
                platform=MonitoringPlatform.INSTAGRAM,
                enabled=True,
                detection_methods=[
                    DetectionMethod.VISUAL_RECOGNITION,
                    DetectionMethod.HASH_COMPARISON,
                    DetectionMethod.METADATA_ANALYSIS
                ],
                monitoring_frequency=DetectionFrequency.EVERY_15_MINUTES,
                api_credentials={"access_token": "", "app_id": "", "app_secret": ""},
                rate_limits={"requests_per_hour": 150, "requests_per_day": 3000},
                automated_response=True,
                response_actions=[
                    ResponseAction.CONTENT_BLOCKING,
                    ResponseAction.WARNING_MESSAGE
                ],
                escalation_threshold=3
            ),
            "tiktok": PlatformMonitoringConfig(
                platform=MonitoringPlatform.TIKTOK,
                enabled=True,
                detection_methods=[
                    DetectionMethod.FINGERPRINT_MATCHING,
                    DetectionMethod.AI_CONTENT_ANALYSIS,
                    DetectionMethod.AUDIO_RECOGNITION
                ],
                monitoring_frequency=DetectionFrequency.REAL_TIME,
                api_credentials={"client_key": "", "client_secret": ""},
                rate_limits={"requests_per_minute": 50, "requests_per_day": 2000},
                automated_response=True,
                response_actions=[
                    ResponseAction.AUTOMATED_TAKEDOWN,
                    ResponseAction.DMCA_NOTICE
                ],
                escalation_threshold=2
            ),
            "twitter": PlatformMonitoringConfig(
                platform=MonitoringPlatform.TWITTER,
                enabled=True,
                detection_methods=[
                    DetectionMethod.TEXT_SIMILARITY,
                    DetectionMethod.HASH_COMPARISON,
                    DetectionMethod.BEHAVIORAL_ANALYSIS
                ],
                monitoring_frequency=DetectionFrequency.EVERY_MINUTE,
                api_credentials={"api_key": "", "api_secret": "", "bearer_token": ""},
                rate_limits={"requests_per_minute": 300, "requests_per_day": 50000},
                automated_response=True,
                response_actions=[
                    ResponseAction.WARNING_MESSAGE,
                    ResponseAction.DMCA_NOTICE
                ],
                escalation_threshold=4
            )
        }
    )
    
    # Detection Algorithm Configuration
    detection_algorithms: Dict[str, DetectionAlgorithmConfig] = Field(
        default_factory=lambda: {
            "fingerprint_matching": DetectionAlgorithmConfig(
                method=DetectionMethod.FINGERPRINT_MATCHING,
                accuracy_threshold=0.95,
                false_positive_rate=0.001,
                processing_speed_ms=500,
                resource_requirements={
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "storage_gb": 100
                },
                model_version="v2.1",
                enabled=True,
                fallback_methods=[DetectionMethod.HASH_COMPARISON]
            ),
            "ai_content_analysis": DetectionAlgorithmConfig(
                method=DetectionMethod.AI_CONTENT_ANALYSIS,
                accuracy_threshold=0.92,
                false_positive_rate=0.005,
                processing_speed_ms=2000,
                resource_requirements={
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "gpu_memory_gb": 4
                },
                model_version="v3.0",
                enabled=True,
                fallback_methods=[DetectionMethod.PATTERN_RECOGNITION]
            ),
            "visual_recognition": DetectionAlgorithmConfig(
                method=DetectionMethod.VISUAL_RECOGNITION,
                accuracy_threshold=0.90,
                false_positive_rate=0.01,
                processing_speed_ms=1500,
                resource_requirements={
                    "cpu_cores": 6,
                    "memory_gb": 12,
                    "gpu_memory_gb": 2
                },
                model_version="v2.5",
                enabled=True,
                fallback_methods=[DetectionMethod.HASH_COMPARISON]
            ),
            "audio_recognition": DetectionAlgorithmConfig(
                method=DetectionMethod.AUDIO_RECOGNITION,
                accuracy_threshold=0.94,
                false_positive_rate=0.002,
                processing_speed_ms=3000,
                resource_requirements={
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "storage_gb": 50
                },
                model_version="v1.8",
                enabled=True,
                fallback_methods=[DetectionMethod.FINGERPRINT_MATCHING]
            ),
            "text_similarity": DetectionAlgorithmConfig(
                method=DetectionMethod.TEXT_SIMILARITY,
                accuracy_threshold=0.88,
                false_positive_rate=0.02,
                processing_speed_ms=100,
                resource_requirements={
                    "cpu_cores": 2,
                    "memory_gb": 4,
                    "storage_gb": 10
                },
                model_version="v1.5",
                enabled=True,
                fallback_methods=[DetectionMethod.PATTERN_RECOGNITION]
            )
        }
    )
    
    # Violation Response Configuration
    violation_responses: Dict[str, ViolationResponse] = Field(
        default_factory=lambda: {
            "copyright_infringement": ViolationResponse(
                violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
                severity=ViolationSeverity.HIGH,
                automatic_response=True,
                response_actions=[
                    ResponseAction.DMCA_NOTICE,
                    ResponseAction.AUTOMATED_TAKEDOWN,
                    ResponseAction.REVENUE_CLAIM
                ],
                escalation_timeline=[1, 24, 72],  # Hours
                legal_review_required=True,
                notification_settings={
                    "email_alert": True,
                    "sms_alert": True,
                    "dashboard_notification": True,
                    "legal_team_notification": True
                }
            ),
            "unauthorized_use": ViolationResponse(
                violation_type=ViolationType.UNAUTHORIZED_USE,
                severity=ViolationSeverity.MEDIUM,
                automatic_response=True,
                response_actions=[
                    ResponseAction.WARNING_MESSAGE,
                    ResponseAction.CEASE_DESIST,
                    ResponseAction.CONTENT_BLOCKING
                ],
                escalation_timeline=[6, 48, 168],  # Hours
                legal_review_required=False,
                notification_settings={
                    "email_alert": True,
                    "dashboard_notification": True
                }
            ),
            "plagiarism": ViolationResponse(
                violation_type=ViolationType.PLAGIARISM,
                severity=ViolationSeverity.MEDIUM,
                automatic_response=True,
                response_actions=[
                    ResponseAction.WARNING_MESSAGE,
                    ResponseAction.DMCA_NOTICE
                ],
                escalation_timeline=[12, 72, 336],  # Hours
                legal_review_required=False,
                notification_settings={
                    "email_alert": True,
                    "dashboard_notification": True
                }
            ),
            "revenue_theft": ViolationResponse(
                violation_type=ViolationType.REVENUE_THEFT,
                severity=ViolationSeverity.CRITICAL,
                automatic_response=True,
                response_actions=[
                    ResponseAction.REVENUE_CLAIM,
                    ResponseAction.AUTOMATED_TAKEDOWN,
                    ResponseAction.LEGAL_NOTICE,
                    ResponseAction.ACCOUNT_SUSPENSION
                ],
                escalation_timeline=[1, 6, 24],  # Hours
                legal_review_required=True,
                notification_settings={
                    "email_alert": True,
                    "sms_alert": True,
                    "dashboard_notification": True,
                    "legal_team_notification": True,
                    "executive_notification": True
                }
            )
        }
    )
    
    # DMCA Configuration
    dmca_configuration: DMCAConfiguration = Field(
        default_factory=lambda: DMCAConfiguration(
            auto_filing=True,
            counter_notification_handling=True,
            repeat_infringer_tracking=True,
            safe_harbor_compliance=True,
            takedown_processing_time_hours=24,
            counter_claim_response_time_hours=72,
            legal_review_threshold=ViolationSeverity.HIGH,
            automated_restoration=False  # Requires manual review
        )
    )
    
    # Detection Performance Settings
    detection_performance: Dict[str, Any] = Field(
        default_factory=lambda: {
            "parallel_processing": True,
            "batch_processing": True,
            "real_time_alerts": True,
            "performance_monitoring": True,
            "accuracy_tracking": True,
            "false_positive_analysis": True,
            "speed_optimization": True,
            "resource_optimization": True
        }
    )
    
    # Global Detection Settings
    global_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "detection_enabled": True,
            "automated_response_enabled": True,
            "legal_automation_enabled": True,
            "cross_platform_correlation": True,
            "historical_analysis": True,
            "predictive_detection": True,
            "machine_learning_enabled": True,
            "continuous_improvement": True
        }
    )
    
    # Security and Privacy Settings
    security_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "encrypted_storage": True,
            "secure_api_communications": True,
            "access_control": "rbac",
            "audit_logging": True,
            "data_anonymization": True,
            "gdpr_compliance": True,
            "data_retention_days": 365,
            "secure_deletion": True
        }
    )
    
    # Integration Settings
    integration_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "legal_system_integration": True,
            "payment_system_integration": True,
            "crm_integration": True,
            "analytics_integration": True,
            "notification_system_integration": True,
            "document_management_integration": True,
            "blockchain_integration": True,
            "api_webhook_support": True
        }
    )
    
    # Monitoring and Analytics
    monitoring_analytics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "detection_metrics": True,
            "response_effectiveness": True,
            "platform_coverage": True,
            "cost_analysis": True,
            "roi_tracking": True,
            "trend_analysis": True,
            "predictive_analytics": True,
            "dashboard_reporting": True
        }
    )
    
    class Config:
        env_prefix = "VIOLATION_DETECTION_"
        case_sensitive = False
        extra = "allow"
    
    def get_platform_config(self, platform: str) -> Optional[PlatformMonitoringConfig]:
        """Get platform monitoring configuration"""
        return self.platform_monitoring.get(platform)
    
    def get_detection_algorithm(self, method: str) -> Optional[DetectionAlgorithmConfig]:
        """Get detection algorithm configuration"""
        return self.detection_algorithms.get(method)
    
    def get_violation_response(self, violation_type: str) -> Optional[ViolationResponse]:
        """Get violation response configuration"""
        return self.violation_responses.get(violation_type)
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if platform monitoring is enabled"""
        config = self.get_platform_config(platform)
        return config.enabled if config else False
    
    def is_algorithm_enabled(self, method: str) -> bool:
        """Check if detection algorithm is enabled"""
        config = self.get_detection_algorithm(method)
        return config.enabled if config else False
    
    def get_platform_detection_methods(self, platform: str) -> List[DetectionMethod]:
        """Get detection methods for a platform"""
        config = self.get_platform_config(platform)
        return config.detection_methods if config else []
    
    def get_automated_response_actions(self, violation_type: str) -> List[ResponseAction]:
        """Get automated response actions for violation type"""
        config = self.get_violation_response(violation_type)
        return config.response_actions if config and config.automatic_response else []
    
    def get_escalation_timeline(self, violation_type: str) -> List[int]:
        """Get escalation timeline for violation type"""
        config = self.get_violation_response(violation_type)
        return config.escalation_timeline if config else []
    
    def is_legal_review_required(self, violation_type: str) -> bool:
        """Check if legal review is required for violation type"""
        config = self.get_violation_response(violation_type)
        return config.legal_review_required if config else True
    
    def get_accuracy_threshold(self, method: str) -> float:
        """Get accuracy threshold for detection method"""
        config = self.get_detection_algorithm(method)
        return config.accuracy_threshold if config else 0.90
    
    def get_false_positive_rate(self, method: str) -> float:
        """Get false positive rate for detection method"""
        config = self.get_detection_algorithm(method)
        return config.false_positive_rate if config else 0.01
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete violation detection configuration"""
        errors = []
        
        # Validate platform configurations
        for platform, config in self.platform_monitoring.items():
            if config.enabled and not config.detection_methods:
                errors.append(f"Platform '{platform}' is enabled but has no detection methods")
            if config.escalation_threshold <= 0:
                errors.append(f"Platform '{platform}' has invalid escalation threshold")
        
        # Validate detection algorithms
        for method, config in self.detection_algorithms.items():
            if config.accuracy_threshold < 0 or config.accuracy_threshold > 1:
                errors.append(f"Detection method '{method}' has invalid accuracy threshold")
            if config.false_positive_rate < 0 or config.false_positive_rate > 1:
                errors.append(f"Detection method '{method}' has invalid false positive rate")
        
        # Validate violation responses
        for violation_type, config in self.violation_responses.items():
            if not config.response_actions:
                errors.append(f"Violation type '{violation_type}' has no response actions")
            if not config.escalation_timeline:
                errors.append(f"Violation type '{violation_type}' has no escalation timeline")
        
        # Validate DMCA configuration
        if self.dmca_configuration.takedown_processing_time_hours <= 0:
            errors.append("DMCA takedown processing time must be positive")
        if self.dmca_configuration.counter_claim_response_time_hours <= 0:
            errors.append("DMCA counter claim response time must be positive")
        
        return errors


# Global violation detection settings instance
violation_detection_settings = ViolationDetectionSettings()

__all__ = [
    "ViolationDetectionSettings",
    "violation_detection_settings",
    "ViolationType",
    "MonitoringPlatform",
    "DetectionMethod",
    "ResponseAction",
    "ViolationSeverity",
    "DetectionFrequency",
    "PlatformMonitoringConfig",
    "DetectionAlgorithmConfig",
    "ViolationResponse",
    "DMCAConfiguration"
]