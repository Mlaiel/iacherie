"""
Backend Challenges & Competitions Core Module

This module provides enterprise-grade challenge and competition management
for creator engagement, gamification, and collaboration platform integration.

Features:
- Advanced challenge engine with multi-tier scoring
- Competition management with real-time leaderboards  
- Professional scoring systems with ML-based evaluation
- Comprehensive challenge validation and compliance
- Integration with creator collaboration workflows
- Multi-format content challenge support
- Revenue-impact challenge tracking
- Cross-platform challenge distribution

Business Logic Integration:
- Creator multi-format content → Challenge participation → IA processing
- Content protection → Challenge validation → Monetization opportunities
- Collaboration matching → Team challenges → Revenue optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from .challenge_engine import ChallengeEngine, ChallengeConfiguration, ChallengeExecutionResult
from .competition_manager import CompetitionManager, CompetitionConfiguration, CompetitionStatus
from .scoring_system import ChallengeScoringSystem, ScoringConfiguration, ScoreResult
from .challenge_validator import ChallengeValidator, ValidationConfiguration, ValidationResult
from .index import ChallengeIndexManager

__all__ = [
    # Core Engine
    'ChallengeEngine',
    'ChallengeConfiguration', 
    'ChallengeExecutionResult',
    
    # Competition Management
    'CompetitionManager',
    'CompetitionConfiguration',
    'CompetitionStatus',
    
    # Scoring System
    'ChallengeScoringSystem',
    'ScoringConfiguration',
    'ScoreResult',
    
    # Validation
    'ChallengeValidator',
    'ValidationConfiguration',
    'ValidationResult',
    
    # Index Management
    'ChallengeIndexManager'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"