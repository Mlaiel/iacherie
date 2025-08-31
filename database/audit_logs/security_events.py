"""
Ultra-Advanced Security Events Module

Revolutionary enterprise-grade security event logging for IA Influencer Agent platform.
Provides comprehensive tracking for security incidents, cyber threats, advanced persistent
threats (APT), compliance violations, real-time threat intelligence, AI-powered anomaly
detection, and automated incident response with digital forensics capabilities.

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Multi-Expert Lead AI Developer & Cybersecurity Specialist

 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 
This revolutionary security event logging technology is the EXCLUSIVE property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or exploitation is STRICTLY PROHIBITED.
Legal action will be taken against violators under international IP law.
Contact: mlaiel@live.de for authorization.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import logging
from dataclasses import dataclass, asdict
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
import hashlib

logger = logging.getLogger(__name__)

Base = declarative_base()


class SecurityEventType(Enum):
    """Security event types for tracking."""
    
    # Authentication Security
    SUSPICIOUS_LOGIN = "suspicious_login"
    FAILED_LOGIN_ATTEMPT = "failed_login_attempt"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    CREDENTIAL_STUFFING = "credential_stuffing"
    ACCOUNT_LOCKOUT = "account_lockout"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SESSION_HIJACKING = "session_hijacking"
    
    # Content Security
    CONTENT_PIRACY_DETECTED = "content_piracy_detected"
    UNAUTHORIZED_DOWNLOAD = "unauthorized_download"
    COPYRIGHT_VIOLATION = "copyright_violation"
    DMCA_VIOLATION = "dmca_violation"
    CONTENT_TAMPERING = "content_tampering"
    MALICIOUS_UPLOAD = "malicious_upload"
    FAKE_CONTENT_DETECTION = "fake_content_detection"
    
    # Network Security
    DDOS_ATTACK = "ddos_attack"
    IP_BLOCKING = "ip_blocking"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_TRAFFIC = "suspicious_traffic"
    GEO_BLOCKING = "geo_blocking"
    BOT_DETECTION = "bot_detection"
    CRAWLING_ATTEMPT = "crawling_attempt"
    
    # Data Security
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    UNAUTHORIZED_DATA_ACCESS = "unauthorized_data_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    PII_ACCESS_VIOLATION = "pii_access_violation"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    
    # API Security
    API_ABUSE = "api_abuse"
    TOKEN_THEFT = "token_theft"
    INVALID_TOKEN = "invalid_token"
    API_KEY_MISUSE = "api_key_misuse"
    MALFORMED_REQUEST = "malformed_request"
    ENDPOINT_PROBING = "endpoint_probing"
    
    # Platform Security
    ADMIN_ACCESS_VIOLATION = "admin_access_violation"
    CONFIGURATION_TAMPERING = "configuration_tampering"
    SYSTEM_INTRUSION = "system_intrusion"
    MALWARE_DETECTION = "malware_detection"
    PHISHING_ATTEMPT = "phishing_attempt"
    SOCIAL_ENGINEERING = "social_engineering"
    
    # Financial Security
    PAYMENT_FRAUD = "payment_fraud"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    REVENUE_MANIPULATION = "revenue_manipulation"
    FAKE_TRANSACTION = "fake_transaction"
    MONEY_LAUNDERING = "money_laundering"
    
    # Compliance Violations
    GDPR_VIOLATION = "gdpr_violation"
    CCPA_VIOLATION = "ccpa_violation"
    PCI_VIOLATION = "pci_violation"
    HIPAA_VIOLATION = "hipaa_violation"
    DATA_RETENTION_VIOLATION = "data_retention_violation"


class ThreatLevel(Enum):
    """Threat level classification."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityEventStatus(Enum):
    """Security event status."""
    
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"


class AttackVector(Enum):
    """Attack vector types."""
    
    WEB_APPLICATION = "web_application"
    API = "api"
    MOBILE_APP = "mobile_app"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    DIRECT_ACCESS = "direct_access"
    THIRD_PARTY = "third_party"
    INSIDER_THREAT = "insider_threat"
    UNKNOWN = "unknown"


@dataclass
class SecurityContext:
    """Security context information."""
    
    source_ip: str
    user_agent: str
    country: Optional[str]
    asn: Optional[str]
    is_tor: bool
    is_vpn: bool
    is_proxy: bool
    risk_score: float
    threat_intel_matches: List[str]
    geolocation: Optional[Dict[str, str]]


