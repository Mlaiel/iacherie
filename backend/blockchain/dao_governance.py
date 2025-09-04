"""DAO Governance Module - IA-Influencer-Agent Platform

This module provides comprehensive Decentralized Autonomous Organization (DAO) governance
functionality for the backend layer, enabling democratic decision-making, proposal management,
and community governance for the platform.

Features:
- DAO proposal creation and management
- Multi-tier voting mechanisms
- Token-based governance with delegation
- Treasury management and fund allocation
- Reputation-based voting weights
- Automated proposal execution
- Cross-chain governance coordination
- Governance analytics and participation tracking

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid
import hashlib

from web3 import Web3
from web3.contract import Contract
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ProposalType(Enum):
    """Types of governance proposals"""
    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARAMETER_CHANGE = "parameter_change"
    TREASURY_ALLOCATION = "treasury_allocation"
    FEATURE_REQUEST = "feature_request"
    PARTNERSHIP = "partnership"
    MODERATION_POLICY = "moderation_policy"
    TOKEN_ECONOMICS = "token_economics"
    PLATFORM_INTEGRATION = "platform_integration"


class VotingMechanism(Enum):
    """Voting mechanisms available"""
    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    QUADRATIC_VOTING = "quadratic_voting"
    WEIGHTED_VOTING = "weighted_voting"
    RANKED_CHOICE = "ranked_choice"
    CONVICTION_VOTING = "conviction_voting"


class ProposalStatus(Enum):
    """Proposal lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    DEFEATED = "defeated"
    EXPIRED = "expired"


class VoteChoice(Enum):
    """Voting choices"""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


class GovernanceRole(Enum):
    """Governance participant roles"""
    CREATOR = "creator"
    VALIDATOR = "validator"
    COMMUNITY = "community"
    MODERATOR = "moderator"
    TREASURY_MANAGER = "treasury_manager"
    ADMIN = "admin"


@dataclass
class GovernanceToken:
    """Governance token information"""
    token_address: str
    token_symbol: str
    total_supply: Decimal
    circulating_supply: Decimal
    voting_weight: Decimal
    delegation_enabled: bool
    min_proposal_threshold: Decimal
    min_voting_threshold: Decimal


@dataclass
class Proposal:
    """Governance proposal structure"""
    proposal_id: str
    title: str
    description: str
    proposer_address: str
    proposal_type: ProposalType
    voting_mechanism: VotingMechanism
    vote_start_time: datetime
    vote_end_time: datetime
    execution_delay: timedelta
    status: ProposalStatus
    votes_for: Decimal
    votes_against: Decimal
    votes_abstain: Decimal
    total_votes: Decimal
    quorum_threshold: Decimal
    approval_threshold: Decimal
    metadata: Dict[str, Any]
    execution_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class Vote:
    """Individual vote record"""
    vote_id: str
    proposal_id: str
    voter_address: str
    choice: VoteChoice
    voting_power: Decimal
    conviction: Optional[Decimal]
    delegation_path: List[str]
    timestamp: datetime
    transaction_hash: str
    metadata: Dict[str, Any]


@dataclass
class Delegation:
    """Vote delegation record"""
    delegation_id: str
    delegator_address: str
    delegate_address: str
    voting_power: Decimal
    proposal_types: List[ProposalType]
    expiry_date: Optional[datetime]
    created_at: datetime
    is_active: bool


@dataclass
class TreasuryProposal:
    """Treasury allocation proposal"""
    proposal_id: str
    allocation_amount: Decimal
    recipient_address: str
    purpose: str
    milestone_requirements: List[Dict[str, Any]]
    vesting_schedule: Optional[Dict[str, Any]]
    reporting_requirements: List[str]


