"""
Reward Repository - Enterprise Reward Data Management

This module provides comprehensive data access layer for reward management
with advanced tracking, distribution analytics, and business intelligence.

Features:
- High-performance reward data access and distribution tracking
- Advanced reward analytics and ROI calculation
- Real-time reward processing and validation
- Comprehensive reward transaction management
- Cross-platform reward synchronization
- Professional audit trails and compliance
- Integration with achievement and challenge systems
- Reward performance monitoring and optimization

Business Logic Integration:
- Achievement unlock → Reward distribution → Transaction tracking
- Challenge completion → Reward calculation → Business analytics
- Reward distribution → Revenue tracking → Business intelligence
- Reward data → Creator engagement → Monetization optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class RewardType(Enum):
    """Reward type classification"""
    POINTS = "points"
    BADGE = "badge"
    MONETARY = "monetary"
    PREMIUM_ACCESS = "premium_access"
    FEATURE_UNLOCK = "feature_unlock"
    COLLABORATION_BOOST = "collaboration_boost"
    VISIBILITY_BOOST = "visibility_boost"
    CUSTOM_PROFILE = "custom_profile"
    EARLY_ACCESS = "early_access"
    EXCLUSIVE_CONTENT = "exclusive_content"


class RewardStatus(Enum):
    """Reward distribution status"""
    PENDING = "pending"
    DISTRIBUTED = "distributed"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TransactionType(Enum):
    """Transaction type classification"""
    ACHIEVEMENT_REWARD = "achievement_reward"
    CHALLENGE_REWARD = "challenge_reward"
    BONUS_REWARD = "bonus_reward"
    REFERRAL_REWARD = "referral_reward"
    COMPENSATION = "compensation"
    MANUAL_AWARD = "manual_award"


@dataclass
class RewardData:
    """Comprehensive reward data model"""
    reward_id: str
    name: str
    description: str
    reward_type: RewardType
    
    # Value and configuration
    value: Union[int, float, str]
    currency: str = "points"  # points, USD, EUR, etc.
    is_transferable: bool = False
    is_stackable: bool = True
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Requirements and conditions
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    usage_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Display and branding
    icon_url: str = ""
    badge_url: str = ""
    rarity: str = "common"  # common, rare, epic, legendary
    
    # Business metrics
    business_value: float = 0.0
    cost_to_distribute: float = 0.0
    estimated_engagement_boost: float = 0.0
    
    # Analytics
    distribution_count: int = 0
    claim_count: int = 0
    redemption_count: int = 0
    
    # Configuration
    max_distributions: Optional[int] = None
    is_active: bool = True
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewardTransaction:
    """Reward transaction record"""
    transaction_id: str
    user_id: str
    reward_id: str
    transaction_type: TransactionType
    status: RewardStatus
    
    # Value and details
    reward_value: Union[int, float, str]
    currency: str
    quantity: int = 1
    
    # Source information
    source_id: str = ""  # achievement_id, challenge_id, etc.
    source_type: str = ""  # achievement, challenge, etc.
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    distributed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Processing
    processing_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    retry_count: int = 0
    
    # Validation
    validation_status: str = "pending"  # pending, validated, rejected
    validation_data: Dict[str, Any] = field(default_factory=dict)
    
    # Business tracking
    business_impact: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewardQuery:
    """Reward query parameters"""
    reward_ids: Optional[List[str]] = None
    reward_types: Optional[List[RewardType]] = None
    transaction_types: Optional[List[TransactionType]] = None
    statuses: Optional[List[RewardStatus]] = None
    
    # User-specific filters
    user_id: Optional[str] = None
    include_user_transactions: bool = False
    
    # Value filters
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    currency: Optional[str] = None
    
    # Timing filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    active_only: bool = True
    non_expired_only: bool = True
    
    # Source filters
    source_id: Optional[str] = None
    source_type: Optional[str] = None
    
    # Sorting and pagination
    sort_by: str = "created_at"
    sort_desc: bool = True
    limit: int = 50
    offset: int = 0
    
    # Includes
    include_analytics: bool = False
    include_business_metrics: bool = False


class RewardRepository:
    """
    Enterprise-grade reward repository with advanced transaction management
    
    Provides comprehensive reward data access with high-performance
    distribution tracking, analytics, and business intelligence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize reward repository"""
        self.config = config or {}
        
        # Core storage
        self._rewards: Dict[str, RewardData] = {}
        self._transactions: Dict[str, RewardTransaction] = {}
        
        # Performance indices
        self._type_index: Dict[RewardType, Set[str]] = {
            reward_type: set() for reward_type in RewardType
        }
        self._user_index: Dict[str, Set[str]] = {}  # user_id -> transaction_ids
        self._source_index: Dict[str, Set[str]] = {}  # source_id -> transaction_ids
        self._status_index: Dict[RewardStatus, Set[str]] = {
            status: set() for status in RewardStatus
        }
        
        # Caching
        self._query_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._user_rewards_cache: Dict[str, Tuple[datetime, Dict[str, Any]]] = {}
        
        # Analytics
        self._reward_analytics: Dict[str, Dict[str, Any]] = {}
        self._distribution_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl_seconds = self.config.get('cache_ttl_seconds', 300)
        
        logger.info("Reward Repository initialized successfully")
    
    async def create_reward(self, reward_data: RewardData) -> bool:
        """Create a new reward"""
        try:
            reward_id = reward_data.reward_id
            
            if reward_id in self._rewards:
                logger.warning(f"Reward {reward_id} already exists")
                return False
            
            # Store reward
            self._rewards[reward_id] = reward_data
            
            # Update indices
            self._type_index[reward_data.reward_type].add(reward_id)
            
            # Initialize analytics
            await self._initialize_analytics(reward_id)
            
            logger.info(f"Reward {reward_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating reward: {e}")
            return False
    
    async def distribute_reward(
        self,
        user_id: str,
        reward_id: str,
        transaction_type: TransactionType,
        source_id: str = "",
        source_type: str = "",
        quantity: int = 1
    ) -> Optional[str]:
        """Distribute reward to user"""
        try:
            if reward_id not in self._rewards:
                logger.error(f"Reward {reward_id} not found")
                return None
            
            reward = self._rewards[reward_id]
            
            # Check distribution limits
            if reward.max_distributions and reward.distribution_count >= reward.max_distributions:
                logger.warning(f"Reward {reward_id} has reached distribution limit")
                return None
            
            # Check if reward is active
            if not reward.is_active:
                logger.warning(f"Reward {reward_id} is not active")
                return None
            
            # Create transaction
            transaction_id = f"txn_{int(datetime.now(timezone.utc).timestamp())}_{user_id}_{reward_id}"
            
            transaction = RewardTransaction(
                transaction_id=transaction_id,
                user_id=user_id,
                reward_id=reward_id,
                transaction_type=transaction_type,
                status=RewardStatus.PENDING,
                reward_value=reward.value,
                currency=reward.currency,
                quantity=quantity,
                source_id=source_id,
                source_type=source_type,
                expires_at=reward.expires_at
            )
            
            # Store transaction
            self._transactions[transaction_id] = transaction
            
            # Update indices
            if user_id not in self._user_index:
                self._user_index[user_id] = set()
            self._user_index[user_id].add(transaction_id)
            
            if source_id:
                if source_id not in self._source_index:
                    self._source_index[source_id] = set()
                self._source_index[source_id].add(transaction_id)
            
            self._status_index[RewardStatus.PENDING].add(transaction_id)
            
            # Update reward statistics
            reward.distribution_count += 1
            
            # Process distribution
            success = await self._process_reward_distribution(transaction_id)
            
            if success:
                logger.info(f"Reward {reward_id} distributed to user {user_id}")
                return transaction_id
            else:
                logger.error(f"Failed to distribute reward {reward_id} to user {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error distributing reward: {e}")
            return None
    
    async def claim_reward(self, transaction_id: str, user_id: str) -> bool:
        """Claim distributed reward"""
        try:
            if transaction_id not in self._transactions:
                return False
            
            transaction = self._transactions[transaction_id]
            
            # Verify user ownership
            if transaction.user_id != user_id:
                return False
            
            # Check if reward can be claimed
            if transaction.status != RewardStatus.DISTRIBUTED:
                return False
            
            # Check expiration
            if transaction.expires_at and datetime.now(timezone.utc) > transaction.expires_at:
                transaction.status = RewardStatus.EXPIRED
                await self._update_status_index(transaction_id, RewardStatus.DISTRIBUTED, RewardStatus.EXPIRED)
                return False
            
            # Process claim
            success = await self._process_reward_claim(transaction_id)
            
            if success:
                transaction.status = RewardStatus.CLAIMED
                transaction.claimed_at = datetime.now(timezone.utc)
                
                # Update indices
                await self._update_status_index(transaction_id, RewardStatus.DISTRIBUTED, RewardStatus.CLAIMED)
                
                # Update reward statistics
                reward = self._rewards[transaction.reward_id]
                reward.claim_count += 1
                
                # Update analytics
                await self._update_analytics(transaction.reward_id, 'claim', {
                    'user_id': user_id,
                    'transaction_id': transaction_id,
                    'value': transaction.reward_value
                })
                
                # Clear cache
                await self._clear_user_cache(user_id)
                
                logger.info(f"Reward claimed: {transaction_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error claiming reward: {e}")
            return False
    
    async def get_user_rewards(
        self,
        user_id: str,
        include_pending: bool = True,
        include_claimed: bool = True
    ) -> Dict[str, Any]:
        """Get all rewards for user"""
        try:
            # Check cache
            cache_key = f"user_{user_id}_{include_pending}_{include_claimed}"
            if self.cache_enabled and cache_key in self._user_rewards_cache:
                cached_time, cached_data = self._user_rewards_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_time).total_seconds() < self.cache_ttl_seconds:
                    return cached_data
            
            if user_id not in self._user_index:
                return {'user_id': user_id, 'rewards': [], 'summary': {}}
            
            transaction_ids = self._user_index[user_id]
            user_rewards = []
            
            # Counters for summary
            total_value = 0.0
            pending_count = 0
            claimed_count = 0
            expired_count = 0
            
            for transaction_id in transaction_ids:
                transaction = self._transactions[transaction_id]
                reward = self._rewards[transaction.reward_id]
                
                # Apply status filters
                if transaction.status == RewardStatus.PENDING and not include_pending:
                    continue
                if transaction.status == RewardStatus.CLAIMED and not include_claimed:
                    continue
                
                reward_data = {
                    'transaction_id': transaction_id,
                    'reward_id': transaction.reward_id,
                    'reward_name': reward.name,
                    'reward_type': reward.reward_type.value,
                    'value': transaction.reward_value,
                    'currency': transaction.currency,
                    'quantity': transaction.quantity,
                    'status': transaction.status.value,
                    'source_type': transaction.source_type,
                    'source_id': transaction.source_id,
                    'created_at': transaction.created_at.isoformat(),
                    'distributed_at': transaction.distributed_at.isoformat() if transaction.distributed_at else None,
                    'claimed_at': transaction.claimed_at.isoformat() if transaction.claimed_at else None,
                    'expires_at': transaction.expires_at.isoformat() if transaction.expires_at else None,
                    'icon_url': reward.icon_url,
                    'badge_url': reward.badge_url,
                    'rarity': reward.rarity
                }
                
                user_rewards.append(reward_data)
                
                # Update counters
                if transaction.status == RewardStatus.CLAIMED:
                    if isinstance(transaction.reward_value, (int, float)):
                        total_value += transaction.reward_value * transaction.quantity
                    claimed_count += 1
                elif transaction.status == RewardStatus.PENDING:
                    pending_count += 1
                elif transaction.status == RewardStatus.EXPIRED:
                    expired_count += 1
            
            # Sort by creation date (newest first)
            user_rewards.sort(key=lambda x: x['created_at'], reverse=True)
            
            result = {
                'user_id': user_id,
                'rewards': user_rewards,
                'summary': {
                    'total_rewards': len(user_rewards),
                    'total_value': total_value,
                    'pending_count': pending_count,
                    'claimed_count': claimed_count,
                    'expired_count': expired_count
                }
            }
            
            # Cache result
            if self.cache_enabled:
                self._user_rewards_cache[cache_key] = (datetime.now(timezone.utc), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user rewards: {e}")
            return {'user_id': user_id, 'rewards': [], 'summary': {}}
    
    async def get_reward_analytics(
        self,
        reward_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive reward analytics"""
        try:
            if reward_id:
                return await self._get_single_reward_analytics(reward_id, time_range)
            else:
                return await self._get_overall_analytics(time_range)
            
        except Exception as e:
            logger.error(f"Error getting reward analytics: {e}")
            return {}
    
    # Helper methods
    
    async def _process_reward_distribution(self, transaction_id: str) -> bool:
        """Process reward distribution"""
        try:
            transaction = self._transactions[transaction_id]
            
            # Simulate distribution processing
            # In production, this would integrate with payment systems, etc.
            
            transaction.status = RewardStatus.DISTRIBUTED
            transaction.distributed_at = datetime.now(timezone.utc)
            transaction.validation_status = "validated"
            
            # Update status index
            await self._update_status_index(transaction_id, RewardStatus.PENDING, RewardStatus.DISTRIBUTED)
            
            # Update analytics
            await self._update_analytics(transaction.reward_id, 'distribution', {
                'user_id': transaction.user_id,
                'transaction_id': transaction_id,
                'value': transaction.reward_value
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing reward distribution: {e}")
            return False
    
    async def _process_reward_claim(self, transaction_id: str) -> bool:
        """Process reward claim"""
        try:
            transaction = self._transactions[transaction_id]
            reward = self._rewards[transaction.reward_id]
            
            # Simulate claim processing based on reward type
            if reward.reward_type == RewardType.POINTS:
                # Add points to user account
                transaction.processing_data['points_added'] = transaction.reward_value
            elif reward.reward_type == RewardType.MONETARY:
                # Process monetary reward
                transaction.processing_data['payment_processed'] = True
            elif reward.reward_type == RewardType.PREMIUM_ACCESS:
                # Grant premium access
                transaction.processing_data['access_granted'] = True
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing reward claim: {e}")
            return False
    
    async def _update_status_index(
        self,
        transaction_id: str,
        old_status: RewardStatus,
        new_status: RewardStatus
    ) -> None:
        """Update status index"""
        try:
            self._status_index[old_status].discard(transaction_id)
            self._status_index[new_status].add(transaction_id)
            
        except Exception as e:
            logger.error(f"Error updating status index: {e}")
    
    # Analytics methods
    
    async def _initialize_analytics(self, reward_id: str) -> None:
        """Initialize analytics for reward"""
        try:
            self._reward_analytics[reward_id] = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'distribution_events': [],
                'claim_events': [],
                'daily_stats': {}
            }
            
        except Exception as e:
            logger.error(f"Error initializing analytics: {e}")
    
    async def _update_analytics(
        self,
        reward_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Update reward analytics"""
        try:
            if reward_id not in self._reward_analytics:
                await self._initialize_analytics(reward_id)
            
            analytics = self._reward_analytics[reward_id]
            
            event = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': event_type,
                'data': event_data
            }
            
            if event_type == 'distribution':
                analytics['distribution_events'].append(event)
            elif event_type == 'claim':
                analytics['claim_events'].append(event)
            
            # Update daily stats
            today = datetime.now(timezone.utc).date().isoformat()
            if today not in analytics['daily_stats']:
                analytics['daily_stats'][today] = {
                    'distributions': 0,
                    'claims': 0,
                    'unique_users': set(),
                    'total_value_distributed': 0.0,
                    'total_value_claimed': 0.0
                }
            
            daily_stats = analytics['daily_stats'][today]
            if event_type == 'distribution':
                daily_stats['distributions'] += 1
                if 'value' in event_data and isinstance(event_data['value'], (int, float)):
                    daily_stats['total_value_distributed'] += event_data['value']
            elif event_type == 'claim':
                daily_stats['claims'] += 1
                if 'value' in event_data and isinstance(event_data['value'], (int, float)):
                    daily_stats['total_value_claimed'] += event_data['value']
            
            if 'user_id' in event_data:
                daily_stats['unique_users'].add(event_data['user_id'])
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def _get_single_reward_analytics(
        self,
        reward_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Get analytics for single reward"""
        try:
            if reward_id not in self._reward_analytics:
                return {}
            
            analytics = self._reward_analytics[reward_id]
            reward = self._rewards[reward_id]
            
            return {
                'reward_id': reward_id,
                'basic_info': {
                    'name': reward.name,
                    'type': reward.reward_type.value,
                    'value': reward.value,
                    'distribution_count': reward.distribution_count,
                    'claim_count': reward.claim_count,
                    'claim_rate': (reward.claim_count / reward.distribution_count * 100) if reward.distribution_count > 0 else 0
                },
                'events': {
                    'total_distributions': len(analytics['distribution_events']),
                    'total_claims': len(analytics['claim_events']),
                    'recent_events': (analytics['distribution_events'] + analytics['claim_events'])[-20:]
                },
                'daily_stats': analytics['daily_stats']
            }
            
        except Exception as e:
            logger.error(f"Error getting single reward analytics: {e}")
            return {}
    
    async def _get_overall_analytics(
        self,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Get overall reward analytics"""
        try:
            total_rewards = len(self._rewards)
            total_transactions = len(self._transactions)
            
            # Count by status
            status_counts = {}
            for status in RewardStatus:
                status_counts[status.value] = len(self._status_index[status])
            
            # Count by type
            type_counts = {}
            total_value_distributed = 0.0
            total_value_claimed = 0.0
            
            for reward_type in RewardType:
                type_counts[reward_type.value] = len(self._type_index[reward_type])
            
            # Calculate value metrics
            for transaction in self._transactions.values():
                if isinstance(transaction.reward_value, (int, float)):
                    if transaction.status in [RewardStatus.DISTRIBUTED, RewardStatus.CLAIMED]:
                        total_value_distributed += transaction.reward_value * transaction.quantity
                    if transaction.status == RewardStatus.CLAIMED:
                        total_value_claimed += transaction.reward_value * transaction.quantity
            
            return {
                'summary': {
                    'total_rewards': total_rewards,
                    'total_transactions': total_transactions,
                    'total_value_distributed': total_value_distributed,
                    'total_value_claimed': total_value_claimed,
                    'claim_rate': (total_value_claimed / total_value_distributed * 100) if total_value_distributed > 0 else 0
                },
                'distribution_by_status': status_counts,
                'distribution_by_type': type_counts,
                'top_rewards': await self._get_top_performing_rewards()
            }
            
        except Exception as e:
            logger.error(f"Error getting overall analytics: {e}")
            return {}
    
    async def _get_top_performing_rewards(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing rewards"""
        try:
            reward_performance = []
            
            for reward_id, reward in self._rewards.items():
                performance_score = (
                    reward.distribution_count * 0.3 +
                    reward.claim_count * 0.5 +
                    (reward.claim_count / max(reward.distribution_count, 1)) * 100 * 0.2
                )
                
                reward_performance.append({
                    'reward_id': reward_id,
                    'name': reward.name,
                    'type': reward.reward_type.value,
                    'distribution_count': reward.distribution_count,
                    'claim_count': reward.claim_count,
                    'claim_rate': (reward.claim_count / reward.distribution_count * 100) if reward.distribution_count > 0 else 0,
                    'performance_score': performance_score
                })
            
            # Sort by performance score
            reward_performance.sort(key=lambda x: x['performance_score'], reverse=True)
            
            return reward_performance[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top performing rewards: {e}")
            return []
    
    # Cache management
    
    async def _clear_user_cache(self, user_id: str) -> None:
        """Clear cache for specific user"""
        try:
            keys_to_remove = [k for k in self._user_rewards_cache if k.startswith(f"user_{user_id}")]
            for key in keys_to_remove:
                del self._user_rewards_cache[key]
                
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")