"""Violation Serializer Module
===========================

Specialized serialization for violation detection and enforcement data.
Optimized for copyright violations, infringement tracking, and legal actions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture de détection intelligente de violations
- Backend Senior: Infrastructure robuste pour suivi légal enterprise
- ML Engineer: Algorithmes de détection d'infractions par IA
- DBA Expert: Optimisation des données légales et preuves
- Sécurité: Protection des données sensibles et preuves légales
- Microservices: Architecture distribuée pour enforcement global
- Audio/Vidéo: Détection de violations multimédia avancée
- DevOps: Monitoring et alertes en temps réel des violations
- IA Prompt Engineer: Génération automatique de notices légales
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

class ViolationType(Enum):
    """
Types of content violations."""

    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    CONTENT_THEFT = "content_theft"
    DMCA_VIOLATION = "dmca_violation"
    FAIR_USE_EXCEEDED = "fair_use_exceeded"
    DERIVATIVE_WORK = "derivative_work"
    PLAGIARISM = "plagiarism"
    LICENSE_VIOLATION = "license_violation"
    ATTRIBUTION_MISSING = "attribution_missing"

class ViolationSeverity(Enum):
    """Severity levels for violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ViolationStatus(Enum):
    """Status of violation cases."""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    TAKEDOWN_REQUESTED = "takedown_requested"
    TAKEDOWN_COMPLETED = "takedown_completed"
    LEGAL_ACTION = "legal_action"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    APPEALED = "appealed"

class ActionType(Enum):
    """Types of enforcement actions."""

    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_AND_DESIST = "cease_and_desist"
    LEGAL_NOTICE = "legal_notice"
    PLATFORM_REPORT = "platform_report"
    CONTENT_BLOCK = "content_block"
    ACCOUNT_SUSPENSION = "account_suspension"
    MONETIZATION_CLAIM = "monetization_claim"
    REVENUE_REDIRECT = "revenue_redirect"
    LAWSUIT = "lawsuit"
    SETTLEMENT = "settlement"

