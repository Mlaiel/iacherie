"""Multi-Platform Session Synchronization - IA Influencer Agent

Enterprise-grade cross-platform session synchronization for content creators
managing conversations across Instagram, TikTok, YouTube, Spotify, and other
platforms with real-time state management and conflict resolution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, SessionState, PlatformType
from ...models.sync import CrossPlatformSyncModel, SyncState, ConflictResolution
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher

logger = get_logger(__name__)


class SyncOperation(Enum):
    """Platform synchronization operation types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    CONFLICT_RESOLVE = "conflict_resolve"
    FULL_SYNC = "full_sync"


class ConflictStrategy(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    MOST_RECENT_PLATFORM = "most_recent_platform"
    USER_PREFERENCE = "user_preference"
    MERGE_INTELLIGENT = "merge_intelligent"
    MANUAL_RESOLUTION = "manual_resolution"


@dataclass
class PlatformSyncConfig:
    """Platform-specific synchronization configuration"""
    platform_type: PlatformType
    sync_enabled: bool = True
    sync_interval: int = 30  # seconds
    conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS
    batch_size: int = 100
    retry_attempts: int = 3
    timeout: int = 30
    priority: int = 1  # 1-10, higher = more priority


class SyncConflict(BaseModel):
    """Represents a synchronization conflict"""
    conflict_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    platforms: List[str]
    conflict_type: str
    local_state: Dict[str, Any]
    remote_states: Dict[str, Dict[str, Any]]
    resolution_strategy: ConflictStrategy
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_data: Optional[Dict[str, Any]] = None


class PlatformSessionAdapter:
    """Adapter for platform-specific session management"""
    
    def __init__(self, platform_type: PlatformType, config: PlatformSyncConfig):
        self.platform_type = platform_type
        self.config = config
        self.cache_manager = CacheManager()
        self.encryption_manager = EncryptionManager()
        self.logger = get_logger(f"{self.__class__.__name__}_{platform_type.value}")
    
    async def serialize_session_state(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Serialize session state for platform-specific format"""
        
        platform_state = {
            "session_id": session_data["session_id"],
            "user_id": session_data["user_id"],
            "platform": self.platform_type.value,
            "state": session_data["state"],
            "last_modified": datetime.utcnow().isoformat(),
            "sync_version": session_data.get("sync_version", 1),
            "platform_metadata": {}
        }
        
        # Platform-specific serialization
        if self.platform_type == PlatformType.INSTAGRAM:
            platform_state["platform_metadata"] = {
                "story_context": session_data.get("story_context", {}),
                "reel_interactions": session_data.get("reel_interactions", []),
                "dm_thread_id": session_data.get("dm_thread_id"),
                "business_account": session_data.get("business_account", False)
            }
        
        elif self.platform_type == PlatformType.TIKTOK:
            platform_state["platform_metadata"] = {
                "video_context": session_data.get("video_context", {}),
                "trending_sounds": session_data.get("trending_sounds", []),
                "challenge_participation": session_data.get("challenge_participation", {}),
                "duet_opportunities": session_data.get("duet_opportunities", [])
            }
        
        elif self.platform_type == PlatformType.YOUTUBE:
            platform_state["platform_metadata"] = {
                "video_analytics": session_data.get("video_analytics", {}),
                "comment_management": session_data.get("comment_management", {}),
                "live_stream_data": session_data.get("live_stream_data", {}),
                "shorts_optimization": session_data.get("shorts_optimization", {})
            }
        
        elif self.platform_type == PlatformType.SPOTIFY:
            platform_state["platform_metadata"] = {
                "track_context": session_data.get("track_context", {}),
                "playlist_interactions": session_data.get("playlist_interactions", []),
                "artist_insights": session_data.get("artist_insights", {}),
                "collaboration_requests": session_data.get("collaboration_requests", [])
            }
        
        return platform_state
    
    async def deserialize_session_state(
        self,
        platform_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deserialize platform state to universal session format"""
        
        session_data = {
            "session_id": platform_state["session_id"],
            "user_id": platform_state["user_id"],
            "state": platform_state["state"],
            "last_modified": platform_state["last_modified"],
            "sync_version": platform_state.get("sync_version", 1),
            "platform_data": {
                self.platform_type.value: platform_state.get("platform_metadata", {})
            }
        }
        
        return session_data
    
    async def validate_platform_state(
        self,
        platform_state: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate platform-specific state format"""
        
        errors = []
        
        # Common validation
        required_fields = ["session_id", "user_id", "state", "last_modified"]
        for field in required_fields:
            if field not in platform_state:
                errors.append(f"Missing required field: {field}")
        
        # Platform-specific validation
        if self.platform_type == PlatformType.INSTAGRAM:
            metadata = platform_state.get("platform_metadata", {})
            if metadata.get("business_account") and not metadata.get("dm_thread_id"):
                errors.append("Business accounts require dm_thread_id")
        
        elif self.platform_type == PlatformType.SPOTIFY:
            metadata = platform_state.get("platform_metadata", {})
            if metadata.get("track_context") and "track_id" not in metadata["track_context"]:
                errors.append("track_context missing track_id")
        
        return len(errors) == 0, errors


class CrossPlatformStateManager:
    """Manages state consistency across multiple platforms"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Platform adapters
        self.adapters: Dict[PlatformType, PlatformSessionAdapter] = {}
        self.sync_configs: Dict[PlatformType, PlatformSyncConfig] = {}
    
    def register_platform(
        self,
        platform_type: PlatformType,
        config: PlatformSyncConfig
    ):
        """Register platform for synchronization"""
        
        self.sync_configs[platform_type] = config
        self.adapters[platform_type] = PlatformSessionAdapter(platform_type, config)
        
        self.logger.info(f"Platform registered for sync: {platform_type.value}")
    
    async def get_session_state(
        self,
        session_id: str,
        platform: Optional[PlatformType] = None
    ) -> Dict[str, Any]:
        """Get session state for specific platform or unified state"""
        
        if platform:
            # Get platform-specific state
            cache_key = f"platform_session:{platform.value}:{session_id}"
            platform_state = await self.cache_manager.get(cache_key)
            
            if platform_state:
                adapter = self.adapters.get(platform)
                if adapter:
                    return await adapter.deserialize_session_state(platform_state)
            
            return {}
        
        else:
            # Get unified state from all platforms
            unified_state = {}
            
            for platform_type in self.adapters.keys():
                platform_state = await self.get_session_state(session_id, platform_type)
                if platform_state:
                    unified_state[platform_type.value] = platform_state
            
            return unified_state
    
    async def update_session_state(
        self,
        session_id: str,
        state_updates: Dict[str, Any],
        source_platform: Optional[PlatformType] = None
    ) -> bool:
        """Update session state and propagate to other platforms"""
        
        try:
            # Get current unified state
            current_state = await self.get_session_state(session_id)
            
            # Apply updates
            updated_state = self._merge_state_updates(current_state, state_updates)
            
            # Increment sync version
            updated_state["sync_version"] = updated_state.get("sync_version", 0) + 1
            updated_state["last_modified"] = datetime.utcnow().isoformat()
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(session_id, updated_state, source_platform)
            
            if conflicts:
                # Handle conflicts
                resolved_state = await self._resolve_conflicts(session_id, conflicts, updated_state)
                updated_state = resolved_state
            
            # Propagate to all platforms
            await self._propagate_state_updates(session_id, updated_state, source_platform)
            
            # Publish sync event
            await self.event_publisher.publish_event(
                "session.state_synchronized",
                {
                    "session_id": session_id,
                    "source_platform": source_platform.value if source_platform else "unified",
                    "sync_version": updated_state["sync_version"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.metrics_collector.increment("session.state_updates")
            return True
            
        except Exception as e:
            self.logger.error(f"State update failed: {str(e)}")
            await self.metrics_collector.increment("session.state_update_errors")
            return False
    
    def _merge_state_updates(
        self,
        current_state: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligently merge state updates"""
        
        merged_state = current_state.copy()
        
        for key, value in updates.items():
            if isinstance(value, dict) and key in merged_state:
                # Deep merge dictionaries
                merged_state[key] = {**merged_state[key], **value}
            elif isinstance(value, list) and key in merged_state:
                # Append to lists (could be made smarter)
                merged_state[key] = list(set(merged_state[key] + value))
            else:
                # Direct replacement
                merged_state[key] = value
        
        return merged_state
    
    async def _detect_conflicts(
        self,
        session_id: str,
        updated_state: Dict[str, Any],
        source_platform: Optional[PlatformType]
    ) -> List[SyncConflict]:
        """Detect synchronization conflicts"""
        
        conflicts = []
        
        # Get states from other platforms
        for platform_type in self.adapters.keys():
            if platform_type == source_platform:
                continue
            
            platform_state = await self.get_session_state(session_id, platform_type)
            
            if platform_state:
                # Check for version conflicts
                local_version = updated_state.get("sync_version", 0)
                remote_version = platform_state.get("sync_version", 0)
                
                if remote_version > local_version:
                    conflict = SyncConflict(
                        session_id=session_id,
                        platforms=[source_platform.value if source_platform else "unified", platform_type.value],
                        conflict_type="version_conflict",
                        local_state=updated_state,
                        remote_states={platform_type.value: platform_state},
                        resolution_strategy=self.sync_configs[platform_type].conflict_strategy
                    )
                    conflicts.append(conflict)
                
                # Check for data conflicts
                if await self._has_data_conflicts(updated_state, platform_state):
                    conflict = SyncConflict(
                        session_id=session_id,
                        platforms=[source_platform.value if source_platform else "unified", platform_type.value],
                        conflict_type="data_conflict",
                        local_state=updated_state,
                        remote_states={platform_type.value: platform_state},
                        resolution_strategy=self.sync_configs[platform_type].conflict_strategy
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    async def _has_data_conflicts(
        self,
        state1: Dict[str, Any],
        state2: Dict[str, Any]
    ) -> bool:
        """Check if two states have conflicting data"""
        
        # Compare critical fields
        critical_fields = ["user_id", "state", "conversation_context"]
        
        for field in critical_fields:
            if field in state1 and field in state2:
                if state1[field] != state2[field]:
                    return True
        
        return False
    
    async def _resolve_conflicts(
        self,
        session_id: str,
        conflicts: List[SyncConflict],
        proposed_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve synchronization conflicts"""
        
        resolved_state = proposed_state.copy()
        
        for conflict in conflicts:
            strategy = conflict.resolution_strategy
            
            if strategy == ConflictStrategy.LAST_WRITE_WINS:
                # Use the most recent timestamp
                latest_state = self._get_latest_state(conflict)
                resolved_state.update(latest_state)
            
            elif strategy == ConflictStrategy.MOST_RECENT_PLATFORM:
                # Use state from most recently active platform
                recent_platform_state = await self._get_most_recent_platform_state(conflict)
                resolved_state.update(recent_platform_state)
            
            elif strategy == ConflictStrategy.MERGE_INTELLIGENT:
                # Intelligent merge based on field priorities
                merged_state = await self._intelligent_merge(conflict)
                resolved_state.update(merged_state)
            
            elif strategy == ConflictStrategy.MANUAL_RESOLUTION:
                # Queue for manual resolution
                await self._queue_manual_resolution(conflict)
                continue
            
            # Mark conflict as resolved
            conflict.resolved_at = datetime.utcnow()
            conflict.resolution_data = resolved_state
            
            await self._store_conflict_resolution(conflict)
        
        return resolved_state
    
    def _get_latest_state(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Get state with latest timestamp"""
        
        latest_timestamp = None
        latest_state = conflict.local_state
        
        # Check local state
        local_time = datetime.fromisoformat(conflict.local_state.get("last_modified"))
        latest_timestamp = local_time
        
        # Check remote states
        for platform, state in conflict.remote_states.items():
            remote_time = datetime.fromisoformat(state.get("last_modified"))
            if remote_time > latest_timestamp:
                latest_timestamp = remote_time
                latest_state = state
        
        return latest_state
    
    async def _get_most_recent_platform_state(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Get state from most recently active platform"""
        
        # Implementation would check platform activity metrics
        # For now, return local state
        return conflict.local_state
    
    async def _intelligent_merge(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Perform intelligent merge of conflicting states"""
        
        merged_state = conflict.local_state.copy()
        
        # Field priority rules
        field_priorities = {
            "user_preferences": "remote",  # Remote user preferences take priority
            "conversation_context": "merge",  # Merge conversation contexts
            "analytics_data": "local",  # Local analytics take priority
            "collaboration_data": "merge"  # Merge collaboration data
        }
        
        for platform, remote_state in conflict.remote_states.items():
            for field, priority in field_priorities.items():
                if field in remote_state:
                    if priority == "remote":
                        merged_state[field] = remote_state[field]
                    elif priority == "merge" and field in merged_state:
                        merged_state[field] = self._merge_field_data(
                            merged_state[field],
                            remote_state[field]
                        )
        
        return merged_state
    
    def _merge_field_data(self, local_data: Any, remote_data: Any) -> Any:
        """Merge specific field data intelligently"""
        
        if isinstance(local_data, dict) and isinstance(remote_data, dict):
            return {**local_data, **remote_data}
        elif isinstance(local_data, list) and isinstance(remote_data, list):
            return list(set(local_data + remote_data))
        else:
            return remote_data  # Default to remote data
    
    async def _queue_manual_resolution(self, conflict: SyncConflict):
        """Queue conflict for manual resolution"""
        
        queue_key = f"manual_resolution_queue"
        await self.cache_manager.list_push(queue_key, conflict.dict())
        
        # Notify administrators
        await self.event_publisher.publish_event(
            "session.conflict_requires_manual_resolution",
            {
                "conflict_id": conflict.conflict_id,
                "session_id": conflict.session_id,
                "platforms": conflict.platforms,
                "conflict_type": conflict.conflict_type
            }
        )
    
    async def _store_conflict_resolution(self, conflict: SyncConflict):
        """Store conflict resolution for audit purposes"""
        
        async with get_async_session() as session:
            resolution_record = CrossPlatformSyncModel(
                conflict_id=conflict.conflict_id,
                session_id=conflict.session_id,
                platforms=conflict.platforms,
                conflict_type=conflict.conflict_type,
                resolution_strategy=conflict.resolution_strategy.value,
                resolution_data=conflict.resolution_data,
                created_at=conflict.created_at,
                resolved_at=conflict.resolved_at
            )
            
            session.add(resolution_record)
            await session.commit()
    
    async def _propagate_state_updates(
        self,
        session_id: str,
        updated_state: Dict[str, Any],
        source_platform: Optional[PlatformType]
    ):
        """Propagate state updates to all registered platforms"""
        
        for platform_type, adapter in self.adapters.items():
            if platform_type == source_platform:
                continue  # Skip source platform
            
            try:
                # Convert to platform-specific format
                platform_state = await adapter.serialize_session_state(updated_state)
                
                # Validate platform state
                is_valid, errors = await adapter.validate_platform_state(platform_state)
                
                if not is_valid:
                    self.logger.warning(
                        f"Invalid state for {platform_type.value}: {errors}"
                    )
                    continue
                
                # Store platform state
                cache_key = f"platform_session:{platform_type.value}:{session_id}"
                await self.cache_manager.set(cache_key, platform_state, ttl=3600)
                
                await self.metrics_collector.increment(
                    "session.platform_sync",
                    tags={"platform": platform_type.value}
                )
                
            except Exception as e:
                self.logger.error(
                    f"Failed to propagate to {platform_type.value}: {str(e)}"
                )
                await self.metrics_collector.increment(
                    "session.platform_sync_errors",
                    tags={"platform": platform_type.value}
                )


class SessionSynchronizationEngine:
    """Main session synchronization orchestrator"""
    
    def __init__(self):
        self.state_manager = CrossPlatformStateManager()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Background sync tasks
        self.sync_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize_platforms(self):
        """Initialize all supported platforms"""
        
        # Instagram configuration
        instagram_config = PlatformSyncConfig(
            platform_type=PlatformType.INSTAGRAM,
            sync_interval=30,
            conflict_strategy=ConflictStrategy.MERGE_INTELLIGENT,
            priority=5
        )
        self.state_manager.register_platform(PlatformType.INSTAGRAM, instagram_config)
        
        # TikTok configuration
        tiktok_config = PlatformSyncConfig(
            platform_type=PlatformType.TIKTOK,
            sync_interval=45,
            conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
            priority=4
        )
        self.state_manager.register_platform(PlatformType.TIKTOK, tiktok_config)
        
        # YouTube configuration
        youtube_config = PlatformSyncConfig(
            platform_type=PlatformType.YOUTUBE,
            sync_interval=60,
            conflict_strategy=ConflictStrategy.MERGE_INTELLIGENT,
            priority=5
        )
        self.state_manager.register_platform(PlatformType.YOUTUBE, youtube_config)
        
        # Spotify configuration
        spotify_config = PlatformSyncConfig(
            platform_type=PlatformType.SPOTIFY,
            sync_interval=90,
            conflict_strategy=ConflictStrategy.MOST_RECENT_PLATFORM,
            priority=3
        )
        self.state_manager.register_platform(PlatformType.SPOTIFY, spotify_config)
        
        self.logger.info("All platforms initialized for synchronization")
    
    async def start_session_sync(self, session_id: str) -> bool:
        """Start background synchronization for session"""
        
        if session_id in self.sync_tasks:
            self.logger.warning(f"Sync already running for session: {session_id}")
            return False
        
        try:
            # Create background sync task
            sync_task = asyncio.create_task(
                self._background_sync_loop(session_id)
            )
            
            self.sync_tasks[session_id] = sync_task
            
            self.logger.info(f"Started sync for session: {session_id}")
            await self.metrics_collector.increment("session.sync_started")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sync: {str(e)}")
            return False
    
    async def stop_session_sync(self, session_id: str) -> bool:
        """Stop background synchronization for session"""
        
        if session_id not in self.sync_tasks:
            return False
        
        try:
            # Cancel sync task
            sync_task = self.sync_tasks[session_id]
            sync_task.cancel()
            
            try:
                await sync_task
            except asyncio.CancelledError:
                pass
            
            del self.sync_tasks[session_id]
            
            self.logger.info(f"Stopped sync for session: {session_id}")
            await self.metrics_collector.increment("session.sync_stopped")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop sync: {str(e)}")
            return False
    
    async def _background_sync_loop(self, session_id: str):
        """Background synchronization loop for session"""
        
        try:
            while True:
                # Get minimum sync interval from all platforms
                min_interval = min(
                    config.sync_interval 
                    for config in self.state_manager.sync_configs.values()
                    if config.sync_enabled
                )
                
                await asyncio.sleep(min_interval)
                
                # Perform sync check
                await self._perform_sync_check(session_id)
                
        except asyncio.CancelledError:
            self.logger.info(f"Sync loop cancelled for session: {session_id}")
        except Exception as e:
            self.logger.error(f"Sync loop error for session {session_id}: {str(e)}")
    
    async def _perform_sync_check(self, session_id: str):
        """Perform periodic synchronization check"""
        
        try:
            # Get current unified state
            unified_state = await self.state_manager.get_session_state(session_id)
            
            if not unified_state:
                return
            
            # Check each platform for updates
            for platform_type in self.state_manager.adapters.keys():
                config = self.state_manager.sync_configs[platform_type]
                
                if not config.sync_enabled:
                    continue
                
                # Check if sync interval has passed
                last_sync_key = f"last_sync:{platform_type.value}:{session_id}"
                last_sync = await self.cache_manager.get(last_sync_key)
                
                if last_sync:
                    last_sync_time = datetime.fromisoformat(last_sync)
                    if datetime.utcnow() - last_sync_time < timedelta(seconds=config.sync_interval):
                        continue
                
                # Perform platform sync
                await self._sync_platform(session_id, platform_type)
                
                # Update last sync time
                await self.cache_manager.set(
                    last_sync_key,
                    datetime.utcnow().isoformat(),
                    ttl=86400
                )
                
        except Exception as e:
            self.logger.error(f"Sync check failed: {str(e)}")
    
    async def _sync_platform(self, session_id: str, platform_type: PlatformType):
        """Synchronize specific platform"""
        
        try:
            # Get platform state
            platform_state = await self.state_manager.get_session_state(
                session_id, 
                platform_type
            )
            
            # Get unified state
            unified_state = await self.state_manager.get_session_state(session_id)
            
            # Compare and update if needed
            if platform_state and unified_state:
                platform_version = platform_state.get("sync_version", 0)
                unified_version = max(
                    state.get("sync_version", 0) 
                    for state in unified_state.values()
                    if isinstance(state, dict)
                )
                
                if unified_version > platform_version:
                    # Update platform with unified state
                    await self.state_manager.update_session_state(
                        session_id,
                        unified_state.get(platform_type.value, {}),
                        platform_type
                    )
            
            await self.metrics_collector.increment(
                "session.platform_synced",
                tags={"platform": platform_type.value}
            )
            
        except Exception as e:
            self.logger.error(f"Platform sync failed for {platform_type.value}: {str(e)}")
            await self.metrics_collector.increment(
                "session.platform_sync_errors",
                tags={"platform": platform_type.value}
            )


class MultiPlatformSessionSync:
    """Main multi-platform session synchronization facade"""
    
    def __init__(self):
        self.sync_engine = SessionSynchronizationEngine()
        self.state_manager = self.sync_engine.state_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def initialize(self):
        """Initialize the synchronization system"""
        
        await self.sync_engine.initialize_platforms()
        self.logger.info("Multi-platform session sync initialized")
    
    async def start_session_sync(self, session_id: str) -> bool:
        """Start synchronization for a session"""
        
        return await self.sync_engine.start_session_sync(session_id)
    
    async def stop_session_sync(self, session_id: str) -> bool:
        """Stop synchronization for a session"""
        
        return await self.sync_engine.stop_session_sync(session_id)
    
    async def update_session_state(
        self,
        session_id: str,
        updates: Dict[str, Any],
        platform: Optional[PlatformType] = None
    ) -> bool:
        """Update session state with cross-platform sync"""
        
        return await self.state_manager.update_session_state(
            session_id,
            updates,
            platform
        )
    
    async def get_session_state(
        self,
        session_id: str,
        platform: Optional[PlatformType] = None
    ) -> Dict[str, Any]:
        """Get session state for platform or unified view"""
        
        return await self.state_manager.get_session_state(session_id, platform)
    
    async def get_sync_status(self, session_id: str) -> Dict[str, Any]:
        """Get synchronization status for session"""
        
        try:
            status = {
                "session_id": session_id,
                "sync_active": session_id in self.sync_engine.sync_tasks,
                "platforms": {},
                "last_sync": {},
                "conflicts": []
            }
            
            # Get platform status
            for platform_type in self.state_manager.adapters.keys():
                platform_state = await self.state_manager.get_session_state(
                    session_id, 
                    platform_type
                )
                
                status["platforms"][platform_type.value] = {
                    "connected": platform_state is not None,
                    "sync_version": platform_state.get("sync_version", 0) if platform_state else 0,
                    "last_modified": platform_state.get("last_modified") if platform_state else None
                }
                
                # Get last sync time
                last_sync_key = f"last_sync:{platform_type.value}:{session_id}"
                last_sync = await self.sync_engine.cache_manager.get(last_sync_key)
                status["last_sync"][platform_type.value] = last_sync
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get sync status: {str(e)}")
            return {"error": str(e)}
    
    async def force_full_sync(self, session_id: str) -> bool:
        """Force full synchronization across all platforms"""
        
        try:
            # Get unified state
            unified_state = await self.state_manager.get_session_state(session_id)
            
            if not unified_state:
                return False
            
            # Force update to all platforms
            for platform_type in self.state_manager.adapters.keys():
                await self.state_manager.update_session_state(
                    session_id,
                    unified_state.get(platform_type.value, {}),
                    platform_type
                )
            
            # Publish full sync event
            await self.sync_engine.event_publisher.publish_event(
                "session.full_sync_completed",
                {
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.sync_engine.metrics_collector.increment("session.full_sync")
            return True
            
        except Exception as e:
            self.logger.error(f"Full sync failed: {str(e)}")
            return False
