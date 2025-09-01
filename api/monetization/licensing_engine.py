"""Automated licensing engine for content monetization and rights management.

This module implements sophisticated content licensing workflows including:
- Automated license generation and management
- Rights negotiation and pricing algorithms  
- Multi-territory licensing support
- Revenue sharing and royalty distribution
- Legal compliance and contract automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Legal Technology Specialist: Rights Management & Contract Automation
- Licensing Strategy Expert: Content Monetization & Revenue Models
- Intellectual Property Lawyer: Legal Compliance & Rights Protection
- Business Development Manager: Partnership & Licensing Negotiations

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
from pathlib import Path
import hashlib
from urllib.parse import quote
import aiofiles
import jinja2
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from ..core.config import get_database
from ..core.exceptions import LicensingException, ContractException


class LicenseType(Enum):
    """
Types of content licenses available."""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC_LICENSE = "sync_license"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"
    SYNCHRONIZATION = "synchronization"
    DERIVATIVE_WORKS = "derivative_works"
    COMMERCIAL_USE = "commercial_use"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    DOWNLOAD = "download"


class LicenseStatus(Enum):
    """License agreement status."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    RENEWED = "renewed"


class Territory(Enum):
    """Geographic territories for licensing."""

    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    UNITED_STATES = "united_states"
    UNITED_KINGDOM = "united_kingdom"
    GERMANY = "germany"
    FRANCE = "france"
    JAPAN = "japan"
    CHINA = "china"
    CUSTOM = "custom"


class UsageType(Enum):
    """Types of licensed content usage."""

    COMMERCIAL_ADVERTISING = "commercial_advertising"
    FILM_TV = "film_tv"
    DOCUMENTARY = "documentary"
    CORPORATE_VIDEO = "corporate_video"
    ONLINE_VIDEO = "online_video"
    PODCAST = "podcast"
    RADIO = "radio"
    LIVE_PERFORMANCE = "live_performance"
    STREAMING_PLATFORM = "streaming_platform"
    SOCIAL_MEDIA = "social_media"
    EDUCATIONAL = "educational"
    NON_PROFIT = "non_profit"


@dataclass
class LicenseTerms:
    """Licensing terms and conditions."""
    license_type: LicenseType
    territory: Territory
    usage_type: UsageType
    duration_months: int
    base_fee: Decimal
    royalty_percentage: Decimal
    minimum_guarantee: Decimal
    advance_payment: Decimal
    exclusivity: bool = False
    sublicense_rights: bool = False
    modification_rights: bool = False
    attribution_required: bool = True
    commercial_use_allowed: bool = True
    broadcast_rights: bool = False
    streaming_rights: bool = True
    download_rights: bool = False
    territory_restrictions: List[str] = field(default_factory=list)
    usage_limitations: List[str] = field(default_factory=list)
    performance_restrictions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueShare:
    """
Revenue sharing configuration."""
    creator_percentage: Decimal
    platform_percentage: Decimal
    publisher_percentage: Decimal
    distributor_percentage: Decimal
    performance_rights_percentage: Decimal
    mechanical_rights_percentage: Decimal
    sync_rights_percentage: Decimal
    minimum_payout_threshold: Decimal = Decimal("50.00")
    payout_frequency: str = "monthly"
    currency: str = "USD"


@dataclass
class LicenseAgreement:
    """Complete license agreement structure."""
    agreement_id: str
    creator_id: str
    licensee_id: str
    content_id: str
    license_terms: LicenseTerms
    revenue_share: RevenueShare
    status: LicenseStatus
    created_at: datetime
    effective_date: datetime
    expiration_date: datetime
    total_value: Decimal
    advance_paid: Decimal
    royalties_paid: Decimal
    contract_hash: str
    legal_jurisdiction: str = "United States"
    governing_law: str = "California"
    dispute_resolution: str = "arbitration"
    force_majeure_clause: bool = True
    termination_notice_days: int = 30
    renewal_options: Dict[str, Any] = field(default_factory=dict)
    special_provisions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LicenseRequest:
    """Incoming license request from potential licensee."""
    request_id: str
    licensee_id: str
    content_id: str
    requested_terms: LicenseTerms
    proposed_budget: Decimal
    intended_usage: str
    project_description: str
    urgency_level: str
    contact_information: Dict[str, str]
    additional_requirements: List[str] = field(default_factory=list)
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"


