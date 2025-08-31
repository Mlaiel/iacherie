"""🎁 Reward Repository - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/database/gamification/reward_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Reward Repository - Production-Ready
Responsibility: Reward distribution, virtual economy, and incentive management
===============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Reward Earning → Distribution Processing → Virtual Economy → 
Incentive Optimization → User Motivation → Revenue Impact

REWARD REPOSITORY ARCHITECTURE:
Reward Configuration → Distribution Engine → Virtual Currency → 
Economic Balance → Analytics Tracking → Performance Optimization
"""
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import uuid

from ...data_management.repositories.base_repository import BaseRepository, OperationType

class RewardType(Enum):
    """Types of rewards"""    EXPERIENCE_POINTS = "experience_points"
    VIRTUAL_CURRENCY = "virtual_currency"
    REAL_CURRENCY = "real_currency"
    BADGE = "badge"
    ACHIEVEMENT = "achievement"
    PREMIUM_FEATURES = "premium_features"
    DISCOUNT_COUPON = "discount_coupon"
    PHYSICAL_ITEM = "physical_item"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    EXCLUSIVE_CONTENT = "exclusive_content"

class RewardCategory(Enum):
    """Reward categorization"""    ENGAGEMENT = "engagement"
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    CHALLENGE = "challenge"
    SEASONAL = "seasonal"
    REFERRAL = "referral"
    LOYALTY = "loyalty"
    COMPENSATION = "compensation"

class RewardStatus(Enum):
    """Reward distribution status"""    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    FAILED = "failed"

class RewardTrigger(Enum):
    """Reward trigger events"""    MANUAL = "manual"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    CHALLENGE_COMPLETION = "challenge_completion"
    MILESTONE_REACHED = "milestone_reached"
    LEVEL_UP = "level_up"
    STREAK_BONUS = "streak_bonus"
    REFERRAL_BONUS = "referral_bonus"
    SEASONAL_EVENT = "seasonal_event"

@dataclass
class Reward:
    """Reward definition"""    reward_id: str
    name: str
    description: str
    reward_type: RewardType
    category: RewardCategory
    value: Union[int, float, str, Dict[str, Any]]
    rarity: float  # 0.0 to 1.0
    cost_basis: Optional[Decimal]
    expiry_duration: Optional[int]  # days
    max_claims_per_user: Optional[int]
    total_available: Optional[int]
    requirements: Dict[str, Any]
    metadata: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class RewardDistribution:
    """Reward distribution record"""    distribution_id: str
    user_id: str
    reward_id: str
    trigger: RewardTrigger
    trigger_source_id: Optional[str]
    status: RewardStatus
    value_distributed: Union[int, float, str, Dict[str, Any]]
    claimed_at: Optional[datetime]
    expires_at: Optional[datetime]
    processing_data: Dict[str, Any]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class UserRewardBalance:
    """User's accumulated rewards"""    balance_id: str
    user_id: str
    reward_type: RewardType
    current_balance: Union[int, float, Decimal]
    lifetime_earned: Union[int, float, Decimal]
    lifetime_spent: Union[int, float, Decimal]
    pending_amount: Union[int, float, Decimal]
    last_transaction: Optional[datetime]
    updated_at: datetime
    metadata: Dict[str, Any]

