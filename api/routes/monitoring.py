"""
Monitoring API Routes
Real-time content monitoring and violation detection endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import aiohttp

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monitoring.alerts.violation_detector import ViolationDetector
from ...monitoring.alerts.real_time_scanner import RealTimeScanner
from ...monitoring.alerts.notification_manager import NotificationManager
from ...monitoring.automation.dmca_automation import DMCAAutomation


# Pydantic models
class MonitoringTarget(BaseModel):
    target_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fingerprint_id: str
    platform: str = Field(..., pattern="^(youtube|instagram|tiktok|spotify|facebook|twitter|all)$")
    monitoring_frequency: str = Field(default="hourly", pattern="^(realtime|hourly|daily|weekly)$")
    alert_threshold: float = Field(default=0.8, ge=0.5, le=1.0)
    auto_takedown: bool = Field(default=False)
    notification_channels: List[str] = Field(default=["email"], pattern="^(email|sms|push|slack|webhook)$")


class MonitoringAlert(BaseModel):
    alert_id: str
    target_id: str
    violation_type: str
    platform: str
    detected_url: str
    similarity_score: float
    confidence_level: float
    status: str
    evidence_data: Dict[str, Any]
    detected_at: datetime
    resolved_at: Optional[datetime] = None


class ViolationReport(BaseModel):
    report_id: str
    user_id: str
    fingerprint_id: str
    violations_detected: int
    platforms_monitored: List[str]
    highest_similarity: float
    total_takedowns: int
    pending_actions: int
    report_period: Dict[str, str]
    generated_at: datetime


class DMCARequest(BaseModel):
    target_id: str
    violation_url: str
    evidence_fingerprint_id: str
    claim_type: str = Field(default="copyright", pattern="^(copyright|trademark|privacy)$")
    urgency: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    custom_message: Optional[str] = None


class PlatformScanRequest(BaseModel):
    platform: str
    search_terms: List[str]
    fingerprint_ids: List[str]
    scan_depth: str = Field(default="standard", pattern="^(quick|standard|deep|comprehensive)$")
    time_range: str = Field(default="24h", pattern="^(1h|6h|24h|7d|30d)$")


class MonitoringSettings(BaseModel):
    user_id: str
    auto_monitoring_enabled: bool = Field(default=True)
    notification_preferences: Dict[str, bool]
    alert_threshold: float = Field(default=0.8, ge=0.5, le=1.0)
    auto_takedown_enabled: bool = Field(default=False)
    monitoring_frequency: str = Field(default="hourly")
    platforms_enabled: List[str]


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize monitoring components
violation_detector = ViolationDetector()
real_time_scanner = RealTimeScanner()
notification_manager = NotificationManager()
dmca_automation = DMCAAutomation()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/targets", response_model=Dict[str, str])
async def create_monitoring_target(
    target: MonitoringTarget,
    user: dict = Depends(get_current_user)
):
    """Create a new monitoring target for content protection"""
    try:
        # Verify fingerprint exists and belongs to user
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT cf.fingerprint_id, cf.content_type
                FROM content_fingerprints cf
                JOIN uploaded_files uf ON cf.file_id = uf.file_id
                WHERE cf.fingerprint_id = %s AND uf.user_id = %s
            """, (target.fingerprint_id, user['user_id']))
            
            fingerprint_info = result.fetchone()
            if not fingerprint_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fingerprint not found or access denied"
                )
        
        content_type = fingerprint_info[1]
        
        # Create monitoring target
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO monitoring_targets (target_id, user_id, fingerprint_id, platform,
                                              monitoring_frequency, alert_threshold, auto_takedown,
                                              notification_channels, content_type, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                target.target_id, user['user_id'], target.fingerprint_id, target.platform,
                target.monitoring_frequency, target.alert_threshold, target.auto_takedown,
                target.notification_channels, content_type, "active", datetime.utcnow()
            ))
            await session.commit()
        
        # Start real-time monitoring if requested
        if target.monitoring_frequency == "realtime":
            await real_time_scanner.start_monitoring(target.target_id)
        
        logger.info(f"Monitoring target created: {target.target_id} for user {user['user_id']}")
        
        return {
            "target_id": target.target_id,
            "message": "Monitoring target created successfully",
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Create monitoring target failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitoring target"
        )


