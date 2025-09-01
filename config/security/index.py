"""Security Configuration Index Module
===================================

Central index for all security configurations in the IA Influencer Agent platform.
Provides easy access to all security modules and their configurations.

This module serves as the main entry point for security configuration management,
offering a unified interface to access authentication, authorization, content protection,
revenue security, and platform integration security settings.

Business Logic Integration:
- Centralized security configuration management
- Easy access to all security modules
- Configuration validation and initialization
- Security policy enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Engineers

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .authentication import AuthenticationConfig, get_authentication_config
from .authorization import AuthorizationConfig, get_authorization_config
from .encryption import EncryptionConfig, get_encryption_config
from .content_validation import ContentValidationConfig, get_content_validation_config
from .rate_limiting import RateLimitingConfig, get_rate_limiting_config
from .audit_logging import AuditLoggingConfig, get_audit_logging_config
from .compliance import ComplianceConfig, get_compliance_config
from .threat_detection import ThreatDetectionConfig, get_threat_detection_config
from .api_security import ApiSecurityConfig, get_api_security_config
from .content_protection import ContentProtectionConfig, get_content_protection_config
from .revenue_security import RevenueSecurityConfig, get_revenue_security_config
from .platform_integration import PlatformIntegrationSecurityConfig, get_platform_integration_security_config


class SecurityProfile(Enum):
    """
Security profile presets for different deployment scenarios."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_SECURITY = "high_security"
    ENTERPRISE = "enterprise"


