"""Badge System - Digital Badge Management and NFT Integration
===========================================================

Advanced badge management system providing digital badge creation,
distribution, rarity management, and Web3 NFT integration for
content creator achievements and milestones.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/achievements/badge_system.py
Expert Team: Lead Dev IA + Backend Senior + Blockchain + Security

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
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib

logger = logging.getLogger(__name__)


class BadgeType(str, Enum):
    """Badge types and categories."""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    INNOVATION = "innovation"
    COMMUNITY = "community"
    SEASONAL = "seasonal"


class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class BadgeStatus(str, Enum):
    """Badge status states."""
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    LIMITED = "limited"


@dataclass
class BadgeDesign:
    """Badge visual design configuration."""
    background_color: str = "#1a1a1a"
    border_color: str = "#gold"
    icon_url: str = ""
    pattern: str = "classic"
    animation: bool = False
    glow_effect: bool = False
    particle_effects: List[str] = field(default_factory=list)


@dataclass
class Badge:
    """Badge definition and metadata."""
    id: str
    name: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    status: BadgeStatus
    design: BadgeDesign
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    issue_count: int = 0
    max_issuance: Optional[int] = None
    time_limited: bool = False
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserBadge:
    """User's badge ownership record."""
    id: str
    user_id: str
    badge_id: str
    issued_at: datetime
    sequence_number: int  # Issue order (1st, 2nd, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)
    nft_token_id: Optional[str] = None
    blockchain_tx: Optional[str] = None