@router.get("/targets", response_model=List[Dict[str, Any]])
async def get_monitoring_targets(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get all monitoring targets for the user"""
    try:
        query = """
            SELECT mt.target_id, mt.fingerprint_id, mt.platform, mt.monitoring_frequency,
                   mt.alert_threshold, mt.auto_takedown, mt.notification_channels,
                   mt.status, mt.created_at, mt.last_scan,
                   uf.original_filename, cf.content_type
            FROM monitoring_targets mt
            JOIN content_fingerprints cf ON mt.fingerprint_id = cf.fingerprint_id
            JOIN uploaded_files uf ON cf.file_id = uf.file_id
            WHERE mt.user_id = %s
        """
        params = [user['user_id']]
        
        if platform:
            query += " AND mt.platform = %s"
            params.append(platform)
        
        if status:
            query += " AND mt.status = %s"
            params.append(status)
            
        query += " ORDER BY mt.created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            targets = result.fetchall()
        
        target_list = []
        for target in targets:
            target_list.append({
                "target_id": target[0],
                "fingerprint_id": target[1],
                "platform": target[2],
                "monitoring_frequency": target[3],
                "alert_threshold": target[4],
                "auto_takedown": target[5],
                "notification_channels": target[6],
                "status": target[7],
                "created_at": target[8],
                "last_scan": target[9],
                "filename": target[10],
                "content_type": target[11]
            })
        
        return target_list
        
    except Exception as e:
        logger.error(f"Get monitoring targets failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring targets"
        )


@router.post("/scan", response_model=Dict[str, Any])
async def manual_platform_scan(
    scan_request: PlatformScanRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Manually trigger a platform scan for violations"""
    try:
        scan_id = str(uuid.uuid4())
        
        # Verify all fingerprints belong to user
        async with database_manager.get_postgres_session() as session:
            for fingerprint_id in scan_request.fingerprint_ids:
                result = await session.execute("""
                    SELECT COUNT(*)
                    FROM content_fingerprints cf
                    JOIN uploaded_files uf ON cf.file_id = uf.file_id
                    WHERE cf.fingerprint_id = %s AND uf.user_id = %s
                """, (fingerprint_id, user['user_id']))
                
                count = result.fetchone()[0]
                if count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Fingerprint not found or access denied: {fingerprint_id}"
                    )
        
        # Create scan job
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO platform_scan_jobs (scan_id, user_id, platform, fingerprint_ids,
                                               search_terms, scan_depth, time_range, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                scan_id, user['user_id'], scan_request.platform, scan_request.fingerprint_ids,
                scan_request.search_terms, scan_request.scan_depth, scan_request.time_range,
                "queued", datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule background scan
        background_tasks.add_task(
            _execute_platform_scan, scan_id, scan_request, user
        )
        
        logger.info(f"Manual platform scan initiated: {scan_id}")
        
        return {
            "scan_id": scan_id,
            "platform": scan_request.platform,
            "fingerprint_count": len(scan_request.fingerprint_ids),
            "status": "queued",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Manual platform scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate platform scan"
        )


@router.get("/alerts", response_model=List[MonitoringAlert])
async def get_monitoring_alerts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Field(default=7, ge=1, le=90),
    user: dict = Depends(get_current_user)
):
    """Get monitoring alerts for the user"""
    try:
        query = """
            SELECT alert_id, target_id, violation_type, platform, detected_url,
                   similarity_score, confidence_level, status, evidence_data,
                   detected_at, resolved_at
            FROM monitoring_alerts
            WHERE user_id = %s AND detected_at >= %s
        """
        params = [user['user_id'], datetime.utcnow() - timedelta(days=days)]
        
        if platform:
            query += " AND platform = %s"
            params.append(platform)
        
        if status:
            query += " AND status = %s"
            params.append(status)
            
        query += " ORDER BY detected_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            alerts = result.fetchall()
        
        alert_list = []
        for alert in alerts:
            alert_list.append(MonitoringAlert(
                alert_id=alert[0],
                target_id=alert[1],
                violation_type=alert[2],
                platform=alert[3],
                detected_url=alert[4],
                similarity_score=alert[5],
                confidence_level=alert[6],
                status=alert[7],
                evidence_data=alert[8],
                detected_at=alert[9],
                resolved_at=alert[10]
            ))
        
        return alert_list
        
    except Exception as e:
        logger.error(f"Get monitoring alerts failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring alerts"
        )


@router.post("/dmca", response_model=Dict[str, str])
async def submit_dmca_takedown(
    dmca_request: DMCARequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Submit DMCA takedown request"""
    try:
        # Verify target ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT mt.target_id, cf.fingerprint_data
                FROM monitoring_targets mt
                JOIN content_fingerprints cf ON mt.fingerprint_id = cf.fingerprint_id
                JOIN uploaded_files uf ON cf.file_id = uf.file_id
                WHERE mt.target_id = %s AND uf.user_id = %s
            """, (dmca_request.target_id, user['user_id']))
            
            target_info = result.fetchone()
            if not target_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target not found or access denied"
                )
        
        dmca_id = str(uuid.uuid4())
        
        # Create DMCA request record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO dmca_requests (dmca_id, user_id, target_id, violation_url,
                                         evidence_fingerprint_id, claim_type, urgency,
                                         custom_message, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dmca_id, user['user_id'], dmca_request.target_id, dmca_request.violation_url,
                dmca_request.evidence_fingerprint_id, dmca_request.claim_type,
                dmca_request.urgency, dmca_request.custom_message, "pending", datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule DMCA automation
        background_tasks.add_task(
            _process_dmca_request, dmca_id, dmca_request, user
        )
        
        logger.info(f"DMCA takedown submitted: {dmca_id}")
        
        return {
            "dmca_id": dmca_id,
            "status": "pending",
            "message": "DMCA takedown request submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"DMCA submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit DMCA request"
        )


