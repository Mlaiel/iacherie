"""Fingerprinting Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade fingerprinting capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    FingerprintingManager,
    FingerprintingSystemStatus
)

# Core System
from .core.fingerprinting_engine import (
    FingerprintingEngine,
    FingerprintingJob,
    FingerprintingResult
)

# Legacy compatibility (for smooth migration)
from .manager import FingerprintingManager as FingerprintingAgent

__all__ = [
    # Master Manager
    'FingerprintingManager',
    'FingerprintingSystemStatus',
    
    # Core System
    'FingerprintingEngine',
    'FingerprintingJob',
    'FingerprintingResult',
    
    # Legacy compatibility
    'FingerprintingAgent'
]
