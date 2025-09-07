"""Badge Monetization System - Enterprise Badge-Based Revenue Engine
=================================================================

Enterprise-grade badge monetization system providing automated revenue
generation through digital badges, skill certifications, and achievement
tokens with comprehensive tracking and marketplace integration.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/badge_monetization_system.py
Business Logic: Badge Creation → Skill Validation → Market Valuation → Revenue Generation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class BadgeType(str, Enum):
    """Types of badges in the monetization system."""
    SKILL_CERTIFICATION = "skill_certification"
    ACHIEVEMENT_BADGE = "achievement_badge"
    EXPERIENCE_LEVEL = "experience_level"
    QUALITY_ASSURANCE = "quality_assurance"
    COLLABORATION_EXPERT = "collaboration_expert"
    INNOVATION_PIONEER = "innovation_pioneer"
    COMMUNITY_LEADER = "community_leader"
    PLATFORM_ADVOCATE = "platform_advocate"
    MENTOR_CERTIFICATION = "mentor_certification"
    TECHNICAL_MASTERY = "technical_mastery"


class BadgeRarity(str, Enum):
    """Rarity levels affecting badge value."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class BadgeMonetizationMethod(str, Enum):
    """Methods for monetizing badges."""
    MARKETPLACE_SALES = "marketplace_sales"
    SKILL_PREMIUM = "skill_premium"
    ACCESS_PRIVILEGES = "access_privileges"
    REVENUE_MULTIPLIER = "revenue_multiplier"
    EXCLUSIVE_OPPORTUNITIES = "exclusive_opportunities"
    CERTIFICATION_FEES = "certification_fees"
    BADGE_STAKING = "badge_staking"
    COLLECTION_REWARDS = "collection_rewards"


class BadgeStatus(str, Enum):
    """Status of badge in creator's profile."""
    EARNED = "earned"
    VERIFIED = "verified"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    TRANSFERRED = "transferred"
    STAKED = "staked"


@dataclass
class BadgeDefinition:
    """Definition of a badge with monetization parameters."""
    badge_id: str
    name: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    base_value: Decimal
    earning_criteria: Dict[str, Any]
    verification_requirements: Dict[str, Any]
    monetization_methods: List[BadgeMonetizationMethod]
    revenue_multiplier: float = 1.0
    validity_period: Optional[timedelta] = None
    transferable: bool = False
    stackable: bool = False
    max_supply: Optional[int] = None
    current_supply: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True


@dataclass
class CreatorBadge:
    """Badge owned by a creator."""
    badge_instance_id: str
    creator_id: str
    badge_id: str
    earned_date: datetime
    verified_date: Optional[datetime] = None
    status: BadgeStatus = BadgeStatus.EARNED
    verification_score: float = 0.0
    current_value: Optional[Decimal] = None
    staking_rewards: Decimal = Decimal("0")
    usage_count: int = 0
    transfer_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


@dataclass
class BadgeTransaction:
    """Transaction involving badge monetization."""
    transaction_id: str
    badge_instance_id: str
    creator_id: str
    transaction_type: str  # sale, purchase, stake, unstake, reward
    amount: Decimal
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    counterparty_id: Optional[str] = None
    marketplace_fees: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    status: str = "completed"


@dataclass
class BadgeMarketListing:
    """Marketplace listing for badge sales."""
    listing_id: str
    badge_instance_id: str
    seller_id: str
    asking_price: Decimal
    listing_date: datetime
    expires_at: datetime
    currency: str = "USD"
    description: str = ""
    status: str = "active"
    buyer_id: Optional[str] = None
    sold_at: Optional[datetime] = None
    final_price: Optional[Decimal] = None


