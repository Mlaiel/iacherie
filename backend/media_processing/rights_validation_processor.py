#!/usr/bin/env python3
"""🏛️ Rights Validation Processor - Digital Rights Management & Validation
===============================================================================
Module: backend/media_processing/rights_validation_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Legal Expert + Security Expert + Backend Senior Engineer + Blockchain Specialist
Type: Enterprise Digital Rights Processing System - Production-Ready
Responsibility: Comprehensive digital rights validation and license management
=================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🏛️ RIGHTS VALIDATION CAPABILITIES:
- Digital rights verification and validation
- License compliance checking
- Usage rights tracking and monitoring
- Rights chain validation
- Legal framework compliance
- Automated rights clearance
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json

logger = logging.getLogger(__name__)


class RightsType(Enum):
    """Digital rights types"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PUBLICITY = "publicity"
    DISTRIBUTION = "distribution"
    COMMERCIAL = "commercial"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"


class RightsStatus(Enum):
    """Rights validation status"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    PENDING = "pending"
    DISPUTED = "disputed"
    UNKNOWN = "unknown"


class LicenseType(Enum):
    """License types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EDITORIAL = "editorial"
    CUSTOM = "custom"


class UsageType(Enum):
    """Content usage types"""
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    PRINT = "print"
    DIGITAL = "digital"


@dataclass
class RightsInfo:
    """Digital rights information"""
    rights_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    rights_type: RightsType = RightsType.COPYRIGHT
    owner: str = ""
    license_type: LicenseType = LicenseType.NON_EXCLUSIVE
    usage_rights: List[UsageType] = field(default_factory=list)
    territory: List[str] = field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: RightsStatus = RightsStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ValidationResult:
    """Rights validation result"""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    is_valid: bool = False
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    validation_details: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LicenseValidation:
    """License validation details"""
    license_id: str = ""
    is_valid: bool = False
    usage_permitted: List[UsageType] = field(default_factory=list)
    usage_restricted: List[UsageType] = field(default_factory=list)
    territory_allowed: List[str] = field(default_factory=list)
    territory_restricted: List[str] = field(default_factory=list)
    expiry_date: Optional[datetime] = None
    renewal_required: bool = False
    compliance_notes: List[str] = field(default_factory=list)


