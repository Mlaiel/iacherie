"""
IA-Influencer Agent - Workflow Agent Module

This module provides advanced workflow orchestration and automation capabilities
for multi-format content creators in the IA-Influencer ecosystem.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

from .workflow_agent import WorkflowAgent
from .workflow_orchestrator import (
    WorkflowOrchestrator,
    OrchestrationStrategy,
    WorkflowNode,
    ExecutionContext,
    ExecutionResult
)
from .workflow_engine import (
    WorkflowEngine,
    ExecutionMode,
    OptimizationStrategy,
    ExecutionPlan,
    ExecutionMetrics,
    ExecutionTask
)
from .workflow_templates import (
    WorkflowTemplateManager,
    TemplateType,
    TemplateCategory,
    WorkflowTemplate,
    TemplateMetadata,
    TemplateInstance
)
from .workflow_scheduler import (
    WorkflowScheduler,
    ScheduleType,
    ScheduleStatus,
    Priority,
    WorkflowSchedule,
    ScheduleExecution
)
from .workflow_monitor import (
    WorkflowMonitor,
    AlertSeverity,
    MetricType,
    HealthStatus,
    WorkflowMetric,
    Alert,
    HealthCheck,
    PerformanceReport
)

__all__ = [
    # Main agent
    'WorkflowAgent',
    
    # Orchestrator components
    'WorkflowOrchestrator',
    'OrchestrationStrategy',
    'WorkflowNode',
    'ExecutionContext',
    'ExecutionResult',
    
    # Engine components
    'WorkflowEngine',
    'ExecutionMode',
    'OptimizationStrategy',
    'ExecutionPlan',
    'ExecutionMetrics',
    'ExecutionTask',
    
    # Template components
    'WorkflowTemplateManager',
    'TemplateType',
    'TemplateCategory',
    'WorkflowTemplate',
    'TemplateMetadata',
    'TemplateInstance',
    
    # Scheduler components
    'WorkflowScheduler',
    'ScheduleType',
    'ScheduleStatus',
    'Priority',
    'WorkflowSchedule',
    'ScheduleExecution',
    
    # Monitor components
    'WorkflowMonitor',
    'AlertSeverity',
    'MetricType',
    'HealthStatus',
    'WorkflowMetric',
    'Alert',
    'HealthCheck',
    'PerformanceReport',
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "2025 Fahed Mlaiel"

# Module metadata
MODULE_INFO = {
    'name': 'Workflow Agent',
    'description': 'Enterprise-grade workflow orchestration and automation system',
    'version': __version__,
    'author': __author__,
    'email': __email__,
    'capabilities': [
        'Multi-step workflow orchestration',
        'AI-powered workflow optimization',
        'Real-time workflow monitoring',
        'Dynamic workflow templates',
        'Intelligent scheduling',
        'Enterprise scalability'
    ],
    'supported_formats': [
        'Audio workflows',
        'Video workflows',
        'Content creation workflows',
        'Social media workflows',
        'Protection workflows',
        'SEO workflows'
    ],
    'integrations': [
        'Spotify API',
        'Social Media APIs',
        'Content Protection Systems',
        'Analytics Platforms',
        'Cloud Storage Services'
    ]
}
