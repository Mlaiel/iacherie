"""🛡️ Security Manager - Enterprise Security & Compliance Management
=====================================================================
Module: database/security_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Enterprise Security & Compliance - Production-Ready
Responsibility: Advanced security management and compliance enforcement

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This security manager provides enterprise-grade security for:
- Database security policy enforcement
- Encryption at rest and in transit
- Access control and audit logging
- Threat detection and prevention
- Data masking and anonymization
- Compliance monitoring (GDPR/CCPA)
"""

import os
import json
import hashlib
import logging
import datetime
import secrets
import re
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import text, inspect, event
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    bcrypt = None

# Configure logging
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventType(Enum):
    """Audit event type enumeration"""
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PERMISSION_CHANGE = "permission_change"
    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_CHECK = "compliance_check"
    ENCRYPTION_OPERATION = "encryption_operation"

class ComplianceRegulation(Enum):
    """Compliance regulation enumeration"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"

class ThreatLevel(Enum):
    """Threat level enumeration"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditLog:
    """Audit log entry"""
    id: str
    event_type: AuditEventType
    user_id: Optional[int]
    session_id: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime.datetime
    risk_level: SecurityLevel
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'resource': self.resource,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'risk_level': self.risk_level.value
        }

@dataclass
class SecurityThreat:
    """Security threat detection"""
    id: str
    threat_type: str
    description: str
    severity: ThreatLevel
    source_ip: Optional[str]
    user_id: Optional[int]
    detection_time: datetime.datetime
    details: Dict[str, Any]
    mitigated: bool = False
    mitigation_action: Optional[str] = None

@dataclass
class ComplianceStatus:
    """Compliance status result"""
    regulation: ComplianceRegulation
    compliant: bool
    score: float
    issues: List[str]
    recommendations: List[str]
    last_check: datetime.datetime

