"""Protection Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade protection capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    ProtectionManager,
    ProtectionSystemStatus
)

# Core System
from .core.protection_engine import (
    ProtectionEngine,
    ProtectionJob,
    ProtectionResult
)

# Legacy compatibility (for smooth migration)
from .manager import ProtectionManager as ProtectionAgent

__all__ = [
    # Master Manager
    'ProtectionManager',
    'ProtectionSystemStatus',
    
    # Core System
    'ProtectionEngine',
    'ProtectionJob',
    'ProtectionResult',
    
    # Legacy compatibility
    'ProtectionAgent'
]
