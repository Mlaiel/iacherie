"""Comprehensive rights management system for content creators and intellectual property protection.

This module implements enterprise-grade digital rights management including:
- Automated copyright registration and tracking
- Intellectual property protection workflows
- Content usage monitoring and enforcement
- Revenue tracking for protected content
- Legal compliance and DMCA automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Legal Technology Specialist: Digital Rights & IP Protection
- Copyright Automation Engineer: DMCA & Content Enforcement
- Blockchain Technology Expert: Immutable Rights Registration
- Revenue Protection Analyst: Content Monetization Security
- Compliance Officer: International Copyright Laws

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import json
import hashlib
from pathlib import Path
import aiofiles
from urllib.parse import urlencode
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_database, get_redis_client
from ..core.exceptions import RightsException, ProtectionException


class RightType(Enum):
    """
Types of intellectual property rights."""

    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    TRADE_SECRET = "trade_secret"
    PUBLICITY_RIGHT = "publicity_right"
    MORAL_RIGHT = "moral_right"
    NEIGHBORING_RIGHT = "neighboring_right"
    PERFORMANCE_RIGHT = "performance_right"
    MECHANICAL_RIGHT = "mechanical_right"
    SYNCHRONIZATION_RIGHT = "synchronization_right"


class ProtectionLevel(Enum):
    """Content protection levels."""

    PUBLIC = "public"
    PROTECTED = "protected"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"
    TOP_SECRET = "top_secret"


class UsageType(Enum):
    """Types of content usage."""

    STREAMING = "streaming"
    DOWNLOAD = "download"
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    BROADCAST = "broadcast"
    ADAPTATION = "adaptation"
    TRANSLATION = "translation"
    SYNCHRONIZATION = "synchronization"
    COMMERCIAL_USE = "commercial_use"


class EnforcementAction(Enum):
    """Types of enforcement actions."""

    TAKEDOWN_NOTICE = "takedown_notice"
    DMCA_CLAIM = "dmca_claim"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_STRIKE = "copyright_strike"
    MONETIZATION_CLAIM = "monetization_claim"
    LEGAL_ACTION = "legal_action"
    ACCOUNT_SUSPENSION = "account_suspension"
    CONTENT_BLOCKING = "content_blocking"


@dataclass
class IntellectualProperty:
    """Intellectual property registration record."""
    ip_id: str
    creator_id: str
    title: str
    description: str
    right_type: RightType
    protection_level: ProtectionLevel
    content_hash: str
    registration_number: Optional[str] = None
    registration_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    jurisdiction: str = "international"
    metadata: Dict[str, Any] = field(default_factory=dict)
    proof_of_creation: Dict[str, Any] = field(default_factory=dict)
    blockchain_record: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UsagePermission:
    """Content usage permission record."""
    permission_id: str
    ip_id: str
    grantee_id: str
    usage_type: UsageType
    granted_by: str
    start_date: datetime
    end_date: Optional[datetime] = None
    territory_restrictions: List[str] = field(default_factory=list)
    usage_conditions: Dict[str, Any] = field(default_factory=dict)
    revenue_sharing: Optional[Decimal] = None
    is_exclusive: bool = False
    is_transferable: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InfringementCase:
    """
