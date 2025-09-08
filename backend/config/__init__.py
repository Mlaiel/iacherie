"""Backend Configuration Module - Consolidated Configuration Management
=====================================================================

Consolidated configuration system for IA-Influencer Agent Platform.
This module consolidates all configuration modules from the main config/ directory
into 12 focused configuration files organized by domain.

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

# Import consolidated configuration modules
try:
    from . import database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

try:
    from . import cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from . import ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from . import security
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

try:
    from . import monetization
    MONETIZATION_AVAILABLE = True
except ImportError:
    MONETIZATION_AVAILABLE = False

try:
    from . import api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

try:
    from . import monitoring
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from . import storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False

try:
    from . import deployment
    DEPLOYMENT_AVAILABLE = True
except ImportError:
    DEPLOYMENT_AVAILABLE = False

try:
    from . import integrations
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False

try:
    from . import business
    BUSINESS_AVAILABLE = True
except ImportError:
    BUSINESS_AVAILABLE = False

try:
    from . import environment_manager
    ENVIRONMENT_MANAGER_AVAILABLE = True
except ImportError:
    ENVIRONMENT_MANAGER_AVAILABLE = False

try:
    from . import configuration_orchestrator
    CONFIGURATION_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    CONFIGURATION_ORCHESTRATOR_AVAILABLE = False

try:
    from . import secrets_manager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

try:
    from . import feature_flags
    FEATURE_FLAGS_AVAILABLE = True
except ImportError:
    FEATURE_FLAGS_AVAILABLE = False

try:
    from . import performance_tuning
    PERFORMANCE_TUNING_AVAILABLE = True
except ImportError:
    PERFORMANCE_TUNING_AVAILABLE = False

try:
    from . import compliance_config
    COMPLIANCE_CONFIG_AVAILABLE = True
except ImportError:
    COMPLIANCE_CONFIG_AVAILABLE = False

try:
    from . import microservices_config
    MICROSERVICES_CONFIG_AVAILABLE = True
except ImportError:
    MICROSERVICES_CONFIG_AVAILABLE = False

try:
    from . import ml_pipeline_config
    ML_PIPELINE_CONFIG_AVAILABLE = True
except ImportError:
    ML_PIPELINE_CONFIG_AVAILABLE = False

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Export available modules
available_modules = []
if DATABASE_AVAILABLE:
    available_modules.append("database")
if CACHE_AVAILABLE:
    available_modules.append("cache")
if AI_AVAILABLE:
    available_modules.append("ai")
if SECURITY_AVAILABLE:
    available_modules.append("security")
if MONETIZATION_AVAILABLE:
    available_modules.append("monetization")
if API_AVAILABLE:
    available_modules.append("api")
if MONITORING_AVAILABLE:
    available_modules.append("monitoring")
if STORAGE_AVAILABLE:
    available_modules.append("storage")
if DEPLOYMENT_AVAILABLE:
    available_modules.append("deployment")
if INTEGRATIONS_AVAILABLE:
    available_modules.append("integrations")
if BUSINESS_AVAILABLE:
    available_modules.append("business")
if ENVIRONMENT_MANAGER_AVAILABLE:
    available_modules.append("environment_manager")
if CONFIGURATION_ORCHESTRATOR_AVAILABLE:
    available_modules.append("configuration_orchestrator")
if SECRETS_MANAGER_AVAILABLE:
    available_modules.append("secrets_manager")
if FEATURE_FLAGS_AVAILABLE:
    available_modules.append("feature_flags")
if PERFORMANCE_TUNING_AVAILABLE:
    available_modules.append("performance_tuning")
if COMPLIANCE_CONFIG_AVAILABLE:
    available_modules.append("compliance_config")
if MICROSERVICES_CONFIG_AVAILABLE:
    available_modules.append("microservices_config")
if ML_PIPELINE_CONFIG_AVAILABLE:
    available_modules.append("ml_pipeline_config")

__all__ = available_modules