"""
🎯 Security Microservice
Authentication, authorization, and security service with multi-factor auth, encryption, and threat protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import secrets
import time
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
import re
import ipaddress
from collections import defaultdict, deque
import jwt
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuthenticationMethod(str, Enum):
    """Authentication methods"""
    PASSWORD = "password"
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    SAML = "saml"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"


class AuthorizationLevel(str, Enum):
    """Authorization levels"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SecurityThreatType(str, Enum):
    """Security threat types"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    MALWARE = "malware"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    FERNET = "fernet"


@dataclass
class User:
    """User entity"""
    id: str
    username: str
    email: str
    password_hash: str
    salt: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_locked(self) -> bool:
        """Check if user is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
        
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': self.roles,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'mfa_enabled': self.mfa_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'password_hash': self.password_hash,
                'salt': self.salt,
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'mfa_secret': self.mfa_secret
            })
            
        return data


@dataclass
class Session:
    """User session"""
    id: str
    user_id: str
    token: str
    refresh_token: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
        
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return self.is_active and not self.is_expired()


@dataclass
class SecurityEvent:
    """Security event"""
    id: str
    event_type: SecurityThreatType
    severity: str  # low, medium, high, critical
    description: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'severity': self.severity,
            'description': self.description,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'resolved': self.resolved
        }


