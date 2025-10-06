"""Voice Rights Manager - Intellectual Property & Licensing System
=================================================================

Enterprise rights management for voice content with licensing, royalties,
compliance tracking, and automated rights enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class RightsType(Enum):
    """Types of rights"""
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    DERIVATIVE_WORKS = "derivative_works"
    COMMERCIAL_USE = "commercial_use"
    STREAMING = "streaming"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"


class LicenseType(Enum):
    """License types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    PUBLIC_DOMAIN = "public_domain"


class RightsStatus(Enum):
    """Rights status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class ComplianceLevel(Enum):
    """Compliance levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


@dataclass
class VoiceRights:
    """Voice content rights"""
    rights_id: str
    voice_id: str
    owner_id: str
    rights_types: List[RightsType]
    territory: List[str] = field(default_factory=lambda: ["worldwide"])
    duration: Optional[timedelta] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: RightsStatus = RightsStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceLicense:
    """License agreement for voice usage"""
    license_id: str
    voice_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    permitted_uses: List[RightsType]
    territory: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    royalty_rate: float = 0.0
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    status: RightsStatus = RightsStatus.ACTIVE


@dataclass
class RightsViolation:
    """Rights violation record"""
    violation_id: str
    voice_id: str
    violator_id: Optional[str]
    violation_type: str
    description: str
    severity: ComplianceLevel
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_details: Optional[Dict[str, Any]] = None


