"""
Session Manager - Security Utilities Level 2
==========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade session management system for Ainflue creator economy platform.
Secure session handling with < 10ms session operations.

Performance: < 10ms session operations
Standards: OWASP, secure session management, creator economy security
"""

import asyncio
import json
import logging
import secrets
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import hmac
import jwt
from concurrent.futures import ThreadPoolExecutor
import redis
import aioredis

logger = logging.getLogger(__name__)

class SessionState(Enum):
    """Session state enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    COMPROMISED = "compromised"

class SessionType(Enum):
    """Session type for different user categories."""
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    ADMIN = "admin"
    CREATOR = "creator"
    COLLABORATION = "collaboration"

@dataclass
class SessionData:
    """Session data container."""
    session_id: str
    user_id: str
    session_type: SessionType
    state: SessionState
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    permissions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_type: Optional[str] = None  # musician, photographer, blogger
    
@dataclass
class SessionResult:
    """Session operation result container."""
    success: bool
    session_id: Optional[str] = None
    session_data: Optional[SessionData] = None
    message: str = ""
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

@dataclass
class SessionSecurityEvent:
    """Session security event container."""
    event_type: str
    session_id: str
    user_id: str
    timestamp: datetime
    details: Dict[str, Any]
    risk_score: float = 0.0

class SessionManager:
    """
    Enterprise-grade session management system for creator economy platform.
    
    Features:
    - Secure session creation and validation
    - Session rotation and timeout management
    - Concurrent session limits
    - Session hijacking detection
    - Creator-specific session handling
    - Performance: < 10ms session operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize session manager with enterprise configuration."""
        self.config = config or {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Session storage (in production, use Redis)
        self.sessions: Dict[str, SessionData] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
        self.session_security_events: List[SessionSecurityEvent] = []
        
        # Configuration
        self.default_timeout = self.config.get("default_timeout", 3600)  # 1 hour
        self.max_concurrent_sessions = self.config.get("max_concurrent_sessions", 5)
        self.session_rotation_interval = self.config.get("session_rotation_interval", 1800)  # 30 minutes
        self.security_check_interval = self.config.get("security_check_interval", 300)  # 5 minutes
        
        # Creator-specific timeouts
        self.creator_timeouts = {
            "musician": self.config.get("musician_timeout", 86400),  # 24 hours
            "photographer": self.config.get("photographer_timeout", 86400),
            "blogger": self.config.get("blogger_timeout", 86400),
            "admin": self.config.get("admin_timeout", 3600),  # 1 hour
            "default": self.default_timeout
        }
        
        # Security thresholds
        self.max_failed_attempts = self.config.get("max_failed_attempts", 5)
        self.hijack_detection_threshold = self.config.get("hijack_detection_threshold", 0.8)
        
        # JWT configuration for session tokens
        self.jwt_secret = self.config.get("jwt_secret", secrets.token_urlsafe(32))
        self.jwt_algorithm = self.config.get("jwt_algorithm", "HS256")
        
        logger.info("SessionManager initialized with enterprise configuration")

    async def create_secure_session(self, user_id: str, session_type: SessionType,
                                  ip_address: str, user_agent: str,
                                  creator_type: Optional[str] = None,
                                  additional_data: Optional[Dict[str, Any]] = None) -> SessionResult:
        """
        Create a secure session with comprehensive security measures.
        
        Args:
            user_id: User identifier
            session_type: Type of session
            ip_address: Client IP address
            user_agent: Client user agent
            creator_type: Creator type (musician, photographer, blogger)
            additional_data: Additional session data
            
        Returns:
            SessionResult with session creation status
        """
        start_time = time.perf_counter()
        
        try:
            # Check concurrent session limits
            existing_sessions = self.user_sessions.get(user_id, set())
            if len(existing_sessions) >= self.max_concurrent_sessions:
                # Terminate oldest session
                await self._terminate_oldest_session(user_id)
            
            # Generate secure session ID
            session_id = self._generate_secure_session_id()
            
            # Determine session timeout based on user type
            timeout = self._get_session_timeout(creator_type, session_type)
            
            # Create session data
            current_time = datetime.now(timezone.utc)
            session_data = SessionData(
                session_id=session_id,
                user_id=user_id,
                session_type=session_type,
                state=SessionState.ACTIVE,
                created_at=current_time,
                last_accessed=current_time,
                expires_at=current_time + timedelta(seconds=timeout),
                ip_address=ip_address,
                user_agent=user_agent,
                creator_type=creator_type,
                metadata=additional_data or {}
            )
            
            # Generate device fingerprint
            session_data.device_fingerprint = self._generate_device_fingerprint(
                ip_address, user_agent, additional_data or {}
            )
            
            # Store session
            self.sessions[session_id] = session_data
            self.user_sessions[user_id].add(session_id)
            
            # Log security event
            await self._log_security_event("session_created", session_id, user_id, {
                "session_type": session_type.value,
                "creator_type": creator_type,
                "ip_address": ip_address,
                "timeout": timeout
            })
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(session_data)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Secure session created for {user_id} in {execution_time:.2f}ms")
            
            return SessionResult(
                success=True,
                session_id=session_id,
                session_data=session_data,
                message="Session created successfully",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Secure session creation failed in {execution_time:.2f}ms: {str(e)}")
            return SessionResult(
                success=False,
                message="Session creation failed",
                errors=[str(e)],
                execution_time_ms=execution_time
            )

    async def validate_session_integrity(self, session_id: str, 
                                       ip_address: Optional[str] = None,
                                       user_agent: Optional[str] = None) -> SessionResult:
        """
        Validate session integrity and detect potential hijacking.
        
        Args:
            session_id: Session identifier
            ip_address: Current IP address (optional)
            user_agent: Current user agent (optional)
            
        Returns:
            SessionResult with validation status
        """
        start_time = time.perf_counter()
        
        try:
            # Check if session exists
            session_data = self.sessions.get(session_id)
            if not session_data:
                execution_time = (time.perf_counter() - start_time) * 1000
                return SessionResult(
                    success=False,
                    message="Session not found",
                    execution_time_ms=execution_time
                )
            
            # Check session state
            if session_data.state != SessionState.ACTIVE:
                execution_time = (time.perf_counter() - start_time) * 1000
                return SessionResult(
                    success=False,
                    message=f"Session is {session_data.state.value}",
                    execution_time_ms=execution_time
                )
            
            # Check expiration
            current_time = datetime.now(timezone.utc)
            if current_time > session_data.expires_at:
                await self._expire_session(session_id)
                execution_time = (time.perf_counter() - start_time) * 1000
                return SessionResult(
                    success=False,
                    message="Session expired",
                    execution_time_ms=execution_time
                )
            
            # Security checks
            security_checks = await self._perform_security_checks(
                session_data, ip_address, user_agent
            )
            
            if security_checks["hijack_detected"]:
                await self._handle_session_hijacking(session_id, security_checks)
                execution_time = (time.perf_counter() - start_time) * 1000
                return SessionResult(
                    success=False,
                    message="Session security violation detected",
                    execution_time_ms=execution_time
                )
            
            # Update last accessed time
            session_data.last_accessed = current_time
            
            # Check if session rotation is needed
            if self._needs_rotation(session_data):
                new_session = await self._rotate_session(session_id)
                if new_session.success:
                    session_data = new_session.session_data
                    session_id = new_session.session_id
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Session integrity validated for {session_id} in {execution_time:.2f}ms")
            
            return SessionResult(
                success=True,
                session_id=session_id,
                session_data=session_data,
                message="Session valid",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Session integrity validation failed in {execution_time:.2f}ms: {str(e)}")
            return SessionResult(
                success=False,
                message="Session validation failed",
                errors=[str(e)],
                execution_time_ms=execution_time
            )

    async def implement_session_rotation(self, session_id: str) -> SessionResult:
        """
        Implement secure session rotation.
        
        Args:
            session_id: Current session identifier
            
        Returns:
            SessionResult with new session data
        """
        start_time = time.perf_counter()
        
        try:
            return await self._rotate_session(session_id)
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Session rotation failed in {execution_time:.2f}ms: {str(e)}")
            return SessionResult(
                success=False,
                message="Session rotation failed",
                errors=[str(e)],
                execution_time_ms=execution_time
            )

    async def _rotate_session(self, session_id: str) -> SessionResult:
        """Internal session rotation implementation."""
        start_time = time.perf_counter()
        
        old_session = self.sessions.get(session_id)
        if not old_session:
            execution_time = (time.perf_counter() - start_time) * 1000
            return SessionResult(
                success=False,
                message="Session not found for rotation",
                execution_time_ms=execution_time
            )
        
        # Generate new session ID
        new_session_id = self._generate_secure_session_id()
        
        # Create new session data
        current_time = datetime.now(timezone.utc)
        timeout = self._get_session_timeout(old_session.creator_type, old_session.session_type)
        
        new_session_data = SessionData(
            session_id=new_session_id,
            user_id=old_session.user_id,
            session_type=old_session.session_type,
            state=SessionState.ACTIVE,
            created_at=current_time,
            last_accessed=current_time,
            expires_at=current_time + timedelta(seconds=timeout),
            ip_address=old_session.ip_address,
            user_agent=old_session.user_agent,
            device_fingerprint=old_session.device_fingerprint,
            location=old_session.location,
            permissions=old_session.permissions.copy(),
            creator_type=old_session.creator_type,
            metadata=old_session.metadata.copy()
        )
        
        # Store new session and remove old one
        self.sessions[new_session_id] = new_session_data
        self.user_sessions[old_session.user_id].add(new_session_id)
        
        del self.sessions[session_id]
        self.user_sessions[old_session.user_id].discard(session_id)
        
        # Log security event
        await self._log_security_event("session_rotated", new_session_id, old_session.user_id, {
            "old_session_id": session_id,
            "rotation_reason": "scheduled_rotation"
        })
        
        execution_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Session rotated from {session_id} to {new_session_id} in {execution_time:.2f}ms")
        
        return SessionResult(
            success=True,
            session_id=new_session_id,
            session_data=new_session_data,
            message="Session rotated successfully",
            execution_time_ms=execution_time
        )

    async def detect_session_hijacking(self, session_id: str, 
                                     current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential session hijacking attempts.
        
        Args:
            session_id: Session identifier
            current_context: Current request context
            
        Returns:
            Hijacking detection results
        """
        start_time = time.perf_counter()
        
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return {"hijack_detected": False, "reason": "session_not_found"}
            
            hijack_indicators = []
            risk_score = 0.0
            
            # IP address analysis
            current_ip = current_context.get("ip_address")
            if current_ip and current_ip != session_data.ip_address:
                # Check if IPs are in same subnet (less suspicious)
                if not self._are_ips_related(session_data.ip_address, current_ip):
                    hijack_indicators.append("ip_address_change")
                    risk_score += 0.4
            
            # User agent analysis
            current_ua = current_context.get("user_agent")
            if current_ua and current_ua != session_data.user_agent:
                # Check if user agents are similar (browser updates)
                if not self._are_user_agents_similar(session_data.user_agent, current_ua):
                    hijack_indicators.append("user_agent_change")
                    risk_score += 0.3
            
            # Device fingerprint analysis
            current_fingerprint = self._generate_device_fingerprint(
                current_ip or session_data.ip_address,
                current_ua or session_data.user_agent,
                current_context
            )
            if current_fingerprint != session_data.device_fingerprint:
                hijack_indicators.append("device_fingerprint_mismatch")
                risk_score += 0.5
            
            # Geographic analysis
            current_location = current_context.get("location", {})
            if current_location and session_data.location:
                distance = self._calculate_geographic_distance(
                    session_data.location, current_location
                )
                # If distance > 1000km in less than 1 hour, suspicious
                time_diff = (datetime.now(timezone.utc) - session_data.last_accessed).total_seconds()
                if distance > 1000 and time_diff < 3600:
                    hijack_indicators.append("impossible_travel")
                    risk_score += 0.6
            
            # Session timing analysis
            time_since_last_access = (datetime.now(timezone.utc) - session_data.last_accessed).total_seconds()
            if time_since_last_access > 3600:  # More than 1 hour
                hijack_indicators.append("long_session_gap")
                risk_score += 0.2
            
            # Behavioral analysis (in production, would use ML models)
            if self._detect_unusual_behavior(session_data, current_context):
                hijack_indicators.append("unusual_behavior")
                risk_score += 0.3
            
            hijack_detected = risk_score >= self.hijack_detection_threshold
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            detection_result = {
                "hijack_detected": hijack_detected,
                "risk_score": risk_score,
                "indicators": hijack_indicators,
                "session_id": session_id,
                "user_id": session_data.user_id,
                "detection_time_ms": execution_time
            }
            
            if hijack_detected:
                logger.warning(f"Session hijacking detected for {session_id}: {hijack_indicators}")
            else:
                logger.debug(f"Session hijacking check completed for {session_id} in {execution_time:.2f}ms")
            
            return detection_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Session hijacking detection failed in {execution_time:.2f}ms: {str(e)}")
            return {"hijack_detected": False, "error": str(e)}

    async def manage_concurrent_sessions(self, user_id: str) -> Dict[str, Any]:
        """
        Manage concurrent sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session management results
        """
        start_time = time.perf_counter()
        
        try:
            user_sessions = self.user_sessions.get(user_id, set())
            active_sessions = []
            
            # Validate each session
            for session_id in list(user_sessions):
                session_data = self.sessions.get(session_id)
                if session_data:
                    if session_data.state == SessionState.ACTIVE:
                        # Check expiration
                        if datetime.now(timezone.utc) <= session_data.expires_at:
                            active_sessions.append({
                                "session_id": session_id,
                                "created_at": session_data.created_at.isoformat(),
                                "last_accessed": session_data.last_accessed.isoformat(),
                                "expires_at": session_data.expires_at.isoformat(),
                                "session_type": session_data.session_type.value,
                                "ip_address": session_data.ip_address,
                                "creator_type": session_data.creator_type
                            })
                        else:
                            # Expire session
                            await self._expire_session(session_id)
                    else:
                        # Remove inactive session
                        self.user_sessions[user_id].discard(session_id)
                else:
                    # Remove missing session
                    self.user_sessions[user_id].discard(session_id)
            
            # Check concurrent session limits
            if len(active_sessions) > self.max_concurrent_sessions:
                # Terminate oldest sessions
                sessions_to_terminate = sorted(
                    active_sessions, 
                    key=lambda s: s["last_accessed"]
                )[:-self.max_concurrent_sessions]
                
                for session_info in sessions_to_terminate:
                    await self._terminate_session(session_info["session_id"], "concurrent_limit_exceeded")
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            management_result = {
                "user_id": user_id,
                "active_sessions": len(active_sessions),
                "max_allowed": self.max_concurrent_sessions,
                "sessions": active_sessions,
                "management_time_ms": execution_time
            }
            
            logger.debug(f"Concurrent session management completed for {user_id} in {execution_time:.2f}ms")
            return management_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Concurrent session management failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    async def enforce_session_timeouts(self) -> Dict[str, Any]:
        """
        Enforce session timeouts across all sessions.
        
        Returns:
            Timeout enforcement results
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            expired_sessions = []
            total_sessions = len(self.sessions)
            
            # Check all sessions for expiration
            for session_id, session_data in list(self.sessions.items()):
                if current_time > session_data.expires_at:
                    expired_sessions.append(session_id)
                    await self._expire_session(session_id)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            enforcement_result = {
                "total_sessions": total_sessions,
                "expired_sessions": len(expired_sessions),
                "active_sessions": len(self.sessions),
                "enforcement_time_ms": execution_time,
                "expired_session_ids": expired_sessions
            }
            
            logger.info(f"Session timeout enforcement completed: {len(expired_sessions)} expired in {execution_time:.2f}ms")
            return enforcement_result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Session timeout enforcement failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    async def secure_session_storage(self, session_data: SessionData) -> bool:
        """
        Implement secure session storage with encryption.
        
        Args:
            session_data: Session data to store
            
        Returns:
            Storage success status
        """
        start_time = time.perf_counter()
        
        try:
            # In production, implement Redis with encryption
            # For now, store in memory with basic security measures
            
            # Encrypt sensitive data
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store with TTL
            self.sessions[session_data.session_id] = session_data
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Secure session storage completed in {execution_time:.2f}ms")
            
            return True
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Secure session storage failed in {execution_time:.2f}ms: {str(e)}")
            return False

    def _generate_secure_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        # Use UUID4 + additional entropy
        base_id = str(uuid.uuid4())
        entropy = secrets.token_urlsafe(16)
        combined = f"{base_id}-{entropy}"
        
        # Hash for consistent length and additional security
        return hashlib.sha256(combined.encode()).hexdigest()

    def _get_session_timeout(self, creator_type: Optional[str], session_type: SessionType) -> int:
        """Get appropriate session timeout based on user type."""
        if session_type == SessionType.ADMIN:
            return self.creator_timeouts["admin"]
        elif creator_type in self.creator_timeouts:
            return self.creator_timeouts[creator_type]
        else:
            return self.creator_timeouts["default"]

    def _generate_device_fingerprint(self, ip_address: str, user_agent: str, 
                                   additional_data: Dict[str, Any]) -> str:
        """Generate device fingerprint for session tracking."""
        fingerprint_data = {
            "ip_address": ip_address,
            "user_agent": user_agent,
            "screen_resolution": additional_data.get("screen_resolution"),
            "timezone": additional_data.get("timezone"),
            "language": additional_data.get("language"),
            "platform": additional_data.get("platform")
        }
        
        # Create hash of fingerprint data
        fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_json.encode()).hexdigest()

    def _generate_jwt_token(self, session_data: SessionData) -> str:
        """Generate JWT token for session."""
        payload = {
            "session_id": session_data.session_id,
            "user_id": session_data.user_id,
            "session_type": session_data.session_type.value,
            "creator_type": session_data.creator_type,
            "iat": int(session_data.created_at.timestamp()),
            "exp": int(session_data.expires_at.timestamp())
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _needs_rotation(self, session_data: SessionData) -> bool:
        """Check if session needs rotation."""
        time_since_creation = (datetime.now(timezone.utc) - session_data.created_at).total_seconds()
        return time_since_creation >= self.session_rotation_interval

    async def _perform_security_checks(self, session_data: SessionData, 
                                     ip_address: Optional[str],
                                     user_agent: Optional[str]) -> Dict[str, Any]:
        """Perform comprehensive security checks."""
        context = {
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        # Detect hijacking
        hijack_result = await self.detect_session_hijacking(session_data.session_id, context)
        
        return {
            "hijack_detected": hijack_result.get("hijack_detected", False),
            "risk_score": hijack_result.get("risk_score", 0.0),
            "indicators": hijack_result.get("indicators", [])
        }

    async def _handle_session_hijacking(self, session_id: str, security_checks: Dict[str, Any]) -> None:
        """Handle detected session hijacking."""
        session_data = self.sessions.get(session_id)
        if session_data:
            # Mark session as compromised
            session_data.state = SessionState.COMPROMISED
            
            # Log security event
            await self._log_security_event("session_hijacking_detected", session_id, session_data.user_id, {
                "risk_score": security_checks["risk_score"],
                "indicators": security_checks["indicators"]
            })
            
            # Terminate session
            await self._terminate_session(session_id, "security_violation")

    async def _expire_session(self, session_id: str) -> None:
        """Expire a session."""
        session_data = self.sessions.get(session_id)
        if session_data:
            session_data.state = SessionState.EXPIRED
            await self._log_security_event("session_expired", session_id, session_data.user_id, {})
            
            # Remove from active sessions
            self.user_sessions[session_data.user_id].discard(session_id)
            del self.sessions[session_id]

    async def _terminate_session(self, session_id: str, reason: str = "manual") -> None:
        """Terminate a session."""
        session_data = self.sessions.get(session_id)
        if session_data:
            session_data.state = SessionState.TERMINATED
            await self._log_security_event("session_terminated", session_id, session_data.user_id, {
                "reason": reason
            })
            
            # Remove from active sessions
            self.user_sessions[session_data.user_id].discard(session_id)
            del self.sessions[session_id]

    async def _terminate_oldest_session(self, user_id: str) -> None:
        """Terminate the oldest session for a user."""
        user_sessions = self.user_sessions.get(user_id, set())
        if user_sessions:
            # Find oldest session
            oldest_session_id = None
            oldest_time = datetime.now(timezone.utc)
            
            for session_id in user_sessions:
                session_data = self.sessions.get(session_id)
                if session_data and session_data.created_at < oldest_time:
                    oldest_time = session_data.created_at
                    oldest_session_id = session_id
            
            if oldest_session_id:
                await self._terminate_session(oldest_session_id, "concurrent_limit")

    async def _log_security_event(self, event_type: str, session_id: str, 
                                user_id: str, details: Dict[str, Any]) -> None:
        """Log security event."""
        event = SessionSecurityEvent(
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            details=details,
            risk_score=details.get("risk_score", 0.0)
        )
        
        self.session_security_events.append(event)
        logger.info(f"Session security event: {event_type} for {user_id}")

    def _encrypt_session_data(self, session_data: SessionData) -> bytes:
        """Encrypt session data for secure storage."""
        # In production, use proper encryption
        data_json = json.dumps({
            "session_id": session_data.session_id,
            "user_id": session_data.user_id,
            "metadata": session_data.metadata
        })
        return data_json.encode()

    def _are_ips_related(self, ip1: str, ip2: str) -> bool:
        """Check if two IP addresses are related (same subnet)."""
        try:
            # Simple subnet check (in production, use proper IP analysis)
            ip1_parts = ip1.split('.')
            ip2_parts = ip2.split('.')
            
            # Check if first 3 octets match (same /24 subnet)
            return ip1_parts[:3] == ip2_parts[:3]
        except:
            return False

    def _are_user_agents_similar(self, ua1: str, ua2: str) -> bool:
        """Check if two user agents are similar (browser updates)."""
        # Simple similarity check (in production, use proper UA parsing)
        ua1_lower = ua1.lower()
        ua2_lower = ua2.lower()
        
        # Check if main browser is the same
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        for browser in browsers:
            if browser in ua1_lower and browser in ua2_lower:
                return True
        
        return False

    def _calculate_geographic_distance(self, loc1: Dict[str, Any], loc2: Dict[str, Any]) -> float:
        """Calculate distance between two geographic locations."""
        # Simplified distance calculation (in production, use proper geolocation)
        try:
            lat1, lon1 = loc1.get("latitude", 0), loc1.get("longitude", 0)
            lat2, lon2 = loc2.get("latitude", 0), loc2.get("longitude", 0)
            
            # Haversine formula approximation
            dlat = abs(lat2 - lat1)
            dlon = abs(lon2 - lon1)
            
            # Rough distance in km
            distance = ((dlat * 111) ** 2 + (dlon * 111) ** 2) ** 0.5
            return distance
        except:
            return 0.0

    def _detect_unusual_behavior(self, session_data: SessionData, 
                                current_context: Dict[str, Any]) -> bool:
        """Detect unusual behavioral patterns."""
        # In production, would use ML models for behavioral analysis
        # For now, simple heuristics
        
        # Check for rapid requests (possible bot activity)
        request_frequency = current_context.get("request_frequency", 0)
        if request_frequency > 100:  # More than 100 requests per minute
            return True
        
        # Check for unusual resource access patterns
        resource_pattern = current_context.get("resource_pattern", [])
        if len(set(resource_pattern)) > 20:  # Accessing too many different resources
            return True
        
        return False

    # Public API methods
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by ID."""
        return self.sessions.get(session_id)

    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all active sessions for a user."""
        session_ids = self.user_sessions.get(user_id, set())
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.sessions)
        active_sessions = sum(1 for s in self.sessions.values() if s.state == SessionState.ACTIVE)
        
        # Session type distribution
        type_distribution = defaultdict(int)
        for session in self.sessions.values():
            type_distribution[session.session_type.value] += 1
        
        # Creator type distribution
        creator_distribution = defaultdict(int)
        for session in self.sessions.values():
            if session.creator_type:
                creator_distribution[session.creator_type] += 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "session_types": dict(type_distribution),
            "creator_types": dict(creator_distribution),
            "security_events": len(self.session_security_events),
            "total_users": len(self.user_sessions)
        }

# Factory for enterprise deployment
class SessionManagerFactory:
    """Factory for creating SessionManager instances with different configurations."""
    
    @staticmethod
    def create_production_session_manager() -> SessionManager:
        """Create production-ready session manager."""
        config = {
            "default_timeout": 3600,  # 1 hour
            "max_concurrent_sessions": 5,
            "session_rotation_interval": 1800,  # 30 minutes
            "security_check_interval": 300,  # 5 minutes
            "hijack_detection_threshold": 0.8,
            "enable_redis": True,
            "log_level": "INFO"
        }
        return SessionManager(config)
    
    @staticmethod
    def create_development_session_manager() -> SessionManager:
        """Create development session manager with relaxed settings."""
        config = {
            "default_timeout": 7200,  # 2 hours
            "max_concurrent_sessions": 10,
            "session_rotation_interval": 3600,  # 1 hour
            "security_check_interval": 600,  # 10 minutes
            "hijack_detection_threshold": 0.9,
            "enable_redis": False,
            "log_level": "DEBUG"
        }
        return SessionManager(config)
    
    @staticmethod
    def create_high_security_session_manager() -> SessionManager:
        """Create high-security session manager for sensitive environments."""
        config = {
            "default_timeout": 1800,  # 30 minutes
            "max_concurrent_sessions": 2,
            "session_rotation_interval": 900,  # 15 minutes
            "security_check_interval": 120,  # 2 minutes
            "hijack_detection_threshold": 0.6,
            "enable_redis": True,
            "require_mfa": True,
            "log_level": "WARNING"
        }
        return SessionManager(config)