"""IA Influencer Agent - Advanced Indexing Security
===============================================

Enterprise-grade security system for content indexing operations
with encryption, access control, audit logging, and threat detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import time
import json
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import ipaddress
from redis.asyncio import Redis
from collections import defaultdict, deque
import re

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """
Security levels for content protection"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class AccessType(Enum):
    """Types of access operations"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SEARCH = "search"
    INDEX = "index"


class ThreatLevel(Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_algorithm: str = "AES-256-GCM"
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_expiration_hours: int = 24
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    audit_retention_days: int = 365
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    enable_ip_whitelist: bool = False
    allowed_ip_ranges: List[str] = None
    password_min_length: int = 8
    require_mfa: bool = True


@dataclass
class UserCredentials:
    """User credentials structure"""
    user_id: str
    username: str
    password_hash: str
    salt: str
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None


@dataclass
class AccessToken:
    """
Access token structure"""
    token_id: str
    user_id: str
    token_type: str  # "access", "refresh", "api"
    scopes: List[str]
    expires_at: datetime
    created_at: datetime
    last_used: Optional[datetime] = None
    revoked: bool = False


@dataclass
class AuditLogEntry:
    """Audit log entry structure"""
    log_id: str
    user_id: str
    action: str
    resource: str
    result: str  # "success", "failure", "denied"
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    security_level: SecurityLevel


@dataclass
class SecurityThreat:
    """Security threat detection structure"""
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    detected_at: datetime
    indicators: Dict[str, Any]
    mitigated: bool = False


class EncryptionManager:
    """
