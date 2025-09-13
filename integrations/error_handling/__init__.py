"""
Error Handling Module - Ainflue Integrations
===========================================
Enterprise error handling module providing comprehensive error management,
logging, recovery automation, and exception handling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Error Handling Core Components
from .error_handler import ErrorHandler

# Public exports
__all__ = [
    'ErrorHandler',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise error handling and recovery for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_ERROR_HANDLING = {
    'platforms': 65,
    'error_features': ['intelligent_recovery', 'automated_logging', 'escalation_management'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}