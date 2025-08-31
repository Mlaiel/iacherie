"""
Content Licensing System
AI-powered content licensing, rights management and automated deal processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ...database.models import User, ContentLicense
from ...core.security.encryption import SecurityManager
from .revenue_calculator import RevenueCalculator


class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC_LICENSE = "sync_license"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"


class ContentType(Enum):
    """Types of content that can be licensed"""
    MUSIC = "music"
    VIDEO = "video"
    PHOTO = "photo"
    AUDIO = "audio"
    TEXT = "text"
    ARTWORK = "artwork"
    LOGO = "logo"
    BRAND = "brand"


class LicenseStatus(Enum):
    """License agreement status"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class UsageRights(Enum):
    """Permitted usage rights"""
    COMMERCIAL_USE = "commercial_use"
    EDITORIAL_USE = "editorial_use"
    PERSONAL_USE = "personal_use"
    EDUCATIONAL_USE = "educational_use"
    BROADCAST_USE = "broadcast_use"
    STREAMING_USE = "streaming_use"
    SOCIAL_MEDIA = "social_media"
    PRINT_MEDIA = "print_media"
    DIGITAL_MEDIA = "digital_media"
    MERCHANDISE = "merchandise"


@dataclass
class LicenseTerms:
    """License agreement terms"""
    license_type: LicenseType
    usage_rights: List[UsageRights]
    territory: List[str]  # Countries/regions
    duration_months: int
    payment_amount: Decimal
    currency: str = "EUR"
    royalty_percentage: Optional[Decimal] = None
    minimum_guarantee: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    restrictions: List[str] = field(default_factory=list)
    
    def calculate_total_value(self) -> Decimal:
        """Calculate total license value"""
        total = self.payment_amount
        
        if self.advance_payment:
            total += self.advance_payment
        
        if self.minimum_guarantee:
            total = max(total, self.minimum_guarantee)
        
        return total


@dataclass
class LicenseOffer:
    """License offer from potential licensee"""
    offer_id: str
    licensee_name: str
    licensee_email: str
    content_id: str
    content_title: str
    proposed_terms: LicenseTerms
    offer_date: datetime
    expiry_date: datetime
    message: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    status: str = "pending"
    
    def is_expired(self) -> bool:
        """Check if offer has expired"""



        return datetime.now() > self.expiry_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "offer_id": self.offer_id,
            "licensee_name": self.licensee_name,
            "licensee_email": self.licensee_email,
            "content_id": self.content_id,
            "content_title": self.content_title,
            "proposed_terms": {
                "license_type": self.proposed_terms.license_type.value,
                "usage_rights": [right.value for right in self.proposed_terms.usage_rights],
                "territory": self.proposed_terms.territory,
                "duration_months": self.proposed_terms.duration_months,
                "payment_amount": float(self.proposed_terms.payment_amount),
                "currency": self.proposed_terms.currency,
                "royalty_percentage": float(self.proposed_terms.royalty_percentage) if self.proposed_terms.royalty_percentage else None,
                "minimum_guarantee": float(self.proposed_terms.minimum_guarantee) if self.proposed_terms.minimum_guarantee else None,
                "advance_payment": float(self.proposed_terms.advance_payment) if self.proposed_terms.advance_payment else None,
                "restrictions": self.proposed_terms.restrictions
            },
            "offer_date": self.offer_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "message": self.message,
            "attachments": self.attachments,
            "status": self.status
        }


