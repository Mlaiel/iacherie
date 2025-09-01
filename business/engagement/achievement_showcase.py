"""Achievement Showcase System - Display and manage achievement progress for users.

This module provides a comprehensive showcase system for the 50+ achievements,
allowing users to view their progress, unlock status, and achievement details.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .achievement_tracker import AchievementTracker, AchievementCategory, AchievementDifficulty

logger = logging.getLogger(__name__)


class ShowcaseFilter(str, Enum):
    """
Filters for achievement showcase."""

    ALL = "all"
    UNLOCKED = "unlocked"
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BY_CATEGORY = "by_category"
    BY_DIFFICULTY = "by_difficulty"


@dataclass
class AchievementDisplay:
    """Display model for achievements in the showcase."""
    achievement_id: str
    name: str
    description: str
    category: str
    difficulty: str
    experience_points: int
    virtual_currency: int
    real_currency: float
    badge_icon: str
    progress_percentage: float
    status: str
    unlocked_at: Optional[datetime] = None
    estimated_completion: Optional[str] = None
    special_benefits: List[str] = field(default_factory=list)
    next_milestone: Optional[str] = None


class AchievementShowcase:
    """
    Achievement showcase system for displaying user progress.
    
    Provides comprehensive views of all 50+ achievements with filtering,
    sorting, and progress tracking capabilities.
    """
    
    def __init__(self, achievement_tracker: AchievementTracker):
        """
