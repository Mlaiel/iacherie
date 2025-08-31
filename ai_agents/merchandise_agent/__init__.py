"""Merchandise Agent - Automated Product Derivatives

This module provides automated merchandise management and product generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import MerchandiseManager
from .core.merchandise_engine import MerchandiseEngine

MerchandiseAgent = MerchandiseManager

__all__ = ['MerchandiseManager', 'MerchandiseEngine', 'MerchandiseAgent']