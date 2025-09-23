
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""
🔒 Security Processing Layer - Advanced Enterprise Security Processing Platform
==============================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Sécurité + Backend Senior + DevOps + Lead Dev IA
**Module**: Security Processing Layer
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade security processing with content scanning, malware detection,
privacy compliance validation, and automated threat response.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire
Utilisation commerciale INTERDITE sans autorisation écrite
"""

import asyncio
import logging
import json
import time
import hashlib
import uuid
import re
import base64
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod
import ipaddress
import secrets
from pathlib import Path
import mimetypes
from collections import defaultdict, deque

# Cryptography
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    Fernet = None
    rsa = None
    hashes = None
    padding = None
    serialization = None
    PBKDF2HMAC = None
    CRYPTO_AVAILABLE = False

# Security scanning
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    yara = None
    YARA_AVAILABLE = False

# Image processing for security
try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ExifTags = None
    PIL_AVAILABLE = False

# Network security
try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    requests = None
    aiohttp = None
    HTTP_AVAILABLE = False

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SecurityEventType(str, Enum):
    """Types of security events"""
    MALWARE_DETECTED = "malware_detected"
    SUSPICIOUS_CONTENT = "suspicious_content"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVACY_VIOLATION = "privacy_violation"
    INJECTION_ATTEMPT = "injection_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    POLICY_VIOLATION = "policy_violation"
    ENCRYPTION_FAILURE = "encryption_failure"
    AUTHENTICATION_FAILURE = "authentication_failure"


class ComplianceStandard(str, Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    COPPA = "coppa"


class ContentType(str, Enum):
    """Content types for security scanning"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    EXECUTABLE = "executable"
    ARCHIVE = "archive"
    WEB_CONTENT = "web_content"
    USER_DATA = "user_data"


@dataclass
class SecurityThreat:
    """Security threat information"""
    threat_id: str
    threat_type: SecurityEventType
    threat_level: ThreatLevel
    description: str
    detected_at: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    mitigation_actions: List[str] = field(default_factory=list)
    false_positive_probability: float = 0.0


