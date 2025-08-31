"""
Enterprise Payment Processing System
Multi-gateway payment handling with advanced security and compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import stripe
import paypal
from wise import WiseAPI
import hashlib
import hmac
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator

from ...database.models import User, Payment, Transaction
from ...security.encryption import EncryptionManager
from ...core.exceptions import PaymentError, ValidationError


class PaymentGateway(Enum):
    """Supported payment gateways"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Currency(Enum):
    """Supported currencies"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"


@dataclass
class PaymentConfig:
    """Payment gateway configuration"""
    gateway: PaymentGateway
    api_key: str
    secret_key: str
    webhook_secret: str
    sandbox_mode: bool = False
    currency: Currency = Currency.EUR
    fee_percentage: Decimal = Decimal("2.9")
    fixed_fee: Decimal = Decimal("0.30")
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key or not self.secret_key:
            raise ValidationError("API key and secret key are required")


class PaymentRequest(BaseModel):
    """Payment request data model"""
    user_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: Currency = Currency.EUR
    gateway: PaymentGateway = PaymentGateway.STRIPE
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    recipient_email: Optional[str] = None
    recipient_bank_details: Optional[Dict[str, str]] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v < Decimal("1.00"):
            raise ValueError("Minimum payment amount is 1.00")
        return v


class PaymentResponse(BaseModel):
    """Payment response data model"""
    payment_id: str
    status: PaymentStatus
    gateway_transaction_id: Optional[str] = None
    amount: Decimal
    currency: Currency
    fees: Decimal
    net_amount: Decimal
    created_at: datetime
    estimated_arrival: Optional[datetime] = None
    tracking_url: Optional[str] = None


class PaymentProcessor:
    """Advanced payment processing engine with multi-gateway support"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.logger = logging.getLogger(__name__)
        self.gateway_configs: Dict[PaymentGateway, PaymentConfig] = {}
        self.gateway_clients: Dict[PaymentGateway, Any] = {}
        
    def configure_gateway(self, config: PaymentConfig) -> None:
        """Configure payment gateway"""



        try:
            self.gateway_configs[config.gateway] = config
            
            # Initialize gateway client
            if config.gateway == PaymentGateway.STRIPE:
                stripe.api_key = config.secret_key
                self.gateway_clients[config.gateway] = stripe
                
            elif config.gateway == PaymentGateway.WISE:
                self.gateway_clients[config.gateway] = WiseAPI(
                    api_key=config.api_key,
                    sandbox=config.sandbox_mode
                )
                
            self.logger.info(f"Gateway {config.gateway.value} configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure gateway {config.gateway.value}: {str(e)}")
            raise PaymentError(f"Gateway configuration failed: {str(e)}")
    
    async def process_payment(
        self, 
        request: PaymentRequest,
        session: AsyncSession
    ) -> PaymentResponse:
        """Process payment through specified gateway"""



        try:
            # Validate gateway configuration
            if request.gateway not in self.gateway_configs:
                raise PaymentError(f"Gateway {request.gateway.value} not configured")
            
            config = self.gateway_configs[request.gateway]
            
            # Calculate fees
            fees = self._calculate_fees(request.amount, config)
            net_amount = request.amount - fees
            
            # Process payment based on gateway
            if request.gateway == PaymentGateway.STRIPE:
                response = await self._process_stripe_payment(request, config)
            elif request.gateway == PaymentGateway.WISE:
                response = await self._process_wise_payment(request, config)
            elif request.gateway == PaymentGateway.PAYPAL:
                response = await self._process_paypal_payment(request, config)
            else:
                raise PaymentError(f"Unsupported gateway: {request.gateway.value}")
            
            # Store payment record
            payment = await self._store_payment_record(
                request, response, fees, net_amount, session
            )
            
            return PaymentResponse(
                payment_id=payment.id,
                status=PaymentStatus(response['status']),
                gateway_transaction_id=response.get('transaction_id'),
                amount=request.amount,
                currency=request.currency,
                fees=fees,
                net_amount=net_amount,
                created_at=payment.created_at,
                estimated_arrival=response.get('estimated_arrival'),
                tracking_url=response.get('tracking_url')
            )
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {str(e)}")
            raise PaymentError(f"Payment processing failed: {str(e)}")
    
    async def _process_stripe_payment(
        self, 
        request: PaymentRequest, 
        config: PaymentConfig
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""



        try:
            # Create Stripe transfer
            transfer = stripe.Transfer.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.value.lower(),
                destination=request.recipient_email,
                description=request.description or "IA Influencer Agent payout",
                metadata=request.metadata
            )
            
            return {
                'status': 'processing',
                'transaction_id': transfer.id,
                'estimated_arrival': datetime.now() + timedelta(days=1)
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe payment failed: {str(e)}")
    
    async def _process_wise_payment(
        self, 
        request: PaymentRequest, 
        config: PaymentConfig
    ) -> Dict[str, Any]:
        """Process payment through Wise (formerly TransferWise)"""



        try:
            wise_client = self.gateway_clients[PaymentGateway.WISE]
            
            # Create recipient
            recipient = await wise_client.create_recipient(
                email=request.recipient_email,
                bank_details=request.recipient_bank_details
            )
            
            # Create transfer
            transfer = await wise_client.create_transfer(
                recipient_id=recipient['id'],
                amount=float(request.amount),
                currency=request.currency.value,
                reference=request.description or "IA Influencer Agent payout"
            )
            
            return {
                'status': 'processing',
                'transaction_id': transfer['id'],
                'tracking_url': transfer.get('tracking_url'),
                'estimated_arrival': datetime.now() + timedelta(days=2)
            }
            
        except Exception as e:
            raise PaymentError(f"Wise payment failed: {str(e)}")
    
    async def _process_paypal_payment(
        self, 
        request: PaymentRequest, 
        config: PaymentConfig
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""



        try:
            # PayPal payout implementation
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": f"payout_{int(datetime.now().timestamp())}",
                    "email_subject": "IA Influencer Agent Payout",
                    "email_message": "Your revenue payout from IA Influencer Agent"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(request.amount),
                        "currency": request.currency.value
                    },
                    "receiver": request.recipient_email,
                    "note": request.description or "IA Influencer Agent payout"
                }]
            }
            
            # Execute PayPal payout (mock implementation)
            return {
                'status': 'processing',
                'transaction_id': f"paypal_{int(datetime.now().timestamp())}",
                'estimated_arrival': datetime.now() + timedelta(hours=24)
            }
            
        except Exception as e:
            raise PaymentError(f"PayPal payment failed: {str(e)}")
    
    def _calculate_fees(self, amount: Decimal, config: PaymentConfig) -> Decimal:
        """Calculate payment processing fees"""
        percentage_fee = amount * (config.fee_percentage / 100)
        total_fee = percentage_fee + config.fixed_fee
        return min(total_fee, amount * Decimal("0.05"))  # Cap at 5%
    
    async def _store_payment_record(
        self,
        request: PaymentRequest,
        response: Dict[str, Any],
        fees: Decimal,
        net_amount: Decimal,
        session: AsyncSession
    ) -> Payment:
        """Store payment record in database"""
        payment = Payment(
            user_id=request.user_id,
            gateway=request.gateway.value,
            amount=request.amount,
            currency=request.currency.value,
            fees=fees,
            net_amount=net_amount,
            status=response['status'],
            gateway_transaction_id=response.get('transaction_id'),
            description=request.description,
            metadata=request.metadata
        )
        
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        
        return payment
    
    async def verify_webhook(
        self, 
        payload: str, 
        signature: str, 
        gateway: PaymentGateway
    ) -> bool:
        """Verify webhook signature for security"""



        try:
            config = self.gateway_configs.get(gateway)
            if not config:
                return False
            
            # Verify signature
            expected_signature = hmac.new(
                config.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Webhook verification failed: {str(e)}")
            return False
    
    async def get_payment_status(
        self, 
        payment_id: str, 
        session: AsyncSession
    ) -> Optional[PaymentResponse]:
        """Get payment status by ID"""



        try:
            payment = await session.get(Payment, payment_id)
            if not payment:
                return None
            
            return PaymentResponse(
                payment_id=payment.id,
                status=PaymentStatus(payment.status),
                gateway_transaction_id=payment.gateway_transaction_id,
                amount=payment.amount,
                currency=Currency(payment.currency),
                fees=payment.fees,
                net_amount=payment.net_amount,
                created_at=payment.created_at
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get payment status: {str(e)}")
            return None
    
    async def cancel_payment(
        self, 
        payment_id: str, 
        session: AsyncSession
    ) -> bool:
        """Cancel pending payment"""



        try:
            payment = await session.get(Payment, payment_id)
            if not payment or payment.status != PaymentStatus.PENDING.value:
                return False
            
            # Cancel payment at gateway level
            gateway = PaymentGateway(payment.gateway)
            if gateway == PaymentGateway.STRIPE:
                stripe.Transfer.cancel(payment.gateway_transaction_id)
            
            # Update status
            payment.status = PaymentStatus.CANCELLED.value
            await session.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel payment: {str(e)}")
            return False


class PaymentWebhookHandler:
    """Handle payment gateway webhooks"""
    
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
        self.logger = logging.getLogger(__name__)
    
    async def handle_stripe_webhook(
        self, 
        payload: str, 
        signature: str,
        session: AsyncSession
    ) -> bool:
        """Handle Stripe webhook events"""



        try:
            if not await self.payment_processor.verify_webhook(
                payload, signature, PaymentGateway.STRIPE
            ):
                return False
            
            # Process webhook event
            import json
            event = json.loads(payload)
            
            if event['type'] == 'transfer.updated':
                await self._update_payment_status(
                    event['data']['object']['id'],
                    event['data']['object']['status'],
                    session
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Stripe webhook handling failed: {str(e)}")
            return False
    
    async def _update_payment_status(
        self,
        transaction_id: str,
        status: str,
        session: AsyncSession
    ) -> None:
        """Update payment status from webhook"""



        try:
            # Find payment by transaction ID
            from sqlalchemy import select
            result = await session.execute(
                select(Payment).where(
                    Payment.gateway_transaction_id == transaction_id
                )
            )
            payment = result.scalar_one_or_none()
            
            if payment:
                payment.status = status
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update payment status: {str(e)}")
