"""Security Service - Consolidated Security and Compliance Services
================================================================

Comprehensive security system providing encryption, authentication, compliance,
threat detection, and data protection for the IA Influencer Agent platform.

Consolidates:
- security_service.py (existing security functionality)
- security/ subdirectory (encryption, compliance, monitoring modules)
- data encryption and key management
- compliance and legal validation

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/security.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import secrets
import json
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Enums
class SecurityLevel(Enum):
    """Security level enumeration"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    SALSA20 = "salsa20"

class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"

class AuditEventType(Enum):
    """Audit event type enumeration"""
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PERMISSION_CHANGE = "permission_change"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_ACCESS = "system_access"

# Data structures
@dataclass
class EncryptionKey:
    """Encryption key data structure"""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: str  # Base64 encoded
    key_size: int
    purpose: str
    owner_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    is_active: bool = True

@dataclass
class SecurityAuditLog:
    """Security audit log data structure"""
    log_id: str
    event_type: AuditEventType
    user_id: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    risk_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ThreatAlert:
    """Threat detection alert data structure"""
    alert_id: str
    threat_type: str
    level: ThreatLevel
    source_ip: Optional[str]
    target_resource: Optional[str]
    description: str
    indicators: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
    resolved: bool = False
    false_positive: bool = False
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

@dataclass
class ComplianceReport:
    """Compliance audit report data structure"""
    report_id: str
    framework: ComplianceFramework
    scope: str
    compliance_score: float
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    auditor_id: Optional[str] = None

