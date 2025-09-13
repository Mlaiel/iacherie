"""
Error Handling Module - Ainflue Integrations
===========================================
Enterprise-grade error handling providing intelligent error recovery,
automated logging, escalation management, and exception orchestration
across 65+ platform integrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all error handling components
from .error_handler import *

# Re-export for convenience
from . import error_handler

# Exports publics
__all__ = [
    'ErrorHandler',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise error handling infrastructure for multi-platform content distribution"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'error_features': [
        'intelligent_recovery',
        'automated_logging',
        'escalation_management',
        'exception_orchestration',
        'failure_analysis'
    ]
}