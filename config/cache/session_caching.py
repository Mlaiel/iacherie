#!/usr/bin/env python3
"""
Session Caching Implementation
Advanced session management with user sessions, crawler sessions, and automatic cleanup
"""
import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class SessionType(Enum):
    """Session types for different use cases"""
    USER = "user"
    CRAWLER = "crawler"
    API = "api"
    ADMIN = "admin"
    TEMPORARY = "temporary"
    GUEST = "guest"

class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

@dataclass
class SessionEntry:
    """Session data entry"""
    session_id: str
    session_type: SessionType
    user_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionConfig:
    """Session cache configuration"""
    default_ttl: int = 3600  # 1 hour
    max_sessions_per_user: int = 10
    cleanup_interval: int = 300  # 5 minutes
    enable_tracking: bool = True
    enable_notifications: bool = True
    session_ttls: Dict[SessionType, int] = field(default_factory=lambda: {
        SessionType.USER: 7200,      # 2 hours
        SessionType.CRAWLER: 1800,   # 30 minutes
        SessionType.API: 3600,       # 1 hour
        SessionType.ADMIN: 14400,    # 4 hours
        SessionType.TEMPORARY: 300,  # 5 minutes
        SessionType.GUEST: 1800      # 30 minutes
    })

class SessionCacheManager:
    """
    Advanced Session Cache Manager
    
    Features:
    - Multiple session types
    - Automatic expiration and cleanup
    - User session limits
    - Activity tracking
    - Session extension
    - Security monitoring
    - Notification support
    """
    
    def __init__(self, cache_manager, config: Optional[SessionConfig] = None, event_bus=None):
        self.cache_manager = cache_manager
        self.config = config or SessionConfig()
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"{__name__}.SessionCacheManager")
        
        # Key prefixes
        self.session_prefix = "session:"
        self.user_index_prefix = "user_sessions:"
        self.type_index_prefix = "type_sessions:"
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "expired_sessions": 0,
            "revoked_sessions": 0,
            "cleanup_runs": 0
        }
        
        # Background tasks
        self.cleanup_task = None
    
    async def initialize(self):
        """Initialize session cache manager"""
        self.logger.info("🔧 Initializing session cache manager...")
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Load existing session stats
        await self._load_session_stats()
        
        self.logger.info("✅ Session cache manager initialized")
    
    async def create_session(self, session_type: SessionType, user_id: Optional[str] = None,
                           data: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None,
                           ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                           tags: Optional[Set[str]] = None) -> str:
        """Create new session"""
        
        try:
            # Generate session ID
            session_id = self._generate_session_id()
            
            # Get TTL for session type
            if ttl is None:
                ttl = self.config.session_ttls.get(session_type, self.config.default_ttl)
            
            # Check user session limit
            if user_id and session_type == SessionType.USER:
                await self._enforce_user_session_limit(user_id)
            
            # Create session entry
            session_entry = SessionEntry(
                session_id=session_id,
                session_type=session_type,
                user_id=user_id,
                data=data or {},
                expires_at=datetime.now() + timedelta(seconds=ttl),
                ip_address=ip_address,
                user_agent=user_agent,
                tags=tags or set()
            )
            
            # Store session
            session_key = self._make_session_key(session_id)
            await self.cache_manager.set(session_key, session_entry.__dict__, ttl)
            
            # Update indexes
            await self._update_indexes(session_entry, action="create")
            
            # Update statistics
            self.stats["total_sessions"] += 1
            self.stats["active_sessions"] += 1
            
            # Send notification
            await self._send_notification("session_created", session_entry)
            
            self.logger.debug(f"Created {session_type.value} session {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionEntry]:
        """Get session by ID"""
        try:
            session_key = self._make_session_key(session_id)
            session_data = await self.cache_manager.get(session_key)
            
            if not session_data:
                return None
            
            # Convert to SessionEntry
            session_entry = SessionEntry(**session_data)
            
            # Check if expired
            if session_entry.expires_at and session_entry.expires_at < datetime.now():
                await self.revoke_session(session_id, reason="expired")
                return None
            
            # Update last accessed time
            session_entry.last_accessed = datetime.now()
            await self.cache_manager.set(session_key, session_entry.__dict__, 
                                       ttl=self._calculate_remaining_ttl(session_entry))
            
            return session_entry
            
        except Exception as e:
            self.logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_entry = await self.get_session(session_id)
            if not session_entry:
                return False
            
            # Update data
            session_entry.data.update(data)
            session_entry.last_accessed = datetime.now()
            
            # Store updated session
            session_key = self._make_session_key(session_id)
            await self.cache_manager.set(session_key, session_entry.__dict__,
                                       ttl=self._calculate_remaining_ttl(session_entry))
            
            # Send notification
            await self._send_notification("session_updated", session_entry)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    async def extend_session(self, session_id: str, additional_seconds: int) -> bool:
        """Extend session expiration time"""
        try:
            session_entry = await self.get_session(session_id)
            if not session_entry:
                return False
            
            # Extend expiration
            if session_entry.expires_at:
                session_entry.expires_at += timedelta(seconds=additional_seconds)
            
            session_entry.last_accessed = datetime.now()
            
            # Store updated session
            session_key = self._make_session_key(session_id)
            await self.cache_manager.set(session_key, session_entry.__dict__,
                                       ttl=self._calculate_remaining_ttl(session_entry))
            
            # Send notification
            await self._send_notification("session_extended", session_entry)
            
            self.logger.debug(f"Extended session {session_id} by {additional_seconds} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Error extending session {session_id}: {e}")
            return False
    
    async def revoke_session(self, session_id: str, reason: str = "manual") -> bool:
        """Revoke session"""
        try:
            session_entry = await self.get_session(session_id)
            if not session_entry:
                return False
            
            # Update status
            session_entry.status = SessionStatus.REVOKED
            session_entry.metadata["revocation_reason"] = reason
            session_entry.metadata["revoked_at"] = datetime.now().isoformat()
            
            # Remove from cache
            session_key = self._make_session_key(session_id)
            await self.cache_manager.delete(session_key)
            
            # Update indexes
            await self._update_indexes(session_entry, action="revoke")
            
            # Update statistics
            self.stats["revoked_sessions"] += 1
            if self.stats["active_sessions"] > 0:
                self.stats["active_sessions"] -= 1
            
            # Send notification
            await self._send_notification("session_revoked", session_entry)
            
            self.logger.debug(f"Revoked session {session_id}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error revoking session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SessionEntry]:
        """Get all active sessions for a user"""
        try:
            user_index_key = self._make_user_index_key(user_id)
            session_ids = await self.cache_manager.get(user_index_key)
            
            if not session_ids:
                return []
            
            sessions = []
            for session_id in session_ids:
                session_entry = await self.get_session(session_id)
                if session_entry and session_entry.status == SessionStatus.ACTIVE:
                    sessions.append(session_entry)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    async def get_sessions_by_type(self, session_type: SessionType) -> List[SessionEntry]:
        """Get all active sessions of a specific type"""
        try:
            type_index_key = self._make_type_index_key(session_type)
            session_ids = await self.cache_manager.get(type_index_key)
            
            if not session_ids:
                return []
            
            sessions = []
            for session_id in session_ids:
                session_entry = await self.get_session(session_id)
                if session_entry and session_entry.status == SessionStatus.ACTIVE:
                    sessions.append(session_entry)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting sessions by type {session_type}: {e}")
            return []
    
    async def revoke_user_sessions(self, user_id: str, reason: str = "user_request") -> int:
        """Revoke all sessions for a user"""
        try:
            user_sessions = await self.get_user_sessions(user_id)
            revoked_count = 0
            
            for session in user_sessions:
                if await self.revoke_session(session.session_id, reason):
                    revoked_count += 1
            
            self.logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
            return revoked_count
            
        except Exception as e:
            self.logger.error(f"Error revoking user sessions for {user_id}: {e}")
            return 0
    
    async def _cleanup_loop(self):
        """Background cleanup of expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired_sessions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            cleaned_count = 0
            
            # Get all session types
            for session_type in SessionType:
                sessions = await self.get_sessions_by_type(session_type)
                
                for session in sessions:
                    if (session.expires_at and session.expires_at < datetime.now() or
                        session.status != SessionStatus.ACTIVE):
                        
                        await self.revoke_session(session.session_id, "expired")
                        cleaned_count += 1
            
            self.stats["cleanup_runs"] += 1
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")
    
    async def _enforce_user_session_limit(self, user_id: str):
        """Enforce maximum sessions per user"""
        user_sessions = await self.get_user_sessions(user_id)
        
        if len(user_sessions) >= self.config.max_sessions_per_user:
            # Sort by last accessed time and revoke oldest
            user_sessions.sort(key=lambda s: s.last_accessed)
            
            sessions_to_revoke = len(user_sessions) - self.config.max_sessions_per_user + 1
            for i in range(sessions_to_revoke):
                await self.revoke_session(user_sessions[i].session_id, "session_limit_exceeded")
    
    async def _update_indexes(self, session_entry: SessionEntry, action: str):
        """Update session indexes"""
        try:
            # Update user index
            if session_entry.user_id:
                user_index_key = self._make_user_index_key(session_entry.user_id)
                user_sessions = await self.cache_manager.get(user_index_key) or []
                
                if action == "create":
                    user_sessions.append(session_entry.session_id)
                elif action == "revoke":
                    user_sessions = [sid for sid in user_sessions if sid != session_entry.session_id]
                
                await self.cache_manager.set(user_index_key, user_sessions, ttl=86400)  # 24 hours
            
            # Update type index
            type_index_key = self._make_type_index_key(session_entry.session_type)
            type_sessions = await self.cache_manager.get(type_index_key) or []
            
            if action == "create":
                type_sessions.append(session_entry.session_id)
            elif action == "revoke":
                type_sessions = [sid for sid in type_sessions if sid != session_entry.session_id]
            
            await self.cache_manager.set(type_index_key, type_sessions, ttl=86400)  # 24 hours
            
        except Exception as e:
            self.logger.error(f"Error updating indexes: {e}")
    
    async def _send_notification(self, event_type: str, session_entry: SessionEntry):
        """Send session event notification"""
        try:
            if self.config.enable_notifications and self.event_bus:
                event = {
                    "type": event_type,
                    "session_id": session_entry.session_id,
                    "session_type": session_entry.session_type.value,
                    "user_id": session_entry.user_id,
                    "timestamp": datetime.now().isoformat(),
                    "ip_address": session_entry.ip_address
                }
                
                await self.event_bus.publish(f"session.{event_type}", event)
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    async def _load_session_stats(self):
        """Load existing session statistics"""
        try:
            # Count active sessions by type
            active_count = 0
            for session_type in SessionType:
                sessions = await self.get_sessions_by_type(session_type)
                active_count += len(sessions)
            
            self.stats["active_sessions"] = active_count
            
        except Exception as e:
            self.logger.error(f"Error loading session stats: {e}")
    
    def _make_session_key(self, session_id: str) -> str:
        """Create session cache key"""
        return f"{self.session_prefix}{session_id}"
    
    def _make_user_index_key(self, user_id: str) -> str:
        """Create user session index key"""
        return f"{self.user_index_prefix}{user_id}"
    
    def _make_type_index_key(self, session_type: SessionType) -> str:
        """Create type session index key"""
        return f"{self.type_index_prefix}{session_type.value}"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    def _calculate_remaining_ttl(self, session_entry: SessionEntry) -> int:
        """Calculate remaining TTL for session"""
        if not session_entry.expires_at:
            return self.config.default_ttl
        
        remaining = (session_entry.expires_at - datetime.now()).total_seconds()
        return max(int(remaining), 60)  # Minimum 1 minute
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            **self.stats,
            "config": {
                "default_ttl": self.config.default_ttl,
                "max_sessions_per_user": self.config.max_sessions_per_user,
                "cleanup_interval": self.config.cleanup_interval
            }
        }
    
    async def close(self):
        """Close session cache manager"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

# Export main components
__all__ = [
    'SessionCacheManager',
    'SessionEntry',
    'SessionConfig',
    'SessionType',
    'SessionStatus'
]