"""Optimization Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade optimization capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    OptimizationManager,
    OptimizationSystemStatus
)

# Core System
from .core.optimization_engine import (
    OptimizationEngine,
    OptimizationJob,
    OptimizationResult
)

# Legacy compatibility (for smooth migration)
from .manager import OptimizationManager as OptimizationAgent

__all__ = [
    # Master Manager
    'OptimizationManager',
    'OptimizationSystemStatus',
    
    # Core System
    'OptimizationEngine',
    'OptimizationJob',
    'OptimizationResult',
    
    # Legacy compatibility
    'OptimizationAgent'
]
