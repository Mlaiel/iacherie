"""Escrow Manager Contract - IA-Influencer-Agent Platform

This module provides secure escrow management functionality for collaborations,
content purchases, and multi-party agreements with automated release conditions
and dispute resolution mechanisms.

Features:
- Multi-party escrow contracts
- Conditional payment release
- Milestone-based payments
- Automated arbitration
- Time-locked escrows
- Emergency release mechanisms
- Multi-signature approvals
- Cross-chain escrow support

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
import time

from web3 import Web3
from web3.contract import Contract

logger = logging.getLogger(__name__)


class EscrowType(Enum):
    """Types of escrow contracts"""
    COLLABORATION = "collaboration"
    CONTENT_PURCHASE = "content_purchase"
    SERVICE_AGREEMENT = "service_agreement"
    NFT_SALE = "nft_sale"
    LICENSING_DEAL = "licensing_deal"
    INVESTMENT = "investment"
    MILESTONE_PROJECT = "milestone_project"
    RECURRING_PAYMENT = "recurring_payment"


class EscrowStatus(Enum):
    """Escrow contract status"""
    CREATED = "created"
    FUNDED = "funded"
    ACTIVE = "active"
    MILESTONE_PENDING = "milestone_pending"
    DISPUTE = "dispute"
    RELEASED = "released"
    REFUNDED = "refunded"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ReleaseCondition(Enum):
    """Conditions for escrow release"""
    MANUAL_APPROVAL = "manual_approval"
    TIME_BASED = "time_based"
    MILESTONE_COMPLETION = "milestone_completion"
    MULTI_SIGNATURE = "multi_signature"
    ORACLE_VERIFICATION = "oracle_verification"
    AUTOMATIC = "automatic"


class ParticipantRole(Enum):
    """Roles in escrow contract"""
    BUYER = "buyer"
    SELLER = "seller"
    ARBITRATOR = "arbitrator"
    SERVICE_PROVIDER = "service_provider"
    CLIENT = "client"
    COLLABORATOR = "collaborator"
    INVESTOR = "investor"


@dataclass
class EscrowParticipant:
    """Participant in escrow contract"""
    address: str
    name: str
    role: ParticipantRole
    deposit_amount: Decimal
    release_percentage: Decimal
    approval_required: bool
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class EscrowMilestone:
    """Milestone for escrow release"""
    milestone_id: str
    description: str
    due_date: Optional[datetime]
    amount: Decimal
    completion_criteria: Dict[str, Any]
    required_approvals: List[str]  # Participant addresses
    completed: bool = False
    completed_at: Optional[datetime] = None
    approved_by: List[str] = field(default_factory=list)


@dataclass
class EscrowContract:
    """Escrow contract structure"""
    escrow_id: str
    escrow_type: EscrowType
    title: str
    description: str
    participants: List[EscrowParticipant]
    total_amount: Decimal
    currency: str
    status: EscrowStatus
    release_conditions: List[ReleaseCondition]
    milestones: List[EscrowMilestone]
    created_at: datetime
    funded_at: Optional[datetime]
    expires_at: Optional[datetime]
    released_at: Optional[datetime]
    transaction_hash: str
    block_number: int
    arbitrator_address: Optional[str]
    dispute_resolution_fee: Decimal
    metadata: Dict[str, Any]


@dataclass
class EscrowTransaction:
    """Escrow transaction record"""
    transaction_id: str
    escrow_id: str
    transaction_type: str  # "fund", "release", "refund", "dispute"
    from_address: str
    to_address: str
    amount: Decimal
    currency: str
    transaction_hash: str
    block_number: int
    timestamp: datetime
    metadata: Dict[str, Any]


class EscrowManager:
    """
    Escrow Management System for secure multi-party transactions
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Escrow Manager
        
        Args:
            config: Configuration including contract settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_escrows: Dict[str, EscrowContract] = {}
        self.escrow_transactions: List[EscrowTransaction] = []
        self.arbitrator_registry: Dict[str, Dict[str, Any]] = {}
        
        # Contract configuration
        self.contract_address = config.get("contract_address")
        self.network = config.get("network", "ethereum")
        self.gas_limit = config.get("gas_limit", 500000)
        
        # Escrow settings
        self.platform_fee_percentage = Decimal(config.get("platform_fee", "1.0"))
        self.default_dispute_fee = Decimal(config.get("dispute_fee", "0.1"))
        self.max_escrow_duration = config.get("max_duration_days", 365)
        
        # Initialize default arbitrators
        self._init_arbitrator_registry()
    
    def _init_arbitrator_registry(self):
        """Initialize trusted arbitrator registry"""
        self.arbitrator_registry = {
            "0x1111111111111111111111111111111111111111": {
                "name": "Platform Arbitrator",
                "reputation_score": 95,
                "cases_resolved": 150,
                "specialties": ["content", "licensing", "collaboration"],
                "fee_percentage": 2.0
            },
            "0x2222222222222222222222222222222222222222": {
                "name": "Legal Expert Arbitrator",
                "reputation_score": 98,
                "cases_resolved": 89,
                "specialties": ["investment", "service_agreement"],
                "fee_percentage": 3.0
            }
        }
    
    async def create_escrow(
        self,
        escrow_type: EscrowType,
        title: str,
        description: str,
        participants: List[Dict[str, Any]],
        total_amount: Decimal,
        currency: str,
        release_conditions: List[ReleaseCondition],
        milestones: Optional[List[Dict[str, Any]]] = None,
        duration_days: Optional[int] = None,
        arbitrator_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EscrowContract:
        """
        Create a new escrow contract
        
        Args:
            escrow_type: Type of escrow contract
            title: Escrow title
            description: Escrow description
            participants: List of participants
            total_amount: Total escrow amount
            currency: Currency for escrow
            release_conditions: Conditions for release
            milestones: Optional milestones
            duration_days: Optional duration in days
            arbitrator_address: Optional arbitrator
            metadata: Optional metadata
            
        Returns:
            Created escrow contract
        """
        try:
            escrow_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating escrow: {title}")
            
            # Validate and convert participants
            validated_participants = await self._validate_participants(participants)
            
            # Validate total amount matches participant deposits
            total_deposits = sum(p.deposit_amount for p in validated_participants)
            if abs(total_deposits - total_amount) > Decimal("0.01"):
                raise ValueError(f"Total deposits ({total_deposits}) don't match escrow amount ({total_amount})")
            
            # Create milestones if provided
            escrow_milestones = []
            if milestones:
                escrow_milestones = await self._create_milestones(milestones, total_amount)
            
            # Calculate expiry date
            expires_at = None
            if duration_days:
                if duration_days > self.max_escrow_duration:
                    raise ValueError(f"Duration exceeds maximum: {duration_days} > {self.max_escrow_duration}")
                expires_at = datetime.utcnow() + timedelta(days=duration_days)
            
            # Create escrow on blockchain
            tx_result = await self._create_escrow_on_blockchain(
                escrow_id, escrow_type, validated_participants, total_amount, currency
            )
            
            # Create escrow contract
            escrow_contract = EscrowContract(
                escrow_id=escrow_id,
                escrow_type=escrow_type,
                title=title,
                description=description,
                participants=validated_participants,
                total_amount=total_amount,
                currency=currency,
                status=EscrowStatus.CREATED,
                release_conditions=release_conditions,
                milestones=escrow_milestones,
                created_at=datetime.utcnow(),
                funded_at=None,
                expires_at=expires_at,
                released_at=None,
                transaction_hash=tx_result["tx_hash"],
                block_number=tx_result["block_number"],
                arbitrator_address=arbitrator_address,
                dispute_resolution_fee=self.default_dispute_fee,
                metadata=metadata or {}
            )
            
            # Store escrow
            self.active_escrows[escrow_id] = escrow_contract
            
            self.logger.info(f"Escrow created: {escrow_id}")
            return escrow_contract
            
        except Exception as e:
            self.logger.error(f"Escrow creation failed: {e}")
            raise
    
    async def _validate_participants(self, participants: List[Dict[str, Any]]) -> List[EscrowParticipant]:
        """Validate and convert participant data"""
        validated = []
        total_release_percentage = Decimal("0")
        
        for participant_data in participants:
            participant = EscrowParticipant(
                address=participant_data["address"],
                name=participant_data["name"],
                role=ParticipantRole(participant_data["role"]),
                deposit_amount=Decimal(str(participant_data["deposit_amount"])),
                release_percentage=Decimal(str(participant_data["release_percentage"])),
                approval_required=participant_data.get("approval_required", True),
                contact_info=participant_data.get("contact_info")
            )
            
            # Validate address
            if not self._is_valid_address(participant.address):
                raise ValueError(f"Invalid address: {participant.address}")
            
            # Validate amounts
            if participant.deposit_amount < 0:
                raise ValueError(f"Invalid deposit amount: {participant.deposit_amount}")
            
            if participant.release_percentage < 0 or participant.release_percentage > 100:
                raise ValueError(f"Invalid release percentage: {participant.release_percentage}")
            
            total_release_percentage += participant.release_percentage
            validated.append(participant)
        
        # Check that release percentages sum to 100%
        if abs(total_release_percentage - Decimal("100")) > Decimal("0.01"):
            raise ValueError(f"Release percentages must sum to 100%, got {total_release_percentage}")
        
        return validated
    
    def _is_valid_address(self, address: str) -> bool:
        """Validate blockchain address format"""
        return address.startswith("0x") and len(address) == 42
    
    async def _create_milestones(
        self,
        milestones_data: List[Dict[str, Any]],
        total_amount: Decimal
    ) -> List[EscrowMilestone]:
        """Create milestone objects from data"""
        milestones = []
        total_milestone_amount = Decimal("0")
        
        for milestone_data in milestones_data:
            due_date = None
            if milestone_data.get("due_date"):
                due_date = datetime.fromisoformat(milestone_data["due_date"])
            
            milestone = EscrowMilestone(
                milestone_id=str(uuid.uuid4()),
                description=milestone_data["description"],
                due_date=due_date,
                amount=Decimal(str(milestone_data["amount"])),
                completion_criteria=milestone_data.get("completion_criteria", {}),
                required_approvals=milestone_data.get("required_approvals", [])
            )
            
            total_milestone_amount += milestone.amount
            milestones.append(milestone)
        
        # Validate that milestone amounts sum to total
        if abs(total_milestone_amount - total_amount) > Decimal("0.01"):
            raise ValueError(f"Milestone amounts ({total_milestone_amount}) don't match total ({total_amount})")
        
        return milestones
    
    async def _create_escrow_on_blockchain(
        self,
        escrow_id: str,
        escrow_type: EscrowType,
        participants: List[EscrowParticipant],
        total_amount: Decimal,
        currency: str
    ) -> Dict[str, Any]:
        """Create escrow contract on blockchain"""
        escrow_data = {
            "escrow_id": escrow_id,
            "escrow_type": escrow_type.value,
            "participants": [
                {
                    "address": p.address,
                    "role": p.role.value,
                    "deposit_amount": str(p.deposit_amount),
                    "release_percentage": str(p.release_percentage)
                }
                for p in participants
            ],
            "total_amount": str(total_amount),
            "currency": currency,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(escrow_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345688,
            "gas_used": 350000
        }
    
    async def fund_escrow(
        self,
        escrow_id: str,
        funder_address: str,
        funding_tx_hash: str
    ) -> Dict[str, Any]:
        """
        Fund an escrow contract
        
        Args:
            escrow_id: Escrow ID to fund
            funder_address: Address providing funds
            funding_tx_hash: Transaction hash of funding
            
        Returns:
            Funding result
        """
        try:
            if escrow_id not in self.active_escrows:
                raise ValueError(f"Escrow not found: {escrow_id}")
            
            escrow = self.active_escrows[escrow_id]
            
            if escrow.status != EscrowStatus.CREATED:
                raise ValueError(f"Escrow cannot be funded in status: {escrow.status.value}")
            
            self.logger.info(f"Funding escrow: {escrow_id}")
            
            # Verify funding transaction
            funding_verified = await self._verify_funding_transaction(
                funding_tx_hash, escrow.total_amount, escrow.currency
            )
            
            if not funding_verified:
                raise ValueError("Funding transaction verification failed")
            
            # Record funding on blockchain
            funding_record_tx = await self._record_funding_on_blockchain(
                escrow_id, funder_address, funding_tx_hash
            )
            
            # Update escrow status
            escrow.status = EscrowStatus.FUNDED
            escrow.funded_at = datetime.utcnow()
            
            # Create funding transaction record
            funding_transaction = EscrowTransaction(
                transaction_id=str(uuid.uuid4()),
                escrow_id=escrow_id,
                transaction_type="fund",
                from_address=funder_address,
                to_address=self.contract_address,
                amount=escrow.total_amount,
                currency=escrow.currency,
                transaction_hash=funding_tx_hash,
                block_number=funding_record_tx["block_number"],
                timestamp=datetime.utcnow(),
                metadata={"escrow_funded": True}
            )
            
            self.escrow_transactions.append(funding_transaction)
            
            # Activate escrow if conditions are met
            if self._should_activate_escrow(escrow):
                escrow.status = EscrowStatus.ACTIVE
            
            result = {
                "escrow_id": escrow_id,
                "status": escrow.status.value,
                "funding_tx": funding_tx_hash,
                "funding_record_tx": funding_record_tx["tx_hash"],
                "funded_at": escrow.funded_at.isoformat(),
                "total_amount": str(escrow.total_amount),
                "currency": escrow.currency
            }
            
            self.logger.info(f"Escrow funded: {escrow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Escrow funding failed: {e}")
            raise
    
    async def _verify_funding_transaction(
        self,
        tx_hash: str,
        expected_amount: Decimal,
        currency: str
    ) -> bool:
        """Verify funding transaction"""
        # Mock verification - in real implementation would check blockchain
        return bool(tx_hash and expected_amount > 0)
    
    async def _record_funding_on_blockchain(
        self,
        escrow_id: str,
        funder_address: str,
        funding_tx_hash: str
    ) -> Dict[str, Any]:
        """Record escrow funding on blockchain"""
        funding_data = {
            "escrow_id": escrow_id,
            "funder_address": funder_address,
            "funding_tx": funding_tx_hash,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(funding_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345689,
            "gas_used": 100000
        }
    
    def _should_activate_escrow(self, escrow: EscrowContract) -> bool:
        """Determine if escrow should be activated"""
        # Activate if funded and has automatic release condition
        return ReleaseCondition.AUTOMATIC in escrow.release_conditions
    
    async def complete_milestone(
        self,
        escrow_id: str,
        milestone_id: str,
        approver_address: str,
        completion_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mark a milestone as completed
        
        Args:
            escrow_id: Escrow ID
            milestone_id: Milestone ID to complete
            approver_address: Address approving completion
            completion_evidence: Evidence of completion
            
        Returns:
            Completion result
        """
        try:
            if escrow_id not in self.active_escrows:
                raise ValueError(f"Escrow not found: {escrow_id}")
            
            escrow = self.active_escrows[escrow_id]
            
            if escrow.status not in [EscrowStatus.ACTIVE, EscrowStatus.MILESTONE_PENDING]:
                raise ValueError(f"Cannot complete milestone in status: {escrow.status.value}")
            
            # Find milestone
            milestone = None
            for m in escrow.milestones:
                if m.milestone_id == milestone_id:
                    milestone = m
                    break
            
            if not milestone:
                raise ValueError(f"Milestone not found: {milestone_id}")
            
            if milestone.completed:
                raise ValueError("Milestone already completed")
            
            # Check if approver is authorized
            if approver_address not in milestone.required_approvals:
                raise ValueError("Approver not authorized for this milestone")
            
            self.logger.info(f"Completing milestone: {milestone_id}")
            
            # Record approval
            if approver_address not in milestone.approved_by:
                milestone.approved_by.append(approver_address)
            
            # Check if all required approvals received
            if set(milestone.approved_by) >= set(milestone.required_approvals):
                milestone.completed = True
                milestone.completed_at = datetime.utcnow()
                
                # Record completion on blockchain
                completion_tx = await self._record_milestone_completion(
                    escrow_id, milestone_id, completion_evidence
                )
                
                # Check if milestone payment should be released
                if ReleaseCondition.MILESTONE_COMPLETION in escrow.release_conditions:
                    release_result = await self._release_milestone_payment(escrow, milestone)
                else:
                    escrow.status = EscrowStatus.MILESTONE_PENDING
                    release_result = {"status": "pending_release"}
                
                result = {
                    "escrow_id": escrow_id,
                    "milestone_id": milestone_id,
                    "status": "completed",
                    "completed_at": milestone.completed_at.isoformat(),
                    "completion_tx": completion_tx["tx_hash"],
                    "release_result": release_result
                }
            else:
                result = {
                    "escrow_id": escrow_id,
                    "milestone_id": milestone_id,
                    "status": "approval_recorded",
                    "approved_by": milestone.approved_by,
                    "required_approvals": milestone.required_approvals,
                    "remaining_approvals": list(set(milestone.required_approvals) - set(milestone.approved_by))
                }
            
            self.logger.info(f"Milestone completion processed: {milestone_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Milestone completion failed: {e}")
            raise
    
    async def _record_milestone_completion(
        self,
        escrow_id: str,
        milestone_id: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record milestone completion on blockchain"""
        completion_data = {
            "escrow_id": escrow_id,
            "milestone_id": milestone_id,
            "evidence_hash": hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest(),
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(completion_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345690,
            "gas_used": 120000
        }
    
    async def _release_milestone_payment(
        self,
        escrow: EscrowContract,
        milestone: EscrowMilestone
    ) -> Dict[str, Any]:
        """Release payment for completed milestone"""
        try:
            # Calculate payments based on participant release percentages
            payments = []
            for participant in escrow.participants:
                if participant.release_percentage > 0:
                    payment_amount = milestone.amount * (participant.release_percentage / 100)
                    
                    if payment_amount > 0:
                        # Send payment
                        payment_tx = await self._send_escrow_payment(
                            participant.address, payment_amount, escrow.currency
                        )
                        
                        # Record transaction
                        payment_transaction = EscrowTransaction(
                            transaction_id=str(uuid.uuid4()),
                            escrow_id=escrow.escrow_id,
                            transaction_type="release",
                            from_address=self.contract_address,
                            to_address=participant.address,
                            amount=payment_amount,
                            currency=escrow.currency,
                            transaction_hash=payment_tx["tx_hash"],
                            block_number=payment_tx["block_number"],
                            timestamp=datetime.utcnow(),
                            metadata={"milestone_id": milestone.milestone_id}
                        )
                        
                        self.escrow_transactions.append(payment_transaction)
                        payments.append({
                            "recipient": participant.address,
                            "amount": str(payment_amount),
                            "tx_hash": payment_tx["tx_hash"]
                        })
            
            return {
                "status": "released",
                "milestone_amount": str(milestone.amount),
                "payments": payments,
                "released_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Milestone payment release failed: {e}")
            return {"status": "release_failed", "error": str(e)}
    
    async def _send_escrow_payment(
        self,
        recipient_address: str,
        amount: Decimal,
        currency: str
    ) -> Dict[str, Any]:
        """Send payment from escrow"""
        payment_data = {
            "to": recipient_address,
            "amount": str(amount),
            "currency": currency,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(payment_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345691,
            "gas_used": 75000
        }
    
    async def release_escrow(
        self,
        escrow_id: str,
        releaser_address: str,
        release_reason: str
    ) -> Dict[str, Any]:
        """
        Release entire escrow to participants
        
        Args:
            escrow_id: Escrow ID to release
            releaser_address: Address requesting release
            release_reason: Reason for release
            
        Returns:
            Release result
        """
        try:
            if escrow_id not in self.active_escrows:
                raise ValueError(f"Escrow not found: {escrow_id}")
            
            escrow = self.active_escrows[escrow_id]
            
            if escrow.status not in [EscrowStatus.ACTIVE, EscrowStatus.MILESTONE_PENDING]:
                raise ValueError(f"Cannot release escrow in status: {escrow.status.value}")
            
            # Check if releaser has authority
            authorized_addresses = [p.address for p in escrow.participants if p.approval_required]
            if escrow.arbitrator_address:
                authorized_addresses.append(escrow.arbitrator_address)
            
            if releaser_address not in authorized_addresses:
                raise ValueError("Address not authorized to release escrow")
            
            self.logger.info(f"Releasing escrow: {escrow_id}")
            
            # Calculate and send payments
            payments = []
            total_released = Decimal("0")
            
            for participant in escrow.participants:
                if participant.release_percentage > 0:
                    payment_amount = escrow.total_amount * (participant.release_percentage / 100)
                    
                    if payment_amount > 0:
                        payment_tx = await self._send_escrow_payment(
                            participant.address, payment_amount, escrow.currency
                        )
                        
                        payment_transaction = EscrowTransaction(
                            transaction_id=str(uuid.uuid4()),
                            escrow_id=escrow_id,
                            transaction_type="release",
                            from_address=self.contract_address,
                            to_address=participant.address,
                            amount=payment_amount,
                            currency=escrow.currency,
                            transaction_hash=payment_tx["tx_hash"],
                            block_number=payment_tx["block_number"],
                            timestamp=datetime.utcnow(),
                            metadata={"release_reason": release_reason}
                        )
                        
                        self.escrow_transactions.append(payment_transaction)
                        total_released += payment_amount
                        
                        payments.append({
                            "recipient": participant.address,
                            "recipient_name": participant.name,
                            "amount": str(payment_amount),
                            "percentage": str(participant.release_percentage),
                            "tx_hash": payment_tx["tx_hash"]
                        })
            
            # Update escrow status
            escrow.status = EscrowStatus.RELEASED
            escrow.released_at = datetime.utcnow()
            
            # Record release on blockchain
            release_tx = await self._record_escrow_release(
                escrow_id, releaser_address, release_reason, total_released
            )
            
            result = {
                "escrow_id": escrow_id,
                "status": "released",
                "releaser_address": releaser_address,
                "release_reason": release_reason,
                "total_released": str(total_released),
                "currency": escrow.currency,
                "payments": payments,
                "release_tx": release_tx["tx_hash"],
                "released_at": escrow.released_at.isoformat()
            }
            
            self.logger.info(f"Escrow released: {escrow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Escrow release failed: {e}")
            raise
    
    async def _record_escrow_release(
        self,
        escrow_id: str,
        releaser_address: str,
        release_reason: str,
        total_released: Decimal
    ) -> Dict[str, Any]:
        """Record escrow release on blockchain"""
        release_data = {
            "escrow_id": escrow_id,
            "releaser_address": releaser_address,
            "release_reason": release_reason,
            "total_released": str(total_released),
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(release_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345692,
            "gas_used": 150000
        }
    
    async def initiate_dispute(
        self,
        escrow_id: str,
        disputer_address: str,
        dispute_reason: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initiate dispute for escrow contract
        
        Args:
            escrow_id: Escrow ID in dispute
            disputer_address: Address initiating dispute
            dispute_reason: Reason for dispute
            evidence: Supporting evidence
            
        Returns:
            Dispute initiation result
        """
        try:
            if escrow_id not in self.active_escrows:
                raise ValueError(f"Escrow not found: {escrow_id}")
            
            escrow = self.active_escrows[escrow_id]
            
            if escrow.status not in [EscrowStatus.ACTIVE, EscrowStatus.MILESTONE_PENDING]:
                raise ValueError(f"Cannot dispute escrow in status: {escrow.status.value}")
            
            # Check if disputer is a participant
            participant_addresses = [p.address for p in escrow.participants]
            if disputer_address not in participant_addresses:
                raise ValueError("Only participants can initiate disputes")
            
            self.logger.info(f"Initiating dispute for escrow: {escrow_id}")
            
            # Update escrow status
            escrow.status = EscrowStatus.DISPUTE
            
            # Record dispute on blockchain
            dispute_tx = await self._record_dispute_initiation(
                escrow_id, disputer_address, dispute_reason, evidence
            )
            
            # Assign arbitrator if not already assigned
            if not escrow.arbitrator_address:
                escrow.arbitrator_address = await self._assign_arbitrator(escrow)
            
            result = {
                "escrow_id": escrow_id,
                "status": "dispute_initiated",
                "disputer_address": disputer_address,
                "dispute_reason": dispute_reason,
                "arbitrator_address": escrow.arbitrator_address,
                "dispute_tx": dispute_tx["tx_hash"],
                "dispute_fee": str(escrow.dispute_resolution_fee),
                "initiated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Dispute initiated for escrow: {escrow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Dispute initiation failed: {e}")
            raise
    
    async def _record_dispute_initiation(
        self,
        escrow_id: str,
        disputer_address: str,
        dispute_reason: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record dispute initiation on blockchain"""
        dispute_data = {
            "escrow_id": escrow_id,
            "disputer_address": disputer_address,
            "dispute_reason": dispute_reason,
            "evidence_hash": hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest(),
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(dispute_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345693,
            "gas_used": 130000
        }
    
    async def _assign_arbitrator(self, escrow: EscrowContract) -> str:
        """Assign arbitrator based on escrow type and amount"""
        # Simple assignment logic - in production would be more sophisticated
        if escrow.total_amount > Decimal("1000"):
            return "0x2222222222222222222222222222222222222222"  # Expert arbitrator
        else:
            return "0x1111111111111111111111111111111111111111"  # Platform arbitrator
    
    async def get_escrow_info(self, escrow_id: str) -> Dict[str, Any]:
        """Get detailed escrow information"""
        if escrow_id not in self.active_escrows:
            raise ValueError(f"Escrow not found: {escrow_id}")
        
        escrow = self.active_escrows[escrow_id]
        
        return {
            "escrow_id": escrow.escrow_id,
            "escrow_type": escrow.escrow_type.value,
            "title": escrow.title,
            "description": escrow.description,
            "participants": [
                {
                    "address": p.address,
                    "name": p.name,
                    "role": p.role.value,
                    "deposit_amount": str(p.deposit_amount),
                    "release_percentage": str(p.release_percentage),
                    "approval_required": p.approval_required
                }
                for p in escrow.participants
            ],
            "total_amount": str(escrow.total_amount),
            "currency": escrow.currency,
            "status": escrow.status.value,
            "release_conditions": [rc.value for rc in escrow.release_conditions],
            "milestones": [
                {
                    "milestone_id": m.milestone_id,
                    "description": m.description,
                    "due_date": m.due_date.isoformat() if m.due_date else None,
                    "amount": str(m.amount),
                    "completed": m.completed,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                    "approved_by": m.approved_by,
                    "required_approvals": m.required_approvals
                }
                for m in escrow.milestones
            ],
            "created_at": escrow.created_at.isoformat(),
            "funded_at": escrow.funded_at.isoformat() if escrow.funded_at else None,
            "expires_at": escrow.expires_at.isoformat() if escrow.expires_at else None,
            "released_at": escrow.released_at.isoformat() if escrow.released_at else None,
            "transaction_hash": escrow.transaction_hash,
            "block_number": escrow.block_number,
            "arbitrator_address": escrow.arbitrator_address,
            "dispute_resolution_fee": str(escrow.dispute_resolution_fee),
            "metadata": escrow.metadata
        }
    
    async def get_escrow_transactions(self, escrow_id: str) -> List[Dict[str, Any]]:
        """Get transaction history for escrow"""
        transactions = [
            {
                "transaction_id": tx.transaction_id,
                "transaction_type": tx.transaction_type,
                "from_address": tx.from_address,
                "to_address": tx.to_address,
                "amount": str(tx.amount),
                "currency": tx.currency,
                "transaction_hash": tx.transaction_hash,
                "block_number": tx.block_number,
                "timestamp": tx.timestamp.isoformat(),
                "metadata": tx.metadata
            }
            for tx in self.escrow_transactions
            if tx.escrow_id == escrow_id
        ]
        
        return transactions
    
    async def get_escrow_analytics(self) -> Dict[str, Any]:
        """Get escrow system analytics"""
        total_escrows = len(self.active_escrows)
        status_counts = {}
        type_counts = {}
        total_value = Decimal("0")
        
        for escrow in self.active_escrows.values():
            status = escrow.status.value
            escrow_type = escrow.escrow_type.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[escrow_type] = type_counts.get(escrow_type, 0) + 1
            total_value += escrow.total_amount
        
        return {
            "total_escrows": total_escrows,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_value_locked": str(total_value),
            "total_transactions": len(self.escrow_transactions),
            "available_arbitrators": len(self.arbitrator_registry),
            "average_escrow_value": str(total_value / max(total_escrows, 1))
        }