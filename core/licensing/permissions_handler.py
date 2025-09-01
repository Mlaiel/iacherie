"""Ultra-Advanced Permissions Handler - Enterprise Access Control & Usage Rights Administration Engine
===================================================================================================

Advanced permissions management system providing fine-grained access control,
AI-powered usage rights validation, blockchain-secured authorization, role-based
access control, and comprehensive audit trails for all licensing and content operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE & COPYRIGHT PROTECTION:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in severe legal consequences.
Contact: mlaiel@live.de for licensing and usage rights.

Business Logic Flow:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format content
→ AI protection rights analysis → Professional SEO optimization → Collaboration matching
→ Multi-platform distribution → Automated licensing & royalty management
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import hashlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.exceptions import PermissionError, ValidationError, AuthorizationError, SecurityError
from ..utils.monitoring import PermissionMetrics, MetricsCollector
from ..utils.security import SecurityManager
from ..utils.blockchain import BlockchainVerifier
from ..utils.ai_optimization import AIOptimizationEngine
from ..security.access_control import AccessController


class PermissionType(Enum):
    """
Comprehensive permission types"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MODIFY = "modify"
    SHARE = "share"
    DISTRIBUTE = "distribute"
    MONETIZE = "monetize"
    COLLABORATE = "collaborate"
    ADMIN = "admin"
    OWNER = "owner"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_RIGHTS = "manage_rights"
    APPROVE_CONTRACTS = "approve_contracts"
    MANAGE_ROYALTIES = "manage_royalties"
    EXPORT_DATA = "export_data"
    GRANT_PERMISSIONS = "grant_permissions"
    REVOKE_PERMISSIONS = "revoke_permissions"
    AUDIT_ACCESS = "audit_access"


class AccessLevel(Enum):
    """Access levels for permissions"""

    NONE = "none"
    LIMITED = "limited"
    STANDARD = "standard"
    EXTENDED = "extended"
    FULL = "full"
    UNRESTRICTED = "unrestricted"


class UsageRight(Enum):
    """Specific usage rights"""

    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL_REPRODUCTION = "mechanical_reproduction"
    DIGITAL_DISTRIBUTION = "digital_distribution"
    PHYSICAL_DISTRIBUTION = "physical_distribution"
    REMIX = "remix"
    SAMPLING = "sampling"
    COVER_VERSION = "cover_version"
    DERIVATIVE_WORK = "derivative_work"
    COMMERCIAL_USE = "commercial_use"
    NON_COMMERCIAL_USE = "non_commercial_use"
    EDUCATIONAL_USE = "educational_use"
    PROMOTIONAL_USE = "promotional_use"


class RestrictionType(Enum):
    """Types of usage restrictions"""

    TERRITORY = "territory"
    TIME_LIMIT = "time_limit"
    PLATFORM = "platform"
    AUDIENCE = "audience"
    QUALITY = "quality"
    FREQUENCY = "frequency"
    VOLUME = "volume"
    REVENUE_THRESHOLD = "revenue_threshold"
    EXCLUSIVITY = "exclusivity"
    ATTRIBUTION = "attribution"
    METADATA = "metadata"
    WATERMARK = "watermark"


class PermissionScope(Enum):
    """Scope of permissions"""

    GLOBAL = "global"
    REGIONAL = "regional"
    TERRITORIAL = "territorial"
    PLATFORM_SPECIFIC = "platform_specific"
    CONTENT_SPECIFIC = "content_specific"
    USER_SPECIFIC = "user_specific"
    ROLE_SPECIFIC = "role_specific"
    TIME_BOUND = "time_bound"
    CONDITIONAL = "conditional"


