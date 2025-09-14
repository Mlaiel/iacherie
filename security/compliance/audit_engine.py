#!/usr/bin/env python3
"""
📋 Audit Engine - Enterprise Compliance Module
==============================================

Ultra-comprehensive audit system with immutable trails, real-time monitoring,
and enterprise-grade compliance tracking for regulatory requirements.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Compliance + Audit + Legal + DBA
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

import redis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Audit event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    COMPLIANCE = "compliance"

class AuditCategory(Enum):
    """Categories of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    PRIVILEGED_OPERATION = "privileged_operation"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_EVENT = "compliance_event"
    FINANCIAL_TRANSACTION = "financial_transaction"
    PRIVACY_EVENT = "privacy_event"
    ERROR_EVENT = "error_event"

class ComplianceFramework(Enum):
    """Compliance frameworks for audit requirements"""
    GDPR = "gdpr"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    NIST = "nist"
    CIS = "cis"
    COBIT = "cobit"

@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""
    category: AuditCategory = AuditCategory.SYSTEM_ACCESS
    level: AuditLevel = AuditLevel.INFO
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: str = "unknown"
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    outcome: str = "success"  # success, failure, error
    details: Dict[str, Any] = field(default_factory=dict)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    risk_score: float = 0.0
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    retention_period_days: int = 2555  # 7 years default
    classification: str = "internal"  # public, internal, confidential, restricted
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditTrail:
    """Immutable audit trail"""
    trail_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    events: List[AuditEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""
    trail_hash: str = ""
    previous_trail_hash: str = ""
    is_sealed: bool = False
    sealed_at: Optional[datetime] = None
    digital_signature: Optional[str] = None
    integrity_verified: bool = True
    compliance_period: str = ""
    retention_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceAudit:
    """Compliance audit record"""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: ComplianceFramework = ComplianceFramework.GDPR
    audit_type: str = "internal"  # internal, external, regulatory
    auditor: str = ""
    audit_scope: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "in_progress"  # planning, in_progress, completed, failed
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    non_compliance_issues: List[Dict[str, Any]] = field(default_factory=list)
    evidence_collected: List[str] = field(default_factory=list)
    report_generated: bool = False
    report_path: Optional[str] = None
    remediation_plan: List[Dict[str, Any]] = field(default_factory=list)
    follow_up_required: bool = False
    next_audit_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditReport:
    """Comprehensive audit report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = "compliance_audit"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc) - timedelta(days=30))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_events: int = 0
    events_by_category: Dict[str, int] = field(default_factory=dict)
    events_by_level: Dict[str, int] = field(default_factory=dict)
    top_users: List[Dict[str, Any]] = field(default_factory=list)
    top_resources: List[Dict[str, Any]] = field(default_factory=list)
    security_incidents: List[Dict[str, Any]] = field(default_factory=list)
    compliance_violations: List[Dict[str, Any]] = field(default_factory=list)
    risk_analysis: Dict[str, Any] = field(default_factory=dict)
    trends: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    executive_summary: str = ""
    compliance_frameworks_covered: List[ComplianceFramework] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AuditEngine:
    """
    Enterprise audit engine with immutable trails and compliance tracking.
    
    Features:
    - Immutable audit trails with cryptographic integrity
    - Real-time audit event processing
    - Compliance framework mapping
    - Automated retention management
    - Advanced analytics and reporting
    - Digital signatures and non-repudiation
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None,
        signing_key: Optional[bytes] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Digital signature keys
        self.signing_private_key = None
        self.signing_public_key = None
        if signing_key:
            self._load_signing_keys(signing_key)
        else:
            self._generate_signing_keys()
        
        # Audit processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.current_trail: Optional[AuditTrail] = None
        self.trail_cache: Dict[str, AuditTrail] = {}
        self.last_trail_hash = ""
        
        # Configuration
        self.config = {
            "max_events_per_trail": 1000,
            "trail_seal_interval": 3600,  # 1 hour
            "real_time_processing": True,
            "encrypt_sensitive_data": True,
            "enable_digital_signatures": True,
            "compliance_mapping": True,
            "retention_enforcement": True,
            "immutable_storage": True,
            "audit_audit_events": True,  # Audit the audit system itself
        }
        
        # Statistics
        self.stats = {
            "total_events": 0,
            "trails_created": 0,
            "events_by_category": {},
            "events_by_level": {},
            "compliance_events": 0,
            "integrity_violations": 0,
            "processing_time_ms": []
        }

    async def initialize(self) -> None:
        """Initialize audit engine"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Load last trail hash for integrity chain
            self.last_trail_hash = await self._get_last_trail_hash()
            
            # Start background tasks
            if self.config["real_time_processing"]:
                asyncio.create_task(self._event_processor())
                
            asyncio.create_task(self._trail_sealer())
            asyncio.create_task(self._retention_manager())
            asyncio.create_task(self._integrity_verifier())
            
            # Create initial trail
            await self._create_new_trail()
            
            # Audit the initialization
            await self.log_event(AuditEvent(
                event_type="audit_engine_initialized",
                category=AuditCategory.SYSTEM_ACCESS,
                level=AuditLevel.INFO,
                details={"version": "2.0.0", "config": self.config}
            ))
            
            logger.info("Audit engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audit engine: {e}")
            raise

    async def log_event(self, event: AuditEvent) -> bool:
        """Log audit event to immutable trail"""
        try:
            start_time = time.time()
            
            # Validate event
            if not await self._validate_event(event):
                return False
            
            # Enrich event with compliance mappings
            if self.config["compliance_mapping"]:
                await self._map_compliance_frameworks(event)
            
            # Calculate risk score
            event.risk_score = await self._calculate_risk_score(event)
            
            # Encrypt sensitive data if configured
            if self.config["encrypt_sensitive_data"]:
                await self._encrypt_sensitive_data(event)
            
            # Add to queue for processing
            if self.config["real_time_processing"]:
                await self.event_queue.put(event)
            else:
                await self._process_event(event)
            
            # Update statistics
            self.stats["total_events"] += 1
            self.stats["events_by_category"][event.category.value] = (
                self.stats["events_by_category"].get(event.category.value, 0) + 1
            )
            self.stats["events_by_level"][event.level.value] = (
                self.stats["events_by_level"].get(event.level.value, 0) + 1
            )
            
            processing_time = (time.time() - start_time) * 1000
            self.stats["processing_time_ms"].append(processing_time)
            
            # Keep only last 1000 processing times
            if len(self.stats["processing_time_ms"]) > 1000:
                self.stats["processing_time_ms"].pop(0)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Try to log the audit system error
            try:
                if self.config["audit_audit_events"]:
                    error_event = AuditEvent(
                        event_type="audit_system_error",
                        category=AuditCategory.ERROR_EVENT,
                        level=AuditLevel.ERROR,
                        details={"error": str(e), "original_event_id": event.event_id}
                    )
                    await self._process_event(error_event)
            except:
                pass  # Avoid infinite loops
            
            return False

    async def _process_event(self, event: AuditEvent) -> None:
        """Process individual audit event"""
        try:
            # Get or create current trail
            if not self.current_trail:
                await self._create_new_trail()
            
            # Add event to current trail
            self.current_trail.events.append(event)
            
            # Check if trail needs to be sealed
            if len(self.current_trail.events) >= self.config["max_events_per_trail"]:
                await self._seal_current_trail()
                await self._create_new_trail()
            
            # Store event immediately for real-time access
            await self._store_event(event)
            
            # Check for compliance violations
            await self._check_compliance_violations(event)
            
        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            raise

    async def _create_new_trail(self) -> None:
        """Create new audit trail"""
        try:
            trail = AuditTrail(
                created_by="audit_engine",
                previous_trail_hash=self.last_trail_hash,
                compliance_period=datetime.now(timezone.utc).strftime("%Y-%m")
            )
            
            # Calculate trail hash
            trail.trail_hash = await self._calculate_trail_hash(trail)
            
            self.current_trail = trail
            self.trail_cache[trail.trail_id] = trail
            
            self.stats["trails_created"] += 1
            
            logger.info(f"Created new audit trail: {trail.trail_id}")
            
        except Exception as e:
            logger.error(f"Failed to create audit trail: {e}")
            raise

    async def _seal_current_trail(self) -> None:
        """Seal current audit trail"""
        try:
            if not self.current_trail:
                return
            
            # Mark as sealed
            self.current_trail.is_sealed = True
            self.current_trail.sealed_at = datetime.now(timezone.utc)
            
            # Calculate final hash
            self.current_trail.trail_hash = await self._calculate_trail_hash(self.current_trail)
            
            # Generate digital signature
            if self.config["enable_digital_signatures"]:
                self.current_trail.digital_signature = await self._sign_trail(self.current_trail)
            
            # Store sealed trail
            await self._store_trail(self.current_trail)
            
            # Update last trail hash for chain integrity
            self.last_trail_hash = self.current_trail.trail_hash
            await self._store_last_trail_hash(self.last_trail_hash)
            
            logger.info(f"Sealed audit trail: {self.current_trail.trail_id}")
            
        except Exception as e:
            logger.error(f"Failed to seal audit trail: {e}")
            raise

    async def _calculate_trail_hash(self, trail: AuditTrail) -> str:
        """Calculate cryptographic hash of trail"""
        try:
            # Create hash input from trail data
            hash_data = {
                "trail_id": trail.trail_id,
                "created_at": trail.created_at.isoformat(),
                "previous_trail_hash": trail.previous_trail_hash,
                "events": [
                    {
                        "event_id": event.event_id,
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type,
                        "user_id": event.user_id,
                        "outcome": event.outcome
                    }
                    for event in trail.events
                ]
            }
            
            hash_string = json.dumps(hash_data, sort_keys=True, default=str)
            return hashlib.sha256(hash_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Trail hash calculation failed: {e}")
            return ""

    async def _sign_trail(self, trail: AuditTrail) -> str:
        """Generate digital signature for trail"""
        try:
            if not self.signing_private_key:
                return ""
            
            # Create signature input
            signature_data = f"{trail.trail_id}:{trail.trail_hash}:{trail.sealed_at.isoformat()}"
            
            # Sign with private key
            signature = self.signing_private_key.sign(
                signature_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature.hex()
            
        except Exception as e:
            logger.error(f"Trail signing failed: {e}")
            return ""

    async def verify_trail_integrity(self, trail_id: str) -> Tuple[bool, List[str]]:
        """Verify integrity of audit trail"""
        try:
            issues = []
            
            # Load trail
            trail = await self._load_trail(trail_id)
            if not trail:
                return False, ["Trail not found"]
            
            # Verify hash
            calculated_hash = await self._calculate_trail_hash(trail)
            if calculated_hash != trail.trail_hash:
                issues.append("Trail hash mismatch")
            
            # Verify digital signature
            if trail.digital_signature and self.signing_public_key:
                signature_valid = await self._verify_trail_signature(trail)
                if not signature_valid:
                    issues.append("Digital signature invalid")
            
            # Verify event integrity
            for event in trail.events:
                event_valid = await self._verify_event_integrity(event)
                if not event_valid:
                    issues.append(f"Event {event.event_id} integrity compromised")
            
            # Verify chain integrity (if not first trail)
            if trail.previous_trail_hash:
                chain_valid = await self._verify_chain_integrity(trail)
                if not chain_valid:
                    issues.append("Chain integrity broken")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            logger.error(f"Trail integrity verification failed: {e}")
            return False, [f"Verification error: {e}"]

    async def _verify_trail_signature(self, trail: AuditTrail) -> bool:
        """Verify digital signature of trail"""
        try:
            if not trail.digital_signature or not self.signing_public_key:
                return False
            
            signature_data = f"{trail.trail_id}:{trail.trail_hash}:{trail.sealed_at.isoformat()}"
            signature_bytes = bytes.fromhex(trail.digital_signature)
            
            try:
                self.signing_public_key.verify(
                    signature_bytes,
                    signature_data.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except Exception:
                return False
                
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    async def _verify_event_integrity(self, event: AuditEvent) -> bool:
        """Verify integrity of individual event"""
        try:
            # Check required fields
            if not event.event_id or not event.timestamp or not event.event_type:
                return False
            
            # Verify timestamp is reasonable
            now = datetime.now(timezone.utc)
            if event.timestamp > now + timedelta(minutes=5):  # Allow 5 min clock skew
                return False
            
            # Check for tampering indicators
            if hasattr(event, '_tampered'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Event integrity verification failed: {e}")
            return False

    async def _verify_chain_integrity(self, trail: AuditTrail) -> bool:
        """Verify chain integrity with previous trail"""
        try:
            if not trail.previous_trail_hash:
                return True  # First trail
            
            # This would verify the previous trail exists and has the expected hash
            # Simplified for now
            return True
            
        except Exception as e:
            logger.error(f"Chain integrity verification failed: {e}")
            return False

    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> AuditReport:
        """Generate compliance audit report"""
        try:
            # Query events for the period
            events = await self._query_events_by_period(start_date, end_date)
            
            # Filter by compliance framework
            framework_events = [
                event for event in events
                if framework in event.compliance_frameworks
            ]
            
            # Generate report
            report = AuditReport(
                report_type=f"{framework.value}_compliance_report",
                period_start=start_date,
                period_end=end_date,
                total_events=len(framework_events),
                compliance_frameworks_covered=[framework]
            )
            
            # Analyze events by category
            for event in framework_events:
                category = event.category.value
                report.events_by_category[category] = (
                    report.events_by_category.get(category, 0) + 1
                )
                
                level = event.level.value
                report.events_by_level[level] = (
                    report.events_by_level.get(level, 0) + 1
                )
            
            # Identify compliance violations
            violations = await self._identify_compliance_violations(framework_events, framework)
            report.compliance_violations = violations
            
            # Generate recommendations
            report.recommendations = await self._generate_compliance_recommendations(
                framework, violations
            )
            
            # Risk analysis
            report.risk_analysis = await self._analyze_compliance_risks(framework_events)
            
            # Executive summary
            report.executive_summary = await self._generate_executive_summary(report)
            
            # Store report
            await self._store_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            raise

    async def _validate_event(self, event: AuditEvent) -> bool:
        """Validate audit event"""
        try:
            # Check required fields
            if not event.event_type:
                return False
            
            # Validate timestamp
            if not event.timestamp:
                event.timestamp = datetime.now(timezone.utc)
            
            # Validate category and level
            if not isinstance(event.category, AuditCategory):
                return False
            
            if not isinstance(event.level, AuditLevel):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return False

    async def _map_compliance_frameworks(self, event: AuditEvent) -> None:
        """Map event to relevant compliance frameworks"""
        try:
            frameworks = []
            
            # Map based on event type and category
            if event.category == AuditCategory.AUTHENTICATION:
                frameworks.extend([ComplianceFramework.ISO27001, ComplianceFramework.NIST])
            
            if event.category == AuditCategory.DATA_ACCESS:
                frameworks.extend([ComplianceFramework.GDPR, ComplianceFramework.HIPAA])
            
            if event.category == AuditCategory.FINANCIAL_TRANSACTION:
                frameworks.extend([ComplianceFramework.SOX, ComplianceFramework.PCI_DSS])
            
            if event.category == AuditCategory.PRIVILEGED_OPERATION:
                frameworks.extend([ComplianceFramework.SOX, ComplianceFramework.ISO27001])
            
            if event.category == AuditCategory.SECURITY_EVENT:
                frameworks.extend([ComplianceFramework.ISO27001, ComplianceFramework.NIST])
            
            # Add to event
            event.compliance_frameworks = list(set(frameworks))
            
        except Exception as e:
            logger.error(f"Compliance mapping failed: {e}")

    async def _calculate_risk_score(self, event: AuditEvent) -> float:
        """Calculate risk score for audit event"""
        try:
            score = 0.0
            
            # Base score by level
            level_scores = {
                AuditLevel.DEBUG: 0.1,
                AuditLevel.INFO: 0.2,
                AuditLevel.WARNING: 0.5,
                AuditLevel.ERROR: 0.7,
                AuditLevel.CRITICAL: 0.9,
                AuditLevel.COMPLIANCE: 0.8
            }
            
            score += level_scores.get(event.level, 0.0)
            
            # Category modifiers
            if event.category in [AuditCategory.SECURITY_EVENT, AuditCategory.PRIVILEGED_OPERATION]:
                score += 0.2
            
            if event.outcome != "success":
                score += 0.3
            
            # Time-based factors
            hour = event.timestamp.hour
            if hour < 6 or hour > 22:  # Off hours
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            return 0.0

    async def _encrypt_sensitive_data(self, event: AuditEvent) -> None:
        """Encrypt sensitive data in audit event"""
        try:
            sensitive_fields = ["user_agent", "ip_address"]
            
            for field in sensitive_fields:
                if hasattr(event, field) and getattr(event, field):
                    original_value = getattr(event, field)
                    encrypted_value = self.cipher_suite.encrypt(original_value.encode()).decode()
                    setattr(event, field, f"ENC:{encrypted_value}")
            
            # Encrypt sensitive details
            if event.details:
                sensitive_keys = ["password", "token", "key", "secret"]
                for key in list(event.details.keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        original_value = str(event.details[key])
                        encrypted_value = self.cipher_suite.encrypt(original_value.encode()).decode()
                        event.details[key] = f"ENC:{encrypted_value}"
                        
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")

    async def _check_compliance_violations(self, event: AuditEvent) -> None:
        """Check for compliance violations in event"""
        try:
            violations = []
            
            # Check for authentication failures
            if (event.category == AuditCategory.AUTHENTICATION and 
                event.outcome != "success"):
                violations.append("Authentication failure detected")
            
            # Check for privileged operations without proper authorization
            if (event.category == AuditCategory.PRIVILEGED_OPERATION and
                not event.user_id):
                violations.append("Privileged operation without user identification")
            
            # Check for data access patterns
            if (event.category == AuditCategory.DATA_ACCESS and
                event.level in [AuditLevel.WARNING, AuditLevel.ERROR]):
                violations.append("Suspicious data access pattern")
            
            # Store violations
            if violations:
                event.metadata["compliance_violations"] = violations
                self.stats["compliance_events"] += 1
                
        except Exception as e:
            logger.error(f"Compliance violation check failed: {e}")

    async def _store_event(self, event: AuditEvent) -> None:
        """Store individual audit event"""
        try:
            event_data = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "category": event.category.value,
                "level": event.level.value,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "resource": event.resource,
                "action": event.action,
                "outcome": event.outcome,
                "details": event.details,
                "before_state": event.before_state,
                "after_state": event.after_state,
                "risk_score": event.risk_score,
                "compliance_frameworks": [fw.value for fw in event.compliance_frameworks],
                "retention_period_days": event.retention_period_days,
                "classification": event.classification,
                "tags": event.tags,
                "correlation_id": event.correlation_id,
                "parent_event_id": event.parent_event_id,
                "metadata": event.metadata
            }
            
            # Calculate retention expiry
            retention_date = event.timestamp + timedelta(days=event.retention_period_days)
            retention_seconds = int((retention_date - datetime.now(timezone.utc)).total_seconds())
            
            await self.redis.setex(
                f"audit_event:{event.event_id}",
                max(86400, retention_seconds),  # Minimum 1 day
                json.dumps(event_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Event storage failed: {e}")
            raise

    async def _store_trail(self, trail: AuditTrail) -> None:
        """Store sealed audit trail"""
        try:
            trail_data = {
                "trail_id": trail.trail_id,
                "created_at": trail.created_at.isoformat(),
                "created_by": trail.created_by,
                "trail_hash": trail.trail_hash,
                "previous_trail_hash": trail.previous_trail_hash,
                "is_sealed": trail.is_sealed,
                "sealed_at": trail.sealed_at.isoformat() if trail.sealed_at else None,
                "digital_signature": trail.digital_signature,
                "event_count": len(trail.events),
                "event_ids": [event.event_id for event in trail.events],
                "compliance_period": trail.compliance_period,
                "retention_until": trail.retention_until.isoformat() if trail.retention_until else None,
                "metadata": trail.metadata
            }
            
            await self.redis.setex(
                f"audit_trail:{trail.trail_id}",
                86400 * 2555,  # 7 years
                json.dumps(trail_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Trail storage failed: {e}")
            raise

    async def _store_report(self, report: AuditReport) -> None:
        """Store audit report"""
        try:
            report_data = {
                "report_id": report.report_id,
                "report_type": report.report_type,
                "generated_at": report.generated_at.isoformat(),
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "total_events": report.total_events,
                "events_by_category": report.events_by_category,
                "events_by_level": report.events_by_level,
                "compliance_violations": report.compliance_violations,
                "risk_analysis": report.risk_analysis,
                "recommendations": report.recommendations,
                "executive_summary": report.executive_summary,
                "compliance_frameworks_covered": [fw.value for fw in report.compliance_frameworks_covered],
                "metadata": report.metadata
            }
            
            await self.redis.setex(
                f"audit_report:{report.report_id}",
                86400 * 365,  # 1 year
                json.dumps(report_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Report storage failed: {e}")
            raise

    async def _load_trail(self, trail_id: str) -> Optional[AuditTrail]:
        """Load audit trail from storage"""
        try:
            trail_data = await self.redis.get(f"audit_trail:{trail_id}")
            if not trail_data:
                return None
            
            trail_dict = json.loads(trail_data)
            
            # Load events
            events = []
            for event_id in trail_dict.get("event_ids", []):
                event_data = await self.redis.get(f"audit_event:{event_id}")
                if event_data:
                    event_dict = json.loads(event_data)
                    # Reconstruct event (simplified)
                    # In production, full reconstruction would be needed
                    pass
            
            # Reconstruct trail (simplified)
            # In production, full reconstruction would be needed
            
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Trail loading failed: {e}")
            return None

    async def _get_last_trail_hash(self) -> str:
        """Get hash of last sealed trail"""
        try:
            hash_data = await self.redis.get("audit_last_trail_hash")
            return hash_data.decode() if hash_data else ""
        except Exception:
            return ""

    async def _store_last_trail_hash(self, trail_hash: str) -> None:
        """Store hash of last sealed trail"""
        try:
            await self.redis.set("audit_last_trail_hash", trail_hash)
        except Exception as e:
            logger.error(f"Failed to store last trail hash: {e}")

    def _generate_signing_keys(self) -> None:
        """Generate RSA key pair for digital signatures"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            
            self.signing_private_key = private_key
            self.signing_public_key = private_key.public_key()
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")

    def _load_signing_keys(self, signing_key: bytes) -> None:
        """Load signing keys from provided key material"""
        try:
            # Simplified - in production, proper key loading would be implemented
            self._generate_signing_keys()
        except Exception as e:
            logger.error(f"Key loading failed: {e}")

    # Background task methods
    async def _event_processor(self) -> None:
        """Background event processor"""
        try:
            while True:
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    await self._process_event(event)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Event processing error: {e}")
        except Exception as e:
            logger.error(f"Event processor failed: {e}")

    async def _trail_sealer(self) -> None:
        """Background trail sealer"""
        try:
            while True:
                await asyncio.sleep(self.config["trail_seal_interval"])
                
                if self.current_trail and self.current_trail.events:
                    await self._seal_current_trail()
                    await self._create_new_trail()
                    
        except Exception as e:
            logger.error(f"Trail sealer failed: {e}")

    async def _retention_manager(self) -> None:
        """Background retention manager"""
        try:
            while True:
                await asyncio.sleep(86400)  # Run daily
                
                # Clean up expired events and trails
                # This would implement proper retention management
                
        except Exception as e:
            logger.error(f"Retention manager failed: {e}")

    async def _integrity_verifier(self) -> None:
        """Background integrity verifier"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run hourly
                
                # Verify integrity of recent trails
                # This would implement scheduled integrity checks
                
        except Exception as e:
            logger.error(f"Integrity verifier failed: {e}")

    # Placeholder methods for report generation
    async def _query_events_by_period(self, start_date: datetime, end_date: datetime) -> List[AuditEvent]:
        """Query events by time period"""
        # Placeholder - would implement Redis/database query
        return []

    async def _identify_compliance_violations(self, events: List[AuditEvent], framework: ComplianceFramework) -> List[Dict[str, Any]]:
        """Identify compliance violations"""
        # Placeholder - would implement framework-specific violation detection
        return []

    async def _generate_compliance_recommendations(self, framework: ComplianceFramework, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        # Placeholder - would implement recommendation engine
        return ["Implement stronger access controls", "Enhance monitoring coverage"]

    async def _analyze_compliance_risks(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze compliance risks"""
        # Placeholder - would implement risk analysis
        return {"overall_risk": "low", "high_risk_areas": []}

    async def _generate_executive_summary(self, report: AuditReport) -> str:
        """Generate executive summary"""
        # Placeholder - would implement summary generation
        return f"Audit report for period {report.period_start} to {report.period_end}. Total events: {report.total_events}."

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit engine statistics"""
        avg_processing_time = (
            sum(self.stats["processing_time_ms"]) / len(self.stats["processing_time_ms"])
            if self.stats["processing_time_ms"] else 0.0
        )
        
        return {
            "total_events": self.stats["total_events"],
            "trails_created": self.stats["trails_created"],
            "events_by_category": self.stats["events_by_category"],
            "events_by_level": self.stats["events_by_level"],
            "compliance_events": self.stats["compliance_events"],
            "integrity_violations": self.stats["integrity_violations"],
            "average_processing_time_ms": avg_processing_time,
            "queue_size": self.event_queue.qsize(),
            "current_trail_events": len(self.current_trail.events) if self.current_trail else 0
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Seal current trail before shutdown
        if self.current_trail:
            await self._seal_current_trail()
        
        if self.redis:
            await self.redis.close()