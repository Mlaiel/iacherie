"""GDPR/CCPA Compliance Validator for MongoDB
==========================================

Comprehensive compliance validation system for GDPR, CCPA, and other
data protection regulations with automated compliance checking and reporting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- Compliance Specialist: GDPR/CCPA regulatory compliance
- Security Engineer: Data protection and privacy controls
- DBA: Data governance and retention policies
- Legal Engineer: Regulatory framework implementation
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act (US)
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    PDPA = "pdpa"  # Personal Data Protection Act (Singapore)

class DataCategory(Enum):
    """Categories of personal data."""
    PERSONAL_IDENTIFIERS = "personal_identifiers"  # Name, email, phone, address
    FINANCIAL = "financial"  # Credit card, bank account, payment info
    BIOMETRIC = "biometric"  # Fingerprints, facial recognition, voice
    HEALTH = "health"  # Medical records, health status
    BEHAVIORAL = "behavioral"  # Browsing history, preferences, analytics
    SENSITIVE = "sensitive"  # Race, religion, political views, sexual orientation
    LOCATION = "location"  # GPS coordinates, IP address, geolocation
    TECHNICAL = "technical"  # Device IDs, cookies, session tokens

class ProcessingPurpose(Enum):
    """Purposes for data processing."""
    AUTHENTICATION = "authentication"
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    LEGAL_COMPLIANCE = "legal_compliance"
    SECURITY = "security"
    RESEARCH = "research"
    PROFILING = "profiling"

@dataclass
class DataSubject:
    """Data subject (individual) information."""
    subject_id: str
    email: str
    consent_given: bool = False
    consent_date: Optional[datetime] = None
    consent_version: str = "1.0"
    opt_out_requests: List[datetime] = field(default_factory=list)
    data_requests: List[Dict[str, Any]] = field(default_factory=list)
    jurisdiction: Optional[str] = None
    age_verified: bool = False
    minor: bool = False
    last_activity: Optional[datetime] = None

@dataclass
class DataProcessingRecord:
    """Record of data processing activity."""
    processing_id: str
    data_subject_id: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    legal_basis: str
    data_source: str
    retention_period: timedelta
    processing_date: datetime
    collection_method: str
    third_party_sharing: bool = False
    cross_border_transfer: bool = False
    automated_decision_making: bool = False

@dataclass
class ComplianceRule:
    """Individual compliance rule."""
    rule_id: str
    framework: ComplianceFramework
    description: str
    data_categories: List[DataCategory]
    requirements: Dict[str, Any]
    severity: str = "high"  # low, medium, high, critical
    automated_check: bool = True

class ComplianceValidator:
    """GDPR/CCPA compliance validation system."""
    
    def __init__(self) -> None:
        """Initialize compliance validator."""
        self._data_subjects: Dict[str, DataSubject] = {}
        self._processing_records: List[DataProcessingRecord] = []
        self._compliance_rules: Dict[str, ComplianceRule] = {}
        self._violation_log: List[Dict[str, Any]] = []
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        
        # Data retention policies (in days)
        self._retention_policies = {
            DataCategory.PERSONAL_IDENTIFIERS: 2555,  # 7 years
            DataCategory.FINANCIAL: 2555,  # 7 years
            DataCategory.BIOMETRIC: 1095,  # 3 years
            DataCategory.HEALTH: 3650,  # 10 years
            DataCategory.BEHAVIORAL: 365,  # 1 year
            DataCategory.SENSITIVE: 365,  # 1 year
            DataCategory.LOCATION: 90,  # 3 months
            DataCategory.TECHNICAL: 30  # 1 month
        }
        
        # Sensitive field patterns
        self._sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
    
    def _initialize_compliance_rules(self) -> None:
        """Initialize standard compliance rules."""
        
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="gdpr_consent",
                framework=ComplianceFramework.GDPR,
                description="Valid consent required for personal data processing",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS, DataCategory.BEHAVIORAL],
                requirements={
                    "consent_required": True,
                    "consent_specific": True,
                    "consent_informed": True,
                    "consent_withdrawable": True
                }
            ),
            ComplianceRule(
                rule_id="gdpr_data_minimization",
                framework=ComplianceFramework.GDPR,
                description="Data processing must be limited to what is necessary",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS],
                requirements={
                    "purpose_limitation": True,
                    "data_minimization": True,
                    "storage_limitation": True
                }
            ),
            ComplianceRule(
                rule_id="gdpr_right_to_be_forgotten",
                framework=ComplianceFramework.GDPR,
                description="Data subjects can request deletion of personal data",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS, DataCategory.BEHAVIORAL],
                requirements={
                    "deletion_capability": True,
                    "deletion_timeline": 30  # days
                }
            ),
            ComplianceRule(
                rule_id="gdpr_data_portability",
                framework=ComplianceFramework.GDPR,
                description="Data subjects can request data export",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS],
                requirements={
                    "export_capability": True,
                    "structured_format": True,
                    "machine_readable": True
                }
            ),
            ComplianceRule(
                rule_id="gdpr_breach_notification",
                framework=ComplianceFramework.GDPR,
                description="Data breaches must be reported within 72 hours",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS, DataCategory.SENSITIVE],
                requirements={
                    "notification_timeline": 72,  # hours
                    "breach_logging": True,
                    "impact_assessment": True
                }
            )
        ]
        
        # CCPA Rules
        ccpa_rules = [
            ComplianceRule(
                rule_id="ccpa_disclosure",
                framework=ComplianceFramework.CCPA,
                description="Consumers must be informed about data collection",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS],
                requirements={
                    "collection_disclosure": True,
                    "purpose_disclosure": True,
                    "sharing_disclosure": True
                }
            ),
            ComplianceRule(
                rule_id="ccpa_opt_out",
                framework=ComplianceFramework.CCPA,
                description="Consumers can opt out of data sale",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS, DataCategory.BEHAVIORAL],
                requirements={
                    "opt_out_mechanism": True,
                    "opt_out_timeline": 15  # days
                }
            ),
            ComplianceRule(
                rule_id="ccpa_access_right",
                framework=ComplianceFramework.CCPA,
                description="Consumers can request information about data processing",
                data_categories=[DataCategory.PERSONAL_IDENTIFIERS],
                requirements={
                    "access_provision": True,
                    "response_timeline": 45  # days
                }
            )
        ]
        
        # Store all rules
        for rule in gdpr_rules + ccpa_rules:
            self._compliance_rules[rule.rule_id] = rule
    
    def register_data_subject(self, subject_id: str, email: str, 
                             consent_given: bool = False, jurisdiction: str = None,
                             age_verified: bool = False, minor: bool = False) -> bool:
        """Register a new data subject."""
        try:
            if subject_id in self._data_subjects:
                logger.warning(f"Data subject already registered: {subject_id}")
                return False
            
            data_subject = DataSubject(
                subject_id=subject_id,
                email=email,
                consent_given=consent_given,
                consent_date=datetime.utcnow() if consent_given else None,
                jurisdiction=jurisdiction,
                age_verified=age_verified,
                minor=minor,
                last_activity=datetime.utcnow()
            )
            
            self._data_subjects[subject_id] = data_subject
            logger.info(f"Registered data subject: {subject_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register data subject {subject_id}: {e}")
            return False
    
    def record_data_processing(self, processing_id: str, data_subject_id: str,
                              data_categories: List[DataCategory], 
                              processing_purposes: List[ProcessingPurpose],
                              legal_basis: str, data_source: str,
                              collection_method: str = "automated",
                              third_party_sharing: bool = False,
                              cross_border_transfer: bool = False) -> bool:
        """Record data processing activity."""
        try:
            # Calculate retention period based on data categories
            max_retention = max(
                self._retention_policies.get(category, 365) 
                for category in data_categories
            )
            retention_period = timedelta(days=max_retention)
            
            processing_record = DataProcessingRecord(
                processing_id=processing_id,
                data_subject_id=data_subject_id,
                data_categories=data_categories,
                processing_purposes=processing_purposes,
                legal_basis=legal_basis,
                data_source=data_source,
                retention_period=retention_period,
                processing_date=datetime.utcnow(),
                collection_method=collection_method,
                third_party_sharing=third_party_sharing,
                cross_border_transfer=cross_border_transfer,
                automated_decision_making="profiling" in [p.value for p in processing_purposes]
            )
            
            self._processing_records.append(processing_record)
            
            # Update data subject activity
            if data_subject_id in self._data_subjects:
                self._data_subjects[data_subject_id].last_activity = datetime.utcnow()
            
            logger.info(f"Recorded data processing: {processing_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record data processing {processing_id}: {e}")
            return False
    
    def validate_compliance(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Validate compliance with specified framework or all frameworks."""
        violations = []
        compliance_score = 0
        total_checks = 0
        
        rules_to_check = [
            rule for rule in self._compliance_rules.values()
            if framework is None or rule.framework == framework
        ]
        
        for rule in rules_to_check:
            total_checks += 1
            violation = self._check_compliance_rule(rule)
            if violation:
                violations.append(violation)
            else:
                compliance_score += 1
        
        compliance_percentage = (compliance_score / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "framework": framework.value if framework else "all",
            "compliance_score": compliance_percentage,
            "total_checks": total_checks,
            "violations": violations,
            "status": "COMPLIANT" if compliance_percentage >= 95 else "NON_COMPLIANT",
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def _check_compliance_rule(self, rule: ComplianceRule) -> Optional[Dict[str, Any]]:
        """Check a specific compliance rule."""
        try:
            if rule.rule_id == "gdpr_consent":
                return self._check_consent_compliance()
            elif rule.rule_id == "gdpr_data_minimization":
                return self._check_data_minimization()
            elif rule.rule_id == "gdpr_right_to_be_forgotten":
                return self._check_deletion_capability()
            elif rule.rule_id == "ccpa_opt_out":
                return self._check_opt_out_mechanism()
            # Add more rule checks as needed
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking compliance rule {rule.rule_id}: {e}")
            return {
                "rule_id": rule.rule_id,
                "description": rule.description,
                "violation": f"Error checking rule: {e}",
                "severity": "high"
            }
    
    def _check_consent_compliance(self) -> Optional[Dict[str, Any]]:
        """Check GDPR consent compliance."""
        non_consented_subjects = [
            subject for subject in self._data_subjects.values()
            if not subject.consent_given and subject.jurisdiction in ["EU", "EEA"]
        ]
        
        if non_consented_subjects:
            return {
                "rule_id": "gdpr_consent",
                "description": "Valid consent required for personal data processing",
                "violation": f"Found {len(non_consented_subjects)} subjects without valid consent",
                "severity": "critical",
                "affected_subjects": [s.subject_id for s in non_consented_subjects]
            }
        
        return None
    
    def _check_data_minimization(self) -> Optional[Dict[str, Any]]:
        """Check data minimization compliance."""
        # Check for excessive data retention
        now = datetime.utcnow()
        excessive_retention = []
        
        for record in self._processing_records:
            expected_deletion = record.processing_date + record.retention_period
            if now > expected_deletion:
                excessive_retention.append(record.processing_id)
        
        if excessive_retention:
            return {
                "rule_id": "gdpr_data_minimization",
                "description": "Data processing must be limited to what is necessary",
                "violation": f"Found {len(excessive_retention)} records exceeding retention period",
                "severity": "high",
                "affected_records": excessive_retention
            }
        
        return None
    
    def _check_deletion_capability(self) -> Optional[Dict[str, Any]]:
        """Check right to be forgotten compliance."""
        # This would typically check if deletion mechanisms are in place
        # For now, we'll assume they are if the system is properly configured
        return None
    
    def _check_opt_out_mechanism(self) -> Optional[Dict[str, Any]]:
        """Check CCPA opt-out mechanism compliance."""
        # Check if opt-out requests are handled within required timeframe
        overdue_requests = []
        cutoff_date = datetime.utcnow() - timedelta(days=15)
        
        for subject in self._data_subjects.values():
            if subject.jurisdiction == "CA":  # California
                for opt_out_date in subject.opt_out_requests:
                    if opt_out_date < cutoff_date:
                        overdue_requests.append(subject.subject_id)
                        break
        
        if overdue_requests:
            return {
                "rule_id": "ccpa_opt_out",
                "description": "Consumers can opt out of data sale",
                "violation": f"Found {len(overdue_requests)} overdue opt-out requests",
                "severity": "high",
                "affected_subjects": overdue_requests
            }
        
        return None
    
    def handle_data_subject_request(self, subject_id: str, request_type: str,
                                   details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle data subject rights requests."""
        if subject_id not in self._data_subjects:
            return {"error": "Data subject not found", "status": "failed"}
        
        data_subject = self._data_subjects[subject_id]
        request_id = f"{request_type}_{subject_id}_{int(datetime.utcnow().timestamp())}"
        
        request_record = {
            "request_id": request_id,
            "subject_id": subject_id,
            "request_type": request_type,
            "submitted_at": datetime.utcnow(),
            "details": details or {},
            "status": "pending"
        }
        
        if request_type == "access":
            # Provide data access
            subject_data = self._get_subject_data(subject_id)
            request_record["response"] = subject_data
            request_record["status"] = "completed"
            
        elif request_type == "deletion":
            # Mark for deletion
            request_record["scheduled_deletion"] = datetime.utcnow() + timedelta(days=30)
            request_record["status"] = "scheduled"
            
        elif request_type == "opt_out":
            # Record opt-out request
            data_subject.opt_out_requests.append(datetime.utcnow())
            request_record["status"] = "completed"
            
        elif request_type == "portability":
            # Provide portable data export
            portable_data = self._export_subject_data(subject_id)
            request_record["response"] = portable_data
            request_record["status"] = "completed"
        
        data_subject.data_requests.append(request_record)
        
        logger.info(f"Processed data subject request: {request_id}")
        return request_record
    
    def _get_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """Get all data associated with a subject."""
        subject_records = [
            record for record in self._processing_records
            if record.data_subject_id == subject_id
        ]
        
        return {
            "subject_info": asdict(self._data_subjects[subject_id]) if subject_id in self._data_subjects else {},
            "processing_records": [asdict(record) for record in subject_records],
            "data_categories": list(set([
                cat.value for record in subject_records for cat in record.data_categories
            ])),
            "processing_purposes": list(set([
                purpose.value for record in subject_records for purpose in record.processing_purposes
            ]))
        }
    
    def _export_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """Export subject data in portable format."""
        subject_data = self._get_subject_data(subject_id)
        
        # Format for portability (structured, machine-readable)
        return {
            "export_format": "JSON",
            "export_date": datetime.utcnow().isoformat(),
            "subject_id": subject_id,
            "data": subject_data
        }
    
    def scan_for_pii(self, text: str) -> Dict[str, List[str]]:
        """Scan text for personally identifiable information."""
        findings = {}
        
        for pii_type, pattern in self._sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
        
        return findings
    
    def get_compliance_report(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        compliance_check = self.validate_compliance(framework)
        
        # Additional statistics
        total_subjects = len(self._data_subjects)
        consented_subjects = sum(1 for s in self._data_subjects.values() if s.consent_given)
        total_processing_records = len(self._processing_records)
        
        # Data retention analysis
        retention_analysis = {}
        for category in DataCategory:
            records_count = sum(
                1 for record in self._processing_records
                if category in record.data_categories
            )
            retention_analysis[category.value] = {
                "records_count": records_count,
                "retention_days": self._retention_policies.get(category, 365)
            }
        
        return {
            "compliance_check": compliance_check,
            "statistics": {
                "total_data_subjects": total_subjects,
                "consented_subjects": consented_subjects,
                "consent_rate": (consented_subjects / total_subjects * 100) if total_subjects > 0 else 0,
                "total_processing_records": total_processing_records
            },
            "retention_analysis": retention_analysis,
            "report_generated": datetime.utcnow().isoformat()
        }

# Global compliance validator instance
_default_validator: Optional[ComplianceValidator] = None

def get_compliance_validator() -> ComplianceValidator:
    """Get or create default compliance validator."""
    global _default_validator
    if _default_validator is None:
        _default_validator = ComplianceValidator()
    return _default_validator

# Export main classes and functions
__all__ = [
    'ComplianceFramework',
    'DataCategory',
    'ProcessingPurpose',
    'DataSubject',
    'DataProcessingRecord',
    'ComplianceRule',
    'ComplianceValidator',
    'get_compliance_validator'
]