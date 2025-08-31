"""
 Advanced Security & Authentication System
============================================

Enterprise-grade security system with multi-factor authentication,
encryption, access control, and threat detection for content fingerprinting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import time
import json
import jwt
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import ipaddress
from pathlib import Path
import os

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import pyotp
    import qrcode
    from PIL import Image
    import bcrypt
    MFA_AVAILABLE = True
except ImportError:
    MFA_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .models import ContentType

logger = logging.getLogger(__name__)

class SecurityLevel(str, Enum):
    """Security levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class AuthenticationMethod(str, Enum):
    """Authentication methods."""
    PASSWORD = "password"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    MFA = "mfa"
    CERTIFICATE = "certificate"

class PermissionLevel(str, Enum):
    """Permission levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ThreatLevel(str, Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class User:
    """User model with security attributes."""
    id: str
    username: str
    email: str
    password_hash: str
    permissions: List[PermissionLevel] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SecurityEvent:
    """Security event for audit logging."""
    id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    severity: ThreatLevel
    details: Dict[str, Any]
    resolved: bool = False

@dataclass
class AccessToken:
    """Access token with metadata."""
    token: str
    user_id: str
    permissions: List[PermissionLevel]
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None

class EncryptionManager:
    """Advanced encryption and key management."""
    
    def __init__(self, master_key: Optional[str] = None):
        if not CRYPTO_AVAILABLE:
            raise ImportError("Cryptography library not available")
        
        self.master_key = master_key or os.getenv("MASTER_ENCRYPTION_KEY")
        if not self.master_key:
            # Generate new master key
            self.master_key = Fernet.generate_key().decode()
            logger.warning("Generated new master key - store securely!")
        
        self.fernet = Fernet(self.master_key.encode())
        
        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        logger.info("Encryption manager initialized")
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using symmetric encryption."""
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.fernet.encrypt(data)
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using symmetric encryption."""
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def encrypt_large_data(self, data: bytes) -> bytes:
        """Encrypt large data using asymmetric encryption."""
        # For large data, use hybrid encryption
        # Generate symmetric key for this data
        data_key = Fernet.generate_key()
        data_fernet = Fernet(data_key)
        
        # Encrypt data with symmetric key
        encrypted_data = data_fernet.encrypt(data)
        
        # Encrypt symmetric key with public key
        encrypted_key = self.public_key.encrypt(
            data_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine encrypted key and data
        return encrypted_key + b"::::" + encrypted_data
    
    def decrypt_large_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt large data using asymmetric encryption."""
        # Split encrypted key and data
        encrypted_key, encrypted_content = encrypted_data.split(b"::::", 1)
        
        # Decrypt symmetric key with private key
        data_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data with symmetric key
        data_fernet = Fernet(data_key)
        return data_fernet.decrypt(encrypted_content)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        if not MFA_AVAILABLE:
            # Fallback to hashlib
            salt = secrets.token_hex(16)
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ":" + salt
        
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        if not MFA_AVAILABLE:
            # Fallback verification
            if ":" in password_hash:
                hash_part, salt = password_hash.split(":", 1)
                computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
                return hash_part == computed_hash
            return False
        
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except:
            return False
    
    def generate_api_key(self) -> str:
        """Generate secure API key."""



        return secrets.token_urlsafe(32)
    
    def generate_session_token(self) -> str:
        """Generate secure session token."""



        return secrets.token_urlsafe(64)

class MFAManager:
    """Multi-Factor Authentication manager."""
    
    def __init__(self):
        if not MFA_AVAILABLE:
            logger.warning("MFA libraries not available - MFA disabled")
            self.available = False
            return
        
        self.available = True
        logger.info("MFA manager initialized")
    
    def generate_secret(self) -> str:
        """Generate TOTP secret for user."""
        if not self.available:
            return ""
        
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret: str, service_name: str = "FingerPrint Pro") -> bytes:
        """Generate QR code for TOTP setup."""
        if not self.available:
            return b""
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=service_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        import io
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        if not self.available:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""



        return [secrets.token_hex(4) for _ in range(count)]

