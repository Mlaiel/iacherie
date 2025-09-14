"""
Rbac Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🛡️ Role-Based Access Control (RBAC) Engine - Ainflue Platform
============================================================

Enterprise-grade RBAC engine with hierarchical roles, dynamic permissions,
fine-grained access control, and real-time policy evaluation for the
creator content platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Role Expert: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Specialist
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import redis
import aioredis
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of resources in the system"""
    CONTENT = "content"
    PROFILE = "profile"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    COLLABORATION = "collaboration"
    SYSTEM = "system"
    API = "api"
    ADMIN = "admin"

class ActionType(Enum):
    """Types of actions that can be performed"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    PUBLISH = "publish"
    MODERATE = "moderate"
    SHARE = "share"
    MONETIZE = "monetize"

class PermissionEffect(Enum):
    """Permission effect types"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class Permission:
    """Individual permission definition"""
    id: str
    name: str
    description: str
    resource_type: ResourceType
    action: ActionType
    effect: PermissionEffect = PermissionEffect.ALLOW
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Role:
    """Role definition with permissions and hierarchy"""
    id: str
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    child_roles: Set[str] = field(default_factory=set)
    is_system_role: bool = False
    max_users: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserRole:
    """User role assignment with constraints"""
    user_id: str
    role_id: str
    resource_scope: Optional[str] = None  # Specific resource or wildcard
    granted_by: str = ""
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessRequest:
    """Access control request"""
    user_id: str
    resource_type: ResourceType
    resource_id: str
    action: ActionType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessDecision:
    """Access control decision"""
    request: AccessRequest
    decision: PermissionEffect
    applicable_permissions: List[Permission]
    applied_roles: List[str]
    reason: str
    confidence: float
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

