"""Access Control and Permission Management System

Advanced role-based access control (RBAC) and attribute-based access control (ABAC)
system for content governance and security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""import logging
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
from abc import ABC, abstractmethod

from ...core.base import BaseManager
from ...core.exceptions import AccessError, ValidationError
from ...core.database import DatabaseManager
from ...core.cache import CacheManager


class Permission(Enum):
    """System permissions"""    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    SHARE = "share"
    EXPORT = "export"
    IMPORT = "import"
    MODIFY_PERMISSIONS = "modify_permissions"
    VIEW_AUDIT = "view_audit"


class AccessAction(Enum):
    """Access control actions"""    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    AUDIT_ONLY = "audit_only"


class RoleLevel(Enum):
    """Role hierarchy levels"""    SYSTEM = "system"
    ORGANIZATION = "organization"
    PROJECT = "project"
    CONTENT = "content"


@dataclass
class AccessPolicy:
    """Access control policy definition"""    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    action: AccessAction = AccessAction.ALLOW
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """Role definition with permissions"""    role_id: str
    name: str
    description: str
    permissions: Set[Permission]
    level: RoleLevel
    parent_role_id: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """User with access control information"""    user_id: str
    username: str
    email: str
    roles: Set[str]  # Role IDs
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """Access request for audit and decision"""    request_id: str
    user_id: str
    resource_id: str
    resource_type: str
    permission: Permission
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    decision: Optional[AccessAction] = None
    decision_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessLog:
    """Access log entry for auditing"""    log_id: str
    user_id: str
    resource_id: str
    permission: Permission
    action: AccessAction
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyEngine:
    """    Policy evaluation engine for access control decisions
    
    Evaluates access policies using both RBAC and ABAC models
    to make authorization decisions.
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_policies(
        self,
        policies: List[AccessPolicy],
        user: User,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Dict[str, Any]
    ) -> Tuple[AccessAction, str]:
        """        Evaluate access policies for a request
        
        Args:
            policies: List of applicable policies
            user: User making the request
            resource_id: Resource being accessed
            resource_type: Type of resource
            permission: Permission being requested
            context: Request context
            
        Returns:
            Tuple[AccessAction, str]: Decision and reason
        """        try:
            # Sort policies by priority (higher priority first)
            sorted_policies = sorted(policies, key=lambda p: p.priority, reverse=True)
            
            for policy in sorted_policies:
                if not policy.enabled:
                    continue
                
                # Evaluate policy rules
                if self._evaluate_policy_rules(policy, user, resource_id, resource_type, permission, context):
                    return policy.action, f"Policy {policy.name} matched"
            
            # Default deny if no policy matches
            return AccessAction.DENY, "No matching policy found"
            
        except Exception as e:
            self.logger.error(f"Error evaluating policies: {e}")
            return AccessAction.DENY, f"Policy evaluation error: {e}"
    
    def _evaluate_policy_rules(
        self,
        policy: AccessPolicy,
        user: User,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate individual policy rules"""        for rule in policy.rules:
            if not self._evaluate_rule(rule, user, resource_id, resource_type, permission, context):
                return False
        return True
    
    def _evaluate_rule(
        self,
        rule: Dict[str, Any],
        user: User,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single rule"""        rule_type = rule.get("type")
        
        if rule_type == "user_attribute":
            return self._evaluate_user_attribute_rule(rule, user)
        elif rule_type == "resource_type":
            return self._evaluate_resource_type_rule(rule, resource_type)
        elif rule_type == "permission":
            return self._evaluate_permission_rule(rule, permission)
        elif rule_type == "context":
            return self._evaluate_context_rule(rule, context)
        elif rule_type == "time":
            return self._evaluate_time_rule(rule, context)
        else:
            self.logger.warning(f"Unknown rule type: {rule_type}")
            return False
    
    def _evaluate_user_attribute_rule(self, rule: Dict[str, Any], user: User) -> bool:
        """Evaluate user attribute rule"""        attribute = rule.get("attribute")
        operator = rule.get("operator", "eq")
        value = rule.get("value")
        
        user_value = user.attributes.get(attribute)
        
        if operator == "eq":
            return user_value == value
        elif operator == "in":
            return user_value in value if isinstance(value, list) else False
        elif operator == "contains":
            return value in str(user_value) if user_value else False
        
        return False
    
    def _evaluate_resource_type_rule(self, rule: Dict[str, Any], resource_type: str) -> bool:
        """Evaluate resource type rule"""        allowed_types = rule.get("allowed_types", [])
        return resource_type in allowed_types
    
    def _evaluate_permission_rule(self, rule: Dict[str, Any], permission: Permission) -> bool:
        """Evaluate permission rule"""        allowed_permissions = rule.get("allowed_permissions", [])
        return permission.value in allowed_permissions
    
    def _evaluate_context_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate context rule"""        required_context = rule.get("required_context", {})
        
        for key, expected_value in required_context.items():
            actual_value = context.get(key)
            if actual_value != expected_value:
                return False
        
        return True
    
    def _evaluate_time_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate time-based rule"""        current_time = datetime.utcnow()
        
        # Check time range
        start_time = rule.get("start_time")
        end_time = rule.get("end_time")
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time) if isinstance(start_time, str) else start_time
            if current_time < start_dt:
                return False
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time) if isinstance(end_time, str) else end_time
            if current_time > end_dt:
                return False
        
        # Check allowed hours
        allowed_hours = rule.get("allowed_hours")
        if allowed_hours:
            current_hour = current_time.hour
            if current_hour not in allowed_hours:
                return False
        
        return True


