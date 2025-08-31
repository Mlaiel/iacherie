"""
Content Protection Module - Advanced Content Security & Anti-Piracy System

Module spécialisé pour la protection complète du contenu multimédia selon la logique métier :
User → Upload multi-format → IA protection → SEO → Matching → Distribution → Monétisation

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Security Expert, Anti-Piracy Specialist, Content Protection Engineer, AI Security Expert
Copyright: Fahed Mlaiel - All rights reserved

  AVERTISSEMENT LÉGAL 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de

 LOGIQUE MÉTIER INTÉGRÉE :
- Protection automatique dès l'upload
- Fingerprinting AI multi-format avancé  
- Surveillance web temps réel
- DMCA automatisé
- Monétisation des violations détectées
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import hashlib
import asyncio
import json
from abc import ABC, abstractmethod
import re
import uuid
from collections import defaultdict
import aiohttp
import numpy as np
from pathlib import Path

# Import content type managers for fingerprinting
from .audio_content import AudioContentManager, AudioFingerprint
from .video_content import VideoContentManager, VideoFingerprint
from .image_content import ImageContentManager, ImageFingerprint
from .text_content import TextContentManager, TextFingerprint
from .multimedia_content import MultimediaContentManager, MultimediaFingerprint

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat classification levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProtectionRule(Enum):
    """Content protection rule types"""
    COPYRIGHT_DETECTION = "copyright_detection"
    WATERMARK_VERIFICATION = "watermark_verification"
    DUPLICATE_DETECTION = "duplicate_detection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONTENT_MODIFICATION = "content_modification"
    DISTRIBUTION_MONITORING = "distribution_monitoring"
    PIRACY_DETECTION = "piracy_detection"
    DMCA_COMPLIANCE = "dmca_compliance"
    FACIAL_RECOGNITION = "facial_recognition"
    ADULT_CONTENT = "adult_content"
    VIOLENCE_DETECTION = "violence_detection"
    MALWARE_SCANNING = "malware_scanning"

class ViolationType(Enum):
    """Types of content protection violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_COPY = "unauthorized_copy"
    CONTENT_PIRACY = "content_piracy"
    WATERMARK_REMOVAL = "watermark_removal"
    UNAUTHORIZED_MODIFICATION = "unauthorized_modification"
    MALICIOUS_CONTENT = "malicious_content"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    LICENSE_VIOLATION = "license_violation"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    PRIVACY_VIOLATION = "privacy_violation"

class MonitoringStatus(Enum):
    """Content monitoring status"""
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

@dataclass
class ProtectionPolicy:
    """Content protection policy configuration"""
    policy_id: str
    name: str
    description: str
    enabled_rules: List[ProtectionRule]
    severity_thresholds: Dict[str, float]
    auto_actions: Dict[str, List[str]]
    notification_settings: Dict[str, bool]
    monitoring_frequency: int  # minutes
    retention_period_days: int
    whitelist_patterns: List[str] = field(default_factory=list)
    blacklist_patterns: List[str] = field(default_factory=list)
    custom_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ContentViolation:
    """Content protection violation record"""
    violation_id: str
    content_id: str
    violation_type: ViolationType
    threat_level: ThreatLevel
    confidence_score: float
    description: str
    evidence: Dict[str, Any]
    source_url: Optional[str] = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None
    false_positive: bool = False
    review_status: str = "pending"  # pending, approved, rejected
    reviewer_notes: Optional[str] = None
    automated_response: Optional[str] = None
    legal_action_required: bool = False
    affected_platforms: List[str] = field(default_factory=list)
    estimated_impact: Dict[str, float] = field(default_factory=dict)

