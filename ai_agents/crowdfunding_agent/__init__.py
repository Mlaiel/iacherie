"""Crowdfunding Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade crowdfunding and campaign management capabilities with
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
    CrowdfundingManager,
    CrowdfundingSystemStatus
)

# Core System
from .core.crowdfunding_engine import (
    CrowdfundingEngine,
    CrowdfundingJob,
    CrowdfundingResult
)

# Legacy compatibility (for smooth migration)
from .manager import CrowdfundingManager as CrowdfundingAgent

__all__ = [
    # Master Manager
    'CrowdfundingManager',
    'CrowdfundingSystemStatus',
    
    # Core System
    'CrowdfundingEngine',
    'CrowdfundingJob',
    'CrowdfundingResult',
    
    # Legacy compatibility
    'CrowdfundingAgent'
]