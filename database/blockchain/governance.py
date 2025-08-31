"""Decentralized Governance System Module

Advanced decentralized autonomous organization (DAO) governance system for
the IA Influencer Agent platform enabling community-driven decision making,
proposal management, and democratic platform evolution.

Features:
- DAO governance with voting mechanisms
- Proposal creation and management system
- Token-based voting with delegation support
- Multi-signature treasury management
- Governance analytics and participation tracking
- Automated execution of approved proposals
- Reputation-based voting weights
- Quadratic voting and various voting mechanisms

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead AI Developer + Blockchain Specialist + Backend Senior + ML Engineer + 
      DBA + Security Expert + Microservices Architect + Audio Processing + 
      DevOps Engineer + IA Prompt Engineer

Copyright: All rights reserved. Unauthorized use prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import asyncio
from collections import defaultdict

from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

class ProposalType(Enum):
    """Types of governance proposals."""    PARAMETER_CHANGE = "parameter_change"
    TREASURY_ALLOCATION = "treasury_allocation"
    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARTNERSHIP = "partnership"
    EMERGENCY_ACTION = "emergency_action"
    GENERAL = "general"

class ProposalStatus(Enum):
    """Status of governance proposals."""    DRAFT = "draft"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class VotingMechanism(Enum):
    """Different voting mechanisms supported."""    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    QUADRATIC_VOTING = "quadratic_voting"
    CONVICTION_VOTING = "conviction_voting"
    RANKED_CHOICE = "ranked_choice"

class VoteChoice(Enum):
    """Voting choices."""    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"

@dataclass
class GovernanceToken:
    """Governance token configuration."""    token_address: str
    token_symbol: str
    token_name: str
    total_supply: Decimal
    voting_weight: Decimal = Decimal("1.0")
    delegation_enabled: bool = True
    snapshot_strategy: str = "block_number"

@dataclass
class Proposal:
    """Governance proposal structure."""    proposal_id: str
    proposer_address: str
    title: str
    description: str
    proposal_type: ProposalType
    voting_mechanism: VotingMechanism
    status: ProposalStatus
    created_at: datetime
    voting_start: datetime
    voting_end: datetime
    execution_deadline: Optional[datetime]
    quorum_threshold: Decimal
    approval_threshold: Decimal
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_data: Optional[Dict[str, Any]] = None

@dataclass
class Vote:
    """Individual vote record."""    vote_id: str
    proposal_id: str
    voter_address: str
    choice: VoteChoice
    voting_power: Decimal
    timestamp: datetime
    delegated_from: Optional[str] = None
    conviction: Optional[float] = None  # For conviction voting
    ranking: Optional[List[str]] = None  # For ranked choice

@dataclass
class VotingPower:
    """Voting power calculation for an address."""    address: str
    token_balance: Decimal
    delegated_power: Decimal
    reputation_multiplier: Decimal
    total_voting_power: Decimal
    snapshot_block: int

@dataclass
class GovernanceMetrics:
    """Governance participation and health metrics."""    total_proposals: int
    active_proposals: int
    total_voters: int
    average_participation_rate: float
    treasury_balance: Decimal
    token_distribution_gini: float
    governance_health_score: float
    last_updated: datetime

class GovernanceSystem:
    """    Comprehensive decentralized governance system providing democratic
    decision-making capabilities for the IA Influencer Agent platform.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize governance system.
        
        Args:
            config: Governance configuration including token settings, thresholds
        """        self.config = config
        self.governance_tokens: List[GovernanceToken] = []
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = defaultdict(list)
        self.delegations: Dict[str, str] = {}  # delegator -> delegate
        self.web3_instances: Dict[str, Web3] = {}
        self._initialize_governance_tokens()
    
    def _initialize_governance_tokens(self) -> None:
        """Initialize governance tokens from configuration."""        token_configs = self.config.get("governance_tokens", [])
        
        for token_config in token_configs:
            token = GovernanceToken(**token_config)
            self.governance_tokens.append(token)
            logger.info(f"Initialized governance token: {token.token_symbol}")
    
    async def create_proposal(
        self,
        proposer_address: str,
        title: str,
        description: str,
        proposal_type: ProposalType,
        voting_mechanism: VotingMechanism = VotingMechanism.SIMPLE_MAJORITY,
        voting_duration_hours: int = 168,  # 1 week default
        execution_delay_hours: int = 48,
        custom_thresholds: Optional[Dict[str, Decimal]] = None
    ) -> Proposal:
        """        Create a new governance proposal.
        
        Args:
            proposer_address: Address of the proposer
            title: Proposal title
            description: Detailed proposal description
            proposal_type: Type of proposal
            voting_mechanism: Voting mechanism to use
            voting_duration_hours: Duration of voting period
            execution_delay_hours: Delay before execution after approval
            custom_thresholds: Custom quorum and approval thresholds
            
        Returns:
            Created proposal
        """        try:
            # Validate proposer eligibility
            await self._validate_proposer_eligibility(proposer_address)
            
            # Generate proposal ID
            proposal_id = str(uuid.uuid4())
            
            # Set voting period
            now = datetime.utcnow()
            voting_start = now + timedelta(hours=24)  # 24-hour delay before voting starts
            voting_end = voting_start + timedelta(hours=voting_duration_hours)
            execution_deadline = voting_end + timedelta(hours=execution_delay_hours)
            
            # Set thresholds based on proposal type
            if custom_thresholds:
                quorum_threshold = custom_thresholds.get("quorum", Decimal("0.1"))
                approval_threshold = custom_thresholds.get("approval", Decimal("0.5"))
            else:
                quorum_threshold, approval_threshold = self._get_default_thresholds(proposal_type)
            
            # Create proposal
            proposal = Proposal(
                proposal_id=proposal_id,
                proposer_address=proposer_address,
                title=title,
                description=description,
                proposal_type=proposal_type,
                voting_mechanism=voting_mechanism,
                status=ProposalStatus.DRAFT,
                created_at=now,
                voting_start=voting_start,
                voting_end=voting_end,
                execution_deadline=execution_deadline,
                quorum_threshold=quorum_threshold,
                approval_threshold=approval_threshold
            )
            
            # Store proposal
            self.proposals[proposal_id] = proposal
            
            logger.info(f"Created proposal {proposal_id}: {title}")
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to create proposal: {e}")
            raise
    
    async def _validate_proposer_eligibility(self, proposer_address: str) -> None:
        """Validate that an address is eligible to create proposals."""        # Check minimum token balance requirement
        min_balance = self.config.get("min_proposal_balance", Decimal("1000"))
        
        voting_power = await self.calculate_voting_power(proposer_address)
        if voting_power.total_voting_power < min_balance:
            raise ValueError(
                f"Insufficient voting power: {voting_power.total_voting_power} < {min_balance}"
            )
        
        # Check if proposer has any active proposals (prevent spam)
        max_active_proposals = self.config.get("max_active_proposals_per_user", 3)
        active_proposals = [
            p for p in self.proposals.values()
            if p.proposer_address == proposer_address and p.status == ProposalStatus.ACTIVE
        ]
        
        if len(active_proposals) >= max_active_proposals:
            raise ValueError(
                f"Too many active proposals: {len(active_proposals)} >= {max_active_proposals}"
            )
    
    def _get_default_thresholds(self, proposal_type: ProposalType) -> Tuple[Decimal, Decimal]:
        """Get default quorum and approval thresholds for proposal type."""        thresholds = {
            ProposalType.PARAMETER_CHANGE: (Decimal("0.1"), Decimal("0.5")),
            ProposalType.TREASURY_ALLOCATION: (Decimal("0.15"), Decimal("0.6")),
            ProposalType.PROTOCOL_UPGRADE: (Decimal("0.2"), Decimal("0.67")),
            ProposalType.PARTNERSHIP: (Decimal("0.1"), Decimal("0.5")),
            ProposalType.EMERGENCY_ACTION: (Decimal("0.05"), Decimal("0.8")),
            ProposalType.GENERAL: (Decimal("0.1"), Decimal("0.5"))
        }
        
        return thresholds.get(proposal_type, (Decimal("0.1"), Decimal("0.5")))
    
    async def cast_vote(
        self,
        voter_address: str,
        proposal_id: str,
        choice: VoteChoice,
        conviction: Optional[float] = None,
        ranking: Optional[List[str]] = None
    ) -> Vote:
        """        Cast a vote on a proposal.
        
        Args:
            voter_address: Address of the voter
            proposal_id: ID of the proposal to vote on
            choice: Voting choice
            conviction: Conviction level (for conviction voting)
            ranking: Ranking preferences (for ranked choice voting)
            
        Returns:
            Vote record
        """        try:
            # Validate proposal exists and is active
            proposal = self.proposals.get(proposal_id)
            if not proposal:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            if proposal.status != ProposalStatus.ACTIVE:
                raise ValueError(f"Proposal {proposal_id} is not active for voting")
            
            # Check voting period
            now = datetime.utcnow()
            if now < proposal.voting_start or now > proposal.voting_end:
                raise ValueError("Voting period is not active")
            
            # Check if user already voted
            existing_votes = [
                v for v in self.votes[proposal_id]
                if v.voter_address == voter_address
            ]
            if existing_votes:
                raise ValueError("User has already voted on this proposal")
            
            # Calculate voting power
            voting_power_calc = await self.calculate_voting_power(
                voter_address, 
                snapshot_block=proposal.metadata.get("snapshot_block")
            )
            
            # Apply voting mechanism specific logic
            final_voting_power = self._apply_voting_mechanism(
                proposal.voting_mechanism,
                voting_power_calc.total_voting_power,
                conviction
            )
            
            # Create vote
            vote = Vote(
                vote_id=str(uuid.uuid4()),
                proposal_id=proposal_id,
                voter_address=voter_address,
                choice=choice,
                voting_power=final_voting_power,
                timestamp=now,
                conviction=conviction,
                ranking=ranking
            )
            
            # Check for delegation
            delegate = self.delegations.get(voter_address)
            if delegate:
                vote.delegated_from = voter_address
                vote.voter_address = delegate
            
            # Store vote
            self.votes[proposal_id].append(vote)
            
            logger.info(
                f"Vote cast by {voter_address} on proposal {proposal_id}: "
                f"{choice.value} with power {final_voting_power}"
            )
            
            return vote
            
        except Exception as e:
            logger.error(f"Failed to cast vote: {e}")
            raise
    
    def _apply_voting_mechanism(
        self,
        mechanism: VotingMechanism,
        base_power: Decimal,
        conviction: Optional[float]
    ) -> Decimal:
        """Apply voting mechanism specific calculations to voting power."""        if mechanism == VotingMechanism.SIMPLE_MAJORITY:
            return base_power
        
        elif mechanism == VotingMechanism.QUADRATIC_VOTING:
            # Quadratic voting: square root of token balance
            return Decimal(str(float(base_power) ** 0.5))
        
        elif mechanism == VotingMechanism.CONVICTION_VOTING:
            # Conviction voting: power increases with conviction
            if conviction is None:
                conviction = 1.0
            return base_power * Decimal(str(conviction))
        
        else:
            return base_power
    
    async def calculate_voting_power(
        self,
        address: str,
        snapshot_block: Optional[int] = None
    ) -> VotingPower:
        """        Calculate voting power for an address.
        
        Args:
            address: Address to calculate voting power for
            snapshot_block: Block number for snapshot (None for current)
            
        Returns:
            Voting power calculation
        """        try:
            total_power = Decimal("0")
            total_balance = Decimal("0")
            delegated_power = Decimal("0")
            
            # Calculate power from each governance token
            for token in self.governance_tokens:
                balance = await self._get_token_balance(
                    address, 
                    token.token_address, 
                    snapshot_block
                )
                
                weighted_balance = balance * token.voting_weight
                total_balance += balance
                total_power += weighted_balance
            
            # Add delegated power
            delegated_power = await self._calculate_delegated_power(address, snapshot_block)
            total_power += delegated_power
            
            # Apply reputation multiplier
            reputation_multiplier = await self._calculate_reputation_multiplier(address)
            total_power *= reputation_multiplier
            
            return VotingPower(
                address=address,
                token_balance=total_balance,
                delegated_power=delegated_power,
                reputation_multiplier=reputation_multiplier,
                total_voting_power=total_power,
                snapshot_block=snapshot_block or 0
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate voting power: {e}")
            return VotingPower(
                address=address,
                token_balance=Decimal("0"),
                delegated_power=Decimal("0"),
                reputation_multiplier=Decimal("1"),
                total_voting_power=Decimal("0"),
                snapshot_block=snapshot_block or 0
            )
    
    async def _get_token_balance(
        self,
        address: str,
        token_address: str,
        snapshot_block: Optional[int]
    ) -> Decimal:
        """Get token balance for an address at a specific block."""        # Mock implementation - in production, would query blockchain
        return Decimal(str(np.random.uniform(100, 10000)))
    
    async def _calculate_delegated_power(
        self,
        delegate_address: str,
        snapshot_block: Optional[int]
    ) -> Decimal:
        """Calculate total power delegated to an address."""        delegated_power = Decimal("0")
        
        for delegator, delegate in self.delegations.items():
            if delegate == delegate_address:
                delegator_power = await self.calculate_voting_power(delegator, snapshot_block)
                delegated_power += delegator_power.token_balance
        
        return delegated_power
    
    async def _calculate_reputation_multiplier(self, address: str) -> Decimal:
        """Calculate reputation-based voting power multiplier."""        # Mock implementation - in production, would calculate based on:
        # - Participation history
        # - Proposal success rate
        # - Community contribution score
        return Decimal("1.0")
    
    async def delegate_voting_power(
        self,
        delegator_address: str,
        delegate_address: str
    ) -> bool:
        """        Delegate voting power to another address.
        
        Args:
            delegator_address: Address delegating power
            delegate_address: Address receiving delegated power
            
        Returns:
            True if delegation successful
        """        try:
            # Validate addresses
            if delegator_address == delegate_address:
                raise ValueError("Cannot delegate to self")
            
            # Check for circular delegation
            if await self._check_circular_delegation(delegate_address, delegator_address):
                raise ValueError("Circular delegation detected")
            
            # Store delegation
            self.delegations[delegator_address] = delegate_address
            
            logger.info(f"Delegated voting power from {delegator_address} to {delegate_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delegate voting power: {e}")
            return False
    
    async def _check_circular_delegation(
        self,
        start_address: str,
        target_address: str,
        visited: Optional[set] = None
    ) -> bool:
        """Check for circular delegation chains."""        if visited is None:
            visited = set()
        
        if start_address in visited:
            return True
        
        if start_address == target_address:
            return True
        
        visited.add(start_address)
        delegate = self.delegations.get(start_address)
        
        if delegate:
            return await self._check_circular_delegation(delegate, target_address, visited)
        
        return False
    
    async def update_proposal_status(self) -> None:
        """Update status of all proposals based on current state."""        now = datetime.utcnow()
        
        for proposal in self.proposals.values():
            try:
                if proposal.status == ProposalStatus.DRAFT and now >= proposal.voting_start:
                    proposal.status = ProposalStatus.ACTIVE
                    logger.info(f"Proposal {proposal.proposal_id} is now active for voting")
                
                elif proposal.status == ProposalStatus.ACTIVE and now >= proposal.voting_end:
                    # Calculate voting results
                    result = await self._calculate_voting_result(proposal.proposal_id)
                    
                    if result["quorum_reached"] and result["approval_reached"]:
                        proposal.status = ProposalStatus.SUCCEEDED
                        logger.info(f"Proposal {proposal.proposal_id} succeeded")
                    else:
                        proposal.status = ProposalStatus.DEFEATED
                        logger.info(f"Proposal {proposal.proposal_id} was defeated")
                
                elif proposal.status == ProposalStatus.SUCCEEDED:
                    # Queue for execution
                    proposal.status = ProposalStatus.QUEUED
                    await self._queue_proposal_execution(proposal)
                
                elif proposal.status == ProposalStatus.QUEUED:
                    # Check if execution deadline passed
                    if proposal.execution_deadline and now > proposal.execution_deadline:
                        proposal.status = ProposalStatus.EXPIRED
                        logger.warning(f"Proposal {proposal.proposal_id} expired without execution")
                        
            except Exception as e:
                logger.error(f"Failed to update proposal {proposal.proposal_id} status: {e}")
    
    async def _calculate_voting_result(self, proposal_id: str) -> Dict[str, Any]:
        """Calculate voting results for a proposal."""        proposal = self.proposals[proposal_id]
        votes = self.votes[proposal_id]
        
        # Calculate total voting power
        total_for = sum(v.voting_power for v in votes if v.choice == VoteChoice.FOR)
        total_against = sum(v.voting_power for v in votes if v.choice == VoteChoice.AGAINST)
        total_abstain = sum(v.voting_power for v in votes if v.choice == VoteChoice.ABSTAIN)
        total_votes = total_for + total_against + total_abstain
        
        # Get total possible voting power (approximate)
        total_supply = sum(token.total_supply for token in self.governance_tokens)
        
        # Check quorum
        quorum_reached = total_votes >= (total_supply * proposal.quorum_threshold)
        
        # Check approval based on voting mechanism
        if proposal.voting_mechanism == VotingMechanism.SUPERMAJORITY:
            approval_reached = total_for >= (total_votes * Decimal("0.67"))
        else:
            approval_reached = total_for >= (total_votes * proposal.approval_threshold)
        
        return {
            "total_for": float(total_for),
            "total_against": float(total_against),
            "total_abstain": float(total_abstain),
            "total_votes": float(total_votes),
            "quorum_reached": quorum_reached,
            "approval_reached": approval_reached,
            "participation_rate": float(total_votes / total_supply) if total_supply > 0 else 0
        }
    
    async def _queue_proposal_execution(self, proposal: Proposal) -> None:
        """Queue a proposal for automated execution."""        # Mock implementation - in production, would integrate with execution system
        logger.info(f"Queued proposal {proposal.proposal_id} for execution")
    
    async def execute_proposal(self, proposal_id: str) -> bool:
        """        Execute an approved proposal.
        
        Args:
            proposal_id: ID of the proposal to execute
            
        Returns:
            True if execution successful
        """        try:
            proposal = self.proposals.get(proposal_id)
            if not proposal:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            if proposal.status != ProposalStatus.QUEUED:
                raise ValueError(f"Proposal {proposal_id} is not ready for execution")
            
            # Execute based on proposal type
            success = await self._execute_proposal_action(proposal)
            
            if success:
                proposal.status = ProposalStatus.EXECUTED
                logger.info(f"Successfully executed proposal {proposal_id}")
            else:
                logger.error(f"Failed to execute proposal {proposal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute proposal {proposal_id}: {e}")
            return False
    
    async def _execute_proposal_action(self, proposal: Proposal) -> bool:
        """Execute the specific action defined in a proposal."""        # Mock implementation - in production, would execute based on proposal type
        if proposal.proposal_type == ProposalType.PARAMETER_CHANGE:
            return await self._execute_parameter_change(proposal)
        elif proposal.proposal_type == ProposalType.TREASURY_ALLOCATION:
            return await self._execute_treasury_allocation(proposal)
        elif proposal.proposal_type == ProposalType.PROTOCOL_UPGRADE:
            return await self._execute_protocol_upgrade(proposal)
        
        return True
    
    async def _execute_parameter_change(self, proposal: Proposal) -> bool:
        """Execute a parameter change proposal."""        # Mock implementation
        logger.info(f"Executing parameter change for proposal {proposal.proposal_id}")
        return True
    
    async def _execute_treasury_allocation(self, proposal: Proposal) -> bool:
        """Execute a treasury allocation proposal."""        # Mock implementation
        logger.info(f"Executing treasury allocation for proposal {proposal.proposal_id}")
        return True
    
    async def _execute_protocol_upgrade(self, proposal: Proposal) -> bool:
        """Execute a protocol upgrade proposal."""        # Mock implementation
        logger.info(f"Executing protocol upgrade for proposal {proposal.proposal_id}")
        return True
    
    def get_proposal_details(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a proposal including voting results."""        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None
        
        votes = self.votes[proposal_id]
        
        # Calculate voting statistics
        total_for = sum(v.voting_power for v in votes if v.choice == VoteChoice.FOR)
        total_against = sum(v.voting_power for v in votes if v.choice == VoteChoice.AGAINST)
        total_abstain = sum(v.voting_power for v in votes if v.choice == VoteChoice.ABSTAIN)
        
        return {
            "proposal": {
                "id": proposal.proposal_id,
                "title": proposal.title,
                "description": proposal.description,
                "type": proposal.proposal_type.value,
                "status": proposal.status.value,
                "proposer": proposal.proposer_address,
                "created_at": proposal.created_at.isoformat(),
                "voting_start": proposal.voting_start.isoformat(),
                "voting_end": proposal.voting_end.isoformat(),
                "quorum_threshold": float(proposal.quorum_threshold),
                "approval_threshold": float(proposal.approval_threshold)
            },
            "voting_results": {
                "total_for": float(total_for),
                "total_against": float(total_against),
                "total_abstain": float(total_abstain),
                "vote_count": len(votes)
            }
        }
    
    async def get_governance_metrics(self) -> GovernanceMetrics:
        """Get comprehensive governance health and participation metrics."""        try:
            total_proposals = len(self.proposals)
            active_proposals = len([
                p for p in self.proposals.values() 
                if p.status == ProposalStatus.ACTIVE
            ])
            
            # Calculate unique voters
            all_voters = set()
            for votes in self.votes.values():
                all_voters.update(v.voter_address for v in votes)
            
            total_voters = len(all_voters)
            
            # Calculate average participation rate
            participation_rates = []
            for proposal_id, votes in self.votes.items():
                proposal = self.proposals[proposal_id]
                if proposal.status in [ProposalStatus.SUCCEEDED, ProposalStatus.DEFEATED]:
                    total_votes = sum(v.voting_power for v in votes)
                    total_supply = sum(token.total_supply for token in self.governance_tokens)
                    if total_supply > 0:
                        participation_rates.append(float(total_votes / total_supply))
            
            avg_participation = statistics.mean(participation_rates) if participation_rates else 0.0
            
            # Mock treasury balance and other metrics
            treasury_balance = Decimal("1000000")  # Mock value
            token_distribution_gini = 0.4  # Mock Gini coefficient
            
            # Calculate governance health score
            health_score = self._calculate_governance_health_score(
                avg_participation, token_distribution_gini, total_voters
            )
            
            return GovernanceMetrics(
                total_proposals=total_proposals,
                active_proposals=active_proposals,
                total_voters=total_voters,
                average_participation_rate=avg_participation,
                treasury_balance=treasury_balance,
                token_distribution_gini=token_distribution_gini,
                governance_health_score=health_score,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate governance metrics: {e}")
            raise
    
    def _calculate_governance_health_score(
        self,
        participation_rate: float,
        gini_coefficient: float,
        voter_count: int
    ) -> float:
        """Calculate overall governance health score (0-100)."""        # Participation score (0-40 points)
        participation_score = min(participation_rate * 100, 40)
        
        # Distribution score (0-30 points) - lower Gini is better
        distribution_score = max(0, 30 - (gini_coefficient * 30))
        
        # Voter diversity score (0-30 points)
        voter_diversity_score = min(voter_count / 1000 * 30, 30)
        
        total_score = participation_score + distribution_score + voter_diversity_score
        return min(total_score, 100.0)
    
    def get_user_governance_activity(self, address: str) -> Dict[str, Any]:
        """Get governance activity summary for a specific address."""        # Count proposals created
        proposals_created = len([
            p for p in self.proposals.values()
            if p.proposer_address == address
        ])
        
        # Count votes cast
        votes_cast = 0
        for votes in self.votes.values():
            votes_cast += len([v for v in votes if v.voter_address == address])
        
        # Check delegation status
        delegated_to = self.delegations.get(address)
        delegated_from = [
            delegator for delegator, delegate in self.delegations.items()
            if delegate == address
        ]
        
        return {
            "address": address,
            "proposals_created": proposals_created,
            "votes_cast": votes_cast,
            "delegated_to": delegated_to,
            "delegated_from_count": len(delegated_from),
            "delegated_from": delegated_from
        }
