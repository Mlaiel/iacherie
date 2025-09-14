#!/usr/bin/env python3
"""
🛡️ Access Control Engine - Enterprise Security Module
=====================================================

Ultra-secure access control with RBAC, ABAC, and dynamic policy evaluation
for enterprise-grade authorization and permissions management.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + Policy + Compliance
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

import aioredis
from cryptography.fernet import Fernet

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
    MEDIA = "media"
    DATA = "data"

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
    DOWNLOAD = "download"
    UPLOAD = "upload"

class PermissionEffect(Enum):
    """Permission effect types"""
    ALLOW = "allow"
    DENY = "deny"

class PolicyType(Enum):
    """Policy evaluation types"""
    RBAC = "rbac"
    ABAC = "abac"
    HYBRID = "hybrid"

class AccessDecision(Enum):
    """Access control decision types"""
    PERMIT = "permit"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    INDETERMINATE = "indeterminate"

@dataclass
class Permission:
    """Individual permission definition"""
    permission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    resource_type: ResourceType = ResourceType.CONTENT
    action: ActionType = ActionType.READ
    effect: PermissionEffect = PermissionEffect.ALLOW
    resource_pattern: str = "*"  # Resource pattern matching
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100  # Higher numbers = higher priority
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Role:
    """Role definition with permissions and hierarchy"""
    role_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    permissions: Set[str] = field(default_factory=set)  # Permission IDs
    parent_roles: Set[str] = field(default_factory=set)  # Parent role IDs
    child_roles: Set[str] = field(default_factory=set)   # Child role IDs
    is_system_role: bool = False
    max_users: Optional[int] = None
    resource_scope: Optional[str] = None  # Resource scope restriction
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    location_restrictions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserRoleAssignment:
    """User role assignment with constraints"""
    assignment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    role_id: str = ""
    resource_scope: Optional[str] = None  # Specific resource or pattern
    granted_by: str = ""
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Policy:
    """Access control policy definition"""
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policy_type: PolicyType = PolicyType.RBAC
    target: Dict[str, Any] = field(default_factory=dict)  # Target conditions
    rules: List[Dict[str, Any]] = field(default_factory=list)  # Policy rules
    effect: PermissionEffect = PermissionEffect.ALLOW
    priority: int = 100
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityContext:
    """Security context for access control evaluation"""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    request_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_attributes: Dict[str, Any] = field(default_factory=dict)
    environment_attributes: Dict[str, Any] = field(default_factory=dict)
    resource_attributes: Dict[str, Any] = field(default_factory=dict)
    action_attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessRequest:
    """Access control request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    resource_type: ResourceType = ResourceType.CONTENT
    resource_id: str = ""
    action: ActionType = ActionType.READ
    context: Optional[SecurityContext] = None
    additional_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AccessResponse:
    """Access control response"""
    request_id: str
    decision: AccessDecision
    user_id: str
    resource_type: ResourceType
    resource_id: str
    action: ActionType
    reason: str = ""
    applicable_policies: List[str] = field(default_factory=list)
    evaluation_time_ms: float = 0.0
    cached: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