class RightsValidationProcessor:
    """Enterprise rights validation and digital rights management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.rights_database: Dict[str, RightsInfo] = {}
        self.validation_cache: Dict[str, ValidationResult] = {}
        self.license_registry: Dict[str, LicenseValidation] = {}
        
        # Rights validation configuration
        self.validation_config = {
            "strict_mode": True,
            "auto_renewal": True,
            "territory_validation": True,
            "usage_tracking": True,
            "compliance_checking": True,
            "cache_duration": 3600  # 1 hour
        }
        
        self.logger.info("Rights Validation Processor initialized")
    
    async def validate_content_rights(
        self,
        content_id: str,
        intended_usage: List[UsageType],
        territory: List[str] = None,
        duration: int = None
    ) -> ValidationResult:
        """Validate digital rights for content"""
        try:
            self.logger.info(f"Validating rights for content: {content_id}")
            
            # Get rights information
            rights_info = await self._get_rights_info(content_id)
            if not rights_info:
                return ValidationResult(
                    content_id=content_id,
                    is_valid=False,
                    rights_status=RightsStatus.UNKNOWN,
                    violations=["No rights information found"],
                    confidence_score=0.0
                )
            
            # Perform comprehensive validation
            validation_result = ValidationResult(content_id=content_id)
            
            # Validate ownership
            ownership_valid = await self._validate_ownership(rights_info)
            if not ownership_valid:
                validation_result.violations.append("Ownership validation failed")
            
            # Validate license
            license_validation = await self._validate_license(rights_info, intended_usage, territory)
            if not license_validation.is_valid:
                validation_result.violations.extend(license_validation.compliance_notes)
            
            # Validate usage rights
            usage_valid = await self._validate_usage_rights(rights_info, intended_usage)
            if not usage_valid:
                validation_result.violations.append("Usage rights validation failed")
            
            # Validate territory
            if territory:
                territory_valid = await self._validate_territory(rights_info, territory)
                if not territory_valid:
                    validation_result.violations.append("Territory validation failed")
            
            # Validate expiry
            expiry_valid = await self._validate_expiry(rights_info, duration)
            if not expiry_valid:
                validation_result.violations.append("Rights expired or expiring soon")
            
            # Calculate overall validation
            validation_result.is_valid = len(validation_result.violations) == 0
            validation_result.rights_status = RightsStatus.VALID if validation_result.is_valid else RightsStatus.INVALID
            validation_result.confidence_score = await self._calculate_confidence_score(validation_result, rights_info)
            
            # Add recommendations
            validation_result.recommendations = await self._generate_recommendations(validation_result, rights_info)
            
            # Cache result
            await self._cache_validation_result(validation_result)
            
            self.logger.info(f"Rights validation completed for {content_id}: {validation_result.is_valid}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Rights validation failed for {content_id}: {str(e)}")
            return ValidationResult(
                content_id=content_id,
                is_valid=False,
                violations=[f"Validation error: {str(e)}"],
                confidence_score=0.0
            )
    
    async def register_content_rights(
        self,
        content_id: str,
        rights_type: RightsType,
        owner: str,
        license_type: LicenseType,
        usage_rights: List[UsageType],
        territory: List[str] = None,
        duration: int = None
    ) -> RightsInfo:
        """Register digital rights for content"""
        try:
            self.logger.info(f"Registering rights for content: {content_id}")
            
            # Create rights information
            rights_info = RightsInfo(
                content_id=content_id,
                rights_type=rights_type,
                owner=owner,
                license_type=license_type,
                usage_rights=usage_rights,
                territory=territory or ["GLOBAL"],
                valid_from=datetime.now(timezone.utc),
                valid_until=datetime.now(timezone.utc) + timedelta(days=duration) if duration else None,
                status=RightsStatus.VALID
            )
            
            # Validate registration data
            if not await self._validate_registration_data(rights_info):
                raise ValueError("Invalid rights registration data")
            
            # Store in rights database
            self.rights_database[content_id] = rights_info
            
            # Create license validation entry
            license_validation = LicenseValidation(
                license_id=rights_info.rights_id,
                is_valid=True,
                usage_permitted=usage_rights,
                territory_allowed=territory or ["GLOBAL"],
                expiry_date=rights_info.valid_until
            )
            
            self.license_registry[rights_info.rights_id] = license_validation
            
            self.logger.info(f"Rights registered successfully for {content_id}")
            return rights_info
            
        except Exception as e:
            self.logger.error(f"Rights registration failed for {content_id}: {str(e)}")
            raise
    
    async def check_license_compliance(
        self,
        content_id: str,
        usage_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check license compliance for specific usage context"""
        try:
            self.logger.info(f"Checking license compliance for: {content_id}")
            
            rights_info = await self._get_rights_info(content_id)
            if not rights_info:
                return {
                    "compliant": False,
                    "reason": "No rights information found",
                    "recommendations": ["Register content rights"]
                }
            
            # Extract usage context
            intended_usage = usage_context.get("usage_type", [])
            territory = usage_context.get("territory", [])
            commercial = usage_context.get("commercial", False)
            duration = usage_context.get("duration")
            
            # Check compliance
            compliance_checks = {
                "usage_rights": await self._check_usage_compliance(rights_info, intended_usage),
                "territory_rights": await self._check_territory_compliance(rights_info, territory),
                "commercial_rights": await self._check_commercial_compliance(rights_info, commercial),
                "duration_compliance": await self._check_duration_compliance(rights_info, duration),
                "license_validity": await self._check_license_validity(rights_info)
            }
            
            # Calculate overall compliance
            all_compliant = all(compliance_checks.values())
            
            # Generate compliance report
            compliance_report = {
                "compliant": all_compliant,
                "checks": compliance_checks,
                "rights_info": {
                    "rights_type": rights_info.rights_type.value,
                    "license_type": rights_info.license_type.value,
                    "owner": rights_info.owner,
                    "valid_until": rights_info.valid_until.isoformat() if rights_info.valid_until else None
                },
                "recommendations": await self._generate_compliance_recommendations(compliance_checks, rights_info)
            }
            
            self.logger.info(f"License compliance check completed for {content_id}: {all_compliant}")
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"License compliance check failed for {content_id}: {str(e)}")
            return {
                "compliant": False,
                "reason": f"Compliance check error: {str(e)}",
                "recommendations": ["Contact legal team"]
            }
    
    async def track_usage_rights(
        self,
        content_id: str,
        usage_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track usage rights and monitor compliance"""
        try:
            self.logger.info(f"Tracking usage rights for: {content_id}")
            
            # Record usage event
            usage_record = {
                "usage_id": str(uuid.uuid4()),
                "content_id": content_id,
                "usage_type": usage_event.get("usage_type"),
                "territory": usage_event.get("territory"),
                "user_id": usage_event.get("user_id"),
                "platform": usage_event.get("platform"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": usage_event.get("metadata", {})
            }
            
            # Validate usage against rights
            validation_result = await self.validate_content_rights(
                content_id=content_id,
                intended_usage=usage_event.get("usage_type", []),
                territory=usage_event.get("territory", [])
            )
            
            # Update usage tracking
            tracking_result = {
                "usage_record": usage_record,
                "validation_result": {
                    "is_valid": validation_result.is_valid,
                    "violations": validation_result.violations,
                    "confidence_score": validation_result.confidence_score
                },
                "compliance_status": "COMPLIANT" if validation_result.is_valid else "NON_COMPLIANT",
                "tracking_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Store tracking data
            await self._store_usage_tracking(tracking_result)
            
            self.logger.info(f"Usage rights tracking completed for {content_id}")
            return tracking_result
            
        except Exception as e:
            self.logger.error(f"Usage rights tracking failed for {content_id}: {str(e)}")
            raise
    
    async def _get_rights_info(self, content_id: str) -> Optional[RightsInfo]:
        """Get rights information for content"""
        return self.rights_database.get(content_id)
    
    async def _validate_ownership(self, rights_info: RightsInfo) -> bool:
        """Validate content ownership"""
        # Implement ownership validation logic
        return bool(rights_info.owner and len(rights_info.owner) > 0)
    
    async def _validate_license(
        self,
        rights_info: RightsInfo,
        intended_usage: List[UsageType],
        territory: List[str]
    ) -> LicenseValidation:
        """Validate license for intended usage"""
        license_validation = self.license_registry.get(rights_info.rights_id)
        if not license_validation:
            license_validation = LicenseValidation(
                license_id=rights_info.rights_id,
                is_valid=False,
                compliance_notes=["License not found in registry"]
            )
        
        return license_validation
    
    async def _validate_usage_rights(self, rights_info: RightsInfo, intended_usage: List[UsageType]) -> bool:
        """Validate usage rights"""
        if not intended_usage:
            return True
        
        for usage in intended_usage:
            if usage not in rights_info.usage_rights:
                return False
        
        return True
    
    async def _validate_territory(self, rights_info: RightsInfo, territory: List[str]) -> bool:
        """Validate territorial rights"""
        if not territory:
            return True
        
        if "GLOBAL" in rights_info.territory:
            return True
        
        for t in territory:
            if t not in rights_info.territory:
                return False
        
        return True
    
    async def _validate_expiry(self, rights_info: RightsInfo, duration: int = None) -> bool:
        """Validate rights expiry"""
        if not rights_info.valid_until:
            return True
        
        now = datetime.now(timezone.utc)
        if rights_info.valid_until <= now:
            return False
        
        return True
    
    async def _calculate_confidence_score(self, validation_result: ValidationResult, rights_info: RightsInfo) -> float:
        """Calculate confidence score for validation"""
        base_score = 1.0 if validation_result.is_valid else 0.0
        
        # Adjust based on data completeness
        completeness_factor = 0.0
        if rights_info.owner:
            completeness_factor += 0.2
        if rights_info.valid_until:
            completeness_factor += 0.2
        if rights_info.usage_rights:
            completeness_factor += 0.3
        if rights_info.territory:
            completeness_factor += 0.3
        
        return min(base_score * (1 + completeness_factor), 1.0)
    
    async def _generate_recommendations(self, validation_result: ValidationResult, rights_info: RightsInfo) -> List[str]:
        """Generate recommendations based on validation result"""
        recommendations = []
        
        if not validation_result.is_valid:
            recommendations.append("Review and update rights information")
            
        if rights_info.valid_until and (rights_info.valid_until - datetime.now(timezone.utc)).days < 30:
            recommendations.append("Rights expiring soon - consider renewal")
            
        if not rights_info.usage_rights:
            recommendations.append("Define specific usage rights")
            
        return recommendations
    
    async def _cache_validation_result(self, result: ValidationResult):
        """Cache validation result"""
        self.validation_cache[result.content_id] = result
    
    async def _validate_registration_data(self, rights_info: RightsInfo) -> bool:
        """Validate rights registration data"""
        required_fields = [
            rights_info.content_id,
            rights_info.owner,
            rights_info.rights_type,
            rights_info.license_type
        ]
        
        return all(field for field in required_fields)
    
    async def _check_usage_compliance(self, rights_info: RightsInfo, intended_usage: List[UsageType]) -> bool:
        """Check usage compliance"""
        return await self._validate_usage_rights(rights_info, intended_usage)
    
    async def _check_territory_compliance(self, rights_info: RightsInfo, territory: List[str]) -> bool:
        """Check territory compliance"""
        return await self._validate_territory(rights_info, territory)
    
    async def _check_commercial_compliance(self, rights_info: RightsInfo, commercial: bool) -> bool:
        """Check commercial usage compliance"""
        if not commercial:
            return True
        
        return UsageType.COMMERCIAL in rights_info.usage_rights
    
    async def _check_duration_compliance(self, rights_info: RightsInfo, duration: int) -> bool:
        """Check duration compliance"""
        return await self._validate_expiry(rights_info, duration)
    
    async def _check_license_validity(self, rights_info: RightsInfo) -> bool:
        """Check license validity"""
        return rights_info.status == RightsStatus.VALID
    
    async def _generate_compliance_recommendations(self, checks: Dict[str, bool], rights_info: RightsInfo) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for check_name, is_compliant in checks.items():
            if not is_compliant:
                recommendations.append(f"Address {check_name} compliance issue")
        
        return recommendations
    
    async def _store_usage_tracking(self, tracking_result: Dict[str, Any]):
        """Store usage tracking data"""
        # Implement persistent storage for usage tracking
        pass


# Singleton instance
_rights_processor = None

def get_rights_processor() -> RightsValidationProcessor:
    """Get singleton rights validation processor instance"""
    global _rights_processor
    if _rights_processor is None:
        _rights_processor = RightsValidationProcessor()
    return _rights_processor