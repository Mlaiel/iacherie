"""Revenue Sharing Agent - Ultra-Advanced Enterprise System

This module provides equitable revenue distribution with automated calculations and payment processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    RevenueSharingManager,
    RevenueSharingSystemStatus
)

# Core System
from .core.revenue_sharing_engine import (
    RevenueSharingEngine,
    RevenueSharingJob,
    RevenueSharingResult
)

# Legacy compatibility (for smooth migration)
from .manager import RevenueSharingManager as RevenueSharingAgent

__all__ = [
    # Master Manager
    'RevenueSharingManager',
    'RevenueSharingSystemStatus',
    
    # Core System
    'RevenueSharingEngine',
    'RevenueSharingJob',
    'RevenueSharingResult',
    
    # Legacy compatibility
    'RevenueSharingAgent'
]