class RBACEngine:
    """
    Role-Based Access Control engine.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.role_cache: Dict[str, Role] = {}
        self.permission_cache: Dict[str, Permission] = {}
        
    async def initialize(self) -> None:
        """Initialize RBAC engine"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("RBAC engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RBAC engine: {e}")
            raise

    async def create_role(self, role: Role) -> bool:
        """Create a new role"""
        try:
            await self._store_role(role)
            self.role_cache[role.role_id] = role
            logger.info(f"Created role: {role.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            return False

    async def create_permission(self, permission: Permission) -> bool:
        """Create a new permission"""
        try:
            await self._store_permission(permission)
            self.permission_cache[permission.permission_id] = permission
            logger.info(f"Created permission: {permission.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create permission: {e}")
            return False

    async def assign_role_to_user(self, assignment: UserRoleAssignment) -> bool:
        """Assign role to user"""
        try:
            await self._store_user_role_assignment(assignment)
            logger.info(f"Assigned role {assignment.role_id} to user {assignment.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            return False

    async def evaluate_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType,
        context: Optional[SecurityContext] = None
    ) -> AccessDecision:
        """Evaluate access using RBAC"""
        try:
            # Get user roles
            user_roles = await self._get_user_roles(user_id)
            if not user_roles:
                return AccessDecision.DENY
            
            # Check permissions for each role
            for role_id in user_roles:
                role = await self._get_role(role_id)
                if not role or not role.is_active:
                    continue
                
                # Check role permissions
                for permission_id in role.permissions:
                    permission = await self._get_permission(permission_id)
                    if not permission or not permission.is_active:
                        continue
                    
                    # Check if permission matches request
                    if (permission.resource_type == resource_type and
                        permission.action == action and
                        self._match_resource_pattern(resource_id, permission.resource_pattern)):
                        
                        # Evaluate conditions
                        if await self._evaluate_permission_conditions(permission, context):
                            if permission.effect == PermissionEffect.ALLOW:
                                return AccessDecision.PERMIT
                            else:
                                return AccessDecision.DENY
            
            return AccessDecision.DENY
            
        except Exception as e:
            logger.error(f"RBAC evaluation failed: {e}")
            return AccessDecision.INDETERMINATE

    def _match_resource_pattern(self, resource_id: str, pattern: str) -> bool:
        """Match resource ID against pattern"""
        try:
            if pattern == "*":
                return True
            elif pattern.endswith("*"):
                return resource_id.startswith(pattern[:-1])
            elif pattern.startswith("*"):
                return resource_id.endswith(pattern[1:])
            else:
                return resource_id == pattern
        except Exception:
            return False

    async def _evaluate_permission_conditions(
        self,
        permission: Permission,
        context: Optional[SecurityContext]
    ) -> bool:
        """Evaluate permission conditions"""
        try:
            if not permission.conditions or not context:
                return True
            
            # Time-based conditions
            if "time_range" in permission.conditions:
                time_range = permission.conditions["time_range"]
                current_hour = context.request_time.hour
                
                if not (time_range.get("start", 0) <= current_hour <= time_range.get("end", 23)):
                    return False
            
            # IP-based conditions
            if "allowed_ips" in permission.conditions:
                allowed_ips = permission.conditions["allowed_ips"]
                if context.ip_address not in allowed_ips:
                    return False
            
            # User attribute conditions
            if "user_attributes" in permission.conditions:
                required_attrs = permission.conditions["user_attributes"]
                for attr, value in required_attrs.items():
                    if context.user_attributes.get(attr) != value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    async def _store_role(self, role: Role) -> None:
        """Store role in Redis"""
        try:
            role_data = {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "permissions": list(role.permissions),
                "parent_roles": list(role.parent_roles),
                "child_roles": list(role.child_roles),
                "is_system_role": role.is_system_role,
                "max_users": role.max_users,
                "resource_scope": role.resource_scope,
                "time_restrictions": role.time_restrictions,
                "location_restrictions": role.location_restrictions,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat(),
                "is_active": role.is_active,
                "metadata": role.metadata
            }
            
            await self.redis.setex(
                f"rbac_role:{role.role_id}",
                86400 * 30,  # 30 days
                json.dumps(role_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store role: {e}")
            raise

    async def _store_permission(self, permission: Permission) -> None:
        """Store permission in Redis"""
        try:
            permission_data = {
                "permission_id": permission.permission_id,
                "name": permission.name,
                "description": permission.description,
                "resource_type": permission.resource_type.value,
                "action": permission.action.value,
                "effect": permission.effect.value,
                "resource_pattern": permission.resource_pattern,
                "conditions": permission.conditions,
                "priority": permission.priority,
                "created_at": permission.created_at.isoformat(),
                "updated_at": permission.updated_at.isoformat(),
                "is_active": permission.is_active,
                "metadata": permission.metadata
            }
            
            await self.redis.setex(
                f"rbac_permission:{permission.permission_id}",
                86400 * 30,  # 30 days
                json.dumps(permission_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store permission: {e}")
            raise

    async def _store_user_role_assignment(self, assignment: UserRoleAssignment) -> None:
        """Store user role assignment"""
        try:
            assignment_data = {
                "assignment_id": assignment.assignment_id,
                "user_id": assignment.user_id,
                "role_id": assignment.role_id,
                "resource_scope": assignment.resource_scope,
                "granted_by": assignment.granted_by,
                "granted_at": assignment.granted_at.isoformat(),
                "expires_at": assignment.expires_at.isoformat() if assignment.expires_at else None,
                "is_active": assignment.is_active,
                "conditions": assignment.conditions,
                "metadata": assignment.metadata
            }
            
            # Store assignment
            await self.redis.setex(
                f"rbac_assignment:{assignment.assignment_id}",
                86400 * 365,  # 1 year
                json.dumps(assignment_data, default=str)
            )
            
            # Add to user role index
            await self.redis.sadd(f"user_roles:{assignment.user_id}", assignment.role_id)
            
        except Exception as e:
            logger.error(f"Failed to store user role assignment: {e}")
            raise

    async def _get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        try:
            # Check cache first
            if role_id in self.role_cache:
                return self.role_cache[role_id]
            
            # Load from Redis
            role_data = await self.redis.get(f"rbac_role:{role_id}")
            if not role_data:
                return None
            
            role_dict = json.loads(role_data)
            
            role = Role(
                role_id=role_dict["role_id"],
                name=role_dict["name"],
                description=role_dict["description"],
                permissions=set(role_dict["permissions"]),
                parent_roles=set(role_dict["parent_roles"]),
                child_roles=set(role_dict["child_roles"]),
                is_system_role=role_dict["is_system_role"],
                max_users=role_dict["max_users"],
                resource_scope=role_dict["resource_scope"],
                time_restrictions=role_dict["time_restrictions"],
                location_restrictions=role_dict["location_restrictions"],
                created_at=datetime.fromisoformat(role_dict["created_at"]),
                updated_at=datetime.fromisoformat(role_dict["updated_at"]),
                is_active=role_dict["is_active"],
                metadata=role_dict["metadata"]
            )
            
            # Cache role
            self.role_cache[role_id] = role
            
            return role
            
        except Exception as e:
            logger.error(f"Failed to get role {role_id}: {e}")
            return None

    async def _get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID"""
        try:
            # Check cache first
            if permission_id in self.permission_cache:
                return self.permission_cache[permission_id]
            
            # Load from Redis
            permission_data = await self.redis.get(f"rbac_permission:{permission_id}")
            if not permission_data:
                return None
            
            permission_dict = json.loads(permission_data)
            
            permission = Permission(
                permission_id=permission_dict["permission_id"],
                name=permission_dict["name"],
                description=permission_dict["description"],
                resource_type=ResourceType(permission_dict["resource_type"]),
                action=ActionType(permission_dict["action"]),
                effect=PermissionEffect(permission_dict["effect"]),
                resource_pattern=permission_dict["resource_pattern"],
                conditions=permission_dict["conditions"],
                priority=permission_dict["priority"],
                created_at=datetime.fromisoformat(permission_dict["created_at"]),
                updated_at=datetime.fromisoformat(permission_dict["updated_at"]),
                is_active=permission_dict["is_active"],
                metadata=permission_dict["metadata"]
            )
            
            # Cache permission
            self.permission_cache[permission_id] = permission
            
            return permission
            
        except Exception as e:
            logger.error(f"Failed to get permission {permission_id}: {e}")
            return None

    async def _get_user_roles(self, user_id: str) -> List[str]:
        """Get roles assigned to user"""
        try:
            role_ids = await self.redis.smembers(f"user_roles:{user_id}")
            return [role_id.decode() for role_id in role_ids]
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class ABACEngine:
    """
    Attribute-Based Access Control engine.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.policy_cache: Dict[str, Policy] = {}
        
    async def initialize(self) -> None:
        """Initialize ABAC engine"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("ABAC engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ABAC engine: {e}")
            raise

    async def create_policy(self, policy: Policy) -> bool:
        """Create a new ABAC policy"""
        try:
            await self._store_policy(policy)
            self.policy_cache[policy.policy_id] = policy
            logger.info(f"Created ABAC policy: {policy.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ABAC policy: {e}")
            return False

    async def evaluate_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType,
        context: SecurityContext
    ) -> Tuple[AccessDecision, List[str]]:
        """Evaluate access using ABAC policies"""
        try:
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(
                user_id, resource_type, resource_id, action, context
            )
            
            if not applicable_policies:
                return AccessDecision.NOT_APPLICABLE, []
            
            # Evaluate policies in priority order
            policies_evaluated = []
            for policy in sorted(applicable_policies, key=lambda p: p.priority, reverse=True):
                policies_evaluated.append(policy.policy_id)
                
                # Evaluate policy rules
                if await self._evaluate_policy_rules(policy, context):
                    if policy.effect == PermissionEffect.ALLOW:
                        return AccessDecision.PERMIT, policies_evaluated
                    else:
                        return AccessDecision.DENY, policies_evaluated
            
            return AccessDecision.DENY, policies_evaluated
            
        except Exception as e:
            logger.error(f"ABAC evaluation failed: {e}")
            return AccessDecision.INDETERMINATE, []

    async def _get_applicable_policies(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType,
        context: SecurityContext
    ) -> List[Policy]:
        """Get policies applicable to the request"""
        try:
            # Load all active policies (in production, use indexing for efficiency)
            policy_keys = await self.redis.keys("abac_policy:*")
            applicable_policies = []
            
            for key in policy_keys:
                policy_data = await self.redis.get(key)
                if policy_data:
                    policy_dict = json.loads(policy_data)
                    
                    if not policy_dict.get("is_active", False):
                        continue
                    
                    policy = Policy(
                        policy_id=policy_dict["policy_id"],
                        name=policy_dict["name"],
                        description=policy_dict["description"],
                        policy_type=PolicyType(policy_dict["policy_type"]),
                        target=policy_dict["target"],
                        rules=policy_dict["rules"],
                        effect=PermissionEffect(policy_dict["effect"]),
                        priority=policy_dict["priority"],
                        is_active=policy_dict["is_active"],
                        created_at=datetime.fromisoformat(policy_dict["created_at"]),
                        updated_at=datetime.fromisoformat(policy_dict["updated_at"]),
                        metadata=policy_dict["metadata"]
                    )
                    
                    # Check if policy target matches request
                    if await self._match_policy_target(policy, user_id, resource_type, resource_id, action, context):
                        applicable_policies.append(policy)
            
            return applicable_policies
            
        except Exception as e:
            logger.error(f"Failed to get applicable policies: {e}")
            return []

    async def _match_policy_target(
        self,
        policy: Policy,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: ActionType,
        context: SecurityContext
    ) -> bool:
        """Check if policy target matches request"""
        try:
            target = policy.target
            
            # Check user target
            if "user" in target:
                user_target = target["user"]
                if not self._match_attribute_condition(user_id, user_target):
                    return False
            
            # Check resource target
            if "resource" in target:
                resource_target = target["resource"]
                if "type" in resource_target and resource_target["type"] != resource_type.value:
                    return False
                if "id" in resource_target and not self._match_pattern(resource_id, resource_target["id"]):
                    return False
            
            # Check action target
            if "action" in target:
                action_target = target["action"]
                if action_target != action.value:
                    return False
            
            # Check environment target
            if "environment" in target:
                env_target = target["environment"]
                for attr, condition in env_target.items():
                    env_value = context.environment_attributes.get(attr)
                    if not self._match_attribute_condition(env_value, condition):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Policy target matching failed: {e}")
            return False

    async def _evaluate_policy_rules(self, policy: Policy, context: SecurityContext) -> bool:
        """Evaluate policy rules"""
        try:
            if not policy.rules:
                return True
            
            for rule in policy.rules:
                if not await self._evaluate_rule(rule, context):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Policy rule evaluation failed: {e}")
            return False

    async def _evaluate_rule(self, rule: Dict[str, Any], context: SecurityContext) -> bool:
        """Evaluate individual rule"""
        try:
            rule_type = rule.get("type", "condition")
            
            if rule_type == "condition":
                return self._evaluate_condition(rule, context)
            elif rule_type == "time_based":
                return self._evaluate_time_condition(rule, context)
            elif rule_type == "location_based":
                return self._evaluate_location_condition(rule, context)
            else:
                logger.warning(f"Unknown rule type: {rule_type}")
                return False
                
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            return False

    def _evaluate_condition(self, rule: Dict[str, Any], context: SecurityContext) -> bool:
        """Evaluate condition rule"""
        try:
            attribute = rule.get("attribute")
            operator = rule.get("operator")
            value = rule.get("value")
            
            if not all([attribute, operator, value]):
                return False
            
            # Get attribute value from context
            attr_value = None
            if attribute.startswith("user."):
                attr_name = attribute[5:]  # Remove "user." prefix
                attr_value = context.user_attributes.get(attr_name)
            elif attribute.startswith("environment."):
                attr_name = attribute[12:]  # Remove "environment." prefix
                attr_value = context.environment_attributes.get(attr_name)
            elif attribute.startswith("resource."):
                attr_name = attribute[9:]  # Remove "resource." prefix
                attr_value = context.resource_attributes.get(attr_name)
            
            # Evaluate based on operator
            if operator == "equals":
                return attr_value == value
            elif operator == "not_equals":
                return attr_value != value
            elif operator == "in":
                return attr_value in value if isinstance(value, list) else False
            elif operator == "not_in":
                return attr_value not in value if isinstance(value, list) else True
            elif operator == "greater_than":
                return attr_value > value if isinstance(attr_value, (int, float)) else False
            elif operator == "less_than":
                return attr_value < value if isinstance(attr_value, (int, float)) else False
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    def _evaluate_time_condition(self, rule: Dict[str, Any], context: SecurityContext) -> bool:
        """Evaluate time-based condition"""
        try:
            current_time = context.request_time
            
            if "allowed_hours" in rule:
                allowed_hours = rule["allowed_hours"]
                if current_time.hour not in allowed_hours:
                    return False
            
            if "allowed_days" in rule:
                allowed_days = rule["allowed_days"]
                if current_time.weekday() not in allowed_days:
                    return False
            
            if "time_range" in rule:
                time_range = rule["time_range"]
                start_hour = time_range.get("start", 0)
                end_hour = time_range.get("end", 23)
                if not (start_hour <= current_time.hour <= end_hour):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Time condition evaluation failed: {e}")
            return False

    def _evaluate_location_condition(self, rule: Dict[str, Any], context: SecurityContext) -> bool:
        """Evaluate location-based condition"""
        try:
            user_ip = context.ip_address
            
            if "allowed_ips" in rule:
                allowed_ips = rule["allowed_ips"]
                if user_ip not in allowed_ips:
                    return False
            
            if "blocked_ips" in rule:
                blocked_ips = rule["blocked_ips"]
                if user_ip in blocked_ips:
                    return False
            
            if "allowed_countries" in rule:
                # In production, use IP geolocation service
                user_country = context.environment_attributes.get("country")
                allowed_countries = rule["allowed_countries"]
                if user_country not in allowed_countries:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Location condition evaluation failed: {e}")
            return False

    def _match_attribute_condition(self, value: Any, condition: Any) -> bool:
        """Match attribute value against condition"""
        try:
            if isinstance(condition, str):
                return value == condition
            elif isinstance(condition, list):
                return value in condition
            elif isinstance(condition, dict):
                operator = condition.get("operator", "equals")
                target_value = condition.get("value")
                
                if operator == "equals":
                    return value == target_value
                elif operator == "not_equals":
                    return value != target_value
                elif operator == "in":
                    return value in target_value if isinstance(target_value, list) else False
                # Add more operators as needed
                
            return False
            
        except Exception:
            return False

    def _match_pattern(self, value: str, pattern: str) -> bool:
        """Match value against pattern"""
        try:
            if pattern == "*":
                return True
            elif pattern.endswith("*"):
                return value.startswith(pattern[:-1])
            elif pattern.startswith("*"):
                return value.endswith(pattern[1:])
            else:
                return value == pattern
        except Exception:
            return False

    async def _store_policy(self, policy: Policy) -> None:
        """Store ABAC policy"""
        try:
            policy_data = {
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "policy_type": policy.policy_type.value,
                "target": policy.target,
                "rules": policy.rules,
                "effect": policy.effect.value,
                "priority": policy.priority,
                "is_active": policy.is_active,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "metadata": policy.metadata
            }
            
            await self.redis.setex(
                f"abac_policy:{policy.policy_id}",
                86400 * 30,  # 30 days
                json.dumps(policy_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store ABAC policy: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class AccessControlEngine:
    """
    Main access control engine combining RBAC and ABAC.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None,
        cache_ttl: int = 300  # 5 minutes
    ):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.cache_ttl = cache_ttl
        
        # Initialize engines
        self.rbac_engine = RBACEngine(redis_url)
        self.abac_engine = ABACEngine(redis_url)
        
        # Decision cache
        self.decision_cache: Dict[str, AccessResponse] = {}
        
        # Configuration
        self.config = {
            "enable_caching": True,
            "audit_all_decisions": True,
            "default_policy": "deny",
            "policy_combination": "permit_overrides",  # deny_overrides, permit_overrides, first_applicable
            "performance_monitoring": True,
        }

    async def initialize(self) -> None:
        """Initialize access control engine"""
        try:
            # Initialize Redis connection
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize sub-engines
            await self.rbac_engine.initialize()
            await self.abac_engine.initialize()
            
            logger.info("Access control engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize access control engine: {e}")
            raise

    async def evaluate_access(self, request: AccessRequest) -> AccessResponse:
        """Evaluate access control request"""
        try:
            start_time = time.time()
            
            # Check cache first
            if self.config["enable_caching"]:
                cached_response = await self._get_cached_decision(request)
                if cached_response:
                    return cached_response
            
            # Evaluate using RBAC
            rbac_decision = await self.rbac_engine.evaluate_access(
                request.user_id,
                request.resource_type,
                request.resource_id,
                request.action,
                request.context
            )
            
            # Evaluate using ABAC if context is available
            abac_decision = AccessDecision.NOT_APPLICABLE
            applicable_policies = []
            
            if request.context:
                abac_decision, applicable_policies = await self.abac_engine.evaluate_access(
                    request.user_id,
                    request.resource_type,
                    request.resource_id,
                    request.action,
                    request.context
                )
            
            # Combine decisions based on policy combination algorithm
            final_decision, reason = self._combine_decisions(rbac_decision, abac_decision)
            
            # Create response
            evaluation_time = (time.time() - start_time) * 1000
            
            response = AccessResponse(
                request_id=request.request_id,
                decision=final_decision,
                user_id=request.user_id,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                action=request.action,
                reason=reason,
                applicable_policies=applicable_policies,
                evaluation_time_ms=evaluation_time,
                cached=False
            )
            
            # Cache decision
            if self.config["enable_caching"]:
                await self._cache_decision(request, response)
            
            # Audit decision
            if self.config["audit_all_decisions"]:
                await self._audit_decision(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Access evaluation failed: {e}")
            return AccessResponse(
                request_id=request.request_id,
                decision=AccessDecision.INDETERMINATE,
                user_id=request.user_id,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                action=request.action,
                reason=f"Evaluation error: {e}"
            )

    def _combine_decisions(
        self,
        rbac_decision: AccessDecision,
        abac_decision: AccessDecision
    ) -> Tuple[AccessDecision, str]:
        """Combine RBAC and ABAC decisions"""
        try:
            combination_policy = self.config["policy_combination"]
            
            if combination_policy == "permit_overrides":
                # If either allows, permit
                if rbac_decision == AccessDecision.PERMIT or abac_decision == AccessDecision.PERMIT:
                    return AccessDecision.PERMIT, "Permitted by policy combination"
                elif rbac_decision == AccessDecision.DENY or abac_decision == AccessDecision.DENY:
                    return AccessDecision.DENY, "Denied by policy combination"
                else:
                    return AccessDecision.DENY, "Default deny"
                    
            elif combination_policy == "deny_overrides":
                # If either denies, deny
                if rbac_decision == AccessDecision.DENY or abac_decision == AccessDecision.DENY:
                    return AccessDecision.DENY, "Denied by policy combination"
                elif rbac_decision == AccessDecision.PERMIT or abac_decision == AccessDecision.PERMIT:
                    return AccessDecision.PERMIT, "Permitted by policy combination"
                else:
                    return AccessDecision.DENY, "Default deny"
                    
            elif combination_policy == "first_applicable":
                # Use first applicable decision
                if rbac_decision != AccessDecision.NOT_APPLICABLE:
                    return rbac_decision, "RBAC decision applied"
                elif abac_decision != AccessDecision.NOT_APPLICABLE:
                    return abac_decision, "ABAC decision applied"
                else:
                    return AccessDecision.DENY, "No applicable policy"
            
            # Default to deny
            return AccessDecision.DENY, "Default deny"
            
        except Exception as e:
            logger.error(f"Decision combination failed: {e}")
            return AccessDecision.INDETERMINATE, f"Combination error: {e}"

    async def _get_cached_decision(self, request: AccessRequest) -> Optional[AccessResponse]:
        """Get cached access decision"""
        try:
            cache_key = self._generate_cache_key(request)
            
            if cache_key in self.decision_cache:
                cached_response = self.decision_cache[cache_key]
                
                # Check if cache is still valid
                cache_age = (datetime.now(timezone.utc) - cached_response.timestamp).total_seconds()
                if cache_age < self.cache_ttl:
                    cached_response.cached = True
                    return cached_response
                else:
                    # Remove expired cache entry
                    del self.decision_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None

    async def _cache_decision(self, request: AccessRequest, response: AccessResponse) -> None:
        """Cache access decision"""
        try:
            cache_key = self._generate_cache_key(request)
            self.decision_cache[cache_key] = response
            
            # Also store in Redis for persistence
            cache_data = {
                "request_id": response.request_id,
                "decision": response.decision.value,
                "user_id": response.user_id,
                "resource_type": response.resource_type.value,
                "resource_id": response.resource_id,
                "action": response.action.value,
                "reason": response.reason,
                "timestamp": response.timestamp.isoformat()
            }
            
            await self.redis.setex(
                f"access_cache:{cache_key}",
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Decision caching failed: {e}")

    def _generate_cache_key(self, request: AccessRequest) -> str:
        """Generate cache key for request"""
        try:
            key_components = [
                request.user_id,
                request.resource_type.value,
                request.resource_id,
                request.action.value
            ]
            
            # Add context elements that affect decisions
            if request.context:
                key_components.extend([
                    request.context.ip_address,
                    str(request.context.request_time.hour)  # Hour-level caching
                ])
            
            cache_key = ":".join(key_components)
            return hashlib.sha256(cache_key.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Cache key generation failed: {e}")
            return f"error_{time.time()}"

    async def _audit_decision(self, request: AccessRequest, response: AccessResponse) -> None:
        """Audit access control decision"""
        try:
            audit_data = {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "resource_type": request.resource_type.value,
                "resource_id": request.resource_id,
                "action": request.action.value,
                "decision": response.decision.value,
                "reason": response.reason,
                "evaluation_time_ms": response.evaluation_time_ms,
                "timestamp": response.timestamp.isoformat(),
                "ip_address": request.context.ip_address if request.context else "unknown",
                "user_agent": request.context.user_agent if request.context else "unknown"
            }
            
            await self.redis.setex(
                f"access_audit:{request.request_id}",
                86400 * 90,  # Keep for 90 days
                json.dumps(audit_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Access audit failed: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()
        await self.rbac_engine.cleanup()
        await self.abac_engine.cleanup()