"""Voice Rights Management System

Comprehensive voice rights management system for creator voice content
rights, licensing, usage permissions, and legal compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import uuid
import json

class RightsType(Enum):
    """Voice content rights types"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SYNCHRONIZATION = "synchronization"

class LicenseType(Enum):
    """Voice content license types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"

class UsageScope(Enum):
    """Voice content usage scope"""
    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    PLATFORM_SPECIFIC = "platform_specific"

class RightsStatus(Enum):
    """Voice rights status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISPUTED = "disputed"
    SUSPENDED = "suspended"

@dataclass
class VoiceRights:
    """Voice content rights definition"""
    rights_id: str
    creator_id: str
    content_id: str
    rights_type: RightsType
    license_type: LicenseType
    usage_scope: UsageScope
    permissions: Dict[str, bool]
    restrictions: Dict[str, Any]
    territory: List[str]  # Countries/regions
    duration: Optional[timedelta]
    effective_date: datetime
    expiration_date: Optional[datetime]
    rights_holder: str
    licensee: Optional[str]
    royalty_rate: Optional[float]
    minimum_fee: Optional[float]
    status: RightsStatus = RightsStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LicenseAgreement:
    """Voice content license agreement"""
    agreement_id: str
    creator_id: str
    licensee_id: str
    content_ids: List[str]
    license_terms: Dict[str, Any]
    financial_terms: Dict[str, Any]
    usage_permissions: Dict[str, bool]
    usage_restrictions: Dict[str, Any]
    territory_restrictions: List[str]
    duration_months: Optional[int]
    start_date: datetime
    end_date: Optional[datetime]
    renewal_terms: Optional[Dict[str, Any]]
    termination_clauses: Dict[str, Any]
    agreement_status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class UsageReport:
    """Voice content usage report"""
    report_id: str
    content_id: str
    licensee_id: str
    usage_date: datetime
    usage_type: str
    platform: str
    audience_size: Optional[int]
    revenue_generated: Optional[float]
    territory: str
    usage_metadata: Dict[str, Any]
    compliance_status: str = "compliant"
    created_at: datetime = field(default_factory=datetime.now)

