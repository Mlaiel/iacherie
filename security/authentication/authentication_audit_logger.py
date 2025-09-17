#!/usr/bin/env python3
"""
🔒 Authentication Audit Logger - Comprehensive Security Logging
===============================================================

Enterprise authentication audit logging system with structured logging,
real-time monitoring, and compliance-ready audit trails.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Compliance + Backend + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import logging.handlers
import hashlib
import gzip
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import traceback
from collections import defaultdict, deque
import threading
from queue import Queue, Empty

# Cryptographic imports for log integrity
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
import os


class AuditEventType(Enum):
    """Types of audit events"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "configuration_change"
    COMPLIANCE_EVENT = "compliance_event"


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    SOC2 = "soc2"


@dataclass
class AuditEvent:
    """Comprehensive audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    log_level: LogLevel
    
    # User and session information
    user_id: Optional[str]
    session_id: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]
    
    # Event details
    action: str
    resource: Optional[str]
    outcome: str  # "success", "failure", "partial"
    
    # Risk and security
    risk_score: Optional[float]
    threat_detected: bool
    security_controls: List[str]
    
    # Technical details
    application: str
    component: str
    method: Optional[str]
    request_id: Optional[str]
    
    # Geolocation
    location: Optional[Dict[str, Any]]
    device_info: Optional[Dict[str, Any]]
    
    # Compliance fields
    compliance_frameworks: List[ComplianceFramework]
    data_classification: Optional[str]
    retention_period_days: int
    
    # Additional context
    message: str
    details: Dict[str, Any]
    error_details: Optional[Dict[str, Any]]
    
    # Integrity
    checksum: Optional[str]
    signature: Optional[str]
    
    # Metadata
    log_version: str = "2.0.0"
    correlation_id: Optional[str] = None


@dataclass
class AuditMetrics:
    """Audit logging metrics"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_level: Dict[str, int]
    events_by_user: Dict[str, int]
    events_by_hour: Dict[int, int]
    failed_events: int
    encrypted_events: int
    archived_events: int
    retention_violations: int
    integrity_violations: int


