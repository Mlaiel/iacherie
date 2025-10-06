"""Voice Copyright Validator - Copyright Validation & Compliance
================================================================

Advanced copyright validation system for voice content including
ownership verification, license management, and compliance checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import hashlib

logger = logging.getLogger(__name__)

class CopyrightStatus(Enum):
    """Copyright status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    DISPUTED = "disputed"
    EXPIRED = "expired"

class CopyrightType(Enum):
    """Copyright types"""
    ORIGINAL = "original"
    LICENSED = "licensed"
    PUBLIC_DOMAIN = "public_domain"
    FAIR_USE = "fair_use"
    CREATIVE_COMMONS = "creative_commons"

class ValidationMethod(Enum):
    """Validation methods"""
    FINGERPRINT = "fingerprint"
    METADATA = "metadata"
    DATABASE = "database"
    BLOCKCHAIN = "blockchain"
    MANUAL = "manual"

class ComplianceLevel(Enum):
    """Compliance levels"""
    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

@dataclass
class CopyrightRecord:
    """Copyright record"""
    record_id: str
    content_id: str
    owner_id: str
    copyright_type: CopyrightType
    registration_date: datetime
    expiration_date: Optional[datetime]
    jurisdiction: str
    proof_of_ownership: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Copyright validation result"""
    validation_id: str
    content_id: str
    status: CopyrightStatus
    copyright_type: CopyrightType
    owner_verified: bool
    license_valid: bool
    compliance_level: ComplianceLevel
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.now)

@dataclass
class CopyrightClaim:
    """Copyright claim"""
    claim_id: str
    content_id: str
    claimant_id: str
    claim_type: str  # ownership, infringement, license_violation
    evidence: List[str]
    status: str  # pending, approved, rejected
    filed_at: datetime
    resolved_at: Optional[datetime] = None

class VoiceCopyrightValidator:
    """
    Voice Copyright Validator
    
    Provides comprehensive copyright validation including:
    - Ownership verification
    - License validation
    - Compliance checking
    - Copyright registration
    - Dispute resolution
    """
    
    def __init__(self):
        """Initialize copyright validator"""
        self.copyright_records: Dict[str, CopyrightRecord] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.claims: Dict[str, CopyrightClaim] = {}
        self.copyright_database: Dict[str, str] = {}  # content_hash -> owner_id
        
        logger.info("©️ VoiceCopyrightValidator initialized")
    
    async def register_copyright(
        self,
        content_id: str,
        owner_id: str,
        copyright_type: CopyrightType,
        jurisdiction: str = "US",
        expiration_years: Optional[int] = None
    ) -> CopyrightRecord:
        """Register copyright for voice content"""
        try:
            # Generate proof of ownership
            proof = self._generate_proof_of_ownership(content_id, owner_id)
            
            # Calculate expiration date
            expiration_date = None
            if expiration_years:
                expiration_date = datetime.now().replace(
                    year=datetime.now().year + expiration_years
                )
            
            record = CopyrightRecord(
                record_id=str(uuid.uuid4()),
                content_id=content_id,
                owner_id=owner_id,
                copyright_type=copyright_type,
                registration_date=datetime.now(),
                expiration_date=expiration_date,
                jurisdiction=jurisdiction,
                proof_of_ownership=proof
            )
            
            self.copyright_records[record.record_id] = record
            
            # Store in database
            content_hash = self._hash_content(content_id)
            self.copyright_database[content_hash] = owner_id
            
            logger.info(f"©️ Registered copyright for content {content_id}")
            return record
            
        except Exception as e:
            logger.error(f"Failed to register copyright: {e}")
            raise
    
    async def validate_copyright(
        self,
        content_id: str,
        claimed_owner_id: str,
        validation_method: ValidationMethod = ValidationMethod.DATABASE
    ) -> ValidationResult:
        """Validate copyright for content"""
        try:
            # Check if copyright exists
            record = await self._find_copyright_record(content_id)
            
            if not record:
                result = ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    content_id=content_id,
                    status=CopyrightStatus.INVALID,
                    copyright_type=CopyrightType.ORIGINAL,
                    owner_verified=False,
                    license_valid=False,
                    compliance_level=ComplianceLevel.NON_COMPLIANT,
                    issues=["No copyright record found"]
                )
            else:
                # Validate ownership
                owner_verified = record.owner_id == claimed_owner_id
                
                # Check expiration
                license_valid = True
                if record.expiration_date and record.expiration_date < datetime.now():
                    license_valid = False
                
                # Determine status
                if owner_verified and license_valid:
                    status = CopyrightStatus.VALID
                    compliance_level = ComplianceLevel.FULL
                else:
                    status = CopyrightStatus.INVALID
                    compliance_level = ComplianceLevel.NON_COMPLIANT
                
                # Collect issues
                issues = []
                if not owner_verified:
                    issues.append("Owner verification failed")
                if not license_valid:
                    issues.append("Copyright has expired")
                
                result = ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    content_id=content_id,
                    status=status,
                    copyright_type=record.copyright_type,
                    owner_verified=owner_verified,
                    license_valid=license_valid,
                    compliance_level=compliance_level,
                    issues=issues
                )
            
            self.validation_results[result.validation_id] = result
            
            logger.info(f"✅ Validated copyright: {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to validate copyright: {e}")
            raise
    
    async def check_compliance(
        self,
        content_id: str,
        usage_type: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Check copyright compliance for content usage"""
        try:
            record = await self._find_copyright_record(content_id)
            
            if not record:
                return {
                    'compliant': False,
                    'issues': ['No copyright record found'],
                    'recommendations': ['Register copyright before distribution']
                }
            
            issues = []
            recommendations = []
            
            # Check license type compatibility
            if record.copyright_type == CopyrightType.LICENSED:
                if usage_type == 'commercial':
                    issues.append('Commercial use may require additional licensing')
                    recommendations.append('Verify commercial license terms')
            
            # Check platform restrictions
            for platform in platforms:
                if not await self._check_platform_compliance(record, platform):
                    issues.append(f'Platform {platform} may have restrictions')
                    recommendations.append(f'Review {platform} copyright policies')
            
            # Check expiration
            if record.expiration_date and record.expiration_date < datetime.now():
                issues.append('Copyright has expired')
                recommendations.append('Renew copyright registration')
            
            compliance_level = ComplianceLevel.FULL
            if issues:
                compliance_level = ComplianceLevel.PARTIAL if len(issues) < 3 else ComplianceLevel.NON_COMPLIANT
            
            return {
                'compliant': len(issues) == 0,
                'compliance_level': compliance_level.value,
                'issues': issues,
                'recommendations': recommendations,
                'copyright_type': record.copyright_type.value,
                'owner_id': record.owner_id
            }
            
        except Exception as e:
            logger.error(f"Failed to check compliance: {e}")
            raise
    
    async def file_copyright_claim(
        self,
        content_id: str,
        claimant_id: str,
        claim_type: str,
        evidence: List[str]
    ) -> CopyrightClaim:
        """File a copyright claim"""
        try:
            claim = CopyrightClaim(
                claim_id=str(uuid.uuid4()),
                content_id=content_id,
                claimant_id=claimant_id,
                claim_type=claim_type,
                evidence=evidence,
                status='pending',
                filed_at=datetime.now()
            )
            
            self.claims[claim.claim_id] = claim
            
            logger.info(f"⚖️ Filed copyright claim: {claim.claim_id}")
            return claim
            
        except Exception as e:
            logger.error(f"Failed to file claim: {e}")
            raise
    
    async def resolve_claim(
        self,
        claim_id: str,
        approved: bool,
        resolution_notes: str = ""
    ) -> CopyrightClaim:
        """Resolve a copyright claim"""
        try:
            claim = self.claims.get(claim_id)
            if not claim:
                raise ValueError(f"Claim {claim_id} not found")
            
            claim.status = 'approved' if approved else 'rejected'
            claim.resolved_at = datetime.now()
            
            if approved:
                # Update copyright record if needed
                record = await self._find_copyright_record(claim.content_id)
                if record and claim.claim_type == 'ownership':
                    record.owner_id = claim.claimant_id
            
            logger.info(f"✅ Resolved claim {claim_id}: {claim.status}")
            return claim
            
        except Exception as e:
            logger.error(f"Failed to resolve claim: {e}")
            raise
    
    async def get_copyright_info(
        self,
        content_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get copyright information for content"""
        try:
            record = await self._find_copyright_record(content_id)
            
            if not record:
                return None
            
            return {
                'record_id': record.record_id,
                'content_id': record.content_id,
                'owner_id': record.owner_id,
                'copyright_type': record.copyright_type.value,
                'registration_date': record.registration_date.isoformat(),
                'expiration_date': record.expiration_date.isoformat() if record.expiration_date else None,
                'jurisdiction': record.jurisdiction,
                'valid': not record.expiration_date or record.expiration_date > datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to get copyright info: {e}")
            return None
    
    def _generate_proof_of_ownership(self, content_id: str, owner_id: str) -> str:
        """Generate proof of ownership hash"""
        data = f"{content_id}:{owner_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _hash_content(self, content_id: str) -> str:
        """Generate content hash for database lookup"""
        return hashlib.sha256(content_id.encode()).hexdigest()
    
    async def _find_copyright_record(self, content_id: str) -> Optional[CopyrightRecord]:
        """Find copyright record by content ID"""
        for record in self.copyright_records.values():
            if record.content_id == content_id:
                return record
        return None
    
    async def _check_platform_compliance(
        self,
        record: CopyrightRecord,
        platform: str
    ) -> bool:
        """Check if copyright is compliant with platform policies"""
        # Mock implementation - would check real platform policies
        restricted_platforms = {
            CopyrightType.FAIR_USE: ['commercial_streaming'],
            CopyrightType.CREATIVE_COMMONS: []
        }
        
        return platform not in restricted_platforms.get(record.copyright_type, [])


logger.info("©️ Voice Copyright Validator module initialized")
