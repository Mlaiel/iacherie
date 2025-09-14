"""
Timeout Handling Index
Enterprise Timeout Management and Circuit Protection

This module provides comprehensive timeout handling with graceful degradation
and automatic recovery mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TimeoutService:
    """Enterprise timeout handling service"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def execute_with_timeout(
        self,
        func: Callable,
        timeout_seconds: float,
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with timeout protection"""
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=timeout_seconds
                )
            return result
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout after {timeout_seconds}s for {func.__name__}")
            
            if fallback_func:
                try:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Fallback function failed: {str(e)}")
                    raise
            else:
                raise asyncio.TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

# Global timeout service
timeout_service = TimeoutService()

__all__ = ['TimeoutService', 'timeout_service']