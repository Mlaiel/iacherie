#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Authentication Configuration Module
=============================================

Enterprise-grade authentication configuration for the Ainflue platform.
Handles multi-factor authentication, OAuth, SSO, biometric authentication,
passwordless authentication, and comprehensive identity management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

class AuthenticationMethod(str, Enum):
    """Authentication methods"""
    PASSWORD = "password"
    MULTI_FACTOR = "multi_factor"
    BIOMETRIC = "biometric"
    PASSWORDLESS = "passwordless"
    CERTIFICATE = "certificate"
    OAUTH = "oauth"
    SAML = "saml"
    WEBAUTHN = "webauthn"

class IdentityProvider(str, Enum):
    """Identity providers"""
    INTERNAL = "internal"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"
    FACEBOOK = "facebook"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    DISCORD = "discord"

class BiometricType(str, Enum):
    """Biometric authentication types"""
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    VOICE = "voice"
    IRIS = "iris"
    PALM = "palm"
    BEHAVIORAL = "behavioral"

@dataclass
class PasswordPolicyConfig:
    """Password policy configuration"""
    enabled: bool = True
    
    # Password requirements
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Password history and rotation
    password_history_count: int = 12
    password_expiry_days: int = 90
    force_password_change: bool = False
    
    # Complexity rules
    max_repeated_chars: int = 2
    no_common_passwords: bool = True
    no_personal_info: bool = True
    no_keyboard_patterns: bool = True
    
    # Password hashing
    hash_algorithm: str = "argon2id"
    salt_rounds: int = 12
    memory_cost: int = 65536  # 64 MB
    time_cost: int = 3
    parallelism: int = 4
    
    def get_config(self) -> Dict[str, Any]:
        """Get password policy configuration"""
        return {
            "enabled": self.enabled,
            "requirements": {
                "min_length": self.min_length,
                "max_length": self.max_length,
                "require_uppercase": self.require_uppercase,
                "require_lowercase": self.require_lowercase,
                "require_numbers": self.require_numbers,
                "require_special_chars": self.require_special_chars,
                "special_chars": self.special_chars
            },
            "lifecycle": {
                "password_history_count": self.password_history_count,
                "password_expiry_days": self.password_expiry_days,
                "force_password_change": self.force_password_change
            },
            "complexity": {
                "max_repeated_chars": self.max_repeated_chars,
                "no_common_passwords": self.no_common_passwords,
                "no_personal_info": self.no_personal_info,
                "no_keyboard_patterns": self.no_keyboard_patterns
            },
            "hashing": {
                "hash_algorithm": self.hash_algorithm,
                "salt_rounds": self.salt_rounds,
                "memory_cost": self.memory_cost,
                "time_cost": self.time_cost,
                "parallelism": self.parallelism
            }
        }

@dataclass
class MultiFactorAuthConfig:
    """Multi-factor authentication configuration"""
    enabled: bool = True
    required_for_admin: bool = True
    required_for_creators: bool = True
    required_for_sensitive_ops: bool = True
    
    # Supported MFA methods
    supported_methods: List[str] = field(default_factory=lambda: [
        "totp", "sms", "email", "backup_codes", "push_notification", 
        "hardware_token", "biometric", "webauthn"
    ])
    
    # TOTP (Time-based One-Time Password)
    totp_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "issuer": "Ainflue",
        "algorithm": "SHA256",
        "digits": 6,
        "period": 30,
        "window": 1,
        "backup_tokens": 10
    })
    
    # SMS authentication
    sms_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "provider": "twilio",
        "code_length": 6,
        "code_expiry_minutes": 5,
        "rate_limit_per_hour": 5,
        "international_numbers": True
    })
    
    # Email authentication
    email_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "code_length": 8,
        "code_expiry_minutes": 10,
        "rate_limit_per_hour": 3,
        "html_template": True
    })
    
    # Hardware tokens
    hardware_token_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "supported_types": ["yubikey", "rsa_securid", "fido2"],
        "require_pin": True,
        "timeout_seconds": 30
    })
    
    # WebAuthn (FIDO2)
    webauthn_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "rp_name": "Ainflue Platform",
        "rp_id": "ainflue.com",
        "require_resident_key": False,
        "user_verification": "preferred",
        "authenticator_attachment": "any",
        "timeout_ms": 60000
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get MFA configuration"""
        return {
            "enabled": self.enabled,
            "requirements": {
                "required_for_admin": self.required_for_admin,
                "required_for_creators": self.required_for_creators,
                "required_for_sensitive_ops": self.required_for_sensitive_ops
            },
            "supported_methods": self.supported_methods,
            "methods": {
                "totp": self.totp_config,
                "sms": self.sms_config,
                "email": self.email_config,
                "hardware_token": self.hardware_token_config,
                "webauthn": self.webauthn_config
            }
        }

@dataclass
class BiometricAuthConfig:
    """Biometric authentication configuration"""
    enabled: bool = True
    
    # Supported biometric types
    supported_types: List[BiometricType] = field(default_factory=lambda: [
        BiometricType.FINGERPRINT,
        BiometricType.FACE_ID,
        BiometricType.VOICE,
        BiometricType.BEHAVIORAL
    ])
    
    # Fingerprint authentication
    fingerprint_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "template_storage": "secure_enclave",
        "match_threshold": 0.8,
        "liveness_detection": True,
        "max_attempts": 5
    })
    
    # Face ID authentication
    face_id_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "3d_depth_required": True,
        "anti_spoofing": True,
        "template_encryption": True,
        "confidence_threshold": 0.9
    })
    
    # Voice authentication
    voice_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "text_dependent": False,
        "noise_reduction": True,
        "voice_print_encryption": True,
        "verification_threshold": 0.85
    })
    
    # Behavioral biometrics
    behavioral_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "typing_patterns": True,
        "mouse_dynamics": True,
        "gait_analysis": False,
        "continuous_authentication": True,
        "risk_scoring": True
    })
    
    # Privacy and security
    privacy_config: Dict[str, Any] = field(default_factory=lambda: {
        "local_processing": True,
        "template_encryption": True,
        "no_raw_biometric_storage": True,
        "consent_required": True,
        "data_retention_days": 90
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get biometric authentication configuration"""
        return {
            "enabled": self.enabled,
            "supported_types": [bt.value for bt in self.supported_types],
            "methods": {
                "fingerprint": self.fingerprint_config,
                "face_id": self.face_id_config,
                "voice": self.voice_config,
                "behavioral": self.behavioral_config
            },
            "privacy": self.privacy_config
        }

