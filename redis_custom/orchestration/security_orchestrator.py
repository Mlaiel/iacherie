#!/usr/bin/env python3
"""
🔒 Security Orchestrator
========================

Enterprise-grade security orchestration for Redis infrastructure with
zero-trust architecture, threat detection, and automated security response.

Expert Roles Combined:
- Security Architect: Enterprise security framework and threat modeling
- DevOps Engineer: Security automation and infrastructure protection
- Backend Senior: Secure distributed system architecture
- DBA: Database security and access control

Features:
- Zero-trust security orchestration
- Real-time threat detection and response
- Security policy enforcement
- Access control and authentication
- Security audit and compliance
- Vulnerability management
- Incident response automation
- Security metrics and reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security Architect + DevOps + Backend Senior + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
import secrets
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different operations"""
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
    """Types of security events"""
    LOGIN_ATTEMPT = "login_attempt"
    ACCESS_DENIED = "access_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALICIOUS_PAYLOAD = "malicious_payload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SECURITY_VIOLATION = "security_violation"

class AccessLevel(Enum):
    """Access control levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    policy_id: str
    name: str
    description: str
    level: SecurityLevel
    rules: List[Dict[str, Any]]
    enforcement_mode: str = "strict"  # strict, permissive, audit
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True

@dataclass
class SecurityThreat:
    """Security threat detection result"""
    threat_id: str
    event_type: SecurityEvent
    level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    indicators: List[str]
    timestamp: datetime
    mitigated: bool = False
    mitigation_actions: List[str] = field(default_factory=list)

@dataclass
class AccessControlEntry:
    """Access control entry"""
    user_id: str
    resource: str
    access_level: AccessLevel
    permissions: Set[str]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    granted_by: Optional[str] = None

@dataclass
class SecurityMetrics:
    """Security monitoring metrics"""
    total_requests: int = 0
    blocked_requests: int = 0
    threats_detected: int = 0
    threats_mitigated: int = 0
    policy_violations: int = 0
    access_denials: int = 0
    active_sessions: int = 0
    failed_authentications: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class RedisSecurityOrchestrator:
    """
    Enterprise Redis Security Orchestrator
    
    Comprehensive security orchestration for Redis infrastructure with
    zero-trust architecture, threat detection, and automated response.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Security configuration
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.access_control_entries: Dict[str, AccessControlEntry] = {}
        self.active_threats: Dict[str, SecurityThreat] = {}
        self.security_metrics = SecurityMetrics()
        
        # Encryption setup
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Security monitoring
        self.monitoring_enabled = config.get('monitoring_enabled', True)
        self.alert_threshold = config.get('alert_threshold', ThreatLevel.MEDIUM)
        
        # Audit logging
        self.audit_enabled = config.get('audit_enabled', True)
        self.audit_retention_days = config.get('audit_retention_days', 90)
        
        logger.info("Redis Security Orchestrator initialized")
    
    async def initialize(self):
        """Initialize security orchestrator"""
        try:
            # Setup Redis connection
            await self._setup_redis_connection()
            
            # Load security policies
            await self._load_security_policies()
            
            # Initialize access control
            await self._initialize_access_control()
            
            # Start security monitoring
            if self.monitoring_enabled:
                asyncio.create_task(self._start_security_monitoring())
            
            # Load rate limiting rules
            await self._load_rate_limits()
            
            logger.info("Security orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security orchestrator: {e}")
            raise
    
    async def _setup_redis_connection(self):
        """Setup Redis connection with security"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config['redis_url'],
                password=self.config.get('redis_password'),
                ssl=self.config.get('ssl_enabled', True),
                ssl_cert_reqs='required' if self.config.get('ssl_verify', True) else None,
                max_connections=self.config.get('max_connections', 100),
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Secure Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to setup Redis connection: {e}")
            raise
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        password = self.config.get('encryption_password', 'default_password').encode()
        salt = self.config.get('encryption_salt', 'default_salt').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def _load_security_policies(self):
        """Load security policies from configuration"""
        try:
            # Default security policies
            default_policies = [
                SecurityPolicy(
                    policy_id="auth_policy",
                    name="Authentication Policy",
                    description="Strong authentication requirements",
                    level=SecurityLevel.HIGH,
                    rules=[
                        {"type": "password_strength", "min_length": 12, "require_special": True},
                        {"type": "mfa_required", "enabled": True},
                        {"type": "session_timeout", "minutes": 30}
                    ]
                ),
                SecurityPolicy(
                    policy_id="access_policy",
                    name="Access Control Policy",
                    description="Zero-trust access control",
                    level=SecurityLevel.CRITICAL,
                    rules=[
                        {"type": "principle_least_privilege", "enabled": True},
                        {"type": "ip_whitelist", "enabled": True},
                        {"type": "geo_blocking", "enabled": True}
                    ]
                ),
                SecurityPolicy(
                    policy_id="data_policy",
                    name="Data Protection Policy",
                    description="Data encryption and protection",
                    level=SecurityLevel.CRITICAL,
                    rules=[
                        {"type": "encryption_at_rest", "enabled": True},
                        {"type": "encryption_in_transit", "enabled": True},
                        {"type": "data_classification", "enabled": True}
                    ]
                )
            ]
            
            for policy in default_policies:
                self.security_policies[policy.policy_id] = policy
            
            # Load custom policies from Redis
            try:
                stored_policies = await self.redis_client.get("security:policies")
                if stored_policies:
                    policies_data = json.loads(stored_policies)
                    for policy_data in policies_data:
                        policy = SecurityPolicy(**policy_data)
                        self.security_policies[policy.policy_id] = policy
            except Exception as e:
                logger.warning(f"Could not load stored policies: {e}")
            
            logger.info(f"Loaded {len(self.security_policies)} security policies")
            
        except Exception as e:
            logger.error(f"Failed to load security policies: {e}")
            raise
    
    async def _initialize_access_control(self):
        """Initialize access control system"""
        try:
            # Load existing access control entries
            try:
                stored_acl = await self.redis_client.get("security:acl")
                if stored_acl:
                    acl_data = json.loads(stored_acl)
                    for entry_data in acl_data:
                        entry = AccessControlEntry(**entry_data)
                        self.access_control_entries[entry.user_id] = entry
            except Exception as e:
                logger.warning(f"Could not load stored ACL: {e}")
            
            logger.info(f"Access control initialized with {len(self.access_control_entries)} entries")
            
        except Exception as e:
            logger.error(f"Failed to initialize access control: {e}")
            raise
    
    async def _start_security_monitoring(self):
        """Start continuous security monitoring"""
        logger.info("Starting security monitoring")
        
        while True:
            try:
                # Monitor for threats
                await self._scan_for_threats()
                
                # Check policy violations
                await self._check_policy_violations()
                
                # Update security metrics
                await self._update_security_metrics()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(self.config.get('monitoring_interval', 60))
                
            except Exception as e:
                logger.error(f"Error in security monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _scan_for_threats(self):
        """Scan for security threats"""
        try:
            # Check for suspicious patterns
            await self._detect_brute_force_attacks()
            await self._detect_privilege_escalation()
            await self._detect_data_exfiltration()
            await self._detect_malicious_payloads()
            
        except Exception as e:
            logger.error(f"Error scanning for threats: {e}")
    
    async def _detect_brute_force_attacks(self):
        """Detect brute force authentication attempts"""
        try:
            # Get failed login attempts in last 10 minutes
            ten_minutes_ago = time.time() - 600
            
            # Check Redis logs for failed attempts
            pattern_key = "security:failed_logins:*"
            keys = await self.redis_client.keys(pattern_key)
            
            for key in keys:
                attempts_data = await self.redis_client.zrangebyscore(
                    key, ten_minutes_ago, time.time(), withscores=True
                )
                
                if len(attempts_data) >= 5:  # 5 failed attempts in 10 minutes
                    # Extract IP from key
                    ip_address = key.decode().split(':')[-1]
                    
                    threat = SecurityThreat(
                        threat_id=str(uuid.uuid4()),
                        event_type=SecurityEvent.LOGIN_ATTEMPT,
                        level=ThreatLevel.HIGH,
                        source_ip=ip_address,
                        user_id=None,
                        description=f"Brute force attack detected from {ip_address}",
                        indicators=[f"Failed login attempts: {len(attempts_data)}"],
                        timestamp=datetime.now()
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"Error detecting brute force attacks: {e}")
    
    async def _detect_privilege_escalation(self):
        """Detect privilege escalation attempts"""
        try:
            # Monitor for unusual permission requests
            privilege_requests = await self.redis_client.zrange(
                "security:privilege_requests",
                0, -1, withscores=True
            )
            
            for request, score in privilege_requests:
                request_data = json.loads(request)
                
                # Check if user is requesting unusually high privileges
                if (request_data.get('requested_level') == 'super_admin' and
                    request_data.get('current_level') != 'admin'):
                    
                    threat = SecurityThreat(
                        threat_id=str(uuid.uuid4()),
                        event_type=SecurityEvent.PRIVILEGE_ESCALATION,
                        level=ThreatLevel.HIGH,
                        source_ip=request_data.get('source_ip', 'unknown'),
                        user_id=request_data.get('user_id'),
                        description="Privilege escalation attempt detected",
                        indicators=[
                            f"Requested: {request_data.get('requested_level')}",
                            f"Current: {request_data.get('current_level')}"
                        ],
                        timestamp=datetime.fromtimestamp(score)
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"Error detecting privilege escalation: {e}")
    
    async def _detect_data_exfiltration(self):
        """Detect potential data exfiltration"""
        try:
            # Monitor for unusual data access patterns
            data_access_key = "security:data_access"
            recent_access = await self.redis_client.zrange(
                data_access_key, 
                0, -1, withscores=True
            )
            
            # Analyze access patterns
            user_access_counts = {}
            for access, timestamp in recent_access:
                access_data = json.loads(access)
                user_id = access_data.get('user_id')
                
                if user_id not in user_access_counts:
                    user_access_counts[user_id] = 0
                user_access_counts[user_id] += 1
            
            # Check for users with unusually high access
            avg_access = sum(user_access_counts.values()) / len(user_access_counts) if user_access_counts else 0
            threshold = avg_access * 3  # 3x average is suspicious
            
            for user_id, count in user_access_counts.items():
                if count > threshold and count > 100:  # Also require absolute minimum
                    threat = SecurityThreat(
                        threat_id=str(uuid.uuid4()),
                        event_type=SecurityEvent.DATA_BREACH_ATTEMPT,
                        level=ThreatLevel.CRITICAL,
                        source_ip="unknown",
                        user_id=user_id,
                        description=f"Potential data exfiltration by user {user_id}",
                        indicators=[
                            f"Access count: {count}",
                            f"Average access: {avg_access:.2f}"
                        ],
                        timestamp=datetime.now()
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"Error detecting data exfiltration: {e}")
    
    async def _detect_malicious_payloads(self):
        """Detect malicious payloads in requests"""
        try:
            # Monitor Redis commands for suspicious patterns
            command_log_key = "security:command_log"
            recent_commands = await self.redis_client.lrange(command_log_key, 0, 1000)
            
            malicious_patterns = [
                'eval', 'script', 'debug', 'config', 'shutdown',
                'flushdb', 'flushall', 'script kill'
            ]
            
            for command in recent_commands:
                command_data = json.loads(command)
                command_text = command_data.get('command', '').lower()
                
                for pattern in malicious_patterns:
                    if pattern in command_text:
                        threat = SecurityThreat(
                            threat_id=str(uuid.uuid4()),
                            event_type=SecurityEvent.MALICIOUS_PAYLOAD,
                            level=ThreatLevel.HIGH,
                            source_ip=command_data.get('source_ip', 'unknown'),
                            user_id=command_data.get('user_id'),
                            description=f"Malicious payload detected: {pattern}",
                            indicators=[f"Command: {command_text}"],
                            timestamp=datetime.now()
                        )
                        
                        await self._handle_threat(threat)
                        break
            
        except Exception as e:
            logger.error(f"Error detecting malicious payloads: {e}")
    
    async def _handle_threat(self, threat: SecurityThreat):
        """Handle detected security threat"""
        try:
            # Store threat
            self.active_threats[threat.threat_id] = threat
            
            # Log threat
            logger.warning(f"Security threat detected: {threat.description}")
            
            # Apply mitigation actions based on threat level
            mitigation_actions = []
            
            if threat.level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                # Block source IP
                if threat.source_ip and threat.source_ip != "unknown":
                    await self._block_ip(threat.source_ip)
                    mitigation_actions.append(f"Blocked IP: {threat.source_ip}")
                
                # Suspend user if applicable
                if threat.user_id:
                    await self._suspend_user(threat.user_id)
                    mitigation_actions.append(f"Suspended user: {threat.user_id}")
            
            if threat.level == ThreatLevel.CRITICAL:
                # Emergency lockdown
                await self._emergency_lockdown()
                mitigation_actions.append("Emergency lockdown activated")
            
            # Update threat with mitigation actions
            threat.mitigation_actions = mitigation_actions
            threat.mitigated = len(mitigation_actions) > 0
            
            # Store threat details
            await self._store_threat(threat)
            
            # Send alerts
            await self._send_security_alert(threat)
            
            # Update metrics
            self.security_metrics.threats_detected += 1
            if threat.mitigated:
                self.security_metrics.threats_mitigated += 1
            
        except Exception as e:
            logger.error(f"Error handling threat: {e}")
    
    async def _block_ip(self, ip_address: str):
        """Block malicious IP address"""
        try:
            # Add to blocked IPs list
            await self.redis_client.sadd("security:blocked_ips", ip_address)
            
            # Set expiration (24 hours)
            await self.redis_client.expire("security:blocked_ips", 86400)
            
            logger.info(f"Blocked IP address: {ip_address}")
            
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
    
    async def _suspend_user(self, user_id: str):
        """Suspend user account"""
        try:
            # Add to suspended users
            suspension_data = {
                'user_id': user_id,
                'suspended_at': datetime.now().isoformat(),
                'reason': 'Security threat detected'
            }
            
            await self.redis_client.hset(
                "security:suspended_users",
                user_id,
                json.dumps(suspension_data)
            )
            
            logger.info(f"Suspended user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error suspending user {user_id}: {e}")
    
    async def _emergency_lockdown(self):
        """Activate emergency security lockdown"""
        try:
            # Set lockdown flag
            lockdown_data = {
                'activated_at': datetime.now().isoformat(),
                'reason': 'Critical security threat detected'
            }
            
            await self.redis_client.set(
                "security:emergency_lockdown",
                json.dumps(lockdown_data),
                ex=3600  # 1 hour
            )
            
            logger.critical("Emergency security lockdown activated")
            
        except Exception as e:
            logger.error(f"Error activating emergency lockdown: {e}")
    
    async def _store_threat(self, threat: SecurityThreat):
        """Store threat details for analysis"""
        try:
            threat_data = {
                'threat_id': threat.threat_id,
                'event_type': threat.event_type.value,
                'level': threat.level.value,
                'source_ip': threat.source_ip,
                'user_id': threat.user_id,
                'description': threat.description,
                'indicators': threat.indicators,
                'timestamp': threat.timestamp.isoformat(),
                'mitigated': threat.mitigated,
                'mitigation_actions': threat.mitigation_actions
            }
            
            # Store in threat log
            await self.redis_client.lpush(
                "security:threat_log",
                json.dumps(threat_data)
            )
            
            # Trim log to last 10000 entries
            await self.redis_client.ltrim("security:threat_log", 0, 9999)
            
        except Exception as e:
            logger.error(f"Error storing threat: {e}")
    
    async def _send_security_alert(self, threat: SecurityThreat):
        """Send security alert notification"""
        try:
            # Create alert message
            alert_data = {
                'alert_id': str(uuid.uuid4()),
                'threat_id': threat.threat_id,
                'level': threat.level.value,
                'message': threat.description,
                'timestamp': datetime.now().isoformat(),
                'requires_attention': threat.level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            }
            
            # Store alert
            await self.redis_client.lpush(
                "security:alerts",
                json.dumps(alert_data)
            )
            
            # Publish to alert channel
            await self.redis_client.publish(
                "security_alerts",
                json.dumps(alert_data)
            )
            
            logger.info(f"Security alert sent: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
    
    async def _check_policy_violations(self):
        """Check for security policy violations"""
        try:
            # Check each active policy
            for policy_id, policy in self.security_policies.items():
                if not policy.enabled:
                    continue
                
                # Check policy rules
                for rule in policy.rules:
                    await self._check_policy_rule(policy, rule)
            
        except Exception as e:
            logger.error(f"Error checking policy violations: {e}")
    
    async def _check_policy_rule(self, policy: SecurityPolicy, rule: Dict[str, Any]):
        """Check specific policy rule"""
        try:
            rule_type = rule.get('type')
            
            if rule_type == 'session_timeout':
                await self._check_session_timeout_rule(policy, rule)
            elif rule_type == 'ip_whitelist':
                await self._check_ip_whitelist_rule(policy, rule)
            elif rule_type == 'encryption_at_rest':
                await self._check_encryption_rule(policy, rule)
            # Add more rule types as needed
            
        except Exception as e:
            logger.error(f"Error checking policy rule {rule.get('type')}: {e}")
    
    async def _check_session_timeout_rule(self, policy: SecurityPolicy, rule: Dict[str, Any]):
        """Check session timeout policy rule"""
        try:
            timeout_minutes = rule.get('minutes', 30)
            timeout_seconds = timeout_minutes * 60
            
            # Get active sessions
            active_sessions = await self.redis_client.hgetall("security:active_sessions")
            
            current_time = time.time()
            expired_sessions = []
            
            for session_id, session_data in active_sessions.items():
                session_info = json.loads(session_data)
                last_activity = session_info.get('last_activity', 0)
                
                if current_time - last_activity > timeout_seconds:
                    expired_sessions.append(session_id.decode())
            
            # Remove expired sessions
            for session_id in expired_sessions:
                await self.redis_client.hdel("security:active_sessions", session_id)
                logger.info(f"Expired session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error checking session timeout rule: {e}")
    
    async def _check_ip_whitelist_rule(self, policy: SecurityPolicy, rule: Dict[str, Any]):
        """Check IP whitelist policy rule"""
        try:
            if not rule.get('enabled', False):
                return
            
            # Get whitelist
            whitelist = await self.redis_client.smembers("security:ip_whitelist")
            whitelist_ips = {ip.decode() for ip in whitelist}
            
            # Get recent connections
            recent_connections = await self.redis_client.lrange("security:connections", 0, 100)
            
            for connection in recent_connections:
                connection_data = json.loads(connection)
                source_ip = connection_data.get('source_ip')
                
                if source_ip and source_ip not in whitelist_ips:
                    # Policy violation
                    violation_data = {
                        'policy_id': policy.policy_id,
                        'rule_type': 'ip_whitelist',
                        'source_ip': source_ip,
                        'timestamp': datetime.now().isoformat(),
                        'action': 'blocked'
                    }
                    
                    await self.redis_client.lpush(
                        "security:policy_violations",
                        json.dumps(violation_data)
                    )
                    
                    # Block the IP
                    await self._block_ip(source_ip)
                    
                    self.security_metrics.policy_violations += 1
            
        except Exception as e:
            logger.error(f"Error checking IP whitelist rule: {e}")
    
    async def _check_encryption_rule(self, policy: SecurityPolicy, rule: Dict[str, Any]):
        """Check encryption policy rule"""
        try:
            if not rule.get('enabled', False):
                return
            
            # Check for unencrypted data
            unencrypted_keys = await self.redis_client.keys("data:unencrypted:*")
            
            if unencrypted_keys:
                violation_data = {
                    'policy_id': policy.policy_id,
                    'rule_type': 'encryption_at_rest',
                    'unencrypted_count': len(unencrypted_keys),
                    'timestamp': datetime.now().isoformat(),
                    'action': 'encrypt'
                }
                
                await self.redis_client.lpush(
                    "security:policy_violations",
                    json.dumps(violation_data)
                )
                
                # Encrypt the data
                for key in unencrypted_keys:
                    await self._encrypt_redis_key(key.decode())
                
                self.security_metrics.policy_violations += 1
            
        except Exception as e:
            logger.error(f"Error checking encryption rule: {e}")
    
    async def _encrypt_redis_key(self, key: str):
        """Encrypt Redis key data"""
        try:
            # Get current data
            data = await self.redis_client.get(key)
            if not data:
                return
            
            # Encrypt data
            encrypted_data = self.cipher_suite.encrypt(data)
            
            # Store encrypted data with new key
            encrypted_key = key.replace("unencrypted", "encrypted")
            await self.redis_client.set(encrypted_key, encrypted_data)
            
            # Remove unencrypted data
            await self.redis_client.delete(key)
            
            logger.info(f"Encrypted data: {key} -> {encrypted_key}")
            
        except Exception as e:
            logger.error(f"Error encrypting key {key}: {e}")
    
    async def _update_security_metrics(self):
        """Update security monitoring metrics"""
        try:
            # Update timestamp
            self.security_metrics.timestamp = datetime.now()
            
            # Count active sessions
            active_sessions = await self.redis_client.hlen("security:active_sessions")
            self.security_metrics.active_sessions = active_sessions
            
            # Count recent blocked requests
            recent_blocks = await self.redis_client.zcount(
                "security:blocked_requests",
                time.time() - 3600,  # Last hour
                time.time()
            )
            self.security_metrics.blocked_requests = recent_blocks
            
            # Store metrics
            metrics_data = {
                'total_requests': self.security_metrics.total_requests,
                'blocked_requests': self.security_metrics.blocked_requests,
                'threats_detected': self.security_metrics.threats_detected,
                'threats_mitigated': self.security_metrics.threats_mitigated,
                'policy_violations': self.security_metrics.policy_violations,
                'access_denials': self.security_metrics.access_denials,
                'active_sessions': self.security_metrics.active_sessions,
                'failed_authentications': self.security_metrics.failed_authentications,
                'timestamp': self.security_metrics.timestamp.isoformat()
            }
            
            await self.redis_client.set(
                "security:metrics",
                json.dumps(metrics_data),
                ex=3600  # 1 hour
            )
            
        except Exception as e:
            logger.error(f"Error updating security metrics: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old security data"""
        try:
            # Clean up old logs based on retention policy
            retention_seconds = self.audit_retention_days * 24 * 3600
            cutoff_time = time.time() - retention_seconds
            
            # Clean old threat logs
            await self.redis_client.zremrangebyscore(
                "security:threat_log_index",
                0, cutoff_time
            )
            
            # Clean old audit logs
            await self.redis_client.zremrangebyscore(
                "security:audit_log",
                0, cutoff_time
            )
            
            # Clean old blocked IPs (keep for 24 hours max)
            await self.redis_client.zremrangebyscore(
                "security:blocked_ips_history",
                0, time.time() - 86400
            )
            
            logger.debug("Cleaned up old security data")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def _load_rate_limits(self):
        """Load rate limiting configuration"""
        try:
            # Default rate limits
            default_limits = {
                'global': {'requests_per_minute': 1000, 'burst': 100},
                'user': {'requests_per_minute': 100, 'burst': 20},
                'ip': {'requests_per_minute': 200, 'burst': 50},
                'api': {'requests_per_minute': 500, 'burst': 100}
            }
            
            # Load custom limits from Redis
            stored_limits = await self.redis_client.get("security:rate_limits")
            if stored_limits:
                custom_limits = json.loads(stored_limits)
                default_limits.update(custom_limits)
            
            self.rate_limits = default_limits
            logger.info(f"Loaded rate limits: {self.rate_limits}")
            
        except Exception as e:
            logger.error(f"Error loading rate limits: {e}")
    
    async def check_rate_limit(self, identifier: str, limit_type: str = 'user') -> bool:
        """Check if request is within rate limits"""
        try:
            if limit_type not in self.rate_limits:
                return True
            
            limit_config = self.rate_limits[limit_type]
            requests_per_minute = limit_config['requests_per_minute']
            
            # Use sliding window rate limiting
            current_time = time.time()
            window_start = current_time - 60  # 1 minute window
            
            rate_key = f"security:rate_limit:{limit_type}:{identifier}"
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests
            current_requests = await self.redis_client.zcard(rate_key)
            
            if current_requests >= requests_per_minute:
                # Rate limit exceeded
                await self.redis_client.zincrby(
                    "security:rate_limit_violations",
                    1, identifier
                )
                return False
            
            # Add current request
            await self.redis_client.zadd(rate_key, {str(uuid.uuid4()): current_time})
            await self.redis_client.expire(rate_key, 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Fail open for availability
    
    async def authenticate_user(self, user_id: str, password: str, source_ip: str) -> bool:
        """Authenticate user with security checks"""
        try:
            # Check if user is suspended
            suspended_users = await self.redis_client.hgetall("security:suspended_users")
            if user_id.encode() in suspended_users:
                logger.warning(f"Authentication attempt by suspended user: {user_id}")
                return False
            
            # Check if IP is blocked
            blocked_ips = await self.redis_client.smembers("security:blocked_ips")
            if source_ip.encode() in blocked_ips:
                logger.warning(f"Authentication attempt from blocked IP: {source_ip}")
                return False
            
            # Check rate limiting
            if not await self.check_rate_limit(f"{user_id}:{source_ip}", 'user'):
                logger.warning(f"Rate limit exceeded for user {user_id} from {source_ip}")
                await self._record_failed_login(user_id, source_ip, "rate_limit_exceeded")
                return False
            
            # Verify password (simplified - implement proper password verification)
            stored_password = await self.redis_client.hget("users:passwords", user_id)
            if not stored_password:
                await self._record_failed_login(user_id, source_ip, "user_not_found")
                return False
            
            # Hash provided password and compare
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash != stored_password.decode():
                await self._record_failed_login(user_id, source_ip, "invalid_password")
                return False
            
            # Authentication successful
            await self._record_successful_login(user_id, source_ip)
            return True
            
        except Exception as e:
            logger.error(f"Error authenticating user {user_id}: {e}")
            return False
    
    async def _record_failed_login(self, user_id: str, source_ip: str, reason: str):
        """Record failed login attempt"""
        try:
            # Record for user
            await self.redis_client.zadd(
                f"security:failed_logins:{source_ip}",
                {f"{user_id}:{reason}": time.time()}
            )
            
            # Set expiration
            await self.redis_client.expire(f"security:failed_logins:{source_ip}", 3600)
            
            # Update metrics
            self.security_metrics.failed_authentications += 1
            
            logger.info(f"Failed login: {user_id} from {source_ip}, reason: {reason}")
            
        except Exception as e:
            logger.error(f"Error recording failed login: {e}")
    
    async def _record_successful_login(self, user_id: str, source_ip: str):
        """Record successful login"""
        try:
            # Create session
            session_id = str(uuid.uuid4())
            session_data = {
                'user_id': user_id,
                'source_ip': source_ip,
                'login_time': time.time(),
                'last_activity': time.time()
            }
            
            await self.redis_client.hset(
                "security:active_sessions",
                session_id,
                json.dumps(session_data)
            )
            
            # Clear failed login attempts for this IP
            await self.redis_client.delete(f"security:failed_logins:{source_ip}")
            
            logger.info(f"Successful login: {user_id} from {source_ip}")
            
        except Exception as e:
            logger.error(f"Error recording successful login: {e}")
    
    async def authorize_access(self, user_id: str, resource: str, action: str) -> bool:
        """Authorize user access to resource"""
        try:
            # Check if user exists in ACL
            if user_id not in self.access_control_entries:
                logger.warning(f"User {user_id} not found in ACL")
                self.security_metrics.access_denials += 1
                return False
            
            acl_entry = self.access_control_entries[user_id]
            
            # Check if access has expired
            if acl_entry.expires_at and datetime.now() > acl_entry.expires_at:
                logger.warning(f"Access expired for user {user_id}")
                self.security_metrics.access_denials += 1
                return False
            
            # Check resource access
            if acl_entry.resource != "*" and acl_entry.resource != resource:
                logger.warning(f"User {user_id} denied access to resource {resource}")
                self.security_metrics.access_denials += 1
                return False
            
            # Check permission
            if action not in acl_entry.permissions:
                logger.warning(f"User {user_id} denied permission {action} on {resource}")
                self.security_metrics.access_denials += 1
                return False
            
            # Access granted
            await self._record_access_granted(user_id, resource, action)
            return True
            
        except Exception as e:
            logger.error(f"Error authorizing access for {user_id}: {e}")
            return False
    
    async def _record_access_granted(self, user_id: str, resource: str, action: str):
        """Record successful access"""
        try:
            access_data = {
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'timestamp': time.time()
            }
            
            await self.redis_client.zadd(
                "security:data_access",
                {json.dumps(access_data): time.time()}
            )
            
            # Keep only last 10000 access records
            await self.redis_client.zremrangebyrank("security:data_access", 0, -10001)
            
        except Exception as e:
            logger.error(f"Error recording access granted: {e}")
    
    async def add_security_policy(self, policy: SecurityPolicy) -> bool:
        """Add new security policy"""
        try:
            self.security_policies[policy.policy_id] = policy
            
            # Store in Redis
            policies_data = []
            for p in self.security_policies.values():
                policy_dict = {
                    'policy_id': p.policy_id,
                    'name': p.name,
                    'description': p.description,
                    'level': p.level.value,
                    'rules': p.rules,
                    'enforcement_mode': p.enforcement_mode,
                    'created_at': p.created_at.isoformat(),
                    'updated_at': p.updated_at.isoformat(),
                    'enabled': p.enabled
                }
                policies_data.append(policy_dict)
            
            await self.redis_client.set(
                "security:policies",
                json.dumps(policies_data)
            )
            
            logger.info(f"Added security policy: {policy.policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding security policy: {e}")
            return False
    
    async def add_access_control_entry(self, entry: AccessControlEntry) -> bool:
        """Add access control entry"""
        try:
            self.access_control_entries[entry.user_id] = entry
            
            # Store in Redis
            acl_data = []
            for ace in self.access_control_entries.values():
                entry_dict = {
                    'user_id': ace.user_id,
                    'resource': ace.resource,
                    'access_level': ace.access_level.value,
                    'permissions': list(ace.permissions),
                    'granted_at': ace.granted_at.isoformat(),
                    'expires_at': ace.expires_at.isoformat() if ace.expires_at else None,
                    'granted_by': ace.granted_by
                }
                acl_data.append(entry_dict)
            
            await self.redis_client.set(
                "security:acl",
                json.dumps(acl_data)
            )
            
            logger.info(f"Added ACL entry for user: {entry.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding ACL entry: {e}")
            return False
    
    async def get_security_metrics(self) -> SecurityMetrics:
        """Get current security metrics"""
        return self.security_metrics
    
    async def get_active_threats(self) -> List[SecurityThreat]:
        """Get list of active threats"""
        return list(self.active_threats.values())
    
    async def get_security_policies(self) -> List[SecurityPolicy]:
        """Get list of security policies"""
        return list(self.security_policies.values())
    
    async def close(self):
        """Close security orchestrator"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            logger.info("Security orchestrator closed")
            
        except Exception as e:
            logger.error(f"Error closing security orchestrator: {e}")

# Configuration schema for security orchestrator
@dataclass
class SecurityOrchestratorConfig:
    """Security orchestrator configuration"""
    redis_url: str
    redis_password: Optional[str] = None
    ssl_enabled: bool = True
    ssl_verify: bool = True
    max_connections: int = 100
    monitoring_enabled: bool = True
    monitoring_interval: int = 60
    alert_threshold: ThreatLevel = ThreatLevel.MEDIUM
    audit_enabled: bool = True
    audit_retention_days: int = 90
    encryption_password: str = "default_password"
    encryption_salt: str = "default_salt"