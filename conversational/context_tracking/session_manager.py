"""Session Manager - IA Influencer Agent

Enterprise session management for multi-platform content creators with
intelligent session tracking, state persistence, and cross-platform continuity.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

from ...core.exceptions import SessionManagerError
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...utils.cache import CacheManager
from ...utils.validation import validate_required_fields


class SessionStatus(Enum):
    """
Session status types"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class SessionType(Enum):
    """Session types for different interaction modes"""

    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"
    BACKGROUND = "background"


class PlatformType(Enum):
    """Supported platforms"""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    TWITCH = "twitch"
    WEB_APP = "web_app"


@dataclass
class SessionActivity:
    """Individual session activity record"""
    activity_id: str
    session_id: str
    activity_type: str
    timestamp: datetime
    details: Dict[str, Any]
    platform: Optional[PlatformType] = None
    duration: Optional[float] = None  # seconds
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary representation"""
        return {
            "activity_id": self.activity_id,
            "session_id": self.session_id,
            "activity_type": self.activity_type,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "platform": self.platform.value if self.platform else None,
            "duration": self.duration,
            "success": self.success,
            "error_message": self.error_message
        }


@dataclass
class SessionMetrics:
    """Session performance metrics"""
    total_activities: int = 0
    successful_activities: int = 0
    failed_activities: int = 0
    total_duration: float = 0.0  # seconds
    platforms_used: Set[PlatformType] = field(default_factory=set)
    activity_types: Dict[str, int] = field(default_factory=dict)
    average_response_time: float = 0.0
    peak_activity_time: Optional[datetime] = None
    engagement_score: float = 0.0
    
    def calculate_success_rate(self) -> float:
        """
Calculate success rate percentage"""
        if self.total_activities == 0:
            return 0.0
        return (self.successful_activities / self.total_activities) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary representation"""
        return {
            "total_activities": self.total_activities,
            "successful_activities": self.successful_activities,
            "failed_activities": self.failed_activities,
            "success_rate": self.calculate_success_rate(),
            "total_duration": self.total_duration,
            "platforms_used": [p.value for p in self.platforms_used],
            "activity_types": self.activity_types,
            "average_response_time": self.average_response_time,
            "peak_activity_time": self.peak_activity_time.isoformat() if self.peak_activity_time else None,
            "engagement_score": self.engagement_score
        }


@dataclass
class UserSession:
    """Comprehensive user session with state management"""
    session_id: str
    user_id: str
    session_type: SessionType
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    
    # Session context
    platform: Optional[PlatformType] = None
    device_info: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    
    # State management
    session_state: Dict[str, Any] = field(default_factory=dict)
    persistent_data: Dict[str, Any] = field(default_factory=dict)
    temporary_data: Dict[str, Any] = field(default_factory=dict)
    
    # Activity tracking
    activities: List[SessionActivity] = field(default_factory=list)
    metrics: SessionMetrics = field(default_factory=SessionMetrics)
    
    # Security and preferences
    security_context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """
Check if session is currently active"""
        return (
            self.status == SessionStatus.ACTIVE and
            datetime.utcnow() < self.expires_at
        )
    
    def is_expired(self) -> bool:
        """
Check if session has expired"""
        return datetime.utcnow() >= self.expires_at
    
    def update_activity(self):
        """
Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        if self.status == SessionStatus.INACTIVE:
            self.status = SessionStatus.ACTIVE
    
    def add_activity(self, activity: SessionActivity):
        """
