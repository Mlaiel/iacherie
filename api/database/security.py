"""Database Security Management - IA Influencer Agent Platform
Enterprise-grade security features for database access and data protection

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
import hashlib
import hmac
import secrets
import base64
import uuid
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import logging
import re
from contextlib import asynccontextmanager

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import bcrypt
import jwt
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.logging import get_logger
from .connection import DatabaseConnection, SessionManager

logger = get_logger(__name__)
settings = get_settings()


class SecurityLevel(Enum):
    """Security level enumeration"""    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class AccessType(Enum):
    """Database access type enumeration"""    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_4096 = "rsa_4096"
    FERNET = "fernet"
    BCRYPT = "bcrypt"


@dataclass
class SecurityPolicy:
    """Database security policy configuration"""    name: str
    description: str
    min_password_length: int = 12
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True
    require_lowercase: bool = True
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_expiry_days: int = 90
    session_timeout_minutes: int = 60
    require_2fa: bool = False
    allowed_ip_ranges: List[str] = field(default_factory=list)
    encryption_required: bool = True
    audit_required: bool = True
    data_retention_days: int = 2555  # 7 years default
    anonymization_required: bool = False


@dataclass
class AccessPermission:
    """Database access permission"""    user_id: str
    resource_type: str  # table, view, function, etc.
    resource_name: str
    access_types: List[AccessType]
    security_level: SecurityLevel
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)  # Additional conditions


@dataclass
class AuditEvent:
    """Database audit event"""    event_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    action: str
    resource_type: str
    resource_name: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result_count: Optional[int] = None
    execution_time_ms: Optional[float] = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    success: bool = True
    error_message: Optional[str] = None


class DatabaseEncryption:
    """Database field-level encryption service"""    
    def __init__(self):
        self.encryption_keys: Dict[str, bytes] = {}
        self.active_key_id: Optional[str] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize encryption service"""        if self._initialized:
            return
        
        try:
            # Generate or load master encryption key
            master_key = self._get_or_create_master_key()
            
            # Create default encryption key
            key_id = str(uuid.uuid4())
            self.encryption_keys[key_id] = master_key
            self.active_key_id = key_id
            
            self._initialized = True
            logger.info("Database encryption service initialized")
            
        except Exception as e:
            logger.error(f"Encryption service initialization failed: {e}")
            raise
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""        # In production, this should be retrieved from a secure key management service
        master_key_setting = getattr(settings, 'DATABASE_ENCRYPTION_KEY', None)
        
        if master_key_setting:
            return base64.b64decode(master_key_setting.encode())
        
        # Generate new key (should be stored securely)
        key = Fernet.generate_key()
        logger.warning("Generated new encryption key - store this securely!")
        logger.warning(f"DATABASE_ENCRYPTION_KEY={key.decode()}")
        
        return key
    
    def encrypt_field(self, 
                     value: str, 
                     algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET,
                     key_id: Optional[str] = None) -> str:
        """Encrypt a field value"""        if not self._initialized:
            raise RuntimeError("Encryption service not initialized")
        
        if value is None:
            return None
        
        try:
            key_id = key_id or self.active_key_id
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key {key_id} not found")
            
            encryption_key = self.encryption_keys[key_id]
            
            if algorithm == EncryptionAlgorithm.FERNET:
                f = Fernet(encryption_key)
                encrypted_bytes = f.encrypt(value.encode('utf-8'))
                
                # Return with key ID prefix for key rotation support
                return f"{key_id}:{base64.b64encode(encrypted_bytes).decode()}"
            
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                # Implement AES-256-GCM encryption
                return self._encrypt_aes_256_gcm(value, encryption_key, key_id)
            
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Field encryption failed: {e}")
            raise
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a field value using the appropriate algorithm"""        if not self._initialized:
            raise RuntimeError("Encryption service not initialized")
        
        if not encrypted_value:
            return encrypted_value
        
        try:
            # Extract key ID and encrypted data
            if ':' in encrypted_value:
                key_id, encrypted_data = encrypted_value.split(':', 1)
            else:
                # Legacy format without key ID
                key_id = self.active_key_id
                encrypted_data = encrypted_value
            
            if key_id not in self.encryption_keys:
                raise ValueError(f"Decryption key {key_id} not found")
            
            encryption_key = self.encryption_keys[key_id]
            
            # Try to determine algorithm by the encrypted data format
            # AES-256-GCM will have longer data due to nonce + ciphertext
            # Fernet has a specific format we can detect
            
            try:
                # First try Fernet decryption (most common)
                f = Fernet(encryption_key)
                encrypted_bytes = base64.b64decode(encrypted_data.encode())
                decrypted_bytes = f.decrypt(encrypted_bytes)
                return decrypted_bytes.decode('utf-8')
                
            except Exception:
                # If Fernet fails, try AES-256-GCM
                try:
                    return self._decrypt_aes_256_gcm(encrypted_data, encryption_key)
                except Exception:
                    # If both fail, raise the original error
                    raise ValueError("Unable to decrypt data with available algorithms")
            
        except Exception as e:
            logger.error(f"Field decryption failed: {e}")
            raise
    
    def rotate_encryption_key(self) -> str:
        """Rotate encryption key and return new key ID"""        new_key_id = str(uuid.uuid4())
        new_key = Fernet.generate_key()
        
        self.encryption_keys[new_key_id] = new_key
        self.active_key_id = new_key_id
        
        logger.info(f"Encryption key rotated: new key ID {new_key_id}")
        
        return new_key_id
    
    def get_encrypted_columns(self, table_name: str) -> List[str]:
        """Get list of encrypted columns for a table"""        # This should be configured based on your schema
        # For now, return common sensitive field names
        sensitive_fields = [
            'password', 'email', 'phone', 'ssn', 'credit_card',
            'bank_account', 'api_key', 'secret', 'token'
        ]
        
        return sensitive_fields
    
    def _encrypt_aes_256_gcm(self, value: str, encryption_key: bytes, key_id: str) -> str:
        """        Encrypt field value using AES-256-GCM encryption.
        
        Args:
            value: Plain text value to encrypt
            encryption_key: Encryption key bytes
            key_id: Key identifier for rotation support
            
        Returns:
            str: Encrypted value with key ID prefix
        """        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            import os
            import base64
            
            # Generate a random 96-bit (12 byte) nonce for GCM
            nonce = os.urandom(12)
            
            # Create AESGCM instance with 256-bit key
            # Ensure key is exactly 32 bytes (256 bits)
            if len(encryption_key) != 32:
                key_hash = hashlib.sha256(encryption_key).digest()
            else:
                key_hash = encryption_key
            
            aesgcm = AESGCM(key_hash)
            
            # Encrypt the value
            ciphertext = aesgcm.encrypt(nonce, value.encode('utf-8'), None)
            
            # Combine nonce and ciphertext
            encrypted_data = nonce + ciphertext
            
            # Encode to base64 and add key ID prefix
            encrypted_b64 = base64.b64encode(encrypted_data).decode()
            return f"{key_id}:{encrypted_b64}"
            
        except Exception as e:
            logger.error(f"AES-256-GCM encryption failed: {e}")
            # Fallback to Fernet encryption
            f = Fernet(base64.urlsafe_b64encode(hashlib.sha256(encryption_key).digest()))
            encrypted_bytes = f.encrypt(value.encode('utf-8'))
            return f"{key_id}:{base64.b64encode(encrypted_bytes).decode()}"
    
    def _decrypt_aes_256_gcm(self, encrypted_value: str, encryption_key: bytes) -> str:
        """        Decrypt field value using AES-256-GCM decryption.
        
        Args:
            encrypted_value: Base64 encoded encrypted value
            encryption_key: Decryption key bytes
            
        Returns:
            str: Decrypted plain text value
        """        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            import base64
            
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_value.encode())
            
            # Extract nonce (first 12 bytes) and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # Create AESGCM instance with 256-bit key
            if len(encryption_key) != 32:
                key_hash = hashlib.sha256(encryption_key).digest()
            else:
                key_hash = encryption_key
            
            aesgcm = AESGCM(key_hash)
            
            # Decrypt the ciphertext
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"AES-256-GCM decryption failed: {e}")
            # Fallback to Fernet decryption
            f = Fernet(base64.urlsafe_b64encode(hashlib.sha256(encryption_key).digest()))
            return f.decrypt(base64.b64decode(encrypted_value.encode())).decode('utf-8')


class PasswordSecurity:
    """Password security and hashing utilities"""    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password"""        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str, policy: SecurityPolicy) -> Tuple[bool, List[str]]:
        """Validate password against security policy"""        issues = []
        
        if len(password) < policy.min_password_length:
            issues.append(f"Password must be at least {policy.min_password_length} characters long")
        
        if policy.require_lowercase and not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if policy.require_uppercase and not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if policy.require_numbers and not re.search(r'\d', password):
            issues.append("Password must contain at least one number")
        
        if policy.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        
        return len(issues) == 0, issues


