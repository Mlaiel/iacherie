"""Campaign Optimization Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade campaign optimization capabilities with
AI-powered ROI analysis and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

# Master Manager
from .manager import (
    CampaignOptimizationManager,
    CampaignOptimizationSystemStatus
)

# Core System
from .core.optimization_engine import (
    CampaignOptimizationEngine,
    OptimizationJob,
    OptimizationResult
)

# Legacy compatibility (for smooth migration)
from .manager import CampaignOptimizationManager as CampaignOptimizationAgent

__all__ = [
    # Master Manager
    'CampaignOptimizationManager',
    'CampaignOptimizationSystemStatus',
    
    # Core System
    'CampaignOptimizationEngine',
    'OptimizationJob',
    'OptimizationResult',
    
    # Legacy compatibility
    'CampaignOptimizationAgent'
]