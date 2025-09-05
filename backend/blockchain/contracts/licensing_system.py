"""Licensing System Contract - IA-Influencer-Agent Platform

This module provides automated licensing system functionality for content creators,
enabling them to define, manage, and enforce usage rights for their copyrighted
content through smart contracts and automated enforcement.

Features:
- Automated license creation and management
- Usage rights enforcement
- License fee collection and distribution
- Multi-tier licensing (personal, commercial, enterprise)
- Geographic territory restrictions
- Time-based licensing
- Revenue sharing for licensed content
- License compliance monitoring

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid
import hashlib
import time

from web3 import Web3
from web3.contract import Contract

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Types of content licenses"""
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    ENTERPRISE = "enterprise"
    EDUCATIONAL = "educational"
    NON_PROFIT = "non_profit"
    ROYALTY_FREE = "royalty_free"
    EXCLUSIVE = "exclusive"
    CREATIVE_COMMONS = "creative_commons"


class LicenseStatus(Enum):
    """License status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    TRANSFERRED = "transferred"


class UsageType(Enum):
    """Types of content usage"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    REMIX = "remix"
    COMMERCIAL_USE = "commercial_use"
    BROADCAST = "broadcast"
    PRINT = "print"
    DIGITAL_DISTRIBUTION = "digital_distribution"
    SYNCHRONIZATION = "synchronization"


@dataclass
class LicenseTerms:
    """License terms and conditions"""
    license_type: LicenseType
    usage_types: List[UsageType]
    max_uses: Optional[int]
    territory: List[str]
    duration_days: Optional[int]
    price: Decimal
    currency: str
    revenue_share_percentage: Optional[Decimal]
    attribution_required: bool
    commercial_use_allowed: bool
    derivative_works_allowed: bool
    sublicensing_allowed: bool
    restrictions: List[str]
    additional_terms: Dict[str, Any]


@dataclass
class License:
    """License record structure"""
    license_id: str
    content_id: str
    copyright_id: str
    licensor_address: str
    licensee_address: str
    terms: LicenseTerms
    status: LicenseStatus
    created_at: datetime
    activated_at: Optional[datetime]
    expires_at: Optional[datetime]
    transaction_hash: str
    block_number: int
    usage_count: int
    revenue_generated: Decimal
    last_used_at: Optional[datetime]


@dataclass
class LicenseUsage:
    """License usage record"""
    usage_id: str
    license_id: str
    user_address: str
    usage_type: UsageType
    usage_timestamp: datetime
    location: Optional[str]
    device_info: Optional[Dict[str, Any]]
    revenue_generated: Decimal
    transaction_hash: str


