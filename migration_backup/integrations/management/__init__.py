"""
Management Module - Ainflue Integrations
=======================================
Enterprise management module providing integration orchestration,
configuration management, and administrative functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Management Core Components
from .integration_manager import IntegrationManager
from .configuration_manager import ConfigurationManager

# Public exports
__all__ = [
    'IntegrationManager',
    'ConfigurationManager',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise management and orchestration for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_MANAGEMENT = {
    'platforms': 65,
    'management_features': ['integration_orchestration', 'configuration_management', 'lifecycle_management'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}