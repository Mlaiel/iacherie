#!/usr/bin/env python3
"""
🔐 SECURITY & VAULT SERVICE
===========================

Unified service combining security authentication/authorization and vault secrets management.
Provides comprehensive security features including multi-factor auth, encryption, threat protection,
and secure secrets management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import hashlib
import secrets
import time
import logging
import json
import base64
import os
import re
import ipaddress
import threading
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from collections import defaultdict, deque
import jwt
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== SECURITY ENUMS =====
class AuthenticationMethod(str, Enum):
    """Authentication methods"""
    PASSWORD = "password"
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    SAML = "saml"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"

class AuthorizationLevel(str, Enum):
    """Authorization levels"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class SecurityThreatLevel(str, Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

class VaultOperation(str, Enum):
    """Vault operation types"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"

# ===== SECURITY DATA CLASSES =====
@dataclass
class SecurityUser:
    """User security profile"""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    is_locked: bool = False
    lock_until: Optional[datetime] = None

@dataclass
class SecuritySession:
    """User session information"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    status: SessionStatus = SessionStatus.ACTIVE
    last_activity: datetime = field(default_factory=datetime.now)
    permissions: List[str] = field(default_factory=list)

@dataclass
class SecurityToken:
    """Security token information"""
    token_id: str
    token_type: str
    user_id: str
    scope: List[str]
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = False

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    timestamp: datetime
    details: Dict[str, Any]
    threat_level: SecurityThreatLevel = SecurityThreatLevel.LOW

@dataclass
class ThreatDetection:
    """Threat detection information"""
    threat_id: str
    threat_type: str
    source_ip: str
    target_resource: str
    severity: SecurityThreatLevel
    detected_at: datetime
    description: str
    mitigation_applied: bool = False

# ===== VAULT DATA CLASSES =====
@dataclass
class VaultSecret:
    """Vault secret data structure"""
    path: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    ttl: Optional[int] = None
    lease_duration: Optional[timedelta] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VaultLease:
    """Vault lease information"""
    lease_id: str
    secret_path: str
    created_at: datetime
    expires_at: datetime
    renewable: bool = True
    ttl_seconds: int = 3600

@dataclass
class VaultAuditLog:
    """Vault audit log entry"""
    timestamp: datetime
    operation: VaultOperation
    path: str
    user_id: Optional[str]
    ip_address: str
    success: bool
    error_message: Optional[str] = None

