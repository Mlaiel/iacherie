"""
Surveillance Serializer Module
==============================

Specialized serialization for surveillance data and monitoring results.
Optimized for real-time surveillance, alerts, and violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

 LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et surveillance en temps réel
- Backend Senior: Infrastructure robuste pour surveillance distribuée
- ML Engineer: Algorithmes de détection et prédiction d'anomalies
- DBA Expert: Optimisation des requêtes de surveillance massive
- Sécurité: Protection et chiffrement des données de surveillance
- Microservices: Architecture distribuée de surveillance multi-plateformes
- Audio/Vidéo: Analyse multimédia pour détection de violations
- DevOps: Monitoring en temps réel et alertes automatisées
- IA Prompt Engineer: Optimisation de la détection par IA
"""

import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import hashlib
from urllib.parse import urlparse
from pydantic import BaseModel, Field, validator, HttpUrl

logger = logging.getLogger(__name__)

class SurveillanceType(Enum):
    """Types of surveillance monitoring."""
    CONTENT_DETECTION = "content_detection"
    COPYRIGHT_VIOLATION = "copyright_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    PLATFORM_MONITORING = "platform_monitoring"
    BRAND_PROTECTION = "brand_protection"
    SOCIAL_LISTENING = "social_listening"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TREND_MONITORING = "trend_monitoring"

class DetectionMethod(Enum):
    """Detection methods used."""
    FINGERPRINT_MATCHING = "fingerprint_matching"
    AI_VISUAL_RECOGNITION = "ai_visual_recognition"
    AUDIO_ANALYSIS = "audio_analysis"
    TEXT_SIMILARITY = "text_similarity"
    METADATA_COMPARISON = "metadata_comparison"
    REVERSE_IMAGE_SEARCH = "reverse_image_search"
    API_MONITORING = "api_monitoring"
    WEB_SCRAPING = "web_scraping"

class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class ActionStatus(Enum):
    """Status of enforcement actions."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

class PlatformStatus(Enum):
    """Platform monitoring status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class DetectionEvidence:
    """Evidence data for detection results."""
    evidence_id: str
    evidence_type: str  # screenshot, url, metadata, etc.
    evidence_data: Optional[bytes] = None
    evidence_url: Optional[str] = None
    evidence_metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    captured_at: datetime = field(default_factory=datetime.now)
    verified: bool = False

@dataclass
class EnforcementAction:
    """Enforcement action taken."""
    action_id: str
    action_type: str  # dmca_takedown, cease_desist, platform_report, etc.
    status: ActionStatus
    platform: str
    target_url: str
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    initiated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    success: bool = False

@dataclass
class SurveillanceMetrics:
    """Surveillance performance metrics."""
    total_scans: int = 0
    successful_scans: int = 0
    failed_scans: int = 0
    detections_found: int = 0
    false_positives: int = 0
    true_positives: int = 0
    response_time_ms: float = 0.0
    accuracy_rate: float = 0.0
    coverage_percentage: float = 0.0

