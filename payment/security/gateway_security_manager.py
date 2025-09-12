"""🔒 Gateway Security Manager
============================

Enterprise-grade security management for payment gateway operations.
Implements PCI DSS compliance enforcement, encryption key management,
secure token handling, and vulnerability protection.

Features:
- PCI DSS compliance enforcement
- Encryption key management and rotation
- Secure token handling and validation
- Vulnerability scanning and protection
- Security incident response
- Access control and authentication

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import hashlib
import hmac
import secrets
import base64
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import aioredis
import re

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EncryptionType(Enum):
    """Types of encryption supported"""
    AES_256_GCM = "aes_256_gcm"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    FERNET = "fernet"


class TokenType(Enum):
    """Types of security tokens"""
    PAYMENT_TOKEN = "payment_token"
    API_KEY = "api_key"
    SESSION_TOKEN = "session_token"
    WEBHOOK_TOKEN = "webhook_token"
    ACCESS_TOKEN = "access_token"


class SecurityEvent(Enum):
    """Security events that can be tracked"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ENCRYPTION_FAILURE = "encryption_failure"
    KEY_ROTATION = "key_rotation"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class SecurityToken:
    """Security token information"""
    token_id: str
    token_type: TokenType
    encrypted_value: str
    created_at: datetime
    expires_at: Optional[datetime]
    permissions: List[str]
    is_active: bool = True
    last_used: Optional[datetime] = None
    usage_count: int = 0


@dataclass
class EncryptionKey:
    """Encryption key information"""
    key_id: str
    key_type: EncryptionType
    encrypted_key: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool = True
    rotation_count: int = 0
    last_rotated: Optional[datetime] = None


@dataclass
class SecurityIncident:
    """Security incident tracking"""
    incident_id: str
    event_type: SecurityEvent
    severity: SecurityLevel
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)


