"""Professional transaction management and execution for blockchain operations.

This module handles transaction creation, signing, submission, and monitoring
for the IA Influencer Agent platform's blockchain functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited.
"""from typing import Dict, List, Optional, Union, Callable, Any
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from web3 import Web3
from web3.types import TxParams, TxReceipt, HexBytes
from eth_account import Account
import json

logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    """Transaction execution status."""    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REPLACED = "replaced"


@dataclass
class TransactionRequest:
    """Transaction request data structure."""    
    to: str
    value: int = 0
    data: str = "0x"
    gas_limit: Optional[int] = None
    gas_price: Optional[int] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    nonce: Optional[int] = None
    priority_level: str = "standard"
    max_wait_time: int = 300
    

@dataclass 
class TransactionResult:
    """Transaction execution result."""    
    transaction_hash: str
    status: TransactionStatus
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    effective_gas_price: Optional[int] = None
    confirmation_time: Optional[datetime] = None
    receipt: Optional[Dict] = None
    error_message: Optional[str] = None
    

class TransactionManager:
    """Professional transaction management and execution system."""    
    def __init__(self, web3: Web3, account: Account, gas_optimizer=None):
        """Initialize transaction manager.
        
        Args:
            web3: Web3 instance for blockchain interaction
            account: Account for transaction signing
            gas_optimizer: Gas optimization service
        """        self.web3 = web3
        self.account = account
        self.gas_optimizer = gas_optimizer
        self.pending_transactions: Dict[str, Dict] = {}
        self.transaction_history: List[TransactionResult] = []
        self.nonce_manager = NonceManager(web3, account.address)
        self.retry_attempts = 3
        self.confirmation_blocks = 1
        
    async def send_transaction(
        self, 
        tx_request: TransactionRequest,
        callback: Optional[Callable] = None
    ) -> TransactionResult:
        """Send a transaction with optimal gas parameters.
        
        Args:
            tx_request: Transaction parameters
            callback: Optional callback for transaction updates
            
        Returns:
            Transaction execution result
        """        try:
            # Build transaction parameters
            tx_params = await self._build_transaction_params(tx_request)
            
            # Sign transaction
            signed_tx = self.account.sign_transaction(tx_params)
            
            # Submit transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"Transaction submitted: {tx_hash_hex}")
            
            # Track pending transaction
            self.pending_transactions[tx_hash_hex] = {
                "request": tx_request,
                "submitted_at": datetime.utcnow(),
                "tx_params": tx_params,
                "callback": callback
            }
            
            # Start monitoring
            asyncio.create_task(self._monitor_transaction(tx_hash_hex))
            
            return TransactionResult(
                transaction_hash=tx_hash_hex,
                status=TransactionStatus.PENDING
            )
            
        except Exception as e:
            logger.error(f"Transaction submission failed: {e}")
            return TransactionResult(
                transaction_hash="",
                status=TransactionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _build_transaction_params(self, tx_request: TransactionRequest) -> Dict:
        """Build complete transaction parameters."""        try:
            # Base parameters
            tx_params = {
                "to": tx_request.to,
                "value": tx_request.value,
                "data": tx_request.data,
                "from": self.account.address
            }
            
            # Get or assign nonce
            if tx_request.nonce is not None:
                tx_params["nonce"] = tx_request.nonce
            else:
                tx_params["nonce"] = await self.nonce_manager.get_next_nonce()
            
            # Gas optimization
            if self.gas_optimizer:
                gas_estimate = await self.gas_optimizer.estimate_optimal_gas(
                    tx_params, 
                    tx_request.priority_level,
                    tx_request.max_wait_time
                )
                
                tx_params["gas"] = gas_estimate.gas_limit
                
                if gas_estimate.max_fee_per_gas:
                    # EIP-1559 transaction
                    tx_params["maxFeePerGas"] = gas_estimate.max_fee_per_gas
                    tx_params["maxPriorityFeePerGas"] = gas_estimate.max_priority_fee_per_gas
                    tx_params["type"] = "0x2"
                else:
                    # Legacy transaction
                    tx_params["gasPrice"] = gas_estimate.gas_price
            else:
                # Fallback gas settings
                tx_params["gas"] = tx_request.gas_limit or 21000
                if tx_request.gas_price:
                    tx_params["gasPrice"] = tx_request.gas_price
                elif tx_request.max_fee_per_gas:
                    tx_params["maxFeePerGas"] = tx_request.max_fee_per_gas
                    tx_params["maxPriorityFeePerGas"] = tx_request.max_priority_fee_per_gas
                    tx_params["type"] = "0x2"
                else:
                    tx_params["gasPrice"] = self.web3.eth.gas_price
            
            return tx_params
            
        except Exception as e:
            logger.error(f"Failed to build transaction parameters: {e}")
            raise
    
    async def _monitor_transaction(self, tx_hash: str) -> None:
        """Monitor transaction until confirmation or timeout."""        try:
            tx_info = self.pending_transactions.get(tx_hash)
            if not tx_info:
                return
            
            tx_request = tx_info["request"]
            callback = tx_info["callback"]
            start_time = tx_info["submitted_at"]
            
            # Wait for confirmation
            while True:
                try:
                    # Check if transaction is mined
                    receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                    
                    if receipt:
                        # Transaction mined
                        status = (TransactionStatus.CONFIRMED 
                                if receipt.status == 1 
                                else TransactionStatus.FAILED)
                        
                        result = TransactionResult(
                            transaction_hash=tx_hash,
                            status=status,
                            block_number=receipt.blockNumber,
                            gas_used=receipt.gasUsed,
                            effective_gas_price=receipt.effectiveGasPrice,
                            confirmation_time=datetime.utcnow(),
                            receipt=dict(receipt)
                        )
                        
                        # Update tracking
                        self._finalize_transaction(tx_hash, result)
                        
                        # Execute callback
                        if callback:
                            try:
                                await callback(result)
                            except Exception as e:
                                logger.error(f"Transaction callback failed: {e}")
                        
                        return
                        
                except Exception:
                    # Transaction not yet mined
                    pass
                
                # Check timeout
                elapsed = datetime.utcnow() - start_time
                if elapsed.total_seconds() > tx_request.max_wait_time:
                    # Transaction timeout - attempt replacement
                    replacement_result = await self._handle_transaction_timeout(tx_hash)
                    if replacement_result:
                        return
                    
                    # Mark as failed
                    result = TransactionResult(
                        transaction_hash=tx_hash,
                        status=TransactionStatus.FAILED,
                        error_message="Transaction timeout"
                    )
                    
                    self._finalize_transaction(tx_hash, result)
                    
                    if callback:
                        await callback(result)
                    
                    return
                
                # Wait before next check
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Transaction monitoring failed: {e}")
            
            result = TransactionResult(
                transaction_hash=tx_hash,
                status=TransactionStatus.FAILED,
                error_message=str(e)
            )
            
            self._finalize_transaction(tx_hash, result)
    
    async def _handle_transaction_timeout(self, tx_hash: str) -> Optional[TransactionResult]:
        """Handle transaction timeout by attempting replacement."""        try:
            tx_info = self.pending_transactions.get(tx_hash)
            if not tx_info:
                return None
            
            # Create replacement transaction with higher gas
            original_request = tx_info["request"]
            original_params = tx_info["tx_params"]
            
            # Increase gas price for replacement
            replacement_params = original_params.copy()
            
            if "maxFeePerGas" in original_params:
                # EIP-1559 replacement
                replacement_params["maxFeePerGas"] = int(original_params["maxFeePerGas"] * 1.2)
                replacement_params["maxPriorityFeePerGas"] = int(
                    original_params["maxPriorityFeePerGas"] * 1.2
                )
            else:
                # Legacy replacement
                replacement_params["gasPrice"] = int(original_params["gasPrice"] * 1.2)
            
            # Sign and submit replacement
            signed_tx = self.account.sign_transaction(replacement_params)
            replacement_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            replacement_hash_hex = replacement_hash.hex()
            
            logger.info(f"Replacement transaction submitted: {replacement_hash_hex}")
            
            # Update tracking
            self.pending_transactions[replacement_hash_hex] = {
                "request": original_request,
                "submitted_at": datetime.utcnow(),
                "tx_params": replacement_params,
                "callback": tx_info["callback"],
                "replaces": tx_hash
            }
            
            # Mark original as replaced
            result = TransactionResult(
                transaction_hash=tx_hash,
                status=TransactionStatus.REPLACED
            )
            self._finalize_transaction(tx_hash, result)
            
            # Start monitoring replacement
            asyncio.create_task(self._monitor_transaction(replacement_hash_hex))
            
            return result
            
        except Exception as e:
            logger.error(f"Transaction replacement failed: {e}")
            return None
    
    def _finalize_transaction(self, tx_hash: str, result: TransactionResult) -> None:
        """Finalize transaction tracking."""        try:
            # Remove from pending
            if tx_hash in self.pending_transactions:
                del self.pending_transactions[tx_hash]
            
            # Add to history
            self.transaction_history.append(result)
            
            # Limit history size
            if len(self.transaction_history) > 1000:
                self.transaction_history = self.transaction_history[-800:]
            
            logger.info(f"Transaction finalized: {tx_hash} - {result.status.value}")
            
        except Exception as e:
            logger.error(f"Failed to finalize transaction: {e}")
    
    async def cancel_transaction(self, tx_hash: str) -> Optional[TransactionResult]:
        """Attempt to cancel a pending transaction."""        try:
            tx_info = self.pending_transactions.get(tx_hash)
            if not tx_info:
                return None
            
            # Create cancellation transaction (0 ETH to self with same nonce)
            original_params = tx_info["tx_params"]
            
            cancel_params = {
                "to": self.account.address,
                "value": 0,
                "gas": 21000,
                "nonce": original_params["nonce"],
                "from": self.account.address
            }
            
            # Use higher gas price for cancellation priority
            if "maxFeePerGas" in original_params:
                cancel_params["maxFeePerGas"] = int(original_params["maxFeePerGas"] * 1.5)
                cancel_params["maxPriorityFeePerGas"] = int(
                    original_params["maxPriorityFeePerGas"] * 1.5
                )
                cancel_params["type"] = "0x2"
            else:
                cancel_params["gasPrice"] = int(original_params["gasPrice"] * 1.5)
            
            # Submit cancellation
            signed_cancel = self.account.sign_transaction(cancel_params)
            cancel_hash = self.web3.eth.send_raw_transaction(signed_cancel.rawTransaction)
            
            logger.info(f"Cancellation transaction submitted: {cancel_hash.hex()}")
            
            return TransactionResult(
                transaction_hash=cancel_hash.hex(),
                status=TransactionStatus.PENDING
            )
            
        except Exception as e:
            logger.error(f"Transaction cancellation failed: {e}")
            return None
    
    async def send_batch_transactions(
        self, 
        transactions: List[TransactionRequest]
    ) -> List[TransactionResult]:
        """Send multiple transactions in batch."""        try:
            results = []
            
            # Use batch-optimized nonces
            base_nonce = await self.nonce_manager.get_next_nonce()
            
            for i, tx_request in enumerate(transactions):
                # Assign sequential nonces for batch
                tx_request.nonce = base_nonce + i
                
                result = await self.send_transaction(tx_request)
                results.append(result)
                
                # Small delay to prevent RPC overload
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch transaction sending failed: {e}")
            return []
    
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict]:
        """Get current status of a transaction."""        # Check pending transactions
        if tx_hash in self.pending_transactions:
            return {
                "status": "pending",
                "submitted_at": self.pending_transactions[tx_hash]["submitted_at"].isoformat()
            }
        
        # Check history
        for result in self.transaction_history:
            if result.transaction_hash == tx_hash:
                return {
                    "status": result.status.value,
                    "block_number": result.block_number,
                    "gas_used": result.gas_used,
                    "confirmation_time": (
                        result.confirmation_time.isoformat() 
                        if result.confirmation_time else None
                    ),
                    "error_message": result.error_message
                }
        
        return None
    
    def get_pending_transactions(self) -> List[Dict]:
        """Get all pending transactions."""        return [
            {
                "hash": tx_hash,
                "submitted_at": info["submitted_at"].isoformat(),
                "to": info["request"].to,
                "value": info["request"].value
            }
            for tx_hash, info in self.pending_transactions.items()
        ]
    
    def get_transaction_history(self, limit: int = 100) -> List[Dict]:
        """Get transaction history."""        recent_history = self.transaction_history[-limit:]
        
        return [
            {
                "hash": result.transaction_hash,
                "status": result.status.value,
                "block_number": result.block_number,
                "gas_used": result.gas_used,
                "confirmation_time": (
                    result.confirmation_time.isoformat() 
                    if result.confirmation_time else None
                ),
                "error_message": result.error_message
            }
            for result in recent_history
        ]


