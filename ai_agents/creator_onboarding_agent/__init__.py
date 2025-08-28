"""
CreatorOnboarding Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade creator_onboarding capabilities with
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
    CreatorOnboardingManager,
    CreatorOnboardingSystemStatus
)

# Core System
from .core.creator_onboarding_engine import (
    CreatorOnboardingEngine,
    CreatorOnboardingJob,
    CreatorOnboardingResult
)

# Legacy compatibility (for smooth migration)
from .manager import CreatorOnboardingManager as CreatorOnboardingAgent

__all__ = [
    # Master Manager
    'CreatorOnboardingManager',
    'CreatorOnboardingSystemStatus',
    
    # Core System
    'CreatorOnboardingEngine',
    'CreatorOnboardingJob',
    'CreatorOnboardingResult',
    
    # Legacy compatibility
    'CreatorOnboardingAgent'
]
