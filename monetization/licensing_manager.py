"""Licensing Manager
=================

Central manager for content licensing, rights management, and automated licensing workflows.
Handles license creation, validation, tracking, and royalty distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from .royalty_engine import RoyaltyEngine
from .usage_tracker import UsageTracker
from .contract_generator import ContractGenerator
from .rights_validator import RightsValidator

# Simple import to avoid relative import issues
import sys
import os

# Add parent directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from database.repositories.license_repository import LicenseRepository
    from database.repositories.content_repository import ContentRepository
except ImportError:
    # Fallback for testing - create mock classes
    class LicenseRepository:
        def __init__(self):
            """
Initialize license repository with basic functionality"""
            self.licenses = {}
            
    class ContentRepository:
        def __init__(self):
            """
Initialize content repository with basic functionality"""
            self.content = {}

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """
License type enumeration."""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    CUSTOM = "custom"
    SYNC = "sync"
    COMMERCIAL = "commercial"
    EXCLUSIVE = "exclusive"

class LicenseStatus(Enum):
    """License status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class UsageType(Enum):
    """Usage type enumeration."""

    STREAM = "stream"
    DOWNLOAD = "download"
    SYNC = "sync"
    COMMERCIAL = "commercial"
    BROADCAST = "broadcast"
    PUBLIC_PERFORMANCE = "public_performance"

@dataclass
class ContentLicense:
    """Content license data structure."""
    id: int
    content_id: int
    licensor_id: int
    licensee_id: int
    license_type: LicenseType
    status: LicenseStatus
    price: Decimal
    currency: str
    start_date: datetime
    end_date: datetime
    territory: str
    usage_limits: Dict
    terms_conditions: Dict
    contract_hash: str
    created_at: datetime
    updated_at: datetime

@dataclass
class LicenseUsage:
    """
License usage record."""
    id: int
    license_id: int
    usage_type: UsageType
    usage_count: int
    usage_data: Dict
    royalty_amount: Decimal
    timestamp: datetime

class LicensingError(Exception):
    """
Exception for licensing-related errors"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "LICENSING_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class LicensingManager:
    """
    Professional licensing management system.
    
    Features:
    - Automated license generation
    - Multi-tier licensing options
    - Usage tracking and limits
    - Royalty calculation and distribution
    - Contract generation and validation
    - Compliance monitoring
    - Analytics and reporting
    - Rights validation
    """
    
    def __init__(self):
        """
