"""
Authentication Utilities - Security Expert Implementation
========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise authentication and authorization system with multi-factor authentication.
"""

import logging
import secrets
import time
import qrcode
import pyotp
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"
    API_KEY = "api_key"
    OAUTH = "oauth"


class UserRole(Enum):
    """User roles in the system"""
    ADMIN = "admin"
    CREATOR = "creator"
    MODERATOR = "moderator"
    USER = "user"
    API_CLIENT = "api_client"


@dataclass
class AuthSession:
    """Authentication session data"""
    user_id: str
    session_id: str
    roles: List[UserRole]
    permissions: List[str]
    created_at: datetime
    expires_at: datetime
    mfa_verified: bool = False
    last_activity: datetime = None
    ip_address: str = ""
    user_agent: str = ""


@dataclass
class AuthAttempt:
    """Authentication attempt tracking"""
    user_id: str
    method: AuthMethod
    success: bool
    timestamp: datetime
    ip_address: str
    failure_reason: str = ""


class AuthUtilities:
    """
    Enterprise authentication system implementing:
    - Multi-factor authentication (MFA)
    - Role-based access control (RBAC)
    - Session management
    - Rate limiting and security monitoring
    - OAuth integration support
    """
    
    def __init__(self):
        """Initialize authentication system"""
        # Session storage (in production, use Redis/database)
        self.active_sessions: Dict[str, AuthSession] = {}
        self.auth_attempts: List[AuthAttempt] = []
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour
        self.password_min_length = 8
        
        # Failed attempt tracking
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        
        # API key management
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # TOTP secrets (in production, store encrypted in database)
        self.totp_secrets: Dict[str, str] = {}
        
        logger.info("AuthUtilities initialized with enterprise security")
    
    def register_user(self, user_id: str, password: str, email: str, 
                     roles: List[UserRole] = None) -> Dict[str, Any]:
        """Register a new user with security validations"""
        try:
            # Validate password strength
            if not self._validate_password_strength(password):
                raise ValueError("Password does not meet security requirements")
            
            # Hash password
            from .encryption_utilities import encryption_utils
            password_hash = encryption_utils.hash_password(password)
            
            # Generate TOTP secret for MFA
            totp_secret = pyotp.random_base32()
            self.totp_secrets[user_id] = totp_secret
            
            if roles is None:
                roles = [UserRole.USER]
            
            user_data = {
                "user_id": user_id,
                "email": email,
                "password_hash": password_hash,
                "roles": [role.value for role in roles],
                "totp_secret": totp_secret,
                "created_at": datetime.now().isoformat(),
                "mfa_enabled": False,
                "last_login": None,
                "login_count": 0
            }
            
            logger.info(f"User registered: {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "totp_secret": totp_secret,
                "qr_code_url": self._generate_totp_qr_url(user_id, totp_secret)
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise
    
    def authenticate_user(self, user_id: str, password: str, 
                         totp_code: Optional[str] = None,
                         ip_address: str = "", user_agent: str = "") -> Dict[str, Any]:
        """Authenticate user with optional MFA"""
        try:
            # Check if account is locked
            if self._is_account_locked(user_id):
                self._log_auth_attempt(user_id, AuthMethod.PASSWORD, False, 
                                     ip_address, "Account locked")
                raise ValueError("Account is temporarily locked due to multiple failed attempts")
            
            # Verify password (mock - in production, fetch from database)
            if not self._verify_user_password(user_id, password):
                self._handle_failed_login(user_id, ip_address)
                self._log_auth_attempt(user_id, AuthMethod.PASSWORD, False, 
                                     ip_address, "Invalid password")
                raise ValueError("Invalid credentials")
            
            # Check if MFA is required
            mfa_verified = True
            if self._is_mfa_enabled(user_id):
                if not totp_code:
                    return {
                        "success": False,
                        "requires_mfa": True,
                        "message": "MFA verification required"
                    }
                
                mfa_verified = self.verify_totp(user_id, totp_code)
                if not mfa_verified:
                    self._log_auth_attempt(user_id, AuthMethod.TOTP, False, 
                                         ip_address, "Invalid TOTP")
                    raise ValueError("Invalid MFA code")
            
            # Create session
            session = self._create_session(user_id, ip_address, user_agent, mfa_verified)
            
            # Clear failed attempts
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            
            self._log_auth_attempt(user_id, AuthMethod.PASSWORD, True, ip_address)
            
            logger.info(f"User authenticated: {user_id}")
            return {
                "success": True,
                "session_id": session.session_id,
                "expires_at": session.expires_at.isoformat(),
                "roles": [role.value for role in session.roles],
                "mfa_verified": mfa_verified
            }
            
        except Exception as e:
            logger.error(f"Authentication failed for {user_id}: {e}")
            raise
    
    def verify_session(self, session_id: str) -> Optional[AuthSession]:
        """Verify and return session if valid"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Check if session has expired
            if datetime.now() > session.expires_at:
                del self.active_sessions[session_id]
                logger.info(f"Session expired: {session_id}")
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
            
            return session
            
        except Exception as e:
            logger.error(f"Session verification failed: {e}")
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            if session_id in self.active_sessions:
                user_id = self.active_sessions[session_id].user_id
                del self.active_sessions[session_id]
                logger.info(f"User logged out: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def enable_mfa(self, user_id: str) -> Dict[str, Any]:
        """Enable MFA for user and return setup information"""
        try:
            if user_id not in self.totp_secrets:
                totp_secret = pyotp.random_base32()
                self.totp_secrets[user_id] = totp_secret
            else:
                totp_secret = self.totp_secrets[user_id]
            
            qr_url = self._generate_totp_qr_url(user_id, totp_secret)
            
            return {
                "totp_secret": totp_secret,
                "qr_code_url": qr_url,
                "manual_entry_key": totp_secret
            }
            
        except Exception as e:
            logger.error(f"MFA enablement failed: {e}")
            raise
    
    def verify_totp(self, user_id: str, totp_code: str) -> bool:
        """Verify TOTP code for user"""
        try:
            if user_id not in self.totp_secrets:
                return False
            
            totp = pyotp.TOTP(self.totp_secrets[user_id])
            return totp.verify(totp_code)
            
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    def generate_api_key(self, user_id: str, name: str, 
                        permissions: List[str] = None) -> str:
        """Generate API key for user"""
        try:
            from .encryption_utilities import encryption_utils
            api_key = encryption_utils.generate_api_key("ak", 32)
            
            self.api_keys[api_key] = {
                "user_id": user_id,
                "name": name,
                "permissions": permissions or [],
                "created_at": datetime.now(),
                "last_used": None,
                "usage_count": 0
            }
            
            logger.info(f"API key generated for user: {user_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"API key generation failed: {e}")
            raise
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return associated data"""
        try:
            if api_key in self.api_keys:
                key_data = self.api_keys[api_key]
                key_data["last_used"] = datetime.now()
                key_data["usage_count"] += 1
                return key_data
            return None
            
        except Exception as e:
            logger.error(f"API key verification failed: {e}")
            return None
    
    def check_permission(self, session_id: str, required_permission: str) -> bool:
        """Check if session has required permission"""
        try:
            session = self.verify_session(session_id)
            if not session:
                return False
            
            # Admin has all permissions
            if UserRole.ADMIN in session.roles:
                return True
            
            return required_permission in session.permissions
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for user"""
        try:
            user_sessions = []
            for session_id, session in self.active_sessions.items():
                if session.user_id == user_id:
                    user_sessions.append({
                        "session_id": session_id,
                        "created_at": session.created_at.isoformat(),
                        "expires_at": session.expires_at.isoformat(),
                        "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                        "ip_address": session.ip_address,
                        "mfa_verified": session.mfa_verified
                    })
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def revoke_all_sessions(self, user_id: str) -> int:
        """Revoke all sessions for user"""
        try:
            revoked_count = 0
            sessions_to_remove = []
            
            for session_id, session in self.active_sessions.items():
                if session.user_id == user_id:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
                revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} sessions for user: {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Session revocation failed: {e}")
            return 0
    
    def get_auth_statistics(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        try:
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            
            recent_attempts = [a for a in self.auth_attempts if a.timestamp >= last_24h]
            
            return {
                "active_sessions": len(self.active_sessions),
                "locked_accounts": len(self.locked_accounts),
                "total_auth_attempts_24h": len(recent_attempts),
                "successful_logins_24h": len([a for a in recent_attempts if a.success]),
                "failed_attempts_24h": len([a for a in recent_attempts if not a.success]),
                "api_keys_total": len(self.api_keys),
                "mfa_enabled_users": len(self.totp_secrets)
            }
            
        except Exception as e:
            logger.error(f"Failed to get auth statistics: {e}")
            return {}
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < self.password_min_length:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _verify_user_password(self, user_id: str, password: str) -> bool:
        """Verify user password (mock implementation)"""
        # In production, fetch hashed password from database and verify
        from .encryption_utilities import encryption_utils
        
        # Mock: assume password is correct for demo
        # In real implementation: return encryption_utils.verify_password(password, stored_hash)
        return len(password) >= self.password_min_length
    
    def _is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for user"""
        # In production, check user preferences in database
        return user_id in self.totp_secrets
    
    def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked"""
        if user_id in self.locked_accounts:
            lock_time = self.locked_accounts[user_id]
            if datetime.now() - lock_time < timedelta(seconds=self.lockout_duration):
                return True
            else:
                del self.locked_accounts[user_id]
        return False
    
    def _handle_failed_login(self, user_id: str, ip_address: str):
        """Handle failed login attempt"""
        now = datetime.now()
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        # Remove attempts older than 15 minutes
        cutoff_time = now - timedelta(minutes=15)
        self.failed_attempts[user_id] = [
            attempt_time for attempt_time in self.failed_attempts[user_id]
            if attempt_time > cutoff_time
        ]
        
        self.failed_attempts[user_id].append(now)
        
        # Lock account if too many failed attempts
        if len(self.failed_attempts[user_id]) >= self.max_login_attempts:
            self.locked_accounts[user_id] = now
            logger.warning(f"Account locked due to failed attempts: {user_id}")
    
    def _create_session(self, user_id: str, ip_address: str, user_agent: str, 
                       mfa_verified: bool) -> AuthSession:
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        
        # Mock user roles (in production, fetch from database)
        roles = [UserRole.USER]  # Default role
        permissions = ["read", "write"]  # Default permissions
        
        session = AuthSession(
            user_id=user_id,
            session_id=session_id,
            roles=roles,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.session_timeout),
            mfa_verified=mfa_verified,
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def _generate_totp_qr_url(self, user_id: str, secret: str) -> str:
        """Generate TOTP QR code URL"""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name="Ainflue Platform"
        )
    
    def _log_auth_attempt(self, user_id: str, method: AuthMethod, success: bool,
                         ip_address: str, failure_reason: str = ""):
        """Log authentication attempt"""
        attempt = AuthAttempt(
            user_id=user_id,
            method=method,
            success=success,
            timestamp=datetime.now(),
            ip_address=ip_address,
            failure_reason=failure_reason
        )
        
        self.auth_attempts.append(attempt)
        
        # Keep only last 1000 attempts
        if len(self.auth_attempts) > 1000:
            self.auth_attempts = self.auth_attempts[-500:]


# Global instance for easy access
auth_utils = AuthUtilities()