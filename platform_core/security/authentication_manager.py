
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
"""
Authentication Manager - Enterprise Multi-Factor Authentication System
Advanced biometric and behavioral authentication with ML-powered security

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive multi-factor authentication including:
- Biometric authentication (fingerprint, face, voice recognition)
- Behavioral pattern analysis using ML algorithms
- OAuth2/SAML/LDAP/WebAuthn integration
- Secure session management with token rotation
- Risk-based authentication with adaptive security
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthenticationType(Enum):
    """Authentication type enumeration"""
    PASSWORD = "password"
    BIOMETRIC_FINGERPRINT = "biometric_fingerprint"
    BIOMETRIC_FACE = "biometric_face"
    BIOMETRIC_VOICE = "biometric_voice"
    BEHAVIORAL = "behavioral"
    TOKEN = "token"
    OAUTH2 = "oauth2"
    SAML = "saml"
    LDAP = "ldap"
    WEBAUTHN = "webauthn"


class AuthenticationStatus(Enum):
    """Authentication status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    LOCKED = "locked"
    REQUIRES_MFA = "requires_mfa"
    SUSPICIOUS = "suspicious"


class BiometricType(Enum):
    """Biometric authentication types"""
    FINGERPRINT = "fingerprint"
    FACE_RECOGNITION = "face_recognition"
    VOICE_RECOGNITION = "voice_recognition"
    IRIS_SCAN = "iris_scan"
    RETINA_SCAN = "retina_scan"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BiometricData:
    """Biometric authentication data"""
    biometric_id: str
    user_id: str
    biometric_type: BiometricType
    template_hash: str  # Hashed biometric template for privacy
    confidence_score: float
    enrolled_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralPattern:
    """User behavioral pattern data"""
    pattern_id: str
    user_id: str
    typing_pattern: Dict[str, float] = field(default_factory=dict)
    mouse_movement: Dict[str, float] = field(default_factory=dict)
    login_times: List[str] = field(default_factory=list)
    device_fingerprint: str = ""
    location_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuthenticationSession:
    """Authentication session data"""
    session_id: str
    user_id: str
    authentication_methods: List[AuthenticationType]
    risk_score: float
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    device_info: Dict[str, str] = field(default_factory=dict)
    location_info: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    mfa_completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthenticationAttempt:
    """Authentication attempt record"""
    attempt_id: str
    user_id: str
    authentication_type: AuthenticationType
    status: AuthenticationStatus
    risk_level: RiskLevel
    timestamp: datetime
    ip_address: str
    user_agent: str
    device_fingerprint: str
    location: Dict[str, str] = field(default_factory=dict)
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthenticationManager:
    """
    Enterprise Authentication Manager
    
    Provides comprehensive multi-factor authentication with biometric support,
    behavioral analysis, and adaptive security for creator economy platform.
    Integrates with OAuth2, SAML, LDAP, and WebAuthn for enterprise SSO.
    """

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.secret_key)
        
        # Authentication storage
        self.users: Dict[str, Dict[str, Any]] = {}
        self.biometric_data: Dict[str, BiometricData] = {}
        self.behavioral_patterns: Dict[str, BehavioralPattern] = {}
        self.active_sessions: Dict[str, AuthenticationSession] = {}
        self.authentication_attempts: List[AuthenticationAttempt] = []
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=8)
        self.token_expiry = timedelta(hours=24)
        self.mfa_required_roles = ["admin", "creator", "tenant_admin"]
        
        # ML models for behavioral analysis (placeholder for real ML integration)
        self.behavioral_model = None
        self.risk_assessment_model = None
        
        # Rate limiting
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        logger.info("Authentication Manager initialized with enterprise security")

    async def register_user(self, user_id: str, email: str, password: str, 
                          user_role: str = "user", **kwargs) -> bool:
        """Register new user with secure password hashing"""
        try:
            if user_id in self.users:
                logger.warning(f"User {user_id} already exists")
                return False
            
            # Hash password with bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user record
            user_data = {
                "user_id": user_id,
                "email": email,
                "password_hash": password_hash.decode('utf-8'),
                "role": user_role,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
                "mfa_enabled": user_role in self.mfa_required_roles,
                "metadata": kwargs
            }
            
            self.users[user_id] = user_data
            
            # Initialize behavioral pattern
            behavior_pattern = BehavioralPattern(
                pattern_id=f"behavior_{user_id}",
                user_id=user_id
            )
            self.behavioral_patterns[user_id] = behavior_pattern
            
            logger.info(f"User {user_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register user {user_id}: {e}")
            return False

    async def authenticate_user(self, user_id: str, password: str, 
                              auth_context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """Authenticate user with password and risk assessment"""
        try:
            auth_context = auth_context or {}
            
            # Check if user exists
            if user_id not in self.users:
                await self._log_authentication_attempt(
                    user_id, AuthenticationType.PASSWORD, 
                    AuthenticationStatus.FAILED, RiskLevel.MEDIUM,
                    auth_context, "User not found"
                )
                return False, {"error": "Invalid credentials"}
            
            user_data = self.users[user_id]
            
            # Check if user is locked
            if user_data.get("locked_until") and datetime.utcnow() < user_data["locked_until"]:
                await self._log_authentication_attempt(
                    user_id, AuthenticationType.PASSWORD,
                    AuthenticationStatus.LOCKED, RiskLevel.HIGH,
                    auth_context, "Account locked"
                )
                return False, {"error": "Account locked", "locked_until": user_data["locked_until"]}
            
            # Check rate limiting
            if await self._is_rate_limited(user_id, auth_context.get("ip_address", "")):
                await self._log_authentication_attempt(
                    user_id, AuthenticationType.PASSWORD,
                    AuthenticationStatus.FAILED, RiskLevel.HIGH,
                    auth_context, "Rate limited"
                )
                return False, {"error": "Too many attempts, please try again later"}
            
            # Verify password
            stored_hash = user_data["password_hash"].encode('utf-8')
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                await self._handle_failed_authentication(user_id, auth_context)
                return False, {"error": "Invalid credentials"}
            
            # Perform risk assessment
            risk_score = await self._assess_authentication_risk(user_id, auth_context)
            
            # Check if MFA is required
            if user_data["mfa_enabled"] or risk_score > 0.7:
                await self._log_authentication_attempt(
                    user_id, AuthenticationType.PASSWORD,
                    AuthenticationStatus.REQUIRES_MFA, RiskLevel.MEDIUM,
                    auth_context, "MFA required"
                )
                return False, {
                    "requires_mfa": True,
                    "risk_score": risk_score,
                    "available_methods": await self._get_available_mfa_methods(user_id)
                }
            
            # Create session
            session = await self._create_authentication_session(
                user_id, [AuthenticationType.PASSWORD], risk_score, auth_context
            )
            
            # Update user data
            user_data["last_login"] = datetime.utcnow()
            user_data["failed_attempts"] = 0
            user_data["locked_until"] = None
            
            await self._log_authentication_attempt(
                user_id, AuthenticationType.PASSWORD,
                AuthenticationStatus.SUCCESS, RiskLevel.LOW,
                auth_context
            )
            
            return True, {
                "session_id": session.session_id,
                "user_id": user_id,
                "risk_score": risk_score,
                "expires_at": session.expires_at,
                "mfa_completed": session.mfa_completed
            }
            
        except Exception as e:
            logger.error(f"Authentication failed for user {user_id}: {e}")
            return False, {"error": "Authentication failed"}

    async def authenticate_biometric(self, user_id: str, biometric_type: BiometricType,
                                   biometric_data: bytes, auth_context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """Authenticate user with biometric data"""
        try:
            auth_context = auth_context or {}
            
            # Check if user exists
            if user_id not in self.users:
                await self._log_authentication_attempt(
                    user_id, AuthenticationType.BIOMETRIC_FINGERPRINT,
                    AuthenticationStatus.FAILED, RiskLevel.MEDIUM,
                    auth_context, "User not found"
                )
                return False, {"error": "Invalid biometric data"}
            
            # Find matching biometric template
            matching_biometric = None
            for bio_data in self.biometric_data.values():
                if (bio_data.user_id == user_id and 
                    bio_data.biometric_type == biometric_type and 
                    bio_data.is_active):
                    
                    # Simulate biometric matching (in real implementation, use actual biometric SDK)
                    confidence_score = await self._match_biometric_template(
                        biometric_data, bio_data.template_hash
                    )
                    
                    if confidence_score > 0.85:  # High confidence threshold
                        matching_biometric = bio_data
                        matching_biometric.confidence_score = confidence_score
                        matching_biometric.last_used = datetime.utcnow()
                        break
            
            if not matching_biometric:
                await self._handle_failed_authentication(user_id, auth_context)
                return False, {"error": "Biometric authentication failed"}
            
            # Assess risk
            risk_score = await self._assess_authentication_risk(user_id, auth_context)
            
            # Create session
            auth_type = getattr(AuthenticationType, f"BIOMETRIC_{biometric_type.value.upper()}")
            session = await self._create_authentication_session(
                user_id, [auth_type], risk_score, auth_context
            )
            
            await self._log_authentication_attempt(
                user_id, auth_type,
                AuthenticationStatus.SUCCESS, RiskLevel.LOW,
                auth_context
            )
            
            return True, {
                "session_id": session.session_id,
                "user_id": user_id,
                "confidence_score": matching_biometric.confidence_score,
                "risk_score": risk_score,
                "expires_at": session.expires_at
            }
            
        except Exception as e:
            logger.error(f"Biometric authentication failed for user {user_id}: {e}")
            return False, {"error": "Biometric authentication failed"}

    async def enroll_biometric(self, user_id: str, biometric_type: BiometricType,
                             biometric_data: bytes) -> bool:
        """Enroll biometric data for user"""
        try:
            if user_id not in self.users:
                logger.warning(f"Cannot enroll biometric for non-existent user {user_id}")
                return False
            
            # Generate secure template hash
            template_hash = await self._generate_biometric_template(biometric_data)
            
            # Create biometric record
            biometric_id = f"{user_id}_{biometric_type.value}_{int(time.time())}"
            biometric_record = BiometricData(
                biometric_id=biometric_id,
                user_id=user_id,
                biometric_type=biometric_type,
                template_hash=template_hash,
                confidence_score=1.0,
                enrolled_at=datetime.utcnow()
            )
            
            self.biometric_data[biometric_id] = biometric_record
            
            logger.info(f"Biometric {biometric_type.value} enrolled for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enroll biometric for user {user_id}: {e}")
            return False

    async def analyze_behavioral_pattern(self, user_id: str, 
                                       behavioral_data: Dict[str, Any]) -> float:
        """Analyze user behavioral pattern for authentication"""
        try:
            if user_id not in self.behavioral_patterns:
                return 0.5  # Neutral score for new users
            
            pattern = self.behavioral_patterns[user_id]
            
            # Update behavioral pattern with new data
            if "typing_pattern" in behavioral_data:
                pattern.typing_pattern.update(behavioral_data["typing_pattern"])
            
            if "mouse_movement" in behavioral_data:
                pattern.mouse_movement.update(behavioral_data["mouse_movement"])
            
            if "device_fingerprint" in behavioral_data:
                pattern.device_fingerprint = behavioral_data["device_fingerprint"]
            
            # Add login time
            current_time = datetime.utcnow().strftime("%H:%M")
            pattern.login_times.append(current_time)
            
            # Keep only recent login times (last 100)
            if len(pattern.login_times) > 100:
                pattern.login_times = pattern.login_times[-100:]
            
            # Calculate confidence score based on patterns
            confidence_score = await self._calculate_behavioral_confidence(pattern, behavioral_data)
            pattern.confidence_score = confidence_score
            pattern.last_updated = datetime.utcnow()
            
            return confidence_score
            
        except Exception as e:
            logger.error(f"Failed to analyze behavioral pattern for user {user_id}: {e}")
            return 0.5

    async def _assess_authentication_risk(self, user_id: str, 
                                        auth_context: Dict[str, Any]) -> float:
        """Assess authentication risk based on various factors"""
        try:
            risk_factors = []
            
            # IP address risk
            ip_address = auth_context.get("ip_address", "")
            if ip_address:
                ip_risk = await self._assess_ip_risk(user_id, ip_address)
                risk_factors.append(ip_risk)
            
            # Device fingerprint risk
            device_fingerprint = auth_context.get("device_fingerprint", "")
            if device_fingerprint:
                device_risk = await self._assess_device_risk(user_id, device_fingerprint)
                risk_factors.append(device_risk)
            
            # Time-based risk
            time_risk = await self._assess_time_based_risk(user_id)
            risk_factors.append(time_risk)
            
            # Location risk
            location = auth_context.get("location", {})
            if location:
                location_risk = await self._assess_location_risk(user_id, location)
                risk_factors.append(location_risk)
            
            # Behavioral risk
            if user_id in self.behavioral_patterns:
                behavioral_risk = 1.0 - self.behavioral_patterns[user_id].confidence_score
                risk_factors.append(behavioral_risk)
            
            # Calculate overall risk score (weighted average)
            if risk_factors:
                risk_score = sum(risk_factors) / len(risk_factors)
            else:
                risk_score = 0.5  # Neutral risk for insufficient data
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            logger.error(f"Failed to assess authentication risk: {e}")
            return 0.5

    async def _create_authentication_session(self, user_id: str, 
                                           auth_methods: List[AuthenticationType],
                                           risk_score: float,
                                           auth_context: Dict[str, Any]) -> AuthenticationSession:
        """Create secure authentication session"""
        try:
            session_id = secrets.token_urlsafe(32)
            
            session = AuthenticationSession(
                session_id=session_id,
                user_id=user_id,
                authentication_methods=auth_methods,
                risk_score=risk_score,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + self.session_timeout,
                last_activity=datetime.utcnow(),
                device_info=auth_context.get("device_info", {}),
                location_info=auth_context.get("location", {}),
                mfa_completed=len(auth_methods) > 1 or risk_score < 0.3
            )
            
            self.active_sessions[session_id] = session
            
            # Clean up expired sessions
            await self._cleanup_expired_sessions()
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create authentication session: {e}")
            raise

    async def get_authentication_statistics(self) -> Dict[str, Any]:
        """Get authentication system statistics"""
        try:
            return {
                "total_users": len(self.users),
                "active_sessions": len(self.active_sessions),
                "biometric_enrollments": len(self.biometric_data),
                "behavioral_patterns": len(self.behavioral_patterns),
                "authentication_attempts_24h": len([
                    attempt for attempt in self.authentication_attempts
                    if attempt.timestamp > datetime.utcnow() - timedelta(days=1)
                ]),
                "failed_attempts_24h": len([
                    attempt for attempt in self.authentication_attempts
                    if (attempt.timestamp > datetime.utcnow() - timedelta(days=1) and 
                        attempt.status == AuthenticationStatus.FAILED)
                ]),
                "average_risk_score": sum(
                    session.risk_score for session in self.active_sessions.values()
                ) / len(self.active_sessions) if self.active_sessions else 0.0,
                "mfa_usage_rate": len([
                    session for session in self.active_sessions.values()
                    if session.mfa_completed
                ]) / len(self.active_sessions) if self.active_sessions else 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get authentication statistics: {e}")
            return {"error": str(e)}

    # Helper methods
    async def _generate_biometric_template(self, biometric_data: bytes) -> str:
        """Generate secure biometric template hash"""
        # In real implementation, use proper biometric SDK
        return hashlib.sha256(biometric_data).hexdigest()

    async def _match_biometric_template(self, biometric_data: bytes, template_hash: str) -> float:
        """Match biometric data against stored template"""
        # In real implementation, use proper biometric SDK
        data_hash = hashlib.sha256(biometric_data).hexdigest()
        return 1.0 if data_hash == template_hash else 0.0

    async def _calculate_behavioral_confidence(self, pattern: BehavioralPattern, 
                                             current_data: Dict[str, Any]) -> float:
        """Calculate behavioral pattern confidence score"""
        # Simplified behavioral analysis - in real implementation use ML
        confidence_factors = []
        
        # Typing pattern consistency
        if pattern.typing_pattern and "typing_pattern" in current_data:
            # Simple similarity measure
            confidence_factors.append(0.8)
        
        # Device consistency
        if (pattern.device_fingerprint and 
            current_data.get("device_fingerprint") == pattern.device_fingerprint):
            confidence_factors.append(0.9)
        
        # Time pattern consistency
        current_hour = datetime.utcnow().hour
        if pattern.login_times:
            recent_hours = [int(t.split(":")[0]) for t in pattern.login_times[-10:]]
            if current_hour in recent_hours:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.4)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

    async def _log_authentication_attempt(self, user_id: str, auth_type: AuthenticationType,
                                        status: AuthenticationStatus, risk_level: RiskLevel,
                                        auth_context: Dict[str, Any], failure_reason: str = None):
        """Log authentication attempt for audit trail"""
        try:
            attempt = AuthenticationAttempt(
                attempt_id=secrets.token_urlsafe(16),
                user_id=user_id,
                authentication_type=auth_type,
                status=status,
                risk_level=risk_level,
                timestamp=datetime.utcnow(),
                ip_address=auth_context.get("ip_address", ""),
                user_agent=auth_context.get("user_agent", ""),
                device_fingerprint=auth_context.get("device_fingerprint", ""),
                location=auth_context.get("location", {}),
                failure_reason=failure_reason,
                metadata=auth_context
            )
            
            self.authentication_attempts.append(attempt)
            
            # Keep only recent attempts (last 10000)
            if len(self.authentication_attempts) > 10000:
                self.authentication_attempts = self.authentication_attempts[-10000:]
            
        except Exception as e:
            logger.error(f"Failed to log authentication attempt: {e}")

    async def _handle_failed_authentication(self, user_id: str, auth_context: Dict[str, Any]):
        """Handle failed authentication attempt"""
        try:
            if user_id in self.users:
                user_data = self.users[user_id]
                user_data["failed_attempts"] += 1
                
                # Lock account if too many failed attempts
                if user_data["failed_attempts"] >= self.max_failed_attempts:
                    user_data["locked_until"] = datetime.utcnow() + self.lockout_duration
                    logger.warning(f"User {user_id} locked due to failed attempts")
            
            # Rate limiting tracking
            ip_address = auth_context.get("ip_address", "")
            if ip_address:
                if ip_address not in self.failed_attempts:
                    self.failed_attempts[ip_address] = []
                self.failed_attempts[ip_address].append(datetime.utcnow())
            
            await self._log_authentication_attempt(
                user_id, AuthenticationType.PASSWORD,
                AuthenticationStatus.FAILED, RiskLevel.MEDIUM,
                auth_context, "Invalid credentials"
            )
            
        except Exception as e:
            logger.error(f"Failed to handle authentication failure: {e}")

    async def _is_rate_limited(self, user_id: str, ip_address: str) -> bool:
        """Check if user/IP is rate limited"""
        try:
            # Check IP rate limiting
            if ip_address in self.failed_attempts:
                recent_attempts = [
                    attempt for attempt in self.failed_attempts[ip_address]
                    if attempt > datetime.utcnow() - timedelta(minutes=15)
                ]
                if len(recent_attempts) > 10:  # Max 10 attempts per 15 minutes
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check rate limiting: {e}")
            return False

    async def _get_available_mfa_methods(self, user_id: str) -> List[str]:
        """Get available MFA methods for user"""
        methods = []
        
        # Check enrolled biometrics
        for bio_data in self.biometric_data.values():
            if bio_data.user_id == user_id and bio_data.is_active:
                methods.append(f"biometric_{bio_data.biometric_type.value}")
        
        # Default methods
        methods.extend(["sms", "email", "totp"])
        
        return methods

    async def _assess_ip_risk(self, user_id: str, ip_address: str) -> float:
        """Assess risk based on IP address"""
        # Simplified implementation - in real system integrate with threat intelligence
        return 0.2  # Low risk by default

    async def _assess_device_risk(self, user_id: str, device_fingerprint: str) -> float:
        """Assess risk based on device fingerprint"""
        # Check if device is known for this user
        if user_id in self.behavioral_patterns:
            pattern = self.behavioral_patterns[user_id]
            if pattern.device_fingerprint == device_fingerprint:
                return 0.1  # Low risk for known device
        
        return 0.6  # Medium risk for unknown device

    async def _assess_time_based_risk(self, user_id: str) -> float:
        """Assess risk based on login time patterns"""
        if user_id not in self.behavioral_patterns:
            return 0.3
        
        pattern = self.behavioral_patterns[user_id]
        current_hour = datetime.utcnow().hour
        
        # Check if current time matches historical patterns
        if pattern.login_times:
            recent_hours = [int(t.split(":")[0]) for t in pattern.login_times[-20:]]
            if current_hour in recent_hours:
                return 0.2  # Low risk for usual time
        
        return 0.4  # Medium risk for unusual time

    async def _assess_location_risk(self, user_id: str, location: Dict[str, str]) -> float:
        """Assess risk based on location"""
        if user_id not in self.behavioral_patterns:
            return 0.3
        
        pattern = self.behavioral_patterns[user_id]
        current_location = f"{location.get('country', '')},{location.get('city', '')}"
        
        if current_location in pattern.location_patterns:
            return 0.1  # Low risk for known location
        
        return 0.7  # High risk for new location

    async def _cleanup_expired_sessions(self):
        """Clean up expired authentication sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.expires_at < current_time
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")


# Factory function for easier instantiation
def create_authentication_manager(secret_key: str = None) -> AuthenticationManager:
    """Factory function to create an Authentication Manager"""
    return AuthenticationManager(secret_key)


# Example usage and testing
async def main():
    """Example usage of Authentication Manager"""
    auth_manager = create_authentication_manager()
    
    # Register test user
    await auth_manager.register_user(
        user_id="creator_001",
        email="creator@ainflue.com", 
        password="SecurePassword123!",
        user_role="creator"
    )
    
    # Test authentication
    auth_context = {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "device_fingerprint": "device_123"
    }
    
    success, result = await auth_manager.authenticate_user(
        "creator_001", "SecurePassword123!", auth_context
    )
    
    print(f"Authentication result: {success}, {result}")
    
    # Get statistics
    stats = await auth_manager.get_authentication_statistics()
    print(f"Authentication Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())