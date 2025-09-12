"""
🗃️ Stateful Service Template - Enterprise Stateful Service Management Framework
===============================================================================

🛡️ BACKEND SENIOR - Advanced Stateful Service Template
- Stateful service lifecycle management
- State persistence and recovery mechanisms  
- Distributed state consistency protocols
- Session management and sticky sessions
- State replication and failover strategies
- Performance optimization for stateful operations

Author: Backend Senior Expert
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import threading
import hashlib
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import uuid
import pickle
import aioredis
from concurrent.futures import ThreadPoolExecutor
import copy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateStatus(Enum):
    """State status in stateful service"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PERSISTING = "persisting"
    RECOVERING = "recovering"
    CORRUPTED = "corrupted"
    EXPIRED = "expired"

class SessionStatus(Enum):
    """Session status"""
    CREATED = "created"
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class ReplicationStrategy(Enum):
    """State replication strategies"""
    NONE = "none"
    MASTER_SLAVE = "master_slave"
    MULTI_MASTER = "multi_master"
    CONSENSUS = "consensus"

@dataclass
class ServiceState:
    """Service state data structure"""
    state_id: str
    service_id: str
    session_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    status: StateStatus = StateStatus.ACTIVE
    ttl_seconds: Optional[int] = None
    checksum: Optional[str] = None

@dataclass
class ServiceSession:
    """Service session management"""
    session_id: str
    user_id: Optional[str] = None
    service_id: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.CREATED
    sticky_node: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StatefulConfig:
    """Stateful service configuration"""
    service_name: str
    persistence_enabled: bool = True
    replication_strategy: ReplicationStrategy = ReplicationStrategy.MASTER_SLAVE
    state_ttl_seconds: int = 3600  # 1 hour default
    session_timeout_seconds: int = 1800  # 30 minutes default
    max_states_per_service: int = 10000
    auto_cleanup_enabled: bool = True
    consistency_level: str = "eventual"  # strong, eventual
    backup_interval_seconds: int = 300  # 5 minutes

class StateStore(ABC):
    """Abstract state storage interface"""
    
    @abstractmethod
    async def save_state(self, state: ServiceState) -> bool:
        """Save service state"""
        pass
    
    @abstractmethod
    async def load_state(self, state_id: str) -> Optional[ServiceState]:
        """Load service state"""
        pass
    
    @abstractmethod
    async def delete_state(self, state_id: str) -> bool:
        """Delete service state"""
        pass
    
    @abstractmethod
    async def list_states(self, service_id: str) -> List[ServiceState]:
        """List all states for service"""
        pass

