"""Quality Assurance Agent - Ultra-Advanced Enterprise System

This module provides automated QA capabilities with content validation, testing, and quality metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    QualityAssuranceManager,
    QualityAssuranceSystemStatus
)

# Core System
from .core.quality_assurance_engine import (
    QualityAssuranceEngine,
    QualityAssuranceJob,
    QualityAssuranceResult
)

# Legacy compatibility (for smooth migration)
from .manager import QualityAssuranceManager as QualityAssuranceAgent

__all__ = [
    # Master Manager
    'QualityAssuranceManager',
    'QualityAssuranceSystemStatus',
    
    # Core System
    'QualityAssuranceEngine',
    'QualityAssuranceJob',
    'QualityAssuranceResult',
    
    # Legacy compatibility
    'QualityAssuranceAgent'
]