@dataclass
class LicenseAgreement:
    """Executed license agreement"""
    agreement_id: str
    licensor_id: int
    licensee_name: str
    licensee_email: str
    content_id: str
    license_terms: LicenseTerms
    start_date: datetime
    end_date: datetime
    status: LicenseStatus
    signed_date: Optional[datetime] = None
    contract_file_url: Optional[str] = None
    payment_schedule: List[Dict[str, Any]] = field(default_factory=list)
    usage_reports: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if license is currently active"""
        now = datetime.now()
        return (
            self.status == LicenseStatus.ACTIVE and
            self.start_date <= now <= self.end_date
        )
    
    def days_remaining(self) -> int:
        """Calculate days remaining in license"""
        if not self.is_active():
            return 0
        
        remaining = self.end_date - datetime.now()
        return max(0, remaining.days)
    
    def calculate_earned_revenue(self) -> Decimal:
        """Calculate revenue earned from this license"""
        total_revenue = Decimal("0")
        
        # Fixed payment
        total_revenue += self.license_terms.payment_amount
        
        # Advance payment
        if self.license_terms.advance_payment:
            total_revenue += self.license_terms.advance_payment
        
        # Royalty payments from usage reports
        if self.license_terms.royalty_percentage:
            for report in self.usage_reports:
                if 'gross_revenue' in report:
                    royalty = Decimal(str(report['gross_revenue'])) * (self.license_terms.royalty_percentage / 100)
                    total_revenue += royalty
        
        return total_revenue


class PricingEngine:
    """AI-powered license pricing engine"""
    
    def __init__(self, revenue_calculator: RevenueCalculator):
        self.revenue_calculator = revenue_calculator
        self.logger = logging.getLogger(__name__)
    
    async def calculate_suggested_price(
        self,
        content_type: ContentType,
        usage_rights: List[UsageRights],
        territory: List[str],
        duration_months: int,
        licensee_industry: Optional[str] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate AI-suggested licensing price"""



        try:
            base_price = await self._get_base_price(content_type, usage_rights)
            
            # Territory multiplier
            territory_multiplier = self._calculate_territory_multiplier(territory)
            
            # Duration multiplier
            duration_multiplier = self._calculate_duration_multiplier(duration_months)
            
            # Industry multiplier
            industry_multiplier = self._calculate_industry_multiplier(licensee_industry)
            
            # Market demand multiplier
            demand_multiplier = await self._calculate_market_demand(
                content_type, usage_rights, historical_data
            )
            
            # Calculate final price
            suggested_price = (
                base_price * 
                territory_multiplier * 
                duration_multiplier * 
                industry_multiplier * 
                demand_multiplier
            )
            
            # Price ranges
            min_price = suggested_price * Decimal("0.7")
            max_price = suggested_price * Decimal("1.5")
            
            return {
                "suggested_price": float(suggested_price),
                "min_price": float(min_price),
                "max_price": float(max_price),
                "base_price": float(base_price),
                "multipliers": {
                    "territory": float(territory_multiplier),
                    "duration": float(duration_multiplier),
                    "industry": float(industry_multiplier),
                    "demand": float(demand_multiplier)
                },
                "pricing_factors": {
                    "content_type": content_type.value,
                    "usage_rights": [right.value for right in usage_rights],
                    "territory_count": len(territory),
                    "duration_months": duration_months,
                    "industry": licensee_industry
                }
            }
            
        except Exception as e:
            self.logger.error(f"Price calculation failed: {str(e)}")
            return {"suggested_price": 100.0, "error": str(e)}
    
    async def _get_base_price(
        self,
        content_type: ContentType,
        usage_rights: List[UsageRights]
    ) -> Decimal:
        """Get base price for content type and usage rights"""
        
        # Base pricing matrix
        base_prices = {
            ContentType.MUSIC: Decimal("500"),
            ContentType.VIDEO: Decimal("800"),
            ContentType.PHOTO: Decimal("150"),
            ContentType.AUDIO: Decimal("300"),
            ContentType.TEXT: Decimal("100"),
            ContentType.ARTWORK: Decimal("400"),
            ContentType.LOGO: Decimal("600"),
            ContentType.BRAND: Decimal("1000")
        }
        
        base_price = base_prices.get(content_type, Decimal("200"))
        
        # Usage rights multiplier
        usage_multiplier = Decimal("1.0")
        
        for right in usage_rights:
            if right in [UsageRights.COMMERCIAL_USE, UsageRights.BROADCAST_USE]:
                usage_multiplier += Decimal("0.5")
            elif right in [UsageRights.STREAMING_USE, UsageRights.DIGITAL_MEDIA]:
                usage_multiplier += Decimal("0.3")
            elif right in [UsageRights.SOCIAL_MEDIA, UsageRights.EDUCATIONAL_USE]:
                usage_multiplier += Decimal("0.2")
            else:
                usage_multiplier += Decimal("0.1")
        
        return base_price * usage_multiplier
    
    def _calculate_territory_multiplier(self, territory: List[str]) -> Decimal:
        """Calculate territory-based price multiplier"""
        
        # Premium territories
        premium_territories = ['US', 'DE', 'UK', 'FR', 'CA', 'AU', 'JP']
        emerging_territories = ['IN', 'BR', 'MX', 'TR', 'ZA', 'ID']
        
        multiplier = Decimal("1.0")
        
        for country in territory:
            if country in premium_territories:
                multiplier += Decimal("0.3")
            elif country in emerging_territories:
                multiplier += Decimal("0.1")
            else:
                multiplier += Decimal("0.05")
        
        # Global territory bonus
        if len(territory) > 10:
            multiplier += Decimal("0.5")
        
        return min(multiplier, Decimal("3.0"))  # Cap at 3x
    
    def _calculate_duration_multiplier(self, duration_months: int) -> Decimal:
        """Calculate duration-based price multiplier"""
        
        if duration_months <= 3:
            return Decimal("0.8")
        elif duration_months <= 12:
            return Decimal("1.0")
        elif duration_months <= 24:
            return Decimal("1.3")
        elif duration_months <= 60:
            return Decimal("1.8")
        else:
            return Decimal("2.5")
    
    def _calculate_industry_multiplier(
        self,
        licensee_industry: Optional[str]
    ) -> Decimal:
        """Calculate industry-based price multiplier"""
        
        if not licensee_industry:
            return Decimal("1.0")
        
        industry_multipliers = {
            "advertising": Decimal("2.0"),
            "film": Decimal("1.8"),
            "television": Decimal("1.6"),
            "gaming": Decimal("1.4"),
            "streaming": Decimal("1.3"),
            "education": Decimal("0.7"),
            "nonprofit": Decimal("0.6"),
            "personal": Decimal("0.5")
        }
        
        return industry_multipliers.get(
            licensee_industry.lower(),
            Decimal("1.0")
        )
    
    async def _calculate_market_demand(
        self,
        content_type: ContentType,
        usage_rights: List[UsageRights],
        historical_data: Optional[Dict[str, Any]]
    ) -> Decimal:
        """Calculate market demand multiplier using historical data"""
        
        if not historical_data:
            return Decimal("1.0")
        
        # Analyze recent licensing activity
        recent_licenses = historical_data.get('recent_licenses', 0)
        avg_price = Decimal(str(historical_data.get('avg_price', 0)))
        
        demand_multiplier = Decimal("1.0")
        
        # High demand indicator
        if recent_licenses > 10:
            demand_multiplier += Decimal("0.3")
        elif recent_licenses > 5:
            demand_multiplier += Decimal("0.1")
        
        # Price trend indicator
        market_avg = Decimal("500")  # Default market average
        if avg_price > market_avg * Decimal("1.2"):
            demand_multiplier += Decimal("0.2")
        elif avg_price < market_avg * Decimal("0.8"):
            demand_multiplier -= Decimal("0.1")
        
        return max(demand_multiplier, Decimal("0.5"))