class RBACEngine:
    """
    🏗️ Enterprise Role-Based Access Control Engine
    
    Features:
    - Hierarchical role inheritance
    - Fine-grained permissions
    - Resource-scoped access control
    - Dynamic policy evaluation
    - Temporal access controls
    - Audit trail integration
    - High-performance caching
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.redis_client = None
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # In-memory caches for performance
        self.roles_cache: Dict[str, Role] = {}
        self.permissions_cache: Dict[str, Permission] = {}
        self.user_roles_cache: Dict[str, List[UserRole]] = {}
        self.role_hierarchy_cache: Dict[str, Set[str]] = {}
        
        # Performance metrics
        self.access_checks_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("🛡️ RBAC Engine initialized")

    async def initialize(self) -> None:
        """Initialize the RBAC engine"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                encoding='utf-8'
            )
            
            # Initialize default system roles and permissions
            await self._initialize_system_roles()
            await self._initialize_system_permissions()
            
            # Build role hierarchy cache
            await self._build_role_hierarchy_cache()
            
            logger.info("✅ RBAC Engine fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RBAC engine: {e}")
            raise

    async def check_access(self, request: AccessRequest) -> AccessDecision:
        """
        🎯 Check if user has access to perform action on resource
        """
        start_time = time.time()
        self.access_checks_count += 1
        
        try:
            # Get user's effective roles
            user_roles = await self._get_user_effective_roles(request.user_id)
            
            # Get applicable permissions for the request
            applicable_permissions = await self._get_applicable_permissions(
                user_roles, request
            )
            
            # Evaluate permissions with context
            decision = await self._evaluate_permissions(
                applicable_permissions, request
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            access_decision = AccessDecision(
                request=request,
                decision=decision['effect'],
                applicable_permissions=decision['permissions'],
                applied_roles=[role.id for role in user_roles],
                reason=decision['reason'],
                confidence=decision['confidence'],
                processing_time_ms=processing_time,
                timestamp=datetime.now()
            )
            
            # Log access decision for audit
            await self._log_access_decision(access_decision)
            
            logger.info(
                f"🎯 Access check: {request.user_id} -> "
                f"{request.action.value} {request.resource_type.value}/{request.resource_id} "
                f"= {decision['effect'].value} ({processing_time:.1f}ms)"
            )
            
            return access_decision
            
        except Exception as e:
            logger.error(f"❌ Access check failed: {e}")
            # Fail secure - deny access on errors
            return AccessDecision(
                request=request,
                decision=PermissionEffect.DENY,
                applicable_permissions=[],
                applied_roles=[],
                reason=f"Access check failed: {str(e)}",
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )

    async def create_role(self, role: Role) -> bool:
        """Create a new role"""
        try:
            # Validate role
            if not self._validate_role(role):
                return False
            
            # Check if role already exists
            if await self._role_exists(role.id):
                logger.warning(f"⚠️ Role {role.id} already exists")
                return False
            
            # Store role
            await self._store_role(role)
            
            # Update caches
            self.roles_cache[role.id] = role
            await self._build_role_hierarchy_cache()
            
            logger.info(f"✅ Created role: {role.name} ({role.id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create role {role.id}: {e}")
            return False

    async def create_permission(self, permission: Permission) -> bool:
        """Create a new permission"""
        try:
            # Validate permission
            if not self._validate_permission(permission):
                return False
            
            # Check if permission already exists
            if await self._permission_exists(permission.id):
                logger.warning(f"⚠️ Permission {permission.id} already exists")
                return False
            
            # Store permission
            await self._store_permission(permission)
            
            # Update cache
            self.permissions_cache[permission.id] = permission
            
            logger.info(f"✅ Created permission: {permission.name} ({permission.id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create permission {permission.id}: {e}")
            return False

    async def assign_role_to_user(self, user_role: UserRole) -> bool:
        """Assign a role to a user"""
        try:
            # Validate role assignment
            if not await self._validate_role_assignment(user_role):
                return False
            
            # Store user role assignment
            await self._store_user_role(user_role)
            
            # Invalidate user cache
            if user_role.user_id in self.user_roles_cache:
                del self.user_roles_cache[user_role.user_id]
            
            logger.info(
                f"✅ Assigned role {user_role.role_id} to user {user_role.user_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to assign role: {e}")
            return False

    async def revoke_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Revoke a role from a user"""
        try:
            # Remove user role assignment
            await self._remove_user_role(user_id, role_id)
            
            # Invalidate user cache
            if user_id in self.user_roles_cache:
                del self.user_roles_cache[user_id]
            
            logger.info(f"✅ Revoked role {role_id} from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to revoke role: {e}")
            return False

    async def add_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """Add a permission to a role"""
        try:
            # Get role
            role = await self._get_role(role_id)
            if not role:
                logger.error(f"❌ Role {role_id} not found")
                return False
            
            # Add permission
            role.permissions.add(permission_id)
            role.updated_at = datetime.now()
            
            # Update storage
            await self._store_role(role)
            
            # Update cache
            self.roles_cache[role_id] = role
            
            logger.info(f"✅ Added permission {permission_id} to role {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add permission to role: {e}")
            return False

    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Remove a permission from a role"""
        try:
            # Get role
            role = await self._get_role(role_id)
            if not role:
                logger.error(f"❌ Role {role_id} not found")
                return False
            
            # Remove permission
            role.permissions.discard(permission_id)
            role.updated_at = datetime.now()
            
            # Update storage
            await self._store_role(role)
            
            # Update cache
            self.roles_cache[role_id] = role
            
            logger.info(f"✅ Removed permission {permission_id} from role {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove permission from role: {e}")
            return False

    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all effective permissions for a user"""
        try:
            # Get user's effective roles
            user_roles = await self._get_user_effective_roles(user_id)
            
            # Collect all permissions
            permission_ids = set()
            for role in user_roles:
                permission_ids.update(role.permissions)
            
            # Get permission objects
            permissions = []
            for perm_id in permission_ids:
                permission = await self._get_permission(perm_id)
                if permission:
                    permissions.append(permission)
            
            return permissions
            
        except Exception as e:
            logger.error(f"❌ Failed to get user permissions: {e}")
            return []

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles assigned to a user"""
        try:
            user_roles = await self._get_user_roles(user_id)
            roles = []
            
            for user_role in user_roles:
                if user_role.is_active and self._is_role_valid(user_role):
                    role = await self._get_role(user_role.role_id)
                    if role:
                        roles.append(role)
            
            return roles
            
        except Exception as e:
            logger.error(f"❌ Failed to get user roles: {e}")
            return []

    # Private helper methods
    
    async def _get_user_effective_roles(self, user_id: str) -> List[Role]:
        """Get all effective roles for a user including inherited roles"""
        try:
            # Check cache first
            if user_id in self.user_roles_cache:
                self.cache_hits += 1
                user_role_assignments = self.user_roles_cache[user_id]
            else:
                self.cache_misses += 1
                user_role_assignments = await self._get_user_roles(user_id)
                self.user_roles_cache[user_id] = user_role_assignments
            
            effective_roles = []
            processed_roles = set()
            
            # Process directly assigned roles
            for user_role in user_role_assignments:
                if user_role.is_active and self._is_role_valid(user_role):
                    await self._collect_role_hierarchy(
                        user_role.role_id, effective_roles, processed_roles
                    )
            
            return effective_roles
            
        except Exception as e:
            logger.error(f"❌ Failed to get effective roles: {e}")
            return []

    async def _collect_role_hierarchy(
        self, role_id -> None: str, effective_roles -> None: List[Role], processed_roles -> None: Set[str]
    ) -> None:
        """Recursively collect role hierarchy"""
        if role_id in processed_roles:
            return
        
        processed_roles.add(role_id)
        
        # Get role
        role = await self._get_role(role_id)
        if role:
            effective_roles.append(role)
            
            # Process parent roles
            for parent_role_id in role.parent_roles:
                await self._collect_role_hierarchy(
                    parent_role_id, effective_roles, processed_roles
                )

    async def _get_applicable_permissions(
        self, user_roles: List[Role], request: AccessRequest
    ) -> List[Permission]:
        """Get permissions applicable to the request"""
        applicable_permissions = []
        
        for role in user_roles:
            for perm_id in role.permissions:
                permission = await self._get_permission(perm_id)
                if permission and self._is_permission_applicable(permission, request):
                    applicable_permissions.append(permission)
        
        return applicable_permissions

    def _is_permission_applicable(
        self, permission: Permission, request: AccessRequest
    ) -> bool:
        """Check if permission is applicable to the request"""
        # Check resource type
        if permission.resource_type != request.resource_type:
            return False
        
        # Check action
        if permission.action != request.action:
            return False
        
        # Check conditions (simplified)
        if permission.conditions:
            # Implement condition evaluation logic here
            pass
        
        return True

    async def _evaluate_permissions(
        self, permissions: List[Permission], request: AccessRequest
    ) -> Dict[str, Any]:
        """Evaluate permissions and return decision"""
        if not permissions:
            return {
                'effect': PermissionEffect.DENY,
                'permissions': [],
                'reason': 'No applicable permissions found',
                'confidence': 1.0
            }
        
        # Check for explicit DENY permissions first
        for permission in permissions:
            if permission.effect == PermissionEffect.DENY:
                if self._evaluate_permission_conditions(permission, request):
                    return {
                        'effect': PermissionEffect.DENY,
                        'permissions': [permission],
                        'reason': f'Explicitly denied by permission: {permission.name}',
                        'confidence': 1.0
                    }
        
        # Check for ALLOW permissions
        allow_permissions = [
            p for p in permissions 
            if p.effect == PermissionEffect.ALLOW and 
               self._evaluate_permission_conditions(p, request)
        ]
        
        if allow_permissions:
            return {
                'effect': PermissionEffect.ALLOW,
                'permissions': allow_permissions,
                'reason': f'Allowed by {len(allow_permissions)} permission(s)',
                'confidence': 1.0
            }
        
        return {
            'effect': PermissionEffect.DENY,
            'permissions': [],
            'reason': 'No matching ALLOW permissions',
            'confidence': 1.0
        }

    def _evaluate_permission_conditions(
        self, permission: Permission, request: AccessRequest
    ) -> bool:
        """Evaluate permission conditions against request context"""
        if not permission.conditions:
            return True
        
        # Implement condition evaluation logic
        # This is a simplified version - real implementation would be more complex
        for condition_key, condition_value in permission.conditions.items():
            context_value = request.context.get(condition_key)
            if context_value != condition_value:
                return False
        
        return True

    # Storage and caching methods
    
    async def _initialize_system_roles(self) -> None:
        """Initialize default system roles"""
        system_roles = [
            Role(
                id="creator_musician",
                name="Creator - Musician",
                description="Role for music creators",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="creator_blogger",
                name="Creator - Blogger",
                description="Role for blog content creators",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="creator_photographer",
                name="Creator - Photographer",
                description="Role for photography creators",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="creator_influencer",
                name="Creator - Influencer",
                description="Role for social media influencers",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="creator_comedian",
                name="Creator - Comedian",
                description="Role for comedy content creators",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="platform_admin",
                name="Platform Administrator",
                description="Full platform administration role",
                permissions=set(),
                is_system_role=True
            ),
            Role(
                id="content_moderator",
                name="Content Moderator",
                description="Content moderation role",
                permissions=set(),
                is_system_role=True
            )
        ]
        
        for role in system_roles:
            await self.create_role(role)

    async def _initialize_system_permissions(self) -> None:
        """Initialize default system permissions"""
        system_permissions = [
            # Content permissions
            Permission(
                id="content_create",
                name="Create Content",
                description="Create new content",
                resource_type=ResourceType.CONTENT,
                action=ActionType.CREATE
            ),
            Permission(
                id="content_read",
                name="Read Content",
                description="View content",
                resource_type=ResourceType.CONTENT,
                action=ActionType.READ
            ),
            Permission(
                id="content_update",
                name="Update Content",
                description="Edit existing content",
                resource_type=ResourceType.CONTENT,
                action=ActionType.UPDATE
            ),
            Permission(
                id="content_delete",
                name="Delete Content",
                description="Delete content",
                resource_type=ResourceType.CONTENT,
                action=ActionType.DELETE
            ),
            Permission(
                id="content_publish",
                name="Publish Content",
                description="Publish content to platform",
                resource_type=ResourceType.CONTENT,
                action=ActionType.PUBLISH
            ),
            Permission(
                id="content_monetize",
                name="Monetize Content",
                description="Enable monetization for content",
                resource_type=ResourceType.CONTENT,
                action=ActionType.MONETIZE
            ),
            # Profile permissions
            Permission(
                id="profile_read",
                name="Read Profile",
                description="View user profiles",
                resource_type=ResourceType.PROFILE,
                action=ActionType.READ
            ),
            Permission(
                id="profile_update",
                name="Update Profile",
                description="Edit user profiles",
                resource_type=ResourceType.PROFILE,
                action=ActionType.UPDATE
            ),
            # Analytics permissions
            Permission(
                id="analytics_read",
                name="Read Analytics",
                description="View analytics data",
                resource_type=ResourceType.ANALYTICS,
                action=ActionType.READ
            ),
            # System permissions
            Permission(
                id="system_admin",
                name="System Administration",
                description="Full system administration",
                resource_type=ResourceType.SYSTEM,
                action=ActionType.EXECUTE
            )
        ]
        
        for permission in system_permissions:
            await self.create_permission(permission)
        
        # Assign permissions to roles
        await self._assign_default_permissions()

    async def _assign_default_permissions(self) -> None:
        """Assign default permissions to system roles"""
        # Creator roles get basic content permissions
        creator_permissions = [
            "content_create", "content_read", "content_update", 
            "content_publish", "content_monetize", "profile_read", 
            "profile_update", "analytics_read"
        ]
        
        creator_roles = [
            "creator_musician", "creator_blogger", "creator_photographer",
            "creator_influencer", "creator_comedian"
        ]
        
        for role_id in creator_roles:
            for perm_id in creator_permissions:
                await self.add_permission_to_role(role_id, perm_id)
        
        # Admin gets all permissions
        admin_permissions = [p.id for p in self.permissions_cache.values()]
        for perm_id in admin_permissions:
            await self.add_permission_to_role("platform_admin", perm_id)

    async def _build_role_hierarchy_cache(self) -> None:
        """Build role hierarchy cache for performance"""
        self.role_hierarchy_cache = {}
        
        for role_id, role in self.roles_cache.items():
            descendants = set()
            await self._collect_role_descendants(role_id, descendants, set())
            self.role_hierarchy_cache[role_id] = descendants

    async def _collect_role_descendants(
        self, role_id -> None: str, descendants -> None: Set[str], visited -> None: Set[str]
    ) -> None:
        """Recursively collect role descendants"""
        if role_id in visited:
            return
        
        visited.add(role_id)
        role = self.roles_cache.get(role_id)
        
        if role:
            for child_role_id in role.child_roles:
                descendants.add(child_role_id)
                await self._collect_role_descendants(child_role_id, descendants, visited)

    # Data access methods

    async def _get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        if role_id in self.roles_cache:
            return self.roles_cache[role_id]
        
        # Load from storage
        if self.redis_client:
            data = await self.redis_client.get(f"role:{role_id}")
            if data:
                role_dict = json.loads(data)
                role = Role(**role_dict)
                self.roles_cache[role_id] = role
                return role
        
        return None

    async def _get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID"""
        if permission_id in self.permissions_cache:
            return self.permissions_cache[permission_id]
        
        # Load from storage
        if self.redis_client:
            data = await self.redis_client.get(f"permission:{permission_id}")
            if data:
                perm_dict = json.loads(data)
                permission = Permission(**perm_dict)
                self.permissions_cache[permission_id] = permission
                return permission
        
        return None

    async def _get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get user role assignments"""
        if self.redis_client:
            data = await self.redis_client.get(f"user_roles:{user_id}")
            if data:
                user_roles_data = json.loads(data)
                return [UserRole(**ur) for ur in user_roles_data]
        
        return []

    async def _store_role(self, role -> None: Role) -> None:
        """Store role to persistent storage"""
        if self.redis_client:
            data = json.dumps(asdict(role), default=str)
            await self.redis_client.set(f"role:{role.id}", data)

    async def _store_permission(self, permission -> None: Permission) -> None:
        """Store permission to persistent storage"""
        if self.redis_client:
            data = json.dumps(asdict(permission), default=str)
            await self.redis_client.set(f"permission:{permission.id}", data)

    async def _store_user_role(self, user_role -> None: UserRole) -> None:
        """Store user role assignment"""
        if self.redis_client:
            # Get existing user roles
            existing_roles = await self._get_user_roles(user_role.user_id)
            
            # Add new role
            existing_roles.append(user_role)
            
            # Store updated list
            data = json.dumps([asdict(ur) for ur in existing_roles], default=str)
            await self.redis_client.set(f"user_roles:{user_role.user_id}", data)

    async def _remove_user_role(self, user_id -> None: str, role_id -> None: str) -> None:
        """Remove user role assignment"""
        if self.redis_client:
            existing_roles = await self._get_user_roles(user_id)
            updated_roles = [
                ur for ur in existing_roles 
                if ur.role_id != role_id
            ]
            
            data = json.dumps([asdict(ur) for ur in updated_roles], default=str)
            await self.redis_client.set(f"user_roles:{user_id}", data)

    # Validation methods

    def _validate_role(self, role: Role) -> bool:
        """Validate role definition"""
        if not role.id or not role.name:
            return False
        
        if role.max_users and role.max_users < 1:
            return False
        
        return True

    def _validate_permission(self, permission: Permission) -> bool:
        """Validate permission definition"""
        if not permission.id or not permission.name:
            return False
        
        return True

    async def _validate_role_assignment(self, user_role: UserRole) -> bool:
        """Validate role assignment"""
        if not user_role.user_id or not user_role.role_id:
            return False
        
        # Check if role exists
        role = await self._get_role(user_role.role_id)
        if not role:
            return False
        
        # Check role capacity
        if role.max_users:
            current_assignments = await self._count_role_assignments(user_role.role_id)
            if current_assignments >= role.max_users:
                return False
        
        return True

    def _is_role_valid(self, user_role: UserRole) -> bool:
        """Check if role assignment is currently valid"""
        if not user_role.is_active:
            return False
        
        if user_role.expires_at and user_role.expires_at < datetime.now():
            return False
        
        return True

    async def _role_exists(self, role_id: str) -> bool:
        """Check if role exists"""
        return role_id in self.roles_cache or (
            self.redis_client and 
            await self.redis_client.exists(f"role:{role_id}")
        )

    async def _permission_exists(self, permission_id: str) -> bool:
        """Check if permission exists"""
        return permission_id in self.permissions_cache or (
            self.redis_client and 
            await self.redis_client.exists(f"permission:{permission_id}")
        )

    async def _count_role_assignments(self, role_id: str) -> int:
        """Count current role assignments"""
        # This would typically query the database
        # For now, return 0
        return 0

    async def _log_access_decision(self, decision -> None: AccessDecision) -> None:
        """Log access decision for audit trail"""
        if self.redis_client:
            key = f"access_log:{decision.request.user_id}:{decision.timestamp.isoformat()}"
            data = json.dumps(asdict(decision), default=str)
            encrypted_data = self.cipher.encrypt(data.encode())
            await self.redis_client.setex(key, 86400, encrypted_data)  # 24 hour retention

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses) 
            if (self.cache_hits + self.cache_misses) > 0 else 0
        )
        
        return {
            'access_checks_count': self.access_checks_count,
            'cache_hit_rate': cache_hit_rate,
            'roles_cached': len(self.roles_cache),
            'permissions_cached': len(self.permissions_cache),
            'users_cached': len(self.user_roles_cache)
        }

    async def close(self) -> None:
        """Cleanup resources"""
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