class PasswordManager:
    """Password hashing and validation"""
    
    @staticmethod
    def generate_salt() -> str:
        """Generate random salt"""
        return secrets.token_hex(32)
        
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac('sha256', 
                                 password.encode('utf-8'), 
                                 salt.encode('utf-8'), 
                                 100000).hex()
        
    @staticmethod
    def verify_password(password: str, salt: str, password_hash: str) -> bool:
        """Verify password"""
        computed_hash = PasswordManager.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, password_hash)
        
    @staticmethod
    def check_password_strength(password: str) -> Tuple[bool, List[str]]:
        """Check password strength"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
            
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
            
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
            
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
            
        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'abc123']
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Password contains common patterns")
            
        return len(issues) == 0, issues


class TokenManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def generate_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token"""
        payload_copy = payload.copy()
        payload_copy['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload_copy['iat'] = datetime.utcnow()
        payload_copy['jti'] = secrets.token_hex(16)  # JWT ID
        
        return jwt.encode(payload_copy, self.secret_key, algorithm=self.algorithm)
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
            
    def refresh_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """Refresh JWT token"""
        payload = self.verify_token(refresh_token)
        if not payload:
            return None
            
        # Generate new tokens
        new_payload = {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'roles': payload.get('roles', [])
        }
        
        new_token = self.generate_token(new_payload)
        new_refresh_token = self.generate_token(new_payload, expires_in=7*24*3600)  # 7 days
        
        return new_token, new_refresh_token


class MFAManager:
    """Multi-Factor Authentication manager"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate MFA secret"""
        return base64.b32encode(secrets.token_bytes(32)).decode('utf-8')
        
    @staticmethod
    def generate_totp_code(secret: str, timestamp: int = None) -> str:
        """Generate TOTP code"""
        import hmac
        import struct
        
        if timestamp is None:
            timestamp = int(time.time())
            
        # 30-second time step
        time_step = timestamp // 30
        
        # Convert to bytes
        secret_bytes = base64.b32decode(secret.encode('utf-8'))
        time_bytes = struct.pack('>Q', time_step)
        
        # Generate HMAC
        hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
        
        # Extract 4-byte dynamic binary code
        offset = hmac_hash[-1] & 0x0f
        binary_code = struct.unpack('>I', hmac_hash[offset:offset+4])[0] & 0x7fffffff
        
        # Generate 6-digit code
        return str(binary_code % 1000000).zfill(6)
        
    @staticmethod
    def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code with time window"""
        timestamp = int(time.time())
        
        # Check current time and nearby time windows
        for i in range(-window, window + 1):
            test_timestamp = timestamp + (i * 30)
            expected_code = MFAManager.generate_totp_code(secret, test_timestamp)
            if secrets.compare_digest(code, expected_code):
                return True
                
        return False


class RateLimiter:
    """Rate limiting for security"""
    
    def __init__(self):
        self.attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._lock = threading.RLock()
        
    def is_allowed(self, identifier: str, max_attempts: int, window_seconds: int) -> bool:
        """Check if action is allowed based on rate limit"""
        with self._lock:
            now = time.time()
            
            # Clean old attempts
            self.attempts[identifier] = deque(
                [timestamp for timestamp in self.attempts[identifier] 
                 if now - timestamp < window_seconds],
                maxlen=100
            )
            
            # Check limit
            if len(self.attempts[identifier]) >= max_attempts:
                return False
                
            # Record attempt
            self.attempts[identifier].append(now)
            return True
            
    def get_remaining_attempts(self, identifier: str, max_attempts: int, window_seconds: int) -> int:
        """Get remaining attempts"""
        with self._lock:
            now = time.time()
            
            # Clean old attempts
            self.attempts[identifier] = deque(
                [timestamp for timestamp in self.attempts[identifier] 
                 if now - timestamp < window_seconds],
                maxlen=100
            )
            
            return max(0, max_attempts - len(self.attempts[identifier]))


class IPWhitelist:
    """IP address whitelist/blacklist management"""
    
    def __init__(self):
        self.whitelist: List[ipaddress.IPv4Network] = []
        self.blacklist: List[ipaddress.IPv4Network] = []
        self._lock = threading.RLock()
        
    def add_to_whitelist(self, ip_range: str):
        """Add IP range to whitelist"""
        with self._lock:
            try:
                network = ipaddress.IPv4Network(ip_range, strict=False)
                self.whitelist.append(network)
            except ValueError as e:
                logger.error(f"Invalid IP range {ip_range}: {str(e)}")
                
    def add_to_blacklist(self, ip_range: str):
        """Add IP range to blacklist"""
        with self._lock:
            try:
                network = ipaddress.IPv4Network(ip_range, strict=False)
                self.blacklist.append(network)
            except ValueError as e:
                logger.error(f"Invalid IP range {ip_range}: {str(e)}")
                
    def is_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        with self._lock:
            try:
                ip = ipaddress.IPv4Address(ip_address)
                
                # Check blacklist first
                for network in self.blacklist:
                    if ip in network:
                        return False
                        
                # If whitelist is empty, allow all (except blacklisted)
                if not self.whitelist:
                    return True
                    
                # Check whitelist
                for network in self.whitelist:
                    if ip in network:
                        return True
                        
                return False
                
            except ValueError:
                logger.error(f"Invalid IP address: {ip_address}")
                return False


class ThreatDetector:
    """Security threat detection"""
    
    def __init__(self):
        self.patterns = {
            SecurityThreatType.SQL_INJECTION: [
                r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table)",
                r"(?i)('.*or.*'|'.*and.*'|'.*=.*')",
                r"(?i)(exec|execute|sp_|xp_)"
            ],
            SecurityThreatType.XSS: [
                r"(?i)(<script|</script>|javascript:|vbscript:)",
                r"(?i)(on\w+\s*=|src\s*=.*javascript)",
                r"(?i)(alert\(|confirm\(|prompt\()"
            ],
            SecurityThreatType.SUSPICIOUS_ACTIVITY: [
                r"(?i)(\.\.\/|\.\.\\|\/etc\/passwd|\/proc\/)",
                r"(?i)(cmd\.exe|powershell|bash|sh\s)",
                r"(?i)(wget|curl|nc\s|netcat)"
            ]
        }
        
    def detect_threats(self, data: str, ip_address: str = None, 
                      user_agent: str = None) -> List[SecurityThreatType]:
        """Detect security threats in data"""
        threats = []
        
        for threat_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, data):
                    threats.append(threat_type)
                    break
                    
        return threats
        
    def analyze_request(self, url: str, headers: Dict[str, str], 
                       body: str = None) -> List[SecurityThreatType]:
        """Analyze HTTP request for threats"""
        threats = []
        
        # Check URL
        threats.extend(self.detect_threats(url))
        
        # Check headers
        for header_value in headers.values():
            threats.extend(self.detect_threats(header_value))
            
        # Check body
        if body:
            threats.extend(self.detect_threats(body))
            
        return list(set(threats))  # Remove duplicates


class EncryptionManager:
    """Data encryption and decryption"""
    
    def __init__(self, key: str = None):
        self.key = key or self._generate_key()
        
    def _generate_key(self) -> str:
        """Generate encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        
    def encrypt(self, data: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> str:
        """Encrypt data"""
        try:
            if algorithm == EncryptionAlgorithm.FERNET:
                from cryptography.fernet import Fernet
                # Generate key from our key
                key_bytes = base64.urlsafe_b64encode(self.key.encode()[:32].ljust(32, b'0'))
                f = Fernet(key_bytes)
                encrypted = f.encrypt(data.encode('utf-8'))
                return base64.b64encode(encrypted).decode('utf-8')
            else:
                # Fallback to base64 encoding
                return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        except ImportError:
            logger.warning("cryptography library not available, using base64 encoding")
            return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return data
            
    def decrypt(self, encrypted_data: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> str:
        """Decrypt data"""
        try:
            if algorithm == EncryptionAlgorithm.FERNET:
                from cryptography.fernet import Fernet
                # Generate key from our key
                key_bytes = base64.urlsafe_b64encode(self.key.encode()[:32].ljust(32, b'0'))
                f = Fernet(key_bytes)
                decoded = base64.b64decode(encrypted_data.encode('utf-8'))
                decrypted = f.decrypt(decoded)
                return decrypted.decode('utf-8')
            else:
                # Fallback to base64 decoding
                return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
        except ImportError:
            logger.warning("cryptography library not available, using base64 decoding")
            return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_data


class SecurityService:
    """Authentication, Authorization, and Security Service"""
    
    def __init__(self, name: str = "security_service"):
        self.name = name
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.security_events: List[SecurityEvent] = []
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager(secrets.token_hex(32))
        self.mfa_manager = MFAManager()
        self.rate_limiter = RateLimiter()
        self.ip_whitelist = IPWhitelist()
        self.threat_detector = ThreatDetector()
        self.encryption_manager = EncryptionManager()
        self.running = False
        self.cleanup_task = None
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour
        
    async def start(self):
        """Start security service"""
        self.running = True
        
        # Start cleanup task for expired sessions
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        
        logger.info(f"Started security service: {self.name}")
        
    async def stop(self):
        """Stop security service"""
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
        logger.info(f"Stopped security service: {self.name}")
        
    async def register_user(self, username: str, email: str, password: str, 
                          roles: List[str] = None) -> Optional[User]:
        """Register new user"""
        try:
            # Check password strength
            is_strong, issues = self.password_manager.check_password_strength(password)
            if not is_strong:
                logger.warning(f"Weak password for user {username}: {issues}")
                return None
                
            # Check if user exists
            if any(u.username == username or u.email == email for u in self.users.values()):
                logger.warning(f"User {username} or email {email} already exists")
                return None
                
            # Create user
            user_id = secrets.token_hex(16)
            salt = self.password_manager.generate_salt()
            password_hash = self.password_manager.hash_password(password, salt)
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                salt=salt,
                roles=roles or ['user']
            )
            
            self.users[user_id] = user
            
            # Log security event
            await self._log_security_event(
                SecurityThreatType.SUSPICIOUS_ACTIVITY,
                "low",
                f"New user registered: {username}",
                user_id=user_id
            )
            
            logger.info(f"Registered new user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return None
            
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = None, user_agent: str = None,
                              mfa_code: str = None) -> Optional[Session]:
        """Authenticate user"""
        try:
            # Rate limiting
            if not self.rate_limiter.is_allowed(f"login_{username}", self.max_failed_attempts, 300):
                logger.warning(f"Rate limit exceeded for user {username}")
                return None
                
            # IP whitelist check
            if ip_address and not self.ip_whitelist.is_allowed(ip_address):
                await self._log_security_event(
                    SecurityThreatType.UNAUTHORIZED_ACCESS,
                    "high",
                    f"Login attempt from blacklisted IP: {ip_address}",
                    ip_address=ip_address
                )
                return None
                
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
                    
            if not user:
                logger.warning(f"User not found: {username}")
                return None
                
            # Check if user is locked
            if user.is_locked():
                logger.warning(f"User {username} is locked")
                return None
                
            # Verify password
            if not self.password_manager.verify_password(password, user.salt, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock user if too many failed attempts
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
                    await self._log_security_event(
                        SecurityThreatType.BRUTE_FORCE,
                        "high",
                        f"User {username} locked due to failed login attempts",
                        user_id=user.id,
                        ip_address=ip_address
                    )
                    
                logger.warning(f"Invalid password for user {username}")
                return None
                
            # MFA verification
            if user.mfa_enabled:
                if not mfa_code:
                    logger.warning(f"MFA code required for user {username}")
                    return None
                    
                if not self.mfa_manager.verify_totp_code(user.mfa_secret, mfa_code):
                    logger.warning(f"Invalid MFA code for user {username}")
                    return None
                    
            # Reset failed attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Create session
            session = Session(
                id=secrets.token_hex(16),
                user_id=user.id,
                token=self.token_manager.generate_token({
                    'user_id': user.id,
                    'username': user.username,
                    'roles': user.roles
                }),
                refresh_token=self.token_manager.generate_token({
                    'user_id': user.id,
                    'username': user.username,
                    'roles': user.roles
                }, expires_in=7*24*3600),  # 7 days
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=self.session_timeout),
                last_accessed=datetime.utcnow(),
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown"
            )
            
            self.sessions[session.id] = session
            
            logger.info(f"User {username} authenticated successfully")
            return session
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
            
    async def validate_session(self, token: str) -> Optional[User]:
        """Validate session token"""
        try:
            # Verify JWT token
            payload = self.token_manager.verify_token(token)
            if not payload:
                return None
                
            user_id = payload.get('user_id')
            if not user_id or user_id not in self.users:
                return None
                
            # Find active session with this token
            session = None
            for s in self.sessions.values():
                if s.token == token and s.user_id == user_id:
                    session = s
                    break
                    
            if not session or not session.is_valid():
                return None
                
            # Update last accessed time
            session.last_accessed = datetime.utcnow()
            
            return self.users[user_id]
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return None
            
    async def logout_user(self, token: str) -> bool:
        """Logout user"""
        try:
            # Find and invalidate session
            for session in self.sessions.values():
                if session.token == token:
                    session.is_active = False
                    logger.info(f"User {session.user_id} logged out")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error logging out user: {str(e)}")
            return False
            
    async def enable_mfa(self, user_id: str) -> Optional[str]:
        """Enable MFA for user"""
        try:
            if user_id not in self.users:
                return None
                
            user = self.users[user_id]
            user.mfa_secret = self.mfa_manager.generate_secret()
            user.mfa_enabled = True
            
            logger.info(f"MFA enabled for user {user.username}")
            return user.mfa_secret
            
        except Exception as e:
            logger.error(f"Error enabling MFA: {str(e)}")
            return None
            
    async def analyze_request_security(self, url: str, headers: Dict[str, str], 
                                     body: str = None, ip_address: str = None) -> List[SecurityThreatType]:
        """Analyze request for security threats"""
        try:
            threats = self.threat_detector.analyze_request(url, headers, body)
            
            if threats:
                await self._log_security_event(
                    threats[0],  # Log first threat type
                    "medium",
                    f"Security threats detected in request: {', '.join([t.value for t in threats])}",
                    ip_address=ip_address,
                    metadata={
                        'url': url,
                        'threats': [t.value for t in threats]
                    }
                )
                
            return threats
            
        except Exception as e:
            logger.error(f"Error analyzing request security: {str(e)}")
            return []
            
    async def encrypt_data(self, data: str, 
                          algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> str:
        """Encrypt sensitive data"""
        return self.encryption_manager.encrypt(data, algorithm)
        
    async def decrypt_data(self, encrypted_data: str, 
                          algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> str:
        """Decrypt sensitive data"""
        return self.encryption_manager.decrypt(encrypted_data, algorithm)
        
    async def _log_security_event(self, event_type: SecurityThreatType, severity: str,
                                 description: str, user_id: str = None, 
                                 ip_address: str = None, user_agent: str = None,
                                 metadata: Dict[str, Any] = None):
        """Log security event"""
        event = SecurityEvent(
            id=secrets.token_hex(16),
            event_type=event_type,
            severity=severity,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        self.security_events.append(event)
        
        # Keep only recent events (last 10000)
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
            
        logger.warning(f"Security event: {event.description}")
        
    async def _cleanup_expired_sessions(self):
        """Cleanup expired sessions"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                expired_sessions = [
                    session_id for session_id, session in self.sessions.items()
                    if session.is_expired()
                ]
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                    
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {str(e)}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get security service status"""
        active_sessions = sum(1 for s in self.sessions.values() if s.is_valid())
        recent_events = sum(1 for e in self.security_events 
                          if (datetime.utcnow() - e.timestamp).total_seconds() < 3600)
        
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "users_count": len(self.users),
            "active_sessions": active_sessions,
            "total_sessions": len(self.sessions),
            "recent_security_events": recent_events,
            "total_security_events": len(self.security_events),
            "max_failed_attempts": self.max_failed_attempts,
            "lockout_duration": self.lockout_duration,
            "session_timeout": self.session_timeout,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events"""
        recent_events = sorted(self.security_events, key=lambda x: x.timestamp, reverse=True)
        return [event.to_dict() for event in recent_events[:limit]]


def create_security_service(config: Dict[str, Any] = None) -> SecurityService:
    """Factory function to create Security service"""
    config = config or {}
    service_name = config.get('name', 'security_service')
    
    service = SecurityService(service_name)
    
    # Configure security settings
    if 'max_failed_attempts' in config:
        service.max_failed_attempts = config['max_failed_attempts']
        
    if 'lockout_duration' in config:
        service.lockout_duration = config['lockout_duration']
        
    if 'session_timeout' in config:
        service.session_timeout = config['session_timeout']
        
    # Configure JWT secret
    if 'jwt_secret' in config:
        service.token_manager = TokenManager(config['jwt_secret'])
        
    # Configure encryption key
    if 'encryption_key' in config:
        service.encryption_manager = EncryptionManager(config['encryption_key'])
        
    # Configure IP whitelist
    if 'ip_whitelist' in config:
        for ip_range in config['ip_whitelist']:
            service.ip_whitelist.add_to_whitelist(ip_range)
            
    # Configure IP blacklist
    if 'ip_blacklist' in config:
        for ip_range in config['ip_blacklist']:
            service.ip_whitelist.add_to_blacklist(ip_range)
            
    return service


__all__ = [
    'SecurityService', 'User', 'Session', 'SecurityEvent',
    'AuthenticationMethod', 'AuthorizationLevel', 'SecurityThreatType', 'EncryptionAlgorithm',
    'PasswordManager', 'TokenManager', 'MFAManager', 'ThreatDetector', 'EncryptionManager',
    'create_security_service'
]