"""Challenges Module - Challenge System Components
==============================================

This module provides the challenge creator and competition engine
for the gamification services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .challenge_creator import ChallengeCreator, get_challenge_creator
from .competition_engine import CompetitionEngine, get_competition_engine

__all__ = [
    "ChallengeCreator",
    "CompetitionEngine",
    "get_challenge_creator",
    "get_competition_engine"
]