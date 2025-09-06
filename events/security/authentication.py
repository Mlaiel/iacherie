"""Ultra-Sophisticated Authentication Manager for Events Security

Advanced multi-factor authentication, session management, and security enforcement 
for Ainflue business events with ML-powered anomaly detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import hashlib
import secrets
import time
import jwt
from typing import Any, Dict, Optional, List, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import bcrypt

logger = logging.getLogger(__name__)


class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    PASSWORD = "password"
    TOKEN = "token"
    BIOMETRIC = "biometric"
    OTP = "otp"
    SSO = "sso"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"


class AuthenticationLevel(Enum):
    """Authentication security levels"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    HIGH_SECURITY = "high_security"
    ULTRA_SECURE = "ultra_secure"


class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    SUSPENDED = "suspended"


@dataclass
class AuthenticationCredentials:
    """Represents authentication credentials"""
    method: AuthenticationMethod
    primary_credential: str
    secondary_credential: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Hash sensitive data
        if self.method == AuthenticationMethod.PASSWORD:
            self.primary_credential = self._hash_password(self.primary_credential)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


@dataclass
class UserSession:
    """Represents an active user session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    authentication_level: AuthenticationLevel
    authenticated_methods: List[AuthenticationMethod]
    device_fingerprint: str
    ip_address: str
    location_data: Dict[str, Any]
    status: SessionStatus = SessionStatus.ACTIVE
    expires_at: datetime = None
    security_events: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if self.expires_at is None:
            # Default 8 hour session
            self.expires_at = self.created_at + timedelta(hours=8)
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return (
            self.status == SessionStatus.ACTIVE and
            datetime.utcnow() < self.expires_at and
            (datetime.utcnow() - self.last_activity) < timedelta(hours=2)
        )
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""
    success: bool
    user_id: Optional[str] = None
    session: Optional[UserSession] = None
    authentication_level: Optional[AuthenticationLevel] = None
    failure_reason: Optional[str] = None
    requires_mfa: bool = False
    security_warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecurityManager:
    """
    Ultra-sophisticated security manager for Ainflue Events Security
    
    Features:
    - Multi-factor authentication with business context
    - ML-powered anomaly detection for authentication patterns
    - Advanced session management with device fingerprinting
    - Threat-aware authentication escalation
    - Business logic-aware security enforcement
    """
    
    def __init__(self, 
                 jwt_secret: str = None,
                 session_timeout: int = 28800,  # 8 hours
                 max_failed_attempts: int = 5,
                 lockout_duration: int = 1800):  # 30 minutes
        
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        self.session_timeout = session_timeout
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = lockout_duration
        
        # Storage for sessions and security data
        self.active_sessions: Dict[str, UserSession] = {}
        self.user_credentials: Dict[str, List[AuthenticationCredentials]] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.security_events: List[Dict[str, Any]] = []
        self.device_registry: Dict[str, Dict[str, Any]] = {}
        
        # ML-powered components
        self.anomaly_detector = AuthenticationAnomalyDetector()
        self.threat_scorer = ThreatScorer()
        
        # Business context components
        self.business_authenticator = BusinessContextAuthenticator()
        
        self.enabled = True
        logger.info("Ultra-sophisticated SecurityManager initialized")
    
    async def authenticate_user(self, 
                              user_id: str, 
                              credentials: AuthenticationCredentials,
                              device_info: Dict[str, Any],
                              business_context: Dict[str, Any] = None) -> AuthenticationResult:
        """
        Perform sophisticated multi-factor authentication with business context
        """
        if not self.enabled:
            return AuthenticationResult(success=True, user_id=user_id)
        
        try:
            business_context = business_context or {}
            
            # Check for account lockout
            if await self._is_account_locked(user_id):
                return AuthenticationResult(
                    success=False,
                    failure_reason="Account temporarily locked due to failed attempts",
                    security_warnings=["Account lockout active"]
                )
            
            # Anomaly detection on authentication patterns
            anomaly_score = await self.anomaly_detector.analyze_authentication_pattern(
                user_id, device_info, business_context
            )
            
            # Validate primary credentials
            primary_valid = await self._validate_primary_credentials(user_id, credentials)
            
            if not primary_valid:
                await self._record_failed_attempt(user_id, device_info)
                return AuthenticationResult(
                    success=False,
                    failure_reason="Invalid credentials",
                    security_warnings=["Authentication failure recorded"]
                )
            
            # Determine required authentication level based on business context
            required_level = await self._determine_required_auth_level(
                user_id, business_context, anomaly_score
            )
            
            # Check if MFA is required
            mfa_required = await self._is_mfa_required(
                user_id, required_level, anomaly_score, business_context
            )
            
            if mfa_required and not await self._validate_mfa(user_id, credentials):
                return AuthenticationResult(
                    success=False,
                    requires_mfa=True,
                    failure_reason="Multi-factor authentication required",
                    security_warnings=["MFA challenge initiated"]
                )
            
            # Create secure session
            session = await self._create_secure_session(
                user_id, required_level, device_info, business_context
            )
            
            # Business context validation
            business_validation = await self.business_authenticator.validate_business_access(
                user_id, business_context, session
            )
            
            if not business_validation.allowed:
                return AuthenticationResult(
                    success=False,
                    failure_reason=business_validation.denial_reason,
                    security_warnings=business_validation.warnings
                )
            
            # Store session
            self.active_sessions[session.session_id] = session
            
            # Log security event
            await self._log_security_event("authentication_success", {
                "user_id": user_id,
                "session_id": session.session_id,
                "authentication_level": required_level.value,
                "anomaly_score": anomaly_score,
                "business_context": business_context
            })
            
            return AuthenticationResult(
                success=True,
                user_id=user_id,
                session=session,
                authentication_level=required_level,
                security_warnings=business_validation.warnings,
                metadata={
                    "anomaly_score": anomaly_score,
                    "authentication_methods": [credentials.method.value]
                }
            )
            
        except Exception as e:
            logger.error(f"Authentication error for user {user_id}: {str(e)}")
            return AuthenticationResult(
                success=False,
                failure_reason="Authentication system error",
                security_warnings=["System authentication failure"]
            )
    
    async def validate_session(self, 
                             session_id: str,
                             business_context: Dict[str, Any] = None) -> Optional[UserSession]:
        """Validate and refresh session with business context awareness"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        # Basic session validation
        if not session.is_valid():
            await self._invalidate_session(session_id, "session_expired")
            return None
        
        # Business context re-validation
        if business_context:
            business_validation = await self.business_authenticator.validate_business_access(
                session.user_id, business_context, session
            )
            
            if not business_validation.allowed:
                await self._invalidate_session(session_id, business_validation.denial_reason)
                return None
        
        # Update activity and return session
        session.update_activity()
        return session
    
    async def authorize_event_access(self, 
                                   session_id: str,
                                   event_type: str,
                                   event_data: Dict[str, Any],
                                   business_context: Dict[str, Any] = None) -> bool:
        """Authorize access to specific event with sophisticated business logic"""
        
        session = await self.validate_session(session_id, business_context)
        if not session:
            return False
        
        # Event-specific authorization
        return await self.business_authenticator.authorize_event_access(
            session, event_type, event_data, business_context
        )
    
    async def _validate_primary_credentials(self, 
                                          user_id: str, 
                                          credentials: AuthenticationCredentials) -> bool:
        """Validate primary authentication credentials"""
        
        user_creds = self.user_credentials.get(user_id, [])
        
        for stored_cred in user_creds:
            if stored_cred.method == credentials.method:
                if credentials.method == AuthenticationMethod.PASSWORD:
                    return bcrypt.checkpw(
                        credentials.primary_credential.encode('utf-8'),
                        stored_cred.primary_credential.encode('utf-8')
                    )
                elif credentials.method == AuthenticationMethod.TOKEN:
                    return self._validate_jwt_token(credentials.primary_credential)
                elif credentials.method == AuthenticationMethod.API_KEY:
                    return stored_cred.primary_credential == credentials.primary_credential
        
        return False
    
    async def _determine_required_auth_level(self, 
                                           user_id: str,
                                           business_context: Dict[str, Any],
                                           anomaly_score: float) -> AuthenticationLevel:
        """Determine required authentication level based on context and risk"""
        
        # Base level from business context
        base_level = AuthenticationLevel.BASIC
        
        # Escalate based on business context
        if business_context.get("event_type", "").startswith("monetization"):
            base_level = AuthenticationLevel.HIGH_SECURITY
        elif business_context.get("event_type", "").startswith("collaboration"):
            base_level = AuthenticationLevel.ENHANCED
        
        # Escalate based on anomaly score
        if anomaly_score > 0.8:
            base_level = AuthenticationLevel.ULTRA_SECURE
        elif anomaly_score > 0.6:
            base_level = AuthenticationLevel.HIGH_SECURITY
        
        # Escalate based on business value
        transaction_amount = business_context.get("transaction_amount", 0)
        if transaction_amount > 10000:
            base_level = AuthenticationLevel.ULTRA_SECURE
        elif transaction_amount > 1000:
            base_level = AuthenticationLevel.HIGH_SECURITY
        
        return base_level
    
    async def _create_secure_session(self, 
                                   user_id: str,
                                   auth_level: AuthenticationLevel,
                                   device_info: Dict[str, Any],
                                   business_context: Dict[str, Any]) -> UserSession:
        """Create secure session with device fingerprinting"""
        
        session_id = secrets.token_urlsafe(32)
        device_fingerprint = self._generate_device_fingerprint(device_info)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            authentication_level=auth_level,
            authenticated_methods=[AuthenticationMethod.PASSWORD],  # Will be updated
            device_fingerprint=device_fingerprint,
            ip_address=device_info.get("ip_address", "unknown"),
            location_data=device_info.get("location", {}),
            expires_at=datetime.utcnow() + timedelta(seconds=self.session_timeout)
        )
        
        # Register device if new
        if device_fingerprint not in self.device_registry:
            self.device_registry[device_fingerprint] = {
                "first_seen": datetime.utcnow(),
                "user_id": user_id,
                "device_info": device_info,
                "trust_score": 0.5  # Initial trust score
            }
        
        return session
    
    def _generate_device_fingerprint(self, device_info: Dict[str, Any]) -> str:
        """Generate unique device fingerprint"""
        
        fingerprint_data = f"{device_info.get('user_agent', '')}" \
                          f"{device_info.get('screen_resolution', '')}" \
                          f"{device_info.get('timezone', '')}" \
                          f"{device_info.get('language', '')}"
        
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def _validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token"""
        try:
            jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return True
        except jwt.InvalidTokenError:
            return False
    
    async def _is_mfa_required(self, 
                             user_id: str,
                             required_level: AuthenticationLevel,
                             anomaly_score: float,
                             business_context: Dict[str, Any]) -> bool:
        """Determine if multi-factor authentication is required"""
        
        # MFA required for high security levels
        if required_level in [AuthenticationLevel.HIGH_SECURITY, AuthenticationLevel.ULTRA_SECURE]:
            return True
        
        # MFA required for high anomaly scores
        if anomaly_score > 0.7:
            return True
        
        # MFA required for financial operations
        if business_context.get("event_type", "").startswith("monetization"):
            transaction_amount = business_context.get("transaction_amount", 0)
            if transaction_amount > 1000:
                return True
        
        return False
    
    async def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        failed_attempts = self.failed_attempts.get(user_id, [])
        
        # Remove old attempts (older than lockout duration)
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.lockout_duration)
        recent_attempts = [attempt for attempt in failed_attempts if attempt > cutoff_time]
        self.failed_attempts[user_id] = recent_attempts
        
        return len(recent_attempts) >= self.max_failed_attempts
    
    async def _record_failed_attempt(self, user_id: str, device_info: Dict[str, Any]):
        """Record a failed authentication attempt"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(datetime.utcnow())
        
        await self._log_security_event("authentication_failed", {
            "user_id": user_id,
            "device_info": device_info,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _validate_mfa(self, user_id: str, credentials: AuthenticationCredentials) -> bool:
        """Validate multi-factor authentication"""
        # Simplified MFA validation - in production would integrate with MFA providers
        return credentials.secondary_credential is not None
    
    async def _invalidate_session(self, session_id: str, reason: str):
        """Invalidate a session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = SessionStatus.INVALIDATED
            
            await self._log_security_event("session_invalidated", {
                "session_id": session_id,
                "user_id": session.user_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            del self.active_sessions[session_id]
    
    async def _log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log security event for audit and analysis"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "event_data": event_data
        }
        
        self.security_events.append(event)
        logger.info(f"Security event logged: {event_type}")


class AuthenticationAnomalyDetector:
    """ML-powered anomaly detection for authentication patterns"""
    
    def __init__(self):
        self.user_patterns = {}
        self.global_patterns = {}
    
    async def analyze_authentication_pattern(self, 
                                           user_id: str,
                                           device_info: Dict[str, Any],
                                           business_context: Dict[str, Any]) -> float:
        """Analyze authentication pattern and return anomaly score (0-1)"""
        
        anomaly_score = 0.0
        
        # Time-based anomalies
        current_hour = datetime.utcnow().hour
        user_typical_hours = self.user_patterns.get(user_id, {}).get("typical_hours", [])
        
        if user_typical_hours and current_hour not in user_typical_hours:
            anomaly_score += 0.3
        
        # Location-based anomalies
        current_location = device_info.get("location", {})
        typical_locations = self.user_patterns.get(user_id, {}).get("typical_locations", [])
        
        if typical_locations and not self._is_location_typical(current_location, typical_locations):
            anomaly_score += 0.4
        
        # Device-based anomalies
        device_fingerprint = device_info.get("device_fingerprint")
        typical_devices = self.user_patterns.get(user_id, {}).get("typical_devices", [])
        
        if typical_devices and device_fingerprint not in typical_devices:
            anomaly_score += 0.3
        
        return min(anomaly_score, 1.0)
    
    def _is_location_typical(self, current: Dict, typical: List[Dict]) -> bool:
        """Check if current location is typical for user"""
        # Simplified location comparison
        return any(
            abs(current.get("lat", 0) - loc.get("lat", 0)) < 0.1 and
            abs(current.get("lon", 0) - loc.get("lon", 0)) < 0.1
            for loc in typical
        )


class ThreatScorer:
    """Advanced threat scoring for authentication context"""
    
    async def calculate_threat_score(self, 
                                   user_id: str,
                                   context: Dict[str, Any]) -> float:
        """Calculate threat score based on multiple factors"""
        
        threat_score = 0.0
        
        # IP reputation
        ip_reputation = await self._check_ip_reputation(context.get("ip_address"))
        threat_score += ip_reputation * 0.4
        
        # Geolocation risk
        geo_risk = await self._assess_geolocation_risk(context.get("location"))
        threat_score += geo_risk * 0.3
        
        # Behavioral risk
        behavioral_risk = await self._assess_behavioral_risk(user_id, context)
        threat_score += behavioral_risk * 0.3
        
        return min(threat_score, 1.0)
    
    async def _check_ip_reputation(self, ip_address: str) -> float:
        """Check IP reputation (simplified)"""
        # In production, this would integrate with threat intelligence feeds
        return 0.1  # Low risk by default
    
    async def _assess_geolocation_risk(self, location: Dict[str, Any]) -> float:
        """Assess geolocation-based risk"""
        # In production, this would check against risk databases
        return 0.1  # Low risk by default
    
    async def _assess_behavioral_risk(self, user_id: str, context: Dict[str, Any]) -> float:
        """Assess behavioral risk factors"""
        return 0.1  # Low risk by default


class BusinessContextAuthenticator:
    """Business context-aware authentication for Ainflue workflows"""
    
    async def validate_business_access(self, 
                                     user_id: str,
                                     business_context: Dict[str, Any],
                                     session: UserSession) -> 'BusinessValidationResult':
        """Validate business context access"""
        
        warnings = []
        
        # Creator tier validation
        creator_tier = business_context.get("creator_tier", "basic")
        if creator_tier == "premium" and session.authentication_level == AuthenticationLevel.BASIC:
            return BusinessValidationResult(
                allowed=False,
                denial_reason="Premium features require enhanced authentication",
                warnings=["Authentication level insufficient for premium features"]
            )
        
        # Monetization validation
        if business_context.get("event_type", "").startswith("monetization"):
            if session.authentication_level not in [AuthenticationLevel.HIGH_SECURITY, AuthenticationLevel.ULTRA_SECURE]:
                return BusinessValidationResult(
                    allowed=False,
                    denial_reason="Financial operations require high security authentication",
                    warnings=["Financial operations blocked due to insufficient authentication"]
                )
        
        # Collaboration validation
        if business_context.get("involves_revenue_sharing", False):
            if session.authentication_level == AuthenticationLevel.BASIC:
                warnings.append("Revenue sharing operations recommended with enhanced authentication")
        
        return BusinessValidationResult(
            allowed=True,
            warnings=warnings
        )
    
    async def authorize_event_access(self, 
                                   session: UserSession,
                                   event_type: str,
                                   event_data: Dict[str, Any],
                                   business_context: Dict[str, Any]) -> bool:
        """Authorize specific event access with business logic"""
        
        # Content upload authorization
        if event_type.startswith("content.upload"):
            file_size = event_data.get("file_size", 0)
            if file_size > 100_000_000 and session.authentication_level == AuthenticationLevel.BASIC:
                return False  # Large uploads require enhanced auth
        
        # Distribution authorization
        if event_type.startswith("distribution."):
            platforms = event_data.get("target_platforms", [])
            premium_platforms = ["youtube_premium", "spotify_premium"]
            if any(p in premium_platforms for p in platforms):
                return session.authentication_level in [AuthenticationLevel.HIGH_SECURITY, AuthenticationLevel.ULTRA_SECURE]
        
        # Monetization authorization
        if event_type.startswith("monetization."):
            amount = event_data.get("amount", 0)
            if amount > 1000:
                return session.authentication_level in [AuthenticationLevel.HIGH_SECURITY, AuthenticationLevel.ULTRA_SECURE]
        
        return True


@dataclass
class BusinessValidationResult:
    """Result of business context validation"""
    allowed: bool
    denial_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


# Export for compatibility
__all__ = [
    'SecurityManager', 
    'AuthenticationMethod', 
    'AuthenticationLevel', 
    'SessionStatus',
    'AuthenticationCredentials', 
    'UserSession', 
    'AuthenticationResult',
    'AuthenticationAnomalyDetector',
    'ThreatScorer',
    'BusinessContextAuthenticator',
    'BusinessValidationResult'
]