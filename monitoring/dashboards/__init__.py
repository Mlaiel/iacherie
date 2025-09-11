"""
Ainflue Platform - Enterprise Dashboard Module
==============================================

Import and expose the enterprise dashboard system for monitoring
all aspects of the Ainflue platform with real-time visualizations
and business intelligence capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .enterprise_dashboard_system import (
    EnterpriseDashboardSystem,
    Dashboard,
    DashboardWidget,
    DashboardMetrics,
    DashboardType,
    VisualizationType,
    UpdateFrequency,
    enterprise_dashboard_system
)

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export all dashboard components
__all__ = [
    "EnterpriseDashboardSystem",
    "Dashboard",
    "DashboardWidget", 
    "DashboardMetrics",
    "DashboardType",
    "VisualizationType",
    "UpdateFrequency",
    "enterprise_dashboard_system"
]
