"""
Licensing Engine - Automated License Management and Enforcement

Comprehensive licensing system for content rights management, automated license generation,
terms enforcement, and revenue tracking for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass, asdict
import json
import uuid
from decimal import Decimal

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Types of content licenses."""
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    CREATIVE_COMMONS = "creative_commons"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    PROMOTIONAL = "promotional"


class LicenseStatus(Enum):
    """License status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING = "pending"
    TERMINATED = "terminated"


class UsageType(Enum):
    """Types of content usage."""
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SYNCHRONIZATION = "synchronization"
    MERCHANDISING = "merchandising"


class LicenseScope(Enum):
    """Geographic scope of license."""
    WORLDWIDE = "worldwide"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class LicenseTerms:
    """License terms and conditions."""
    usage_types: List[UsageType]
    geographic_scope: LicenseScope
    duration_days: Optional[int]
    max_uses: Optional[int]
    max_impressions: Optional[int]
    attribution_required: bool
    modification_allowed: bool
    commercial_use_allowed: bool
    resale_allowed: bool
    exclusive_rights: bool
    territory_restrictions: List[str]
    platform_restrictions: List[str]


@dataclass
class PricingModel:
    """License pricing configuration."""
    base_price: Decimal
    currency: str
    pricing_type: str  # fixed, tier, usage_based, revenue_share
    usage_tiers: Optional[Dict[str, Decimal]]
    revenue_share_percentage: Optional[float]
    minimum_fee: Optional[Decimal]
    additional_fees: Dict[str, Decimal]


@dataclass
class License:
    """License record structure."""
    license_id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    license_type: LicenseType
    status: LicenseStatus
    terms: LicenseTerms
    pricing: PricingModel
    issued_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime]
    usage_count: int
    impression_count: int
    revenue_generated: Decimal
    last_used: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class LicenseUsage:
    """License usage tracking."""
    usage_id: str
    license_id: str
    user_id: str
    usage_type: UsageType
    platform: str
    usage_date: datetime
    content_location: str
    audience_size: Optional[int]
    revenue_generated: Optional[Decimal]
    metadata: Dict[str, Any]


class LicensingEngine:
    """
    Comprehensive licensing engine for content rights management.
    
    Handles license generation, enforcement, usage tracking,
    and automated revenue distribution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Licensing Engine.
        
        Args:
            config: Configuration dictionary with database connections
        """
        self.config = config
        self.db_config = config.get("database", {})
        self.licensing_config = config.get("licensing", {})
        
        # License registries
        self.licenses: Dict[str, License] = {}
        self.usage_records: Dict[str, LicenseUsage] = {}
        
        # Engine settings
        self.auto_licensing_enabled = self.licensing_config.get("auto_licensing", True)
        self.usage_monitoring_enabled = self.licensing_config.get("usage_monitoring", True)
        self.revenue_tracking_enabled = self.licensing_config.get("revenue_tracking", True)
        
        # Default license templates
        self.license_templates = self._initialize_license_templates()
        
        logger.info("Licensing Engine initialized successfully")
    
    async def create_license(
        self,
        content_id: str,
        licensor_id: str,
        licensee_id: str,
        license_type: str,
        terms: Dict[str, Any],
        pricing: Dict[str, Any],
        duration_days: Optional[int] = None,
        custom_terms: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new content license with specified terms.
        
        Args:
            content_id: ID of content being licensed
            licensor_id: ID of content owner/licensor
            licensee_id: ID of license purchaser/licensee
            license_type: Type of license to create
            terms: License terms and conditions
            pricing: Pricing model configuration
            duration_days: License duration in days
            custom_terms: Custom terms to override defaults
            
        Returns:
            License creation results
        """



        try:
            # Generate unique license ID
            license_id = f"lic_{uuid.uuid4().hex[:12]}"
            
            # Parse terms and pricing
            license_terms = self._parse_license_terms(terms, custom_terms)
            pricing_model = self._parse_pricing_model(pricing)
            
            # Calculate validity period
            valid_from = datetime.utcnow()
            valid_until = None
            if duration_days:
                valid_until = valid_from + timedelta(days=duration_days)
            elif license_terms.duration_days:
                valid_until = valid_from + timedelta(days=license_terms.duration_days)
            
            # Create license record
            license_record = License(
                license_id=license_id,
                content_id=content_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                license_type=LicenseType(license_type),
                status=LicenseStatus.ACTIVE,
                terms=license_terms,
                pricing=pricing_model,
                issued_at=datetime.utcnow(),
                valid_from=valid_from,
                valid_until=valid_until,
                usage_count=0,
                impression_count=0,
                revenue_generated=Decimal('0.00'),
                last_used=None,
                metadata={}
            )
            
            # Store license
            self.licenses[license_id] = license_record
            
            # Process payment if required
            payment_result = await self._process_license_payment(
                license_record, licensee_id
            )
            
            # Set up usage monitoring
            if self.usage_monitoring_enabled:
                await self._setup_usage_monitoring(license_record)
            
            license_result = {
                "license_id": license_id,
                "content_id": content_id,
                "status": "active",
                "issued_at": license_record.issued_at.isoformat(),
                "valid_from": valid_from.isoformat(),
                "valid_until": valid_until.isoformat() if valid_until else None,
                "license_type": license_type,
                "payment_required": payment_result.get("payment_required", False),
                "payment_status": payment_result.get("status", "completed"),
                "terms_summary": self._generate_terms_summary(license_terms),
                "next_steps": []
            }
            
            # Generate next steps
            if payment_result.get("payment_required"):
                license_result["next_steps"].append("Complete payment to activate license")
            else:
                license_result["next_steps"].extend([
                    "License active and ready for use",
                    "Usage tracking enabled",
                    "Revenue sharing configured"
                ])
            
            # Log license creation
            await self._log_license_creation(license_record, license_result)
            
            return license_result
            
        except Exception as e:
            logger.error(f"Error creating license: {str(e)}")
            raise
    
    async def verify_licensing(
        self,
        content_id: str,
        user_id: str,
        usage_type: str = "commercial",
        platform: str = "web"
    ) -> Dict[str, Any]:
        """
        Verify licensing status for content usage.
        
        Args:
            content_id: ID of content to check
            user_id: ID of user attempting to use content
            usage_type: Type of intended usage
            platform: Platform where content will be used
            
        Returns:
            Licensing verification results
        """



        try:
            verification_result = {
                "content_id": content_id,
                "user_id": user_id,
                "verified_at": datetime.utcnow().isoformat(),
                "licensed": False,
                "license_found": False,
                "license_valid": False,
                "usage_permitted": False,
                "restrictions": [],
                "recommendations": [],
                "active_licenses": []
            }
            
            # Find licenses for this content and user
            user_licenses = await self._find_user_licenses(content_id, user_id)
            
            if user_licenses:
                verification_result["license_found"] = True
                verification_result["active_licenses"] = [
                    {
                        "license_id": lic.license_id,
                        "license_type": lic.license_type.value,
                        "status": lic.status.value,
                        "valid_until": lic.valid_until.isoformat() if lic.valid_until else None
                    }
                    for lic in user_licenses
                ]
                
                # Check license validity
                valid_licenses = [lic for lic in user_licenses if self._is_license_valid(lic)]
                
                if valid_licenses:
                    verification_result["license_valid"] = True
                    
                    # Check usage permissions
                    usage_check = await self._check_usage_permissions(
                        valid_licenses, usage_type, platform
                    )
                    
                    verification_result.update(usage_check)
                    
                    if usage_check["usage_permitted"]:
                        verification_result["licensed"] = True
                else:
                    verification_result["restrictions"].append("All licenses expired or invalid")
            else:
                verification_result["recommendations"].extend([
                    f"Purchase license for {usage_type} usage",
                    "Contact content owner for licensing options",
                    "Check if content is available under Creative Commons"
                ])
            
            # Check for public domain or Creative Commons
            if not verification_result["licensed"]:
                public_domain_check = await self._check_public_domain_status(content_id)
                if public_domain_check["is_public_domain"]:
                    verification_result["licensed"] = True
                    verification_result["license_found"] = True
                    verification_result["restrictions"] = public_domain_check.get("restrictions", [])
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying licensing: {str(e)}")
            raise
    
    async def track_usage(
        self,
        license_id: str,
        user_id: str,
        usage_type: str,
        platform: str,
        content_location: str,
        audience_size: Optional[int] = None,
        revenue_generated: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track content usage under a license.
        
        Args:
            license_id: ID of license being used
            user_id: ID of user using the content
            usage_type: Type of usage
            platform: Platform where content is used
            content_location: URL or location of content usage
            audience_size: Size of audience reached
            revenue_generated: Revenue generated from usage
            metadata: Additional usage metadata
            
        Returns:
            Usage tracking results
        """



        try:
            # Verify license exists and is valid
            if license_id not in self.licenses:
                raise ValueError(f"License {license_id} not found")
            
            license_record = self.licenses[license_id]
            
            # Check if usage is permitted
            if not self._is_license_valid(license_record):
                raise ValueError(f"License {license_id} is not valid")
            
            # Generate usage ID
            usage_id = f"usage_{uuid.uuid4().hex[:12]}"
            
            # Create usage record
            usage_record = LicenseUsage(
                usage_id=usage_id,
                license_id=license_id,
                user_id=user_id,
                usage_type=UsageType(usage_type),
                platform=platform,
                usage_date=datetime.utcnow(),
                content_location=content_location,
                audience_size=audience_size,
                revenue_generated=Decimal(str(revenue_generated)) if revenue_generated else None,
                metadata=metadata or {}
            )
            
            # Store usage record
            self.usage_records[usage_id] = usage_record
            
            # Update license usage counters
            license_record.usage_count += 1
            if audience_size:
                license_record.impression_count += audience_size
            if revenue_generated:
                license_record.revenue_generated += Decimal(str(revenue_generated))
            license_record.last_used = datetime.utcnow()
            
            # Check usage limits
            usage_limits_check = await self._check_usage_limits(license_record)
            
            # Process revenue sharing if applicable
            revenue_sharing_result = None
            if revenue_generated and self.revenue_tracking_enabled:
                revenue_sharing_result = await self._process_revenue_sharing(
                    license_record, Decimal(str(revenue_generated))
                )
            
            usage_result = {
                "usage_id": usage_id,
                "license_id": license_id,
                "tracked_at": usage_record.usage_date.isoformat(),
                "usage_type": usage_type,
                "platform": platform,
                "audience_size": audience_size,
                "revenue_generated": float(revenue_generated) if revenue_generated else None,
                "total_usage_count": license_record.usage_count,
                "total_impressions": license_record.impression_count,
                "total_revenue": float(license_record.revenue_generated),
                "usage_limits_status": usage_limits_check,
                "revenue_sharing": revenue_sharing_result,
                "warnings": []
            }
            
            # Check for warnings
            if usage_limits_check.get("approaching_limit"):
                usage_result["warnings"].append("Approaching usage limit")
            
            if usage_limits_check.get("limit_exceeded"):
                usage_result["warnings"].append("Usage limit exceeded")
                # May need to suspend license or charge additional fees
            
            # Log usage tracking
            await self._log_usage_tracking(usage_record, usage_result)
            
            return usage_result
            
        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}")
            raise
    
    async def get_licensing_summary(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get licensing summary for reporting.
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Start date for summary period
            end_date: End date for summary period
            
        Returns:
            Licensing summary
        """



        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            summary = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "user_id": user_id,
                "license_summary": {
                    "total_licenses": 0,
                    "active_licenses": 0,
                    "expired_licenses": 0,
                    "revenue_generated": 0.0,
                    "by_type": {}
                },
                "usage_summary": {
                    "total_usage": 0,
                    "total_impressions": 0,
                    "by_platform": {},
                    "by_usage_type": {}
                },
                "revenue_summary": {
                    "total_revenue": 0.0,
                    "licensing_revenue": 0.0,
                    "usage_revenue": 0.0,
                    "by_license_type": {}
                }
            }
            
            # Filter records by criteria
            filtered_licenses = self._filter_licenses_by_criteria(
                user_id, start_date, end_date
            )
            filtered_usage = self._filter_usage_by_criteria(
                user_id, start_date, end_date
            )
            
            # Calculate license summary
            summary["license_summary"]["total_licenses"] = len(filtered_licenses)
            
            for license_record in filtered_licenses:
                # Count by status
                if license_record.status == LicenseStatus.ACTIVE:
                    summary["license_summary"]["active_licenses"] += 1
                elif license_record.status == LicenseStatus.EXPIRED:
                    summary["license_summary"]["expired_licenses"] += 1
                
                # Count by type
                license_type = license_record.license_type.value
                if license_type not in summary["license_summary"]["by_type"]:
                    summary["license_summary"]["by_type"][license_type] = 0
                summary["license_summary"]["by_type"][license_type] += 1
                
                # Sum revenue
                summary["license_summary"]["revenue_generated"] += float(license_record.revenue_generated)
            
            # Calculate usage summary
            summary["usage_summary"]["total_usage"] = len(filtered_usage)
            
            for usage_record in filtered_usage:
                # Count impressions
                if usage_record.audience_size:
                    summary["usage_summary"]["total_impressions"] += usage_record.audience_size
                
                # Count by platform
                platform = usage_record.platform
                if platform not in summary["usage_summary"]["by_platform"]:
                    summary["usage_summary"]["by_platform"][platform] = 0
                summary["usage_summary"]["by_platform"][platform] += 1
                
                # Count by usage type
                usage_type = usage_record.usage_type.value
                if usage_type not in summary["usage_summary"]["by_usage_type"]:
                    summary["usage_summary"]["by_usage_type"][usage_type] = 0
                summary["usage_summary"]["by_usage_type"][usage_type] += 1
                
                # Sum revenue
                if usage_record.revenue_generated:
                    summary["revenue_summary"]["usage_revenue"] += float(usage_record.revenue_generated)
            
            # Calculate total revenue
            summary["revenue_summary"]["total_revenue"] = (
                summary["license_summary"]["revenue_generated"] + 
                summary["revenue_summary"]["usage_revenue"]
            )
            summary["revenue_summary"]["licensing_revenue"] = summary["license_summary"]["revenue_generated"]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating licensing summary: {str(e)}")
            raise
    
    async def revoke_license(
        self,
        license_id: str,
        reason: str,
        revoked_by: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Revoke a license with specified reason.
        
        Args:
            license_id: ID of license to revoke
            reason: Reason for revocation
            revoked_by: User or system revoking the license
            immediate: Whether revocation is immediate
            
        Returns:
            License revocation results
        """



        try:
            if license_id not in self.licenses:
                raise ValueError(f"License {license_id} not found")
            
            license_record = self.licenses[license_id]
            old_status = license_record.status
            
            # Update license status
            license_record.status = LicenseStatus.REVOKED
            license_record.metadata.update({
                "revocation_date": datetime.utcnow().isoformat(),
                "revocation_reason": reason,
                "revoked_by": revoked_by,
                "immediate_revocation": immediate
            })
            
            # Notify licensee
            await self._notify_license_revocation(license_record, reason)
            
            # If not immediate, may allow grace period
            grace_period_end = None
            if not immediate:
                grace_period_end = datetime.utcnow() + timedelta(days=7)
                license_record.metadata["grace_period_end"] = grace_period_end.isoformat()
            
            revocation_result = {
                "license_id": license_id,
                "revoked_at": datetime.utcnow().isoformat(),
                "old_status": old_status.value,
                "new_status": "revoked",
                "reason": reason,
                "revoked_by": revoked_by,
                "immediate": immediate,
                "grace_period_end": grace_period_end.isoformat() if grace_period_end else None,
                "licensee_notified": True
            }
            
            # Log revocation
            await self._log_license_revocation(license_record, revocation_result)
            
            return revocation_result
            
        except Exception as e:
            logger.error(f"Error revoking license: {str(e)}")
            raise
    
    # Private helper methods
    def _initialize_license_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default license templates."""



        return {
            "royalty_free": {
                "terms": {
                    "attribution_required": False,
                    "modification_allowed": True,
                    "commercial_use_allowed": True,
                    "resale_allowed": False,
                    "exclusive_rights": False
                },
                "pricing": {
                    "pricing_type": "fixed",
                    "base_price": "99.00"
                }
            },
            "rights_managed": {
                "terms": {
                    "attribution_required": True,
                    "modification_allowed": False,
                    "commercial_use_allowed": True,
                    "resale_allowed": False,
                    "exclusive_rights": True
                },
                "pricing": {
                    "pricing_type": "usage_based",
                    "base_price": "199.00"
                }
            },
            "creative_commons": {
                "terms": {
                    "attribution_required": True,
                    "modification_allowed": True,
                    "commercial_use_allowed": False,
                    "resale_allowed": False,
                    "exclusive_rights": False
                },
                "pricing": {
                    "pricing_type": "fixed",
                    "base_price": "0.00"
                }
            }
        }
    
    def _parse_license_terms(
        self, 
        terms: Dict[str, Any], 
        custom_terms: Optional[Dict[str, Any]]
    ) -> LicenseTerms:
        """Parse license terms from configuration."""
        # Merge custom terms with defaults
        final_terms = {**terms}
        if custom_terms:
            final_terms.update(custom_terms)
        
        return LicenseTerms(
            usage_types=[UsageType(ut) for ut in final_terms.get("usage_types", ["commercial"])],
            geographic_scope=LicenseScope(final_terms.get("geographic_scope", "worldwide")),
            duration_days=final_terms.get("duration_days"),
            max_uses=final_terms.get("max_uses"),
            max_impressions=final_terms.get("max_impressions"),
            attribution_required=final_terms.get("attribution_required", False),
            modification_allowed=final_terms.get("modification_allowed", False),
            commercial_use_allowed=final_terms.get("commercial_use_allowed", True),
            resale_allowed=final_terms.get("resale_allowed", False),
            exclusive_rights=final_terms.get("exclusive_rights", False),
            territory_restrictions=final_terms.get("territory_restrictions", []),
            platform_restrictions=final_terms.get("platform_restrictions", [])
        )
    
    def _parse_pricing_model(self, pricing: Dict[str, Any]) -> PricingModel:
        """Parse pricing model from configuration."""



        return PricingModel(
            base_price=Decimal(str(pricing.get("base_price", "0.00"))),
            currency=pricing.get("currency", "EUR"),
            pricing_type=pricing.get("pricing_type", "fixed"),
            usage_tiers=pricing.get("usage_tiers"),
            revenue_share_percentage=pricing.get("revenue_share_percentage"),
            minimum_fee=Decimal(str(pricing.get("minimum_fee", "0.00"))) if pricing.get("minimum_fee") else None,
            additional_fees=pricing.get("additional_fees", {})
        )
    
    def _generate_terms_summary(self, terms: LicenseTerms) -> Dict[str, Any]:
        """Generate human-readable terms summary."""



        return {
            "usage_types": [ut.value for ut in terms.usage_types],
            "geographic_scope": terms.geographic_scope.value,
            "duration": f"{terms.duration_days} days" if terms.duration_days else "Unlimited",
            "commercial_use": "Allowed" if terms.commercial_use_allowed else "Not allowed",
            "attribution_required": terms.attribution_required,
            "modification_allowed": terms.modification_allowed,
            "exclusive": terms.exclusive_rights
        }
    
    async def _find_user_licenses(self, content_id: str, user_id: str) -> List[License]:
        """Find active licenses for user and content."""
        user_licenses = []
        
        for license_record in self.licenses.values():
            if (license_record.content_id == content_id and 
                license_record.licensee_id == user_id):
                user_licenses.append(license_record)
        
        return user_licenses
    
    def _is_license_valid(self, license_record: License) -> bool:
        """Check if license is currently valid."""
        # Check status
        if license_record.status != LicenseStatus.ACTIVE:
            return False
        
        # Check expiration
        if (license_record.valid_until and 
            license_record.valid_until <= datetime.utcnow()):
            license_record.status = LicenseStatus.EXPIRED
            return False
        
        # Check usage limits
        if (license_record.terms.max_uses and 
            license_record.usage_count >= license_record.terms.max_uses):
            return False
        
        if (license_record.terms.max_impressions and 
            license_record.impression_count >= license_record.terms.max_impressions):
            return False
        
        return True
    
    async def _check_usage_permissions(
        self,
        licenses: List[License],
        usage_type: str,
        platform: str
    ) -> Dict[str, Any]:
        """Check if usage is permitted under available licenses."""
        usage_permitted = False
        restrictions = []
        
        for license_record in licenses:
            # Check usage type
            if UsageType(usage_type) not in license_record.terms.usage_types:
                restrictions.append(f"Usage type '{usage_type}' not permitted")
                continue
            
            # Check platform restrictions
            if (license_record.terms.platform_restrictions and 
                platform in license_record.terms.platform_restrictions):
                restrictions.append(f"Platform '{platform}' restricted")
                continue
            
            # Check commercial use
            if (usage_type == "commercial" and 
                not license_record.terms.commercial_use_allowed):
                restrictions.append("Commercial use not permitted")
                continue
            
            usage_permitted = True
            break
        
        return {
            "usage_permitted": usage_permitted,
            "restrictions": restrictions
        }
    
    async def _check_public_domain_status(self, content_id: str) -> Dict[str, Any]:
        """Check if content is in public domain."""
        # Placeholder for public domain checking logic
        return {
            "is_public_domain": False,
            "restrictions": []
        }
    
    async def _check_usage_limits(self, license_record: License) -> Dict[str, Any]:
        """Check usage limits for license."""
        limits_status = {
            "within_limits": True,
            "approaching_limit": False,
            "limit_exceeded": False,
            "details": {}
        }
        
        # Check usage count
        if license_record.terms.max_uses:
            usage_percentage = (license_record.usage_count / license_record.terms.max_uses) * 100
            limits_status["details"]["usage_percentage"] = usage_percentage
            
            if usage_percentage >= 100:
                limits_status["limit_exceeded"] = True
                limits_status["within_limits"] = False
            elif usage_percentage >= 80:
                limits_status["approaching_limit"] = True
        
        # Check impression count
        if license_record.terms.max_impressions:
            impression_percentage = (license_record.impression_count / license_record.terms.max_impressions) * 100
            limits_status["details"]["impression_percentage"] = impression_percentage
            
            if impression_percentage >= 100:
                limits_status["limit_exceeded"] = True
                limits_status["within_limits"] = False
            elif impression_percentage >= 80:
                limits_status["approaching_limit"] = True
        
        return limits_status
    
    def _filter_licenses_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[License]:
        """Filter licenses by criteria."""
        filtered = []
        
        for license_record in self.licenses.values():
            # Filter by user (as licensor or licensee)
            if user_id:
                is_licensor = license_record.licensor_id == user_id
                is_licensee = license_record.licensee_id == user_id
                if not (is_licensor or is_licensee):
                    continue
            
            # Filter by date range
            if (license_record.issued_at < start_date or 
                license_record.issued_at > end_date):
                continue
            
            filtered.append(license_record)
        
        return filtered
    
    def _filter_usage_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[LicenseUsage]:
        """Filter usage records by criteria."""
        filtered = []
        
        for usage_record in self.usage_records.values():
            # Filter by user
            if user_id and usage_record.user_id != user_id:
                continue
            
            # Filter by date range
            if (usage_record.usage_date < start_date or 
                usage_record.usage_date > end_date):
                continue
            
            filtered.append(usage_record)
        
        return filtered
    
    # Placeholder methods for external integrations
    async def _process_license_payment(
        self, 
        license_record: License, 
        licensee_id: str
    ) -> Dict[str, Any]:
        """Process payment for license."""
        if license_record.pricing.base_price > 0:
            return {
                "payment_required": True,
                "status": "pending",
                "amount": float(license_record.pricing.base_price),
                "currency": license_record.pricing.currency
            }
        return {"payment_required": False, "status": "completed"}
    
    async def _setup_usage_monitoring(self, license_record: License) -> None:
        """Set up usage monitoring for license."""
        logger.info(f"Setting up usage monitoring for license {license_record.license_id}")
    
    async def _process_revenue_sharing(
        self, 
        license_record: License, 
        revenue: Decimal
    ) -> Dict[str, Any]:
        """Process revenue sharing for license usage."""
        if license_record.pricing.revenue_share_percentage:
            share_amount = revenue * Decimal(str(license_record.pricing.revenue_share_percentage / 100))
            return {
                "revenue_shared": True,
                "share_percentage": license_record.pricing.revenue_share_percentage,
                "share_amount": float(share_amount),
                "licensor_payout": float(share_amount)
            }
        return {"revenue_shared": False}
    
    async def _notify_license_revocation(self, license_record: License, reason: str) -> None:
        """Notify licensee of license revocation."""
        logger.info(f"Notifying licensee {license_record.licensee_id} of license revocation")
    
    # Logging methods
    async def _log_license_creation(self, license_record: License, result: Dict[str, Any]) -> None:
        """Log license creation."""
        logger.info(f"License created: {license_record.license_id} for content {license_record.content_id}")
    
    async def _log_usage_tracking(self, usage_record: LicenseUsage, result: Dict[str, Any]) -> None:
        """Log usage tracking."""
        logger.info(f"Usage tracked: {usage_record.usage_id} for license {usage_record.license_id}")
    
    async def _log_license_revocation(self, license_record: License, result: Dict[str, Any]) -> None:
        """Log license revocation."""
        logger.info(f"License revoked: {license_record.license_id} - Reason: {result['reason']}")
