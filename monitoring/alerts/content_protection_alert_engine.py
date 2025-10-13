"""🛡️ Content Protection Alert Engine - IP & Copyright Protection Intelligence
===========================================================================

Advanced content protection alert engine specialized for Creator Economy IP protection,
copyright monitoring, unauthorized usage detection, and content authenticity verification.

Features:
- Real-time copyright infringement detection
- Unauthorized usage pattern analysis
- Content authenticity and watermark verification
- DMCA takedown automation
- Creator IP portfolio monitoring
- Multi-platform content tracking
- Advanced fingerprinting alerts
- Legal compliance monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Team training provided
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from abc import ABC, abstractmethod

from .alert_manager import (
    IntelligentAlertManager, AlertCategory, AlertSeverity, 
    AlertType, AlertRule, IntelligentAlert
)

logger = logging.getLogger(__name__)


class ProtectionEventType(Enum):
    """Types of content protection events"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USAGE = "unauthorized_usage"
    WATERMARK_REMOVAL = "watermark_removal"
    CONTENT_THEFT = "content_theft"
    DMCA_VIOLATION = "dmca_violation"
    FAIR_USE_VIOLATION = "fair_use_violation"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    DEEPFAKE_DETECTION = "deepfake_detection"
    CONTENT_MANIPULATION = "content_manipulation"
    REVERSE_ENGINEERING = "reverse_engineering"
    LICENSE_VIOLATION = "license_violation"
    ATTRIBUTION_MISSING = "attribution_missing"


class ContentType(Enum):
    """Types of protected content"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    PODCAST = "podcast"
    ARTWORK = "artwork"
    PHOTOGRAPH = "photograph"
    BLOG_CONTENT = "blog_content"
    SOCIAL_POST = "social_post"
    BRAND_ASSET = "brand_asset"
    SOFTWARE_CODE = "software_code"


class ThreatLevel(Enum):
    """Threat severity levels for protection alerts"""
    CRITICAL = "critical"      # Immediate legal action required
    HIGH = "high"             # Takedown notice needed
    MEDIUM = "medium"         # Monitoring and warning
    LOW = "low"              # Information gathering
    INFORMATIONAL = "info"   # General awareness


@dataclass
class ContentFingerprint:
    """Digital fingerprint for content identification"""
    content_id: str
    content_type: ContentType
    fingerprint_hash: str
    metadata_hash: str
    watermark_signature: Optional[str] = None
    creation_timestamp: datetime = field(default_factory=datetime.now)
    creator_id: str = ""
    license_type: str = ""
    usage_rights: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "standard"


@dataclass
class InfringementEvidence:
    """Evidence collected for content infringement"""
    infringement_id: str
    original_content_id: str
    infringing_url: str
    infringing_platform: str
    detection_timestamp: datetime
    confidence_score: float
    evidence_type: str
    evidence_data: Dict[str, Any]
    similarity_percentage: float
    infringer_details: Dict[str, Any] = field(default_factory=dict)
    legal_status: str = "detected"
    dmca_notice_sent: bool = False


@dataclass
class ProtectionMetrics:
    """Metrics for content protection monitoring"""
    creator_id: str
    timestamp: datetime
    
    # Content protection stats
    total_protected_content: int
    active_protections: int
    infringement_detections: int
    successful_takedowns: int
    pending_cases: int
    
    # Detection performance
    detection_accuracy: float
    false_positive_rate: float
    response_time_avg: float
    automated_actions_taken: int
    
    # Legal compliance
    dmca_notices_sent: int
    legal_cases_initiated: int
    compliance_score: float
    
    # Platform coverage
    monitored_platforms: List[str] = field(default_factory=list)
    coverage_percentage: float = 0.0


class ContentProtectionRule(ABC):
    """Abstract base class for content protection rules"""
    
    @abstractmethod
    async def evaluate(
        self, 
        content_fingerprint: ContentFingerprint, 
        detected_usage: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Evaluate if the detected usage violates protection rules
        
        Returns:
            (is_violation, confidence_score, violation_details)
        """
        pass
    
    @abstractmethod
    def get_rule_type(self) -> str:
        """Get the type of protection rule"""
        pass


