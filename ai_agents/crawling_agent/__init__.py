"""Crawling Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade crawling capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    CrawlingManager,
    CrawlingSystemStatus
)

# Core System
from .core.crawling_engine import (
    CrawlingEngine,
    CrawlingJob,
    CrawlingResult
)

# Legacy compatibility (for smooth migration)
from .manager import CrawlingManager as CrawlingAgent

__all__ = [
    # Master Manager
    'CrawlingManager',
    'CrawlingSystemStatus',
    
    # Core System
    'CrawlingEngine',
    'CrawlingJob',
    'CrawlingResult',
    
    # Legacy compatibility
    'CrawlingAgent'
]
