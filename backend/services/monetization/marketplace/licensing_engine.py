"""Licensing Engine - Advanced Content Licensing Management
=========================================================

Automated licensing and contract management engine with AI-powered
pricing, negotiation, and compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json

logger = logging.getLogger(__name__)


class LicenseType(str, Enum):
    """License type categories."""
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EXCLUSIVE = "exclusive"
    EXTENDED = "extended"
    EDITORIAL = "editorial"
    COMMERCIAL = "commercial"
    SYNC = "sync"
    MECHANICAL = "mechanical"


class LicenseStatus(str, Enum):
    """License agreement status."""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    RENEWED = "renewed"


class UsageType(str, Enum):
    """Content usage types."""
    DIGITAL = "digital"
    PRINT = "print"
    BROADCAST = "broadcast"
    THEATRICAL = "theatrical"
    STREAMING = "streaming"
    ADVERTISING = "advertising"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"


@dataclass
class LicenseTerms:
    """License terms and conditions."""
    license_type: LicenseType
    usage_types: List[UsageType]
    territory: str
    duration_months: int
    price: Decimal
    royalty_rate: Optional[Decimal] = None
    usage_limits: Optional[Dict[str, Any]] = None
    exclusivity: bool = False
    commercial_use: bool = True
    attribution_required: bool = True
    modification_allowed: bool = False
    resale_allowed: bool = False


@dataclass
class LicenseAgreement:
    """License agreement record."""
    id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    terms: LicenseTerms
    status: LicenseStatus
    contract_data: Dict[str, Any]
    created_at: datetime
    signed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    usage_tracking: List[Dict[str, Any]] = field(default_factory=list)
    revenue_generated: Decimal = Decimal("0")


@dataclass
class LicensePricing:
    """License pricing calculation."""
    base_price: Decimal
    territory_multiplier: Decimal
    duration_multiplier: Decimal
    usage_multiplier: Decimal
    exclusivity_multiplier: Decimal
    final_price: Decimal
    calculation_details: Dict[str, Any]


class LicensingEngine:
    """Advanced automated licensing and contract management engine."""
    
    def __init__(self):
        """Initialize licensing engine."""
        self.agreements: Dict[str, LicenseAgreement] = {}
        self.pricing_models = self._initialize_pricing_models()
        self.contract_templates = self._initialize_contract_templates()
        
        logger.info("Licensing engine initialized")
    
    def _initialize_pricing_models(self) -> Dict[LicenseType, Dict[str, Any]]:
        """Initialize default pricing models."""
        return {
            LicenseType.ROYALTY_FREE: {
                "base_price": Decimal("50.00"),
                "commercial_multiplier": Decimal("2.0"),
                "territory_multipliers": {
                    "worldwide": Decimal("3.0"),
                    "north_america": Decimal("1.5"),
                    "europe": Decimal("1.3"),
                    "asia": Decimal("1.2"),
                    "single_country": Decimal("1.0")
                }
            },
            LicenseType.EXCLUSIVE: {
                "base_price": Decimal("500.00"),
                "commercial_multiplier": Decimal("5.0"),
                "territory_multipliers": {
                    "worldwide": Decimal("10.0"),
                    "north_america": Decimal("4.0"),
                    "europe": Decimal("3.0"),
                    "asia": Decimal("2.5"),
                    "single_country": Decimal("2.0")
                }
            },
            LicenseType.SYNC: {
                "base_price": Decimal("200.00"),
                "commercial_multiplier": Decimal("3.0"),
                "territory_multipliers": {
                    "worldwide": Decimal("5.0"),
                    "north_america": Decimal("2.5"),
                    "europe": Decimal("2.0"),
                    "asia": Decimal("1.8"),
                    "single_country": Decimal("1.5")
                }
            },
            LicenseType.RIGHTS_MANAGED: {
                "base_price": Decimal("100.00"),
                "commercial_multiplier": Decimal("2.5"),
                "territory_multipliers": {
                    "worldwide": Decimal("4.0"),
                    "north_america": Decimal("2.0"),
                    "europe": Decimal("1.8"),
                    "asia": Decimal("1.5"),
                    "single_country": Decimal("1.2")
                }
            }
        }
    
    def _initialize_contract_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize contract templates."""
        return {
            "basic_license": {
                "title": "Content License Agreement",
                "clauses": [
                    "grant_of_rights",
                    "license_scope",
                    "payment_terms",
                    "attribution",
                    "warranty_disclaimer",
                    "limitation_liability",
                    "termination",
                    "governing_law"
                ]
            },
            "exclusive_license": {
                "title": "Exclusive Content License Agreement",
                "clauses": [
                    "grant_of_rights",
                    "exclusivity_clause",
                    "license_scope",
                    "payment_terms",
                    "attribution",
                    "warranty_disclaimer",
                    "limitation_liability",
                    "termination",
                    "governing_law"
                ]
            },
            "sync_license": {
                "title": "Synchronization License Agreement",
                "clauses": [
                    "grant_of_rights",
                    "sync_rights",
                    "project_details",
                    "payment_terms",
                    "cue_sheets",
                    "warranty_disclaimer",
                    "limitation_liability",
                    "termination",
                    "governing_law"
                ]
            }
        }
    
    async def calculate_license_price(
        self,
        content_id: str,
        license_type: LicenseType,
        usage_types: List[UsageType],
        territory: str,
        duration_months: int,
        commercial_use: bool = True,
        exclusivity: bool = False
    ) -> LicensePricing:
        """Calculate automated license pricing.
        
        Args:
            content_id: Content identifier
            license_type: Type of license
            usage_types: Types of usage
            territory: Geographic territory
            duration_months: License duration
            commercial_use: Commercial usage flag
            exclusivity: Exclusivity flag
            
        Returns:
            License pricing calculation
        """
        try:
            pricing_model = self.pricing_models.get(license_type)
            if not pricing_model:
                raise ValueError(f"No pricing model for license type: {license_type}")
            
            base_price = pricing_model["base_price"]
            commercial_multiplier = pricing_model.get("commercial_multiplier", Decimal("1.0"))
            territory_multipliers = pricing_model.get("territory_multipliers", {})
            
            # Territory multiplier
            territory_key = territory.lower().replace(" ", "_")
            territory_multiplier = Decimal(str(territory_multipliers.get(territory_key, 1.0)))
            
            # Duration multiplier (longer duration = higher price)
            if duration_months <= 12:
                duration_multiplier = Decimal("1.0")
            elif duration_months <= 24:
                duration_multiplier = Decimal("1.5")
            elif duration_months <= 60:
                duration_multiplier = Decimal("2.0")
            else:
                duration_multiplier = Decimal("3.0")
            
            # Usage type multiplier
            usage_multiplier = Decimal("1.0")
            high_value_usage = [UsageType.BROADCAST, UsageType.THEATRICAL, UsageType.ADVERTISING]
            for usage in usage_types:
                if usage in high_value_usage:
                    usage_multiplier += Decimal("0.5")
                else:
                    usage_multiplier += Decimal("0.2")
            
            # Exclusivity multiplier
            exclusivity_multiplier = Decimal("5.0") if exclusivity else Decimal("1.0")
            
            # Commercial use multiplier
            if commercial_use:
                final_commercial_multiplier = commercial_multiplier
            else:
                final_commercial_multiplier = Decimal("0.5")  # Reduced for non-commercial
            
            # Calculate final price
            final_price = (
                base_price *
                territory_multiplier *
                duration_multiplier *
                usage_multiplier *
                exclusivity_multiplier *
                final_commercial_multiplier
            )
            
            pricing = LicensePricing(
                base_price=base_price,
                territory_multiplier=territory_multiplier,
                duration_multiplier=duration_multiplier,
                usage_multiplier=usage_multiplier,
                exclusivity_multiplier=exclusivity_multiplier,
                final_price=final_price,
                calculation_details={
                    "license_type": license_type.value,
                    "territory": territory,
                    "duration_months": duration_months,
                    "usage_types": [u.value for u in usage_types],
                    "commercial_use": commercial_use,
                    "exclusivity": exclusivity,
                    "multipliers": {
                        "territory": float(territory_multiplier),
                        "duration": float(duration_multiplier),
                        "usage": float(usage_multiplier),
                        "exclusivity": float(exclusivity_multiplier),
                        "commercial": float(final_commercial_multiplier)
                    }
                }
            )
            
            logger.info(f"License price calculated for {content_id}: ${final_price}")
            return pricing
            
        except Exception as e:
            logger.error(f"Failed to calculate license price: {e}")
            raise
    
    async def generate_license_agreement(
        self,
        content_id: str,
        licensor_id: str,
        licensee_id: str,
        terms: LicenseTerms
    ) -> LicenseAgreement:
        """Generate a new licensing agreement.
        
        Args:
            content_id: Content identifier
            licensor_id: Licensor identifier
            licensee_id: Licensee identifier
            terms: License terms
            
        Returns:
            Generated license agreement
        """
        try:
            agreement_id = str(uuid.uuid4())
            
            # Generate contract document
            contract_data = await self._generate_contract_document(terms)
            
            # Calculate expiration date
            expires_at = None
            if terms.duration_months > 0:
                expires_at = datetime.now() + timedelta(days=terms.duration_months * 30)
            
            agreement = LicenseAgreement(
                id=agreement_id,
                content_id=content_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                terms=terms,
                status=LicenseStatus.DRAFT,
                contract_data=contract_data,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            self.agreements[agreement_id] = agreement
            
            logger.info(f"License agreement generated: {agreement_id}")
            return agreement
            
        except Exception as e:
            logger.error(f"Failed to generate license agreement: {e}")
            raise
    
    async def _generate_contract_document(self, terms: LicenseTerms) -> Dict[str, Any]:
        """Generate contract document from terms.
        
        Args:
            terms: License terms
            
        Returns:
            Contract document data
        """
        try:
            template_key = "basic_license"
            if terms.license_type == LicenseType.EXCLUSIVE:
                template_key = "exclusive_license"
            elif terms.license_type == LicenseType.SYNC:
                template_key = "sync_license"
            
            template = self.contract_templates.get(template_key, self.contract_templates["basic_license"])
            
            contract_data = {
                "template": template_key,
                "title": template["title"],
                "parties": {
                    "licensor": "TBD",  # Would be filled with actual details
                    "licensee": "TBD"
                },
                "grant_of_rights": {
                    "license_type": terms.license_type.value,
                    "usage_types": [u.value for u in terms.usage_types],
                    "territory": terms.territory,
                    "duration": f"{terms.duration_months} months",
                    "exclusivity": terms.exclusivity
                },
                "payment_terms": {
                    "license_fee": str(terms.price),
                    "royalty_rate": str(terms.royalty_rate) if terms.royalty_rate else None,
                    "payment_schedule": "Upon execution"
                },
                "usage_restrictions": {
                    "commercial_use": terms.commercial_use,
                    "modification_allowed": terms.modification_allowed,
                    "resale_allowed": terms.resale_allowed,
                    "attribution_required": terms.attribution_required
                },
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            return contract_data
            
        except Exception as e:
            logger.error(f"Failed to generate contract document: {e}")
            return {}
    
    async def sign_agreement(
        self,
        agreement_id: str,
        signatory_id: str,
        digital_signature: str
    ) -> bool:
        """Sign a license agreement digitally.
        
        Args:
            agreement_id: Agreement identifier
            signatory_id: Signatory identifier
            digital_signature: Digital signature data
            
        Returns:
            True if signed successfully
        """
        try:
            if agreement_id not in self.agreements:
                raise ValueError(f"Agreement not found: {agreement_id}")
            
            agreement = self.agreements[agreement_id]
            
            if agreement.status != LicenseStatus.PENDING:
                raise ValueError(f"Agreement not ready for signing: {agreement.status}")
            
            # Verify signatory is authorized (licensor or licensee)
            if signatory_id not in [agreement.licensor_id, agreement.licensee_id]:
                raise ValueError("Unauthorized signatory")
            
            # Record signature
            if "signatures" not in agreement.contract_data:
                agreement.contract_data["signatures"] = {}
            
            agreement.contract_data["signatures"][signatory_id] = {
                "signature": digital_signature,
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if both parties have signed
            required_signatories = {agreement.licensor_id, agreement.licensee_id}
            signed_by = set(agreement.contract_data["signatures"].keys())
            
            if required_signatories.issubset(signed_by):
                agreement.status = LicenseStatus.ACTIVE
                agreement.signed_at = datetime.now()
                
                logger.info(f"Agreement fully executed: {agreement_id}")
            else:
                logger.info(f"Partial signature recorded for agreement: {agreement_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sign agreement: {e}")
            return False
    
    async def track_usage(
        self,
        agreement_id: str,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Track content usage under license agreement.
        
        Args:
            agreement_id: Agreement identifier
            usage_data: Usage tracking data
            
        Returns:
            True if usage recorded successfully
        """
        try:
            if agreement_id not in self.agreements:
                raise ValueError(f"Agreement not found: {agreement_id}")
            
            agreement = self.agreements[agreement_id]
            
            if agreement.status != LicenseStatus.ACTIVE:
                raise ValueError(f"Agreement not active: {agreement.status}")
            
            # Add timestamp to usage data
            usage_data["timestamp"] = datetime.now().isoformat()
            usage_data["recorded_by"] = "system"
            
            agreement.usage_tracking.append(usage_data)
            
            # Check for usage violations
            violations = await self._check_usage_violations(agreement, usage_data)
            if violations:
                logger.warning(f"Usage violations detected for agreement {agreement_id}: {violations}")
                usage_data["violations"] = violations
            
            logger.info(f"Usage tracked for agreement: {agreement_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            return False
    
    async def _check_usage_violations(
        self,
        agreement: LicenseAgreement,
        usage_data: Dict[str, Any]
    ) -> List[str]:
        """Check for usage violations.
        
        Args:
            agreement: License agreement
            usage_data: Usage data to check
            
        Returns:
            List of violations
        """
        violations = []
        
        try:
            terms = agreement.terms
            
            # Check usage type violations
            reported_usage = usage_data.get("usage_type")
            if reported_usage and reported_usage not in [u.value for u in terms.usage_types]:
                violations.append(f"Unauthorized usage type: {reported_usage}")
            
            # Check territory violations
            reported_territory = usage_data.get("territory")
            if reported_territory and reported_territory != terms.territory and terms.territory != "worldwide":
                violations.append(f"Territory violation: {reported_territory}")
            
            # Check commercial use violations
            is_commercial = usage_data.get("commercial_use", False)
            if is_commercial and not terms.commercial_use:
                violations.append("Unauthorized commercial use")
            
            # Check modification violations
            is_modified = usage_data.get("modified", False)
            if is_modified and not terms.modification_allowed:
                violations.append("Unauthorized modification")
            
            # Check usage limits if defined
            if terms.usage_limits:
                for limit_type, limit_value in terms.usage_limits.items():
                    actual_usage = usage_data.get(limit_type, 0)
                    if actual_usage > limit_value:
                        violations.append(f"Usage limit exceeded for {limit_type}: {actual_usage} > {limit_value}")
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to check usage violations: {e}")
            return ["Error checking violations"]
    
    async def renew_license(
        self,
        agreement_id: str,
        new_terms: Optional[LicenseTerms] = None
    ) -> LicenseAgreement:
        """Renew an expiring license agreement.
        
        Args:
            agreement_id: Agreement identifier
            new_terms: Optional new terms (uses existing if not provided)
            
        Returns:
            Renewed agreement
        """
        try:
            if agreement_id not in self.agreements:
                raise ValueError(f"Agreement not found: {agreement_id}")
            
            old_agreement = self.agreements[agreement_id]
            
            # Create new agreement for renewal
            renewed_terms = new_terms or old_agreement.terms
            renewed_terms.duration_months = renewed_terms.duration_months  # Reset duration
            
            new_agreement = await self.generate_license_agreement(
                content_id=old_agreement.content_id,
                licensor_id=old_agreement.licensor_id,
                licensee_id=old_agreement.licensee_id,
                terms=renewed_terms
            )
            
            # Mark old agreement as renewed
            old_agreement.status = LicenseStatus.RENEWED
            old_agreement.contract_data["renewed_to"] = new_agreement.id
            
            # Link new agreement to old one
            new_agreement.contract_data["renewal_of"] = agreement_id
            
            logger.info(f"License renewed: {agreement_id} -> {new_agreement.id}")
            return new_agreement
            
        except Exception as e:
            logger.error(f"Failed to renew license: {e}")
            raise
    
    async def get_agreement(self, agreement_id: str) -> Optional[LicenseAgreement]:
        """Get license agreement by ID.
        
        Args:
            agreement_id: Agreement identifier
            
        Returns:
            License agreement if found
        """
        return self.agreements.get(agreement_id)
    
    async def list_agreements_by_content(self, content_id: str) -> List[LicenseAgreement]:
        """List all agreements for a content item.
        
        Args:
            content_id: Content identifier
            
        Returns:
            List of agreements for content
        """
        return [
            agreement for agreement in self.agreements.values()
            if agreement.content_id == content_id
        ]
    
    async def list_agreements_by_party(
        self,
        party_id: str,
        as_licensor: bool = True
    ) -> List[LicenseAgreement]:
        """List agreements where party is licensor or licensee.
        
        Args:
            party_id: Party identifier
            as_licensor: True for licensor agreements, False for licensee
            
        Returns:
            List of agreements
        """
        if as_licensor:
            return [
                agreement for agreement in self.agreements.values()
                if agreement.licensor_id == party_id
            ]
        else:
            return [
                agreement for agreement in self.agreements.values()
                if agreement.licensee_id == party_id
            ]