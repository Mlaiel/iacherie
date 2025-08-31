"""Content Optimization Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade content optimization capabilities with
intelligent AI-powered analysis and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    ContentOptimizationManager,
    ContentSystemStatus
)

# Core System
from .core.optimization_engine import (
    OptimizationEngine,
    OptimizationJob,
    OptimizationResult
)

# Legacy compatibility (for smooth migration)
from .manager import ContentOptimizationManager as ContentOptimizationAgent

__all__ = [
    # Master Manager
    'ContentOptimizationManager',
    'ContentSystemStatus',
    
    # Core System
    'OptimizationEngine',
    'OptimizationJob',
    'OptimizationResult',
    
    # Legacy compatibility
    'ContentOptimizationAgent'
]