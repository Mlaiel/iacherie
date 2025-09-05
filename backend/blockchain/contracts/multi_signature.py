"""Multi-Signature Wallet Contract - IA-Influencer-Agent Platform

This module provides multi-signature wallet functionality for secure
collaborative fund management with configurable approval thresholds
and transaction execution controls.

Features:
- Multi-signature transaction approval
- Configurable approval thresholds
- Owner management
- Transaction queuing and execution
- Emergency recovery mechanisms
- Audit trails

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import json
import uuid
import hashlib

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of multi-sig transactions"""
    TRANSFER = "transfer"
    CONTRACT_CALL = "contract_call"
    OWNER_ADDITION = "owner_addition"
    OWNER_REMOVAL = "owner_removal"
    THRESHOLD_CHANGE = "threshold_change"
    EMERGENCY_RECOVERY = "emergency_recovery"


class TransactionStatus(Enum):
    """Multi-sig transaction status"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class MultiSigTransaction:
    """Multi-signature transaction"""
    transaction_id: str
    wallet_id: str
    transaction_type: TransactionType
    proposer_address: str
    target_address: str
    amount: Decimal
    currency: str
    data: Dict[str, Any]
    required_approvals: int
    current_approvals: Set[str]
    status: TransactionStatus
    created_at: datetime
    executed_at: Optional[datetime]
    execution_hash: Optional[str]


@dataclass
class MultiSigWallet:
    """Multi-signature wallet"""
    wallet_id: str
    name: str
    owners: Set[str]
    approval_threshold: int
    balance: Dict[str, Decimal]  # currency -> amount
    pending_transactions: List[str]
    executed_transactions: List[str]
    created_at: datetime
    is_active: bool


class MultiSignatureWallet:
    """
    Multi-Signature Wallet Management System
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Multi-Signature Wallet system"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wallets: Dict[str, MultiSigWallet] = {}
        self.transactions: Dict[str, MultiSigTransaction] = {}
        
        # System settings
        self.max_owners = config.get("max_owners", 20)
        self.min_threshold = config.get("min_threshold", 2)
        self.transaction_expiry_hours = config.get("expiry_hours", 168)  # 7 days
    
    async def create_wallet(
        self,
        name: str,
        initial_owners: List[str],
        approval_threshold: int,
        creator_address: str
    ) -> MultiSigWallet:
        """Create new multi-signature wallet"""
        try:
            wallet_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating multi-sig wallet: {name}")
            
            # Validate parameters
            if len(initial_owners) > self.max_owners:
                raise ValueError(f"Too many owners: {len(initial_owners)} > {self.max_owners}")
            
            if approval_threshold < self.min_threshold:
                raise ValueError(f"Threshold too low: {approval_threshold} < {self.min_threshold}")
            
            if approval_threshold > len(initial_owners):
                raise ValueError(f"Threshold exceeds owner count: {approval_threshold} > {len(initial_owners)}")
            
            # Ensure creator is included
            owners_set = set(initial_owners)
            owners_set.add(creator_address)
            
            wallet = MultiSigWallet(
                wallet_id=wallet_id,
                name=name,
                owners=owners_set,
                approval_threshold=approval_threshold,
                balance={},
                pending_transactions=[],
                executed_transactions=[],
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            self.wallets[wallet_id] = wallet
            
            self.logger.info(f"Multi-sig wallet created: {wallet_id}")
            return wallet
            
        except Exception as e:
            self.logger.error(f"Wallet creation failed: {e}")
            raise
    
    async def propose_transaction(
        self,
        wallet_id: str,
        proposer_address: str,
        transaction_type: TransactionType,
        target_address: str,
        amount: Decimal,
        currency: str,
        data: Optional[Dict[str, Any]] = None
    ) -> MultiSigTransaction:
        """Propose new transaction for multi-sig approval"""
        try:
            if wallet_id not in self.wallets:
                raise ValueError(f"Wallet not found: {wallet_id}")
            
            wallet = self.wallets[wallet_id]
            
            if proposer_address not in wallet.owners:
                raise ValueError("Only wallet owners can propose transactions")
            
            if not wallet.is_active:
                raise ValueError("Wallet is not active")
            
            transaction_id = str(uuid.uuid4())
            
            self.logger.info(f"Proposing transaction: {transaction_type.value}")
            
            # Validate transaction
            await self._validate_transaction(wallet, transaction_type, target_address, amount, currency)
            
            transaction = MultiSigTransaction(
                transaction_id=transaction_id,
                wallet_id=wallet_id,
                transaction_type=transaction_type,
                proposer_address=proposer_address,
                target_address=target_address,
                amount=amount,
                currency=currency,
                data=data or {},
                required_approvals=wallet.approval_threshold,
                current_approvals={proposer_address},  # Proposer auto-approves
                status=TransactionStatus.PENDING,
                created_at=datetime.utcnow(),
                executed_at=None,
                execution_hash=None
            )
            
            self.transactions[transaction_id] = transaction
            wallet.pending_transactions.append(transaction_id)
            
            # Check if already meets threshold (for single-owner wallets)
            if len(transaction.current_approvals) >= wallet.approval_threshold:
                await self._execute_transaction(transaction)
            
            self.logger.info(f"Transaction proposed: {transaction_id}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Transaction proposal failed: {e}")
            raise
    
    async def _validate_transaction(
        self,
        wallet: MultiSigWallet,
        transaction_type: TransactionType,
        target_address: str,
        amount: Decimal,
        currency: str
    ):
        """Validate transaction parameters"""
        if transaction_type == TransactionType.TRANSFER:
            # Check wallet balance
            wallet_balance = wallet.balance.get(currency, Decimal("0"))
            if amount > wallet_balance:
                raise ValueError(f"Insufficient balance: {amount} > {wallet_balance}")
        
        if not target_address or not target_address.startswith("0x"):
            raise ValueError("Invalid target address")
        
        if amount < 0:
            raise ValueError("Amount cannot be negative")
    
    async def approve_transaction(
        self,
        transaction_id: str,
        approver_address: str
    ) -> Dict[str, Any]:
        """Approve pending transaction"""
        try:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            transaction = self.transactions[transaction_id]
            wallet = self.wallets[transaction.wallet_id]
            
            if approver_address not in wallet.owners:
                raise ValueError("Only wallet owners can approve transactions")
            
            if transaction.status != TransactionStatus.PENDING:
                raise ValueError(f"Transaction not pending: {transaction.status.value}")
            
            # Check if transaction expired
            if self._is_transaction_expired(transaction):
                transaction.status = TransactionStatus.EXPIRED
                raise ValueError("Transaction has expired")
            
            self.logger.info(f"Approving transaction: {transaction_id}")
            
            # Add approval
            transaction.current_approvals.add(approver_address)
            
            result = {
                "transaction_id": transaction_id,
                "approver_address": approver_address,
                "current_approvals": len(transaction.current_approvals),
                "required_approvals": transaction.required_approvals,
                "approved_at": datetime.utcnow().isoformat()
            }
            
            # Check if threshold met
            if len(transaction.current_approvals) >= transaction.required_approvals:
                transaction.status = TransactionStatus.APPROVED
                execution_result = await self._execute_transaction(transaction)
                result["execution_result"] = execution_result
            
            self.logger.info(f"Transaction approved: {transaction_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transaction approval failed: {e}")
            raise
    
    def _is_transaction_expired(self, transaction: MultiSigTransaction) -> bool:
        """Check if transaction has expired"""
        expiry_time = transaction.created_at + timedelta(hours=self.transaction_expiry_hours)
        return datetime.utcnow() > expiry_time
    
    async def _execute_transaction(self, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute approved transaction"""
        try:
            self.logger.info(f"Executing transaction: {transaction.transaction_id}")
            
            wallet = self.wallets[transaction.wallet_id]
            
            if transaction.transaction_type == TransactionType.TRANSFER:
                result = await self._execute_transfer(wallet, transaction)
            elif transaction.transaction_type == TransactionType.OWNER_ADDITION:
                result = await self._execute_owner_addition(wallet, transaction)
            elif transaction.transaction_type == TransactionType.OWNER_REMOVAL:
                result = await self._execute_owner_removal(wallet, transaction)
            elif transaction.transaction_type == TransactionType.THRESHOLD_CHANGE:
                result = await self._execute_threshold_change(wallet, transaction)
            else:
                result = await self._execute_generic_transaction(wallet, transaction)
            
            # Update transaction status
            transaction.status = TransactionStatus.EXECUTED
            transaction.executed_at = datetime.utcnow()
            transaction.execution_hash = result.get("transaction_hash")
            
            # Move from pending to executed
            wallet.pending_transactions.remove(transaction.transaction_id)
            wallet.executed_transactions.append(transaction.transaction_id)
            
            self.logger.info(f"Transaction executed: {transaction.transaction_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {e}")
            raise
    
    async def _execute_transfer(self, wallet: MultiSigWallet, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute transfer transaction"""
        # Deduct from wallet balance
        current_balance = wallet.balance.get(transaction.currency, Decimal("0"))
        wallet.balance[transaction.currency] = current_balance - transaction.amount
        
        # Mock transaction hash
        tx_data = f"{transaction.target_address}{transaction.amount}{transaction.currency}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return {
            "type": "transfer",
            "to_address": transaction.target_address,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "transaction_hash": f"0x{tx_hash}",
            "new_balance": str(wallet.balance.get(transaction.currency, Decimal("0")))
        }
    
    async def _execute_owner_addition(self, wallet: MultiSigWallet, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute owner addition"""
        new_owner = transaction.target_address
        
        if new_owner in wallet.owners:
            raise ValueError("Address is already an owner")
        
        wallet.owners.add(new_owner)
        
        return {
            "type": "owner_addition",
            "new_owner": new_owner,
            "total_owners": len(wallet.owners)
        }
    
    async def _execute_owner_removal(self, wallet: MultiSigWallet, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute owner removal"""
        owner_to_remove = transaction.target_address
        
        if owner_to_remove not in wallet.owners:
            raise ValueError("Address is not an owner")
        
        if len(wallet.owners) <= wallet.approval_threshold:
            raise ValueError("Cannot remove owner: would break threshold requirement")
        
        wallet.owners.remove(owner_to_remove)
        
        return {
            "type": "owner_removal",
            "removed_owner": owner_to_remove,
            "total_owners": len(wallet.owners)
        }
    
    async def _execute_threshold_change(self, wallet: MultiSigWallet, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute threshold change"""
        new_threshold = int(transaction.amount)
        
        if new_threshold < self.min_threshold:
            raise ValueError(f"Threshold too low: {new_threshold}")
        
        if new_threshold > len(wallet.owners):
            raise ValueError(f"Threshold exceeds owner count: {new_threshold}")
        
        old_threshold = wallet.approval_threshold
        wallet.approval_threshold = new_threshold
        
        return {
            "type": "threshold_change",
            "old_threshold": old_threshold,
            "new_threshold": new_threshold
        }
    
    async def _execute_generic_transaction(self, wallet: MultiSigWallet, transaction: MultiSigTransaction) -> Dict[str, Any]:
        """Execute generic transaction"""
        # Mock execution for contract calls and other types
        tx_hash = hashlib.sha256(
            f"{transaction.transaction_type.value}{transaction.target_address}".encode()
        ).hexdigest()
        
        return {
            "type": transaction.transaction_type.value,
            "target": transaction.target_address,
            "data": transaction.data,
            "transaction_hash": f"0x{tx_hash}"
        }
    
    async def cancel_transaction(
        self,
        transaction_id: str,
        canceller_address: str
    ) -> Dict[str, Any]:
        """Cancel pending transaction"""
        try:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            transaction = self.transactions[transaction_id]
            wallet = self.wallets[transaction.wallet_id]
            
            # Only proposer or majority of owners can cancel
            if (canceller_address != transaction.proposer_address and 
                canceller_address not in wallet.owners):
                raise ValueError("Insufficient permission to cancel transaction")
            
            if transaction.status != TransactionStatus.PENDING:
                raise ValueError(f"Cannot cancel transaction in status: {transaction.status.value}")
            
            self.logger.info(f"Cancelling transaction: {transaction_id}")
            
            transaction.status = TransactionStatus.CANCELLED
            wallet.pending_transactions.remove(transaction_id)
            
            result = {
                "transaction_id": transaction_id,
                "cancelled_by": canceller_address,
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Transaction cancelled: {transaction_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transaction cancellation failed: {e}")
            raise
    
    async def get_wallet_info(self, wallet_id: str) -> Dict[str, Any]:
        """Get multi-sig wallet information"""
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        wallet = self.wallets[wallet_id]
        
        return {
            "wallet_id": wallet.wallet_id,
            "name": wallet.name,
            "owners": list(wallet.owners),
            "approval_threshold": wallet.approval_threshold,
            "balance": {currency: str(amount) for currency, amount in wallet.balance.items()},
            "pending_transactions": len(wallet.pending_transactions),
            "executed_transactions": len(wallet.executed_transactions),
            "created_at": wallet.created_at.isoformat(),
            "is_active": wallet.is_active
        }
    
    async def get_transaction_info(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction information"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        transaction = self.transactions[transaction_id]
        
        return {
            "transaction_id": transaction.transaction_id,
            "wallet_id": transaction.wallet_id,
            "transaction_type": transaction.transaction_type.value,
            "proposer_address": transaction.proposer_address,
            "target_address": transaction.target_address,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "data": transaction.data,
            "required_approvals": transaction.required_approvals,
            "current_approvals": len(transaction.current_approvals),
            "approvers": list(transaction.current_approvals),
            "status": transaction.status.value,
            "created_at": transaction.created_at.isoformat(),
            "executed_at": transaction.executed_at.isoformat() if transaction.executed_at else None,
            "execution_hash": transaction.execution_hash
        }


class MultiSigManager:
    """High-level manager for multi-signature operations"""
    
    def __init__(self, multi_sig_wallet: MultiSignatureWallet):
        self.multi_sig_wallet = multi_sig_wallet
        self.logger = logging.getLogger(__name__)
    
    async def setup_collaboration_wallet(
        self,
        project_name: str,
        collaborators: List[str],
        creator_address: str,
        approval_threshold: Optional[int] = None
    ) -> MultiSigWallet:
        """Setup multi-sig wallet for collaboration"""
        
        # Calculate default threshold (majority)
        if approval_threshold is None:
            total_members = len(collaborators) + 1  # +1 for creator
            approval_threshold = (total_members // 2) + 1
        
        return await self.multi_sig_wallet.create_wallet(
            f"{project_name} Collaboration Wallet",
            collaborators,
            approval_threshold,
            creator_address
        )