class SecurityVaultService:
    """Unified Security and Vault Service"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the security vault service"""
        self.config = config
        
        # Security components
        self.users: Dict[str, SecurityUser] = {}
        self.sessions: Dict[str, SecuritySession] = {}
        self.tokens: Dict[str, SecurityToken] = {}
        self.security_events: List[SecurityEvent] = []
        self.threat_detections: List[ThreatDetection] = []
        self.blacklisted_ips: set = set()
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        
        # Vault components
        self.vault_path = config.get('vault_path', '/tmp/vault')
        self.secrets_cache: Dict[str, VaultSecret] = {}
        self.vault_leases: Dict[str, VaultLease] = {}
        self.vault_audit_logs: List[VaultAuditLog] = []
        
        # Initialize encryption
        self._init_encryption()
        
        # Security settings
        self.jwt_secret = config.get('jwt_secret', secrets.token_hex(32))
        self.token_expiry = config.get('token_expiry', 3600)
        self.max_login_attempts = config.get('max_login_attempts', 5)
        self.lockout_duration = config.get('lockout_duration', 300)
        self.rate_limit_window = config.get('rate_limit_window', 60)
        self.rate_limit_max_requests = config.get('rate_limit_max_requests', 100)
        
        logger.info("Security & Vault Service initialized")

    def _init_encryption(self):
        """Initialize encryption components"""
        key_path = self.config.get('vault_key_path', '/tmp/vault.key')
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                self.encryption_key = key_file.read()
        else:
            self.encryption_key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as key_file:
                key_file.write(self.encryption_key)
        
        self.cipher_suite = Fernet(self.encryption_key)

    # ===== USER MANAGEMENT =====
    async def create_user(self, username: str, email: str, password: str, 
                         roles: List[str] = None) -> str:
        """Create a new user"""
        try:
            user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
            
            # Hash password
            password_hash = self._hash_password(password)
            
            user = SecurityUser(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                roles=roles or [],
                permissions=self._get_permissions_for_roles(roles or [])
            )
            
            self.users[user_id] = user
            
            # Log security event
            await self._log_security_event(
                "user_created",
                user_id,
                "127.0.0.1",
                {"username": username, "email": email}
            )
            
            logger.info(f"User created: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise

    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = "127.0.0.1") -> Optional[str]:
        """Authenticate user with username/password"""
        try:
            # Check rate limiting
            if not await self._check_rate_limit(ip_address):
                await self._log_security_event(
                    "rate_limit_exceeded",
                    None,
                    ip_address,
                    {"username": username},
                    SecurityThreatLevel.HIGH
                )
                return None
            
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                await self._log_security_event(
                    "authentication_failed",
                    None,
                    ip_address,
                    {"username": username, "reason": "user_not_found"}
                )
                return None
            
            # Check if user is locked
            if user.is_locked and user.lock_until and datetime.now() < user.lock_until:
                await self._log_security_event(
                    "authentication_failed",
                    user.user_id,
                    ip_address,
                    {"username": username, "reason": "account_locked"}
                )
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_login_attempts:
                    user.is_locked = True
                    user.lock_until = datetime.now() + timedelta(seconds=self.lockout_duration)
                
                await self._log_security_event(
                    "authentication_failed",
                    user.user_id,
                    ip_address,
                    {"username": username, "reason": "invalid_password"}
                )
                return None
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.is_locked = False
            user.lock_until = None
            user.last_login = datetime.now()
            
            # Create session
            session_id = await self._create_session(user.user_id, ip_address)
            
            await self._log_security_event(
                "authentication_success",
                user.user_id,
                ip_address,
                {"username": username}
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None

    async def _create_session(self, user_id: str, ip_address: str, 
                            user_agent: str = "") -> str:
        """Create a new user session"""
        session_id = f"session_{int(time.time())}_{secrets.token_hex(16)}"
        
        session = SecuritySession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.token_expiry),
            ip_address=ip_address,
            user_agent=user_agent,
            permissions=self.users[user_id].permissions
        )
        
        self.sessions[session_id] = session
        return session_id

    async def validate_session(self, session_id: str) -> Optional[SecuritySession]:
        """Validate and return session if valid"""
        session = self.sessions.get(session_id)
        
        if not session:
            return None
        
        if session.status != SessionStatus.ACTIVE:
            return None
        
        if datetime.now() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        return session

    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a user session"""
        if session_id in self.sessions:
            self.sessions[session_id].status = SessionStatus.REVOKED
            return True
        return False

    # ===== JWT TOKEN MANAGEMENT =====
    async def create_jwt_token(self, user_id: str, scope: List[str] = None) -> str:
        """Create JWT token for user"""
        try:
            user = self.users.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            payload = {
                'user_id': user_id,
                'username': user.username,
                'scope': scope or user.permissions,
                'iat': datetime.now(),
                'exp': datetime.now() + timedelta(seconds=self.token_expiry)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            # Store token info
            token_id = f"token_{int(time.time())}_{secrets.token_hex(8)}"
            token_info = SecurityToken(
                token_id=token_id,
                token_type="jwt",
                user_id=user_id,
                scope=scope or user.permissions,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.token_expiry)
            )
            
            self.tokens[token_id] = token_info
            
            return token
            
        except Exception as e:
            logger.error(f"JWT token creation failed: {e}")
            raise

    async def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if user still exists
            user_id = payload.get('user_id')
            if user_id not in self.users:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ===== AUTHORIZATION =====
    async def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        return permission in user.permissions

    async def check_role(self, user_id: str, role: str) -> bool:
        """Check if user has specific role"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        return role in user.roles

    def _get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        """Get permissions based on roles"""
        role_permissions = {
            'user': ['read'],
            'editor': ['read', 'write'],
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'super_admin': ['*']  # All permissions
        }
        
        permissions = set()
        for role in roles:
            if role in role_permissions:
                permissions.update(role_permissions[role])
        
        return list(permissions)

    # ===== THREAT DETECTION =====
    async def detect_threats(self, ip_address: str, user_agent: str = "", 
                           endpoint: str = "") -> Optional[ThreatDetection]:
        """Detect potential security threats"""
        try:
            # Check if IP is blacklisted
            if ip_address in self.blacklisted_ips:
                threat = ThreatDetection(
                    threat_id=f"threat_{int(time.time())}",
                    threat_type="blacklisted_ip",
                    source_ip=ip_address,
                    target_resource=endpoint,
                    severity=SecurityThreatLevel.HIGH,
                    detected_at=datetime.now(),
                    description=f"Request from blacklisted IP: {ip_address}"
                )
                
                self.threat_detections.append(threat)
                return threat
            
            # Check for suspicious patterns
            if self._is_suspicious_user_agent(user_agent):
                threat = ThreatDetection(
                    threat_id=f"threat_{int(time.time())}",
                    threat_type="suspicious_user_agent",
                    source_ip=ip_address,
                    target_resource=endpoint,
                    severity=SecurityThreatLevel.MEDIUM,
                    detected_at=datetime.now(),
                    description=f"Suspicious user agent: {user_agent}"
                )
                
                self.threat_detections.append(threat)
                return threat
            
            return None
            
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            return None

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r'bot',
            r'crawler',
            r'spider',
            r'scraper',
            r'python-requests',
            r'curl',
            r'wget'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False

    async def _check_rate_limit(self, ip_address: str) -> bool:
        """Check rate limiting for IP address"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.rate_limit_window)
        
        # Clean old requests
        self.rate_limits[ip_address] = [
            timestamp for timestamp in self.rate_limits[ip_address]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[ip_address]) >= self.rate_limit_max_requests:
            return False
        
        # Add current request
        self.rate_limits[ip_address].append(now)
        return True

    # ===== VAULT OPERATIONS =====
    async def store_secret(self, path: str, secret: Dict[str, Any], 
                         ttl: Optional[int] = None, user_id: Optional[str] = None) -> bool:
        """Store encrypted secret in vault"""
        try:
            # Encrypt the secret
            secret_data = {
                'data': secret,
                'created_at': datetime.now().isoformat(),
                'ttl': ttl
            }
            
            encrypted_data = self.cipher_suite.encrypt(
                json.dumps(secret_data).encode()
            )
            
            # Store in file system
            full_path = os.path.join(self.vault_path, path.lstrip('/'))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            async with aiofiles.open(full_path, 'wb') as f:
                await f.write(encrypted_data)
            
            # Create vault secret object
            vault_secret = VaultSecret(
                path=path,
                data=secret,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                ttl=ttl,
                lease_duration=timedelta(seconds=ttl) if ttl else None
            )
            
            self.secrets_cache[path] = vault_secret
            
            # Create lease if TTL specified
            if ttl:
                lease_id = f"lease_{int(time.time())}_{secrets.token_hex(8)}"
                lease = VaultLease(
                    lease_id=lease_id,
                    secret_path=path,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(seconds=ttl),
                    ttl_seconds=ttl
                )
                self.vault_leases[lease_id] = lease
            
            # Log audit
            await self._log_vault_audit(
                VaultOperation.WRITE,
                path,
                user_id,
                "127.0.0.1",
                True
            )
            
            logger.info(f"Secret stored: {path}")
            return True
            
        except Exception as e:
            await self._log_vault_audit(
                VaultOperation.WRITE,
                path,
                user_id,
                "127.0.0.1",
                False,
                str(e)
            )
            logger.error(f"Secret storage failed: {e}")
            return False

    async def retrieve_secret(self, path: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt secret from vault"""
        try:
            # Check cache first
            if path in self.secrets_cache:
                secret = self.secrets_cache[path]
                
                # Check if expired
                if secret.ttl and secret.lease_duration:
                    if datetime.now() > secret.created_at + secret.lease_duration:
                        await self.delete_secret(path, user_id)
                        return None
                
                await self._log_vault_audit(
                    VaultOperation.READ,
                    path,
                    user_id,
                    "127.0.0.1",
                    True
                )
                
                return secret.data
            
            # Load from file system
            full_path = os.path.join(self.vault_path, path.lstrip('/'))
            
            if not os.path.exists(full_path):
                await self._log_vault_audit(
                    VaultOperation.READ,
                    path,
                    user_id,
                    "127.0.0.1",
                    False,
                    "Secret not found"
                )
                return None
            
            async with aiofiles.open(full_path, 'rb') as f:
                encrypted_data = await f.read()
            
            # Decrypt
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode())
            
            # Check TTL
            if secret_data.get('ttl'):
                created_at = datetime.fromisoformat(secret_data['created_at'])
                if datetime.now() > created_at + timedelta(seconds=secret_data['ttl']):
                    await self.delete_secret(path, user_id)
                    return None
            
            # Cache the secret
            vault_secret = VaultSecret(
                path=path,
                data=secret_data['data'],
                created_at=datetime.fromisoformat(secret_data['created_at']),
                updated_at=datetime.now(),
                ttl=secret_data.get('ttl')
            )
            
            self.secrets_cache[path] = vault_secret
            
            await self._log_vault_audit(
                VaultOperation.READ,
                path,
                user_id,
                "127.0.0.1",
                True
            )
            
            return secret_data['data']
            
        except Exception as e:
            await self._log_vault_audit(
                VaultOperation.READ,
                path,
                user_id,
                "127.0.0.1",
                False,
                str(e)
            )
            logger.error(f"Secret retrieval failed: {e}")
            return None

    async def delete_secret(self, path: str, user_id: Optional[str] = None) -> bool:
        """Delete secret from vault"""
        try:
            # Remove from cache
            if path in self.secrets_cache:
                del self.secrets_cache[path]
            
            # Remove from file system
            full_path = os.path.join(self.vault_path, path.lstrip('/'))
            
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # Remove associated leases
            expired_leases = [
                lease_id for lease_id, lease in self.vault_leases.items()
                if lease.secret_path == path
            ]
            
            for lease_id in expired_leases:
                del self.vault_leases[lease_id]
            
            await self._log_vault_audit(
                VaultOperation.DELETE,
                path,
                user_id,
                "127.0.0.1",
                True
            )
            
            logger.info(f"Secret deleted: {path}")
            return True
            
        except Exception as e:
            await self._log_vault_audit(
                VaultOperation.DELETE,
                path,
                user_id,
                "127.0.0.1",
                False,
                str(e)
            )
            logger.error(f"Secret deletion failed: {e}")
            return False

    async def list_secrets(self, path_prefix: str = "", user_id: Optional[str] = None) -> List[str]:
        """List secrets with optional path prefix"""
        try:
            secrets_list = []
            
            # List from cache
            for secret_path in self.secrets_cache.keys():
                if secret_path.startswith(path_prefix):
                    secrets_list.append(secret_path)
            
            # List from file system
            vault_dir = os.path.join(self.vault_path, path_prefix.lstrip('/'))
            
            if os.path.exists(vault_dir):
                for root, dirs, files in os.walk(vault_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, self.vault_path)
                        if relative_path not in secrets_list:
                            secrets_list.append(relative_path)
            
            await self._log_vault_audit(
                VaultOperation.LIST,
                path_prefix,
                user_id,
                "127.0.0.1",
                True
            )
            
            return sorted(list(set(secrets_list)))
            
        except Exception as e:
            await self._log_vault_audit(
                VaultOperation.LIST,
                path_prefix,
                user_id,
                "127.0.0.1",
                False,
                str(e)
            )
            logger.error(f"Secret listing failed: {e}")
            return []

    # ===== UTILITY METHODS =====
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            calculated_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return calculated_hash == hash_value
        except ValueError:
            return False

    async def _log_security_event(self, event_type: str, user_id: Optional[str], 
                                ip_address: str, details: Dict[str, Any],
                                threat_level: SecurityThreatLevel = SecurityThreatLevel.LOW):
        """Log security event"""
        event = SecurityEvent(
            event_id=f"event_{int(time.time())}_{secrets.token_hex(4)}",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.now(),
            details=details,
            threat_level=threat_level
        )
        
        self.security_events.append(event)
        
        if threat_level in [SecurityThreatLevel.HIGH, SecurityThreatLevel.CRITICAL]:
            logger.warning(f"Security event: {event_type} - {threat_level.value}")

    async def _log_vault_audit(self, operation: VaultOperation, path: str, 
                             user_id: Optional[str], ip_address: str, 
                             success: bool, error_message: Optional[str] = None):
        """Log vault audit event"""
        audit_log = VaultAuditLog(
            timestamp=datetime.now(),
            operation=operation,
            path=path,
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        
        self.vault_audit_logs.append(audit_log)

    # ===== STATUS AND REPORTING =====
    async def get_security_stats(self) -> Dict[str, Any]:
        """Get security service statistics"""
        active_sessions = sum(1 for s in self.sessions.values() 
                            if s.status == SessionStatus.ACTIVE)
        
        recent_threats = len([t for t in self.threat_detections 
                            if t.detected_at > datetime.now() - timedelta(hours=24)])
        
        return {
            'total_users': len(self.users),
            'active_sessions': active_sessions,
            'total_sessions': len(self.sessions),
            'security_events_24h': len([e for e in self.security_events 
                                      if e.timestamp > datetime.now() - timedelta(hours=24)]),
            'threats_detected_24h': recent_threats,
            'blacklisted_ips': len(self.blacklisted_ips),
            'vault_secrets_count': len(self.secrets_cache),
            'vault_leases_active': len(self.vault_leases),
            'vault_audit_logs_24h': len([log for log in self.vault_audit_logs 
                                       if log.timestamp > datetime.now() - timedelta(hours=24)])
        }

    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        user_sessions = [
            {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'ip_address': session.ip_address,
                'status': session.status.value,
                'last_activity': session.last_activity.isoformat()
            }
            for session in self.sessions.values()
            if session.user_id == user_id
        ]
        
        return user_sessions

    async def cleanup_expired_data(self):
        """Clean up expired sessions, tokens, and secrets"""
        now = datetime.now()
        
        # Clean expired sessions
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at < now
        ]
        
        for session_id in expired_sessions:
            self.sessions[session_id].status = SessionStatus.EXPIRED
        
        # Clean expired tokens
        expired_tokens = [
            token_id for token_id, token in self.tokens.items()
            if token.expires_at < now
        ]
        
        for token_id in expired_tokens:
            self.tokens[token_id].is_revoked = True
        
        # Clean expired vault leases
        expired_leases = [
            lease_id for lease_id, lease in self.vault_leases.items()
            if lease.expires_at < now
        ]
        
        for lease_id in expired_leases:
            lease = self.vault_leases[lease_id]
            await self.delete_secret(lease.secret_path)
            del self.vault_leases[lease_id]
        
        logger.info(f"Cleanup completed: {len(expired_sessions)} sessions, "
                   f"{len(expired_tokens)} tokens, {len(expired_leases)} leases")

