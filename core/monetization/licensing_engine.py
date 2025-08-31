"""
Advanced Licensing Engine
Automated content licensing, rights management, and legal compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field, validator

from ...database.models import User, Content, License, LicenseAgreement
from ...security.digital_signature import DigitalSignatureManager
from ...legal.contract_generator import ContractGenerator
from ...ai.content_analysis import ContentAnalyzer


class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    SUBSCRIPTION = "subscription"
    SYNC_LICENSE = "sync_license"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"
    SYNCHRONIZATION = "synchronization"


class LicenseStatus(Enum):
    """License agreement status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"
    RENEWED = "renewed"


class UsageRights(Enum):
    """Content usage rights"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SYNC_VIDEO = "sync_video"
    LIVE_PERFORMANCE = "live_performance"
    REMIX = "remix"
    SAMPLING = "sampling"
    COVER_VERSION = "cover_version"


class Territory(Enum):
    """Geographic territories"""
    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    CUSTOM = "custom"


@dataclass
class LicenseTerms:
    """License agreement terms"""
    license_type: LicenseType
    usage_rights: List[UsageRights]
    territory: Territory
    duration_months: Optional[int]  # None for perpetual
    price: Decimal
    currency: str = "EUR"
    royalty_rate: Optional[Decimal] = None  # Percentage for ongoing royalties
    minimum_guarantee: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    attribution_required: bool = True
    exclusive_period: Optional[int] = None  # Months of exclusivity
    restrictions: List[str] = field(default_factory=list)
    custom_terms: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate license terms"""
        if self.price < 0:
            raise ValueError("License price cannot be negative")
        if self.royalty_rate and (self.royalty_rate < 0 or self.royalty_rate > 100):
            raise ValueError("Royalty rate must be between 0 and 100 percent")


@dataclass
class LicenseeInfo:
    """Information about license purchaser"""
    name: str
    email: str
    company: Optional[str] = None
    address: str = ""
    country: str = ""
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    business_type: Optional[str] = None
    intended_use: str = ""
    
    def validate(self) -> bool:
        """Validate licensee information"""
        required_fields = [self.name, self.email, self.intended_use]
        return all(field.strip() for field in required_fields)