class JWTManager:
    """JWT token management."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.default_expiry = timedelta(hours=24)
        
        logger.info("JWT manager initialized")
    
    def create_token(self, user_id: str, permissions: List[PermissionLevel], 
                    expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token."""
        
        expires_delta = expires_delta or self.default_expiry
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user_id,
            "permissions": [p.value for p in permissions],
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "fingerprint-api"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""



        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if valid and not expired."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # Create new token with same permissions
        return self.create_token(
            user_id=payload["sub"],
            permissions=[PermissionLevel(p) for p in payload["permissions"]]
        )

class AccessControlManager:
    """Role-based access control."""
    
    def __init__(self):
        # Define permission hierarchy
        self.permission_hierarchy = {
            PermissionLevel.READ: [],
            PermissionLevel.WRITE: [PermissionLevel.READ],
            PermissionLevel.ADMIN: [PermissionLevel.READ, PermissionLevel.WRITE],
            PermissionLevel.SUPER_ADMIN: [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN]
        }
        
        # Define resource permissions
        self.resource_permissions = {
            "fingerprint:create": [PermissionLevel.WRITE, PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN],
            "fingerprint:read": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN],
            "fingerprint:update": [PermissionLevel.WRITE, PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN],
            "fingerprint:delete": [PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN],
            "system:monitor": [PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN],
            "system:configure": [PermissionLevel.SUPER_ADMIN],
            "user:manage": [PermissionLevel.SUPER_ADMIN]
        }
        
        logger.info("Access control manager initialized")
    
    def check_permission(self, user_permissions: List[PermissionLevel], 
                        required_permission: str) -> bool:
        """Check if user has required permission for resource."""
        
        if required_permission not in self.resource_permissions:
            logger.warning(f"Unknown permission: {required_permission}")
            return False
        
        required_levels = self.resource_permissions[required_permission]
        
        # Check if user has any of the required permission levels
        for user_perm in user_permissions:
            if user_perm in required_levels:
                return True
            
            # Check inherited permissions
            inherited = self.permission_hierarchy.get(user_perm, [])
            if any(perm in required_levels for perm in inherited):
                return True
        
        return False
    
    def get_user_permissions(self, user: User) -> List[PermissionLevel]:
        """Get effective permissions for user."""
        permissions = set(user.permissions)
        
        # Add inherited permissions
        for perm in user.permissions:
            inherited = self.permission_hierarchy.get(perm, [])
            permissions.update(inherited)
        
        return list(permissions)

