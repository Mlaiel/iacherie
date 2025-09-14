"""JWT Token Handler for Ainflue SDK

Multi-expert implementation:
- Security: Secure JWT handling with validation and encryption
- Backend Senior: Robust token processing and validation architecture
- DevOps: Token monitoring and metrics
- Lead Dev IA: Intelligent token optimization and caching strategies

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import base64
import json
import logging
import time
import hmac
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pydantic import BaseModel, Field

from .exceptions import (
    JWTError, TokenExpiredError, TokenInvalidError,
    ValidationError, SecurityError
)


class JWTAlgorithm(Enum):
    """JWT signing algorithms"""
    HS256 = "HS256"  # HMAC with SHA-256
    HS384 = "HS384"  # HMAC with SHA-384
    HS512 = "HS512"  # HMAC with SHA-512
    RS256 = "RS256"  # RSA with SHA-256
    RS384 = "RS384"  # RSA with SHA-384
    RS512 = "RS512"  # RSA with SHA-512
    ES256 = "ES256"  # ECDSA with SHA-256
    ES384 = "ES384"  # ECDSA with SHA-384
    ES512 = "ES512"  # ECDSA with SHA-512


class TokenType(Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    CUSTOM = "custom"


@dataclass
class JWTMetrics:
    """JWT processing metrics (DevOps expertise)"""
    tokens_generated: int = 0
    tokens_validated: int = 0
    validation_failures: int = 0
    expired_tokens: int = 0
    invalid_signatures: int = 0
    average_validation_time: float = 0.0
    total_validation_time: float = 0.0
    algorithm_usage: Dict[str, int] = field(default_factory=dict)
    
    @property
    def validation_success_rate(self) -> float:
        """Calculate token validation success rate"""
        if self.tokens_validated == 0:
            return 0.0
        successful = self.tokens_validated - self.validation_failures
        return (successful / self.tokens_validated) * 100
    
    def update_validation_time(self, validation_time -> None: float) -> None:
        """Update average validation time"""
        self.total_validation_time += validation_time
        if self.tokens_validated > 0:
            self.average_validation_time = self.total_validation_time / self.tokens_validated


class JWTConfig(BaseModel):
    """JWT configuration with security best practices"""
    # Algorithm settings
    algorithm: JWTAlgorithm = Field(default=JWTAlgorithm.HS256, description="JWT signing algorithm")
    
    # Signing keys
    secret_key: Optional[str] = Field(default=None, description="Secret key for HMAC algorithms")
    private_key: Optional[str] = Field(default=None, description="Private key for RSA/ECDSA")
    public_key: Optional[str] = Field(default=None, description="Public key for RSA/ECDSA verification")
    
    # Token lifetime settings
    access_token_expire: int = Field(default=3600, description="Access token expiration (seconds)")
    refresh_token_expire: int = Field(default=604800, description="Refresh token expiration (seconds)")
    
    # Security settings (Security expertise)
    require_exp: bool = Field(default=True, description="Require expiration claim")
    require_iat: bool = Field(default=True, description="Require issued at claim")
    require_nbf: bool = Field(default=False, description="Require not before claim")
    validate_audience: bool = Field(default=True, description="Validate audience claim")
    validate_issuer: bool = Field(default=True, description="Validate issuer claim")
    
    # Issuer and audience
    issuer: str = Field(default="ainflue-sdk", description="Token issuer")
    audience: List[str] = Field(default_factory=lambda: ["ainflue-api"], description="Token audience")
    
    # Clock skew tolerance
    leeway: int = Field(default=10, description="Clock skew tolerance (seconds)")


class JWTClaims(BaseModel):
    """JWT claims with validation"""
    # Standard claims (RFC 7519)
    iss: Optional[str] = Field(default=None, description="Issuer")
    sub: Optional[str] = Field(default=None, description="Subject") 
    aud: Optional[Union[str, List[str]]] = Field(default=None, description="Audience")
    exp: Optional[int] = Field(default=None, description="Expiration time")
    nbf: Optional[int] = Field(default=None, description="Not before")
    iat: Optional[int] = Field(default=None, description="Issued at")
    jti: Optional[str] = Field(default=None, description="JWT ID")
    
    # Custom claims
    token_type: Optional[str] = Field(default=None, description="Token type")
    scope: Optional[str] = Field(default=None, description="Token scope")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    permissions: Optional[List[str]] = Field(default=None, description="User permissions")
    
    # Additional custom claims
    custom_claims: Optional[Dict[str, Any]] = Field(default=None, description="Additional claims")


class JWTKeyManager:
    """JWT key management (Security expertise)"""
    
    def __init__(self, config -> None: JWTConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._validate_keys()
    
    def _validate_keys(self) -> None:
        """Validate JWT signing keys configuration"""
        algorithm = self.config.algorithm
        
        if algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
            if not self.config.secret_key:
                raise SecurityError(f"Secret key required for {algorithm.value}")
            if len(self.config.secret_key) < 32:
                self.logger.warning("Secret key should be at least 32 characters for security")
        
        elif algorithm in [JWTAlgorithm.RS256, JWTAlgorithm.RS384, JWTAlgorithm.RS512]:
            if not self.config.private_key:
                raise SecurityError(f"Private key required for {algorithm.value}")
            if not self.config.public_key:
                raise SecurityError(f"Public key required for {algorithm.value} verification")
    
    def get_signing_key(self) -> Union[str, bytes]:
        """Get appropriate signing key for token generation"""
        algorithm = self.config.algorithm
        
        if algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
            return self.config.secret_key.encode('utf-8')
        
        elif algorithm in [JWTAlgorithm.RS256, JWTAlgorithm.RS384, JWTAlgorithm.RS512]:
            return self.config.private_key.encode('utf-8')
        
        else:
            raise SecurityError(f"Unsupported algorithm: {algorithm.value}")
    
    def get_verification_key(self) -> Union[str, bytes]:
        """Get appropriate verification key for token validation"""
        algorithm = self.config.algorithm
        
        if algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
            return self.config.secret_key.encode('utf-8')
        
        elif algorithm in [JWTAlgorithm.RS256, JWTAlgorithm.RS384, JWTAlgorithm.RS512]:
            return self.config.public_key.encode('utf-8')
        
        else:
            raise SecurityError(f"Unsupported algorithm: {algorithm.value}")


class JWTTokenCache:
    """JWT token caching for performance (Lead Dev IA expertise)"""
    
    def __init__(self, max_size -> None: int = 1000, ttl -> None: int = 300) -> None:
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached token data"""
        if token_hash not in self.cache:
            return None
        
        cached_item = self.cache[token_hash]
        
        # Check TTL
        if time.time() > cached_item["expires_at"]:
            self._remove(token_hash)
            return None
        
        # Update access time for LRU
        self.access_times[token_hash] = time.time()
        
        return cached_item["data"]
    
    def set(self, token_hash -> None: str, data -> None: Dict[str, Any]) -> None:
        """Cache token data"""
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Cache the data
        self.cache[token_hash] = {
            "data": data,
            "cached_at": time.time(),
            "expires_at": time.time() + self.ttl
        }
        self.access_times[token_hash] = time.time()
    
    def _evict_lru(self) -> None:
        """Evict least recently used items"""
        if not self.access_times:
            return
        
        # Find least recently used item
        lru_hash = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(lru_hash)
    
    def _remove(self, token_hash -> None: str) -> None:
        """Remove item from cache"""
        self.cache.pop(token_hash, None)
        self.access_times.pop(token_hash, None)
    
    def invalidate(self, token_hash -> None: str) -> None:
        """Invalidate specific token in cache"""
        self._remove(token_hash)
    
    def clear(self) -> None:
        """Clear all cached tokens"""
        self.cache.clear()
        self.access_times.clear()


