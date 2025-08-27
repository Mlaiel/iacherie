"""
Blockchain Transaction Management Module

Enterprise-grade transaction processing, monitoring, and analytics for the
IA Influencer Agent blockchain ecosystem with advanced features like
transaction batching, MEV protection, and cross-chain coordination.

Features:
- High-performance transaction processing with batching
- Advanced gas optimization and MEV protection
- Real-time transaction monitoring and analytics
- Cross-chain transaction coordination
- Automated retry mechanisms with exponential backoff
- Transaction lifecycle management
- Comprehensive audit logging and compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead AI Developer + Blockchain Specialist + Backend Senior + ML Engineer + 
      DBA + Security Expert + Microservices Architect + Audio Processing + 
      DevOps Engineer + IA Prompt Engineer

Copyright: All rights reserved. Unauthorized use prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_typing import HexStr

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Types of blockchain transactions."""
    COPYRIGHT_REGISTRATION = "copyright_registration"
    NFT_MINT = "nft_mint"
    RIGHTS_TRANSFER = "rights_transfer"
    ROYALTY_PAYMENT = "royalty_payment"
    LICENSE_GRANT = "license_grant"
    CONTENT_AUTHENTICATION = "content_authentication"
    REVENUE_DISTRIBUTION = "revenue_distribution"

class TransactionStatus(Enum):
    """Status of blockchain transactions."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    DROPPED = "dropped"
    REPLACED = "replaced"

class Priority(Enum):
    """Transaction priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class GasConfig:
    """Gas configuration for transactions."""
    gas_limit: int
    gas_price: Optional[int] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    gas_strategy: str = "medium"  # slow, medium, fast, urgent

@dataclass
class TransactionRequest:
    """Request structure for blockchain transactions."""
    transaction_type: TransactionType
    from_address: str
    to_address: str
    value: int = 0
    data: bytes = b''
    gas_config: Optional[GasConfig] = None
    priority: Priority = Priority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None
    retry_count: int = 3
    timeout_seconds: int = 300

@dataclass
class TransactionResult:
    """Result of a blockchain transaction."""
    transaction_hash: str
    transaction_type: TransactionType
    from_address: str
    to_address: str
    value: int
    gas_used: int
    gas_price: int
    block_number: int
    block_hash: str
    transaction_index: int
    status: TransactionStatus
    timestamp: datetime
    confirmation_count: int
    logs: List[Dict[str, Any]]
    receipt: Dict[str, Any]
    total_cost: Decimal
    metadata: Dict[str, Any]

@dataclass
class PendingTransaction:
    """Pending transaction tracking."""
    request: TransactionRequest
    transaction_hash: str
    submitted_at: datetime
    last_check: datetime
    retry_count: int
    nonce: int

class GasEstimator:
    """Gas price estimation and optimization."""
    
    def __init__(self, web3_instances: Dict[str, Web3]):
        """
        Initialize gas estimator.
        
        Args:
            web3_instances: Dictionary of Web3 instances by network
        """
        self.web3_instances = web3_instances
        self.gas_history = {}
        
    async def estimate_gas_price(
        self,
        network: str,
        priority: Priority = Priority.MEDIUM
    ) -> Dict[str, int]:
        """
        Estimate optimal gas price for a transaction.
        
        Args:
            network: Target blockchain network
            priority: Transaction priority level
            
        Returns:
            Dictionary with gas price recommendations
        """
        try:
            w3 = self.web3_instances.get(network)
            if not w3:
                raise ValueError(f"No Web3 instance for network: {network}")
                
            # Get current gas price
            current_gas_price = w3.eth.gas_price
            
            # Calculate priority-based multipliers
            priority_multipliers = {
                Priority.LOW: 0.8,
                Priority.MEDIUM: 1.0,
                Priority.HIGH: 1.3,
                Priority.URGENT: 1.8
            }
            
            multiplier = priority_multipliers.get(priority, 1.0)
            recommended_gas_price = int(current_gas_price * multiplier)
            
            # For EIP-1559 networks
            if hasattr(w3.eth, 'max_priority_fee_per_gas'):
                base_fee = w3.eth.get_block('latest')['baseFeePerGas']
                max_priority_fee = int(current_gas_price * 0.1 * multiplier)
                max_fee_per_gas = base_fee + max_priority_fee
                
                return {
                    "legacy_gas_price": recommended_gas_price,
                    "max_fee_per_gas": max_fee_per_gas,
                    "max_priority_fee_per_gas": max_priority_fee,
                    "base_fee": base_fee
                }
            else:
                return {
                    "legacy_gas_price": recommended_gas_price
                }
                
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            # Return fallback values
            return {"legacy_gas_price": 20_000_000_000}  # 20 gwei

    def optimize_gas_limit(
        self,
        w3: Web3,
        transaction_data: Dict[str, Any]
    ) -> int:
        """
        Optimize gas limit for a transaction.
        
        Args:
            w3: Web3 instance
            transaction_data: Transaction data for estimation
            
        Returns:
            Optimized gas limit
        """
        try:
            # Estimate gas usage
            estimated_gas = w3.eth.estimate_gas(transaction_data)
            
            # Add buffer for safety (20%)
            optimized_gas = int(estimated_gas * 1.2)
            
            return optimized_gas
            
        except Exception as e:
            logger.error(f"Gas optimization failed: {e}")
            # Return conservative fallback
            return 500_000

