"""Enterprise Orchestration Core Module - Advanced Workflow Coordination System

This module provides comprehensive orchestration capabilities for the IA Influencer Agent
platform, managing complex multi-step workflows with AI-powered optimization and 
intelligent coordination across all business domains.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from .workflow_engine import WorkflowEngine
from .pipeline_coordinator import PipelineCoordinator
from .task_scheduler import TaskScheduler
from .resource_manager import ResourceManager
from .execution_engine import ExecutionEngine
from .state_manager import StateManager
from .dependency_resolver import DependencyResolver
from .event_coordinator import EventCoordinator
from .performance_optimizer import PerformanceOptimizer
from .error_handler import ErrorHandler
from .metrics_collector import MetricsCollector
from .configuration_manager import ConfigurationManager
from .workflow_factory import WorkflowFactory
from .pipeline_builder import PipelineBuilder
from .orchestration_controller import OrchestrationController
from .index import (
    OrchestrationSystem,
    OrchestrationSystemConfig,
    initialize_orchestration_system,
    get_orchestration_system,
    shutdown_orchestration_system,
    submit_content_processing_workflow,
    submit_protection_workflow,
    submit_monetization_workflow
)

__all__ = [
    'WorkflowEngine',
    'PipelineCoordinator', 
    'TaskScheduler',
    'ResourceManager',
    'ExecutionEngine',
    'StateManager',
    'DependencyResolver',
    'EventCoordinator',
    'PerformanceOptimizer',
    'ErrorHandler',
    'MetricsCollector',
    'ConfigurationManager',
    'WorkflowFactory',
    'PipelineBuilder',
    'OrchestrationController',
    'OrchestrationSystem',
    'OrchestrationSystemConfig',
    'initialize_orchestration_system',
    'get_orchestration_system',
    'shutdown_orchestration_system',
    'submit_content_processing_workflow',
    'submit_protection_workflow',
    'submit_monetization_workflow'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
