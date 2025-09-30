#!/usr/bin/env python3
"""
🌊 STREAM PROCESSOR TEMPLATE - REAL-TIME DATA STREAMING
======================================================

Real-time stream processing with windowing, aggregation, and 
backpressure handling for continuous data flows.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import asyncio
import logging
from typing import Any, Callable, AsyncIterator
from dataclasses import dataclass
import time
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class StreamConfig:
    """Stream processing configuration"""
    window_size_ms: int = 1000
    max_buffer_size: int = 10000
    backpressure_threshold: float = 0.8

class StreamProcessorTemplate:
    """
    🚀 ENTERPRISE STREAM PROCESSOR TEMPLATE
    
    Real-time streaming with windowing and backpressure handling.
    """
    
    def __init__(self, config: StreamConfig = None):
        """Initialize stream processor"""
        self.config = config or StreamConfig()
        self.buffer = deque(maxlen=self.config.max_buffer_size)
        self.processed_count = 0
        self.running = False
    
    async def process_stream(self, data_stream: AsyncIterator[Any], processor_func: Callable):
        """Process continuous data stream"""
        self.running = True
        
        try:
            async for item in data_stream:
                if not self.running:
                    break
                
                # Check backpressure
                if self._check_backpressure():
                    await asyncio.sleep(0.01)  # Brief delay
                
                # Add to buffer
                self.buffer.append({
                    'data': item,
                    'timestamp': time.time()
                })
                
                # Process if window is full
                if len(self.buffer) >= 100:  # Process in small batches
                    await self._process_buffer(processor_func)
                    
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
        finally:
            self.running = False
    
    def _check_backpressure(self) -> bool:
        """Check if backpressure threshold is exceeded"""
        current_size = len(self.buffer)
        threshold = self.config.max_buffer_size * self.config.backpressure_threshold
        return current_size > threshold
    
    async def _process_buffer(self, processor_func: Callable):
        """Process buffered items"""
        if not self.buffer:
            return
        
        # Extract batch from buffer
        batch = []
        for _ in range(min(100, len(self.buffer))):
            if self.buffer:
                batch.append(self.buffer.popleft())
        
        if batch:
            try:
                if asyncio.iscoroutinefunction(processor_func):
                    await processor_func(batch)
                else:
                    processor_func(batch)
                
                self.processed_count += len(batch)
                
            except Exception as e:
                logger.error(f"Buffer processing failed: {e}")

# Factory function
def create_stream_processor(**kwargs) -> StreamProcessorTemplate:
    """Create stream processor instance"""
    config = StreamConfig(**kwargs)
    return StreamProcessorTemplate(config)