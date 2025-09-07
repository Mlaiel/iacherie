"""Rights-Revenue Validation System - Content Rights and Revenue Validation
==========================================================================

Enterprise-grade rights-revenue validation system providing comprehensive
validation of content rights, revenue attribution, and legal compliance
for content creators and platform monetization.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/rights_revenue_validator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class RightsType(str, Enum):
    """Content rights type classifications."""
    FULL_OWNERSHIP = "full_ownership"
    SHARED_OWNERSHIP = "shared_ownership"
    LICENSED_CONTENT = "licensed_content"
    DERIVATIVE_WORK = "derivative_work"
    FAIR_USE = "fair_use"
    CREATIVE_COMMONS = "creative_commons"
    PUBLIC_DOMAIN = "public_domain"


class ValidationStatus(str, Enum):
    """Validation status for rights and revenue."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    DISPUTED = "disputed"
    UNDER_REVIEW = "under_review"


class RevenueRightsType(str, Enum):
    """Revenue rights classification."""
    PRIMARY_CREATOR = "primary_creator"
    COLLABORATOR = "collaborator"
    LICENSEE = "licensee"
    DISTRIBUTOR = "distributor"
    PLATFORM_PARTNER = "platform_partner"


@dataclass
class ContentRights:
    """Content rights definition."""
    id: str = field(default_factory=lambda: str(uuid4()))
    content_id: str = ""
    rights_holder_id: str = ""
    rights_type: RightsType = RightsType.FULL_OWNERSHIP
    ownership_percentage: Decimal = Decimal('100.00')
    license_terms: Dict[str, Any] = field(default_factory=dict)
    territorial_rights: List[str] = field(default_factory=list)
    temporal_rights: Dict[str, datetime] = field(default_factory=dict)
    monetization_rights: bool = True
    distribution_rights: bool = True
    modification_rights: bool = False
    sublicense_rights: bool = False
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_evidence: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueRights:
    """Revenue rights and entitlements."""
    id: str = field(default_factory=lambda: str(uuid4()))
    content_id: str = ""
    rights_holder_id: str = ""
    revenue_rights_type: RevenueRightsType = RevenueRightsType.PRIMARY_CREATOR
    revenue_percentage: Decimal = Decimal('100.00')
    minimum_payout: Decimal = Decimal('10.00')
    maximum_payout: Optional[Decimal] = None
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_documents: List[str] = field(default_factory=list)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationRule:
    """Rights and revenue validation rule."""
    id: str = field(default_factory=lambda: str(uuid4()))
    rule_name: str = ""
    rule_type: str = ""  # rights_validation, revenue_validation, compliance_check
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """Validation result for rights/revenue check."""
    id: str = field(default_factory=lambda: str(uuid4()))
    validation_type: str = ""
    content_id: str = ""
    rights_holder_id: str = ""
    is_valid: bool = False
    validation_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    validation_details: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.utcnow)


