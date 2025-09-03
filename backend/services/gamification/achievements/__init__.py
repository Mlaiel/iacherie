"""Achievements Module - Achievement System Components
==================================================

This module provides the achievement engine, badge system, leaderboards,
and social proof automation for the gamification services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

from .achievement_engine import AchievementEngine, get_achievement_engine
from .badge_system import BadgeSystem, get_badge_system
from .leaderboards import Leaderboards, get_leaderboards

# Social Proof Engine imports
try:
    from .social_proof_engine import SocialProofEngine, get_social_proof_engine, SocialProofElement, TestimonialTemplate, SocialProofType, TestimonialCategory
    social_proof_available = True
    logger.info("✅ Social Proof Engine loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Social Proof Engine not available: {e}")
    social_proof_available = False

__all__ = [
    "AchievementEngine",
    "BadgeSystem", 
    "Leaderboards",
    "get_achievement_engine",
    "get_badge_system",
    "get_leaderboards",
    # Social Proof Engine
    "SocialProofEngine",
    "get_social_proof_engine",
    "SocialProofElement",
    "TestimonialTemplate", 
    "SocialProofType",
    "TestimonialCategory",
    # Availability flags
    "social_proof_available"
]