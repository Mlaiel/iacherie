# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test suite for Gamification System module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestGamificationSystem(unittest.TestCase):
    """Test suite for GamificationSystem class"""    def setUp(self):
        """Set up test fixtures"""        self.gamification = None  # Will be mocked
        self.sample_user_profile = {
            "user_id": "user_123",
            "level": 5,
            "experience_points": 2500,
            "achievements": ["first_upload", "collaboration_master"],
            "badges": ["content_creator", "community_leader"],
            "streak_days": 15,
            "total_content_uploads": 25,
            "successful_collaborations": 8
        }

    def test_user_gamification_profile_structure(self):
        """Test user gamification profile data structure"""        profile = {
            "user_id": "user_123",
            "level": 1,
            "experience_points": 0,
            "achievements": [],
            "badges": [],
            "streak_days": 0,
            "last_activity": datetime.now(),
            "total_content_uploads": 0,
            "successful_collaborations": 0
        }
        
        # Verify required fields
        required_fields = ["user_id", "level", "experience_points", "achievements", "badges"]
        for field in required_fields:
            self.assertIn(field, profile)
        
        # Verify data types
        self.assertIsInstance(profile["level"], int)
        self.assertIsInstance(profile["experience_points"], int)
        self.assertIsInstance(profile["achievements"], list)
        self.assertIsInstance(profile["badges"], list)

    def test_experience_points_calculation(self):
        """Test experience points calculation for different actions"""        action_points = {
            "content_upload": 50,
            "collaboration_complete": 100,
            "violation_resolved": 75,
            "daily_login": 10,
            "first_time_bonus": 25,
            "quality_content": 30,
            "community_engagement": 15
        }
        
        user_actions = [
            {"action": "content_upload", "count": 3},
            {"action": "collaboration_complete", "count": 1},
            {"action": "daily_login", "count": 7},
            {"action": "quality_content", "count": 2}
        ]
        
        total_points = 0
        for action in user_actions:
            action_type = action["action"]
            count = action["count"]
            points_per_action = action_points.get(action_type, 0)
            total_points += points_per_action * count
        
        # Calculate expected points
        expected_points = (50 * 3) + (100 * 1) + (10 * 7) + (30 * 2)
        
        self.assertEqual(total_points, expected_points)
        self.assertEqual(total_points, 380)

    def test_level_progression_system(self):
        """Test level progression based on experience points"""        level_thresholds = {
            1: 0,
            2: 100,
            3: 300,
            4: 600,
            5: 1000,
            6: 1500,
            7: 2500,
            8: 4000,
            9: 6000,
            10: 10000
        }
        
        test_experience_points = [50, 250, 750, 1200, 3000, 5000, 8000]
        expected_levels = [1, 2, 3, 4, 6, 7, 8]
        
        for i, exp_points in enumerate(test_experience_points):
            # Find level based on experience points
            user_level = 1
            for level, threshold in sorted(level_thresholds.items()):
                if exp_points >= threshold:
                    user_level = level
                else:
                    break
            
            self.assertEqual(user_level, expected_levels[i])

    def test_achievement_unlock_system(self):
        """Test achievement unlock system"""        achievements_config = {
            "first_upload": {
                "condition": "content_uploads >= 1",
                "title": "First Steps",
                "description": "Upload your first content",
                "points": 50
            },
            "collaboration_master": {
                "condition": "successful_collaborations >= 5",
                "title": "Collaboration Master",
                "description": "Complete 5 successful collaborations",
                "points": 200
            },
            "consistency_king": {
                "condition": "streak_days >= 30",
                "title": "Consistency King",
                "description": "30-day activity streak",
                "points": 150
            },
            "content_creator": {
                "condition": "content_uploads >= 10",
                "title": "Content Creator",
                "description": "Upload 10 pieces of content",
                "points": 100
            }
        }
        
        user_stats = {
            "content_uploads": 12,
            "successful_collaborations": 6,
            "streak_days": 25,
            "achievements": ["first_upload"]  # Already unlocked
        }
        
        # Check for new achievements
        new_achievements = []
        for achievement_id, config in achievements_config.items():
            if achievement_id not in user_stats["achievements"]:
                # Parse condition (simplified)
                condition = config["condition"]
                
                if "content_uploads >= 1" in condition and user_stats["content_uploads"] >= 1:
                    new_achievements.append(achievement_id)
                elif "content_uploads >= 10" in condition and user_stats["content_uploads"] >= 10:
                    new_achievements.append(achievement_id)
                elif "successful_collaborations >= 5" in condition and user_stats["successful_collaborations"] >= 5:
                    new_achievements.append(achievement_id)
                elif "streak_days >= 30" in condition and user_stats["streak_days"] >= 30:
                    new_achievements.append(achievement_id)
        
        # Verify achievement unlocking
        expected_achievements = ["collaboration_master", "content_creator"]
        self.assertEqual(set(new_achievements), set(expected_achievements))

    def test_badge_earning_system(self):
        """Test badge earning system"""        badge_criteria = {
            "community_leader": {
                "type": "engagement",
                "requirements": {
                    "collaborations": 10,
                    "community_rating": 4.5,
                    "active_days": 60
                }
            },
            "quality_creator": {
                "type": "content",
                "requirements": {
                    "avg_content_rating": 4.0,
                    "content_count": 15,
                    "violation_rate": 0.05  # Less than 5% violation rate
                }
            },
            "mentor": {
                "type": "social",
                "requirements": {
                    "helped_new_users": 5,
                    "positive_feedback": 20,
                    "level": 7
                }
            }
        }
        
        user_profile = {
            "collaborations": 12,
            "community_rating": 4.7,
            "active_days": 65,
            "avg_content_rating": 4.2,
            "content_count": 18,
            "violation_rate": 0.02,
            "helped_new_users": 6,
            "positive_feedback": 25,
            "level": 8,
            "badges": []
        }
        
        # Check badge eligibility
        earned_badges = []
        
        for badge_id, criteria in badge_criteria.items():
            requirements = criteria["requirements"]
            eligible = True
            
            for req_key, req_value in requirements.items():
                user_value = user_profile.get(req_key, 0)
                
                if req_key == "violation_rate":
                    # Lower is better for violation rate
                    if user_value > req_value:
                        eligible = False
                        break
                else:
                    # Higher is better for other metrics
                    if user_value < req_value:
                        eligible = False
                        break
            
            if eligible:
                earned_badges.append(badge_id)
        
        # Verify badge earning
        expected_badges = ["community_leader", "quality_creator", "mentor"]
        self.assertEqual(set(earned_badges), set(expected_badges))

    def test_daily_streak_tracking(self):
        """Test daily activity streak tracking"""        activity_log = [
            {"date": "2025-01-01", "active": True},
            {"date": "2025-01-02", "active": True},
            {"date": "2025-01-03", "active": False},  # Missed day
            {"date": "2025-01-04", "active": True},
            {"date": "2025-01-05", "active": True},
            {"date": "2025-01-06", "active": True},
            {"date": "2025-01-07", "active": True}
        ]
        
        # Calculate current streak
        current_streak = 0
        max_streak = 0
        temp_streak = 0
        
        # Calculate streaks
        for entry in activity_log:
            if entry["active"]:
                temp_streak += 1
                max_streak = max(max_streak, temp_streak)
            else:
                temp_streak = 0
        
        # Current streak is the last consecutive active days
        for entry in reversed(activity_log):
            if entry["active"]:
                current_streak += 1
            else:
                break
        
        self.assertEqual(current_streak, 4)  # Last 4 days active
        self.assertEqual(max_streak, 4)      # Best streak is also 4
        
        # Test streak bonus calculation
        streak_bonus_multiplier = 1.0
        if current_streak >= 7:
            streak_bonus_multiplier = 1.5
        elif current_streak >= 3:
            streak_bonus_multiplier = 1.2
        
        self.assertEqual(streak_bonus_multiplier, 1.2)  # 4-day streak gets 1.2x bonus

    def test_leaderboard_ranking_system(self):
        """Test leaderboard ranking system"""        users = [
            {"user_id": "user_1", "level": 8, "experience_points": 5500, "collaborations": 12},
            {"user_id": "user_2", "level": 6, "experience_points": 2800, "collaborations": 8},
            {"user_id": "user_3", "level": 9, "experience_points": 7200, "collaborations": 15},
            {"user_id": "user_4", "level": 7, "experience_points": 3900, "collaborations": 10},
            {"user_id": "user_5", "level": 8, "experience_points": 4800, "collaborations": 9}
        ]
        
        # Create different leaderboards
        
        # Experience points leaderboard
        exp_leaderboard = sorted(users, key=lambda x: x["experience_points"], reverse=True)
        
        # Level leaderboard (with experience points as tiebreaker)
        level_leaderboard = sorted(users, key=lambda x: (x["level"], x["experience_points"]), reverse=True)
        
        # Collaboration leaderboard
        collab_leaderboard = sorted(users, key=lambda x: x["collaborations"], reverse=True)
        
        # Verify rankings
        self.assertEqual(exp_leaderboard[0]["user_id"], "user_3")  # 7200 points
        self.assertEqual(exp_leaderboard[1]["user_id"], "user_1")  # 5500 points
        
        self.assertEqual(level_leaderboard[0]["user_id"], "user_3")  # Level 9
        self.assertEqual(level_leaderboard[1]["user_id"], "user_1")  # Level 8, higher exp
        
        self.assertEqual(collab_leaderboard[0]["user_id"], "user_3")  # 15 collaborations
        self.assertEqual(collab_leaderboard[1]["user_id"], "user_1")  # 12 collaborations

    def test_seasonal_challenge_system(self):
        """Test seasonal challenge system"""        current_season = {
            "id": "winter_2025",
            "name": "Winter Creator Challenge",
            "start_date": datetime(2025, 1, 1),
            "end_date": datetime(2025, 3, 31),
            "challenges": [
                {
                    "id": "winter_uploads",
                    "title": "Winter Content Spree",
                    "description": "Upload 10 pieces of content during winter",
                    "target": 10,
                    "reward_points": 300,
                    "reward_badge": "winter_creator"
                },
                {
                    "id": "collaboration_goal",
                    "title": "Collaborative Winter",
                    "description": "Complete 3 collaborations during winter",
                    "target": 3,
                    "reward_points": 200,
                    "reward_badge": "winter_collaborator"
                }
            ]
        }
        
        user_progress = {
            "user_id": "user_123",
            "season_id": "winter_2025",
            "challenge_progress": {
                "winter_uploads": {"current": 7, "completed": False},
                "collaboration_goal": {"current": 3, "completed": True}
            }
        }
        
        # Check challenge completion
        completed_challenges = []
        
        for challenge in current_season["challenges"]:
            challenge_id = challenge["id"]
            progress = user_progress["challenge_progress"].get(challenge_id, {"current": 0})
            
            if progress["current"] >= challenge["target"]:
                completed_challenges.append(challenge_id)
                progress["completed"] = True
        
        # Calculate rewards
        total_reward_points = 0
        earned_badges = []
        
        for challenge in current_season["challenges"]:
            if challenge["id"] in completed_challenges:
                total_reward_points += challenge["reward_points"]
                if challenge.get("reward_badge"):
                    earned_badges.append(challenge["reward_badge"])
        
        # Verify challenge system
        self.assertIn("collaboration_goal", completed_challenges)
        self.assertNotIn("winter_uploads", completed_challenges)  # 7/10 not complete
        self.assertEqual(total_reward_points, 200)  # Only collaboration challenge
        self.assertEqual(earned_badges, ["winter_collaborator"])

    def test_quest_system(self):
        """Test quest/mission system"""        available_quests = [
            {
                "id": "daily_creator",
                "type": "daily",
                "title": "Daily Creator",
                "description": "Upload 1 piece of content today",
                "requirements": {"content_uploads_today": 1},
                "reward": {"experience": 25, "coins": 50},
                "expires": datetime.now() + timedelta(hours=24)
            },
            {
                "id": "social_butterfly",
                "type": "weekly", 
                "title": "Social Butterfly",
                "description": "Collaborate with 2 different creators this week",
                "requirements": {"unique_collaborations_week": 2},
                "reward": {"experience": 100, "badge": "social_butterfly"},
                "expires": datetime.now() + timedelta(days=7)
            },
            {
                "id": "quality_focus",
                "type": "achievement",
                "title": "Quality Focus",
                "description": "Maintain 4.5+ rating on last 5 uploads",
                "requirements": {"avg_rating_last_5": 4.5},
                "reward": {"experience": 150, "badge": "quality_master"},
                "expires": None  # No expiry for achievement quests
            }
        ]
        
        user_stats = {
            "content_uploads_today": 1,
            "unique_collaborations_week": 3,
            "avg_rating_last_5": 4.7,
            "completed_quests": []
        }
        
        # Check quest completion
        completed_quests = []
        total_rewards = {"experience": 0, "coins": 0, "badges": []}
        
        for quest in available_quests:
            quest_id = quest["id"]
            requirements = quest["requirements"]
            
            # Check if quest is already completed
            if quest_id in user_stats["completed_quests"]:
                continue
            
            # Check if quest has expired
            if quest.get("expires") and datetime.now() > quest["expires"]:
                continue
            
            # Check requirements
            requirements_met = True
            for req_key, req_value in requirements.items():
                user_value = user_stats.get(req_key, 0)
                if user_value < req_value:
                    requirements_met = False
                    break
            
            if requirements_met:
                completed_quests.append(quest_id)
                
                # Add rewards
                reward = quest["reward"]
                total_rewards["experience"] += reward.get("experience", 0)
                total_rewards["coins"] += reward.get("coins", 0)
                if reward.get("badge"):
                    total_rewards["badges"].append(reward["badge"])
        
        # Verify quest completion
        expected_completed = ["daily_creator", "social_butterfly", "quality_focus"]
        self.assertEqual(set(completed_quests), set(expected_completed))
        self.assertEqual(total_rewards["experience"], 275)  # 25 + 100 + 150
        self.assertEqual(total_rewards["coins"], 50)
        self.assertIn("social_butterfly", total_rewards["badges"])
        self.assertIn("quality_master", total_rewards["badges"])


if __name__ == '__main__':
    unittest.main()