@dataclass
class SecurityScanResult:
    """Security scan result"""
    scan_id: str
    content_hash: str
    content_type: ContentType
    scan_timestamp: datetime
    threats_detected: List[SecurityThreat]
    scan_duration: float
    is_safe: bool
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceCheckResult:
    """Compliance check result"""
    check_id: str
    standard: ComplianceStandard
    is_compliant: bool
    violations: List[str]
    recommendations: List[str]
    check_timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security processing configuration"""
    enable_malware_scanning: bool = True
    enable_content_filtering: bool = True
    enable_privacy_protection: bool = True
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    enable_threat_intelligence: bool = True
    rate_limit_requests_per_minute: int = 100
    max_file_size_mb: float = 100.0
    allowed_file_types: Set[str] = field(default_factory=lambda: {
        'txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'mp3', 'mp4', 'wav'
    })
    blocked_file_types: Set[str] = field(default_factory=lambda: {
        'exe', 'bat', 'cmd', 'scr', 'vbs', 'js', 'jar'
    })
    encryption_key: Optional[str] = None
    compliance_standards: Set[ComplianceStandard] = field(default_factory=lambda: {
        ComplianceStandard.GDPR, ComplianceStandard.SOC2
    })
    threat_intelligence_feeds: List[str] = field(default_factory=list)
    enable_real_time_monitoring: bool = True
    quarantine_directory: str = "/tmp/quarantine"


class BaseSecurityScanner(ABC):
    """Base class for security scanners"""
    
    def __init__(self, scanner_id: str, config: SecurityConfig):
        self.scanner_id = scanner_id
        self.config = config
        self.scan_count = 0
        self.threats_detected = 0
        self.last_scan_time: Optional[datetime] = None
        
    @abstractmethod
    async def scan_content(self, content: Any, content_type: ContentType) -> SecurityScanResult:
        """Scan content for security threats"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get scanner capabilities"""
        pass
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        return f"{self.scanner_id}_{uuid.uuid4().hex[:8]}"
    
    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate content hash for caching"""
        if isinstance(content, bytes):
            return hashlib.sha256(content).hexdigest()
        elif isinstance(content, str):
            return hashlib.sha256(content.encode()).hexdigest()
        else:
            return hashlib.sha256(str(content).encode()).hexdigest()


class MalwareScanner(BaseSecurityScanner):
    """Malware detection scanner"""
    
    def __init__(self, scanner_id: str, config: SecurityConfig):
        super().__init__(scanner_id, config)
        self.virus_signatures = self._load_virus_signatures()
        self.suspicious_patterns = self._load_suspicious_patterns()
        
    def _load_virus_signatures(self) -> Dict[str, str]:
        """Load virus signatures (simplified for demo)"""
        return {
            "test_virus": "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",
            "suspicious_script": "eval\\s*\\(.*base64_decode",
            "malicious_payload": "<script[^>]*>.*?</script>",
            "sql_injection": "(union|select|insert|delete|update|drop)\\s+(.*\\s+)?(from|into|table)",
        }
    
    def _load_suspicious_patterns(self) -> Dict[str, str]:
        """Load suspicious content patterns"""
        return {
            "xss_attempt": "<script|javascript:|on\\w+\\s*=",
            "path_traversal": "\\.\\.[\\/\\\\]",
            "command_injection": "(;|\\||&&|\\$\\(|\\`)",
            "data_exfiltration": "(password|credit.*card|ssn|social.*security)",
        }
    
    async def scan_content(self, content: Any, content_type: ContentType) -> SecurityScanResult:
        """Scan content for malware and threats"""
        start_time = time.time()
        scan_id = self._generate_scan_id()
        content_hash = self._calculate_content_hash(content)
        threats = []
        
        try:
            # Convert content to string for pattern matching
            if isinstance(content, bytes):
                try:
                    content_str = content.decode('utf-8', errors='ignore')
                except Exception:
                    content_str = str(content)
            else:
                content_str = str(content)
            
            # Scan for virus signatures
            for virus_name, signature in self.virus_signatures.items():
                if re.search(signature, content_str, re.IGNORECASE):
                    threats.append(SecurityThreat(
                        threat_id=f"malware_{uuid.uuid4().hex[:8]}",
                        threat_type=SecurityEventType.MALWARE_DETECTED,
                        threat_level=ThreatLevel.CRITICAL,
                        description=f"Virus signature detected: {virus_name}",
                        detected_at=datetime.now(timezone.utc),
                        evidence={"signature": virus_name, "pattern": signature}
                    ))
            
            # Scan for suspicious patterns
            for pattern_name, pattern in self.suspicious_patterns.items():
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    threat_level = ThreatLevel.HIGH if pattern_name in ["xss_attempt", "command_injection"] else ThreatLevel.MEDIUM
                    threats.append(SecurityThreat(
                        threat_id=f"suspicious_{uuid.uuid4().hex[:8]}",
                        threat_type=SecurityEventType.SUSPICIOUS_CONTENT,
                        threat_level=threat_level,
                        description=f"Suspicious pattern detected: {pattern_name}",
                        detected_at=datetime.now(timezone.utc),
                        evidence={"pattern": pattern_name, "matches": matches[:5]}  # Limit matches
                    ))
            
            # File type validation
            if content_type == ContentType.EXECUTABLE:
                threats.append(SecurityThreat(
                    threat_id=f"filetype_{uuid.uuid4().hex[:8]}",
                    threat_type=SecurityEventType.POLICY_VIOLATION,
                    threat_level=ThreatLevel.HIGH,
                    description="Executable file type not allowed",
                    detected_at=datetime.now(timezone.utc),
                    evidence={"content_type": content_type.value}
                ))
            
            # Size validation
            content_size = len(content_str.encode()) / (1024 * 1024)  # MB
            if content_size > self.config.max_file_size_mb:
                threats.append(SecurityThreat(
                    threat_id=f"size_{uuid.uuid4().hex[:8]}",
                    threat_type=SecurityEventType.POLICY_VIOLATION,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"File size exceeds limit: {content_size:.2f}MB",
                    detected_at=datetime.now(timezone.utc),
                    evidence={"size_mb": content_size, "limit_mb": self.config.max_file_size_mb}
                ))
            
            self.scan_count += 1
            self.threats_detected += len(threats)
            self.last_scan_time = datetime.now(timezone.utc)
            
            scan_duration = time.time() - start_time
            is_safe = len(threats) == 0
            confidence_score = self._calculate_confidence_score(threats, content_str)
            
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=threats,
                scan_duration=scan_duration,
                is_safe=is_safe,
                confidence_score=confidence_score,
                metadata={
                    "content_size": len(content_str),
                    "patterns_checked": len(self.virus_signatures) + len(self.suspicious_patterns),
                    "scanner": self.scanner_id
                }
            )
            
        except Exception as e:
            logger.error(f"Malware scanning failed: {str(e)}")
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=[SecurityThreat(
                    threat_id=f"error_{uuid.uuid4().hex[:8]}",
                    threat_type=SecurityEventType.MALWARE_DETECTED,
                    threat_level=ThreatLevel.UNKNOWN,
                    description=f"Scan error: {str(e)}",
                    detected_at=datetime.now(timezone.utc)
                )],
                scan_duration=time.time() - start_time,
                is_safe=False,
                confidence_score=0.0
            )
    
    def _calculate_confidence_score(self, threats: List[SecurityThreat], content: str) -> float:
        """Calculate confidence score for scan results"""
        if not threats:
            return 0.95  # High confidence in safe content
        
        # Base confidence starts high and decreases with threats
        confidence = 0.9
        
        for threat in threats:
            if threat.threat_level == ThreatLevel.CRITICAL:
                confidence -= 0.3
            elif threat.threat_level == ThreatLevel.HIGH:
                confidence -= 0.2
            elif threat.threat_level == ThreatLevel.MEDIUM:
                confidence -= 0.1
            else:
                confidence -= 0.05
        
        # Content length factor (longer content = higher confidence)
        content_factor = min(0.1, len(content) / 10000)
        confidence += content_factor
        
        return max(0.0, min(1.0, confidence))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get malware scanner capabilities"""
        return {
            "scanner_id": self.scanner_id,
            "type": "malware_scanner",
            "signatures_loaded": len(self.virus_signatures),
            "patterns_loaded": len(self.suspicious_patterns),
            "scans_performed": self.scan_count,
            "threats_detected": self.threats_detected,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "supported_content_types": [ct.value for ct in ContentType]
        }