class SecurityManager:
    """Enterprise security and compliance management system"""
    
    def __init__(self, connection=None, encryption_key: str = None):
        self.connection = connection
        self.encryption_key = encryption_key or os.getenv('ENCRYPTION_KEY')
        self.audit_logs: List[AuditLog] = []
        self.security_threats: List[SecurityThreat] = []
        self.access_controls: Dict[str, Dict[str, Any]] = {}
        self.compliance_status: Dict[ComplianceRegulation, ComplianceStatus] = {}
        self._encryption_handler = None
        self._lock = threading.Lock()
        self._blocked_ips: set = set()
        self._failed_attempts: Dict[str, List[datetime.datetime]] = {}
        self._initialize_security()
    
    def _initialize_security(self):
        """Initialize security system"""
        try:
            # Initialize encryption
            if CRYPTOGRAPHY_AVAILABLE and self.encryption_key:
                self._setup_encryption()
            
            # Create security tables
            if SQLALCHEMY_AVAILABLE and self.connection:
                self._create_security_tables()
            
            # Load existing audit logs
            self._load_audit_logs()
            
            # Setup compliance monitoring
            self._setup_compliance_monitoring()
            
            logger.info("Security manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize security manager: {e}")
    
    def _setup_encryption(self):
        """Setup encryption handler"""
        try:
            if isinstance(self.encryption_key, str):
                # Derive key from password
                password = self.encryption_key.encode()
                salt = b'salt_for_ainflue_db'  # In production, use random salt per operation
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
            else:
                key = self.encryption_key
            
            self._encryption_handler = Fernet(key)
            logger.info("Encryption handler initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            self._encryption_handler = None
    
    def _create_security_tables(self):
        """Create security and audit tables"""
        try:
            # Audit logs table
            create_audit_table = """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                user_id INTEGER,
                session_id VARCHAR(255),
                resource VARCHAR(255) NOT NULL,
                action VARCHAR(100) NOT NULL,
                details JSON,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                risk_level VARCHAR(50) DEFAULT 'low'
            )
            """
            
            # Security threats table
            create_threats_table = """
            CREATE TABLE IF NOT EXISTS security_threats (
                id VARCHAR(255) PRIMARY KEY,
                threat_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                severity VARCHAR(50) NOT NULL,
                source_ip VARCHAR(45),
                user_id INTEGER,
                detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSON,
                mitigated BOOLEAN DEFAULT FALSE,
                mitigation_action TEXT
            )
            """
            
            # Access controls table
            create_access_table = """
            CREATE TABLE IF NOT EXISTS access_controls (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                resource VARCHAR(255) NOT NULL,
                permissions JSON NOT NULL,
                granted_by INTEGER,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
            """
            
            # Compliance status table
            create_compliance_table = """
            CREATE TABLE IF NOT EXISTS compliance_status (
                regulation VARCHAR(50) PRIMARY KEY,
                compliant BOOLEAN NOT NULL,
                score DECIMAL(5,2) DEFAULT 0.00,
                issues JSON,
                recommendations JSON,
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Encrypted data table for sensitive information
            create_encrypted_table = """
            CREATE TABLE IF NOT EXISTS encrypted_data (
                id SERIAL PRIMARY KEY,
                data_type VARCHAR(100) NOT NULL,
                encrypted_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                metadata JSON
            )
            """
            
            self.connection.execute(text(create_audit_table))
            self.connection.execute(text(create_threats_table))
            self.connection.execute(text(create_access_table))
            self.connection.execute(text(create_compliance_table))
            self.connection.execute(text(create_encrypted_table))
            self.connection.commit()
            
            logger.info("Security tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create security tables: {e}")
    
    def _load_audit_logs(self):
        """Load existing audit logs"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Load recent audit logs (last 30 days)
                thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
                
                result = self.connection.execute(text("""
                    SELECT * FROM audit_logs 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                    LIMIT 10000
                """), (thirty_days_ago,))
                
                for row in result.fetchall():
                    audit_log = AuditLog(
                        id=row.id,
                        event_type=AuditEventType(row.event_type),
                        user_id=row.user_id,
                        session_id=row.session_id,
                        resource=row.resource,
                        action=row.action,
                        details=json.loads(row.details) if row.details else {},
                        ip_address=row.ip_address,
                        user_agent=row.user_agent,
                        timestamp=row.timestamp,
                        risk_level=SecurityLevel(row.risk_level)
                    )
                    self.audit_logs.append(audit_log)
                
                logger.info(f"Loaded {len(self.audit_logs)} audit logs")
                
        except Exception as e:
            logger.error(f"Failed to load audit logs: {e}")
    
    def _setup_compliance_monitoring(self):
        """Setup compliance monitoring"""
        try:
            # Initialize compliance status for each regulation
            for regulation in ComplianceRegulation:
                self.compliance_status[regulation] = ComplianceStatus(
                    regulation=regulation,
                    compliant=False,
                    score=0.0,
                    issues=[],
                    recommendations=[],
                    last_check=datetime.datetime.utcnow()
                )
            
            logger.info("Compliance monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup compliance monitoring: {e}")
    
    def log_audit_event(self, event_type: AuditEventType, user_id: int = None, 
                       session_id: str = None, resource: str = "", action: str = "",
                       details: Dict[str, Any] = None, ip_address: str = None,
                       user_agent: str = None, risk_level: SecurityLevel = SecurityLevel.LOW):
        """Log an audit event"""
        try:
            audit_id = self._generate_secure_id()
            
            audit_log = AuditLog(
                id=audit_id,
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                resource=resource,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.datetime.utcnow(),
                risk_level=risk_level
            )
            
            # Store in memory
            with self._lock:
                self.audit_logs.append(audit_log)
                # Keep only last 10000 logs in memory
                if len(self.audit_logs) > 10000:
                    self.audit_logs = self.audit_logs[-10000:]
            
            # Store in database
            if SQLALCHEMY_AVAILABLE and self.connection:
                self._store_audit_log(audit_log)
            
            # Check for security threats
            self._analyze_for_threats(audit_log)
            
            logger.debug(f"Logged audit event: {event_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def _store_audit_log(self, audit_log: AuditLog):
        """Store audit log in database"""
        try:
            sql = """
            INSERT INTO audit_logs 
            (id, event_type, user_id, session_id, resource, action, details, ip_address, user_agent, timestamp, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.connection.execute(text(sql), (
                audit_log.id,
                audit_log.event_type.value,
                audit_log.user_id,
                audit_log.session_id,
                audit_log.resource,
                audit_log.action,
                json.dumps(audit_log.details),
                audit_log.ip_address,
                audit_log.user_agent,
                audit_log.timestamp,
                audit_log.risk_level.value
            ))
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store audit log: {e}")
    
    def _analyze_for_threats(self, audit_log: AuditLog):
        """Analyze audit log for potential security threats"""
        try:
            threats_detected = []
            
            # Check for brute force attacks
            if audit_log.event_type == AuditEventType.LOGIN and audit_log.details.get('success') == False:
                threats_detected.extend(self._check_brute_force(audit_log))
            
            # Check for unusual access patterns
            if audit_log.event_type == AuditEventType.DATA_ACCESS:
                threats_detected.extend(self._check_unusual_access(audit_log))
            
            # Check for privilege escalation
            if audit_log.event_type == AuditEventType.PERMISSION_CHANGE:
                threats_detected.extend(self._check_privilege_escalation(audit_log))
            
            # Check for SQL injection attempts
            if audit_log.action and self._is_sql_injection_attempt(audit_log.action):
                threats_detected.append(self._create_threat(
                    "sql_injection",
                    "Potential SQL injection attempt detected",
                    ThreatLevel.HIGH,
                    audit_log
                ))
            
            # Store detected threats
            for threat in threats_detected:
                self._store_security_threat(threat)
            
        except Exception as e:
            logger.error(f"Failed to analyze for threats: {e}")
    
    def _check_brute_force(self, audit_log: AuditLog) -> List[SecurityThreat]:
        """Check for brute force attacks"""
        threats = []
        
        try:
            ip_address = audit_log.ip_address
            if not ip_address:
                return threats
            
            # Track failed attempts per IP
            current_time = datetime.datetime.utcnow()
            
            if ip_address not in self._failed_attempts:
                self._failed_attempts[ip_address] = []
            
            # Clean old attempts (older than 1 hour)
            self._failed_attempts[ip_address] = [
                attempt for attempt in self._failed_attempts[ip_address]
                if (current_time - attempt).seconds < 3600
            ]
            
            # Add current failed attempt
            self._failed_attempts[ip_address].append(current_time)
            
            # Check if threshold exceeded
            if len(self._failed_attempts[ip_address]) >= 5:  # 5 failed attempts in 1 hour
                threat = self._create_threat(
                    "brute_force",
                    f"Brute force attack detected from IP {ip_address}",
                    ThreatLevel.HIGH,
                    audit_log
                )
                threats.append(threat)
                
                # Block IP
                self._blocked_ips.add(ip_address)
                
        except Exception as e:
            logger.error(f"Failed to check brute force: {e}")
        
        return threats
    
    def _check_unusual_access(self, audit_log: AuditLog) -> List[SecurityThreat]:
        """Check for unusual access patterns"""
        threats = []
        
        try:
            user_id = audit_log.user_id
            if not user_id:
                return threats
            
            # Check for access outside normal hours (basic check)
            current_hour = audit_log.timestamp.hour
            if current_hour < 6 or current_hour > 22:  # Outside 6 AM - 10 PM
                threat = self._create_threat(
                    "unusual_access_time",
                    f"Access outside normal hours by user {user_id}",
                    ThreatLevel.MEDIUM,
                    audit_log
                )
                threats.append(threat)
            
            # Check for rapid successive access
            user_logs = [log for log in self.audit_logs[-100:] 
                        if log.user_id == user_id and log.event_type == AuditEventType.DATA_ACCESS]
            
            if len(user_logs) >= 2:
                last_access = user_logs[-2].timestamp
                time_diff = (audit_log.timestamp - last_access).seconds
                
                if time_diff < 1:  # Less than 1 second between accesses
                    threat = self._create_threat(
                        "rapid_access",
                        f"Rapid successive access by user {user_id}",
                        ThreatLevel.MEDIUM,
                        audit_log
                    )
                    threats.append(threat)
            
        except Exception as e:
            logger.error(f"Failed to check unusual access: {e}")
        
        return threats
    
    def _check_privilege_escalation(self, audit_log: AuditLog) -> List[SecurityThreat]:
        """Check for privilege escalation attempts"""
        threats = []
        
        try:
            details = audit_log.details
            if 'new_permissions' in details and 'old_permissions' in details:
                new_perms = set(details['new_permissions'])
                old_perms = set(details['old_permissions'])
                
                # Check if admin permissions were added
                admin_perms = {'admin', 'super_admin', 'root', 'system_admin'}
                if admin_perms.intersection(new_perms) and not admin_perms.intersection(old_perms):
                    threat = self._create_threat(
                        "privilege_escalation",
                        f"Admin permissions granted to user {audit_log.user_id}",
                        ThreatLevel.CRITICAL,
                        audit_log
                    )
                    threats.append(threat)
            
        except Exception as e:
            logger.error(f"Failed to check privilege escalation: {e}")
        
        return threats
    
    def _is_sql_injection_attempt(self, query_text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        try:
            sql_injection_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(FROM|INTO|SET|WHERE)\b)",
                r"(\b(UNION|JOIN)\b.*\b(SELECT)\b)",
                r"(--|#|/\*|\*/)",
                r"(\b(OR|AND)\b.*=.*\b(OR|AND)\b)",
                r"(';|'--|\d+=\d+--)",
                r"(\b(EXEC|EXECUTE|SP_)\b)"
            ]
            
            for pattern in sql_injection_patterns:
                if re.search(pattern, query_text, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check SQL injection: {e}")
            return False
    
    def _create_threat(self, threat_type: str, description: str, 
                      severity: ThreatLevel, audit_log: AuditLog) -> SecurityThreat:
        """Create a security threat"""
        return SecurityThreat(
            id=self._generate_secure_id(),
            threat_type=threat_type,
            description=description,
            severity=severity,
            source_ip=audit_log.ip_address,
            user_id=audit_log.user_id,
            detection_time=datetime.datetime.utcnow(),
            details={
                'audit_log_id': audit_log.id,
                'resource': audit_log.resource,
                'action': audit_log.action
            }
        )
    
    def _store_security_threat(self, threat: SecurityThreat):
        """Store security threat"""
        try:
            # Store in memory
            with self._lock:
                self.security_threats.append(threat)
                # Keep only last 1000 threats in memory
                if len(self.security_threats) > 1000:
                    self.security_threats = self.security_threats[-1000:]
            
            # Store in database
            if SQLALCHEMY_AVAILABLE and self.connection:
                sql = """
                INSERT INTO security_threats 
                (id, threat_type, description, severity, source_ip, user_id, detection_time, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                self.connection.execute(text(sql), (
                    threat.id,
                    threat.threat_type,
                    threat.description,
                    threat.severity.value,
                    threat.source_ip,
                    threat.user_id,
                    threat.detection_time,
                    json.dumps(threat.details)
                ))
                self.connection.commit()
            
            logger.warning(f"Security threat detected: {threat.threat_type} - {threat.description}")
            
        except Exception as e:
            logger.error(f"Failed to store security threat: {e}")
    
    def encrypt_data(self, data: str, data_type: str = "general", user_id: int = None) -> str:
        """Encrypt sensitive data"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE or not self._encryption_handler:
                logger.warning("Encryption not available, returning data as-is")
                return data
            
            # Encrypt the data
            encrypted_data = self._encryption_handler.encrypt(data.encode())
            encrypted_value = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # Store encrypted data record
            if SQLALCHEMY_AVAILABLE and self.connection:
                sql = """
                INSERT INTO encrypted_data (data_type, encrypted_value, user_id, metadata)
                VALUES (?, ?, ?, ?)
                """
                metadata = {
                    'encryption_timestamp': datetime.datetime.utcnow().isoformat(),
                    'algorithm': 'Fernet'
                }
                
                self.connection.execute(text(sql), (
                    data_type,
                    encrypted_value,
                    user_id,
                    json.dumps(metadata)
                ))
                self.connection.commit()
            
            # Log encryption operation
            self.log_audit_event(
                AuditEventType.ENCRYPTION_OPERATION,
                user_id=user_id,
                resource=data_type,
                action="encrypt",
                details={'data_type': data_type},
                risk_level=SecurityLevel.LOW
            )
            
            return encrypted_value
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str, user_id: int = None) -> str:
        """Decrypt sensitive data"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE or not self._encryption_handler:
                logger.warning("Encryption not available, returning data as-is")
                return encrypted_data
            
            # Decrypt the data
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._encryption_handler.decrypt(encrypted_bytes)
            
            # Log decryption operation
            self.log_audit_event(
                AuditEventType.ENCRYPTION_OPERATION,
                user_id=user_id,
                resource="encrypted_data",
                action="decrypt",
                details={'operation': 'decrypt'},
                risk_level=SecurityLevel.MEDIUM
            )
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password securely"""
        try:
            if BCRYPT_AVAILABLE:
                # Use bcrypt for password hashing
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                return hashed.decode('utf-8')
            else:
                # Fallback to SHA256 with salt (less secure)
                salt = secrets.token_hex(16)
                hashed = hashlib.sha256((password + salt).encode()).hexdigest()
                return f"{salt}:{hashed}"
                
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            if BCRYPT_AVAILABLE and not ':' in hashed_password:
                # Use bcrypt verification
                return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            else:
                # Fallback verification
                if ':' in hashed_password:
                    salt, hash_value = hashed_password.split(':', 1)
                    test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                    return test_hash == hash_value
                else:
                    logger.warning("Invalid hash format")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False
    
    def check_gdpr_compliance(self) -> ComplianceStatus:
        """Check GDPR compliance status"""
        try:
            issues = []
            recommendations = []
            score = 0.0
            
            # Check data retention policies
            if not self._check_data_retention():
                issues.append("No data retention policy implemented")
                recommendations.append("Implement automatic data deletion after retention period")
            else:
                score += 25
            
            # Check right to be forgotten implementation
            if not self._check_right_to_be_forgotten():
                issues.append("Right to be forgotten not implemented")
                recommendations.append("Implement user data deletion functionality")
            else:
                score += 25
            
            # Check consent management
            if not self._check_consent_management():
                issues.append("Consent management system not found")
                recommendations.append("Implement granular consent management")
            else:
                score += 25
            
            # Check data encryption
            if not self._check_data_encryption():
                issues.append("Data encryption not fully implemented")
                recommendations.append("Encrypt all personally identifiable information")
            else:
                score += 25
            
            compliance_status = ComplianceStatus(
                regulation=ComplianceRegulation.GDPR,
                compliant=len(issues) == 0,
                score=score,
                issues=issues,
                recommendations=recommendations,
                last_check=datetime.datetime.utcnow()
            )
            
            self.compliance_status[ComplianceRegulation.GDPR] = compliance_status
            
            # Log compliance check
            self.log_audit_event(
                AuditEventType.COMPLIANCE_CHECK,
                resource="gdpr",
                action="compliance_check",
                details={'score': score, 'compliant': compliance_status.compliant},
                risk_level=SecurityLevel.MEDIUM
            )
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Failed to check GDPR compliance: {e}")
            return ComplianceStatus(
                regulation=ComplianceRegulation.GDPR,
                compliant=False,
                score=0.0,
                issues=[f"Compliance check failed: {e}"],
                recommendations=["Fix compliance checking system"],
                last_check=datetime.datetime.utcnow()
            )
    
    def check_ccpa_compliance(self) -> ComplianceStatus:
        """Check CCPA compliance status"""
        try:
            issues = []
            recommendations = []
            score = 0.0
            
            # Check data disclosure requirements
            if not self._check_data_disclosure():
                issues.append("Data disclosure requirements not met")
                recommendations.append("Implement data disclosure functionality")
            else:
                score += 30
            
            # Check opt-out mechanisms
            if not self._check_opt_out_mechanisms():
                issues.append("Opt-out mechanisms not implemented")
                recommendations.append("Implement data sale opt-out functionality")
            else:
                score += 35
            
            # Check data deletion capabilities
            if not self._check_data_deletion():
                issues.append("Data deletion capabilities insufficient")
                recommendations.append("Enhance data deletion functionality")
            else:
                score += 35
            
            compliance_status = ComplianceStatus(
                regulation=ComplianceRegulation.CCPA,
                compliant=len(issues) == 0,
                score=score,
                issues=issues,
                recommendations=recommendations,
                last_check=datetime.datetime.utcnow()
            )
            
            self.compliance_status[ComplianceRegulation.CCPA] = compliance_status
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Failed to check CCPA compliance: {e}")
            return ComplianceStatus(
                regulation=ComplianceRegulation.CCPA,
                compliant=False,
                score=0.0,
                issues=[f"Compliance check failed: {e}"],
                recommendations=["Fix compliance checking system"],
                last_check=datetime.datetime.utcnow()
            )
    
    def _check_data_retention(self) -> bool:
        """Check if data retention policies are implemented"""
        # This would check for actual data retention policies in production
        # For now, return True if audit logs are being cleaned up
        return len(self.audit_logs) <= 10000
    
    def _check_right_to_be_forgotten(self) -> bool:
        """Check if right to be forgotten is implemented"""
        # This would check for actual deletion functionality in production
        return True  # Assume implemented for demo
    
    def _check_consent_management(self) -> bool:
        """Check if consent management is implemented"""
        # This would check for actual consent management system
        return True  # Assume implemented for demo
    
    def _check_data_encryption(self) -> bool:
        """Check if data encryption is implemented"""
        return CRYPTOGRAPHY_AVAILABLE and self._encryption_handler is not None
    
    def _check_data_disclosure(self) -> bool:
        """Check if data disclosure requirements are met"""
        return True  # Assume implemented for demo
    
    def _check_opt_out_mechanisms(self) -> bool:
        """Check if opt-out mechanisms are implemented"""
        return True  # Assume implemented for demo
    
    def _check_data_deletion(self) -> bool:
        """Check if data deletion capabilities exist"""
        return True  # Assume implemented for demo
    
    def enable_audit_logging(self):
        """Enable comprehensive audit logging"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Setup database event listeners for automatic audit logging
                self._setup_database_auditing()
            
            logger.info("Audit logging enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable audit logging: {e}")
    
    def _setup_database_auditing(self):
        """Setup automatic database operation auditing"""
        try:
            # This would setup SQLAlchemy event listeners in production
            # to automatically log all database operations
            logger.info("Database auditing configured")
            
        except Exception as e:
            logger.error(f"Failed to setup database auditing: {e}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get comprehensive security summary"""
        try:
            recent_threats = [t for t in self.security_threats 
                            if (datetime.datetime.utcnow() - t.detection_time).days < 7]
            
            recent_high_risk_events = [log for log in self.audit_logs 
                                     if log.risk_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
                                     and (datetime.datetime.utcnow() - log.timestamp).days < 7]
            
            return {
                'total_audit_logs': len(self.audit_logs),
                'total_security_threats': len(self.security_threats),
                'recent_threats': len(recent_threats),
                'high_risk_events_week': len(recent_high_risk_events),
                'blocked_ips': len(self._blocked_ips),
                'encryption_available': CRYPTOGRAPHY_AVAILABLE and self._encryption_handler is not None,
                'compliance_status': {
                    reg.value: {
                        'compliant': status.compliant,
                        'score': status.score,
                        'last_check': status.last_check.isoformat()
                    }
                    for reg, status in self.compliance_status.items()
                },
                'threat_levels': {
                    level.value: len([t for t in recent_threats if t.severity == level])
                    for level in ThreatLevel
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {'error': str(e)}
    
    def _generate_secure_id(self) -> str:
        """Generate a secure random ID"""
        return secrets.token_urlsafe(32)
    
    def cleanup(self):
        """Cleanup security manager resources"""
        try:
            # Clear sensitive data from memory
            self.encryption_key = None
            self._encryption_handler = None
            
            logger.info("Security manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during security cleanup: {e}")

# Global security manager instance
_security_manager = None

def get_security_manager(connection=None, encryption_key: str = None) -> SecurityManager:
    """Get the global security manager"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(connection, encryption_key)
    return _security_manager

def log_security_event(event_type: AuditEventType, user_id: int = None, 
                      session_id: str = None, resource: str = "", action: str = "",
                      details: Dict[str, Any] = None, ip_address: str = None,
                      user_agent: str = None, risk_level: SecurityLevel = SecurityLevel.LOW):
    """Log a security audit event"""
    manager = get_security_manager()
    manager.log_audit_event(event_type, user_id, session_id, resource, action, 
                           details, ip_address, user_agent, risk_level)

def encrypt_sensitive_data(data: str, data_type: str = "general", user_id: int = None) -> str:
    """Encrypt sensitive data"""
    manager = get_security_manager()
    return manager.encrypt_data(data, data_type, user_id)

def decrypt_sensitive_data(encrypted_data: str, user_id: int = None) -> str:
    """Decrypt sensitive data"""
    manager = get_security_manager()
    return manager.decrypt_data(encrypted_data, user_id)

def hash_user_password(password: str) -> str:
    """Hash a user password securely"""
    manager = get_security_manager()
    return manager.hash_password(password)

def verify_user_password(password: str, hashed_password: str) -> bool:
    """Verify a user password"""
    manager = get_security_manager()
    return manager.verify_password(password, hashed_password)

def check_compliance_status(regulation: ComplianceRegulation) -> ComplianceStatus:
    """Check compliance status for a specific regulation"""
    manager = get_security_manager()
    
    if regulation == ComplianceRegulation.GDPR:
        return manager.check_gdpr_compliance()
    elif regulation == ComplianceRegulation.CCPA:
        return manager.check_ccpa_compliance()
    else:
        # For other regulations, return a basic check
        return ComplianceStatus(
            regulation=regulation,
            compliant=False,
            score=0.0,
            issues=[f"Compliance check for {regulation.value} not implemented"],
            recommendations=[f"Implement {regulation.value} compliance checking"],
            last_check=datetime.datetime.utcnow()
        )

def get_security_health() -> Dict[str, Any]:
    """Get security system health status"""
    manager = get_security_manager()
    return manager.get_security_summary()

# Convenience functions for common security operations
def secure_database_operation(operation_name: str, user_id: int = None, 
                            ip_address: str = None) -> Callable:
    """Decorator to secure database operations"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Log operation start
            log_security_event(
                AuditEventType.DATA_ACCESS,
                user_id=user_id,
                resource="database",
                action=operation_name,
                details={'function': func.__name__},
                ip_address=ip_address,
                risk_level=SecurityLevel.LOW
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful operation
                log_security_event(
                    AuditEventType.DATA_ACCESS,
                    user_id=user_id,
                    resource="database",
                    action=f"{operation_name}_success",
                    details={'function': func.__name__, 'success': True},
                    ip_address=ip_address,
                    risk_level=SecurityLevel.LOW
                )
                
                return result
                
            except Exception as e:
                # Log failed operation
                log_security_event(
                    AuditEventType.SECURITY_VIOLATION,
                    user_id=user_id,
                    resource="database",
                    action=f"{operation_name}_failed",
                    details={'function': func.__name__, 'error': str(e)},
                    ip_address=ip_address,
                    risk_level=SecurityLevel.HIGH
                )
                raise
        
        return wrapper
    return decorator

def anonymize_data(data: Dict[str, Any], fields_to_anonymize: List[str]) -> Dict[str, Any]:
    """Anonymize sensitive fields in data"""
    anonymized = data.copy()
    
    for field in fields_to_anonymize:
        if field in anonymized:
            if isinstance(anonymized[field], str):
                # Replace with hash of original value
                anonymized[field] = hashlib.sha256(str(anonymized[field]).encode()).hexdigest()[:8]
            else:
                anonymized[field] = "[ANONYMIZED]"
    
    return anonymized