@dataclass
class RoyaltyPayment:
    """Royalty payment tracking."""
    payment_id: str
    agreement_id: str
    creator_id: str
    licensee_id: str
    payment_period_start: datetime
    payment_period_end: datetime
    gross_revenue: Decimal
    net_revenue: Decimal
    royalty_rate: Decimal
    royalty_amount: Decimal
    deductions: Dict[str, Decimal]
    payment_date: datetime
    payment_status: str
    transaction_reference: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutomatedLicensingEngine:
    """
    Advanced automated licensing and rights management system.
    
    Provides comprehensive licensing workflow automation including:
    - Intelligent license term generation
    - Automated contract creation and management
    - Revenue sharing and royalty calculations
    - Multi-territory licensing support
    - Legal compliance and contract enforcement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("monetization.licensing_engine")
        self.db = get_database()
        
        # Contract template settings
        self.template_path = Path(self.config.get("template_path", "./templates/licenses"))
        self.contract_storage_path = Path(self.config.get("contract_storage", "./contracts"))
        
        # Legal settings
        self.default_jurisdiction = self.config.get("default_jurisdiction", "United States")
        self.default_governing_law = self.config.get("default_governing_law", "California")
        
        # Pricing algorithms
        self.base_pricing_matrix = self._initialize_pricing_matrix()
        self.territory_multipliers = self._initialize_territory_multipliers()
        self.usage_multipliers = self._initialize_usage_multipliers()
        
        # Revenue sharing defaults
        self.default_revenue_shares = self._initialize_default_revenue_shares()
        
        # Contract encryption
        self.encryption_key = self._initialize_encryption_key()
        
        # Template engine
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_path)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Ensure directories exist
        self.template_path.mkdir(parents=True, exist_ok=True)
        self.contract_storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("AutomatedLicensingEngine initialized successfully")
    
    def _initialize_pricing_matrix(self) -> Dict[LicenseType, Dict[str, Decimal]]:
        """Initialize base pricing matrix for different license types."""
        return {
            LicenseType.EXCLUSIVE: {
                "base_fee": Decimal("5000.00"),
                "royalty_rate": Decimal("0.15"),  # 15%
                "minimum_guarantee": Decimal("2000.00")
            },
            LicenseType.NON_EXCLUSIVE: {
                "base_fee": Decimal("1000.00"),
                "royalty_rate": Decimal("0.10"),  # 10%
                "minimum_guarantee": Decimal("500.00")
            },
            LicenseType.SYNC_LICENSE: {
                "base_fee": Decimal("2500.00"),
                "royalty_rate": Decimal("0.12"),  # 12%
                "minimum_guarantee": Decimal("1000.00")
            },
            LicenseType.MECHANICAL: {
                "base_fee": Decimal("500.00"),
                "royalty_rate": Decimal("0.08"),  # 8%
                "minimum_guarantee": Decimal("200.00")
            },
            LicenseType.PERFORMANCE: {
                "base_fee": Decimal("1500.00"),
                "royalty_rate": Decimal("0.12"),  # 12%
                "minimum_guarantee": Decimal("600.00")
            },
            LicenseType.STREAMING: {
                "base_fee": Decimal("800.00"),
                "royalty_rate": Decimal("0.08"),  # 8%
                "minimum_guarantee": Decimal("300.00")
            }
        }
    
    def _initialize_territory_multipliers(self) -> Dict[Territory, Decimal]:
        """Initialize territory-based pricing multipliers."""
        return {
            Territory.WORLDWIDE: Decimal("3.0"),
            Territory.NORTH_AMERICA: Decimal("1.8"),
            Territory.EUROPE: Decimal("1.6"),
            Territory.ASIA_PACIFIC: Decimal("1.4"),
            Territory.UNITED_STATES: Decimal("1.5"),
            Territory.UNITED_KINGDOM: Decimal("1.3"),
            Territory.GERMANY: Decimal("1.2"),
            Territory.FRANCE: Decimal("1.1"),
            Territory.JAPAN: Decimal("1.3"),
            Territory.CHINA: Decimal("1.2"),
            Territory.LATIN_AMERICA: Decimal("0.8"),
            Territory.MIDDLE_EAST: Decimal("0.7"),
            Territory.AFRICA: Decimal("0.6")
        }
    
    def _initialize_usage_multipliers(self) -> Dict[UsageType, Decimal]:
        """Initialize usage-based pricing multipliers."""
        return {
            UsageType.COMMERCIAL_ADVERTISING: Decimal("2.5"),
            UsageType.FILM_TV: Decimal("2.0"),
            UsageType.DOCUMENTARY: Decimal("1.2"),
            UsageType.CORPORATE_VIDEO: Decimal("1.5"),
            UsageType.ONLINE_VIDEO: Decimal("1.0"),
            UsageType.PODCAST: Decimal("0.8"),
            UsageType.RADIO: Decimal("1.3"),
            UsageType.LIVE_PERFORMANCE: Decimal("1.4"),
            UsageType.STREAMING_PLATFORM: Decimal("1.1"),
            UsageType.SOCIAL_MEDIA: Decimal("0.6"),
            UsageType.EDUCATIONAL: Decimal("0.5"),
            UsageType.NON_PROFIT: Decimal("0.3")
        }
    
    def _initialize_default_revenue_shares(self) -> Dict[str, RevenueShare]:
        """Initialize default revenue sharing configurations."""
        return {
            "standard": RevenueShare(
                creator_percentage=Decimal("70.00"),
                platform_percentage=Decimal("20.00"),
                publisher_percentage=Decimal("5.00"),
                distributor_percentage=Decimal("3.00"),
                performance_rights_percentage=Decimal("1.00"),
                mechanical_rights_percentage=Decimal("1.00"),
                sync_rights_percentage=Decimal("0.00")
            ),
            "premium": RevenueShare(
                creator_percentage=Decimal("80.00"),
                platform_percentage=Decimal("15.00"),
                publisher_percentage=Decimal("3.00"),
                distributor_percentage=Decimal("2.00"),
                performance_rights_percentage=Decimal("0.00"),
                mechanical_rights_percentage=Decimal("0.00"),
                sync_rights_percentage=Decimal("0.00")
            ),
            "sync_heavy": RevenueShare(
                creator_percentage=Decimal("60.00"),
                platform_percentage=Decimal("15.00"),
                publisher_percentage=Decimal("10.00"),
                distributor_percentage=Decimal("5.00"),
                performance_rights_percentage=Decimal("5.00"),
                mechanical_rights_percentage=Decimal("2.50"),
                sync_rights_percentage=Decimal("2.50")
            )
        }
    
    def _initialize_encryption_key(self) -> Fernet:
        """Initialize encryption key for contract security."""
        try:
            # In production, this should come from secure key management
            password = self.config.get("encryption_password", "default_password").encode()
            salt = self.config.get("encryption_salt", "default_salt").encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Encryption key initialization failed: {e}")
            # Fallback to basic key
            return Fernet(Fernet.generate_key())
    
    async def create_license_agreement(
        self,
        creator_id: str,
        licensee_id: str,
        content_id: str,
        license_terms: LicenseTerms,
        revenue_share_type: str = "standard"
    ) -> LicenseAgreement:
        """
        Create new license agreement with automated terms generation.
        
        Args:
            creator_id: Content creator identifier
            licensee_id: License purchaser identifier  
            content_id: Content being licensed
            license_terms: Licensing terms and conditions
            revenue_share_type: Revenue sharing model to use
            
        Returns:
            Complete license agreement with generated contract
        """
        try:
            self.logger.info(f"Creating license agreement for content: {content_id}")
            
            # Generate unique agreement ID
            agreement_id = f"lic_{uuid.uuid4().hex[:12]}"
            
            # Calculate pricing based on terms
            pricing = await self._calculate_license_pricing(license_terms)
            
            # Get revenue sharing configuration
            revenue_share = self.default_revenue_shares.get(
                revenue_share_type, 
                self.default_revenue_shares["standard"]
            )
            
            # Set agreement dates
            created_at = datetime.utcnow()
            effective_date = created_at + timedelta(days=1)  # Next day effective
            expiration_date = effective_date + timedelta(days=license_terms.duration_months * 30)
            
            # Create license agreement
            agreement = LicenseAgreement(
                agreement_id=agreement_id,
                creator_id=creator_id,
                licensee_id=licensee_id,
                content_id=content_id,
                license_terms=license_terms,
                revenue_share=revenue_share,
                status=LicenseStatus.DRAFT,
                created_at=created_at,
                effective_date=effective_date,
                expiration_date=expiration_date,
                total_value=pricing["total_value"],
                advance_paid=Decimal("0.00"),
                royalties_paid=Decimal("0.00"),
                contract_hash="",  # Will be set after contract generation
                legal_jurisdiction=self.default_jurisdiction,
                governing_law=self.default_governing_law
            )
            
            # Generate legal contract
            contract_data = await self._generate_contract(agreement)
            agreement.contract_hash = contract_data["hash"]
            
            # Store agreement in database
            await self._store_license_agreement(agreement)
            
            # Store contract document
            await self._store_contract_document(agreement_id, contract_data["content"])
            
            # Send notifications
            await self._send_agreement_notifications(agreement)
            
            self.logger.info(f"License agreement created successfully: {agreement_id}")
            
            return agreement
            
        except Exception as e:
            self.logger.error(f"License agreement creation failed: {e}")
            raise LicensingException(f"Agreement creation error: {e}")
    
    async def _calculate_license_pricing(self, terms: LicenseTerms) -> Dict[str, Decimal]:
        """Calculate comprehensive licensing pricing."""
        try:
            # Get base pricing for license type
            base_pricing = self.base_pricing_matrix.get(terms.license_type)
            if not base_pricing:
                raise LicensingException(f"No pricing matrix for license type: {terms.license_type}")
            
            base_fee = base_pricing["base_fee"]
            royalty_rate = base_pricing["royalty_rate"]
            minimum_guarantee = base_pricing["minimum_guarantee"]
            
            # Apply territory multiplier
            territory_multiplier = self.territory_multipliers.get(terms.territory, Decimal("1.0"))
            
            # Apply usage multiplier
            usage_multiplier = self.usage_multipliers.get(terms.usage_type, Decimal("1.0"))
            
            # Apply duration scaling
            duration_multiplier = self._calculate_duration_multiplier(terms.duration_months)
            
            # Apply exclusivity premium
            exclusivity_multiplier = Decimal("2.0") if terms.exclusivity else Decimal("1.0")
            
            # Calculate final pricing
            adjusted_base_fee = (
                base_fee * 
                territory_multiplier * 
                usage_multiplier * 
                duration_multiplier * 
                exclusivity_multiplier
            )
            
            adjusted_minimum_guarantee = (
                minimum_guarantee * 
                territory_multiplier * 
                usage_multiplier
            )
            
            # Override with provided terms if specified
            final_base_fee = terms.base_fee if terms.base_fee > 0 else adjusted_base_fee
            final_royalty_rate = terms.royalty_percentage if terms.royalty_percentage > 0 else royalty_rate
            final_minimum_guarantee = terms.minimum_guarantee if terms.minimum_guarantee > 0 else adjusted_minimum_guarantee
            
            # Calculate total value (base fee + minimum guarantee)
            total_value = final_base_fee + final_minimum_guarantee
            
            return {
                "base_fee": final_base_fee.quantize(Decimal('0.01')),
                "royalty_rate": final_royalty_rate.quantize(Decimal('0.001')),
                "minimum_guarantee": final_minimum_guarantee.quantize(Decimal('0.01')),
                "total_value": total_value.quantize(Decimal('0.01')),
                "territory_multiplier": territory_multiplier,
                "usage_multiplier": usage_multiplier,
                "duration_multiplier": duration_multiplier,
                "exclusivity_multiplier": exclusivity_multiplier
            }
            
        except Exception as e:
            self.logger.error(f"License pricing calculation failed: {e}")
            raise LicensingException(f"Pricing calculation error: {e}")
    
    def _calculate_duration_multiplier(self, duration_months: int) -> Decimal:
        """Calculate duration-based pricing multiplier."""
        if duration_months <= 3:
            return Decimal("0.8")  # Short-term discount
        elif duration_months <= 6:
            return Decimal("1.0")  # Standard rate
        elif duration_months <= 12:
            return Decimal("1.2")  # Annual premium
        elif duration_months <= 24:
            return Decimal("1.5")  # Multi-year premium
        else:
            return Decimal("2.0")  # Long-term premium
    
    async def _generate_contract(self, agreement: LicenseAgreement) -> Dict[str, str]:
        """Generate legal contract document from agreement."""
        try:
            # Select appropriate contract template
            template_name = self._get_contract_template(agreement.license_terms.license_type)
            
            # Prepare template context
            context = await self._prepare_contract_context(agreement)
            
            # Load and render template
            try:
                template = self.template_env.get_template(template_name)
                contract_content = template.render(**context)
            except jinja2.TemplateNotFound:
                # Fallback to default template
                contract_content = await self._generate_default_contract(agreement, context)
            
            # Generate contract hash for integrity
            contract_hash = hashlib.sha256(contract_content.encode()).hexdigest()
            
            return {
                "content": contract_content,
                "hash": contract_hash,
                "template": template_name
            }
            
        except Exception as e:
            self.logger.error(f"Contract generation failed: {e}")
            raise ContractException(f"Contract generation error: {e}")
    
    def _get_contract_template(self, license_type: LicenseType) -> str:
        """Get appropriate contract template for license type."""
        template_mapping = {
            LicenseType.EXCLUSIVE: "exclusive_license_agreement.html",
            LicenseType.NON_EXCLUSIVE: "non_exclusive_license_agreement.html",
            LicenseType.SYNC_LICENSE: "sync_license_agreement.html",
            LicenseType.MECHANICAL: "mechanical_license_agreement.html",
            LicenseType.PERFORMANCE: "performance_license_agreement.html",
            LicenseType.STREAMING: "streaming_license_agreement.html"
        }
        
        return template_mapping.get(license_type, "standard_license_agreement.html")
    
    async def _prepare_contract_context(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Prepare template context for contract generation."""
        try:
            # Get creator and licensee information
            creator_info = await self._get_creator_info(agreement.creator_id)
            licensee_info = await self._get_licensee_info(agreement.licensee_id)
            content_info = await self._get_content_info(agreement.content_id)
            
            return {
                "agreement": agreement,
                "creator": creator_info,
                "licensee": licensee_info,
                "content": content_info,
                "terms": agreement.license_terms,
                "revenue_share": agreement.revenue_share,
                "generation_date": datetime.utcnow().strftime("%B %d, %Y"),
                "effective_date_formatted": agreement.effective_date.strftime("%B %d, %Y"),
                "expiration_date_formatted": agreement.expiration_date.strftime("%B %d, %Y"),
                "total_value_formatted": f"${agreement.total_value:,.2f}",
                "currency_symbol": "$",
                "legal_jurisdiction": agreement.legal_jurisdiction,
                "governing_law": agreement.governing_law
            }
            
        except Exception as e:
            self.logger.error(f"Contract context preparation failed: {e}")
            return {}
    
    async def _get_creator_info(self, creator_id: str) -> Dict[str, Any]:
        """Get creator information for contract."""
        try:
            query = """
            SELECT 
                name, email, legal_name, business_name,
                address, city, state, country, postal_code,
                tax_id, business_type
            FROM creators 
            WHERE creator_id = $1
            """
            
            result = await self.db.fetchrow(query, creator_id)
            
            if result:
                return dict(result)
            else:
                return {
                    "name": "Creator Name",
                    "email": "creator@example.com",
                    "legal_name": "Creator Legal Name",
                    "address": "Creator Address"
                }
                
        except Exception as e:
            self.logger.error(f"Creator info retrieval failed: {e}")
            return {"name": "Creator", "email": "creator@example.com"}
    
    async def _get_licensee_info(self, licensee_id: str) -> Dict[str, Any]:
        """Get licensee information for contract."""
        try:
            query = """
            SELECT 
                company_name, contact_name, email, legal_name,
                address, city, state, country, postal_code,
                tax_id, business_type, industry
            FROM licensees 
            WHERE licensee_id = $1
            """
            
            result = await self.db.fetchrow(query, licensee_id)
            
            if result:
                return dict(result)
            else:
                return {
                    "company_name": "Licensee Company",
                    "contact_name": "Contact Name",
                    "email": "licensee@example.com",
                    "address": "Licensee Address"
                }
                
        except Exception as e:
            self.logger.error(f"Licensee info retrieval failed: {e}")
            return {"company_name": "Licensee", "email": "licensee@example.com"}
    
    async def _get_content_info(self, content_id: str) -> Dict[str, Any]:
        """Get content information for contract."""
        try:
            query = """
            SELECT 
                title, description, duration, genre, release_date,
                isrc, upc, composer, lyricist, publisher,
                recording_date, master_owner
            FROM content_catalog 
            WHERE content_id = $1
            """
            
            result = await self.db.fetchrow(query, content_id)
            
            if result:
                return dict(result)
            else:
                return {
                    "title": "Content Title",
                    "description": "Content Description",
                    "genre": "Music",
                    "composer": "Composer Name"
                }
                
        except Exception as e:
            self.logger.error(f"Content info retrieval failed: {e}")
            return {"title": "Content", "description": "Licensed Content"}
    
    async def _generate_default_contract(
        self,
        agreement: LicenseAgreement,
        context: Dict[str, Any]
    ) -> str:
        """Generate default contract when template is not available."""
        
        contract_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>License Agreement - {agreement.agreement_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .signature-block {{ margin-top: 50px; border-top: 1px solid #ccc; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MUSIC LICENSING AGREEMENT</h1>
        <p>Agreement ID: {agreement.agreement_id}</p>
        <p>Date: {context.get('generation_date', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>PARTIES</h2>
        <p><strong>LICENSOR:</strong> {context.get('creator', {}).get('legal_name', 'Creator Name')}<br>
        Email: {context.get('creator', {}).get('email', 'N/A')}</p>
        
        <p><strong>LICENSEE:</strong> {context.get('licensee', {}).get('company_name', 'Licensee Company')}<br>
        Contact: {context.get('licensee', {}).get('contact_name', 'N/A')}<br>
        Email: {context.get('licensee', {}).get('email', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>LICENSED WORK</h2>
        <p><strong>Title:</strong> {context.get('content', {}).get('title', 'N/A')}<br>
        <strong>Description:</strong> {context.get('content', {}).get('description', 'N/A')}<br>
        <strong>Genre:</strong> {context.get('content', {}).get('genre', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>LICENSE TERMS</h2>
        <p><strong>License Type:</strong> {agreement.license_terms.license_type.value.replace('_', ' ').title()}<br>
        <strong>Territory:</strong> {agreement.license_terms.territory.value.replace('_', ' ').title()}<br>
        <strong>Usage Type:</strong> {agreement.license_terms.usage_type.value.replace('_', ' ').title()}<br>
        <strong>Duration:</strong> {agreement.license_terms.duration_months} months<br>
        <strong>Effective Date:</strong> {context.get('effective_date_formatted', 'N/A')}<br>
        <strong>Expiration Date:</strong> {context.get('expiration_date_formatted', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>FINANCIAL TERMS</h2>
        <p><strong>Base License Fee:</strong> ${agreement.license_terms.base_fee:,.2f}<br>
        <strong>Royalty Rate:</strong> {agreement.license_terms.royalty_percentage:.1%}<br>
        <strong>Minimum Guarantee:</strong> ${agreement.license_terms.minimum_guarantee:,.2f}<br>
        <strong>Total Agreement Value:</strong> {context.get('total_value_formatted', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>REVENUE SHARING</h2>
        <p><strong>Creator Share:</strong> {agreement.revenue_share.creator_percentage:.1%}<br>
        <strong>Platform Share:</strong> {agreement.revenue_share.platform_percentage:.1%}<br>
        <strong>Publisher Share:</strong> {agreement.revenue_share.publisher_percentage:.1%}</p>
    </div>

    <div class="section">
        <h2>RIGHTS GRANTED</h2>
        <ul>
            <li>Commercial Use: {'Yes' if agreement.license_terms.commercial_use_allowed else 'No'}</li>
            <li>Broadcast Rights: {'Yes' if agreement.license_terms.broadcast_rights else 'No'}</li>
            <li>Streaming Rights: {'Yes' if agreement.license_terms.streaming_rights else 'No'}</li>
            <li>Download Rights: {'Yes' if agreement.license_terms.download_rights else 'No'}</li>
            <li>Modification Rights: {'Yes' if agreement.license_terms.modification_rights else 'No'}</li>
            <li>Sublicense Rights: {'Yes' if agreement.license_terms.sublicense_rights else 'No'}</li>
        </ul>
    </div>

    <div class="section">
        <h2>LEGAL TERMS</h2>
        <p><strong>Governing Law:</strong> {agreement.governing_law}<br>
        <strong>Jurisdiction:</strong> {agreement.legal_jurisdiction}<br>
        <strong>Dispute Resolution:</strong> {agreement.dispute_resolution.title()}<br>
        <strong>Termination Notice:</strong> {agreement.termination_notice_days} days</p>
    </div>

    <div class="signature-block">
        <div style="display: flex; justify-content: space-between;">
            <div style="width: 45%;">
                <p><strong>LICENSOR:</strong></p>
                <br><br>
                <p>_________________________<br>
                {context.get('creator', {}).get('legal_name', 'Creator Name')}<br>
                Date: _______________</p>
            </div>
            <div style="width: 45%;">
                <p><strong>LICENSEE:</strong></p>
                <br><br>
                <p>_________________________<br>
                {context.get('licensee', {}).get('contact_name', 'Licensee Representative')}<br>
                Date: _______________</p>
            </div>
        </div>
    </div>

    <div style="margin-top: 30px; font-size: 12px; color: #666; text-align: center;">
        <p>This agreement was generated automatically by the IA-Influencer Licensing System<br>
        Contract Hash: {agreement.contract_hash}<br>
        Generated on: {context.get('generation_date', 'N/A')}</p>
    </div>
</body>
</html>
        """
        
        return contract_template
    
    async def _store_license_agreement(self, agreement: LicenseAgreement):
        """
Store license agreement in database."""
        try:
            query = """
            INSERT INTO license_agreements (
                agreement_id, creator_id, licensee_id, content_id,
                license_type, territory, usage_type, duration_months,
                base_fee, royalty_percentage, minimum_guarantee, advance_payment,
                exclusivity, sublicense_rights, modification_rights,
                attribution_required, commercial_use_allowed, broadcast_rights,
                streaming_rights, download_rights, territory_restrictions,
                usage_limitations, performance_restrictions, status,
                created_at, effective_date, expiration_date, total_value,
                advance_paid, royalties_paid, contract_hash,
                legal_jurisdiction, governing_law, dispute_resolution,
                force_majeure_clause, termination_notice_days,
                renewal_options, special_provisions, metadata,
                creator_percentage, platform_percentage, publisher_percentage,
                distributor_percentage, performance_rights_percentage,
                mechanical_rights_percentage, sync_rights_percentage,
                minimum_payout_threshold, payout_frequency, currency
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                      $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,
                      $23, $24, $25, $26, $27, $28, $29, $30, $31, $32,
                      $33, $34, $35, $36, $37, $38, $39, $40, $41, $42,
                      $43, $44, $45, $46, $47, $48, $49, $50)
            """
            
            await self.db.execute(
                query,
                agreement.agreement_id,
                agreement.creator_id,
                agreement.licensee_id,
                agreement.content_id,
                agreement.license_terms.license_type.value,
                agreement.license_terms.territory.value,
                agreement.license_terms.usage_type.value,
                agreement.license_terms.duration_months,
                agreement.license_terms.base_fee,
                agreement.license_terms.royalty_percentage,
                agreement.license_terms.minimum_guarantee,
                agreement.license_terms.advance_payment,
                agreement.license_terms.exclusivity,
                agreement.license_terms.sublicense_rights,
                agreement.license_terms.modification_rights,
                agreement.license_terms.attribution_required,
                agreement.license_terms.commercial_use_allowed,
                agreement.license_terms.broadcast_rights,
                agreement.license_terms.streaming_rights,
                agreement.license_terms.download_rights,
                json.dumps(agreement.license_terms.territory_restrictions),
                json.dumps(agreement.license_terms.usage_limitations),
                json.dumps(agreement.license_terms.performance_restrictions),
                agreement.status.value,
                agreement.created_at,
                agreement.effective_date,
                agreement.expiration_date,
                agreement.total_value,
                agreement.advance_paid,
                agreement.royalties_paid,
                agreement.contract_hash,
                agreement.legal_jurisdiction,
                agreement.governing_law,
                agreement.dispute_resolution,
                agreement.force_majeure_clause,
                agreement.termination_notice_days,
                json.dumps(agreement.renewal_options),
                json.dumps(agreement.special_provisions),
                json.dumps(agreement.metadata),
                agreement.revenue_share.creator_percentage,
                agreement.revenue_share.platform_percentage,
                agreement.revenue_share.publisher_percentage,
                agreement.revenue_share.distributor_percentage,
                agreement.revenue_share.performance_rights_percentage,
                agreement.revenue_share.mechanical_rights_percentage,
                agreement.revenue_share.sync_rights_percentage,
                agreement.revenue_share.minimum_payout_threshold,
                agreement.revenue_share.payout_frequency,
                agreement.revenue_share.currency
            )
            
            self.logger.info(f"License agreement stored successfully: {agreement.agreement_id}")
            
        except Exception as e:
            self.logger.error(f"License agreement storage failed: {e}")
            raise LicensingException(f"Agreement storage error: {e}")
    
    async def _store_contract_document(self, agreement_id: str, contract_content: str):
        """Store encrypted contract document."""
        try:
            # Encrypt contract content
            encrypted_content = self.encryption_key.encrypt(contract_content.encode())
            
            # Store in filesystem
            contract_file = self.contract_storage_path / f"{agreement_id}_contract.enc"
            
            async with aiofiles.open(contract_file, 'wb') as f:
                await f.write(encrypted_content)
            
            # Store metadata in database
            query = """
            INSERT INTO contract_documents (
                agreement_id, file_path, file_size, content_hash,
                encryption_method, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            content_hash = hashlib.sha256(contract_content.encode()).hexdigest()
            
            await self.db.execute(
                query,
                agreement_id,
                str(contract_file),
                len(encrypted_content),
                content_hash,
                "Fernet",
                datetime.utcnow()
            )
            
            self.logger.info(f"Contract document stored successfully: {agreement_id}")
            
        except Exception as e:
            self.logger.error(f"Contract document storage failed: {e}")
            raise ContractException(f"Document storage error: {e}")
    
    async def _send_agreement_notifications(self, agreement: LicenseAgreement):
        """Send notifications about new agreement."""
        try:
            # This would integrate with notification service
            # For now, just log the notification
            self.logger.info(
                f"Agreement notification sent for {agreement.agreement_id} "
                f"to creator {agreement.creator_id} and licensee {agreement.licensee_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Agreement notification failed: {e}")
    
    async def process_license_request(
        self,
        license_request: LicenseRequest
    ) -> Dict[str, Any]:
        """
        Process incoming license request with automated evaluation.
        
        Args:
            license_request: Incoming license request to process
            
        Returns:
            Processing result with recommendation and pricing
        """
        try:
            self.logger.info(f"Processing license request: {license_request.request_id}")
            
            # Evaluate request feasibility
            evaluation = await self._evaluate_license_request(license_request)
            
            # Generate pricing recommendation
            pricing_recommendation = await self._generate_pricing_recommendation(license_request)
            
            # Check content availability
            content_availability = await self._check_content_availability(
                license_request.content_id,
                license_request.requested_terms
            )
            
            # Generate counter-proposal if needed
            counter_proposal = await self._generate_counter_proposal(
                license_request,
                evaluation,
                pricing_recommendation
            )
            
            # Determine automatic approval eligibility
            auto_approval_eligible = await self._check_auto_approval_eligibility(
                license_request,
                evaluation
            )
            
            result = {
                "request_id": license_request.request_id,
                "evaluation": evaluation,
                "pricing_recommendation": pricing_recommendation,
                "content_availability": content_availability,
                "counter_proposal": counter_proposal,
                "auto_approval_eligible": auto_approval_eligible,
                "processing_status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Store processing result
            await self._store_request_processing_result(license_request.request_id, result)
            
            # Auto-approve if eligible
            if auto_approval_eligible and evaluation["score"] >= 0.8:
                approval_result = await self._auto_approve_request(license_request, counter_proposal)
                result["auto_approval"] = approval_result
            
            self.logger.info(f"License request processed successfully: {license_request.request_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"License request processing failed: {e}")
            raise LicensingException(f"Request processing error: {e}")
    
    async def _evaluate_license_request(self, request: LicenseRequest) -> Dict[str, Any]:
        """Evaluate license request quality and feasibility."""
        try:
            evaluation_score = 0.0
            evaluation_factors = {}
            
            # Budget evaluation (30% weight)
            budget_score = await self._evaluate_budget_adequacy(
                request.proposed_budget,
                request.requested_terms
            )
            evaluation_factors["budget_adequacy"] = budget_score
            evaluation_score += budget_score * 0.30
            
            # Licensee reputation (25% weight)
            reputation_score = await self._evaluate_licensee_reputation(request.licensee_id)
            evaluation_factors["licensee_reputation"] = reputation_score
            evaluation_score += reputation_score * 0.25
            
            # Content fit (20% weight)
            content_fit_score = await self._evaluate_content_usage_fit(
                request.content_id,
                request.intended_usage,
                request.requested_terms.usage_type
            )
            evaluation_factors["content_usage_fit"] = content_fit_score
            evaluation_score += content_fit_score * 0.20
            
            # Request completeness (15% weight)
            completeness_score = self._evaluate_request_completeness(request)
            evaluation_factors["request_completeness"] = completeness_score
            evaluation_score += completeness_score * 0.15
            
            # Urgency penalty/bonus (10% weight)
            urgency_score = self._evaluate_urgency_factor(request.urgency_level)
            evaluation_factors["urgency_factor"] = urgency_score
            evaluation_score += urgency_score * 0.10
            
            # Determine recommendation
            if evaluation_score >= 0.8:
                recommendation = "approve"
            elif evaluation_score >= 0.6:
                recommendation = "negotiate"
            elif evaluation_score >= 0.4:
                recommendation = "counter_offer"
            else:
                recommendation = "decline"
            
            return {
                "score": round(evaluation_score, 3),
                "recommendation": recommendation,
                "factors": evaluation_factors,
                "confidence": min(1.0, evaluation_score + 0.2),
                "risk_level": "low" if evaluation_score >= 0.7 else "medium" if evaluation_score >= 0.4 else "high"
            }
            
        except Exception as e:
            self.logger.error(f"Request evaluation failed: {e}")
            return {
                "score": 0.0,
                "recommendation": "manual_review",
                "factors": {},
                "confidence": 0.0,
                "risk_level": "high"
            }
    
    async def _evaluate_budget_adequacy(
        self,
        proposed_budget: Decimal,
        requested_terms: LicenseTerms
    ) -> float:
        """Evaluate if proposed budget is adequate for requested terms."""
        try:
            # Calculate expected pricing for requested terms
            expected_pricing = await self._calculate_license_pricing(requested_terms)
            expected_total = expected_pricing["total_value"]
            
            # Calculate budget adequacy ratio
            if expected_total == 0:
                return 0.5  # Neutral score
            
            budget_ratio = float(proposed_budget / expected_total)
            
            # Convert ratio to score (0-1)
            if budget_ratio >= 1.2:  # 20% above expected
                return 1.0
            elif budget_ratio >= 1.0:  # At or above expected
                return 0.9
            elif budget_ratio >= 0.8:  # 80% of expected
                return 0.7
            elif budget_ratio >= 0.6:  # 60% of expected
                return 0.4
            else:  # Below 60%
                return 0.1
                
        except Exception as e:
            self.logger.error(f"Budget evaluation failed: {e}")
            return 0.5  # Default score
    
    async def _evaluate_licensee_reputation(self, licensee_id: str) -> float:
        """Evaluate licensee reputation and payment history."""
        try:
            query = """
            SELECT 
                COUNT(*) as total_agreements,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completion_rate,
                AVG(CASE WHEN payment_status = 'paid_on_time' THEN 1 ELSE 0 END) as payment_rate,
                AVG(rating) as average_rating
            FROM licensee_history 
            WHERE licensee_id = $1
            """
            
            result = await self.db.fetchrow(query, licensee_id)
            
            if not result or result["total_agreements"] == 0:
                return 0.5  # Neutral score for new licensees
            
            # Calculate reputation score
            completion_rate = float(result["completion_rate"] or 0)
            payment_rate = float(result["payment_rate"] or 0)
            average_rating = float(result["average_rating"] or 3.0) / 5.0  # Normalize to 0-1
            
            reputation_score = (completion_rate * 0.4) + (payment_rate * 0.4) + (average_rating * 0.2)
            
            return min(1.0, reputation_score)
            
        except Exception as e:
            self.logger.error(f"Licensee reputation evaluation failed: {e}")
            return 0.5
    
    async def _evaluate_content_usage_fit(
        self,
        content_id: str,
        intended_usage: str,
        usage_type: UsageType
    ) -> float:
        """Evaluate how well content fits intended usage."""
        try:
            # Get content metadata
            query = """
            SELECT genre, mood, tempo, explicit_content, content_tags
            FROM content_catalog 
            WHERE content_id = $1
            """
            
            result = await self.db.fetchrow(query, content_id)
            
            if not result:
                return 0.5  # Neutral if no content data
            
            # Simple fit evaluation based on usage type
            fit_score = 0.7  # Base score
            
            # Adjust based on content characteristics
            content_tags = json.loads(result["content_tags"] or "[]")
            explicit_content = result["explicit_content"]
            
            # Penalize explicit content for certain usage types
            if explicit_content and usage_type in [
                UsageType.COMMERCIAL_ADVERTISING,
                UsageType.EDUCATIONAL,
                UsageType.CORPORATE_VIDEO
            ]:
                fit_score -= 0.3
            
            # Bonus for good genre-usage alignment
            genre = result["genre"]
            if self._is_genre_usage_match(genre, usage_type):
                fit_score += 0.2
            
            return min(1.0, max(0.0, fit_score))
            
        except Exception as e:
            self.logger.error(f"Content usage fit evaluation failed: {e}")
            return 0.5
    
    def _is_genre_usage_match(self, genre: str, usage_type: UsageType) -> bool:
        """Check if genre matches well with usage type."""
        genre_usage_matches = {
            "electronic": [UsageType.COMMERCIAL_ADVERTISING, UsageType.CORPORATE_VIDEO],
            "classical": [UsageType.DOCUMENTARY, UsageType.FILM_TV],
            "pop": [UsageType.COMMERCIAL_ADVERTISING, UsageType.SOCIAL_MEDIA],
            "rock": [UsageType.COMMERCIAL_ADVERTISING, UsageType.ONLINE_VIDEO],
            "ambient": [UsageType.CORPORATE_VIDEO, UsageType.PODCAST],
            "jazz": [UsageType.DOCUMENTARY, UsageType.CORPORATE_VIDEO]
        }
        
        genre_lower = genre.lower() if genre else ""
        matching_usages = genre_usage_matches.get(genre_lower, [])
        
        return usage_type in matching_usages
    
    def _evaluate_request_completeness(self, request: LicenseRequest) -> float:
        """Evaluate completeness of license request."""
        completeness_score = 0.0
        total_fields = 10
        
        # Check required fields
        if request.proposed_budget and request.proposed_budget > 0:
            completeness_score += 0.15
        
        if request.intended_usage and len(request.intended_usage) > 10:
            completeness_score += 0.15
        
        if request.project_description and len(request.project_description) > 20:
            completeness_score += 0.15
        
        if request.contact_information and len(request.contact_information) >= 2:
            completeness_score += 0.1
        
        if request.requested_terms.duration_months > 0:
            completeness_score += 0.1
        
        if request.requested_terms.territory != Territory.CUSTOM:
            completeness_score += 0.1
        
        if request.requested_terms.usage_type:
            completeness_score += 0.1
        
        if request.urgency_level:
            completeness_score += 0.05
        
        if request.additional_requirements:
            completeness_score += 0.05
        
        # Bonus for providing all optional details
        if len(request.additional_requirements) > 0:
            completeness_score += 0.05
        
        return min(1.0, completeness_score)
    
    def _evaluate_urgency_factor(self, urgency_level: str) -> float:
        """
Evaluate urgency factor impact on approval."""
        urgency_scores = {
            "low": 0.7,      # Standard processing, slight bonus
            "normal": 0.8,   # Normal processing
            "high": 0.6,     # Rushed processing, slight penalty
            "urgent": 0.4,   # Very rushed, higher penalty
            "emergency": 0.2  # Emergency processing, significant penalty
        }
        
        return urgency_scores.get(urgency_level.lower(), 0.5)


# Factory function for easy instantiation
def create_licensing_engine(config: Optional[Dict[str, Any]] = None) -> AutomatedLicensingEngine:
    """Create and return configured licensing engine instance."""
    return AutomatedLicensingEngine(config)
