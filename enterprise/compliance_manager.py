"""Compliance Management System
============================

Advanced compliance and regulatory management system supporting GDPR, CCPA,
PCI-DSS, HIPAA, SOX, and other regulatory frameworks with automated auditing,
data governance, risk assessment, and comprehensive compliance reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""
import asyncio
import logging
import json
import uuid
import hashlib
import time
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import pandas as pd
import aiofiles
import aioredis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOX = "sox"  # Sarbanes-Oxley Act
    ISO_27001 = "iso_27001"  # Information Security Management
    NIST = "nist"  # National Institute of Standards and Technology
    FISMA = "fisma"  # Federal Information Security Management Act
    FEDRAMP = "fedramp"  # Federal Risk and Authorization Management Program
    SOC2 = "soc2"  # Service Organization Control 2
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)


class ComplianceStatus(Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataCategory(Enum):
    """Data categorization for privacy compliance"""    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_DATA = "behavioral_data"
    PUBLIC_DATA = "public_data"


class ConsentType(Enum):
    """Types of data processing consent"""    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONTRACTUAL = "contractual"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"


class AuditEventType(Enum):
    """Types of audit events"""    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"
    DATA_SHARING = "data_sharing"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    SECURITY_INCIDENT = "security_incident"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_ACCESS = "system_access"
    ADMIN_ACTION = "admin_action"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    requirement_text: str
    implementation_guidance: str
    validation_criteria: List[str]
    risk_level: RiskLevel
    applicable_data_types: List[DataCategory]
    automated_check: bool = False
    check_frequency: str = "daily"  # daily, weekly, monthly, quarterly
    remediation_steps: List[str] = field(default_factory=list)
    related_rules: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""    assessment_id: str
    framework: ComplianceFramework
    organization_id: str
    overall_status: ComplianceStatus
    score: float  # 0-100 percentage
    rule_assessments: Dict[str, Dict[str, Any]]
    gaps_identified: List[Dict[str, Any]]
    recommendations: List[str]
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessor: str = ""
    next_assessment_due: Optional[datetime] = None
    evidence_collected: List[Dict[str, Any]] = field(default_factory=list)
    remediation_plan: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DataProcessingRecord:
    """Record of data processing activities (GDPR Article 30)"""    record_id: str
    organization_id: str
    processing_purpose: str
    data_categories: List[DataCategory]
    data_subjects: List[str]
    recipients: List[str]
    international_transfers: List[Dict[str, Any]]
    retention_period: str
    security_measures: List[str]
    legal_basis: List[ConsentType]
    controller_details: Dict[str, str]
    processor_details: Optional[Dict[str, str]] = None
    dpo_contact: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConsentRecord:
    """Individual consent record"""    consent_id: str
    user_id: str
    organization_id: str
    consent_type: ConsentType
    purpose: str
    data_categories: List[DataCategory]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    consent_text: str = ""
    version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class AuditEvent:
    """Audit trail event"""    event_id: str
    event_type: AuditEventType
    user_id: str
    organization_id: str
    resource_id: Optional[str]
    resource_type: Optional[str]
    timestamp: datetime
    ip_address: str
    user_agent: str
    action_details: Dict[str, Any]
    compliance_relevant: bool = True
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'action_details': self.action_details,
            'compliance_relevant': self.compliance_relevant,
            'risk_score': self.risk_score,
            'metadata': self.metadata
        }


class DataClassifier:
    """Advanced data classification engine"""    
    def __init__(self):
        self._classification_patterns = {
            DataCategory.PERSONAL_DATA: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}-?\d{2}-?\d{4}\b',  # SSN
                r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            ],
            DataCategory.FINANCIAL_DATA: [
                r'\b4[0-9]{12}(?:[0-9]{3})?\b',  # Visa
                r'\b5[1-5][0-9]{14}\b',  # MasterCard
                r'\b3[47][0-9]{13}\b',  # American Express
                r'\b\d{10,12}\b',  # Bank account
            ],
            DataCategory.HEALTH_DATA: [
                r'\bmrn\s*:?\s*\d+\b',  # Medical Record Number
                r'\bpatient\s*id\s*:?\s*\d+\b',
                r'\bdiagnosis\b',
                r'\bmedication\b',
            ],
            DataCategory.LOCATION_DATA: [
                r'\b-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+\b',  # Coordinates
                r'\b\d{5}(-\d{4})?\b',  # ZIP codes
                r'\blatitude\b|\blongitude\b',
            ]
        }
    
    async def classify_data(self, data: Union[str, Dict[str, Any], List[Any]]) -> Dict[DataCategory, List[str]]:
        """Classify data and identify sensitive information"""        try:
            classifications = {category: [] for category in DataCategory}
            
            # Convert data to string for pattern matching
            if isinstance(data, dict):
                text_data = json.dumps(data, default=str)
            elif isinstance(data, list):
                text_data = ' '.join(str(item) for item in data)
            else:
                text_data = str(data)
            
            # Apply classification patterns
            for category, patterns in self._classification_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_data, re.IGNORECASE)
                    if matches:
                        classifications[category].extend(matches)
            
            # Remove empty categories
            return {k: v for k, v in classifications.items() if v}
            
        except Exception as e:
            logger.error(f"Data classification failed: {e}")
            return {}
    
    async def scan_database_schema(self, schema_info: Dict[str, Any]) -> Dict[str, List[DataCategory]]:
        """Scan database schema for sensitive data"""        try:
            table_classifications = {}
            
            for table_name, columns in schema_info.items():
                table_categories = []
                
                for column in columns:
                    column_name = column['name'].lower()
                    column_type = column.get('type', '').lower()
                    
                    # Check column names for sensitive data indicators
                    if any(indicator in column_name for indicator in ['email', 'mail']):
                        table_categories.append(DataCategory.PERSONAL_DATA)
                    elif any(indicator in column_name for indicator in ['phone', 'mobile', 'tel']):
                        table_categories.append(DataCategory.PERSONAL_DATA)
                    elif any(indicator in column_name for indicator in ['ssn', 'social', 'passport']):
                        table_categories.append(DataCategory.SENSITIVE_DATA)
                    elif any(indicator in column_name for indicator in ['credit', 'card', 'payment', 'bank']):
                        table_categories.append(DataCategory.FINANCIAL_DATA)
                    elif any(indicator in column_name for indicator in ['medical', 'health', 'diagnosis']):
                        table_categories.append(DataCategory.HEALTH_DATA)
                    elif any(indicator in column_name for indicator in ['lat', 'lng', 'location', 'address']):
                        table_categories.append(DataCategory.LOCATION_DATA)
                
                if table_categories:
                    table_classifications[table_name] = list(set(table_categories))
            
            return table_classifications
            
        except Exception as e:
            logger.error(f"Schema scanning failed: {e}")
            return {}


class ConsentManager:
    """Advanced consent management system"""    
    def __init__(self):
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._consent_history: Dict[str, List[ConsentRecord]] = {}
        
    async def record_consent(
        self,
        user_id: str,
        organization_id: str,
        consent_type: ConsentType,
        purpose: str,
        data_categories: List[DataCategory],
        consent_text: str,
        ip_address: str,
        user_agent: str,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Record user consent"""        try:
            consent_id = f"consent_{uuid.uuid4().hex[:12]}"
            
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                organization_id=organization_id,
                consent_type=consent_type,
                purpose=purpose,
                data_categories=data_categories,
                granted_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                consent_text=consent_text,
                ip_address=ip_address,
                user_agent=user_agent,
                evidence={
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'method': 'web_form',
                    'version': '1.0'
                }
            )
            
            # Store consent record
            self._consent_records[consent_id] = consent_record
            
            # Add to user's consent history
            if user_id not in self._consent_history:
                self._consent_history[user_id] = []
            self._consent_history[user_id].append(consent_record)
            
            logger.info(f"Recorded consent: {consent_id} for user: {user_id}")
            return consent_id
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise
    
    async def withdraw_consent(self, consent_id: str, user_id: str, reason: str = "") -> bool:
        """Withdraw user consent"""        try:
            if consent_id not in self._consent_records:
                raise ValueError(f"Consent record not found: {consent_id}")
            
            consent_record = self._consent_records[consent_id]
            
            # Verify user ownership
            if consent_record.user_id != user_id:
                raise ValueError("User not authorized to withdraw this consent")
            
            # Mark as withdrawn
            consent_record.withdrawn_at = datetime.now(timezone.utc)
            consent_record.is_active = False
            consent_record.evidence['withdrawal'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'reason': reason
            }
            
            logger.info(f"Withdrawn consent: {consent_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
    
    async def check_consent_validity(self, user_id: str, purpose: str, data_categories: List[DataCategory]) -> bool:
        """Check if user has valid consent for specified purpose and data categories"""        try:
            user_consents = self._consent_history.get(user_id, [])
            
            for consent in user_consents:
                if not consent.is_active:
                    continue
                
                # Check if consent covers the purpose
                if purpose not in consent.purpose:
                    continue
                
                # Check if consent covers all required data categories
                if not all(category in consent.data_categories for category in data_categories):
                    continue
                
                # Check if consent is still valid (not expired)
                if consent.expires_at and consent.expires_at < datetime.now(timezone.utc):
                    continue
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Consent validity check failed: {e}")
            return False
    
    async def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get all consents for a user"""        return self._consent_history.get(user_id, [])
    
    async def generate_consent_report(self, organization_id: str) -> Dict[str, Any]:
        """Generate consent compliance report"""        try:
            org_consents = [
                consent for consent_list in self._consent_history.values()
                for consent in consent_list
                if consent.organization_id == organization_id
            ]
            
            active_consents = [c for c in org_consents if c.is_active]
            withdrawn_consents = [c for c in org_consents if not c.is_active]
            expired_consents = [
                c for c in active_consents
                if c.expires_at and c.expires_at < datetime.now(timezone.utc)
            ]
            
            report = {
                'organization_id': organization_id,
                'total_consents': len(org_consents),
                'active_consents': len(active_consents),
                'withdrawn_consents': len(withdrawn_consents),
                'expired_consents': len(expired_consents),
                'consent_types': {},
                'data_categories': {},
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Analyze consent types
            for consent in org_consents:
                consent_type = consent.consent_type.value
                report['consent_types'][consent_type] = report['consent_types'].get(consent_type, 0) + 1
            
            # Analyze data categories
            for consent in org_consents:
                for category in consent.data_categories:
                    cat_name = category.value
                    report['data_categories'][cat_name] = report['data_categories'].get(cat_name, 0) + 1
            
            return report
            
        except Exception as e:
            logger.error(f"Consent report generation failed: {e}")
            return {}


class AuditTrail:
    """Comprehensive audit trail system"""    
    def __init__(self, storage_config: Dict[str, Any]):
        self.storage_config = storage_config
        self._audit_events: List[AuditEvent] = []
        self._redis: Optional[aioredis.Redis] = None
        
    async def initialize(self):
        """Initialize audit trail storage"""        try:
            if 'redis_url' in self.storage_config:
                self._redis = aioredis.from_url(self.storage_config['redis_url'])
                await self._redis.ping()
            
            logger.info("Audit trail system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize audit trail: {e}")
            raise
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        organization_id: str,
        action_details: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        risk_score: float = 0.0
    ) -> str:
        """Log audit event"""        try:
            event_id = f"audit_{uuid.uuid4().hex[:12]}"
            
            audit_event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                organization_id=organization_id,
                resource_id=resource_id,
                resource_type=resource_type,
                timestamp=datetime.now(timezone.utc),
                ip_address=ip_address,
                user_agent=user_agent,
                action_details=action_details,
                risk_score=risk_score,
                metadata={
                    'logged_at': datetime.now(timezone.utc).isoformat(),
                    'source': 'compliance_manager'
                }
            )
            
            # Store event
            self._audit_events.append(audit_event)
            
            # Store in Redis for real-time access
            if self._redis:
                key = f"audit_event:{event_id}"
                await self._redis.setex(key, 86400, json.dumps(audit_event.to_dict()))  # 24 hours TTL
                
                # Add to organization's audit log
                org_key = f"org_audit:{organization_id}"
                await self._redis.lpush(org_key, event_id)
                await self._redis.expire(org_key, 2592000)  # 30 days
            
            # Check for compliance violations
            await self._check_compliance_violations(audit_event)
            
            logger.info(f"Logged audit event: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            raise
    
    async def _check_compliance_violations(self, event: AuditEvent):
        """Check audit event for potential compliance violations"""        try:
            violations = []
            
            # Check for unusual access patterns
            if event.event_type == AuditEventType.DATA_ACCESS:
                # Check for access outside business hours
                access_time = event.timestamp.time()
                if access_time.hour < 6 or access_time.hour > 22:
                    violations.append({
                        'type': 'unusual_access_time',
                        'severity': 'medium',
                        'description': 'Data access outside normal business hours'
                    })
                
                # Check for bulk data access
                if event.action_details.get('records_accessed', 0) > 1000:
                    violations.append({
                        'type': 'bulk_data_access',
                        'severity': 'high',
                        'description': 'Large volume of data accessed'
                    })
            
            # Check for data deletion events
            if event.event_type == AuditEventType.DATA_DELETION:
                violations.append({
                    'type': 'data_deletion',
                    'severity': 'high',
                    'description': 'Data deletion event requires review'
                })
            
            # Log violations if found
            if violations:
                logger.warning(f"Compliance violations detected for event {event.event_id}: {violations}")
                
        except Exception as e:
            logger.error(f"Compliance violation check failed: {e}")
    
    async def query_events(
        self,
        organization_id: str,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events with filters"""        try:
            filtered_events = []
            
            for event in self._audit_events:
                # Filter by organization
                if event.organization_id != organization_id:
                    continue
                
                # Filter by event types
                if event_types and event.event_type not in event_types:
                    continue
                
                # Filter by user
                if user_id and event.user_id != user_id:
                    continue
                
                # Filter by time range
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                
                filtered_events.append(event)
                
                # Apply limit
                if len(filtered_events) >= limit:
                    break
            
            return filtered_events
            
        except Exception as e:
            logger.error(f"Audit event query failed: {e}")
            return []
    
    async def generate_audit_report(
        self,
        organization_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report"""        try:
            start_time, end_time = time_range
            events = await self.query_events(
                organization_id=organization_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
            
            # Analyze events
            event_types = {}
            user_activity = {}
            risk_events = []
            
            for event in events:
                # Count event types
                event_type = event.event_type.value
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # Count user activity
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
                
                # Identify high-risk events
                if event.risk_score > 7.0:
                    risk_events.append(event.to_dict())
            
            report = {
                'organization_id': organization_id,
                'report_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'total_events': len(events),
                'event_types': event_types,
                'user_activity': user_activity,
                'high_risk_events': len(risk_events),
                'risk_events_details': risk_events[:10],  # Top 10 risk events
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Audit report generation failed: {e}")
            return {}


class RegulatoryFramework:
    """Regulatory framework implementation"""    
    def __init__(self):
        self._compliance_rules: Dict[ComplianceFramework, List[ComplianceRule]] = {}
        self._initialize_frameworks()
    
    def _initialize_frameworks(self):
        """Initialize compliance frameworks with rules"""        # GDPR Rules
        self._compliance_rules[ComplianceFramework.GDPR] = [
            ComplianceRule(
                rule_id="gdpr_art_6",
                framework=ComplianceFramework.GDPR,
                title="Lawfulness of processing",
                description="Processing must have a lawful basis",
                requirement_text="Article 6 - Lawfulness of processing",
                implementation_guidance="Ensure valid legal basis for all data processing",
                validation_criteria=["Legal basis documented", "Consent obtained where required"],
                risk_level=RiskLevel.HIGH,
                applicable_data_types=[DataCategory.PERSONAL_DATA]
            ),
            ComplianceRule(
                rule_id="gdpr_art_7",
                framework=ComplianceFramework.GDPR,
                title="Conditions for consent",
                description="Consent must be freely given, specific, informed and unambiguous",
                requirement_text="Article 7 - Conditions for consent",
                implementation_guidance="Implement proper consent management",
                validation_criteria=["Consent is freely given", "Consent is specific", "Consent is informed"],
                risk_level=RiskLevel.HIGH,
                applicable_data_types=[DataCategory.PERSONAL_DATA]
            ),
            ComplianceRule(
                rule_id="gdpr_art_30",
                framework=ComplianceFramework.GDPR,
                title="Records of processing activities",
                description="Maintain records of processing activities",
                requirement_text="Article 30 - Records of processing activities",
                implementation_guidance="Maintain detailed records of all data processing",
                validation_criteria=["Processing records maintained", "Records are up to date"],
                risk_level=RiskLevel.MEDIUM,
                applicable_data_types=[DataCategory.PERSONAL_DATA]
            )
        ]
        
        # PCI DSS Rules
        self._compliance_rules[ComplianceFramework.PCI_DSS] = [
            ComplianceRule(
                rule_id="pci_req_1",
                framework=ComplianceFramework.PCI_DSS,
                title="Install and maintain firewall configuration",
                description="Protect cardholder data with firewall",
                requirement_text="Requirement 1: Install and maintain a firewall configuration",
                implementation_guidance="Configure and maintain network firewalls",
                validation_criteria=["Firewall configured", "Firewall rules documented"],
                risk_level=RiskLevel.HIGH,
                applicable_data_types=[DataCategory.FINANCIAL_DATA]
            ),
            ComplianceRule(
                rule_id="pci_req_3",
                framework=ComplianceFramework.PCI_DSS,
                title="Protect stored cardholder data",
                description="Encrypt cardholder data storage",
                requirement_text="Requirement 3: Protect stored cardholder data",
                implementation_guidance="Implement strong encryption for stored card data",
                validation_criteria=["Data encrypted at rest", "Encryption keys managed securely"],
                risk_level=RiskLevel.CRITICAL,
                applicable_data_types=[DataCategory.FINANCIAL_DATA]
            )
        ]
        
        # HIPAA Rules
        self._compliance_rules[ComplianceFramework.HIPAA] = [
            ComplianceRule(
                rule_id="hipaa_security_rule",
                framework=ComplianceFramework.HIPAA,
                title="Security Rule",
                description="Protect PHI with administrative, physical, and technical safeguards",
                requirement_text="HIPAA Security Rule - 45 CFR Part 164",
                implementation_guidance="Implement comprehensive security measures for PHI",
                validation_criteria=["Administrative safeguards", "Physical safeguards", "Technical safeguards"],
                risk_level=RiskLevel.HIGH,
                applicable_data_types=[DataCategory.HEALTH_DATA]
            )
        ]
    
    async def get_applicable_rules(
        self,
        frameworks: List[ComplianceFramework],
        data_categories: List[DataCategory]
    ) -> List[ComplianceRule]:
        """Get applicable compliance rules"""        try:
            applicable_rules = []
            
            for framework in frameworks:
                if framework in self._compliance_rules:
                    for rule in self._compliance_rules[framework]:
                        # Check if rule applies to any of the data categories
                        if any(category in rule.applicable_data_types for category in data_categories):
                            applicable_rules.append(rule)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Failed to get applicable rules: {e}")
            return []
    
    async def validate_rule_compliance(
        self,
        rule: ComplianceRule,
        organization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate compliance with specific rule"""        try:
            validation_result = {
                'rule_id': rule.rule_id,
                'status': ComplianceStatus.UNKNOWN,
                'score': 0.0,
                'findings': [],
                'evidence': [],
                'recommendations': []
            }
            
            # Perform rule-specific validation
            if rule.automated_check:
                validation_result = await self._automated_rule_check(rule, organization_data)
            else:
                validation_result['status'] = ComplianceStatus.UNDER_REVIEW
                validation_result['findings'].append("Manual review required")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            return {
                'rule_id': rule.rule_id,
                'status': ComplianceStatus.UNKNOWN,
                'error': str(e)
            }
    
    async def _automated_rule_check(self, rule: ComplianceRule, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated compliance check"""        try:
            # Simplified automated checks - in real implementation, these would be more comprehensive
            if rule.rule_id == "gdpr_art_30":
                # Check for processing records
                has_records = 'processing_records' in org_data
                status = ComplianceStatus.COMPLIANT if has_records else ComplianceStatus.NON_COMPLIANT
                score = 100.0 if has_records else 0.0
                
                return {
                    'rule_id': rule.rule_id,
                    'status': status,
                    'score': score,
                    'findings': ['Processing records found'] if has_records else ['No processing records found'],
                    'evidence': [org_data.get('processing_records', {})],
                    'recommendations': [] if has_records else ['Create and maintain processing records']
                }
            
            elif rule.rule_id == "pci_req_3":
                # Check for encryption
                has_encryption = org_data.get('encryption_enabled', False)
                status = ComplianceStatus.COMPLIANT if has_encryption else ComplianceStatus.NON_COMPLIANT
                score = 100.0 if has_encryption else 0.0
                
                return {
                    'rule_id': rule.rule_id,
                    'status': status,
                    'score': score,
                    'findings': ['Encryption enabled'] if has_encryption else ['Encryption not enabled'],
                    'evidence': [{'encryption_status': has_encryption}],
                    'recommendations': [] if has_encryption else ['Enable data encryption']
                }
            
            # Default response for unimplemented automated checks
            return {
                'rule_id': rule.rule_id,
                'status': ComplianceStatus.UNDER_REVIEW,
                'score': 50.0,
                'findings': ['Automated check not implemented'],
                'evidence': [],
                'recommendations': ['Implement manual review process']
            }
            
        except Exception as e:
            logger.error(f"Automated rule check failed: {e}")
            return {
                'rule_id': rule.rule_id,
                'status': ComplianceStatus.UNKNOWN,
                'error': str(e)
            }


class DataGovernance:
    """Data governance and lifecycle management"""    
    def __init__(self):
        self._data_inventory: Dict[str, Dict[str, Any]] = {}
        self._retention_policies: Dict[str, Dict[str, Any]] = {}
        self._data_lineage: Dict[str, List[str]] = {}
        
    async def register_data_asset(
        self,
        asset_id: str,
        asset_name: str,
        data_categories: List[DataCategory],
        owner: str,
        location: str,
        classification: str,
        retention_period: str,
        security_level: str
    ) -> bool:
        """Register data asset in inventory"""        try:
            self._data_inventory[asset_id] = {
                'asset_name': asset_name,
                'data_categories': [cat.value for cat in data_categories],
                'owner': owner,
                'location': location,
                'classification': classification,
                'retention_period': retention_period,
                'security_level': security_level,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_accessed': None,
                'access_count': 0
            }
            
            logger.info(f"Registered data asset: {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register data asset: {e}")
            return False
    
    async def create_retention_policy(
        self,
        policy_id: str,
        data_categories: List[DataCategory],
        retention_period: str,
        disposal_method: str,
        legal_basis: str
    ) -> bool:
        """Create data retention policy"""        try:
            self._retention_policies[policy_id] = {
                'data_categories': [cat.value for cat in data_categories],
                'retention_period': retention_period,
                'disposal_method': disposal_method,
                'legal_basis': legal_basis,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'active': True
            }
            
            logger.info(f"Created retention policy: {policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create retention policy: {e}")
            return False
    
    async def identify_expired_data(self) -> List[Dict[str, Any]]:
        """Identify data that has exceeded retention period"""        try:
            expired_data = []
            current_time = datetime.now(timezone.utc)
            
            for asset_id, asset_info in self._data_inventory.items():
                retention_period = asset_info['retention_period']
                created_at = datetime.fromisoformat(asset_info['created_at'])
                
                # Parse retention period (simplified - assumes format like "365d", "2y")
                if retention_period.endswith('d'):
                    retention_days = int(retention_period[:-1])
                elif retention_period.endswith('y'):
                    retention_days = int(retention_period[:-1]) * 365
                else:
                    continue  # Skip invalid formats
                
                expiry_date = created_at + timedelta(days=retention_days)
                
                if current_time > expiry_date:
                    expired_data.append({
                        'asset_id': asset_id,
                        'asset_name': asset_info['asset_name'],
                        'expired_since': (current_time - expiry_date).days,
                        'retention_period': retention_period,
                        'location': asset_info['location']
                    })
            
            return expired_data
            
        except Exception as e:
            logger.error(f"Failed to identify expired data: {e}")
            return []
    
    async def generate_data_map(self, organization_id: str) -> Dict[str, Any]:
        """Generate comprehensive data map"""        try:
            data_map = {
                'organization_id': organization_id,
                'total_assets': len(self._data_inventory),
                'data_categories': {},
                'security_levels': {},
                'locations': {},
                'owners': {},
                'retention_policies': len(self._retention_policies),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Analyze data inventory
            for asset_info in self._data_inventory.values():
                # Count data categories
                for category in asset_info['data_categories']:
                    data_map['data_categories'][category] = data_map['data_categories'].get(category, 0) + 1
                
                # Count security levels
                security_level = asset_info['security_level']
                data_map['security_levels'][security_level] = data_map['security_levels'].get(security_level, 0) + 1
                
                # Count locations
                location = asset_info['location']
                data_map['locations'][location] = data_map['locations'].get(location, 0) + 1
                
                # Count owners
                owner = asset_info['owner']
                data_map['owners'][owner] = data_map['owners'].get(owner, 0) + 1
            
            return data_map
            
        except Exception as e:
            logger.error(f"Data map generation failed: {e}")
            return {}


class ComplianceManager:
    """Main compliance management orchestrator"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_classifier = DataClassifier()
        self.consent_manager = ConsentManager()
        self.audit_trail = AuditTrail(self.config.get('storage', {}))
        self.regulatory_framework = RegulatoryFramework()
        self.data_governance = DataGovernance()
        self._assessments: Dict[str, ComplianceAssessment] = {}
        
    async def initialize(self):
        """Initialize compliance management system"""        try:
            await self.audit_trail.initialize()
            logger.info("Compliance management system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize compliance system: {e}")
            raise
    
    async def conduct_compliance_assessment(
        self,
        organization_id: str,
        frameworks: List[ComplianceFramework],
        organization_data: Dict[str, Any]
    ) -> str:
        """Conduct comprehensive compliance assessment"""        try:
            assessment_id = f"assessment_{uuid.uuid4().hex[:12]}"
            
            # Get all applicable rules
            data_categories = [DataCategory(cat) for cat in organization_data.get('data_categories', [])]
            applicable_rules = await self.regulatory_framework.get_applicable_rules(frameworks, data_categories)
            
            # Validate each rule
            rule_assessments = {}
            total_score = 0.0
            gaps_identified = []
            recommendations = []
            
            for rule in applicable_rules:
                validation_result = await self.regulatory_framework.validate_rule_compliance(rule, organization_data)
                rule_assessments[rule.rule_id] = validation_result
                
                # Calculate overall score
                rule_score = validation_result.get('score', 0.0)
                total_score += rule_score
                
                # Collect gaps and recommendations
                if validation_result.get('status') == ComplianceStatus.NON_COMPLIANT:
                    gaps_identified.append({
                        'rule_id': rule.rule_id,
                        'title': rule.title,
                        'findings': validation_result.get('findings', [])
                    })
                
                recommendations.extend(validation_result.get('recommendations', []))
            
            # Calculate overall compliance status
            if applicable_rules:
                overall_score = total_score / len(applicable_rules)
                if overall_score >= 90:
                    overall_status = ComplianceStatus.COMPLIANT
                elif overall_score >= 70:
                    overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
                else:
                    overall_status = ComplianceStatus.NON_COMPLIANT
            else:
                overall_score = 0.0
                overall_status = ComplianceStatus.UNKNOWN
            
            # Create assessment
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                framework=frameworks[0] if frameworks else ComplianceFramework.GDPR,
                organization_id=organization_id,
                overall_status=overall_status,
                score=overall_score,
                rule_assessments=rule_assessments,
                gaps_identified=gaps_identified,
                recommendations=list(set(recommendations)),  # Remove duplicates
                next_assessment_due=datetime.now(timezone.utc) + timedelta(days=90)
            )
            
            self._assessments[assessment_id] = assessment
            
            # Log assessment completion
            await self.audit_trail.log_event(
                event_type=AuditEventType.ADMIN_ACTION,
                user_id="system",
                organization_id=organization_id,
                action_details={
                    'action': 'compliance_assessment',
                    'assessment_id': assessment_id,
                    'frameworks': [f.value for f in frameworks],
                    'overall_score': overall_score
                },
                ip_address="127.0.0.1",
                user_agent="compliance_system"
            )
            
            logger.info(f"Completed compliance assessment: {assessment_id}")
            return assessment_id
            
        except Exception as e:
            logger.error(f"Compliance assessment failed: {e}")
            raise
    
    async def get_compliance_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get compliance dashboard data"""        try:
            # Get recent assessments
            org_assessments = [
                assessment for assessment in self._assessments.values()
                if assessment.organization_id == organization_id
            ]
            org_assessments.sort(key=lambda x: x.assessed_at, reverse=True)
            
            # Get consent statistics
            consent_report = await self.consent_manager.generate_consent_report(organization_id)
            
            # Get audit summary
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=30)
            audit_report = await self.audit_trail.generate_audit_report(
                organization_id, (start_time, end_time)
            )
            
            # Get data governance summary
            data_map = await self.data_governance.generate_data_map(organization_id)
            expired_data = await self.data_governance.identify_expired_data()
            
            dashboard = {
                'organization_id': organization_id,
                'compliance_summary': {
                    'latest_assessment': org_assessments[0] if org_assessments else None,
                    'total_assessments': len(org_assessments),
                    'compliance_trends': [
                        {
                            'date': assessment.assessed_at.isoformat(),
                            'score': assessment.score
                        }
                        for assessment in org_assessments[-12:]  # Last 12 assessments
                    ]
                },
                'consent_management': consent_report,
                'audit_activity': {
                    'total_events': audit_report.get('total_events', 0),
                    'high_risk_events': audit_report.get('high_risk_events', 0),
                    'recent_activity': audit_report.get('event_types', {})
                },
                'data_governance': {
                    'total_assets': data_map.get('total_assets', 0),
                    'data_categories': data_map.get('data_categories', {}),
                    'expired_data_assets': len(expired_data)
                },
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Compliance dashboard generation failed: {e}")
            return {}
    
    async def handle_data_subject_request(
        self,
        request_type: str,
        user_id: str,
        organization_id: str,
        request_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle data subject requests (GDPR Articles 15-22)"""        try:
            request_id = f"dsr_{uuid.uuid4().hex[:12]}"
            
            # Log the request
            await self.audit_trail.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=user_id,
                organization_id=organization_id,
                action_details={
                    'request_type': request_type,
                    'request_id': request_id,
                    'details': request_details
                },
                ip_address=request_details.get('ip_address', ''),
                user_agent=request_details.get('user_agent', '')
            )
            
            response = {
                'request_id': request_id,
                'request_type': request_type,
                'user_id': user_id,
                'status': 'received',
                'received_at': datetime.now(timezone.utc).isoformat(),
                'estimated_completion': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            }
            
            # Handle specific request types
            if request_type == "access":
                # Article 15 - Right of access
                user_consents = await self.consent_manager.get_user_consents(user_id)
                response['data'] = {
                    'consents': [asdict(consent) for consent in user_consents],
                    'processing_purposes': [consent.purpose for consent in user_consents],
                    'data_categories': list(set([
                        cat.value for consent in user_consents
                        for cat in consent.data_categories
                    ]))
                }
                
            elif request_type == "rectification":
                # Article 16 - Right to rectification
                response['status'] = 'processing'
                response['message'] = 'Data rectification request received and will be processed'
                
            elif request_type == "erasure":
                # Article 17 - Right to erasure ('right to be forgotten')
                response['status'] = 'processing'
                response['message'] = 'Data erasure request received and will be processed'
                
            elif request_type == "portability":
                # Article 20 - Right to data portability
                response['status'] = 'processing'
                response['message'] = 'Data portability request received'
                
            logger.info(f"Processed data subject request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Data subject request handling failed: {e}")
            return {
                'request_id': f"dsr_{uuid.uuid4().hex[:12]}",
                'status': 'error',
                'error': str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for compliance system"""        try:
            return {
                'status': 'healthy',
                'components': {
                    'data_classifier': 'active',
                    'consent_manager': 'active',
                    'audit_trail': 'active',
                    'regulatory_framework': 'active',
                    'data_governance': 'active'
                },
                'active_assessments': len(self._assessments),
                'consent_records': len(self.consent_manager._consent_records),
                'audit_events': len(self.audit_trail._audit_events),
                'data_assets': len(self.data_governance._data_inventory),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 1.0
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 0.0
            }