Copyright infringement case tracking."""
    case_id: str
    ip_id: str
    reported_by: str
    infringing_url: str
    infringing_party: Optional[str] = None
    infringement_type: UsageType = UsageType.REPRODUCTION
    evidence: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    case_status: str = "reported"
    enforcement_actions: List[str] = field(default_factory=list)
    resolution_date: Optional[datetime] = None
    compensation_claimed: Optional[Decimal] = None
    compensation_received: Optional[Decimal] = None
    legal_notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RightsRevenue:
    """Revenue tracking for protected content."""
    revenue_id: str
    ip_id: str
    usage_permission_id: Optional[str] = None
    revenue_amount: Decimal = Decimal("0.00")
    currency: str = "USD"
    revenue_source: str = ""
    collection_date: datetime = field(default_factory=datetime.utcnow)
    payout_date: Optional[datetime] = None
    revenue_type: UsageType = UsageType.STREAMING
    territory: str = "global"
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnterpriseRightsManager:
    """
    Enterprise-grade digital rights management system.
    
    Provides comprehensive intellectual property protection including:
    - Automated copyright registration and tracking
    - Content usage monitoring and enforcement
    - Revenue protection and collection
    - Legal compliance automation
    - International rights management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("protection.rights_management")
        self.db = get_database()
        self.redis = get_redis_client()
        
        # Session management
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=60, connect=15)
        
        # Encryption for sensitive data
        self.encryption_key = self._initialize_encryption()
        
        # Rights monitoring settings
        self.monitoring_enabled = self.config.get("monitoring_enabled", True)
        self.scan_frequency_hours = self.config.get("scan_frequency_hours", 6)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.85)
        
        # Legal automation settings
        self.auto_takedown_enabled = self.config.get("auto_takedown", False)
        self.dmca_template_path = self.config.get("dmca_template_path", "templates/dmca.html")
        
        # Revenue tracking settings
        self.revenue_tracking_enabled = self.config.get("revenue_tracking", True)
        self.revenue_collection_schedule = self.config.get("revenue_schedule", "daily")
        
        # Thread pool for intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize components
        asyncio.create_task(self._initialize_rights_manager())
        
        self.logger.info("EnterpriseRightsManager initialized successfully")
    
    async def _initialize_rights_manager(self):
        """Initialize rights management system components."""
        try:
            # Initialize HTTP session
            await self._initialize_session()
            
            # Initialize rights monitoring
            await self._initialize_rights_monitoring()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info("Rights manager components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Rights manager initialization failed: {e}")
            raise RightsException(f"Initialization error: {e}")
    
    async def _initialize_session(self):
        """Initialize aiohttp session for external API calls."""
        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.session_timeout,
                headers={
                    "User-Agent": "IA-Influencer-Agent/2.0 Rights-Manager"
                }
            )
            
            self.logger.info("Rights manager HTTP session initialized")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise RightsException(f"Session initialization error: {e}")
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption for sensitive rights data."""
        try:
            # Get or generate encryption key
            key = self.config.get("encryption_key")
            if not key:
                # Generate new key
                password = self.config.get("encryption_password", "default_password").encode()
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
            
            return Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Encryption initialization failed: {e}")
            # Fallback to basic encryption
            return Fernet(Fernet.generate_key())
    
    async def register_intellectual_property(
        self,
        creator_id: str,
        title: str,
        description: str,
        right_type: RightType,
        content_data: bytes,
        protection_level: ProtectionLevel = ProtectionLevel.PROTECTED,
        jurisdiction: str = "international"
    ) -> IntellectualProperty:
        """
        Register intellectual property with comprehensive protection.
        
        Args:
            creator_id: Creator identifier
            title: IP title/name
            description: Detailed description
            right_type: Type of intellectual property right
            content_data: Binary content data for hashing
            protection_level: Level of protection required
            jurisdiction: Legal jurisdiction
            
        Returns:
            Registered intellectual property record
        """
        try:
            # Generate unique IP ID
            ip_id = f"ip_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Registering intellectual property: {ip_id}")
            
            # Generate content hash for uniqueness verification
            content_hash = hashlib.sha256(content_data).hexdigest()
            
            # Check for existing registration
            existing_ip = await self._check_existing_registration(content_hash)
            if existing_ip:
                raise RightsException(f"Content already registered: {existing_ip['ip_id']}")
            
            # Generate proof of creation
            proof_of_creation = await self._generate_proof_of_creation(
                creator_id, title, content_data
            )
            
            # Create IP record
            ip_record = IntellectualProperty(
                ip_id=ip_id,
                creator_id=creator_id,
                title=title,
                description=description,
                right_type=right_type,
                protection_level=protection_level,
                content_hash=content_hash,
                jurisdiction=jurisdiction,
                proof_of_creation=proof_of_creation
            )
            
            # Generate registration number
            ip_record.registration_number = await self._generate_registration_number(
                right_type, jurisdiction
            )
            
            # Set expiry date based on right type
            ip_record.expiry_date = self._calculate_expiry_date(right_type)
            
            # Register on blockchain if enabled
            if self.config.get("blockchain_enabled", False):
                ip_record.blockchain_record = await self._register_on_blockchain(ip_record)
            
            # Store in database
            await self._store_ip_record(ip_record)
            
            # Start monitoring for this IP
            if self.monitoring_enabled:
                await self._start_ip_monitoring(ip_record)
            
            # Generate legal certificates
            await self._generate_ip_certificates(ip_record)
            
            self.logger.info(f"Intellectual property registered successfully: {ip_id}")
            
            return ip_record
            
        except Exception as e:
            self.logger.error(f"IP registration failed: {e}")
            raise RightsException(f"Registration error: {e}")
    
    async def _check_existing_registration(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Check if content is already registered."""
        try:
            query = """
            SELECT ip_id, creator_id, title, registration_date
            FROM intellectual_property 
            WHERE content_hash = $1 AND is_active = true
            LIMIT 1
            """
            
            result = await self.db.fetchrow(query, content_hash)
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Registration check failed: {e}")
            return None
    
    async def _generate_proof_of_creation(
        self,
        creator_id: str,
        title: str,
        content_data: bytes
    ) -> Dict[str, Any]:
        """Generate cryptographic proof of creation."""
        try:
            timestamp = datetime.utcnow()
            
            # Create proof data
            proof_data = {
                "creator_id": creator_id,
                "title": title,
                "timestamp": timestamp.isoformat(),
                "content_size": len(content_data),
                "content_hash": hashlib.sha256(content_data).hexdigest(),
                "metadata_hash": hashlib.md5(f"{creator_id}{title}{timestamp}".encode()).hexdigest()
            }
            
            # Generate digital signature
            proof_signature = jwt.encode(
                proof_data,
                self.config.get("jwt_secret", "default_secret"),
                algorithm="HS256"
            )
            
            # Encrypt sensitive proof data
            encrypted_proof = self.encryption_key.encrypt(
                json.dumps(proof_data).encode()
            )
            
            return {
                "proof_data": proof_data,
                "digital_signature": proof_signature,
                "encrypted_proof": base64.b64encode(encrypted_proof).decode(),
                "verification_method": "JWT+AES256"
            }
            
        except Exception as e:
            self.logger.error(f"Proof generation failed: {e}")
            return {"error": str(e)}
    
    async def _generate_registration_number(
        self,
        right_type: RightType,
        jurisdiction: str
    ) -> str:
        """Generate unique registration number."""
        try:
            # Get current year
            year = datetime.utcnow().year
            
            # Get sequence number for this type and jurisdiction
            sequence_key = f"registration_seq:{right_type.value}:{jurisdiction}:{year}"
            sequence = await self.redis.incr(sequence_key)
            
            # Set expiry for sequence key (1 year)
            await self.redis.expire(sequence_key, 365 * 24 * 3600)
            
            # Generate registration number
            type_code = {
                RightType.COPYRIGHT: "CR",
                RightType.TRADEMARK: "TM", 
                RightType.PATENT: "PT",
                RightType.TRADE_SECRET: "TS",
                RightType.PUBLICITY_RIGHT: "PR",
                RightType.MORAL_RIGHT: "MR",
                RightType.NEIGHBORING_RIGHT: "NR",
                RightType.PERFORMANCE_RIGHT: "PF",
                RightType.MECHANICAL_RIGHT: "MC",
                RightType.SYNCHRONIZATION_RIGHT: "SR"
            }.get(right_type, "XX")
            
            jurisdiction_code = jurisdiction.upper()[:2]
            
            return f"{type_code}{jurisdiction_code}{year}{sequence:06d}"
            
        except Exception as e:
            self.logger.error(f"Registration number generation failed: {e}")
            return f"REG{uuid.uuid4().hex[:8].upper()}"
    
    def _calculate_expiry_date(self, right_type: RightType) -> Optional[datetime]:
        """Calculate expiry date based on right type and jurisdiction."""
        current_date = datetime.utcnow()
        
        # Standard copyright terms (varies by jurisdiction)
        if right_type == RightType.COPYRIGHT:
            return current_date + timedelta(days=365 * 70)  # 70 years
        elif right_type == RightType.TRADEMARK:
            return current_date + timedelta(days=365 * 10)  # 10 years, renewable
        elif right_type == RightType.PATENT:
            return current_date + timedelta(days=365 * 20)  # 20 years
        elif right_type in [RightType.PERFORMANCE_RIGHT, RightType.MECHANICAL_RIGHT]:
            return current_date + timedelta(days=365 * 50)  # 50 years
        else:
            return None  # Perpetual or case-by-case
    
    async def grant_usage_permission(
        self,
        ip_id: str,
        grantee_id: str,
        usage_type: UsageType,
        granted_by: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        revenue_sharing: Optional[Decimal] = None,
        territory_restrictions: List[str] = None,
        usage_conditions: Dict[str, Any] = None
    ) -> UsagePermission:
        """
        Grant usage permission for protected content.
        
        Args:
            ip_id: Intellectual property ID
            grantee_id: User/entity receiving permission
            usage_type: Type of usage being granted
            granted_by: User granting the permission
            start_date: Permission start date
            end_date: Permission expiry date
            revenue_sharing: Revenue sharing percentage
            territory_restrictions: Geographic restrictions
            usage_conditions: Additional usage conditions
            
        Returns:
            Usage permission record
        """
        try:
            # Verify IP ownership
            ip_record = await self._get_ip_record(ip_id)
            if not ip_record:
                raise RightsException(f"IP not found: {ip_id}")
            
            if ip_record["creator_id"] != granted_by:
                raise RightsException("Permission can only be granted by IP owner")
            
            # Generate permission ID
            permission_id = f"perm_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Granting usage permission: {permission_id}")
            
            # Create permission record
            permission = UsagePermission(
                permission_id=permission_id,
                ip_id=ip_id,
                grantee_id=grantee_id,
                usage_type=usage_type,
                granted_by=granted_by,
                start_date=start_date,
                end_date=end_date,
                territory_restrictions=territory_restrictions or [],
                usage_conditions=usage_conditions or {},
                revenue_sharing=revenue_sharing
            )
            
            # Store permission in database
            await self._store_usage_permission(permission)
            
            # Generate usage license document
            await self._generate_usage_license(permission, ip_record)
            
            # Set up revenue tracking if applicable
            if revenue_sharing and revenue_sharing > 0:
                await self._setup_revenue_tracking(permission)
            
            # Notify relevant parties
            await self._notify_permission_granted(permission, ip_record)
            
            self.logger.info(f"Usage permission granted successfully: {permission_id}")
            
            return permission
            
        except Exception as e:
            self.logger.error(f"Permission granting failed: {e}")
            raise RightsException(f"Permission error: {e}")
    
    async def report_infringement(
        self,
        ip_id: str,
        reported_by: str,
        infringing_url: str,
        infringing_party: Optional[str] = None,
        evidence: Dict[str, Any] = None
    ) -> InfringementCase:
        """
        Report copyright infringement case.
        
        Args:
            ip_id: Intellectual property being infringed
            reported_by: User reporting the infringement
            infringing_url: URL where infringement occurs
            infringing_party: Entity committing infringement
            evidence: Evidence of infringement
            
        Returns:
            Infringement case record
        """
        try:
            # Generate case ID
            case_id = f"case_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Reporting infringement case: {case_id}")
            
            # Verify IP ownership
            ip_record = await self._get_ip_record(ip_id)
            if not ip_record:
                raise RightsException(f"IP not found: {ip_id}")
            
            # Analyze similarity if content provided
            similarity_score = 0.0
            if evidence and evidence.get("content_data"):
                similarity_score = await self._analyze_content_similarity(
                    ip_record["content_hash"],
                    evidence["content_data"]
                )
            
            # Create infringement case
            case = InfringementCase(
                case_id=case_id,
                ip_id=ip_id,
                reported_by=reported_by,
                infringing_url=infringing_url,
                infringing_party=infringing_party,
                evidence=evidence or {},
                similarity_score=similarity_score
            )
            
            # Store case in database
            await self._store_infringement_case(case)
            
            # Automatic enforcement if similarity is high
            if similarity_score >= self.similarity_threshold:
                await self._trigger_automatic_enforcement(case, ip_record)
            
            # Notify IP owner
            await self._notify_infringement_reported(case, ip_record)
            
            self.logger.info(f"Infringement case reported successfully: {case_id}")
            
            return case
            
        except Exception as e:
            self.logger.error(f"Infringement reporting failed: {e}")
            raise RightsException(f"Reporting error: {e}")
    
    async def _analyze_content_similarity(
        self,
        original_hash: str,
        suspected_content: bytes
    ) -> float:
        """Analyze similarity between original and suspected infringing content."""
        try:
            # Calculate hash of suspected content
            suspected_hash = hashlib.sha256(suspected_content).hexdigest()
            
            # Exact match
            if original_hash == suspected_hash:
                return 1.0
            
            # For more sophisticated similarity analysis, we would use:
            # - Audio fingerprinting for music
            # - Image similarity algorithms for photos
            # - Text similarity for written content
            # This is a placeholder for the actual implementation
            
            # Simple hash comparison for now
            original_bytes = bytes.fromhex(original_hash)
            suspected_bytes = bytes.fromhex(suspected_hash)
            
            # Calculate Hamming distance
            hamming_distance = sum(a != b for a, b in zip(original_bytes, suspected_bytes))
            max_distance = len(original_bytes)
            
            similarity = 1.0 - (hamming_distance / max_distance)
            
            return similarity
            
        except Exception as e:
            self.logger.error(f"Similarity analysis failed: {e}")
            return 0.0
    
    async def _trigger_automatic_enforcement(
        self,
        case: InfringementCase,
        ip_record: Dict[str, Any]
    ):
        """Trigger automatic enforcement actions for high-confidence infringement."""
        try:
            if not self.auto_takedown_enabled:
                return
            
            self.logger.info(f"Triggering automatic enforcement for case: {case.case_id}")
            
            # Send DMCA takedown notice
            if case.similarity_score >= 0.95:
                await self._send_dmca_takedown(case, ip_record)
                case.enforcement_actions.append("dmca_takedown_sent")
            
            # Issue copyright strike
            elif case.similarity_score >= 0.90:
                await self._issue_copyright_strike(case, ip_record)
                case.enforcement_actions.append("copyright_strike_issued")
            
            # Send cease and desist
            elif case.similarity_score >= self.similarity_threshold:
                await self._send_cease_desist(case, ip_record)
                case.enforcement_actions.append("cease_desist_sent")
            
            # Update case status
            case.case_status = "enforcement_initiated"
            await self._update_infringement_case(case)
            
        except Exception as e:
            self.logger.error(f"Automatic enforcement failed: {e}")
    
    async def track_rights_revenue(
        self,
        ip_id: str,
        revenue_amount: Decimal,
        revenue_source: str,
        usage_permission_id: Optional[str] = None,
        currency: str = "USD",
        territory: str = "global"
    ) -> RightsRevenue:
        """
        Track revenue generated from protected content.
        
        Args:
            ip_id: Intellectual property ID
            revenue_amount: Revenue amount
            revenue_source: Source of revenue
            usage_permission_id: Associated usage permission
            currency: Revenue currency
            territory: Geographic territory
            
        Returns:
            Revenue record
        """
        try:
            # Generate revenue ID
            revenue_id = f"rev_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Tracking rights revenue: {revenue_id}")
            
            # Verify IP exists
            ip_record = await self._get_ip_record(ip_id)
            if not ip_record:
                raise RightsException(f"IP not found: {ip_id}")
            
            # Create revenue record
            revenue = RightsRevenue(
                revenue_id=revenue_id,
                ip_id=ip_id,
                usage_permission_id=usage_permission_id,
                revenue_amount=revenue_amount,
                currency=currency,
                revenue_source=revenue_source,
                territory=territory
            )
            
            # Store revenue record
            await self._store_rights_revenue(revenue)
            
            # Calculate and distribute revenue shares
            if usage_permission_id:
                await self._process_revenue_sharing(revenue, usage_permission_id)
            
            # Update IP statistics
            await self._update_ip_revenue_stats(ip_id, revenue_amount)
            
            # Notify IP owner of revenue
            await self._notify_revenue_tracked(revenue, ip_record)
            
            self.logger.info(f"Rights revenue tracked successfully: {revenue_id}")
            
            return revenue
            
        except Exception as e:
            self.logger.error(f"Revenue tracking failed: {e}")
            raise RightsException(f"Revenue tracking error: {e}")
    
    async def get_rights_analytics(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get comprehensive rights management analytics.
        
        Args:
            creator_id: Creator identifier
            start_date: Analytics period start
            end_date: Analytics period end
            
        Returns:
            Comprehensive analytics data
        """
        try:
            self.logger.info(f"Generating rights analytics for creator: {creator_id}")
            
            analytics = {
                "summary": {
                    "total_ip_registered": 0,
                    "active_permissions": 0,
                    "total_revenue": Decimal("0.00"),
                    "infringement_cases": 0,
                    "enforcement_actions": 0
                },
                "ip_portfolio": {},
                "revenue_analysis": {},
                "infringement_analysis": {},
                "protection_effectiveness": {},
                "recommendations": []
            }
            
            # Get IP portfolio summary
            ip_query = """
            SELECT 
                right_type,
                protection_level,
                COUNT(*) as count,
                AVG(EXTRACT(days FROM age(NOW(), registration_date))) as avg_age_days
            FROM intellectual_property 
            WHERE creator_id = $1 
                AND is_active = true
                AND registration_date BETWEEN $2 AND $3
            GROUP BY right_type, protection_level
            ORDER BY count DESC
            """
            
            ip_results = await self.db.fetch(ip_query, creator_id, start_date, end_date)
            
            for row in ip_results:
                analytics["summary"]["total_ip_registered"] += row["count"]
                
                right_type = row["right_type"]
                if right_type not in analytics["ip_portfolio"]:
                    analytics["ip_portfolio"][right_type] = {
                        "total_count": 0,
                        "protection_levels": {},
                        "average_age_days": 0
                    }
                
                analytics["ip_portfolio"][right_type]["total_count"] += row["count"]
                analytics["ip_portfolio"][right_type]["protection_levels"][row["protection_level"]] = row["count"]
                analytics["ip_portfolio"][right_type]["average_age_days"] = float(row["avg_age_days"])
            
            # Get revenue analytics
            revenue_query = """
            SELECT 
                ip.right_type,
                rr.currency,
                SUM(rr.revenue_amount) as total_revenue,
                COUNT(rr.revenue_id) as revenue_events,
                AVG(rr.revenue_amount) as avg_revenue
            FROM rights_revenue rr
            JOIN intellectual_property ip ON rr.ip_id = ip.ip_id
            WHERE ip.creator_id = $1 
                AND rr.collection_date BETWEEN $2 AND $3
            GROUP BY ip.right_type, rr.currency
            ORDER BY total_revenue DESC
            """
            
            revenue_results = await self.db.fetch(revenue_query, creator_id, start_date, end_date)
            
            for row in revenue_results:
                right_type = row["right_type"]
                analytics["summary"]["total_revenue"] += row["total_revenue"]
                
                if right_type not in analytics["revenue_analysis"]:
                    analytics["revenue_analysis"][right_type] = {
                        "total_revenue": Decimal("0.00"),
                        "revenue_events": 0,
                        "currencies": {},
                        "average_revenue": Decimal("0.00")
                    }
                
                analytics["revenue_analysis"][right_type]["total_revenue"] += row["total_revenue"]
                analytics["revenue_analysis"][right_type]["revenue_events"] += row["revenue_events"]
                analytics["revenue_analysis"][right_type]["currencies"][row["currency"]] = float(row["total_revenue"])
                analytics["revenue_analysis"][right_type]["average_revenue"] = row["avg_revenue"]
            
            # Get infringement analytics
            infringement_query = """
            SELECT 
                ic.infringement_type,
                ic.case_status,
                COUNT(*) as case_count,
                AVG(ic.similarity_score) as avg_similarity,
                COUNT(CASE WHEN array_length(ic.enforcement_actions, 1) > 0 THEN 1 END) as enforced_cases
            FROM infringement_cases ic
            JOIN intellectual_property ip ON ic.ip_id = ip.ip_id
            WHERE ip.creator_id = $1 
                AND ic.created_at BETWEEN $2 AND $3
            GROUP BY ic.infringement_type, ic.case_status
            ORDER BY case_count DESC
            """
            
            infringement_results = await self.db.fetch(infringement_query, creator_id, start_date, end_date)
            
            for row in infringement_results:
                analytics["summary"]["infringement_cases"] += row["case_count"]
                analytics["summary"]["enforcement_actions"] += row["enforced_cases"]
                
                infringement_type = row["infringement_type"]
                if infringement_type not in analytics["infringement_analysis"]:
                    analytics["infringement_analysis"][infringement_type] = {
                        "total_cases": 0,
                        "case_statuses": {},
                        "average_similarity": 0.0,
                        "enforcement_rate": 0.0
                    }
                
                analytics["infringement_analysis"][infringement_type]["total_cases"] += row["case_count"]
                analytics["infringement_analysis"][infringement_type]["case_statuses"][row["case_status"]] = row["case_count"]
                analytics["infringement_analysis"][infringement_type]["average_similarity"] = float(row["avg_similarity"])
                
                if row["case_count"] > 0:
                    enforcement_rate = row["enforced_cases"] / row["case_count"]
                    analytics["infringement_analysis"][infringement_type]["enforcement_rate"] = enforcement_rate
            
            # Calculate protection effectiveness
            if analytics["summary"]["infringement_cases"] > 0:
                effectiveness_rate = analytics["summary"]["enforcement_actions"] / analytics["summary"]["infringement_cases"]
                analytics["protection_effectiveness"]["enforcement_rate"] = effectiveness_rate
                analytics["protection_effectiveness"]["avg_response_time_days"] = await self._calculate_avg_response_time(creator_id, start_date, end_date)
            
            # Generate recommendations
            analytics["recommendations"] = await self._generate_rights_recommendations(analytics)
            
            self.logger.info(f"Rights analytics generated successfully for creator: {creator_id}")
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Rights analytics generation failed: {e}")
            raise RightsException(f"Analytics error: {e}")
    
    async def cleanup_resources(self):
        """Clean up rights manager resources."""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            self.logger.info("Rights manager resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Resource cleanup failed: {e}")


# Factory function for easy instantiation
def create_rights_manager(config: Optional[Dict[str, Any]] = None) -> EnterpriseRightsManager:
    """Create and return configured rights manager instance."""
    return EnterpriseRightsManager(config)