class BadgeSystem:
    """
    Advanced badge management system.
    
    Provides comprehensive badge creation, distribution, rarity management,
    and integration with blockchain NFT systems for permanent badge ownership.
    """
    
    def __init__(self):
        """Initialize the badge system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialized = False
        
        # Badge definitions
        self.badges: Dict[str, Badge] = {}
        
        # User badge ownership
        self.user_badges: Dict[str, List[UserBadge]] = {}
        
        # Badge issuance tracking
        self.issuance_counter: Dict[str, int] = {}
        
        # Badge triggers and automation
        self.badge_triggers: Dict[str, List[str]] = {}
        
        self.logger.info("BadgeSystem initialized")
    
    async def initialize(self) -> bool:
        """Initialize the badge system with default badges."""
        try:
            # Load default badge definitions
            await self._load_default_badges()
            
            # Setup badge triggers
            await self._setup_badge_triggers()
            
            self.initialized = True
            self.logger.info(f"✅ BadgeSystem initialized with {len(self.badges)} badges")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize BadgeSystem: {e}")
            return False
    
    async def _load_default_badges(self):
        """Load default badge definitions."""
        default_badges = [
            # Achievement Badges
            Badge(
                id="first_content",
                name="First Steps",
                description="Awarded for uploading your first piece of content",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#4CAF50",
                    border_color="#2E7D32",
                    icon_url="/badges/first_steps.svg",
                    pattern="classic",
                    glow_effect=True
                ),
                requirements={"total_uploads": 1},
                rewards={"xp": 100, "points": 50}
            ),
            Badge(
                id="content_master",
                name="Content Master",
                description="Awarded for creating exceptional content consistently",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.EPIC,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#9C27B0",
                    border_color="#6A1B9A",
                    icon_url="/badges/content_master.svg",
                    pattern="diamond",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["sparkle", "star"]
                ),
                requirements={"total_uploads": 100, "avg_quality_score": 0.85},
                rewards={"xp": 2000, "points": 1000, "revenue_boost": 0.05}
            ),
            
            # Collaboration Badges
            Badge(
                id="team_player",
                name="Team Player",
                description="Awarded for successful collaboration efforts",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.UNCOMMON,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#FF9800",
                    border_color="#E65100",
                    icon_url="/badges/team_player.svg",
                    pattern="hexagon",
                    glow_effect=True
                ),
                requirements={"collaborations_completed": 5},
                rewards={"xp": 500, "points": 250}
            ),
            Badge(
                id="global_connector",
                name="Global Connector",
                description="Legendary badge for extraordinary collaboration achievements",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.LEGENDARY,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#FFD700",
                    border_color="#FFA000",
                    icon_url="/badges/global_connector.svg",
                    pattern="crown",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["golden_sparkle", "crown_glow"]
                ),
                requirements={"collaborations_completed": 100, "global_reach": True},
                rewards={"xp": 5000, "points": 2500, "special_privileges": True},
                max_issuance=100  # Limited edition
            ),
            
            # Quality Badges
            Badge(
                id="viral_creator",
                name="Viral Creator",
                description="Awarded for creating viral content",
                badge_type=BadgeType.ENGAGEMENT,
                rarity=BadgeRarity.RARE,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#E91E63",
                    border_color="#AD1457",
                    icon_url="/badges/viral_creator.svg",
                    pattern="burst",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["viral_explosion"]
                ),
                requirements={"max_views": 10000, "viral_coefficient": 1.5},
                rewards={"xp": 1500, "points": 750, "viral_boost": 0.10}
            ),
            
            # Revenue Badges
            Badge(
                id="first_revenue",
                name="First Revenue",
                description="Awarded for earning your first revenue",
                badge_type=BadgeType.REVENUE,
                rarity=BadgeRarity.COMMON,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#4CAF50",
                    border_color="#2E7D32",
                    icon_url="/badges/first_revenue.svg",
                    pattern="coin",
                    glow_effect=True
                ),
                requirements={"total_revenue": 1},
                rewards={"xp": 200, "points": 100}
            ),
            Badge(
                id="revenue_king",
                name="Revenue King",
                description="Legendary badge for exceptional revenue generation",
                badge_type=BadgeType.REVENUE,
                rarity=BadgeRarity.LEGENDARY,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#FFD700",
                    border_color="#FFA000",
                    icon_url="/badges/revenue_king.svg",
                    pattern="royal_crown",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["golden_coins", "money_rain"]
                ),
                requirements={"total_revenue": 10000, "monthly_revenue": 1000},
                rewards={"xp": 5000, "points": 2500, "revenue_boost": 0.15},
                max_issuance=50  # Ultra limited
            ),
            
            # Seasonal/Special Event Badges
            Badge(
                id="beta_tester",
                name="Beta Tester",
                description="Awarded to early platform adopters and beta testers",
                badge_type=BadgeType.SPECIAL_EVENT,
                rarity=BadgeRarity.MYTHICAL,
                status=BadgeStatus.LIMITED,
                design=BadgeDesign(
                    background_color="#9C27B0",
                    border_color="#4A148C",
                    icon_url="/badges/beta_tester.svg",
                    pattern="exclusive",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["beta_aura", "exclusive_glow"]
                ),
                requirements={"beta_participation": True},
                rewards={"xp": 1000, "points": 500, "exclusive_access": True},
                max_issuance=1000,  # Limited to first 1000 users
                time_limited=True,
                expires_at=datetime(2025, 12, 31)
            ),
            
            # Innovation Badges
            Badge(
                id="innovation_pioneer",
                name="Innovation Pioneer",
                description="Awarded for being first to use new platform features",
                badge_type=BadgeType.INNOVATION,
                rarity=BadgeRarity.EPIC,
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(
                    background_color="#2196F3",
                    border_color="#1565C0",
                    icon_url="/badges/innovation_pioneer.svg",
                    pattern="tech",
                    animation=True,
                    glow_effect=True,
                    particle_effects=["tech_sparkle"]
                ),
                requirements={"new_features_used": 10, "early_adoption": True},
                rewards={"xp": 1200, "points": 600, "beta_access": True}
            )
        ]
        
        for badge in default_badges:
            self.badges[badge.id] = badge
            self.issuance_counter[badge.id] = 0
        
        self.logger.info(f"Loaded {len(default_badges)} default badges")
    
    async def _setup_badge_triggers(self):
        """Setup automated badge triggers based on actions."""
        # Map action types to badge IDs
        self.badge_triggers = {
            "content_upload": ["first_content"],
            "collaboration_success": ["team_player"],
            "revenue_milestone": ["first_revenue", "revenue_king"],
            "viral_content": ["viral_creator"],
            "quality_milestone": ["content_master"],
            "innovation_usage": ["innovation_pioneer"],
            "beta_participation": ["beta_tester"]
        }
        
        self.logger.info("Badge triggers configured")
    
    async def process_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user action and check for badge awards."""
        try:
            awarded_badges = []
            
            # Check for triggered badges
            if action_type in self.badge_triggers:
                potential_badges = self.badge_triggers[action_type]
                
                for badge_id in potential_badges:
                    if await self._should_award_badge(user_id, badge_id, action_data):
                        badge = await self._award_badge(user_id, badge_id, action_data)
                        if badge:
                            awarded_badges.append(badge.id)
            
            return {
                "awarded": awarded_badges,
                "total_badges": len(self.user_badges.get(user_id, [])),
                "rarity_distribution": self._get_user_rarity_distribution(user_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing badge action for user {user_id}: {e}")
            return {"awarded": [], "error": str(e)}
    
    async def _should_award_badge(
        self,
        user_id: str,
        badge_id: str,
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if user should be awarded a specific badge."""
        try:
            # Check if badge exists
            if badge_id not in self.badges:
                return False
            
            badge = self.badges[badge_id]
            
            # Check if badge is active
            if badge.status != BadgeStatus.ACTIVE:
                return False
            
            # Check if user already has this badge (non-repeatable)
            if self._user_has_badge(user_id, badge_id):
                return False
            
            # Check issuance limits
            if badge.max_issuance and self.issuance_counter[badge_id] >= badge.max_issuance:
                return False
            
            # Check time limits
            if badge.time_limited and badge.expires_at and datetime.utcnow() > badge.expires_at:
                return False
            
            # Check requirements
            return self._check_badge_requirements(badge, action_data)
            
        except Exception as e:
            self.logger.error(f"Error checking badge award conditions: {e}")
            return False
    
    def _user_has_badge(self, user_id: str, badge_id: str) -> bool:
        """Check if user already has a specific badge."""
        user_badges = self.user_badges.get(user_id, [])
        return any(ub.badge_id == badge_id for ub in user_badges)
    
    def _check_badge_requirements(
        self,
        badge: Badge,
        action_data: Dict[str, Any]
    ) -> bool:
        """Check if action data meets badge requirements."""
        try:
            requirements = badge.requirements
            
            for req_key, req_value in requirements.items():
                if req_key not in action_data:
                    return False
                
                action_value = action_data[req_key]
                
                if isinstance(req_value, (int, float)):
                    if action_value < req_value:
                        return False
                elif isinstance(req_value, bool):
                    if action_value != req_value:
                        return False
                elif isinstance(req_value, str):
                    if action_value != req_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking badge requirements: {e}")
            return False
    
    async def _award_badge(
        self,
        user_id: str,
        badge_id: str,
        action_data: Dict[str, Any]
    ) -> Optional[UserBadge]:
        """Award a badge to a user."""
        try:
            badge = self.badges[badge_id]
            
            # Create user badge record
            user_badge = UserBadge(
                id=str(uuid4()),
                user_id=user_id,
                badge_id=badge_id,
                issued_at=datetime.utcnow(),
                sequence_number=self.issuance_counter[badge_id] + 1,
                metadata=action_data.copy()
            )
            
            # Add to user's badges
            if user_id not in self.user_badges:
                self.user_badges[user_id] = []
            
            self.user_badges[user_id].append(user_badge)
            
            # Update issuance counter
            self.issuance_counter[badge_id] += 1
            
            # Update badge issue count
            badge.issue_count += 1
            
            self.logger.info(f"🏅 Badge awarded: {user_id} - {badge.name} (#{user_badge.sequence_number})")
            
            return user_badge
            
        except Exception as e:
            self.logger.error(f"Error awarding badge: {e}")
            return None
    
    async def get_user_badges(self, user_id: str) -> Dict[str, Any]:
        """Get user's badge collection."""
        try:
            user_badges = self.user_badges.get(user_id, [])
            
            # Organize badges by type and rarity
            badge_data = []
            rarity_counts = {rarity.value: 0 for rarity in BadgeRarity}
            type_counts = {badge_type.value: 0 for badge_type in BadgeType}
            
            for user_badge in user_badges:
                badge = self.badges.get(user_badge.badge_id)
                if badge:
                    badge_info = {
                        "id": user_badge.id,
                        "badge_id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "type": badge.badge_type.value,
                        "rarity": badge.rarity.value,
                        "design": badge.design,
                        "issued_at": user_badge.issued_at,
                        "sequence_number": user_badge.sequence_number,
                        "total_issued": badge.issue_count,
                        "is_limited": badge.max_issuance is not None,
                        "nft_token_id": user_badge.nft_token_id
                    }
                    badge_data.append(badge_info)
                    
                    # Update counts
                    rarity_counts[badge.rarity.value] += 1
                    type_counts[badge.badge_type.value] += 1
            
            # Sort badges by rarity and issue date
            rarity_order = {
                BadgeRarity.MYTHICAL.value: 6,
                BadgeRarity.LEGENDARY.value: 5,
                BadgeRarity.EPIC.value: 4,
                BadgeRarity.RARE.value: 3,
                BadgeRarity.UNCOMMON.value: 2,
                BadgeRarity.COMMON.value: 1
            }
            
            badge_data.sort(key=lambda x: (rarity_order.get(x["rarity"], 0), x["issued_at"]), reverse=True)
            
            return {
                "owned": badge_data,
                "total_badges": len(badge_data),
                "rarity_distribution": rarity_counts,
                "type_distribution": type_counts,
                "completion_rate": self._calculate_badge_completion_rate(user_id),
                "rarest_badge": self._get_rarest_badge(user_badges),
                "collection_value": self._calculate_collection_value(user_badges)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user badges: {e}")
            return {}
    
    def _get_user_rarity_distribution(self, user_id: str) -> Dict[str, int]:
        """Get user's badge rarity distribution."""
        user_badges = self.user_badges.get(user_id, [])
        distribution = {rarity.value: 0 for rarity in BadgeRarity}
        
        for user_badge in user_badges:
            badge = self.badges.get(user_badge.badge_id)
            if badge:
                distribution[badge.rarity.value] += 1
        
        return distribution
    
    def _calculate_badge_completion_rate(self, user_id: str) -> float:
        """Calculate user's badge collection completion rate."""
        try:
            total_available = len([b for b in self.badges.values() if b.status == BadgeStatus.ACTIVE])
            user_count = len(self.user_badges.get(user_id, []))
            
            return (user_count / total_available * 100) if total_available > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _get_rarest_badge(self, user_badges: List[UserBadge]) -> Optional[Dict[str, Any]]:
        """Get user's rarest badge."""
        try:
            rarest_badge = None
            highest_rarity_value = 0
            
            rarity_values = {
                BadgeRarity.COMMON: 1,
                BadgeRarity.UNCOMMON: 2,
                BadgeRarity.RARE: 3,
                BadgeRarity.EPIC: 4,
                BadgeRarity.LEGENDARY: 5,
                BadgeRarity.MYTHICAL: 6
            }
            
            for user_badge in user_badges:
                badge = self.badges.get(user_badge.badge_id)
                if badge:
                    rarity_value = rarity_values.get(badge.rarity, 0)
                    if rarity_value > highest_rarity_value:
                        highest_rarity_value = rarity_value
                        rarest_badge = {
                            "name": badge.name,
                            "rarity": badge.rarity.value,
                            "sequence_number": user_badge.sequence_number,
                            "total_issued": badge.issue_count
                        }
            
            return rarest_badge
            
        except Exception:
            return None
    
    def _calculate_collection_value(self, user_badges: List[UserBadge]) -> float:
        """Calculate estimated collection value."""
        try:
            # Simple value calculation based on rarity and scarcity
            rarity_multipliers = {
                BadgeRarity.COMMON: 1.0,
                BadgeRarity.UNCOMMON: 2.5,
                BadgeRarity.RARE: 5.0,
                BadgeRarity.EPIC: 10.0,
                BadgeRarity.LEGENDARY: 25.0,
                BadgeRarity.MYTHICAL: 50.0
            }
            
            total_value = 0.0
            
            for user_badge in user_badges:
                badge = self.badges.get(user_badge.badge_id)
                if badge:
                    base_value = 10.0  # Base badge value
                    rarity_multiplier = rarity_multipliers.get(badge.rarity, 1.0)
                    
                    # Scarcity bonus
                    scarcity_bonus = 1.0
                    if badge.max_issuance:
                        scarcity_factor = badge.max_issuance / max(1, badge.issue_count)
                        scarcity_bonus = min(5.0, scarcity_factor)
                    
                    badge_value = base_value * rarity_multiplier * scarcity_bonus
                    total_value += badge_value
            
            return round(total_value, 2)
            
        except Exception:
            return 0.0
    
    async def create_custom_badge(
        self,
        badge_data: Dict[str, Any],
        creator_id: str
    ) -> Optional[str]:
        """Create a custom badge (for special events, etc.)."""
        try:
            badge_id = f"custom_{uuid4().hex[:8]}"
            
            badge = Badge(
                id=badge_id,
                name=badge_data["name"],
                description=badge_data["description"],
                badge_type=BadgeType(badge_data.get("type", "special_event")),
                rarity=BadgeRarity(badge_data.get("rarity", "rare")),
                status=BadgeStatus.ACTIVE,
                design=BadgeDesign(**badge_data.get("design", {})),
                requirements=badge_data.get("requirements", {}),
                rewards=badge_data.get("rewards", {}),
                max_issuance=badge_data.get("max_issuance"),
                time_limited=badge_data.get("time_limited", False),
                expires_at=badge_data.get("expires_at")
            )
            
            self.badges[badge_id] = badge
            self.issuance_counter[badge_id] = 0
            
            self.logger.info(f"Created custom badge: {badge.name} by {creator_id}")
            
            return badge_id
            
        except Exception as e:
            self.logger.error(f"Error creating custom badge: {e}")
            return None
    
    async def get_badge_statistics(self) -> Dict[str, Any]:
        """Get system-wide badge statistics."""
        try:
            total_badges = len(self.badges)
            total_issued = sum(self.issuance_counter.values())
            total_users_with_badges = len(self.user_badges)
            
            # Rarity distribution
            rarity_distribution = {rarity.value: 0 for rarity in BadgeRarity}
            for badge in self.badges.values():
                rarity_distribution[badge.rarity.value] += 1
            
            # Most popular badges
            popular_badges = sorted(
                [(badge_id, count) for badge_id, count in self.issuance_counter.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "total_badges": total_badges,
                "total_issued": total_issued,
                "total_users_with_badges": total_users_with_badges,
                "avg_badges_per_user": total_issued / total_users_with_badges if total_users_with_badges > 0 else 0,
                "rarity_distribution": rarity_distribution,
                "most_popular_badges": [
                    {
                        "badge_id": badge_id,
                        "name": self.badges[badge_id].name,
                        "issued_count": count
                    } for badge_id, count in popular_badges if badge_id in self.badges
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting badge statistics: {e}")
            return {}