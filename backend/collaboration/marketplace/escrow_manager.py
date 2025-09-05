"""Escrow Manager Module - Secure Transaction Management for Creator Marketplace
==============================================================================

Advanced escrow system providing secure payment holding, milestone-based releases,
dispute resolution, and automated transaction management for creator collaborations.

This module implements:
- Multi-party escrow with milestone releases
- Smart contract integration for automated payments
- Dispute resolution and arbitration workflows
- Payment security and fraud protection
- Multi-currency and multi-payment method support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json

logger = logging.getLogger(__name__)


class EscrowStatus(Enum):
    """Escrow transaction status"""
    CREATED = "created"
    FUNDED = "funded"
    ACTIVE = "active"
    DISPUTED = "disputed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class MilestoneStatus(Enum):
    """Individual milestone status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"
    DISPUTED = "disputed"


class DisputeStatus(Enum):
    """Dispute resolution status"""
    CREATED = "created"
    UNDER_REVIEW = "under_review"
    ARBITRATION = "arbitration"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    PLATFORM_CREDITS = "platform_credits"


@dataclass
class EscrowParty:
    """Party in an escrow transaction"""
    party_id: str
    role: str  # "buyer", "seller", "arbitrator", "platform"
    name: str
    email: str
    wallet_address: Optional[str] = None
    payment_methods: List[PaymentMethod] = field(default_factory=list)
    verification_status: str = "unverified"  # "verified", "pending", "unverified"


@dataclass
class Milestone:
    """Individual milestone in escrow"""
    milestone_id: str
    title: str
    description: str
    amount: Decimal
    currency: str
    status: MilestoneStatus
    due_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    released_date: Optional[datetime] = None
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    approval_criteria: List[str] = field(default_factory=list)
    reviewer_notes: str = ""
    creator_notes: str = ""


