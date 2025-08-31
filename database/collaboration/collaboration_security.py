"""
Collaboration Security Database Module

Enterprise-grade security framework for collaborative projects with advanced
access control, audit logging, threat detection, and compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
import hashlib
import secrets
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress

logger = logging.getLogger(__name__)

Base = declarative_base()

class SecurityRole(Enum):
    """Security roles for collaboration access control"""
    OWNER = "owner"
    ADMIN = "admin"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    GUEST = "guest"
    EXTERNAL_PARTNER = "external_partner"
    RESTRICTED_ACCESS = "restricted_access"

class PermissionType(Enum):
    """Granular permission types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SHARE = "share"
    DOWNLOAD = "download"
    COMMENT = "comment"
    APPROVE = "approve"
    MANAGE_USERS = "manage_users"
    MANAGE_PERMISSIONS = "manage_permissions"
    EXPORT = "export"
    PUBLISH = "publish"

class AccessControlScope(Enum):
    """Scope of access control"""
    PROJECT = "project"
    CONTENT = "content"
    WORKFLOW = "workflow"
    TEAM = "team"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    FINANCIAL = "financial"
    SYSTEM = "system"

class SecurityEventType(Enum):
    """Types of security events for audit logging"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    CONTENT_ACCESS = "content_access"
    CONTENT_MODIFIED = "content_modified"
    CONTENT_SHARED = "content_shared"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_BREACH = "security_breach"
    DATA_EXPORT = "data_export"
    CONFIGURATION_CHANGE = "configuration_change"

class ThreatLevel(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CollaborationAccessControl(Base):
    """
    Granular access control for collaboration projects and resources.
    """
    __tablename__ = 'collaboration_access_control'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Role and permissions
    role = Column(ENUM(SecurityRole), nullable=False)
    permissions = Column(ARRAY(ENUM(PermissionType)))
    scope = Column(ENUM(AccessControlScope), nullable=False)
    
    # Access constraints
    ip_restrictions = Column(ARRAY(String))  # CIDR notation
    time_restrictions = Column(JSONB)  # Time-based access rules
    device_restrictions = Column(JSONB)  # Device fingerprinting
    location_restrictions = Column(JSONB)  # Geo-fencing
    
    # Resource-specific permissions
    resource_id = Column(UUID(as_uuid=True))  # Specific resource (content, workflow, etc.)
    resource_type = Column(String(100))
    resource_permissions = Column(JSONB)  # Granular resource permissions
    
    # Delegation and inheritance
    granted_by = Column(UUID(as_uuid=True), nullable=False)
    can_delegate = Column(Boolean, default=False)
    inherited_from = Column(UUID(as_uuid=True))  # Parent permission
    
    # Temporal access control
    effective_from = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_temporary = Column(Boolean, default=False)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    suspension_reason = Column(Text)
    metadata = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Performance indexes
    __table_args__ = (
        Index('idx_access_project_user', 'project_id', 'user_id'),
        Index('idx_access_role_scope', 'role', 'scope'),
        Index('idx_access_expiry', 'expires_at', 'is_active'),
    )

class SecurityAuditLog(Base):
    """
    Comprehensive audit logging for all security-related events.
    """
    __tablename__ = 'security_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(ENUM(SecurityEventType), nullable=False)
    event_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(255))
    
    # Actor information
    user_id = Column(UUID(as_uuid=True))
    user_email = Column(String(255))
    user_role = Column(ENUM(SecurityRole))
    impersonated_by = Column(UUID(as_uuid=True))  # For admin impersonation
    
    # Context information
    project_id = Column(UUID(as_uuid=True))
    resource_id = Column(UUID(as_uuid=True))
    resource_type = Column(String(100))
    action_performed = Column(String(255))
    
    # Technical details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    request_id = Column(String(255))
    api_endpoint = Column(String(500))
    http_method = Column(String(10))
    http_status_code = Column(Integer)
    
    # Security context
    authentication_method = Column(String(100))
    mfa_verified = Column(Boolean)
    risk_score = Column(Float)  # 0-100
    threat_level = Column(ENUM(ThreatLevel))
    
    # Geolocation and device
    country_code = Column(String(2))
    city = Column(String(100))
    device_fingerprint = Column(String(255))
    device_type = Column(String(50))
    browser_info = Column(JSONB)
    
    # Event details
    event_data = Column(JSONB)  # Detailed event payload
    previous_values = Column(JSONB)  # For change tracking
    new_values = Column(JSONB)  # For change tracking
    
    # Results and impact
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    error_code = Column(String(100))
    impact_assessment = Column(JSONB)
    
    # Timing information
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_duration_ms = Column(Integer)
    
    # Investigation and response
    is_flagged = Column(Boolean, default=False)
    investigation_status = Column(String(50))  # pending, in_progress, resolved
    assigned_to = Column(UUID(as_uuid=True))
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    # Compliance and retention
    retention_period_days = Column(Integer, default=2555)  # 7 years default
    is_pii_anonymized = Column(Boolean, default=False)
    compliance_tags = Column(ARRAY(String))
    
    # Performance indexes
    __table_args__ = (
        Index('idx_audit_event_timestamp', 'event_timestamp'),
        Index('idx_audit_user_event', 'user_id', 'event_type'),
        Index('idx_audit_project_event', 'project_id', 'event_type'),
        Index('idx_audit_threat_level', 'threat_level', 'event_timestamp'),
        Index('idx_audit_flagged', 'is_flagged', 'event_timestamp'),
    )

class SecurityPolicy(Base):
    """
    Security policies and rules for collaboration projects.
    """
    __tablename__ = 'security_policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(255), nullable=False)
    policy_type = Column(String(100), nullable=False)  # access_control, data_protection, compliance
    
    # Policy scope
    scope = Column(ENUM(AccessControlScope), nullable=False)
    applies_to_projects = Column(ARRAY(UUID(as_uuid=True)))  # Empty = all projects
    applies_to_roles = Column(ARRAY(ENUM(SecurityRole)))
    
    # Policy definition
    policy_rules = Column(JSONB, nullable=False)
    policy_conditions = Column(JSONB)
    enforcement_level = Column(String(50), default="strict")  # advisory, standard, strict
    
    # Implementation details
    auto_enforce = Column(Boolean, default=True)
    violation_action = Column(String(100))  # warn, block, suspend, escalate
    notification_settings = Column(JSONB)
    
    # Compliance framework
    compliance_framework = Column(String(100))  # GDPR, SOX, HIPAA, ISO27001
    regulatory_requirements = Column(JSONB)
    audit_requirements = Column(JSONB)
    
    # Policy lifecycle
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    review_frequency_days = Column(Integer, default=365)
    last_reviewed_at = Column(DateTime)
    next_review_due = Column(DateTime)
    
    # Approval and governance
    approved_by = Column(UUID(as_uuid=True))
    approval_date = Column(DateTime)
    policy_version = Column(String(50), default="1.0")
    change_reason = Column(Text)
    
    # Metrics and effectiveness
    violation_count = Column(Integer, default=0)
    exception_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)  # 0-100
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ThreatDetection(Base):
    """
    Real-time threat detection and security monitoring.
    """
    __tablename__ = 'threat_detections'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Threat identification
    threat_id = Column(String(100), unique=True, nullable=False)
    threat_type = Column(String(100), nullable=False)
    threat_level = Column(ENUM(ThreatLevel), nullable=False)
    threat_score = Column(Float, nullable=False)  # 0-100
    
    # Detection details
    detection_method = Column(String(100))  # rule_based, ml_based, anomaly_detection
    detection_algorithm = Column(String(100))
    confidence_score = Column(Float)  # 0-100
    
    # Source information
    source_ip = Column(String(45))
    source_country = Column(String(2))
    user_id = Column(UUID(as_uuid=True))
    session_id = Column(String(255))
    project_id = Column(UUID(as_uuid=True))
    
    # Threat context
    attack_vector = Column(String(100))
    attack_pattern = Column(String(100))
    affected_resources = Column(ARRAY(String))
    potential_impact = Column(JSONB)
    
    # Evidence and indicators
    indicators_of_compromise = Column(JSONB)
    attack_signatures = Column(JSONB)
    behavioral_anomalies = Column(JSONB)
    supporting_evidence = Column(JSONB)
    
    # Response and mitigation
    auto_response_taken = Column(Boolean, default=False)
    response_actions = Column(JSONB)
    mitigation_steps = Column(JSONB)
    escalation_required = Column(Boolean, default=False)
    
    # Investigation workflow
    status = Column(String(50), default="detected")  # detected, investigating, confirmed, false_positive, resolved
    assigned_to = Column(UUID(as_uuid=True))
    investigation_notes = Column(Text)
    investigation_timeline = Column(JSONB)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolution_method = Column(String(100))
    resolution_time_minutes = Column(Integer)
    lessons_learned = Column(Text)
    
    # Timing
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    last_detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Related incidents
    related_threats = Column(ARRAY(UUID(as_uuid=True)))
    parent_incident_id = Column(UUID(as_uuid=True))
    
    # Performance indexes
    __table_args__ = (
        Index('idx_threat_level_timestamp', 'threat_level', 'first_detected_at'),
        Index('idx_threat_user_project', 'user_id', 'project_id'),
        Index('idx_threat_status', 'status', 'first_detected_at'),
    )

class EncryptionKey(Base):
    """
    Encryption key management for secure content storage and transmission.
    """
    __tablename__ = 'encryption_keys'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_id = Column(String(100), unique=True, nullable=False)
    
    # Key properties
    key_type = Column(String(50), nullable=False)  # AES256, RSA2048, etc.
    key_purpose = Column(String(100), nullable=False)  # content_encryption, communication, signature
    key_algorithm = Column(String(50), nullable=False)
    key_length = Column(Integer, nullable=False)
    
    # Key material (encrypted)
    encrypted_key_material = Column(Text, nullable=False)
    key_derivation_method = Column(String(100))
    salt = Column(String(255))
    iterations = Column(Integer)
    
    # Key scope and access
    project_id = Column(UUID(as_uuid=True))  # Project-specific key
    resource_type = Column(String(100))  # Type of resource this key protects
    authorized_users = Column(ARRAY(UUID(as_uuid=True)))
    authorized_roles = Column(ARRAY(ENUM(SecurityRole)))
    
    # Key lifecycle
    status = Column(String(50), default="active")  # active, expired, revoked, compromised
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime)
    revocation_reason = Column(Text)
    
    # Key rotation
    rotation_policy = Column(String(100))  # manual, time_based, usage_based
    rotation_frequency_days = Column(Integer)
    usage_count = Column(Integer, default=0)
    max_usage_count = Column(Integer)
    last_used_at = Column(DateTime)
    
    # Backup and recovery
    backup_locations = Column(ARRAY(String))
    recovery_threshold = Column(Integer)  # Shamir's Secret Sharing threshold
    
    # Compliance
    compliance_requirements = Column(ARRAY(String))
    audit_trail = Column(JSONB)
    
    # Performance indexes
    __table_args__ = (
        Index('idx_encryption_project_purpose', 'project_id', 'key_purpose'),
        Index('idx_encryption_status_expiry', 'status', 'expires_at'),
    )

@dataclass
class SecurityContext:
    """Security context for request validation"""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    project_id: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    mfa_verified: bool = False

class CollaborationSecurityEngine:
    """
    Comprehensive security engine for collaboration platform.
    Handles access control, threat detection, audit logging, and compliance.
    """
    
    def __init__(self, db_session, redis_client=None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize security components
        self.fernet = None
        self._initialize_encryption()
    
    async def validate_access(self, context: SecurityContext, required_permission: PermissionType, scope: AccessControlScope) -> bool:
        """
        Validate user access for specific action and scope.
        
        Args:
            context: Security context
            required_permission: Required permission
            scope: Access scope
            
        Returns:
            True if access is granted
        """



        try:
            # Log access attempt
            await self._log_security_event(
                SecurityEventType.PERMISSION_DENIED if not await self._check_access(context, required_permission, scope) else SecurityEventType.PERMISSION_GRANTED,
                context,
                {"permission": required_permission.value, "scope": scope.value}
            )
            
            # Check basic access control
            if not await self._check_access(context, required_permission, scope):
                return False
            
            # Check additional security constraints
            if not await self._check_ip_restrictions(context):
                return False
            
            if not await self._check_time_restrictions(context):
                return False
            
            if not await self._check_device_restrictions(context):
                return False
            
            # Threat detection
            risk_score = await self._calculate_risk_score(context)
            if risk_score > 80:  # High risk threshold
                await self._trigger_threat_detection(context, risk_score)
                return False
            
            # Update last access time
            await self._update_access_tracking(context)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating access: {str(e)}")
            return False
    
    async def grant_access(self, granter_id: str, user_id: str, project_id: str, role: SecurityRole, permissions: List[PermissionType], scope: AccessControlScope, **kwargs) -> CollaborationAccessControl:
        """
        Grant access permissions to a user for a project/resource.
        
        Args:
            granter_id: User granting the access
            user_id: User receiving access
            project_id: Project ID
            role: Security role
            permissions: List of permissions
            scope: Access scope
            **kwargs: Additional access control parameters
            
        Returns:
            Created access control record
        """



        try:
            # Validate granter has permission to grant access
            granter_context = SecurityContext(
                user_id=granter_id,
                session_id=kwargs.get("session_id", ""),
                ip_address=kwargs.get("ip_address", ""),
                user_agent=kwargs.get("user_agent", ""),
                project_id=project_id
            )
            
            if not await self.validate_access(granter_context, PermissionType.MANAGE_PERMISSIONS, scope):
                raise PermissionError("Insufficient permissions to grant access")
            
            # Create access control record
            access_control = CollaborationAccessControl(
                project_id=project_id,
                user_id=user_id,
                role=role,
                permissions=permissions,
                scope=scope,
                granted_by=granter_id,
                resource_id=kwargs.get("resource_id"),
                resource_type=kwargs.get("resource_type"),
                ip_restrictions=kwargs.get("ip_restrictions"),
                time_restrictions=kwargs.get("time_restrictions"),
                device_restrictions=kwargs.get("device_restrictions"),
                location_restrictions=kwargs.get("location_restrictions"),
                expires_at=kwargs.get("expires_at"),
                is_temporary=kwargs.get("is_temporary", False),
                requires_approval=kwargs.get("requires_approval", False),
                can_delegate=kwargs.get("can_delegate", False),
                metadata=kwargs.get("metadata", {})
            )
            
            self.db_session.add(access_control)
            self.db_session.commit()
            
            # Log access grant
            await self._log_security_event(
                SecurityEventType.PERMISSION_GRANTED,
                granter_context,
                {
                    "granted_to": user_id,
                    "role": role.value,
                    "permissions": [p.value for p in permissions],
                    "scope": scope.value
                }
            )
            
            self.logger.info(f"Access granted: {user_id} -> {project_id}")
            return access_control
            
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error granting access: {str(e)}")
            raise
    
    async def revoke_access(self, revoker_id: str, access_control_id: str, reason: str) -> bool:
        """
        Revoke access permissions.
        
        Args:
            revoker_id: User revoking the access
            access_control_id: Access control record ID
            reason: Reason for revocation
            
        Returns:
            True if revocation successful
        """



        try:
            # Get access control record
            access_control = self.db_session.query(CollaborationAccessControl).filter(
                CollaborationAccessControl.id == access_control_id
            ).first()
            
            if not access_control:
                raise ValueError(f"Access control record not found: {access_control_id}")
            
            # Validate revoker has permission
            revoker_context = SecurityContext(
                user_id=revoker_id,
                session_id="",
                ip_address="",
                user_agent="",
                project_id=access_control.project_id
            )
            
            if not await self.validate_access(revoker_context, PermissionType.MANAGE_PERMISSIONS, access_control.scope):
                raise PermissionError("Insufficient permissions to revoke access")
            
            # Revoke access
            access_control.is_active = False
            access_control.is_suspended = True
            access_control.suspension_reason = reason
            access_control.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            # Log access revocation
            await self._log_security_event(
                SecurityEventType.PERMISSION_DENIED,
                revoker_context,
                {
                    "revoked_from": access_control.user_id,
                    "reason": reason,
                    "access_control_id": access_control_id
                }
            )
            
            return True
            
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error revoking access: {str(e)}")
            raise
    
    async def detect_threats(self, context: SecurityContext) -> Optional[ThreatDetection]:
        """
        Real-time threat detection based on behavioral analysis.
        
        Args:
            context: Security context
            
        Returns:
            Threat detection record if threat detected
        """



        try:
            # Calculate risk score
            risk_score = await self._calculate_risk_score(context)
            
            # Check for known attack patterns
            attack_patterns = await self._check_attack_patterns(context)
            
            # Behavioral analysis
            behavioral_anomalies = await self._detect_behavioral_anomalies(context)
            
            # Determine threat level
            threat_level = self._determine_threat_level(risk_score, attack_patterns, behavioral_anomalies)
            
            if threat_level == ThreatLevel.INFO:
                return None  # No threat detected
            
            # Create threat detection record
            threat = ThreatDetection(
                threat_id=f"THREAT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}",
                threat_type=self._classify_threat_type(attack_patterns, behavioral_anomalies),
                threat_level=threat_level,
                threat_score=risk_score,
                detection_method="behavioral_analysis",
                confidence_score=self._calculate_detection_confidence(risk_score, attack_patterns),
                source_ip=context.ip_address,
                user_id=context.user_id,
                session_id=context.session_id,
                project_id=context.project_id,
                attack_vector=attack_patterns.get("primary_vector", "unknown"),
                indicators_of_compromise={"risk_score": risk_score, "patterns": attack_patterns},
                behavioral_anomalies=behavioral_anomalies,
                auto_response_taken=False
            )
            
            self.db_session.add(threat)
            self.db_session.commit()
            
            # Auto-response for high/critical threats
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._execute_auto_response(threat.id)
            
            return threat
            
        except Exception as e:
            self.logger.error(f"Error in threat detection: {str(e)}")
            raise
    
    async def encrypt_sensitive_data(self, data: str, project_id: str, purpose: str = "content_encryption") -> Dict[str, str]:
        """
        Encrypt sensitive data using project-specific encryption keys.
        
        Args:
            data: Data to encrypt
            project_id: Project ID
            purpose: Encryption purpose
            
        Returns:
            Encryption result with encrypted data and key information
        """



        try:
            # Get or create encryption key
            key_record = await self._get_or_create_encryption_key(project_id, purpose)
            
            # Decrypt the key material
            encryption_key = await self._decrypt_key_material(key_record.encrypted_key_material)
            
            # Initialize Fernet with the key
            fernet = Fernet(encryption_key)
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(data.encode())
            
            # Update key usage
            key_record.usage_count += 1
            key_record.last_used_at = datetime.utcnow()
            self.db_session.commit()
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "key_id": key_record.key_id,
                "algorithm": key_record.key_algorithm,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    async def decrypt_sensitive_data(self, encrypted_data: str, key_id: str, context: SecurityContext) -> str:
        """
        Decrypt sensitive data with access validation.
        
        Args:
            encrypted_data: Encrypted data
            key_id: Encryption key ID
            context: Security context
            
        Returns:
            Decrypted data
        """



        try:
            # Get encryption key
            key_record = self.db_session.query(EncryptionKey).filter(
                EncryptionKey.key_id == key_id,
                EncryptionKey.status == "active"
            ).first()
            
            if not key_record:
                raise ValueError(f"Encryption key not found or inactive: {key_id}")
            
            # Validate access to the key
            if not await self._validate_key_access(key_record, context):
                raise PermissionError("Insufficient permissions to access encryption key")
            
            # Decrypt the key material
            encryption_key = await self._decrypt_key_material(key_record.encrypted_key_material)
            
            # Initialize Fernet with the key
            fernet = Fernet(encryption_key)
            
            # Decrypt the data
            decrypted_data = fernet.decrypt(base64.b64decode(encrypted_data.encode()))
            
            # Update key usage and log access
            key_record.usage_count += 1
            key_record.last_used_at = datetime.utcnow()
            
            await self._log_security_event(
                SecurityEventType.CONTENT_ACCESS,
                context,
                {"key_id": key_id, "operation": "decrypt"}
            )
            
            self.db_session.commit()
            
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    async def generate_security_report(self, project_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive security report for a project.
        
        Args:
            project_id: Project ID
            timeframe_days: Report timeframe
            
        Returns:
            Security report data
        """



        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=timeframe_days)
            
            # Get audit logs
            audit_logs = self.db_session.query(SecurityAuditLog).filter(
                SecurityAuditLog.project_id == project_id,
                SecurityAuditLog.event_timestamp >= start_date
            ).all()
            
            # Get threat detections
            threats = self.db_session.query(ThreatDetection).filter(
                ThreatDetection.project_id == project_id,
                ThreatDetection.first_detected_at >= start_date
            ).all()
            
            # Get access controls
            access_controls = self.db_session.query(CollaborationAccessControl).filter(
                CollaborationAccessControl.project_id == project_id
            ).all()
            
            # Generate report
            report = {
                "project_id": project_id,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": timeframe_days
                },
                "security_overview": {
                    "total_security_events": len(audit_logs),
                    "successful_accesses": len([log for log in audit_logs if log.success]),
                    "failed_accesses": len([log for log in audit_logs if not log.success]),
                    "threats_detected": len(threats),
                    "high_severity_threats": len([t for t in threats if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]),
                    "active_access_controls": len([ac for ac in access_controls if ac.is_active])
                },
                "threat_analysis": self._analyze_threats(threats),
                "access_patterns": self._analyze_access_patterns(audit_logs),
                "security_metrics": self._calculate_security_metrics(audit_logs, threats),
                "compliance_status": await self._assess_compliance(project_id),
                "recommendations": await self._generate_security_recommendations(project_id, audit_logs, threats)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating security report: {str(e)}")
            raise
    
    def _initialize_encryption(self):
        """Initialize encryption components"""



        try:
            # This would typically use a master key from a secure key management service
            # For demo purposes, we'll generate a key (in production, use proper KMS)
            master_key = Fernet.generate_key()
            self.fernet = Fernet(master_key)
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {str(e)}")
            raise
    
    async def _check_access(self, context: SecurityContext, required_permission: PermissionType, scope: AccessControlScope) -> bool:
        """Check basic access control"""



        try:
            access_controls = self.db_session.query(CollaborationAccessControl).filter(
                CollaborationAccessControl.user_id == context.user_id,
                CollaborationAccessControl.project_id == context.project_id,
                CollaborationAccessControl.scope == scope,
                CollaborationAccessControl.is_active == True,
                CollaborationAccessControl.is_suspended == False
            ).all()
            
            for access_control in access_controls:
                # Check expiration
                if access_control.expires_at and access_control.expires_at <= datetime.utcnow():
                    continue
                
                # Check permissions
                if required_permission in access_control.permissions:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking access: {str(e)}")
            return False
    
    async def _calculate_risk_score(self, context: SecurityContext) -> float:
        """Calculate risk score based on various factors"""



        try:
            risk_score = 0.0
            
            # IP reputation check
            ip_risk = await self._check_ip_reputation(context.ip_address)
            risk_score += ip_risk * 0.3
            
            # Unusual access patterns
            access_pattern_risk = await self._check_access_patterns(context)
            risk_score += access_pattern_risk * 0.2
            
            # Device fingerprinting
            device_risk = await self._check_device_risk(context)
            risk_score += device_risk * 0.2
            
            # Time-based analysis
            time_risk = await self._check_time_based_risk(context)
            risk_score += time_risk * 0.1
            
            # Session analysis
            session_risk = await self._check_session_risk(context)
            risk_score += session_risk * 0.2
            
            return min(100.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {str(e)}")
            return 50.0  # Default medium risk
    
    async def _log_security_event(self, event_type: SecurityEventType, context: SecurityContext, event_data: Dict[str, Any]):
        """Log security event for audit trail"""



        try:
            audit_log = SecurityAuditLog(
                event_type=event_type,
                event_id=f"{event_type.value}_{secrets.token_hex(8)}",
                session_id=context.session_id,
                user_id=context.user_id,
                project_id=context.project_id,
                resource_id=context.resource_id,
                action_performed=context.action,
                ip_address=context.ip_address,
                user_agent=context.user_agent,
                mfa_verified=context.mfa_verified,
                event_data=event_data,
                success=True  # Will be set based on the actual outcome
            )
            
            self.db_session.add(audit_log)
            self.db_session.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {str(e)}")

# Additional helper methods would be implemented here for IP checking, device fingerprinting, behavioral analysis, etc.
