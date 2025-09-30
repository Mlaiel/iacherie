#!/usr/bin/env python3
"""
📦 BATCH PROCESSOR TEMPLATE - EFFICIENT BULK DATA PROCESSING
============================================================

High-performance batch processing with chunking, parallel execution,
and intelligent resource management for large-scale data operations.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import asyncio
import logging
from typing import Any, Callable, List, Optional, Iterator
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class BatchConfig:
    """Batch processing configuration"""
    batch_size: int = 100
    max_concurrent_batches: int = 5
    retry_failed_items: bool = True
    max_retries: int = 3

class BatchProcessorTemplate:
    """
    🚀 ENTERPRISE BATCH PROCESSOR TEMPLATE
    
    Efficient bulk processing with chunking and parallel execution.
    """
    
    def __init__(self, config: BatchConfig = None):
        """Initialize batch processor"""
        self.config = config or BatchConfig()
        self.processed_count = 0
        self.failed_count = 0
    
    async def process_batch(self, items: List[Any], processor_func: Callable) -> List[Any]:
        """Process items in batches"""
        if not items:
            return []
        
        # Split into chunks
        chunks = self._create_chunks(items, self.config.batch_size)
        
        # Process chunks concurrently
        semaphore = asyncio.Semaphore(self.config.max_concurrent_batches)
        tasks = [
            self._process_chunk(chunk, processor_func, semaphore)
            for chunk in chunks
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        processed_items = []
        for result in results:
            if isinstance(result, list):
                processed_items.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Batch processing failed: {result}")
                self.failed_count += len(items)
        
        return processed_items
    
    def _create_chunks(self, items: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split items into chunks"""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    
    async def _process_chunk(self, chunk: List[Any], processor_func: Callable, semaphore: asyncio.Semaphore) -> List[Any]:
        """Process a single chunk"""
        async with semaphore:
            try:
                if asyncio.iscoroutinefunction(processor_func):
                    results = await processor_func(chunk)
                else:
                    results = processor_func(chunk)
                
                self.processed_count += len(chunk)
                return results if isinstance(results, list) else [results]
                
            except Exception as e:
                logger.error(f"Chunk processing failed: {e}")
                raise

# Factory function
def create_batch_processor(**kwargs) -> BatchProcessorTemplate:
    """Create batch processor instance"""
    config = BatchConfig(**kwargs)
    return BatchProcessorTemplate(config)