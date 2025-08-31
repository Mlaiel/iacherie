"""Authentication & Authorization Database Module

Enterprise-grade authentication and authorization database components for multi-format creators
(musicians, bloggers, photographers, influencers, comedians) with advanced security features.

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
"""

from .session_manager import SessionManager, SessionStore, UserSession
from .token_repository import TokenRepository, RefreshTokenStore, TokenManager
from .permission_manager import PermissionManager, RoleManager, AccessControl
from .multi_factor_auth import MultiFactorAuth, MFAProvider, TwoFactorSetup
from .oauth_providers import OAuthProviderManager, ExternalProvider, OAuthCredentials
from .user_credentials import UserCredentialManager, PasswordPolicy, LoginAttempts
from .biometric_auth import BiometricAuthManager, BiometricTemplate, BiometricVerification
from .device_registry import DeviceRegistry, TrustedDevice, DeviceFingerprint
from .authentication_logs import AuthenticationLogger, SecurityAudit, ActivityTracker
from .compliance_manager import ComplianceManager, GDPRCompliance, SOCCompliance

__all__ = [
    # Session Management
    "SessionManager",
    "SessionStore", 
    "UserSession",
    
    # Token Management
    "TokenRepository",
    "RefreshTokenStore",
    "TokenManager",
    
    # Permission & Access Control
    "PermissionManager",
    "RoleManager",
    "AccessControl",
    
    # Multi-Factor Authentication
    "MultiFactorAuth",
    "MFAProvider",
    "TwoFactorSetup",
    
    # OAuth Integration
    "OAuthProviderManager",
    "ExternalProvider",
    "OAuthCredentials",
    
    # User Credentials
    "UserCredentialManager",
    "PasswordPolicy",
    "LoginAttempts",
    
    # Biometric Authentication
    "BiometricAuthManager",
    "BiometricTemplate",
    "BiometricVerification",
    
    # Device Management
    "DeviceRegistry",
    "TrustedDevice",
    "DeviceFingerprint",
    
    # Audit & Logging
    "AuthenticationLogger",
    "SecurityAudit", 
    "ActivityTracker",
    
    # Compliance
    "ComplianceManager",
    "GDPRCompliance",
    "SOCCompliance"
]
