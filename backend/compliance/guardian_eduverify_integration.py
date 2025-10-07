"""Guardian-EduVerify Integration Module - Unified Orchestration System
=========================================================================

Module d'orchestration et d'intégration pour coordination complète
entre Guardian (protection contenu) et EduVerify (vérification éducative).

Business Logic (Unified Protection & Verification):
Content Submission → Guardian Security Scan → EduVerify Quality Check → 
Combined Decision → Policy Enforcement → Age Validation → Standards Check → 
Cross-Module Analytics → Certification → Monitoring → Continuous Improvement

Core Components:
- GuardianEduVerifyOrchestrator: Main orchestrator for unified processing
- UnifiedComplianceEngine: Combined compliance and verification engine
- CrossModuleAnalytics: Analytics across Guardian and EduVerify
- DataFlowCoordinator: Data synchronization and flow management
- CombinedDecisionEngine: Intelligent decision-making combining both systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL NOTICE:
ALL RIGHTS RESERVED - PROPRIETARY SOFTWARE
This software and all associated intellectual property are the exclusive 
property of Fahed Mlaiel. Unauthorized use, reproduction, or distribution 
is strictly prohibited and will result in immediate legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

# Import Guardian and EduVerify modules
from .guardian_compliance import (
    GuardianComplianceEngine,
    SecurityLevel,
    ThreatLevel,
    ContentStatus,
    GuardianAction
)
from .eduverify_compliance import (
    EduVerifyEngine,
    EducationalMetadata,
    ContentQuality,
    VerificationStatus,
    AgeGroup
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    INITIALIZED = "initialized"
    GUARDIAN_SCAN = "guardian_scan"
    EDUVERIFY_CHECK = "eduverify_check"
    COMBINED_ANALYSIS = "combined_analysis"
    DECISION_MAKING = "decision_making"
    ENFORCEMENT = "enforcement"
    COMPLETED = "completed"
    FAILED = "failed"


class UnifiedStatus(str, Enum):
    """Unified content status"""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    REJECTED_SECURITY = "rejected_security"
    REJECTED_QUALITY = "rejected_quality"
    REJECTED_AGE = "rejected_age"
    QUARANTINED = "quarantined"


class DecisionConfidence(str, Enum):
    """Decision confidence levels"""
    VERY_HIGH = "very_high"  # >95%
    HIGH = "high"  # 85-95%
    MEDIUM = "medium"  # 70-85%
    LOW = "low"  # 50-70%
    UNCERTAIN = "uncertain"  # <50%


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UnifiedProcessingResult:
    """Complete unified processing result"""
    content_id: str
    unified_status: UnifiedStatus
    guardian_result: Dict[str, Any]
    eduverify_result: Dict[str, Any]
    combined_score: float  # 0-100
    decision_confidence: DecisionConfidence
    processing_stages: List[str]
    recommendations: List[str]
    actions_taken: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrossModuleMetrics:
    """Cross-module analytics metrics"""
    total_processed: int
    guardian_blocks: int
    eduverify_rejections: int
    combined_approvals: int
    average_processing_time: float
    security_score_avg: float
    quality_score_avg: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SyncedData:
    """Synchronized data between modules"""
    content_id: str
    guardian_data: Dict[str, Any]
    eduverify_data: Dict[str, Any]
    sync_timestamp: datetime = field(default_factory=datetime.utcnow)
    consistency_validated: bool = False


# ============================================================================
# UNIFIED COMPLIANCE ENGINE
# ============================================================================

class UnifiedComplianceEngine:
    """Combined compliance and verification engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Unified Compliance Engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Compliance rules
        self.unified_rules = self._initialize_unified_rules()
        
        # Processing cache
        self.processing_cache: Dict[str, UnifiedProcessingResult] = {}
        
        logger.info("UnifiedComplianceEngine initialized")
    
    def _initialize_unified_rules(self) -> Dict[str, Any]:
        """Initialize unified compliance rules
        
        Returns:
            Dictionary of unified rules
        """
        return {
            "security_threshold": 70,  # Minimum security score
            "quality_threshold": 7.0,  # Minimum quality score
            "combined_threshold": 75,  # Minimum combined score
            "auto_approve_threshold": 90,  # Auto-approve if above this
            "auto_reject_threshold": 30,  # Auto-reject if below this
            "require_review_threshold": 60,  # Require manual review if below
        }
    
    async def evaluate_unified_compliance(
        self,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any]
    ) -> Tuple[UnifiedStatus, float, List[str]]:
        """Evaluate unified compliance across both systems
        
        Args:
            guardian_result: Guardian processing result
            eduverify_result: EduVerify processing result
            
        Returns:
            Tuple of (unified_status, combined_score, recommendations)
        """
        # Calculate combined score (0-100)
        guardian_score = (100 - guardian_result.get("threat_score", 0))
        eduverify_score = eduverify_result.get("quality_score", {}).get("overall_score", 0) * 10
        
        # Weighted combination: 60% security, 40% quality
        combined_score = (guardian_score * 0.6) + (eduverify_score * 0.4)
        
        # Determine unified status
        guardian_status = guardian_result.get("status", "pending")
        eduverify_status = eduverify_result.get("status", "pending")
        
        unified_status = await self._determine_unified_status(
            guardian_status,
            eduverify_status,
            combined_score,
            guardian_result,
            eduverify_result
        )
        
        # Generate recommendations
        recommendations = await self._generate_unified_recommendations(
            guardian_result,
            eduverify_result,
            combined_score
        )
        
        return unified_status, combined_score, recommendations
    
    async def _determine_unified_status(
        self,
        guardian_status: str,
        eduverify_status: str,
        combined_score: float,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any]
    ) -> UnifiedStatus:
        """Determine unified status from both systems
        
        Args:
            guardian_status: Guardian status
            eduverify_status: EduVerify status
            combined_score: Combined score
            guardian_result: Guardian result
            eduverify_result: EduVerify result
            
        Returns:
            Unified status
        """
        # Security issues take priority
        if guardian_status in ["rejected", "quarantined"]:
            return UnifiedStatus.REJECTED_SECURITY
        
        # Age appropriateness issues
        if not eduverify_result.get("age_appropriateness", {}).get("is_appropriate", True):
            return UnifiedStatus.REJECTED_AGE
        
        # Quality issues
        quality_level = eduverify_result.get("quality_score", {}).get("quality_level", "")
        if quality_level == "unacceptable":
            return UnifiedStatus.REJECTED_QUALITY
        
        # High combined score - approve
        if combined_score >= self.unified_rules["auto_approve_threshold"]:
            return UnifiedStatus.APPROVED
        
        # Good score with minor concerns
        if combined_score >= self.unified_rules["combined_threshold"]:
            if guardian_status == "flagged" or eduverify_status == "needs_review":
                return UnifiedStatus.APPROVED_WITH_CONDITIONS
            return UnifiedStatus.APPROVED
        
        # Moderate score - needs review
        if combined_score >= self.unified_rules["require_review_threshold"]:
            return UnifiedStatus.FLAGGED_FOR_REVIEW
        
        # Low score - reject or quarantine
        if combined_score < self.unified_rules["auto_reject_threshold"]:
            return UnifiedStatus.REJECTED_QUALITY
        
        return UnifiedStatus.QUARANTINED
    
    async def _generate_unified_recommendations(
        self,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any],
        combined_score: float
    ) -> List[str]:
        """Generate unified recommendations
        
        Args:
            guardian_result: Guardian result
            eduverify_result: EduVerify result
            combined_score: Combined score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add Guardian recommendations
        if guardian_result.get("threat_score", 0) > 30:
            recommendations.append("Review and address security concerns")
        
        # Add EduVerify recommendations
        eduverify_recs = eduverify_result.get("recommendations", [])
        recommendations.extend(eduverify_recs)
        
        # Add combined recommendations
        if combined_score < 70:
            recommendations.append("Improve overall content quality and security")
        
        return list(set(recommendations))  # Remove duplicates


# ============================================================================
# CROSS-MODULE ANALYTICS
# ============================================================================

class CrossModuleAnalytics:
    """Analytics system spanning Guardian and EduVerify"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Cross-Module Analytics
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Analytics data
        self.processing_history: List[UnifiedProcessingResult] = []
        self.metrics_cache: Optional[CrossModuleMetrics] = None
        self.last_metrics_update: Optional[datetime] = None
        
        logger.info("CrossModuleAnalytics initialized")
    
    def record_processing(self, result: UnifiedProcessingResult):
        """Record a processing result for analytics
        
        Args:
            result: Processing result to record
        """
        self.processing_history.append(result)
        
        # Invalidate cache
        self.metrics_cache = None
    
    async def calculate_metrics(self) -> CrossModuleMetrics:
        """Calculate cross-module metrics
        
        Returns:
            Cross-module metrics
        """
        # Check cache
        if self.metrics_cache and self.last_metrics_update:
            if (datetime.utcnow() - self.last_metrics_update).seconds < 300:  # 5 min cache
                return self.metrics_cache
        
        total_processed = len(self.processing_history)
        
        if total_processed == 0:
            return CrossModuleMetrics(
                total_processed=0,
                guardian_blocks=0,
                eduverify_rejections=0,
                combined_approvals=0,
                average_processing_time=0,
                security_score_avg=0,
                quality_score_avg=0
            )
        
        # Calculate statistics
        guardian_blocks = sum(
            1 for r in self.processing_history
            if "rejected_security" in r.unified_status.value
        )
        
        eduverify_rejections = sum(
            1 for r in self.processing_history
            if "rejected_quality" in r.unified_status.value or "rejected_age" in r.unified_status.value
        )
        
        combined_approvals = sum(
            1 for r in self.processing_history
            if r.unified_status in [UnifiedStatus.APPROVED, UnifiedStatus.APPROVED_WITH_CONDITIONS]
        )
        
        # Average scores
        security_scores = [
            100 - r.guardian_result.get("threat_score", 0)
            for r in self.processing_history
        ]
        security_score_avg = sum(security_scores) / len(security_scores) if security_scores else 0
        
        quality_scores = [
            r.eduverify_result.get("quality_score", {}).get("overall_score", 0)
            for r in self.processing_history
        ]
        quality_score_avg = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        metrics = CrossModuleMetrics(
            total_processed=total_processed,
            guardian_blocks=guardian_blocks,
            eduverify_rejections=eduverify_rejections,
            combined_approvals=combined_approvals,
            average_processing_time=0,  # Would calculate from timestamps
            security_score_avg=security_score_avg,
            quality_score_avg=quality_score_avg
        )
        
        # Update cache
        self.metrics_cache = metrics
        self.last_metrics_update = datetime.utcnow()
        
        return metrics
    
    async def generate_insights(self) -> Dict[str, Any]:
        """Generate intelligent insights from analytics
        
        Returns:
            Dict of insights and recommendations
        """
        metrics = await self.calculate_metrics()
        
        insights = {
            "overall_health": "good",
            "trends": [],
            "alerts": [],
            "recommendations": []
        }
        
        # Analyze approval rate
        if metrics.total_processed > 0:
            approval_rate = (metrics.combined_approvals / metrics.total_processed) * 100
            
            if approval_rate < 50:
                insights["overall_health"] = "poor"
                insights["alerts"].append("Low approval rate detected")
                insights["recommendations"].append("Review content guidelines and quality standards")
            elif approval_rate < 70:
                insights["overall_health"] = "fair"
                insights["recommendations"].append("Consider adjusting quality thresholds")
        
        # Analyze security
        if metrics.security_score_avg < 60:
            insights["alerts"].append("Security scores below acceptable threshold")
            insights["recommendations"].append("Enhance security scanning and threat detection")
        
        # Analyze quality
        if metrics.quality_score_avg < 6:
            insights["alerts"].append("Educational quality below acceptable threshold")
            insights["recommendations"].append("Improve content quality guidelines and validation")
        
        return insights


