"""
🔐🎫 JWT HANDLER - ENTERPRISE JWT AUTHENTICATION MODULE 🎫🔐
Enterprise JWT Token Management for IA Chérie Platform
Copyright (C) 2024 IA Chérie Platform. All Rights Reserved.
"""

import logging
import jwt
import secrets
from typing import Dict, Optional, Any, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class TokenType(Enum):
    """🎫 Token Types"""
    ACCESS = "access"
    REFRESH = "refresh"
    API = "api"
    RESET = "reset"
    VERIFICATION = "verification"

class Algorithm(Enum):
    """🔐 JWT Algorithms"""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"

@dataclass
class TokenPayload:
    """🎫 JWT Token Payload"""
    user_id: str = ""
    username: str = ""
    email: str = ""
    roles: List[str] = None
    permissions: List[str] = None
    token_type: TokenType = TokenType.ACCESS
    issued_at: datetime = None
    expires_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []
        if self.issued_at is None:
            self.issued_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TokenResult:
    """🎫 JWT Token Result"""
    token: str = ""
    payload: Optional[TokenPayload] = None
    is_valid: bool = False
    error_message: str = ""
    expires_in: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class JWTHandler:
    """🔐🎫 Enterprise JWT Handler"""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: Algorithm = Algorithm.HS256):
        self.initialized = False
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = algorithm
        self.token_cache: Dict[str, TokenPayload] = {}
        self.blacklisted_tokens: set = set()
        self.logger = logging.getLogger(f"{__name__}.JWTHandler")
        
        # Token expiration times (in seconds)
        self.token_expiration = {
            TokenType.ACCESS: 3600,      # 1 hour
            TokenType.REFRESH: 86400 * 7, # 7 days
            TokenType.API: 86400 * 30,    # 30 days
            TokenType.RESET: 1800,        # 30 minutes
            TokenType.VERIFICATION: 3600   # 1 hour
        }
        
        self._initialize_handler()
        
    def _initialize_handler(self):
        """🔧 Initialize JWT Handler"""
        try:
            # Validate secret key
            if len(self.secret_key) < 32:
                self.logger.warning("⚠️ JWT secret key is short, generating stronger key")
                self.secret_key = self._generate_secret_key()
            
            # Test JWT operations
            test_payload = TokenPayload(user_id="test", username="test_user")
            test_token = self.generate_token(test_payload)
            
            if test_token.is_valid:
                verify_result = self.verify_token(test_token.token)
                if verify_result.is_valid:
                    self.initialized = True
                    self.logger.info("🔐 JWT Handler initialized successfully")
                else:
                    raise Exception("JWT verification test failed")
            else:
                raise Exception("JWT generation test failed")
            
        except Exception as e:
            self.logger.error(f"❌ JWT Handler initialization failed: {e}")
            self.initialized = False
    
    def _generate_secret_key(self) -> str:
        """🔑 Generate Secure Secret Key"""
        return secrets.token_urlsafe(64)
    
    def generate_token(self, payload: TokenPayload, 
                      custom_expiration: Optional[int] = None) -> TokenResult:
        """🎫 Generate JWT Token"""
        try:
            # Set expiration time
            expiration_seconds = custom_expiration or self.token_expiration.get(
                payload.token_type, 3600
            )
            
            if payload.expires_at is None:
                payload.expires_at = datetime.utcnow() + timedelta(seconds=expiration_seconds)
            
            # Create JWT payload
            jwt_payload = {
                'user_id': payload.user_id,
                'username': payload.username,
                'email': payload.email,
                'roles': payload.roles,
                'permissions': payload.permissions,
                'token_type': payload.token_type.value,
                'iat': int(payload.issued_at.timestamp()),
                'exp': int(payload.expires_at.timestamp()),
                'jti': secrets.token_hex(16),  # JWT ID
                'metadata': payload.metadata
            }
            
            # Generate token
            token = jwt.encode(
                jwt_payload,
                self.secret_key,
                algorithm=self.algorithm.value
            )
            
            # Cache payload
            self.token_cache[token] = payload
            
            result = TokenResult(
                token=token,
                payload=payload,
                is_valid=True,
                expires_in=expiration_seconds,
                metadata={
                    'algorithm': self.algorithm.value,
                    'token_type': payload.token_type.value
                }
            )
            
            self.logger.info(f"🎫 JWT token generated for user: {payload.user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ JWT token generation failed: {e}")
            return TokenResult(
                is_valid=False,
                error_message=f"Token generation error: {str(e)}"
            )
    
    def verify_token(self, token: str, verify_expiration: bool = True) -> TokenResult:
        """✅ Verify JWT Token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                return TokenResult(
                    token=token,
                    is_valid=False,
                    error_message="Token has been revoked"
                )
            
            # Check cache first
            if token in self.token_cache:
                cached_payload = self.token_cache[token]
                if verify_expiration and datetime.utcnow() > cached_payload.expires_at:
                    del self.token_cache[token]
                    return TokenResult(
                        token=token,
                        is_valid=False,
                        error_message="Token has expired"
                    )
                
                return TokenResult(
                    token=token,
                    payload=cached_payload,
                    is_valid=True,
                    metadata={'source': 'cache'}
                )
            
            # Decode and verify token
            decoded_payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm.value],
                options={'verify_exp': verify_expiration}
            )
            
            # Create payload object
            payload = TokenPayload(
                user_id=decoded_payload.get('user_id', ''),
                username=decoded_payload.get('username', ''),
                email=decoded_payload.get('email', ''),
                roles=decoded_payload.get('roles', []),
                permissions=decoded_payload.get('permissions', []),
                token_type=TokenType(decoded_payload.get('token_type', 'access')),
                issued_at=datetime.fromtimestamp(decoded_payload.get('iat', 0)),
                expires_at=datetime.fromtimestamp(decoded_payload.get('exp', 0)),
                metadata=decoded_payload.get('metadata', {})
            )
            
            # Cache payload
            self.token_cache[token] = payload
            
            result = TokenResult(
                token=token,
                payload=payload,
                is_valid=True,
                expires_in=int((payload.expires_at - datetime.utcnow()).total_seconds()),
                metadata={
                    'jti': decoded_payload.get('jti'),
                    'algorithm': self.algorithm.value
                }
            )
            
            self.logger.debug(f"✅ JWT token verified for user: {payload.user_id}")
            return result
            
        except jwt.ExpiredSignatureError:
            self.logger.warning(f"⚠️ JWT token expired: {token[:20]}...")
            return TokenResult(
                token=token,
                is_valid=False,
                error_message="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"⚠️ JWT token invalid: {str(e)}")
            return TokenResult(
                token=token,
                is_valid=False,
                error_message=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"❌ JWT token verification failed: {e}")
            return TokenResult(
                token=token,
                is_valid=False,
                error_message=f"Verification error: {str(e)}"
            )
    
    def refresh_token(self, refresh_token: str) -> TokenResult:
        """🔄 Refresh Access Token"""
        try:
            # Verify refresh token
            refresh_result = self.verify_token(refresh_token)
            
            if not refresh_result.is_valid:
                return TokenResult(
                    is_valid=False,
                    error_message="Invalid refresh token"
                )
            
            if refresh_result.payload.token_type != TokenType.REFRESH:
                return TokenResult(
                    is_valid=False,
                    error_message="Token is not a refresh token"
                )
            
            # Generate new access token
            new_payload = TokenPayload(
                user_id=refresh_result.payload.user_id,
                username=refresh_result.payload.username,
                email=refresh_result.payload.email,
                roles=refresh_result.payload.roles,
                permissions=refresh_result.payload.permissions,
                token_type=TokenType.ACCESS,
                metadata=refresh_result.payload.metadata
            )
            
            new_token = self.generate_token(new_payload)
            
            if new_token.is_valid:
                self.logger.info(f"🔄 Token refreshed for user: {new_payload.user_id}")
            
            return new_token
            
        except Exception as e:
            self.logger.error(f"❌ Token refresh failed: {e}")
            return TokenResult(
                is_valid=False,
                error_message=f"Refresh error: {str(e)}"
            )
    
    def revoke_token(self, token: str) -> bool:
        """🚫 Revoke Token"""
        try:
            # Add to blacklist
            self.blacklisted_tokens.add(token)
            
            # Remove from cache
            if token in self.token_cache:
                del self.token_cache[token]
            
            self.logger.info(f"🚫 JWT token revoked: {token[:20]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Token revocation failed: {e}")
            return False
    
    def decode_token_payload(self, token: str, verify: bool = False) -> Optional[Dict[str, Any]]:
        """📋 Decode Token Payload (without verification)"""
        try:
            if verify:
                result = self.verify_token(token)
                if result.is_valid and result.payload:
                    return {
                        'user_id': result.payload.user_id,
                        'username': result.payload.username,
                        'email': result.payload.email,
                        'roles': result.payload.roles,
                        'permissions': result.payload.permissions,
                        'token_type': result.payload.token_type.value,
                        'issued_at': result.payload.issued_at.isoformat(),
                        'expires_at': result.payload.expires_at.isoformat(),
                        'metadata': result.payload.metadata
                    }
            else:
                # Decode without verification
                decoded = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_exp": False}
                )
                return decoded
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Token payload decoding failed: {e}")
            return None
    
    def create_user_tokens(self, user_id: str, username: str, email: str,
                          roles: List[str] = None, permissions: List[str] = None) -> Dict[str, TokenResult]:
        """👤 Create Access and Refresh Tokens for User"""
        try:
            if roles is None:
                roles = ['user']
            if permissions is None:
                permissions = ['read']
            
            # Create access token
            access_payload = TokenPayload(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles,
                permissions=permissions,
                token_type=TokenType.ACCESS
            )
            
            access_token = self.generate_token(access_payload)
            
            # Create refresh token
            refresh_payload = TokenPayload(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles,
                permissions=permissions,
                token_type=TokenType.REFRESH
            )
            
            refresh_token = self.generate_token(refresh_payload)
            
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
            self.logger.info(f"👤 User tokens created for: {username}")
            return tokens
            
        except Exception as e:
            self.logger.error(f"❌ User tokens creation failed: {e}")
            return {}
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """📋 Get Token Information"""
        try:
            result = self.verify_token(token, verify_expiration=False)
            
            if result.payload:
                time_remaining = int((result.payload.expires_at - datetime.utcnow()).total_seconds())
                
                return {
                    'is_valid': result.is_valid,
                    'user_id': result.payload.user_id,
                    'username': result.payload.username,
                    'token_type': result.payload.token_type.value,
                    'issued_at': result.payload.issued_at.isoformat(),
                    'expires_at': result.payload.expires_at.isoformat(),
                    'time_remaining': max(0, time_remaining),
                    'is_expired': time_remaining <= 0,
                    'roles': result.payload.roles,
                    'permissions': result.payload.permissions
                }
            
            return {
                'is_valid': False,
                'error': result.error_message
            }
            
        except Exception as e:
            self.logger.error(f"❌ Token info retrieval failed: {e}")
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    def cleanup_expired_tokens(self):
        """🧹 Cleanup Expired Tokens from Cache"""
        try:
            current_time = datetime.utcnow()
            expired_tokens = []
            
            for token, payload in self.token_cache.items():
                if current_time > payload.expires_at:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.token_cache[token]
            
            if expired_tokens:
                self.logger.info(f"🧹 Cleaned up {len(expired_tokens)} expired tokens")
            
        except Exception as e:
            self.logger.error(f"❌ Token cleanup failed: {e}")
    
    def set_token_expiration(self, token_type: TokenType, seconds: int):
        """⏰ Set Token Expiration Time"""
        self.token_expiration[token_type] = seconds
        self.logger.info(f"⏰ Token expiration set for {token_type.value}: {seconds} seconds")
    
    def is_initialized(self) -> bool:
        """✅ Check Initialization Status"""
        return self.initialized

# Instance globale
jwt_handler = JWTHandler()

if jwt_handler.is_initialized():
    logger.info("🚀💯🔥 JWT HANDLER MODULE LOADED - AUTHENTICATION FOUNDATION! 🔥💯🚀")
    logger.info("✅ Enterprise JWT token management with refresh and revocation operational!")
    logger.info("🏆 CRITICAL JWT MODULE FOR 100% SUCCESS ACHIEVED!")

__all__ = [
    'JWTHandler',
    'TokenPayload',
    'TokenResult',
    'TokenType',
    'Algorithm',
    'jwt_handler',
]