class DAOGovernance:
    """
    DAO Governance system for decentralized decision-making
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DAO Governance
        
        Args:
            config: Governance configuration including token contracts, voting parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = {}
        self.delegations: Dict[str, Delegation] = {}
        self.governance_tokens: Dict[str, GovernanceToken] = {}
        
        # Initialize governance tokens
        self._initialize_governance_tokens()
        
        # Voting parameters
        self.voting_config = config.get("voting", {})
        self.quorum_thresholds = config.get("quorum_thresholds", {})
        self.approval_thresholds = config.get("approval_thresholds", {})
        
    def _initialize_governance_tokens(self) -> None:
        """Initialize governance tokens from configuration"""
        tokens_config = self.config.get("governance_tokens", [])
        
        for token_config in tokens_config:
            token = GovernanceToken(
                token_address=token_config["address"],
                token_symbol=token_config["symbol"],
                total_supply=Decimal(token_config["total_supply"]),
                circulating_supply=Decimal(token_config["circulating_supply"]),
                voting_weight=Decimal(token_config.get("voting_weight", "1.0")),
                delegation_enabled=token_config.get("delegation_enabled", True),
                min_proposal_threshold=Decimal(token_config.get("min_proposal_threshold", "1000")),
                min_voting_threshold=Decimal(token_config.get("min_voting_threshold", "1"))
            )
            
            self.governance_tokens[token.token_symbol] = token
    
    async def create_proposal(
        self,
        title: str,
        description: str,
        proposer_address: str,
        proposal_type: ProposalType,
        voting_mechanism: VotingMechanism = VotingMechanism.SIMPLE_MAJORITY,
        voting_duration_hours: int = 168,  # 1 week default
        execution_delay_hours: int = 48,
        execution_params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Proposal:
        """
        Create a new governance proposal
        
        Args:
            title: Proposal title
            description: Detailed proposal description
            proposer_address: Address of the proposer
            proposal_type: Type of proposal
            voting_mechanism: Voting mechanism to use
            voting_duration_hours: Duration of voting period
            execution_delay_hours: Delay before execution after approval
            execution_params: Parameters for proposal execution
            metadata: Additional proposal metadata
            
        Returns:
            Created proposal
        """
        try:
            proposal_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating governance proposal: {title}")
            
            # Validate proposer eligibility
            await self._validate_proposer_eligibility(proposer_address)
            
            # Calculate thresholds based on proposal type
            quorum_threshold = self._get_quorum_threshold(proposal_type)
            approval_threshold = self._get_approval_threshold(proposal_type, voting_mechanism)
            
            # Set voting timeline
            vote_start_time = datetime.utcnow() + timedelta(hours=24)  # 24h delay
            vote_end_time = vote_start_time + timedelta(hours=voting_duration_hours)
            execution_delay = timedelta(hours=execution_delay_hours)
            
            proposal = Proposal(
                proposal_id=proposal_id,
                title=title,
                description=description,
                proposer_address=proposer_address,
                proposal_type=proposal_type,
                voting_mechanism=voting_mechanism,
                vote_start_time=vote_start_time,
                vote_end_time=vote_end_time,
                execution_delay=execution_delay,
                status=ProposalStatus.ACTIVE,
                votes_for=Decimal("0"),
                votes_against=Decimal("0"),
                votes_abstain=Decimal("0"),
                total_votes=Decimal("0"),
                quorum_threshold=quorum_threshold,
                approval_threshold=approval_threshold,
                metadata=metadata or {},
                execution_params=execution_params or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store proposal
            self.proposals[proposal_id] = proposal
            self.votes[proposal_id] = []
            
            self.logger.info(f"Governance proposal created: {proposal_id}")
            return proposal
            
        except Exception as e:
            self.logger.error(f"Proposal creation failed: {e}")
            raise
    
    async def _validate_proposer_eligibility(self, proposer_address: str) -> None:
        """Validate that an address is eligible to create proposals"""
        # Check minimum token holding requirement
        total_voting_power = await self._get_voting_power(proposer_address)
        
        min_threshold = Decimal("0")
        for token in self.governance_tokens.values():
            min_threshold = max(min_threshold, token.min_proposal_threshold)
        
        if total_voting_power < min_threshold:
            raise ValueError(f"Insufficient voting power for proposal creation: {total_voting_power} < {min_threshold}")
    
    def _get_quorum_threshold(self, proposal_type: ProposalType) -> Decimal:
        """Get quorum threshold based on proposal type"""
        thresholds = {
            ProposalType.PROTOCOL_UPGRADE: Decimal("20.0"),  # 20% of total supply
            ProposalType.PARAMETER_CHANGE: Decimal("10.0"),
            ProposalType.TREASURY_ALLOCATION: Decimal("15.0"),
            ProposalType.FEATURE_REQUEST: Decimal("5.0"),
            ProposalType.PARTNERSHIP: Decimal("8.0"),
            ProposalType.MODERATION_POLICY: Decimal("12.0"),
            ProposalType.TOKEN_ECONOMICS: Decimal("25.0"),
            ProposalType.PLATFORM_INTEGRATION: Decimal("7.0")
        }
        return thresholds.get(proposal_type, Decimal("10.0"))
    
    def _get_approval_threshold(
        self,
        proposal_type: ProposalType,
        voting_mechanism: VotingMechanism
    ) -> Decimal:
        """Get approval threshold based on proposal type and voting mechanism"""
        base_thresholds = {
            ProposalType.PROTOCOL_UPGRADE: Decimal("75.0"),  # 75% approval
            ProposalType.PARAMETER_CHANGE: Decimal("60.0"),
            ProposalType.TREASURY_ALLOCATION: Decimal("65.0"),
            ProposalType.FEATURE_REQUEST: Decimal("50.0"),
            ProposalType.PARTNERSHIP: Decimal("55.0"),
            ProposalType.MODERATION_POLICY: Decimal("60.0"),
            ProposalType.TOKEN_ECONOMICS: Decimal("80.0"),
            ProposalType.PLATFORM_INTEGRATION: Decimal("55.0")
        }
        
        base_threshold = base_thresholds.get(proposal_type, Decimal("50.0"))
        
        # Adjust based on voting mechanism
        if voting_mechanism == VotingMechanism.SUPERMAJORITY:
            return max(base_threshold, Decimal("66.7"))
        elif voting_mechanism == VotingMechanism.QUADRATIC_VOTING:
            return base_threshold * Decimal("0.9")  # Lower threshold for quadratic voting
        
        return base_threshold
    
    async def submit_vote(
        self,
        proposal_id: str,
        voter_address: str,
        choice: VoteChoice,
        conviction: Optional[Decimal] = None,
        voting_power_override: Optional[Decimal] = None
    ) -> Vote:
        """
        Submit a vote on a proposal
        
        Args:
            proposal_id: Proposal to vote on
            voter_address: Address of the voter
            choice: Vote choice (for/against/abstain)
            conviction: Conviction level for conviction voting
            voting_power_override: Override voting power (for testing)
            
        Returns:
            Vote record
        """
        try:
            if proposal_id not in self.proposals:
                raise ValueError(f"Proposal not found: {proposal_id}")
            
            proposal = self.proposals[proposal_id]
            
            # Validate voting period
            now = datetime.utcnow()
            if now < proposal.vote_start_time:
                raise ValueError("Voting has not started yet")
            if now > proposal.vote_end_time:
                raise ValueError("Voting period has ended")
            
            # Check if already voted
            existing_votes = [v for v in self.votes[proposal_id] if v.voter_address == voter_address]
            if existing_votes:
                raise ValueError("Address has already voted on this proposal")
            
            # Calculate voting power
            if voting_power_override:
                voting_power = voting_power_override
            else:
                voting_power = await self._get_voting_power(voter_address)
                
            # Get delegation path
            delegation_path = await self._get_delegation_path(voter_address)
            
            # Apply conviction multiplier if applicable
            if proposal.voting_mechanism == VotingMechanism.CONVICTION_VOTING and conviction:
                voting_power = voting_power * conviction
            
            # Create vote record
            vote_id = str(uuid.uuid4())
            vote = Vote(
                vote_id=vote_id,
                proposal_id=proposal_id,
                voter_address=voter_address,
                choice=choice,
                voting_power=voting_power,
                conviction=conviction,
                delegation_path=delegation_path,
                timestamp=datetime.utcnow(),
                transaction_hash=f"0x{hashlib.sha256(vote_id.encode()).hexdigest()}",
                metadata={}
            )
            
            # Update proposal vote counts
            if choice == VoteChoice.FOR:
                proposal.votes_for += voting_power
            elif choice == VoteChoice.AGAINST:
                proposal.votes_against += voting_power
            elif choice == VoteChoice.ABSTAIN:
                proposal.votes_abstain += voting_power
            
            proposal.total_votes += voting_power
            proposal.updated_at = datetime.utcnow()
            
            # Store vote
            self.votes[proposal_id].append(vote)
            
            self.logger.info(f"Vote submitted: {vote_id} on proposal {proposal_id}")
            return vote
            
        except Exception as e:
            self.logger.error(f"Vote submission failed: {e}")
            raise
    
    async def _get_voting_power(self, address: str) -> Decimal:
        """Calculate total voting power for an address"""
        total_power = Decimal("0")
        
        # Calculate voting power from each governance token
        for token in self.governance_tokens.values():
            # Mock token balance - in real implementation would query blockchain
            token_balance = Decimal("1000")  # Mock balance
            power = token_balance * token.voting_weight
            total_power += power
        
        # Add delegated voting power
        delegated_power = await self._get_delegated_voting_power(address)
        total_power += delegated_power
        
        return total_power
    
    async def _get_delegated_voting_power(self, delegate_address: str) -> Decimal:
        """Get voting power delegated to an address"""
        delegated_power = Decimal("0")
        
        for delegation in self.delegations.values():
            if (delegation.delegate_address == delegate_address and 
                delegation.is_active and
                (not delegation.expiry_date or delegation.expiry_date > datetime.utcnow())):
                delegated_power += delegation.voting_power
        
        return delegated_power
    
    async def _get_delegation_path(self, address: str) -> List[str]:
        """Get delegation path for an address"""
        path = [address]
        
        # Check if this address has delegated to someone else
        for delegation in self.delegations.values():
            if (delegation.delegator_address == address and 
                delegation.is_active and
                (not delegation.expiry_date or delegation.expiry_date > datetime.utcnow())):
                path.append(delegation.delegate_address)
                break
        
        return path
    
    async def delegate_voting_power(
        self,
        delegator_address: str,
        delegate_address: str,
        voting_power: Decimal,
        proposal_types: Optional[List[ProposalType]] = None,
        expiry_hours: Optional[int] = None
    ) -> Delegation:
        """
        Delegate voting power to another address
        
        Args:
            delegator_address: Address delegating the power
            delegate_address: Address receiving the delegation
            voting_power: Amount of voting power to delegate
            proposal_types: Types of proposals the delegation applies to
            expiry_hours: Hours until delegation expires
            
        Returns:
            Delegation record
        """
        try:
            delegation_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating delegation: {delegator_address} -> {delegate_address}")
            
            # Validate delegation
            await self._validate_delegation(delegator_address, delegate_address, voting_power)
            
            # Set expiry date
            expiry_date = None
            if expiry_hours:
                expiry_date = datetime.utcnow() + timedelta(hours=expiry_hours)
            
            delegation = Delegation(
                delegation_id=delegation_id,
                delegator_address=delegator_address,
                delegate_address=delegate_address,
                voting_power=voting_power,
                proposal_types=proposal_types or list(ProposalType),
                expiry_date=expiry_date,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            # Store delegation
            self.delegations[delegation_id] = delegation
            
            self.logger.info(f"Delegation created: {delegation_id}")
            return delegation
            
        except Exception as e:
            self.logger.error(f"Delegation creation failed: {e}")
            raise
    
    async def _validate_delegation(
        self,
        delegator_address: str,
        delegate_address: str,
        voting_power: Decimal
    ) -> None:
        """Validate delegation parameters"""
        if delegator_address == delegate_address:
            raise ValueError("Cannot delegate to self")
        
        # Check for circular delegation
        if await self._check_circular_delegation(delegator_address, delegate_address):
            raise ValueError("Circular delegation detected")
        
        # Validate available voting power
        available_power = await self._get_voting_power(delegator_address)
        if voting_power > available_power:
            raise ValueError(f"Insufficient voting power: {voting_power} > {available_power}")
    
    async def _check_circular_delegation(
        self,
        start_address: str,
        target_address: str,
        visited: Optional[set] = None
    ) -> bool:
        """Check for circular delegation chains"""
        if visited is None:
            visited = set()
        
        if start_address in visited:
            return True
        
        if start_address == target_address:
            return True
        
        visited.add(start_address)
        
        # Check if target_address has delegated to someone in the chain
        for delegation in self.delegations.values():
            if (delegation.delegator_address == target_address and 
                delegation.is_active):
                if await self._check_circular_delegation(
                    delegation.delegate_address, start_address, visited
                ):
                    return True
        
        return False
    
    async def execute_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Execute an approved proposal
        
        Args:
            proposal_id: Proposal to execute
            
        Returns:
            Execution result
        """
        try:
            if proposal_id not in self.proposals:
                raise ValueError(f"Proposal not found: {proposal_id}")
            
            proposal = self.proposals[proposal_id]
            
            # Validate execution eligibility
            await self._validate_execution_eligibility(proposal)
            
            self.logger.info(f"Executing proposal: {proposal_id}")
            
            # Execute based on proposal type
            execution_result = await self._execute_proposal_action(proposal)
            
            # Update proposal status
            proposal.status = ProposalStatus.EXECUTED
            proposal.updated_at = datetime.utcnow()
            
            result = {
                "proposal_id": proposal_id,
                "execution_result": execution_result,
                "executed_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Proposal executed: {proposal_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Proposal execution failed: {e}")
            proposal.status = ProposalStatus.CANCELLED
            raise
    
    async def _validate_execution_eligibility(self, proposal: Proposal) -> None:
        """Validate that a proposal is eligible for execution"""
        now = datetime.utcnow()
        
        # Check voting period has ended
        if now <= proposal.vote_end_time:
            raise ValueError("Voting period has not ended")
        
        # Check execution delay has passed
        execution_time = proposal.vote_end_time + proposal.execution_delay
        if now < execution_time:
            raise ValueError(f"Execution delay has not passed. Can execute at {execution_time}")
        
        # Check quorum
        total_supply = sum(token.circulating_supply for token in self.governance_tokens.values())
        quorum_percentage = (proposal.total_votes / total_supply) * 100
        
        if quorum_percentage < proposal.quorum_threshold:
            raise ValueError(f"Quorum not met: {quorum_percentage}% < {proposal.quorum_threshold}%")
        
        # Check approval
        if proposal.total_votes > 0:
            approval_percentage = (proposal.votes_for / proposal.total_votes) * 100
            
            if approval_percentage < proposal.approval_threshold:
                raise ValueError(f"Approval threshold not met: {approval_percentage}% < {proposal.approval_threshold}%")
        else:
            raise ValueError("No votes cast")
    
    async def _execute_proposal_action(self, proposal: Proposal) -> Dict[str, Any]:
        """Execute the specific action for a proposal type"""
        if proposal.proposal_type == ProposalType.PROTOCOL_UPGRADE:
            return await self._execute_protocol_upgrade(proposal)
        elif proposal.proposal_type == ProposalType.PARAMETER_CHANGE:
            return await self._execute_parameter_change(proposal)
        elif proposal.proposal_type == ProposalType.TREASURY_ALLOCATION:
            return await self._execute_treasury_allocation(proposal)
        else:
            # Generic execution
            return {
                "type": proposal.proposal_type.value,
                "params": proposal.execution_params,
                "executed": True
            }
    
    async def _execute_protocol_upgrade(self, proposal: Proposal) -> Dict[str, Any]:
        """Execute a protocol upgrade proposal"""
        # Mock implementation
        self.logger.info(f"Executing protocol upgrade for proposal {proposal.proposal_id}")
        return {
            "upgrade_type": "protocol",
            "version": proposal.execution_params.get("version", "1.0.0"),
            "contracts_upgraded": proposal.execution_params.get("contracts", []),
            "success": True
        }
    
    async def _execute_parameter_change(self, proposal: Proposal) -> Dict[str, Any]:
        """Execute a parameter change proposal"""
        # Mock implementation
        self.logger.info(f"Executing parameter change for proposal {proposal.proposal_id}")
        return {
            "parameters_changed": proposal.execution_params.get("parameters", {}),
            "success": True
        }
    
    async def _execute_treasury_allocation(self, proposal: Proposal) -> Dict[str, Any]:
        """Execute a treasury allocation proposal"""
        # Mock implementation
        self.logger.info(f"Executing treasury allocation for proposal {proposal.proposal_id}")
        return {
            "allocation_amount": proposal.execution_params.get("amount", "0"),
            "recipient": proposal.execution_params.get("recipient", ""),
            "purpose": proposal.execution_params.get("purpose", ""),
            "success": True
        }
    
    async def get_proposal_details(self, proposal_id: str) -> Dict[str, Any]:
        """Get detailed proposal information"""
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        proposal = self.proposals[proposal_id]
        votes = self.votes.get(proposal_id, [])
        
        return {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "description": proposal.description,
            "proposer_address": proposal.proposer_address,
            "proposal_type": proposal.proposal_type.value,
            "voting_mechanism": proposal.voting_mechanism.value,
            "vote_start_time": proposal.vote_start_time.isoformat(),
            "vote_end_time": proposal.vote_end_time.isoformat(),
            "status": proposal.status.value,
            "votes_for": str(proposal.votes_for),
            "votes_against": str(proposal.votes_against),
            "votes_abstain": str(proposal.votes_abstain),
            "total_votes": str(proposal.total_votes),
            "quorum_threshold": str(proposal.quorum_threshold),
            "approval_threshold": str(proposal.approval_threshold),
            "vote_count": len(votes),
            "metadata": proposal.metadata,
            "execution_params": proposal.execution_params,
            "created_at": proposal.created_at.isoformat(),
            "updated_at": proposal.updated_at.isoformat()
        }