# Export main classes
__all__ = [
    'RBACEngine', 'Role', 'Permission', 'UserRole', 
    'AccessRequest', 'AccessDecision', 'ResourceType', 
    'ActionType', 'PermissionEffect'
]

if __name__ == "__main__":
    async def test_rbac_engine() -> None:
        """Test the RBAC engine"""
        config = {}
        
        rbac = RBACEngine(config)
        await rbac.initialize()
        
        # Test access check
        request = AccessRequest(
            user_id="test_user",
            resource_type=ResourceType.CONTENT,
            resource_id="content123",
            action=ActionType.CREATE,
            context={}
        )
        
        # Assign role to test user
        user_role = UserRole(
            user_id="test_user",
            role_id="creator_musician",
            granted_by="admin"
        )
        await rbac.assign_role_to_user(user_role)
        
        # Check access
        decision = await rbac.check_access(request)
        
        print(f"🎯 Access Decision:")
        print(f"   User: {request.user_id}")
        print(f"   Action: {request.action.value}")
        print(f"   Resource: {request.resource_type.value}/{request.resource_id}")
        print(f"   Decision: {decision.decision.value}")
        print(f"   Reason: {decision.reason}")
        print(f"   Processing Time: {decision.processing_time_ms:.1f}ms")
        
        # Performance metrics
        metrics = rbac.get_performance_metrics()
        print(f"\n📊 Performance Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        await rbac.close()
    
    # Run test
    asyncio.run(test_rbac_engine())