class NonceManager:
    """Professional nonce management for transaction ordering."""    
    def __init__(self, web3: Web3, address: str):
        """Initialize nonce manager.
        
        Args:
            web3: Web3 instance
            address: Wallet address
        """        self.web3 = web3
        self.address = address
        self.local_nonce: Optional[int] = None
        self.nonce_lock = asyncio.Lock()
    
    async def get_next_nonce(self) -> int:
        """Get next available nonce."""        async with self.nonce_lock:
            try:
                # Get current network nonce
                network_nonce = self.web3.eth.get_transaction_count(self.address, "pending")
                
                # Initialize or sync local nonce
                if self.local_nonce is None:
                    self.local_nonce = network_nonce
                else:
                    # Use higher of network or local nonce
                    self.local_nonce = max(self.local_nonce, network_nonce)
                
                current_nonce = self.local_nonce
                self.local_nonce += 1
                
                return current_nonce
                
            except Exception as e:
                logger.error(f"Nonce management failed: {e}")
                # Fallback to network nonce
                return self.web3.eth.get_transaction_count(self.address, "pending")
    
    def reset_nonce(self) -> None:
        """Reset local nonce tracking."""        self.local_nonce = None
    
    async def sync_nonce(self) -> int:
        """Synchronize with network nonce."""        async with self.nonce_lock:
            network_nonce = self.web3.eth.get_transaction_count(self.address, "pending")
            self.local_nonce = network_nonce
            return network_nonce
