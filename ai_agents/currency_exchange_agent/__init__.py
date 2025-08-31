"""CurrencyExchange Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade currency exchange and conversion capabilities with
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
    CurrencyExchangeManager,
    CurrencyExchangeSystemStatus
)

# Core System
from .core.currency_exchange_engine import (
    CurrencyExchangeEngine,
    CurrencyExchangeJob,
    CurrencyExchangeResult
)

# Legacy compatibility (for smooth migration)
from .manager import CurrencyExchangeManager as CurrencyExchangeAgent

__all__ = [
    # Master Manager
    'CurrencyExchangeManager',
    'CurrencyExchangeSystemStatus',
    
    # Core System
    'CurrencyExchangeEngine',
    'CurrencyExchangeJob',
    'CurrencyExchangeResult',
    
    # Legacy compatibility
    'CurrencyExchangeAgent'
]