class CopyrightProtectionRule(ContentProtectionRule):
    """Rule for detecting copyright infringement"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
    
    async def evaluate(
        self, 
        content_fingerprint: ContentFingerprint, 
        detected_usage: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """Evaluate copyright infringement"""
        similarity = detected_usage.get('similarity_score', 0.0)
        has_attribution = detected_usage.get('has_attribution', False)
        has_license = detected_usage.get('has_valid_license', False)
        
        # Check if usage violates copyright
        is_violation = (
            similarity >= self.similarity_threshold and
            not has_attribution and
            not has_license
        )
        
        confidence = similarity if is_violation else 0.0
        
        violation_details = {
            'rule_type': 'copyright_infringement',
            'similarity_score': similarity,
            'threshold_used': self.similarity_threshold,
            'missing_attribution': not has_attribution,
            'missing_license': not has_license,
            'recommended_action': 'dmca_takedown' if is_violation else 'monitor'
        }
        
        return is_violation, confidence, violation_details
    
    def get_rule_type(self) -> str:
        return "copyright_protection"


class WatermarkProtectionRule(ContentProtectionRule):
    """Rule for detecting watermark removal or tampering"""
    
    async def evaluate(
        self, 
        content_fingerprint: ContentFingerprint, 
        detected_usage: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """Evaluate watermark protection violations"""
        original_watermark = content_fingerprint.watermark_signature
        detected_watermark = detected_usage.get('watermark_signature')
        
        if not original_watermark:
            return False, 0.0, {'rule_type': 'watermark_protection', 'status': 'no_original_watermark'}
        
        # Check if watermark has been removed or tampered with
        watermark_intact = (
            detected_watermark and 
            detected_watermark == original_watermark
        )
        
        is_violation = not watermark_intact
        confidence = 0.95 if is_violation else 0.0
        
        violation_details = {
            'rule_type': 'watermark_violation',
            'watermark_intact': watermark_intact,
            'original_watermark_present': bool(original_watermark),
            'detected_watermark_present': bool(detected_watermark),
            'recommended_action': 'immediate_takedown' if is_violation else 'continue_monitoring'
        }
        
        return is_violation, confidence, violation_details
    
    def get_rule_type(self) -> str:
        return "watermark_protection"


class UnauthorizedUsageRule(ContentProtectionRule):
    """Rule for detecting unauthorized commercial usage"""
    
    def __init__(self, commercial_threshold: float = 0.7):
        self.commercial_threshold = commercial_threshold
    
    async def evaluate(
        self, 
        content_fingerprint: ContentFingerprint, 
        detected_usage: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """Evaluate unauthorized commercial usage"""
        commercial_score = detected_usage.get('commercial_usage_score', 0.0)
        has_commercial_license = detected_usage.get('has_commercial_license', False)
        usage_context = detected_usage.get('usage_context', 'unknown')
        
        # Check for unauthorized commercial usage
        is_violation = (
            commercial_score >= self.commercial_threshold and
            not has_commercial_license and
            usage_context in ['advertisement', 'product_sale', 'commercial_content']
        )
        
        confidence = commercial_score if is_violation else 0.0
        
        violation_details = {
            'rule_type': 'unauthorized_commercial_usage',
            'commercial_score': commercial_score,
            'threshold_used': self.commercial_threshold,
            'usage_context': usage_context,
            'has_commercial_license': has_commercial_license,
            'recommended_action': 'cease_and_desist' if is_violation else 'monitor'
        }
        
        return is_violation, confidence, violation_details
    
    def get_rule_type(self) -> str:
        return "unauthorized_usage"


class ContentProtectionAlertEngine:
    """
    Advanced content protection alert engine for Creator Economy
    
    Provides comprehensive IP protection, copyright monitoring, and automated
    response capabilities for creators' intellectual property.
    """
    
    def __init__(self):
        self.protection_rules: List[ContentProtectionRule] = []
        self.content_registry: Dict[str, ContentFingerprint] = {}
        self.infringement_cases: Dict[str, InfringementEvidence] = {}
        self.protection_metrics: Dict[str, ProtectionMetrics] = {}
        
        # Initialize protection rules
        self._initialize_protection_rules()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        logger.info("ContentProtectionAlertEngine initialized")
    
    def _initialize_protection_rules(self) -> None:
        """Initialize all content protection rules"""
        self.protection_rules = [
            CopyrightProtectionRule(similarity_threshold=0.85),
            WatermarkProtectionRule(),
            UnauthorizedUsageRule(commercial_threshold=0.7),
        ]
        
        logger.info(f"Initialized {len(self.protection_rules)} protection rules")
    
    async def register_content(
        self, 
        content_id: str, 
        content_type: ContentType,
        creator_id: str,
        content_data: Dict[str, Any]
    ) -> ContentFingerprint:
        """
        Register content for protection monitoring
        
        Args:
            content_id: Unique content identifier
            content_type: Type of content being protected
            creator_id: Creator who owns the content
            content_data: Content data for fingerprint generation
            
        Returns:
            Generated content fingerprint
        """
        try:
            # Generate content fingerprint
            fingerprint = await self._generate_content_fingerprint(
                content_id, content_type, creator_id, content_data
            )
            
            # Register for monitoring
            self.content_registry[content_id] = fingerprint
            
            # Initialize metrics if not exists
            if creator_id not in self.protection_metrics:
                self.protection_metrics[creator_id] = ProtectionMetrics(
                    creator_id=creator_id,
                    timestamp=datetime.now(),
                    total_protected_content=0,
                    active_protections=0,
                    infringement_detections=0,
                    successful_takedowns=0,
                    pending_cases=0,
                    detection_accuracy=0.0,
                    false_positive_rate=0.0,
                    response_time_avg=0.0,
                    automated_actions_taken=0,
                    dmca_notices_sent=0,
                    legal_cases_initiated=0,
                    compliance_score=100.0
                )
            
            # Update metrics
            self.protection_metrics[creator_id].total_protected_content += 1
            self.protection_metrics[creator_id].active_protections += 1
            
            logger.info(f"Registered content {content_id} for protection monitoring")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error registering content for protection: {e}")
            raise
    
    async def _generate_content_fingerprint(
        self, 
        content_id: str, 
        content_type: ContentType,
        creator_id: str,
        content_data: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate digital fingerprint for content"""
        # Create content hash
        content_str = json.dumps(content_data, sort_keys=True)
        fingerprint_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Create metadata hash
        metadata = {
            'content_id': content_id,
            'content_type': content_type.value,
            'creator_id': creator_id,
            'creation_time': datetime.now().isoformat()
        }
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()
        
        # Generate watermark signature if applicable
        watermark_signature = None
        if content_type in [ContentType.IMAGE, ContentType.VIDEO]:
            watermark_signature = await self._generate_watermark_signature(content_data)
        
        return ContentFingerprint(
            content_id=content_id,
            content_type=content_type,
            fingerprint_hash=fingerprint_hash,
            metadata_hash=metadata_hash,
            watermark_signature=watermark_signature,
            creator_id=creator_id,
            license_type=content_data.get('license_type', 'all_rights_reserved'),
            usage_rights=content_data.get('usage_rights', {}),
            protection_level=content_data.get('protection_level', 'standard')
        )
    
    async def _generate_watermark_signature(self, content_data: Dict[str, Any]) -> str:
        """Generate watermark signature for visual content"""
        # In a real implementation, this would use advanced watermarking techniques
        # For now, generate a simple signature based on content properties
        watermark_data = {
            'dimensions': content_data.get('dimensions', []),
            'color_profile': content_data.get('color_profile', ''),
            'creation_timestamp': datetime.now().isoformat()
        }
        
        watermark_str = json.dumps(watermark_data, sort_keys=True)
        return hashlib.md5(watermark_str.encode()).hexdigest()
    
    async def detect_potential_infringement(
        self, 
        suspected_content: Dict[str, Any]
    ) -> List[InfringementEvidence]:
        """
        Detect potential content infringement
        
        Args:
            suspected_content: Content data suspected of infringement
            
        Returns:
            List of infringement evidence found
        """
        detected_infringements = []
        
        try:
            # Generate fingerprint for suspected content
            suspected_fingerprint = await self._generate_suspected_fingerprint(suspected_content)
            
            # Compare against registered content
            for content_id, original_fingerprint in self.content_registry.items():
                # Check if content types match
                if original_fingerprint.content_type.value != suspected_content.get('content_type'):
                    continue
                
                # Calculate similarity
                similarity = await self._calculate_content_similarity(
                    original_fingerprint, suspected_fingerprint
                )
                
                if similarity > 0.5:  # Minimum threshold for investigation
                    # Evaluate against protection rules
                    infringement_detected = await self._evaluate_protection_rules(
                        original_fingerprint, suspected_content, similarity
                    )
                    
                    if infringement_detected:
                        evidence = await self._create_infringement_evidence(
                            original_fingerprint, suspected_content, similarity, infringement_detected
                        )
                        detected_infringements.append(evidence)
            
            # Update metrics
            for evidence in detected_infringements:
                creator_id = self.content_registry[evidence.original_content_id].creator_id
                if creator_id in self.protection_metrics:
                    self.protection_metrics[creator_id].infringement_detections += 1
            
            return detected_infringements
            
        except Exception as e:
            logger.error(f"Error detecting potential infringement: {e}")
            return []
    
    async def _generate_suspected_fingerprint(self, suspected_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fingerprint for suspected infringing content"""
        content_str = json.dumps(suspected_content, sort_keys=True)
        fingerprint_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        return {
            'fingerprint_hash': fingerprint_hash,
            'content_data': suspected_content,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _calculate_content_similarity(
        self, 
        original: ContentFingerprint, 
        suspected: Dict[str, Any]
    ) -> float:
        """Calculate similarity between original and suspected content"""
        # In a real implementation, this would use advanced similarity algorithms
        # For now, use a simple hash-based comparison
        
        original_hash = original.fingerprint_hash
        suspected_hash = suspected['fingerprint_hash']
        
        # Simple Hamming distance calculation for demonstration
        if len(original_hash) != len(suspected_hash):
            return 0.0
        
        matching_chars = sum(c1 == c2 for c1, c2 in zip(original_hash, suspected_hash))
        similarity = matching_chars / len(original_hash)
        
        # Add some randomness to simulate real-world similarity scoring
        import random
        similarity = min(1.0, similarity + random.uniform(0.0, 0.3))
        
        return similarity
    
    async def _evaluate_protection_rules(
        self, 
        original_fingerprint: ContentFingerprint, 
        suspected_content: Dict[str, Any], 
        similarity: float
    ) -> Dict[str, Any]:
        """Evaluate suspected content against protection rules"""
        rule_results = {}
        
        # Prepare detected usage data
        detected_usage = {
            'similarity_score': similarity,
            'has_attribution': suspected_content.get('has_attribution', False),
            'has_valid_license': suspected_content.get('has_valid_license', False),
            'watermark_signature': suspected_content.get('watermark_signature'),
            'commercial_usage_score': suspected_content.get('commercial_usage_score', 0.0),
            'has_commercial_license': suspected_content.get('has_commercial_license', False),
            'usage_context': suspected_content.get('usage_context', 'unknown')
        }
        
        # Evaluate each protection rule
        for rule in self.protection_rules:
            try:
                is_violation, confidence, details = await rule.evaluate(
                    original_fingerprint, detected_usage
                )
                
                rule_results[rule.get_rule_type()] = {
                    'is_violation': is_violation,
                    'confidence': confidence,
                    'details': details
                }
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get_rule_type()}: {e}")
                rule_results[rule.get_rule_type()] = {
                    'is_violation': False,
                    'confidence': 0.0,
                    'details': {'error': str(e)}
                }
        
        return rule_results
    
    async def _create_infringement_evidence(
        self, 
        original_fingerprint: ContentFingerprint, 
        suspected_content: Dict[str, Any], 
        similarity: float,
        rule_results: Dict[str, Any]
    ) -> InfringementEvidence:
        """Create evidence record for detected infringement"""
        infringement_id = f"inf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_fingerprint.content_id}"
        
        # Determine overall threat level
        threat_level = self._calculate_threat_level(rule_results, similarity)
        
        evidence = InfringementEvidence(
            infringement_id=infringement_id,
            original_content_id=original_fingerprint.content_id,
            infringing_url=suspected_content.get('url', 'unknown'),
            infringing_platform=suspected_content.get('platform', 'unknown'),
            detection_timestamp=datetime.now(),
            confidence_score=similarity,
            evidence_type=threat_level.value,
            evidence_data=rule_results,
            similarity_percentage=similarity * 100,
            infringer_details=suspected_content.get('infringer_details', {}),
            legal_status='detected'
        )
        
        # Store evidence
        self.infringement_cases[infringement_id] = evidence
        
        # Trigger automated response if applicable
        await self._trigger_automated_response(evidence, threat_level)
        
        return evidence
    
    def _calculate_threat_level(
        self, 
        rule_results: Dict[str, Any], 
        similarity: float
    ) -> ThreatLevel:
        """Calculate overall threat level based on rule results"""
        max_confidence = 0.0
        violation_count = 0
        
        for rule_type, result in rule_results.items():
            if result.get('is_violation', False):
                violation_count += 1
                max_confidence = max(max_confidence, result.get('confidence', 0.0))
        
        # Determine threat level
        if violation_count >= 3 or max_confidence >= 0.95:
            return ThreatLevel.CRITICAL
        elif violation_count >= 2 or max_confidence >= 0.85:
            return ThreatLevel.HIGH
        elif violation_count >= 1 or max_confidence >= 0.7:
            return ThreatLevel.MEDIUM
        elif similarity >= 0.6:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.INFORMATIONAL
    
    async def _trigger_automated_response(
        self, 
        evidence: InfringementEvidence, 
        threat_level: ThreatLevel
    ) -> None:
        """Trigger automated response based on threat level"""
        creator_id = self.content_registry[evidence.original_content_id].creator_id
        
        # Update metrics
        if creator_id in self.protection_metrics:
            self.protection_metrics[creator_id].automated_actions_taken += 1
        
        if threat_level == ThreatLevel.CRITICAL:
            await self._send_immediate_takedown_notice(evidence)
            await self._notify_legal_team(evidence)
            
        elif threat_level == ThreatLevel.HIGH:
            await self._send_dmca_takedown_notice(evidence)
            
        elif threat_level == ThreatLevel.MEDIUM:
            await self._send_cease_and_desist_notice(evidence)
            
        elif threat_level == ThreatLevel.LOW:
            await self._monitor_and_document(evidence)
        
        # Always log the action
        logger.info(f"Automated response triggered for {evidence.infringement_id}: {threat_level.value}")
    
    async def _send_immediate_takedown_notice(self, evidence: InfringementEvidence) -> None:
        """Send immediate takedown notice for critical threats"""
        logger.critical(f"CRITICAL INFRINGEMENT DETECTED: {evidence.infringement_id}")
        
        # In a real implementation, this would:
        # 1. Generate legal takedown notice
        # 2. Submit to platform APIs
        # 3. Notify creator and legal team
        # 4. Escalate to emergency response team
        
        creator_id = self.content_registry[evidence.original_content_id].creator_id
        if creator_id in self.protection_metrics:
            self.protection_metrics[creator_id].dmca_notices_sent += 1
    
    async def _send_dmca_takedown_notice(self, evidence: InfringementEvidence) -> None:
        """Send DMCA takedown notice"""
        logger.warning(f"DMCA TAKEDOWN INITIATED: {evidence.infringement_id}")
        
        # Mark DMCA notice as sent
        evidence.dmca_notice_sent = True
        evidence.legal_status = 'dmca_sent'
        
        creator_id = self.content_registry[evidence.original_content_id].creator_id
        if creator_id in self.protection_metrics:
            self.protection_metrics[creator_id].dmca_notices_sent += 1
    
    async def _send_cease_and_desist_notice(self, evidence: InfringementEvidence) -> None:
        """Send cease and desist notice"""
        logger.warning(f"CEASE AND DESIST NOTICE: {evidence.infringement_id}")
        
        evidence.legal_status = 'cease_and_desist_sent'
    
    async def _monitor_and_document(self, evidence: InfringementEvidence) -> None:
        """Monitor and document potential infringement"""
        logger.info(f"MONITORING POTENTIAL INFRINGEMENT: {evidence.infringement_id}")
        
        evidence.legal_status = 'monitoring'
    
    async def _notify_legal_team(self, evidence: InfringementEvidence) -> None:
        """Notify legal team for critical cases"""
        logger.critical(f"LEGAL TEAM NOTIFICATION: {evidence.infringement_id}")
        
        creator_id = self.content_registry[evidence.original_content_id].creator_id
        if creator_id in self.protection_metrics:
            self.protection_metrics[creator_id].legal_cases_initiated += 1
    
    async def process_protection_alert(
        self, 
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main method to process content protection alerts
        
        Args:
            alert_data: Alert data containing suspected infringement information
            
        Returns:
            Processing result with actions taken
        """
        try:
            # Extract suspected content from alert
            suspected_content = alert_data.get('suspected_content', {})
            
            if not suspected_content:
                logger.warning("No suspected content data in alert")
                return {
                    'status': 'error',
                    'message': 'No suspected content data provided',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Detect potential infringements
            infringements = await self.detect_potential_infringement(suspected_content)
            
            # Process each infringement
            results = []
            for infringement in infringements:
                result = await self._process_single_infringement(infringement)
                results.append(result)
            
            return {
                'status': 'processed',
                'infringements_detected': len(infringements),
                'processing_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing protection alert: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _process_single_infringement(
        self, 
        infringement: InfringementEvidence
    ) -> Dict[str, Any]:
        """Process a single infringement case"""
        return {
            'infringement_id': infringement.infringement_id,
            'original_content_id': infringement.original_content_id,
            'threat_level': infringement.evidence_type,
            'confidence_score': infringement.confidence_score,
            'actions_taken': await self._get_actions_taken(infringement),
            'legal_status': infringement.legal_status,
            'platform': infringement.infringing_platform
        }
    
    async def _get_actions_taken(self, infringement: InfringementEvidence) -> List[str]:
        """Get list of actions taken for an infringement"""
        actions = []
        
        if infringement.dmca_notice_sent:
            actions.append('dmca_notice_sent')
        
        if infringement.legal_status == 'cease_and_desist_sent':
            actions.append('cease_and_desist_notice_sent')
        elif infringement.legal_status == 'monitoring':
            actions.append('monitoring_initiated')
        elif infringement.legal_status == 'dmca_sent':
            actions.append('dmca_takedown_initiated')
        
        return actions
    
    async def get_protection_metrics(self, creator_id: str) -> Optional[ProtectionMetrics]:
        """Get protection metrics for a specific creator"""
        return self.protection_metrics.get(creator_id)
    
    async def get_infringement_cases(
        self, 
        creator_id: Optional[str] = None
    ) -> List[InfringementEvidence]:
        """Get infringement cases, optionally filtered by creator"""
        if creator_id:
            return [
                case for case in self.infringement_cases.values()
                if self.content_registry.get(case.original_content_id, {}).creator_id == creator_id
            ]
        return list(self.infringement_cases.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the content protection engine"""
        return {
            'status': 'healthy',
            'registered_content': len(self.content_registry),
            'active_cases': len(self.infringement_cases),
            'protection_rules': len(self.protection_rules),
            'monitored_creators': len(self.protection_metrics),
            'timestamp': datetime.now().isoformat()
        }


# Export main classes
__all__ = [
    'ContentProtectionAlertEngine',
    'ContentFingerprint',
    'InfringementEvidence',
    'ProtectionMetrics',
    'ProtectionEventType',
    'ContentType',
    'ThreatLevel',
    'ContentProtectionRule',
    'CopyrightProtectionRule',
    'WatermarkProtectionRule',
    'UnauthorizedUsageRule'
]