class JWTValidator:
    """JWT token validation (Security expertise)"""
    
    def __init__(self, config -> None: JWTConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_claims(self, claims: Dict[str, Any]) -> bool:
        """Validate JWT claims according to configuration"""
        current_time = int(time.time())
        
        # Validate required claims
        if self.config.require_exp and "exp" not in claims:
            raise TokenInvalidError("Missing required expiration claim")
        
        if self.config.require_iat and "iat" not in claims:
            raise TokenInvalidError("Missing required issued at claim")
        
        if self.config.require_nbf and "nbf" not in claims:
            raise TokenInvalidError("Missing required not before claim")
        
        # Validate expiration
        if "exp" in claims:
            exp_time = claims["exp"]
            if current_time > (exp_time + self.config.leeway):
                raise TokenExpiredError("Token has expired")
        
        # Validate not before
        if "nbf" in claims:
            nbf_time = claims["nbf"]
            if current_time < (nbf_time - self.config.leeway):
                raise TokenInvalidError("Token not yet valid (nbf)")
        
        # Validate issuer
        if self.config.validate_issuer and "iss" in claims:
            if claims["iss"] != self.config.issuer:
                raise TokenInvalidError(f"Invalid issuer: {claims['iss']}")
        
        # Validate audience
        if self.config.validate_audience and "aud" in claims:
            token_audience = claims["aud"]
            if isinstance(token_audience, str):
                token_audience = [token_audience]
            
            if not any(aud in self.config.audience for aud in token_audience):
                raise TokenInvalidError(f"Invalid audience: {token_audience}")
        
        return True
    
    def validate_token_structure(self, token: str) -> bool:
        """Validate JWT token structure"""
        parts = token.split('.')
        if len(parts) != 3:
            raise TokenInvalidError("Invalid JWT structure")
        
        # Validate each part is valid base64
        for i, part in enumerate(parts):
            try:
                # Add padding if needed
                padded = part + '=' * (4 - len(part) % 4)
                base64.urlsafe_b64decode(padded)
            except Exception:
                raise TokenInvalidError(f"Invalid base64 in JWT part {i}")
        
        return True


class JWTHandler:
    """Main JWT handler with multi-expert security implementation"""
    
    def __init__(self, config -> None: JWTConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Expert components
        self.key_manager = JWTKeyManager(config)
        self.validator = JWTValidator(config)
        self.cache = JWTTokenCache()
        
        # Metrics
        self.metrics = JWTMetrics()
        
        # Token blacklist (for revoked tokens)
        self.blacklisted_tokens = set()
    
    def generate_token(self, 
                      claims: Union[JWTClaims, Dict[str, Any]],
                      token_type: TokenType = TokenType.ACCESS,
                      custom_expiry: Optional[int] = None) -> str:
        """Generate JWT token with security best practices"""
        try:
            # Convert claims to dict if needed
            if isinstance(claims, JWTClaims):
                claims_dict = claims.dict(exclude_none=True)
                if claims.custom_claims:
                    claims_dict.update(claims.custom_claims)
            else:
                claims_dict = claims.copy()
            
            # Add standard claims
            current_time = int(time.time())
            
            if self.config.require_iat:
                claims_dict["iat"] = current_time
            
            # Set expiration based on token type
            if custom_expiry:
                expires_in = custom_expiry
            elif token_type == TokenType.ACCESS:
                expires_in = self.config.access_token_expire
            elif token_type == TokenType.REFRESH:
                expires_in = self.config.refresh_token_expire
            else:
                expires_in = self.config.access_token_expire
            
            if self.config.require_exp:
                claims_dict["exp"] = current_time + expires_in
            
            # Add not before if required
            if self.config.require_nbf:
                claims_dict["nbf"] = current_time
            
            # Add issuer and audience
            claims_dict["iss"] = self.config.issuer
            claims_dict["aud"] = self.config.audience
            
            # Add token type
            claims_dict["token_type"] = token_type.value
            
            # Generate unique token ID
            import uuid
            claims_dict["jti"] = str(uuid.uuid4())
            
            # Get signing key
            signing_key = self.key_manager.get_signing_key()
            
            # Generate token
            token = jwt.encode(
                payload=claims_dict,
                key=signing_key,
                algorithm=self.config.algorithm.value
            )
            
            # Update metrics
            self.metrics.tokens_generated += 1
            algorithm_name = self.config.algorithm.value
            self.metrics.algorithm_usage[algorithm_name] = \
                self.metrics.algorithm_usage.get(algorithm_name, 0) + 1
            
            self.logger.debug(f"Generated {token_type.value} token with {self.config.algorithm.value}")
            return token
            
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise JWTError(f"Token generation failed: {e}")
    
    def validate_token(self, 
                      token: str,
                      verify_signature: bool = True,
                      verify_expiration: bool = True,
                      verify_claims: bool = True) -> Dict[str, Any]:
        """Validate JWT token with comprehensive security checks"""
        start_time = time.time()
        
        try:
            self.metrics.tokens_validated += 1
            
            # Check if token is blacklisted
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash in self.blacklisted_tokens:
                raise TokenInvalidError("Token has been revoked")
            
            # Check cache first
            cached_result = self.cache.get(token_hash)
            if cached_result:
                validation_time = time.time() - start_time
                self.metrics.update_validation_time(validation_time)
                return cached_result
            
            # Validate token structure
            self.validator.validate_token_structure(token)
            
            # Get verification key
            verification_key = self.key_manager.get_verification_key()
            
            # Decode and validate token
            options = {
                "verify_signature": verify_signature,
                "verify_exp": verify_expiration,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": self.config.validate_audience,
                "verify_iss": self.config.validate_issuer,
            }
            
            try:
                payload = jwt.decode(
                    jwt=token,
                    key=verification_key,
                    algorithms=[self.config.algorithm.value],
                    audience=self.config.audience if self.config.validate_audience else None,
                    issuer=self.config.issuer if self.config.validate_issuer else None,
                    options=options,
                    leeway=self.config.leeway
                )
            except jwt.ExpiredSignatureError:
                self.metrics.expired_tokens += 1
                raise TokenExpiredError("Token has expired")
            except jwt.InvalidSignatureError:
                self.metrics.invalid_signatures += 1
                raise TokenInvalidError("Invalid token signature")
            except jwt.InvalidTokenError as e:
                raise TokenInvalidError(f"Invalid token: {e}")
            
            # Additional claim validation
            if verify_claims:
                self.validator.validate_claims(payload)
            
            # Cache successful validation
            self.cache.set(token_hash, payload)
            
            # Update metrics
            validation_time = time.time() - start_time
            self.metrics.update_validation_time(validation_time)
            
            self.logger.debug(f"Successfully validated token for subject: {payload.get('sub', 'unknown')}")
            return payload
            
        except (TokenExpiredError, TokenInvalidError):
            self.metrics.validation_failures += 1
            raise
        except Exception as e:
            self.metrics.validation_failures += 1
            self.logger.error(f"Token validation failed: {e}")
            raise JWTError(f"Token validation failed: {e}")
    
    def refresh_token(self, refresh_token: str, new_claims: Optional[Dict[str, Any]] = None) -> str:
        """Generate new access token from refresh token"""
        try:
            # Validate refresh token
            refresh_payload = self.validate_token(refresh_token)
            
            # Check if it's actually a refresh token
            if refresh_payload.get("token_type") != TokenType.REFRESH.value:
                raise TokenInvalidError("Token is not a refresh token")
            
            # Create new access token claims
            new_token_claims = {
                "sub": refresh_payload.get("sub"),
                "user_id": refresh_payload.get("user_id"),
                "session_id": refresh_payload.get("session_id"),
                "permissions": refresh_payload.get("permissions"),
                "scope": refresh_payload.get("scope")
            }
            
            # Add any new claims
            if new_claims:
                new_token_claims.update(new_claims)
            
            # Generate new access token
            new_token = self.generate_token(
                claims=new_token_claims,
                token_type=TokenType.ACCESS
            )
            
            self.logger.info(f"Refreshed token for subject: {refresh_payload.get('sub')}")
            return new_token
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            raise JWTError(f"Token refresh failed: {e}")
    
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token by adding to blacklist"""
        try:
            # Validate token first
            payload = self.validate_token(token, verify_expiration=False)
            
            # Add to blacklist
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.blacklisted_tokens.add(token_hash)
            
            # Remove from cache
            self.cache.invalidate(token_hash)
            
            self.logger.info(f"Revoked token for subject: {payload.get('sub')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Token revocation failed: {e}")
            return False
    
    def decode_token_unsafe(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)"""
        try:
            # Split token
            parts = token.split('.')
            if len(parts) != 3:
                raise TokenInvalidError("Invalid JWT structure")
            
            # Decode payload
            payload_part = parts[1]
            # Add padding if needed
            padded = payload_part + '=' * (4 - len(payload_part) % 4)
            payload_bytes = base64.urlsafe_b64decode(padded)
            payload = json.loads(payload_bytes.decode('utf-8'))
            
            return payload
            
        except Exception as e:
            raise JWTError(f"Token decoding failed: {e}")
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiration time"""
        try:
            payload = self.decode_token_unsafe(token)
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            return None
        except Exception:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            expiry = self.get_token_expiry(token)
            if expiry:
                return datetime.now() >= expiry
            return False
        except Exception:
            return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get JWT processing metrics"""
        return {
            "tokens_generated": self.metrics.tokens_generated,
            "tokens_validated": self.metrics.tokens_validated,
            "validation_failures": self.metrics.validation_failures,
            "validation_success_rate": self.metrics.validation_success_rate,
            "expired_tokens": self.metrics.expired_tokens,
            "invalid_signatures": self.metrics.invalid_signatures,
            "average_validation_time": self.metrics.average_validation_time,
            "algorithm_usage": self.metrics.algorithm_usage,
            "blacklisted_tokens": len(self.blacklisted_tokens)
        }
    
    def cleanup_expired_blacklist(self) -> None:
        """Clean up expired tokens from blacklist"""
        # This would require storing expiration times with blacklisted tokens
        # Simplified implementation for now
        pass


# Utility functions
def generate_secret_key(length: int = 64) -> str:
    """Generate cryptographically secure secret key"""
    import secrets
    return secrets.token_urlsafe(length)


def generate_rsa_keypair(key_size: int = 2048) -> tuple[str, str]:
    """Generate RSA key pair for JWT signing"""
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
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
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


# Example usage
def example_jwt_usage() -> None:
    """Example JWT usage"""
    # Generate RSA key pair
    private_key, public_key = generate_rsa_keypair()
    
    # Create JWT configuration
    config = JWTConfig(
        algorithm=JWTAlgorithm.RS256,
        private_key=private_key,
        public_key=public_key,
        issuer="ainflue-platform",
        audience=["ainflue-api", "ainflue-web"]
    )
    
    # Create JWT handler
    jwt_handler = JWTHandler(config)
    
    # Create token claims
    claims = JWTClaims(
        sub="user123",
        user_id="user123",
        scope="read write",
        permissions=["upload", "download", "share"]
    )
    
    # Generate access token
    access_token = jwt_handler.generate_token(claims, TokenType.ACCESS)
    print(f"Access token: {access_token}")
    
    # Generate refresh token
    refresh_token = jwt_handler.generate_token(claims, TokenType.REFRESH)
    print(f"Refresh token: {refresh_token}")
    
    # Validate token
    try:
        payload = jwt_handler.validate_token(access_token)
        print(f"Token valid, subject: {payload['sub']}")
    except Exception as e:
        print(f"Token validation failed: {e}")
    
    # Get metrics
    metrics = jwt_handler.get_metrics()
    print(f"JWT metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    example_jwt_usage()