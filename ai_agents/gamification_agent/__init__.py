"""
Gamification Agent Module - Advanced AI-Powered Creator Engagement System

Industrial-grade gamification intelligence providing automated challenge generation,
reward optimization, engagement prediction, and social competition management
for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This gamification system and AI methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

🎯 BUSINESS LOGIC INTEGRATION:
Creator Registration → Content Upload → AI Gamification Analysis → Challenge Generation
→ Engagement Prediction → Reward Optimization → Social Competition → Badge Generation

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Gamification Specialist
- Microservices Architect & Database Expert
- DevOps Engineer & Security Specialist
- Audio Processing & Multimedia Expert
"""

from .gamification_agent import GamificationAgent, GamificationConfig
from .challenge_ai import ChallengeGenerator, ChallengeConfig
from .reward_optimization_ai import RewardOptimizer, RewardConfig
from .user_engagement_predictor import EngagementPredictor, EngagementConfig
from .social_competition_ai import SocialCompetitionManager, CompetitionConfig
from .badge_generation_ai import BadgeGenerator, BadgeConfig
from .progression_analyzer import ProgressionAnalyzer, ProgressionConfig

# Export main agent
__all__ = [
    # Main Agent
    'GamificationAgent',
    'GamificationConfig',
    
    # AI Modules
    'ChallengeGenerator',
    'ChallengeConfig',
    'RewardOptimizer', 
    'RewardConfig',
    'EngagementPredictor',
    'EngagementConfig',
    'SocialCompetitionManager',
    'CompetitionConfig',
    'BadgeGenerator',
    'BadgeConfig',
    'ProgressionAnalyzer',
    'ProgressionConfig'
]

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"