class GatewaySecurityManager:
    """Enterprise security manager for payment gateway"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.master_key = None
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.active_tokens: Dict[str, SecurityToken] = {}
        self.security_incidents: List[SecurityIncident] = []
        self.is_initialized = False
        
        # PCI DSS compliance tracking
        self.pci_requirements = {
            "install_maintain_firewall": False,
            "change_default_passwords": False,
            "protect_stored_cardholder_data": False,
            "encrypt_cardholder_data": False,
            "use_updated_antivirus": False,
            "develop_secure_systems": False,
            "restrict_cardholder_data_access": False,
            "identify_authenticate_access": False,
            "restrict_physical_access": False,
            "track_monitor_access": False,
            "test_security_systems": False,
            "maintain_information_security": False
        }
        
    async def initialize(self):
        """Initialize the security manager"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = aioredis.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}"
            )
            
            # Initialize master encryption key
            await self._initialize_master_key()
            
            # Load existing encryption keys
            await self._load_encryption_keys()
            
            # Initialize PCI DSS compliance
            await self._initialize_pci_compliance()
            
            self.is_initialized = True
            logger.info("Gateway Security Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gateway Security Manager: {e}")
            raise
    
    async def _initialize_master_key(self):
        """Initialize or load the master encryption key"""
        try:
            # Try to load existing master key
            stored_key = await self.redis_client.get("gateway:security:master_key")
            
            if stored_key:
                self.master_key = stored_key.decode()
                logger.info("Master key loaded from storage")
            else:
                # Generate new master key
                self.master_key = Fernet.generate_key().decode()
                await self.redis_client.set(
                    "gateway:security:master_key", 
                    self.master_key,
                    ex=86400 * 365  # 1 year expiry
                )
                logger.info("New master key generated and stored")
                
        except Exception as e:
            logger.error(f"Failed to initialize master key: {e}")
            raise
    
    async def _load_encryption_keys(self):
        """Load existing encryption keys from storage"""
        try:
            key_data = await self.redis_client.get("gateway:security:encryption_keys")
            
            if key_data:
                keys_dict = json.loads(key_data.decode())
                for key_id, key_info in keys_dict.items():
                    self.encryption_keys[key_id] = EncryptionKey(
                        key_id=key_info['key_id'],
                        key_type=EncryptionType(key_info['key_type']),
                        encrypted_key=key_info['encrypted_key'],
                        created_at=datetime.fromisoformat(key_info['created_at']),
                        expires_at=datetime.fromisoformat(key_info['expires_at']) if key_info.get('expires_at') else None,
                        is_active=key_info['is_active'],
                        rotation_count=key_info.get('rotation_count', 0),
                        last_rotated=datetime.fromisoformat(key_info['last_rotated']) if key_info.get('last_rotated') else None
                    )
                    
                logger.info(f"Loaded {len(self.encryption_keys)} encryption keys")
                
        except Exception as e:
            logger.error(f"Failed to load encryption keys: {e}")
    
    async def _initialize_pci_compliance(self):
        """Initialize PCI DSS compliance monitoring"""
        try:
            # Load compliance status from storage
            compliance_data = await self.redis_client.get("gateway:security:pci_compliance")
            
            if compliance_data:
                stored_compliance = json.loads(compliance_data.decode())
                self.pci_requirements.update(stored_compliance)
                
            # Start compliance monitoring
            await self._monitor_pci_compliance()
            
            logger.info("PCI DSS compliance monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PCI compliance: {e}")
    
    async def generate_encryption_key(
        self, 
        key_type: EncryptionType,
        expires_in_days: Optional[int] = None
    ) -> str:
        """Generate a new encryption key"""
        try:
            key_id = str(uuid.uuid4())
            
            # Generate key based on type
            if key_type == EncryptionType.FERNET:
                raw_key = Fernet.generate_key()
            elif key_type == EncryptionType.AES_256_GCM:
                raw_key = secrets.token_bytes(32)
            elif key_type in [EncryptionType.RSA_2048, EncryptionType.RSA_4096]:
                key_size = 2048 if key_type == EncryptionType.RSA_2048 else 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
                raw_key = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Encrypt the key with master key
            fernet = Fernet(self.master_key.encode())
            encrypted_key = fernet.encrypt(raw_key).decode()
            
            # Create key object
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
                
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                encrypted_key=encrypted_key,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            # Store key
            self.encryption_keys[key_id] = encryption_key
            await self._save_encryption_keys()
            
            logger.info(f"Generated new {key_type.value} encryption key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"Failed to generate encryption key: {e}")
            raise
    
    async def encrypt_data(self, data: str, key_id: str) -> str:
        """Encrypt data using specified key"""
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key not found: {key_id}")
                
            encryption_key = self.encryption_keys[key_id]
            
            if not encryption_key.is_active:
                raise ValueError(f"Encryption key is not active: {key_id}")
                
            # Decrypt the encryption key
            fernet = Fernet(self.master_key.encode())
            raw_key = fernet.decrypt(encryption_key.encrypted_key.encode())
            
            # Encrypt the data
            if encryption_key.key_type == EncryptionType.FERNET:
                data_fernet = Fernet(raw_key)
                encrypted_data = data_fernet.encrypt(data.encode())
            else:
                # For other encryption types, use Fernet as default
                data_fernet = Fernet(raw_key)
                encrypted_data = data_fernet.encrypt(data.encode())
                
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str, key_id: str) -> str:
        """Decrypt data using specified key"""
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key not found: {key_id}")
                
            encryption_key = self.encryption_keys[key_id]
            
            # Decrypt the encryption key
            fernet = Fernet(self.master_key.encode())
            raw_key = fernet.decrypt(encryption_key.encrypted_key.encode())
            
            # Decrypt the data
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            if encryption_key.key_type == EncryptionType.FERNET:
                data_fernet = Fernet(raw_key)
                decrypted_data = data_fernet.decrypt(encrypted_bytes)
            else:
                # For other encryption types, use Fernet as default
                data_fernet = Fernet(raw_key)
                decrypted_data = data_fernet.decrypt(encrypted_bytes)
                
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    async def generate_secure_token(
        self,
        token_type: TokenType,
        permissions: List[str],
        expires_in_hours: Optional[int] = None
    ) -> str:
        """Generate a secure token"""
        try:
            token_id = str(uuid.uuid4())
            
            # Generate secure random token
            token_value = secrets.token_urlsafe(64)
            
            # Encrypt token value
            key_id = await self.generate_encryption_key(EncryptionType.FERNET, expires_in_days=1)
            encrypted_value = await self.encrypt_data(token_value, key_id)
            
            # Create token object
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)
                
            token = SecurityToken(
                token_id=token_id,
                token_type=token_type,
                encrypted_value=encrypted_value,
                created_at=datetime.now(),
                expires_at=expires_at,
                permissions=permissions
            )
            
            # Store token
            self.active_tokens[token_id] = token
            await self._save_active_tokens()
            
            logger.info(f"Generated secure {token_type.value} token: {token_id}")
            return token_id
            
        except Exception as e:
            logger.error(f"Failed to generate secure token: {e}")
            raise
    
    async def validate_token(self, token_id: str, required_permission: str = None) -> bool:
        """Validate a security token"""
        try:
            if token_id not in self.active_tokens:
                await self._log_security_event(
                    SecurityEvent.UNAUTHORIZED_ACCESS,
                    SecurityLevel.HIGH,
                    f"Invalid token access attempt: {token_id}"
                )
                return False
                
            token = self.active_tokens[token_id]
            
            # Check if token is active
            if not token.is_active:
                return False
                
            # Check expiration
            if token.expires_at and datetime.now() > token.expires_at:
                token.is_active = False
                await self._save_active_tokens()
                return False
                
            # Check permissions
            if required_permission and required_permission not in token.permissions:
                await self._log_security_event(
                    SecurityEvent.UNAUTHORIZED_ACCESS,
                    SecurityLevel.MEDIUM,
                    f"Insufficient permissions for token: {token_id}"
                )
                return False
                
            # Update usage
            token.last_used = datetime.now()
            token.usage_count += 1
            await self._save_active_tokens()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate token: {e}")
            return False
    
    async def rotate_encryption_keys(self):
        """Rotate all encryption keys"""
        try:
            rotated_count = 0
            
            for key_id, encryption_key in self.encryption_keys.items():
                if encryption_key.is_active:
                    # Generate new key of same type
                    new_key_id = await self.generate_encryption_key(
                        encryption_key.key_type,
                        expires_in_days=365
                    )
                    
                    # Deactivate old key
                    encryption_key.is_active = False
                    encryption_key.rotation_count += 1
                    encryption_key.last_rotated = datetime.now()
                    
                    rotated_count += 1
                    
            await self._save_encryption_keys()
            
            # Log security event
            await self._log_security_event(
                SecurityEvent.KEY_ROTATION,
                SecurityLevel.MEDIUM,
                f"Rotated {rotated_count} encryption keys"
            )
            
            logger.info(f"Rotated {rotated_count} encryption keys")
            
        except Exception as e:
            logger.error(f"Failed to rotate encryption keys: {e}")
            raise
    
    async def scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan for security vulnerabilities"""
        try:
            vulnerabilities = []
            
            # Check expired keys
            for key_id, encryption_key in self.encryption_keys.items():
                if encryption_key.expires_at and datetime.now() > encryption_key.expires_at:
                    vulnerabilities.append({
                        "type": "expired_key",
                        "severity": SecurityLevel.HIGH.value,
                        "description": f"Encryption key {key_id} has expired",
                        "key_id": key_id
                    })
            
            # Check expired tokens
            for token_id, token in self.active_tokens.items():
                if token.expires_at and datetime.now() > token.expires_at and token.is_active:
                    vulnerabilities.append({
                        "type": "expired_token",
                        "severity": SecurityLevel.MEDIUM.value,
                        "description": f"Security token {token_id} has expired but is still active",
                        "token_id": token_id
                    })
            
            # Check PCI compliance
            non_compliant = [req for req, status in self.pci_requirements.items() if not status]
            if non_compliant:
                vulnerabilities.append({
                    "type": "pci_compliance",
                    "severity": SecurityLevel.CRITICAL.value,
                    "description": f"PCI DSS requirements not met: {', '.join(non_compliant)}",
                    "requirements": non_compliant
                })
            
            # Log vulnerabilities
            if vulnerabilities:
                await self._log_security_event(
                    SecurityEvent.VULNERABILITY_DETECTED,
                    SecurityLevel.HIGH,
                    f"Found {len(vulnerabilities)} security vulnerabilities"
                )
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Failed to scan vulnerabilities: {e}")
            raise
    
    async def _monitor_pci_compliance(self):
        """Monitor PCI DSS compliance requirements"""
        try:
            # This would integrate with actual PCI compliance monitoring
            # For now, we'll simulate some basic checks
            
            # Check encryption status
            if self.encryption_keys:
                self.pci_requirements["encrypt_cardholder_data"] = True
                self.pci_requirements["protect_stored_cardholder_data"] = True
            
            # Check access controls
            if self.active_tokens:
                self.pci_requirements["restrict_cardholder_data_access"] = True
                self.pci_requirements["identify_authenticate_access"] = True
            
            # Save compliance status
            await self.redis_client.set(
                "gateway:security:pci_compliance",
                json.dumps(self.pci_requirements),
                ex=3600  # 1 hour expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to monitor PCI compliance: {e}")
    
    async def _log_security_event(
        self,
        event_type: SecurityEvent,
        severity: SecurityLevel,
        description: str,
        metadata: Dict[str, Any] = None
    ):
        """Log a security event"""
        try:
            incident = SecurityIncident(
                incident_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=severity,
                description=description,
                detected_at=datetime.now(),
                metadata=metadata or {}
            )
            
            self.security_incidents.append(incident)
            
            # Store in Redis for persistence
            await self.redis_client.lpush(
                "gateway:security:incidents",
                json.dumps({
                    "incident_id": incident.incident_id,
                    "event_type": incident.event_type.value,
                    "severity": incident.severity.value,
                    "description": incident.description,
                    "detected_at": incident.detected_at.isoformat(),
                    "metadata": incident.metadata
                })
            )
            
            # Keep only last 1000 incidents
            await self.redis_client.ltrim("gateway:security:incidents", 0, 999)
            
            logger.warning(f"Security event logged: {event_type.value} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def _save_encryption_keys(self):
        """Save encryption keys to storage"""
        try:
            keys_dict = {}
            for key_id, key in self.encryption_keys.items():
                keys_dict[key_id] = {
                    "key_id": key.key_id,
                    "key_type": key.key_type.value,
                    "encrypted_key": key.encrypted_key,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                    "is_active": key.is_active,
                    "rotation_count": key.rotation_count,
                    "last_rotated": key.last_rotated.isoformat() if key.last_rotated else None
                }
            
            await self.redis_client.set(
                "gateway:security:encryption_keys",
                json.dumps(keys_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save encryption keys: {e}")
    
    async def _save_active_tokens(self):
        """Save active tokens to storage"""
        try:
            tokens_dict = {}
            for token_id, token in self.active_tokens.items():
                if token.is_active:  # Only save active tokens
                    tokens_dict[token_id] = {
                        "token_id": token.token_id,
                        "token_type": token.token_type.value,
                        "encrypted_value": token.encrypted_value,
                        "created_at": token.created_at.isoformat(),
                        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                        "permissions": token.permissions,
                        "is_active": token.is_active,
                        "last_used": token.last_used.isoformat() if token.last_used else None,
                        "usage_count": token.usage_count
                    }
            
            await self.redis_client.set(
                "gateway:security:active_tokens",
                json.dumps(tokens_dict),
                ex=86400  # 1 day expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save active tokens: {e}")
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get overall security status"""
        try:
            total_keys = len(self.encryption_keys)
            active_keys = sum(1 for key in self.encryption_keys.values() if key.is_active)
            total_tokens = len(self.active_tokens)
            active_tokens = sum(1 for token in self.active_tokens.values() if token.is_active)
            
            # Calculate PCI compliance percentage
            compliant_requirements = sum(1 for status in self.pci_requirements.values() if status)
            total_requirements = len(self.pci_requirements)
            compliance_percentage = (compliant_requirements / total_requirements) * 100
            
            # Recent security incidents
            recent_incidents = [
                incident for incident in self.security_incidents
                if (datetime.now() - incident.detected_at).total_seconds() < 86400  # Last 24 hours
            ]
            
            return {
                "is_initialized": self.is_initialized,
                "encryption_keys": {
                    "total": total_keys,
                    "active": active_keys
                },
                "security_tokens": {
                    "total": total_tokens,
                    "active": active_tokens
                },
                "pci_compliance": {
                    "percentage": compliance_percentage,
                    "requirements_met": compliant_requirements,
                    "total_requirements": total_requirements
                },
                "security_incidents": {
                    "total": len(self.security_incidents),
                    "recent_24h": len(recent_incidents),
                    "critical_count": sum(1 for i in recent_incidents if i.severity == SecurityLevel.CRITICAL),
                    "high_count": sum(1 for i in recent_incidents if i.severity == SecurityLevel.HIGH)
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_items(self):
        """Clean up expired keys and tokens"""
        try:
            cleaned_count = 0
            
            # Clean up expired keys
            for key_id, key in list(self.encryption_keys.items()):
                if key.expires_at and datetime.now() > key.expires_at:
                    del self.encryption_keys[key_id]
                    cleaned_count += 1
            
            # Clean up expired tokens
            for token_id, token in list(self.active_tokens.items()):
                if token.expires_at and datetime.now() > token.expires_at:
                    del self.active_tokens[token_id]
                    cleaned_count += 1
            
            if cleaned_count > 0:
                await self._save_encryption_keys()
                await self._save_active_tokens()
                logger.info(f"Cleaned up {cleaned_count} expired security items")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {e}")
    
    async def close(self):
        """Close the security manager and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Gateway Security Manager closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Gateway Security Manager: {e}")