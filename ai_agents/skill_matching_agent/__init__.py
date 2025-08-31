"""Skill Matching Agent - Ultra-Advanced Enterprise System

This module provides intelligent skill and competency matching for optimal team formation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    SkillMatchingManager,
    SkillMatchingSystemStatus
)

# Core System
from .core.skill_matching_engine import (
    SkillMatchingEngine,
    SkillMatchingJob,
    SkillMatchingResult
)

# Legacy compatibility (for smooth migration)
from .manager import SkillMatchingManager as SkillMatchingAgent

__all__ = [
    # Master Manager
    'SkillMatchingManager',
    'SkillMatchingSystemStatus',
    
    # Core System
    'SkillMatchingEngine',
    'SkillMatchingJob',
    'SkillMatchingResult',
    
    # Legacy compatibility
    'SkillMatchingAgent'
]