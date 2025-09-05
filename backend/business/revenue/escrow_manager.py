"""Escrow Manager - IA Influencer Agent Platform
============================================

Advanced escrow management system for secure collaborative payments
and multi-party transactions with automated release conditions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class EscrowStatus(Enum):
    """Escrow transaction status."""
    CREATED = "created"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ReleaseCondition(Enum):
    """Escrow release conditions."""
    MANUAL_APPROVAL = "manual_approval"
    AUTOMATIC_TIME = "automatic_time"
    MILESTONE_COMPLETION = "milestone_completion"
    APPROVAL_THRESHOLD = "approval_threshold"
    DELIVERABLE_VERIFICATION = "deliverable_verification"


@dataclass
class EscrowParty:
    """Party involved in escrow transaction."""
    party_id: str
    party_type: str  # payer, payee, arbiter
    wallet_address: str
    approval_required: bool = True


@dataclass
class EscrowMilestone:
    """Escrow milestone definition."""
    milestone_id: str
    description: str
    amount: Decimal
    due_date: Optional[datetime]
    completion_criteria: Dict[str, Any]
    status: str = "pending"
    completed_at: Optional[datetime] = None


@dataclass
class EscrowTransaction:
    """Escrow transaction record."""
    escrow_id: str
    parties: List[EscrowParty]
    total_amount: Decimal
    currency: str
    release_conditions: List[ReleaseCondition]
    milestones: List[EscrowMilestone]
    status: EscrowStatus
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]


class EscrowManager:
    """Advanced escrow management system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize escrow manager."""
        self.config = config or {}
        self.active_escrows: Dict[str, EscrowTransaction] = {}
        self.escrow_history: List[EscrowTransaction] = []
        self.dispute_resolution_queue: List[str] = []
        
    async def create_escrow(
        self,
        escrow_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new escrow transaction."""
        try:
            # Validate escrow request
            validated_request = await self._validate_escrow_request(escrow_request)
            
            # Create parties
            parties = await self._create_escrow_parties(validated_request['parties'])
            
            # Create milestones
            milestones = await self._create_milestones(validated_request.get('milestones', []))
            
            # Determine release conditions
            release_conditions = await self._determine_release_conditions(validated_request)
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(
                days=validated_request.get('duration_days', 30)
            )
            
            # Create escrow transaction
            escrow = EscrowTransaction(
                escrow_id=str(uuid.uuid4()),
                parties=parties,
                total_amount=Decimal(str(validated_request['amount'])),
                currency=validated_request.get('currency', 'USD'),
                release_conditions=release_conditions,
                milestones=milestones,
                status=EscrowStatus.CREATED,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                metadata=validated_request.get('metadata', {})
            )
            
            # Store escrow
            self.active_escrows[escrow.escrow_id] = escrow
            
            # Generate funding instructions
            funding_instructions = await self._generate_funding_instructions(escrow)
            
            return {
                "escrow_id": escrow.escrow_id,
                "status": escrow.status.value,
                "total_amount": float(escrow.total_amount),
                "currency": escrow.currency,
                "parties": [
                    {
                        "party_id": party.party_id,
                        "party_type": party.party_type,
                        "approval_required": party.approval_required
                    }
                    for party in parties
                ],
                "milestones": len(milestones),
                "expires_at": expires_at.isoformat(),
                "funding_instructions": funding_instructions
            }
            
        except Exception as e:
            logger.error(f"Escrow creation failed: {e}")
            raise
    
    async def manage_escrow_lifecycle(
        self,
        escrow_id: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage escrow transaction lifecycle."""
        try:
            escrow = self.active_escrows.get(escrow_id)
            if not escrow:
                raise ValueError(f"Escrow {escrow_id} not found")
            
            if action == "fund":
                return await self._fund_escrow(escrow, parameters)
            elif action == "approve_milestone":
                return await self._approve_milestone(escrow, parameters)
            elif action == "submit_deliverable":
                return await self._submit_deliverable(escrow, parameters)
            elif action == "request_release":
                return await self._request_release(escrow, parameters)
            elif action == "dispute":
                return await self._initiate_dispute(escrow, parameters)
            elif action == "cancel":
                return await self._cancel_escrow(escrow, parameters)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Escrow lifecycle management failed: {e}")
            raise
    
    async def process_automatic_releases(self) -> Dict[str, Any]:
        """Process automatic escrow releases based on conditions."""
        try:
            releases_processed = []
            current_time = datetime.utcnow()
            
            for escrow_id, escrow in self.active_escrows.items():
                if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.IN_PROGRESS]:
                    continue
                
                # Check for automatic release conditions
                release_eligible = await self._check_automatic_release_conditions(
                    escrow, current_time
                )
                
                if release_eligible:
                    release_result = await self._execute_automatic_release(escrow)
                    releases_processed.append(release_result)
            
            return {
                "processed_at": current_time.isoformat(),
                "releases_processed": len(releases_processed),
                "release_details": releases_processed,
                "summary": await self._generate_release_summary(releases_processed)
            }
            
        except Exception as e:
            logger.error(f"Automatic release processing failed: {e}")
            raise
    
    async def resolve_dispute(
        self,
        escrow_id: str,
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve escrow dispute with arbitration decision."""
        try:
            escrow = self.active_escrows.get(escrow_id)
            if not escrow:
                raise ValueError(f"Escrow {escrow_id} not found")
            
            if escrow.status != EscrowStatus.DISPUTED:
                raise ValueError(f"Escrow {escrow_id} is not in disputed status")
            
            # Validate resolution
            validated_resolution = await self._validate_dispute_resolution(resolution)
            
            # Execute resolution
            resolution_result = await self._execute_dispute_resolution(
                escrow, validated_resolution
            )
            
            # Update escrow status
            if resolution_result['action'] == 'release':
                escrow.status = EscrowStatus.COMPLETED
            elif resolution_result['action'] == 'cancel':
                escrow.status = EscrowStatus.CANCELLED
            
            # Remove from dispute queue
            if escrow_id in self.dispute_resolution_queue:
                self.dispute_resolution_queue.remove(escrow_id)
            
            # Record resolution
            escrow.metadata['dispute_resolution'] = {
                'resolved_at': datetime.utcnow().isoformat(),
                'resolution': validated_resolution,
                'result': resolution_result
            }
            
            return {
                "escrow_id": escrow_id,
                "resolution_action": resolution_result['action'],
                "resolution_details": resolution_result,
                "new_status": escrow.status.value,
                "resolved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dispute resolution failed: {e}")
            raise
    
    async def analyze_escrow_performance(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze escrow transaction performance and metrics."""
        try:
            # Get relevant escrows
            relevant_escrows = await self._get_escrows_in_period(start_date, end_date)
            
            # Calculate completion metrics
            completion_metrics = await self._calculate_completion_metrics(relevant_escrows)
            
            # Analyze dispute patterns
            dispute_analysis = await self._analyze_dispute_patterns(relevant_escrows)
            
            # Calculate financial metrics
            financial_metrics = await self._calculate_financial_metrics(relevant_escrows)
            
            # Analyze performance by type
            performance_by_type = await self._analyze_performance_by_type(relevant_escrows)
            
            return {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "completion_metrics": completion_metrics,
                "dispute_analysis": dispute_analysis,
                "financial_metrics": financial_metrics,
                "performance_by_type": performance_by_type,
                "recommendations": await self._generate_escrow_recommendations(
                    completion_metrics, dispute_analysis, financial_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"Escrow performance analysis failed: {e}")
            raise
    
    async def _validate_escrow_request(
        self,
        escrow_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate escrow creation request."""
        required_fields = ['amount', 'parties']
        
        for field in required_fields:
            if field not in escrow_request:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate amount
        amount = Decimal(str(escrow_request['amount']))
        if amount <= 0:
            raise ValueError("Escrow amount must be positive")
        
        # Validate parties
        parties = escrow_request['parties']
        if len(parties) < 2:
            raise ValueError("At least 2 parties required for escrow")
        
        # Check for required party types
        party_types = [party.get('party_type') for party in parties]
        if 'payer' not in party_types or 'payee' not in party_types:
            raise ValueError("Both payer and payee parties required")
        
        return escrow_request
    
    async def _create_escrow_parties(
        self,
        parties_data: List[Dict[str, Any]]
    ) -> List[EscrowParty]:
        """Create escrow party objects."""
        parties = []
        
        for party_data in parties_data:
            party = EscrowParty(
                party_id=party_data['party_id'],
                party_type=party_data['party_type'],
                wallet_address=party_data.get('wallet_address', ''),
                approval_required=party_data.get('approval_required', True)
            )
            parties.append(party)
        
        return parties
    
    async def _create_milestones(
        self,
        milestones_data: List[Dict[str, Any]]
    ) -> List[EscrowMilestone]:
        """Create escrow milestone objects."""
        milestones = []
        
        for milestone_data in milestones_data:
            due_date = None
            if milestone_data.get('due_date'):
                due_date = datetime.fromisoformat(milestone_data['due_date'])
            
            milestone = EscrowMilestone(
                milestone_id=str(uuid.uuid4()),
                description=milestone_data['description'],
                amount=Decimal(str(milestone_data['amount'])),
                due_date=due_date,
                completion_criteria=milestone_data.get('completion_criteria', {}),
                status="pending"
            )
            milestones.append(milestone)
        
        return milestones
    
    async def _determine_release_conditions(
        self,
        escrow_request: Dict[str, Any]
    ) -> List[ReleaseCondition]:
        """Determine appropriate release conditions."""
        conditions = []
        
        # Check request for specific conditions
        if 'release_conditions' in escrow_request:
            for condition_str in escrow_request['release_conditions']:
                try:
                    condition = ReleaseCondition(condition_str)
                    conditions.append(condition)
                except ValueError:
                    logger.warning(f"Unknown release condition: {condition_str}")
        
        # Default conditions if none specified
        if not conditions:
            if escrow_request.get('milestones'):
                conditions.append(ReleaseCondition.MILESTONE_COMPLETION)
            else:
                conditions.append(ReleaseCondition.MANUAL_APPROVAL)
        
        return conditions
    
    async def _generate_funding_instructions(
        self,
        escrow: EscrowTransaction
    ) -> Dict[str, Any]:
        """Generate funding instructions for escrow."""
        # Find payer party
        payer = next((p for p in escrow.parties if p.party_type == 'payer'), None)
        if not payer:
            raise ValueError("No payer party found in escrow")
        
        instructions = {
            "funding_address": f"escrow_{escrow.escrow_id}@ainflue.com",
            "amount": float(escrow.total_amount),
            "currency": escrow.currency,
            "reference": escrow.escrow_id,
            "deadline": escrow.expires_at.isoformat(),
            "instructions": [
                f"Transfer {escrow.total_amount} {escrow.currency} to the escrow account",
                f"Include reference: {escrow.escrow_id}",
                "Funds will be held securely until release conditions are met",
                "Contact support if you need assistance with funding"
            ]
        }
        
        return instructions
    
    async def _fund_escrow(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fund escrow transaction."""
        if escrow.status != EscrowStatus.CREATED:
            raise ValueError(f"Escrow must be in CREATED status to fund (current: {escrow.status.value})")
        
        # Validate funding
        funded_amount = Decimal(str(parameters.get('amount', 0)))
        if funded_amount != escrow.total_amount:
            raise ValueError(f"Funded amount {funded_amount} does not match escrow amount {escrow.total_amount}")
        
        # Update escrow status
        escrow.status = EscrowStatus.FUNDED
        escrow.metadata['funded_at'] = datetime.utcnow().isoformat()
        escrow.metadata['funding_transaction'] = parameters.get('transaction_id')
        
        # Start milestone tracking if applicable
        if escrow.milestones:
            escrow.status = EscrowStatus.IN_PROGRESS
        
        return {
            "escrow_id": escrow.escrow_id,
            "status": escrow.status.value,
            "funded_amount": float(funded_amount),
            "funded_at": escrow.metadata['funded_at'],
            "next_steps": await self._get_next_steps(escrow)
        }
    
    async def _approve_milestone(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Approve milestone completion."""
        milestone_id = parameters.get('milestone_id')
        approver_id = parameters.get('approver_id')
        
        # Find milestone
        milestone = next(
            (m for m in escrow.milestones if m.milestone_id == milestone_id),
            None
        )
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        if milestone.status == "completed":
            raise ValueError(f"Milestone {milestone_id} already completed")
        
        # Validate approver
        approver = next(
            (p for p in escrow.parties if p.party_id == approver_id and p.approval_required),
            None
        )
        
        if not approver:
            raise ValueError(f"Approver {approver_id} not authorized")
        
        # Mark milestone as completed
        milestone.status = "completed"
        milestone.completed_at = datetime.utcnow()
        
        # Check if all milestones completed
        all_completed = all(m.status == "completed" for m in escrow.milestones)
        
        if all_completed:
            release_result = await self._execute_release(escrow, "milestone_completion")
            return {
                "milestone_id": milestone_id,
                "status": "completed",
                "escrow_released": True,
                "release_details": release_result
            }
        
        return {
            "milestone_id": milestone_id,
            "status": "completed",
            "completed_at": milestone.completed_at.isoformat(),
            "remaining_milestones": len([m for m in escrow.milestones if m.status != "completed"])
        }
    
    async def _submit_deliverable(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit deliverable for escrow."""
        deliverable_data = parameters.get('deliverable')
        submitter_id = parameters.get('submitter_id')
        
        # Validate submitter
        submitter = next(
            (p for p in escrow.parties if p.party_id == submitter_id),
            None
        )
        
        if not submitter:
            raise ValueError(f"Submitter {submitter_id} not authorized")
        
        # Store deliverable
        if 'deliverables' not in escrow.metadata:
            escrow.metadata['deliverables'] = []
        
        deliverable_record = {
            'deliverable_id': str(uuid.uuid4()),
            'submitter_id': submitter_id,
            'submitted_at': datetime.utcnow().isoformat(),
            'data': deliverable_data,
            'status': 'pending_review'
        }
        
        escrow.metadata['deliverables'].append(deliverable_record)
        
        # Check for automatic verification
        if ReleaseCondition.DELIVERABLE_VERIFICATION in escrow.release_conditions:
            verification_result = await self._verify_deliverable(deliverable_record)
            if verification_result['verified']:
                release_result = await self._execute_release(escrow, "deliverable_verified")
                return {
                    "deliverable_id": deliverable_record['deliverable_id'],
                    "status": "verified",
                    "escrow_released": True,
                    "release_details": release_result
                }
        
        return {
            "deliverable_id": deliverable_record['deliverable_id'],
            "status": "submitted",
            "submitted_at": deliverable_record['submitted_at'],
            "pending_review": True
        }
    
    async def _request_release(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request escrow release."""
        requester_id = parameters.get('requester_id')
        
        # Validate requester
        requester = next(
            (p for p in escrow.parties if p.party_id == requester_id),
            None
        )
        
        if not requester:
            raise ValueError(f"Requester {requester_id} not authorized")
        
        # Check release conditions
        can_release = await self._check_release_eligibility(escrow)
        
        if can_release:
            release_result = await self._execute_release(escrow, "manual_approval")
            return {
                "release_approved": True,
                "release_details": release_result
            }
        else:
            # Store release request for approval
            if 'release_requests' not in escrow.metadata:
                escrow.metadata['release_requests'] = []
            
            request_record = {
                'request_id': str(uuid.uuid4()),
                'requester_id': requester_id,
                'requested_at': datetime.utcnow().isoformat(),
                'status': 'pending_approval'
            }
            
            escrow.metadata['release_requests'].append(request_record)
            
            return {
                "release_approved": False,
                "request_id": request_record['request_id'],
                "status": "pending_approval",
                "required_approvals": await self._get_required_approvals(escrow)
            }
    
    async def _initiate_dispute(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate escrow dispute."""
        disputer_id = parameters.get('disputer_id')
        dispute_reason = parameters.get('reason', 'Unspecified')
        
        # Validate disputer
        disputer = next(
            (p for p in escrow.parties if p.party_id == disputer_id),
            None
        )
        
        if not disputer:
            raise ValueError(f"Disputer {disputer_id} not authorized")
        
        if escrow.status == EscrowStatus.DISPUTED:
            raise ValueError("Escrow is already in dispute")
        
        # Update escrow status
        escrow.status = EscrowStatus.DISPUTED
        
        # Record dispute
        dispute_record = {
            'dispute_id': str(uuid.uuid4()),
            'disputer_id': disputer_id,
            'initiated_at': datetime.utcnow().isoformat(),
            'reason': dispute_reason,
            'evidence': parameters.get('evidence', []),
            'status': 'open'
        }
        
        escrow.metadata['dispute'] = dispute_record
        
        # Add to dispute resolution queue
        self.dispute_resolution_queue.append(escrow.escrow_id)
        
        return {
            "dispute_id": dispute_record['dispute_id'],
            "status": "initiated",
            "escrow_status": escrow.status.value,
            "initiated_at": dispute_record['initiated_at'],
            "resolution_process": "Dispute has been escalated to arbitration"
        }
    
    async def _cancel_escrow(
        self,
        escrow: EscrowTransaction,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cancel escrow transaction."""
        canceller_id = parameters.get('canceller_id')
        
        # Validate cancellation eligibility
        if escrow.status not in [EscrowStatus.CREATED, EscrowStatus.FUNDED]:
            raise ValueError(f"Cannot cancel escrow in {escrow.status.value} status")
        
        # Check if mutual consent required
        if escrow.status == EscrowStatus.FUNDED:
            # Require consent from all parties
            consent_required = [p.party_id for p in escrow.parties if p.approval_required]
            provided_consent = parameters.get('consent_from', [])
            
            if not all(party_id in provided_consent for party_id in consent_required):
                raise ValueError("Mutual consent required for cancellation")
        
        # Update escrow status
        escrow.status = EscrowStatus.CANCELLED
        
        # Record cancellation
        cancellation_record = {
            'cancelled_by': canceller_id,
            'cancelled_at': datetime.utcnow().isoformat(),
            'reason': parameters.get('reason', 'User requested'),
            'refund_processed': escrow.status == EscrowStatus.FUNDED
        }
        
        escrow.metadata['cancellation'] = cancellation_record
        
        return {
            "escrow_id": escrow.escrow_id,
            "status": "cancelled",
            "cancelled_at": cancellation_record['cancelled_at'],
            "refund_processed": cancellation_record['refund_processed']
        }
    
    async def _check_automatic_release_conditions(
        self,
        escrow: EscrowTransaction,
        current_time: datetime
    ) -> bool:
        """Check if escrow meets automatic release conditions."""
        for condition in escrow.release_conditions:
            if condition == ReleaseCondition.AUTOMATIC_TIME:
                # Check if enough time has passed
                time_threshold = escrow.created_at + timedelta(
                    days=escrow.metadata.get('auto_release_days', 7)
                )
                if current_time >= time_threshold:
                    return True
            
            elif condition == ReleaseCondition.MILESTONE_COMPLETION:
                # Check if all milestones completed
                if escrow.milestones and all(m.status == "completed" for m in escrow.milestones):
                    return True
        
        return False
    
    async def _execute_automatic_release(
        self,
        escrow: EscrowTransaction
    ) -> Dict[str, Any]:
        """Execute automatic escrow release."""
        return await self._execute_release(escrow, "automatic")
    
    async def _execute_release(
        self,
        escrow: EscrowTransaction,
        release_type: str
    ) -> Dict[str, Any]:
        """Execute escrow release to payee."""
        # Find payee
        payee = next((p for p in escrow.parties if p.party_type == 'payee'), None)
        if not payee:
            raise ValueError("No payee party found")
        
        # Update escrow status
        escrow.status = EscrowStatus.COMPLETED
        
        # Record release
        release_record = {
            'released_at': datetime.utcnow().isoformat(),
            'release_type': release_type,
            'released_to': payee.party_id,
            'amount': float(escrow.total_amount),
            'transaction_id': str(uuid.uuid4())
        }
        
        escrow.metadata['release'] = release_record
        
        # Move to history
        self.escrow_history.append(escrow)
        if escrow.escrow_id in self.active_escrows:
            del self.active_escrows[escrow.escrow_id]
        
        return release_record
    
    async def _get_next_steps(self, escrow: EscrowTransaction) -> List[str]:
        """Get next steps for escrow transaction."""
        steps = []
        
        if escrow.status == EscrowStatus.FUNDED:
            if escrow.milestones:
                steps.append("Complete milestones and request approval")
            else:
                steps.append("Submit deliverables or request release")
        elif escrow.status == EscrowStatus.IN_PROGRESS:
            pending_milestones = [m for m in escrow.milestones if m.status != "completed"]
            if pending_milestones:
                steps.append(f"Complete {len(pending_milestones)} remaining milestones")
        
        return steps
    
    async def _verify_deliverable(self, deliverable_record: Dict[str, Any]) -> Dict[str, Any]:
        """Verify submitted deliverable."""
        # Simplified verification logic
        verification_result = {
            'verified': True,  # Assume verified for demo
            'verification_score': 0.95,
            'verification_details': 'Deliverable meets all requirements'
        }
        
        deliverable_record['verification'] = verification_result
        deliverable_record['status'] = 'verified' if verification_result['verified'] else 'rejected'
        
        return verification_result
    
    async def _check_release_eligibility(self, escrow: EscrowTransaction) -> bool:
        """Check if escrow is eligible for release."""
        # Check basic eligibility
        if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.IN_PROGRESS]:
            return False
        
        # Check specific release conditions
        for condition in escrow.release_conditions:
            if condition == ReleaseCondition.MILESTONE_COMPLETION:
                if not all(m.status == "completed" for m in escrow.milestones):
                    return False
            elif condition == ReleaseCondition.DELIVERABLE_VERIFICATION:
                deliverables = escrow.metadata.get('deliverables', [])
                if not any(d.get('status') == 'verified' for d in deliverables):
                    return False
        
        return True
    
    async def _get_required_approvals(self, escrow: EscrowTransaction) -> List[str]:
        """Get list of required approvals for release."""
        approvals = []
        
        for party in escrow.parties:
            if party.approval_required and party.party_type != 'payee':
                approvals.append(party.party_id)
        
        return approvals
    
    async def _validate_dispute_resolution(
        self,
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate dispute resolution."""
        required_fields = ['action', 'reasoning']
        
        for field in required_fields:
            if field not in resolution:
                raise ValueError(f"Missing required field: {field}")
        
        valid_actions = ['release', 'cancel', 'partial_release']
        if resolution['action'] not in valid_actions:
            raise ValueError(f"Invalid resolution action: {resolution['action']}")
        
        return resolution
    
    async def _execute_dispute_resolution(
        self,
        escrow: EscrowTransaction,
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute dispute resolution decision."""
        action = resolution['action']
        
        if action == 'release':
            return await self._execute_release(escrow, "dispute_resolution")
        elif action == 'cancel':
            return await self._execute_cancellation_with_refund(escrow)
        elif action == 'partial_release':
            return await self._execute_partial_release(escrow, resolution)
        
        raise ValueError(f"Unknown resolution action: {action}")
    
    async def _execute_cancellation_with_refund(self, escrow: EscrowTransaction) -> Dict[str, Any]:
        """Execute escrow cancellation with refund."""
        # Find payer for refund
        payer = next((p for p in escrow.parties if p.party_type == 'payer'), None)
        
        return {
            'action': 'cancel',
            'refunded_to': payer.party_id if payer else 'unknown',
            'refund_amount': float(escrow.total_amount),
            'transaction_id': str(uuid.uuid4())
        }
    
    async def _execute_partial_release(
        self,
        escrow: EscrowTransaction,
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute partial release resolution."""
        release_percentage = resolution.get('release_percentage', 0.5)
        release_amount = escrow.total_amount * Decimal(str(release_percentage))
        refund_amount = escrow.total_amount - release_amount
        
        payee = next((p for p in escrow.parties if p.party_type == 'payee'), None)
        payer = next((p for p in escrow.parties if p.party_type == 'payer'), None)
        
        return {
            'action': 'partial_release',
            'released_to': payee.party_id if payee else 'unknown',
            'release_amount': float(release_amount),
            'refunded_to': payer.party_id if payer else 'unknown',
            'refund_amount': float(refund_amount),
            'transaction_id': str(uuid.uuid4())
        }
    
    async def _get_escrows_in_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[EscrowTransaction]:
        """Get escrow transactions in specified period."""
        relevant_escrows = []
        
        # Check active escrows
        for escrow in self.active_escrows.values():
            if start_date <= escrow.created_at <= end_date:
                relevant_escrows.append(escrow)
        
        # Check historical escrows
        for escrow in self.escrow_history:
            if start_date <= escrow.created_at <= end_date:
                relevant_escrows.append(escrow)
        
        return relevant_escrows
    
    async def _calculate_completion_metrics(
        self,
        escrows: List[EscrowTransaction]
    ) -> Dict[str, Any]:
        """Calculate escrow completion metrics."""
        if not escrows:
            return {}
        
        total_escrows = len(escrows)
        completed_escrows = len([e for e in escrows if e.status == EscrowStatus.COMPLETED])
        disputed_escrows = len([e for e in escrows if e.status == EscrowStatus.DISPUTED])
        cancelled_escrows = len([e for e in escrows if e.status == EscrowStatus.CANCELLED])
        
        completion_rate = completed_escrows / total_escrows if total_escrows > 0 else 0
        dispute_rate = disputed_escrows / total_escrows if total_escrows > 0 else 0
        cancellation_rate = cancelled_escrows / total_escrows if total_escrows > 0 else 0
        
        return {
            "total_escrows": total_escrows,
            "completed_escrows": completed_escrows,
            "disputed_escrows": disputed_escrows,
            "cancelled_escrows": cancelled_escrows,
            "completion_rate": completion_rate,
            "dispute_rate": dispute_rate,
            "cancellation_rate": cancellation_rate
        }
    
    async def _analyze_dispute_patterns(
        self,
        escrows: List[EscrowTransaction]
    ) -> Dict[str, Any]:
        """Analyze dispute patterns in escrow transactions."""
        disputed_escrows = [e for e in escrows if e.status == EscrowStatus.DISPUTED]
        
        if not disputed_escrows:
            return {"dispute_count": 0}
        
        # Analyze dispute reasons
        dispute_reasons = {}
        for escrow in disputed_escrows:
            dispute = escrow.metadata.get('dispute', {})
            reason = dispute.get('reason', 'unknown')
            dispute_reasons[reason] = dispute_reasons.get(reason, 0) + 1
        
        return {
            "dispute_count": len(disputed_escrows),
            "dispute_reasons": dispute_reasons,
            "common_dispute_reason": max(dispute_reasons, key=dispute_reasons.get) if dispute_reasons else None
        }
    
    async def _calculate_financial_metrics(
        self,
        escrows: List[EscrowTransaction]
    ) -> Dict[str, Any]:
        """Calculate financial metrics for escrow transactions."""
        if not escrows:
            return {}
        
        total_value = sum(float(e.total_amount) for e in escrows)
        completed_value = sum(
            float(e.total_amount) for e in escrows
            if e.status == EscrowStatus.COMPLETED
        )
        
        avg_escrow_value = total_value / len(escrows)
        
        return {
            "total_escrow_value": total_value,
            "completed_escrow_value": completed_value,
            "average_escrow_value": avg_escrow_value,
            "value_completion_rate": completed_value / total_value if total_value > 0 else 0
        }
    
    async def _analyze_performance_by_type(
        self,
        escrows: List[EscrowTransaction]
    ) -> Dict[str, Any]:
        """Analyze escrow performance by transaction type."""
        # Categorize by milestones
        milestone_escrows = [e for e in escrows if e.milestones]
        simple_escrows = [e for e in escrows if not e.milestones]
        
        performance = {}
        
        if milestone_escrows:
            milestone_completed = len([e for e in milestone_escrows if e.status == EscrowStatus.COMPLETED])
            performance["milestone_based"] = {
                "total": len(milestone_escrows),
                "completed": milestone_completed,
                "completion_rate": milestone_completed / len(milestone_escrows)
            }
        
        if simple_escrows:
            simple_completed = len([e for e in simple_escrows if e.status == EscrowStatus.COMPLETED])
            performance["simple_escrows"] = {
                "total": len(simple_escrows),
                "completed": simple_completed,
                "completion_rate": simple_completed / len(simple_escrows)
            }
        
        return performance
    
    async def _generate_escrow_recommendations(
        self,
        completion_metrics: Dict[str, Any],
        dispute_analysis: Dict[str, Any],
        financial_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate escrow optimization recommendations."""
        recommendations = []
        
        # Completion rate recommendations
        completion_rate = completion_metrics.get("completion_rate", 0)
        if completion_rate < 0.8:
            recommendations.append("Low completion rate - review escrow terms and conditions")
        
        # Dispute rate recommendations
        dispute_rate = completion_metrics.get("dispute_rate", 0)
        if dispute_rate > 0.1:
            recommendations.append("High dispute rate - improve project scoping and communication")
        
        # Value recommendations
        avg_value = financial_metrics.get("average_escrow_value", 0)
        if avg_value < 100:
            recommendations.append("Low average escrow value - consider minimum transaction limits")
        
        # Common dispute recommendations
        common_dispute = dispute_analysis.get("common_dispute_reason")
        if common_dispute:
            recommendations.append(f"Address common dispute reason: {common_dispute}")
        
        # General recommendations
        recommendations.extend([
            "Implement milestone-based escrows for better success rates",
            "Provide clear project templates and guidelines",
            "Offer mediation services before formal disputes"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _generate_release_summary(
        self,
        releases_processed: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of processed releases."""
        if not releases_processed:
            return {"total_releases": 0}
        
        total_amount = sum(float(release.get('amount', 0)) for release in releases_processed)
        
        return {
            "total_releases": len(releases_processed),
            "total_amount_released": total_amount,
            "release_types": list(set(release.get('release_type') for release in releases_processed))
        }