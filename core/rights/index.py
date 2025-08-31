"""
Rights Management Central Orchestrator & API Index
=================================================

Central coordination system for all rights management operations,
providing unified API interface and orchestrating all sub-systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Enterprise Content Protection Platform - Central Rights Orchestrator

  COPYRIGHT NOTICE 
This is proprietary software owned by Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution is strictly prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .rights_manager import RightsManager
from .digital_fingerprint import DigitalFingerprintEngine
from .copyright_detector import CopyrightDetectionService
from .protection_engine import ContentProtectionEngine
from .web_monitoring import WebMonitoringEngine, MonitoringTarget, ViolationResult
from .monetization_engine import MonetizationEngine, RevenueMetrics, RevenueLeak
from .legal_compliance import LegalComplianceEngine, DMCANoticeData
from .notification_system import NotificationEngine, NotificationType, NotificationPriority

from ...utils.monitoring import performance_monitor
from ...utils.cache import enterprise_cache
from ...database.dependencies import get_db_session
from ...security.auth import get_current_user
from ...config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# FastAPI router for rights management endpoints
router = APIRouter(prefix="/api/v1/rights", tags=["Rights Management"])
security = HTTPBearer()


class ProtectionLevel(str, Enum):
    """Content protection levels."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class OperationStatus(str, Enum):
    """Operation status types."""
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    PARTIAL = "partial"


