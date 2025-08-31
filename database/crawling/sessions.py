"""Enterprise Crawling Sessions Manager

Advanced session management for persistent crawler operations
with multi-platform support and robust state tracking.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    CrawlingSession,
    SessionStatus,
    PlatformType
)
from ..core.exceptions import (
    CrawlingSessionError,
    DatabaseError,
    ValidationError
)


class SessionPriority(Enum):
    """Session priority levels for resource allocation."""    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class CrawlingSessionManager(DatabaseManager):
    """    Enterprise-grade crawling session manager for persistent
    crawler operations across multiple platforms.
    
    Handles:
    - Session lifecycle management
    - Platform-specific configurations
    - Resource allocation and cleanup
    - Performance monitoring
    - Failure recovery and resumption
    """    
    def __init__(self, db_session: Session):
        """        Initialize crawling session manager.
        
        Args:
            db_session: SQLAlchemy database session
        """        super().__init__(db_session)
        self.table = CrawlingSession
    
    async def create_session(
        self,
        platform: str,
        user_id: str,
        config: Dict[str, Any],
        proxy_info: Optional[Dict[str, Any]] = None,
        priority: SessionPriority = SessionPriority.NORMAL,
        max_duration_hours: int = 24,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Create a new crawling session with comprehensive configuration.
        
        Args:
            platform: Target platform (youtube, tiktok, instagram, twitter, generic)
            user_id: User identifier for session ownership
            config: Platform-specific configuration
            proxy_info: Optional proxy configuration
            priority: Session priority for resource allocation
            max_duration_hours: Maximum session duration in hours
            metadata: Optional additional metadata
            
        Returns:
            Dict containing session details
            
        Raises:
            CrawlingSessionError: If session creation fails
            ValidationError: If invalid parameters provided
        """        try:
            # Validate platform
            if platform not in [p.value for p in PlatformType]:
                raise ValidationError(f"Unsupported platform: {platform}")
            
            # Generate unique session ID
            session_id = str(uuid4())
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=max_duration_hours)
            
            # Prepare session data
            session_data = {
                'session_id': session_id,
                'platform': platform,
                'user_id': user_id,
                'status': SessionStatus.INITIALIZING.value,
                'priority': priority.value,
                'config': json.dumps(config),
                'proxy_info': json.dumps(proxy_info) if proxy_info else None,
                'metadata': json.dumps(metadata) if metadata else None,
                'max_duration_hours': max_duration_hours,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at,
                'last_activity': datetime.utcnow(),
                'jobs_count': 0,
                'discoveries_count': 0,
                'errors_count': 0,
                'total_requests': 0,
                'successful_requests': 0
            }
            
            # Create session record
            session = CrawlingSession(**session_data)
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            
            # Update status to active
            await self.update_session_status(session_id, SessionStatus.ACTIVE)
            
            return {
                'session_id': session_id,
                'platform': platform,
                'user_id': user_id,
                'status': SessionStatus.ACTIVE.value,
                'priority': priority.value,
                'created_at': session_data['created_at'],
                'expires_at': expires_at,
                'config': config,
                'proxy_info': proxy_info
            }
            
        except Exception as e:
            await self.db.rollback()
            raise CrawlingSessionError(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """        Retrieve session details by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict containing session data or None if not found
        """        try:
            session = await self.db.query(CrawlingSession).filter(
                CrawlingSession.session_id == session_id
            ).first()
            
            if not session:
                return None
            
            return {
                'session_id': session.session_id,
                'platform': session.platform,
                'user_id': session.user_id,
                'status': session.status,
                'priority': session.priority,
                'config': json.loads(session.config) if session.config else {},
                'proxy_info': json.loads(session.proxy_info) if session.proxy_info else None,
                'metadata': json.loads(session.metadata) if session.metadata else {},
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'last_activity': session.last_activity,
                'expires_at': session.expires_at,
                'jobs_count': session.jobs_count,
                'discoveries_count': session.discoveries_count,
                'errors_count': session.errors_count,
                'total_requests': session.total_requests,
                'successful_requests': session.successful_requests,
                'success_rate': (
                    session.successful_requests / session.total_requests * 100
                    if session.total_requests > 0 else 0.0
                )
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve session: {str(e)}")
    
    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> bool:
        """        Update session status with timestamp tracking.
        
        Args:
            session_id: Session identifier
            status: New session status
            
        Returns:
            bool indicating success
        """        try:
            result = await self.db.execute(
                text("""                UPDATE crawling_sessions 
                SET status = :status, 
                    updated_at = :now,
                    last_activity = :now
                WHERE session_id = :session_id
                """),
                {
                    'status': status.value,
                    'session_id': session_id,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update session status: {str(e)}")
    
    async def update_session_activity(
        self,
        session_id: str,
        increment_requests: int = 1,
        increment_successful: int = 0,
        increment_errors: int = 0
    ) -> bool:
        """        Update session activity metrics.
        
        Args:
            session_id: Session identifier
            increment_requests: Number of requests to add
            increment_successful: Number of successful requests to add
            increment_errors: Number of errors to add
            
        Returns:
            bool indicating success
        """        try:
            result = await self.db.execute(
                text("""                UPDATE crawling_sessions 
                SET last_activity = :now,
                    total_requests = total_requests + :requests,
                    successful_requests = successful_requests + :successful,
                    errors_count = errors_count + :errors,
                    updated_at = :now
                WHERE session_id = :session_id
                """),
                {
                    'session_id': session_id,
                    'requests': increment_requests,
                    'successful': increment_successful,
                    'errors': increment_errors,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update session activity: {str(e)}")
    
    async def add_job_to_session(self, session_id: str, job_id: str) -> bool:
        """        Associate a job with a session and increment job counter.
        
        Args:
            session_id: Session identifier
            job_id: Job identifier to associate
            
        Returns:
            bool indicating success
        """        try:
            result = await self.db.execute(
                text("""                UPDATE crawling_sessions 
                SET jobs_count = jobs_count + 1,
                    last_activity = :now,
                    updated_at = :now
                WHERE session_id = :session_id
                """),
                {
                    'session_id': session_id,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to add job to session: {str(e)}")
    
    async def increment_discoveries(self, session_id: str, count: int = 1) -> bool:
        """        Increment discovery count for session.
        
        Args:
            session_id: Session identifier
            count: Number of discoveries to add
            
        Returns:
            bool indicating success
        """        try:
            result = await self.db.execute(
                text("""                UPDATE crawling_sessions 
                SET discoveries_count = discoveries_count + :count,
                    last_activity = :now,
                    updated_at = :now
                WHERE session_id = :session_id
                """),
                {
                    'session_id': session_id,
                    'count': count,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to increment discoveries: {str(e)}")
    
    async def get_user_active_sessions(
        self,
        user_id: str,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
            platform: Optional platform filter
            
        Returns:
            List of active session dictionaries
        """        try:
            query = self.db.query(CrawlingSession).filter(
                and_(
                    CrawlingSession.user_id == user_id,
                    CrawlingSession.status.in_([
                        SessionStatus.ACTIVE.value,
                        SessionStatus.RUNNING.value,
                        SessionStatus.PAUSED.value
                    ])
                )
            )
            
            if platform:
                query = query.filter(CrawlingSession.platform == platform)
            
            sessions = await query.order_by(desc(CrawlingSession.created_at)).all()
            
            return [
                {
                    'session_id': session.session_id,
                    'platform': session.platform,
                    'status': session.status,
                    'priority': session.priority,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'jobs_count': session.jobs_count,
                    'discoveries_count': session.discoveries_count,
                    'success_rate': (
                        session.successful_requests / session.total_requests * 100
                        if session.total_requests > 0 else 0.0
                    )
                }
                for session in sessions
            ]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user active sessions: {str(e)}")
    
    async def get_expired_sessions(
        self,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """        Get sessions that have expired or been inactive.
        
        Args:
            cutoff_time: Time before which sessions are considered expired
            
        Returns:
            List of expired session dictionaries
        """        try:
            sessions = await self.db.query(CrawlingSession).filter(
                or_(
                    CrawlingSession.expires_at < datetime.utcnow(),
                    CrawlingSession.last_activity < cutoff_time,
                    CrawlingSession.status == SessionStatus.FAILED.value
                )
            ).all()
            
            return [
                {
                    'session_id': session.session_id,
                    'platform': session.platform,
                    'user_id': session.user_id,
                    'status': session.status,
                    'proxy_id': (
                        json.loads(session.proxy_info).get('proxy_id')
                        if session.proxy_info else None
                    ),
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'expires_at': session.expires_at
                }
                for session in sessions
            ]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expired sessions: {str(e)}")
    
    async def delete_session(self, session_id: str) -> bool:
        """        Delete a session and clean up associated data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool indicating success
        """        try:
            result = await self.db.execute(
                text("DELETE FROM crawling_sessions WHERE session_id = :session_id"),
                {'session_id': session_id}
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to delete session: {str(e)}")
    
    async def get_session_statistics(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """        Get comprehensive session statistics for dashboard.
        
        Args:
            time_range: Time range for statistics
            
        Returns:
            Dict containing session statistics
        """        try:
            since_time = datetime.utcnow() - time_range
            
            # Get session counts by status
            status_counts = await self.db.execute(
                text("""                SELECT status, COUNT(*) as count
                FROM crawling_sessions
                WHERE created_at >= :since_time
                GROUP BY status
                """),
                {'since_time': since_time}
            )
            
            # Get platform breakdown
            platform_counts = await self.db.execute(
                text("""                SELECT platform, COUNT(*) as count,
                       AVG(discoveries_count) as avg_discoveries,
                       AVG(successful_requests::float / NULLIF(total_requests, 0) * 100) as avg_success_rate
                FROM crawling_sessions
                WHERE created_at >= :since_time
                GROUP BY platform
                """),
                {'since_time': since_time}
            )
            
            # Get performance metrics
            performance_metrics = await self.db.execute(
                text("""                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(discoveries_count) as total_discoveries,
                    SUM(total_requests) as total_requests,
                    SUM(successful_requests) as successful_requests,
                    AVG(discoveries_count) as avg_discoveries_per_session,
                    AVG(successful_requests::float / NULLIF(total_requests, 0) * 100) as overall_success_rate
                FROM crawling_sessions
                WHERE created_at >= :since_time
                """),
                {'since_time': since_time}
            )
            
            status_data = {row.status: row.count for row in status_counts}
            platform_data = {
                row.platform: {
                    'count': row.count,
                    'avg_discoveries': float(row.avg_discoveries or 0),
                    'avg_success_rate': float(row.avg_success_rate or 0)
                }
                for row in platform_counts
            }
            perf_data = performance_metrics.first()
            
            return {
                'time_range_days': time_range.days,
                'status_breakdown': status_data,
                'platform_breakdown': platform_data,
                'performance_metrics': {
                    'total_sessions': perf_data.total_sessions or 0,
                    'total_discoveries': perf_data.total_discoveries or 0,
                    'total_requests': perf_data.total_requests or 0,
                    'successful_requests': perf_data.successful_requests or 0,
                    'avg_discoveries_per_session': float(perf_data.avg_discoveries_per_session or 0),
                    'overall_success_rate': float(perf_data.overall_success_rate or 0)
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get session statistics: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """        Perform health check of session management system.
        
        Returns:
            Dict containing health status
        """        try:
            # Check active sessions count
            active_count = await self.db.query(func.count(CrawlingSession.session_id)).filter(
                CrawlingSession.status.in_([
                    SessionStatus.ACTIVE.value,
                    SessionStatus.RUNNING.value
                ])
            ).scalar()
            
            # Check for stuck sessions (active but no activity > 1 hour)
            stuck_count = await self.db.query(func.count(CrawlingSession.session_id)).filter(
                and_(
                    CrawlingSession.status.in_([
                        SessionStatus.ACTIVE.value,
                        SessionStatus.RUNNING.value
                    ]),
                    CrawlingSession.last_activity < datetime.utcnow() - timedelta(hours=1)
                )
            ).scalar()
            
            # Determine health status
            status = 'healthy'
            if stuck_count > active_count * 0.1:  # More than 10% stuck
                status = 'degraded'
            if stuck_count > active_count * 0.3:  # More than 30% stuck
                status = 'unhealthy'
            
            return {
                'status': status,
                'active_sessions': active_count,
                'stuck_sessions': stuck_count,
                'stuck_percentage': (stuck_count / max(active_count, 1)) * 100,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['CrawlingSessionManager', 'SessionPriority']