class QuerySanitizer:
    """SQL injection prevention and query sanitization"""    
    DANGEROUS_PATTERNS = [
        r'(union\s+select)',
        r'(drop\s+table)',
        r'(delete\s+from)',
        r'(insert\s+into)',
        r'(update\s+set)',
        r'(alter\s+table)',
        r'(create\s+table)',
        r'(exec\s*\()',
        r'(execute\s*\()',
        r'(sp_executesql)',
        r'(xp_cmdshell)',
        r'(\bor\b.*\s*=\s*\d)',
        r'(\band\b.*\s*=\s*\d)',
        r'(--)',
        r'(/\*.*\*/)',
        r'(\bselect\b.*\bfrom\b.*\bwhere\b.*\bor\b.*=)',
    ]
    
    @classmethod
    def is_safe_query(cls, query: str) -> Tuple[bool, List[str]]:
        """Check if query is safe from SQL injection"""        issues = []
        query_lower = query.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                issues.append(f"Potentially dangerous pattern detected: {pattern}")
        
        return len(issues) == 0, issues
    
    @classmethod
    def sanitize_identifier(cls, identifier: str) -> str:
        """Sanitize database identifier (table name, column name)"""        # Remove dangerous characters and limit length
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', identifier)
        return sanitized[:64]  # Limit to 64 characters
    
    @classmethod
    def escape_string_value(cls, value: str) -> str:
        """Escape string value for safe SQL usage"""        # This is basic escaping - always prefer parameterized queries
        return value.replace("'", "''").replace('"', '""')


