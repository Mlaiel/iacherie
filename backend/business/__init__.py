"""Backend Business Module - IA Influencer Agent Platform
========================================================

Consolidated business logic module providing comprehensive enterprise-grade
business rules, workflow orchestration, and process automation for content
creators and influencer management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Architecture: 12-file consolidated structure (Phase 5 reorganization)
"""

from .rules import BusinessRulesEngine
from .workflows import WorkflowOrchestrator  
from .validation import BusinessValidator
from .automation import ProcessAutomation
from .integration import SystemIntegrator
from .analytics import BusinessAnalytics
from .reporting import BusinessReporter
from .compliance import ComplianceManager
from .optimization import PerformanceOptimizer
from .monitoring import BusinessMonitor
from .orchestration import ServiceOrchestrator

__all__ = [
    'BusinessRulesEngine',
    'WorkflowOrchestrator', 
    'BusinessValidator',
    'ProcessAutomation',
    'SystemIntegrator',
    'BusinessAnalytics',
    'BusinessReporter',
    'ComplianceManager',
    'PerformanceOptimizer',
    'BusinessMonitor',
    'ServiceOrchestrator'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"