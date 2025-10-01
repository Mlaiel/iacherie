"""
Testing Module - IA Chéries Integrations
====================================
Enterprise testing module providing comprehensive integration testing,
validation, security testing, and quality assurance.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

# Testing Core Components
from .validate_integrations import ValidationManager

# Integration testing components (decomposed from integration_tests.py)
from .integration_tests_core import IntegrationTestsCore
from .api_tests import APITests
from .performance_tests import PerformanceTests
from .security_tests import SecurityTests

# Public exports
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
__description__ = "Enterprise testing and validation for IA Chéries platform"

# Configuration logique métier IA Chéries
IA CHÉRIES_TESTING = {
    'platforms': 65,
    'testing_features': ['integration_testing', 'security_testing', 'performance_testing', 'validation'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}