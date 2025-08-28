"""
Rights Validator - Content Rights Validation System
==================================================

Advanced rights validation system for content licensing with comprehensive
rights checking, ownership verification, and compliance validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class RightType(Enum):
    """Types of content rights"""
    COPYRIGHT = "copyright"
    LICENSING = "licensing"
    DISTRIBUTION = "distribution"
    COMMERCIAL = "commercial"
    SYNCHRONIZATION = "synchronization"
    PUBLIC_PERFORMANCE = "public_performance"
    MECHANICAL = "mechanical"
    DIGITAL = "digital"
    BROADCAST = "broadcast"
    STREAMING = "streaming"


class RightStatus(Enum):
    """Status of rights"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    PENDING = "pending"
    DISPUTED = "disputed"
    REVOKED = "revoked"


class ValidationResult(Enum):
    """Results of rights validation"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    INSUFFICIENT_RIGHTS = "insufficient_rights"
    CONFLICTING_CLAIMS = "conflicting_claims"


@dataclass
class ContentRight:
    """Individual content right"""
    right_id: str
    content_id: int
    owner_id: int
    right_type: RightType
    status: RightStatus
    granted_date: datetime
    expiry_date: Optional[datetime] = None
    territory: str = "worldwide"
    exclusivity: bool = False
    transferable: bool = True
    sublicensable: bool = False
    restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RightsChain:
    """Chain of rights for content"""
    content_id: int
    original_owner: int
    current_owner: int
    rights_history: List[ContentRight]
    active_rights: List[ContentRight]
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    last_verified: Optional[datetime] = None


@dataclass
class ValidationRequest:
    """Rights validation request"""
    request_id: str
    content_id: int
    requester_id: int
    requested_rights: List[RightType]
    intended_use: Dict[str, Any]
    territory: str = "worldwide"
    duration: Optional[int] = None  # days
    commercial: bool = False
    exclusive: bool = False
    submitted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationReport:
    """Rights validation report"""
    request_id: str
    content_id: int
    result: ValidationResult
    validated_rights: List[RightType]
    denied_rights: List[RightType]
    issues: List[str]
    recommendations: List[str]
    expiry_warnings: List[str]
    conflicts: List[Dict[str, Any]]
    validation_date: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


class RightsValidator:
    """
    Advanced rights validation system
    
    Features:
    - Comprehensive rights checking
    - Ownership verification
    - Territory restrictions
    - Exclusivity conflicts detection
    - Rights chain validation
    - Automated compliance checking
    - Third-party verification
    - Historical rights tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize rights validator"""
        self.config = config or {}
        
        # Rights storage
        self.content_rights: Dict[int, RightsChain] = {}  # content_id -> RightsChain
        self.validation_requests: Dict[str, ValidationRequest] = {}
        self.validation_reports: Dict[str, ValidationReport] = {}
        
        # Rights databases and registries
        self.copyright_registry = {}  # Mock copyright registry
        self.licensing_registry = {}  # Mock licensing registry
        self.third_party_verifiers = []  # External verification services
        
        # Validation rules
        self.validation_rules = {
            "minimum_ownership_period": 30,  # days
            "require_original_ownership_proof": True,
            "allow_sublicensing": False,
            "territory_restrictions_enabled": True,
            "exclusive_rights_conflicts_check": True,
            "automated_expiry_warnings": True
        }
        
        # Rights hierarchy (higher level rights include lower level)
        self.rights_hierarchy = {
            RightType.COPYRIGHT: [
                RightType.LICENSING, RightType.DISTRIBUTION, RightType.COMMERCIAL,
                RightType.SYNCHRONIZATION, RightType.PUBLIC_PERFORMANCE,
                RightType.MECHANICAL, RightType.DIGITAL, RightType.BROADCAST, RightType.STREAMING
            ],
            RightType.LICENSING: [
                RightType.DISTRIBUTION, RightType.COMMERCIAL
            ],
            RightType.DISTRIBUTION: [
                RightType.DIGITAL, RightType.STREAMING
            ]
        }
        
        # Performance metrics
        self.metrics = {
            "total_validations": 0,
            "approved_validations": 0,
            "rejected_validations": 0,
            "conflicts_detected": 0,
            "average_validation_time": 0.0
        }
        
        logger.info("RightsValidator initialized successfully")
    
    async def validate_licensing_rights(
        self,
        content_id: int,
        requester_id: int,
        requested_rights: Optional[List[str]] = None,
        intended_use: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Quick validation for licensing rights
        
        Args:
            content_id: Content ID to validate
            requester_id: ID of user requesting rights
            requested_rights: List of rights being requested
            intended_use: Description of intended use
            
        Returns:
            bool: True if licensing rights are valid
        """
        try:
            # Create validation request
            request = ValidationRequest(
                request_id=f"quick_val_{content_id}_{datetime.utcnow().timestamp()}",
                content_id=content_id,
                requester_id=requester_id,
                requested_rights=[RightType.LICENSING],
                intended_use=intended_use or {},
                territory="worldwide",
                commercial=intended_use.get("commercial", False) if intended_use else False
            )
            
            # Perform full validation
            report = await self.validate_rights(request)
            
            # Return simple boolean result
            return report.result == ValidationResult.APPROVED
            
        except Exception as e:
            logger.error(f"Error in quick licensing validation: {e}")
            return False
    
    async def validate_rights(self, request: ValidationRequest) -> ValidationReport:
        """
        Comprehensive rights validation
        
        Args:
            request: Validation request with all parameters
            
        Returns:
            ValidationReport: Detailed validation report
        """
        start_time = datetime.utcnow()
        
        try:
            # Store validation request
            self.validation_requests[request.request_id] = request
            
            # Initialize validation report
            report = ValidationReport(
                request_id=request.request_id,
                content_id=request.content_id,
                result=ValidationResult.REQUIRES_REVIEW,
                validated_rights=[],
                denied_rights=[],
                issues=[],
                recommendations=[],
                expiry_warnings=[],
                conflicts=[]
            )
            
            # Get or create rights chain for content
            rights_chain = await self._get_or_create_rights_chain(request.content_id)
            
            # Verify ownership
            ownership_valid = await self._verify_ownership(
                request.content_id, request.requester_id, rights_chain
            )
            
            if not ownership_valid:
                report.result = ValidationResult.INSUFFICIENT_RIGHTS
                report.issues.append("Insufficient ownership rights")
                return report
            
            # Validate each requested right
            for right_type in request.requested_rights:
                validation_result = await self._validate_individual_right(
                    request, right_type, rights_chain
                )
                
                if validation_result["valid"]:
                    report.validated_rights.append(right_type)
                else:
                    report.denied_rights.append(right_type)
                    report.issues.extend(validation_result["issues"])
                
                # Add warnings
                report.expiry_warnings.extend(validation_result.get("warnings", []))
            
            # Check for conflicts
            conflicts = await self._check_rights_conflicts(request, rights_chain)
            report.conflicts = conflicts
            
            if conflicts:
                report.issues.append(f"Found {len(conflicts)} rights conflicts")
                report.result = ValidationResult.CONFLICTING_CLAIMS
            
            # Territory validation
            territory_valid = await self._validate_territory(request, rights_chain)
            if not territory_valid:
                report.issues.append(f"Rights not valid for territory: {request.territory}")
            
            # Commercial use validation
            if request.commercial:
                commercial_valid = await self._validate_commercial_rights(request, rights_chain)
                if not commercial_valid:
                    report.issues.append("Commercial use not permitted")
            
            # Determine final result
            if len(report.issues) == 0 and len(report.conflicts) == 0:
                report.result = ValidationResult.APPROVED
            elif len(report.validated_rights) > 0:
                report.result = ValidationResult.REQUIRES_REVIEW
            else:
                report.result = ValidationResult.REJECTED
            
            # Set validity period
            if report.result == ValidationResult.APPROVED:
                validity_days = request.duration or 365
                report.valid_until = datetime.utcnow() + timedelta(days=validity_days)
            
            # Generate recommendations
            report.recommendations = await self._generate_recommendations(request, report)
            
            # Store validation report
            self.validation_reports[request.request_id] = report
            
            # Update metrics
            await self._update_validation_metrics(report, start_time)
            
            logger.info(f"Rights validation completed: {request.request_id} -> {report.result.value}")
            return report
            
        except Exception as e:
            logger.error(f"Error validating rights: {e}")
            
            # Return error report
            error_report = ValidationReport(
                request_id=request.request_id,
                content_id=request.content_id,
                result=ValidationResult.REJECTED,
                validated_rights=[],
                denied_rights=request.requested_rights,
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Contact support for manual review"],
                expiry_warnings=[],
                conflicts=[]
            )
            
            return error_report
    
    async def register_content_rights(
        self,
        content_id: int,
        owner_id: int,
        rights: List[Dict[str, Any]]
    ) -> bool:
        """
        Register rights for content
        
        Args:
            content_id: Content ID
            owner_id: Owner ID
            rights: List of rights to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Create rights chain if not exists
            if content_id not in self.content_rights:
                self.content_rights[content_id] = RightsChain(
                    content_id=content_id,
                    original_owner=owner_id,
                    current_owner=owner_id,
                    rights_history=[],
                    active_rights=[]
                )
            
            rights_chain = self.content_rights[content_id]
            
            # Register each right
            for right_data in rights:
                content_right = ContentRight(
                    right_id=f"right_{content_id}_{datetime.utcnow().timestamp()}",
                    content_id=content_id,
                    owner_id=owner_id,
                    right_type=RightType(right_data["type"]),
                    status=RightStatus.VALID,
                    granted_date=datetime.utcnow(),
                    expiry_date=datetime.fromisoformat(right_data["expiry"]) if right_data.get("expiry") else None,
                    territory=right_data.get("territory", "worldwide"),
                    exclusivity=right_data.get("exclusive", False),
                    transferable=right_data.get("transferable", True),
                    sublicensable=right_data.get("sublicensable", False),
                    restrictions=right_data.get("restrictions", []),
                    metadata=right_data.get("metadata", {})
                )
                
                rights_chain.rights_history.append(content_right)
                rights_chain.active_rights.append(content_right)
            
            rights_chain.last_verified = datetime.utcnow()
            
            logger.info(f"Rights registered for content {content_id}: {len(rights)} rights")
            return True
            
        except Exception as e:
            logger.error(f"Error registering rights: {e}")
            return False
    
    async def transfer_rights(
        self,
        content_id: int,
        from_owner: int,
        to_owner: int,
        rights_to_transfer: List[RightType],
        transfer_terms: Dict[str, Any]
    ) -> bool:
        """
        Transfer rights between owners
        
        Args:
            content_id: Content ID
            from_owner: Current owner ID
            to_owner: New owner ID
            rights_to_transfer: Rights to transfer
            transfer_terms: Terms of transfer
            
        Returns:
            bool: True if transfer successful
        """
        try:
            if content_id not in self.content_rights:
                return False
            
            rights_chain = self.content_rights[content_id]
            
            # Verify current ownership
            if rights_chain.current_owner != from_owner:
                logger.error(f"Rights transfer denied: {from_owner} is not current owner")
                return False
            
            # Check if rights are transferable
            for right_type in rights_to_transfer:
                active_right = None
                for right in rights_chain.active_rights:
                    if right.right_type == right_type and right.owner_id == from_owner:
                        active_right = right
                        break
                
                if not active_right or not active_right.transferable:
                    logger.error(f"Right {right_type.value} is not transferable")
                    return False
            
            # Create new rights for new owner
            for right_type in rights_to_transfer:
                # Find original right
                original_right = None
                for right in rights_chain.active_rights:
                    if right.right_type == right_type and right.owner_id == from_owner:
                        original_right = right
                        break
                
                if original_right:
                    # Create transferred right
                    transferred_right = ContentRight(
                        right_id=f"transfer_{content_id}_{datetime.utcnow().timestamp()}",
                        content_id=content_id,
                        owner_id=to_owner,
                        right_type=right_type,
                        status=RightStatus.VALID,
                        granted_date=datetime.utcnow(),
                        expiry_date=original_right.expiry_date,
                        territory=original_right.territory,
                        exclusivity=original_right.exclusivity,
                        transferable=original_right.transferable,
                        sublicensable=original_right.sublicensable,
                        restrictions=original_right.restrictions.copy(),
                        metadata={
                            **original_right.metadata,
                            "transferred_from": from_owner,
                            "transfer_date": datetime.utcnow().isoformat(),
                            "transfer_terms": transfer_terms
                        }
                    )
                    
                    # Add to rights chain
                    rights_chain.rights_history.append(transferred_right)
                    rights_chain.active_rights.append(transferred_right)
                    
                    # Revoke original right
                    original_right.status = RightStatus.REVOKED
                    original_right.metadata["revoked_date"] = datetime.utcnow().isoformat()
                    original_right.metadata["revocation_reason"] = "transferred"
            
            # Update current owner if all primary rights transferred
            primary_rights = [RightType.COPYRIGHT, RightType.LICENSING]
            if all(right in rights_to_transfer for right in primary_rights):
                rights_chain.current_owner = to_owner
            
            rights_chain.last_verified = datetime.utcnow()
            
            logger.info(f"Rights transferred for content {content_id}: {from_owner} -> {to_owner}")
            return True
            
        except Exception as e:
            logger.error(f"Error transferring rights: {e}")
            return False
    
    async def get_validation_report(self, request_id: str) -> Optional[ValidationReport]:
        """Get validation report by request ID"""
        return self.validation_reports.get(request_id)
    
    async def get_content_rights(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get rights information for content"""
        try:
            if content_id not in self.content_rights:
                return None
            
            rights_chain = self.content_rights[content_id]
            
            # Get active rights by type
            active_rights_by_type = {}
            for right in rights_chain.active_rights:
                if right.status == RightStatus.VALID:
                    right_type = right.right_type.value
                    if right_type not in active_rights_by_type:
                        active_rights_by_type[right_type] = []
                    
                    active_rights_by_type[right_type].append({
                        "right_id": right.right_id,
                        "owner_id": right.owner_id,
                        "granted_date": right.granted_date.isoformat(),
                        "expiry_date": right.expiry_date.isoformat() if right.expiry_date else None,
                        "territory": right.territory,
                        "exclusive": right.exclusivity,
                        "transferable": right.transferable,
                        "sublicensable": right.sublicensable,
                        "restrictions": right.restrictions
                    })
            
            return {
                "content_id": content_id,
                "original_owner": rights_chain.original_owner,
                "current_owner": rights_chain.current_owner,
                "active_rights": active_rights_by_type,
                "rights_count": len(rights_chain.active_rights),
                "conflicts": rights_chain.conflicts,
                "last_verified": rights_chain.last_verified.isoformat() if rights_chain.last_verified else None
            }
            
        except Exception as e:
            logger.error(f"Error getting content rights: {e}")
            return None
    
    async def _get_or_create_rights_chain(self, content_id: int) -> RightsChain:
        """Get or create rights chain for content"""
        if content_id not in self.content_rights:
            # Create default rights chain (assume content owner has all rights)
            self.content_rights[content_id] = RightsChain(
                content_id=content_id,
                original_owner=0,  # Unknown owner
                current_owner=0,
                rights_history=[],
                active_rights=[]
            )
        
        return self.content_rights[content_id]
    
    async def _verify_ownership(
        self,
        content_id: int,
        requester_id: int,
        rights_chain: RightsChain
    ) -> bool:
        """Verify ownership rights"""
        try:
            # Check if requester is current owner
            if rights_chain.current_owner == requester_id:
                return True
            
            # Check if requester has valid licensing rights
            for right in rights_chain.active_rights:
                if (right.owner_id == requester_id and
                    right.right_type in [RightType.COPYRIGHT, RightType.LICENSING] and
                    right.status == RightStatus.VALID):
                    
                    # Check expiry
                    if right.expiry_date and datetime.utcnow() > right.expiry_date:
                        continue
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying ownership: {e}")
            return False
    
    async def _validate_individual_right(
        self,
        request: ValidationRequest,
        right_type: RightType,
        rights_chain: RightsChain
    ) -> Dict[str, Any]:
        """Validate individual right type"""
        result = {
            "valid": False,
            "issues": [],
            "warnings": []
        }
        
        try:
            # Find relevant rights
            relevant_rights = []
            for right in rights_chain.active_rights:
                if right.owner_id == request.requester_id:
                    # Check hierarchy - higher level rights include lower level
                    if (right.right_type == right_type or
                        (right.right_type in self.rights_hierarchy and
                         right_type in self.rights_hierarchy[right.right_type])):
                        relevant_rights.append(right)
            
            if not relevant_rights:
                result["issues"].append(f"No {right_type.value} rights found")
                return result
            
            # Check each relevant right
            for right in relevant_rights:
                # Check status
                if right.status != RightStatus.VALID:
                    result["issues"].append(f"Right status is {right.status.value}")
                    continue
                
                # Check expiry
                if right.expiry_date and datetime.utcnow() > right.expiry_date:
                    result["issues"].append(f"Right expired on {right.expiry_date}")
                    continue
                
                # Check expiry warning (30 days)
                if right.expiry_date:
                    days_until_expiry = (right.expiry_date - datetime.utcnow()).days
                    if days_until_expiry <= 30:
                        result["warnings"].append(
                            f"Right expires in {days_until_expiry} days"
                        )
                
                # Check territory
                if request.territory != "worldwide" and right.territory != "worldwide":
                    if request.territory != right.territory:
                        result["issues"].append(f"Territory mismatch: {request.territory} vs {right.territory}")
                        continue
                
                # Check exclusivity conflicts
                if request.exclusive and not right.exclusivity:
                    result["issues"].append("Exclusive rights requested but not available")
                    continue
                
                # If we get here, the right is valid
                result["valid"] = True
                break
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating individual right: {e}")
            result["issues"].append(f"Validation error: {str(e)}")
            return result
    
    async def _check_rights_conflicts(
        self,
        request: ValidationRequest,
        rights_chain: RightsChain
    ) -> List[Dict[str, Any]]:
        """Check for rights conflicts"""
        conflicts = []
        
        try:
            # Check for exclusive rights conflicts
            if request.exclusive:
                for right in rights_chain.active_rights:
                    if (right.owner_id != request.requester_id and
                        right.exclusivity and
                        right.right_type in request.requested_rights and
                        right.status == RightStatus.VALID):
                        
                        conflicts.append({
                            "type": "exclusive_conflict",
                            "description": f"Exclusive {right.right_type.value} rights already granted to user {right.owner_id}",
                            "conflicting_right_id": right.right_id,
                            "conflicting_owner": right.owner_id
                        })
            
            # Check for territory conflicts
            for right_type in request.requested_rights:
                existing_exclusive_rights = [
                    right for right in rights_chain.active_rights
                    if (right.right_type == right_type and
                        right.exclusivity and
                        right.status == RightStatus.VALID and
                        right.owner_id != request.requester_id)
                ]
                
                for existing_right in existing_exclusive_rights:
                    if (request.territory == existing_right.territory or
                        request.territory == "worldwide" or
                        existing_right.territory == "worldwide"):
                        
                        conflicts.append({
                            "type": "territory_conflict",
                            "description": f"Exclusive {right_type.value} rights in {existing_right.territory} already granted",
                            "conflicting_right_id": existing_right.right_id,
                            "territory": existing_right.territory
                        })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return []
    
    async def _validate_territory(
        self,
        request: ValidationRequest,
        rights_chain: RightsChain
    ) -> bool:
        """Validate territory restrictions"""
        try:
            # For worldwide requests, need worldwide or specific territory rights
            if request.territory == "worldwide":
                # Check if requester has worldwide rights
                for right in rights_chain.active_rights:
                    if (right.owner_id == request.requester_id and
                        right.territory == "worldwide" and
                        right.status == RightStatus.VALID):
                        return True
            
            # For specific territory, check for territory or worldwide rights
            for right in rights_chain.active_rights:
                if (right.owner_id == request.requester_id and
                    (right.territory == request.territory or right.territory == "worldwide") and
                    right.status == RightStatus.VALID):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating territory: {e}")
            return False
    
    async def _validate_commercial_rights(
        self,
        request: ValidationRequest,
        rights_chain: RightsChain
    ) -> bool:
        """Validate commercial use rights"""
        try:
            # Check for commercial or higher level rights
            commercial_rights = [RightType.COMMERCIAL, RightType.COPYRIGHT, RightType.LICENSING]
            
            for right in rights_chain.active_rights:
                if (right.owner_id == request.requester_id and
                    right.right_type in commercial_rights and
                    right.status == RightStatus.VALID):
                    
                    # Check restrictions
                    if "no_commercial" not in right.restrictions:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating commercial rights: {e}")
            return False
    
    async def _generate_recommendations(
        self,
        request: ValidationRequest,
        report: ValidationReport
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        try:
            if report.result == ValidationResult.REJECTED:
                recommendations.append("Contact content owner to obtain necessary rights")
                
                if report.denied_rights:
                    recommendations.append(
                        f"Specific rights needed: {', '.join([r.value for r in report.denied_rights])}"
                    )
            
            elif report.result == ValidationResult.REQUIRES_REVIEW:
                recommendations.append("Manual review required due to complexity")
                
                if report.conflicts:
                    recommendations.append("Resolve rights conflicts before proceeding")
            
            elif report.result == ValidationResult.APPROVED:
                recommendations.append("Rights validation successful")
                
                if report.expiry_warnings:
                    recommendations.append("Monitor rights expiry dates")
            
            # Territory-specific recommendations
            if request.territory != "worldwide":
                recommendations.append(f"Ensure compliance with {request.territory} laws")
            
            # Commercial use recommendations
            if request.commercial:
                recommendations.append("Ensure proper attribution and royalty payments")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Manual review recommended due to validation error"]
    
    async def _update_validation_metrics(
        self,
        report: ValidationReport,
        start_time: datetime
    ) -> None:
        """Update validation metrics"""
        try:
            self.metrics["total_validations"] += 1
            
            if report.result == ValidationResult.APPROVED:
                self.metrics["approved_validations"] += 1
            elif report.result == ValidationResult.REJECTED:
                self.metrics["rejected_validations"] += 1
            
            if report.conflicts:
                self.metrics["conflicts_detected"] += len(report.conflicts)
            
            # Update average validation time
            validation_time = (datetime.utcnow() - start_time).total_seconds()
            total_validations = self.metrics["total_validations"]
            current_avg = self.metrics["average_validation_time"]
            
            self.metrics["average_validation_time"] = (
                (current_avg * (total_validations - 1) + validation_time) / total_validations
            )
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def get_validator_stats(self) -> Dict[str, Any]:
        """Get rights validator statistics"""
        try:
            total_content = len(self.content_rights)
            total_rights = sum(len(chain.active_rights) for chain in self.content_rights.values())
            
            # Rights type distribution
            rights_distribution = {}
            for chain in self.content_rights.values():
                for right in chain.active_rights:
                    if right.status == RightStatus.VALID:
                        right_type = right.right_type.value
                        rights_distribution[right_type] = rights_distribution.get(right_type, 0) + 1
            
            return {
                "version": "1.0.0",
                "content": {
                    "total_content_with_rights": total_content,
                    "total_active_rights": total_rights,
                    "rights_distribution": rights_distribution
                },
                "validations": self.metrics,
                "configuration": {
                    "supported_right_types": [rt.value for rt in RightType],
                    "validation_rules": self.validation_rules,
                    "rights_hierarchy_enabled": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting validator stats: {e}")
            return {"error": str(e)}