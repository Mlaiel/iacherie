"""
Security Utilities for Content Protection

Advanced security utilities for encryption, authentication, and secure
communication in the DMCA automation and content protection system.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Project: IA Influencer Agent Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

 COPYRIGHT & LICENSE WARNING 
This code is proprietary and confidential. Any unauthorized copying, modification,
distribution, or use without explicit written permission from Fahed Mlaiel is strictly
prohibited and will result in legal action.

All rights reserved © 2025 Fahed Mlaiel
"""

import os
import base64
import hashlib
import hmac
import secrets
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import jwt

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class ContentProtectionSecurityService:
    """
    Advanced security service for content protection operations
    
    Features:
    - AES-256 encryption/decryption
    - RSA key pair generation and management
    - JWT token generation and validation
    - Secure hash generation
    - Digital signatures
    - API key management
    - Rate limiting tokens
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security service"""
        self.config = config or {}
        self.logger = logger
        
        # Get or generate master key
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        
        # JWT configuration
        self.jwt_secret = self.config.get('jwt_secret', self._generate_jwt_secret())
        self.jwt_algorithm = self.config.get('jwt_algorithm', 'HS256')
        self.jwt_expiry_hours = self.config.get('jwt_expiry_hours', 24)
        
        # Security settings
        self.min_password_length = self.config.get('min_password_length', 12)
        self.max_failed_attempts = self.config.get('max_failed_attempts', 5)
        self.lockout_duration_minutes = self.config.get('lockout_duration_minutes', 30)
    
    def encrypt_sensitive_data(self, data: Union[str, bytes], 
                             additional_context: Optional[str] = None) -> str:
        """
        Encrypt sensitive data using AES-256
        
        Args:
            data: Data to encrypt (string or bytes)
            additional_context: Optional additional context for encryption
            
        Returns:
            Base64-encoded encrypted data
        """



        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Add context if provided
            if additional_context:
                context_hash = hashlib.sha256(additional_context.encode('utf-8')).digest()
                data = context_hash + data
            
            # Encrypt data
            encrypted_data = self.fernet.encrypt(data)
            
            # Return base64-encoded result
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise SecurityError(f"Encryption failed: {str(e)}")
    
    def decrypt_sensitive_data(self, encrypted_data: str,
                             additional_context: Optional[str] = None) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            additional_context: Optional additional context used during encryption
            
        Returns:
            Decrypted data as string
        """



        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt data
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # Remove context if it was added
            if additional_context:
                context_hash = hashlib.sha256(additional_context.encode('utf-8')).digest()
                if decrypted_data.startswith(context_hash):
                    decrypted_data = decrypted_data[32:]  # Remove 32-byte hash
                else:
                    raise SecurityError("Invalid encryption context")
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise SecurityError(f"Decryption failed: {str(e)}")
    
    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Generate secure hash with optional salt
        
        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Dictionary with hash and salt
        """



        try:
            if salt is None:
                salt = secrets.token_hex(32)
            
            # Combine data and salt
            combined = f"{data}{salt}"
            
            # Generate multiple hashes for extra security
            sha256_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            sha512_hash = hashlib.sha512(combined.encode('utf-8')).hexdigest()
            
            # Use PBKDF2 for additional security
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode('utf-8'),
                iterations=100000,
                backend=default_backend()
            )
            pbkdf2_hash = base64.b64encode(kdf.derive(data.encode('utf-8'))).decode('utf-8')
            
            return {
                'sha256': sha256_hash,
                'sha512': sha512_hash,
                'pbkdf2': pbkdf2_hash,
                'salt': salt,
                'algorithm': 'PBKDF2-SHA256',
                'iterations': 100000
            }
            
        except Exception as e:
            self.logger.error(f"Hash generation failed: {str(e)}")
            raise SecurityError(f"Hash generation failed: {str(e)}")
    
    def verify_secure_hash(self, data: str, stored_hash: Dict[str, str]) -> bool:
        """
        Verify data against stored hash
        
        Args:
            data: Original data to verify
            stored_hash: Dictionary containing hash and salt
            
        Returns:
            True if verification successful, False otherwise
        """



        try:
            # Regenerate hash with stored salt
            new_hash = self.generate_secure_hash(data, stored_hash['salt'])
            
            # Compare hashes (use PBKDF2 for primary comparison)
            return hmac.compare_digest(new_hash['pbkdf2'], stored_hash['pbkdf2'])
            
        except Exception as e:
            self.logger.error(f"Hash verification failed: {str(e)}")
            return False
    
    def generate_api_key(self, user_id: str, permissions: List[str],
                        expiry_days: int = 365) -> Dict[str, Any]:
        """
        Generate secure API key with permissions
        
        Args:
            user_id: User identifier
            permissions: List of permissions
            expiry_days: Days until expiration
            
        Returns:
            API key information
        """



        try:
            # Generate secure random key
            api_key = secrets.token_urlsafe(32)
            
            # Create key metadata
            created_at = datetime.now(timezone.utc)
            expires_at = created_at + timedelta(days=expiry_days)
            
            key_data = {
                'user_id': user_id,
                'permissions': permissions,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'key_id': secrets.token_hex(16)
            }
            
            # Create secure hash of key data
            key_hash = self.generate_secure_hash(f"{api_key}{user_id}")
            
            return {
                'api_key': api_key,
                'key_id': key_data['key_id'],
                'user_id': user_id,
                'permissions': permissions,
                'created_at': key_data['created_at'],
                'expires_at': key_data['expires_at'],
                'key_hash': key_hash['pbkdf2'],
                'salt': key_hash['salt']
            }
            
        except Exception as e:
            self.logger.error(f"API key generation failed: {str(e)}")
            raise SecurityError(f"API key generation failed: {str(e)}")
    
    def validate_api_key(self, api_key: str, stored_key_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate API key against stored data
        
        Args:
            api_key: API key to validate
            stored_key_data: Stored key information
            
        Returns:
            Validation result
        """



        try:
            # Check expiration
            expires_at = datetime.fromisoformat(stored_key_data['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                return {
                    'valid': False,
                    'reason': 'API key expired',
                    'expired': True
                }
            
            # Verify key hash
            expected_hash = {
                'pbkdf2': stored_key_data['key_hash'],
                'salt': stored_key_data['salt']
            }
            
            key_valid = self.verify_secure_hash(
                f"{api_key}{stored_key_data['user_id']}", 
                expected_hash
            )
            
            if not key_valid:
                return {
                    'valid': False,
                    'reason': 'Invalid API key',
                    'expired': False
                }
            
            return {
                'valid': True,
                'user_id': stored_key_data['user_id'],
                'permissions': stored_key_data['permissions'],
                'expires_at': stored_key_data['expires_at']
            }
            
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'expired': False
            }
    
    def generate_jwt_token(self, payload: Dict[str, Any], 
                          expiry_hours: Optional[int] = None) -> str:
        """
        Generate JWT token with payload
        
        Args:
            payload: Token payload
            expiry_hours: Hours until expiration (uses default if not provided)
            
        Returns:
            JWT token string
        """



        try:
            # Set expiration time
            exp_hours = expiry_hours or self.jwt_expiry_hours
            exp_time = datetime.now(timezone.utc) + timedelta(hours=exp_hours)
            
            # Add standard claims
            token_payload = {
                **payload,
                'iat': datetime.now(timezone.utc),
                'exp': exp_time,
                'iss': 'content-protection-system',
                'jti': secrets.token_hex(16)  # Unique token ID
            }
            
            # Generate token
            token = jwt.encode(
                token_payload, 
                self.jwt_secret, 
                algorithm=self.jwt_algorithm
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"JWT generation failed: {str(e)}")
            raise SecurityError(f"JWT generation failed: {str(e)}")
    
    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode JWT token
        
        Args:
            token: JWT token to validate
            
        Returns:
            Validation result with payload if valid
        """



        try:
            # Decode and validate token
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload.get('user_id'),
                'permissions': payload.get('permissions', []),
                'expires_at': payload.get('exp')
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'reason': 'Token expired',
                'expired': True
            }
        except jwt.InvalidTokenError as e:
            return {
                'valid': False,
                'reason': f'Invalid token: {str(e)}',
                'expired': False
            }
        except Exception as e:
            self.logger.error(f"JWT validation failed: {str(e)}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'expired': False
            }
    
    def generate_rsa_key_pair(self, key_size: int = 2048) -> Dict[str, str]:
        """
        Generate RSA key pair for digital signatures
        
        Args:
            key_size: RSA key size in bits
            
        Returns:
            Dictionary with private and public keys
        """



        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                'private_key': private_pem.decode('utf-8'),
                'public_key': public_pem.decode('utf-8'),
                'key_size': key_size,
                'algorithm': 'RSA',
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"RSA key generation failed: {str(e)}")
            raise SecurityError(f"RSA key generation failed: {str(e)}")
    
    def create_digital_signature(self, data: str, private_key_pem: str) -> str:
        """
        Create digital signature for data
        
        Args:
            data: Data to sign
            private_key_pem: Private key in PEM format
            
        Returns:
            Base64-encoded signature
        """



        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            
            # Create signature
            signature = private_key.sign(
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Digital signature creation failed: {str(e)}")
            raise SecurityError(f"Digital signature creation failed: {str(e)}")
    
    def verify_digital_signature(self, data: str, signature: str, public_key_pem: str) -> bool:
        """
        Verify digital signature
        
        Args:
            data: Original data
            signature: Base64-encoded signature
            public_key_pem: Public key in PEM format
            
        Returns:
            True if signature is valid, False otherwise
        """



        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Decode signature
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Digital signature verification failed: {str(e)}")
            return False
    
    def generate_rate_limit_token(self, user_id: str, resource: str, 
                                limit: int, window_seconds: int) -> str:
        """
        Generate rate limiting token
        
        Args:
            user_id: User identifier
            resource: Resource being rate limited
            limit: Request limit
            window_seconds: Time window in seconds
            
        Returns:
            Rate limit token
        """



        try:
            current_time = int(datetime.now(timezone.utc).timestamp())
            window_start = current_time - (current_time % window_seconds)
            
            token_data = {
                'user_id': user_id,
                'resource': resource,
                'limit': limit,
                'window_start': window_start,
                'window_seconds': window_seconds
            }
            
            token = self.generate_jwt_token(token_data, expiry_hours=1)
            return token
            
        except Exception as e:
            self.logger.error(f"Rate limit token generation failed: {str(e)}")
            raise SecurityError(f"Rate limit token generation failed: {str(e)}")
    
    # Private helper methods
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = self.config.get('master_key_file', '.master_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key
    
    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret if not provided"""



        return secrets.token_urlsafe(64)


# Factory function
def create_security_service(config: Optional[Dict[str, Any]] = None) -> ContentProtectionSecurityService:
    """Factory function to create security service"""



    return ContentProtectionSecurityService(config)


# Convenience functions
def encrypt_sensitive_data(data: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function for encryption"""
    service = create_security_service(config)
    return service.encrypt_sensitive_data(data)


def decrypt_sensitive_data(encrypted_data: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function for decryption"""
    service = create_security_service(config)
    return service.decrypt_sensitive_data(encrypted_data)


def generate_secure_hash(data: str, salt: Optional[str] = None) -> Dict[str, str]:
    """Convenience function for hash generation"""
    service = create_security_service()
    return service.generate_secure_hash(data, salt)


# Compatibility aliases for business modules
class SecurityManager:
    """Security manager compatibility class for business modules"""
    
    def __init__(self):
        self._service = ContentProtectionSecurityService()
    
    def __getattr__(self, name):
        """Delegate to the underlying service"""



        return getattr(self._service, name)


class EncryptionManager:
    """Encryption manager compatibility class for business modules"""
    
    def __init__(self):
        self._service = ContentProtectionSecurityService()
    
    def encrypt(self, data: str, key: Optional[str] = None) -> str:
        """Encrypt data using the service"""



        return self._service.encrypt_data(data, key)
    
    def decrypt(self, encrypted_data: str, key: Optional[str] = None) -> str:
        """Decrypt data using the service"""



        return self._service.decrypt_data(encrypted_data, key)
    
    def __getattr__(self, name):
        """Delegate to the underlying service"""



        return getattr(self._service, name)


# Export all security components
__all__ = [
    'SecurityError',
    'ContentProtectionSecurityService',
    'SecurityManager',
    'EncryptionManager',
    'create_security_service',
    'encrypt_sensitive_data',
    'decrypt_sensitive_data',
    'generate_secure_hash'
]
