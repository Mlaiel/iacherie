"""Production Security Configuration
==================================

Production-ready security configuration integrating all security components
for the Ainflue platform. This module orchestrates WAF, rate limiting, 
DDoS protection, vulnerability scanning, SIEM, 2FA, audit trail, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import Field


class SecurityEnvironment(Enum):
    """Security environment levels"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"


@dataclass
class CloudFlareConfig:
    """CloudFlare DDoS protection configuration"""
    enabled: bool = True
    api_token: str = field(default_factory=lambda: os.getenv("CLOUDFLARE_API_TOKEN", ""))
    zone_id: str = field(default_factory=lambda: os.getenv("CLOUDFLARE_ZONE_ID", ""))
    email: str = field(default_factory=lambda: os.getenv("CLOUDFLARE_EMAIL", ""))
    api_key: str = field(default_factory=lambda: os.getenv("CLOUDFLARE_API_KEY", ""))
    
    # DDoS protection settings
    ddos_protection_level: str = "high"  # low, medium, high, essentially_off
    security_level: str = "high"  # essentially_off, low, medium, high, under_attack
    challenge_ttl: int = 1800  # Challenge TTL in seconds
    
    # Rate limiting rules
    rate_limiting_enabled: bool = True
    requests_per_minute: int = 1000
    burst_size: int = 100


@dataclass  
class VulnerabilityScanConfig:
    """Vulnerability scanning automation configuration"""
    enabled: bool = True
    scanner_type: str = "trivy"  # trivy, clair, snyk
    scan_schedule: str = "0 2 * * *"  # Daily at 2 AM UTC
    critical_threshold: int = 0  # Max critical vulnerabilities allowed
    high_threshold: int = 5  # Max high vulnerabilities allowed
    
    # Scan targets
    scan_images: List[str] = field(default_factory=lambda: [
        "ainflue/api:latest",
        "ainflue/worker:latest", 
        "ainflue/frontend:latest"
    ])
    
    # Notification settings
    notify_on_vulnerabilities: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["slack", "email"])


@dataclass
class SIEMConfig:
    """SIEM (Security Information and Event Management) configuration"""
    enabled: bool = True
    log_level: str = "INFO"
    retention_days: int = 365
    
    # Detection rules
    intrusion_detection: bool = True
    anomaly_detection: bool = True
    threat_intelligence: bool = True
    
    # Alert thresholds
    failed_login_threshold: int = 5
    suspicious_activity_threshold: int = 10
    data_exfiltration_threshold: int = 100  # MB
    
    # Integration
    elasticsearch_url: str = field(default_factory=lambda: os.getenv("ELASTICSEARCH_URL", ""))
    kibana_url: str = field(default_factory=lambda: os.getenv("KIBANA_URL", ""))


@dataclass
class TwoFactorAuthConfig:
    """2FA Configuration for admin accounts"""
    enabled: bool = True
    mandatory_for_admin: bool = True
    mandatory_for_privileged: bool = True
    
    # TOTP settings
    totp_window: int = 1  # Time window for TOTP validation
    backup_codes_count: int = 10
    
    # Enforcement
    grace_period_days: int = 7  # Days to enable 2FA before enforcement
    admin_roles: List[str] = field(default_factory=lambda: [
        "super_admin", "admin", "security_admin", "system_admin"
    ])


@dataclass
class AuditTrailConfig:
    """Complete audit trail configuration"""
    enabled: bool = True
    log_all_api_calls: bool = True
    log_data_access: bool = True
    log_admin_actions: bool = True
    log_user_authentication: bool = True
    
    # Retention and storage
    retention_years: int = 7  # Compliance requirement
    encrypt_logs: bool = True
    backup_logs: bool = True
    
    # Monitoring
    real_time_monitoring: bool = True
    suspicious_pattern_detection: bool = True


@dataclass
class APIKeyRotationConfig:
    """API key automatic rotation configuration"""
    enabled: bool = True
    rotation_interval_days: int = 90
    advance_notice_days: int = 7
    
    # Key types to rotate
    rotate_internal_keys: bool = True
    rotate_external_integrations: bool = True
    rotate_service_keys: bool = True
    
    # Notification
    notify_before_rotation: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])


