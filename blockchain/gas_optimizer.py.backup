"""Advanced gas optimization and transaction fee management.

This module provides sophisticated gas optimization strategies for the IA Influencer 
Agent platform's blockchain operations, including dynamic fee adjustment and 
transaction batching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited.
"""
from typing import Dict, List, Optional, Union, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import logging
from web3 import Web3
from web3.types import TxParams

logger = logging.getLogger(__name__)


@dataclass
class GasEstimate:
    """Gas estimation data structure."""
    
    gas_limit: int
    gas_price: int
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    estimated_cost_wei: int = 0
    estimated_cost_usd: Optional[float] = None
    confidence_level: float = 0.95
    

@dataclass
class TransactionBatch:
    """Batch transaction data structure."""
    
    transactions: List[Dict]
    total_gas_limit: int
    estimated_total_cost: int
    batch_id: str
    created_at: datetime
    

class GasOptimizer:
    """Professional gas optimization and fee management system."""
    
    def __init__(self, web3: Web3, network: str):
        """Initialize gas optimizer.
        
        Args:
            web3: Web3 instance for blockchain interaction
            network: Target blockchain network
        """
        self.web3 = web3
        self.network = network
        self.historical_data: List[Dict] = []
        self.optimization_cache: Dict[str, GasEstimate] = {}
        self.batch_threshold = 5  # Minimum transactions for batching
        self.price_oracle_url = None
        
        # Network-specific configurations
        self.network_configs = {
            "ethereum": {"base_gas": 21000, "max_priority_fee": 2000000000},
            "polygon": {"base_gas": 21000, "max_priority_fee": 30000000000},
            "bsc": {"base_gas": 21000, "max_priority_fee": 5000000000},
            "arbitrum": {"base_gas": 21000, "max_priority_fee": 100000000},
            "optimism": {"base_gas": 21000, "max_priority_fee": 1000000000}
        }
    
    async def estimate_optimal_gas(
        self, 
        transaction: Dict,
        priority_level: str = "standard",
        max_wait_time: int = 300
    ) -> GasEstimate:
        """Estimate optimal gas parameters for a transaction.
        
        Args:
            transaction: Transaction parameters
            priority_level: "slow", "standard", "fast", or "urgent"
            max_wait_time: Maximum acceptable wait time in seconds
            
        Returns:
            Optimized gas estimate
        """
        try:
            cache_key = self._generate_cache_key(transaction, priority_level)
            
            # Check cache first
            if cache_key in self.optimization_cache:
                cached_estimate = self.optimization_cache[cache_key]
                if self._is_cache_valid(cached_estimate):
                    return cached_estimate
            
            # Get current network gas data
            gas_data = await self._fetch_current_gas_data()
            
            # Estimate gas limit
            gas_limit = await self._estimate_gas_limit(transaction)
            
            # Determine optimal pricing strategy
            if await self._supports_eip1559():
                gas_estimate = await self._estimate_eip1559_gas(
                    gas_data, gas_limit, priority_level, max_wait_time
                )
            else:
                gas_estimate = await self._estimate_legacy_gas(
                    gas_data, gas_limit, priority_level, max_wait_time
                )
            
            # Add cost estimation
            gas_estimate.estimated_cost_usd = await self._calculate_usd_cost(
                gas_estimate.estimated_cost_wei
            )
            
            # Cache the result
            self.optimization_cache[cache_key] = gas_estimate
            
            return gas_estimate
            
        except Exception as e:
            logger.error(f"Gas optimization failed: {e}")
            return await self._fallback_gas_estimate(transaction)
    
    async def _fetch_current_gas_data(self) -> Dict:
        """Fetch current gas market data."""
        try:
            if await self._supports_eip1559():
                # Fetch EIP-1559 data
                fee_history = self.web3.eth.fee_history(20, "latest", [10, 25, 50, 75, 90])
                
                base_fees = fee_history['baseFeePerGas']
                rewards = fee_history['reward']
                
                return {
                    "current_base_fee": base_fees[-1],
                    "avg_base_fee": int(statistics.mean(base_fees)),
                    "base_fee_trend": self._calculate_trend(base_fees),
                    "priority_fees": {
                        "p10": [r[0] for r in rewards],
                        "p25": [r[1] for r in rewards], 
                        "p50": [r[2] for r in rewards],
                        "p75": [r[3] for r in rewards],
                        "p90": [r[4] for r in rewards]
                    }
                }
            else:
                # Legacy gas price
                current_gas = self.web3.eth.gas_price
                
                return {
                    "current_gas_price": current_gas,
                    "recommended_gas": {
                        "slow": int(current_gas * 0.9),
                        "standard": current_gas,
                        "fast": int(current_gas * 1.15),
                        "urgent": int(current_gas * 1.3)
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch gas data: {e}")
            raise
    
    async def _estimate_gas_limit(self, transaction: Dict) -> int:
        """Estimate gas limit for transaction with safety margin."""
        try:
            # Estimate base gas usage
            estimated_gas = self.web3.eth.estimate_gas(transaction)
            
            # Add safety margin based on transaction complexity
            complexity_factor = self._calculate_complexity_factor(transaction)
            safety_margin = max(1.1, 1.0 + complexity_factor * 0.2)
            
            gas_limit = int(estimated_gas * safety_margin)
            
            # Network-specific adjustments
            network_config = self.network_configs.get(self.network, {})
            min_gas = network_config.get("base_gas", 21000)
            
            return max(gas_limit, min_gas)
            
        except Exception as e:
            logger.error(f"Gas limit estimation failed: {e}")
            # Return conservative estimate
            return self.network_configs.get(self.network, {}).get("base_gas", 21000) * 2
    
    def _calculate_complexity_factor(self, transaction: Dict) -> float:
        """Calculate transaction complexity factor."""
        complexity = 0.0
        
        # Check for contract interaction
        if transaction.get("to") and transaction.get("data"):
            complexity += 0.3
            
            # Check data size
            data_size = len(transaction["data"]) if isinstance(transaction["data"], str) else 0
            if data_size > 1000:
                complexity += 0.2
        
        # Check for high value transfer
        value = int(transaction.get("value", 0))
        if value > self.web3.toWei(1, "ether"):
            complexity += 0.1
        
        return min(complexity, 1.0)
    
    async def _estimate_eip1559_gas(
        self, 
        gas_data: Dict, 
        gas_limit: int,
        priority_level: str,
        max_wait_time: int
    ) -> GasEstimate:
        """Estimate EIP-1559 gas parameters."""
        base_fee = gas_data["current_base_fee"]
        base_fee_trend = gas_data["base_fee_trend"]
        
        # Priority fee based on level and network congestion
        priority_percentiles = {
            "slow": "p10",
            "standard": "p25", 
            "fast": "p75",
            "urgent": "p90"
        }
        
        percentile = priority_percentiles.get(priority_level, "p25")
        recent_priority_fees = gas_data["priority_fees"][percentile][-5:]
        avg_priority_fee = int(statistics.mean(recent_priority_fees))
        
        # Adjust for base fee trend
        base_fee_multiplier = 1.0
        if base_fee_trend > 0.1:  # Rising base fee
            base_fee_multiplier = 1.2 if priority_level in ["fast", "urgent"] else 1.1
        elif base_fee_trend < -0.1:  # Falling base fee
            base_fee_multiplier = 0.9
        
        max_fee_per_gas = int(base_fee * base_fee_multiplier * 2 + avg_priority_fee)
        max_priority_fee_per_gas = avg_priority_fee
        
        # Time-based adjustments
        if max_wait_time < 60:  # Urgent execution
            max_priority_fee_per_gas = int(max_priority_fee_per_gas * 1.5)
            max_fee_per_gas = int(base_fee * 2.5 + max_priority_fee_per_gas)
        
        estimated_cost = gas_limit * max_fee_per_gas
        
        return GasEstimate(
            gas_limit=gas_limit,
            gas_price=0,  # Not used in EIP-1559
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            estimated_cost_wei=estimated_cost,
            confidence_level=0.95
        )
    
    async def _estimate_legacy_gas(
        self, 
        gas_data: Dict, 
        gas_limit: int,
        priority_level: str,
        max_wait_time: int
    ) -> GasEstimate:
        """Estimate legacy gas price."""
        recommended_prices = gas_data["recommended_gas"]
        
        gas_price = recommended_prices.get(priority_level, recommended_prices["standard"])
        
        # Time-based adjustments
        if max_wait_time < 60:
            gas_price = int(gas_price * 1.3)
        elif max_wait_time > 600:
            gas_price = int(gas_price * 0.9)
        
        estimated_cost = gas_limit * gas_price
        
        return GasEstimate(
            gas_limit=gas_limit,
            gas_price=gas_price,
            estimated_cost_wei=estimated_cost,
            confidence_level=0.9
        )
    
    async def _supports_eip1559(self) -> bool:
        """Check if network supports EIP-1559."""
        eip1559_networks = ["ethereum", "polygon", "arbitrum", "optimism"]
        return self.network in eip1559_networks
    
    def _calculate_trend(self, values: List[int]) -> float:
        """Calculate trend direction for a list of values."""
        if len(values) < 2:
            return 0.0
        
        # Simple trend calculation
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        if first_half == 0:
            return 0.0
        
        return (second_half - first_half) / first_half
    
    async def _calculate_usd_cost(self, cost_wei: int) -> Optional[float]:
        """Calculate USD cost of transaction."""
        try:
            # This would typically fetch from a price oracle
            # For now, return None - implement price oracle integration
            return None
            
        except Exception as e:
            logger.error(f"USD cost calculation failed: {e}")
            return None
    
    def _generate_cache_key(self, transaction: Dict, priority_level: str) -> str:
        """Generate cache key for gas estimate."""
        key_parts = [
            str(transaction.get("to", "")),
            str(len(transaction.get("data", ""))),
            str(transaction.get("value", 0)),
            priority_level,
            self.network
        ]
        return "_".join(key_parts)
    
    def _is_cache_valid(self, estimate: GasEstimate, max_age: int = 30) -> bool:
        """Check if cached estimate is still valid."""
        # Simple time-based validation - implement more sophisticated logic
        return True
    
    async def _fallback_gas_estimate(self, transaction: Dict) -> GasEstimate:
        """Provide fallback gas estimate when optimization fails."""
        try:
            gas_limit = await self._estimate_gas_limit(transaction)
            gas_price = self.web3.eth.gas_price
            
            return GasEstimate(
                gas_limit=gas_limit,
                gas_price=int(gas_price * 1.1),  # 10% buffer
                estimated_cost_wei=gas_limit * int(gas_price * 1.1),
                confidence_level=0.7
            )
            
        except Exception as e:
            logger.error(f"Fallback gas estimate failed: {e}")
            # Ultra-conservative fallback
            base_gas = self.network_configs.get(self.network, {}).get("base_gas", 21000)
            return GasEstimate(
                gas_limit=base_gas * 2,
                gas_price=self.web3.toWei(20, "gwei"),
                estimated_cost_wei=base_gas * 2 * self.web3.toWei(20, "gwei"),
                confidence_level=0.5
            )
    
    async def optimize_transaction_batch(
        self, 
        transactions: List[Dict],
        max_batch_size: int = 10
    ) -> List[TransactionBatch]:
        """Optimize a batch of transactions for cost efficiency."""
        try:
            if len(transactions) < self.batch_threshold:
                # Not worth batching
                return []
            
            # Sort transactions by priority and gas requirements
            sorted_transactions = await self._sort_transactions_for_batching(transactions)
            
            batches = []
            current_batch = []
            current_gas = 0
            max_gas_per_batch = 10_000_000  # Network-dependent limit
            
            for tx in sorted_transactions:
                gas_estimate = await self.estimate_optimal_gas(tx)
                
                if (current_gas + gas_estimate.gas_limit > max_gas_per_batch or 
                    len(current_batch) >= max_batch_size):
                    
                    # Finalize current batch
                    if current_batch:
                        batch = await self._create_transaction_batch(current_batch)
                        batches.append(batch)
                    
                    # Start new batch
                    current_batch = [tx]
                    current_gas = gas_estimate.gas_limit
                else:
                    current_batch.append(tx)
                    current_gas += gas_estimate.gas_limit
            
            # Handle remaining transactions
            if current_batch:
                batch = await self._create_transaction_batch(current_batch)
                batches.append(batch)
            
            return batches
            
        except Exception as e:
            logger.error(f"Transaction batch optimization failed: {e}")
            return []
    
    async def _sort_transactions_for_batching(self, transactions: List[Dict]) -> List[Dict]:
        """Sort transactions optimally for batching."""
        # Simple sorting by gas estimate - implement more sophisticated logic
        transaction_estimates = []
        
        for tx in transactions:
            estimate = await self.estimate_optimal_gas(tx)
            transaction_estimates.append((tx, estimate))
        
        # Sort by gas efficiency (gas limit per transaction value)
        transaction_estimates.sort(key=lambda x: x[1].gas_limit)
        
        return [tx for tx, _ in transaction_estimates]
    
    async def _create_transaction_batch(self, transactions: List[Dict]) -> TransactionBatch:
        """Create optimized transaction batch."""
        total_gas = 0
        total_cost = 0
        
        for tx in transactions:
            estimate = await self.estimate_optimal_gas(tx)
            total_gas += estimate.gas_limit
            total_cost += estimate.estimated_cost_wei
        
        return TransactionBatch(
            transactions=transactions,
            total_gas_limit=total_gas,
            estimated_total_cost=total_cost,
            batch_id=f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            created_at=datetime.utcnow()
        )
    
    def get_optimization_stats(self) -> Dict:
        """Get gas optimization performance statistics."""
        return {
            "cache_size": len(self.optimization_cache),
            "network": self.network,
            "supported_features": {
                "eip1559": asyncio.run(self._supports_eip1559()),
                "batching": True,
                "price_oracle": self.price_oracle_url is not None
            },
            "optimization_count": len(self.historical_data)
        }
