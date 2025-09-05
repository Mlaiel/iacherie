"""Time-Locked Payments Contract - IA-Influencer-Agent Platform

This module provides time-locked payment functionality for delayed releases,
vesting schedules, and milestone-based payments with precise timing control.

Features:
- Time-locked payment releases
- Vesting schedule management
- Milestone-based unlocking
- Early release mechanisms
- Payment streaming
- Cliff periods

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class LockType(Enum):
    """Types of time locks"""
    SINGLE_RELEASE = "single_release"
    VESTING_SCHEDULE = "vesting_schedule"
    MILESTONE_BASED = "milestone_based"
    STREAMING = "streaming"
    CLIFF_VESTING = "cliff_vesting"


class PaymentStatus(Enum):
    """Time-locked payment status"""
    LOCKED = "locked"
    PARTIALLY_UNLOCKED = "partially_unlocked"
    FULLY_UNLOCKED = "fully_unlocked"
    CANCELLED = "cancelled"
    EMERGENCY_RELEASED = "emergency_released"


@dataclass
class VestingSchedule:
    """Vesting schedule configuration"""
    total_amount: Decimal
    start_date: datetime
    cliff_period_days: int
    vesting_period_days: int
    release_frequency_days: int
    initial_unlock_percentage: Decimal


@dataclass
class TimeLockedPayment:
    """Time-locked payment record"""
    payment_id: str
    beneficiary_address: str
    lock_type: LockType
    total_amount: Decimal
    currency: str
    locked_amount: Decimal
    released_amount: Decimal
    lock_start: datetime
    lock_end: datetime
    vesting_schedule: Optional[VestingSchedule]
    milestones: List[Dict[str, Any]]
    status: PaymentStatus
    creator_address: str
    created_at: datetime
    last_release_at: Optional[datetime]


class TimeLockedPayments:
    """
    Time-Locked Payment Management System
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Time-Locked Payments system"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.locked_payments: Dict[str, TimeLockedPayment] = {}
        
        # System settings
        self.min_lock_duration = config.get("min_lock_hours", 1)
        self.max_lock_duration = config.get("max_lock_days", 3650)  # 10 years
        self.emergency_release_enabled = config.get("emergency_release", True)
    
    async def create_time_lock(
        self,
        beneficiary_address: str,
        amount: Decimal,
        currency: str,
        lock_type: LockType,
        lock_duration_days: int,
        creator_address: str,
        vesting_config: Optional[Dict[str, Any]] = None,
        milestones: Optional[List[Dict[str, Any]]] = None
    ) -> TimeLockedPayment:
        """Create new time-locked payment"""
        try:
            payment_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating time lock: {amount} {currency} for {lock_duration_days} days")
            
            # Validate duration
            if lock_duration_days < 0:
                raise ValueError("Lock duration cannot be negative")
            
            if lock_duration_days > self.max_lock_duration:
                raise ValueError(f"Lock duration exceeds maximum: {lock_duration_days}")
            
            # Calculate lock period
            lock_start = datetime.utcnow()
            lock_end = lock_start + timedelta(days=lock_duration_days)
            
            # Create vesting schedule if provided
            vesting_schedule = None
            if vesting_config and lock_type in [LockType.VESTING_SCHEDULE, LockType.CLIFF_VESTING]:
                vesting_schedule = VestingSchedule(
                    total_amount=amount,
                    start_date=lock_start,
                    cliff_period_days=vesting_config.get("cliff_days", 0),
                    vesting_period_days=lock_duration_days,
                    release_frequency_days=vesting_config.get("frequency_days", 30),
                    initial_unlock_percentage=Decimal(str(vesting_config.get("initial_unlock", 0)))
                )
            
            payment = TimeLockedPayment(
                payment_id=payment_id,
                beneficiary_address=beneficiary_address,
                lock_type=lock_type,
                total_amount=amount,
                currency=currency,
                locked_amount=amount,
                released_amount=Decimal("0"),
                lock_start=lock_start,
                lock_end=lock_end,
                vesting_schedule=vesting_schedule,
                milestones=milestones or [],
                status=PaymentStatus.LOCKED,
                creator_address=creator_address,
                created_at=datetime.utcnow(),
                last_release_at=None
            )
            
            self.locked_payments[payment_id] = payment
            
            self.logger.info(f"Time lock created: {payment_id}")
            return payment
            
        except Exception as e:
            self.logger.error(f"Time lock creation failed: {e}")
            raise
    
    async def check_unlock_eligibility(self, payment_id: str) -> Dict[str, Any]:
        """Check if payment is eligible for unlock"""
        try:
            if payment_id not in self.locked_payments:
                raise ValueError(f"Payment not found: {payment_id}")
            
            payment = self.locked_payments[payment_id]
            current_time = datetime.utcnow()
            
            if payment.status in [PaymentStatus.CANCELLED, PaymentStatus.EMERGENCY_RELEASED]:
                return {
                    "eligible": False,
                    "reason": f"Payment status: {payment.status.value}",
                    "unlockable_amount": "0"
                }
            
            if payment.lock_type == LockType.SINGLE_RELEASE:
                eligible = current_time >= payment.lock_end
                unlockable = payment.locked_amount if eligible else Decimal("0")
                
            elif payment.lock_type in [LockType.VESTING_SCHEDULE, LockType.CLIFF_VESTING]:
                unlockable = await self._calculate_vested_amount(payment, current_time)
                eligible = unlockable > 0
                
            elif payment.lock_type == LockType.MILESTONE_BASED:
                unlockable = await self._calculate_milestone_unlocks(payment)
                eligible = unlockable > 0
                
            elif payment.lock_type == LockType.STREAMING:
                unlockable = await self._calculate_streaming_amount(payment, current_time)
                eligible = unlockable > 0
                
            else:
                eligible = False
                unlockable = Decimal("0")
            
            return {
                "eligible": eligible,
                "unlockable_amount": str(unlockable),
                "locked_amount": str(payment.locked_amount),
                "released_amount": str(payment.released_amount),
                "total_amount": str(payment.total_amount),
                "lock_end": payment.lock_end.isoformat(),
                "current_time": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Unlock eligibility check failed: {e}")
            raise
    
    async def _calculate_vested_amount(self, payment: TimeLockedPayment, current_time: datetime) -> Decimal:
        """Calculate vested amount for vesting schedule"""
        if not payment.vesting_schedule:
            return Decimal("0")
        
        schedule = payment.vesting_schedule
        
        # Check if we're before cliff period
        cliff_end = schedule.start_date + timedelta(days=schedule.cliff_period_days)
        if current_time < cliff_end:
            return Decimal("0")
        
        # Calculate initial unlock
        initial_unlock = schedule.total_amount * (schedule.initial_unlock_percentage / 100)
        
        # Calculate time-based vesting
        vesting_start = max(cliff_end, schedule.start_date)
        vesting_end = schedule.start_date + timedelta(days=schedule.vesting_period_days)
        
        if current_time >= vesting_end:
            # Fully vested
            total_vested = schedule.total_amount
        else:
            # Partially vested
            vesting_duration = vesting_end - vesting_start
            elapsed_time = current_time - vesting_start
            vesting_progress = elapsed_time / vesting_duration
            
            remaining_amount = schedule.total_amount - initial_unlock
            vested_amount = initial_unlock + (remaining_amount * vesting_progress)
            total_vested = min(vested_amount, schedule.total_amount)
        
        # Subtract already released amount
        unlockable = total_vested - payment.released_amount
        return max(unlockable, Decimal("0"))
    
    async def _calculate_milestone_unlocks(self, payment: TimeLockedPayment) -> Decimal:
        """Calculate unlockable amount from completed milestones"""
        unlockable = Decimal("0")
        
        for milestone in payment.milestones:
            if milestone.get("completed", False) and not milestone.get("released", False):
                milestone_amount = Decimal(str(milestone.get("amount", 0)))
                unlockable += milestone_amount
        
        return min(unlockable, payment.locked_amount)
    
    async def _calculate_streaming_amount(self, payment: TimeLockedPayment, current_time: datetime) -> Decimal:
        """Calculate unlockable amount for streaming payments"""
        if current_time < payment.lock_start:
            return Decimal("0")
        
        total_duration = payment.lock_end - payment.lock_start
        elapsed_time = current_time - payment.lock_start
        
        if elapsed_time >= total_duration:
            # Fully unlocked
            return payment.locked_amount
        
        # Calculate streaming progress
        progress = elapsed_time / total_duration
        unlocked_amount = payment.total_amount * progress
        
        # Subtract already released amount
        unlockable = unlocked_amount - payment.released_amount
        return max(unlockable, Decimal("0"))
    
    async def unlock_payment(
        self,
        payment_id: str,
        unlock_amount: Optional[Decimal] = None,
        requester_address: str = ""
    ) -> Dict[str, Any]:
        """Unlock eligible payment amount"""
        try:
            if payment_id not in self.locked_payments:
                raise ValueError(f"Payment not found: {payment_id}")
            
            payment = self.locked_payments[payment_id]
            
            # Check eligibility
            eligibility = await self.check_unlock_eligibility(payment_id)
            if not eligibility["eligible"]:
                raise ValueError(f"Payment not eligible for unlock: {eligibility['reason']}")
            
            max_unlockable = Decimal(eligibility["unlockable_amount"])
            
            # Determine unlock amount
            if unlock_amount is None:
                unlock_amount = max_unlockable
            else:
                unlock_amount = min(unlock_amount, max_unlockable)
            
            if unlock_amount <= 0:
                raise ValueError("No amount available for unlock")
            
            self.logger.info(f"Unlocking payment: {unlock_amount} {payment.currency}")
            
            # Process unlock
            unlock_result = await self._process_unlock(payment, unlock_amount)
            
            # Update payment record
            payment.released_amount += unlock_amount
            payment.locked_amount -= unlock_amount
            payment.last_release_at = datetime.utcnow()
            
            # Update status
            if payment.locked_amount <= 0:
                payment.status = PaymentStatus.FULLY_UNLOCKED
            else:
                payment.status = PaymentStatus.PARTIALLY_UNLOCKED
            
            result = {
                "payment_id": payment_id,
                "unlocked_amount": str(unlock_amount),
                "currency": payment.currency,
                "beneficiary_address": payment.beneficiary_address,
                "remaining_locked": str(payment.locked_amount),
                "total_released": str(payment.released_amount),
                "unlock_transaction": unlock_result["transaction_hash"],
                "unlocked_at": datetime.utcnow().isoformat(),
                "new_status": payment.status.value
            }
            
            self.logger.info(f"Payment unlocked: {payment_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Payment unlock failed: {e}")
            raise
    
    async def _process_unlock(self, payment: TimeLockedPayment, amount: Decimal) -> Dict[str, Any]:
        """Process the actual unlock transaction"""
        # Mock transaction processing
        import hashlib
        tx_data = f"{payment.beneficiary_address}{amount}{payment.currency}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return {
            "transaction_hash": f"0x{tx_hash}",
            "block_number": 12345700,
            "gas_used": 50000
        }
    
    async def complete_milestone(
        self,
        payment_id: str,
        milestone_id: str,
        completion_evidence: Dict[str, Any],
        completer_address: str
    ) -> Dict[str, Any]:
        """Mark milestone as completed for milestone-based locks"""
        try:
            if payment_id not in self.locked_payments:
                raise ValueError(f"Payment not found: {payment_id}")
            
            payment = self.locked_payments[payment_id]
            
            if payment.lock_type != LockType.MILESTONE_BASED:
                raise ValueError("Payment is not milestone-based")
            
            # Find milestone
            milestone = None
            for m in payment.milestones:
                if m.get("id") == milestone_id:
                    milestone = m
                    break
            
            if not milestone:
                raise ValueError(f"Milestone not found: {milestone_id}")
            
            if milestone.get("completed", False):
                raise ValueError("Milestone already completed")
            
            self.logger.info(f"Completing milestone: {milestone_id}")
            
            # Mark milestone as completed
            milestone["completed"] = True
            milestone["completed_at"] = datetime.utcnow().isoformat()
            milestone["completed_by"] = completer_address
            milestone["evidence"] = completion_evidence
            
            result = {
                "payment_id": payment_id,
                "milestone_id": milestone_id,
                "milestone_amount": str(milestone.get("amount", 0)),
                "completed_by": completer_address,
                "completed_at": milestone["completed_at"],
                "ready_for_unlock": True
            }
            
            self.logger.info(f"Milestone completed: {milestone_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Milestone completion failed: {e}")
            raise
    
    async def emergency_release(
        self,
        payment_id: str,
        releaser_address: str,
        reason: str
    ) -> Dict[str, Any]:
        """Emergency release of locked funds"""
        try:
            if not self.emergency_release_enabled:
                raise ValueError("Emergency release is disabled")
            
            if payment_id not in self.locked_payments:
                raise ValueError(f"Payment not found: {payment_id}")
            
            payment = self.locked_payments[payment_id]
            
            # Only creator or beneficiary can emergency release
            if releaser_address not in [payment.creator_address, payment.beneficiary_address]:
                raise ValueError("Insufficient permission for emergency release")
            
            if payment.locked_amount <= 0:
                raise ValueError("No locked funds to release")
            
            self.logger.info(f"Emergency releasing payment: {payment_id}")
            
            # Release all locked funds
            release_amount = payment.locked_amount
            unlock_result = await self._process_unlock(payment, release_amount)
            
            # Update payment record
            payment.released_amount += release_amount
            payment.locked_amount = Decimal("0")
            payment.status = PaymentStatus.EMERGENCY_RELEASED
            payment.last_release_at = datetime.utcnow()
            
            result = {
                "payment_id": payment_id,
                "released_amount": str(release_amount),
                "currency": payment.currency,
                "releaser_address": releaser_address,
                "reason": reason,
                "release_transaction": unlock_result["transaction_hash"],
                "released_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Emergency release completed: {payment_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Emergency release failed: {e}")
            raise
    
    async def get_payment_info(self, payment_id: str) -> Dict[str, Any]:
        """Get time-locked payment information"""
        if payment_id not in self.locked_payments:
            raise ValueError(f"Payment not found: {payment_id}")
        
        payment = self.locked_payments[payment_id]
        
        return {
            "payment_id": payment.payment_id,
            "beneficiary_address": payment.beneficiary_address,
            "lock_type": payment.lock_type.value,
            "total_amount": str(payment.total_amount),
            "currency": payment.currency,
            "locked_amount": str(payment.locked_amount),
            "released_amount": str(payment.released_amount),
            "lock_start": payment.lock_start.isoformat(),
            "lock_end": payment.lock_end.isoformat(),
            "status": payment.status.value,
            "creator_address": payment.creator_address,
            "created_at": payment.created_at.isoformat(),
            "last_release_at": payment.last_release_at.isoformat() if payment.last_release_at else None,
            "vesting_schedule": {
                "cliff_period_days": payment.vesting_schedule.cliff_period_days,
                "vesting_period_days": payment.vesting_schedule.vesting_period_days,
                "release_frequency_days": payment.vesting_schedule.release_frequency_days,
                "initial_unlock_percentage": str(payment.vesting_schedule.initial_unlock_percentage)
            } if payment.vesting_schedule else None,
            "milestones": payment.milestones,
            "milestones_completed": len([m for m in payment.milestones if m.get("completed", False)])
        }


class TimeLockManager:
    """High-level manager for time-locked payment operations"""
    
    def __init__(self, time_locked_payments: TimeLockedPayments):
        self.time_locked_payments = time_locked_payments
        self.logger = logging.getLogger(__name__)
    
    async def setup_creator_vesting(
        self,
        creator_address: str,
        total_amount: Decimal,
        currency: str,
        vesting_months: int,
        cliff_months: int = 6
    ) -> TimeLockedPayment:
        """Setup standard creator vesting schedule"""
        vesting_config = {
            "cliff_days": cliff_months * 30,
            "frequency_days": 30,  # Monthly releases
            "initial_unlock": 10  # 10% initial unlock
        }
        
        return await self.time_locked_payments.create_time_lock(
            creator_address,
            total_amount,
            currency,
            LockType.CLIFF_VESTING,
            vesting_months * 30,
            "system",
            vesting_config
        )