class ThreatDetectionSystem:
    """Advanced threat detection and response."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        
        # Rate limiting configuration
        self.rate_limits = {
            "login_attempts": {"limit": 5, "window": 300},  # 5 attempts per 5 minutes
            "api_requests": {"limit": 1000, "window": 3600},  # 1000 requests per hour
            "fingerprint_requests": {"limit": 100, "window": 60}  # 100 per minute
        }
        
        # Suspicious patterns
        self.suspicious_patterns = {
            "brute_force": re.compile(r"(admin|root|password|123456)"),
            "sql_injection": re.compile(r"(union|select|drop|insert|update|delete).*--", re.IGNORECASE),
            "xss_attempt": re.compile(r"<script|javascript:|onload=", re.IGNORECASE),
            "path_traversal": re.compile(r"\.\./|\.\.\\"),
        }
        
        # IP reputation tracking
        self.blocked_ips = set()
        self.suspicious_ips = {}
        
        logger.info("Threat detection system initialized")
    
    def check_rate_limit(self, identifier: str, action: str) -> bool:
        """Check if request exceeds rate limit."""
        if not self.redis_client:
            return True  # No rate limiting without Redis
        
        if action not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[action]
        key = f"rate_limit:{action}:{identifier}"
        
        try:
            current = self.redis_client.get(key)
            if current is None:
                # First request
                self.redis_client.setex(key, limit_config["window"], 1)
                return True
            
            count = int(current)
            if count >= limit_config["limit"]:
                logger.warning(f"Rate limit exceeded for {identifier} on {action}")
                return False
            
            # Increment counter
            self.redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Fail open
    
    def detect_suspicious_activity(self, request_data: Dict[str, Any]) -> Tuple[bool, ThreatLevel, str]:
        """Detect suspicious activity in request."""
        
        ip_address = request_data.get("ip_address", "")
        user_agent = request_data.get("user_agent", "")
        request_path = request_data.get("path", "")
        request_body = request_data.get("body", "")
        
        threats = []
        
        # Check blocked IPs
        if ip_address in self.blocked_ips:
            return True, ThreatLevel.HIGH, "Blocked IP address"
        
        # Check suspicious patterns
        combined_text = f"{request_path} {request_body} {user_agent}"
        
        for pattern_name, pattern in self.suspicious_patterns.items():
            if pattern.search(combined_text):
                threats.append(f"Suspicious pattern: {pattern_name}")
        
        # Check for suspicious IP behavior
        if ip_address in self.suspicious_ips:
            score = self.suspicious_ips[ip_address]
            if score > 50:
                threats.append("High suspicious IP score")
        
        # Check for unusual user agent
        if self._is_suspicious_user_agent(user_agent):
            threats.append("Suspicious user agent")
        
        # Check for geographic anomalies (simplified)
        if self._is_suspicious_location(ip_address):
            threats.append("Suspicious geographic location")
        
        if threats:
            severity = self._calculate_threat_severity(threats)
            return True, severity, "; ".join(threats)
        
        return False, ThreatLevel.LOW, "No threats detected"
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious."""
        suspicious_agents = [
            "curl", "wget", "python-requests", "bot", "crawler", 
            "scanner", "sqlmap", "nikto"
        ]
        
        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)
    
    def _is_suspicious_location(self, ip_address: str) -> bool:
        """Check if IP location is suspicious (simplified)."""



        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for private/local IPs
            if ip.is_private or ip.is_loopback:
                return False
            
            # Add more sophisticated geolocation checks here
            # For now, just basic checks
            
        except ValueError:
            return True  # Invalid IP is suspicious
        
        return False
    
    def _calculate_threat_severity(self, threats: List[str]) -> ThreatLevel:
        """Calculate overall threat severity."""
        if len(threats) >= 3:
            return ThreatLevel.CRITICAL
        elif len(threats) == 2:
            return ThreatLevel.HIGH
        elif len(threats) == 1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def add_suspicious_ip(self, ip_address: str, score_increment: int = 10):
        """Add IP to suspicious list."""
        if ip_address in self.suspicious_ips:
            self.suspicious_ips[ip_address] += score_increment
        else:
            self.suspicious_ips[ip_address] = score_increment
        
        # Block IP if score is too high
        if self.suspicious_ips[ip_address] > 100:
            self.blocked_ips.add(ip_address)
            logger.warning(f"Blocked IP due to high suspicious score: {ip_address}")
    
    def block_ip(self, ip_address: str, reason: str):
        """Manually block IP address."""
        self.blocked_ips.add(ip_address)
        logger.warning(f"Manually blocked IP {ip_address}: {reason}")

class SecurityAuditLogger:
    """Security event audit logging."""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup dedicated security logger
        self.security_logger = logging.getLogger("security_audit")
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.security_logger.addHandler(handler)
        self.security_logger.setLevel(logging.INFO)
        
        logger.info(f"Security audit logger initialized: {self.log_file}")
    
    def log_event(self, event: SecurityEvent):
        """Log security event."""
        
        event_data = {
            "id": event.id,
            "type": event.event_type,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "timestamp": event.timestamp.isoformat(),
            "severity": event.severity.value,
            "details": event.details,
            "resolved": event.resolved
        }
        
        log_level = {
            ThreatLevel.LOW: logging.INFO,
            ThreatLevel.MEDIUM: logging.WARNING,
            ThreatLevel.HIGH: logging.ERROR,
            ThreatLevel.CRITICAL: logging.CRITICAL
        }.get(event.severity, logging.INFO)
        
        self.security_logger.log(
            log_level,
            f"Security Event: {json.dumps(event_data)}"
        )
    
    def log_authentication(self, user_id: str, success: bool, ip_address: str, 
                          user_agent: str, method: AuthenticationMethod):
        """Log authentication attempt."""
        
        event = SecurityEvent(
            id=secrets.token_hex(8),
            event_type="authentication",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            severity=ThreatLevel.LOW if success else ThreatLevel.MEDIUM,
            details={
                "success": success,
                "method": method.value
            }
        )
        
        self.log_event(event)
    
    def log_access_attempt(self, user_id: str, resource: str, success: bool, 
                          ip_address: str, user_agent: str):
        """Log resource access attempt."""
        
        event = SecurityEvent(
            id=secrets.token_hex(8),
            event_type="access_attempt",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            severity=ThreatLevel.LOW if success else ThreatLevel.MEDIUM,
            details={
                "resource": resource,
                "success": success
            }
        )
        
        self.log_event(event)
    
    def log_threat_detection(self, threat_level: ThreatLevel, description: str, 
                           ip_address: str, user_agent: str, details: Dict[str, Any]):
        """Log threat detection."""
        
        event = SecurityEvent(
            id=secrets.token_hex(8),
            event_type="threat_detection",
            user_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            severity=threat_level,
            details={
                "description": description,
                **details
            }
        )
        
        self.log_event(event)