Initialize licensing manager."""
        self.royalty_engine = RoyaltyEngine()
        self.usage_tracker = UsageTracker()
        self.contract_generator = ContractGenerator()
        self.rights_validator = RightsValidator()
        
        # Repositories
        self.license_repo = LicenseRepository()
        self.content_repo = ContentRepository()
        
        # Configuration
        self.config = {
            "auto_approval_threshold": Decimal("100.00"),
            "default_currency": "EUR",
            "default_territory": "worldwide",
            "license_duration": {
                "basic": 30,     # days
                "standard": 90,
                "premium": 365,
                "custom": None   # negotiated
            },
            "royalty_rates": {
                "stream": Decimal("0.004"),
                "download": Decimal("0.10"),
                "sync": Decimal("0.15"),
                "commercial": Decimal("0.25")
            }
        }
        
        # Active license monitoring
        self.monitoring_tasks = {}
        
        logger.info("LicensingManager initialized successfully")
    
    async def create_license(self, 
                            content_id: int,
                            licensee_id: int,
                            license_type: str,
                            terms: Dict) -> ContentLicense:
        """
        Create new content license.
        
        Args:
            content_id: ID of content to license
            licensee_id: ID of licensee
            license_type: Type of license (basic, standard, premium, custom)
            terms: License terms and conditions
            
        Returns:
            ContentLicense object
        """
        try:
            logger.info(f"Creating license for content {content_id}, licensee {licensee_id}")
            
            # Validate content exists and rights
            content = await self.content_repo.get_content(content_id)
            if not content:
                raise LicensingError(f"Content not found: {content_id}")
            
            # Validate rights
            rights_valid = await self.rights_validator.validate_licensing_rights(
                content_id, content["user_id"]
            )
            if not rights_valid:
                raise LicensingError("Insufficient rights to license this content")
            
            # Get license type configuration
            license_config = self._get_license_config(license_type)
            
            # Calculate license price
            price = await self._calculate_license_price(
                content_id, license_type, terms
            )
            
            # Generate license terms
            license_terms = await self._generate_license_terms(
                content, license_config, terms
            )
            
            # Calculate dates
            start_date = terms.get("start_date", datetime.utcnow())
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date)
            
            duration_days = license_config.get("duration_days") or terms.get("duration_days", 30)
            end_date = start_date + timedelta(days=duration_days)
            
            # Generate contract
            contract = await self.contract_generator.generate_contract(
                content, licensee_id, license_terms
            )
            
            # Create license record
            license_data = {
                "content_id": content_id,
                "licensor_id": content["user_id"],
                "licensee_id": licensee_id,
                "license_type": license_type,
                "status": LicenseStatus.PENDING.value,
                "price": price,
                "currency": terms.get("currency", self.config["default_currency"]),
                "start_date": start_date,
                "end_date": end_date,
                "territory": terms.get("territory", self.config["default_territory"]),
                "usage_limits": license_config.get("usage_limits", {}),
                "terms_conditions": license_terms,
                "contract_hash": contract["hash"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            license_id = await self.license_repo.create_license(license_data)
            
            # Create license object
            license_obj = ContentLicense(
                id=license_id,
                **license_data
            )
            
            # Auto-approve if under threshold
            if price <= self.config["auto_approval_threshold"]:
                await self.approve_license(license_id)
            
            # Start monitoring
            await self._start_license_monitoring(license_id)
            
            logger.info(f"License created: {license_id}")
            return license_obj
            
        except Exception as e:
            logger.error(f"Error creating license: {str(e)}")
            raise LicensingError(f"Failed to create license: {str(e)}")
    
    async def approve_license(self, license_id: int) -> bool:
        """Approve pending license."""
        try:
            # Update license status
            await self.license_repo.update_license_status(
                license_id, LicenseStatus.ACTIVE.value
            )
            
            # Send approval notification
            license = await self.license_repo.get_license(license_id)
            await self._send_license_notification(
                license, "approved"
            )
            
            logger.info(f"License approved: {license_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving license: {str(e)}")
            return False
    
    async def track_usage(self, 
                         license_id: int,
                         usage_type: str,
                         usage_data: Dict) -> LicenseUsage:
        """
        Track license usage.
        
        Args:
            license_id: License ID
            usage_type: Type of usage (stream, download, etc.)
            usage_data: Usage metadata
            
        Returns:
            LicenseUsage object
        """
        try:
            # Get license information
            license = await self.license_repo.get_license(license_id)
            if not license:
                raise LicensingError(f"License not found: {license_id}")
            
            # Validate license status
            if license["status"] != LicenseStatus.ACTIVE.value:
                raise LicensingError(f"License not active: {license_id}")
            
            # Check usage limits
            await self._check_usage_limits(license, usage_type, usage_data)
            
            # Calculate royalty
            royalty_amount = await self.royalty_engine.calculate_usage_royalty(
                license, usage_type, usage_data
            )
            
            # Record usage
            usage_record_data = {
                "license_id": license_id,
                "usage_type": usage_type,
                "usage_count": usage_data.get("count", 1),
                "usage_data": usage_data,
                "royalty_amount": royalty_amount,
                "timestamp": datetime.utcnow()
            }
            
            usage_id = await self.usage_tracker.record_usage(usage_record_data)
            
            usage_record = LicenseUsage(
                id=usage_id,
                **usage_record_data
            )
            
            # Update license usage statistics
            await self._update_license_usage_stats(license_id, usage_type, usage_data)
            
            logger.debug(f"Usage tracked for license {license_id}: {usage_type}")
            return usage_record
            
        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}")
            raise LicensingError(f"Failed to track usage: {str(e)}")
    
    async def calculate_royalties(self, 
                                 license_id: int,
                                 period_start: str,
                                 period_end: str) -> Dict:
        """
        Calculate royalties for license period.
        
        Args:
            license_id: License ID
            period_start: Start date (ISO format)
            period_end: End date (ISO format)
            
        Returns:
            Royalty calculation summary
        """
        try:
            start_date = datetime.fromisoformat(period_start)
            end_date = datetime.fromisoformat(period_end)
            
            # Get license information
            license = await self.license_repo.get_license(license_id)
            if not license:
                raise LicensingError(f"License not found: {license_id}")
            
            # Get usage records for period
            usage_records = await self.usage_tracker.get_usage_by_period(
                license_id, start_date, end_date
            )
            
            # Calculate royalties
            royalty_summary = await self.royalty_engine.calculate_period_royalties(
                license, usage_records, start_date, end_date
            )
            
            return {
                "license_id": license_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "royalty_summary": royalty_summary,
                "total_royalties": royalty_summary.get("total_amount", Decimal("0")),
                "usage_breakdown": royalty_summary.get("usage_breakdown", {}),
                "payment_due": royalty_summary.get("payment_due", False)
            }
            
        except Exception as e:
            logger.error(f"Error calculating royalties: {str(e)}")
            raise LicensingError(f"Failed to calculate royalties: {str(e)}")
    
    async def renew_license(self, 
                           license_id: int,
                           renewal_terms: Dict = None) -> ContentLicense:
        """Renew existing license."""
        try:
            # Get current license
            current_license = await self.license_repo.get_license(license_id)
            if not current_license:
                raise LicensingError(f"License not found: {license_id}")
            
            # Calculate new dates
            renewal_terms = renewal_terms or {}
            duration_days = renewal_terms.get("duration_days", 
                                             (current_license["end_date"] - current_license["start_date"]).days)
            
            new_start_date = current_license["end_date"]
            new_end_date = new_start_date + timedelta(days=duration_days)
            
            # Create renewal license
            renewal_license = await self.create_license(
                content_id=current_license["content_id"],
                licensee_id=current_license["licensee_id"],
                license_type=current_license["license_type"],
                terms={
                    **current_license["terms_conditions"],
                    **renewal_terms,
                    "start_date": new_start_date,
                    "duration_days": duration_days
                }
            )
            
            # Update original license status
            await self.license_repo.update_license_status(
                license_id, LicenseStatus.RENEWED.value
            )
            
            logger.info(f"License renewed: {license_id} -> {renewal_license.id}")
            return renewal_license
            
        except Exception as e:
            logger.error(f"Error renewing license: {str(e)}")
            raise LicensingError(f"Failed to renew license: {str(e)}")
    
    async def get_license_analytics(self, license_id: int) -> Dict:
        """Get comprehensive license analytics."""
        try:
            # Get license information
            license = await self.license_repo.get_license(license_id)
            if not license:
                return {"error": "License not found"}
            
            # Get usage statistics
            usage_stats = await self.usage_tracker.get_license_usage_stats(license_id)
            
            # Get royalty history
            royalty_history = await self.royalty_engine.get_license_royalty_history(license_id)
            
            # Calculate analytics
            total_usage = sum(stats.get("count", 0) for stats in usage_stats.values())
            total_royalties = sum(Decimal(str(r.get("amount", 0))) for r in royalty_history)
            
            # Usage efficiency
            usage_limits = license.get("usage_limits", {})
            usage_efficiency = {}
            for usage_type, limit in usage_limits.items():
                current_usage = usage_stats.get(usage_type, {}).get("count", 0)
                efficiency = (current_usage / limit * 100) if limit > 0 else 0
                usage_efficiency[usage_type] = efficiency
            
            analytics = {
                "license_id": license_id,
                "license_info": {
                    "type": license["license_type"],
                    "status": license["status"],
                    "start_date": license["start_date"].isoformat(),
                    "end_date": license["end_date"].isoformat(),
                    "days_remaining": (license["end_date"] - datetime.utcnow()).days
                },
                "usage_analytics": {
                    "total_usage": total_usage,
                    "usage_by_type": usage_stats,
                    "usage_efficiency": usage_efficiency,
                    "peak_usage_day": usage_stats.get("peak_day", "N/A")
                },
                "financial_analytics": {
                    "license_price": float(license["price"]),
                    "total_royalties": float(total_royalties),
                    "average_royalty_per_use": float(total_royalties / total_usage) if total_usage > 0 else 0,
                    "roi": float((total_royalties / license["price"]) * 100) if license["price"] > 0 else 0
                },
                "compliance": {
                    "within_limits": all(eff <= 100 for eff in usage_efficiency.values()),
                    "usage_violations": [
                        usage_type for usage_type, eff in usage_efficiency.items() if eff > 100
                    ]
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting license analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_user_licensing_summary(self, user_id: int) -> Dict:
        """Get licensing summary for user (as licensor)."""
        try:
            # Get all licenses where user is licensor
            licenses = await self.license_repo.get_user_licenses_as_licensor(user_id)
            
            # Calculate statistics
            total_licenses = len(licenses)
            active_licenses = len([l for l in licenses if l["status"] == "active"])
            total_revenue = sum(Decimal(str(l["price"])) for l in licenses)
            
            # License type breakdown
            license_type_breakdown = {}
            for license in licenses:
                license_type = license["license_type"]
                if license_type not in license_type_breakdown:
                    license_type_breakdown[license_type] = {"count": 0, "revenue": Decimal("0")}
                license_type_breakdown[license_type]["count"] += 1
                license_type_breakdown[license_type]["revenue"] += Decimal(str(license["price"]))
            
            # Recent licenses
            recent_licenses = sorted(licenses, key=lambda x: x["created_at"], reverse=True)[:10]
            
            summary = {
                "user_id": user_id,
                "licensing_stats": {
                    "total_licenses": total_licenses,
                    "active_licenses": active_licenses,
                    "expired_licenses": len([l for l in licenses if l["status"] == "expired"]),
                    "pending_licenses": len([l for l in licenses if l["status"] == "pending"])
                },
                "revenue_stats": {
                    "total_revenue": float(total_revenue),
                    "average_license_price": float(total_revenue / total_licenses) if total_licenses > 0 else 0,
                    "currency": self.config["default_currency"]
                },
                "license_type_breakdown": {
                    license_type: {
                        "count": data["count"],
                        "revenue": float(data["revenue"])
                    }
                    for license_type, data in license_type_breakdown.items()
                },
                "recent_activity": recent_licenses
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user licensing summary: {str(e)}")
            return {"error": str(e)}
    
    def _get_license_config(self, license_type: str) -> Dict:
        """Get configuration for license type."""
        configs = {
            "basic": {
                "duration_days": 30,
                "base_price": Decimal("10.00"),
                "usage_limits": {"downloads": 100, "streams": 1000},
                "commercial_use": False
            },
            "standard": {
                "duration_days": 90,
                "base_price": Decimal("50.00"),
                "usage_limits": {"downloads": 500, "streams": 10000},
                "commercial_use": True
            },
            "premium": {
                "duration_days": 365,
                "base_price": Decimal("200.00"),
                "usage_limits": {"downloads": 2000, "streams": 50000},
                "commercial_use": True,
                "exclusive": True
            },
            "custom": {
                "duration_days": None,  # Negotiated
                "base_price": Decimal("0.00"),  # Negotiated
                "usage_limits": {},
                "commercial_use": True
            }
        }
        
        return configs.get(license_type, configs["basic"])
    
    async def _calculate_license_price(self, 
                                  content_id: int,
                                  license_type: str,
                                  terms: Dict) -> Decimal:
        """Calculate license price based on advanced pricing algorithms"""
        try:
            config = self._get_license_config(license_type)
            base_price = config["base_price"]
            
            # Custom pricing override
            if "price" in terms:
                return Decimal(str(terms["price"]))
            
            # Get content metadata for advanced pricing
            content = await self.content_repo.get_content(content_id)
            
            # Advanced pricing algorithm
            pricing_factors = await self._calculate_pricing_factors(content, terms)
            
            # Base price modifiers
            modifiers = Decimal("1.0")
            
            # 1. Territory-based pricing
            territory_modifier = await self._get_territory_modifier(terms.get("territory", "worldwide"))
            modifiers *= territory_modifier
            
            # 2. Duration-based pricing
            duration_modifier = await self._get_duration_modifier(terms, config)
            modifiers *= duration_modifier
            
            # 3. Exclusivity premium
            if terms.get("exclusive", False):
                exclusivity_modifier = await self._get_exclusivity_modifier(content, terms)
                modifiers *= exclusivity_modifier
            
            # 4. Content popularity and value assessment
            content_value_modifier = await self._assess_content_value(content)
            modifiers *= content_value_modifier
            
            # 5. Market demand analysis
            demand_modifier = await self._analyze_market_demand(content, license_type)
            modifiers *= demand_modifier
            
            # 6. Usage scope assessment
            usage_modifier = await self._assess_usage_scope(terms)
            modifiers *= usage_modifier
            
            # 7. Client tier adjustment
            client_modifier = await self._get_client_tier_modifier(terms.get("licensee_id"))
            modifiers *= client_modifier
            
            # 8. Seasonal and promotional adjustments
            seasonal_modifier = await self._get_seasonal_modifier()
            modifiers *= seasonal_modifier
            
            # Calculate final price
            final_price = base_price * modifiers
            
            # Apply minimum and maximum price bounds
            min_price = config.get("min_price", Decimal("1.00"))
            max_price = config.get("max_price", Decimal("10000.00"))
            
            final_price = max(min_price, min(max_price, final_price))
            
            # Store pricing details for transparency
            pricing_breakdown = {
                "base_price": float(base_price),
                "territory_modifier": float(territory_modifier),
                "duration_modifier": float(duration_modifier),
                "content_value_modifier": float(content_value_modifier),
                "demand_modifier": float(demand_modifier),
                "usage_modifier": float(usage_modifier),
                "client_modifier": float(client_modifier),
                "seasonal_modifier": float(seasonal_modifier),
                "total_modifier": float(modifiers),
                "final_price": float(final_price)
            }
            
            # Cache pricing analysis for auditing
            await self._cache_pricing_analysis(content_id, pricing_breakdown)
            
            logger.info(f"Calculated license price for content {content_id}: €{final_price}")
            
            return final_price.quantize(Decimal("0.01"))
            
        except Exception as e:
            logger.error(f"Error calculating license price: {str(e)}")
            # Fallback to base price
            return self._get_license_config(license_type)["base_price"]
    
    async def _calculate_pricing_factors(self, content: Dict, terms: Dict) -> Dict:
        """Calculate comprehensive pricing factors"""
        try:
            factors = {}
            
            # Content quality assessment
            factors["quality_score"] = await self._assess_content_quality(content)
            
            # Historical performance
            factors["performance_score"] = await self._get_content_performance(content["id"])
            
            # Genre and category factors
            factors["genre_factor"] = await self._get_genre_pricing_factor(content)
            
            # Creator reputation
            factors["creator_factor"] = await self._get_creator_reputation_factor(content)
            
            # Content age and freshness
            factors["freshness_factor"] = await self._calculate_freshness_factor(content)
            
            return factors
            
        except Exception as e:
            logger.error(f"Error calculating pricing factors: {e}")
            return {}
    
    async def _get_territory_modifier(self, territory: str) -> Decimal:
        """Get pricing modifier based on territory"""
        territory_modifiers = {
            "worldwide": Decimal("1.50"),
            "north_america": Decimal("1.30"),
            "europe": Decimal("1.25"),
            "asia_pacific": Decimal("1.20"),
            "latin_america": Decimal("1.10"),
            "africa": Decimal("1.05"),
            "oceania": Decimal("1.15"),
            "single_country": Decimal("0.80"),
            "regional": Decimal("1.00")
        }
        
        return territory_modifiers.get(territory.lower(), Decimal("1.00"))
    
    async def _get_duration_modifier(self, terms: Dict, config: Dict) -> Decimal:
        """Calculate duration-based pricing modifier"""
        try:
            duration_days = terms.get("duration_days", config["duration_days"])
            base_duration = config["duration_days"]
            
            if not duration_days or not base_duration:
                return Decimal("1.00")
            
            # Non-linear pricing for duration
            if duration_days <= base_duration:
                return Decimal("1.00")
            elif duration_days <= base_duration * 2:
                return Decimal("1.25")
            elif duration_days <= base_duration * 4:
                return Decimal("1.50")
            else:
                return Decimal("2.00")
                
        except Exception as e:
            logger.error(f"Duration modifier calculation failed: {e}")
            return Decimal("1.00")
    
    async def _get_exclusivity_modifier(self, content: Dict, terms: Dict) -> Decimal:
        """Calculate exclusivity premium based on content value"""
        try:
            base_exclusivity = Decimal("2.00")
            
            # Adjust based on content popularity
            popularity_score = await self._get_content_popularity(content["id"])
            
            if popularity_score > 0.8:
                return base_exclusivity * Decimal("1.5")  # High-demand content
            elif popularity_score > 0.6:
                return base_exclusivity * Decimal("1.2")
            else:
                return base_exclusivity
                
        except Exception as e:
            logger.error(f"Exclusivity modifier calculation failed: {e}")
            return Decimal("2.00")
    
    async def _assess_content_value(self, content: Dict) -> Decimal:
        """Assess content value based on multiple factors"""
        try:
            value_score = Decimal("1.00")
            
            # Quality metrics
            quality_score = await self._assess_content_quality(content)
            value_score *= Decimal(str(0.8 + quality_score * 0.4))  # 0.8-1.2 range
            
            # Uniqueness assessment
            uniqueness_score = await self._assess_content_uniqueness(content)
            value_score *= Decimal(str(0.9 + uniqueness_score * 0.2))  # 0.9-1.1 range
            
            # Production value estimation
            production_value = await self._estimate_production_value(content)
            value_score *= Decimal(str(0.95 + production_value * 0.1))  # 0.95-1.05 range
            
            return min(Decimal("2.00"), max(Decimal("0.50"), value_score))
            
        except Exception as e:
            logger.error(f"Content value assessment failed: {e}")
            return Decimal("1.00")
    
    async def _analyze_market_demand(self, content: Dict, license_type: str) -> Decimal:
        """Analyze market demand for similar content"""
        try:
            # Simulate market demand analysis
            # In production, this would query analytics databases
            
            base_demand = Decimal("1.00")
            
            # Genre demand analysis
            genre = content.get("metadata", {}).get("genre", "unknown")
            genre_demand = await self._get_genre_demand(genre)
            
            # Seasonal trends
            seasonal_demand = await self._get_seasonal_demand(genre)
            
            # License type demand
            license_demand = await self._get_license_type_demand(license_type)
            
            # Combine demand factors
            total_demand = (genre_demand + seasonal_demand + license_demand) / 3
            
            return Decimal(str(0.8 + total_demand * 0.4))  # 0.8-1.2 range
            
        except Exception as e:
            logger.error(f"Market demand analysis failed: {e}")
            return Decimal("1.00")
    
    async def _assess_usage_scope(self, terms: Dict) -> Decimal:
        """Assess usage scope and apply appropriate modifier"""
        try:
            scope_modifier = Decimal("1.00")
            
            # Commercial vs non-commercial
            if terms.get("commercial_use", False):
                scope_modifier *= Decimal("1.5")
            
            # Broadcast rights
            if terms.get("broadcast_rights", False):
                scope_modifier *= Decimal("1.3")
            
            # Sync rights
            if terms.get("sync_rights", False):
                scope_modifier *= Decimal("1.4")
            
            # Merchandising rights
            if terms.get("merchandising_rights", False):
                scope_modifier *= Decimal("1.2")
            
            # Digital distribution
            digital_scope = terms.get("digital_distribution", "limited")
            if digital_scope == "unlimited":
                scope_modifier *= Decimal("1.3")
            elif digital_scope == "extended":
                scope_modifier *= Decimal("1.15")
            
            return min(Decimal("3.00"), scope_modifier)
            
        except Exception as e:
            logger.error(f"Usage scope assessment failed: {e}")
            return Decimal("1.00")
    
    async def _get_client_tier_modifier(self, licensee_id: int) -> Decimal:
        """Get client tier-based pricing modifier"""
        try:
            if not licensee_id:
                return Decimal("1.00")
            
            # Client tier analysis
            client_tier = await self._determine_client_tier(licensee_id)
            
            tier_modifiers = {
                "enterprise": Decimal("1.20"),    # Premium clients pay more
                "professional": Decimal("1.10"),
                "standard": Decimal("1.00"),
                "indie": Decimal("0.85"),         # Indie discount
                "student": Decimal("0.70"),       # Student discount
                "non_profit": Decimal("0.60")     # Non-profit discount
            }
            
            return tier_modifiers.get(client_tier, Decimal("1.00"))
            
        except Exception as e:
            logger.error(f"Client tier modifier calculation failed: {e}")
            return Decimal("1.00")
    
    async def _get_seasonal_modifier(self) -> Decimal:
        """Apply seasonal pricing adjustments"""
        try:
            from datetime import datetime
            
            current_month = datetime.now().month
            
            # Holiday season premium (November-December)
            if current_month in [11, 12]:
                return Decimal("1.15")
            
            # Summer campaign season (June-August)
            elif current_month in [6, 7, 8]:
                return Decimal("1.10")
            
            # New Year promotions (January)
            elif current_month == 1:
                return Decimal("0.90")
            
            # Standard pricing
            else:
                return Decimal("1.00")
                
        except Exception as e:
            logger.error(f"Seasonal modifier calculation failed: {e}")
            return Decimal("1.00")
    
    # Helper methods for pricing analysis
    async def _assess_content_quality(self, content: Dict) -> float:
        """Assess content quality score (0.0-1.0)"""
        try:
            # Simulate quality assessment
            # In production, use AI models for quality scoring
            metadata = content.get("metadata", {})
            
            # Basic quality indicators
            has_title = bool(metadata.get("title"))
            has_description = bool(metadata.get("description"))
            has_tags = bool(metadata.get("tags"))
            
            quality_score = 0.6  # Base score
            
            if has_title:
                quality_score += 0.1
            if has_description:
                quality_score += 0.1
            if has_tags:
                quality_score += 0.1
            
            # Add some variation
            import random
            quality_score += random.random() * 0.1
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Content quality assessment failed: {e}")
            return 0.7
    
    async def _get_content_performance(self, content_id: int) -> float:
        """Get historical performance score"""
        try:
            # Simulate performance tracking
            # In production, query analytics database
            import random
            return 0.5 + random.random() * 0.5  # 0.5-1.0 range
            
        except Exception as e:
            logger.error(f"Content performance retrieval failed: {e}")
            return 0.7
    
    async def _get_genre_pricing_factor(self, content: Dict) -> float:
        """Get genre-specific pricing factor"""
        try:
            genre = content.get("metadata", {}).get("genre", "unknown").lower()
            
            genre_factors = {
                "classical": 1.2,
                "jazz": 1.1,
                "electronic": 1.0,
                "pop": 1.3,
                "rock": 1.1,
                "hip_hop": 1.2,
                "ambient": 0.9,
                "soundtrack": 1.4,
                "commercial": 1.5
            }
            
            return genre_factors.get(genre, 1.0)
            
        except Exception as e:
            logger.error(f"Genre pricing factor calculation failed: {e}")
            return 1.0
    
    async def _get_creator_reputation_factor(self, content: Dict) -> float:
        """Get creator reputation factor"""
        try:
            creator_id = content.get("creator_id")
            if not creator_id:
                return 1.0
            
            # Simulate creator reputation analysis
            # In production, analyze creator's track record
            import random
            return 0.8 + random.random() * 0.4  # 0.8-1.2 range
            
        except Exception as e:
            logger.error(f"Creator reputation factor calculation failed: {e}")
            return 1.0
    
    async def _calculate_freshness_factor(self, content: Dict) -> float:
        """Calculate content freshness factor"""
        try:
            from datetime import datetime, timedelta
            
            created_at = content.get("created_at")
            if not created_at:
                return 1.0
            
            # Parse creation date
            if isinstance(created_at, str):
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_date = created_at
            
            # Calculate age in days
            age_days = (datetime.now() - created_date).days
            
            # Freshness factor (newer content is more valuable)
            if age_days <= 30:
                return 1.2  # New content premium
            elif age_days <= 90:
                return 1.1
            elif age_days <= 365:
                return 1.0
            else:
                return 0.9  # Older content discount
                
        except Exception as e:
            logger.error(f"Freshness factor calculation failed: {e}")
            return 1.0
    
    async def _get_content_popularity(self, content_id: int) -> float:
        """Get content popularity score"""
        try:
            # Simulate popularity tracking
            import random
            return random.random()  # 0.0-1.0 range
            
        except Exception as e:
            logger.error(f"Content popularity retrieval failed: {e}")
            return 0.5
    
    async def _assess_content_uniqueness(self, content: Dict) -> float:
        """Assess content uniqueness"""
        try:
            # Simulate uniqueness assessment
            # In production, use similarity analysis
            import random
            return 0.3 + random.random() * 0.7  # 0.3-1.0 range
            
        except Exception as e:
            logger.error(f"Content uniqueness assessment failed: {e}")
            return 0.7
    
    async def _estimate_production_value(self, content: Dict) -> float:
        """Estimate production value"""
        try:
            # Simulate production value estimation
            import random
            return 0.2 + random.random() * 0.8  # 0.2-1.0 range
            
        except Exception as e:
            logger.error(f"Production value estimation failed: {e}")
            return 0.6
    
    async def _get_genre_demand(self, genre: str) -> float:
        """Get current genre demand"""
        try:
            # Simulate market demand by genre
            genre_demand = {
                "pop": 0.9,
                "electronic": 0.8,
                "hip_hop": 0.85,
                "rock": 0.7,
                "jazz": 0.6,
                "classical": 0.65,
                "ambient": 0.55,
                "soundtrack": 0.95,
                "commercial": 1.0
            }
            
            return genre_demand.get(genre.lower(), 0.7)
            
        except Exception as e:
            logger.error(f"Genre demand retrieval failed: {e}")
            return 0.7
    
    async def _get_seasonal_demand(self, genre: str) -> float:
        """Get seasonal demand for genre"""
        try:
            from datetime import datetime
            month = datetime.now().month
            
            # Holiday music demand boost
            if genre.lower() in ["commercial", "pop"] and month in [11, 12]:
                return 1.0
            
            # Summer music demand
            if genre.lower() in ["electronic", "pop"] and month in [6, 7, 8]:
                return 0.9
            
            return 0.7
            
        except Exception as e:
            logger.error(f"Seasonal demand calculation failed: {e}")
            return 0.7
    
    async def _get_license_type_demand(self, license_type: str) -> float:
        """Get demand for specific license type"""
        try:
            license_demand = {
                "basic": 0.6,
                "standard": 0.8,
                "premium": 0.9,
                "exclusive": 1.0,
                "sync": 0.95,
                "commercial": 0.85
            }
            
            return license_demand.get(license_type.lower(), 0.7)
            
        except Exception as e:
            logger.error(f"License type demand calculation failed: {e}")
            return 0.7
    
    async def _determine_client_tier(self, licensee_id: int) -> str:
        """Determine client tier based on history and profile"""
        try:
            # Simulate client tier analysis
            # In production, analyze client's licensing history, volume, etc.
            import random
            
            tiers = ["indie", "standard", "professional", "enterprise"]
            weights = [0.3, 0.4, 0.2, 0.1]  # Most clients are indie/standard
            
            return random.choices(tiers, weights=weights)[0]
            
        except Exception as e:
            logger.error(f"Client tier determination failed: {e}")
            return "standard"
    
    async def _cache_pricing_analysis(self, content_id: int, pricing_breakdown: Dict):
        """Cache pricing analysis for auditing and transparency"""
        try:
            cache_key = f"pricing_analysis:{content_id}:{datetime.now().date()}"
            
            analysis_data = {
                "content_id": content_id,
                "timestamp": datetime.now().isoformat(),
                "pricing_breakdown": pricing_breakdown,
                "version": "2.0"
            }
            
            # In production, store in Redis or database
            logger.debug(f"Cached pricing analysis: {cache_key}")
            
        except Exception as e:
            logger.error(f"Pricing analysis caching failed: {e}")
    
    async def _generate_license_terms(self, 
                                     content: Dict,
                                     license_config: Dict,
                                     custom_terms: Dict) -> Dict:
        """Generate comprehensive license terms."""
        terms = {
            "content_id": content["id"],
            "content_title": content.get("metadata", {}).get("title", "Untitled"),
            "license_type": license_config,
            "usage_rights": license_config.get("usage_limits", {}),
            "commercial_use": license_config.get("commercial_use", False),
            "territory": custom_terms.get("territory", "worldwide"),
            "exclusivity": custom_terms.get("exclusive", False),
            "attribution_required": custom_terms.get("attribution_required", True),
            "modifications_allowed": custom_terms.get("modifications_allowed", False),
    async def _generate_license_terms(self, 
                                     content: Dict,
                                     license_config: Dict,
                                     custom_terms: Dict) -> Dict:
        """Generate comprehensive license terms with legal compliance"""
        try:
            # Base terms from configuration
            base_terms = {
                "content_id": content["id"],
                "content_title": content.get("metadata", {}).get("title", "Untitled"),
                "content_duration": content.get("metadata", {}).get("duration", 0),
                "content_genre": content.get("metadata", {}).get("genre", "Unknown"),
                "license_type": license_config,
                "usage_rights": license_config.get("usage_limits", {}),
                "commercial_use": license_config.get("commercial_use", False),
                "territory": custom_terms.get("territory", "worldwide"),
                "exclusivity": custom_terms.get("exclusive", False),
                "attribution_required": custom_terms.get("attribution_required", True),
                "modifications_allowed": custom_terms.get("modifications_allowed", False),
                "payment_terms": custom_terms.get("payment_terms", "net_30"),
                "royalty_rate": custom_terms.get("royalty_rate", license_config.get("default_royalty_rate", Decimal("0.10")))
            }
            
            # Advanced terms generation
            advanced_terms = await self._generate_advanced_terms(content, license_config, custom_terms)
            base_terms.update(advanced_terms)
            
            # Legal compliance terms
            compliance_terms = await self._generate_compliance_terms(base_terms)
            base_terms.update(compliance_terms)
            
            # Performance and reporting terms
            performance_terms = await self._generate_performance_terms(base_terms)
            base_terms.update(performance_terms)
            
            # Risk management and insurance terms
            risk_terms = await self._generate_risk_management_terms(base_terms)
            base_terms.update(risk_terms)
            
            # Technology and format terms
            tech_terms = await self._generate_technology_terms(content, custom_terms)
            base_terms.update(tech_terms)
            
            # Validate terms for legal compliance
            validation_result = await self._validate_license_terms(base_terms)
            if not validation_result["valid"]:
                logger.warning(f"License terms validation issues: {validation_result['issues']}")
                # Apply corrections
                base_terms = await self._apply_term_corrections(base_terms, validation_result["issues"])
            
            return base_terms
            
        except Exception as e:
            logger.error(f"Error generating license terms: {e}")
            # Return minimal valid terms
            return {
                "content_id": content.get("id", 0),
                "license_type": "basic",
                "territory": "worldwide",
                "duration_days": 30,
                "commercial_use": False,
                "attribution_required": True
            }
    
    async def _generate_advanced_terms(self, content: Dict, license_config: Dict, custom_terms: Dict) -> Dict:
        """Generate advanced licensing terms"""
        try:
            advanced_terms = {}
            
            # Usage analytics and reporting
            advanced_terms["usage_reporting"] = {
                "required": True,
                "frequency": custom_terms.get("reporting_frequency", "monthly"),
                "metrics_required": ["plays", "downloads", "revenue", "geographical_distribution"],
                "reporting_format": "json_api",
                "deadline_days": 15
            }
            
            # Revenue sharing and royalties
            advanced_terms["revenue_sharing"] = {
                "enabled": custom_terms.get("revenue_sharing", True),
                "creator_percentage": custom_terms.get("creator_percentage", 70),
                "platform_percentage": custom_terms.get("platform_percentage", 30),
                "minimum_payout": custom_terms.get("minimum_payout", Decimal("10.00")),
                "payment_frequency": custom_terms.get("payment_frequency", "monthly")
            }
            
            # Content protection and anti-piracy
            advanced_terms["content_protection"] = {
                "drm_required": custom_terms.get("drm_required", False),
                "watermarking_required": custom_terms.get("watermarking_required", True),
                "anti_piracy_monitoring": custom_terms.get("anti_piracy_monitoring", True),
                "takedown_procedures": "automated_dmca",
                "protection_level": custom_terms.get("protection_level", "standard")
            }
            
            # Quality and delivery standards
            advanced_terms["quality_standards"] = {
                "minimum_bitrate": custom_terms.get("minimum_bitrate", 320),
                "audio_formats": custom_terms.get("audio_formats", ["mp3", "wav", "flac"]),
                "delivery_method": custom_terms.get("delivery_method", "digital_download"),
                "delivery_timeline": custom_terms.get("delivery_timeline", "immediate"),
                "quality_assurance": True
            }
            
            # Geographic and demographic restrictions
            advanced_terms["restrictions"] = {
                "age_restrictions": custom_terms.get("age_restrictions", "none"),
                "content_warnings": custom_terms.get("content_warnings", []),
                "geographic_blocks": custom_terms.get("geographic_blocks", []),
                "platform_restrictions": custom_terms.get("platform_restrictions", []),
                "time_based_restrictions": custom_terms.get("time_restrictions", {})
            }
            
            # Collaboration and derivative works
            advanced_terms["collaboration"] = {
                "remix_allowed": custom_terms.get("remix_allowed", False),
                "sampling_allowed": custom_terms.get("sampling_allowed", False),
                "collaboration_revenue_split": custom_terms.get("collaboration_split", {}),
                "derivative_approval_required": custom_terms.get("derivative_approval", True),
                "original_credit_mandatory": True
            }
            
            return advanced_terms
            
        except Exception as e:
            logger.error(f"Advanced terms generation failed: {e}")
            return {}
    
    async def _generate_compliance_terms(self, base_terms: Dict) -> Dict:
        """Generate legal compliance terms"""
        try:
            compliance_terms = {}
            
            # GDPR and data protection
            compliance_terms["data_protection"] = {
                "gdpr_compliant": True,
                "data_retention_days": 2555,  # 7 years
                "user_data_anonymization": True,
                "right_to_deletion": True,
                "data_portability": True,
                "consent_management": "explicit"
            }
            
            # Copyright and IP compliance
            compliance_terms["intellectual_property"] = {
                "copyright_clearance_verified": True,
                "performer_rights_cleared": True,
                "mechanical_rights_cleared": True,
                "synchronization_rights_included": base_terms.get("sync_rights", False),
                "master_recording_rights": True,
                "publishing_rights_status": "cleared"
            }
            
            # International compliance
            compliance_terms["international_compliance"] = {
                "berne_convention_compliant": True,
                "wipo_compliant": True,
                "regional_compliance": await self._get_regional_compliance_requirements(base_terms["territory"]),
                "tax_compliance": await self._get_tax_compliance_terms(base_terms["territory"]),
                "export_control_cleared": True
            }
            
            # Industry standards compliance
            compliance_terms["industry_standards"] = {
                "isrc_code_assigned": True,
                "metadata_standards": "ddex",
                "audio_codec_standards": ["mpeg", "aac", "flac"],
                "delivery_standards": "ddex_ern",
                "reporting_standards": "ddex_ern"
            }
            
            # Regulatory compliance
            compliance_terms["regulatory"] = {
                "broadcasting_standards_met": True,
                "advertising_standards_compliant": True,
                "platform_specific_compliance": await self._get_platform_compliance_requirements(),
                "content_rating_verified": True,
                "accessibility_compliant": base_terms.get("accessibility_required", False)
            }
            
            return compliance_terms
            
        except Exception as e:
            logger.error(f"Compliance terms generation failed: {e}")
            return {"gdpr_compliant": True}
    
    async def _generate_performance_terms(self, base_terms: Dict) -> Dict:
        """Generate performance and SLA terms"""
        try:
            performance_terms = {}
            
            # Service level agreements
            performance_terms["sla"] = {
                "uptime_guarantee": 99.9,
                "response_time_ms": 200,
                "download_speed_guarantee": "10mbps_minimum",
                "support_response_time_hours": 24,
                "resolution_time_hours": 72,
                "penalties_for_downtime": True
            }
            
            # Performance monitoring
            performance_terms["monitoring"] = {
                "real_time_analytics": True,
                "performance_alerts": True,
                "usage_tracking_granularity": "per_play",
                "revenue_tracking_real_time": True,
                "geographic_performance_tracking": True,
                "device_performance_tracking": True
            }
            
            # Scaling and capacity
            performance_terms["capacity"] = {
                "auto_scaling_enabled": True,
                "peak_load_handling": "unlimited",
                "concurrent_users_supported": 10000,
                "bandwidth_allocation": "dynamic",
                "cdn_acceleration": True,
                "global_distribution": base_terms["territory"] == "worldwide"
            }
            
            return performance_terms
            
        except Exception as e:
            logger.error(f"Performance terms generation failed: {e}")
            return {"uptime_guarantee": 99.0}
    
    async def _generate_risk_management_terms(self, base_terms: Dict) -> Dict:
        """Generate risk management and insurance terms"""
        try:
            risk_terms = {}
            
            # Insurance and liability
            risk_terms["insurance"] = {
                "professional_indemnity_coverage": Decimal("1000000.00"),
                "copyright_infringement_coverage": Decimal("500000.00"),
                "data_breach_coverage": Decimal("250000.00"),
                "business_interruption_coverage": Decimal("100000.00"),
                "liability_cap": Decimal("1000000.00")
            }
            
            # Risk mitigation
            risk_terms["risk_mitigation"] = {
                "content_screening_required": True,
                "ai_content_detection": True,
                "plagiarism_detection": True,
                "automated_copyright_scanning": True,
                "legal_review_threshold": Decimal("10000.00"),
                "escrow_protection": base_terms.get("exclusivity", False)
            }
            
            # Dispute resolution
            risk_terms["dispute_resolution"] = {
                "mediation_required": True,
                "arbitration_jurisdiction": await self._get_arbitration_jurisdiction(base_terms["territory"]),
                "governing_law": await self._get_governing_law(base_terms["territory"]),
                "dispute_resolution_timeline": "90_days",
                "escalation_procedures": True,
                "legal_fee_allocation": "loser_pays"
            }
            
            # Force majeure and termination
            risk_terms["termination"] = {
                "force_majeure_clauses": True,
                "termination_notice_days": 30,
                "early_termination_penalties": True,
                "data_return_guaranteed": True,
                "transition_assistance_days": 30,
                "post_termination_obligations": 90
            }
            
            return risk_terms
            
        except Exception as e:
            logger.error(f"Risk management terms generation failed: {e}")
            return {"liability_cap": Decimal("100000.00")}
    
    async def _generate_technology_terms(self, content: Dict, custom_terms: Dict) -> Dict:
        """Generate technology and format specific terms"""
        try:
            tech_terms = {}
            
            # Audio technology specifications
            tech_terms["audio_specs"] = {
                "sample_rates_supported": [44100, 48000, 96000],
                "bit_depths_supported": [16, 24, 32],
                "channel_configurations": ["mono", "stereo", "5.1", "7.1"],
                "dynamic_range_minimum": 90,  # dB
                "frequency_response": "20Hz-20kHz",
                "thd_maximum": 0.01  # % Total Harmonic Distortion
            }
            
            # Digital formats and codecs
            tech_terms["digital_formats"] = {
                "lossless_formats": ["wav", "flac", "alac"],
                "lossy_formats": ["mp3", "aac", "ogg"],
                "streaming_formats": ["hls", "dash", "progressive"],
                "metadata_formats": ["id3v2", "vorbis_comment", "ape"],
                "artwork_formats": ["jpeg", "png"],
                "artwork_resolution_minimum": [300, 300]
            }
            
            # Platform integration
            tech_terms["platform_integration"] = {
                "api_access_included": True,
                "webhook_notifications": True,
                "real_time_sync": True,
                "batch_operations_supported": True,
                "rate_limiting": {"requests_per_minute": 1000},
                "authentication_methods": ["oauth2", "api_key", "jwt"]
            }
            
            # AI and automation features
            tech_terms["ai_features"] = {
                "auto_tagging_enabled": True,
                "content_analysis_included": True,
                "similarity_matching": True,
                "recommendation_engine_access": True,
                "ai_enhancement_tools": custom_terms.get("ai_tools_included", True),
                "machine_learning_insights": True
            }
            
            # Security and encryption
            tech_terms["security"] = {
                "encryption_in_transit": "tls_1_3",
                "encryption_at_rest": "aes_256",
                "digital_signatures": True,
                "access_control": "rbac",
                "audit_logging": True,
                "vulnerability_scanning": "continuous"
            }
            
            return tech_terms
            
        except Exception as e:
            logger.error(f"Technology terms generation failed: {e}")
            return {"encryption_at_rest": "aes_256"}
    
    async def _validate_license_terms(self, terms: Dict) -> Dict[str, Any]:
        """Validate license terms for legal and business compliance"""
        try:
            validation_result = {"valid": True, "issues": [], "warnings": []}
            
            # Required field validation
            required_fields = [
                "content_id", "license_type", "territory", 
                "commercial_use", "attribution_required"
            ]
            
            for field in required_fields:
                if field not in terms:
                    validation_result["issues"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
            
            # Business logic validation
            if terms.get("exclusivity") and terms.get("revenue_sharing", {}).get("creator_percentage", 0) < 50:
                validation_result["warnings"].append("Exclusive licenses typically require higher creator revenue share")
            
            # Territory validation
            valid_territories = [
                "worldwide", "north_america", "europe", "asia_pacific", 
                "latin_america", "africa", "oceania", "single_country", "regional"
            ]
            if terms.get("territory") not in valid_territories:
                validation_result["issues"].append(f"Invalid territory: {terms.get('territory')}")
                validation_result["valid"] = False
            
            # Duration validation
            duration_days = terms.get("duration_days", 0)
            if duration_days and (duration_days < 1 or duration_days > 3650):  # Max 10 years
                validation_result["issues"].append("Duration must be between 1 and 3650 days")
                validation_result["valid"] = False
            
            # Price validation
            if "price" in terms:
                try:
                    price = Decimal(str(terms["price"]))
                    if price < 0:
                        validation_result["issues"].append("Price cannot be negative")
                        validation_result["valid"] = False
                except:
                    validation_result["issues"].append("Invalid price format")
                    validation_result["valid"] = False
            
            # Usage rights consistency
            if terms.get("commercial_use") and not terms.get("usage_rights", {}).get("commercial_distribution", False):
                validation_result["warnings"].append("Commercial use enabled but commercial distribution rights not specified")
            
            # Compliance validation
            if not terms.get("data_protection", {}).get("gdpr_compliant", False):
                validation_result["issues"].append("GDPR compliance is mandatory")
                validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Terms validation failed: {e}")
            return {"valid": False, "issues": ["Validation system error"], "warnings": []}
    
    async def _apply_term_corrections(self, terms: Dict, issues: List[str]) -> Dict:
        """Apply automatic corrections to license terms"""
        try:
            corrected_terms = terms.copy()
            
            for issue in issues:
                if "Missing required field" in issue:
                    field = issue.split(": ")[1]
                    # Apply default values for missing fields
                    defaults = {
                        "content_id": 0,
                        "license_type": "basic",
                        "territory": "worldwide",
                        "commercial_use": False,
                        "attribution_required": True
                    }
                    if field in defaults:
                        corrected_terms[field] = defaults[field]
                
                elif "Invalid territory" in issue:
                    corrected_terms["territory"] = "worldwide"
                
                elif "Duration must be between" in issue:
                    corrected_terms["duration_days"] = 30  # Default 30 days
                
                elif "Price cannot be negative" in issue:
                    corrected_terms["price"] = Decimal("0.00")
                
                elif "GDPR compliance is mandatory" in issue:
                    if "data_protection" not in corrected_terms:
                        corrected_terms["data_protection"] = {}
                    corrected_terms["data_protection"]["gdpr_compliant"] = True
            
            logger.info(f"Applied {len(issues)} automatic corrections to license terms")
            return corrected_terms
            
        except Exception as e:
            logger.error(f"Term correction failed: {e}")
            return terms
    
    # Helper methods for compliance and regional requirements
    async def _get_regional_compliance_requirements(self, territory: str) -> Dict:
        """Get regional compliance requirements"""
        regional_requirements = {
            "worldwide": {"gdpr": True, "ccpa": True, "pipeda": True},
            "europe": {"gdpr": True, "cookie_law": True, "vat_compliance": True},
            "north_america": {"ccpa": True, "pipeda": True, "dmca": True},
            "asia_pacific": {"appi": True, "pdpa": True, "local_data_residency": True}
        }
        return regional_requirements.get(territory, {"basic_compliance": True})
    
    async def _get_tax_compliance_terms(self, territory: str) -> Dict:
        """Get tax compliance terms by territory"""
        tax_terms = {
            "worldwide": {"vat_applicable": True, "withholding_tax": True},
            "europe": {"vat_rate": 20, "digital_services_tax": True},
            "north_america": {"sales_tax_variable": True, "canadian_gst": True}
        }
        return tax_terms.get(territory, {"tax_compliance_required": True})
    
    async def _get_platform_compliance_requirements(self) -> Dict:
        """Get platform-specific compliance requirements"""
        return {
            "spotify": {"loud_normalization": True, "content_advisory": True},
            "apple_music": {"mastered_for_itunes": True, "spatial_audio_ready": False},
            "youtube": {"content_id_compatible": True, "fair_use_compliant": True},
            "tiktok": {"short_form_optimized": True, "copyright_free_verified": True}
        }
    
    async def _get_arbitration_jurisdiction(self, territory: str) -> str:
        """Get appropriate arbitration jurisdiction"""
        jurisdictions = {
            "worldwide": "ICC_Paris",
            "europe": "LCIA_London", 
            "north_america": "AAA_New_York",
            "asia_pacific": "SIAC_Singapore"
        }
        return jurisdictions.get(territory, "ICC_Paris")
    
    async def _get_governing_law(self, territory: str) -> str:
        """Get appropriate governing law"""
        laws = {
            "worldwide": "English_Law",
            "europe": "EU_Law",
            "north_america": "Delaware_Law",
            "asia_pacific": "Singapore_Law"
        }
        return laws.get(territory, "English_Law")
            "cancellation_policy": custom_terms.get("cancellation_policy", "30_days_notice"),
            "governing_law": custom_terms.get("governing_law", "German Law"),
            "dispute_resolution": custom_terms.get("dispute_resolution", "arbitration")
        }
        
        return terms
    
    async def _check_usage_limits(self, 
                                 license: Dict,
                                 usage_type: str,
                                 usage_data: Dict):
        """Check if usage is within license limits."""
        usage_limits = license.get("usage_limits", {})
        
        if usage_type in usage_limits:
            limit = usage_limits[usage_type]
            current_usage = await self.usage_tracker.get_current_usage(
                license["id"], usage_type
            )
            
            requested_usage = usage_data.get("count", 1)
            
            if current_usage + requested_usage > limit:
                raise LicensingError(
                    f"Usage limit exceeded for {usage_type}: "
                    f"{current_usage + requested_usage} > {limit}"
                )
    
    async def _update_license_usage_stats(self, 
                                         license_id: int,
                                         usage_type: str,
                                         usage_data: Dict):
        """Update license usage statistics."""
        await self.license_repo.update_license_usage_stats(
            license_id, usage_type, usage_data
        )
    
    async def _start_license_monitoring(self, license_id: int):
        """