@router.get("/reports/violations", response_model=ViolationReport)
async def get_violation_report(
    days: int = Field(default=30, ge=1, le=365),
    user: dict = Depends(get_current_user)
):
    """Generate violation detection report"""
    try:
        report_id = str(uuid.uuid4())
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        # Get violation statistics
        async with database_manager.get_postgres_session() as session:
            # Count violations
            result = await session.execute("""
                SELECT COUNT(*) FROM monitoring_alerts
                WHERE user_id = %s AND detected_at >= %s AND detected_at <= %s
            """, (user['user_id'], start_date, end_date))
            violations_count = result.fetchone()[0]
            
            # Get platforms monitored
            result = await session.execute("""
                SELECT DISTINCT platform FROM monitoring_alerts
                WHERE user_id = %s AND detected_at >= %s AND detected_at <= %s
            """, (user['user_id'], start_date, end_date))
            platforms = [row[0] for row in result.fetchall()]
            
            # Get highest similarity
            result = await session.execute("""
                SELECT MAX(similarity_score) FROM monitoring_alerts
                WHERE user_id = %s AND detected_at >= %s AND detected_at <= %s
            """, (user['user_id'], start_date, end_date))
            highest_similarity = result.fetchone()[0] or 0.0
            
            # Count takedowns
            result = await session.execute("""
                SELECT COUNT(*) FROM dmca_requests
                WHERE user_id = %s AND created_at >= %s AND created_at <= %s
                  AND status = 'completed'
            """, (user['user_id'], start_date, end_date))
            takedowns_count = result.fetchone()[0]
            
            # Count pending actions
            result = await session.execute("""
                SELECT COUNT(*) FROM monitoring_alerts
                WHERE user_id = %s AND detected_at >= %s AND detected_at <= %s
                  AND status = 'pending'
            """, (user['user_id'], start_date, end_date))
            pending_count = result.fetchone()[0]
        
        report = ViolationReport(
            report_id=report_id,
            user_id=user['user_id'],
            fingerprint_id="",  # General report
            violations_detected=violations_count,
            platforms_monitored=platforms,
            highest_similarity=highest_similarity,
            total_takedowns=takedowns_count,
            pending_actions=pending_count,
            report_period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"Violation report generated: {report_id}")
        
        return report
        
    except Exception as e:
        logger.error(f"Generate violation report failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate violation report"
        )


