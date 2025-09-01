"""Authentication Logging Database Components

Enterprise authentication audit logging with comprehensive security monitoring,
anomaly detection, and compliance reporting for content creator platforms.

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

import uuid
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()
logger = logging.getLogger(__name__)


class AuthEventType(Enum):
    """
Authentication event types"""

    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_SETUP = "mfa_setup"
    MFA_VERIFICATION = "mfa_verification"
    TOKEN_GENERATED = "token_generated"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    DEVICE_REGISTERED = "device_registered"
    DEVICE_TRUSTED = "device_trusted"
    DEVICE_REVOKED = "device_revoked"
    BIOMETRIC_ENROLLED = "biometric_enrolled"
    BIOMETRIC_VERIFIED = "biometric_verified"
    OAUTH_AUTHORIZED = "oauth_authorized"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_ALERT = "security_alert"


class AuthResult(Enum):
    """Authentication result types"""

    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPICIOUS = "suspicious"
    ERROR = "error"


class RiskLevel(Enum):
    """Risk level classifications"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuthContext:
    """Authentication context structure"""
    user_agent: str
    ip_address: str
    device_fingerprint: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    api_version: Optional[str] = None
    client_version: Optional[str] = None
    platform: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    headers: Dict[str, str] = field(default_factory=dict)


class AuthenticationLog(Base):
    """
Comprehensive authentication logging"""
    __tablename__ = "authentication_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Can be null for failed attempts
    username = Column(String(255), nullable=True, index=True)  # For failed login tracking
    event_type = Column(String(100), nullable=False, index=True)
    auth_result = Column(String(50), nullable=False, index=True)
    auth_method = Column(String(100), nullable=True)  # password, mfa, biometric, oauth
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    location_info = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)
    auth_details = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_level = Column(String(20), nullable=True, index=True)
    anomaly_indicators = Column(JSON, nullable=True)
    failure_reason = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_auth_log_user_event', 'user_id', 'event_type'),
        Index('idx_auth_log_ip_created', 'ip_address', 'created_at'),
        Index('idx_auth_log_risk_level', 'risk_level', 'created_at'),
        Index('idx_auth_log_result_created', 'auth_result', 'created_at'),
    )


class SecurityAudit(Base):
    """Security audit events"""
    __tablename__ = "security_audit"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    audit_category = Column(String(100), nullable=False, index=True)  # authentication, authorization, data_access
    audit_action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)  # user, device, token, content
    resource_id = Column(String(255), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    actor_id = Column(UUID(as_uuid=True), nullable=True)  # Who performed the action
    actor_type = Column(String(50), nullable=True)  # user, system, admin
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_context = Column(JSON, nullable=True)
    compliance_tags = Column(ARRAY(String), nullable=True)  # GDPR, SOC2, etc.
    severity_level = Column(String(20), nullable=False, default="info", index=True)
    audit_result = Column(String(50), nullable=False)
    audit_message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_category_action', 'audit_category', 'audit_action'),
        Index('idx_audit_user_created', 'user_id', 'created_at'),
        Index('idx_audit_severity_created', 'severity_level', 'created_at'),
        Index('idx_audit_compliance', 'compliance_tags'),
    )


class ActivityTracker(Base):
    """User activity tracking"""
    __tablename__ = "user_activity_tracker"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False, index=True)
    activity_description = Column(String(500), nullable=False)
    resource_accessed = Column(String(255), nullable=True)
    action_performed = Column(String(100), nullable=False)
    activity_result = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    device_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    data_accessed = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_user_type', 'user_id', 'activity_type'),
        Index('idx_activity_created_result', 'created_at', 'activity_result'),
        Index('idx_activity_session', 'session_id', 'created_at'),
    )


class AnomalyDetection(Base):
    """Authentication anomaly detection"""
    __tablename__ = "authentication_anomalies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    anomaly_type = Column(String(100), nullable=False, index=True)
    anomaly_score = Column(Integer, nullable=False)  # 0-100
    detection_algorithm = Column(String(100), nullable=False)
    baseline_data = Column(JSON, nullable=True)
    observed_data = Column(JSON, nullable=False)
    deviation_metrics = Column(JSON, nullable=False)
    risk_assessment = Column(JSON, nullable=False)
    auto_action_taken = Column(String(100), nullable=True)
    manual_review_required = Column(Boolean, nullable=False, default=False)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_anomaly_user_type', 'user_id', 'anomaly_type'),
        Index('idx_anomaly_score_created', 'anomaly_score', 'created_at'),
        Index('idx_anomaly_resolved', 'is_resolved', 'manual_review_required'),
    )


