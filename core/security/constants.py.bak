"""Security Constants Module
Security-related constants and configurations for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""from typing import Dict, List, Set, Tuple
import re

# =============================================================================
# AUTHENTICATION CONSTANTS
# =============================================================================

# JWT Configuration
JWT_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]
DEFAULT_JWT_ALGORITHM = "HS256"
JWT_TOKEN_PREFIX = "Bearer"
JWT_HEADER_NAME = "Authorization"

# Token Expiration Times (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 10080  # 7 days
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15
EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# OAuth2 Providers
OAUTH2_PROVIDERS = {
    "spotify": {
        "authorize_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "scope": "user-read-email user-read-private user-library-read playlist-read-private"
    },
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "openid email profile"
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scope": "user:email"
    },
    "discord": {
        "authorize_url": "https://discord.com/api/oauth2/authorize",
        "token_url": "https://discord.com/api/oauth2/token",
        "scope": "identify email"
    }
}

# Password Requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = True
PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

# Password Validation Regex
PASSWORD_PATTERNS = {
    "uppercase": re.compile(r'[A-Z]'),
    "lowercase": re.compile(r'[a-z]'),
    "numbers": re.compile(r'\d'),
    "special": re.compile(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]'),
    "no_whitespace": re.compile(r'^\S+$')
}

# Common weak passwords (partial list for demonstration)
WEAK_PASSWORDS = {
    "password", "123456", "password123", "admin", "qwerty", "letmein",
    "welcome", "monkey", "dragon", "master", "shadow", "12345678",
    "football", "baseball", "superman", "batman", "trustno1", "hello"
}

# =============================================================================
# ENCRYPTION CONSTANTS
# =============================================================================

# Encryption Algorithms
ENCRYPTION_ALGORITHMS = {
    "AES_256_GCM": {
        "key_size": 32,  # 256 bits
        "iv_size": 12,   # 96 bits for GCM
        "tag_size": 16   # 128 bits
    },
    "AES_256_CBC": {
        "key_size": 32,  # 256 bits
        "iv_size": 16,   # 128 bits
        "padding": "PKCS7"
    },
    "CHACHA20_POLY1305": {
        "key_size": 32,  # 256 bits
        "nonce_size": 12 # 96 bits
    },
    "RSA_OAEP_4096": {
        "key_size": 4096,
        "padding": "OAEP",
        "hash": "SHA256"
    }
}

# Key Derivation
PBKDF2_ITERATIONS = 100000  # Minimum recommended by OWASP
SCRYPT_N = 32768           # CPU/memory cost parameter
SCRYPT_R = 8               # Block size parameter
SCRYPT_P = 1               # Parallelization parameter
ARGON2_TIME_COST = 3       # Number of iterations
ARGON2_MEMORY_COST = 65536 # Memory usage in KiB
ARGON2_PARALLELISM = 4     # Number of parallel threads

# Salt sizes
SALT_SIZE = 32  # 256 bits
NONCE_SIZE = 12 # 96 bits for GCM
IV_SIZE = 16    # 128 bits for CBC

# =============================================================================
# CONTENT PROTECTION CONSTANTS
# =============================================================================

# Supported Content Types
SUPPORTED_CONTENT_TYPES = {
    "audio": [
        "audio/mpeg", "audio/mp3", "audio/wav", "audio/flac", "audio/aac",
        "audio/ogg", "audio/webm", "audio/m4a", "audio/wma"
    ],
    "video": [
        "video/mp4", "video/avi", "video/mov", "video/wmv", "video/flv",
        "video/webm", "video/mkv", "video/m4v", "video/3gp"
    ],
    "image": [
        "image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp",
        "image/webp", "image/tiff", "image/svg+xml"
    ],
    "text": [
        "text/plain", "text/html", "text/css", "text/javascript",
        "application/json", "application/xml", "text/markdown"
    ],
    "document": [
        "application/pdf", "application/msword", "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint", "application/rtf"
    ]
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    "audio": 100 * 1024 * 1024,      # 100 MB
    "video": 1024 * 1024 * 1024,     # 1 GB
    "image": 50 * 1024 * 1024,       # 50 MB
    "text": 10 * 1024 * 1024,         # 10 MB
    "document": 100 * 1024 * 1024,   # 100 MB
    "default": 100 * 1024 * 1024     # 100 MB
}

# Fingerprinting algorithms
FINGERPRINT_ALGORITHMS = {
    "audio": ["chromaprint", "essentia", "pyaudio_analysis"],
    "video": ["opencv_hash", "perceptual_hash", "video_signature"],
    "image": ["phash", "dhash", "ahash", "whash", "clip_embedding"],
    "text": ["tfidf", "bert_embedding", "hash_fingerprint"]
}

# Watermark types
WATERMARK_TYPES = {
    "visible": ["text_overlay", "logo_overlay", "timestamp"],
    "invisible": ["lsb_embedding", "dct_embedding", "frequency_domain"],
    "audio": ["echo_hiding", "phase_coding", "spread_spectrum"],
    "video": ["frame_embedding", "motion_vector_embedding"]
}

# =============================================================================
# SECURITY MONITORING CONSTANTS
# =============================================================================

# Threat Levels
THREAT_LEVELS = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
    "EMERGENCY": 5
}

# Event Categories
SECURITY_EVENT_CATEGORIES = {
    "authentication": [
        "login_success", "login_failure", "logout", "password_change",
        "mfa_enabled", "mfa_disabled", "account_locked", "account_unlocked"
    ],
    "authorization": [
        "permission_granted", "permission_denied", "role_changed",
        "privilege_escalation", "unauthorized_access"
    ],
    "content": [
        "content_uploaded", "content_downloaded", "content_modified",
        "content_deleted", "fingerprint_match", "copyright_violation"
    ],
    "system": [
        "system_startup", "system_shutdown", "configuration_changed",
        "service_started", "service_stopped", "error_occurred"
    ],
    "security": [
        "intrusion_detected", "malware_found", "suspicious_activity",
        "ddos_attack", "brute_force_attack", "data_breach"
    ]
}

# Anomaly Detection Thresholds
ANOMALY_THRESHOLDS = {
    "login_attempts_per_minute": 10,
    "failed_logins_per_hour": 50,
    "api_requests_per_minute": 1000,
    "data_transfer_rate_mbps": 100,
    "concurrent_sessions_per_user": 5,
    "file_upload_rate_per_minute": 20,
    "content_modification_rate": 0.1  # 10% of content modified
}

# =============================================================================
# API SECURITY CONSTANTS
# =============================================================================

# Rate Limiting
RATE_LIMIT_DEFAULTS = {
    "requests_per_minute": 100,
    "requests_per_hour": 5000,
    "requests_per_day": 100000,
    "burst_size": 200,
    "window_size": 60  # seconds
}

# Rate limit by endpoint type
ENDPOINT_RATE_LIMITS = {
    "auth": {"requests_per_minute": 10, "burst_size": 20},
    "upload": {"requests_per_minute": 5, "burst_size": 10},
    "download": {"requests_per_minute": 50, "burst_size": 100},
    "search": {"requests_per_minute": 200, "burst_size": 400},
    "analytics": {"requests_per_minute": 100, "burst_size": 200}
}

# DDoS Protection
DDOS_PROTECTION_THRESHOLDS = {
    "requests_per_second": 100,
    "concurrent_connections": 1000,
    "bandwidth_mbps": 100,
    "packet_rate_pps": 10000,
    "tcp_syn_rate": 100,
    "udp_packet_rate": 1000
}

# Bot Detection Patterns
BOT_USER_AGENTS = [
    r".*bot.*", r".*crawler.*", r".*spider.*", r".*scraper.*",
    r".*harvester.*", r".*extractor.*", r".*monitor.*", r".*scanner.*"
]

# Suspicious IP Patterns
SUSPICIOUS_IP_PATTERNS = [
    # TOR exit nodes pattern
    r"^192\.42\.116\.",
    # Known VPN ranges (partial list)
    r"^185\.220\.",
    # Cloud provider ranges that might be misused
    r"^54\..*",  # AWS
    r"^34\..*",  # GCP
]

# =============================================================================
# COMPLIANCE CONSTANTS
# =============================================================================

# GDPR Article References
GDPR_ARTICLES = {
    "lawful_basis": "Article 6",
    "consent": "Article 7",
    "children": "Article 8",
    "data_subject_rights": "Articles 15-22",
    "right_to_erasure": "Article 17",
    "data_portability": "Article 20",
    "data_protection_impact": "Article 35",
    "breach_notification": "Articles 33-34"
}

# Data Retention Periods (in days)
DATA_RETENTION_PERIODS = {
    "user_data": 2555,        # 7 years
    "audit_logs": 2555,       # 7 years
    "session_data": 30,       # 30 days
    "temporary_files": 7,     # 7 days
    "error_logs": 365,        # 1 year
    "access_logs": 90,        # 90 days
    "security_events": 2555,  # 7 years
    "financial_data": 2555    # 7 years
}

# DMCA Contact Information Template
DMCA_CONTACT_TEMPLATE = {
    "designated_agent": "DMCA Agent",
    "address": "Company Address",
    "phone": "Company Phone",
    "email": "dmca@company.com",
    "fax": "Company Fax"
}

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Input Validation Patterns
VALIDATION_PATTERNS = {
    "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    "phone": re.compile(r'^\+?[1-9]\d{1,14}$'),
    "url": re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'),
    "username": re.compile(r'^[a-zA-Z0-9_]{3,20}$'),
    "uuid": re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE),
    "ip_address": re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
    "date_iso": re.compile(r'^\d{4}-\d{2}-\d{2}$'),
    "time_iso": re.compile(r'^\d{2}:\d{2}:\d{2}$'),
    "datetime_iso": re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})$')
}

# Dangerous File Extensions
DANGEROUS_EXTENSIONS = {
    "executable": [".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],  # Can contain malware
    "script": [".php", ".asp", ".jsp", ".py", ".pl", ".rb", ".sh"],
    "office_macro": [".doc", ".xls", ".ppt", ".docm", ".xlsm", ".pptm"]
}

# Magic Number Validation (first few bytes of files)
FILE_MAGIC_NUMBERS = {
    "pdf": b"%PDF",
    "jpg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "gif": b"GIF8",
    "zip": b"PK\x03\x04",
    "mp3": b"ID3",
    "mp4": b"\x00\x00\x00\x20ftypmp4",
    "avi": b"RIFF",
    "wav": b"RIFF"
}

# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES = {
    # Authentication Errors
    "INVALID_CREDENTIALS": "Invalid email or password",
    "ACCOUNT_LOCKED": "Account is locked due to too many failed login attempts",
    "TOKEN_EXPIRED": "Authentication token has expired",
    "TOKEN_INVALID": "Invalid authentication token",
    "MFA_REQUIRED": "Multi-factor authentication is required",
    "MFA_INVALID": "Invalid MFA token",
    
    # Authorization Errors
    "PERMISSION_DENIED": "You don't have permission to perform this action",
    "RESOURCE_NOT_FOUND": "Requested resource not found",
    "INSUFFICIENT_PRIVILEGES": "Insufficient privileges for this operation",
    
    # Validation Errors
    "INVALID_FILE_TYPE": "File type not supported",
    "FILE_TOO_LARGE": "File size exceeds maximum limit",
    "MALWARE_DETECTED": "Malware detected in uploaded file",
    "CONTENT_VALIDATION_FAILED": "Content validation failed",
    
    # Rate Limiting Errors
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please try again later",
    "TOO_MANY_REQUESTS": "Too many requests. Please slow down",
    
    # General Security Errors
    "SECURITY_VIOLATION": "Security policy violation detected",
    "SUSPICIOUS_ACTIVITY": "Suspicious activity detected",
    "ACCESS_DENIED": "Access denied"
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================

DEFAULT_SECURITY_FEATURES = {
    # Authentication Features
    "multi_factor_auth": True,
    "oauth2_integration": True,
    "session_management": True,
    "password_policies": True,
    
    # Content Protection Features
    "content_fingerprinting": True,
    "watermarking": True,
    "copyright_protection": True,
    "anti_tamper": True,
    
    # Security Monitoring Features
    "threat_detection": True,
    "anomaly_detection": True,
    "audit_logging": True,
    "real_time_monitoring": True,
    
    # API Security Features
    "rate_limiting": True,
    "ddos_protection": True,
    "bot_detection": True,
    "geo_blocking": False,
    
    # Compliance Features
    "gdpr_compliance": True,
    "ccpa_compliance": True,
    "dmca_compliance": True,
    "data_retention": True,
    
    # Validation Features
    "malware_scanning": True,
    "content_validation": True,
    "input_sanitization": True,
    "file_type_validation": True
}
