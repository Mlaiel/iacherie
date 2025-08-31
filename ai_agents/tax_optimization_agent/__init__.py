"""TaxOptimization Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade tax optimization and compliance capabilities with
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
    TaxOptimizationManager,
    TaxOptimizationSystemStatus
)

# Core System
from .core.tax_optimization_engine import (
    TaxOptimizationEngine,
    TaxOptimizationJob,
    TaxOptimizationResult
)

# Legacy compatibility (for smooth migration)
from .manager import TaxOptimizationManager as TaxOptimizationAgent

__all__ = [
    # Master Manager
    'TaxOptimizationManager',
    'TaxOptimizationSystemStatus',
    
    # Core System
    'TaxOptimizationEngine',
    'TaxOptimizationJob',
    'TaxOptimizationResult',
    
    # Legacy compatibility
    'TaxOptimizationAgent'
]