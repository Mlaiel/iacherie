"""Protection Alert Repository Module

Enterprise-grade repository for content protection alert management
with advanced threat detection, automated response, and evidence collection.

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

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import uuid
from ..models.protection_alerts import (
    ProtectionAlert,
    AlertType,
    AlertSeverity,
    AlertStatus,
    DetectionMethod,
    AutomatedAction,
    EvidenceType,
    ThreatLevel
)
from ..models.content_fingerprints import ContentFingerprint
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class ProtectionAlertRepository(BaseRepository[ProtectionAlert]):
    """
    Repository for protection alert operations with advanced threat assessment,
    automated response coordination, and comprehensive evidence management.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize protection alert repository"""
        super().__init__(db_session, ProtectionAlert)
        
    def create_alert(self,
                    fingerprint_id: int,
                    detected_url: str,
                    platform: str,
                    similarity_score: float,
                    detection_method: DetectionMethod,
                    alert_type: AlertType = AlertType.COPYRIGHT_INFRINGEMENT,
                    threat_level: ThreatLevel = ThreatLevel.MEDIUM,
                    evidence_data: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> ProtectionAlert:
        """
        Create protection alert with automatic severity assessment
        
        Args:
            fingerprint_id: Associated fingerprint ID
            detected_url: URL where infringement was detected
            platform: Platform name where content was found
            similarity_score: Similarity score of the match
            detection_method: Method used for detection
            alert_type: Type of alert
            threat_level: Assessed threat level
            evidence_data: Evidence collection data
            metadata: Additional metadata
            
        Returns:
            Created ProtectionAlert instance
        """
        try:
            # Auto-assess severity based on similarity score and threat level
            severity = self._assess_alert_severity(similarity_score, threat_level, platform)
            
            # Generate alert ID
            alert_id = str(uuid.uuid4())
            
            alert_data = {
                'fingerprint_id': fingerprint_id,
                'detected_url': detected_url,
                'platform': platform,
                'similarity_score': similarity_score,
                'detection_method': detection_method,
                'alert_type': alert_type,
                'severity': severity,
                'threat_level': threat_level,
                'status': AlertStatus.PENDING,
                'evidence_data': evidence_data or {},
                'metadata': metadata or {},
                'alert_id': alert_id,
                'detected_at': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            alert = self.create(**alert_data)
            
            # Trigger automated actions if necessary
            if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                self._trigger_automated_response(alert)
            
            self.logger.info(
                f"Created {severity.value} severity alert for {platform}: {detected_url}"
            )
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Failed to create protection alert: {str(e)}")
            raise RepositoryException(f"Alert creation failed: {str(e)}")
            
    def _assess_alert_severity(self,
                              similarity_score: float,
                              threat_level: ThreatLevel,
                              platform: str) -> AlertSeverity:
        """
        Automatically assess alert severity based on multiple factors
        
        Args:
            similarity_score: Content similarity score
            threat_level: Assessed threat level
            platform: Platform where content was detected
            
        Returns:
            Assessed AlertSeverity
        """
        try:
            # High-impact platforms get higher severity
            high_impact_platforms = ['youtube', 'instagram', 'tiktok', 'spotify']
            platform_multiplier = 1.2 if platform.lower() in high_impact_platforms else 1.0
            
            # Calculate severity score
            severity_score = similarity_score * platform_multiplier
            
            # Adjust based on threat level
            threat_multipliers = {
                ThreatLevel.LOW: 0.8,
                ThreatLevel.MEDIUM: 1.0,
                ThreatLevel.HIGH: 1.3,
                ThreatLevel.CRITICAL: 1.5
            }
            
            severity_score *= threat_multipliers.get(threat_level, 1.0)
            
            # Determine severity
            if severity_score >= 0.95:
                return AlertSeverity.CRITICAL
            elif severity_score >= 0.85:
                return AlertSeverity.HIGH
            elif severity_score >= 0.7:
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.LOW
                
        except Exception as e:
            self.logger.error(f"Failed to assess alert severity: {str(e)}")
            return AlertSeverity.MEDIUM
            
    def _trigger_automated_response(self, alert: ProtectionAlert) -> None:
        """
        Trigger automated response actions for high-severity alerts
        
        Args:
            alert: ProtectionAlert instance
        """
        try:
            automated_actions = []
            
            # Critical alerts get immediate DMCA takedown
            if alert.severity == AlertSeverity.CRITICAL:
                automated_actions.extend([
                    AutomatedAction.DMCA_TAKEDOWN,
                    AutomatedAction.EVIDENCE_COLLECTION,
                    AutomatedAction.USER_NOTIFICATION
                ])
            
            # High severity alerts get evidence collection and notification
            elif alert.severity == AlertSeverity.HIGH:
                automated_actions.extend([
                    AutomatedAction.EVIDENCE_COLLECTION,
                    AutomatedAction.USER_NOTIFICATION,
                    AutomatedAction.PLATFORM_REPORT
                ])
            
            # Update alert with automated actions
            if automated_actions:
                metadata = alert.metadata or {}
                metadata['automated_actions'] = [action.value for action in automated_actions]
                metadata['auto_response_triggered'] = datetime.utcnow().isoformat()
                
                self.update(alert.id, 
                          automated_actions=automated_actions,
                          metadata=metadata)
                
                self.logger.info(
                    f"Triggered automated actions for alert {alert.alert_id}: {automated_actions}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to trigger automated response: {str(e)}")
            
    def get_by_fingerprint_id(self,
                             fingerprint_id: int,
                             status: Optional[AlertStatus] = None,
                             limit: Optional[int] = None,
                             offset: Optional[int] = None) -> List[ProtectionAlert]:
        """
        Get alerts by fingerprint ID with optional filtering
        
        Args:
            fingerprint_id: Fingerprint ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ProtectionAlert instances
        """
        try:
            query = self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.fingerprint_id == fingerprint_id
            )
            
            if status:
                query = query.filter(ProtectionAlert.status == status)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            query = query.order_by(ProtectionAlert.detected_at.desc())
            
            alerts = query.all()
            
            self.logger.debug(
                f"Retrieved {len(alerts)} alerts for fingerprint {fingerprint_id}"
            )
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts by fingerprint: {str(e)}")
            return []
            
    def get_by_user_id(self,
                      user_id: int,
                      severity: Optional[AlertSeverity] = None,
                      status: Optional[AlertStatus] = None,
                      days_back: Optional[int] = 30,
                      limit: Optional[int] = None,
                      offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get alerts for user with fingerprint details
        
        Args:
            user_id: User ID to filter by
            severity: Optional severity filter
            status: Optional status filter
            days_back: Number of days to look back
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of alert dictionaries with fingerprint details
        """
        try:
            # Join with ContentFingerprint to get user's alerts
            query = self.db_session.query(
                ProtectionAlert, ContentFingerprint
            ).join(
                ContentFingerprint, 
                ProtectionAlert.fingerprint_id == ContentFingerprint.id
            ).filter(
                ContentFingerprint.user_id == user_id
            )
            
            # Apply filters
            if severity:
                query = query.filter(ProtectionAlert.severity == severity)
                
            if status:
                query = query.filter(ProtectionAlert.status == status)
                
            if days_back:
                cutoff_date = datetime.utcnow() - timedelta(days=days_back)
                query = query.filter(ProtectionAlert.detected_at >= cutoff_date)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            query = query.order_by(ProtectionAlert.detected_at.desc())
            
            results = query.all()
            
            # Format results with fingerprint details
            alert_data = []
            for alert, fingerprint in results:
                alert_dict = {
                    'alert': alert,
                    'fingerprint': fingerprint,
                    'content_details': {
                        'filename': fingerprint.original_filename,
                        'content_type': fingerprint.content_type.value,
                        'upload_date': fingerprint.created_at.isoformat()
                    }
                }
                alert_data.append(alert_dict)
            
            self.logger.debug(
                f"Retrieved {len(alert_data)} alerts for user {user_id}"
            )
            
            return alert_data
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts by user: {str(e)}")
            return []
            
    def get_pending_alerts(self,
                          severity: Optional[AlertSeverity] = None,
                          platform: Optional[str] = None,
                          limit: Optional[int] = None) -> List[ProtectionAlert]:
        """
        Get pending alerts for processing
        
        Args:
            severity: Optional severity filter
            platform: Optional platform filter
            limit: Maximum number of results
            
        Returns:
            List of pending ProtectionAlert instances
        """
        try:
            query = self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.status == AlertStatus.PENDING
            )
            
            if severity:
                query = query.filter(ProtectionAlert.severity == severity)
                
            if platform:
                query = query.filter(ProtectionAlert.platform.ilike(f"%{platform}%"))
            
            # Order by severity (critical first) then by detection time
            query = query.order_by(
                desc(ProtectionAlert.severity),
                asc(ProtectionAlert.detected_at)
            )
            
            if limit:
                query = query.limit(limit)
                
            alerts = query.all()
            
            self.logger.debug(f"Retrieved {len(alerts)} pending alerts")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get pending alerts: {str(e)}")
            return []
            
    def update_alert_status(self,
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
    def get_alert_statistics(self,
                           user_id: Optional[int] = None,
                           days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive alert statistics
        
        Args:
            user_id: Optional user ID to filter statistics
            days_back: Number of days to include in statistics
            
        Returns:
            Dictionary containing alert statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Base query
            if user_id:
                base_query = self.db_session.query(ProtectionAlert).join(
                    ContentFingerprint,
                    ProtectionAlert.fingerprint_id == ContentFingerprint.id
                ).filter(ContentFingerprint.user_id == user_id)
            else:
                base_query = self.db_session.query(ProtectionAlert)
            
            # Recent alerts
            recent_query = base_query.filter(ProtectionAlert.detected_at >= cutoff_date)
            
            # Count statistics
            total_alerts = base_query.count()
            recent_alerts = recent_query.count()
            
            # Status distribution
            status_stats = {}
            for status in AlertStatus:
                count = recent_query.filter(ProtectionAlert.status == status).count()
                status_stats[status.value] = count
            
            # Severity distribution
            severity_stats = {}
            for severity in AlertSeverity:
                count = recent_query.filter(ProtectionAlert.severity == severity).count()
                severity_stats[severity.value] = count
            
            # Platform distribution
            platform_stats = {}
            platform_results = recent_query.with_entities(
                ProtectionAlert.platform,
                func.count(ProtectionAlert.id)
            ).group_by(ProtectionAlert.platform).all()
            
            for platform, count in platform_results:
                platform_stats[platform] = count
            
            # Average similarity score
            avg_similarity = recent_query.with_entities(
                func.avg(ProtectionAlert.similarity_score)
            ).scalar() or 0.0
            
            # Resolution rate
            resolved_count = recent_query.filter(
                ProtectionAlert.status.in_([AlertStatus.RESOLVED, AlertStatus.DISMISSED])
            ).count()
            resolution_rate = (resolved_count / recent_alerts * 100) if recent_alerts > 0 else 0.0
            
            statistics = {
                'total_alerts': total_alerts,
                'recent_alerts': recent_alerts,
                'status_distribution': status_stats,
                'severity_distribution': severity_stats,
                'platform_distribution': platform_stats,
                'average_similarity_score': round(avg_similarity, 3),
                'resolution_rate_percent': round(resolution_rate, 2),
                'days_included': days_back,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get alert statistics: {str(e)}")
            return {'error': str(e)}
            
    def bulk_update_alerts(self,
                          alert_ids: List[int],
                          updates: Dict[str, Any]) -> int:
        """
        Bulk update multiple alerts
        
        Args:
            alert_ids: List of alert IDs to update
            updates: Dictionary of updates to apply
            
        Returns:
            Number of updated alerts
        """
        try:
            # Add timestamp
            updates['updated_at'] = datetime.utcnow()
            
            updated_count = self.db_session.query(ProtectionAlert).filter(
                ProtectionAlert.id.in_(alert_ids)
            ).update(updates, synchronize_session=False)
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(f"Bulk updated {updated_count} alerts")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Failed to bulk update alerts: {str(e)}")
            raise RepositoryException(f"Bulk alert update failed: {str(e)}")
            
    def get_threat_assessment_report(self, user_id: int, days_back: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive threat assessment report for user
        
        Args:
            user_id: User ID to generate report for
            days_back: Number of days to include in assessment
            
        Returns:
            Threat assessment report
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get recent alerts for user
            user_alerts = self.get_by_user_id(
                user_id=user_id,
                days_back=days_back
            )
            
            if not user_alerts:
                return {
                    'user_id': user_id,
                    'threat_level': 'LOW',
                    'total_threats': 0,
                    'assessment_period_days': days_back,
                    'recommendations': ['Continue regular monitoring'],
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Analyze threat patterns
            threat_scores = []
            high_risk_platforms = []
            
            for alert_data in user_alerts:
                alert = alert_data['alert']
                
                # Calculate threat score
                severity_weights = {
                    AlertSeverity.LOW: 1,
                    AlertSeverity.MEDIUM: 2,
                    AlertSeverity.HIGH: 4,
                    AlertSeverity.CRITICAL: 8
                }
                
                threat_score = (
                    severity_weights.get(alert.severity, 2) * 
                    alert.similarity_score
                )
                threat_scores.append(threat_score)
                
                # Track high-risk platforms
                if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                    high_risk_platforms.append(alert.platform)
            
            # Calculate overall threat level
            avg_threat_score = sum(threat_scores) / len(threat_scores)
            
            if avg_threat_score >= 6:
                overall_threat_level = 'CRITICAL'
            elif avg_threat_score >= 4:
                overall_threat_level = 'HIGH'
            elif avg_threat_score >= 2:
                overall_threat_level = 'MEDIUM'
            else:
                overall_threat_level = 'LOW'
            
            # Generate recommendations
            recommendations = self._generate_threat_recommendations(
                overall_threat_level,
                high_risk_platforms,
                len(user_alerts)
            )
            
            report = {
                'user_id': user_id,
                'threat_level': overall_threat_level,
                'total_threats': len(user_alerts),
                'average_threat_score': round(avg_threat_score, 2),
                'high_risk_platforms': list(set(high_risk_platforms)),
                'assessment_period_days': days_back,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate threat assessment: {str(e)}")
            return {'error': str(e), 'user_id': user_id}
            
    def _generate_threat_recommendations(self,
                                       threat_level: str,
                                       high_risk_platforms: List[str],
                                       threat_count: int) -> List[str]:
        """
        Generate personalized threat mitigation recommendations
        
        Args:
            threat_level: Overall threat assessment level
            high_risk_platforms: List of high-risk platforms
            threat_count: Total number of threats detected
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if threat_level == 'CRITICAL':
            recommendations.extend([
                'Immediate action required: Review all critical alerts',
                'Consider enabling automated DMCA takedown',
                'Increase monitoring frequency to daily',
                'Contact legal team for high-value content protection'
            ])
        elif threat_level == 'HIGH':
            recommendations.extend([
                'Review and respond to high-severity alerts within 24 hours',
                'Enable automated evidence collection',
                'Consider watermarking future content'
            ])
        elif threat_level == 'MEDIUM':
            recommendations.extend([
                'Monitor trending platforms more closely',
                'Review protection policies',
                'Consider expanding fingerprint coverage'
            ])
        else:
            recommendations.extend([
                'Continue regular monitoring',
                'Maintain current protection settings'
            ])
        
        # Platform-specific recommendations
        if 'youtube' in high_risk_platforms:
            recommendations.append('Enable YouTube Content ID protection')
        if 'instagram' in high_risk_platforms:
            recommendations.append('Increase Instagram monitoring frequency')
        if 'tiktok' in high_risk_platforms:
            recommendations.append('Consider TikTok creator protection program')
        
        return recommendations

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
