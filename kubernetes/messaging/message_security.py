"""
IA Influencer Agent - Message Security & Encryption
Enterprise security layer for messaging infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import base64
import hashlib
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SecurityConfig(BaseModel):
    """Security configuration for messaging"""
    encryption_enabled: bool = Field(default=True, description="Enable message encryption")
    signing_enabled: bool = Field(default=True, description="Enable message signing")
    key_rotation_interval: int = Field(default=86400, description="Key rotation interval in seconds")
    max_message_age: int = Field(default=3600, description="Maximum message age in seconds")
    audit_logging: bool = Field(default=True, description="Enable audit logging")
    rate_limiting: bool = Field(default=True, description="Enable rate limiting")


class MessageSecurityManager:
    """
    Enterprise message security manager
    Handles encryption, signing, and security validation for messaging
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.encryption_key: Optional[bytes] = None
        self.signing_key: Optional[rsa.RSAPrivateKey] = None
        self.verification_key: Optional[rsa.RSAPublicKey] = None
        self.fernet: Optional[Fernet] = None
        
        # Security audit log
        self.audit_events: list = []
        
        self._initialize_security()

    def _initialize_security(self) -> None:
        """Initialize security components"""



        try:
            # Generate or load encryption key
            self._setup_encryption_key()
            
            # Generate or load signing keys
            self._setup_signing_keys()
            
            # Setup Fernet for symmetric encryption
            if self.encryption_key:
                self.fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
            
            logger.info("Message security manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize security: {e}")
            raise

    def _setup_encryption_key(self) -> None:
        """Setup symmetric encryption key"""



        try:
            # Try to load existing key
            key_file = "messaging_encryption.key"
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate new key
                self.encryption_key = os.urandom(32)  # 256-bit key
                
                # Save key
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                
                os.chmod(key_file, 0o600)  # Restrict permissions
                
            logger.info("Encryption key setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup encryption key: {e}")
            raise

    def _setup_signing_keys(self) -> None:
        """Setup RSA key pair for message signing"""



        try:
            private_key_file = "messaging_signing_private.pem"
            public_key_file = "messaging_signing_public.pem"
            
            # Try to load existing keys
            if os.path.exists(private_key_file) and os.path.exists(public_key_file):
                # Load private key
                with open(private_key_file, 'rb') as f:
                    private_key_data = f.read()
                self.signing_key = serialization.load_pem_private_key(
                    private_key_data, password=None
                )
                
                # Load public key
                with open(public_key_file, 'rb') as f:
                    public_key_data = f.read()
                self.verification_key = serialization.load_pem_public_key(public_key_data)
                
            else:
                # Generate new key pair
                self.signing_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                self.verification_key = self.signing_key.public_key()
                
                # Save private key
                private_pem = self.signing_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                with open(private_key_file, 'wb') as f:
                    f.write(private_pem)
                os.chmod(private_key_file, 0o600)
                
                # Save public key
                public_pem = self.verification_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                with open(public_key_file, 'wb') as f:
                    f.write(public_pem)
                
            logger.info("Signing keys setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup signing keys: {e}")
            raise

    def encrypt_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a message"""



        try:
            if not self.config.encryption_enabled or not self.fernet:
                return message
            
            # Serialize message
            message_str = str(message).encode()
            
            # Encrypt message
            encrypted_data = self.fernet.encrypt(message_str)
            
            # Create encrypted message envelope
            encrypted_message = {
                "encrypted": True,
                "data": base64.b64encode(encrypted_data).decode(),
                "timestamp": time.time(),
                "algorithm": "fernet"
            }
            
            # Log security event
            self._log_security_event("message_encrypted", {
                "message_size": len(message_str),
                "encrypted_size": len(encrypted_data)
            })
            
            return encrypted_message
            
        except Exception as e:
            logger.error(f"Failed to encrypt message: {e}")
            self._log_security_event("encryption_failed", {"error": str(e)})
            raise

    def decrypt_message(self, encrypted_message: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt a message"""



        try:
            if not encrypted_message.get("encrypted", False):
                return encrypted_message
            
            if not self.fernet:
                raise ValueError("Encryption not initialized")
            
            # Validate message age
            message_age = time.time() - encrypted_message.get("timestamp", 0)
            if message_age > self.config.max_message_age:
                raise ValueError("Message too old")
            
            # Decode and decrypt
            encrypted_data = base64.b64decode(encrypted_message["data"])
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Deserialize message
            message = eval(decrypted_data.decode())  # In production, use proper JSON
            
            # Log security event
            self._log_security_event("message_decrypted", {
                "message_age": message_age,
                "decrypted_size": len(decrypted_data)
            })
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}")
            self._log_security_event("decryption_failed", {"error": str(e)})
            raise

    def sign_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a message for integrity verification"""



        try:
            if not self.config.signing_enabled or not self.signing_key:
                return message
            
            # Create message hash
            message_str = str(sorted(message.items())).encode()
            message_hash = hashlib.sha256(message_str).digest()
            
            # Sign hash
            signature = self.signing_key.sign(
                message_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Add signature to message
            signed_message = message.copy()
            signed_message["_signature"] = base64.b64encode(signature).decode()
            signed_message["_signed_at"] = time.time()
            signed_message["_hash_algorithm"] = "sha256"
            
            # Log security event
            self._log_security_event("message_signed", {
                "message_size": len(message_str),
                "signature_size": len(signature)
            })
            
            return signed_message
            
        except Exception as e:
            logger.error(f"Failed to sign message: {e}")
            self._log_security_event("signing_failed", {"error": str(e)})
            raise

    def verify_message_signature(self, signed_message: Dict[str, Any]) -> bool:
        """Verify message signature"""



        try:
            if "_signature" not in signed_message:
                return not self.config.signing_enabled  # Allow unsigned if signing disabled
            
            if not self.verification_key:
                raise ValueError("Verification key not available")
            
            # Extract signature and create message copy
            signature = base64.b64decode(signed_message["_signature"])
            message = signed_message.copy()
            
            # Remove signature fields
            del message["_signature"]
            del message["_signed_at"]
            del message["_hash_algorithm"]
            
            # Create message hash
            message_str = str(sorted(message.items())).encode()
            message_hash = hashlib.sha256(message_str).digest()
            
            # Verify signature
            try:
                self.verification_key.verify(
                    signature,
                    message_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                # Log security event
                self._log_security_event("signature_verified", {
                    "message_size": len(message_str)
                })
                
                return True
                
            except Exception:
                # Log security event
                self._log_security_event("signature_verification_failed", {
                    "message_size": len(message_str)
                })
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify signature: {e}")
            self._log_security_event("verification_error", {"error": str(e)})
            return False

    def secure_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply full security to message (sign + encrypt)"""



        try:
            # First sign the message
            signed_message = self.sign_message(message)
            
            # Then encrypt the signed message
            encrypted_message = self.encrypt_message(signed_message)
            
            return encrypted_message
            
        except Exception as e:
            logger.error(f"Failed to secure message: {e}")
            raise

    def unsecure_message(self, secured_message: Dict[str, Any]) -> Dict[str, Any]:
        """Remove security from message (decrypt + verify)"""



        try:
            # First decrypt the message
            decrypted_message = self.decrypt_message(secured_message)
            
            # Then verify signature
            if not self.verify_message_signature(decrypted_message):
                raise ValueError("Message signature verification failed")
            
            # Remove signature fields for clean message
            clean_message = decrypted_message.copy()
            for key in ["_signature", "_signed_at", "_hash_algorithm"]:
                clean_message.pop(key, None)
            
            return clean_message
            
        except Exception as e:
            logger.error(f"Failed to unsecure message: {e}")
            raise

    def generate_message_id(self, message: Dict[str, Any]) -> str:
        """Generate secure message ID"""



        try:
            # Create deterministic hash of message content
            message_str = str(sorted(message.items())).encode()
            message_hash = hashlib.sha256(message_str).digest()
            
            # Add timestamp for uniqueness
            timestamp = str(time.time()).encode()
            combined_hash = hashlib.sha256(message_hash + timestamp).digest()
            
            # Return base64 encoded ID
            return base64.urlsafe_b64encode(combined_hash[:16]).decode().rstrip('=')
            
        except Exception as e:
            logger.error(f"Failed to generate message ID: {e}")
            return f"msg_{int(time.time())}"

    def validate_message_format(self, message: Dict[str, Any]) -> bool:
        """Validate message format and security"""



        try:
            # Basic format validation
            if not isinstance(message, dict):
                return False
            
            # Check required fields
            required_fields = ["timestamp", "type"]
            for field in required_fields:
                if field not in message:
                    logger.warning(f"Message missing required field: {field}")
                    return False
            
            # Validate timestamp
            message_timestamp = message.get("timestamp", 0)
            current_time = time.time()
            message_age = current_time - message_timestamp
            
            if message_age > self.config.max_message_age:
                logger.warning(f"Message too old: {message_age}s")
                return False
            
            if message_timestamp > current_time + 300:  # 5 minutes future tolerance
                logger.warning("Message timestamp in future")
                return False
            
            # Validate message size
            message_size = len(str(message))
            if message_size > 1048576:  # 1MB limit
                logger.warning(f"Message too large: {message_size} bytes")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Message validation error: {e}")
            return False

    def sanitize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize message content"""



        try:
            sanitized = {}
            
            for key, value in message.items():
                # Skip security fields
                if key.startswith("_"):
                    continue
                
                # Sanitize string values
                if isinstance(value, str):
                    # Remove potential script tags and harmful content
                    value = value.replace("<script", "&lt;script")
                    value = value.replace("javascript:", "")
                    
                    # Limit string length
                    if len(value) > 10000:
                        value = value[:10000] + "..."
                
                # Recursively sanitize nested dictionaries
                elif isinstance(value, dict):
                    value = self.sanitize_message(value)
                
                # Sanitize lists
                elif isinstance(value, list):
                    value = [self.sanitize_message(item) if isinstance(item, dict) else item for item in value]
                
                sanitized[key] = value
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Message sanitization error: {e}")
            return message

    def _log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security event for audit"""



        try:
            if not self.config.audit_logging:
                return
            
            event = {
                "timestamp": time.time(),
                "event_type": event_type,
                "details": details
            }
            
            self.audit_events.append(event)
            
            # Keep only last 1000 events
            if len(self.audit_events) > 1000:
                self.audit_events = self.audit_events[-1000:]
            
            # Log to file/database in production
            logger.info(f"Security event: {event_type} - {details}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    def rotate_keys(self) -> bool:
        """Rotate encryption and signing keys"""



        try:
            logger.info("Starting key rotation")
            
            # Backup current keys
            self._backup_current_keys()
            
            # Generate new encryption key
            self.encryption_key = os.urandom(32)
            self.fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
            
            # Generate new signing key pair
            self.signing_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.verification_key = self.signing_key.public_key()
            
            # Save new keys
            self._save_keys()
            
            # Log security event
            self._log_security_event("keys_rotated", {
                "rotation_time": time.time()
            })
            
            logger.info("Key rotation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            self._log_security_event("key_rotation_failed", {"error": str(e)})
            return False

    def _backup_current_keys(self) -> None:
        """Backup current keys before rotation"""



        try:
            import shutil
            timestamp = int(time.time())
            
            # Backup encryption key
            if os.path.exists("messaging_encryption.key"):
                shutil.copy2("messaging_encryption.key", f"messaging_encryption.key.{timestamp}")
            
            # Backup signing keys
            if os.path.exists("messaging_signing_private.pem"):
                shutil.copy2("messaging_signing_private.pem", f"messaging_signing_private.pem.{timestamp}")
            
            if os.path.exists("messaging_signing_public.pem"):
                shutil.copy2("messaging_signing_public.pem", f"messaging_signing_public.pem.{timestamp}")
                
        except Exception as e:
            logger.error(f"Failed to backup keys: {e}")

    def _save_keys(self) -> None:
        """Save current keys to files"""



        try:
            # Save encryption key
            with open("messaging_encryption.key", 'wb') as f:
                f.write(self.encryption_key)
            os.chmod("messaging_encryption.key", 0o600)
            
            # Save signing keys
            private_pem = self.signing_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            with open("messaging_signing_private.pem", 'wb') as f:
                f.write(private_pem)
            os.chmod("messaging_signing_private.pem", 0o600)
            
            public_pem = self.verification_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open("messaging_signing_public.pem", 'wb') as f:
                f.write(public_pem)
                
        except Exception as e:
            logger.error(f"Failed to save keys: {e}")
            raise

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""



        try:
            # Count events by type
            event_counts = {}
            for event in self.audit_events:
                event_type = event["event_type"]
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            return {
                "encryption_enabled": self.config.encryption_enabled,
                "signing_enabled": self.config.signing_enabled,
                "audit_logging": self.config.audit_logging,
                "total_audit_events": len(self.audit_events),
                "event_counts": event_counts,
                "key_rotation_interval": self.config.key_rotation_interval,
                "max_message_age": self.config.max_message_age
            }
            
        except Exception as e:
            logger.error(f"Failed to get security stats: {e}")
            return {"error": str(e)}

    def get_audit_events(self, limit: int = 100) -> list:
        """Get recent audit events"""



        try:
            return self.audit_events[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
