"""
🔥 ORCHESTRATION LAYER - ENTERPRISE WORKFLOW AINFLUE
Ultra-advanced workflow orchestration with distributed architecture
Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING

# Enterprise imports with error handling for optimal loading
try:
    from .workflow_orchestrator import (
        WorkflowOrchestrator,
        WorkflowStage,
        WorkflowStatus,
        WorkflowContext,
        WorkflowConfig,
        WorkflowEventType,
        EnterpriseEventCoordinator,
        WorkflowEvent,
        EventHandler,
        EventType,
        EventPriority
    )
except ImportError as e:
    print(f"Orchestration layer import warning: {e}")

try:
    from .automation_engine import (
        AutomationEngine,
        AutomationRule,
        AutomationTrigger,
        AutomationAction,
        ScheduledTask,
        EnterpriseSchedulerCore,
        SchedulePriority,
        SchedulerConfig
    )
except ImportError as e:
    print(f"Automation engine import warning: {e}")

# Enterprise exports - only available classes
__all__ = [
    # Core orchestration (if available)
    "WorkflowOrchestrator",
    "WorkflowStage",
    "WorkflowStatus", 
    "WorkflowContext",
    "WorkflowConfig",
    "WorkflowEventType",
    
    # Automation engine (if available)
    "AutomationEngine",
    "AutomationRule",
    "AutomationTrigger",
    "AutomationAction",
    "ScheduledTask",
    "EnterpriseSchedulerCore",
    "SchedulePriority",
    "SchedulerConfig",
    
    # Event coordination (if available)
    "EnterpriseEventCoordinator",
    "WorkflowEvent",
    "EventHandler",
    "EventType",
    "EventPriority"
]

# Enterprise module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__license__ = "Proprietary - Ainflue Platform"
__enterprise_grade__ = True
__async_optimized__ = True