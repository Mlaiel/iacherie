"""Session Controller - Advanced session management for chat orchestration
======================================================================

Manages chat session lifecycle, persistence, and state management with
high-performance caching and database integration.

Author: Fahed Mlaiel <mlaiel@live.de>
"""import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import asdict
import pickle

from backend.core.database import DatabaseManager
from backend.core.cache import CacheManager
from backend.core.config import settings


class SessionController:
    """    Advanced session controller managing chat session persistence,
    state management, and performance optimization through intelligent
    caching strategies.
    """    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db = db_manager
        self.cache = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # Session configuration
        self.default_session_ttl = 24 * 3600  # 24 hours in seconds
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.max_sessions_per_user = 10
        self.session_cleanup_interval = 300  # 5 minutes
        
        # Performance metrics
        self.metrics = {
            "sessions_created": 0,
            "sessions_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cleanup_runs": 0
        }
        
    async def save_session(self, session: Any) -> bool:
        """        Save chat session to database and cache
        
        Args:
            session: ChatSession object to save
            
        Returns:
            bool: Success status
        """        try:
            # Convert session to dictionary for storage
            session_data = self._serialize_session(session)
            
            # Save to database
            db_success = await self._save_to_database(session.session_id, session_data)
            if not db_success:
                self.logger.error(f"Failed to save session {session.session_id} to database")
                return False
            
            # Save to cache for quick access
            cache_success = await self._save_to_cache(session.session_id, session_data)
            if not cache_success:
                self.logger.warning(f"Failed to cache session {session.session_id}")
            
            # Update user session index
            await self._update_user_session_index(session.user_id, session.session_id)
            
            # Update metrics
            self.metrics["sessions_created"] += 1
            
            self.logger.info(f"Successfully saved session {session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {str(e)}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Any]:
        """        Retrieve chat session from cache or database
        
        Args:
            session_id: Session identifier
            
        Returns:
            ChatSession object or None if not found
        """        try:
            # Try cache first
            session_data = await self._get_from_cache(session_id)
            
            if session_data:
                self.metrics["cache_hits"] += 1
                session = self._deserialize_session(session_data)
                self.logger.debug(f"Retrieved session {session_id} from cache")
                return session
            
            # Cache miss - try database
            self.metrics["cache_misses"] += 1
            session_data = await self._get_from_database(session_id)
            
            if session_data:
                # Restore to cache
                await self._save_to_cache(session_id, session_data)
                session = self._deserialize_session(session_data)
                self.logger.debug(f"Retrieved session {session_id} from database")
                return session
            
            self.logger.debug(f"Session {session_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
    
    async def update_session(self, session: Any) -> bool:
        """        Update existing session in database and cache
        
        Args:
            session: Updated ChatSession object
            
        Returns:
            bool: Success status
        """        try:
            # Update timestamp
            session.updated_at = datetime.utcnow()
            
            # Save updated session
            return await self.save_session(session)
            
        except Exception as e:
            self.logger.error(f"Failed to update session {session.session_id}: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """        Delete session from database and cache
        
        Args:
            session_id: Session to delete
            
        Returns:
            bool: Success status
        """        try:
            # Get session first to get user_id
            session_data = await self._get_from_database(session_id)
            user_id = None
            if session_data:
                user_id = session_data.get("user_id")
            
            # Delete from database
            db_success = await self._delete_from_database(session_id)
            
            # Delete from cache
            cache_success = await self._delete_from_cache(session_id)
            
            # Update user session index
            if user_id:
                await self._remove_from_user_session_index(user_id, session_id)
            
            success = db_success and cache_success
            if success:
                self.logger.info(f"Successfully deleted session {session_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """        Get all sessions for a specific user
        
        Args:
            user_id: User identifier
            active_only: Only return active sessions
            limit: Maximum sessions to return
            offset: Pagination offset
            
        Returns:
            List of session summaries
        """        try:
            # Get session IDs from user index
            session_ids = await self._get_user_session_ids(user_id)
            
            if not session_ids:
                return []
            
            # Apply pagination
            paginated_ids = session_ids[offset:offset + limit]
            
            # Retrieve session data
            sessions = []
            for session_id in paginated_ids:
                session_data = await self._get_from_cache(session_id)
                if not session_data:
                    session_data = await self._get_from_database(session_id)
                
                if session_data:
                    # Filter by active status if requested
                    if active_only and session_data.get("status") != "active":
                        continue
                    
                    # Create session summary
                    session_summary = {
                        "session_id": session_id,
                        "creator_type": session_data.get("creator_type"),
                        "status": session_data.get("status"),
                        "message_count": len(session_data.get("messages", [])),
                        "created_at": session_data.get("created_at"),
                        "updated_at": session_data.get("updated_at"),
                        "expires_at": session_data.get("expires_at")
                    }
                    sessions.append(session_summary)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions for {user_id}: {str(e)}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """        Clean up expired sessions from database and cache
        
        Returns:
            int: Number of sessions cleaned up
        """        try:
            current_time = datetime.utcnow()
            cleanup_count = 0
            
            # Query expired sessions from database
            expired_sessions = await self._get_expired_sessions(current_time)
            
            for session_data in expired_sessions:
                session_id = session_data.get("session_id")
                if session_id:
                    success = await self.delete_session(session_id)
                    if success:
                        cleanup_count += 1
            
            # Update metrics
            self.metrics["cleanup_runs"] += 1
            
            if cleanup_count > 0:
                self.logger.info(f"Cleaned up {cleanup_count} expired sessions")
            
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """        Get session management statistics
        
        Returns:
            Dict with various statistics
        """        try:
            stats = {
                "total_active_sessions": await self._count_active_sessions(),
                "sessions_by_creator_type": await self._count_sessions_by_creator_type(),
                "average_session_duration": await self._calculate_average_session_duration(),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "performance_metrics": self.metrics.copy()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get session statistics: {str(e)}")
            return {}
    
    async def validate_session_access(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """        Validate that user has access to specific session
        
        Args:
            session_id: Session to validate
            user_id: User requesting access
            
        Returns:
            bool: Access granted status
        """        try:
            session_data = await self._get_from_cache(session_id)
            if not session_data:
                session_data = await self._get_from_database(session_id)
            
            if not session_data:
                return False
            
            # Check if user owns the session
            return session_data.get("user_id") == user_id
            
        except Exception as e:
            self.logger.error(f"Failed to validate session access: {str(e)}")
            return False
    
    def _serialize_session(self, session: Any) -> Dict[str, Any]:
        """Convert session object to dictionary for storage"""        try:
            # Convert session object to dictionary
            if hasattr(session, '__dict__'):
                session_dict = {}
                for key, value in session.__dict__.items():
                    if isinstance(value, datetime):
                        session_dict[key] = value.isoformat()
                    elif hasattr(value, 'value'):  # Enum values
                        session_dict[key] = value.value
                    else:
                        session_dict[key] = value
                return session_dict
            else:
                return asdict(session)
                
        except Exception as e:
            self.logger.error(f"Failed to serialize session: {str(e)}")
            return {}
    
    def _deserialize_session(self, session_data: Dict[str, Any]) -> Any:
        """Convert dictionary back to session object"""        try:
            # Import here to avoid circular imports
            from .chat_manager import ChatSession, ChatStatus, CreatorType
            
            # Convert datetime strings back to datetime objects
            for datetime_field in ["created_at", "updated_at", "expires_at"]:
                if datetime_field in session_data and session_data[datetime_field]:
                    if isinstance(session_data[datetime_field], str):
                        session_data[datetime_field] = datetime.fromisoformat(
                            session_data[datetime_field]
                        )
            
            # Convert enum strings back to enum objects
            if "status" in session_data:
                session_data["status"] = ChatStatus(session_data["status"])
            
            if "creator_type" in session_data:
                session_data["creator_type"] = CreatorType(session_data["creator_type"])
            
            # Create session object
            return ChatSession(**session_data)
            
        except Exception as e:
            self.logger.error(f"Failed to deserialize session: {str(e)}")
            return None
    
    async def _save_to_database(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session to database"""        try:
            query = """                INSERT INTO chat_sessions (
                    session_id, user_id, creator_type, status, context,
                    messages, metadata, created_at, updated_at, expires_at
                ) VALUES (
                    %(session_id)s, %(user_id)s, %(creator_type)s, %(status)s, %(context)s,
                    %(messages)s, %(metadata)s, %(created_at)s, %(updated_at)s, %(expires_at)s
                )
                ON CONFLICT (session_id) DO UPDATE SET
                    status = %(status)s,
                    context = %(context)s,
                    messages = %(messages)s,
                    metadata = %(metadata)s,
                    updated_at = %(updated_at)s,
                    expires_at = %(expires_at)s
            """            
            params = {
                "session_id": session_id,
                "user_id": session_data.get("user_id"),
                "creator_type": session_data.get("creator_type"),
                "status": session_data.get("status"),
                "context": json.dumps(session_data.get("context", {})),
                "messages": json.dumps(session_data.get("messages", [])),
                "metadata": json.dumps(session_data.get("metadata", {})),
                "created_at": session_data.get("created_at"),
                "updated_at": session_data.get("updated_at"),
                "expires_at": session_data.get("expires_at")
            }
            
            await self.db.execute_query(query, params)
            return True
            
        except Exception as e:
            self.logger.error(f"Database save failed for session {session_id}: {str(e)}")
            return False
    
    async def _get_from_database(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from database"""        try:
            query = """                SELECT session_id, user_id, creator_type, status, context,
                       messages, metadata, created_at, updated_at, expires_at
                FROM chat_sessions
                WHERE session_id = %(session_id)s
            """            
            result = await self.db.fetch_one(query, {"session_id": session_id})
            
            if result:
                # Parse JSON fields
                session_data = dict(result)
                session_data["context"] = json.loads(session_data["context"] or "{}")
                session_data["messages"] = json.loads(session_data["messages"] or "[]")
                session_data["metadata"] = json.loads(session_data["metadata"] or "{}")
                
                return session_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Database get failed for session {session_id}: {str(e)}")
            return None
    
    async def _delete_from_database(self, session_id: str) -> bool:
        """Delete session from database"""        try:
            query = "DELETE FROM chat_sessions WHERE session_id = %(session_id)s"
            await self.db.execute_query(query, {"session_id": session_id})
            return True
            
        except Exception as e:
            self.logger.error(f"Database delete failed for session {session_id}: {str(e)}")
            return False
    
    async def _save_to_cache(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session to cache"""        try:
            cache_key = f"chat_session:{session_id}"
            serialized_data = pickle.dumps(session_data)
            await self.cache.set(cache_key, serialized_data, expire=self.cache_ttl)
            return True
            
        except Exception as e:
            self.logger.error(f"Cache save failed for session {session_id}: {str(e)}")
            return False
    
    async def _get_from_cache(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from cache"""        try:
            cache_key = f"chat_session:{session_id}"
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                return pickle.loads(cached_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get failed for session {session_id}: {str(e)}")
            return None
    
    async def _delete_from_cache(self, session_id: str) -> bool:
        """Delete session from cache"""        try:
            cache_key = f"chat_session:{session_id}"
            await self.cache.delete(cache_key)
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete failed for session {session_id}: {str(e)}")
            return False
    
    async def _update_user_session_index(self, user_id: str, session_id: str):
        """Update user session index for quick lookup"""        try:
            cache_key = f"user_sessions:{user_id}"
            existing_sessions = await self.cache.get(cache_key) or []
            
            if isinstance(existing_sessions, bytes):
                existing_sessions = pickle.loads(existing_sessions)
            
            if session_id not in existing_sessions:
                existing_sessions.append(session_id)
                # Keep only recent sessions (last 50)
                existing_sessions = existing_sessions[-50:]
                
                serialized_sessions = pickle.dumps(existing_sessions)
                await self.cache.set(cache_key, serialized_sessions, expire=86400)  # 24 hours
                
        except Exception as e:
            self.logger.error(f"Failed to update user session index: {str(e)}")
    
    async def _remove_from_user_session_index(self, user_id: str, session_id: str):
        """Remove session from user index"""        try:
            cache_key = f"user_sessions:{user_id}"
            existing_sessions = await self.cache.get(cache_key) or []
            
            if isinstance(existing_sessions, bytes):
                existing_sessions = pickle.loads(existing_sessions)
            
            if session_id in existing_sessions:
                existing_sessions.remove(session_id)
                serialized_sessions = pickle.dumps(existing_sessions)
                await self.cache.set(cache_key, serialized_sessions, expire=86400)
                
        except Exception as e:
            self.logger.error(f"Failed to remove from user session index: {str(e)}")
    
    async def _get_user_session_ids(self, user_id: str) -> List[str]:
        """Get session IDs for user"""        try:
            cache_key = f"user_sessions:{user_id}"
            cached_sessions = await self.cache.get(cache_key)
            
            if cached_sessions:
                if isinstance(cached_sessions, bytes):
                    return pickle.loads(cached_sessions)
                return cached_sessions
            
            # Fallback to database query
            query = """                SELECT session_id FROM chat_sessions 
                WHERE user_id = %(user_id)s 
                ORDER BY updated_at DESC
                LIMIT 50
            """            
            results = await self.db.fetch_all(query, {"user_id": user_id})
            session_ids = [row["session_id"] for row in results]
            
            # Cache the result
            serialized_sessions = pickle.dumps(session_ids)
            await self.cache.set(cache_key, serialized_sessions, expire=86400)
            
            return session_ids
            
        except Exception as e:
            self.logger.error(f"Failed to get user session IDs: {str(e)}")
            return []
    
    async def _get_expired_sessions(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Get expired sessions from database"""        try:
            query = """                SELECT session_id, user_id FROM chat_sessions
                WHERE expires_at < %(current_time)s
                ORDER BY expires_at ASC
                LIMIT 1000
            """            
            results = await self.db.fetch_all(query, {"current_time": current_time})
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Failed to get expired sessions: {str(e)}")
            return []
    
    async def _count_active_sessions(self) -> int:
        """Count active sessions"""        try:
            query = "SELECT COUNT(*) as count FROM chat_sessions WHERE status = 'active'"
            result = await self.db.fetch_one(query)
            return result["count"] if result else 0
            
        except Exception as e:
            self.logger.error(f"Failed to count active sessions: {str(e)}")
            return 0
    
    async def _count_sessions_by_creator_type(self) -> Dict[str, int]:
        """Count sessions by creator type"""        try:
            query = """                SELECT creator_type, COUNT(*) as count 
                FROM chat_sessions 
                WHERE status = 'active'
                GROUP BY creator_type
            """            
            results = await self.db.fetch_all(query)
            return {row["creator_type"]: row["count"] for row in results}
            
        except Exception as e:
            self.logger.error(f"Failed to count sessions by creator type: {str(e)}")
            return {}
    
    async def _calculate_average_session_duration(self) -> float:
        """Calculate average session duration in minutes"""        try:
            query = """                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60) as avg_duration
                FROM chat_sessions
                WHERE status IN ('ended', 'active')
                AND updated_at > created_at
            """            
            result = await self.db.fetch_one(query)
            return float(result["avg_duration"]) if result and result["avg_duration"] else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate average session duration: {str(e)}")
            return 0.0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_requests == 0:
            return 0.0
        
        return (self.metrics["cache_hits"] / total_requests) * 100
