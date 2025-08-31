"""
Content Protection Configuration Module

Advanced copyright protection, watermarking, and rights management system
for multi-format content creators (musicians, bloggers, photographers, influencers, comedians).

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected intellectual property. Unauthorized use is prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import hashlib
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"


class ContentType(Enum):
    """Supported content types for protection"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    MULTIMEDIA = "multimedia"


class WatermarkType(Enum):
    """Types of watermarks"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    STEGANOGRAPHIC = "steganographic"
    DIGITAL_SIGNATURE = "digital_signature"
    BLOCKCHAIN = "blockchain"


class DetectionMethod(Enum):
    """Copyright detection methods"""
    HASH_MATCHING = "hash_matching"
    PERCEPTUAL_HASHING = "perceptual_hashing"
    FINGERPRINTING = "fingerprinting"
    NEURAL_MATCHING = "neural_matching"
    CONTENT_ID = "content_id"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"


class LicenseType(Enum):
    """Content license types"""
    ALL_RIGHTS_RESERVED = "all_rights_reserved"
    CREATIVE_COMMONS_BY = "cc_by"
    CREATIVE_COMMONS_BY_SA = "cc_by_sa"
    CREATIVE_COMMONS_BY_NC = "cc_by_nc"
    CREATIVE_COMMONS_BY_ND = "cc_by_nd"
    MIT = "mit"
    CUSTOM = "custom"
    COMMERCIAL = "commercial"
    ROYALTY_FREE = "royalty_free"


@dataclass
class WatermarkConfig:
    """Watermark configuration"""
    enabled: bool = True
    watermark_type: WatermarkType = WatermarkType.INVISIBLE
    intensity: float = 0.3  # 0.0 to 1.0
    position: str = "bottom_right"  # For visible watermarks
    text: str = "© Fahed Mlaiel - Unauthorized use prohibited"
    font_size: int = 12
    opacity: float = 0.5
    color: str = "#FFFFFF"
    logo_path: Optional[str] = None
    
    # Advanced watermark settings
    frequency_domain: bool = True  # For invisible watermarks
    redundancy_level: int = 3
    error_correction: bool = True
    payload_size: int = 64  # bits
    
    # Dynamic watermarking
    dynamic_positioning: bool = True
    rotation_angle: float = 0.0
    scale_factor: float = 1.0
    
    def validate(self) -> List[str]:
        """Validate watermark configuration"""
        issues = []
        if not 0.0 <= self.intensity <= 1.0:
            issues.append("Intensity must be between 0.0 and 1.0")
        if not 0.0 <= self.opacity <= 1.0:
            issues.append("Opacity must be between 0.0 and 1.0")
        if self.logo_path and not Path(self.logo_path).exists():
            issues.append(f"Logo file not found: {self.logo_path}")
        return issues


@dataclass
class CopyrightDetectionConfig:
    """Copyright detection configuration"""
    enabled: bool = True
    detection_methods: List[DetectionMethod] = field(default_factory=lambda: [
        DetectionMethod.PERCEPTUAL_HASHING,
        DetectionMethod.NEURAL_MATCHING,
        DetectionMethod.CONTENT_ID
    ])
    
    # Detection thresholds
    similarity_threshold: float = 0.85
    partial_match_threshold: float = 0.70
    suspicious_threshold: float = 0.60
    
    # Content database settings
    reference_database_enabled: bool = True
    external_databases: List[str] = field(default_factory=lambda: [
        "youtube_content_id",
        "soundcloud_copyright",
        "instagram_rights_manager",
        "tiktok_copyright"
    ])
    
    # Real-time monitoring
    real_time_monitoring: bool = True
    monitoring_frequency: int = 3600  # seconds
    alert_threshold: int = 5  # number of matches to trigger alert
    
    # Advanced detection
    deep_learning_models: List[str] = field(default_factory=lambda: [
        "copyright_bert",
        "visual_similarity_cnn",
        "audio_fingerprint_rnn"
    ])
    
    # False positive reduction
    whitelist_sources: List[str] = field(default_factory=list)
    trusted_creators: List[str] = field(default_factory=list)
    fair_use_detection: bool = True


@dataclass
class RightsManagementConfig:
    """Rights management configuration"""
    enabled: bool = True
    default_license: LicenseType = LicenseType.ALL_RIGHTS_RESERVED
    
    # Creator information
    creator_name: str = "Fahed Mlaiel"
    creator_email: str = "mlaiel@live.de"
    creator_id: str = "fahed_mlaiel_creator_id"
    organization: str = "IA Influencer Agent Platform"
    
    # Rights tracking
    creation_timestamp: bool = True
    modification_tracking: bool = True
    usage_analytics: bool = True
    geographic_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Licensing terms
    commercial_use_allowed: bool = False
    derivative_works_allowed: bool = False
    attribution_required: bool = True
    share_alike_required: bool = False
    
    # Monetization settings
    royalty_percentage: float = 0.0
    minimum_payment: float = 0.0
    payment_threshold: float = 100.0
    currency: str = "EUR"
    
    # Collaboration rights
    collaboration_allowed: bool = True
    collaboration_approval_required: bool = True
    revenue_split_default: float = 0.5
    
    # Contract automation
    smart_contracts_enabled: bool = True
    blockchain_registration: bool = True
    automated_licensing: bool = True


@dataclass
class AntiPiracyConfig:
    """Anti-piracy configuration"""
    enabled: bool = True
    
    # Detection strategies
    web_crawling_enabled: bool = True
    social_media_monitoring: bool = True
    p2p_network_monitoring: bool = True
    marketplace_monitoring: bool = True
    
    # Monitoring platforms
    platforms_to_monitor: List[str] = field(default_factory=lambda: [
        "youtube", "instagram", "tiktok", "facebook", "twitter",
        "soundcloud", "spotify", "apple_music", "bandcamp",
        "flickr", "unsplash", "shutterstock", "getty_images",
        "etsy", "amazon", "ebay"
    ])
    
    # Response actions
    automated_takedown: bool = True
    dmca_notices_enabled: bool = True
    legal_action_threshold: int = 10
    
    # Tracking and evidence
    screenshot_evidence: bool = True
    metadata_collection: bool = True
    chain_of_custody: bool = True
    legal_documentation: bool = True
    
    # Prevention measures
    content_encryption: bool = True
    access_control: bool = True
    time_limited_access: bool = False
    geographic_blocking: bool = False


@dataclass
class ComplianceConfig:
    """Legal compliance configuration"""
    enabled: bool = True
    
    # Jurisdictions
    primary_jurisdiction: str = "DE"  # Germany
    additional_jurisdictions: List[str] = field(default_factory=lambda: ["EU", "US", "UK"])
    
    # Regulatory compliance
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    coppa_compliance: bool = True
    dmca_compliance: bool = True
    
    # Data protection
    personal_data_protection: bool = True
    anonymization_enabled: bool = True
    consent_management: bool = True
    data_retention_days: int = 2555  # 7 years
    
    # Audit and reporting
    audit_logging: bool = True
    compliance_reporting: bool = True
    incident_reporting: bool = True
    
    # Terms and policies
    terms_of_service_url: str = ""
    privacy_policy_url: str = ""
    copyright_policy_url: str = ""
    acceptable_use_policy_url: str = ""


@dataclass
class ProtectionConfig:
    """Main content protection configuration"""
    
    # Core protection settings
    protection_level: ProtectionLevel = ProtectionLevel.ENTERPRISE
    enabled_content_types: List[ContentType] = field(default_factory=lambda: [
        ContentType.TEXT, ContentType.IMAGE, ContentType.AUDIO, ContentType.VIDEO
    ])
    
    # Sub-configurations
    watermark: WatermarkConfig = field(default_factory=WatermarkConfig)
    copyright_detection: CopyrightDetectionConfig = field(default_factory=CopyrightDetectionConfig)
    rights_management: RightsManagementConfig = field(default_factory=RightsManagementConfig)
    anti_piracy: AntiPiracyConfig = field(default_factory=AntiPiracyConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    
    # Advanced features
    ai_powered_protection: bool = True
    blockchain_integration: bool = True
    quantum_encryption: bool = False  # Future feature
    
    # Performance settings
    background_processing: bool = True
    batch_processing: bool = True
    parallel_processing: bool = True
    max_concurrent_jobs: int = 10
    
    # Integration settings
    api_endpoints: Dict[str, str] = field(default_factory=dict)
    webhook_urls: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack", "discord"])
    
    # Emergency settings
    emergency_lockdown: bool = False
    emergency_contacts: List[str] = field(default_factory=lambda: ["mlaiel@live.de"])
    incident_response_plan: str = "auto_block_and_notify"

    def __post_init__(self):
        """Initialize default configurations"""
        if not self.api_endpoints:
            self._setup_default_api_endpoints()
        if not self.webhook_urls:
            self._setup_default_webhooks()

    def _setup_default_api_endpoints(self):
        """Setup default API endpoints"""
        self.api_endpoints = {
            "copyright_check": "https://api.ia-influencer.com/v1/protection/copyright/check",
            "watermark_apply": "https://api.ia-influencer.com/v1/protection/watermark/apply",
            "rights_register": "https://api.ia-influencer.com/v1/protection/rights/register",
            "piracy_report": "https://api.ia-influencer.com/v1/protection/piracy/report",
            "takedown_request": "https://api.ia-influencer.com/v1/protection/takedown/request"
        }

    def _setup_default_webhooks(self):
        """Setup default webhook URLs"""
        self.webhook_urls = {
            "copyright_violation": "https://api.ia-influencer.com/webhooks/copyright_violation",
            "piracy_detected": "https://api.ia-influencer.com/webhooks/piracy_detected",
            "rights_claimed": "https://api.ia-influencer.com/webhooks/rights_claimed",
            "takedown_completed": "https://api.ia-influencer.com/webhooks/takedown_completed"
        }

    def generate_content_fingerprint(self, content: Union[str, bytes], content_type: ContentType) -> str:
        """Generate unique fingerprint for content"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Create multi-hash fingerprint
        sha256_hash = hashlib.sha256(content).hexdigest()
        md5_hash = hashlib.md5(content).hexdigest()
        
        timestamp = datetime.now().isoformat()
        creator_id = self.rights_management.creator_id
        
        fingerprint_data = f"{sha256_hash}:{md5_hash}:{creator_id}:{timestamp}:{content_type.value}"
        
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    def register_content(self, content_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Register content for protection"""
        registration_record = {
            "content_id": content_id,
            "creator_id": self.rights_management.creator_id,
            "creator_name": self.rights_management.creator_name,
            "creator_email": self.rights_management.creator_email,
            "registration_timestamp": datetime.now().isoformat(),
            "license_type": self.rights_management.default_license.value,
            "protection_level": self.protection_level.value,
            "metadata": metadata,
            "fingerprint": self.generate_content_fingerprint(content_id, ContentType.TEXT),
            "blockchain_hash": None,  # To be implemented
            "rights_expires": None,  # For time-limited licenses
            "commercial_use_allowed": self.rights_management.commercial_use_allowed,
            "derivative_works_allowed": self.rights_management.derivative_works_allowed,
            "attribution_required": self.rights_management.attribution_required
        }
        
        logger.info(f"Content registered for protection: {content_id}")
        return registration_record

    def check_usage_rights(self, content_id: str, requester_id: str, usage_type: str) -> Dict[str, Any]:
        """Check if usage is allowed for specific content"""
        # This would integrate with the rights management database
        usage_check_result = {
            "content_id": content_id,
            "requester_id": requester_id,
            "usage_type": usage_type,
            "allowed": False,
            "requires_payment": False,
            "requires_attribution": self.rights_management.attribution_required,
            "license_fee": 0.0,
            "restrictions": [],
            "expires_at": None
        }
        
        # Basic logic - would be expanded with database integration
        if usage_type == "personal_use" and not self.rights_management.commercial_use_allowed:
            usage_check_result["allowed"] = True
        elif usage_type == "commercial_use" and self.rights_management.commercial_use_allowed:
            usage_check_result["allowed"] = True
            usage_check_result["requires_payment"] = True
            usage_check_result["license_fee"] = 50.0  # Example fee
        
        return usage_check_result

    def validate_configuration(self) -> List[str]:
        """Validate protection configuration"""
        issues = []
        
        # Validate watermark configuration
        issues.extend(self.watermark.validate())
        
        # Check required fields
        if not self.rights_management.creator_name:
            issues.append("Creator name is required")
        if not self.rights_management.creator_email:
            issues.append("Creator email is required")
        
        # Validate thresholds
        if not 0.0 <= self.copyright_detection.similarity_threshold <= 1.0:
            issues.append("Similarity threshold must be between 0.0 and 1.0")
        
        # Check API endpoints
        for endpoint_name, url in self.api_endpoints.items():
            if not url.startswith(('http://', 'https://')):
                issues.append(f"Invalid API endpoint URL for {endpoint_name}: {url}")
        
        return issues

    def get_protection_summary(self) -> Dict[str, Any]:
        """Get summary of protection configuration"""



        return {
            "protection_level": self.protection_level.value,
            "enabled_content_types": [ct.value for ct in self.enabled_content_types],
            "watermark_enabled": self.watermark.enabled,
            "copyright_detection_enabled": self.copyright_detection.enabled,
            "anti_piracy_enabled": self.anti_piracy.enabled,
            "blockchain_integration": self.blockchain_integration,
            "ai_powered_protection": self.ai_powered_protection,
            "creator": {
                "name": self.rights_management.creator_name,
                "email": self.rights_management.creator_email,
                "id": self.rights_management.creator_id
            },
            "compliance": {
                "gdpr": self.compliance.gdpr_compliance,
                "dmca": self.compliance.dmca_compliance,
                "jurisdiction": self.compliance.primary_jurisdiction
            }
        }

    @classmethod
    def from_env(cls) -> 'ProtectionConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Load basic settings
        config.protection_level = ProtectionLevel(os.getenv("PROTECTION_LEVEL", "enterprise"))
        config.ai_powered_protection = os.getenv("AI_PROTECTION", "true").lower() == "true"
        config.blockchain_integration = os.getenv("BLOCKCHAIN_PROTECTION", "true").lower() == "true"
        
        # Load watermark settings
        config.watermark.enabled = os.getenv("WATERMARK_ENABLED", "true").lower() == "true"
        config.watermark.intensity = float(os.getenv("WATERMARK_INTENSITY", "0.3"))
        config.watermark.text = os.getenv("WATERMARK_TEXT", config.watermark.text)
        
        # Load copyright detection settings
        config.copyright_detection.enabled = os.getenv("COPYRIGHT_DETECTION", "true").lower() == "true"
        config.copyright_detection.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
        
        # Load rights management settings
        config.rights_management.creator_name = os.getenv("CREATOR_NAME", "Fahed Mlaiel")
        config.rights_management.creator_email = os.getenv("CREATOR_EMAIL", "mlaiel@live.de")
        config.rights_management.creator_id = os.getenv("CREATOR_ID", "fahed_mlaiel_creator_id")
        
        # Load compliance settings
        config.compliance.primary_jurisdiction = os.getenv("PRIMARY_JURISDICTION", "DE")
        config.compliance.gdpr_compliance = os.getenv("GDPR_COMPLIANCE", "true").lower() == "true"
        
        return config

    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""



        try:
            data = asdict(self)
            # Convert enums to strings for JSON serialization
            self._convert_enums_to_strings(data)
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Protection configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to file {config_file}: {e}")

    def _convert_enums_to_strings(self, data: Dict[str, Any]):
        """Convert enum values to strings for JSON serialization"""
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'value'):  # Enum
                    data[key] = value.value
                elif isinstance(value, list):
                    data[key] = [item.value if hasattr(item, 'value') else item for item in value]
                elif isinstance(value, dict):
                    self._convert_enums_to_strings(value)

    @classmethod
    def load_from_file(cls, config_file: str) -> 'ProtectionConfig':
        """Load configuration from JSON file"""



        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Convert string enums back to enum objects
            # This would need more sophisticated handling for nested enums
            
            config = cls()
            # Update configuration with loaded data
            # Implementation would depend on the specific structure
            
            logger.info(f"Protection configuration loaded from {config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file {config_file}: {e}")
            return cls.from_env()


# Global configuration instance
protection_config = ProtectionConfig.from_env()