# ===== SERVICE FACTORY =====
def create_security_vault_service(config: Dict[str, Any]) -> SecurityVaultService:
    """Factory function to create security vault service"""
    return SecurityVaultService(config)

# Example usage and testing
if __name__ == "__main__":
    async def main():
        config = {
            'vault_path': '/tmp/vault',
            'vault_key_path': '/tmp/vault.key',
            'jwt_secret': 'your-secret-key',
            'token_expiry': 3600,
            'max_login_attempts': 5,
            'lockout_duration': 300,
            'rate_limit_window': 60,
            'rate_limit_max_requests': 100
        }
        
        service = create_security_vault_service(config)
        
        # Create a test user
        user_id = await service.create_user(
            "testuser",
            "test@example.com",
            "secure_password",
            ["user", "editor"]
        )
        
        print(f"User created: {user_id}")
        
        # Authenticate user
        session_id = await service.authenticate_user("testuser", "secure_password")
        print(f"Session created: {session_id}")
        
        # Store a secret
        await service.store_secret(
            "/app/database/password",
            {"password": "super_secret_db_password"},
            ttl=3600,
            user_id=user_id
        )
        
        # Retrieve the secret
        secret = await service.retrieve_secret("/app/database/password", user_id)
        print(f"Retrieved secret: {secret}")
        
        # Get service stats
        stats = await service.get_security_stats()
        print(f"Service stats: {stats}")
        
        # Clean up
        await service.cleanup_expired_data()
    
    asyncio.run(main())