@dataclass
class OAuthConfig:
    """OAuth authentication configuration"""
    enabled: bool = True
    
    # OAuth providers
    providers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "google": {
            "enabled": True,
            "client_id": "google_client_id",
            "scopes": ["openid", "email", "profile"],
            "prompt": "select_account"
        },
        "microsoft": {
            "enabled": True,
            "client_id": "microsoft_client_id",
            "scopes": ["openid", "email", "profile"],
            "tenant": "common"
        },
        "apple": {
            "enabled": True,
            "client_id": "apple_client_id",
            "scopes": ["email", "name"],
            "response_mode": "form_post"
        },
        "github": {
            "enabled": True,
            "client_id": "github_client_id",
            "scopes": ["user:email", "read:user"]
        }
    })
    
    # OAuth flow configuration
    flow_config: Dict[str, Any] = field(default_factory=lambda: {
        "authorization_code_flow": True,
        "implicit_flow": False,  # Deprecated
        "client_credentials_flow": True,
        "device_authorization_flow": True,
        "pkce_required": True,
        "state_parameter": True
    })
    
    # Token configuration
    token_config: Dict[str, Any] = field(default_factory=lambda: {
        "access_token_lifetime": 3600,  # 1 hour
        "refresh_token_lifetime": 2592000,  # 30 days
        "id_token_lifetime": 3600,  # 1 hour
        "token_rotation": True,
        "revocation_endpoint": True
    })
    
    # Security settings
    security_config: Dict[str, Any] = field(default_factory=lambda: {
        "validate_redirect_uri": True,
        "require_https": True,
        "validate_issuer": True,
        "validate_audience": True,
        "check_token_expiry": True,
        "verify_signature": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get OAuth configuration"""
        return {
            "enabled": self.enabled,
            "providers": self.providers,
            "flow": self.flow_config,
            "tokens": self.token_config,
            "security": self.security_config
        }

@dataclass
class SessionManagementConfig:
    """Session management configuration"""
    
    # Session settings
    session_timeout_minutes: int = 480  # 8 hours
    absolute_timeout_minutes: int = 1440  # 24 hours
    idle_timeout_minutes: int = 60  # 1 hour
    
    # Session security
    secure_cookies: bool = True
    httponly_cookies: bool = True
    samesite_policy: str = "strict"
    session_encryption: bool = True
    session_signing: bool = True
    
    # Concurrent sessions
    max_concurrent_sessions: int = 5
    allow_multiple_devices: bool = True
    force_logout_on_password_change: bool = True
    
    # Session monitoring
    track_session_activity: bool = True
    log_session_events: bool = True
    detect_session_hijacking: bool = True
    ip_validation: bool = True
    user_agent_validation: bool = True
    
    # Remember me functionality
    remember_me_enabled: bool = True
    remember_me_duration_days: int = 30
    remember_me_secure: bool = True
    
    def get_config(self) -> Dict[str, Any]:
        """Get session management configuration"""
        return {
            "timeouts": {
                "session_timeout_minutes": self.session_timeout_minutes,
                "absolute_timeout_minutes": self.absolute_timeout_minutes,
                "idle_timeout_minutes": self.idle_timeout_minutes
            },
            "security": {
                "secure_cookies": self.secure_cookies,
                "httponly_cookies": self.httponly_cookies,
                "samesite_policy": self.samesite_policy,
                "session_encryption": self.session_encryption,
                "session_signing": self.session_signing
            },
            "concurrent_sessions": {
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "allow_multiple_devices": self.allow_multiple_devices,
                "force_logout_on_password_change": self.force_logout_on_password_change
            },
            "monitoring": {
                "track_session_activity": self.track_session_activity,
                "log_session_events": self.log_session_events,
                "detect_session_hijacking": self.detect_session_hijacking,
                "ip_validation": self.ip_validation,
                "user_agent_validation": self.user_agent_validation
            },
            "remember_me": {
                "remember_me_enabled": self.remember_me_enabled,
                "remember_me_duration_days": self.remember_me_duration_days,
                "remember_me_secure": self.remember_me_secure
            }
        }

@dataclass
class RiskBasedAuthConfig:
    """Risk-based authentication configuration"""
    enabled: bool = True
    
    # Risk factors
    risk_factors: Dict[str, Any] = field(default_factory=lambda: {
        "geolocation": {
            "enabled": True,
            "new_location_risk": 0.6,
            "high_risk_countries": ["CN", "RU", "KP"],
            "travel_speed_check": True
        },
        "device_fingerprinting": {
            "enabled": True,
            "new_device_risk": 0.7,
            "device_reputation": True,
            "browser_fingerprinting": True
        },
        "behavioral_analysis": {
            "enabled": True,
            "typing_patterns": True,
            "navigation_patterns": True,
            "time_based_patterns": True
        },
        "network_analysis": {
            "enabled": True,
            "tor_detection": True,
            "vpn_detection": True,
            "proxy_detection": True,
            "malicious_ip_check": True
        }
    })
    
    # Risk scoring
    risk_scoring: Dict[str, Any] = field(default_factory=lambda: {
        "algorithm": "weighted_sum",
        "weights": {
            "geolocation": 0.25,
            "device": 0.30,
            "behavioral": 0.25,
            "network": 0.20
        },
        "low_risk_threshold": 0.3,
        "medium_risk_threshold": 0.6,
        "high_risk_threshold": 0.8
    })
    
    # Risk responses
    risk_responses: Dict[str, Any] = field(default_factory=lambda: {
        "low_risk": {
            "action": "allow",
            "additional_verification": False
        },
        "medium_risk": {
            "action": "challenge",
            "mfa_required": True,
            "captcha_required": True
        },
        "high_risk": {
            "action": "block",
            "manual_review": True,
            "admin_notification": True
        }
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get risk-based authentication configuration"""
        return {
            "enabled": self.enabled,
            "risk_factors": self.risk_factors,
            "risk_scoring": self.risk_scoring,
            "risk_responses": self.risk_responses
        }

class AuthenticationConfiguration:
    """Main authentication configuration manager"""
    
    def __init__(self):
        """Initialize authentication configuration"""
        # Authentication components
        self.password_policy = PasswordPolicyConfig()
        self.mfa_config = MultiFactorAuthConfig()
        self.biometric_config = BiometricAuthConfig()
        self.oauth_config = OAuthConfig()
        self.session_config = SessionManagementConfig()
        self.risk_auth_config = RiskBasedAuthConfig()
        
        # Supported authentication methods
        self.enabled_methods = [
            AuthenticationMethod.PASSWORD,
            AuthenticationMethod.MULTI_FACTOR,
            AuthenticationMethod.BIOMETRIC,
            AuthenticationMethod.OAUTH,
            AuthenticationMethod.WEBAUTHN
        ]
        
        # Global authentication settings
        self.password_less_enabled = True
        self.adaptive_authentication = True
        self.zero_trust_verification = True
        
        # Account security
        self.account_lockout_enabled = True
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
        self.progressive_lockout = True
        
        # Compliance
        self.gdpr_compliant = True
        self.privacy_by_design = True
        self.data_minimization = True
    
    def get_authentication_strength_score(self) -> float:
        """Calculate authentication strength score (0-1)"""
        score = 0.0
        
        # Base password score
        if self.password_policy.enabled:
            score += 0.2
        
        # MFA bonus
        if self.mfa_config.enabled:
            score += 0.3
        
        # Biometric bonus
        if self.biometric_config.enabled:
            score += 0.2
        
        # Risk-based authentication bonus
        if self.risk_auth_config.enabled:
            score += 0.2
        
        # Zero trust bonus
        if self.zero_trust_verification:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported identity providers"""
        providers = ["internal"]  # Always support internal authentication
        
        for provider, config in self.oauth_config.providers.items():
            if config.get("enabled", False):
                providers.append(provider)
        
        return providers
    
    async def authenticate_user(self, 
                              credentials: Dict[str, Any],
                              risk_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Authenticate user with comprehensive verification"""
        
        authentication_result = {
            "success": False,
            "user_id": None,
            "authentication_methods": [],
            "risk_score": 0.0,
            "additional_verification_required": False,
            "session_token": None,
            "expires_at": None
        }
        
        # Risk assessment
        if self.risk_auth_config.enabled and risk_context:
            risk_score = await self._calculate_risk_score(risk_context)
            authentication_result["risk_score"] = risk_score
            
            if risk_score > self.risk_auth_config.risk_scoring["high_risk_threshold"]:
                authentication_result["additional_verification_required"] = True
                return authentication_result
        
        # Primary authentication
        primary_auth_success = await self._verify_primary_credentials(credentials)
        if not primary_auth_success:
            return authentication_result
        
        authentication_result["authentication_methods"].append("primary")
        
        # MFA verification if required
        if self.mfa_config.enabled:
            mfa_success = await self._verify_mfa(credentials)
            if not mfa_success:
                authentication_result["additional_verification_required"] = True
                return authentication_result
            authentication_result["authentication_methods"].append("mfa")
        
        # Biometric verification if available
        if self.biometric_config.enabled and "biometric_data" in credentials:
            biometric_success = await self._verify_biometric(credentials["biometric_data"])
            if biometric_success:
                authentication_result["authentication_methods"].append("biometric")
        
        # Success
        authentication_result["success"] = True
        authentication_result["user_id"] = credentials.get("user_id")
        authentication_result["session_token"] = "session_token_placeholder"
        authentication_result["expires_at"] = (
            datetime.now() + timedelta(minutes=self.session_config.session_timeout_minutes)
        ).isoformat()
        
        return authentication_result
    
    async def _calculate_risk_score(self, risk_context: Dict[str, Any]) -> float:
        """Calculate risk score based on context"""
        # This would implement actual risk calculation
        # For now, return a mock score
        return 0.2
    
    async def _verify_primary_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Verify primary authentication credentials"""
        # This would implement actual credential verification
        # For now, return success for demonstration
        return True
    
    async def _verify_mfa(self, credentials: Dict[str, Any]) -> bool:
        """Verify multi-factor authentication"""
        # This would implement actual MFA verification
        # For now, return success for demonstration
        return True
    
    async def _verify_biometric(self, biometric_data: Dict[str, Any]) -> bool:
        """Verify biometric authentication"""
        # This would implement actual biometric verification
        # For now, return success for demonstration
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete authentication configuration"""
        return {
            "authentication_strength_score": self.get_authentication_strength_score(),
            "enabled_methods": [method.value for method in self.enabled_methods],
            "supported_providers": self.get_supported_providers(),
            "password_policy": self.password_policy.get_config(),
            "multi_factor_auth": self.mfa_config.get_config(),
            "biometric_auth": self.biometric_config.get_config(),
            "oauth": self.oauth_config.get_config(),
            "session_management": self.session_config.get_config(),
            "risk_based_auth": self.risk_auth_config.get_config(),
            "global_settings": {
                "password_less_enabled": self.password_less_enabled,
                "adaptive_authentication": self.adaptive_authentication,
                "zero_trust_verification": self.zero_trust_verification
            },
            "account_security": {
                "account_lockout_enabled": self.account_lockout_enabled,
                "max_failed_attempts": self.max_failed_attempts,
                "lockout_duration_minutes": self.lockout_duration_minutes,
                "progressive_lockout": self.progressive_lockout
            },
            "compliance": {
                "gdpr_compliant": self.gdpr_compliant,
                "privacy_by_design": self.privacy_by_design,
                "data_minimization": self.data_minimization
            }
        }

# Global authentication configuration instance
authentication_config = AuthenticationConfiguration()

# Export main classes
__all__ = [
    "AuthenticationConfiguration",
    "AuthenticationMethod",
    "IdentityProvider",
    "BiometricType",
    "PasswordPolicyConfig",
    "MultiFactorAuthConfig",
    "BiometricAuthConfig",
    "OAuthConfig",
    "SessionManagementConfig",
    "RiskBasedAuthConfig",
    "authentication_config"
]
