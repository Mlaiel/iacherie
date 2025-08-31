"""Intelligence Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade intelligence capabilities with
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
    IntelligenceManager,
    IntelligenceSystemStatus
)

# Core System
from .core.intelligence_engine import (
    IntelligenceEngine,
    IntelligenceJob,
    IntelligenceResult
)

# Legacy compatibility (for smooth migration)
from .manager import IntelligenceManager as IntelligenceAgent

__all__ = [
    # Master Manager
    'IntelligenceManager',
    'IntelligenceSystemStatus',
    
    # Core System
    'IntelligenceEngine',
    'IntelligenceJob',
    'IntelligenceResult',
    
    # Legacy compatibility
    'IntelligenceAgent'
]
