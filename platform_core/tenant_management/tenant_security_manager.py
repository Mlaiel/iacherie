#!/usr/bin/env python3
"""
Tenant Security Manager - Enterprise Security Component
Tenant-level security policies, data isolation, and access control

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive tenant security including:
- Tenant-level security policies and enforcement
- Data isolation and multi-tenancy security
- Access control per tenant with granular permissions
- Security compliance monitoring per tenant
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import secrets
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level enumeration"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AccessType(Enum):
    """Access type enumeration"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    OWNER = "owner"


class IsolationLevel(Enum):
    """Data isolation level"""
    SHARED = "shared"
    ISOLATED = "isolated"
    DEDICATED = "dedicated"


@dataclass
class TenantSecurityPolicy:
    """Tenant security policy definition"""
    policy_id: str
    tenant_id: str
    security_level: SecurityLevel
    isolation_level: IsolationLevel
    allowed_operations: List[str] = field(default_factory=list)
    denied_operations: List[str] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    encryption_required: bool = True
    audit_logging: bool = True
    session_timeout_minutes: int = 480  # 8 hours
    max_concurrent_sessions: int = 10
    password_policy: Dict[str, Any] = field(default_factory=dict)
    compliance_requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TenantUser:
    """Tenant user definition"""
    user_id: str
    tenant_id: str
    username: str
    email: str
    roles: List[str] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    is_active: bool = True
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    password_hash: Optional[str] = None
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TenantRole:
    """Tenant role definition"""
    role_id: str
    tenant_id: str
    role_name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TenantSession:
    """Tenant user session"""
    session_id: str
    user_id: str
    tenant_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True


