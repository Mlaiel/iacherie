"""Rights Management - Advanced Digital Rights Management and Licensing
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, modification, distribution, or theft of this code 
without explicit written permission from the author is strictly prohibited
and will result in severe legal consequences under German and international law.

Email: mlaiel@live.de

This module provides comprehensive digital rights management including
licensing, royalty tracking, and automated rights enforcement.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import json
from decimal import Decimal

from .fingerprinting import AudioFingerprint

if TYPE_CHECKING:
    from .audio_manager import ContentType

logger = logging.getLogger(__name__)

class RightsLevel(Enum):
    """Rights management levels"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    GLOBAL = "global"

class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"
    PUBLISHING_LICENSE = "publishing_license"
    SAMPLING_LICENSE = "sampling_license"

class UsageType(Enum):
    """Types of content usage"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    SYNC_VIDEO = "sync_video"
    COMMERCIAL_USE = "commercial_use"
    EDUCATIONAL_USE = "educational_use"
    LIVE_PERFORMANCE = "live_performance"
    REMIXING = "remixing"
    SAMPLING = "sampling"
    COVER_VERSION = "cover_version"

class RoyaltyType(Enum):
    """Types of royalties"""
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    DIGITAL = "digital"
    PRINT = "print"
    NEIGHBORING = "neighboring"

class RightsStatus(Enum):
    """Status of rights"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    DISPUTED = "disputed"

@dataclass
class RightsHolder:
    """Rights holder information"""
    holder_id: str
    name: str
    email: str
    percentage_share: Decimal  # 0.00 to 100.00
    role: str  # composer, performer, producer, publisher, etc.
    contact_info: Dict[str, Any] = field(default_factory=dict)
    payment_info: Dict[str, Any] = field(default_factory=dict)
    territory: str = "worldwide"
    verification_status: str = "pending"  # pending, verified, rejected

@dataclass
class LicenseTerms:
    """License terms and conditions"""
    license_id: str
    license_type: LicenseType
    usage_types: List[UsageType]
    territory: str = "worldwide"
    duration_months: Optional[int] = None  # None for perpetual
    max_uses: Optional[int] = None  # None for unlimited
    royalty_rate: Decimal = Decimal('0.00')  # Percentage
    flat_fee: Decimal = Decimal('0.00')
    minimum_guarantee: Decimal = Decimal('0.00')
    advance_payment: Decimal = Decimal('0.00')
    restrictions: List[str] = field(default_factory=list)
    attribution_required: bool = True
    commercial_use_allowed: bool = True
    derivative_works_allowed: bool = False
    distribution_allowed: bool = True
    exclusive_territory: bool = False
    custom_terms: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RightsRegistration:
    """Rights registration record"""
    registration_id: str
    fingerprint_id: str
    content_title: str
    content_type: "ContentType"
    rights_holders: List[RightsHolder]
    license_terms: LicenseTerms
    registration_date: datetime = field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    status: RightsStatus = RightsStatus.PENDING
    verification_documents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    blockchain_hash: Optional[str] = None
    isrc_code: Optional[str] = None
    iswc_code: Optional[str] = None
    publishing_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoyaltyPayment:
    """Royalty payment record"""
    payment_id: str
    registration_id: str
    rights_holder_id: str
    royalty_type: RoyaltyType
    gross_amount: Decimal
    net_amount: Decimal
    currency: str = "USD"
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0
    revenue_source: str = ""  # platform or service
    tax_withheld: Decimal = Decimal('0.00')
    fees_deducted: Decimal = Decimal('0.00')
    payment_date: Optional[datetime] = None
    payment_method: str = ""
    payment_status: str = "pending"  # pending, processed, failed
    transaction_id: Optional[str] = None
    notes: str = ""