class GovernanceManager:
    """
    Manager class for coordinating multiple DAO governance instances
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Governance Manager
        
        Args:
            config: Global governance configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.dao_instances: Dict[str, DAOGovernance] = {}
        
        # Initialize DAO instances for different domains
        dao_configs = config.get("dao_instances", {})
        for dao_name, dao_config in dao_configs.items():
            self.dao_instances[dao_name] = DAOGovernance(dao_config)
    
    async def create_cross_dao_proposal(
        self,
        proposal_template: Dict[str, Any],
        target_daos: List[str]
    ) -> Dict[str, Proposal]:
        """
        Create proposals across multiple DAO instances
        
        Args:
            proposal_template: Template for proposal creation
            target_daos: List of DAO names to create proposals in
            
        Returns:
            Proposals created in each DAO
        """
        results = {}
        
        for dao_name in target_daos:
            if dao_name in self.dao_instances:
                try:
                    dao = self.dao_instances[dao_name]
                    proposal = await dao.create_proposal(**proposal_template)
                    results[dao_name] = proposal
                    self.logger.info(f"Cross-DAO proposal created in {dao_name}")
                except Exception as e:
                    self.logger.error(f"Failed to create proposal in {dao_name}: {e}")
                    results[dao_name] = {"error": str(e)}
        
        return results
    
    async def get_governance_analytics(self) -> Dict[str, Any]:
        """Get governance analytics across all DAOs"""
        analytics = {
            "total_daos": len(self.dao_instances),
            "dao_names": list(self.dao_instances.keys()),
            "global_stats": {
                "total_proposals": 0,
                "active_proposals": 0,
                "total_votes": 0,
                "total_delegations": 0
            },
            "dao_stats": {}
        }
        
        for dao_name, dao in self.dao_instances.items():
            dao_proposals = len(dao.proposals)
            dao_active = len([p for p in dao.proposals.values() if p.status == ProposalStatus.ACTIVE])
            dao_votes = sum(len(votes) for votes in dao.votes.values())
            dao_delegations = len(dao.delegations)
            
            analytics["dao_stats"][dao_name] = {
                "proposals": dao_proposals,
                "active_proposals": dao_active,
                "votes": dao_votes,
                "delegations": dao_delegations
            }
            
            analytics["global_stats"]["total_proposals"] += dao_proposals
            analytics["global_stats"]["active_proposals"] += dao_active
            analytics["global_stats"]["total_votes"] += dao_votes
            analytics["global_stats"]["total_delegations"] += dao_delegations
        
        return analytics