@dataclass
class EnhancedPermission:
    """Enhanced permission data structure"""
    permission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Permission details
    permission_type: PermissionType = PermissionType.READ
    access_level: AccessLevel = AccessLevel.STANDARD
    usage_rights: List[UsageRight] = field(default_factory=list)
    restrictions: List[RestrictionType] = field(default_factory=list)
    scope: PermissionScope = PermissionScope.CONTENT_SPECIFIC
    
    # Subject and object
    subject_id: str = ""  # User, role, or entity being granted permission
    subject_type: str = "user"  # user, role, group, system
    object_id: str = ""  # Resource being accessed
    object_type: str = "content"  # content, license, agreement, etc.
    
    # Conditions and constraints
    territorial_restrictions: List[str] = field(default_factory=list)
    platform_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, datetime] = field(default_factory=dict)
    usage_limits: Dict[str, Any] = field(default_factory=dict)
    
    # Business rules
    revenue_sharing_required: bool = False
    attribution_required: bool = True
    watermark_required: bool = False
    metadata_preservation_required: bool = True
    
    # Status and validity
    active: bool = True
    granted_at: datetime = field(default_factory=datetime.utcnow)
    granted_by: str = ""
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    
    # Approval workflow
    requires_approval: bool = False
    approved: bool = False
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approval_notes: str = ""
    
    # Security and verification
    blockchain_verified: bool = False
    blockchain_hash: Optional[str] = None
    security_level: str = "standard"
    encryption_required: bool = False
    
    # Audit trail
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    access_logs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PermissionRequest:
    """Permission request data structure"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Request details
    requested_permission_type: PermissionType = PermissionType.READ
    requested_access_level: AccessLevel = AccessLevel.STANDARD
    requested_usage_rights: List[UsageRight] = field(default_factory=list)
    
    # Requesting party
    requester_id: str = ""
    requester_type: str = "user"
    requester_role: str = ""
    
    # Target resource
    target_object_id: str = ""
    target_object_type: str = "content"
    
    # Justification
    business_justification: str = ""
    intended_use: str = ""
    duration_requested: Optional[timedelta] = None
    territory_requested: List[str] = field(default_factory=list)
    
    # Request metadata
    priority: str = "standard"
    urgency: str = "normal"
    request_date: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    
    # Supporting information
    supporting_documents: List[str] = field(default_factory=list)
    legal_basis: str = ""
    commercial_terms: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: str = "pending"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    decision: Optional[str] = None
    decision_notes: str = ""


@dataclass
class PermissionGrant:
    """Permission grant result"""
    grant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    
    # Grant details
    granted_permission: Optional[EnhancedPermission] = None
    granted: bool = False
    grant_type: str = "standard"  # standard, conditional, temporary
    
    # Conditions and modifications
    conditions: List[str] = field(default_factory=list)
    modifications_from_request: List[str] = field(default_factory=list)
    additional_restrictions: List[str] = field(default_factory=list)
    
    # Authority
    granted_by: str = ""
    authority_level: str = ""
    delegation_allowed: bool = False
    
    # Validity
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    renewable: bool = True
    auto_renewal: bool = False
    
    # Compliance
    compliance_requirements: List[str] = field(default_factory=list)
    monitoring_required: bool = True
    reporting_required: bool = False
    
    # Documentation
    grant_document: Optional[str] = None
    legal_agreement: Optional[str] = None
    
    # Metadata
    grant_notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


class UltraAdvancedPermissionsHandler:
    """
    Ultra-advanced permissions management engine with comprehensive access control,
    AI-powered authorization decisions, blockchain verification, and global compliance
    """
    
    def __init__(
        self,
        security_manager: SecurityManager,
        blockchain_verifier: BlockchainVerifier,
        ai_optimizer: AIOptimizationEngine,
        access_controller: AccessController,
        redis_client: Optional[aioredis.Redis] = None
    ):
        self.security_manager = security_manager
        self.blockchain_verifier = blockchain_verifier
        self.ai_optimizer = ai_optimizer
        self.access_controller = access_controller
        self.redis_client = redis_client
        self.metrics_collector = MetricsCollector("permissions_handler")
        self.logger = logging.getLogger(__name__)
        
        # Permission cache
        self._permission_cache = {}
        self._access_cache = {}
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.max_permissions_per_user = 1000
        self.permission_expiry_days = 365
        
        # Business logic validation
        self._validate_business_logic()
    
    def _validate_business_logic(self) -> None:
        """Validate business logic flow requirements"""
        required_components = [
            self.security_manager,
            self.blockchain_verifier,
            self.ai_optimizer,
            self.access_controller
        ]
        
        if not all(required_components):
            raise PermissionError("Missing required components for business logic flow")
        
        self.logger.info("Permissions handler business logic validated successfully")
    
    async def request_permission(
        self,
        request: PermissionRequest,
        session: Optional[AsyncSession] = None
    ) -> PermissionGrant:
        """
        Process permission request with AI-powered decision making and compliance validation
        """
        try:
            # Validate request
            await self._validate_permission_request(request)
            
            # Security validation
            await self.security_manager.validate_permission_operation(
                request.requester_id,
                request.target_object_id,
                "request_permission"
            )
            
            # Check existing permissions
            existing_permissions = await self.get_user_permissions(
                request.requester_id,
                request.target_object_id,
                session
            )
            
            # AI-powered decision making
            ai_recommendation = await self.ai_optimizer.analyze_permission_request(
                request, existing_permissions
            )
            
            # Authority validation
            authority_check = await self._validate_grant_authority(
                request.requester_id,
                request.requested_permission_type,
                request.target_object_id
            )
            
            # Initialize grant result
            grant = PermissionGrant(
                request_id=request.request_id,
                granted_by="ultra_advanced_permissions_handler"
            )
            
            # Determine if permission should be granted
            should_grant = await self._should_grant_permission(
                request, ai_recommendation, authority_check, existing_permissions
            )
            
            if should_grant:
                # Create permission
                permission = await self._create_permission_from_request(request, ai_recommendation)
                
                # Apply AI recommendations and restrictions
                permission = await self._apply_ai_restrictions(permission, ai_recommendation)
                
                # Blockchain verification for high-value permissions
                if self._requires_blockchain_verification(permission):
                    blockchain_result = await self.blockchain_verifier.verify_permission_grant(permission)
                    permission.blockchain_verified = blockchain_result.get("verified", False)
                    permission.blockchain_hash = blockchain_result.get("hash")
                
                # Store permission
                await self._store_permission(permission, session)
                
                # Update grant
                grant.granted = True
                grant.granted_permission = permission
                grant.grant_type = ai_recommendation.get("grant_type", "standard")
                grant.conditions = ai_recommendation.get("conditions", [])
                
                # Set expiry based on AI recommendation
                if ai_recommendation.get("suggested_duration"):
                    grant.expiry_date = datetime.utcnow() + ai_recommendation["suggested_duration"]
                
            else:
                # Permission denied
                grant.granted = False
                grant.grant_notes = ai_recommendation.get("denial_reason", "Permission denied")
                grant.conditions = ai_recommendation.get("requirements_for_approval", [])
            
            # Record metrics
            await self.metrics_collector.record_metric(
                "permission_request_processed",
                {
                    "requester_id": request.requester_id,
                    "permission_type": request.requested_permission_type.value,
                    "granted": grant.granted,
                    "object_type": request.target_object_type
                }
            )
            
            return grant
            
        except Exception as e:
            self.logger.error(f"Permission request processing failed: {str(e)}")
            await self.metrics_collector.record_error("permission_request_error", str(e))
            
            # Return denial grant
            error_grant = PermissionGrant(
                request_id=request.request_id,
                granted=False,
                grant_notes=f"Processing error: {str(e)}",
                granted_by="ultra_advanced_permissions_handler"
            )
            return error_grant
    
    async def check_permission(
        self,
        subject_id: str,
        object_id: str,
        permission_type: PermissionType,
        usage_context: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """
        Check if subject has specific permission for object with context validation
        """
        try:
            # Check cache first
            cache_key = f"permission_check:{subject_id}:{object_id}:{permission_type.value}"
            cached_result = await self._get_cached_permission_check(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Security validation
            await self.security_manager.validate_permission_operation(
                subject_id, object_id, "check_permission"
            )
            
            # Get user permissions
            permissions = await self.get_user_permissions(subject_id, object_id, session)
            
            # Check if any permission grants the requested access
            for permission in permissions:
                if await self._permission_grants_access(
                    permission, permission_type, usage_context
                ):
                    # Update usage tracking
                    await self._track_permission_usage(permission, usage_context)
                    
                    # Cache positive result
                    await self._cache_permission_check(cache_key, True)
                    return True
            
            # Cache negative result
            await self._cache_permission_check(cache_key, False)
            return False
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {str(e)}")
            await self.metrics_collector.record_error("permission_check_error", str(e))
            return False
    
    async def get_user_permissions(
        self,
        user_id: str,
        object_id: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> List[EnhancedPermission]:
        """
        Get all permissions for a user, optionally filtered by object
        """
        try:
            # Check cache first
            cache_key = f"user_permissions:{user_id}:{object_id or 'all'}"
            cached_permissions = await self._get_cached_user_permissions(cache_key)
            if cached_permissions:
                return cached_permissions
            
            # Security validation
            await self.security_manager.validate_permission_operation(
                user_id, object_id or "system", "get_permissions"
            )
            
            # Query permissions from database
            permissions = await self._query_user_permissions(user_id, object_id, session)
            
            # Filter active and non-expired permissions
            active_permissions = []
            current_time = datetime.utcnow()
            
            for permission in permissions:
                if (permission.active and 
                    (not permission.expires_at or permission.expires_at > current_time)):
                    active_permissions.append(permission)
            
            # Cache results
            await self._cache_user_permissions(cache_key, active_permissions)
            
            return active_permissions
            
        except Exception as e:
            self.logger.error(f"Get user permissions failed: {str(e)}")
            await self.metrics_collector.record_error("get_permissions_error", str(e))
            return []
    
    async def grant_permission(
        self,
        subject_id: str,
        object_id: str,
        permission_type: PermissionType,
        access_level: AccessLevel = AccessLevel.STANDARD,
        usage_rights: Optional[List[UsageRight]] = None,
        restrictions: Optional[List[RestrictionType]] = None,
        granted_by: str = "",
        expires_at: Optional[datetime] = None,
        session: Optional[AsyncSession] = None
    ) -> EnhancedPermission:
        """
        Grant permission directly (for administrative use)
        """
        try:
            # Security validation - check if granter has authority
            await self.security_manager.validate_permission_operation(
                granted_by, object_id, "grant_permission"
            )
            
            # Create permission
            permission = EnhancedPermission(
                permission_type=permission_type,
                access_level=access_level,
                usage_rights=usage_rights or [],
                restrictions=restrictions or [],
                subject_id=subject_id,
                object_id=object_id,
                granted_by=granted_by,
                expires_at=expires_at or (datetime.utcnow() + timedelta(days=self.permission_expiry_days)),
                approved=True,
                approved_at=datetime.utcnow(),
                approved_by=granted_by
            )
            
            # AI optimization for permission parameters
            ai_optimization = await self.ai_optimizer.optimize_permission_grant(permission)
            if ai_optimization:
                permission.usage_limits = ai_optimization.get("usage_limits", {})
                permission.security_level = ai_optimization.get("security_level", "standard")
                permission.metadata.update(ai_optimization.get("metadata", {}))
            
            # Blockchain verification for high-value permissions
            if self._requires_blockchain_verification(permission):
                blockchain_result = await self.blockchain_verifier.verify_permission_grant(permission)
                permission.blockchain_verified = blockchain_result.get("verified", False)
                permission.blockchain_hash = blockchain_result.get("hash")
            
            # Store permission
            await self._store_permission(permission, session)
            
            # Clear relevant caches
            await self._clear_permission_caches(subject_id, object_id)
            
            # Record audit trail
            await self._record_permission_audit(
                permission, "granted", f"Permission granted by {granted_by}"
            )
            
            # Record metrics
            await self.metrics_collector.record_metric(
                "permission_granted",
                {
                    "subject_id": subject_id,
                    "object_id": object_id,
                    "permission_type": permission_type.value,
                    "access_level": access_level.value,
                    "granted_by": granted_by
                }
            )
            
            return permission
            
        except Exception as e:
            self.logger.error(f"Grant permission failed: {str(e)}")
            await self.metrics_collector.record_error("grant_permission_error", str(e))
            raise PermissionError(f"Failed to grant permission: {str(e)}")
    
    async def revoke_permission(
        self,
        permission_id: str,
        revoked_by: str,
        reason: str = "",
        session: Optional[AsyncSession] = None
    ) -> bool:
        """
        Revoke an existing permission
        """
        try:
            # Get permission
            permission = await self._get_permission_by_id(permission_id, session)
            if not permission:
                raise PermissionError("Permission not found")
            
            # Security validation
            await self.security_manager.validate_permission_operation(
                revoked_by, permission.object_id, "revoke_permission"
            )
            
            # Check if user has authority to revoke
            can_revoke = await self._can_revoke_permission(permission, revoked_by)
            if not can_revoke:
                raise AuthorizationError("Insufficient authority to revoke permission")
            
            # Deactivate permission
            permission.active = False
            permission.updated_at = datetime.utcnow()
            
            # Update in database
            await self._update_permission(permission, session)
            
            # Clear caches
            await self._clear_permission_caches(permission.subject_id, permission.object_id)
            
            # Record audit trail
            await self._record_permission_audit(
                permission, "revoked", f"Permission revoked by {revoked_by}. Reason: {reason}"
            )
            
            # Blockchain record for high-value permissions
            if permission.blockchain_verified:
                await self.blockchain_verifier.record_permission_revocation(
                    permission, revoked_by, reason
                )
            
            # Record metrics
            await self.metrics_collector.record_metric(
                "permission_revoked",
                {
                    "permission_id": permission_id,
                    "subject_id": permission.subject_id,
                    "object_id": permission.object_id,
                    "revoked_by": revoked_by,
                    "reason": reason
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Revoke permission failed: {str(e)}")
            await self.metrics_collector.record_error("revoke_permission_error", str(e))
            return False
    
    async def _validate_permission_request(self, request: PermissionRequest) -> None:
        """Validate permission request"""
        if not request.requester_id:
            raise ValidationError("Requester ID is required")
        
        if not request.target_object_id:
            raise ValidationError("Target object ID is required")
        
        if not request.business_justification:
            raise ValidationError("Business justification is required")
        
        # Validate usage rights consistency
        if (PermissionType.MONETIZE in [request.requested_permission_type] and
            not any(right in request.requested_usage_rights for right in [
                UsageRight.COMMERCIAL_USE, UsageRight.STREAMING, UsageRight.DISTRIBUTION
            ])):
            raise ValidationError("Monetize permission requires commercial usage rights")
    
    async def _should_grant_permission(
        self,
        request: PermissionRequest,
        ai_recommendation: Dict[str, Any],
        authority_check: Dict[str, Any],
        existing_permissions: List[EnhancedPermission]
    ) -> bool:
        """Determine if permission should be granted"""
        
        # Check AI recommendation
        ai_approval = ai_recommendation.get("recommend_approval", False)
        ai_risk_score = ai_recommendation.get("risk_score", 0.5)
        
        # Check authority
        has_authority = authority_check.get("has_authority", False)
        
        # Check for conflicts with existing permissions
        has_conflicts = await self._check_permission_conflicts(request, existing_permissions)
        
        # Business rules
        meets_business_rules = await self._check_business_rules(request)
        
        # Final decision logic
        should_grant = (
            ai_approval and
            has_authority and
            not has_conflicts and
            meets_business_rules and
            ai_risk_score < 0.7  # Risk threshold
        )
        
        return should_grant
    
    async def _permission_grants_access(
        self,
        permission: EnhancedPermission,
        requested_type: PermissionType,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if permission grants access for requested type and context"""
        
        # Check permission type hierarchy
        if not self._permission_type_allows(permission.permission_type, requested_type):
            return False
        
        # Check context restrictions
        if context:
            # Territory restrictions
            if (context.get("territory") and 
                permission.territorial_restrictions and
                context["territory"] not in permission.territorial_restrictions):
                return False
            
            # Platform restrictions
            if (context.get("platform") and
                permission.platform_restrictions and
                context["platform"] not in permission.platform_restrictions):
                return False
            
            # Time restrictions
            current_time = datetime.utcnow()
            if permission.time_restrictions:
                start_time = permission.time_restrictions.get("start")
                end_time = permission.time_restrictions.get("end")
                
                if start_time and current_time < start_time:
                    return False
                if end_time and current_time > end_time:
                    return False
            
            # Usage limits
            if permission.usage_limits:
                max_uses = permission.usage_limits.get("max_uses")
                if max_uses and permission.usage_count >= max_uses:
                    return False
        
        return True
    
    def _permission_type_allows(
        self,
        granted_type: PermissionType,
        requested_type: PermissionType
    ) -> bool:
        """Check if granted permission type allows requested type"""
        
        # Permission hierarchy
        hierarchy = {
            PermissionType.OWNER: [  # Owner can do everything
                PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE,
                PermissionType.MODIFY, PermissionType.SHARE, PermissionType.DISTRIBUTE,
                PermissionType.MONETIZE, PermissionType.COLLABORATE, PermissionType.ADMIN,
                PermissionType.VIEW_ANALYTICS, PermissionType.MANAGE_RIGHTS,
                PermissionType.APPROVE_CONTRACTS, PermissionType.MANAGE_ROYALTIES,
                PermissionType.EXPORT_DATA, PermissionType.GRANT_PERMISSIONS,
                PermissionType.REVOKE_PERMISSIONS, PermissionType.AUDIT_ACCESS
            ],
            PermissionType.ADMIN: [  # Admin has broad access
                PermissionType.READ, PermissionType.WRITE, PermissionType.MODIFY,
                PermissionType.SHARE, PermissionType.VIEW_ANALYTICS,
                PermissionType.MANAGE_RIGHTS, PermissionType.APPROVE_CONTRACTS,
                PermissionType.MANAGE_ROYALTIES, PermissionType.EXPORT_DATA
            ],
            PermissionType.WRITE: [  # Write includes read
                PermissionType.READ, PermissionType.MODIFY
            ],
            PermissionType.SHARE: [  # Share includes read
                PermissionType.READ
            ],
            PermissionType.DISTRIBUTE: [  # Distribute includes read and share
                PermissionType.READ, PermissionType.SHARE
            ],
            PermissionType.MONETIZE: [  # Monetize includes read, share, and distribute
                PermissionType.READ, PermissionType.SHARE, PermissionType.DISTRIBUTE
            ]
        }
        
        # Check if granted type allows requested type
        allowed_types = hierarchy.get(granted_type, [granted_type])
        return requested_type in allowed_types
    
    def _requires_blockchain_verification(self, permission: EnhancedPermission) -> bool:
        """
Determine if permission requires blockchain verification"""
        high_value_types = [
            PermissionType.OWNER,
            PermissionType.MONETIZE,
            PermissionType.DISTRIBUTE,
            PermissionType.MANAGE_RIGHTS,
            PermissionType.MANAGE_ROYALTIES
        ]
        
        return (
            permission.permission_type in high_value_types or
            permission.access_level in [AccessLevel.FULL, AccessLevel.UNRESTRICTED] or
            UsageRight.COMMERCIAL_USE in permission.usage_rights
        )
    
    async def _cache_permission_check(self, cache_key: str, result: bool) -> None:
        """
Cache permission check result"""
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    300,  # 5 minutes for permission checks
                    "1" if result else "0"
                )
            except Exception as e:
                self.logger.warning(f"Failed to cache permission check: {str(e)}")
    
    async def _get_cached_permission_check(self, cache_key: str) -> Optional[bool]:
        """Get cached permission check result"""
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return cached.decode() == "1"
            except Exception as e:
                self.logger.warning(f"Failed to get cached permission check: {str(e)}")
        return None


