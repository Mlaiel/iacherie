#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Session Cache - User and Crawler Session Management
==================================================

Advanced session caching for users, crawlers, and temporary data
with intelligent session lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class SessionType(Enum):
    """Session type enumeration."""
    USER = "user"
    CRAWLER = "crawler"
    API = "api"
    ADMIN = "admin"
    SYSTEM = "system"
    TEMPORARY = "temporary"

@dataclass
class SessionData:
    """Session data structure."""
    session_id: str
    session_type: SessionType
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def extend_session(self, extension_seconds: int) -> None:
        """Extend session expiration."""
        if self.expires_at:
            self.expires_at += timedelta(seconds=extension_seconds)
        else:
            self.expires_at = datetime.now() + timedelta(seconds=extension_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type.value,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "data": self.data,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary."""
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        return cls(
            session_id=data['session_id'],
            session_type=SessionType(data['session_type']),
            user_id=data.get('user_id'),
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            expires_at=expires_at,
            data=data.get('data', {}),
            metadata=data.get('metadata', {}),
            access_count=data.get('access_count', 0),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent')
        )

class SessionCache:
    """
    Advanced session cache implementation.
    
    Features:
    - Multiple session types
    - Automatic expiration
    - Session extension
    - User-based indexing
    - Activity tracking
    - Security monitoring
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None,
                 default_ttl: int = 3600, max_sessions_per_user: int = 10):
        """
        Initialize session cache.
        
        Args:
            cache_manager: Cache manager instance
            default_ttl: Default session TTL in seconds
            max_sessions_per_user: Maximum sessions per user
        """
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl
        self.max_sessions_per_user = max_sessions_per_user
        self.logger = logging.getLogger(f"{__name__}.SessionCache")
        
        # Session configuration by type
        self.ttl_by_type = {
            SessionType.USER: 7200,      # 2 hours
            SessionType.CRAWLER: 14400,  # 4 hours
            SessionType.API: 3600,       # 1 hour
            SessionType.ADMIN: 1800,     # 30 minutes
            SessionType.SYSTEM: 86400,   # 24 hours
            SessionType.TEMPORARY: 300   # 5 minutes
        }
        
        # Key prefixes
        self.session_key_prefix = "session:"
        self.user_index_prefix = "user_sessions:"
        self.type_index_prefix = "type_sessions:"
        
        # Metrics
        self.session_count = 0
        self.active_users = set()
        
        self.logger.info("Session cache initialized")
    
    async def _get_cache_manager(self) -> CacheManager:
        """Get cache manager instance."""
        if self.cache_manager is None:
            from .cache_manager import get_cache_manager
            self.cache_manager = await get_cache_manager()
        return self.cache_manager
    
    def _make_session_key(self, session_id: str) -> str:
        """Create session cache key."""
        return f"{self.session_key_prefix}{session_id}"
    
    def _make_user_index_key(self, user_id: str) -> str:
        """Create user session index key."""
        return f"{self.user_index_prefix}{user_id}"
    
    def _make_type_index_key(self, session_type: SessionType) -> str:
        """Create type session index key."""
        return f"{self.type_index_prefix}{session_type.value}"
    
    async def create_session(self, session_type: SessionType,
                           user_id: Optional[str] = None,
                           ttl: Optional[int] = None,
                           data: Optional[Dict[str, Any]] = None,
                           **kwargs) -> str:
        """
        Create new session.
        
        Args:
            session_type: Type of session
            user_id: User ID for user sessions
            ttl: Session TTL override
            data: Initial session data
            **kwargs: Additional session metadata
            
        Returns:
            Session ID
        """
        try:
            cache_manager = await self._get_cache_manager()
            
            # Generate session ID
            session_id = generate_uuid()
            
            # Determine TTL
            if ttl is None:
                ttl = self.ttl_by_type.get(session_type, self.default_ttl)
            
            # Create session data
            session_data = SessionData(
                session_id=session_id,
                session_type=session_type,
                user_id=user_id,
                expires_at=datetime.now() + timedelta(seconds=ttl),
                data=data or {},
                metadata=kwargs
            )
            
            # Store session
            session_key = self._make_session_key(session_id)
            success = await cache_manager.set(session_key, session_data.to_dict(), ttl)
            
            if not success:
                self.logger.error(f"Failed to store session {session_id}")
                return None
            
            # Update indexes
            await self._add_to_indexes(session_data)
            
            # Cleanup old sessions if user has too many
            if user_id:
                await self._cleanup_user_sessions(user_id)
            
            self.session_count += 1
            if user_id:
                self.active_users.add(user_id)
            
            self.logger.debug(f"Created {session_type.value} session {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found/expired
        """
        try:
            cache_manager = await self._get_cache_manager()
            session_key = self._make_session_key(session_id)
            
            session_dict = await cache_manager.get(session_key)
            if not session_dict:
                return None
            
            session_data = SessionData.from_dict(session_dict)
            
            # Check expiration
            if session_data.is_expired():
                await self.delete_session(session_id)
                return None
            
            # Update access info
            session_data.last_accessed = datetime.now()
            session_data.access_count += 1
            
            # Save updated session
            await cache_manager.set(session_key, session_data.to_dict(), 
                                  self.ttl_by_type.get(session_data.session_type, self.default_ttl))
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, 
                           data: Optional[Dict[str, Any]] = None,
                           metadata: Optional[Dict[str, Any]] = None,
                           extend_ttl: Optional[int] = None) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            data: Data to update (merged with existing)
            metadata: Metadata to update
            extend_ttl: Extend TTL by seconds
            
        Returns:
            True if successful
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                return False
            
            # Update data
            if data:
                session_data.data.update(data)
            
            if metadata:
                session_data.metadata.update(metadata)
            
            # Extend TTL if requested
            if extend_ttl:
                session_data.extend_session(extend_ttl)
            
            # Save updated session
            cache_manager = await self._get_cache_manager()
            session_key = self._make_session_key(session_id)
            
            ttl = self.ttl_by_type.get(session_data.session_type, self.default_ttl)
            if session_data.expires_at:
                remaining_ttl = int((session_data.expires_at - datetime.now()).total_seconds())
                ttl = max(remaining_ttl, 60)  # At least 1 minute
            
            return await cache_manager.set(session_key, session_data.to_dict(), ttl)
            
        except Exception as e:
            self.logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        try:
            # Get session data for cleanup
            session_data = await self.get_session(session_id)
            
            cache_manager = await self._get_cache_manager()
            session_key = self._make_session_key(session_id)
            
            success = await cache_manager.delete(session_key)
            
            # Remove from indexes
            if session_data:
                await self._remove_from_indexes(session_data)
            
            if success:
                self.session_count = max(0, self.session_count - 1)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all sessions for user."""
        try:
            cache_manager = await self._get_cache_manager()
            user_index_key = self._make_user_index_key(user_id)
            
            session_ids = await cache_manager.get(user_index_key) or []
            sessions = []
            
            for session_id in session_ids:
                session_data = await self.get_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for user."""
        try:
            sessions = await self.get_user_sessions(user_id)
            deleted_count = 0
            
            for session in sessions:
                if await self.delete_session(session.session_id):
                    deleted_count += 1
            
            # Clear user index
            cache_manager = await self._get_cache_manager()
            user_index_key = self._make_user_index_key(user_id)
            await cache_manager.delete(user_index_key)
            
            if user_id in self.active_users:
                self.active_users.remove(user_id)
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error deleting user sessions for {user_id}: {e}")
            return 0
    
    async def get_sessions_by_type(self, session_type: SessionType) -> List[SessionData]:
        """Get all sessions of specific type."""
        try:
            cache_manager = await self._get_cache_manager()
            type_index_key = self._make_type_index_key(session_type)
            
            session_ids = await cache_manager.get(type_index_key) or []
            sessions = []
            
            for session_id in session_ids:
                session_data = await self.get_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting sessions by type {session_type}: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            cleaned_count = 0
            
            # Check all session types
            for session_type in SessionType:
                sessions = await self.get_sessions_by_type(session_type)
                
                for session in sessions:
                    if session.is_expired():
                        if await self.delete_session(session.session_id):
                            cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    async def _add_to_indexes(self, session_data: SessionData) -> None:
        """Add session to indexes."""
        try:
            cache_manager = await self._get_cache_manager()
            
            # User index
            if session_data.user_id:
                user_index_key = self._make_user_index_key(session_data.user_id)
                user_sessions = await cache_manager.get(user_index_key) or []
                if session_data.session_id not in user_sessions:
                    user_sessions.append(session_data.session_id)
                    await cache_manager.set(user_index_key, user_sessions, 86400)  # 24 hours
            
            # Type index
            type_index_key = self._make_type_index_key(session_data.session_type)
            type_sessions = await cache_manager.get(type_index_key) or []
            if session_data.session_id not in type_sessions:
                type_sessions.append(session_data.session_id)
                # Keep only recent sessions
                if len(type_sessions) > 1000:
                    type_sessions = type_sessions[-1000:]
                await cache_manager.set(type_index_key, type_sessions, 86400)
            
        except Exception as e:
            self.logger.error(f"Error adding to indexes: {e}")
    
    async def _remove_from_indexes(self, session_data: SessionData) -> None:
        """Remove session from indexes."""
        try:
            cache_manager = await self._get_cache_manager()
            
            # User index
            if session_data.user_id:
                user_index_key = self._make_user_index_key(session_data.user_id)
                user_sessions = await cache_manager.get(user_index_key) or []
                if session_data.session_id in user_sessions:
                    user_sessions.remove(session_data.session_id)
                    if user_sessions:
                        await cache_manager.set(user_index_key, user_sessions, 86400)
                    else:
                        await cache_manager.delete(user_index_key)
            
            # Type index
            type_index_key = self._make_type_index_key(session_data.session_type)
            type_sessions = await cache_manager.get(type_index_key) or []
            if session_data.session_id in type_sessions:
                type_sessions.remove(session_data.session_id)
                await cache_manager.set(type_index_key, type_sessions, 86400)
            
        except Exception as e:
            self.logger.error(f"Error removing from indexes: {e}")
    
    async def _cleanup_user_sessions(self, user_id: str) -> None:
        """Cleanup old sessions if user has too many."""
        try:
            sessions = await self.get_user_sessions(user_id)
            
            if len(sessions) > self.max_sessions_per_user:
                # Sort by last accessed (oldest first)
                sessions.sort(key=lambda s: s.last_accessed)
                
                # Delete oldest sessions
                sessions_to_delete = sessions[:-self.max_sessions_per_user]
                for session in sessions_to_delete:
                    await self.delete_session(session.session_id)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up user sessions for {user_id}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get session cache statistics."""
        try:
            stats = {
                "total_sessions": self.session_count,
                "active_users": len(self.active_users),
                "sessions_by_type": {}
            }
            
            # Count sessions by type
            for session_type in SessionType:
                sessions = await self.get_sessions_by_type(session_type)
                stats["sessions_by_type"][session_type.value] = len(sessions)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting session stats: {e}")
            return {}

class UserCache(SessionCache):
    """
    Specialized cache for user sessions and data.
    
    Enhanced with user-specific features and preferences.
    """
    
    def __init__(self, **kwargs):
        """Initialize user cache."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.UserCache")
        
        # User-specific settings
        self.default_ttl = 7200  # 2 hours for user sessions

class CrawlerSessionCache(SessionCache):
    """
    Specialized cache for crawler sessions and state.
    
    Enhanced with crawler-specific features and monitoring.
    """
    
    def __init__(self, **kwargs):
        """Initialize crawler session cache."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.CrawlerSessionCache")
        
        # Crawler-specific settings
        self.default_ttl = 14400  # 4 hours for crawler sessions
        self.max_sessions_per_user = 50  # Crawlers may need more sessions
