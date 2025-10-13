"""
Retry Mechanisms Index
Enterprise Retry and Resilience Patterns

This module provides intelligent retry mechanisms with exponential backoff,
circuit breaker integration, and failure pattern analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import random
from typing import Any, Callable, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RetryService:
    """Enterprise retry service with intelligent backoff"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_factor: float = 2.0,
        jitter: bool = True,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    self.logger.error(f"Max retries reached for {func.__name__}: {str(e)}")
                    raise e
                
                # Calculate delay with exponential backoff
                delay = min(base_delay * (exponential_factor ** attempt), max_delay)
                
                # Add jitter to prevent thundering herd
                if jitter:
                    delay = delay * (0.5 + random.random() * 0.5)
                
                self.logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay:.2f}s: {str(e)}")
                await asyncio.sleep(delay)
        
        if last_exception:
            raise last_exception

# Global retry service
retry_service = RetryService()

__all__ = ['RetryService', 'retry_service']