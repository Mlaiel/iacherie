"""
Enterprise Crawling Database Index

Main entry point for crawling database operations, session management,
and platform-specific crawler database interactions.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status

from .sessions import CrawlingSessionManager
from .jobs import CrawlingJobManager  
from .analytics import CrawlingAnalyticsManager
from .rate_limits import RateLimitManager
from .proxy_pools import ProxyPoolManager
from .platform_configs import PlatformConfigManager
from .content_discoveries import ContentDiscoveryManager

from ..core.base import DatabaseManager
from ..core.exceptions import (
    DatabaseError,
    CrawlingSessionError,
    RateLimitExceededError,
    ProxyPoolExhaustedError
)


class CrawlingDatabaseManager(DatabaseManager):
    """
    Enterprise-grade crawling database manager for multi-platform
    web surveillance and content discovery operations.
    
    Handles all database operations for:
    - Crawling sessions and job management
    - Platform-specific configurations
    - Rate limiting and quota management
    - Proxy pool rotation and health monitoring
    - Content discovery and metadata storage
    - Performance analytics and reporting
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize crawling database manager with all sub-managers.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        
        # Initialize specialized managers
        self.sessions = CrawlingSessionManager(db_session)
        self.jobs = CrawlingJobManager(db_session)
        self.analytics = CrawlingAnalyticsManager(db_session)
        self.rate_limits = RateLimitManager(db_session)
        self.proxy_pools = ProxyPoolManager(db_session)
        self.platform_configs = PlatformConfigManager(db_session)
        self.content_discoveries = ContentDiscoveryManager(db_session)
        
    async def initialize_platform_crawler(
        self,
        platform: str,
        user_id: str,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a new crawler for specified platform with optimal configuration.
        
        Args:
            platform: Target platform (youtube, tiktok, instagram, twitter, generic)
            user_id: User identifier for session tracking
            config_overrides: Optional configuration overrides
            
        Returns:
            Dict containing session details and crawler configuration
            
        Raises:
            CrawlingSessionError: If session initialization fails
            RateLimitExceededError: If platform rate limits exceeded
        """



        try:
            # Check rate limits for platform
            if not await self.rate_limits.check_platform_quota(platform, user_id):
                raise RateLimitExceededError(
                    f"Rate limit exceeded for platform {platform}"
                )
            
            # Get platform configuration
            platform_config = await self.platform_configs.get_config(
                platform, config_overrides
            )
            
            # Get available proxy for platform
            proxy_info = await self.proxy_pools.assign_proxy(platform, user_id)
            
            # Create new crawling session
            session_data = await self.sessions.create_session(
                platform=platform,
                user_id=user_id,
                config=platform_config,
                proxy_info=proxy_info
            )
            
            # Update rate limit counters
            await self.rate_limits.increment_usage(platform, user_id)
            
            # Log analytics event
            await self.analytics.log_session_start(
                session_data['session_id'],
                platform,
                user_id
            )
            
            return {
                'session_id': session_data['session_id'],
                'platform': platform,
                'config': platform_config,
                'proxy': proxy_info,
                'rate_limit_remaining': await self.rate_limits.get_remaining_quota(
                    platform, user_id
                ),
                'created_at': session_data['created_at']
            }
            
        except Exception as e:
            await self.analytics.log_error(
                'crawler_initialization_failed',
                {'platform': platform, 'user_id': user_id, 'error': str(e)}
            )
            raise CrawlingSessionError(f"Failed to initialize crawler: {str(e)}")
    
    async def schedule_crawling_job(
        self,
        session_id: str,
        job_type: str,
        targets: List[str],
        priority: int = 5,
        schedule_time: Optional[datetime] = None,
        recurring_interval: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Schedule a new crawling job with specified parameters.
        
        Args:
            session_id: Active crawling session ID
            job_type: Type of crawling job (discovery, monitoring, analytics)
            targets: List of target URLs or identifiers to crawl
            priority: Job priority (1-10, higher = more priority)
            schedule_time: Optional specific scheduling time
            recurring_interval: Optional recurring interval in minutes
            
        Returns:
            Dict containing job details and scheduling information
        """



        try:
            # Validate session exists and is active
            session_info = await self.sessions.get_session(session_id)
            if not session_info or session_info['status'] != 'active':
                raise CrawlingSessionError(f"Invalid or inactive session: {session_id}")
            
            # Create crawling job
            job_data = await self.jobs.create_job(
                session_id=session_id,
                job_type=job_type,
                targets=targets,
                priority=priority,
                schedule_time=schedule_time or datetime.utcnow(),
                recurring_interval=recurring_interval
            )
            
            # Update session with job reference
            await self.sessions.add_job_to_session(session_id, job_data['job_id'])
            
            # Log analytics
            await self.analytics.log_job_scheduled(
                job_data['job_id'],
                session_id,
                job_type,
                len(targets)
            )
            
            return {
                'job_id': job_data['job_id'],
                'session_id': session_id,
                'job_type': job_type,
                'targets_count': len(targets),
                'priority': priority,
                'scheduled_for': job_data['scheduled_for'],
                'estimated_duration': job_data['estimated_duration'],
                'status': job_data['status']
            }
            
        except Exception as e:
            await self.analytics.log_error(
                'job_scheduling_failed',
                {'session_id': session_id, 'job_type': job_type, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to schedule crawling job: {str(e)}")
    
    async def store_content_discovery(
        self,
        session_id: str,
        job_id: str,
        discovered_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store discovered content with metadata and analysis results.
        
        Args:
            session_id: Crawling session ID
            job_id: Job ID that discovered the content
            discovered_content: Content data and metadata
            
        Returns:
            Dict containing stored content information
        """



        try:
            # Validate session and job
            session_info = await self.sessions.get_session(session_id)
            job_info = await self.jobs.get_job(job_id)
            
            if not session_info or not job_info:
                raise DatabaseError("Invalid session or job ID")
            
            # Store content discovery
            discovery_data = await self.content_discoveries.store_discovery(
                session_id=session_id,
                job_id=job_id,
                content_data=discovered_content,
                platform=session_info['platform']
            )
            
            # Update job progress
            await self.jobs.increment_discoveries(job_id)
            
            # Update analytics
            await self.analytics.log_content_discovered(
                discovery_data['discovery_id'],
                session_id,
                job_id,
                discovered_content.get('content_type', 'unknown')
            )
            
            return {
                'discovery_id': discovery_data['discovery_id'],
                'content_type': discovered_content.get('content_type'),
                'platform': session_info['platform'],
                'confidence_score': discovery_data.get('confidence_score', 0.0),
                'discovered_at': discovery_data['discovered_at'],
                'metadata': discovery_data['metadata']
            }
            
        except Exception as e:
            await self.analytics.log_error(
                'content_storage_failed',
                {'session_id': session_id, 'job_id': job_id, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to store content discovery: {str(e)}")
    
    async def get_crawling_dashboard_data(
        self,
        user_id: str,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for crawling operations.
        
        Args:
            user_id: User identifier
            time_range: Time range for analytics data
            
        Returns:
            Dict containing dashboard metrics and statistics
        """



        try:
            since_time = datetime.utcnow() - time_range
            
            # Get active sessions
            active_sessions = await self.sessions.get_user_active_sessions(user_id)
            
            # Get recent discoveries
            recent_discoveries = await self.content_discoveries.get_user_discoveries(
                user_id, since=since_time, limit=50
            )
            
            # Get analytics summary
            analytics_summary = await self.analytics.get_user_summary(
                user_id, since=since_time
            )
            
            # Get rate limit status
            rate_limit_status = await self.rate_limits.get_user_status(user_id)
            
            # Get job queue status
            job_queue_status = await self.jobs.get_user_queue_status(user_id)
            
            return {
                'active_sessions': len(active_sessions),
                'session_details': active_sessions,
                'recent_discoveries_count': len(recent_discoveries),
                'recent_discoveries': recent_discoveries[:10],  # Top 10
                'analytics': {
                    'total_discoveries': analytics_summary.get('total_discoveries', 0),
                    'success_rate': analytics_summary.get('success_rate', 0.0),
                    'avg_response_time': analytics_summary.get('avg_response_time', 0.0),
                    'platform_breakdown': analytics_summary.get('platform_breakdown', {})
                },
                'rate_limits': rate_limit_status,
                'job_queue': {
                    'pending_jobs': job_queue_status.get('pending', 0),
                    'running_jobs': job_queue_status.get('running', 0),
                    'completed_jobs': job_queue_status.get('completed', 0),
                    'failed_jobs': job_queue_status.get('failed', 0)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.analytics.log_error(
                'dashboard_data_failed',
                {'user_id': user_id, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to generate dashboard data: {str(e)}")
    
    async def cleanup_expired_sessions(self, max_age_hours: int = 24) -> Dict[str, int]:
        """
        Clean up expired crawling sessions and associated data.
        
        Args:
            max_age_hours: Maximum age in hours before session cleanup
            
        Returns:
            Dict containing cleanup statistics
        """



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Get expired sessions
            expired_sessions = await self.sessions.get_expired_sessions(cutoff_time)
            
            cleanup_stats = {
                'sessions_cleaned': 0,
                'jobs_cleaned': 0,
                'discoveries_cleaned': 0,
                'proxy_assignments_released': 0
            }
            
            for session in expired_sessions:
                session_id = session['session_id']
                
                # Clean up jobs for this session
                job_count = await self.jobs.cleanup_session_jobs(session_id)
                cleanup_stats['jobs_cleaned'] += job_count
                
                # Archive discoveries (don't delete, move to archive)
                discovery_count = await self.content_discoveries.archive_session_discoveries(
                    session_id
                )
                cleanup_stats['discoveries_cleaned'] += discovery_count
                
                # Release proxy assignments
                if session.get('proxy_id'):
                    await self.proxy_pools.release_proxy(session['proxy_id'])
                    cleanup_stats['proxy_assignments_released'] += 1
                
                # Delete session
                await self.sessions.delete_session(session_id)
                cleanup_stats['sessions_cleaned'] += 1
            
            # Log cleanup operation
            await self.analytics.log_cleanup_operation(cleanup_stats)
            
            return cleanup_stats
            
        except Exception as e:
            await self.analytics.log_error(
                'cleanup_operation_failed',
                {'max_age_hours': max_age_hours, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to cleanup expired sessions: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of crawling database systems.
        
        Returns:
            Dict containing health status of all components
        """



        try:
            health_status = {
                'overall_status': 'healthy',
                'components': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Check each component
            components = [
                ('sessions', self.sessions),
                ('jobs', self.jobs),
                ('analytics', self.analytics),
                ('rate_limits', self.rate_limits),
                ('proxy_pools', self.proxy_pools),
                ('platform_configs', self.platform_configs),
                ('content_discoveries', self.content_discoveries)
            ]
            
            for component_name, component in components:
                try:
                    component_health = await component.health_check()
                    health_status['components'][component_name] = component_health
                    
                    if component_health.get('status') != 'healthy':
                        health_status['overall_status'] = 'degraded'
                        
                except Exception as e:
                    health_status['components'][component_name] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    health_status['overall_status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Export main interface
__all__ = [
    'CrawlingDatabaseManager',
    'CrawlingSessionManager',
    'CrawlingJobManager',
    'CrawlingAnalyticsManager',
    'RateLimitManager',
    'ProxyPoolManager',
    'PlatformConfigManager',
    'ContentDiscoveryManager'
]
