"""Version Control Agent - Ultra-Advanced Enterprise System

This module provides Git-like version control for creative content with branching, merging, and history tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    VersionControlManager,
    VersionControlSystemStatus
)

# Core System
from .core.version_control_engine import (
    VersionControlEngine,
    VersionControlJob,
    VersionControlResult
)

# Legacy compatibility (for smooth migration)
from .manager import VersionControlManager as VersionControlAgent

__all__ = [
    # Master Manager
    'VersionControlManager',
    'VersionControlSystemStatus',
    
    # Core System
    'VersionControlEngine',
    'VersionControlJob',
    'VersionControlResult',
    
    # Legacy compatibility
    'VersionControlAgent'
]