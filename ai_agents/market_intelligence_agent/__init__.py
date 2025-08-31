"""MarketIntelligence Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade market_intelligence capabilities with
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
    MarketIntelligenceManager,
    MarketIntelligenceSystemStatus
)

# Core System
from .core.market_intelligence_engine import (
    MarketIntelligenceEngine,
    MarketIntelligenceJob,
    MarketIntelligenceResult
)

# Legacy compatibility (for smooth migration)
from .manager import MarketIntelligenceManager as MarketIntelligenceAgent

__all__ = [
    # Master Manager
    'MarketIntelligenceManager',
    'MarketIntelligenceSystemStatus',
    
    # Core System
    'MarketIntelligenceEngine',
    'MarketIntelligenceJob',
    'MarketIntelligenceResult',
    
    # Legacy compatibility
    'MarketIntelligenceAgent'
]