# Pydantic models for API requests/responses
class ContentRegistrationRequest(BaseModel):
    """Content registration request model."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    content_type: str = Field(..., regex="^(audio|video|image|text)$")
    tags: List[str] = Field(default_factory=list)
    protection_level: ProtectionLevel = Field(default=ProtectionLevel.STANDARD)
    commercial_use: bool = Field(default=False)
    platforms_to_monitor: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class ContentRegistrationResponse(BaseModel):
    """Content registration response model."""
    content_id: str
    fingerprint_hash: str
    protection_status: str
    monitoring_active: bool
    registration_date: datetime
    estimated_processing_time: int  # seconds


class ViolationResponse(BaseModel):
    """Violation detection response model."""
    violation_id: str
    content_id: str
    platform: str
    infringing_url: str
    similarity_score: float
    detection_date: datetime
    severity: str
    status: str
    estimated_lost_revenue: Optional[float] = None


class DMCANoticeResponse(BaseModel):
    """DMCA notice response model."""
    notice_id: str
    content_id: str
    platform: str
    status: str
    sent_date: Optional[datetime] = None
    compliance_deadline: Optional[datetime] = None


class RevenueAnalyticsResponse(BaseModel):
    """Revenue analytics response model."""
    total_revenue: float
    platform_breakdown: Dict[str, float]
    period_start: datetime
    period_end: datetime
    detected_leaks: int
    estimated_lost_revenue: float


class RightsOrchestrator:
    """Central orchestrator for all rights management operations."""
    
    def __init__(self):
        self.rights_manager = RightsManager()
        self.fingerprint_engine = DigitalFingerprintEngine()
        self.copyright_detector = CopyrightDetectionService()
        self.protection_engine = ContentProtectionEngine()
        self.web_monitoring = WebMonitoringEngine()
        self.monetization_engine = MonetizationEngine()
        self.legal_compliance = LegalComplianceEngine()
        self.notification_engine = NotificationEngine()
        
        self._initialization_complete = False
    
    async def initialize(self):
        """Initialize all sub-systems."""
        if self._initialization_complete:
            return
        
        try:
            # Start notification processing
            await self.notification_engine.start_processing()
            
            # Initialize monitoring systems
            logger.info("Rights orchestrator initialized successfully")
            self._initialization_complete = True
            
        except Exception as e:
            logger.error(f"Rights orchestrator initialization error: {e}")
            raise
    
    @performance_monitor
    async def register_content_complete(
        self,
        user_id: str,
        content_file: bytes,
        registration_data: ContentRegistrationRequest
    ) -> ContentRegistrationResponse:
        """Complete content registration with full protection setup."""



        
        try:
            # Step 1: Register content rights
            rights_record = await self.rights_manager.register_rights(
                user_id=user_id,
                content_file=content_file,
                content_type=registration_data.content_type,
                title=registration_data.title,
                description=registration_data.description,
                protection_level=registration_data.protection_level,
                commercial_use=registration_data.commercial_use
            )
            
            # Step 2: Generate digital fingerprint
            fingerprint_result = await self.fingerprint_engine.generate_fingerprint(
                content_data=content_file,
                content_type=registration_data.content_type
            )
            
            # Step 3: Set up web monitoring
            monitoring_target = MonitoringTarget(
                content_id=rights_record.id,
                content_hash=fingerprint_result.fingerprint_hash,
                content_type=registration_data.content_type,
                owner_id=user_id,
                platforms=registration_data.platforms_to_monitor,
                keywords=registration_data.keywords or [registration_data.title]
            )
            
            await self.web_monitoring.add_monitoring_target(monitoring_target)
            
            # Step 4: Initialize protection engine
            await self.protection_engine.activate_protection(
                content_id=rights_record.id,
                protection_level=registration_data.protection_level
            )
            
            # Step 5: Send confirmation notification
            await self.notification_engine.send_notification(
                user_id=user_id,
                notification_type=NotificationType.CONTENT_PROTECTED,
                data={
                    'content_title': registration_data.title,
                    'content_id': rights_record.id,
                    'protection_level': registration_data.protection_level,
                    'monitoring_platforms': len(registration_data.platforms_to_monitor)
                },
                priority=NotificationPriority.NORMAL
            )
            
            return ContentRegistrationResponse(
                content_id=rights_record.id,
                fingerprint_hash=fingerprint_result.fingerprint_hash,
                protection_status="active",
                monitoring_active=True,
                registration_date=rights_record.created_at,
                estimated_processing_time=30
            )
            
        except Exception as e:
            logger.error(f"Content registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content registration failed: {str(e)}"
            )
    
    @performance_monitor
    async def handle_violation_detected(
        self,
        violation: ViolationResult,
        auto_action: bool = True
    ) -> Dict[str, Any]:
        """Handle detected content violation with automated response."""



        
        try:
            # Step 1: Verify violation authenticity
            verification_result = await self.copyright_detector.verify_violation(
                violation.content_id,
                violation.url,
                violation.similarity_score
            )
            
            if not verification_result.is_valid:
                logger.info(f"Violation {violation.violation_id} marked as false positive")
                return {'status': 'dismissed', 'reason': 'false_positive'}
            
            # Step 2: Send immediate notification
            await self.notification_engine.send_notification(
                user_id=violation.content_id,  # Assuming content_id maps to user
                notification_type=NotificationType.VIOLATION_DETECTED,
                data={
                    'content_title': violation.metadata.get('title', 'Unknown'),
                    'platform': violation.platform,
                    'similarity': f"{violation.similarity_score * 100:.1f}",
                    'violation_url': violation.url,
                    'detection_time': violation.detection_timestamp.isoformat()
                },
                priority=NotificationPriority.HIGH
            )
            
            # Step 3: Automated DMCA if enabled
            if auto_action and violation.severity in ['high', 'critical']:
                dmca_notice = await self.legal_compliance.generate_dmca_notice(
                    content_id=violation.content_id,
                    copyright_owner=verification_result.owner_name,
                    owner_contact=verification_result.owner_email,
                    infringing_url=violation.url,
                    original_work_description=verification_result.work_description,
                    platform=violation.platform
                )
                
                dmca_sent = await self.legal_compliance.send_automated_dmca_notice(dmca_notice)
                
                if dmca_sent:
                    await self.notification_engine.send_notification(
                        user_id=violation.content_id,
                        notification_type=NotificationType.DMCA_SENT,
                        data={
                            'platform': violation.platform,
                            'content_title': verification_result.work_description,
                            'notice_id': dmca_notice.notice_id
                        },
                        priority=NotificationPriority.NORMAL
                    )
            
            # Step 4: Calculate potential revenue impact
            revenue_impact = await self.monetization_engine.estimate_violation_impact(
                violation.content_id,
                violation.platform,
                violation.metadata
            )
            
            return {
                'status': 'processed',
                'violation_id': violation.violation_id,
                'dmca_sent': auto_action,
                'estimated_lost_revenue': revenue_impact,
                'next_action': 'monitoring_compliance' if auto_action else 'manual_review'
            }
            
        except Exception as e:
            logger.error(f"Violation handling error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @performance_monitor
    async def generate_comprehensive_report(
        self,
        user_id: str,
        date_range: Tuple[datetime, datetime],
        report_type: str = "full"
    ) -> Dict[str, Any]:
        """Generate comprehensive rights management report."""



        
        try:
            # Gather data from all systems
            tasks = [
                self.web_monitoring.get_violation_statistics(user_id),
                self.monetization_engine.get_revenue_analytics(user_id, date_range),
                self.legal_compliance.generate_compliance_report(date_range),
                self.notification_engine.get_notification_statistics(user_id, date_range)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            violation_stats = results[0] if not isinstance(results[0], Exception) else {}
            revenue_analytics = results[1] if not isinstance(results[1], Exception) else {}
            compliance_report = results[2] if not isinstance(results[2], Exception) else {}
            notification_stats = results[3] if not isinstance(results[3], Exception) else {}
            
            # Compile comprehensive report
            report = {
                'user_id': user_id,
                'report_type': report_type,
                'period_start': date_range[0],
                'period_end': date_range[1],
                'generated_at': datetime.utcnow(),
                
                'protection_summary': {
                    'total_content_protected': violation_stats.get('total_content', 0),
                    'active_monitoring_targets': violation_stats.get('active_targets', 0),
                    'violations_detected': violation_stats.get('total_violations', 0),
                    'violations_resolved': violation_stats.get('resolved_violations', 0)
                },
                
                'revenue_summary': {
                    'total_revenue': revenue_analytics.get('total_revenue', 0),
                    'platform_breakdown': revenue_analytics.get('platform_breakdown', {}),
                    'revenue_leaks_detected': revenue_analytics.get('revenue_leaks_detected', 0),
                    'estimated_lost_revenue': revenue_analytics.get('estimated_lost_revenue', 0)
                },
                
                'legal_summary': {
                    'dmca_notices_sent': compliance_report.get('notices_sent', 0),
                    'compliance_rate': compliance_report.get('compliance_rate', 0),
                    'escalated_cases': compliance_report.get('escalated_cases', 0),
                    'recommendations': compliance_report.get('recommendations', [])
                },
                
                'notification_summary': {
                    'total_notifications': notification_stats.get('total_sent', 0),
                    'delivery_rate': notification_stats.get('delivery_rate', 0),
                    'channel_breakdown': notification_stats.get('channel_breakdown', {})
                },
                
                'recommendations': self._generate_actionable_recommendations(
                    violation_stats, revenue_analytics, compliance_report
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            raise
    
    def _generate_actionable_recommendations(
        self,
        violation_stats: Dict,
        revenue_analytics: Dict,
        compliance_report: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on analytics."""
        
        recommendations = []
        
        # Violation-based recommendations
        violation_rate = violation_stats.get('total_violations', 0) / max(
            violation_stats.get('total_content', 1), 1
        )
        
        if violation_rate > 0.1:  # More than 10% violation rate
            recommendations.append(
                "High violation rate detected. Consider upgrading to premium protection level."
            )
        
        # Revenue-based recommendations
        lost_revenue = revenue_analytics.get('estimated_lost_revenue', 0)
        if lost_revenue > 1000:  # More than $1000 lost
            recommendations.append(
                f"Significant revenue loss detected (${lost_revenue}). Recommend aggressive enforcement."
            )
        
        # Compliance-based recommendations
        compliance_rate = compliance_report.get('compliance_rate', 1.0)
        if compliance_rate < 0.7:
            recommendations.append(
                "Low DMCA compliance rate. Consider legal consultation for stronger enforcement."
            )
        
        return recommendations
    
    async def cleanup(self):
        """Cleanup all resources."""
        cleanup_tasks = [
            self.web_monitoring.cleanup(),
            self.monetization_engine.cleanup(),
            self.legal_compliance.cleanup(),
            self.notification_engine.cleanup()
        ]
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        logger.info("Rights orchestrator cleanup completed")


