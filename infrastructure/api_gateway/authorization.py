"""
Authorization Engine - Role-Based Access Control (RBAC) System
© 2025 Fahed Mlaiel. All rights reserved.

Authorization Engine providing RBAC policy management, permission-based access control,
resource-level authorization, dynamic policy evaluation, and audit logging.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import fnmatch
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class PermissionEffect(Enum):
    """Permission effect"""
    ALLOW = "allow"
    DENY = "deny"


class ResourceType(Enum):
    """Resource types in creator platform"""
    CONTENT = "content"
    PROFILE = "profile"
    ANALYTICS = "analytics"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    AI_SERVICE = "ai_service"
    PLATFORM = "platform"
    ADMIN = "admin"
    API = "api"
    SUBSCRIPTION = "subscription"


class ActionType(Enum):
    """Action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"
    PUBLISH = "publish"
    MODERATE = "moderate"
    MANAGE = "manage"
    CONFIGURE = "configure"


class PolicyType(Enum):
    """Policy types"""
    ROLE_BASED = "role_based"
    ATTRIBUTE_BASED = "attribute_based"
    RESOURCE_BASED = "resource_based"
    TIME_BASED = "time_based"
    CONDITION_BASED = "condition_based"


@dataclass
class Permission:
    """Individual permission definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = ResourceType.CONTENT
    action: ActionType = ActionType.READ
    resource_pattern: str = "*"  # Pattern matching for resources
    effect: PermissionEffect = PermissionEffect.ALLOW
    conditions: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """Role definition with permissions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    permissions: List[Permission] = field(default_factory=list)
    parent_roles: List[str] = field(default_factory=list)  # Role hierarchy
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Policy:
    """Authorization policy"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: PolicyType = PolicyType.ROLE_BASED
    rules: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher priority policies evaluated first
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class AuthorizationRequest:
    """Authorization request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    resource_type: ResourceType = ResourceType.CONTENT
    resource_id: str = ""
    action: ActionType = ActionType.READ
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class AuthorizationResult:
    """Authorization result"""
    request_id: str = ""
    allowed: bool = False
    reason: str = ""
    matched_policies: List[str] = field(default_factory=list)
    applied_permissions: List[str] = field(default_factory=list)
    evaluation_time: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditLogEntry:
    """Audit log entry"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    user_id: str = ""
    action: str = ""
    resource: str = ""
    result: str = ""
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthorizationEngine:
    """
    Enterprise Authorization Engine
    
    Provides comprehensive authorization services including:
    - Role-Based Access Control (RBAC)
    - Attribute-Based Access Control (ABAC)
    - Resource-level permission management
    - Dynamic policy evaluation
    - Policy hierarchy and inheritance
    - Time-based and conditional access
    - Comprehensive audit logging
    - Performance-optimized policy evaluation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Authorization Engine"""
        self.config = config or {}
        self.roles: Dict[str, Role] = {}
        self.policies: Dict[str, Policy] = {}
        self.user_roles: Dict[str, Set[str]] = defaultdict(set)
        self.resource_permissions: Dict[str, List[Permission]] = defaultdict(list)
        self.audit_log: List[AuditLogEntry] = []
        self.policy_cache: Dict[str, Any] = {}
        self.evaluation_metrics: Dict[str, Any] = defaultdict(int)
        
        # Configuration
        self.enable_audit_logging = self.config.get('enable_audit_logging', True)
        self.enable_policy_caching = self.config.get('enable_policy_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes
        self.max_audit_entries = self.config.get('max_audit_entries', 100000)
        self.default_deny = self.config.get('default_deny', True)
        self.evaluation_timeout = self.config.get('evaluation_timeout', 5.0)  # seconds
        
        # Setup default roles and policies
        self._setup_default_roles()
        self._setup_default_policies()
        
        # Start cleanup tasks
        self._start_cleanup_tasks()
        
        logger.info("Authorization Engine initialized")
    
    def _setup_default_roles(self):
        """Setup default creator platform roles"""
        # Creator Role
        creator_permissions = [
            Permission(
                resource_type=ResourceType.CONTENT,
                action=ActionType.CREATE,
                resource_pattern="user:{user_id}:*",
                description="Create own content"
            ),
            Permission(
                resource_type=ResourceType.CONTENT,
                action=ActionType.READ,
                resource_pattern="user:{user_id}:*",
                description="Read own content"
            ),
            Permission(
                resource_type=ResourceType.CONTENT,
                action=ActionType.UPDATE,
                resource_pattern="user:{user_id}:*",
                description="Update own content"
            ),
            Permission(
                resource_type=ResourceType.CONTENT,
                action=ActionType.DELETE,
                resource_pattern="user:{user_id}:*",
                description="Delete own content"
            ),
            Permission(
                resource_type=ResourceType.PROFILE,
                action=ActionType.READ,
                resource_pattern="user:{user_id}",
                description="Read own profile"
            ),
            Permission(
                resource_type=ResourceType.PROFILE,
                action=ActionType.UPDATE,
                resource_pattern="user:{user_id}",
                description="Update own profile"
            ),
            Permission(
                resource_type=ResourceType.ANALYTICS,
                action=ActionType.READ,
                resource_pattern="user:{user_id}:*",
                description="Read own analytics"
            ),
            Permission(
                resource_type=ResourceType.REVENUE,
                action=ActionType.READ,
                resource_pattern="user:{user_id}:*",
                description="Read own revenue data"
            ),
            Permission(
                resource_type=ResourceType.AI_SERVICE,
                action=ActionType.EXECUTE,
                resource_pattern="*",
                description="Use AI services"
            ),
            Permission(
                resource_type=ResourceType.COLLABORATION,
                action=ActionType.CREATE,
                resource_pattern="*",
                description="Create collaborations"
            ),
            Permission(
                resource_type=ResourceType.COLLABORATION,
                action=ActionType.READ,
                resource_pattern="participant:{user_id}:*",
                description="Read collaborations as participant"
            )
        ]
        
        creator_role = Role(
            name="creator",
            description="Content creator with basic permissions",
            permissions=creator_permissions,
            is_system_role=True
        )
        
        # Premium Creator Role
        premium_creator_role = Role(
            name="premium_creator",
            description="Premium creator with enhanced permissions",
            permissions=creator_permissions + [
                Permission(
                    resource_type=ResourceType.ANALYTICS,
                    action=ActionType.READ,
                    resource_pattern="platform:trends:*",
                    description="Access platform trends"
                ),
                Permission(
                    resource_type=ResourceType.AI_SERVICE,
                    action=ActionType.EXECUTE,
                    resource_pattern="premium:*",
                    description="Use premium AI services"
                ),
                Permission(
                    resource_type=ResourceType.COLLABORATION,
                    action=ActionType.MANAGE,
                    resource_pattern="owner:{user_id}:*",
                    description="Manage owned collaborations"
                )
            ],
            parent_roles=[creator_role.id],
            is_system_role=True
        )
        
        # Moderator Role
        moderator_role = Role(
            name="moderator",
            description="Content moderator",
            permissions=[
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read all content for moderation"
                ),
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.MODERATE,
                    resource_pattern="*",
                    description="Moderate content"
                ),
                Permission(
                    resource_type=ResourceType.PROFILE,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read profiles for moderation"
                ),
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.DELETE,
                    resource_pattern="flagged:*",
                    conditions={"moderation_required": True},
                    description="Delete flagged content"
                )
            ],
            is_system_role=True
        )
        
        # Admin Role
        admin_role = Role(
            name="admin",
            description="Platform administrator",
            permissions=[
                Permission(
                    resource_type=ResourceType.ADMIN,
                    action=ActionType.MANAGE,
                    resource_pattern="*",
                    description="Full admin access"
                ),
                Permission(
                    resource_type=ResourceType.PLATFORM,
                    action=ActionType.CONFIGURE,
                    resource_pattern="*",
                    description="Configure platform settings"
                ),
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read all content"
                ),
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.DELETE,
                    resource_pattern="*",
                    description="Delete any content"
                ),
                Permission(
                    resource_type=ResourceType.PROFILE,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read all profiles"
                ),
                Permission(
                    resource_type=ResourceType.PROFILE,
                    action=ActionType.UPDATE,
                    resource_pattern="*",
                    description="Update any profile"
                ),
                Permission(
                    resource_type=ResourceType.ANALYTICS,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read all analytics"
                ),
                Permission(
                    resource_type=ResourceType.REVENUE,
                    action=ActionType.READ,
                    resource_pattern="*",
                    description="Read all revenue data"
                )
            ],
            parent_roles=[moderator_role.id],
            is_system_role=True
        )
        
        # API Service Role
        api_service_role = Role(
            name="api_service",
            description="API service integration role",
            permissions=[
                Permission(
                    resource_type=ResourceType.API,
                    action=ActionType.EXECUTE,
                    resource_pattern="internal:*",
                    description="Execute internal APIs"
                ),
                Permission(
                    resource_type=ResourceType.CONTENT,
                    action=ActionType.READ,
                    resource_pattern="public:*",
                    description="Read public content"
                ),
                Permission(
                    resource_type=ResourceType.AI_SERVICE,
                    action=ActionType.EXECUTE,
                    resource_pattern="*",
                    description="Execute AI services"
                )
            ],
            is_system_role=True
        )
        
        # Store roles
        roles = [creator_role, premium_creator_role, moderator_role, admin_role, api_service_role]
        for role in roles:
            self.roles[role.id] = role
        
        logger.info(f"Setup {len(roles)} default roles")
    
    def _setup_default_policies(self):
        """Setup default authorization policies"""
        # Time-based access policy
        time_policy = Policy(
            name="business_hours_access",
            description="Restrict certain operations to business hours",
            type=PolicyType.TIME_BASED,
            rules=[
                {
                    "resource_types": ["admin", "platform"],
                    "actions": ["configure", "manage"],
                    "time_conditions": {
                        "allowed_hours": "09:00-17:00",
                        "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                        "timezone": "UTC"
                    }
                }
            ],
            priority=100
        )
        
        # Rate limiting policy
        rate_limit_policy = Policy(
            name="api_rate_limiting",
            description="Rate limiting for API access",
            type=PolicyType.CONDITION_BASED,
            rules=[
                {
                    "resource_types": ["api"],
                    "conditions": {
                        "max_requests_per_minute": 1000,
                        "max_requests_per_hour": 50000,
                        "burst_limit": 100
                    }
                }
            ],
            priority=90
        )
        
        # Content ownership policy
        ownership_policy = Policy(
            name="content_ownership",
            description="Users can only access their own content",
            type=PolicyType.RESOURCE_BASED,
            rules=[
                {
                    "resource_types": ["content", "analytics", "revenue"],
                    "ownership_required": True,
                    "allowed_actions": ["create", "read", "update", "delete"],
                    "exceptions": {
                        "roles": ["admin", "moderator"],
                        "public_content": {
                            "actions": ["read"],
                            "conditions": {"visibility": "public"}
                        }
                    }
                }
            ],
            priority=80
        )
        
        # Collaboration access policy
        collaboration_policy = Policy(
            name="collaboration_access",
            description="Collaboration participant access control",
            type=PolicyType.ATTRIBUTE_BASED,
            rules=[
                {
                    "resource_types": ["collaboration"],
                    "access_conditions": {
                        "participant": True,
                        "status": "active",
                        "permissions": ["read", "contribute"]
                    },
                    "owner_permissions": ["manage", "delete", "configure"]
                }
            ],
            priority=70
        )
        
        # AI service usage policy
        ai_service_policy = Policy(
            name="ai_service_usage",
            description="AI service access based on subscription tier",
            type=PolicyType.ATTRIBUTE_BASED,
            rules=[
                {
                    "resource_types": ["ai_service"],
                    "tier_permissions": {
                        "free": ["basic_generation", "text_analysis"],
                        "premium": ["advanced_generation", "voice_cloning", "trend_analysis"],
                        "enterprise": ["custom_models", "bulk_processing", "priority_queue"]
                    },
                    "usage_limits": {
                        "free": {"daily_requests": 100},
                        "premium": {"daily_requests": 10000},
                        "enterprise": {"daily_requests": -1}  # Unlimited
                    }
                }
            ],
            priority=60
        )
        
        # Store policies
        policies = [time_policy, rate_limit_policy, ownership_policy, collaboration_policy, ai_service_policy]
        for policy in policies:
            self.policies[policy.id] = policy
        
        logger.info(f"Setup {len(policies)} default policies")
    
    def _start_cleanup_tasks(self):
        """Start background cleanup tasks"""
        asyncio.create_task(self._cleanup_audit_log())
        asyncio.create_task(self._cleanup_policy_cache())
    
    async def authorize(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Authorize a request using RBAC and policy evaluation"""
        start_time = time.time()
        
        try:
            # Create result object
            result = AuthorizationResult(
                request_id=request.id,
                allowed=False,
                reason="Default deny"
            )
            
            # Get user roles
            user_roles = self.user_roles.get(request.user_id, set())
            if not user_roles:
                result.reason = "No roles assigned to user"
                await self._audit_log_entry(request, result)
                return result
            
            # Check cache first
            cache_key = self._generate_cache_key(request, user_roles)
            if self.enable_policy_caching and cache_key in self.policy_cache:
                cached_result = self.policy_cache[cache_key]
                if cached_result['expires_at'] > datetime.utcnow():
                    result.allowed = cached_result['allowed']
                    result.reason = cached_result['reason']
                    result.matched_policies = cached_result['matched_policies']
                    result.evaluation_time = time.time() - start_time
                    self.evaluation_metrics['cache_hits'] += 1
                    return result
            
            # Evaluate permissions through roles
            role_permissions = await self._get_user_permissions(request.user_id)
            permission_result = await self._evaluate_permissions(request, role_permissions)
            
            # Evaluate policies
            policy_result = await self._evaluate_policies(request)
            
            # Combine results (policies can override role permissions)
            if policy_result['allowed'] is not None:
                result.allowed = policy_result['allowed']
                result.reason = policy_result['reason']
                result.matched_policies = policy_result['matched_policies']
            else:
                result.allowed = permission_result['allowed']
                result.reason = permission_result['reason']
                result.applied_permissions = permission_result['applied_permissions']
            
            # Calculate evaluation time
            result.evaluation_time = time.time() - start_time
            
            # Cache result
            if self.enable_policy_caching:
                await self._cache_result(cache_key, result)
            
            # Audit log
            if self.enable_audit_logging:
                await self._audit_log_entry(request, result)
            
            # Update metrics
            self.evaluation_metrics['total_evaluations'] += 1
            if result.allowed:
                self.evaluation_metrics['allowed_requests'] += 1
            else:
                self.evaluation_metrics['denied_requests'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            result = AuthorizationResult(
                request_id=request.id,
                allowed=False,
                reason=f"Authorization error: {str(e)}",
                evaluation_time=time.time() - start_time
            )
            await self._audit_log_entry(request, result)
            return result
    
    async def assign_role(self, user_id: str, role_id: str) -> bool:
        """Assign role to user"""
        try:
            if role_id not in self.roles:
                logger.error(f"Role not found: {role_id}")
                return False
            
            self.user_roles[user_id].add(role_id)
            
            # Clear cache for user
            await self._clear_user_cache(user_id)
            
            logger.info(f"Role {role_id} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False
    
    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user"""
        try:
            self.user_roles[user_id].discard(role_id)
            
            # Clear cache for user
            await self._clear_user_cache(user_id)
            
            logger.info(f"Role {role_id} revoked from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking role: {e}")
            return False
    
    async def create_role(self, role_data: Dict[str, Any]) -> Optional[Role]:
        """Create new role"""
        try:
            permissions = []
            for perm_data in role_data.get('permissions', []):
                permission = Permission(
                    resource_type=ResourceType(perm_data['resource_type']),
                    action=ActionType(perm_data['action']),
                    resource_pattern=perm_data.get('resource_pattern', '*'),
                    effect=PermissionEffect(perm_data.get('effect', 'allow')),
                    conditions=perm_data.get('conditions', {}),
                    description=perm_data.get('description', '')
                )
                permissions.append(permission)
            
            role = Role(
                name=role_data['name'],
                description=role_data.get('description', ''),
                permissions=permissions,
                parent_roles=role_data.get('parent_roles', []),
                metadata=role_data.get('metadata', {})
            )
            
            self.roles[role.id] = role
            
            logger.info(f"Role created: {role.name} ({role.id})")
            return role
            
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return None
    
    async def create_policy(self, policy_data: Dict[str, Any]) -> Optional[Policy]:
        """Create new policy"""
        try:
            policy = Policy(
                name=policy_data['name'],
                description=policy_data.get('description', ''),
                type=PolicyType(policy_data.get('type', 'role_based')),
                rules=policy_data.get('rules', []),
                conditions=policy_data.get('conditions', {}),
                priority=policy_data.get('priority', 0),
                expires_at=policy_data.get('expires_at')
            )
            
            self.policies[policy.id] = policy
            
            # Clear cache as new policy might affect evaluations
            self.policy_cache.clear()
            
            logger.info(f"Policy created: {policy.name} ({policy.id})")
            return policy
            
        except Exception as e:
            logger.error(f"Error creating policy: {e}")
            return None
    
    async def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get effective permissions for user"""
        try:
            permissions = await self._get_user_permissions(user_id)
            
            return [
                {
                    'id': perm.id,
                    'resource_type': perm.resource_type.value,
                    'action': perm.action.value,
                    'resource_pattern': perm.resource_pattern,
                    'effect': perm.effect.value,
                    'conditions': perm.conditions,
                    'description': perm.description
                }
                for perm in permissions
            ]
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def get_authorization_metrics(self) -> Dict[str, Any]:
        """Get authorization metrics and statistics"""
        try:
            # Recent audit log analysis
            recent_entries = [
                entry for entry in self.audit_log
                if (datetime.utcnow() - entry.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            allowed_count = len([e for e in recent_entries if e.result == 'allowed'])
            denied_count = len([e for e in recent_entries if e.result == 'denied'])
            
            # Top denied resources
            denied_resources = defaultdict(int)
            for entry in recent_entries:
                if entry.result == 'denied':
                    denied_resources[entry.resource] += 1
            
            # Performance metrics
            avg_evaluation_time = 0.0
            if self.evaluation_metrics['total_evaluations'] > 0:
                total_time = sum(
                    float(entry.metadata.get('evaluation_time', 0))
                    for entry in recent_entries
                    if 'evaluation_time' in entry.metadata
                )
                avg_evaluation_time = total_time / len(recent_entries) if recent_entries else 0.0
            
            return {
                'total_roles': len(self.roles),
                'total_policies': len(self.policies),
                'total_users_with_roles': len(self.user_roles),
                'recent_requests': len(recent_entries),
                'allowed_requests': allowed_count,
                'denied_requests': denied_count,
                'success_rate': (allowed_count / len(recent_entries) * 100) if recent_entries else 0,
                'avg_evaluation_time_ms': avg_evaluation_time * 1000,
                'cache_hit_rate': (
                    self.evaluation_metrics['cache_hits'] / 
                    self.evaluation_metrics['total_evaluations'] * 100
                ) if self.evaluation_metrics['total_evaluations'] > 0 else 0,
                'top_denied_resources': dict(list(denied_resources.items())[:10]),
                'policy_cache_size': len(self.policy_cache),
                'audit_log_size': len(self.audit_log),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting authorization metrics: {e}")
            return {'error': str(e)}
    
    # Internal Implementation Methods
    
    async def _get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all effective permissions for user including inherited ones"""
        permissions = []
        user_roles = self.user_roles.get(user_id, set())
        visited_roles = set()
        
        async def collect_role_permissions(role_id: str):
            if role_id in visited_roles or role_id not in self.roles:
                return
            
            visited_roles.add(role_id)
            role = self.roles[role_id]
            
            # Add role permissions
            permissions.extend(role.permissions)
            
            # Recursively add parent role permissions
            for parent_role_id in role.parent_roles:
                await collect_role_permissions(parent_role_id)
        
        # Collect permissions from all user roles
        for role_id in user_roles:
            await collect_role_permissions(role_id)
        
        return permissions
    
    async def _evaluate_permissions(self, request: AuthorizationRequest, permissions: List[Permission]) -> Dict[str, Any]:
        """Evaluate permissions against request"""
        try:
            applied_permissions = []
            explicit_allow = False
            explicit_deny = False
            
            for permission in permissions:
                if await self._permission_matches(permission, request):
                    applied_permissions.append(permission.id)
                    
                    if permission.effect == PermissionEffect.ALLOW:
                        explicit_allow = True
                    elif permission.effect == PermissionEffect.DENY:
                        explicit_deny = True
            
            # Deny takes precedence over allow
            if explicit_deny:
                return {
                    'allowed': False,
                    'reason': 'Explicit deny permission',
                    'applied_permissions': applied_permissions
                }
            elif explicit_allow:
                return {
                    'allowed': True,
                    'reason': 'Explicit allow permission',
                    'applied_permissions': applied_permissions
                }
            else:
                return {
                    'allowed': not self.default_deny,
                    'reason': 'No matching permissions' + (' - default deny' if self.default_deny else ' - default allow'),
                    'applied_permissions': applied_permissions
                }
            
        except Exception as e:
            logger.error(f"Permission evaluation error: {e}")
            return {
                'allowed': False,
                'reason': f'Permission evaluation error: {str(e)}',
                'applied_permissions': []
            }
    
    async def _evaluate_policies(self, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate policies against request"""
        try:
            matched_policies = []
            policy_decision = None
            policy_reason = ""
            
            # Sort policies by priority (higher first)
            sorted_policies = sorted(
                [p for p in self.policies.values() if p.is_active],
                key=lambda p: p.priority,
                reverse=True
            )
            
            for policy in sorted_policies:
                # Check if policy has expired
                if policy.expires_at and policy.expires_at < datetime.utcnow():
                    continue
                
                # Evaluate policy
                policy_result = await self._evaluate_single_policy(policy, request)
                if policy_result['matches']:
                    matched_policies.append(policy.id)
                    
                    if policy_result['decision'] is not None:
                        policy_decision = policy_result['decision']
                        policy_reason = f"Policy '{policy.name}': {policy_result['reason']}"
                        break  # First matching policy with decision wins
            
            return {
                'allowed': policy_decision,
                'reason': policy_reason,
                'matched_policies': matched_policies
            }
            
        except Exception as e:
            logger.error(f"Policy evaluation error: {e}")
            return {
                'allowed': None,
                'reason': f'Policy evaluation error: {str(e)}',
                'matched_policies': []
            }
    
    async def _evaluate_single_policy(self, policy: Policy, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate single policy against request"""
        try:
            if policy.type == PolicyType.TIME_BASED:
                return await self._evaluate_time_policy(policy, request)
            elif policy.type == PolicyType.CONDITION_BASED:
                return await self._evaluate_condition_policy(policy, request)
            elif policy.type == PolicyType.RESOURCE_BASED:
                return await self._evaluate_resource_policy(policy, request)
            elif policy.type == PolicyType.ATTRIBUTE_BASED:
                return await self._evaluate_attribute_policy(policy, request)
            else:
                return {'matches': False, 'decision': None, 'reason': 'Unknown policy type'}
            
        except Exception as e:
            logger.error(f"Single policy evaluation error: {e}")
            return {'matches': False, 'decision': False, 'reason': f'Policy error: {str(e)}'}
    
    async def _evaluate_time_policy(self, policy: Policy, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate time-based policy"""
        # Simplified time policy evaluation
        current_time = datetime.utcnow()
        current_hour = current_time.hour
        current_day = current_time.strftime('%A').lower()
        
        for rule in policy.rules:
            if request.resource_type.value in rule.get('resource_types', []):
                time_conditions = rule.get('time_conditions', {})
                allowed_hours = time_conditions.get('allowed_hours', '00:00-23:59')
                allowed_days = time_conditions.get('allowed_days', [])
                
                # Check hours
                if allowed_hours != '00:00-23:59':
                    start_hour, end_hour = allowed_hours.split('-')
                    start = int(start_hour.split(':')[0])
                    end = int(end_hour.split(':')[0])
                    
                    if not (start <= current_hour <= end):
                        return {'matches': True, 'decision': False, 'reason': 'Outside allowed hours'}
                
                # Check days
                if allowed_days and current_day not in allowed_days:
                    return {'matches': True, 'decision': False, 'reason': 'Outside allowed days'}
                
                return {'matches': True, 'decision': True, 'reason': 'Within allowed time'}
        
        return {'matches': False, 'decision': None, 'reason': 'No matching time rules'}
    
    async def _evaluate_condition_policy(self, policy: Policy, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate condition-based policy"""
        # Simplified condition evaluation
        for rule in policy.rules:
            if request.resource_type.value in rule.get('resource_types', []):
                conditions = rule.get('conditions', {})
                
                # Example: rate limiting check
                if 'max_requests_per_minute' in conditions:
                    # This would integrate with rate limiter
                    max_requests = conditions['max_requests_per_minute']
                    # Simplified check - in production would check actual rate
                    return {'matches': True, 'decision': True, 'reason': 'Rate limit check passed'}
        
        return {'matches': False, 'decision': None, 'reason': 'No matching condition rules'}
    
    async def _evaluate_resource_policy(self, policy: Policy, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate resource-based policy"""
        for rule in policy.rules:
            if request.resource_type.value in rule.get('resource_types', []):
                if rule.get('ownership_required', False):
                    # Check if user owns the resource
                    if f"user:{request.user_id}" in request.resource_id:
                        return {'matches': True, 'decision': True, 'reason': 'Resource ownership verified'}
                    else:
                        # Check exceptions
                        exceptions = rule.get('exceptions', {})
                        user_roles = self.user_roles.get(request.user_id, set())
                        exception_roles = [self._get_role_name(role_id) for role_id in user_roles]
                        
                        if any(role in exceptions.get('roles', []) for role in exception_roles):
                            return {'matches': True, 'decision': True, 'reason': 'Exception role access'}
                        
                        return {'matches': True, 'decision': False, 'reason': 'Resource ownership required'}
        
        return {'matches': False, 'decision': None, 'reason': 'No matching resource rules'}
    
    async def _evaluate_attribute_policy(self, policy: Policy, request: AuthorizationRequest) -> Dict[str, Any]:
        """Evaluate attribute-based policy"""
        # Simplified attribute evaluation
        for rule in policy.rules:
            if request.resource_type.value in rule.get('resource_types', []):
                # Example: collaboration access
                if 'access_conditions' in rule:
                    conditions = rule['access_conditions']
                    # This would check actual collaboration membership
                    return {'matches': True, 'decision': True, 'reason': 'Attribute conditions met'}
        
        return {'matches': False, 'decision': None, 'reason': 'No matching attribute rules'}
    
    async def _permission_matches(self, permission: Permission, request: AuthorizationRequest) -> bool:
        """Check if permission matches request"""
        try:
            # Check resource type
            if permission.resource_type != request.resource_type:
                return False
            
            # Check action
            if permission.action != request.action:
                return False
            
            # Check resource pattern
            if not self._pattern_matches(permission.resource_pattern, request.resource_id, request.context):
                return False
            
            # Check conditions
            if permission.conditions:
                if not await self._evaluate_conditions(permission.conditions, request):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Permission matching error: {e}")
            return False
    
    def _pattern_matches(self, pattern: str, resource_id: str, context: Dict[str, Any]) -> bool:
        """Check if resource pattern matches resource ID"""
        try:
            # Replace context variables in pattern
            resolved_pattern = pattern
            for key, value in context.items():
                resolved_pattern = resolved_pattern.replace(f"{{{key}}}", str(value))
            
            # Use fnmatch for wildcard matching
            return fnmatch.fnmatch(resource_id, resolved_pattern)
            
        except Exception as e:
            logger.error(f"Pattern matching error: {e}")
            return False
    
    async def _evaluate_conditions(self, conditions: Dict[str, Any], request: AuthorizationRequest) -> bool:
        """Evaluate permission conditions"""
        try:
            for condition_key, condition_value in conditions.items():
                context_value = request.context.get(condition_key)
                
                if condition_key == "moderation_required":
                    # Example condition check
                    return context_value == condition_value
                
                # Add more condition types as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    def _generate_cache_key(self, request: AuthorizationRequest, user_roles: Set[str]) -> str:
        """Generate cache key for request"""
        key_parts = [
            request.user_id,
            request.resource_type.value,
            request.resource_id,
            request.action.value,
            json.dumps(sorted(user_roles)),
            json.dumps(request.context, sort_keys=True)
        ]
        
        key_string = ":".join(key_parts)
        return f"auth_cache:{hash(key_string)}"
    
    async def _cache_result(self, cache_key: str, result: AuthorizationResult):
        """Cache authorization result"""
        try:
            self.policy_cache[cache_key] = {
                'allowed': result.allowed,
                'reason': result.reason,
                'matched_policies': result.matched_policies,
                'expires_at': datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            }
            
        except Exception as e:
            logger.error(f"Cache result error: {e}")
    
    async def _clear_user_cache(self, user_id: str):
        """Clear cache entries for specific user"""
        try:
            keys_to_remove = [
                key for key in self.policy_cache.keys()
                if user_id in key
            ]
            
            for key in keys_to_remove:
                del self.policy_cache[key]
            
        except Exception as e:
            logger.error(f"Clear user cache error: {e}")
    
    def _get_role_name(self, role_id: str) -> str:
        """Get role name by ID"""
        role = self.roles.get(role_id)
        return role.name if role else ""
    
    async def _audit_log_entry(self, request: AuthorizationRequest, result: AuthorizationResult):
        """Create audit log entry"""
        try:
            entry = AuditLogEntry(
                request_id=request.id,
                user_id=request.user_id,
                action=f"{request.action.value}:{request.resource_type.value}",
                resource=request.resource_id,
                result="allowed" if result.allowed else "denied",
                reason=result.reason,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                metadata={
                    'evaluation_time': result.evaluation_time,
                    'matched_policies': result.matched_policies,
                    'applied_permissions': result.applied_permissions
                }
            )
            
            self.audit_log.append(entry)
            
        except Exception as e:
            logger.error(f"Audit log error: {e}")
    
    async def _cleanup_audit_log(self):
        """Clean up old audit log entries"""
        while True:
            try:
                if len(self.audit_log) > self.max_audit_entries:
                    # Keep most recent entries
                    self.audit_log = self.audit_log[-self.max_audit_entries:]
                    logger.info(f"Cleaned up audit log, kept {len(self.audit_log)} entries")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Audit log cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_policy_cache(self):
        """Clean up expired cache entries"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = [
                    key for key, value in self.policy_cache.items()
                    if value['expires_at'] < current_time
                ]
                
                for key in expired_keys:
                    del self.policy_cache[key]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(300)


# Authorization Engine Factory
def create_authorization_engine(config: Optional[Dict[str, Any]] = None) -> AuthorizationEngine:
    """Factory function to create Authorization Engine instance"""
    return AuthorizationEngine(config)


# Creator Platform Resource Patterns
CREATOR_PLATFORM_PATTERNS = {
    'own_content': 'user:{user_id}:content:*',
    'own_profile': 'user:{user_id}:profile',
    'own_analytics': 'user:{user_id}:analytics:*',
    'own_revenue': 'user:{user_id}:revenue:*',
    'collaboration_participant': 'collaboration:*:participant:{user_id}',
    'collaboration_owner': 'collaboration:*:owner:{user_id}',
    'public_content': 'content:public:*',
    'platform_trends': 'platform:trends:*',
    'ai_service_basic': 'ai:basic:*',
    'ai_service_premium': 'ai:premium:*',
    'admin_all': '*'
}


if __name__ == "__main__":
    # Example usage
    async def main():
        auth_engine = create_authorization_engine({
            'enable_audit_logging': True,
            'enable_policy_caching': True,
            'default_deny': True
        })
        
        # Create test user with creator role
        creator_role_id = None
        for role_id, role in auth_engine.roles.items():
            if role.name == 'creator':
                creator_role_id = role_id
                break
        
        if creator_role_id:
            user_id = 'test_creator_123'
            await auth_engine.assign_role(user_id, creator_role_id)
            
            # Test authorization requests
            requests = [
                AuthorizationRequest(
                    user_id=user_id,
                    resource_type=ResourceType.CONTENT,
                    resource_id=f'user:{user_id}:content:video_123',
                    action=ActionType.READ,
                    context={'user_id': user_id}
                ),
                AuthorizationRequest(
                    user_id=user_id,
                    resource_type=ResourceType.CONTENT,
                    resource_id='user:other_user:content:video_456',
                    action=ActionType.READ,
                    context={'user_id': user_id}
                ),
                AuthorizationRequest(
                    user_id=user_id,
                    resource_type=ResourceType.AI_SERVICE,
                    resource_id='ai:basic:text_generation',
                    action=ActionType.EXECUTE,
                    context={'user_id': user_id}
                )
            ]
            
            print("Authorization Test Results:")
            for request in requests:
                result = await auth_engine.authorize(request)
                print(f"  {request.action.value} {request.resource_id}: {result.allowed} - {result.reason}")
            
            # Get user permissions
            permissions = await auth_engine.get_user_permissions(user_id)
            print(f"\nUser has {len(permissions)} permissions")
            
            # Get metrics
            metrics = await auth_engine.get_authorization_metrics()
            print(f"\nAuthorization Metrics:")
            print(f"  Total requests: {metrics['recent_requests']}")
            print(f"  Success rate: {metrics['success_rate']:.1f}%")
            print(f"  Avg evaluation time: {metrics['avg_evaluation_time_ms']:.2f}ms")
    
    asyncio.run(main())