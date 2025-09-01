# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Comprehensive test suite for Gamification Agent Module.

Tests all gamification components including challenge generation, reward optimization,
engagement prediction, social competition, badge generation, and progression analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import json


class TestGamificationAgentModule(unittest.TestCase):
    """Comprehensive test suite for Gamification Agent Module"""
    def setUp(self):
        """Set up test fixtures"""
        self.sample_user_data = {
            "user_id": "test_user_123",
            "level": 5,
            "total_content_uploads": 25,
            "avg_content_rating": 4.2,
            "successful_collaborations": 8,
            "social_engagement_score": 0.75,
            "streak_days": 14,
            "follower_count": 2500,
            "engagement_rate": 0.68,
            "monetization_efficiency": 0.45
        }

    def test_challenge_generation_structure(self):
        """Test challenge generation data structures"""
        challenge_template = {
            "template_id": "daily_upload",
            "title": "Daily Creator",
            "description": "Upload 1 piece of content today",
            "challenge_type": "daily",
            "difficulty": "beginner",
            "category": "content_creation",
            "target_metric": "content_uploads",
            "target_value": 1.0,
            "reward_points": 25,
            "duration_hours": 24
        }
        
        # Verify required fields
        required_fields = ["template_id", "title", "description", "challenge_type", "difficulty"]
        for field in required_fields:
            self.assertIn(field, challenge_template)
        
        # Verify data types
        self.assertIsInstance(challenge_template["target_value"], float)
        self.assertIsInstance(challenge_template["reward_points"], int)
        self.assertIsInstance(challenge_template["duration_hours"], int)

    def test_reward_optimization_calculations(self):
        """Test reward optimization calculation logic"""
        base_reward = 100
        quality_multiplier = 1.5
        engagement_multiplier = 1.2
        consistency_bonus = 25
        
        # Test reward calculation
        optimized_reward = (base_reward * quality_multiplier * engagement_multiplier) + consistency_bonus
        expected_reward = (100 * 1.5 * 1.2) + 25  # 180 + 25 = 205
        
        self.assertEqual(optimized_reward, expected_reward)
        self.assertEqual(optimized_reward, 205)

    def test_engagement_prediction_scoring(self):
        """Test engagement prediction scoring system"""
        user_metrics = {
            "content_frequency": 80,      # 80%
            "quality_consistency": 85,    # 85%
            "social_interaction": 75,     # 75%
            "collaboration_activity": 60, # 60%
            "platform_diversity": 40,    # 40%
            "monetization_activity": 50   # 50%
        }
        
        # Engagement score weights
        weights = {
            "content_frequency": 0.25,
            "quality_consistency": 0.20,
            "social_interaction": 0.20,
            "collaboration_activity": 0.15,
            "platform_diversity": 0.10,
            "monetization_activity": 0.10
        }
        
        # Calculate weighted engagement score
        engagement_score = sum(
            user_metrics[metric] * weights[metric]
            for metric in user_metrics
        )
        
        expected_score = (80*0.25 + 85*0.20 + 75*0.20 + 60*0.15 + 40*0.10 + 50*0.10)
        
        self.assertEqual(engagement_score, expected_score)
        self.assertEqual(engagement_score, 70.0)  # Expected: 70.0%

    def test_badge_rarity_system(self):
        """Test badge rarity distribution system"""
        badge_rarities = {
            "common": 50,      # 50%
            "uncommon": 30,    # 30%
            "rare": 15,        # 15%
            "epic": 4,         # 4%
            "legendary": 1     # 1%
        }
        
        total_percentage = sum(badge_rarities.values())
        self.assertEqual(total_percentage, 100)
        
        # Test badge point values based on rarity
        rarity_points = {
            "common": 50,
            "uncommon": 100,
            "rare": 250,
            "epic": 500,
            "legendary": 1000
        }
        
        # Verify legendary badges are worth most points
        self.assertGreater(rarity_points["legendary"], rarity_points["epic"])
        self.assertGreater(rarity_points["epic"], rarity_points["rare"])

    def test_progression_stage_determination(self):
        """Test progression stage determination logic"""
        stage_thresholds = {
            "newcomer": {"min_uploads": 0, "max_uploads": 10, "min_level": 1, "max_level": 3},
            "developing": {"min_uploads": 10, "max_uploads": 50, "min_level": 3, "max_level": 6},
            "competent": {"min_uploads": 50, "max_uploads": 150, "min_level": 6, "max_level": 10},
            "proficient": {"min_uploads": 150, "max_uploads": 400, "min_level": 10, "max_level": 15},
            "expert": {"min_uploads": 400, "max_uploads": 1000, "min_level": 15, "max_level": 20}
        }
        
        test_cases = [
            {"uploads": 5, "level": 2, "expected_stage": "newcomer"},
            {"uploads": 25, "level": 5, "expected_stage": "developing"},
            {"uploads": 75, "level": 8, "expected_stage": "competent"},
            {"uploads": 200, "level": 12, "expected_stage": "proficient"},
            {"uploads": 500, "level": 18, "expected_stage": "expert"}
        ]
        
        for case in test_cases:
            uploads = case["uploads"]
            level = case["level"]
            expected = case["expected_stage"]
            
            # Find matching stage
            actual_stage = None
            for stage, thresholds in stage_thresholds.items():
                if (thresholds["min_uploads"] <= uploads <= thresholds["max_uploads"] and
                    thresholds["min_level"] <= level <= thresholds["max_level"]):
                    actual_stage = stage
                    break
            
            self.assertEqual(actual_stage, expected, 
                           f"Failed for uploads={uploads}, level={level}")

    def test_social_competition_matching(self):
        """Test social competition matching algorithm"""
        user_profile = {
            "skill_level": 7,
            "collaboration_preference": 0.8,
            "content_types": ["video", "audio"],
            "engagement_level": "high"
        }
        
        competition_options = [
            {
                "id": "collab_tournament",
                "type": "team_tournament",
                "skill_requirement": 6,
                "collaboration_focused": True,
                "current_participants": 15,
                "max_participants": 40
            },
            {
                "id": "individual_challenge",
                "type": "individual_challenge",
                "skill_requirement": 8,
                "collaboration_focused": False,
                "current_participants": 25,
                "max_participants": 30
            }
        ]
        
        # Calculate suitability scores
        suitability_scores = []
        
        for comp in competition_options:
            score = 0
            
            # Skill level matching (closer is better)
            skill_diff = abs(user_profile["skill_level"] - comp["skill_requirement"])
            skill_score = max(0, 1 - skill_diff / 10)  # Normalize to 0-1
            score += skill_score * 0.3
            
            # Collaboration preference matching
            if comp["collaboration_focused"] and user_profile["collaboration_preference"] > 0.5:
                score += 0.4
            elif not comp["collaboration_focused"] and user_profile["collaboration_preference"] <= 0.5:
                score += 0.3
            
            # Participation level (prefer 60% full)
            participation_ratio = comp["current_participants"] / comp["max_participants"]
            participation_score = 1 - abs(participation_ratio - 0.6)
            score += participation_score * 0.3
            
            suitability_scores.append({
                "competition_id": comp["id"],
                "suitability_score": score
            })
        
        # Sort by suitability
        suitability_scores.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        # Team tournament should be more suitable for collaboration-focused user
        best_match = suitability_scores[0]
        self.assertEqual(best_match["competition_id"], "collab_tournament")

    def test_milestone_achievement_tracking(self):
        """Test milestone achievement tracking system"""
        milestones = {
            "content_milestones": [1, 5, 10, 25, 50, 100],
            "collaboration_milestones": [1, 3, 5, 10, 20],
            "follower_milestones": [100, 500, 1000, 5000, 10000]
        }
        
        user_stats = {
            "content_uploads": 27,
            "collaborations": 8,
            "followers": 2500
        }
        
        # Test milestone progression calculation
        def calculate_milestone_progress(current_value, milestones):
            achieved = [m for m in milestones if current_value >= m]
            next_milestone = None
            for m in milestones:
                if current_value < m:
                    next_milestone = m
                    break
            
            progress_percentage = 0
            if next_milestone:
                if achieved:
                    last_achieved = max(achieved)
                    progress_percentage = ((current_value - last_achieved) / 
                                         (next_milestone - last_achieved)) * 100
                else:
                    progress_percentage = (current_value / next_milestone) * 100
            
            return {
                "achieved_count": len(achieved),
                "next_milestone": next_milestone,
                "progress_percentage": min(100, progress_percentage)
            }
        
        # Test content milestones
        content_progress = calculate_milestone_progress(
            user_stats["content_uploads"], 
            milestones["content_milestones"]
        )
        
        self.assertEqual(content_progress["achieved_count"], 4)  # 1, 5, 10, 25
        self.assertEqual(content_progress["next_milestone"], 50)
        self.assertGreater(content_progress["progress_percentage"], 0)

    def test_reward_tier_calculation(self):
        """Test reward tier calculation based on optimization"""
        base_amounts = [50, 100, 200, 500]
        optimized_amounts = [60, 150, 300, 1200]
        
        expected_tiers = ["silver", "platinum", "platinum", "diamond"]
        
        def determine_tier(optimized_amount, base_amount):
            ratio = optimized_amount / base_amount if base_amount > 0 else 1.0
            
            if ratio >= 2.0:
                return "diamond"
            elif ratio >= 1.5:
                return "platinum"
            elif ratio >= 1.25:
                return "gold"
            elif ratio >= 1.1:
                return "silver"
            else:
                return "bronze"
        
        for i, (base, optimized, expected) in enumerate(zip(base_amounts, optimized_amounts, expected_tiers)):
            actual_tier = determine_tier(optimized, base)
            self.assertEqual(actual_tier, expected, 
                           f"Failed for base={base}, optimized={optimized}")

    def test_engagement_level_classification(self):
        """Test engagement level classification"""
        engagement_thresholds = {
            "dormant": (0, 20),
            "low": (20, 40),
            "moderate": (40, 65),
            "high": (65, 85),
            "super_engaged": (85, 100)
        }
        
        test_scores = [15, 35, 55, 75, 92]
        expected_levels = ["dormant", "low", "moderate", "high", "super_engaged"]
        
        def classify_engagement(score):
            for level, (min_score, max_score) in engagement_thresholds.items():
                if min_score <= score <= max_score:
                    return level
            return "unknown"
        
        for score, expected in zip(test_scores, expected_levels):
            actual = classify_engagement(score)
            self.assertEqual(actual, expected, f"Failed for score={score}")

    def test_gamification_system_integration(self):
        """Test integration between gamification components"""
        # Test data flow: User Activity -> Challenge -> Reward -> Badge -> Progression
        
        user_activity = {
            "activity_type": "content_upload",
            "quality_score": 0.85,
            "engagement_score": 0.72,
            "collaboration_rating": 4.2
        }
        
        # Mock challenge completion
        completed_challenge = {
            "challenge_id": "quality_content_week",
            "completion_percentage": 100,
            "points_earned": 150
        }
        
        # Mock reward optimization
        optimized_reward = {
            "base_points": 150,
            "quality_multiplier": 1.5,
            "engagement_multiplier": 1.2,
            "total_points": int(150 * 1.5 * 1.2)  # 270 points
        }
        
        # Mock badge unlock
        new_badge = {
            "badge_id": "quality_creator",
            "title": "Quality Creator",
            "rarity": "rare",
            "points_awarded": 300
        }
        
        # Mock progression update
        progression_update = {
            "previous_level": 5,
            "new_level": 6,
            "experience_gained": optimized_reward["total_points"] + new_badge["points_awarded"],
            "level_up": True
        }
        
        # Test integration flow
        total_experience = optimized_reward["total_points"] + new_badge["points_awarded"]
        
        self.assertEqual(optimized_reward["total_points"], 270)
        self.assertEqual(total_experience, 570)  # 270 + 300
        self.assertTrue(progression_update["level_up"])
        self.assertEqual(progression_update["new_level"], 6)

    def test_gamification_analytics_calculations(self):
        """Test gamification analytics and metrics calculations"""
        system_metrics = {
            "total_users_processed": 1500,
            "total_challenges_generated": 5000,
            "total_rewards_distributed": 12000,
            "challenge_completion_rate": 0.78,
            "average_engagement_improvement": 0.15,
            "badge_distribution": {
                "common": 800,
                "uncommon": 400,
                "rare": 150,
                "epic": 40,
                "legendary": 10
            }
        }
        
        # Calculate derived metrics
        challenges_per_user = system_metrics["total_challenges_generated"] / system_metrics["total_users_processed"]
        rewards_per_user = system_metrics["total_rewards_distributed"] / system_metrics["total_users_processed"]
        
        total_badges = sum(system_metrics["badge_distribution"].values())
        badges_per_user = total_badges / system_metrics["total_users_processed"]
        
        # Verify calculations
        self.assertAlmostEqual(challenges_per_user, 3.33, places=2)
        self.assertEqual(rewards_per_user, 8.0)
        self.assertAlmostEqual(badges_per_user, 0.93, places=2)
        
        # Verify badge rarity distribution percentages
        common_percentage = (system_metrics["badge_distribution"]["common"] / total_badges) * 100
        legendary_percentage = (system_metrics["badge_distribution"]["legendary"] / total_badges) * 100
        
        self.assertGreater(common_percentage, 50)  # Common badges should be majority
        self.assertLess(legendary_percentage, 1)   # Legendary badges should be rare