Add activity to session"""
        self.activities.append(activity)
        self.update_activity()
        
        # Update metrics
        self.metrics.total_activities += 1
        if activity.success:
            self.metrics.successful_activities += 1
        else:
            self.metrics.failed_activities += 1
        
        if activity.platform:
            self.metrics.platforms_used.add(activity.platform)
        
        activity_type = activity.activity_type
        self.metrics.activity_types[activity_type] = self.metrics.activity_types.get(activity_type, 0) + 1
        
        if activity.duration:
            self.metrics.total_duration += activity.duration
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary representation"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_type": self.session_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "platform": self.platform.value if self.platform else None,
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "location": self.location,
            "session_state": self.session_state,
            "persistent_data": self.persistent_data,
            "activities_count": len(self.activities),
            "metrics": self.metrics.to_dict(),
            "security_context": self.security_context,
            "preferences": self.preferences
        }


class SessionManager:
    """
    Enterprise session manager providing intelligent session tracking,
    state persistence, and cross-platform continuity for content creators.
    
    Features:
    - Multi-platform session management
    - Intelligent session lifecycle management
    - State persistence and restoration
    - Activity tracking and analytics
    - Security-aware session handling
    - Cross-device session continuity
    """
    
    def __init__(
        self,
        cache_manager: CacheManager,
        security_manager: SecurityManager,
        metrics_collector: MetricsCollector,
        default_session_ttl: int = 86400,  # 24 hours
        max_sessions_per_user: int = 10,
        activity_timeout: int = 3600,  # 1 hour
        cleanup_interval: int = 300  # 5 minutes
    ):
        self.cache_manager = cache_manager
        self.security_manager = security_manager
        self.metrics_collector = metrics_collector
        self.default_session_ttl = default_session_ttl
        self.max_sessions_per_user = max_sessions_per_user
        self.activity_timeout = activity_timeout
        self.cleanup_interval = cleanup_interval
        
        # Session storage
        self.active_sessions: Dict[str, UserSession] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("SessionManager initialized")
    
    async def start(self):
        """Start the session manager"""
        try:
            # Load existing sessions
            await self._load_sessions()
            
            # Start background cleanup
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            
            self.logger.info("SessionManager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start SessionManager: {e}")
            raise SessionManagerError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the session manager"""
        try:
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Save active sessions
            await self._save_sessions()
            
            self.logger.info("SessionManager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping SessionManager: {e}")
    
    async def create_session(
        self,
        user_id: str,
        session_type: SessionType,
        platform: Optional[PlatformType] = None,
        device_info: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        security_context: Optional[Dict[str, Any]] = None
    ) -> UserSession:
        """
        Create new user session
        
        Args:
            user_id: User identifier
            session_type: Type of session
            platform: Platform for the session
            device_info: Device information
            ttl: Session time-to-live in seconds
            initial_state: Initial session state
            security_context: Security context
            
        Returns:
            UserSession: Created session
        """
        try:
            validate_required_fields({"user_id": user_id, "session_type": session_type})
            
            # Security validation
            if not await self.security_manager.validate_session_creation(user_id):
                raise SecurityManagerError("Session creation not authorized")
            
            # Check session limits
            await self._enforce_session_limits(user_id)
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Calculate expiration
            session_ttl = ttl or self.default_session_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=session_ttl)
            
            # Create session
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                session_type=session_type,
                status=SessionStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                expires_at=expires_at,
                platform=platform,
                device_info=device_info or {},
                session_state=initial_state or {},
                security_context=security_context or {}
            )
            
            # Store session
            self.active_sessions[session_id] = session
            self.user_sessions[user_id].add(session_id)
            
            # Cache session for quick access
            await self.cache_manager.set(
                f"session:{session_id}",
                session.to_dict(),
                ttl=session_ttl
            )
            
            # Collect metrics
            await self.metrics_collector.increment(
                "sessions.created",
                tags={
                    "type": session_type.value,
                    "platform": platform.value if platform else "unknown"
                }
            )
            
            self.logger.info(f"Session created: {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            await self.metrics_collector.increment("sessions.creation_errors")
            raise SessionManagerError(f"Failed to create session: {e}")
    
    async def get_session(
        self,
        session_id: str,
        validate_active: bool = True
    ) -> Optional[UserSession]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
            validate_active: Whether to validate session is active
            
        Returns:
            UserSession or None if not found
        """
        try:
            # Check in-memory storage first
            session = self.active_sessions.get(session_id)
            
            if not session:
                # Try to load from cache
                session_data = await self.cache_manager.get(f"session:{session_id}")
                if session_data:
                    session = self._session_from_dict(session_data)
                    self.active_sessions[session_id] = session
                    self.user_sessions[session.user_id].add(session_id)
            
            if not session:
                await self.metrics_collector.increment("sessions.not_found")
                return None
            
            # Validate session if requested
            if validate_active:
                if not session.is_active():
                    if session.is_expired():
                        await self._expire_session(session_id)
                    return None
            
            await self.metrics_collector.increment("sessions.retrieved")
            return session
            
        except Exception as e:
            self.logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session_activity(
        self,
        session_id: str,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None,
        platform: Optional[PlatformType] = None,
        duration: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update session with new activity
        
        Args:
            session_id: Session identifier
            activity_type: Type of activity
            details: Activity details
            platform: Platform for the activity
            duration: Activity duration in seconds
            success: Whether activity was successful
            error_message: Error message if failed
            
        Returns:
            bool: Success status
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Create activity record
            activity = SessionActivity(
                activity_id=str(uuid.uuid4()),
                session_id=session_id,
                activity_type=activity_type,
                timestamp=datetime.utcnow(),
                details=details or {},
                platform=platform,
                duration=duration,
                success=success,
                error_message=error_message
            )
            
            # Add to session
            session.add_activity(activity)
            
            # Update session cache
            await self._update_session_cache(session)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "sessions.activities",
                tags={
                    "type": activity_type,
                    "success": str(success).lower(),
                    "platform": platform.value if platform else "unknown"
                }
            )
            
            self.logger.debug(f"Activity added to session {session_id}: {activity_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating session activity: {e}")
            return False
    
    async def set_session_state(
        self,
        session_id: str,
        key: str,
        value: Any,
        persistent: bool = False
    ) -> bool:
        """
        Set session state value
        
        Args:
            session_id: Session identifier
            key: State key
            value: State value
            persistent: Whether to persist across session restarts
            
        Returns:
            bool: Success status
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            if persistent:
                session.persistent_data[key] = value
            else:
                session.session_state[key] = value
            
            session.update_activity()
            
            # Update session cache
            await self._update_session_cache(session)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting session state: {e}")
            return False
    
    async def get_session_state(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get session state value
        
        Args:
            session_id: Session identifier
            key: State key
            default: Default value if not found
            
        Returns:
            State value or default
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return default
            
            # Check persistent data first, then session state
            value = session.persistent_data.get(key)
            if value is None:
                value = session.session_state.get(key, default)
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting session state: {e}")
            return default
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True
    ) -> List[UserSession]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            active_only: Whether to return only active sessions
            
        Returns:
            List of user sessions
        """
        try:
            session_ids = self.user_sessions.get(user_id, set())
            sessions = []
            
            for session_id in session_ids:
                session = await self.get_session(session_id, validate_active=active_only)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def terminate_session(
        self,
        session_id: str,
        reason: str = "user_request"
    ) -> bool:
        """
        Terminate session
        
        Args:
            session_id: Session identifier
            reason: Termination reason
            
        Returns:
            bool: Success status
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Update session status
            session.status = SessionStatus.TERMINATED
            
            # Add termination activity
            await self.update_session_activity(
                session_id,
                "session_terminated",
                {"reason": reason}
            )
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            if session.user_id in self.user_sessions:
                self.user_sessions[session.user_id].discard(session_id)
            
            # Remove from cache
            await self.cache_manager.delete(f"session:{session_id}")
            
            # Archive session if important
            if session.metrics.total_activities > 10:
                await self._archive_session(session)
            
            await self.metrics_collector.increment("sessions.terminated")
            
            self.logger.info(f"Session terminated: {session_id} (reason: {reason})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error terminating session {session_id}: {e}")
            return False
    
    async def extend_session(
        self,
        session_id: str,
        extension_seconds: int
    ) -> bool:
        """
        Extend session expiration time
        
        Args:
            session_id: Session identifier
            extension_seconds: Seconds to extend
            
        Returns:
            bool: Success status
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Extend expiration
            session.expires_at += timedelta(seconds=extension_seconds)
            session.update_activity()
            
            # Update cache with new TTL
            remaining_ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            await self.cache_manager.set(
                f"session:{session_id}",
                session.to_dict(),
                ttl=remaining_ttl
            )
            
            await self.metrics_collector.increment("sessions.extended")
            
            self.logger.debug(f"Session extended: {session_id} by {extension_seconds}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error extending session {session_id}: {e}")
            return False
    
    async def get_session_analytics(
        self,
        user_id: Optional[str] = None,
        platform: Optional[PlatformType] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get session analytics
        
        Args:
            user_id: Filter by specific user
            platform: Filter by specific platform
            time_range: Filter by time range (start, end)
            
        Returns:
            Dict containing analytics data
        """
        try:
            sessions_to_analyze = []
            
            # Collect sessions based on filters
            if user_id:
                sessions_to_analyze = await self.get_user_sessions(user_id, active_only=False)
            else:
                # Get all sessions
                for session in self.active_sessions.values():
                    sessions_to_analyze.append(session)
            
            # Apply additional filters
            if platform:
                sessions_to_analyze = [s for s in sessions_to_analyze if s.platform == platform]
            
            if time_range:
                start_time, end_time = time_range
                sessions_to_analyze = [
                    s for s in sessions_to_analyze
                    if start_time <= s.created_at <= end_time
                ]
            
            if not sessions_to_analyze:
                return {"total_sessions": 0}
            
            # Calculate analytics
            total_sessions = len(sessions_to_analyze)
            active_sessions = sum(1 for s in sessions_to_analyze if s.is_active())
            
            # Platform distribution
            platform_dist = defaultdict(int)
            for session in sessions_to_analyze:
                if session.platform:
                    platform_dist[session.platform.value] += 1
            
            # Session type distribution
            type_dist = defaultdict(int)
            for session in sessions_to_analyze:
                type_dist[session.session_type.value] += 1
            
            # Activity statistics
            total_activities = sum(s.metrics.total_activities for s in sessions_to_analyze)
            successful_activities = sum(s.metrics.successful_activities for s in sessions_to_analyze)
            
            # Duration statistics
            durations = [s.metrics.total_duration for s in sessions_to_analyze if s.metrics.total_duration > 0]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Engagement statistics
            engagement_scores = [s.metrics.engagement_score for s in sessions_to_analyze]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "platform_distribution": dict(platform_dist),
                "session_type_distribution": dict(type_dist),
                "activity_statistics": {
                    "total_activities": total_activities,
                    "successful_activities": successful_activities,
                    "success_rate": (successful_activities / total_activities * 100) if total_activities > 0 else 0
                },
                "duration_statistics": {
                    "average_duration": avg_duration,
                    "total_sessions_with_duration": len(durations)
                },
                "engagement_statistics": {
                    "average_engagement": avg_engagement,
                    "high_engagement_sessions": sum(1 for score in engagement_scores if score > 0.7)
                },
                "time_range": {
                    "start": time_range[0].isoformat() if time_range else None,
                    "end": time_range[1].isoformat() if time_range else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating session analytics: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""
        user_session_ids = self.user_sessions.get(user_id, set())
        
        if len(user_session_ids) >= self.max_sessions_per_user:
            # Terminate oldest sessions
            sessions_to_check = []
            for session_id in user_session_ids:
                session = self.active_sessions.get(session_id)
                if session:
                    sessions_to_check.append(session)
            
            # Sort by last activity (oldest first)
            sessions_to_check.sort(key=lambda s: s.last_activity)
            
            # Terminate oldest sessions
            sessions_to_terminate = len(sessions_to_check) - self.max_sessions_per_user + 1
            for session in sessions_to_check[:sessions_to_terminate]:
                await self.terminate_session(session.session_id, "session_limit_exceeded")
    
    async def _update_session_cache(self, session: UserSession):
        """Update session in cache"""
        try:
            remaining_ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            if remaining_ttl > 0:
                await self.cache_manager.set(
                    f"session:{session.session_id}",
                    session.to_dict(),
                    ttl=remaining_ttl
                )
        except Exception as e:
            self.logger.error(f"Error updating session cache: {e}")
    
    async def _expire_session(self, session_id: str):
        """Mark session as expired"""
        try:
            session = self.active_sessions.get(session_id)
            if session:
                session.status = SessionStatus.EXPIRED
                
                # Add expiration activity
                await self.update_session_activity(
                    session_id,
                    "session_expired",
                    {"expired_at": datetime.utcnow().isoformat()}
                )
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                if session.user_id in self.user_sessions:
                    self.user_sessions[session.user_id].discard(session_id)
                
                # Archive if significant activity
                if session.metrics.total_activities > 5:
                    await self._archive_session(session)
                
                await self.metrics_collector.increment("sessions.expired")
                
        except Exception as e:
            self.logger.error(f"Error expiring session {session_id}: {e}")
    
    async def _archive_session(self, session: UserSession):
        """Archive session for historical analysis"""
        try:
            archive_key = f"session_archive:{session.user_id}:{session.session_id}"
            await self.cache_manager.set(
                archive_key,
                session.to_dict(),
                ttl=86400 * 30  # Keep archives for 30 days
            )
        except Exception as e:
            self.logger.error(f"Error archiving session: {e}")
    
    async def _background_cleanup(self):
        """Background task for session cleanup"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean up expired sessions
                expired_sessions = []
                for session_id, session in self.active_sessions.items():
                    if session.is_expired():
                        expired_sessions.append(session_id)
                    elif (datetime.utcnow() - session.last_activity).total_seconds() > self.activity_timeout:
                        # Mark inactive sessions
                        session.status = SessionStatus.INACTIVE
                
                # Expire sessions
                for session_id in expired_sessions:
                    await self._expire_session(session_id)
                
                # Save sessions periodically
                await self._save_sessions()
                
                await self.metrics_collector.increment("sessions.cleanup_runs")
                
                if expired_sessions:
                    self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            # Load from cache
            session_data = await self.cache_manager.get("active_sessions")
            if session_data:
                for session_id, session_dict in session_data.items():
                    session = self._session_from_dict(session_dict)
                    if not session.is_expired():
                        self.active_sessions[session_id] = session
                        self.user_sessions[session.user_id].add(session_id)
                        
        except Exception as e:
            self.logger.error(f"Error loading sessions: {e}")
    
    async def _save_sessions(self):
        """Save sessions to persistent storage"""
        try:
            # Save only important active sessions
            sessions_to_save = {}
            for session_id, session in self.active_sessions.items():
                if session.metrics.total_activities > 0:  # Only save sessions with activity
                    sessions_to_save[session_id] = session.to_dict()
            
            await self.cache_manager.set(
                "active_sessions",
                sessions_to_save,
                ttl=86400  # 24 hours
            )
            
        except Exception as e:
            self.logger.error(f"Error saving sessions: {e}")
    
    def _session_from_dict(self, data: Dict[str, Any]) -> UserSession:
        """Reconstruct session from dictionary"""
        # Reconstruct activities
        activities = []
        # Note: Activities are not stored in dict to reduce size
        # They would be loaded separately if needed
        
        # Reconstruct metrics
        metrics_data = data.get("metrics", {})
        metrics = SessionMetrics(
            total_activities=metrics_data.get("total_activities", 0),
            successful_activities=metrics_data.get("successful_activities", 0),
            failed_activities=metrics_data.get("failed_activities", 0),
            total_duration=metrics_data.get("total_duration", 0.0),
            platforms_used=set(PlatformType(p) for p in metrics_data.get("platforms_used", [])),
            activity_types=metrics_data.get("activity_types", {}),
            average_response_time=metrics_data.get("average_response_time", 0.0),
            peak_activity_time=datetime.fromisoformat(metrics_data["peak_activity_time"]) if metrics_data.get("peak_activity_time") else None,
            engagement_score=metrics_data.get("engagement_score", 0.0)
        )
        
        session = UserSession(
            session_id=data["session_id"],
            user_id=data["user_id"],
            session_type=SessionType(data["session_type"]),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            platform=PlatformType(data["platform"]) if data.get("platform") else None,
            device_info=data.get("device_info", {}),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            location=data.get("location"),
            session_state=data.get("session_state", {}),
            persistent_data=data.get("persistent_data", {}),
            activities=activities,
            metrics=metrics,
            security_context=data.get("security_context", {}),
            preferences=data.get("preferences", {})
        )
        
        return session
