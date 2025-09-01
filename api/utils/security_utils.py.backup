"""Security Utilities for IA Influencer Agent Platform
Advanced security features including threat detection, access control, and audit logging

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
import hashlib
import hmac
import secrets
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64
import time
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
import sqlite3
import threading
import uuid
import ipaddress
import re
from functools import wraps
import asyncio
from collections import defaultdict
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)


class SecurityLevel(str):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str):
    """Threat type enumeration"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALICIOUS_FILE = "malicious_file"
    SUSPICIOUS_LOGIN = "suspicious_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"


class AccessLevel(str):
    """Access level enumeration"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'description': self.description,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'actions_taken': self.actions_taken
        }


@dataclass
class AccessAttempt:
    """Access attempt record"""
    attempt_id: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'attempt_id': self.attempt_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'success': self.success,
            'timestamp': self.timestamp.isoformat(),
            'failure_reason': self.failure_reason,
            'geolocation': self.geolocation
        }


@dataclass
class SecurityConfig:
    """Security configuration"""
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    session_timeout_minutes: int = 60
    require_2fa: bool = True
    rate_limit_requests_per_minute: int = 100
    allowed_file_extensions: List[str] = field(default_factory=lambda: ['.jpg', '.png', '.mp3', '.mp4', '.wav'])
    max_file_size_mb: int = 100
    blocked_countries: List[str] = field(default_factory=list)
    trusted_ip_ranges: List[str] = field(default_factory=list)


class PasswordManager:
    """Advanced password management and validation"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.common_passwords = self._load_common_passwords()
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str, username: str = "") -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < self.config.password_min_length:
            issues.append(f"Password must be at least {self.config.password_min_length} characters long")
        else:
            score += min(len(password) * 2, 20)  # Up to 20 points for length
        
        # Character type checks
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if self.config.password_require_uppercase and not has_upper:
            issues.append("Password must contain at least one uppercase letter")
        elif has_upper:
            score += 10
        
        if not has_lower:
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 10
        
        if self.config.password_require_numbers and not has_digit:
            issues.append("Password must contain at least one number")
        elif has_digit:
            score += 10
        
        if self.config.password_require_special and not has_special:
            issues.append("Password must contain at least one special character")
        elif has_special:
            score += 10
        
        # Common password check
        if password.lower() in self.common_passwords:
            issues.append("Password is too common")
            score -= 20
        
        # Username similarity check
        if username and username.lower() in password.lower():
            issues.append("Password should not contain username")
            score -= 10
        
        # Repetitive pattern check
        if self._has_repetitive_patterns(password):
            issues.append("Password contains repetitive patterns")
            score -= 10
        
        # Dictionary word check
        if self._contains_dictionary_words(password):
            issues.append("Password should not contain common dictionary words")
            score -= 5
        
        # Calculate strength level
        strength_level = "weak"
        if score >= 70:
            strength_level = "very_strong"
        elif score >= 50:
            strength_level = "strong"
        elif score >= 30:
            strength_level = "medium"
        elif score >= 10:
            strength_level = "weak"
        else:
            strength_level = "very_weak"
        
        return {
            'valid': len(issues) == 0,
            'score': max(0, score),
            'strength': strength_level,
            'issues': issues,
            'suggestions': self._get_password_suggestions(password, issues)
        }
    
    def generate_secure_password(self, length: int = 16, 
                                include_symbols: bool = True) -> str:
        """Generate a secure password"""
        import string
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each required category
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits)
        ]
        
        if include_symbols:
            password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # Fill the rest randomly
        for _ in range(length - len(password)):
            password.append(secrets.choice(characters))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        # In a real implementation, you'd load from a file
        return {
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890', 'password1',
            'abc123', '111111', '123123', 'password!', 'admin123'
        }
    
    def _has_repetitive_patterns(self, password: str) -> bool:
        """Check for repetitive patterns"""
        # Check for repeated characters
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        
        # Check for sequential patterns
        sequences = ['abcd', '1234', 'qwer', 'asdf', 'zxcv']
        for seq in sequences:
            if seq in password.lower() or seq[::-1] in password.lower():
                return True
        
        return False
    
    def _contains_dictionary_words(self, password: str) -> bool:
        """Check for common dictionary words"""
        common_words = {
            'password', 'admin', 'user', 'login', 'welcome',
            'hello', 'world', 'test', 'demo', 'sample'
        }
        
        password_lower = password.lower()
        return any(word in password_lower for word in common_words)
    
    def _get_password_suggestions(self, password: str, issues: List[str]) -> List[str]:
        """Get suggestions for improving password"""
        suggestions = []
        
        if any("length" in issue for issue in issues):
            suggestions.append("Make your password longer")
        
        if any("uppercase" in issue for issue in issues):
            suggestions.append("Add uppercase letters")
        
        if any("number" in issue for issue in issues):
            suggestions.append("Add numbers")
        
        if any("special" in issue for issue in issues):
            suggestions.append("Add special characters (!@#$%^&*)")
        
        if any("common" in issue for issue in issues):
            suggestions.append("Avoid common passwords")
        
        if any("username" in issue for issue in issues):
            suggestions.append("Don't include your username")
        
        return suggestions


