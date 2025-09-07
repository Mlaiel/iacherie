"""Voice Rights Management System

Comprehensive voice content rights management, licensing automation,
and legal compliance system for enterprise voice content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class RightsType(Enum):
    """Types of voice content rights"""
    OWNERSHIP = "ownership"
    USAGE = "usage"
    DISTRIBUTION = "distribution"
    COMMERCIAL = "commercial"
    DERIVATIVE = "derivative"
    PERFORMANCE = "performance"
    REPRODUCTION = "reproduction"
    SYNCHRONIZATION = "synchronization"


class LicenseType(Enum):
    """Voice content license types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"


class RightsStatus(Enum):
    """Rights management status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISPUTED = "disputed"
    TRANSFERRED = "transferred"


class ComplianceLevel(Enum):
    """Legal compliance levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    LEGAL_PLUS = "legal_plus"


@dataclass
class VoiceRights:
    """Voice content rights definition"""
    rights_id: str
    content_id: str
    creator_id: str
    rights_holder: str
    rights_types: List[RightsType]
    jurisdiction: str
    validity_period: Dict[str, datetime]
    usage_restrictions: Dict[str, Any]
    monetary_terms: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    status: RightsStatus = RightsStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceLicense:
    """Voice content license agreement"""
    license_id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    license_type: LicenseType
    rights_granted: List[RightsType]
    license_terms: Dict[str, Any]
    financial_terms: Dict[str, Any]
    usage_limitations: Dict[str, Any]
    territory: List[str]
    duration: Dict[str, datetime]
    created_at: datetime = field(default_factory=datetime.now)
    status: RightsStatus = RightsStatus.PENDING
    compliance_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RightsViolation:
    """Rights violation record"""
    violation_id: str
    content_id: str
    violator_info: Dict[str, Any]
    violation_type: str
    violation_details: Dict[str, Any]
    evidence: Dict[str, Any]
    severity: str
    detected_at: datetime = field(default_factory=datetime.now)
    resolution_status: str = "pending"
    legal_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RightsManagementResult:
    """Rights management operation result"""
    operation_type: str
    success: bool
    rights_id: Optional[str] = None
    license_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class VoiceRightsManager:
    """Voice Rights Management System"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Rights database (in production, this would be a real database)
        self.voice_rights: Dict[str, VoiceRights] = {}
        self.voice_licenses: Dict[str, VoiceLicense] = {}
        self.rights_violations: List[RightsViolation] = []
        
        # Legal frameworks and jurisdictions
        self.legal_frameworks = self._initialize_legal_frameworks()
        self.jurisdiction_rules = self._initialize_jurisdiction_rules()
        
        # Compliance systems
        self.compliance_checkers = {}
        self.legal_automation = True
        
        # Licensing automation
        self.auto_licensing_enabled = True
        self.licensing_templates = self._initialize_licensing_templates()
        
        # Rights monitoring
        self.rights_monitoring_enabled = True
        self.violation_detection_enabled = True
        
    def _initialize_legal_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize legal frameworks for different jurisdictions"""
        return {
            "US": {
                "copyright_law": "US Copyright Act",
                "performance_rights": "ASCAP/BMI/SESAC",
                "fair_use": "17 USC 107",
                "dmca": "Digital Millennium Copyright Act",
                "duration": "Life + 70 years",
                "registration": "US Copyright Office"
            },
            "EU": {
                "copyright_law": "EU Copyright Directive 2019/790",
                "performance_rights": "CISAC members",
                "fair_use": "EU exceptions and limitations",
                "digital_single_market": "DSM Directive",
                "duration": "Life + 70 years",
                "registration": "National copyright offices"
            },
            "UK": {
                "copyright_law": "Copyright, Designs and Patents Act 1988",
                "performance_rights": "PRS for Music/PPL",
                "fair_dealing": "UK fair dealing provisions",
                "duration": "Life + 70 years",
                "registration": "UK Intellectual Property Office"
            },
            "INTERNATIONAL": {
                "berne_convention": "Berne Convention for Literary and Artistic Works",
                "wipo": "World Intellectual Property Organization",
                "trips": "TRIPS Agreement",
                "wct": "WIPO Copyright Treaty",
                "wppt": "WIPO Performances and Phonograms Treaty"
            }
        }
    
    def _initialize_jurisdiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize jurisdiction-specific rules"""
        return {
            "US": {
                "registration_required": False,
                "work_for_hire": True,
                "moral_rights": False,
                "termination_rights": True,
                "statutory_damages": True,
                "attorney_fees": True
            },
            "EU": {
                "registration_required": False,
                "work_for_hire": False,
                "moral_rights": True,
                "resale_rights": True,
                "orphan_works": True,
                "collective_licensing": True
            },
            "UK": {
                "registration_required": False,
                "work_for_hire": False,
                "moral_rights": True,
                "performers_rights": True,
                "fair_dealing": True,
                "collective_licensing": True
            }
        }
    
    def _initialize_licensing_templates(self) -> Dict[LicenseType, Dict[str, Any]]:
        """Initialize licensing templates"""
        return {
            LicenseType.EXCLUSIVE: {
                "exclusivity": True,
                "transferable": True,
                "sublicensing": True,
                "revenue_sharing": "negotiable",
                "territory": "worldwide",
                "duration": "negotiable",
                "minimum_guarantees": True
            },
            LicenseType.NON_EXCLUSIVE: {
                "exclusivity": False,
                "transferable": False,
                "sublicensing": False,
                "revenue_sharing": "standard",
                "territory": "specific",
                "duration": "limited",
                "minimum_guarantees": False
            },
            LicenseType.ROYALTY_FREE: {
                "exclusivity": False,
                "transferable": True,
                "sublicensing": True,
                "revenue_sharing": "none",
                "territory": "worldwide",
                "duration": "perpetual",
                "upfront_payment": True
            },
            LicenseType.CREATIVE_COMMONS: {
                "exclusivity": False,
                "transferable": True,
                "sublicensing": True,
                "revenue_sharing": "none",
                "territory": "worldwide",
                "duration": "perpetual",
                "attribution_required": True
            }
        }
    
    async def register_voice_rights(
        self,
        content_id: str,
        creator_id: str,
        rights_holder: str,
        rights_types: List[RightsType],
        jurisdiction: str = "US",
        metadata: Optional[Dict[str, Any]] = None
    ) -> RightsManagementResult:
        """Register voice content rights"""
        
        try:
            self.logger.info(f"Registering voice rights for content {content_id}")
            
            rights_id = f"rights_{uuid.uuid4().hex[:12]}"
            
            # Validate jurisdiction
            if jurisdiction not in self.legal_frameworks:
                return RightsManagementResult(
                    operation_type="register_rights",
                    success=False,
                    message=f"Unsupported jurisdiction: {jurisdiction}"
                )
            
            # Check for existing rights
            existing_rights = await self._check_existing_rights(content_id)
            if existing_rights and existing_rights.status == RightsStatus.ACTIVE:
                return RightsManagementResult(
                    operation_type="register_rights",
                    success=False,
                    message="Rights already exist for this content",
                    details={"existing_rights_id": existing_rights.rights_id}
                )
            
            # Calculate validity period based on jurisdiction
            validity_period = await self._calculate_validity_period(jurisdiction, creator_id)
            
            # Create usage restrictions based on rights types
            usage_restrictions = await self._create_usage_restrictions(rights_types, jurisdiction)
            
            # Create monetary terms template
            monetary_terms = await self._create_monetary_terms(rights_types, jurisdiction)
            
            # Create rights record
            voice_rights = VoiceRights(
                rights_id=rights_id,
                content_id=content_id,
                creator_id=creator_id,
                rights_holder=rights_holder,
                rights_types=rights_types,
                jurisdiction=jurisdiction,
                validity_period=validity_period,
                usage_restrictions=usage_restrictions,
                monetary_terms=monetary_terms,
                metadata=metadata or {}
            )
            
            # Store rights
            self.voice_rights[rights_id] = voice_rights
            
            # Start rights monitoring
            if self.rights_monitoring_enabled:
                asyncio.create_task(self._monitor_rights(rights_id))
            
            self.logger.info(f"Voice rights registered successfully: {rights_id}")
            
            return RightsManagementResult(
                operation_type="register_rights",
                success=True,
                rights_id=rights_id,
                message="Rights registered successfully",
                details={
                    "jurisdiction": jurisdiction,
                    "rights_types": [rt.value for rt in rights_types],
                    "validity_period": {k: v.isoformat() for k, v in validity_period.items()}
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error registering voice rights: {str(e)}")
            return RightsManagementResult(
                operation_type="register_rights",
                success=False,
                message=f"Error registering rights: {str(e)}"
            )
    
    async def create_voice_license(
        self,
        content_id: str,
        licensor_id: str,
        licensee_id: str,
        license_type: LicenseType,
        rights_granted: List[RightsType],
        territory: List[str],
        duration_months: int,
        financial_terms: Optional[Dict[str, Any]] = None
    ) -> RightsManagementResult:
        """Create voice content license agreement"""
        
        try:
            self.logger.info(f"Creating voice license for content {content_id}")
            
            license_id = f"license_{uuid.uuid4().hex[:12]}"
            
            # Verify rights ownership
            rights_check = await self._verify_licensing_rights(content_id, licensor_id)
            if not rights_check["can_license"]:
                return RightsManagementResult(
                    operation_type="create_license",
                    success=False,
                    message=f"Licensor does not have licensing rights: {rights_check['reason']}"
                )
            
            # Get license template
            template = self.licensing_templates[license_type]
            
            # Create license terms
            license_terms = await self._create_license_terms(
                license_type, rights_granted, template
            )
            
            # Set financial terms
            if not financial_terms:
                financial_terms = await self._generate_financial_terms(
                    license_type, rights_granted, duration_months
                )
            
            # Create usage limitations
            usage_limitations = await self._create_usage_limitations(
                license_type, rights_granted
            )
            
            # Calculate duration
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_months * 30)
            duration = {
                "start_date": start_date,
                "end_date": end_date,
                "duration_months": duration_months
            }
            
            # Perform compliance check
            compliance_data = await self._perform_compliance_check(
                content_id, license_type, territory
            )
            
            # Create license
            voice_license = VoiceLicense(
                license_id=license_id,
                content_id=content_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                license_type=license_type,
                rights_granted=rights_granted,
                license_terms=license_terms,
                financial_terms=financial_terms,
                usage_limitations=usage_limitations,
                territory=territory,
                duration=duration,
                compliance_data=compliance_data
            )
            
            # Store license
            self.voice_licenses[license_id] = voice_license
            
            # Auto-approve if enabled and compliant
            if self.auto_licensing_enabled and compliance_data["compliant"]:
                voice_license.status = RightsStatus.ACTIVE
                asyncio.create_task(self._start_license_monitoring(license_id))
            
            self.logger.info(f"Voice license created successfully: {license_id}")
            
            return RightsManagementResult(
                operation_type="create_license",
                success=True,
                license_id=license_id,
                message="License created successfully",
                details={
                    "license_type": license_type.value,
                    "rights_granted": [rg.value for rg in rights_granted],
                    "status": voice_license.status.value,
                    "duration": duration_months
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating voice license: {str(e)}")
            return RightsManagementResult(
                operation_type="create_license",
                success=False,
                message=f"Error creating license: {str(e)}"
            )
    
    async def _check_existing_rights(self, content_id: str) -> Optional[VoiceRights]:
        """Check for existing rights on content"""
        for rights in self.voice_rights.values():
            if rights.content_id == content_id and rights.status == RightsStatus.ACTIVE:
                return rights
        return None
    
    async def _calculate_validity_period(
        self, 
        jurisdiction: str, 
        creator_id: str
    ) -> Dict[str, datetime]:
        """Calculate rights validity period based on jurisdiction"""
        
        framework = self.legal_frameworks.get(jurisdiction, self.legal_frameworks["US"])
        
        start_date = datetime.now()
        
        # Simplified calculation - in production, this would consider actual legal terms
        if "Life + 70 years" in framework.get("duration", ""):
            # Assume creator lives 80 more years, then add 70
            end_date = start_date + timedelta(days=150 * 365)  # 150 years total
        else:
            # Default to 95 years
            end_date = start_date + timedelta(days=95 * 365)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "jurisdiction_based": True
        }
    
    async def _create_usage_restrictions(
        self, 
        rights_types: List[RightsType], 
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Create usage restrictions based on rights types and jurisdiction"""
        
        restrictions = {
            "commercial_use": RightsType.COMMERCIAL in rights_types,
            "distribution": RightsType.DISTRIBUTION in rights_types,
            "derivative_works": RightsType.DERIVATIVE in rights_types,
            "public_performance": RightsType.PERFORMANCE in rights_types,
            "reproduction": RightsType.REPRODUCTION in rights_types,
            "synchronization": RightsType.SYNCHRONIZATION in rights_types
        }
        
        jurisdiction_rules = self.jurisdiction_rules.get(jurisdiction, {})
        
        # Add jurisdiction-specific restrictions
        restrictions.update({
            "moral_rights_respected": jurisdiction_rules.get("moral_rights", False),
            "attribution_required": True,
            "resale_rights": jurisdiction_rules.get("resale_rights", False)
        })
        
        return restrictions
    
    async def _create_monetary_terms(
        self, 
        rights_types: List[RightsType], 
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Create monetary terms template"""
        
        base_rates = {
            RightsType.COMMERCIAL: 0.15,  # 15% royalty
            RightsType.DISTRIBUTION: 0.10,  # 10% royalty
            RightsType.PERFORMANCE: 0.08,   # 8% royalty
            RightsType.SYNCHRONIZATION: 0.12  # 12% royalty
        }
        
        monetary_terms = {
            "currency": "USD",
            "royalty_rates": {},
            "minimum_guarantees": {},
            "advance_payments": {},
            "payment_schedule": "quarterly"
        }
        
        for rights_type in rights_types:
            if rights_type in base_rates:
                monetary_terms["royalty_rates"][rights_type.value] = base_rates[rights_type]
        
        return monetary_terms
    
    async def _verify_licensing_rights(
        self, 
        content_id: str, 
        licensor_id: str
    ) -> Dict[str, Any]:
        """Verify that licensor has rights to license the content"""
        
        # Find rights for this content
        content_rights = None
        for rights in self.voice_rights.values():
            if rights.content_id == content_id and rights.status == RightsStatus.ACTIVE:
                content_rights = rights
                break
        
        if not content_rights:
            return {
                "can_license": False,
                "reason": "No active rights found for content"
            }
        
        # Check if licensor is rights holder or authorized
        if content_rights.rights_holder != licensor_id and content_rights.creator_id != licensor_id:
            return {
                "can_license": False,
                "reason": "Licensor is not the rights holder or creator"
            }
        
        # Check if licensing rights are included
        if RightsType.DISTRIBUTION not in content_rights.rights_types:
            return {
                "can_license": False,
                "reason": "Distribution rights not held"
            }
        
        return {
            "can_license": True,
            "rights_id": content_rights.rights_id,
            "rights_types": content_rights.rights_types
        }
    
    async def _create_license_terms(
        self,
        license_type: LicenseType,
        rights_granted: List[RightsType],
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create detailed license terms"""
        
        license_terms = {
            "exclusivity": template["exclusivity"],
            "transferable": template["transferable"],
            "sublicensing_allowed": template["sublicensing"],
            "rights_granted": [rg.value for rg in rights_granted],
            "quality_standards": "professional",
            "attribution_requirements": "as specified",
            "modification_rights": RightsType.DERIVATIVE in rights_granted,
            "performance_rights": RightsType.PERFORMANCE in rights_granted,
            "commercial_rights": RightsType.COMMERCIAL in rights_granted
        }
        
        # Add specific terms based on license type
        if license_type == LicenseType.CREATIVE_COMMONS:
            license_terms.update({
                "cc_license_version": "4.0",
                "share_alike": False,
                "commercial_use": RightsType.COMMERCIAL in rights_granted,
                "derivatives": RightsType.DERIVATIVE in rights_granted
            })
        
        return license_terms
    
    async def _generate_financial_terms(
        self,
        license_type: LicenseType,
        rights_granted: List[RightsType],
        duration_months: int
    ) -> Dict[str, Any]:
        """Generate financial terms for license"""
        
        if license_type == LicenseType.ROYALTY_FREE:
            # One-time payment
            base_price = 500 * len(rights_granted)  # $500 per right type
            return {
                "payment_type": "one_time",
                "total_amount": base_price * (1 + duration_months / 12),  # Scale by duration
                "currency": "USD",
                "payment_due": "upon_signing"
            }
        
        # Royalty-based
        royalty_rate = 0.10  # 10% base rate
        if RightsType.COMMERCIAL in rights_granted:
            royalty_rate += 0.05  # Additional 5% for commercial rights
        
        return {
            "payment_type": "royalty",
            "royalty_rate": royalty_rate,
            "minimum_guarantee": 1000,  # $1000 minimum
            "advance_payment": 500,     # $500 advance
            "currency": "USD",
            "payment_schedule": "quarterly",
            "revenue_threshold": 10000  # Start royalties after $10k revenue
        }
    
    async def _create_usage_limitations(
        self,
        license_type: LicenseType,
        rights_granted: List[RightsType]
    ) -> Dict[str, Any]:
        """Create usage limitations for license"""
        
        limitations = {
            "maximum_reproductions": "unlimited" if license_type in [LicenseType.EXCLUSIVE, LicenseType.ROYALTY_FREE] else 10000,
            "geographic_restrictions": [],
            "platform_restrictions": [],
            "format_restrictions": [],
            "quality_requirements": "minimum_44khz_16bit",
            "attribution_format": "Creator Name - Voice Content Title",
            "usage_reporting": license_type not in [LicenseType.ROYALTY_FREE, LicenseType.CREATIVE_COMMONS]
        }
        
        # Add restrictions based on rights granted
        if RightsType.COMMERCIAL not in rights_granted:
            limitations["commercial_use_prohibited"] = True
        
        if RightsType.DERIVATIVE not in rights_granted:
            limitations["modifications_prohibited"] = True
        
        return limitations
    
    async def _perform_compliance_check(
        self,
        content_id: str,
        license_type: LicenseType,
        territory: List[str]
    ) -> Dict[str, Any]:
        """Perform legal compliance check"""
        
        compliance_issues = []
        warnings = []
        
        # Check territorial compliance
        for country in territory:
            if country not in self.legal_frameworks:
                warnings.append(f"Unknown legal framework for {country}")
        
        # Check license type compliance
        if license_type == LicenseType.CREATIVE_COMMONS:
            # CC licenses have specific requirements
            if "commercial" in str(license_type).lower():
                warnings.append("Verify CC commercial license compatibility")
        
        # Check for conflicting existing licenses
        existing_licenses = [
            lic for lic in self.voice_licenses.values()
            if lic.content_id == content_id and lic.status == RightsStatus.ACTIVE
        ]
        
        for existing_license in existing_licenses:
            if existing_license.license_type == LicenseType.EXCLUSIVE:
                compliance_issues.append("Existing exclusive license prevents new licensing")
        
        compliance_score = 1.0 - (len(compliance_issues) * 0.5) - (len(warnings) * 0.1)
        
        return {
            "compliant": len(compliance_issues) == 0,
            "compliance_score": max(0.0, compliance_score),
            "issues": compliance_issues,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat(),
            "frameworks_checked": territory
        }
    
    async def _monitor_rights(self, rights_id: str):
        """Monitor rights for violations and expiry"""
        
        while self.rights_monitoring_enabled:
            try:
                if rights_id not in self.voice_rights:
                    break
                
                rights = self.voice_rights[rights_id]
                
                # Check for expiry
                if datetime.now() > rights.validity_period["end_date"]:
                    rights.status = RightsStatus.EXPIRED
                    self.logger.info(f"Rights {rights_id} expired")
                    break
                
                # Check for violations (simplified)
                violations = await self._scan_for_violations(rights)
                if violations:
                    self.logger.warning(f"Detected {len(violations)} violations for rights {rights_id}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring rights {rights_id}: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _start_license_monitoring(self, license_id: str):
        """Start monitoring for active license"""
        
        while self.rights_monitoring_enabled:
            try:
                if license_id not in self.voice_licenses:
                    break
                
                license_obj = self.voice_licenses[license_id]
                
                # Check for expiry
                if datetime.now() > license_obj.duration["end_date"]:
                    license_obj.status = RightsStatus.EXPIRED
                    self.logger.info(f"License {license_id} expired")
                    break
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring license {license_id}: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _scan_for_violations(self, rights: VoiceRights) -> List[RightsViolation]:
        """Scan for rights violations (simplified implementation)"""
        
        # In production, this would integrate with various monitoring services
        # and platforms to detect unauthorized usage
        
        violations = []
        
        # Simulate violation detection
        if len(self.rights_violations) < 5:  # Limit for demo
            # Random chance of detecting a violation
            import random
            if random.random() < 0.01:  # 1% chance per scan
                violation = RightsViolation(
                    violation_id=f"violation_{uuid.uuid4().hex[:8]}",
                    content_id=rights.content_id,
                    violator_info={"platform": "simulated_platform", "user": "unknown"},
                    violation_type="unauthorized_usage",
                    violation_details={"detected_usage": "commercial_without_license"},
                    evidence={"similarity_score": 0.95, "detection_method": "automated"},
                    severity="medium"
                )
                violations.append(violation)
                self.rights_violations.append(violation)
        
        return violations
    
    async def get_rights_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get rights status for content"""
        
        content_rights = None
        for rights in self.voice_rights.values():
            if rights.content_id == content_id:
                content_rights = rights
                break
        
        if not content_rights:
            return None
        
        # Get licenses for this content
        content_licenses = [
            lic for lic in self.voice_licenses.values()
            if lic.content_id == content_id
        ]
        
        # Get violations for this content
        content_violations = [
            v for v in self.rights_violations
            if v.content_id == content_id
        ]
        
        return {
            "content_id": content_id,
            "rights_id": content_rights.rights_id,
            "rights_holder": content_rights.rights_holder,
            "rights_types": [rt.value for rt in content_rights.rights_types],
            "status": content_rights.status.value,
            "jurisdiction": content_rights.jurisdiction,
            "validity_period": {
                k: v.isoformat() for k, v in content_rights.validity_period.items()
            },
            "active_licenses": len([l for l in content_licenses if l.status == RightsStatus.ACTIVE]),
            "total_licenses": len(content_licenses),
            "violations_detected": len(content_violations),
            "last_monitored": datetime.now().isoformat()
        }
    
    async def get_rights_analytics(self) -> Dict[str, Any]:
        """Get rights management analytics"""
        
        total_rights = len(self.voice_rights)
        total_licenses = len(self.voice_licenses)
        total_violations = len(self.rights_violations)
        
        # Rights by status
        rights_by_status = {}
        for status in RightsStatus:
            count = len([r for r in self.voice_rights.values() if r.status == status])
            rights_by_status[status.value] = count
        
        # Licenses by type
        licenses_by_type = {}
        for license_type in LicenseType:
            count = len([l for l in self.voice_licenses.values() if l.license_type == license_type])
            licenses_by_type[license_type.value] = count
        
        # Revenue analytics (simplified)
        total_revenue = 0
        for license_obj in self.voice_licenses.values():
            if license_obj.status == RightsStatus.ACTIVE:
                financial_terms = license_obj.financial_terms
                if financial_terms.get("payment_type") == "one_time":
                    total_revenue += financial_terms.get("total_amount", 0)
                elif financial_terms.get("payment_type") == "royalty":
                    total_revenue += financial_terms.get("minimum_guarantee", 0)
        
        return {
            "rights_summary": {
                "total_rights_registered": total_rights,
                "total_licenses_created": total_licenses,
                "total_violations_detected": total_violations,
                "rights_by_status": rights_by_status
            },
            "licensing_analytics": {
                "licenses_by_type": licenses_by_type,
                "active_licenses": len([l for l in self.voice_licenses.values() if l.status == RightsStatus.ACTIVE]),
                "estimated_total_revenue": total_revenue
            },
            "compliance_metrics": {
                "compliance_rate": 0.95,  # Simplified
                "average_compliance_score": 0.87,
                "jurisdictions_covered": len(self.legal_frameworks)
            },
            "violation_analytics": {
                "total_violations": total_violations,
                "resolved_violations": len([v for v in self.rights_violations if v.resolution_status == "resolved"]),
                "pending_violations": len([v for v in self.rights_violations if v.resolution_status == "pending"])
            }
        }