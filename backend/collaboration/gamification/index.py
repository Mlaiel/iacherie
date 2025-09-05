"""Index Module - Gamification System Entry Point
==============================================

Centralized entry point for the gamification system providing
quick access to all engagement and motivation tools.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import (
    AchievementSystem,
    # PointsCalculator,
    # LevelManager,
    # BadgeEngine,
    # LeaderboardSystem,
    # ChallengeCreator,
    # RewardDistributor,
    # StreakTracker,
    # CompetitionManager,
    # SocialRewardSystem,
    # EngagementBooster
)

def get_gamification_system(config=None):
    """Get unified gamification system with all components"""
    return {
        'achievements': AchievementSystem(config),
        # 'points': PointsCalculator(config),
        # 'levels': LevelManager(config),
        # 'badges': BadgeEngine(config),
        # 'leaderboards': LeaderboardSystem(config),
        # 'challenges': ChallengeCreator(config),
        # 'rewards': RewardDistributor(config),
        # 'streaks': StreakTracker(config),
        # 'competitions': CompetitionManager(config),
        # 'social_rewards': SocialRewardSystem(config),
        # 'engagement': EngagementBooster(config)
    }

async def setup_project_gamification(project_id, participants, config=None):
    """Set up complete gamification system for a project"""
    system = get_gamification_system(config)
    
    # Create project-specific achievements
    project_achievements = []
    
    # Collaboration achievement
    collab_achievement = await system['achievements'].create_achievement(
        name=f"Project {project_id} Collaborator",
        description="Successfully participate in project collaboration",
        achievement_type="COLLABORATION",
        tier="SILVER",
        rules=[{
            'rule_type': 'count',
            'conditions': {'project_id': project_id, 'activity_types': ['collaboration_joined']},
            'target_value': 1
        }],
        points_value=200
    )
    project_achievements.append(collab_achievement)
    
    # Content creation achievement
    content_achievement = await system['achievements'].create_achievement(
        name=f"Project {project_id} Creator",
        description="Create content for the project",
        achievement_type="CONTENT_CREATION",
        tier="BRONZE",
        rules=[{
            'rule_type': 'count',
            'conditions': {'project_id': project_id, 'activity_types': ['content_created']},
            'target_value': 1
        }],
        points_value=100
    )
    project_achievements.append(content_achievement)
    
    return {
        'project_id': project_id,
        'achievements': project_achievements,
        'gamification_system': system
    }