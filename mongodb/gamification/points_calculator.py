"""MongoDB Points Calculator
=========================

Advanced points and scoring system for gamification in the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import math

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)

class PointsCategory(Enum):
    """Points categories."""
    CONTENT = "content"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    SOCIAL = "social"
    LEARNING = "learning"
    ACHIEVEMENT = "achievement"
    BONUS = "bonus"
    PENALTY = "penalty"

class PointsMultiplier(Enum):
    """Points multiplier reasons."""
    STREAK_BONUS = "streak_bonus"
    QUALITY_BONUS = "quality_bonus"
    VIRAL_BONUS = "viral_bonus"
    PREMIUM_BONUS = "premium_bonus"
    EVENT_BONUS = "event_bonus"
    PENALTY_REDUCTION = "penalty_reduction"

@dataclass
class PointsRule:
    """Points calculation rule."""
    rule_id: str
    name: str
    category: PointsCategory
    base_points: int
    multiplier_conditions: Dict[str, Any]
    max_daily_points: Optional[int] = None
    cooldown_hours: Optional[int] = None
    enabled: bool = True

@dataclass
class PointsTransaction:
    """Points transaction record."""
    transaction_id: str
    user_id: str
    category: PointsCategory
    points_change: int
    reason: str
    reference_id: Optional[str]
    multipliers_applied: List[Dict[str, Any]]
    timestamp: datetime
    metadata: Dict[str, Any]

class PointsCalculator:
    """Enterprise-grade points calculation system."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize points calculator."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for points calculation")
            
        self.client = client
        self.database = client[database_name]
        
        # Collections
        self.points_rules_collection = self.database['points_rules']
        self.points_transactions_collection = self.database['points_transactions']
        self.user_points_collection = self.database['user_points']
        self.points_multipliers_collection = self.database['points_multipliers']
        
        # Configuration
        self.max_daily_points_default = 10000
        self.streak_multiplier_base = 1.1
        self.quality_score_threshold = 0.8
        self.viral_view_threshold = 100000
        
        # Initialize default rules
        self._ensure_default_rules()
    
    def _ensure_default_rules(self):
        """Ensure default points rules exist."""
        default_rules = [
            PointsRule(
                rule_id="content_upload_base",
                name="Content Upload Base Points",
                category=PointsCategory.CONTENT,
                base_points=50,
                multiplier_conditions={
                    "quality_score": {"min": 0.7, "multiplier": 1.5},
                    "first_upload_today": {"multiplier": 2.0}
                },
                max_daily_points=500,
                cooldown_hours=1
            ),
            PointsRule(
                rule_id="content_view_points",
                name="Content View Points",
                category=PointsCategory.ENGAGEMENT,
                base_points=1,
                multiplier_conditions={
                    "viral_threshold": {"min_views": 100000, "multiplier": 10.0},
                    "trending": {"multiplier": 3.0}
                },
                max_daily_points=1000
            ),
            PointsRule(
                rule_id="collaboration_completion",
                name="Collaboration Completion",
                category=PointsCategory.COLLABORATION,
                base_points=200,
                multiplier_conditions={
                    "project_size": {"min_collaborators": 5, "multiplier": 1.5},
                    "success_rating": {"min": 4.0, "multiplier": 2.0}
                },
                max_daily_points=2000
            ),
            PointsRule(
                rule_id="revenue_generation",
                name="Revenue Generation",
                category=PointsCategory.REVENUE,
                base_points=100,
                multiplier_conditions={
                    "milestone_reached": {"multiplier": 5.0},
                    "recurring_revenue": {"multiplier": 2.0}
                }
            ),
            PointsRule(
                rule_id="social_engagement",
                name="Social Engagement",
                category=PointsCategory.SOCIAL,
                base_points=5,
                multiplier_conditions={
                    "engagement_rate": {"min": 0.05, "multiplier": 2.0},
                    "cross_platform": {"multiplier": 1.5}
                },
                max_daily_points=200
            ),
            PointsRule(
                rule_id="achievement_unlock",
                name="Achievement Unlock",
                category=PointsCategory.ACHIEVEMENT,
                base_points=0,  # Points come from achievement itself
                multiplier_conditions={
                    "rare_achievement": {"multiplier": 2.0},
                    "first_in_category": {"multiplier": 1.5}
                }
            ),
            PointsRule(
                rule_id="learning_progress",
                name="Learning Progress",
                category=PointsCategory.LEARNING,
                base_points=25,
                multiplier_conditions={
                    "completion_streak": {"multiplier": 1.2},
                    "perfect_score": {"multiplier": 2.0}
                },
                max_daily_points=300
            )
        ]
        
        # Insert rules if they don't exist
        for rule in default_rules:
            existing = self.points_rules_collection.find_one({"rule_id": rule.rule_id})
            if not existing:
                self.points_rules_collection.insert_one(asdict(rule))
                logger.info(f"Created default points rule: {rule.name}")
    
    def calculate_points(self, user_id: str, action: str, context: Dict[str, Any]) -> PointsTransaction:
        """Calculate points for a user action."""
        try:
            # Find applicable rule
            rule = self._find_applicable_rule(action, context)
            if not rule:
                logger.warning(f"No points rule found for action: {action}")
                return None
            
            # Check cooldown
            if rule.cooldown_hours and self._is_in_cooldown(user_id, rule.rule_id, rule.cooldown_hours):
                logger.debug(f"Action {action} is in cooldown for user {user_id}")
                return None
            
            # Calculate base points
            base_points = rule.base_points
            
            # Apply context-specific multipliers
            multipliers_applied = []
            total_multiplier = 1.0
            
            for condition_key, condition_value in rule.multiplier_conditions.items():
                multiplier = self._check_multiplier_condition(condition_key, condition_value, context)
                if multiplier > 1.0:
                    multipliers_applied.append({
                        "condition": condition_key,
                        "multiplier": multiplier,
                        "reason": f"Condition {condition_key} met"
                    })
                    total_multiplier *= multiplier
            
            # Apply user-specific multipliers (streaks, premium, etc.)
            user_multipliers = self._get_user_multipliers(user_id, rule.category)
            for multiplier_data in user_multipliers:
                multipliers_applied.append(multiplier_data)
                total_multiplier *= multiplier_data["multiplier"]
            
            # Calculate final points
            final_points = int(base_points * total_multiplier)
            
            # Apply daily limits
            if rule.max_daily_points:
                daily_points = self._get_daily_points(user_id, rule.category)
                if daily_points + final_points > rule.max_daily_points:
                    final_points = max(0, rule.max_daily_points - daily_points)
                    
                    if final_points < base_points:
                        multipliers_applied.append({
                            "condition": "daily_limit",
                            "multiplier": final_points / base_points if base_points > 0 else 0,
                            "reason": "Daily points limit applied"
                        })
            
            # Create transaction
            transaction = PointsTransaction(
                transaction_id=self._generate_transaction_id(),
                user_id=user_id,
                category=rule.category,
                points_change=final_points,
                reason=f"{rule.name}: {action}",
                reference_id=context.get("reference_id"),
                multipliers_applied=multipliers_applied,
                timestamp=datetime.now(),
                metadata=context.copy()
            )
            
            # Record transaction and update user points
            if final_points > 0:
                self._record_transaction(transaction)
                self._update_user_points(user_id, final_points, rule.category)
            
            logger.info(f"Awarded {final_points} points to user {user_id} for {action}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to calculate points for {action}: {e}")
            return None
    
    def _find_applicable_rule(self, action: str, context: Dict[str, Any]) -> Optional[PointsRule]:
        """Find the applicable points rule for an action."""
        # Map actions to rule IDs (simplified mapping)
        action_rule_map = {
            "content_upload": "content_upload_base",
            "content_view": "content_view_points",
            "collaboration_complete": "collaboration_completion",
            "revenue_earned": "revenue_generation",
            "social_interaction": "social_engagement",
            "achievement_earned": "achievement_unlock",
            "learning_completed": "learning_progress"
        }
        
        rule_id = action_rule_map.get(action)
        if not rule_id:
            return None
        
        rule_data = self.points_rules_collection.find_one({"rule_id": rule_id, "enabled": True})
        if not rule_data:
            return None
        
        # Convert to PointsRule object
        rule_data["category"] = PointsCategory(rule_data["category"])
        rule_data.pop("_id", None)
        
        return PointsRule(**rule_data)
    
    def _check_multiplier_condition(self, condition_key: str, condition_value: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Check if a multiplier condition is met and return the multiplier."""
        try:
            if condition_key == "quality_score":
                quality_score = context.get("quality_score", 0)
                min_score = condition_value.get("min", 0)
                if quality_score >= min_score:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "viral_threshold":
                views = context.get("views", 0)
                min_views = condition_value.get("min_views", 0)
                if views >= min_views:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "first_upload_today":
                is_first = context.get("first_upload_today", False)
                if is_first:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "project_size":
                collaborators = context.get("collaborators_count", 0)
                min_collaborators = condition_value.get("min_collaborators", 0)
                if collaborators >= min_collaborators:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "success_rating":
                rating = context.get("success_rating", 0)
                min_rating = condition_value.get("min", 0)
                if rating >= min_rating:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "engagement_rate":
                engagement_rate = context.get("engagement_rate", 0)
                min_rate = condition_value.get("min", 0)
                if engagement_rate >= min_rate:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "trending":
                is_trending = context.get("is_trending", False)
                if is_trending:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "cross_platform":
                is_cross_platform = context.get("cross_platform", False)
                if is_cross_platform:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "milestone_reached":
                is_milestone = context.get("milestone_reached", False)
                if is_milestone:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "recurring_revenue":
                is_recurring = context.get("is_recurring", False)
                if is_recurring:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "rare_achievement":
                rarity = context.get("achievement_rarity", "common")
                if rarity in ["rare", "epic", "legendary"]:
                    return condition_value.get("multiplier", 1.0)
            
            elif condition_key == "completion_streak":
                streak = context.get("completion_streak", 0)
                if streak > 1:
                    return min(2.0, 1.0 + (streak - 1) * 0.1)
            
            elif condition_key == "perfect_score":
                is_perfect = context.get("perfect_score", False)
                if is_perfect:
                    return condition_value.get("multiplier", 1.0)
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error checking multiplier condition {condition_key}: {e}")
            return 1.0
    
    def _get_user_multipliers(self, user_id: str, category: PointsCategory) -> List[Dict[str, Any]]:
        """Get user-specific multipliers (streaks, premium status, etc.)."""
        multipliers = []
        
        try:
            # Streak multiplier
            streak_days = self._get_user_streak(user_id, category)
            if streak_days > 1:
                streak_multiplier = min(3.0, 1.0 + (streak_days - 1) * 0.1)
                multipliers.append({
                    "condition": "streak_bonus",
                    "multiplier": streak_multiplier,
                    "reason": f"{streak_days}-day streak bonus"
                })
            
            # Premium multiplier
            if self._is_premium_user(user_id):
                multipliers.append({
                    "condition": "premium_bonus",
                    "multiplier": 1.5,
                    "reason": "Premium member bonus"
                })
            
            # Event multiplier (if active event)
            event_multiplier = self._get_active_event_multiplier(category)
            if event_multiplier > 1.0:
                multipliers.append({
                    "condition": "event_bonus",
                    "multiplier": event_multiplier,
                    "reason": "Special event bonus"
                })
            
            return multipliers
            
        except Exception as e:
            logger.error(f"Error getting user multipliers: {e}")
            return []
    
    def _get_user_streak(self, user_id: str, category: PointsCategory) -> int:
        """Get user's current streak for a category."""
        try:
            # Look at last 30 days of transactions
            cutoff_date = datetime.now() - timedelta(days=30)
            
            transactions = list(
                self.points_transactions_collection.find({
                    "user_id": user_id,
                    "category": category.value,
                    "timestamp": {"$gte": cutoff_date}
                }).sort("timestamp", -1)
            )
            
            if not transactions:
                return 0
            
            # Count consecutive days with points
            streak = 0
            last_date = None
            
            for transaction in transactions:
                transaction_date = transaction["timestamp"].date()
                
                if last_date is None:
                    # First transaction
                    last_date = transaction_date
                    streak = 1
                elif (last_date - transaction_date).days == 1:
                    # Consecutive day
                    streak += 1
                    last_date = transaction_date
                elif transaction_date == last_date:
                    # Same day, continue
                    continue
                else:
                    # Streak broken
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating user streak: {e}")
            return 0
    
    def _is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium status."""
        # This would integrate with user subscription system
        # For now, return False as placeholder
        return False
    
    def _get_active_event_multiplier(self, category: PointsCategory) -> float:
        """Get active event multiplier for category."""
        try:
            # Check for active events
            active_events = list(
                self.points_multipliers_collection.find({
                    "category": category.value,
                    "start_date": {"$lte": datetime.now()},
                    "end_date": {"$gte": datetime.now()},
                    "active": True
                })
            )
            
            # Return highest multiplier if multiple events
            max_multiplier = 1.0
            for event in active_events:
                max_multiplier = max(max_multiplier, event.get("multiplier", 1.0))
            
            return max_multiplier
            
        except Exception as e:
            logger.error(f"Error getting event multiplier: {e}")
            return 1.0
    
    def _is_in_cooldown(self, user_id: str, rule_id: str, cooldown_hours: int) -> bool:
        """Check if user is in cooldown for a specific rule."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=cooldown_hours)
            
            recent_transaction = self.points_transactions_collection.find_one({
                "user_id": user_id,
                "metadata.rule_id": rule_id,
                "timestamp": {"$gte": cutoff_time}
            })
            
            return recent_transaction is not None
            
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    def _get_daily_points(self, user_id: str, category: PointsCategory) -> int:
        """Get points earned today in a specific category."""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "category": category.value,
                        "timestamp": {"$gte": today_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_points": {"$sum": "$points_change"}
                    }
                }
            ]
            
            result = list(self.points_transactions_collection.aggregate(pipeline))
            return result[0]["total_points"] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting daily points: {e}")
            return 0
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        import time
        timestamp = int(time.time() * 1000000)
        return f"pts_{timestamp}"
    
    def _record_transaction(self, transaction: PointsTransaction):
        """Record points transaction in database."""
        try:
            self.points_transactions_collection.insert_one(asdict(transaction))
        except Exception as e:
            logger.error(f"Failed to record transaction: {e}")
    
    def _update_user_points(self, user_id: str, points: int, category: PointsCategory):
        """Update user's total points."""
        try:
            # Update total points
            self.user_points_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "total_points": points,
                        f"category_points.{category.value}": points
                    },
                    "$set": {"last_updated": datetime.now()}
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to update user points: {e}")
    
    def get_user_points(self, user_id: str) -> Dict[str, Any]:
        """Get user's current points breakdown."""
        try:
            user_points = self.user_points_collection.find_one({"user_id": user_id})
            
            if not user_points:
                return {
                    "user_id": user_id,
                    "total_points": 0,
                    "category_points": {},
                    "rank": None,
                    "last_updated": None
                }
            
            # Calculate rank
            rank = self._calculate_user_rank(user_id, user_points["total_points"])
            
            user_points["rank"] = rank
            user_points.pop("_id", None)
            
            return user_points
            
        except Exception as e:
            logger.error(f"Failed to get user points: {e}")
            return {}
    
    def _calculate_user_rank(self, user_id: str, total_points: int) -> int:
        """Calculate user's rank based on total points."""
        try:
            higher_users = self.user_points_collection.count_documents({
                "total_points": {"$gt": total_points}
            })
            
            return higher_users + 1
            
        except Exception as e:
            logger.error(f"Error calculating user rank: {e}")
            return 0
    
    def get_points_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's points transaction history."""
        try:
            transactions = list(
                self.points_transactions_collection.find(
                    {"user_id": user_id}
                ).sort("timestamp", -1).limit(limit)
            )
            
            # Remove MongoDB _id field
            for transaction in transactions:
                transaction.pop("_id", None)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get points history: {e}")
            return []
    
    def adjust_user_points(self, user_id: str, points_change: int, reason: str, admin_id: str) -> PointsTransaction:
        """Manually adjust user points (admin function)."""
        try:
            transaction = PointsTransaction(
                transaction_id=self._generate_transaction_id(),
                user_id=user_id,
                category=PointsCategory.BONUS if points_change > 0 else PointsCategory.PENALTY,
                points_change=points_change,
                reason=f"Manual adjustment: {reason}",
                reference_id=None,
                multipliers_applied=[],
                timestamp=datetime.now(),
                metadata={"admin_id": admin_id, "manual_adjustment": True}
            )
            
            self._record_transaction(transaction)
            self._update_user_points(user_id, points_change, transaction.category)
            
            logger.info(f"Admin {admin_id} adjusted {points_change} points for user {user_id}: {reason}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to adjust user points: {e}")
            return None

# Export the main class
__all__ = ['PointsCalculator', 'PointsRule', 'PointsTransaction', 'PointsCategory', 'PointsMultiplier']