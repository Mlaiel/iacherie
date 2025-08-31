"""
Enterprise Crawling Jobs Manager

Advanced job scheduling and execution management for distributed
crawling operations with priority queuing and failure recovery.

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
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    CrawlingJob,
    JobStatus,
    JobType,
    JobPriority
)
from ..core.exceptions import (
    CrawlingJobError,
    DatabaseError,
    ValidationError
)


class CrawlingJobManager(DatabaseManager):
    """
    Enterprise-grade crawling job manager for distributed
    scheduling and execution of crawling operations.
    
    Handles:
    - Job scheduling and prioritization
    - Distributed execution management
    - Progress tracking and reporting
    - Failure recovery and retry logic
    - Performance optimization
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize crawling job manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        self.table = CrawlingJob
    
    async def create_job(
        self,
        session_id: str,
        job_type: str,
        targets: List[str],
        priority: int = 5,
        schedule_time: Optional[datetime] = None,
        recurring_interval: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        estimated_duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new crawling job with comprehensive configuration.
        
        Args:
            session_id: Associated crawling session ID
            job_type: Type of job (discovery, monitoring, analytics, content_scan)
            targets: List of URLs or identifiers to crawl
            priority: Job priority (1-10, higher = more urgent)
            schedule_time: When to execute job (default: now)
            recurring_interval: Recurring interval in minutes (optional)
            config: Job-specific configuration
            estimated_duration: Estimated execution time in seconds
            metadata: Additional job metadata
            
        Returns:
            Dict containing job details
            
        Raises:
            CrawlingJobError: If job creation fails
            ValidationError: If invalid parameters provided
        """



        try:
            # Validate job type
            if job_type not in [jt.value for jt in JobType]:
                raise ValidationError(f"Invalid job type: {job_type}")
            
            # Validate priority
            if not 1 <= priority <= 10:
                raise ValidationError("Priority must be between 1 and 10")
            
            # Validate targets
            if not targets or not isinstance(targets, list):
                raise ValidationError("Targets must be a non-empty list")
            
            # Generate unique job ID
            job_id = str(uuid4())
            
            # Set default schedule time
            if schedule_time is None:
                schedule_time = datetime.utcnow()
            
            # Estimate duration if not provided
            if estimated_duration is None:
                estimated_duration = self._estimate_job_duration(job_type, len(targets))
            
            # Calculate expected completion time
            expected_completion = schedule_time + timedelta(seconds=estimated_duration)
            
            # Prepare job data
            job_data = {
                'job_id': job_id,
                'session_id': session_id,
                'job_type': job_type,
                'status': JobStatus.PENDING.value,
                'priority': priority,
                'targets': json.dumps(targets),
                'targets_count': len(targets),
                'config': json.dumps(config) if config else None,
                'metadata': json.dumps(metadata) if metadata else None,
                'scheduled_for': schedule_time,
                'recurring_interval': recurring_interval,
                'estimated_duration': estimated_duration,
                'expected_completion': expected_completion,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'progress_percentage': 0.0,
                'discoveries_count': 0,
                'errors_count': 0,
                'retry_count': 0,
                'max_retries': 3
            }
            
            # Create job record
            job = CrawlingJob(**job_data)
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
            
            return {
                'job_id': job_id,
                'session_id': session_id,
                'job_type': job_type,
                'status': JobStatus.PENDING.value,
                'priority': priority,
                'targets_count': len(targets),
                'scheduled_for': schedule_time,
                'estimated_duration': estimated_duration,
                'expected_completion': expected_completion,
                'created_at': job_data['created_at']
            }
            
        except Exception as e:
            await self.db.rollback()
            raise CrawlingJobError(f"Failed to create job: {str(e)}")
    
    def _estimate_job_duration(self, job_type: str, targets_count: int) -> int:
        """
        Estimate job duration based on type and target count.
        
        Args:
            job_type: Type of crawling job
            targets_count: Number of targets to process
            
        Returns:
            Estimated duration in seconds
        """
        # Base time per target in seconds
        base_times = {
            JobType.DISCOVERY.value: 30,      # 30s per discovery target
            JobType.MONITORING.value: 15,     # 15s per monitoring target
            JobType.ANALYTICS.value: 45,      # 45s per analytics target
            JobType.CONTENT_SCAN.value: 60,   # 60s per content scan
            JobType.DEEP_CRAWL.value: 180     # 3 minutes per deep crawl
        }
        
        base_time = base_times.get(job_type, 30)
        return base_time * targets_count + 60  # Add 1 minute overhead
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve job details by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dict containing job data or None if not found
        """



        try:
            job = await self.db.query(CrawlingJob).filter(
                CrawlingJob.job_id == job_id
            ).first()
            
            if not job:
                return None
            
            return {
                'job_id': job.job_id,
                'session_id': job.session_id,
                'job_type': job.job_type,
                'status': job.status,
                'priority': job.priority,
                'targets': json.loads(job.targets) if job.targets else [],
                'targets_count': job.targets_count,
                'config': json.loads(job.config) if job.config else {},
                'metadata': json.loads(job.metadata) if job.metadata else {},
                'scheduled_for': job.scheduled_for,
                'started_at': job.started_at,
                'completed_at': job.completed_at,
                'recurring_interval': job.recurring_interval,
                'estimated_duration': job.estimated_duration,
                'actual_duration': job.actual_duration,
                'expected_completion': job.expected_completion,
                'progress_percentage': job.progress_percentage,
                'discoveries_count': job.discoveries_count,
                'errors_count': job.errors_count,
                'retry_count': job.retry_count,
                'max_retries': job.max_retries,
                'created_at': job.created_at,
                'updated_at': job.updated_at,
                'error_message': job.error_message
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve job: {str(e)}")
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update job status with proper timestamp tracking.
        
        Args:
            job_id: Job identifier
            status: New job status
            error_message: Optional error message for failed jobs
            
        Returns:
            bool indicating success
        """



        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.utcnow()
            }
            
            # Set specific timestamps based on status
            if status == JobStatus.RUNNING:
                update_data['started_at'] = datetime.utcnow()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                now = datetime.utcnow()
                update_data['completed_at'] = now
                
                # Calculate actual duration if job was started
                job_data = await self.get_job(job_id)
                if job_data and job_data.get('started_at'):
                    duration = (now - job_data['started_at']).total_seconds()
                    update_data['actual_duration'] = int(duration)
            
            if error_message:
                update_data['error_message'] = error_message
            
            # Build update query
            set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
            
            result = await self.db.execute(
                text(f"UPDATE crawling_jobs SET {set_clause} WHERE job_id = :job_id"),
                {**update_data, 'job_id': job_id}
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update job status: {str(e)}")
    
    async def update_job_progress(
        self,
        job_id: str,
        progress_percentage: float,
        discoveries_increment: int = 0,
        errors_increment: int = 0
    ) -> bool:
        """
        Update job progress metrics.
        
        Args:
            job_id: Job identifier
            progress_percentage: Current progress (0-100)
            discoveries_increment: Number of new discoveries
            errors_increment: Number of new errors
            
        Returns:
            bool indicating success
        """



        try:
            result = await self.db.execute(
                text("""
                UPDATE crawling_jobs 
                SET progress_percentage = :progress,
                    discoveries_count = discoveries_count + :discoveries,
                    errors_count = errors_count + :errors,
                    updated_at = :now
                WHERE job_id = :job_id
                """),
                {
                    'job_id': job_id,
                    'progress': progress_percentage,
                    'discoveries': discoveries_increment,
                    'errors': errors_increment,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update job progress: {str(e)}")
    
    async def increment_discoveries(self, job_id: str, count: int = 1) -> bool:
        """
        Increment discovery count for job.
        
        Args:
            job_id: Job identifier
            count: Number of discoveries to add
            
        Returns:
            bool indicating success
        """



        try:
            result = await self.db.execute(
                text("""
                UPDATE crawling_jobs 
                SET discoveries_count = discoveries_count + :count,
                    updated_at = :now
                WHERE job_id = :job_id
                """),
                {
                    'job_id': job_id,
                    'count': count,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to increment discoveries: {str(e)}")
    
    async def get_pending_jobs(
        self,
        limit: int = 50,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending jobs ordered by priority and schedule time.
        
        Args:
            limit: Maximum number of jobs to return
            platform: Optional platform filter
            
        Returns:
            List of pending job dictionaries
        """



        try:
            query = self.db.query(CrawlingJob).filter(
                and_(
                    CrawlingJob.status == JobStatus.PENDING.value,
                    CrawlingJob.scheduled_for <= datetime.utcnow()
                )
            )
            
            # Add platform filter if specified
            if platform:
                # Join with sessions table to filter by platform
                query = query.join(CrawlingJob.session).filter(
                    CrawlingSession.platform == platform
                )
            
            jobs = await query.order_by(
                desc(CrawlingJob.priority),
                asc(CrawlingJob.scheduled_for)
            ).limit(limit).all()
            
            return [
                {
                    'job_id': job.job_id,
                    'session_id': job.session_id,
                    'job_type': job.job_type,
                    'priority': job.priority,
                    'targets_count': job.targets_count,
                    'scheduled_for': job.scheduled_for,
                    'estimated_duration': job.estimated_duration,
                    'retry_count': job.retry_count,
                    'max_retries': job.max_retries
                }
                for job in jobs
            ]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending jobs: {str(e)}")
    
    async def get_user_queue_status(self, user_id: str) -> Dict[str, int]:
        """
        Get job queue status for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing job counts by status
        """



        try:
            # Query job counts by status for user's sessions
            result = await self.db.execute(
                text("""
                SELECT cj.status, COUNT(*) as count
                FROM crawling_jobs cj
                JOIN crawling_sessions cs ON cj.session_id = cs.session_id
                WHERE cs.user_id = :user_id
                  AND cj.created_at >= :since_time
                GROUP BY cj.status
                """),
                {
                    'user_id': user_id,
                    'since_time': datetime.utcnow() - timedelta(days=30)
                }
            )
            
            status_counts = {row.status: row.count for row in result}
            
            return {
                'pending': status_counts.get(JobStatus.PENDING.value, 0),
                'running': status_counts.get(JobStatus.RUNNING.value, 0),
                'completed': status_counts.get(JobStatus.COMPLETED.value, 0),
                'failed': status_counts.get(JobStatus.FAILED.value, 0),
                'cancelled': status_counts.get(JobStatus.CANCELLED.value, 0),
                'total': sum(status_counts.values())
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user queue status: {str(e)}")
    
    async def get_job_analytics(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Get comprehensive job analytics for dashboard.
        
        Args:
            time_range: Time range for analytics
            
        Returns:
            Dict containing job analytics
        """



        try:
            since_time = datetime.utcnow() - time_range
            
            # Get job counts by status
            status_counts = await self.db.execute(
                text("""
                SELECT status, COUNT(*) as count
                FROM crawling_jobs
                WHERE created_at >= :since_time
                GROUP BY status
                """),
                {'since_time': since_time}
            )
            
            # Get job type breakdown
            type_counts = await self.db.execute(
                text("""
                SELECT job_type, COUNT(*) as count,
                       AVG(actual_duration) as avg_duration,
                       AVG(discoveries_count) as avg_discoveries
                FROM crawling_jobs
                WHERE created_at >= :since_time
                  AND status = :completed_status
                GROUP BY job_type
                """),
                {
                    'since_time': since_time,
                    'completed_status': JobStatus.COMPLETED.value
                }
            )
            
            # Get performance metrics
            performance = await self.db.execute(
                text("""
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(discoveries_count) as total_discoveries,
                    AVG(actual_duration) as avg_duration,
                    AVG(progress_percentage) as avg_progress,
                    COUNT(CASE WHEN status = :completed THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = :failed THEN 1 END) as failed_jobs
                FROM crawling_jobs
                WHERE created_at >= :since_time
                """),
                {
                    'since_time': since_time,
                    'completed': JobStatus.COMPLETED.value,
                    'failed': JobStatus.FAILED.value
                }
            )
            
            status_data = {row.status: row.count for row in status_counts}
            type_data = {
                row.job_type: {
                    'count': row.count,
                    'avg_duration': float(row.avg_duration or 0),
                    'avg_discoveries': float(row.avg_discoveries or 0)
                }
                for row in type_counts
            }
            perf_data = performance.first()
            
            success_rate = 0.0
            if perf_data.total_jobs > 0:
                success_rate = (perf_data.completed_jobs / perf_data.total_jobs) * 100
            
            return {
                'time_range_days': time_range.days,
                'status_breakdown': status_data,
                'job_type_breakdown': type_data,
                'performance_metrics': {
                    'total_jobs': perf_data.total_jobs or 0,
                    'completed_jobs': perf_data.completed_jobs or 0,
                    'failed_jobs': perf_data.failed_jobs or 0,
                    'success_rate': success_rate,
                    'total_discoveries': perf_data.total_discoveries or 0,
                    'avg_duration_seconds': float(perf_data.avg_duration or 0),
                    'avg_progress_percentage': float(perf_data.avg_progress or 0)
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get job analytics: {str(e)}")
    
    async def retry_failed_job(self, job_id: str) -> bool:
        """
        Retry a failed job if retry count hasn't exceeded maximum.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool indicating if retry was scheduled
        """



        try:
            job_data = await self.get_job(job_id)
            if not job_data:
                raise CrawlingJobError(f"Job not found: {job_id}")
            
            if job_data['status'] != JobStatus.FAILED.value:
                raise CrawlingJobError(f"Job is not in failed status: {job_id}")
            
            if job_data['retry_count'] >= job_data['max_retries']:
                return False  # Max retries exceeded
            
            # Reset job for retry
            result = await self.db.execute(
                text("""
                UPDATE crawling_jobs 
                SET status = :status,
                    retry_count = retry_count + 1,
                    scheduled_for = :schedule_time,
                    started_at = NULL,
                    completed_at = NULL,
                    actual_duration = NULL,
                    progress_percentage = 0.0,
                    error_message = NULL,
                    updated_at = :now
                WHERE job_id = :job_id
                """),
                {
                    'job_id': job_id,
                    'status': JobStatus.PENDING.value,
                    'schedule_time': datetime.utcnow() + timedelta(minutes=5),  # Retry in 5 minutes
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise CrawlingJobError(f"Failed to retry job: {str(e)}")
    
    async def cleanup_session_jobs(self, session_id: str) -> int:
        """
        Clean up all jobs for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of jobs cleaned up
        """



        try:
            result = await self.db.execute(
                text("DELETE FROM crawling_jobs WHERE session_id = :session_id"),
                {'session_id': session_id}
            )
            
            await self.db.commit()
            return result.rowcount
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to cleanup session jobs: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of job management system.
        
        Returns:
            Dict containing health status
        """



        try:
            # Check pending jobs count
            pending_count = await self.db.query(func.count(CrawlingJob.job_id)).filter(
                CrawlingJob.status == JobStatus.PENDING.value
            ).scalar()
            
            # Check stuck running jobs (running > 2 hours)
            stuck_running = await self.db.query(func.count(CrawlingJob.job_id)).filter(
                and_(
                    CrawlingJob.status == JobStatus.RUNNING.value,
                    CrawlingJob.started_at < datetime.utcnow() - timedelta(hours=2)
                )
            ).scalar()
            
            # Check failed jobs in last hour
            recent_failures = await self.db.query(func.count(CrawlingJob.job_id)).filter(
                and_(
                    CrawlingJob.status == JobStatus.FAILED.value,
                    CrawlingJob.updated_at >= datetime.utcnow() - timedelta(hours=1)
                )
            ).scalar()
            
            # Determine health status
            status = 'healthy'
            if stuck_running > 10 or recent_failures > 50:
                status = 'degraded'
            if stuck_running > 50 or recent_failures > 200:
                status = 'unhealthy'
            
            return {
                'status': status,
                'pending_jobs': pending_count,
                'stuck_running_jobs': stuck_running,
                'recent_failures': recent_failures,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['CrawlingJobManager']
