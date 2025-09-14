"""
Communication Security Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Communication Security Manager - Enterprise Security Component
Message encryption, authentication, and secure communication channels

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive security for platform communications including:
- End-to-end message encryption and decryption
- Authentication and authorization for communication channels
- Certificate management and validation
- Secure communication channels with integrity verification
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import hmac
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthenticationMethod(Enum):
    """Authentication method types"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    CERTIFICATE = "certificate"
    MUTUAL_TLS = "mutual_tls"
    OAUTH2 = "oauth2"


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    security_level: SecurityLevel
    encryption_required: bool = True
    authentication_methods: List[AuthenticationMethod] = field(default_factory=list)
    max_message_size: int = 10485760  # 10MB
    message_ttl: int = 3600  # 1 hour
    rate_limit: int = 1000  # messages per minute
    allowed_origins: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EncryptionKey:
    """Encryption key management"""
    key_id: str
    key_type: str  # symmetric, asymmetric
    key_data: bytes
    algorithm: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


@dataclass
class SecurityCertificate:
    """Security certificate definition"""
    cert_id: str
    common_name: str
    certificate_data: bytes
    private_key_data: Optional[bytes] = None
    issuer: str = ""
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True


@dataclass
class SecureMessage:
    """Secure message container"""
    message_id: str
    sender_id: str
    recipient_id: str
    encrypted_payload: bytes
    signature: bytes
    encryption_algorithm: str
    timestamp: datetime
    ttl: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommunicationSecurityManager:
    """
    Enterprise Communication Security Manager
    
    Provides comprehensive security for platform communications including
    encryption, authentication, certificate management, and secure channels
    with enterprise-grade security standards and compliance.
    """
    
    def __init__(self) -> None:
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.certificates: Dict[str, SecurityCertificate] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.message_cache: Dict[str, SecureMessage] = {}
        self.security_events: List[Dict[str, Any]] = []
        
        # Initialize default security components
        self._initialize_default_security()
        
        logger.info("Communication Security Manager initialized")
    
    def _initialize_default_security(self) -> None:
        """Initialize default security policies and keys"""
        try:
            # Create default security policy
            default_policy = SecurityPolicy(
                policy_id="default_enterprise",
                name="Default Enterprise Security Policy",
                security_level=SecurityLevel.HIGH,
                encryption_required=True,
                authentication_methods=[
                    AuthenticationMethod.JWT_TOKEN,
                    AuthenticationMethod.API_KEY
                ],
                allowed_origins=["*"]
            )
            
            self.security_policies["default"] = default_policy
            
            # Generate default encryption keys
            self._generate_encryption_key("default_symmetric", "symmetric", "AES-256-GCM")
            self._generate_encryption_key("default_asymmetric", "asymmetric", "RSA-2048")
            
            logger.info("Default security components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default security: {e}")
    
    # Policy Management
    async def create_security_policy(self, policy: SecurityPolicy) -> bool:
        """Create a new security policy"""
        try:
            if policy.policy_id in self.security_policies:
                logger.warning(f"Security policy {policy.policy_id} already exists")
                return False
            
            # Validate policy
            if not policy.authentication_methods:
                policy.authentication_methods = [AuthenticationMethod.JWT_TOKEN]
            
            self.security_policies[policy.policy_id] = policy
            
            # Log security event
            await self._log_security_event("policy_created", {
                "policy_id": policy.policy_id,
                "security_level": policy.security_level.value
            })
            
            logger.info(f"Security policy {policy.policy_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create security policy {policy.policy_id}: {e}")
            return False
    
    async def get_security_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get security policy by ID"""
        return self.security_policies.get(policy_id)
    
    async def update_security_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Update security policy"""
        try:
            if policy_id not in self.security_policies:
                logger.error(f"Security policy {policy_id} not found")
                return False
            
            policy = self.security_policies[policy_id]
            
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            # Log security event
            await self._log_security_event("policy_updated", {
                "policy_id": policy_id,
                "updates": list(updates.keys())
            })
            
            logger.info(f"Security policy {policy_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update security policy {policy_id}: {e}")
            return False
    
    # Key Management
    def _generate_encryption_key(self, key_id: str, key_type: str, algorithm: str) -> bool:
        """Generate encryption key"""
        try:
            if key_type == "symmetric":
                if algorithm == "AES-256-GCM":
                    key_data = Fernet.generate_key()
                else:
                    key_data = secrets.token_bytes(32)  # 256-bit key
            
            elif key_type == "asymmetric":
                if algorithm == "RSA-2048":
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=2048,
                        backend=default_backend()
                    )
                    key_data = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                else:
                    raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Store encryption key
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                key_data=key_data,
                algorithm=algorithm,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year expiry
            )
            
            self.encryption_keys[key_id] = encryption_key
            
            logger.info(f"Encryption key {key_id} generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate encryption key {key_id}: {e}")
            return False
    
    async def rotate_encryption_key(self, key_id: str) -> bool:
        """Rotate encryption key"""
        try:
            if key_id not in self.encryption_keys:
                logger.error(f"Encryption key {key_id} not found")
                return False
            
            old_key = self.encryption_keys[key_id]
            
            # Generate new key with same parameters
            new_key_id = f"{key_id}_rotated_{int(datetime.utcnow().timestamp())}"
            success = self._generate_encryption_key(
                new_key_id, 
                old_key.key_type, 
                old_key.algorithm
            )
            
            if success:
                # Deactivate old key
                old_key.is_active = False
                
                # Update reference to new key
                self.encryption_keys[key_id] = self.encryption_keys[new_key_id]
                self.encryption_keys[key_id].key_id = key_id
                
                # Log security event
                await self._log_security_event("key_rotated", {
                    "key_id": key_id,
                    "old_key_id": old_key.key_id,
                    "new_key_id": new_key_id
                })
                
                logger.info(f"Encryption key {key_id} rotated successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to rotate encryption key {key_id}: {e}")
            return False
    
    # Message Encryption/Decryption
    async def encrypt_message(self, message: str, key_id: str = "default_symmetric", 
                            metadata: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
        """Encrypt message using specified key"""
        try:
            if key_id not in self.encryption_keys:
                logger.error(f"Encryption key {key_id} not found")
                return None
            
            key = self.encryption_keys[key_id]
            if not key.is_active:
                logger.error(f"Encryption key {key_id} is not active")
                return None
            
            if key.key_type == "symmetric":
                if key.algorithm == "AES-256-GCM":
                    fernet = Fernet(key.key_data)
                    encrypted_data = fernet.encrypt(message.encode('utf-8'))
                else:
                    # Generic AES encryption
                    iv = secrets.token_bytes(16)
                    cipher = Cipher(
                        algorithms.AES(key.key_data),
                        modes.GCM(iv),
                        backend=default_backend()
                    )
                    encryptor = cipher.encryptor()
                    encrypted_data = iv + encryptor.update(message.encode('utf-8')) + encryptor.finalize()
                    encrypted_data += encryptor.tag
            
            elif key.key_type == "asymmetric":
                # Load private key for RSA encryption
                private_key = serialization.load_pem_private_key(
                    key.key_data,
                    password=None,
                    backend=default_backend()
                )
                public_key = private_key.public_key()
                
                encrypted_data = public_key.encrypt(
                    message.encode('utf-8'),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            
            else:
                raise ValueError(f"Unsupported key type: {key.key_type}")
            
            logger.debug(f"Message encrypted successfully with key {key_id}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Failed to encrypt message: {e}")
            return None
    
    async def decrypt_message(self, encrypted_data: bytes, key_id: str = "default_symmetric") -> Optional[str]:
        """Decrypt message using specified key"""
        try:
            if key_id not in self.encryption_keys:
                logger.error(f"Encryption key {key_id} not found")
                return None
            
            key = self.encryption_keys[key_id]
            
            if key.key_type == "symmetric":
                if key.algorithm == "AES-256-GCM":
                    fernet = Fernet(key.key_data)
                    decrypted_data = fernet.decrypt(encrypted_data)
                else:
                    # Generic AES decryption
                    iv = encrypted_data[:16]
                    tag = encrypted_data[-16:]
                    ciphertext = encrypted_data[16:-16]
                    
                    cipher = Cipher(
                        algorithms.AES(key.key_data),
                        modes.GCM(iv, tag),
                        backend=default_backend()
                    )
                    decryptor = cipher.decryptor()
                    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            elif key.key_type == "asymmetric":
                # Load private key for RSA decryption
                private_key = serialization.load_pem_private_key(
                    key.key_data,
                    password=None,
                    backend=default_backend()
                )
                
                decrypted_data = private_key.decrypt(
                    encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            
            else:
                raise ValueError(f"Unsupported key type: {key.key_type}")
            
            logger.debug(f"Message decrypted successfully with key {key_id}")
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}")
            return None
    
    # Authentication
    async def authenticate_request(self, token: str, method: AuthenticationMethod) -> Optional[Dict[str, Any]]:
        """Authenticate request using specified method"""
        try:
            if method == AuthenticationMethod.JWT_TOKEN:
                return await self._authenticate_jwt(token)
            elif method == AuthenticationMethod.API_KEY:
                return await self._authenticate_api_key(token)
            elif method == AuthenticationMethod.CERTIFICATE:
                return await self._authenticate_certificate(token)
            else:
                logger.error(f"Unsupported authentication method: {method}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def _authenticate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate JWT token"""
        try:
            # In a real implementation, you would use a proper secret key
            secret_key = "your-secret-key"
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Validate token claims
            if 'exp' in payload and datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                logger.error("JWT token has expired")
                return None
            
            return {
                "user_id": payload.get("user_id"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "authenticated": True
            }
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
    
    async def _authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Authenticate API key"""
        try:
            # In a real implementation, you would look up the API key in a database
            # For now, we'll use a simple validation
            if len(api_key) < 32:
                logger.error("Invalid API key format")
                return None
            
            return {
                "api_key": api_key,
                "authenticated": True,
                "permissions": ["read", "write"]
            }
            
        except Exception as e:
            logger.error(f"API key authentication failed: {e}")
            return None
    
    async def _authenticate_certificate(self, cert_data: str) -> Optional[Dict[str, Any]]:
        """Authenticate using certificate"""
        try:
            # In a real implementation, you would validate the certificate
            # against a trusted CA and check for revocation
            return {
                "certificate": cert_data,
                "authenticated": True,
                "trust_level": "high"
            }
            
        except Exception as e:
            logger.error(f"Certificate authentication failed: {e}")
            return None
    
    # Digital Signatures
    async def sign_message(self, message: str, key_id: str = "default_asymmetric") -> Optional[bytes]:
        """Create digital signature for message"""
        try:
            if key_id not in self.encryption_keys:
                logger.error(f"Signing key {key_id} not found")
                return None
            
            key = self.encryption_keys[key_id]
            if key.key_type != "asymmetric":
                logger.error(f"Key {key_id} is not suitable for signing")
                return None
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            
            # Create signature
            signature = private_key.sign(
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug(f"Message signed successfully with key {key_id}")
            return signature
            
        except Exception as e:
            logger.error(f"Failed to sign message: {e}")
            return None
    
    async def verify_signature(self, message: str, signature: bytes, key_id: str = "default_asymmetric") -> bool:
        """Verify digital signature"""
        try:
            if key_id not in self.encryption_keys:
                logger.error(f"Verification key {key_id} not found")
                return False
            
            key = self.encryption_keys[key_id]
            if key.key_type != "asymmetric":
                logger.error(f"Key {key_id} is not suitable for verification")
                return False
            
            # Load private key and extract public key
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Verify signature
            public_key.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug(f"Signature verified successfully with key {key_id}")
            return True
            
        except Exception as e:
            logger.debug(f"Signature verification failed: {e}")
            return False
    
    # Security Event Logging
    async def _log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log security event"""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "event_data": event_data,
                "event_id": secrets.token_hex(16)
            }
            
            self.security_events.append(event)
            
            # Keep only last 10000 events
            if len(self.security_events) > 10000:
                self.security_events = self.security_events[-10000:]
            
            logger.info(f"Security event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def get_security_events(self, event_type: Optional[str] = None, 
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get security events with optional filtering"""
        try:
            events = self.security_events
            
            if event_type:
                events = [e for e in events if e["event_type"] == event_type]
            
            if start_time:
                events = [e for e in events if datetime.fromisoformat(e["timestamp"]) >= start_time]
            
            if end_time:
                events = [e for e in events if datetime.fromisoformat(e["timestamp"]) <= end_time]
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
    
    # Security Health Check
    async def security_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive security health check"""
        try:
            health_status = {
                "overall_status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    "encryption_keys": {"status": "healthy", "active_keys": 0, "expired_keys": 0},
                    "security_policies": {"status": "healthy", "total_policies": len(self.security_policies)},
                    "certificates": {"status": "healthy", "active_certs": 0, "expired_certs": 0},
                    "security_events": {"status": "healthy", "recent_events": 0}
                }
            }
            
            # Check encryption keys
            active_keys = sum(1 for key in self.encryption_keys.values() if key.is_active)
            expired_keys = sum(1 for key in self.encryption_keys.values() 
                             if key.expires_at and key.expires_at < datetime.utcnow())
            
            health_status["checks"]["encryption_keys"]["active_keys"] = active_keys
            health_status["checks"]["encryption_keys"]["expired_keys"] = expired_keys
            
            if expired_keys > 0:
                health_status["checks"]["encryption_keys"]["status"] = "warning"
            
            # Check certificates
            active_certs = sum(1 for cert in self.certificates.values() if cert.is_active)
            expired_certs = sum(1 for cert in self.certificates.values()
                              if cert.valid_until and cert.valid_until < datetime.utcnow())
            
            health_status["checks"]["certificates"]["active_certs"] = active_certs
            health_status["checks"]["certificates"]["expired_certs"] = expired_certs
            
            if expired_certs > 0:
                health_status["checks"]["certificates"]["status"] = "warning"
            
            # Check recent security events
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_events = len([e for e in self.security_events 
                               if datetime.fromisoformat(e["timestamp"]) > one_hour_ago])
            
            health_status["checks"]["security_events"]["recent_events"] = recent_events
            
            # Determine overall status
            warning_checks = [check for check in health_status["checks"].values() 
                            if check["status"] == "warning"]
            
            if warning_checks:
                health_status["overall_status"] = "warning"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Security health check failed: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Factory function for easier instantiation
def create_communication_security_manager() -> CommunicationSecurityManager:
    """Factory function to create a Communication Security Manager"""
    return CommunicationSecurityManager()


# Example usage
async def main() -> None:
    """Example usage of Communication Security Manager"""
    security_manager = create_communication_security_manager()
    
    # Create a high-security policy
    high_security_policy = SecurityPolicy(
        policy_id="high_security",
        name="High Security Policy",
        security_level=SecurityLevel.CRITICAL,
        encryption_required=True,
        authentication_methods=[
            AuthenticationMethod.JWT_TOKEN,
            AuthenticationMethod.CERTIFICATE
        ],
        max_message_size=1048576,  # 1MB
        message_ttl=300  # 5 minutes
    )
    
    await security_manager.create_security_policy(high_security_policy)
    
    # Test message encryption/decryption
    test_message = "This is a confidential message from the creator platform"
    
    encrypted_data = await security_manager.encrypt_message(test_message)
    if encrypted_data:
        decrypted_message = await security_manager.decrypt_message(encrypted_data)
        print(f"Original: {test_message}")
        print(f"Decrypted: {decrypted_message}")
        print(f"Encryption successful: {test_message == decrypted_message}")
    
    # Test digital signature
    signature = await security_manager.sign_message(test_message)
    if signature:
        is_valid = await security_manager.verify_signature(test_message, signature)
        print(f"Signature valid: {is_valid}")
    
    # Perform health check
    health_status = await security_manager.security_health_check()
    print(f"Security health: {health_status['overall_status']}")


if __name__ == "__main__":
    asyncio.run(main())