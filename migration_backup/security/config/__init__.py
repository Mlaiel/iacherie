#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise Security Configuration Module
========================================

This module provides centralized access to all security configuration components
for the IA Chéries Creator Economy Platform. It exports configuration loaders,
validators, and management utilities for enterprise-grade security policies.

Core Features:
- Security Policies Management
- RBAC/ABAC Configuration
- Vault Integration
- Compliance Rules Engine
- WAF Configuration
- OAuth2 Enterprise Setup
- Threat Intelligence
- Creator Security Profiles
- Network Security Policies
- Zero Trust Architecture
- API Security Configuration
- Encryption Standards
- Incident Response
- Security Monitoring
- Backup Security
- Security Automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary Enterprise License
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configuration file paths
CONFIG_DIR = Path(__file__).parent

# Core security configuration files
SECURITY_POLICIES_FILE = CONFIG_DIR / "security_policies.yaml"
RBAC_POLICIES_FILE = CONFIG_DIR / "rbac-policies.yaml"
VAULT_CONFIG_FILE = CONFIG_DIR / "vault-config.hcl"
COMPLIANCE_RULES_FILE = CONFIG_DIR / "compliance_rules.yaml"
WAF_RULES_FILE = CONFIG_DIR / "waf-rules.yaml"
OAUTH2_CONFIG_FILE = CONFIG_DIR / "oauth2-config.yaml"
THREAT_INTELLIGENCE_FILE = CONFIG_DIR / "threat_intelligence.yaml"

# Extended security configuration files
NETWORK_SECURITY_FILE = CONFIG_DIR / "network_security_policies.yaml"
DATA_PROTECTION_FILE = CONFIG_DIR / "data_protection_config.yaml"
CREATOR_SECURITY_FILE = CONFIG_DIR / "creator_security_profiles.yaml"
API_SECURITY_FILE = CONFIG_DIR / "api_security_config.yaml"
ENCRYPTION_STANDARDS_FILE = CONFIG_DIR / "encryption_standards.yaml"
INCIDENT_RESPONSE_FILE = CONFIG_DIR / "incident_response_config.yaml"
MONITORING_SECURITY_FILE = CONFIG_DIR / "monitoring_security_config.yaml"
BACKUP_SECURITY_FILE = CONFIG_DIR / "backup_security_policies.yaml"
ZERO_TRUST_FILE = CONFIG_DIR / "zero_trust_architecture.yaml"
SECURITY_AUTOMATION_FILE = CONFIG_DIR / "security_automation_config.yaml"