class LicensingEngine:
    """Advanced content licensing engine"""
    
    def __init__(
        self,
        pricing_engine: PricingEngine,
        security_manager: SecurityManager
    ):
        self.pricing_engine = pricing_engine
        self.security_manager = security_manager
        self.logger = logging.getLogger(__name__)
    
    async def create_license_offer(
        self,
        licensee_name: str,
        licensee_email: str,
        content_id: str,
        content_title: str,
        proposed_terms: LicenseTerms,
        message: Optional[str] = None,
        expiry_days: int = 30
    ) -> LicenseOffer:
        """Create a new license offer"""
        
        offer = LicenseOffer(
            offer_id=str(uuid.uuid4()),
            licensee_name=licensee_name,
            licensee_email=licensee_email,
            content_id=content_id,
            content_title=content_title,
            proposed_terms=proposed_terms,
            offer_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=expiry_days),
            message=message
        )
        
        self.logger.info(f"Created license offer {offer.offer_id} for content {content_id}")
        return offer
    
    async def evaluate_license_offer(
        self,
        offer: LicenseOffer,
        content_owner_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Evaluate license offer using AI pricing"""



        
        try:
            # Get suggested pricing
            pricing_data = await self.pricing_engine.calculate_suggested_price(
                content_type=ContentType.MUSIC,  # This should be determined from content
                usage_rights=offer.proposed_terms.usage_rights,
                territory=offer.proposed_terms.territory,
                duration_months=offer.proposed_terms.duration_months,
                licensee_industry=None  # Could be inferred from licensee data
            )
            
            suggested_price = Decimal(str(pricing_data["suggested_price"]))
            offered_price = offer.proposed_terms.payment_amount
            
            # Calculate offer quality
            price_ratio = offered_price / suggested_price if suggested_price > 0 else Decimal("0")
            
            evaluation = {
                "offer_id": offer.offer_id,
                "evaluation_score": float(price_ratio),
                "suggested_price": float(suggested_price),
                "offered_price": float(offered_price),
                "price_difference": float(offered_price - suggested_price),
                "price_difference_percentage": float((price_ratio - 1) * 100),
                "recommendation": self._get_recommendation(price_ratio),
                "pricing_analysis": pricing_data,
                "risk_factors": await self._analyze_risk_factors(offer),
                "evaluation_date": datetime.now().isoformat()
            }
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Offer evaluation failed: {str(e)}")
            return {"error": str(e)}
    
    def _get_recommendation(self, price_ratio: Decimal) -> str:
        """Get recommendation based on price ratio"""
        
        if price_ratio >= Decimal("1.2"):
            return "STRONGLY_ACCEPT"
        elif price_ratio >= Decimal("1.0"):
            return "ACCEPT"
        elif price_ratio >= Decimal("0.8"):
            return "NEGOTIATE"
        elif price_ratio >= Decimal("0.6"):
            return "COUNTER_OFFER"
        else:
            return "DECLINE"
    
    async def _analyze_risk_factors(self, offer: LicenseOffer) -> List[str]:
        """Analyze potential risk factors in the offer"""
        
        risk_factors = []
        
        # Expiry risk
        if offer.is_expired():
            risk_factors.append("Offer has expired")
        
        # Duration risk
        if offer.proposed_terms.duration_months > 60:
            risk_factors.append("Very long license duration")
        
        # Territory risk
        if len(offer.proposed_terms.territory) > 20:
            risk_factors.append("Global territory license")
        
        # Exclusive license risk
        if offer.proposed_terms.license_type == LicenseType.EXCLUSIVE:
            risk_factors.append("Exclusive license limits future opportunities")
        
        # Low payment risk
        if offer.proposed_terms.payment_amount < Decimal("100"):
            risk_factors.append("Below minimum recommended payment")
        
        # No advance payment
        if (offer.proposed_terms.royalty_percentage and 
            not offer.proposed_terms.advance_payment):
            risk_factors.append("Royalty-based with no advance payment")
        
        return risk_factors
    
    async def generate_license_agreement(
        self,
        licensor_id: int,
        offer: LicenseOffer,
        custom_terms: Optional[LicenseTerms] = None,
        session: AsyncSession
    ) -> LicenseAgreement:
        """Generate executable license agreement"""



        
        try:
            # Use custom terms if provided, otherwise use offer terms
            terms = custom_terms or offer.proposed_terms
            
            agreement = LicenseAgreement(
                agreement_id=str(uuid.uuid4()),
                licensor_id=licensor_id,
                licensee_name=offer.licensee_name,
                licensee_email=offer.licensee_email,
                content_id=offer.content_id,
                license_terms=terms,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=terms.duration_months * 30),
                status=LicenseStatus.DRAFT
            )
            
            # Generate payment schedule
            payment_schedule = await self._generate_payment_schedule(agreement)
            agreement.payment_schedule = payment_schedule
            
            self.logger.info(f"Generated license agreement {agreement.agreement_id}")
            return agreement
            
        except Exception as e:
            self.logger.error(f"Agreement generation failed: {str(e)}")
            raise
    
    async def _generate_payment_schedule(
        self,
        agreement: LicenseAgreement
    ) -> List[Dict[str, Any]]:
        """Generate payment schedule for license agreement"""
        
        schedule = []
        terms = agreement.license_terms
        
        # Advance payment
        if terms.advance_payment:
            schedule.append({
                "payment_id": str(uuid.uuid4()),
                "type": "advance",
                "amount": float(terms.advance_payment),
                "currency": terms.currency,
                "due_date": agreement.start_date.isoformat(),
                "status": "pending"
            })
        
        # Main payment
        if terms.payment_amount:
            # Split into quarterly payments if large amount
            if terms.payment_amount > Decimal("1000") and terms.duration_months > 3:
                quarterly_amount = terms.payment_amount / (terms.duration_months // 3)
                
                for quarter in range(terms.duration_months // 3):
                    due_date = agreement.start_date + timedelta(days=quarter * 90)
                    
                    schedule.append({
                        "payment_id": str(uuid.uuid4()),
                        "type": "quarterly",
                        "amount": float(quarterly_amount),
                        "currency": terms.currency,
                        "due_date": due_date.isoformat(),
                        "status": "pending"
                    })
            else:
                # Single payment
                schedule.append({
                    "payment_id": str(uuid.uuid4()),
                    "type": "full",
                    "amount": float(terms.payment_amount),
                    "currency": terms.currency,
                    "due_date": agreement.start_date.isoformat(),
                    "status": "pending"
                })
        
        return schedule
    
    async def execute_license_agreement(
        self,
        agreement: LicenseAgreement,
        digital_signature: str,
        session: AsyncSession
    ) -> bool:
        """Execute and activate license agreement"""



        
        try:
            # Verify digital signature
            signature_valid = await self.security_manager.verify_digital_signature(
                data=agreement.agreement_id,
                signature=digital_signature,
                signer_id=agreement.licensor_id
            )
            
            if not signature_valid:
                raise ValueError("Invalid digital signature")
            
            # Update agreement status
            agreement.status = LicenseStatus.ACTIVE
            agreement.signed_date = datetime.now()
            
            # Store in database
            license_record = ContentLicense(
                agreement_id=agreement.agreement_id,
                licensor_id=agreement.licensor_id,
                licensee_email=agreement.licensee_email,
                content_id=agreement.content_id,
                license_type=agreement.license_terms.license_type.value,
                start_date=agreement.start_date,
                end_date=agreement.end_date,
                payment_amount=agreement.license_terms.payment_amount,
                status=agreement.status.value,
                terms_json=agreement.__dict__
            )
            
            session.add(license_record)
            await session.commit()
            
            self.logger.info(f"License agreement {agreement.agreement_id} executed successfully")
            return True
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Agreement execution failed: {str(e)}")
            return False
    
    async def get_active_licenses(
        self,
        licensor_id: int,
        session: AsyncSession
    ) -> List[LicenseAgreement]:
        """Get all active licenses for a licensor"""



        
        try:
            result = await session.execute(
                select(ContentLicense).where(
                    ContentLicense.licensor_id == licensor_id,
                    ContentLicense.status == LicenseStatus.ACTIVE.value,
                    ContentLicense.end_date > datetime.now()
                )
            )
            
            licenses = []
            for record in result.scalars():
                # Convert database record back to LicenseAgreement
                # This would need proper deserialization
                agreement = LicenseAgreement(
                    agreement_id=record.agreement_id,
                    licensor_id=record.licensor_id,
                    licensee_name="",  # Would need to be stored
                    licensee_email=record.licensee_email,
                    content_id=record.content_id,
                    license_terms=LicenseTerms(
                        license_type=LicenseType(record.license_type),
                        usage_rights=[],  # Would need proper storage
                        territory=[],
                        duration_months=0,
                        payment_amount=record.payment_amount
                    ),
                    start_date=record.start_date,
                    end_date=record.end_date,
                    status=LicenseStatus(record.status)
                )
                licenses.append(agreement)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"Failed to get active licenses: {str(e)}")
            return []
    
    async def calculate_licensing_revenue(
        self,
        licensor_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate total licensing revenue for period"""



        
        try:
            result = await session.execute(
                select(
                    func.sum(ContentLicense.payment_amount).label('total_revenue'),
                    func.count(ContentLicense.id).label('license_count')
                ).where(
                    ContentLicense.licensor_id == licensor_id,
                    ContentLicense.start_date >= start_date,
                    ContentLicense.start_date <= end_date,
                    ContentLicense.status.in_([
                        LicenseStatus.ACTIVE.value,
                        LicenseStatus.EXPIRED.value
                    ])
                )
            )
            
            row = result.first()
            total_revenue = Decimal(str(row.total_revenue or 0))
            license_count = int(row.license_count or 0)
            
            return {
                "total_revenue": float(total_revenue),
                "license_count": license_count,
                "average_license_value": float(total_revenue / license_count) if license_count > 0 else 0,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Revenue calculation failed: {str(e)}")
            return {
                "total_revenue": 0,
                "license_count": 0,
                "average_license_value": 0
            }


class LicenseMonitor:
    """License monitoring and compliance system"""
    
    def __init__(self, licensing_engine: LicensingEngine):
        self.licensing_engine = licensing_engine
        self.logger = logging.getLogger(__name__)
    
    async def monitor_license_compliance(self, session: AsyncSession):
        """Monitor all licenses for compliance issues"""



        
        try:
            # Get all active licenses
            result = await session.execute(
                select(ContentLicense).where(
                    ContentLicense.status == LicenseStatus.ACTIVE.value
                )
            )
            
            compliance_issues = []
            
            for record in result.scalars():
                issues = await self._check_license_compliance(record)
                if issues:
                    compliance_issues.extend(issues)
            
            return compliance_issues
            
        except Exception as e:
            self.logger.error(f"Compliance monitoring failed: {str(e)}")
            return []
    
    async def _check_license_compliance(
        self,
        license_record: ContentLicense
    ) -> List[Dict[str, Any]]:
        """Check individual license for compliance issues"""
        
        issues = []
        
        # Check expiry
        if license_record.end_date <= datetime.now():
            issues.append({
                "license_id": license_record.agreement_id,
                "issue_type": "EXPIRED",
                "severity": "HIGH",
                "description": "License has expired",
                "detected_at": datetime.now().isoformat()
            })
        
        # Check payment overdue
        # This would check against payment schedule
        
        # Check usage reporting
        # This would verify usage reports are being submitted
        
        return issues
