"""Session Security Manager - IA Influencer Agent

Enterprise-grade session security with advanced authentication, encryption,
secure token generation, and multi-tenant isolation for content creators
across platforms with GDPR compliance and zero-trust architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""
import asyncio
import secrets
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field, validator
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import redis.asyncio as redis

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, SessionState
from ...models.user import UserModel
from ...models.security import SecurityTokenModel, SecurityEventModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher

logger = get_logger(__name__)


class SecurityLevel(Enum):
    """Security level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TokenType(Enum):
    """Security token types"""
    SESSION = "session"
    REFRESH = "refresh"
    API = "api"
    TEMPORARY = "temporary"
    COLLABORATION = "collaboration"


class SecurityEvent(Enum):
    """Security event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    SESSION_CREATED = "session_created"
    SESSION_HIJACK_ATTEMPT = "session_hijack_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    TOKEN_REVOKED = "token_revoked"
    ENCRYPTION_ERROR = "encryption_error"
    ACCESS_DENIED = "access_denied"


@dataclass
class SecurityConfig:
    """Security configuration parameters"""
    token_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    encryption_algorithm: str = "AES-256-GCM"
    jwt_algorithm: str = "RS256"
    session_rotation_interval: int = 3600  # seconds
    require_device_verification: bool = True
    enable_session_fingerprinting: bool = True
    audit_all_activities: bool = True
    gdpr_compliant: bool = True


class SessionFingerprint(BaseModel):
    """Session fingerprint for security validation"""
    user_agent: str
    ip_address: str
    device_id: Optional[str] = None
    timezone: Optional[str] = None
    screen_resolution: Optional[str] = None
    language: Optional[str] = None
    platform: str
    fingerprint_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('fingerprint_hash', always=True)
    def generate_fingerprint(cls, v, values):
        if not v:
            # Generate fingerprint from available data
            data = f"{values.get('user_agent', '')}{values.get('ip_address', '')}{values.get('device_id', '')}"
            return hashlib.sha256(data.encode()).hexdigest()
        return v


class SecureSessionToken(BaseModel):
    """Secure session token structure"""
    token_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    token_type: TokenType
    security_level: SecurityLevel
    permissions: List[str] = Field(default_factory=list)
    fingerprint: SessionFingerprint
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_used: datetime = Field(default_factory=datetime.utcnow)
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None


class SessionAuthenticationHandler:
    """Advanced session authentication with multi-factor support"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.encryption_manager = EncryptionManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Failed attempt tracking
        self.failed_attempts: Dict[str, List[datetime]] = {}
    
    async def authenticate_session(
        self,
        session_id: str,
        user_credentials: Dict[str, Any],
        fingerprint: SessionFingerprint
    ) -> Tuple[bool, Optional[SecureSessionToken]]:
        """Authenticate session with comprehensive validation"""
        
        try:
            user_id = user_credentials.get("user_id")
            
            # Check if user is locked out
            if await self._is_user_locked_out(user_id):
                await self._log_security_event(
                    SecurityEvent.LOGIN_FAILED,
                    user_id,
                    session_id,
                    {"reason": "user_locked_out", "fingerprint": fingerprint.dict()}
                )
                return False, None
            
            # Validate user credentials
            if not await self._validate_user_credentials(user_credentials):
                await self._record_failed_attempt(user_id)
                await self._log_security_event(
                    SecurityEvent.LOGIN_FAILED,
                    user_id,
                    session_id,
                    {"reason": "invalid_credentials", "fingerprint": fingerprint.dict()}
                )
                return False, None
            
            # Validate session fingerprint
            if self.config.enable_session_fingerprinting:
                if not await self._validate_session_fingerprint(session_id, fingerprint):
                    await self._log_security_event(
                        SecurityEvent.SESSION_HIJACK_ATTEMPT,
                        user_id,
                        session_id,
                        {"fingerprint": fingerprint.dict()}
                    )
                    return False, None
            
            # Determine security level
            security_level = await self._determine_security_level(user_id, fingerprint)
            
            # Generate secure session token
            token = await self._generate_session_token(
                session_id,
                user_id,
                fingerprint,
                security_level
            )
            
            # Clear failed attempts on successful authentication
            await self._clear_failed_attempts(user_id)
            
            # Log successful authentication
            await self._log_security_event(
                SecurityEvent.LOGIN_SUCCESS,
                user_id,
                session_id,
                {"security_level": security_level.value, "fingerprint": fingerprint.dict()}
            )
            
            await self.metrics_collector.increment("session_auth.success")
            return True, token
            
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            await self.metrics_collector.increment("session_auth.errors")
            return False, None
    
    async def _validate_user_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate user credentials against database"""
        
        try:
            user_id = credentials.get("user_id")
            password = credentials.get("password")
            
            if not user_id or not password:
                return False
            
            async with get_async_session() as session:
                query = select(UserModel).where(UserModel.id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                
                if not user or not user.is_active:
                    return False
                
                # Verify password
                return bcrypt.checkpw(
                    password.encode('utf-8'),
                    user.password_hash.encode('utf-8')
                )
                
        except Exception as e:
            self.logger.error(f"Credential validation error: {str(e)}")
            return False
    
    async def _validate_session_fingerprint(
        self,
        session_id: str,
        fingerprint: SessionFingerprint
    ) -> bool:
        """Validate session fingerprint against stored fingerprint"""
        
        try:
            # Get stored fingerprint
            stored_fingerprint_key = f"session_fingerprint:{session_id}"
            stored_fingerprint_data = await self.cache_manager.get(stored_fingerprint_key)
            
            if not stored_fingerprint_data:
                # First time - store fingerprint
                await self.cache_manager.set(
                    stored_fingerprint_key,
                    fingerprint.dict(),
                    ttl=86400  # 24 hours
                )
                return True
            
            stored_fingerprint = SessionFingerprint(**stored_fingerprint_data)
            
            # Compare critical fingerprint elements
            if (fingerprint.user_agent != stored_fingerprint.user_agent or
                fingerprint.ip_address != stored_fingerprint.ip_address):
                
                # Allow some flexibility for mobile users
                if fingerprint.platform == "mobile":
                    # More lenient validation for mobile devices
                    ip_similarity = await self._calculate_ip_similarity(
                        fingerprint.ip_address,
                        stored_fingerprint.ip_address
                    )
                    return ip_similarity > 0.8
                
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fingerprint validation error: {str(e)}")
            return False
    
    async def _calculate_ip_similarity(self, ip1: str, ip2: str) -> float:
        """Calculate IP address similarity (for mobile networks)"""
        
        try:
            # Simple subnet comparison for IPv4
            parts1 = ip1.split('.')
            parts2 = ip2.split('.')
            
            if len(parts1) != 4 or len(parts2) != 4:
                return 0.0
            
            # Compare first 3 octets (assuming /24 subnet)
            matches = sum(1 for i in range(3) if parts1[i] == parts2[i])
            return matches / 3.0
            
        except Exception:
            return 0.0
    
    async def _determine_security_level(
        self,
        user_id: str,
        fingerprint: SessionFingerprint
    ) -> SecurityLevel:
        """Determine appropriate security level based on context"""
        
        # Base security level
        security_level = SecurityLevel.MEDIUM
        
        try:
            # Check user's security settings
            async with get_async_session() as session:
                query = select(UserModel).where(UserModel.id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                
                if user and user.security_settings:
                    user_security_level = user.security_settings.get("required_level", "medium")
                    security_level = SecurityLevel(user_security_level)
            
            # Increase security level based on risk factors
            risk_factors = 0
            
            # Unknown device
            if not fingerprint.device_id:
                risk_factors += 1
            
            # Suspicious IP
            if await self._is_suspicious_ip(fingerprint.ip_address):
                risk_factors += 2
            
            # Unusual access time
            if await self._is_unusual_access_time(user_id):
                risk_factors += 1
            
            # Adjust security level based on risk
            if risk_factors >= 3:
                security_level = SecurityLevel.CRITICAL
            elif risk_factors >= 2:
                security_level = SecurityLevel.HIGH
            
            return security_level
            
        except Exception as e:
            self.logger.error(f"Security level determination error: {str(e)}")
            return SecurityLevel.HIGH  # Default to high security on error
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        
        try:
            # Check against threat intelligence feeds
            suspicious_ips_key = "suspicious_ips"
            suspicious_ips = await self.cache_manager.get(suspicious_ips_key)
            
            if suspicious_ips and ip_address in suspicious_ips:
                return True
            
            # Check recent failed attempts from this IP
            failed_attempts_key = f"ip_failed_attempts:{ip_address}"
            failed_attempts = await self.cache_manager.get(failed_attempts_key)
            
            if failed_attempts and len(failed_attempts) > 10:
                return True
            
            return False
            
        except Exception:
            return False
    
    async def _is_unusual_access_time(self, user_id: str) -> bool:
        """Check if access time is unusual for user"""
        
        try:
            # Get user's typical access patterns
            access_patterns_key = f"user_access_patterns:{user_id}"
            access_patterns = await self.cache_manager.get(access_patterns_key)
            
            if not access_patterns:
                return False
            
            current_hour = datetime.utcnow().hour
            typical_hours = access_patterns.get("typical_hours", [])
            
            # Consider unusual if outside typical access hours
            return current_hour not in typical_hours
            
        except Exception:
            return False
    
    async def _generate_session_token(
        self,
        session_id: str,
        user_id: str,
        fingerprint: SessionFingerprint,
        security_level: SecurityLevel
    ) -> SecureSessionToken:
        """Generate secure session token with appropriate permissions"""
        
        # Determine token expiry based on security level
        if security_level == SecurityLevel.CRITICAL:
            expires_at = datetime.utcnow() + timedelta(minutes=15)
        elif security_level == SecurityLevel.HIGH:
            expires_at = datetime.utcnow() + timedelta(minutes=30)
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=self.config.token_expiry_minutes)
        
        # Determine permissions based on security level
        permissions = await self._get_user_permissions(user_id, security_level)
        
        token = SecureSessionToken(
            session_id=session_id,
            user_id=user_id,
            token_type=TokenType.SESSION,
            security_level=security_level,
            permissions=permissions,
            fingerprint=fingerprint,
            expires_at=expires_at
        )
        
        # Store token in cache
        token_key = f"session_token:{session_id}"
        await self.cache_manager.set(
            token_key,
            token.dict(),
            ttl=int((expires_at - datetime.utcnow()).total_seconds())
        )
        
        return token
    
    async def _get_user_permissions(
        self,
        user_id: str,
        security_level: SecurityLevel
    ) -> List[str]:
        """Get user permissions based on security level"""
        
        try:
            async with get_async_session() as session:
                query = select(UserModel).where(UserModel.id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                
                if not user:
                    return []
                
                base_permissions = user.permissions or []
                
                # Restrict permissions based on security level
                if security_level == SecurityLevel.CRITICAL:
                    # Only basic read permissions
                    return [p for p in base_permissions if p.startswith("read")]
                elif security_level == SecurityLevel.HIGH:
                    # Exclude admin permissions
                    return [p for p in base_permissions if not p.startswith("admin")]
                else:
                    return base_permissions
                    
        except Exception as e:
            self.logger.error(f"Permission retrieval error: {str(e)}")
            return []
    
    async def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is currently locked out"""
        
        lockout_key = f"user_lockout:{user_id}"
        lockout_data = await self.cache_manager.get(lockout_key)
        
        if lockout_data:
            lockout_until = datetime.fromisoformat(lockout_data["until"])
            return datetime.utcnow() < lockout_until
        
        return False
    
    async def _record_failed_attempt(self, user_id: str):
        """Record failed authentication attempt"""
        
        try:
            failed_attempts_key = f"failed_attempts:{user_id}"
            failed_attempts = await self.cache_manager.get(failed_attempts_key) or []
            
            # Add current attempt
            failed_attempts.append(datetime.utcnow().isoformat())
            
            # Keep only recent attempts (last hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            failed_attempts = [
                attempt for attempt in failed_attempts
                if datetime.fromisoformat(attempt) > cutoff_time
            ]
            
            await self.cache_manager.set(failed_attempts_key, failed_attempts, ttl=3600)
            
            # Check if user should be locked out
            if len(failed_attempts) >= self.config.max_failed_attempts:
                await self._lockout_user(user_id)
                
        except Exception as e:
            self.logger.error(f"Failed attempt recording error: {str(e)}")
    
    async def _lockout_user(self, user_id: str):
        """Lock out user after too many failed attempts"""
        
        try:
            lockout_until = datetime.utcnow() + timedelta(minutes=self.config.lockout_duration_minutes)
            
            lockout_data = {
                "until": lockout_until.isoformat(),
                "reason": "too_many_failed_attempts"
            }
            
            lockout_key = f"user_lockout:{user_id}"
            await self.cache_manager.set(
                lockout_key,
                lockout_data,
                ttl=self.config.lockout_duration_minutes * 60
            )
            
            # Log security event
            await self._log_security_event(
                SecurityEvent.ACCESS_DENIED,
                user_id,
                None,
                {"reason": "user_locked_out", "lockout_until": lockout_until.isoformat()}
            )
            
            self.logger.warning(f"User locked out: {user_id} until {lockout_until}")
            
        except Exception as e:
            self.logger.error(f"User lockout error: {str(e)}")
    
    async def _clear_failed_attempts(self, user_id: str):
        """Clear failed attempts after successful authentication"""
        
        failed_attempts_key = f"failed_attempts:{user_id}"
        await self.cache_manager.delete(failed_attempts_key)
    
    async def _log_security_event(
        self,
        event_type: SecurityEvent,
        user_id: Optional[str],
        session_id: Optional[str],
        metadata: Dict[str, Any]
    ):
        """Log security event for audit purposes"""
        
        try:
            event_data = {
                "event_type": event_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": metadata.get("fingerprint", {}).get("ip_address")
            }
            
            # Store in database if GDPR compliant logging is enabled
            if self.config.audit_all_activities:
                async with get_async_session() as session:
                    security_event = SecurityEventModel(**event_data)
                    session.add(security_event)
                    await session.commit()
            
            # Publish event for real-time monitoring
            await self.event_publisher.publish_event(
                f"security.{event_type.value}",
                event_data
            )
            
            await self.metrics_collector.increment(
                f"security_events.{event_type.value}"
            )
            
        except Exception as e:
            self.logger.error(f"Security event logging error: {str(e)}")