class VoiceRightsManager:
    """Voice Rights Management System"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Rights data storage
        self.voice_rights: Dict[str, VoiceRights] = {}
        self.license_agreements: Dict[str, LicenseAgreement] = {}
        self.usage_reports: Dict[str, List[UsageReport]] = {}
        self.rights_templates: Dict[str, Dict[str, Any]] = {}
        
        # Rights management configuration
        self.default_permissions = self._initialize_default_permissions()
        self.license_templates = self._initialize_license_templates()
        self.compliance_rules = self._initialize_compliance_rules()
        
        # Rights analytics and metrics
        self.rights_metrics = {
            "total_rights": 0,
            "active_licenses": 0,
            "revenue_generated": 0.0,
            "compliance_rate": 0.0
        }
        
        # Initialize rights management system
        self._initialize_rights_system()
    
    def _initialize_rights_system(self) -> None:
        """Initialize voice rights management system"""
        try:
            # Setup default rights configurations
            self._setup_default_rights_configurations()
            
            # Initialize compliance monitoring
            self._initialize_compliance_monitoring()
            
            # Setup automated renewals
            self._setup_automated_renewals()
            
            self.logger.info("Voice rights management system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize rights system: {e}")
            raise
    
    def _initialize_default_permissions(self) -> Dict[RightsType, Dict[str, bool]]:
        """Initialize default permissions for different rights types"""
        return {
            RightsType.COMMERCIAL: {
                "reproduction": True,
                "distribution": True,
                "public_performance": True,
                "modification": False,
                "resale": False,
                "sublicensing": False,
                "attribution_required": True
            },
            RightsType.NON_COMMERCIAL: {
                "reproduction": True,
                "distribution": True,
                "public_performance": True,
                "modification": True,
                "resale": False,
                "sublicensing": False,
                "attribution_required": True
            },
            RightsType.EDUCATIONAL: {
                "reproduction": True,
                "distribution": True,
                "public_performance": True,
                "modification": True,
                "resale": False,
                "sublicensing": False,
                "attribution_required": True
            },
            RightsType.PROMOTIONAL: {
                "reproduction": True,
                "distribution": True,
                "public_performance": True,
                "modification": False,
                "resale": False,
                "sublicensing": False,
                "attribution_required": True
            }
        }
    
    def _initialize_license_templates(self) -> Dict[LicenseType, Dict[str, Any]]:
        """Initialize license agreement templates"""
        return {
            LicenseType.EXCLUSIVE: {
                "exclusivity": True,
                "territory": ["global"],
                "duration_months": 12,
                "royalty_rate": 0.15,
                "minimum_fee": 1000.0,
                "renewal_option": True,
                "termination_notice_days": 30
            },
            LicenseType.NON_EXCLUSIVE: {
                "exclusivity": False,
                "territory": ["global"],
                "duration_months": 6,
                "royalty_rate": 0.10,
                "minimum_fee": 500.0,
                "renewal_option": True,
                "termination_notice_days": 15
            },
            LicenseType.ROYALTY_FREE: {
                "exclusivity": False,
                "territory": ["global"],
                "duration_months": None,  # Perpetual
                "royalty_rate": 0.0,
                "minimum_fee": 2000.0,
                "renewal_option": False,
                "termination_notice_days": 0
            }
        }
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance rules for rights management"""
        return {
            "usage_reporting": {
                "required": True,
                "frequency": "monthly",
                "grace_period_days": 30
            },
            "attribution": {
                "required": True,
                "format": "Creator: {creator_name} | Content: {content_title}",
                "placement": "visible"
            },
            "territory_restrictions": {
                "enforcement": "strict",
                "geo_blocking": True,
                "violation_penalty": 0.5
            },
            "modification_rights": {
                "approval_required": True,
                "derivative_works": False,
                "quality_standards": True
            }
        }
    
    async def create_voice_rights(
        self,
        creator_id: str,
        content_id: str,
        rights_type: RightsType,
        license_type: LicenseType = LicenseType.NON_EXCLUSIVE,
        usage_scope: UsageScope = UsageScope.GLOBAL,
        custom_permissions: Optional[Dict[str, bool]] = None,
        custom_restrictions: Optional[Dict[str, Any]] = None,
        territory: Optional[List[str]] = None,
        duration_months: Optional[int] = None
    ) -> VoiceRights:
        """Create voice content rights definition"""
        
        try:
            self.logger.info(f"Creating voice rights for content {content_id}")
            
            # Generate rights ID
            rights_id = str(uuid.uuid4())
            
            # Get default permissions and merge with custom
            default_perms = self.default_permissions.get(rights_type, {})
            permissions = {**default_perms, **(custom_permissions or {})}
            
            # Setup restrictions
            restrictions = custom_restrictions or {}
            
            # Set territory
            territory = territory or ["global"]
            
            # Calculate duration
            duration = timedelta(days=duration_months * 30) if duration_months else None
            expiration_date = datetime.now() + duration if duration else None
            
            # Create rights object
            voice_rights = VoiceRights(
                rights_id=rights_id,
                creator_id=creator_id,
                content_id=content_id,
                rights_type=rights_type,
                license_type=license_type,
                usage_scope=usage_scope,
                permissions=permissions,
                restrictions=restrictions,
                territory=territory,
                duration=duration,
                effective_date=datetime.now(),
                expiration_date=expiration_date,
                rights_holder=creator_id,
                licensee=None,
                royalty_rate=self.license_templates.get(license_type, {}).get("royalty_rate"),
                minimum_fee=self.license_templates.get(license_type, {}).get("minimum_fee")
            )
            
            # Store rights
            self.voice_rights[rights_id] = voice_rights
            
            # Update metrics
            self.rights_metrics["total_rights"] += 1
            
            return voice_rights
            
        except Exception as e:
            self.logger.error(f"Failed to create voice rights: {e}")
            raise
    
    async def create_license_agreement(
        self,
        creator_id: str,
        licensee_id: str,
        content_ids: List[str],
        license_type: LicenseType,
        financial_terms: Dict[str, Any],
        duration_months: Optional[int] = None,
        custom_terms: Optional[Dict[str, Any]] = None,
        territory_restrictions: Optional[List[str]] = None
    ) -> LicenseAgreement:
        """Create license agreement for voice content"""
        
        try:
            self.logger.info(f"Creating license agreement between {creator_id} and {licensee_id}")
            
            # Generate agreement ID
            agreement_id = str(uuid.uuid4())
            
            # Get license template
            template = self.license_templates.get(license_type, {})
            
            # Merge terms
            license_terms = {**template, **(custom_terms or {})}
            
            # Set usage permissions based on rights
            usage_permissions = {}
            for content_id in content_ids:
                content_rights = self._get_content_rights(content_id, creator_id)
                if content_rights:
                    usage_permissions.update(content_rights.permissions)
            
            # Setup restrictions
            usage_restrictions = {}
            territory_restrictions = territory_restrictions or ["global"]
            
            # Calculate dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_months * 30) if duration_months else None
            
            # Create agreement
            agreement = LicenseAgreement(
                agreement_id=agreement_id,
                creator_id=creator_id,
                licensee_id=licensee_id,
                content_ids=content_ids,
                license_terms=license_terms,
                financial_terms=financial_terms,
                usage_permissions=usage_permissions,
                usage_restrictions=usage_restrictions,
                territory_restrictions=territory_restrictions,
                duration_months=duration_months,
                start_date=start_date,
                end_date=end_date,
                termination_clauses={
                    "breach_termination": True,
                    "notice_period_days": template.get("termination_notice_days", 30),
                    "refund_policy": "pro_rated"
                }
            )
            
            # Store agreement
            self.license_agreements[agreement_id] = agreement
            
            # Update rights assignments
            await self._assign_rights_to_licensee(content_ids, creator_id, licensee_id)
            
            # Update metrics
            self.rights_metrics["active_licenses"] += 1
            
            return agreement
            
        except Exception as e:
            self.logger.error(f"Failed to create license agreement: {e}")
            raise
    
    def _get_content_rights(self, content_id: str, creator_id: str) -> Optional[VoiceRights]:
        """Get rights for specific content"""
        for rights in self.voice_rights.values():
            if rights.content_id == content_id and rights.creator_id == creator_id:
                return rights
        return None
    
    async def _assign_rights_to_licensee(
        self,
        content_ids: List[str],
        creator_id: str,
        licensee_id: str
    ) -> None:
        """Assign rights to licensee"""
        for content_id in content_ids:
            content_rights = self._get_content_rights(content_id, creator_id)
            if content_rights:
                content_rights.licensee = licensee_id
    
    async def validate_usage_rights(
        self,
        content_id: str,
        licensee_id: str,
        usage_type: str,
        territory: str,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate usage rights for voice content"""
        
        try:
            # Find relevant rights
            content_rights = None
            for rights in self.voice_rights.values():
                if (rights.content_id == content_id and 
                    rights.licensee == licensee_id and 
                    rights.status == RightsStatus.ACTIVE):
                    content_rights = rights
                    break
            
            if not content_rights:
                return {
                    "valid": False,
                    "reason": "No valid rights found for this content and licensee",
                    "violation_type": "unauthorized_usage"
                }
            
            # Check expiration
            if content_rights.expiration_date and datetime.now() > content_rights.expiration_date:
                return {
                    "valid": False,
                    "reason": "Rights have expired",
                    "violation_type": "expired_license",
                    "expiration_date": content_rights.expiration_date.isoformat()
                }
            
            # Check territory restrictions
            if territory not in content_rights.territory and "global" not in content_rights.territory:
                return {
                    "valid": False,
                    "reason": f"Usage not permitted in territory: {territory}",
                    "violation_type": "territory_violation",
                    "allowed_territories": content_rights.territory
                }
            
            # Check usage permissions
            usage_mapping = {
                "commercial": "reproduction",
                "broadcast": "public_performance",
                "streaming": "distribution",
                "promotional": "public_performance",
                "educational": "reproduction"
            }
            
            required_permission = usage_mapping.get(usage_type, "reproduction")
            if not content_rights.permissions.get(required_permission, False):
                return {
                    "valid": False,
                    "reason": f"Usage type '{usage_type}' not permitted",
                    "violation_type": "permission_violation",
                    "required_permission": required_permission
                }
            
            return {
                "valid": True,
                "rights_id": content_rights.rights_id,
                "license_type": content_rights.license_type.value,
                "permissions": content_rights.permissions,
                "restrictions": content_rights.restrictions,
                "royalty_rate": content_rights.royalty_rate,
                "attribution_required": content_rights.permissions.get("attribution_required", True)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate usage rights: {e}")
            raise
    
    async def report_content_usage(
        self,
        content_id: str,
        licensee_id: str,
        usage_date: datetime,
        usage_type: str,
        platform: str,
        audience_size: Optional[int] = None,
        revenue_generated: Optional[float] = None,
        territory: str = "global",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageReport:
        """Report voice content usage"""
        
        try:
            # Validate usage rights first
            validation_result = await self.validate_usage_rights(
                content_id, licensee_id, usage_type, territory, platform
            )
            
            if not validation_result["valid"]:
                raise ValueError(f"Invalid usage: {validation_result['reason']}")
            
            # Create usage report
            report = UsageReport(
                report_id=str(uuid.uuid4()),
                content_id=content_id,
                licensee_id=licensee_id,
                usage_date=usage_date,
                usage_type=usage_type,
                platform=platform,
                audience_size=audience_size,
                revenue_generated=revenue_generated,
                territory=territory,
                usage_metadata=metadata or {},
                compliance_status="compliant"
            )
            
            # Store usage report
            if content_id not in self.usage_reports:
                self.usage_reports[content_id] = []
            self.usage_reports[content_id].append(report)
            
            # Calculate royalties if applicable
            await self._calculate_and_record_royalties(report, validation_result)
            
            # Update metrics
            if revenue_generated:
                self.rights_metrics["revenue_generated"] += revenue_generated
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to report content usage: {e}")
            raise
    
    async def _calculate_and_record_royalties(
        self,
        usage_report: UsageReport,
        validation_result: Dict[str, Any]
    ) -> None:
        """Calculate and record royalties for usage"""
        
        royalty_rate = validation_result.get("royalty_rate", 0.0)
        revenue = usage_report.revenue_generated or 0.0
        
        if royalty_rate and revenue:
            royalty_amount = revenue * royalty_rate
            
            # Record royalty (would integrate with payment system)
            self.logger.info(f"Royalty calculated: ${royalty_amount:.2f} for usage {usage_report.report_id}")
    
    async def get_rights_status(
        self,
        creator_id: str,
        content_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get rights status for creator content"""
        
        # Filter rights for creator
        creator_rights = [
            rights for rights in self.voice_rights.values()
            if rights.creator_id == creator_id and 
            (not content_id or rights.content_id == content_id)
        ]
        
        # Calculate metrics
        total_rights = len(creator_rights)
        active_rights = len([r for r in creator_rights if r.status == RightsStatus.ACTIVE])
        expired_rights = len([r for r in creator_rights if r.status == RightsStatus.EXPIRED])
        
        # Get license agreements
        creator_agreements = [
            agreement for agreement in self.license_agreements.values()
            if agreement.creator_id == creator_id
        ]
        
        # Calculate revenue
        total_revenue = 0.0
        for agreement in creator_agreements:
            for content_id_in_agreement in agreement.content_ids:
                usage_reports = self.usage_reports.get(content_id_in_agreement, [])
                for report in usage_reports:
                    if report.revenue_generated:
                        total_revenue += report.revenue_generated
        
        return {
            "creator_id": creator_id,
            "content_id": content_id,
            "total_rights": total_rights,
            "active_rights": active_rights,
            "expired_rights": expired_rights,
            "active_licenses": len(creator_agreements),
            "total_revenue": total_revenue,
            "rights_breakdown": self._analyze_rights_breakdown(creator_rights),
            "compliance_status": await self._check_compliance_status(creator_id),
            "upcoming_expirations": await self._get_upcoming_expirations(creator_rights)
        }
    
    def _analyze_rights_breakdown(self, rights: List[VoiceRights]) -> Dict[str, int]:
        """Analyze rights breakdown by type"""
        breakdown = {}
        for right in rights:
            rights_type = right.rights_type.value
            breakdown[rights_type] = breakdown.get(rights_type, 0) + 1
        return breakdown
    
    async def _check_compliance_status(self, creator_id: str) -> Dict[str, Any]:
        """Check compliance status for creator"""
        
        # Get all usage reports for creator's content
        creator_content_ids = [
            rights.content_id for rights in self.voice_rights.values()
            if rights.creator_id == creator_id
        ]
        
        all_usage_reports = []
        for content_id in creator_content_ids:
            all_usage_reports.extend(self.usage_reports.get(content_id, []))
        
        # Calculate compliance metrics
        total_usage = len(all_usage_reports)
        compliant_usage = len([r for r in all_usage_reports if r.compliance_status == "compliant"])
        
        compliance_rate = compliant_usage / total_usage if total_usage > 0 else 1.0
        
        return {
            "compliance_rate": compliance_rate,
            "total_usage_reports": total_usage,
            "compliant_usage": compliant_usage,
            "violations": total_usage - compliant_usage,
            "status": "good" if compliance_rate >= 0.95 else "attention_needed"
        }
    
    async def _get_upcoming_expirations(self, rights: List[VoiceRights]) -> List[Dict[str, Any]]:
        """Get upcoming rights expirations"""
        
        upcoming = []
        now = datetime.now()
        
        for right in rights:
            if right.expiration_date and right.status == RightsStatus.ACTIVE:
                days_until_expiration = (right.expiration_date - now).days
                if 0 <= days_until_expiration <= 30:
                    upcoming.append({
                        "rights_id": right.rights_id,
                        "content_id": right.content_id,
                        "expiration_date": right.expiration_date.isoformat(),
                        "days_remaining": days_until_expiration,
                        "rights_type": right.rights_type.value,
                        "licensee": right.licensee
                    })
        
        return sorted(upcoming, key=lambda x: x["days_remaining"])
    
    async def _setup_default_rights_configurations(self) -> None:
        """Setup default rights configurations"""
        self.logger.info("Setting up default rights configurations")
        # Implementation would setup default configurations
    
    def _initialize_compliance_monitoring(self) -> None:
        """Initialize compliance monitoring system"""
        self.logger.info("Initializing compliance monitoring")
        # Implementation would setup compliance monitoring
    
    def _setup_automated_renewals(self) -> None:
        """Setup automated renewal system"""
        self.logger.info("Setting up automated renewals")
        # Implementation would setup automated renewal processes