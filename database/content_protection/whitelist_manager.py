"""
Whitelist Manager Repository

Ultra-advanced whitelist management system for authorized content and users
with AI-powered risk assessment, dynamic trust scoring, and automated whitelist optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION 
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models.content_models import (
    WhitelistEntry, WhitelistCategory, WhitelistApproval,
    TrustScore, UserWhitelist, ContentWhitelist, DomainWhitelist
)
from ..security.encryption import AdvancedEncryptionManager
from ...core.config import DatabaseConfig
from ...utils.trust_analyzer import TrustAnalyzer
from ...utils.ai_models import RiskAssessmentModel
from ...utils.validators import WhitelistValidator


logger = logging.getLogger(__name__)


class WhitelistType(Enum):
    """Types of whitelist entries"""
    USER = "user"
    CONTENT = "content"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    CREATOR = "creator"
    PLATFORM = "platform"
    ORGANIZATION = "organization"
    COLLABORATION = "collaboration"
    API_CLIENT = "api_client"
    TRUSTED_PARTNER = "trusted_partner"


class WhitelistStatus(Enum):
    """Whitelist entry status"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class TrustLevel(Enum):
    """Trust levels for whitelist entries"""
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERIFIED = "verified"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ApprovalType(Enum):
    """Types of whitelist approvals"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AI_ASSISTED = "ai_assisted"
    BATCH_APPROVAL = "batch_approval"
    EMERGENCY = "emergency"
    TEMPORARY = "temporary"


class RiskCategory(Enum):
    """Risk categories for assessment"""
    CONTENT_VIOLATION = "content_violation"
    IMPERSONATION = "impersonation"
    FRAUD = "fraud"
    SPAM = "spam"
    MALWARE = "malware"
    PHISHING = "phishing"
    COPYRIGHT_ABUSE = "copyright_abuse"
    REPUTATION_DAMAGE = "reputation_damage"


class WhitelistManagerError(Exception):
    """Custom exception for whitelist operations"""
    pass


class WhitelistManager:
    """
    Ultra-advanced whitelist management system with enterprise features:
    - AI-powered risk assessment and trust scoring
    - Dynamic whitelist optimization and maintenance
    - Multi-level approval workflows
    - Real-time monitoring and threat detection
    - Automated whitelist lifecycle management
    - Compliance and audit trail tracking
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        config: DatabaseConfig,
        encryption_manager: Optional[AdvancedEncryptionManager] = None,
        trust_analyzer: Optional[TrustAnalyzer] = None,
        risk_model: Optional[RiskAssessmentModel] = None
    ):
        self.db_session = db_session
        self.config = config
        self.encryption_manager = encryption_manager or AdvancedEncryptionManager()
        self.trust_analyzer = trust_analyzer or TrustAnalyzer()
        self.risk_model = risk_model or RiskAssessmentModel()
        self.whitelist_validator = WhitelistValidator()
        
        # Whitelist configuration
        self.max_whitelist_entries = config.max_whitelist_entries or 10000
        self.trust_score_threshold = config.trust_score_threshold or 0.7
        self.automatic_approval_enabled = config.automatic_approval_enabled or True
        self.ai_risk_assessment_enabled = config.ai_risk_assessment_enabled or True
        
        # Trust scoring weights
        self.trust_factors = {
            "historical_behavior": 0.3,
            "verification_status": 0.25,
            "community_reputation": 0.2,
            "content_quality": 0.15,
            "compliance_record": 0.1
        }
        
        # Cache for performance
        self.whitelist_cache = {}
        self.trust_scores_cache = {}
        self.cache_ttl = 600  # 10 minutes
        
        # Performance metrics
        self.whitelist_metrics = {
            "total_entries": 0,
            "active_entries": 0,
            "pending_approvals": 0,
            "risk_assessments_per_hour": 0,
            "avg_trust_score": 0.0,
            "false_positive_rate": 0.0,
            "automated_approvals": 0
        }
        
        logger.info("WhitelistManager initialized with AI risk assessment")
    
    async def add_to_whitelist(
        self,
        entity_type: WhitelistType,
        entity_identifier: str,
        entity_metadata: Dict[str, Any],
        requester_id: str,
        approval_type: ApprovalType = ApprovalType.MANUAL,
        expiration_date: Optional[datetime] = None,
        trust_level_override: Optional[TrustLevel] = None
    ) -> WhitelistEntry:
        """
        Add entity to whitelist with comprehensive validation and risk assessment
        
        Args:
            entity_type: Type of entity to whitelist
            entity_identifier: Unique identifier for entity
            entity_metadata: Additional metadata about entity
            requester_id: ID of user requesting whitelist addition
            approval_type: Type of approval process
            expiration_date: Optional expiration date
            trust_level_override: Override calculated trust level
            
        Returns:
            Created WhitelistEntry record
            
        Raises:
            WhitelistManagerError: If addition fails
        """



        try:
            # Validate entity identifier
            await self._validate_entity_identifier(entity_type, entity_identifier)
            
            # Check if entity already whitelisted
            existing_entry = await self._get_existing_whitelist_entry(
                entity_type, entity_identifier
            )
            
            if existing_entry and existing_entry.status in [
                WhitelistStatus.ACTIVE.value, 
                WhitelistStatus.PENDING.value
            ]:
                raise WhitelistManagerError(f"Entity already whitelisted: {entity_identifier}")
            
            # Perform AI-powered risk assessment
            risk_assessment = await self._perform_risk_assessment(
                entity_type, entity_identifier, entity_metadata
            )
            
            # Calculate trust score
            trust_score = await self._calculate_trust_score(
                entity_type, entity_identifier, entity_metadata, risk_assessment
            )
            
            # Determine trust level
            trust_level = trust_level_override or await self._determine_trust_level(trust_score)
            
            # Create whitelist entry
            entry_id = uuid4()
            
            # Encrypt sensitive metadata
            encrypted_metadata = await self.encryption_manager.encrypt_data(
                json.dumps(entity_metadata)
            )
            
            # Create main whitelist entry
            whitelist_entry = WhitelistEntry(
                id=entry_id,
                entity_type=entity_type.value,
                entity_identifier=entity_identifier,
                entity_metadata=encrypted_metadata,
                status=WhitelistStatus.PENDING.value,
                trust_level=trust_level.value,
                trust_score=trust_score,
                risk_score=risk_assessment["overall_risk_score"],
                requester_id=requester_id,
                approval_type=approval_type.value,
                expiration_date=expiration_date,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(whitelist_entry)
            
            # Create trust score record
            trust_score_record = TrustScore(
                id=uuid4(),
                whitelist_entry_id=entry_id,
                trust_score=trust_score,
                trust_factors=risk_assessment["trust_factors"],
                calculation_method="ai_hybrid",
                calculated_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(trust_score_record)
            
            # Handle automatic approval
            if (approval_type == ApprovalType.AUTOMATIC and 
                self.automatic_approval_enabled and
                trust_score >= self.trust_score_threshold and
                risk_assessment["overall_risk_score"] < 0.3):
                
                await self._auto_approve_entry(whitelist_entry, risk_assessment)
            
            await self.db_session.commit()
            
            # Update metrics
            self.whitelist_metrics["total_entries"] += 1
            if whitelist_entry.status == WhitelistStatus.PENDING.value:
                self.whitelist_metrics["pending_approvals"] += 1
            
            # Clear cache
            self._clear_whitelist_cache()
            
            logger.info(f"Entity added to whitelist: {entity_identifier} [{entity_type.value}] with trust score {trust_score:.3f}")
            return whitelist_entry
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Whitelist addition failed: {e}")
            raise WhitelistManagerError(f"Whitelist addition failed: {e}")
    
    async def approve_whitelist_entry(
        self,
        entry_id: UUID,
        approver_id: str,
        approval_notes: Optional[str] = None,
        conditional_approval: bool = False,
        approval_conditions: Optional[List[str]] = None
    ) -> WhitelistEntry:
        """
        Approve pending whitelist entry with detailed audit trail
        
        Args:
            entry_id: Whitelist entry ID
            approver_id: ID of approving user
            approval_notes: Optional approval notes
            conditional_approval: Whether approval has conditions
            approval_conditions: List of approval conditions
            
        Returns:
            Approved WhitelistEntry record
        """



        try:
            # Get pending entry
            entry = await self.db_session.query(WhitelistEntry).filter(
                WhitelistEntry.id == entry_id
            ).first()
            
            if not entry:
                raise WhitelistManagerError(f"Whitelist entry not found: {entry_id}")
            
            if entry.status != WhitelistStatus.PENDING.value:
                raise WhitelistManagerError(f"Entry not pending approval: {entry.status}")
            
            # Validate approver permissions
            await self._validate_approver_permissions(approver_id, entry)
            
            # Perform final risk check
            final_risk_check = await self._perform_final_risk_check(entry)
            
            if final_risk_check["high_risk"]:
                raise WhitelistManagerError(f"High risk detected during final check: {final_risk_check['reasons']}")
            
            # Update entry status
            entry.status = WhitelistStatus.APPROVED.value if not conditional_approval else WhitelistStatus.UNDER_REVIEW.value
            entry.approved_at = datetime.now(timezone.utc)
            entry.approved_by = approver_id
            entry.updated_at = datetime.now(timezone.utc)
            
            # Create approval record
            approval_record = WhitelistApproval(
                id=uuid4(),
                whitelist_entry_id=entry_id,
                approver_id=approver_id,
                approval_status="approved" if not conditional_approval else "conditional",
                approval_notes=approval_notes,
                approval_conditions=approval_conditions or [],
                conditional_approval=conditional_approval,
                approved_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(approval_record)
            
            # If not conditional, activate entry
            if not conditional_approval:
                await self._activate_whitelist_entry(entry)
            
            await self.db_session.commit()
            
            # Update metrics
            self.whitelist_metrics["pending_approvals"] -= 1
            if entry.status == WhitelistStatus.ACTIVE.value:
                self.whitelist_metrics["active_entries"] += 1
            
            # Clear cache
            self._clear_whitelist_cache()
            
            logger.info(f"Whitelist entry approved: {entry.entity_identifier} by {approver_id}")
            return entry
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Whitelist approval failed: {e}")
            raise WhitelistManagerError(f"Whitelist approval failed: {e}")
    
    async def check_whitelist_status(
        self,
        entity_type: WhitelistType,
        entity_identifier: str,
        check_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check comprehensive whitelist status for entity
        
        Args:
            entity_type: Type of entity to check
            entity_identifier: Entity identifier
            check_context: Additional context for check
            
        Returns:
            Detailed whitelist status information
        """



        try:
            # Check cache first
            cache_key = f"whitelist_status_{entity_type.value}_{entity_identifier}"
            if cache_key in self.whitelist_cache:
                cache_entry = self.whitelist_cache[cache_key]
                if datetime.now() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cache_entry["status"]
            
            # Get whitelist entry
            entry = await self._get_existing_whitelist_entry(entity_type, entity_identifier)
            
            if not entry:
                return {
                    "whitelisted": False,
                    "status": None,
                    "trust_level": None,
                    "trust_score": 0.0,
                    "risk_score": 1.0,
                    "reason": "not_whitelisted"
                }
            
            # Check if entry is expired
            if entry.expiration_date and entry.expiration_date < datetime.now(timezone.utc):
                await self._handle_expired_entry(entry)
                return {
                    "whitelisted": False,
                    "status": "expired",
                    "trust_level": entry.trust_level,
                    "trust_score": entry.trust_score,
                    "risk_score": entry.risk_score,
                    "reason": "entry_expired",
                    "expired_at": entry.expiration_date.isoformat()
                }
            
            # Get current trust score
            current_trust_score = await self._get_current_trust_score(entry)
            
            # Perform real-time risk assessment if context provided
            real_time_risk = None
            if check_context and self.ai_risk_assessment_enabled:
                real_time_risk = await self._perform_real_time_risk_check(
                    entry, check_context
                )
            
            # Determine final status
            is_whitelisted = entry.status == WhitelistStatus.ACTIVE.value
            
            # Additional checks for active entries
            if is_whitelisted and real_time_risk:
                if real_time_risk["risk_score"] > 0.8:
                    # High risk detected, temporarily suspend
                    await self._temporarily_suspend_entry(entry, real_time_risk)
                    is_whitelisted = False
            
            status_info = {
                "whitelisted": is_whitelisted,
                "status": entry.status,
                "trust_level": entry.trust_level,
                "trust_score": current_trust_score,
                "risk_score": entry.risk_score,
                "entry_id": str(entry.id),
                "created_at": entry.created_at.isoformat(),
                "last_updated": entry.updated_at.isoformat()
            }
            
            # Add real-time risk information
            if real_time_risk:
                status_info["real_time_risk"] = real_time_risk
            
            # Cache result
            self.whitelist_cache[cache_key] = {
                "status": status_info,
                "timestamp": datetime.now()
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Whitelist status check failed: {e}")
            raise WhitelistManagerError(f"Whitelist status check failed: {e}")
    
    async def bulk_whitelist_operation(
        self,
        operation: str,
        entities: List[Dict[str, Any]],
        requester_id: str,
        operation_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform bulk whitelist operations with batch processing
        
        Args:
            operation: Type of operation (add, approve, remove, suspend)
            entities: List of entities to process
            requester_id: ID of user requesting operation
            operation_metadata: Additional operation metadata
            
        Returns:
            Bulk operation results
        """



        try:
            operation_id = uuid4()
            operation_start = datetime.now(timezone.utc)
            
            results = {
                "operation_id": str(operation_id),
                "operation": operation,
                "total_entities": len(entities),
                "successful": 0,
                "failed": 0,
                "results": [],
                "errors": [],
                "execution_time_seconds": 0
            }
            
            # Validate operation
            if operation not in ["add", "approve", "remove", "suspend", "activate"]:
                raise WhitelistManagerError(f"Invalid bulk operation: {operation}")
            
            # Process entities in batches
            batch_size = min(50, len(entities))  # Process max 50 at a time
            
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                batch_results = await self._process_batch_operation(
                    operation, batch, requester_id, operation_metadata
                )
                
                # Aggregate results
                results["successful"] += batch_results["successful"]
                results["failed"] += batch_results["failed"]
                results["results"].extend(batch_results["results"])
                results["errors"].extend(batch_results["errors"])
                
                # Commit batch
                await self.db_session.commit()
            
            # Calculate execution time
            results["execution_time_seconds"] = (
                datetime.now(timezone.utc) - operation_start
            ).total_seconds()
            
            # Update metrics
            if operation == "add":
                self.whitelist_metrics["total_entries"] += results["successful"]
            elif operation == "approve":
                self.whitelist_metrics["pending_approvals"] -= results["successful"]
                self.whitelist_metrics["active_entries"] += results["successful"]
            
            # Clear cache
            self._clear_whitelist_cache()
            
            logger.info(f"Bulk {operation} operation completed: {results['successful']}/{results['total_entities']} successful")
            return results
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Bulk whitelist operation failed: {e}")
            raise WhitelistManagerError(f"Bulk whitelist operation failed: {e}")
    
    async def optimize_whitelist_performance(
        self,
        optimization_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize whitelist performance using AI analysis
        
        Args:
            optimization_criteria: Specific optimization criteria
            
        Returns:
            Optimization results and recommendations
        """



        try:
            optimization_start = datetime.now(timezone.utc)
            
            # Get all whitelist entries for analysis
            entries = await self.db_session.query(WhitelistEntry).options(
                selectinload(WhitelistEntry.trust_scores),
                selectinload(WhitelistEntry.approvals)
            ).all()
            
            optimization_results = {
                "analysis_timestamp": optimization_start.isoformat(),
                "total_entries_analyzed": len(entries),
                "optimization_recommendations": [],
                "performance_metrics": {},
                "cleanup_suggestions": [],
                "trust_score_distribution": {},
                "execution_time_seconds": 0
            }
            
            # Analyze trust score distribution
            trust_scores = [entry.trust_score for entry in entries if entry.trust_score is not None]
            if trust_scores:
                optimization_results["trust_score_distribution"] = {
                    "average": sum(trust_scores) / len(trust_scores),
                    "median": sorted(trust_scores)[len(trust_scores) // 2],
                    "high_trust_count": len([s for s in trust_scores if s > 0.8]),
                    "low_trust_count": len([s for s in trust_scores if s < 0.3]),
                    "total_scored": len(trust_scores)
                }
            
            # Identify optimization opportunities
            for entry in entries:
                # Check for expired entries
                if (entry.expiration_date and 
                    entry.expiration_date < datetime.now(timezone.utc) and
                    entry.status == WhitelistStatus.ACTIVE.value):
                    
                    optimization_results["cleanup_suggestions"].append({
                        "type": "expired_entry",
                        "entry_id": str(entry.id),
                        "entity_identifier": entry.entity_identifier,
                        "recommendation": "Remove expired entry"
                    })
                
                # Check for low trust scores
                if entry.trust_score and entry.trust_score < 0.3:
                    optimization_results["optimization_recommendations"].append({
                        "type": "low_trust_score",
                        "entry_id": str(entry.id),
                        "entity_identifier": entry.entity_identifier,
                        "current_trust_score": entry.trust_score,
                        "recommendation": "Review entry for potential removal or trust score recalculation"
                    })
                
                # Check for stale entries (no activity in 90 days)
                if (entry.updated_at < datetime.now(timezone.utc) - timedelta(days=90) and
                    entry.status == WhitelistStatus.ACTIVE.value):
                    
                    optimization_results["optimization_recommendations"].append({
                        "type": "stale_entry",
                        "entry_id": str(entry.id),
                        "entity_identifier": entry.entity_identifier,
                        "last_updated": entry.updated_at.isoformat(),
                        "recommendation": "Review entry activity and consider expiration date"
                    })
            
            # Calculate performance metrics
            active_entries = [e for e in entries if e.status == WhitelistStatus.ACTIVE.value]
            pending_entries = [e for e in entries if e.status == WhitelistStatus.PENDING.value]
            
            optimization_results["performance_metrics"] = {
                "active_entries_count": len(active_entries),
                "pending_entries_count": len(pending_entries),
                "average_approval_time_hours": await self._calculate_average_approval_time(),
                "whitelist_utilization_rate": len(active_entries) / self.max_whitelist_entries * 100,
                "trust_score_coverage": len(trust_scores) / len(entries) * 100 if entries else 0
            }
            
            # AI-powered recommendations
            if self.ai_risk_assessment_enabled:
                ai_recommendations = await self._generate_ai_optimization_recommendations(entries)
                optimization_results["optimization_recommendations"].extend(ai_recommendations)
            
            # Calculate execution time
            optimization_results["execution_time_seconds"] = (
                datetime.now(timezone.utc) - optimization_start
            ).total_seconds()
            
            logger.info(f"Whitelist optimization completed: {len(optimization_results['optimization_recommendations'])} recommendations generated")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Whitelist optimization failed: {e}")
            raise WhitelistManagerError(f"Whitelist optimization failed: {e}")
    
    async def generate_whitelist_analytics(
        self,
        analytics_period_days: int = 30,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive whitelist analytics and insights
        
        Args:
            analytics_period_days: Period for analytics calculation
            include_predictions: Whether to include ML predictions
            
        Returns:
            Comprehensive analytics report
        """



        try:
            analysis_start = datetime.now(timezone.utc)
            period_start = analysis_start - timedelta(days=analytics_period_days)
            
            # Get entries for analysis period
            entries = await self.db_session.query(WhitelistEntry).filter(
                WhitelistEntry.created_at >= period_start
            ).options(
                selectinload(WhitelistEntry.trust_scores),
                selectinload(WhitelistEntry.approvals)
            ).all()
            
            analytics = {
                "analytics_period_days": analytics_period_days,
                "analysis_timestamp": analysis_start.isoformat(),
                "summary_statistics": {},
                "trend_analysis": {},
                "risk_analysis": {},
                "performance_metrics": {},
                "entity_type_distribution": {},
                "trust_level_distribution": {},
                "approval_analytics": {}
            }
            
            # Summary statistics
            analytics["summary_statistics"] = {
                "total_entries": len(entries),
                "active_entries": len([e for e in entries if e.status == WhitelistStatus.ACTIVE.value]),
                "pending_entries": len([e for e in entries if e.status == WhitelistStatus.PENDING.value]),
                "suspended_entries": len([e for e in entries if e.status == WhitelistStatus.SUSPENDED.value]),
                "expired_entries": len([e for e in entries if e.status == WhitelistStatus.EXPIRED.value])
            }
            
            # Entity type distribution
            entity_types = {}
            for entry in entries:
                entity_type = entry.entity_type
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            analytics["entity_type_distribution"] = entity_types
            
            # Trust level distribution
            trust_levels = {}
            for entry in entries:
                trust_level = entry.trust_level
                trust_levels[trust_level] = trust_levels.get(trust_level, 0) + 1
            analytics["trust_level_distribution"] = trust_levels
            
            # Approval analytics
            approved_entries = [e for e in entries if e.approved_at]
            if approved_entries:
                approval_times = []
                for entry in approved_entries:
                    if entry.approved_at and entry.created_at:
                        approval_time = (entry.approved_at - entry.created_at).total_seconds() / 3600  # hours
                        approval_times.append(approval_time)
                
                if approval_times:
                    analytics["approval_analytics"] = {
                        "average_approval_time_hours": sum(approval_times) / len(approval_times),
                        "median_approval_time_hours": sorted(approval_times)[len(approval_times) // 2],
                        "fastest_approval_hours": min(approval_times),
                        "slowest_approval_hours": max(approval_times),
                        "auto_approved_count": len([e for e in approved_entries if e.approval_type == ApprovalType.AUTOMATIC.value])
                    }
            
            # Risk analysis
            risk_scores = [e.risk_score for e in entries if e.risk_score is not None]
            if risk_scores:
                analytics["risk_analysis"] = {
                    "average_risk_score": sum(risk_scores) / len(risk_scores),
                    "high_risk_entries": len([s for s in risk_scores if s > 0.7]),
                    "medium_risk_entries": len([s for s in risk_scores if 0.3 <= s <= 0.7]),
                    "low_risk_entries": len([s for s in risk_scores if s < 0.3])
                }
            
            # Trend analysis
            if analytics_period_days >= 7:
                analytics["trend_analysis"] = await self._calculate_whitelist_trends(
                    entries, analytics_period_days
                )
            
            # ML predictions
            if include_predictions and self.ai_risk_assessment_enabled:
                analytics["predictions"] = await self._generate_whitelist_predictions(entries)
            
            logger.info(f"Whitelist analytics generated for {len(entries)} entries over {analytics_period_days} days")
            return analytics
            
        except Exception as e:
            logger.error(f"Whitelist analytics generation failed: {e}")
            raise WhitelistManagerError(f"Whitelist analytics generation failed: {e}")
    
    # Private helper methods
    
    async def _validate_entity_identifier(
        self,
        entity_type: WhitelistType,
        entity_identifier: str
    ) -> None:
        """Validate entity identifier format and uniqueness"""
        if not entity_identifier or len(entity_identifier.strip()) == 0:
            raise WhitelistManagerError("Entity identifier cannot be empty")
        
        # Type-specific validation
        validation_result = await self.whitelist_validator.validate_entity_identifier(
            entity_type, entity_identifier
        )
        
        if not validation_result["valid"]:
            raise WhitelistManagerError(f"Invalid entity identifier: {validation_result['error']}")
    
    async def _get_existing_whitelist_entry(
        self,
        entity_type: WhitelistType,
        entity_identifier: str
    ) -> Optional[WhitelistEntry]:
        """Get existing whitelist entry if it exists"""



        return await self.db_session.query(WhitelistEntry).filter(
            and_(
                WhitelistEntry.entity_type == entity_type.value,
                WhitelistEntry.entity_identifier == entity_identifier
            )
        ).first()
    
    async def _perform_risk_assessment(
        self,
        entity_type: WhitelistType,
        entity_identifier: str,
        entity_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive AI-powered risk assessment"""



        try:
            if not self.ai_risk_assessment_enabled:
                return {
                    "overall_risk_score": 0.5,
                    "risk_categories": {},
                    "trust_factors": {},
                    "assessment_confidence": 0.5
                }
            
            # Prepare assessment data
            assessment_data = {
                "entity_type": entity_type.value,
                "entity_identifier": entity_identifier,
                "metadata": entity_metadata,
                "historical_data": await self._get_historical_data(entity_identifier),
                "context_data": await self._get_context_data(entity_type, entity_identifier)
            }
            
            # Perform AI risk assessment
            risk_result = await self.risk_model.assess_risk(assessment_data)
            
            # Update metrics
            self.whitelist_metrics["risk_assessments_per_hour"] += 1
            
            return risk_result
            
        except Exception as e:
            logger.warning(f"Risk assessment failed, using default values: {e}")
            return {
                "overall_risk_score": 0.5,
                "risk_categories": {},
                "trust_factors": {},
                "assessment_confidence": 0.0,
                "error": str(e)
            }
    
    async def _calculate_trust_score(
        self,
        entity_type: WhitelistType,
        entity_identifier: str,
        entity_metadata: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive trust score"""



        try:
            # Get trust factors from risk assessment
            trust_factors = risk_assessment.get("trust_factors", {})
            
            # Calculate weighted trust score
            trust_score = 0.0
            total_weight = 0.0
            
            for factor, weight in self.trust_factors.items():
                if factor in trust_factors:
                    trust_score += trust_factors[factor] * weight
                    total_weight += weight
                else:
                    # Use neutral score for missing factors
                    trust_score += 0.5 * weight
                    total_weight += weight
            
            # Normalize score
            if total_weight > 0:
                trust_score = trust_score / total_weight
            else:
                trust_score = 0.5  # Default neutral score
            
            # Apply risk adjustment
            overall_risk = risk_assessment.get("overall_risk_score", 0.5)
            trust_score = trust_score * (1.0 - overall_risk * 0.3)  # Reduce trust based on risk
            
            # Ensure score is between 0 and 1
            trust_score = max(0.0, min(1.0, trust_score))
            
            return trust_score
            
        except Exception as e:
            logger.warning(f"Trust score calculation failed, using default: {e}")
            return 0.5  # Default neutral trust score
    
    async def _determine_trust_level(self, trust_score: float) -> TrustLevel:
        """Determine trust level based on trust score"""
        if trust_score >= 0.9:
            return TrustLevel.ENTERPRISE
        elif trust_score >= 0.8:
            return TrustLevel.PREMIUM
        elif trust_score >= 0.7:
            return TrustLevel.VERIFIED
        elif trust_score >= 0.5:
            return TrustLevel.HIGH
        elif trust_score >= 0.3:
            return TrustLevel.MODERATE
        elif trust_score >= 0.1:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNKNOWN
    
    async def _auto_approve_entry(
        self,
        entry: WhitelistEntry,
        risk_assessment: Dict[str, Any]
    ) -> None:
        """Automatically approve low-risk, high-trust entries"""
        entry.status = WhitelistStatus.APPROVED.value
        entry.approved_at = datetime.now(timezone.utc)
        entry.approved_by = "system_auto_approval"
        
        # Create approval record
        approval_record = WhitelistApproval(
            id=uuid4(),
            whitelist_entry_id=entry.id,
            approver_id="system",
            approval_status="auto_approved",
            approval_notes=f"Automatically approved - Trust score: {entry.trust_score:.3f}, Risk score: {entry.risk_score:.3f}",
            conditional_approval=False,
            approved_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        self.db_session.add(approval_record)
        
        # Activate entry
        await self._activate_whitelist_entry(entry)
        
        # Update metrics
        self.whitelist_metrics["automated_approvals"] += 1
    
    async def _activate_whitelist_entry(self, entry: WhitelistEntry) -> None:
        """Activate approved whitelist entry"""
        entry.status = WhitelistStatus.ACTIVE.value
        entry.activated_at = datetime.now(timezone.utc)
        entry.updated_at = datetime.now(timezone.utc)
    
    async def _validate_approver_permissions(
        self,
        approver_id: str,
        entry: WhitelistEntry
    ) -> None:
        """Validate approver has permissions to approve entry"""
        # Implementation would check user permissions
        # For now, assume all approvers are valid
        pass
    
    async def _perform_final_risk_check(
        self,
        entry: WhitelistEntry
    ) -> Dict[str, Any]:
        """Perform final risk check before approval"""



        try:
            # Get latest risk data
            entity_metadata = json.loads(
                await self.encryption_manager.decrypt_data(entry.entity_metadata)
            )
            
            # Perform fresh risk assessment
            current_risk = await self._perform_risk_assessment(
                WhitelistType(entry.entity_type),
                entry.entity_identifier,
                entity_metadata
            )
            
            # Check for high risk indicators
            high_risk = current_risk.get("overall_risk_score", 0) > 0.8
            
            return {
                "high_risk": high_risk,
                "current_risk_score": current_risk.get("overall_risk_score", 0),
                "reasons": current_risk.get("high_risk_reasons", [])
            }
            
        except Exception as e:
            logger.warning(f"Final risk check failed: {e}")
            return {"high_risk": False, "error": str(e)}
    
    async def _get_current_trust_score(self, entry: WhitelistEntry) -> float:
        """Get current trust score (may be recalculated)"""
        # Check if trust score needs recalculation
        if (not entry.trust_score or 
            entry.updated_at < datetime.now(timezone.utc) - timedelta(days=7)):
            
            # Recalculate trust score
            entity_metadata = json.loads(
                await self.encryption_manager.decrypt_data(entry.entity_metadata)
            )
            
            risk_assessment = await self._perform_risk_assessment(
                WhitelistType(entry.entity_type),
                entry.entity_identifier,
                entity_metadata
            )
            
            new_trust_score = await self._calculate_trust_score(
                WhitelistType(entry.entity_type),
                entry.entity_identifier,
                entity_metadata,
                risk_assessment
            )
            
            # Update entry if score changed significantly
            if abs(new_trust_score - (entry.trust_score or 0)) > 0.1:
                entry.trust_score = new_trust_score
                entry.updated_at = datetime.now(timezone.utc)
            
            return new_trust_score
        
        return entry.trust_score or 0.0
    
    async def _perform_real_time_risk_check(
        self,
        entry: WhitelistEntry,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform real-time risk check with current context"""



        try:
            # Combine entry data with current context
            entity_metadata = json.loads(
                await self.encryption_manager.decrypt_data(entry.entity_metadata)
            )
            
            risk_data = {
                "entity_type": entry.entity_type,
                "entity_identifier": entry.entity_identifier,
                "metadata": entity_metadata,
                "current_context": context,
                "trust_score": entry.trust_score,
                "historical_risk": entry.risk_score
            }
            
            # Perform real-time assessment
            risk_result = await self.risk_model.assess_real_time_risk(risk_data)
            
            return risk_result
            
        except Exception as e:
            logger.warning(f"Real-time risk check failed: {e}")
            return {"risk_score": entry.risk_score or 0.5, "error": str(e)}
    
    async def _temporarily_suspend_entry(
        self,
        entry: WhitelistEntry,
        risk_info: Dict[str, Any]
    ) -> None:
        """Temporarily suspend entry due to high risk"""
        entry.status = WhitelistStatus.SUSPENDED.value
        entry.suspended_at = datetime.now(timezone.utc)
        entry.suspension_reason = f"High real-time risk detected: {risk_info.get('risk_score', 'unknown')}"
        entry.updated_at = datetime.now(timezone.utc)
        
        logger.warning(f"Whitelist entry temporarily suspended: {entry.entity_identifier} due to high risk")
    
    async def _handle_expired_entry(self, entry: WhitelistEntry) -> None:
        """Handle expired whitelist entry"""
        entry.status = WhitelistStatus.EXPIRED.value
        entry.updated_at = datetime.now(timezone.utc)
        
        # Update metrics
        if entry.status == WhitelistStatus.ACTIVE.value:
            self.whitelist_metrics["active_entries"] -= 1
    
    async def _process_batch_operation(
        self,
        operation: str,
        batch: List[Dict[str, Any]],
        requester_id: str,
        operation_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process batch of whitelist operations"""
        batch_results = {
            "successful": 0,
            "failed": 0,
            "results": [],
            "errors": []
        }
        
        for entity_data in batch:
            try:
                if operation == "add":
                    result = await self.add_to_whitelist(
                        entity_type=WhitelistType(entity_data["entity_type"]),
                        entity_identifier=entity_data["entity_identifier"],
                        entity_metadata=entity_data.get("entity_metadata", {}),
                        requester_id=requester_id,
                        approval_type=ApprovalType(entity_data.get("approval_type", "manual")),
                        expiration_date=entity_data.get("expiration_date")
                    )
                    
                    batch_results["results"].append({
                        "entity_identifier": entity_data["entity_identifier"],
                        "status": "success",
                        "entry_id": str(result.id)
                    })
                    
                elif operation == "approve":
                    result = await self.approve_whitelist_entry(
                        entry_id=UUID(entity_data["entry_id"]),
                        approver_id=requester_id,
                        approval_notes=entity_data.get("approval_notes")
                    )
                    
                    batch_results["results"].append({
                        "entry_id": entity_data["entry_id"],
                        "status": "success",
                        "approved_status": result.status
                    })
                
                batch_results["successful"] += 1
                
            except Exception as e:
                batch_results["failed"] += 1
                batch_results["errors"].append({
                    "entity_data": entity_data,
                    "error": str(e)
                })
        
        return batch_results
    
    async def _calculate_average_approval_time(self) -> float:
        """Calculate average approval time in hours"""



        try:
            # Get recent approvals
            recent_approvals = await self.db_session.query(WhitelistEntry).filter(
                and_(
                    WhitelistEntry.approved_at.isnot(None),
                    WhitelistEntry.approved_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            ).all()
            
            if not recent_approvals:
                return 0.0
            
            approval_times = []
            for entry in recent_approvals:
                if entry.approved_at and entry.created_at:
                    approval_time = (entry.approved_at - entry.created_at).total_seconds() / 3600
                    approval_times.append(approval_time)
            
            return sum(approval_times) / len(approval_times) if approval_times else 0.0
            
        except Exception as e:
            logger.warning(f"Average approval time calculation failed: {e}")
            return 0.0
    
    async def _generate_ai_optimization_recommendations(
        self,
        entries: List[WhitelistEntry]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered optimization recommendations"""



        try:
            # Prepare data for AI analysis
            analysis_data = []
            for entry in entries:
                try:
                    entity_metadata = json.loads(
                        await self.encryption_manager.decrypt_data(entry.entity_metadata)
                    )
                    
                    analysis_data.append({
                        "entry_id": str(entry.id),
                        "entity_type": entry.entity_type,
                        "entity_identifier": entry.entity_identifier,
                        "status": entry.status,
                        "trust_score": entry.trust_score,
                        "risk_score": entry.risk_score,
                        "metadata": entity_metadata,
                        "created_at": entry.created_at.isoformat(),
                        "updated_at": entry.updated_at.isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Failed to prepare entry data for AI analysis: {e}")
            
            # Generate AI recommendations
            ai_recommendations = await self.risk_model.generate_optimization_recommendations(
                analysis_data
            )
            
            return ai_recommendations.get("recommendations", [])
            
        except Exception as e:
            logger.warning(f"AI optimization recommendations failed: {e}")
            return []
    
    async def _calculate_whitelist_trends(
        self,
        entries: List[WhitelistEntry],
        period_days: int
    ) -> Dict[str, Any]:
        """Calculate whitelist trends over time"""



        try:
            # Group entries by day
            daily_stats = {}
            
            for entry in entries:
                day_key = entry.created_at.date().isoformat()
                if day_key not in daily_stats:
                    daily_stats[day_key] = {
                        "new_entries": 0,
                        "approvals": 0,
                        "activations": 0
                    }
                
                daily_stats[day_key]["new_entries"] += 1
                
                if entry.approved_at and entry.approved_at.date().isoformat() == day_key:
                    daily_stats[day_key]["approvals"] += 1
                
                if (hasattr(entry, 'activated_at') and entry.activated_at and 
                    entry.activated_at.date().isoformat() == day_key):
                    daily_stats[day_key]["activations"] += 1
            
            # Calculate trends
            total_entries = sum(stats["new_entries"] for stats in daily_stats.values())
            avg_daily_entries = total_entries / period_days if period_days > 0 else 0
            
            return {
                "daily_statistics": daily_stats,
                "average_daily_entries": avg_daily_entries,
                "total_period_entries": total_entries,
                "trend_direction": "stable"  # Could be enhanced with actual trend calculation
            }
            
        except Exception as e:
            logger.warning(f"Trend calculation failed: {e}")
            return {}
    
    async def _generate_whitelist_predictions(
        self,
        entries: List[WhitelistEntry]
    ) -> Dict[str, Any]:
        """Generate ML predictions for whitelist management"""



        try:
            # Prepare prediction data
            prediction_data = {
                "current_entries": len(entries),
                "active_entries": len([e for e in entries if e.status == WhitelistStatus.ACTIVE.value]),
                "pending_entries": len([e for e in entries if e.status == WhitelistStatus.PENDING.value]),
                "average_trust_score": sum(e.trust_score for e in entries if e.trust_score) / len([e for e in entries if e.trust_score]) if entries else 0,
                "entity_types": [e.entity_type for e in entries]
            }
            
            # Generate predictions using AI model
            predictions = await self.risk_model.generate_predictions(prediction_data)
            
            return predictions
            
        except Exception as e:
            logger.warning(f"Whitelist predictions failed: {e}")
            return {}
    
    async def _get_historical_data(self, entity_identifier: str) -> Dict[str, Any]:
        """Get historical data for entity"""
        # Implementation would gather historical violation, content, and behavior data
        return {"placeholder": "historical_data"}
    
    async def _get_context_data(
        self,
        entity_type: WhitelistType,
        entity_identifier: str
    ) -> Dict[str, Any]:
        """Get context data for entity assessment"""
        # Implementation would gather contextual data from various sources
        return {"placeholder": "context_data"}
    
    def _clear_whitelist_cache(self) -> None:
        """Clear whitelist cache to force refresh"""
        self.whitelist_cache.clear()
        self.trust_scores_cache.clear()
        logger.debug("Whitelist cache cleared")
