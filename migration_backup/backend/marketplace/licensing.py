"""Content Licensing Management System
=====================================

Advanced content licensing orchestrator integrating with existing licensing
infrastructure for the IA Influencer Agent platform.

Features:
- Automated license agreement generation and validation
- Multi-format content licensing (audio, video, image, text)
- Rights management and usage tracking
- License compliance monitoring
- Integration with existing licensing engines

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """License type enumeration"""
    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC = "sync"
    MASTER = "master"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"

class LicenseStatus(Enum):
    """License status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"

class UsageRights(Enum):
    """Usage rights enumeration"""
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    COMMERCIAL_USE = "commercial_use"
    PUBLIC_PERFORMANCE = "public_performance"
    SYNCHRONIZATION = "synchronization"
    REPRODUCTION = "reproduction"
    BROADCASTING = "broadcasting"
    STREAMING = "streaming"

@dataclass
class LicenseTerms:
    """License terms and conditions"""
    usage_rights: List[UsageRights]
    territory: str = "Worldwide"
    duration_months: Optional[int] = None
    max_distributions: Optional[int] = None
    revenue_sharing_percentage: Decimal = Decimal('0.00')
    attribution_required: bool = True
    modifications_allowed: bool = False
    commercial_use_allowed: bool = False
    exclusivity_period_days: Optional[int] = None
    restrictions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert terms to dictionary"""
        return {
            "usage_rights": [right.value for right in self.usage_rights],
            "territory": self.territory,
            "duration_months": self.duration_months,
            "max_distributions": self.max_distributions,
            "revenue_sharing_percentage": float(self.revenue_sharing_percentage),
            "attribution_required": self.attribution_required,
            "modifications_allowed": self.modifications_allowed,
            "commercial_use_allowed": self.commercial_use_allowed,
            "exclusivity_period_days": self.exclusivity_period_days,
            "restrictions": self.restrictions
        }

@dataclass
class LicenseAgreement:
    """License agreement data structure"""
    license_id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    license_type: LicenseType
    terms: LicenseTerms
    price: Decimal
    currency: str = "USD"
    status: LicenseStatus = LicenseStatus.DRAFT
    signed_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    auto_renewal: bool = False
    usage_count: int = 0
    revenue_generated: Decimal = Decimal('0.00')
    compliance_score: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_active(self) -> bool:
        """Check if license is currently active"""
        if self.status != LicenseStatus.ACTIVE:
            return False
        
        now = datetime.utcnow()
        
        if self.effective_date and now < self.effective_date:
            return False
        
        if self.expiration_date and now > self.expiration_date:
            return False
        
        return True
    
    def days_until_expiration(self) -> Optional[int]:
        """Get days until license expires"""
        if not self.expiration_date:
            return None
        
        delta = self.expiration_date - datetime.utcnow()
        return max(0, delta.days)

class LicenseValidation:
    """License validation and compliance checker"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize validation system"""
        self.config = config or {}
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules"""
        return {
            "min_license_duration": 1,  # months
            "max_license_duration": 120,  # months
            "required_usage_rights": [],
            "territory_restrictions": [],
            "price_limits": {
                "min": Decimal('0.01'),
                "max": Decimal('1000000.00')
            }
        }
    
    async def validate_license_request(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate license request"""
        errors = []
        warnings = []
        
        try:
            # Validate required fields
            required_fields = ['content_id', 'licensor_id', 'licensee_id', 'license_type', 'terms', 'price']
            for field in required_fields:
                if field not in license_data:
                    errors.append(f"Missing required field: {field}")
            
            if errors:
                return {"valid": False, "errors": errors, "warnings": warnings}
            
            # Validate license type
            try:
                LicenseType(license_data['license_type'])
            except ValueError:
                errors.append(f"Invalid license type: {license_data['license_type']}")
            
            # Validate price
            price = Decimal(str(license_data['price']))
            if price < self.validation_rules['price_limits']['min']:
                errors.append(f"Price too low: minimum {self.validation_rules['price_limits']['min']}")
            elif price > self.validation_rules['price_limits']['max']:
                errors.append(f"Price too high: maximum {self.validation_rules['price_limits']['max']}")
            
            # Validate terms
            terms_data = license_data.get('terms', {})
            if 'duration_months' in terms_data:
                duration = terms_data['duration_months']
                if duration and (duration < self.validation_rules['min_license_duration'] or 
                               duration > self.validation_rules['max_license_duration']):
                    errors.append(f"Invalid duration: must be between {self.validation_rules['min_license_duration']} and {self.validation_rules['max_license_duration']} months")
            
            # Check for potential conflicts
            if license_data.get('license_type') == 'exclusive':
                # Check for existing exclusive licenses (would require database check)
                warnings.append("Exclusive license - verify no conflicting licenses exist")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return {"valid": False, "errors": [f"Validation error: {e}"], "warnings": warnings}
    
    async def check_compliance(self, license: LicenseAgreement, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check license compliance"""
        violations = []
        score = 100.0
        
        try:
            # Check usage count limits
            if license.terms.max_distributions:
                if usage_data.get('distribution_count', 0) > license.terms.max_distributions:
                    violations.append("Exceeded maximum distribution limit")
                    score -= 20
            
            # Check territory restrictions
            usage_territories = usage_data.get('territories', [])
            if license.terms.territory != "Worldwide" and usage_territories:
                allowed_territories = license.terms.territory.split(',')
                for territory in usage_territories:
                    if territory.strip() not in allowed_territories:
                        violations.append(f"Unauthorized territory usage: {territory}")
                        score -= 15
            
            # Check usage rights compliance
            requested_rights = usage_data.get('usage_rights', [])
            for right in requested_rights:
                if UsageRights(right) not in license.terms.usage_rights:
                    violations.append(f"Unauthorized usage right: {right}")
                    score -= 10
            
            # Check commercial use
            if usage_data.get('commercial_use', False) and not license.terms.commercial_use_allowed:
                violations.append("Unauthorized commercial use")
                score -= 25
            
            # Check modifications
            if usage_data.get('modifications_made', False) and not license.terms.modifications_allowed:
                violations.append("Unauthorized content modification")
                score -= 15
            
            return {
                "compliant": len(violations) == 0,
                "violations": violations,
                "compliance_score": max(0, score),
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {
                "compliant": False,
                "violations": [f"Compliance check failed: {e}"],
                "compliance_score": 0,
                "checked_at": datetime.utcnow().isoformat()
            }

class LicensingManager:
    """Advanced licensing management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize licensing manager"""
        self.config = config or {}
        self.licenses: Dict[str, LicenseAgreement] = {}
        self.validation_engine = LicenseValidation(self.config.get('validation', {}))
        
        # Integration with existing licensing engines
        self.has_core_licensing = False
        self.has_monetization_licensing = False
        
        try:
            from ...core.licensing.licensing_engine import LicensingEngine
            self.core_licensing_engine = LicensingEngine(self.config.get('core_licensing', {}))
            self.has_core_licensing = True
        except ImportError:
            logger.warning("Core licensing engine not available")
        
        try:
            from ...monetization.licensing_engine import LicensingEngine as MonetizationLicensingEngine
            self.monetization_licensing_engine = MonetizationLicensingEngine(self.config.get('monetization_licensing', {}))
            self.has_monetization_licensing = True
        except ImportError:
            logger.warning("Monetization licensing engine not available")
        
        logger.info("📄 Licensing Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize licensing manager"""
        logger.info("🚀 Initializing Licensing Manager")
        
        # Initialize integrated engines
        if self.has_core_licensing:
            await self.core_licensing_engine.initialize()
        
        # Start background tasks
        asyncio.create_task(self._compliance_monitor())
        asyncio.create_task(self._expiration_monitor())
    
    async def create_license(self, license_data: Dict[str, Any]) -> LicenseAgreement:
        """Create new license agreement"""
        try:
            # Validate license request
            validation_result = await self.validation_engine.validate_license_request(license_data)
            
            if not validation_result['valid']:
                raise ValueError(f"License validation failed: {validation_result['errors']}")
            
            license_id = str(uuid.uuid4())
            
            # Parse terms
            terms_data = license_data['terms']
            terms = LicenseTerms(
                usage_rights=[UsageRights(right) for right in terms_data.get('usage_rights', [])],
                territory=terms_data.get('territory', 'Worldwide'),
                duration_months=terms_data.get('duration_months'),
                max_distributions=terms_data.get('max_distributions'),
                revenue_sharing_percentage=Decimal(str(terms_data.get('revenue_sharing_percentage', '0.00'))),
                attribution_required=terms_data.get('attribution_required', True),
                modifications_allowed=terms_data.get('modifications_allowed', False),
                commercial_use_allowed=terms_data.get('commercial_use_allowed', False),
                exclusivity_period_days=terms_data.get('exclusivity_period_days'),
                restrictions=terms_data.get('restrictions', [])
            )
            
            # Calculate effective and expiration dates
            effective_date = datetime.utcnow()
            expiration_date = None
            if terms.duration_months:
                expiration_date = effective_date + timedelta(days=terms.duration_months * 30)
            
            license = LicenseAgreement(
                license_id=license_id,
                content_id=license_data['content_id'],
                licensor_id=license_data['licensor_id'],
                licensee_id=license_data['licensee_id'],
                license_type=LicenseType(license_data['license_type']),
                terms=terms,
                price=Decimal(str(license_data['price'])),
                currency=license_data.get('currency', 'USD'),
                status=LicenseStatus.PENDING_APPROVAL,  # Set to pending approval
                effective_date=effective_date,
                expiration_date=expiration_date,
                auto_renewal=license_data.get('auto_renewal', False),
                metadata=license_data.get('metadata', {})
            )
            
            self.licenses[license_id] = license
            
            # Integrate with core licensing if available
            if self.has_core_licensing:
                await self._sync_with_core_licensing(license)
            
            logger.info(f"Created license: {license_id} for content: {license.content_id}")
            return license
            
        except Exception as e:
            logger.error(f"Failed to create license: {e}")
            raise
    
    async def activate_license(self, license_id: str) -> LicenseAgreement:
        """Activate a license agreement"""
        try:
            if license_id not in self.licenses:
                raise ValueError(f"License {license_id} not found")
            
            license = self.licenses[license_id]
            
            if license.status != LicenseStatus.PENDING_APPROVAL:
                raise ValueError(f"License must be in pending approval status to activate")
            
            license.status = LicenseStatus.ACTIVE
            license.signed_date = datetime.utcnow()
            license.updated_at = datetime.utcnow()
            
            logger.info(f"Activated license: {license_id}")
            return license
            
        except Exception as e:
            logger.error(f"Failed to activate license: {e}")
            raise
    
    async def check_license_compliance(self, license_id: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check license compliance"""
        try:
            if license_id not in self.licenses:
                raise ValueError(f"License {license_id} not found")
            
            license = self.licenses[license_id]
            
            compliance_result = await self.validation_engine.check_compliance(license, usage_data)
            
            # Update license compliance score
            license.compliance_score = compliance_result['compliance_score']
            license.updated_at = datetime.utcnow()
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Failed to check compliance: {e}")
            return {
                "compliant": False,
                "violations": [f"Compliance check error: {e}"],
                "compliance_score": 0,
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def record_usage(self, license_id: str, usage_data: Dict[str, Any]) -> None:
        """Record license usage"""
        try:
            if license_id not in self.licenses:
                raise ValueError(f"License {license_id} not found")
            
            license = self.licenses[license_id]
            license.usage_count += 1
            
            # Record revenue if provided
            if 'revenue' in usage_data:
                revenue = Decimal(str(usage_data['revenue']))
                license.revenue_generated += revenue
            
            license.updated_at = datetime.utcnow()
            
            # Check compliance with usage
            await self.check_license_compliance(license_id, usage_data)
            
            logger.info(f"Recorded usage for license: {license_id}")
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            raise
    
    async def get_license(self, license_id: str) -> Optional[LicenseAgreement]:
        """Get license by ID"""
        return self.licenses.get(license_id)
    
    async def get_licenses_by_content(self, content_id: str) -> List[LicenseAgreement]:
        """Get all licenses for content"""
        return [license for license in self.licenses.values() if license.content_id == content_id]
    
    async def get_licenses_by_user(self, user_id: str, as_licensor: bool = True) -> List[LicenseAgreement]:
        """Get licenses by user (as licensor or licensee)"""
        if as_licensor:
            return [license for license in self.licenses.values() if license.licensor_id == user_id]
        else:
            return [license for license in self.licenses.values() if license.licensee_id == user_id]
    
    async def get_expiring_licenses(self, days_ahead: int = 30) -> List[LicenseAgreement]:
        """Get licenses expiring within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return [
            license for license in self.licenses.values()
            if license.expiration_date and 
            license.expiration_date <= cutoff_date and
            license.status == LicenseStatus.ACTIVE
        ]
    
    async def _sync_with_core_licensing(self, license: LicenseAgreement) -> None:
        """Sync with core licensing engine"""
        if self.has_core_licensing:
            try:
                # Create corresponding license in core system
                license_request = {
                    "content_id": license.content_id,
                    "licensee_id": license.licensee_id,
                    "license_type": license.license_type,
                    "usage_rights": [right.value for right in license.terms.usage_rights],
                    "territory": license.terms.territory,
                    "duration_months": license.terms.duration_months
                }
                
                await self.core_licensing_engine.create_license(license_request)
                
            except Exception as e:
                logger.warning(f"Failed to sync with core licensing: {e}")
    
    async def _compliance_monitor(self) -> None:
        """Background compliance monitoring"""
        while True:
            try:
                for license in self.licenses.values():
                    if license.status == LicenseStatus.ACTIVE:
                        # Check for compliance issues
                        if license.compliance_score < 80:
                            logger.warning(f"License {license.license_id} has low compliance score: {license.compliance_score}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in compliance monitor: {e}")
                await asyncio.sleep(3600)
    
    async def _expiration_monitor(self) -> None:
        """Background expiration monitoring"""
        while True:
            try:
                expiring_licenses = await self.get_expiring_licenses(7)  # 7 days ahead
                
                for license in expiring_licenses:
                    logger.info(f"License {license.license_id} expires in {license.days_until_expiration()} days")
                    
                    # Handle auto-renewal
                    if license.auto_renewal and license.days_until_expiration() <= 1:
                        if license.terms.duration_months:
                            license.expiration_date += timedelta(days=license.terms.duration_months * 30)
                            logger.info(f"Auto-renewed license {license.license_id}")
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"Error in expiration monitor: {e}")
                await asyncio.sleep(86400)


# Export main classes
__all__ = [
    "LicenseType",
    "LicenseStatus",
    "UsageRights",
    "LicenseTerms",
    "LicenseAgreement",
    "LicenseValidation",
    "LicensingManager"
]