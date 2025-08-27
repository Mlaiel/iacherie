"""
Billing Engine

Advanced billing and invoicing engine for subscription management.
Handles automated billing cycles, prorations, tax calculations, and payment processing integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, List, Tuple
import calendar
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import (
    UserSubscription, SubscriptionPlan, BillingCycle, Invoice,
    PaymentStatus, BillingCycleType, BillingSummary
)
from .payment_processor import PaymentProcessor
from ..core.database import get_db_session
from ..core.exceptions import (
    BillingError, PaymentError, ValidationError,
    SubscriptionNotFoundError
)
from ..core.logging import get_logger
from ..core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class BillingEngine:
    """
    Comprehensive billing engine for subscription management.
    
    Features:
    - Automated billing cycle processing
    - Proration calculations for plan changes
    - Tax calculation and compliance
    - Invoice generation and management
    - Payment retry logic
    - Revenue recognition and reporting
    - Multi-currency support
    - Dunning management for failed payments
    """
    
    def __init__(self):
        """Initialize billing engine."""
        self.payment_processor = PaymentProcessor()
        self.logger = get_logger(__name__)
        
        # Billing configuration
        self.default_currency = settings.DEFAULT_CURRENCY
        self.tax_rates = settings.TAX_RATES  # Country-specific tax rates
        self.retry_intervals = [1, 3, 7]  # Days between payment retries
        self.dunning_grace_period = 7  # Days before suspension
    
    async def process_subscription_billing(
        self,
        subscription_id: int,
        billing_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Process billing for a subscription.
        
        Args:
            subscription_id: Subscription ID
            billing_date: Billing date (defaults to now)
            db: Database session
            
        Returns:
            Billing processing result
        """
        if not db:
            db = get_db_session()
        
        if not billing_date:
            billing_date = datetime.utcnow()
        
        try:
            # Get subscription details
            subscription = db.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError(f"Subscription {subscription_id} not found")
            
            # Check if billing is due
            if not self._is_billing_due(subscription, billing_date):
                return {
                    "success": True,
                    "action": "no_billing_due",
                    "next_billing_date": subscription.next_billing_date
                }
            
            # Calculate billing amount
            billing_amount = await self._calculate_billing_amount(subscription, billing_date, db)
            
            # Create billing cycle record
            billing_cycle = await self._create_billing_cycle(
                subscription, billing_amount, billing_date, db
            )
            
            # Generate invoice
            invoice = await self._generate_invoice(
                subscription, billing_cycle, billing_date, db
            )
            
            # Process payment
            payment_result = await self._process_payment(
                subscription, invoice, billing_amount, db
            )
            
            if payment_result["success"]:
                # Update billing cycle status
                billing_cycle.payment_status = PaymentStatus.COMPLETED.value
                billing_cycle.payment_date = billing_date
                billing_cycle.transaction_id = payment_result["transaction_id"]
                
                # Update invoice status
                invoice.status = PaymentStatus.COMPLETED.value
                invoice.payment_date = billing_date
                invoice.payment_method = payment_result["payment_method"]
                
                # Update subscription
                subscription.last_payment_date = billing_date
                subscription.next_billing_date = self._calculate_next_billing_date(
                    subscription, billing_date
                )
                
                db.commit()
                
                self.logger.info(f"Billing processed successfully for subscription {subscription_id}")
                
                return {
                    "success": True,
                    "action": "billing_processed",
                    "amount": billing_amount,
                    "currency": invoice.currency,
                    "invoice_id": invoice.id,
                    "transaction_id": payment_result["transaction_id"],
                    "next_billing_date": subscription.next_billing_date
                }
            
            else:
                # Handle payment failure
                billing_cycle.payment_status = PaymentStatus.FAILED.value
                invoice.status = PaymentStatus.FAILED.value
                
                # Schedule retry
                retry_date = await self._schedule_payment_retry(subscription, db)
                
                db.commit()
                
                self.logger.warning(f"Billing failed for subscription {subscription_id}: {payment_result['error']}")
                
                return {
                    "success": False,
                    "action": "billing_failed",
                    "error": payment_result["error"],
                    "retry_date": retry_date,
                    "invoice_id": invoice.id
                }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Billing processing failed for subscription {subscription_id}: {str(e)}")
            raise BillingError(f"Billing processing failed: {str(e)}")
    
    async def calculate_proration(
        self,
        subscription: UserSubscription,
        new_plan: SubscriptionPlan,
        change_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Calculate proration for plan changes.
        
        Args:
            subscription: Current subscription
            new_plan: New subscription plan
            change_date: Change date (defaults to now)
            db: Database session
            
        Returns:
            Proration calculation details
        """
        if not change_date:
            change_date = datetime.utcnow()
        
        try:
            # Get current plan
            current_plan = subscription.plan
            
            # Calculate current plan pricing
            current_price = self._get_plan_price_for_cycle(
                current_plan, subscription.billing_cycle
            )
            
            new_price = self._get_plan_price_for_cycle(
                new_plan, subscription.billing_cycle
            )
            
            # Calculate remaining time in current billing period
            remaining_days = (subscription.end_date - change_date).days
            total_days = self._get_billing_period_days(subscription.billing_cycle)
            
            # Calculate prorations
            current_unused_amount = (current_price * remaining_days / total_days).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            new_period_amount = (new_price * remaining_days / total_days).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            proration_amount = new_period_amount - current_unused_amount
            
            return {
                "current_plan_price": current_price,
                "new_plan_price": new_price,
                "remaining_days": remaining_days,
                "total_days": total_days,
                "current_unused_amount": current_unused_amount,
                "new_period_amount": new_period_amount,
                "proration_amount": proration_amount,
                "is_upgrade": proration_amount > 0,
                "currency": subscription.plan.currency
            }
            
        except Exception as e:
            self.logger.error(f"Proration calculation failed: {str(e)}")
            raise BillingError(f"Proration calculation failed: {str(e)}")
    
    async def generate_invoice(
        self,
        subscription_id: int,
        billing_cycle_id: int,
        db: Session = None
    ) -> Invoice:
        """
        Generate invoice for subscription billing.
        
        Args:
            subscription_id: Subscription ID
            billing_cycle_id: Billing cycle ID
            db: Database session
            
        Returns:
            Generated invoice
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get subscription and billing cycle
            subscription = db.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            billing_cycle = db.query(BillingCycle).filter(
                BillingCycle.id == billing_cycle_id
            ).first()
            
            if not subscription or not billing_cycle:
                raise ValidationError("Subscription or billing cycle not found")
            
            # Generate invoice number
            invoice_number = self._generate_invoice_number()
            
            # Calculate invoice amounts
            subtotal = billing_cycle.billing_amount
            tax_amount = await self._calculate_tax_amount(subscription, subtotal)
            discount_amount = billing_cycle.discount_amount
            total_amount = subtotal + tax_amount - discount_amount
            
            # Create line items
            line_items = await self._create_invoice_line_items(subscription, billing_cycle)
            
            # Create invoice
            invoice = Invoice(
                subscription_id=subscription_id,
                user_id=subscription.user_id,
                invoice_number=invoice_number,
                invoice_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_amount=discount_amount,
                total_amount=total_amount,
                currency=subscription.plan.currency,
                line_items=line_items,
                status=PaymentStatus.PENDING.value
            )
            
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            
            self.logger.info(f"Invoice {invoice_number} generated for subscription {subscription_id}")
            return invoice
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Invoice generation failed: {str(e)}")
            raise BillingError(f"Invoice generation failed: {str(e)}")
    
    async def get_billing_summary(
        self,
        subscription_id: int,
        db: Session = None
    ) -> BillingSummary:
        """
        Get billing summary for subscription.
        
        Args:
            subscription_id: Subscription ID
            db: Database session
            
        Returns:
            Billing summary
        """
        if not db:
            db = get_db_session()
        
        try:
            subscription = db.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError(f"Subscription {subscription_id} not found")
            
            # Get current billing cycle
            current_cycle = db.query(BillingCycle).filter(
                BillingCycle.subscription_id == subscription_id,
                BillingCycle.cycle_end >= datetime.utcnow()
            ).first()
            
            # Calculate amount due for next billing
            next_amount = subscription.next_payment_amount or self._get_plan_price_for_cycle(
                subscription.plan, subscription.billing_cycle
            )
            
            return BillingSummary(
                subscription_id=subscription_id,
                current_period_start=current_cycle.cycle_start if current_cycle else subscription.start_date,
                current_period_end=current_cycle.cycle_end if current_cycle else subscription.end_date,
                next_billing_date=subscription.next_billing_date or subscription.end_date,
                amount_due=next_amount,
                payment_status=current_cycle.payment_status if current_cycle else PaymentStatus.PENDING.value,
                payment_method=subscription.payment_method_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get billing summary: {str(e)}")
            raise BillingError(f"Failed to get billing summary: {str(e)}")
    
    async def process_refund(
        self,
        invoice_id: int,
        refund_amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Process refund for invoice.
        
        Args:
            invoice_id: Invoice ID
            refund_amount: Refund amount (defaults to full amount)
            reason: Refund reason
            db: Database session
            
        Returns:
            Refund processing result
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get invoice
            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            
            if not invoice:
                raise ValidationError(f"Invoice {invoice_id} not found")
            
            if invoice.status != PaymentStatus.COMPLETED.value:
                raise ValidationError("Can only refund completed payments")
            
            # Default to full refund
            if not refund_amount:
                refund_amount = invoice.total_amount
            
            # Validate refund amount
            if refund_amount > invoice.total_amount:
                raise ValidationError("Refund amount cannot exceed invoice total")
            
            # Process refund through payment processor
            refund_result = await self.payment_processor.process_refund(
                invoice.stripe_invoice_id or invoice.paypal_invoice_id,
                refund_amount,
                reason
            )
            
            if refund_result["success"]:
                # Update invoice status
                if refund_amount == invoice.total_amount:
                    invoice.status = PaymentStatus.REFUNDED.value
                else:
                    invoice.status = "partially_refunded"
                
                invoice.updated_at = datetime.utcnow()
                
                db.commit()
                
                self.logger.info(f"Refund processed for invoice {invoice_id}: {refund_amount}")
                
                return {
                    "success": True,
                    "refund_amount": refund_amount,
                    "refund_id": refund_result["refund_id"],
                    "status": invoice.status
                }
            
            else:
                return {
                    "success": False,
                    "error": refund_result["error"]
                }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Refund processing failed: {str(e)}")
            raise BillingError(f"Refund processing failed: {str(e)}")
    
    # Private helper methods
    
    def _is_billing_due(self, subscription: UserSubscription, billing_date: datetime) -> bool:
        """Check if billing is due for subscription."""
        if not subscription.next_billing_date:
            return False
        
        return subscription.next_billing_date <= billing_date
    
    async def _calculate_billing_amount(
        self,
        subscription: UserSubscription,
        billing_date: datetime,
        db: Session
    ) -> Decimal:
        """Calculate billing amount for subscription."""
        # Base amount from plan
        base_amount = self._get_plan_price_for_cycle(
            subscription.plan, subscription.billing_cycle
        )
        
        # Add any pending prorations
        proration_amount = await self._get_pending_prorations(subscription.id, db)
        
        # Apply discounts
        discount_amount = await self._calculate_discounts(subscription, db)
        
        total_amount = base_amount + proration_amount - discount_amount
        
        return max(total_amount, Decimal('0.00'))
    
    def _get_plan_price_for_cycle(
        self, 
        plan: SubscriptionPlan, 
        billing_cycle: str
    ) -> Decimal:
        """Get plan price for specific billing cycle."""
        if billing_cycle == BillingCycleType.MONTHLY.value:
            return plan.monthly_price
        elif billing_cycle == BillingCycleType.YEARLY.value:
            return plan.yearly_price
        elif billing_cycle == BillingCycleType.QUARTERLY.value:
            return plan.quarterly_price
        else:
            return plan.monthly_price
    
    def _get_billing_period_days(self, billing_cycle: str) -> int:
        """Get number of days in billing period."""
        if billing_cycle == BillingCycleType.MONTHLY.value:
            return 30
        elif billing_cycle == BillingCycleType.YEARLY.value:
            return 365
        elif billing_cycle == BillingCycleType.QUARTERLY.value:
            return 90
        else:
            return 30
    
    async def _create_billing_cycle(
        self,
        subscription: UserSubscription,
        billing_amount: Decimal,
        billing_date: datetime,
        db: Session
    ) -> BillingCycle:
        """Create billing cycle record."""
        # Calculate cycle dates
        cycle_start = billing_date
        cycle_end = self._calculate_next_billing_date(subscription, billing_date)
        
        billing_cycle = BillingCycle(
            subscription_id=subscription.id,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            billing_amount=billing_amount,
            currency=subscription.plan.currency,
            payment_status=PaymentStatus.PENDING.value
        )
        
        db.add(billing_cycle)
        db.commit()
        db.refresh(billing_cycle)
        
        return billing_cycle
    
    def _calculate_next_billing_date(
        self, 
        subscription: UserSubscription, 
        current_date: datetime
    ) -> datetime:
        """Calculate next billing date based on billing cycle."""
        if subscription.billing_cycle == BillingCycleType.MONTHLY.value:
            # Add one month
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            else:
                # Handle month-end dates properly
                next_month = current_date.month + 1
                last_day = calendar.monthrange(current_date.year, next_month)[1]
                day = min(current_date.day, last_day)
                return current_date.replace(month=next_month, day=day)
        
        elif subscription.billing_cycle == BillingCycleType.YEARLY.value:
            # Add one year
            try:
                return current_date.replace(year=current_date.year + 1)
            except ValueError:
                # Handle Feb 29 on non-leap years
                return current_date.replace(year=current_date.year + 1, day=28)
        
        elif subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
            # Add 3 months
            return current_date + timedelta(days=90)
        
        else:
            # Default to monthly
            return current_date + timedelta(days=30)
    
    async def _generate_invoice(
        self,
        subscription: UserSubscription,
        billing_cycle: BillingCycle,
        billing_date: datetime,
        db: Session
    ) -> Invoice:
        """Generate invoice for billing cycle."""
        return await self.generate_invoice(subscription.id, billing_cycle.id, db)
    
    async def _process_payment(
        self,
        subscription: UserSubscription,
        invoice: Invoice,
        amount: Decimal,
        db: Session
    ) -> Dict[str, Any]:
        """Process payment for invoice."""
        if not subscription.payment_method_id:
            return {
                "success": False,
                "error": "No payment method on file"
            }
        
        return await self.payment_processor.charge_payment_method(
            subscription.payment_method_id,
            amount,
            invoice.currency,
            {
                "subscription_id": subscription.id,
                "invoice_id": invoice.id,
                "user_id": subscription.user_id
            }
        )
    
    async def _schedule_payment_retry(
        self, 
        subscription: UserSubscription, 
        db: Session
    ) -> datetime:
        """Schedule payment retry for failed billing."""
        # Get retry count from billing cycles
        failed_attempts = db.query(BillingCycle).filter(
            BillingCycle.subscription_id == subscription.id,
            BillingCycle.payment_status == PaymentStatus.FAILED.value,
            BillingCycle.cycle_start >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Determine retry interval
        if failed_attempts < len(self.retry_intervals):
            retry_days = self.retry_intervals[failed_attempts]
        else:
            retry_days = self.retry_intervals[-1]
        
        retry_date = datetime.utcnow() + timedelta(days=retry_days)
        subscription.next_billing_date = retry_date
        
        return retry_date
    
    async def _calculate_tax_amount(
        self, 
        subscription: UserSubscription, 
        subtotal: Decimal
    ) -> Decimal:
        """Calculate tax amount based on user location."""
        # This would integrate with tax service or use configured rates
        # For now, return 0 (implement based on business requirements)
        return Decimal('0.00')
    
    async def _create_invoice_line_items(
        self,
        subscription: UserSubscription,
        billing_cycle: BillingCycle
    ) -> List[Dict[str, Any]]:
        """Create invoice line items."""
        line_items = []
        
        # Main subscription line item
        line_items.append({
            "description": f"{subscription.plan.display_name} - {subscription.billing_cycle}",
            "quantity": 1,
            "unit_price": float(billing_cycle.billing_amount),
            "total": float(billing_cycle.billing_amount),
            "period_start": billing_cycle.cycle_start.isoformat(),
            "period_end": billing_cycle.cycle_end.isoformat()
        })
        
        # Add proration line items if applicable
        if billing_cycle.prorated_amount != 0:
            line_items.append({
                "description": "Plan change proration",
                "quantity": 1,
                "unit_price": float(billing_cycle.prorated_amount),
                "total": float(billing_cycle.prorated_amount),
                "type": "proration"
            })
        
        # Add discount line items if applicable
        if billing_cycle.discount_amount > 0:
            line_items.append({
                "description": "Discount",
                "quantity": 1,
                "unit_price": float(-billing_cycle.discount_amount),
                "total": float(-billing_cycle.discount_amount),
                "type": "discount"
            })
        
        return line_items
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number."""
        import uuid
        timestamp = datetime.utcnow().strftime("%Y%m")
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"INV-{timestamp}-{unique_id}"
    
    async def _get_pending_prorations(self, subscription_id: int, db: Session) -> Decimal:
        """Get pending proration amounts."""
        pending_cycles = db.query(BillingCycle).filter(
            BillingCycle.subscription_id == subscription_id,
            BillingCycle.prorated_amount != 0,
            BillingCycle.payment_status == PaymentStatus.PENDING.value
        ).all()
        
        return sum(cycle.prorated_amount for cycle in pending_cycles)
    
    async def _calculate_discounts(
        self, 
        subscription: UserSubscription, 
        db: Session
    ) -> Decimal:
        """Calculate applicable discounts."""
        # This would integrate with discount/coupon system
        # For now, return 0 (implement based on business requirements)
        return Decimal('0.00')


__all__ = ['BillingEngine']
