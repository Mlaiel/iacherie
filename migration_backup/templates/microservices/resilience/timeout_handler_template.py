#!/usr/bin/env python3
"""Timeout Handler Template - Request timeout and cancellation management"""

import asyncio
from typing import Callable, Any

class TimeoutHandlerTemplate:
    """Request timeout handler"""
    
    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout
    
    async def execute_with_timeout(self, func: Callable, timeout: float = None, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        timeout = timeout or self.default_timeout
        
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            else:
                # For synchronous functions, run in executor with timeout
                loop = asyncio.get_event_loop()
                return await asyncio.wait_for(
                    loop.run_in_executor(None, func, *args),
                    timeout=timeout
                )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")