@dataclass
class BackupConfig:
    """Encrypted backup with restoration tests"""
    enabled: bool = True
    encryption_enabled: bool = True
    
    # Schedule
    daily_backup: bool = True
    weekly_full_backup: bool = True
    monthly_archive: bool = True
    
    # Retention
    daily_retention_days: int = 30
    weekly_retention_weeks: int = 12
    monthly_retention_months: int = 12
    
    # Testing
    test_restoration_weekly: bool = True
    test_restoration_schedule: str = "0 3 * * 0"  # Sunday at 3 AM
    
    # Storage
    backup_location: str = field(default_factory=lambda: os.getenv("BACKUP_LOCATION", "s3://ainflue-backups"))
    encryption_key: str = field(default_factory=lambda: os.getenv("BACKUP_ENCRYPTION_KEY", ""))


class ProductionSecuritySettings(BaseSettings):
    """Production security settings"""
    
    # Environment
    environment: SecurityEnvironment = SecurityEnvironment.PRODUCTION
    debug: bool = False
    
    # Component configurations
    cloudflare: CloudFlareConfig = field(default_factory=CloudFlareConfig)
    vulnerability_scan: VulnerabilityScanConfig = field(default_factory=VulnerabilityScanConfig)
    siem: SIEMConfig = field(default_factory=SIEMConfig)
    two_factor_auth: TwoFactorAuthConfig = field(default_factory=TwoFactorAuthConfig)
    audit_trail: AuditTrailConfig = field(default_factory=AuditTrailConfig)
    api_key_rotation: APIKeyRotationConfig = field(default_factory=APIKeyRotationConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    
    # Security headers enforcement
    security_headers_enforced: bool = True
    
    # WAF and rate limiting
    waf_enabled: bool = True
    rate_limiting_enabled: bool = True
    ddos_protection_enabled: bool = True
    
    class Config:
        env_file = ".env.production"
        env_prefix = "SECURITY_"


# Global instance
production_security_settings = ProductionSecuritySettings()


def get_security_config() -> ProductionSecuritySettings:
    """Get production security configuration"""
    return production_security_settings


def validate_security_config() -> Dict[str, Any]:
    """Validate security configuration and return status"""
    config = get_security_config()
    status = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "components": {}
    }
    
    # Validate CloudFlare config
    if config.cloudflare.enabled:
        if not config.cloudflare.api_token and not config.cloudflare.api_key:
            status["errors"].append("CloudFlare API credentials not configured")
            status["valid"] = False
        status["components"]["cloudflare"] = "configured" if config.cloudflare.api_token else "missing_credentials"
    
    # Validate vulnerability scanning
    if config.vulnerability_scan.enabled:
        if not config.vulnerability_scan.scan_images:
            status["warnings"].append("No container images configured for vulnerability scanning")
        status["components"]["vulnerability_scan"] = "configured"
    
    # Validate SIEM
    if config.siem.enabled:
        if not config.siem.elasticsearch_url:
            status["warnings"].append("SIEM Elasticsearch URL not configured")
        status["components"]["siem"] = "configured"
    
    # Validate backup
    if config.backup.enabled:
        if not config.backup.backup_location:
            status["errors"].append("Backup location not configured")
            status["valid"] = False
        if config.backup.encryption_enabled and not config.backup.encryption_key:
            status["errors"].append("Backup encryption key not configured")
            status["valid"] = False
        status["components"]["backup"] = "configured" if config.backup.backup_location else "missing_location"
    
    return status


if __name__ == "__main__":
    # Test configuration
    config = get_security_config()
    print(f"Security Environment: {config.environment}")
    print(f"CloudFlare enabled: {config.cloudflare.enabled}")
    print(f"2FA mandatory for admin: {config.two_factor_auth.mandatory_for_admin}")
    
    # Validate
    validation = validate_security_config()
    print(f"Configuration valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")