class RoleManager:
    """    Role management system for RBAC
    
    Manages roles, role hierarchies, and permission assignments
    with support for inheritance and delegation.
    """    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.role_hierarchy: Dict[str, Set[str]] = {}  # parent -> children
        self.logger = logging.getLogger(__name__)
    
    def create_role(
        self,
        role_id: str,
        name: str,
        description: str,
        permissions: Set[Permission],
        level: RoleLevel,
        parent_role_id: Optional[str] = None
    ) -> Role:
        """Create a new role"""        if role_id in self.roles:
            raise AccessError(f"Role {role_id} already exists")
        
        # Validate parent role
        if parent_role_id and parent_role_id not in self.roles:
            raise AccessError(f"Parent role {parent_role_id} not found")
        
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            level=level,
            parent_role_id=parent_role_id
        )
        
        self.roles[role_id] = role
        
        # Update hierarchy
        if parent_role_id:
            if parent_role_id not in self.role_hierarchy:
                self.role_hierarchy[parent_role_id] = set()
            self.role_hierarchy[parent_role_id].add(role_id)
        
        return role
    
    def get_effective_permissions(self, role_id: str) -> Set[Permission]:
        """Get effective permissions for a role including inherited"""        if role_id not in self.roles:
            return set()
        
        role = self.roles[role_id]
        permissions = role.permissions.copy()
        
        # Add inherited permissions
        if role.parent_role_id:
            parent_permissions = self.get_effective_permissions(role.parent_role_id)
            permissions.update(parent_permissions)
        
        return permissions
    
    def get_user_permissions(self, user_roles: Set[str]) -> Set[Permission]:
        """Get effective permissions for a user based on their roles"""        all_permissions = set()
        
        for role_id in user_roles:
            role_permissions = self.get_effective_permissions(role_id)
            all_permissions.update(role_permissions)
        
        return all_permissions
    
    def has_permission(self, user_roles: Set[str], permission: Permission) -> bool:
        """Check if user has a specific permission"""        user_permissions = self.get_user_permissions(user_roles)
        return permission in user_permissions or Permission.ADMIN in user_permissions
    
    def get_role_hierarchy(self, role_id: str) -> List[str]:
        """Get complete role hierarchy for a role"""        hierarchy = [role_id]
        
        if role_id in self.roles:
            parent_id = self.roles[role_id].parent_role_id
            if parent_id:
                hierarchy.extend(self.get_role_hierarchy(parent_id))
        
        return hierarchy