@router.put("/settings", response_model=Dict[str, str])
async def update_monitoring_settings(
    settings: MonitoringSettings,
    user: dict = Depends(get_current_user)
):
    """Update user monitoring settings"""
    try:
        # Update or insert monitoring settings
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO monitoring_settings (user_id, auto_monitoring_enabled, 
                                               notification_preferences, alert_threshold,
                                               auto_takedown_enabled, monitoring_frequency,
                                               platforms_enabled, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    auto_monitoring_enabled = EXCLUDED.auto_monitoring_enabled,
                    notification_preferences = EXCLUDED.notification_preferences,
                    alert_threshold = EXCLUDED.alert_threshold,
                    auto_takedown_enabled = EXCLUDED.auto_takedown_enabled,
                    monitoring_frequency = EXCLUDED.monitoring_frequency,
                    platforms_enabled = EXCLUDED.platforms_enabled,
                    updated_at = EXCLUDED.updated_at
            """, (
                user['user_id'], settings.auto_monitoring_enabled,
                settings.notification_preferences, settings.alert_threshold,
                settings.auto_takedown_enabled, settings.monitoring_frequency,
                settings.platforms_enabled, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"Monitoring settings updated for user {user['user_id']}")
        
        return {"message": "Monitoring settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Update monitoring settings failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monitoring settings"
        )


@router.delete("/targets/{target_id}")
async def delete_monitoring_target(
    target_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a monitoring target"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Verify ownership
            result = await session.execute("""
                SELECT target_id FROM monitoring_targets
                WHERE target_id = %s AND user_id = %s
            """, (target_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target not found or access denied"
                )
            
            # Delete target
            await session.execute("""
                DELETE FROM monitoring_targets WHERE target_id = %s
            """, (target_id,))
            await session.commit()
        
        # Stop real-time monitoring
        await real_time_scanner.stop_monitoring(target_id)
        
        logger.info(f"Monitoring target deleted: {target_id}")
        
        return {"message": "Monitoring target deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete monitoring target failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete monitoring target"
        )


# Background task functions
async def _execute_platform_scan(scan_id: str, scan_request: PlatformScanRequest, user: dict):
    """Execute platform scan in background"""
    try:
        # Update scan status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE platform_scan_jobs 
                SET status = 'processing', started_at = %s
                WHERE scan_id = %s
            """, (datetime.utcnow(), scan_id))
            await session.commit()
        
        # Execute scan based on platform
        violations_found = []
        
        if scan_request.platform in ["youtube", "all"]:
            violations_found.extend(await _scan_youtube(scan_request, user))
        
        if scan_request.platform in ["instagram", "all"]:
            violations_found.extend(await _scan_instagram(scan_request, user))
        
        if scan_request.platform in ["tiktok", "all"]:
            violations_found.extend(await _scan_tiktok(scan_request, user))
        
        # Store results
        async with database_manager.get_postgres_session() as session:
            for violation in violations_found:
                alert_id = str(uuid.uuid4())
                await session.execute("""
                    INSERT INTO monitoring_alerts (alert_id, user_id, target_id, violation_type,
                                                 platform, detected_url, similarity_score,
                                                 confidence_level, status, evidence_data, detected_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    alert_id, user['user_id'], violation.get('target_id', ''),
                    violation['violation_type'], violation['platform'], violation['url'],
                    violation['similarity_score'], violation['confidence_level'],
                    'pending', violation['evidence'], datetime.utcnow()
                ))
            
            # Update scan job
            await session.execute("""
                UPDATE platform_scan_jobs 
                SET status = 'completed', completed_at = %s, violations_found = %s
                WHERE scan_id = %s
            """, (datetime.utcnow(), len(violations_found), scan_id))
            await session.commit()
        
        # Send notifications
        if violations_found:
            await notification_manager.send_violation_alerts(user['user_id'], violations_found)
        
        logger.info(f"Platform scan completed: {scan_id}, {len(violations_found)} violations found")
        
    except Exception as e:
        logger.error(f"Platform scan execution failed: {e}")
        
        # Mark scan as failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE platform_scan_jobs 
                SET status = 'failed', error_message = %s
                WHERE scan_id = %s
            """, (str(e), scan_id))
            await session.commit()


async def _process_dmca_request(dmca_id: str, dmca_request: DMCARequest, user: dict):
    """Process DMCA takedown request"""
    try:
        # Update status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE dmca_requests 
                SET status = 'processing', started_at = %s
                WHERE dmca_id = %s
            """, (datetime.utcnow(), dmca_id))
            await session.commit()
        
        # Generate DMCA notice
        dmca_notice = await dmca_automation.generate_dmca_notice(
            dmca_request, user
        )
        
        # Submit to platform
        submission_result = await dmca_automation.submit_to_platform(
            dmca_request.violation_url, dmca_notice
        )
        
        # Update request with results
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE dmca_requests 
                SET status = %s, dmca_notice = %s, platform_response = %s, completed_at = %s
                WHERE dmca_id = %s
            """, (
                submission_result['status'], dmca_notice,
                submission_result['response'], datetime.utcnow(), dmca_id
            ))
            await session.commit()
        
        # Send notification
        await notification_manager.send_dmca_status_update(user['user_id'], dmca_id, submission_result)
        
        logger.info(f"DMCA request processed: {dmca_id}")
        
    except Exception as e:
        logger.error(f"DMCA processing failed: {e}")
        
        # Mark as failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE dmca_requests 
                SET status = 'failed', error_message = %s
                WHERE dmca_id = %s
            """, (str(e), dmca_id))
            await session.commit()


# Platform-specific scanning functions
async def _scan_youtube(scan_request: PlatformScanRequest, user: dict) -> List[Dict[str, Any]]:
    """Scan YouTube for violations"""
    # Implementation would use YouTube API to search for content
    # This is a placeholder implementation
    return []


async def _scan_instagram(scan_request: PlatformScanRequest, user: dict) -> List[Dict[str, Any]]:
    """Scan Instagram for violations"""
    # Implementation would use Instagram API to search for content
    # This is a placeholder implementation
    return []


async def _scan_tiktok(scan_request: PlatformScanRequest, user: dict) -> List[Dict[str, Any]]:
    """Scan TikTok for violations"""
    # Implementation would use TikTok API to search for content
    # This is a placeholder implementation
    return []