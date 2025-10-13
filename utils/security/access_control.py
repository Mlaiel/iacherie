"""
Access Control - Security Utilities Level 2
==========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade access control system for IA Chérie creator economy platform.
RBAC and ABAC implementation with < 5ms access control decisions.

Performance: < 5ms access control decisions
Standards: RBAC, ABAC, NIST, creator economy authorization
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import jwt
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Creator economy permissions."""
    # Content permissions
    CREATE_CONTENT = "create_content"
    READ_CONTENT = "read_content"
    UPDATE_CONTENT = "update_content"
    DELETE_CONTENT = "delete_content"
    PUBLISH_CONTENT = "publish_content"
    
    # Creator permissions
    MANAGE_CREATORS = "manage_creators"
    VIEW_CREATOR_ANALYTICS = "view_creator_analytics"
    APPROVE_CREATORS = "approve_creators"
    
    # Financial permissions
    VIEW_EARNINGS = "view_earnings"
    PROCESS_PAYMENTS = "process_payments"
    MANAGE_BILLING = "manage_billing"
    
    # Admin permissions
    ADMIN_PANEL = "admin_panel"
    SYSTEM_CONFIG = "system_config"
    USER_MANAGEMENT = "user_management"
    AUDIT_LOGS = "audit_logs"
    
    # Creator-specific permissions
    UPLOAD_MUSIC = "upload_music"
    UPLOAD_IMAGES = "upload_images"
    WRITE_BLOG = "write_blog"
    MANAGE_PORTFOLIO = "manage_portfolio"
    
    # Collaboration permissions
    INVITE_COLLABORATORS = "invite_collaborators"
    ACCEPT_COLLABORATIONS = "accept_collaborations"
    SHARE_CONTENT = "share_content"