# ============================================================================
# DATA FLOW COORDINATOR
# ============================================================================

class DataFlowCoordinator:
    """Coordinator for data synchronization and flow between modules"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Data Flow Coordinator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.sync_interval = self.config.get("sync_interval", 300)  # 5 minutes
        
        # Synced data storage
        self.synced_data: Dict[str, SyncedData] = {}
        self.sync_queue: List[str] = []
        
        logger.info("DataFlowCoordinator initialized")
    
    async def sync_data(
        self,
        content_id: str,
        guardian_data: Dict[str, Any],
        eduverify_data: Dict[str, Any]
    ) -> SyncedData:
        """Synchronize data between Guardian and EduVerify
        
        Args:
            content_id: Content identifier
            guardian_data: Guardian data
            eduverify_data: EduVerify data
            
        Returns:
            Synced data object
        """
        # Validate consistency
        consistency_validated = await self._validate_consistency(
            guardian_data, eduverify_data
        )
        
        synced = SyncedData(
            content_id=content_id,
            guardian_data=guardian_data,
            eduverify_data=eduverify_data,
            consistency_validated=consistency_validated
        )
        
        self.synced_data[content_id] = synced
        
        logger.info(f"Data synced for content {content_id}: consistent={consistency_validated}")
        
        return synced
    
    async def _validate_consistency(
        self,
        guardian_data: Dict[str, Any],
        eduverify_data: Dict[str, Any]
    ) -> bool:
        """Validate data consistency between modules
        
        Args:
            guardian_data: Guardian data
            eduverify_data: EduVerify data
            
        Returns:
            True if data is consistent
        """
        # Check if content IDs match
        if guardian_data.get("content_id") != eduverify_data.get("content_id"):
            logger.warning("Content ID mismatch in cross-module data")
            return False
        
        # Check timestamp consistency (within 1 minute)
        guardian_time = guardian_data.get("timestamp", "")
        eduverify_time = eduverify_data.get("verified_at", "")
        
        # Additional consistency checks can be added here
        
        return True


# ============================================================================
# COMBINED DECISION ENGINE
# ============================================================================

class CombinedDecisionEngine:
    """Intelligent decision-making combining Guardian and EduVerify"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Combined Decision Engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Decision weights
        self.weights = {
            "security": 0.6,
            "quality": 0.25,
            "age_appropriateness": 0.15
        }
        
        # Decision history
        self.decision_history: List[Dict[str, Any]] = []
        
        logger.info("CombinedDecisionEngine initialized")
    
    async def make_decision(
        self,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[UnifiedStatus, DecisionConfidence, List[str]]:
        """Make combined decision based on both systems
        
        Args:
            guardian_result: Guardian analysis result
            eduverify_result: EduVerify analysis result
            context: Additional context
            
        Returns:
            Tuple of (decision, confidence, reasoning)
        """
        # Calculate weighted scores
        security_score = self._calculate_security_score(guardian_result)
        quality_score = self._calculate_quality_score(eduverify_result)
        age_score = self._calculate_age_score(eduverify_result)
        
        # Calculate overall score
        overall_score = (
            security_score * self.weights["security"] +
            quality_score * self.weights["quality"] +
            age_score * self.weights["age_appropriateness"]
        )
        
        # Determine decision
        decision = await self._determine_decision(
            overall_score,
            security_score,
            quality_score,
            age_score,
            guardian_result,
            eduverify_result
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            overall_score,
            guardian_result,
            eduverify_result
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            decision,
            overall_score,
            security_score,
            quality_score,
            age_score
        )
        
        # Record decision
        self.decision_history.append({
            "decision": decision.value,
            "confidence": confidence.value,
            "overall_score": overall_score,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return decision, confidence, reasoning
    
    def _calculate_security_score(self, guardian_result: Dict[str, Any]) -> float:
        """Calculate normalized security score (0-100)
        
        Args:
            guardian_result: Guardian result
            
        Returns:
            Security score
        """
        threat_score = guardian_result.get("threat_score", 0)
        return max(0, 100 - threat_score)
    
    def _calculate_quality_score(self, eduverify_result: Dict[str, Any]) -> float:
        """Calculate normalized quality score (0-100)
        
        Args:
            eduverify_result: EduVerify result
            
        Returns:
            Quality score
        """
        quality_data = eduverify_result.get("quality_score", {})
        overall_score = quality_data.get("overall_score", 0)
        return overall_score * 10  # Convert 0-10 to 0-100
    
    def _calculate_age_score(self, eduverify_result: Dict[str, Any]) -> float:
        """Calculate age appropriateness score (0-100)
        
        Args:
            eduverify_result: EduVerify result
            
        Returns:
            Age appropriateness score
        """
        age_data = eduverify_result.get("age_appropriateness", {})
        is_appropriate = age_data.get("is_appropriate", False)
        concerns_count = len(age_data.get("detected_concerns", []))
        
        if is_appropriate and concerns_count == 0:
            return 100
        elif is_appropriate:
            return max(70, 100 - (concerns_count * 10))
        else:
            return max(0, 50 - (concerns_count * 10))
    
    async def _determine_decision(
        self,
        overall_score: float,
        security_score: float,
        quality_score: float,
        age_score: float,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any]
    ) -> UnifiedStatus:
        """Determine final decision
        
        Args:
            overall_score: Overall combined score
            security_score: Security score
            quality_score: Quality score
            age_score: Age score
            guardian_result: Guardian result
            eduverify_result: EduVerify result
            
        Returns:
            Unified decision status
        """
        # Critical failures
        if security_score < 30:
            return UnifiedStatus.REJECTED_SECURITY
        
        if age_score < 50:
            return UnifiedStatus.REJECTED_AGE
        
        if quality_score < 30:
            return UnifiedStatus.REJECTED_QUALITY
        
        # Excellent content
        if overall_score >= 90:
            return UnifiedStatus.APPROVED
        
        # Good content with minor issues
        if overall_score >= 75:
            if any([security_score < 80, quality_score < 70, age_score < 80]):
                return UnifiedStatus.APPROVED_WITH_CONDITIONS
            return UnifiedStatus.APPROVED
        
        # Moderate content needs review
        if overall_score >= 60:
            return UnifiedStatus.FLAGGED_FOR_REVIEW
        
        # Low quality - quarantine
        return UnifiedStatus.QUARANTINED
    
    def _calculate_confidence(
        self,
        overall_score: float,
        guardian_result: Dict[str, Any],
        eduverify_result: Dict[str, Any]
    ) -> DecisionConfidence:
        """Calculate decision confidence
        
        Args:
            overall_score: Overall score
            guardian_result: Guardian result
            eduverify_result: EduVerify result
            
        Returns:
            Confidence level
        """
        # High confidence at extremes
        if overall_score >= 90 or overall_score <= 30:
            return DecisionConfidence.VERY_HIGH
        
        # Check for conflicting signals
        guardian_confidence = guardian_result.get("access_details", {}).get("granted", True)
        eduverify_confidence = eduverify_result.get("quality_score", {}).get("overall_score", 0)
        
        if overall_score >= 75:
            return DecisionConfidence.HIGH
        elif overall_score >= 60:
            return DecisionConfidence.MEDIUM
        elif overall_score >= 45:
            return DecisionConfidence.LOW
        else:
            return DecisionConfidence.UNCERTAIN
    
    def _generate_reasoning(
        self,
        decision: UnifiedStatus,
        overall_score: float,
        security_score: float,
        quality_score: float,
        age_score: float
    ) -> List[str]:
        """Generate decision reasoning
        
        Args:
            decision: Decision made
            overall_score: Overall score
            security_score: Security score
            quality_score: Quality score
            age_score: Age score
            
        Returns:
            List of reasoning points
        """
        reasoning = []
        
        reasoning.append(f"Overall score: {overall_score:.1f}/100")
        reasoning.append(f"Security: {security_score:.1f}/100")
        reasoning.append(f"Quality: {quality_score:.1f}/100")
        reasoning.append(f"Age-appropriateness: {age_score:.1f}/100")
        
        if decision == UnifiedStatus.APPROVED:
            reasoning.append("All criteria meet approval standards")
        elif decision == UnifiedStatus.APPROVED_WITH_CONDITIONS:
            reasoning.append("Approved with monitoring for minor concerns")
        elif decision == UnifiedStatus.REJECTED_SECURITY:
            reasoning.append("Rejected due to security concerns")
        elif decision == UnifiedStatus.REJECTED_AGE:
            reasoning.append("Rejected due to age-appropriateness issues")
        elif decision == UnifiedStatus.REJECTED_QUALITY:
            reasoning.append("Rejected due to quality standards not met")
        
        return reasoning


# ============================================================================
# GUARDIAN-EDUVERIFY ORCHESTRATOR (MAIN)
# ============================================================================

class GuardianEduVerifyOrchestrator:
    """Main orchestrator for unified Guardian and EduVerify processing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Guardian-EduVerify Orchestrator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize Guardian and EduVerify engines
        self.guardian_engine = GuardianComplianceEngine(
            self.config.get("guardian", {})
        )
        self.eduverify_engine = EduVerifyEngine(
            self.config.get("eduverify", {})
        )
        
        # Initialize integration components
        self.compliance_engine = UnifiedComplianceEngine(
            self.config.get("unified_compliance", {})
        )
        self.analytics = CrossModuleAnalytics(
            self.config.get("analytics", {})
        )
        self.data_coordinator = DataFlowCoordinator(
            self.config.get("data_flow", {})
        )
        self.decision_engine = CombinedDecisionEngine(
            self.config.get("decision_engine", {})
        )
        
        # Orchestrator state
        self.processing_count = 0
        self.start_time = datetime.utcnow()
        
        logger.info("GuardianEduVerifyOrchestrator initialized successfully")
    
    async def process_content(
        self,
        content_id: str,
        content: str,
        content_type: str,
        educational_metadata: EducationalMetadata,
        user_id: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedProcessingResult:
        """Process content through complete Guardian-EduVerify pipeline
        
        Args:
            content_id: Content identifier
            content: Content to process
            content_type: Type of content
            educational_metadata: Educational metadata
            user_id: User identifier
            additional_metadata: Additional metadata
            
        Returns:
            Complete unified processing result
        """
        try:
            logger.info(f"Processing content {content_id} through unified pipeline")
            self.processing_count += 1
            
            processing_stages = []
            start_time = datetime.utcnow()
            
            # Stage 1: Guardian security scan
            processing_stages.append(ProcessingStage.GUARDIAN_SCAN.value)
            guardian_result = await self.guardian_engine.process_content(
                content_id, content, content_type, user_id, additional_metadata
            )
            
            # Stage 2: EduVerify quality check
            processing_stages.append(ProcessingStage.EDUVERIFY_CHECK.value)
            eduverify_result = await self.eduverify_engine.verify_educational_content(
                content_id, content, educational_metadata
            )
            
            # Stage 3: Sync data
            await self.data_coordinator.sync_data(
                content_id,
                guardian_result,
                eduverify_result.__dict__ if hasattr(eduverify_result, '__dict__') else {}
            )
            
            # Stage 4: Combined analysis
            processing_stages.append(ProcessingStage.COMBINED_ANALYSIS.value)
            unified_status, combined_score, recommendations = await self.compliance_engine.evaluate_unified_compliance(
                guardian_result,
                eduverify_result.__dict__ if hasattr(eduverify_result, '__dict__') else {}
            )
            
            # Stage 5: Decision making
            processing_stages.append(ProcessingStage.DECISION_MAKING.value)
            final_decision, confidence, reasoning = await self.decision_engine.make_decision(
                guardian_result,
                eduverify_result.__dict__ if hasattr(eduverify_result, '__dict__') else {}
            )
            
            # Stage 6: Enforcement
            processing_stages.append(ProcessingStage.ENFORCEMENT.value)
            actions_taken = await self._enforce_decision(
                content_id, final_decision, guardian_result
            )
            
            processing_stages.append(ProcessingStage.COMPLETED.value)
            
            # Create unified result
            result = UnifiedProcessingResult(
                content_id=content_id,
                unified_status=final_decision,
                guardian_result=guardian_result,
                eduverify_result=eduverify_result.__dict__ if hasattr(eduverify_result, '__dict__') else {},
                combined_score=combined_score,
                decision_confidence=confidence,
                processing_stages=processing_stages,
                recommendations=recommendations + reasoning,
                actions_taken=actions_taken,
                metadata={
                    "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                    "user_id": user_id,
                    "content_type": content_type
                }
            )
            
            # Record for analytics
            self.analytics.record_processing(result)
            
            logger.info(
                f"Content {content_id} processing complete: "
                f"status={final_decision.value}, score={combined_score:.1f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing content {content_id}: {e}")
            return UnifiedProcessingResult(
                content_id=content_id,
                unified_status=UnifiedStatus.FLAGGED_FOR_REVIEW,
                guardian_result={"error": str(e)},
                eduverify_result={"error": str(e)},
                combined_score=0,
                decision_confidence=DecisionConfidence.UNCERTAIN,
                processing_stages=[ProcessingStage.FAILED.value],
                recommendations=[f"Manual review required: {str(e)}"],
                actions_taken=["flagged_for_manual_review"],
                metadata={"error": str(e)}
            )
    
    async def _enforce_decision(
        self,
        content_id: str,
        decision: UnifiedStatus,
        guardian_result: Dict[str, Any]
    ) -> List[str]:
        """Enforce the unified decision
        
        Args:
            content_id: Content identifier
            decision: Decision to enforce
            guardian_result: Guardian result for enforcement
            
        Returns:
            List of actions taken
        """
        actions = []
        
        if decision == UnifiedStatus.APPROVED:
            actions.append("content_approved")
        elif decision == UnifiedStatus.APPROVED_WITH_CONDITIONS:
            actions.append("content_approved_with_monitoring")
        elif decision in [UnifiedStatus.REJECTED_SECURITY, UnifiedStatus.REJECTED_AGE, UnifiedStatus.REJECTED_QUALITY]:
            actions.append("content_rejected")
            actions.append("user_notified")
        elif decision == UnifiedStatus.QUARANTINED:
            actions.append("content_quarantined")
            actions.append("admin_notified")
        elif decision == UnifiedStatus.FLAGGED_FOR_REVIEW:
            actions.append("flagged_for_review")
            actions.append("review_queue_added")
        
        logger.info(f"Enforcement actions for {content_id}: {actions}")
        return actions
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status
        
        Returns:
            System status and metrics
        """
        uptime = datetime.utcnow() - self.start_time
        metrics = await self.analytics.calculate_metrics()
        insights = await self.analytics.generate_insights()
        
        guardian_status = await self.guardian_engine.get_system_status()
        eduverify_status = await self.eduverify_engine.get_engine_status()
        
        return {
            "orchestrator_status": "operational",
            "uptime_seconds": uptime.total_seconds(),
            "processing_count": self.processing_count,
            "components": {
                "guardian": guardian_status,
                "eduverify": eduverify_status,
                "unified_compliance": "operational",
                "analytics": "operational",
                "data_coordinator": "operational",
                "decision_engine": "operational"
            },
            "metrics": {
                "total_processed": metrics.total_processed,
                "approval_rate": (
                    metrics.combined_approvals / metrics.total_processed * 100
                    if metrics.total_processed > 0 else 0
                ),
                "security_avg": metrics.security_score_avg,
                "quality_avg": metrics.quality_score_avg
            },
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main Orchestrator
    "GuardianEduVerifyOrchestrator",
    
    # Core Components
    "UnifiedComplianceEngine",
    "CrossModuleAnalytics",
    "DataFlowCoordinator",
    "CombinedDecisionEngine",
    
    # Enums
    "ProcessingStage",
    "UnifiedStatus",
    "DecisionConfidence",
    
    # Data Models
    "UnifiedProcessingResult",
    "CrossModuleMetrics",
    "SyncedData",
]
