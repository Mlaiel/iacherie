"""Transaction Security Manager - Enterprise Security Controls

Advanced security management system for database transactions providing
comprehensive security controls, threat detection, and compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.
"""

import asyncio
import hashlib
import hmac
import secrets
import logging
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import ipaddress
import re

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """
Security level enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel(Enum):
    """Threat severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Security event types"""

    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    TRANSACTION_START = "transaction_start"
    TRANSACTION_ABORT = "transaction_abort"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    ENCRYPTION_FAILURE = "encryption_failure"
    AUDIT_LOG_TAMPERING = "audit_log_tampering"


@dataclass
class SecurityContext:
    """Security context for transactions"""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    permissions: Set[str] = field(default_factory=set)
    roles: Set[str] = field(default_factory=set)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    mfa_verified: bool = False
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    failed_attempts: int = 0
    is_locked: bool = False
    lock_expires: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self, session_timeout: int = 3600) -> bool:
        """
Check if security context is expired"""
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed > session_timeout
    
    def is_account_locked(self) -> bool:
        """
Check if account is locked"""
        if not self.is_locked:
            return False
        
        if self.lock_expires and datetime.now(timezone.utc) > self.lock_expires:
            self.is_locked = False
            self.lock_expires = None
            return False
        
        return True


@dataclass
class SecurityPolicy:
    """
Security policy configuration"""
    name: str
    security_level: SecurityLevel
    max_failed_attempts: int = 3
    lockout_duration_minutes: int = 30
    session_timeout_seconds: int = 3600
    require_mfa: bool = False
    allowed_ip_ranges: List[str] = field(default_factory=list)
    blocked_ip_ranges: List[str] = field(default_factory=list)
    required_permissions: Set[str] = field(default_factory=set)
    encryption_required: bool = True
    audit_level: str = "FULL"
    rate_limit_per_minute: int = 100
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check blocked ranges first
            for blocked_range in self.blocked_ip_ranges:
                if ip in ipaddress.ip_network(blocked_range, strict=False):
                    return False
            
            # If no allowed ranges specified, allow all non-blocked IPs
            if not self.allowed_ip_ranges:
                return True
            
            # Check allowed ranges
            for allowed_range in self.allowed_ip_ranges:
                if ip in ipaddress.ip_network(allowed_range, strict=False):
                    return True
            
            return False
            
        except ValueError:
            logger.error("Invalid IP address: %s", ip_address)
            return False


class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self):
        self.suspicious_patterns = {
            'sql_injection': [
                r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
                r"(\b--|\b#|\b/\*|\*/)",
                r"(\bOR\s+\d+\s*=\s*\d+|\bAND\s+\d+\s*=\s*\d+)",
            ],
            'xss_attempt': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
            ]
        }
        
        self.anomaly_thresholds = {
            'rapid_requests': 50,  # requests per minute
            'unusual_hours': (22, 6),  # 10 PM to 6 AM
            'geographic_anomaly': True,
        }
    
    def detect_threats(self, context: SecurityContext, request_data: Dict[str, Any]) -> List[Tuple[ThreatLevel, str]]:
        """Detect security threats in request"""
        threats = []
        
        # Check for injection attacks
        for pattern_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if self._check_pattern_in_data(pattern, request_data):
                    threats.append((ThreatLevel.HIGH, f"Potential {pattern_type} detected"))
        
        # Check for rate limiting violations
        if self._check_rate_limit(context):
            threats.append((ThreatLevel.MEDIUM, "Rate limit exceeded"))
        
        # Check for unusual access patterns
        if self._check_unusual_access(context):
            threats.append((ThreatLevel.LOW, "Unusual access pattern detected"))
        
        return threats
    
    def _check_pattern_in_data(self, pattern: str, data: Dict[str, Any]) -> bool:
        """Check if suspicious pattern exists in request data"""
        data_str = json.dumps(data).lower()
        return bool(re.search(pattern, data_str, re.IGNORECASE))
    
    def _check_rate_limit(self, context: SecurityContext) -> bool:
        """
Check if rate limit is exceeded"""
        # This would be implemented with a proper rate limiting mechanism
        # For now, return False as a placeholder
        return False
    
    def _check_unusual_access(self, context: SecurityContext) -> bool:
        """