Initialize the achievement showcase."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.tracker = achievement_tracker
        
        # Achievement progression paths
        self.progression_paths = {
            "content_creation": [
                "First Steps", "Content Rookie", "Content Regular", "Content Creator",
                "Content Producer", "Content Master", "Content Virtuoso", 
                "Content Legend", "Legend Creator"
            ],
            "collaboration": [
                "Collaborator", "Team Player", "Partner", "Collaborator Pro",
                "Partnership Master", "Super Collaborator", "Global Connector"
            ],
            "monetization": [
                "First Dollar", "Century Club", "Four Figures", "Five Figures",
                "Revenue Master", "Income Architect"
            ],
            "protection": [
                "Guardian", "Content Shield", "Digital Protector", "IP Guardian",
                "Rights Defender", "IP Defender"
            ]
        }
        
        self.logger.info("AchievementShowcase initialized successfully")
    
    async def get_user_showcase(
        self,
        user_id: str,
        filter_type: ShowcaseFilter = ShowcaseFilter.ALL,
        category: Optional[str] = None,
        include_hidden: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive achievement showcase for a user."""
        try:
            # Initialize user progress if needed
            if user_id not in self.tracker._user_progress:
                await self.tracker._initialize_user_progress(user_id)
            
            user_progress = self.tracker._user_progress[user_id]
            showcase_data = {
                "user_id": user_id,
                "total_achievements": len(self.tracker._achievements),
                "unlocked_count": 0,
                "in_progress_count": 0,
                "total_experience": 0,
                "total_currency": 0,
                "achievements": [],
                "categories": {},
                "progression_summary": {},
                "featured_achievements": [],
                "next_recommendations": []
            }
            
            # Process all achievements
            for achievement_id, achievement in self.tracker._achievements.items():
                # Skip hidden achievements if not requested
                if achievement.hidden and not include_hidden:
                    continue
                
                # Apply category filter
                if category and achievement.category.value != category:
                    continue
                
                # Get user progress for this achievement
                progress = user_progress.get(achievement_id)
                if not progress:
                    continue
                
                # Create display model
                display = self._create_achievement_display(achievement, progress)
                
                # Apply status filter
                if filter_type != ShowcaseFilter.ALL:
                    if filter_type == ShowcaseFilter.UNLOCKED and display.status not in ["completed", "claimed"]:
                        continue
                    elif filter_type == ShowcaseFilter.LOCKED and display.status != "locked":
                        continue
                    elif filter_type == ShowcaseFilter.IN_PROGRESS and display.status != "in_progress":
                        continue
                    elif filter_type == ShowcaseFilter.COMPLETED and display.status not in ["completed", "claimed"]:
                        continue
                
                showcase_data["achievements"].append(display)
                
                # Update statistics
                if display.status in ["completed", "claimed"]:
                    showcase_data["unlocked_count"] += 1
                    showcase_data["total_experience"] += display.experience_points
                    showcase_data["total_currency"] += display.virtual_currency
                elif display.status == "in_progress":
                    showcase_data["in_progress_count"] += 1
            
            # Generate category summaries
            showcase_data["categories"] = self._generate_category_summaries(showcase_data["achievements"])
            
            # Generate progression summaries
            showcase_data["progression_summary"] = self._generate_progression_summaries(user_id, showcase_data["achievements"])
            
            # Get featured achievements
            showcase_data["featured_achievements"] = self._get_featured_achievements(showcase_data["achievements"])
            
            # Get recommendations
            showcase_data["next_recommendations"] = await self._get_achievement_recommendations(user_id, showcase_data["achievements"])
            
            return showcase_data
            
        except Exception as e:
            self.logger.error(f"Error generating achievement showcase: {e}")
            return {}
    
    def _create_achievement_display(self, achievement, progress) -> AchievementDisplay:
        """Create display model for an achievement."""
        return AchievementDisplay(
            achievement_id=achievement.achievement_id,
            name=achievement.name,
            description=achievement.description,
            category=achievement.category.value,
            difficulty=achievement.difficulty.value,
            experience_points=achievement.experience_points,
            virtual_currency=achievement.virtual_currency,
            real_currency=achievement.real_currency,
            badge_icon=achievement.badge_icon,
            progress_percentage=progress.progress_percentage if progress else 0.0,
            status=progress.status.value if progress else "locked",
            unlocked_at=progress.completed_at if progress else None,
            special_benefits=achievement.special_benefits,
            estimated_completion=self._estimate_completion_time(achievement, progress),
            next_milestone=self._get_next_milestone(achievement, progress)
        )
    
    def _generate_category_summaries(self, achievements: List[AchievementDisplay]) -> Dict[str, Any]:
        """Generate summaries for each category."""
        categories = {}
        
        for achievement in achievements:
            category = achievement.category
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "unlocked": 0,
                    "in_progress": 0,
                    "completion_rate": 0.0,
                    "total_xp": 0,
                    "earned_xp": 0
                }
            
            cat_data = categories[category]
            cat_data["total"] += 1
            cat_data["total_xp"] += achievement.experience_points
            
            if achievement.status in ["completed", "claimed"]:
                cat_data["unlocked"] += 1
                cat_data["earned_xp"] += achievement.experience_points
            elif achievement.status == "in_progress":
                cat_data["in_progress"] += 1
            
            # Calculate completion rate
            if cat_data["total"] > 0:
                cat_data["completion_rate"] = (cat_data["unlocked"] / cat_data["total"]) * 100
        
        return categories
    
    def _generate_progression_summaries(self, user_id: str, achievements: List[AchievementDisplay]) -> Dict[str, Any]:
        """Generate progression summaries for main achievement paths."""
        progression_summary = {}
        
        for path_name, path_achievements in self.progression_paths.items():
            unlocked_in_path = [
                ach for ach in achievements 
                if ach.name in path_achievements and ach.status in ["completed", "claimed"]
            ]
            
            current_level = len(unlocked_in_path)
            next_achievement = None
            
            if current_level < len(path_achievements):
                next_name = path_achievements[current_level]
                next_achievement = next((ach for ach in achievements if ach.name == next_name), None)
            
            progression_summary[path_name] = {
                "current_level": current_level,
                "total_levels": len(path_achievements),
                "progress_percentage": (current_level / len(path_achievements)) * 100 if path_achievements else 0,
                "next_achievement": next_achievement.name if next_achievement else None,
                "next_progress": next_achievement.progress_percentage if next_achievement else 0,
                "completed": current_level == len(path_achievements)
            }
        
        return progression_summary
    
    def _get_featured_achievements(self, achievements: List[AchievementDisplay]) -> List[AchievementDisplay]:
        """Get featured achievements to highlight."""
        featured = []
        
        # Recently completed achievements
        recent_completed = [
            ach for ach in achievements 
            if ach.status in ["completed", "claimed"] and ach.unlocked_at
            and ach.unlocked_at > datetime.utcnow() - timedelta(days=7)
        ]
        featured.extend(sorted(recent_completed, key=lambda x: x.unlocked_at, reverse=True)[:3])
        
        # High-progress achievements
        high_progress = [
            ach for ach in achievements 
            if ach.status == "in_progress" and ach.progress_percentage >= 75
        ]
        featured.extend(sorted(high_progress, key=lambda x: x.progress_percentage, reverse=True)[:2])
        
        # Legendary achievements
        legendary = [
            ach for ach in achievements 
            if ach.difficulty == "legendary" and ach.status in ["completed", "claimed"]
        ]
        featured.extend(legendary[:2])
        
        return featured
    
    async def _get_achievement_recommendations(self, user_id: str, achievements: List[AchievementDisplay]) -> List[Dict[str, Any]]:
        """Get personalized achievement recommendations."""
        recommendations = []
        
        # Find achievements close to completion
        close_to_completion = [
            ach for ach in achievements 
            if ach.status == "in_progress" and ach.progress_percentage >= 50
        ]
        
        for ach in sorted(close_to_completion, key=lambda x: x.progress_percentage, reverse=True)[:5]:
            recommendations.append({
                "achievement": ach,
                "reason": f"You're {ach.progress_percentage:.0f}% complete",
                "priority": "high" if ach.progress_percentage >= 80 else "medium",
                "estimated_time": ach.estimated_completion
            })
        
        # Find next achievements in progression paths
        for path_name, progression in self._generate_progression_summaries(user_id, achievements).items():
            if not progression["completed"] and progression["next_achievement"]:
                next_ach = next((ach for ach in achievements if ach.name == progression["next_achievement"]), None)
                if next_ach and next_ach not in [r["achievement"] for r in recommendations]:
                    recommendations.append({
                        "achievement": next_ach,
                        "reason": f"Next step in {path_name.replace('_', ' ').title()} progression",
                        "priority": "medium",
                        "estimated_time": next_ach.estimated_completion
                    })
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _estimate_completion_time(self, achievement, progress) -> Optional[str]:
        """Estimate time to complete achievement."""
        if not progress or progress.status.value in ["completed", "claimed"]:
            return None
        
        if progress.progress_percentage <= 0:
            return "Start now"
        
        # Simple estimation based on progress and difficulty
        difficulty_multipliers = {
            "trivial": 0.5,
            "easy": 1.0,
            "medium": 2.0,
            "hard": 5.0,
            "very_hard": 10.0,
            "legendary": 30.0
        }
        
        base_time = difficulty_multipliers.get(achievement.difficulty.value, 5.0)
        remaining_progress = 100 - progress.progress_percentage
        estimated_days = (remaining_progress / 100) * base_time
        
        if estimated_days < 1:
            return "Less than a day"
        elif estimated_days < 7:
            return f"{int(estimated_days)} day(s)"
        elif estimated_days < 30:
            return f"{int(estimated_days / 7)} week(s)"
        else:
            return f"{int(estimated_days / 30)} month(s)"
    
    def _get_next_milestone(self, achievement, progress) -> Optional[str]:
        """Get next milestone for achievement."""
        if not progress or progress.status.value in ["completed", "claimed"]:
            return None
        
        # For counter-based achievements, show next milestone
        if achievement.achievement_type.value == "counter" and achievement.criteria:
            criteria = achievement.criteria[0]
            current = progress.criteria_progress.get(criteria.criteria_id)
            if current:
                target = criteria.target_value
                current_val = current.current_value
                progress_percent = (current_val / target) * 100 if target > 0 else 0
                
                if progress_percent < 25:
                    return f"Reach 25% ({int(target * 0.25)})"
                elif progress_percent < 50:
                    return f"Reach 50% ({int(target * 0.5)})"
                elif progress_percent < 75:
                    return f"Reach 75% ({int(target * 0.75)})"
                else:
                    return f"Complete ({target})"
        
        return "Keep going!"
    
    async def get_leaderboard_data(self, category: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get leaderboard data for achievements."""
        try:
            leaderboard_data = {
                "category": category or "all",
                "total_users": len(self.tracker._user_progress),
                "leaders": [],
                "category_leaders": {}
            }
            
            # Calculate user scores
            user_scores = {}
            for user_id, user_progress in self.tracker._user_progress.items():
                total_xp = 0
                unlocked_count = 0
                category_scores = {}
                
                for achievement_id, progress in user_progress.items():
                    achievement = self.tracker._achievements.get(achievement_id)
                    if not achievement:
                        continue
                    
                    if progress.status.value in ["completed", "claimed"]:
                        xp = achievement.experience_points
                        total_xp += xp
                        unlocked_count += 1
                        
                        cat = achievement.category.value
                        if cat not in category_scores:
                            category_scores[cat] = {"xp": 0, "count": 0}
                        category_scores[cat]["xp"] += xp
                        category_scores[cat]["count"] += 1
                
                user_scores[user_id] = {
                    "user_id": user_id,
                    "total_xp": total_xp,
                    "unlocked_count": unlocked_count,
                    "category_scores": category_scores
                }
            
            # Sort and get top leaders
            if category:
                # Category-specific leaderboard
                leaders = sorted(
                    user_scores.values(),
                    key=lambda x: x["category_scores"].get(category, {}).get("xp", 0),
                    reverse=True
                )[:limit]
            else:
                # Overall leaderboard
                leaders = sorted(
                    user_scores.values(),
                    key=lambda x: x["total_xp"],
                    reverse=True
                )[:limit]
            
            leaderboard_data["leaders"] = leaders
            
            return leaderboard_data
            
        except Exception as e:
            self.logger.error(f"Error generating leaderboard data: {e}")
            return {}


async def get_achievement_showcase(user_id: str, achievement_tracker: AchievementTracker) -> AchievementShowcase:
    """Factory function to get achievement showcase instance."""
    return AchievementShowcase(achievement_tracker)