# Global orchestrator instance
orchestrator = RightsOrchestrator()


# FastAPI endpoints
@router.on_event("startup")
async def startup_rights_management():
    """Initialize rights management on startup."""
    await orchestrator.initialize()


@router.on_event("shutdown")
async def shutdown_rights_management():
    """Cleanup rights management on shutdown."""
    await orchestrator.cleanup()


@router.post("/register", response_model=ContentRegistrationResponse)
async def register_content(
    registration_data: ContentRegistrationRequest,
    content_file: bytes,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = None
) -> ContentRegistrationResponse:
    """Register content with full rights protection."""



    
    return await orchestrator.register_content_complete(
        user_id=current_user.id,
        content_file=content_file,
        registration_data=registration_data
    )


@router.get("/violations/{content_id}", response_model=List[ViolationResponse])
async def get_content_violations(
    content_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[ViolationResponse]:
    """Get violations for specific content."""
    
    violations = await orchestrator.web_monitoring.get_violations(content_id)
    
    return [
        ViolationResponse(
            violation_id=v.violation_id,
            content_id=v.content_id,
            platform=v.platform,
            infringing_url=v.url,
            similarity_score=v.similarity_score,
            detection_date=v.detection_timestamp,
            severity=v.severity,
            status=v.status
        )
        for v in violations
    ]


@router.post("/dmca/{violation_id}", response_model=DMCANoticeResponse)
async def send_dmca_notice(
    violation_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DMCANoticeResponse:
    """Send DMCA takedown notice for violation."""
    
    # Get violation details
    violation = await orchestrator.web_monitoring.get_violation_by_id(violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    # Generate and send DMCA notice
    dmca_notice = await orchestrator.legal_compliance.generate_dmca_notice(
        content_id=violation.content_id,
        copyright_owner=current_user.name,
        owner_contact=current_user.email,
        infringing_url=violation.url,
        original_work_description=f"Content ID: {violation.content_id}",
        platform=violation.platform
    )
    
    success = await orchestrator.legal_compliance.send_automated_dmca_notice(dmca_notice)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send DMCA notice")
    
    return DMCANoticeResponse(
        notice_id=dmca_notice.notice_id,
        content_id=violation.content_id,
        platform=violation.platform,
        status=dmca_notice.status,
        sent_date=dmca_notice.date_created,
        compliance_deadline=dmca_notice.date_created + timedelta(days=7)
    )


@router.get("/revenue/{content_id}", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    content_id: str,
    days: int = 30,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> RevenueAnalyticsResponse:
    """Get revenue analytics for content."""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    revenue_metrics = await orchestrator.monetization_engine.calculate_total_revenue(
        content_id=content_id,
        date_range=(start_date, end_date)
    )
    
    revenue_leaks = await orchestrator.monetization_engine.detect_revenue_leaks(
        content_id=content_id,
        expected_revenue=revenue_metrics.total_revenue * 1.2,  # 20% higher expected
        actual_revenue=revenue_metrics.total_revenue,
        platforms=list(revenue_metrics.platform_breakdown.keys())
    )
    
    return RevenueAnalyticsResponse(
        total_revenue=float(revenue_metrics.total_revenue),
        platform_breakdown={k: float(v) for k, v in revenue_metrics.platform_breakdown.items()},
        period_start=start_date,
        period_end=end_date,
        detected_leaks=len(revenue_leaks),
        estimated_lost_revenue=sum(float(leak.estimated_lost_revenue) for leak in revenue_leaks)
    )


@router.get("/report/{user_id}")
async def generate_user_report(
    days: int = 30,
    report_type: str = "full",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Generate comprehensive rights management report."""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return await orchestrator.generate_comprehensive_report(
        user_id=current_user.id,
        date_range=(start_date, end_date),
        report_type=report_type
    )


@router.get("/status")
async def get_rights_system_status() -> Dict[str, Any]:
    """Get overall rights management system status."""



    
    return {
        'status': 'operational',
        'initialized': orchestrator._initialization_complete,
        'active_monitoring_jobs': len(orchestrator.web_monitoring.active_jobs),
        'notifications_queue_size': orchestrator.notification_engine.notification_queue.qsize(),
        'timestamp': datetime.utcnow()
    }


# Export main components
__all__ = [
    'RightsOrchestrator',
    'router',
    'orchestrator',
    'ContentRegistrationRequest',
    'ContentRegistrationResponse',
    'ViolationResponse',
    'DMCANoticeResponse',
    'RevenueAnalyticsResponse'
]