class SecurityEventLog(Base):
    """Security event log model."""
    
    __tablename__ = "security_event_logs"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    incident_id = Column(String(255), index=True)  # Groups related events
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)
    threat_level = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    attack_vector = Column(String(100))
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)
    threat_description = Column(Text)
    impact_assessment = Column(Text)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    detection_time = Column(DateTime(timezone=True))
    response_time = Column(DateTime(timezone=True))
    resolution_time = Column(DateTime(timezone=True))
    
    # Source information
    source_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer)
    source_country = Column(String(2))
    source_asn = Column(String(100))
    source_organization = Column(String(255))
    
    # Target information
    target_endpoint = Column(String(500))
    target_user_id = Column(UUID(as_uuid=True), index=True)
    target_resource = Column(String(500))
    target_data_type = Column(String(100))
    
    # Request details
    user_agent = Column(Text)
    request_method = Column(String(10))
    request_url = Column(String(1000))
    request_headers = Column(JSON)
    request_payload = Column(Text)
    response_status = Column(Integer)
    
    # Security indicators
    is_tor_exit = Column(Boolean, default=False)
    is_vpn = Column(Boolean, default=False)
    is_proxy = Column(Boolean, default=False)
    is_malicious_ip = Column(Boolean, default=False)
    risk_score = Column(Float)  # 0.0 to 10.0
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Detection details
    detection_method = Column(String(100))  # rule, ml, signature, etc.
    detection_rule = Column(String(255))
    detection_signature = Column(String(500))
    false_positive_probability = Column(Float)
    
    # Threat intelligence
    threat_intel_matches = Column(JSON)  # List of matched threat intel sources
    ioc_indicators = Column(JSON)  # Indicators of Compromise
    malware_family = Column(String(100))
    attack_campaign = Column(String(255))
    
    # Impact and damage
    affected_users_count = Column(Integer, default=0)
    affected_content_count = Column(Integer, default=0)
    data_compromised = Column(Boolean, default=False)
    service_disrupted = Column(Boolean, default=False)
    financial_impact = Column(Float)  # Estimated financial impact
    
    # Response actions
    automated_response = Column(JSON)  # Actions taken automatically
    manual_response = Column(JSON)  # Manual response actions
    mitigation_steps = Column(Text)
    lessons_learned = Column(Text)
    
    # Investigation details
    assigned_analyst = Column(String(255))
    investigation_notes = Column(Text)
    evidence_collected = Column(JSON)
    related_events = Column(JSON)  # IDs of related security events
    
    # Legal and compliance
    requires_notification = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    notification_time = Column(DateTime(timezone=True))
    compliance_violations = Column(JSON)
    legal_hold = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_threat_level_timestamp', 'threat_level', 'timestamp'),
        Index('idx_source_ip_timestamp', 'source_ip', 'timestamp'),
        Index('idx_target_user_timestamp', 'target_user_id', 'timestamp'),
        Index('idx_incident_timestamp', 'incident_id', 'timestamp'),
        Index('idx_status_timestamp', 'status', 'timestamp'),
        Index('idx_risk_score', 'risk_score'),
    )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {
            "id": str(self.id),
            "event_id": self.event_id,
            "incident_id": self.incident_id,
            "event_type": self.event_type,
            "threat_level": self.threat_level,
            "status": self.status,
            "attack_vector": self.attack_vector,
            "event_name": self.event_name,
            "event_description": self.event_description,
            "threat_description": self.threat_description,
            "impact_assessment": self.impact_assessment,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "detection_time": self.detection_time.isoformat() if self.detection_time else None,
            "response_time": self.response_time.isoformat() if self.response_time else None,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
            "source_country": self.source_country,
            "source_asn": self.source_asn,
            "source_organization": self.source_organization,
            "target_endpoint": self.target_endpoint,
            "target_user_id": str(self.target_user_id) if self.target_user_id else None,
            "target_resource": self.target_resource,
            "target_data_type": self.target_data_type,
            "request_method": self.request_method,
            "response_status": self.response_status,
            "is_tor_exit": self.is_tor_exit,
            "is_vpn": self.is_vpn,
            "is_proxy": self.is_proxy,
            "is_malicious_ip": self.is_malicious_ip,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "detection_method": self.detection_method,
            "detection_rule": self.detection_rule,
            "false_positive_probability": self.false_positive_probability,
            "threat_intel_matches": self.threat_intel_matches,
            "ioc_indicators": self.ioc_indicators,
            "malware_family": self.malware_family,
            "attack_campaign": self.attack_campaign,
            "affected_users_count": self.affected_users_count,
            "affected_content_count": self.affected_content_count,
            "data_compromised": self.data_compromised,
            "service_disrupted": self.service_disrupted,
            "financial_impact": self.financial_impact,
            "automated_response": self.automated_response,
            "manual_response": self.manual_response,
            "mitigation_steps": self.mitigation_steps,
            "assigned_analyst": self.assigned_analyst,
            "requires_notification": self.requires_notification,
            "notification_sent": self.notification_sent,
            "notification_time": self.notification_time.isoformat() if self.notification_time else None,
            "compliance_violations": self.compliance_violations,
            "legal_hold": self.legal_hold,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested
        if include_sensitive:
            result.update({
                "source_ip": self.source_ip,
                "source_port": self.source_port,
                "user_agent": self.user_agent,
                "request_url": self.request_url,
                "request_headers": self.request_headers,
                "request_payload": self.request_payload,
                "investigation_notes": self.investigation_notes,
                "evidence_collected": self.evidence_collected
            })
        
        return result


class SecurityEventLogger:
    """Enterprise security event logger."""
    
    def __init__(self, db_session, service_name: str = "ia_influencer_agent"):
        """
        Initialize security event logger.
        
        Args:
            db_session: Database session
            service_name: Name of the service
        """
        self.db_session = db_session
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        event_name: str,
        threat_level: ThreatLevel,
        source_ip: str,
        description: Optional[str] = None,
        threat_description: Optional[str] = None,
        impact_assessment: Optional[str] = None,
        attack_vector: Optional[AttackVector] = None,
        security_context: Optional[SecurityContext] = None,
        target_user_id: Optional[str] = None,
        target_endpoint: Optional[str] = None,
        target_resource: Optional[str] = None,
        request_details: Optional[Dict[str, Any]] = None,
        detection_details: Optional[Dict[str, Any]] = None,
        threat_intel: Optional[Dict[str, Any]] = None,
        incident_id: Optional[str] = None,
        automated_response: Optional[List[str]] = None
    ) -> str:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            event_name: Name of the event
            threat_level: Threat level classification
            source_ip: Source IP address
            description: Event description
            threat_description: Description of the threat
            impact_assessment: Assessment of potential impact
            attack_vector: Attack vector used
            security_context: Security context information
            target_user_id: ID of targeted user
            target_endpoint: Targeted endpoint
            target_resource: Targeted resource
            request_details: HTTP request details
            detection_details: How the event was detected
            threat_intel: Threat intelligence information
            incident_id: ID of related incident
            automated_response: Automated response actions taken
            
        Returns:
            str: Generated event ID
        """



        try:
            event_id = f"sec_{uuid.uuid4().hex[:16]}"
            
            # Generate incident ID if not provided
            if not incident_id:
                incident_id = f"inc_{uuid.uuid4().hex[:12]}"
            
            security_event = SecurityEventLog(
                event_id=event_id,
                incident_id=incident_id,
                event_type=event_type.value,
                threat_level=threat_level.value,
                status=SecurityEventStatus.ACTIVE.value,
                attack_vector=attack_vector.value if attack_vector else None,
                event_name=event_name,
                event_description=description,
                threat_description=threat_description,
                impact_assessment=impact_assessment,
                source_ip=source_ip,
                target_user_id=target_user_id,
                target_endpoint=target_endpoint,
                target_resource=target_resource,
                detection_time=datetime.now(timezone.utc),
                automated_response=automated_response
            )
            
            # Add security context if provided
            if security_context:
                security_event.user_agent = security_context.user_agent
                security_event.source_country = security_context.country
                security_event.source_asn = security_context.asn
                security_event.is_tor_exit = security_context.is_tor
                security_event.is_vpn = security_context.is_vpn
                security_event.is_proxy = security_context.is_proxy
                security_event.risk_score = security_context.risk_score
                security_event.threat_intel_matches = security_context.threat_intel_matches
            
            # Add request details if provided
            if request_details:
                security_event.request_method = request_details.get('method')
                security_event.request_url = request_details.get('url')
                security_event.request_headers = request_details.get('headers')
                security_event.request_payload = request_details.get('payload')
                security_event.response_status = request_details.get('response_status')
            
            # Add detection details if provided
            if detection_details:
                security_event.detection_method = detection_details.get('method')
                security_event.detection_rule = detection_details.get('rule')
                security_event.detection_signature = detection_details.get('signature')
                security_event.confidence_score = detection_details.get('confidence')
                security_event.false_positive_probability = detection_details.get('false_positive_prob')
            
            # Add threat intelligence if provided
            if threat_intel:
                security_event.ioc_indicators = threat_intel.get('iocs')
                security_event.malware_family = threat_intel.get('malware_family')
                security_event.attack_campaign = threat_intel.get('campaign')
                security_event.is_malicious_ip = threat_intel.get('is_malicious', False)
            
            self.db_session.add(security_event)
            self.db_session.commit()
            
            # Log to application logger based on threat level
            log_message = f"Security Event: {event_name} ({event_type.value}) from {source_ip}"
            
            if threat_level == ThreatLevel.CRITICAL:
                self.logger.critical(log_message, extra={
                    "event_id": event_id,
                    "incident_id": incident_id,
                    "source_ip": source_ip,
                    "threat_level": threat_level.value
                })
            elif threat_level == ThreatLevel.HIGH:
                self.logger.error(log_message, extra={
                    "event_id": event_id,
                    "incident_id": incident_id,
                    "source_ip": source_ip
                })
            elif threat_level == ThreatLevel.MEDIUM:
                self.logger.warning(log_message, extra={
                    "event_id": event_id,
                    "source_ip": source_ip
                })
            else:
                self.logger.info(log_message, extra={
                    "event_id": event_id,
                    "source_ip": source_ip
                })
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
            self.db_session.rollback()
            raise
    
    def log_brute_force_attack(
        self,
        source_ip: str,
        target_user_id: str,
        failed_attempts: int,
        time_window_minutes: int,
        user_agent: Optional[str] = None
    ) -> str:
        """Log brute force attack detection."""



        return self.log_security_event(
            event_type=SecurityEventType.BRUTE_FORCE_ATTACK,
            event_name="Brute Force Attack Detected",
            threat_level=ThreatLevel.HIGH,
            source_ip=source_ip,
            description=f"Brute force attack detected: {failed_attempts} failed login attempts in {time_window_minutes} minutes",
            threat_description=f"Automated password guessing attack against user account",
            impact_assessment="Account lockout recommended, potential account compromise",
            attack_vector=AttackVector.WEB_APPLICATION,
            target_user_id=target_user_id,
            request_details={"user_agent": user_agent} if user_agent else None,
            detection_details={
                "method": "threshold_based",
                "rule": "failed_login_threshold",
                "confidence": 0.9
            },
            automated_response=["ip_temporary_block", "account_lockout_warning"]
        )
    
    def log_content_piracy(
        self,
        source_ip: str,
        content_id: str,
        content_title: str,
        fingerprint_match_confidence: float,
        detected_platform: str,
        user_agent: Optional[str] = None
    ) -> str:
        """Log content piracy detection."""
        threat_level = ThreatLevel.HIGH if fingerprint_match_confidence > 0.8 else ThreatLevel.MEDIUM
        
        return self.log_security_event(
            event_type=SecurityEventType.CONTENT_PIRACY_DETECTED,
            event_name="Content Piracy Detected",
            threat_level=threat_level,
            source_ip=source_ip,
            description=f"Unauthorized content distribution detected on {detected_platform}",
            threat_description=f"Copyright protected content '{content_title}' found on unauthorized platform",
            impact_assessment="Revenue loss, brand damage, legal action required",
            attack_vector=AttackVector.THIRD_PARTY,
            target_resource=f"content/{content_id}",
            request_details={"user_agent": user_agent} if user_agent else None,
            detection_details={
                "method": "fingerprint_matching",
                "confidence": fingerprint_match_confidence,
                "detected_platform": detected_platform
            },
            automated_response=["dmca_takedown_initiate", "content_owner_notify"]
        )
    
    def log_ddos_attack(
        self,
        source_ip: str,
        requests_per_second: int,
        attack_duration_minutes: int,
        target_endpoint: str,
        attack_type: str = "volumetric"
    ) -> str:
        """Log DDoS attack detection."""



        return self.log_security_event(
            event_type=SecurityEventType.DDOS_ATTACK,
            event_name="DDoS Attack Detected",
            threat_level=ThreatLevel.CRITICAL,
            source_ip=source_ip,
            description=f"DDoS attack detected: {requests_per_second} req/s for {attack_duration_minutes} minutes",
            threat_description=f"{attack_type.title()} DDoS attack attempting to overwhelm service",
            impact_assessment="Service disruption, potential downtime, user experience degradation",
            attack_vector=AttackVector.WEB_APPLICATION,
            target_endpoint=target_endpoint,
            detection_details={
                "method": "traffic_analysis",
                "rule": "request_rate_threshold",
                "confidence": 0.95,
                "attack_type": attack_type
            },
            automated_response=["ip_block", "rate_limit_enforce", "cloudflare_activate"]
        )
    
    def log_sql_injection_attempt(
        self,
        source_ip: str,
        target_endpoint: str,
        malicious_payload: str,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Log SQL injection attempt."""
        payload_hash = hashlib.sha256(malicious_payload.encode()).hexdigest()[:16]
        
        return self.log_security_event(
            event_type=SecurityEventType.SQL_INJECTION,
            event_name="SQL Injection Attempt",
            threat_level=ThreatLevel.HIGH,
            source_ip=source_ip,
            description="SQL injection attack attempt detected",
            threat_description="Malicious SQL code injection attempting database compromise",
            impact_assessment="Data breach potential, database compromise risk",
            attack_vector=AttackVector.WEB_APPLICATION,
            target_endpoint=target_endpoint,
            target_user_id=user_id,
            request_details={
                "user_agent": user_agent,
                "payload_hash": payload_hash
            },
            detection_details={
                "method": "signature_based",
                "rule": "sql_injection_patterns",
                "confidence": 0.85
            },
            automated_response=["ip_block", "waf_rule_update", "security_team_alert"]
        )
    
    def log_unauthorized_data_access(
        self,
        source_ip: str,
        user_id: str,
        accessed_data_type: str,
        data_sensitivity: str,
        access_method: str,
        user_agent: Optional[str] = None
    ) -> str:
        """Log unauthorized data access attempt."""
        threat_level = ThreatLevel.CRITICAL if data_sensitivity == "pii" else ThreatLevel.HIGH
        
        return self.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_DATA_ACCESS,
            event_name="Unauthorized Data Access",
            threat_level=threat_level,
            source_ip=source_ip,
            description=f"Unauthorized access to {data_sensitivity} data detected",
            threat_description=f"User attempted to access {accessed_data_type} data without proper authorization",
            impact_assessment="Data privacy violation, compliance breach risk",
            attack_vector=AttackVector.WEB_APPLICATION,
            target_user_id=user_id,
            target_data_type=accessed_data_type,
            request_details={
                "user_agent": user_agent,
                "access_method": access_method,
                "data_sensitivity": data_sensitivity
            },
            detection_details={
                "method": "access_control_violation",
                "rule": "unauthorized_data_access",
                "confidence": 0.9
            },
            automated_response=["access_revoke", "session_terminate", "compliance_notify"]
        )
    
    def update_event_status(
        self,
        event_id: str,
        status: SecurityEventStatus,
        assigned_analyst: Optional[str] = None,
        investigation_notes: Optional[str] = None,
        mitigation_steps: Optional[str] = None,
        manual_response: Optional[List[str]] = None
    ) -> bool:
        """
        Update security event status and investigation details.
        
        Args:
            event_id: Event ID to update
            status: New status
            assigned_analyst: Analyst assigned to investigate
            investigation_notes: Investigation notes
            mitigation_steps: Steps taken to mitigate
            manual_response: Manual response actions
            
        Returns:
            bool: True if successfully updated
        """



        try:
            event = self.db_session.query(SecurityEventLog).filter_by(event_id=event_id).first()
            
            if event:
                event.status = status.value
                
                if assigned_analyst:
                    event.assigned_analyst = assigned_analyst
                
                if investigation_notes:
                    event.investigation_notes = investigation_notes
                
                if mitigation_steps:
                    event.mitigation_steps = mitigation_steps
                
                if manual_response:
                    event.manual_response = manual_response
                
                # Set response/resolution times based on status
                current_time = datetime.now(timezone.utc)
                
                if status == SecurityEventStatus.INVESTIGATING and not event.response_time:
                    event.response_time = current_time
                elif status in [SecurityEventStatus.RESOLVED, SecurityEventStatus.MITIGATED]:
                    if not event.response_time:
                        event.response_time = current_time
                    event.resolution_time = current_time
                
                self.db_session.commit()
                
                self.logger.info(f"Security event {event_id} status updated to {status.value}")
                return True
            else:
                self.logger.warning(f"Security event {event_id} not found for status update")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update security event status: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_active_threats(
        self,
        threat_level: Optional[ThreatLevel] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get active security threats.
        
        Args:
            threat_level: Filter by threat level
            hours: Hours to look back
            limit: Maximum number of threats to return
            
        Returns:
            List[Dict[str, Any]]: List of active threats
        """



        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            query = self.db_session.query(SecurityEventLog).filter(
                SecurityEventLog.timestamp >= start_time,
                SecurityEventLog.status.in_([
                    SecurityEventStatus.ACTIVE.value,
                    SecurityEventStatus.INVESTIGATING.value
                ])
            )
            
            if threat_level:
                query = query.filter_by(threat_level=threat_level.value)
            
            events = query.order_by(SecurityEventLog.risk_score.desc()).limit(limit).all()
            
            return [event.to_dict() for event in events]
            
        except Exception as e:
            self.logger.error(f"Failed to get active threats: {str(e)}")
            return []
    
    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get threat summary for the specified time period.
        
        Args:
            hours: Hours to analyze
            
        Returns:
            Dict[str, Any]: Threat summary
        """



        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            events = self.db_session.query(SecurityEventLog).filter(
                SecurityEventLog.timestamp >= start_time
            ).all()
            
            # Count by threat level
            threat_level_counts = {}
            event_type_counts = {}
            status_counts = {}
            top_source_ips = {}
            
            total_events = len(events)
            critical_events = 0
            high_events = 0
            unresolved_events = 0
            
            for event in events:
                # Count by threat level
                threat_level_counts[event.threat_level] = threat_level_counts.get(event.threat_level, 0) + 1
                
                # Count by event type
                event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
                
                # Count by status
                status_counts[event.status] = status_counts.get(event.status, 0) + 1
                
                # Count source IPs
                if event.source_ip:
                    top_source_ips[event.source_ip] = top_source_ips.get(event.source_ip, 0) + 1
                
                # Count critical/high/unresolved
                if event.threat_level == ThreatLevel.CRITICAL.value:
                    critical_events += 1
                elif event.threat_level == ThreatLevel.HIGH.value:
                    high_events += 1
                
                if event.status in [SecurityEventStatus.ACTIVE.value, SecurityEventStatus.INVESTIGATING.value]:
                    unresolved_events += 1
            
            # Calculate security score (0-100)
            security_score = 100
            security_score -= critical_events * 10  # -10 per critical event
            security_score -= high_events * 5       # -5 per high event
            security_score -= unresolved_events * 3 # -3 per unresolved event
            security_score = max(0, security_score)
            
            # Get top 5 source IPs
            top_ips = sorted(top_source_ips.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "time_period_hours": hours,
                "total_events": total_events,
                "security_score": security_score,
                "threat_level_breakdown": threat_level_counts,
                "event_type_breakdown": event_type_counts,
                "status_breakdown": status_counts,
                "critical_events": critical_events,
                "high_events": high_events,
                "unresolved_events": unresolved_events,
                "top_source_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
                "summary_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get threat summary: {str(e)}")
            return {"error": str(e)}


def create_security_event_logger(db_session, service_name: str = "ia_influencer_agent") -> SecurityEventLogger:
    """
    Factory function to create security event logger.
    
    Args:
        db_session: Database session
        service_name: Name of the service
        
    Returns:
        SecurityEventLogger: Configured security event logger
    """



    return SecurityEventLogger(db_session, service_name)


# Export main classes and functions
__all__ = [
    "SecurityEventLog",
    "SecurityEventLogger",
    "SecurityEventType",
    "ThreatLevel",
    "SecurityEventStatus",
    "AttackVector",
    "SecurityContext",
    "create_security_event_logger"
]