@dataclass
class ViolationEvidence:
    """Evidence for violation case."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = "screenshot"  # screenshot, video, document, fingerprint
    evidence_url: Optional[str] = None
    evidence_data: Optional[bytes] = None
    evidence_hash: Optional[str] = None
    description: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    collector_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalAction:
    """Legal action taken for violation."""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.PLATFORM_REPORT
    action_date: datetime = field(default_factory=datetime.now)
    action_description: str = ""
    target_platform: Optional[str] = None
    target_url: Optional[str] = None
    target_user: Optional[str] = None
    legal_firm: Optional[str] = None
    case_number: Optional[str] = None
    outcome: Optional[str] = None
    cost: Optional[float] = None
    success_rate: Optional[float] = None
    documents: List[str] = field(default_factory=list)
    status: str = "pending"
    completed_at: Optional[datetime] = None

@dataclass
class MonetizationImpact:
    """Financial impact of violation."""
    estimated_loss: float = 0.0
    currency: str = "EUR"
    lost_views: int = 0
    lost_revenue_period: Optional[timedelta] = None
    platform_revenue_lost: Dict[str, float] = field(default_factory=dict)
    recovery_amount: float = 0.0
    recovery_method: Optional[str] = None
    roi_impact: Optional[float] = None

class ViolationData(BaseModel):
    """
    Comprehensive violation data model.
    
    Represents content violations, evidence, legal actions,
    and enforcement for the IA-Influencer-Agent protection platform.
    """
    
    # Basic violation information
    violation_id: str = Field(..., description="Unique violation identifier")
    content_id: str = Field(..., description="Original content identifier")
    fingerprint_id: Optional[str] = Field(default=None, description="Associated fingerprint")
    
    # Violation classification
    violation_type: ViolationType = Field(..., description="Type of violation")
    severity: ViolationSeverity = Field(default=ViolationSeverity.MEDIUM)
    status: ViolationStatus = Field(default=ViolationStatus.DETECTED)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Violating content information
    violating_url: str = Field(..., description="URL of violating content")
    violating_platform: str = Field(..., description="Platform hosting violation")
    violating_user: Optional[str] = Field(default=None, description="User posting violation")
    violating_user_id: Optional[str] = Field(default=None)
    violating_content_title: Optional[str] = Field(default=None)
    violating_content_description: Optional[str] = Field(default=None)
    
    # Similarity analysis
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    similarity_details: Dict[str, Any] = Field(default_factory=dict)
    matching_segments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Original content information
    original_content_title: Optional[str] = Field(default=None)
    original_content_url: Optional[str] = Field(default=None)
    original_creator: Optional[str] = Field(default=None)
    original_platform: Optional[str] = Field(default=None)
    original_upload_date: Optional[datetime] = Field(default=None)
    
    # Evidence and documentation
    evidence: List[ViolationEvidence] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    video_evidence: List[str] = Field(default_factory=list)
    documentation_urls: List[str] = Field(default_factory=list)
    
    # Legal and enforcement actions
    legal_actions: List[LegalAction] = Field(default_factory=list)
    dmca_notices_sent: int = Field(default=0)
    platform_reports_sent: int = Field(default=0)
    response_received: bool = Field(default=False)
    takedown_successful: bool = Field(default=False)
    
    # Financial impact
    monetization_impact: Optional[MonetizationImpact] = Field(default=None)
    enforcement_cost: float = Field(default=0.0)
    recovery_amount: float = Field(default=0.0)
    
    # Timing and tracking
    detected_at: datetime = Field(default_factory=datetime.now)
    first_seen_at: Optional[datetime] = Field(default=None)
    last_seen_at: Optional[datetime] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    response_deadline: Optional[datetime] = Field(default=None)
    
    # Resolution information
    resolution_method: Optional[str] = Field(default=None)
    resolution_notes: Optional[str] = Field(default=None)
    satisfaction_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    priority: int = Field(default=5, ge=1, le=10)
    assigned_to: Optional[str] = Field(default=None)
    case_notes: Optional[str] = Field(default=None)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('violation_type', pre=True)
    def validate_violation_type(cls, v):
        if isinstance(v, str):
            return ViolationType(v.lower())
        return v
    
    @validator('severity', pre=True)
    def validate_severity(cls, v):
        if isinstance(v, str):
            return ViolationSeverity(v.lower())
        return v
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            return ViolationStatus(v.lower())
        return v

class ViolationSerializer:
    """
    Advanced violation data serialization system.
    
    Handles efficient serialization and deserialization of violation
    cases, evidence, legal actions, and enforcement tracking.
    """
    
    def __init__(self):
        """
