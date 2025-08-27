"""
Cross-Platform Monitoring Repository

Enterprise-grade repository for real-time cross-platform content monitoring,
violation detection, and automated response systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc, and_, or_, func, text

from .base_repository import BaseRepository
from ..models.cross_platform_monitoring import (
    PlatformMonitoring,
    ScanResult,
    ViolationDetection,
    MonitoringPlatform,
    MonitoringStatus,
    DetectionMethod,
    ResponseAction
)
from ..connections.manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class CrossPlatformMonitoringRepository(BaseRepository[PlatformMonitoring]):
    """
    Enterprise Cross-Platform Monitoring Repository
    
    Manages real-time monitoring across multiple content platforms with
    AI-powered violation detection and automated response systems.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(PlatformMonitoring, db_session)
        self.model = PlatformMonitoring
    
    async def create_monitoring_job(
        self,
        content_fingerprint_id: str,
        user_id: str,
        platform: MonitoringPlatform,
        detection_methods: List[DetectionMethod],
        **kwargs
    ) -> PlatformMonitoring:
        """
        Create new platform monitoring job
        
        Args:
            content_fingerprint_id: Content fingerprint UUID
            user_id: User UUID
            platform: Target platform for monitoring
            detection_methods: List of detection methods to use
            **kwargs: Additional monitoring parameters
            
        Returns:
            Created PlatformMonitoring instance
        """
        try:
            monitoring_data = {
                "content_fingerprint_id": content_fingerprint_id,
                "user_id": user_id,
                "platform": platform,
                "detection_methods": detection_methods,
                "monitoring_status": MonitoringStatus.ACTIVE,
                "next_scan_at": datetime.now(timezone.utc) + timedelta(minutes=kwargs.get('scan_frequency_minutes', 60)),
                **kwargs
            }
            
            monitoring_job = PlatformMonitoring(**monitoring_data)
            
            self.db_session.add(monitoring_job)
            await self.db_session.commit()
            await self.db_session.refresh(monitoring_job)
            
            logger.info(f"Created monitoring job: {monitoring_job.id} for platform: {platform.value}")
            return monitoring_job
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create monitoring job: {str(e)}")
            raise
    
    async def get_due_scans(
        self,
        limit: int = 100
    ) -> List[PlatformMonitoring]:
        """
        Get monitoring jobs that are due for scanning
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of PlatformMonitoring instances due for scanning
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            due_scans = self.db_session.query(self.model).filter(
                and_(
                    self.model.monitoring_status == MonitoringStatus.ACTIVE,
                    self.model.next_scan_at <= current_time,
                    self.model.is_active == True
                )
            ).order_by(asc(self.model.priority_level), asc(self.model.next_scan_at)).limit(limit).all()
            
            logger.info(f"Found {len(due_scans)} monitoring jobs due for scanning")
            return due_scans
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get due scans: {str(e)}")
            raise
    
    async def update_scan_schedule(
        self,
        monitoring_id: str,
        last_scan_time: datetime,
        next_scan_time: datetime,
        scan_successful: bool = True
    ) -> PlatformMonitoring:
        """
        Update monitoring job scan schedule
        
        Args:
            monitoring_id: PlatformMonitoring UUID
            last_scan_time: When the scan was performed
            next_scan_time: When the next scan should occur
            scan_successful: Whether the scan was successful
            
        Returns:
            Updated PlatformMonitoring instance
        """
        try:
            monitoring_job = await self.get_by_id(monitoring_id)
            if not monitoring_job:
                raise ValueError(f"Monitoring job not found: {monitoring_id}")
            
            monitoring_job.last_scan_at = last_scan_time
            monitoring_job.next_scan_at = next_scan_time
            monitoring_job.total_scans_performed += 1
            
            if scan_successful:
                monitoring_job.last_successful_scan = last_scan_time
                monitoring_job.consecutive_errors = 0
            else:
                monitoring_job.consecutive_errors += 1
                
                # Auto-pause if too many consecutive errors
                if monitoring_job.consecutive_errors >= 5:
                    monitoring_job.monitoring_status = MonitoringStatus.ERROR
                    logger.warning(f"Monitoring job {monitoring_id} paused due to consecutive errors")
            
            await self.db_session.commit()
            
            logger.info(f"Updated scan schedule for monitoring job: {monitoring_id}")
            return monitoring_job
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update scan schedule: {str(e)}")
            raise
    
    async def record_scan_result(
        self,
        monitoring_id: str,
        scan_started_at: datetime,
        scan_completed_at: datetime,
        total_items_scanned: int,
        potential_matches_found: int,
        scan_results_data: Dict[str, Any]
    ) -> ScanResult:
        """
        Record detailed scan results
        
        Args:
            monitoring_id: PlatformMonitoring UUID
            scan_started_at: Scan start timestamp
            scan_completed_at: Scan completion timestamp
            total_items_scanned: Number of items scanned
            potential_matches_found: Number of potential matches found
            scan_results_data: Detailed scan results
            
        Returns:
            Created ScanResult instance
        """
        try:
            scan_duration = (scan_completed_at - scan_started_at).total_seconds()
            
            scan_result_data = {
                "platform_monitoring_id": monitoring_id,
                "scan_started_at": scan_started_at,
                "scan_completed_at": scan_completed_at,
                "scan_duration_seconds": int(scan_duration),
                "total_items_scanned": total_items_scanned,
                "potential_matches_found": potential_matches_found,
                "scan_results_data": scan_results_data,
                "scan_completed_successfully": True
            }
            
            scan_result = ScanResult(**scan_result_data)
            
            self.db_session.add(scan_result)
            
            # Update monitoring job statistics
            monitoring_job = await self.get_by_id(monitoring_id)
            if monitoring_job:
                monitoring_job.matches_found += potential_matches_found
            
            await self.db_session.commit()
            await self.db_session.refresh(scan_result)
            
            logger.info(f"Recorded scan result for monitoring job: {monitoring_id} - {potential_matches_found} matches found")
            return scan_result
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to record scan result: {str(e)}")
            raise
    
    async def record_violation_detection(
        self,
        monitoring_id: str,
        scan_result_id: str,
        detected_url: str,
        similarity_score: float,
        confidence_level: float,
        detection_method: DetectionMethod,
        **kwargs
    ) -> ViolationDetection:
        """
        Record a content violation detection
        
        Args:
            monitoring_id: PlatformMonitoring UUID
            scan_result_id: ScanResult UUID
            detected_url: URL of detected violation
            similarity_score: Similarity score of the match
            confidence_level: Confidence level of detection
            detection_method: Method used for detection
            **kwargs: Additional violation details
            
        Returns:
            Created ViolationDetection instance
        """
        try:
            violation_data = {
                "platform_monitoring_id": monitoring_id,
                "scan_result_id": scan_result_id,
                "detected_url": detected_url,
                "similarity_score": similarity_score,
                "confidence_level": confidence_level,
                "detection_method_used": detection_method,
                "detected_at": datetime.now(timezone.utc),
                **kwargs
            }
            
            # Determine severity based on similarity score
            if similarity_score >= 0.95:
                violation_data["violation_severity"] = "critical"
                violation_data["requires_immediate_action"] = True
            elif similarity_score >= 0.85:
                violation_data["violation_severity"] = "high"
            elif similarity_score >= 0.75:
                violation_data["violation_severity"] = "medium"
            else:
                violation_data["violation_severity"] = "low"
            
            violation_detection = ViolationDetection(**violation_data)
            
            self.db_session.add(violation_detection)
            await self.db_session.commit()
            await self.db_session.refresh(violation_detection)
            
            logger.info(f"Recorded violation detection: {violation_detection.id} with score: {similarity_score}")
            return violation_detection
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to record violation detection: {str(e)}")
            raise
    
    async def get_monitoring_jobs_by_user(
        self,
        user_id: str,
        platform: Optional[MonitoringPlatform] = None,
        status: Optional[MonitoringStatus] = None,
        active_only: bool = True
    ) -> List[PlatformMonitoring]:
        """
        Get monitoring jobs by user with optional filters
        
        Args:
            user_id: User UUID
            platform: Optional platform filter
            status: Optional status filter
            active_only: Only return active monitoring jobs
            
        Returns:
            List of PlatformMonitoring instances
        """
        try:
            query = self.db_session.query(self.model).filter(
                self.model.user_id == user_id
            )
            
            if platform:
                query = query.filter(self.model.platform == platform)
            
            if status:
                query = query.filter(self.model.monitoring_status == status)
            
            if active_only:
                query = query.filter(self.model.is_active == True)
            
            monitoring_jobs = query.order_by(desc(self.model.created_at)).all()
            
            logger.info(f"Retrieved {len(monitoring_jobs)} monitoring jobs for user: {user_id}")
            return monitoring_jobs
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get monitoring jobs by user: {str(e)}")
            raise
    
    async def get_recent_violations(
        self,
        user_id: str,
        days: int = 7,
        severity_filter: Optional[str] = None
    ) -> List[ViolationDetection]:
        """
        Get recent violation detections for a user
        
        Args:
            user_id: User UUID
            days: Number of days to look back
            severity_filter: Optional severity filter
            
        Returns:
            List of ViolationDetection instances
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = self.db_session.query(ViolationDetection).join(
                PlatformMonitoring,
                ViolationDetection.platform_monitoring_id == PlatformMonitoring.id
            ).filter(
                and_(
                    PlatformMonitoring.user_id == user_id,
                    ViolationDetection.detected_at >= cutoff_date
                )
            )
            
            if severity_filter:
                query = query.filter(ViolationDetection.violation_severity == severity_filter)
            
            violations = query.order_by(desc(ViolationDetection.detected_at)).all()
            
            logger.info(f"Retrieved {len(violations)} recent violations for user: {user_id}")
            return violations
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recent violations: {str(e)}")
            raise
    
    async def update_automated_response(
        self,
        violation_id: str,
        response_action: ResponseAction,
        response_sent_at: datetime,
        response_successful: bool = True
    ) -> ViolationDetection:
        """
        Update automated response status for a violation
        
        Args:
            violation_id: ViolationDetection UUID
            response_action: Action taken in response
            response_sent_at: When the response was sent
            response_successful: Whether the response was successful
            
        Returns:
            Updated ViolationDetection instance
        """
        try:
            violation = self.db_session.query(ViolationDetection).filter(
                ViolationDetection.id == violation_id
            ).first()
            
            if not violation:
                raise ValueError(f"Violation detection not found: {violation_id}")
            
            violation.automated_response_sent = True
            violation.response_action_taken = response_action
            violation.response_sent_at = response_sent_at
            
            if response_successful:
                # Update monitoring job success count
                monitoring_job = await self.get_by_id(violation.platform_monitoring_id)
                if monitoring_job:
                    monitoring_job.successful_takedowns += 1
            
            await self.db_session.commit()
            
            logger.info(f"Updated automated response for violation: {violation_id}")
            return violation
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update automated response: {str(e)}")
            raise
    
    async def get_monitoring_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive monitoring analytics for a user
        
        Args:
            user_id: User UUID
            period_days: Analysis period in days
            
        Returns:
            Dictionary containing monitoring analytics
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            
            # Total monitoring jobs
            total_jobs = self.db_session.query(func.count(self.model.id)).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).scalar()
            
            # Active jobs by platform
            platform_distribution = self.db_session.query(
                self.model.platform,
                func.count(self.model.id)
            ).filter(
                self.model.user_id == user_id,
                self.model.monitoring_status == MonitoringStatus.ACTIVE
            ).group_by(self.model.platform).all()
            
            # Scan statistics
            scan_stats = self.db_session.query(
                func.sum(self.model.total_scans_performed).label('total_scans'),
                func.sum(self.model.matches_found).label('total_matches'),
                func.sum(self.model.successful_takedowns).label('total_takedowns'),
                func.avg(self.model.monitoring_cost_daily).label('avg_daily_cost')
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).first()
            
            # Recent violations
            recent_violations = self.db_session.query(
                func.count(ViolationDetection.id).label('total_violations'),
                func.count(ViolationDetection.id).filter(
                    ViolationDetection.violation_severity == 'critical'
                ).label('critical_violations')
            ).join(
                PlatformMonitoring,
                ViolationDetection.platform_monitoring_id == PlatformMonitoring.id
            ).filter(
                and_(
                    PlatformMonitoring.user_id == user_id,
                    ViolationDetection.detected_at >= cutoff_date
                )
            ).first()
            
            # Performance metrics
            performance_stats = self.db_session.query(
                func.avg(self.model.false_positives).label('avg_false_positives'),
                func.count(self.model.id).filter(
                    self.model.consecutive_errors == 0
                ).label('stable_jobs'),
                func.count(self.model.id).filter(
                    self.model.monitoring_status == MonitoringStatus.ERROR
                ).label('error_jobs')
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).first()
            
            analytics = {
                "overview": {
                    "total_monitoring_jobs": total_jobs or 0,
                    "active_platforms": len(platform_distribution),
                    "total_scans_performed": int(scan_stats.total_scans or 0) if scan_stats else 0,
                    "total_matches_found": int(scan_stats.total_matches or 0) if scan_stats else 0,
                    "successful_takedowns": int(scan_stats.total_takedowns or 0) if scan_stats else 0
                },
                "platform_distribution": {
                    platform.value: count for platform, count in platform_distribution
                },
                "violation_metrics": {
                    "total_violations_detected": int(recent_violations.total_violations or 0) if recent_violations else 0,
                    "critical_violations": int(recent_violations.critical_violations or 0) if recent_violations else 0,
                    "violation_detection_rate": 0.0  # To be calculated
                },
                "performance_metrics": {
                    "average_false_positive_rate": float(performance_stats.avg_false_positives or 0) if performance_stats else 0,
                    "stable_monitoring_jobs": int(performance_stats.stable_jobs or 0) if performance_stats else 0,
                    "jobs_with_errors": int(performance_stats.error_jobs or 0) if performance_stats else 0,
                    "system_reliability": 0.0  # To be calculated
                },
                "cost_analysis": {
                    "average_daily_cost": float(scan_stats.avg_daily_cost or 0) if scan_stats else 0,
                    "total_period_cost": float((scan_stats.avg_daily_cost or 0) * period_days) if scan_stats else 0,
                    "cost_per_detection": 0.0  # To be calculated
                }
            }
            
            logger.info(f"Generated monitoring analytics for user: {user_id}")
            return analytics
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get monitoring analytics: {str(e)}")
            raise
    
    async def pause_monitoring_job(
        self,
        monitoring_id: str,
        reason: str = "Manual pause"
    ) -> PlatformMonitoring:
        """
        Pause a monitoring job
        
        Args:
            monitoring_id: PlatformMonitoring UUID
            reason: Reason for pausing
            
        Returns:
            Updated PlatformMonitoring instance
        """
        try:
            monitoring_job = await self.get_by_id(monitoring_id)
            if not monitoring_job:
                raise ValueError(f"Monitoring job not found: {monitoring_id}")
            
            monitoring_job.monitoring_status = MonitoringStatus.PAUSED
            monitoring_job.last_error_message = reason
            
            await self.db_session.commit()
            
            logger.info(f"Paused monitoring job: {monitoring_id} - Reason: {reason}")
            return monitoring_job
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to pause monitoring job: {str(e)}")
            raise
    
    async def resume_monitoring_job(
        self,
        monitoring_id: str
    ) -> PlatformMonitoring:
        """
        Resume a paused monitoring job
        
        Args:
            monitoring_id: PlatformMonitoring UUID
            
        Returns:
            Updated PlatformMonitoring instance
        """
        try:
            monitoring_job = await self.get_by_id(monitoring_id)
            if not monitoring_job:
                raise ValueError(f"Monitoring job not found: {monitoring_id}")
            
            monitoring_job.monitoring_status = MonitoringStatus.ACTIVE
            monitoring_job.consecutive_errors = 0
            monitoring_job.last_error_message = None
            monitoring_job.next_scan_at = datetime.now(timezone.utc) + timedelta(minutes=monitoring_job.scan_frequency_minutes)
            
            await self.db_session.commit()
            
            logger.info(f"Resumed monitoring job: {monitoring_id}")
            return monitoring_job
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to resume monitoring job: {str(e)}")
            raise
