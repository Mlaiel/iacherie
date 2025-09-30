"""
👥 Creator Model Permissions - Enterprise RBAC System
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Gestion permissions modèles par créateur Creator Economy
Expertise: Backend Senior + Sécurité + DBA + Lead Dev IA
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class CreatorTier(Enum):
    """Creator subscription tiers"""
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class PermissionScope(Enum):
    """Permission scopes"""
    MODEL = "model"
    API = "api"
    DATA = "data"
    ANALYTICS = "analytics"
    ADMIN = "admin"
    BILLING = "billing"


class PermissionAction(Enum):
    """Permission actions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"
    EXPORT = "export"
    ADMIN = "admin"


class AccessDecision(Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class Permission:
    """Individual permission definition"""
    permission_id: str
    name: str
    description: str
    scope: PermissionScope
    action: PermissionAction
    resource_pattern: str  # e.g., "model:*", "model:nlp:*", "api:inference:*"
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary"""
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope.value,
            "action": self.action.value,
            "resource_pattern": self.resource_pattern,
            "conditions": self.conditions,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    name: str
    description: str
    permissions: List[str]  # permission_ids
    tier_restrictions: List[CreatorTier] = field(default_factory=list)
    auto_assign_conditions: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary"""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "tier_restrictions": [tier.value for tier in self.tier_restrictions],
            "auto_assign_conditions": self.auto_assign_conditions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "active": self.active
        }


@dataclass
class CreatorProfile:
    """Creator profile with permissions context"""
    creator_id: str
    username: str
    email: str
    tier: CreatorTier
    roles: List[str]  # role_ids
    direct_permissions: List[str]  # permission_ids
    api_quota: Dict[str, int] = field(default_factory=dict)
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, suspended, banned
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert creator profile to dictionary"""
        return {
            "creator_id": self.creator_id,
            "username": self.username,
            "email": self.email,
            "tier": self.tier.value,
            "roles": self.roles,
            "direct_permissions": self.direct_permissions,
            "api_quota": self.api_quota,
            "usage_stats": self.usage_stats,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }


@dataclass
class AccessRequest:
    """Access request for audit trail"""
    request_id: str
    creator_id: str
    resource: str
    action: str
    timestamp: datetime
    decision: AccessDecision
    reason: str
    context: Dict[str, Any] = field(default_factory=dict)
    approved_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert access request to dictionary"""
        return {
            "request_id": self.request_id,
            "creator_id": self.creator_id,
            "resource": self.resource,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "decision": self.decision.value,
            "reason": self.reason,
            "context": self.context,
            "approved_by": self.approved_by
        }