class SurveillanceData(BaseModel):
    """
    Comprehensive surveillance data model.
    
    Represents surveillance monitoring results, detections, and actions
    for content protection in the IA-Influencer-Agent platform.
    """
    
    # Basic identification
    surveillance_id: str = Field(..., description="Unique surveillance identifier")
    session_id: str = Field(..., description="Surveillance session identifier")
    surveillance_type: SurveillanceType = Field(..., description="Type of surveillance")
    detection_method: DetectionMethod = Field(..., description="Detection method used")
    
    # Target information
    target_content_id: str = Field(..., description="Target content being monitored")
    target_fingerprint_id: Optional[str] = Field(default=None, description="Target fingerprint")
    target_creator_id: str = Field(..., description="Content creator identifier")
    
    # Detection results
    detection_found: bool = Field(default=False, description="Whether detection was found")
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Similarity score")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Detection confidence")
    
    # Location information
    detected_url: Optional[HttpUrl] = Field(default=None, description="URL where content was detected")
    platform_name: str = Field(..., description="Platform where detection occurred")
    platform_id: Optional[str] = Field(default=None, description="Platform-specific ID")
    page_title: Optional[str] = Field(default=None, description="Page title")
    
    # Content analysis
    detected_content_type: Optional[str] = Field(default=None, description="Type of detected content")
    detected_metadata: Dict[str, Any] = Field(default_factory=dict, description="Detected content metadata")
    content_modifications: List[str] = Field(default_factory=list, description="Detected modifications")
    
    # Evidence collection
    evidence_items: List[DetectionEvidence] = Field(default_factory=list, description="Evidence collected")
    screenshot_data: Optional[bytes] = Field(default=None, description="Screenshot evidence")
    html_source: Optional[str] = Field(default=None, description="HTML source if applicable")
    
    # Alert information
    alert_severity: AlertSeverity = Field(default=AlertSeverity.MEDIUM, description="Alert severity")
    alert_triggered: bool = Field(default=False, description="Whether alert was triggered")
    alert_message: Optional[str] = Field(default=None, description="Alert message")
    requires_action: bool = Field(default=False, description="Whether action is required")
    
    # Enforcement actions
    enforcement_actions: List[EnforcementAction] = Field(default_factory=list, description="Actions taken")
    dmca_submitted: bool = Field(default=False, description="DMCA takedown submitted")
    platform_reported: bool = Field(default=False, description="Reported to platform")
    
    # Tracking information
    first_detected: datetime = Field(default_factory=datetime.now, description="First detection time")
    last_seen: datetime = Field(default_factory=datetime.now, description="Last seen time")
    detection_count: int = Field(default=1, description="Number of times detected")
    status_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Status change history")
    
    # Surveillance configuration
    monitoring_enabled: bool = Field(default=True, description="Monitoring enabled")
    monitoring_frequency: int = Field(default=3600, description="Monitoring frequency in seconds")
    next_scan_at: Optional[datetime] = Field(default=None, description="Next scheduled scan")
    
    # Performance metrics
    scan_duration_ms: float = Field(default=0.0, description="Scan duration in milliseconds")
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    bandwidth_used_kb: float = Field(default=0.0, description="Bandwidth used in KB")
    
    # Metadata and tags
    tags: List[str] = Field(default_factory=list, description="Surveillance tags")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data")
    
    @validator('surveillance_type', pre=True)
    def validate_surveillance_type(cls, v):
        if isinstance(v, str):
            return SurveillanceType(v.lower())
        return v
    
    @validator('detection_method', pre=True)
    def validate_detection_method(cls, v):
        if isinstance(v, str):
            return DetectionMethod(v.lower())
        return v
    
    @validator('alert_severity', pre=True)
    def validate_alert_severity(cls, v):
        if isinstance(v, str):
            return AlertSeverity(v.lower())
        return v
    
    @validator('platform_name')
    def validate_platform_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Platform name cannot be empty")
        return v.strip().lower()