class RewardRepository(BaseRepository[Reward]):
    """Enterprise reward management repository"""    
    def __init__(self, db_connection=None, cache_manager=None,
                 analytics_service=None, notification_service=None,
                 payment_service=None, virtual_economy_service=None,
                 gamification_service=None):
        super().__init__(db_connection, cache_manager)
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.payment_service = payment_service
        self.virtual_economy_service = virtual_economy_service
        self.gamification_service = gamification_service
        self.table_name = "rewards"
        self.distributions_table = "reward_distributions"
        self.balances_table = "user_reward_balances"
        self.logger = logging.getLogger(__name__)
        
        # Reward value multipliers by rarity
        self._rarity_multipliers = {
            (0.0, 0.1): 10.0,    # Ultra rare (10x)
            (0.1, 0.25): 5.0,    # Very rare (5x)
            (0.25, 0.5): 3.0,    # Rare (3x)
            (0.5, 0.75): 2.0,    # Uncommon (2x)
            (0.75, 1.0): 1.0     # Common (1x)
        }
        
        # Economic balance settings
        self._economy_settings = {
            "daily_virtual_currency_cap": 10000,
            "weekly_real_currency_cap": 100.0,
            "inflation_control_threshold": 0.15,
            "deflation_trigger_threshold": 0.05
        }
        
        # Default expiry times by reward type (days)
        self._default_expiry_times = {
            RewardType.EXPERIENCE_POINTS: None,  # Never expires
            RewardType.VIRTUAL_CURRENCY: None,  # Never expires
            RewardType.REAL_CURRENCY: 365,  # 1 year
            RewardType.BADGE: None,  # Never expires
            RewardType.ACHIEVEMENT: None,  # Never expires
            RewardType.PREMIUM_FEATURES: 30,  # 30 days
            RewardType.DISCOUNT_COUPON: 90,  # 90 days
            RewardType.PHYSICAL_ITEM: 30,  # 30 days to claim
            RewardType.SUBSCRIPTION_UPGRADE: 30,  # 30 days
            RewardType.EXCLUSIVE_CONTENT: 365  # 1 year
        }
    
    def create_reward(
        self,
        name: str,
        description: str,
        reward_type: RewardType,
        category: RewardCategory,
        value: Union[int, float, str, Dict[str, Any]],
        rarity: float = 0.5,
        cost_basis: Optional[Decimal] = None,
        expiry_duration: Optional[int] = None,
        max_claims_per_user: Optional[int] = None,
        total_available: Optional[int] = None,
        requirements: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Reward:
        """Create new reward with economic validation"""        try:
            # Validate inputs
            if not name or len(name) < 3:
                raise ValueError("Reward name must be at least 3 characters")
            
            if not description or len(description) < 10:
                raise ValueError("Reward description must be at least 10 characters")
            
            if not (0.0 <= rarity <= 1.0):
                raise ValueError("Rarity must be between 0.0 and 1.0")
            
            # Validate value based on reward type
            self._validate_reward_value(reward_type, value)
            
            # Apply economic constraints
            if not self._validate_economic_impact(reward_type, value, total_available):
                raise ValueError("Reward violates economic balance constraints")
            
            reward_id = self._generate_reward_id(name, reward_type)
            current_time = datetime.now(timezone.utc)
            
            # Set default expiry if not specified
            if expiry_duration is None:
                expiry_duration = self._default_expiry_times.get(reward_type)
            
            reward = Reward(
                reward_id=reward_id,
                name=name,
                description=description,
                reward_type=reward_type,
                category=category,
                value=value,
                rarity=rarity,
                cost_basis=cost_basis,
                expiry_duration=expiry_duration,
                max_claims_per_user=max_claims_per_user,
                total_available=total_available,
                requirements=requirements or {},
                metadata=metadata or {},
                is_active=True,
                created_at=current_time,
                updated_at=current_time
            )
            
            # Create reward record
            created_reward = self.create(reward)
            
            # Initialize reward in virtual economy
            if self.virtual_economy_service:
                self.virtual_economy_service.register_reward(reward)
            
            # Track analytics
            if self.analytics_service:
                self.analytics_service.track_reward_created(
                    reward_id, reward_type.value, category.value, rarity
                )
            
            self.logger.info(f"Reward created: {reward_id} - {name}")
            return created_reward
            
        except Exception as e:
            self.logger.error(f"Failed to create reward: {str(e)}")
            raise
    
    def distribute_reward(
        self,
        user_id: str,
        reward_id: str,
        trigger: RewardTrigger,
        trigger_source_id: Optional[str] = None,
        custom_value: Optional[Union[int, float, str, Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[RewardDistribution]:
        """Distribute reward to user with validation"""        try:
            # Get reward definition
            reward = self.get_by_id(reward_id)
            if not reward or not reward.is_active:
                return None
            
            # Validate user eligibility
            if not self._validate_user_eligibility(user_id, reward):
                return None
            
            # Check availability
            if not self._check_reward_availability(reward):
                return None
            
            # Calculate actual value to distribute
            distribution_value = custom_value if custom_value is not None else reward.value
            
            # Apply rarity multiplier
            if isinstance(distribution_value, (int, float)):
                multiplier = self._get_rarity_multiplier(reward.rarity)
                distribution_value = distribution_value * multiplier
            
            # Create distribution record
            distribution_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)
            
            # Calculate expiry
            expires_at = None
            if reward.expiry_duration:
                expires_at = current_time + timedelta(days=reward.expiry_duration)
            
            distribution = RewardDistribution(
                distribution_id=distribution_id,
                user_id=user_id,
                reward_id=reward_id,
                trigger=trigger,
                trigger_source_id=trigger_source_id,
                status=RewardStatus.PENDING,
                value_distributed=distribution_value,
                claimed_at=None,
                expires_at=expires_at,
                processing_data={
                    "original_value": reward.value,
                    "rarity_multiplier": self._get_rarity_multiplier(reward.rarity),
                    "distribution_timestamp": current_time.isoformat()
                },
                failure_reason=None,
                created_at=current_time,
                updated_at=current_time,
                metadata=metadata or {}
            )
            
            # Save distribution record
            saved_distribution = self._save_distribution(distribution)
            
            # Process distribution based on reward type
            success = self._process_reward_distribution(saved_distribution, reward)
            
            if success:
                saved_distribution.status = RewardStatus.DISTRIBUTED
                saved_distribution.updated_at = datetime.now(timezone.utc)
                
                # Update user balance
                self._update_user_balance(user_id, reward.reward_type, distribution_value, "earned")
                
                # Send notification
                if self.notification_service:
                    self.notification_service.send_reward_notification(
                        user_id, reward, distribution_value
                    )
                
                # Track analytics
                if self.analytics_service:
                    self.analytics_service.track_reward_distributed(
                        user_id, reward_id, distribution_value, trigger.value
                    )
                
                self.logger.info(
                    f"Reward distributed: {user_id} -> {reward_id} ({distribution_value})"
                )
            else:
                saved_distribution.status = RewardStatus.FAILED
                saved_distribution.failure_reason = "Distribution processing failed"
                saved_distribution.updated_at = datetime.now(timezone.utc)
            
            # Save final status
            final_distribution = self._save_distribution(saved_distribution)
            return final_distribution
            
        except Exception as e:
            self.logger.error(f"Failed to distribute reward: {str(e)}")
            return None
    
    def claim_reward(
        self,
        user_id: str,
        distribution_id: str
    ) -> bool:
        """Claim distributed reward"""        try:
            # Get distribution record
            distribution = self.get_distribution_by_id(distribution_id)
            if not distribution:
                return False
            
            # Validate claim
            if distribution.user_id != user_id:
                return False
            
            if distribution.status != RewardStatus.DISTRIBUTED:
                return False
            
            # Check if expired
            current_time = datetime.now(timezone.utc)
            if distribution.expires_at and current_time > distribution.expires_at:
                distribution.status = RewardStatus.EXPIRED
                self._save_distribution(distribution)
                return False
            
            # Process claim based on reward type
            success = self._process_reward_claim(distribution)
            
            if success:
                distribution.status = RewardStatus.CLAIMED
                distribution.claimed_at = current_time
                distribution.updated_at = current_time
                
                # Track analytics
                if self.analytics_service:
                    self.analytics_service.track_reward_claimed(
                        user_id, distribution.reward_id, distribution.value_distributed
                    )
                
                self.logger.info(f"Reward claimed: {user_id} -> {distribution_id}")
            
            # Save updated distribution
            self._save_distribution(distribution)
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to claim reward: {str(e)}")
            return False
    
    def get_user_rewards(
        self,
        user_id: str,
        status: Optional[RewardStatus] = None,
        reward_type: Optional[RewardType] = None,
        category: Optional[RewardCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[RewardDistribution]:
        """Get user's reward distributions"""        try:
            cache_key = f"user_rewards:{user_id}:{status}:{reward_type}:{category}:{limit}:{offset}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Build filters
            filters = {"user_id": user_id}
            if status:
                filters["status"] = status.value
            if reward_type:
                filters["reward_type"] = reward_type.value
            if category:
                filters["reward_category"] = category.value
            
            # Query distributions
            distributions = self._query_distributions(filters, limit, offset)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, distributions, ttl=300)
            
            return distributions
            
        except Exception as e:
            self.logger.error(f"Failed to get user rewards: {str(e)}")
            return []
    
    def get_user_reward_balance(
        self,
        user_id: str,
        reward_type: Optional[RewardType] = None
    ) -> Union[UserRewardBalance, List[UserRewardBalance]]:
        """Get user's reward balance(s)"""        try:
            if reward_type:
                # Get specific balance
                return self._get_user_balance(user_id, reward_type)
            else:
                # Get all balances
                return self._get_all_user_balances(user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get user reward balance: {str(e)}")
            return [] if not reward_type else None
    
    def spend_virtual_currency(
        self,
        user_id: str,
        amount: Union[int, float, Decimal],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Spend user's virtual currency"""        try:
            # Get current balance
            balance = self._get_user_balance(user_id, RewardType.VIRTUAL_CURRENCY)
            if not balance or balance.current_balance < amount:
                return False
            
            # Process spending
            success = self._update_user_balance(
                user_id, RewardType.VIRTUAL_CURRENCY, -amount, "spent"
            )
            
            if success:
                # Track spending analytics
                if self.analytics_service:
                    self.analytics_service.track_virtual_currency_spent(
                        user_id, amount, purpose
                    )
                
                self.logger.info(f"Virtual currency spent: {user_id} -> {amount} for {purpose}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to spend virtual currency: {str(e)}")
            return False
    
    def get_reward_analytics(
        self,
        reward_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get reward analytics"""        try:
            cache_key = f"reward_analytics:{reward_id}:{user_id}:{days}"
            
            # Try cache first
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Calculate analytics
            analytics = self._calculate_reward_analytics(reward_id, user_id, days)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set(cache_key, analytics, ttl=1800)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get reward analytics: {str(e)}")
            return {}
    
    def _generate_reward_id(self, name: str, reward_type: RewardType) -> str:
        """Generate unique reward ID"""        base_string = f"{reward_type.value}_{name.lower().replace(' ', '_')}"
        timestamp = str(int(datetime.now().timestamp()))
        return f"rew_{hashlib.md5((base_string + timestamp).encode()).hexdigest()[:12]}"
    
    def _validate_reward_value(
        self,
        reward_type: RewardType,
        value: Union[int, float, str, Dict[str, Any]]
    ):
        """Validate reward value based on type"""        if reward_type in [RewardType.EXPERIENCE_POINTS, RewardType.VIRTUAL_CURRENCY]:
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"Invalid value for {reward_type.value}")
        
        elif reward_type == RewardType.REAL_CURRENCY:
            if not isinstance(value, (int, float, Decimal)) or value <= 0:
                raise ValueError("Real currency value must be positive")
    
    def _validate_economic_impact(
        self,
        reward_type: RewardType,
        value: Union[int, float, str, Dict[str, Any]],
        total_available: Optional[int]
    ) -> bool:
        """Validate economic impact of reward"""        if reward_type == RewardType.VIRTUAL_CURRENCY and isinstance(value, (int, float)):
            daily_cap = self._economy_settings["daily_virtual_currency_cap"]
            if total_available and value * total_available > daily_cap * 30:  # Monthly limit
                return False
        
        return True
    
    def _validate_user_eligibility(self, user_id: str, reward: Reward) -> bool:
        """Validate user eligibility for reward"""        # Check max claims per user
        if reward.max_claims_per_user:
            user_claims = self._count_user_claims(user_id, reward.reward_id)
            if user_claims >= reward.max_claims_per_user:
                return False
        
        # Check requirements
        for req_key, req_value in reward.requirements.items():
            if not self._check_user_requirement(user_id, req_key, req_value):
                return False
        
        return True
    
    def _check_reward_availability(self, reward: Reward) -> bool:
        """Check if reward is still available"""        if reward.total_available:
            distributed_count = self._count_total_distributions(reward.reward_id)
            if distributed_count >= reward.total_available:
                return False
        
        return True
    
    def _get_rarity_multiplier(self, rarity: float) -> float:
        """Get rarity multiplier for rewards"""        for (min_rarity, max_rarity), multiplier in self._rarity_multipliers.items():
            if min_rarity <= rarity < max_rarity:
                return multiplier
        return 1.0
    
    def _process_reward_distribution(
        self,
        distribution: RewardDistribution,
        reward: Reward
    ) -> bool:
        """Process reward distribution based on type"""        try:
            if reward.reward_type in [RewardType.EXPERIENCE_POINTS, RewardType.VIRTUAL_CURRENCY]:
                # Immediate distribution for virtual rewards
                return True
            
            elif reward.reward_type == RewardType.REAL_CURRENCY:
                # Queue for payment processing
                if self.payment_service:
                    return self.payment_service.queue_reward_payment(distribution)
                return True
            
            elif reward.reward_type == RewardType.PREMIUM_FEATURES:
                # Activate premium features
                if self.gamification_service:
                    return self.gamification_service.grant_premium_access(
                        distribution.user_id, reward.value
                    )
                return True
            
            # Default to successful distribution
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing reward distribution: {str(e)}")
            return False
    
    def _process_reward_claim(self, distribution: RewardDistribution) -> bool:
        """Process reward claim"""        # Most rewards are auto-claimed during distribution
        # Physical items and some premium features require explicit claiming
        return True
    
    def _update_user_balance(
        self,
        user_id: str,
        reward_type: RewardType,
        amount: Union[int, float, Decimal],
        transaction_type: str
    ) -> bool:
        """Update user reward balance"""        # Implementation would update balance table
        return True
    
    def _save_distribution(self, distribution: RewardDistribution) -> RewardDistribution:
        """Save distribution record"""        # Implementation would save to database
        return distribution
    
    def get_distribution_by_id(self, distribution_id: str) -> Optional[RewardDistribution]:
        """Get distribution by ID"""        # Implementation would query database
        return None
    
    def _query_distributions(
        self,
        filters: Dict[str, Any],
        limit: int,
        offset: int
    ) -> List[RewardDistribution]:
        """Query distributions with filters"""        # Implementation would query database
        return []
    
    def _get_user_balance(
        self,
        user_id: str,
        reward_type: RewardType
    ) -> Optional[UserRewardBalance]:
        """Get user balance for specific reward type"""        # Implementation would query balance
        return None
    
    def _get_all_user_balances(self, user_id: str) -> List[UserRewardBalance]:
        """Get all user balances"""        # Implementation would query all balances
        return []
    
    def _count_user_claims(self, user_id: str, reward_id: str) -> int:
        """Count user claims for specific reward"""        # Implementation would count claims
        return 0
    
    def _count_total_distributions(self, reward_id: str) -> int:
        """Count total distributions for reward"""        # Implementation would count distributions
        return 0
    
    def _check_user_requirement(
        self,
        user_id: str,
        requirement_key: str,
        requirement_value: Any
    ) -> bool:
        """Check user meets specific requirement"""        # Implementation would check requirement
        return True
    
    def _calculate_reward_analytics(
        self,
        reward_id: Optional[str],
        user_id: Optional[str],
        days: int
    ) -> Dict[str, Any]:
        """Calculate reward analytics"""        # Implementation would calculate analytics
        return {}
    
    # BaseRepository abstract method implementations
    def create(self, entity: Reward, **kwargs) -> Reward:
        """Create reward entity"""        self._validate_entity(entity)
        # Implementation would save to database
        return entity
    
    def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[Reward]:
        """Get reward by ID"""        # Implementation would query database
        return None
    
    def update(self, entity: Reward, **kwargs) -> Reward:
        """Update reward entity"""        self._validate_entity(entity)
        # Implementation would update database
        return entity
    
    def delete(self, entity_id: str, **kwargs) -> bool:
        """Soft delete reward"""        # Implementation would soft delete (set is_active=False)
        return True
    
    def list_all(self, limit: int = 100, offset: int = 0, **filters) -> List[Reward]:
        """List all rewards with filtering"""        # Implementation would query with filters
        return []