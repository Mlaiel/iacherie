"""Licensing Engine
Automated content licensing and contract management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """
License types"""

    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC = "sync"
    MASTER = "master"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"


class LicenseStatus(Enum):
    """License status"""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"


@dataclass
class LicenseTerms:
    """License terms and conditions"""
    license_type: LicenseType
    usage_rights: List[str]
    territory: str
    duration_months: int
    price: float
    currency: str = "EUR"
    royalty_rate: float = 0.0
    exclusivity: bool = False
    commercial_use: bool = True
    modification_allowed: bool = False
    attribution_required: bool = True
    revenue_sharing: bool = False
    maximum_uses: Optional[int] = None


@dataclass
class LicensingAgreement:
    """Licensing agreement structure"""
    id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    terms: LicenseTerms
    status: LicenseStatus
    created_at: datetime
    signed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    contract_data: Optional[Dict] = None
    usage_tracking: Optional[Dict] = None


class LicensingEngine:
    """
Automated licensing and contract management engine"""
    
    # Default pricing models
    PRICING_MODELS = {
        LicenseType.ROYALTY_FREE: {
            "base_price": 50.0,
            "commercial_multiplier": 2.0,
            "territory_multipliers": {
                "worldwide": 3.0,
                "north_america": 1.5,
                "europe": 1.3,
                "asia": 1.2,
                "single_country": 1.0
            }
        },
        LicenseType.EXCLUSIVE: {
            "base_price": 500.0,
            "commercial_multiplier": 5.0,
            "territory_multipliers": {
                "worldwide": 10.0,
                "north_america": 4.0,
                "europe": 3.0,
                "asia": 2.5,
                "single_country": 2.0
            }
        },
        LicenseType.SYNC: {
            "base_price": 200.0,
            "commercial_multiplier": 3.0,
            "territory_multipliers": {
                "worldwide": 5.0,
                "north_america": 2.5,
                "europe": 2.0,
                "asia": 1.8,
                "single_country": 1.5
            }
        }
    }
    
    # Legal templates
    CONTRACT_TEMPLATES = {
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
    
    def __init__(self):
        self.agreements = {}
        self.templates = self.CONTRACT_TEMPLATES
        
    async def calculate_license_price(
        self,
        content_id: str,
        license_type: LicenseType,
        usage_rights: List[str],
        territory: str,
        duration_months: int,
        commercial_use: bool = True,
        exclusivity: bool = False
    ) -> float:
        """Calculate automated license pricing"""
        try:
            pricing_model = self.PRICING_MODELS.get(license_type)
            if not pricing_model:
                logger.warning(f"No pricing model for license type: {license_type}")
                return 100.0  # Default price
                
            base_price = pricing_model["base_price"]
            
            # Territory multiplier
            territory_key = self._normalize_territory(territory)
            territory_multiplier = pricing_model["territory_multipliers"].get(territory_key, 1.0)
            
            # Commercial use multiplier
            commercial_multiplier = pricing_model["commercial_multiplier"] if commercial_use else 1.0
            
            # Duration factor
            duration_factor = min(duration_months / 12, 3.0)  # Max 3x for long-term
            
            # Exclusivity factor
            exclusivity_factor = 5.0 if exclusivity else 1.0
            
            # Usage rights factor
            usage_factor = len(usage_rights) * 0.2 + 1.0
            
            final_price = (
                base_price * 
                territory_multiplier * 
                commercial_multiplier * 
                duration_factor * 
                exclusivity_factor * 
                usage_factor
            )
            
            logger.info(f"License price calculated for {content_id}: €{final_price:.2f}")
            return round(final_price, 2)
            
        except Exception as e:
            logger.error(f"Error calculating license price: {str(e)}")
            return 100.0
    
    async def generate_license_agreement(
        self,
        content_id: str,
        licensor_id: str,
        licensee_id: str,
        terms: LicenseTerms
    ) -> LicensingAgreement:
        """Generate a new licensing agreement"""
        try:
            agreement_id = str(uuid.uuid4())
            
            agreement = LicensingAgreement(
                id=agreement_id,
                content_id=content_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                terms=terms,
                status=LicenseStatus.DRAFT,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=terms.duration_months * 30)
            )
            
            # Generate contract document
            contract_data = await self._generate_contract_document(agreement)
            agreement.contract_data = contract_data
            
            self.agreements[agreement_id] = agreement
            
            logger.info(f"License agreement generated: {agreement_id}")
            return agreement
            
        except Exception as e:
            logger.error(f"Error generating license agreement: {str(e)}")
            raise
    
    async def negotiate_price_automatically(
        self,
        agreement_id: str,
        counter_offer: float,
        licensee_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """Automated price negotiation"""
        try:
            agreement = self.agreements.get(agreement_id)
            if not agreement:
                return {"success": False, "error": "Agreement not found"}
                
            original_price = agreement.terms.price
            minimum_price = original_price * 0.7  # 30% discount max
            
            if counter_offer < minimum_price:
                # Reject if too low
                return {
                    "success": False,
                    "counter_offer": minimum_price,
                    "message": f"Minimum acceptable price is €{minimum_price:.2f}"
                }
            elif counter_offer < original_price * 0.9:
                # Counter-negotiate
                new_offer = (counter_offer + original_price) / 2
                return {
                    "success": False,
                    "counter_offer": new_offer,
                    "message": f"Counter-offer: €{new_offer:.2f}"
                }
            else:
                # Accept
                agreement.terms.price = counter_offer
                return {
                    "success": True,
                    "final_price": counter_offer,
                    "message": "Price accepted"
                }
                
        except Exception as e:
            logger.error(f"Error in price negotiation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def track_license_usage(
        self,
        agreement_id: str,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Track licensed content usage"""
        try:
            agreement = self.agreements.get(agreement_id)
            if not agreement:
                logger.error(f"Agreement not found: {agreement_id}")
                return False
                
            if not agreement.usage_tracking:
                agreement.usage_tracking = {
                    "total_uses": 0,
                    "usage_history": [],
                    "revenue_generated": 0.0
                }
            
            # Record usage
            usage_record = {
                "timestamp": datetime.now().isoformat(),
                "platform": usage_data.get("platform"),
                "views": usage_data.get("views", 0),
                "revenue": usage_data.get("revenue", 0.0),
                "location": usage_data.get("location")
            }
            
            agreement.usage_tracking["usage_history"].append(usage_record)
            agreement.usage_tracking["total_uses"] += 1
            agreement.usage_tracking["revenue_generated"] += usage_data.get("revenue", 0.0)
            
            # Check usage limits
            max_uses = agreement.terms.maximum_uses
            if max_uses and agreement.usage_tracking["total_uses"] >= max_uses:
                logger.warning(f"Usage limit reached for agreement {agreement_id}")
                # Could automatically terminate or notify
                
            logger.info(f"Usage tracked for agreement {agreement_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking license usage: {str(e)}")
            return False
    
    async def calculate_royalties(
        self,
        agreement_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """Calculate royalties for a period"""
        try:
            agreement = self.agreements.get(agreement_id)
            if not agreement:
                return {"error": "Agreement not found"}
                
            if not agreement.usage_tracking:
                return {"royalties": 0.0, "revenue": 0.0}
                
            # Filter usage in period
            period_usage = []
            for usage in agreement.usage_tracking["usage_history"]:
                usage_date = datetime.fromisoformat(usage["timestamp"])
                if period_start <= usage_date <= period_end:
                    period_usage.append(usage)
            
            total_revenue = sum(usage.get("revenue", 0.0) for usage in period_usage)
            royalty_rate = agreement.terms.royalty_rate
            
            royalties = total_revenue * royalty_rate
            
            return {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_revenue": total_revenue,
                "royalty_rate": royalty_rate,
                "royalties": royalties,
                "usage_count": len(period_usage)
            }
            
        except Exception as e:
            logger.error(f"Error calculating royalties: {str(e)}")
            return {"error": str(e)}
    
    async def generate_legal_templates(
        self,
        license_type: LicenseType,
        jurisdiction: str = "EU"
    ) -> Dict[str, str]:
        """Generate legal contract templates"""
        try:
            if license_type == LicenseType.EXCLUSIVE:
                template_key = "exclusive_license"
            elif license_type == LicenseType.SYNC:
                template_key = "sync_license"
            else:
                template_key = "basic_license"
                
            template = self.templates[template_key]
            
            # Generate clauses based on jurisdiction
            clauses = {}
            for clause_name in template["clauses"]:
                clauses[clause_name] = await self._generate_clause(clause_name, jurisdiction)
                
            return {
                "title": template["title"],
                "jurisdiction": jurisdiction,
                "clauses": clauses,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating legal templates: {str(e)}")
            return {}
    
    async def check_license_compliance(
        self,
        agreement_id: str
    ) -> Dict[str, Any]:
        """Check license compliance and violations"""
        try:
            agreement = self.agreements.get(agreement_id)
            if not agreement:
                return {"error": "Agreement not found"}
                
            compliance_issues = []
            
            # Check expiration
            if agreement.expires_at and datetime.now() > agreement.expires_at:
                compliance_issues.append("License has expired")
                
            # Check usage limits
            if agreement.terms.maximum_uses and agreement.usage_tracking:
                total_uses = agreement.usage_tracking["total_uses"]
                if total_uses > agreement.terms.maximum_uses:
                    compliance_issues.append(f"Usage limit exceeded: {total_uses}/{agreement.terms.maximum_uses}")
            
            # Check territory compliance
            if agreement.usage_tracking:
                for usage in agreement.usage_tracking["usage_history"]:
                    location = usage.get("location")
                    if location and not self._is_territory_allowed(location, agreement.terms.territory):
                        compliance_issues.append(f"Usage in unauthorized territory: {location}")
            
            return {
                "agreement_id": agreement_id,
                "compliant": len(compliance_issues) == 0,
                "issues": compliance_issues,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking license compliance: {str(e)}")
            return {"error": str(e)}
    
    async def get_active_licenses(self, content_id: str) -> List[LicensingAgreement]:
        """Get all active licenses for content"""
        try:
            active_licenses = []
            
            for agreement in self.agreements.values():
                if (agreement.content_id == content_id and 
                    agreement.status == LicenseStatus.ACTIVE and
                    (not agreement.expires_at or datetime.now() < agreement.expires_at)):
                    active_licenses.append(agreement)
                    
            return active_licenses
            
        except Exception as e:
            logger.error(f"Error getting active licenses: {str(e)}")
            return []
    
    def _normalize_territory(self, territory: str) -> str:
        """Normalize territory string for pricing"""
        territory_lower = territory.lower()
        
        if "worldwide" in territory_lower or "global" in territory_lower:
            return "worldwide"
        elif any(region in territory_lower for region in ["usa", "canada", "north america"]):
            return "north_america"
        elif any(region in territory_lower for region in ["europe", "eu", "uk"]):
            return "europe"
        elif any(region in territory_lower for region in ["asia", "japan", "china", "india"]):
            return "asia"
        else:
            return "single_country"
    
    def _is_territory_allowed(self, location: str, allowed_territory: str) -> bool:
        """Check if location is within allowed territory"""
        # Simplified territory checking
        if "worldwide" in allowed_territory.lower():
            return True
        
        location_lower = location.lower()
        territory_lower = allowed_territory.lower()
        
        return location_lower in territory_lower or territory_lower in location_lower
    
    async def _generate_contract_document(self, agreement: LicensingAgreement) -> Dict[str, Any]:
        """Generate contract document content"""
        try:
            return {
                "agreement_id": agreement.id,
                "title": f"Content License Agreement - {agreement.content_id}",
                "parties": {
                    "licensor": agreement.licensor_id,
                    "licensee": agreement.licensee_id
                },
                "terms": asdict(agreement.terms),
                "effective_date": agreement.created_at.isoformat(),
                "expiration_date": agreement.expires_at.isoformat() if agreement.expires_at else None,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating contract document: {str(e)}")
            return {}
    
    async def _generate_clause(self, clause_name: str, jurisdiction: str) -> str:
        """Generate legal clause text"""
        # Simplified clause generation
        clauses = {
            "grant_of_rights": f"The Licensor hereby grants to the Licensee a license to use the Content under the laws of {jurisdiction}.",
            "license_scope": "The scope of this license is limited to the specific rights and territories outlined in this agreement.",
            "payment_terms": "Payment shall be made according to the terms specified in this agreement.",
            "attribution": "The Licensee agrees to provide appropriate attribution to the Licensor.",
            "warranty_disclaimer": "The Content is provided 'as is' without warranty of any kind.",
            "limitation_liability": "The Licensor's liability is limited as provided by applicable law.",
            "termination": "This agreement may be terminated under the conditions specified herein.",
            "governing_law": f"This agreement shall be governed by the laws of {jurisdiction}.",
            "exclusivity_clause": "This license grants exclusive rights to the Licensee for the specified territory and duration.",
            "sync_rights": "This license includes synchronization rights for the specified project.",
            "project_details": "The licensed content may be used in connection with the specified project only.",
            "cue_sheets": "The Licensee agrees to provide cue sheets as required by performing rights organizations."
        }
        
        return clauses.get(clause_name, f"Standard {clause_name} clause applies.")