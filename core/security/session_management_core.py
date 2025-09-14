"""
Session Management Core - Advanced Session Management and Security System
=========================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for session management, session security,
multi-device sessions, and advanced session analytics.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import secrets
from abc import ABC, abstractmethod

# Get logger
logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    LOCKED = "locked"

class DeviceType(Enum):
    """Device types"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    WEB = "web"
    API = "api"
    UNKNOWN = "unknown"

class SessionSecurityLevel(Enum):
    """Session security levels"""
    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    user_id: str
    status: SessionStatus
    device_type: DeviceType
    security_level: SessionSecurityLevel
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityEvent:
    """Security event"""
    event_id: str
    session_id: str
    event_type: str
    severity: str
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class SessionManagementCore:
    """Advanced Session Management Core System"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.version = "2.1.0"
        self.level = level
        self.sessions = {}
        self.user_sessions = {}  # user_id -> [session_ids]
        self.security_events = {}
        self.session_config = {
            "default_ttl": 3600,  # 1 hour
            "max_sessions_per_user": 5,
            "session_rotation_interval": 1800,  # 30 minutes
            "suspicious_activity_threshold": 10
        }
        
        logger.info(f"Session Management Core initialized - Level: {level}")

    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create new session"""
        try:
            session_id = self._generate_session_id()
            
            # Determine device type
            user_agent = session_data.get("user_agent", "")
            device_type = self._detect_device_type(user_agent)
            
            # Determine security level
            security_level = self._determine_security_level(session_data)
            
            # Calculate expiration
            ttl = session_data.get("ttl", self.session_config["default_ttl"])
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Create session info
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                status=SessionStatus.ACTIVE,
                device_type=device_type,
                security_level=security_level,
                ip_address=session_data.get("ip_address", ""),
                user_agent=user_agent,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=expires_at,
                location=session_data.get("location"),
                device_fingerprint=session_data.get("device_fingerprint"),
                metadata=session_data.get("metadata", {})
            )
            
            # Store session
            self.sessions[session_id] = session_info
            
            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Enforce session limits
            await self._enforce_session_limits(user_id)
            
            # Log security event
            await self._log_security_event(session_id, "session_created", "info", "New session created")
            
            logger.info(f"Session created: {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return ""

    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return f"sess_{secrets.token_urlsafe(32)}"

    def _detect_device_type(self, user_agent: str) -> DeviceType:
        """Detect device type from user agent"""
        user_agent_lower = user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            return DeviceType.MOBILE
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return DeviceType.TABLET
        elif "api" in user_agent_lower or "curl" in user_agent_lower:
            return DeviceType.API
        elif any(browser in user_agent_lower for browser in ["chrome", "firefox", "safari", "edge"]):
            return DeviceType.WEB
        else:
            return DeviceType.UNKNOWN

    def _determine_security_level(self, session_data: Dict[str, Any]) -> SessionSecurityLevel:
        """Determine security level based on session data"""
        # Check for high-risk indicators
        risk_factors = 0
        
        # Location risk
        if session_data.get("location") and "unknown" in session_data.get("location", "").lower():
            risk_factors += 1
        
        # IP reputation
        if session_data.get("ip_reputation", "good") == "bad":
            risk_factors += 2
        
        # Device fingerprint
        if not session_data.get("device_fingerprint"):
            risk_factors += 1
        
        # Determine security level
        if risk_factors >= 3:
            return SessionSecurityLevel.CRITICAL
        elif risk_factors >= 2:
            return SessionSecurityLevel.HIGH
        elif risk_factors >= 1:
            return SessionSecurityLevel.STANDARD
        else:
            return SessionSecurityLevel.LOW

    async def _enforce_session_limits(self, user_id -> None: str) -> None:
        """Enforce session limits per user"""
        try:
            user_session_ids = self.user_sessions.get(user_id, [])
            max_sessions = self.session_config["max_sessions_per_user"]
            
            if len(user_session_ids) > max_sessions:
                # Remove oldest sessions
                sessions_to_remove = user_session_ids[:-max_sessions]
                for session_id in sessions_to_remove:
                    await self.terminate_session(session_id, "session_limit_exceeded")
                    
        except Exception as e:
            logger.error(f"Failed to enforce session limits: {str(e)}")

    async def validate_session(self, session_id: str) -> bool:
        """Validate session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Check if session is active
            if session.status != SessionStatus.ACTIVE:
                return False
            
            # Check if session has expired
            if datetime.now() > session.expires_at:
                await self.expire_session(session_id)
                return False
            
            # Update last activity
            session.last_activity = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            return False

    async def refresh_session(self, session_id: str, extend_ttl: bool = True) -> bool:
        """Refresh session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            if session.status != SessionStatus.ACTIVE:
                return False
            
            # Update last activity
            session.last_activity = datetime.now()
            
            # Extend TTL if requested
            if extend_ttl:
                ttl = self.session_config["default_ttl"]
                session.expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Check if session rotation is needed
            rotation_interval = self.session_config["session_rotation_interval"]
            if (datetime.now() - session.created_at).total_seconds() > rotation_interval:
                return await self._rotate_session(session_id)
            
            logger.info(f"Session refreshed: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session refresh failed: {str(e)}")
            return False

    async def _rotate_session(self, old_session_id: str) -> bool:
        """Rotate session ID for security"""
        try:
            old_session = self.sessions.get(old_session_id)
            if not old_session:
                return False
            
            # Create new session with same data
            new_session_id = self._generate_session_id()
            new_session = SessionInfo(
                session_id=new_session_id,
                user_id=old_session.user_id,
                status=old_session.status,
                device_type=old_session.device_type,
                security_level=old_session.security_level,
                ip_address=old_session.ip_address,
                user_agent=old_session.user_agent,
                created_at=datetime.now(),  # New creation time
                last_activity=datetime.now(),
                expires_at=old_session.expires_at,
                location=old_session.location,
                device_fingerprint=old_session.device_fingerprint,
                metadata=old_session.metadata
            )
            
            # Store new session
            self.sessions[new_session_id] = new_session
            
            # Update user sessions
            user_sessions = self.user_sessions.get(old_session.user_id, [])
            if old_session_id in user_sessions:
                user_sessions.remove(old_session_id)
                user_sessions.append(new_session_id)
            
            # Remove old session
            del self.sessions[old_session_id]
            
            # Log security event
            await self._log_security_event(new_session_id, "session_rotated", "info", 
                                          f"Session rotated from {old_session_id}")
            
            logger.info(f"Session rotated: {old_session_id} -> {new_session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session rotation failed: {str(e)}")
            return False

    async def terminate_session(self, session_id: str, reason: str = "manual") -> bool:
        """Terminate session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = SessionStatus.TERMINATED
            
            # Remove from user sessions
            user_sessions = self.user_sessions.get(session.user_id, [])
            if session_id in user_sessions:
                user_sessions.remove(session_id)
            
            # Log security event
            await self._log_security_event(session_id, "session_terminated", "info", 
                                          f"Session terminated: {reason}")
            
            logger.info(f"Session terminated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session termination failed: {str(e)}")
            return False

    async def expire_session(self, session_id: str) -> bool:
        """Expire session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = SessionStatus.EXPIRED
            
            # Log security event
            await self._log_security_event(session_id, "session_expired", "info", "Session expired")
            
            logger.info(f"Session expired: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session expiration failed: {str(e)}")
            return False

    async def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """Get all sessions for user"""
        try:
            session_ids = self.user_sessions.get(user_id, [])
            return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []

    async def _log_security_event(self, session_id -> None: str, event_type -> None: str, severity -> None: str, description -> None: str) -> None:
        """Log security event"""
        try:
            event_id = f"evt_{uuid.uuid4().hex[:8]}"
            
            event = SecurityEvent(
                event_id=event_id,
                session_id=session_id,
                event_type=event_type,
                severity=severity,
                description=description,
                timestamp=datetime.now()
            )
            
            self.security_events[event_id] = event
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")

    async def get_session_analytics(self, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get session analytics"""
        try:
            analytics = {
                "total_sessions": 0,
                "active_sessions": 0,
                "expired_sessions": 0,
                "terminated_sessions": 0,
                "device_distribution": {},
                "security_level_distribution": {},
                "average_session_duration": 0,
                "security_events": 0
            }
            
            session_durations = []
            
            for session in self.sessions.values():
                if time_range[0] <= session.created_at <= time_range[1]:
                    analytics["total_sessions"] += 1
                    
                    # Count by status
                    if session.status == SessionStatus.ACTIVE:
                        analytics["active_sessions"] += 1
                    elif session.status == SessionStatus.EXPIRED:
                        analytics["expired_sessions"] += 1
                    elif session.status == SessionStatus.TERMINATED:
                        analytics["terminated_sessions"] += 1
                    
                    # Device distribution
                    device = session.device_type.value
                    analytics["device_distribution"][device] = analytics["device_distribution"].get(device, 0) + 1
                    
                    # Security level distribution
                    security = session.security_level.value
                    analytics["security_level_distribution"][security] = analytics["security_level_distribution"].get(security, 0) + 1
                    
                    # Session duration
                    if session.status != SessionStatus.ACTIVE:
                        duration = (session.last_activity - session.created_at).total_seconds()
                        session_durations.append(duration)
            
            # Calculate average session duration
            if session_durations:
                analytics["average_session_duration"] = sum(session_durations) / len(session_durations)
            
            # Count security events
            analytics["security_events"] = len([
                e for e in self.security_events.values()
                if time_range[0] <= e.timestamp <= time_range[1]
            ])
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {str(e)}")
            return {}

# Module exports
__all__ = [
    "SessionManagementCore",
    "SessionStatus",
    "DeviceType",
    "SessionSecurityLevel",
    "SessionInfo",
    "SecurityEvent"
]

logger.info("🔐 Session Management Core module loaded")