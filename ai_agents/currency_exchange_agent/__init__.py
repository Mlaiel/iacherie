"""Currency Exchange Agent - Multi-Currency Exchange

This module provides intelligent multi-currency exchange management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import CurrencyExchangeManager
from .core.exchange_engine import CurrencyExchangeEngine

CurrencyExchangeAgent = CurrencyExchangeManager

__all__ = ['CurrencyExchangeManager', 'CurrencyExchangeEngine', 'CurrencyExchangeAgent']