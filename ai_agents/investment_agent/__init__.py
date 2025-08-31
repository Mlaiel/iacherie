"""Investment Agent - Investor Matching

This module provides intelligent investor matching and investment management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import InvestmentManager
from .core.investment_engine import InvestmentEngine

InvestmentAgent = InvestmentManager

__all__ = ['InvestmentManager', 'InvestmentEngine', 'InvestmentAgent']