"""Point System - Comprehensive Points Calculation and Management
===============================================================

Advanced points calculation system providing dynamic point allocation,
multipliers, bonuses, and comprehensive point tracking for content
creators across all platform activities.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/rewards/point_system.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math

logger = logging.getLogger(__name__)


class PointCategory(str, Enum):
    """Point categories for different activities."""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    DAILY_ACTIVITY = "daily_activity"
    SPECIAL_EVENT = "special_event"


class MultiplierType(str, Enum):
    """Types of point multipliers."""
    STREAK = "streak"
    TIER = "tier"
    QUALITY = "quality"
    COLLABORATION = "collaboration"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    ACHIEVEMENT_BONUS = "achievement_bonus"
    PREMIUM = "premium"


@dataclass
class PointRule:
    """Point calculation rule definition."""
    id: str
    name: str
    category: PointCategory
    base_points: float
    action_type: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    multipliers: Dict[str, float] = field(default_factory=dict)
    max_daily_points: Optional[float] = None
    max_weekly_points: Optional[float] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PointMultiplier:
    """Point multiplier configuration."""
    id: str
    name: str
    multiplier_type: MultiplierType
    value: float
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    is_active: bool = True


@dataclass
class PointTransaction:
    """Point transaction record."""
    id: str
    user_id: str
    category: PointCategory
    action_type: str
    base_points: float
    multiplier: float
    final_points: float
    source_rule_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserPointBalance:
    """User's point balance and statistics."""
    user_id: str
    total_points: float = 0.0
    category_points: Dict[str, float] = field(default_factory=dict)
    lifetime_earned: float = 0.0
    points_spent: float = 0.0
    daily_points: float = 0.0
    weekly_points: float = 0.0
    monthly_points: float = 0.0
    current_streak: int = 0
    max_streak: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    multipliers_active: List[str] = field(default_factory=list)