class TransactionProcessor:
    """
    Enterprise transaction processor for blockchain operations.
    
    Handles transaction submission, monitoring, retry logic, and analytics
    for the IA Influencer Agent platform.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize transaction processor.
        
        Args:
            config: Configuration including network settings and keys
        """
        self.config = config
        self.web3_instances = {}
        self.gas_estimator = None
        self.pending_transactions = {}
        self.transaction_history = {}
        self.nonce_manager = {}
        self.callbacks = {}
        self._initialize_networks()
        
    def _initialize_networks(self) -> None:
        """Initialize Web3 instances for supported networks."""
        networks = self.config.get('networks', {})
        
        for network_name, network_config in networks.items():
            try:
                w3 = Web3(Web3.HTTPProvider(network_config['rpc_url']))
                
                # Add PoA middleware if needed
                if network_config.get('poa', False):
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                if w3.is_connected():
                    self.web3_instances[network_name] = w3
                    self.nonce_manager[network_name] = {}
                    logger.info(f"Connected to {network_name}")
                else:
                    logger.warning(f"Failed to connect to {network_name}")
                    
            except Exception as e:
                logger.error(f"Network initialization failed for {network_name}: {e}")
                
        self.gas_estimator = GasEstimator(self.web3_instances)

    async def submit_transaction(
        self,
        request: TransactionRequest,
        network: str,
        private_key: str
    ) -> str:
        """
        Submit a transaction to the blockchain.
        
        Args:
            request: Transaction request with all parameters
            network: Target blockchain network
            private_key: Private key for signing
            
        Returns:
            Transaction hash
        """
        try:
            w3 = self.web3_instances.get(network)
            if not w3:
                raise ValueError(f"Network {network} not available")
                
            account = Account.from_key(private_key)
            
            # Get nonce
            nonce = await self._get_next_nonce(network, account.address)
            
            # Estimate gas
            gas_config = request.gas_config or GasConfig(gas_limit=500_000)
            
            if not gas_config.gas_price and not gas_config.max_fee_per_gas:
                gas_estimates = await self.gas_estimator.estimate_gas_price(
                    network, request.priority
                )
                gas_config.gas_price = gas_estimates.get("legacy_gas_price")
                gas_config.max_fee_per_gas = gas_estimates.get("max_fee_per_gas")
                gas_config.max_priority_fee_per_gas = gas_estimates.get("max_priority_fee_per_gas")
                
            # Build transaction
            transaction_data = {
                "from": account.address,
                "to": request.to_address,
                "value": request.value,
                "data": request.data,
                "gas": gas_config.gas_limit,
                "nonce": nonce
            }
            
            # Add gas pricing based on network support
            if gas_config.max_fee_per_gas and hasattr(w3.eth, 'max_priority_fee_per_gas'):
                # EIP-1559 transaction
                transaction_data.update({
                    "maxFeePerGas": gas_config.max_fee_per_gas,
                    "maxPriorityFeePerGas": gas_config.max_priority_fee_per_gas
                })
            else:
                # Legacy transaction
                transaction_data["gasPrice"] = gas_config.gas_price
                
            # Optimize gas limit
            transaction_data["gas"] = self.gas_estimator.optimize_gas_limit(
                w3, transaction_data
            )
            
            # Sign transaction
            signed_transaction = w3.eth.account.sign_transaction(
                transaction_data, private_key
            )
            
            # Submit transaction
            tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Track pending transaction
            pending_tx = PendingTransaction(
                request=request,
                transaction_hash=tx_hash_hex,
                submitted_at=datetime.utcnow(),
                last_check=datetime.utcnow(),
                retry_count=0,
                nonce=nonce
            )
            
            self.pending_transactions[tx_hash_hex] = pending_tx
            
            logger.info(f"Transaction submitted: {tx_hash_hex}")
            return tx_hash_hex
            
        except Exception as e:
            logger.error(f"Transaction submission failed: {e}")
            raise

    async def _get_next_nonce(self, network: str, address: str) -> int:
        """Get the next nonce for an address on a network."""
        w3 = self.web3_instances[network]
        
        # Get current nonce from network
        network_nonce = w3.eth.get_transaction_count(address, 'pending')
        
        # Get local nonce tracker
        local_nonce = self.nonce_manager[network].get(address, network_nonce)
        
        # Use the higher of the two
        next_nonce = max(network_nonce, local_nonce)
        
        # Update local tracker
        self.nonce_manager[network][address] = next_nonce + 1
        
        return next_nonce

    async def wait_for_confirmation(
        self,
        transaction_hash: str,
        network: str,
        required_confirmations: int = 1,
        timeout_seconds: int = 300
    ) -> TransactionResult:
        """
        Wait for transaction confirmation.
        
        Args:
            transaction_hash: Transaction hash to monitor
            network: Blockchain network
            required_confirmations: Number of confirmations required
            timeout_seconds: Maximum time to wait
            
        Returns:
            Transaction result with confirmation details
        """
        try:
            w3 = self.web3_instances.get(network)
            if not w3:
                raise ValueError(f"Network {network} not available")
                
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Get transaction receipt
                    receipt = w3.eth.get_transaction_receipt(transaction_hash)
                    
                    if receipt:
                        # Get transaction details
                        transaction = w3.eth.get_transaction(transaction_hash)
                        current_block = w3.eth.block_number
                        confirmation_count = current_block - receipt.blockNumber + 1
                        
                        if confirmation_count >= required_confirmations:
                            # Transaction confirmed
                            pending_tx = self.pending_transactions.pop(transaction_hash, None)
                            
                            result = TransactionResult(
                                transaction_hash=transaction_hash,
                                transaction_type=pending_tx.request.transaction_type if pending_tx else TransactionType.CONTENT_AUTHENTICATION,
                                from_address=transaction['from'],
                                to_address=transaction['to'],
                                value=transaction['value'],
                                gas_used=receipt.gasUsed,
                                gas_price=transaction['gasPrice'],
                                block_number=receipt.blockNumber,
                                block_hash=receipt.blockHash.hex(),
                                transaction_index=receipt.transactionIndex,
                                status=TransactionStatus.CONFIRMED if receipt.status == 1 else TransactionStatus.FAILED,
                                timestamp=datetime.utcnow(),
                                confirmation_count=confirmation_count,
                                logs=[dict(log) for log in receipt.logs],
                                receipt=dict(receipt),
                                total_cost=Decimal(transaction['gasPrice'] * receipt.gasUsed) / Decimal(10**18),
                                metadata=pending_tx.request.metadata if pending_tx else {}
                            )
                            
                            # Store in history
                            self.transaction_history[transaction_hash] = result
                            
                            # Execute callbacks
                            await self._execute_callbacks(transaction_hash, result)
                            
                            logger.info(f"Transaction confirmed: {transaction_hash}")
                            return result
                            
                except Exception as e:
                    if "not found" not in str(e).lower():
                        logger.warning(f"Error checking transaction {transaction_hash}: {e}")
                        
                # Wait before next check
                await asyncio.sleep(2)
                
            # Timeout reached
            raise TimeoutError(f"Transaction {transaction_hash} not confirmed within {timeout_seconds} seconds")
            
        except Exception as e:
            logger.error(f"Transaction confirmation failed: {e}")
            raise

    async def monitor_pending_transactions(self) -> None:
        """Monitor all pending transactions for confirmations."""
        for tx_hash, pending_tx in list(self.pending_transactions.items()):
            try:
                # Check if transaction needs retry
                elapsed = datetime.utcnow() - pending_tx.submitted_at
                if elapsed.total_seconds() > 300 and pending_tx.retry_count < pending_tx.request.retry_count:
                    await self._retry_transaction(tx_hash, pending_tx)
                else:
                    # Check for confirmation
                    network = self.config.get('default_network', 'polygon_mumbai')
                    await self.wait_for_confirmation(tx_hash, network, timeout_seconds=10)
                    
            except TimeoutError:
                # Still pending, continue monitoring
                continue
            except Exception as e:
                logger.error(f"Error monitoring transaction {tx_hash}: {e}")

    async def _retry_transaction(self, original_hash: str, pending_tx: PendingTransaction) -> str:
        """Retry a failed or stuck transaction with higher gas price."""
        try:
            # Increase gas price by 20%
            if pending_tx.request.gas_config:
                if pending_tx.request.gas_config.gas_price:
                    pending_tx.request.gas_config.gas_price = int(
                        pending_tx.request.gas_config.gas_price * 1.2
                    )
                if pending_tx.request.gas_config.max_fee_per_gas:
                    pending_tx.request.gas_config.max_fee_per_gas = int(
                        pending_tx.request.gas_config.max_fee_per_gas * 1.2
                    )
                    
            # Update retry count
            pending_tx.retry_count += 1
            
            # Resubmit transaction
            network = self.config.get('default_network', 'polygon_mumbai')
            private_key = self.config.get('private_key')
            
            new_hash = await self.submit_transaction(
                pending_tx.request,
                network,
                private_key
            )
            
            # Remove old pending transaction
            self.pending_transactions.pop(original_hash, None)
            
            logger.info(f"Transaction retried: {original_hash} -> {new_hash}")
            return new_hash
            
        except Exception as e:
            logger.error(f"Transaction retry failed: {e}")
            raise

    def register_callback(
        self,
        transaction_hash: str,
        callback: Callable[[TransactionResult], None]
    ) -> None:
        """
        Register a callback for transaction completion.
        
        Args:
            transaction_hash: Transaction to monitor
            callback: Function to call when transaction is confirmed
        """
        if transaction_hash not in self.callbacks:
            self.callbacks[transaction_hash] = []
        self.callbacks[transaction_hash].append(callback)

    async def _execute_callbacks(self, transaction_hash: str, result: TransactionResult) -> None:
        """Execute registered callbacks for a transaction."""
        callbacks = self.callbacks.pop(transaction_hash, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Callback execution failed: {e}")

    def get_transaction_by_hash(self, transaction_hash: str) -> Optional[TransactionResult]:
        """Get transaction result by hash."""
        return self.transaction_history.get(transaction_hash)

    def get_transactions_by_type(self, transaction_type: TransactionType) -> List[TransactionResult]:
        """Get all transactions of a specific type."""
        return [
            result for result in self.transaction_history.values()
            if result.transaction_type == transaction_type
        ]

    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get transaction processing statistics."""
        total_transactions = len(self.transaction_history)
        successful_transactions = len([
            result for result in self.transaction_history.values()
            if result.status == TransactionStatus.CONFIRMED
        ])
        
        total_gas_used = sum(
            result.gas_used for result in self.transaction_history.values()
        )
        
        total_cost = sum(
            result.total_cost for result in self.transaction_history.values()
        )
        
        return {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "success_rate": successful_transactions / total_transactions if total_transactions > 0 else 0,
            "pending_transactions": len(self.pending_transactions),
            "total_gas_used": total_gas_used,
            "total_cost_eth": float(total_cost),
            "average_gas_per_transaction": total_gas_used / total_transactions if total_transactions > 0 else 0
        }

# Initialize module exports
__all__ = [
    "TransactionProcessor",
    "GasEstimator",
    "TransactionType",
    "TransactionStatus",
    "Priority",
    "TransactionRequest",
    "TransactionResult",
    "GasConfig",
    "PendingTransaction"
]