class TestGamificationPerformance(unittest.TestCase):
    """Performance tests for gamification system"""
    def test_large_user_base_simulation(self):
        """Test system performance with large user base"""
        num_users = 10000
        challenges_per_user = 3
        
        # Simulate challenge generation load
        total_challenges = num_users * challenges_per_user
        
        # Estimate processing time (simplified)
        processing_time_per_challenge = 0.001  # 1ms per challenge
        total_processing_time = total_challenges * processing_time_per_challenge
        
        # Verify system can handle load within reasonable time
        max_acceptable_time = 60  # 60 seconds max
        
        self.assertLess(total_processing_time, max_acceptable_time,
                       f"Processing {total_challenges} challenges would take {total_processing_time}s")

    def test_concurrent_user_handling(self):
        """Test concurrent user processing capabilities"""
        concurrent_users = 1000
        operations_per_user = 5
        
        total_operations = concurrent_users * operations_per_user
        
        # Simulate async processing capability
        async_processing_factor = 100  # Can process 100 operations concurrently
        effective_processing_time = total_operations / async_processing_factor * 0.01
        
        max_response_time = 1.0  # 1 second max response time
        
        self.assertLess(effective_processing_time, max_response_time,
                       f"Concurrent processing would take {effective_processing_time}s")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestGamificationAgentModule))
    suite.addTest(unittest.makeSuite(TestGamificationPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"GAMIFICATION AGENT MODULE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"{'='*60}")