@dataclass
class SecurityAuditEvent:
    """Security audit event"""
    event_id: str
    tenant_id: str
    user_id: Optional[str]
    event_type: str
    event_description: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_accessed: Optional[str]
    success: bool
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantSecurityManager:
    """
    Enterprise Tenant Security Manager
    
    Provides comprehensive security management for multi-tenant environments
    including policy enforcement, access control, data isolation, and
    compliance monitoring with enterprise-grade security standards.
    """
    
    def __init__(self):
        self.tenant_policies: Dict[str, TenantSecurityPolicy] = {}
        self.tenant_users: Dict[str, Dict[str, TenantUser]] = defaultdict(dict)
        self.tenant_roles: Dict[str, Dict[str, TenantRole]] = defaultdict(dict)
        self.active_sessions: Dict[str, TenantSession] = {}
        self.audit_events: List[SecurityAuditEvent] = []
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        
        # Initialize default roles and policies
        self._initialize_default_configuration()
        
        logger.info("Tenant Security Manager initialized")
    
    def _initialize_default_configuration(self) -> None:
        """Initialize default security configuration"""
        try:
            # Default password policy
            default_password_policy = {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "max_age_days": 90,
                "history_count": 5
            }
            
            # Common compliance requirements
            common_compliance = ["GDPR", "SOC2", "ISO27001"]
            
            logger.info("Default security configuration initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default configuration: {e}")
    
    # Policy Management
    async def create_tenant_security_policy(self, policy: TenantSecurityPolicy) -> bool:
        """Create tenant security policy"""
        try:
            if policy.tenant_id in self.tenant_policies:
                logger.warning(f"Security policy already exists for tenant {policy.tenant_id}")
                return False
            
            # Set default operations if not specified
            if not policy.allowed_operations:
                policy.allowed_operations = [
                    "read_own_data", "write_own_data", "create_content", 
                    "update_content", "delete_own_content"
                ]
            
            # Set default password policy
            if not policy.password_policy:
                policy.password_policy = {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90,
                    "history_count": 5
                }
            
            self.tenant_policies[policy.tenant_id] = policy
            
            # Initialize default roles for tenant
            await self._create_default_tenant_roles(policy.tenant_id)
            
            # Log audit event
            await self._log_audit_event(SecurityAuditEvent(
                event_id=secrets.token_hex(16),
                tenant_id=policy.tenant_id,
                user_id=None,
                event_type="policy_created",
                event_description=f"Security policy created for tenant {policy.tenant_id}",
                ip_address=None,
                user_agent=None,
                resource_accessed="security_policy",
                success=True,
                timestamp=datetime.utcnow()
            ))
            
            logger.info(f"Security policy created for tenant {policy.tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create security policy for tenant {policy.tenant_id}: {e}")
            return False
    
    async def _create_default_tenant_roles(self, tenant_id: str) -> None:
        """Create default roles for tenant"""
        try:
            default_roles = [
                {
                    "role_name": "tenant_admin",
                    "description": "Tenant Administrator",
                    "permissions": {
                        "manage_users", "manage_roles", "manage_content", "view_analytics",
                        "manage_billing", "export_data", "manage_integrations"
                    },
                    "is_system_role": True
                },
                {
                    "role_name": "content_creator",
                    "description": "Content Creator",
                    "permissions": {
                        "create_content", "edit_own_content", "delete_own_content",
                        "view_own_analytics", "manage_collaborations"
                    },
                    "is_system_role": True
                },
                {
                    "role_name": "content_viewer",
                    "description": "Content Viewer",
                    "permissions": {
                        "view_content", "view_public_analytics"
                    },
                    "is_system_role": True
                },
                {
                    "role_name": "billing_manager",
                    "description": "Billing Manager",
                    "permissions": {
                        "view_billing", "manage_subscriptions", "view_usage_reports"
                    },
                    "is_system_role": True
                }
            ]
            
            for role_config in default_roles:
                role = TenantRole(
                    role_id=f"{tenant_id}_{role_config['role_name']}",
                    tenant_id=tenant_id,
                    role_name=role_config["role_name"],
                    description=role_config["description"],
                    permissions=role_config["permissions"],
                    is_system_role=role_config["is_system_role"]
                )
                
                self.tenant_roles[tenant_id][role.role_id] = role
            
            logger.info(f"Default roles created for tenant {tenant_id}")
            
        except Exception as e:
            logger.error(f"Failed to create default roles for tenant {tenant_id}: {e}")
    
    async def update_tenant_security_policy(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant security policy"""
        try:
            if tenant_id not in self.tenant_policies:
                logger.error(f"Security policy not found for tenant {tenant_id}")
                return False
            
            policy = self.tenant_policies[tenant_id]
            
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            policy.updated_at = datetime.utcnow()
            
            # Log audit event
            await self._log_audit_event(SecurityAuditEvent(
                event_id=secrets.token_hex(16),
                tenant_id=tenant_id,
                user_id=None,
                event_type="policy_updated",
                event_description=f"Security policy updated for tenant {tenant_id}",
                ip_address=None,
                user_agent=None,
                resource_accessed="security_policy",
                success=True,
                timestamp=datetime.utcnow(),
                metadata={"updated_fields": list(updates.keys())}
            ))
            
            logger.info(f"Security policy updated for tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update security policy for tenant {tenant_id}: {e}")
            return False
    
    # User Management
    async def create_tenant_user(self, user: TenantUser, password: str) -> bool:
        """Create tenant user"""
        try:
            # Validate user doesn't exist
            if user.user_id in self.tenant_users[user.tenant_id]:
                logger.warning(f"User {user.user_id} already exists in tenant {user.tenant_id}")
                return False
            
            # Validate tenant policy exists
            if user.tenant_id not in self.tenant_policies:
                logger.error(f"No security policy found for tenant {user.tenant_id}")
                return False
            
            # Validate password against policy
            if not await self._validate_password(password, user.tenant_id):
                logger.error(f"Password does not meet policy requirements for tenant {user.tenant_id}")
                return False
            
            # Hash password
            user.password_hash = self._hash_password(password)
            
            # Set default role if none specified
            if not user.roles:
                user.roles = ["content_viewer"]
            
            # Calculate permissions from roles
            user.permissions = await self._calculate_user_permissions(user.tenant_id, user.roles)
            
            self.tenant_users[user.tenant_id][user.user_id] = user
            
            # Log audit event
            await self._log_audit_event(SecurityAuditEvent(
                event_id=secrets.token_hex(16),
                tenant_id=user.tenant_id,
                user_id=user.user_id,
                event_type="user_created",
                event_description=f"User {user.username} created in tenant {user.tenant_id}",
                ip_address=None,
                user_agent=None,
                resource_accessed="user_management",
                success=True,
                timestamp=datetime.utcnow()
            ))
            
            logger.info(f"User {user.user_id} created in tenant {user.tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user {user.user_id}: {e}")
            return False
    
    async def _validate_password(self, password: str, tenant_id: str) -> bool:
        """Validate password against tenant policy"""
        try:
            policy = self.tenant_policies.get(tenant_id)
            if not policy or not policy.password_policy:
                return len(password) >= 8  # Minimum default
            
            pwd_policy = policy.password_policy
            
            # Check length
            if len(password) < pwd_policy.get("min_length", 8):
                return False
            
            # Check character requirements
            if pwd_policy.get("require_uppercase", True) and not any(c.isupper() for c in password):
                return False
            
            if pwd_policy.get("require_lowercase", True) and not any(c.islower() for c in password):
                return False
            
            if pwd_policy.get("require_numbers", True) and not any(c.isdigit() for c in password):
                return False
            
            if pwd_policy.get("require_special_chars", True):
                special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                if not any(c in special_chars for c in password):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate password: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        try:
            salt = secrets.token_hex(32)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return f"{salt}:{pwd_hash.hex()}"
            
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            return ""
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            if not password_hash or ':' not in password_hash:
                return False
            
            salt, stored_hash = password_hash.split(':', 1)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return pwd_hash.hex() == stored_hash
            
        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False
    
    async def _calculate_user_permissions(self, tenant_id: str, roles: List[str]) -> Set[str]:
        """Calculate user permissions from roles"""
        try:
            permissions = set()
            
            for role_name in roles:
                role_id = f"{tenant_id}_{role_name}"
                if role_id in self.tenant_roles[tenant_id]:
                    role = self.tenant_roles[tenant_id][role_id]
                    permissions.update(role.permissions)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to calculate user permissions: {e}")
            return set()
    
    # Authentication and Authorization
    async def authenticate_user(self, tenant_id: str, username: str, password: str, 
                              ip_address: str, user_agent: str) -> Optional[str]:
        """Authenticate user and create session"""
        try:
            # Find user
            user = None
            for user_data in self.tenant_users[tenant_id].values():
                if user_data.username == username:
                    user = user_data
                    break
            
            if not user:
                await self._log_failed_attempt(tenant_id, username, ip_address)
                return None
            
            # Check if account is locked
            if user.account_locked:
                logger.warning(f"Authentication attempt for locked account: {username}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Authentication attempt for inactive user: {username}")
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                await self._handle_failed_login(user, ip_address)
                return None
            
            # Check IP restrictions
            if not await self._check_ip_restrictions(tenant_id, ip_address):
                logger.warning(f"Authentication blocked for IP {ip_address}")
                return None
            
            # Reset failed attempts
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            
            # Create session
            session_id = await self._create_session(user, ip_address, user_agent)
            
            # Log successful authentication
            await self._log_audit_event(SecurityAuditEvent(
                event_id=secrets.token_hex(16),
                tenant_id=tenant_id,
                user_id=user.user_id,
                event_type="authentication_success",
                event_description=f"User {username} authenticated successfully",
                ip_address=ip_address,
                user_agent=user_agent,
                resource_accessed="authentication",
                success=True,
                timestamp=datetime.utcnow()
            ))
            
            return session_id
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return None
    
    async def _log_failed_attempt(self, tenant_id: str, username: str, ip_address: str) -> None:
        """Log failed authentication attempt"""
        try:
            # Log audit event
            await self._log_audit_event(SecurityAuditEvent(
                event_id=secrets.token_hex(16),
                tenant_id=tenant_id,
                user_id=None,
                event_type="authentication_failed",
                event_description=f"Failed authentication attempt for {username}",
                ip_address=ip_address,
                user_agent=None,
                resource_accessed="authentication",
                success=False,
                timestamp=datetime.utcnow()
            ))
            
        except Exception as e:
            logger.error(f"Failed to log failed attempt: {e}")
    
    async def _handle_failed_login(self, user: TenantUser, ip_address: str) -> None:
        """Handle failed login attempt"""
        try:
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.account_locked = True
                
                # Log account lock
                await self._log_audit_event(SecurityAuditEvent(
                    event_id=secrets.token_hex(16),
                    tenant_id=user.tenant_id,
                    user_id=user.user_id,
                    event_type="account_locked",
                    event_description=f"Account locked due to failed login attempts",
                    ip_address=ip_address,
                    user_agent=None,
                    resource_accessed="authentication",
                    success=False,
                    timestamp=datetime.utcnow()
                ))
            
        except Exception as e:
            logger.error(f"Failed to handle failed login: {e}")
    
    async def _check_ip_restrictions(self, tenant_id: str, ip_address: str) -> bool:
        """Check IP address restrictions"""
        try:
            policy = self.tenant_policies.get(tenant_id)
            if not policy:
                return True
            
            # Check blacklist
            if ip_address in policy.ip_blacklist:
                return False
            
            # Check whitelist (if configured)
            if policy.ip_whitelist and ip_address not in policy.ip_whitelist:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check IP restrictions: {e}")
            return True
    
    async def _create_session(self, user: TenantUser, ip_address: str, user_agent: str) -> str:
        """Create user session"""
        try:
            policy = self.tenant_policies[user.tenant_id]
            session_id = secrets.token_urlsafe(32)
            
            session = TenantSession(
                session_id=session_id,
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=policy.session_timeout_minutes)
            )
            
            self.active_sessions[session_id] = session
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return ""
    
    async def validate_session(self, session_id: str) -> Optional[TenantSession]:
        """Validate user session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            # Check if session is expired
            if datetime.utcnow() > session.expires_at:
                session.is_active = False
                return None
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to validate session: {e}")
            return None
    
    async def check_permission(self, session_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        try:
            session = await self.validate_session(session_id)
            if not session:
                return False
            
            user = self.tenant_users[session.tenant_id].get(session.user_id)
            if not user or not user.is_active:
                return False
            
            return permission in user.permissions
            
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False
    
    # Audit and Compliance
    async def _log_audit_event(self, event: SecurityAuditEvent) -> None:
        """Log security audit event"""
        try:
            self.audit_events.append(event)
            
            # Keep only last 100,000 events
            if len(self.audit_events) > 100000:
                self.audit_events = self.audit_events[-100000:]
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def get_audit_events(self, tenant_id: str, hours: int = 24,
                             event_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get audit events for tenant"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            events = [
                e for e in self.audit_events
                if e.tenant_id == tenant_id and e.timestamp >= start_time
            ]
            
            if event_types:
                events = [e for e in events if e.event_type in event_types]
            
            return [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "event_description": e.event_description,
                    "user_id": e.user_id,
                    "ip_address": e.ip_address,
                    "resource_accessed": e.resource_accessed,
                    "success": e.success,
                    "timestamp": e.timestamp.isoformat(),
                    "metadata": e.metadata
                }
                for e in events
            ]
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    async def get_security_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get security summary for tenant"""
        try:
            policy = self.tenant_policies.get(tenant_id)
            if not policy:
                return {"error": "Tenant not found"}
            
            users = self.tenant_users[tenant_id]
            
            # Recent audit events (last 24 hours)
            recent_events = await self.get_audit_events(tenant_id, hours=24)
            
            # Active sessions
            active_sessions = [
                s for s in self.active_sessions.values()
                if s.tenant_id == tenant_id and s.is_active
            ]
            
            summary = {
                "tenant_id": tenant_id,
                "security_level": policy.security_level.value,
                "isolation_level": policy.isolation_level.value,
                "total_users": len(users),
                "active_users": len([u for u in users.values() if u.is_active]),
                "locked_users": len([u for u in users.values() if u.account_locked]),
                "active_sessions": len(active_sessions),
                "recent_events": len(recent_events),
                "failed_logins_24h": len([e for e in recent_events if e["event_type"] == "authentication_failed"]),
                "policy_updated": policy.updated_at.isoformat(),
                "compliance_requirements": policy.compliance_requirements,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_tenant_security_manager() -> TenantSecurityManager:
    """Factory function to create a Tenant Security Manager"""
    return TenantSecurityManager()


# Example usage
async def main():
    """Example usage of Tenant Security Manager"""
    security_manager = create_tenant_security_manager()
    
    # Create tenant security policy
    policy = TenantSecurityPolicy(
        policy_id="tenant_123_policy",
        tenant_id="tenant_123",
        security_level=SecurityLevel.ENHANCED,
        isolation_level=IsolationLevel.ISOLATED,
        compliance_requirements=["GDPR", "SOC2"]
    )
    
    await security_manager.create_tenant_security_policy(policy)
    
    # Create tenant user
    user = TenantUser(
        user_id="user_456",
        tenant_id="tenant_123",
        username="john.creator",
        email="john@example.com",
        roles=["content_creator"]
    )
    
    await security_manager.create_tenant_user(user, "SecurePassword123!")
    
    # Authenticate user
    session_id = await security_manager.authenticate_user(
        "tenant_123", "john.creator", "SecurePassword123!", "192.168.1.100", "Mozilla/5.0"
    )
    
    if session_id:
        print(f"User authenticated, session: {session_id}")
        
        # Check permission
        can_create = await security_manager.check_permission(session_id, "create_content")
        print(f"Can create content: {can_create}")
    
    # Get security summary
    summary = await security_manager.get_security_summary("tenant_123")
    print(f"Security Summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())