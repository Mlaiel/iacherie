"""Achievements Module - Achievement System Components
==================================================

This module provides the achievement engine, badge system, and leaderboards
for the gamification services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .achievement_engine import AchievementEngine, get_achievement_engine
from .badge_system import BadgeSystem, get_badge_system
from .leaderboards import Leaderboards, get_leaderboards

__all__ = [
    "AchievementEngine",
    "BadgeSystem", 
    "Leaderboards",
    "get_achievement_engine",
    "get_badge_system",
    "get_leaderboards"
]