class DatabaseAuditor:
    """Database activity auditing service"""    
    def __init__(self):
        self.audit_events: List[AuditEvent] = []
        self.session_manager = SessionManager()
        self.encryption = DatabaseEncryption()
        self._audit_enabled = True
        self._retention_days = 2555  # 7 years
    
    async def initialize(self):
        """Initialize audit service"""        await self.encryption.initialize()
        self._setup_database_event_listeners()
        logger.info("Database auditor initialized")
    
    def _setup_database_event_listeners(self):
        """Setup SQLAlchemy event listeners for auditing"""        @event.listens_for(Session, 'before_cursor_execute', named=True)
        def receive_before_cursor_execute(**kw):
            if self._audit_enabled:
                self._on_before_execute(kw.get('statement'), kw.get('parameters'))
        
        @event.listens_for(Session, 'after_cursor_execute', named=True)
        def receive_after_cursor_execute(**kw):
            if self._audit_enabled:
                self._on_after_execute(kw.get('statement'), kw.get('parameters'))
    
    def _on_before_execute(self, statement: str, parameters: Any):
        """Handle before query execution"""        # Log query start - could be used for performance monitoring
        pass
    
    def _on_after_execute(self, statement: str, parameters: Any):
        """Handle after query execution"""        try:
            # Create audit event
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                user_id=self._get_current_user_id(),
                session_id=self._get_current_session_id(),
                action=self._extract_action_from_statement(statement),
                resource_type='table',
                resource_name=self._extract_table_from_statement(statement),
                timestamp=datetime.utcnow(),
                query=statement[:1000] if statement else None,  # Limit query size
                parameters=self._sanitize_parameters(parameters)
            )
            
            self.audit_events.append(event)
            
        except Exception as e:
            logger.error(f"Audit event creation failed: {e}")
    
    def _get_current_user_id(self) -> Optional[str]:
        """Get current user ID from context"""        # This should be implemented based on your authentication system
        return None
    
    def _get_current_session_id(self) -> Optional[str]:
        """Get current session ID from context"""        # This should be implemented based on your session management
        return None
    
    def _extract_action_from_statement(self, statement: str) -> str:
        """Extract action type from SQL statement"""        if not statement:
            return 'unknown'
        
        statement_lower = statement.lower().strip()
        
        if statement_lower.startswith('select'):
            return 'select'
        elif statement_lower.startswith('insert'):
            return 'insert'
        elif statement_lower.startswith('update'):
            return 'update'
        elif statement_lower.startswith('delete'):
            return 'delete'
        elif statement_lower.startswith('create'):
            return 'create'
        elif statement_lower.startswith('alter'):
            return 'alter'
        elif statement_lower.startswith('drop'):
            return 'drop'
        else:
            return 'other'
    
    def _extract_table_from_statement(self, statement: str) -> str:
        """Extract table name from SQL statement"""        if not statement:
            return 'unknown'
        
        # Basic table name extraction - could be improved with SQL parsing
        statement_lower = statement.lower()
        
        patterns = [
            r'from\s+(\w+)',
            r'into\s+(\w+)',
            r'update\s+(\w+)',
            r'table\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, statement_lower)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def _sanitize_parameters(self, parameters: Any) -> Optional[Dict[str, Any]]:
        """Sanitize parameters for audit logging"""        if not parameters:
            return None
        
        if isinstance(parameters, dict):
            # Remove sensitive data from parameters
            sanitized = {}
            sensitive_keys = ['password', 'secret', 'token', 'key', 'api_key']
            
            for key, value in parameters.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = str(value)[:100]  # Limit value size
            
            return sanitized
        
        return {'params': str(parameters)[:100]}
    
    async def log_security_event(self, 
                               event_type: str,
                               user_id: Optional[str],
                               description: str,
                               severity: SecurityLevel = SecurityLevel.INTERNAL,
                               metadata: Optional[Dict[str, Any]] = None):
        """Log a security-related event"""        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=self._get_current_session_id(),
            action=event_type,
            resource_type='security',
            resource_name='system',
            timestamp=datetime.utcnow(),
            security_level=severity,
            query=description
        )
        
        if metadata:
            event.parameters = metadata
        
        self.audit_events.append(event)
        
        # Log high-severity events immediately
        if severity in [SecurityLevel.RESTRICTED, SecurityLevel.TOP_SECRET]:
            logger.warning(f"SECURITY EVENT: {event_type} - {description}")
    
    async def get_audit_trail(self, 
                            user_id: Optional[str] = None,
                            resource_name: Optional[str] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            limit: int = 1000) -> List[AuditEvent]:
        """Get audit trail with filtering"""        filtered_events = self.audit_events
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if resource_name:
            filtered_events = [e for e in filtered_events if e.resource_name == resource_name]
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
        
        # Sort by timestamp descending
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_events[:limit]
    
    async def cleanup_old_audit_events(self):
        """Clean up old audit events based on retention policy"""        cutoff_date = datetime.utcnow() - timedelta(days=self._retention_days)
        
        initial_count = len(self.audit_events)
        self.audit_events = [e for e in self.audit_events if e.timestamp >= cutoff_date]
        
        removed_count = initial_count - len(self.audit_events)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old audit events")
        
        return removed_count