class CreatorTier(Enum):
    """Creator subscription tiers affecting security configurations."""

    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class SecurityConfigurationManager:
    """Central security configuration manager."""
    
    # Core security configurations
    authentication: AuthenticationConfig = field(default_factory=get_authentication_config)
    authorization: AuthorizationConfig = field(default_factory=get_authorization_config)
    encryption: EncryptionConfig = field(default_factory=get_encryption_config)
    content_validation: ContentValidationConfig = field(default_factory=get_content_validation_config)
    rate_limiting: RateLimitingConfig = field(default_factory=get_rate_limiting_config)
    audit_logging: AuditLoggingConfig = field(default_factory=get_audit_logging_config)
    compliance: ComplianceConfig = field(default_factory=get_compliance_config)
    threat_detection: ThreatDetectionConfig = field(default_factory=get_threat_detection_config)
    api_security: ApiSecurityConfig = field(default_factory=get_api_security_config)
    
    # Advanced security configurations
    content_protection: ContentProtectionConfig = field(default_factory=get_content_protection_config)
    revenue_security: RevenueSecurityConfig = field(default_factory=get_revenue_security_config)
    platform_integration: PlatformIntegrationSecurityConfig = field(default_factory=get_platform_integration_security_config)
    
    # Global security settings
    security_profile: SecurityProfile = SecurityProfile.PRODUCTION
    debug_mode: bool = False
    strict_mode: bool = True
    
    def get_config_by_name(self, config_name: str) -> Optional[Any]:
        """
Get configuration by name."""
        config_mapping = {
            "authentication": self.authentication,
            "authorization": self.authorization,
            "encryption": self.encryption,
            "content_validation": self.content_validation,
            "rate_limiting": self.rate_limiting,
            "audit_logging": self.audit_logging,
            "compliance": self.compliance,
            "threat_detection": self.threat_detection,
            "api_security": self.api_security,
            "content_protection": self.content_protection,
            "revenue_security": self.revenue_security,
            "platform_integration": self.platform_integration
        }
        return config_mapping.get(config_name)
    
    def apply_security_profile(self, profile: SecurityProfile) -> None:
        """Apply security profile configurations."""
        profile_configs = self._get_profile_configurations(profile)
        
        for config_name, overrides in profile_configs.items():
            config = self.get_config_by_name(config_name)
            if config:
                self._apply_config_overrides(config, overrides)
    
    def apply_creator_tier_config(self, tier: CreatorTier) -> None:
        """
Apply creator tier-specific security configurations."""
        tier_configs = self._get_tier_configurations(tier)
        
        for config_name, overrides in tier_configs.items():
            config = self.get_config_by_name(config_name)
            if config:
                self._apply_config_overrides(config, overrides)
    
    def validate_all_configurations(self) -> Dict[str, bool]:
        """
Validate all security configurations."""
        validation_results = {}
        
        # Import validation functions
        from .authentication import validate_authentication_config
        from .authorization import validate_authorization_config
        from .encryption import validate_encryption_config
        from .content_validation import validate_content_validation_config
        from .rate_limiting import validate_rate_limiting_config
        from .audit_logging import validate_audit_logging_config
        from .compliance import validate_compliance_config
        from .threat_detection import validate_threat_detection_config
        from .api_security import validate_api_security_config
        from .content_protection import validate_content_protection_config
        from .revenue_security import validate_revenue_security_config
        from .platform_integration import validate_platform_integration_config
        
        # Validate each configuration
        validation_functions = {
            "authentication": validate_authentication_config,
            "authorization": validate_authorization_config,
            "encryption": validate_encryption_config,
            "content_validation": validate_content_validation_config,
            "rate_limiting": validate_rate_limiting_config,
            "audit_logging": validate_audit_logging_config,
            "compliance": validate_compliance_config,
            "threat_detection": validate_threat_detection_config,
            "api_security": validate_api_security_config,
            "content_protection": validate_content_protection_config,
            "revenue_security": validate_revenue_security_config,
            "platform_integration": validate_platform_integration_config
        }
        
        for config_name, validate_func in validation_functions.items():
            try:
                config = self.get_config_by_name(config_name)
                validation_results[config_name] = validate_func(config)
            except Exception as e:
                validation_results[config_name] = False
                if self.debug_mode:
                    print(f"Validation failed for {config_name}: {e}")
        
        return validation_results
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get a summary of current security configuration."""
        return {
            "profile": self.security_profile.value,
            "strict_mode": self.strict_mode,
            "debug_mode": self.debug_mode,
            "configurations": {
                "authentication": {
                    "method": self.authentication.default_method.value,
                    "mfa_enabled": self.authentication.mfa.enabled,
                    "jwt_enabled": bool(self.authentication.jwt.secret_key)
                },
                "content_protection": {
                    "protection_level": self.content_protection.protection_level.value,
                    "auto_protection": self.content_protection.auto_protection_enabled,
                    "monitoring": self.content_protection.monitoring.real_time_monitoring
                },
                "revenue_security": {
                    "fraud_detection": self.revenue_security.fraud_detection.ml_fraud_detection,
                    "pci_compliance": self.revenue_security.payment_security.pci_compliance_level,
                    "automated_payouts": True
                },
                "platform_integration": {
                    "security_level": self.platform_integration.security_level.value,
                    "enabled_platforms": len(self.platform_integration.enabled_platforms),
                    "rate_limiting": self.platform_integration.rate_limiting.enforcement_enabled
                }
            }
        }
    
    def _get_profile_configurations(self, profile: SecurityProfile) -> Dict[str, Dict[str, Any]]:
        """Get configuration overrides for security profiles."""
        profile_configs = {
            SecurityProfile.DEVELOPMENT: {
                "authentication": {
                    "jwt.access_token_expire_minutes": 60,
                    "mfa.enabled": False,
                    "session.secure_cookies": False
                },
                "encryption": {
                    "key_rotation_days": 30,
                    "hardware_security_module": False
                },
                "audit_logging": {
                    "log_level": "DEBUG",
                    "detailed_logging": True
                }
            },
            SecurityProfile.STAGING: {
                "authentication": {
                    "jwt.access_token_expire_minutes": 45,
                    "mfa.enabled": True,
                    "session.secure_cookies": True
                },
                "threat_detection": {
                    "real_time_detection": True,
                    "automated_response": False
                }
            },
            SecurityProfile.PRODUCTION: {
                "authentication": {
                    "jwt.access_token_expire_minutes": 30,
                    "mfa.enabled": True,
                    "brute_force_protection": True
                },
                "encryption": {
                    "hardware_security_module": True,
                    "key_escrow_enabled": True
                },
                "threat_detection": {
                    "real_time_detection": True,
                    "automated_response": True
                }
            },
            SecurityProfile.HIGH_SECURITY: {
                "authentication": {
                    "jwt.access_token_expire_minutes": 15,
                    "mfa.required_for_creators": True,
                    "creator_verification_required": True
                },
                "content_protection": {
                    "protection_level": "enterprise",
                    "encryption.hardware_security_module": True
                },
                "audit_logging": {
                    "immutable_logs": True,
                    "blockchain_verification": True
                }
            },
            SecurityProfile.ENTERPRISE: {
                "authentication": {
                    "jwt.access_token_expire_minutes": 15,
                    "creator_document_verification": True
                },
                "content_protection": {
                    "protection_level": "ultra_secure",
                    "compliance.legal_hold_support": True
                },
                "revenue_security": {
                    "audit.third_party_audits": True,
                    "compliance.sox_compliance": True
                }
            }
        }
        
        return profile_configs.get(profile, {})
    
    def _get_tier_configurations(self, tier: CreatorTier) -> Dict[str, Dict[str, Any]]:
        """Get configuration overrides for creator tiers."""
        tier_configs = {
            CreatorTier.FREE: {
                "rate_limiting": {
                    "requests_per_minute": 50,
                    "requests_per_hour": 1000
                },
                "content_protection": {
                    "fingerprint.max_concurrent_jobs": 2,
                    "monitoring.monitoring_interval_minutes": 60
                },
                "revenue_security": {
                    "payment_security.daily_limit_eur": 1000,
                    "payout.minimum_payout_amount": 50
                }
            },
            CreatorTier.PROFESSIONAL: {
                "rate_limiting": {
                    "requests_per_minute": 150,
                    "requests_per_hour": 5000
                },
                "content_protection": {
                    "fingerprint.max_concurrent_jobs": 5,
                    "monitoring.monitoring_interval_minutes": 15
                },
                "revenue_security": {
                    "payment_security.daily_limit_eur": 10000,
                    "payout.minimum_payout_amount": 25
                }
            },
            CreatorTier.ENTERPRISE: {
                "rate_limiting": {
                    "requests_per_minute": 500,
                    "requests_per_hour": 20000
                },
                "content_protection": {
                    "fingerprint.max_concurrent_jobs": 10,
                    "monitoring.monitoring_interval_minutes": 5,
                    "protection_level": "enterprise"
                },
                "revenue_security": {
                    "payment_security.daily_limit_eur": 50000,
                    "payout.minimum_payout_amount": 10,
                    "audit.third_party_audits": True
                }
            }
        }
        
        return tier_configs.get(tier, {})
    
    def _apply_config_overrides(self, config: Any, overrides: Dict[str, Any]) -> None:
        """Apply configuration overrides to a config object."""
        for key, value in overrides.items():
            if "." in key:
                # Handle nested attributes
                parts = key.split(".")
                obj = config
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                # Handle direct attributes
                setattr(config, key, value)


# Global security configuration manager instance
security_manager = SecurityConfigurationManager()


def get_security_manager() -> SecurityConfigurationManager:
    """Get the global security configuration manager instance."""
    return security_manager


def initialize_security_config(
    profile: SecurityProfile = SecurityProfile.PRODUCTION,
    creator_tier: Optional[CreatorTier] = None,
    custom_overrides: Optional[Dict[str, Any]] = None
) -> SecurityConfigurationManager:
    """