Advanced encryption and decryption management"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.master_key = None
        self.field_keys = {}
        self.cipher_suite = None
        
    async def initialize(self):
        """
Initialize encryption manager"""
        try:
            # Generate or load master key
            self.master_key = self._generate_master_key()
            self.cipher_suite = Fernet(self.master_key)
            
            # Generate field-specific encryption keys
            await self._generate_field_keys()
            
            logger.info("EncryptionManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize EncryptionManager: {e}")
            raise
    
    def _generate_master_key(self) -> bytes:
        """Generate or retrieve master encryption key"""
        try:
            # In production, this would be retrieved from a secure key management service
            password = self.config.jwt_secret_key.encode()
            salt = b'ia_influencer_salt'  # In production, use random salt stored securely
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
            
        except Exception as e:
            logger.error(f"Failed to generate master key: {e}")
            raise
    
    async def _generate_field_keys(self):
        """Generate encryption keys for specific data fields"""
        try:
            sensitive_fields = [
                "user_credentials", "personal_data", "financial_data",
                "api_keys", "content_metadata", "search_queries"
            ]
            
            for field in sensitive_fields:
                field_key = Fernet.generate_key()
                self.field_keys[field] = Fernet(field_key)
                
        except Exception as e:
            logger.error(f"Failed to generate field keys: {e}")
            raise
    
    async def encrypt_data(
        self, 
        data: Union[str, Dict, List], 
        field_type: str = "general"
    ) -> str:
        """Encrypt data with field-specific encryption"""
        try:
            # Serialize data
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, default=str)
            else:
                data_str = str(data)
            
            # Choose encryption cipher
            if field_type in self.field_keys:
                cipher = self.field_keys[field_type]
            else:
                cipher = self.cipher_suite
            
            # Encrypt data
            encrypted_data = cipher.encrypt(data_str.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    async def decrypt_data(
        self, 
        encrypted_data: str, 
        field_type: str = "general"
    ) -> Union[str, Dict, List]:
        """Decrypt data with field-specific decryption"""
        try:
            # Decode base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Choose decryption cipher
            if field_type in self.field_keys:
                cipher = self.field_keys[field_type]
            else:
                cipher = self.cipher_suite
            
            # Decrypt data
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode()
            
            # Try to deserialize JSON
            try:
                return json.loads(decrypted_str)
            except:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    async def generate_content_hash(self, content: bytes) -> str:
        """Generate secure hash for content integrity"""
        try:
            sha256_hash = hashlib.sha256()
            sha256_hash.update(content)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to generate content hash: {e}")
            raise
    
    async def verify_content_integrity(self, content: bytes, expected_hash: str) -> bool:
        """Verify content integrity using hash"""
        try:
            computed_hash = await self.generate_content_hash(content)
            return hmac.compare_digest(computed_hash, expected_hash)
            
        except Exception as e:
            logger.error(f"Failed to verify content integrity: {e}")
            return False


class AccessControlManager:
    """Role-based access control management"""
    
    def __init__(self, config: SecurityConfig, redis_client: Redis):
        self.config = config
        self.redis_client = redis_client
        self.user_credentials = {}
        self.active_tokens = {}
        self.role_permissions = {}
        self._setup_default_roles()
        
    def _setup_default_roles(self):
        """
Setup default roles and permissions"""
        self.role_permissions = {
            "admin": [
                AccessType.READ, AccessType.WRITE, AccessType.DELETE,
                AccessType.ADMIN, AccessType.SEARCH, AccessType.INDEX
            ],
            "creator": [
                AccessType.READ, AccessType.WRITE, AccessType.SEARCH, AccessType.INDEX
            ],
            "viewer": [
                AccessType.READ, AccessType.SEARCH
            ],
            "api_user": [
                AccessType.READ, AccessType.SEARCH, AccessType.INDEX
            ]
        }
    
    async def create_user(
        self, 
        username: str, 
        try:
            logger.info(f"Executing create_user")
            
            # Implementation for create_user
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"create_user completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"create_user failed: {e}")
            raise
            user_id = secrets.token_urlsafe(16)
            
            # Generate salt and hash password
            salt = secrets.token_urlsafe(32)
            password_hash = self._hash_password(password, salt)
            
            # Create user credentials
            credentials = UserCredentials(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                salt=salt,
                roles=roles,
                permissions=self._get_permissions_for_roles(roles),
                created_at=datetime.now(timezone.utc)
            )
            
            # Store in memory and Redis
            self.user_credentials[user_id] = credentials
            await self.redis_client.hset(
                "user_credentials",
                user_id,
                json.dumps(asdict(credentials), default=str)
            )
            
            logger.info(f"Created user: {username} with roles: {roles}")
        try:
            logger.info(f"Executing _hash_password")
            
            # Implementation for _hash_password
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_hash_password completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_hash_password failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            raise
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using PBKDF2"""
        try:
            password_bytes = password.encode('utf-8')
            salt_bytes = salt.encode('utf-8')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            
            key = kdf.derive(password_bytes)
            return base64.urlsafe_b64encode(key).decode()
            
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise
    
    def _get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        """Get combined permissions for user roles"""
        permissions = set()
        for role in roles:
            if role in self.role_permissions:
                permissions.update([perm.value for perm in self.role_permissions[role]])
        return list(permissions)
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str,
        ip_address: str = None,
        mfa_token: str = None
    ) -> Optional[str]:
        """
Authenticate user and return access token"""
        try:
            # Find user by username
            user_creds = None
            for creds in self.user_credentials.values():
                if creds.username == username:
                    user_creds = creds
                    break
            
            if not user_creds:
                logger.warning(f"Authentication failed: user {username} not found")
                return None
            
            # Check if account is locked
            if (user_creds.account_locked_until and 
                user_creds.account_locked_until > datetime.now(timezone.utc)):
                logger.warning(f"Authentication failed: account {username} is locked")
                return None
            
            # Verify password
            password_hash = self._hash_password(password, user_creds.salt)
            if not hmac.compare_digest(password_hash, user_creds.password_hash):
                # Increment failed attempts
                user_creds.failed_login_attempts += 1
                
                if user_creds.failed_login_attempts >= self.config.max_login_attempts:
                    user_creds.account_locked_until = (
                        datetime.now(timezone.utc) + 
                        timedelta(minutes=self.config.lockout_duration_minutes)
                    )
                    logger.warning(f"Account {username} locked due to failed attempts")
                
                await self._update_user_credentials(user_creds)
                logger.warning(f"Authentication failed: invalid password for {username}")
                return None
            
            # Verify MFA if enabled
            if user_creds.mfa_enabled and self.config.require_mfa:
                if not mfa_token or not self._verify_mfa_token(user_creds.mfa_secret, mfa_token):
                    logger.warning(f"Authentication failed: invalid MFA token for {username}")
                    return None
            
            # Reset failed attempts on successful authentication
            user_creds.failed_login_attempts = 0
            user_creds.last_login = datetime.now(timezone.utc)
            user_creds.account_locked_until = None
            await self._update_user_credentials(user_creds)
            
            # Generate access token
            token = await self._generate_access_token(user_creds)
            
            logger.info(f"User {username} authenticated successfully from {ip_address}")
            return token
            
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            return None
    
    def _verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verify MFA token (TOTP)"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except:
            return False
    
    async def _generate_access_token(self, user_creds: UserCredentials) -> str:
        """
Generate JWT access token"""
        try:
            token_id = secrets.token_urlsafe(16)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.config.jwt_expiration_hours)
            
            payload = {
                "token_id": token_id,
                "user_id": user_creds.user_id,
                "username": user_creds.username,
                "roles": user_creds.roles,
                "permissions": user_creds.permissions,
                "exp": expires_at.timestamp(),
                "iat": datetime.now(timezone.utc).timestamp()
            }
            
            token = jwt.encode(payload, self.config.jwt_secret_key, algorithm="HS256")
            
            # Store token info
            token_info = AccessToken(
                token_id=token_id,
                user_id=user_creds.user_id,
                token_type="access",
                scopes=user_creds.permissions,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc)
            )
            
            self.active_tokens[token_id] = token_info
            await self.redis_client.setex(
                f"access_token:{token_id}",
                self.config.jwt_expiration_hours * 3600,
                json.dumps(asdict(token_info), default=str)
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            raise
    
    async def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                token, 
                self.config.jwt_secret_key, 
                algorithms=["HS256"]
            )
            
            token_id = payload.get("token_id")
            
            # Check if token is active
            if token_id in self.active_tokens:
                token_info = self.active_tokens[token_id]
                if not token_info.revoked and token_info.expires_at > datetime.now(timezone.utc):
                    # Update last used
                    token_info.last_used = datetime.now(timezone.utc)
                    return payload
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid access token")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def check_permission(
        self, 
        user_id: str, 
        resource: str, 
        access_type: AccessType
    ) -> bool:
        """Check if user has permission for specific resource access"""
        try:
            if user_id not in self.user_credentials:
                return False
            
            user_creds = self.user_credentials[user_id]
            
            # Check if user has required permission
            required_permission = access_type.value
            if required_permission in user_creds.permissions:
                return True
            
            # Check admin override
            if "admin" in user_creds.roles:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    async def _update_user_credentials(self, credentials: UserCredentials):
        """Update user credentials in storage"""
        try:
            self.user_credentials[credentials.user_id] = credentials
            await self.redis_client.hset(
                "user_credentials",
                credentials.user_id,
                json.dumps(asdict(credentials), default=str)
            )
        except Exception as e:
            logger.error(f"Failed to update user credentials: {e}")


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, config: SecurityConfig, redis_client: Redis):
        self.config = config
        self.redis_client = redis_client
        self.audit_buffer = deque(maxlen=1000)
        
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None,
        security_level: SecurityLevel = SecurityLevel.INTERNAL
    ):
        """
Log user action for audit trail"""
        try:
            log_entry = AuditLogEntry(
                log_id=secrets.token_urlsafe(16),
                user_id=user_id,
                action=action,
                resource=resource,
                result=result,
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown",
                timestamp=datetime.now(timezone.utc),
                details=details or {},
                security_level=security_level
            )
            
            # Add to buffer
            self.audit_buffer.append(log_entry)
            
            # Store in Redis with TTL
            await self.redis_client.zadd(
                "audit_logs",
                {
                    json.dumps(asdict(log_entry), default=str): time.time()
                }
            )
            
            # Clean old logs based on retention policy
            cutoff_time = time.time() - (self.config.audit_retention_days * 24 * 3600)
            await self.redis_client.zremrangebyscore("audit_logs", 0, cutoff_time)
            
            # Log critical actions immediately
            if security_level in [SecurityLevel.RESTRICTED, SecurityLevel.TOP_SECRET]:
                logger.critical(f"HIGH SECURITY ACTION: {action} on {resource} by {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
    
    async def get_audit_logs(
        self,
        user_id: str = None,
        action: str = None,
        time_range: Dict[str, datetime] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Retrieve audit logs with filters"""
        try:
            # Get logs from Redis
            if time_range:
                start_time = time_range["start"].timestamp()
                end_time = time_range["end"].timestamp()
                log_entries = await self.redis_client.zrangebyscore(
                    "audit_logs", start_time, end_time, withscores=False
                )
            else:
                log_entries = await self.redis_client.zrange(
                    "audit_logs", -limit, -1, withscores=False
                )
            
            logs = []
            for entry_json in log_entries:
                try:
                    entry_dict = json.loads(entry_json)
                    log_entry = AuditLogEntry(**entry_dict)
                    
                    # Apply filters
                    if user_id and log_entry.user_id != user_id:
                        continue
                    if action and log_entry.action != action:
                        continue
                    
                    logs.append(log_entry)
                except:
                    continue
            
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []


class ThreatDetector:
    """Advanced threat detection and prevention"""
    
    def __init__(self, config: SecurityConfig, redis_client: Redis):
        self.config = config
        self.redis_client = redis_client
        self.threat_patterns = {}
        self.active_threats = {}
        self.ip_reputation = defaultdict(float)
        self.rate_limits = defaultdict(deque)
        self._setup_threat_patterns()
        
    def _setup_threat_patterns(self):
        """
Setup threat detection patterns"""
        self.threat_patterns = {
            "brute_force": {
                "pattern": "multiple_failed_logins",
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "severity": ThreatLevel.HIGH
            },
            "sql_injection": {
                "pattern": r"(union|select|insert|delete|drop|alter|exec|script)",
                "threshold": 1,
                "time_window": 60,
                "severity": ThreatLevel.CRITICAL
            },
            "suspicious_ip": {
                "pattern": "known_malicious_ip",
                "threshold": 1,
                "time_window": 3600,
                "severity": ThreatLevel.MEDIUM
            },
            "rate_limit_exceeded": {
                "pattern": "excessive_requests",
                "threshold": self.config.rate_limit_requests_per_minute,
                "time_window": 60,
                "severity": ThreatLevel.MEDIUM
            }
        }
    
    async def analyze_request(
        self,
        ip_address: str,
        user_id: str = None,
        request_data: Dict[str, Any] = None
    ) -> Optional[SecurityThreat]:
        """Analyze incoming request for threats"""
        try:
            # Check rate limiting
            threat = await self._check_rate_limit(ip_address, user_id)
            if threat:
                return threat
            
            # Check IP reputation
            threat = await self._check_ip_reputation(ip_address)
            if threat:
                return threat
            
            # Check for SQL injection patterns
            if request_data:
                threat = await self._check_sql_injection(ip_address, request_data)
                if threat:
                    return threat
            
            # Check for other suspicious patterns
            threat = await self._check_suspicious_patterns(ip_address, user_id, request_data)
            if threat:
                return threat
            
            return None
            
        except Exception as e:
            logger.error(f"Threat analysis error: {e}")
            return None
    
    async def _check_rate_limit(self, ip_address: str, user_id: str = None) -> Optional[SecurityThreat]:
        """Check rate limiting violations"""
        try:
            current_time = time.time()
            rate_key = f"{ip_address}:{user_id}" if user_id else ip_address
            
            # Clean old entries
            self.rate_limits[rate_key] = deque([
                t for t in self.rate_limits[rate_key]
                if current_time - t < 60  # Last minute
            ], maxlen=self.config.rate_limit_requests_per_minute * 2)
            
            # Add current request
            self.rate_limits[rate_key].append(current_time)
            
            # Check if rate limit exceeded
            if len(self.rate_limits[rate_key]) > self.config.rate_limit_requests_per_minute:
                return SecurityThreat(
                    threat_id=secrets.token_urlsafe(16),
                    threat_type="rate_limit_exceeded",
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=ip_address,
                    user_id=user_id,
                    description=f"Rate limit exceeded: {len(self.rate_limits[rate_key])} requests per minute",
                    detected_at=datetime.now(timezone.utc),
                    indicators={"request_count": len(self.rate_limits[rate_key])}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return None
    
    async def _check_ip_reputation(self, ip_address: str) -> Optional[SecurityThreat]:
        """Check IP address reputation"""
        try:
            # Check if IP is in known malicious list
            malicious_ips = await self.redis_client.sismember("malicious_ips", ip_address)
            
            if malicious_ips:
                return SecurityThreat(
                    threat_id=secrets.token_urlsafe(16),
                    threat_type="malicious_ip",
                    threat_level=ThreatLevel.HIGH,
                    source_ip=ip_address,
                    user_id=None,
                    description=f"Request from known malicious IP: {ip_address}",
                    detected_at=datetime.now(timezone.utc),
                    indicators={"ip_reputation": "malicious"}
                )
            
            # Check IP reputation score
            reputation_score = self.ip_reputation.get(ip_address, 0.0)
            if reputation_score < -0.8:  # Highly suspicious
                return SecurityThreat(
                    threat_id=secrets.token_urlsafe(16),
                    threat_type="suspicious_ip",
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=ip_address,
                    user_id=None,
                    description=f"Request from suspicious IP: {ip_address} (score: {reputation_score})",
                    detected_at=datetime.now(timezone.utc),
                    indicators={"reputation_score": reputation_score}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"IP reputation check error: {e}")
            return None
    
    async def _check_sql_injection(
        self, 
        ip_address: str, 
        request_data: Dict[str, Any]
    ) -> Optional[SecurityThreat]:
        """Check for SQL injection patterns"""
        try:
            sql_pattern = re.compile(
                r"(union|select|insert|delete|drop|alter|exec|script|--|;|'|\"|%27|%22)",
                re.IGNORECASE
            )
            
            # Check all string values in request data
            for key, value in request_data.items():
                if isinstance(value, str) and sql_pattern.search(value):
                    return SecurityThreat(
                        threat_id=secrets.token_urlsafe(16),
                        threat_type="sql_injection",
                        threat_level=ThreatLevel.CRITICAL,
                        source_ip=ip_address,
                        user_id=None,
                        description=f"SQL injection attempt detected in field: {key}",
                        detected_at=datetime.now(timezone.utc),
                        indicators={"field": key, "value": value[:100]}
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"SQL injection check error: {e}")
            return None
    
    async def _check_suspicious_patterns(
        self,
        ip_address: str,
        user_id: str = None,
        request_data: Dict[str, Any] = None
    ) -> Optional[SecurityThreat]:
        """Check for other suspicious patterns"""
        try:
            # Check for unusual access patterns
            if user_id:
                # Get recent activity for user
                recent_activity = await self.redis_client.zrange(
                    f"user_activity:{user_id}", -10, -1, withscores=True
                )
                
                if len(recent_activity) > 0:
                    # Check for unusual timing patterns
                    timestamps = [score for _, score in recent_activity]
                    time_deltas = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                    
                    if time_deltas and all(delta < 1 for delta in time_deltas):  # Very rapid requests
                        return SecurityThreat(
                            threat_id=secrets.token_urlsafe(16),
                            threat_type="automated_behavior",
                            threat_level=ThreatLevel.MEDIUM,
                            source_ip=ip_address,
                            user_id=user_id,
                            description="Possible automated/bot behavior detected",
                            detected_at=datetime.now(timezone.utc),
                            indicators={"rapid_requests": True, "min_delta": min(time_deltas)}
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Suspicious pattern check error: {e}")
            return None
    
    async def mitigate_threat(self, threat: SecurityThreat) -> Dict[str, Any]:
        """Implement threat mitigation measures"""
        try:
            mitigation_actions = []
            
            if threat.threat_type == "rate_limit_exceeded":
                # Temporarily block IP
                await self.redis_client.setex(
                    f"blocked_ip:{threat.source_ip}",
                    300,  # 5 minutes
                    "rate_limit_exceeded"
                )
                mitigation_actions.append("ip_temporarily_blocked")
            
            elif threat.threat_type in ["sql_injection", "malicious_ip"]:
                # Block IP for longer period
                await self.redis_client.setex(
                    f"blocked_ip:{threat.source_ip}",
                    3600,  # 1 hour
                    threat.threat_type
                )
                mitigation_actions.append("ip_blocked_extended")
                
                # Add to malicious IP list
                await self.redis_client.sadd("malicious_ips", threat.source_ip)
                mitigation_actions.append("added_to_malicious_list")
            
            elif threat.threat_type == "brute_force":
                # Lock user account if applicable
                if threat.user_id:
                    await self.redis_client.setex(
                        f"locked_user:{threat.user_id}",
                        1800,  # 30 minutes
                        "brute_force_detected"
                    )
                    mitigation_actions.append("user_account_locked")
            
            # Mark threat as mitigated
            threat.mitigated = True
            self.active_threats[threat.threat_id] = threat
            
            # Store threat in Redis
            await self.redis_client.hset(
                "security_threats",
                threat.threat_id,
                json.dumps(asdict(threat), default=str)
            )
            
            logger.warning(f"Threat mitigated: {threat.threat_type} from {threat.source_ip}")
            
            return {
                "threat_id": threat.threat_id,
                "mitigation_actions": mitigation_actions,
                "status": "mitigated"
            }
            
        except Exception as e:
            logger.error(f"Threat mitigation error: {e}")
            return {"status": "failed", "error": str(e)}