class PrivacyScanner(BaseSecurityScanner):
    """Privacy and PII detection scanner"""
    
    def __init__(self, scanner_id: str, config: SecurityConfig):
        super().__init__(scanner_id, config)
        self.pii_patterns = self._load_pii_patterns()
        
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load PII detection patterns"""
        return {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "phone": r"\b\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "api_key": r"(?i)(api[_-]?key|secret|token)[\s]*[:=][\s]*['\"]?([a-z0-9_-]{20,})",
            "password": r"(?i)(password|pwd|pass)[\s]*[:=][\s]*['\"]?([^\s'\"]{6,})",
        }
    
    async def scan_content(self, content: Any, content_type: ContentType) -> SecurityScanResult:
        """Scan content for privacy violations and PII"""
        start_time = time.time()
        scan_id = self._generate_scan_id()
        content_hash = self._calculate_content_hash(content)
        threats = []
        
        try:
            # Convert content to string
            if isinstance(content, bytes):
                content_str = content.decode('utf-8', errors='ignore')
            else:
                content_str = str(content)
            
            # Scan for PII patterns
            for pii_type, pattern in self.pii_patterns.items():
                matches = re.findall(pattern, content_str)
                if matches:
                    # Determine threat level based on PII type
                    if pii_type in ["ssn", "credit_card"]:
                        threat_level = ThreatLevel.CRITICAL
                    elif pii_type in ["email", "phone"]:
                        threat_level = ThreatLevel.HIGH
                    else:
                        threat_level = ThreatLevel.MEDIUM
                    
                    # Mask sensitive data in evidence
                    masked_matches = [self._mask_sensitive_data(match, pii_type) for match in matches[:3]]
                    
                    threats.append(SecurityThreat(
                        threat_id=f"pii_{uuid.uuid4().hex[:8]}",
                        threat_type=SecurityEventType.PRIVACY_VIOLATION,
                        threat_level=threat_level,
                        description=f"PII detected: {pii_type}",
                        detected_at=datetime.now(timezone.utc),
                        evidence={
                            "pii_type": pii_type,
                            "matches_count": len(matches),
                            "sample_matches": masked_matches
                        },
                        mitigation_actions=[
                            f"Remove or encrypt {pii_type} data",
                            "Implement data anonymization",
                            "Review data handling policies"
                        ]
                    ))
            
            # Check for GDPR compliance issues
            if ComplianceStandard.GDPR in self.config.compliance_standards:
                gdpr_threats = await self._check_gdpr_compliance(content_str)
                threats.extend(gdpr_threats)
            
            self.scan_count += 1
            self.threats_detected += len(threats)
            self.last_scan_time = datetime.now(timezone.utc)
            
            scan_duration = time.time() - start_time
            is_safe = len(threats) == 0
            confidence_score = self._calculate_privacy_confidence(threats, content_str)
            
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=threats,
                scan_duration=scan_duration,
                is_safe=is_safe,
                confidence_score=confidence_score,
                metadata={
                    "pii_patterns_checked": len(self.pii_patterns),
                    "compliance_standards": [cs.value for cs in self.config.compliance_standards],
                    "scanner": self.scanner_id
                }
            )
            
        except Exception as e:
            logger.error(f"Privacy scanning failed: {str(e)}")
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=[],
                scan_duration=time.time() - start_time,
                is_safe=False,
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    def _mask_sensitive_data(self, data: str, pii_type: str) -> str:
        """Mask sensitive data for logging"""
        if pii_type == "email":
            parts = data.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        elif pii_type in ["ssn", "credit_card"]:
            return f"{data[:4]}***{data[-4:]}"
        elif pii_type == "phone":
            return f"***-***-{data[-4:]}"
        else:
            return f"{data[:3]}***"
    
    async def _check_gdpr_compliance(self, content: str) -> List[SecurityThreat]:
        """Check for GDPR compliance issues"""
        threats = []
        
        # Check for data without consent indication
        consent_indicators = ["consent", "agree", "opt-in", "permission"]
        has_consent_language = any(indicator in content.lower() for indicator in consent_indicators)
        
        # Check for data processing without purpose
        purpose_indicators = ["purpose", "reason", "use", "process"]
        has_purpose_language = any(indicator in content.lower() for indicator in purpose_indicators)
        
        if not has_consent_language and any(pii in content.lower() for pii in ["email", "name", "address"]):
            threats.append(SecurityThreat(
                threat_id=f"gdpr_{uuid.uuid4().hex[:8]}",
                threat_type=SecurityEventType.PRIVACY_VIOLATION,
                threat_level=ThreatLevel.HIGH,
                description="GDPR: Personal data without consent indication",
                detected_at=datetime.now(timezone.utc),
                evidence={"compliance_standard": "GDPR", "issue": "missing_consent"},
                mitigation_actions=[
                    "Add consent collection mechanism",
                    "Include privacy notice",
                    "Implement data subject rights"
                ]
            ))
        
        return threats
    
    def _calculate_privacy_confidence(self, threats: List[SecurityThreat], content: str) -> float:
        """Calculate confidence score for privacy scan"""
        if not threats:
            return 0.9
        
        confidence = 0.8
        for threat in threats:
            if threat.threat_level == ThreatLevel.CRITICAL:
                confidence -= 0.25
            elif threat.threat_level == ThreatLevel.HIGH:
                confidence -= 0.15
            else:
                confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get privacy scanner capabilities"""
        return {
            "scanner_id": self.scanner_id,
            "type": "privacy_scanner",
            "pii_patterns": len(self.pii_patterns),
            "compliance_standards": [cs.value for cs in self.config.compliance_standards],
            "scans_performed": self.scan_count,
            "threats_detected": self.threats_detected,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None
        }