class AccessControlManager:
    """Database access control and authorization"""    
    def __init__(self):
        self.permissions: Dict[str, List[AccessPermission]] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.locked_users: Dict[str, datetime] = {}
    
    async def initialize(self):
        """Initialize access control manager"""        # Setup default security policies
        self.security_policies['default'] = SecurityPolicy(
            name='Default Security Policy',
            description='Standard security policy for regular users'
        )
        
        self.security_policies['admin'] = SecurityPolicy(
            name='Admin Security Policy',
            description='Enhanced security policy for administrators',
            min_password_length=16,
            require_2fa=True,
            session_timeout_minutes=30,
            max_failed_attempts=3
        )
        
        logger.info("Access control manager initialized")
    
    async def grant_permission(self, permission: AccessPermission) -> bool:
        """Grant database permission to user"""        try:
            if permission.user_id not in self.permissions:
                self.permissions[permission.user_id] = []
            
            # Check if permission already exists
            existing = self._find_existing_permission(
                permission.user_id, 
                permission.resource_type, 
                permission.resource_name
            )
            
            if existing:
                # Update existing permission
                existing.access_types = permission.access_types
                existing.security_level = permission.security_level
                existing.expires_at = permission.expires_at
            else:
                # Add new permission
                self.permissions[permission.user_id].append(permission)
            
            logger.info(f"Permission granted to {permission.user_id} for {permission.resource_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant permission: {e}")
            return False
    
    async def revoke_permission(self, 
                              user_id: str, 
                              resource_type: str, 
                              resource_name: str) -> bool:
        """Revoke database permission from user"""        try:
            if user_id not in self.permissions:
                return False
            
            original_count = len(self.permissions[user_id])
            
            self.permissions[user_id] = [
                p for p in self.permissions[user_id]
                if not (p.resource_type == resource_type and p.resource_name == resource_name)
            ]
            
            removed_count = original_count - len(self.permissions[user_id])
            
            if removed_count > 0:
                logger.info(f"Revoked {removed_count} permissions from {user_id} for {resource_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False
    
    async def check_permission(self, 
                             user_id: str, 
                             resource_type: str, 
                             resource_name: str, 
                             access_type: AccessType) -> bool:
        """Check if user has permission for resource access"""        try:
            # Check if user is locked
            if self._is_user_locked(user_id):
                logger.warning(f"Access denied for locked user: {user_id}")
                return False
            
            if user_id not in self.permissions:
                return False
            
            current_time = datetime.utcnow()
            
            for permission in self.permissions[user_id]:
                if (permission.resource_type == resource_type and 
                    permission.resource_name == resource_name):
                    
                    # Check expiration
                    if permission.expires_at and current_time > permission.expires_at:
                        continue
                    
                    # Check access type
                    if access_type in permission.access_types:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def _find_existing_permission(self, 
                                user_id: str, 
                                resource_type: str, 
                                resource_name: str) -> Optional[AccessPermission]:
        """Find existing permission for user and resource"""        if user_id not in self.permissions:
            return None
        
        for permission in self.permissions[user_id]:
            if (permission.resource_type == resource_type and 
                permission.resource_name == resource_name):
                return permission
        
        return None
    
    async def record_failed_attempt(self, user_id: str, ip_address: Optional[str] = None):
        """Record failed authentication attempt"""        current_time = datetime.utcnow()
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(current_time)
        
        # Get security policy
        policy = self.security_policies.get('default')
        
        # Check if user should be locked
        recent_attempts = [
            attempt for attempt in self.failed_attempts[user_id]
            if current_time - attempt <= timedelta(minutes=policy.lockout_duration_minutes)
        ]
        
        if len(recent_attempts) >= policy.max_failed_attempts:
            lockout_until = current_time + timedelta(minutes=policy.lockout_duration_minutes)
            self.locked_users[user_id] = lockout_until
            
            logger.warning(f"User {user_id} locked due to {len(recent_attempts)} failed attempts")
    
    def _is_user_locked(self, user_id: str) -> bool:
        """Check if user is currently locked"""        if user_id not in self.locked_users:
            return False
        
        current_time = datetime.utcnow()
        lockout_until = self.locked_users[user_id]
        
        if current_time >= lockout_until:
            # Unlock user
            del self.locked_users[user_id]
            return False
        
        return True
    
    async def get_user_permissions(self, user_id: str) -> List[AccessPermission]:
        """Get all permissions for a user"""        return self.permissions.get(user_id, [])
    
    async def cleanup_expired_permissions(self):
        """Clean up expired permissions"""        current_time = datetime.utcnow()
        cleanup_count = 0
        
        for user_id in self.permissions:
            original_count = len(self.permissions[user_id])
            
            self.permissions[user_id] = [
                p for p in self.permissions[user_id]
                if not (p.expires_at and current_time > p.expires_at)
            ]
            
            cleanup_count += original_count - len(self.permissions[user_id])
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} expired permissions")
        
        return cleanup_count


