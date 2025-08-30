"""
🎮 Gamification Database Module - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/database/gamification/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Gamification Database Module - Production-Ready
Responsibility: Enterprise gamification data persistence and repository management
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching + Gamification → 
Multi-platform distribution

GAMIFICATION DATABASE ARCHITECTURE:
Achievement Tracking → Challenge Management → Leaderboard Systems → 
Reward Distribution → Progress Analytics → Engagement Optimization
"""

from .achievement_repository import AchievementRepository
from .challenge_repository import ChallengeRepository
from .leaderboard_repository import LeaderboardRepository
from .reward_repository import RewardRepository
from .index import GamificationRepositoryRegistry

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel (mlaiel@live.de)"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core Repositories
    "AchievementRepository",
    "ChallengeRepository", 
    "LeaderboardRepository",
    "RewardRepository",
    
    # Registry & Factory
    "GamificationRepositoryRegistry",
    
    # Module Info
    "__version__",
    "__author__",
    "__copyright__"
]