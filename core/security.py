"""
Security Management System
Advanced security features including JWT, OAuth2, encryption, and access control.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends, Request
import secrets
import hashlib
import time
from functools import wraps

from ..config import settings


class PasswordManager:
    """Advanced password hashing and verification"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        return self.pwd_context.hash(password + settings.security.password_salt)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password + settings.security.password_salt, hashed_password)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)


class EncryptionManager:
    """Advanced encryption for sensitive data"""
    
    def __init__(self):
        self.fernet = Fernet(settings.security.encryption_key.encode()[:44] + b'=')
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_dict(self, data_dict: Dict) -> Dict:
        """Encrypt dictionary values"""
        encrypted_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                encrypted_dict[key] = self.encrypt_data(value)
            else:
                encrypted_dict[key] = value
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_dict: Dict) -> Dict:
        """Decrypt dictionary values"""
        decrypted_dict = {}
        for key, value in encrypted_dict.items():
            if isinstance(value, str) and self._is_encrypted(value):
                try:
                    decrypted_dict[key] = self.decrypt_data(value)
                except Exception:
                    decrypted_dict[key] = value
            else:
                decrypted_dict[key] = value
        return decrypted_dict
    
    def _is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted"""
        try:
            self.fernet.decrypt(data.encode())
            return True
        except Exception:
            return False


class JWTManager:
    """Advanced JWT token management"""
    
    def __init__(self):
        self.secret_key = settings.security.jwt_secret_key
        self.algorithm = settings.security.jwt_algorithm
        self.access_token_expire = settings.security.jwt_access_token_expire
        self.refresh_token_expire = settings.security.jwt_refresh_token_expire
    
    def create_access_token(self, user_id: str, user_data: Dict = None, 
                          expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
        
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        if user_data:
            payload.update(user_data)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(seconds=self.refresh_token_expire)
        
        payload = {
            "sub": user_id,
            "type": "refresh", 
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return self.create_access_token(payload["sub"])


class RateLimiter:
    """Advanced rate limiting system"""
    
    def __init__(self):
        self.requests = {}
        self.max_requests = settings.security.rate_limit_requests
        self.window_seconds = settings.security.rate_limit_window
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limits"""
        current_time = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_time = time.time()
        
        if identifier not in self.requests:
            return self.max_requests
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(self.requests[identifier]))


class OAuth2Manager:
    """OAuth2 integration manager"""
    
    def __init__(self):
        self.google_client_id = settings.security.oauth2_google_client_id
        self.google_client_secret = settings.security.oauth2_google_client_secret
        self.github_client_id = settings.security.oauth2_github_client_id
        self.github_client_secret = settings.security.oauth2_github_client_secret
    
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify Google OAuth2 token"""
        # Implementation for Google token verification
        # This would integrate with Google's OAuth2 API
        pass
    
    async def verify_github_token(self, token: str) -> Dict[str, Any]:
        """Verify GitHub OAuth2 token"""
        # Implementation for GitHub token verification
        # This would integrate with GitHub's OAuth2 API
        pass


class MultiTenantManager:
    """Multi-tenant security and data isolation"""
    
    def __init__(self):
        self.tenant_cache = {}
    
    def get_tenant_id(self, user_id: str) -> str:
        """Get tenant ID for user"""
        # Hash user ID to create consistent tenant identifier
        return hashlib.sha256(f"tenant_{user_id}".encode()).hexdigest()[:16]
    
    def validate_tenant_access(self, user_id: str, resource_tenant_id: str) -> bool:
        """Validate user has access to tenant resources"""
        user_tenant_id = self.get_tenant_id(user_id)
        return user_tenant_id == resource_tenant_id
    
    def create_tenant_context(self, user_id: str) -> Dict[str, str]:
        """Create tenant context for database queries"""
        tenant_id = self.get_tenant_id(user_id)
        return {
            "tenant_id": tenant_id,
            "user_id": user_id
        }


class SecurityManager:
    """Main security manager orchestrating all security components"""
    
    def __init__(self):
        self.password_manager = PasswordManager()
        self.encryption_manager = EncryptionManager()
        self.jwt_manager = JWTManager()
        self.rate_limiter = RateLimiter()
        self.oauth2_manager = OAuth2Manager()
        self.multitenant_manager = MultiTenantManager()
        self.security_bearer = HTTPBearer(auto_error=False)
    
    async def authenticate_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """Authenticate user from JWT token"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        return self.jwt_manager.verify_token(credentials.credentials)
    
    async def get_current_user(self, token_data: Dict = Depends(authenticate_user)) -> Dict[str, Any]:
        """Get current authenticated user"""
        return {
            "user_id": token_data["sub"],
            "token_data": token_data
        }
    
    def require_permissions(self, required_permissions: List[str]):
        """Decorator to require specific permissions"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current user from kwargs
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Check permissions
                user_permissions = current_user.get("token_data", {}).get("permissions", [])
                
                for permission in required_permissions:
                    if permission not in user_permissions:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission '{permission}' required"
                        )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def check_rate_limit(self, request: Request) -> bool:
        """Check rate limit for request"""
        # Use IP address or user ID as identifier
        identifier = request.client.host
        
        if not self.rate_limiter.is_allowed(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return True
    
    def create_user_tokens(self, user_id: str, user_data: Dict = None) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        access_token = self.jwt_manager.create_access_token(user_id, user_data)
        refresh_token = self.jwt_manager.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def validate_content_access(self, user_id: str, content_user_id: str) -> bool:
        """Validate user has access to content"""
        return self.multitenant_manager.validate_tenant_access(user_id, 
                                                              self.multitenant_manager.get_tenant_id(content_user_id))


# Global security manager instance
security_manager = SecurityManager()