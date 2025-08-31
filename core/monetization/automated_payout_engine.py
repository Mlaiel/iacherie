"""Automated Payout Engine
Intelligent payout processing, scheduling and optimization system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ...database.models import User, Payout, RevenueRecord
from ...core.security.encryption import SecurityManager
from .payment_processor import PaymentProcessor, PaymentConfig


class PayoutStatus(Enum):
    """Payout processing status"""    SCHEDULED = "scheduled"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PayoutMethod(Enum):
    """Available payout methods"""    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    WISE = "wise"
    STRIPE_TRANSFER = "stripe_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"


class PayoutFrequency(Enum):
    """Payout frequency options"""    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


@dataclass
class PayoutDestination:
    """Payout destination details"""    method: PayoutMethod
    account_id: str
    account_name: str
    routing_details: Dict[str, str]
    currency: str = "EUR"
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "method": self.method.value,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "routing_details": self.routing_details,
            "currency": self.currency,
            "is_verified": self.is_verified,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None
        }


@dataclass
class PayoutRequest:
    """Payout request details"""    request_id: str
    user_id: int
    amount: Decimal
    currency: str
    destination: PayoutDestination
    description: Optional[str] = None
    requested_date: datetime = field(default_factory=datetime.now)
    scheduled_date: Optional[datetime] = None
    status: PayoutStatus = PayoutStatus.SCHEDULED
    processing_fee: Decimal = Decimal("0")
    net_amount: Optional[Decimal] = None
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount after fees"""        if self.net_amount is None:
            self.net_amount = self.amount - self.processing_fee
        return self.net_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "destination": self.destination.to_dict(),
            "description": self.description,
            "requested_date": self.requested_date.isoformat(),
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "status": self.status.value,
            "processing_fee": float(self.processing_fee),
            "net_amount": float(self.net_amount) if self.net_amount else None,
            "transaction_id": self.transaction_id,
            "failure_reason": self.failure_reason,
            "metadata": self.metadata
        }


@dataclass
class PayoutSchedule:
    """User payout schedule configuration"""    user_id: int
    frequency: PayoutFrequency
    minimum_amount: Decimal
    destination: PayoutDestination
    auto_payout_enabled: bool = True
    hold_period_days: int = 7
    timezone: str = "UTC"
    next_payout_date: Optional[datetime] = None
    
    def calculate_next_payout_date(self, last_payout_date: Optional[datetime] = None) -> datetime:
        """Calculate next payout date based on frequency"""        base_date = last_payout_date or datetime.now()
        
        if self.frequency == PayoutFrequency.DAILY:
            next_date = base_date + timedelta(days=1)
        elif self.frequency == PayoutFrequency.WEEKLY:
            next_date = base_date + timedelta(weeks=1)
        elif self.frequency == PayoutFrequency.BIWEEKLY:
            next_date = base_date + timedelta(weeks=2)
        elif self.frequency == PayoutFrequency.MONTHLY:
            # First day of next month
            if base_date.month == 12:
                next_date = base_date.replace(year=base_date.year + 1, month=1, day=1)
            else:
                next_date = base_date.replace(month=base_date.month + 1, day=1)
        elif self.frequency == PayoutFrequency.QUARTERLY:
            # Add 3 months
            month = base_date.month
            year = base_date.year
            month += 3
            if month > 12:
                year += 1
                month -= 12
            next_date = base_date.replace(year=year, month=month, day=1)
        else:
            # ON_DEMAND - no automatic scheduling
            next_date = base_date
        
        self.next_payout_date = next_date
        return next_date


