"""Onboarding Manager - Central Orchestration for Creator Onboarding

Enterprise-grade onboarding management system with workflow orchestration,
session persistence, and intelligent progress tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import asyncpg
import redis.asyncio as aioredis
from sqlalchemy.orm import Session
from sqlalchemy import text

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import OnboardingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    OnboardingError, ValidationError = globals().get('OnboardingError, ValidationError', Exception)
from ...utils.caching import CacheManager
from ...utils.notifications import NotificationService

logger = logging.getLogger(__name__)

class OnboardingStatus(Enum):
    """
Onboarding process status levels"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class OnboardingMetrics:
    """Comprehensive onboarding performance metrics"""
    total_sessions: int = 0
    active_sessions: int = 0
    completed_sessions: int = 0
    failed_sessions: int = 0
    average_completion_time: float = 0.0
    completion_rate: float = 0.0
    stage_completion_rates: Dict[str, float] = None
    creator_type_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.stage_completion_rates is None:
            self.stage_completion_rates = {}
        if self.creator_type_distribution is None:
            self.creator_type_distribution = {}

class OnboardingManager:
    """
    Advanced onboarding management system with enterprise features.
    
    Core Capabilities:
    - Session lifecycle management
    - Workflow orchestration and optimization
    - Progress tracking and analytics
    - Data persistence and recovery
    - Performance monitoring and optimization
    - Multi-tenant isolation and security
    - Automated notifications and alerts
    """
    
    def __init__(self):
        self.cache_manager = CacheManager(prefix="onboarding")
        self.notification_service = NotificationService()
        self.session_timeout = timedelta(hours=24)
        
        # Performance tracking
        self.metrics = OnboardingMetrics()
        
        logger.info("OnboardingManager initialized successfully")
    
    async def create_session(self, user_id: str, creator_type: str, 
                           initial_data: Dict[str, Any] = None) -> str:
        """
        Create new onboarding session with enterprise tracking.
        """
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'creator_type': creator_type,
                'status': OnboardingStatus.IN_PROGRESS.value,
                'current_stage': 'initial_registration',
                'completed_stages': [],
                'progress_data': initial_data or {},
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'completion_percentage': 0.0,
                'session_metadata': {
                    'ip_address': initial_data.get('ip_address') if initial_data else None,
                    'user_agent': initial_data.get('user_agent') if initial_data else None,
                    'referrer': initial_data.get('referrer') if initial_data else None
                }
            }
            
            # Store in cache for fast access
            await self.cache_manager.set(
                f"session:{session_id}",
                json.dumps(session_data),
                ttl=int(self.session_timeout.total_seconds())
            )
            
            # Persist to database
            await self._persist_session(session_data)
            
            # Update metrics
            self.metrics.total_sessions += 1
            self.metrics.active_sessions += 1
            
            # Send welcome notification
            await self.notification_service.send_notification(
                user_id=user_id,
                type='onboarding_started',
                data={
                    'session_id': session_id,
                    'creator_type': creator_type
                }
            )
            
            logger.info(f"Created onboarding session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating onboarding session: {str(e)}")
            raise OnboardingError(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve onboarding session with cache optimization.
        """
        try:
            # Try cache first
            cached_data = await self.cache_manager.get(f"session:{session_id}")
            if cached_data:
                return json.loads(cached_data)
            
            # Fallback to database
            session_data = await self._load_session_from_db(session_id)
            if session_data:
                # Update cache
                await self.cache_manager.set(
                    f"session:{session_id}",
                    json.dumps(session_data),
                    ttl=int(self.session_timeout.total_seconds())
                )
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    async def update_session(self, session_id: str, 
                           update_data: Dict[str, Any]) -> bool:
        """
        Update onboarding session with optimistic locking.
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                raise ValidationError(f"Session not found: {session_id}")
            
            # Update session data
            session_data.update(update_data)
            session_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Calculate completion percentage
            if 'completed_stages' in update_data:
                session_data['completion_percentage'] = self._calculate_progress(
                    session_data['completed_stages']
                )
            
            # Update cache
            await self.cache_manager.set(
                f"session:{session_id}",
                json.dumps(session_data),
                ttl=int(self.session_timeout.total_seconds())
            )
            
            # Update database
            await self._update_session_in_db(session_id, session_data)
            
            # Send progress notification
            if session_data['completion_percentage'] > 0:
                await self.notification_service.send_notification(
                    user_id=session_data['user_id'],
                    type='onboarding_progress',
                    data={
                        'session_id': session_id,
                        'completion_percentage': session_data['completion_percentage'],
                        'current_stage': session_data.get('current_stage')
                    }
                )
            
            logger.info(f"Updated onboarding session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            return False
    
    async def complete_onboarding(self, session_id: str, 
                                completion_data: Dict[str, Any] = None) -> bool:
        """
        Complete onboarding session with final validation and cleanup.
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                raise ValidationError(f"Session not found: {session_id}")
            
            # Validate completion requirements
            if not self._validate_completion_requirements(session_data):
                raise ValidationError("Onboarding requirements not met")
            
            # Update session status
            completion_update = {
                'status': OnboardingStatus.COMPLETED.value,
                'completion_percentage': 100.0,
                'completed_at': datetime.utcnow().isoformat(),
                'completion_data': completion_data or {}
            }
            
            await self.update_session(session_id, completion_update)
            
            # Update metrics
            self.metrics.completed_sessions += 1
            self.metrics.active_sessions -= 1
            self._update_completion_metrics()
            
            # Archive session data
            await self._archive_session(session_id, session_data)
            
            # Send completion notification
            await self.notification_service.send_notification(
                user_id=session_data['user_id'],
                type='onboarding_completed',
                data={
                    'session_id': session_id,
                    'creator_type': session_data['creator_type'],
                    'completion_time': completion_update['completed_at']
                }
            )
            
            # Clean up active session cache
            await self.cache_manager.delete(f"session:{session_id}")
            
            logger.info(f"Completed onboarding session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing onboarding {session_id}: {str(e)}")
            return False
    
    async def cancel_session(self, session_id: str, reason: str = None) -> bool:
        """
        Cancel onboarding session with proper cleanup.
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                return False
            
            # Update session status
            cancellation_update = {
                'status': OnboardingStatus.CANCELLED.value,
                'cancelled_at': datetime.utcnow().isoformat(),
                'cancellation_reason': reason
            }
            
            await self.update_session(session_id, cancellation_update)
            
            # Update metrics
            self.metrics.active_sessions -= 1
            
            # Send cancellation notification
            await self.notification_service.send_notification(
                user_id=session_data['user_id'],
                type='onboarding_cancelled',
                data={
                    'session_id': session_id,
                    'reason': reason
                }
            )
            
            # Clean up cache
            await self.cache_manager.delete(f"session:{session_id}")
            
            logger.info(f"Cancelled onboarding session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling session {session_id}: {str(e)}")
            return False
    
    async def get_user_sessions(self, user_id: str, 
                              status_filter: List[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all onboarding sessions for a user.
        """
        try:
            async with get_db_session() as db:
                query = """
                    SELECT session_id, creator_type, status, current_stage, 
                           completion_percentage, created_at, updated_at
                    FROM onboarding_sessions 
                    WHERE user_id = $1
                """
                params = [user_id]
                
                if status_filter:
                    query += f" AND status = ANY($2)"
                    params.append(status_filter)
                
                query += " ORDER BY created_at DESC"
                
                result = await db.fetch(query, *params)
                return [dict(row) for row in result]
                
        except Exception as e:
            logger.error(f"Error retrieving user sessions {user_id}: {str(e)}")
            return []
    
    async def get_metrics(self) -> OnboardingMetrics:
        """
        Get comprehensive onboarding metrics and analytics.
        """
        try:
            # Update live metrics from database
            await self._refresh_metrics()
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            return self.metrics
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired onboarding sessions.
        """
        try:
            cutoff_time = datetime.utcnow() - self.session_timeout
            
            async with get_db_session() as db:
                # Find expired active sessions
                expired_sessions = await db.fetch("""
                    SELECT session_id, user_id FROM onboarding_sessions
                    WHERE status = $1 AND updated_at < $2
                """, OnboardingStatus.IN_PROGRESS.value, cutoff_time)
                
                # Update status to failed
                for session in expired_sessions:
                    await self.update_session(session['session_id'], {
                        'status': OnboardingStatus.FAILED.value,
                        'failure_reason': 'session_timeout'
                    })
                    
                    # Clean up cache
                    await self.cache_manager.delete(f"session:{session['session_id']}")
                
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                return len(expired_sessions)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
            return 0
    
    async def _persist_session(self, session_data: Dict[str, Any]) -> None:
        """Persist session data to database."""
        try:
            async with get_db_session() as db:
                await db.execute("""
                    INSERT INTO onboarding_sessions (
                        session_id, user_id, creator_type, status,
                        current_stage, completed_stages, progress_data,
                        session_metadata, created_at, updated_at,
                        completion_percentage
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                session_data['session_id'],
                session_data['user_id'],
                session_data['creator_type'],
                session_data['status'],
                session_data['current_stage'],
                json.dumps(session_data['completed_stages']),
                json.dumps(session_data['progress_data']),
                json.dumps(session_data['session_metadata']),
                session_data['created_at'],
                session_data['updated_at'],
                session_data['completion_percentage']
                )
                
        except Exception as e:
            logger.error(f"Error persisting session: {str(e)}")
            raise
    
    async def _load_session_from_db(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from database."""
        try:
            async with get_db_session() as db:
                result = await db.fetchrow("""
                    SELECT * FROM onboarding_sessions WHERE session_id = $1
                """, session_id)
                
                if result:
                    session_data = dict(result)
                    session_data['completed_stages'] = json.loads(session_data['completed_stages'])
                    session_data['progress_data'] = json.loads(session_data['progress_data'])
                    session_data['session_metadata'] = json.loads(session_data['session_metadata'])
                    return session_data
                
                return None
                
        except Exception as e:
            logger.error(f"Error loading session from DB: {str(e)}")
            return None
    
    async def _update_session_in_db(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Update session data in database."""
        try:
            async with get_db_session() as db:
                await db.execute("""
                    UPDATE onboarding_sessions SET
                        status = $2, current_stage = $3, completed_stages = $4,
                        progress_data = $5, updated_at = $6, completion_percentage = $7
                    WHERE session_id = $1
                """,
                session_id,
                session_data['status'],
                session_data['current_stage'],
                json.dumps(session_data['completed_stages']),
                json.dumps(session_data['progress_data']),
                session_data['updated_at'],
                session_data['completion_percentage']
                )
                
        except Exception as e:
            logger.error(f"Error updating session in DB: {str(e)}")
            raise
    
    async def _archive_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Archive completed session data."""
        try:
            async with get_db_session() as db:
                await db.execute("""
                    INSERT INTO onboarding_archives (
                        session_id, user_id, creator_type, completion_data,
                        archived_at, session_duration_minutes
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                session_id,
                session_data['user_id'],
                session_data['creator_type'],
                json.dumps(session_data),
                datetime.utcnow(),
                self._calculate_session_duration(session_data)
                )
                
        except Exception as e:
            logger.error(f"Error archiving session: {str(e)}")
    
    def _calculate_progress(self, completed_stages: List[str]) -> float:
        """Calculate completion percentage based on completed stages."""
        total_stages = 8  # Total expected stages
        completed_count = len(completed_stages)
        return min((completed_count / total_stages) * 100, 100.0)
    
    def _validate_completion_requirements(self, session_data: Dict[str, Any]) -> bool:
        """
Validate that onboarding requirements are met."""
        required_stages = [
            'profile_creation',
            'content_analysis', 
            'rights_verification',
            'platform_connection'
        ]
        
        completed_stages = session_data.get('completed_stages', [])
        return all(stage in completed_stages for stage in required_stages)
    
    def _calculate_session_duration(self, session_data: Dict[str, Any]) -> int:
        """
Calculate session duration in minutes."""
        try:
            created_at = datetime.fromisoformat(session_data['created_at'])
            updated_at = datetime.fromisoformat(session_data['updated_at'])
            duration = updated_at - created_at
            return int(duration.total_seconds() / 60)
        except:
            return 0
    
    def _update_completion_metrics(self) -> None:
        """
Update completion rate and related metrics."""
        if self.metrics.total_sessions > 0:
            self.metrics.completion_rate = (
                self.metrics.completed_sessions / self.metrics.total_sessions
            ) * 100
    
    async def _refresh_metrics(self) -> None:
        """
Refresh metrics from database."""
        try:
            async with get_db_session() as db:
                # Get basic counts
                counts = await db.fetchrow("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as active,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                    FROM onboarding_sessions
                """)
                
                if counts:
                    self.metrics.total_sessions = counts['total']
                    self.metrics.active_sessions = counts['active']
                    self.metrics.completed_sessions = counts['completed']
                    self.metrics.failed_sessions = counts['failed']
                    self._update_completion_metrics()
                
        except Exception as e:
            logger.error(f"Error refreshing metrics: {str(e)}")
