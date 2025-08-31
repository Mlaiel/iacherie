"""Authentication Database Module Index - Enterprise Multi-Creator Platform

Central orchestrator for all authentication database operations supporting
multi-format content creators with enterprise-grade security, compliance,
and performance optimization. Integrates session management, token operations, 
biometric authentication, device trust, compliance tracking, and advanced audit.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer

Business Logic Flow:
Multi-Format Creator → Registration → Identity Verification → Multi-Factor Setup → 
Device Trust → Biometric Enrollment → Content Upload → AI Protection → 
Rights Management → Distribution → Monetization → Advanced Analytics
"""import asyncio
import hashlib
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from uuid import UUID, uuid4

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
import aiohttp
from cryptography.fernet import Fernet

# Import all authentication components
from .session_manager import SessionManager, SessionStore, UserSession
from .token_repository import TokenRepository, TokenManager, RefreshTokenStore
from .permission_manager import PermissionManager, RoleManager, AccessControl
from .multi_factor_auth import MultiFactorAuth, MFAProvider, TwoFactorSetup
from .oauth_providers import OAuthProviderManager, ExternalProvider, OAuthCredentials
from .user_credentials import UserCredentialManager, PasswordPolicy, LoginAttempts
from .biometric_auth import BiometricAuthManager, BiometricTemplate, BiometricVerification
from .device_registry import DeviceRegistry, TrustedDevice, DeviceFingerprint
from .authentication_logs import AuthenticationLogger, SecurityAudit, ActivityTracker
from .compliance_manager import ComplianceManager, GDPRCompliance, SOCCompliance

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Content creator type classifications"""    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEOGRAPHER = "videographer"
    ARTIST = "artist"
    
    
class AuthenticationResult(Enum):
    """Authentication operation results"""    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    MFA_REQUIRED = "mfa_required"
    DEVICE_VERIFICATION_REQUIRED = "device_verification_required"
    BIOMETRIC_VERIFICATION_REQUIRED = "biometric_verification_required"
    COMPLIANCE_VERIFICATION_REQUIRED = "compliance_verification_required"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"
    SECURITY_REVIEW_REQUIRED = "security_review_required"


@dataclass
class AuthenticationContext:
    """Complete authentication context"""    user_id: Optional[UUID] = None
    creator_type: Optional[CreatorType] = None
    session_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    risk_score: float = 0.0
    authentication_methods: List[str] = None
    
    def __post_init__(self):
        if self.authentication_methods is None:
            self.authentication_methods = []


class AuthenticationDatabaseManager:
    """    Enterprise Authentication Database Orchestrator
    
    Unified authentication database manager providing centralized access
    to all authentication-related database operations for multi-format
    content creators with enterprise security and compliance features.
    """    
    def __init__(
        self, 
        db_session: AsyncSession, 
        redis_client: redis.Redis,
        encryption_key: bytes,
        security_config: Dict[str, Any],
        geoip_db_path: Optional[str] = None,
        fraud_detection_enabled: bool = True
    ):
        """        Initialize enterprise authentication database manager.
        
        Args:
            db_session: Async SQLAlchemy database session
            redis_client: Redis client for caching and session storage
            encryption_key: Encryption key for sensitive data
            security_config: Security configuration parameters
            geoip_db_path: Path to GeoIP database for location services
            fraud_detection_enabled: Enable ML-based fraud detection
        """        self.db = db_session
        self.redis = redis_client
        self.encryption_key = encryption_key
        self.security_config = security_config
        self.fraud_detection_enabled = fraud_detection_enabled
        
        # Initialize all authentication components
        self.session_manager = SessionManager(db_session, redis_client)
        self.token_repository = TokenRepository(db_session, redis_client, encryption_key)
        self.token_manager = TokenManager(self.token_repository)
        self.permission_manager = PermissionManager(db_session)
        self.mfa_manager = MultiFactorAuth(db_session, encryption_key)
        self.oauth_manager = OAuthProviderManager(db_session, encryption_key)
        self.credential_manager = UserCredentialManager(db_session, encryption_key)
        self.biometric_manager = BiometricAuthManager(db_session, encryption_key)
        self.device_registry = DeviceRegistry(db_session, geoip_db_path)
        self.auth_logger = AuthenticationLogger(db_session)
        self.compliance_manager = ComplianceManager(db_session)
        
        # Cache for rate limiting
        self._rate_limit_cache = {}
        
        logger.info("Enterprise authentication database manager initialized successfully")
    
    async def authenticate_creator(
        self,
        username: str,
        password: str,
        device_info: Dict[str, Any],
        request_context: Dict[str, Any]
    ) -> Tuple[AuthenticationResult, Optional[AuthenticationContext]]:
        """        Complete creator authentication flow with comprehensive security checks.
        
        Args:
            username: Creator username or email
            password: Creator password
            device_info: Device information for fingerprinting
            request_context: Request context (IP, headers, etc.)
            
        Returns:
            Authentication result with tokens and security status
        """        try:
            # Step 1: Validate credentials
            credential_result = await self.credential_manager.validate_credentials(
                username, password
            )
            
            if not credential_result["valid"]:
                await self.auth_logger.log_auth_event(
                    event_type="login_failure",
                    auth_result="failure",
                    auth_context=request_context,
                    username=username,
                    failure_reason="invalid_credentials"
                )
                return {"success": False, "reason": "Invalid credentials"}
            
            user_id = credential_result["user_id"]
            
            # Step 2: Check account status
            account_status = await self.credential_manager.get_account_status(user_id)
            if account_status != "active":
                return {"success": False, "reason": f"Account {account_status}"}
            
            # Step 3: Device verification
            device_fingerprint = await self.device_registry.register_device(
                user_id=user_id,
                user_agent=request_context["user_agent"],
                ip_address=request_context["ip_address"],
                request_headers=request_context["headers"]
            )
            
            device_trust = await self.device_registry.verify_device_trust(
                user_id=user_id,
                fingerprint_hash=device_fingerprint[0],
                ip_address=request_context["ip_address"],
                activity_type="login"
            )
            
            # Step 4: Multi-factor authentication check
            mfa_required = await self.mfa_manager.is_mfa_required(user_id)
            if mfa_required and not device_trust.get("trusted", False):
                return {
                    "success": False,
                    "mfa_required": True,
                    "available_methods": await self.mfa_manager.get_user_mfa_methods(user_id),
                    "session_token": await self._create_pending_session(user_id, device_info)
                }
            
            # Step 5: Generate authentication tokens
            tokens = await self.token_manager.authenticate_user(
                user_id=user_id,
                device_fingerprint=device_fingerprint[0],
                ip_address=request_context["ip_address"],
                user_agent=request_context["user_agent"],
                scopes=["content:read", "content:write", "profile:read"],
                permissions=await self.permission_manager.get_user_permissions(user_id)
            )
            
            # Step 6: Create session
            session_id = await self.session_manager.create_session(
                user_id=user_id,
                device_info=device_info,
                security_context=request_context
            )
            
            # Step 7: Log successful authentication
            await self.auth_logger.log_auth_event(
                event_type="login_success",
                auth_result="success",
                auth_context=request_context,
                user_id=user_id,
                auth_method="password",
                duration_ms=request_context.get("duration_ms")
            )
            
            # Step 8: Update device activity
            await self.device_registry._log_device_activity(
                user_id=user_id,
                device_id=device_trust.get("device_id"),
                activity_type="login",
                activity_result="success",
                ip_address=request_context["ip_address"],
                session_id=session_id
            )
            
            return {
                "success": True,
                "tokens": tokens,
                "session_id": session_id,
                "user_id": user_id,
                "device_trusted": device_trust.get("trusted", False),
                "requires_device_verification": device_trust.get("requires_verification", False)
            }
            
        except Exception as e:
            logger.error(f"Creator authentication failed: {e}")
            return {"success": False, "reason": "Authentication system error"}
    
    async def register_new_creator(
        self,
        username: str,
        email: str,
        password: str,
        creator_type: str,  # musician, blogger, photographer, influencer, comedian
        device_info: Dict[str, Any],
        request_context: Dict[str, Any],
        consent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Register new content creator with complete compliance and security setup.
        
        Args:
            username: Unique creator username
            email: Creator email address
            password: Creator password
            creator_type: Type of creator (musician, blogger, etc.)
            device_info: Device information
            request_context: Request context
            consent_data: GDPR consent information
            
        Returns:
            Registration result with verification requirements
        """        try:
            # Step 1: Create user credentials
            user_id = await self.credential_manager.create_user_account(
                username=username,
                email=email,
                password=password,
                account_type=creator_type
            )
            
            if not user_id:
                return {"success": False, "reason": "Account creation failed"}
            
            # Step 2: Setup default permissions
            await self.permission_manager.assign_creator_permissions(
                user_id=user_id,
                creator_type=creator_type
            )
            
            # Step 3: Initialize compliance tracking
            await self.compliance_manager.initialize_gdpr_compliance(
                user_id=user_id,
                data_categories=self._get_creator_data_categories(creator_type),
                processing_purposes=self._get_creator_processing_purposes(),
                legal_basis="consent",
                consent_required=True
            )
            
            # Step 4: Record consent
            await self.compliance_manager.record_consent(
                user_id=user_id,
                consent_purposes=consent_data["purposes"],
                consent_given=consent_data["given"],
                consent_method="registration_form"
            )
            
            # Step 5: Register initial device
            device_fingerprint = await self.device_registry.register_device(
                user_id=user_id,
                user_agent=request_context["user_agent"],
                ip_address=request_context["ip_address"],
                request_headers=request_context["headers"],
                device_name=f"{creator_type.title()} Creator Device"
            )
            
            # Step 6: Establish device trust
            trusted_device_id = await self.device_registry.establish_device_trust(
                user_id=user_id,
                fingerprint_id=device_fingerprint[0],
                verification_method="email_verification",
                device_nickname=f"Primary {creator_type.title()} Device",
                ip_address=request_context["ip_address"]
            )
            
            # Step 7: Log registration
            await self.auth_logger.log_auth_event(
                event_type="user_registration",
                auth_result="success",
                auth_context=request_context,
                user_id=user_id,
                auth_details={
                    "creator_type": creator_type,
                    "device_registered": True,
                    "consent_recorded": True
                }
            )
            
            # Step 8: Log compliance
            await self.auth_logger.log_security_audit(
                audit_category="data_protection",
                audit_action="user_registration",
                audit_message=f"New {creator_type} creator registered with GDPR compliance",
                user_id=user_id,
                compliance_tags=["GDPR", "consent"],
                ip_address=request_context["ip_address"]
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "verification_required": True,
                "verification_methods": ["email"],
                "trusted_device_id": trusted_device_id,
                "next_steps": [
                    "verify_email",
                    "setup_mfa",
                    "complete_profile"
                ]
            }
            
        except Exception as e:
            logger.error(f"Creator registration failed: {e}")
            return {"success": False, "reason": "Registration system error"}
    
    def _get_creator_data_categories(self, creator_type: str) -> List[str]:
        """Get data categories based on creator type"""        base_categories = [
            "personal_identity",
            "authentication_data",
            "device_data",
            "behavioral_data"
        ]
        
        creator_specific = {
            "musician": ["content_data", "location_data"],
            "blogger": ["content_data", "communication_data"],
            "photographer": ["content_data", "location_data"],
            "influencer": ["content_data", "behavioral_data", "communication_data"],
            "comedian": ["content_data", "location_data"]
        }
        
        return base_categories + creator_specific.get(creator_type, [])
    
    def _get_creator_processing_purposes(self) -> List[str]:
        """Get processing purposes for creators"""        return [
            "authentication",
            "content_protection",
            "personalization",
            "analytics",
            "security",
            "fraud_prevention"
        ]
    
    async def _create_pending_session(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Create pending session for MFA completion"""        try:
            pending_session = await self.session_manager.create_pending_session(
                user_id=user_id,
                device_info=device_info,
                purpose="mfa_completion",
                expires_in_minutes=10
            )
            return pending_session
            
        except Exception as e:
            logger.error(f"Failed to create pending session: {e}")
            return None
    
    async def complete_mfa_verification(
        self,
        session_token: str,
        mfa_code: str,
        mfa_method: str,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete MFA verification and issue full authentication"""        try:
            # Validate pending session
            session_data = await self.session_manager.validate_pending_session(session_token)
            if not session_data:
                return {"success": False, "reason": "Invalid or expired session"}
            
            user_id = session_data["user_id"]
            
            # Verify MFA code
            mfa_result = await self.mfa_manager.verify_mfa_code(
                user_id=user_id,
                code=mfa_code,
                method=mfa_method
            )
            
            if not mfa_result["valid"]:
                return {"success": False, "reason": "Invalid MFA code"}
            
            # Complete authentication
            tokens = await self.token_manager.authenticate_user(
                user_id=user_id,
                device_fingerprint=device_info["fingerprint"],
                ip_address=device_info["ip_address"],
                user_agent=device_info["user_agent"],
                scopes=["content:read", "content:write", "profile:read"],
                permissions=await self.permission_manager.get_user_permissions(user_id)
            )
            
            # Create full session
            session_id = await self.session_manager.create_session(
                user_id=user_id,
                device_info=device_info,
                security_context={"mfa_verified": True}
            )
            
            # Invalidate pending session
            await self.session_manager.invalidate_pending_session(session_token)
            
            return {
                "success": True,
                "tokens": tokens,
                "session_id": session_id,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"MFA verification failed: {e}")
            return {"success": False, "reason": "MFA verification system error"}
    
    async def enroll_biometric(
        self,
        user_id: str,
        biometric_type: str,
        biometric_data: bytes,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enroll user biometric for authentication"""        try:
            # Extract biometric features (implementation specific)
            features = await self._extract_biometric_features(biometric_type, biometric_data)
            if not features:
                return {"success": False, "reason": "Biometric feature extraction failed"}
            
            # Enroll biometric
            template_id = await self.biometric_manager.enroll_biometric(
                user_id=user_id,
                biometric_type=biometric_type,
                features=features,
                device_info=device_info
            )
            
            if not template_id:
                return {"success": False, "reason": "Biometric enrollment failed"}
            
            # Log enrollment
            await self.auth_logger.log_auth_event(
                event_type="biometric_enrolled",
                auth_result="success",
                auth_context=device_info,
                user_id=user_id,
                auth_details={
                    "biometric_type": biometric_type,
                    "template_id": template_id
                }
            )
            
            return {
                "success": True,
                "template_id": template_id,
                "biometric_type": biometric_type
            }
            
        except Exception as e:
            logger.error(f"Biometric enrollment failed: {e}")
            return {"success": False, "reason": "Biometric enrollment system error"}
    
    async def _extract_biometric_features(self, biometric_type: str, data: bytes):
        """Extract biometric features from raw data"""        # Implementation would use appropriate biometric libraries
        # This is a placeholder for the actual feature extraction
        pass
    
    async def get_creator_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for content creator"""        try:
            dashboard_data = {
                "authentication_status": {
                    "mfa_enabled": await self.mfa_manager.is_mfa_enabled(user_id),
                    "biometrics_enrolled": len(await self.biometric_manager.get_user_biometrics(user_id)),
                    "trusted_devices": len(await self.device_registry.get_user_devices(user_id)),
                    "active_sessions": await self.session_manager.get_active_session_count(user_id)
                },
                "security_status": {
                    "recent_alerts": await self.auth_logger.get_security_alerts(user_id=user_id, limit=5),
                    "login_history": await self.auth_logger.get_user_auth_history(user_id, limit=10),
                    "compliance_status": await self.compliance_manager.get_compliance_status(user_id)
                },
                "permissions": await self.permission_manager.get_user_permissions(user_id),
                "oauth_connections": await self.oauth_manager.get_user_connections(user_id)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    async def revoke_all_access(self, user_id: str, reason: str = "security_breach") -> bool:
        """Emergency access revocation for security incidents"""        try:
            # Revoke all tokens
            await self.token_repository.revoke_all_user_tokens(user_id, reason)
            
            # Terminate all sessions
            await self.session_manager.terminate_all_user_sessions(user_id, reason)
            
            # Revoke device trust
            devices = await self.device_registry.get_user_devices(user_id)
            for device in devices:
                await self.device_registry.revoke_device_trust(
                    user_id, device["id"], reason
                )
            
            # Log security action
            await self.auth_logger.log_security_audit(
                audit_category="security",
                audit_action="emergency_revocation",
                audit_message=f"All access revoked for user due to: {reason}",
                user_id=user_id,
                severity_level="critical"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Emergency access revocation failed: {e}")
            return False
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Cleanup expired authentication data"""        try:
            cleanup_stats = {}
            
            # Cleanup expired tokens
            cleanup_stats["expired_tokens"] = await self.token_repository.cleanup_expired_tokens()
            
            # Cleanup expired sessions
            cleanup_stats["expired_sessions"] = await self.session_manager.cleanup_expired_sessions()
            
            # Execute compliance cleanup
            compliance_stats = await self.compliance_manager.execute_data_retention_cleanup()
            cleanup_stats.update(compliance_stats)
            
            logger.info(f"Authentication cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Authentication cleanup failed: {e}")
            return {"error": 1}
    
    async def generate_security_report(
        self, 
        user_id: Optional[str] = None,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive security report"""        try:
            report = {
                "report_id": str(uuid4()),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "timeframe_days": timeframe_days,
                "summary": {}
            }
            
            if user_id:
                # User-specific security report
                report["user_id"] = user_id
                report["user_security"] = await self._generate_user_security_report(user_id, timeframe_days)
            else:
                # System-wide security report
                report["system_security"] = await self._generate_system_security_report(timeframe_days)
            
            return report
            
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            return {"error": "Report generation failed"}
    
    async def _generate_user_security_report(self, user_id: str, days: int) -> Dict[str, Any]:
        """Generate user-specific security report"""        return {
            "authentication_summary": {
                "total_logins": await self.auth_logger.count_user_logins(user_id, days),
                "failed_attempts": await self.auth_logger.count_failed_attempts(user_id, days),
                "unique_devices": await self.device_registry.count_user_devices(user_id),
                "unique_locations": await self.auth_logger.count_unique_locations(user_id, days)
            },
            "security_events": await self.auth_logger.get_security_alerts(user_id=user_id, days=days),
            "device_analysis": await self.device_registry.analyze_device_patterns(user_id, days),
            "compliance_status": await self.compliance_manager.get_compliance_status(user_id),
            "risk_assessment": await self._calculate_user_risk_profile(user_id, days)
        }
    
    async def _generate_system_security_report(self, days: int) -> Dict[str, Any]:
        """Generate system-wide security report"""        return {
            "authentication_metrics": {
                "total_authentications": await self.auth_logger.count_total_authentications(days),
                "success_rate": await self.auth_logger.calculate_success_rate(days),
                "average_risk_score": await self.auth_logger.calculate_average_risk_score(days),
                "blocked_attempts": await self.auth_logger.count_blocked_attempts(days)
            },
            "threat_analysis": {
                "suspicious_patterns": await self.auth_logger.detect_suspicious_patterns(days),
                "brute_force_attempts": await self.auth_logger.detect_brute_force_attempts(days),
                "geographic_anomalies": await self.auth_logger.detect_geographic_anomalies(days)
            },
            "compliance_metrics": await self.compliance_manager.generate_compliance_metrics(days),
            "performance_metrics": {
                "average_auth_time": await self._calculate_average_auth_time(days),
                "system_availability": await self._calculate_system_availability(days)
            }
        }
    
    async def _calculate_user_risk_profile(self, user_id: str, days: int) -> Dict[str, Any]:
        """Calculate comprehensive user risk profile"""        try:
            # Behavioral analysis
            login_patterns = await self.auth_logger.analyze_login_patterns(user_id, days)
            device_patterns = await self.device_registry.analyze_device_usage(user_id, days)
            location_patterns = await self.auth_logger.analyze_location_patterns(user_id, days)
            
            # Risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Unusual login times
            if login_patterns.get("unusual_times", 0) > 0:
                risk_factors.append("unusual_login_times")
                risk_score += 0.2
            
            # Multiple devices
            if device_patterns.get("device_count", 0) > 5:
                risk_factors.append("multiple_devices")
                risk_score += 0.1
            
            # Geographic distribution
            if location_patterns.get("country_count", 0) > 3:
                risk_factors.append("multiple_countries")
                risk_score += 0.3
            
            # Recent security events
            recent_alerts = await self.auth_logger.get_security_alerts(user_id=user_id, days=7)
            if recent_alerts:
                risk_factors.append("recent_security_events")
                risk_score += len(recent_alerts) * 0.1
            
            return {
                "risk_score": min(risk_score, 1.0),
                "risk_level": "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low",
                "risk_factors": risk_factors,
                "behavioral_patterns": {
                    "login_patterns": login_patterns,
                    "device_patterns": device_patterns,
                    "location_patterns": location_patterns
                },
                "recommendations": self._generate_security_recommendations(risk_score, risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Risk profile calculation failed: {e}")
            return {"error": "Risk calculation failed"}
    
    def _generate_security_recommendations(self, risk_score: float, risk_factors: List[str]) -> List[str]:
        """Generate security recommendations based on risk analysis"""        recommendations = []
        
        if risk_score > 0.6:
            recommendations.append("Enable mandatory MFA for all logins")
            recommendations.append("Review and revoke suspicious device access")
        
        if "multiple_countries" in risk_factors:
            recommendations.append("Enable location-based alerts")
            recommendations.append("Review travel patterns for authenticity")
        
        if "multiple_devices" in risk_factors:
            recommendations.append("Audit registered devices")
            recommendations.append("Enable device approval workflow")
        
        if "unusual_login_times" in risk_factors:
            recommendations.append("Enable time-based access restrictions")
        
        if "recent_security_events" in risk_factors:
            recommendations.append("Investigate recent security alerts")
            recommendations.append("Consider temporary access restrictions")
        
        # Always include baseline recommendations
        if risk_score > 0.3:
            recommendations.append("Enable biometric authentication")
            recommendations.append("Regular password updates")
            recommendations.append("Security awareness training")
        
        return recommendations
    
    async def _calculate_average_auth_time(self, days: int) -> float:
        """Calculate average authentication time"""        try:
            auth_times = await self.auth_logger.get_authentication_durations(days)
            if auth_times:
                return sum(auth_times) / len(auth_times)
            return 0.0
        except Exception as e:
            logger.error(f"Average auth time calculation failed: {e}")
            return 0.0
    
    async def _calculate_system_availability(self, days: int) -> float:
        """Calculate system availability percentage"""        try:
            # This would integrate with monitoring systems
            # For now, return a high availability assumption
            return 99.9
        except Exception as e:
            logger.error(f"System availability calculation failed: {e}")
            return 0.0
    
    @asynccontextmanager
    async def transaction(self):
        """Database transaction context manager"""        try:
            async with self.db.begin():
                yield self.db
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            await self.db.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for authentication system"""        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {}
            }
            
            # Database connectivity
            try:
                await self.db.execute("SELECT 1")
                health_status["components"]["database"] = "healthy"
            except Exception as e:
                health_status["components"]["database"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Redis connectivity
            try:
                await self.redis.ping()
                health_status["components"]["redis"] = "healthy"
            except Exception as e:
                health_status["components"]["redis"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Component health checks
            for component_name, component in [
                ("session_manager", self.session_manager),
                ("token_repository", self.token_repository),
                ("permission_manager", self.permission_manager),
                ("mfa_manager", self.mfa_manager),
                ("device_registry", self.device_registry),
                ("auth_logger", self.auth_logger),
                ("compliance_manager", self.compliance_manager)
            ]:
                try:
                    if hasattr(component, "health_check"):
                        component_health = await component.health_check()
                        health_status["components"][component_name] = component_health
                    else:
                        health_status["components"][component_name] = "healthy"
                except Exception as e:
                    health_status["components"][component_name] = f"unhealthy: {e}"
                    health_status["status"] = "degraded"
            
            # Performance metrics
            health_status["metrics"] = {
                "active_sessions": await self.session_manager.count_active_sessions(),
                "redis_memory_usage": await self._get_redis_memory_usage(),
                "recent_auth_rate": await self.auth_logger.get_recent_auth_rate()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _get_redis_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage information"""        try:
            info = await self.redis.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B")
            }
        except Exception as e:
            logger.error(f"Redis memory usage check failed: {e}")
            return {"error": str(e)}


# Advanced authentication factory and utilities
class AuthenticationFactory:
    """Factory for creating authentication components with different configurations"""    
    @staticmethod
    async def create_production_manager(
        db_session: AsyncSession,
        redis_client: redis.Redis,
        config: Dict[str, Any]
    ) -> AuthenticationDatabaseManager:
        """Create production-ready authentication manager"""        return AuthenticationDatabaseManager(
            db_session=db_session,
            redis_client=redis_client,
            encryption_key=config["encryption_key"],
            security_config=config.get("security", {}),
            geoip_db_path=config.get("geoip_db_path"),
            fraud_detection_enabled=config.get("fraud_detection", True)
        )
    
    @staticmethod
    async def create_development_manager(
        db_session: AsyncSession,
        redis_client: redis.Redis
    ) -> AuthenticationDatabaseManager:
        """Create development authentication manager with relaxed security"""        dev_config = {
            "max_user_attempts": 10,
            "max_ip_attempts": 50,
            "enforce_mfa": False
        }
        
        return AuthenticationDatabaseManager(
            db_session=db_session,
            redis_client=redis_client,
            encryption_key=Fernet.generate_key(),
            security_config=dev_config,
            fraud_detection_enabled=False
        )


# Export the main manager class and key components
__all__ = [
    "AuthenticationDatabaseManager",
    "AuthenticationFactory",
    "AuthenticationResult",
    "AuthenticationContext",
    "CreatorType",
    "SessionManager",
    "TokenRepository", 
    "TokenManager",
    "PermissionManager",
    "MultiFactorAuth",
    "OAuthProviderManager",
    "UserCredentialManager",
    "BiometricAuthManager",
    "DeviceRegistry",
    "AuthenticationLogger",
    "ComplianceManager"
]
