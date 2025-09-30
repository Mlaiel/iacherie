#!/usr/bin/env python3
"""
🚀 Performance Templates - IA Chérie Microservices Enterprise

High-performance templates for microservices optimization including caching,
connection pooling, async processing, memory optimization, and more.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de

⚠️ PROPRIETARY SOFTWARE - Unauthorized use prohibited
"""

from .caching_strategy_template import CachingStrategyTemplate
from .connection_pool_template import ConnectionPoolTemplate
from .async_processor_template import AsyncProcessorTemplate
from .batch_processor_template import BatchProcessorTemplate
from .stream_processor_template import StreamProcessorTemplate
from .memory_optimizer_template import MemoryOptimizerTemplate
from .cpu_optimizer_template import CPUOptimizerTemplate
from .io_optimizer_template import IOOptimizerTemplate

__all__ = [
    "CachingStrategyTemplate",
    "ConnectionPoolTemplate",
    "AsyncProcessorTemplate",
    "BatchProcessorTemplate",
    "StreamProcessorTemplate",
    "MemoryOptimizerTemplate",
    "CPUOptimizerTemplate", 
    "IOOptimizerTemplate"
]