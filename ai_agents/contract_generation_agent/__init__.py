"""Contract Generation Agent - Ultra-Advanced Enterprise System

This module provides intelligent contract generation with legal compliance and automated terms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    ContractGenerationManager,
    ContractGenerationSystemStatus
)

# Core System
from .core.contract_generation_engine import (
    ContractGenerationEngine,
    ContractGenerationJob,
    ContractGenerationResult
)

# Legacy compatibility (for smooth migration)
from .manager import ContractGenerationManager as ContractGenerationAgent

__all__ = [
    # Master Manager
    'ContractGenerationManager',
    'ContractGenerationSystemStatus',
    
    # Core System
    'ContractGenerationEngine',
    'ContractGenerationJob',
    'ContractGenerationResult',
    
    # Legacy compatibility
    'ContractGenerationAgent'
]