class BadgeMonetizationSystem:
    """
    Enterprise badge monetization system providing automated revenue
    generation through digital badges and skill certifications.
    """
    
    def __init__(self):
        """Initialize the badge monetization system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core storage
        self.badge_definitions: Dict[str, BadgeDefinition] = {}
        self.creator_badges: Dict[str, List[CreatorBadge]] = {}
        self.badge_transactions: Dict[str, List[BadgeTransaction]] = {}
        self.market_listings: Dict[str, BadgeMarketListing] = {}
        
        # Configuration
        self.marketplace_fee_rate = Decimal("0.05")  # 5% marketplace fee
        self.platform_fee_rate = Decimal("0.03")    # 3% platform fee
        self.staking_reward_rate = Decimal("0.001")  # 0.1% daily staking reward
        self.default_listing_duration = timedelta(days=30)
        
        # Rarity multipliers
        self.rarity_multipliers = {
            BadgeRarity.COMMON: 1.0,
            BadgeRarity.UNCOMMON: 1.5,
            BadgeRarity.RARE: 2.5,
            BadgeRarity.EPIC: 5.0,
            BadgeRarity.LEGENDARY: 10.0,
            BadgeRarity.MYTHIC: 25.0
        }
        
        # Analytics
        self.total_badge_revenue = Decimal("0")
        self.total_badges_issued = 0
        self.marketplace_volume = Decimal("0")
        
        self.initialized = False
        self.logger.info("BadgeMonetizationSystem initialized")
    
    async def initialize(self) -> bool:
        """Initialize the badge monetization system."""
        try:
            await self._load_badge_definitions()
            await self._load_creator_badges()
            await self._load_market_data()
            await self._calculate_badge_values()
            
            self.initialized = True
            self.logger.info("BadgeMonetizationSystem initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BadgeMonetizationSystem: {e}")
            return False
    
    async def _load_badge_definitions(self):
        """Load badge definitions from storage."""
        # Initialize default badge definitions
        default_badges = [
            # Skill Certifications
            BadgeDefinition(
                badge_id="content_creator_certified",
                name="Certified Content Creator",
                description="Verified content creation skills",
                badge_type=BadgeType.SKILL_CERTIFICATION,
                rarity=BadgeRarity.UNCOMMON,
                base_value=Decimal("25.00"),
                earning_criteria={"content_count": 50, "quality_score": 4.0},
                verification_requirements={"peer_reviews": 5, "platform_tenure": 90},
                monetization_methods=[
                    BadgeMonetizationMethod.SKILL_PREMIUM,
                    BadgeMonetizationMethod.ACCESS_PRIVILEGES
                ],
                revenue_multiplier=1.1,
                validity_period=timedelta(days=365),
                transferable=True
            ),
            BadgeDefinition(
                badge_id="video_production_expert",
                name="Video Production Expert",
                description="Advanced video production skills",
                badge_type=BadgeType.TECHNICAL_MASTERY,
                rarity=BadgeRarity.RARE,
                base_value=Decimal("100.00"),
                earning_criteria={"video_count": 100, "production_quality": 4.5},
                verification_requirements={"expert_reviews": 3, "portfolio_assessment": True},
                monetization_methods=[
                    BadgeMonetizationMethod.MARKETPLACE_SALES,
                    BadgeMonetizationMethod.SKILL_PREMIUM,
                    BadgeMonetizationMethod.EXCLUSIVE_OPPORTUNITIES
                ],
                revenue_multiplier=1.25,
                validity_period=timedelta(days=730),
                transferable=True,
                max_supply=1000
            ),
            
            # Achievement Badges
            BadgeDefinition(
                badge_id="million_views_club",
                name="Million Views Club",
                description="Achieved over 1 million total views",
                badge_type=BadgeType.ACHIEVEMENT_BADGE,
                rarity=BadgeRarity.EPIC,
                base_value=Decimal("500.00"),
                earning_criteria={"total_views": 1000000},
                verification_requirements={"platform_verification": True},
                monetization_methods=[
                    BadgeMonetizationMethod.MARKETPLACE_SALES,
                    BadgeMonetizationMethod.REVENUE_MULTIPLIER,
                    BadgeMonetizationMethod.BADGE_STAKING
                ],
                revenue_multiplier=1.5,
                transferable=False,
                max_supply=100
            ),
            
            # Community Leadership
            BadgeDefinition(
                badge_id="collaboration_master",
                name="Collaboration Master",
                description="Expert in creator collaborations",
                badge_type=BadgeType.COLLABORATION_EXPERT,
                rarity=BadgeRarity.RARE,
                base_value=Decimal("75.00"),
                earning_criteria={"successful_collaborations": 25, "collaboration_rating": 4.5},
                verification_requirements={"partner_endorsements": 10},
                monetization_methods=[
                    BadgeMonetizationMethod.EXCLUSIVE_OPPORTUNITIES,
                    BadgeMonetizationMethod.SKILL_PREMIUM
                ],
                revenue_multiplier=1.2,
                validity_period=timedelta(days=365),
                transferable=True
            ),
            
            # Innovation Badges
            BadgeDefinition(
                badge_id="ai_innovation_pioneer",
                name="AI Innovation Pioneer",
                description="Pioneer in AI-assisted content creation",
                badge_type=BadgeType.INNOVATION_PIONEER,
                rarity=BadgeRarity.LEGENDARY,
                base_value=Decimal("1000.00"),
                earning_criteria={"ai_usage_score": 4.8, "innovation_projects": 5},
                verification_requirements={"tech_assessment": True, "peer_nominations": 10},
                monetization_methods=[
                    BadgeMonetizationMethod.MARKETPLACE_SALES,
                    BadgeMonetizationMethod.EXCLUSIVE_OPPORTUNITIES,
                    BadgeMonetizationMethod.BADGE_STAKING
                ],
                revenue_multiplier=2.0,
                transferable=True,
                max_supply=50
            )
        ]
        
        for badge in default_badges:
            self.badge_definitions[badge.badge_id] = badge
        
        self.logger.info(f"Loaded {len(self.badge_definitions)} badge definitions")
    
    async def _load_creator_badges(self):
        """Load creator badges from storage."""
        # In production, this would load from database
        self.logger.info("Loading creator badges...")
    
    async def _load_market_data(self):
        """Load marketplace data from storage."""
        # In production, this would load from database
        self.logger.info("Loading marketplace data...")
    
    async def _calculate_badge_values(self):
        """Calculate current market values for all badges."""
        # In production, this would use market data and algorithms
        self.logger.info("Calculating badge values...")
    
    async def award_badge(
        self,
        creator_id: str,
        badge_id: str,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> CreatorBadge:
        """
        Award a badge to a creator.
        
        Args:
            creator_id: Creator identifier
            badge_id: Badge to award
            verification_data: Optional verification data
            
        Returns:
            Created creator badge instance
        """
        try:
            if badge_id not in self.badge_definitions:
                raise ValueError("Badge definition not found")
            
            badge_def = self.badge_definitions[badge_id]
            
            # Check if creator already has this badge (for non-stackable badges)
            if not badge_def.stackable:
                existing_badges = self.creator_badges.get(creator_id, [])
                if any(b.badge_id == badge_id and b.status == BadgeStatus.ACTIVE for b in existing_badges):
                    raise ValueError("Creator already has this badge")
            
            # Check supply limits
            if badge_def.max_supply and badge_def.current_supply >= badge_def.max_supply:
                raise ValueError("Badge supply limit reached")
            
            # Calculate badge value based on rarity
            current_value = await self._calculate_badge_current_value(badge_def)
            
            # Create badge instance
            creator_badge = CreatorBadge(
                badge_instance_id=str(uuid4()),
                creator_id=creator_id,
                badge_id=badge_id,
                earned_date=datetime.utcnow(),
                current_value=current_value,
                metadata=verification_data or {}
            )
            
            # Set expiry if badge has validity period
            if badge_def.validity_period:
                creator_badge.expires_at = datetime.utcnow() + badge_def.validity_period
            
            # Store badge
            if creator_id not in self.creator_badges:
                self.creator_badges[creator_id] = []
            self.creator_badges[creator_id].append(creator_badge)
            
            # Update badge supply
            badge_def.current_supply += 1
            self.total_badges_issued += 1
            
            self.logger.info(f"Awarded badge {badge_def.name} to creator {creator_id}")
            return creator_badge
            
        except Exception as e:
            self.logger.error(f"Error awarding badge: {e}")
            raise
    
    async def _calculate_badge_current_value(self, badge_def: BadgeDefinition) -> Decimal:
        """Calculate current market value of a badge."""
        
        base_value = badge_def.base_value
        rarity_multiplier = Decimal(str(self.rarity_multipliers[badge_def.rarity]))
        
        # Supply scarcity multiplier
        scarcity_multiplier = Decimal("1.0")
        if badge_def.max_supply:
            remaining_ratio = (badge_def.max_supply - badge_def.current_supply) / badge_def.max_supply
            scarcity_multiplier = Decimal("1.0") + (Decimal("1.0") - Decimal(str(remaining_ratio))) * Decimal("0.5")
        
        # Market demand multiplier (simplified)
        demand_multiplier = Decimal("1.0")  # In production, calculate from market data
        
        current_value = base_value * rarity_multiplier * scarcity_multiplier * demand_multiplier
        
        return current_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def verify_badge(
        self,
        badge_instance_id: str,
        verification_score: float,
        verifier_id: str
    ) -> bool:
        """Verify a creator's badge."""
        try:
            # Find badge instance
            creator_badge = None
            for badges in self.creator_badges.values():
                for badge in badges:
                    if badge.badge_instance_id == badge_instance_id:
                        creator_badge = badge
                        break
                if creator_badge:
                    break
            
            if not creator_badge:
                raise ValueError("Badge instance not found")
            
            # Update verification
            creator_badge.verified_date = datetime.utcnow()
            creator_badge.verification_score = verification_score
            creator_badge.status = BadgeStatus.VERIFIED
            
            # Update metadata
            if not creator_badge.metadata:
                creator_badge.metadata = {}
            creator_badge.metadata.update({
                "verifier_id": verifier_id,
                "verification_score": verification_score,
                "verified_at": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Verified badge {creator_badge.badge_id} for creator {creator_badge.creator_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying badge: {e}")
            return False
    
    async def create_marketplace_listing(
        self,
        badge_instance_id: str,
        asking_price: Decimal,
        description: str = "",
        listing_duration: Optional[timedelta] = None
    ) -> BadgeMarketListing:
        """Create a marketplace listing for a badge."""
        try:
            # Find badge instance
            creator_badge = None
            for badges in self.creator_badges.values():
                for badge in badges:
                    if badge.badge_instance_id == badge_instance_id:
                        creator_badge = badge
                        break
                if creator_badge:
                    break
            
            if not creator_badge:
                raise ValueError("Badge instance not found")
            
            # Check if badge is transferable
            badge_def = self.badge_definitions[creator_badge.badge_id]
            if not badge_def.transferable:
                raise ValueError("Badge is not transferable")
            
            # Check badge status
            if creator_badge.status != BadgeStatus.ACTIVE:
                raise ValueError("Badge is not available for sale")
            
            # Create listing
            duration = listing_duration or self.default_listing_duration
            listing = BadgeMarketListing(
                listing_id=str(uuid4()),
                badge_instance_id=badge_instance_id,
                seller_id=creator_badge.creator_id,
                asking_price=asking_price,
                listing_date=datetime.utcnow(),
                expires_at=datetime.utcnow() + duration,
                description=description
            )
            
            # Store listing
            self.market_listings[listing.listing_id] = listing
            
            # Update badge status
            creator_badge.status = BadgeStatus.TRANSFERRED  # Temporarily transferred to marketplace
            
            self.logger.info(f"Created marketplace listing for badge {creator_badge.badge_id}")
            return listing
            
        except Exception as e:
            self.logger.error(f"Error creating marketplace listing: {e}")
            raise
    
    async def purchase_badge(
        self,
        listing_id: str,
        buyer_id: str,
        offered_price: Optional[Decimal] = None
    ) -> BadgeTransaction:
        """Purchase a badge from the marketplace."""
        try:
            if listing_id not in self.market_listings:
                raise ValueError("Listing not found")
            
            listing = self.market_listings[listing_id]
            
            if listing.status != "active":
                raise ValueError("Listing is not active")
            
            if datetime.utcnow() > listing.expires_at:
                listing.status = "expired"
                raise ValueError("Listing has expired")
            
            # Determine final price
            final_price = offered_price if offered_price and offered_price >= listing.asking_price else listing.asking_price
            
            # Calculate fees
            marketplace_fee = final_price * self.marketplace_fee_rate
            platform_fee = final_price * self.platform_fee_rate
            seller_net = final_price - marketplace_fee - platform_fee
            
            # Create transaction
            transaction = BadgeTransaction(
                transaction_id=str(uuid4()),
                badge_instance_id=listing.badge_instance_id,
                creator_id=listing.seller_id,
                transaction_type="sale",
                amount=final_price,
                counterparty_id=buyer_id,
                marketplace_fees=marketplace_fee + platform_fee,
                net_amount=seller_net
            )
            
            # Transfer badge ownership
            await self._transfer_badge_ownership(listing.badge_instance_id, listing.seller_id, buyer_id)
            
            # Update listing
            listing.status = "sold"
            listing.buyer_id = buyer_id
            listing.sold_at = datetime.utcnow()
            listing.final_price = final_price
            
            # Store transaction
            if listing.seller_id not in self.badge_transactions:
                self.badge_transactions[listing.seller_id] = []
            self.badge_transactions[listing.seller_id].append(transaction)
            
            # Update analytics
            self.marketplace_volume += final_price
            self.total_badge_revenue += seller_net
            
            self.logger.info(f"Badge sold for ${final_price}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error purchasing badge: {e}")
            raise
    
    async def _transfer_badge_ownership(self, badge_instance_id: str, from_creator: str, to_creator: str):
        """Transfer badge ownership between creators."""
        
        # Find and remove badge from current owner
        from_badges = self.creator_badges.get(from_creator, [])
        badge_to_transfer = None
        
        for i, badge in enumerate(from_badges):
            if badge.badge_instance_id == badge_instance_id:
                badge_to_transfer = from_badges.pop(i)
                break
        
        if not badge_to_transfer:
            raise ValueError("Badge not found in creator's collection")
        
        # Update badge ownership
        badge_to_transfer.creator_id = to_creator
        badge_to_transfer.status = BadgeStatus.ACTIVE
        
        # Add transfer to history
        badge_to_transfer.transfer_history.append({
            "from": from_creator,
            "to": to_creator,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "marketplace_sale"
        })
        
        # Add to new owner's collection
        if to_creator not in self.creator_badges:
            self.creator_badges[to_creator] = []
        self.creator_badges[to_creator].append(badge_to_transfer)
    
    async def stake_badge(
        self, badge_instance_id: str, staking_duration: timedelta
    ) -> Dict[str, Any]:
        """Stake a badge to earn passive rewards."""
        try:
            # Find badge instance
            creator_badge = None
            for badges in self.creator_badges.values():
                for badge in badges:
                    if badge.badge_instance_id == badge_instance_id:
                        creator_badge = badge
                        break
                if creator_badge:
                    break
            
            if not creator_badge:
                raise ValueError("Badge instance not found")
            
            if creator_badge.status != BadgeStatus.ACTIVE:
                raise ValueError("Badge is not available for staking")
            
            # Calculate staking rewards
            badge_def = self.badge_definitions[creator_badge.badge_id]
            daily_reward = creator_badge.current_value * self.staking_reward_rate
            total_reward = daily_reward * Decimal(str(staking_duration.days))
            
            # Update badge status
            creator_badge.status = BadgeStatus.STAKED
            creator_badge.staking_rewards = total_reward
            
            # Add staking metadata
            if not creator_badge.metadata:
                creator_badge.metadata = {}
            creator_badge.metadata.update({
                "staking_start": datetime.utcnow().isoformat(),
                "staking_duration_days": staking_duration.days,
                "expected_rewards": float(total_reward)
            })
            
            result = {
                "badge_instance_id": badge_instance_id,
                "staking_duration_days": staking_duration.days,
                "daily_reward": float(daily_reward),
                "total_expected_reward": float(total_reward),
                "currency": "USD"
            }
            
            self.logger.info(f"Staked badge {creator_badge.badge_id} for {staking_duration.days} days")
            return result
            
        except Exception as e:
            self.logger.error(f"Error staking badge: {e}")
            raise
    
    async def calculate_creator_badge_value(self, creator_id: str) -> Dict[str, Any]:
        """Calculate total value of creator's badge collection."""
        try:
            creator_badges = self.creator_badges.get(creator_id, [])
            
            if not creator_badges:
                return {"creator_id": creator_id, "total_value": 0.0, "badge_count": 0}
            
            total_value = Decimal("0")
            active_badges = 0
            staked_rewards = Decimal("0")
            
            # Badge breakdown by type and rarity
            type_breakdown = {}
            rarity_breakdown = {}
            
            for badge in creator_badges:
                badge_def = self.badge_definitions.get(badge.badge_id)
                if not badge_def:
                    continue
                
                if badge.status in [BadgeStatus.ACTIVE, BadgeStatus.VERIFIED, BadgeStatus.STAKED]:
                    total_value += badge.current_value or Decimal("0")
                    active_badges += 1
                    
                    if badge.status == BadgeStatus.STAKED:
                        staked_rewards += badge.staking_rewards
                    
                    # Type breakdown
                    badge_type = badge_def.badge_type.value
                    if badge_type not in type_breakdown:
                        type_breakdown[badge_type] = {"count": 0, "value": 0.0}
                    type_breakdown[badge_type]["count"] += 1
                    type_breakdown[badge_type]["value"] += float(badge.current_value or Decimal("0"))
                    
                    # Rarity breakdown
                    rarity = badge_def.rarity.value
                    if rarity not in rarity_breakdown:
                        rarity_breakdown[rarity] = {"count": 0, "value": 0.0}
                    rarity_breakdown[rarity]["count"] += 1
                    rarity_breakdown[rarity]["value"] += float(badge.current_value or Decimal("0"))
            
            # Most valuable badges
            valuable_badges = sorted(
                [b for b in creator_badges if b.current_value],
                key=lambda x: x.current_value,
                reverse=True
            )[:5]
            
            return {
                "creator_id": creator_id,
                "summary": {
                    "total_value": float(total_value),
                    "total_badges": len(creator_badges),
                    "active_badges": active_badges,
                    "staked_rewards": float(staked_rewards),
                    "currency": "USD"
                },
                "breakdown": {
                    "by_type": type_breakdown,
                    "by_rarity": rarity_breakdown
                },
                "top_badges": [
                    {
                        "badge_id": b.badge_id,
                        "name": self.badge_definitions.get(b.badge_id, {}).name if b.badge_id in self.badge_definitions else b.badge_id,
                        "value": float(b.current_value),
                        "status": b.status.value,
                        "earned_date": b.earned_date.isoformat()
                    }
                    for b in valuable_badges
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating creator badge value: {e}")
            return {"error": str(e)}
    
    async def get_marketplace_analytics(self) -> Dict[str, Any]:
        """Get marketplace analytics and trends."""
        try:
            total_listings = len(self.market_listings)
            
            if total_listings == 0:
                return {"message": "No marketplace data found"}
            
            # Listing status distribution
            status_distribution = {}
            for listing in self.market_listings.values():
                status = listing.status
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Calculate average prices by badge type
            badge_type_prices = {}
            for listing in self.market_listings.values():
                if listing.status == "sold" and listing.final_price:
                    # Find badge type
                    badge_instance_id = listing.badge_instance_id
                    badge_type = "unknown"
                    
                    for badges in self.creator_badges.values():
                        for badge in badges:
                            if badge.badge_instance_id == badge_instance_id:
                                badge_def = self.badge_definitions.get(badge.badge_id)
                                if badge_def:
                                    badge_type = badge_def.badge_type.value
                                break
                        if badge_type != "unknown":
                            break
                    
                    if badge_type not in badge_type_prices:
                        badge_type_prices[badge_type] = []
                    badge_type_prices[badge_type].append(float(listing.final_price))
            
            # Calculate averages
            avg_prices = {}
            for badge_type, prices in badge_type_prices.items():
                avg_prices[badge_type] = sum(prices) / len(prices) if prices else 0
            
            # Recent sales
            recent_sales = sorted(
                [l for l in self.market_listings.values() if l.status == "sold"],
                key=lambda x: x.sold_at or datetime.min,
                reverse=True
            )[:10]
            
            return {
                "overview": {
                    "total_listings": total_listings,
                    "active_listings": status_distribution.get("active", 0),
                    "completed_sales": status_distribution.get("sold", 0),
                    "total_volume": float(self.marketplace_volume),
                    "currency": "USD"
                },
                "status_distribution": status_distribution,
                "pricing": {
                    "average_prices_by_type": avg_prices,
                    "highest_sale": float(max((l.final_price for l in self.market_listings.values() if l.final_price), default=0)),
                    "volume_last_30_days": float(self.marketplace_volume)  # Simplified
                },
                "recent_sales": [
                    {
                        "listing_id": sale.listing_id,
                        "price": float(sale.final_price) if sale.final_price else 0,
                        "sold_at": sale.sold_at.isoformat() if sale.sold_at else None
                    }
                    for sale in recent_sales
                ],
                "market_health": {
                    "liquidity_score": min(95.0, 75.0 + (len(recent_sales) / max(total_listings, 1)) * 100),
                    "price_stability": "High",  # Simplified
                    "trading_activity": "Active" if len(recent_sales) > 5 else "Moderate"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting marketplace analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_badge_analytics(self) -> Dict[str, Any]:
        """Get system-wide badge analytics."""
        try:
            total_badges_issued = self.total_badges_issued
            
            if total_badges_issued == 0:
                return {"message": "No badge data found"}
            
            # Badge distribution by type
            type_distribution = {}
            rarity_distribution = {}
            
            for creator_badges in self.creator_badges.values():
                for badge in creator_badges:
                    badge_def = self.badge_definitions.get(badge.badge_id)
                    if badge_def:
                        # Type distribution
                        badge_type = badge_def.badge_type.value
                        type_distribution[badge_type] = type_distribution.get(badge_type, 0) + 1
                        
                        # Rarity distribution
                        rarity = badge_def.rarity.value
                        rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + 1
            
            # Most popular badges
            badge_counts = {}
            for creator_badges in self.creator_badges.values():
                for badge in creator_badges:
                    badge_id = badge.badge_id
                    badge_counts[badge_id] = badge_counts.get(badge_id, 0) + 1
            
            popular_badges = sorted(
                badge_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "overview": {
                    "total_badges_issued": total_badges_issued,
                    "total_badge_types": len(self.badge_definitions),
                    "total_creators_with_badges": len(self.creator_badges),
                    "total_badge_revenue": float(self.total_badge_revenue),
                    "marketplace_volume": float(self.marketplace_volume),
                    "currency": "USD"
                },
                "distributions": {
                    "by_type": type_distribution,
                    "by_rarity": rarity_distribution
                },
                "popular_badges": [
                    {
                        "badge_id": badge_id,
                        "name": self.badge_definitions.get(badge_id, {}).name if badge_id in self.badge_definitions else badge_id,
                        "count": count,
                        "type": self.badge_definitions.get(badge_id, {}).badge_type.value if badge_id in self.badge_definitions else "unknown"
                    }
                    for badge_id, count in popular_badges
                ],
                "economics": {
                    "average_badge_value": float(self.total_badge_revenue / max(total_badges_issued, 1)),
                    "marketplace_activity": len(self.market_listings),
                    "staking_participation": sum(
                        len([b for b in badges if b.status == BadgeStatus.STAKED])
                        for badges in self.creator_badges.values()
                    )
                },
                "system_health": {
                    "badge_economy_score": min(95.0, 80.0 + (len(self.market_listings) / max(total_badges_issued, 1)) * 100),
                    "creator_engagement": "High",
                    "market_liquidity": "Good"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system badge analytics: {e}")
            return {"error": str(e)}


# Global instance
_badge_monetization_system: Optional[BadgeMonetizationSystem] = None

async def get_badge_monetization_system() -> BadgeMonetizationSystem:
    """Get the global badge monetization system instance."""
    global _badge_monetization_system
    
    if _badge_monetization_system is None:
        _badge_monetization_system = BadgeMonetizationSystem()
        await _badge_monetization_system.initialize()
    
    return _badge_monetization_system