"""🔒 Security Compliance Database Module - Enterprise Security & Regulatory Compliance
========================================================================================
Module: backend/database/security_compliance.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Consolidated Security Compliance Database - Ultra Enterprise Production-Ready
Responsibility: Encryption management, GDPR/CCPA compliance, audit trails, access control, and security incidents
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class ComplianceStandard(Enum):
    """ComplianceStandard class implementation"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"

class SecurityEventType(Enum):
    """SecurityEventType class implementation"""
    LOGIN_ATTEMPT = "login_attempt"
    DATA_ACCESS = "data_access"
    PERMISSION_CHANGE = "permission_change"
    SECURITY_BREACH = "security_breach"

class EncryptionKeyManagement(Base):
    """Enterprise encryption key management."""
    __tablename__ = 'encryption_key_management'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_id = Column(String(255), nullable=False, unique=True)
    key_type = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False)
    key_size_bits = Column(Integer, nullable=False)
    key_purpose = Column(String(100), nullable=False)
    status = Column(String(50), default='active')
    encrypted_key_data = Column(Text, nullable=False)
    key_derivation_info = Column(JSONB, default={})
    rotation_schedule_days = Column(Integer, default=90)
    last_rotation_at = Column(DateTime(timezone=True), nullable=True)
    next_rotation_due = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)

class ComplianceRecord(Base):
    """GDPR/CCPA compliance tracking."""
    __tablename__ = 'compliance_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    compliance_standard = Column(SQLEnum(ComplianceStandard), nullable=False)
    compliance_status = Column(String(50), default='compliant')
    consent_records = Column(JSONB, default={})
    data_processing_purposes = Column(JSONB, default=[])
    data_retention_policy = Column(JSONB, default={})
    data_subject_rights = Column(JSONB, default={})
    privacy_settings = Column(JSONB, default={})
    consent_given_at = Column(DateTime(timezone=True), nullable=True)
    consent_withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    last_privacy_review = Column(DateTime(timezone=True), nullable=True)
    data_deletion_scheduled = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditTrail(Base):
    """Comprehensive audit trail system."""
    __tablename__ = 'audit_trails'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    session_id = Column(String(255), nullable=True)
    action_type = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    action_description = Column(Text, nullable=False)
    action_result = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_details = Column(JSONB, default={})
    response_details = Column(JSONB, default={})
    security_context = Column(JSONB, default={})
    risk_score = Column(Float, nullable=True)
    geolocation = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AccessControlMatrix(Base):
    """Granular access control management."""
    __tablename__ = 'access_control_matrix'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    permission_type = Column(String(100), nullable=False)
    access_level = Column(String(50), nullable=False)
    granted_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    grant_reason = Column(Text, nullable=True)
    conditions = Column(JSONB, default={})
    time_restrictions = Column(JSONB, default={})
    ip_restrictions = Column(ARRAY(String), default=[])
    device_restrictions = Column(ARRAY(String), default=[])
    status = Column(String(50), default='active')
    granted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

class SecurityIncident(Base):
    """Security incident management."""
    __tablename__ = 'security_incidents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_type = Column(SQLEnum(SecurityEventType), nullable=False)
    severity_level = Column(Integer, nullable=False)  # 1-5
    status = Column(String(50), default='open')
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    affected_users = Column(ARRAY(UUID), default=[])
    affected_systems = Column(ARRAY(String), default=[])
    attack_vector = Column(String(100), nullable=True)
    impact_assessment = Column(JSONB, default={})
    mitigation_steps = Column(JSONB, default=[])
    evidence_collected = Column(JSONB, default={})
    investigation_notes = Column(Text, nullable=True)
    assigned_to_user_id = Column(UUID(as_uuid=True), nullable=True)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    reported_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
class DataAnonymization(Base):
    """Data anonymization tracking."""
    __tablename__ = 'data_anonymization'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    anonymized_user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    anonymization_method = Column(String(100), nullable=False)
    anonymization_level = Column(String(50), nullable=False)
    data_categories_anonymized = Column(ARRAY(String), default=[])
    reversibility_key_id = Column(String(255), nullable=True)
    retention_period_days = Column(Integer, nullable=True)
    anonymization_metadata = Column(JSONB, default={})
    anonymized_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)

def get_security_compliance_models() -> None:
    return [EncryptionKeyManagement, ComplianceRecord, AuditTrail, AccessControlMatrix, SecurityIncident, DataAnonymization]

def create_security_compliance_tables(engine) -> None:
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_security_compliance_models()])
        logger.info("Successfully created security compliance tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create security compliance tables: {str(e)}")
        return False

__all__ = ['ComplianceStandard', 'SecurityEventType', 'EncryptionKeyManagement', 'ComplianceRecord', 'AuditTrail', 'AccessControlMatrix', 'SecurityIncident', 'DataAnonymization', 'get_security_compliance_models', 'create_security_compliance_tables']