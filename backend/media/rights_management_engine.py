"""Rights Management Engine - Comprehensive Digital Rights Management
================================================================

Unified digital rights management system providing intellectual property protection,
licensing management, piracy detection, and watermarking capabilities.

Consolidates:
- Piracy detection and monitoring (piracy_detection_system.py)
- Rights management and licensing (rights_management_system.py)  
- Watermarking and steganography (watermark_integration.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary rights management system contains advanced legal and security algorithms
and trade secrets belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Rights management algorithm extraction or appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import uuid
import hashlib
import hmac
import base64
import json
import struct
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from decimal import Decimal

# Graceful imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)

class RightsType(Enum):
    """Types of intellectual property rights"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    TRADE_SECRET = "trade_secret"
    PUBLICITY = "publicity"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    SYNCHRONIZATION = "synchronization"

class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EXTENDED = "extended"
    CUSTOM = "custom"

class UsageType(Enum):
    """Types of content usage"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    SOCIAL_MEDIA = "social_media"
    PRINT = "print"
    COMMERCIAL_USE = "commercial_use"
    EDUCATIONAL = "educational"
    RESEARCH = "research"

class PiracyThreatLevel(Enum):
    """Piracy threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CONFIRMED = "confirmed"

class MonitoringPlatform(Enum):
    """Platforms monitored for piracy"""
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    TORRENT_SITES = "torrent_sites"
    FILE_SHARING = "file_sharing"
    STREAMING_SITES = "streaming_sites"
    MARKETPLACE = "marketplace"
    BLOGS = "blogs"
    FORUMS = "forums"
    UNKNOWN = "unknown"

class DetectionMethod(Enum):
    """Piracy detection methods"""
    VISUAL_FINGERPRINT = "visual_fingerprint"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    PERCEPTUAL_HASH = "perceptual_hash"
    TEXT_SIMILARITY = "text_similarity"
    METADATA_MATCHING = "metadata_matching"
    REVERSE_IMAGE_SEARCH = "reverse_image_search"
    BRAND_MONITORING = "brand_monitoring"
    WATERMARK_DETECTION = "watermark_detection"
    AI_CONTENT_ANALYSIS = "ai_content_analysis"
    MANUAL_REPORT = "manual_report"