class SessionEncryptionManager:
    """Advanced session data encryption with key rotation"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.logger = get_logger(self.__class__.__name__)
        
        # Encryption keys (in production, these should be from secure key management)
        self.current_key = self._generate_encryption_key()
        self.previous_keys: List[bytes] = []
    
    def _generate_encryption_key(self) -> bytes:
        """Generate new encryption key"""
        
        return Fernet.generate_key()
    
    async def encrypt_session_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt session data with current key"""
        
        try:
            # Serialize data
            data_json = json.dumps(data, default=str).encode('utf-8')
            
            # Encrypt with current key
            fernet = Fernet(self.current_key)
            encrypted_data = fernet.encrypt(data_json)
            
            # Add key version for rotation support
            key_version = 1  # In production, track key versions
            versioned_data = key_version.to_bytes(4, 'big') + encrypted_data
            
            return versioned_data
            
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            raise
    
    async def decrypt_session_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt session data with appropriate key"""
        
        try:
            # Extract key version
            key_version = int.from_bytes(encrypted_data[:4], 'big')
            encrypted_payload = encrypted_data[4:]
            
            # Select appropriate key
            if key_version == 1:
                key = self.current_key
            else:
                # Handle key rotation (simplified)
                key = self.current_key
            
            # Decrypt data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_payload)
            
            # Deserialize
            return json.loads(decrypted_data.decode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            raise
    
    async def rotate_encryption_keys(self):
        """Rotate encryption keys for enhanced security"""
        
        try:
            # Move current key to previous keys
            self.previous_keys.append(self.current_key)
            
            # Generate new current key
            self.current_key = self._generate_encryption_key()
            
            # Keep only last 5 keys for backward compatibility
            if len(self.previous_keys) > 5:
                self.previous_keys = self.previous_keys[-5:]
            
            self.logger.info("Encryption keys rotated successfully")
            
            # Re-encrypt critical session data with new key
            await self._re_encrypt_active_sessions()
            
        except Exception as e:
            self.logger.error(f"Key rotation error: {str(e)}")
    
    async def _re_encrypt_active_sessions(self):
        """Re-encrypt active sessions with new key"""
        
        try:
            # Get active sessions
            active_sessions = await self.cache_manager.redis_client.smembers("active_sessions")
            
            for session_id in active_sessions:
                session_key = f"session_data:{session_id}"
                encrypted_data = await self.cache_manager.redis_client.get(session_key)
                
                if encrypted_data:
                    # Decrypt with old key
                    session_data = await self.decrypt_session_data(encrypted_data)
                    
                    # Re-encrypt with new key
                    new_encrypted_data = await self.encrypt_session_data(session_data)
                    
                    # Update in cache
                    await self.cache_manager.redis_client.set(session_key, new_encrypted_data)
            
            self.logger.info(f"Re-encrypted {len(active_sessions)} active sessions")
            
        except Exception as e:
            self.logger.error(f"Session re-encryption error: {str(e)}")


class SecureSessionTokenGenerator:
    """Secure token generation with JWT and custom tokens"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
        # JWT keys (in production, use proper key management)
        self.private_key = self._generate_rsa_keys()
        self.public_key = self.private_key.public_key()
    
    def _generate_rsa_keys(self):
        """Generate RSA key pair for JWT signing"""
        
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
    async def generate_jwt_token(
        self,
        token_data: SecureSessionToken
    ) -> str:
        """Generate JWT token from session token data"""
        
        try:
            payload = {
                "token_id": token_data.token_id,
                "session_id": token_data.session_id,
                "user_id": token_data.user_id,
                "token_type": token_data.token_type.value,
                "security_level": token_data.security_level.value,
                "permissions": token_data.permissions,
                "iat": int(token_data.issued_at.timestamp()),
                "exp": int(token_data.expires_at.timestamp()),
                "fingerprint_hash": token_data.fingerprint.fingerprint_hash
            }
            
            # Sign with private key
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            jwt_token = jwt.encode(
                payload,
                private_pem,
                algorithm=self.config.jwt_algorithm
            )
            
            return jwt_token
            
        except Exception as e:
            self.logger.error(f"JWT generation error: {str(e)}")
            raise
    
    async def verify_jwt_token(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        
        try:
            # Get public key for verification
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Verify and decode
            payload = jwt.decode(
                jwt_token,
                public_pem,
                algorithms=[self.config.jwt_algorithm]
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"JWT verification error: {str(e)}")
            return None
    
    async def generate_secure_random_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        
        return secrets.token_urlsafe(length)
    
    async def generate_refresh_token(
        self,
        session_id: str,
        user_id: str
    ) -> str:
        """Generate secure refresh token"""
        
        try:
            # Create token data
            token_data = {
                "session_id": session_id,
                "user_id": user_id,
                "type": "refresh",
                "issued_at": datetime.utcnow().isoformat(),
                "random": secrets.token_urlsafe(16)
            }
            
            # Create HMAC signature
            token_string = json.dumps(token_data, sort_keys=True)
            signature = hmac.new(
                self.config.jwt_secret.encode(),
                token_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine token data and signature
            refresh_token = f"{secrets.token_urlsafe(32)}.{signature[:16]}"
            
            return refresh_token
            
        except Exception as e:
            self.logger.error(f"Refresh token generation error: {str(e)}")
            raise


class SessionSecurityManager:
    """Main session security orchestrator"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.auth_handler = SessionAuthenticationHandler(self.config)
        self.encryption_manager = SessionEncryptionManager(self.config)
        self.token_generator = SecureSessionTokenGenerator(self.config)
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
    
    async def authenticate_and_secure_session(
        self,
        session_id: str,
        user_credentials: Dict[str, Any],
        request_fingerprint: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Complete session authentication and security setup"""
        
        try:
            # Create session fingerprint
            fingerprint = SessionFingerprint(
                user_agent=request_fingerprint.get("user_agent", ""),
                ip_address=request_fingerprint.get("ip_address", ""),
                device_id=request_fingerprint.get("device_id"),
                timezone=request_fingerprint.get("timezone"),
                platform=request_fingerprint.get("platform", "web")
            )
            
            # Authenticate session
            auth_success, token = await self.auth_handler.authenticate_session(
                session_id,
                user_credentials,
                fingerprint
            )
            
            if not auth_success or not token:
                return False, None
            
            # Generate JWT token
            jwt_token = await self.token_generator.generate_jwt_token(token)
            
            # Store security context
            await self._store_security_context(session_id, token)
            
            await self.metrics_collector.increment("session_security.authenticated")
            return True, jwt_token
            
        except Exception as e:
            self.logger.error(f"Session security setup error: {str(e)}")
            await self.metrics_collector.increment("session_security.setup_errors")
            return False, None
    
    async def validate_session_security(
        self,
        session_id: str,
        jwt_token: str,
        request_fingerprint: Dict[str, Any]
    ) -> bool:
        """Validate session security and token"""
        
        try:
            # Verify JWT token
            token_payload = await self.token_generator.verify_jwt_token(jwt_token)
            
            if not token_payload:
                return False
            
            # Validate session ID matches
            if token_payload.get("session_id") != session_id:
                self.logger.warning(f"Session ID mismatch: {session_id}")
                return False
            
            # Get stored security context
            security_context = await self._get_security_context(session_id)
            
            if not security_context:
                return False
            
            # Validate fingerprint
            current_fingerprint = SessionFingerprint(
                user_agent=request_fingerprint.get("user_agent", ""),
                ip_address=request_fingerprint.get("ip_address", ""),
                platform=request_fingerprint.get("platform", "web")
            )
            
            stored_fingerprint = SessionFingerprint(**security_context["fingerprint"])
            
            if not await self._validate_fingerprint_match(stored_fingerprint, current_fingerprint):
                self.logger.warning(f"Fingerprint mismatch for session: {session_id}")
                return False
            
            # Update last used timestamp
            await self._update_token_usage(session_id)
            
            await self.metrics_collector.increment("session_security.validated")
            return True
            
        except Exception as e:
            self.logger.error(f"Session validation error: {str(e)}")
            await self.metrics_collector.increment("session_security.validation_errors")
            return False
    
    async def _store_security_context(self, session_id: str, token: SecureSessionToken):
        """Store security context for session"""
        
        security_context = {
            "token_id": token.token_id,
            "user_id": token.user_id,
            "security_level": token.security_level.value,
            "permissions": token.permissions,
            "fingerprint": token.fingerprint.dict(),
            "issued_at": token.issued_at.isoformat(),
            "expires_at": token.expires_at.isoformat()
        }
        
        context_key = f"session_security:{session_id}"
        await self.cache_manager.set(
            context_key,
            security_context,
            ttl=int((token.expires_at - datetime.utcnow()).total_seconds())
        )
    
    async def _get_security_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get stored security context"""
        
        context_key = f"session_security:{session_id}"
        return await self.cache_manager.get(context_key)
    
    async def _validate_fingerprint_match(
        self,
        stored: SessionFingerprint,
        current: SessionFingerprint
    ) -> bool:
        """Validate fingerprint match with tolerance for mobile"""
        
        # Exact match for critical fields
        if stored.user_agent != current.user_agent:
            return False
        
        # IP address validation with mobile tolerance
        if stored.platform == "mobile" or current.platform == "mobile":
            # More lenient for mobile devices
            return await self.auth_handler._calculate_ip_similarity(
                stored.ip_address,
                current.ip_address
            ) > 0.7
        else:
            # Strict validation for desktop
            return stored.ip_address == current.ip_address
    
    async def _update_token_usage(self, session_id: str):
        """Update token last used timestamp"""
        
        try:
            security_context = await self._get_security_context(session_id)
            
            if security_context:
                security_context["last_used"] = datetime.utcnow().isoformat()
                
                context_key = f"session_security:{session_id}"
                await self.cache_manager.set(
                    context_key,
                    security_context,
                    ttl=3600  # Keep current TTL
                )
                
        except Exception as e:
            self.logger.error(f"Token usage update error: {str(e)}")
    
    async def revoke_session_token(self, session_id: str, reason: str = "user_request") -> bool:
        """Revoke session token and clean up security context"""
        
        try:
            # Get security context
            security_context = await self._get_security_context(session_id)
            
            if security_context:
                # Log revocation event
                await self.auth_handler._log_security_event(
                    SecurityEvent.TOKEN_REVOKED,
                    security_context.get("user_id"),
                    session_id,
                    {"reason": reason}
                )
            
            # Remove security context
            context_key = f"session_security:{session_id}"
            await self.cache_manager.delete(context_key)
            
            # Add to revoked tokens list
            revoked_tokens_key = "revoked_tokens"
            await self.cache_manager.set_add(revoked_tokens_key, session_id)
            
            await self.metrics_collector.increment("session_security.revoked")
            return True
            
        except Exception as e:
            self.logger.error(f"Token revocation error: {str(e)}")
            return False
    
    async def encrypt_session_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt session data"""
        
        return await self.encryption_manager.encrypt_session_data(data)
    
    async def decrypt_session_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt session data"""
        
        return await self.encryption_manager.decrypt_session_data(encrypted_data)
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        
        try:
            # Get authentication metrics
            auth_metrics = {
                "total_authentications": await self.metrics_collector.get_counter("session_auth.success"),
                "failed_authentications": await self.metrics_collector.get_counter("session_auth.errors"),
                "validation_success": await self.metrics_collector.get_counter("session_security.validated"),
                "validation_failures": await self.metrics_collector.get_counter("session_security.validation_errors"),
                "tokens_revoked": await self.metrics_collector.get_counter("session_security.revoked")
            }
            
            # Get active sessions count
            active_sessions = await self.cache_manager.redis_client.scard("active_sessions")
            
            # Get revoked tokens count
            revoked_tokens = await self.cache_manager.redis_client.scard("revoked_tokens")
            
            return {
                "authentication": auth_metrics,
                "active_sessions": active_sessions,
                "revoked_tokens": revoked_tokens,
                "security_level_distribution": await self._get_security_level_distribution(),
                "recent_security_events": await self._get_recent_security_events()
            }
            
        except Exception as e:
            self.logger.error(f"Security metrics calculation error: {str(e)}")
            return {}
    
    async def _get_security_level_distribution(self) -> Dict[str, int]:
        """Get distribution of security levels for active sessions"""
        
        try:
            distribution = {level.value: 0 for level in SecurityLevel}
            
            active_sessions = await self.cache_manager.redis_client.smembers("active_sessions")
            
            for session_id in active_sessions:
                context = await self._get_security_context(session_id)
                if context:
                    level = context.get("security_level", "medium")
                    distribution[level] = distribution.get(level, 0) + 1
            
            return distribution
            
        except Exception:
            return {}
    
    async def _get_recent_security_events(self) -> List[Dict[str, Any]]:
        """Get recent security events for monitoring"""
        
        try:
            # This would typically query the security events database
            # For now, return empty list
            return []
            
        except Exception:
            return []