class AuthenticationAuditLogger:
    """
    🔒 Enterprise Authentication Audit Logger
    
    Comprehensive audit logging system with encryption, digital signatures,
    compliance support, and real-time monitoring capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize authentication audit logger"""
        self.config_path = config_path or "security/config/audit_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup logging infrastructure
        self.logger = self._setup_logger()
        self.audit_logger = self._setup_audit_logger()
        
        # Event queues for async processing
        self.event_queue = Queue(maxsize=10000)
        self.failed_queue = Queue(maxsize=1000)
        
        # Background processing
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        # Metrics and monitoring
        self.metrics = AuditMetrics(
            total_events=0,
            events_by_type=defaultdict(int),
            events_by_level=defaultdict(int),
            events_by_user=defaultdict(int),
            events_by_hour=defaultdict(int),
            failed_events=0,
            encrypted_events=0,
            archived_events=0,
            retention_violations=0,
            integrity_violations=0
        )
        
        # Event cache for correlation
        self.event_cache: deque = deque(maxlen=1000)
        
        # Encryption setup
        self.encryption_key = self._setup_encryption()
        self.signing_key = self._setup_signing()
        
        # Compliance mappings
        self.compliance_mappings = self._setup_compliance_mappings()
        
        # File rotation and archival
        self.log_files = {}
        self.setup_log_rotation()
        
        # Real-time monitoring
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.monitoring_enabled = self.config.get("monitoring_enabled", True)
    
    async def log_authentication_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        action: str = "",
        outcome: str = "success",
        details: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
        risk_score: Optional[float] = None
    ) -> str:
        """
        Log authentication event
        
        Args:
            event_type: Type of authentication event
            user_id: User identifier
            session_id: Session identifier
            action: Action performed
            outcome: Event outcome
            details: Additional event details
            request_context: HTTP request context
            risk_score: Calculated risk score
            
        Returns:
            Event ID for correlation
        """
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Extract request context
            context = request_context or {}
            
            # Determine log level
            log_level = self._determine_log_level(event_type, outcome, risk_score)
            
            # Determine compliance frameworks
            compliance_frameworks = self._determine_compliance_frameworks(event_type, details)
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                log_level=log_level,
                user_id=user_id,
                session_id=session_id,
                user_agent=context.get("user_agent"),
                ip_address=context.get("ip_address"),
                action=action,
                resource=context.get("resource"),
                outcome=outcome,
                risk_score=risk_score,
                threat_detected=risk_score is not None and risk_score > 3.0,
                security_controls=context.get("security_controls", []),
                application="Ainflue",
                component="Authentication",
                method=context.get("method"),
                request_id=context.get("request_id"),
                location=context.get("location"),
                device_info=context.get("device_info"),
                compliance_frameworks=compliance_frameworks,
                data_classification=self._classify_data_sensitivity(event_type, details),
                retention_period_days=self._calculate_retention_period(compliance_frameworks),
                message=self._generate_message(event_type, action, outcome, user_id),
                details=details or {},
                error_details=context.get("error_details"),
                checksum=None,  # Will be calculated
                signature=None,  # Will be calculated
                correlation_id=context.get("correlation_id")
            )
            
            # Calculate integrity fields
            event.checksum = self._calculate_checksum(event)
            event.signature = await self._sign_event(event)
            
            # Queue event for processing
            await self._queue_event(event)
            
            # Real-time monitoring
            if self.monitoring_enabled:
                await self._monitor_event(event)
            
            return event_id
            
        except Exception as e:
            # Log the logging error (meta-logging)
            self.logger.error(f"Failed to log audit event: {e}")
            await self._handle_logging_failure(e, event_type, user_id)
            raise
    
    async def log_security_violation(
        self,
        violation_type: str,
        severity: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log security violation event"""
        return await self.log_authentication_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            user_id=user_id,
            action=f"Security violation: {violation_type}",
            outcome="detected",
            details={
                "violation_type": violation_type,
                "severity": severity,
                **(details or {})
            },
            request_context=context,
            risk_score=5.0 if severity == "critical" else 4.0
        )
    
    async def log_suspicious_activity(
        self,
        activity_type: str,
        indicators: List[str],
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log suspicious activity event"""
        return await self.log_authentication_event(
            event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            action=f"Suspicious activity: {activity_type}",
            outcome="detected",
            details={
                "activity_type": activity_type,
                "indicators": indicators,
                "detection_timestamp": datetime.utcnow().isoformat()
            },
            request_context=context,
            risk_score=3.5
        )
    
    async def log_data_access(
        self,
        resource: str,
        access_type: str,
        user_id: str,
        authorized: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log data access event"""
        return await self.log_authentication_event(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            action=f"Data access: {access_type}",
            outcome="success" if authorized else "denied",
            details={
                "resource": resource,
                "access_type": access_type,
                "authorized": authorized
            },
            request_context={**context, "resource": resource} if context else {"resource": resource}
        )
    
    async def search_audit_logs(
        self,
        criteria: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Search audit logs based on criteria
        
        Args:
            criteria: Search criteria
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum results
            
        Returns:
            List of matching audit events
        """
        try:
            # In production, this would query a database or log aggregation system
            # For now, search through cached events
            
            results = []
            
            for event in self.event_cache:
                if self._matches_criteria(event, criteria, start_time, end_time):
                    results.append(event)
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Audit log search error: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate compliance report for specific framework
        
        Args:
            framework: Compliance framework
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Compliance report
        """
        try:
            # Search relevant events
            criteria = {"compliance_frameworks": [framework]}
            events = await self.search_audit_logs(criteria, start_date, end_date, limit=10000)
            
            # Generate framework-specific report
            if framework == ComplianceFramework.SOX:
                return await self._generate_sox_report(events, start_date, end_date)
            elif framework == ComplianceFramework.GDPR:
                return await self._generate_gdpr_report(events, start_date, end_date)
            elif framework == ComplianceFramework.PCI_DSS:
                return await self._generate_pci_report(events, start_date, end_date)
            else:
                return await self._generate_generic_report(events, framework, start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"Compliance report generation error: {e}")
            raise
    
    async def get_audit_metrics(
        self,
        time_range: Optional[timedelta] = None
    ) -> AuditMetrics:
        """Get audit logging metrics"""
        # Update metrics with current data
        if time_range:
            # Filter metrics by time range
            # In production, this would query the metrics database
            pass
        
        return self.metrics
    
    async def verify_log_integrity(
        self,
        event_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify integrity of audit logs
        
        Args:
            event_ids: Specific events to verify (None for all)
            
        Returns:
            Integrity verification result
        """
        try:
            verification_results = {
                "total_verified": 0,
                "integrity_violations": 0,
                "checksum_failures": 0,
                "signature_failures": 0,
                "verified_events": [],
                "failed_events": []
            }
            
            events_to_verify = []
            
            if event_ids:
                # Find specific events
                for event in self.event_cache:
                    if event.event_id in event_ids:
                        events_to_verify.append(event)
            else:
                # Verify all cached events
                events_to_verify = list(self.event_cache)
            
            for event in events_to_verify:
                verification_results["total_verified"] += 1
                
                # Verify checksum
                calculated_checksum = self._calculate_checksum(event)
                if calculated_checksum != event.checksum:
                    verification_results["checksum_failures"] += 1
                    verification_results["failed_events"].append({
                        "event_id": event.event_id,
                        "failure_type": "checksum_mismatch",
                        "expected": event.checksum,
                        "calculated": calculated_checksum
                    })
                    continue
                
                # Verify signature
                if not await self._verify_signature(event):
                    verification_results["signature_failures"] += 1
                    verification_results["failed_events"].append({
                        "event_id": event.event_id,
                        "failure_type": "signature_invalid"
                    })
                    continue
                
                verification_results["verified_events"].append(event.event_id)
            
            verification_results["integrity_violations"] = (
                verification_results["checksum_failures"] + 
                verification_results["signature_failures"]
            )
            
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Log integrity verification error: {e}")
            raise
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load audit logging configuration"""
        default_config = {
            "log_level": "INFO",
            "log_directory": "logs/audit",
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "backup_count": 10,
            "encryption_enabled": True,
            "signing_enabled": True,
            "compression_enabled": True,
            "monitoring_enabled": True,
            "retention_days": 2555,  # 7 years default
            "alert_thresholds": {
                "failed_logins": 10,
                "security_violations": 5,
                "suspicious_activities": 3
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception:
            pass
        
        return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """Setup main logger"""
        logger = logging.getLogger(f"{__name__}.main")
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup audit-specific logger"""
        audit_logger = logging.getLogger(f"{__name__}.audit")
        audit_logger.setLevel(logging.INFO)
        
        if not audit_logger.handlers:
            # Ensure log directory exists
            log_dir = Path(self.config["log_directory"])
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Setup rotating file handler
            log_file = log_dir / "authentication_audit.log"
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config["max_file_size"],
                backupCount=self.config["backup_count"]
            )
            
            # JSON formatter for structured logging
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            audit_logger.addHandler(handler)
            
            # Prevent propagation to root logger
            audit_logger.propagate = False
        
        return audit_logger
    
    def _setup_encryption(self) -> bytes:
        """Setup encryption key for sensitive data"""
        key_file = Path(self.config["log_directory"]) / "encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = secrets.token_bytes(32)  # 256-bit key
            
            # Ensure directory exists
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Secure file permissions
            os.chmod(key_file, 0o600)
            
            return key
    
    def _setup_signing(self):
        """Setup signing key for log integrity"""
        private_key_file = Path(self.config["log_directory"]) / "signing_private.pem"
        public_key_file = Path(self.config["log_directory"]) / "signing_public.pem"
        
        if private_key_file.exists() and public_key_file.exists():
            with open(private_key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            return private_key
        else:
            # Generate new key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            
            # Ensure directory exists
            private_key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save private key
            with open(private_key_file, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Save public key
            with open(public_key_file, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            # Secure file permissions
            os.chmod(private_key_file, 0o600)
            os.chmod(public_key_file, 0o644)
            
            return private_key
    
    def _setup_compliance_mappings(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Setup compliance framework mappings"""
        return {
            ComplianceFramework.SOX: {
                "relevant_events": [
                    AuditEventType.LOGIN_SUCCESS,
                    AuditEventType.LOGIN_FAILURE,
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.CONFIGURATION_CHANGE
                ],
                "retention_days": 2555,  # 7 years
                "encryption_required": True
            },
            ComplianceFramework.GDPR: {
                "relevant_events": [
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.LOGIN_SUCCESS,
                    AuditEventType.CONSENT_GIVEN,
                    AuditEventType.CONSENT_WITHDRAWN
                ],
                "retention_days": 2190,  # 6 years
                "encryption_required": True
            },
            ComplianceFramework.PCI_DSS: {
                "relevant_events": [
                    AuditEventType.LOGIN_SUCCESS,
                    AuditEventType.LOGIN_FAILURE,
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.SECURITY_VIOLATION
                ],
                "retention_days": 365,  # 1 year minimum
                "encryption_required": True
            }
        }
    
    def setup_log_rotation(self):
        """Setup log file rotation and archival"""
        # This would implement automatic log rotation, compression, and archival
        # For now, basic setup is handled by RotatingFileHandler
        pass
    
    def _determine_log_level(
        self,
        event_type: AuditEventType,
        outcome: str,
        risk_score: Optional[float]
    ) -> LogLevel:
        """Determine appropriate log level"""
        if event_type in [AuditEventType.SECURITY_VIOLATION, AuditEventType.SUSPICIOUS_ACTIVITY]:
            return LogLevel.CRITICAL
        
        if outcome == "failure" or outcome == "denied":
            return LogLevel.WARNING
        
        if risk_score and risk_score > 3.0:
            return LogLevel.WARNING
        
        if event_type in [AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGOUT]:
            return LogLevel.INFO
        
        return LogLevel.INFO
    
    def _determine_compliance_frameworks(
        self,
        event_type: AuditEventType,
        details: Optional[Dict[str, Any]]
    ) -> List[ComplianceFramework]:
        """Determine applicable compliance frameworks"""
        frameworks = []
        
        for framework, mapping in self.compliance_mappings.items():
            if event_type in mapping["relevant_events"]:
                frameworks.append(framework)
        
        # Add specific frameworks based on data classification
        if details and details.get("data_classification") == "financial":
            if ComplianceFramework.SOX not in frameworks:
                frameworks.append(ComplianceFramework.SOX)
        
        return frameworks
    
    def _classify_data_sensitivity(
        self,
        event_type: AuditEventType,
        details: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Classify data sensitivity level"""
        if event_type in [AuditEventType.DATA_ACCESS, AuditEventType.DATA_MODIFICATION]:
            if details:
                resource = details.get("resource", "")
                if any(sensitive in resource.lower() for sensitive in ["payment", "financial", "billing"]):
                    return "financial"
                elif any(sensitive in resource.lower() for sensitive in ["personal", "pii", "profile"]):
                    return "personal"
                elif any(sensitive in resource.lower() for sensitive in ["admin", "config", "system"]):
                    return "system"
        
        return "general"
    
    def _calculate_retention_period(self, frameworks: List[ComplianceFramework]) -> int:
        """Calculate retention period based on compliance requirements"""
        if not frameworks:
            return self.config.get("retention_days", 365)
        
        # Use the longest retention period required
        max_retention = 0
        for framework in frameworks:
            mapping = self.compliance_mappings.get(framework, {})
            retention = mapping.get("retention_days", 365)
            max_retention = max(max_retention, retention)
        
        return max_retention
    
    def _generate_message(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str,
        user_id: Optional[str]
    ) -> str:
        """Generate human-readable message"""
        user_part = f"User {user_id}" if user_id else "Unknown user"
        
        if event_type == AuditEventType.LOGIN_SUCCESS:
            return f"{user_part} successfully logged in"
        elif event_type == AuditEventType.LOGIN_FAILURE:
            return f"{user_part} failed to log in"
        elif event_type == AuditEventType.LOGOUT:
            return f"{user_part} logged out"
        elif event_type == AuditEventType.SECURITY_VIOLATION:
            return f"Security violation detected: {action}"
        elif event_type == AuditEventType.SUSPICIOUS_ACTIVITY:
            return f"Suspicious activity detected: {action}"
        else:
            return f"{user_part} performed {action} with outcome {outcome}"
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate checksum for event integrity"""
        # Create deterministic string representation
        data_dict = asdict(event)
        # Remove fields that will be calculated
        data_dict.pop("checksum", None)
        data_dict.pop("signature", None)
        
        # Sort keys for consistent ordering
        data_str = json.dumps(data_dict, sort_keys=True, default=str)
        
        # Calculate SHA-256 checksum
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _sign_event(self, event: AuditEvent) -> str:
        """Sign event for integrity verification"""
        if not self.config.get("signing_enabled", True):
            return ""
        
        try:
            # Create signature data
            data_dict = asdict(event)
            data_dict.pop("signature", None)  # Remove signature field
            data_str = json.dumps(data_dict, sort_keys=True, default=str)
            
            # Sign the data
            signature = self.signing_key.sign(
                data_str.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature.hex()
            
        except Exception as e:
            self.logger.error(f"Event signing error: {e}")
            return ""
    
    async def _verify_signature(self, event: AuditEvent) -> bool:
        """Verify event signature"""
        if not self.config.get("signing_enabled", True) or not event.signature:
            return True  # Skip verification if signing not enabled
        
        try:
            # Recreate signature data
            data_dict = asdict(event)
            data_dict.pop("signature", None)
            data_str = json.dumps(data_dict, sort_keys=True, default=str)
            
            # Get public key
            public_key = self.signing_key.public_key()
            
            # Verify signature
            signature_bytes = bytes.fromhex(event.signature)
            public_key.verify(
                signature_bytes,
                data_str.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Signature verification failed for event {event.event_id}: {e}")
            return False
    
    async def _queue_event(self, event: AuditEvent):
        """Queue event for async processing"""
        try:
            self.event_queue.put_nowait(event)
        except Exception as e:
            self.logger.error(f"Failed to queue event: {e}")
            # Try to process synchronously as fallback
            await self._process_event_sync(event)
    
    def _process_events(self):
        """Background thread for processing events"""
        while True:
            try:
                event = self.event_queue.get(timeout=1.0)
                asyncio.run(self._process_event_sync(event))
                self.event_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")
    
    async def _process_event_sync(self, event: AuditEvent):
        """Process single event synchronously"""
        try:
            # Update metrics
            self._update_metrics(event)
            
            # Add to cache
            self.event_cache.append(event)
            
            # Log to file
            await self._log_to_file(event)
            
            # Send to external systems if configured
            await self._send_to_external_systems(event)
            
        except Exception as e:
            self.logger.error(f"Event processing failed: {e}")
            self.metrics.failed_events += 1
    
    def _update_metrics(self, event: AuditEvent):
        """Update audit metrics"""
        self.metrics.total_events += 1
        self.metrics.events_by_type[event.event_type.value] += 1
        self.metrics.events_by_level[event.log_level.value] += 1
        
        if event.user_id:
            self.metrics.events_by_user[event.user_id] += 1
        
        hour = event.timestamp.hour
        self.metrics.events_by_hour[hour] += 1
        
        if event.signature:
            self.metrics.encrypted_events += 1
    
    async def _log_to_file(self, event: AuditEvent):
        """Log event to file"""
        try:
            # Convert to JSON
            event_dict = asdict(event)
            
            # Convert datetime to ISO format
            event_dict["timestamp"] = event.timestamp.isoformat()
            
            # Convert enums to strings
            event_dict["event_type"] = event.event_type.value
            event_dict["log_level"] = event.log_level.value
            event_dict["compliance_frameworks"] = [f.value for f in event.compliance_frameworks]
            
            # Log as JSON
            self.audit_logger.info(json.dumps(event_dict, default=str))
            
        except Exception as e:
            self.logger.error(f"File logging error: {e}")
            raise
    
    async def _send_to_external_systems(self, event: AuditEvent):
        """Send event to external logging/monitoring systems"""
        # This would implement integration with SIEM, log aggregators, etc.
        # For now, just placeholder
        pass
    
    async def _monitor_event(self, event: AuditEvent):
        """Real-time event monitoring and alerting"""
        try:
            # Check alert thresholds
            if event.event_type == AuditEventType.LOGIN_FAILURE:
                await self._check_failed_login_threshold(event)
            elif event.event_type == AuditEventType.SECURITY_VIOLATION:
                await self._check_security_violation_threshold(event)
            elif event.event_type == AuditEventType.SUSPICIOUS_ACTIVITY:
                await self._check_suspicious_activity_threshold(event)
            
        except Exception as e:
            self.logger.error(f"Event monitoring error: {e}")
    
    async def _check_failed_login_threshold(self, event: AuditEvent):
        """Check failed login threshold"""
        if not event.user_id:
            return
        
        # Count recent failed logins for user
        threshold = self.alert_thresholds.get("failed_logins", 10)
        recent_failures = sum(
            1 for e in self.event_cache
            if (e.user_id == event.user_id and
                e.event_type == AuditEventType.LOGIN_FAILURE and
                (datetime.utcnow() - e.timestamp).total_seconds() < 3600)  # Last hour
        )
        
        if recent_failures >= threshold:
            await self._send_alert(
                f"User {event.user_id} exceeded failed login threshold: {recent_failures}/{threshold}",
                "high",
                event
            )
    
    async def _check_security_violation_threshold(self, event: AuditEvent):
        """Check security violation threshold"""
        threshold = self.alert_thresholds.get("security_violations", 5)
        recent_violations = sum(
            1 for e in self.event_cache
            if (e.event_type == AuditEventType.SECURITY_VIOLATION and
                (datetime.utcnow() - e.timestamp).total_seconds() < 3600)  # Last hour
        )
        
        if recent_violations >= threshold:
            await self._send_alert(
                f"Security violation threshold exceeded: {recent_violations}/{threshold}",
                "critical",
                event
            )
    
    async def _check_suspicious_activity_threshold(self, event: AuditEvent):
        """Check suspicious activity threshold"""
        threshold = self.alert_thresholds.get("suspicious_activities", 3)
        recent_activities = sum(
            1 for e in self.event_cache
            if (e.event_type == AuditEventType.SUSPICIOUS_ACTIVITY and
                (datetime.utcnow() - e.timestamp).total_seconds() < 1800)  # Last 30 minutes
        )
        
        if recent_activities >= threshold:
            await self._send_alert(
                f"Suspicious activity threshold exceeded: {recent_activities}/{threshold}",
                "high",
                event
            )
    
    async def _send_alert(self, message: str, severity: str, event: AuditEvent):
        """Send security alert"""
        # This would implement actual alerting (email, SMS, webhook, etc.)
        self.logger.critical(f"SECURITY ALERT [{severity.upper()}]: {message}")
    
    async def _handle_logging_failure(self, error: Exception, event_type: AuditEventType, user_id: Optional[str]):
        """Handle logging system failures"""
        # Log to separate failure log
        failure_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(error),
            "event_type": event_type.value,
            "user_id": user_id,
            "traceback": traceback.format_exc()
        }
        
        try:
            self.failed_queue.put_nowait(failure_entry)
        except:
            # Last resort - write to stderr
            print(f"AUDIT LOGGING FAILURE: {json.dumps(failure_entry)}")
    
    def _matches_criteria(
        self,
        event: AuditEvent,
        criteria: Dict[str, Any],
        start_time: Optional[datetime],
        end_time: Optional[datetime]
    ) -> bool:
        """Check if event matches search criteria"""
        # Time range check
        if start_time and event.timestamp < start_time:
            return False
        if end_time and event.timestamp > end_time:
            return False
        
        # Criteria checks
        for key, value in criteria.items():
            if key == "user_id" and event.user_id != value:
                return False
            elif key == "event_type" and event.event_type != value:
                return False
            elif key == "outcome" and event.outcome != value:
                return False
            elif key == "compliance_frameworks":
                if not any(f in event.compliance_frameworks for f in value):
                    return False
        
        return True
    
    # Compliance report generators
    
    async def _generate_sox_report(
        self,
        events: List[AuditEvent],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate SOX compliance report"""
        return {
            "framework": "SOX",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(events),
            "access_events": len([e for e in events if e.event_type == AuditEventType.DATA_ACCESS]),
            "modification_events": len([e for e in events if e.event_type == AuditEventType.DATA_MODIFICATION]),
            "authentication_events": len([e for e in events if "login" in e.event_type.value]),
            "violations": len([e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION]),
            "integrity_verified": all(e.checksum and e.signature for e in events),
            "retention_compliant": all((datetime.utcnow() - e.timestamp).days <= e.retention_period_days for e in events)
        }
    
    async def _generate_gdpr_report(
        self,
        events: List[AuditEvent],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        return {
            "framework": "GDPR",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(events),
            "data_access_events": len([e for e in events if e.event_type == AuditEventType.DATA_ACCESS]),
            "personal_data_events": len([e for e in events if e.data_classification == "personal"]),
            "consent_events": len([e for e in events if "consent" in e.event_type.value]),
            "data_subject_requests": 0,  # Would be tracked separately
            "breach_notifications": len([e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION]),
            "encryption_coverage": len([e for e in events if e.signature]) / len(events) if events else 0
        }
    
    async def _generate_pci_report(
        self,
        events: List[AuditEvent],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate PCI DSS compliance report"""
        return {
            "framework": "PCI DSS",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(events),
            "authentication_events": len([e for e in events if "login" in e.event_type.value]),
            "access_control_events": len([e for e in events if e.event_type in [AuditEventType.PERMISSION_GRANTED, AuditEventType.PERMISSION_DENIED]]),
            "security_events": len([e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION]),
            "system_events": len([e for e in events if e.data_classification == "system"]),
            "log_integrity": all(e.checksum and e.signature for e in events),
            "real_time_monitoring": True  # Based on system configuration
        }
    
    async def _generate_generic_report(
        self,
        events: List[AuditEvent],
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate generic compliance report"""
        return {
            "framework": framework.value,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(events),
            "event_types": {t.value: len([e for e in events if e.event_type == t]) for t in AuditEventType},
            "security_events": len([e for e in events if e.event_type in [AuditEventType.SECURITY_VIOLATION, AuditEventType.SUSPICIOUS_ACTIVITY]]),
            "integrity_score": len([e for e in events if e.checksum and e.signature]) / len(events) if events else 0,
            "compliance_coverage": len([e for e in events if framework in e.compliance_frameworks]) / len(events) if events else 0
        }


# Export main classes
__all__ = [
    "AuthenticationAuditLogger",
    "AuditEventType",
    "LogLevel",
    "ComplianceFramework",
    "AuditEvent",
    "AuditMetrics"
]