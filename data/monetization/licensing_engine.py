"""Automated Content Licensing Engine
==================================

Professional licensing system for content creators and rights management.
Handles automatic licensing, royalty distribution, compliance tracking,
and legal protection for multi-format content monetization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis

from ..models.licensing_model import LicenseModel, RoyaltyModel
from .revenue_calculator import Currency


class LicenseType(Enum):
    """Types of content licenses"""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    SYNC = "sync"
    MECHANICAL = "mechanical"


class LicenseStatus(Enum):
    """License status"""    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISPUTED = "disputed"
    TERMINATED = "terminated"


class ContentType(Enum):
    """Types of licensable content"""    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    EBOOK = "ebook"
    SOFTWARE = "software"
    COURSE = "course"


class UsageType(Enum):
    """Content usage types"""    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    SYNC_VIDEO = "sync_video"
    LIVE_PERFORMANCE = "live_performance"
    MERCHANDISE = "merchandise"
    ADVERTISING = "advertising"
    EDUCATIONAL = "educational"


@dataclass
class LicenseTerms:
    """License terms and conditions"""    license_type: LicenseType
    usage_types: List[UsageType]
    territory: List[str]  # Country codes
    duration_months: Optional[int]  # None for perpetual
    max_uses: Optional[int]  # None for unlimited
    exclusivity: bool
    royalty_rate: Decimal  # Percentage
    minimum_fee: Decimal
    advance_payment: Decimal
    payment_schedule: str  # monthly, quarterly, annually
    attribution_required: bool
    modification_allowed: bool
    resale_allowed: bool
    commercial_use: bool


@dataclass
class LicenseAgreement:
    """Complete license agreement"""    license_id: str
    content_id: str
    licensor_id: str  # Content owner
    licensee_id: str  # License buyer
    terms: LicenseTerms
    start_date: datetime
    end_date: Optional[datetime]
    total_fee: Decimal
    currency: Currency
    status: LicenseStatus
    metadata: Dict[str, Any]


@dataclass
class RoyaltyPayment:
    """Royalty payment record"""    payment_id: str
    license_id: str
    period_start: datetime
    period_end: datetime
    usage_count: int
    revenue_generated: Decimal
    royalty_amount: Decimal
    payment_date: datetime
    payment_status: str


@dataclass
class LicenseReport:
    """License performance report"""    content_id: str
    total_licenses: int
    active_licenses: int
    total_revenue: Decimal
    royalty_payments: Decimal
    top_licensees: List[Dict]
    usage_analytics: Dict[str, Any]
    performance_metrics: Dict[str, float]


class LicensingEngine:
    """    Professional content licensing engine for IA Influencer Agent platform.
    
    Provides automated licensing, royalty management, compliance tracking,
    and comprehensive rights management for content creators across
    multiple formats and platforms.
    """    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """        Initialize LicensingEngine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.minimum_license_fee = Decimal('10.00')  # €10
        self.default_royalty_rate = Decimal('0.15')  # 15%
        self.license_expiry_buffer = timedelta(days=7)  # 7 days notice
        
        # Default license terms by content type
        self.default_terms = {
            ContentType.MUSIC: LicenseTerms(
                license_type=LicenseType.NON_EXCLUSIVE,
                usage_types=[UsageType.STREAMING, UsageType.DOWNLOAD],
                territory=['DE', 'EU', 'US'],
                duration_months=12,
                max_uses=None,
                exclusivity=False,
                royalty_rate=Decimal('0.15'),
                minimum_fee=Decimal('50.00'),
                advance_payment=Decimal('0.00'),
                payment_schedule='monthly',
                attribution_required=True,
                modification_allowed=False,
                resale_allowed=False,
                commercial_use=True
            ),
            ContentType.VIDEO: LicenseTerms(
                license_type=LicenseType.NON_EXCLUSIVE,
                usage_types=[UsageType.STREAMING, UsageType.BROADCAST],
                territory=['DE', 'EU'],
                duration_months=6,
                max_uses=1000,
                exclusivity=False,
                royalty_rate=Decimal('0.20'),
                minimum_fee=Decimal('100.00'),
                advance_payment=Decimal('0.00'),
                payment_schedule='quarterly',
                attribution_required=True,
                modification_allowed=True,
                resale_allowed=False,
                commercial_use=True
            ),
            ContentType.IMAGE: LicenseTerms(
                license_type=LicenseType.ROYALTY_FREE,
                usage_types=[UsageType.ADVERTISING, UsageType.MERCHANDISE],
                territory=['WORLDWIDE'],
                duration_months=None,  # Perpetual
                max_uses=None,
                exclusivity=False,
                royalty_rate=Decimal('0.00'),
                minimum_fee=Decimal('25.00'),
                advance_payment=Decimal('25.00'),
                payment_schedule='one_time',
                attribution_required=False,
                modification_allowed=True,
                resale_allowed=False,
                commercial_use=True
            )
        }
        
        # Territory pricing multipliers
        self.territory_multipliers = {
            'US': Decimal('1.5'),
            'EU': Decimal('1.2'),
            'DE': Decimal('1.0'),
            'UK': Decimal('1.3'),
            'CA': Decimal('1.1'),
            'AU': Decimal('1.1'),
            'JP': Decimal('1.4'),
            'WORLDWIDE': Decimal('2.0')
        }
    
    async def create_license_offer(self, content_id: str, licensor_id: str,
                                 content_type: ContentType,
                                 custom_terms: Optional[LicenseTerms] = None) -> str:
        """        Create a license offer for content.
        
        Args:
            content_id: Content identifier
            licensor_id: Content owner identifier
            content_type: Type of content being licensed
            custom_terms: Optional custom license terms
            
        Returns:
            License offer identifier
        """        try:
            # Use custom terms or defaults
            terms = custom_terms or self.default_terms.get(content_type)
            if not terms:
                raise ValueError(f"No default terms found for content type: {content_type}")
            
            # Calculate pricing based on terms
            base_fee = await self._calculate_license_fee(content_id, terms)
            
            # Create license offer
            license_id = str(uuid.uuid4())
            
            offer = LicenseAgreement(
                license_id=license_id,
                content_id=content_id,
                licensor_id=licensor_id,
                licensee_id="",  # To be filled when accepted
                terms=terms,
                start_date=datetime.utcnow(),
                end_date=None,  # To be set when accepted
                total_fee=base_fee,
                currency=Currency.EUR,
                status=LicenseStatus.PENDING,
                metadata={
                    'content_type': content_type.value,
                    'created_at': datetime.utcnow().isoformat(),
                    'offer_expires': (datetime.utcnow() + timedelta(days=30)).isoformat()
                }
            )
            
            # Store license offer
            await self._store_license_agreement(offer)
            
            # Index for search
            await self._index_license_offer(offer)
            
            self.logger.info(f"License offer created: {license_id} for content {content_id}")
            return license_id
            
        except Exception as e:
            self.logger.error(f"Error creating license offer: {str(e)}")
            raise
    
    async def accept_license(self, license_id: str, licensee_id: str,
                           custom_terms: Optional[Dict[str, Any]] = None) -> bool:
        """        Accept a license offer.
        
        Args:
            license_id: License identifier
            licensee_id: License buyer identifier
            custom_terms: Optional custom terms modifications
            
        Returns:
            Acceptance success status
        """        try:
            # Get license offer
            license_offer = await self._get_license_agreement(license_id)
            if not license_offer:
                raise ValueError(f"License offer not found: {license_id}")
            
            if license_offer.status != LicenseStatus.PENDING:
                raise ValueError(f"License offer not available: {license_offer.status}")
            
            # Apply custom terms if provided
            if custom_terms:
                license_offer = await self._apply_custom_terms(license_offer, custom_terms)
            
            # Set licensee and activate
            license_offer.licensee_id = licensee_id
            license_offer.status = LicenseStatus.ACTIVE
            license_offer.start_date = datetime.utcnow()
            
            # Set end date if duration specified
            if license_offer.terms.duration_months:
                license_offer.end_date = license_offer.start_date + timedelta(
                    days=30 * license_offer.terms.duration_months
                )
            
            # Process initial payment
            payment_processed = await self._process_license_payment(license_offer)
            if not payment_processed:
                raise ValueError("License payment processing failed")
            
            # Update license agreement
            await self._update_license_agreement(license_offer)
            
            # Setup royalty tracking
            await self._setup_royalty_tracking(license_offer)
            
            # Send notifications
            await self._send_license_notifications(license_offer, 'accepted')
            
            # Create initial royalty record
            await self._create_initial_royalty_record(license_offer)
            
            self.logger.info(f"License accepted: {license_id} by {licensee_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error accepting license: {str(e)}")
            return False
    
    async def calculate_royalties(self, license_id: str, usage_data: Dict[str, Any]) -> RoyaltyPayment:
        """        Calculate royalty payment for license usage.
        
        Args:
            license_id: License identifier
            usage_data: Usage metrics and revenue data
            
        Returns:
            Calculated royalty payment
        """        try:
            # Get license agreement
            license_agreement = await self._get_license_agreement(license_id)
            if not license_agreement:
                raise ValueError(f"License agreement not found: {license_id}")
            
            # Extract usage metrics
            usage_count = usage_data.get('usage_count', 0)
            revenue_generated = Decimal(str(usage_data.get('revenue_generated', 0)))
            period_start = datetime.fromisoformat(usage_data.get('period_start'))
            period_end = datetime.fromisoformat(usage_data.get('period_end'))
            
            # Calculate royalty amount
            royalty_rate = license_agreement.terms.royalty_rate
            royalty_amount = revenue_generated * royalty_rate
            
            # Apply minimum fee if applicable
            if royalty_amount < license_agreement.terms.minimum_fee:
                royalty_amount = license_agreement.terms.minimum_fee
            
            # Create royalty payment record
            payment_id = str(uuid.uuid4())
            
            royalty_payment = RoyaltyPayment(
                payment_id=payment_id,
                license_id=license_id,
                period_start=period_start,
                period_end=period_end,
                usage_count=usage_count,
                revenue_generated=revenue_generated,
                royalty_amount=royalty_amount,
                payment_date=datetime.utcnow(),
                payment_status='pending'
            )
            
            # Store royalty payment
            await self._store_royalty_payment(royalty_payment)
            
            # Process payment
            payment_processed = await self._process_royalty_payment(royalty_payment)
            if payment_processed:
                royalty_payment.payment_status = 'completed'
                await self._update_royalty_payment(royalty_payment)
            
            return royalty_payment
            
        except Exception as e:
            self.logger.error(f"Error calculating royalties: {str(e)}")
            raise
    
    async def search_licenses(self, search_criteria: Dict[str, Any],
                            limit: int = 50) -> List[LicenseAgreement]:
        """        Search available licenses.
        
        Args:
            search_criteria: Search filters
            limit: Maximum number of results
            
        Returns:
            List of matching licenses
        """        try:
            # Build search query
            filters = []
            
            if 'content_type' in search_criteria:
                filters.append(f"content_type:{search_criteria['content_type']}")
            
            if 'license_type' in search_criteria:
                filters.append(f"license_type:{search_criteria['license_type']}")
            
            if 'territory' in search_criteria:
                filters.append(f"territory:{search_criteria['territory']}")
            
            if 'max_fee' in search_criteria:
                filters.append(f"total_fee:<={search_criteria['max_fee']}")
            
            if 'usage_type' in search_criteria:
                filters.append(f"usage_types:{search_criteria['usage_type']}")
            
            # Search in license index
            search_results = await self._search_license_index(filters, limit)
            
            # Convert to LicenseAgreement objects
            licenses = []
            for result in search_results:
                license_agreement = await self._get_license_agreement(result['license_id'])
                if license_agreement and license_agreement.status == LicenseStatus.PENDING:
                    licenses.append(license_agreement)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"Error searching licenses: {str(e)}")
            return []
    
    async def get_license_report(self, content_id: str, period_days: int = 30) -> LicenseReport:
        """        Generate license performance report for content.
        
        Args:
            content_id: Content identifier
            period_days: Report period in days
            
        Returns:
            License performance report
        """        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get all licenses for content
            all_licenses = await self._get_content_licenses(content_id)
            
            # Filter active licenses in period
            period_licenses = [
                lic for lic in all_licenses
                if lic.start_date >= start_date and lic.status == LicenseStatus.ACTIVE
            ]
            
            # Calculate total revenue
            total_revenue = sum(lic.total_fee for lic in period_licenses)
            
            # Get royalty payments
            royalty_payments = await self._get_content_royalties(content_id, start_date, end_date)
            total_royalties = sum(payment.royalty_amount for payment in royalty_payments)
            
            # Get top licensees
            licensee_revenue = {}
            for license_agreement in period_licenses:
                licensee_id = license_agreement.licensee_id
                licensee_revenue[licensee_id] = licensee_revenue.get(licensee_id, Decimal('0')) + license_agreement.total_fee
            
            top_licensees = [
                {'licensee_id': k, 'revenue': float(v)}
                for k, v in sorted(licensee_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Calculate usage analytics
            usage_analytics = await self._calculate_usage_analytics(content_id, period_licenses)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_license_performance_metrics(
                content_id, period_licenses, royalty_payments
            )
            
            report = LicenseReport(
                content_id=content_id,
                total_licenses=len(all_licenses),
                active_licenses=len(period_licenses),
                total_revenue=total_revenue,
                royalty_payments=total_royalties,
                top_licensees=top_licensees,
                usage_analytics=usage_analytics,
                performance_metrics=performance_metrics
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating license report: {str(e)}")
            return LicenseReport(
                content_id=content_id,
                total_licenses=0,
                active_licenses=0,
                total_revenue=Decimal('0'),
                royalty_payments=Decimal('0'),
                top_licensees=[],
                usage_analytics={},
                performance_metrics={}
            )
    
    async def process_license_renewals(self) -> List[Dict[str, Any]]:
        """        Process automatic license renewals.
        
        Returns:
            List of renewal processing results
        """        try:
            results = []
            
            # Get licenses expiring soon
            expiring_licenses = await self._get_expiring_licenses()
            
            for license_agreement in expiring_licenses:
                try:
                    # Check if renewal is configured
                    auto_renew = license_agreement.metadata.get('auto_renew', False)
                    
                    if auto_renew:
                        # Process automatic renewal
                        renewed = await self._renew_license(license_agreement)
                        
                        results.append({
                            'license_id': license_agreement.license_id,
                            'action': 'auto_renewed',
                            'success': renewed,
                            'new_end_date': license_agreement.end_date.isoformat() if renewed else None
                        })
                    else:
                        # Send renewal notification
                        await self._send_renewal_notification(license_agreement)
                        
                        results.append({
                            'license_id': license_agreement.license_id,
                            'action': 'notification_sent',
                            'success': True,
                            'expires_at': license_agreement.end_date.isoformat()
                        })
                
                except Exception as e:
                    results.append({
                        'license_id': license_agreement.license_id,
                        'action': 'error',
                        'success': False,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing license renewals: {str(e)}")
            return []
    
    async def revoke_license(self, license_id: str, reason: str) -> bool:
        """        Revoke a license agreement.
        
        Args:
            license_id: License identifier
            reason: Revocation reason
            
        Returns:
            Revocation success status
        """        try:
            # Get license agreement
            license_agreement = await self._get_license_agreement(license_id)
            if not license_agreement:
                raise ValueError(f"License agreement not found: {license_id}")
            
            # Update status
            license_agreement.status = LicenseStatus.REVOKED
            license_agreement.metadata['revocation_reason'] = reason
            license_agreement.metadata['revoked_at'] = datetime.utcnow().isoformat()
            
            # Update license agreement
            await self._update_license_agreement(license_agreement)
            
            # Process refund if applicable
            refund_processed = await self._process_license_refund(license_agreement, reason)
            
            # Send notifications
            await self._send_license_notifications(license_agreement, 'revoked')
            
            # Stop royalty tracking
            await self._stop_royalty_tracking(license_id)
            
            self.logger.info(f"License revoked: {license_id} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error revoking license: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _calculate_license_fee(self, content_id: str, terms: LicenseTerms) -> Decimal:
        """Calculate license fee based on terms"""        base_fee = terms.minimum_fee
        
        # Apply territory multiplier
        territory_multiplier = Decimal('1.0')
        for territory in terms.territory:
            multiplier = self.territory_multipliers.get(territory, Decimal('1.0'))
            territory_multiplier = max(territory_multiplier, multiplier)
        
        # Apply exclusivity multiplier
        exclusivity_multiplier = Decimal('2.0') if terms.exclusivity else Decimal('1.0')
        
        # Apply duration multiplier
        duration_multiplier = Decimal('1.0')
        if terms.duration_months:
            duration_multiplier = Decimal(str(terms.duration_months / 12))  # Annual basis
        else:
            duration_multiplier = Decimal('3.0')  # Perpetual premium
        
        # Calculate final fee
        final_fee = base_fee * territory_multiplier * exclusivity_multiplier * duration_multiplier
        
        return final_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _store_license_agreement(self, agreement: LicenseAgreement):
        """Store license agreement in database"""        # Implementation would store in database
        license_record = LicenseModel(
            id=agreement.license_id,
            content_id=agreement.content_id,
            licensor_id=agreement.licensor_id,
            licensee_id=agreement.licensee_id,
            terms=agreement.terms.__dict__,
            start_date=agreement.start_date,
            end_date=agreement.end_date,
            total_fee=agreement.total_fee,
            currency=agreement.currency.value,
            status=agreement.status.value,
            metadata=agreement.metadata,
            created_at=datetime.utcnow()
        )
        
        self.db_session.add(license_record)
        await self.db_session.commit()
    
    async def _get_license_agreement(self, license_id: str) -> Optional[LicenseAgreement]:
        """Get license agreement from database"""        # Implementation would query database
        # Placeholder implementation
        return None
    
    async def _index_license_offer(self, offer: LicenseAgreement):
        """Index license offer for search"""        # Implementation would index in search engine
        search_doc = {
            'license_id': offer.license_id,
            'content_id': offer.content_id,
            'license_type': offer.terms.license_type.value,
            'territory': offer.terms.territory,
            'total_fee': float(offer.total_fee),
            'usage_types': [ut.value for ut in offer.terms.usage_types],
            'status': offer.status.value
        }
        
        # Cache for search
        cache_key = f"license_search:{offer.license_id}"
        await self._save_to_cache(cache_key, search_doc)
    
    async def _search_license_index(self, filters: List[str], limit: int) -> List[Dict]:
        """Search license index"""        # Implementation would search in Elasticsearch or similar
        # Placeholder implementation
        return []
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    # Additional helper methods would be implemented here...
    
    async def _apply_custom_terms(self, license_offer: LicenseAgreement, 
                                custom_terms: Dict[str, Any]) -> LicenseAgreement:
        """Apply custom terms to license offer"""        # Implementation would modify terms based on custom_terms
        return license_offer
    
    async def _process_license_payment(self, license_agreement: LicenseAgreement) -> bool:
        """Process license payment"""        # Implementation would process payment through payment processor
        return True
    
    async def _setup_royalty_tracking(self, license_agreement: LicenseAgreement):
        """Setup royalty tracking for license"""        # Implementation would setup tracking
        pass
    
    async def _send_license_notifications(self, license_agreement: LicenseAgreement, event: str):
        """Send license notifications"""        # Implementation would send notifications
        pass
    
    async def _create_initial_royalty_record(self, license_agreement: LicenseAgreement):
        """Create initial royalty record"""        # Implementation would create royalty tracking record
        pass
