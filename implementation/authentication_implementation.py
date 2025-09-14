"""Authentication Implementation - Enterprise Identity & Access Management System

Advanced authentication system for Ainflue creator economy platform with
multi-factor authentication, biometric support, and enterprise security protocols.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import secrets
import hmac
import base64
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import jwt
import bcrypt
import pyotp
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)


class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    
    EMAIL_PASSWORD = "email_password"
    PHONE_OTP = "phone_otp"
    GOOGLE_OAUTH = "google_oauth"
    FACEBOOK_OAUTH = "facebook_oauth"
    APPLE_OAUTH = "apple_oauth"
    TWITTER_OAUTH = "twitter_oauth"
    LINKEDIN_OAUTH = "linkedin_oauth"
    GITHUB_OAUTH = "github_oauth"
    BIOMETRIC = "biometric"
    HARDWARE_KEY = "hardware_key"
    SSO_SAML = "sso_saml"
    SSO_OIDC = "sso_oidc"


class MFAMethod(Enum):
    """Multi-factor authentication methods"""
    
    TOTP = "totp"  # Time-based OTP
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR_APP = "authenticator_app"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"
    BACKUP_CODES = "backup_codes"
    PUSH_NOTIFICATION = "push_notification"


class SessionType(Enum):
    """Session types for different access levels"""
    
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"
    API = "api"
    TEMPORARY = "temporary"
    IMPERSONATION = "impersonation"


class AuthenticationStatus(Enum):
    """Authentication attempt status"""
    
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING_MFA = "pending_mfa"
    EXPIRED = "expired"
    REQUIRES_VERIFICATION = "requires_verification"
    ACCOUNT_LOCKED = "account_locked"
    RATE_LIMITED = "rate_limited"


@dataclass
class UserCredentials:
    """User authentication credentials"""
    user_id: str
    email: str
    phone: Optional[str] = None
    password_hash: Optional[str] = None
    salt: Optional[str] = None
    oauth_providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    biometric_templates: Dict[str, str] = field(default_factory=dict)
    hardware_keys: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    email_verified: bool = False
    phone_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MFAConfiguration:
    """Multi-factor authentication configuration"""
    user_id: str
    is_enabled: bool
    primary_method: Optional[MFAMethod] = None
    backup_methods: List[MFAMethod] = field(default_factory=list)
    totp_secret: Optional[str] = None
    backup_codes: List[str] = field(default_factory=list)
    trusted_devices: List[str] = field(default_factory=list)
    require_mfa_for_sensitive: bool = True
    mfa_session_timeout: int = 3600  # 1 hour
    last_mfa_at: Optional[datetime] = None


@dataclass
class AuthenticationSession:
    """User authentication session"""
    session_id: str
    user_id: str
    session_type: SessionType
    authentication_methods: List[AuthenticationMethod]
    mfa_completed: bool
    device_info: Dict[str, Any]
    ip_address: str
    user_agent: str
    location: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class AuthenticationAttempt:
    """Authentication attempt tracking"""
    attempt_id: str
    user_id: Optional[str]
    email: Optional[str]
    ip_address: str
    user_agent: str
    authentication_method: AuthenticationMethod
    status: AuthenticationStatus
    failure_reason: Optional[str] = None
    device_fingerprint: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityEvent:
    """Security-related events"""
    event_id: str
    user_id: Optional[str]
    event_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    metadata: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


@dataclass
class DeviceInfo:
    """Device information for authentication"""
    device_id: str
    device_name: str
    device_type: str  # 'mobile', 'desktop', 'tablet', 'other'
    platform: str
    browser: Optional[str] = None
    fingerprint: str = ""
    is_trusted: bool = False
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)


class AuthenticationImplementation:
    """
    Enterprise Authentication Implementation for Ainflue Creator Economy Platform
    
    Comprehensive identity and access management system with multi-factor authentication,
    OAuth integration, biometric support, and advanced security monitoring.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Authentication data stores
        self.user_credentials: Dict[str, UserCredentials] = {}
        self.mfa_configurations: Dict[str, MFAConfiguration] = {}
        self.active_sessions: Dict[str, AuthenticationSession] = {}
        self.authentication_attempts: List[AuthenticationAttempt] = []
        self.security_events: List[SecurityEvent] = []
        self.trusted_devices: Dict[str, List[DeviceInfo]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Security configuration
        self.security_config = self.config.get("security", {
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "password_min_length": 12,
            "password_require_special": True,
            "password_require_numbers": True,
            "password_require_uppercase": True,
            "session_timeout_hours": 24,
            "mfa_grace_period_hours": 1,
            "rate_limit_window_minutes": 15,
            "rate_limit_max_attempts": 10,
            "jwt_secret": secrets.token_urlsafe(32),
            "jwt_algorithm": "HS256"
        })
        
        # OAuth providers configuration
        self.oauth_providers = self._initialize_oauth_providers()
        
        # Performance metrics
        self.metrics = {
            "total_authentication_attempts": 0,
            "successful_authentications": 0,
            "failed_authentications": 0,
            "mfa_activations": 0,
            "security_events": 0,
            "active_sessions": 0,
            "average_session_duration": 0.0
        }
    
    async def register_user(
        self,
        email: str,
        password: str,
        phone: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new user with email and password"""
        
        # Validate email format
        if not self._is_valid_email(email):
            return {"success": False, "error": "Invalid email format"}
        
        # Check if user already exists
        if any(cred.email == email for cred in self.user_credentials.values()):
            return {"success": False, "error": "User already exists"}
        
        # Validate password strength
        password_validation = self._validate_password_strength(password)
        if not password_validation["valid"]:
            return {"success": False, "error": password_validation["error"]}
        
        # Generate user ID and salt
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        salt = bcrypt.gensalt()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Create user credentials
        credentials = UserCredentials(
            user_id=user_id,
            email=email,
            phone=phone,
            password_hash=password_hash,
            salt=salt.decode('utf-8')
        )
        
        self.user_credentials[user_id] = credentials
        
        # Initialize MFA configuration (disabled by default)
        mfa_config = MFAConfiguration(
            user_id=user_id,
            is_enabled=False
        )
        self.mfa_configurations[user_id] = mfa_config
        
        # Log security event
        await self._log_security_event(
            user_id=user_id,
            event_type="user_registration",
            severity="low",
            description=f"New user registered: {email}",
            metadata={"email": email, "phone": phone}
        )
        
        self.logger.info(f"New user registered: {user_id} ({email})")
        
        return {
            "success": True,
            "user_id": user_id,
            "email_verification_required": True,
            "phone_verification_required": bool(phone)
        }
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        device_info: Dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        
        attempt_id = f"attempt_{uuid.uuid4().hex[:12]}"
        
        # Rate limiting check
        if not await self._check_rate_limit(ip_address):
            await self._log_authentication_attempt(
                attempt_id=attempt_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
                status=AuthenticationStatus.RATE_LIMITED
            )
            return {"success": False, "error": "Rate limit exceeded", "retry_after": 900}
        
        # Find user by email
        user_credentials = next(
            (cred for cred in self.user_credentials.values() if cred.email == email),
            None
        )
        
        if not user_credentials:
            await self._log_authentication_attempt(
                attempt_id=attempt_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
                status=AuthenticationStatus.FAILED,
                failure_reason="User not found"
            )
            return {"success": False, "error": "Invalid credentials"}
        
        # Check if account is active
        if not user_credentials.is_active:
            await self._log_authentication_attempt(
                attempt_id=attempt_id,
                user_id=user_credentials.user_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
                status=AuthenticationStatus.BLOCKED,
                failure_reason="Account inactive"
            )
            return {"success": False, "error": "Account is inactive"}
        
        # Check account lockout
        if await self._is_account_locked(user_credentials.user_id):
            await self._log_authentication_attempt(
                attempt_id=attempt_id,
                user_id=user_credentials.user_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
                status=AuthenticationStatus.ACCOUNT_LOCKED,
                failure_reason="Account locked due to failed attempts"
            )
            return {"success": False, "error": "Account is locked"}
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user_credentials.password_hash.encode('utf-8')):
            await self._log_authentication_attempt(
                attempt_id=attempt_id,
                user_id=user_credentials.user_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
                status=AuthenticationStatus.FAILED,
                failure_reason="Invalid password"
            )
            
            # Check if account should be locked
            await self._check_and_apply_account_lockout(user_credentials.user_id)
            
            return {"success": False, "error": "Invalid credentials"}
        
        # Password verified - check MFA requirement
        mfa_config = self.mfa_configurations.get(user_credentials.user_id)
        requires_mfa = mfa_config and mfa_config.is_enabled
        
        # Create preliminary session
        session = await self._create_session(
            user_id=user_credentials.user_id,
            authentication_methods=[AuthenticationMethod.EMAIL_PASSWORD],
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_completed=not requires_mfa,
            session_type=SessionType.STANDARD if not requires_mfa else SessionType.TEMPORARY
        )
        
        # Log successful authentication
        await self._log_authentication_attempt(
            attempt_id=attempt_id,
            user_id=user_credentials.user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            authentication_method=AuthenticationMethod.EMAIL_PASSWORD,
            status=AuthenticationStatus.PENDING_MFA if requires_mfa else AuthenticationStatus.SUCCESS
        )
        
        # Check for suspicious activity
        await self._analyze_authentication_patterns(user_credentials.user_id, device_info, ip_address)
        
        if requires_mfa:
            return {
                "success": True,
                "requires_mfa": True,
                "available_mfa_methods": self._get_available_mfa_methods(user_credentials.user_id),
                "temporary_session_id": session.session_id
            }
        else:
            # Generate JWT token
            jwt_token = self._generate_jwt_token(user_credentials.user_id, session.session_id)
            
            return {
                "success": True,
                "user_id": user_credentials.user_id,
                "session_id": session.session_id,
                "access_token": jwt_token,
                "expires_at": session.expires_at.isoformat(),
                "requires_mfa": False
            }
    
    async def complete_mfa_authentication(
        self,
        temporary_session_id: str,
        mfa_method: MFAMethod,
        mfa_code: str,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete multi-factor authentication"""
        
        # Verify temporary session
        temp_session = self.active_sessions.get(temporary_session_id)
        if not temp_session or temp_session.session_type != SessionType.TEMPORARY:
            return {"success": False, "error": "Invalid or expired temporary session"}
        
        user_id = temp_session.user_id
        mfa_config = self.mfa_configurations.get(user_id)
        
        if not mfa_config or not mfa_config.is_enabled:
            return {"success": False, "error": "MFA not configured"}
        
        # Verify MFA code
        mfa_valid = await self._verify_mfa_code(user_id, mfa_method, mfa_code)
        
        if not mfa_valid:
            await self._log_security_event(
                user_id=user_id,
                event_type="mfa_failed",
                severity="medium",
                description=f"Failed MFA attempt with method: {mfa_method.value}",
                metadata={"mfa_method": mfa_method.value, "device_info": device_info},
                ip_address=temp_session.ip_address,
                user_agent=temp_session.user_agent
            )
            return {"success": False, "error": "Invalid MFA code"}
        
        # MFA successful - upgrade session
        temp_session.session_type = SessionType.STANDARD
        temp_session.mfa_completed = True
        temp_session.authentication_methods.append(self._mfa_method_to_auth_method(mfa_method))
        
        # Update MFA timestamp
        mfa_config.last_mfa_at = datetime.utcnow()
        
        # Check if device should be trusted
        if device_info.get("trust_device"):
            await self._trust_device(user_id, device_info)
        
        # Generate JWT token
        jwt_token = self._generate_jwt_token(user_id, temp_session.session_id)
        
        # Log security event
        await self._log_security_event(
            user_id=user_id,
            event_type="mfa_completed",
            severity="low",
            description=f"MFA completed with method: {mfa_method.value}",
            metadata={"mfa_method": mfa_method.value, "device_info": device_info},
            ip_address=temp_session.ip_address,
            user_agent=temp_session.user_agent
        )
        
        self.logger.info(f"MFA authentication completed for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "session_id": temp_session.session_id,
            "access_token": jwt_token,
            "expires_at": temp_session.expires_at.isoformat()
        }
    
    async def enable_mfa(
        self,
        user_id: str,
        primary_method: MFAMethod,
        backup_methods: Optional[List[MFAMethod]] = None
    ) -> Dict[str, Any]:
        """Enable multi-factor authentication for a user"""
        
        if user_id not in self.user_credentials:
            return {"success": False, "error": "User not found"}
        
        mfa_config = self.mfa_configurations.get(user_id)
        if not mfa_config:
            mfa_config = MFAConfiguration(user_id=user_id, is_enabled=False)
            self.mfa_configurations[user_id] = mfa_config
        
        # Generate TOTP secret if needed
        totp_secret = None
        qr_code = None
        
        if primary_method == MFAMethod.TOTP or primary_method == MFAMethod.AUTHENTICATOR_APP:
            totp_secret = pyotp.random_base32()
            mfa_config.totp_secret = totp_secret
            
            # Generate QR code for authenticator app setup
            user_email = self.user_credentials[user_id].email
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=user_email,
                issuer_name="Ainflue"
            )
            
            qr_img = qrcode.make(totp_uri)
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_code = base64.b64encode(qr_buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        mfa_config.backup_codes = backup_codes
        
        # Update MFA configuration
        mfa_config.is_enabled = True
        mfa_config.primary_method = primary_method
        mfa_config.backup_methods = backup_methods or []
        
        # Log security event
        await self._log_security_event(
            user_id=user_id,
            event_type="mfa_enabled",
            severity="low",
            description=f"MFA enabled with primary method: {primary_method.value}",
            metadata={"primary_method": primary_method.value, "backup_methods": [m.value for m in (backup_methods or [])]}
        )
        
        self.metrics["mfa_activations"] += 1
        
        self.logger.info(f"MFA enabled for user {user_id}")
        
        result = {
            "success": True,
            "backup_codes": backup_codes,
            "primary_method": primary_method.value
        }
        
        if qr_code:
            result.update({
                "totp_secret": totp_secret,
                "qr_code": qr_code
            })
        
        return result
    
    async def oauth_authenticate(
        self,
        provider: str,
        authorization_code: str,
        device_info: Dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Authenticate user via OAuth provider"""
        
        if provider not in self.oauth_providers:
            return {"success": False, "error": "Unsupported OAuth provider"}
        
        # Exchange authorization code for access token
        oauth_data = await self._exchange_oauth_code(provider, authorization_code)
        
        if not oauth_data.get("success"):
            return {"success": False, "error": "OAuth authentication failed"}
        
        # Get user information from OAuth provider
        user_info = await self._get_oauth_user_info(provider, oauth_data["access_token"])
        
        if not user_info.get("success"):
            return {"success": False, "error": "Failed to get user information"}
        
        oauth_email = user_info["email"]
        oauth_user_id = user_info["user_id"]
        
        # Find or create user
        user_credentials = next(
            (cred for cred in self.user_credentials.values() if cred.email == oauth_email),
            None
        )
        
        if not user_credentials:
            # Create new user with OAuth
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_credentials = UserCredentials(
                user_id=user_id,
                email=oauth_email,
                email_verified=True  # OAuth providers verify emails
            )
            
            # Initialize MFA configuration
            mfa_config = MFAConfiguration(user_id=user_id, is_enabled=False)
            self.mfa_configurations[user_id] = mfa_config
            
            self.user_credentials[user_id] = user_credentials
        
        # Update OAuth provider information
        auth_method = AuthenticationMethod(f"{provider}_oauth")
        user_credentials.oauth_providers[provider] = {
            "oauth_user_id": oauth_user_id,
            "access_token": oauth_data["access_token"],
            "refresh_token": oauth_data.get("refresh_token"),
            "last_login": datetime.utcnow().isoformat()
        }
        
        # Create session
        session = await self._create_session(
            user_id=user_credentials.user_id,
            authentication_methods=[auth_method],
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_completed=True,  # OAuth is considered secure
            session_type=SessionType.STANDARD
        )
        
        # Generate JWT token
        jwt_token = self._generate_jwt_token(user_credentials.user_id, session.session_id)
        
        # Log authentication
        await self._log_authentication_attempt(
            attempt_id=f"oauth_{uuid.uuid4().hex[:8]}",
            user_id=user_credentials.user_id,
            email=oauth_email,
            ip_address=ip_address,
            user_agent=user_agent,
            authentication_method=auth_method,
            status=AuthenticationStatus.SUCCESS
        )
        
        self.logger.info(f"OAuth authentication successful for user {user_credentials.user_id} via {provider}")
        
        return {
            "success": True,
            "user_id": user_credentials.user_id,
            "session_id": session.session_id,
            "access_token": jwt_token,
            "expires_at": session.expires_at.isoformat(),
            "provider": provider
        }
    
    async def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        # Invalidate session
        session.is_active = False
        del self.active_sessions[session_id]
        
        # Log security event
        await self._log_security_event(
            user_id=session.user_id,
            event_type="user_logout",
            severity="low",
            description="User logged out",
            metadata={"session_id": session_id},
            ip_address=session.ip_address,
            user_agent=session.user_agent
        )
        
        self.logger.info(f"User {session.user_id} logged out")
        
        return {"success": True}
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate active session"""
        
        session = self.active_sessions.get(session_id)
        
        if not session or not session.is_active:
            return {"valid": False, "error": "Session not found or inactive"}
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            session.is_active = False
            del self.active_sessions[session_id]
            return {"valid": False, "error": "Session expired"}
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        return {
            "valid": True,
            "user_id": session.user_id,
            "session_type": session.session_type.value,
            "mfa_completed": session.mfa_completed,
            "expires_at": session.expires_at.isoformat()
        }
    
    async def refresh_session(self, session_id: str) -> Dict[str, Any]:
        """Refresh session expiration"""
        
        session = self.active_sessions.get(session_id)
        
        if not session or not session.is_active:
            return {"success": False, "error": "Session not found or inactive"}
        
        # Extend session expiration
        session.expires_at = datetime.utcnow() + timedelta(hours=self.security_config["session_timeout_hours"])
        session.last_activity = datetime.utcnow()
        
        # Generate new JWT token
        jwt_token = self._generate_jwt_token(session.user_id, session.session_id)
        
        return {
            "success": True,
            "access_token": jwt_token,
            "expires_at": session.expires_at.isoformat()
        }
    
    async def get_user_security_overview(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive security overview for a user"""
        
        if user_id not in self.user_credentials:
            return {"error": "User not found"}
        
        credentials = self.user_credentials[user_id]
        mfa_config = self.mfa_configurations.get(user_id)
        
        # Get active sessions
        user_sessions = [
            {
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "device_info": session.device_info,
                "ip_address": session.ip_address,
                "location": session.location,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            for session in self.active_sessions.values()
            if session.user_id == user_id and session.is_active
        ]
        
        # Get recent authentication attempts
        recent_attempts = [
            {
                "timestamp": attempt.timestamp.isoformat(),
                "method": attempt.authentication_method.value,
                "status": attempt.status.value,
                "ip_address": attempt.ip_address,
                "location": attempt.location
            }
            for attempt in self.authentication_attempts[-20:]
            if attempt.user_id == user_id
        ]
        
        # Get security events
        user_security_events = [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "severity": event.severity,
                "description": event.description
            }
            for event in self.security_events[-10:]
            if event.user_id == user_id
        ]
        
        # Get trusted devices
        trusted_devices = self.trusted_devices.get(user_id, [])
        
        return {
            "user_id": user_id,
            "account_security": {
                "email_verified": credentials.email_verified,
                "phone_verified": credentials.phone_verified,
                "mfa_enabled": mfa_config.is_enabled if mfa_config else False,
                "mfa_methods": [mfa_config.primary_method.value] + [m.value for m in mfa_config.backup_methods] if mfa_config and mfa_config.is_enabled else [],
                "oauth_providers": list(credentials.oauth_providers.keys()),
                "password_set": bool(credentials.password_hash),
                "account_active": credentials.is_active
            },
            "active_sessions": user_sessions,
            "trusted_devices": [
                {
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "platform": device.platform,
                    "last_seen": device.last_seen.isoformat(),
                    "first_seen": device.first_seen.isoformat()
                }
                for device in trusted_devices
            ],
            "recent_activity": {
                "authentication_attempts": recent_attempts,
                "security_events": user_security_events
            },
            "security_score": await self._calculate_security_score(user_id)
        }
    
    # Private helper methods
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength based on security policy"""
        
        config = self.security_config
        errors = []
        
        if len(password) < config["password_min_length"]:
            errors.append(f"Password must be at least {config['password_min_length']} characters")
        
        if config["password_require_uppercase"] and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if config["password_require_numbers"] and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if config["password_require_special"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None
        }
    
    async def _check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier is within rate limits"""
        
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.security_config["rate_limit_window_minutes"])
        
        # Clean old attempts
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                attempt_time for attempt_time in self.rate_limits[identifier]
                if attempt_time > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Check limit
        if len(self.rate_limits[identifier]) >= self.security_config["rate_limit_max_attempts"]:
            return False
        
        # Add current attempt
        self.rate_limits[identifier].append(now)
        return True
    
    async def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        
        # Count recent failed attempts
        lockout_threshold = datetime.utcnow() - timedelta(minutes=self.security_config["lockout_duration_minutes"])
        
        failed_attempts = [
            attempt for attempt in self.authentication_attempts
            if (attempt.user_id == user_id and 
                attempt.status == AuthenticationStatus.FAILED and
                attempt.timestamp > lockout_threshold)
        ]
        
        return len(failed_attempts) >= self.security_config["max_login_attempts"]
    
    async def _check_and_apply_account_lockout(self, user_id -> None: str) -> None:
        """Check if account should be locked and apply lockout"""
        
        if await self._is_account_locked(user_id):
            await self._log_security_event(
                user_id=user_id,
                event_type="account_locked",
                severity="high",
                description="Account locked due to excessive failed login attempts",
                metadata={"max_attempts": self.security_config["max_login_attempts"]}
            )
    
    async def _create_session(
        self,
        user_id: str,
        authentication_methods: List[AuthenticationMethod],
        device_info: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        mfa_completed: bool,
        session_type: SessionType
    ) -> AuthenticationSession:
        """Create a new authentication session"""
        
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        
        session = AuthenticationSession(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            authentication_methods=authentication_methods,
            mfa_completed=mfa_completed,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            location=await self._geolocate_ip(ip_address)
        )
        
        self.active_sessions[session_id] = session
        self.metrics["active_sessions"] = len(self.active_sessions)
        
        return session
    
    async def _log_authentication_attempt(
        self,
        attempt_id -> None: str,
        authentication_method -> None: AuthenticationMethod,
        status -> None: AuthenticationStatus,
        ip_address -> None: str,
        user_agent -> None: str,
        user_id -> None: Optional[str] = None,
        email -> None: Optional[str] = None,
        failure_reason -> None: Optional[str] = None
    ) -> None:
        """Log authentication attempt"""
        
        attempt = AuthenticationAttempt(
            attempt_id=attempt_id,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            authentication_method=authentication_method,
            status=status,
            failure_reason=failure_reason,
            location=await self._geolocate_ip(ip_address)
        )
        
        self.authentication_attempts.append(attempt)
        
        # Update metrics
        self.metrics["total_authentication_attempts"] += 1
        if status == AuthenticationStatus.SUCCESS:
            self.metrics["successful_authentications"] += 1
        else:
            self.metrics["failed_authentications"] += 1
    
    async def _log_security_event(
        self,
        event_type -> None: str,
        severity -> None: str,
        description -> None: str,
        metadata -> None: Dict[str, Any],
        user_id -> None: Optional[str] = None,
        ip_address -> None: Optional[str] = None,
        user_agent -> None: Optional[str] = None
    ) -> None:
        """Log security event"""
        
        event = SecurityEvent(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.security_events.append(event)
        self.metrics["security_events"] += 1
        
        # Log critical events immediately
        if severity == "critical":
            self.logger.critical(f"Critical security event: {description}")
        elif severity == "high":
            self.logger.warning(f"High severity security event: {description}")
    
    def _generate_jwt_token(self, user_id: str, session_id: str) -> str:
        """Generate JWT access token"""
        
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.security_config["session_timeout_hours"])
        }
        
        return jwt.encode(
            payload,
            self.security_config["jwt_secret"],
            algorithm=self.security_config["jwt_algorithm"]
        )
    
    async def _verify_mfa_code(self, user_id: str, method: MFAMethod, code: str) -> bool:
        """Verify MFA code"""
        
        mfa_config = self.mfa_configurations.get(user_id)
        if not mfa_config:
            return False
        
        if method == MFAMethod.TOTP or method == MFAMethod.AUTHENTICATOR_APP:
            if mfa_config.totp_secret:
                totp = pyotp.TOTP(mfa_config.totp_secret)
                return totp.verify(code, valid_window=1)
        
        elif method == MFAMethod.BACKUP_CODES:
            if code.upper() in mfa_config.backup_codes:
                # Remove used backup code
                mfa_config.backup_codes.remove(code.upper())
                return True
        
        elif method == MFAMethod.SMS:
            # In real implementation, this would verify SMS OTP
            return len(code) == 6 and code.isdigit()
        
        elif method == MFAMethod.EMAIL:
            # In real implementation, this would verify email OTP
            return len(code) == 6 and code.isdigit()
        
        return False
    
    def _get_available_mfa_methods(self, user_id: str) -> List[str]:
        """Get available MFA methods for user"""
        
        mfa_config = self.mfa_configurations.get(user_id)
        if not mfa_config or not mfa_config.is_enabled:
            return []
        
        methods = []
        
        if mfa_config.primary_method:
            methods.append(mfa_config.primary_method.value)
        
        methods.extend([method.value for method in mfa_config.backup_methods])
        
        # Always include backup codes if available
        if mfa_config.backup_codes:
            methods.append(MFAMethod.BACKUP_CODES.value)
        
        return list(set(methods))
    
    def _mfa_method_to_auth_method(self, mfa_method: MFAMethod) -> AuthenticationMethod:
        """Convert MFA method to authentication method"""
        
        mapping = {
            MFAMethod.TOTP: AuthenticationMethod.EMAIL_PASSWORD,  # TOTP is secondary
            MFAMethod.SMS: AuthenticationMethod.PHONE_OTP,
            MFAMethod.EMAIL: AuthenticationMethod.EMAIL_PASSWORD,
            MFAMethod.AUTHENTICATOR_APP: AuthenticationMethod.EMAIL_PASSWORD,
            MFAMethod.BIOMETRIC: AuthenticationMethod.BIOMETRIC,
            MFAMethod.HARDWARE_TOKEN: AuthenticationMethod.HARDWARE_KEY
        }
        
        return mapping.get(mfa_method, AuthenticationMethod.EMAIL_PASSWORD)
    
    async def _trust_device(self, user_id -> None: str, device_info -> None: Dict[str, Any]) -> None:
        """Add device to trusted devices"""
        
        device = DeviceInfo(
            device_id=device_info.get("device_id", uuid.uuid4().hex),
            device_name=device_info.get("device_name", "Unknown Device"),
            device_type=device_info.get("device_type", "other"),
            platform=device_info.get("platform", "unknown"),
            browser=device_info.get("browser"),
            fingerprint=device_info.get("fingerprint", ""),
            is_trusted=True
        )
        
        if user_id not in self.trusted_devices:
            self.trusted_devices[user_id] = []
        
        # Remove existing device with same ID
        self.trusted_devices[user_id] = [
            d for d in self.trusted_devices[user_id] 
            if d.device_id != device.device_id
        ]
        
        self.trusted_devices[user_id].append(device)
    
    async def _analyze_authentication_patterns(self, user_id -> None: str, device_info -> None: Dict[str, Any], ip_address -> None: str) -> None:
        """Analyze authentication patterns for suspicious activity"""
        
        # Get recent authentication attempts for this user
        recent_attempts = [
            attempt for attempt in self.authentication_attempts[-50:]
            if attempt.user_id == user_id and attempt.status == AuthenticationStatus.SUCCESS
        ]
        
        if len(recent_attempts) < 2:
            return  # Not enough data for analysis
        
        # Check for unusual IP addresses
        recent_ips = [attempt.ip_address for attempt in recent_attempts[-10:]]
        if ip_address not in recent_ips:
            await self._log_security_event(
                user_id=user_id,
                event_type="unusual_ip",
                severity="medium",
                description="Login from new IP address",
                metadata={"ip_address": ip_address, "recent_ips": recent_ips},
                ip_address=ip_address
            )
        
        # Check for unusual device
        device_fingerprint = device_info.get("fingerprint")
        if device_fingerprint:
            trusted_devices = self.trusted_devices.get(user_id, [])
            known_fingerprints = [device.fingerprint for device in trusted_devices]
            
            if device_fingerprint not in known_fingerprints:
                await self._log_security_event(
                    user_id=user_id,
                    event_type="new_device",
                    severity="medium",
                    description="Login from new device",
                    metadata={"device_info": device_info},
                    ip_address=ip_address
                )
    
    async def _geolocate_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get geolocation for IP address"""
        
        # Simplified geolocation - would use actual service in real implementation
        return {
            "country": "Unknown",
            "city": "Unknown",
            "region": "Unknown",
            "coordinates": {"lat": 0.0, "lon": 0.0}
        }
    
    async def _calculate_security_score(self, user_id: str) -> Dict[str, Any]:
        """Calculate security score for user"""
        
        credentials = self.user_credentials.get(user_id)
        mfa_config = self.mfa_configurations.get(user_id)
        
        if not credentials:
            return {"score": 0, "max_score": 100, "factors": []}
        
        score = 0
        max_score = 100
        factors = []
        
        # Email verification (20 points)
        if credentials.email_verified:
            score += 20
            factors.append("Email verified")
        
        # Phone verification (10 points)
        if credentials.phone_verified:
            score += 10
            factors.append("Phone verified")
        
        # Strong password (15 points)
        if credentials.password_hash:
            score += 15
            factors.append("Password set")
        
        # MFA enabled (30 points)
        if mfa_config and mfa_config.is_enabled:
            score += 30
            factors.append("Multi-factor authentication enabled")
        
        # OAuth providers (10 points)
        if credentials.oauth_providers:
            score += 10
            factors.append("OAuth providers connected")
        
        # Recent security activity (15 points)
        recent_activity = len([
            event for event in self.security_events[-20:]
            if event.user_id == user_id and 
            event.timestamp > datetime.utcnow() - timedelta(days=30)
        ])
        
        if recent_activity == 0:
            score += 15
            factors.append("No recent security incidents")
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "factors": factors,
            "level": "High" if score >= 80 else "Medium" if score >= 60 else "Low"
        }
    
    def _initialize_oauth_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize OAuth provider configurations"""
        
        return {
            "google": {
                "client_id": self.config.get("google_client_id", ""),
                "client_secret": self.config.get("google_client_secret", ""),
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile"
            },
            "facebook": {
                "client_id": self.config.get("facebook_client_id", ""),
                "client_secret": self.config.get("facebook_client_secret", ""),
                "auth_url": "https://www.facebook.com/v12.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v12.0/oauth/access_token",
                "user_info_url": "https://graph.facebook.com/me",
                "scope": "email"
            },
            "apple": {
                "client_id": self.config.get("apple_client_id", ""),
                "client_secret": self.config.get("apple_client_secret", ""),
                "auth_url": "https://appleid.apple.com/auth/authorize",
                "token_url": "https://appleid.apple.com/auth/token",
                "user_info_url": None,  # Apple doesn't provide user info endpoint
                "scope": "name email"
            }
        }
    
    async def _exchange_oauth_code(self, provider: str, authorization_code: str) -> Dict[str, Any]:
        """Exchange OAuth authorization code for access token"""
        
        # Simplified OAuth exchange - would use actual HTTP requests in real implementation
        return {
            "success": True,
            "access_token": f"oauth_token_{uuid.uuid4().hex[:16]}",
            "refresh_token": f"refresh_token_{uuid.uuid4().hex[:16]}",
            "expires_in": 3600
        }
    
    async def _get_oauth_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        
        # Simplified user info retrieval - would use actual API calls in real implementation
        return {
            "success": True,
            "user_id": f"{provider}_user_{uuid.uuid4().hex[:8]}",
            "email": f"user@{provider}.com",
            "name": "OAuth User",
            "verified": True
        }


# Export all classes and enums for the implementation module
__all__ = [
    'AuthenticationImplementation',
    'AuthenticationMethod',
    'MFAMethod',
    'SessionType',
    'AuthenticationStatus',
    'UserCredentials',
    'MFAConfiguration',
    'AuthenticationSession',
    'AuthenticationAttempt',
    'SecurityEvent',
    'DeviceInfo'
]