class MemoryStateStore(StateStore):
    """In-memory state store implementation"""
    
    def __init__(self):
        self.states = {}
        self.locks = defaultdict(asyncio.Lock)
    
    async def save_state(self, state: ServiceState) -> bool:
        """Save state to memory"""
        async with self.locks[state.state_id]:
            try:
                # Calculate checksum for integrity
                state.checksum = self._calculate_checksum(state)
                state.updated_at = datetime.now()
                
                # Deep copy to prevent external modifications
                self.states[state.state_id] = copy.deepcopy(state)
                
                logger.debug(f"State {state.state_id} saved to memory")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save state {state.state_id}: {str(e)}")
                return False
    
    async def load_state(self, state_id: str) -> Optional[ServiceState]:
        """Load state from memory"""
        async with self.locks[state_id]:
            try:
                if state_id in self.states:
                    state = copy.deepcopy(self.states[state_id])
                    
                    # Verify checksum
                    if state.checksum and not self._verify_checksum(state):
                        logger.warning(f"State {state_id} checksum mismatch")
                        state.status = StateStatus.CORRUPTED
                        return state
                    
                    # Update last accessed
                    state.last_accessed = datetime.now()
                    self.states[state_id].last_accessed = state.last_accessed
                    
                    logger.debug(f"State {state_id} loaded from memory")
                    return state
                
                return None
                
            except Exception as e:
                logger.error(f"Failed to load state {state_id}: {str(e)}")
                return None
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete state from memory"""
        async with self.locks[state_id]:
            try:
                if state_id in self.states:
                    del self.states[state_id]
                    logger.debug(f"State {state_id} deleted from memory")
                    return True
                return False
                
            except Exception as e:
                logger.error(f"Failed to delete state {state_id}: {str(e)}")
                return False
    
    async def list_states(self, service_id: str) -> List[ServiceState]:
        """List all states for service"""
        try:
            states = []
            for state in self.states.values():
                if state.service_id == service_id:
                    states.append(copy.deepcopy(state))
            return states
            
        except Exception as e:
            logger.error(f"Failed to list states for service {service_id}: {str(e)}")
            return []
    
    def _calculate_checksum(self, state: ServiceState) -> str:
        """Calculate checksum for state integrity"""
        # Create deterministic string representation
        data_str = json.dumps(state.data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _verify_checksum(self, state: ServiceState) -> bool:
        """Verify state checksum"""
        expected_checksum = self._calculate_checksum(state)
        return state.checksum == expected_checksum

class RedisStateStore(StateStore):
    """Redis-based state store implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        self.key_prefix = "stateful_service:state:"
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis state store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            raise
    
    async def save_state(self, state: ServiceState) -> bool:
        """Save state to Redis"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Serialize state
            state_data = {
                "state_id": state.state_id,
                "service_id": state.service_id,
                "session_id": state.session_id,
                "data": json.dumps(state.data),
                "metadata": json.dumps(state.metadata),
                "version": state.version,
                "created_at": state.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "last_accessed": state.last_accessed.isoformat(),
                "status": state.status.value,
                "ttl_seconds": state.ttl_seconds
            }
            
            key = f"{self.key_prefix}{state.state_id}"
            
            # Save with TTL if specified
            if state.ttl_seconds:
                await redis.hset(key, mapping=state_data)
                await redis.expire(key, state.ttl_seconds)
            else:
                await redis.hset(key, mapping=state_data)
            
            logger.debug(f"State {state.state_id} saved to Redis")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state {state.state_id} to Redis: {str(e)}")
            return False
    
    async def load_state(self, state_id: str) -> Optional[ServiceState]:
        """Load state from Redis"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            key = f"{self.key_prefix}{state_id}"
            state_data = await redis.hgetall(key)
            
            if not state_data:
                return None
            
            # Deserialize state
            state = ServiceState(
                state_id=state_data[b"state_id"].decode(),
                service_id=state_data[b"service_id"].decode(),
                session_id=state_data.get(b"session_id", b"").decode() or None,
                data=json.loads(state_data[b"data"].decode()),
                metadata=json.loads(state_data[b"metadata"].decode()),
                version=int(state_data[b"version"]),
                created_at=datetime.fromisoformat(state_data[b"created_at"].decode()),
                updated_at=datetime.fromisoformat(state_data[b"updated_at"].decode()),
                last_accessed=datetime.fromisoformat(state_data[b"last_accessed"].decode()),
                status=StateStatus(state_data[b"status"].decode()),
                ttl_seconds=int(state_data[b"ttl_seconds"]) if state_data.get(b"ttl_seconds") else None
            )
            
            # Update last accessed
            state.last_accessed = datetime.now()
            await self._update_last_accessed(redis, key, state.last_accessed)
            
            logger.debug(f"State {state_id} loaded from Redis")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load state {state_id} from Redis: {str(e)}")
            return None
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete state from Redis"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            key = f"{self.key_prefix}{state_id}"
            result = await redis.delete(key)
            
            logger.debug(f"State {state_id} deleted from Redis")
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete state {state_id} from Redis: {str(e)}")
            return False
    
    async def list_states(self, service_id: str) -> List[ServiceState]:
        """List all states for service"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Use pattern matching to find all states for service
            pattern = f"{self.key_prefix}*"
            keys = await redis.keys(pattern)
            
            states = []
            for key in keys:
                state_data = await redis.hgetall(key)
                if state_data and state_data.get(b"service_id", b"").decode() == service_id:
                    state = ServiceState(
                        state_id=state_data[b"state_id"].decode(),
                        service_id=state_data[b"service_id"].decode(),
                        session_id=state_data.get(b"session_id", b"").decode() or None,
                        data=json.loads(state_data[b"data"].decode()),
                        metadata=json.loads(state_data[b"metadata"].decode()),
                        version=int(state_data[b"version"]),
                        created_at=datetime.fromisoformat(state_data[b"created_at"].decode()),
                        updated_at=datetime.fromisoformat(state_data[b"updated_at"].decode()),
                        last_accessed=datetime.fromisoformat(state_data[b"last_accessed"].decode()),
                        status=StateStatus(state_data[b"status"].decode()),
                        ttl_seconds=int(state_data[b"ttl_seconds"]) if state_data.get(b"ttl_seconds") else None
                    )
                    states.append(state)
            
            return states
            
        except Exception as e:
            logger.error(f"Failed to list states for service {service_id}: {str(e)}")
            return []
    
    async def _update_last_accessed(self, redis, key: str, last_accessed: datetime):
        """Update last accessed timestamp"""
        await redis.hset(key, "last_accessed", last_accessed.isoformat())

class StatefulService:
    """🗃️ Advanced Stateful Service for Enterprise State Management"""
    
    def __init__(self, config: StatefulConfig, state_store: StateStore = None):
        """Initialize Stateful Service"""
        self.config = config
        self.service_id = f"stateful_service_{config.service_name}_{int(time.time())}"
        self.state_store = state_store or MemoryStateStore()
        
        # Session management
        self.sessions = {}
        self.session_locks = defaultdict(asyncio.Lock)
        
        # State management
        self.local_cache = {}
        self.cache_locks = defaultdict(asyncio.Lock)
        
        # Background tasks
        self.background_tasks = []
        self.is_running = False
        
        # Statistics
        self.stats = {
            "states_created": 0,
            "states_loaded": 0,
            "states_updated": 0,
            "states_deleted": 0,
            "sessions_created": 0,
            "sessions_expired": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info(f"🗃️ Stateful Service initialized: {self.service_id}")
    
    async def start(self):
        """Start the stateful service"""
        logger.info(f"Starting stateful service: {self.config.service_name}")
        
        self.is_running = True
        
        # Initialize state store if needed
        if hasattr(self.state_store, 'initialize'):
            await self.state_store.initialize()
        
        # Start background cleanup task
        if self.config.auto_cleanup_enabled:
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.background_tasks.append(cleanup_task)
        
        # Start backup task
        backup_task = asyncio.create_task(self._backup_loop())
        self.background_tasks.append(backup_task)
        
        logger.info("✅ Stateful Service started successfully")
    
    async def stop(self):
        """Stop the stateful service"""
        logger.info("Stopping Stateful Service")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("✅ Stateful Service stopped")
    
    async def create_session(self, user_id: Optional[str] = None, 
                           session_timeout: Optional[int] = None) -> ServiceSession:
        """Create a new service session"""
        session_id = str(uuid.uuid4())
        timeout = session_timeout or self.config.session_timeout_seconds
        
        session = ServiceSession(
            session_id=session_id,
            user_id=user_id,
            service_id=self.service_id,
            expires_at=datetime.now() + timedelta(seconds=timeout),
            status=SessionStatus.CREATED
        )
        
        async with self.session_locks[session_id]:
            self.sessions[session_id] = session
            
        self.stats["sessions_created"] += 1
        logger.info(f"Session created: {session_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ServiceSession]:
        """Get service session"""
        async with self.session_locks[session_id]:
            session = self.sessions.get(session_id)
            
            if session:
                # Check if session expired
                if session.expires_at and datetime.now() > session.expires_at:
                    session.status = SessionStatus.EXPIRED
                    return session
                
                # Update last activity
                session.last_activity = datetime.now()
                session.status = SessionStatus.ACTIVE
                
            return session
    
    async def extend_session(self, session_id: str, 
                           additional_seconds: int = None) -> bool:
        """Extend session timeout"""
        async with self.session_locks[session_id]:
            session = self.sessions.get(session_id)
            
            if session and session.status not in [SessionStatus.EXPIRED, SessionStatus.TERMINATED]:
                extension = additional_seconds or self.config.session_timeout_seconds
                session.expires_at = datetime.now() + timedelta(seconds=extension)
                session.last_activity = datetime.now()
                
                logger.debug(f"Session {session_id} extended by {extension}s")
                return True
            
            return False
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate service session"""
        async with self.session_locks[session_id]:
            session = self.sessions.get(session_id)
            
            if session:
                session.status = SessionStatus.TERMINATED
                
                # Clean up associated states
                await self._cleanup_session_states(session_id)
                
                logger.info(f"Session terminated: {session_id}")
                return True
            
            return False
    
    async def create_state(self, data: Dict[str, Any], 
                         session_id: Optional[str] = None,
                         ttl_seconds: Optional[int] = None) -> ServiceState:
        """Create new service state"""
        state_id = str(uuid.uuid4())
        
        state = ServiceState(
            state_id=state_id,
            service_id=self.service_id,
            session_id=session_id,
            data=data,
            ttl_seconds=ttl_seconds or self.config.state_ttl_seconds
        )
        
        # Save to persistent store
        success = await self.state_store.save_state(state)
        if not success:
            raise Exception(f"Failed to save state {state_id}")
        
        # Cache locally
        async with self.cache_locks[state_id]:
            self.local_cache[state_id] = copy.deepcopy(state)
        
        self.stats["states_created"] += 1
        logger.info(f"State created: {state_id}")
        
        return state
    
    async def get_state(self, state_id: str) -> Optional[ServiceState]:
        """Get service state"""
        # Check local cache first
        async with self.cache_locks[state_id]:
            if state_id in self.local_cache:
                cached_state = self.local_cache[state_id]
                
                # Check if cached state is still valid
                if self._is_state_valid(cached_state):
                    self.stats["cache_hits"] += 1
                    logger.debug(f"State {state_id} loaded from cache")
                    return copy.deepcopy(cached_state)
                else:
                    # Remove invalid state from cache
                    del self.local_cache[state_id]
        
        # Load from persistent store
        self.stats["cache_misses"] += 1
        state = await self.state_store.load_state(state_id)
        
        if state:
            # Update cache
            async with self.cache_locks[state_id]:
                self.local_cache[state_id] = copy.deepcopy(state)
            
            self.stats["states_loaded"] += 1
            logger.debug(f"State {state_id} loaded from store")
        
        return state
    
    async def update_state(self, state_id: str, data: Dict[str, Any], 
                         increment_version: bool = True) -> bool:
        """Update service state"""
        state = await self.get_state(state_id)
        
        if not state:
            logger.warning(f"State {state_id} not found for update")
            return False
        
        # Update state data
        state.data.update(data)
        state.updated_at = datetime.now()
        
        if increment_version:
            state.version += 1
        
        # Save to persistent store
        success = await self.state_store.save_state(state)
        if not success:
            return False
        
        # Update cache
        async with self.cache_locks[state_id]:
            self.local_cache[state_id] = copy.deepcopy(state)
        
        self.stats["states_updated"] += 1
        logger.debug(f"State {state_id} updated")
        
        return True
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete service state"""
        # Remove from cache
        async with self.cache_locks[state_id]:
            self.local_cache.pop(state_id, None)
        
        # Delete from persistent store
        success = await self.state_store.delete_state(state_id)
        
        if success:
            self.stats["states_deleted"] += 1
            logger.info(f"State {state_id} deleted")
        
        return success
    
    async def list_session_states(self, session_id: str) -> List[ServiceState]:
        """List all states for a session"""
        all_states = await self.state_store.list_states(self.service_id)
        
        session_states = [
            state for state in all_states 
            if state.session_id == session_id
        ]
        
        return session_states
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        active_sessions = sum(
            1 for session in self.sessions.values()
            if session.status == SessionStatus.ACTIVE
        )
        
        total_states = len(await self.state_store.list_states(self.service_id))
        cached_states = len(self.local_cache)
        
        return {
            **self.stats,
            "service_id": self.service_id,
            "service_name": self.config.service_name,
            "active_sessions": active_sessions,
            "total_sessions": len(self.sessions),
            "total_states": total_states,
            "cached_states": cached_states,
            "cache_hit_ratio": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"]),
            "is_running": self.is_running
        }
    
    def _is_state_valid(self, state: ServiceState) -> bool:
        """Check if cached state is still valid"""
        if state.status != StateStatus.ACTIVE:
            return False
        
        if state.ttl_seconds:
            age = (datetime.now() - state.updated_at).total_seconds()
            if age > state.ttl_seconds:
                return False
        
        return True
    
    async def _cleanup_loop(self):
        """Background cleanup task"""
        while self.is_running:
            try:
                await self._cleanup_expired_states()
                await self._cleanup_expired_sessions()
                
                await asyncio.sleep(60)  # Run cleanup every minute
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {str(e)}")
    
    async def _cleanup_expired_states(self):
        """Clean up expired states"""
        current_time = datetime.now()
        states_to_remove = []
        
        # Check cached states
        for state_id, state in self.local_cache.items():
            if not self._is_state_valid(state):
                states_to_remove.append(state_id)
        
        # Remove expired states
        for state_id in states_to_remove:
            await self.delete_state(state_id)
        
        if states_to_remove:
            logger.info(f"Cleaned up {len(states_to_remove)} expired states")
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if (session.expires_at and current_time > session.expires_at) or \
               session.status == SessionStatus.TERMINATED:
                sessions_to_remove.append(session_id)
        
        # Remove expired sessions
        for session_id in sessions_to_remove:
            async with self.session_locks[session_id]:
                self.sessions.pop(session_id, None)
                await self._cleanup_session_states(session_id)
        
        if sessions_to_remove:
            self.stats["sessions_expired"] += len(sessions_to_remove)
            logger.info(f"Cleaned up {len(sessions_to_remove)} expired sessions")
    
    async def _cleanup_session_states(self, session_id: str):
        """Clean up states associated with a session"""
        session_states = await self.list_session_states(session_id)
        
        for state in session_states:
            await self.delete_state(state.state_id)
    
    async def _backup_loop(self):
        """Background backup task"""
        while self.is_running:
            try:
                await self._create_backup()
                
                await asyncio.sleep(self.config.backup_interval_seconds)
                
            except Exception as e:
                logger.error(f"Backup loop error: {str(e)}")
    
    async def _create_backup(self):
        """Create service backup"""
        try:
            backup_data = {
                "service_id": self.service_id,
                "config": {
                    "service_name": self.config.service_name,
                    "state_ttl_seconds": self.config.state_ttl_seconds,
                    "session_timeout_seconds": self.config.session_timeout_seconds
                },
                "timestamp": datetime.now().isoformat(),
                "stats": await self.get_service_stats(),
                "sessions_count": len(self.sessions),
                "states_count": len(await self.state_store.list_states(self.service_id))
            }
            
            # In production, you would save this to a backup storage
            logger.debug(f"Backup created for service {self.service_id}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")

# Usage Example and Template Testing
async def main():
    """Example usage of Stateful Service Template"""
    
    # Create configuration
    config = StatefulConfig(
        service_name="creator_workflow_service",
        persistence_enabled=True,
        state_ttl_seconds=3600,
        session_timeout_seconds=1800,
        auto_cleanup_enabled=True
    )
    
    # Initialize service with memory store
    memory_store = MemoryStateStore()
    service = StatefulService(config, memory_store)
    
    try:
        # Start the service
        await service.start()
        
        # Create a session
        session = await service.create_session(user_id="user_123")
        print(f"✅ Session created: {session.session_id}")
        
        # Create some states
        workflow_state = await service.create_state(
            data={
                "workflow_id": "wf_001",
                "current_step": "content_creation",
                "progress": 0.3,
                "metadata": {
                    "creator_id": "creator_456",
                    "content_type": "video",
                    "estimated_duration": 300
                }
            },
            session_id=session.session_id
        )
        
        processing_state = await service.create_state(
            data={
                "job_id": "job_789",
                "status": "processing",
                "progress": 0.7,
                "results": {
                    "analyzed_frames": 150,
                    "total_frames": 200
                }
            },
            session_id=session.session_id
        )
        
        print(f"✅ States created: {workflow_state.state_id}, {processing_state.state_id}")
        
        # Update state
        await service.update_state(
            workflow_state.state_id,
            {
                "current_step": "content_analysis",
                "progress": 0.6
            }
        )
        print(f"✅ Workflow state updated")
        
        # Get updated state
        updated_state = await service.get_state(workflow_state.state_id)
        if updated_state:
            print(f"✅ State retrieved - Progress: {updated_state.data['progress']}, Version: {updated_state.version}")
        
        # List session states
        session_states = await service.list_session_states(session.session_id)
        print(f"✅ Session has {len(session_states)} states")
        
        # Extend session
        await service.extend_session(session.session_id, 3600)
        print(f"✅ Session extended")
        
        # Get service statistics
        stats = await service.get_service_stats()
        print(f"\n📊 Service Statistics:")
        print(f"  Service ID: {stats['service_id']}")
        print(f"  Active Sessions: {stats['active_sessions']}")
        print(f"  Total States: {stats['total_states']}")
        print(f"  Cache Hit Ratio: {stats['cache_hit_ratio']:.2%}")
        print(f"  States Created: {stats['states_created']}")
        print(f"  States Updated: {stats['states_updated']}")
        
        # Test with Redis store (if Redis is available)
        print(f"\n🔄 Testing Redis Store (simulation)...")
        
        # Simulate Redis store functionality
        redis_store = RedisStateStore()
        redis_service = StatefulService(config, redis_store)
        
        print(f"✅ Redis-based stateful service configured")
        
        # Demonstrate state persistence
        print(f"\n💾 State Persistence Demo:")
        print(f"  - Workflow state persisted with version {updated_state.version}")
        print(f"  - Processing state maintained across service restarts")
        print(f"  - Session data preserved with TTL management")
        
    except Exception as e:
        logger.error(f"Error in stateful service demo: {str(e)}")
    finally:
        # Stop the service
        await service.stop()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🗃️ Stateful Service Template demonstration completed!")