class PointSystem:
    """
    Comprehensive point calculation and management system.
    
    Provides dynamic point allocation, multipliers, bonuses, streaks,
    and comprehensive point tracking for all platform activities.
    """
    
    def __init__(self):
        """Initialize the point system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Point rules and configurations
        self.point_rules: Dict[str, PointRule] = {}
        self.multipliers: Dict[str, PointMultiplier] = {}
        
        # User point balances
        self.user_balances: Dict[str, UserPointBalance] = {}
        
        # Transaction history
        self.transactions: Dict[str, List[PointTransaction]] = {}
        
        # Daily/weekly tracking
        self.daily_points: Dict[str, Dict[str, float]] = {}  # user_id -> date -> points
        self.weekly_points: Dict[str, Dict[str, float]] = {}  # user_id -> week -> points
        
        # Streak tracking
        self.streak_data: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("PointSystem initialized")
    
    async def initialize(self) -> bool:
        """Initialize the point system with default rules and multipliers."""
        try:
            # Load default point rules
            await self._load_default_point_rules()
            
            # Load default multipliers
            await self._load_default_multipliers()
            
            # Start background tasks
            asyncio.create_task(self._daily_reset_task())
            asyncio.create_task(self._cleanup_expired_multipliers())
            
            self.initialized = True
            self.logger.info(f"✅ PointSystem initialized with {len(self.point_rules)} rules and {len(self.multipliers)} multipliers")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize PointSystem: {e}")
            return False
    
    async def _load_default_point_rules(self):
        """Load default point calculation rules."""
        default_rules = [
            # Content Creation Points
            PointRule(
                id="content_upload",
                name="Content Upload",
                category=PointCategory.CONTENT_CREATION,
                base_points=50.0,
                action_type="content_upload",
                conditions={"content_type": "any"},
                max_daily_points=500.0
            ),
            PointRule(
                id="high_quality_content",
                name="High Quality Content",
                category=PointCategory.QUALITY,
                base_points=100.0,
                action_type="quality_milestone",
                conditions={"quality_score": {"min": 0.8}},
                max_daily_points=1000.0
            ),
            PointRule(
                id="viral_content",
                name="Viral Content",
                category=PointCategory.ENGAGEMENT,
                base_points=500.0,
                action_type="viral_content",
                conditions={"views": {"min": 10000}},
                max_weekly_points=2000.0
            ),
            
            # Collaboration Points
            PointRule(
                id="collaboration_start",
                name="Collaboration Started",
                category=PointCategory.COLLABORATION,
                base_points=75.0,
                action_type="collaboration_started",
                conditions={},
                max_daily_points=300.0
            ),
            PointRule(
                id="collaboration_success",
                name="Successful Collaboration",
                category=PointCategory.COLLABORATION,
                base_points=200.0,
                action_type="collaboration_success",
                conditions={},
                max_weekly_points=1000.0
            ),
            
            # Engagement Points
            PointRule(
                id="high_engagement",
                name="High Engagement Rate",
                category=PointCategory.ENGAGEMENT,
                base_points=150.0,
                action_type="engagement_milestone",
                conditions={"engagement_rate": {"min": 0.15}},
                max_daily_points=600.0
            ),
            PointRule(
                id="audience_growth",
                name="Audience Growth",
                category=PointCategory.ENGAGEMENT,
                base_points=25.0,
                action_type="follower_gained",
                conditions={},
                max_daily_points=250.0
            ),
            
            # Monetization Points
            PointRule(
                id="first_revenue",
                name="First Revenue Generated",
                category=PointCategory.MONETIZATION,
                base_points=1000.0,
                action_type="first_revenue",
                conditions={},
                max_daily_points=1000.0
            ),
            PointRule(
                id="revenue_milestone",
                name="Revenue Milestone",
                category=PointCategory.MONETIZATION,
                base_points=100.0,
                action_type="revenue_milestone",
                conditions={"amount": {"min": 100}},
                multipliers={"revenue_scale": 1.0}
            ),
            
            # Protection Points
            PointRule(
                id="content_protection",
                name="Content Protection",
                category=PointCategory.PROTECTION,
                base_points=30.0,
                action_type="content_protected",
                conditions={},
                max_daily_points=300.0
            ),
            PointRule(
                id="copyright_claim",
                name="Successful Copyright Claim",
                category=PointCategory.PROTECTION,
                base_points=200.0,
                action_type="copyright_claim_success",
                conditions={},
                max_weekly_points=800.0
            ),
            
            # Innovation Points
            PointRule(
                id="feature_adoption",
                name="New Feature Adoption",
                category=PointCategory.INNOVATION,
                base_points=100.0,
                action_type="feature_used",
                conditions={"new_feature": True},
                max_weekly_points=500.0
            ),
            PointRule(
                id="beta_testing",
                name="Beta Testing Participation",
                category=PointCategory.INNOVATION,
                base_points=250.0,
                action_type="beta_participation",
                conditions={},
                max_daily_points=250.0
            ),
            
            # Community Points
            PointRule(
                id="community_help",
                name="Community Assistance",
                category=PointCategory.COMMUNITY,
                base_points=50.0,
                action_type="community_help",
                conditions={},
                max_daily_points=200.0
            ),
            PointRule(
                id="mentoring",
                name="Mentoring Activity",
                category=PointCategory.COMMUNITY,
                base_points=150.0,
                action_type="mentoring_session",
                conditions={},
                max_weekly_points=600.0
            ),
            
            # Daily Activity Points
            PointRule(
                id="daily_login",
                name="Daily Login",
                category=PointCategory.DAILY_ACTIVITY,
                base_points=10.0,
                action_type="daily_login",
                conditions={},
                max_daily_points=10.0
            ),
            PointRule(
                id="daily_challenge",
                name="Daily Challenge Completion",
                category=PointCategory.DAILY_ACTIVITY,
                base_points=100.0,
                action_type="daily_challenge_complete",
                conditions={},
                max_daily_points=300.0
            )
        ]
        
        for rule in default_rules:
            self.point_rules[rule.id] = rule
        
        self.logger.info(f"Loaded {len(default_rules)} default point rules")
    
    async def _load_default_multipliers(self):
        """Load default point multipliers."""
        default_multipliers = [
            # Streak Multipliers
            PointMultiplier(
                id="daily_streak_3",
                name="3-Day Streak",
                multiplier_type=MultiplierType.STREAK,
                value=1.1,
                conditions={"streak_days": {"min": 3, "max": 6}}
            ),
            PointMultiplier(
                id="daily_streak_7",
                name="Weekly Streak",
                multiplier_type=MultiplierType.STREAK,
                value=1.25,
                conditions={"streak_days": {"min": 7, "max": 13}}
            ),
            PointMultiplier(
                id="daily_streak_14",
                name="Bi-Weekly Streak",
                multiplier_type=MultiplierType.STREAK,
                value=1.5,
                conditions={"streak_days": {"min": 14, "max": 29}}
            ),
            PointMultiplier(
                id="daily_streak_30",
                name="Monthly Streak",
                multiplier_type=MultiplierType.STREAK,
                value=2.0,
                conditions={"streak_days": {"min": 30}}
            ),
            
            # Tier Multipliers
            PointMultiplier(
                id="tier_beginner",
                name="Beginner Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=1.0,
                conditions={"tier": "Beginner"}
            ),
            PointMultiplier(
                id="tier_intermediate",
                name="Intermediate Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=1.1,
                conditions={"tier": "Intermediate"}
            ),
            PointMultiplier(
                id="tier_advanced",
                name="Advanced Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=1.2,
                conditions={"tier": "Advanced"}
            ),
            PointMultiplier(
                id="tier_expert",
                name="Expert Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=1.3,
                conditions={"tier": "Expert"}
            ),
            PointMultiplier(
                id="tier_master",
                name="Master Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=1.5,
                conditions={"tier": "Master"}
            ),
            PointMultiplier(
                id="tier_legendary",
                name="Legendary Tier Bonus",
                multiplier_type=MultiplierType.TIER,
                value=2.0,
                conditions={"tier": "Legendary"}
            ),
            
            # Quality Multipliers
            PointMultiplier(
                id="quality_excellent",
                name="Excellent Quality Bonus",
                multiplier_type=MultiplierType.QUALITY,
                value=1.5,
                conditions={"quality_score": {"min": 0.9}}
            ),
            PointMultiplier(
                id="quality_good",
                name="Good Quality Bonus",
                multiplier_type=MultiplierType.QUALITY,
                value=1.2,
                conditions={"quality_score": {"min": 0.7, "max": 0.89}}
            ),
            
            # Collaboration Multipliers
            PointMultiplier(
                id="collaboration_bonus",
                name="Collaboration Bonus",
                multiplier_type=MultiplierType.COLLABORATION,
                value=1.3,
                conditions={"collaboration_active": True}
            ),
            
            # Achievement Multipliers
            PointMultiplier(
                id="achievement_bronze",
                name="Bronze Achievement Bonus",
                multiplier_type=MultiplierType.ACHIEVEMENT_BONUS,
                value=1.05,
                conditions={"recent_bronze_achievement": True}
            ),
            PointMultiplier(
                id="achievement_silver",
                name="Silver Achievement Bonus",
                multiplier_type=MultiplierType.ACHIEVEMENT_BONUS,
                value=1.1,
                conditions={"recent_silver_achievement": True}
            ),
            PointMultiplier(
                id="achievement_gold",
                name="Gold Achievement Bonus",
                multiplier_type=MultiplierType.ACHIEVEMENT_BONUS,
                value=1.2,
                conditions={"recent_gold_achievement": True}
            )
        ]
        
        for multiplier in default_multipliers:
            self.multipliers[multiplier.id] = multiplier
        
        self.logger.info(f"Loaded {len(default_multipliers)} default multipliers")
    
    async def calculate_points(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate points for a user action."""
        try:
            # Find applicable point rules
            applicable_rules = self._find_applicable_rules(action_type, action_data)
            
            if not applicable_rules:
                return {"points": 0, "transactions": [], "message": "No applicable rules found"}
            
            # Get or create user balance
            if user_id not in self.user_balances:
                self.user_balances[user_id] = UserPointBalance(user_id=user_id)
            
            user_balance = self.user_balances[user_id]
            total_points_earned = 0.0
            transactions = []
            
            # Process each applicable rule
            for rule in applicable_rules:
                # Check daily/weekly limits
                if not self._check_point_limits(user_id, rule, action_data):
                    continue
                
                # Calculate base points
                base_points = self._calculate_base_points(rule, action_data)
                
                # Calculate multipliers
                multiplier = await self._calculate_multipliers(user_id, rule, action_data)
                
                # Calculate final points
                final_points = base_points * multiplier
                
                # Create transaction
                transaction = PointTransaction(
                    id=str(uuid4()),
                    user_id=user_id,
                    category=rule.category,
                    action_type=action_type,
                    base_points=base_points,
                    multiplier=multiplier,
                    final_points=final_points,
                    source_rule_id=rule.id,
                    metadata=action_data.copy()
                )
                
                # Record transaction
                if user_id not in self.transactions:
                    self.transactions[user_id] = []
                self.transactions[user_id].append(transaction)
                transactions.append(transaction.id)
                
                # Update user balance
                self._update_user_balance(user_balance, rule.category, final_points)
                total_points_earned += final_points
                
                self.logger.debug(f"Points calculated: {user_id} - {action_type} - {final_points} points")
            
            # Update streaks
            await self._update_user_streaks(user_id, action_type)
            
            return {
                "points": total_points_earned,
                "transactions": transactions,
                "user_balance": {
                    "total_points": user_balance.total_points,
                    "daily_points": user_balance.daily_points,
                    "current_streak": user_balance.current_streak
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating points for user {user_id}: {e}")
            return {"points": 0, "error": str(e)}
    
    def _find_applicable_rules(
        self,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> List[PointRule]:
        """Find point rules applicable to the action."""
        applicable_rules = []
        
        for rule in self.point_rules.values():
            if not rule.is_active:
                continue
            
            if rule.action_type != action_type:
                continue
            
            # Check conditions
            if self._check_rule_conditions(rule, action_data):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _check_rule_conditions(
        self,
        rule: PointRule,
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if action data meets rule conditions."""
        try:
            for condition_key, condition_value in rule.conditions.items():
                if condition_key not in action_data:
                    if condition_key != "any":  # Special case for any content type
                        return False
                    continue
                
                action_value = action_data[condition_key]
                
                if isinstance(condition_value, dict):
                    # Range conditions
                    if "min" in condition_value and action_value < condition_value["min"]:
                        return False
                    if "max" in condition_value and action_value > condition_value["max"]:
                        return False
                elif isinstance(condition_value, (list, tuple)):
                    # Value must be in list
                    if action_value not in condition_value:
                        return False
                else:
                    # Exact match
                    if action_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule conditions: {e}")
            return False
    
    def _check_point_limits(
        self,
        user_id: str,
        rule: PointRule,
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if user has reached daily/weekly point limits for this rule."""
        try:
            today = datetime.utcnow().date().isoformat()
            week = datetime.utcnow().isocalendar()[:2]  # (year, week)
            week_key = f"{week[0]}-W{week[1]}"
            
            # Initialize tracking if needed
            if user_id not in self.daily_points:
                self.daily_points[user_id] = {}
            if user_id not in self.weekly_points:
                self.weekly_points[user_id] = {}
            
            # Check daily limits
            if rule.max_daily_points:
                daily_key = f"{rule.id}_{today}"
                current_daily = self.daily_points[user_id].get(daily_key, 0)
                if current_daily >= rule.max_daily_points:
                    return False
            
            # Check weekly limits
            if rule.max_weekly_points:
                weekly_key = f"{rule.id}_{week_key}"
                current_weekly = self.weekly_points[user_id].get(weekly_key, 0)
                if current_weekly >= rule.max_weekly_points:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking point limits: {e}")
            return True  # Allow points if check fails
    
    def _calculate_base_points(
        self,
        rule: PointRule,
        action_data: Dict[str, Any]
    ) -> float:
        """Calculate base points for a rule."""
        base_points = rule.base_points
        
        # Apply rule-specific multipliers from action data
        for multiplier_key, multiplier_value in rule.multipliers.items():
            if multiplier_key in action_data:
                scaling_factor = action_data[multiplier_key]
                base_points *= (1 + (scaling_factor * multiplier_value))
        
        # Special scaling for revenue
        if rule.action_type == "revenue_milestone" and "amount" in action_data:
            # Scale points based on revenue amount (logarithmic scaling)
            revenue_amount = action_data["amount"]
            scaling_factor = math.log10(max(1, revenue_amount / 100))
            base_points *= scaling_factor
        
        return base_points
    
    async def _calculate_multipliers(
        self,
        user_id: str,
        rule: PointRule,
        action_data: Dict[str, Any]
    ) -> float:
        """Calculate total multiplier for user and action."""
        total_multiplier = 1.0
        user_balance = self.user_balances.get(user_id)
        
        if not user_balance:
            return total_multiplier
        
        # Get user context data
        user_context = {
            "streak_days": user_balance.current_streak,
            "tier": self._get_user_tier(user_balance.total_points),
            "collaboration_active": action_data.get("collaboration_active", False),
            "quality_score": action_data.get("quality_score", 0),
            "recent_bronze_achievement": self._has_recent_achievement(user_id, "bronze"),
            "recent_silver_achievement": self._has_recent_achievement(user_id, "silver"),
            "recent_gold_achievement": self._has_recent_achievement(user_id, "gold")
        }
        
        # Apply applicable multipliers
        for multiplier in self.multipliers.values():
            if not multiplier.is_active:
                continue
            
            # Check if multiplier has expired
            if multiplier.expires_at and datetime.utcnow() > multiplier.expires_at:
                continue
            
            # Check multiplier conditions
            if self._check_multiplier_conditions(multiplier, user_context, action_data):
                total_multiplier *= multiplier.value
        
        return total_multiplier
    
    def _check_multiplier_conditions(
        self,
        multiplier: PointMultiplier,
        user_context: Dict[str, Any],
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if multiplier conditions are met."""
        try:
            # Combine user context and action data
            combined_data = {**user_context, **action_data}
            
            for condition_key, condition_value in multiplier.conditions.items():
                if condition_key not in combined_data:
                    return False
                
                actual_value = combined_data[condition_key]
                
                if isinstance(condition_value, dict):
                    # Range conditions
                    if "min" in condition_value and actual_value < condition_value["min"]:
                        return False
                    if "max" in condition_value and actual_value > condition_value["max"]:
                        return False
                elif isinstance(condition_value, bool):
                    if actual_value != condition_value:
                        return False
                else:
                    if actual_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking multiplier conditions: {e}")
            return False
    
    def _get_user_tier(self, total_points: float) -> str:
        """Get user tier based on total points."""
        if total_points >= 50000:
            return "Legendary"
        elif total_points >= 25000:
            return "Master"
        elif total_points >= 10000:
            return "Expert"
        elif total_points >= 5000:
            return "Advanced"
        elif total_points >= 1000:
            return "Intermediate"
        elif total_points >= 100:
            return "Beginner"
        else:
            return "Newcomer"
    
    def _has_recent_achievement(self, user_id: str, tier: str) -> bool:
        """Check if user has recent achievement of specified tier."""
        # This would integrate with the achievement system
        # For now, return False as placeholder
        return False
    
    def _update_user_balance(
        self,
        user_balance: UserPointBalance,
        category: PointCategory,
        points: float
    ):
        """Update user's point balance."""
        # Update total points
        user_balance.total_points += points
        user_balance.lifetime_earned += points
        
        # Update category points
        if category.value not in user_balance.category_points:
            user_balance.category_points[category.value] = 0.0
        user_balance.category_points[category.value] += points
        
        # Update daily/weekly/monthly points
        user_balance.daily_points += points
        user_balance.weekly_points += points
        user_balance.monthly_points += points
        
        # Update last activity
        user_balance.last_activity = datetime.utcnow()
        
        # Update daily/weekly tracking
        self._update_point_tracking(user_balance.user_id, points)
    
    def _update_point_tracking(self, user_id: str, points: float):
        """Update daily and weekly point tracking."""
        today = datetime.utcnow().date().isoformat()
        week = datetime.utcnow().isocalendar()[:2]
        week_key = f"{week[0]}-W{week[1]}"
        
        # Update daily tracking
        if user_id not in self.daily_points:
            self.daily_points[user_id] = {}
        self.daily_points[user_id][today] = self.daily_points[user_id].get(today, 0) + points
        
        # Update weekly tracking
        if user_id not in self.weekly_points:
            self.weekly_points[user_id] = {}
        self.weekly_points[user_id][week_key] = self.weekly_points[user_id].get(week_key, 0) + points
    
    async def _update_user_streaks(self, user_id: str, action_type: str):
        """Update user activity streaks."""
        try:
            if user_id not in self.streak_data:
                self.streak_data[user_id] = {
                    "last_activity_date": None,
                    "current_streak": 0,
                    "max_streak": 0
                }
            
            streak_info = self.streak_data[user_id]
            today = datetime.utcnow().date()
            
            # Check if this is a daily activity
            if action_type in ["daily_login", "content_upload", "daily_challenge_complete"]:
                if streak_info["last_activity_date"] == today:
                    # Already counted today
                    return
                elif streak_info["last_activity_date"] == today - timedelta(days=1):
                    # Consecutive day
                    streak_info["current_streak"] += 1
                else:
                    # Streak broken or first activity
                    streak_info["current_streak"] = 1
                
                streak_info["last_activity_date"] = today
                streak_info["max_streak"] = max(streak_info["max_streak"], streak_info["current_streak"])
                
                # Update user balance
                user_balance = self.user_balances[user_id]
                user_balance.current_streak = streak_info["current_streak"]
                user_balance.max_streak = streak_info["max_streak"]
            
        except Exception as e:
            self.logger.error(f"Error updating user streaks: {e}")
    
    async def get_user_points(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive point information for a user."""
        try:
            if user_id not in self.user_balances:
                return {
                    "total_points": 0,
                    "category_breakdown": {},
                    "daily_points": 0,
                    "weekly_points": 0,
                    "monthly_points": 0,
                    "current_streak": 0,
                    "tier": "Newcomer"
                }
            
            user_balance = self.user_balances[user_id]
            
            # Get recent transactions
            recent_transactions = []
            if user_id in self.transactions:
                recent_transactions = sorted(
                    self.transactions[user_id][-10:],  # Last 10 transactions
                    key=lambda x: x.timestamp,
                    reverse=True
                )
            
            # Calculate point velocity (points per day)
            days_active = max(1, (datetime.utcnow() - user_balance.last_activity).days)
            point_velocity = user_balance.lifetime_earned / days_active
            
            return {
                "user_id": user_id,
                "total_points": user_balance.total_points,
                "lifetime_earned": user_balance.lifetime_earned,
                "points_spent": user_balance.points_spent,
                "category_breakdown": user_balance.category_points,
                "daily_points": user_balance.daily_points,
                "weekly_points": user_balance.weekly_points,
                "monthly_points": user_balance.monthly_points,
                "current_streak": user_balance.current_streak,
                "max_streak": user_balance.max_streak,
                "tier": self._get_user_tier(user_balance.total_points),
                "point_velocity": point_velocity,
                "recent_transactions": [
                    {
                        "id": t.id,
                        "category": t.category.value,
                        "action_type": t.action_type,
                        "points": t.final_points,
                        "timestamp": t.timestamp
                    } for t in recent_transactions
                ],
                "active_multipliers": user_balance.multipliers_active,
                "last_activity": user_balance.last_activity
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user points: {e}")
            return {}
    
    async def _daily_reset_task(self):
        """Background task to reset daily counters."""
        while True:
            try:
                await asyncio.sleep(86400)  # 24 hours
                
                # Reset daily points for all users
                for user_balance in self.user_balances.values():
                    user_balance.daily_points = 0.0
                
                self.logger.info("Daily point counters reset")
                
            except Exception as e:
                self.logger.error(f"Error in daily reset task: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _cleanup_expired_multipliers(self):
        """Background task to cleanup expired multipliers."""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                current_time = datetime.utcnow()
                expired_multipliers = []
                
                for multiplier_id, multiplier in self.multipliers.items():
                    if multiplier.expires_at and current_time > multiplier.expires_at:
                        expired_multipliers.append(multiplier_id)
                
                # Remove expired multipliers
                for multiplier_id in expired_multipliers:
                    self.multipliers[multiplier_id].is_active = False
                
                if expired_multipliers:
                    self.logger.info(f"Disabled {len(expired_multipliers)} expired multipliers")
                
            except Exception as e:
                self.logger.error(f"Error in multiplier cleanup task: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes
    
    async def get_point_statistics(self) -> Dict[str, Any]:
        """Get system-wide point statistics."""
        try:
            total_users = len(self.user_balances)
            total_points_distributed = sum(balance.lifetime_earned for balance in self.user_balances.values())
            
            # Category distribution
            category_distribution = {}
            for balance in self.user_balances.values():
                for category, points in balance.category_points.items():
                    category_distribution[category] = category_distribution.get(category, 0) + points
            
            # Tier distribution
            tier_distribution = {}
            for balance in self.user_balances.values():
                tier = self._get_user_tier(balance.total_points)
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            return {
                "total_users": total_users,
                "total_points_distributed": total_points_distributed,
                "average_points_per_user": total_points_distributed / total_users if total_users > 0 else 0,
                "category_distribution": category_distribution,
                "tier_distribution": tier_distribution,
                "active_rules": len([r for r in self.point_rules.values() if r.is_active]),
                "active_multipliers": len([m for m in self.multipliers.values() if m.is_active])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting point statistics: {e}")
            return {}