class DatabaseSecurity:
    """Main database security orchestrator"""    
    def __init__(self):
        self.encryption = DatabaseEncryption()
        self.auditor = DatabaseAuditor()
        self.access_control = AccessControlManager()
        self.query_sanitizer = QuerySanitizer()
        self._initialized = False
    
    async def initialize(self):
        """Initialize all security components"""        if self._initialized:
            return
        
        try:
            await self.encryption.initialize()
            await self.auditor.initialize()
            await self.access_control.initialize()
            
            self._initialized = True
            logger.info("Database security system initialized")
            
        except Exception as e:
            logger.error(f"Database security initialization failed: {e}")
            raise
    
    @asynccontextmanager
    async def secure_session(self, 
                           user_id: str, 
                           required_permissions: List[Tuple[str, str, AccessType]]):
        """        Secure database session with permission checks and auditing
        
        Args:
            user_id: User ID requesting access
            required_permissions: List of (resource_type, resource_name, access_type) tuples
        """        if not self._initialized:
            raise RuntimeError("Database security not initialized")
        
        # Check all required permissions
        for resource_type, resource_name, access_type in required_permissions:
            if not await self.access_control.check_permission(
                user_id, resource_type, resource_name, access_type
            ):
                raise PermissionError(
                    f"User {user_id} lacks {access_type.value} permission for {resource_type}:{resource_name}"
                )
        
        # Log session start
        await self.auditor.log_security_event(
            'session_start',
            user_id,
            f"Secure session started with permissions: {required_permissions}",
            SecurityLevel.INTERNAL
        )
        
        session_manager = SessionManager()
        
        try:
            async with session_manager.get_async_session() as session:
                yield SecureSessionWrapper(session, user_id, self)
                
        except Exception as e:
            await self.auditor.log_security_event(
                'session_error',
                user_id,
                f"Session error: {str(e)}",
                SecurityLevel.CONFIDENTIAL
            )
            raise
        finally:
            await self.auditor.log_security_event(
                'session_end',
                user_id,
                "Secure session ended",
                SecurityLevel.INTERNAL
            )
    
    async def validate_query_security(self, query: str) -> Tuple[bool, List[str]]:
        """Validate query for security issues"""        return self.query_sanitizer.is_safe_query(query)
    
    async def get_security_summary(self) -> Dict[str, Any]:
        """Get security system summary"""        return {
            'encryption_active': self.encryption._initialized,
            'audit_enabled': self.auditor._audit_enabled,
            'total_permissions': sum(len(perms) for perms in self.access_control.permissions.values()),
            'locked_users': len(self.access_control.locked_users),
            'recent_audit_events': len([
                e for e in self.auditor.audit_events
                if datetime.utcnow() - e.timestamp <= timedelta(hours=24)
            ]),
            'security_policies': len(self.access_control.security_policies)
        }