class TwoFactorAuth:
    """Two-factor authentication manager"""
    
    def __init__(self):
        self.backup_codes_count = 10
    
    def generate_secret(self, user_id: str, service_name: str = "IA Influencer Agent") -> str:
        """Generate TOTP secret for user"""
        secret = pyotp.random_base32()
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str, 
                        service_name: str = "IA Influencer Agent") -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=service_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_code_data
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    
    def generate_backup_codes(self, count: int = None) -> List[str]:
        """Generate backup codes"""
        if count is None:
            count = self.backup_codes_count
        
        codes = []
        for _ in range(count):
            # Generate 8-digit backup codes
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            codes.append(code)
        
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> List[str]:
        """Hash backup codes for storage"""
        return [hashlib.sha256(code.encode()).hexdigest() for code in codes]
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> bool:
        """Verify backup code"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return code_hash in hashed_codes


class IPSecurityManager:
    """IP-based security management"""
    
    def __init__(self, config: SecurityConfig, geoip_db_path: Optional[str] = None):
        self.config = config
        self.blocked_ips = set()
        self.trusted_ips = set()
        self.geoip_reader = None
        
        # Load GeoIP database if available
        if geoip_db_path and Path(geoip_db_path).exists():
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_db_path)
            except Exception as e:
                logger.error(f"Failed to load GeoIP database: {str(e)}")
        
        # Parse trusted IP ranges
        for ip_range in self.config.trusted_ip_ranges:
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
                self.trusted_ips.add(network)
            except ValueError:
                logger.warning(f"Invalid IP range: {ip_range}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check direct blocks
            if ip in self.blocked_ips:
                return True
            
            # Check geolocation blocks
            if self.config.blocked_countries and self.geoip_reader:
                try:
                    response = self.geoip_reader.country(ip_address)
                    country_code = response.country.iso_code
                    if country_code in self.config.blocked_countries:
                        return True
                except geoip2.errors.AddressNotFoundError:
                    pass
            
            return False
            
        except ValueError:
            # Invalid IP address format
            return True
    
    def is_ip_trusted(self, ip_address: str) -> bool:
        """Check if IP address is trusted"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for trusted_network in self.trusted_ips:
                if ip in trusted_network:
                    return True
            
            return False
            
        except ValueError:
            return False
    
    def block_ip(self, ip_address: str, duration_hours: Optional[int] = None):
        """Block IP address"""
        try:
            ip = ipaddress.ip_address(ip_address)
            self.blocked_ips.add(ip)
            
            if duration_hours:
                # Schedule unblock (in a real implementation, you'd use a task scheduler)
                logger.info(f"IP {ip_address} blocked for {duration_hours} hours")
            else:
                logger.info(f"IP {ip_address} permanently blocked")
                
        except ValueError:
            logger.error(f"Invalid IP address for blocking: {ip_address}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        try:
            ip = ipaddress.ip_address(ip_address)
            self.blocked_ips.discard(ip)
            logger.info(f"IP {ip_address} unblocked")
        except ValueError:
            logger.error(f"Invalid IP address for unblocking: {ip_address}")
    
    def get_geolocation(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get geolocation information for IP"""
        if not self.geoip_reader:
            return None
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.name,
                'country_code': response.country.iso_code,
                'city': response.city.name,
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None,
                'timezone': str(response.location.time_zone) if response.location.time_zone else None
            }
        except Exception as e:
            logger.error(f"Geolocation lookup failed: {str(e)}")
            return None


class RateLimiter:
    """Advanced rate limiting system"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.request_counts = defaultdict(lambda: {'count': 0, 'reset_time': datetime.utcnow()})
        self._lock = threading.Lock()
    
    def is_rate_limited(self, identifier: str, 
                       custom_limit: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if identifier is rate limited"""
        with self._lock:
            limit = custom_limit or self.config.rate_limit_requests_per_minute
            now = datetime.utcnow()
            
            if identifier not in self.request_counts:
                self.request_counts[identifier] = {'count': 0, 'reset_time': now}
            
            request_data = self.request_counts[identifier]
            
            # Reset counter if a minute has passed
            if (now - request_data['reset_time']).total_seconds() >= 60:
                request_data['count'] = 0
                request_data['reset_time'] = now
            
            # Check if limit exceeded
            if request_data['count'] >= limit:
                time_until_reset = 60 - (now - request_data['reset_time']).total_seconds()
                return True, {
                    'limited': True,
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': int(time.time() + time_until_reset)
                }
            
            # Increment counter
            request_data['count'] += 1
            
            return False, {
                'limited': False,
                'limit': limit,
                'remaining': limit - request_data['count'],
                'reset_time': int((request_data['reset_time'] + timedelta(minutes=1)).timestamp())
            }
    
    def clear_rate_limit(self, identifier: str):
        """Clear rate limit for identifier"""
        with self._lock:
            if identifier in self.request_counts:
                del self.request_counts[identifier]


class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.detection_patterns = self._load_detection_patterns()
        self.failed_attempts = defaultdict(list)
        self._lock = threading.Lock()
    
    def detect_threats(self, request_data: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect threats in request data"""
        threats = []
        
        # SQL Injection detection
        sql_threat = self._detect_sql_injection(request_data)
        if sql_threat:
            threats.append(sql_threat)
        
        # XSS detection
        xss_threat = self._detect_xss(request_data)
        if xss_threat:
            threats.append(xss_threat)
        
        # Brute force detection
        brute_force_threat = self._detect_brute_force(request_data)
        if brute_force_threat:
            threats.append(brute_force_threat)
        
        # File upload threats
        file_threat = self._detect_malicious_file(request_data)
        if file_threat:
            threats.append(file_threat)
        
        return threats
    
    def _detect_sql_injection(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"delete\s+from",
            r"insert\s+into", r"update\s+set", r"'.*or.*'.*=.*'",
            r";\s*--", r"/\*.*\*/"
        ]
        
        content = json.dumps(request_data).lower()
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=ThreatType.SQL_INJECTION,
                    severity=SecurityLevel.HIGH,
                    source_ip=request_data.get('ip', 'unknown'),
                    description=f"SQL injection pattern detected: {pattern}",
                    metadata={'pattern': pattern, 'request_data': request_data}
                )
        
        return None
    
    def _detect_xss(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect XSS attempts"""
        xss_patterns = [
            r"<script.*?>.*?</script>", r"javascript:", r"vbscript:",
            r"onload\s*=", r"onerror\s*=", r"onclick\s*=",
            r"alert\s*\(", r"document\.cookie", r"window\.location"
        ]
        
        content = json.dumps(request_data).lower()
        
        for pattern in xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=ThreatType.XSS,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=request_data.get('ip', 'unknown'),
                    description=f"XSS pattern detected: {pattern}",
                    metadata={'pattern': pattern, 'request_data': request_data}
                )
        
        return None
    
    def _detect_brute_force(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect brute force attacks"""
        if request_data.get('login_failed'):
            ip = request_data.get('ip', 'unknown')
            user_id = request_data.get('user_id')
            
            with self._lock:
                now = datetime.utcnow()
                
                # Clean old attempts
                cutoff_time = now - timedelta(minutes=10)
                self.failed_attempts[ip] = [
                    attempt for attempt in self.failed_attempts[ip]
                    if attempt > cutoff_time
                ]
                
                # Add current attempt
                self.failed_attempts[ip].append(now)
                
                # Check if threshold exceeded
                if len(self.failed_attempts[ip]) >= self.config.max_login_attempts:
                    return SecurityEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=ThreatType.BRUTE_FORCE,
                        severity=SecurityLevel.HIGH,
                        source_ip=ip,
                        user_id=user_id,
                        description=f"Brute force attack detected: {len(self.failed_attempts[ip])} failed attempts",
                        metadata={
                            'failed_attempts': len(self.failed_attempts[ip]),
                            'time_window': '10 minutes'
                        }
                    )
        
        return None
    
    def _detect_malicious_file(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect malicious file uploads"""
        files = request_data.get('files', [])
        
        for file_info in files:
            filename = file_info.get('filename', '')
            file_size = file_info.get('size', 0)
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.config.allowed_file_extensions:
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=ThreatType.MALICIOUS_FILE,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=request_data.get('ip', 'unknown'),
                    description=f"Disallowed file extension: {file_ext}",
                    metadata={'filename': filename, 'extension': file_ext}
                )
            
            # Check file size
            max_size = self.config.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=ThreatType.MALICIOUS_FILE,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=request_data.get('ip', 'unknown'),
                    description=f"File size exceeds limit: {file_size} bytes",
                    metadata={'filename': filename, 'size': file_size, 'limit': max_size}
                )
        
        return None
    
    def _load_detection_patterns(self) -> Dict[str, List[str]]:
        """Load threat detection patterns"""
        return {
            'sql_injection': [
                'union select', 'drop table', 'insert into',
                'delete from', 'update set', 'exec master',
                'script src', 'javascript:', 'vbscript:'
            ],
            'xss': [
                '<script', '</script>', 'javascript:', 'vbscript:',
                'onload=', 'onerror=', 'onclick=', 'onmouseover='
            ],
            'path_traversal': [
                '../', '..\\', '%2e%2e%2f', '%2e%2e%5c',
                'etc/passwd', 'boot.ini', 'windows/system32'
            ]
        }


class AuditLogger:
    """Security audit logging system"""
    
    def __init__(self, database_path: str = "security_audit.db"):
        self.database_path = database_path
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize audit database"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    user_agent TEXT,
                    endpoint TEXT,
                    description TEXT,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at TEXT,
                    actions_taken TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    failure_reason TEXT,
                    geolocation TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events (timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_type ON security_events (event_type)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_attempts_ip ON access_attempts (ip_address)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_attempts_user ON access_attempts (user_id)
            ''')
    
    def log_security_event(self, event: SecurityEvent) -> bool:
        """Log security event"""
        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    conn.execute('''
                        INSERT INTO security_events
                        (event_id, event_type, severity, source_ip, user_id,
                         user_agent, endpoint, description, metadata, timestamp,
                         resolved, resolved_at, actions_taken)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.event_id,
                        event.event_type,
                        event.severity,
                        event.source_ip,
                        event.user_id,
                        event.user_agent,
                        event.endpoint,
                        event.description,
                        json.dumps(event.metadata),
                        event.timestamp.isoformat(),
                        event.resolved,
                        event.resolved_at.isoformat() if event.resolved_at else None,
                        json.dumps(event.actions_taken)
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return False
    
    def log_access_attempt(self, attempt: AccessAttempt) -> bool:
        """Log access attempt"""
        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    conn.execute('''
                        INSERT INTO access_attempts
                        (attempt_id, user_id, ip_address, user_agent, endpoint,
                         success, timestamp, failure_reason, geolocation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        attempt.attempt_id,
                        attempt.user_id,
                        attempt.ip_address,
                        attempt.user_agent,
                        attempt.endpoint,
                        attempt.success,
                        attempt.timestamp.isoformat(),
                        attempt.failure_reason,
                        json.dumps(attempt.geolocation) if attempt.geolocation else None
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to log access attempt: {str(e)}")
            return False
    
    def get_security_events(self, hours: int = 24, 
                           event_type: Optional[ThreatType] = None,
                           severity: Optional[SecurityLevel] = None) -> List[SecurityEvent]:
        """Get security events from specified time period"""
        events = []
        try:
            since_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            query = '''
                SELECT * FROM security_events 
                WHERE timestamp >= ?
            '''
            params = [since_time]
            
            if event_type:
                query += ' AND event_type = ?'
                params.append(event_type)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity)
            
            query += ' ORDER BY timestamp DESC'
            
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                
                for row in cursor:
                    event = SecurityEvent(
                        event_id=row['event_id'],
                        event_type=ThreatType(row['event_type']),
                        severity=SecurityLevel(row['severity']),
                        source_ip=row['source_ip'],
                        user_id=row['user_id'],
                        user_agent=row['user_agent'],
                        endpoint=row['endpoint'],
                        description=row['description'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        resolved=bool(row['resolved']),
                        resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                        actions_taken=json.loads(row['actions_taken']) if row['actions_taken'] else []
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Failed to get security events: {str(e)}")
        
        return events
    
    def get_security_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get security statistics"""
        try:
            since_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Total events
                cursor = conn.execute(
                    'SELECT COUNT(*) as count FROM security_events WHERE timestamp >= ?',
                    (since_time,)
                )
                total_events = cursor.fetchone()['count']
                
                # Events by type
                cursor = conn.execute('''
                    SELECT event_type, COUNT(*) as count 
                    FROM security_events 
                    WHERE timestamp >= ? 
                    GROUP BY event_type
                ''', (since_time,))
                events_by_type = {row['event_type']: row['count'] for row in cursor}
                
                # Events by severity
                cursor = conn.execute('''
                    SELECT severity, COUNT(*) as count 
                    FROM security_events 
                    WHERE timestamp >= ? 
                    GROUP BY severity
                ''', (since_time,))
                events_by_severity = {row['severity']: row['count'] for row in cursor}
                
                # Top source IPs
                cursor = conn.execute('''
                    SELECT source_ip, COUNT(*) as count 
                    FROM security_events 
                    WHERE timestamp >= ? 
                    GROUP BY source_ip 
                    ORDER BY count DESC 
                    LIMIT 10
                ''', (since_time,))
                top_source_ips = {row['source_ip']: row['count'] for row in cursor}
                
                # Access attempt statistics
                cursor = conn.execute(
                    'SELECT COUNT(*) as count FROM access_attempts WHERE timestamp >= ?',
                    (since_time,)
                )
                total_attempts = cursor.fetchone()['count']
                
                cursor = conn.execute(
                    'SELECT COUNT(*) as count FROM access_attempts WHERE timestamp >= ? AND success = 1',
                    (since_time,)
                )
                successful_attempts = cursor.fetchone()['count']
                
                return {
                    'time_period_hours': hours,
                    'total_security_events': total_events,
                    'events_by_type': events_by_type,
                    'events_by_severity': events_by_severity,
                    'top_source_ips': top_source_ips,
                    'total_access_attempts': total_attempts,
                    'successful_access_attempts': successful_attempts,
                    'failed_access_attempts': total_attempts - successful_attempts,
                    'success_rate': successful_attempts / total_attempts if total_attempts > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get security statistics: {str(e)}")
            return {'error': str(e)}


class SecurityManager:
    """Main security management system"""
    
    def __init__(self, config: SecurityConfig, geoip_db_path: Optional[str] = None):
        self.config = config
        self.password_manager = PasswordManager(config)
        self.two_factor_auth = TwoFactorAuth()
        self.ip_manager = IPSecurityManager(config, geoip_db_path)
        self.rate_limiter = RateLimiter(config)
        self.threat_detector = ThreatDetector(config)
        self.audit_logger = AuditLogger()
        
        # Session management
        self.active_sessions = {}
        self._session_lock = threading.Lock()
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Authenticate user with comprehensive security checks"""
        attempt_id = str(uuid.uuid4())
        
        # Check if IP is blocked
        if self.ip_manager.is_ip_blocked(ip_address):
            attempt = AccessAttempt(
                attempt_id=attempt_id,
                user_id=username,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint="/auth/login",
                success=False,
                failure_reason="IP address blocked"
            )
            self.audit_logger.log_access_attempt(attempt)
            
            return {
                'success': False,
                'error': 'Access denied from this location',
                'blocked': True
            }
        
        # Check rate limiting
        rate_limited, rate_info = self.rate_limiter.is_rate_limited(ip_address)
        if rate_limited:
            attempt = AccessAttempt(
                attempt_id=attempt_id,
                user_id=username,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint="/auth/login",
                success=False,
                failure_reason="Rate limit exceeded"
            )
            self.audit_logger.log_access_attempt(attempt)
            
            return {
                'success': False,
                'error': 'Too many attempts. Please try again later.',
                'rate_limit': rate_info
            }
        
        # Detect threats
        request_data = {
            'ip': ip_address,
            'user_agent': user_agent,
            'username': username,
            'login_attempt': True
        }
        
        threats = self.threat_detector.detect_threats(request_data)
        for threat in threats:
            self.audit_logger.log_security_event(threat)
        
        # Here you would validate credentials against your user database
        # For demo purposes, assuming validation is done elsewhere
        
        # Log successful attempt
        geolocation = self.ip_manager.get_geolocation(ip_address)
        attempt = AccessAttempt(
            attempt_id=attempt_id,
            user_id=username,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint="/auth/login",
            success=True,
            geolocation=geolocation
        )
        self.audit_logger.log_access_attempt(attempt)
        
        # Create session
        session_id = self.create_session(username, ip_address)
        
        return {
            'success': True,
            'session_id': session_id,
            'requires_2fa': self.config.require_2fa,
            'geolocation': geolocation
        }
    
    def create_session(self, user_id: str, ip_address: str) -> str:
        """Create secure session"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=self.config.session_timeout_minutes)
        }
        
        with self._session_lock:
            self.active_sessions[session_id] = session_data
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate session"""
        with self._session_lock:
            session = self.active_sessions.get(session_id)
            
            if not session:
                return None
            
            # Check expiration
            if datetime.utcnow() > session['expires_at']:
                del self.active_sessions[session_id]
                return None
            
            # Check IP address (optional, for enhanced security)
            if session['ip_address'] != ip_address and not self.ip_manager.is_ip_trusted(ip_address):
                # Log suspicious activity
                event = SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=ThreatType.SUSPICIOUS_LOGIN,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=ip_address,
                    user_id=session['user_id'],
                    description="Session accessed from different IP address",
                    metadata={'original_ip': session['ip_address'], 'new_ip': ip_address}
                )
                self.audit_logger.log_security_event(event)
            
            # Update last activity
            session['last_activity'] = datetime.utcnow()
            
            return session
    
    def revoke_session(self, session_id: str):
        """Revoke session"""
        with self._session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        
        with self._session_lock:
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if now > session['expires_at']
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        stats = self.audit_logger.get_security_statistics(hours=24)
        recent_events = self.audit_logger.get_security_events(hours=1)
        
        return {
            'statistics': stats,
            'recent_events': [event.to_dict() for event in recent_events[:10]],
            'active_sessions': len(self.active_sessions),
            'blocked_ips': len(self.ip_manager.blocked_ips),
            'system_status': 'operational'
        }


def require_permission(required_level: AccessLevel):
    """Decorator to require specific permission level"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user session from request context
            # This is a simplified example - implement based on your framework
            user_level = kwargs.get('user_access_level', AccessLevel.PUBLIC)
            
            access_levels = [
                AccessLevel.PUBLIC,
                AccessLevel.AUTHENTICATED,
                AccessLevel.PREMIUM,
                AccessLevel.ADMIN,
                AccessLevel.SUPER_ADMIN
            ]
            
            if access_levels.index(user_level) < access_levels.index(required_level):
                raise PermissionError(f"Insufficient permissions. Required: {required_level}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError(Exception):
    """Custom security exception"""
    pass
