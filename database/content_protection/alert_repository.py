"""
Protection Alert Repository

Enterprise-grade alert management system for content protection violations
with real-time monitoring, advanced analytics, and automated response capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models.content_models import (
    ProtectionAlert, ContentFingerprint, ViolationReport,
    AlertEscalation, AlertResponse, PlatformContact
)
from ..security.encryption import AdvancedEncryptionManager
from ..monitoring.alert_monitor import AlertMonitor
from ...core.config import DatabaseConfig
from ...utils.notifications import NotificationManager
from ...utils.validators import ValidationManager


logger = logging.getLogger(__name__)


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status types"""
    PENDING = "pending"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    FALSE_POSITIVE = "false_positive"


class AlertCategory(Enum):
    """Alert categories"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    CONTENT_MANIPULATION = "content_manipulation"
    TRADEMARK_VIOLATION = "trademark_violation"
    BRAND_IMPERSONATION = "brand_impersonation"
    DEEPFAKE_DETECTION = "deepfake_detection"


class ProtectionAlertRepositoryError(Exception):
    """Custom exception for alert repository operations"""
    pass


class ProtectionAlertRepository:
    """
    Ultra-advanced protection alert repository with enterprise features:
    - Real-time alert processing and intelligent routing
    - Advanced alert correlation and pattern recognition
    - Automated escalation and response workflows
    - Multi-channel notification system
    - Comprehensive analytics and reporting
    - Integration with legal action systems
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        config: DatabaseConfig,
        encryption_manager: Optional[AdvancedEncryptionManager] = None,
        notification_manager: Optional[NotificationManager] = None,
        alert_monitor: Optional[AlertMonitor] = None
    ):
        self.db_session = db_session
        self.config = config
        self.encryption_manager = encryption_manager or AdvancedEncryptionManager()
        self.notification_manager = notification_manager or NotificationManager()
        self.alert_monitor = alert_monitor or AlertMonitor()
        self.validator = ValidationManager()
        
        # Alert processing settings
        self.batch_size = config.alert_batch_size or 500
        self.escalation_thresholds = config.escalation_thresholds or {
            "high_similarity": 0.95,
            "multiple_platforms": 3,
            "repeat_offender": 5,
            "commercial_use": True
        }
        
        # Alert correlation settings
        self.correlation_window_hours = 24
        self.correlation_similarity_threshold = 0.85
        
        # Performance metrics
        self.alert_metrics = {
            "total_alerts": 0,
            "pending_alerts": 0,
            "resolved_alerts": 0,
            "false_positives": 0,
            "avg_resolution_time_hours": 0,
            "escalation_rate": 0
        }
        
        logger.info("ProtectionAlertRepository initialized with enterprise configuration")
    
    async def create_alert(
        self,
        fingerprint_id: UUID,
        detection_data: Dict[str, Any],
        alert_priority: AlertPriority = AlertPriority.MEDIUM,
        auto_escalate: bool = True
    ) -> ProtectionAlert:
        """
        Create new protection alert with intelligent categorization
        
        Args:
            fingerprint_id: Associated content fingerprint ID
            detection_data: Comprehensive detection data
            alert_priority: Initial alert priority
            auto_escalate: Enable automatic escalation
            
        Returns:
            Created ProtectionAlert record
            
        Raises:
            ProtectionAlertRepositoryError: If creation fails
        """
        try:
            # Validate detection data
            await self._validate_detection_data(detection_data)
            
            # Determine alert category
            alert_category = await self._categorize_alert(detection_data)
            
            # Check for correlation with existing alerts
            correlations = await self._find_correlated_alerts(
                fingerprint_id, detection_data
            )
            
            # Adjust priority based on correlations
            if correlations:
                alert_priority = await self._adjust_priority_for_correlations(
                    alert_priority, correlations
                )
            
            # Encrypt sensitive detection data
            encrypted_data = await self.encryption_manager.encrypt_data(
                json.dumps(detection_data)
            )
            
            # Create alert record
            alert = ProtectionAlert(
                id=uuid4(),
                fingerprint_id=fingerprint_id,
                alert_category=alert_category.value,
                alert_priority=alert_priority.value,
                status=AlertStatus.PENDING.value,
                detected_url=detection_data.get("detected_url"),
                platform=detection_data.get("platform"),
                similarity_score=detection_data.get("similarity_score", 0.0),
                detection_method=detection_data.get("detection_method"),
                evidence_data=encrypted_data,
                correlation_ids=[str(corr.id) for corr in correlations],
                metadata={
                    "auto_escalate": auto_escalate,
                    "detection_timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_system": detection_data.get("source_system", "unknown")
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(alert)
            await self.db_session.commit()
            
            # Trigger automatic escalation if enabled
            if auto_escalate and await self._should_auto_escalate(alert):
                await self.escalate_alert(alert.id, "automatic_escalation")
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            # Update metrics
            self.alert_metrics["total_alerts"] += 1
            self.alert_metrics["pending_alerts"] += 1
            
            logger.info(f"Protection alert created: {alert.id} [{alert_category.value}]")
            return alert
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Alert creation failed: {e}")
            raise ProtectionAlertRepositoryError(f"Alert creation failed: {e}")
    
    async def get_pending_alerts(
        self,
        priority_filter: Optional[List[AlertPriority]] = None,
        category_filter: Optional[List[AlertCategory]] = None,
        platform_filter: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ProtectionAlert]:
        """
        Retrieve pending alerts with advanced filtering
        
        Args:
            priority_filter: Filter by alert priorities
            category_filter: Filter by alert categories
            platform_filter: Filter by platforms
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of ProtectionAlert records
        """
        try:
            query = self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.status == AlertStatus.PENDING.value
            )
            
            # Apply filters
            if priority_filter:
                priority_values = [p.value for p in priority_filter]
                query = query.filter(ProtectionAlert.alert_priority.in_(priority_values))
            
            if category_filter:
                category_values = [c.value for c in category_filter]
                query = query.filter(ProtectionAlert.alert_category.in_(category_values))
            
            if platform_filter:
                query = query.filter(ProtectionAlert.platform.in_(platform_filter))
            
            # Order by priority and creation time
            priority_order = {
                AlertPriority.EMERGENCY.value: 1,
                AlertPriority.CRITICAL.value: 2,
                AlertPriority.HIGH.value: 3,
                AlertPriority.MEDIUM.value: 4,
                AlertPriority.LOW.value: 5
            }
            
            query = query.order_by(
                func.field(ProtectionAlert.alert_priority, *priority_order.keys()),
                desc(ProtectionAlert.created_at)
            )
            
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            # Load with related data
            alerts = await query.options(
                joinedload(ProtectionAlert.fingerprint),
                selectinload(ProtectionAlert.escalations)
            ).all()
            
            logger.info(f"Retrieved {len(alerts)} pending alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Pending alerts retrieval failed: {e}")
            raise ProtectionAlertRepositoryError(f"Pending alerts retrieval failed: {e}")
    
    async def update_alert_status(
        self,
        alert_id: UUID,
        new_status: AlertStatus,
        resolution_data: Optional[Dict[str, Any]] = None,
        analyst_id: Optional[str] = None
    ) -> ProtectionAlert:
        """
        Update alert status with comprehensive audit trail
        
        Args:
            alert_id: Alert identifier
            new_status: New alert status
            resolution_data: Resolution details and metadata
            analyst_id: ID of analyst handling the alert
            
        Returns:
            Updated ProtectionAlert record
        """
        try:
            alert = await self.db_session.get(ProtectionAlert, alert_id)
            
            if not alert:
                raise ProtectionAlertRepositoryError(f"Alert not found: {alert_id}")
            
            # Create status history entry
            old_status = alert.status
            status_change = {
                "from_status": old_status,
                "to_status": new_status.value,
                "changed_by": analyst_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resolution_data": resolution_data
            }
            
            # Update alert
            alert.status = new_status.value
            alert.updated_at = datetime.now(timezone.utc)
            
            if resolution_data:
                alert.resolution_data = await self.encryption_manager.encrypt_data(
                    json.dumps(resolution_data)
                )
            
            # Add to status history
            if "status_history" not in alert.metadata:
                alert.metadata["status_history"] = []
            
            alert.metadata["status_history"].append(status_change)
            
            # Update resolution timestamp for resolved statuses
            if new_status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED, AlertStatus.FALSE_POSITIVE]:
                alert.resolved_at = datetime.now(timezone.utc)
                
                # Calculate resolution time
                resolution_time = alert.resolved_at - alert.created_at
                alert.metadata["resolution_time_hours"] = resolution_time.total_seconds() / 3600
                
                # Update metrics
                self.alert_metrics["pending_alerts"] -= 1
                self.alert_metrics["resolved_alerts"] += 1
                
                if new_status == AlertStatus.FALSE_POSITIVE:
                    self.alert_metrics["false_positives"] += 1
            
            await self.db_session.commit()
            
            # Send status update notifications
            await self._send_status_update_notifications(alert, old_status, new_status.value)
            
            logger.info(f"Alert status updated: {alert_id} -> {new_status.value}")
            return alert
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Alert status update failed: {e}")
            raise ProtectionAlertRepositoryError(f"Alert status update failed: {e}")
    
    async def escalate_alert(
        self,
        alert_id: UUID,
        escalation_reason: str,
        escalated_by: Optional[str] = None,
        escalation_data: Optional[Dict[str, Any]] = None
    ) -> AlertEscalation:
        """
        Escalate alert with detailed reasoning and tracking
        
        Args:
            alert_id: Alert identifier
            escalation_reason: Reason for escalation
            escalated_by: ID of person/system escalating
            escalation_data: Additional escalation data
            
        Returns:
            Created AlertEscalation record
        """
        try:
            alert = await self.db_session.get(ProtectionAlert, alert_id)
            
            if not alert:
                raise ProtectionAlertRepositoryError(f"Alert not found: {alert_id}")
            
            # Create escalation record
            escalation = AlertEscalation(
                id=uuid4(),
                alert_id=alert_id,
                escalation_reason=escalation_reason,
                escalated_by=escalated_by or "system",
                escalation_level=await self._determine_escalation_level(alert),
                escalation_data=escalation_data or {},
                created_at=datetime.now(timezone.utc)
            )
            
            # Update alert status
            alert.status = AlertStatus.ESCALATED.value
            alert.alert_priority = await self._increase_priority(alert.alert_priority)
            alert.updated_at = datetime.now(timezone.utc)
            
            # Add escalation to alert metadata
            if "escalations" not in alert.metadata:
                alert.metadata["escalations"] = []
            
            alert.metadata["escalations"].append({
                "escalation_id": str(escalation.id),
                "reason": escalation_reason,
                "timestamp": escalation.created_at.isoformat(),
                "level": escalation.escalation_level
            })
            
            self.db_session.add(escalation)
            await self.db_session.commit()
            
            # Send escalation notifications
            await self._send_escalation_notifications(alert, escalation)
            
            # Update metrics
            self.alert_metrics["escalation_rate"] = await self._calculate_escalation_rate()
            
            logger.info(f"Alert escalated: {alert_id} -> Level {escalation.escalation_level}")
            return escalation
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Alert escalation failed: {e}")
            raise ProtectionAlertRepositoryError(f"Alert escalation failed: {e}")
    
    async def batch_process_alerts(
        self,
        alert_ids: List[UUID],
        action: str,
        action_data: Optional[Dict[str, Any]] = None,
        analyst_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple alerts in batch for efficiency
        
        Args:
            alert_ids: List of alert identifiers
            action: Action to perform (resolve, dismiss, escalate, etc.)
            action_data: Action-specific data
            analyst_id: ID of analyst performing action
            
        Returns:
            Batch processing results
        """
        try:
            results = {
                "processed": 0,
                "failed": 0,
                "errors": [],
                "processed_alerts": []
            }
            
            # Process alerts in batches
            for i in range(0, len(alert_ids), self.batch_size):
                batch_ids = alert_ids[i:i + self.batch_size]
                
                # Load batch of alerts
                alerts = await self.db_session.query(ProtectionAlert).filter(
                    ProtectionAlert.id.in_(batch_ids)
                ).all()
                
                for alert in alerts:
                    try:
                        if action == "resolve":
                            await self.update_alert_status(
                                alert.id, AlertStatus.RESOLVED, action_data, analyst_id
                            )
                        elif action == "dismiss":
                            await self.update_alert_status(
                                alert.id, AlertStatus.DISMISSED, action_data, analyst_id
                            )
                        elif action == "escalate":
                            await self.escalate_alert(
                                alert.id, 
                                action_data.get("reason", "batch_escalation"),
                                analyst_id,
                                action_data
                            )
                        else:
                            raise ValueError(f"Unknown action: {action}")
                        
                        results["processed"] += 1
                        results["processed_alerts"].append(str(alert.id))
                        
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "alert_id": str(alert.id),
                            "error": str(e)
                        })
                        logger.error(f"Batch processing failed for alert {alert.id}: {e}")
            
            logger.info(f"Batch processing completed: {results['processed']} processed, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise ProtectionAlertRepositoryError(f"Batch processing failed: {e}")
    
    async def get_alert_analytics(
        self,
        time_range_days: int = 30,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive alert analytics and insights
        
        Args:
            time_range_days: Number of days to analyze
            group_by: Grouping interval (hour, day, week, month)
            
        Returns:
            Comprehensive analytics data
        """
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=time_range_days)
            
            # Basic alert counts
            total_alerts = await self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.created_at >= start_date
            ).count()
            
            pending_alerts = await self.db_session.query(ProtectionAlert).filter(
                and_(
                    ProtectionAlert.created_at >= start_date,
                    ProtectionAlert.status == AlertStatus.PENDING.value
                )
            ).count()
            
            resolved_alerts = await self.db_session.query(ProtectionAlert).filter(
                and_(
                    ProtectionAlert.created_at >= start_date,
                    ProtectionAlert.status == AlertStatus.RESOLVED.value
                )
            ).count()
            
            # Priority distribution
            priority_distribution = await self.db_session.query(
                ProtectionAlert.alert_priority,
                func.count(ProtectionAlert.id)
            ).filter(
                ProtectionAlert.created_at >= start_date
            ).group_by(ProtectionAlert.alert_priority).all()
            
            # Category distribution
            category_distribution = await self.db_session.query(
                ProtectionAlert.alert_category,
                func.count(ProtectionAlert.id)
            ).filter(
                ProtectionAlert.created_at >= start_date
            ).group_by(ProtectionAlert.alert_category).all()
            
            # Platform distribution
            platform_distribution = await self.db_session.query(
                ProtectionAlert.platform,
                func.count(ProtectionAlert.id)
            ).filter(
                ProtectionAlert.created_at >= start_date
            ).group_by(ProtectionAlert.platform).all()
            
            # Average resolution time
            avg_resolution_query = await self.db_session.query(
                func.avg(
                    func.extract('epoch', ProtectionAlert.resolved_at - ProtectionAlert.created_at) / 3600
                )
            ).filter(
                and_(
                    ProtectionAlert.created_at >= start_date,
                    ProtectionAlert.resolved_at.isnot(None)
                )
            ).scalar()
            
            avg_resolution_time = float(avg_resolution_query) if avg_resolution_query else 0.0
            
            # Time series data
            time_series = await self._generate_time_series_data(start_date, group_by)
            
            analytics = {
                "time_range_days": time_range_days,
                "total_alerts": total_alerts,
                "pending_alerts": pending_alerts,
                "resolved_alerts": resolved_alerts,
                "resolution_rate": (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0,
                "avg_resolution_time_hours": avg_resolution_time,
                "priority_distribution": dict(priority_distribution),
                "category_distribution": dict(category_distribution),
                "platform_distribution": dict(platform_distribution),
                "time_series": time_series,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("Alert analytics generated successfully")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            raise ProtectionAlertRepositoryError(f"Analytics generation failed: {e}")
    
    async def find_alert_patterns(
        self,
        lookback_days: int = 7,
        min_pattern_size: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify patterns and trends in alert data for proactive protection
        
        Args:
            lookback_days: Days to analyze for patterns
            min_pattern_size: Minimum number of alerts to constitute a pattern
            
        Returns:
            List of identified patterns with details
        """
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            
            # Get recent alerts
            alerts = await self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.created_at >= start_date
            ).options(
                joinedload(ProtectionAlert.fingerprint)
            ).all()
            
            patterns = []
            
            # Pattern 1: Same URL/Platform combinations
            url_patterns = defaultdict(list)
            for alert in alerts:
                key = (alert.detected_url, alert.platform)
                url_patterns[key].append(alert)
            
            for (url, platform), alert_list in url_patterns.items():
                if len(alert_list) >= min_pattern_size:
                    patterns.append({
                        "type": "repeated_url_platform",
                        "description": f"Multiple alerts from {platform} URL: {url}",
                        "alert_count": len(alert_list),
                        "alerts": [str(a.id) for a in alert_list],
                        "first_seen": min(a.created_at for a in alert_list).isoformat(),
                        "last_seen": max(a.created_at for a in alert_list).isoformat(),
                        "severity": "high" if len(alert_list) > 5 else "medium"
                    })
            
            # Pattern 2: Same content across multiple platforms
            content_patterns = defaultdict(list)
            for alert in alerts:
                if alert.fingerprint:
                    content_patterns[alert.fingerprint_id].append(alert)
            
            for fingerprint_id, alert_list in content_patterns.items():
                platforms = set(a.platform for a in alert_list)
                if len(platforms) >= min_pattern_size:
                    patterns.append({
                        "type": "cross_platform_distribution",
                        "description": f"Same content detected across {len(platforms)} platforms",
                        "platform_count": len(platforms),
                        "platforms": list(platforms),
                        "alert_count": len(alert_list),
                        "alerts": [str(a.id) for a in alert_list],
                        "fingerprint_id": str(fingerprint_id),
                        "severity": "critical" if len(platforms) > 5 else "high"
                    })
            
            # Pattern 3: High similarity score clusters
            high_similarity_alerts = [a for a in alerts if a.similarity_score > 0.9]
            if len(high_similarity_alerts) >= min_pattern_size:
                patterns.append({
                    "type": "high_similarity_cluster",
                    "description": f"Cluster of {len(high_similarity_alerts)} high-similarity alerts",
                    "alert_count": len(high_similarity_alerts),
                    "avg_similarity": sum(a.similarity_score for a in high_similarity_alerts) / len(high_similarity_alerts),
                    "alerts": [str(a.id) for a in high_similarity_alerts],
                    "severity": "high"
                })
            
            logger.info(f"Found {len(patterns)} alert patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            raise ProtectionAlertRepositoryError(f"Pattern detection failed: {e}")
    
    # Private helper methods
    
    async def _validate_detection_data(self, detection_data: Dict[str, Any]) -> None:
        """Validate detection data structure"""
        required_fields = ["detected_url", "platform", "similarity_score"]
        
        for field in required_fields:
            if field not in detection_data:
                raise ProtectionAlertRepositoryError(f"Missing required field: {field}")
        
        if not (0.0 <= detection_data["similarity_score"] <= 1.0):
            raise ProtectionAlertRepositoryError("Similarity score must be between 0.0 and 1.0")
    
    async def _categorize_alert(self, detection_data: Dict[str, Any]) -> AlertCategory:
        """Determine alert category based on detection data"""
        detection_method = detection_data.get("detection_method", "").lower()
        platform = detection_data.get("platform", "").lower()
        
        # AI-based categorization logic
        if "deepfake" in detection_method or "manipulation" in detection_method:
            return AlertCategory.DEEPFAKE_DETECTION
        elif "trademark" in detection_method or "logo" in detection_method:
            return AlertCategory.TRADEMARK_VIOLATION
        elif "commercial" in detection_data.get("context", "").lower():
            return AlertCategory.UNAUTHORIZED_DISTRIBUTION
        elif detection_data.get("similarity_score", 0) > 0.95:
            return AlertCategory.COPYRIGHT_INFRINGEMENT
        else:
            return AlertCategory.COPYRIGHT_INFRINGEMENT  # Default
    
    async def _find_correlated_alerts(
        self,
        fingerprint_id: UUID,
        detection_data: Dict[str, Any]
    ) -> List[ProtectionAlert]:
        """Find alerts correlated with current detection"""
        correlation_window = datetime.now(timezone.utc) - timedelta(hours=self.correlation_window_hours)
        
        # Find alerts with same fingerprint
        same_content = await self.db_session.query(ProtectionAlert).filter(
            and_(
                ProtectionAlert.fingerprint_id == fingerprint_id,
                ProtectionAlert.created_at >= correlation_window,
                ProtectionAlert.status != AlertStatus.FALSE_POSITIVE.value
            )
        ).all()
        
        # Find alerts from same URL or platform
        same_source = await self.db_session.query(ProtectionAlert).filter(
            and_(
                or_(
                    ProtectionAlert.detected_url == detection_data.get("detected_url"),
                    ProtectionAlert.platform == detection_data.get("platform")
                ),
                ProtectionAlert.created_at >= correlation_window,
                ProtectionAlert.status != AlertStatus.FALSE_POSITIVE.value
            )
        ).all()
        
        # Combine and deduplicate
        correlations = list(set(same_content + same_source))
        return correlations
    
    async def _adjust_priority_for_correlations(
        self,
        base_priority: AlertPriority,
        correlations: List[ProtectionAlert]
    ) -> AlertPriority:
        """Adjust alert priority based on correlations"""
        if len(correlations) > 5:
            return AlertPriority.CRITICAL
        elif len(correlations) > 2:
            return AlertPriority.HIGH
        else:
            return base_priority
    
    async def _should_auto_escalate(self, alert: ProtectionAlert) -> bool:
        """Determine if alert should be automatically escalated"""
        if alert.alert_priority in [AlertPriority.CRITICAL.value, AlertPriority.EMERGENCY.value]:
            return True
        
        if alert.similarity_score >= self.escalation_thresholds["high_similarity"]:
            return True
        
        if len(alert.correlation_ids) >= self.escalation_thresholds["multiple_platforms"]:
            return True
        
        return False
    
    async def _send_alert_notifications(self, alert: ProtectionAlert) -> None:
        """Send notifications for new alert"""
        try:
            notification_data = {
                "alert_id": str(alert.id),
                "priority": alert.alert_priority,
                "category": alert.alert_category,
                "platform": alert.platform,
                "similarity_score": alert.similarity_score
            }
            
            await self.notification_manager.send_alert_notification(notification_data)
            
        except Exception as e:
            logger.warning(f"Alert notification failed: {e}")
    
    async def _send_status_update_notifications(
        self,
        alert: ProtectionAlert,
        old_status: str,
        new_status: str
    ) -> None:
        """Send notifications for status updates"""
        try:
            notification_data = {
                "alert_id": str(alert.id),
                "old_status": old_status,
                "new_status": new_status,
                "priority": alert.alert_priority
            }
            
            await self.notification_manager.send_status_update_notification(notification_data)
            
        except Exception as e:
            logger.warning(f"Status update notification failed: {e}")
    
    async def _send_escalation_notifications(
        self,
        alert: ProtectionAlert,
        escalation: AlertEscalation
    ) -> None:
        """Send notifications for alert escalation"""
        try:
            notification_data = {
                "alert_id": str(alert.id),
                "escalation_id": str(escalation.id),
                "escalation_reason": escalation.escalation_reason,
                "escalation_level": escalation.escalation_level
            }
            
            await self.notification_manager.send_escalation_notification(notification_data)
            
        except Exception as e:
            logger.warning(f"Escalation notification failed: {e}")
    
    async def _determine_escalation_level(self, alert: ProtectionAlert) -> int:
        """Determine escalation level based on alert properties"""
        current_escalations = len(alert.metadata.get("escalations", []))
        return current_escalations + 1
    
    async def _increase_priority(self, current_priority: str) -> str:
        """Increase alert priority level"""
        priority_levels = [
            AlertPriority.LOW.value,
            AlertPriority.MEDIUM.value,
            AlertPriority.HIGH.value,
            AlertPriority.CRITICAL.value,
            AlertPriority.EMERGENCY.value
        ]
        
        try:
            current_index = priority_levels.index(current_priority)
            if current_index < len(priority_levels) - 1:
                return priority_levels[current_index + 1]
        except ValueError:
            pass
        
        return current_priority
    
    async def _calculate_escalation_rate(self) -> float:
        """Calculate current escalation rate"""
        try:
            total_alerts = await self.db_session.query(ProtectionAlert).count()
            escalated_alerts = await self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.status == AlertStatus.ESCALATED.value
            ).count()
            
            return (escalated_alerts / total_alerts * 100) if total_alerts > 0 else 0.0
            
        except Exception:
            return 0.0
    
    async def _generate_time_series_data(
        self,
        start_date: datetime,
        group_by: str
    ) -> List[Dict[str, Any]]:
        """Generate time series data for analytics"""
        try:
            time_format = {
                "hour": "%Y-%m-%d %H:00:00",
                "day": "%Y-%m-%d",
                "week": "%Y-%W",
                "month": "%Y-%m"
            }.get(group_by, "%Y-%m-%d")
            
            query = await self.db_session.query(
                func.date_trunc(group_by, ProtectionAlert.created_at).label('time_period'),
                func.count(ProtectionAlert.id).label('alert_count'),
                func.avg(ProtectionAlert.similarity_score).label('avg_similarity')
            ).filter(
                ProtectionAlert.created_at >= start_date
            ).group_by('time_period').order_by('time_period').all()
            
            return [
                {
                    "time_period": row.time_period.isoformat(),
                    "alert_count": row.alert_count,
                    "avg_similarity_score": float(row.avg_similarity) if row.avg_similarity else 0.0
                }
                for row in query
            ]
            
        except Exception as e:
            logger.warning(f"Time series generation failed: {e}")
            return []
