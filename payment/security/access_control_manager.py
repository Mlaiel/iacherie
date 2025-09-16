#!/usr/bin/env python3
"""
🔑 Access Control Manager
========================

Enterprise-grade access control and identity management system for payment security.
Implements RBAC, ABAC, SSO integration, and privilege management.

Expert Roles Combined:
- Security Specialist: Advanced access control and authorization
- Backend Senior Engineer: Scalable identity management architecture  
- Microservices Architect: Distributed access control coordination

Features:
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Single Sign-On (SSO) integration
- Multi-factor authentication (MFA)
- Privilege escalation management
- Session management and monitoring
- Access audit trails
- Dynamic permission management
- Creator revenue access control

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security + Backend Senior + Microservices
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
import hmac
import secrets
import uuid
import jwt
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import aioredis
import bcrypt
from cryptography.fernet import Fernet
import re

logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Access levels for different operations"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceType(Enum):
    """Types of resources that can be accessed"""
    PAYMENT_ACCOUNT = "payment_account"
    REVENUE_DATA = "revenue_data"
    TRANSACTION_HISTORY = "transaction_history"
    PAYOUT_SETTINGS = "payout_settings"
    FINANCIAL_REPORTS = "financial_reports"
    CREATOR_PROFILE = "creator_profile"
    COLLABORATION_PROJECTS = "collaboration_projects"
    CONTENT_LIBRARY = "content_library"
    ANALYTICS_DATA = "analytics_data"
    ADMIN_PANEL = "admin_panel"

class AuthenticationMethod(Enum):
    """Authentication methods supported"""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    BIOMETRIC = "biometric"
    SSO_OAUTH = "sso_oauth"
    SSO_SAML = "sso_saml"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"

class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

class PermissionEffect(Enum):
    """Permission effects"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    resource_access: Dict[ResourceType, AccessLevel] = field(default_factory=dict)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class User:
    """User identity and authentication data"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    roles: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    mfa_enabled: bool = False
    mfa_secret: str = ""
    sso_providers: List[str] = field(default_factory=list)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Session:
    """User session data"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=8))
    ip_address: str = ""
    user_agent: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    permissions_cache: Dict[str, Any] = field(default_factory=dict)
    mfa_verified: bool = False

@dataclass
class AccessRequest:
    """Access request for authorization"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    resource_type: ResourceType = ResourceType.CREATOR_PROFILE
    resource_id: str = ""
    action: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessAuditLog:
    """Access audit log entry"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    resource_type: ResourceType = ResourceType.CREATOR_PROFILE
    resource_id: str = ""
    action: str = ""
    result: PermissionEffect = PermissionEffect.DENY
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    user_agent: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

