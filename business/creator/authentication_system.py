"""
Creator Authentication System - Advanced Multi-Factor Authentication & Security

Ultra-sophisticated authentication system for content creators with multi-factor authentication,
session management, security controls, and advanced threat protection.

Business Logic Flow:
Login Request → Identity Verification → MFA Challenge → Session Creation → 
Security Monitoring → Activity Tracking → Session Management → Logout

Project: IA Influencer Agent + Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import secrets
import hashlib
import json
import hmac
from ipaddress import ip_address, ip_network

# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import jwt
import pyotp
import qrcode
from PIL import Image
import io
import base64

# Internal imports
from ...core.config import get_settings
from ...core.cache import CacheManager
from ...core.security import SecurityManager
from ...core.logging import get_logger
from .profile_manager import CreatorProfileManager, CreatorProfile

# Configure logging
logger = get_logger(__name__)


class AuthenticationMethod(Enum):
    """Authentication methods supported"""
    PASSWORD = "password"
    TWO_FACTOR = "two_factor"
    BIOMETRIC = "biometric"
    SOCIAL_OAUTH = "social_oauth"
    API_KEY = "api_key"
    MAGIC_LINK = "magic_link"


class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPICIOUS = "suspicious"
    LOCKED = "locked"


class SecurityThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceType(Enum):
    """Device types for tracking"""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    API = "api"
    UNKNOWN = "unknown"


@dataclass
class AuthenticationRequest:
    """Authentication request data"""
    email: str
    password: str
    remember_me: bool = False
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    mfa_token: Optional[str] = None


@dataclass
class SessionInfo:
    """User session information"""
    session_id: str
    creator_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    status: SessionStatus
    
    # Device and location info
    device_type: DeviceType
    device_id: str
    ip_address: str
    user_agent: str
    location: Optional[Dict[str, str]] = None
    
    # Security info
    authentication_method: AuthenticationMethod
    mfa_verified: bool = False
    threat_level: SecurityThreatLevel = SecurityThreatLevel.LOW
    
    # Session metadata
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MFASetup:
    """Multi-factor authentication setup"""
    creator_id: str
    method_type: str  # totp, sms, email
    secret_key: str
    backup_codes: List[str]
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityEvent:
    """Security event tracking"""
    event_id: str
    creator_id: str
    event_type: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    severity: SecurityThreatLevel
    details: Dict[str, Any]
    resolved: bool = False


class MultiFactorAuth:
    """
    Multi-Factor Authentication manager
    
    Handles setup, verification, and management of various MFA methods
    including TOTP, SMS, email, and backup codes.
    """
    
    def __init__(self, cache_manager: CacheManager, security_manager: SecurityManager):
        self.cache = cache_manager
        self.security = security_manager
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        
        # MFA configuration
        self.totp_issuer = "IA Influencer Agent"
        self.backup_codes_count = 10
        self.code_length = 6
        self.code_validity_period = 300  # 5 minutes
    
    async def setup_totp(self, creator_id: str) -> Dict[str, Any]:
        """
        Set up TOTP (Time-based One-Time Password) authentication
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            TOTP setup information including QR code
        """
        try:
            self.logger.info(f"Setting up TOTP for creator {creator_id}")
            
            # Generate secret key
            secret_key = pyotp.random_base32()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret_key)
            
            # Generate provisioning URI
            provisioning_uri = totp.provisioning_uri(
                name=creator_id,
                issuer_name=self.totp_issuer
            )
            
            # Generate QR code
            qr_code_data = await self._generate_qr_code(provisioning_uri)
            
            # Generate backup codes
            backup_codes = [secrets.token_hex(8) for _ in range(self.backup_codes_count)]
            
            # Store MFA setup (temporarily, until verified)
            mfa_setup = MFASetup(
                creator_id=creator_id,
                method_type="totp",
                secret_key=secret_key,
                backup_codes=backup_codes
            )
            
            await self.cache.set(
                f"mfa_setup:{creator_id}",
                json.dumps(asdict(mfa_setup), default=str),
                ttl=1800  # 30 minutes
            )
            
            return {
                'setup_id': f"totp_{creator_id}_{int(datetime.utcnow().timestamp())}",
                'secret_key': secret_key,
                'qr_code': qr_code_data,
                'backup_codes': backup_codes,
                'manual_entry_key': secret_key,
                'issuer': self.totp_issuer,
                'account_name': creator_id,
                'expires_in': 1800
            }
            
        except Exception as e:
            self.logger.error(f"TOTP setup failed for creator {creator_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to setup TOTP authentication"
            )
    
    async def verify_totp_setup(
        self,
        creator_id: str,
        verification_code: str
    ) -> bool:
        """
        Verify TOTP setup with provided code
        
        Args:
            creator_id: Creator identifier
            verification_code: TOTP verification code
            
        Returns:
            True if verification successful
        """
        try:
            # Get MFA setup data
            cached_setup = await self.cache.get(f"mfa_setup:{creator_id}")
            if not cached_setup:
                return False
            
            mfa_setup = MFASetup(**json.loads(cached_setup))
            
            # Verify TOTP code
            totp = pyotp.TOTP(mfa_setup.secret_key)
            if not totp.verify(verification_code):
                return False
            
            # Mark as verified and store permanently
            mfa_setup.is_verified = True
            
            # Store verified MFA setup
            await self.cache.set(
                f"mfa_verified:{creator_id}",
                json.dumps(asdict(mfa_setup), default=str),
                ttl=86400 * 365  # 1 year
            )
            
            # Clean up temporary setup
            await self.cache.delete(f"mfa_setup:{creator_id}")
            
            self.logger.info(f"TOTP verification successful for creator {creator_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"TOTP verification failed for creator {creator_id}: {e}")
            return False
    
    async def verify_totp_login(
        self,
        creator_id: str,
        verification_code: str
    ) -> bool:
        """
        Verify TOTP code during login
        
        Args:
            creator_id: Creator identifier
            verification_code: TOTP verification code
            
        Returns:
            True if verification successful
        """
        try:
            # Get verified MFA setup
            cached_setup = await self.cache.get(f"mfa_verified:{creator_id}")
            if not cached_setup:
                return False
            
            mfa_setup = MFASetup(**json.loads(cached_setup))
            
            # Check if it's a backup code
            if verification_code in mfa_setup.backup_codes:
                # Remove used backup code
                mfa_setup.backup_codes.remove(verification_code)
                
                # Update stored setup
                await self.cache.set(
                    f"mfa_verified:{creator_id}",
                    json.dumps(asdict(mfa_setup), default=str),
                    ttl=86400 * 365
                )
                
                return True
            
            # Verify TOTP code
            totp = pyotp.TOTP(mfa_setup.secret_key)
            return totp.verify(verification_code, valid_window=1)
            
        except Exception as e:
            self.logger.error(f"TOTP login verification failed for creator {creator_id}: {e}")
            return False
    
    async def disable_mfa(self, creator_id: str) -> bool:
        """
        Disable MFA for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            True if successful
        """
        try:
            await self.cache.delete(f"mfa_verified:{creator_id}")
            await self.cache.delete(f"mfa_setup:{creator_id}")
            
            self.logger.info(f"MFA disabled for creator {creator_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disable MFA for creator {creator_id}: {e}")
            return False
    
    async def get_mfa_status(self, creator_id: str) -> Dict[str, Any]:
        """
        Get MFA status for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            MFA status information
        """
        try:
            cached_setup = await self.cache.get(f"mfa_verified:{creator_id}")
            if not cached_setup:
                return {
                    'enabled': False,
                    'methods': [],
                    'backup_codes_remaining': 0
                }
            
            mfa_setup = MFASetup(**json.loads(cached_setup))
            
            return {
                'enabled': True,
                'methods': [mfa_setup.method_type],
                'backup_codes_remaining': len(mfa_setup.backup_codes),
                'setup_date': mfa_setup.created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get MFA status for creator {creator_id}: {e}")
            return {
                'enabled': False,
                'methods': [],
                'backup_codes_remaining': 0,
                'error': str(e)
            }
    
    async def _generate_qr_code(self, data: str) -> str:
        """Generate QR code as base64 image"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            self.logger.error(f"QR code generation failed: {e}")
            return ""


