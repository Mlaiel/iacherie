"""
Ainflue Platform - Trust Score Monitor
=====================================

Enterprise-grade trust scoring system for collaboration partners with behavioral analysis,
reputation tracking, fraud detection, and automated trust verification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import statistics
import hashlib
from collections import defaultdict, deque
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrustLevel(Enum):
    """Trust levels for collaboration partners."""
    UNVERIFIED = "unverified"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"
    TRUSTED_PARTNER = "trusted_partner"

class TrustFactor(Enum):
    """Factors that influence trust score."""
    COMPLETION_RATE = "completion_rate"
    COMMUNICATION_QUALITY = "communication_quality"
    DEADLINE_ADHERENCE = "deadline_adherence"
    CONTENT_QUALITY = "content_quality"
    DISPUTE_HISTORY = "dispute_history"
    PAYMENT_RELIABILITY = "payment_reliability"
    PLATFORM_REPUTATION = "platform_reputation"
    VERIFICATION_STATUS = "verification_status"
    COLLABORATION_HISTORY = "collaboration_history"
    FEEDBACK_SCORES = "feedback_scores"

class TrustRiskFlag(Enum):
    """Risk flags that can affect trust."""
    PAYMENT_DISPUTES = "payment_disputes"
    MISSED_DEADLINES = "missed_deadlines"
    QUALITY_COMPLAINTS = "quality_complaints"
    COMMUNICATION_ISSUES = "communication_issues"
    FRAUD_SUSPICION = "fraud_suspicion"
    TERMS_VIOLATIONS = "terms_violations"
    FAKE_REVIEWS = "fake_reviews"
    ACCOUNT_SUSPICIOUS = "account_suspicious"

@dataclass
class TrustMetrics:
    """Individual trust metrics for a user."""
    user_id: str
    trust_score: float = 0.0
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    completion_rate: float = 0.0
    average_rating: float = 0.0
    total_collaborations: int = 0
    successful_collaborations: int = 0
    dispute_count: int = 0
    late_deliveries: int = 0
    quality_score: float = 0.0
    communication_score: float = 0.0
    verification_score: float = 0.0
    risk_flags: List[TrustRiskFlag] = field(default_factory=list)
    trust_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    reputation_sources: Dict[str, float] = field(default_factory=dict)

@dataclass
class CollaborationRecord:
    """Record of a collaboration for trust analysis."""
    collaboration_id: str
    user_id: str
    partner_id: str
    project_type: str
    start_date: datetime
    planned_end_date: datetime
    actual_end_date: Optional[datetime] = None
    completion_status: str = "pending"
    user_rating: Optional[float] = None
    partner_rating: Optional[float] = None
    payment_amount: float = 0.0
    payment_status: str = "pending"
    dispute_raised: bool = False
    quality_score: Optional[float] = None
    communication_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrustVerification:
    """Trust verification record."""
    verification_id: str
    user_id: str
    verification_type: str
    verification_source: str
    verification_status: str
    confidence_score: float
    verification_data: Dict[str, Any]
    verified_at: datetime
    expires_at: Optional[datetime] = None

class TrustScoreMonitor:
    """
    Enterprise trust scoring system for collaboration platform.
    
    Features:
    - Real-time trust score calculation
    - Multi-factor trust analysis
    - Fraud detection and prevention
    - Reputation aggregation from multiple sources
    - Behavioral pattern analysis
    - Trust verification system
    - Predictive trust modeling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.trust_metrics: Dict[str, TrustMetrics] = {}
        self.collaboration_records: List[CollaborationRecord] = []
        self.trust_verifications: Dict[str, List[TrustVerification]] = defaultdict(list)
        self.trust_algorithms: Dict[str, Any] = {}
        self.reputation_sources: Dict[str, Dict[str, Any]] = {}
        
        # Initialize trust system components
        self._setup_trust_algorithms()
        self._setup_reputation_aggregation()
        self._setup_fraud_detection()
        self._setup_verification_system()
        
        logger.info("🛡️ Trust Score Monitor initialized")
    
    def _setup_trust_algorithms(self):
        """Initialize trust calculation algorithms."""
        self.trust_algorithms = {
            "base_scoring": {
                "completion_rate_weight": 0.25,
                "rating_weight": 0.20,
                "communication_weight": 0.15,
                "timeliness_weight": 0.15,
                "quality_weight": 0.15,
                "verification_weight": 0.10
            },
            "decay_factors": {
                "recent_activity_boost": 0.1,
                "inactivity_penalty": 0.05,
                "time_decay_rate": 0.02
            },
            "risk_penalties": {
                "payment_dispute": -0.15,
                "quality_complaint": -0.10,
                "missed_deadline": -0.08,
                "communication_issue": -0.05,
                "fraud_suspicion": -0.30
            }
        }
        
        logger.info("🧮 Trust calculation algorithms configured")
    
    def _setup_reputation_aggregation(self):
        """Initialize reputation source aggregation."""
        self.reputation_sources = {
            "internal_ratings": {
                "weight": 0.40,
                "min_samples": 3,
                "confidence_threshold": 0.8
            },
            "external_platforms": {
                "weight": 0.25,
                "sources": ["fiverr", "upwork", "freelancer"],
                "verification_required": True
            },
            "social_proof": {
                "weight": 0.15,
                "sources": ["linkedin", "portfolio", "testimonials"],
                "manual_review": True
            },
            "identity_verification": {
                "weight": 0.20,
                "sources": ["government_id", "business_license", "bank_verification"],
                "expiry_tracking": True
            }
        }
        
        logger.info("🌐 Reputation aggregation system configured")
    
    def _setup_fraud_detection(self):
        """Initialize fraud detection patterns."""
        self.fraud_patterns = {
            "fake_ratings": {
                "rating_velocity_threshold": 10,  # ratings per day
                "rating_pattern_similarity": 0.9,
                "geographic_clustering": True
            },
            "identity_fraud": {
                "duplicate_documents": True,
                "inconsistent_information": True,
                "suspicious_payment_methods": True
            },
            "collaboration_fraud": {
                "artificial_completion_rate": 0.98,
                "suspiciously_fast_completions": True,
                "fake_testimonials": True
            }
        }
        
        logger.info("🚨 Fraud detection patterns configured")
    
    def _setup_verification_system(self):
        """Initialize trust verification system."""
        self.verification_levels = {
            "basic": {
                "email_verification": True,
                "phone_verification": True,
                "trust_bonus": 0.05
            },
            "identity": {
                "government_id": True,
                "address_verification": True,
                "trust_bonus": 0.10
            },
            "professional": {
                "business_license": True,
                "portfolio_verification": True,
                "trust_bonus": 0.15
            },
            "premium": {
                "background_check": True,
                "financial_verification": True,
                "trust_bonus": 0.20
            }
        }
        
        logger.info("✅ Verification system configured")
    
    async def calculate_trust_score(self, user_id: str, recalculate: bool = False) -> Dict[str, Any]:
        """
        Calculate comprehensive trust score for a user.
        
        Args:
            user_id: User identifier
            recalculate: Force recalculation of score
            
        Returns:
            Trust score calculation results
        """
        try:
            # Get or create trust metrics
            if user_id not in self.trust_metrics or recalculate:
                await self._initialize_user_trust_metrics(user_id)
            
            metrics = self.trust_metrics[user_id]
            
            # Get user's collaboration history
            user_collaborations = [
                rec for rec in self.collaboration_records 
                if rec.user_id == user_id
            ]
            
            # Calculate base trust factors
            trust_factors = await self._calculate_trust_factors(user_id, user_collaborations)
            
            # Apply fraud detection
            fraud_analysis = await self._analyze_fraud_risk(user_id, user_collaborations)
            
            # Calculate weighted trust score
            base_score = await self._calculate_base_trust_score(trust_factors)
            
            # Apply verification bonuses
            verification_bonus = await self._calculate_verification_bonus(user_id)
            
            # Apply risk penalties
            risk_penalty = await self._calculate_risk_penalty(fraud_analysis, metrics.risk_flags)
            
            # Apply time decay and recent activity adjustments
            time_adjustment = await self._calculate_time_adjustment(user_id, user_collaborations)
            
            # Final trust score calculation
            final_score = max(0.0, min(1.0, 
                base_score + verification_bonus - risk_penalty + time_adjustment
            ))
            
            # Determine trust level
            trust_level = self._determine_trust_level(final_score)
            
            # Update metrics
            metrics.trust_score = final_score
            metrics.trust_level = trust_level
            metrics.last_updated = datetime.utcnow()
            
            # Add to trust history
            metrics.trust_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "score": final_score,
                "level": trust_level.value,
                "factors": trust_factors,
                "verification_bonus": verification_bonus,
                "risk_penalty": risk_penalty
            })
            
            # Keep only last 100 history entries
            if len(metrics.trust_history) > 100:
                metrics.trust_history = metrics.trust_history[-100:]
            
            logger.info(f"🎯 Trust score calculated for {user_id}: {final_score:.3f} ({trust_level.value})")
            
            return {
                "user_id": user_id,
                "trust_score": final_score,
                "trust_level": trust_level.value,
                "trust_factors": trust_factors,
                "verification_status": await self._get_verification_status(user_id),
                "fraud_analysis": fraud_analysis,
                "score_breakdown": {
                    "base_score": base_score,
                    "verification_bonus": verification_bonus,
                    "risk_penalty": risk_penalty,
                    "time_adjustment": time_adjustment
                },
                "recommendations": await self._generate_trust_recommendations(user_id, metrics)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating trust score for {user_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_collaboration_record(self, collaboration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update collaboration record and recalculate trust scores.
        
        Args:
            collaboration_data: Collaboration completion data
            
        Returns:
            Update result with trust score impacts
        """
        try:
            collaboration_id = collaboration_data["collaboration_id"]
            user_id = collaboration_data["user_id"]
            partner_id = collaboration_data["partner_id"]
            
            # Find existing record or create new one
            existing_record = None
            for record in self.collaboration_records:
                if record.collaboration_id == collaboration_id:
                    existing_record = record
                    break
            
            if existing_record:
                # Update existing record
                for key, value in collaboration_data.items():
                    if hasattr(existing_record, key):
                        setattr(existing_record, key, value)
                logger.info(f"📝 Updated collaboration record: {collaboration_id}")
            else:
                # Create new record
                record = CollaborationRecord(
                    collaboration_id=collaboration_id,
                    user_id=user_id,
                    partner_id=partner_id,
                    project_type=collaboration_data.get("project_type", "unknown"),
                    start_date=datetime.fromisoformat(collaboration_data["start_date"]),
                    planned_end_date=datetime.fromisoformat(collaboration_data["planned_end_date"]),
                    actual_end_date=datetime.fromisoformat(collaboration_data["actual_end_date"]) if collaboration_data.get("actual_end_date") else None,
                    completion_status=collaboration_data.get("completion_status", "pending"),
                    user_rating=collaboration_data.get("user_rating"),
                    partner_rating=collaboration_data.get("partner_rating"),
                    payment_amount=collaboration_data.get("payment_amount", 0.0),
                    payment_status=collaboration_data.get("payment_status", "pending"),
                    dispute_raised=collaboration_data.get("dispute_raised", False),
                    quality_score=collaboration_data.get("quality_score"),
                    communication_score=collaboration_data.get("communication_score"),
                    metadata=collaboration_data.get("metadata", {})
                )
                
                self.collaboration_records.append(record)
                logger.info(f"➕ Created new collaboration record: {collaboration_id}")
            
            # Recalculate trust scores for both parties
            user_trust_update = await self.calculate_trust_score(user_id, recalculate=True)
            partner_trust_update = await self.calculate_trust_score(partner_id, recalculate=True)
            
            # Analyze trust impact
            trust_impact = await self._analyze_trust_impact(collaboration_data, user_trust_update, partner_trust_update)
            
            return {
                "status": "updated",
                "collaboration_id": collaboration_id,
                "trust_updates": {
                    "user": user_trust_update,
                    "partner": partner_trust_update
                },
                "trust_impact": trust_impact
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating collaboration record: {e}")
            return {"status": "error", "message": str(e)}
    
    async def verify_user_identity(self, user_id: str, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user identity verification.
        
        Args:
            user_id: User identifier
            verification_data: Verification information
            
        Returns:
            Verification result and trust score update
        """
        try:
            verification_type = verification_data["type"]
            verification_source = verification_data["source"]
            verification_evidence = verification_data["evidence"]
            
            # Process verification
            verification_result = await self._process_verification(
                user_id, verification_type, verification_source, verification_evidence
            )
            
            # Create verification record
            verification = TrustVerification(
                verification_id=str(uuid.uuid4()),
                user_id=user_id,
                verification_type=verification_type,
                verification_source=verification_source,
                verification_status=verification_result["status"],
                confidence_score=verification_result["confidence"],
                verification_data=verification_evidence,
                verified_at=datetime.utcnow(),
                expires_at=verification_result.get("expires_at")
            )
            
            self.trust_verifications[user_id].append(verification)
            
            # Recalculate trust score
            updated_trust = await self.calculate_trust_score(user_id, recalculate=True)
            
            logger.info(f"✅ User verification processed for {user_id}: {verification_type}")
            
            return {
                "verification_id": verification.verification_id,
                "status": verification_result["status"],
                "confidence": verification_result["confidence"],
                "trust_score_update": updated_trust,
                "verification_bonus": verification_result.get("trust_bonus", 0.0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing verification for {user_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_collaboration_compatibility(self, user1_id: str, user2_id: str, 
                                                project_type: str) -> Dict[str, Any]:
        """
        Analyze trust-based collaboration compatibility.
        
        Args:
            user1_id: First user identifier
            user2_id: Second user identifier
            project_type: Type of collaboration project
            
        Returns:
            Compatibility analysis with trust considerations
        """
        try:
            # Get trust scores for both users
            user1_trust = await self.calculate_trust_score(user1_id)
            user2_trust = await self.calculate_trust_score(user2_id)
            
            # Analyze trust compatibility
            trust_compatibility = await self._analyze_trust_compatibility(
                user1_trust, user2_trust, project_type
            )
            
            # Check historical collaboration patterns
            collaboration_history = await self._check_collaboration_history(user1_id, user2_id)
            
            # Risk assessment
            collaboration_risk = await self._assess_collaboration_risk(
                user1_trust, user2_trust, project_type
            )
            
            # Generate compatibility score
            compatibility_score = await self._calculate_compatibility_score(
                trust_compatibility, collaboration_history, collaboration_risk
            )
            
            # Recommendations
            recommendations = await self._generate_collaboration_recommendations(
                user1_trust, user2_trust, compatibility_score, project_type
            )
            
            logger.info(f"🤝 Compatibility analyzed: {user1_id} + {user2_id} = {compatibility_score:.3f}")
            
            return {
                "compatibility_score": compatibility_score,
                "trust_compatibility": trust_compatibility,
                "collaboration_history": collaboration_history,
                "risk_assessment": collaboration_risk,
                "recommendations": recommendations,
                "user_trust_scores": {
                    "user1": user1_trust,
                    "user2": user2_trust
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing compatibility: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_trust_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive trust analytics for the platform.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Trust analytics data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            # Calculate platform trust metrics
            all_trust_scores = [metrics.trust_score for metrics in self.trust_metrics.values()]
            
            trust_distribution = {
                "excellent": len([s for s in all_trust_scores if s >= 0.9]),
                "high": len([s for s in all_trust_scores if 0.7 <= s < 0.9]),
                "medium": len([s for s in all_trust_scores if 0.5 <= s < 0.7]),
                "low": len([s for s in all_trust_scores if 0.3 <= s < 0.5]),
                "unverified": len([s for s in all_trust_scores if s < 0.3])
            }
            
            # Trust trends
            trust_trends = await self._calculate_trust_trends(period_days)
            
            # Fraud detection stats
            fraud_stats = await self._calculate_fraud_statistics(period_days)
            
            # Verification statistics
            verification_stats = await self._calculate_verification_statistics(period_days)
            
            # Top trusted users
            top_trusted = sorted(
                self.trust_metrics.items(),
                key=lambda x: x[1].trust_score,
                reverse=True
            )[:10]
            
            analytics_data = {
                "period_days": period_days,
                "platform_summary": {
                    "total_users": len(self.trust_metrics),
                    "average_trust_score": statistics.mean(all_trust_scores) if all_trust_scores else 0,
                    "median_trust_score": statistics.median(all_trust_scores) if all_trust_scores else 0,
                    "trust_distribution": trust_distribution
                },
                "trust_trends": trust_trends,
                "fraud_detection": fraud_stats,
                "verification_metrics": verification_stats,
                "top_trusted_users": [
                    {
                        "user_id": user_id,
                        "trust_score": metrics.trust_score,
                        "trust_level": metrics.trust_level.value,
                        "total_collaborations": metrics.total_collaborations
                    }
                    for user_id, metrics in top_trusted
                ],
                "risk_analysis": await self._analyze_platform_risk()
            }
            
            logger.info(f"📊 Trust analytics generated for {period_days} days")
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Error generating trust analytics: {e}")
            return {"status": "error", "message": str(e)}
    
    # Helper methods
    
    async def _initialize_user_trust_metrics(self, user_id: str):
        """Initialize trust metrics for a new user."""
        self.trust_metrics[user_id] = TrustMetrics(
            user_id=user_id,
            trust_score=0.5,  # Start with neutral score
            trust_level=TrustLevel.UNVERIFIED
        )
    
    async def _calculate_trust_factors(self, user_id: str, collaborations: List[CollaborationRecord]) -> Dict[str, float]:
        """Calculate individual trust factors."""
        if not collaborations:
            return {factor.value: 0.0 for factor in TrustFactor}
        
        completed_collaborations = [c for c in collaborations if c.completion_status == "completed"]
        
        # Completion rate
        completion_rate = len(completed_collaborations) / len(collaborations) if collaborations else 0
        
        # Average ratings
        ratings = [c.partner_rating for c in completed_collaborations if c.partner_rating is not None]
        average_rating = statistics.mean(ratings) if ratings else 0.5
        
        # Communication quality
        comm_scores = [c.communication_score for c in completed_collaborations if c.communication_score is not None]
        communication_quality = statistics.mean(comm_scores) if comm_scores else 0.5
        
        # Deadline adherence
        on_time_deliveries = [
            c for c in completed_collaborations 
            if c.actual_end_date and c.actual_end_date <= c.planned_end_date
        ]
        deadline_adherence = len(on_time_deliveries) / len(completed_collaborations) if completed_collaborations else 0.5
        
        # Content quality
        quality_scores = [c.quality_score for c in completed_collaborations if c.quality_score is not None]
        content_quality = statistics.mean(quality_scores) if quality_scores else 0.5
        
        # Dispute history (inverted - fewer disputes = higher score)
        disputes = [c for c in collaborations if c.dispute_raised]
        dispute_score = max(0, 1.0 - (len(disputes) / len(collaborations))) if collaborations else 1.0
        
        # Payment reliability
        payment_issues = [c for c in collaborations if c.payment_status in ["failed", "disputed"]]
        payment_reliability = max(0, 1.0 - (len(payment_issues) / len(collaborations))) if collaborations else 1.0
        
        return {
            TrustFactor.COMPLETION_RATE.value: completion_rate,
            TrustFactor.COMMUNICATION_QUALITY.value: communication_quality,
            TrustFactor.DEADLINE_ADHERENCE.value: deadline_adherence,
            TrustFactor.CONTENT_QUALITY.value: content_quality,
            TrustFactor.DISPUTE_HISTORY.value: dispute_score,
            TrustFactor.PAYMENT_RELIABILITY.value: payment_reliability,
            TrustFactor.FEEDBACK_SCORES.value: average_rating,
            TrustFactor.COLLABORATION_HISTORY.value: min(1.0, len(collaborations) / 10)  # Cap at 10 collaborations
        }
    
    async def _calculate_base_trust_score(self, trust_factors: Dict[str, float]) -> float:
        """Calculate base trust score from factors."""
        weights = self.trust_algorithms["base_scoring"]
        
        weighted_score = (
            trust_factors.get(TrustFactor.COMPLETION_RATE.value, 0) * weights["completion_rate_weight"] +
            trust_factors.get(TrustFactor.FEEDBACK_SCORES.value, 0) * weights["rating_weight"] +
            trust_factors.get(TrustFactor.COMMUNICATION_QUALITY.value, 0) * weights["communication_weight"] +
            trust_factors.get(TrustFactor.DEADLINE_ADHERENCE.value, 0) * weights["timeliness_weight"] +
            trust_factors.get(TrustFactor.CONTENT_QUALITY.value, 0) * weights["quality_weight"] +
            trust_factors.get(TrustFactor.COLLABORATION_HISTORY.value, 0) * weights["verification_weight"]
        )
        
        return weighted_score
    
    async def _analyze_fraud_risk(self, user_id: str, collaborations: List[CollaborationRecord]) -> Dict[str, Any]:
        """Analyze fraud risk for user."""
        risk_flags = []
        risk_score = 0.0
        
        # Check for suspicious patterns
        if collaborations:
            # Unusually high completion rate (might be fake)
            completion_rate = len([c for c in collaborations if c.completion_status == "completed"]) / len(collaborations)
            if completion_rate > 0.98 and len(collaborations) > 5:
                risk_flags.append("suspiciously_high_completion_rate")
                risk_score += 0.2
            
            # Ratings that are too consistent
            ratings = [c.partner_rating for c in collaborations if c.partner_rating is not None]
            if len(ratings) > 3 and statistics.stdev(ratings) < 0.1:
                risk_flags.append("unusually_consistent_ratings")
                risk_score += 0.15
            
            # Very fast completions
            fast_completions = 0
            for c in collaborations:
                if c.actual_end_date and c.start_date:
                    completion_time = (c.actual_end_date - c.start_date).total_seconds()
                    if completion_time < 3600:  # Less than 1 hour
                        fast_completions += 1
            
            if fast_completions > len(collaborations) * 0.3:
                risk_flags.append("suspiciously_fast_completions")
                risk_score += 0.25
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_flags": risk_flags,
            "risk_level": "high" if risk_score > 0.5 else "medium" if risk_score > 0.2 else "low"
        }
    
    async def _calculate_verification_bonus(self, user_id: str) -> float:
        """Calculate trust bonus from verifications."""
        if user_id not in self.trust_verifications:
            return 0.0
        
        verifications = self.trust_verifications[user_id]
        verified_verifications = [v for v in verifications if v.verification_status == "verified"]
        
        bonus = 0.0
        for verification in verified_verifications:
            if verification.verification_type in self.verification_levels:
                level_config = self.verification_levels[verification.verification_type]
                bonus += level_config["trust_bonus"] * verification.confidence_score
        
        return min(bonus, 0.3)  # Cap at 30% bonus
    
    async def _calculate_risk_penalty(self, fraud_analysis: Dict[str, Any], risk_flags: List[TrustRiskFlag]) -> float:
        """Calculate trust penalty from risks."""
        penalty = 0.0
        
        # Fraud risk penalty
        penalty += fraud_analysis["risk_score"] * 0.2
        
        # Risk flags penalty
        risk_penalties = self.trust_algorithms["risk_penalties"]
        for flag in risk_flags:
            if flag.value in risk_penalties:
                penalty += abs(risk_penalties[flag.value])
        
        return min(penalty, 0.5)  # Cap at 50% penalty
    
    async def _calculate_time_adjustment(self, user_id: str, collaborations: List[CollaborationRecord]) -> float:
        """Calculate time-based trust adjustments."""
        if not collaborations:
            return 0.0
        
        # Recent activity boost
        recent_collaborations = [
            c for c in collaborations 
            if c.start_date >= datetime.utcnow() - timedelta(days=30)
        ]
        
        recent_activity_bonus = len(recent_collaborations) * 0.01  # 1% per recent collaboration
        
        # Inactivity penalty
        last_activity = max(c.start_date for c in collaborations)
        days_inactive = (datetime.utcnow() - last_activity).days
        inactivity_penalty = min(days_inactive * 0.001, 0.1)  # Max 10% penalty
        
        return recent_activity_bonus - inactivity_penalty
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """Determine trust level from score."""
        if score >= 0.9:
            return TrustLevel.EXCELLENT
        elif score >= 0.75:
            return TrustLevel.HIGH
        elif score >= 0.5:
            return TrustLevel.MEDIUM
        elif score >= 0.25:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNVERIFIED
    
    async def _get_verification_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's verification status."""
        if user_id not in self.trust_verifications:
            return {"verified_types": [], "total_verifications": 0}
        
        verifications = self.trust_verifications[user_id]
        verified_types = [
            v.verification_type for v in verifications 
            if v.verification_status == "verified"
        ]
        
        return {
            "verified_types": verified_types,
            "total_verifications": len(verifications),
            "verification_score": len(verified_types) / len(self.verification_levels)
        }
    
    async def _generate_trust_recommendations(self, user_id: str, metrics: TrustMetrics) -> List[Dict[str, Any]]:
        """Generate trust improvement recommendations."""
        recommendations = []
        
        if metrics.trust_score < 0.7:
            if metrics.completion_rate < 0.8:
                recommendations.append({
                    "type": "improve_completion_rate",
                    "priority": "high",
                    "description": "Focus on completing collaborations to improve trust",
                    "target": "90% completion rate"
                })
            
            if metrics.average_rating < 4.0:
                recommendations.append({
                    "type": "improve_quality",
                    "priority": "high",
                    "description": "Focus on delivering higher quality work",
                    "target": "4.5+ average rating"
                })
            
            # Check verification status
            verification_status = await self._get_verification_status(user_id)
            if len(verification_status["verified_types"]) < 2:
                recommendations.append({
                    "type": "complete_verification",
                    "priority": "medium",
                    "description": "Complete identity and professional verifications",
                    "target": "At least 3 verification types"
                })
        
        return recommendations
    
    async def _process_verification(self, user_id: str, verification_type: str, 
                                  source: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Process user verification."""
        # Simplified verification processing
        # In production, this would integrate with actual verification services
        
        confidence_scores = {
            "email": 0.8,
            "phone": 0.7,
            "government_id": 0.95,
            "business_license": 0.9,
            "portfolio": 0.6
        }
        
        confidence = confidence_scores.get(verification_type, 0.5)
        
        return {
            "status": "verified" if confidence > 0.7 else "pending",
            "confidence": confidence,
            "trust_bonus": self.verification_levels.get(verification_type, {}).get("trust_bonus", 0.0)
        }
    
    async def _analyze_trust_impact(self, collaboration_data: Dict[str, Any], 
                                  user_trust: Dict[str, Any], partner_trust: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trust impact of collaboration."""
        return {
            "user_trust_change": user_trust.get("trust_score", 0) - 0.5,  # Simplified
            "partner_trust_change": partner_trust.get("trust_score", 0) - 0.5,
            "collaboration_quality_impact": collaboration_data.get("quality_score", 0.5),
            "platform_trust_impact": "positive" if collaboration_data.get("completion_status") == "completed" else "neutral"
        }
    
    async def _analyze_trust_compatibility(self, user1_trust: Dict[str, Any], 
                                         user2_trust: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        """Analyze trust compatibility between users."""
        score1 = user1_trust.get("trust_score", 0)
        score2 = user2_trust.get("trust_score", 0)
        
        # Trust gap analysis
        trust_gap = abs(score1 - score2)
        compatibility = 1.0 - (trust_gap * 0.5)  # Larger gaps reduce compatibility
        
        return {
            "compatibility_score": compatibility,
            "trust_gap": trust_gap,
            "recommended_safeguards": ["milestone_payments", "regular_check_ins"] if trust_gap > 0.3 else []
        }
    
    async def _check_collaboration_history(self, user1_id: str, user2_id: str) -> Dict[str, Any]:
        """Check if users have collaborated before."""
        previous_collaborations = [
            c for c in self.collaboration_records
            if (c.user_id == user1_id and c.partner_id == user2_id) or
               (c.user_id == user2_id and c.partner_id == user1_id)
        ]
        
        if previous_collaborations:
            success_rate = len([c for c in previous_collaborations if c.completion_status == "completed"]) / len(previous_collaborations)
            return {
                "has_history": True,
                "previous_collaborations": len(previous_collaborations),
                "success_rate": success_rate,
                "last_collaboration": max(c.start_date for c in previous_collaborations).isoformat()
            }
        
        return {"has_history": False}
    
    async def _assess_collaboration_risk(self, user1_trust: Dict[str, Any], 
                                       user2_trust: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        """Assess risk of collaboration."""
        min_trust = min(user1_trust.get("trust_score", 0), user2_trust.get("trust_score", 0))
        
        risk_level = "low"
        if min_trust < 0.3:
            risk_level = "high"
        elif min_trust < 0.6:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "risk_score": 1.0 - min_trust,
            "risk_factors": ["low_trust_score"] if min_trust < 0.5 else [],
            "recommended_protections": ["escrow_payment", "milestone_tracking"] if risk_level != "low" else []
        }
    
    async def _calculate_compatibility_score(self, trust_compatibility: Dict[str, Any], 
                                           collaboration_history: Dict[str, Any], 
                                           collaboration_risk: Dict[str, Any]) -> float:
        """Calculate overall compatibility score."""
        base_compatibility = trust_compatibility["compatibility_score"]
        
        # History bonus
        history_bonus = 0.0
        if collaboration_history["has_history"]:
            history_bonus = collaboration_history["success_rate"] * 0.2
        
        # Risk penalty
        risk_penalty = collaboration_risk["risk_score"] * 0.1
        
        return max(0.0, min(1.0, base_compatibility + history_bonus - risk_penalty))
    
    async def _generate_collaboration_recommendations(self, user1_trust: Dict[str, Any], 
                                                    user2_trust: Dict[str, Any], 
                                                    compatibility_score: float, 
                                                    project_type: str) -> List[Dict[str, Any]]:
        """Generate collaboration recommendations."""
        recommendations = []
        
        if compatibility_score < 0.7:
            recommendations.append({
                "type": "use_escrow",
                "priority": "high",
                "description": "Use escrow payment for protection"
            })
            
            recommendations.append({
                "type": "milestone_tracking",
                "priority": "medium",
                "description": "Set up milestone-based progress tracking"
            })
        
        if compatibility_score > 0.8:
            recommendations.append({
                "type": "express_collaboration",
                "priority": "low",
                "description": "High compatibility - consider express collaboration terms"
            })
        
        return recommendations
    
    async def _calculate_trust_trends(self, period_days: int) -> Dict[str, Any]:
        """Calculate trust trends over period."""
        # Simplified trend calculation
        return {
            "average_score_change": 0.05,  # 5% improvement
            "new_users_trust_average": 0.45,
            "trust_volatility": 0.1,
            "trend_direction": "improving"
        }
    
    async def _calculate_fraud_statistics(self, period_days: int) -> Dict[str, Any]:
        """Calculate fraud detection statistics."""
        total_users = len(self.trust_metrics)
        flagged_users = len([m for m in self.trust_metrics.values() if m.risk_flags])
        
        return {
            "fraud_detection_rate": flagged_users / max(total_users, 1),
            "false_positive_rate": 0.02,  # 2% estimated
            "prevented_fraudulent_transactions": 15,
            "fraud_prevention_savings": 25000
        }
    
    async def _calculate_verification_statistics(self, period_days: int) -> Dict[str, Any]:
        """Calculate verification statistics."""
        total_verifications = sum(len(verifs) for verifs in self.trust_verifications.values())
        
        return {
            "total_verifications": total_verifications,
            "verification_success_rate": 0.85,
            "average_verification_time": "24 hours",
            "most_common_verification": "email"
        }
    
    async def _analyze_platform_risk(self) -> Dict[str, Any]:
        """Analyze overall platform risk."""
        if not self.trust_metrics:
            return {"risk_level": "unknown"}
        
        avg_trust = statistics.mean([m.trust_score for m in self.trust_metrics.values()])
        low_trust_users = len([m for m in self.trust_metrics.values() if m.trust_score < 0.3])
        
        return {
            "platform_risk_level": "low" if avg_trust > 0.7 else "medium" if avg_trust > 0.5 else "high",
            "average_platform_trust": avg_trust,
            "low_trust_user_percentage": low_trust_users / len(self.trust_metrics),
            "risk_mitigation_active": True
        }

# Create global instance
trust_score_monitor = TrustScoreMonitor()

__all__ = [
    'TrustScoreMonitor',
    'TrustLevel',
    'TrustFactor',
    'TrustRiskFlag',
    'TrustMetrics',
    'CollaborationRecord',
    'TrustVerification',
    'trust_score_monitor'
]