"""Audit and Compliance Tracking Schemas

Comprehensive Pydantic schemas for audit trails, compliance monitoring,
and regulatory compliance in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.

⚠️ COPYRIGHT WARNING ⚠️
ALL RIGHTS RESERVED - This code, concept, and implementation are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Unauthorized use, copying, 
modification, or distribution is strictly prohibited and will result in immediate 
legal action under German and international copyright law.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class AuditEventTypeEnum(str, Enum):
    """Types of audit events"""    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DELETE = "content_delete"
    PROTECTION_ALERT = "protection_alert"
    PAYMENT_PROCESSED = "payment_processed"
    LICENSE_CREATED = "license_created"
    COLLABORATION_STARTED = "collaboration_started"
    SECURITY_INCIDENT = "security_incident"
    DATA_EXPORT = "data_export"
    SETTINGS_CHANGED = "settings_changed"
    API_ACCESS = "api_access"
    ADMIN_ACTION = "admin_action"
    COMPLIANCE_REVIEW = "compliance_review"
    VIOLATION_DETECTED = "violation_detected"
    SYSTEM_ACCESS = "system_access"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONTENT_MODIFICATION = "content_modification"


class ComplianceFrameworkEnum(str, Enum):
    """Compliance frameworks"""    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    DMCA = "dmca"
    COPPA = "coppa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    PDPA = "pdpa"
    COPYRIGHT_LAW = "copyright_law"
    TRADEMARK_LAW = "trademark_law"
    EU_AI_ACT = "eu_ai_act"
    MUSIC_LICENSE = "music_license"


class ComplianceStatusEnum(str, Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    EXEMPTED = "exempted"
    PENDING_ASSESSMENT = "pending_assessment"
    EXPIRED = "expired"


class RiskLevelEnum(str, Enum):
    """Risk assessment levels"""    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class DataCategoryEnum(str, Enum):
    """Data categories for privacy compliance"""    PERSONAL_IDENTITY = "personal_identity"
    FINANCIAL_DATA = "financial_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_DATA = "behavioral_data"
    COMMUNICATION_DATA = "communication_data"
    CONTENT_DATA = "content_data"
    METADATA = "metadata"
    USAGE_ANALYTICS = "usage_analytics"
    DEVICE_INFORMATION = "device_information"
    PREFERENCE_DATA = "preference_data"
    AUTHENTICATION_DATA = "authentication_data"


class AuditTrailSchema(BaseModel):
    """Schema for comprehensive audit trail entries"""    audit_id: str = Field(..., description="Unique audit identifier")
    event_type: AuditEventTypeEnum = Field(..., description="Type of audited event")
    user_id: Optional[PositiveInt] = Field(None, description="User who performed the action")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Event details
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="Identifier of affected resource")
    action_performed: str = Field(..., description="Specific action performed")
    action_result: str = Field(..., description="Result of the action")
    
    # Context information
    timestamp: datetime = Field(..., description="Event timestamp")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    geolocation: Optional[Dict[str, Any]] = Field(None, description="Geographic location")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint")
    
    # Data changes
    old_values: Optional[Dict[str, Any]] = Field(None, description="Values before change")
    new_values: Optional[Dict[str, Any]] = Field(None, description="Values after change")
    sensitive_data_accessed: Optional[List[DataCategoryEnum]] = Field(None, description="Sensitive data categories accessed")
    
    # Risk and compliance
    risk_level: RiskLevelEnum = Field(..., description="Risk level of the event")
    compliance_frameworks: Optional[List[ComplianceFrameworkEnum]] = Field(None, description="Relevant compliance frameworks")
    privacy_impact: bool = Field(False, description="Whether event has privacy implications")
    
    # Technical details
    request_method: Optional[str] = Field(None, description="HTTP request method")
    request_url: Optional[str] = Field(None, description="Request URL")
    response_code: Optional[int] = Field(None, description="HTTP response code")
    processing_time: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    # Additional metadata
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for related events")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "AUD-2024-001234",
                "event_type": "content_upload",
                "user_id": 123,
                "resource_type": "content_fingerprint",
                "action_performed": "create_fingerprint",
                "action_result": "success",
                "ip_address": "192.168.1.100",
                "risk_level": "low",
                "privacy_impact": True
            }
        }


class ComplianceAssessmentSchema(BaseModel):
    """Schema for compliance assessments"""    assessment_id: str = Field(..., description="Unique assessment identifier")
    framework: ComplianceFrameworkEnum = Field(..., description="Compliance framework")
    user_id: Optional[PositiveInt] = Field(None, description="User being assessed")
    resource_type: Optional[str] = Field(None, description="Resource type being assessed")
    
    # Assessment details
    assessment_date: datetime = Field(..., description="Assessment date")
    assessor_id: PositiveInt = Field(..., description="ID of person conducting assessment")
    assessment_scope: str = Field(..., description="Scope of the assessment")
    methodology: str = Field(..., description="Assessment methodology used")
    
    # Results
    overall_status: ComplianceStatusEnum = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    findings: List[Dict[str, Any]] = Field(..., description="Detailed findings")
    non_compliance_areas: Optional[List[str]] = Field(None, description="Areas of non-compliance")
    
    # Risk assessment
    risk_level: RiskLevelEnum = Field(..., description="Overall risk level")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    mitigation_requirements: List[str] = Field(..., description="Required mitigations")
    
    # Timeline and actions
    remediation_deadline: Optional[date] = Field(None, description="Deadline for remediation")
    next_assessment_date: Optional[date] = Field(None, description="Next scheduled assessment")
    action_items: List[Dict[str, Any]] = Field([], description="Required action items")
    
    # Documentation
    evidence_collected: List[str] = Field([], description="Evidence collected during assessment")
    documentation_urls: Optional[List[HttpUrl]] = Field(None, description="Supporting documentation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "COMP-2024-001234",
                "framework": "gdpr",
                "assessor_id": 456,
                "overall_status": "compliant",
                "compliance_score": 0.95,
                "risk_level": "low",
                "assessment_scope": "Data processing activities"
            }
        }


class PrivacyImpactAssessmentSchema(BaseModel):
    """Schema for Privacy Impact Assessments (PIA)"""    pia_id: str = Field(..., description="Unique PIA identifier")
    project_name: str = Field(..., description="Name of project being assessed")
    project_description: str = Field(..., description="Description of the project")
    
    # Assessment details
    assessment_date: datetime = Field(..., description="Assessment date")
    assessor_id: PositiveInt = Field(..., description="Assessor ID")
    review_board: Optional[List[str]] = Field(None, description="Review board members")
    
    # Data processing details
    data_categories: List[DataCategoryEnum] = Field(..., description="Categories of data processed")
    data_subjects: List[str] = Field(..., description="Types of data subjects")
    processing_purposes: List[str] = Field(..., description="Purposes of data processing")
    data_sources: List[str] = Field(..., description="Sources of data")
    data_recipients: List[str] = Field(..., description="Recipients of data")
    
    # Risk assessment
    privacy_risks: List[Dict[str, Any]] = Field(..., description="Identified privacy risks")
    risk_mitigation_measures: List[Dict[str, Any]] = Field(..., description="Risk mitigation measures")
    residual_risk_level: RiskLevelEnum = Field(..., description="Residual risk level after mitigation")
    
    # Legal basis and compliance
    legal_basis: List[str] = Field(..., description="Legal basis for processing")
    compliance_frameworks: List[ComplianceFrameworkEnum] = Field(..., description="Applicable frameworks")
    data_retention_period: Optional[int] = Field(None, description="Data retention period in days")
    
    # Approval and monitoring
    approval_status: str = Field(..., description="Approval status of the PIA")
    approval_date: Optional[datetime] = Field(None, description="Date of approval")
    monitoring_requirements: List[str] = Field([], description="Monitoring requirements")
    review_schedule: Optional[str] = Field(None, description="Review schedule")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pia_id": "PIA-2024-001234",
                "project_name": "AI Content Analysis",
                "data_categories": ["content_data", "behavioral_data"],
                "processing_purposes": ["content_protection", "analytics"],
                "residual_risk_level": "low",
                "approval_status": "approved"
            }
        }


class DataSubjectRequestSchema(BaseModel):
    """Schema for data subject requests (GDPR Article 15-22)"""    request_id: str = Field(..., description="Unique request identifier")
    request_type: str = Field(..., description="Type of request (access, rectification, erasure, etc.)")
    requester_email: str = Field(..., description="Email of the data subject")
    requester_name: Optional[str] = Field(None, description="Name of the data subject")
    
    # Request details
    request_date: datetime = Field(..., description="Date request was received")
    request_description: str = Field(..., description="Description of the request")
    affected_data_categories: List[DataCategoryEnum] = Field(..., description="Data categories affected")
    
    # Processing information
    status: str = Field(..., description="Current status of the request")
    assigned_to: Optional[PositiveInt] = Field(None, description="Assigned processor ID")
    verification_method: Optional[str] = Field(None, description="Method used to verify identity")
    verification_completed: bool = Field(False, description="Whether identity verification completed")
    
    # Response details
    response_deadline: date = Field(..., description="Legal deadline for response")
    response_date: Optional[datetime] = Field(None, description="Date response was sent")
    response_method: Optional[str] = Field(None, description="Method of response delivery")
    
    # Actions taken
    data_provided: Optional[Dict[str, Any]] = Field(None, description="Data provided to subject")
    data_rectified: Optional[Dict[str, Any]] = Field(None, description="Data that was rectified")
    data_erased: Optional[List[str]] = Field(None, description="Data that was erased")
    processing_restricted: Optional[List[str]] = Field(None, description="Processing that was restricted")
    
    # Compliance tracking
    complexity_assessment: str = Field(..., description="Complexity assessment of request")
    legal_basis_review: Optional[str] = Field(None, description="Legal basis review notes")
    third_party_notifications: Optional[List[str]] = Field(None, description="Third parties notified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "DSR-2024-001234",
                "request_type": "access_request",
                "requester_email": "user@example.com",
                "status": "processing",
                "response_deadline": "2024-09-23",
                "complexity_assessment": "simple"
            }
        }


class ComplianceReportSchema(BaseModel):
    """Schema for compliance reporting"""    report_id: str = Field(..., description="Unique report identifier")
    report_type: str = Field(..., description="Type of compliance report")
    reporting_period_start: date = Field(..., description="Start of reporting period")
    reporting_period_end: date = Field(..., description="End of reporting period")
    
    # Report metadata
    generated_date: datetime = Field(..., description="Report generation date")
    generated_by: PositiveInt = Field(..., description="User who generated the report")
    frameworks_covered: List[ComplianceFrameworkEnum] = Field(..., description="Frameworks covered")
    
    # Compliance metrics
    overall_compliance_score: float = Field(..., ge=0.0, le=1.0, description="Overall compliance score")
    framework_scores: Dict[str, float] = Field(..., description="Scores by framework")
    compliance_trends: List[Dict[str, Any]] = Field(..., description="Compliance trends over time")
    
    # Incident reporting
    security_incidents: int = Field(0, description="Number of security incidents")
    data_breaches: int = Field(0, description="Number of data breaches")
    privacy_violations: int = Field(0, description="Number of privacy violations")
    compliance_violations: int = Field(0, description="Number of compliance violations")
    
    # Data subject requests
    data_subject_requests: Dict[str, int] = Field(..., description="Data subject requests by type")
    average_response_time: float = Field(..., description="Average response time in hours")
    requests_within_deadline: float = Field(..., description="Percentage of requests completed on time")
    
    # Risk assessment
    high_risk_areas: List[str] = Field([], description="Areas identified as high risk")
    risk_mitigation_progress: Dict[str, float] = Field(..., description="Risk mitigation progress")
    outstanding_issues: List[Dict[str, Any]] = Field([], description="Outstanding compliance issues")
    
    # Recommendations
    recommendations: List[str] = Field([], description="Compliance recommendations")
    action_plan: List[Dict[str, Any]] = Field([], description="Action plan for improvements")
    next_review_date: Optional[date] = Field(None, description="Next scheduled review")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "REP-2024-Q3",
                "report_type": "quarterly_compliance",
                "overall_compliance_score": 0.92,
                "security_incidents": 0,
                "data_breaches": 0,
                "frameworks_covered": ["gdpr", "ccpa"]
            }
        }


class RetentionPolicySchema(BaseModel):
    """Schema for data retention policies"""    policy_id: str = Field(..., description="Unique policy identifier")
    policy_name: str = Field(..., description="Name of the retention policy")
    data_category: DataCategoryEnum = Field(..., description="Category of data covered")
    
    # Retention rules
    retention_period_days: PositiveInt = Field(..., description="Retention period in days")
    retention_basis: str = Field(..., description="Legal/business basis for retention")
    disposal_method: str = Field(..., description="Method of data disposal")
    
    # Scope and application
    applicable_users: Optional[List[str]] = Field(None, description="User categories affected")
    applicable_regions: Optional[List[str]] = Field(None, description="Geographic regions")
    exceptions: Optional[List[str]] = Field(None, description="Exceptions to the policy")
    
    # Compliance and legal
    legal_requirements: List[str] = Field(..., description="Legal requirements driving retention")
    compliance_frameworks: List[ComplianceFrameworkEnum] = Field(..., description="Applicable frameworks")
    
    # Policy management
    effective_date: date = Field(..., description="Policy effective date")
    expiry_date: Optional[date] = Field(None, description="Policy expiry date")
    review_frequency: int = Field(..., description="Review frequency in months")
    last_reviewed: Optional[date] = Field(None, description="Last review date")
    next_review: Optional[date] = Field(None, description="Next review date")
    
    # Implementation
    automated_enforcement: bool = Field(False, description="Whether enforcement is automated")
    monitoring_enabled: bool = Field(True, description="Whether monitoring is enabled")
    notification_before_disposal: bool = Field(True, description="Whether to notify before disposal")
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "RET-001",
                "policy_name": "User Content Retention",
                "data_category": "content_data",
                "retention_period_days": 2555,  # 7 years
                "retention_basis": "legal_requirement",
                "disposal_method": "secure_deletion"
            }
        }


# Export schemas
__all__ = [
    # Enums
    "AuditEventTypeEnum",
    "ComplianceFrameworkEnum",
    "ComplianceStatusEnum",
    "RiskLevelEnum",
    "DataCategoryEnum",
    
    # Main schemas
    "AuditTrailSchema",
    "ComplianceAssessmentSchema",
    "PrivacyImpactAssessmentSchema",
    "DataSubjectRequestSchema",
    "ComplianceReportSchema",
    "RetentionPolicySchema"
]