@dataclass
class RightsManagementResult:
    """Result of rights operation"""
    success: bool
    operation: str
    voice_id: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class VoiceRightsManager:
    """
    Comprehensive voice rights management system
    """
    
    def __init__(self):
        """Initialize rights manager"""
        self.rights_registry = {}
        self.licenses = {}
        self.violations = []
        self.royalty_tracking = {}
        
        logger.info("⚖️ VoiceRightsManager initialized")
    
    async def register_rights(
        self,
        voice_id: str,
        owner_id: str,
        rights_types: List[RightsType],
        territory: List[str] = None,
        duration: Optional[timedelta] = None
    ) -> RightsManagementResult:
        """
        Register rights for voice content
        
        Args:
            voice_id: Voice identifier
            owner_id: Rights owner identifier
            rights_types: Types of rights to register
            territory: Geographic territories
            duration: Rights duration (None = perpetual)
            
        Returns:
            RightsManagementResult
        """
        try:
            rights_id = str(uuid.uuid4())
            territory = territory or ["worldwide"]
            
            expires_at = None
            if duration:
                expires_at = datetime.now() + duration
            
            rights = VoiceRights(
                rights_id=rights_id,
                voice_id=voice_id,
                owner_id=owner_id,
                rights_types=rights_types,
                territory=territory,
                duration=duration,
                expires_at=expires_at
            )
            
            self.rights_registry[rights_id] = rights
            
            logger.info(f"✅ Rights registered: {rights_id} for voice {voice_id}")
            
            return RightsManagementResult(
                success=True,
                operation="register_rights",
                voice_id=voice_id,
                message=f"Rights successfully registered: {rights_id}",
                details={'rights_id': rights_id, 'owner_id': owner_id}
            )
            
        except Exception as e:
            logger.error(f"Rights registration failed: {e}")
            return RightsManagementResult(
                success=False,
                operation="register_rights",
                voice_id=voice_id,
                message=f"Registration failed: {str(e)}"
            )
    
    async def issue_license(
        self,
        voice_id: str,
        licensee_id: str,
        licensor_id: str,
        license_type: LicenseType,
        permitted_uses: List[RightsType],
        territory: List[str],
        duration: timedelta,
        royalty_rate: float = 0.0
    ) -> RightsManagementResult:
        """
        Issue license for voice usage
        
        Args:
            voice_id: Voice identifier
            licensee_id: License recipient
            licensor_id: License issuer
            license_type: Type of license
            permitted_uses: Allowed usage types
            territory: Geographic scope
            duration: License duration
            royalty_rate: Royalty percentage (0.0-1.0)
            
        Returns:
            RightsManagementResult
        """
        try:
            # Verify licensor has rights
            if not await self._verify_ownership(voice_id, licensor_id):
                raise ValueError(f"Licensor {licensor_id} does not own rights to voice {voice_id}")
            
            license_id = str(uuid.uuid4())
            start_date = datetime.now()
            end_date = start_date + duration
            
            license = VoiceLicense(
                license_id=license_id,
                voice_id=voice_id,
                licensee_id=licensee_id,
                licensor_id=licensor_id,
                license_type=license_type,
                permitted_uses=permitted_uses,
                territory=territory,
                start_date=start_date,
                end_date=end_date,
                royalty_rate=royalty_rate
            )
            
            self.licenses[license_id] = license
            
            logger.info(f"✅ License issued: {license_id}")
            
            return RightsManagementResult(
                success=True,
                operation="issue_license",
                voice_id=voice_id,
                message=f"License successfully issued: {license_id}",
                details={
                    'license_id': license_id,
                    'licensee_id': licensee_id,
                    'end_date': end_date.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"License issuance failed: {e}")
            return RightsManagementResult(
                success=False,
                operation="issue_license",
                voice_id=voice_id,
                message=f"License issuance failed: {str(e)}"
            )
    
    async def verify_usage_rights(
        self,
        voice_id: str,
        user_id: str,
        intended_use: RightsType,
        territory: str
    ) -> Dict[str, Any]:
        """
        Verify if user has rights for intended usage
        
        Args:
            voice_id: Voice identifier
            user_id: User attempting usage
            intended_use: Intended usage type
            territory: Usage territory
            
        Returns:
            Verification result
        """
        try:
            # Check active licenses
            user_licenses = [
                lic for lic in self.licenses.values()
                if lic.voice_id == voice_id
                and lic.licensee_id == user_id
                and lic.status == RightsStatus.ACTIVE
                and (lic.end_date is None or lic.end_date > datetime.now())
            ]
            
            for license in user_licenses:
                if intended_use in license.permitted_uses:
                    if territory in license.territory or "worldwide" in license.territory:
                        return {
                            'authorized': True,
                            'license_id': license.license_id,
                            'license_type': license.license_type.value,
                            'expires_at': license.end_date.isoformat() if license.end_date else None
                        }
            
            return {
                'authorized': False,
                'reason': 'No valid license found for requested usage'
            }
            
        except Exception as e:
            logger.error(f"Rights verification failed: {e}")
            return {
                'authorized': False,
                'error': str(e)
            }
    
    async def track_royalties(
        self,
        voice_id: str,
        usage_type: RightsType,
        revenue: float,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Track royalty-generating usage
        
        Args:
            voice_id: Voice identifier
            usage_type: Type of usage
            revenue: Revenue generated
            metadata: Additional tracking data
            
        Returns:
            Royalty tracking result
        """
        try:
            # Find applicable licenses
            applicable_licenses = [
                lic for lic in self.licenses.values()
                if lic.voice_id == voice_id
                and usage_type in lic.permitted_uses
                and lic.status == RightsStatus.ACTIVE
            ]
            
            royalty_distributions = []
            
            for license in applicable_licenses:
                royalty_amount = revenue * license.royalty_rate
                
                distribution = {
                    'license_id': license.license_id,
                    'licensor_id': license.licensor_id,
                    'licensee_id': license.licensee_id,
                    'royalty_amount': royalty_amount,
                    'revenue': revenue,
                    'royalty_rate': license.royalty_rate,
                    'usage_type': usage_type.value,
                    'timestamp': datetime.now()
                }
                
                royalty_distributions.append(distribution)
                
                # Store in tracking
                if voice_id not in self.royalty_tracking:
                    self.royalty_tracking[voice_id] = []
                
                self.royalty_tracking[voice_id].append(distribution)
            
            logger.info(f"✅ Royalties tracked for voice {voice_id}: {len(royalty_distributions)} distributions")
            
            return {
                'success': True,
                'voice_id': voice_id,
                'total_revenue': revenue,
                'distributions': royalty_distributions,
                'total_royalties': sum(d['royalty_amount'] for d in royalty_distributions)
            }
            
        except Exception as e:
            logger.error(f"Royalty tracking failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_compliance(
        self,
        voice_id: str
    ) -> Dict[str, Any]:
        """
        Check compliance status for voice
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            Compliance report
        """
        try:
            # Get all rights for voice
            voice_rights = [
                r for r in self.rights_registry.values()
                if r.voice_id == voice_id
            ]
            
            # Get violations
            voice_violations = [
                v for v in self.violations
                if v.voice_id == voice_id and not v.resolved
            ]
            
            # Determine compliance level
            if not voice_violations:
                compliance = ComplianceLevel.COMPLIANT
            elif any(v.severity == ComplianceLevel.CRITICAL for v in voice_violations):
                compliance = ComplianceLevel.CRITICAL
            elif any(v.severity == ComplianceLevel.VIOLATION for v in voice_violations):
                compliance = ComplianceLevel.VIOLATION
            else:
                compliance = ComplianceLevel.WARNING
            
            return {
                'voice_id': voice_id,
                'compliance_level': compliance.value,
                'rights_registered': len(voice_rights) > 0,
                'active_licenses': len([l for l in self.licenses.values() if l.voice_id == voice_id and l.status == RightsStatus.ACTIVE]),
                'violations': len(voice_violations),
                'unresolved_violations': voice_violations,
                'requires_action': compliance in [ComplianceLevel.VIOLATION, ComplianceLevel.CRITICAL]
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                'voice_id': voice_id,
                'compliance_level': ComplianceLevel.WARNING.value,
                'error': str(e)
            }
    
    async def report_violation(
        self,
        voice_id: str,
        violation_type: str,
        description: str,
        severity: ComplianceLevel,
        violator_id: Optional[str] = None
    ) -> str:
        """Report rights violation"""
        violation_id = str(uuid.uuid4())
        
        violation = RightsViolation(
            violation_id=violation_id,
            voice_id=voice_id,
            violator_id=violator_id,
            violation_type=violation_type,
            description=description,
            severity=severity
        )
        
        self.violations.append(violation)
        
        logger.warning(f"⚠️ Violation reported: {violation_id} ({severity.value})")
        
        return violation_id
    
    async def resolve_violation(
        self,
        violation_id: str,
        resolution_details: Dict[str, Any]
    ) -> bool:
        """Resolve reported violation"""
        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.resolved = True
                violation.resolution_details = resolution_details
                logger.info(f"✅ Violation resolved: {violation_id}")
                return True
        
        return False
    
    async def get_royalty_report(
        self,
        voice_id: str,
        time_period: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Get royalty report for voice"""
        if voice_id not in self.royalty_tracking:
            return {
                'voice_id': voice_id,
                'total_revenue': 0,
                'total_royalties': 0,
                'distributions': []
            }
        
        distributions = self.royalty_tracking[voice_id]
        
        if time_period:
            start, end = time_period
            distributions = [
                d for d in distributions
                if start <= d['timestamp'] <= end
            ]
        
        total_revenue = sum(d['revenue'] for d in distributions)
        total_royalties = sum(d['royalty_amount'] for d in distributions)
        
        # Group by licensor
        by_licensor = {}
        for d in distributions:
            licensor = d['licensor_id']
            if licensor not in by_licensor:
                by_licensor[licensor] = {
                    'total_royalties': 0,
                    'distributions': []
                }
            by_licensor[licensor]['total_royalties'] += d['royalty_amount']
            by_licensor[licensor]['distributions'].append(d)
        
        return {
            'voice_id': voice_id,
            'total_revenue': total_revenue,
            'total_royalties': total_royalties,
            'num_distributions': len(distributions),
            'by_licensor': by_licensor,
            'distributions': distributions
        }
    
    # Private methods
    
    async def _verify_ownership(
        self,
        voice_id: str,
        user_id: str
    ) -> bool:
        """Verify user owns rights to voice"""
        for rights in self.rights_registry.values():
            if rights.voice_id == voice_id and rights.owner_id == user_id:
                if rights.status == RightsStatus.ACTIVE:
                    if rights.expires_at is None or rights.expires_at > datetime.now():
                        return True
        return False
