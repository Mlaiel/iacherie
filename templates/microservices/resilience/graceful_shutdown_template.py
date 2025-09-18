#!/usr/bin/env python3
"""Graceful Shutdown Template - Graceful service shutdown handling"""

import asyncio
import signal
from typing import List, Callable

class GracefulShutdownTemplate:
    """Graceful shutdown handler"""
    
    def __init__(self):
        self.shutdown_hooks: List[Callable] = []
        self.is_shutting_down = False
    
    def register_shutdown_hook(self, hook: Callable):
        """Register shutdown hook"""
        self.shutdown_hooks.append(hook)
    
    async def graceful_shutdown(self):
        """Execute graceful shutdown"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        print("🔄 Starting graceful shutdown...")
        
        for hook in self.shutdown_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                print(f"Shutdown hook failed: {e}")
        
        print("✅ Graceful shutdown completed")