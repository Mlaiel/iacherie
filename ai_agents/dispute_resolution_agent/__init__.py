"""Dispute Resolution Agent - Ultra-Advanced Enterprise System

This module provides AI-powered dispute resolution with mediation, arbitration, and conflict management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    DisputeResolutionManager,
    DisputeResolutionSystemStatus
)

# Core System
from .core.dispute_resolution_engine import (
    DisputeResolutionEngine,
    DisputeResolutionJob,
    DisputeResolutionResult
)

# Legacy compatibility (for smooth migration)
from .manager import DisputeResolutionManager as DisputeResolutionAgent

__all__ = [
    # Master Manager
    'DisputeResolutionManager',
    'DisputeResolutionSystemStatus',
    
    # Core System
    'DisputeResolutionEngine',
    'DisputeResolutionJob',
    'DisputeResolutionResult',
    
    # Legacy compatibility
    'DisputeResolutionAgent'
]