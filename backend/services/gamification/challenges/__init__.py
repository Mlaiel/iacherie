"""Challenges Module - Challenge System Components
==============================================

Comprehensive challenge management including challenge creation,
competition engine, and challenge participation functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .challenge_creator import ChallengeCreator
from .competition_engine import CompetitionEngine

__all__ = [
    "ChallengeCreator",
    "CompetitionEngine"
]