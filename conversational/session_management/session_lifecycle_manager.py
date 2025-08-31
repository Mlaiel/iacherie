"""Session Lifecycle Manager - IA Influencer Agent

Enterprise-grade session lifecycle management for conversational AI interactions
with complete session creation, state transitions, and termination handling
for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, SessionState, SessionType
from ...models.user import UserModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher

logger = get_logger(__name__)


class SessionTransition(Enum):
    """Session state transition types"""    CREATED = "created"
    ACTIVATED = "activated"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    FORCE_CLOSED = "force_closed"


@dataclass
class SessionConfig:
    """Session configuration parameters"""    max_duration: timedelta = field(default_factory=lambda: timedelta(hours=24))
    idle_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    max_concurrent_sessions: int = 10
    auto_save_interval: int = 60  # seconds
    encryption_enabled: bool = True
    cross_platform_sync: bool = True
    conversation_persistence: bool = True
    analytics_enabled: bool = True


class SessionMetadata(BaseModel):
    """Session metadata structure"""    user_id: str
    session_type: SessionType
    platform: str
    device_info: Dict[str, Any] = Field(default_factory=dict)
    conversation_context: Dict[str, Any] = Field(default_factory=dict)
    business_context: Dict[str, Any] = Field(default_factory=dict)
    content_protection_enabled: bool = True
    monetization_active: bool = False
    collaboration_mode: bool = False
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Invalid user_id format")
        return v


class SessionCreationHandler:
    """Handles session creation with advanced configuration"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.encryption_manager = EncryptionManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_session(
        self,
        metadata: SessionMetadata,
        config: Optional[SessionConfig] = None
    ) -> str:
        """Create new conversation session with full lifecycle setup"""        
        config = config or SessionConfig()
        session_id = str(uuid4())
        
        try:
            # Validate user session limits
            await self._validate_session_limits(metadata.user_id, config)
            
            # Create session record
            session_data = {
                "session_id": session_id,
                "user_id": metadata.user_id,
                "session_type": metadata.session_type,
                "platform": metadata.platform,
                "state": SessionState.CREATED,
                "metadata": metadata.dict(),
                "config": config.__dict__,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "expires_at": datetime.utcnow() + config.max_duration
            }
            
            # Persist to database
            async with get_async_session() as session:
                db_session = SessionModel(**session_data)
                session.add(db_session)
                await session.commit()
            
            # Cache session data
            await self._cache_session_data(session_id, session_data)
            
            # Initialize session workspace
            await self._initialize_session_workspace(session_id, metadata)
            
            # Publish session created event
            await self.event_publisher.publish_event(
                "session.created",
                {
                    "session_id": session_id,
                    "user_id": metadata.user_id,
                    "platform": metadata.platform,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Start session monitoring
            asyncio.create_task(self._start_session_monitoring(session_id, config))
            
            self.logger.info(f"Session created successfully: {session_id}")
            await self.metrics_collector.increment("sessions.created")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            await self.metrics_collector.increment("sessions.creation_failed")
            raise
    
    async def _validate_session_limits(self, user_id: str, config: SessionConfig):
        """Validate user session creation limits"""        
        # Check active sessions count
        active_sessions = await self._get_active_session_count(user_id)
        
        if active_sessions >= config.max_concurrent_sessions:
            raise ValueError(
                f"Maximum concurrent sessions exceeded: {active_sessions}/{config.max_concurrent_sessions}"
            )
    
    async def _get_active_session_count(self, user_id: str) -> int:
        """Get count of active sessions for user"""        
        cache_key = f"user_sessions:{user_id}"
        cached_count = await self.cache_manager.get(cache_key)
        
        if cached_count is not None:
            return int(cached_count)
        
        async with get_async_session() as session:
            query = select(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.state.in_([SessionState.ACTIVE, SessionState.SUSPENDED])
            )
            result = await session.execute(query)
            count = len(result.fetchall())
            
            # Cache for 5 minutes
            await self.cache_manager.set(cache_key, count, ttl=300)
            return count
    
    async def _cache_session_data(self, session_id: str, session_data: Dict[str, Any]):
        """Cache session data for fast access"""        
        cache_key = f"session:{session_id}"
        
        # Encrypt sensitive data if enabled
        if session_data.get("config", {}).get("encryption_enabled", True):
            session_data = await self.encryption_manager.encrypt_data(session_data)
        
        await self.cache_manager.set(
            cache_key,
            session_data,
            ttl=3600  # 1 hour TTL
        )
    
    async def _initialize_session_workspace(self, session_id: str, metadata: SessionMetadata):
        """Initialize session workspace environment"""        
        workspace_data = {
            "conversation_history": [],
            "context_stack": [],
            "entity_repository": {},
            "intent_history": [],
            "collaboration_space": {},
            "content_protection_logs": [],
            "monetization_tracking": {},
            "personalization_profile": {}
        }
        
        workspace_key = f"session_workspace:{session_id}"
        await self.cache_manager.set(workspace_key, workspace_data, ttl=86400)  # 24 hours
    
    async def _start_session_monitoring(self, session_id: str, config: SessionConfig):
        """Start background session monitoring"""        
        try:
            while True:
                await asyncio.sleep(config.auto_save_interval)
                
                # Check if session still exists
                session_data = await self.cache_manager.get(f"session:{session_id}")
                if not session_data:
                    break
                
                # Auto-save session state
                await self._auto_save_session(session_id)
                
                # Check for idle timeout
                await self._check_idle_timeout(session_id, config.idle_timeout)
                
        except asyncio.CancelledError:
            self.logger.info(f"Session monitoring cancelled for: {session_id}")
        except Exception as e:
            self.logger.error(f"Session monitoring error: {str(e)}")
    
    async def _auto_save_session(self, session_id: str):
        """Auto-save session state to persistent storage"""        
        try:
            # Get current session data from cache
            session_data = await self.cache_manager.get(f"session:{session_id}")
            workspace_data = await self.cache_manager.get(f"session_workspace:{session_id}")
            
            if session_data and workspace_data:
                # Update database with current state
                async with get_async_session() as session:
                    await session.execute(
                        update(SessionModel)
                        .where(SessionModel.session_id == session_id)
                        .values(
                            workspace_data=workspace_data,
                            last_activity=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    await session.commit()
                
                await self.metrics_collector.increment("sessions.auto_saved")
                
        except Exception as e:
            self.logger.error(f"Auto-save failed for session {session_id}: {str(e)}")
    
    async def _check_idle_timeout(self, session_id: str, idle_timeout: timedelta):
        """Check and handle session idle timeout"""        
        try:
            session_data = await self.cache_manager.get(f"session:{session_id}")
            
            if session_data:
                last_activity = datetime.fromisoformat(session_data.get("last_activity"))
                
                if datetime.utcnow() - last_activity > idle_timeout:
                    await self._suspend_idle_session(session_id)
                    
        except Exception as e:
            self.logger.error(f"Idle timeout check failed: {str(e)}")
    
    async def _suspend_idle_session(self, session_id: str):
        """Suspend idle session"""        
        try:
            # Update session state to suspended
            async with get_async_session() as session:
                await session.execute(
                    update(SessionModel)
                    .where(SessionModel.session_id == session_id)
                    .values(
                        state=SessionState.SUSPENDED,
                        suspended_at=datetime.utcnow()
                    )
                )
                await session.commit()
            
            # Publish suspension event
            await self.event_publisher.publish_event(
                "session.suspended",
                {
                    "session_id": session_id,
                    "reason": "idle_timeout",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.metrics_collector.increment("sessions.suspended")
            
        except Exception as e:
            self.logger.error(f"Session suspension failed: {str(e)}")


class SessionTerminationHandler:
    """Handles session termination with cleanup and data preservation"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
    
    async def terminate_session(
        self,
        session_id: str,
        reason: str = "user_request",
        save_conversation: bool = True
    ) -> bool:
        """Terminate session with complete cleanup"""        
        try:
            # Get session data
            session_data = await self._get_session_data(session_id)
            if not session_data:
                self.logger.warning(f"Session not found for termination: {session_id}")
                return False
            
            # Save conversation history if requested
            if save_conversation:
                await self._save_conversation_history(session_id)
            
            # Update session state to terminated
            await self._mark_session_terminated(session_id, reason)
            
            # Clean up cache and temporary data
            await self._cleanup_session_data(session_id)
            
            # Generate session analytics
            await self._generate_session_analytics(session_id, session_data)
            
            # Publish termination event
            await self.event_publisher.publish_event(
                "session.terminated",
                {
                    "session_id": session_id,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.metrics_collector.increment("sessions.terminated")
            self.logger.info(f"Session terminated successfully: {session_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Session termination failed: {str(e)}")
            await self.metrics_collector.increment("sessions.termination_failed")
            return False
    
    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from cache or database"""        
        # Try cache first
        session_data = await self.cache_manager.get(f"session:{session_id}")
        if session_data:
            return session_data
        
        # Fallback to database
        async with get_async_session() as session:
            query = select(SessionModel).where(SessionModel.session_id == session_id)
            result = await session.execute(query)
            db_session = result.scalar_one_or_none()
            
            if db_session:
                return {
                    "session_id": db_session.session_id,
                    "user_id": db_session.user_id,
                    "state": db_session.state,
                    "created_at": db_session.created_at.isoformat(),
                    "metadata": db_session.metadata
                }
        
        return None
    
    async def _save_conversation_history(self, session_id: str):
        """Save conversation history to long-term storage"""        
        try:
            workspace_data = await self.cache_manager.get(f"session_workspace:{session_id}")
            
            if workspace_data and workspace_data.get("conversation_history"):
                # Create conversation archive record
                archive_data = {
                    "session_id": session_id,
                    "conversation_history": workspace_data["conversation_history"],
                    "context_data": workspace_data.get("context_stack", []),
                    "entities": workspace_data.get("entity_repository", {}),
                    "archived_at": datetime.utcnow()
                }
                
                # Store in conversation archive
                archive_key = f"conversation_archive:{session_id}"
                await self.cache_manager.set(
                    archive_key,
                    archive_data,
                    ttl=2592000  # 30 days
                )
                
                self.logger.info(f"Conversation history archived: {session_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to save conversation history: {str(e)}")
    
    async def _mark_session_terminated(self, session_id: str, reason: str):
        """Mark session as terminated in database"""        
        async with get_async_session() as session:
            await session.execute(
                update(SessionModel)
                .where(SessionModel.session_id == session_id)
                .values(
                    state=SessionState.TERMINATED,
                    terminated_at=datetime.utcnow(),
                    termination_reason=reason
                )
            )
            await session.commit()
    
    async def _cleanup_session_data(self, session_id: str):
        """Clean up session cache and temporary data"""        
        try:
            # Remove session cache entries
            cache_keys = [
                f"session:{session_id}",
                f"session_workspace:{session_id}",
                f"session_metrics:{session_id}",
                f"session_analytics:{session_id}"
            ]
            
            for key in cache_keys:
                await self.cache_manager.delete(key)
            
            self.logger.info(f"Session cache cleaned up: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {str(e)}")
    
    async def _generate_session_analytics(self, session_id: str, session_data: Dict[str, Any]):
        """Generate final session analytics"""        
        try:
            created_at = datetime.fromisoformat(session_data["created_at"])
            duration = datetime.utcnow() - created_at
            
            analytics = {
                "session_id": session_id,
                "user_id": session_data["user_id"],
                "duration_seconds": duration.total_seconds(),
                "final_state": session_data["state"],
                "platform": session_data.get("metadata", {}).get("platform"),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Store analytics
            analytics_key = f"session_final_analytics:{session_id}"
            await self.cache_manager.set(analytics_key, analytics, ttl=604800)  # 7 days
            
            # Update metrics
            await self.metrics_collector.record_histogram(
                "session.duration",
                duration.total_seconds(),
                tags={"platform": analytics.get("platform", "unknown")}
            )
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")


class SessionStateTransitionManager:
    """Manages session state transitions with validation and monitoring"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.event_publisher = EventPublisher()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Valid state transitions
        self.valid_transitions = {
            SessionState.CREATED: [SessionState.ACTIVE, SessionState.TERMINATED],
            SessionState.ACTIVE: [SessionState.SUSPENDED, SessionState.TERMINATED],
            SessionState.SUSPENDED: [SessionState.ACTIVE, SessionState.TERMINATED],
            SessionState.TERMINATED: []  # Terminal state
        }
    
    async def transition_session(
        self,
        session_id: str,
        target_state: SessionState,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute session state transition with validation"""        
        try:
            # Get current session state
            current_state = await self._get_current_state(session_id)
            if not current_state:
                raise ValueError(f"Session not found: {session_id}")
            
            # Validate transition
            if not self._is_valid_transition(current_state, target_state):
                raise ValueError(
                    f"Invalid transition from {current_state} to {target_state}"
                )
            
            # Execute transition
            await self._execute_transition(session_id, current_state, target_state, metadata)
            
            # Publish transition event
            await self.event_publisher.publish_event(
                "session.state_changed",
                {
                    "session_id": session_id,
                    "from_state": current_state.value,
                    "to_state": target_state.value,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.metrics_collector.increment(
                "session.transitions",
                tags={
                    "from_state": current_state.value,
                    "to_state": target_state.value
                }
            )
            
            self.logger.info(
                f"Session transition successful: {session_id} "
                f"{current_state.value} -> {target_state.value}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Session transition failed: {str(e)}")
            await self.metrics_collector.increment("session.transition_errors")
            return False
    
    async def _get_current_state(self, session_id: str) -> Optional[SessionState]:
        """Get current session state"""        
        session_data = await self.cache_manager.get(f"session:{session_id}")
        if session_data:
            return SessionState(session_data.get("state"))
        
        # Fallback to database
        async with get_async_session() as session:
            query = select(SessionModel.state).where(SessionModel.session_id == session_id)
            result = await session.execute(query)
            state = result.scalar_one_or_none()
            
            return SessionState(state) if state else None
    
    def _is_valid_transition(self, current_state: SessionState, target_state: SessionState) -> bool:
        """Validate if state transition is allowed"""        
        return target_state in self.valid_transitions.get(current_state, [])
    
    async def _execute_transition(
        self,
        session_id: str,
        current_state: SessionState,
        target_state: SessionState,
        metadata: Optional[Dict[str, Any]]
    ):
        """Execute the actual state transition"""        
        transition_data = {
            "state": target_state,
            "last_state_change": datetime.utcnow(),
            "transition_metadata": metadata or {}
        }
        
        # Add state-specific fields
        if target_state == SessionState.SUSPENDED:
            transition_data["suspended_at"] = datetime.utcnow()
        elif target_state == SessionState.ACTIVE:
            transition_data["activated_at"] = datetime.utcnow()
        elif target_state == SessionState.TERMINATED:
            transition_data["terminated_at"] = datetime.utcnow()
        
        # Update database
        async with get_async_session() as session:
            await session.execute(
                update(SessionModel)
                .where(SessionModel.session_id == session_id)
                .values(**transition_data)
            )
            await session.commit()
        
        # Update cache
        session_cache = await self.cache_manager.get(f"session:{session_id}")
        if session_cache:
            session_cache.update(transition_data)
            await self.cache_manager.set(f"session:{session_id}", session_cache)


class SessionLifecycleManager:
    """Main session lifecycle orchestrator"""    
    def __init__(self):
        self.creation_handler = SessionCreationHandler()
        self.termination_handler = SessionTerminationHandler()
        self.transition_manager = SessionStateTransitionManager()
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_session(
        self,
        metadata: SessionMetadata,
        config: Optional[SessionConfig] = None
    ) -> str:
        """Create new session with full lifecycle management"""        
        return await self.creation_handler.create_session(metadata, config)
    
    async def activate_session(self, session_id: str) -> bool:
        """Activate created session"""        
        return await self.transition_manager.transition_session(
            session_id,
            SessionState.ACTIVE,
            {"activation_time": datetime.utcnow().isoformat()}
        )
    
    async def suspend_session(self, session_id: str, reason: str = "user_request") -> bool:
        """Suspend active session"""        
        return await self.transition_manager.transition_session(
            session_id,
            SessionState.SUSPENDED,
            {"suspension_reason": reason}
        )
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume suspended session"""        
        return await self.transition_manager.transition_session(
            session_id,
            SessionState.ACTIVE,
            {"resumed_at": datetime.utcnow().isoformat()}
        )
    
    async def terminate_session(
        self,
        session_id: str,
        reason: str = "user_request",
        save_conversation: bool = True
    ) -> bool:
        """Terminate session with cleanup"""        
        return await self.termination_handler.terminate_session(
            session_id,
            reason,
            save_conversation
        )
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session status"""        
        try:
            current_state = await self.transition_manager._get_current_state(session_id)
            session_data = await self.termination_handler._get_session_data(session_id)
            
            if not session_data:
                return None
            
            return {
                "session_id": session_id,
                "current_state": current_state.value if current_state else None,
                "user_id": session_data.get("user_id"),
                "created_at": session_data.get("created_at"),
                "last_activity": session_data.get("last_activity"),
                "metadata": session_data.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session status: {str(e)}")
            return None
    
    @asynccontextmanager
    async def session_context(
        self,
        metadata: SessionMetadata,
        config: Optional[SessionConfig] = None
    ):
        """Context manager for automatic session lifecycle management"""        
        session_id = None
        try:
            # Create and activate session
            session_id = await self.create_session(metadata, config)
            await self.activate_session(session_id)
            
            yield session_id
            
        except Exception as e:
            self.logger.error(f"Session context error: {str(e)}")
            raise
        finally:
            # Always terminate session
            if session_id:
                await self.terminate_session(session_id, "context_exit")
