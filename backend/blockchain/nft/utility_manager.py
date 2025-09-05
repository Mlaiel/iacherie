"""Utility Manager - IA-Influencer-Agent Platform

Comprehensive NFT utility management system for adding,
managing, and executing NFT-based functionalities.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class UtilityType(Enum):
    ACCESS_TOKEN = "access_token"
    MEMBERSHIP = "membership"
    GOVERNANCE = "governance"
    REWARDS = "rewards"
    GAMING = "gaming"
    CONTENT_UNLOCK = "content_unlock"

@dataclass
class NFTUtility:
    utility_id: str
    token_id: str
    utility_type: UtilityType
    utility_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int
    max_uses: Optional[int]

class UtilityManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.nft_utilities: Dict[str, List[NFTUtility]] = {}
        self.utility_registry: Dict[str, NFTUtility] = {}
    
    async def add_utility(
        self,
        token_id: str,
        utility_type: UtilityType,
        utility_data: Dict[str, Any],
        expires_at: Optional[datetime] = None,
        max_uses: Optional[int] = None
    ) -> NFTUtility:
        try:
            import uuid
            utility_id = str(uuid.uuid4())
            
            utility = NFTUtility(
                utility_id=utility_id,
                token_id=token_id,
                utility_type=utility_type,
                utility_data=utility_data,
                is_active=True,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                usage_count=0,
                max_uses=max_uses
            )
            
            # Add to token utilities
            if token_id not in self.nft_utilities:
                self.nft_utilities[token_id] = []
            
            self.nft_utilities[token_id].append(utility)
            self.utility_registry[utility_id] = utility
            
            self.logger.info(f"Utility added to NFT: {token_id} - {utility_type.value}")
            return utility
            
        except Exception as e:
            self.logger.error(f"Utility addition failed: {e}")
            raise
    
    async def use_utility(
        self,
        utility_id: str,
        user_address: str,
        usage_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            if utility_id not in self.utility_registry:
                raise ValueError(f"Utility not found: {utility_id}")
            
            utility = self.utility_registry[utility_id]
            
            # Check if utility is active
            if not utility.is_active:
                raise ValueError("Utility is not active")
            
            # Check expiration
            if utility.expires_at and datetime.utcnow() > utility.expires_at:
                utility.is_active = False
                raise ValueError("Utility has expired")
            
            # Check usage limits
            if utility.max_uses and utility.usage_count >= utility.max_uses:
                utility.is_active = False
                raise ValueError("Utility usage limit reached")
            
            # Execute utility function
            execution_result = await self._execute_utility(utility, user_address, usage_context)
            
            # Update usage count
            utility.usage_count += 1
            
            result = {
                "utility_id": utility_id,
                "token_id": utility.token_id,
                "utility_type": utility.utility_type.value,
                "used_by": user_address,
                "used_at": datetime.utcnow().isoformat(),
                "usage_count": utility.usage_count,
                "execution_result": execution_result
            }
            
            self.logger.info(f"Utility used: {utility_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Utility usage failed: {e}")
            raise
    
    async def _execute_utility(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute utility-specific functionality"""
        execution_handlers = {
            UtilityType.ACCESS_TOKEN: self._execute_access_token,
            UtilityType.MEMBERSHIP: self._execute_membership,
            UtilityType.GOVERNANCE: self._execute_governance,
            UtilityType.REWARDS: self._execute_rewards,
            UtilityType.CONTENT_UNLOCK: self._execute_content_unlock
        }
        
        handler = execution_handlers.get(utility.utility_type)
        if handler:
            return await handler(utility, user_address, context)
        else:
            return {"status": "executed", "message": "Generic utility execution"}
    
    async def _execute_access_token(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute access token utility"""
        return {
            "access_granted": True,
            "access_level": utility.utility_data.get("access_level", "basic"),
            "expires_in": 3600  # 1 hour
        }
    
    async def _execute_membership(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute membership utility"""
        return {
            "membership_activated": True,
            "tier": utility.utility_data.get("tier", "standard"),
            "benefits": utility.utility_data.get("benefits", [])
        }
    
    async def _execute_governance(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute governance utility"""
        return {
            "voting_power": utility.utility_data.get("voting_power", 1),
            "governance_access": True
        }
    
    async def _execute_rewards(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute rewards utility"""
        reward_amount = utility.utility_data.get("reward_amount", 10)
        return {
            "reward_claimed": True,
            "reward_amount": reward_amount,
            "reward_type": utility.utility_data.get("reward_type", "points")
        }
    
    async def _execute_content_unlock(
        self,
        utility: NFTUtility,
        user_address: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute content unlock utility"""
        return {
            "content_unlocked": True,
            "content_id": utility.utility_data.get("content_id"),
            "access_duration": utility.utility_data.get("access_duration", "unlimited")
        }
    
    async def get_token_utilities(self, token_id: str) -> List[NFTUtility]:
        """Get all utilities for a specific token"""
        return self.nft_utilities.get(token_id, [])
    
    async def deactivate_utility(self, utility_id: str, reason: str) -> Dict[str, Any]:
        """Deactivate a utility"""
        try:
            if utility_id not in self.utility_registry:
                raise ValueError(f"Utility not found: {utility_id}")
            
            utility = self.utility_registry[utility_id]
            utility.is_active = False
            
            result = {
                "utility_id": utility_id,
                "deactivated": True,
                "reason": reason,
                "deactivated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Utility deactivated: {utility_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Utility deactivation failed: {e}")
            raise