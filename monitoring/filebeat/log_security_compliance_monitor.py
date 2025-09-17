#!/usr/bin/env python3
"""
Log Security Compliance Monitor - Creator Economy Enterprise
==========================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from pathlib import Path
import redis.asyncio as redis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress


class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    CREATOR_PRIVACY = "creator_privacy"


class SecurityLevel(Enum):
    """Security levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ViolationType(Enum):
    """Types of security violations"""
    PII_EXPOSURE = "pii_exposure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_LEAK = "data_leak"
    ENCRYPTION_VIOLATION = "encryption_violation"
    ACCESS_CONTROL_VIOLATION = "access_control_violation"
    AUDIT_LOG_TAMPERING = "audit_log_tampering"
    RETENTION_VIOLATION = "retention_violation"
    CROSS_BORDER_VIOLATION = "cross_border_violation"
    CONSENT_VIOLATION = "consent_violation"
    ANONYMIZATION_FAILURE = "anonymization_failure"


@dataclass
class SecurityViolation:
    """Security compliance violation"""
    violation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: ViolationType = ViolationType.PII_EXPOSURE
    severity: str = "medium"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    creator_id: Optional[str] = None
    log_source: str = ""
    log_content: str = ""
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    remediation_actions: List[str] = field(default_factory=list)
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "creator_id": self.creator_id,
            "log_source": self.log_source,
            "log_content": self.log_content,
            "compliance_standards": [std.value for std in self.compliance_standards],
            "detected_patterns": self.detected_patterns,
            "risk_score": self.risk_score,
            "remediation_actions": self.remediation_actions,
            "status": self.status,
            "metadata": self.metadata
        }


