"""Badge System - Système de badges
=================================

Badge management system for creating, awarding, and displaying badges
for content creator achievements and milestones.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum


class BadgeType(str, Enum):
    """Types of badges available in the system."""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"
    COLLABORATION = "collaboration"
    TIER = "tier"
    SEASONAL = "seasonal"


class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Badge:
    """Badge definition."""
    id: str
    name: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    icon_url: str
    color_scheme: Dict[str, str] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class UserBadge:
    """User's awarded badge."""
    id: str
    user_id: str
    badge_id: str
    awarded_at: datetime
    awarded_for: str  # Reason for awarding
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_displayed: bool = True


class BadgeSystem:
    """
    Comprehensive badge management system providing badge creation,
    awarding, and display functionality for content creators.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the badge system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, List[UserBadge]] = {}
        
        # Initialize default badges
        self._initialize_default_badges()
        
        self.logger.info("BadgeSystem initialized")
    
    def _initialize_default_badges(self):
        """Initialize default badge templates."""
        try:
            # Achievement badges
            self.badges["newcomer"] = Badge(
                id="newcomer",
                name="Newcomer",
                description="Welcome to the platform!",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                icon_url="/badges/newcomer.svg",
                color_scheme={"primary": "#4CAF50", "secondary": "#81C784"},
                requirements={"uploads": 1}
            )
            
            self.badges["prolific"] = Badge(
                id="prolific",
                name="Prolific Creator",
                description="Created 100+ pieces of content",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.UNCOMMON,
                icon_url="/badges/prolific.svg",
                color_scheme={"primary": "#2196F3", "secondary": "#64B5F6"},
                requirements={"uploads": 100}
            )
            
            self.badges["viral"] = Badge(
                id="viral",
                name="Viral Master",
                description="Content reached 1M+ views",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.RARE,
                icon_url="/badges/viral.svg",
                color_scheme={"primary": "#FF9800", "secondary": "#FFB74D"},
                requirements={"max_views": 1000000}
            )
            
            self.badges["collaborator"] = Badge(
                id="collaborator",
                name="Team Player",
                description="Completed multiple collaborations",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.UNCOMMON,
                icon_url="/badges/collaborator.svg",
                color_scheme={"primary": "#9C27B0", "secondary": "#BA68C8"},
                requirements={"collaborations": 5}
            )
            
            self.badges["influencer"] = Badge(
                id="influencer",
                name="Rising Influencer",
                description="Gained significant following",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.EPIC,
                icon_url="/badges/influencer.svg",
                color_scheme={"primary": "#E91E63", "secondary": "#F06292"},
                requirements={"followers": 10000}
            )
            
            # Tier badges
            self.badges["bronze_tier"] = Badge(
                id="bronze_tier",
                name="Bronze Creator",
                description="Achieved Bronze tier status",
                badge_type=BadgeType.TIER,
                rarity=BadgeRarity.COMMON,
                icon_url="/badges/bronze_tier.svg",
                color_scheme={"primary": "#CD7F32", "secondary": "#DAA520"}
            )
            
            self.badges["silver_tier"] = Badge(
                id="silver_tier",
                name="Silver Creator",
                description="Achieved Silver tier status",
                badge_type=BadgeType.TIER,
                rarity=BadgeRarity.UNCOMMON,
                icon_url="/badges/silver_tier.svg",
                color_scheme={"primary": "#C0C0C0", "secondary": "#E5E5E5"}
            )
            
            self.badges["gold_tier"] = Badge(
                id="gold_tier",
                name="Gold Creator",
                description="Achieved Gold tier status",
                badge_type=BadgeType.TIER,
                rarity=BadgeRarity.RARE,
                icon_url="/badges/gold_tier.svg",
                color_scheme={"primary": "#FFD700", "secondary": "#FFF8DC"}
            )
            
            # Special event badges
            self.badges["early_adopter"] = Badge(
                id="early_adopter",
                name="Early Adopter",
                description="Joined during beta phase",
                badge_type=BadgeType.SPECIAL_EVENT,
                rarity=BadgeRarity.LEGENDARY,
                icon_url="/badges/early_adopter.svg",
                color_scheme={"primary": "#673AB7", "secondary": "#9575CD"}
            )
            
            self.logger.info(f"Initialized {len(self.badges)} default badges")
            
        except Exception as e:
            self.logger.error(f"Error initializing default badges: {e}")
    
    async def award_badge(
        self,
        user_id: str,
        badge_id: str,
        awarded_for: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Award a badge to a user."""
        try:
            badge = self.badges.get(badge_id)
            if not badge:
                self.logger.warning(f"Badge {badge_id} not found")
                return False
            
            # Check if user already has this badge
            user_badges = self.user_badges.get(user_id, [])
            if any(ub.badge_id == badge_id for ub in user_badges):
                self.logger.info(f"User {user_id} already has badge {badge_id}")
                return False
            
            # Create user badge
            user_badge = UserBadge(
                id=f"{user_id}_{badge_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                badge_id=badge_id,
                awarded_at=datetime.now(timezone.utc),
                awarded_for=awarded_for,
                metadata=metadata or {}
            )
            
            # Add to user's badges
            if user_id not in self.user_badges:
                self.user_badges[user_id] = []
            self.user_badges[user_id].append(user_badge)
            
            self.logger.info(f"🎖️ Badge '{badge.name}' awarded to user {user_id} for: {awarded_for}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error awarding badge: {e}")
            return False
    
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all badges for a user."""
        try:
            user_badges = self.user_badges.get(user_id, [])
            result = []
            
            for user_badge in user_badges:
                badge = self.badges.get(user_badge.badge_id)
                if badge:
                    result.append({
                        "id": user_badge.id,
                        "badge_id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "badge_type": badge.badge_type,
                        "rarity": badge.rarity,
                        "icon_url": badge.icon_url,
                        "color_scheme": badge.color_scheme,
                        "awarded_at": user_badge.awarded_at.isoformat(),
                        "awarded_for": user_badge.awarded_for,
                        "is_displayed": user_badge.is_displayed
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting user badges: {e}")
            return []
    
    async def get_badge_showcase(self, user_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        """Get user's badge showcase (most impressive badges for display)."""
        try:
            user_badges = await self.get_user_badges(user_id)
            
            # Sort by rarity and recency
            rarity_order = {
                BadgeRarity.LEGENDARY: 5,
                BadgeRarity.EPIC: 4,
                BadgeRarity.RARE: 3,
                BadgeRarity.UNCOMMON: 2,
                BadgeRarity.COMMON: 1
            }
            
            displayed_badges = [b for b in user_badges if b.get("is_displayed", True)]
            
            sorted_badges = sorted(
                displayed_badges,
                key=lambda x: (
                    rarity_order.get(x["rarity"], 0),
                    datetime.fromisoformat(x["awarded_at"])
                ),
                reverse=True
            )
            
            return sorted_badges[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting badge showcase: {e}")
            return []
    
    async def get_badge_stats(self, user_id: str) -> Dict[str, Any]:
        """Get badge statistics for a user."""
        try:
            user_badges = self.user_badges.get(user_id, [])
            
            stats = {
                "total_badges": len(user_badges),
                "by_type": {},
                "by_rarity": {},
                "recent_badges": [],
                "showcase_badges": []
            }
            
            # Count by type and rarity
            for user_badge in user_badges:
                badge = self.badges.get(user_badge.badge_id)
                if badge:
                    # By type
                    badge_type = badge.badge_type
                    if badge_type not in stats["by_type"]:
                        stats["by_type"][badge_type] = 0
                    stats["by_type"][badge_type] += 1
                    
                    # By rarity
                    rarity = badge.rarity
                    if rarity not in stats["by_rarity"]:
                        stats["by_rarity"][rarity] = 0
                    stats["by_rarity"][rarity] += 1
            
            # Recent badges (last 5)
            recent = sorted(user_badges, key=lambda x: x.awarded_at, reverse=True)[:5]
            stats["recent_badges"] = [
                {
                    "badge_id": ub.badge_id,
                    "name": self.badges.get(ub.badge_id, {}).get("name", ""),
                    "awarded_at": ub.awarded_at.isoformat(),
                    "awarded_for": ub.awarded_for
                }
                for ub in recent
            ]
            
            # Showcase badges
            stats["showcase_badges"] = await self.get_badge_showcase(user_id)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting badge stats: {e}")
            return {}
    
    async def create_custom_badge(
        self,
        badge_id: str,
        name: str,
        description: str,
        badge_type: BadgeType,
        rarity: BadgeRarity,
        icon_url: str,
        color_scheme: Dict[str, str],
        requirements: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a custom badge."""
        try:
            if badge_id in self.badges:
                self.logger.warning(f"Badge {badge_id} already exists")
                return False
            
            badge = Badge(
                id=badge_id,
                name=name,
                description=description,
                badge_type=badge_type,
                rarity=rarity,
                icon_url=icon_url,
                color_scheme=color_scheme,
                requirements=requirements or {}
            )
            
            self.badges[badge_id] = badge
            self.logger.info(f"Created custom badge: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating custom badge: {e}")
            return False
    
    async def update_badge_display(self, user_id: str, badge_id: str, is_displayed: bool) -> bool:
        """Update badge display status for a user."""
        try:
            user_badges = self.user_badges.get(user_id, [])
            
            for user_badge in user_badges:
                if user_badge.badge_id == badge_id:
                    user_badge.is_displayed = is_displayed
                    self.logger.info(f"Updated badge display for {user_id}: {badge_id} -> {is_displayed}")
                    return True
            
            self.logger.warning(f"Badge {badge_id} not found for user {user_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating badge display: {e}")
            return False
    
    async def get_available_badges(self) -> List[Dict[str, Any]]:
        """Get list of all available badges."""
        try:
            return [
                {
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "badge_type": badge.badge_type,
                    "rarity": badge.rarity,
                    "icon_url": badge.icon_url,
                    "color_scheme": badge.color_scheme,
                    "requirements": badge.requirements
                }
                for badge in self.badges.values()
                if badge.is_active
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting available badges: {e}")
            return []


# Global instance
_badge_system = None

def get_badge_system(database_connection=None, cache_client=None) -> BadgeSystem:
    """Get the global badge system instance."""
    global _badge_system
    if _badge_system is None:
        _badge_system = BadgeSystem(database_connection, cache_client)
    return _badge_system