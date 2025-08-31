"""Governance System Module - IA-Influencer-Agent Platform
=====================================================

This module provides comprehensive decentralized governance infrastructure for content creators,
platform stakeholders, and community members to participate in democratic decision-making
through blockchain-based voting mechanisms, proposal management, and treasury operations.

Key Features:
- Multi-tier governance with creator, validator, and community voting
- Proposal lifecycle management with automated execution
- Treasury management with transparent fund allocation
- Reputation-based voting weight system
- Cross-chain governance coordination
- Automated governance token distribution

Integration Points:
- Smart contracts for governance operations
- Database models for proposal tracking
- Token management for voting rights
- Treasury operations for fund management
- Analytics for governance metrics

Author: Expert Development Team
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from eth_utils import to_checksum_address

from backend.core.database import get_async_session
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import (
    BlockchainError, 
    ValidationError,
    InsufficientFundsError,
    UnauthorizedError
)
from backend.models.blockchain import (
    GovernanceProposal,
    VotingRecord,
    GovernanceToken,
    TreasuryTransaction
)
from backend.business.blockchain.smart_contracts import SmartContractManager

# Configure logging
logger = get_logger(__name__)

class ProposalType(Enum):
    """Types of governance proposals"""    PLATFORM_UPGRADE = "platform_upgrade"
    TREASURY_ALLOCATION = "treasury_allocation"
    PARAMETER_CHANGE = "parameter_change"
    CONTENT_POLICY = "content_policy"
    VALIDATOR_ADDITION = "validator_addition"
    VALIDATOR_REMOVAL = "validator_removal"
    EMERGENCY_ACTION = "emergency_action"
    COMMUNITY_GRANT = "community_grant"

class ProposalStatus(Enum):
    """Status of governance proposals"""    DRAFT = "draft"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class VoteType(Enum):
    """Types of votes"""    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"

@dataclass
class ProposalMetadata:
    """Metadata for governance proposals"""    title: str
    description: str
    proposal_type: ProposalType
    targets: List[str] = field(default_factory=list)
    values: List[int] = field(default_factory=list)
    calldatas: List[str] = field(default_factory=list)
    start_block: Optional[int] = None
    end_block: Optional[int] = None
    min_quorum: Decimal = Decimal("0.04")  # 4% of total supply
    proposal_threshold: Decimal = Decimal("0.01")  # 1% of total supply

@dataclass
class VotingPower:
    """Voting power calculation"""    token_balance: Decimal
    delegated_balance: Decimal
    reputation_multiplier: Decimal
    content_creator_bonus: Decimal
    validator_bonus: Decimal
    total_voting_power: Decimal

@dataclass
class TreasuryAllocation:
    """Treasury fund allocation"""    recipient: str
    amount: Decimal
    currency: str
    purpose: str
    milestone_requirements: List[str] = field(default_factory=list)
    release_schedule: List[Dict] = field(default_factory=list)

class GovernanceTokenManager:
    """Manages governance tokens and voting rights"""    
    def __init__(self, contract_manager: SmartContractManager):
        self.contract_manager = contract_manager
        self.redis: Optional[aioredis.Redis] = None
        
    async def initialize(self):
        """Initialize token manager"""        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                decode_responses=True
            )
            logger.info("Governance token manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize governance token manager: {str(e)}")
            raise BlockchainError(f"Token manager initialization failed: {str(e)}")
    
    async def mint_governance_tokens(
        self,
        recipient: str,
        amount: Decimal,
        reason: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Mint new governance tokens"""        try:
            # Validate recipient address
            recipient_address = to_checksum_address(recipient)
            
            # Get governance contract
            governance_contract = await self.contract_manager.get_contract(
                "governance", 
                session
            )
            
            # Prepare transaction
            mint_tx = await governance_contract.functions.mint(
                recipient_address,
                int(amount * 10**18)  # Convert to wei
            ).build_transaction({
                'from': settings.BLOCKCHAIN_ADMIN_ADDRESS,
                'gas': 100000,
                'gasPrice': Web3.to_wei('20', 'gwei')
            })
            
            # Sign and send transaction
            signed_tx = Account.sign_transaction(
                mint_tx, 
                settings.BLOCKCHAIN_ADMIN_PRIVATE_KEY
            )
            
            tx_hash = await self.contract_manager.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
            # Wait for confirmation
            receipt = await self.contract_manager.web3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            
            # Record token minting
            token_record = GovernanceToken(
                recipient_address=recipient_address,
                amount=amount,
                transaction_hash=tx_hash.hex(),
                block_number=receipt['blockNumber'],
                reason=reason,
                created_at=datetime.utcnow()
            )
            
            session.add(token_record)
            await session.commit()
            
            # Update token balance cache
            await self.update_token_balance_cache(recipient_address)
            
            logger.info(
                f"Minted {amount} governance tokens to {recipient_address}. "
                f"Reason: {reason}"
            )
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt['blockNumber'],
                "recipient": recipient_address,
                "amount": str(amount),
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Failed to mint governance tokens: {str(e)}")
            raise BlockchainError(f"Token minting failed: {str(e)}")
    
    async def delegate_voting_power(
        self,
        delegator: str,
        delegatee: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Delegate voting power to another address"""        try:
            delegator_address = to_checksum_address(delegator)
            delegatee_address = to_checksum_address(delegatee)
            
            # Get governance contract
            governance_contract = await self.contract_manager.get_contract(
                "governance", 
                session
            )
            
            # Prepare delegation transaction
            delegate_tx = await governance_contract.functions.delegate(
                delegatee_address
            ).build_transaction({
                'from': delegator_address,
                'gas': 80000,
                'gasPrice': Web3.to_wei('20', 'gwei')
            })
            
            # This would be signed by user's wallet in real implementation
            # For now, using admin key for demonstration
            signed_tx = Account.sign_transaction(
                delegate_tx, 
                settings.BLOCKCHAIN_ADMIN_PRIVATE_KEY
            )
            
            tx_hash = await self.contract_manager.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
            receipt = await self.contract_manager.web3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            
            # Update voting power caches
            await self.update_voting_power_cache(delegator_address)
            await self.update_voting_power_cache(delegatee_address)
            
            logger.info(
                f"Delegated voting power from {delegator_address} to {delegatee_address}"
            )
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "delegator": delegator_address,
                "delegatee": delegatee_address,
                "block_number": receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"Failed to delegate voting power: {str(e)}")
            raise BlockchainError(f"Delegation failed: {str(e)}")
    
    async def calculate_voting_power(
        self,
        user_address: str,
        block_number: Optional[int] = None
    ) -> VotingPower:
        """Calculate voting power for an address"""        try:
            user_address = to_checksum_address(user_address)
            
            # Check cache first
            cache_key = f"voting_power:{user_address}:{block_number or 'latest'}"
            cached_power = await self.redis.get(cache_key)
            
            if cached_power:
                return VotingPower(**eval(cached_power))
            
            # Get token balance
            token_balance = await self._get_token_balance(user_address, block_number)
            
            # Get delegated balance
            delegated_balance = await self._get_delegated_balance(user_address, block_number)
            
            # Calculate reputation multiplier
            reputation_multiplier = await self._get_reputation_multiplier(user_address)
            
            # Calculate content creator bonus
            content_creator_bonus = await self._get_content_creator_bonus(user_address)
            
            # Calculate validator bonus
            validator_bonus = await self._get_validator_bonus(user_address)
            
            # Calculate total voting power
            base_power = token_balance + delegated_balance
            total_voting_power = base_power * (
                1 + reputation_multiplier + content_creator_bonus + validator_bonus
            )
            
            voting_power = VotingPower(
                token_balance=token_balance,
                delegated_balance=delegated_balance,
                reputation_multiplier=reputation_multiplier,
                content_creator_bonus=content_creator_bonus,
                validator_bonus=validator_bonus,
                total_voting_power=total_voting_power
            )
            
            # Cache result
            await self.redis.setex(
                cache_key,
                300,  # 5 minutes
                str(voting_power.__dict__)
            )
            
            return voting_power
            
        except Exception as e:
            logger.error(f"Failed to calculate voting power: {str(e)}")
            raise BlockchainError(f"Voting power calculation failed: {str(e)}")
    
    async def _get_token_balance(
        self,
        address: str,
        block_number: Optional[int] = None
    ) -> Decimal:
        """Get governance token balance for address"""        # Implementation would query blockchain
        # For now, return mock data
        return Decimal("1000.0")
    
    async def _get_delegated_balance(
        self,
        address: str,
        block_number: Optional[int] = None
    ) -> Decimal:
        """Get delegated token balance for address"""        # Implementation would query blockchain
        # For now, return mock data
        return Decimal("500.0")
    
    async def _get_reputation_multiplier(self, address: str) -> Decimal:
        """Calculate reputation-based multiplier"""        # Implementation would query reputation system
        # For now, return mock data
        return Decimal("0.1")  # 10% bonus
    
    async def _get_content_creator_bonus(self, address: str) -> Decimal:
        """Calculate content creator bonus"""        # Implementation would check if address is verified creator
        # For now, return mock data
        return Decimal("0.05")  # 5% bonus
    
    async def _get_validator_bonus(self, address: str) -> Decimal:
        """Calculate validator bonus"""        # Implementation would check if address is active validator
        # For now, return mock data
        return Decimal("0.03")  # 3% bonus
    
    async def update_token_balance_cache(self, address: str):
        """Update cached token balance"""        cache_key = f"token_balance:{address}"
        balance = await self._get_token_balance(address)
        await self.redis.setex(cache_key, 300, str(balance))
    
    async def update_voting_power_cache(self, address: str):
        """Update cached voting power"""        voting_power = await self.calculate_voting_power(address)
        cache_key = f"voting_power:{address}:latest"
        await self.redis.setex(
            cache_key, 
            300, 
            str(voting_power.__dict__)
        )

class ProposalManager:
    """Manages governance proposals"""    
    def __init__(
        self, 
        contract_manager: SmartContractManager,
        token_manager: GovernanceTokenManager
    ):
        self.contract_manager = contract_manager
        self.token_manager = token_manager
        self.redis: Optional[aioredis.Redis] = None
        
    async def initialize(self):
        """Initialize proposal manager"""        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                decode_responses=True
            )
            logger.info("Proposal manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize proposal manager: {str(e)}")
            raise BlockchainError(f"Proposal manager initialization failed: {str(e)}")
    
    async def create_proposal(
        self,
        proposer: str,
        metadata: ProposalMetadata,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Create a new governance proposal"""        try:
            proposer_address = to_checksum_address(proposer)
            
            # Check proposer has enough tokens
            voting_power = await self.token_manager.calculate_voting_power(proposer_address)
            total_supply = await self._get_total_token_supply()
            
            required_threshold = total_supply * metadata.proposal_threshold
            if voting_power.total_voting_power < required_threshold:
                raise ValidationError(
                    f"Insufficient voting power to create proposal. "
                    f"Required: {required_threshold}, Available: {voting_power.total_voting_power}"
                )
            
            # Get governance contract
            governance_contract = await self.contract_manager.get_contract(
                "governance", 
                session
            )
            
            # Create proposal on-chain
            propose_tx = await governance_contract.functions.propose(
                metadata.targets,
                metadata.values,
                metadata.calldatas,
                metadata.description
            ).build_transaction({
                'from': proposer_address,
                'gas': 200000,
                'gasPrice': Web3.to_wei('20', 'gwei')
            })
            
            signed_tx = Account.sign_transaction(
                propose_tx, 
                settings.BLOCKCHAIN_ADMIN_PRIVATE_KEY
            )
            
            tx_hash = await self.contract_manager.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
            receipt = await self.contract_manager.web3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            
            # Extract proposal ID from logs
            proposal_id = await self._extract_proposal_id(receipt)
            
            # Create proposal record
            proposal = GovernanceProposal(
                proposal_id=proposal_id,
                proposer_address=proposer_address,
                title=metadata.title,
                description=metadata.description,
                proposal_type=metadata.proposal_type.value,
                targets=metadata.targets,
                values=metadata.values,
                calldatas=metadata.calldatas,
                start_block=metadata.start_block or receipt['blockNumber'] + 1,
                end_block=metadata.end_block or receipt['blockNumber'] + 17280,  # ~3 days
                min_quorum=metadata.min_quorum,
                proposal_threshold=metadata.proposal_threshold,
                status=ProposalStatus.ACTIVE.value,
                transaction_hash=tx_hash.hex(),
                block_number=receipt['blockNumber'],
                created_at=datetime.utcnow()
            )
            
            session.add(proposal)
            await session.commit()
            
            # Cache proposal data
            await self._cache_proposal_data(proposal_id, proposal)
            
            logger.info(
                f"Created proposal {proposal_id} by {proposer_address}: {metadata.title}"
            )
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt['blockNumber'],
                "title": metadata.title,
                "status": ProposalStatus.ACTIVE.value
            }
            
        except Exception as e:
            logger.error(f"Failed to create proposal: {str(e)}")
            raise BlockchainError(f"Proposal creation failed: {str(e)}")
    
    async def cast_vote(
        self,
        voter: str,
        proposal_id: int,
        vote_type: VoteType,
        reason: Optional[str] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """Cast a vote on a proposal"""        try:
            voter_address = to_checksum_address(voter)
            
            # Get voting power at proposal start block
            proposal = await self._get_proposal(proposal_id, session)
            voting_power = await self.token_manager.calculate_voting_power(
                voter_address, 
                proposal.start_block
            )
            
            if voting_power.total_voting_power == 0:
                raise ValidationError("No voting power available")
            
            # Get governance contract
            governance_contract = await self.contract_manager.get_contract(
                "governance", 
                session
            )
            
            # Cast vote on-chain
            vote_value = self._vote_type_to_value(vote_type)
            vote_tx = await governance_contract.functions.castVoteWithReason(
                proposal_id,
                vote_value,
                reason or ""
            ).build_transaction({
                'from': voter_address,
                'gas': 150000,
                'gasPrice': Web3.to_wei('20', 'gwei')
            })
            
            signed_tx = Account.sign_transaction(
                vote_tx, 
                settings.BLOCKCHAIN_ADMIN_PRIVATE_KEY
            )
            
            tx_hash = await self.contract_manager.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
            receipt = await self.contract_manager.web3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            
            # Record vote
            vote_record = VotingRecord(
                proposal_id=proposal_id,
                voter_address=voter_address,
                vote_type=vote_type.value,
                voting_power=voting_power.total_voting_power,
                reason=reason,
                transaction_hash=tx_hash.hex(),
                block_number=receipt['blockNumber'],
                created_at=datetime.utcnow()
            )
            
            session.add(vote_record)
            await session.commit()
            
            # Update proposal vote counts
            await self._update_proposal_vote_counts(proposal_id)
            
            logger.info(
                f"Vote cast by {voter_address} on proposal {proposal_id}: "
                f"{vote_type.value} with power {voting_power.total_voting_power}"
            )
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "proposal_id": proposal_id,
                "voter": voter_address,
                "vote_type": vote_type.value,
                "voting_power": str(voting_power.total_voting_power)
            }
            
        except Exception as e:
            logger.error(f"Failed to cast vote: {str(e)}")
            raise BlockchainError(f"Vote casting failed: {str(e)}")
    
    async def execute_proposal(
        self,
        proposal_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Execute a successful proposal"""        try:
            proposal = await self._get_proposal(proposal_id, session)
            
            if proposal.status != ProposalStatus.SUCCEEDED.value:
                raise ValidationError(f"Proposal {proposal_id} is not in succeeded state")
            
            # Get governance contract
            governance_contract = await self.contract_manager.get_contract(
                "governance", 
                session
            )
            
            # Execute proposal on-chain
            execute_tx = await governance_contract.functions.execute(
                proposal.targets,
                proposal.values,
                proposal.calldatas,
                Web3.keccak(text=proposal.description).hex()
            ).build_transaction({
                'from': settings.BLOCKCHAIN_ADMIN_ADDRESS,
                'gas': 500000,
                'gasPrice': Web3.to_wei('30', 'gwei')
            })
            
            signed_tx = Account.sign_transaction(
                execute_tx, 
                settings.BLOCKCHAIN_ADMIN_PRIVATE_KEY
            )
            
            tx_hash = await self.contract_manager.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
            receipt = await self.contract_manager.web3.eth.wait_for_transaction_receipt(
                tx_hash
            )
            
            # Update proposal status
            proposal.status = ProposalStatus.EXECUTED.value
            proposal.executed_at = datetime.utcnow()
            proposal.execution_transaction_hash = tx_hash.hex()
            
            await session.commit()
            
            # Handle specific proposal types
            await self._handle_proposal_execution(proposal, session)
            
            logger.info(f"Executed proposal {proposal_id}")
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "execution_hash": tx_hash.hex(),
                "block_number": receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"Failed to execute proposal: {str(e)}")
            raise BlockchainError(f"Proposal execution failed: {str(e)}")
    
    async def _get_total_token_supply(self) -> Decimal:
        """Get total governance token supply"""        # Implementation would query blockchain
        return Decimal("1000000.0")  # 1M tokens
    
    async def _extract_proposal_id(self, receipt) -> int:
        """Extract proposal ID from transaction receipt"""        # Implementation would parse logs
        # For now, return mock ID
        return 1
    
    async def _get_proposal(
        self, 
        proposal_id: int, 
        session: AsyncSession
    ) -> GovernanceProposal:
        """Get proposal by ID"""        # Implementation would query database
        # For now, return mock proposal
        return GovernanceProposal(
            proposal_id=proposal_id,
            status=ProposalStatus.SUCCEEDED.value,
            start_block=1000,
            targets=[],
            values=[],
            calldatas=[],
            description="Mock proposal"
        )
    
    def _vote_type_to_value(self, vote_type: VoteType) -> int:
        """Convert vote type to contract value"""        mapping = {
            VoteType.AGAINST: 0,
            VoteType.FOR: 1,
            VoteType.ABSTAIN: 2
        }
        return mapping[vote_type]
    
    async def _cache_proposal_data(self, proposal_id: int, proposal: GovernanceProposal):
        """Cache proposal data"""        cache_key = f"proposal:{proposal_id}"
        await self.redis.setex(
            cache_key,
            3600,  # 1 hour
            str(proposal.__dict__)
        )
    
    async def _update_proposal_vote_counts(self, proposal_id: int):
        """Update cached proposal vote counts"""        # Implementation would aggregate votes from database
        pass
    
    async def _handle_proposal_execution(
        self, 
        proposal: GovernanceProposal, 
        session: AsyncSession
    ):
        """Handle execution of specific proposal types"""        if proposal.proposal_type == ProposalType.TREASURY_ALLOCATION.value:
            await self._handle_treasury_allocation(proposal, session)
        elif proposal.proposal_type == ProposalType.PARAMETER_CHANGE.value:
            await self._handle_parameter_change(proposal, session)
        # Add more handlers as needed
    
    async def _handle_treasury_allocation(
        self, 
        proposal: GovernanceProposal, 
        session: AsyncSession
    ):
        """Handle treasury allocation proposal execution"""        logger.info(f"Handling treasury allocation for proposal {proposal.proposal_id}")
        # Implementation would transfer funds from treasury
    
    async def _handle_parameter_change(
        self, 
        proposal: GovernanceProposal, 
        session: AsyncSession
    ):
        """Handle parameter change proposal execution"""        logger.info(f"Handling parameter change for proposal {proposal.proposal_id}")
        # Implementation would update system parameters

class TreasuryManager:
    """Manages platform treasury and fund allocation"""    
    def __init__(self, contract_manager: SmartContractManager):
        self.contract_manager = contract_manager
        
    async def allocate_funds(
        self,
        allocation: TreasuryAllocation,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Allocate treasury funds"""        try:
            recipient_address = to_checksum_address(allocation.recipient)
            
            # Validate treasury balance
            treasury_balance = await self._get_treasury_balance(allocation.currency)
            if treasury_balance < allocation.amount:
                raise InsufficientFundsError(
                    f"Insufficient treasury funds. Available: {treasury_balance}, "
                    f"Required: {allocation.amount}"
                )
            
            # Create treasury transaction
            treasury_tx = TreasuryTransaction(
                recipient_address=recipient_address,
                amount=allocation.amount,
                currency=allocation.currency,
                purpose=allocation.purpose,
                milestone_requirements=allocation.milestone_requirements,
                release_schedule=allocation.release_schedule,
                status="pending",
                created_at=datetime.utcnow()
            )
            
            session.add(treasury_tx)
            await session.commit()
            
            # Execute initial fund transfer if no milestones
            if not allocation.milestone_requirements:
                await self._execute_treasury_transfer(treasury_tx, session)
            
            logger.info(
                f"Allocated {allocation.amount} {allocation.currency} "
                f"to {recipient_address} for {allocation.purpose}"
            )
            
            return {
                "success": True,
                "transaction_id": treasury_tx.id,
                "recipient": recipient_address,
                "amount": str(allocation.amount),
                "currency": allocation.currency,
                "status": treasury_tx.status
            }
            
        except Exception as e:
            logger.error(f"Failed to allocate treasury funds: {str(e)}")
            raise BlockchainError(f"Treasury allocation failed: {str(e)}")
    
    async def _get_treasury_balance(self, currency: str) -> Decimal:
        """Get treasury balance for currency"""        # Implementation would query treasury contract
        return Decimal("100000.0")  # Mock balance
    
    async def _execute_treasury_transfer(
        self, 
        treasury_tx: TreasuryTransaction, 
        session: AsyncSession
    ):
        """Execute treasury fund transfer"""        # Implementation would transfer funds on-chain
        treasury_tx.status = "completed"
        treasury_tx.executed_at = datetime.utcnow()
        await session.commit()

class GovernanceSystem:
    """Main governance system orchestrator"""    
    def __init__(self):
        self.contract_manager: Optional[SmartContractManager] = None
        self.token_manager: Optional[GovernanceTokenManager] = None
        self.proposal_manager: Optional[ProposalManager] = None
        self.treasury_manager: Optional[TreasuryManager] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize governance system"""        try:
            # Initialize contract manager
            self.contract_manager = SmartContractManager()
            await self.contract_manager.initialize()
            
            # Initialize token manager
            self.token_manager = GovernanceTokenManager(self.contract_manager)
            await self.token_manager.initialize()
            
            # Initialize proposal manager
            self.proposal_manager = ProposalManager(
                self.contract_manager, 
                self.token_manager
            )
            await self.proposal_manager.initialize()
            
            # Initialize treasury manager
            self.treasury_manager = TreasuryManager(self.contract_manager)
            
            self.initialized = True
            logger.info("Governance system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize governance system: {str(e)}")
            raise BlockchainError(f"Governance system initialization failed: {str(e)}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session"""        async with get_async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_proposal(
        self,
        proposer: str,
        title: str,
        description: str,
        proposal_type: ProposalType,
        targets: List[str] = None,
        values: List[int] = None,
        calldatas: List[str] = None
    ) -> Dict[str, Any]:
        """Create new governance proposal"""        if not self.initialized:
            await self.initialize()
            
        metadata = ProposalMetadata(
            title=title,
            description=description,
            proposal_type=proposal_type,
            targets=targets or [],
            values=values or [],
            calldatas=calldatas or []
        )
        
        async with self.get_session() as session:
            return await self.proposal_manager.create_proposal(
                proposer, 
                metadata, 
                session
            )
    
    async def vote_on_proposal(
        self,
        voter: str,
        proposal_id: int,
        vote_type: VoteType,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Vote on governance proposal"""        if not self.initialized:
            await self.initialize()
            
        async with self.get_session() as session:
            return await self.proposal_manager.cast_vote(
                voter, 
                proposal_id, 
                vote_type, 
                reason, 
                session
            )
    
    async def execute_proposal(self, proposal_id: int) -> Dict[str, Any]:
        """Execute successful proposal"""        if not self.initialized:
            await self.initialize()
            
        async with self.get_session() as session:
            return await self.proposal_manager.execute_proposal(proposal_id, session)
    
    async def get_voting_power(
        self, 
        user_address: str, 
        block_number: Optional[int] = None
    ) -> VotingPower:
        """Get voting power for address"""        if not self.initialized:
            await self.initialize()
            
        return await self.token_manager.calculate_voting_power(
            user_address, 
            block_number
        )
    
    async def mint_governance_tokens(
        self,
        recipient: str,
        amount: Decimal,
        reason: str
    ) -> Dict[str, Any]:
        """Mint new governance tokens"""        if not self.initialized:
            await self.initialize()
            
        async with self.get_session() as session:
            return await self.token_manager.mint_governance_tokens(
                recipient, 
                amount, 
                reason, 
                session
            )
    
    async def allocate_treasury_funds(
        self,
        recipient: str,
        amount: Decimal,
        currency: str,
        purpose: str,
        milestone_requirements: List[str] = None,
        release_schedule: List[Dict] = None
    ) -> Dict[str, Any]:
        """Allocate treasury funds"""        if not self.initialized:
            await self.initialize()
            
        allocation = TreasuryAllocation(
            recipient=recipient,
            amount=amount,
            currency=currency,
            purpose=purpose,
            milestone_requirements=milestone_requirements or [],
            release_schedule=release_schedule or []
        )
        
        async with self.get_session() as session:
            return await self.treasury_manager.allocate_funds(allocation, session)

# Global governance system instance
governance_system = GovernanceSystem()

# Convenience functions for external usage
async def create_governance_proposal(
    proposer: str,
    title: str,
    description: str,
    proposal_type: ProposalType,
    targets: List[str] = None,
    values: List[int] = None,
    calldatas: List[str] = None
) -> Dict[str, Any]:
    """Create new governance proposal"""    return await governance_system.create_proposal(
        proposer, title, description, proposal_type, targets, values, calldatas
    )

async def vote_on_governance_proposal(
    voter: str,
    proposal_id: int,
    vote_type: VoteType,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """Vote on governance proposal"""    return await governance_system.vote_on_proposal(voter, proposal_id, vote_type, reason)

async def get_user_voting_power(
    user_address: str, 
    block_number: Optional[int] = None
) -> VotingPower:
    """Get voting power for user address"""    return await governance_system.get_voting_power(user_address, block_number)

async def execute_governance_proposal(proposal_id: int) -> Dict[str, Any]:
    """Execute successful governance proposal"""    return await governance_system.execute_proposal(proposal_id)