class SecurityConfigurationManager:
    """
    Enterprise Security Configuration Manager
    
    Provides centralized access to all security configurations
    with validation, caching, and environment-specific overrides.
    """
    
    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._environment = os.getenv("ENVIRONMENT", "production")
    
    def load_yaml_config(self, file_path: Path) -> Dict[str, Any]:
        """Load and cache YAML configuration file."""
        cache_key = str(file_path)
        
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Security configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Apply environment-specific overrides
        config = self._apply_environment_overrides(config)
        
        self._config_cache[cache_key] = config
        return config
    
    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides."""
        if "environments" in config and self._environment in config["environments"]:
            env_config = config["environments"][self._environment]
            # Deep merge environment configuration
            return self._deep_merge(config, env_config)
        return config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_security_policies(self) -> Dict[str, Any]:
        """Get enterprise security policies configuration."""
        return self.load_yaml_config(SECURITY_POLICIES_FILE)
    
    def get_rbac_policies(self) -> Dict[str, Any]:
        """Get RBAC/ABAC policies configuration."""
        return self.load_yaml_config(RBAC_POLICIES_FILE)
    
    def get_compliance_rules(self) -> Dict[str, Any]:
        """Get compliance rules (GDPR/SOX/PCI) configuration."""
        return self.load_yaml_config(COMPLIANCE_RULES_FILE)
    
    def get_waf_rules(self) -> Dict[str, Any]:
        """Get WAF rules configuration."""
        return self.load_yaml_config(WAF_RULES_FILE)
    
    def get_oauth2_config(self) -> Dict[str, Any]:
        """Get OAuth2 enterprise configuration."""
        return self.load_yaml_config(OAUTH2_CONFIG_FILE)
    
    def get_threat_intelligence(self) -> Dict[str, Any]:
        """Get threat intelligence configuration."""
        return self.load_yaml_config(THREAT_INTELLIGENCE_FILE)
    
    def get_network_security_policies(self) -> Dict[str, Any]:
        """Get network security policies configuration."""
        return self.load_yaml_config(NETWORK_SECURITY_FILE)
    
    def get_data_protection_config(self) -> Dict[str, Any]:
        """Get data protection configuration."""
        return self.load_yaml_config(DATA_PROTECTION_FILE)
    
    def get_creator_security_profiles(self) -> Dict[str, Any]:
        """Get creator security profiles configuration."""
        return self.load_yaml_config(CREATOR_SECURITY_FILE)
    
    def get_api_security_config(self) -> Dict[str, Any]:
        """Get API security configuration."""
        return self.load_yaml_config(API_SECURITY_FILE)
    
    def get_encryption_standards(self) -> Dict[str, Any]:
        """Get encryption standards configuration."""
        return self.load_yaml_config(ENCRYPTION_STANDARDS_FILE)
    
    def get_incident_response_config(self) -> Dict[str, Any]:
        """Get incident response configuration."""
        return self.load_yaml_config(INCIDENT_RESPONSE_FILE)
    
    def get_monitoring_security_config(self) -> Dict[str, Any]:
        """Get security monitoring configuration."""
        return self.load_yaml_config(MONITORING_SECURITY_FILE)
    
    def get_backup_security_policies(self) -> Dict[str, Any]:
        """Get backup security policies configuration."""
        return self.load_yaml_config(BACKUP_SECURITY_FILE)
    
    def get_zero_trust_architecture(self) -> Dict[str, Any]:
        """Get zero trust architecture configuration."""
        return self.load_yaml_config(ZERO_TRUST_FILE)
    
    def get_security_automation_config(self) -> Dict[str, Any]:
        """Get security automation configuration."""
        return self.load_yaml_config(SECURITY_AUTOMATION_FILE)
    
    def validate_all_configurations(self) -> List[str]:
        """Validate all security configurations and return list of errors."""
        errors = []
        
        config_methods = [
            ("Security Policies", self.get_security_policies),
            ("RBAC Policies", self.get_rbac_policies),
            ("Compliance Rules", self.get_compliance_rules),
            ("WAF Rules", self.get_waf_rules),
            ("OAuth2 Config", self.get_oauth2_config),
            ("Threat Intelligence", self.get_threat_intelligence),
            ("Network Security", self.get_network_security_policies),
            ("Data Protection", self.get_data_protection_config),
            ("Creator Security", self.get_creator_security_profiles),
            ("API Security", self.get_api_security_config),
            ("Encryption Standards", self.get_encryption_standards),
            ("Incident Response", self.get_incident_response_config),
            ("Security Monitoring", self.get_monitoring_security_config),
            ("Backup Security", self.get_backup_security_policies),
            ("Zero Trust", self.get_zero_trust_architecture),
            ("Security Automation", self.get_security_automation_config),
        ]
        
        for config_name, method in config_methods:
            try:
                config = method()
                if not config:
                    errors.append(f"{config_name}: Configuration is empty")
            except FileNotFoundError as e:
                errors.append(f"{config_name}: {str(e)}")
            except yaml.YAMLError as e:
                errors.append(f"{config_name}: YAML parsing error - {str(e)}")
            except Exception as e:
                errors.append(f"{config_name}: Unexpected error - {str(e)}")
        
        return errors
    
    def get_all_configurations(self) -> Dict[str, Any]:
        """Get all security configurations in a single dictionary."""
        return {
            "security_policies": self.get_security_policies(),
            "rbac_policies": self.get_rbac_policies(),
            "compliance_rules": self.get_compliance_rules(),
            "waf_rules": self.get_waf_rules(),
            "oauth2_config": self.get_oauth2_config(),
            "threat_intelligence": self.get_threat_intelligence(),
            "network_security_policies": self.get_network_security_policies(),
            "data_protection_config": self.get_data_protection_config(),
            "creator_security_profiles": self.get_creator_security_profiles(),
            "api_security_config": self.get_api_security_config(),
            "encryption_standards": self.get_encryption_standards(),
            "incident_response_config": self.get_incident_response_config(),
            "monitoring_security_config": self.get_monitoring_security_config(),
            "backup_security_policies": self.get_backup_security_policies(),
            "zero_trust_architecture": self.get_zero_trust_architecture(),
            "security_automation_config": self.get_security_automation_config(),
        }


# Global configuration manager instance
security_config = SecurityConfigurationManager()

# Exported functions for convenience
get_security_policies = security_config.get_security_policies
get_rbac_policies = security_config.get_rbac_policies
get_compliance_rules = security_config.get_compliance_rules
get_waf_rules = security_config.get_waf_rules
get_oauth2_config = security_config.get_oauth2_config
get_threat_intelligence = security_config.get_threat_intelligence
get_network_security_policies = security_config.get_network_security_policies
get_data_protection_config = security_config.get_data_protection_config
get_creator_security_profiles = security_config.get_creator_security_profiles
get_api_security_config = security_config.get_api_security_config
get_encryption_standards = security_config.get_encryption_standards
get_incident_response_config = security_config.get_incident_response_config
get_monitoring_security_config = security_config.get_monitoring_security_config
get_backup_security_policies = security_config.get_backup_security_policies
get_zero_trust_architecture = security_config.get_zero_trust_architecture
get_security_automation_config = security_config.get_security_automation_config

validate_all_configurations = security_config.validate_all_configurations
get_all_configurations = security_config.get_all_configurations

# Version information
__version__ = "4.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary Enterprise License"

# Module exports
__all__ = [
    "SecurityConfigurationManager",
    "security_config",
    "get_security_policies",
    "get_rbac_policies", 
    "get_compliance_rules",
    "get_waf_rules",
    "get_oauth2_config",
    "get_threat_intelligence",
    "get_network_security_policies",
    "get_data_protection_config",
    "get_creator_security_profiles",
    "get_api_security_config",
    "get_encryption_standards",
    "get_incident_response_config",
    "get_monitoring_security_config",
    "get_backup_security_policies",
    "get_zero_trust_architecture",
    "get_security_automation_config",
    "validate_all_configurations",
    "get_all_configurations",
]