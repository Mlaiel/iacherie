"""Security Utilities for Ainflue SDK

Multi-expert implementation:
- Security: Comprehensive security utilities and encryption
- Backend Senior: Robust security architecture patterns
- DevOps: Security monitoring and audit logging  
- Lead Dev IA: Intelligent threat detection and prevention

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import base64
import hashlib
import hmac
import logging
import secrets
import time
import re
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
from urllib.parse import urlparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import bcrypt

from .exceptions import SecurityError, ValidationError


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Security event types"""
    INVALID_AUTH = "invalid_auth"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_IP = "suspicious_ip"
    MALFORMED_REQUEST = "malformed_request"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


@dataclass
class SecurityMetrics:
    """Security monitoring metrics (DevOps expertise)"""
    total_security_events: int = 0
    blocked_requests: int = 0
    threat_detections: int = 0
    false_positives: int = 0
    threat_distribution: Dict[str, int] = field(default_factory=dict)
    ip_reputation: Dict[str, float] = field(default_factory=dict)
    
    @property
    def block_rate(self) -> float:
        """Calculate request block rate"""
        if self.total_security_events == 0:
            return 0.0
        return (self.blocked_requests / self.total_security_events) * 100


@dataclass
class SecurityAlert:
    """Security alert data structure"""
    event_type: SecurityEvent
    threat_level: ThreatLevel
    source_ip: Optional[str]
    user_agent: Optional[str]
    request_data: Optional[Dict[str, Any]]
    timestamp: datetime
    description: str
    blocked: bool = False


class PasswordValidator:
    """Password security validation (Security expertise)"""
    
    def __init__(self) -> None:
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Common password patterns to reject
        self.forbidden_patterns = [
            r'password',
            r'123456',
            r'qwerty',
            r'admin',
            r'root',
            r'user',
            r'test'
        ]
    
    def validate_password(self, password: str) -> tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        # Length validation
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for forbidden patterns
        password_lower = password.lower()
        for pattern in self.forbidden_patterns:
            if re.search(pattern, password_lower):
                errors.append(f"Password contains forbidden pattern: {pattern}")
        
        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append("Password contains too many repeated characters")
        
        return len(errors) == 0, errors
    
    def _has_repeated_chars(self, password: str, max_repeat: int = 3) -> bool:
        """Check for excessive character repetition"""
        for i in range(len(password) - max_repeat + 1):
            if all(password[i] == password[i + j] for j in range(max_repeat)):
                return True
        return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate cryptographically secure password"""
        if length < self.min_length:
            length = self.min_length
        
        # Ensure we have at least one of each required character type
        chars = []
        
        if self.require_uppercase:
            chars.append(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        
        if self.require_lowercase:
            chars.append(secrets.choice('abcdefghijklmnopqrstuvwxyz'))
        
        if self.require_digits:
            chars.append(secrets.choice('0123456789'))
        
        if self.require_special:
            chars.append(secrets.choice(self.special_chars))
        
        # Fill remaining length with random characters
        all_chars = ''
        if self.require_uppercase:
            all_chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.require_lowercase:
            all_chars += 'abcdefghijklmnopqrstuvwxyz'
        if self.require_digits:
            all_chars += '0123456789'
        if self.require_special:
            all_chars += self.special_chars
        
        while len(chars) < length:
            chars.append(secrets.choice(all_chars))
        
        # Shuffle the characters
        secrets.SystemRandom().shuffle(chars)
        
        return ''.join(chars)


class EncryptionManager:
    """Encryption and decryption utilities (Security expertise)"""
    
    def __init__(self, master_key -> None: Optional[str] = None) -> None:
        self.master_key = master_key
        self._fernet = None
        
        if master_key:
            self._setup_encryption()
    
    def _setup_encryption(self) -> None:
        """Setup Fernet encryption with derived key"""
        if isinstance(self.master_key, str):
            # Derive key from master key
            password = self.master_key.encode()
            salt = self._get_or_generate_salt()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = self.master_key
        
        self._fernet = Fernet(key)
    
    def _get_or_generate_salt(self) -> bytes:
        """Get or generate salt for key derivation"""
        # In production, store salt securely
        return b'ainflue_security_salt_2025'
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using Fernet"""
        if not self._fernet:
            raise SecurityError("Encryption not configured")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self._fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        if not self._fernet:
            raise SecurityError("Encryption not configured")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise SecurityError(f"Decryption failed: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix: str = "ak_", length: int = 32) -> str:
        """Generate secure API key"""
        key_part = secrets.token_urlsafe(length)
        return f"{prefix}{key_part}"
    
    def compute_hmac(self, data: str, secret: str, algorithm: str = 'sha256') -> str:
        """Compute HMAC for data integrity"""
        if algorithm == 'sha256':
            hash_func = hashlib.sha256
        elif algorithm == 'sha512':
            hash_func = hashlib.sha512
        else:
            raise SecurityError(f"Unsupported HMAC algorithm: {algorithm}")
        
        signature = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hash_func
        ).hexdigest()
        
        return signature
    
    def verify_hmac(self, data: str, signature: str, secret: str, algorithm: str = 'sha256') -> bool:
        """Verify HMAC signature"""
        try:
            expected_signature = self.compute_hmac(data, secret, algorithm)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False


