"""
🔐 TEAM PERMISSIONS ENGINE - ENTERPRISE ARCHITECTURE
=================================================

Role-based access control system for multimedia collaboration with
granular permissions, dynamic roles, and enterprise-grade security.

**Expert Implementation:**
- Security Engineer: Advanced permission models and access control
- Backend Senior: High-performance permission evaluation
- Database Administrator: Efficient permission storage and indexing
- Enterprise Architect: Scalable role hierarchy and delegation

**Features:** RBAC, Granular permissions, Role hierarchy, Resource-level access, Audit logging
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import copy

# Permission system libraries
try:
    import redis
    import asyncpg
    from datetime import datetime, timedelta
    import jwt
    import hashlib
except ImportError as e:
    logging.warning(f"Team permissions dependencies not available: {e}")

logger = logging.getLogger(__name__)

class Permission(Enum):
    """System permissions"""
    # Basic permissions
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # Content permissions
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    PUBLISH_CONTENT = "publish_content"
    
    # Collaboration permissions
    COMMENT = "comment"
    REPLY = "reply"
    REACT = "react"
    MENTION = "mention"
    
    # Workflow permissions
    REQUEST_APPROVAL = "request_approval"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    
    # Team management permissions
    INVITE_USERS = "invite_users"
    REMOVE_USERS = "remove_users"
    ASSIGN_ROLES = "assign_roles"
    MANAGE_PERMISSIONS = "manage_permissions"
    
    # Administrative permissions
    ADMIN = "admin"
    MANAGE_WORKSPACE = "manage_workspace"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # Advanced permissions
    MANAGE_VERSIONS = "manage_versions"
    MERGE_BRANCHES = "merge_branches"
    MANAGE_ASSETS = "manage_assets"
    CONFIGURE_WORKFLOWS = "configure_workflows"

class ResourceType(Enum):
    """Types of resources that can be protected"""
    WORKSPACE = "workspace"
    PROJECT = "project"
    CONTENT = "content"
    ASSET = "asset"
    COMMENT = "comment"
    VERSION = "version"
    BRANCH = "branch"
    WORKFLOW = "workflow"

class PermissionScope(Enum):
    """Permission scope levels"""
    GLOBAL = "global"          # System-wide permissions
    WORKSPACE = "workspace"    # Workspace-level permissions
    PROJECT = "project"        # Project-level permissions
    RESOURCE = "resource"      # Individual resource permissions

@dataclass
class Role:
    """Role definition"""
    role_id: str
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[str]  # Role inheritance
    is_system_role: bool
    is_custom: bool
    created_by: str
    created_at: float
    metadata: Dict[str, Any]

@dataclass
class UserRole:
    """User role assignment"""
    assignment_id: str
    user_id: str
    role_id: str
    scope: PermissionScope
    resource_id: Optional[str]  # Specific resource if scope is RESOURCE
    assigned_by: str
    assigned_at: float
    expires_at: Optional[float]
    is_active: bool
    conditions: Dict[str, Any]  # Conditional permissions

@dataclass
class PermissionRule:
    """Permission rule"""
    rule_id: str
    resource_type: ResourceType
    resource_id: Optional[str]
    user_id: Optional[str]
    role_id: Optional[str]
    permission: Permission
    action: str  # 'allow' or 'deny'
    priority: int
    conditions: Dict[str, Any]
    created_at: float

@dataclass
class AccessRequest:
    """Access request for auditing"""
    request_id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission: Permission
    timestamp: float
    granted: bool
    reason: str
    session_id: Optional[str]

class TeamPermissionEngine:
    """Core team permission management engine"""
    
    def __init__(self):
        self.roles = {}  # role_id -> Role
        self.user_roles = defaultdict(list)  # user_id -> [UserRole]
        self.permission_rules = defaultdict(list)  # resource_type -> [PermissionRule]
        self.access_log = deque(maxlen=10000)  # Access request history
        
        # Permission cache for performance
        self.permission_cache = {}  # user_id:resource_id:permission -> (result, timestamp)
        self.cache_ttl = 300  # 5 minutes
        
        # Database connections
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except:
            self.redis_client = None
            logger.warning("Redis not available for permission caching")
        
        # Initialize system roles
        self._initialize_system_roles()
        
        # Permission evaluation settings
        self.default_deny = True
        self.permission_inheritance = True
        self.audit_enabled = True
        
    def _initialize_system_roles(self):
        """Initialize predefined system roles"""
        system_roles = [
            {
                'name': 'owner',
                'description': 'Workspace owner with full permissions',
                'permissions': set(Permission),  # All permissions
                'inherits_from': None
            },
            {
                'name': 'admin',
                'description': 'Administrator with management permissions',
                'permissions': {
                    Permission.READ, Permission.WRITE, Permission.DELETE,
                    Permission.CREATE_CONTENT, Permission.EDIT_CONTENT, Permission.DELETE_CONTENT,
                    Permission.PUBLISH_CONTENT, Permission.COMMENT, Permission.REPLY, Permission.REACT,
                    Permission.APPROVE, Permission.REJECT, Permission.REQUEST_CHANGES,
                    Permission.INVITE_USERS, Permission.REMOVE_USERS, Permission.ASSIGN_ROLES,
                    Permission.MANAGE_WORKSPACE, Permission.VIEW_ANALYTICS,
                    Permission.MANAGE_VERSIONS, Permission.MERGE_BRANCHES, Permission.MANAGE_ASSETS
                },
                'inherits_from': None
            },
            {
                'name': 'editor',
                'description': 'Content editor with creation and editing permissions',
                'permissions': {
                    Permission.READ, Permission.WRITE,
                    Permission.CREATE_CONTENT, Permission.EDIT_CONTENT,
                    Permission.COMMENT, Permission.REPLY, Permission.REACT, Permission.MENTION,
                    Permission.REQUEST_APPROVAL, Permission.MANAGE_VERSIONS
                },
                'inherits_from': None
            },
            {
                'name': 'reviewer',
                'description': 'Content reviewer with approval permissions',
                'permissions': {
                    Permission.READ, Permission.COMMENT, Permission.REPLY, Permission.REACT,
                    Permission.APPROVE, Permission.REJECT, Permission.REQUEST_CHANGES,
                    Permission.VIEW_ANALYTICS
                },
                'inherits_from': None
            },
            {
                'name': 'contributor',
                'description': 'Limited contributor with basic editing',
                'permissions': {
                    Permission.READ, Permission.WRITE,
                    Permission.COMMENT, Permission.REPLY, Permission.REACT,
                    Permission.REQUEST_APPROVAL
                },
                'inherits_from': None
            },
            {
                'name': 'viewer',
                'description': 'Read-only access with commenting',
                'permissions': {
                    Permission.READ, Permission.COMMENT, Permission.REPLY, Permission.REACT
                },
                'inherits_from': None
            }
        ]
        
        for role_data in system_roles:
            role_id = str(uuid.uuid4())
            role = Role(
                role_id=role_id,
                name=role_data['name'],
                description=role_data['description'],
                permissions=role_data['permissions'],
                inherits_from=role_data['inherits_from'],
                is_system_role=True,
                is_custom=False,
                created_by='system',
                created_at=time.time(),
                metadata={}
            )
            self.roles[role_id] = role
    
    async def create_custom_role(self, name: str, description: str,
                               permissions: Set[Permission], creator_id: str,
                               inherits_from: Optional[str] = None) -> Role:
        """Create custom role"""
        try:
            role_id = str(uuid.uuid4())
            
            # Validate inherited role exists
            if inherits_from and inherits_from not in self.roles:
                raise ValueError(f"Parent role {inherits_from} not found")
            
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                permissions=permissions,
                inherits_from=inherits_from,
                is_system_role=False,
                is_custom=True,
                created_by=creator_id,
                created_at=time.time(),
                metadata={}
            )
            
            self.roles[role_id] = role
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_role_redis(role)
            
            logger.info(f"Created custom role {name} ({role_id})")
            return role
            
        except Exception as e:
            logger.error(f"Failed to create custom role: {e}")
            raise
    
    async def assign_role(self, user_id: str, role_id: str, assigner_id: str,
                         scope: PermissionScope = PermissionScope.WORKSPACE,
                         resource_id: Optional[str] = None,
                         expires_at: Optional[float] = None,
                         conditions: Dict[str, Any] = None) -> UserRole:
        """Assign role to user"""
        try:
            if role_id not in self.roles:
                raise ValueError(f"Role {role_id} not found")
            
            assignment_id = str(uuid.uuid4())
            
            user_role = UserRole(
                assignment_id=assignment_id,
                user_id=user_id,
                role_id=role_id,
                scope=scope,
                resource_id=resource_id,
                assigned_by=assigner_id,
                assigned_at=time.time(),
                expires_at=expires_at,
                is_active=True,
                conditions=conditions or {}
            )
            
            self.user_roles[user_id].append(user_role)
            
            # Clear permission cache for user
            self._clear_user_cache(user_id)
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_user_role_redis(user_role)
            
            logger.info(f"Assigned role {role_id} to user {user_id}")
            return user_role
            
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            raise
    
    async def revoke_role(self, assignment_id: str, revoker_id: str) -> bool:
        """Revoke role assignment"""
        try:
            # Find and deactivate assignment
            for user_id, assignments in self.user_roles.items():
                for assignment in assignments:
                    if assignment.assignment_id == assignment_id:
                        assignment.is_active = False
                        
                        # Clear permission cache
                        self._clear_user_cache(user_id)
                        
                        logger.info(f"Revoked role assignment {assignment_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke role: {e}")
            return False
    
    async def check_permission(self, user_id: str, resource_type: ResourceType,
                             resource_id: str, permission: Permission,
                             session_id: Optional[str] = None) -> bool:
        """Check if user has permission for resource"""
        try:
            # Check cache first
            cache_key = f"{user_id}:{resource_id}:{permission.value}"
            cached_result = self._get_cached_permission(cache_key)
            if cached_result is not None:
                granted, _ = cached_result
                await self._log_access_request(user_id, resource_type, resource_id, 
                                             permission, granted, "cached", session_id)
                return granted
            
            # Evaluate permission
            granted = await self._evaluate_permission(user_id, resource_type, resource_id, permission)
            
            # Cache result
            self._cache_permission(cache_key, granted)
            
            # Log access request
            if self.audit_enabled:
                await self._log_access_request(user_id, resource_type, resource_id,
                                             permission, granted, "evaluated", session_id)
            
            return granted
            
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False  # Default deny
    
    async def _evaluate_permission(self, user_id: str, resource_type: ResourceType,
                                 resource_id: str, permission: Permission) -> bool:
        """Evaluate permission using roles and rules"""
        try:
            # Get user roles
            user_assignments = self.user_roles.get(user_id, [])
            
            # Check each role assignment
            for assignment in user_assignments:
                if not assignment.is_active:
                    continue
                
                # Check if assignment is expired
                if assignment.expires_at and time.time() > assignment.expires_at:
                    assignment.is_active = False
                    continue
                
                # Check scope compatibility
                if not self._check_scope_compatibility(assignment, resource_type, resource_id):
                    continue
                
                # Check role permissions
                role = self.roles.get(assignment.role_id)
                if not role:
                    continue
                
                # Get effective permissions (including inheritance)
                effective_permissions = await self._get_effective_permissions(role)
                
                if permission in effective_permissions:
                    # Check conditional permissions
                    if await self._check_conditions(assignment.conditions, user_id, resource_id):
                        return True
            
            # Check explicit permission rules
            rules = self.permission_rules.get(resource_type, [])
            for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
                if await self._rule_matches(rule, user_id, resource_id, permission):
                    return rule.action == 'allow'
            
            # Default deny
            return not self.default_deny
            
        except Exception as e:
            logger.error(f"Failed to evaluate permission: {e}")
            return False
    
    async def _get_effective_permissions(self, role: Role) -> Set[Permission]:
        """Get effective permissions including inheritance"""
        try:
            effective_permissions = copy.deepcopy(role.permissions)
            
            # Add inherited permissions
            if self.permission_inheritance and role.inherits_from:
                parent_role = self.roles.get(role.inherits_from)
                if parent_role:
                    parent_permissions = await self._get_effective_permissions(parent_role)
                    effective_permissions.update(parent_permissions)
            
            return effective_permissions
            
        except Exception as e:
            logger.error(f"Failed to get effective permissions: {e}")
            return set()
    
    def _check_scope_compatibility(self, assignment: UserRole, 
                                 resource_type: ResourceType, resource_id: str) -> bool:
        """Check if role assignment scope is compatible with resource"""
        if assignment.scope == PermissionScope.GLOBAL:
            return True
        elif assignment.scope == PermissionScope.WORKSPACE:
            # Check if resource belongs to workspace
            return True  # Simplified - would check actual workspace membership
        elif assignment.scope == PermissionScope.PROJECT:
            # Check if resource belongs to project
            return True  # Simplified - would check actual project membership
        elif assignment.scope == PermissionScope.RESOURCE:
            return assignment.resource_id == resource_id
        
        return False
    
    async def _check_conditions(self, conditions: Dict[str, Any], 
                              user_id: str, resource_id: str) -> bool:
        """Check conditional permissions"""
        try:
            if not conditions:
                return True
            
            # Time-based conditions
            if 'time_range' in conditions:
                current_time = time.time()
                time_range = conditions['time_range']
                start_time = time_range.get('start', 0)
                end_time = time_range.get('end', float('inf'))
                if not (start_time <= current_time <= end_time):
                    return False
            
            # IP-based conditions
            if 'allowed_ips' in conditions:
                # Would check actual IP address
                pass
            
            # Resource-specific conditions
            if 'resource_conditions' in conditions:
                # Would check resource-specific conditions
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check conditions: {e}")
            return False
    
    async def _rule_matches(self, rule: PermissionRule, user_id: str,
                          resource_id: str, permission: Permission) -> bool:
        """Check if permission rule matches request"""
        try:
            # Check permission match
            if rule.permission != permission:
                return False
            
            # Check resource match
            if rule.resource_id and rule.resource_id != resource_id:
                return False
            
            # Check user match
            if rule.user_id and rule.user_id != user_id:
                return False
            
            # Check role match
            if rule.role_id:
                user_assignments = self.user_roles.get(user_id, [])
                role_matches = any(a.role_id == rule.role_id and a.is_active 
                                 for a in user_assignments)
                if not role_matches:
                    return False
            
            # Check conditions
            return await self._check_conditions(rule.conditions, user_id, resource_id)
            
        except Exception as e:
            logger.error(f"Failed to check rule match: {e}")
            return False
    
    async def add_permission_rule(self, resource_type: ResourceType,
                                resource_id: Optional[str], permission: Permission,
                                action: str, priority: int = 0,
                                user_id: Optional[str] = None,
                                role_id: Optional[str] = None,
                                conditions: Dict[str, Any] = None) -> PermissionRule:
        """Add explicit permission rule"""
        try:
            rule_id = str(uuid.uuid4())
            
            rule = PermissionRule(
                rule_id=rule_id,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id,
                role_id=role_id,
                permission=permission,
                action=action,
                priority=priority,
                conditions=conditions or {},
                created_at=time.time()
            )
            
            self.permission_rules[resource_type].append(rule)
            
            # Clear relevant caches
            self._clear_permission_cache()
            
            logger.info(f"Added permission rule {rule_id}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to add permission rule: {e}")
            raise
    
    async def get_user_permissions(self, user_id: str, 
                                 scope: PermissionScope = PermissionScope.WORKSPACE,
                                 resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive user permissions"""
        try:
            user_assignments = self.user_roles.get(user_id, [])
            effective_permissions = set()
            role_info = []
            
            for assignment in user_assignments:
                if not assignment.is_active:
                    continue
                
                # Check scope
                if scope != PermissionScope.GLOBAL and assignment.scope != scope:
                    if not (assignment.scope == PermissionScope.GLOBAL):
                        continue
                
                # Check resource
                if resource_id and assignment.resource_id and assignment.resource_id != resource_id:
                    continue
                
                role = self.roles.get(assignment.role_id)
                if role:
                    role_permissions = await self._get_effective_permissions(role)
                    effective_permissions.update(role_permissions)
                    
                    role_info.append({
                        'role_id': role.role_id,
                        'role_name': role.name,
                        'assignment_id': assignment.assignment_id,
                        'scope': assignment.scope.value,
                        'resource_id': assignment.resource_id,
                        'expires_at': assignment.expires_at
                    })
            
            return {
                'user_id': user_id,
                'permissions': [p.value for p in effective_permissions],
                'roles': role_info,
                'scope': scope.value,
                'resource_id': resource_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return {'user_id': user_id, 'permissions': [], 'roles': []}
    
    async def get_resource_permissions(self, resource_type: ResourceType,
                                     resource_id: str) -> Dict[str, Any]:
        """Get all permissions for a resource"""
        try:
            resource_permissions = []
            
            # Get from role assignments
            for user_id, assignments in self.user_roles.items():
                for assignment in assignments:
                    if not assignment.is_active:
                        continue
                    
                    # Check if assignment applies to resource
                    if self._check_scope_compatibility(assignment, resource_type, resource_id):
                        role = self.roles.get(assignment.role_id)
                        if role:
                            permissions = await self._get_effective_permissions(role)
                            resource_permissions.append({
                                'user_id': user_id,
                                'role_name': role.name,
                                'permissions': [p.value for p in permissions],
                                'assignment_id': assignment.assignment_id,
                                'scope': assignment.scope.value
                            })
            
            # Get from explicit rules
            rules = self.permission_rules.get(resource_type, [])
            rule_permissions = []
            for rule in rules:
                if not rule.resource_id or rule.resource_id == resource_id:
                    rule_permissions.append({
                        'rule_id': rule.rule_id,
                        'permission': rule.permission.value,
                        'action': rule.action,
                        'priority': rule.priority,
                        'user_id': rule.user_id,
                        'role_id': rule.role_id
                    })
            
            return {
                'resource_type': resource_type.value,
                'resource_id': resource_id,
                'role_permissions': resource_permissions,
                'rule_permissions': rule_permissions
            }
            
        except Exception as e:
            logger.error(f"Failed to get resource permissions: {e}")
            return {}
    
    async def get_access_audit_log(self, user_id: Optional[str] = None,
                                 resource_id: Optional[str] = None,
                                 limit: int = 100) -> List[AccessRequest]:
        """Get access audit log"""
        try:
            # Filter access log
            filtered_requests = []
            
            for request in reversed(list(self.access_log)):
                if user_id and request.user_id != user_id:
                    continue
                if resource_id and request.resource_id != resource_id:
                    continue
                
                filtered_requests.append(request)
                
                if len(filtered_requests) >= limit:
                    break
            
            return filtered_requests
            
        except Exception as e:
            logger.error(f"Failed to get access audit log: {e}")
            return []
    
    def _get_cached_permission(self, cache_key: str) -> Optional[Tuple[bool, float]]:
        """Get cached permission result"""
        try:
            if cache_key in self.permission_cache:
                result, timestamp = self.permission_cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return result, timestamp
                else:
                    # Cache expired
                    del self.permission_cache[cache_key]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached permission: {e}")
            return None
    
    def _cache_permission(self, cache_key: str, result: bool):
        """Cache permission result"""
        try:
            self.permission_cache[cache_key] = (result, time.time())
            
        except Exception as e:
            logger.error(f"Failed to cache permission: {e}")
    
    def _clear_user_cache(self, user_id: str):
        """Clear permission cache for user"""
        try:
            keys_to_remove = []
            for key in self.permission_cache.keys():
                if key.startswith(f"{user_id}:"):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.permission_cache[key]
                
        except Exception as e:
            logger.error(f"Failed to clear user cache: {e}")
    
    def _clear_permission_cache(self):
        """Clear entire permission cache"""
        try:
            self.permission_cache.clear()
            
        except Exception as e:
            logger.error(f"Failed to clear permission cache: {e}")
    
    async def _log_access_request(self, user_id: str, resource_type: ResourceType,
                                resource_id: str, permission: Permission,
                                granted: bool, reason: str, session_id: Optional[str]):
        """Log access request for auditing"""
        try:
            if not self.audit_enabled:
                return
            
            request = AccessRequest(
                request_id=str(uuid.uuid4()),
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                permission=permission,
                timestamp=time.time(),
                granted=granted,
                reason=reason,
                session_id=session_id
            )
            
            self.access_log.append(request)
            
        except Exception as e:
            logger.error(f"Failed to log access request: {e}")
    
    async def _store_role_redis(self, role: Role):
        """Store role in Redis"""
        try:
            if self.redis_client:
                key = f"role:{role.role_id}"
                # Convert permissions to list for JSON serialization
                role_data = asdict(role)
                role_data['permissions'] = [p.value for p in role.permissions]
                value = json.dumps(role_data, default=str)
                self.redis_client.setex(key, 86400, value)
                
        except Exception as e:
            logger.error(f"Failed to store role in Redis: {e}")
    
    async def _store_user_role_redis(self, user_role: UserRole):
        """Store user role assignment in Redis"""
        try:
            if self.redis_client:
                key = f"user_role:{user_role.assignment_id}"
                value = json.dumps(asdict(user_role), default=str)
                self.redis_client.setex(key, 86400, value)
                
        except Exception as e:
            logger.error(f"Failed to store user role in Redis: {e}")

class RoleBasedAccessManager:
    """High-level role-based access management"""
    
    def __init__(self):
        self.permission_engine = TeamPermissionEngine()
        self.role_templates = self._load_role_templates()
    
    async def setup_workspace_permissions(self, workspace_id: str, owner_id: str) -> Dict[str, Any]:
        """Set up permissions for new workspace"""
        try:
            # Find owner role
            owner_role = None
            for role in self.permission_engine.roles.values():
                if role.name == 'owner' and role.is_system_role:
                    owner_role = role
                    break
            
            if not owner_role:
                raise ValueError("Owner role not found")
            
            # Assign owner role
            await self.permission_engine.assign_role(
                user_id=owner_id,
                role_id=owner_role.role_id,
                assigner_id=owner_id,
                scope=PermissionScope.WORKSPACE,
                resource_id=workspace_id
            )
            
            return {
                'workspace_id': workspace_id,
                'owner_id': owner_id,
                'owner_role_id': owner_role.role_id,
                'status': 'configured'
            }
            
        except Exception as e:
            logger.error(f"Failed to setup workspace permissions: {e}")
            raise
    
    async def invite_user_with_role(self, workspace_id: str, user_id: str,
                                  role_name: str, inviter_id: str) -> bool:
        """Invite user to workspace with specific role"""
        try:
            # Find role by name
            target_role = None
            for role in self.permission_engine.roles.values():
                if role.name == role_name:
                    target_role = role
                    break
            
            if not target_role:
                raise ValueError(f"Role {role_name} not found")
            
            # Check if inviter has permission to assign roles
            can_invite = await self.permission_engine.check_permission(
                user_id=inviter_id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=workspace_id,
                permission=Permission.INVITE_USERS
            )
            
            if not can_invite:
                raise PermissionError("Inviter does not have permission to invite users")
            
            # Assign role
            await self.permission_engine.assign_role(
                user_id=user_id,
                role_id=target_role.role_id,
                assigner_id=inviter_id,
                scope=PermissionScope.WORKSPACE,
                resource_id=workspace_id
            )
            
            logger.info(f"Invited user {user_id} with role {role_name} to workspace {workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invite user with role: {e}")
            return False
    
    async def create_project_role(self, project_id: str, role_name: str,
                                permissions: List[str], creator_id: str) -> Optional[str]:
        """Create project-specific role"""
        try:
            # Convert permission strings to enums
            permission_enums = set()
            for perm_str in permissions:
                try:
                    perm = Permission(perm_str)
                    permission_enums.add(perm)
                except ValueError:
                    logger.warning(f"Invalid permission: {perm_str}")
            
            role = await self.permission_engine.create_custom_role(
                name=f"{role_name}_project_{project_id}",
                description=f"Custom role for project {project_id}",
                permissions=permission_enums,
                creator_id=creator_id
            )
            
            return role.role_id
            
        except Exception as e:
            logger.error(f"Failed to create project role: {e}")
            return None
    
    def _load_role_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined role templates"""
        return {
            'content_creator': {
                'description': 'Content creation specialist',
                'permissions': [
                    Permission.READ.value, Permission.WRITE.value,
                    Permission.CREATE_CONTENT.value, Permission.EDIT_CONTENT.value,
                    Permission.COMMENT.value, Permission.REQUEST_APPROVAL.value
                ]
            },
            'quality_reviewer': {
                'description': 'Quality assurance reviewer',
                'permissions': [
                    Permission.READ.value, Permission.COMMENT.value,
                    Permission.APPROVE.value, Permission.REJECT.value,
                    Permission.REQUEST_CHANGES.value
                ]
            },
            'project_manager': {
                'description': 'Project management role',
                'permissions': [
                    Permission.READ.value, Permission.WRITE.value,
                    Permission.INVITE_USERS.value, Permission.ASSIGN_ROLES.value,
                    Permission.VIEW_ANALYTICS.value, Permission.CONFIGURE_WORKFLOWS.value
                ]
            }
        }

# Module exports
__all__ = [
    'TeamPermissionEngine',
    'RoleBasedAccessManager',
    'Role',
    'UserRole',
    'PermissionRule',
    'AccessRequest',
    'Permission',
    'ResourceType',
    'PermissionScope'
]