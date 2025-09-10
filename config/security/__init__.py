"""Ainflue Security Configuration
===============================

Security configurations for content protection, copyright enforcement,
rights management, violation detection, encryption, and authentication.

Enterprise security configuration management for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# Security system imports
from .protection_business_config import ProtectionBusinessConfiguration
from .copyright_fingerprinting_config import CopyrightFingerprintingConfiguration
from .rights_management_config import RightsManagementConfiguration
from .violation_detection_config import ViolationDetectionConfiguration

logger = logging.getLogger(__name__)

class SecurityConfigurationLevel(str, Enum):
    """Security configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class SecurityConfigurationManager:
    """Security configuration manager"""
    
    def __init__(self, level: SecurityConfigurationLevel = SecurityConfigurationLevel.ENTERPRISE):
        self.level = level
        self.configurations = {}
        self._initialize_security_configs()
    
    def _initialize_security_configs(self):
        """Initialize all security configurations"""
        self.configurations = {
            "protection": ProtectionBusinessConfiguration(level=self.level),
            "copyright": CopyrightFingerprintingConfiguration(level=self.level),
            "rights_management": RightsManagementConfiguration(level=self.level),
            "violation_detection": ViolationDetectionConfiguration(level=self.level)
        }
        
        logger.info(f"🔒 Security configurations initialized - Level: {self.level.value}")
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """Get specific security configuration"""
        return self.configurations.get(config_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all security configurations"""
        return self.configurations.copy()
    
    def get_protection_config(self) -> Optional[Any]:
        """Get content protection configuration"""
        return self.get_config("protection")
    
    def get_copyright_config(self) -> Optional[Any]:
        """Get copyright fingerprinting configuration"""
        return self.get_config("copyright")
    
    def get_rights_config(self) -> Optional[Any]:
        """Get rights management configuration"""
        return self.get_config("rights_management")
    
    def get_violation_config(self) -> Optional[Any]:
        """Get violation detection configuration"""
        return self.get_config("violation_detection")
    
    def validate_security_compliance(self) -> Dict[str, Any]:
        """Validate security compliance across all configurations"""
        compliance_status = {
            "overall_compliance": True,
            "security_levels": {},
            "missing_configurations": [],
            "compliance_warnings": []
        }
        
        required_configs = ["protection", "copyright", "rights_management", "violation_detection"]
        
        for config_name in required_configs:
            if config_name in self.configurations:
                compliance_status["security_levels"][config_name] = "COMPLIANT"
            else:
                compliance_status["missing_configurations"].append(config_name)
                compliance_status["overall_compliance"] = False
        
        if not compliance_status["overall_compliance"]:
            compliance_status["compliance_warnings"].append(
                "Missing critical security configurations"
            )
        
        return compliance_status

# Global security configuration manager
security_config_manager = SecurityConfigurationManager()

# Module exports
__all__ = [
    "ProtectionBusinessConfiguration",
    "CopyrightFingerprintingConfiguration",
    "RightsManagementConfiguration",
    "ViolationDetectionConfiguration",
    "SecurityConfigurationManager",
    "SecurityConfigurationLevel",
    "security_config_manager"
]

logger.info("🔒 Ainflue Security Configuration Module loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
