"""
Testing Module - Ainflue Integrations
====================================
Enterprise-grade testing providing comprehensive integration testing,
automated validation, security testing, performance benchmarking,
and quality assurance across 65+ platform integrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all testing components
from .validate_integrations import *
from .integration_tests_core import *
from .api_tests import *
from .performance_tests import *
from .security_tests import *

# Re-export for convenience
from . import (
    validate_integrations,
    integration_tests_core,
    api_tests,
    performance_tests,
    security_tests
)

# Exports publics
__all__ = [
    'ValidationManager',
    'IntegrationTestsCore',
    'APITests',
    'PerformanceTests',
    'SecurityTests',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise testing infrastructure for multi-platform content distribution validation"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'testing_features': [
        'comprehensive_validation',
        'automated_integration_testing',
        'security_penetration_testing',
        'performance_benchmarking',
        'quality_assurance_automation'
    ]
}