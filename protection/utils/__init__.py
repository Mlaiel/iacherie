"""Protection utilities module.

This module provides utility functions and compatibility wrappers
for the protection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

from .redis_compat import aioredis, REDIS_AVAILABLE

__all__ = ['aioredis', 'REDIS_AVAILABLE']