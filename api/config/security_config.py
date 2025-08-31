"""Security Configuration - IA Influencer Agent Platform
Enterprise-grade security configuration for authentication, encryption, and protection

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import os
import secrets
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import timedelta, datetime
from enum import Enum
import hashlib
import hmac
from cryptography.fernet import Fernet
from passlib.context import CryptContext


class AuthenticationMethod(Enum):
    """Supported authentication methods"""    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    CUSTOM = "custom"


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    FERNET = "fernet"


@dataclass
class SecurityConfig:
    """Comprehensive security configuration"""    
    # Application Secrets
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", secrets.token_hex(32)))
    jwt_secret_key: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", secrets.token_hex(32)))
    encryption_key: str = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode()))
    api_key_secret: str = field(default_factory=lambda: os.getenv("API_KEY_SECRET", secrets.token_hex(32)))
    
    # Password Security
    password_salt: str = field(default_factory=lambda: os.getenv("PASSWORD_SALT", secrets.token_hex(16)))
    password_hash_algorithm: str = field(default_factory=lambda: os.getenv("PASSWORD_HASH_ALGORITHM", "bcrypt"))
    password_min_length: int = field(default_factory=lambda: int(os.getenv("PASSWORD_MIN_LENGTH", "8")))
    password_require_uppercase: bool = field(default_factory=lambda: 
        os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true")
    password_require_lowercase: bool = field(default_factory=lambda: 
        os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true")
    password_require_numbers: bool = field(default_factory=lambda: 
        os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true")
    password_require_special: bool = field(default_factory=lambda: 
        os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true")
    password_max_age_days: int = field(default_factory=lambda: int(os.getenv("PASSWORD_MAX_AGE_DAYS", "90")))
    
    # JWT Configuration
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_expire_minutes: int = field(default_factory=lambda: 
        int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE", "60")))
    jwt_refresh_token_expire_days: int = field(default_factory=lambda: 
        int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE", "30")))
    jwt_issuer: str = field(default_factory=lambda: 
        os.getenv("JWT_ISSUER", "ia-influencer-agent"))
    jwt_audience: str = field(default_factory=lambda: 
        os.getenv("JWT_AUDIENCE", "ia-influencer-users"))
    jwt_leeway_seconds: int = field(default_factory=lambda: 
        int(os.getenv("JWT_LEEWAY_SECONDS", "10")))
    
    # Session Management
    session_timeout_minutes: int = field(default_factory=lambda: 
        int(os.getenv("SESSION_TIMEOUT_MINUTES", "1440")))  # 24 hours
    session_cookie_name: str = field(default_factory=lambda: 
        os.getenv("SESSION_COOKIE_NAME", "ia_influencer_session"))
    session_cookie_domain: Optional[str] = field(default_factory=lambda: 
        os.getenv("SESSION_COOKIE_DOMAIN"))
    session_cookie_secure: bool = field(default_factory=lambda: 
        os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true")
    session_cookie_httponly: bool = field(default_factory=lambda: 
        os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true")
    session_cookie_samesite: str = field(default_factory=lambda: 
        os.getenv("SESSION_COOKIE_SAMESITE", "lax"))
    
    # CORS Configuration
    cors_allowed_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://app.ia-influencer-agent.com",
        "https://dashboard.ia-influencer-agent.com"
    ])
    cors_allowed_methods: List[str] = field(default_factory=lambda: 
        ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
    cors_allowed_headers: List[str] = field(default_factory=lambda: [
        "Authorization", "Content-Type", "X-API-Key", "X-Request-ID", "X-User-ID"
    ])
    cors_allow_credentials: bool = field(default_factory=lambda: 
        os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true")
    cors_max_age: int = field(default_factory=lambda: int(os.getenv("CORS_MAX_AGE", "3600")))
    
    # Authentication Configuration
    max_login_attempts: int = field(default_factory=lambda: 
        int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")))
    login_lockout_duration_minutes: int = field(default_factory=lambda: 
        int(os.getenv("LOGIN_LOCKOUT_DURATION", "30")))
    require_email_verification: bool = field(default_factory=lambda: 
        os.getenv("REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true")
    require_phone_verification: bool = field(default_factory=lambda: 
        os.getenv("REQUIRE_PHONE_VERIFICATION", "false").lower() == "true")
    enable_two_factor_auth: bool = field(default_factory=lambda: 
        os.getenv("ENABLE_TWO_FACTOR_AUTH", "true").lower() == "true")
    
    # OAuth2 Configuration
    oauth2_enabled: bool = field(default_factory=lambda: 
        os.getenv("OAUTH2_ENABLED", "true").lower() == "true")
    google_oauth_client_id: Optional[str] = field(default_factory=lambda: 
        os.getenv("GOOGLE_OAUTH_CLIENT_ID"))
    google_oauth_client_secret: Optional[str] = field(default_factory=lambda: 
        os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"))
    facebook_oauth_client_id: Optional[str] = field(default_factory=lambda: 
        os.getenv("FACEBOOK_OAUTH_CLIENT_ID"))
    facebook_oauth_client_secret: Optional[str] = field(default_factory=lambda: 
        os.getenv("FACEBOOK_OAUTH_CLIENT_SECRET"))
    github_oauth_client_id: Optional[str] = field(default_factory=lambda: 
        os.getenv("GITHUB_OAUTH_CLIENT_ID"))
    github_oauth_client_secret: Optional[str] = field(default_factory=lambda: 
        os.getenv("GITHUB_OAUTH_CLIENT_SECRET"))
    
    # API Security
    api_key_header_name: str = field(default_factory=lambda: 
        os.getenv("API_KEY_HEADER_NAME", "X-API-Key"))
    api_key_length: int = field(default_factory=lambda: int(os.getenv("API_KEY_LENGTH", "32")))
    api_key_expire_days: int = field(default_factory=lambda: int(os.getenv("API_KEY_EXPIRE_DAYS", "365")))
    enable_api_key_rotation: bool = field(default_factory=lambda: 
        os.getenv("ENABLE_API_KEY_ROTATION", "true").lower() == "true")
    
    # Rate Limiting
    rate_limit_enabled: bool = field(default_factory=lambda: 
        os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    rate_limit_requests_per_minute: int = field(default_factory=lambda: 
        int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")))
    rate_limit_requests_per_hour: int = field(default_factory=lambda: 
        int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")))
    rate_limit_requests_per_day: int = field(default_factory=lambda: 
        int(os.getenv("RATE_LIMIT_PER_DAY", "10000")))
    rate_limit_burst_size: int = field(default_factory=lambda: 
        int(os.getenv("RATE_LIMIT_BURST_SIZE", "200")))
    
    # Content Security Policy
    csp_enabled: bool = field(default_factory=lambda: 
        os.getenv("CSP_ENABLED", "true").lower() == "true")
    csp_default_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_script_src: List[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    csp_style_src: List[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    csp_img_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    csp_connect_src: List[str] = field(default_factory=lambda: ["'self'"])
    csp_report_uri: Optional[str] = field(default_factory=lambda: 
        os.getenv("CSP_REPORT_URI"))
    
    # Encryption Configuration
    encryption_algorithm: EncryptionAlgorithm = field(default_factory=lambda: 
        EncryptionAlgorithm(os.getenv("ENCRYPTION_ALGORITHM", "fernet")))
    field_encryption_enabled: bool = field(default_factory=lambda: 
        os.getenv("FIELD_ENCRYPTION_ENABLED", "true").lower() == "true")
    database_encryption_enabled: bool = field(default_factory=lambda: 
        os.getenv("DATABASE_ENCRYPTION_ENABLED", "false").lower() == "true")
    
    # File Upload Security
    max_file_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "100")))
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "audio/mpeg", "audio/wav", "audio/ogg", "audio/flac",
        "video/mp4", "video/avi", "video/mov", "video/webm",
        "text/plain", "text/csv", "application/pdf"
    ])
    virus_scan_enabled: bool = field(default_factory=lambda: 
        os.getenv("VIRUS_SCAN_ENABLED", "true").lower() == "true")
    
    # Audit and Logging
    audit_log_enabled: bool = field(default_factory=lambda: 
        os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true")
    security_log_enabled: bool = field(default_factory=lambda: 
        os.getenv("SECURITY_LOG_ENABLED", "true").lower() == "true")
    log_sensitive_data: bool = field(default_factory=lambda: 
        os.getenv("LOG_SENSITIVE_DATA", "false").lower() == "true")
    security_incident_webhook: Optional[str] = field(default_factory=lambda: 
        os.getenv("SECURITY_INCIDENT_WEBHOOK"))
    
    # Network Security
    allowed_ip_ranges: List[str] = field(default_factory=list)
    blocked_ip_ranges: List[str] = field(default_factory=list)
    geolocation_blocking_enabled: bool = field(default_factory=lambda: 
        os.getenv("GEOLOCATION_BLOCKING_ENABLED", "false").lower() == "true")
    blocked_countries: List[str] = field(default_factory=list)
    
    # Advanced Security Features
    honeypot_enabled: bool = field(default_factory=lambda: 
        os.getenv("HONEYPOT_ENABLED", "false").lower() == "true")
    intrusion_detection_enabled: bool = field(default_factory=lambda: 
        os.getenv("INTRUSION_DETECTION_ENABLED", "false").lower() == "true")
    anomaly_detection_enabled: bool = field(default_factory=lambda: 
        os.getenv("ANOMALY_DETECTION_ENABLED", "false").lower() == "true")
    
    def __post_init__(self):
        """Validate and set up security configuration"""        self._validate_configuration()
        self._setup_password_context()
        self._setup_encryption()
    
    def _validate_configuration(self):
        """Validate security configuration parameters"""        if self.jwt_access_token_expire_minutes <= 0:
            raise ValueError("JWT access token expiration must be positive")
        
        if self.jwt_refresh_token_expire_days <= 0:
            raise ValueError("JWT refresh token expiration must be positive")
        
        if self.max_login_attempts <= 0:
            raise ValueError("Max login attempts must be positive")
        
        if self.password_min_length < 6:
            raise ValueError("Password minimum length should be at least 6")
        
        if len(self.secret_key) < 32:
            raise ValueError("Secret key should be at least 32 characters")
    
    def _setup_password_context(self):
        """Set up password hashing context"""        schemes = [self.password_hash_algorithm]
        if self.password_hash_algorithm not in ["bcrypt", "pbkdf2_sha256", "argon2"]:
            schemes = ["bcrypt"]  # fallback to bcrypt
        
        self.password_context = CryptContext(
            schemes=schemes,
            deprecated="auto",
            bcrypt__rounds=12,
            pbkdf2_sha256__rounds=100000,
            argon2__time_cost=2,
            argon2__memory_cost=512,
            argon2__parallelism=2
        )
    
    def _setup_encryption(self):
        """Set up encryption context"""        if self.encryption_algorithm == EncryptionAlgorithm.FERNET:
            # Ensure the encryption key is properly formatted for Fernet
            try:
                key_bytes = self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key
                self.cipher_suite = Fernet(key_bytes)
            except Exception:
                # Generate new key if current one is invalid
                self.encryption_key = Fernet.generate_key().decode()
                self.cipher_suite = Fernet(self.encryption_key.encode())
    
    @property
    def jwt_access_token_expire_delta(self) -> timedelta:
        """Get JWT access token expiration as timedelta"""        return timedelta(minutes=self.jwt_access_token_expire_minutes)
    
    @property
    def jwt_refresh_token_expire_delta(self) -> timedelta:
        """Get JWT refresh token expiration as timedelta"""        return timedelta(days=self.jwt_refresh_token_expire_days)
    
    @property
    def session_timeout_delta(self) -> timedelta:
        """Get session timeout as timedelta"""        return timedelta(minutes=self.session_timeout_minutes)
    
    @property
    def login_lockout_delta(self) -> timedelta:
        """Get login lockout duration as timedelta"""        return timedelta(minutes=self.login_lockout_duration_minutes)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using configured algorithm"""        return self.password_context.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""        return self.password_context.verify(password, hashed)
    
    def encrypt_data(self, data: str) -> str:
        """        Encrypt sensitive data using the configured encryption algorithm.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            str: Encrypted data as string
        """        try:
            if self.encryption_algorithm == EncryptionAlgorithm.FERNET:
                return self.cipher_suite.encrypt(data.encode()).decode()
            elif self.encryption_algorithm == EncryptionAlgorithm.AES_256:
                return self._encrypt_aes_256(data)
            elif self.encryption_algorithm == EncryptionAlgorithm.RSA_2048:
                return self._encrypt_rsa(data, 2048)
            elif self.encryption_algorithm == EncryptionAlgorithm.RSA_4096:
                return self._encrypt_rsa(data, 4096)
            else:
                # Fallback to Fernet for unknown algorithms
                self.logger.warning(f"Unknown encryption algorithm {self.encryption_algorithm}, falling back to Fernet")
                return self.cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise ValueError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """        Decrypt data using the configured encryption algorithm.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            str: Decrypted plain text data
        """        try:
            if self.encryption_algorithm == EncryptionAlgorithm.FERNET:
                return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
            elif self.encryption_algorithm == EncryptionAlgorithm.AES_256:
                return self._decrypt_aes_256(encrypted_data)
            elif self.encryption_algorithm == EncryptionAlgorithm.RSA_2048:
                return self._decrypt_rsa(encrypted_data, 2048)
            elif self.encryption_algorithm == EncryptionAlgorithm.RSA_4096:
                return self._decrypt_rsa(encrypted_data, 4096)
            else:
                # Fallback to Fernet for unknown algorithms
                self.logger.warning(f"Unknown encryption algorithm {self.encryption_algorithm}, falling back to Fernet")
                return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def _encrypt_aes_256(self, data: str) -> str:
        """Encrypt data using AES-256"""        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            import base64
            
            # Generate a random IV
            iv = os.urandom(16)
            
            # Create cipher
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Pad data to multiple of 16 bytes
            padded_data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
            
            # Encrypt
            encrypted = encryptor.update(padded_data.encode()) + encryptor.finalize()
            
            # Return IV + encrypted data, base64 encoded
            return base64.b64encode(iv + encrypted).decode()
            
        except Exception as e:
            self.logger.error(f"AES-256 encryption failed: {str(e)}")
            # Fallback to Fernet
            return self.cipher_suite.encrypt(data.encode()).decode()
    
    def _decrypt_aes_256(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256"""        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            import base64
            
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Extract IV and encrypted data
            iv = encrypted_bytes[:16]
            encrypted = encrypted_bytes[16:]
            
            # Create cipher
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # Decrypt
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            
            # Remove padding
            padding_length = decrypted[-1]
            return decrypted[:-padding_length].decode()
            
        except Exception as e:
            self.logger.error(f"AES-256 decryption failed: {str(e)}")
            # Fallback to Fernet
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def _encrypt_rsa(self, data: str, key_size: int) -> str:
        """Encrypt data using RSA"""        try:
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            from cryptography.hazmat.primitives import hashes, serialization
            import base64
            
            # For RSA, we'll use hybrid encryption (RSA for key, AES for data)
            # This is a simplified implementation
            
            # Generate ephemeral RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            public_key = private_key.public_key()
            
            # For demo purposes, use a simple encryption scheme
            # In production, implement proper hybrid encryption
            data_bytes = data.encode()
            
            # If data is too long for RSA, use AES-256 fallback
            if len(data_bytes) > (key_size // 8) - 42:  # RSA padding overhead
                return self._encrypt_aes_256(data)
            
            # Encrypt with RSA
            encrypted = public_key.encrypt(
                data_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Store both private key and encrypted data (for demo)
            # In production, you'd have proper key management
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            result = {
                'encrypted_data': base64.b64encode(encrypted).decode(),
                'key': base64.b64encode(key_pem).decode()
            }
            
            return base64.b64encode(str(result).encode()).decode()
            
        except Exception as e:
            self.logger.error(f"RSA encryption failed: {str(e)}")
            # Fallback to AES-256
            return self._encrypt_aes_256(data)
    
    def _decrypt_rsa(self, encrypted_data: str, key_size: int) -> str:
        """Decrypt data using RSA"""        try:
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes, serialization
            import base64
            import ast
            
            # Decode the result structure
            result_str = base64.b64decode(encrypted_data.encode()).decode()
            result = ast.literal_eval(result_str)
            
            # Extract encrypted data and key
            encrypted_bytes = base64.b64decode(result['encrypted_data'].encode())
            key_pem = base64.b64decode(result['key'].encode())
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                key_pem,
                password=None,
            )
            
            # Decrypt
            decrypted = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted.decode()
            
        except Exception as e:
            self.logger.error(f"RSA decryption failed: {str(e)}")
            # Try AES-256 fallback
            return self._decrypt_aes_256(encrypted_data)
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""        return secrets.token_urlsafe(self.api_key_length)
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""        return secrets.token_urlsafe(32)
    
    def create_hmac_signature(self, data: str) -> str:
        """Create HMAC signature for data integrity"""        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC signature"""        expected_signature = self.create_hmac_signature(data)
        return hmac.compare_digest(signature, expected_signature)
    
    def validate_password_strength(self, password: str) -> Dict[str, bool]:
        """Validate password against security requirements"""        validations = {
            'min_length': len(password) >= self.password_min_length,
            'has_uppercase': any(c.isupper() for c in password) if self.password_require_uppercase else True,
            'has_lowercase': any(c.islower() for c in password) if self.password_require_lowercase else True,
            'has_numbers': any(c.isdigit() for c in password) if self.password_require_numbers else True,
            'has_special': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password) if self.password_require_special else True
        }
        
        return validations
    
    def is_password_valid(self, password: str) -> bool:
        """Check if password meets all security requirements"""        validations = self.validate_password_strength(password)
        return all(validations.values())
    
    def get_csp_header(self) -> str:
        """Generate Content Security Policy header"""        if not self.csp_enabled:
            return ""
        
        policies = [
            f"default-src {' '.join(self.csp_default_src)}",
            f"script-src {' '.join(self.csp_script_src)}",
            f"style-src {' '.join(self.csp_style_src)}",
            f"img-src {' '.join(self.csp_img_src)}",
            f"connect-src {' '.join(self.csp_connect_src)}"
        ]
        
        if self.csp_report_uri:
            policies.append(f"report-uri {self.csp_report_uri}")
        
        return "; ".join(policies)
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers"""        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        if self.csp_enabled:
            headers["Content-Security-Policy"] = self.get_csp_header()
        
        return headers
    
    def is_file_type_allowed(self, content_type: str) -> bool:
        """Check if file type is allowed for upload"""        return content_type in self.allowed_file_types
    
    def get_oauth_config(self, provider: str) -> Optional[Dict[str, str]]:
        """Get OAuth configuration for specific provider"""        oauth_configs = {
            "google": {
                "client_id": self.google_oauth_client_id,
                "client_secret": self.google_oauth_client_secret
            },
            "facebook": {
                "client_id": self.facebook_oauth_client_id,
                "client_secret": self.facebook_oauth_client_secret
            },
            "github": {
                "client_id": self.github_oauth_client_id,
                "client_secret": self.github_oauth_client_secret
            }
        }
        
        config = oauth_configs.get(provider)
        if config and config["client_id"] and config["client_secret"]:
            return config
        return None