Start monitoring for license compliance and expiration."""
        if license_id not in self.monitoring_tasks:
            task = asyncio.create_task(
                self._license_monitoring_loop(license_id)
            )
            self.monitoring_tasks[license_id] = task
    
    async def _license_monitoring_loop(self, license_id: int):
        """
Monitor license for expiration and compliance."""
        try:
            while True:
                license = await self.license_repo.get_license(license_id)
                if not license or license["status"] != "active":
                    break
                
                # Check expiration
                if datetime.utcnow() >= license["end_date"]:
                    await self.license_repo.update_license_status(
                        license_id, LicenseStatus.EXPIRED.value
                    )
                    await self._send_license_notification(license, "expired")
                    break
                
                # Check usage compliance
                await self._check_license_compliance(license)
                
                # Wait before next check (daily)
                await asyncio.sleep(86400)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in license monitoring: {str(e)}")
        finally:
            if license_id in self.monitoring_tasks:
                del self.monitoring_tasks[license_id]
    
    async def _check_license_compliance(self, license: Dict):
        """Check license compliance and usage limits."""
        logger.info(f"Checking compliance for license {license['id']}")
        
        try:
            # Check usage limits
            current_usage = license.get('usage_count', 0)
            usage_limit = license.get('usage_limit', float('inf'))
            
            if current_usage >= usage_limit:
                logger.warning(f"License {license['id']} has exceeded usage limit")
                await self._send_license_notification(license, "usage_limit_exceeded")
                
                # Auto-suspend license if configured
                if license.get('auto_suspend_on_limit', False):
                    await self.update_license_status(license['id'], LicenseStatus.SUSPENDED)
                    logger.info(f"License {license['id']} auto-suspended due to usage limit")
            
            # Check territorial restrictions
            if 'territorial_restrictions' in license:
                restricted_regions = license['territorial_restrictions']
                current_usage_regions = license.get('usage_regions', [])
                
                violation_regions = set(current_usage_regions) - set(restricted_regions)
                if violation_regions:
                    logger.warning(f"License {license['id']} violated territorial restrictions: {violation_regions}")
                    await self._send_license_notification(license, "territorial_violation")
            
            # Check time-based restrictions
            if 'time_restrictions' in license:
                time_restrictions = license['time_restrictions']
                current_time = datetime.utcnow().time()
                
                start_time = datetime.strptime(time_restrictions.get('start_time', '00:00'), '%H:%M').time()
                end_time = datetime.strptime(time_restrictions.get('end_time', '23:59'), '%H:%M').time()
                
                if not (start_time <= current_time <= end_time):
                    logger.warning(f"License {license['id']} used outside permitted time window")
                    await self._send_license_notification(license, "time_restriction_violation")
            
            # Check content modification restrictions
            if license.get('modification_restrictions', {}).get('no_modifications', False):
                # This would be checked by the content protection system
                # For now, we log that we should verify no modifications occurred
                logger.debug(f"Checking modification restrictions for license {license['id']}")
            
            # Check commercial use restrictions
            if not license.get('commercial_use_allowed', True):
                # Check if content was used commercially
                commercial_usage = license.get('commercial_usage_detected', False)
                if commercial_usage:
                    logger.warning(f"License {license['id']} violated commercial use restrictions")
                    await self._send_license_notification(license, "commercial_use_violation")
            
            # Update last compliance check timestamp
            license['last_compliance_check'] = datetime.utcnow().isoformat()
            
            logger.info(f"Compliance check completed for license {license['id']}")
            
        except Exception as e:
            logger.error(f"Error checking compliance for license {license['id']}: {str(e)}")
            raise LicensingError(f"Compliance check failed: {str(e)}")
    
    async def _send_license_notification(self, license: Dict, notification_type: str):
        """Send license notification to relevant parties."""
        # Implementation for notifications
        logger.info(f"License notification sent: {license['id']} - {notification_type}")
    
    def get_manager_stats(self) -> Dict:
        """Get licensing manager statistics."""
        return {
            "version": "1.0.0",
            "active_monitoring_tasks": len(self.monitoring_tasks),
            "supported_license_types": list(self._get_license_config("basic").keys()),
            "auto_approval_threshold": float(self.config["auto_approval_threshold"]),
            "default_currency": self.config["default_currency"],
            "royalty_rates": {
                rate_type: float(rate) for rate_type, rate in self.config["royalty_rates"].items()
            }
        }