class LicenseRequest(BaseModel):
    """License request data model"""
    content_id: str
    licensee_info: Dict[str, Any]
    license_terms: Dict[str, Any]
    usage_description: str
    project_details: Optional[Dict[str, Any]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    additional_notes: Optional[str] = None
    
    @validator('usage_description')
    def validate_usage_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Usage description must be at least 10 characters")
        return v


class LicenseAgreementResponse(BaseModel):
    """License agreement response"""
    license_id: str
    status: LicenseStatus
    agreement_url: Optional[str] = None
    payment_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    total_amount: Decimal
    terms_summary: Dict[str, Any]
    next_action: str


class LicensingEngine:
    """Advanced content licensing and rights management engine"""
    
    def __init__(
        self,
        signature_manager: DigitalSignatureManager,
        contract_generator: ContractGenerator,
        content_analyzer: ContentAnalyzer
    ):
        self.signature_manager = signature_manager
        self.contract_generator = contract_generator
        self.content_analyzer = content_analyzer
        self.logger = logging.getLogger(__name__)
        self.pricing_rules = self._initialize_pricing_rules()
        
    def _initialize_pricing_rules(self) -> Dict[str, Any]:
        """Initialize dynamic pricing rules"""



        return {
            "base_prices": {
                LicenseType.NON_EXCLUSIVE: {
                    UsageRights.COMMERCIAL: Decimal("500.00"),
                    UsageRights.NON_COMMERCIAL: Decimal("50.00"),
                    UsageRights.STREAMING: Decimal("200.00"),
                    UsageRights.BROADCAST: Decimal("1000.00"),
                    UsageRights.SYNC_VIDEO: Decimal("750.00")
                },
                LicenseType.EXCLUSIVE: {
                    UsageRights.COMMERCIAL: Decimal("2500.00"),
                    UsageRights.BROADCAST: Decimal("5000.00"),
                    UsageRights.SYNC_VIDEO: Decimal("3000.00")
                },
                LicenseType.SYNC_LICENSE: {
                    UsageRights.SYNC_VIDEO: Decimal("1500.00"),
                    UsageRights.BROADCAST: Decimal("2000.00")
                }
            },
            "territory_multipliers": {
                Territory.WORLDWIDE: Decimal("2.0"),
                Territory.NORTH_AMERICA: Decimal("1.5"),
                Territory.EUROPE: Decimal("1.3"),
                Territory.ASIA_PACIFIC: Decimal("1.2"),
                Territory.LATIN_AMERICA: Decimal("0.8"),
                Territory.AFRICA: Decimal("0.6")
            },
            "duration_factors": {
                "perpetual": Decimal("3.0"),
                "5_years": Decimal("2.0"),
                "1_year": Decimal("1.0"),
                "6_months": Decimal("0.7"),
                "3_months": Decimal("0.5")
            }
        }
    
    async def create_license_offer(
        self,
        content_id: str,
        license_request: LicenseRequest,
        session: AsyncSession
    ) -> LicenseAgreementResponse:
        """Create automated license offer based on request"""



        try:
            # Validate content exists and is available for licensing
            content = await self._get_content(content_id, session)
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            # Analyze content for licensing suitability
            content_analysis = await self.content_analyzer.analyze_licensing_potential(
                content_id
            )
            
            # Generate license terms based on request and content analysis
            license_terms = await self._generate_license_terms(
                license_request, content_analysis
            )
            
            # Create license agreement
            license_agreement = await self._create_license_agreement(
                content, license_request, license_terms, session
            )
            
            # Generate contract document
            contract_url = await self.contract_generator.generate_license_contract(
                license_agreement, license_terms
            )
            
            # Create payment link if needed
            payment_url = None
            if license_terms.price > 0:
                payment_url = await self._create_payment_link(
                    license_agreement, license_terms
                )
            
            return LicenseAgreementResponse(
                license_id=license_agreement.id,
                status=LicenseStatus.PENDING_APPROVAL,
                agreement_url=contract_url,
                payment_url=payment_url,
                expires_at=datetime.now() + timedelta(days=30),  # Offer expires in 30 days
                total_amount=license_terms.price,
                terms_summary=self._create_terms_summary(license_terms),
                next_action="Review and sign the license agreement"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create license offer: {str(e)}")
            raise
    
    async def _generate_license_terms(
        self,
        license_request: LicenseRequest,
        content_analysis: Dict[str, Any]
    ) -> LicenseTerms:
        """Generate optimized license terms using AI analysis"""
        
        # Extract request parameters
        licensee_info = LicenseeInfo(**license_request.licensee_info)
        requested_terms = license_request.license_terms
        
        # Determine license type
        license_type = LicenseType(requested_terms.get("type", "non_exclusive"))
        
        # Determine usage rights
        usage_rights = [
            UsageRights(right) for right in requested_terms.get("usage_rights", ["commercial"])
        ]
        
        # Determine territory
        territory = Territory(requested_terms.get("territory", "worldwide"))
        
        # Calculate dynamic pricing
        base_price = await self._calculate_dynamic_price(
            license_type, usage_rights, territory, content_analysis
        )
        
        # Apply content quality multiplier
        quality_score = content_analysis.get("quality_score", 0.7)
        price_multiplier = Decimal(str(0.5 + quality_score))  # 0.5 to 1.5 range
        final_price = base_price * price_multiplier
        
        # Determine duration
        duration_months = requested_terms.get("duration_months")
        if duration_months and duration_months > 60:  # Cap at 5 years
            duration_months = 60
        
        # Generate restrictions based on content type and request
        restrictions = self._generate_restrictions(
            license_type, usage_rights, content_analysis
        )
        
        return LicenseTerms(
            license_type=license_type,
            usage_rights=usage_rights,
            territory=territory,
            duration_months=duration_months,
            price=final_price.quantize(Decimal('0.01')),
            royalty_rate=self._calculate_royalty_rate(license_type, usage_rights),
            attribution_required=license_type != LicenseType.EXCLUSIVE,
            restrictions=restrictions,
            custom_terms=requested_terms.get("custom_terms", {})
        )
    
    async def _calculate_dynamic_price(
        self,
        license_type: LicenseType,
        usage_rights: List[UsageRights],
        territory: Territory,
        content_analysis: Dict[str, Any]
    ) -> Decimal:
        """Calculate dynamic pricing based on multiple factors"""
        
        # Get base price for primary usage right
        primary_right = usage_rights[0] if usage_rights else UsageRights.COMMERCIAL
        base_prices = self.pricing_rules["base_prices"].get(license_type, {})
        base_price = base_prices.get(primary_right, Decimal("100.00"))
        
        # Apply territory multiplier
        territory_multiplier = self.pricing_rules["territory_multipliers"].get(
            territory, Decimal("1.0")
        )
        
        # Apply popularity multiplier from content analysis
        popularity_score = content_analysis.get("popularity_score", 0.5)
        popularity_multiplier = Decimal(str(0.8 + (popularity_score * 0.4)))  # 0.8 to 1.2
        
        # Multiple usage rights multiplier
        usage_multiplier = Decimal(str(1.0 + (len(usage_rights) - 1) * 0.3))
        
        # Calculate final price
        final_price = (
            base_price * 
            territory_multiplier * 
            popularity_multiplier * 
            usage_multiplier
        )
        
        return final_price
    
    def _calculate_royalty_rate(
        self,
        license_type: LicenseType,
        usage_rights: List[UsageRights]
    ) -> Optional[Decimal]:
        """Calculate ongoing royalty rate if applicable"""
        if license_type == LicenseType.EXCLUSIVE:
            return None  # No ongoing royalties for exclusive licenses
        
        if UsageRights.COMMERCIAL in usage_rights:
            return Decimal("10.0")  # 10% royalty rate
        elif UsageRights.BROADCAST in usage_rights:
            return Decimal("15.0")  # 15% for broadcast
        else:
            return Decimal("5.0")   # 5% for other uses
    
    def _generate_restrictions(
        self,
        license_type: LicenseType,
        usage_rights: List[UsageRights],
        content_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate license restrictions based on terms and content"""
        restrictions = []
        
        # Standard restrictions
        if license_type == LicenseType.NON_EXCLUSIVE:
            restrictions.append("Non-exclusive license - licensor retains all rights")
        
        if UsageRights.REMIX not in usage_rights:
            restrictions.append("No derivative works or remixes allowed")
        
        if UsageRights.COMMERCIAL in usage_rights:
            restrictions.append("Commercial use limited to specified project")
        
        # Content-specific restrictions
        content_type = content_analysis.get("content_type", "audio")
        if content_type == "audio":
            restrictions.append("Audio synchronization must maintain original tempo")
        
        # Add AI-generated content disclosure if applicable
        if content_analysis.get("ai_generated", False):
            restrictions.append("Content contains AI-generated elements - disclosure required")
        
        return restrictions
    
    async def _create_license_agreement(
        self,
        content: Content,
        license_request: LicenseRequest,
        license_terms: LicenseTerms,
        session: AsyncSession
    ) -> LicenseAgreement:
        """Create license agreement record"""
        
        licensee_info = LicenseeInfo(**license_request.licensee_info)
        
        agreement = LicenseAgreement(
            content_id=content.id,
            licensor_id=content.user_id,
            licensee_name=licensee_info.name,
            licensee_email=licensee_info.email,
            licensee_company=licensee_info.company,
            license_type=license_terms.license_type.value,
            usage_rights=json.dumps([right.value for right in license_terms.usage_rights]),
            territory=license_terms.territory.value,
            duration_months=license_terms.duration_months,
            price=license_terms.price,
            currency=license_terms.currency,
            royalty_rate=license_terms.royalty_rate,
            status=LicenseStatus.PENDING_APPROVAL.value,
            terms_hash=self._generate_terms_hash(license_terms),
            usage_description=license_request.usage_description,
            restrictions=json.dumps(license_terms.restrictions),
            custom_terms=json.dumps(license_terms.custom_terms)
        )
        
        session.add(agreement)
        await session.commit()
        await session.refresh(agreement)
        
        return agreement
    
    def _generate_terms_hash(self, license_terms: LicenseTerms) -> str:
        """Generate hash of license terms for integrity verification"""
        import hashlib
        import json
        
        terms_dict = {
            "license_type": license_terms.license_type.value,
            "usage_rights": [right.value for right in license_terms.usage_rights],
            "territory": license_terms.territory.value,
            "duration_months": license_terms.duration_months,
            "price": str(license_terms.price),
            "royalty_rate": str(license_terms.royalty_rate) if license_terms.royalty_rate else None,
            "restrictions": license_terms.restrictions
        }
        
        terms_json = json.dumps(terms_dict, sort_keys=True)
        return hashlib.sha256(terms_json.encode()).hexdigest()
    
    async def _create_payment_link(
        self,
        license_agreement: LicenseAgreement,
        license_terms: LicenseTerms
    ) -> str:
        """Create payment link for license purchase"""
        # Integration with payment processor
        # This would typically integrate with Stripe, PayPal, etc.
        
        payment_data = {
            "license_id": license_agreement.id,
            "amount": float(license_terms.price),
            "currency": license_terms.currency,
            "description": f"License for content {license_agreement.content_id}",
            "success_url": f"/licensing/success/{license_agreement.id}",
            "cancel_url": f"/licensing/cancel/{license_agreement.id}"
        }
        
        # Mock payment URL - would be real payment processor URL
        return f"https://payments.example.com/checkout/{license_agreement.id}"
    
    def _create_terms_summary(self, license_terms: LicenseTerms) -> Dict[str, Any]:
        """Create human-readable terms summary"""



        return {
            "license_type": license_terms.license_type.value.replace("_", " ").title(),
            "usage_rights": [right.value.replace("_", " ").title() for right in license_terms.usage_rights],
            "territory": license_terms.territory.value.replace("_", " ").title(),
            "duration": f"{license_terms.duration_months} months" if license_terms.duration_months else "Perpetual",
            "price": f"{license_terms.price} {license_terms.currency}",
            "royalty_rate": f"{license_terms.royalty_rate}%" if license_terms.royalty_rate else "None",
            "attribution_required": license_terms.attribution_required,
            "restrictions_count": len(license_terms.restrictions)
        }
    
    async def approve_license(
        self,
        license_id: str,
        approver_signature: str,
        session: AsyncSession
    ) -> bool:
        """Approve and activate license agreement"""



        try:
            # Get license agreement
            agreement = await session.get(LicenseAgreement, license_id)
            if not agreement:
                return False
            
            # Verify digital signature
            if not await self.signature_manager.verify_signature(
                license_id, approver_signature
            ):
                return False
            
            # Update status to active
            agreement.status = LicenseStatus.ACTIVE.value
            agreement.approved_at = datetime.now()
            agreement.approver_signature = approver_signature
            
            # Set license expiration if applicable
            if agreement.duration_months:
                agreement.expires_at = datetime.now() + timedelta(
                    days=agreement.duration_months * 30
                )
            
            await session.commit()
            
            # Generate final signed contract
            await self.contract_generator.generate_signed_contract(agreement)
            
            # Send confirmation notifications
            await self._send_license_confirmation(agreement)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to approve license {license_id}: {str(e)}")
            return False
    
    async def revoke_license(
        self,
        license_id: str,
        reason: str,
        session: AsyncSession
    ) -> bool:
        """Revoke active license agreement"""



        try:
            agreement = await session.get(LicenseAgreement, license_id)
            if not agreement or agreement.status != LicenseStatus.ACTIVE.value:
                return False
            
            # Update status
            agreement.status = LicenseStatus.TERMINATED.value
            agreement.terminated_at = datetime.now()
            agreement.termination_reason = reason
            
            await session.commit()
            
            # Send termination notifications
            await self._send_license_termination(agreement, reason)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke license {license_id}: {str(e)}")
            return False
    
    async def get_license_status(
        self,
        license_id: str,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get current license status and details"""



        try:
            agreement = await session.get(LicenseAgreement, license_id)
            if not agreement:
                return None
            
            return {
                "license_id": agreement.id,
                "status": agreement.status,
                "content_id": agreement.content_id,
                "licensee": agreement.licensee_name,
                "license_type": agreement.license_type,
                "price": float(agreement.price),
                "currency": agreement.currency,
                "created_at": agreement.created_at.isoformat(),
                "expires_at": agreement.expires_at.isoformat() if agreement.expires_at else None,
                "approved_at": agreement.approved_at.isoformat() if agreement.approved_at else None,
                "usage_description": agreement.usage_description,
                "restrictions": json.loads(agreement.restrictions) if agreement.restrictions else []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get license status: {str(e)}")
            return None
    
    async def _get_content(self, content_id: str, session: AsyncSession) -> Optional[Content]:
        """Get content by ID"""



        return await session.get(Content, content_id)
    
    async def _send_license_confirmation(self, agreement: LicenseAgreement) -> None:
        """Send license confirmation notifications"""
        # Send email to licensee and licensor
        # Implementation would use email service
        self.logger.info(f"License confirmation sent for {agreement.id}")
    
    async def _send_license_termination(self, agreement: LicenseAgreement, reason: str) -> None:
        """Send license termination notifications"""
        # Send termination notice
        self.logger.info(f"License termination notice sent for {agreement.id}: {reason}")


class LicenseManager:
    """High-level license management interface"""
    
    def __init__(self, licensing_engine: LicensingEngine):
        self.licensing_engine = licensing_engine
        self.logger = logging.getLogger(__name__)
    
    async def create_instant_license(
        self,
        content_id: str,
        license_type: LicenseType,
        usage_rights: List[UsageRights],
        licensee_email: str,
        session: AsyncSession
    ) -> Optional[str]:
        """Create instant license for simple use cases"""



        try:
            # Create simplified license request
            license_request = LicenseRequest(
                content_id=content_id,
                licensee_info={
                    "name": "Instant License User",
                    "email": licensee_email,
                    "intended_use": "Standard usage"
                },
                license_terms={
                    "type": license_type.value,
                    "usage_rights": [right.value for right in usage_rights],
                    "territory": "worldwide"
                },
                usage_description="Instant license for standard usage"
            )
            
            # Create license offer
            response = await self.licensing_engine.create_license_offer(
                content_id, license_request, session
            )
            
            return response.license_id
            
        except Exception as e:
            self.logger.error(f"Failed to create instant license: {str(e)}")
            return None
    
    async def get_user_licenses(
        self,
        user_id: int,
        session: AsyncSession,
        status_filter: Optional[LicenseStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get all licenses for a user (as licensor or licensee)"""



        try:
            # Build query
            query = select(LicenseAgreement).where(
                (LicenseAgreement.licensor_id == user_id) |
                (LicenseAgreement.licensee_email.in_(
                    select(User.email).where(User.id == user_id)
                ))
            )
            
            if status_filter:
                query = query.where(LicenseAgreement.status == status_filter.value)
            
            result = await session.execute(query)
            agreements = result.scalars().all()
            
            licenses = []
            for agreement in agreements:
                license_data = await self.licensing_engine.get_license_status(
                    agreement.id, session
                )
                if license_data:
                    licenses.append(license_data)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"Failed to get user licenses: {str(e)}")
            return []
    
    async def calculate_licensing_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate licensing revenue for user"""



        try:
            # Get active licenses in date range
            result = await session.execute(
                select(LicenseAgreement).where(
                    LicenseAgreement.licensor_id == user_id,
                    LicenseAgreement.status == LicenseStatus.ACTIVE.value,
                    LicenseAgreement.approved_at >= start_date,
                    LicenseAgreement.approved_at <= end_date
                )
            )
            
            agreements = result.scalars().all()
            
            total_revenue = Decimal("0")
            license_count = 0
            revenue_by_type = {}
            
            for agreement in agreements:
                total_revenue += agreement.price
                license_count += 1
                
                license_type = agreement.license_type
                if license_type not in revenue_by_type:
                    revenue_by_type[license_type] = Decimal("0")
                revenue_by_type[license_type] += agreement.price
            
            return {
                "total_revenue": float(total_revenue),
                "license_count": license_count,
                "average_license_value": float(total_revenue / license_count) if license_count > 0 else 0,
                "revenue_by_type": {k: float(v) for k, v in revenue_by_type.items()},
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate licensing revenue: {str(e)}")
            return {}