class InputSanitizer:
    """Input sanitization and validation (Security expertise)"""
    
    def __init__(self) -> None:
        # SQL injection patterns
        self.sql_patterns = [
            r"(union\s+select)",
            r"(drop\s+table)",
            r"(delete\s+from)",
            r"(insert\s+into)",
            r"(update\s+set)",
            r"(exec\s*\()",
            r"(script\s*>)",
            r"(javascript:)",
            r"(vbscript:)",
            r"(onload\s*=)",
            r"(onerror\s*=)",
            r"(<\s*script)",
            r"(eval\s*\()",
            r"(expression\s*\()",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<\s*script",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<\s*iframe",
            r"<\s*object",
            r"<\s*embed",
            r"eval\s*\(",
            r"expression\s*\(",
        ]
    
    def sanitize_string(self, input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            raise ValidationError("Input must be a string")
        
        # Truncate if too long
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # Remove null bytes
        input_str = input_str.replace('\x00', '')
        
        # Remove control characters except common whitespace
        sanitized = ''
        for char in input_str:
            if ord(char) >= 32 or char in '\t\n\r':
                sanitized += char
        
        return sanitized.strip()
    
    def detect_sql_injection(self, input_str: str) -> bool:
        """Detect potential SQL injection attempts"""
        input_lower = input_str.lower()
        
        for pattern in self.sql_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    def detect_xss(self, input_str: str) -> bool:
        """Detect potential XSS attempts"""
        input_lower = input_str.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address (IPv4 or IPv6)"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def validate_url(self, url: str, allowed_schemes: List[str] = None) -> bool:
        """Validate URL format and scheme"""
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in allowed_schemes and
                parsed.netloc and
                not any(char in url for char in '<>"\'')
            )
        except Exception:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove potentially dangerous characters
        dangerous_chars = '<>:"|?*'
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Ensure filename is not empty
        if not filename.strip():
            filename = 'unnamed_file'
        
        return filename