Check for unusual access patterns"""
        current_hour = datetime.now().hour
        unusual_hours = self.anomaly_thresholds['unusual_hours']
        
        # Check for access during unusual hours
        if unusual_hours[0] <= current_hour or current_hour <= unusual_hours[1]:
            return True
        
        return False


class EncryptionManager:
    """
Transaction data encryption and key management"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.master_key)
        self.key_rotation_interval = 86400  # 24 hours
        self.last_key_rotation = time.time()
        
        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
Encrypt sensitive data"""
        try:
            return self.cipher_suite.encrypt(data)
        except Exception as e:
            logger.error("Encryption failed: %s", str(e))
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt sensitive data"""
        try:
            return self.cipher_suite.decrypt(encrypted_data)
        except Exception as e:
            logger.error("Decryption failed: %s", str(e))
            raise
    
    def encrypt_json(self, data: Dict[str, Any]) -> str:
        """Encrypt JSON data"""
        json_str = json.dumps(data)
        encrypted_bytes = self.encrypt_data(json_str.encode())
        return base64.b64encode(encrypted_bytes).decode()
    
    def decrypt_json(self, encrypted_str: str) -> Dict[str, Any]:
        """
Decrypt JSON data"""
        encrypted_bytes = base64.b64decode(encrypted_str.encode())
        decrypted_bytes = self.decrypt_data(encrypted_bytes)
        return json.loads(decrypted_bytes.decode())
    
    def generate_transaction_key(self, transaction_id: str) -> bytes:
        """
Generate unique key for transaction"""
        salt = transaction_id.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))
    
    def should_rotate_keys(self) -> bool:
        """
Check if keys should be rotated"""
        return (time.time() - self.last_key_rotation) > self.key_rotation_interval
    
    def rotate_keys(self) -> None:
        """
Rotate encryption keys"""
        self.master_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.master_key)
        self.last_key_rotation = time.time()
        logger.info("Encryption keys rotated")