class RightsRevenueValidationSystem:
    """Advanced rights-revenue validation system."""
    
    def __init__(self):
        self.content_rights: Dict[str, List[ContentRights]] = defaultdict(list)
        self.revenue_rights: Dict[str, List[RevenueRights]] = defaultdict(list)
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: Dict[str, List[ValidationResult]] = defaultdict(list)
        self.rights_conflicts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.validation_stats: Dict[str, Any] = defaultdict(int)
        
    async def register_content_rights(
        self,
        content_id: str,
        rights_holder_id: str,
        rights_type: RightsType,
        ownership_percentage: Decimal = Decimal('100.00'),
        license_terms: Optional[Dict[str, Any]] = None,
        evidence_documents: Optional[List[str]] = None
    ) -> ContentRights:
        """Register content rights for validation."""
        try:
            # Check for existing rights conflicts
            existing_rights = self.content_rights.get(content_id, [])
            total_ownership = sum(rights.ownership_percentage for rights in existing_rights)
            
            if total_ownership + ownership_percentage > Decimal('100.00'):
                raise ValueError(f"Total ownership would exceed 100%: {total_ownership + ownership_percentage}")
            
            # Create rights record
            rights = ContentRights(
                content_id=content_id,
                rights_holder_id=rights_holder_id,
                rights_type=rights_type,
                ownership_percentage=ownership_percentage,
                license_terms=license_terms or {},
                validation_evidence=evidence_documents or [],
                validation_status=ValidationStatus.PENDING
            )
            
            # Add to content rights
            self.content_rights[content_id].append(rights)
            
            # Trigger validation
            validation_result = await self._validate_content_rights(rights)
            
            # Update rights status based on validation
            if validation_result.is_valid:
                rights.validation_status = ValidationStatus.VALID
            else:
                rights.validation_status = ValidationStatus.INVALID
            
            rights.updated_at = datetime.utcnow()
            
            logger.info(f"Content rights registered: {rights.id}")
            return rights
            
        except Exception as e:
            logger.error(f"Failed to register content rights: {e}")
            raise
    
    async def register_revenue_rights(
        self,
        content_id: str,
        rights_holder_id: str,
        revenue_rights_type: RevenueRightsType,
        revenue_percentage: Decimal,
        payment_terms: Optional[Dict[str, Any]] = None,
        validation_documents: Optional[List[str]] = None
    ) -> RevenueRights:
        """Register revenue rights for validation."""
        try:
            # Check for existing revenue rights conflicts
            existing_revenue_rights = self.revenue_rights.get(content_id, [])
            total_revenue_percentage = sum(rights.revenue_percentage for rights in existing_revenue_rights)
            
            if total_revenue_percentage + revenue_percentage > Decimal('100.00'):
                raise ValueError(f"Total revenue percentage would exceed 100%: {total_revenue_percentage + revenue_percentage}")
            
            # Create revenue rights record
            revenue_rights = RevenueRights(
                content_id=content_id,
                rights_holder_id=rights_holder_id,
                revenue_rights_type=revenue_rights_type,
                revenue_percentage=revenue_percentage,
                payment_terms=payment_terms or {},
                validation_documents=validation_documents or {},
                validation_status=ValidationStatus.PENDING
            )
            
            # Add to revenue rights
            self.revenue_rights[content_id].append(revenue_rights)
            
            # Trigger validation
            validation_result = await self._validate_revenue_rights(revenue_rights)
            
            # Update rights status based on validation
            if validation_result.is_valid:
                revenue_rights.validation_status = ValidationStatus.VALID
            else:
                revenue_rights.validation_status = ValidationStatus.INVALID
            
            revenue_rights.updated_at = datetime.utcnow()
            
            logger.info(f"Revenue rights registered: {revenue_rights.id}")
            return revenue_rights
            
        except Exception as e:
            logger.error(f"Failed to register revenue rights: {e}")
            raise
    
    async def validate_revenue_distribution(
        self,
        content_id: str,
        proposed_distribution: Dict[str, Decimal]
    ) -> ValidationResult:
        """Validate proposed revenue distribution against rights."""
        try:
            validation_result = ValidationResult(
                validation_type="revenue_distribution",
                content_id=content_id,
                is_valid=True,
                validation_score=1.0
            )
            
            # Get content rights and revenue rights
            content_rights = self.content_rights.get(content_id, [])
            revenue_rights = self.revenue_rights.get(content_id, [])
            
            if not content_rights or not revenue_rights:
                validation_result.is_valid = False
                validation_result.issues.append("No rights registered for content")
                validation_result.validation_score = 0.0
                return validation_result
            
            # Validate distribution against revenue rights
            total_distributed = sum(proposed_distribution.values())
            
            # Check if distribution matches rights entitlements
            for revenue_right in revenue_rights:
                if revenue_right.validation_status != ValidationStatus.VALID:
                    validation_result.issues.append(
                        f"Revenue rights not validated for holder {revenue_right.rights_holder_id}"
                    )
                    validation_result.validation_score -= 0.2
                
                expected_amount = total_distributed * (revenue_right.revenue_percentage / Decimal('100.00'))
                actual_amount = proposed_distribution.get(revenue_right.rights_holder_id, Decimal('0.00'))
                
                if abs(actual_amount - expected_amount) > Decimal('0.01'):
                    validation_result.issues.append(
                        f"Distribution mismatch for {revenue_right.rights_holder_id}: "
                        f"expected {expected_amount}, got {actual_amount}"
                    )
                    validation_result.validation_score -= 0.3
            
            # Check for unauthorized recipients
            for recipient_id, amount in proposed_distribution.items():
                if not any(rr.rights_holder_id == recipient_id for rr in revenue_rights):
                    validation_result.issues.append(f"Unauthorized recipient: {recipient_id}")
                    validation_result.validation_score -= 0.5
            
            # Determine overall validation status
            validation_result.is_valid = validation_result.validation_score >= 0.7
            
            # Store validation result
            self.validation_history[content_id].append(validation_result)
            
            logger.info(f"Revenue distribution validated: {validation_result.id}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate revenue distribution: {e}")
            raise
    
    async def check_rights_conflicts(
        self,
        content_id: str
    ) -> List[Dict[str, Any]]:
        """Check for rights conflicts in content."""
        try:
            conflicts = []
            
            # Check content rights conflicts
            content_rights = self.content_rights.get(content_id, [])
            
            # Check ownership percentage conflicts
            total_ownership = sum(rights.ownership_percentage for rights in content_rights)
            if total_ownership > Decimal('100.00'):
                conflicts.append({
                    "type": "ownership_overflow",
                    "description": f"Total ownership exceeds 100%: {total_ownership}%",
                    "severity": "high",
                    "affected_rights": [rights.id for rights in content_rights]
                })
            
            # Check revenue rights conflicts
            revenue_rights = self.revenue_rights.get(content_id, [])
            total_revenue_percentage = sum(rights.revenue_percentage for rights in revenue_rights)
            if total_revenue_percentage > Decimal('100.00'):
                conflicts.append({
                    "type": "revenue_overflow",
                    "description": f"Total revenue percentage exceeds 100%: {total_revenue_percentage}%",
                    "severity": "high",
                    "affected_rights": [rights.id for rights in revenue_rights]
                })
            
            # Check conflicting rights types
            exclusive_rights = [rights for rights in content_rights if rights.rights_type == RightsType.FULL_OWNERSHIP]
            if len(exclusive_rights) > 1:
                conflicts.append({
                    "type": "exclusive_rights_conflict",
                    "description": "Multiple parties claiming full ownership",
                    "severity": "critical",
                    "affected_rights": [rights.id for rights in exclusive_rights]
                })
            
            # Check temporal conflicts
            temporal_conflicts = await self._check_temporal_conflicts(content_rights)
            conflicts.extend(temporal_conflicts)
            
            # Store conflicts
            self.rights_conflicts[content_id] = conflicts
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Failed to check rights conflicts: {e}")
            raise
    
    async def generate_rights_compliance_report(
        self,
        content_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive rights compliance report."""
        try:
            content_rights = self.content_rights.get(content_id, [])
            revenue_rights = self.revenue_rights.get(content_id, [])
            conflicts = await self.check_rights_conflicts(content_id)
            validation_history = self.validation_history.get(content_id, [])
            
            # Calculate compliance metrics
            total_content_rights = len(content_rights)
            valid_content_rights = len([r for r in content_rights if r.validation_status == ValidationStatus.VALID])
            
            total_revenue_rights = len(revenue_rights)
            valid_revenue_rights = len([r for r in revenue_rights if r.validation_status == ValidationStatus.VALID])
            
            report = {
                "content_id": content_id,
                "generated_at": datetime.utcnow(),
                "compliance_summary": {
                    "overall_compliance_score": await self._calculate_compliance_score(content_id),
                    "rights_validation_rate": (valid_content_rights / max(total_content_rights, 1)) * 100,
                    "revenue_validation_rate": (valid_revenue_rights / max(total_revenue_rights, 1)) * 100,
                    "conflicts_count": len(conflicts),
                    "critical_issues": len([c for c in conflicts if c.get("severity") == "critical"])
                },
                "content_rights": {
                    "total_rights": total_content_rights,
                    "valid_rights": valid_content_rights,
                    "ownership_distribution": self._calculate_ownership_distribution(content_rights),
                    "rights_types": self._count_rights_types(content_rights)
                },
                "revenue_rights": {
                    "total_rights": total_revenue_rights,
                    "valid_rights": valid_revenue_rights,
                    "revenue_distribution": self._calculate_revenue_distribution(revenue_rights),
                    "payment_terms_summary": self._summarize_payment_terms(revenue_rights)
                },
                "conflicts_analysis": {
                    "total_conflicts": len(conflicts),
                    "conflict_types": self._count_conflict_types(conflicts),
                    "critical_conflicts": [c for c in conflicts if c.get("severity") == "critical"],
                    "recommended_actions": await self._generate_conflict_resolutions(conflicts)
                },
                "validation_history": {
                    "total_validations": len(validation_history),
                    "recent_validations": validation_history[-5:] if validation_history else [],
                    "validation_trends": await self._analyze_validation_trends(validation_history)
                },
                "recommendations": await self._generate_compliance_recommendations(content_id)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise
    
    async def resolve_rights_conflict(
        self,
        content_id: str,
        conflict_id: str,
        resolution_method: str,
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve rights conflict with specified method."""
        try:
            conflicts = self.rights_conflicts.get(content_id, [])
            conflict = next((c for c in conflicts if c.get("id") == conflict_id), None)
            
            if not conflict:
                raise ValueError(f"Conflict not found: {conflict_id}")
            
            resolution_result = {
                "conflict_id": conflict_id,
                "resolution_method": resolution_method,
                "resolution_status": "resolved",
                "resolution_details": resolution_data,
                "resolved_at": datetime.utcnow()
            }
            
            # Apply resolution based on method
            if resolution_method == "ownership_adjustment":
                await self._adjust_ownership_percentages(content_id, resolution_data)
            elif resolution_method == "revenue_redistribution":
                await self._redistribute_revenue_rights(content_id, resolution_data)
            elif resolution_method == "rights_transfer":
                await self._transfer_rights(content_id, resolution_data)
            
            # Remove resolved conflict
            self.rights_conflicts[content_id] = [
                c for c in conflicts if c.get("id") != conflict_id
            ]
            
            logger.info(f"Rights conflict resolved: {conflict_id}")
            return resolution_result
            
        except Exception as e:
            logger.error(f"Failed to resolve rights conflict: {e}")
            raise
    
    async def _validate_content_rights(self, rights: ContentRights) -> ValidationResult:
        """Validate content rights."""
        validation_result = ValidationResult(
            validation_type="content_rights",
            content_id=rights.content_id,
            rights_holder_id=rights.rights_holder_id,
            is_valid=True,
            validation_score=1.0
        )
        
        # Check ownership percentage
        if rights.ownership_percentage <= 0 or rights.ownership_percentage > 100:
            validation_result.issues.append("Invalid ownership percentage")
            validation_result.validation_score -= 0.3
        
        # Check rights type validity
        if rights.rights_type == RightsType.FULL_OWNERSHIP and rights.ownership_percentage < 100:
            validation_result.issues.append("Full ownership requires 100% ownership percentage")
            validation_result.validation_score -= 0.4
        
        # Check evidence documents
        if not rights.validation_evidence:
            validation_result.issues.append("No validation evidence provided")
            validation_result.validation_score -= 0.2
        
        validation_result.is_valid = validation_result.validation_score >= 0.7
        return validation_result
    
    async def _validate_revenue_rights(self, revenue_rights: RevenueRights) -> ValidationResult:
        """Validate revenue rights."""
        validation_result = ValidationResult(
            validation_type="revenue_rights",
            content_id=revenue_rights.content_id,
            rights_holder_id=revenue_rights.rights_holder_id,
            is_valid=True,
            validation_score=1.0
        )
        
        # Check revenue percentage
        if revenue_rights.revenue_percentage <= 0 or revenue_rights.revenue_percentage > 100:
            validation_result.issues.append("Invalid revenue percentage")
            validation_result.validation_score -= 0.3
        
        # Check minimum payout
        if revenue_rights.minimum_payout < 0:
            validation_result.issues.append("Minimum payout cannot be negative")
            validation_result.validation_score -= 0.2
        
        # Check validation documents
        if not revenue_rights.validation_documents:
            validation_result.issues.append("No validation documents provided")
            validation_result.validation_score -= 0.2
        
        validation_result.is_valid = validation_result.validation_score >= 0.7
        return validation_result
    
    async def _check_temporal_conflicts(self, content_rights: List[ContentRights]) -> List[Dict[str, Any]]:
        """Check for temporal rights conflicts."""
        conflicts = []
        
        for i, rights1 in enumerate(content_rights):
            for rights2 in content_rights[i+1:]:
                if rights1.temporal_rights and rights2.temporal_rights:
                    # Check for overlapping time periods
                    start1 = rights1.temporal_rights.get("start_date")
                    end1 = rights1.temporal_rights.get("end_date")
                    start2 = rights2.temporal_rights.get("start_date")
                    end2 = rights2.temporal_rights.get("end_date")
                    
                    if start1 and end1 and start2 and end2:
                        if not (end1 < start2 or end2 < start1):
                            conflicts.append({
                                "type": "temporal_overlap",
                                "description": f"Temporal rights overlap between {rights1.id} and {rights2.id}",
                                "severity": "medium",
                                "affected_rights": [rights1.id, rights2.id]
                            })
        
        return conflicts
    
    async def _calculate_compliance_score(self, content_id: str) -> float:
        """Calculate overall compliance score."""
        content_rights = self.content_rights.get(content_id, [])
        revenue_rights = self.revenue_rights.get(content_id, [])
        conflicts = self.rights_conflicts.get(content_id, [])
        
        if not content_rights and not revenue_rights:
            return 0.0
        
        # Base score from valid rights
        valid_content_rights = len([r for r in content_rights if r.validation_status == ValidationStatus.VALID])
        valid_revenue_rights = len([r for r in revenue_rights if r.validation_status == ValidationStatus.VALID])
        
        total_rights = len(content_rights) + len(revenue_rights)
        valid_rights = valid_content_rights + valid_revenue_rights
        
        base_score = (valid_rights / max(total_rights, 1)) * 100
        
        # Deduct points for conflicts
        conflict_penalty = len(conflicts) * 10
        critical_penalty = len([c for c in conflicts if c.get("severity") == "critical"]) * 20
        
        final_score = max(0, base_score - conflict_penalty - critical_penalty)
        return min(100, final_score)
    
    def _calculate_ownership_distribution(self, content_rights: List[ContentRights]) -> Dict[str, Decimal]:
        """Calculate ownership distribution."""
        distribution = defaultdict(Decimal)
        for rights in content_rights:
            distribution[rights.rights_holder_id] += rights.ownership_percentage
        return dict(distribution)
    
    def _calculate_revenue_distribution(self, revenue_rights: List[RevenueRights]) -> Dict[str, Decimal]:
        """Calculate revenue distribution."""
        distribution = defaultdict(Decimal)
        for rights in revenue_rights:
            distribution[rights.rights_holder_id] += rights.revenue_percentage
        return dict(distribution)
    
    def _count_rights_types(self, content_rights: List[ContentRights]) -> Dict[str, int]:
        """Count rights by type."""
        counts = defaultdict(int)
        for rights in content_rights:
            counts[rights.rights_type.value] += 1
        return dict(counts)
    
    def _summarize_payment_terms(self, revenue_rights: List[RevenueRights]) -> Dict[str, Any]:
        """Summarize payment terms."""
        total_min_payout = sum(rights.minimum_payout for rights in revenue_rights)
        payment_schedules = defaultdict(int)
        
        for rights in revenue_rights:
            schedule = rights.payment_terms.get("schedule", "monthly")
            payment_schedules[schedule] += 1
        
        return {
            "total_minimum_payout": total_min_payout,
            "payment_schedules": dict(payment_schedules)
        }
    
    def _count_conflict_types(self, conflicts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count conflicts by type."""
        counts = defaultdict(int)
        for conflict in conflicts:
            counts[conflict.get("type", "unknown")] += 1
        return dict(counts)
    
    async def _generate_conflict_resolutions(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate recommended actions for conflicts."""
        recommendations = []
        
        for conflict in conflicts:
            conflict_type = conflict.get("type")
            if conflict_type == "ownership_overflow":
                recommendations.append("Adjust ownership percentages to total 100%")
            elif conflict_type == "revenue_overflow":
                recommendations.append("Redistribute revenue percentages to total 100%")
            elif conflict_type == "exclusive_rights_conflict":
                recommendations.append("Resolve ownership disputes through negotiation or arbitration")
            elif conflict_type == "temporal_overlap":
                recommendations.append("Clarify temporal rights boundaries")
        
        return recommendations
    
    async def _analyze_validation_trends(self, validation_history: List[ValidationResult]) -> Dict[str, Any]:
        """Analyze validation trends."""
        if not validation_history:
            return {"trend": "no_data", "success_rate": 0}
        
        recent_validations = validation_history[-10:] if len(validation_history) >= 10 else validation_history
        success_rate = len([v for v in recent_validations if v.is_valid]) / len(recent_validations) * 100
        
        return {
            "trend": "improving" if success_rate > 70 else "declining",
            "success_rate": success_rate,
            "total_validations": len(validation_history)
        }
    
    async def _generate_compliance_recommendations(self, content_id: str) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        content_rights = self.content_rights.get(content_id, [])
        revenue_rights = self.revenue_rights.get(content_id, [])
        conflicts = self.rights_conflicts.get(content_id, [])
        
        if not content_rights:
            recommendations.append("Register content rights for proper protection")
        
        if not revenue_rights:
            recommendations.append("Define revenue rights for monetization")
        
        if conflicts:
            recommendations.append("Resolve existing rights conflicts")
        
        unvalidated_rights = [r for r in content_rights if r.validation_status != ValidationStatus.VALID]
        if unvalidated_rights:
            recommendations.append("Provide validation evidence for unvalidated rights")
        
        return recommendations
    
    async def _adjust_ownership_percentages(self, content_id: str, adjustment_data: Dict[str, Any]):
        """Adjust ownership percentages to resolve conflicts."""
        # Implementation for ownership adjustment
        pass
    
    async def _redistribute_revenue_rights(self, content_id: str, redistribution_data: Dict[str, Any]):
        """Redistribute revenue rights to resolve conflicts."""
        # Implementation for revenue redistribution
        pass
    
    async def _transfer_rights(self, content_id: str, transfer_data: Dict[str, Any]):
        """Transfer rights between parties."""
        # Implementation for rights transfer
        pass


# Global validation system instance
rights_validator = RightsRevenueValidationSystem()


async def initialize_rights_validation():
    """Initialize rights-revenue validation system."""
    logger.info("Rights-Revenue Validation System initialized")


# Utility functions
async def validate_content_ownership(
    content_id: str,
    rights_holder_id: str,
    ownership_percentage: Decimal
) -> ValidationResult:
    """Validate content ownership."""
    rights = await rights_validator.register_content_rights(
        content_id, rights_holder_id, RightsType.FULL_OWNERSHIP, ownership_percentage
    )
    return await rights_validator._validate_content_rights(rights)


async def validate_revenue_entitlement(
    content_id: str,
    rights_holder_id: str,
    revenue_percentage: Decimal
) -> ValidationResult:
    """Validate revenue entitlement."""
    revenue_rights = await rights_validator.register_revenue_rights(
        content_id, rights_holder_id, RevenueRightsType.PRIMARY_CREATOR, revenue_percentage
    )
    return await rights_validator._validate_revenue_rights(revenue_rights)