class ActionType(Enum):
    """Types of actions that can be performed"""

    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"
    CREATE = "create"
    SHARE = "share"
    PUBLISH = "publish"
    DOWNLOAD = "download"
    STREAM = "stream"
    BROADCAST = "broadcast"
    SYNC = "sync"
    MONETIZE = "monetize"
    DISTRIBUTE = "distribute"
    ANALYZE = "analyze"
    EXPORT = "export"
    IMPORT = "import"


class UsageRight(Enum):
    """Specific usage rights for content"""

    MECHANICAL_REPRODUCTION = "mechanical_reproduction"
    PUBLIC_PERFORMANCE = "public_performance"
    SYNCHRONIZATION = "synchronization"
    DIGITAL_TRANSMISSION = "digital_transmission"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    SUBLICENSE = "sublicense"
    DERIVATIVE_WORKS = "derivative_works"
    COMMERCIAL_USE = "commercial_use"
    EDUCATIONAL_USE = "educational_use"
    PERSONAL_USE = "personal_use"


@dataclass
class Permission:
    """Individual permission entry"""
    permission_id: str
    resource_type: ResourceType
    resource_id: str
    subject_id: str  # User, role, or group ID
    subject_type: str  # "user", "role", "group"
    permission_level: PermissionLevel
    allowed_actions: Set[ActionType]
    usage_rights: Set[UsageRight]
    granted_at: datetime
    granted_by: str
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class AccessRequest:
    """Access request for validation"""
    request_id: str
    subject_id: str
    subject_type: str
    resource_type: ResourceType
    resource_id: str
    action: ActionType
    usage_right: Optional[UsageRight]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PermissionGrant:
    """
Permission grant result"""
    granted: bool
    permission_id: Optional[str]
    access_level: PermissionLevel
    allowed_actions: Set[ActionType]
    usage_rights: Set[UsageRight]
    conditions: Dict[str, Any]
    expires_at: Optional[datetime]
    reason: str