@dataclass
class UsageReport:
    """Content usage report"""
    report_id: str
    registration_id: str
    usage_type: UsageType
    platform: str
    usage_count: int
    revenue_generated: Decimal
    currency: str = "USD"
    report_period_start: datetime = field(default_factory=datetime.utcnow)
    report_period_end: datetime = field(default_factory=datetime.utcnow)
    territory: str = "worldwide"
    user_demographics: Dict[str, Any] = field(default_factory=dict)
    detailed_usage: List[Dict[str, Any]] = field(default_factory=list)
    verification_status: str = "pending"

@dataclass
class RightsResult:
    """Rights management operation result"""
    operation_id: str
    registration_id: Optional[str] = None
    success: bool = True
    message: str = ""
    rights_registration: Optional[RightsRegistration] = None
    license_granted: Optional[LicenseTerms] = None
    royalty_calculation: Optional[Dict[str, Decimal]] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RightsManager:
    """
    Advanced Digital Rights Management System
    
    Provides comprehensive rights management including:
    - Rights registration and verification
    - License generation and management
    - Royalty calculation and distribution
    - Usage tracking and reporting
    - Automated compliance monitoring
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        
        # Rights database (in production, use proper database)
        self.rights_registrations: Dict[str, RightsRegistration] = {}
        self.license_agreements: Dict[str, LicenseTerms] = {}
        self.royalty_payments: Dict[str, List[RoyaltyPayment]] = {}
        self.usage_reports: Dict[str, List[UsageReport]] = {}
        
        # Standard royalty rates (configurable)
        self.standard_rates = {
            RoyaltyType.MECHANICAL: Decimal('9.1'),  # cents per unit
            RoyaltyType.PERFORMANCE: Decimal('0.0022'),  # per stream
            RoyaltyType.SYNCHRONIZATION: Decimal('15.0'),  # percentage
            RoyaltyType.DIGITAL: Decimal('0.70'),  # per download
        }
        
        # Territory codes (ISO 3166-1 alpha-2)
        self.territories = {
            'US': 'United States',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'CA': 'Canada',
            'AU': 'Australia',
            'JP': 'Japan',
            'WW': 'Worldwide'
        }
        
        # Integration with external rights organizations
        self._setup_rights_organization_apis()
        
        self.logger.info("RightsManager initialized successfully")
    
    def _setup_rights_organization_apis(self):
        """Setup APIs for rights organizations"""
        # Mock setup for rights organizations like ASCAP, BMI, SESAC, etc.
        self.rights_orgs = {
            'ASCAP': {'api_key': self.config.get('ascap_api_key'), 'base_url': 'https://api.ascap.com'},
            'BMI': {'api_key': self.config.get('bmi_api_key'), 'base_url': 'https://api.bmi.com'},
            'SESAC': {'api_key': self.config.get('sesac_api_key'), 'base_url': 'https://api.sesac.com'},
            'GEMA': {'api_key': self.config.get('gema_api_key'), 'base_url': 'https://api.gema.de'},
        }
    
    async def register_rights(
        self,
        fingerprint: AudioFingerprint,
        user_id: str,
        content_type: "ContentType",
        metadata: Dict[str, Any],
        rights_holders: Optional[List[RightsHolder]] = None,
        license_terms: Optional[LicenseTerms] = None
    ) -> RightsResult:
        """
        Register rights for audio content
        
        Args:
            fingerprint: Audio fingerprint
            user_id: Primary rights holder ID
            content_type: Type of content
            metadata: Content metadata
            rights_holders: List of rights holders (optional)
            license_terms: License terms (optional)
            
        Returns:
            RightsResult with registration details
        """
        operation_id = str(uuid.uuid4())
        registration_id = str(uuid.uuid4())
        
        try:
            # Create default rights holder if none provided
            if not rights_holders:
                rights_holders = [
                    RightsHolder(
                        holder_id=user_id,
                        name=metadata.get('artist_name', 'Unknown'),
                        email=metadata.get('contact_email', ''),
                        percentage_share=Decimal('100.00'),
                        role='owner'
                    )
                ]
            
            # Create default license terms if none provided
            if not license_terms:
                license_terms = LicenseTerms(
                    license_id=str(uuid.uuid4()),
                    license_type=LicenseType.NON_EXCLUSIVE,
                    usage_types=[UsageType.STREAMING, UsageType.DOWNLOAD],
                    royalty_rate=Decimal('15.0')
                )
            
            # Validate rights holders percentages
            total_percentage = sum(holder.percentage_share for holder in rights_holders)
            if total_percentage != Decimal('100.00'):
                return RightsResult(
                    operation_id=operation_id,
                    success=False,
                    message=f"Rights holders percentages must total 100.00%, got {total_percentage}%"
                )
            
            # Create rights registration
            registration = RightsRegistration(
                registration_id=registration_id,
                fingerprint_id=fingerprint.fingerprint_id,
                content_title=metadata.get('title', 'Untitled'),
                content_type=content_type,
                rights_holders=rights_holders,
                license_terms=license_terms,
                metadata=metadata
            )
            
            # Import ContentType lazily to avoid circular import
            from .audio_manager import ContentType
            
            # Generate ISRC/ISWC codes if not provided
            if not registration.isrc_code and content_type == ContentType.MUSIC_TRACK:
                registration.isrc_code = await self._generate_isrc_code(registration)
            
            if not registration.iswc_code and content_type == ContentType.MUSIC_TRACK:
                registration.iswc_code = await self._generate_iswc_code(registration)
            
            # Register with blockchain if configured
            if self.config.get('blockchain_enabled'):
                registration.blockchain_hash = await self._register_on_blockchain(registration)
            
            # Store registration
            self.rights_registrations[registration_id] = registration
            self.license_agreements[license_terms.license_id] = license_terms
            
            # Initialize royalty tracking
            self.royalty_payments[registration_id] = []
            self.usage_reports[registration_id] = []
            
            # Submit to rights organizations
            await self._submit_to_rights_organizations(registration)
            
            result = RightsResult(
                operation_id=operation_id,
                registration_id=registration_id,
                success=True,
                message="Rights registered successfully",
                rights_registration=registration,
                license_granted=license_terms
            )
            
            self.logger.info(f"Rights registered successfully: {registration_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Rights registration failed: {str(e)}")
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message=f"Rights registration failed: {str(e)}"
            )
    
    async def _generate_isrc_code(self, registration: RightsRegistration) -> str:
        """Generate ISRC code for music track"""
        # ISRC format: CC-XXX-YY-NNNNN
        country = 'US'  # Default to US
        registrant = 'FAH'  # Fahed's code
        year = str(datetime.utcnow().year)[-2:]
        
        # Get next sequential number
        existing_codes = [
            reg.isrc_code for reg in self.rights_registrations.values()
            if reg.isrc_code and reg.isrc_code.startswith(f'{country}-{registrant}-{year}')
        ]
        
        next_number = len(existing_codes) + 1
        designation = f"{next_number:05d}"
        
        isrc_code = f"{country}-{registrant}-{year}-{designation}"
        
        self.logger.info(f"Generated ISRC code: {isrc_code}")
        
        return isrc_code
    
    async def _generate_iswc_code(self, registration: RightsRegistration) -> str:
        """Generate ISWC code for musical work"""
        # ISWC format: T-NNNNNNNNN-C
        # Simplified generation
        next_number = len(self.rights_registrations) + 1
        base_number = f"{next_number:09d}"
        
        # Calculate check digit (simplified)
        check_digit = str(sum(int(d) for d in base_number) % 10)
        
        iswc_code = f"T-{base_number}-{check_digit}"
        
        self.logger.info(f"Generated ISWC code: {iswc_code}")
        
        return iswc_code
    
    async def _register_on_blockchain(self, registration: RightsRegistration) -> str:
        """Register rights on blockchain"""
        # Mock blockchain registration
        import hashlib
        
        registration_data = {
            'registration_id': registration.registration_id,
            'fingerprint_id': registration.fingerprint_id,
            'rights_holders': [
                {
                    'holder_id': holder.holder_id,
                    'share': str(holder.percentage_share)
                }
                for holder in registration.rights_holders
            ],
            'timestamp': registration.registration_date.isoformat()
        }
        
        data_str = json.dumps(registration_data, sort_keys=True)
        blockchain_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        self.logger.info(f"Rights registered on blockchain: {blockchain_hash}")
        
        return f"0x{blockchain_hash}"
    
    async def _submit_to_rights_organizations(self, registration: RightsRegistration):
        """Submit registration to rights organizations"""
        # Mock submission to rights organizations
        for org_name, org_config in self.rights_orgs.items():
            try:
                # Simulate API call to rights organization
                submission_data = {
                    'title': registration.content_title,
                    'isrc': registration.isrc_code,
                    'iswc': registration.iswc_code,
                    'rights_holders': [
                        {
                            'name': holder.name,
                            'share': str(holder.percentage_share),
                            'role': holder.role
                        }
                        for holder in registration.rights_holders
                    ]
                }
                
                # Mock successful submission
                self.logger.info(f"Submitted to {org_name}: {registration.registration_id}")
                
            except Exception as e:
                self.logger.warning(f"Failed to submit to {org_name}: {str(e)}")
    
    async def calculate_royalties(
        self,
        registration_id: str,
        usage_data: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime
    ) -> RightsResult:
        """
        Calculate royalties based on usage data
        
        Args:
            registration_id: Rights registration ID
            usage_data: List of usage records
            period_start: Start of calculation period
            period_end: End of calculation period
            
        Returns:
            RightsResult with royalty calculations
        """
        operation_id = str(uuid.uuid4())
        
        try:
            registration = self.rights_registrations.get(registration_id)
            if not registration:
                return RightsResult(
                    operation_id=operation_id,
                    success=False,
                    message="Rights registration not found"
                )
            
            total_royalties = {}
            detailed_calculations = {}
            
            # Calculate royalties by type
            for usage in usage_data:
                usage_type = UsageType(usage.get('usage_type', 'streaming'))
                platform = usage.get('platform', 'unknown')
                count = usage.get('count', 0)
                revenue = Decimal(str(usage.get('revenue', 0)))
                
                # Determine royalty type based on usage type
                if usage_type in [UsageType.STREAMING, UsageType.DOWNLOAD]:
                    royalty_type = RoyaltyType.DIGITAL
                elif usage_type == UsageType.BROADCAST:
                    royalty_type = RoyaltyType.PERFORMANCE
                elif usage_type == UsageType.SYNC_VIDEO:
                    royalty_type = RoyaltyType.SYNCHRONIZATION
                else:
                    royalty_type = RoyaltyType.MECHANICAL
                
                # Calculate base royalty
                if royalty_type in [RoyaltyType.DIGITAL, RoyaltyType.MECHANICAL]:
                    base_royalty = self.standard_rates[royalty_type] * count
                else:
                    # Percentage-based royalties
                    rate = self.standard_rates.get(royalty_type, Decimal('10.0'))
                    base_royalty = revenue * (rate / 100)
                
                # Apply license terms
                license_royalty = base_royalty * (registration.license_terms.royalty_rate / 100)
                
                if royalty_type not in total_royalties:
                    total_royalties[royalty_type] = Decimal('0')
                    detailed_calculations[royalty_type] = []
                
                total_royalties[royalty_type] += license_royalty
                
                detailed_calculations[royalty_type].append({
                    'platform': platform,
                    'usage_count': count,
                    'base_revenue': str(revenue),
                    'base_royalty': str(base_royalty),
                    'license_royalty': str(license_royalty)
                })
            
            # Distribute royalties among rights holders
            holder_royalties = {}
            
            for holder in registration.rights_holders:
                holder_royalties[holder.holder_id] = {}
                
                for royalty_type, amount in total_royalties.items():
                    holder_share = amount * (holder.percentage_share / 100)
                    holder_royalties[holder.holder_id][royalty_type.value] = holder_share
                    
                    # Create royalty payment record
                    payment = RoyaltyPayment(
                        payment_id=str(uuid.uuid4()),
                        registration_id=registration_id,
                        rights_holder_id=holder.holder_id,
                        royalty_type=royalty_type,
                        gross_amount=holder_share,
                        net_amount=holder_share,  # Before taxes/fees
                        period_start=period_start,
                        period_end=period_end
                    )
                    
                    self.royalty_payments[registration_id].append(payment)
            
            result = RightsResult(
                operation_id=operation_id,
                registration_id=registration_id,
                success=True,
                message="Royalties calculated successfully",
                royalty_calculation={
                    'total_by_type': {k.value: str(v) for k, v in total_royalties.items()},
                    'by_rights_holder': {k: {kt: str(vt) for kt, vt in v.items()} 
                                       for k, v in holder_royalties.items()},
                    'detailed_calculations': {k.value: v for k, v in detailed_calculations.items()}
                }
            )
            
            self.logger.info(f"Royalties calculated: {registration_id}, Total: ${sum(total_royalties.values())}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Royalty calculation failed: {str(e)}")
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message=f"Royalty calculation failed: {str(e)}"
            )
    
    async def grant_license(
        self,
        registration_id: str,
        licensee_id: str,
        license_terms: LicenseTerms,
        custom_terms: Dict[str, Any] = None
    ) -> RightsResult:
        """Grant license for registered content"""
        operation_id = str(uuid.uuid4())
        
        try:
            registration = self.rights_registrations.get(registration_id)
            if not registration:
                return RightsResult(
                    operation_id=operation_id,
                    success=False,
                    message="Rights registration not found"
                )
            
            # Create new license with unique ID
            new_license = LicenseTerms(
                license_id=str(uuid.uuid4()),
                license_type=license_terms.license_type,
                usage_types=license_terms.usage_types,
                territory=license_terms.territory,
                duration_months=license_terms.duration_months,
                max_uses=license_terms.max_uses,
                royalty_rate=license_terms.royalty_rate,
                flat_fee=license_terms.flat_fee,
                minimum_guarantee=license_terms.minimum_guarantee,
                advance_payment=license_terms.advance_payment,
                restrictions=license_terms.restrictions,
                attribution_required=license_terms.attribution_required,
                commercial_use_allowed=license_terms.commercial_use_allowed,
                derivative_works_allowed=license_terms.derivative_works_allowed,
                distribution_allowed=license_terms.distribution_allowed,
                exclusive_territory=license_terms.exclusive_territory,
                custom_terms=custom_terms or {}
            )
            
            # Add licensee information to custom terms
            new_license.custom_terms.update({
                'licensee_id': licensee_id,
                'granted_date': datetime.utcnow().isoformat(),
                'registration_id': registration_id
            })
            
            # Store license
            self.license_agreements[new_license.license_id] = new_license
            
            result = RightsResult(
                operation_id=operation_id,
                registration_id=registration_id,
                success=True,
                message="License granted successfully",
                license_granted=new_license
            )
            
            self.logger.info(f"License granted: {new_license.license_id} for {registration_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"License granting failed: {str(e)}")
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message=f"License granting failed: {str(e)}"
            )
    
    def get_rights_registration(self, registration_id: str) -> Optional[RightsRegistration]:
        """Get rights registration by ID"""
        return self.rights_registrations.get(registration_id)
    
    def get_user_registrations(self, user_id: str) -> List[RightsRegistration]:
        """Get all rights registrations for user"""
        return [
            reg for reg in self.rights_registrations.values()
            if any(holder.holder_id == user_id for holder in reg.rights_holders)
        ]
    
    def get_royalty_payments(
        self,
        registration_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[RoyaltyPayment]:
        """Get royalty payments for registration"""
        payments = self.royalty_payments.get(registration_id, [])
        
        if start_date or end_date:
            filtered_payments = []
            for payment in payments:
                if start_date and payment.period_start < start_date:
                    continue
                if end_date and payment.period_end > end_date:
                    continue
                filtered_payments.append(payment)
            return filtered_payments
        
        return payments
    
    def get_license_agreements(
        self,
        registration_id: str
    ) -> List[LicenseTerms]:
        """Get all license agreements for registration"""
        return [
            license_terms for license_terms in self.license_agreements.values()
            if license_terms.custom_terms.get('registration_id') == registration_id
        ]
    
    async def verify_rights(
        self,
        fingerprint_id: str,
        usage_type: UsageType,
        user_id: str
    ) -> RightsResult:
        """Verify if user has rights for specific usage"""
        operation_id = str(uuid.uuid4())
        
        try:
            # Find registration by fingerprint
            registration = None
            for reg in self.rights_registrations.values():
                if reg.fingerprint_id == fingerprint_id:
                    registration = reg
                    break
            
            if not registration:
                return RightsResult(
                    operation_id=operation_id,
                    success=False,
                    message="No rights registration found for content"
                )
            
            # Check if user is a rights holder
            is_rights_holder = any(
                holder.holder_id == user_id 
                for holder in registration.rights_holders
            )
            
            if is_rights_holder:
                return RightsResult(
                    operation_id=operation_id,
                    registration_id=registration.registration_id,
                    success=True,
                    message="User is a rights holder"
                )
            
            # Check if user has valid license
            for license_terms in self.license_agreements.values():
                if (license_terms.custom_terms.get('registration_id') == registration.registration_id and
                    license_terms.custom_terms.get('licensee_id') == user_id and
                    usage_type in license_terms.usage_types):
                    
                    # Check license expiration
                    granted_date_str = license_terms.custom_terms.get('granted_date')
                    if granted_date_str and license_terms.duration_months:
                        granted_date = datetime.fromisoformat(granted_date_str.replace('Z', '+00:00'))
                        expiration_date = granted_date + timedelta(days=30 * license_terms.duration_months)
                        
                        if datetime.utcnow() > expiration_date:
                            return RightsResult(
                                operation_id=operation_id,
                                success=False,
                                message="License has expired"
                            )
                    
                    return RightsResult(
                        operation_id=operation_id,
                        registration_id=registration.registration_id,
                        success=True,
                        message="Valid license found",
                        license_granted=license_terms
                    )
            
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message="No valid rights or license found for usage"
            )
            
        except Exception as e:
            self.logger.error(f"Rights verification failed: {str(e)}")
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message=f"Rights verification failed: {str(e)}"
            )
    
    async def report_usage(
        self,
        registration_id: str,
        usage_data: Dict[str, Any]
    ) -> RightsResult:
        """Report content usage for royalty calculation"""
        operation_id = str(uuid.uuid4())
        
        try:
            registration = self.rights_registrations.get(registration_id)
            if not registration:
                return RightsResult(
                    operation_id=operation_id,
                    success=False,
                    message="Rights registration not found"
                )
            
            # Create usage report
            report = UsageReport(
                report_id=str(uuid.uuid4()),
                registration_id=registration_id,
                usage_type=UsageType(usage_data.get('usage_type', 'streaming')),
                platform=usage_data.get('platform', 'unknown'),
                usage_count=usage_data.get('count', 0),
                revenue_generated=Decimal(str(usage_data.get('revenue', 0))),
                territory=usage_data.get('territory', 'worldwide'),
                user_demographics=usage_data.get('demographics', {}),
                detailed_usage=usage_data.get('details', [])
            )
            
            # Store usage report
            if registration_id not in self.usage_reports:
                self.usage_reports[registration_id] = []
            
            self.usage_reports[registration_id].append(report)
            
            self.logger.info(f"Usage reported: {report.report_id} for {registration_id}")
            
            return RightsResult(
                operation_id=operation_id,
                registration_id=registration_id,
                success=True,
                message="Usage reported successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Usage reporting failed: {str(e)}")
            return RightsResult(
                operation_id=operation_id,
                success=False,
                message=f"Usage reporting failed: {str(e)}"
            )
