"""
Monitoring Alerting Module
=========================

Central alerting system for the Ainflue monitoring platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export main components
try:
    from .intelligent_alert_manager import IntelligentAlertManager
    from .technical_alerts import TechnicalAlertsSystem
    
    __all__ = [
        'IntelligentAlertManager',
        'TechnicalAlertsSystem'
    ]
except ImportError as e:
    # Graceful degradation if imports fail
    __all__ = []