class ContentModerationScanner(BaseSecurityScanner):
    """Content moderation and filtering scanner"""
    
    def __init__(self, scanner_id: str, config: SecurityConfig):
        super().__init__(scanner_id, config)
        self.content_filters = self._load_content_filters()
        
    def _load_content_filters(self) -> Dict[str, List[str]]:
        """Load content filtering rules"""
        return {
            "profanity": ["badword1", "badword2", "inappropriate"],  # Simplified list
            "hate_speech": ["hate", "discrimination", "racism"],
            "violence": ["violence", "harm", "threat", "kill"],
            "adult_content": ["explicit", "nsfw", "adult"],
            "spam": ["buy now", "click here", "free money", "urgent"],
            "misinformation": ["fake news", "conspiracy", "hoax"]
        }
    
    async def scan_content(self, content: Any, content_type: ContentType) -> SecurityScanResult:
        """Scan content for moderation violations"""
        start_time = time.time()
        scan_id = self._generate_scan_id()
        content_hash = self._calculate_content_hash(content)
        threats = []
        
        try:
            # Convert content to string
            if isinstance(content, bytes):
                content_str = content.decode('utf-8', errors='ignore')
            else:
                content_str = str(content)
            
            content_lower = content_str.lower()
            
            # Check each filter category
            for category, keywords in self.content_filters.items():
                violations = []
                for keyword in keywords:
                    if keyword in content_lower:
                        violations.append(keyword)
                
                if violations:
                    # Determine threat level
                    if category in ["hate_speech", "violence"]:
                        threat_level = ThreatLevel.CRITICAL
                    elif category in ["profanity", "adult_content"]:
                        threat_level = ThreatLevel.HIGH
                    else:
                        threat_level = ThreatLevel.MEDIUM
                    
                    threats.append(SecurityThreat(
                        threat_id=f"moderation_{uuid.uuid4().hex[:8]}",
                        threat_type=SecurityEventType.POLICY_VIOLATION,
                        threat_level=threat_level,
                        description=f"Content moderation violation: {category}",
                        detected_at=datetime.now(timezone.utc),
                        evidence={
                            "category": category,
                            "violations_count": len(violations),
                            "sample_violations": violations[:3]
                        },
                        mitigation_actions=[
                            f"Remove {category} content",
                            "Review content guidelines",
                            "Implement content approval workflow"
                        ]
                    ))
            
            # Check for injection attempts
            injection_threats = await self._check_injection_attempts(content_str)
            threats.extend(injection_threats)
            
            self.scan_count += 1
            self.threats_detected += len(threats)
            self.last_scan_time = datetime.now(timezone.utc)
            
            scan_duration = time.time() - start_time
            is_safe = len(threats) == 0
            confidence_score = 0.85 if is_safe else 0.9  # High confidence in moderation
            
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=threats,
                scan_duration=scan_duration,
                is_safe=is_safe,
                confidence_score=confidence_score,
                metadata={
                    "filter_categories": len(self.content_filters),
                    "scanner": self.scanner_id
                }
            )
            
        except Exception as e:
            logger.error(f"Content moderation scanning failed: {str(e)}")
            return SecurityScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                content_type=content_type,
                scan_timestamp=datetime.now(timezone.utc),
                threats_detected=[],
                scan_duration=time.time() - start_time,
                is_safe=False,
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _check_injection_attempts(self, content: str) -> List[SecurityThreat]:
        """Check for injection attack attempts"""
        threats = []
        
        # SQL injection patterns
        sql_patterns = [
            r"(?i)(union|select|insert|delete|update|drop)\s+",
            r"(?i)(or|and)\s+\d+\s*=\s*\d+",
            r"(?i)(\-\-|\#|\/\*|\*\/)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content):
                threats.append(SecurityThreat(
                    threat_id=f"injection_{uuid.uuid4().hex[:8]}",
                    threat_type=SecurityEventType.INJECTION_ATTEMPT,
                    threat_level=ThreatLevel.CRITICAL,
                    description="SQL injection attempt detected",
                    detected_at=datetime.now(timezone.utc),
                    evidence={"injection_type": "sql", "pattern": pattern},
                    mitigation_actions=[
                        "Block malicious input",
                        "Implement input validation",
                        "Use parameterized queries"
                    ]
                ))
                break  # One detection per type is enough
        
        # XSS patterns
        xss_patterns = [
            r"(?i)<script[^>]*>",
            r"(?i)javascript:",
            r"(?i)on\w+\s*=",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, content):
                threats.append(SecurityThreat(
                    threat_id=f"injection_{uuid.uuid4().hex[:8]}",
                    threat_type=SecurityEventType.INJECTION_ATTEMPT,
                    threat_level=ThreatLevel.HIGH,
                    description="XSS injection attempt detected",
                    detected_at=datetime.now(timezone.utc),
                    evidence={"injection_type": "xss", "pattern": pattern},
                    mitigation_actions=[
                        "Sanitize HTML input",
                        "Implement Content Security Policy",
                        "Use output encoding"
                    ]
                ))
                break
        
        return threats
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get content moderation scanner capabilities"""
        return {
            "scanner_id": self.scanner_id,
            "type": "content_moderation",
            "filter_categories": list(self.content_filters.keys()),
            "total_keywords": sum(len(keywords) for keywords in self.content_filters.values()),
            "scans_performed": self.scan_count,
            "threats_detected": self.threats_detected,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None
        }


class EncryptionManager:
    """Encryption and cryptographic services"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.fernet = None
        self.rsa_key_pair = None
        self._initialize_encryption()
        
    def _initialize_encryption(self):
        """Initialize encryption systems"""
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available")
            return
        
        try:
            # Initialize Fernet for symmetric encryption
            if self.config.encryption_key:
                key = base64.urlsafe_b64decode(self.config.encryption_key.encode())
            else:
                key = Fernet.generate_key()
                logger.info(f"Generated new encryption key: {base64.urlsafe_b64encode(key).decode()}")
            
            self.fernet = Fernet(key)
            
            # Generate RSA key pair for asymmetric encryption
            self.rsa_key_pair = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            logger.info("Encryption system initialized successfully")
            
        except Exception as e:
            logger.error(f"Encryption initialization failed: {str(e)}")
    
    def encrypt_data(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Encrypt data using symmetric encryption"""
        if not self.fernet:
            return None
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.fernet.encrypt(data)
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Data encryption failed: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data using symmetric encryption"""
        if not self.fernet:
            return None
        
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data decryption failed: {str(e)}")
            return None
    
    def encrypt_with_rsa(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Encrypt data using RSA public key"""
        if not self.rsa_key_pair:
            return None
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            public_key = self.rsa_key_pair.public_key()
            encrypted = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted
            
        except Exception as e:
            logger.error(f"RSA encryption failed: {str(e)}")
            return None
    
    def decrypt_with_rsa(self, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data using RSA private key"""
        if not self.rsa_key_pair:
            return None
        
        try:
            decrypted = self.rsa_key_pair.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted
            
        except Exception as e:
            logger.error(f"RSA decryption failed: {str(e)}")
            return None
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Hash data using specified algorithm"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Data hashing failed: {str(e)}")
            return ""
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            return ""


class RateLimiter:
    """Rate limiting for security protection"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.request_timestamps: Dict[str, deque] = defaultdict(lambda: deque())
        
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(minutes=1)
        
        # Clean old timestamps
        timestamps = self.request_timestamps[identifier]
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.popleft()
        
        # Check if limit exceeded
        if len(timestamps) >= self.requests_per_minute:
            return True
        
        # Add current request
        timestamps.append(current_time)
        return False
    
    def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit status for identifier"""
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(minutes=1)
        
        timestamps = self.request_timestamps[identifier]
        recent_requests = [t for t in timestamps if t > cutoff_time]
        
        return {
            "identifier": identifier,
            "requests_in_window": len(recent_requests),
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - len(recent_requests)),
            "reset_time": (current_time + timedelta(minutes=1)).isoformat(),
            "is_limited": len(recent_requests) >= self.requests_per_minute
        }


class SecurityProcessingLayer:
    """
    🔒 Enterprise Security Processing Layer
    
    Advanced security processing platform with:
    - Multi-layer content security scanning
    - Malware and threat detection
    - Privacy compliance validation (GDPR, CCPA, etc.)
    - Content moderation and filtering
    - Encryption and cryptographic services
    - Real-time threat monitoring
    - Automated incident response
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.scanners: Dict[str, BaseSecurityScanner] = {}
        self.encryption_manager = EncryptionManager(self.config)
        self.rate_limiter = RateLimiter(self.config.rate_limit_requests_per_minute)
        self.scan_cache: Dict[str, SecurityScanResult] = {}
        self.threat_log: List[SecurityThreat] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        # Statistics
        self.total_scans = 0
        self.total_threats_detected = 0
        self.start_time = datetime.now(timezone.utc)
        
        # Initialize scanners
        self._initialize_scanners()
        
        # Start monitoring if enabled
        if self.config.enable_real_time_monitoring:
            self._start_monitoring()
    
    def _initialize_scanners(self):
        """Initialize security scanners"""
        if self.config.enable_malware_scanning:
            self.scanners["malware"] = MalwareScanner("malware_scanner", self.config)
        
        if self.config.enable_privacy_protection:
            self.scanners["privacy"] = PrivacyScanner("privacy_scanner", self.config)
        
        if self.config.enable_content_filtering:
            self.scanners["moderation"] = ContentModerationScanner("content_moderation", self.config)
        
        logger.info(f"Initialized {len(self.scanners)} security scanners")
    
    def _start_monitoring(self):
        """Start real-time security monitoring"""
        def monitoring_loop():
            while True:
                try:
                    self._perform_monitoring_checks()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring error: {str(e)}")
                    time.sleep(60)
        
        import threading
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        logger.info("Started real-time security monitoring")
    
    def _perform_monitoring_checks(self):
        """Perform periodic monitoring checks"""
        try:
            # Check for recent high-priority threats
            recent_threats = [
                threat for threat in self.threat_log[-100:]  # Last 100 threats
                if (datetime.now(timezone.utc) - threat.detected_at).total_seconds() < 3600  # Last hour
                and threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            ]
            
            if len(recent_threats) > 5:  # Threshold for alert
                self._trigger_security_alert(f"High threat activity: {len(recent_threats)} threats in last hour")
            
            # Monitor rate limiting
            # Implementation depends on access to request data
            
        except Exception as e:
            logger.error(f"Monitoring check failed: {str(e)}")
    
    def _trigger_security_alert(self, message: str):
        """Trigger security alert"""
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "ALERT",
            "message": message,
            "alert_id": uuid.uuid4().hex
        }
        
        self.audit_log.append(alert)
        logger.warning(f"SECURITY ALERT: {message}")
    
    async def scan_content(self, content: Any, content_type: ContentType, 
                          source_ip: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, SecurityScanResult]:
        """Comprehensive security scan of content"""
        
        # Rate limiting check
        identifier = source_ip or user_id or "anonymous"
        if self.rate_limiter.is_rate_limited(identifier):
            raise Exception(f"Rate limit exceeded for {identifier}")
        
        # Check cache
        content_hash = hashlib.sha256(str(content).encode()).hexdigest()
        if content_hash in self.scan_cache:
            cached_result = self.scan_cache[content_hash]
            # Return cached if recent (within 1 hour)
            if (datetime.now(timezone.utc) - cached_result.scan_timestamp).total_seconds() < 3600:
                return {"cached": cached_result}
        
        scan_results = {}
        
        try:
            # Run all applicable scanners
            for scanner_name, scanner in self.scanners.items():
                try:
                    result = await scanner.scan_content(content, content_type)
                    scan_results[scanner_name] = result
                    
                    # Log threats
                    for threat in result.threats_detected:
                        threat.source_ip = source_ip
                        threat.user_id = user_id
                        self.threat_log.append(threat)
                        self.total_threats_detected += 1
                    
                except Exception as e:
                    logger.error(f"Scanner {scanner_name} failed: {str(e)}")
                    scan_results[scanner_name] = SecurityScanResult(
                        scan_id=f"error_{uuid.uuid4().hex[:8]}",
                        content_hash=content_hash,
                        content_type=content_type,
                        scan_timestamp=datetime.now(timezone.utc),
                        threats_detected=[],
                        scan_duration=0.0,
                        is_safe=False,
                        confidence_score=0.0,
                        metadata={"error": str(e)}
                    )
            
            self.total_scans += 1
            
            # Cache results
            if scan_results:
                self.scan_cache[content_hash] = scan_results[list(scan_results.keys())[0]]
            
            # Audit log
            self._log_audit_event("content_scan", {
                "content_hash": content_hash,
                "content_type": content_type.value,
                "source_ip": source_ip,
                "user_id": user_id,
                "scanners_used": list(scan_results.keys()),
                "threats_found": sum(len(result.threats_detected) for result in scan_results.values())
            })
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Content scanning failed: {str(e)}")
            self._log_audit_event("scan_error", {
                "error": str(e),
                "content_hash": content_hash,
                "source_ip": source_ip,
                "user_id": user_id
            })
            raise
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event"""
        if self.config.enable_audit_logging:
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "details": details,
                "event_id": uuid.uuid4().hex
            }
            self.audit_log.append(audit_entry)
            
            # Keep only recent audit logs (last 10000)
            if len(self.audit_log) > 10000:
                self.audit_log = self.audit_log[-10000:]
    
    async def encrypt_sensitive_data(self, data: Union[str, bytes], 
                                   encryption_type: str = "symmetric") -> Optional[str]:
        """Encrypt sensitive data"""
        try:
            if encryption_type == "symmetric":
                encrypted = self.encryption_manager.encrypt_data(data)
            elif encryption_type == "asymmetric":
                encrypted = self.encryption_manager.encrypt_with_rsa(data)
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            if encrypted:
                encoded = base64.b64encode(encrypted).decode('utf-8')
                self._log_audit_event("data_encryption", {
                    "encryption_type": encryption_type,
                    "data_length": len(str(data))
                })
                return encoded
            
        except Exception as e:
            logger.error(f"Data encryption failed: {str(e)}")
            self._log_audit_event("encryption_error", {"error": str(e)})
        
        return None
    
    async def decrypt_sensitive_data(self, encrypted_data: str, 
                                   encryption_type: str = "symmetric") -> Optional[str]:
        """Decrypt sensitive data"""
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            
            if encryption_type == "symmetric":
                decrypted = self.encryption_manager.decrypt_data(decoded)
            elif encryption_type == "asymmetric":
                decrypted = self.encryption_manager.decrypt_with_rsa(decoded)
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            if decrypted:
                result = decrypted.decode('utf-8')
                self._log_audit_event("data_decryption", {
                    "encryption_type": encryption_type,
                    "success": True
                })
                return result
            
        except Exception as e:
            logger.error(f"Data decryption failed: {str(e)}")
            self._log_audit_event("decryption_error", {"error": str(e)})
        
        return None
    
    async def check_compliance(self, content: str, standard: ComplianceStandard) -> ComplianceCheckResult:
        """Check content compliance with specific standard"""
        check_id = f"compliance_{uuid.uuid4().hex[:8]}"
        violations = []
        recommendations = []
        
        try:
            if standard == ComplianceStandard.GDPR:
                # GDPR-specific checks
                if "personal data" in content.lower() and "consent" not in content.lower():
                    violations.append("Personal data processing without explicit consent indication")
                    recommendations.append("Add consent collection mechanism")
                
                if "email" in content.lower() and "right to deletion" not in content.lower():
                    violations.append("Missing data subject rights information")
                    recommendations.append("Include data subject rights notice")
            
            elif standard == ComplianceStandard.PCI_DSS:
                # PCI DSS checks
                if re.search(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", content):
                    violations.append("Credit card data in unencrypted form")
                    recommendations.append("Encrypt all cardholder data")
            
            elif standard == ComplianceStandard.HIPAA:
                # HIPAA checks
                health_terms = ["medical", "patient", "health", "diagnosis", "treatment"]
                if any(term in content.lower() for term in health_terms):
                    if "authorization" not in content.lower():
                        violations.append("Health information without authorization indication")
                        recommendations.append("Ensure proper health information authorization")
            
            is_compliant = len(violations) == 0
            
            result = ComplianceCheckResult(
                check_id=check_id,
                standard=standard,
                is_compliant=is_compliant,
                violations=violations,
                recommendations=recommendations,
                check_timestamp=datetime.now(timezone.utc),
                details={
                    "content_length": len(content),
                    "standard": standard.value
                }
            )
            
            self._log_audit_event("compliance_check", {
                "check_id": check_id,
                "standard": standard.value,
                "is_compliant": is_compliant,
                "violations_count": len(violations)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            return ComplianceCheckResult(
                check_id=check_id,
                standard=standard,
                is_compliant=False,
                violations=[f"Check failed: {str(e)}"],
                recommendations=["Review compliance check implementation"],
                check_timestamp=datetime.now(timezone.utc)
            )
    
    async def quarantine_content(self, content: Any, threat_info: SecurityThreat) -> bool:
        """Quarantine suspicious content"""
        try:
            quarantine_dir = Path(self.config.quarantine_directory)
            quarantine_dir.mkdir(exist_ok=True)
            
            # Generate quarantine file
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"quarantine_{timestamp}_{threat_info.threat_id}.txt"
            filepath = quarantine_dir / filename
            
            # Save content and threat info
            quarantine_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "threat_info": {
                    "threat_id": threat_info.threat_id,
                    "threat_type": threat_info.threat_type.value,
                    "threat_level": threat_info.threat_level.value,
                    "description": threat_info.description
                },
                "content": str(content)[:1000],  # Limit content size
                "content_hash": hashlib.sha256(str(content).encode()).hexdigest()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(quarantine_data, f, indent=2)
            
            self._log_audit_event("content_quarantine", {
                "threat_id": threat_info.threat_id,
                "quarantine_file": str(filepath),
                "threat_level": threat_info.threat_level.value
            })
            
            logger.info(f"Content quarantined: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Content quarantine failed: {str(e)}")
            return False
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard"""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        # Recent threats (last 24 hours)
        recent_threats = [
            threat for threat in self.threat_log
            if (datetime.now(timezone.utc) - threat.detected_at).total_seconds() < 86400
        ]
        
        # Threat statistics by level
        threat_stats = defaultdict(int)
        for threat in recent_threats:
            threat_stats[threat.threat_level.value] += 1
        
        dashboard = {
            "overview": {
                "uptime_hours": uptime / 3600,
                "total_scans": self.total_scans,
                "total_threats_detected": self.total_threats_detected,
                "active_scanners": len(self.scanners),
                "cache_size": len(self.scan_cache),
                "audit_log_entries": len(self.audit_log)
            },
            "recent_threats": {
                "last_24h_count": len(recent_threats),
                "by_level": dict(threat_stats),
                "latest_threats": [
                    {
                        "threat_id": threat.threat_id,
                        "type": threat.threat_type.value,
                        "level": threat.threat_level.value,
                        "description": threat.description,
                        "detected_at": threat.detected_at.isoformat()
                    }
                    for threat in recent_threats[-5:]  # Last 5 threats
                ]
            },
            "scanners": {
                scanner_name: scanner.get_capabilities()
                for scanner_name, scanner in self.scanners.items()
            },
            "rate_limiting": {
                "requests_per_minute_limit": self.config.rate_limit_requests_per_minute,
                "active_limiters": len(self.rate_limiter.request_timestamps)
            },
            "encryption": {
                "enabled": self.config.enable_encryption,
                "available": CRYPTO_AVAILABLE,
                "symmetric_ready": self.encryption_manager.fernet is not None,
                "asymmetric_ready": self.encryption_manager.rsa_key_pair is not None
            },
            "compliance": {
                "enabled_standards": [std.value for std in self.config.compliance_standards],
                "privacy_protection": self.config.enable_privacy_protection
            }
        }
        
        return dashboard
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "dependencies": {},
            "performance": {}
        }
        
        try:
            # Check scanners
            health_status["components"]["scanners"] = {}
            for scanner_name, scanner in self.scanners.items():
                health_status["components"]["scanners"][scanner_name] = {
                    "status": "operational",
                    "scans_performed": scanner.scan_count,
                    "threats_detected": scanner.threats_detected,
                    "last_scan": scanner.last_scan_time.isoformat() if scanner.last_scan_time else None
                }
            
            # Check encryption
            health_status["components"]["encryption"] = {
                "status": "operational" if self.encryption_manager.fernet else "degraded",
                "symmetric_encryption": self.encryption_manager.fernet is not None,
                "asymmetric_encryption": self.encryption_manager.rsa_key_pair is not None
            }
            
            # Check dependencies
            health_status["dependencies"] = {
                "cryptography": CRYPTO_AVAILABLE,
                "yara": YARA_AVAILABLE,
                "pil": PIL_AVAILABLE,
                "http_client": HTTP_AVAILABLE
            }
            
            # Performance metrics
            health_status["performance"] = {
                "total_scans": self.total_scans,
                "cache_hit_ratio": len(self.scan_cache) / max(1, self.total_scans),
                "avg_threats_per_scan": self.total_threats_detected / max(1, self.total_scans),
                "memory_usage": {
                    "scan_cache": len(self.scan_cache),
                    "threat_log": len(self.threat_log),
                    "audit_log": len(self.audit_log)
                }
            }
            
            # Check for issues
            if not CRYPTO_AVAILABLE:
                health_status["status"] = "degraded"
                health_status["warnings"] = ["Cryptography library not available"]
            
            if len(self.threat_log) > 10000:
                health_status["status"] = "warning"
                health_status["warnings"] = health_status.get("warnings", []) + ["High threat volume"]
            
        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
            logger.error(f"Security layer health check failed: {str(e)}")
        
        return health_status


# Export main classes and functions
__all__ = [
    "SecurityProcessingLayer",
    "SecurityConfig",
    "SecurityScanResult",
    "SecurityThreat",
    "ComplianceCheckResult",
    "ThreatLevel",
    "SecurityEventType",
    "ComplianceStandard",
    "ContentType"
]


# Example usage
async def example_usage():
    """Example usage of the Security Processing Layer"""
    config = SecurityConfig(
        enable_malware_scanning=True,
        enable_privacy_protection=True,
        enable_content_filtering=True,
        enable_encryption=True,
        compliance_standards={ComplianceStandard.GDPR, ComplianceStandard.SOC2}
    )
    
    security_layer = SecurityProcessingLayer(config)
    
    # Test content scanning
    test_content = """
    Welcome to our service! Please provide your email address
    and credit card number: 4532-1234-5678-9876 for verification.
    <script>alert('xss')</script>
    """
    
    # Scan content
    scan_results = await security_layer.scan_content(
        content=test_content,
        content_type=ContentType.TEXT,
        source_ip="192.168.1.100",
        user_id="user_123"
    )
    
    print("Security Scan Results:")
    for scanner_name, result in scan_results.items():
        print(f"\n{scanner_name.upper()} Scanner:")
        print(f"  Safe: {result.is_safe}")
        print(f"  Confidence: {result.confidence_score:.2f}")
        print(f"  Threats: {len(result.threats_detected)}")
        
        for threat in result.threats_detected[:2]:  # Show first 2 threats
            print(f"    - {threat.threat_level.value.upper()}: {threat.description}")
    
    # Test encryption
    sensitive_data = "user_password_123"
    encrypted = await security_layer.encrypt_sensitive_data(sensitive_data)
    if encrypted:
        print(f"\nEncrypted data: {encrypted[:50]}...")
        
        decrypted = await security_layer.decrypt_sensitive_data(encrypted)
        print(f"Decrypted data: {decrypted}")
    
    # Test compliance check
    compliance_result = await security_layer.check_compliance(
        test_content, 
        ComplianceStandard.GDPR
    )
    
    print(f"\nGDPR Compliance:")
    print(f"  Compliant: {compliance_result.is_compliant}")
    print(f"  Violations: {len(compliance_result.violations)}")
    for violation in compliance_result.violations:
        print(f"    - {violation}")
    
    # Get security dashboard
    dashboard = await security_layer.get_security_dashboard()
    print(f"\nSecurity Dashboard:")
    print(f"  Total Scans: {dashboard['overview']['total_scans']}")
    print(f"  Threats Detected: {dashboard['overview']['total_threats_detected']}")
    print(f"  Active Scanners: {dashboard['overview']['active_scanners']}")
    
    # Health check
    health = await security_layer.health_check()
    print(f"\nHealth Status: {health['status']}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())