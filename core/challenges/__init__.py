"""🎯 Challenge System Core Module - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/core/challenges/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge System Core - Production-Ready
Responsibility: Enterprise challenge and competition management system
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching + Gamification → 
Multi-platform distribution

CHALLENGE SYSTEM ARCHITECTURE:
Challenge Creation → User Participation → Progress Tracking → 
Competition Management → Scoring & Ranking → Reward Distribution
"""
from .challenge_engine import (
    ChallengeEngine,
    ChallengeType,
    ChallengeCategory,
    ChallengeStatus,
    ChallengeDifficulty,
    ChallengeConfiguration
)

from .competition_manager import (
    CompetitionManager,
    CompetitionType,
    CompetitionStatus,
    CompetitionPhase,
    ParticipationStatus,
    CompetitionRule,
    CompetitionConfiguration
)

from .scoring_system import (
    ScoringSystem,
    ScoreCalculator,
    ScoreMetric,
    ScoreWeight,
    ScoreModifier,
    RankingEngine,
    LeaderboardManager
)

from .challenge_validator import (
    ChallengeValidator,
    ValidationRule,
    ValidationResult,
    ComplianceChecker,
    RequirementValidator,
    ProgressValidator
)

from .index import (
    ChallengeSystemRegistry,
    ChallengeServiceFactory,
    create_challenge_system,
    get_default_challenge_system
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel (mlaiel@live.de)"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core Engine
    "ChallengeEngine",
    "ChallengeType",
    "ChallengeCategory", 
    "ChallengeStatus",
    "ChallengeDifficulty",
    "ChallengeConfiguration",
    
    # Competition Management
    "CompetitionManager",
    "CompetitionType",
    "CompetitionStatus",
    "CompetitionPhase",
    "ParticipationStatus",
    "CompetitionRule",
    "CompetitionConfiguration",
    
    # Scoring System
    "ScoringSystem",
    "ScoreCalculator",
    "ScoreMetric",
    "ScoreWeight", 
    "ScoreModifier",
    "RankingEngine",
    "LeaderboardManager",
    
    # Validation System
    "ChallengeValidator",
    "ValidationRule",
    "ValidationResult",
    "ComplianceChecker",
    "RequirementValidator",
    "ProgressValidator",
    
    # Registry & Factory
    "ChallengeSystemRegistry",
    "ChallengeServiceFactory",
    "create_challenge_system",
    "get_default_challenge_system",
    
    # Module Info
    "__version__",
    "__author__",
    "__copyright__"
]