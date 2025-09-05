"""Environments Configuration Module - Multi-Cloud Environment Management
=====================================================================

Enterprise-grade multi-cloud environment configuration system for the 
IA-Influencer Agent Platform with support for development, staging, 
production, and specialized environments across AWS, Azure, and GCP.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, Any, Optional, List
import os

# Import environment configuration modules
try:
    from . import development
    DEVELOPMENT_AVAILABLE = True
except ImportError:
    DEVELOPMENT_AVAILABLE = False

try:
    from . import staging
    STAGING_AVAILABLE = True
except ImportError:
    STAGING_AVAILABLE = False

try:
    from . import production
    PRODUCTION_AVAILABLE = True
except ImportError:
    PRODUCTION_AVAILABLE = False

try:
    from . import testing
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False

try:
    from . import cloud_providers
    CLOUD_PROVIDERS_AVAILABLE = True
except ImportError:
    CLOUD_PROVIDERS_AVAILABLE = False

try:
    from . import regional_config
    REGIONAL_CONFIG_AVAILABLE = True
except ImportError:
    REGIONAL_CONFIG_AVAILABLE = False

try:
    from . import disaster_recovery
    DISASTER_RECOVERY_AVAILABLE = True
except ImportError:
    DISASTER_RECOVERY_AVAILABLE = False

try:
    from . import performance_profiles
    PERFORMANCE_PROFILES_AVAILABLE = True
except ImportError:
    PERFORMANCE_PROFILES_AVAILABLE = False

try:
    from . import compliance_environments
    COMPLIANCE_ENVIRONMENTS_AVAILABLE = True
except ImportError:
    COMPLIANCE_ENVIRONMENTS_AVAILABLE = False

try:
    from . import cost_optimization
    COST_OPTIMIZATION_AVAILABLE = True
except ImportError:
    COST_OPTIMIZATION_AVAILABLE = False

try:
    from . import environment_validator
    ENVIRONMENT_VALIDATOR_AVAILABLE = True
except ImportError:
    ENVIRONMENT_VALIDATOR_AVAILABLE = False

# Environment configuration manager
class EnvironmentManager:
    """Central environment configuration manager for multi-cloud deployments"""
    
    def __init__(self):
        self.current_environment = os.getenv('ENVIRONMENT', 'development')
        self.cloud_provider = os.getenv('CLOUD_PROVIDER', 'aws')
        self.region = os.getenv('REGION', 'eu-central-1')
        
    def get_environment_config(self, environment: str = None) -> Dict[str, Any]:
        """Get configuration for specified environment"""
        env = environment or self.current_environment
        
        if env == 'development' and DEVELOPMENT_AVAILABLE:
            return development.get_config()
        elif env == 'staging' and STAGING_AVAILABLE:
            return staging.get_config()
        elif env == 'production' and PRODUCTION_AVAILABLE:
            return production.get_config()
        elif env == 'testing' and TESTING_AVAILABLE:
            return testing.get_config()
        else:
            return self._get_default_config()
    
    def get_cloud_config(self, provider: str = None) -> Dict[str, Any]:
        """Get cloud provider configuration"""
        if CLOUD_PROVIDERS_AVAILABLE:
            return cloud_providers.get_config(provider or self.cloud_provider)
        return {}
    
    def get_regional_config(self, region: str = None) -> Dict[str, Any]:
        """Get regional configuration"""
        if REGIONAL_CONFIG_AVAILABLE:
            return regional_config.get_config(region or self.region)
        return {}
    
    def validate_environment(self) -> bool:
        """Validate current environment configuration"""
        if ENVIRONMENT_VALIDATOR_AVAILABLE:
            return environment_validator.validate(self.current_environment)
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when specific environment is unavailable"""
        return {
            'environment': self.current_environment,
            'cloud_provider': self.cloud_provider,
            'region': self.region,
            'debug': self.current_environment in ['development', 'testing'],
            'log_level': 'DEBUG' if self.current_environment in ['development', 'testing'] else 'INFO'
        }

# Global environment manager instance
environment_manager = EnvironmentManager()

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Export available modules
available_modules = []
if DEVELOPMENT_AVAILABLE:
    available_modules.append("development")
if STAGING_AVAILABLE:
    available_modules.append("staging")
if PRODUCTION_AVAILABLE:
    available_modules.append("production")
if TESTING_AVAILABLE:
    available_modules.append("testing")
if CLOUD_PROVIDERS_AVAILABLE:
    available_modules.append("cloud_providers")
if REGIONAL_CONFIG_AVAILABLE:
    available_modules.append("regional_config")
if DISASTER_RECOVERY_AVAILABLE:
    available_modules.append("disaster_recovery")
if PERFORMANCE_PROFILES_AVAILABLE:
    available_modules.append("performance_profiles")
if COMPLIANCE_ENVIRONMENTS_AVAILABLE:
    available_modules.append("compliance_environments")
if COST_OPTIMIZATION_AVAILABLE:
    available_modules.append("cost_optimization")
if ENVIRONMENT_VALIDATOR_AVAILABLE:
    available_modules.append("environment_validator")

__all__ = ['environment_manager', 'EnvironmentManager'] + available_modules