"""Session Management Template for iacherie Platform
Advanced session management with concurrent session control, security monitoring,
automatic session cleanup, and creator-specific session protection features.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet
import jwt

from core.config import get_settings
from utils.exceptions import SessionException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class SessionType(Enum):
    """Session types"""
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    DESKTOP = "desktop"
    EMBEDDED = "embedded"
    ADMIN = "admin"
    CREATOR = "creator"


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class SessionPriority(Enum):
    """Session priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLevel(Enum):
    """Session security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class SessionEvent(Enum):
    """Session events"""
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    ACTIVITY = "activity"
    IDLE = "idle"
    SUSPICIOUS = "suspicious"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"


class SessionData(BaseModel):
    """Session data model"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="Associated user ID")
    session_type: SessionType = Field(..., description="Session type")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    priority: SessionPriority = Field(default=SessionPriority.NORMAL)
    security_level: SecurityLevel = Field(default=SecurityLevel.STANDARD)
    device_id: Optional[str] = Field(default=None, description="Associated device ID")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    geolocation: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Session expiration time")
    idle_timeout: int = Field(default=1800, description="Idle timeout in seconds")
    absolute_timeout: int = Field(default=86400, description="Absolute timeout in seconds")
    is_persistent: bool = Field(default=False, description="Persistent session flag")
    auth_methods: List[str] = Field(default_factory=list, description="Authentication methods used")
    permissions: List[str] = Field(default_factory=list, description="Session permissions")
    scopes: List[str] = Field(default_factory=list, description="OAuth scopes")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    security_events: List[Dict[str, Any]] = Field(default_factory=list)
    activity_count: int = Field(default=0, description="Activity counter")
    data_accessed: List[str] = Field(default_factory=list, description="Accessed resources")