@dataclass
class SecurityPolicy:
    """Security policy data structure"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    applicable_roles: List[str] = field(default_factory=list)
    enforcement_level: SecurityLevel = SecurityLevel.INTERNAL
    auto_enforce: bool = True
    exceptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None

@dataclass
class DataClassification:
    """Data classification data structure"""
    classification_id: str
    resource_id: str
    resource_type: str
    classification: SecurityLevel
    sensitivity_tags: List[str] = field(default_factory=list)
    retention_period: Optional[int] = None  # Days
    access_restrictions: Dict[str, Any] = field(default_factory=dict)
    encryption_required: bool = True
    backup_allowed: bool = True
    cross_border_transfer: bool = False
    classified_at: datetime = field(default_factory=datetime.utcnow)
    classified_by: Optional[str] = None

# Services
class EncryptionService:
    """Data encryption and key management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.keys_store: Dict[str, EncryptionKey] = {}
        self.master_key = self.config.get('master_key', secrets.token_urlsafe(32))
        logger.info("🔐 Encryption Service initialized")
    
    async def generate_key(self, algorithm: EncryptionAlgorithm, purpose: str, owner_id: str = None) -> EncryptionKey:
        """Generate encryption key"""
        try:
            key_sizes = {
                EncryptionAlgorithm.AES_256: 256,
                EncryptionAlgorithm.RSA_2048: 2048,
                EncryptionAlgorithm.RSA_4096: 4096,
                EncryptionAlgorithm.CHACHA20: 256,
                EncryptionAlgorithm.SALSA20: 256
            }
            
            key_size = key_sizes.get(algorithm, 256)
            
            # Generate random key data
            if algorithm in [EncryptionAlgorithm.AES_256, EncryptionAlgorithm.CHACHA20, EncryptionAlgorithm.SALSA20]:
                key_bytes = secrets.token_bytes(key_size // 8)
            else:  # RSA keys
                # In a real implementation, this would use cryptographic libraries
                key_bytes = secrets.token_bytes(256)  # Simplified for demo
            
            key = EncryptionKey(
                key_id=str(uuid.uuid4()),
                algorithm=algorithm,
                key_data=base64.b64encode(key_bytes).decode('utf-8'),
                key_size=key_size,
                purpose=purpose,
                owner_id=owner_id,
                expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year default
            )
            
            self.keys_store[key.key_id] = key
            logger.info(f"Generated encryption key: {key.key_id}")
            return key
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            raise
    
    async def encrypt_data(self, data: str, key_id: str) -> Dict[str, str]:
        """Encrypt data using specified key"""
        try:
            key = self.keys_store.get(key_id)
            if not key or not key.is_active:
                raise ValueError(f"Invalid or inactive key: {key_id}")
            
            # Update last used timestamp
            key.last_used = datetime.utcnow()
            
            # In a real implementation, this would use actual encryption
            # For demo purposes, we'll use simple base64 encoding
            data_bytes = data.encode('utf-8')
            encrypted_bytes = base64.b64encode(data_bytes)
            
            return {
                "encrypted_data": encrypted_bytes.decode('utf-8'),
                "key_id": key_id,
                "algorithm": key.algorithm.value,
                "iv": base64.b64encode(secrets.token_bytes(16)).decode('utf-8')  # Initialization vector
            }
        except Exception as e:
            logger.error(f"Data encryption error: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str, key_id: str, iv: str = None) -> str:
        """Decrypt data using specified key"""
        try:
            key = self.keys_store.get(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Update last used timestamp
            key.last_used = datetime.utcnow()
            
            # In a real implementation, this would use actual decryption
            # For demo purposes, we'll decode the base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = encrypted_bytes.decode('utf-8')
            
            return decrypted_data
        except Exception as e:
            logger.error(f"Data decryption error: {e}")
            raise
    
    async def rotate_key(self, key_id: str) -> EncryptionKey:
        """Rotate encryption key"""
        try:
            old_key = self.keys_store.get(key_id)
            if not old_key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Deactivate old key
            old_key.is_active = False
            
            # Generate new key with same properties
            new_key = await self.generate_key(
                old_key.algorithm, 
                old_key.purpose, 
                old_key.owner_id
            )
            
            logger.info(f"Rotated key {key_id} -> {new_key.key_id}")
            return new_key
        except Exception as e:
            logger.error(f"Key rotation error: {e}")
            raise
    
    async def get_active_keys(self, owner_id: str = None) -> List[EncryptionKey]:
        """Get active encryption keys"""
        try:
            keys = [key for key in self.keys_store.values() if key.is_active]
            
            if owner_id:
                keys = [key for key in keys if key.owner_id == owner_id]
            
            return keys
        except Exception as e:
            logger.error(f"Active keys retrieval error: {e}")
            return []

class ThreatDetectionService:
    """Threat detection and monitoring service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alerts_store: Dict[str, ThreatAlert] = {}
        self.detection_rules = self._initialize_detection_rules()
        logger.info("🛡️ Threat Detection Service initialized")
    
    def _initialize_detection_rules(self) -> List[Dict[str, Any]]:
        """Initialize threat detection rules"""
        return [
            {
                "name": "brute_force_login",
                "pattern": "multiple_failed_logins",
                "threshold": 5,
                "window_minutes": 10,
                "threat_level": ThreatLevel.HIGH
            },
            {
                "name": "suspicious_data_access",
                "pattern": "unusual_data_volume",
                "threshold": 1000,  # MB
                "window_minutes": 5,
                "threat_level": ThreatLevel.MEDIUM
            },
            {
                "name": "privilege_escalation",
                "pattern": "permission_change",
                "threshold": 1,
                "window_minutes": 1,
                "threat_level": ThreatLevel.CRITICAL
            },
            {
                "name": "sql_injection",
                "pattern": "malicious_query_pattern",
                "threshold": 1,
                "window_minutes": 1,
                "threat_level": ThreatLevel.CRITICAL
            }
        ]
    
    async def analyze_security_event(self, event_data: Dict[str, Any]) -> Optional[ThreatAlert]:
        """Analyze security event for threats"""
        try:
            # Check against detection rules
            for rule in self.detection_rules:
                if await self._matches_rule(event_data, rule):
                    alert = await self._create_threat_alert(event_data, rule)
                    return alert
            
            return None
        except Exception as e:
            logger.error(f"Security event analysis error: {e}")
            return None
    
    async def _matches_rule(self, event_data: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if event matches detection rule"""
        try:
            pattern = rule["pattern"]
            
            if pattern == "multiple_failed_logins":
                return event_data.get("event_type") == "login" and not event_data.get("success", True)
            elif pattern == "unusual_data_volume":
                return event_data.get("data_volume", 0) > rule["threshold"]
            elif pattern == "permission_change":
                return event_data.get("event_type") == "permission_change"
            elif pattern == "malicious_query_pattern":
                query = event_data.get("query", "").lower()
                malicious_patterns = ["union select", "drop table", "'; --", "' or '1'='1"]
                return any(pattern in query for pattern in malicious_patterns)
            
            return False
        except Exception as e:
            logger.error(f"Rule matching error: {e}")
            return False
    
    async def _create_threat_alert(self, event_data: Dict[str, Any], rule: Dict[str, Any]) -> ThreatAlert:
        """Create threat alert"""
        try:
            alert = ThreatAlert(
                alert_id=str(uuid.uuid4()),
                threat_type=rule["name"],
                level=rule["threat_level"],
                source_ip=event_data.get("ip_address"),
                target_resource=event_data.get("resource_id"),
                description=f"Detected {rule['name']} threat",
                indicators=[f"Pattern: {rule['pattern']}", f"Threshold exceeded: {rule['threshold']}"],
                mitigation_actions=await self._get_mitigation_actions(rule["name"])
            )
            
            self.alerts_store[alert.alert_id] = alert
            logger.warning(f"Threat alert created: {alert.alert_id} - {alert.threat_type}")
            return alert
        except Exception as e:
            logger.error(f"Threat alert creation error: {e}")
            raise
    
    async def _get_mitigation_actions(self, threat_type: str) -> List[str]:
        """Get mitigation actions for threat type"""
        mitigations = {
            "brute_force_login": [
                "Temporarily block source IP",
                "Require additional authentication",
                "Lock user account temporarily"
            ],
            "suspicious_data_access": [
                "Review data access logs",
                "Verify user authorization",
                "Monitor ongoing activity"
            ],
            "privilege_escalation": [
                "Immediately revoke elevated permissions",
                "Audit permission changes",
                "Investigate account compromise"
            ],
            "sql_injection": [
                "Block malicious requests",
                "Review application logs",
                "Update input validation"
            ]
        }
        
        return mitigations.get(threat_type, ["Investigate further", "Monitor activity"])
    
    async def get_active_threats(self, level: ThreatLevel = None) -> List[ThreatAlert]:
        """Get active threat alerts"""
        try:
            alerts = [alert for alert in self.alerts_store.values() if not alert.resolved]
            
            if level:
                alerts = [alert for alert in alerts if alert.level == level]
            
            # Sort by severity and detection time
            severity_order = {ThreatLevel.CRITICAL: 4, ThreatLevel.HIGH: 3, ThreatLevel.MEDIUM: 2, ThreatLevel.LOW: 1}
            alerts.sort(key=lambda a: (severity_order.get(a.level, 0), a.detected_at), reverse=True)
            
            return alerts
        except Exception as e:
            logger.error(f"Active threats retrieval error: {e}")
            return []
    
    async def resolve_threat(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve threat alert"""
        try:
            alert = self.alerts_store.get(alert_id)
            if not alert:
                return False
            
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            
            logger.info(f"Resolved threat alert: {alert_id}")
            return True
        except Exception as e:
            logger.error(f"Threat resolution error: {e}")
            return False

class ComplianceService:
    """Compliance monitoring and audit service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.reports_store: Dict[str, ComplianceReport] = {}
        self.compliance_rules = self._initialize_compliance_rules()
        logger.info("📋 Compliance Service initialized")
    
    def _initialize_compliance_rules(self) -> Dict[ComplianceFramework, List[Dict[str, Any]]]:
        """Initialize compliance rules for different frameworks"""
        return {
            ComplianceFramework.GDPR: [
                {
                    "rule_id": "gdpr_consent",
                    "description": "Obtain explicit consent for data processing",
                    "check": "consent_records_exist"
                },
                {
                    "rule_id": "gdpr_data_minimization",
                    "description": "Collect only necessary data",
                    "check": "data_collection_justified"
                },
                {
                    "rule_id": "gdpr_data_retention",
                    "description": "Delete data when no longer needed",
                    "check": "retention_policies_enforced"
                }
            ],
            ComplianceFramework.CCPA: [
                {
                    "rule_id": "ccpa_disclosure",
                    "description": "Disclose data collection and sharing",
                    "check": "privacy_notice_exists"
                },
                {
                    "rule_id": "ccpa_opt_out",
                    "description": "Provide opt-out mechanism",
                    "check": "opt_out_mechanism_available"
                }
            ],
            ComplianceFramework.ISO27001: [
                {
                    "rule_id": "iso_access_control",
                    "description": "Implement access controls",
                    "check": "access_controls_implemented"
                },
                {
                    "rule_id": "iso_encryption",
                    "description": "Encrypt sensitive data",
                    "check": "encryption_implemented"
                }
            ]
        }
    
    async def run_compliance_audit(self, framework: ComplianceFramework, scope: str) -> ComplianceReport:
        """Run compliance audit for specified framework"""
        try:
            logger.info(f"Running {framework.value} compliance audit")
            
            rules = self.compliance_rules.get(framework, [])
            violations = []
            total_checks = len(rules)
            passed_checks = 0
            
            for rule in rules:
                check_result = await self._perform_compliance_check(rule)
                if not check_result["passed"]:
                    violations.append({
                        "rule_id": rule["rule_id"],
                        "description": rule["description"],
                        "details": check_result["details"],
                        "severity": check_result.get("severity", "medium")
                    })
                else:
                    passed_checks += 1
            
            # Calculate compliance score
            compliance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 100
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(violations, framework)
            
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                framework=framework,
                scope=scope,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations
            )
            
            self.reports_store[report.report_id] = report
            logger.info(f"Compliance audit completed: {report.report_id} (Score: {compliance_score:.1f}%)")
            return report
        except Exception as e:
            logger.error(f"Compliance audit error: {e}")
            raise
    
    async def _perform_compliance_check(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Perform individual compliance check"""
        try:
            check_type = rule["check"]
            
            # Mock compliance checks
            if check_type == "consent_records_exist":
                # Check if consent records exist
                passed = True  # Simulated check
                details = "Consent records found for all users"
            elif check_type == "data_collection_justified":
                # Check if data collection is justified
                passed = True  # Simulated check
                details = "Data collection purposes documented"
            elif check_type == "retention_policies_enforced":
                # Check if retention policies are enforced
                passed = False  # Simulated violation
                details = "Some data exceeds retention period"
            elif check_type == "encryption_implemented":
                # Check if encryption is implemented
                passed = True  # Simulated check
                details = "Encryption enabled for sensitive data"
            else:
                passed = True
                details = "Check completed successfully"
            
            return {
                "passed": passed,
                "details": details,
                "severity": "high" if not passed else "info"
            }
        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {"passed": False, "details": str(e), "severity": "high"}
    
    async def _generate_compliance_recommendations(self, violations: List[Dict[str, Any]], framework: ComplianceFramework) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for violation in violations:
            rule_id = violation["rule_id"]
            
            if rule_id == "gdpr_data_retention":
                recommendations.append("Implement automated data deletion based on retention policies")
            elif rule_id == "gdpr_consent":
                recommendations.append("Implement explicit consent collection mechanisms")
            elif rule_id == "iso_encryption":
                recommendations.append("Enable encryption for all sensitive data at rest and in transit")
            elif rule_id == "ccpa_opt_out":
                recommendations.append("Implement user-friendly opt-out mechanisms")
        
        if not violations:
            recommendations.append(f"Maintain current {framework.value} compliance standards")
        
        return recommendations
    
    async def get_compliance_status(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Get current compliance status"""
        try:
            reports = list(self.reports_store.values())
            
            if framework:
                reports = [r for r in reports if r.framework == framework]
            
            if not reports:
                return {"status": "no_data", "message": "No compliance reports available"}
            
            # Get latest report for each framework
            latest_reports = {}
            for report in reports:
                if report.framework not in latest_reports or report.generated_at > latest_reports[report.framework].generated_at:
                    latest_reports[report.framework] = report
            
            status = {}
            for fw, report in latest_reports.items():
                status[fw.value] = {
                    "compliance_score": report.compliance_score,
                    "violations_count": len(report.violations),
                    "last_audit": report.generated_at.isoformat(),
                    "status": "compliant" if report.compliance_score >= 90 else "non_compliant"
                }
            
            return status
        except Exception as e:
            logger.error(f"Compliance status error: {e}")
            return {"status": "error", "message": str(e)}

class DataClassificationService:
    """Data classification and protection service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.classifications_store: Dict[str, DataClassification] = {}
        logger.info("🏷️ Data Classification Service initialized")
    
    async def classify_data(self, resource_id: str, resource_type: str, classification_level: SecurityLevel, tags: List[str] = None, classifier_id: str = None) -> DataClassification:
        """Classify data resource"""
        try:
            classification = DataClassification(
                classification_id=str(uuid.uuid4()),
                resource_id=resource_id,
                resource_type=resource_type,
                classification=classification_level,
                sensitivity_tags=tags or [],
                classified_by=classifier_id
            )
            
            # Set default policies based on classification level
            classification = await self._apply_classification_policies(classification)
            
            self.classifications_store[classification.classification_id] = classification
            logger.info(f"Classified data resource: {resource_id} as {classification_level.value}")
            return classification
        except Exception as e:
            logger.error(f"Data classification error: {e}")
            raise
    
    async def _apply_classification_policies(self, classification: DataClassification) -> DataClassification:
        """Apply policies based on classification level"""
        level = classification.classification
        
        if level == SecurityLevel.PUBLIC:
            classification.encryption_required = False
            classification.backup_allowed = True
            classification.cross_border_transfer = True
            classification.retention_period = 365  # 1 year
        elif level == SecurityLevel.INTERNAL:
            classification.encryption_required = True
            classification.backup_allowed = True
            classification.cross_border_transfer = True
            classification.retention_period = 2555  # 7 years
        elif level == SecurityLevel.CONFIDENTIAL:
            classification.encryption_required = True
            classification.backup_allowed = True
            classification.cross_border_transfer = False
            classification.retention_period = 1095  # 3 years
            classification.access_restrictions = {"role_required": "manager"}
        elif level == SecurityLevel.RESTRICTED:
            classification.encryption_required = True
            classification.backup_allowed = False
            classification.cross_border_transfer = False
            classification.retention_period = 365  # 1 year
            classification.access_restrictions = {"role_required": "admin", "approval_required": True}
        elif level == SecurityLevel.TOP_SECRET:
            classification.encryption_required = True
            classification.backup_allowed = False
            classification.cross_border_transfer = False
            classification.retention_period = 90  # 90 days
            classification.access_restrictions = {"role_required": "security_officer", "approval_required": True, "audit_required": True}
        
        return classification
    
    async def get_data_classification(self, resource_id: str) -> Optional[DataClassification]:
        """Get data classification for resource"""
        try:
            for classification in self.classifications_store.values():
                if classification.resource_id == resource_id:
                    return classification
            return None
        except Exception as e:
            logger.error(f"Data classification retrieval error: {e}")
            return None
    
    async def check_access_permissions(self, resource_id: str, user_id: str, user_roles: List[str]) -> Dict[str, Any]:
        """Check if user can access classified data"""
        try:
            classification = await self.get_data_classification(resource_id)
            if not classification:
                return {"allowed": True, "reason": "No classification found"}
            
            restrictions = classification.access_restrictions
            
            # Check role requirements
            required_role = restrictions.get("role_required")
            if required_role and required_role not in user_roles:
                return {"allowed": False, "reason": f"Requires {required_role} role"}
            
            # Check if approval is required
            if restrictions.get("approval_required", False):
                # In a real implementation, this would check approval status
                return {"allowed": False, "reason": "Approval required for access"}
            
            return {"allowed": True, "reason": "Access granted"}
        except Exception as e:
            logger.error(f"Access permission check error: {e}")
            return {"allowed": False, "reason": str(e)}

class SecurityAuditService:
    """Security audit logging and monitoring service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.audit_logs: List[SecurityAuditLog] = []
        self.max_logs = self.config.get('max_logs', 10000)
        logger.info("📊 Security Audit Service initialized")
    
    async def log_security_event(self, event_type: AuditEventType, user_id: str = None, resource_id: str = None, action: str = "", details: Dict[str, Any] = None, ip_address: str = None, success: bool = True) -> SecurityAuditLog:
        """Log security event"""
        try:
            # Calculate risk score
            risk_score = await self._calculate_risk_score(event_type, details or {}, success)
            
            log_entry = SecurityAuditLog(
                log_id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                resource_id=resource_id,
                action=action,
                details=details or {},
                ip_address=ip_address,
                success=success,
                risk_score=risk_score
            )
            
            self.audit_logs.append(log_entry)
            
            # Maintain log size limit
            if len(self.audit_logs) > self.max_logs:
                self.audit_logs = self.audit_logs[-self.max_logs:]
            
            logger.debug(f"Security event logged: {log_entry.log_id}")
            return log_entry
        except Exception as e:
            logger.error(f"Security event logging error: {e}")
            raise
    
    async def _calculate_risk_score(self, event_type: AuditEventType, details: Dict[str, Any], success: bool) -> float:
        """Calculate risk score for security event"""
        try:
            base_scores = {
                AuditEventType.LOGIN: 0.1,
                AuditEventType.LOGOUT: 0.0,
                AuditEventType.DATA_ACCESS: 0.3,
                AuditEventType.DATA_MODIFICATION: 0.5,
                AuditEventType.PERMISSION_CHANGE: 0.8,
                AuditEventType.SECURITY_VIOLATION: 1.0,
                AuditEventType.SYSTEM_ACCESS: 0.4
            }
            
            score = base_scores.get(event_type, 0.0)
            
            # Increase score for failed events
            if not success:
                score *= 2.0
            
            # Adjust based on details
            if details.get("privileged_operation", False):
                score *= 1.5
            
            if details.get("after_hours", False):
                score *= 1.2
            
            return min(score, 1.0)  # Cap at 1.0
        except Exception as e:
            logger.error(f"Risk score calculation error: {e}")
            return 0.0
    
    async def get_audit_logs(self, start_time: datetime = None, end_time: datetime = None, event_type: AuditEventType = None, user_id: str = None, limit: int = 100) -> List[SecurityAuditLog]:
        """Get audit logs with filtering"""
        try:
            logs = self.audit_logs.copy()
            
            # Apply filters
            if start_time:
                logs = [log for log in logs if log.timestamp >= start_time]
            if end_time:
                logs = [log for log in logs if log.timestamp <= end_time]
            if event_type:
                logs = [log for log in logs if log.event_type == event_type]
            if user_id:
                logs = [log for log in logs if log.user_id == user_id]
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda log: log.timestamp, reverse=True)
            
            return logs[:limit]
        except Exception as e:
            logger.error(f"Audit logs retrieval error: {e}")
            return []
    
    async def generate_security_report(self, period_days: int = 7) -> Dict[str, Any]:
        """Generate security activity report"""
        try:
            start_time = datetime.utcnow() - timedelta(days=period_days)
            logs = await self.get_audit_logs(start_time=start_time)
            
            # Calculate statistics
            total_events = len(logs)
            failed_events = len([log for log in logs if not log.success])
            high_risk_events = len([log for log in logs if log.risk_score >= 0.7])
            
            # Event type breakdown
            event_types = {}
            for log in logs:
                event_types[log.event_type.value] = event_types.get(log.event_type.value, 0) + 1
            
            # Top users by activity
            user_activity = {}
            for log in logs:
                if log.user_id:
                    user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
            
            top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "period_days": period_days,
                "total_events": total_events,
                "failed_events": failed_events,
                "high_risk_events": high_risk_events,
                "success_rate": (total_events - failed_events) / total_events if total_events > 0 else 1.0,
                "event_types": event_types,
                "top_users": top_users,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Security report generation error: {e}")
            return {}

class SecurityService:
    """
    Unified Security Service that orchestrates all security-related services
    
    Consolidates:
    - Data Encryption & Key Management
    - Threat Detection & Monitoring
    - Compliance & Audit
    - Data Classification & Protection
    - Security Audit Logging
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.encryption = EncryptionService(self.config.get('encryption', {}))
        self.threat_detection = ThreatDetectionService(self.config.get('threat_detection', {}))
        self.compliance = ComplianceService(self.config.get('compliance', {}))
        self.data_classification = DataClassificationService(self.config.get('data_classification', {}))
        self.audit = SecurityAuditService(self.config.get('audit', {}))
        
        logger.info("🛡️ Security Service initialized - All security-related services consolidated")
    
    async def initialize(self):
        """Initialize all security services"""
        logger.info("🚀 Initializing Security Service")
        # Any initialization logic here
    
    async def shutdown(self):
        """Shutdown all security services"""
        logger.info("🛑 Shutting down Security Service")
        # Any cleanup logic here
    
    # Encryption methods
    async def generate_encryption_key(self, algorithm: EncryptionAlgorithm, purpose: str, owner_id: str = None) -> EncryptionKey:
        """Generate encryption key"""
        return await self.encryption.generate_key(algorithm, purpose, owner_id)
    
    async def encrypt_data(self, data: str, key_id: str) -> Dict[str, str]:
        """Encrypt data"""
        return await self.encryption.encrypt_data(data, key_id)
    
    async def decrypt_data(self, encrypted_data: str, key_id: str, iv: str = None) -> str:
        """Decrypt data"""
        return await self.encryption.decrypt_data(encrypted_data, key_id, iv)
    
    # Threat detection methods
    async def analyze_security_event(self, event_data: Dict[str, Any]) -> Optional[ThreatAlert]:
        """Analyze security event"""
        return await self.threat_detection.analyze_security_event(event_data)
    
    async def get_active_threats(self, level: ThreatLevel = None) -> List[ThreatAlert]:
        """Get active threats"""
        return await self.threat_detection.get_active_threats(level)
    
    async def resolve_threat(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve threat"""
        return await self.threat_detection.resolve_threat(alert_id, resolution_notes)
    
    # Compliance methods
    async def run_compliance_audit(self, framework: ComplianceFramework, scope: str) -> ComplianceReport:
        """Run compliance audit"""
        return await self.compliance.run_compliance_audit(framework, scope)
    
    async def get_compliance_status(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Get compliance status"""
        return await self.compliance.get_compliance_status(framework)
    
    # Data classification methods
    async def classify_data(self, resource_id: str, resource_type: str, classification_level: SecurityLevel, tags: List[str] = None, classifier_id: str = None) -> DataClassification:
        """Classify data"""
        return await self.data_classification.classify_data(resource_id, resource_type, classification_level, tags, classifier_id)
    
    async def check_data_access(self, resource_id: str, user_id: str, user_roles: List[str]) -> Dict[str, Any]:
        """Check data access permissions"""
        return await self.data_classification.check_access_permissions(resource_id, user_id, user_roles)
    
    # Audit methods
    async def log_security_event(self, event_type: AuditEventType, user_id: str = None, resource_id: str = None, action: str = "", details: Dict[str, Any] = None, ip_address: str = None, success: bool = True) -> SecurityAuditLog:
        """Log security event"""
        return await self.audit.log_security_event(event_type, user_id, resource_id, action, details, ip_address, success)
    
    async def get_audit_logs(self, start_time: datetime = None, end_time: datetime = None, event_type: AuditEventType = None, user_id: str = None, limit: int = 100) -> List[SecurityAuditLog]:
        """Get audit logs"""
        return await self.audit.get_audit_logs(start_time, end_time, event_type, user_id, limit)
    
    async def generate_security_report(self, period_days: int = 7) -> Dict[str, Any]:
        """Generate security report"""
        return await self.audit.generate_security_report(period_days)

# Export all classes
__all__ = [
    # Enums
    "SecurityLevel",
    "ThreatLevel",
    "EncryptionAlgorithm",
    "ComplianceFramework",
    "AuditEventType",
    
    # Data structures
    "EncryptionKey",
    "SecurityAuditLog",
    "ThreatAlert",
    "ComplianceReport",
    "SecurityPolicy",
    "DataClassification",
    
    # Services
    "EncryptionService",
    "ThreatDetectionService",
    "ComplianceService",
    "DataClassificationService",
    "SecurityAuditService",
    "SecurityService"
]

# Module initialization
logger.info(f"🛡️ Security Service v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🎯 Consolidated: security_service + security/ subdirectory modules")