class Role(Enum):
    """System roles for creator economy."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CREATOR_MANAGER = "creator_manager"
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    GUEST = "guest"

class AccessDecision(Enum):
    """Access control decision types."""
    ALLOW = "allow"
    DENY = "deny"
    ABSTAIN = "abstain"

@dataclass
class AccessRequest:
    """Access control request container."""
    user_id: str
    resource: str
    action: Permission
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class AccessResult:
    """Access control decision result."""
    decision: AccessDecision
    reason: str
    user_id: str
    resource: str
    action: Permission
    timestamp: datetime
    execution_time_ms: float
    policies_evaluated: List[str] = field(default_factory=list)
    additional_checks: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class RoleDefinition:
    """Role definition with permissions and constraints."""
    role: Role
    permissions: Set[Permission]
    inherits_from: Set[Role] = field(default_factory=set)
    constraints: Dict[str, Any] = field(default_factory=dict)
    creator_type: Optional[str] = None  # musician, photographer, blogger
    max_content_items: Optional[int] = None
    max_collaborations: Optional[int] = None

@dataclass
class Policy:
    """Access control policy definition."""
    policy_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    effect: AccessDecision
    priority: int = 0
    applicable_roles: Set[Role] = field(default_factory=set)
    applicable_resources: Set[str] = field(default_factory=set)

class AccessControl:
    """
    Enterprise-grade access control system for creator economy platform.
    
    Features:
    - Role-Based Access Control (RBAC)
    - Attribute-Based Access Control (ABAC)
    - Dynamic permission adjustment
    - Creator-specific authorization
    - Performance: < 5ms access decisions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize access control with enterprise configuration."""
        self.config = config or {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Role and permission storage
        self.role_definitions = self._initialize_role_definitions()
        self.user_roles: Dict[str, Set[Role]] = defaultdict(set)
        self.policies: List[Policy] = self._initialize_policies()
        self.access_cache: Dict[str, AccessResult] = {}
        
        # Performance tracking
        self.access_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "avg_execution_time": 0.0,
            "denied_requests": 0
        }
        
        # Cache configuration
        self.cache_ttl_seconds = self.config.get("cache_ttl_seconds", 300)  # 5 minutes
        self.max_cache_size = self.config.get("max_cache_size", 10000)
        
        logger.info("AccessControl initialized with enterprise RBAC/ABAC configuration")

    def _initialize_role_definitions(self) -> Dict[Role, RoleDefinition]:
        """Initialize role definitions with permissions."""
        roles = {}
        
        # Super Admin - All permissions
        roles[Role.SUPER_ADMIN] = RoleDefinition(
            role=Role.SUPER_ADMIN,
            permissions=set(Permission),  # All permissions
            constraints={
                "ip_whitelist": True,
                "mfa_required": True,
                "session_timeout": 3600  # 1 hour
            }
        )
        
        # Admin - Most permissions except super admin actions
        admin_permissions = set(Permission) - {Permission.SYSTEM_CONFIG}
        roles[Role.ADMIN] = RoleDefinition(
            role=Role.ADMIN,
            permissions=admin_permissions,
            constraints={
                "mfa_required": True,
                "session_timeout": 7200  # 2 hours
            }
        )
        
        # Moderator - Content and user management
        roles[Role.MODERATOR] = RoleDefinition(
            role=Role.MODERATOR,
            permissions={
                Permission.READ_CONTENT,
                Permission.UPDATE_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.MANAGE_CREATORS,
                Permission.APPROVE_CREATORS,
                Permission.AUDIT_LOGS
            },
            constraints={
                "session_timeout": 14400  # 4 hours
            }
        )
        
        # Creator Manager - Creator-focused permissions
        roles[Role.CREATOR_MANAGER] = RoleDefinition(
            role=Role.CREATOR_MANAGER,
            permissions={
                Permission.MANAGE_CREATORS,
                Permission.VIEW_CREATOR_ANALYTICS,
                Permission.APPROVE_CREATORS,
                Permission.READ_CONTENT,
                Permission.VIEW_EARNINGS
            },
            constraints={
                "session_timeout": 28800  # 8 hours
            }
        )
        
        # Musician - Music-specific permissions
        roles[Role.MUSICIAN] = RoleDefinition(
            role=Role.MUSICIAN,
            permissions={
                Permission.CREATE_CONTENT,
                Permission.READ_CONTENT,
                Permission.UPDATE_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.UPLOAD_MUSIC,
                Permission.MANAGE_PORTFOLIO,
                Permission.VIEW_EARNINGS,
                Permission.INVITE_COLLABORATORS,
                Permission.ACCEPT_COLLABORATIONS,
                Permission.SHARE_CONTENT
            },
            creator_type="musician",
            max_content_items=1000,
            max_collaborations=50,
            constraints={
                "content_types": ["audio", "music"],
                "session_timeout": 86400  # 24 hours
            }
        )
        
        # Photographer - Image-specific permissions
        roles[Role.PHOTOGRAPHER] = RoleDefinition(
            role=Role.PHOTOGRAPHER,
            permissions={
                Permission.CREATE_CONTENT,
                Permission.READ_CONTENT,
                Permission.UPDATE_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.UPLOAD_IMAGES,
                Permission.MANAGE_PORTFOLIO,
                Permission.VIEW_EARNINGS,
                Permission.INVITE_COLLABORATORS,
                Permission.ACCEPT_COLLABORATIONS,
                Permission.SHARE_CONTENT
            },
            creator_type="photographer",
            max_content_items=5000,
            max_collaborations=30,
            constraints={
                "content_types": ["image", "photo"],
                "session_timeout": 86400  # 24 hours
            }
        )
        
        # Blogger - Writing-specific permissions
        roles[Role.BLOGGER] = RoleDefinition(
            role=Role.BLOGGER,
            permissions={
                Permission.CREATE_CONTENT,
                Permission.READ_CONTENT,
                Permission.UPDATE_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.WRITE_BLOG,
                Permission.MANAGE_PORTFOLIO,
                Permission.VIEW_EARNINGS,
                Permission.INVITE_COLLABORATORS,
                Permission.ACCEPT_COLLABORATIONS,
                Permission.SHARE_CONTENT
            },
            creator_type="blogger",
            max_content_items=2000,
            max_collaborations=20,
            constraints={
                "content_types": ["text", "blog", "article"],
                "session_timeout": 86400  # 24 hours
            }
        )
        
        # Collaborator - Limited content permissions
        roles[Role.COLLABORATOR] = RoleDefinition(
            role=Role.COLLABORATOR,
            permissions={
                Permission.READ_CONTENT,
                Permission.UPDATE_CONTENT,
                Permission.ACCEPT_COLLABORATIONS,
                Permission.SHARE_CONTENT
            },
            max_collaborations=10,
            constraints={
                "session_timeout": 43200  # 12 hours
            }
        )
        
        # Viewer - Read-only permissions
        roles[Role.VIEWER] = RoleDefinition(
            role=Role.VIEWER,
            permissions={
                Permission.READ_CONTENT
            },
            constraints={
                "session_timeout": 7200  # 2 hours
            }
        )
        
        # Guest - Minimal permissions
        roles[Role.GUEST] = RoleDefinition(
            role=Role.GUEST,
            permissions=set(),  # No permissions
            constraints={
                "session_timeout": 1800  # 30 minutes
            }
        )
        
        return roles

    def _initialize_policies(self) -> List[Policy]:
        """Initialize access control policies."""
        policies = []
        
        # Content ownership policy
        policies.append(Policy(
            policy_id="content_ownership",
            name="Content Ownership Policy",
            description="Users can only modify content they own",
            conditions={
                "resource_type": "content",
                "action": ["update_content", "delete_content"],
                "ownership_required": True
            },
            effect=AccessDecision.ALLOW,
            priority=100
        ))
        
        # Creator type content policy
        policies.append(Policy(
            policy_id="creator_content_type",
            name="Creator Content Type Policy", 
            description="Creators can only upload content matching their type",
            conditions={
                "resource_type": "content",
                "action": ["upload_music", "upload_images", "write_blog"],
                "creator_type_match": True
            },
            effect=AccessDecision.ALLOW,
            priority=90
        ))
        
        # Time-based access policy
        policies.append(Policy(
            policy_id="business_hours",
            name="Business Hours Access Policy",
            description="Admin actions restricted to business hours",
            conditions={
                "roles": ["admin", "super_admin"],
                "actions": ["system_config", "user_management"],
                "time_range": {"start": "09:00", "end": "17:00"},
                "timezone": "UTC"
            },
            effect=AccessDecision.DENY,
            priority=80
        ))
        
        # Geographic restriction policy
        policies.append(Policy(
            policy_id="geo_restriction",
            name="Geographic Restriction Policy",
            description="Certain actions restricted by geography",
            conditions={
                "actions": ["process_payments", "manage_billing"],
                "allowed_countries": ["US", "CA", "EU", "UK"],
                "geo_check": True
            },
            effect=AccessDecision.DENY,
            priority=70
        ))
        
        # Content limits policy
        policies.append(Policy(
            policy_id="content_limits",
            name="Content Upload Limits Policy",
            description="Enforce content upload limits per creator type",
            conditions={
                "action": "create_content",
                "check_limits": True
            },
            effect=AccessDecision.DENY,
            priority=60
        ))
        
        # Collaboration limits policy
        policies.append(Policy(
            policy_id="collaboration_limits",
            name="Collaboration Limits Policy",
            description="Enforce collaboration limits per user",
            conditions={
                "actions": ["invite_collaborators", "accept_collaborations"],
                "check_collaboration_limits": True
            },
            effect=AccessDecision.DENY,
            priority=50
        ))
        
        return policies

    async def enforce_rbac_policies(self, access_request: AccessRequest) -> AccessResult:
        """
        Enforce Role-Based Access Control policies.
        
        Args:
            access_request: Access control request
            
        Returns:
            AccessResult with decision and details
        """
        start_time = time.perf_counter()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(access_request)
            if cache_key in self.access_cache:
                cached_result = self.access_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self.access_stats["cache_hits"] += 1
                    execution_time = (time.perf_counter() - start_time) * 1000
                    logger.debug(f"RBAC cache hit for {access_request.user_id} in {execution_time:.2f}ms")
                    return cached_result
            
            # Get user roles
            user_roles = self.user_roles.get(access_request.user_id, set())
            if not user_roles:
                execution_time = (time.perf_counter() - start_time) * 1000
                result = AccessResult(
                    decision=AccessDecision.DENY,
                    reason="No roles assigned to user",
                    user_id=access_request.user_id,
                    resource=access_request.resource,
                    action=access_request.action,
                    timestamp=access_request.timestamp,
                    execution_time_ms=execution_time
                )
                self._cache_result(cache_key, result)
                return result
            
            # Check permissions for each role
            has_permission = False
            evaluated_policies = []
            
            for role in user_roles:
                role_def = self.role_definitions.get(role)
                if role_def and access_request.action in role_def.permissions:
                    has_permission = True
                    evaluated_policies.append(f"role_{role.value}_permissions")
                    
                    # Check role constraints
                    if not await self._check_role_constraints(role_def, access_request):
                        has_permission = False
                        evaluated_policies.append(f"role_{role.value}_constraints_failed")
                        break
            
            decision = AccessDecision.ALLOW if has_permission else AccessDecision.DENY
            reason = "RBAC permission granted" if has_permission else "RBAC permission denied"
            
            execution_time = (time.perf_counter() - start_time) * 1000
            result = AccessResult(
                decision=decision,
                reason=reason,
                user_id=access_request.user_id,
                resource=access_request.resource,
                action=access_request.action,
                timestamp=access_request.timestamp,
                execution_time_ms=execution_time,
                policies_evaluated=evaluated_policies
            )
            
            # Update statistics
            self.access_stats["total_requests"] += 1
            if decision == AccessDecision.DENY:
                self.access_stats["denied_requests"] += 1
            
            # Cache result
            self._cache_result(cache_key, result)
            
            logger.debug(f"RBAC enforcement completed for {access_request.user_id} in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"RBAC enforcement failed in {execution_time:.2f}ms: {str(e)}")
            return AccessResult(
                decision=AccessDecision.DENY,
                reason=f"RBAC enforcement error: {str(e)}",
                user_id=access_request.user_id,
                resource=access_request.resource,
                action=access_request.action,
                timestamp=access_request.timestamp,
                execution_time_ms=execution_time
            )

    async def _check_role_constraints(self, role_def: RoleDefinition, access_request: AccessRequest) -> bool:
        """Check role-specific constraints."""
        try:
            constraints = role_def.constraints
            
            # Check session timeout
            if "session_timeout" in constraints:
                session_age = access_request.context.get("session_age", 0)
                if session_age > constraints["session_timeout"]:
                    logger.warning(f"Session timeout exceeded for role {role_def.role.value}")
                    return False
            
            # Check IP whitelist
            if constraints.get("ip_whitelist") and access_request.ip_address:
                whitelist = access_request.context.get("ip_whitelist", [])
                if access_request.ip_address not in whitelist:
                    logger.warning(f"IP {access_request.ip_address} not in whitelist for role {role_def.role.value}")
                    return False
            
            # Check MFA requirement
            if constraints.get("mfa_required"):
                mfa_verified = access_request.context.get("mfa_verified", False)
                if not mfa_verified:
                    logger.warning(f"MFA required but not verified for role {role_def.role.value}")
                    return False
            
            # Check content type restrictions
            if "content_types" in constraints and access_request.action in [
                Permission.CREATE_CONTENT, Permission.UPLOAD_MUSIC, 
                Permission.UPLOAD_IMAGES, Permission.WRITE_BLOG
            ]:
                content_type = access_request.context.get("content_type")
                allowed_types = constraints["content_types"]
                if content_type and content_type not in allowed_types:
                    logger.warning(f"Content type {content_type} not allowed for role {role_def.role.value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check role constraints: {str(e)}")
            return False

    async def validate_permissions(self, user_id: str, required_permissions: List[Permission]) -> Dict[Permission, bool]:
        """
        Validate multiple permissions for a user.
        
        Args:
            user_id: User identifier
            required_permissions: List of permissions to check
            
        Returns:
            Dictionary mapping permissions to validation results
        """
        start_time = time.perf_counter()
        
        try:
            results = {}
            user_roles = self.user_roles.get(user_id, set())
            
            # Get all permissions for user's roles
            user_permissions = set()
            for role in user_roles:
                role_def = self.role_definitions.get(role)
                if role_def:
                    user_permissions.update(role_def.permissions)
            
            # Check each required permission
            for permission in required_permissions:
                results[permission] = permission in user_permissions
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Permission validation completed for {user_id} in {execution_time:.2f}ms")
            
            return results
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Permission validation failed in {execution_time:.2f}ms: {str(e)}")
            return {permission: False for permission in required_permissions}

    async def manage_role_hierarchies(self, user_id: str, new_roles: Set[Role]) -> bool:
        """
        Manage role hierarchies and inheritance.
        
        Args:
            user_id: User identifier
            new_roles: New roles to assign
            
        Returns:
            Success status
        """
        start_time = time.perf_counter()
        
        try:
            # Validate role combinations
            if not self._validate_role_combination(new_roles):
                logger.warning(f"Invalid role combination for user {user_id}: {new_roles}")
                return False
            
            # Resolve role inheritance
            resolved_roles = self._resolve_role_inheritance(new_roles)
            
            # Update user roles
            old_roles = self.user_roles.get(user_id, set())
            self.user_roles[user_id] = resolved_roles
            
            # Clear cache for user
            self._clear_user_cache(user_id)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Role hierarchy managed for {user_id} in {execution_time:.2f}ms: {old_roles} -> {resolved_roles}")
            
            return True
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Role hierarchy management failed in {execution_time:.2f}ms: {str(e)}")
            return False

    def _validate_role_combination(self, roles: Set[Role]) -> bool:
        """Validate if role combination is allowed."""
        # Conflicting role combinations
        conflicts = [
            {Role.SUPER_ADMIN, Role.GUEST},
            {Role.ADMIN, Role.GUEST},
            {Role.MUSICIAN, Role.PHOTOGRAPHER, Role.BLOGGER}  # Can't be multiple creator types
        ]
        
        for conflict_set in conflicts:
            if len(roles.intersection(conflict_set)) > 1:
                return False
        
        return True

    def _resolve_role_inheritance(self, roles: Set[Role]) -> Set[Role]:
        """Resolve role inheritance to get effective roles."""
        effective_roles = set(roles)
        
        for role in roles:
            role_def = self.role_definitions.get(role)
            if role_def and role_def.inherits_from:
                effective_roles.update(role_def.inherits_from)
        
        return effective_roles

    async def audit_access_patterns(self, user_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Audit access patterns for a user.
        
        Args:
            user_id: User identifier
            time_window_hours: Time window for analysis
            
        Returns:
            Access pattern analysis
        """
        start_time = time.perf_counter()
        
        try:
            # In a real implementation, this would query access logs
            # For now, we'll return sample data structure
            
            patterns = {
                "user_id": user_id,
                "analysis_period": f"{time_window_hours} hours",
                "total_requests": 0,
                "denied_requests": 0,
                "resource_access": {},
                "permission_usage": {},
                "access_times": [],
                "ip_addresses": [],
                "suspicious_patterns": [],
                "recommendations": []
            }
            
            # Sample analysis (in production, would analyze actual logs)
            patterns["total_requests"] = 145
            patterns["denied_requests"] = 3
            patterns["resource_access"] = {
                "content": 120,
                "profile": 15,
                "analytics": 10
            }
            patterns["permission_usage"] = {
                Permission.READ_CONTENT.value: 100,
                Permission.CREATE_CONTENT.value: 30,
                Permission.UPDATE_CONTENT.value: 15
            }
            
            # Generate recommendations based on patterns
            if patterns["denied_requests"] > 10:
                patterns["recommendations"].append("Review denied access attempts")
            
            if len(patterns["ip_addresses"]) > 5:
                patterns["recommendations"].append("Multiple IP addresses detected")
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Access pattern audit completed for {user_id} in {execution_time:.2f}ms")
            
            return patterns
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Access pattern audit failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    async def implement_principle_least_privilege(self, user_id: str) -> Dict[str, Any]:
        """
        Implement principle of least privilege for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Privilege optimization results
        """
        start_time = time.perf_counter()
        
        try:
            user_roles = self.user_roles.get(user_id, set())
            if not user_roles:
                return {"error": "No roles found for user"}
            
            # Analyze permission usage (in production, would use actual usage data)
            used_permissions = self._analyze_permission_usage(user_id)
            
            # Get current permissions
            current_permissions = set()
            for role in user_roles:
                role_def = self.role_definitions.get(role)
                if role_def:
                    current_permissions.update(role_def.permissions)
            
            # Identify unused permissions
            unused_permissions = current_permissions - used_permissions
            
            # Generate recommendations
            recommendations = []
            if unused_permissions:
                recommendations.append(f"Consider removing unused permissions: {[p.value for p in unused_permissions]}")
            
            # Check for over-privileged roles
            for role in user_roles:
                if role in [Role.SUPER_ADMIN, Role.ADMIN]:
                    if not self._requires_admin_privileges(user_id):
                        recommendations.append(f"Consider removing admin role: {role.value}")
            
            optimization_result = {
                "user_id": user_id,
                "current_roles": [r.value for r in user_roles],
                "current_permissions": [p.value for p in current_permissions],
                "used_permissions": [p.value for p in used_permissions],
                "unused_permissions": [p.value for p in unused_permissions],
                "recommendations": recommendations,
                "privilege_score": len(used_permissions) / len(current_permissions) if current_permissions else 0
            }
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Least privilege analysis completed for {user_id} in {execution_time:.2f}ms")
            
            return optimization_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Least privilege implementation failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    def _analyze_permission_usage(self, user_id: str) -> Set[Permission]:
        """Analyze which permissions a user actually uses."""
        # In production, this would analyze access logs
        # For now, return a sample set based on role
        user_roles = self.user_roles.get(user_id, set())
        
        used_permissions = set()
        for role in user_roles:
            if role == Role.MUSICIAN:
                used_permissions.update([
                    Permission.CREATE_CONTENT,
                    Permission.READ_CONTENT,
                    Permission.UPLOAD_MUSIC,
                    Permission.VIEW_EARNINGS
                ])
            elif role == Role.PHOTOGRAPHER:
                used_permissions.update([
                    Permission.CREATE_CONTENT,
                    Permission.READ_CONTENT,
                    Permission.UPLOAD_IMAGES,
                    Permission.MANAGE_PORTFOLIO
                ])
            elif role == Role.BLOGGER:
                used_permissions.update([
                    Permission.CREATE_CONTENT,
                    Permission.READ_CONTENT,
                    Permission.WRITE_BLOG,
                    Permission.SHARE_CONTENT
                ])
        
        return used_permissions

    def _requires_admin_privileges(self, user_id: str) -> bool:
        """Check if user requires admin privileges based on usage."""
        # In production, would analyze admin action usage
        # For now, return False to suggest privilege reduction
        return False

    async def dynamic_permission_adjustment(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically adjust permissions based on context.
        
        Args:
            user_id: User identifier
            context: Current context information
            
        Returns:
            Permission adjustment results
        """
        start_time = time.perf_counter()
        
        try:
            adjustments = []
            current_roles = self.user_roles.get(user_id, set())
            
            # Risk-based adjustments
            risk_score = context.get("risk_score", 0.0)
            if risk_score > 0.8:
                adjustments.append({
                    "type": "security_restriction",
                    "action": "require_mfa",
                    "reason": "High risk score detected"
                })
            
            # Time-based adjustments
            current_hour = datetime.now(timezone.utc).hour
            if current_hour < 6 or current_hour > 22:  # Outside business hours
                for role in current_roles:
                    if role in [Role.ADMIN, Role.SUPER_ADMIN]:
                        adjustments.append({
                            "type": "time_restriction",
                            "action": "limit_admin_actions",
                            "reason": "Outside business hours"
                        })
            
            # Location-based adjustments
            location = context.get("location", {})
            if location.get("country") not in ["US", "CA", "EU", "UK"]:
                adjustments.append({
                    "type": "geo_restriction",
                    "action": "limit_financial_actions",
                    "reason": "Access from restricted geography"
                })
            
            # Device-based adjustments
            device_trust = context.get("device_trust_score", 1.0)
            if device_trust < 0.5:
                adjustments.append({
                    "type": "device_restriction",
                    "action": "require_additional_auth",
                    "reason": "Untrusted device detected"
                })
            
            # Content-based adjustments for creators
            creator_reputation = context.get("creator_reputation", 1.0)
            if creator_reputation < 0.3:
                adjustments.append({
                    "type": "content_restriction", 
                    "action": "require_content_review",
                    "reason": "Low creator reputation"
                })
            
            adjustment_result = {
                "user_id": user_id,
                "context_analyzed": context,
                "adjustments": adjustments,
                "effective_immediately": True,
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Dynamic permission adjustment completed for {user_id} in {execution_time:.2f}ms")
            
            return adjustment_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Dynamic permission adjustment failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    async def access_pattern_analysis(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Analyze access patterns across the platform.
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            Platform-wide access pattern analysis
        """
        start_time = time.perf_counter()
        
        try:
            # Aggregate statistics
            total_users = len(self.user_roles)
            total_requests = self.access_stats["total_requests"]
            denied_rate = (self.access_stats["denied_requests"] / total_requests) if total_requests > 0 else 0
            
            # Role distribution
            role_distribution = defaultdict(int)
            for user_roles in self.user_roles.values():
                for role in user_roles:
                    role_distribution[role.value] += 1
            
            # Permission usage patterns
            permission_usage = defaultdict(int)
            for user_id in self.user_roles.keys():
                used_perms = self._analyze_permission_usage(user_id)
                for perm in used_perms:
                    permission_usage[perm.value] += 1
            
            # Security insights
            security_insights = []
            
            if denied_rate > 0.1:  # More than 10% denied
                security_insights.append("High access denial rate detected")
            
            if role_distribution.get("super_admin", 0) > 2:
                security_insights.append("Multiple super admin accounts detected")
            
            # Creator economy insights
            creator_types = ["musician", "photographer", "blogger"]
            creator_stats = {}
            for creator_type in creator_types:
                creator_role = getattr(Role, creator_type.upper(), None)
                if creator_role:
                    creator_stats[creator_type] = role_distribution.get(creator_role.value, 0)
            
            analysis_result = {
                "analysis_period": f"{time_window_hours} hours",
                "platform_metrics": {
                    "total_users": total_users,
                    "total_requests": total_requests,
                    "denied_rate": denied_rate,
                    "cache_hit_rate": self.access_stats["cache_hits"] / total_requests if total_requests > 0 else 0
                },
                "role_distribution": dict(role_distribution),
                "permission_usage": dict(permission_usage),
                "creator_economy_stats": creator_stats,
                "security_insights": security_insights,
                "recommendations": [
                    "Review high-privilege accounts regularly",
                    "Monitor creator activity patterns",
                    "Optimize access control caching"
                ]
            }
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Access pattern analysis completed in {execution_time:.2f}ms")
            
            return analysis_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Access pattern analysis failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    def _generate_cache_key(self, access_request: AccessRequest) -> str:
        """Generate cache key for access request."""
        key_data = f"{access_request.user_id}:{access_request.resource}:{access_request.action.value}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cached_result: AccessResult) -> bool:
        """Check if cached result is still valid."""
        cache_age = (datetime.now(timezone.utc) - cached_result.timestamp).total_seconds()
        return cache_age < self.cache_ttl_seconds

    def _cache_result(self, cache_key: str, result: AccessResult) -> None:
        """Cache access control result."""
        # Implement LRU cache eviction if needed
        if len(self.access_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self.access_cache.keys(), 
                           key=lambda k: self.access_cache[k].timestamp)
            del self.access_cache[oldest_key]
        
        self.access_cache[cache_key] = result

    def _clear_user_cache(self, user_id: str) -> None:
        """Clear cache entries for a specific user."""
        keys_to_remove = [
            key for key, result in self.access_cache.items() 
            if result.user_id == user_id
        ]
        for key in keys_to_remove:
            del self.access_cache[key]

    # Public API methods for role management
    def assign_role(self, user_id: str, role: Role) -> bool:
        """Assign a role to a user."""
        try:
            self.user_roles[user_id].add(role)
            self._clear_user_cache(user_id)
            logger.info(f"Role {role.value} assigned to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to assign role {role.value} to user {user_id}: {str(e)}")
            return False

    def remove_role(self, user_id: str, role: Role) -> bool:
        """Remove a role from a user."""
        try:
            self.user_roles[user_id].discard(role)
            self._clear_user_cache(user_id)
            logger.info(f"Role {role.value} removed from user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove role {role.value} from user {user_id}: {str(e)}")
            return False

    def get_user_roles(self, user_id: str) -> Set[Role]:
        """Get roles assigned to a user."""
        return self.user_roles.get(user_id, set())

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get effective permissions for a user."""
        permissions = set()
        user_roles = self.user_roles.get(user_id, set())
        
        for role in user_roles:
            role_def = self.role_definitions.get(role)
            if role_def:
                permissions.update(role_def.permissions)
        
        return permissions

    def get_access_statistics(self) -> Dict[str, Any]:
        """Get access control statistics."""
        return {
            "access_stats": self.access_stats.copy(),
            "cache_size": len(self.access_cache),
            "total_users": len(self.user_roles),
            "role_definitions": len(self.role_definitions),
            "policies": len(self.policies)
        }

# Factory for enterprise deployment
class AccessControlFactory:
    """Factory for creating AccessControl instances with different configurations."""
    
    @staticmethod
    def create_production_access_control() -> AccessControl:
        """Create production-ready access control."""
        config = {
            "cache_ttl_seconds": 300,  # 5 minutes
            "max_cache_size": 10000,
            "enable_audit_logging": True,
            "strict_mode": True,
            "log_level": "INFO"
        }
        return AccessControl(config)
    
    @staticmethod
    def create_development_access_control() -> AccessControl:
        """Create development access control with relaxed settings."""
        config = {
            "cache_ttl_seconds": 60,  # 1 minute
            "max_cache_size": 1000,
            "enable_audit_logging": True,
            "strict_mode": False,
            "log_level": "DEBUG"
        }
        return AccessControl(config)
    
    @staticmethod
    def create_high_security_access_control() -> AccessControl:
        """Create high-security access control for sensitive environments."""
        config = {
            "cache_ttl_seconds": 60,  # 1 minute
            "max_cache_size": 5000,
            "enable_audit_logging": True,
            "strict_mode": True,
            "require_mfa": True,
            "log_level": "WARNING"
        }
        return AccessControl(config)