class SurveillanceSerializer:
    """
    Advanced surveillance data serialization system.
    
    Handles efficient serialization and deserialization of surveillance monitoring data,
    detection results, and enforcement actions for the IA-Influencer-Agent platform.
    """
    
    def __init__(self):
        """Initialize surveillance serializer."""
        self.max_evidence_size = 50 * 1024 * 1024  # 50MB max evidence size
        self.evidence_compression_threshold = 1024  # 1KB threshold for compression
        
        logger.info("Surveillance serializer initialized")
    
    def serialize_surveillance(
        self,
        surveillance: SurveillanceData,
        include_evidence: bool = True,
        include_html_source: bool = False,
        compress_large_data: bool = True
    ) -> Dict[str, Any]:
        """
        Serialize surveillance data to dictionary format.
        
        Args:
            surveillance: Surveillance data to serialize
            include_evidence: Whether to include evidence data
            include_html_source: Whether to include HTML source
            compress_large_data: Whether to compress large data
            
        Returns:
            Serialized surveillance dictionary
        """



        try:
            # Convert to dictionary
            data = surveillance.dict()
            
            # Handle datetime conversions
            data['first_detected'] = surveillance.first_detected.isoformat()
            data['last_seen'] = surveillance.last_seen.isoformat()
            if surveillance.next_scan_at:
                data['next_scan_at'] = surveillance.next_scan_at.isoformat()
            
            # Handle URL conversion
            if surveillance.detected_url:
                data['detected_url'] = str(surveillance.detected_url)
            
            # Serialize evidence items
            if include_evidence and surveillance.evidence_items:
                data['evidence_items'] = [
                    self._serialize_detection_evidence(evidence, compress_large_data)
                    for evidence in surveillance.evidence_items
                ]
            elif not include_evidence:
                data.pop('evidence_items', None)
            
            # Handle screenshot data
            if surveillance.screenshot_data:
                if include_evidence:
                    data['screenshot_data'] = self._encode_binary_data(
                        surveillance.screenshot_data,
                        compress=compress_large_data
                    )
                else:
                    data.pop('screenshot_data', None)
            
            # Handle HTML source
            if not include_html_source:
                data.pop('html_source', None)
            elif surveillance.html_source and compress_large_data:
                data['html_source'] = self._compress_text_data(surveillance.html_source)
            
            # Serialize enforcement actions
            if surveillance.enforcement_actions:
                data['enforcement_actions'] = [
                    self._serialize_enforcement_action(action)
                    for action in surveillance.enforcement_actions
                ]
            
            # Convert enums
            data['surveillance_type'] = surveillance.surveillance_type.value
            data['detection_method'] = surveillance.detection_method.value
            data['alert_severity'] = surveillance.alert_severity.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_evidence': include_evidence,
                'includes_html_source': include_html_source,
                'data_compressed': compress_large_data,
                'surveillance_type': surveillance.surveillance_type.value
            }
            
            logger.debug(f"Serialized surveillance {surveillance.surveillance_id}")
            return data
            
        except Exception as e:
            logger.error(f"Surveillance serialization failed: {e}")
            raise
    
    def deserialize_surveillance(
        self,
        data: Dict[str, Any]
    ) -> SurveillanceData:
        """
        Deserialize surveillance data from dictionary format.
        
        Args:
            data: Serialized surveillance dictionary
            
        Returns:
            Deserialized SurveillanceData object
        """



        try:
            # Handle datetime conversions
            if isinstance(data.get('first_detected'), str):
                data['first_detected'] = datetime.fromisoformat(data['first_detected'])
            
            if isinstance(data.get('last_seen'), str):
                data['last_seen'] = datetime.fromisoformat(data['last_seen'])
            
            if isinstance(data.get('next_scan_at'), str):
                data['next_scan_at'] = datetime.fromisoformat(data['next_scan_at'])
            
            # Deserialize evidence items
            if 'evidence_items' in data and data['evidence_items']:
                data['evidence_items'] = [
                    self._deserialize_detection_evidence(evidence_data)
                    for evidence_data in data['evidence_items']
                ]
            
            # Handle screenshot data
            if 'screenshot_data' in data and isinstance(data['screenshot_data'], str):
                data['screenshot_data'] = self._decode_binary_data(data['screenshot_data'])
            
            # Handle compressed HTML source
            if 'html_source' in data and isinstance(data['html_source'], str):
                if data['html_source'].startswith('gzip:'):
                    data['html_source'] = self._decompress_text_data(data['html_source'])
            
            # Deserialize enforcement actions
            if 'enforcement_actions' in data and data['enforcement_actions']:
                data['enforcement_actions'] = [
                    self._deserialize_enforcement_action(action_data)
                    for action_data in data['enforcement_actions']
                ]
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create SurveillanceData object
            surveillance = SurveillanceData(**data)
            
            logger.debug(f"Deserialized surveillance {surveillance.surveillance_id}")
            return surveillance
            
        except Exception as e:
            logger.error(f"Surveillance deserialization failed: {e}")
            raise
    
    def serialize_surveillance_batch(
        self,
        surveillance_list: List[SurveillanceData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple surveillance records efficiently."""



        try:
            serialized_list = []
            
            for surveillance in surveillance_list:
                serialized = self.serialize_surveillance(
                    surveillance,
                    include_evidence=not compact_mode,
                    include_html_source=not compact_mode,
                    compress_large_data=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(surveillance_list)} surveillance records")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Surveillance batch serialization failed: {e}")
            raise
    
    def deserialize_surveillance_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[SurveillanceData]:
        """Deserialize multiple surveillance records efficiently."""



        try:
            surveillance_list = []
            
            for data in data_list:
                surveillance = self.deserialize_surveillance(data)
                surveillance_list.append(surveillance)
            
            logger.info(f"Deserialized {len(data_list)} surveillance records")
            return surveillance_list
            
        except Exception as e:
            logger.error(f"Surveillance batch deserialization failed: {e}")
            raise
    
    def _serialize_detection_evidence(
        self,
        evidence: DetectionEvidence,
        compress: bool = True
    ) -> Dict[str, Any]:
        """Serialize detection evidence."""



        try:
            data = {
                'evidence_id': evidence.evidence_id,
                'evidence_type': evidence.evidence_type,
                'evidence_url': evidence.evidence_url,
                'evidence_metadata': evidence.evidence_metadata,
                'confidence_score': evidence.confidence_score,
                'captured_at': evidence.captured_at.isoformat(),
                'verified': evidence.verified
            }
            
            # Handle evidence data
            if evidence.evidence_data:
                if len(evidence.evidence_data) > self.max_evidence_size:
                    logger.warning(f"Evidence {evidence.evidence_id} exceeds max size")
                    data['evidence_data'] = None
                    data['_oversized'] = True
                else:
                    data['evidence_data'] = self._encode_binary_data(
                        evidence.evidence_data,
                        compress=compress
                    )
            
            return data
            
        except Exception as e:
            logger.error(f"Evidence serialization failed: {e}")
            raise
    
    def _deserialize_detection_evidence(
        self,
        data: Dict[str, Any]
    ) -> DetectionEvidence:
        """Deserialize detection evidence."""



        try:
            # Handle datetime conversion
            if isinstance(data.get('captured_at'), str):
                data['captured_at'] = datetime.fromisoformat(data['captured_at'])
            
            # Handle evidence data
            if 'evidence_data' in data and isinstance(data['evidence_data'], str):
                data['evidence_data'] = self._decode_binary_data(data['evidence_data'])
            elif data.get('_oversized'):
                data['evidence_data'] = None
            
            # Remove internal flags
            data.pop('_oversized', None)
            
            return DetectionEvidence(**data)
            
        except Exception as e:
            logger.error(f"Evidence deserialization failed: {e}")
            raise
    
    def _serialize_enforcement_action(
        self,
        action: EnforcementAction
    ) -> Dict[str, Any]:
        """Serialize enforcement action."""



        try:
            data = {
                'action_id': action.action_id,
                'action_type': action.action_type,
                'status': action.status.value,
                'platform': action.platform,
                'target_url': action.target_url,
                'request_data': action.request_data,
                'response_data': action.response_data,
                'initiated_at': action.initiated_at.isoformat(),
                'success': action.success
            }
            
            if action.completed_at:
                data['completed_at'] = action.completed_at.isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Enforcement action serialization failed: {e}")
            raise
    
    def _deserialize_enforcement_action(
        self,
        data: Dict[str, Any]
    ) -> EnforcementAction:
        """Deserialize enforcement action."""



        try:
            # Handle datetime conversions
            if isinstance(data.get('initiated_at'), str):
                data['initiated_at'] = datetime.fromisoformat(data['initiated_at'])
            
            if isinstance(data.get('completed_at'), str):
                data['completed_at'] = datetime.fromisoformat(data['completed_at'])
            
            # Handle status enum
            if isinstance(data.get('status'), str):
                data['status'] = ActionStatus(data['status'])
            
            return EnforcementAction(**data)
            
        except Exception as e:
            logger.error(f"Enforcement action deserialization failed: {e}")
            raise
    
    def _encode_binary_data(self, binary_data: bytes, compress: bool = True) -> str:
        """Encode binary data to base64 string with optional compression."""



        try:
            import base64
            
            if compress and len(binary_data) > self.evidence_compression_threshold:
                import gzip
                compressed_data = gzip.compress(binary_data)
                encoded = base64.b64encode(compressed_data).decode('utf-8')
                return f"gzip:{encoded}"
            else:
                encoded = base64.b64encode(binary_data).decode('utf-8')
                return f"raw:{encoded}"
                
        except Exception as e:
            logger.error(f"Binary data encoding failed: {e}")
            raise
    
    def _decode_binary_data(self, encoded_data: str) -> bytes:
        """Decode binary data from base64 string with decompression."""



        try:
            import base64
            
            if encoded_data.startswith('gzip:'):
                import gzip
                encoded = encoded_data[5:]  # Remove 'gzip:' prefix
                compressed_data = base64.b64decode(encoded)
                return gzip.decompress(compressed_data)
            elif encoded_data.startswith('raw:'):
                encoded = encoded_data[4:]  # Remove 'raw:' prefix
                return base64.b64decode(encoded)
            else:
                # Legacy format
                return base64.b64decode(encoded_data)
                
        except Exception as e:
            logger.error(f"Binary data decoding failed: {e}")
            raise
    
    def _compress_text_data(self, text_data: str) -> str:
        """Compress text data using gzip."""



        try:
            import gzip
            
            compressed = gzip.compress(text_data.encode('utf-8'))
            encoded = base64.b64encode(compressed).decode('utf-8')
            return f"gzip:{encoded}"
            
        except Exception as e:
            logger.error(f"Text compression failed: {e}")
            return text_data
    
    def _decompress_text_data(self, compressed_data: str) -> str:
        """Decompress text data from gzip."""



        try:
            import gzip
            
            if compressed_data.startswith('gzip:'):
                encoded = compressed_data[5:]  # Remove 'gzip:' prefix
                compressed = base64.b64decode(encoded)
                return gzip.decompress(compressed).decode('utf-8')
            else:
                return compressed_data
                
        except Exception as e:
            logger.error(f"Text decompression failed: {e}")
            return compressed_data
    
    def create_surveillance_summary(
        self,
        surveillance: SurveillanceData
    ) -> Dict[str, Any]:
        """Create summary of surveillance data."""



        try:
            return {
                'surveillance_id': surveillance.surveillance_id,
                'surveillance_type': surveillance.surveillance_type.value,
                'detection_method': surveillance.detection_method.value,
                'platform_name': surveillance.platform_name,
                'detection_found': surveillance.detection_found,
                'similarity_score': surveillance.similarity_score,
                'confidence_score': surveillance.confidence_score,
                'alert_severity': surveillance.alert_severity.value,
                'alert_triggered': surveillance.alert_triggered,
                'requires_action': surveillance.requires_action,
                'enforcement_actions_count': len(surveillance.enforcement_actions),
                'evidence_items_count': len(surveillance.evidence_items),
                'first_detected': surveillance.first_detected.isoformat(),
                'last_seen': surveillance.last_seen.isoformat(),
                'detection_count': surveillance.detection_count,
                'scan_duration_ms': surveillance.scan_duration_ms,
                'detected_url': str(surveillance.detected_url) if surveillance.detected_url else None
            }
            
        except Exception as e:
            logger.error(f"Surveillance summary creation failed: {e}")
            return {'error': str(e)}
    
    def validate_surveillance_data(
        self,
        surveillance: SurveillanceData
    ) -> Dict[str, Any]:
        """Validate surveillance data integrity."""



        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Required field validation
            if not surveillance.surveillance_id:
                validation_result['errors'].append("Missing surveillance_id")
            
            if not surveillance.target_content_id:
                validation_result['errors'].append("Missing target_content_id")
            
            if not surveillance.platform_name:
                validation_result['errors'].append("Missing platform_name")
            
            # Score validation
            if not 0.0 <= surveillance.similarity_score <= 1.0:
                validation_result['errors'].append("Invalid similarity_score range")
            
            if not 0.0 <= surveillance.confidence_score <= 1.0:
                validation_result['errors'].append("Invalid confidence_score range")
            
            # Evidence validation
            for evidence in surveillance.evidence_items:
                if evidence.evidence_data and len(evidence.evidence_data) > self.max_evidence_size:
                    validation_result['warnings'].append(f"Evidence {evidence.evidence_id} exceeds max size")
            
            # URL validation
            if surveillance.detected_url:
                try:
                    parsed = urlparse(str(surveillance.detected_url))
                    if not parsed.scheme or not parsed.netloc:
                        validation_result['errors'].append("Invalid detected_url format")
                except:
                    validation_result['errors'].append("Invalid detected_url")
            
            # Set validation result
            validation_result['valid'] = len(validation_result['errors']) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Surveillance validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {e}"],
                'warnings': []
            }


# Export main classes
__all__ = [
    'SurveillanceSerializer',
    'SurveillanceData',
    'DetectionEvidence',
    'EnforcementAction',
    'SurveillanceMetrics',
    'SurveillanceType',
    'DetectionMethod',
    'AlertSeverity',
    'ActionStatus',
    'PlatformStatus'
]ce Serializer Module
==============================

Specialized serialization for surveillance data, targets, and monitoring results.
Optimized for real-time surveillance operations and threat detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class SurveillanceStatus(Enum):
    """Surveillance operation status."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ThreatLevel(Enum):
    """Threat level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class SurveillanceType(Enum):
    """Types of surveillance operations."""
    CONTENT_MONITORING = "content_monitoring"
    VIOLATION_DETECTION = "violation_detection"
    TRADEMARK_WATCH = "trademark_watch"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TREND_MONITORING = "trend_monitoring"
    SENTIMENT_TRACKING = "sentiment_tracking"

class Platform(Enum):
    """Supported surveillance platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    GENERIC = "generic"

@dataclass
class SurveillanceTarget:
    """Surveillance target configuration."""
    target_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform = Platform.GENERIC
    target_type: str = "content"  # content, user, hashtag, keyword
    identifier: str = ""  # URL, username, hashtag, etc.
    keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10 scale
    frequency_minutes: int = 60  # Check frequency
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None

@dataclass
class SurveillanceResult:
    """Surveillance operation result."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str = ""
    operation_id: str = ""
    platform: Platform = Platform.GENERIC
    threat_level: ThreatLevel = ThreatLevel.UNKNOWN
    violations_detected: int = 0
    content_found: int = 0
    similarity_scores: List[float] = field(default_factory=list)
    evidence_urls: List[str] = field(default_factory=list)
    evidence_screenshots: List[str] = field(default_factory=list)
    detection_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

@dataclass
class SurveillanceMetrics:
    """Surveillance operation metrics."""
    total_targets: int = 0
    active_targets: int = 0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    violations_detected: int = 0
    threat_level_distribution: Dict[str, int] = field(default_factory=dict)
    average_response_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class SurveillanceData(BaseModel):
    """
    Comprehensive surveillance data model.
    
    Represents surveillance operations, targets, results, and metrics
    for the IA-Influencer-Agent content protection platform.
    """
    
    # Operation information
    operation_id: str = Field(..., description="Unique operation identifier")
    surveillance_type: SurveillanceType = Field(..., description="Type of surveillance")
    status: SurveillanceStatus = Field(default=SurveillanceStatus.PENDING)
    priority: int = Field(default=5, ge=1, le=10, description="Operation priority (1-10)")
    
    # Targets and configuration
    targets: List[SurveillanceTarget] = Field(default_factory=list)
    surveillance_config: Dict[str, Any] = Field(default_factory=dict)
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Results and findings
    results: List[SurveillanceResult] = Field(default_factory=list)
    total_violations: int = Field(default=0)
    highest_threat_level: ThreatLevel = Field(default=ThreatLevel.UNKNOWN)
    
    # Timing information
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    next_scheduled: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[float] = Field(default=None)
    
    # Performance metrics
    metrics: Optional[SurveillanceMetrics] = Field(default=None)
    
    # Notification settings
    notification_enabled: bool = Field(default=True)
    notification_channels: List[str] = Field(default_factory=list)
    notification_thresholds: Dict[str, Any] = Field(default_factory=dict)
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('surveillance_type', pre=True)
    def validate_surveillance_type(cls, v):
        if isinstance(v, str):
            return SurveillanceType(v.lower())
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            return SurveillanceStatus(v.lower())
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("Priority must be between 1 and 10")
        return v

class SurveillanceSerializer:
    """
    Advanced surveillance data serialization system.
    
    Handles efficient serialization and deserialization of surveillance
    operations, targets, results, and metrics with real-time optimization.
    """
    
    def __init__(self):
        """Initialize surveillance serializer."""
        self.compression_threshold = 10 * 1024  # 10KB
        self.max_result_history = 1000  # Maximum results to keep
        
        logger.info("Surveillance serializer initialized")
    
    def serialize_surveillance_data(
        self,
        surveillance_data: SurveillanceData,
        include_full_history: bool = False,
        compress_results: bool = True
    ) -> Dict[str, Any]:
        """
        Serialize surveillance data to dictionary format.
        
        Args:
            surveillance_data: Surveillance data to serialize
            include_full_history: Whether to include complete result history
            compress_results: Whether to compress large result sets
            
        Returns:
            Serialized surveillance dictionary
        """



        try:
            # Convert to dictionary
            data = surveillance_data.dict()
            
            # Handle datetime conversions
            data['started_at'] = surveillance_data.started_at.isoformat()
            if surveillance_data.completed_at:
                data['completed_at'] = surveillance_data.completed_at.isoformat()
            if surveillance_data.next_scheduled:
                data['next_scheduled'] = surveillance_data.next_scheduled.isoformat()
            
            # Serialize targets
            data['targets'] = [
                self._serialize_target(target) for target in surveillance_data.targets
            ]
            
            # Serialize results with optional history limitation
            results = surveillance_data.results
            if not include_full_history and len(results) > self.max_result_history:
                # Keep only recent results
                results = results[-self.max_result_history:]
                data['_truncated_results'] = True
                data['_total_results_count'] = len(surveillance_data.results)
            
            data['results'] = [
                self._serialize_result(result) for result in results
            ]
            
            # Serialize metrics if available
            if surveillance_data.metrics:
                data['metrics'] = self._serialize_metrics(surveillance_data.metrics)
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_full_history': include_full_history,
                'results_compressed': compress_results,
                'surveillance_type': surveillance_data.surveillance_type.value
            }
            
            logger.debug(f"Serialized surveillance operation {surveillance_data.operation_id}")
            return data
            
        except Exception as e:
            logger.error(f"Surveillance data serialization failed: {e}")
            raise
    
    def deserialize_surveillance_data(
        self,
        data: Dict[str, Any]
    ) -> SurveillanceData:
        """
        Deserialize surveillance data from dictionary format.
        
        Args:
            data: Serialized surveillance dictionary
            
        Returns:
            Deserialized SurveillanceData object
        """



        try:
            # Handle datetime conversions
            if isinstance(data.get('started_at'), str):
                data['started_at'] = datetime.fromisoformat(data['started_at'])
            
            if isinstance(data.get('completed_at'), str):
                data['completed_at'] = datetime.fromisoformat(data['completed_at'])
            
            if isinstance(data.get('next_scheduled'), str):
                data['next_scheduled'] = datetime.fromisoformat(data['next_scheduled'])
            
            # Deserialize targets
            if 'targets' in data:
                data['targets'] = [
                    self._deserialize_target(target_data)
                    for target_data in data['targets']
                ]
            
            # Deserialize results
            if 'results' in data:
                data['results'] = [
                    self._deserialize_result(result_data)
                    for result_data in data['results']
                ]
            
            # Deserialize metrics if available
            if 'metrics' in data and data['metrics']:
                data['metrics'] = self._deserialize_metrics(data['metrics'])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            data.pop('_truncated_results', None)
            data.pop('_total_results_count', None)
            
            # Create SurveillanceData object
            surveillance_data = SurveillanceData(**data)
            
            logger.debug(f"Deserialized surveillance operation {surveillance_data.operation_id}")
            return surveillance_data
            
        except Exception as e:
            logger.error(f"Surveillance data deserialization failed: {e}")
            raise
    
    def serialize_surveillance_batch(
        self,
        surveillance_list: List[SurveillanceData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple surveillance operations efficiently."""



        try:
            serialized_list = []
            
            for surveillance in surveillance_list:
                serialized = self.serialize_surveillance_data(
                    surveillance,
                    include_full_history=not compact_mode,
                    compress_results=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(surveillance_list)} surveillance operations")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Surveillance batch serialization failed: {e}")
            raise
    
    def deserialize_surveillance_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[SurveillanceData]:
        """Deserialize multiple surveillance operations efficiently."""



        try:
            surveillance_list = []
            
            for data in data_list:
                surveillance = self.deserialize_surveillance_data(data)
                surveillance_list.append(surveillance)
            
            logger.info(f"Deserialized {len(data_list)} surveillance operations")
            return surveillance_list
            
        except Exception as e:
            logger.error(f"Surveillance batch deserialization failed: {e}")
            raise
    
    def _serialize_target(self, target: SurveillanceTarget) -> Dict[str, Any]:
        """Serialize surveillance target."""
        data = {
            'target_id': target.target_id,
            'platform': target.platform.value,
            'target_type': target.target_type,
            'identifier': target.identifier,
            'keywords': target.keywords,
            'exclude_keywords': target.exclude_keywords,
            'priority': target.priority,
            'frequency_minutes': target.frequency_minutes,
            'active': target.active,
            'metadata': target.metadata,
            'created_at': target.created_at.isoformat()
        }
        
        if target.last_checked:
            data['last_checked'] = target.last_checked.isoformat()
        
        return data
    
    def _deserialize_target(self, data: Dict[str, Any]) -> SurveillanceTarget:
        """Deserialize surveillance target."""
        # Convert datetime strings
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if isinstance(data.get('last_checked'), str):
            data['last_checked'] = datetime.fromisoformat(data['last_checked'])
        
        # Convert platform enum
        if isinstance(data.get('platform'), str):
            data['platform'] = Platform(data['platform'])
        
        return SurveillanceTarget(**data)
    
    def _serialize_result(self, result: SurveillanceResult) -> Dict[str, Any]:
        """Serialize surveillance result."""
        data = {
            'result_id': result.result_id,
            'target_id': result.target_id,
            'operation_id': result.operation_id,
            'platform': result.platform.value,
            'threat_level': result.threat_level.value,
            'violations_detected': result.violations_detected,
            'content_found': result.content_found,
            'similarity_scores': result.similarity_scores,
            'evidence_urls': result.evidence_urls,
            'evidence_screenshots': result.evidence_screenshots,
            'detection_details': result.detection_details,
            'recommendations': result.recommendations,
            'detected_at': result.detected_at.isoformat()
        }
        
        if result.processed_at:
            data['processed_at'] = result.processed_at.isoformat()
        
        return data
    
    def _deserialize_result(self, data: Dict[str, Any]) -> SurveillanceResult:
        """Deserialize surveillance result."""
        # Convert datetime strings
        if isinstance(data.get('detected_at'), str):
            data['detected_at'] = datetime.fromisoformat(data['detected_at'])
        
        if isinstance(data.get('processed_at'), str):
            data['processed_at'] = datetime.fromisoformat(data['processed_at'])
        
        # Convert enum values
        if isinstance(data.get('platform'), str):
            data['platform'] = Platform(data['platform'])
        
        if isinstance(data.get('threat_level'), str):
            data['threat_level'] = ThreatLevel(data['threat_level'])
        
        return SurveillanceResult(**data)
    
    def _serialize_metrics(self, metrics: SurveillanceMetrics) -> Dict[str, Any]:
        """Serialize surveillance metrics."""



        return {
            'total_targets': metrics.total_targets,
            'active_targets': metrics.active_targets,
            'total_operations': metrics.total_operations,
            'successful_operations': metrics.successful_operations,
            'failed_operations': metrics.failed_operations,
            'violations_detected': metrics.violations_detected,
            'threat_level_distribution': metrics.threat_level_distribution,
            'average_response_time': metrics.average_response_time,
            'last_updated': metrics.last_updated.isoformat()
        }
    
    def _deserialize_metrics(self, data: Dict[str, Any]) -> SurveillanceMetrics:
        """Deserialize surveillance metrics."""
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return SurveillanceMetrics(**data)
    
    def create_surveillance_summary(
        self,
        surveillance_data: SurveillanceData
    ) -> Dict[str, Any]:
        """Create compact summary of surveillance operation."""



        try:
            summary = {
                'operation_id': surveillance_data.operation_id,
                'surveillance_type': surveillance_data.surveillance_type.value,
                'status': surveillance_data.status.value,
                'priority': surveillance_data.priority,
                'total_targets': len(surveillance_data.targets),
                'active_targets': len([t for t in surveillance_data.targets if t.active]),
                'total_violations': surveillance_data.total_violations,
                'highest_threat_level': surveillance_data.highest_threat_level.value,
                'started_at': surveillance_data.started_at.isoformat(),
                'duration_seconds': surveillance_data.duration_seconds
            }
            
            if surveillance_data.completed_at:
                summary['completed_at'] = surveillance_data.completed_at.isoformat()
            
            if surveillance_data.next_scheduled:
                summary['next_scheduled'] = surveillance_data.next_scheduled.isoformat()
            
            # Add latest results summary
            if surveillance_data.results:
                latest_results = surveillance_data.results[-5:]  # Last 5 results
                summary['latest_results'] = [
                    {
                        'result_id': r.result_id,
                        'threat_level': r.threat_level.value,
                        'violations_detected': r.violations_detected,
                        'detected_at': r.detected_at.isoformat()
                    }
                    for r in latest_results
                ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Surveillance summary creation failed: {e}")
            return {'error': str(e)}
    
    def filter_results_by_threat_level(
        self,
        surveillance_data: SurveillanceData,
        min_threat_level: ThreatLevel
    ) -> List[SurveillanceResult]:
        """Filter surveillance results by minimum threat level."""



        try:
            threat_levels = {
                ThreatLevel.LOW: 1,
                ThreatLevel.MEDIUM: 2,
                ThreatLevel.HIGH: 3,
                ThreatLevel.CRITICAL: 4,
                ThreatLevel.UNKNOWN: 0
            }
            
            min_level = threat_levels[min_threat_level]
            
            filtered_results = [
                result for result in surveillance_data.results
                if threat_levels[result.threat_level] >= min_level
            ]
            
            logger.debug(
                f"Filtered {len(filtered_results)} results with threat level >= {min_threat_level.value}"
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Surveillance result filtering failed: {e}")
            return []
    
    def aggregate_surveillance_metrics(
        self,
        surveillance_list: List[SurveillanceData]
    ) -> Dict[str, Any]:
        """Aggregate metrics across multiple surveillance operations."""



        try:
            total_targets = 0
            total_violations = 0
            threat_distribution = {level.value: 0 for level in ThreatLevel}
            status_distribution = {status.value: 0 for status in SurveillanceStatus}
            
            for surveillance in surveillance_list:
                total_targets += len(surveillance.targets)
                total_violations += surveillance.total_violations
                
                # Count by status
                status_distribution[surveillance.status.value] += 1
                
                # Count threat levels from results
                for result in surveillance.results:
                    threat_distribution[result.threat_level.value] += 1
            
            return {
                'total_operations': len(surveillance_list),
                'total_targets': total_targets,
                'total_violations': total_violations,
                'status_distribution': status_distribution,
                'threat_level_distribution': threat_distribution,
                'average_targets_per_operation': total_targets / max(len(surveillance_list), 1),
                'average_violations_per_operation': total_violations / max(len(surveillance_list), 1),
                'aggregated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Surveillance metrics aggregation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'SurveillanceSerializer',
    'SurveillanceData',
    'SurveillanceTarget',
    'SurveillanceResult',
    'SurveillanceMetrics',
    'SurveillanceStatus',
    'SurveillanceType',
    'ThreatLevel',
    'Platform'
]
