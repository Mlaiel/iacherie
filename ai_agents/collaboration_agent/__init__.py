"""Collaboration Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade collaboration capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    CollaborationManager,
    CollaborationSystemStatus
)

# Core System
from .core.collaboration_engine import (
    CollaborationEngine,
    CollaborationJob,
    CollaborationResult
)

# Legacy compatibility (for smooth migration)
from .manager import CollaborationManager as CollaborationAgent

__all__ = [
    # Master Manager
    'CollaborationManager',
    'CollaborationSystemStatus',
    
    # Core System
    'CollaborationEngine',
    'CollaborationJob',
    'CollaborationResult',
    
    # Legacy compatibility
    'CollaborationAgent'
]