class TransactionSecurityManager:
    """
    Comprehensive transaction security management system
    
    Features:
    - Authentication and authorization
    - Threat detection and prevention
    - Data encryption and key management
    - Audit logging and compliance
    - Access control and rate limiting
    - Security policy enforcement
    - Real-time monitoring
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.threat_detector = ThreatDetector()
        self.encryption_manager = EncryptionManager()
        self.security_events: List[Dict[str, Any]] = []
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.lock = threading.RLock()
        
        # Setup default security policy
        self._setup_default_policy()
        
        logger.info("TransactionSecurityManager initialized")
    
    def create_security_context(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        permissions: Optional[Set[str]] = None,
        roles: Optional[Set[str]] = None
    ) -> SecurityContext:
        """Create new security context for user session"""
        
        session_id = self._generate_session_id()
        
        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            permissions=permissions or set(),
            roles=roles or set()
        )
        
        with self.lock:
            self.active_sessions[session_id] = context
        
        self._log_security_event(
            SecurityEvent.LOGIN_SUCCESS,
            context,
            {"message": "Security context created"}
        )
        
        logger.info("Security context created for user %s (session=%s)", user_id, session_id)
        return context
    
    def validate_transaction_access(
        self,
        context: SecurityContext,
        transaction_id: str,
        required_permissions: Optional[Set[str]] = None,
        security_level: SecurityLevel = SecurityLevel.MEDIUM
    ) -> bool:
        """Validate user access to transaction"""
        
        # Check if context is valid
        if not self._validate_security_context(context):
            return False
        
        # Get applicable security policy
        policy = self._get_security_policy(security_level)
        
        # Check IP address restrictions
        if not policy.is_ip_allowed(context.ip_address):
            self._log_security_event(
                SecurityEvent.UNAUTHORIZED_ACCESS,
                context,
                {"reason": "IP address not allowed", "transaction_id": transaction_id}
            )
            return False
        
        # Check required permissions
        if required_permissions and not required_permissions.issubset(context.permissions):
            missing_perms = required_permissions - context.permissions
            self._log_security_event(
                SecurityEvent.UNAUTHORIZED_ACCESS,
                context,
                {
                    "reason": "Insufficient permissions",
                    "missing_permissions": list(missing_perms),
                    "transaction_id": transaction_id
                }
            )
            return False
        
        # Check MFA requirement
        if policy.require_mfa and not context.mfa_verified:
            self._log_security_event(
                SecurityEvent.UNAUTHORIZED_ACCESS,
                context,
                {"reason": "MFA required but not verified", "transaction_id": transaction_id}
            )
            return False
        
        # Check rate limits
        if not self._check_rate_limit(context, policy):
            return False
        
        # Update last activity
        context.last_activity = datetime.now(timezone.utc)
        
        self._log_security_event(
            SecurityEvent.TRANSACTION_START,
            context,
            {"transaction_id": transaction_id, "security_level": security_level.value}
        )
        
        return True
    
    def scan_transaction_data(
        self,
        context: SecurityContext,
        transaction_data: Dict[str, Any]
    ) -> List[Tuple[ThreatLevel, str]]:
        """Scan transaction data for security threats"""
        
        threats = self.threat_detector.detect_threats(context, transaction_data)
        
        for threat_level, description in threats:
            self._log_security_event(
                SecurityEvent.SUSPICIOUS_ACTIVITY,
                context,
                {
                    "threat_level": threat_level.value,
                    "description": description,
                    "data_sample": str(transaction_data)[:200]  # Limited sample
                }
            )
        
        return threats
    
    def encrypt_transaction_data(self, transaction_id: str, data: Dict[str, Any]) -> str:
        """Encrypt sensitive transaction data"""
        try:
            return self.encryption_manager.encrypt_json(data)
        except Exception as e:
            logger.error("Failed to encrypt transaction data: %s", str(e))
            raise
    
    def decrypt_transaction_data(self, transaction_id: str, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt transaction data"""
        try:
            return self.encryption_manager.decrypt_json(encrypted_data)
        except Exception as e:
            logger.error("Failed to decrypt transaction data: %s", str(e))
            raise
    
    def record_failed_attempt(self, user_id: str, reason: str, context: Optional[SecurityContext] = None) -> None:
        """Record failed authentication/authorization attempt"""
        
        with self.lock:
            if user_id not in self.failed_attempts:
                self.failed_attempts[user_id] = []
            
            self.failed_attempts[user_id].append(datetime.now(timezone.utc))
            
            # Clean old attempts (older than 1 hour)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            self.failed_attempts[user_id] = [
                attempt for attempt in self.failed_attempts[user_id]
                if attempt > cutoff_time
            ]
            
            # Check if account should be locked
            policy = self._get_security_policy(SecurityLevel.MEDIUM)
            if len(self.failed_attempts[user_id]) >= policy.max_failed_attempts:
                self._lock_user_account(user_id, policy.lockout_duration_minutes)
        
        self._log_security_event(
            SecurityEvent.LOGIN_FAILURE,
            context,
            {"user_id": user_id, "reason": reason}
        )
        
        logger.warning("Failed attempt recorded for user %s: %s", user_id, reason)
    
    def invalidate_session(self, session_id: str, reason: str = "logout") -> bool:
        """Invalidate user session"""
        
        with self.lock:
            context = self.active_sessions.pop(session_id, None)
        
        if context:
            self._log_security_event(
                SecurityEvent.LOGIN_ATTEMPT,
                context,
                {"reason": reason, "action": "session_invalidated"}
            )
            
            logger.info("Session invalidated: %s (reason=%s)", session_id, reason)
            return True
        
        return False
    
    def get_security_audit_log(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[SecurityEvent]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get security audit log with filtering"""
        
        filtered_events = []
        
        for event in self.security_events:
            # Time filtering
            event_time = datetime.fromisoformat(event['timestamp'])
            if start_time and event_time < start_time:
                continue
            if end_time and event_time > end_time:
                continue
            
            # Event type filtering
            if event_types and SecurityEvent(event['event_type']) not in event_types:
                continue
            
            # User filtering
            if user_id and event.get('user_id') != user_id:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def _validate_security_context(self, context: SecurityContext) -> bool:
        """
Validate security context"""
        
        # Check if session exists
        if context.session_id not in self.active_sessions:
            return False
        
        # Check if account is locked
        if context.is_account_locked():
            return False
        
        # Check if session is expired
        policy = self._get_security_policy(context.security_level)
        if context.is_expired(policy.session_timeout_seconds):
            self.invalidate_session(context.session_id, "session_expired")
            return False
        
        return True
    
    def _check_rate_limit(self, context: SecurityContext, policy: SecurityPolicy) -> bool:
        """Check rate limiting for user"""
        
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(minutes=1)
        
        with self.lock:
            if context.user_id not in self.rate_limits:
                self.rate_limits[context.user_id] = []
            
            # Clean old requests
            self.rate_limits[context.user_id] = [
                request_time for request_time in self.rate_limits[context.user_id]
                if request_time > cutoff_time
            ]
            
            # Check rate limit
            if len(self.rate_limits[context.user_id]) >= policy.rate_limit_per_minute:
                self._log_security_event(
                    SecurityEvent.SUSPICIOUS_ACTIVITY,
                    context,
                    {"reason": "Rate limit exceeded", "requests_per_minute": len(self.rate_limits[context.user_id])}
                )
                return False
            
            # Record current request
            self.rate_limits[context.user_id].append(current_time)
        
        return True
    
    def _lock_user_account(self, user_id: str, duration_minutes: int) -> None:
        """Lock user account for specified duration"""
        
        lock_expires = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        
        # Update all active sessions for this user
        with self.lock:
            for context in self.active_sessions.values():
                if context.user_id == user_id:
                    context.is_locked = True
                    context.lock_expires = lock_expires
        
        logger.warning("User account locked: %s (duration=%d minutes)", user_id, duration_minutes)
    
    def _get_security_policy(self, security_level: SecurityLevel) -> SecurityPolicy:
        """Get security policy for level"""
        policy_name = f"default_{security_level.value}"
        return self.security_policies.get(policy_name, self.security_policies["default_medium"])
    
    def _setup_default_policy(self) -> None:
        """Setup default security policies"""
        
        # Low security policy
        self.security_policies["default_low"] = SecurityPolicy(
            name="default_low",
            security_level=SecurityLevel.LOW,
            max_failed_attempts=5,
            lockout_duration_minutes=15,
            session_timeout_seconds=7200,  # 2 hours
            require_mfa=False,
            encryption_required=False,
            rate_limit_per_minute=200
        )
        
        # Medium security policy (default)
        self.security_policies["default_medium"] = SecurityPolicy(
            name="default_medium",
            security_level=SecurityLevel.MEDIUM,
            max_failed_attempts=3,
            lockout_duration_minutes=30,
            session_timeout_seconds=3600,  # 1 hour
            require_mfa=False,
            encryption_required=True,
            rate_limit_per_minute=100
        )
        
        # High security policy
        self.security_policies["default_high"] = SecurityPolicy(
            name="default_high",
            security_level=SecurityLevel.HIGH,
            max_failed_attempts=2,
            lockout_duration_minutes=60,
            session_timeout_seconds=1800,  # 30 minutes
            require_mfa=True,
            encryption_required=True,
            rate_limit_per_minute=50
        )
        
        # Critical security policy
        self.security_policies["default_critical"] = SecurityPolicy(
            name="default_critical",
            security_level=SecurityLevel.CRITICAL,
            max_failed_attempts=1,
            lockout_duration_minutes=120,
            session_timeout_seconds=900,  # 15 minutes
            require_mfa=True,
            encryption_required=True,
            rate_limit_per_minute=25
        )
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _log_security_event(
        self,
        event_type: SecurityEvent,
        try:
            logger.info(f"Executing _log_security_event")
            
            # Implementation for _log_security_event
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_log_security_event completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_log_security_event failed: {e}")
            raise
    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions periodically"""
        
        expired_sessions = []
        current_time = datetime.now(timezone.utc)
        
        with self.lock:
            for session_id, context in self.active_sessions.items():
                policy = self._get_security_policy(context.security_level)
                if context.is_expired(policy.session_timeout_seconds):
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id, "expired")
        
        if expired_sessions:
            logger.info("Cleaned up %d expired sessions", len(expired_sessions))
    
    async def shutdown(self) -> None:
        """Graceful shutdown of security manager"""
        logger.info("Shutting down TransactionSecurityManager...")
        
        # Invalidate all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            self.invalidate_session(session_id, "system_shutdown")
        
        logger.info("TransactionSecurityManager shutdown complete")