@dataclass
class ProtectionMetrics:
    """Protection system metrics and statistics"""
    total_scans: int = 0
    violations_detected: int = 0
    false_positives: int = 0
    resolved_violations: int = 0
    pending_violations: int = 0
    average_detection_time_ms: float = 0.0
    average_resolution_time_hours: float = 0.0
    content_protected: int = 0
    monitoring_coverage: float = 0.0
    threat_distribution: Dict[str, int] = field(default_factory=dict)
    platform_coverage: Dict[str, bool] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class MonitoringTarget:
    """Content monitoring target configuration"""
    target_id: str
    content_id: str
    fingerprint_hash: str
    monitoring_platforms: List[str]
    search_keywords: List[str]
    monitoring_status: MonitoringStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_scanned: Optional[datetime] = None
    next_scan_at: Optional[datetime] = None
    scan_frequency_minutes: int = 60
    violation_count: int = 0
    last_violation_at: Optional[datetime] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

class ContentScanner(ABC):
    """Abstract base class for content scanners"""
    
    @abstractmethod
    async def scan_content(
        self, 
        content_data: Dict[str, Any], 
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan content for violations"""
        pass
    
    @abstractmethod
    async def scan_url(
        self, 
        url: str, 
        reference_fingerprint: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan remote URL for violations"""
        pass

class DuplicateContentScanner(ContentScanner):
    """Scanner for detecting duplicate and unauthorized copies"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DuplicateContentScanner")
        self.similarity_threshold = 0.85
        
    async def scan_content(
        self, 
        content_data: Dict[str, Any], 
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan for duplicate content"""
        violations = []
        
        try:
            content_type = content_data.get('content_type')
            fingerprint = content_data.get('fingerprint')
            
            if not fingerprint:
                return violations
            
            # Search for similar content across platforms
            similar_content = await self._search_similar_content(fingerprint, content_type)
            
            for match in similar_content:
                if match['similarity_score'] >= self.similarity_threshold:
                    violation = ContentViolation(
                        violation_id=str(uuid.uuid4()),
                        content_id=content_data.get('content_id', ''),
                        violation_type=ViolationType.UNAUTHORIZED_COPY,
                        threat_level=self._assess_threat_level(match['similarity_score']),
                        confidence_score=match['similarity_score'],
                        description=f"Potential unauthorized copy detected with {match['similarity_score']:.2%} similarity",
                        evidence={
                            'similar_content_url': match['url'],
                            'similarity_score': match['similarity_score'],
                            'matching_features': match.get('matching_features', []),
                            'platform': match.get('platform', 'unknown')
                        },
                        source_url=match['url'],
                        affected_platforms=[match.get('platform', 'unknown')]
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Duplicate content scanning failed: {e}")
            return violations
    
    async def scan_url(
        self, 
        url: str, 
        reference_fingerprint: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan specific URL for duplicate content"""
        violations = []
        
        try:
            # Download and analyze content from URL
            content_fingerprint = await self._extract_url_fingerprint(url)
            
            if content_fingerprint:
                similarity = await self._compare_fingerprints(
                    reference_fingerprint, 
                    content_fingerprint
                )
                
                if similarity >= self.similarity_threshold:
                    violation = ContentViolation(
                        violation_id=str(uuid.uuid4()),
                        content_id=reference_fingerprint.get('content_id', ''),
                        violation_type=ViolationType.UNAUTHORIZED_COPY,
                        threat_level=self._assess_threat_level(similarity),
                        confidence_score=similarity,
                        description=f"Unauthorized copy detected at URL with {similarity:.2%} similarity",
                        evidence={
                            'url': url,
                            'similarity_score': similarity,
                            'fingerprint_comparison': content_fingerprint
                        },
                        source_url=url
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"URL scanning failed for {url}: {e}")
            return violations
    
    async def _search_similar_content(
        self, 
        fingerprint: Dict[str, Any], 
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Search for similar content across platforms"""
        # This would integrate with various platforms' APIs
        # For demonstration, returning mock results
        return [
            {
                'url': 'https://example.com/similar-content-1',
                'similarity_score': 0.92,
                'platform': 'example_platform',
                'matching_features': ['perceptual_hash', 'audio_fingerprint']
            }
        ]
    
    async def _extract_url_fingerprint(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract fingerprint from content at URL"""



        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Basic fingerprinting (simplified)
                        return {
                            'content_hash': hashlib.sha256(content).hexdigest(),
                            'size': len(content),
                            'url': url
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract fingerprint from {url}: {e}")
            return None
    
    async def _compare_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare two fingerprints and return similarity score"""



        try:
            # Simple hash comparison (would be more sophisticated in reality)
            if fp1.get('content_hash') == fp2.get('content_hash'):
                return 1.0
            
            # Size-based similarity
            size1 = fp1.get('size', 0)
            size2 = fp2.get('size', 0)
            
            if size1 == 0 or size2 == 0:
                return 0.0
            
            size_ratio = min(size1, size2) / max(size1, size2)
            return size_ratio * 0.8  # Simplified similarity
            
        except Exception:
            return 0.0
    
    def _assess_threat_level(self, similarity_score: float) -> ThreatLevel:
        """Assess threat level based on similarity score"""
        if similarity_score >= 0.95:
            return ThreatLevel.CRITICAL
        elif similarity_score >= 0.90:
            return ThreatLevel.HIGH
        elif similarity_score >= 0.85:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

class WatermarkScanner(ContentScanner):
    """Scanner for detecting watermark tampering"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WatermarkScanner")
        
    async def scan_content(
        self, 
        content_data: Dict[str, Any], 
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan for watermark violations"""
        violations = []
        
        try:
            # Check if content should have watermark
            if not content_data.get('should_have_watermark', False):
                return violations
            
            watermark_detected = await self._detect_watermark(content_data)
            
            if not watermark_detected:
                violation = ContentViolation(
                    violation_id=str(uuid.uuid4()),
                    content_id=content_data.get('content_id', ''),
                    violation_type=ViolationType.WATERMARK_REMOVAL,
                    threat_level=ThreatLevel.HIGH,
                    confidence_score=0.9,
                    description="Required watermark is missing or has been removed",
                    evidence={
                        'watermark_expected': True,
                        'watermark_detected': False,
                        'content_type': content_data.get('content_type')
                    }
                )
                violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Watermark scanning failed: {e}")
            return violations
    
    async def scan_url(
        self, 
        url: str, 
        reference_fingerprint: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan URL for watermark violations"""
        # Similar implementation to scan_content but for remote URL
        return []
    
    async def _detect_watermark(self, content_data: Dict[str, Any]) -> bool:
        """Detect presence of watermark in content"""
        # This would use actual watermark detection algorithms
        # For demonstration, returning mock result
        return content_data.get('has_watermark', False)

class ContentProtectionEngine:
    """Main content protection engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize content protection engine
        
        Args:
            config: Configuration for protection engine
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.ContentProtectionEngine")
        
        # Initialize scanners
        self.scanners: Dict[str, ContentScanner] = {
            'duplicate': DuplicateContentScanner(),
            'watermark': WatermarkScanner()
        }
        
        # Protection policies
        self.policies: Dict[str, ProtectionPolicy] = {}
        
        # Monitoring targets
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        
        # Violation tracking
        self.violations: Dict[str, ContentViolation] = {}
        
        # Metrics
        self.metrics = ProtectionMetrics()
        
        # Initialize components
        self._init_components()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for protection engine"""



        return {
            "monitoring_enabled": True,
            "real_time_scanning": True,
            "automated_responses": True,
            "notification_enabled": True,
            "max_concurrent_scans": 10,
            "scan_timeout_seconds": 300,
            "violation_retention_days": 365,
            "false_positive_threshold": 0.1,
            "auto_quarantine_threshold": 0.9,
            "dmca_compliance_mode": True,
            "legal_notice_template": "standard",
            "monitoring_platforms": [
                "youtube", "vimeo", "dailymotion", "twitch",
                "instagram", "facebook", "twitter", "tiktok"
            ],
            "scan_frequencies": {
                "high_priority": 15,  # minutes
                "medium_priority": 60,
                "low_priority": 240
            }
        }
    
    def _init_components(self):
        """Initialize protection engine components"""
        self.logger.info("Initializing Content Protection Engine...")
        
        # Create default protection policy
        default_policy = ProtectionPolicy(
            policy_id="default",
            name="Default Protection Policy",
            description="Standard content protection with comprehensive monitoring",
            enabled_rules=[
                ProtectionRule.COPYRIGHT_DETECTION,
                ProtectionRule.DUPLICATE_DETECTION,
                ProtectionRule.WATERMARK_VERIFICATION,
                ProtectionRule.UNAUTHORIZED_ACCESS
            ],
            severity_thresholds={
                "similarity": 0.85,
                "confidence": 0.8,
                "threat_level": 0.7
            },
            auto_actions={
                "critical": ["quarantine", "notify_legal", "issue_takedown"],
                "high": ["flag_for_review", "notify_owner"],
                "medium": ["log_violation", "schedule_review"],
                "low": ["log_violation"]
            },
            notification_settings={
                "email_alerts": True,
                "dashboard_notifications": True,
                "webhook_notifications": False,
                "sms_alerts": False
            },
            monitoring_frequency=60,
            retention_period_days=365
        )
        
        self.policies["default"] = default_policy
        
        self.logger.info("Content Protection Engine initialized successfully")
    
    async def protect_content(
        self,
        content_data: Dict[str, Any],
        policy_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Protect content by scanning for violations and setting up monitoring
        
        Args:
            content_data: Content information and metadata
            policy_id: Protection policy to apply
            
        Returns:
            Protection results and recommendations
        """



        try:
            self.logger.info(f"Starting content protection for: {content_data.get('content_id')}")
            
            # Get protection policy
            policy = self.policies.get(policy_id)
            if not policy:
                raise ValueError(f"Protection policy not found: {policy_id}")
            
            results = {
                "content_id": content_data.get('content_id'),
                "policy_applied": policy_id,
                "protection_timestamp": datetime.now(timezone.utc),
                "violations_detected": [],
                "monitoring_setup": {},
                "recommendations": []
            }
            
            # Perform initial content scanning
            violations = await self._scan_content_comprehensive(content_data, policy)
            results["violations_detected"] = [self._violation_to_dict(v) for v in violations]
            
            # Store violations
            for violation in violations:
                self.violations[violation.violation_id] = violation
            
            # Set up continuous monitoring
            if self.config["monitoring_enabled"]:
                monitoring_target = await self._setup_monitoring(content_data, policy)
                if monitoring_target:
                    self.monitoring_targets[monitoring_target.target_id] = monitoring_target
                    results["monitoring_setup"] = {
                        "target_id": monitoring_target.target_id,
                        "platforms": monitoring_target.monitoring_platforms,
                        "frequency_minutes": monitoring_target.scan_frequency_minutes,
                        "status": monitoring_target.monitoring_status.value
                    }
            
            # Generate protection recommendations
            recommendations = await self._generate_recommendations(content_data, violations, policy)
            results["recommendations"] = recommendations
            
            # Update metrics
            self._update_metrics(violations)
            
            self.logger.info(f"Content protection completed for: {content_data.get('content_id')}")
            return results
            
        except Exception as e:
            self.logger.error(f"Content protection failed: {e}")
            raise
    
    async def _scan_content_comprehensive(
        self,
        content_data: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Perform comprehensive content scanning"""
        all_violations = []
        
        # Run enabled scanners based on policy
        for rule in policy.enabled_rules:
            scanner = None
            
            if rule == ProtectionRule.DUPLICATE_DETECTION:
                scanner = self.scanners.get('duplicate')
            elif rule == ProtectionRule.WATERMARK_VERIFICATION:
                scanner = self.scanners.get('watermark')
            
            if scanner:
                try:
                    violations = await scanner.scan_content(content_data, policy)
                    all_violations.extend(violations)
                except Exception as e:
                    self.logger.error(f"Scanner {rule.value} failed: {e}")
        
        return all_violations
    
    async def _setup_monitoring(
        self,
        content_data: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> Optional[MonitoringTarget]:
        """Set up continuous monitoring for content"""



        try:
            fingerprint = content_data.get('fingerprint')
            if not fingerprint:
                return None
            
            # Generate search keywords based on content metadata
            keywords = self._generate_search_keywords(content_data)
            
            monitoring_target = MonitoringTarget(
                target_id=str(uuid.uuid4()),
                content_id=content_data.get('content_id', ''),
                fingerprint_hash=fingerprint.get('primary_hash', ''),
                monitoring_platforms=self.config["monitoring_platforms"],
                search_keywords=keywords,
                monitoring_status=MonitoringStatus.ACTIVE,
                scan_frequency_minutes=policy.monitoring_frequency
            )
            
            # Schedule first scan
            monitoring_target.next_scan_at = datetime.now(timezone.utc) + timedelta(
                minutes=monitoring_target.scan_frequency_minutes
            )
            
            return monitoring_target
            
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring: {e}")
            return None
    
    def _generate_search_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """Generate search keywords for content monitoring"""
        keywords = []
        
        # Add title and description keywords
        metadata = content_data.get('metadata', {})
        if hasattr(metadata, 'title') and metadata.title:
            keywords.extend(metadata.title.split()[:5])
        
        if hasattr(metadata, 'description') and metadata.description:
            # Extract key phrases from description
            description_words = metadata.description.split()[:10]
            keywords.extend(description_words)
        
        # Add content-specific keywords
        if hasattr(metadata, 'keywords'):
            keywords.extend(metadata.keywords[:10])
        
        # Clean and filter keywords
        filtered_keywords = []
        for keyword in keywords:
            # Remove special characters and short words
            clean_keyword = re.sub(r'[^\w\s]', '', keyword.lower())
            if len(clean_keyword) >= 3:
                filtered_keywords.append(clean_keyword)
        
        return list(set(filtered_keywords))[:20]  # Limit to 20 unique keywords
    
    async def _generate_recommendations(
        self,
        content_data: Dict[str, Any],
        violations: List[ContentViolation],
        policy: ProtectionPolicy
    ) -> List[Dict[str, str]]:
        """Generate protection recommendations"""
        recommendations = []
        
        # Analyze violations and suggest actions
        if violations:
            high_risk_violations = [v for v in violations if v.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
            
            if high_risk_violations:
                recommendations.append({
                    "type": "immediate_action",
                    "priority": "high",
                    "action": "Review and address high-risk violations immediately",
                    "details": f"Found {len(high_risk_violations)} high-risk violations requiring attention"
                })
            
            # Check for watermark violations
            watermark_violations = [v for v in violations if v.violation_type == ViolationType.WATERMARK_REMOVAL]
            if watermark_violations:
                recommendations.append({
                    "type": "watermark",
                    "priority": "medium",
                    "action": "Add or enhance watermarking",
                    "details": "Consider adding visible or invisible watermarks to protect content"
                })
        
        # General protection recommendations
        if not content_data.get('has_watermark', False):
            recommendations.append({
                "type": "watermark",
                "priority": "medium",
                "action": "Consider adding watermark protection",
                "details": "Watermarks can help deter unauthorized use and aid in violation detection"
            })
        
        if not self.config["monitoring_enabled"]:
            recommendations.append({
                "type": "monitoring",
                "priority": "high",
                "action": "Enable continuous monitoring",
                "details": "Continuous monitoring helps detect violations early"
            })
        
        return recommendations
    
    def _update_metrics(self, violations: List[ContentViolation]):
        """Update protection metrics"""
        self.metrics.total_scans += 1
        self.metrics.violations_detected += len(violations)
        
        for violation in violations:
            threat_key = violation.threat_level.value
            self.metrics.threat_distribution[threat_key] = (
                self.metrics.threat_distribution.get(threat_key, 0) + 1
            )
        
        self.metrics.last_updated = datetime.now(timezone.utc)
    
    async def scan_monitoring_targets(self) -> Dict[str, Any]:
        """Scan all active monitoring targets"""
        scan_results = {
            "targets_scanned": 0,
            "violations_found": 0,
            "errors": 0,
            "scan_timestamp": datetime.now(timezone.utc)
        }
        
        current_time = datetime.now(timezone.utc)
        
        for target_id, target in self.monitoring_targets.items():
            if (target.monitoring_status == MonitoringStatus.ACTIVE and
                target.next_scan_at and target.next_scan_at <= current_time):
                
                try:
                    violations = await self._scan_monitoring_target(target)
                    scan_results["targets_scanned"] += 1
                    scan_results["violations_found"] += len(violations)
                    
                    # Store new violations
                    for violation in violations:
                        self.violations[violation.violation_id] = violation
                        target.violation_count += 1
                        target.last_violation_at = datetime.now(timezone.utc)
                    
                    # Update scan schedule
                    target.last_scanned = current_time
                    target.next_scan_at = current_time + timedelta(minutes=target.scan_frequency_minutes)
                    
                except Exception as e:
                    self.logger.error(f"Failed to scan monitoring target {target_id}: {e}")
                    scan_results["errors"] += 1
        
        return scan_results
    
    async def _scan_monitoring_target(self, target: MonitoringTarget) -> List[ContentViolation]:
        """Scan a specific monitoring target"""
        violations = []
        
        # Get reference fingerprint (would be loaded from database)
        reference_fingerprint = {
            'content_id': target.content_id,
            'primary_hash': target.fingerprint_hash
        }
        
        # Get applicable policy
        policy = self.policies.get("default")  # Could be target-specific
        
        # Search each platform for potential violations
        for platform in target.monitoring_platforms:
            try:
                platform_violations = await self._scan_platform(
                    platform, target.search_keywords, reference_fingerprint, policy
                )
                violations.extend(platform_violations)
                
            except Exception as e:
                self.logger.error(f"Failed to scan platform {platform}: {e}")
        
        return violations
    
    async def _scan_platform(
        self,
        platform: str,
        keywords: List[str],
        reference_fingerprint: Dict[str, Any],
        policy: ProtectionPolicy
    ) -> List[ContentViolation]:
        """Scan a specific platform for violations"""
        violations = []
        
        try:
            # Search platform for content matching keywords
            search_results = await self._search_platform_content(platform, keywords)
            
            # Analyze each result for potential violations
            for result in search_results:
                # Use duplicate scanner to check similarity
                scanner = self.scanners.get('duplicate')
                if scanner:
                    result_violations = await scanner.scan_url(
                        result['url'], reference_fingerprint, policy
                    )
                    
                    # Add platform information to violations
                    for violation in result_violations:
                        violation.affected_platforms = [platform]
                        violation.evidence['search_result'] = result
                    
                    violations.extend(result_violations)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Platform scanning failed for {platform}: {e}")
            return violations
    
    async def _search_platform_content(
        self, 
        platform: str, 
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Search platform for content matching keywords"""
        # This would integrate with platform APIs
        # For demonstration, returning mock results
        search_query = " ".join(keywords[:3])
        
        return [
            {
                'url': f'https://{platform}.com/content/123',
                'title': f'Content matching {search_query}',
                'platform': platform,
                'found_keywords': keywords[:2]
            }
        ]
    
    def _violation_to_dict(self, violation: ContentViolation) -> Dict[str, Any]:
        """Convert violation object to dictionary"""



        return {
            'violation_id': violation.violation_id,
            'content_id': violation.content_id,
            'violation_type': violation.violation_type.value,
            'threat_level': violation.threat_level.value,
            'confidence_score': violation.confidence_score,
            'description': violation.description,
            'evidence': violation.evidence,
            'source_url': violation.source_url,
            'detected_at': violation.detected_at.isoformat(),
            'resolved_at': violation.resolved_at.isoformat() if violation.resolved_at else None,
            'false_positive': violation.false_positive,
            'review_status': violation.review_status,
            'affected_platforms': violation.affected_platforms
        }
    
    async def resolve_violation(
        self,
        violation_id: str,
        resolution_action: str,
        reviewer_notes: Optional[str] = None
    ) -> bool:
        """Resolve a content violation"""



        try:
            if violation_id not in self.violations:
                raise ValueError(f"Violation not found: {violation_id}")
            
            violation = self.violations[violation_id]
            violation.resolved_at = datetime.now(timezone.utc)
            violation.resolution_action = resolution_action
            violation.reviewer_notes = reviewer_notes
            violation.review_status = "resolved"
            
            # Update metrics
            self.metrics.resolved_violations += 1
            
            self.logger.info(f"Violation {violation_id} resolved with action: {resolution_action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve violation {violation_id}: {e}")
            return False
    
    async def mark_false_positive(self, violation_id: str, reviewer_notes: Optional[str] = None) -> bool:
        """Mark a violation as false positive"""



        try:
            if violation_id not in self.violations:
                raise ValueError(f"Violation not found: {violation_id}")
            
            violation = self.violations[violation_id]
            violation.false_positive = True
            violation.review_status = "false_positive"
            violation.reviewer_notes = reviewer_notes
            violation.resolved_at = datetime.now(timezone.utc)
            
            # Update metrics
            self.metrics.false_positives += 1
            
            self.logger.info(f"Violation {violation_id} marked as false positive")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark false positive {violation_id}: {e}")
            return False
    
    def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get protection status for specific content"""
        # Find monitoring target
        monitoring_target = None
        for target in self.monitoring_targets.values():
            if target.content_id == content_id:
                monitoring_target = target
                break
        
        # Find violations
        content_violations = [
            v for v in self.violations.values() 
            if v.content_id == content_id
        ]
        
        # Calculate threat level
        max_threat = ThreatLevel.NONE
        for violation in content_violations:
            if violation.threat_level.value > max_threat.value:
                max_threat = violation.threat_level
        
        return {
            'content_id': content_id,
            'monitoring_active': monitoring_target is not None,
            'monitoring_status': monitoring_target.monitoring_status.value if monitoring_target else None,
            'total_violations': len(content_violations),
            'unresolved_violations': len([v for v in content_violations if not v.resolved_at]),
            'max_threat_level': max_threat.value,
            'last_scan': monitoring_target.last_scanned.isoformat() if monitoring_target and monitoring_target.last_scanned else None,
            'next_scan': monitoring_target.next_scan_at.isoformat() if monitoring_target and monitoring_target.next_scan_at else None
        }
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive protection metrics"""
        # Update pending violations count
        self.metrics.pending_violations = len([
            v for v in self.violations.values() 
            if v.review_status == "pending"
        ])
        
        return {
            'total_scans': self.metrics.total_scans,
            'violations_detected': self.metrics.violations_detected,
            'false_positives': self.metrics.false_positives,
            'resolved_violations': self.metrics.resolved_violations,
            'pending_violations': self.metrics.pending_violations,
            'content_protected': len(self.monitoring_targets),
            'monitoring_coverage': len([t for t in self.monitoring_targets.values() if t.monitoring_status == MonitoringStatus.ACTIVE]),
            'threat_distribution': self.metrics.threat_distribution,
            'last_updated': self.metrics.last_updated.isoformat()
        }
    
    async def create_protection_policy(self, policy_data: Dict[str, Any]) -> str:
        """Create a new protection policy"""



        try:
            policy = ProtectionPolicy(
                policy_id=policy_data.get('policy_id', str(uuid.uuid4())),
                name=policy_data['name'],
                description=policy_data['description'],
                enabled_rules=[ProtectionRule(rule) for rule in policy_data['enabled_rules']],
                severity_thresholds=policy_data['severity_thresholds'],
                auto_actions=policy_data['auto_actions'],
                notification_settings=policy_data['notification_settings'],
                monitoring_frequency=policy_data['monitoring_frequency'],
                retention_period_days=policy_data['retention_period_days']
            )
            
            self.policies[policy.policy_id] = policy
            
            self.logger.info(f"Created protection policy: {policy.name}")
            return policy.policy_id
            
        except Exception as e:
            self.logger.error(f"Failed to create protection policy: {e}")
            raise
    
    def get_protection_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get all protection policies"""



        return {
            policy_id: {
                'name': policy.name,
                'description': policy.description,
                'enabled_rules': [rule.value for rule in policy.enabled_rules],
                'monitoring_frequency': policy.monitoring_frequency,
                'created_at': policy.created_at.isoformat(),
                'updated_at': policy.updated_at.isoformat()
            }
            for policy_id, policy in self.policies.items()
        }
