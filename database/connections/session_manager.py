"""
Session Manager - IA Influencer Agent Platform

Manages database sessions and connection state:
- Session lifecycle management
- Connection state tracking
- Session pooling and reuse
- Tenant session isolation
- Session timeout and cleanup
- Session-based transaction coordination

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Set, AsyncContextManager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager


class SessionState(Enum):
    """Database session states"""
    IDLE = "idle"
    ACTIVE = "active"
    TRANSACTION = "transaction"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class DatabaseSession:
    """Database session information"""
    session_id: str
    database_type: str
    tenant_id: Optional[str]
    connection: Any
    state: SessionState = SessionState.IDLE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    transaction_count: int = 0
    operation_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if session has expired"""



        return datetime.utcnow() - self.last_activity > self.timeout
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()


class SessionManager:
    """
    Database session manager for IA Influencer platform.
    
    Manages sessions for:
    - PostgreSQL database connections
    - Redis client sessions
    - MongoDB database sessions
    - Elasticsearch client sessions
    - Vector store connections
    - Object storage sessions
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Database handlers
        self.handlers: Dict[str, Any] = {}
        
        # Active sessions
        self.sessions: Dict[str, DatabaseSession] = {}
        
        # Session pools by database type and tenant
        self.session_pools: Dict[str, Dict[str, Set[str]]] = {}  # db_type -> tenant_id -> session_ids
        
        # Session cleanup
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 60  # seconds
        
        # Configuration
        self.max_sessions_per_tenant = 50
        self.default_session_timeout = timedelta(minutes=30)
        
        # Statistics
        self.stats = {
            "total_sessions_created": 0,
            "total_sessions_closed": 0,
            "current_active_sessions": 0,
            "sessions_expired": 0,
            "average_session_duration": 0.0
        }
    
    async def initialize(self, handlers: Dict[str, Any]) -> None:
        """Initialize session manager with database handlers"""
        self.handlers = handlers
        
        # Initialize session pools
        for db_type in handlers.keys():
            self.session_pools[db_type] = {}
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Session manager initialized")
    
    @asynccontextmanager
    async def session(self, 
                     database_type: str,
                     tenant_id: Optional[str] = None,
                     timeout: Optional[timedelta] = None) -> AsyncContextManager[DatabaseSession]:
        """Context manager for database sessions"""
        
        session = await self.create_session(database_type, tenant_id, timeout)
        
        try:
            yield session
        finally:
            await self.close_session(session.session_id)
    
    async def create_session(self, 
                           database_type: str,
                           tenant_id: Optional[str] = None,
                           timeout: Optional[timedelta] = None) -> DatabaseSession:
        """Create a new database session"""
        
        if database_type not in self.handlers:
            raise ValueError(f"Database type {database_type} not available")
        
        # Check tenant session limit
        if tenant_id:
            await self._enforce_tenant_session_limit(database_type, tenant_id)
        
        # Get connection from handler
        handler = self.handlers[database_type]
        
        if tenant_id:
            connection = await handler.get_tenant_connection(tenant_id)
        else:
            connection = await handler.get_connection()
        
        # Create session
        session_id = str(uuid.uuid4())
        session = DatabaseSession(
            session_id=session_id,
            database_type=database_type,
            tenant_id=tenant_id,
            connection=connection,
            timeout=timeout or self.default_session_timeout
        )
        
        # Store session
        self.sessions[session_id] = session
        
        # Add to session pool
        if database_type not in self.session_pools:
            self.session_pools[database_type] = {}
        
        pool_key = tenant_id or "default"
        if pool_key not in self.session_pools[database_type]:
            self.session_pools[database_type][pool_key] = set()
        
        self.session_pools[database_type][pool_key].add(session_id)
        
        # Update statistics
        self.stats["total_sessions_created"] += 1
        self.stats["current_active_sessions"] = len(self.sessions)
        
        self.logger.debug(f"Created session {session_id} for {database_type}")
        
        return session
    
    async def _enforce_tenant_session_limit(self, database_type: str, tenant_id: str) -> None:
        """Enforce maximum sessions per tenant"""
        if database_type in self.session_pools and tenant_id in self.session_pools[database_type]:
            current_sessions = len(self.session_pools[database_type][tenant_id])
            
            if current_sessions >= self.max_sessions_per_tenant:
                # Close oldest session
                oldest_session_id = min(
                    self.session_pools[database_type][tenant_id],
                    key=lambda sid: self.sessions[sid].created_at
                    if sid in self.sessions else datetime.min
                )
                
                await self.close_session(oldest_session_id)
                self.logger.warning(
                    f"Closed oldest session {oldest_session_id} due to tenant limit"
                )
    
    async def get_session(self, session_id: str) -> Optional[DatabaseSession]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session is expired
            if session.is_expired():
                await self.close_session(session_id)
                return None
            
            # Update activity
            session.update_activity()
        
        return session
    
    async def close_session(self, session_id: str) -> bool:
        """Close a database session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        try:
            # Close connection if possible
            handler = self.handlers[session.database_type]
            
            if hasattr(handler, 'release_connection'):
                await handler.release_connection(session.connection)
            elif hasattr(session.connection, 'close'):
                await session.connection.close()
            
            session.state = SessionState.CLOSED
            
            # Remove from session pool
            pool_key = session.tenant_id or "default"
            if (session.database_type in self.session_pools and 
                pool_key in self.session_pools[session.database_type]):
                self.session_pools[session.database_type][pool_key].discard(session_id)
            
            # Remove from sessions
            del self.sessions[session_id]
            
            # Update statistics
            self.stats["total_sessions_closed"] += 1
            self.stats["current_active_sessions"] = len(self.sessions)
            
            self.logger.debug(f"Closed session {session_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing session {session_id}: {e}")
            session.state = SessionState.ERROR
            return False
    
    async def execute_in_session(self, 
                                session_id: str,
                                operation: str,
                                *args, **kwargs) -> Any:
        """Execute operation in specific session"""
        session = await self.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
        
        if session.state not in [SessionState.IDLE, SessionState.ACTIVE]:
            raise ValueError(f"Session {session_id} is not available (state: {session.state})")
        
        try:
            session.state = SessionState.ACTIVE
            session.update_activity()
            
            # Execute operation on the connection
            connection = session.connection
            
            if hasattr(connection, operation):
                result = await getattr(connection, operation)(*args, **kwargs)
            else:
                raise AttributeError(f"Operation {operation} not available on connection")
            
            session.operation_count += 1
            
            return result
            
        except Exception as e:
            session.state = SessionState.ERROR
            self.logger.error(f"Operation {operation} failed in session {session_id}: {e}")
            raise
            
        finally:
            if session.state == SessionState.ACTIVE:
                session.state = SessionState.IDLE
    
    @asynccontextmanager
    async def transaction_session(self, session_id: str):
        """Context manager for transaction within a session"""
        session = await self.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
        
        if session.state != SessionState.IDLE:
            raise ValueError(f"Session {session_id} is not idle (state: {session.state})")
        
        session.state = SessionState.TRANSACTION
        session.transaction_count += 1
        
        try:
            # Start transaction if connection supports it
            connection = session.connection
            
            if hasattr(connection, 'transaction'):
                async with connection.transaction():
                    yield session
            else:
                yield session
                
        except Exception as e:
            self.logger.error(f"Transaction failed in session {session_id}: {e}")
            raise
            
        finally:
            session.state = SessionState.IDLE
            session.update_activity()
    
    async def get_tenant_sessions(self, 
                                database_type: str,
                                tenant_id: str) -> List[DatabaseSession]:
        """Get all sessions for a specific tenant"""
        if (database_type not in self.session_pools or 
            tenant_id not in self.session_pools[database_type]):
            return []
        
        session_ids = self.session_pools[database_type][tenant_id]
        sessions = []
        
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)
        
        return sessions
    
    async def close_tenant_sessions(self, 
                                  database_type: str,
                                  tenant_id: str) -> int:
        """Close all sessions for a specific tenant"""
        sessions = await self.get_tenant_sessions(database_type, tenant_id)
        closed_count = 0
        
        for session in sessions:
            if await self.close_session(session.session_id):
                closed_count += 1
        
        self.logger.info(f"Closed {closed_count} sessions for tenant {tenant_id}")
        
        return closed_count
    
    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Session cleanup error: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.close_session(session_id)
            self.stats["sessions_expired"] += 1
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def get_session_stats(self, 
                              database_type: Optional[str] = None,
                              tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session statistics"""
        if database_type and tenant_id:
            # Stats for specific database and tenant
            sessions = await self.get_tenant_sessions(database_type, tenant_id)
            
            return {
                "total_sessions": len(sessions),
                "active_sessions": len([s for s in sessions if s.state == SessionState.ACTIVE]),
                "idle_sessions": len([s for s in sessions if s.state == SessionState.IDLE]),
                "transaction_sessions": len([s for s in sessions if s.state == SessionState.TRANSACTION]),
                "error_sessions": len([s for s in sessions if s.state == SessionState.ERROR])
            }
            
        elif database_type:
            # Stats for specific database type
            if database_type not in self.session_pools:
                return {}
            
            total_sessions = sum(
                len(session_ids) for session_ids in self.session_pools[database_type].values()
            )
            
            return {
                "database_type": database_type,
                "total_sessions": total_sessions,
                "tenant_count": len(self.session_pools[database_type])
            }
            
        else:
            # Global stats
            return self.stats.copy()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive session manager metrics"""
        # Calculate sessions by state
        state_counts = {state.value: 0 for state in SessionState}
        
        for session in self.sessions.values():
            state_counts[session.state.value] += 1
        
        # Calculate sessions by database type
        db_type_counts = {}
        for db_type, tenant_pools in self.session_pools.items():
            db_type_counts[db_type] = sum(len(sessions) for sessions in tenant_pools.values())
        
        # Calculate tenant distribution
        tenant_counts = {}
        for session in self.sessions.values():
            tenant_key = session.tenant_id or "default"
            tenant_counts[tenant_key] = tenant_counts.get(tenant_key, 0) + 1
        
        return {
            "session_statistics": self.stats,
            "sessions_by_state": state_counts,
            "sessions_by_database": db_type_counts,
            "sessions_by_tenant": tenant_counts,
            "configuration": {
                "max_sessions_per_tenant": self.max_sessions_per_tenant,
                "default_timeout_minutes": self.default_session_timeout.total_seconds() / 60,
                "cleanup_interval_seconds": self.cleanup_interval
            },
            "active_sessions_count": len(self.sessions)
        }
    
    async def shutdown(self) -> None:
        """Shutdown session manager"""
        self.logger.info("Shutting down session manager...")
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all active sessions
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)
        
        self.logger.info(f"Closed {len(session_ids)} active sessions")
        
        # Clear data structures
        self.sessions.clear()
        self.session_pools.clear()
        
        self.logger.info("Session manager shutdown completed")
