#!/usr/bin/env python3
"""Fallback Handler Template - Graceful degradation and fallback mechanisms"""

from typing import Callable, Any

class FallbackHandlerTemplate:
    """Fallback handler for graceful degradation"""
    
    def __init__(self):
        self.fallback_functions = {}
    
    def register_fallback(self, operation_name: str, fallback_func: Callable):
        """Register fallback function for operation"""
        self.fallback_functions[operation_name] = fallback_func
    
    async def execute_with_fallback(self, operation_name: str, primary_func: Callable, *args, **kwargs) -> Any:
        """Execute primary function with fallback"""
        try:
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)
        except Exception as e:
            print(f"Primary function failed: {e}")
            
            # Execute fallback if available
            fallback_func = self.fallback_functions.get(operation_name)
            if fallback_func:
                try:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    print(f"Fallback also failed: {fallback_error}")
                    raise e
            else:
                raise e