Initialize security configuration with profile and tier settings."""
    manager = get_security_manager()
    
    # Apply security profile
    manager.apply_security_profile(profile)
    
    # Apply creator tier configuration if specified
    if creator_tier:
        manager.apply_creator_tier_config(creator_tier)
    
    # Apply custom overrides if provided
    if custom_overrides:
        for config_name, overrides in custom_overrides.items():
            config = manager.get_config_by_name(config_name)
            if config:
                manager._apply_config_overrides(config, overrides)
    
    # Validate all configurations
    validation_results = manager.validate_all_configurations()
    
    # Check for validation failures
    failed_configs = [name for name, result in validation_results.items() if not result]
    if failed_configs and manager.strict_mode:
        raise ValueError(f"Security configuration validation failed for: {', '.join(failed_configs)}")
    
    return manager


def get_config_for_creator(creator_id: str, creator_tier: CreatorTier) -> SecurityConfigurationManager:
    """Get security configuration customized for a specific creator."""
    manager = SecurityConfigurationManager()
    manager.apply_creator_tier_config(creator_tier)
    
    # Add creator-specific customizations here if needed
    # For example, custom rate limits, protection levels, etc.
    
    return manager


# Export main configuration classes and functions
__all__ = [
    "SecurityConfigurationManager",
    "SecurityProfile", 
    "CreatorTier",
    "get_security_manager",
    "initialize_security_config",
    "get_config_for_creator"
]
