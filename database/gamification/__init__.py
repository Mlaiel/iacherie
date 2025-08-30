"""
Database Gamification Module - Enterprise Data Layer for Gamification System

This module provides comprehensive data access layer for gamification features
including achievements, challenges, leaderboards, and rewards with advanced
repository patterns and database optimization.

Features:
- High-performance repository pattern implementation
- Advanced database optimization and query caching
- Comprehensive gamification data modeling
- Real-time leaderboard management
- Achievement tracking and progression analytics
- Reward distribution and transaction management
- Professional audit trails and data integrity
- Cross-platform gamification data synchronization

Business Logic Integration:
- Creator achievements → Database persistence → Analytics tracking
- Challenge participation → Data storage → Performance optimization
- Leaderboard updates → Real-time caching → Distribution systems
- Reward transactions → Financial tracking → Business intelligence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from .achievement_repository import AchievementRepository, AchievementData, AchievementQuery
from .challenge_repository import ChallengeRepository, ChallengeData, ChallengeQuery  
from .leaderboard_repository import LeaderboardRepository, LeaderboardData, LeaderboardQuery
from .reward_repository import RewardRepository, RewardData, RewardQuery
from .index import GamificationIndexManager

__all__ = [
    # Achievement Management
    'AchievementRepository',
    'AchievementData',
    'AchievementQuery',
    
    # Challenge Management
    'ChallengeRepository', 
    'ChallengeData',
    'ChallengeQuery',
    
    # Leaderboard Management
    'LeaderboardRepository',
    'LeaderboardData', 
    'LeaderboardQuery',
    
    # Reward Management
    'RewardRepository',
    'RewardData',
    'RewardQuery',
    
    # Index Management
    'GamificationIndexManager'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"