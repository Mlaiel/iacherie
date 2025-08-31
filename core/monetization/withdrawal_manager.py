"""Withdrawal Management System
Advanced withdrawal request processing and validation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel, Field, validator

from ...database.models import User, WithdrawalRequest as DBWithdrawalRequest, Payout
from .payment_processor import PaymentProcessor, PaymentRequest, PaymentGateway
from ...security.fraud_detection import FraudDetectionEngine


class WithdrawalStatus(Enum):
    """Withdrawal request status"""    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"


class WithdrawalMethod(Enum):
    """Withdrawal methods"""    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTO = "crypto"
    CHECK = "check"


class RejectionReason(Enum):
    """Reasons for withdrawal rejection"""    INSUFFICIENT_BALANCE = "insufficient_balance"
    FRAUD_DETECTED = "fraud_detected"
    INVALID_BANK_DETAILS = "invalid_bank_details"
    ACCOUNT_SUSPENDED = "account_suspended"
    MINIMUM_NOT_MET = "minimum_not_met"
    VERIFICATION_REQUIRED = "verification_required"
    TECHNICAL_ERROR = "technical_error"


@dataclass
class WithdrawalLimits:
    """Withdrawal limits configuration"""    minimum_amount: Decimal = Decimal("25.00")
    maximum_amount: Decimal = Decimal("50000.00")
    daily_limit: Decimal = Decimal("10000.00")
    weekly_limit: Decimal = Decimal("25000.00")
    monthly_limit: Decimal = Decimal("100000.00")
    max_pending_requests: int = 3
    cooldown_period_hours: int = 24


class WithdrawalRequest(BaseModel):
    """Withdrawal request data model"""    user_id: int
    amount: Decimal = Field(..., gt=0)
    method: WithdrawalMethod = WithdrawalMethod.BANK_TRANSFER
    currency: str = "EUR"
    bank_details: Optional[Dict[str, str]] = None
    paypal_email: Optional[str] = None
    crypto_address: Optional[str] = None
    notes: Optional[str] = None
    priority: bool = False
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if v < Decimal("1.00"):
            raise ValueError("Minimum withdrawal amount is €1.00")
        return v
    
    @validator('bank_details')
    def validate_bank_details(cls, v, values):
        if values.get('method') == WithdrawalMethod.BANK_TRANSFER and not v:
            raise ValueError("Bank details required for bank transfer")
        return v
    
    @validator('paypal_email')
    def validate_paypal_email(cls, v, values):
        if values.get('method') == WithdrawalMethod.PAYPAL and not v:
            raise ValueError("PayPal email required for PayPal withdrawal")
        return v


class WithdrawalValidationResult(BaseModel):
    """Withdrawal validation result"""    is_valid: bool
    available_balance: Decimal
    requested_amount: Decimal
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    fraud_score: Optional[float] = None
    limits_check: Dict[str, Any] = Field(default_factory=dict)


class WithdrawalResponse(BaseModel):
    """Withdrawal processing response"""    request_id: str
    status: WithdrawalStatus
    message: str
    estimated_processing_time: Optional[str] = None
    transaction_id: Optional[str] = None
    tracking_url: Optional[str] = None


class WithdrawalManager:
    """Advanced withdrawal management system"""    
    def __init__(
        self,
        payment_processor: PaymentProcessor,
        fraud_detection: FraudDetectionEngine
    ):
        self.payment_processor = payment_processor
        self.fraud_detection = fraud_detection
        self.logger = logging.getLogger(__name__)
        self.limits = WithdrawalLimits()
        
    async def submit_withdrawal_request(
        self,
        request: WithdrawalRequest,
        session: AsyncSession
    ) -> WithdrawalResponse:
        """Submit new withdrawal request"""        try:
            # Validate request
            validation = await self._validate_withdrawal_request(request, session)
            
            if not validation.is_valid:
                return WithdrawalResponse(
                    request_id="",
                    status=WithdrawalStatus.REJECTED,
                    message=f"Validation failed: {', '.join(validation.validation_errors)}"
                )
            
            # Create withdrawal record
            withdrawal_record = DBWithdrawalRequest(
                user_id=request.user_id,
                amount=request.amount,
                currency=request.currency,
                method=request.method.value,
                status=WithdrawalStatus.PENDING.value,
                bank_details=request.bank_details,
                paypal_email=request.paypal_email,
                crypto_address=request.crypto_address,
                notes=request.notes,
                priority=request.priority,
                fraud_score=validation.fraud_score
            )
            
            session.add(withdrawal_record)
            await session.commit()
            await session.refresh(withdrawal_record)
            
            # Determine processing approach
            if validation.fraud_score and validation.fraud_score > 0.7:
                # High fraud risk - require manual review
                withdrawal_record.status = WithdrawalStatus.UNDER_REVIEW.value
                message = "Request under manual review due to security checks"
                estimated_time = "1-3 business days"
                
            elif request.amount > Decimal("10000.00") or request.priority:
                # High amount or priority - expedited review
                withdrawal_record.status = WithdrawalStatus.UNDER_REVIEW.value
                message = "Request queued for priority processing"
                estimated_time = "2-4 hours"
                
            else:
                # Standard processing
                message = "Request submitted successfully"
                estimated_time = "1-2 business days"
            
            await session.commit()
            
            # Schedule automatic processing for eligible requests
            if withdrawal_record.status == WithdrawalStatus.PENDING.value:
                await self._schedule_automatic_processing(withdrawal_record.id)
            
            return WithdrawalResponse(
                request_id=withdrawal_record.id,
                status=WithdrawalStatus(withdrawal_record.status),
                message=message,
                estimated_processing_time=estimated_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to submit withdrawal request: {str(e)}")
            return WithdrawalResponse(
                request_id="",
                status=WithdrawalStatus.FAILED,
                message=f"System error: {str(e)}"
            )
    
    async def _validate_withdrawal_request(
        self,
        request: WithdrawalRequest,
        session: AsyncSession
    ) -> WithdrawalValidationResult:
        """Comprehensive withdrawal request validation"""        errors = []
        warnings = []
        
        # Get user and check account status
        user = await session.get(User, request.user_id)
        if not user:
            errors.append("User not found")
            return WithdrawalValidationResult(
                is_valid=False,
                available_balance=Decimal("0"),
                requested_amount=request.amount,
                validation_errors=errors
            )
        
        if user.status != "active":
            errors.append("Account not active")
        
        # Check available balance
        available_balance = await self._get_available_balance(request.user_id, session)
        
        if request.amount > available_balance:
            errors.append(f"Insufficient balance. Available: €{available_balance}")
        
        # Check minimum/maximum limits
        if request.amount < self.limits.minimum_amount:
            errors.append(f"Amount below minimum: €{self.limits.minimum_amount}")
        
        if request.amount > self.limits.maximum_amount:
            errors.append(f"Amount exceeds maximum: €{self.limits.maximum_amount}")
        
        # Check withdrawal limits
        limits_check = await self._check_withdrawal_limits(request, session)
        if not limits_check["within_limits"]:
            errors.extend(limits_check["violations"])
        
        # Check pending requests limit
        pending_count = await self._get_pending_requests_count(request.user_id, session)
        if pending_count >= self.limits.max_pending_requests:
            errors.append(f"Too many pending requests. Maximum: {self.limits.max_pending_requests}")
        
        # Check cooldown period
        last_request_time = await self._get_last_request_time(request.user_id, session)
        if last_request_time:
            cooldown_end = last_request_time + timedelta(hours=self.limits.cooldown_period_hours)
            if datetime.now() < cooldown_end:
                errors.append(f"Cooldown period active until {cooldown_end}")
        
        # Fraud detection
        fraud_score = await self.fraud_detection.analyze_withdrawal_request(request)
        
        if fraud_score > 0.8:
            warnings.append("High fraud risk detected - manual review required")
        elif fraud_score > 0.5:
            warnings.append("Moderate fraud risk detected")
        
        # Validate payment method details
        method_validation = await self._validate_payment_method_details(request)
        if not method_validation["valid"]:
            errors.extend(method_validation["errors"])
        
        return WithdrawalValidationResult(
            is_valid=len(errors) == 0,
            available_balance=available_balance,
            requested_amount=request.amount,
            validation_errors=errors,
            warnings=warnings,
            fraud_score=fraud_score,
            limits_check=limits_check
        )
    
    async def _get_available_balance(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Decimal:
        """Get user's available balance for withdrawal"""        from ...database.models import RevenueRecord
        
        # Total confirmed revenue
        revenue_result = await session.execute(
            select(func.sum(RevenueRecord.amount)).where(
                RevenueRecord.user_id == user_id,
                RevenueRecord.status == "confirmed"
            )
        )
        total_revenue = revenue_result.scalar() or 0
        
        # Total completed withdrawals
        withdrawal_result = await session.execute(
            select(func.sum(DBWithdrawalRequest.amount)).where(
                DBWithdrawalRequest.user_id == user_id,
                DBWithdrawalRequest.status.in_([
                    WithdrawalStatus.COMPLETED.value,
                    WithdrawalStatus.PROCESSING.value
                ])
            )
        )
        total_withdrawals = withdrawal_result.scalar() or 0
        
        # Pending withdrawals (reserved)
        pending_result = await session.execute(
            select(func.sum(DBWithdrawalRequest.amount)).where(
                DBWithdrawalRequest.user_id == user_id,
                DBWithdrawalRequest.status.in_([
                    WithdrawalStatus.PENDING.value,
                    WithdrawalStatus.APPROVED.value,
                    WithdrawalStatus.UNDER_REVIEW.value
                ])
            )
        )
        pending_withdrawals = pending_result.scalar() or 0
        
        available = Decimal(str(total_revenue)) - Decimal(str(total_withdrawals)) - Decimal(str(pending_withdrawals))
        return max(available, Decimal("0"))
    
    async def _check_withdrawal_limits(
        self,
        request: WithdrawalRequest,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Check withdrawal limits compliance"""        violations = []
        
        # Daily limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_total = await self._get_withdrawal_total_for_period(
            request.user_id, today_start, datetime.now(), session
        )
        
        if daily_total + request.amount > self.limits.daily_limit:
            violations.append(f"Daily limit exceeded. Limit: €{self.limits.daily_limit}")
        
        # Weekly limit
        week_start = today_start - timedelta(days=today_start.weekday())
        weekly_total = await self._get_withdrawal_total_for_period(
            request.user_id, week_start, datetime.now(), session
        )
        
        if weekly_total + request.amount > self.limits.weekly_limit:
            violations.append(f"Weekly limit exceeded. Limit: €{self.limits.weekly_limit}")
        
        # Monthly limit
        month_start = today_start.replace(day=1)
        monthly_total = await self._get_withdrawal_total_for_period(
            request.user_id, month_start, datetime.now(), session
        )
        
        if monthly_total + request.amount > self.limits.monthly_limit:
            violations.append(f"Monthly limit exceeded. Limit: €{self.limits.monthly_limit}")
        
        return {
            "within_limits": len(violations) == 0,
            "violations": violations,
            "usage": {
                "daily": {
                    "used": float(daily_total),
                    "limit": float(self.limits.daily_limit),
                    "remaining": float(self.limits.daily_limit - daily_total)
                },
                "weekly": {
                    "used": float(weekly_total),
                    "limit": float(self.limits.weekly_limit),
                    "remaining": float(self.limits.weekly_limit - weekly_total)
                },
                "monthly": {
                    "used": float(monthly_total),
                    "limit": float(self.limits.monthly_limit),
                    "remaining": float(self.limits.monthly_limit - monthly_total)
                }
            }
        }
    
    async def _get_withdrawal_total_for_period(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Decimal:
        """Get total withdrawal amount for period"""        result = await session.execute(
            select(func.sum(DBWithdrawalRequest.amount)).where(
                DBWithdrawalRequest.user_id == user_id,
                DBWithdrawalRequest.created_at >= start_date,
                DBWithdrawalRequest.created_at <= end_date,
                DBWithdrawalRequest.status.in_([
                    WithdrawalStatus.COMPLETED.value,
                    WithdrawalStatus.PROCESSING.value,
                    WithdrawalStatus.APPROVED.value,
                    WithdrawalStatus.PENDING.value
                ])
            )
        )
        
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")
    
    async def _get_pending_requests_count(
        self,
        user_id: int,
        session: AsyncSession
    ) -> int:
        """Get count of pending withdrawal requests"""        result = await session.execute(
            select(func.count(DBWithdrawalRequest.id)).where(
                DBWithdrawalRequest.user_id == user_id,
                DBWithdrawalRequest.status.in_([
                    WithdrawalStatus.PENDING.value,
                    WithdrawalStatus.UNDER_REVIEW.value,
                    WithdrawalStatus.APPROVED.value
                ])
            )
        )
        
        return result.scalar() or 0
    
    async def _get_last_request_time(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[datetime]:
        """Get timestamp of last withdrawal request"""        result = await session.execute(
            select(func.max(DBWithdrawalRequest.created_at)).where(
                DBWithdrawalRequest.user_id == user_id
            )
        )
        
        return result.scalar()
    
    async def _validate_payment_method_details(
        self,
        request: WithdrawalRequest
    ) -> Dict[str, Any]:
        """Validate payment method specific details"""        errors = []
        
        if request.method == WithdrawalMethod.BANK_TRANSFER:
            if not request.bank_details:
                errors.append("Bank details required for bank transfer")
            else:
                required_fields = ["account_number", "routing_number", "bank_name"]
                missing_fields = [field for field in required_fields if field not in request.bank_details]
                if missing_fields:
                    errors.append(f"Missing bank details: {', '.join(missing_fields)}")
        
        elif request.method == WithdrawalMethod.PAYPAL:
            if not request.paypal_email:
                errors.append("PayPal email required")
            elif "@" not in request.paypal_email:
                errors.append("Invalid PayPal email format")
        
        elif request.method == WithdrawalMethod.CRYPTO:
            if not request.crypto_address:
                errors.append("Crypto address required")
            elif len(request.crypto_address) < 20:
                errors.append("Invalid crypto address format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def process_withdrawal(
        self,
        request_id: str,
        session: AsyncSession
    ) -> WithdrawalResponse:
        """Process approved withdrawal request"""        try:
            # Get withdrawal request
            withdrawal = await session.get(DBWithdrawalRequest, request_id)
            if not withdrawal:
                return WithdrawalResponse(
                    request_id=request_id,
                    status=WithdrawalStatus.FAILED,
                    message="Withdrawal request not found"
                )
            
            # Check if eligible for processing
            if withdrawal.status not in [WithdrawalStatus.APPROVED.value, WithdrawalStatus.PENDING.value]:
                return WithdrawalResponse(
                    request_id=request_id,
                    status=WithdrawalStatus(withdrawal.status),
                    message=f"Cannot process request in {withdrawal.status} status"
                )
            
            # Update status to processing
            withdrawal.status = WithdrawalStatus.PROCESSING.value
            withdrawal.processed_at = datetime.now()
            await session.commit()
            
            # Create payment request
            user = await session.get(User, withdrawal.user_id)
            payment_request = PaymentRequest(
                user_id=withdrawal.user_id,
                amount=withdrawal.amount,
                currency=withdrawal.currency,
                gateway=self._get_payment_gateway(WithdrawalMethod(withdrawal.method)),
                description=f"Withdrawal for {user.name}",
                recipient_email=user.email if withdrawal.method == "paypal" else withdrawal.paypal_email,
                recipient_bank_details=withdrawal.bank_details
            )
            
            # Process payment
            payment_response = await self.payment_processor.process_payment(
                payment_request, session
            )
            
            # Update withdrawal with payment details
            withdrawal.transaction_id = payment_response.gateway_transaction_id
            withdrawal.payment_processor_response = payment_response.dict()
            
            if payment_response.status.value == "completed":
                withdrawal.status = WithdrawalStatus.COMPLETED.value
                withdrawal.completed_at = datetime.now()
                message = "Withdrawal completed successfully"
            else:
                message = "Withdrawal is being processed"
            
            await session.commit()
            
            return WithdrawalResponse(
                request_id=request_id,
                status=WithdrawalStatus(withdrawal.status),
                message=message,
                transaction_id=payment_response.gateway_transaction_id,
                tracking_url=payment_response.tracking_url
            )
            
        except Exception as e:
            # Mark withdrawal as failed
            if withdrawal:
                withdrawal.status = WithdrawalStatus.FAILED.value
                withdrawal.error_message = str(e)
                await session.commit()
            
            self.logger.error(f"Failed to process withdrawal {request_id}: {str(e)}")
            return WithdrawalResponse(
                request_id=request_id,
                status=WithdrawalStatus.FAILED,
                message=f"Processing failed: {str(e)}"
            )
    
    def _get_payment_gateway(self, method: WithdrawalMethod) -> PaymentGateway:
        """Map withdrawal method to payment gateway"""        mapping = {
            WithdrawalMethod.BANK_TRANSFER: PaymentGateway.WISE,
            WithdrawalMethod.PAYPAL: PaymentGateway.PAYPAL,
            WithdrawalMethod.STRIPE: PaymentGateway.STRIPE,
            WithdrawalMethod.WISE: PaymentGateway.WISE
        }
        
        return mapping.get(method, PaymentGateway.STRIPE)
    
    async def _schedule_automatic_processing(self, request_id: str) -> None:
        """Schedule automatic processing for eligible requests"""        # This would typically use a task queue like Celery
        # For now, we'll just log the scheduling
        self.logger.info(f"Scheduled automatic processing for withdrawal {request_id}")
    
    async def get_withdrawal_status(
        self,
        request_id: str,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get withdrawal request status and details"""        try:
            withdrawal = await session.get(DBWithdrawalRequest, request_id)
            if not withdrawal:
                return None
            
            return {
                "request_id": withdrawal.id,
                "user_id": withdrawal.user_id,
                "amount": float(withdrawal.amount),
                "currency": withdrawal.currency,
                "method": withdrawal.method,
                "status": withdrawal.status,
                "created_at": withdrawal.created_at.isoformat(),
                "processed_at": withdrawal.processed_at.isoformat() if withdrawal.processed_at else None,
                "completed_at": withdrawal.completed_at.isoformat() if withdrawal.completed_at else None,
                "transaction_id": withdrawal.transaction_id,
                "notes": withdrawal.notes,
                "fraud_score": withdrawal.fraud_score,
                "error_message": withdrawal.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get withdrawal status: {str(e)}")
            return None
    
    async def cancel_withdrawal(
        self,
        request_id: str,
        user_id: int,
        reason: str,
        session: AsyncSession
    ) -> bool:
        """Cancel pending withdrawal request"""        try:
            withdrawal = await session.get(DBWithdrawalRequest, request_id)
            if not withdrawal or withdrawal.user_id != user_id:
                return False
            
            # Can only cancel pending or under review requests
            if withdrawal.status not in [WithdrawalStatus.PENDING.value, WithdrawalStatus.UNDER_REVIEW.value]:
                return False
            
            withdrawal.status = WithdrawalStatus.CANCELLED.value
            withdrawal.cancellation_reason = reason
            withdrawal.cancelled_at = datetime.now()
            
            await session.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel withdrawal: {str(e)}")
            return False
    
    async def get_user_withdrawal_history(
        self,
        user_id: int,
        session: AsyncSession,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's withdrawal history"""        try:
            result = await session.execute(
                select(DBWithdrawalRequest).where(
                    DBWithdrawalRequest.user_id == user_id
                ).order_by(DBWithdrawalRequest.created_at.desc()).limit(limit)
            )
            
            withdrawals = result.scalars().all()
            
            return [
                {
                    "request_id": w.id,
                    "amount": float(w.amount),
                    "currency": w.currency,
                    "method": w.method,
                    "status": w.status,
                    "created_at": w.created_at.isoformat(),
                    "completed_at": w.completed_at.isoformat() if w.completed_at else None,
                    "transaction_id": w.transaction_id
                }
                for w in withdrawals
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get withdrawal history: {str(e)}")
            return []
    
    async def get_withdrawal_statistics(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get user's withdrawal statistics"""        try:
            # Total statistics
            total_result = await session.execute(
                select(
                    func.sum(DBWithdrawalRequest.amount).label('total_amount'),
                    func.count(DBWithdrawalRequest.id).label('total_count')
                ).where(
                    DBWithdrawalRequest.user_id == user_id,
                    DBWithdrawalRequest.status == WithdrawalStatus.COMPLETED.value
                )
            )
            total_row = total_result.first()
            
            # Status breakdown
            status_result = await session.execute(
                select(
                    DBWithdrawalRequest.status,
                    func.count(DBWithdrawalRequest.id).label('count')
                ).where(
                    DBWithdrawalRequest.user_id == user_id
                ).group_by(DBWithdrawalRequest.status)
            )
            
            status_breakdown = {row.status: row.count for row in status_result}
            
            return {
                "total_amount_withdrawn": float(total_row.total_amount) if total_row.total_amount else 0,
                "total_requests": total_row.total_count or 0,
                "average_withdrawal": float(total_row.total_amount / total_row.total_count) if total_row.total_count else 0,
                "status_breakdown": status_breakdown,
                "available_balance": float(await self._get_available_balance(user_id, session))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get withdrawal statistics: {str(e)}")
            return {}