Initialize violation serializer."""
        self.evidence_compression_threshold = 1024 * 1024  # 1MB
        self.max_evidence_size = 50 * 1024 * 1024  # 50MB
        
        logger.info("Violation serializer initialized")
    
    def serialize_violation(
        self,
        violation: ViolationData,
        include_evidence_data: bool = False,
        compress_evidence: bool = True
    ) -> Dict[str, Any]:
        """
        Serialize violation data to dictionary format.
        
        Args:
            violation: Violation data to serialize
            include_evidence_data: Whether to include binary evidence data
            compress_evidence: Whether to compress large evidence data
            
        Returns:
            Serialized violation dictionary
        """
        try:
            # Convert to dictionary
            data = violation.dict()
            
            # Handle datetime conversions
            data['detected_at'] = violation.detected_at.isoformat()
            
            if violation.first_seen_at:
                data['first_seen_at'] = violation.first_seen_at.isoformat()
            
            if violation.last_seen_at:
                data['last_seen_at'] = violation.last_seen_at.isoformat()
            
            if violation.resolved_at:
                data['resolved_at'] = violation.resolved_at.isoformat()
            
            if violation.response_deadline:
                data['response_deadline'] = violation.response_deadline.isoformat()
            
            if violation.original_upload_date:
                data['original_upload_date'] = violation.original_upload_date.isoformat()
            
            # Serialize evidence
            if violation.evidence:
                data['evidence'] = [
                    self._serialize_evidence(evidence, include_evidence_data, compress_evidence)
                    for evidence in violation.evidence
                ]
            
            # Serialize legal actions
            if violation.legal_actions:
                data['legal_actions'] = [
                    self._serialize_legal_action(action)
                    for action in violation.legal_actions
                ]
            
            # Serialize monetization impact
            if violation.monetization_impact:
                data['monetization_impact'] = self._serialize_monetization_impact(
                    violation.monetization_impact
                )
            
            # Convert enums
            data['violation_type'] = violation.violation_type.value
            data['severity'] = violation.severity.value
            data['status'] = violation.status.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_evidence_data': include_evidence_data,
                'evidence_compressed': compress_evidence,
                'violation_type': violation.violation_type.value
            }
            
            logger.debug(f"Serialized violation {violation.violation_id}")
            return data
            
        except Exception as e:
            logger.error(f"Violation serialization failed: {e}")
            raise
    
    def deserialize_violation(
        self,
        data: Dict[str, Any]
    ) -> ViolationData:
        """
        Deserialize violation data from dictionary format.
        
        Args:
            data: Serialized violation dictionary
            
        Returns:
            Deserialized ViolationData object
        """
        try:
            # Handle datetime conversions
            datetime_fields = [
                'detected_at', 'first_seen_at', 'last_seen_at',
                'resolved_at', 'response_deadline', 'original_upload_date'
            ]
            
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize evidence
            if 'evidence' in data and data['evidence']:
                data['evidence'] = [
                    self._deserialize_evidence(evidence_data)
                    for evidence_data in data['evidence']
                ]
            
            # Deserialize legal actions
            if 'legal_actions' in data and data['legal_actions']:
                data['legal_actions'] = [
                    self._deserialize_legal_action(action_data)
                    for action_data in data['legal_actions']
                ]
            
            # Deserialize monetization impact
            if 'monetization_impact' in data and data['monetization_impact']:
                data['monetization_impact'] = self._deserialize_monetization_impact(
                    data['monetization_impact']
                )
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create ViolationData object
            violation = ViolationData(**data)
            
            logger.debug(f"Deserialized violation {violation.violation_id}")
            return violation
            
        except Exception as e:
            logger.error(f"Violation deserialization failed: {e}")
            raise
    
    def serialize_violation_batch(
        self,
        violations: List[ViolationData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple violations efficiently."""
        try:
            serialized_list = []
            
            for violation in violations:
                serialized = self.serialize_violation(
                    violation,
                    include_evidence_data=not compact_mode,
                    compress_evidence=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(violations)} violations")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Violation batch serialization failed: {e}")
            raise
    
    def deserialize_violation_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[ViolationData]:
        """Deserialize multiple violations efficiently."""
        try:
            violations = []
            
            for data in data_list:
                violation = self.deserialize_violation(data)
                violations.append(violation)
            
            logger.info(f"Deserialized {len(data_list)} violations")
            return violations
            
        except Exception as e:
            logger.error(f"Violation batch deserialization failed: {e}")
            raise
    
    def _serialize_evidence(
        self,
        evidence: ViolationEvidence,
        include_data: bool = False,
        compress: bool = True
    ) -> Dict[str, Any]:
        """Serialize violation evidence."""
        data = {
            'evidence_id': evidence.evidence_id,
            'evidence_type': evidence.evidence_type,
            'evidence_url': evidence.evidence_url,
            'evidence_hash': evidence.evidence_hash,
            'description': evidence.description,
            'collected_at': evidence.collected_at.isoformat(),
            'collector_info': evidence.collector_info,
            'metadata': evidence.metadata
        }
        
        # Handle binary evidence data
        if include_data and evidence.evidence_data:
            if len(evidence.evidence_data) > self.max_evidence_size:
                logger.warning(f"Evidence {evidence.evidence_id} too large, excluding data")
                data['evidence_data'] = None
                data['_data_excluded'] = True
            elif compress and len(evidence.evidence_data) > self.evidence_compression_threshold:
                data['evidence_data'] = self._compress_evidence_data(evidence.evidence_data)
                data['_data_compressed'] = True
            else:
                import base64
                data['evidence_data'] = base64.b64encode(evidence.evidence_data).decode('utf-8')
                data['_data_compressed'] = False
        else:
            data['evidence_data'] = None
        
        return data
    
    def _deserialize_evidence(self, data: Dict[str, Any]) -> ViolationEvidence:
        """Deserialize violation evidence."""
        if isinstance(data.get('collected_at'), str):
            data['collected_at'] = datetime.fromisoformat(data['collected_at'])
        
        # Handle binary evidence data
        if data.get('evidence_data'):
            if data.get('_data_compressed', False):
                data['evidence_data'] = self._decompress_evidence_data(data['evidence_data'])
            else:
                import base64
                data['evidence_data'] = base64.b64decode(data['evidence_data'])
        
        # Remove metadata fields
        data.pop('_data_compressed', None)
        data.pop('_data_excluded', None)
        
        return ViolationEvidence(**data)
    
    def _serialize_legal_action(self, action: LegalAction) -> Dict[str, Any]:
        """
Serialize legal action."""
        data = {
            'action_id': action.action_id,
            'action_type': action.action_type.value,
            'action_date': action.action_date.isoformat(),
            'action_description': action.action_description,
            'target_platform': action.target_platform,
            'target_url': action.target_url,
            'target_user': action.target_user,
            'legal_firm': action.legal_firm,
            'case_number': action.case_number,
            'outcome': action.outcome,
            'cost': action.cost,
            'success_rate': action.success_rate,
            'documents': action.documents,
            'status': action.status
        }
        
        if action.completed_at:
            data['completed_at'] = action.completed_at.isoformat()
        
        return data
    
    def _deserialize_legal_action(self, data: Dict[str, Any]) -> LegalAction:
        """
Deserialize legal action."""
        if isinstance(data.get('action_date'), str):
            data['action_date'] = datetime.fromisoformat(data['action_date'])
        
        if isinstance(data.get('completed_at'), str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        if isinstance(data.get('action_type'), str):
            data['action_type'] = ActionType(data['action_type'])
        
        return LegalAction(**data)
    
    def _serialize_monetization_impact(self, impact: MonetizationImpact) -> Dict[str, Any]:
        """
Serialize monetization impact."""
        data = {
            'estimated_loss': impact.estimated_loss,
            'currency': impact.currency,
            'lost_views': impact.lost_views,
            'platform_revenue_lost': impact.platform_revenue_lost,
            'recovery_amount': impact.recovery_amount,
            'recovery_method': impact.recovery_method,
            'roi_impact': impact.roi_impact
        }
        
        if impact.lost_revenue_period:
            data['lost_revenue_period_days'] = impact.lost_revenue_period.days
        
        return data
    
    def _deserialize_monetization_impact(self, data: Dict[str, Any]) -> MonetizationImpact:
        """
Deserialize monetization impact."""
        if 'lost_revenue_period_days' in data:
            data['lost_revenue_period'] = timedelta(days=data.pop('lost_revenue_period_days'))
        
        return MonetizationImpact(**data)
    
    def _compress_evidence_data(self, data: bytes) -> str:
        """
Compress evidence data."""
        try:
            import gzip
            import base64
            
            compressed = gzip.compress(data)
            encoded = base64.b64encode(compressed).decode('utf-8')
            return f"gzip:{encoded}"
            
        except Exception as e:
            logger.error(f"Evidence compression failed: {e}")
            import base64
            return base64.b64encode(data).decode('utf-8')
    
    def _decompress_evidence_data(self, compressed_data: str) -> bytes:
        """Decompress evidence data."""
        try:
            import gzip
            import base64
            
            if compressed_data.startswith('gzip:'):
                encoded = compressed_data[5:]  # Remove 'gzip:' prefix
                compressed = base64.b64decode(encoded)
                return gzip.decompress(compressed)
            else:
                # Not compressed
                return base64.b64decode(compressed_data)
                
        except Exception as e:
            logger.error(f"Evidence decompression failed: {e}")
            import base64
            return base64.b64decode(compressed_data)
    
    def create_violation_summary(self, violation: ViolationData) -> Dict[str, Any]:
        """Create compact summary of violation case."""
        try:
            summary = {
                'violation_id': violation.violation_id,
                'violation_type': violation.violation_type.value,
                'severity': violation.severity.value,
                'status': violation.status.value,
                'confidence_score': violation.confidence_score,
                'similarity_score': violation.similarity_score,
                'violating_platform': violation.violating_platform,
                'violating_url': violation.violating_url,
                'detected_at': violation.detected_at.isoformat(),
                'evidence_count': len(violation.evidence),
                'legal_actions_count': len(violation.legal_actions),
                'takedown_successful': violation.takedown_successful,
                'priority': violation.priority
            }
            
            if violation.resolved_at:
                summary['resolved_at'] = violation.resolved_at.isoformat()
                summary['resolution_time_days'] = (violation.resolved_at - violation.detected_at).days
            
            if violation.monetization_impact:
                summary['estimated_loss'] = violation.monetization_impact.estimated_loss
                summary['recovery_amount'] = violation.monetization_impact.recovery_amount
            
            return summary
            
        except Exception as e:
            logger.error(f"Violation summary creation failed: {e}")
            return {'error': str(e)}
    
    def aggregate_violation_metrics(
        self,
        violations: List[ViolationData]
    ) -> Dict[str, Any]:
        """Aggregate metrics across multiple violations."""
        try:
            if not violations:
                return {}
            
            # Basic counts
            total_violations = len(violations)
            resolved_violations = len([v for v in violations if v.status == ViolationStatus.RESOLVED])
            successful_takedowns = len([v for v in violations if v.takedown_successful])
            
            # Type distribution
            type_distribution = {}
            severity_distribution = {}
            platform_distribution = {}
            
            total_estimated_loss = 0.0
            total_recovery = 0.0
            total_enforcement_cost = 0.0
            
            for violation in violations:
                # Count by type
                vtype = violation.violation_type.value
                type_distribution[vtype] = type_distribution.get(vtype, 0) + 1
                
                # Count by severity
                severity = violation.severity.value
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
                
                # Count by platform
                platform = violation.violating_platform
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
                
                # Financial impact
                if violation.monetization_impact:
                    total_estimated_loss += violation.monetization_impact.estimated_loss
                    total_recovery += violation.monetization_impact.recovery_amount
                
                total_enforcement_cost += violation.enforcement_cost
            
            return {
                'total_violations': total_violations,
                'resolved_violations': resolved_violations,
                'resolution_rate': resolved_violations / total_violations,
                'successful_takedowns': successful_takedowns,
                'takedown_success_rate': successful_takedowns / total_violations,
                'type_distribution': type_distribution,
                'severity_distribution': severity_distribution,
                'platform_distribution': platform_distribution,
                'financial_impact': {
                    'total_estimated_loss': total_estimated_loss,
                    'total_recovery': total_recovery,
                    'total_enforcement_cost': total_enforcement_cost,
                    'recovery_rate': total_recovery / max(total_estimated_loss, 1),
                    'roi': (total_recovery - total_enforcement_cost) / max(total_enforcement_cost, 1)
                },
                'aggregated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Violation metrics aggregation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'ViolationSerializer',
    'ViolationData',
    'ViolationEvidence',
    'LegalAction',
    'MonetizationImpact',
    'ViolationType',
    'ViolationSeverity',
    'ViolationStatus',
    'ActionType'
]