class SecurityManager:
    """
    Master security management system.
    
    Features:
    - Multi-factor authentication (TOTP, backup codes)
    - Advanced encryption and key management
    - JWT token management with refresh capabilities
    - Role-based access control (RBAC)
    - Real-time threat detection and blocking
    - Rate limiting and DDoS protection
    - Comprehensive security audit logging
    - IP reputation and geolocation analysis
    - Session management and security
    """
    
    def __init__(self, 
                 master_key: Optional[str] = None,
                 jwt_secret: Optional[str] = None,
                 redis_client=None):
        
        # Initialize security components
        self.encryption_manager = EncryptionManager(master_key)
        self.mfa_manager = MFAManager()
        self.jwt_manager = JWTManager(jwt_secret or secrets.token_urlsafe(64))
        self.access_control = AccessControlManager()
        self.threat_detection = ThreatDetectionSystem(redis_client)
        self.audit_logger = SecurityAuditLogger()
        
        # User and session storage
        self.users = {}  # In production, use proper database
        self.active_sessions = {}
        self.blocked_tokens = set()
        
        logger.info("Security manager initialized with all subsystems")
    
    async def authenticate_user(self, username: str, password: str, 
                               ip_address: str, user_agent: str,
                               totp_token: Optional[str] = None) -> Optional[AccessToken]:
        """Authenticate user with optional MFA."""
        
        # Check rate limiting
        if not self.threat_detection.check_rate_limit(ip_address, "login_attempts"):
            self.audit_logger.log_authentication(
                username, False, ip_address, user_agent, AuthenticationMethod.PASSWORD
            )
            return None
        
        # Find user
        user = self.users.get(username)
        if not user:
            self.audit_logger.log_authentication(
                username, False, ip_address, user_agent, AuthenticationMethod.PASSWORD
            )
            return None
        
        # Check if account is locked
        if user.account_locked:
            self.audit_logger.log_authentication(
                username, False, ip_address, user_agent, AuthenticationMethod.PASSWORD
            )
            return None
        
        # Verify password
        if not self.encryption_manager.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account after too many failures
            if user.failed_login_attempts >= 5:
                user.account_locked = True
                logger.warning(f"Account locked for user: {username}")
            
            self.audit_logger.log_authentication(
                username, False, ip_address, user_agent, AuthenticationMethod.PASSWORD
            )
            return None
        
        # Check MFA if enabled
        if user.mfa_enabled:
            if not totp_token:
                # MFA required but not provided
                return None
            
            if not self.mfa_manager.verify_totp(user.mfa_secret, totp_token):
                self.audit_logger.log_authentication(
                    username, False, ip_address, user_agent, AuthenticationMethod.MFA
                )
                return None
        
        # Successful authentication
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        
        # Create access token
        token = self.jwt_manager.create_token(user.id, user.permissions)
        access_token = AccessToken(
            token=token,
            user_id=user.id,
            permissions=user.permissions,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        # Store session
        self.active_sessions[token] = access_token
        
        self.audit_logger.log_authentication(
            user.id, True, ip_address, user_agent, 
            AuthenticationMethod.MFA if user.mfa_enabled else AuthenticationMethod.PASSWORD
        )
        
        return access_token
    
    async def verify_access_token(self, token: str) -> Optional[AccessToken]:
        """Verify and return access token if valid."""
        
        # Check if token is blocked
        if token in self.blocked_tokens:
            return None
        
        # Check active sessions
        if token not in self.active_sessions:
            return None
        
        access_token = self.active_sessions[token]
        
        # Check expiration
        if datetime.utcnow() > access_token.expires_at:
            del self.active_sessions[token]
            return None
        
        # Verify JWT
        payload = self.jwt_manager.verify_token(token)
        if not payload:
            del self.active_sessions[token]
            return None
        
        # Update last used
        access_token.last_used = datetime.utcnow()
        
        return access_token
    
    async def check_permissions(self, token: str, resource: str, 
                               ip_address: str, user_agent: str) -> bool:
        """Check if user has permissions for resource."""
        
        access_token = await self.verify_access_token(token)
        if not access_token:
            return False
        
        # Check permissions
        has_permission = self.access_control.check_permission(
            access_token.permissions, 
            resource
        )
        
        # Log access attempt
        self.audit_logger.log_access_attempt(
            access_token.user_id, resource, has_permission, ip_address, user_agent
        )
        
        return has_permission
    
    async def enable_mfa(self, user_id: str) -> Tuple[str, bytes]:
        """Enable MFA for user and return secret and QR code."""
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Generate MFA secret
        secret = self.mfa_manager.generate_secret()
        qr_code = self.mfa_manager.generate_qr_code(user.email, secret)
        
        # Save secret (but don't enable until verified)
        user.mfa_secret = secret
        
        return secret, qr_code
    
    async def verify_mfa_setup(self, user_id: str, totp_token: str) -> bool:
        """Verify MFA setup and enable it."""
        
        user = self.users.get(user_id)
        if not user or not user.mfa_secret:
            return False
        
        if self.mfa_manager.verify_totp(user.mfa_secret, totp_token):
            user.mfa_enabled = True
            logger.info(f"MFA enabled for user: {user_id}")
            return True
        
        return False
    
    async def analyze_security_threat(self, request_data: Dict[str, Any]) -> SecurityEvent:
        """Analyze request for security threats."""
        
        is_threat, threat_level, description = self.threat_detection.detect_suspicious_activity(request_data)
        
        if is_threat:
            # Log threat
            self.audit_logger.log_threat_detection(
                threat_level, description,
                request_data.get("ip_address", ""),
                request_data.get("user_agent", ""),
                request_data
            )
            
            # Take action based on threat level
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                ip_address = request_data.get("ip_address")
                if ip_address:
                    self.threat_detection.add_suspicious_ip(ip_address, 50)
        
        return SecurityEvent(
            id=secrets.token_hex(8),
            event_type="threat_analysis",
            user_id=request_data.get("user_id"),
            ip_address=request_data.get("ip_address", ""),
            user_agent=request_data.get("user_agent", ""),
            timestamp=datetime.utcnow(),
            severity=threat_level,
            details={"description": description, "is_threat": is_threat}
        )
    
    def create_user(self, username: str, email: str, password: str, 
                   permissions: List[PermissionLevel] = None) -> User:
        """Create new user account."""
        
        if username in self.users:
            raise ValueError("Username already exists")
        
        permissions = permissions or [PermissionLevel.READ]
        
        user = User(
            id=secrets.token_hex(16),
            username=username,
            email=email,
            password_hash=self.encryption_manager.hash_password(password),
            permissions=permissions
        )
        
        self.users[username] = user
        logger.info(f"Created user: {username}")
        
        return user
    
    def revoke_token(self, token: str):
        """Revoke access token."""
        self.blocked_tokens.add(token)
        if token in self.active_sessions:
            del self.active_sessions[token]
        
        logger.info("Access token revoked")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security system summary."""



        
        return {
            "users": {
                "total": len(self.users),
                "mfa_enabled": sum(1 for u in self.users.values() if u.mfa_enabled),
                "locked_accounts": sum(1 for u in self.users.values() if u.account_locked)
            },
            "sessions": {
                "active": len(self.active_sessions),
                "blocked_tokens": len(self.blocked_tokens)
            },
            "threats": {
                "blocked_ips": len(self.threat_detection.blocked_ips),
                "suspicious_ips": len(self.threat_detection.suspicious_ips)
            },
            "system": {
                "encryption_enabled": True,
                "mfa_available": self.mfa_manager.available,
                "threat_detection_enabled": True
            }
        }

# Export main classes
__all__ = [
    'SecurityManager', 'EncryptionManager', 'MFAManager', 'JWTManager',
    'AccessControlManager', 'ThreatDetectionSystem', 'SecurityAuditLogger',
    'User', 'SecurityEvent', 'AccessToken',
    'SecurityLevel', 'AuthenticationMethod', 'PermissionLevel', 'ThreatLevel'
]