class WatermarkType(Enum):
    """Types of watermarks"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    STEGANOGRAPHIC = "steganographic"
    FREQUENCY_DOMAIN = "frequency_domain"
    SPATIAL_DOMAIN = "spatial_domain"

class WatermarkStrength(Enum):
    """Watermark embedding strength"""
    LOW = "low"           # Minimal impact on quality
    MEDIUM = "medium"     # Balanced protection/quality
    HIGH = "high"         # Maximum protection
    ADAPTIVE = "adaptive" # Dynamic based on content

@dataclass
class RightsConfig:
    """Rights management configuration"""
    rights_types: List[RightsType]
    license_type: LicenseType
    usage_permissions: List[UsageType]
    territory_restrictions: List[str] = field(default_factory=list)
    duration_days: Optional[int] = None
    royalty_rate: Decimal = Decimal('0.0')
    revenue_sharing: Dict[str, Decimal] = field(default_factory=dict)
    watermark_required: bool = True
    monitoring_enabled: bool = True

@dataclass
class License:
    """Digital license structure"""
    license_id: str
    content_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    usage_permissions: List[UsageType]
    territory_restrictions: List[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    royalty_rate: Decimal
    max_usage_count: Optional[int] = None
    current_usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PiracyIncident:
    """Piracy incident record"""
    incident_id: str
    content_id: str
    platform: MonitoringPlatform
    infringing_url: str
    detection_method: DetectionMethod
    threat_level: PiracyThreatLevel
    confidence_score: float
    similarity_score: float
    evidence: Dict[str, Any] = field(default_factory=dict)
    infringer_info: Dict[str, Any] = field(default_factory=dict)
    status: str = "detected"
    actions_taken: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

@dataclass
class WatermarkConfig:
    """Watermark configuration"""
    watermark_type: WatermarkType
    strength: WatermarkStrength
    text: str
    position: Tuple[int, int] = (10, 10)
    opacity: int = 128
    font_size: int = 24
    color: Tuple[int, int, int] = (255, 255, 255)
    rotation: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageRecord:
    """Content usage tracking record"""
    usage_id: str
    content_id: str
    license_id: str
    user_id: str
    usage_type: UsageType
    platform: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    revenue_generated: Decimal = Decimal('0.0')

@dataclass
class RoyaltyDistribution:
    """Royalty distribution record"""
    distribution_id: str
    content_id: str
    total_revenue: Decimal
    distribution_date: datetime
    distributions: Dict[str, Decimal] = field(default_factory=dict)  # user_id -> amount
    metadata: Dict[str, Any] = field(default_factory=dict)

class RightsManagementEngine:
    """Comprehensive digital rights management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize rights management engine"""
        self.config = config or {}
        self.licenses = {}
        self.piracy_incidents = {}
        self.usage_records = {}
        self.watermark_engines = {}
        self.detection_engines = {}
        self.monitoring_services = {}
        
        # Initialize subsystems
        self._initialize_watermark_engines()
        self._initialize_detection_engines()
        self._initialize_monitoring_services()
        
        logger.info("⚖️ Rights Management Engine initialized")
    
    def _initialize_watermark_engines(self):
        """Initialize watermark engines"""
        self.watermark_engines = {
            WatermarkType.VISIBLE: self._create_visible_watermark_engine(),
            WatermarkType.INVISIBLE: self._create_invisible_watermark_engine(),
            WatermarkType.STEGANOGRAPHIC: self._create_steganographic_engine(),
        }
        logger.info("Watermark engines initialized")
    
    def _initialize_detection_engines(self):
        """Initialize piracy detection engines"""
        self.detection_engines = {
            DetectionMethod.VISUAL_FINGERPRINT: self._create_visual_detection_engine(),
            DetectionMethod.AUDIO_FINGERPRINT: self._create_audio_detection_engine(),
            DetectionMethod.TEXT_SIMILARITY: self._create_text_detection_engine(),
            DetectionMethod.WATERMARK_DETECTION: self._create_watermark_detection_engine(),
        }
        logger.info("Detection engines initialized")
    
    def _initialize_monitoring_services(self):
        """Initialize platform monitoring services"""
        self.monitoring_services = {
            MonitoringPlatform.YOUTUBE: self._create_youtube_monitor(),
            MonitoringPlatform.INSTAGRAM: self._create_instagram_monitor(),
            MonitoringPlatform.FACEBOOK: self._create_facebook_monitor(),
        }
        logger.info("Monitoring services initialized")
    
    async def create_license(
        self, 
        content_id: str,
        licensee_id: str,
        licensor_id: str,
        rights_config: RightsConfig
    ) -> License:
        """Create a new digital license"""
        try:
            license_id = str(uuid.uuid4())
            
            # Calculate license duration
            valid_from = datetime.now(timezone.utc)
            valid_until = None
            if rights_config.duration_days:
                valid_until = valid_from + timedelta(days=rights_config.duration_days)
            
            # Create license
            license = License(
                license_id=license_id,
                content_id=content_id,
                licensee_id=licensee_id,
                licensor_id=licensor_id,
                license_type=rights_config.license_type,
                usage_permissions=rights_config.usage_permissions,
                territory_restrictions=rights_config.territory_restrictions,
                valid_from=valid_from,
                valid_until=valid_until,
                royalty_rate=rights_config.royalty_rate
            )
            
            # Store license
            self.licenses[license_id] = license
            
            logger.info(f"License created: {license_id} for content: {content_id}")
            return license
            
        except Exception as e:
            logger.error(f"License creation failed: {e}")
            raise
    
    async def validate_usage(
        self, 
        content_id: str,
        user_id: str,
        usage_type: UsageType,
        platform: str = "unknown"
    ) -> Dict[str, Any]:
        """Validate content usage against licenses"""
        try:
            # Find applicable licenses
            applicable_licenses = []
            for license in self.licenses.values():
                if (license.content_id == content_id and 
                    license.licensee_id == user_id and
                    usage_type in license.usage_permissions):
                    
                    # Check if license is valid
                    now = datetime.now(timezone.utc)
                    if (license.valid_from <= now and 
                        (license.valid_until is None or license.valid_until >= now)):
                        
                        # Check usage count
                        if (license.max_usage_count is None or 
                            license.current_usage_count < license.max_usage_count):
                            applicable_licenses.append(license)
            
            if not applicable_licenses:
                return {
                    "valid": False,
                    "reason": "No valid license found",
                    "requires_license": True
                }
            
            # Use the first applicable license
            license = applicable_licenses[0]
            
            # Record usage
            usage_record = await self._record_usage(
                content_id, license.license_id, user_id, usage_type, platform
            )
            
            # Update license usage count
            license.current_usage_count += 1
            
            return {
                "valid": True,
                "license_id": license.license_id,
                "usage_id": usage_record.usage_id,
                "royalty_rate": float(license.royalty_rate),
                "remaining_uses": (license.max_usage_count - license.current_usage_count 
                                 if license.max_usage_count else None)
            }
            
        except Exception as e:
            logger.error(f"Usage validation failed: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "error": True
            }
    
    async def apply_watermark(
        self, 
        content_data: Any,
        watermark_config: WatermarkConfig
    ) -> Dict[str, Any]:
        """Apply watermark to content"""
        try:
            engine = self.watermark_engines.get(watermark_config.watermark_type)
            if not engine:
                raise ValueError(f"Watermark engine {watermark_config.watermark_type.value} not available")
            
            watermarked_content = await engine(content_data, watermark_config)
            
            return {
                "success": True,
                "watermarked_content": watermarked_content,
                "watermark_type": watermark_config.watermark_type.value,
                "metadata": {
                    "text": watermark_config.text,
                    "strength": watermark_config.strength.value,
                    "applied_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Watermark application failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "watermarked_content": content_data
            }
    
    async def detect_piracy(
        self, 
        content_id: str,
        platforms: List[MonitoringPlatform] = None,
        detection_methods: List[DetectionMethod] = None
    ) -> List[PiracyIncident]:
        """Detect piracy across specified platforms"""
        if platforms is None:
            platforms = list(MonitoringPlatform)
        
        if detection_methods is None:
            detection_methods = [
                DetectionMethod.VISUAL_FINGERPRINT,
                DetectionMethod.WATERMARK_DETECTION
            ]
        
        try:
            incidents = []
            
            # Monitor each platform
            for platform in platforms:
                monitor = self.monitoring_services.get(platform)
                if monitor:
                    platform_incidents = await monitor(content_id, detection_methods)
                    incidents.extend(platform_incidents)
            
            # Store incidents
            for incident in incidents:
                self.piracy_incidents[incident.incident_id] = incident
            
            logger.info(f"Piracy detection completed for {content_id}: {len(incidents)} incidents found")
            return incidents
            
        except Exception as e:
            logger.error(f"Piracy detection failed: {e}")
            return []
    
    async def calculate_royalties(
        self, 
        content_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> RoyaltyDistribution:
        """Calculate and distribute royalties for a content piece"""
        try:
            # Get usage records for the period
            relevant_usage = []
            for usage in self.usage_records.values():
                if (usage.content_id == content_id and 
                    period_start <= usage.timestamp <= period_end):
                    relevant_usage.append(usage)
            
            # Calculate total revenue
            total_revenue = sum(usage.revenue_generated for usage in relevant_usage)
            
            # Get license information for revenue sharing
            revenue_shares = {}
            for usage in relevant_usage:
                license = self.licenses.get(usage.license_id)
                if license:
                    licensor_share = total_revenue * license.royalty_rate
                    revenue_shares[license.licensor_id] = revenue_shares.get(
                        license.licensor_id, Decimal('0.0')
                    ) + licensor_share
            
            # Create distribution record
            distribution = RoyaltyDistribution(
                distribution_id=str(uuid.uuid4()),
                content_id=content_id,
                total_revenue=total_revenue,
                distribution_date=datetime.now(timezone.utc),
                distributions=revenue_shares,
                metadata={
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "usage_count": len(relevant_usage)
                }
            )
            
            logger.info(f"Royalty distribution calculated for {content_id}: ${total_revenue}")
            return distribution
            
        except Exception as e:
            logger.error(f"Royalty calculation failed: {e}")
            raise
    
    async def generate_takedown_notice(
        self, 
        incident: PiracyIncident
    ) -> Dict[str, Any]:
        """Generate DMCA takedown notice for piracy incident"""
        try:
            notice = {
                "notice_id": str(uuid.uuid4()),
                "incident_id": incident.incident_id,
                "platform": incident.platform.value,
                "infringing_url": incident.infringing_url,
                "notice_type": "DMCA",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "content": {
                    "title": f"DMCA Takedown Notice - Content ID: {incident.content_id}",
                    "description": f"Unauthorized use of copyrighted content detected",
                    "evidence": incident.evidence,
                    "confidence_score": incident.confidence_score
                },
                "status": "generated"
            }
            
            # Mark incident as having takedown notice generated
            incident.actions_taken.append("takedown_notice_generated")
            
            logger.info(f"Takedown notice generated for incident: {incident.incident_id}")
            return notice
            
        except Exception as e:
            logger.error(f"Takedown notice generation failed: {e}")
            raise
    
    # Private helper methods
    
    async def _record_usage(
        self, 
        content_id: str, 
        license_id: str, 
        user_id: str, 
        usage_type: UsageType,
        platform: str
    ) -> UsageRecord:
        """Record content usage"""
        usage_id = str(uuid.uuid4())
        
        usage_record = UsageRecord(
            usage_id=usage_id,
            content_id=content_id,
            license_id=license_id,
            user_id=user_id,
            usage_type=usage_type,
            platform=platform
        )
        
        self.usage_records[usage_id] = usage_record
        return usage_record
    
    # Watermark engine creators
    
    def _create_visible_watermark_engine(self):
        """Create visible watermark engine"""
        async def visible_watermark(content_data: Any, config: WatermarkConfig) -> Any:
            try:
                if PIL_AVAILABLE and isinstance(content_data, str):
                    # Handle base64 image data
                    if content_data.startswith('data:image'):
                        content_data = content_data.split(',')[1]
                    image_data = base64.b64decode(content_data)
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Create watermark
                    draw = ImageDraw.Draw(image)
                    
                    # Apply watermark text
                    draw.text(
                        config.position, 
                        config.text, 
                        fill=(*config.color, config.opacity),
                        font=None  # Use default font
                    )
                    
                    # Convert back to base64
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return content_data
                
            except Exception as e:
                logger.error(f"Visible watermark failed: {e}")
                return content_data
        
        return visible_watermark
    
    def _create_invisible_watermark_engine(self):
        """Create invisible watermark engine"""
        async def invisible_watermark(content_data: Any, config: WatermarkConfig) -> Any:
            # Placeholder implementation for invisible watermarking
            # In a real implementation, this would use LSB steganography or DCT embedding
            return content_data
        
        return invisible_watermark
    
    def _create_steganographic_engine(self):
        """Create steganographic watermark engine"""
        async def steganographic_watermark(content_data: Any, config: WatermarkConfig) -> Any:
            # Placeholder implementation for steganographic embedding
            # In a real implementation, this would use advanced steganographic techniques
            return content_data
        
        return steganographic_watermark
    
    # Detection engine creators
    
    def _create_visual_detection_engine(self):
        """Create visual fingerprint detection engine"""
        async def visual_detection(content_id: str, platform_data: Any) -> List[PiracyIncident]:
            # Placeholder visual detection implementation
            return []
        
        return visual_detection
    
    def _create_audio_detection_engine(self):
        """Create audio fingerprint detection engine"""
        async def audio_detection(content_id: str, platform_data: Any) -> List[PiracyIncident]:
            # Placeholder audio detection implementation
            return []
        
        return audio_detection
    
    def _create_text_detection_engine(self):
        """Create text similarity detection engine"""
        async def text_detection(content_id: str, platform_data: Any) -> List[PiracyIncident]:
            # Placeholder text detection implementation
            return []
        
        return text_detection
    
    def _create_watermark_detection_engine(self):
        """Create watermark detection engine"""
        async def watermark_detection(content_id: str, platform_data: Any) -> List[PiracyIncident]:
            # Placeholder watermark detection implementation
            return []
        
        return watermark_detection
    
    # Monitoring service creators
    
    def _create_youtube_monitor(self):
        """Create YouTube monitoring service"""
        async def youtube_monitor(content_id: str, detection_methods: List[DetectionMethod]) -> List[PiracyIncident]:
            # Placeholder YouTube monitoring implementation
            return []
        
        return youtube_monitor
    
    def _create_instagram_monitor(self):
        """Create Instagram monitoring service"""
        async def instagram_monitor(content_id: str, detection_methods: List[DetectionMethod]) -> List[PiracyIncident]:
            # Placeholder Instagram monitoring implementation
            return []
        
        return instagram_monitor
    
    def _create_facebook_monitor(self):
        """Create Facebook monitoring service"""
        async def facebook_monitor(content_id: str, detection_methods: List[DetectionMethod]) -> List[PiracyIncident]:
            # Placeholder Facebook monitoring implementation
            return []
        
        return facebook_monitor


# Backward compatibility classes
class PiracyDetection:
    """Backward compatibility for PiracyDetection"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.rights_engine = RightsManagementEngine(config)
    
    async def detect_piracy(self, content_id: str, platforms: List[MonitoringPlatform] = None) -> List[PiracyIncident]:
        return await self.rights_engine.detect_piracy(content_id, platforms)

class WatermarkIntegration:
    """Backward compatibility for WatermarkIntegration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.rights_engine = RightsManagementEngine(config)
    
    async def apply_watermark(self, content_data: Any, config: WatermarkConfig) -> Dict[str, Any]:
        return await self.rights_engine.apply_watermark(content_data, config)

class LicenseManager:
    """Backward compatibility for LicenseManager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.rights_engine = RightsManagementEngine(config)
    
    async def create_license(self, content_id: str, licensee_id: str, licensor_id: str, rights_config: RightsConfig) -> License:
        return await self.rights_engine.create_license(content_id, licensee_id, licensor_id, rights_config)

# Configuration helper classes
@dataclass
class RightsComplianceConfig:
    """Rights compliance configuration"""
    automatic_licensing: bool = True
    piracy_monitoring_enabled: bool = True
    takedown_automation: bool = False
    royalty_calculation_frequency: str = "monthly"
    watermark_default_enabled: bool = True

@dataclass
class ComplianceReport:
    """Rights compliance report"""
    content_id: str
    license_status: str
    piracy_incidents: int
    usage_violations: int
    revenue_compliance: bool
    recommendations: List[str]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))