class SessionManager:
    """
    Advanced session management system
    
    Handles session creation, validation, renewal, and cleanup with
    comprehensive security monitoring and device tracking.
    """
    
    def __init__(self, cache_manager: CacheManager, security_manager: SecurityManager):
        self.cache = cache_manager
        self.security = security_manager
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        
        # Session configuration
        self.default_session_duration = 86400  # 24 hours
        self.remember_me_duration = 86400 * 30  # 30 days
        self.max_sessions_per_user = 5
        self.session_renewal_threshold = 3600  # 1 hour
    
    async def create_session(
        self,
        creator_id: str,
        user_id: str,
        auth_method: AuthenticationMethod,
        request_info: Dict[str, Any],
        remember_me: bool = False
    ) -> SessionInfo:
        """
        Create new authenticated session
        
        Args:
            creator_id: Creator identifier
            user_id: User identifier
            auth_method: Authentication method used
            request_info: Request information (IP, user agent, etc.)
            remember_me: Extended session duration flag
            
        Returns:
            Created session information
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Determine session duration
            duration = self.remember_me_duration if remember_me else self.default_session_duration
            expires_at = now + timedelta(seconds=duration)
            
            # Extract device information
            device_info = await self._extract_device_info(request_info)
            
            # Create session
            session = SessionInfo(
                session_id=session_id,
                creator_id=creator_id,
                user_id=user_id,
                created_at=now,
                last_activity=now,
                expires_at=expires_at,
                status=SessionStatus.ACTIVE,
                device_type=device_info['type'],
                device_id=device_info['id'],
                ip_address=request_info.get('ip_address', ''),
                user_agent=request_info.get('user_agent', ''),
                authentication_method=auth_method,
                mfa_verified=request_info.get('mfa_verified', False),
                permissions=request_info.get('permissions', [])
            )
            
            # Check for suspicious activity
            await self._check_session_security(session)
            
            # Store session
            await self._store_session(session)
            
            # Clean up old sessions
            await self._cleanup_old_sessions(creator_id)
            
            # Log session creation
            await self._log_security_event(
                creator_id,
                "session_created",
                SecurityThreatLevel.LOW,
                {
                    'session_id': session_id,
                    'ip_address': session.ip_address,
                    'device_type': device_info['type'].value,
                    'auth_method': auth_method.value
                }
            )
            
            self.logger.info(f"Session created for creator {creator_id}: {session_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Session creation failed for creator {creator_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )
    
    async def validate_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Validate and refresh session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Valid session information or None
        """
        try:
            # Get session from cache
            cached_session = await self.cache.get(f"session:{session_id}")
            if not cached_session:
                return None
            
            session_data = json.loads(cached_session)
            session = SessionInfo(
                session_id=session_data['session_id'],
                creator_id=session_data['creator_id'],
                user_id=session_data['user_id'],
                created_at=datetime.fromisoformat(session_data['created_at']),
                last_activity=datetime.fromisoformat(session_data['last_activity']),
                expires_at=datetime.fromisoformat(session_data['expires_at']),
                status=SessionStatus(session_data['status']),
                device_type=DeviceType(session_data['device_type']),
                device_id=session_data['device_id'],
                ip_address=session_data['ip_address'],
                user_agent=session_data['user_agent'],
                authentication_method=AuthenticationMethod(session_data['authentication_method']),
                mfa_verified=session_data.get('mfa_verified', False),
                threat_level=SecurityThreatLevel(session_data.get('threat_level', SecurityThreatLevel.LOW.value)),
                permissions=session_data.get('permissions', []),
                metadata=session_data.get('metadata', {})
            )
            
            # Check if session is expired
            if session.expires_at < datetime.utcnow():
                await self._revoke_session(session_id)
                return None
            
            # Check if session is active
            if session.status != SessionStatus.ACTIVE:
                return None
            
            # Update last activity if needed
            now = datetime.utcnow()
            if (now - session.last_activity).seconds > self.session_renewal_threshold:
                session.last_activity = now
                await self._store_session(session)
            
            return session
            
        except Exception as e:
            self.logger.error(f"Session validation failed for {session_id}: {e}")
            return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            return await self._revoke_session(session_id)
            
        except Exception as e:
            self.logger.error(f"Session revocation failed for {session_id}: {e}")
            return False
    
    async def revoke_all_sessions(self, creator_id: str, except_session: Optional[str] = None) -> int:
        """
        Revoke all sessions for a creator
        
        Args:
            creator_id: Creator identifier
            except_session: Session to exclude from revocation
            
        Returns:
            Number of sessions revoked
        """
        try:
            # Get all sessions for creator
            session_keys = await self.cache.get(f"user_sessions:{creator_id}")
            if not session_keys:
                return 0
            
            sessions = json.loads(session_keys)
            revoked_count = 0
            
            for session_id in sessions:
                if except_session and session_id == except_session:
                    continue
                
                if await self._revoke_session(session_id):
                    revoked_count += 1
            
            # Update session list
            if except_session:
                await self.cache.set(
                    f"user_sessions:{creator_id}",
                    json.dumps([except_session]),
                    ttl=self.remember_me_duration
                )
            else:
                await self.cache.delete(f"user_sessions:{creator_id}")
            
            self.logger.info(f"Revoked {revoked_count} sessions for creator {creator_id}")
            return revoked_count
            
        except Exception as e:
            self.logger.error(f"Failed to revoke all sessions for creator {creator_id}: {e}")
            return 0
    
    async def get_active_sessions(self, creator_id: str) -> List[Dict[str, Any]]:
        """
        Get all active sessions for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            List of active session information
        """
        try:
            session_keys = await self.cache.get(f"user_sessions:{creator_id}")
            if not session_keys:
                return []
            
            sessions = json.loads(session_keys)
            active_sessions = []
            
            for session_id in sessions:
                session = await self.validate_session(session_id)
                if session:
                    active_sessions.append({
                        'session_id': session.session_id,
                        'created_at': session.created_at.isoformat(),
                        'last_activity': session.last_activity.isoformat(),
                        'expires_at': session.expires_at.isoformat(),
                        'device_type': session.device_type.value,
                        'ip_address': session.ip_address,
                        'location': session.location,
                        'is_current': session_id == session.session_id
                    })
            
            return active_sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get active sessions for creator {creator_id}: {e}")
            return []
    
    # Private helper methods
    
    async def _extract_device_info(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract device information from request"""
        user_agent = request_info.get('user_agent', '').lower()
        
        # Simple device type detection
        if any(keyword in user_agent for keyword in ['mobile', 'android', 'iphone']):
            device_type = DeviceType.MOBILE
        elif any(keyword in user_agent for keyword in ['tablet', 'ipad']):
            device_type = DeviceType.TABLET
        elif 'api' in request_info.get('source', ''):
            device_type = DeviceType.API
        else:
            device_type = DeviceType.DESKTOP
        
        # Generate device ID based on user agent and IP
        device_string = f"{user_agent}:{request_info.get('ip_address', '')}"
        device_id = hashlib.sha256(device_string.encode()).hexdigest()[:16]
        
        return {
            'type': device_type,
            'id': device_id
        }
    
    async def _check_session_security(self, session: SessionInfo) -> None:
        """Check session for security threats"""
        try:
            threat_level = SecurityThreatLevel.LOW
            
            # Check for suspicious IP addresses
            if await self._is_suspicious_ip(session.ip_address):
                threat_level = SecurityThreatLevel.HIGH
                session.status = SessionStatus.SUSPICIOUS
            
            # Check for unusual device/location patterns
            # (Implementation would include geolocation and device fingerprinting)
            
            session.threat_level = threat_level
            
        except Exception as e:
            self.logger.warning(f"Security check failed for session {session.session_id}: {e}")
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            # Implement IP reputation checking
            # For now, just check against some known bad networks
            suspicious_networks = [
                '10.0.0.0/8',  # Private networks (for demo)
                '192.168.0.0/16',
                '172.16.0.0/12'
            ]
            
            ip = ip_address(ip_address)
            return any(ip in ip_network(network, strict=False) for network in suspicious_networks)
            
        except Exception:
            return False
    
    async def _store_session(self, session: SessionInfo) -> None:
        """Store session in cache"""
        try:
            session_data = {
                'session_id': session.session_id,
                'creator_id': session.creator_id,
                'user_id': session.user_id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'status': session.status.value,
                'device_type': session.device_type.value,
                'device_id': session.device_id,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'authentication_method': session.authentication_method.value,
                'mfa_verified': session.mfa_verified,
                'threat_level': session.threat_level.value,
                'permissions': session.permissions,
                'metadata': session.metadata
            }
            
            # Store session
            ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            await self.cache.set(
                f"session:{session.session_id}",
                json.dumps(session_data, default=str),
                ttl=ttl
            )
            
            # Update user's session list
            session_keys = await self.cache.get(f"user_sessions:{session.creator_id}")
            if session_keys:
                sessions = json.loads(session_keys)
            else:
                sessions = []
            
            if session.session_id not in sessions:
                sessions.append(session.session_id)
            
            await self.cache.set(
                f"user_sessions:{session.creator_id}",
                json.dumps(sessions),
                ttl=self.remember_me_duration
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store session {session.session_id}: {e}")
            raise
    
    async def _revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session"""
        try:
            # Get session first
            cached_session = await self.cache.get(f"session:{session_id}")
            if not cached_session:
                return False
            
            session_data = json.loads(cached_session)
            creator_id = session_data['creator_id']
            
            # Remove session
            await self.cache.delete(f"session:{session_id}")
            
            # Remove from user's session list
            session_keys = await self.cache.get(f"user_sessions:{creator_id}")
            if session_keys:
                sessions = json.loads(session_keys)
                if session_id in sessions:
                    sessions.remove(session_id)
                    
                    if sessions:
                        await self.cache.set(
                            f"user_sessions:{creator_id}",
                            json.dumps(sessions),
                            ttl=self.remember_me_duration
                        )
                    else:
                        await self.cache.delete(f"user_sessions:{creator_id}")
            
            # Log security event
            await self._log_security_event(
                creator_id,
                "session_revoked",
                SecurityThreatLevel.LOW,
                {'session_id': session_id}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke session {session_id}: {e}")
            return False
    
    async def _cleanup_old_sessions(self, creator_id: str) -> None:
        """Clean up old sessions for a creator"""
        try:
            session_keys = await self.cache.get(f"user_sessions:{creator_id}")
            if not session_keys:
                return
            
            sessions = json.loads(session_keys)
            
            # If too many sessions, remove oldest ones
            if len(sessions) > self.max_sessions_per_user:
                # This would require storing creation timestamps
                # For now, just remove excess sessions
                excess_count = len(sessions) - self.max_sessions_per_user
                for _ in range(excess_count):
                    old_session_id = sessions.pop(0)
                    await self._revoke_session(old_session_id)
                
                await self.cache.set(
                    f"user_sessions:{creator_id}",
                    json.dumps(sessions),
                    ttl=self.remember_me_duration
                )
                
        except Exception as e:
            self.logger.warning(f"Session cleanup failed for creator {creator_id}: {e}")
    
    async def _log_security_event(
        self,
        creator_id: str,
        event_type: str,
        severity: SecurityThreatLevel,
        details: Dict[str, Any]
    ) -> None:
        """Log security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                creator_id=creator_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                ip_address=details.get('ip_address', ''),
                user_agent=details.get('user_agent', ''),
                severity=severity,
                details=details
            )
            
            # Store security event
            await self.cache.set(
                f"security_event:{event.event_id}",
                json.dumps(asdict(event), default=str),
                ttl=86400 * 30  # 30 days
            )
            
            # Add to creator's security log
            security_log_key = f"security_log:{creator_id}"
            security_log = await self.cache.get(security_log_key)
            
            if security_log:
                events = json.loads(security_log)
            else:
                events = []
            
            events.insert(0, event.event_id)  # Most recent first
            
            # Keep only last 100 events
            events = events[:100]
            
            await self.cache.set(
                security_log_key,
                json.dumps(events),
                ttl=86400 * 30
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")


class SecurityController:
    """
    Advanced security controller for threat detection and response
    
    Monitors authentication patterns, detects anomalies, and implements
    automated security responses to protect creator accounts.
    """
    
    def __init__(self, cache_manager: CacheManager, security_manager: SecurityManager):
        self.cache = cache_manager
        self.security = security_manager
        self.logger = get_logger(self.__class__.__name__)
        
        # Security thresholds
        self.failed_login_threshold = 5
        self.lockout_duration = 3600  # 1 hour
        self.unusual_activity_threshold = 10
        self.rate_limit_requests = 100
        self.rate_limit_window = 3600  # 1 hour
    
    async def check_authentication_security(
        self,
        creator_id: str,
        request_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check authentication attempt for security issues
        
        Args:
            creator_id: Creator identifier
            request_info: Request information
            
        Returns:
            Security check results
        """
        try:
            security_issues = []
            threat_level = SecurityThreatLevel.LOW
            
            # Check for account lockout
            if await self._is_account_locked(creator_id):
                return {
                    'allowed': False,
                    'reason': 'Account temporarily locked due to suspicious activity',
                    'threat_level': SecurityThreatLevel.HIGH.value,
                    'retry_after': self.lockout_duration
                }
            
            # Check failed login attempts
            failed_attempts = await self._get_failed_attempts(creator_id)
            if failed_attempts >= self.failed_login_threshold:
                await self._lock_account(creator_id)
                security_issues.append('Too many failed login attempts')
                threat_level = SecurityThreatLevel.HIGH
            
            # Check for unusual IP address
            if await self._is_unusual_ip(creator_id, request_info.get('ip_address')):
                security_issues.append('Login from unusual location')
                threat_level = max(threat_level, SecurityThreatLevel.MEDIUM)
            
            # Check rate limiting
            if await self._is_rate_limited(creator_id, request_info.get('ip_address')):
                security_issues.append('Rate limit exceeded')
                threat_level = max(threat_level, SecurityThreatLevel.MEDIUM)
            
            return {
                'allowed': threat_level != SecurityThreatLevel.HIGH,
                'security_issues': security_issues,
                'threat_level': threat_level.value,
                'requires_additional_verification': threat_level == SecurityThreatLevel.MEDIUM
            }
            
        except Exception as e:
            self.logger.error(f"Security check failed for creator {creator_id}: {e}")
            return {
                'allowed': True,  # Fail open for availability
                'security_issues': [f'Security check error: {str(e)}'],
                'threat_level': SecurityThreatLevel.UNKNOWN.value
            }
    
    async def record_failed_login(self, creator_id: str, request_info: Dict[str, Any]) -> None:
        """Record failed login attempt"""
        try:
            # Increment failed attempts counter
            failed_key = f"failed_logins:{creator_id}"
            failed_count = await self.cache.get(failed_key)
            
            if failed_count:
                new_count = int(failed_count) + 1
            else:
                new_count = 1
            
            await self.cache.set(failed_key, str(new_count), ttl=3600)
            
            # Log security event
            await self._log_security_event(
                creator_id,
                "failed_login",
                SecurityThreatLevel.MEDIUM,
                {
                    'attempt_count': new_count,
                    'ip_address': request_info.get('ip_address', ''),
                    'user_agent': request_info.get('user_agent', '')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record failed login for creator {creator_id}: {e}")
    
    async def record_successful_login(self, creator_id: str, request_info: Dict[str, Any]) -> None:
        """Record successful login attempt"""
        try:
            # Clear failed attempts
            await self.cache.delete(f"failed_logins:{creator_id}")
            
            # Record IP address for future anomaly detection
            await self._record_ip_address(creator_id, request_info.get('ip_address'))
            
            # Log security event
            await self._log_security_event(
                creator_id,
                "successful_login",
                SecurityThreatLevel.LOW,
                {
                    'ip_address': request_info.get('ip_address', ''),
                    'user_agent': request_info.get('user_agent', '')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record successful login for creator {creator_id}: {e}")
    
    # Private helper methods
    
    async def _is_account_locked(self, creator_id: str) -> bool:
        """Check if account is locked"""
        try:
            locked_until = await self.cache.get(f"account_locked:{creator_id}")
            if not locked_until:
                return False
            
            unlock_time = datetime.fromisoformat(locked_until)
            return datetime.utcnow() < unlock_time
            
        except Exception as e:
            self.logger.error(f"Failed to check account lock status: {e}")
            return False
    
    async def _lock_account(self, creator_id: str) -> None:
        """Lock account temporarily"""
        try:
            unlock_time = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
            await self.cache.set(
                f"account_locked:{creator_id}",
                unlock_time.isoformat(),
                ttl=self.lockout_duration
            )
            
            self.logger.warning(f"Account locked for creator {creator_id} until {unlock_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to lock account for creator {creator_id}: {e}")
    
    async def _get_failed_attempts(self, creator_id: str) -> int:
        """Get number of failed attempts"""
        try:
            failed_count = await self.cache.get(f"failed_logins:{creator_id}")
            return int(failed_count) if failed_count else 0
        except Exception:
            return 0
    
    async def _is_unusual_ip(self, creator_id: str, ip_address: str) -> bool:
        """Check if IP address is unusual for this creator"""
        try:
            known_ips_key = f"known_ips:{creator_id}"
            known_ips = await self.cache.get(known_ips_key)
            
            if not known_ips:
                return False  # First login, not unusual
            
            ips = json.loads(known_ips)
            return ip_address not in ips
            
        except Exception as e:
            self.logger.error(f"Failed to check unusual IP: {e}")
            return False
    
    async def _record_ip_address(self, creator_id: str, ip_address: str) -> None:
        """Record IP address for creator"""
        try:
            known_ips_key = f"known_ips:{creator_id}"
            known_ips = await self.cache.get(known_ips_key)
            
            if known_ips:
                ips = json.loads(known_ips)
            else:
                ips = []
            
            if ip_address not in ips:
                ips.append(ip_address)
                # Keep only last 10 IPs
                ips = ips[-10:]
                
                await self.cache.set(
                    known_ips_key,
                    json.dumps(ips),
                    ttl=86400 * 30  # 30 days
                )
                
        except Exception as e:
            self.logger.error(f"Failed to record IP address: {e}")
    
    async def _is_rate_limited(self, creator_id: str, ip_address: str) -> bool:
        """Check if requests are rate limited"""
        try:
            rate_key = f"rate_limit:{ip_address}:{creator_id}"
            request_count = await self.cache.get(rate_key)
            
            if not request_count:
                await self.cache.set(rate_key, "1", ttl=self.rate_limit_window)
                return False
            
            count = int(request_count)
            if count >= self.rate_limit_requests:
                return True
            
            await self.cache.set(rate_key, str(count + 1), ttl=self.rate_limit_window)
            return False
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return False
    
    async def _log_security_event(
        self,
        creator_id: str,
        event_type: str,
        severity: SecurityThreatLevel,
        details: Dict[str, Any]
    ) -> None:
        """Log security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                creator_id=creator_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                ip_address=details.get('ip_address', ''),
                user_agent=details.get('user_agent', ''),
                severity=severity,
                details=details
            )
            
            # Store security event
            await self.cache.set(
                f"security_event:{event.event_id}",
                json.dumps(asdict(event), default=str),
                ttl=86400 * 30  # 30 days
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")


class CreatorAuthenticationSystem:
    """
    Main creator authentication system
    
    Orchestrates all authentication operations including login, MFA,
    session management, and security controls for content creators.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        cache_manager: CacheManager,
        security_manager: SecurityManager
    ):
        self.db = db_session
        self.cache = cache_manager
        self.security = security_manager
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        
        # Initialize subsystems
        self.mfa = MultiFactorAuth(cache_manager, security_manager)
        self.session_manager = SessionManager(cache_manager, security_manager)
        self.security_controller = SecurityController(cache_manager, security_manager)
        
        # JWT configuration
        self.jwt_secret = self.settings.SECRET_KEY
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    async def authenticate_creator(
        self,
        auth_request: AuthenticationRequest
    ) -> Dict[str, Any]:
        """
        Authenticate creator with comprehensive security checks
        
        Args:
            auth_request: Authentication request data
            
        Returns:
            Authentication result with tokens and session info
        """
        try:
            self.logger.info(f"Authentication attempt for {auth_request.email}")
            
            # Extract request information
            request_info = {
                'ip_address': auth_request.ip_address,
                'user_agent': auth_request.user_agent,
                'device_info': auth_request.device_info
            }
            
            # Security check (placeholder - would use actual creator_id)
            creator_id = "placeholder"  # This would be resolved from email
            security_check = await self.security_controller.check_authentication_security(
                creator_id, request_info
            )
            
            if not security_check['allowed']:
                await self.security_controller.record_failed_login(creator_id, request_info)
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=security_check['reason']
                )
            
            # Verify credentials (placeholder implementation)
            creator_profile = await self._verify_credentials(
                auth_request.email,
                auth_request.password
            )
            
            if not creator_profile:
                await self.security_controller.record_failed_login(creator_id, request_info)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check MFA if enabled
            mfa_status = await self.mfa.get_mfa_status(creator_profile['creator_id'])
            if mfa_status['enabled'] and not auth_request.mfa_token:
                return {
                    'status': 'mfa_required',
                    'message': 'Multi-factor authentication required',
                    'mfa_methods': mfa_status['methods'],
                    'partial_token': await self._generate_partial_token(creator_profile['creator_id'])
                }
            
            if mfa_status['enabled'] and auth_request.mfa_token:
                if not await self.mfa.verify_totp_login(creator_profile['creator_id'], auth_request.mfa_token):
                    await self.security_controller.record_failed_login(creator_profile['creator_id'], request_info)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid MFA token"
                    )
                request_info['mfa_verified'] = True
            
            # Create session
            session = await self.session_manager.create_session(
                creator_id=creator_profile['creator_id'],
                user_id=creator_profile['user_id'],
                auth_method=AuthenticationMethod.TWO_FACTOR if mfa_status['enabled'] else AuthenticationMethod.PASSWORD,
                request_info=request_info,
                remember_me=auth_request.remember_me
            )
            
            # Generate JWT tokens
            access_token = await self._generate_access_token(creator_profile, session)
            refresh_token = await self._generate_refresh_token(session.session_id)
            
            # Record successful login
            await self.security_controller.record_successful_login(
                creator_profile['creator_id'],
                request_info
            )
            
            return {
                'status': 'success',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': self.access_token_expire_minutes * 60,
                'session_id': session.session_id,
                'creator_profile': {
                    'creator_id': creator_profile['creator_id'],
                    'email': creator_profile['email'],
                    'display_name': creator_profile['display_name'],
                    'verification_level': creator_profile['verification_level']
                },
                'security_info': {
                    'mfa_enabled': mfa_status['enabled'],
                    'session_expires_at': session.expires_at.isoformat(),
                    'threat_level': session.threat_level.value
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed for {auth_request.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
        """
        try:
            # Validate refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            session_id = payload.get('session_id')
            
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Validate session
            session = await self.session_manager.validate_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired or invalid"
                )
            
            # Get creator profile (placeholder)
            creator_profile = await self._get_creator_profile(session.creator_id)
            if not creator_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Creator not found"
                )
            
            # Generate new access token
            access_token = await self._generate_access_token(creator_profile, session)
            
            return {
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': self.access_token_expire_minutes * 60
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )
    
    async def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Logout and revoke session
        
        Args:
            session_id: Session to logout
            
        Returns:
            Logout result
        """
        try:
            success = await self.session_manager.revoke_session(session_id)
            
            return {
                'status': 'success' if success else 'error',
                'message': 'Logged out successfully' if success else 'Session not found'
            }
            
        except Exception as e:
            self.logger.error(f"Logout failed for session {session_id}: {e}")
            return {
                'status': 'error',
                'message': 'Logout failed'
            }
    
    # Private helper methods
    
    async def _verify_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify creator credentials"""
        try:
            # This would be a database query in production
            # For now, return placeholder data
            return {
                'creator_id': str(uuid.uuid4()),
                'user_id': str(uuid.uuid4()),
                'email': email,
                'display_name': 'Test Creator',
                'verification_level': 'email_verified'
            }
            
        except Exception as e:
            self.logger.error(f"Credential verification failed: {e}")
            return None
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator profile by ID"""
        try:
            # This would be a database query in production
            return {
                'creator_id': creator_id,
                'user_id': str(uuid.uuid4()),
                'email': 'test@example.com',
                'display_name': 'Test Creator',
                'verification_level': 'email_verified'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get creator profile: {e}")
            return None
    
    async def _generate_access_token(
        self,
        creator_profile: Dict[str, Any],
        session: SessionInfo
    ) -> str:
        """Generate JWT access token"""
        try:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            payload = {
                'sub': creator_profile['creator_id'],
                'user_id': creator_profile['user_id'],
                'email': creator_profile['email'],
                'session_id': session.session_id,
                'permissions': session.permissions,
                'exp': expire,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
        except Exception as e:
            self.logger.error(f"Access token generation failed: {e}")
            raise
    
    async def _generate_refresh_token(self, session_id: str) -> str:
        """Generate JWT refresh token"""
        try:
            expire = datetime.utcnow() + timedelta(days=30)
            
            payload = {
                'session_id': session_id,
                'exp': expire,
                'iat': datetime.utcnow(),
                'type': 'refresh'
            }
            
            return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
        except Exception as e:
            self.logger.error(f"Refresh token generation failed: {e}")
            raise
    
    async def _generate_partial_token(self, creator_id: str) -> str:
        """Generate partial token for MFA flow"""
        try:
            expire = datetime.utcnow() + timedelta(minutes=10)
            
            payload = {
                'creator_id': creator_id,
                'exp': expire,
                'type': 'partial'
            }
            
            return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
        except Exception as e:
            self.logger.error(f"Partial token generation failed: {e}")
            raise


# Export main classes
__all__ = [
    'CreatorAuthenticationSystem',
    'MultiFactorAuth',
    'SessionManager',
    'SecurityController',
    'AuthenticationRequest',
    'SessionInfo',
    'AuthenticationMethod',
    'SessionStatus',
    'SecurityThreatLevel'
]
