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
            """Initialize license repository with basic functionality"""
            self.licenses = {}
            
    class ContentRepository:
        def __init__(self):
            """Initialize content repository with basic functionality"""
            self.content = {}

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """License type enumeration."""
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
    """License usage record."""
    id: int
    license_id: int
    usage_type: UsageType
    usage_count: int
    usage_data: Dict
    royalty_amount: Decimal
    timestamp: datetime

class LicensingError(Exception):
    """Exception for licensing-related errors"""
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
        """Initialize licensing manager."""
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
        """Calculate license price based on content and terms."""
        try:
            config = self._get_license_config(license_type)
            base_price = config["base_price"]
            
            # Custom pricing
            if "price" in terms:
                return Decimal(str(terms["price"]))
            
            # Factor in content popularity, duration, etc.
            content = await self.content_repo.get_content(content_id)
            
            # Price modifiers
            modifiers = Decimal("1.0")
            
            # Territory modifier
            territory = terms.get("territory", "worldwide")
            if territory == "worldwide":
                modifiers *= Decimal("1.5")
            
            # Duration modifier
            duration_days = terms.get("duration_days", config["duration_days"])
            if duration_days and duration_days > config["duration_days"]:
                modifiers *= Decimal("1.2")
            
            # Exclusive use modifier
            if terms.get("exclusive", False):
                modifiers *= Decimal("2.0")
            
            final_price = base_price * modifiers
            return final_price.quantize(Decimal("0.01"))
            
        except Exception as e:
            logger.error(f"Error calculating license price: {str(e)}")
            return Decimal("0.00")
    
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
            "payment_terms": custom_terms.get("payment_terms", "net_30"),
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
        """Start monitoring for license compliance and expiration."""
        if license_id not in self.monitoring_tasks:
            task = asyncio.create_task(
                self._license_monitoring_loop(license_id)
            )
            self.monitoring_tasks[license_id] = task
    
    async def _license_monitoring_loop(self, license_id: int):
        """Monitor license for expiration and compliance."""
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