@dataclass
class PaymentInfo:
    """Payment information for escrow"""
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    fees: Decimal = Decimal('0')
    exchange_rate: Decimal = Decimal('1')
    payment_processor: Optional[str] = None
    payment_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DisputeCase:
    """Dispute case information"""
    dispute_id: str
    escrow_id: str
    raised_by: str
    dispute_type: str
    description: str
    status: DisputeStatus
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    arbitrator_id: Optional[str] = None
    resolution: Optional[str] = None
    resolution_date: Optional[datetime] = None
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EscrowTransaction:
    """Complete escrow transaction"""
    escrow_id: str
    project_id: str
    buyer: EscrowParty
    seller: EscrowParty
    arbitrator: Optional[EscrowParty] = None
    total_amount: Decimal = Decimal('0')
    currency: str = "USD"
    status: EscrowStatus = EscrowStatus.CREATED
    milestones: List[Milestone] = field(default_factory=list)
    payment_info: Optional[PaymentInfo] = None
    fees: Dict[str, Decimal] = field(default_factory=dict)
    dispute: Optional[DisputeCase] = None
    terms_hash: Optional[str] = None
    smart_contract_address: Optional[str] = None
    auto_release_enabled: bool = True
    auto_release_days: int = 7
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscrowResult:
    """Result of escrow operation"""
    success: bool
    escrow_id: str
    message: str
    transaction_details: Optional[Dict[str, Any]] = None
    next_steps: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class EscrowManager:
    """Advanced escrow management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the escrow manager"""
        self.config = config or {}
        self.escrow_transactions: Dict[str, EscrowTransaction] = {}
        self.dispute_cases: Dict[str, DisputeCase] = {}
        self.payment_processors = {}
        self.smart_contracts = {}
        
        # Configuration
        self.platform_fee_rate = Decimal(self.config.get('platform_fee_rate', '0.025'))  # 2.5%
        self.arbitration_fee_rate = Decimal(self.config.get('arbitration_fee_rate', '0.01'))  # 1%
        self.auto_release_enabled = self.config.get('auto_release_enabled', True)
        self.dispute_timeout_days = self.config.get('dispute_timeout_days', 30)
        
        logger.info("🔒 Escrow Manager initialized")
    
    async def create_escrow(
        self,
        project_id: str,
        buyer: EscrowParty,
        seller: EscrowParty,
        milestones: List[Dict[str, Any]],
        currency: str = "USD",
        arbitrator: Optional[EscrowParty] = None
    ) -> EscrowResult:
        """Create a new escrow transaction"""
        try:
            escrow_id = str(uuid.uuid4())
            
            # Validate parties
            validation_result = await self._validate_parties(buyer, seller, arbitrator)
            if not validation_result["valid"]:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Party validation failed",
                    errors=validation_result["errors"]
                )
            
            # Create milestone objects
            milestone_objects = []
            total_amount = Decimal('0')
            
            for i, milestone_data in enumerate(milestones):
                milestone = Milestone(
                    milestone_id=str(uuid.uuid4()),
                    title=milestone_data['title'],
                    description=milestone_data['description'],
                    amount=Decimal(str(milestone_data['amount'])),
                    currency=currency,
                    status=MilestoneStatus.PENDING,
                    due_date=datetime.fromisoformat(milestone_data['due_date']) if milestone_data.get('due_date') else None,
                    deliverables=milestone_data.get('deliverables', []),
                    approval_criteria=milestone_data.get('approval_criteria', [])
                )
                milestone_objects.append(milestone)
                total_amount += milestone.amount
            
            # Calculate fees
            platform_fee = total_amount * self.platform_fee_rate
            arbitration_fee = total_amount * self.arbitration_fee_rate if arbitrator else Decimal('0')
            
            fees = {
                'platform_fee': platform_fee,
                'arbitration_fee': arbitration_fee,
                'total_fees': platform_fee + arbitration_fee
            }
            
            # Create escrow transaction
            escrow = EscrowTransaction(
                escrow_id=escrow_id,
                project_id=project_id,
                buyer=buyer,
                seller=seller,
                arbitrator=arbitrator,
                total_amount=total_amount,
                currency=currency,
                milestones=milestone_objects,
                fees=fees,
                expiry_date=datetime.now(timezone.utc) + timedelta(days=90)  # 90 day default expiry
            )
            
            # Generate terms hash for integrity
            escrow.terms_hash = await self._generate_terms_hash(escrow)
            
            # Store escrow
            self.escrow_transactions[escrow_id] = escrow
            
            # Initialize smart contract if enabled
            if self.config.get('smart_contracts_enabled', False):
                await self._initialize_smart_contract(escrow)
            
            logger.info(f"🔒 Escrow created: {escrow_id} for project {project_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Escrow created successfully",
                transaction_details={
                    'total_amount': float(total_amount),
                    'currency': currency,
                    'milestones_count': len(milestone_objects),
                    'platform_fee': float(platform_fee),
                    'arbitration_fee': float(arbitration_fee)
                },
                next_steps=[
                    "Fund escrow account",
                    "Begin milestone execution",
                    "Submit deliverables for approval"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating escrow: {e}")
            return EscrowResult(
                success=False,
                escrow_id="",
                message="Failed to create escrow",
                errors=[str(e)]
            )
    
    async def fund_escrow(
        self,
        escrow_id: str,
        payment_info: PaymentInfo
    ) -> EscrowResult:
        """Fund an escrow transaction"""
        try:
            escrow = self.escrow_transactions.get(escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Escrow not found"
                )
            
            if escrow.status != EscrowStatus.CREATED:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message=f"Cannot fund escrow in status: {escrow.status.value}"
                )
            
            # Validate payment amount
            required_amount = escrow.total_amount + escrow.fees['total_fees']
            if payment_info.amount < required_amount:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message=f"Insufficient payment amount. Required: {required_amount}, Provided: {payment_info.amount}"
                )
            
            # Process payment
            payment_result = await self._process_payment(payment_info)
            if not payment_result["success"]:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Payment processing failed",
                    errors=payment_result.get("errors", [])
                )
            
            # Update escrow
            escrow.payment_info = payment_info
            escrow.status = EscrowStatus.FUNDED
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Activate first milestone
            if escrow.milestones:
                escrow.milestones[0].status = MilestoneStatus.IN_PROGRESS
                escrow.status = EscrowStatus.ACTIVE
            
            # Update smart contract
            if escrow.smart_contract_address:
                await self._update_smart_contract(escrow, "funded")
            
            logger.info(f"🔒 Escrow funded: {escrow_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Escrow funded successfully",
                transaction_details={
                    'payment_id': payment_info.payment_id,
                    'amount_paid': float(payment_info.amount)
                },
                next_steps=[
                    "Begin work on first milestone",
                    "Submit deliverables when ready",
                    "Request milestone approval"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error funding escrow: {e}")
            return EscrowResult(
                success=False,
                escrow_id=escrow_id,
                message="Failed to fund escrow",
                errors=[str(e)]
            )
    
    async def submit_milestone(
        self,
        escrow_id: str,
        milestone_id: str,
        deliverables: List[Dict[str, Any]],
        creator_notes: str = ""
    ) -> EscrowResult:
        """Submit milestone deliverables for approval"""
        try:
            escrow = self.escrow_transactions.get(escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Escrow not found"
                )
            
            # Find milestone
            milestone = next((m for m in escrow.milestones if m.milestone_id == milestone_id), None)
            if not milestone:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Milestone not found"
                )
            
            if milestone.status != MilestoneStatus.IN_PROGRESS:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message=f"Milestone not in progress. Current status: {milestone.status.value}"
                )
            
            # Validate deliverables
            validation_result = await self._validate_deliverables(milestone, deliverables)
            if not validation_result["valid"]:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Deliverables validation failed",
                    errors=validation_result["errors"]
                )
            
            # Update milestone
            milestone.deliverables = deliverables
            milestone.creator_notes = creator_notes
            milestone.status = MilestoneStatus.SUBMITTED
            milestone.submitted_date = datetime.now(timezone.utc)
            
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Start auto-approval timer if enabled
            if escrow.auto_release_enabled:
                await self._schedule_auto_approval(escrow_id, milestone_id)
            
            # Notify buyer
            await self._notify_milestone_submitted(escrow, milestone)
            
            logger.info(f"🔒 Milestone submitted: {milestone_id} for escrow {escrow_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Milestone submitted successfully",
                next_steps=[
                    "Wait for buyer review",
                    "Respond to any feedback",
                    f"Auto-approval in {escrow.auto_release_days} days if no action"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error submitting milestone: {e}")
            return EscrowResult(
                success=False,
                escrow_id=escrow_id,
                message="Failed to submit milestone",
                errors=[str(e)]
            )
    
    async def approve_milestone(
        self,
        escrow_id: str,
        milestone_id: str,
        approver_id: str,
        reviewer_notes: str = ""
    ) -> EscrowResult:
        """Approve a submitted milestone"""
        try:
            escrow = self.escrow_transactions.get(escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Escrow not found"
                )
            
            # Verify approver authorization
            if approver_id != escrow.buyer.party_id:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Unauthorized: Only buyer can approve milestones"
                )
            
            # Find milestone
            milestone = next((m for m in escrow.milestones if m.milestone_id == milestone_id), None)
            if not milestone:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Milestone not found"
                )
            
            if milestone.status != MilestoneStatus.SUBMITTED:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message=f"Milestone not submitted. Current status: {milestone.status.value}"
                )
            
            # Approve milestone
            milestone.status = MilestoneStatus.APPROVED
            milestone.reviewer_notes = reviewer_notes
            milestone.approved_date = datetime.now(timezone.utc)
            
            # Release payment
            release_result = await self._release_milestone_payment(escrow, milestone)
            if release_result["success"]:
                milestone.status = MilestoneStatus.RELEASED
                milestone.released_date = datetime.now(timezone.utc)
            
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Check if all milestones are complete
            if all(m.status == MilestoneStatus.RELEASED for m in escrow.milestones):
                escrow.status = EscrowStatus.COMPLETED
                await self._notify_escrow_completed(escrow)
            else:
                # Activate next milestone
                await self._activate_next_milestone(escrow)
            
            # Update smart contract
            if escrow.smart_contract_address:
                await self._update_smart_contract(escrow, "milestone_approved", milestone_id)
            
            logger.info(f"🔒 Milestone approved and payment released: {milestone_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Milestone approved and payment released",
                transaction_details={
                    'milestone_id': milestone_id,
                    'amount_released': float(milestone.amount),
                    'release_details': release_result.get("details", {})
                },
                next_steps=await self._get_next_steps_after_approval(escrow)
            )
            
        except Exception as e:
            logger.error(f"❌ Error approving milestone: {e}")
            return EscrowResult(
                success=False,
                escrow_id=escrow_id,
                message="Failed to approve milestone",
                errors=[str(e)]
            )
    
    async def reject_milestone(
        self,
        escrow_id: str,
        milestone_id: str,
        rejector_id: str,
        reason: str,
        reviewer_notes: str = ""
    ) -> EscrowResult:
        """Reject a submitted milestone"""
        try:
            escrow = self.escrow_transactions.get(escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Escrow not found"
                )
            
            # Verify rejector authorization
            if rejector_id != escrow.buyer.party_id:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Unauthorized: Only buyer can reject milestones"
                )
            
            # Find milestone
            milestone = next((m for m in escrow.milestones if m.milestone_id == milestone_id), None)
            if not milestone:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Milestone not found"
                )
            
            if milestone.status != MilestoneStatus.SUBMITTED:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message=f"Milestone not submitted. Current status: {milestone.status.value}"
                )
            
            # Reject milestone
            milestone.status = MilestoneStatus.REJECTED
            milestone.reviewer_notes = reviewer_notes
            
            # Reset to in progress for rework
            milestone.status = MilestoneStatus.IN_PROGRESS
            milestone.submitted_date = None
            
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Notify seller
            await self._notify_milestone_rejected(escrow, milestone, reason)
            
            logger.info(f"🔒 Milestone rejected: {milestone_id} - {reason}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Milestone rejected",
                next_steps=[
                    "Review rejection feedback",
                    "Revise deliverables based on comments",
                    "Resubmit milestone when ready"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error rejecting milestone: {e}")
            return EscrowResult(
                success=False,
                escrow_id=escrow_id,
                message="Failed to reject milestone",
                errors=[str(e)]
            )
    
    async def raise_dispute(
        self,
        escrow_id: str,
        raised_by: str,
        dispute_type: str,
        description: str,
        evidence: List[Dict[str, Any]] = None
    ) -> EscrowResult:
        """Raise a dispute for an escrow transaction"""
        try:
            escrow = self.escrow_transactions.get(escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Escrow not found"
                )
            
            # Verify dispute raiser is a party
            if raised_by not in [escrow.buyer.party_id, escrow.seller.party_id]:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Unauthorized: Only transaction parties can raise disputes"
                )
            
            if escrow.dispute:
                return EscrowResult(
                    success=False,
                    escrow_id=escrow_id,
                    message="Dispute already exists for this escrow"
                )
            
            # Create dispute
            dispute_id = str(uuid.uuid4())
            dispute = DisputeCase(
                dispute_id=dispute_id,
                escrow_id=escrow_id,
                raised_by=raised_by,
                dispute_type=dispute_type,
                description=description,
                status=DisputeStatus.CREATED,
                evidence=evidence or []
            )
            
            # Assign arbitrator if available
            if escrow.arbitrator:
                dispute.arbitrator_id = escrow.arbitrator.party_id
                dispute.status = DisputeStatus.ARBITRATION
            else:
                dispute.status = DisputeStatus.UNDER_REVIEW
            
            # Update escrow
            escrow.dispute = dispute
            escrow.status = EscrowStatus.DISPUTED
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Store dispute
            self.dispute_cases[dispute_id] = dispute
            
            # Notify parties
            await self._notify_dispute_raised(escrow, dispute)
            
            logger.info(f"🔒 Dispute raised: {dispute_id} for escrow {escrow_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=escrow_id,
                message="Dispute raised successfully",
                transaction_details={
                    'dispute_id': dispute_id,
                    'dispute_type': dispute_type,
                    'arbitrator_assigned': dispute.arbitrator_id is not None
                },
                next_steps=[
                    "Wait for arbitrator assignment" if not dispute.arbitrator_id else "Arbitrator will review case",
                    "Provide additional evidence if needed",
                    "Participate in resolution process"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Error raising dispute: {e}")
            return EscrowResult(
                success=False,
                escrow_id=escrow_id,
                message="Failed to raise dispute",
                errors=[str(e)]
            )
    
    async def resolve_dispute(
        self,
        dispute_id: str,
        arbitrator_id: str,
        resolution: str,
        distribution: Dict[str, Decimal]
    ) -> EscrowResult:
        """Resolve a dispute with arbitrator decision"""
        try:
            dispute = self.dispute_cases.get(dispute_id)
            if not dispute:
                return EscrowResult(
                    success=False,
                    escrow_id="",
                    message="Dispute not found"
                )
            
            escrow = self.escrow_transactions.get(dispute.escrow_id)
            if not escrow:
                return EscrowResult(
                    success=False,
                    escrow_id=dispute.escrow_id,
                    message="Associated escrow not found"
                )
            
            # Verify arbitrator authorization
            if arbitrator_id != dispute.arbitrator_id:
                return EscrowResult(
                    success=False,
                    escrow_id=dispute.escrow_id,
                    message="Unauthorized: Only assigned arbitrator can resolve dispute"
                )
            
            # Validate distribution
            total_distributed = sum(distribution.values())
            available_amount = escrow.total_amount
            
            if total_distributed > available_amount:
                return EscrowResult(
                    success=False,
                    escrow_id=dispute.escrow_id,
                    message="Distribution exceeds available amount"
                )
            
            # Process resolution
            dispute.resolution = resolution
            dispute.status = DisputeStatus.RESOLVED
            dispute.resolution_date = datetime.now(timezone.utc)
            
            # Execute payment distribution
            distribution_result = await self._execute_dispute_distribution(escrow, distribution)
            if not distribution_result["success"]:
                return EscrowResult(
                    success=False,
                    escrow_id=dispute.escrow_id,
                    message="Failed to execute payment distribution",
                    errors=distribution_result.get("errors", [])
                )
            
            # Close escrow
            escrow.status = EscrowStatus.COMPLETED
            escrow.updated_date = datetime.now(timezone.utc)
            
            # Close dispute
            dispute.status = DisputeStatus.CLOSED
            
            # Notify parties
            await self._notify_dispute_resolved(escrow, dispute, distribution)
            
            logger.info(f"🔒 Dispute resolved: {dispute_id}")
            
            return EscrowResult(
                success=True,
                escrow_id=dispute.escrow_id,
                message="Dispute resolved and payments distributed",
                transaction_details={
                    'dispute_id': dispute_id,
                    'resolution': resolution,
                    'distribution': {k: float(v) for k, v in distribution.items()}
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error resolving dispute: {e}")
            return EscrowResult(
                success=False,
                escrow_id="",
                message="Failed to resolve dispute",
                errors=[str(e)]
            )
    
    # Helper methods
    async def _validate_parties(
        self,
        buyer: EscrowParty,
        seller: EscrowParty,
        arbitrator: Optional[EscrowParty]
    ) -> Dict[str, Any]:
        """Validate transaction parties"""
        errors = []
        
        # Check required fields
        for party in [buyer, seller]:
            if not party.party_id or not party.email:
                errors.append(f"Missing required information for {party.role}")
        
        # Check unique parties
        if buyer.party_id == seller.party_id:
            errors.append("Buyer and seller cannot be the same party")
        
        if arbitrator and arbitrator.party_id in [buyer.party_id, seller.party_id]:
            errors.append("Arbitrator cannot be buyer or seller")
        
        # Check verification status (optional, based on requirements)
        if self.config.get('require_verification', False):
            for party in [buyer, seller, arbitrator]:
                if party and party.verification_status != "verified":
                    errors.append(f"{party.role} must be verified")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _validate_deliverables(
        self,
        milestone: Milestone,
        deliverables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate milestone deliverables"""
        errors = []
        
        # Check if deliverables exist
        if not deliverables:
            errors.append("No deliverables provided")
            return {"valid": False, "errors": errors}
        
        # Validate each deliverable
        for i, deliverable in enumerate(deliverables):
            if not deliverable.get('title'):
                errors.append(f"Deliverable {i+1}: Missing title")
            
            if not deliverable.get('description'):
                errors.append(f"Deliverable {i+1}: Missing description")
            
            if not deliverable.get('file_url') and not deliverable.get('content'):
                errors.append(f"Deliverable {i+1}: Missing content or file")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _process_payment(self, payment_info: PaymentInfo) -> Dict[str, Any]:
        """Process payment through payment processor"""
        try:
            # This would integrate with actual payment processors
            # For now, simulate payment processing
            
            # Validate payment method
            if payment_info.payment_method not in [pm.value for pm in PaymentMethod]:
                return {
                    "success": False,
                    "errors": ["Unsupported payment method"]
                }
            
            # Simulate payment processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate transaction ID
            payment_info.transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
            payment_info.payment_id = f"pay_{uuid.uuid4().hex[:16]}"
            
            return {
                "success": True,
                "transaction_id": payment_info.transaction_id,
                "payment_id": payment_info.payment_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)]
            }
    
    async def _release_milestone_payment(
        self,
        escrow: EscrowTransaction,
        milestone: Milestone
    ) -> Dict[str, Any]:
        """Release payment for approved milestone"""
        try:
            # Calculate net payment (after fees)
            net_amount = milestone.amount
            
            # This would integrate with payment processor to transfer funds
            # For now, simulate payment release
            
            release_details = {
                "milestone_id": milestone.milestone_id,
                "gross_amount": float(milestone.amount),
                "net_amount": float(net_amount),
                "recipient": escrow.seller.party_id,
                "payment_method": escrow.payment_info.payment_method.value if escrow.payment_info else "platform_credits",
                "transaction_id": f"release_{uuid.uuid4().hex[:16]}",
                "release_date": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"💰 Payment released: {milestone.amount} for milestone {milestone.milestone_id}")
            
            return {
                "success": True,
                "details": release_details
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)]
            }
    
    async def _execute_dispute_distribution(
        self,
        escrow: EscrowTransaction,
        distribution: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """Execute payment distribution after dispute resolution"""
        try:
            distribution_details = []
            
            for party_id, amount in distribution.items():
                if amount > 0:
                    # Process payment to party
                    detail = {
                        "party_id": party_id,
                        "amount": float(amount),
                        "transaction_id": f"dispute_dist_{uuid.uuid4().hex[:16]}",
                        "processed_date": datetime.now(timezone.utc).isoformat()
                    }
                    distribution_details.append(detail)
            
            return {
                "success": True,
                "distribution_details": distribution_details
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)]
            }
    
    async def _generate_terms_hash(self, escrow: EscrowTransaction) -> str:
        """Generate hash of escrow terms for integrity verification"""
        terms_data = {
            "project_id": escrow.project_id,
            "buyer_id": escrow.buyer.party_id,
            "seller_id": escrow.seller.party_id,
            "total_amount": float(escrow.total_amount),
            "currency": escrow.currency,
            "milestones": [
                {
                    "title": m.title,
                    "amount": float(m.amount),
                    "description": m.description
                }
                for m in escrow.milestones
            ]
        }
        
        terms_json = json.dumps(terms_data, sort_keys=True)
        return hashlib.sha256(terms_json.encode()).hexdigest()
    
    async def _activate_next_milestone(self, escrow: EscrowTransaction) -> None:
        """Activate the next pending milestone"""
        for milestone in escrow.milestones:
            if milestone.status == MilestoneStatus.PENDING:
                milestone.status = MilestoneStatus.IN_PROGRESS
                await self._notify_milestone_activated(escrow, milestone)
                break
    
    async def _get_next_steps_after_approval(self, escrow: EscrowTransaction) -> List[str]:
        """Get next steps after milestone approval"""
        if escrow.status == EscrowStatus.COMPLETED:
            return [
                "All milestones completed",
                "Project finalization",
                "Final documentation"
            ]
        else:
            return [
                "Continue with next milestone",
                "Submit next deliverables",
                "Maintain project timeline"
            ]
    
    async def _schedule_auto_approval(self, escrow_id: str, milestone_id: str) -> None:
        """Schedule automatic approval if no action taken"""
        # In production, this would use a proper scheduler/queue system
        delay = self.escrow_transactions[escrow_id].auto_release_days * 24 * 3600  # Convert to seconds
        asyncio.create_task(self._auto_approve_milestone(escrow_id, milestone_id, delay))
    
    async def _auto_approve_milestone(self, escrow_id: str, milestone_id: str, delay: float) -> None:
        """Automatically approve milestone after delay"""
        await asyncio.sleep(delay)
        
        escrow = self.escrow_transactions.get(escrow_id)
        if not escrow:
            return
        
        milestone = next((m for m in escrow.milestones if m.milestone_id == milestone_id), None)
        if not milestone or milestone.status != MilestoneStatus.SUBMITTED:
            return
        
        # Auto-approve milestone
        await self.approve_milestone(
            escrow_id,
            milestone_id,
            "system",  # System approval
            "Auto-approved: No action taken within specified timeframe"
        )
        
        logger.info(f"🔒 Auto-approved milestone: {milestone_id}")
    
    # Smart contract integration methods
    async def _initialize_smart_contract(self, escrow: EscrowTransaction) -> None:
        """Initialize smart contract for escrow"""
        # This would deploy or reference a smart contract
        # For now, just simulate
        contract_address = f"0x{uuid.uuid4().hex[:40]}"
        escrow.smart_contract_address = contract_address
        
        logger.info(f"📋 Smart contract initialized: {contract_address}")
    
    async def _update_smart_contract(
        self,
        escrow: EscrowTransaction,
        action: str,
        milestone_id: Optional[str] = None
    ) -> None:
        """Update smart contract state"""
        # This would interact with actual smart contract
        logger.info(f"📋 Smart contract updated: {action} for {escrow.escrow_id}")
    
    # Notification methods
    async def _notify_milestone_submitted(self, escrow: EscrowTransaction, milestone: Milestone) -> None:
        """Notify buyer of milestone submission"""
        logger.info(f"📧 Milestone submitted notification sent for {milestone.milestone_id}")
    
    async def _notify_milestone_rejected(
        self,
        escrow: EscrowTransaction,
        milestone: Milestone,
        reason: str
    ) -> None:
        """Notify seller of milestone rejection"""
        logger.info(f"📧 Milestone rejection notification sent for {milestone.milestone_id}")
    
    async def _notify_milestone_activated(self, escrow: EscrowTransaction, milestone: Milestone) -> None:
        """Notify parties of milestone activation"""
        logger.info(f"📧 Milestone activation notification sent for {milestone.milestone_id}")
    
    async def _notify_escrow_completed(self, escrow: EscrowTransaction) -> None:
        """Notify parties of escrow completion"""
        logger.info(f"📧 Escrow completion notification sent for {escrow.escrow_id}")
    
    async def _notify_dispute_raised(self, escrow: EscrowTransaction, dispute: DisputeCase) -> None:
        """Notify parties of dispute"""
        logger.info(f"📧 Dispute notification sent for {dispute.dispute_id}")
    
    async def _notify_dispute_resolved(
        self,
        escrow: EscrowTransaction,
        dispute: DisputeCase,
        distribution: Dict[str, Decimal]
    ) -> None:
        """Notify parties of dispute resolution"""
        logger.info(f"📧 Dispute resolution notification sent for {dispute.dispute_id}")
    
    # Public query methods
    async def get_escrow(self, escrow_id: str) -> Optional[EscrowTransaction]:
        """Get escrow by ID"""
        return self.escrow_transactions.get(escrow_id)
    
    async def get_escrow_status(self, escrow_id: str) -> Optional[Dict[str, Any]]:
        """Get escrow status summary"""
        escrow = self.escrow_transactions.get(escrow_id)
        if not escrow:
            return None
        
        return {
            "escrow_id": escrow.escrow_id,
            "status": escrow.status.value,
            "total_amount": float(escrow.total_amount),
            "currency": escrow.currency,
            "milestones_total": len(escrow.milestones),
            "milestones_completed": len([m for m in escrow.milestones if m.status == MilestoneStatus.RELEASED]),
            "has_dispute": escrow.dispute is not None,
            "created_date": escrow.created_date.isoformat(),
            "updated_date": escrow.updated_date.isoformat()
        }


# Export main classes
__all__ = [
    'EscrowManager',
    'EscrowTransaction',
    'EscrowParty',
    'Milestone',
    'PaymentInfo',
    'DisputeCase',
    'EscrowResult',
    'EscrowStatus',
    'MilestoneStatus',
    'DisputeStatus',
    'PaymentMethod'
]