class ThreatDetector:
    """Intelligent threat detection (Lead Dev IA expertise)"""
    
    def __init__(self) -> None:
        self.request_history = {}  # IP -> list of timestamps
        self.failed_auth_attempts = {}  # IP -> count
        self.suspicious_patterns = {}  # IP -> pattern count
        self.ip_reputation = {}  # IP -> reputation score (0-1)
        
        # Detection thresholds
        self.rate_limit_threshold = 100  # requests per minute
        self.brute_force_threshold = 5   # failed auth attempts
        self.suspicious_threshold = 3    # suspicious patterns
        
    def analyze_request(self, 
                       client_ip: str,
                       user_agent: Optional[str] = None,
                       request_data: Optional[Dict[str, Any]] = None) -> Optional[SecurityAlert]:
        """Analyze request for security threats"""
        current_time = time.time()
        
        # Initialize IP tracking
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
            self.ip_reputation[client_ip] = 1.0  # Start with good reputation
        
        # Add current request
        self.request_history[client_ip].append(current_time)
        
        # Clean old requests (older than 1 hour)
        cutoff_time = current_time - 3600
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip] if ts > cutoff_time
        ]
        
        # Rate limiting check
        recent_requests = [
            ts for ts in self.request_history[client_ip]
            if ts > current_time - 60  # Last minute
        ]
        
        if len(recent_requests) > self.rate_limit_threshold:
            self._update_reputation(client_ip, -0.2)
            return SecurityAlert(
                event_type=SecurityEvent.RATE_LIMIT_EXCEEDED,
                threat_level=ThreatLevel.HIGH,
                source_ip=client_ip,
                user_agent=user_agent,
                request_data=request_data,
                timestamp=datetime.now(),
                description=f"Rate limit exceeded: {len(recent_requests)} requests in last minute",
                blocked=True
            )
        
        # Check for suspicious patterns in request data
        if request_data:
            threat = self._check_request_patterns(client_ip, request_data, user_agent)
            if threat:
                return threat
        
        # Check user agent patterns
        if user_agent:
            threat = self._check_user_agent(client_ip, user_agent, request_data)
            if threat:
                return threat
        
        return None
    
    def record_auth_failure(self, client_ip: str, user_agent: Optional[str] = None) -> Optional[SecurityAlert]:
        """Record authentication failure and check for brute force"""
        if client_ip not in self.failed_auth_attempts:
            self.failed_auth_attempts[client_ip] = 0
        
        self.failed_auth_attempts[client_ip] += 1
        self._update_reputation(client_ip, -0.1)
        
        if self.failed_auth_attempts[client_ip] >= self.brute_force_threshold:
            return SecurityAlert(
                event_type=SecurityEvent.BRUTE_FORCE_ATTACK,
                threat_level=ThreatLevel.CRITICAL,
                source_ip=client_ip,
                user_agent=user_agent,
                request_data=None,
                timestamp=datetime.now(),
                description=f"Brute force attack detected: {self.failed_auth_attempts[client_ip]} failed attempts",
                blocked=True
            )
        
        return None
    
    def record_auth_success(self, client_ip -> None: str) -> None:
        """Record successful authentication"""
        # Reset failed attempts on successful auth
        self.failed_auth_attempts[client_ip] = 0
        self._update_reputation(client_ip, 0.1)
    
    def _check_request_patterns(self, 
                               client_ip: str, 
                               request_data: Dict[str, Any],
                               user_agent: Optional[str]) -> Optional[SecurityAlert]:
        """Check request data for malicious patterns"""
        sanitizer = InputSanitizer()
        
        # Convert request data to string for pattern checking
        request_str = str(request_data)
        
        # Check for SQL injection
        if sanitizer.detect_sql_injection(request_str):
            self._update_reputation(client_ip, -0.3)
            return SecurityAlert(
                event_type=SecurityEvent.SQL_INJECTION_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                source_ip=client_ip,
                user_agent=user_agent,
                request_data=request_data,
                timestamp=datetime.now(),
                description="SQL injection attempt detected",
                blocked=True
            )
        
        # Check for XSS
        if sanitizer.detect_xss(request_str):
            self._update_reputation(client_ip, -0.3)
            return SecurityAlert(
                event_type=SecurityEvent.XSS_ATTEMPT,
                threat_level=ThreatLevel.HIGH,
                source_ip=client_ip,
                user_agent=user_agent,
                request_data=request_data,
                timestamp=datetime.now(),
                description="XSS attempt detected",
                blocked=True
            )
        
        return None
    
    def _check_user_agent(self, 
                         client_ip: str, 
                         user_agent: str,
                         request_data: Optional[Dict[str, Any]]) -> Optional[SecurityAlert]:
        """Check user agent for suspicious patterns"""
        suspicious_patterns = [
            'sqlmap',
            'nikto',
            'nessus',
            'burp',
            'owasp',
            'masscan',
            'nmap',
            'dirb',
            'gobuster',
            'wget',
            'curl',  # Suspicious if not legitimate API usage
        ]
        
        user_agent_lower = user_agent.lower()
        
        for pattern in suspicious_patterns:
            if pattern in user_agent_lower:
                self._update_reputation(client_ip, -0.2)
                return SecurityAlert(
                    event_type=SecurityEvent.SUSPICIOUS_IP,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=client_ip,
                    user_agent=user_agent,
                    request_data=request_data,
                    timestamp=datetime.now(),
                    description=f"Suspicious user agent detected: {pattern}",
                    blocked=False
                )
        
        return None
    
    def _update_reputation(self, client_ip -> None: str, delta -> None: float) -> None:
        """Update IP reputation score"""
        current_reputation = self.ip_reputation.get(client_ip, 1.0)
        new_reputation = max(0.0, min(1.0, current_reputation + delta))
        self.ip_reputation[client_ip] = new_reputation
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP should be blocked based on reputation"""
        reputation = self.ip_reputation.get(client_ip, 1.0)
        return reputation < 0.3  # Block if reputation is very low
    
    def get_ip_reputation(self, client_ip: str) -> float:
        """Get IP reputation score"""
        return self.ip_reputation.get(client_ip, 1.0)


class SecurityAuditor:
    """Security audit logging (DevOps expertise)"""
    
    def __init__(self, log_file -> None: Optional[str] = None) -> None:
        self.logger = logging.getLogger('security_audit')
        self.metrics = SecurityMetrics()
        
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_security_event(self, alert -> None: SecurityAlert) -> None:
        """Log security event for audit trail"""
        try:
            self.metrics.total_security_events += 1
            
            if alert.blocked:
                self.metrics.blocked_requests += 1
            
            # Update threat distribution
            event_type = alert.event_type.value
            self.metrics.threat_distribution[event_type] = \
                self.metrics.threat_distribution.get(event_type, 0) + 1
            
            # Log the event
            log_data = {
                'event_type': alert.event_type.value,
                'threat_level': alert.threat_level.value,
                'source_ip': alert.source_ip,
                'user_agent': alert.user_agent,
                'timestamp': alert.timestamp.isoformat(),
                'description': alert.description,
                'blocked': alert.blocked
            }
            
            self.logger.warning(f"Security Event: {log_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics summary"""
        return {
            'total_security_events': self.metrics.total_security_events,
            'blocked_requests': self.metrics.blocked_requests,
            'block_rate': self.metrics.block_rate,
            'threat_distribution': self.metrics.threat_distribution,
            'top_threats': sorted(
                self.metrics.threat_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


class SecurityUtils:
    """Main security utilities class with multi-expert implementation"""
    
    def __init__(self, master_key -> None: Optional[str] = None, audit_log_file -> None: Optional[str] = None) -> None:
        self.password_validator = PasswordValidator()
        self.encryption_manager = EncryptionManager(master_key)
        self.input_sanitizer = InputSanitizer()
        self.threat_detector = ThreatDetector()
        self.security_auditor = SecurityAuditor(audit_log_file)
        
        self.logger = logging.getLogger(__name__)
    
    def validate_and_sanitize_input(self, 
                                   input_data: Dict[str, Any],
                                   client_ip: str,
                                   user_agent: Optional[str] = None) -> tuple[bool, Dict[str, Any], Optional[SecurityAlert]]:
        """Validate and sanitize input data"""
        try:
            # Analyze request for threats
            threat_alert = self.threat_detector.analyze_request(client_ip, user_agent, input_data)
            
            if threat_alert:
                self.security_auditor.log_security_event(threat_alert)
                if threat_alert.blocked:
                    return False, {}, threat_alert
            
            # Sanitize input data
            sanitized_data = {}
            for key, value in input_data.items():
                if isinstance(value, str):
                    # Check for malicious patterns
                    if (self.input_sanitizer.detect_sql_injection(value) or 
                        self.input_sanitizer.detect_xss(value)):
                        
                        alert = SecurityAlert(
                            event_type=SecurityEvent.MALFORMED_REQUEST,
                            threat_level=ThreatLevel.HIGH,
                            source_ip=client_ip,
                            user_agent=user_agent,
                            request_data={key: value},
                            timestamp=datetime.now(),
                            description=f"Malicious pattern detected in field: {key}",
                            blocked=True
                        )
                        
                        self.security_auditor.log_security_event(alert)
                        return False, {}, alert
                    
                    # Sanitize the value
                    sanitized_data[key] = self.input_sanitizer.sanitize_string(value)
                else:
                    sanitized_data[key] = value
            
            return True, sanitized_data, threat_alert
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {e}")
            return False, {}, None
    
    def check_ip_reputation(self, client_ip: str) -> tuple[bool, float]:
        """Check IP reputation and whether it should be blocked"""
        reputation = self.threat_detector.get_ip_reputation(client_ip)
        is_blocked = self.threat_detector.is_ip_blocked(client_ip)
        
        return not is_blocked, reputation
    
    def record_authentication_event(self, 
                                   client_ip: str, 
                                   success: bool,
                                   user_agent: Optional[str] = None) -> Optional[SecurityAlert]:
        """Record authentication event"""
        if success:
            self.threat_detector.record_auth_success(client_ip)
            return None
        else:
            alert = self.threat_detector.record_auth_failure(client_ip, user_agent)
            if alert:
                self.security_auditor.log_security_event(alert)
            return alert
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get comprehensive security summary"""
        return {
            'security_metrics': self.security_auditor.get_security_metrics(),
            'ip_reputation_stats': {
                'total_tracked_ips': len(self.threat_detector.ip_reputation),
                'blocked_ips': sum(1 for rep in self.threat_detector.ip_reputation.values() if rep < 0.3),
                'average_reputation': sum(self.threat_detector.ip_reputation.values()) / len(self.threat_detector.ip_reputation) if self.threat_detector.ip_reputation else 0
            }
        }


# Example usage
def example_security_usage() -> None:
    """Example security utilities usage"""
    # Initialize security utils
    security = SecurityUtils(
        master_key="your-master-encryption-key",
        audit_log_file="security_audit.log"
    )
    
    # Validate password
    password = "MySecureP@ssw0rd123"
    is_valid, errors = security.password_validator.validate_password(password)
    print(f"Password valid: {is_valid}, Errors: {errors}")
    
    # Generate secure password
    secure_password = security.password_validator.generate_secure_password(16)
    print(f"Generated password: {secure_password}")
    
    # Encrypt sensitive data
    sensitive_data = "user-credit-card-number"
    encrypted = security.encryption_manager.encrypt_data(sensitive_data)
    decrypted = security.encryption_manager.decrypt_data(encrypted)
    print(f"Encryption test: {sensitive_data} -> {encrypted} -> {decrypted}")
    
    # Validate and sanitize input
    test_input = {
        "username": "testuser",
        "comment": "<script>alert('xss')</script>",
        "query": "SELECT * FROM users WHERE id = 1"
    }
    
    is_safe, sanitized, alert = security.validate_and_sanitize_input(
        test_input, 
        "192.168.1.100", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    print(f"Input safe: {is_safe}")
    print(f"Sanitized: {sanitized}")
    if alert:
        print(f"Security alert: {alert.description}")
    
    # Get security summary
    summary = security.get_security_summary()
    print(f"Security summary: {summary}")


if __name__ == "__main__":
    # Run example
    example_security_usage()