class LicensingSystem:
    """
    Automated Licensing System for content creators
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Licensing System
        
        Args:
            config: Configuration including contract settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_licenses: Dict[str, License] = {}
        self.license_usage_history: List[LicenseUsage] = []
        self.license_templates: Dict[str, LicenseTerms] = {}
        
        # Contract configuration
        self.contract_address = config.get("contract_address")
        self.network = config.get("network", "ethereum")
        self.gas_limit = config.get("gas_limit", 300000)
        
        # Platform settings
        self.platform_fee_percentage = Decimal(config.get("platform_fee", "2.5"))
        self.min_license_duration = config.get("min_license_duration", 30)  # days
        
        # Initialize default license templates
        self._init_license_templates()
    
    def _init_license_templates(self):
        """Initialize default license templates"""
        self.license_templates = {
            "basic_personal": LicenseTerms(
                license_type=LicenseType.PERSONAL,
                usage_types=[UsageType.STREAMING, UsageType.DOWNLOAD],
                max_uses=100,
                territory=["worldwide"],
                duration_days=365,
                price=Decimal("9.99"),
                currency="USD",
                revenue_share_percentage=None,
                attribution_required=True,
                commercial_use_allowed=False,
                derivative_works_allowed=False,
                sublicensing_allowed=False,
                restrictions=["no_commercial_use", "attribution_required"],
                additional_terms={}
            ),
            "commercial_standard": LicenseTerms(
                license_type=LicenseType.COMMERCIAL,
                usage_types=[UsageType.COMMERCIAL_USE, UsageType.BROADCAST, UsageType.DIGITAL_DISTRIBUTION],
                max_uses=None,
                territory=["worldwide"],
                duration_days=365,
                price=Decimal("99.99"),
                currency="USD",
                revenue_share_percentage=Decimal("10.0"),
                attribution_required=True,
                commercial_use_allowed=True,
                derivative_works_allowed=True,
                sublicensing_allowed=False,
                restrictions=["attribution_required"],
                additional_terms={"reporting_required": True}
            ),
            "enterprise_unlimited": LicenseTerms(
                license_type=LicenseType.ENTERPRISE,
                usage_types=list(UsageType),
                max_uses=None,
                territory=["worldwide"],
                duration_days=None,  # Perpetual
                price=Decimal("999.99"),
                currency="USD",
                revenue_share_percentage=Decimal("5.0"),
                attribution_required=False,
                commercial_use_allowed=True,
                derivative_works_allowed=True,
                sublicensing_allowed=True,
                restrictions=[],
                additional_terms={"priority_support": True, "custom_integration": True}
            )
        }
    
    async def create_license(
        self,
        content_id: str,
        copyright_id: str,
        licensor_address: str,
        licensee_address: str,
        license_template: str,
        custom_terms: Optional[Dict[str, Any]] = None
    ) -> License:
        """
        Create a new content license
        
        Args:
            content_id: ID of content being licensed
            copyright_id: Copyright registration ID
            licensor_address: Address of license creator
            licensee_address: Address of licensee
            license_template: Template name for license terms
            custom_terms: Optional custom modifications to template
            
        Returns:
            Created license record
        """
        try:
            license_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating license: {license_template} for content {content_id}")
            
            # Get license terms from template
            if license_template not in self.license_templates:
                raise ValueError(f"License template not found: {license_template}")
            
            terms = self._customize_license_terms(
                self.license_templates[license_template], custom_terms or {}
            )
            
            # Validate license terms
            await self._validate_license_terms(terms, licensor_address)
            
            # Calculate expiry date
            expires_at = None
            if terms.duration_days:
                expires_at = datetime.utcnow() + timedelta(days=terms.duration_days)
            
            # Create license on blockchain
            tx_result = await self._create_license_on_blockchain(
                license_id, content_id, copyright_id, licensor_address, 
                licensee_address, terms
            )
            
            # Create license record
            license_record = License(
                license_id=license_id,
                content_id=content_id,
                copyright_id=copyright_id,
                licensor_address=licensor_address,
                licensee_address=licensee_address,
                terms=terms,
                status=LicenseStatus.PENDING,
                created_at=datetime.utcnow(),
                activated_at=None,
                expires_at=expires_at,
                transaction_hash=tx_result["tx_hash"],
                block_number=tx_result["block_number"],
                usage_count=0,
                revenue_generated=Decimal("0"),
                last_used_at=None
            )
            
            # Store license
            self.active_licenses[license_id] = license_record
            
            self.logger.info(f"License created: {license_id}")
            return license_record
            
        except Exception as e:
            self.logger.error(f"License creation failed: {e}")
            raise
    
    def _customize_license_terms(
        self, 
        template_terms: LicenseTerms, 
        custom_terms: Dict[str, Any]
    ) -> LicenseTerms:
        """Customize license terms based on template and custom modifications"""
        
        # Create a copy of template terms
        terms_dict = {
            "license_type": template_terms.license_type,
            "usage_types": template_terms.usage_types.copy(),
            "max_uses": template_terms.max_uses,
            "territory": template_terms.territory.copy(),
            "duration_days": template_terms.duration_days,
            "price": template_terms.price,
            "currency": template_terms.currency,
            "revenue_share_percentage": template_terms.revenue_share_percentage,
            "attribution_required": template_terms.attribution_required,
            "commercial_use_allowed": template_terms.commercial_use_allowed,
            "derivative_works_allowed": template_terms.derivative_works_allowed,
            "sublicensing_allowed": template_terms.sublicensing_allowed,
            "restrictions": template_terms.restrictions.copy(),
            "additional_terms": template_terms.additional_terms.copy()
        }
        
        # Apply custom modifications
        for key, value in custom_terms.items():
            if key in terms_dict:
                if key == "usage_types" and isinstance(value, list):
                    terms_dict[key] = [UsageType(t) if isinstance(t, str) else t for t in value]
                elif key == "price" and isinstance(value, (int, float, str)):
                    terms_dict[key] = Decimal(str(value))
                elif key == "revenue_share_percentage" and value is not None:
                    terms_dict[key] = Decimal(str(value))
                else:
                    terms_dict[key] = value
        
        return LicenseTerms(**terms_dict)
    
    async def _validate_license_terms(self, terms: LicenseTerms, licensor_address: str):
        """Validate license terms"""
        if terms.price < 0:
            raise ValueError("License price cannot be negative")
        
        if terms.revenue_share_percentage and (terms.revenue_share_percentage < 0 or terms.revenue_share_percentage > 100):
            raise ValueError("Revenue share percentage must be between 0 and 100")
        
        if terms.duration_days and terms.duration_days < self.min_license_duration:
            raise ValueError(f"License duration must be at least {self.min_license_duration} days")
        
        if not terms.territory:
            raise ValueError("License territory cannot be empty")
        
        if not terms.usage_types:
            raise ValueError("License must specify at least one usage type")
    
    async def _create_license_on_blockchain(
        self,
        license_id: str,
        content_id: str,
        copyright_id: str,
        licensor_address: str,
        licensee_address: str,
        terms: LicenseTerms
    ) -> Dict[str, Any]:
        """Create license record on blockchain"""
        license_data = {
            "license_id": license_id,
            "content_id": content_id,
            "copyright_id": copyright_id,
            "licensor_address": licensor_address,
            "licensee_address": licensee_address,
            "license_type": terms.license_type.value,
            "price": str(terms.price),
            "currency": terms.currency,
            "duration_days": terms.duration_days,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(license_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345681,
            "gas_used": 200000
        }
    
    async def activate_license(
        self,
        license_id: str,
        payment_tx_hash: str,
        activator_address: str
    ) -> Dict[str, Any]:
        """
        Activate a license after payment confirmation
        
        Args:
            license_id: License ID to activate
            payment_tx_hash: Transaction hash of payment
            activator_address: Address activating the license
            
        Returns:
            Activation result
        """
        try:
            if license_id not in self.active_licenses:
                raise ValueError(f"License not found: {license_id}")
            
            license_record = self.active_licenses[license_id]
            
            if license_record.status != LicenseStatus.PENDING:
                raise ValueError(f"License cannot be activated in status: {license_record.status.value}")
            
            self.logger.info(f"Activating license: {license_id}")
            
            # Verify payment (mock implementation)
            payment_verified = await self._verify_license_payment(
                payment_tx_hash, license_record.terms.price
            )
            
            if not payment_verified:
                raise ValueError("License payment verification failed")
            
            # Activate license on blockchain
            activation_tx = await self._activate_license_on_blockchain(
                license_id, payment_tx_hash
            )
            
            # Update license record
            license_record.status = LicenseStatus.ACTIVE
            license_record.activated_at = datetime.utcnow()
            
            # Distribute revenue
            revenue_distribution = await self._distribute_license_revenue(
                license_record, payment_tx_hash
            )
            
            result = {
                "license_id": license_id,
                "status": "activated",
                "payment_tx": payment_tx_hash,
                "activation_tx": activation_tx["tx_hash"],
                "activated_at": license_record.activated_at.isoformat(),
                "expires_at": license_record.expires_at.isoformat() if license_record.expires_at else None,
                "revenue_distribution": revenue_distribution
            }
            
            self.logger.info(f"License activated: {license_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"License activation failed: {e}")
            raise
    
    async def _verify_license_payment(self, payment_tx_hash: str, expected_amount: Decimal) -> bool:
        """Verify license payment transaction"""
        # Mock payment verification
        return bool(payment_tx_hash and expected_amount > 0)
    
    async def _activate_license_on_blockchain(
        self,
        license_id: str,
        payment_tx_hash: str
    ) -> Dict[str, Any]:
        """Record license activation on blockchain"""
        activation_data = {
            "license_id": license_id,
            "payment_tx": payment_tx_hash,
            "activated_at": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(activation_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345682,
            "gas_used": 100000
        }
    
    async def _distribute_license_revenue(
        self,
        license_record: License,
        payment_tx_hash: str
    ) -> Dict[str, Any]:
        """Distribute license revenue among stakeholders"""
        total_amount = license_record.terms.price
        platform_fee = total_amount * (self.platform_fee_percentage / 100)
        licensor_amount = total_amount - platform_fee
        
        distribution = {
            "total_amount": str(total_amount),
            "platform_fee": str(platform_fee),
            "platform_fee_percentage": str(self.platform_fee_percentage),
            "licensor_amount": str(licensor_amount),
            "currency": license_record.terms.currency,
            "distribution_tx": f"0x{hashlib.sha256(payment_tx_hash.encode()).hexdigest()}",
            "distributed_at": datetime.utcnow().isoformat()
        }
        
        return distribution
    
    async def record_license_usage(
        self,
        license_id: str,
        user_address: str,
        usage_type: UsageType,
        location: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        revenue_amount: Decimal = Decimal("0")
    ) -> LicenseUsage:
        """
        Record license usage for tracking and compliance
        
        Args:
            license_id: License being used
            user_address: Address of user
            usage_type: Type of usage
            location: Optional location information
            device_info: Optional device information
            revenue_amount: Revenue generated from this usage
            
        Returns:
            Usage record
        """
        try:
            if license_id not in self.active_licenses:
                raise ValueError(f"License not found: {license_id}")
            
            license_record = self.active_licenses[license_id]
            
            if license_record.status != LicenseStatus.ACTIVE:
                raise ValueError(f"License not active: {license_record.status.value}")
            
            # Check if license has expired
            if license_record.expires_at and datetime.utcnow() > license_record.expires_at:
                license_record.status = LicenseStatus.EXPIRED
                raise ValueError("License has expired")
            
            # Check usage limits
            if license_record.terms.max_uses and license_record.usage_count >= license_record.terms.max_uses:
                raise ValueError("License usage limit exceeded")
            
            # Check if usage type is allowed
            if usage_type not in license_record.terms.usage_types:
                raise ValueError(f"Usage type not allowed: {usage_type.value}")
            
            usage_id = str(uuid.uuid4())
            
            # Record usage on blockchain
            usage_tx = await self._record_usage_on_blockchain(
                usage_id, license_id, user_address, usage_type, revenue_amount
            )
            
            # Create usage record
            usage_record = LicenseUsage(
                usage_id=usage_id,
                license_id=license_id,
                user_address=user_address,
                usage_type=usage_type,
                usage_timestamp=datetime.utcnow(),
                location=location,
                device_info=device_info,
                revenue_generated=revenue_amount,
                transaction_hash=usage_tx["tx_hash"]
            )
            
            # Update license record
            license_record.usage_count += 1
            license_record.revenue_generated += revenue_amount
            license_record.last_used_at = datetime.utcnow()
            
            # Store usage record
            self.license_usage_history.append(usage_record)
            
            self.logger.info(f"License usage recorded: {usage_id}")
            return usage_record
            
        except Exception as e:
            self.logger.error(f"License usage recording failed: {e}")
            raise
    
    async def _record_usage_on_blockchain(
        self,
        usage_id: str,
        license_id: str,
        user_address: str,
        usage_type: UsageType,
        revenue_amount: Decimal
    ) -> Dict[str, Any]:
        """Record license usage on blockchain"""
        usage_data = {
            "usage_id": usage_id,
            "license_id": license_id,
            "user_address": user_address,
            "usage_type": usage_type.value,
            "revenue_amount": str(revenue_amount),
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(usage_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345683,
            "gas_used": 75000
        }
    
    async def revoke_license(
        self,
        license_id: str,
        revoker_address: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Revoke an active license
        
        Args:
            license_id: License ID to revoke
            revoker_address: Address requesting revocation
            reason: Reason for revocation
            
        Returns:
            Revocation result
        """
        try:
            if license_id not in self.active_licenses:
                raise ValueError(f"License not found: {license_id}")
            
            license_record = self.active_licenses[license_id]
            
            # Only licensor can revoke
            if revoker_address != license_record.licensor_address:
                raise ValueError("Only licensor can revoke license")
            
            self.logger.info(f"Revoking license: {license_id}")
            
            # Record revocation on blockchain
            revocation_tx = await self._record_revocation_on_blockchain(
                license_id, revoker_address, reason
            )
            
            # Update license status
            license_record.status = LicenseStatus.REVOKED
            
            result = {
                "license_id": license_id,
                "status": "revoked",
                "revoker_address": revoker_address,
                "reason": reason,
                "revocation_tx": revocation_tx["tx_hash"],
                "revoked_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"License revoked: {license_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"License revocation failed: {e}")
            raise
    
    async def _record_revocation_on_blockchain(
        self,
        license_id: str,
        revoker_address: str,
        reason: str
    ) -> Dict[str, Any]:
        """Record license revocation on blockchain"""
        revocation_data = {
            "license_id": license_id,
            "revoker_address": revoker_address,
            "reason": reason,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(revocation_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345684,
            "gas_used": 80000
        }
    
    async def get_license_info(self, license_id: str) -> Dict[str, Any]:
        """Get detailed license information"""
        if license_id not in self.active_licenses:
            raise ValueError(f"License not found: {license_id}")
        
        license_record = self.active_licenses[license_id]
        
        return {
            "license_id": license_record.license_id,
            "content_id": license_record.content_id,
            "copyright_id": license_record.copyright_id,
            "licensor_address": license_record.licensor_address,
            "licensee_address": license_record.licensee_address,
            "terms": {
                "license_type": license_record.terms.license_type.value,
                "usage_types": [ut.value for ut in license_record.terms.usage_types],
                "max_uses": license_record.terms.max_uses,
                "territory": license_record.terms.territory,
                "duration_days": license_record.terms.duration_days,
                "price": str(license_record.terms.price),
                "currency": license_record.terms.currency,
                "revenue_share_percentage": str(license_record.terms.revenue_share_percentage) if license_record.terms.revenue_share_percentage else None,
                "attribution_required": license_record.terms.attribution_required,
                "commercial_use_allowed": license_record.terms.commercial_use_allowed,
                "derivative_works_allowed": license_record.terms.derivative_works_allowed,
                "sublicensing_allowed": license_record.terms.sublicensing_allowed,
                "restrictions": license_record.terms.restrictions,
                "additional_terms": license_record.terms.additional_terms
            },
            "status": license_record.status.value,
            "created_at": license_record.created_at.isoformat(),
            "activated_at": license_record.activated_at.isoformat() if license_record.activated_at else None,
            "expires_at": license_record.expires_at.isoformat() if license_record.expires_at else None,
            "transaction_hash": license_record.transaction_hash,
            "block_number": license_record.block_number,
            "usage_count": license_record.usage_count,
            "revenue_generated": str(license_record.revenue_generated),
            "last_used_at": license_record.last_used_at.isoformat() if license_record.last_used_at else None
        }
    
    async def get_license_usage_history(
        self,
        license_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get license usage history"""
        usage_records = [
            {
                "usage_id": usage.usage_id,
                "license_id": usage.license_id,
                "user_address": usage.user_address,
                "usage_type": usage.usage_type.value,
                "usage_timestamp": usage.usage_timestamp.isoformat(),
                "location": usage.location,
                "device_info": usage.device_info,
                "revenue_generated": str(usage.revenue_generated),
                "transaction_hash": usage.transaction_hash
            }
            for usage in self.license_usage_history
            if usage.license_id == license_id
        ]
        
        return usage_records[:limit]
    
    async def get_licensing_analytics(self) -> Dict[str, Any]:
        """Get licensing system analytics"""
        total_licenses = len(self.active_licenses)
        status_counts = {}
        type_counts = {}
        total_revenue = Decimal("0")
        
        for license_record in self.active_licenses.values():
            status = license_record.status.value
            license_type = license_record.terms.license_type.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[license_type] = type_counts.get(license_type, 0) + 1
            total_revenue += license_record.revenue_generated
        
        return {
            "total_licenses": total_licenses,
            "status_distribution": status_counts,
            "license_type_distribution": type_counts,
            "total_revenue": str(total_revenue),
            "total_usage_records": len(self.license_usage_history),
            "average_revenue_per_license": str(total_revenue / max(total_licenses, 1)),
            "available_templates": list(self.license_templates.keys())
        }


class LicenseManager:
    """
    High-level manager for licensing operations
    """
    
    def __init__(self, licensing_system: LicensingSystem):
        """
        Initialize License Manager
        
        Args:
            licensing_system: Underlying licensing system
        """
        self.licensing_system = licensing_system
        self.logger = logging.getLogger(__name__)
    
    async def create_license_from_template(
        self,
        content_id: str,
        copyright_id: str,
        licensor_address: str,
        licensee_address: str,
        template_name: str,
        custom_price: Optional[Decimal] = None
    ) -> License:
        """Create license using predefined template with optional price override"""
        custom_terms = {}
        if custom_price is not None:
            custom_terms["price"] = custom_price
        
        return await self.licensing_system.create_license(
            content_id, copyright_id, licensor_address, licensee_address,
            template_name, custom_terms
        )
    
    async def bulk_license_creation(
        self,
        license_requests: List[Dict[str, Any]]
    ) -> List[License]:
        """Create multiple licenses in batch"""
        results = []
        
        for request in license_requests:
            try:
                license_record = await self.licensing_system.create_license(**request)
                results.append(license_record)
            except Exception as e:
                self.logger.error(f"Bulk license creation failed for request: {e}")
                # Continue with other licenses
        
        return results
    
    async def get_user_licenses(
        self,
        user_address: str,
        role: str = "both"  # "licensor", "licensee", or "both"
    ) -> List[Dict[str, Any]]:
        """Get all licenses for a user"""
        user_licenses = []
        
        for license_record in self.licensing_system.active_licenses.values():
            if (role in ["licensor", "both"] and license_record.licensor_address == user_address) or \
               (role in ["licensee", "both"] and license_record.licensee_address == user_address):
                license_info = await self.licensing_system.get_license_info(license_record.license_id)
                user_licenses.append(license_info)
        
        return user_licenses