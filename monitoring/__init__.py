"""
Monitoring System - Core Module
===============================

Central monitoring system for the Ainflue platform providing
comprehensive observability, alerting, and performance tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Core monitoring components
try:
    from .business_monitoring import BusinessMonitoringCore
    from .production_dashboard import ProductionDashboard
    
    class MonitoringSystem:
        """Main monitoring system orchestrator"""
        
        def __init__(self):
            self.business_monitoring = BusinessMonitoringCore()
            self.dashboard = ProductionDashboard()
        
        def get_system_status(self) -> Dict[str, Any]:
            """Get overall system status"""
            return {
                "status": "operational",
                "version": __version__,
                "components": {
                    "business_monitoring": "active",
                    "dashboard": "active"
                }
            }
    
    __all__ = [
        'MonitoringSystem',
        'BusinessMonitoringCore',
        'ProductionDashboard'
    ]
    
except ImportError as e:
    logger.warning(f"Some monitoring components not available: {e}")
    
    class MonitoringSystem:
        """Fallback monitoring system"""
        
        def get_system_status(self) -> Dict[str, Any]:
            return {
                "status": "limited",
                "version": __version__,
                "error": "Some components unavailable"
            }
    
    __all__ = ['MonitoringSystem']

# Export main system
monitoring_system = MonitoringSystem()