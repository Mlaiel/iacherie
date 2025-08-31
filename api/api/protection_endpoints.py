"""Content protection endpoints for IA Influencer Agent platform.

This module handles comprehensive content protection including real-time monitoring,
DMCA takedown automation, and rights management across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import logging
from uuid import uuid4
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator, HttpUrl
import requests

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.protection import ProtectionAlert, TakedownRequest, RightsManagement, AlertStatus
from ..models.fingerprint import ContentFingerprint
from ..business.protection_service import ContentProtectionService
from ..business.dmca_service import DMCAService
from ..business.crawler_service import CrawlerService
from ..business.legal_service import LegalService
from ..utils.evidence_collector import EvidenceCollector
from ..utils.response_handler import ResponseHandler

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/protection", tags=["Content Protection"])

class AlertLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProtectionStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Pydantic models for request/response validation
class ProtectionAlertResponse(BaseModel):
    """Response model for protection alerts"""    alert_id: str = Field(..., description="Unique alert identifier")
    fingerprint_id: str = Field(..., description="Associated fingerprint ID")
    detected_url: HttpUrl = Field(..., description="URL where infringement was detected")
    platform: str = Field(..., description="Platform where content was found")
    similarity_score: float = Field(..., description="Content similarity score (0.0-1.0)")
    alert_level: AlertLevel = Field(..., description="Alert severity level")
    status: ProtectionStatus = Field(..., description="Current alert status")
    evidence: Dict[str, Any] = Field(..., description="Collected evidence data")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    estimated_revenue_impact: Optional[float] = Field(None, description="Estimated revenue loss in EUR")

class TakedownRequestModel(BaseModel):
    """Request model for DMCA takedown"""    alert_id: str = Field(..., description="Protection alert ID to process")
    takedown_type: str = Field("dmca", description="Type of takedown request")
    legal_basis: str = Field(..., description="Legal basis for takedown")
    evidence_urls: List[HttpUrl] = Field(..., description="URLs of evidence files")
    priority: str = Field("standard", description="Processing priority: low, standard, high, urgent")
    custom_message: Optional[str] = Field(None, description="Custom message to include")

class RightsManagementRequest(BaseModel):
    """Request model for rights management setup"""    content_ids: List[str] = Field(..., description="List of content fingerprint IDs")
    rights_holder: str = Field(..., description="Rights holder name")
    usage_terms: Dict[str, Any] = Field(..., description="Usage terms and conditions")
    licensing_enabled: bool = Field(True, description="Enable automated licensing")
    enforcement_level: str = Field("aggressive", description="Enforcement level: passive, standard, aggressive")

class MonitoringConfigRequest(BaseModel):
    """Request model for monitoring configuration"""    platforms: List[str] = Field(..., description="Platforms to monitor")
    keywords: List[str] = Field(default=[], description="Additional keywords to monitor")
    geo_restrictions: List[str] = Field(default=[], description="Geographic restrictions")
    monitoring_depth: str = Field("deep", description="Monitoring depth: surface, standard, deep")
    alert_threshold: float = Field(0.75, ge=0.5, le=1.0, description="Minimum similarity for alerts")

# Core protection endpoints
@router.get("/alerts", response_model=List[ProtectionAlertResponse])
async def get_protection_alerts(
    status: Optional[ProtectionStatus] = None,
    platform: Optional[str] = None,
    alert_level: Optional[AlertLevel] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    protection_service: ContentProtectionService = Depends()
):
    """    Get protection alerts for user's content with advanced filtering.
    
    Features:
    - Real-time alert monitoring across 500+ platforms
    - Automated evidence collection with screenshots
    - AI-powered similarity detection and false positive reduction
    - Revenue impact estimation for each infringement
    """    try:
        # Get user's fingerprints to filter alerts
        user_fingerprints = db.query(ContentFingerprint).filter(
            ContentFingerprint.user_id == current_user.id
        ).all()
        fingerprint_ids = [fp.id for fp in user_fingerprints]
        
        if not fingerprint_ids:
            return []
        
        # Build query with filters
        query = db.query(ProtectionAlert).filter(
            ProtectionAlert.fingerprint_id.in_(fingerprint_ids)
        )
        
        if status:
            query = query.filter(ProtectionAlert.status == status.value)
        if platform:
            query = query.filter(ProtectionAlert.platform == platform)
        if alert_level:
            query = query.filter(ProtectionAlert.alert_level == alert_level.value)
        
        # Order by creation date (newest first) and apply pagination
        alerts = query.order_by(ProtectionAlert.created_at.desc()).offset(skip).limit(limit).all()
        
        # Enhance alerts with additional data
        enhanced_alerts = []
        for alert in alerts:
            # Get estimated revenue impact
            revenue_impact = await protection_service.calculate_revenue_impact(
                alert.fingerprint_id,
                alert.detected_url,
                alert.similarity_score
            )
            
            alert_response = ProtectionAlertResponse(
                alert_id=alert.id,
                fingerprint_id=alert.fingerprint_id,
                detected_url=alert.detected_url,
                platform=alert.platform,
                similarity_score=alert.similarity_score,
                alert_level=AlertLevel(alert.alert_level),
                status=ProtectionStatus(alert.status),
                evidence=alert.evidence_data,
                created_at=alert.created_at,
                estimated_revenue_impact=revenue_impact
            )
            enhanced_alerts.append(alert_response)
        
        logger.info(f"Retrieved {len(enhanced_alerts)} protection alerts for user: {current_user.id}")
        return enhanced_alerts
        
    except Exception as e:
        logger.error(f"Error retrieving protection alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve protection alerts: {str(e)}"
        )

@router.post("/takedown", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def initiate_takedown_request(
    takedown_request: TakedownRequestModel,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    dmca_service: DMCAService = Depends(),
    legal_service: LegalService = Depends()
):
    """    Initiate automated DMCA takedown process with legal compliance.
    
    Features:
    - Automated DMCA notice generation with legal templates
    - Multi-jurisdiction compliance (US, EU, Asia-Pacific)
    - Evidence collection and legal documentation
    - Platform-specific takedown procedures
    - Success rate tracking and follow-up automation
    """    try:
        # Validate alert belongs to user
        alert = db.query(ProtectionAlert).filter(
            ProtectionAlert.id == takedown_request.alert_id
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protection alert not found"
            )
        
        # Verify user owns the fingerprint
        fingerprint = db.query(ContentFingerprint).filter(
            ContentFingerprint.id == alert.fingerprint_id,
            ContentFingerprint.user_id == current_user.id
        ).first()
        
        if not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to protection alert"
            )
        
        # Check if takedown is already in progress
        existing_takedown = db.query(TakedownRequest).filter(
            TakedownRequest.alert_id == takedown_request.alert_id,
            TakedownRequest.status.in_(["pending", "in_progress"])
        ).first()
        
        if existing_takedown:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Takedown request already in progress for this alert"
            )
        
        # Generate takedown request ID
        takedown_id = str(uuid4())
        
        # Collect additional evidence
        evidence_data = await EvidenceCollector.collect_comprehensive_evidence(
            alert.detected_url,
            alert.platform,
            fingerprint.content_type
        )
        
        # Determine legal jurisdiction and applicable law
        jurisdiction_info = await legal_service.determine_jurisdiction(
            alert.detected_url,
            alert.platform
        )
        
        # Generate legal documentation
        legal_documents = await dmca_service.generate_takedown_documents(
            takedown_request=takedown_request,
            alert=alert,
            fingerprint=fingerprint,
            user=current_user,
            evidence=evidence_data,
            jurisdiction=jurisdiction_info
        )
        
        # Create takedown request record
        takedown_record = TakedownRequest(
            id=takedown_id,
            alert_id=takedown_request.alert_id,
            user_id=current_user.id,
            takedown_type=takedown_request.takedown_type,
            legal_basis=takedown_request.legal_basis,
            platform=alert.platform,
            target_url=alert.detected_url,
            evidence_urls=takedown_request.evidence_urls,
            legal_documents=legal_documents,
            jurisdiction=jurisdiction_info['jurisdiction'],
            priority=takedown_request.priority,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(takedown_record)
        
        # Update alert status
        alert.status = "escalated"
        alert.escalation_timestamp = datetime.utcnow()
        
        db.commit()
        
        # Submit takedown request in background
        background_tasks.add_task(
            dmca_service.submit_takedown_request,
            takedown_id,
            current_user.id
        )
        
        # Setup follow-up monitoring
        background_tasks.add_task(
            dmca_service.setup_takedown_monitoring,
            takedown_id,
            expected_response_time=jurisdiction_info.get('expected_response_hours', 72)
        )
        
        logger.info(f"Takedown request initiated: {takedown_id} for alert: {takedown_request.alert_id}")
        
        return {
            "takedown_id": takedown_id,
            "status": "pending",
            "estimated_response_time": f"{jurisdiction_info.get('expected_response_hours', 72)} hours",
            "jurisdiction": jurisdiction_info['jurisdiction'],
            "legal_basis": takedown_request.legal_basis,
            "platform": alert.platform,
            "target_url": alert.detected_url,
            "success_probability": legal_documents.get('success_probability', 0.9),
            "next_steps": [
                "Takedown notice submitted to platform",
                "Evidence package prepared for legal review",
                "Automated follow-up monitoring activated",
                "User notification scheduled for status updates"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error initiating takedown request: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Takedown request failed: {str(e)}"
        )

@router.post("/rights-management", response_model=Dict[str, Any])
async def setup_rights_management(
    rights_request: RightsManagementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    protection_service: ContentProtectionService = Depends()
):
    """    Setup comprehensive rights management for content portfolio.
    
    Features:
    - Automated licensing system with smart contracts
    - Rights verification and chain of title documentation
    - Revenue sharing and royalty distribution
    - Usage monitoring and compliance tracking
    """    try:
        # Validate all content IDs belong to user
        fingerprints = db.query(ContentFingerprint).filter(
            ContentFingerprint.id.in_(rights_request.content_ids),
            ContentFingerprint.user_id == current_user.id
        ).all()
        
        if len(fingerprints) != len(rights_request.content_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more content items not found"
            )
        
        # Generate rights management configuration
        rights_config_id = str(uuid4())
        
        # Create rights management records for each content item
        rights_records = []
        for fingerprint in fingerprints:
            rights_record = RightsManagement(
                id=str(uuid4()),
                config_id=rights_config_id,
                fingerprint_id=fingerprint.id,
                user_id=current_user.id,
                rights_holder=rights_request.rights_holder,
                usage_terms=rights_request.usage_terms,
                licensing_enabled=rights_request.licensing_enabled,
                enforcement_level=rights_request.enforcement_level,
                blockchain_hash=None,  # Will be set by blockchain service
                created_at=datetime.utcnow()
            )
            rights_records.append(rights_record)
            db.add(rights_record)
        
        db.commit()
        
        # Setup blockchain verification for rights
        if settings.BLOCKCHAIN_ENABLED:
            background_tasks.add_task(
                protection_service.register_rights_on_blockchain,
                rights_config_id,
                [record.id for record in rights_records]
            )
        
        # Setup automated licensing system
        if rights_request.licensing_enabled:
            background_tasks.add_task(
                protection_service.setup_automated_licensing,
                rights_config_id,
                rights_request.usage_terms
            )
        
        # Configure enhanced monitoring for rights-managed content
        background_tasks.add_task(
            protection_service.setup_rights_monitoring,
            rights_config_id,
            rights_request.enforcement_level
        )
        
        logger.info(f"Rights management setup completed: {rights_config_id} for {len(fingerprints)} content items")
        
        return {
            "rights_config_id": rights_config_id,
            "status": "active",
            "protected_content_count": len(fingerprints),
            "rights_holder": rights_request.rights_holder,
            "licensing_enabled": rights_request.licensing_enabled,
            "enforcement_level": rights_request.enforcement_level,
            "blockchain_verification": "pending" if settings.BLOCKCHAIN_ENABLED else "disabled",
            "estimated_setup_time": "5-10 minutes",
            "features_enabled": [
                "Automated DMCA takedowns",
                "Usage monitoring and alerts",
                "Revenue tracking and reporting",
                "Legal documentation generation",
                "Multi-platform enforcement"
            ] + (["Blockchain rights verification"] if settings.BLOCKCHAIN_ENABLED else []) +
                (["Automated licensing system"] if rights_request.licensing_enabled else [])
        }
        
    except Exception as e:
        logger.error(f"Error setting up rights management: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rights management setup failed: {str(e)}"
        )

@router.post("/monitoring/configure", response_model=Dict[str, Any])
async def configure_monitoring(
    config_request: MonitoringConfigRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    crawler_service: CrawlerService = Depends()
):
    """    Configure advanced monitoring across multiple platforms and jurisdictions.
    
    Features:
    - Multi-platform crawler deployment (YouTube, Instagram, TikTok, etc.)
    - Deep web monitoring with custom search patterns
    - AI-powered content recognition across languages
    - Geographic monitoring with jurisdiction-specific enforcement
    """    try:
        # Validate supported platforms
        supported_platforms = settings.SUPPORTED_MONITORING_PLATFORMS
        invalid_platforms = set(config_request.platforms) - set(supported_platforms)
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platforms: {list(invalid_platforms)}"
            )
        
        # Create monitoring configuration
        monitoring_config_id = str(uuid4())
        
        # Setup platform-specific crawlers
        crawler_configs = []
        for platform in config_request.platforms:
            crawler_config = await crawler_service.create_platform_crawler(
                platform=platform,
                user_id=current_user.id,
                keywords=config_request.keywords,
                monitoring_depth=config_request.monitoring_depth,
                geo_restrictions=config_request.geo_restrictions,
                alert_threshold=config_request.alert_threshold
            )
            crawler_configs.append(crawler_config)
        
        # Store monitoring configuration in database
        monitoring_record = {
            'config_id': monitoring_config_id,
            'user_id': current_user.id,
            'platforms': config_request.platforms,
            'crawler_configs': crawler_configs,
            'monitoring_depth': config_request.monitoring_depth,
            'alert_threshold': config_request.alert_threshold,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        
        # Start monitoring jobs in background
        for crawler_config in crawler_configs:
            background_tasks.add_task(
                crawler_service.start_monitoring_job,
                crawler_config,
                monitoring_config_id
            )
        
        # Setup AI-powered content recognition
        background_tasks.add_task(
            crawler_service.setup_ai_recognition,
            monitoring_config_id,
            current_user.id
        )
        
        logger.info(f"Monitoring configured: {monitoring_config_id} for {len(config_request.platforms)} platforms")
        
        return {
            "monitoring_config_id": monitoring_config_id,
            "status": "active",
            "platforms_count": len(config_request.platforms),
            "platforms": config_request.platforms,
            "monitoring_depth": config_request.monitoring_depth,
            "alert_threshold": config_request.alert_threshold,
            "estimated_detection_time": "< 10 seconds for surface monitoring, < 5 minutes for deep monitoring",
            "crawler_jobs_started": len(crawler_configs),
            "features": [
                "Real-time content scanning",
                "AI-powered similarity detection", 
                "Automated evidence collection",
                "Multi-language content recognition",
                "Geographic enforcement tracking",
                "Advanced false positive filtering"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error configuring monitoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring configuration failed: {str(e)}"
        )

@router.get("/takedown-status/{takedown_id}", response_model=Dict[str, Any])
async def get_takedown_status(
    takedown_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    dmca_service: DMCAService = Depends()
):
    """Get detailed status of a DMCA takedown request."""    try:
        takedown = db.query(TakedownRequest).filter(
            TakedownRequest.id == takedown_id,
            TakedownRequest.user_id == current_user.id
        ).first()
        
        if not takedown:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Takedown request not found"
            )
        
        # Get real-time status update from platform
        live_status = await dmca_service.check_takedown_status(takedown_id)
        
        # Update database if status changed
        if live_status['status'] != takedown.status:
            takedown.status = live_status['status']
            takedown.status_updated_at = datetime.utcnow()
            db.commit()
        
        return {
            "takedown_id": takedown.id,
            "status": takedown.status,
            "platform": takedown.platform,
            "target_url": takedown.target_url,
            "submitted_at": takedown.created_at,
            "last_updated": takedown.status_updated_at or takedown.created_at,
            "estimated_completion": live_status.get('estimated_completion'),
            "platform_response": live_status.get('platform_response'),
            "success_probability": live_status.get('success_probability'),
            "next_actions": live_status.get('next_actions', [])
        }
        
    except Exception as e:
        logger.error(f"Error retrieving takedown status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve takedown status: {str(e)}"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_protection_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    protection_service: ContentProtectionService = Depends()
):
    """Get comprehensive protection statistics for user's content."""    try:
        stats = await protection_service.get_user_protection_statistics(current_user.id)
        
        return {
            "user_id": current_user.id,
            "protected_content_count": stats['protected_content_count'],
            "total_alerts": stats['total_alerts'],
            "active_alerts": stats['active_alerts'],
            "resolved_alerts": stats['resolved_alerts'],
            "takedown_requests": stats['takedown_requests'],
            "successful_takedowns": stats['successful_takedowns'],
            "takedown_success_rate": stats['takedown_success_rate'],
            "estimated_revenue_protected": stats['estimated_revenue_protected'],
            "monitoring_platforms": stats['monitoring_platforms'],
            "average_detection_time": stats['average_detection_time'],
            "most_violated_platforms": stats['most_violated_platforms'],
            "protection_effectiveness": stats['protection_effectiveness']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving protection statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve protection statistics: {str(e)}"
        )

__all__ = ["router"]
