"""
Rbac Configuration module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - RBAC Configuration
# =================================================
# 
# Enterprise-grade Role-Based Access Control for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
RBAC Configuration - Enterprise Role-Based Access Control

Provides comprehensive role-based access control including:
- Role and permission management
- User and group assignments
- Policy enforcement
- Audit logging and compliance
- Multi-tenant access control
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import jwt
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """Permission level enumeration"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceType(Enum):
    """Resource type enumeration"""
    USER = "user"
    CONTENT = "content"
    AI_MODEL = "ai_model"
    PAYMENT = "payment"
    ANALYTICS = "analytics"
    INFRASTRUCTURE = "infrastructure"
    API = "api"
    WORKFLOW = "workflow"

class ActionType(Enum):
    """Action type enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    PUBLISH = "publish"
    MANAGE = "manage"

@dataclass
class Permission:
    """Permission dataclass"""
    resource_type: ResourceType
    action: ActionType
    level: PermissionLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None

@dataclass
class Role:
    """Role dataclass"""
    name: str
    description: str
    permissions: List[Permission] = field(default_factory=list)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class User:
    """User dataclass"""
    id: str
    username: str
    email: str
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

@dataclass
class Group:
    """Group dataclass"""
    name: str
    description: str
    roles: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AccessRequest:
    """Access request dataclass"""
    user_id: str
    resource_type: ResourceType
    resource_id: str
    action: ActionType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessDecision:
    """Access decision dataclass"""
    request: AccessRequest
    allowed: bool
    reason: str
    matched_permissions: List[Permission] = field(default_factory=list)
    evaluated_at: datetime = field(default_factory=datetime.now)

class RBACConfigurator:
    """
    Enterprise Role-Based Access Control Configurator
    
    Manages roles, permissions, users, and groups for comprehensive
    access control across the Ainflue platform.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize RBAC configurator"""
        self.config_path = config_path or "/home/runner/work/Ainflue/Ainflue/infra/security"
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.access_history: List[AccessDecision] = []
        
        # Enterprise configuration
        self.max_role_permissions = 100
        self.max_user_roles = 10
        self.permission_cache_ttl = 300  # 5 minutes
        self.audit_enabled = True
        
        # Permission cache
        self._permission_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Initialize RBAC system
        self._initialize_rbac()
    
    def _initialize_rbac(self) -> None:
        """Initialize RBAC system with default roles"""
        try:
            # Create default system roles
            self._create_system_roles()
            
            # Load existing configuration
            self._load_rbac_config()
            
            logger.info("RBAC configurator initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize RBAC: {e}")
            raise
    
    def _create_system_roles(self) -> None:
        """Create default system roles"""
        try:
            # Platform Administrator
            admin_role = Role(
                name="platform_admin",
                description="Platform Administrator with full access",
                is_system_role=True,
                permissions=[
                    Permission(ResourceType.USER, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.CONTENT, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.AI_MODEL, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.PAYMENT, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.ANALYTICS, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.INFRASTRUCTURE, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.API, ActionType.MANAGE, PermissionLevel.ADMIN),
                    Permission(ResourceType.WORKFLOW, ActionType.MANAGE, PermissionLevel.ADMIN)
                ]
            )
            
            # Content Creator
            creator_role = Role(
                name="content_creator",
                description="Content Creator with content management access",
                is_system_role=True,
                permissions=[
                    Permission(ResourceType.CONTENT, ActionType.CREATE, PermissionLevel.WRITE),
                    Permission(ResourceType.CONTENT, ActionType.UPDATE, PermissionLevel.WRITE),
                    Permission(ResourceType.CONTENT, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.AI_MODEL, ActionType.EXECUTE, PermissionLevel.READ),
                    Permission(ResourceType.ANALYTICS, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.WORKFLOW, ActionType.EXECUTE, PermissionLevel.READ)
                ]
            )
            
            # Collaborator
            collaborator_role = Role(
                name="collaborator",
                description="Collaborator with limited content access",
                is_system_role=True,
                permissions=[
                    Permission(ResourceType.CONTENT, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.CONTENT, ActionType.UPDATE, PermissionLevel.WRITE,
                              conditions={"owner_permission": True}),
                    Permission(ResourceType.WORKFLOW, ActionType.EXECUTE, PermissionLevel.READ)
                ]
            )
            
            # Viewer
            viewer_role = Role(
                name="viewer",
                description="Read-only access to public content",
                is_system_role=True,
                permissions=[
                    Permission(ResourceType.CONTENT, ActionType.READ, PermissionLevel.READ,
                              conditions={"visibility": "public"}),
                    Permission(ResourceType.ANALYTICS, ActionType.READ, PermissionLevel.READ,
                              conditions={"public_metrics": True})
                ]
            )
            
            # Developer
            developer_role = Role(
                name="developer",
                description="Developer with API and infrastructure access",
                is_system_role=True,
                permissions=[
                    Permission(ResourceType.API, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.API, ActionType.EXECUTE, PermissionLevel.READ),
                    Permission(ResourceType.INFRASTRUCTURE, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.AI_MODEL, ActionType.READ, PermissionLevel.READ),
                    Permission(ResourceType.ANALYTICS, ActionType.READ, PermissionLevel.READ)
                ]
            )
            
            # Store system roles
            system_roles = [admin_role, creator_role, collaborator_role, viewer_role, developer_role]
            for role in system_roles:
                self.roles[role.name] = role
            
            logger.info(f"Created {len(system_roles)} system roles")
            
        except Exception as e:
            logger.error(f"Failed to create system roles: {e}")
            raise
    
    def _load_rbac_config(self) -> None:
        """Load existing RBAC configuration"""
        try:
            config_file = Path(f"{self.config_path}/rbac_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Load custom roles
                if "roles" in config_data:
                    for role_data in config_data["roles"]:
                        if role_data["name"] not in self.roles:  # Don't override system roles
                            role = self._deserialize_role(role_data)
                            self.roles[role.name] = role
                
                # Load users
                if "users" in config_data:
                    for user_data in config_data["users"]:
                        user = self._deserialize_user(user_data)
                        self.users[user.id] = user
                
                # Load groups
                if "groups" in config_data:
                    for group_data in config_data["groups"]:
                        group = self._deserialize_group(group_data)
                        self.groups[group.name] = group
                
                logger.info("RBAC configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load RBAC config: {e}")
    
    def _deserialize_role(self, role_data: Dict[str, Any]) -> Role:
        """Deserialize role from JSON data"""
        permissions = []
        for perm_data in role_data.get("permissions", []):
            permission = Permission(
                resource_type=ResourceType(perm_data["resource_type"]),
                action=ActionType(perm_data["action"]),
                level=PermissionLevel(perm_data["level"]),
                conditions=perm_data.get("conditions", {}),
                expiry=datetime.fromisoformat(perm_data["expiry"]) if perm_data.get("expiry") else None
            )
            permissions.append(permission)
        
        return Role(
            name=role_data["name"],
            description=role_data["description"],
            permissions=permissions,
            is_system_role=role_data.get("is_system_role", False),
            created_at=datetime.fromisoformat(role_data["created_at"]),
            updated_at=datetime.fromisoformat(role_data["updated_at"]),
            metadata=role_data.get("metadata", {})
        )
    
    def _deserialize_user(self, user_data: Dict[str, Any]) -> User:
        """Deserialize user from JSON data"""
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            roles=user_data.get("roles", []),
            groups=user_data.get("groups", []),
            attributes=user_data.get("attributes", {}),
            is_active=user_data.get("is_active", True),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
        )
    
    def _deserialize_group(self, group_data: Dict[str, Any]) -> Group:
        """Deserialize group from JSON data"""
        return Group(
            name=group_data["name"],
            description=group_data["description"],
            roles=group_data.get("roles", []),
            members=group_data.get("members", []),
            metadata=group_data.get("metadata", {}),
            created_at=datetime.fromisoformat(group_data["created_at"])
        )
    
    def create_role(self, role: Role) -> bool:
        """Create a new role"""
        try:
            # Validate role
            if not self._validate_role(role):
                return False
            
            # Check if role already exists
            if role.name in self.roles:
                logger.error(f"Role already exists: {role.name}")
                return False
            
            # Add role
            self.roles[role.name] = role
            
            # Save configuration
            self._save_rbac_config()
            
            logger.info(f"Role created: {role.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create role {role.name}: {e}")
            return False
    
    def _validate_role(self, role: Role) -> bool:
        """Validate role configuration"""
        try:
            # Check role name
            if not role.name or not isinstance(role.name, str):
                logger.error("Invalid role name")
                return False
            
            # Check permissions count
            if len(role.permissions) > self.max_role_permissions:
                logger.error(f"Too many permissions in role: {len(role.permissions)}")
                return False
            
            # Validate permissions
            for permission in role.permissions:
                if not self._validate_permission(permission):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate role: {e}")
            return False
    
    def _validate_permission(self, permission: Permission) -> bool:
        """Validate permission configuration"""
        try:
            # Check required fields
            if not all([permission.resource_type, permission.action, permission.level]):
                logger.error("Permission missing required fields")
                return False
            
            # Check expiry
            if permission.expiry and permission.expiry <= datetime.now():
                logger.warning("Permission has expired")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate permission: {e}")
            return False
    
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            # Validate user
            if not self._validate_user(user):
                return False
            
            # Check if user already exists
            if user.id in self.users:
                logger.error(f"User already exists: {user.id}")
                return False
            
            # Validate roles exist
            for role_name in user.roles:
                if role_name not in self.roles:
                    logger.error(f"Role not found: {role_name}")
                    return False
            
            # Add user
            self.users[user.id] = user
            
            # Save configuration
            self._save_rbac_config()
            
            logger.info(f"User created: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user {user.username}: {e}")
            return False
    
    def _validate_user(self, user: User) -> bool:
        """Validate user configuration"""
        try:
            # Check required fields
            if not all([user.id, user.username, user.email]):
                logger.error("User missing required fields")
                return False
            
            # Check roles count
            if len(user.roles) > self.max_user_roles:
                logger.error(f"Too many roles for user: {len(user.roles)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate user: {e}")
            return False
    
    def create_group(self, group: Group) -> bool:
        """Create a new group"""
        try:
            # Check if group already exists
            if group.name in self.groups:
                logger.error(f"Group already exists: {group.name}")
                return False
            
            # Validate roles exist
            for role_name in group.roles:
                if role_name not in self.roles:
                    logger.error(f"Role not found: {role_name}")
                    return False
            
            # Add group
            self.groups[group.name] = group
            
            # Save configuration
            self._save_rbac_config()
            
            logger.info(f"Group created: {group.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create group {group.name}: {e}")
            return False
    
    def check_access(self, request: AccessRequest) -> AccessDecision:
        """Check access permission for a request"""
        try:
            # Get user permissions
            user_permissions = self._get_user_permissions(request.user_id)
            
            # Evaluate permissions
            matched_permissions = []
            for permission in user_permissions:
                if self._matches_permission(request, permission):
                    matched_permissions.append(permission)
            
            # Determine access decision
            allowed = len(matched_permissions) > 0
            reason = self._generate_decision_reason(request, matched_permissions, allowed)
            
            decision = AccessDecision(
                request=request,
                allowed=allowed,
                reason=reason,
                matched_permissions=matched_permissions
            )
            
            # Add to audit trail
            if self.audit_enabled:
                self.access_history.append(decision)
            
            logger.debug(f"Access decision for {request.user_id}: {allowed}")
            return decision
            
        except Exception as e:
            logger.error(f"Failed to check access: {e}")
            return AccessDecision(
                request=request,
                allowed=False,
                reason=f"Error evaluating access: {str(e)}"
            )
    
    def _get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        try:
            # Check cache first
            cache_key = f"permissions_{user_id}"
            if self._is_cache_valid(cache_key):
                return self._permission_cache[cache_key]["permissions"]
            
            permissions = []
            
            # Get user
            if user_id not in self.users:
                logger.warning(f"User not found: {user_id}")
                return permissions
            
            user = self.users[user_id]
            
            # Get permissions from user roles
            for role_name in user.roles:
                if role_name in self.roles:
                    role = self.roles[role_name]
                    permissions.extend(role.permissions)
            
            # Get permissions from group roles
            for group_name in user.groups:
                if group_name in self.groups:
                    group = self.groups[group_name]
                    for role_name in group.roles:
                        if role_name in self.roles:
                            role = self.roles[role_name]
                            permissions.extend(role.permissions)
            
            # Filter expired permissions
            active_permissions = [
                p for p in permissions 
                if not p.expiry or p.expiry > datetime.now()
            ]
            
            # Cache permissions
            self._permission_cache[cache_key] = {
                "permissions": active_permissions,
                "timestamp": datetime.now()
            }
            self._cache_timestamps[cache_key] = datetime.now()
            
            return active_permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        timestamp = self._cache_timestamps[cache_key]
        return (datetime.now() - timestamp).total_seconds() < self.permission_cache_ttl
    
    def _matches_permission(self, request: AccessRequest, permission: Permission) -> bool:
        """Check if permission matches request"""
        try:
            # Check resource type
            if permission.resource_type != request.resource_type:
                return False
            
            # Check action
            if permission.action != request.action and permission.action != ActionType.MANAGE:
                return False
            
            # Check conditions
            if permission.conditions:
                if not self._evaluate_conditions(request, permission.conditions):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to match permission: {e}")
            return False
    
    def _evaluate_conditions(self, request: AccessRequest, conditions: Dict[str, Any]) -> bool:
        """Evaluate permission conditions"""
        try:
            for condition_key, condition_value in conditions.items():
                if condition_key == "owner_permission":
                    # Check if user owns the resource
                    if condition_value and not self._check_resource_ownership(request):
                        return False
                
                elif condition_key == "visibility":
                    # Check resource visibility
                    if not self._check_resource_visibility(request, condition_value):
                        return False
                
                elif condition_key == "public_metrics":
                    # Check if metrics are public
                    if condition_value and not self._check_public_metrics(request):
                        return False
                
                # Add more condition types as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to evaluate conditions: {e}")
            return False
    
    def _check_resource_ownership(self, request: AccessRequest) -> bool:
        """Check if user owns the resource"""
        # This would integrate with resource ownership system
        # For now, return True for demo purposes
        return True
    
    def _check_resource_visibility(self, request: AccessRequest, required_visibility: str) -> bool:
        """Check resource visibility"""
        # This would integrate with resource visibility system
        # For now, return True for demo purposes
        return True
    
    def _check_public_metrics(self, request: AccessRequest) -> bool:
        """Check if metrics are public"""
        # This would integrate with metrics visibility system
        # For now, return True for demo purposes
        return True
    
    def _generate_decision_reason(self, request: AccessRequest, matched_permissions: List[Permission], allowed: bool) -> str:
        """Generate human-readable decision reason"""
        if allowed:
            if len(matched_permissions) == 1:
                perm = matched_permissions[0]
                return f"Access granted via {perm.level.value} permission for {perm.resource_type.value} {perm.action.value}"
            else:
                return f"Access granted via {len(matched_permissions)} matching permissions"
        else:
            return f"Access denied: No permissions found for {request.resource_type.value} {request.action.value}"
    
    def _save_rbac_config(self) -> None:
        """Save RBAC configuration to file"""
        try:
            config_data = {
                "roles": [self._serialize_role(role) for role in self.roles.values() if not role.is_system_role],
                "users": [self._serialize_user(user) for user in self.users.values()],
                "groups": [self._serialize_group(group) for group in self.groups.values()]
            }
            
            config_file = Path(f"{self.config_path}/rbac_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.debug("RBAC configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save RBAC config: {e}")
    
    def _serialize_role(self, role: Role) -> Dict[str, Any]:
        """Serialize role to JSON-compatible dict"""
        return {
            "name": role.name,
            "description": role.description,
            "permissions": [self._serialize_permission(p) for p in role.permissions],
            "is_system_role": role.is_system_role,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat(),
            "metadata": role.metadata
        }
    
    def _serialize_permission(self, permission: Permission) -> Dict[str, Any]:
        """Serialize permission to JSON-compatible dict"""
        return {
            "resource_type": permission.resource_type.value,
            "action": permission.action.value,
            "level": permission.level.value,
            "conditions": permission.conditions,
            "expiry": permission.expiry.isoformat() if permission.expiry else None
        }
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user to JSON-compatible dict"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "groups": user.groups,
            "attributes": user.attributes,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    
    def _serialize_group(self, group: Group) -> Dict[str, Any]:
        """Serialize group to JSON-compatible dict"""
        return {
            "name": group.name,
            "description": group.description,
            "roles": group.roles,
            "members": group.members,
            "metadata": group.metadata,
            "created_at": group.created_at.isoformat()
        }
    
    def get_rbac_status(self) -> Dict[str, Any]:
        """Get RBAC system status"""
        return {
            "total_roles": len(self.roles),
            "system_roles": len([r for r in self.roles.values() if r.is_system_role]),
            "custom_roles": len([r for r in self.roles.values() if not r.is_system_role]),
            "total_users": len(self.users),
            "active_users": len([u for u in self.users.values() if u.is_active]),
            "total_groups": len(self.groups),
            "access_decisions": len(self.access_history),
            "cache_entries": len(self._permission_cache),
            "audit_enabled": self.audit_enabled
        }

# Enterprise RBAC Configurator instance
rbac_config = RBACConfigurator()

# Export for use in other modules
__all__ = [
    "RBACConfigurator",
    "Role",
    "User", 
    "Group",
    "Permission",
    "AccessRequest",
    "AccessDecision",
    "PermissionLevel",
    "ResourceType",
    "ActionType",
    "rbac_config"
]