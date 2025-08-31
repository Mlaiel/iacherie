"""Project Management Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade project management capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    ProjectManagementManager,
    ProjectManagementSystemStatus
)

# Core System
from .core.project_management_engine import (
    ProjectManagementEngine,
    ProjectManagementJob,
    ProjectManagementResult
)

# Legacy compatibility (for smooth migration)
from .manager import ProjectManagementManager as ProjectManagementAgent

__all__ = [
    # Master Manager
    'ProjectManagementManager',
    'ProjectManagementSystemStatus',
    
    # Core System
    'ProjectManagementEngine',
    'ProjectManagementJob',
    'ProjectManagementResult',
    
    # Legacy compatibility
    'ProjectManagementAgent'
]