@dataclass
class Role:
    """
User role definition"""
    role_id: str
    role_name: str
    description: str
    permissions: Set[str]  # Permission IDs
    default_permission_level: PermissionLevel
    created_at: datetime
    created_by: str
    is_system_role: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PermissionPolicy:
    """
Permission policy definition"""
    policy_id: str
    policy_name: str
    resource_type: ResourceType
    default_permissions: Dict[str, PermissionLevel]
    inheritance_rules: Dict[str, Any]
    restriction_rules: Dict[str, Any]
    approval_workflow: Optional[str]
    created_at: datetime
    created_by: str
    is_active: bool = True


class PermissionsHandler:
    """
    Granular access control and usage rights administration system
    
    Features:
    - Role-based access control (RBAC)
    - Attribute-based access control (ABAC)
    - Fine-grained permission management
    - Usage rights validation and enforcement
    - Hierarchical permission inheritance
    - Time-based and conditional permissions
    - Comprehensive audit trails
    - Policy-driven authorization
    - Multi-tenant permission isolation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.access_controller = AccessController()
        self.permission_metrics = PermissionMetrics()
        
        # Permission data storage
        self.permissions = {}  # permission_id -> Permission
        self.roles = {}  # role_id -> Role
        self.policies = {}  # policy_id -> PermissionPolicy
        self.user_roles = defaultdict(set)  # user_id -> set of role_ids
        self.resource_permissions = defaultdict(list)  # resource_id -> list of permission_ids
        
        # Audit and monitoring
        self.access_log = []
        self.permission_changes = []
        
        # Configuration
        self.enable_inheritance = self.config.get('enable_inheritance', True)
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes
        self.audit_all_access = self.config.get('audit_all_access', True)
        
        # Permission cache
        self.permission_cache = {}
        self.cache_timestamps = {}
        
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """
Initialize permissions handler and security systems"""
        try:
            self.logger.info("Initializing PermissionsHandler")
            
            # Initialize components
            await asyncio.gather(
                self.access_controller.initialize(),
                self.permission_metrics.initialize()
            )
            
            # Create default roles
            await self._create_default_roles()
            
            # Create default policies
            await self._create_default_policies()
            
            self.is_initialized = True
            self.logger.info("PermissionsHandler initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PermissionsHandler: {str(e)}")
            raise PermissionError(f"Initialization failed: {str(e)}")
    
    async def grant_permission(
        self,
        resource_type: ResourceType,
        resource_id: str,
        subject_id: str,
        subject_type: str,
        permission_level: PermissionLevel,
        granted_by: str,
        allowed_actions: Optional[Set[ActionType]] = None,
        usage_rights: Optional[Set[UsageRight]] = None,
        expires_at: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Grant permission to a subject for a specific resource
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            subject_id: Subject (user/role/group) identifier
            subject_type: Type of subject ("user", "role", "group")
            permission_level: Level of permission
            granted_by: ID of user granting permission
            allowed_actions: Specific actions allowed
            usage_rights: Specific usage rights granted
            expires_at: Optional expiration time
            conditions: Additional conditions for permission
            
        Returns:
            Permission ID
        """
        if not self.is_initialized:
            raise PermissionError("PermissionsHandler not initialized")
        
        permission_id = str(uuid.uuid4())
        
        try:
            # Validate granting authority
            await self._validate_granting_authority(
                granted_by=granted_by,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_level=permission_level
            )
            
            # Apply policy-based defaults if not specified
            if allowed_actions is None:
                allowed_actions = await self._get_default_actions(permission_level, resource_type)
            
            if usage_rights is None:
                usage_rights = await self._get_default_usage_rights(permission_level, resource_type)
            
            # Create permission
            permission = Permission(
                permission_id=permission_id,
                resource_type=resource_type,
                resource_id=resource_id,
                subject_id=subject_id,
                subject_type=subject_type,
                permission_level=permission_level,
                allowed_actions=allowed_actions,
                usage_rights=usage_rights,
                granted_at=datetime.now(),
                granted_by=granted_by,
                expires_at=expires_at,
                conditions=conditions or {},
                is_active=True
            )
            
            # Store permission
            self.permissions[permission_id] = permission
            self.resource_permissions[resource_id].append(permission_id)
            
            # Clear cache for affected resources
            await self._clear_permission_cache(subject_id, resource_id)
            
            # Log permission grant
            await self._log_permission_change(
                action="grant",
                permission=permission,
                changed_by=granted_by
            )
            
            # Record metrics
            await self.permission_metrics.record_permission_grant(
                resource_type=resource_type.value,
                permission_level=permission_level.value,
                granted_by=granted_by
            )
            
            self.logger.info(f"Permission granted: {permission_id}")
            return permission_id
            
        except Exception as e:
            self.logger.error(f"Failed to grant permission: {str(e)}")
            raise PermissionError(f"Permission grant failed: {str(e)}")
    
    async def check_permission(
        self,
        subject_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType,
        usage_right: Optional[UsageRight] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PermissionGrant:
        """
        Check if a subject has permission to perform an action
        
        Args:
            subject_id: Subject identifier
            resource_type: Type of resource
            resource_id: Resource identifier
            action: Action to perform
            usage_right: Specific usage right to check
            context: Additional context for permission evaluation
            
        Returns:
            Permission grant result
        """
        if not self.is_initialized:
            raise PermissionError("PermissionsHandler not initialized")
        
        try:
            # Create access request
            request = AccessRequest(
                request_id=str(uuid.uuid4()),
                subject_id=subject_id,
                subject_type="user",
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                usage_right=usage_right,
                context=context or {}
            )
            
            # Check cache first
            if self.enable_caching:
                cached_result = await self._get_cached_permission(request)
                if cached_result:
                    return cached_result
            
            # Evaluate permission
            grant = await self._evaluate_permission(request)
            
            # Cache result
            if self.enable_caching:
                await self._cache_permission_result(request, grant)
            
            # Log access attempt
            if self.audit_all_access:
                await self._log_access_attempt(request, grant)
            
            # Record metrics
            await self.permission_metrics.record_access_check(
                resource_type=resource_type.value,
                action=action.value,
                granted=grant.granted,
                subject_id=subject_id
            )
            
            return grant
            
        except Exception as e:
            self.logger.error(f"Failed to check permission: {str(e)}")
            raise PermissionError(f"Permission check failed: {str(e)}")
    
    async def revoke_permission(
        self,
        permission_id: str,
        revoked_by: str,
        reason: str = ""
    ) -> None:
        """
        Revoke a specific permission
        
        Args:
            permission_id: Permission identifier
            revoked_by: ID of user revoking permission
            reason: Reason for revocation
        """
        if not self.is_initialized:
            raise PermissionError("PermissionsHandler not initialized")
        
        try:
            permission = self.permissions.get(permission_id)
            if not permission:
                raise ValidationError(f"Permission not found: {permission_id}")
            
            # Validate revocation authority
            await self._validate_revocation_authority(
                revoked_by=revoked_by,
                permission=permission
            )
            
            # Deactivate permission
            permission.is_active = False
            permission.metadata['revoked_at'] = datetime.now().isoformat()
            permission.metadata['revoked_by'] = revoked_by
            permission.metadata['revocation_reason'] = reason
            
            # Remove from resource permissions
            if permission_id in self.resource_permissions[permission.resource_id]:
                self.resource_permissions[permission.resource_id].remove(permission_id)
            
            # Clear cache
            await self._clear_permission_cache(permission.subject_id, permission.resource_id)
            
            # Log revocation
            await self._log_permission_change(
                action="revoke",
                permission=permission,
                changed_by=revoked_by,
                reason=reason
            )
            
            # Record metrics
            await self.permission_metrics.record_permission_revocation(
                resource_type=permission.resource_type.value,
                permission_level=permission.permission_level.value,
                revoked_by=revoked_by
            )
            
            self.logger.info(f"Permission revoked: {permission_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to revoke permission: {str(e)}")
            raise PermissionError(f"Permission revocation failed: {str(e)}")
    
    async def create_role(
        self,
        role_name: str,
        description: str,
        permissions: Set[str],
        default_permission_level: PermissionLevel,
        created_by: str
    ) -> str:
        """
        Create a new role with specific permissions
        
        Args:
            role_name: Name of the role
            description: Role description
            permissions: Set of permission IDs
            default_permission_level: Default permission level for role
            created_by: ID of user creating role
            
        Returns:
            Role ID
        """
        if not self.is_initialized:
            raise PermissionError("PermissionsHandler not initialized")
        
        role_id = str(uuid.uuid4())
        
        try:
            # Validate role creation authority
            await self._validate_role_management_authority(created_by)
            
            # Create role
            role = Role(
                role_id=role_id,
                role_name=role_name,
                description=description,
                permissions=permissions,
                default_permission_level=default_permission_level,
                created_at=datetime.now(),
                created_by=created_by
            )
            
            # Store role
            self.roles[role_id] = role
            
            # Log role creation
            await self._log_role_change(
                action="create",
                role=role,
                changed_by=created_by
            )
            
            self.logger.info(f"Role created: {role_id} ({role_name})")
            return role_id
            
        except Exception as e:
            self.logger.error(f"Failed to create role: {str(e)}")
            raise PermissionError(f"Role creation failed: {str(e)}")
    
    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str
    ) -> None:
        """
        Assign a role to a user
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            assigned_by: ID of user assigning role
        """
        if not self.is_initialized:
            raise PermissionError("PermissionsHandler not initialized")
        
        try:
            # Validate role exists
            role = self.roles.get(role_id)
            if not role:
                raise ValidationError(f"Role not found: {role_id}")
            
            # Validate assignment authority
            await self._validate_role_assignment_authority(assigned_by, role)
            
            # Assign role
            self.user_roles[user_id].add(role_id)
            
            # Clear user permission cache
            await self._clear_user_permission_cache(user_id)
            
            # Log role assignment
            await self._log_role_assignment(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by
            )
            
            self.logger.info(f"Role assigned: user {user_id} -> role {role_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to assign role: {str(e)}")
            raise PermissionError(f"Role assignment failed: {str(e)}")
    
    async def get_user_permissions(
        self,
        user_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[Permission]:
        """
        Get all permissions for a user (direct and role-based)
        
        Args:
            user_id: User identifier
            resource_type: Optional filter by resource type
            
        Returns:
            List of user permissions
        """
        try:
            permissions = []
            
            # Get direct permissions
            direct_permissions = [
                p for p in self.permissions.values()
                if (p.subject_id == user_id and 
                    p.subject_type == "user" and 
                    p.is_active and
                    (not p.expires_at or p.expires_at > datetime.now()))
            ]
            
            # Get role-based permissions
            user_role_ids = self.user_roles.get(user_id, set())
            role_permissions = []
            
            for role_id in user_role_ids:
                role = self.roles.get(role_id)
                if role:
                    for perm_id in role.permissions:
                        permission = self.permissions.get(perm_id)
                        if (permission and permission.is_active and
                            (not permission.expires_at or permission.expires_at > datetime.now())):
                            role_permissions.append(permission)
            
            # Combine and filter
            all_permissions = direct_permissions + role_permissions
            
            if resource_type:
                all_permissions = [p for p in all_permissions if p.resource_type == resource_type]
            
            return all_permissions
            
        except Exception as e:
            self.logger.error(f"Failed to get user permissions: {str(e)}")
            raise PermissionError(f"Failed to get user permissions: {str(e)}")
    
    async def _evaluate_permission(self, request: AccessRequest) -> PermissionGrant:
        """Evaluate permission request against all applicable permissions"""
        try:
            # Get user permissions for the resource
            user_permissions = await self.get_user_permissions(
                user_id=request.subject_id,
                resource_type=request.resource_type
            )
            
            # Filter permissions for the specific resource
            relevant_permissions = [
                p for p in user_permissions
                if p.resource_id == request.resource_id or p.resource_id == "*"
            ]
            
            if not relevant_permissions:
                return PermissionGrant(
                    granted=False,
                    permission_id=None,
                    access_level=PermissionLevel.NONE,
                    allowed_actions=set(),
                    usage_rights=set(),
                    conditions={},
                    expires_at=None,
                    reason="No applicable permissions found"
                )
            
            # Find best matching permission
            best_permission = await self._find_best_permission(relevant_permissions, request)
            
            if not best_permission:
                return PermissionGrant(
                    granted=False,
                    permission_id=None,
                    access_level=PermissionLevel.NONE,
                    allowed_actions=set(),
                    usage_rights=set(),
                    conditions={},
                    expires_at=None,
                    reason="No matching permissions for requested action"
                )
            
            # Check specific action permission
            action_allowed = request.action in best_permission.allowed_actions
            
            # Check usage right if specified
            usage_right_allowed = True
            if request.usage_right:
                usage_right_allowed = request.usage_right in best_permission.usage_rights
            
            # Evaluate conditions
            conditions_met = await self._evaluate_conditions(
                best_permission.conditions,
                request.context
            )
            
            granted = action_allowed and usage_right_allowed and conditions_met
            
            return PermissionGrant(
                granted=granted,
                permission_id=best_permission.permission_id,
                access_level=best_permission.permission_level,
                allowed_actions=best_permission.allowed_actions,
                usage_rights=best_permission.usage_rights,
                conditions=best_permission.conditions,
                expires_at=best_permission.expires_at,
                reason="Permission granted" if granted else "Conditions not met"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate permission: {str(e)}")
            return PermissionGrant(
                granted=False,
                permission_id=None,
                access_level=PermissionLevel.NONE,
                allowed_actions=set(),
                usage_rights=set(),
                conditions={},
                expires_at=None,
                reason=f"Evaluation error: {str(e)}"
            )
    
    async def _find_best_permission(
        self,
        permissions: List[Permission],
        request: AccessRequest
    ) -> Optional[Permission]:
        """Find the best matching permission for a request"""
        if not permissions:
            return None
        
        # Sort by permission level (highest first)
        permission_levels_order = [
            PermissionLevel.OWNER,
            PermissionLevel.ADMIN,
            PermissionLevel.WRITE,
            PermissionLevel.READ,
            PermissionLevel.NONE
        ]
        
        sorted_permissions = sorted(
            permissions,
            key=lambda p: permission_levels_order.index(p.permission_level)
        )
        
        # Return first permission that contains the requested action
        for permission in sorted_permissions:
            if request.action in permission.allowed_actions:
                if request.usage_right is None or request.usage_right in permission.usage_rights:
                    return permission
        
        # If no exact match, return highest level permission
        return sorted_permissions[0] if sorted_permissions else None
    
    async def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
Evaluate permission conditions against request context"""
        if not conditions:
            return True
        
        try:
            # Time-based conditions
            if 'time_restrictions' in conditions:
                time_allowed = await self._check_time_restrictions(
                    conditions['time_restrictions'],
                    context
                )
                if not time_allowed:
                    return False
            
            # Location-based conditions
            if 'location_restrictions' in conditions:
                location_allowed = await self._check_location_restrictions(
                    conditions['location_restrictions'],
                    context
                )
                if not location_allowed:
                    return False
            
            # Usage quota conditions
            if 'usage_quota' in conditions:
                quota_available = await self._check_usage_quota(
                    conditions['usage_quota'],
                    context
                )
                if not quota_available:
                    return False
            
            # Custom conditions
            if 'custom_conditions' in conditions:
                custom_met = await self._evaluate_custom_conditions(
                    conditions['custom_conditions'],
                    context
                )
                if not custom_met:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {str(e)}")
            return False
    
    async def _create_default_roles(self) -> None:
        """Create default system roles"""
        default_roles = [
            {
                'role_name': 'Content Creator',
                'description': 'Can create and manage own content',
                'default_level': PermissionLevel.WRITE,
                'is_system': True
            },
            {
                'role_name': 'License Manager',
                'description': 'Can manage licensing and agreements',
                'default_level': PermissionLevel.ADMIN,
                'is_system': True
            },
            {
                'role_name': 'Platform Administrator',
                'description': 'Full platform administration rights',
                'default_level': PermissionLevel.OWNER,
                'is_system': True
            }
        ]
        
        for role_data in default_roles:
            role_id = str(uuid.uuid4())
            role = Role(
                role_id=role_id,
                role_name=role_data['role_name'],
                description=role_data['description'],
                permissions=set(),
                default_permission_level=role_data['default_level'],
                created_at=datetime.now(),
                created_by="system",
                is_system_role=role_data['is_system']
            )
            self.roles[role_id] = role
    
    async def _create_default_policies(self) -> None:
        """Create default permission policies"""
        # Implementation would create default policies for different resource types
        pass
    
    async def _get_default_actions(
        self,
        permission_level: PermissionLevel,
        resource_type: ResourceType
    ) -> Set[ActionType]:
        """
Get default actions for a permission level and resource type"""
        action_mappings = {
            PermissionLevel.READ: {ActionType.VIEW},
            PermissionLevel.WRITE: {ActionType.VIEW, ActionType.EDIT, ActionType.CREATE},
            PermissionLevel.ADMIN: {
                ActionType.VIEW, ActionType.EDIT, ActionType.CREATE, 
                ActionType.DELETE, ActionType.SHARE, ActionType.PUBLISH
            },
            PermissionLevel.OWNER: set(ActionType)  # All actions
        }
        
        return action_mappings.get(permission_level, set())
    
    async def _get_default_usage_rights(
        self,
        permission_level: PermissionLevel,
        resource_type: ResourceType
    ) -> Set[UsageRight]:
        """
Get default usage rights for a permission level and resource type"""
        if permission_level == PermissionLevel.OWNER:
            return set(UsageRight)  # All usage rights
        elif permission_level == PermissionLevel.ADMIN:
            return {
                UsageRight.STREAMING, UsageRight.DOWNLOAD, 
                UsageRight.COMMERCIAL_USE, UsageRight.SUBLICENSE
            }
        elif permission_level == PermissionLevel.WRITE:
            return {UsageRight.STREAMING, UsageRight.PERSONAL_USE}
        else:
            return {UsageRight.PERSONAL_USE}
    
    async def _validate_granting_authority(
        self,
        granted_by: str,
        resource_type: ResourceType,
        resource_id: str,
        permission_level: PermissionLevel
    ) -> None:
        """
Validate that the user has authority to grant the permission"""
        # Check if granter has admin or owner rights on the resource
        granter_grant = await self.check_permission(
            subject_id=granted_by,
            resource_type=resource_type,
            resource_id=resource_id,
            action=ActionType.SHARE
        )
        
        if not granter_grant.granted:
            raise AuthorizationError("Insufficient authority to grant permission")
        
        # Check if granter can grant the specific permission level
        if (permission_level in [PermissionLevel.ADMIN, PermissionLevel.OWNER] and
            granter_grant.access_level not in [PermissionLevel.ADMIN, PermissionLevel.OWNER]):
            raise AuthorizationError("Insufficient authority to grant admin/owner permissions")
    
    async def _validate_revocation_authority(
        self,
        revoked_by: str,
        permission: Permission
    ) -> None:
        """Validate that the user has authority to revoke the permission"""
        # Check if revoker granted the permission originally
        if permission.granted_by == revoked_by:
            return  # Can always revoke own grants
        
        # Check if revoker has admin rights on the resource
        revoker_grant = await self.check_permission(
            subject_id=revoked_by,
            resource_type=permission.resource_type,
            resource_id=permission.resource_id,
            action=ActionType.DELETE
        )
        
        if not revoker_grant.granted or revoker_grant.access_level not in [PermissionLevel.ADMIN, PermissionLevel.OWNER]:
            raise AuthorizationError("Insufficient authority to revoke permission")
    
    async def _validate_role_management_authority(self, user_id: str) -> None:
        """Validate user has authority to manage roles"""
        # This would check system admin permissions
        pass
    
    async def _validate_role_assignment_authority(self, assigned_by: str, role: Role) -> None:
        """
Validate user has authority to assign specific role"""
        # This would check role assignment permissions
        pass
    
    async def _log_permission_change(
        self,
        action: str,
        permission: Permission,
        changed_by: str,
        reason: str = ""
    ) -> None:
        """Log permission changes for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'permission_id': permission.permission_id,
            'resource_type': permission.resource_type.value,
            'resource_id': permission.resource_id,
            'subject_id': permission.subject_id,
            'changed_by': changed_by,
            'reason': reason
        }
        self.permission_changes.append(log_entry)
    
    async def _log_access_attempt(self, request: AccessRequest, grant: PermissionGrant) -> None:
        """
Log access attempts for audit trail"""
        log_entry = {
            'timestamp': request.timestamp.isoformat(),
            'request_id': request.request_id,
            'subject_id': request.subject_id,
            'resource_type': request.resource_type.value,
            'resource_id': request.resource_id,
            'action': request.action.value,
            'usage_right': request.usage_right.value if request.usage_right else None,
            'granted': grant.granted,
            'reason': grant.reason
        }
        self.access_log.append(log_entry)
    
    async def _log_role_change(self, action: str, role: Role, changed_by: str) -> None:
        """
Log role changes for audit trail"""
        # Implementation for role change logging
        pass
    
    async def _log_role_assignment(self, user_id: str, role_id: str, assigned_by: str) -> None:
        """
Log role assignments for audit trail"""
        # Implementation for role assignment logging
        pass
    
    async def _clear_permission_cache(self, subject_id: str, resource_id: str) -> None:
        """
Clear permission cache for subject and resource"""
        if not self.enable_caching:
            return
        
        # Clear specific cache entries
        cache_keys_to_remove = []
        for key in self.permission_cache.keys():
            if subject_id in key and resource_id in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self.permission_cache[key]
            del self.cache_timestamps[key]
    
    async def _clear_user_permission_cache(self, user_id: str) -> None:
        """
Clear all permission cache entries for a user"""
        if not self.enable_caching:
            return
        
        # Clear all cache entries for the user
        cache_keys_to_remove = []
        for key in self.permission_cache.keys():
            if user_id in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self.permission_cache[key]
            del self.cache_timestamps[key]
    
    async def _get_cached_permission(self, request: AccessRequest) -> Optional[PermissionGrant]:
        """
Get cached permission result if available and valid"""
        if not self.enable_caching:
            return None
        
        cache_key = f"{request.subject_id}:{request.resource_type.value}:{request.resource_id}:{request.action.value}"
        
        if cache_key in self.permission_cache:
            cache_time = self.cache_timestamps.get(cache_key)
            if cache_time and (datetime.now() - cache_time).seconds < self.cache_ttl:
                return self.permission_cache[cache_key]
            else:
                # Remove expired cache entry
                del self.permission_cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        return None
    
    async def _cache_permission_result(self, request: AccessRequest, grant: PermissionGrant) -> None:
        """Cache permission result"""
        if not self.enable_caching:
            return
        
        cache_key = f"{request.subject_id}:{request.resource_type.value}:{request.resource_id}:{request.action.value}"
        self.permission_cache[cache_key] = grant
        self.cache_timestamps[cache_key] = datetime.now()
    
    async def _check_time_restrictions(
        self,
        time_restrictions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check if current time meets time restrictions"""
        # Implementation for time-based access control
        return True
    
    async def _check_location_restrictions(
        self,
        location_restrictions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
Check if location meets restrictions"""
        # Implementation for location-based access control
        return True
    
    async def _check_usage_quota(
        self,
        usage_quota: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
Check if usage quota is available"""
        # Implementation for usage quota checking
        return True
    
    async def _evaluate_custom_conditions(
        self,
        custom_conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
Evaluate custom permission conditions"""
        # Implementation for custom condition evaluation
        return True
