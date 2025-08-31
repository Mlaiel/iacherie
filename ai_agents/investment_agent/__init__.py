"""Investment Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade investment matching and management capabilities with
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
    InvestmentManager,
    InvestmentSystemStatus
)

# Core System
from .core.investment_engine import (
    InvestmentEngine,
    InvestmentJob,
    InvestmentResult
)

# Legacy compatibility (for smooth migration)
from .manager import InvestmentManager as InvestmentAgent

__all__ = [
    # Master Manager
    'InvestmentManager',
    'InvestmentSystemStatus',
    
    # Core System
    'InvestmentEngine',
    'InvestmentJob',
    'InvestmentResult',
    
    # Legacy compatibility
    'InvestmentAgent'
]