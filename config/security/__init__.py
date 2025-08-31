"""Security Configuration Module for IA Influencer Agent Platform
=============================================================

Advanced enterprise-grade security configuration module for the IA Influencer Agent platform.
Provides comprehensive security settings, authentication, authorization, encryption, 
content protection, and compliance configurations.

This module integrates with the core business logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → SEO pro → Matching collaboration → Multi-platform distribution

Created by: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer
- DBA + Security + Microservices + Audio
- DevOps + IA Prompt Engineer

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from .authentication import *
from .authorization import *
from .encryption import *
from .content_validation import *
from .rate_limiting import *
from .audit_logging import *
from .compliance import *
from .threat_detection import *
from .api_security import *
from .content_protection import *
from .revenue_security import *
from .platform_integration import *
# from .validation import SecurityConfigurationValidator, run_security_validation, quick_security_check

# Import new advanced cybersecurity module
from .advanced_cybersecurity_config import (
    AdvancedCybersecurityConfig,
    advanced_cybersecurity_config,
    ThreatLevel,
    AttackType,
    SecurityAction,
    ThreatDetectionRule,
    SecurityMonitoringConfig,
    IncidentResponseConfig,
    get_threat_detection_rule,
    assess_threat_level,
    get_security_actions
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "AuthenticationConfig",
    "AuthorizationConfig", 
    "EncryptionConfig",
    "ContentValidationConfig",
    "RateLimitingConfig",
    "AuditLoggingConfig",
    "ComplianceConfig",
    "ThreatDetectionConfig",
    "ApiSecurityConfig",
    "ContentProtectionConfig",
    "RevenueSecurityConfig",
    "PlatformIntegrationSecurityConfig",
    "SecurityConfigurationValidator",
    "run_security_validation",
    "quick_security_check",
]
