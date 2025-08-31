"""Tax Optimization Agent - Fiscal Optimization

This module provides intelligent tax optimization and fiscal management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import TaxOptimizationManager
from .core.tax_engine import TaxOptimizationEngine

TaxOptimizationAgent = TaxOptimizationManager

__all__ = ['TaxOptimizationManager', 'TaxOptimizationEngine', 'TaxOptimizationAgent']