class ComplianceLog(Base):
    """Compliance and regulatory logging"""
    __tablename__ = "compliance_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    compliance_framework = Column(String(50), nullable=False, index=True)  # GDPR, SOC2, HIPAA
    regulation_requirement = Column(String(100), nullable=False)
    data_subject_type = Column(String(50), nullable=True)  # user, content_creator, admin
    personal_data_categories = Column(ARRAY(String), nullable=True)
    processing_purpose = Column(String(255), nullable=False)
    legal_basis = Column(String(100), nullable=True)
    data_retention_period = Column(Integer, nullable=True)  # Days
    third_party_sharing = Column(Boolean, nullable=False, default=False)
    consent_status = Column(String(50), nullable=True)
    data_location = Column(String(100), nullable=True)
    encryption_status = Column(String(50), nullable=False)
    access_controls = Column(JSON, nullable=True)
    audit_trail_reference = Column(UUID(as_uuid=True), nullable=True)
    compliance_status = Column(String(50), nullable=False, default="compliant")
    violation_details = Column(Text, nullable=True)
    remediation_actions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_framework_status', 'compliance_framework', 'compliance_status'),
        Index('idx_compliance_user_created', 'user_id', 'created_at'),
        Index('idx_compliance_retention', 'data_retention_period', 'created_at'),
    )


class AuthenticationLogger:
    """Enterprise authentication logging manager"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def log_auth_event(
        self,
        event_type: AuthEventType,
        auth_result: AuthResult,
        auth_context: AuthContext,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        auth_method: Optional[str] = None,
        auth_details: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> str:
        """
Log authentication event"""
        try:
            # Calculate risk score
            risk_score = self._calculate_risk_score(auth_context, event_type, auth_result)
            risk_level = self._determine_risk_level(risk_score)
            
            # Detect anomalies
            anomaly_indicators = await self._detect_anomalies(user_id, auth_context, event_type)
            
            auth_log = AuthenticationLog(
                user_id=uuid.UUID(user_id) if user_id else None,
                username=username,
                event_type=event_type.value,
                auth_result=auth_result.value,
                auth_method=auth_method,
                ip_address=auth_context.ip_address,
                user_agent=auth_context.user_agent,
                device_fingerprint=auth_context.device_fingerprint,
                session_id=auth_context.session_id,
                request_id=auth_context.request_id,
                location_info=auth_context.location,
                request_headers=auth_context.headers,
                auth_details=auth_details,
                risk_score=risk_score,
                risk_level=risk_level.value if risk_level else None,
                anomaly_indicators=anomaly_indicators,
                failure_reason=failure_reason,
                duration_ms=duration_ms
            )
            
            self.db.add(auth_log)
            await self.db.commit()
            
            # Trigger alerts for high-risk events
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._trigger_security_alert(auth_log)
            
            logger.info(f"Logged {event_type.value} event for user {user_id or username}")
            return str(auth_log.id)
            
        except Exception as e:
            logger.error(f"Failed to log auth event: {e}")
            await self.db.rollback()
            raise
    
    def _calculate_risk_score(
        self,
        auth_context: AuthContext,
        event_type: AuthEventType,
        auth_result: AuthResult
    ) -> int:
        """Calculate risk score for authentication event"""
        risk_score = 0
        
        # Base risk by event type
        event_risk = {
            AuthEventType.LOGIN_FAILURE: 30,
            AuthEventType.LOGIN_SUCCESS: 10,
            AuthEventType.ACCOUNT_LOCKED: 80,
            AuthEventType.SUSPICIOUS_ACTIVITY: 90,
            AuthEventType.PASSWORD_RESET: 40,
            AuthEventType.MFA_VERIFICATION: 20,
            AuthEventType.DEVICE_REGISTERED: 50,
        }
        risk_score += event_risk.get(event_type, 20)
        
        # Result-based risk
        if auth_result == AuthResult.FAILURE:
            risk_score += 20
        elif auth_result == AuthResult.BLOCKED:
            risk_score += 40
        elif auth_result == AuthResult.SUSPICIOUS:
            risk_score += 60
        
        # IP-based risk (simplified)
        if auth_context.ip_address.startswith("192.168.") or auth_context.ip_address.startswith("10."):
            risk_score -= 10  # Internal network
        else:
            risk_score += 10  # External network
        
        # Device fingerprint risk
        if not auth_context.device_fingerprint:
            risk_score += 20
        
        return min(100, max(0, risk_score))
    
    def _determine_risk_level(self, risk_score: int) -> Optional[RiskLevel]:
        """Determine risk level from score"""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _detect_anomalies(
        self,
        user_id: Optional[str],
        auth_context: AuthContext,
        event_type: AuthEventType
    ) -> Dict[str, Any]:
        """