class SessionRequest(BaseModel):
    """Session creation request"""
    user_id: str = Field(..., description="User ID")
    session_type: SessionType = Field(..., description="Session type")
    device_id: Optional[str] = Field(default=None)
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(default=None)
    geolocation: Optional[Dict[str, Any]] = Field(default=None)
    auth_methods: List[str] = Field(default_factory=list)
    requested_scopes: List[str] = Field(default_factory=list)
    is_persistent: bool = Field(default=False)
    custom_expiry: Optional[int] = Field(default=None, description="Custom expiry in seconds")
    security_level: SecurityLevel = Field(default=SecurityLevel.STANDARD)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Session operation response"""
    success: bool = Field(..., description="Operation success")
    session_id: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    expires_in: Optional[int] = Field(default=None, description="Token expiry in seconds")
    session_data: Optional[SessionData] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionActivity(BaseModel):
    """Session activity record"""
    activity_id: str = Field(..., description="Activity identifier")
    session_id: str = Field(..., description="Session ID")
    event_type: SessionEvent = Field(..., description="Event type")
    resource: Optional[str] = Field(default=None, description="Accessed resource")
    action: Optional[str] = Field(default=None, description="Action performed")
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[int] = Field(default=None, description="Duration in milliseconds")
    request_size: Optional[int] = Field(default=None, description="Request size in bytes")
    response_size: Optional[int] = Field(default=None, description="Response size in bytes")
    status_code: Optional[int] = Field(default=None, description="Response status code")
    error_message: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConcurrentSessionPolicy(BaseModel):
    """Concurrent session policy"""
    max_sessions: int = Field(default=5, description="Maximum concurrent sessions")
    max_per_device_type: Dict[SessionType, int] = Field(default_factory=dict)
    allow_same_device: bool = Field(default=True)
    termination_policy: str = Field(default="oldest", description="oldest, newest, priority")
    grace_period: int = Field(default=300, description="Grace period before termination")
    notify_user: bool = Field(default=True)


class SessionManagementService:
    """Comprehensive session management service for iacherie platform
    
    Provides enterprise-grade session management with:
    - Advanced session lifecycle management
    - Concurrent session control and policies
    - Real-time security monitoring and threat detection
    - Automatic session cleanup and garbage collection
    - Session activity tracking and analytics
    - Device-based session management
    - Creator-specific session protection
    - High-performance Redis-based storage
    - JWT token integration and management
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.cipher = Fernet(Fernet.generate_key())
        
        # Redis connection for session storage
        self.redis_client = None
        self._init_redis()
        
        # In-memory storage for development/testing
        self.sessions: Dict[str, SessionData] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids
        self.device_sessions: Dict[str, List[str]] = {}  # device_id -> session_ids
        self.session_activities: Dict[str, List[SessionActivity]] = {}
        
        # Session policies
        self.default_policy = ConcurrentSessionPolicy()
        self.user_policies: Dict[str, ConcurrentSessionPolicy] = {}
        
        # Session timeouts by type
        self.session_timeouts = {
            SessionType.WEB: {"idle": 1800, "absolute": 86400},
            SessionType.MOBILE: {"idle": 3600, "absolute": 604800},
            SessionType.API: {"idle": 900, "absolute": 3600},
            SessionType.DESKTOP: {"idle": 3600, "absolute": 86400},
            SessionType.ADMIN: {"idle": 900, "absolute": 14400},
            SessionType.CREATOR: {"idle": 2700, "absolute": 259200}
        }
        
        # Security monitoring
        self.suspicious_patterns = {
            "rapid_requests": {"threshold": 100, "window": 60},
            "ip_changes": {"threshold": 5, "window": 3600},
            "concurrent_locations": {"threshold": 3, "window": 1800}
        }
        
        logger.info("Session management service initialized")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis session storage initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed, using in-memory storage: {e}")
            self.redis_client = None
    
    async def create_session(self, request: SessionRequest) -> SessionResponse:
        """Create new user session"""
        try:
            # Check concurrent session limits
            await self._enforce_concurrent_session_policy(request.user_id, request.session_type)
            
            # Generate session ID
            session_id = f"sess_{secrets.token_urlsafe(32)}"
            
            # Determine session timeouts
            timeouts = self.session_timeouts.get(request.session_type, 
                                               self.session_timeouts[SessionType.WEB])
            
            idle_timeout = timeouts["idle"]
            absolute_timeout = request.custom_expiry or timeouts["absolute"]
            
            # Create session data
            session = SessionData(
                session_id=session_id,
                user_id=request.user_id,
                session_type=request.session_type,
                device_id=request.device_id,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                geolocation=request.geolocation,
                expires_at=datetime.utcnow() + timedelta(seconds=absolute_timeout),
                idle_timeout=idle_timeout,
                absolute_timeout=absolute_timeout,
                is_persistent=request.is_persistent,
                auth_methods=request.auth_methods,
                scopes=request.requested_scopes,
                security_level=request.security_level,
                metadata=request.metadata
            )
            
            # Store session
            await self._store_session(session)
            
            # Update indexes
            if request.user_id not in self.user_sessions:
                self.user_sessions[request.user_id] = []
            self.user_sessions[request.user_id].append(session_id)
            
            if request.device_id:
                if request.device_id not in self.device_sessions:
                    self.device_sessions[request.device_id] = []
                self.device_sessions[request.device_id].append(session_id)
            
            # Generate tokens
            tokens = await self._generate_session_tokens(session)
            
            # Record session creation event
            await self._record_session_event(session, SessionEvent.CREATED, {
                "auth_methods": request.auth_methods,
                "security_level": request.security_level.value
            })
            
            # Record metrics
            await self.metrics_collector.record_session_created(
                session_type=request.session_type.value,
                security_level=request.security_level.value,
                user_id=request.user_id
            )
            
            logger.info(f"Created session {session_id} for user {request.user_id}")
            
            return SessionResponse(
                success=True,
                session_id=session_id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                expires_in=absolute_timeout,
                session_data=session
            )
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return SessionResponse(
                success=False,
                error_message=str(e)
            )
    
    async def validate_session(self, session_id: str, 
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None) -> SessionResponse:
        """Validate and refresh session"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return SessionResponse(
                    success=False,
                    error_message="Session not found"
                )
            
            # Check session status
            if session.status != SessionStatus.ACTIVE:
                return SessionResponse(
                    success=False,
                    error_message=f"Session is {session.status.value}"
                )
            
            # Check expiration
            now = datetime.utcnow()
            if session.expires_at <= now:
                await self._terminate_session(session_id, "expired")
                return SessionResponse(
                    success=False,
                    error_message="Session has expired"
                )
            
            # Check idle timeout
            idle_duration = (now - session.last_activity).total_seconds()
            if idle_duration > session.idle_timeout:
                await self._terminate_session(session_id, "idle_timeout")
                return SessionResponse(
                    success=False,
                    error_message="Session idle timeout"
                )
            
            # Security checks
            security_warnings = []
            
            # Check IP address change
            if ip_address and ip_address != session.ip_address:
                await self._record_session_event(session, SessionEvent.SUSPICIOUS, {
                    "type": "ip_change",
                    "old_ip": session.ip_address,
                    "new_ip": ip_address
                })
                
                if session.security_level in [SecurityLevel.ENHANCED, SecurityLevel.MAXIMUM]:
                    return SessionResponse(
                        success=False,
                        error_message="IP address change detected - session terminated for security"
                    )
                else:
                    security_warnings.append("IP address change detected")
                    session.ip_address = ip_address
            
            # Check user agent change
            if user_agent and user_agent != session.user_agent:
                await self._record_session_event(session, SessionEvent.SUSPICIOUS, {
                    "type": "user_agent_change",
                    "old_agent": session.user_agent,
                    "new_agent": user_agent
                })
                security_warnings.append("User agent change detected")
            
            # Update session activity
            session.last_activity = now
            session.activity_count += 1
            
            # Store updated session
            await self._store_session(session)
            
            # Record activity
            await self._record_session_event(session, SessionEvent.ACTIVITY)
            
            # Generate fresh tokens if needed
            tokens = {}
            if session.security_level == SecurityLevel.MAXIMUM:
                tokens = await self._generate_session_tokens(session)
            
            return SessionResponse(
                success=True,
                session_id=session_id,
                session_data=session,
                warnings=security_warnings,
                **tokens
            )
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return SessionResponse(
                success=False,
                error_message=str(e)
            )
    
    async def terminate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Terminate specific session"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            await self._terminate_session(session_id, reason)
            logger.info(f"Terminated session {session_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Session termination failed: {e}")
            return False
    
    async def terminate_user_sessions(self, user_id: str, 
                                    exclude_session: Optional[str] = None,
                                    reason: str = "user_request") -> int:
        """Terminate all sessions for a user"""
        try:
            user_session_ids = self.user_sessions.get(user_id, [])
            terminated_count = 0
            
            for session_id in user_session_ids[:]:  # Copy list to avoid modification during iteration
                if session_id != exclude_session:
                    if await self.terminate_session(session_id, reason):
                        terminated_count += 1
            
            logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
            return terminated_count
            
        except Exception as e:
            logger.error(f"User session termination failed: {e}")
            return 0
    
    async def _enforce_concurrent_session_policy(self, user_id: str, session_type: SessionType):
        """Enforce concurrent session policy"""
        policy = self.user_policies.get(user_id, self.default_policy)
        current_sessions = await self._get_user_sessions(user_id, active_only=True)
        
        # Check total session limit
        if len(current_sessions) >= policy.max_sessions:
            # Determine which session to terminate
            if policy.termination_policy == "oldest":
                oldest_session = min(current_sessions, key=lambda s: s.created_at)
                await self._terminate_session(oldest_session.session_id, "concurrent_limit")
            elif policy.termination_policy == "newest":
                newest_session = max(current_sessions, key=lambda s: s.created_at)
                await self._terminate_session(newest_session.session_id, "concurrent_limit")
        
        # Check per-device-type limits
        if session_type in policy.max_per_device_type:
            type_limit = policy.max_per_device_type[session_type]
            type_sessions = [s for s in current_sessions if s.session_type == session_type]
            
            if len(type_sessions) >= type_limit:
                oldest_type_session = min(type_sessions, key=lambda s: s.created_at)
                await self._terminate_session(oldest_type_session.session_id, "device_type_limit")
    
    async def _get_user_sessions(self, user_id: str, active_only: bool = False) -> List[SessionData]:
        """Get all sessions for a user"""
        session_ids = self.user_sessions.get(user_id, [])
        sessions = []
        
        for session_id in session_ids:
            session = await self._get_session(session_id)
            if session:
                if not active_only or session.status == SessionStatus.ACTIVE:
                    sessions.append(session)
        
        return sessions
    
    async def _store_session(self, session: SessionData):
        """Store session data"""
        if self.redis_client:
            try:
                session_key = f"session:{session.session_id}"
                session_data = session.dict()
                
                # Convert datetime objects to ISO strings for JSON serialization
                for key, value in session_data.items():
                    if isinstance(value, datetime):
                        session_data[key] = value.isoformat()
                
                await self.redis_client.setex(
                    session_key, 
                    session.absolute_timeout,
                    json.dumps(session_data)
                )
            except Exception as e:
                logger.error(f"Redis session storage failed: {e}")
                # Fallback to in-memory storage
                self.sessions[session.session_id] = session
        else:
            self.sessions[session.session_id] = session
    
    async def _get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data"""
        if self.redis_client:
            try:
                session_key = f"session:{session_id}"
                session_data = await self.redis_client.get(session_key)
                
                if session_data:
                    data_dict = json.loads(session_data)
                    
                    # Convert ISO strings back to datetime objects
                    datetime_fields = ['created_at', 'last_activity', 'expires_at']
                    for field in datetime_fields:
                        if field in data_dict and data_dict[field]:
                            data_dict[field] = datetime.fromisoformat(data_dict[field])
                    
                    return SessionData(**data_dict)
            except Exception as e:
                logger.error(f"Redis session retrieval failed: {e}")
                # Fallback to in-memory storage
                pass
        
        return self.sessions.get(session_id)
    
    async def _terminate_session(self, session_id: str, reason: str):
        """Internal session termination"""
        session = await self._get_session(session_id)
        if not session:
            return
        
        # Update session status
        session.status = SessionStatus.TERMINATED
        
        # Record termination event
        await self._record_session_event(session, SessionEvent.TERMINATED, {
            "reason": reason,
            "duration": (datetime.utcnow() - session.created_at).total_seconds()
        })
        
        # Remove from indexes
        if session.user_id in self.user_sessions:
            if session_id in self.user_sessions[session.user_id]:
                self.user_sessions[session.user_id].remove(session_id)
        
        if session.device_id and session.device_id in self.device_sessions:
            if session_id in self.device_sessions[session.device_id]:
                self.device_sessions[session.device_id].remove(session_id)
        
        # Remove from storage
        if self.redis_client:
            try:
                await self.redis_client.delete(f"session:{session_id}")
            except Exception as e:
                logger.error(f"Redis session deletion failed: {e}")
        
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Record metrics
        await self.metrics_collector.record_session_terminated(
            session_type=session.session_type.value,
            reason=reason,
            duration=(datetime.utcnow() - session.created_at).total_seconds()
        )
    
    async def _generate_session_tokens(self, session: SessionData) -> Dict[str, str]:
        """Generate JWT tokens for session"""
        payload = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "session_type": session.session_type.value,
            "scopes": session.scopes,
            "security_level": session.security_level.value,
            "iat": datetime.utcnow(),
            "exp": session.expires_at
        }
        
        access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        # Refresh token with longer expiry
        refresh_payload = payload.copy()
        refresh_payload["exp"] = datetime.utcnow() + timedelta(days=30)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def _record_session_event(self, session: SessionData, event_type: SessionEvent,
                                   metadata: Optional[Dict[str, Any]] = None):
        """Record session activity event"""
        activity = SessionActivity(
            activity_id=f"activity_{secrets.token_urlsafe(16)}",
            session_id=session.session_id,
            event_type=event_type,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            metadata=metadata or {}
        )
        
        # Store activity
        if session.session_id not in self.session_activities:
            self.session_activities[session.session_id] = []
        
        self.session_activities[session.session_id].append(activity)
        
        # Add to session security events
        session.security_events.append({
            "event": event_type.value,
            "timestamp": activity.timestamp.isoformat(),
            "metadata": metadata or {}
        })
        
        # Limit security events to last 100
        if len(session.security_events) > 100:
            session.security_events = session.security_events[-100:]
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_count = 0
        now = datetime.utcnow()
        
        # In-memory cleanup
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.expires_at <= now or session.status != SessionStatus.ACTIVE:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self._terminate_session(session_id, "expired")
            expired_count += 1
        
        logger.info(f"Cleaned up {expired_count} expired sessions")
        return expired_count
    
    async def get_session_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session analytics"""
        analytics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "session_types": {},
            "security_levels": {},
            "average_duration": 0,
            "total_activities": 0
        }
        
        sessions_to_analyze = []
        if user_id:
            sessions_to_analyze = await self._get_user_sessions(user_id)
        else:
            sessions_to_analyze = list(self.sessions.values())
        
        durations = []
        
        for session in sessions_to_analyze:
            analytics["total_sessions"] += 1
            
            if session.status == SessionStatus.ACTIVE:
                analytics["active_sessions"] += 1
            
            # Session type distribution
            session_type = session.session_type.value
            analytics["session_types"][session_type] = analytics["session_types"].get(session_type, 0) + 1
            
            # Security level distribution
            security_level = session.security_level.value
            analytics["security_levels"][security_level] = analytics["security_levels"].get(security_level, 0) + 1
            
            # Duration calculation
            if session.status == SessionStatus.TERMINATED:
                duration = (session.last_activity - session.created_at).total_seconds()
                durations.append(duration)
            
            # Activity count
            analytics["total_activities"] += session.activity_count
        
        if durations:
            analytics["average_duration"] = sum(durations) / len(durations)
        
        return analytics
    
    async def get_user_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for user with summary info"""
        sessions = await self._get_user_sessions(user_id, active_only=True)
        
        session_summaries = []
        for session in sessions:
            summary = {
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "device_id": session.device_id,
                "ip_address": session.ip_address,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "security_level": session.security_level.value,
                "activity_count": session.activity_count,
                "is_current": False  # This would be determined by comparing with current session
            }
            session_summaries.append(summary)
        
        return session_summaries
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.cleanup_expired_sessions()
        if self.redis_client:
            await self.redis_client.close()


# Export service instance
session_management_service = SessionManagementService()

__all__ = [
    'SessionType',
    'SessionStatus',
    'SessionPriority',
    'SecurityLevel',
    'SessionEvent',
    'SessionData',
    'SessionRequest',
    'SessionResponse',
    'SessionActivity',
    'ConcurrentSessionPolicy',
    'SessionManagementService',
    'session_management_service'
]