class AccessController(BaseManager):
    """    Central access control management system
    
    Provides comprehensive access control using RBAC and ABAC models
    with policy evaluation, audit logging, and permission management.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the access controller"""        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(config)
        self.cache_manager = CacheManager(config)
        self.policy_engine = PolicyEngine()
        self.role_manager = RoleManager()
        
        # Access control storage
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.access_requests: List[AccessRequest] = []
        self.access_logs: List[AccessLog] = []
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "allowed_requests": 0,
            "denied_requests": 0,
            "policy_evaluations": 0
        }
    
    async def initialize(self) -> None:
        """Initialize the access controller"""        try:
            await self._load_users()
            await self._load_roles()
            await self._load_policies()
            await self._create_default_roles()
            
            self.logger.info("Access controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize access controller: {e}")
            raise AccessError(f"Access controller initialization failed: {e}")
    
    async def check_access(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Check if user has access to perform action on resource
        
        Args:
            user_id: ID of user making request
            resource_id: ID of resource being accessed
            resource_type: Type of resource
            permission: Permission being requested
            context: Additional context for decision
            
        Returns:
            bool: True if access allowed, False otherwise
        """        try:
            # Create access request
            request = AccessRequest(
                request_id=f"access_{user_id}_{resource_id}_{permission.value}_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type,
                permission=permission,
                context=context or {}
            )
            
            self.access_requests.append(request)
            
            # Get user
            user = self.users.get(user_id)
            if not user or not user.is_active:
                request.decision = AccessAction.DENY
                request.decision_reason = "User not found or inactive"
                await self._log_access(request, AccessAction.DENY)
                return False
            
            # Check role-based permissions first
            if self.role_manager.has_permission(user.roles, permission):
                request.decision = AccessAction.ALLOW
                request.decision_reason = "Role-based permission granted"
                await self._log_access(request, AccessAction.ALLOW)
                return True
            
            # Evaluate policies
            applicable_policies = await self._get_applicable_policies(
                user, resource_id, resource_type, permission, context or {}
            )
            
            decision, reason = self.policy_engine.evaluate_policies(
                applicable_policies, user, resource_id, resource_type, permission, context or {}
            )
            
            request.decision = decision
            request.decision_reason = reason
            
            # Log access
            await self._log_access(request, decision)
            
            # Update metrics
            self.metrics["total_requests"] += 1
            self.metrics["policy_evaluations"] += len(applicable_policies)
            
            if decision == AccessAction.ALLOW:
                self.metrics["allowed_requests"] += 1
                return True
            else:
                self.metrics["denied_requests"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking access for user {user_id}: {e}")
            return False
    
    async def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: Set[str],
        attributes: Optional[Dict[str, Any]] = None
    ) -> User:
        """        Create a new user
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: User email
            roles: Set of role IDs
            attributes: User attributes
            
        Returns:
            User: Created user object
        """        try:
            if user_id in self.users:
                raise AccessError(f"User {user_id} already exists")
            
            # Validate roles
            for role_id in roles:
                if role_id not in self.role_manager.roles:
                    raise AccessError(f"Role {role_id} not found")
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles,
                attributes=attributes or {}
            )
            
            self.users[user_id] = user
            
            self.logger.info(f"Created user: {user_id}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error creating user {user_id}: {e}")
            raise AccessError(f"User creation failed: {e}")
    
    async def assign_role(self, user_id: str, role_id: str) -> bool:
        """        Assign a role to a user
        
        Args:
            user_id: User ID
            role_id: Role ID to assign
            
        Returns:
            bool: True if role assigned successfully
        """        try:
            user = self.users.get(user_id)
            if not user:
                raise AccessError(f"User {user_id} not found")
            
            if role_id not in self.role_manager.roles:
                raise AccessError(f"Role {role_id} not found")
            
            user.roles.add(role_id)
            
            self.logger.info(f"Assigned role {role_id} to user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning role: {e}")
            return False
    
    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """        Revoke a role from a user
        
        Args:
            user_id: User ID
            role_id: Role ID to revoke
            
        Returns:
            bool: True if role revoked successfully
        """        try:
            user = self.users.get(user_id)
            if not user:
                raise AccessError(f"User {user_id} not found")
            
            user.roles.discard(role_id)
            
            self.logger.info(f"Revoked role {role_id} from user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error revoking role: {e}")
            return False
    
    async def create_policy(self, policy: AccessPolicy) -> bool:
        """        Create a new access policy
        
        Args:
            policy: AccessPolicy to create
            
        Returns:
            bool: True if policy created successfully
        """        try:
            # Validate policy
            await self._validate_policy(policy)
            
            self.policies[policy.policy_id] = policy
            
            self.logger.info(f"Created access policy: {policy.policy_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating policy {policy.policy_id}: {e}")
            raise AccessError(f"Policy creation failed: {e}")
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """        Get effective permissions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Set[Permission]: User's effective permissions
        """        user = self.users.get(user_id)
        if not user:
            return set()
        
        return self.role_manager.get_user_permissions(user.roles)
    
    async def get_access_logs(
        self,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        permission: Optional[Permission] = None,
        action: Optional[AccessAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AccessLog]:
        """        Get access logs with optional filtering
        
        Args:
            user_id: Filter by user ID
            resource_id: Filter by resource ID
            permission: Filter by permission
            action: Filter by action
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List[AccessLog]: Filtered access logs
        """        filtered_logs = self.access_logs.copy()
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        
        if resource_id:
            filtered_logs = [log for log in filtered_logs if log.resource_id == resource_id]
        
        if permission:
            filtered_logs = [log for log in filtered_logs if log.permission == permission]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        return sorted(filtered_logs, key=lambda log: log.timestamp, reverse=True)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get access control metrics"""        return {
            **self.metrics,
            "total_users": len(self.users),
            "total_roles": len(self.role_manager.roles),
            "total_policies": len(self.policies),
            "active_users": len([u for u in self.users.values() if u.is_active]),
            "access_rate": (
                (self.metrics["allowed_requests"] / self.metrics["total_requests"] * 100)
                if self.metrics["total_requests"] > 0 else 0
            )
        }
    
    async def _get_applicable_policies(
        self,
        user: User,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Dict[str, Any]
    ) -> List[AccessPolicy]:
        """Get policies applicable to the access request"""        applicable = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            # Simple applicability check - can be enhanced
            applicable.append(policy)
        
        return applicable
    
    async def _log_access(self, request: AccessRequest, decision: AccessAction) -> None:
        """Log access decision"""        log_entry = AccessLog(
            log_id=f"log_{request.request_id}",
            user_id=request.user_id,
            resource_id=request.resource_id,
            permission=request.permission,
            action=decision,
            timestamp=request.timestamp,
            metadata={
                "resource_type": request.resource_type,
                "decision_reason": request.decision_reason,
                "context": request.context
            }
        )
        
        self.access_logs.append(log_entry)
    
    async def _validate_policy(self, policy: AccessPolicy) -> None:
        """Validate access policy configuration"""        if not policy.policy_id or not policy.name:
            raise ValidationError("Policy ID and name are required")
        
        if not policy.rules:
            raise ValidationError("Policy must have at least one rule")
    
    async def _create_default_roles(self) -> None:
        """Create default system roles"""        # Create system admin role
        self.role_manager.create_role(
            role_id="system_admin",
            name="System Administrator",
            description="Full system access",
            permissions={Permission.ADMIN},
            level=RoleLevel.SYSTEM
        )
        
        # Create content owner role
        self.role_manager.create_role(
            role_id="content_owner",
            name="Content Owner",
            description="Full access to owned content",
            permissions={Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE},
            level=RoleLevel.CONTENT
        )
        
        # Create viewer role
        self.role_manager.create_role(
            role_id="viewer",
            name="Viewer",
            description="Read-only access",
            permissions={Permission.READ},
            level=RoleLevel.CONTENT
        )
    
    async def _load_users(self) -> None:
        """Load users from database"""        try:
            logger.info("Loading users and permissions from database")
            
            # Simulate database query for users
            db_users = [
                {
                    "user_id": "admin_user",
                    "username": "admin", 
                    "roles": ["system_admin", "content_manager"],
                    "permissions": ["admin", "read", "write", "delete"],
                    "attributes": {"department": "it", "clearance_level": "high"},
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": datetime.utcnow().isoformat(),
                    "active": True
                },
                {
                    "user_id": "content_creator", 
                    "username": "creator01",
                    "roles": ["content_creator"],
                    "permissions": ["read", "write", "share"],
                    "attributes": {"department": "content", "clearance_level": "medium"},
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "active": True
                },
                {
                    "user_id": "viewer_user",
                    "username": "viewer01", 
                    "roles": ["content_viewer"],
                    "permissions": ["read"],
                    "attributes": {"department": "marketing", "clearance_level": "low"},
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "active": True
                }
            ]
            
            # Load users into memory
            for user_data in db_users:
                user_id = user_data["user_id"]
                self.users[user_id] = user_data
                
                # Cache user permissions for quick access
                self.user_permissions[user_id] = set(user_data["permissions"])
                
                logger.debug(f"Loaded user {user_id} with roles: {user_data['roles']}")
            
            logger.info(f"Loaded {len(db_users)} users from database")
            
        except Exception as e:
            logger.error(f"Error loading users from database: {str(e)}")
            # Fall back to creating default admin user
            await self._create_default_admin_user()
    
    async def _load_roles(self) -> None:
        """Load roles from database"""        try:
            logger.info("Loading roles and role permissions from database")
            
            # Simulate database query for roles
            db_roles = [
                {
                    "role_id": "system_admin",
                    "name": "System Administrator",
                    "description": "Full system access and management capabilities",
                    "permissions": ["admin", "read", "write", "delete", "execute", "modify_permissions", "view_audit"],
                    "inherits_from": [],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "role_id": "content_manager", 
                    "name": "Content Manager",
                    "description": "Manage and moderate content across platforms",
                    "permissions": ["read", "write", "delete", "share", "export"],
                    "inherits_from": ["content_creator"],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "role_id": "content_creator",
                    "name": "Content Creator", 
                    "description": "Create and edit content",
                    "permissions": ["read", "write", "share"],
                    "inherits_from": ["content_viewer"],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "role_id": "content_viewer",
                    "name": "Content Viewer",
                    "description": "View content with read-only access", 
                    "permissions": ["read"],
                    "inherits_from": [],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "role_id": "guest",
                    "name": "Guest User",
                    "description": "Limited access for guest users",
                    "permissions": [],
                    "inherits_from": [],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            # Load roles into memory  
            for role_data in db_roles:
                role_id = role_data["role_id"]
                self.roles[role_id] = role_data
                
                # Build role hierarchy and effective permissions
                effective_permissions = set(role_data["permissions"])
                
                # Inherit permissions from parent roles
                for parent_role_id in role_data["inherits_from"]:
                    if parent_role_id in self.roles:
                        parent_permissions = set(self.roles[parent_role_id]["permissions"])
                        effective_permissions.update(parent_permissions)
                
                self.role_permissions[role_id] = effective_permissions
                
                logger.debug(f"Loaded role {role_id} with {len(effective_permissions)} effective permissions")
            
            logger.info(f"Loaded {len(db_roles)} roles from database")
            
        except Exception as e:
            logger.error(f"Error loading roles from database: {str(e)}")
            # Fall back to creating basic roles
            await self._create_default_roles()
    
    async def _load_policies(self) -> None:
        """Load policies from database"""        try:
            logger.info("Loading access control policies from database")
            
            # Simulate database query for access control policies
            db_policies = [
                {
                    "policy_id": "time_based_access",
                    "name": "Time-based Access Control",
                    "description": "Restrict access based on time of day and day of week",
                    "type": "conditional",
                    "conditions": {
                        "time_restrictions": {
                            "allowed_hours": {"start": "09:00", "end": "18:00"},
                            "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                            "timezone": "UTC"
                        }
                    },
                    "actions": {
                        "allow": ["read"],
                        "deny": ["write", "delete"],
                        "conditional": ["execute"]
                    },
                    "priority": 100,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "policy_id": "location_based_access",
                    "name": "Location-based Access Control",
                    "description": "Restrict access based on user location and IP address",
                    "type": "conditional", 
                    "conditions": {
                        "location_restrictions": {
                            "allowed_countries": ["US", "CA", "GB", "DE", "FR"],
                            "blocked_ips": [],
                            "require_vpn": False
                        }
                    },
                    "actions": {
                        "allow": ["read", "write"],
                        "deny": ["admin", "delete"],
                        "conditional": ["export"]
                    },
                    "priority": 90,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "policy_id": "content_sensitivity_access",
                    "name": "Content Sensitivity Access Control",
                    "description": "Control access based on content classification and user clearance",
                    "type": "conditional",
                    "conditions": {
                        "sensitivity_mapping": {
                            "public": ["low", "medium", "high"],
                            "internal": ["medium", "high"], 
                            "confidential": ["high"],
                            "restricted": ["high"]
                        }
                    },
                    "actions": {
                        "allow": ["read"],
                        "deny": [],
                        "conditional": ["write", "share", "export"]
                    },
                    "priority": 80,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            # Load policies into memory
            for policy_data in db_policies:
                policy_id = policy_data["policy_id"]
                self.access_policies[policy_id] = policy_data
                
                logger.debug(f"Loaded access policy {policy_id} with priority {policy_data['priority']}")
            
            # Sort policies by priority (higher number = higher priority)
            self.policy_order = sorted(
                self.access_policies.keys(),
                key=lambda pid: self.access_policies[pid]["priority"],
                reverse=True
            )
            
            logger.info(f"Loaded {len(db_policies)} access control policies from database")
            
        except Exception as e:
            logger.error(f"Error loading access policies from database: {str(e)}")
            # Fall back to creating default policies
            await self._create_default_policies()


class PermissionManager:
    """    Permission management utilities
    
    Provides helper functions for permission checking and management
    across the platform.
    """    
    def __init__(self, access_controller: AccessController):
        self.access_controller = access_controller
        self.logger = logging.getLogger(__name__)
    
    async def require_permission(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        permission: Permission,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """        Require permission or raise access error
        
        Args:
            user_id: User ID
            resource_id: Resource ID
            resource_type: Resource type
            permission: Required permission
            context: Additional context
            
        Raises:
            AccessError: If permission denied
        """        has_access = await self.access_controller.check_access(
            user_id, resource_id, resource_type, permission, context
        )
        
        if not has_access:
            raise AccessError(
                f"User {user_id} does not have {permission.value} permission "
                f"for {resource_type} {resource_id}"
            )
    
    async def check_resource_ownership(
        self,
        user_id: str,
        resource_id: str,
        resource_metadata: Dict[str, Any]
    ) -> bool:
        """        Check if user owns the resource
        
        Args:
            user_id: User ID
            resource_id: Resource ID
            resource_metadata: Resource metadata
            
        Returns:
            bool: True if user owns the resource
        """        owner_id = resource_metadata.get("owner_id")
        return owner_id == user_id
    
    async def get_accessible_resources(
        self,
        user_id: str,
        resource_type: str,
        permission: Permission,
        resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """        Filter resources based on user permissions
        
        Args:
            user_id: User ID
            resource_type: Type of resources
            permission: Required permission
            resources: List of resources to filter
            
        Returns:
            List[Dict]: Accessible resources
        """        accessible = []
        
        for resource in resources:
            resource_id = resource.get("id", resource.get("resource_id"))
            if resource_id:
                has_access = await self.access_controller.check_access(
                    user_id, resource_id, resource_type, permission
                )
                if has_access:
                    accessible.append(resource)
        
        return accessible