class PayoutOptimizer:
    """Payout cost optimization engine"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Fee structures for different methods
        self.fee_structures = {
            PayoutMethod.BANK_TRANSFER: {
                "fixed_fee": Decimal("2.50"),
                "percentage_fee": Decimal("0.01"),  # 1%
                "min_fee": Decimal("1.00"),
                "max_fee": Decimal("25.00")
            },
            PayoutMethod.PAYPAL: {
                "fixed_fee": Decimal("0.30"),
                "percentage_fee": Decimal("0.029"),  # 2.9%
                "min_fee": Decimal("0.30"),
                "max_fee": Decimal("50.00")
            },
            PayoutMethod.WISE: {
                "fixed_fee": Decimal("0.50"),
                "percentage_fee": Decimal("0.005"),  # 0.5%
                "min_fee": Decimal("0.50"),
                "max_fee": Decimal("15.00")
            },
            PayoutMethod.STRIPE_TRANSFER: {
                "fixed_fee": Decimal("0.25"),
                "percentage_fee": Decimal("0.025"),  # 2.5%
                "min_fee": Decimal("0.25"),
                "max_fee": Decimal("30.00")
            }
        }
    
    def calculate_optimal_method(
        self,
        amount: Decimal,
        currency: str,
        available_methods: List[PayoutMethod]
    ) -> Tuple[PayoutMethod, Decimal]:
        """Calculate optimal payout method with lowest fees"""        
        best_method = None
        lowest_fee = None
        
        for method in available_methods:
            if method not in self.fee_structures:
                continue
            
            fee = self.calculate_fee(amount, method)
            
            if lowest_fee is None or fee < lowest_fee:
                lowest_fee = fee
                best_method = method
        
        return best_method or PayoutMethod.BANK_TRANSFER, lowest_fee or Decimal("0")
    
    def calculate_fee(self, amount: Decimal, method: PayoutMethod) -> Decimal:
        """Calculate fee for specific payout method"""        
        if method not in self.fee_structures:
            return Decimal("0")
        
        structure = self.fee_structures[method]
        
        # Calculate percentage fee
        percentage_fee = amount * structure["percentage_fee"]
        
        # Add fixed fee
        total_fee = percentage_fee + structure["fixed_fee"]
        
        # Apply min/max limits
        total_fee = max(total_fee, structure["min_fee"])
        total_fee = min(total_fee, structure["max_fee"])
        
        return total_fee
    
    def recommend_payout_timing(
        self,
        user_id: int,
        current_balance: Decimal,
        schedule: PayoutSchedule
    ) -> Dict[str, Any]:
        """Recommend optimal payout timing"""        
        now = datetime.now()
        
        # Check if minimum amount is met
        if current_balance < schedule.minimum_amount:
            return {
                "should_payout": False,
                "reason": "Below minimum payout amount",
                "next_check_date": (now + timedelta(days=1)).isoformat(),
                "required_amount": float(schedule.minimum_amount),
                "current_balance": float(current_balance),
                "shortage": float(schedule.minimum_amount - current_balance)
            }
        
        # Check if hold period has passed
        # This would check the last revenue date and hold period
        
        # Check if scheduled date has arrived
        if schedule.next_payout_date and now < schedule.next_payout_date:
            return {
                "should_payout": False,
                "reason": "Scheduled date not reached",
                "next_payout_date": schedule.next_payout_date.isoformat(),
                "days_remaining": (schedule.next_payout_date - now).days
            }
        
        return {
            "should_payout": True,
            "recommended_amount": float(current_balance),
            "estimated_fee": float(self.calculate_fee(current_balance, schedule.destination.method)),
            "net_amount": float(current_balance - self.calculate_fee(current_balance, schedule.destination.method))
        }


class PayoutEngine:
    """Main payout processing engine"""    
    def __init__(
        self,
        payment_processor: PaymentProcessor,
        optimizer: PayoutOptimizer,
        security_manager: SecurityManager
    ):
        self.payment_processor = payment_processor
        self.optimizer = optimizer
        self.security_manager = security_manager
        self.logger = logging.getLogger(__name__)
        self.processing_lock = asyncio.Lock()
    
    async def create_payout_request(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        destination: PayoutDestination,
        description: Optional[str] = None,
        scheduled_date: Optional[datetime] = None,
        session: AsyncSession
    ) -> PayoutRequest:
        """Create a new payout request"""        
        try:
            # Validate destination
            if not destination.is_verified:
                raise ValueError("Payout destination must be verified")
            
            # Calculate processing fee
            processing_fee = self.optimizer.calculate_fee(amount, destination.method)
            
            # Create payout request
            request = PayoutRequest(
                request_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=amount,
                currency=currency,
                destination=destination,
                description=description,
                scheduled_date=scheduled_date,
                processing_fee=processing_fee
            )
            
            request.calculate_net_amount()
            
            # Store in database
            payout_record = Payout(
                request_id=request.request_id,
                user_id=user_id,
                amount=amount,
                currency=currency,
                destination_method=destination.method.value,
                destination_account=destination.account_id,
                processing_fee=processing_fee,
                net_amount=request.net_amount,
                status=request.status.value,
                scheduled_date=scheduled_date,
                metadata=request.to_dict()
            )
            
            session.add(payout_record)
            await session.commit()
            
            self.logger.info(f"Created payout request {request.request_id} for user {user_id}")
            return request
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Failed to create payout request: {str(e)}")
            raise
    
    async def process_scheduled_payouts(self, session: AsyncSession) -> List[PayoutRequest]:
        """Process all scheduled payouts that are due"""        
        async with self.processing_lock:
            try:
                # Get pending payouts
                result = await session.execute(
                    select(Payout).where(
                        Payout.status.in_([PayoutStatus.SCHEDULED.value, PayoutStatus.PENDING.value]),
                        or_(
                            Payout.scheduled_date <= datetime.now(),
                            Payout.scheduled_date.is_(None)
                        )
                    )
                )
                
                processed_payouts = []
                
                for record in result.scalars():
                    try:
                        payout_request = await self._convert_record_to_request(record)
                        processed_request = await self.process_single_payout(payout_request, session)
                        processed_payouts.append(processed_request)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to process payout {record.request_id}: {str(e)}")
                        # Mark as failed
                        record.status = PayoutStatus.FAILED.value
                        record.failure_reason = str(e)
                
                await session.commit()
                return processed_payouts
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Scheduled payout processing failed: {str(e)}")
                return []
    
    async def process_single_payout(
        self,
        request: PayoutRequest,
        session: AsyncSession
    ) -> PayoutRequest:
        """Process a single payout request"""        
        try:
            # Update status to processing
            request.status = PayoutStatus.PROCESSING
            await self._update_payout_status(request, session)
            
            # Verify user balance
            available_balance = await self._get_user_available_balance(request.user_id, session)
            
            if available_balance < request.amount:
                raise ValueError(f"Insufficient balance: {available_balance} < {request.amount}")
            
            # Process payment based on destination method
            if request.destination.method == PayoutMethod.PAYPAL:
                transaction_id = await self._process_paypal_payout(request)
            elif request.destination.method == PayoutMethod.WISE:
                transaction_id = await self._process_wise_payout(request)
            elif request.destination.method == PayoutMethod.STRIPE_TRANSFER:
                transaction_id = await self._process_stripe_payout(request)
            elif request.destination.method == PayoutMethod.BANK_TRANSFER:
                transaction_id = await self._process_bank_transfer(request)
            else:
                raise ValueError(f"Unsupported payout method: {request.destination.method}")
            
            # Update successful completion
            request.status = PayoutStatus.COMPLETED
            request.transaction_id = transaction_id
            
            # Record the payout in user's balance
            await self._record_payout_transaction(request, session)
            
            await self._update_payout_status(request, session)
            
            self.logger.info(f"Payout {request.request_id} completed successfully")
            return request
            
        except Exception as e:
            # Mark as failed
            request.status = PayoutStatus.FAILED
            request.failure_reason = str(e)
            await self._update_payout_status(request, session)
            
            self.logger.error(f"Payout processing failed: {str(e)}")
            raise
    
    async def _process_paypal_payout(self, request: PayoutRequest) -> str:
        """Process PayPal payout"""        
        # Configure PayPal payment
        config = PaymentConfig(
            gateway="paypal",
            amount=request.net_amount,
            currency=request.currency,
            recipient_email=request.destination.account_id,
            description=request.description or f"Payout {request.request_id}"
        )
        
        # Process payment
        result = await self.payment_processor.process_payout(config)
        
        if not result.get("success"):
            raise ValueError(f"PayPal payout failed: {result.get('error')}")
        
        return result.get("transaction_id")
    
    async def _process_wise_payout(self, request: PayoutRequest) -> str:
        """Process Wise (TransferWise) payout"""        
        config = PaymentConfig(
            gateway="wise",
            amount=request.net_amount,
            currency=request.currency,
            recipient_account=request.destination.account_id,
            routing_details=request.destination.routing_details,
            description=request.description or f"Payout {request.request_id}"
        )
        
        result = await self.payment_processor.process_payout(config)
        
        if not result.get("success"):
            raise ValueError(f"Wise payout failed: {result.get('error')}")
        
        return result.get("transaction_id")
    
    async def _process_stripe_payout(self, request: PayoutRequest) -> str:
        """Process Stripe Connect payout"""        
        config = PaymentConfig(
            gateway="stripe",
            amount=request.net_amount,
            currency=request.currency,
            destination_account=request.destination.account_id,
            description=request.description or f"Payout {request.request_id}"
        )
        
        result = await self.payment_processor.process_payout(config)
        
        if not result.get("success"):
            raise ValueError(f"Stripe payout failed: {result.get('error')}")
        
        return result.get("transaction_id")
    
    async def _process_bank_transfer(self, request: PayoutRequest) -> str:
        """Process direct bank transfer"""        
        # This would integrate with banking APIs or manual processing
        # For now, return a mock transaction ID
        transaction_id = f"BANK_{request.request_id[:8]}_{int(datetime.now().timestamp())}"
        
        # In production, this would:
        # 1. Create ACH/SEPA transfer
        # 2. Submit to banking partner
        # 3. Return actual transaction ID
        
        return transaction_id
    
    async def _get_user_available_balance(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Decimal:
        """Get user's available balance for payout"""        
        # Calculate total revenue
        revenue_result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.status == "confirmed"
            )
        )
        
        total_revenue = Decimal(str(revenue_result.scalar() or 0))
        
        # Calculate total payouts
        payout_result = await session.execute(
            select(func.sum(Payout.amount)).where(
                Payout.user_id == user_id,
                Payout.status.in_([PayoutStatus.COMPLETED.value, PayoutStatus.PROCESSING.value])
            )
        )
        
        total_payouts = Decimal(str(payout_result.scalar() or 0))
        
        return total_revenue - total_payouts
    
    async def _record_payout_transaction(
        self,
        request: PayoutRequest,
        session: AsyncSession
    ) -> None:
        """Record payout transaction in user's transaction history"""        
        # This would create a transaction record
        # Implementation depends on your transaction model
        pass
    
    async def _update_payout_status(
        self,
        request: PayoutRequest,
        session: AsyncSession
    ) -> None:
        """Update payout status in database"""        
        result = await session.execute(
            select(Payout).where(Payout.request_id == request.request_id)
        )
        
        record = result.scalar_one_or_none()
        if record:
            record.status = request.status.value
            record.transaction_id = request.transaction_id
            record.failure_reason = request.failure_reason
            await session.commit()
    
    async def _convert_record_to_request(self, record: Payout) -> PayoutRequest:
        """Convert database record to PayoutRequest object"""        
        # Reconstruct destination from metadata
        metadata = record.metadata or {}
        destination_data = metadata.get("destination", {})
        
        destination = PayoutDestination(
            method=PayoutMethod(record.destination_method),
            account_id=record.destination_account,
            account_name=destination_data.get("account_name", ""),
            routing_details=destination_data.get("routing_details", {}),
            currency=record.currency,
            is_verified=True  # Assume verified if record exists
        )
        
        return PayoutRequest(
            request_id=record.request_id,
            user_id=record.user_id,
            amount=record.amount,
            currency=record.currency,
            destination=destination,
            description=metadata.get("description"),
            requested_date=record.created_at,
            scheduled_date=record.scheduled_date,
            status=PayoutStatus(record.status),
            processing_fee=record.processing_fee,
            net_amount=record.net_amount,
            transaction_id=record.transaction_id,
            failure_reason=record.failure_reason,
            metadata=metadata
        )
    
    async def get_user_payout_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        session: AsyncSession
    ) -> List[PayoutRequest]:
        """Get user's payout history"""        
        try:
            result = await session.execute(
                select(Payout)
                .where(Payout.user_id == user_id)
                .order_by(Payout.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            history = []
            for record in result.scalars():
                request = await self._convert_record_to_request(record)
                history.append(request)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get payout history: {str(e)}")
            return []


class PayoutScheduler:
    """Automated payout scheduling service"""    
    def __init__(self, payout_engine: PayoutEngine, optimizer: PayoutOptimizer):
        self.payout_engine = payout_engine
        self.optimizer = optimizer
        self.logger = logging.getLogger(__name__)
        self.scheduler_running = False
    
    async def start_scheduler(self, check_interval_minutes: int = 60):
        """Start automated payout scheduler"""        
        self.scheduler_running = True
        
        while self.scheduler_running:
            try:
                await self._process_scheduled_payouts()
                await asyncio.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def stop_scheduler(self):
        """Stop automated payout scheduler"""        self.scheduler_running = False
    
    async def _process_scheduled_payouts(self):
        """Process all due scheduled payouts"""        
        # This would get database session and process payouts
        # Implementation depends on your database session management
        pass
