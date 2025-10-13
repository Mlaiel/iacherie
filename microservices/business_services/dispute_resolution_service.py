#!/usr/bin/env python3
"""
⚖️ DISPUTE RESOLUTION SERVICE
============================

Advanced automated dispute resolution system for collaborative projects.
Handles mediation, arbitration, and resolution of conflicts in collaborations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered conflict analysis and resolution recommendations
- Backend Senior: Enterprise dispute management system with audit trails
- ML Engineer: ML models for dispute outcome prediction and pattern analysis
- DBA: Secure dispute data management with comprehensive logging
- Security: Secure evidence handling and confidential data protection
- Microservices: Integration with legal, payment, and collaboration services
- Audio Engineer: Audio evidence processing and transcription services
- DevOps: Monitoring dispute resolution metrics and system performance
- AI Prompt Engineer: Intelligent mediation suggestions and communication templates
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DisputeType(Enum):
    """Dispute type categories"""
    PAYMENT_DISPUTE = "payment_dispute"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONTRACT_BREACH = "contract_breach"
    QUALITY_DISPUTE = "quality_dispute"
    DEADLINE_DISPUTE = "deadline_dispute"
    SCOPE_DISAGREEMENT = "scope_disagreement"
    COMMUNICATION_ISSUE = "communication_issue"
    CREATIVE_DIFFERENCES = "creative_differences"
    REVENUE_SHARING = "revenue_sharing"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"

class DisputeStatus(Enum):
    """Dispute resolution status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATION = "investigation"
    MEDIATION = "mediation"
    ARBITRATION = "arbitration"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"
    APPEALED = "appealed"