@dataclass
class ComplianceRule:
    """Compliance monitoring rule"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    compliance_standard: ComplianceStandard = ComplianceStandard.GDPR
    pattern: str = ""
    violation_type: ViolationType = ViolationType.PII_EXPOSURE
    severity: str = "medium"
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def matches(self, log_content: str) -> bool:
        """Check if rule matches log content"""
        try:
            return bool(re.search(self.pattern, log_content, re.IGNORECASE))
        except re.error:
            return False


class PIIDetector:
    """Personal Identifiable Information detector"""
    
    def __init__(self):
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "uuid": r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            "api_key": r'(?i)\b(?:api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{16,})',
            "password": r'(?i)\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']+)',
            "username": r'(?i)\b(?:username|user[_-]?name|login)["\']?\s*[:=]\s*["\']?([^\s"\']+)'
        }
    
    def detect_pii(self, text: str) -> List[Tuple[str, str]]:
        """Detect PII in text"""
        findings = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append((pii_type, match.group()))
        
        return findings
    
    def anonymize_pii(self, text: str) -> str:
        """Anonymize detected PII"""
        anonymized_text = text
        
        for pii_type, pattern in self.patterns.items():
            if pii_type == "email":
                anonymized_text = re.sub(pattern, "[EMAIL_REDACTED]", anonymized_text, flags=re.IGNORECASE)
            elif pii_type == "phone":
                anonymized_text = re.sub(pattern, "[PHONE_REDACTED]", anonymized_text, flags=re.IGNORECASE)
            elif pii_type == "ssn":
                anonymized_text = re.sub(pattern, "[SSN_REDACTED]", anonymized_text, flags=re.IGNORECASE)
            elif pii_type == "credit_card":
                anonymized_text = re.sub(pattern, "[CARD_REDACTED]", anonymized_text, flags=re.IGNORECASE)
            elif pii_type == "api_key":
                anonymized_text = re.sub(pattern, r'\1[API_KEY_REDACTED]', anonymized_text, flags=re.IGNORECASE)
            elif pii_type == "password":
                anonymized_text = re.sub(pattern, r'\1[PASSWORD_REDACTED]', anonymized_text, flags=re.IGNORECASE)
        
        return anonymized_text


class LogSecurityComplianceMonitor:
    """
    Monitor conformité sécurité logs enterprise
    
    Features:
    - Log security compliance Creator Economy monitoring
    - Creator log privacy protection
    - Log compliance Creator Economy validation
    - Creator log security analytics
    - Log security Creator compliance reporting
    - Creator log security intelligence
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Redis connection for caching
        self._redis_client: Optional[redis.Redis] = None
        
        # Encryption for sensitive data
        self._encryption_key = self._generate_encryption_key()
        self._cipher_suite = Fernet(self._encryption_key)
        
        # PII detector
        self._pii_detector = PIIDetector()
        
        # Compliance state
        self._compliance_rules: Dict[str, ComplianceRule] = {}
        self._violations: Dict[str, SecurityViolation] = {}
        self._monitored_creators: Set[str] = set()
        self._blocked_ips: Set[str] = set()
        
        # Security metrics
        self._security_metrics = {
            "logs_monitored": 0,
            "violations_detected": 0,
            "pii_instances_found": 0,
            "pii_instances_anonymized": 0,
            "compliance_checks": 0,
            "encryption_operations": 0,
            "access_denials": 0,
            "security_alerts": 0
        }
        
        # Compliance configuration
        self._compliance_config = {
            "enable_pii_detection": True,
            "enable_auto_anonymization": True,
            "enable_access_control": True,
            "enable_encryption": True,
            "retention_days": 2555,  # 7 years for compliance
            "alert_threshold": 0.7,  # Risk score threshold
            "max_violations_per_hour": 10,
            "blocked_countries": ["CN", "RU", "KP"],  # Example blocked countries
            "allowed_ip_ranges": []
        }
        
        # Initialize components
        self._initialized = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for security monitor"""
        logger = logging.getLogger(f"{__name__}.LogSecurityComplianceMonitor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        password = self.config.get("encryption_password", "default_password").encode()
        salt = self.config.get("encryption_salt", "default_salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def initialize(self) -> bool:
        """Initialize security compliance monitor"""
        try:
            self.logger.info("🛡️ Initializing Log Security Compliance Monitor...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Load compliance rules
            await self._load_compliance_rules()
            
            # Load cached data
            await self._load_cached_data()
            
            # Validate configuration
            self._validate_configuration()
            
            self._initialized = True
            self.logger.info("✅ Log Security Compliance Monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize security monitor: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            redis_config = self.config.get("redis", {})
            self._redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                decode_responses=True
            )
            await self._redis_client.ping()
            self.logger.info("✅ Redis connection established")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis connection failed: {e}")
            self._redis_client = None
    
    async def _load_compliance_rules(self):
        """Load compliance monitoring rules"""
        try:
            # Default GDPR rules
            gdpr_rules = [
                ComplianceRule(
                    name="Email Detection",
                    description="Detect email addresses in logs",
                    compliance_standard=ComplianceStandard.GDPR,
                    pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    violation_type=ViolationType.PII_EXPOSURE,
                    severity="high"
                ),
                ComplianceRule(
                    name="Phone Number Detection",
                    description="Detect phone numbers in logs",
                    compliance_standard=ComplianceStandard.GDPR,
                    pattern=r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                    violation_type=ViolationType.PII_EXPOSURE,
                    severity="high"
                ),
                ComplianceRule(
                    name="API Key Exposure",
                    description="Detect exposed API keys",
                    compliance_standard=ComplianceStandard.CREATOR_PRIVACY,
                    pattern=r'(?i)\b(?:api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{16,})',
                    violation_type=ViolationType.DATA_LEAK,
                    severity="critical"
                ),
                ComplianceRule(
                    name="Password Exposure",
                    description="Detect exposed passwords",
                    compliance_standard=ComplianceStandard.CREATOR_PRIVACY,
                    pattern=r'(?i)\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']+)',
                    violation_type=ViolationType.DATA_LEAK,
                    severity="critical"
                )
            ]
            
            # CCPA rules
            ccpa_rules = [
                ComplianceRule(
                    name="California Resident Data",
                    description="Detect California resident data processing",
                    compliance_standard=ComplianceStandard.CCPA,
                    pattern=r'(?i)\b(california|ca)\b.*\b(resident|user|customer)\b',
                    violation_type=ViolationType.CONSENT_VIOLATION,
                    severity="medium"
                )
            ]
            
            # Load all rules
            all_rules = gdpr_rules + ccpa_rules
            
            # Add custom rules from configuration
            custom_rules = self.config.get("compliance_rules", [])
            for rule_config in custom_rules:
                try:
                    rule = ComplianceRule(
                        name=rule_config.get("name", "Custom Rule"),
                        description=rule_config.get("description", ""),
                        compliance_standard=ComplianceStandard(rule_config.get("standard", "gdpr")),
                        pattern=rule_config.get("pattern", ""),
                        violation_type=ViolationType(rule_config.get("violation_type", "pii_exposure")),
                        severity=rule_config.get("severity", "medium")
                    )
                    all_rules.append(rule)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"⚠️ Invalid custom rule configuration: {e}")
            
            # Store rules
            for rule in all_rules:
                self._compliance_rules[rule.rule_id] = rule
            
            self.logger.info(f"📋 Loaded {len(self._compliance_rules)} compliance rules")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading compliance rules: {e}")
    
    async def _load_cached_data(self):
        """Load cached security data"""
        if not self._redis_client:
            return
            
        try:
            # Load violations cache
            violation_keys = await self._redis_client.keys("security:violation:*")
            for key in violation_keys:
                violation_data = await self._redis_client.get(key)
                if violation_data:
                    data = json.loads(violation_data)
                    violation = self._dict_to_violation(data)
                    self._violations[violation.violation_id] = violation
            
            # Load blocked IPs
            blocked_ips = await self._redis_client.smembers("security:blocked_ips")
            self._blocked_ips.update(blocked_ips)
            
            # Load monitored creators
            monitored_creators = await self._redis_client.smembers("security:monitored_creators")
            self._monitored_creators.update(monitored_creators)
            
            self.logger.info(f"🔒 Loaded {len(self._violations)} violations and {len(self._blocked_ips)} blocked IPs")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load cached security data: {e}")
    
    def _dict_to_violation(self, data: Dict[str, Any]) -> SecurityViolation:
        """Convert dictionary to SecurityViolation object"""
        return SecurityViolation(
            violation_id=data["violation_id"],
            violation_type=ViolationType(data["violation_type"]),
            severity=data["severity"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            creator_id=data.get("creator_id"),
            log_source=data.get("log_source", ""),
            log_content=data.get("log_content", ""),
            compliance_standards=[ComplianceStandard(std) for std in data.get("compliance_standards", [])],
            detected_patterns=data.get("detected_patterns", []),
            risk_score=data.get("risk_score", 0.0),
            remediation_actions=data.get("remediation_actions", []),
            status=data.get("status", "open"),
            metadata=data.get("metadata", {})
        )
    
    def _validate_configuration(self):
        """Validate security configuration"""
        required_config = ["output_path", "compliance_standards"]
        for key in required_config:
            if key not in self.config:
                self.logger.warning(f"⚠️ Missing configuration key: {key}")
    
    async def monitor_log_entry(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor a single log entry for security compliance"""
        try:
            if not self._initialized:
                await self.initialize()
            
            log_content = log_data.get("message", "")
            log_source = log_data.get("source", "unknown")
            creator_id = log_data.get("creator_id")
            timestamp = datetime.utcnow()
            
            monitoring_result = {
                "compliant": True,
                "violations": [],
                "pii_detected": [],
                "anonymized_content": log_content,
                "risk_score": 0.0,
                "recommendations": []
            }
            
            # Check access control
            if not await self._check_access_control(log_data):
                monitoring_result["compliant"] = False
                monitoring_result["violations"].append("Access control violation")
            
            # Detect PII
            if self._compliance_config["enable_pii_detection"]:
                pii_findings = self._pii_detector.detect_pii(log_content)
                monitoring_result["pii_detected"] = pii_findings
                
                if pii_findings:
                    self._security_metrics["pii_instances_found"] += len(pii_findings)
                    
                    # Auto-anonymize if enabled
                    if self._compliance_config["enable_auto_anonymization"]:
                        monitoring_result["anonymized_content"] = self._pii_detector.anonymize_pii(log_content)
                        self._security_metrics["pii_instances_anonymized"] += len(pii_findings)
            
            # Check compliance rules
            violations = await self._check_compliance_rules(log_content, log_source, creator_id)
            monitoring_result["violations"].extend([v.to_dict() for v in violations])
            
            if violations:
                monitoring_result["compliant"] = False
                
                # Calculate risk score
                risk_score = self._calculate_risk_score(violations, pii_findings)
                monitoring_result["risk_score"] = risk_score
                
                # Generate recommendations
                recommendations = self._generate_recommendations(violations, pii_findings)
                monitoring_result["recommendations"] = recommendations
                
                # Cache violations
                for violation in violations:
                    await self._cache_violation(violation)
                    self._violations[violation.violation_id] = violation
                
                # Check if alert threshold is reached
                if risk_score >= self._compliance_config["alert_threshold"]:
                    await self._trigger_security_alert(violations, risk_score)
            
            # Encrypt sensitive data if required
            if self._compliance_config["enable_encryption"] and monitoring_result["pii_detected"]:
                monitoring_result["encrypted_content"] = await self._encrypt_sensitive_data(log_content)
                self._security_metrics["encryption_operations"] += 1
            
            # Log compliance check
            await self._log_compliance_check(log_data, monitoring_result)
            
            self._security_metrics["logs_monitored"] += 1
            self._security_metrics["compliance_checks"] += 1
            
            return monitoring_result
            
        except Exception as e:
            self.logger.error(f"❌ Error monitoring log entry: {e}")
            return {"compliant": False, "error": str(e)}
    
    async def _check_access_control(self, log_data: Dict[str, Any]) -> bool:
        """Check access control compliance"""
        try:
            if not self._compliance_config["enable_access_control"]:
                return True
            
            # Check IP address restrictions
            client_ip = log_data.get("client_ip")
            if client_ip:
                # Check blocked IPs
                if client_ip in self._blocked_ips:
                    self._security_metrics["access_denials"] += 1
                    return False
                
                # Check IP address validity
                try:
                    ip = ipaddress.ip_address(client_ip)
                    
                    # Check if IP is in allowed ranges
                    allowed_ranges = self._compliance_config.get("allowed_ip_ranges", [])
                    if allowed_ranges:
                        allowed = False
                        for range_str in allowed_ranges:
                            try:
                                network = ipaddress.ip_network(range_str)
                                if ip in network:
                                    allowed = True
                                    break
                            except ValueError:
                                continue
                        
                        if not allowed:
                            self._security_metrics["access_denials"] += 1
                            return False
                
                except ValueError:
                    # Invalid IP address
                    return False
            
            # Check creator access
            creator_id = log_data.get("creator_id")
            if creator_id and creator_id in self._monitored_creators:
                # Additional monitoring for flagged creators
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking access control: {e}")
            return False
    
    async def _check_compliance_rules(self, log_content: str, log_source: str, creator_id: Optional[str]) -> List[SecurityViolation]:
        """Check log content against compliance rules"""
        violations = []
        
        try:
            for rule in self._compliance_rules.values():
                if not rule.enabled:
                    continue
                
                if rule.matches(log_content):
                    violation = SecurityViolation(
                        violation_type=rule.violation_type,
                        severity=rule.severity,
                        creator_id=creator_id,
                        log_source=log_source,
                        log_content=log_content,
                        compliance_standards=[rule.compliance_standard],
                        detected_patterns=[rule.pattern],
                        metadata={
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "rule_description": rule.description
                        }
                    )
                    violations.append(violation)
                    self._security_metrics["violations_detected"] += 1
            
            return violations
            
        except Exception as e:
            self.logger.error(f"❌ Error checking compliance rules: {e}")
            return []
    
    def _calculate_risk_score(self, violations: List[SecurityViolation], pii_findings: List[Tuple[str, str]]) -> float:
        """Calculate risk score based on violations and PII findings"""
        try:
            risk_score = 0.0
            
            # Base score for PII findings
            risk_score += len(pii_findings) * 0.1
            
            # Score based on violations
            for violation in violations:
                if violation.severity == "critical":
                    risk_score += 0.4
                elif violation.severity == "high":
                    risk_score += 0.3
                elif violation.severity == "medium":
                    risk_score += 0.2
                elif violation.severity == "low":
                    risk_score += 0.1
            
            # Cap at 1.0
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating risk score: {e}")
            return 0.0
    
    def _generate_recommendations(self, violations: List[SecurityViolation], pii_findings: List[Tuple[str, str]]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        try:
            if pii_findings:
                recommendations.append("Enable automatic PII anonymization")
                recommendations.append("Implement data masking for sensitive fields")
                recommendations.append("Review data collection practices")
            
            violation_types = set(v.violation_type for v in violations)
            
            if ViolationType.PII_EXPOSURE in violation_types:
                recommendations.append("Enhance PII detection and removal processes")
                recommendations.append("Implement field-level encryption for sensitive data")
            
            if ViolationType.DATA_LEAK in violation_types:
                recommendations.append("Review and secure API key management")
                recommendations.append("Implement secrets management solution")
                recommendations.append("Audit access controls and permissions")
            
            if ViolationType.UNAUTHORIZED_ACCESS in violation_types:
                recommendations.append("Strengthen authentication mechanisms")
                recommendations.append("Implement IP whitelisting")
                recommendations.append("Enable multi-factor authentication")
            
            if ViolationType.ENCRYPTION_VIOLATION in violation_types:
                recommendations.append("Implement end-to-end encryption")
                recommendations.append("Use encryption at rest for sensitive data")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error generating recommendations: {e}")
            return []
    
    async def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"❌ Error encrypting data: {e}")
            return data
    
    async def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"❌ Error decrypting data: {e}")
            return encrypted_data
    
    async def _trigger_security_alert(self, violations: List[SecurityViolation], risk_score: float):
        """Trigger security alert for high-risk violations"""
        try:
            alert_data = {
                "alert_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "alert_type": "security_compliance_violation",
                "risk_score": risk_score,
                "violation_count": len(violations),
                "violations": [v.to_dict() for v in violations],
                "severity": "high" if risk_score >= 0.8 else "medium"
            }
            
            # Log alert
            self.logger.warning(f"🚨 SECURITY ALERT: Risk score {risk_score:.2f} with {len(violations)} violations")
            
            # Cache alert
            if self._redis_client:
                alert_key = f"security:alert:{alert_data['alert_id']}"
                await self._redis_client.setex(
                    alert_key,
                    86400 * 30,  # 30 days
                    json.dumps(alert_data)
                )
            
            self._security_metrics["security_alerts"] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering security alert: {e}")
    
    async def _cache_violation(self, violation: SecurityViolation):
        """Cache security violation"""
        if not self._redis_client:
            return
        
        try:
            violation_key = f"security:violation:{violation.violation_id}"
            await self._redis_client.setex(
                violation_key,
                86400 * self._compliance_config["retention_days"],
                json.dumps(violation.to_dict())
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cache violation: {e}")
    
    async def _log_compliance_check(self, log_data: Dict[str, Any], monitoring_result: Dict[str, Any]):
        """Log compliance check result"""
        try:
            compliance_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "log_type": "security_compliance_check",
                "original_log": log_data,
                "monitoring_result": monitoring_result,
                "processor": "LogSecurityComplianceMonitor",
                "version": "1.0.0"
            }
            
            # Log to structured format
            log_format = self.config.get("log_format", "json")
            if log_format == "json":
                self.logger.info(json.dumps(compliance_log))
            else:
                compliant = "COMPLIANT" if monitoring_result["compliant"] else "NON_COMPLIANT"
                self.logger.info(f"COMPLIANCE_CHECK: {compliant} | Risk: {monitoring_result['risk_score']:.2f} | Violations: {len(monitoring_result['violations'])}")
                
        except Exception as e:
            self.logger.error(f"❌ Error logging compliance check: {e}")
    
    async def add_blocked_ip(self, ip_address: str, reason: str = "Security violation") -> bool:
        """Add IP address to blocked list"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)
            
            self._blocked_ips.add(ip_address)
            
            # Cache blocked IP
            if self._redis_client:
                await self._redis_client.sadd("security:blocked_ips", ip_address)
                
                # Log block reason
                block_data = {
                    "ip_address": ip_address,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                    "blocked_by": "LogSecurityComplianceMonitor"
                }
                
                block_key = f"security:ip_block:{ip_address}"
                await self._redis_client.setex(
                    block_key,
                    86400 * 30,  # 30 days
                    json.dumps(block_data)
                )
            
            self.logger.info(f"🚫 Blocked IP address: {ip_address} - {reason}")
            return True
            
        except ValueError:
            self.logger.error(f"❌ Invalid IP address: {ip_address}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error blocking IP address: {e}")
            return False
    
    async def remove_blocked_ip(self, ip_address: str) -> bool:
        """Remove IP address from blocked list"""
        try:
            self._blocked_ips.discard(ip_address)
            
            if self._redis_client:
                await self._redis_client.srem("security:blocked_ips", ip_address)
                block_key = f"security:ip_block:{ip_address}"
                await self._redis_client.delete(block_key)
            
            self.logger.info(f"✅ Unblocked IP address: {ip_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error unblocking IP address: {e}")
            return False
    
    async def add_monitored_creator(self, creator_id: str, reason: str = "Enhanced monitoring") -> bool:
        """Add creator to enhanced monitoring list"""
        try:
            self._monitored_creators.add(creator_id)
            
            if self._redis_client:
                await self._redis_client.sadd("security:monitored_creators", creator_id)
                
                # Log monitoring reason
                monitor_data = {
                    "creator_id": creator_id,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                    "added_by": "LogSecurityComplianceMonitor"
                }
                
                monitor_key = f"security:creator_monitor:{creator_id}"
                await self._redis_client.setex(
                    monitor_key,
                    86400 * 90,  # 90 days
                    json.dumps(monitor_data)
                )
            
            self.logger.info(f"👁️ Added creator to monitoring: {creator_id} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error adding creator to monitoring: {e}")
            return False
    
    async def get_compliance_report(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter violations by date range
            violations_in_range = [
                v for v in self._violations.values()
                if start_date <= v.timestamp <= end_date
            ]
            
            # Analyze violations by type
            violation_counts = {}
            for violation in violations_in_range:
                v_type = violation.violation_type.value
                violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
            
            # Analyze by severity
            severity_counts = {}
            for violation in violations_in_range:
                severity = violation.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Analyze by compliance standard
            standard_counts = {}
            for violation in violations_in_range:
                for standard in violation.compliance_standards:
                    std_name = standard.value
                    standard_counts[std_name] = standard_counts.get(std_name, 0) + 1
            
            # Calculate compliance score
            total_checks = self._security_metrics["compliance_checks"]
            total_violations = len(violations_in_range)
            compliance_score = ((total_checks - total_violations) / total_checks * 100) if total_checks > 0 else 100
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "compliance_score": round(compliance_score, 2),
                "total_violations": total_violations,
                "violations_by_type": violation_counts,
                "violations_by_severity": severity_counts,
                "violations_by_standard": standard_counts,
                "security_metrics": self._security_metrics.copy(),
                "blocked_ips_count": len(self._blocked_ips),
                "monitored_creators_count": len(self._monitored_creators),
                "active_rules_count": sum(1 for rule in self._compliance_rules.values() if rule.enabled),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating compliance report: {e}")
            return {"error": str(e)}
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security monitoring metrics"""
        metrics = self._security_metrics.copy()
        metrics["cached_violations"] = len(self._violations)
        metrics["blocked_ips"] = len(self._blocked_ips)
        metrics["monitored_creators"] = len(self._monitored_creators)
        metrics["active_rules"] = sum(1 for rule in self._compliance_rules.values() if rule.enabled)
        metrics["uptime"] = "active"
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "redis_connected": self._redis_client is not None,
            "metrics": await self.get_security_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self._redis_client:
            try:
                await self._redis_client.ping()
                health["redis_status"] = "connected"
            except:
                health["redis_status"] = "disconnected"
        
        return health
    
    async def shutdown(self):
        """Shutdown security monitor gracefully"""
        self.logger.info("🔄 Shutting down Log Security Compliance Monitor...")
        
        if self._redis_client:
            await self._redis_client.close()
        
        self.logger.info("✅ Security monitor shutdown complete")


# Example usage and testing
async def main():
    """Main function for testing"""
    monitor = LogSecurityComplianceMonitor({
        "output_path": "/tmp/security_logs",
        "compliance_standards": ["gdpr", "ccpa"],
        "log_format": "json",
        "redis": {"host": "localhost", "port": 6379}
    })
    
    # Test log entry with PII
    test_log = {
        "message": "User john.doe@example.com logged in with password secret123",
        "source": "auth_service",
        "creator_id": "creator_123",
        "client_ip": "192.168.1.100",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    result = await monitor.monitor_log_entry(test_log)
    print(f"Monitoring result: {result}")
    
    # Get compliance report
    report = await monitor.get_compliance_report()
    print(f"Compliance report: {report}")
    
    # Health check
    health = await monitor.health_check()
    print(f"Health check: {health}")
    
    await monitor.shutdown()


if __name__ == "__main__":
    asyncio.run(main())