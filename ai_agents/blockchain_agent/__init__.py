"""Blockchain Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade blockchain capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    BlockchainManager,
    BlockchainSystemStatus
)

# Core System
from .core.blockchain_engine import (
    BlockchainEngine,
    BlockchainJob,
    BlockchainResult
)

# Legacy compatibility (for smooth migration)
from .manager import BlockchainManager as BlockchainAgent

__all__ = [
    # Master Manager
    'BlockchainManager',
    'BlockchainSystemStatus',
    
    # Core System
    'BlockchainEngine',
    'BlockchainJob',
    'BlockchainResult',
    
    # Legacy compatibility
    'BlockchainAgent'
]
