"""Workflow Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade workflow capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    WorkflowManager,
    WorkflowSystemStatus
)

# Core System
from .core.workflow_engine import (
    WorkflowEngine,
    WorkflowJob,
    WorkflowResult
)

# Legacy compatibility (for smooth migration)
from .manager import WorkflowManager as WorkflowAgent

__all__ = [
    # Master Manager
    'WorkflowManager',
    'WorkflowSystemStatus',
    
    # Core System
    'WorkflowEngine',
    'WorkflowJob',
    'WorkflowResult',
    
    # Legacy compatibility
    'WorkflowAgent'
]
