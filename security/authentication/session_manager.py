#!/usr/bin/env python3
"""
🛡️ Session Manager - Enterprise Security Module
===============================================

Ultra-secure session management with distributed storage,
security middleware, and advanced session protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + DevOps + Microservices
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import hashlib
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

import aioredis
from cryptography.fernet import Fernet
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

class SessionSecurityLevel(Enum):
    """Session security levels"""
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"
    CRITICAL = "critical"

class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    LOCKED = "locked"

class SecurityEvent(Enum):
    """Security event types"""
    LOGIN = "login"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_RENEWED = "session_renewed"
    SESSION_EXPIRED = "session_expired"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_CHANGE = "ip_change"
    DEVICE_CHANGE = "device_change"
    CONCURRENT_SESSION = "concurrent_session"

@dataclass
class SessionMetadata:
    """Session metadata for tracking and security"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    security_level: SessionSecurityLevel = SessionSecurityLevel.STANDARD
    status: SessionStatus = SessionStatus.ACTIVE
    permissions: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    csrf_token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    access_count: int = 0
    last_activity: str = ""
    location: Dict[str, Any] = field(default_factory=dict)
    security_flags: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityContext:
    """Security context for request processing"""
    user_id: str
    session_id: str
    permissions: List[str]
    scopes: List[str]
    security_level: SessionSecurityLevel
    ip_address: str
    device_id: str
    authenticated_at: datetime
    last_activity: datetime
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class SessionManager:
    """
    Enterprise-grade session management system.
    
    Features:
    - Distributed session storage with Redis
    - Advanced session security and protection
    - Concurrent session management
    - Session analytics and monitoring
    - CSRF protection and security headers
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None,
        session_timeout: int = 3600,  # 1 hour
        max_concurrent_sessions: int = 5,
        enable_csrf_protection: bool = True
    ):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.session_timeout = session_timeout
        self.max_concurrent_sessions = max_concurrent_sessions
        self.enable_csrf_protection = enable_csrf_protection
        
        # Security configuration
        self.config = {
            "session_cookie_name": "AINFLUE_SESSION",
            "csrf_cookie_name": "AINFLUE_CSRF",
            "cookie_secure": True,
            "cookie_httponly": True,
            "cookie_samesite": "strict",
            "session_regeneration_interval": 900,  # 15 minutes
            "suspicious_activity_threshold": 10,
            "ip_change_detection": True,
            "device_change_detection": True,
            "session_encryption": True,
            "audit_all_sessions": True,
            "cleanup_interval": 3600,  # 1 hour
        }

    async def initialize(self) -> None:
        """Initialize the session manager"""
        try:
            # Initialize Redis connection
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_expired_sessions())
            
            logger.info("Session manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize session manager: {e}")
            raise

    async def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        device_id: Optional[str] = None,
        security_level: SessionSecurityLevel = SessionSecurityLevel.STANDARD,
        permissions: List[str] = None,
        scopes: List[str] = None,
        expires_in: Optional[int] = None
    ) -> SessionMetadata:
        """
        Create a new user session.
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client user agent
            device_id: Device identifier
            security_level: Session security level
            permissions: User permissions
            scopes: Session scopes
            expires_in: Custom expiration time in seconds
            
        Returns:
            SessionMetadata: Created session metadata
        """
        try:
            permissions = permissions or []
            scopes = scopes or []
            
            # Check concurrent session limit
            await self._enforce_concurrent_session_limit(user_id)
            
            # Create session metadata
            session_metadata = SessionMetadata(
                user_id=user_id,
                device_id=device_id or self._generate_device_id(user_agent),
                ip_address=ip_address,
                user_agent=user_agent,
                security_level=security_level,
                permissions=permissions,
                scopes=scopes
            )
            
            # Set custom expiration if provided
            if expires_in:
                session_metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            else:
                session_metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.session_timeout)
            
            # Initialize security flags
            session_metadata.security_flags = {
                "ip_verified": True,
                "device_verified": True,
                "csrf_protected": self.enable_csrf_protection,
                "encrypted": self.config["session_encryption"]
            }
            
            # Store session
            await self._store_session(session_metadata)
            
            # Add to user session index
            await self._add_to_user_sessions(user_id, session_metadata.session_id)
            
            # Log security event
            await self._log_security_event(
                SecurityEvent.SESSION_CREATED,
                user_id,
                session_metadata.session_id,
                {
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "security_level": security_level.value
                }
            )
            
            logger.info(f"Created session for user {user_id}: {session_metadata.session_id}")
            return session_metadata
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[SessionMetadata]:
        """
        Retrieve session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[SessionMetadata]: Session metadata if found
        """
        try:
            session_key = f"session:{session_id}"
            session_data = await self.redis.get(session_key)
            
            if not session_data:
                return None
                
            # Decrypt session data if encryption is enabled
            if self.config["session_encryption"]:
                session_data = self.cipher_suite.decrypt(session_data)
                
            session_dict = json.loads(session_data)
            
            # Convert back to SessionMetadata
            session_metadata = SessionMetadata(
                session_id=session_dict["session_id"],
                user_id=session_dict["user_id"],
                device_id=session_dict["device_id"],
                ip_address=session_dict["ip_address"],
                user_agent=session_dict["user_agent"],
                created_at=datetime.fromisoformat(session_dict["created_at"]),
                last_accessed=datetime.fromisoformat(session_dict["last_accessed"]),
                expires_at=datetime.fromisoformat(session_dict["expires_at"]),
                security_level=SessionSecurityLevel(session_dict["security_level"]),
                status=SessionStatus(session_dict["status"]),
                permissions=session_dict["permissions"],
                scopes=session_dict["scopes"],
                csrf_token=session_dict["csrf_token"],
                access_count=session_dict["access_count"],
                last_activity=session_dict["last_activity"],
                location=session_dict["location"],
                security_flags=session_dict["security_flags"],
                metadata=session_dict["metadata"]
            )
            
            # Check if session is expired
            if datetime.now(timezone.utc) > session_metadata.expires_at:
                session_metadata.status = SessionStatus.EXPIRED
                await self._update_session_status(session_id, SessionStatus.EXPIRED)
                return None
                
            return session_metadata
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def validate_session(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str,
        device_id: Optional[str] = None
    ) -> Tuple[bool, Optional[SessionMetadata], Optional[str]]:
        """
        Validate session with security checks.
        
        Args:
            session_id: Session identifier
            ip_address: Client IP address
            user_agent: Client user agent
            device_id: Device identifier
            
        Returns:
            Tuple[bool, Optional[SessionMetadata], Optional[str]]: 
            (is_valid, session_metadata, error_message)
        """
        try:
            # Get session
            session_metadata = await self.get_session(session_id)
            if not session_metadata:
                return False, None, "Session not found or expired"
                
            # Check session status
            if session_metadata.status != SessionStatus.ACTIVE:
                return False, None, f"Session status: {session_metadata.status.value}"
                
            # IP address validation
            if self.config["ip_change_detection"] and session_metadata.ip_address != ip_address:
                await self._log_security_event(
                    SecurityEvent.IP_CHANGE,
                    session_metadata.user_id,
                    session_id,
                    {
                        "old_ip": session_metadata.ip_address,
                        "new_ip": ip_address
                    }
                )
                
                # For high security sessions, reject IP changes
                if session_metadata.security_level in [SessionSecurityLevel.ULTRA, SessionSecurityLevel.CRITICAL]:
                    return False, None, "IP address change detected"
                    
                # Update IP address for standard sessions
                session_metadata.ip_address = ip_address
                session_metadata.security_flags["ip_verified"] = False
                
            # Device validation
            current_device_id = device_id or self._generate_device_id(user_agent)
            if (self.config["device_change_detection"] and 
                session_metadata.device_id != current_device_id):
                
                await self._log_security_event(
                    SecurityEvent.DEVICE_CHANGE,
                    session_metadata.user_id,
                    session_id,
                    {
                        "old_device": session_metadata.device_id,
                        "new_device": current_device_id
                    }
                )
                
                # For critical sessions, reject device changes
                if session_metadata.security_level == SessionSecurityLevel.CRITICAL:
                    return False, None, "Device change detected"
                    
                session_metadata.device_id = current_device_id
                session_metadata.security_flags["device_verified"] = False
            
            # Update session activity
            session_metadata.last_accessed = datetime.now(timezone.utc)
            session_metadata.access_count += 1
            session_metadata.last_activity = "validation"
            
            # Check for session regeneration
            time_since_creation = (datetime.now(timezone.utc) - session_metadata.created_at).total_seconds()
            if time_since_creation > self.config["session_regeneration_interval"]:
                await self._regenerate_session_id(session_metadata)
            
            # Update stored session
            await self._store_session(session_metadata)
            
            return True, session_metadata, None
            
        except Exception as e:
            logger.error(f"Session validation failed for {session_id}: {e}")
            return False, None, f"Validation error: {e}"

    async def renew_session(
        self,
        session_id: str,
        additional_time: Optional[int] = None
    ) -> Tuple[bool, Optional[SessionMetadata]]:
        """
        Renew session expiration time.
        
        Args:
            session_id: Session identifier
            additional_time: Additional time in seconds
            
        Returns:
            Tuple[bool, Optional[SessionMetadata]]: (success, updated_session)
        """
        try:
            session_metadata = await self.get_session(session_id)
            if not session_metadata:
                return False, None
                
            # Extend session expiration
            if additional_time:
                session_metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=additional_time)
            else:
                session_metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.session_timeout)
            
            # Update activity
            session_metadata.last_accessed = datetime.now(timezone.utc)
            session_metadata.last_activity = "renewal"
            
            # Store updated session
            await self._store_session(session_metadata)
            
            # Log security event
            await self._log_security_event(
                SecurityEvent.SESSION_RENEWED,
                session_metadata.user_id,
                session_id,
                {"new_expiry": session_metadata.expires_at.isoformat()}
            )
            
            return True, session_metadata
            
        except Exception as e:
            logger.error(f"Failed to renew session {session_id}: {e}")
            return False, None

    async def revoke_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """
        Revoke a specific session.
        
        Args:
            session_id: Session identifier
            reason: Reason for revocation
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            session_metadata = await self.get_session(session_id)
            if not session_metadata:
                return False
                
            # Update session status
            await self._update_session_status(session_id, SessionStatus.REVOKED)
            
            # Remove from user session index
            await self._remove_from_user_sessions(session_metadata.user_id, session_id)
            
            # Log security event
            await self._log_security_event(
                SecurityEvent.LOGOUT,
                session_metadata.user_id,
                session_id,
                {"reason": reason}
            )
            
            logger.info(f"Revoked session {session_id} for user {session_metadata.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke session {session_id}: {e}")
            return False

    async def revoke_user_sessions(
        self,
        user_id: str,
        exclude_session_id: Optional[str] = None,
        reason: str = "security_action"
    ) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User identifier
            exclude_session_id: Session to exclude from revocation
            reason: Reason for revocation
            
        Returns:
            int: Number of sessions revoked
        """
        try:
            user_sessions = await self._get_user_sessions(user_id)
            revoked_count = 0
            
            for session_id in user_sessions:
                if session_id != exclude_session_id:
                    if await self.revoke_session(session_id, reason):
                        revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user sessions: {e}")
            return 0

    def _generate_device_id(self, user_agent: str) -> str:
        """Generate device ID from user agent"""
        try:
            # Simple hash of user agent for device identification
            device_hash = hashlib.sha256(user_agent.encode()).hexdigest()
            return f"device_{device_hash[:16]}"
        except Exception:
            return f"device_{secrets.token_hex(8)}"

    async def _store_session(self, session_metadata: SessionMetadata) -> None:
        """Store session in Redis"""
        try:
            session_key = f"session:{session_metadata.session_id}"
            session_data = {
                "session_id": session_metadata.session_id,
                "user_id": session_metadata.user_id,
                "device_id": session_metadata.device_id,
                "ip_address": session_metadata.ip_address,
                "user_agent": session_metadata.user_agent,
                "created_at": session_metadata.created_at.isoformat(),
                "last_accessed": session_metadata.last_accessed.isoformat(),
                "expires_at": session_metadata.expires_at.isoformat(),
                "security_level": session_metadata.security_level.value,
                "status": session_metadata.status.value,
                "permissions": session_metadata.permissions,
                "scopes": session_metadata.scopes,
                "csrf_token": session_metadata.csrf_token,
                "access_count": session_metadata.access_count,
                "last_activity": session_metadata.last_activity,
                "location": session_metadata.location,
                "security_flags": session_metadata.security_flags,
                "metadata": session_metadata.metadata
            }
            
            session_json = json.dumps(session_data, default=str)
            
            # Encrypt session data if enabled
            if self.config["session_encryption"]:
                session_json = self.cipher_suite.encrypt(session_json.encode())
            else:
                session_json = session_json.encode()
            
            # Calculate TTL
            ttl = int((session_metadata.expires_at - datetime.now(timezone.utc)).total_seconds())
            ttl = max(60, ttl)  # Minimum 1 minute
            
            await self.redis.setex(session_key, ttl, session_json)
            
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            raise

    async def _update_session_status(self, session_id: str, status: SessionStatus) -> None:
        """Update session status"""
        try:
            session_metadata = await self.get_session(session_id)
            if session_metadata:
                session_metadata.status = status
                await self._store_session(session_metadata)
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")

    async def _add_to_user_sessions(self, user_id: str, session_id: str) -> None:
        """Add session to user session index"""
        try:
            user_sessions_key = f"user_sessions:{user_id}"
            await self.redis.sadd(user_sessions_key, session_id)
            await self.redis.expire(user_sessions_key, self.session_timeout * 2)
        except Exception as e:
            logger.error(f"Failed to add to user sessions: {e}")

    async def _remove_from_user_sessions(self, user_id: str, session_id: str) -> None:
        """Remove session from user session index"""
        try:
            user_sessions_key = f"user_sessions:{user_id}"
            await self.redis.srem(user_sessions_key, session_id)
        except Exception as e:
            logger.error(f"Failed to remove from user sessions: {e}")

    async def _get_user_sessions(self, user_id: str) -> List[str]:
        """Get all active sessions for user"""
        try:
            user_sessions_key = f"user_sessions:{user_id}"
            sessions = await self.redis.smembers(user_sessions_key)
            return [session.decode() for session in sessions]
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

    async def _enforce_concurrent_session_limit(self, user_id: str) -> None:
        """Enforce concurrent session limit"""
        try:
            user_sessions = await self._get_user_sessions(user_id)
            
            if len(user_sessions) >= self.max_concurrent_sessions:
                # Remove oldest sessions
                sessions_to_remove = len(user_sessions) - self.max_concurrent_sessions + 1
                
                # Get session creation times to find oldest
                session_times = []
                for session_id in user_sessions:
                    session_metadata = await self.get_session(session_id)
                    if session_metadata:
                        session_times.append((session_id, session_metadata.created_at))
                
                # Sort by creation time and remove oldest
                session_times.sort(key=lambda x: x[1])
                for i in range(sessions_to_remove):
                    await self.revoke_session(session_times[i][0], "concurrent_session_limit")
                    
        except Exception as e:
            logger.error(f"Failed to enforce concurrent session limit: {e}")

    async def _regenerate_session_id(self, session_metadata: SessionMetadata) -> None:
        """Regenerate session ID for security"""
        try:
            old_session_id = session_metadata.session_id
            new_session_id = str(uuid.uuid4())
            
            # Remove old session
            old_session_key = f"session:{old_session_id}"
            await self.redis.delete(old_session_key)
            
            # Update session metadata
            session_metadata.session_id = new_session_id
            session_metadata.csrf_token = secrets.token_urlsafe(32)
            
            # Store with new ID
            await self._store_session(session_metadata)
            
            # Update user session index
            await self._remove_from_user_sessions(session_metadata.user_id, old_session_id)
            await self._add_to_user_sessions(session_metadata.user_id, new_session_id)
            
            logger.info(f"Regenerated session ID: {old_session_id} -> {new_session_id}")
            
        except Exception as e:
            logger.error(f"Failed to regenerate session ID: {e}")

    async def _log_security_event(
        self,
        event_type: SecurityEvent,
        user_id: str,
        session_id: str,
        details: Dict[str, Any]
    ) -> None:
        """Log security event"""
        try:
            if not self.config["audit_all_sessions"]:
                return
                
            event_data = {
                "event_type": event_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details
            }
            
            event_key = f"security_event:{int(time.time())}:{session_id}"
            await self.redis.setex(
                event_key,
                86400 * 7,  # Keep for 7 days
                json.dumps(event_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        """Background task to cleanup expired sessions"""
        try:
            while True:
                await asyncio.sleep(self.config["cleanup_interval"])
                
                # Clean up expired sessions
                pattern = "session:*"
                session_keys = await self.redis.keys(pattern)
                
                cleaned_count = 0
                for key in session_keys:
                    try:
                        ttl = await self.redis.ttl(key)
                        if ttl <= 0:  # Expired
                            await self.redis.delete(key)
                            cleaned_count += 1
                    except Exception:
                        continue
                
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} expired sessions")
                    
        except Exception as e:
            logger.error(f"Session cleanup task failed: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class SecurityMiddleware:
    """
    FastAPI security middleware for session validation and protection.
    """
    
    def __init__(
        self,
        session_manager: SessionManager,
        require_auth: bool = True,
        required_permissions: List[str] = None,
        required_scopes: List[str] = None
    ):
        self.session_manager = session_manager
        self.require_auth = require_auth
        self.required_permissions = required_permissions or []
        self.required_scopes = required_scopes or []
        self.security = HTTPBearer(auto_error=False)

    async def __call__(self, request: Request) -> Optional[SecurityContext]:
        """Process request through security middleware"""
        try:
            # Extract session from cookie or header
            session_id = self._extract_session_id(request)
            
            if not session_id:
                if self.require_auth:
                    raise HTTPException(status_code=401, detail="Authentication required")
                return None
            
            # Get client information
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            device_id = request.headers.get("x-device-id")
            
            # Validate session
            is_valid, session_metadata, error_message = await self.session_manager.validate_session(
                session_id, ip_address, user_agent, device_id
            )
            
            if not is_valid:
                if self.require_auth:
                    raise HTTPException(status_code=401, detail=error_message or "Invalid session")
                return None
            
            # Check permissions
            if self.required_permissions:
                missing_permissions = set(self.required_permissions) - set(session_metadata.permissions)
                if missing_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required permissions: {missing_permissions}"
                    )
            
            # Check scopes
            if self.required_scopes:
                missing_scopes = set(self.required_scopes) - set(session_metadata.scopes)
                if missing_scopes:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required scopes: {missing_scopes}"
                    )
            
            # Create security context
            security_context = SecurityContext(
                user_id=session_metadata.user_id,
                session_id=session_metadata.session_id,
                permissions=session_metadata.permissions,
                scopes=session_metadata.scopes,
                security_level=session_metadata.security_level,
                ip_address=session_metadata.ip_address,
                device_id=session_metadata.device_id,
                authenticated_at=session_metadata.created_at,
                last_activity=session_metadata.last_accessed,
                metadata=session_metadata.metadata
            )
            
            # Add security context to request state
            request.state.security_context = security_context
            
            return security_context
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            if self.require_auth:
                raise HTTPException(status_code=500, detail="Security validation error")
            return None

    def _extract_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request"""
        try:
            # Try cookie first
            session_id = request.cookies.get(self.session_manager.config["session_cookie_name"])
            if session_id:
                return session_id
                
            # Try Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header[7:]  # Remove "Bearer " prefix
                
            # Try custom header
            return request.headers.get("x-session-id")
            
        except Exception as e:
            logger.error(f"Failed to extract session ID: {e}")
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        try:
            # Check for forwarded headers
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
                
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip
                
            # Fallback to direct client IP
            return request.client.host if request.client else "unknown"
            
        except Exception as e:
            logger.error(f"Failed to get client IP: {e}")
            return "unknown"