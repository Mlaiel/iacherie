"""
import logging

Core Security Components for Ainflue Platform
Provides encryption, hashing, token management, and security utilities
"""

import hashlib
import secrets
import base64
import hmac
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from .logging import get_logger

logger = get_logger("security")


class SecurityManager:
    """Main security manager for the platform"""
    
    def __init__(self, secret_key -> None: Optional[str] = None) -> None:
        self.secret_key = secret_key or self._generate_secret_key()
        self.logger = get_logger("security_manager")
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> str:
        """Generate a secure hash of data"""
        if salt is None:
            salt = secrets.token_urlsafe(16)
        
        combined = f"{data}{salt}".encode('utf-8')
        hash_obj = hashlib.sha256(combined)
        
        return f"{hash_obj.hexdigest()}:{salt}"
    
    def verify_hash(self, data: str, hash_with_salt: str) -> bool:
        """Verify a hash against data"""
        try:
            hash_part, salt = hash_with_salt.split(':')
            new_hash = self.generate_secure_hash(data, salt)
            new_hash_part = new_hash.split(':')[0]
            
            return hmac.compare_digest(hash_part, new_hash_part)
        except Exception as e:
            self.logger.error(f"Hash verification error: {str(e)}")
            return False
    
    def generate_encryption_key(self) -> str:
        """Generate an encryption key"""
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    def encrypt_data(self, data: str, key: Optional[str] = None) -> str:
        """Basic encryption (for demo purposes - use proper encryption in production)"""
        if key is None:
            key = self.secret_key
        
        # Simple XOR encryption for demonstration
        # In production, use proper encryption like AES
        data_bytes = data.encode('utf-8')
        key_bytes = key.encode('utf-8')
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str, key: Optional[str] = None) -> str:
        """Basic decryption (for demo purposes - use proper encryption in production)"""
        if key is None:
            key = self.secret_key
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            key_bytes = key.encode('utf-8')
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            return ""


class TokenManager:
    """Manages security tokens and API keys"""
    
    def __init__(self, expiry_hours -> None: int = 24) -> None:
        self.expiry_hours = expiry_hours
        self.logger = get_logger("token_manager")
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
    
    def generate_token(self, user_id: str, additional_data: Optional[Dict] = None) -> str:
        """Generate a secure token for a user"""
        token_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=self.expiry_hours),
            'additional_data': additional_data or {}
        }
        
        token = secrets.token_urlsafe(32)
        self.active_tokens[token] = token_data
        
        self.logger.info(f"Token generated for user: {user_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a token and return its data"""
        if token not in self.active_tokens:
            self.logger.warning(f"Invalid token attempted: {token[:8]}...")
            return None
        
        token_data = self.active_tokens[token]
        
        if datetime.utcnow() > token_data['expires_at']:
            self.logger.warning(f"Expired token attempted: {token[:8]}...")
            del self.active_tokens[token]
            return None
        
        return token_data
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        if token in self.active_tokens:
            del self.active_tokens[token]
            self.logger.info(f"Token revoked: {token[:8]}...")
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens and return count removed"""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, data in self.active_tokens.items()
            if current_time > data['expires_at']
        ]
        
        for token in expired_tokens:
            del self.active_tokens[token]
        
        if expired_tokens:
            self.logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        
        return len(expired_tokens)


class SecurityValidator:
    """Validates security requirements and policies"""
    
    def __init__(self) -> None:
        self.logger = get_logger("security_validator")
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            'is_valid': True,
            'score': 0,
            'issues': []
        }
        
        if len(password) < 8:
            result['issues'].append("Password must be at least 8 characters long")
            result['is_valid'] = False
        else:
            result['score'] += 1
        
        if not any(c.isupper() for c in password):
            result['issues'].append("Password must contain at least one uppercase letter")
            result['is_valid'] = False
        else:
            result['score'] += 1
        
        if not any(c.islower() for c in password):
            result['issues'].append("Password must contain at least one lowercase letter") 
            result['is_valid'] = False
        else:
            result['score'] += 1
        
        if not any(c.isdigit() for c in password):
            result['issues'].append("Password must contain at least one number")
            result['is_valid'] = False
        else:
            result['score'] += 1
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result['issues'].append("Password must contain at least one special character")
        else:
            result['score'] += 1
        
        return result
    
    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def check_rate_limit_violation(self, client_id: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """Check if client has exceeded rate limits"""
        # This would typically check against a database or cache
        # For this implementation, it's a placeholder
        self.logger.debug(f"Rate limit check for client: {client_id}")
        return False


# Factory functions
def create_security_manager(secret_key: Optional[str] = None) -> SecurityManager:
    """Create a security manager instance"""
    return SecurityManager(secret_key=secret_key)


def create_token_manager(expiry_hours: int = 24) -> TokenManager:
    """Create a token manager instance"""
    return TokenManager(expiry_hours=expiry_hours)


def create_security_validator() -> SecurityValidator:
    """Create a security validator instance"""
    return SecurityValidator()


__all__ = [
    "SecurityManager",
    "TokenManager", 
    "SecurityValidator",
    "create_security_manager",
    "create_token_manager",
    "create_security_validator"
]