@dataclass
class QuotaLimit:
    """Resource quota limits"""
    quota_id: str
    name: str
    resource_type: str  # api_calls, model_usage, data_storage, etc.
    limit_value: int
    period: str  # hourly, daily, monthly
    tier_restrictions: List[CreatorTier] = field(default_factory=list)
    overage_allowed: bool = False
    overage_rate: float = 0.0
    reset_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quota limit to dictionary"""
        return {
            "quota_id": self.quota_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "limit_value": self.limit_value,
            "period": self.period,
            "tier_restrictions": [tier.value for tier in self.tier_restrictions],
            "overage_allowed": self.overage_allowed,
            "overage_rate": self.overage_rate,
            "reset_time": self.reset_time.isoformat() if self.reset_time else None
        }


class CreatorModelPermissions:
    """
    👥 Gestion permissions modèles par créateur
    
    Enterprise RBAC system with:
    - Role-based access control with hierarchical permissions
    - Creator tier permission mapping with automatic assignments
    - Model usage quota management with overage handling
    - API access control per creator with rate limiting
    - Permission audit trail with compliance reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize creator permissions manager
        
        Args:
            config: Permissions management configuration
        """
        self.config = config or self._get_default_config()
        self.manager_id = str(uuid.uuid4())
        
        # Core permission data
        self._permissions: Dict[str, Permission] = {}
        self._roles: Dict[str, Role] = {}
        self._creators: Dict[str, CreatorProfile] = {}
        self._quota_limits: Dict[str, QuotaLimit] = {}
        
        # Access tracking
        self._access_requests: List[AccessRequest] = []
        self._quota_usage: Dict[str, Dict[str, int]] = defaultdict(dict)  # creator_id -> resource_type -> usage
        self._session_cache: Dict[str, Dict[str, Any]] = {}  # creator_id -> cached permissions
        
        # Performance metrics
        self._metrics = {
            "access_checks_total": 0,
            "access_granted": 0,
            "access_denied": 0,
            "quota_violations": 0,
            "role_assignments": 0,
            "permission_cache_hits": 0
        }
        
        # Initialize default permissions and roles
        self._initialize_default_permissions()
        self._initialize_default_roles()
        self._initialize_tier_quotas()
        
        logger.info(f"👥 CreatorModelPermissions initialized with ID: {self.manager_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default permissions configuration"""
        return {
            "rbac": {
                "enable_hierarchical_roles": True,
                "enable_conditional_permissions": True,
                "cache_permissions": True,
                "cache_ttl_seconds": 300
            },
            "creator_tiers": {
                "basic": {
                    "api_calls_per_hour": 100,
                    "models_accessible": 5,
                    "data_export_limit_mb": 10,
                    "concurrent_sessions": 1
                },
                "premium": {
                    "api_calls_per_hour": 1000,
                    "models_accessible": 25,
                    "data_export_limit_mb": 100,
                    "concurrent_sessions": 3
                },
                "professional": {
                    "api_calls_per_hour": 5000,
                    "models_accessible": 100,
                    "data_export_limit_mb": 1000,
                    "concurrent_sessions": 5
                },
                "enterprise": {
                    "api_calls_per_hour": 50000,
                    "models_accessible": -1,  # unlimited
                    "data_export_limit_mb": 10000,
                    "concurrent_sessions": 20
                }
            },
            "quota_management": {
                "enable_overages": True,
                "overage_multiplier": 2.0,
                "auto_suspend_on_violation": False,
                "quota_reset_time": "midnight"
            },
            "audit": {
                "log_all_access": True,
                "retention_days": 365,
                "compliance_reporting": True,
                "real_time_alerts": True
            },
            "api_access": {
                "rate_limiting": True,
                "require_authentication": True,
                "token_expiry_hours": 24,
                "refresh_token_enabled": True
            }
        }
    
    def _initialize_default_permissions(self) -> None:
        """Initialize default permissions"""
        try:
            default_permissions = [
                # Model permissions
                Permission(
                    permission_id="model_read_basic",
                    name="Read Basic Models",
                    description="Read access to basic AI models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.READ,
                    resource_pattern="model:basic:*"
                ),
                Permission(
                    permission_id="model_execute_basic",
                    name="Execute Basic Models",
                    description="Execute/inference access to basic AI models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.EXECUTE,
                    resource_pattern="model:basic:*"
                ),
                Permission(
                    permission_id="model_read_premium",
                    name="Read Premium Models",
                    description="Read access to premium AI models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.READ,
                    resource_pattern="model:premium:*"
                ),
                Permission(
                    permission_id="model_execute_premium",
                    name="Execute Premium Models",
                    description="Execute premium AI models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.EXECUTE,
                    resource_pattern="model:premium:*"
                ),
                Permission(
                    permission_id="model_read_enterprise",
                    name="Read Enterprise Models",
                    description="Read access to enterprise AI models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.READ,
                    resource_pattern="model:enterprise:*"
                ),
                Permission(
                    permission_id="model_admin",
                    name="Model Admin",
                    description="Full administrative access to models",
                    scope=PermissionScope.MODEL,
                    action=PermissionAction.ADMIN,
                    resource_pattern="model:*"
                ),
                
                # API permissions
                Permission(
                    permission_id="api_inference_basic",
                    name="Basic API Inference",
                    description="Access to basic inference API endpoints",
                    scope=PermissionScope.API,
                    action=PermissionAction.EXECUTE,
                    resource_pattern="api:inference:basic:*"
                ),
                Permission(
                    permission_id="api_inference_premium",
                    name="Premium API Inference",
                    description="Access to premium inference API endpoints",
                    scope=PermissionScope.API,
                    action=PermissionAction.EXECUTE,
                    resource_pattern="api:inference:premium:*"
                ),
                Permission(
                    permission_id="api_batch_processing",
                    name="Batch Processing API",
                    description="Access to batch processing API endpoints",  
                    scope=PermissionScope.API,
                    action=PermissionAction.EXECUTE,
                    resource_pattern="api:batch:*"
                ),
                
                # Data permissions
                Permission(
                    permission_id="data_export_basic",
                    name="Basic Data Export",
                    description="Export model outputs and basic analytics",
                    scope=PermissionScope.DATA,
                    action=PermissionAction.EXPORT,
                    resource_pattern="data:export:basic:*"
                ),
                Permission(
                    permission_id="data_export_advanced",
                    name="Advanced Data Export",
                    description="Export detailed analytics and model insights",
                    scope=PermissionScope.DATA,
                    action=PermissionAction.EXPORT,
                    resource_pattern="data:export:advanced:*"
                ),
                
                # Analytics permissions
                Permission(
                    permission_id="analytics_read_basic",
                    name="Basic Analytics Access",
                    description="View basic usage analytics and reports",
                    scope=PermissionScope.ANALYTICS,
                    action=PermissionAction.READ,
                    resource_pattern="analytics:basic:*"
                ),
                Permission(
                    permission_id="analytics_read_advanced",
                    name="Advanced Analytics Access",
                    description="View detailed analytics and custom reports",
                    scope=PermissionScope.ANALYTICS,
                    action=PermissionAction.READ,
                    resource_pattern="analytics:advanced:*"
                )
            ]
            
            for permission in default_permissions:
                self._permissions[permission.permission_id] = permission
            
            logger.info(f"📝 Initialized {len(default_permissions)} default permissions")
            
        except Exception as e:
            logger.error(f"Default permissions initialization error: {str(e)}")
    
    def _initialize_default_roles(self) -> None:
        """Initialize default roles with tier mappings"""
        try:
            default_roles = [
                # Basic tier role
                Role(
                    role_id="creator_basic",
                    name="Basic Creator",
                    description="Basic creator with limited model access",
                    permissions=[
                        "model_read_basic",
                        "model_execute_basic",
                        "api_inference_basic",
                        "data_export_basic",
                        "analytics_read_basic"
                    ],
                    tier_restrictions=[CreatorTier.BASIC]
                ),
                
                # Premium tier role
                Role(
                    role_id="creator_premium",
                    name="Premium Creator",
                    description="Premium creator with enhanced model access",
                    permissions=[
                        "model_read_basic",
                        "model_execute_basic",
                        "model_read_premium",
                        "model_execute_premium",
                        "api_inference_basic",
                        "api_inference_premium",
                        "data_export_basic",
                        "data_export_advanced",
                        "analytics_read_basic",
                        "analytics_read_advanced"
                    ],
                    tier_restrictions=[CreatorTier.PREMIUM]
                ),
                
                # Professional tier role
                Role(
                    role_id="creator_professional",
                    name="Professional Creator",
                    description="Professional creator with batch processing access",
                    permissions=[
                        "model_read_basic",
                        "model_execute_basic",
                        "model_read_premium",
                        "model_execute_premium",
                        "api_inference_basic",
                        "api_inference_premium",
                        "api_batch_processing",
                        "data_export_basic",
                        "data_export_advanced",
                        "analytics_read_basic",
                        "analytics_read_advanced"
                    ],
                    tier_restrictions=[CreatorTier.PROFESSIONAL]
                ),
                
                # Enterprise tier role
                Role(
                    role_id="creator_enterprise",
                    name="Enterprise Creator",
                    description="Enterprise creator with full access",
                    permissions=[
                        "model_read_basic",
                        "model_execute_basic",
                        "model_read_premium",
                        "model_execute_premium",
                        "model_read_enterprise",
                        "api_inference_basic",
                        "api_inference_premium",
                        "api_batch_processing",
                        "data_export_basic",
                        "data_export_advanced",
                        "analytics_read_basic",
                        "analytics_read_advanced"
                    ],
                    tier_restrictions=[CreatorTier.ENTERPRISE]
                ),
                
                # Admin role
                Role(
                    role_id="admin",
                    name="Administrator",
                    description="Full administrative access",
                    permissions=list(self._permissions.keys()),  # All permissions
                    tier_restrictions=[]  # No tier restrictions
                )
            ]
            
            for role in default_roles:
                self._roles[role.role_id] = role
            
            logger.info(f"👤 Initialized {len(default_roles)} default roles")
            
        except Exception as e:
            logger.error(f"Default roles initialization error: {str(e)}")
    
    def _initialize_tier_quotas(self) -> None:
        """Initialize quota limits by tier"""
        try:
            tier_config = self.config["creator_tiers"]
            
            for tier_name, limits in tier_config.items():
                tier = CreatorTier(tier_name)
                
                # API calls quota
                api_quota = QuotaLimit(
                    quota_id=f"api_calls_{tier_name}",
                    name=f"API Calls - {tier_name.title()}",
                    resource_type="api_calls",
                    limit_value=limits["api_calls_per_hour"],
                    period="hourly",
                    tier_restrictions=[tier],
                    overage_allowed=self.config["quota_management"]["enable_overages"],
                    overage_rate=self.config["quota_management"]["overage_multiplier"]
                )
                self._quota_limits[api_quota.quota_id] = api_quota
                
                # Model access quota
                if limits["models_accessible"] > 0:
                    model_quota = QuotaLimit(
                        quota_id=f"models_accessible_{tier_name}",
                        name=f"Models Accessible - {tier_name.title()}",
                        resource_type="models_accessible",
                        limit_value=limits["models_accessible"],
                        period="monthly",
                        tier_restrictions=[tier]
                    )
                    self._quota_limits[model_quota.quota_id] = model_quota
                
                # Data export quota
                export_quota = QuotaLimit(
                    quota_id=f"data_export_{tier_name}",
                    name=f"Data Export - {tier_name.title()}",
                    resource_type="data_export_mb",
                    limit_value=limits["data_export_limit_mb"],
                    period="daily",
                    tier_restrictions=[tier]
                )
                self._quota_limits[export_quota.quota_id] = export_quota
            
            logger.info(f"📊 Initialized quotas for {len(tier_config)} creator tiers")
            
        except Exception as e:
            logger.error(f"Quota initialization error: {str(e)}")
    
    async def register_creator(
        self,
        creator_id: str,
        username: str,
        email: str,
        tier: CreatorTier,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register new creator with automatic role assignment
        
        Args:
            creator_id: Unique creator identifier
            username: Creator username
            email: Creator email
            tier: Creator subscription tier
            metadata: Additional creator metadata
            
        Returns:
            Success status
        """
        try:
            if creator_id in self._creators:
                logger.warning(f"Creator {creator_id} already exists")
                return False
            
            # Auto-assign role based on tier
            auto_role = self._get_tier_role(tier)
            
            # Create creator profile
            creator = CreatorProfile(
                creator_id=creator_id,
                username=username,
                email=email,
                tier=tier,
                roles=[auto_role] if auto_role else [],
                direct_permissions=[],
                api_quota=self._get_tier_quotas(tier),
                metadata=metadata or {}
            )
            
            self._creators[creator_id] = creator
            
            # Initialize quota usage tracking
            self._quota_usage[creator_id] = {}
            
            # Clear permission cache for this creator
            if creator_id in self._session_cache:
                del self._session_cache[creator_id]
            
            self._metrics["role_assignments"] += 1
            
            logger.info(f"👤 Registered creator {username} ({creator_id}) with tier {tier.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Creator registration error: {str(e)}")
            return False
    
    def _get_tier_role(self, tier: CreatorTier) -> Optional[str]:
        """Get default role for creator tier"""
        tier_role_map = {
            CreatorTier.BASIC: "creator_basic",
            CreatorTier.PREMIUM: "creator_premium", 
            CreatorTier.PROFESSIONAL: "creator_professional",
            CreatorTier.ENTERPRISE: "creator_enterprise"
        }
        return tier_role_map.get(tier)
    
    def _get_tier_quotas(self, tier: CreatorTier) -> Dict[str, int]:
        """Get quota limits for creator tier"""
        tier_config = self.config["creator_tiers"].get(tier.value, {})
        return {
            "api_calls_per_hour": tier_config.get("api_calls_per_hour", 100),
            "models_accessible": tier_config.get("models_accessible", 5),
            "data_export_limit_mb": tier_config.get("data_export_limit_mb", 10),
            "concurrent_sessions": tier_config.get("concurrent_sessions", 1)
        }
    
    async def check_access(
        self,
        creator_id: str,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[AccessDecision, str]:
        """
        Check if creator has access to resource/action
        
        Args:
            creator_id: Creator identifier
            resource: Resource pattern (e.g., "model:nlp:sentiment")
            action: Action to perform (e.g., "execute")
            context: Additional context for conditional permissions
            
        Returns:
            Tuple of (access_decision, reason)
        """
        try:
            self._metrics["access_checks_total"] += 1
            
            # Get creator profile
            creator = self._creators.get(creator_id)
            if not creator:
                decision = AccessDecision.DENY
                reason = f"Creator {creator_id} not found"
                await self._log_access_request(creator_id, resource, action, decision, reason, context)
                self._metrics["access_denied"] += 1
                return decision, reason
            
            # Check if creator is active
            if creator.status != "active":
                decision = AccessDecision.DENY
                reason = f"Creator account is {creator.status}"
                await self._log_access_request(creator_id, resource, action, decision, reason, context)
                self._metrics["access_denied"] += 1
                return decision, reason
            
            # Check quota limits first
            quota_check = await self._check_quota_limits(creator, resource, action)
            if not quota_check["allowed"]:
                decision = AccessDecision.DENY
                reason = quota_check["reason"]
                await self._log_access_request(creator_id, resource, action, decision, reason, context)
                self._metrics["access_denied"] += 1
                self._metrics["quota_violations"] += 1
                return decision, reason
            
            # Get effective permissions (from cache if available)
            effective_permissions = await self._get_effective_permissions(creator_id)
            
            # Check permissions against resource/action
            access_granted = False
            matching_permission = None
            
            for permission_id in effective_permissions:
                permission = self._permissions.get(permission_id)
                if permission and self._permission_matches(permission, resource, action):
                    # Check permission conditions
                    if await self._check_permission_conditions(permission, creator, context):
                        access_granted = True
                        matching_permission = permission
                        break
            
            if access_granted:
                decision = AccessDecision.ALLOW
                reason = f"Access granted via permission: {matching_permission.name}"
                self._metrics["access_granted"] += 1
            else:
                decision = AccessDecision.DENY
                reason = "No matching permissions found"
                self._metrics["access_denied"] += 1
            
            # Log access request
            await self._log_access_request(creator_id, resource, action, decision, reason, context)
            
            return decision, reason
            
        except Exception as e:
            logger.error(f"Access check error: {str(e)}")
            decision = AccessDecision.DENY
            reason = f"Access check failed: {str(e)}"
            await self._log_access_request(creator_id, resource, action, decision, reason, context)
            self._metrics["access_denied"] += 1
            return decision, reason
    
    async def _check_quota_limits(
        self,
        creator: CreatorProfile,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """Check if creator has quota available for request"""
        try:
            # Determine resource type from resource pattern
            resource_type = self._get_resource_type(resource, action)
            if not resource_type:
                return {"allowed": True, "reason": "No quota restrictions"}
            
            # Get applicable quota limits
            applicable_quotas = [
                quota for quota in self._quota_limits.values()
                if (quota.resource_type == resource_type and
                    (not quota.tier_restrictions or creator.tier in quota.tier_restrictions))
            ]
            
            if not applicable_quotas:
                return {"allowed": True, "reason": "No quota limits defined"}
            
            # Check each applicable quota
            for quota in applicable_quotas:
                current_usage = self._quota_usage[creator.creator_id].get(resource_type, 0)
                
                if current_usage >= quota.limit_value:
                    if quota.overage_allowed:
                        # Calculate overage cost/penalty
                        overage_amount = current_usage - quota.limit_value
                        overage_cost = overage_amount * quota.overage_rate
                        
                        return {
                            "allowed": True,
                            "reason": f"Overage allowed (cost: ${overage_cost:.2f})",
                            "overage": True,
                            "overage_cost": overage_cost
                        }
                    else:
                        return {
                            "allowed": False,
                            "reason": f"Quota exceeded: {current_usage}/{quota.limit_value} {quota.name}"
                        }
            
            return {"allowed": True, "reason": "Within quota limits"}
            
        except Exception as e:
            logger.error(f"Quota check error: {str(e)}")
            return {"allowed": False, "reason": f"Quota check failed: {str(e)}"}
    
    def _get_resource_type(self, resource: str, action: str) -> Optional[str]:
        """Extract resource type for quota checking"""
        if resource.startswith("api:") and action == "execute":
            return "api_calls"
        elif resource.startswith("model:") and action == "read":
            return "models_accessible"
        elif resource.startswith("data:export"):
            return "data_export_mb"
        
        return None
    
    async def _get_effective_permissions(self, creator_id: str) -> Set[str]:
        """Get effective permissions for creator (with caching)"""
        try:
            # Check cache first
            if (self.config["rbac"]["cache_permissions"] and 
                creator_id in self._session_cache):
                cache_entry = self._session_cache[creator_id]
                cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
                
                if cache_age < self.config["rbac"]["cache_ttl_seconds"]:
                    self._metrics["permission_cache_hits"] += 1
                    return set(cache_entry["permissions"])
            
            creator = self._creators[creator_id]
            effective_permissions = set()
            
            # Add direct permissions
            effective_permissions.update(creator.direct_permissions)
            
            # Add permissions from roles
            for role_id in creator.roles:
                role = self._roles.get(role_id)
                if role and role.active:
                    # Check tier restrictions
                    if not role.tier_restrictions or creator.tier in role.tier_restrictions:
                        effective_permissions.update(role.permissions)
            
            # Cache the result
            if self.config["rbac"]["cache_permissions"]:
                self._session_cache[creator_id] = {
                    "permissions": list(effective_permissions),
                    "timestamp": datetime.now()
                }
            
            return effective_permissions
            
        except Exception as e:
            logger.error(f"Effective permissions calculation error: {str(e)}")
            return set()
    
    def _permission_matches(self, permission: Permission, resource: str, action: str) -> bool:
        """Check if permission matches resource and action"""
        try:
            # Check action match
            if permission.action.value != action and permission.action != PermissionAction.ADMIN:
                return False
            
            # Check resource pattern match
            return self._resource_pattern_matches(permission.resource_pattern, resource)
            
        except Exception as e:
            logger.error(f"Permission matching error: {str(e)}")
            return False
    
    def _resource_pattern_matches(self, pattern: str, resource: str) -> bool:
        """Check if resource matches pattern (supports wildcards)"""
        try:
            pattern_parts = pattern.split(':')
            resource_parts = resource.split(':')
            
            if len(pattern_parts) > len(resource_parts):
                return False
            
            for i, pattern_part in enumerate(pattern_parts):
                if pattern_part == '*':
                    return True  # Wildcard matches everything from this point
                
                if i >= len(resource_parts) or pattern_part != resource_parts[i]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Pattern matching error: {str(e)}")
            return False
    
    async def _check_permission_conditions(
        self,
        permission: Permission,
        creator: CreatorProfile,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check permission conditions"""
        try:
            if not permission.conditions:
                return True
            
            # Check expiration
            if permission.expires_at and datetime.now() > permission.expires_at:
                return False
            
            # Check custom conditions
            for condition in permission.conditions:
                if not await self._evaluate_condition(condition, creator, context):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition checking error: {str(e)}")
            return False
    
    async def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        creator: CreatorProfile,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Evaluate individual permission condition"""
        try:
            condition_type = condition.get("type")
            
            if condition_type == "time_range":
                return self._check_time_range_condition(condition)
            elif condition_type == "usage_limit":
                return await self._check_usage_limit_condition(condition, creator)
            elif condition_type == "context_match":
                return self._check_context_condition(condition, context)
            elif condition_type == "tier_minimum":
                return self._check_tier_condition(condition, creator)
            
            logger.warning(f"Unknown condition type: {condition_type}")
            return True  # Default to allow for unknown conditions
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {str(e)}")
            return False
    
    def _check_time_range_condition(self, condition: Dict[str, Any]) -> bool:
        """Check time range condition"""
        try:
            now = datetime.now()
            start_hour = condition.get("start_hour", 0)
            end_hour = condition.get("end_hour", 24)
            
            current_hour = now.hour
            return start_hour <= current_hour < end_hour
            
        except Exception as e:
            logger.error(f"Time range condition error: {str(e)}")
            return False
    
    async def _check_usage_limit_condition(
        self,
        condition: Dict[str, Any],
        creator: CreatorProfile
    ) -> bool:
        """Check usage limit condition"""
        try:
            resource_type = condition.get("resource_type")
            limit = condition.get("limit", 0)
            
            current_usage = self._quota_usage[creator.creator_id].get(resource_type, 0)
            return current_usage < limit
            
        except Exception as e:
            logger.error(f"Usage limit condition error: {str(e)}")
            return False
    
    def _check_context_condition(
        self,
        condition: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check context matching condition"""
        try:
            if not context:
                return False
            
            required_context = condition.get("required_context", {})
            
            for key, expected_value in required_context.items():
                if context.get(key) != expected_value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Context condition error: {str(e)}")
            return False
    
    def _check_tier_condition(
        self,
        condition: Dict[str, Any],
        creator: CreatorProfile
    ) -> bool:
        """Check tier minimum condition"""
        try:
            minimum_tier = CreatorTier(condition.get("minimum_tier", "basic"))
            
            tier_hierarchy = {
                CreatorTier.BASIC: 0,
                CreatorTier.PREMIUM: 1,
                CreatorTier.PROFESSIONAL: 2,
                CreatorTier.ENTERPRISE: 3,
                CreatorTier.CUSTOM: 4
            }
            
            return tier_hierarchy.get(creator.tier, 0) >= tier_hierarchy.get(minimum_tier, 0)
            
        except Exception as e:
            logger.error(f"Tier condition error: {str(e)}")
            return False
    
    async def _log_access_request(
        self,
        creator_id: str,
        resource: str,
        action: str,
        decision: AccessDecision,
        reason: str,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Log access request for audit trail"""
        try:
            request = AccessRequest(
                request_id=str(uuid.uuid4()),
                creator_id=creator_id,
                resource=resource,
                action=action,
                timestamp=datetime.now(),
                decision=decision,
                reason=reason,
                context=context or {}
            )
            
            self._access_requests.append(request)
            
            # Trim access request history if needed
            if len(self._access_requests) > 10000:  # Keep last 10k requests
                self._access_requests = self._access_requests[-5000:]
            
        except Exception as e:
            logger.error(f"Access request logging error: {str(e)}")
    
    async def increment_usage(
        self,
        creator_id: str,
        resource_type: str,
        amount: int = 1
    ) -> bool:
        """
        Increment usage counter for creator
        
        Args:
            creator_id: Creator identifier
            resource_type: Type of resource used
            amount: Amount to increment
            
        Returns:
            Success status
        """
        try:
            if creator_id not in self._creators:
                return False
            
            if creator_id not in self._quota_usage:
                self._quota_usage[creator_id] = {}
            
            current_usage = self._quota_usage[creator_id].get(resource_type, 0)
            self._quota_usage[creator_id][resource_type] = current_usage + amount
            
            logger.debug(f"📊 Incremented usage for {creator_id}: {resource_type} +{amount} = {current_usage + amount}")
            
            return True
            
        except Exception as e:
            logger.error(f"Usage increment error: {str(e)}")
            return False
    
    def get_creator_permissions(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator's complete permission profile"""
        try:
            creator = self._creators.get(creator_id)
            if not creator:
                return None
            
            # Get effective permissions
            effective_permissions = asyncio.run(self._get_effective_permissions(creator_id))
            
            # Get quota usage
            quota_usage = self._quota_usage.get(creator_id, {})
            
            return {
                "creator": creator.to_dict(),
                "effective_permissions": list(effective_permissions),
                "quota_usage": quota_usage,
                "access_requests_count": len([r for r in self._access_requests if r.creator_id == creator_id])
            }
            
        except Exception as e:
            logger.error(f"Get creator permissions error: {str(e)}")
            return None
    
    def get_access_audit_trail(
        self,
        creator_id: Optional[str] = None,
        resource_pattern: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get access audit trail with filters"""
        try:
            filtered_requests = self._access_requests
            
            # Apply filters
            if creator_id:
                filtered_requests = [r for r in filtered_requests if r.creator_id == creator_id]
            
            if resource_pattern:
                filtered_requests = [
                    r for r in filtered_requests 
                    if self._resource_pattern_matches(resource_pattern, r.resource)
                ]
            
            if start_time:
                filtered_requests = [r for r in filtered_requests if r.timestamp >= start_time]
            
            # Sort by timestamp (newest first) and limit
            filtered_requests.sort(key=lambda x: x.timestamp, reverse=True)
            
            return [r.to_dict() for r in filtered_requests[:limit]]
            
        except Exception as e:
            logger.error(f"Audit trail retrieval error: {str(e)}")
            return []
    
    def get_permission_metrics(self) -> Dict[str, Any]:
        """Get permission system metrics"""
        return {
            **self._metrics,
            "total_creators": len(self._creators),
            "total_permissions": len(self._permissions),
            "total_roles": len(self._roles),
            "active_creators": len([c for c in self._creators.values() if c.status == "active"]),
            "quota_limits": len(self._quota_limits),
            "cached_sessions": len(self._session_cache)
        }
    
    def health_check(self) -> str:
        """Health check for permission system"""
        try:
            # Check for creators without roles
            creators_without_roles = [c for c in self._creators.values() if not c.roles]
            if len(creators_without_roles) > len(self._creators) * 0.1:  # More than 10%
                return f"WARNING: {len(creators_without_roles)} creators without roles"
            
            # Check for excessive access denials
            if self._metrics["access_checks_total"] > 0:
                denial_rate = self._metrics["access_denied"] / self._metrics["access_checks_total"]
                if denial_rate > 0.5:  # More than 50% denials
                    return f"WARNING: High access denial rate: {denial_rate:.2%}"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and related types
__all__ = [
    "CreatorModelPermissions",
    "CreatorTier",
    "PermissionScope",
    "PermissionAction",
    "AccessDecision",
    "Permission",
    "Role",
    "CreatorProfile",
    "AccessRequest",
    "QuotaLimit"
]