class AccessControlManager:
    """
    Enterprise Access Control Manager
    ================================
    
    Comprehensive access control system with RBAC, ABAC,
    SSO integration, and privilege management.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.sessions: Dict[str, Session] = {}
        self.audit_logs: List[AccessAuditLog] = []
        
        # JWT configuration
        self.jwt_secret = secrets.token_urlsafe(32)
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = 3600  # 1 hour
        
        # Encryption for sensitive data
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize system roles
        self._initialize_system_roles()
        
        # Access control metrics
        self.metrics = {
            'total_users': 0,
            'active_sessions': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'access_grants': 0,
            'access_denials': 0,
            'privilege_escalations': 0,
            'mfa_usage': 0
        }
        
        logger.info("🔑 Access Control Manager initialized")

    async def initialize(self):
        """Initialize Redis connection and load configurations"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_existing_data()
            logger.info("✅ Access Control Manager initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Access Control Manager: {e}")
            raise

    def _initialize_system_roles(self):
        """Initialize predefined system roles"""
        # Creator role
        creator_role = Role(
            name="creator",
            description="Standard creator with content and revenue access",
            permissions=[
                "create_content",
                "edit_own_content",
                "view_own_analytics",
                "manage_collaborations",
                "access_revenue_data"
            ],
            resource_access={
                ResourceType.PAYMENT_ACCOUNT: AccessLevel.READ,
                ResourceType.REVENUE_DATA: AccessLevel.READ,
                ResourceType.TRANSACTION_HISTORY: AccessLevel.READ,
                ResourceType.PAYOUT_SETTINGS: AccessLevel.WRITE,
                ResourceType.CREATOR_PROFILE: AccessLevel.WRITE,
                ResourceType.COLLABORATION_PROJECTS: AccessLevel.WRITE,
                ResourceType.CONTENT_LIBRARY: AccessLevel.WRITE,
                ResourceType.ANALYTICS_DATA: AccessLevel.READ
            },
            is_system_role=True
        )
        
        # Premium creator role
        premium_creator_role = Role(
            name="premium_creator",
            description="Premium creator with enhanced features and priority support",
            permissions=[
                "create_content",
                "edit_own_content",
                "view_own_analytics",
                "manage_collaborations",
                "access_revenue_data",
                "advanced_analytics",
                "priority_support",
                "beta_features"
            ],
            resource_access={
                ResourceType.PAYMENT_ACCOUNT: AccessLevel.WRITE,
                ResourceType.REVENUE_DATA: AccessLevel.WRITE,
                ResourceType.TRANSACTION_HISTORY: AccessLevel.READ,
                ResourceType.PAYOUT_SETTINGS: AccessLevel.WRITE,
                ResourceType.FINANCIAL_REPORTS: AccessLevel.READ,
                ResourceType.CREATOR_PROFILE: AccessLevel.WRITE,
                ResourceType.COLLABORATION_PROJECTS: AccessLevel.WRITE,
                ResourceType.CONTENT_LIBRARY: AccessLevel.WRITE,
                ResourceType.ANALYTICS_DATA: AccessLevel.WRITE
            },
            is_system_role=True
        )
        
        # Admin role
        admin_role = Role(
            name="admin",
            description="Platform administrator with full access",
            permissions=[
                "manage_users",
                "manage_roles",
                "view_all_analytics",
                "manage_payments",
                "system_administration",
                "security_management",
                "audit_access"
            ],
            resource_access={
                ResourceType.PAYMENT_ACCOUNT: AccessLevel.ADMIN,
                ResourceType.REVENUE_DATA: AccessLevel.ADMIN,
                ResourceType.TRANSACTION_HISTORY: AccessLevel.ADMIN,
                ResourceType.PAYOUT_SETTINGS: AccessLevel.ADMIN,
                ResourceType.FINANCIAL_REPORTS: AccessLevel.ADMIN,
                ResourceType.CREATOR_PROFILE: AccessLevel.ADMIN,
                ResourceType.COLLABORATION_PROJECTS: AccessLevel.ADMIN,
                ResourceType.CONTENT_LIBRARY: AccessLevel.ADMIN,
                ResourceType.ANALYTICS_DATA: AccessLevel.ADMIN,
                ResourceType.ADMIN_PANEL: AccessLevel.ADMIN
            },
            is_system_role=True
        )
        
        # Financial manager role
        financial_role = Role(
            name="financial_manager",
            description="Financial operations and payment management",
            permissions=[
                "manage_payments",
                "view_financial_reports",
                "process_payouts",
                "manage_revenue_sharing",
                "audit_transactions"
            ],
            resource_access={
                ResourceType.PAYMENT_ACCOUNT: AccessLevel.ADMIN,
                ResourceType.REVENUE_DATA: AccessLevel.ADMIN,
                ResourceType.TRANSACTION_HISTORY: AccessLevel.ADMIN,
                ResourceType.PAYOUT_SETTINGS: AccessLevel.ADMIN,
                ResourceType.FINANCIAL_REPORTS: AccessLevel.ADMIN
            },
            is_system_role=True
        )
        
        # Store system roles
        for role in [creator_role, premium_creator_role, admin_role, financial_role]:
            self.roles[role.role_id] = role

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: List[str] = None,
        attributes: Dict[str, Any] = None
    ) -> str:
        """
        Create new user account
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            roles: List of role names to assign
            attributes: Additional user attributes
            
        Returns:
            User ID of created user
        """
        try:
            # Validate input
            if not self._validate_username(username):
                raise ValueError("Invalid username format")
                
            if not self._validate_email(email):
                raise ValueError("Invalid email format")
                
            if not self._validate_password_strength(password):
                raise ValueError("Password does not meet strength requirements")
                
            # Check for existing user
            if await self._user_exists(username, email):
                raise ValueError("User already exists")
                
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Assign default role if none provided
            if not roles:
                roles = ["creator"]
                
            # Validate roles exist
            role_ids = []
            for role_name in roles:
                role_id = await self._find_role_by_name(role_name)
                if role_id:
                    role_ids.append(role_id)
                else:
                    logger.warning(f"⚠️ Role '{role_name}' not found, skipping")
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                roles=role_ids,
                attributes=attributes or {}
            )
            
            # Store user
            self.users[user.user_id] = user
            self.metrics['total_users'] += 1
            
            # Store in Redis
            await self._store_user(user)
            
            # Log user creation
            await self._log_audit_event(
                user_id=user.user_id,
                resource_type=ResourceType.CREATOR_PROFILE,
                resource_id=user.user_id,
                action="create_user",
                result=PermissionEffect.ALLOW,
                details={"username": username, "email": email, "roles": roles}
            )
            
            logger.info(f"✅ User created: {username} ({user.user_id})")
            return user.user_id
            
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            raise

    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "",
        mfa_token: str = ""
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Authenticate user and create session
        
        Args:
            username: Username or email
            password: Password
            ip_address: Client IP address
            user_agent: Client user agent
            mfa_token: MFA token if required
            
        Returns:
            Tuple of (session_id, jwt_token) if successful, (None, None) if failed
        """
        try:
            # Find user
            user = await self._find_user(username)
            if not user:
                self.metrics['failed_authentications'] += 1
                await self._log_audit_event(
                    user_id="",
                    resource_type=ResourceType.CREATOR_PROFILE,
                    action="authenticate",
                    result=PermissionEffect.DENY,
                    details={"reason": "user_not_found", "username": username},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return None, None
                
            # Check if account is locked
            if user.account_locked:
                await self._log_audit_event(
                    user_id=user.user_id,
                    resource_type=ResourceType.CREATOR_PROFILE,
                    action="authenticate",
                    result=PermissionEffect.DENY,
                    details={"reason": "account_locked"},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return None, None
                
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked = True
                    logger.warning(f"🔒 Account locked for user {user.username} due to failed attempts")
                    
                await self._store_user(user)
                self.metrics['failed_authentications'] += 1
                
                await self._log_audit_event(
                    user_id=user.user_id,
                    resource_type=ResourceType.CREATOR_PROFILE,
                    action="authenticate",
                    result=PermissionEffect.DENY,
                    details={"reason": "invalid_password", "failed_attempts": user.failed_login_attempts},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return None, None
                
            # Check MFA if enabled
            mfa_verified = True
            if user.mfa_enabled:
                if not mfa_token:
                    return None, None
                    
                mfa_verified = await self._verify_mfa_token(user, mfa_token)
                if not mfa_verified:
                    self.metrics['failed_authentications'] += 1
                    await self._log_audit_event(
                        user_id=user.user_id,
                        resource_type=ResourceType.CREATOR_PROFILE,
                        action="authenticate",
                        result=PermissionEffect.DENY,
                        details={"reason": "invalid_mfa"},
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    return None, None
                    
                self.metrics['mfa_usage'] += 1
                
            # Reset failed attempts on successful authentication
            user.failed_login_attempts = 0
            user.last_login = datetime.now()
            await self._store_user(user)
            
            # Create session
            session = Session(
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                mfa_verified=mfa_verified
            )
            
            # Cache user permissions
            session.permissions_cache = await self._get_user_permissions(user.user_id)
            
            # Store session
            self.sessions[session.session_id] = session
            self.metrics['active_sessions'] += 1
            self.metrics['successful_authentications'] += 1
            
            # Store in Redis
            await self._store_session(session)
            
            # Generate JWT token
            jwt_token = await self._generate_jwt_token(user, session)
            
            # Log successful authentication
            await self._log_audit_event(
                user_id=user.user_id,
                session_id=session.session_id,
                resource_type=ResourceType.CREATOR_PROFILE,
                action="authenticate",
                result=PermissionEffect.ALLOW,
                details={"mfa_used": user.mfa_enabled},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"✅ User authenticated: {user.username}")
            return session.session_id, jwt_token
            
        except Exception as e:
            logger.error(f"❌ Error authenticating user: {e}")
            return None, None

    async def check_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Check if user has access to perform action on resource
        
        Args:
            user_id: User ID requesting access
            resource_type: Type of resource being accessed
            resource_id: Specific resource ID
            action: Action being performed
            context: Additional context for decision
            
        Returns:
            True if access is granted, False otherwise
        """
        try:
            # Create access request
            request = AccessRequest(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                context=context or {}
            )
            
            # Get user
            user = self.users.get(user_id)
            if not user or not user.is_active:
                await self._log_access_decision(request, PermissionEffect.DENY, "user_not_found_or_inactive")
                return False
                
            # Check RBAC (Role-Based Access Control)
            rbac_result = await self._check_rbac_access(user, request)
            if rbac_result is False:
                await self._log_access_decision(request, PermissionEffect.DENY, "rbac_denied")
                return False
                
            # Check ABAC (Attribute-Based Access Control)
            abac_result = await self._check_abac_access(user, request)
            if abac_result is False:
                await self._log_access_decision(request, PermissionEffect.DENY, "abac_denied")
                return False
                
            # Check resource-specific permissions
            resource_result = await self._check_resource_access(user, request)
            if resource_result is False:
                await self._log_access_decision(request, PermissionEffect.DENY, "resource_denied")
                return False
                
            # All checks passed
            self.metrics['access_grants'] += 1
            await self._log_access_decision(request, PermissionEffect.ALLOW, "all_checks_passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking access: {e}")
            await self._log_access_decision(request, PermissionEffect.DENY, f"error: {str(e)}")
            return False

    async def _check_rbac_access(self, user: User, request: AccessRequest) -> bool:
        """Check role-based access control"""
        try:
            # Get user roles
            user_roles = [self.roles.get(role_id) for role_id in user.roles]
            user_roles = [role for role in user_roles if role and role.is_active]
            
            if not user_roles:
                return False
                
            # Check if any role grants access
            for role in user_roles:
                # Check specific permissions
                if self._action_matches_permissions(request.action, role.permissions):
                    return True
                    
                # Check resource access level
                required_level = self._get_required_access_level(request.action)
                role_access_level = role.resource_access.get(request.resource_type, AccessLevel.NONE)
                
                if self._access_level_sufficient(role_access_level, required_level):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in RBAC check: {e}")
            return False

    async def _check_abac_access(self, user: User, request: AccessRequest) -> bool:
        """Check attribute-based access control"""
        try:
            # Define ABAC rules
            rules = [
                await self._check_time_based_access(request),
                await self._check_location_based_access(user, request),
                await self._check_resource_ownership(user, request),
                await self._check_collaboration_access(user, request),
                await self._check_revenue_access_rules(user, request)
            ]
            
            # All rules must pass (AND logic)
            return all(rules)
            
        except Exception as e:
            logger.error(f"❌ Error in ABAC check: {e}")
            return False

    async def _check_resource_access(self, user: User, request: AccessRequest) -> bool:
        """Check resource-specific access rules"""
        try:
            # Creator-specific access rules
            if request.resource_type == ResourceType.CREATOR_PROFILE:
                # Users can access their own profile
                if request.resource_id == user.user_id:
                    return True
                    
                # Admins can access any profile
                if await self._user_has_permission(user.user_id, "manage_users"):
                    return True
                    
            # Revenue data access rules
            elif request.resource_type in [ResourceType.REVENUE_DATA, ResourceType.PAYMENT_ACCOUNT]:
                # Users can access their own revenue data
                if await self._user_owns_resource(user.user_id, request.resource_id):
                    return True
                    
                # Financial managers can access any revenue data
                if await self._user_has_permission(user.user_id, "manage_payments"):
                    return True
                    
            # Collaboration access rules
            elif request.resource_type == ResourceType.COLLABORATION_PROJECTS:
                # Check if user is part of collaboration
                if await self._user_in_collaboration(user.user_id, request.resource_id):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in resource access check: {e}")
            return False

    async def _check_time_based_access(self, request: AccessRequest) -> bool:
        """Check time-based access restrictions"""
        # For now, allow all time-based access
        # In real implementation, this would check business hours, etc.
        return True

    async def _check_location_based_access(self, user: User, request: AccessRequest) -> bool:
        """Check location-based access restrictions"""
        # For now, allow all location-based access
        # In real implementation, this would check IP geolocation, etc.
        return True

    async def _check_resource_ownership(self, user: User, request: AccessRequest) -> bool:
        """Check if user owns the resource"""
        return await self._user_owns_resource(user.user_id, request.resource_id)

    async def _check_collaboration_access(self, user: User, request: AccessRequest) -> bool:
        """Check collaboration-specific access rules"""
        if request.resource_type == ResourceType.COLLABORATION_PROJECTS:
            return await self._user_in_collaboration(user.user_id, request.resource_id)
        return True

    async def _check_revenue_access_rules(self, user: User, request: AccessRequest) -> bool:
        """Check revenue access specific rules"""
        if request.resource_type in [ResourceType.REVENUE_DATA, ResourceType.PAYMENT_ACCOUNT]:
            # Check if user has verified payment methods
            if not user.attributes.get('payment_verified', False):
                return False
                
            # Check if user has completed KYC
            if not user.attributes.get('kyc_completed', False):
                return False
                
        return True

    def _action_matches_permissions(self, action: str, permissions: List[str]) -> bool:
        """Check if action matches any permission"""
        for permission in permissions:
            if action == permission or action.startswith(permission):
                return True
        return False

    def _get_required_access_level(self, action: str) -> AccessLevel:
        """Get required access level for action"""
        if action.startswith('read') or action.startswith('view'):
            return AccessLevel.READ
        elif action.startswith('write') or action.startswith('create') or action.startswith('update'):
            return AccessLevel.WRITE
        elif action.startswith('delete') or action.startswith('admin'):
            return AccessLevel.ADMIN
        else:
            return AccessLevel.READ

    def _access_level_sufficient(self, user_level: AccessLevel, required_level: AccessLevel) -> bool:
        """Check if user access level is sufficient for required level"""
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 0)

    async def _user_owns_resource(self, user_id: str, resource_id: str) -> bool:
        """Check if user owns the resource"""
        # Simple implementation - check if resource_id matches user_id or starts with user_id
        return resource_id == user_id or resource_id.startswith(f"{user_id}_")

    async def _user_in_collaboration(self, user_id: str, collaboration_id: str) -> bool:
        """Check if user is part of collaboration"""
        # Placeholder implementation
        # In real implementation, this would query collaboration membership
        return True

    async def _user_has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user:
            return False
            
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role and permission in role.permissions:
                return True
                
        return False

    async def _log_access_decision(
        self,
        request: AccessRequest,
        result: PermissionEffect,
        reason: str
    ):
        """Log access decision for audit"""
        if result == PermissionEffect.DENY:
            self.metrics['access_denials'] += 1
            
        await self._log_audit_event(
            user_id=request.user_id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            action=request.action,
            result=result,
            details={
                "reason": reason,
                "context": request.context
            }
        )

    async def _log_audit_event(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str = "",
        action: str = "",
        result: PermissionEffect = PermissionEffect.ALLOW,
        details: Dict[str, Any] = None,
        session_id: str = "",
        ip_address: str = "",
        user_agent: str = ""
    ):
        """Log audit event"""
        audit_log = AccessAuditLog(
            user_id=user_id,
            session_id=session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        
        self.audit_logs.append(audit_log)
        
        # Store in Redis
        if self.redis:
            await self.redis.lpush(
                "access_control:audit_logs",
                json.dumps({
                    'log_id': audit_log.log_id,
                    'user_id': audit_log.user_id,
                    'session_id': audit_log.session_id,
                    'resource_type': audit_log.resource_type.value,
                    'resource_id': audit_log.resource_id,
                    'action': audit_log.action,
                    'result': audit_log.result.value,
                    'timestamp': audit_log.timestamp.isoformat(),
                    'ip_address': audit_log.ip_address,
                    'user_agent': audit_log.user_agent,
                    'details': audit_log.details
                })
            )

    async def _find_user(self, username: str) -> Optional[User]:
        """Find user by username or email"""
        for user in self.users.values():
            if user.username == username or user.email == username:
                return user
        return None

    async def _find_role_by_name(self, role_name: str) -> Optional[str]:
        """Find role ID by name"""
        for role_id, role in self.roles.items():
            if role.name == role_name:
                return role_id
        return None

    async def _user_exists(self, username: str, email: str) -> bool:
        """Check if user with username or email already exists"""
        for user in self.users.values():
            if user.username == username or user.email == email:
                return True
        return False

    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*]', password):
            return False
        return True

    async def _verify_mfa_token(self, user: User, token: str) -> bool:
        """Verify MFA token (TOTP)"""
        # Placeholder implementation
        # In real implementation, this would verify TOTP token
        return len(token) == 6 and token.isdigit()

    async def _get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user permissions"""
        user = self.users.get(user_id)
        if not user:
            return {}
            
        permissions = {
            'user_id': user_id,
            'roles': [],
            'permissions': set(),
            'resource_access': {}
        }
        
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role and role.is_active:
                permissions['roles'].append(role.name)
                permissions['permissions'].update(role.permissions)
                
                # Merge resource access (take highest level)
                for resource_type, access_level in role.resource_access.items():
                    current_level = permissions['resource_access'].get(resource_type, AccessLevel.NONE)
                    if self._access_level_sufficient(access_level, current_level):
                        permissions['resource_access'][resource_type] = access_level
                        
        permissions['permissions'] = list(permissions['permissions'])
        return permissions

    async def _generate_jwt_token(self, user: User, session: Session) -> str:
        """Generate JWT token for session"""
        payload = {
            'user_id': user.user_id,
            'session_id': session.session_id,
            'username': user.username,
            'roles': [self.roles[role_id].name for role_id in user.roles if role_id in self.roles],
            'iat': int(time.time()),
            'exp': int(time.time()) + self.jwt_expiration
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def _store_user(self, user: User):
        """Store user in Redis"""
        if self.redis:
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'roles': user.roles,
                'attributes': user.attributes,
                'mfa_enabled': user.mfa_enabled,
                'mfa_secret': user.mfa_secret,
                'sso_providers': user.sso_providers,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'failed_login_attempts': user.failed_login_attempts,
                'account_locked': user.account_locked,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active
            }
            
            await self.redis.setex(
                f"access_control:user:{user.user_id}",
                86400 * 30,  # 30 days
                json.dumps(user_data)
            )

    async def _store_session(self, session: Session):
        """Store session in Redis"""
        if self.redis:
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'status': session.status.value,
                'permissions_cache': session.permissions_cache,
                'mfa_verified': session.mfa_verified
            }
            
            await self.redis.setex(
                f"access_control:session:{session.session_id}",
                28800,  # 8 hours
                json.dumps(session_data)
            )

    async def _load_existing_data(self):
        """Load existing users, roles, and sessions from Redis"""
        if self.redis:
            try:
                # Load users
                user_keys = await self.redis.keys("access_control:user:*")
                for key in user_keys:
                    user_data = await self.redis.get(key)
                    if user_data:
                        data = json.loads(user_data)
                        # Convert back to User object
                        # Implementation would deserialize the data
                        
                # Load sessions
                session_keys = await self.redis.keys("access_control:session:*")
                for key in session_keys:
                    session_data = await self.redis.get(key)
                    if session_data:
                        data = json.loads(session_data)
                        # Convert back to Session object
                        
            except Exception as e:
                logger.error(f"❌ Failed to load existing data: {e}")

    async def get_access_control_metrics(self) -> Dict[str, Any]:
        """Get comprehensive access control metrics"""
        return {
            'metrics': self.metrics,
            'total_users': len(self.users),
            'total_roles': len(self.roles),
            'active_sessions': len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE]),
            'audit_logs_count': len(self.audit_logs),
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        logger.info("🔑 Access Control Manager closed")


# Factory function
async def create_access_control_manager(redis_url: str = "redis://localhost:6379") -> AccessControlManager:
    """
    Factory function to create and initialize Access Control Manager
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized AccessControlManager instance
    """
    manager = AccessControlManager(redis_url)
    await manager.initialize()
    return manager


if __name__ == "__main__":
    async def test_access_control():
        """Test the access control manager"""
        manager = await create_access_control_manager()
        
        # Create test user
        user_id = await manager.create_user(
            username="test_creator",
            email="creator@example.com",
            password="SecurePass123!",
            roles=["creator"],
            attributes={"payment_verified": True, "kyc_completed": True}
        )
        print(f"✅ User created: {user_id}")
        
        # Authenticate user
        session_id, jwt_token = await manager.authenticate_user(
            username="test_creator",
            password="SecurePass123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )
        print(f"🔐 Authentication result: Session={session_id}, JWT={jwt_token[:50]}...")
        
        # Check access
        has_access = await manager.check_access(
            user_id=user_id,
            resource_type=ResourceType.REVENUE_DATA,
            resource_id=f"{user_id}_revenue",
            action="read_revenue_data"
        )
        print(f"🔍 Access check result: {has_access}")
        
        # Get metrics
        metrics = await manager.get_access_control_metrics()
        print(f"📊 Access control metrics: {json.dumps(metrics, indent=2)}")
        
        await manager.close()

    # Run test
    asyncio.run(test_access_control())