Detect authentication anomalies"""
        anomalies = {}
        
        if not user_id:
            return anomalies
        
        try:
            # Check for unusual login times
            recent_logins = self.db.query(AuthenticationLog).filter(
                AuthenticationLog.user_id == uuid.UUID(user_id),
                AuthenticationLog.event_type == AuthEventType.LOGIN_SUCCESS.value,
                AuthenticationLog.created_at > datetime.now(timezone.utc) - timedelta(days=30)
            ).all()
            
            if recent_logins:
                # Analyze login time patterns
                current_hour = datetime.now(timezone.utc).hour
                usual_hours = [log.created_at.hour for log in recent_logins]
                
                if usual_hours and abs(current_hour - sum(usual_hours) / len(usual_hours)) > 6:
                    anomalies["unusual_time"] = {
                        "current_hour": current_hour,
                        "usual_average": sum(usual_hours) / len(usual_hours)
                    }
            
            # Check for new IP addresses
            recent_ips = set(log.ip_address for log in recent_logins)
            if auth_context.ip_address not in recent_ips:
                anomalies["new_ip_address"] = {
                    "new_ip": auth_context.ip_address,
                    "known_ips": list(recent_ips)[:5]  # Limit for privacy
                }
            
            # Check for rapid authentication attempts
            recent_attempts = self.db.query(AuthenticationLog).filter(
                AuthenticationLog.user_id == uuid.UUID(user_id),
                AuthenticationLog.created_at > datetime.now(timezone.utc) - timedelta(minutes=5)
            ).count()
            
            if recent_attempts > 5:
                anomalies["rapid_attempts"] = {
                    "attempts_count": recent_attempts,
                    "time_window": "5_minutes"
                }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
        
        return anomalies
    
    async def _trigger_security_alert(self, auth_log: AuthenticationLog):
        """Trigger security alert for high-risk events"""
        try:
            # Create security audit entry
            audit_entry = SecurityAudit(
                user_id=auth_log.user_id,
                audit_category="authentication",
                audit_action="security_alert",
                resource_type="authentication_event",
                resource_id=str(auth_log.id),
                severity_level="high",
                audit_result="alert_triggered",
                audit_message=f"High-risk authentication event: {auth_log.event_type}",
                ip_address=auth_log.ip_address,
                user_agent=auth_log.user_agent,
                session_id=auth_log.session_id,
                request_context={
                    "risk_score": auth_log.risk_score,
                    "anomaly_indicators": auth_log.anomaly_indicators
                }
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
            logger.warning(f"Security alert triggered for auth log {auth_log.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")
    
    async def log_security_audit(
        self,
        audit_category: str,
        audit_action: str,
        audit_message: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        severity_level: str = "info",
        compliance_tags: Optional[List[str]] = None
    ) -> str:
        """Log security audit event"""
        try:
            audit_entry = SecurityAudit(
                user_id=uuid.UUID(user_id) if user_id else None,
                audit_category=audit_category,
                audit_action=audit_action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                actor_id=uuid.UUID(actor_id) if actor_id else None,
                actor_type=actor_type,
                ip_address=ip_address,
                session_id=session_id,
                compliance_tags=compliance_tags or [],
                severity_level=severity_level,
                audit_result="success",
                audit_message=audit_message
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
            logger.info(f"Security audit logged: {audit_category}.{audit_action}")
            return str(audit_entry.id)
            
        except Exception as e:
            logger.error(f"Failed to log security audit: {e}")
            await self.db.rollback()
            raise
    
    async def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_description: str,
        action_performed: str,
        activity_result: str,
        ip_address: str,
        resource_accessed: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        data_accessed: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track user activity"""
        try:
            activity = ActivityTracker(
                user_id=uuid.UUID(user_id),
                activity_type=activity_type,
                activity_description=activity_description,
                resource_accessed=resource_accessed,
                action_performed=action_performed,
                activity_result=activity_result,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=uuid.UUID(device_id) if device_id else None,
                session_id=session_id,
                duration_ms=duration_ms,
                data_accessed=data_accessed,
                metadata=metadata
            )
            
            self.db.add(activity)
            await self.db.commit()
            
            return str(activity.id)
            
        except Exception as e:
            logger.error(f"Failed to track user activity: {e}")
            await self.db.rollback()
            raise
    
    async def log_compliance_event(
        self,
        compliance_framework: str,
        regulation_requirement: str,
        processing_purpose: str,
        user_id: Optional[str] = None,
        personal_data_categories: Optional[List[str]] = None,
        legal_basis: Optional[str] = None,
        data_retention_period: Optional[int] = None,
        encryption_status: str = "encrypted",
        compliance_status: str = "compliant"
    ) -> str:
        """Log compliance event"""
        try:
            compliance_log = ComplianceLog(
                user_id=uuid.UUID(user_id) if user_id else None,
                compliance_framework=compliance_framework,
                regulation_requirement=regulation_requirement,
                personal_data_categories=personal_data_categories or [],
                processing_purpose=processing_purpose,
                legal_basis=legal_basis,
                data_retention_period=data_retention_period,
                encryption_status=encryption_status,
                compliance_status=compliance_status
            )
            
            self.db.add(compliance_log)
            await self.db.commit()
            
            return str(compliance_log.id)
            
        except Exception as e:
            logger.error(f"Failed to log compliance event: {e}")
            await self.db.rollback()
            raise
    
    async def get_user_auth_history(
        self,
        user_id: str,
        limit: int = 100,
        event_type: Optional[AuthEventType] = None
    ) -> List[Dict[str, Any]]:
        """Get user authentication history"""
        try:
            query = self.db.query(AuthenticationLog).filter(
                AuthenticationLog.user_id == uuid.UUID(user_id)
            )
            
            if event_type:
                query = query.filter(AuthenticationLog.event_type == event_type.value)
            
            logs = query.order_by(AuthenticationLog.created_at.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    "id": str(log.id),
                    "event_type": log.event_type,
                    "auth_result": log.auth_result,
                    "auth_method": log.auth_method,
                    "ip_address": log.ip_address,
                    "device_fingerprint": log.device_fingerprint,
                    "risk_score": log.risk_score,
                    "risk_level": log.risk_level,
                    "failure_reason": log.failure_reason,
                    "created_at": log.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user auth history: {e}")
            return []
    
    async def get_security_alerts(
        self,
        user_id: Optional[str] = None,
        severity_level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get security alerts"""
        try:
            query = self.db.query(SecurityAudit).filter(
                SecurityAudit.audit_category == "authentication"
            )
            
            if user_id:
                query = query.filter(SecurityAudit.user_id == uuid.UUID(user_id))
            
            if severity_level:
                query = query.filter(SecurityAudit.severity_level == severity_level)
            
            alerts = query.order_by(SecurityAudit.created_at.desc()).limit(limit).all()
            
            result = []
            for alert in alerts:
                result.append({
                    "id": str(alert.id),
                    "audit_action": alert.audit_action,
                    "severity_level": alert.severity_level,
                    "audit_message": alert.audit_message,
                    "user_id": str(alert.user_id) if alert.user_id else None,
                    "ip_address": alert.ip_address,
                    "created_at": alert.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get security alerts: {e}")
            return []