class SecureSessionWrapper:
    """Wrapper for database session with security features"""    
    def __init__(self, session: AsyncSession, user_id: str, security: DatabaseSecurity):
        self.session = session
        self.user_id = user_id
        self.security = security
    
    async def execute_secure(self, query: str, parameters: Dict[str, Any] = None) -> Any:
        """Execute query with security validation"""        # Validate query security
        is_safe, issues = await self.security.validate_query_security(query)
        
        if not is_safe:
            raise SecurityError(f"Query security validation failed: {'; '.join(issues)}")
        
        # Execute with audit logging
        start_time = datetime.utcnow()
        
        try:
            result = await self.session.execute(text(query), parameters or {})
            
            # Log successful execution
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            await self.security.auditor.log_security_event(
                'query_execution',
                self.user_id,
                f"Query executed successfully in {execution_time:.2f}ms",
                SecurityLevel.INTERNAL,
                {'query_hash': hashlib.sha256(query.encode()).hexdigest()[:16]}
            )
            
            return result
            
        except Exception as e:
            await self.security.auditor.log_security_event(
                'query_error',
                self.user_id,
                f"Query execution failed: {str(e)}",
                SecurityLevel.CONFIDENTIAL,
                {'error_type': type(e).__name__}
            )
            raise
    
    async def encrypt_field(self, value: str) -> str:
        """Encrypt field value"""        return self.security.encryption.encrypt_field(value)
    
    async def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt field value"""        return self.security.encryption.decrypt_field(encrypted_value)


class SecurityError(Exception):
    """Security-related exception"""    pass


# Global security instance
_security_instance: Optional[DatabaseSecurity] = None


async def get_database_security() -> DatabaseSecurity:
    """Get global database security instance"""    global _security_instance
    
    if _security_instance is None:
        _security_instance = DatabaseSecurity()
        await _security_instance.initialize()
    
    return _security_instance


# Convenience functions
async def secure_password_hash(password: str) -> str:
    """Hash password securely"""    return PasswordSecurity.hash_password(password)


async def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""    return PasswordSecurity.verify_password(password, hashed)


async def encrypt_sensitive_field(value: str) -> str:
    """Encrypt sensitive field value"""    security = await get_database_security()
    return security.encryption.encrypt_field(value)


async def decrypt_sensitive_field(encrypted_value: str) -> str:
    """Decrypt sensitive field value"""    security = await get_database_security()
    return security.encryption.decrypt_field(encrypted_value)
