"""
Queue Security Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_security_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Security & Protection System - Enterprise-Grade
Responsibility: Comprehensive security management for crawler queue operations
Technologies: Security Analytics, Threat Detection, Access Control, Encryption
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Security assessment → Threat detection → Access validation → Encryption management →
Audit logging → Compliance monitoring → Incident response → Security optimization
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import hashlib
import hmac
import secrets
from collections import defaultdict, deque
import time
import ipaddress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import jwt

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level classifications"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    ENTERPRISE = "enterprise"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SecurityEventType(Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALICIOUS_PAYLOAD = "malicious_payload"
    SYSTEM_INTRUSION = "system_intrusion"
    COMPLIANCE_VIOLATION = "compliance_violation"


class AccessPermission(Enum):
    """Access permission levels"""
    READ_ONLY = "read_only"
    WRITE_LIMITED = "write_limited"
    WRITE_FULL = "write_full"
    ADMIN_LIMITED = "admin_limited"
    ADMIN_FULL = "admin_full"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class SecurityConfiguration:
    """Security configuration parameters"""
    security_level: SecurityLevel = SecurityLevel.ENHANCED
    encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    threat_detection_enabled: bool = True
    rate_limiting_enabled: bool = True
    access_control_enabled: bool = True
    compliance_monitoring_enabled: bool = True
    
    # Authentication settings
    jwt_expiration_minutes: int = 60
    refresh_token_expiration_hours: int = 24
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # Rate limiting settings
    default_rate_limit_per_minute: int = 100
    burst_rate_limit: int = 200
    rate_limit_window_minutes: int = 1
    
    # Encryption settings
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval_hours: int = 24
    backup_key_count: int = 3
    
    # Monitoring settings
    security_log_retention_days: int = 90
    threat_detection_sensitivity: float = 0.8
    anomaly_detection_threshold: float = 0.9


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    severity: ThreatSeverity
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    queue_id: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_actions: List[str] = field(default_factory=list)


@dataclass
class SecurityToken:
    """Security token information"""
    token_id: str
    user_id: str
    permissions: List[AccessPermission]
    issued_at: datetime
    expires_at: datetime
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityAudit:
    """Security audit result"""
    audit_id: str
    audit_type: str
    security_score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_status: Dict[str, bool]
    audit_timestamp: datetime = field(default_factory=datetime.now)


class ThreatDetectionEngine:
    """Advanced threat detection engine"""
    
    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity
        self.threat_patterns = self._initialize_threat_patterns()
        self.anomaly_baselines = {}
        self.detection_rules = []
        self.threat_intelligence = {}
        
    async def detect_threats(
        self,
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]] = None
    ) -> List[SecurityEvent]:
        """Detect security threats in event data"""
        
        threats = []
        
        # Pattern-based detection
        pattern_threats = await self._detect_pattern_threats(event_data)
        threats.extend(pattern_threats)
        
        # Anomaly-based detection
        if historical_data:
            anomaly_threats = await self._detect_anomaly_threats(event_data, historical_data)
            threats.extend(anomaly_threats)
        
        # Behavioral analysis
        behavioral_threats = await self._detect_behavioral_threats(event_data)
        threats.extend(behavioral_threats)
        
        # Rule-based detection
        rule_threats = await self._detect_rule_based_threats(event_data)
        threats.extend(rule_threats)
        
        return threats
    
    async def _detect_pattern_threats(self, event_data: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect threats using pattern matching"""
        
        threats = []
        
        for pattern_name, pattern_config in self.threat_patterns.items():
            if await self._matches_threat_pattern(event_data, pattern_config):
                threat = SecurityEvent(
                    event_id=f"threat_{uuid.uuid4().hex[:8]}",
                    event_type=pattern_config['event_type'],
                    severity=pattern_config['severity'],
                    source_ip=event_data.get('source_ip'),
                    user_id=event_data.get('user_id'),
                    description=f"Threat pattern detected: {pattern_name}",
                    metadata={'pattern': pattern_name, 'confidence': pattern_config['confidence']}
                )
                threats.append(threat)
        
        return threats
    
    async def _detect_anomaly_threats(
        self,
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> List[SecurityEvent]:
        """Detect threats using anomaly detection"""
        
        threats = []
        
        # Calculate anomaly score
        anomaly_score = await self._calculate_anomaly_score(event_data, historical_data)
        
        if anomaly_score > self.sensitivity:
            threat = SecurityEvent(
                event_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                severity=self._calculate_severity_from_score(anomaly_score),
                source_ip=event_data.get('source_ip'),
                user_id=event_data.get('user_id'),
                description=f"Anomalous behavior detected (score: {anomaly_score:.2f})",
                metadata={'anomaly_score': anomaly_score, 'baseline_deviation': anomaly_score}
            )
            threats.append(threat)
        
        return threats
    
    async def _detect_behavioral_threats(self, event_data: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect threats using behavioral analysis"""
        
        threats = []
        
        # Check for suspicious IP patterns
        source_ip = event_data.get('source_ip')
        if source_ip:
            if await self._is_suspicious_ip(source_ip):
                threat = SecurityEvent(
                    event_id=f"behavioral_{uuid.uuid4().hex[:8]}",
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    severity=ThreatSeverity.MEDIUM,
                    source_ip=source_ip,
                    description=f"Suspicious IP activity: {source_ip}",
                    metadata={'check_type': 'ip_reputation'}
                )
                threats.append(threat)
        
        # Check for unusual request patterns
        if await self._is_unusual_request_pattern(event_data):
            threat = SecurityEvent(
                event_id=f"pattern_{uuid.uuid4().hex[:8]}",
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                severity=ThreatSeverity.MEDIUM,
                source_ip=event_data.get('source_ip'),
                user_id=event_data.get('user_id'),
                description="Unusual request pattern detected",
                metadata={'check_type': 'request_pattern'}
            )
            threats.append(threat)
        
        return threats
    
    async def _detect_rule_based_threats(self, event_data: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect threats using custom rules"""
        
        threats = []
        
        for rule in self.detection_rules:
            if await self._evaluate_detection_rule(event_data, rule):
                threat = SecurityEvent(
                    event_id=f"rule_{uuid.uuid4().hex[:8]}",
                    event_type=rule['event_type'],
                    severity=rule['severity'],
                    source_ip=event_data.get('source_ip'),
                    user_id=event_data.get('user_id'),
                    description=f"Security rule triggered: {rule['name']}",
                    metadata={'rule_id': rule['id'], 'rule_name': rule['name']}
                )
                threats.append(threat)
        
        return threats
    
    def _initialize_threat_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threat detection patterns"""
        
        return {
            'sql_injection': {
                'event_type': SecurityEventType.MALICIOUS_PAYLOAD,
                'severity': ThreatSeverity.HIGH,
                'patterns': ['union select', 'drop table', 'exec(', '--', ';--'],
                'confidence': 0.9
            },
            'xss_attack': {
                'event_type': SecurityEventType.MALICIOUS_PAYLOAD,
                'severity': ThreatSeverity.HIGH,
                'patterns': ['<script>', 'javascript:', 'onerror=', 'onload='],
                'confidence': 0.85
            },
            'brute_force': {
                'event_type': SecurityEventType.AUTHENTICATION_FAILURE,
                'severity': ThreatSeverity.MEDIUM,
                'patterns': ['multiple_failures', 'rapid_attempts'],
                'confidence': 0.8
            },
            'rate_abuse': {
                'event_type': SecurityEventType.RATE_LIMIT_EXCEEDED,
                'severity': ThreatSeverity.MEDIUM,
                'patterns': ['excessive_requests', 'burst_activity'],
                'confidence': 0.75
            }
        }
    
    async def _matches_threat_pattern(
        self,
        event_data: Dict[str, Any],
        pattern_config: Dict[str, Any]
    ) -> bool:
        """Check if event matches threat pattern"""
        
        # Check payload for malicious patterns
        payload = str(event_data.get('payload', ''))
        for pattern in pattern_config.get('patterns', []):
            if pattern.lower() in payload.lower():
                return True
        
        # Check request frequency for rate abuse
        if 'rapid_attempts' in pattern_config.get('patterns', []):
            return await self._check_rapid_attempts(event_data)
        
        return False
    
    async def _calculate_anomaly_score(
        self,
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate anomaly score for event"""
        
        # Simple anomaly detection based on frequency and patterns
        score = 0.0
        
        # Check request frequency anomaly
        current_rate = event_data.get('request_rate', 0)
        historical_rates = [d.get('request_rate', 0) for d in historical_data[-100:]]
        
        if historical_rates:
            avg_rate = sum(historical_rates) / len(historical_rates)
            if avg_rate > 0:
                rate_deviation = abs(current_rate - avg_rate) / avg_rate
                score += min(rate_deviation, 1.0) * 0.4
        
        # Check timing anomaly
        time_anomaly = await self._check_timing_anomaly(event_data, historical_data)
        score += time_anomaly * 0.3
        
        # Check payload anomaly
        payload_anomaly = await self._check_payload_anomaly(event_data, historical_data)
        score += payload_anomaly * 0.3
        
        return min(score, 1.0)
    
    def _calculate_severity_from_score(self, score: float) -> ThreatSeverity:
        """Calculate threat severity from anomaly score"""
        
        if score >= 0.9:
            return ThreatSeverity.CRITICAL
        elif score >= 0.7:
            return ThreatSeverity.HIGH
        elif score >= 0.5:
            return ThreatSeverity.MEDIUM
        else:
            return ThreatSeverity.LOW
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check if private IP (less suspicious)
            if ip.is_private:
                return False
            
            # Check against threat intelligence (placeholder)
            # In production, this would check against threat feeds
            return False
            
        except ValueError:
            return True  # Invalid IP format is suspicious
    
    async def _is_unusual_request_pattern(self, event_data: Dict[str, Any]) -> bool:
        """Check for unusual request patterns"""
        
        # Check request timing
        timestamp = event_data.get('timestamp', datetime.now())
        hour = timestamp.hour
        
        # Unusual hours (late night/early morning)
        if hour < 6 or hour > 22:
            return True
        
        # Check request payload size
        payload_size = len(str(event_data.get('payload', '')))
        if payload_size > 10000:  # Very large payload
            return True
        
        return False
    
    async def _evaluate_detection_rule(
        self,
        event_data: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> bool:
        """Evaluate custom detection rule"""
        
        # Placeholder for rule evaluation engine
        # In production, this would implement a rule engine
        return False
    
    async def _check_rapid_attempts(self, event_data: Dict[str, Any]) -> bool:
        """Check for rapid successive attempts"""
        
        # Placeholder for rapid attempt detection
        return event_data.get('request_rate', 0) > 100
    
    async def _check_timing_anomaly(
        self,
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> float:
        """Check for timing anomalies"""
        
        # Simple timing anomaly detection
        current_hour = event_data.get('timestamp', datetime.now()).hour
        historical_hours = [
            d.get('timestamp', datetime.now()).hour
            for d in historical_data[-100:]
        ]
        
        if not historical_hours:
            return 0.0
        
        # Calculate hour frequency
        hour_counts = defaultdict(int)
        for h in historical_hours:
            hour_counts[h] += 1
        
        expected_frequency = hour_counts.get(current_hour, 0) / len(historical_hours)
        
        # Return anomaly score (low frequency = higher anomaly)
        return max(0.0, 1.0 - expected_frequency * 10)
    
    async def _check_payload_anomaly(
        self,
        event_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> float:
        """Check for payload anomalies"""
        
        current_payload = str(event_data.get('payload', ''))
        current_size = len(current_payload)
        
        historical_sizes = [
            len(str(d.get('payload', '')))
            for d in historical_data[-100:]
        ]
        
        if not historical_sizes:
            return 0.0
        
        avg_size = sum(historical_sizes) / len(historical_sizes)
        
        if avg_size > 0:
            size_deviation = abs(current_size - avg_size) / avg_size
            return min(size_deviation, 1.0)
        
        return 0.0


class EncryptionManager:
    """Advanced encryption management system"""
    
    def __init__(self, config: SecurityConfiguration):
        self.config = config
        self.active_key = None
        self.backup_keys = []
        self.key_rotation_schedule = None
        
    async def initialize(self):
        """Initialize encryption manager"""
        
        if self.config.encryption_enabled:
            await self._generate_initial_keys()
            await self._schedule_key_rotation()
        
        logger.info("EncryptionManager initialized")
    
    async def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt sensitive data"""
        
        if not self.config.encryption_enabled:
            return data if isinstance(data, str) else data.decode()
        
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.active_key.encrypt(data)
        return base64.b64encode(encrypted).decode()
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt encrypted data"""
        
        if not self.config.encryption_enabled:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.active_key.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            # Try backup keys
            for backup_key in self.backup_keys:
                try:
                    decrypted = backup_key.decrypt(encrypted_bytes)
                    return decrypted.decode()
                except:
                    continue
            
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    async def rotate_keys(self):
        """Rotate encryption keys"""
        
        logger.info("Rotating encryption keys")
        
        # Move current key to backup
        if self.active_key:
            self.backup_keys.append(self.active_key)
        
        # Keep only configured number of backup keys
        if len(self.backup_keys) > self.config.backup_key_count:
            self.backup_keys = self.backup_keys[-self.config.backup_key_count:]
        
        # Generate new active key
        self.active_key = self._generate_key()
        
        logger.info("Key rotation completed")
    
    async def _generate_initial_keys(self):
        """Generate initial encryption keys"""
        
        self.active_key = self._generate_key()
        
        # Generate backup keys
        for _ in range(self.config.backup_key_count):
            self.backup_keys.append(self._generate_key())
    
    def _generate_key(self) -> Fernet:
        """Generate encryption key"""
        
        # Use PBKDF2 for key derivation
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    async def _schedule_key_rotation(self):
        """Schedule automatic key rotation"""
        
        async def rotation_loop():
            while True:
                await asyncio.sleep(self.config.key_rotation_interval_hours * 3600)
                await self.rotate_keys()
        
        self.key_rotation_schedule = asyncio.create_task(rotation_loop())


class QueueSecurityManager:
    """Enterprise-grade queue security management system"""
    
    def __init__(self, config: SecurityConfiguration = None):
        self.config = config or SecurityConfiguration()
        self.threat_detector = ThreatDetectionEngine(self.config.threat_detection_sensitivity)
        self.encryption_manager = EncryptionManager(self.config)
        
        # Security state
        self.security_events = deque(maxlen=10000)
        self.active_tokens = {}
        self.blocked_ips = set()
        self.rate_limits = defaultdict(deque)
        self.audit_logs = deque(maxlen=50000)
        
        # Access control
        self.user_permissions = {}
        self.role_permissions = {}
        self.session_tokens = {}
        
        logger.info(f"QueueSecurityManager initialized with security level: {self.config.security_level.value}")
    
    async def initialize(self):
        """Initialize security manager"""
        
        await self.encryption_manager.initialize()
        
        # Initialize security rules and patterns
        await self._initialize_security_rules()
        
        # Start security monitoring
        await self._start_security_monitoring()
        
        logger.info("QueueSecurityManager initialization completed")
        return True
    
    async def authenticate_request(
        self,
        token: str,
        required_permissions: List[AccessPermission] = None
    ) -> Optional[SecurityToken]:
        """Authenticate and authorize request"""
        
        try:
            # Validate token format
            if not token or not isinstance(token, str):
                await self._log_security_event(
                    SecurityEventType.AUTHENTICATION_FAILURE,
                    ThreatSeverity.LOW,
                    description="Invalid token format"
                )
                return None
            
            # Decode and validate JWT token
            token_data = await self._validate_jwt_token(token)
            if not token_data:
                await self._log_security_event(
                    SecurityEventType.AUTHENTICATION_FAILURE,
                    ThreatSeverity.MEDIUM,
                    description="Invalid or expired token"
                )
                return None
            
            # Create security token
            security_token = SecurityToken(
                token_id=token_data['jti'],
                user_id=token_data['sub'],
                permissions=[AccessPermission(p) for p in token_data.get('permissions', [])],
                issued_at=datetime.fromtimestamp(token_data['iat']),
                expires_at=datetime.fromtimestamp(token_data['exp']),
                scopes=token_data.get('scopes', [])
            )
            
            # Check permissions if required
            if required_permissions:
                if not await self._check_permissions(security_token, required_permissions):
                    await self._log_security_event(
                        SecurityEventType.AUTHORIZATION_VIOLATION,
                        ThreatSeverity.MEDIUM,
                        user_id=security_token.user_id,
                        description=f"Insufficient permissions: {required_permissions}"
                    )
                    return None
            
            # Update active tokens
            self.active_tokens[security_token.token_id] = security_token
            
            return security_token
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self._log_security_event(
                SecurityEventType.AUTHENTICATION_FAILURE,
                ThreatSeverity.HIGH,
                description=f"Authentication exception: {str(e)}"
            )
            return None
    
    async def validate_queue_access(
        self,
        security_token: SecurityToken,
        queue_id: str,
        operation: str
    ) -> bool:
        """Validate access to specific queue"""
        
        # Check if user has general queue access
        required_permission = self._get_required_permission(operation)
        if required_permission not in security_token.permissions:
            await self._log_security_event(
                SecurityEventType.AUTHORIZATION_VIOLATION,
                ThreatSeverity.MEDIUM,
                user_id=security_token.user_id,
                queue_id=queue_id,
                description=f"Missing permission for operation: {operation}"
            )
            return False
        
        # Check queue-specific permissions
        if not await self._check_queue_specific_access(security_token, queue_id, operation):
            await self._log_security_event(
                SecurityEventType.AUTHORIZATION_VIOLATION,
                ThreatSeverity.MEDIUM,
                user_id=security_token.user_id,
                queue_id=queue_id,
                description=f"Access denied to queue {queue_id} for operation: {operation}"
            )
            return False
        
        return True
    
    async def check_rate_limit(
        self,
        identifier: str,
        request_type: str = "default"
    ) -> bool:
        """Check if request is within rate limits"""
        
        if not self.config.rate_limiting_enabled:
            return True
        
        now = datetime.now()
        rate_key = f"{identifier}:{request_type}"
        
        # Clean old entries
        self.rate_limits[rate_key] = deque([
            timestamp for timestamp in self.rate_limits[rate_key]
            if now - timestamp < timedelta(minutes=self.config.rate_limit_window_minutes)
        ])
        
        # Check current rate
        current_count = len(self.rate_limits[rate_key])
        limit = self.config.default_rate_limit_per_minute
        
        if current_count >= limit:
            await self._log_security_event(
                SecurityEventType.RATE_LIMIT_EXCEEDED,
                ThreatSeverity.MEDIUM,
                description=f"Rate limit exceeded for {identifier}: {current_count}/{limit}"
            )
            return False
        
        # Add current request
        self.rate_limits[rate_key].append(now)
        return True
    
    async def analyze_security_threats(
        self,
        event_data: Dict[str, Any]
    ) -> List[SecurityEvent]:
        """Analyze incoming data for security threats"""
        
        if not self.config.threat_detection_enabled:
            return []
        
        # Collect historical data for context
        historical_data = list(self.audit_logs)[-1000:]  # Last 1000 events
        
        # Detect threats
        threats = await self.threat_detector.detect_threats(event_data, historical_data)
        
        # Process and store threats
        for threat in threats:
            self.security_events.append(threat)
            
            # Auto-response for critical threats
            if threat.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EMERGENCY]:
                await self._handle_critical_threat(threat)
        
        return threats
    
    async def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in data"""
        
        if not self.config.encryption_enabled:
            return data
        
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'private_key']
        encrypted_data = data.copy()
        
        for field, value in data.items():
            if any(sensitive_term in field.lower() for sensitive_term in sensitive_fields):
                if isinstance(value, (str, bytes)):
                    encrypted_data[field] = await self.encryption_manager.encrypt_data(value)
        
        return encrypted_data
    
    async def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in data"""
        
        if not self.config.encryption_enabled:
            return data
        
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'private_key']
        decrypted_data = data.copy()
        
        for field, value in data.items():
            if any(sensitive_term in field.lower() for sensitive_term in sensitive_fields):
                if isinstance(value, str):
                    try:
                        decrypted_data[field] = await self.encryption_manager.decrypt_data(value)
                    except:
                        # Keep original if decryption fails
                        pass
        
        return decrypted_data
    
    async def perform_security_audit(self, audit_scope: str = "full") -> SecurityAudit:
        """Perform comprehensive security audit"""
        
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        findings = []
        recommendations = []
        compliance_status = {}
        
        # Security configuration audit
        config_findings = await self._audit_security_configuration()
        findings.extend(config_findings)
        
        # Access control audit
        if audit_scope in ["full", "access_control"]:
            access_findings = await self._audit_access_control()
            findings.extend(access_findings)
        
        # Threat detection audit
        if audit_scope in ["full", "threat_detection"]:
            threat_findings = await self._audit_threat_detection()
            findings.extend(threat_findings)
        
        # Encryption audit
        if audit_scope in ["full", "encryption"]:
            encryption_findings = await self._audit_encryption()
            findings.extend(encryption_findings)
        
        # Calculate security score
        security_score = await self._calculate_security_score(findings)
        
        # Generate recommendations
        recommendations = await self._generate_security_recommendations(findings)
        
        # Check compliance
        compliance_status = await self._check_compliance_status()
        
        audit = SecurityAudit(
            audit_id=audit_id,
            audit_type=audit_scope,
            security_score=security_score,
            findings=findings,
            recommendations=recommendations,
            compliance_status=compliance_status
        )
        
        logger.info(f"Security audit completed: {audit_id} (score: {security_score:.2f})")
        return audit
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        
        recent_events = list(self.security_events)[-100:]
        
        return {
            'security_level': self.config.security_level.value,
            'active_threats': len([e for e in recent_events if not e.resolved]),
            'critical_threats': len([
                e for e in recent_events 
                if e.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EMERGENCY] and not e.resolved
            ]),
            'active_tokens': len(self.active_tokens),
            'blocked_ips': len(self.blocked_ips),
            'encryption_status': 'enabled' if self.config.encryption_enabled else 'disabled',
            'threat_detection_status': 'enabled' if self.config.threat_detection_enabled else 'disabled',
            'audit_log_count': len(self.audit_logs),
            'recent_security_score': await self._calculate_current_security_score()
        }
    
    # Private methods
    
    async def _initialize_security_rules(self):
        """Initialize security rules and patterns"""
        
        # Initialize detection rules
        self.threat_detector.detection_rules = [
            {
                'id': 'rule_001',
                'name': 'Multiple Authentication Failures',
                'event_type': SecurityEventType.AUTHENTICATION_FAILURE,
                'severity': ThreatSeverity.MEDIUM,
                'condition': 'consecutive_failures > 5'
            },
            {
                'id': 'rule_002',
                'name': 'Suspicious IP Activity',
                'event_type': SecurityEventType.SUSPICIOUS_ACTIVITY,
                'severity': ThreatSeverity.HIGH,
                'condition': 'ip_reputation_score < 0.3'
            }
        ]
    
    async def _start_security_monitoring(self):
        """Start security monitoring tasks"""
        
        async def monitoring_loop():
            while True:
                try:
                    await self._perform_routine_security_checks()
                    await asyncio.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Security monitoring error: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(monitoring_loop())
    
    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        
        try:
            # In production, use proper JWT secret from secure storage
            secret = "your-secret-key"  # This should be from config
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def _check_permissions(
        self,
        security_token: SecurityToken,
        required_permissions: List[AccessPermission]
    ) -> bool:
        """Check if token has required permissions"""
        
        for required_permission in required_permissions:
            if required_permission not in security_token.permissions:
                return False
        return True
    
    def _get_required_permission(self, operation: str) -> AccessPermission:
        """Get required permission for operation"""
        
        permission_map = {
            'read': AccessPermission.READ_ONLY,
            'write': AccessPermission.WRITE_LIMITED,
            'admin': AccessPermission.ADMIN_LIMITED,
            'system': AccessPermission.SYSTEM_ADMIN
        }
        
        return permission_map.get(operation, AccessPermission.READ_ONLY)
    
    async def _check_queue_specific_access(
        self,
        security_token: SecurityToken,
        queue_id: str,
        operation: str
    ) -> bool:
        """Check queue-specific access permissions"""
        
        # Check if user has access to specific queue
        user_queue_access = self.user_permissions.get(security_token.user_id, {})
        queue_permissions = user_queue_access.get(queue_id, [])
        
        required_permission = self._get_required_permission(operation)
        return required_permission in queue_permissions
    
    async def _log_security_event(
        self,
        event_type: SecurityEventType,
        severity: ThreatSeverity,
        source_ip: str = None,
        user_id: str = None,
        queue_id: str = None,
        description: str = ""
    ):
        """Log security event"""
        
        event = SecurityEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            queue_id=queue_id,
            description=description
        )
        
        self.security_events.append(event)
        
        # Add to audit log
        audit_entry = {
            'timestamp': event.timestamp,
            'event_type': event_type.value,
            'severity': severity.value,
            'description': description,
            'metadata': {
                'source_ip': source_ip,
                'user_id': user_id,
                'queue_id': queue_id
            }
        }
        self.audit_logs.append(audit_entry)
        
        logger.warning(f"Security event: {event_type.value} ({severity.value}) - {description}")
    
    async def _handle_critical_threat(self, threat: SecurityEvent):
        """Handle critical security threats"""
        
        logger.critical(f"Critical threat detected: {threat.description}")
        
        # Auto-block source IP if available
        if threat.source_ip:
            self.blocked_ips.add(threat.source_ip)
            logger.info(f"Auto-blocked IP: {threat.source_ip}")
        
        # Invalidate user tokens if user-related
        if threat.user_id:
            await self._invalidate_user_tokens(threat.user_id)
            logger.info(f"Invalidated tokens for user: {threat.user_id}")
        
        # Additional emergency measures
        if threat.severity == ThreatSeverity.EMERGENCY:
            await self._activate_emergency_mode()
    
    async def _invalidate_user_tokens(self, user_id: str):
        """Invalidate all tokens for a user"""
        
        tokens_to_remove = [
            token_id for token_id, token in self.active_tokens.items()
            if token.user_id == user_id
        ]
        
        for token_id in tokens_to_remove:
            del self.active_tokens[token_id]
    
    async def _activate_emergency_mode(self):
        """Activate emergency security mode"""
        
        logger.critical("EMERGENCY SECURITY MODE ACTIVATED")
        
        # Implement emergency measures
        # - Increase security level
        # - Tighten rate limits
        # - Enable additional monitoring
        # - Alert administrators
    
    async def _perform_routine_security_checks(self):
        """Perform routine security maintenance"""
        
        # Clean expired tokens
        await self._clean_expired_tokens()
        
        # Update threat intelligence
        await self._update_threat_intelligence()
        
        # Check system health
        await self._check_security_system_health()
    
    async def _clean_expired_tokens(self):
        """Clean expired authentication tokens"""
        
        now = datetime.now()
        expired_tokens = [
            token_id for token_id, token in self.active_tokens.items()
            if token.expires_at < now
        ]
        
        for token_id in expired_tokens:
            del self.active_tokens[token_id]
        
        if expired_tokens:
            logger.info(f"Cleaned {len(expired_tokens)} expired tokens")
    
    async def _update_threat_intelligence(self):
        """Update threat intelligence data"""
        
        # Placeholder for threat intelligence updates
        # In production, this would fetch from threat intelligence feeds
        pass
    
    async def _check_security_system_health(self):
        """Check security system health"""
        
        # Check encryption manager
        if self.config.encryption_enabled and not self.encryption_manager.active_key:
            logger.error("Encryption manager not properly initialized")
        
        # Check threat detector
        if self.config.threat_detection_enabled and not self.threat_detector.threat_patterns:
            logger.error("Threat detector not properly initialized")
    
    async def _audit_security_configuration(self) -> List[Dict[str, Any]]:
        """Audit security configuration"""
        
        findings = []
        
        # Check encryption settings
        if not self.config.encryption_enabled:
            findings.append({
                'category': 'encryption',
                'severity': 'medium',
                'issue': 'Encryption is disabled',
                'recommendation': 'Enable encryption for sensitive data'
            })
        
        # Check authentication settings
        if self.config.max_login_attempts > 10:
            findings.append({
                'category': 'authentication',
                'severity': 'low',
                'issue': f'High login attempt threshold: {self.config.max_login_attempts}',
                'recommendation': 'Reduce max login attempts to 5 or less'
            })
        
        return findings
    
    async def _audit_access_control(self) -> List[Dict[str, Any]]:
        """Audit access control configuration"""
        
        findings = []
        
        # Check for overprivileged users
        for user_id, permissions in self.user_permissions.items():
            admin_permissions = [p for p in permissions if 'admin' in str(p).lower()]
            if len(admin_permissions) > 2:
                findings.append({
                    'category': 'access_control',
                    'severity': 'medium',
                    'issue': f'User {user_id} has excessive admin permissions',
                    'recommendation': 'Review and reduce user privileges'
                })
        
        return findings
    
    async def _audit_threat_detection(self) -> List[Dict[str, Any]]:
        """Audit threat detection capabilities"""
        
        findings = []
        
        if not self.config.threat_detection_enabled:
            findings.append({
                'category': 'threat_detection',
                'severity': 'high',
                'issue': 'Threat detection is disabled',
                'recommendation': 'Enable threat detection for security monitoring'
            })
        
        return findings
    
    async def _audit_encryption(self) -> List[Dict[str, Any]]:
        """Audit encryption implementation"""
        
        findings = []
        
        if self.config.encryption_enabled:
            # Check key rotation
            if self.config.key_rotation_interval_hours > 168:  # 1 week
                findings.append({
                    'category': 'encryption',
                    'severity': 'low',
                    'issue': 'Key rotation interval too long',
                    'recommendation': 'Reduce key rotation to weekly or daily'
                })
        
        return findings
    
    async def _calculate_security_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate security score based on findings"""
        
        base_score = 1.0
        
        for finding in findings:
            severity = finding['severity']
            if severity == 'critical':
                base_score -= 0.2
            elif severity == 'high':
                base_score -= 0.1
            elif severity == 'medium':
                base_score -= 0.05
            elif severity == 'low':
                base_score -= 0.02
        
        return max(0.0, base_score)
    
    async def _generate_security_recommendations(
        self,
        findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate security recommendations"""
        
        recommendations = []
        
        # Extract recommendations from findings
        for finding in findings:
            recommendations.append(finding.get('recommendation', ''))
        
        # Add general recommendations
        if not self.config.encryption_enabled:
            recommendations.append("Enable encryption for sensitive data protection")
        
        if not self.config.threat_detection_enabled:
            recommendations.append("Enable threat detection for proactive security monitoring")
        
        return [r for r in recommendations if r]
    
    async def _check_compliance_status(self) -> Dict[str, bool]:
        """Check compliance with security standards"""
        
        return {
            'gdpr_compliant': self.config.audit_logging_enabled and self.config.encryption_enabled,
            'pci_dss_compliant': self.config.encryption_enabled and self.config.access_control_enabled,
            'iso27001_compliant': (
                self.config.threat_detection_enabled and 
                self.config.audit_logging_enabled and 
                self.config.access_control_enabled
            ),
            'soc2_compliant': (
                self.config.audit_logging_enabled and 
                self.config.access_control_enabled and 
                self.config.encryption_enabled
            )
        }
    
    async def _calculate_current_security_score(self) -> float:
        """Calculate current security score"""
        
        # Quick security assessment
        findings = []
        
        if not self.config.encryption_enabled:
            findings.append({'severity': 'medium'})
        
        if not self.config.threat_detection_enabled:
            findings.append({'severity': 'high'})
        
        if len(self.blocked_ips) > 100:
            findings.append({'severity': 'low'})
        
        return await self._calculate_security_score(findings)


# Factory function
def create_queue_security_manager(
    security_level: SecurityLevel = SecurityLevel.ENHANCED,
    enable_encryption: bool = True,
    enable_threat_detection: bool = True
) -> QueueSecurityManager:
    """Create queue security manager instance"""
    
    config = SecurityConfiguration(
        security_level=security_level,
        encryption_enabled=enable_encryption,
        threat_detection_enabled=enable_threat_detection
    )
    
    return QueueSecurityManager(config)


# Export all classes and functions
__all__ = [
    'QueueSecurityManager',
    'ThreatDetectionEngine',
    'EncryptionManager',
    'SecurityConfiguration',
    'SecurityEvent',
    'SecurityToken',
    'SecurityAudit',
    'SecurityLevel',
    'ThreatSeverity',
    'SecurityEventType',
    'AccessPermission',
    'create_queue_security_manager'
]
