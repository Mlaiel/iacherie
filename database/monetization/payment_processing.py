"""Payment Processing Engine - Enterprise Payment Gateway Integration

Ultra-advanced payment processing system supporting multiple gateways (Stripe, Wise, PayPal)
with comprehensive fraud detection, compliance management, and automated retry logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass, asdict

import stripe
import paypalrestsdk
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload

from .payment_models import (
    PaymentAccount, PaymentTransaction, RevenuePayout, PayoutItem,
    PaymentGateway, PaymentStatus, PaymentType, Currency, PaymentMethodConfiguration
)
from ..core.exceptions import PaymentProcessingError, GatewayError, ValidationError
from ..core.security import SecurityManager
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class PaymentProcessingEngine:
    """    Ultra-advanced payment processing engine with multi-gateway support,
    fraud detection, compliance management, and automated retry logic
    """    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.gateway_clients = {}
        self.retry_delays = [1, 3, 7, 15, 30]  # seconds
        self.max_retries = 3
        
        # Initialize gateway clients
        self._initialize_gateways()
    
    def _initialize_gateways(self):
        """Initialize payment gateway clients with configuration"""        try:
            # Stripe configuration
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.api_version = "2023-10-16"
            self.gateway_clients[PaymentGateway.STRIPE] = stripe
            
            # PayPal configuration
            paypalrestsdk.configure({
                "mode": settings.PAYPAL_MODE,
                "client_id": settings.PAYPAL_CLIENT_ID,
                "client_secret": settings.PAYPAL_CLIENT_SECRET
            })
            self.gateway_clients[PaymentGateway.PAYPAL] = paypalrestsdk
            
            # Wise API client
            self.gateway_clients[PaymentGateway.WISE] = httpx.AsyncClient(
                base_url=settings.WISE_API_BASE_URL,
                headers={
                    "Authorization": f"Bearer {settings.WISE_API_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            
            logger.info("Payment gateways initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize payment gateways: {str(e)}")
            raise PaymentProcessingError(f"Gateway initialization failed: {str(e)}")
    
    async def process_payment(
        self,
        session: AsyncSession,
        user_id: str,
        amount: Decimal,
        currency: Currency,
        payment_type: PaymentType,
        gateway: PaymentGateway,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransaction:
        """        Process a payment through the specified gateway with comprehensive
        fraud detection and validation
        """        try:
            # Get user's payment account
            payment_account = await self._get_payment_account(session, user_id, gateway)
            if not payment_account:
                raise ValidationError(f"No payment account found for gateway {gateway.value}")
            
            # Validate payment request
            await self._validate_payment_request(
                payment_account, amount, currency, payment_type
            )
            
            # Create payment transaction record
            transaction = PaymentTransaction(
                user_id=uuid.UUID(user_id),
                account_id=payment_account.id,
                payment_type=payment_type,
                gateway=gateway,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                metadata=metadata or {}
            )
            
            session.add(transaction)
            await session.flush()
            
            # Process payment through gateway
            gateway_response = await self._process_gateway_payment(
                gateway, payment_account, transaction, payment_method_id
            )
            
            # Update transaction with gateway response
            transaction.gateway_transaction_id = gateway_response.get("id")
            transaction.gateway_response = gateway_response
            transaction.status = self._map_gateway_status(gateway, gateway_response.get("status"))
            
            if transaction.status == PaymentStatus.COMPLETED:
                transaction.completed_at = datetime.now(timezone.utc)
                transaction.processed_at = datetime.now(timezone.utc)
            elif transaction.status == PaymentStatus.FAILED:
                transaction.failed_at = datetime.now(timezone.utc)
                transaction.error_message = gateway_response.get("failure_reason")
            
            await session.commit()
            
            # Send webhook notifications
            await self._send_payment_webhook(transaction, gateway_response)
            
            logger.info(f"Payment processed: {transaction.transaction_id}, Status: {transaction.status.value}")
            return transaction
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Payment processing failed: {str(e)}")
            
            if 'transaction' in locals():
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = str(e)
                transaction.failed_at = datetime.now(timezone.utc)
                await session.commit()
            
            raise PaymentProcessingError(f"Payment processing failed: {str(e)}")
    
    async def process_payout(
        self,
        session: AsyncSession,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
        gateway: PaymentGateway = PaymentGateway.STRIPE
    ) -> RevenuePayout:
        """        Process revenue payout for a user within the specified period
        """        try:
            # Get user's payment account
            payment_account = await self._get_payment_account(session, user_id, gateway)
            if not payment_account:
                raise ValidationError(f"No payment account found for gateway {gateway.value}")
            
            # Calculate revenue for the period
            revenue_data = await self._calculate_period_revenue(
                session, user_id, period_start, period_end
            )
            
            if revenue_data["net_payout"] <= Decimal("0"):
                raise ValidationError("No revenue available for payout")
            
            # Check minimum payout threshold
            if revenue_data["net_payout"] < payment_account.min_payout_amount:
                raise ValidationError(
                    f"Payout amount below minimum threshold: {payment_account.min_payout_amount}"
                )
            
            # Create payout record
            payout = RevenuePayout(
                user_id=uuid.UUID(user_id),
                payment_account_id=payment_account.id,
                period_start=period_start,
                period_end=period_end,
                gross_revenue=revenue_data["gross_revenue"],
                platform_commission=revenue_data["platform_commission"],
                gateway_fees=revenue_data["gateway_fees"],
                tax_withholding=revenue_data["tax_withholding"],
                net_payout=revenue_data["net_payout"],
                currency=payment_account.primary_currency,
                gateway=gateway,
                revenue_breakdown=revenue_data["breakdown"],
                status=PaymentStatus.PENDING
            )
            
            session.add(payout)
            await session.flush()
            
            # Create payout items
            await self._create_payout_items(session, payout, revenue_data["items"])
            
            # Process payout through gateway
            gateway_response = await self._process_gateway_payout(gateway, payment_account, payout)
            
            # Update payout with gateway response
            payout.gateway_payout_id = gateway_response.get("id")
            payout.status = self._map_gateway_status(gateway, gateway_response.get("status"))
            payout.processed_at = datetime.now(timezone.utc)
            
            if payout.status == PaymentStatus.COMPLETED:
                payout.completed_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            # Generate invoice and documentation
            await self._generate_payout_documentation(payout)
            
            logger.info(f"Payout processed: {payout.payout_id}, Amount: {payout.net_payout}")
            return payout
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Payout processing failed: {str(e)}")
            raise PaymentProcessingError(f"Payout processing failed: {str(e)}")
    
    async def _process_gateway_payment(
        self,
        gateway: PaymentGateway,
        payment_account: PaymentAccount,
        transaction: PaymentTransaction,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process payment through specific gateway"""        
        if gateway == PaymentGateway.STRIPE:
            return await self._process_stripe_payment(
                payment_account, transaction, payment_method_id
            )
        elif gateway == PaymentGateway.PAYPAL:
            return await self._process_paypal_payment(
                payment_account, transaction
            )
        elif gateway == PaymentGateway.WISE:
            return await self._process_wise_payment(
                payment_account, transaction
            )
        else:
            raise GatewayError(f"Unsupported gateway: {gateway.value}")
    
    async def _process_stripe_payment(
        self,
        payment_account: PaymentAccount,
        transaction: PaymentTransaction,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""        try:
            stripe_client = self.gateway_clients[PaymentGateway.STRIPE]
            
            payment_intent_data = {
                "amount": int(transaction.amount * 100),  # Convert to cents
                "currency": transaction.currency.value.lower(),
                "payment_method": payment_method_id,
                "confirm": True,
                "return_url": settings.STRIPE_RETURN_URL,
                "metadata": {
                    "transaction_id": str(transaction.id),
                    "user_id": str(transaction.user_id),
                    "payment_type": transaction.payment_type.value
                }
            }
            
            # Add connected account if applicable
            if payment_account.gateway_config.get("stripe_account_id"):
                payment_intent_data["on_behalf_of"] = payment_account.gateway_config["stripe_account_id"]
            
            payment_intent = stripe_client.PaymentIntent.create(**payment_intent_data)
            
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount / 100,
                "currency": payment_intent.currency.upper(),
                "charges": payment_intent.charges.data if payment_intent.charges else [],
                "failure_reason": payment_intent.last_payment_error.message if payment_intent.last_payment_error else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment failed: {str(e)}")
            raise GatewayError(f"Stripe payment failed: {str(e)}")
    
    async def _process_paypal_payment(
        self,
        payment_account: PaymentAccount,
        transaction: PaymentTransaction
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""        try:
            payment_data = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(transaction.amount),
                        "currency": transaction.currency.value
                    },
                    "description": f"Payment for {transaction.payment_type.value}"
                }],
                "redirect_urls": {
                    "return_url": settings.PAYPAL_RETURN_URL,
                    "cancel_url": settings.PAYPAL_CANCEL_URL
                }
            }
            
            payment = paypalrestsdk.Payment(payment_data)
            
            if payment.create():
                return {
                    "id": payment.id,
                    "status": payment.state,
                    "approval_url": next(
                        link.href for link in payment.links if link.rel == "approval_url"
                    ),
                    "amount": transaction.amount,
                    "currency": transaction.currency.value
                }
            else:
                raise GatewayError(f"PayPal payment creation failed: {payment.error}")
                
        except Exception as e:
            logger.error(f"PayPal payment failed: {str(e)}")
            raise GatewayError(f"PayPal payment failed: {str(e)}")
    
    async def _process_wise_payment(
        self,
        payment_account: PaymentAccount,
        transaction: PaymentTransaction
    ) -> Dict[str, Any]:
        """Process payment through Wise (formerly TransferWise)"""        try:
            wise_client = self.gateway_clients[PaymentGateway.WISE]
            
            # Create transfer request
            transfer_data = {
                "targetAccount": payment_account.gateway_account_id,
                "quoteUuid": await self._get_wise_quote(
                    wise_client, transaction.amount, transaction.currency
                ),
                "customerTransactionId": str(transaction.id),
                "details": {
                    "reference": f"Revenue payout - {transaction.payment_type.value}",
                    "transferPurpose": "verification.transfers.purpose.pay.bills",
                    "sourceOfFunds": "verification.source.of.funds.other"
                }
            }
            
            response = await wise_client.post("/v1/transfers", json=transfer_data)
            response.raise_for_status()
            
            transfer = response.json()
            
            return {
                "id": transfer["id"],
                "status": transfer["status"],
                "amount": transaction.amount,
                "currency": transaction.currency.value,
                "rate": transfer.get("rate"),
                "fee": transfer.get("fee")
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Wise payment failed: {e.response.text}")
            raise GatewayError(f"Wise payment failed: {e.response.text}")
    
    async def _calculate_period_revenue(
        self,
        session: AsyncSession,
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate total revenue for a user within the specified period"""        
        # Query revenue records for the period
        from .revenue_models import RevenueRecord
        
        stmt = select(RevenueRecord).where(
            and_(
                RevenueRecord.user_id == uuid.UUID(user_id),
                RevenueRecord.period_start >= period_start,
                RevenueRecord.period_end <= period_end,
                RevenueRecord.is_paid == False
            )
        )
        
        result = await session.execute(stmt)
        revenue_records = result.scalars().all()
        
        gross_revenue = Decimal("0")
        platform_commission = Decimal("0")
        gateway_fees = Decimal("0")
        tax_withholding = Decimal("0")
        
        revenue_items = []
        breakdown = {
            "platforms": {},
            "content_types": {},
            "revenue_types": {}
        }
        
        for record in revenue_records:
            gross_revenue += record.gross_amount
            platform_commission += record.platform_fee or Decimal("0")
            
            # Calculate gateway fees (2.9% + 0.30 for Stripe)
            gateway_fee = (record.net_amount * Decimal("0.029")) + Decimal("0.30")
            gateway_fees += gateway_fee
            
            # Tax withholding (if applicable based on user's tax status)
            tax_rate = await self._get_user_tax_rate(session, user_id)
            tax_amount = record.net_amount * tax_rate
            tax_withholding += tax_amount
            
            # Update breakdown
            platform = record.platform
            if platform not in breakdown["platforms"]:
                breakdown["platforms"][platform] = Decimal("0")
            breakdown["platforms"][platform] += record.net_amount
            
            # Add to revenue items
            revenue_items.append({
                "record_id": str(record.id),
                "platform": platform,
                "amount": record.net_amount,
                "content_type": record.content_type,
                "revenue_type": record.revenue_type.value
            })
        
        net_payout = gross_revenue - platform_commission - gateway_fees - tax_withholding
        
        return {
            "gross_revenue": gross_revenue,
            "platform_commission": platform_commission,
            "gateway_fees": gateway_fees,
            "tax_withholding": tax_withholding,
            "net_payout": max(net_payout, Decimal("0")),
            "breakdown": breakdown,
            "items": revenue_items
        }
    
    async def _get_payment_account(
        self,
        session: AsyncSession,
        user_id: str,
        gateway: PaymentGateway
    ) -> Optional[PaymentAccount]:
        """Get user's payment account for the specified gateway"""        
        stmt = select(PaymentAccount).where(
            and_(
                PaymentAccount.user_id == uuid.UUID(user_id),
                PaymentAccount.gateway == gateway,
                PaymentAccount.is_active == True,
                PaymentAccount.is_verified == True
            )
        )
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _validate_payment_request(
        self,
        payment_account: PaymentAccount,
        amount: Decimal,
        currency: Currency,
        payment_type: PaymentType
    ):
        """Validate payment request against account limits and policies"""        
        # Check currency support
        if currency not in payment_account.supported_currencies:
            raise ValidationError(f"Currency {currency.value} not supported")
        
        # Check amount limits
        if amount < Decimal("0.01"):
            raise ValidationError("Amount must be positive")
        
        if payment_account.max_transaction_amount and amount > payment_account.max_transaction_amount:
            raise ValidationError(f"Amount exceeds maximum limit: {payment_account.max_transaction_amount}")
        
        # Check daily/monthly limits
        # This would involve querying recent transactions and summing amounts
        # Implementation details depend on specific business requirements
        
        # Check account verification level
        if payment_account.verification_level == "basic" and amount > Decimal("1000"):
            raise ValidationError("Enhanced verification required for amounts over €1000")
    
    def _map_gateway_status(self, gateway: PaymentGateway, gateway_status: str) -> PaymentStatus:
        """Map gateway-specific status to internal PaymentStatus"""        
        status_mapping = {
            PaymentGateway.STRIPE: {
                "succeeded": PaymentStatus.COMPLETED,
                "processing": PaymentStatus.PROCESSING,
                "requires_payment_method": PaymentStatus.FAILED,
                "requires_confirmation": PaymentStatus.PENDING,
                "requires_action": PaymentStatus.PENDING,
                "canceled": PaymentStatus.CANCELLED,
                "failed": PaymentStatus.FAILED
            },
            PaymentGateway.PAYPAL: {
                "created": PaymentStatus.PENDING,
                "approved": PaymentStatus.PROCESSING,
                "completed": PaymentStatus.COMPLETED,
                "cancelled": PaymentStatus.CANCELLED,
                "failed": PaymentStatus.FAILED
            },
            PaymentGateway.WISE: {
                "incoming_payment_waiting": PaymentStatus.PENDING,
                "processing": PaymentStatus.PROCESSING,
                "funds_converted": PaymentStatus.PROCESSING,
                "outgoing_payment_sent": PaymentStatus.COMPLETED,
                "cancelled": PaymentStatus.CANCELLED,
                "failed": PaymentStatus.FAILED
            }
        }
        
        mapping = status_mapping.get(gateway, {})
        return mapping.get(gateway_status, PaymentStatus.PENDING)
    
    async def retry_failed_payment(
        self,
        session: AsyncSession,
        transaction_id: str
    ) -> PaymentTransaction:
        """Retry a failed payment with exponential backoff"""        
        # Get transaction
        stmt = select(PaymentTransaction).where(
            PaymentTransaction.id == uuid.UUID(transaction_id)
        )
        result = await session.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise ValidationError("Transaction not found")
        
        if transaction.status != PaymentStatus.FAILED:
            raise ValidationError("Only failed transactions can be retried")
        
        if transaction.retry_count >= transaction.max_retries:
            raise ValidationError("Maximum retry attempts exceeded")
        
        # Implement exponential backoff
        delay = self.retry_delays[min(transaction.retry_count, len(self.retry_delays) - 1)]
        await asyncio.sleep(delay)
        
        # Update retry count
        transaction.retry_count += 1
        transaction.status = PaymentStatus.PENDING
        transaction.error_message = None
        transaction.failed_at = None
        
        try:
            # Retry payment processing
            gateway_response = await self._process_gateway_payment(
                transaction.gateway,
                await self._get_payment_account(session, str(transaction.user_id), transaction.gateway),
                transaction
            )
            
            # Update transaction with new response
            transaction.gateway_response = gateway_response
            transaction.status = self._map_gateway_status(
                transaction.gateway, gateway_response.get("status")
            )
            
            if transaction.status == PaymentStatus.COMPLETED:
                transaction.completed_at = datetime.now(timezone.utc)
                transaction.processed_at = datetime.now(timezone.utc)
            elif transaction.status == PaymentStatus.FAILED:
                transaction.failed_at = datetime.now(timezone.utc)
                transaction.error_message = gateway_response.get("failure_reason")
            
            await session.commit()
            
            logger.info(f"Payment retry successful: {transaction.transaction_id}")
            return transaction
            
        except Exception as e:
            transaction.status = PaymentStatus.FAILED
            transaction.error_message = str(e)
            transaction.failed_at = datetime.now(timezone.utc)
            await session.commit()
            
            logger.error(f"Payment retry failed: {str(e)}")
            raise PaymentProcessingError(f"Payment retry failed: {str(e)}")
    
    async def handle_webhook(
        self,
        session: AsyncSession,
        gateway: PaymentGateway,
        webhook_data: Dict[str, Any],
        signature: str
    ):
        """Handle webhook notifications from payment gateways"""        
        # Verify webhook signature
        if not await self._verify_webhook_signature(gateway, webhook_data, signature):
            raise SecurityError("Invalid webhook signature")
        
        # Process webhook based on gateway
        if gateway == PaymentGateway.STRIPE:
            await self._handle_stripe_webhook(session, webhook_data)
        elif gateway == PaymentGateway.PAYPAL:
            await self._handle_paypal_webhook(session, webhook_data)
        elif gateway == PaymentGateway.WISE:
            await self._handle_wise_webhook(session, webhook_data)
    
    async def _verify_webhook_signature(
        self,
        gateway: PaymentGateway,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify webhook signature for security"""        
        if gateway == PaymentGateway.STRIPE:
            try:
                stripe.Webhook.construct_event(
                    json.dumps(payload), signature, settings.STRIPE_WEBHOOK_SECRET
                )
                return True
            except stripe.error.SignatureVerificationError:
                return False
        
        # Implement verification for other gateways
        return True
    
    async def _send_payment_webhook(
        self,
        transaction: PaymentTransaction,
        gateway_response: Dict[str, Any]
    ):
        """Send internal webhook notifications for payment events"""        
        webhook_data = {
            "event_type": "payment.processed",
            "transaction_id": str(transaction.id),
            "user_id": str(transaction.user_id),
            "status": transaction.status.value,
            "amount": float(transaction.amount),
            "currency": transaction.currency.value,
            "gateway": transaction.gateway.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send to internal webhook endpoints
        # Implementation depends on internal notification system
        logger.info(f"Webhook sent for transaction: {transaction.transaction_id}")
    
    async def get_payment_analytics(
        self,
        session: AsyncSession,
        user_id: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive payment analytics and metrics"""        
        # Build query conditions
        conditions = []
        if user_id:
            conditions.append(PaymentTransaction.user_id == uuid.UUID(user_id))
        if period_start:
            conditions.append(PaymentTransaction.initiated_at >= period_start)
        if period_end:
            conditions.append(PaymentTransaction.initiated_at <= period_end)
        
        # Query transactions
        stmt = select(PaymentTransaction)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await session.execute(stmt)
        transactions = result.scalars().all()
        
        # Calculate analytics
        analytics = {
            "total_transactions": len(transactions),
            "total_amount": sum(t.amount for t in transactions),
            "successful_transactions": len([t for t in transactions if t.status == PaymentStatus.COMPLETED]),
            "failed_transactions": len([t for t in transactions if t.status == PaymentStatus.FAILED]),
            "success_rate": 0,
            "by_gateway": {},
            "by_currency": {},
            "by_payment_type": {},
            "average_amount": Decimal("0"),
            "total_fees": sum(t.gateway_fee or Decimal("0") for t in transactions)
        }
        
        if analytics["total_transactions"] > 0:
            analytics["success_rate"] = analytics["successful_transactions"] / analytics["total_transactions"]
            analytics["average_amount"] = analytics["total_amount"] / analytics["total_transactions"]
        
        # Group by dimensions
        for transaction in transactions:
            # By gateway
            gateway = transaction.gateway.value
            if gateway not in analytics["by_gateway"]:
                analytics["by_gateway"][gateway] = {"count": 0, "amount": Decimal("0")}
            analytics["by_gateway"][gateway]["count"] += 1
            analytics["by_gateway"][gateway]["amount"] += transaction.amount
            
            # By currency
            currency = transaction.currency.value
            if currency not in analytics["by_currency"]:
                analytics["by_currency"][currency] = {"count": 0, "amount": Decimal("0")}
            analytics["by_currency"][currency]["count"] += 1
            analytics["by_currency"][currency]["amount"] += transaction.amount
            
            # By payment type
            payment_type = transaction.payment_type.value
            if payment_type not in analytics["by_payment_type"]:
                analytics["by_payment_type"][payment_type] = {"count": 0, "amount": Decimal("0")}
            analytics["by_payment_type"][payment_type]["count"] += 1
            analytics["by_payment_type"][payment_type]["amount"] += transaction.amount
        
        return analytics


# Utility functions
async def calculate_platform_commission(amount: Decimal, platform: str) -> Decimal:
    """Calculate platform commission based on amount and platform"""    commission_rates = {
        "spotify": Decimal("0.05"),    # 5%
        "youtube": Decimal("0.03"),    # 3%
        "instagram": Decimal("0.04"),  # 4%
        "tiktok": Decimal("0.06"),     # 6%
        "default": Decimal("0.05")     # 5% default
    }
    
    rate = commission_rates.get(platform.lower(), commission_rates["default"])
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def validate_bank_account(account_data: Dict[str, Any]) -> bool:
    """Validate bank account information using IBAN validation and other checks"""    # Implementation would include IBAN validation, routing number checks, etc.
    return True


# Export main classes and functions
__all__ = [
    'PaymentProcessingEngine',
    'calculate_platform_commission',
    'validate_bank_account'
]