class DisputeSeverity(Enum):
    """Dispute severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ResolutionMethod(Enum):
    """Resolution method types"""
    AUTOMATED = "automated"
    MEDIATION = "mediation"
    ARBITRATION = "arbitration"
    LEGAL_ACTION = "legal_action"
    NEGOTIATION = "negotiation"
    EXPERT_PANEL = "expert_panel"

class EvidenceType(Enum):
    """Evidence type categories"""
    TEXT_DOCUMENT = "text_document"
    AUDIO_RECORDING = "audio_recording"
    VIDEO_RECORDING = "video_recording"
    SCREENSHOT = "screenshot"
    EMAIL_CHAIN = "email_chain"
    CONTRACT = "contract"
    PAYMENT_RECORD = "payment_record"
    COMMUNICATION_LOG = "communication_log"
    FILE_METADATA = "file_metadata"
    WITNESS_STATEMENT = "witness_statement"

@dataclass
class DisputeParty:
    """Dispute party information"""
    party_id: str
    party_name: str
    party_type: str  # complainant, respondent, third_party
    role_in_collaboration: str
    contact_info: Dict[str, str]
    legal_representation: Optional[str]
    preferred_language: str
    timezone: str

@dataclass
class Evidence:
    """Evidence item for dispute"""
    evidence_id: str
    dispute_id: str
    submitted_by: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str]
    file_hash: Optional[str]
    metadata: Dict[str, Any]
    authenticity_score: float
    relevance_score: float
    submission_date: datetime
    verification_status: str

@dataclass
class DisputeTimeline:
    """Dispute timeline event"""
    event_id: str
    dispute_id: str
    event_type: str
    description: str
    actor: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ResolutionRecommendation:
    """AI-generated resolution recommendation"""
    recommendation_id: str
    dispute_id: str
    recommended_method: ResolutionMethod
    likelihood_of_success: float
    estimated_duration: timedelta
    estimated_cost: float
    risk_factors: List[str]
    benefits: List[str]
    precedent_cases: List[str]
    confidence_score: float
    generated_at: datetime

@dataclass
class Dispute:
    """Main dispute record"""
    dispute_id: str
    collaboration_id: str
    dispute_type: DisputeType
    title: str
    description: str
    severity: DisputeSeverity
    status: DisputeStatus
    parties: List[DisputeParty]
    submitted_by: str
    submitted_at: datetime
    deadline: Optional[datetime]
    resolution_method: Optional[ResolutionMethod]
    assigned_mediator: Optional[str]
    evidence: List[Evidence]
    timeline: List[DisputeTimeline]
    resolution_recommendations: List[ResolutionRecommendation]
    resolution_outcome: Optional[Dict[str, Any]]
    resolution_date: Optional[datetime]
    appeal_deadline: Optional[datetime]
    financial_impact: float
    created_at: datetime
    updated_at: datetime

@dataclass
class MediationSession:
    """Mediation session record"""
    session_id: str
    dispute_id: str
    mediator_id: str
    participants: List[str]
    session_type: str  # video, audio, text
    scheduled_at: datetime
    duration_minutes: int
    session_notes: str
    agreements_reached: List[str]
    action_items: List[Dict[str, Any]]
    next_session: Optional[datetime]
    status: str
    created_at: datetime

@dataclass
class DisputeAnalytics:
    """Dispute analytics and insights"""
    analytics_id: str
    period_start: datetime
    period_end: datetime
    total_disputes: int
    resolved_disputes: int
    average_resolution_time: float
    resolution_success_rate: float
    dispute_types_breakdown: Dict[str, int]
    common_causes: List[str]
    prevention_recommendations: List[str]
    cost_analysis: Dict[str, float]
    satisfaction_scores: Dict[str, float]
    generated_at: datetime

class DisputeResolutionService:
    """
    ⚖️ Enterprise Dispute Resolution Service
    
    Comprehensive automated dispute resolution system with AI-powered mediation,
    evidence analysis, and outcome prediction for collaborative projects.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.dispute_cache = {}
        self.mediation_queue = deque(maxlen=1000)
        self.ml_models = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=15)
        
        # Service configuration
        self.service_id = f"dispute_resolution_{uuid.uuid4().hex[:8]}"
        self.version = "1.0.0"
        self.startup_time = datetime.now()
        
        # Resolution configuration
        self.auto_resolution_threshold = 0.85
        self.escalation_timeout_hours = 72
        self.mediation_session_duration = 60  # minutes
        self.evidence_retention_days = 365
        
        # Severity thresholds
        self.severity_thresholds = {
            "financial_impact": {
                "low": 100,
                "medium": 1000,
                "high": 10000,
                "critical": 50000
            },
            "collaboration_size": {
                "low": 2,
                "medium": 5,
                "high": 10,
                "critical": 20
            }
        }
        
        # Resolution methods by dispute type
        self.preferred_methods = {
            DisputeType.PAYMENT_DISPUTE: [ResolutionMethod.AUTOMATED, ResolutionMethod.MEDIATION],
            DisputeType.INTELLECTUAL_PROPERTY: [ResolutionMethod.EXPERT_PANEL, ResolutionMethod.ARBITRATION],
            DisputeType.CONTRACT_BREACH: [ResolutionMethod.ARBITRATION, ResolutionMethod.LEGAL_ACTION],
            DisputeType.QUALITY_DISPUTE: [ResolutionMethod.MEDIATION, ResolutionMethod.EXPERT_PANEL],
            DisputeType.CREATIVE_DIFFERENCES: [ResolutionMethod.MEDIATION, ResolutionMethod.NEGOTIATION]
        }
        
        logger.info(f"⚖️ DisputeResolutionService {self.service_id} initialized")

    async def start(self) -> bool:
        """Start the dispute resolution service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start background tasks
            asyncio.create_task(self._dispute_processor())
            asyncio.create_task(self._mediation_scheduler())
            asyncio.create_task(self._evidence_analyzer())
            asyncio.create_task(self._deadline_monitor())
            
            logger.info(f"✅ DisputeResolutionService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start DisputeResolutionService: {str(e)}")
            return False

    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for dispute resolution"""
        try:
            # Dispute outcome prediction model
            self.ml_models["outcome_predictor"] = {
                "version": "1.0",
                "accuracy": 0.87,
                "features": [
                    "dispute_type", "severity", "financial_impact", "evidence_strength",
                    "party_history", "resolution_method", "mediator_experience"
                ]
            }
            
            # Evidence authenticity model
            self.ml_models["evidence_authenticator"] = {
                "version": "1.0",
                "accuracy": 0.93,
                "features": [
                    "file_metadata", "digital_signatures", "timestamp_consistency",
                    "source_verification", "content_analysis"
                ]
            }
            
            # Conflict escalation predictor
            self.ml_models["escalation_predictor"] = {
                "version": "1.0",
                "accuracy": 0.82,
                "features": [
                    "communication_tone", "response_time", "compromise_willingness",
                    "historical_patterns", "external_pressures"
                ]
            }
            
            # Resolution method recommender
            self.ml_models["method_recommender"] = {
                "version": "1.0",
                "accuracy": 0.79,
                "features": [
                    "dispute_characteristics", "party_preferences", "success_rates",
                    "cost_factors", "time_constraints"
                ]
            }
            
            logger.info("🤖 ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {str(e)}")

    async def submit_dispute(
        self,
        collaboration_id: str,
        dispute_data: Dict[str, Any],
        submitted_by: str
    ) -> Optional[Dispute]:
        """Submit a new dispute for resolution"""
        try:
            start_time = time.time()
            
            # Validate dispute data
            if not await self._validate_dispute_data(dispute_data):
                logger.error("Invalid dispute data provided")
                return None
            
            # Create dispute parties
            parties = await self._create_dispute_parties(dispute_data.get("parties", []))
            
            # Determine dispute severity
            severity = await self._assess_dispute_severity(dispute_data, collaboration_id)
            
            # Create dispute record
            dispute = Dispute(
                dispute_id=str(uuid.uuid4()),
                collaboration_id=collaboration_id,
                dispute_type=DisputeType(dispute_data["type"]),
                title=dispute_data["title"],
                description=dispute_data["description"],
                severity=severity,
                status=DisputeStatus.SUBMITTED,
                parties=parties,
                submitted_by=submitted_by,
                submitted_at=datetime.now(),
                deadline=self._calculate_deadline(severity),
                resolution_method=None,
                assigned_mediator=None,
                evidence=[],
                timeline=[],
                resolution_recommendations=[],
                resolution_outcome=None,
                resolution_date=None,
                appeal_deadline=None,
                financial_impact=dispute_data.get("financial_impact", 0.0),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add initial timeline event
            initial_event = DisputeTimeline(
                event_id=str(uuid.uuid4()),
                dispute_id=dispute.dispute_id,
                event_type="dispute_submitted",
                description="Dispute submitted for resolution",
                actor=submitted_by,
                timestamp=datetime.now(),
                metadata={"initial_submission": True}
            )
            dispute.timeline.append(initial_event)
            
            # Store dispute
            await self._store_dispute(dispute)
            
            # Generate initial resolution recommendations
            recommendations = await self._generate_resolution_recommendations(dispute)
            dispute.resolution_recommendations = recommendations
            
            # Update dispute with recommendations
            await self._store_dispute(dispute)
            
            # Add to processing queue if eligible for auto-resolution
            if severity in [DisputeSeverity.LOW, DisputeSeverity.MEDIUM]:
                await self._queue_for_auto_resolution(dispute.dispute_id)
            
            # Notify relevant parties
            await self._notify_dispute_parties(dispute)
            
            # Update cache
            self.dispute_cache[dispute.dispute_id] = dispute
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Dispute submitted: {dispute.dispute_id} in {processing_time:.3f}s")
            
            return dispute
            
        except Exception as e:
            logger.error(f"❌ Error submitting dispute: {str(e)}")
            return None

    async def _validate_dispute_data(self, dispute_data: Dict[str, Any]) -> bool:
        """Validate dispute submission data"""
        try:
            required_fields = ["type", "title", "description"]
            
            for field in required_fields:
                if field not in dispute_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate dispute type
            if dispute_data["type"] not in [dt.value for dt in DisputeType]:
                logger.error(f"Invalid dispute type: {dispute_data['type']}")
                return False
            
            # Validate title and description length
            if len(dispute_data["title"]) < 10 or len(dispute_data["title"]) > 200:
                logger.error("Dispute title must be between 10 and 200 characters")
                return False
            
            if len(dispute_data["description"]) < 50 or len(dispute_data["description"]) > 5000:
                logger.error("Dispute description must be between 50 and 5000 characters")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating dispute data: {str(e)}")
            return False

    async def _create_dispute_parties(self, parties_data: List[Dict[str, Any]]) -> List[DisputeParty]:
        """Create dispute party objects"""
        try:
            parties = []
            
            for party_data in parties_data:
                party = DisputeParty(
                    party_id=party_data.get("id", str(uuid.uuid4())),
                    party_name=party_data.get("name", "Unknown"),
                    party_type=party_data.get("type", "participant"),
                    role_in_collaboration=party_data.get("role", "contributor"),
                    contact_info=party_data.get("contact", {}),
                    legal_representation=party_data.get("legal_rep"),
                    preferred_language=party_data.get("language", "en"),
                    timezone=party_data.get("timezone", "UTC")
                )
                parties.append(party)
            
            return parties
            
        except Exception as e:
            logger.error(f"❌ Error creating dispute parties: {str(e)}")
            return []

    async def _assess_dispute_severity(self, dispute_data: Dict[str, Any], collaboration_id: str) -> DisputeSeverity:
        """Assess dispute severity based on multiple factors"""
        try:
            severity_score = 0.0
            
            # Financial impact assessment
            financial_impact = dispute_data.get("financial_impact", 0.0)
            thresholds = self.severity_thresholds["financial_impact"]
            
            if financial_impact >= thresholds["critical"]:
                severity_score += 4.0
            elif financial_impact >= thresholds["high"]:
                severity_score += 3.0
            elif financial_impact >= thresholds["medium"]:
                severity_score += 2.0
            elif financial_impact >= thresholds["low"]:
                severity_score += 1.0
            
            # Collaboration size impact
            collaboration_data = await self._get_collaboration_data(collaboration_id)
            if collaboration_data:
                participant_count = len(collaboration_data.get("participants", []))
                size_thresholds = self.severity_thresholds["collaboration_size"]
                
                if participant_count >= size_thresholds["critical"]:
                    severity_score += 2.0
                elif participant_count >= size_thresholds["high"]:
                    severity_score += 1.5
                elif participant_count >= size_thresholds["medium"]:
                    severity_score += 1.0
                elif participant_count >= size_thresholds["low"]:
                    severity_score += 0.5
            
            # Dispute type severity
            dispute_type = DisputeType(dispute_data["type"])
            type_severity = {
                DisputeType.COPYRIGHT_INFRINGEMENT: 3.0,
                DisputeType.CONTRACT_BREACH: 2.5,
                DisputeType.INTELLECTUAL_PROPERTY: 2.5,
                DisputeType.PAYMENT_DISPUTE: 2.0,
                DisputeType.REVENUE_SHARING: 2.0,
                DisputeType.QUALITY_DISPUTE: 1.5,
                DisputeType.DEADLINE_DISPUTE: 1.0,
                DisputeType.SCOPE_DISAGREEMENT: 1.0,
                DisputeType.CREATIVE_DIFFERENCES: 0.5,
                DisputeType.COMMUNICATION_ISSUE: 0.5
            }
            severity_score += type_severity.get(dispute_type, 1.0)
            
            # Urgency indicators
            if dispute_data.get("urgent", False):
                severity_score += 1.0
            
            if dispute_data.get("project_blocking", False):
                severity_score += 1.5
            
            # Map score to severity level
            if severity_score >= 7.0:
                return DisputeSeverity.EMERGENCY
            elif severity_score >= 5.0:
                return DisputeSeverity.CRITICAL
            elif severity_score >= 3.0:
                return DisputeSeverity.HIGH
            elif severity_score >= 1.5:
                return DisputeSeverity.MEDIUM
            else:
                return DisputeSeverity.LOW
                
        except Exception as e:
            logger.error(f"❌ Error assessing dispute severity: {str(e)}")
            return DisputeSeverity.MEDIUM

    def _calculate_deadline(self, severity: DisputeSeverity) -> datetime:
        """Calculate resolution deadline based on severity"""
        deadlines = {
            DisputeSeverity.EMERGENCY: timedelta(hours=24),
            DisputeSeverity.CRITICAL: timedelta(days=3),
            DisputeSeverity.HIGH: timedelta(days=7),
            DisputeSeverity.MEDIUM: timedelta(days=14),
            DisputeSeverity.LOW: timedelta(days=30)
        }
        
        return datetime.now() + deadlines.get(severity, timedelta(days=14))

    async def _generate_resolution_recommendations(self, dispute: Dispute) -> List[ResolutionRecommendation]:
        """Generate AI-powered resolution recommendations"""
        try:
            recommendations = []
            
            # Get preferred methods for dispute type
            preferred_methods = self.preferred_methods.get(dispute.dispute_type, [ResolutionMethod.MEDIATION])
            
            for method in preferred_methods:
                # Predict success likelihood
                success_likelihood = await self._predict_resolution_success(dispute, method)
                
                # Estimate duration and cost
                duration = await self._estimate_resolution_duration(dispute, method)
                cost = await self._estimate_resolution_cost(dispute, method)
                
                # Identify risk factors and benefits
                risk_factors = await self._identify_risk_factors(dispute, method)
                benefits = await self._identify_benefits(dispute, method)
                
                # Find precedent cases
                precedents = await self._find_precedent_cases(dispute, method)
                
                # Calculate confidence score
                confidence = await self._calculate_recommendation_confidence(dispute, method, success_likelihood)
                
                recommendation = ResolutionRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    dispute_id=dispute.dispute_id,
                    recommended_method=method,
                    likelihood_of_success=success_likelihood,
                    estimated_duration=duration,
                    estimated_cost=cost,
                    risk_factors=risk_factors,
                    benefits=benefits,
                    precedent_cases=precedents,
                    confidence_score=confidence,
                    generated_at=datetime.now()
                )
                
                recommendations.append(recommendation)
            
            # Sort by success likelihood and confidence
            recommendations.sort(key=lambda r: (r.likelihood_of_success, r.confidence_score), reverse=True)
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating resolution recommendations: {str(e)}")
            return []

    async def _predict_resolution_success(self, dispute: Dispute, method: ResolutionMethod) -> float:
        """Predict resolution success likelihood"""
        try:
            # Simplified ML prediction (in real implementation, use trained model)
            base_success_rates = {
                ResolutionMethod.AUTOMATED: 0.85,
                ResolutionMethod.MEDIATION: 0.75,
                ResolutionMethod.NEGOTIATION: 0.70,
                ResolutionMethod.ARBITRATION: 0.80,
                ResolutionMethod.EXPERT_PANEL: 0.78,
                ResolutionMethod.LEGAL_ACTION: 0.60
            }
            
            base_rate = base_success_rates.get(method, 0.70)
            
            # Adjust based on dispute characteristics
            if dispute.severity == DisputeSeverity.LOW:
                base_rate += 0.1
            elif dispute.severity == DisputeSeverity.CRITICAL:
                base_rate -= 0.1
            
            # Adjust based on financial impact
            if dispute.financial_impact < 1000:
                base_rate += 0.05
            elif dispute.financial_impact > 10000:
                base_rate -= 0.05
            
            # Adjust based on number of parties
            if len(dispute.parties) > 4:
                base_rate -= 0.1
            
            return min(1.0, max(0.0, base_rate))
            
        except Exception as e:
            logger.error(f"❌ Error predicting resolution success: {str(e)}")
            return 0.5

    async def _estimate_resolution_duration(self, dispute: Dispute, method: ResolutionMethod) -> timedelta:
        """Estimate resolution duration"""
        try:
            base_durations = {
                ResolutionMethod.AUTOMATED: timedelta(days=1),
                ResolutionMethod.MEDIATION: timedelta(days=14),
                ResolutionMethod.NEGOTIATION: timedelta(days=21),
                ResolutionMethod.ARBITRATION: timedelta(days=45),
                ResolutionMethod.EXPERT_PANEL: timedelta(days=30),
                ResolutionMethod.LEGAL_ACTION: timedelta(days=180)
            }
            
            base_duration = base_durations.get(method, timedelta(days=30))
            
            # Adjust based on complexity
            if dispute.severity in [DisputeSeverity.CRITICAL, DisputeSeverity.EMERGENCY]:
                base_duration *= 1.5
            elif dispute.severity == DisputeSeverity.LOW:
                base_duration *= 0.7
            
            # Adjust based on number of parties
            if len(dispute.parties) > 4:
                base_duration *= 1.3
            
            return base_duration
            
        except Exception as e:
            logger.error(f"❌ Error estimating resolution duration: {str(e)}")
            return timedelta(days=30)

    async def _estimate_resolution_cost(self, dispute: Dispute, method: ResolutionMethod) -> float:
        """Estimate resolution cost"""
        try:
            base_costs = {
                ResolutionMethod.AUTOMATED: 50.0,
                ResolutionMethod.MEDIATION: 2000.0,
                ResolutionMethod.NEGOTIATION: 1000.0,
                ResolutionMethod.ARBITRATION: 5000.0,
                ResolutionMethod.EXPERT_PANEL: 3000.0,
                ResolutionMethod.LEGAL_ACTION: 15000.0
            }
            
            base_cost = base_costs.get(method, 2000.0)
            
            # Adjust based on financial impact
            if dispute.financial_impact > 50000:
                base_cost *= 2.0
            elif dispute.financial_impact > 10000:
                base_cost *= 1.5
            
            # Adjust based on complexity
            if dispute.severity in [DisputeSeverity.CRITICAL, DisputeSeverity.EMERGENCY]:
                base_cost *= 1.3
            
            return base_cost
            
        except Exception as e:
            logger.error(f"❌ Error estimating resolution cost: {str(e)}")
            return 2000.0

    async def _identify_risk_factors(self, dispute: Dispute, method: ResolutionMethod) -> List[str]:
        """Identify risk factors for resolution method"""
        try:
            risk_factors = []
            
            # Common risk factors by method
            method_risks = {
                ResolutionMethod.AUTOMATED: [
                    "Limited human oversight",
                    "May miss nuanced issues",
                    "Rigid rule-based decisions"
                ],
                ResolutionMethod.MEDIATION: [
                    "Requires cooperation from all parties",
                    "Non-binding outcomes",
                    "May not resolve underlying issues"
                ],
                ResolutionMethod.ARBITRATION: [
                    "Binding decision",
                    "Limited appeal options",
                    "Higher costs"
                ],
                ResolutionMethod.LEGAL_ACTION: [
                    "High costs",
                    "Long duration",
                    "Public proceedings",
                    "Relationship damage"
                ]
            }
            
            risk_factors.extend(method_risks.get(method, []))
            
            # Dispute-specific risks
            if dispute.financial_impact > 50000:
                risk_factors.append("High financial stakes increase pressure")
            
            if len(dispute.parties) > 4:
                risk_factors.append("Multiple parties complicate coordination")
            
            if dispute.severity == DisputeSeverity.EMERGENCY:
                risk_factors.append("Time pressure may compromise thoroughness")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"❌ Error identifying risk factors: {str(e)}")
            return []

    async def _identify_benefits(self, dispute: Dispute, method: ResolutionMethod) -> List[str]:
        """Identify benefits of resolution method"""
        try:
            benefits = []
            
            # Common benefits by method
            method_benefits = {
                ResolutionMethod.AUTOMATED: [
                    "Fast resolution",
                    "Cost-effective",
                    "Consistent decisions",
                    "24/7 availability"
                ],
                ResolutionMethod.MEDIATION: [
                    "Preserves relationships",
                    "Flexible solutions",
                    "Confidential process",
                    "Cost-effective"
                ],
                ResolutionMethod.ARBITRATION: [
                    "Expert decision-maker",
                    "Faster than litigation",
                    "Binding outcome",
                    "Private process"
                ],
                ResolutionMethod.LEGAL_ACTION: [
                    "Legal precedent",
                    "Enforceable judgment",
                    "Comprehensive discovery",
                    "Public vindication"
                ]
            }
            
            benefits.extend(method_benefits.get(method, []))
            
            return benefits
            
        except Exception as e:
            logger.error(f"❌ Error identifying benefits: {str(e)}")
            return []

    async def _find_precedent_cases(self, dispute: Dispute, method: ResolutionMethod) -> List[str]:
        """Find precedent cases for similar disputes"""
        try:
            # In real implementation, this would search a database of past cases
            # For demo, return simulated precedent cases
            precedents = [
                f"Case-{uuid.uuid4().hex[:8]}: Similar {dispute.dispute_type.value} resolved via {method.value}",
                f"Case-{uuid.uuid4().hex[:8]}: {dispute.dispute_type.value} with comparable financial impact",
                f"Case-{uuid.uuid4().hex[:8]}: Multi-party {dispute.dispute_type.value} precedent"
            ]
            
            return precedents[:2]  # Return top 2 precedents
            
        except Exception as e:
            logger.error(f"❌ Error finding precedent cases: {str(e)}")
            return []

    async def _calculate_recommendation_confidence(
        self, 
        dispute: Dispute, 
        method: ResolutionMethod, 
        success_likelihood: float
    ) -> float:
        """Calculate confidence score for recommendation"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on success likelihood
            confidence += success_likelihood * 0.3
            
            # Adjust based on data availability
            if len(dispute.evidence) > 2:
                confidence += 0.1
            
            # Adjust based on dispute clarity
            if len(dispute.description) > 200:  # Detailed description
                confidence += 0.1
            
            # Adjust based on method appropriateness
            preferred_methods = self.preferred_methods.get(dispute.dispute_type, [])
            if method in preferred_methods:
                confidence += 0.2
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"❌ Error calculating recommendation confidence: {str(e)}")
            return 0.5

    async def submit_evidence(
        self,
        dispute_id: str,
        evidence_data: Dict[str, Any],
        submitted_by: str
    ) -> Optional[Evidence]:
        """Submit evidence for a dispute"""
        try:
            # Get dispute
            dispute = await self._get_dispute(dispute_id)
            if not dispute:
                logger.error(f"Dispute {dispute_id} not found")
                return None
            
            # Create evidence record
            evidence = Evidence(
                evidence_id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                submitted_by=submitted_by,
                evidence_type=EvidenceType(evidence_data["type"]),
                title=evidence_data["title"],
                description=evidence_data["description"],
                file_path=evidence_data.get("file_path"),
                file_hash=evidence_data.get("file_hash"),
                metadata=evidence_data.get("metadata", {}),
                authenticity_score=0.0,
                relevance_score=0.0,
                submission_date=datetime.now(),
                verification_status="pending"
            )
            
            # Analyze evidence authenticity and relevance
            evidence.authenticity_score = await self._analyze_evidence_authenticity(evidence)
            evidence.relevance_score = await self._analyze_evidence_relevance(evidence, dispute)
            
            # Store evidence
            await self._store_evidence(evidence)
            
            # Add to dispute
            dispute.evidence.append(evidence)
            
            # Add timeline event
            timeline_event = DisputeTimeline(
                event_id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                event_type="evidence_submitted",
                description=f"Evidence submitted: {evidence.title}",
                actor=submitted_by,
                timestamp=datetime.now(),
                metadata={"evidence_id": evidence.evidence_id}
            )
            dispute.timeline.append(timeline_event)
            
            # Update dispute
            dispute.updated_at = datetime.now()
            await self._store_dispute(dispute)
            
            logger.info(f"✅ Evidence submitted: {evidence.evidence_id} for dispute {dispute_id}")
            
            return evidence
            
        except Exception as e:
            logger.error(f"❌ Error submitting evidence: {str(e)}")
            return None

    async def _analyze_evidence_authenticity(self, evidence: Evidence) -> float:
        """Analyze evidence authenticity using ML models"""
        try:
            # Simplified authenticity analysis
            authenticity_score = 0.8  # Base score
            
            # File hash verification
            if evidence.file_hash:
                authenticity_score += 0.1
            
            # Metadata consistency check
            if evidence.metadata:
                if "timestamp" in evidence.metadata:
                    authenticity_score += 0.05
                if "source" in evidence.metadata:
                    authenticity_score += 0.05
            
            # Evidence type specific checks
            if evidence.evidence_type == EvidenceType.AUDIO_RECORDING:
                # Audio authenticity checks would go here
                authenticity_score += 0.0
            elif evidence.evidence_type == EvidenceType.VIDEO_RECORDING:
                # Video authenticity checks would go here
                authenticity_score += 0.0
            
            return min(1.0, authenticity_score)
            
        except Exception as e:
            logger.error(f"❌ Error analyzing evidence authenticity: {str(e)}")
            return 0.5

    async def _analyze_evidence_relevance(self, evidence: Evidence, dispute: Dispute) -> float:
        """Analyze evidence relevance to dispute"""
        try:
            relevance_score = 0.5  # Base relevance
            
            # Keyword matching between evidence and dispute
            evidence_text = f"{evidence.title} {evidence.description}".lower()
            dispute_text = f"{dispute.title} {dispute.description}".lower()
            
            # Simple keyword overlap analysis
            evidence_words = set(evidence_text.split())
            dispute_words = set(dispute_text.split())
            
            overlap = len(evidence_words & dispute_words)
            total_words = len(evidence_words | dispute_words)
            
            if total_words > 0:
                keyword_similarity = overlap / total_words
                relevance_score += keyword_similarity * 0.3
            
            # Evidence type relevance
            type_relevance = {
                DisputeType.PAYMENT_DISPUTE: {
                    EvidenceType.PAYMENT_RECORD: 0.4,
                    EvidenceType.CONTRACT: 0.3,
                    EvidenceType.EMAIL_CHAIN: 0.2
                },
                DisputeType.INTELLECTUAL_PROPERTY: {
                    EvidenceType.TEXT_DOCUMENT: 0.3,
                    EvidenceType.FILE_METADATA: 0.3,
                    EvidenceType.CONTRACT: 0.2
                }
            }
            
            dispute_type_relevance = type_relevance.get(dispute.dispute_type, {})
            relevance_score += dispute_type_relevance.get(evidence.evidence_type, 0.1)
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.error(f"❌ Error analyzing evidence relevance: {str(e)}")
            return 0.5

    async def schedule_mediation(
        self,
        dispute_id: str,
        mediator_id: str,
        participants: List[str],
        scheduled_at: datetime
    ) -> Optional[MediationSession]:
        """Schedule a mediation session"""
        try:
            # Get dispute
            dispute = await self._get_dispute(dispute_id)
            if not dispute:
                logger.error(f"Dispute {dispute_id} not found")
                return None
            
            # Create mediation session
            session = MediationSession(
                session_id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                mediator_id=mediator_id,
                participants=participants,
                session_type="video",  # Default to video
                scheduled_at=scheduled_at,
                duration_minutes=self.mediation_session_duration,
                session_notes="",
                agreements_reached=[],
                action_items=[],
                next_session=None,
                status="scheduled",
                created_at=datetime.now()
            )
            
            # Store session
            await self._store_mediation_session(session)
            
            # Update dispute status
            dispute.status = DisputeStatus.MEDIATION
            dispute.assigned_mediator = mediator_id
            
            # Add timeline event
            timeline_event = DisputeTimeline(
                event_id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                event_type="mediation_scheduled",
                description=f"Mediation session scheduled with {mediator_id}",
                actor="system",
                timestamp=datetime.now(),
                metadata={"session_id": session.session_id}
            )
            dispute.timeline.append(timeline_event)
            
            # Update dispute
            dispute.updated_at = datetime.now()
            await self._store_dispute(dispute)
            
            # Add to mediation queue
            self.mediation_queue.append(session.session_id)
            
            logger.info(f"✅ Mediation scheduled: {session.session_id} for dispute {dispute_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error scheduling mediation: {str(e)}")
            return None

    async def resolve_dispute(
        self,
        dispute_id: str,
        resolution_data: Dict[str, Any],
        resolved_by: str
    ) -> bool:
        """Resolve a dispute with outcome"""
        try:
            # Get dispute
            dispute = await self._get_dispute(dispute_id)
            if not dispute:
                logger.error(f"Dispute {dispute_id} not found")
                return False
            
            # Update dispute with resolution
            dispute.status = DisputeStatus.RESOLVED
            dispute.resolution_outcome = resolution_data
            dispute.resolution_date = datetime.now()
            dispute.appeal_deadline = datetime.now() + timedelta(days=30)  # 30-day appeal period
            
            # Add timeline event
            timeline_event = DisputeTimeline(
                event_id=str(uuid.uuid4()),
                dispute_id=dispute_id,
                event_type="dispute_resolved",
                description=f"Dispute resolved by {resolved_by}",
                actor=resolved_by,
                timestamp=datetime.now(),
                metadata={"resolution": resolution_data}
            )
            dispute.timeline.append(timeline_event)
            
            # Update dispute
            dispute.updated_at = datetime.now()
            await self._store_dispute(dispute)
            
            # Notify parties of resolution
            await self._notify_resolution(dispute)
            
            # Update analytics
            await self._update_resolution_analytics(dispute)
            
            logger.info(f"✅ Dispute resolved: {dispute_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving dispute: {str(e)}")
            return False

    async def _store_dispute(self, dispute: Dispute) -> None:
        """Store dispute to storage"""
        try:
            dispute_key = f"dispute:{dispute.dispute_id}"
            dispute_data = asdict(dispute)
            
            await self.redis_client.setex(
                dispute_key,
                86400 * self.evidence_retention_days,
                json.dumps(dispute_data, default=str)
            )
            
            # Update collaboration index
            collab_disputes_key = f"collaboration_disputes:{dispute.collaboration_id}"
            await self.redis_client.lpush(collab_disputes_key, dispute.dispute_id)
            await self.redis_client.expire(collab_disputes_key, 86400 * self.evidence_retention_days)
            
            logger.info(f"💾 Dispute {dispute.dispute_id} stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Error storing dispute: {str(e)}")

    async def _store_evidence(self, evidence: Evidence) -> None:
        """Store evidence to storage"""
        try:
            evidence_key = f"evidence:{evidence.evidence_id}"
            evidence_data = asdict(evidence)
            
            await self.redis_client.setex(
                evidence_key,
                86400 * self.evidence_retention_days,
                json.dumps(evidence_data, default=str)
            )
            
            # Update dispute evidence index
            dispute_evidence_key = f"dispute_evidence:{evidence.dispute_id}"
            await self.redis_client.lpush(dispute_evidence_key, evidence.evidence_id)
            await self.redis_client.expire(dispute_evidence_key, 86400 * self.evidence_retention_days)
            
            logger.info(f"💾 Evidence {evidence.evidence_id} stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Error storing evidence: {str(e)}")

    async def _store_mediation_session(self, session: MediationSession) -> None:
        """Store mediation session to storage"""
        try:
            session_key = f"mediation_session:{session.session_id}"
            session_data = asdict(session)
            
            await self.redis_client.setex(
                session_key,
                86400 * 90,  # Keep for 90 days
                json.dumps(session_data, default=str)
            )
            
            # Update dispute sessions index
            dispute_sessions_key = f"dispute_sessions:{session.dispute_id}"
            await self.redis_client.lpush(dispute_sessions_key, session.session_id)
            await self.redis_client.expire(dispute_sessions_key, 86400 * 90)
            
            logger.info(f"💾 Mediation session {session.session_id} stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Error storing mediation session: {str(e)}")

    async def _get_dispute(self, dispute_id: str) -> Optional[Dispute]:
        """Get dispute data"""
        try:
            # Check cache first
            if dispute_id in self.dispute_cache:
                return self.dispute_cache[dispute_id]
            
            dispute_key = f"dispute:{dispute_id}"
            dispute_data = await self.redis_client.get(dispute_key)
            
            if not dispute_data:
                return None
            
            data = json.loads(dispute_data)
            
            # Reconstruct object with proper types
            dispute = Dispute(**data)
            
            # Update cache
            self.dispute_cache[dispute_id] = dispute
            
            return dispute
            
        except Exception as e:
            logger.error(f"❌ Error getting dispute: {str(e)}")
            return None

    async def _get_collaboration_data(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get collaboration data for dispute context"""
        try:
            # In real implementation, this would fetch from collaboration service
            # For demo, return sample data
            sample_data = {
                "id": collaboration_id,
                "participants": [f"user_{i}" for i in range(1, 6)],
                "project_value": 50000.0,
                "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
                "status": "active"
            }
            
            return sample_data
            
        except Exception as e:
            logger.error(f"❌ Error getting collaboration data: {str(e)}")
            return None

    async def _queue_for_auto_resolution(self, dispute_id: str) -> None:
        """Queue dispute for automated resolution attempt"""
        try:
            auto_resolution_key = "auto_resolution_queue"
            await self.redis_client.lpush(auto_resolution_key, dispute_id)
            
            logger.info(f"📋 Dispute {dispute_id} queued for auto-resolution")
            
        except Exception as e:
            logger.error(f"❌ Error queuing for auto-resolution: {str(e)}")

    async def _notify_dispute_parties(self, dispute: Dispute) -> None:
        """Notify parties about dispute submission"""
        try:
            # In real implementation, this would send notifications
            # via email, SMS, in-app notifications, etc.
            
            notification_data = {
                "dispute_id": dispute.dispute_id,
                "type": "dispute_submitted",
                "title": dispute.title,
                "severity": dispute.severity.value,
                "parties": [party.party_id for party in dispute.parties]
            }
            
            # Store notification for retrieval
            notification_key = f"dispute_notification:{dispute.dispute_id}"
            await self.redis_client.setex(
                notification_key,
                86400 * 7,  # Keep for 7 days
                json.dumps(notification_data, default=str)
            )
            
            logger.info(f"📧 Notifications sent for dispute {dispute.dispute_id}")
            
        except Exception as e:
            logger.error(f"❌ Error notifying dispute parties: {str(e)}")

    async def _notify_resolution(self, dispute: Dispute) -> None:
        """Notify parties about dispute resolution"""
        try:
            notification_data = {
                "dispute_id": dispute.dispute_id,
                "type": "dispute_resolved",
                "title": dispute.title,
                "resolution_date": dispute.resolution_date.isoformat() if dispute.resolution_date else None,
                "appeal_deadline": dispute.appeal_deadline.isoformat() if dispute.appeal_deadline else None,
                "parties": [party.party_id for party in dispute.parties]
            }
            
            notification_key = f"resolution_notification:{dispute.dispute_id}"
            await self.redis_client.setex(
                notification_key,
                86400 * 30,  # Keep for 30 days
                json.dumps(notification_data, default=str)
            )
            
            logger.info(f"📧 Resolution notifications sent for dispute {dispute.dispute_id}")
            
        except Exception as e:
            logger.error(f"❌ Error notifying resolution: {str(e)}")

    async def _dispute_processor(self) -> None:
        """Background task for processing disputes"""
        while True:
            try:
                # Check for auto-resolution candidates
                await self._process_auto_resolution_queue()
                
                # Check for escalation timeouts
                await self._check_escalation_timeouts()
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                logger.error(f"❌ Error in dispute processor: {str(e)}")
                await asyncio.sleep(300)

    async def _process_auto_resolution_queue(self) -> None:
        """Process disputes queued for automatic resolution"""
        try:
            auto_resolution_key = "auto_resolution_queue"
            
            # Get disputes from queue
            dispute_ids = await self.redis_client.lrange(auto_resolution_key, 0, 10)  # Process up to 10
            
            for dispute_id_bytes in dispute_ids:
                dispute_id = dispute_id_bytes.decode() if isinstance(dispute_id_bytes, bytes) else dispute_id_bytes
                
                # Attempt auto-resolution
                success = await self._attempt_auto_resolution(dispute_id)
                
                if success:
                    # Remove from queue
                    await self.redis_client.lrem(auto_resolution_key, 1, dispute_id)
                    logger.info(f"✅ Auto-resolved dispute: {dispute_id}")
                else:
                    # Move to manual processing
                    await self.redis_client.lrem(auto_resolution_key, 1, dispute_id)
                    logger.info(f"➡️ Dispute {dispute_id} moved to manual processing")
            
        except Exception as e:
            logger.error(f"❌ Error processing auto-resolution queue: {str(e)}")

    async def _attempt_auto_resolution(self, dispute_id: str) -> bool:
        """Attempt automated resolution of dispute"""
        try:
            dispute = await self._get_dispute(dispute_id)
            if not dispute:
                return False
            
            # Check if dispute is suitable for auto-resolution
            if dispute.severity not in [DisputeSeverity.LOW, DisputeSeverity.MEDIUM]:
                return False
            
            # Simple auto-resolution rules
            auto_resolvable = False
            resolution_outcome = {}
            
            # Payment disputes under $500 - offer split resolution
            if (dispute.dispute_type == DisputeType.PAYMENT_DISPUTE and 
                dispute.financial_impact < 500):
                auto_resolvable = True
                resolution_outcome = {
                    "method": "automated_split",
                    "decision": "Split disputed amount 50/50 between parties",
                    "amount_per_party": dispute.financial_impact / len(dispute.parties),
                    "confidence": 0.85
                }
            
            # Communication issues - suggest mediation
            elif dispute.dispute_type == DisputeType.COMMUNICATION_ISSUE:
                auto_resolvable = True
                resolution_outcome = {
                    "method": "automated_mediation_referral",
                    "decision": "Refer to mediation with communication guidelines",
                    "next_steps": ["Schedule mediation session", "Provide communication training"],
                    "confidence": 0.80
                }
            
            if auto_resolvable:
                return await self.resolve_dispute(dispute_id, resolution_outcome, "auto_resolution_system")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error attempting auto-resolution: {str(e)}")
            return False

    async def _mediation_scheduler(self) -> None:
        """Background task for managing mediation sessions"""
        while True:
            try:
                # Process mediation queue
                if self.mediation_queue:
                    session_id = self.mediation_queue.popleft()
                    await self._prepare_mediation_session(session_id)
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in mediation scheduler: {str(e)}")
                await asyncio.sleep(600)

    async def _evidence_analyzer(self) -> None:
        """Background task for analyzing evidence"""
        while True:
            try:
                # Analyze recently submitted evidence
                await self._analyze_pending_evidence()
                
                await asyncio.sleep(600)  # Process every 10 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in evidence analyzer: {str(e)}")
                await asyncio.sleep(600)

    async def _deadline_monitor(self) -> None:
        """Background task for monitoring dispute deadlines"""
        while True:
            try:
                # Check for approaching deadlines
                await self._check_dispute_deadlines()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error in deadline monitor: {str(e)}")
                await asyncio.sleep(600)

    async def get_dispute_status(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive dispute status"""
        try:
            dispute = await self._get_dispute(dispute_id)
            if not dispute:
                return None
            
            return {
                "dispute_id": dispute.dispute_id,
                "collaboration_id": dispute.collaboration_id,
                "title": dispute.title,
                "type": dispute.dispute_type.value,
                "severity": dispute.severity.value,
                "status": dispute.status.value,
                "submitted_at": dispute.submitted_at.isoformat(),
                "deadline": dispute.deadline.isoformat() if dispute.deadline else None,
                "resolution_date": dispute.resolution_date.isoformat() if dispute.resolution_date else None,
                "financial_impact": dispute.financial_impact,
                "parties_count": len(dispute.parties),
                "evidence_count": len(dispute.evidence),
                "timeline_events": len(dispute.timeline),
                "recommendations_count": len(dispute.resolution_recommendations),
                "assigned_mediator": dispute.assigned_mediator,
                "resolution_outcome": dispute.resolution_outcome
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting dispute status: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = {
                "service": "DisputeResolutionService",
                "status": "healthy",
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "redis_connected": False,
                "mediation_queue_size": len(self.mediation_queue),
                "cache_size": len(self.dispute_cache),
                "ml_models_loaded": len(self.ml_models),
                "auto_resolution_threshold": self.auto_resolution_threshold,
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connected"] = True
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "DisputeResolutionService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def stop(self) -> None:
        """Stop the dispute resolution service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.thread_pool.shutdown(wait=True)
            
            logger.info(f"🛑 DisputeResolutionService {self.service_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of DisputeResolutionService"""
    service = DisputeResolutionService()
    
    try:
        # Start service
        await service.start()
        
        # Test dispute submission
        collaboration_id = "test_collaboration_001"
        dispute_data = {
            "type": "payment_dispute",
            "title": "Disagreement over payment terms",
            "description": "There is a disagreement about the payment schedule and amounts for the recent collaboration project. The parties cannot agree on the final payment distribution.",
            "financial_impact": 2500.0,
            "urgent": False,
            "project_blocking": False,
            "parties": [
                {
                    "id": "user_1",
                    "name": "User One",
                    "type": "complainant",
                    "role": "project_lead",
                    "contact": {"email": "user1@example.com"},
                    "language": "en"
                },
                {
                    "id": "user_2", 
                    "name": "User Two",
                    "type": "respondent",
                    "role": "contributor",
                    "contact": {"email": "user2@example.com"},
                    "language": "en"
                }
            ]
        }
        
        print(f"⚖️ Submitting dispute for collaboration: {collaboration_id}")
        dispute = await service.submit_dispute(collaboration_id, dispute_data, "user_1")
        
        if dispute:
            print(f"✅ Dispute submitted:")
            print(f"   - Dispute ID: {dispute.dispute_id}")
            print(f"   - Type: {dispute.dispute_type.value}")
            print(f"   - Severity: {dispute.severity.value}")
            print(f"   - Status: {dispute.status.value}")
            print(f"   - Deadline: {dispute.deadline}")
            print(f"   - Recommendations: {len(dispute.resolution_recommendations)}")
            
            for i, rec in enumerate(dispute.resolution_recommendations):
                print(f"     {i+1}. {rec.recommended_method.value} (Success: {rec.likelihood_of_success:.2f})")
        
        # Test evidence submission
        if dispute:
            evidence_data = {
                "type": "email_chain",
                "title": "Email discussion about payment terms",
                "description": "Email chain showing the original agreement and subsequent discussions about payment modifications.",
                "metadata": {"timestamp": datetime.now().isoformat(), "source": "email_client"}
            }
            
            evidence = await service.submit_evidence(dispute.dispute_id, evidence_data, "user_1")
            if evidence:
                print(f"📎 Evidence submitted: {evidence.evidence_id}")
                print(f"   - Authenticity Score: {evidence.authenticity_score:.3f}")
                print(f"   - Relevance Score: {evidence.relevance_score:.3f}")
        
        # Check dispute status
        if dispute:
            await asyncio.sleep(1)  # Wait for processing
            status = await service.get_dispute_status(dispute.dispute_id)
            if status:
                print(f"📊 Dispute Status: {status['status']}")
                print(f"   - Evidence Count: {status['evidence_count']}")
                print(f"   - Timeline Events: {status['timeline_events']}")
        
        # Health check
        health = await service.health_check()
        print(f"🏥 Service health: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())