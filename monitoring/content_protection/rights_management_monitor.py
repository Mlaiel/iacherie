"""
Ainflue Platform - Rights Management Monitor
============================================

Comprehensive automated rights management monitoring system for tracking
licenses, permissions, royalties, and compliance across digital content
distribution and monetization workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from decimal import Decimal
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Types of content licenses."""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"
    SAMPLING_LICENSE = "sampling_license"
    DERIVATIVE_WORK = "derivative_work"

class RightsStatus(Enum):
    """Rights management status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"
    DISPUTED = "disputed"
    UNDER_REVIEW = "under_review"
    SUSPENDED = "suspended"

class RoyaltyType(Enum):
    """Types of royalty payments."""
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    DIGITAL_STREAMING = "digital_streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    PUBLIC_PERFORMANCE = "public_performance"
    DERIVATIVE = "derivative"

@dataclass
class RightsHolder:
    """Rights holder information."""
    holder_id: str
    name: str
    entity_type: str  # individual, company, organization
    contact_email: str
    territory: str
    tax_id: Optional[str] = None
    payment_info: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False

@dataclass
class LicenseAgreement:
    """License agreement details."""
    license_id: str
    content_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    rights_granted: List[str]
    territories: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    royalty_rate: Decimal
    royalty_type: RoyaltyType
    minimum_guarantee: Decimal
    advance_payment: Decimal
    terms_conditions: str
    status: RightsStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RoyaltyPayment:
    """Royalty payment record."""
    payment_id: str
    license_id: str
    rights_holder_id: str
    royalty_type: RoyaltyType
    amount: Decimal
    currency: str
    calculation_period_start: datetime
    calculation_period_end: datetime
    usage_count: int
    revenue_share_percentage: Decimal
    gross_revenue: Decimal
    deductions: Decimal
    net_amount: Decimal
    payment_date: Optional[datetime]
    payment_status: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UsageReport:
    """Content usage tracking for royalty calculations."""
    usage_id: str
    content_id: str
    license_id: str
    platform: str
    usage_type: str  # stream, download, broadcast, etc.
    usage_count: int
    revenue_generated: Decimal
    territory: str
    timestamp: datetime
    user_demographics: Dict[str, Any] = field(default_factory=dict)

class RightsManagementMonitor:
    """
    Enterprise rights management monitoring system.
    
    Features:
    - Automated license tracking and compliance monitoring
    - Real-time royalty calculation and distribution
    - Rights holder verification and payment management
    - Usage analytics and revenue optimization
    - Territory-specific rights enforcement
    - Compliance reporting and audit trails
    - Integration with payment systems and legal frameworks
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rights_holders: Dict[str, RightsHolder] = {}
        self.license_agreements: Dict[str, LicenseAgreement] = {}
        self.royalty_payments: deque = deque(maxlen=50000)
        self.usage_reports: deque = deque(maxlen=100000)
        self.compliance_rules = self._initialize_compliance_rules()
        self.royalty_calculators = self._initialize_royalty_calculators()
        
        logger.info("Rights Management Monitor initialized")
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance rules for different territories and license types."""
        return {
            'territory_rules': {
                'US': {
                    'mechanical_rate_per_stream': Decimal('0.00091'),
                    'performance_rate_percentage': Decimal('0.15'),
                    'tax_withholding': Decimal('0.30'),
                    'reporting_frequency_days': 30
                },
                'EU': {
                    'mechanical_rate_per_stream': Decimal('0.00084'),
                    'performance_rate_percentage': Decimal('0.12'),
                    'vat_rate': Decimal('0.20'),
                    'gdpr_compliance_required': True,
                    'reporting_frequency_days': 30
                },
                'UK': {
                    'mechanical_rate_per_stream': Decimal('0.00089'),
                    'performance_rate_percentage': Decimal('0.13'),
                    'prs_licensing_required': True,
                    'reporting_frequency_days': 30
                },
                'DE': {
                    'mechanical_rate_per_stream': Decimal('0.00095'),
                    'performance_rate_percentage': Decimal('0.11'),
                    'gema_licensing_required': True,
                    'reporting_frequency_days': 30
                }
            },
            'license_requirements': {
                LicenseType.SYNC_LICENSE: {
                    'requires_master_rights': True,
                    'requires_publishing_rights': True,
                    'territory_specific': True
                },
                LicenseType.MECHANICAL_LICENSE: {
                    'compulsory_license_available': True,
                    'statutory_rate_applicable': True
                },
                LicenseType.PERFORMANCE_LICENSE: {
                    'pro_registration_required': True,
                    'venue_reporting_required': True
                }
            }
        }
    
    def _initialize_royalty_calculators(self) -> Dict[RoyaltyType, Any]:
        """Initialize royalty calculation engines for different royalty types."""
        return {
            RoyaltyType.DIGITAL_STREAMING: self._calculate_streaming_royalties,
            RoyaltyType.MECHANICAL: self._calculate_mechanical_royalties,
            RoyaltyType.PERFORMANCE: self._calculate_performance_royalties,
            RoyaltyType.SYNCHRONIZATION: self._calculate_sync_royalties,
            RoyaltyType.DOWNLOAD: self._calculate_download_royalties
        }
    
    async def register_rights_holder(self, name: str, entity_type: str,
                                   contact_email: str, territory: str,
                                   tax_id: Optional[str] = None,
                                   payment_info: Optional[Dict[str, Any]] = None) -> str:
        """Register a new rights holder in the system."""
        holder_id = str(uuid.uuid4())
        
        rights_holder = RightsHolder(
            holder_id=holder_id,
            name=name,
            entity_type=entity_type,
            contact_email=contact_email,
            territory=territory,
            tax_id=tax_id,
            payment_info=payment_info or {},
            verified=False  # Requires verification process
        )
        
        self.rights_holders[holder_id] = rights_holder
        
        logger.info(f"Rights holder registered: {holder_id} - {name} ({territory})")
        return holder_id
    
    async def create_license_agreement(self, content_id: str, licensee_id: str,
                                     licensor_id: str, license_type: LicenseType,
                                     rights_granted: List[str], territories: List[str],
                                     start_date: datetime, end_date: Optional[datetime],
                                     royalty_rate: Decimal, royalty_type: RoyaltyType,
                                     terms_conditions: str,
                                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new license agreement."""
        license_id = str(uuid.uuid4())
        
        # Validate rights holders exist
        if licensee_id not in self.rights_holders:
            raise ValueError(f"Licensee not found: {licensee_id}")
        if licensor_id not in self.rights_holders:
            raise ValueError(f"Licensor not found: {licensor_id}")
        
        license_agreement = LicenseAgreement(
            license_id=license_id,
            content_id=content_id,
            licensee_id=licensee_id,
            licensor_id=licensor_id,
            license_type=license_type,
            rights_granted=rights_granted,
            territories=territories,
            start_date=start_date,
            end_date=end_date,
            royalty_rate=royalty_rate,
            royalty_type=royalty_type,
            minimum_guarantee=Decimal('0'),
            advance_payment=Decimal('0'),
            terms_conditions=terms_conditions,
            status=RightsStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        self.license_agreements[license_id] = license_agreement
        
        # Check for compliance issues
        await self._validate_license_compliance(license_agreement)
        
        logger.info(f"License agreement created: {license_id} "
                   f"({license_type.value}, {royalty_type.value})")
        
        return license_id
    
    async def record_content_usage(self, content_id: str, platform: str,
                                 usage_type: str, usage_count: int,
                                 revenue_generated: Decimal, territory: str,
                                 user_demographics: Optional[Dict[str, Any]] = None) -> str:
        """Record content usage for royalty calculation."""
        usage_id = str(uuid.uuid4())
        
        # Find applicable license
        applicable_license = await self._find_applicable_license(
            content_id, platform, territory, usage_type
        )
        
        usage_report = UsageReport(
            usage_id=usage_id,
            content_id=content_id,
            license_id=applicable_license.license_id if applicable_license else "",
            platform=platform,
            usage_type=usage_type,
            usage_count=usage_count,
            revenue_generated=revenue_generated,
            territory=territory,
            timestamp=datetime.utcnow(),
            user_demographics=user_demographics or {}
        )
        
        self.usage_reports.append(usage_report)
        
        # Trigger royalty calculation if license exists
        if applicable_license:
            await self._calculate_and_record_royalties(usage_report, applicable_license)
        
        logger.debug(f"Usage recorded: {usage_id} - {usage_count} {usage_type}s "
                    f"on {platform} ({territory})")
        
        return usage_id
    
    async def _find_applicable_license(self, content_id: str, platform: str,
                                     territory: str, usage_type: str) -> Optional[LicenseAgreement]:
        """Find the applicable license for content usage."""
        current_time = datetime.utcnow()
        
        applicable_licenses = []
        for license_agreement in self.license_agreements.values():
            if (license_agreement.content_id == content_id and
                license_agreement.status == RightsStatus.ACTIVE and
                license_agreement.start_date <= current_time and
                (not license_agreement.end_date or license_agreement.end_date >= current_time) and
                territory in license_agreement.territories):
                
                # Check if rights cover this usage type
                if self._usage_type_covered_by_rights(usage_type, license_agreement.rights_granted):
                    applicable_licenses.append(license_agreement)
        
        # Return most specific license (prefer exclusive over non-exclusive)
        if applicable_licenses:
            exclusive_licenses = [l for l in applicable_licenses if l.license_type == LicenseType.EXCLUSIVE]
            return exclusive_licenses[0] if exclusive_licenses else applicable_licenses[0]
        
        return None
    
    def _usage_type_covered_by_rights(self, usage_type: str, rights_granted: List[str]) -> bool:
        """Check if usage type is covered by granted rights."""
        usage_rights_mapping = {
            'stream': ['streaming', 'digital_streaming', 'performance'],
            'download': ['download', 'digital_download', 'mechanical'],
            'broadcast': ['broadcast', 'performance', 'public_performance'],
            'sync': ['synchronization', 'sync', 'visual_media'],
            'remix': ['derivative_work', 'adaptation', 'remix'],
            'sample': ['sampling', 'interpolation', 'excerpt']
        }
        
        required_rights = usage_rights_mapping.get(usage_type, [usage_type])
        return any(right in rights_granted for right in required_rights)
    
    async def _calculate_and_record_royalties(self, usage_report: UsageReport,
                                            license_agreement: LicenseAgreement):
        """Calculate and record royalties for content usage."""
        calculator = self.royalty_calculators.get(license_agreement.royalty_type)
        if not calculator:
            logger.warning(f"No calculator for royalty type: {license_agreement.royalty_type}")
            return
        
        royalty_amount = await calculator(usage_report, license_agreement)
        
        if royalty_amount > 0:
            payment_id = str(uuid.uuid4())
            
            royalty_payment = RoyaltyPayment(
                payment_id=payment_id,
                license_id=license_agreement.license_id,
                rights_holder_id=license_agreement.licensor_id,
                royalty_type=license_agreement.royalty_type,
                amount=royalty_amount,
                currency="USD",  # Default currency
                calculation_period_start=usage_report.timestamp,
                calculation_period_end=usage_report.timestamp,
                usage_count=usage_report.usage_count,
                revenue_share_percentage=license_agreement.royalty_rate,
                gross_revenue=usage_report.revenue_generated,
                deductions=Decimal('0'),
                net_amount=royalty_amount,
                payment_date=None,  # Will be set when payment is processed
                payment_status="pending",
                metadata={
                    'usage_id': usage_report.usage_id,
                    'platform': usage_report.platform,
                    'territory': usage_report.territory
                }
            )
            
            self.royalty_payments.append(royalty_payment)
            
            logger.info(f"Royalty calculated: {payment_id} - ${royalty_amount} "
                       f"for {license_agreement.royalty_type.value}")
    
    async def _calculate_streaming_royalties(self, usage_report: UsageReport,
                                           license_agreement: LicenseAgreement) -> Decimal:
        """Calculate streaming royalties."""
        territory_rules = self.compliance_rules['territory_rules'].get(
            usage_report.territory, self.compliance_rules['territory_rules']['US']
        )
        
        per_stream_rate = territory_rules.get('mechanical_rate_per_stream', Decimal('0.00091'))
        royalty_share = license_agreement.royalty_rate
        
        total_royalties = per_stream_rate * usage_report.usage_count * royalty_share
        return total_royalties
    
    async def _calculate_mechanical_royalties(self, usage_report: UsageReport,
                                            license_agreement: LicenseAgreement) -> Decimal:
        """Calculate mechanical royalties."""
        # Use statutory rates or negotiated rates
        if usage_report.usage_type == 'download':
            per_download_rate = Decimal('0.091')  # US statutory rate
        else:
            per_download_rate = Decimal('0.00091')  # Streaming rate
        
        total_royalties = per_download_rate * usage_report.usage_count * license_agreement.royalty_rate
        return total_royalties
    
    async def _calculate_performance_royalties(self, usage_report: UsageReport,
                                             license_agreement: LicenseAgreement) -> Decimal:
        """Calculate performance royalties."""
        # Performance royalties typically based on revenue share
        performance_share = license_agreement.royalty_rate
        total_royalties = usage_report.revenue_generated * performance_share
        return total_royalties
    
    async def _calculate_sync_royalties(self, usage_report: UsageReport,
                                      license_agreement: LicenseAgreement) -> Decimal:
        """Calculate synchronization royalties."""
        # Sync royalties often flat fee or revenue share
        if 'sync_fee' in license_agreement.metadata:
            return Decimal(str(license_agreement.metadata['sync_fee']))
        else:
            return usage_report.revenue_generated * license_agreement.royalty_rate
    
    async def _calculate_download_royalties(self, usage_report: UsageReport,
                                          license_agreement: LicenseAgreement) -> Decimal:
        """Calculate download royalties."""
        # Similar to mechanical royalties
        return await self._calculate_mechanical_royalties(usage_report, license_agreement)
    
    async def _validate_license_compliance(self, license_agreement: LicenseAgreement):
        """Validate license agreement compliance with regulations."""
        license_requirements = self.compliance_rules['license_requirements'].get(
            license_agreement.license_type, {}
        )
        
        compliance_issues = []
        
        # Check territory-specific requirements
        for territory in license_agreement.territories:
            territory_rules = self.compliance_rules['territory_rules'].get(territory)
            if not territory_rules:
                compliance_issues.append(f"No compliance rules defined for territory: {territory}")
        
        # Check license-specific requirements
        if license_requirements.get('requires_master_rights') and 'master_rights' not in license_agreement.rights_granted:
            compliance_issues.append("Master rights required but not granted")
        
        if compliance_issues:
            logger.warning(f"Compliance issues for license {license_agreement.license_id}: {compliance_issues}")
            license_agreement.status = RightsStatus.UNDER_REVIEW
    
    def get_rights_management_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive rights management statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_usage = [
            usage for usage in self.usage_reports
            if usage.timestamp >= cutoff_time
        ]
        
        recent_royalties = [
            payment for payment in self.royalty_payments
            if payment.created_at >= cutoff_time
        ]
        
        # Calculate statistics
        total_usage_count = sum(usage.usage_count for usage in recent_usage)
        total_revenue = sum(usage.revenue_generated for usage in recent_usage)
        total_royalties = sum(payment.net_amount for payment in recent_royalties)
        
        # License type distribution
        license_type_counts = {}
        for license_type in LicenseType:
            count = len([l for l in self.license_agreements.values() if l.license_type == license_type])
            if count > 0:
                license_type_counts[license_type.value] = count
        
        # Territory analysis
        territory_stats = {}
        for usage in recent_usage:
            if usage.territory not in territory_stats:
                territory_stats[usage.territory] = {
                    'usage_count': 0,
                    'revenue': Decimal('0'),
                    'unique_content': set()
                }
            territory_stats[usage.territory]['usage_count'] += usage.usage_count
            territory_stats[usage.territory]['revenue'] += usage.revenue_generated
            territory_stats[usage.territory]['unique_content'].add(usage.content_id)
        
        # Convert sets to counts for JSON serialization
        for territory, stats in territory_stats.items():
            stats['unique_content_count'] = len(stats['unique_content'])
            del stats['unique_content']
            stats['revenue'] = float(stats['revenue'])
        
        return {
            'period_hours': hours,
            'usage_statistics': {
                'total_usage_events': len(recent_usage),
                'total_usage_count': total_usage_count,
                'total_revenue': float(total_revenue),
                'unique_content_items': len(set(usage.content_id for usage in recent_usage)),
                'unique_platforms': len(set(usage.platform for usage in recent_usage))
            },
            'royalty_statistics': {
                'total_royalty_payments': len(recent_royalties),
                'total_royalties_calculated': float(total_royalties),
                'pending_payments': len([p for p in recent_royalties if p.payment_status == 'pending']),
                'processed_payments': len([p for p in recent_royalties if p.payment_status == 'processed'])
            },
            'license_management': {
                'total_active_licenses': len([l for l in self.license_agreements.values() if l.status == RightsStatus.ACTIVE]),
                'license_type_distribution': license_type_counts,
                'expiring_licenses_30_days': len([
                    l for l in self.license_agreements.values()
                    if l.end_date and l.end_date <= datetime.utcnow() + timedelta(days=30)
                ])
            },
            'territory_analysis': territory_stats,
            'rights_holders': {
                'total_registered': len(self.rights_holders),
                'verified_holders': len([h for h in self.rights_holders.values() if h.verified])
            }
        }
    
    def get_royalty_report(self, rights_holder_id: str, 
                          start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate royalty report for specific rights holder."""
        if rights_holder_id not in self.rights_holders:
            raise ValueError(f"Rights holder not found: {rights_holder_id}")
        
        rights_holder = self.rights_holders[rights_holder_id]
        
        # Get all royalty payments for this rights holder in date range
        relevant_payments = [
            payment for payment in self.royalty_payments
            if (payment.rights_holder_id == rights_holder_id and
                start_date <= payment.created_at <= end_date)
        ]
        
        # Group by royalty type
        royalty_breakdown = {}
        for royalty_type in RoyaltyType:
            type_payments = [p for p in relevant_payments if p.royalty_type == royalty_type]
            if type_payments:
                royalty_breakdown[royalty_type.value] = {
                    'payment_count': len(type_payments),
                    'total_amount': float(sum(p.net_amount for p in type_payments)),
                    'total_usage': sum(p.usage_count for p in type_payments)
                }
        
        total_royalties = sum(p.net_amount for p in relevant_payments)
        
        return {
            'rights_holder': {
                'id': rights_holder.holder_id,
                'name': rights_holder.name,
                'territory': rights_holder.territory
            },
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_royalties': float(total_royalties),
                'total_payments': len(relevant_payments),
                'payment_status_breakdown': {
                    'pending': len([p for p in relevant_payments if p.payment_status == 'pending']),
                    'processed': len([p for p in relevant_payments if p.payment_status == 'processed']),
                    'failed': len([p for p in relevant_payments if p.payment_status == 'failed'])
                }
            },
            'royalty_breakdown': royalty_breakdown,
            'generated_at': datetime.utcnow().isoformat()
        }

# Global rights management monitor instance
rights_management_monitor = RightsManagementMonitor()

# Export main components
__all__ = [
    'RightsManagementMonitor',
    'LicenseAgreement',
    'RoyaltyPayment',
    'RightsHolder',
    'UsageReport',
    'LicenseType',
    'RightsStatus',
    'RoyaltyType',
    'rights_management_monitor'
]