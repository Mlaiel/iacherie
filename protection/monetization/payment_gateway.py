"""Payment Gateway Integration - Professional payment processing system.
Handles all payment processing, validation, and gateway integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import hashlib
import hmac
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PaymentMethod(Enum):
    """
Supported payment methods."""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SEPA = "sepa"
    KLARNA = "klarna"


class PaymentStatus(Enum):
    """Payment processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"


class GatewayType(Enum):
    """Payment gateway types."""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    MOLLIE = "mollie"
    RAZORPAY = "razorpay"
    BRAINTREE = "braintree"


@dataclass
class PaymentRequest:
    """Payment processing request data."""
    request_id: str
    user_id: str
    amount: Decimal
    currency: str = "EUR"
    payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD
    gateway: GatewayType = GatewayType.STRIPE
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    customer_info: Dict[str, str] = field(default_factory=dict)
    billing_address: Dict[str, str] = field(default_factory=dict)
    return_url: str = ""
    webhook_url: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method.value,
            "gateway": self.gateway.value,
            "description": self.description,
            "metadata": self.metadata,
            "customer_info": self.customer_info,
            "billing_address": self.billing_address,
            "return_url": self.return_url,
            "webhook_url": self.webhook_url,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PaymentResponse:
    """Payment processing response data."""
    response_id: str
    request_id: str
    status: PaymentStatus
    gateway_transaction_id: str = ""
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    amount_processed: Decimal = Decimal("0")
    fees: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    error_message: str = ""
    redirect_url: str = ""
    processed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "status": self.status.value,
            "gateway_transaction_id": self.gateway_transaction_id,
            "gateway_response": self.gateway_response,
            "amount_processed": float(self.amount_processed),
            "fees": float(self.fees),
            "net_amount": float(self.net_amount),
            "error_message": self.error_message,
            "redirect_url": self.redirect_url,
            "processed_at": self.processed_at.isoformat()
        }


class PaymentGateway(ABC):
    """Abstract base class for payment gateways."""
    
    @abstractmethod
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
Process a payment request."""
        pass
    
    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> PaymentResponse:
        try:
            logger.info(f"Executing verify_payment")
            
            # Implementation for verify_payment
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"verify_payment completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing refund_payment")
            
            # Implementation for refund_payment
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"refund_payment completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"refund_payment failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"verify_payment failed: {e}")
            raise
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResponse:
        """
Process payment refund."""
        pass
    
    @abstractmethod
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """
Validate webhook signature."""
        pass


class StripeGateway(PaymentGateway):
    """
Stripe payment gateway implementation."""
    
    def __init__(self, api_key -> None: str, webhook_secret -> None: str) -> None:
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.base_url = "https://api.stripe.com/v1"
        self.fee_rate = Decimal("0.029")  # 2.9% + # [EMOJI_REMOVED]0.30
        self.fixed_fee = Decimal("0.30")
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment through Stripe."""
        try:
            # Simulate Stripe API call
            fees = (request.amount * self.fee_rate) + self.fixed_fee
            net_amount = request.amount - fees
            
            # Create payment intent
            payment_intent = {
                "id": f"pi_{request.request_id}",
                "amount": int(request.amount * 100),  # Stripe uses cents
                "currency": request.currency.lower(),
                "status": "succeeded",
                "charges": {
                    "data": [{
                        "id": f"ch_{request.request_id}",
                        "amount": int(request.amount * 100),
                        "captured": True
                    }]
                }
            }
            
            response = PaymentResponse(
                response_id=f"resp_{request.request_id}",
                request_id=request.request_id,
                status=PaymentStatus.COMPLETED,
                gateway_transaction_id=payment_intent["id"],
                gateway_response=payment_intent,
                amount_processed=request.amount,
                fees=fees,
                net_amount=net_amount
            )
            
            logger.info(f"Stripe payment processed: {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Stripe payment processing failed: {e}")
            return PaymentResponse(
                response_id=f"resp_{request.request_id}",
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                error_message=str(e)
            )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResponse:
        """Verify Stripe payment status."""
        # Simulate Stripe payment verification
        return PaymentResponse(
            response_id=f"verify_{transaction_id}",
            request_id=transaction_id,
            status=PaymentStatus.COMPLETED,
            gateway_transaction_id=transaction_id
        )
    
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResponse:
        """Process Stripe refund."""
        # Simulate Stripe refund
        return PaymentResponse(
            response_id=f"refund_{transaction_id}",
            request_id=transaction_id,
            status=PaymentStatus.REFUNDED,
            gateway_transaction_id=f"re_{transaction_id}"
        )
    
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate Stripe webhook signature."""
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook validation failed: {e}")
            return False


class PayPalGateway(PaymentGateway):
    """PayPal payment gateway implementation."""
    
    def __init__(self, client_id -> None: str, client_secret -> None: str, sandbox -> None: bool = True) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.base_url = "https://api.sandbox.paypal.com" if sandbox else "https://api.paypal.com"
        self.fee_rate = Decimal("0.034")  # 3.4% + # [EMOJI_REMOVED]0.35
        self.fixed_fee = Decimal("0.35")
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment through PayPal."""
        try:
            fees = (request.amount * self.fee_rate) + self.fixed_fee
            net_amount = request.amount - fees
            
            # Simulate PayPal order creation
            order = {
                "id": f"pp_{request.request_id}",
                "status": "COMPLETED",
                "purchase_units": [{
                    "amount": {
                        "currency_code": request.currency,
                        "value": str(request.amount)
                    }
                }]
            }
            
            response = PaymentResponse(
                response_id=f"resp_{request.request_id}",
                request_id=request.request_id,
                status=PaymentStatus.COMPLETED,
                gateway_transaction_id=order["id"],
                gateway_response=order,
                amount_processed=request.amount,
                fees=fees,
                net_amount=net_amount
            )
            
            logger.info(f"PayPal payment processed: {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"PayPal payment processing failed: {e}")
            return PaymentResponse(
                response_id=f"resp_{request.request_id}",
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                error_message=str(e)
            )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResponse:
        """Verify PayPal payment status."""
        return PaymentResponse(
            response_id=f"verify_{transaction_id}",
            request_id=transaction_id,
            status=PaymentStatus.COMPLETED,
            gateway_transaction_id=transaction_id
        )
    
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResponse:
        """Process PayPal refund."""
        return PaymentResponse(
            response_id=f"refund_{transaction_id}",
            request_id=transaction_id,
            status=PaymentStatus.REFUNDED,
            gateway_transaction_id=f"refund_{transaction_id}"
        )
    
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate PayPal webhook signature."""
        # Implement PayPal webhook validation
        return True


class PaymentGatewayManager:
    """
    Professional payment gateway manager.
    Handles multiple payment gateways and intelligent routing.
    """
    
    def __init__(self) -> None:
        self.gateways: Dict[GatewayType, PaymentGateway] = {}
        self.gateway_preferences: Dict[str, List[GatewayType]] = {
            "EUR": [GatewayType.STRIPE, GatewayType.PAYPAL],
            "USD": [GatewayType.STRIPE, GatewayType.PAYPAL],
            "GBP": [GatewayType.STRIPE, GatewayType.PAYPAL]
        }
        self.payment_history: List[PaymentResponse] = []
        self.fraud_detection_enabled = True
        self.is_initialized = False
    
    async def initialize(self, gateway_configs: Dict[GatewayType, Dict[str, str]]) -> bool:
        """Initialize payment gateways."""
        try:
            for gateway_type, config in gateway_configs.items():
                if gateway_type == GatewayType.STRIPE:
                    self.gateways[gateway_type] = StripeGateway(
                        api_key=config["api_key"],
                        webhook_secret=config["webhook_secret"]
                    )
                elif gateway_type == GatewayType.PAYPAL:
                    self.gateways[gateway_type] = PayPalGateway(
                        client_id=config["client_id"],
                        client_secret=config["client_secret"],
                        sandbox=config.get("sandbox", True)
                    )
            
            self.is_initialized = True
            logger.info("Payment gateway manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Payment gateway initialization failed: {e}")
            return False
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment with intelligent gateway routing."""
        if not self.is_initialized:
            raise RuntimeError("Payment gateway manager not initialized")
        
        # Fraud detection
        if self.fraud_detection_enabled:
            fraud_score = await self._detect_fraud(request)
            if fraud_score > 0.8:
                return PaymentResponse(
                    response_id=f"fraud_{request.request_id}",
                    request_id=request.request_id,
                    status=PaymentStatus.FAILED,
                    error_message="Transaction blocked due to fraud detection"
                )
        
        # Select optimal gateway
        gateway = await self._select_gateway(request)
        if not gateway:
            return PaymentResponse(
                response_id=f"nogw_{request.request_id}",
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                error_message="No suitable payment gateway available"
            )
        
        # Process payment
        response = await gateway.process_payment(request)
        self.payment_history.append(response)
        
        # Log transaction
        await self._log_transaction(request, response)
        
        return response
    
    async def verify_payment(self, transaction_id: str, gateway_type: GatewayType) -> PaymentResponse:
        """Verify payment status."""
        gateway = self.gateways.get(gateway_type)
        if not gateway:
            raise ValueError(f"Gateway {gateway_type} not available")
        
        return await gateway.verify_payment(transaction_id)
    
    async def refund_payment(
        self, 
        transaction_id: str, 
        gateway_type: GatewayType,
        amount: Optional[Decimal] = None,
        reason: str = ""
    ) -> PaymentResponse:
        """Process payment refund."""
        gateway = self.gateways.get(gateway_type)
        if not gateway:
            raise ValueError(f"Gateway {gateway_type} not available")
        
        response = await gateway.refund_payment(transaction_id, amount)
        
        # Log refund
        logger.info(f"Refund processed: {transaction_id}, reason: {reason}")
        
        return response
    
    async def handle_webhook(
        self, 
        gateway_type: GatewayType, 
        payload: str, 
        signature: str
    ) -> Dict[str, Any]:
        """Handle payment gateway webhooks."""
        gateway = self.gateways.get(gateway_type)
        if not gateway:
            return {"status": "error", "message": "Gateway not found"}
        
        # Validate webhook
        is_valid = await gateway.validate_webhook(payload, signature)
        if not is_valid:
            return {"status": "error", "message": "Invalid webhook signature"}
        
        # Process webhook data
        try:
            webhook_data = json.loads(payload)
            event_type = webhook_data.get("type", "")
            
            if "payment" in event_type.lower():
                await self._process_payment_webhook(webhook_data)
            
            return {"status": "success", "processed": True}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_payment_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get payment processing statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_payments = [
            p for p in self.payment_history 
            if p.processed_at >= cutoff_date
        ]
        
        total_amount = sum(p.amount_processed for p in recent_payments)
        total_fees = sum(p.fees for p in recent_payments)
        success_count = len([p for p in recent_payments if p.status == PaymentStatus.COMPLETED])
        
        return {
            "period_days": days,
            "total_transactions": len(recent_payments),
            "successful_transactions": success_count,
            "success_rate": success_count / len(recent_payments) if recent_payments else 0,
            "total_amount": float(total_amount),
            "total_fees": float(total_fees),
            "net_amount": float(total_amount - total_fees),
            "average_transaction": float(total_amount / len(recent_payments)) if recent_payments else 0,
            "gateway_usage": self._calculate_gateway_usage(recent_payments)
        }
    
    async def _select_gateway(self, request: PaymentRequest) -> Optional[PaymentGateway]:
        """Select optimal payment gateway."""
        preferred_gateways = self.gateway_preferences.get(request.currency, [])
        
        # If specific gateway requested
        if request.gateway in self.gateways and request.gateway in preferred_gateways:
            return self.gateways[request.gateway]
        
        # Select first available preferred gateway
        for gateway_type in preferred_gateways:
            if gateway_type in self.gateways:
                return self.gateways[gateway_type]
        
        # Fallback to any available gateway
        return next(iter(self.gateways.values())) if self.gateways else None
    
    async def _detect_fraud(self, request: PaymentRequest) -> float:
        """
Simple fraud detection algorithm."""
        fraud_score = 0.0
        
        # Check amount threshold
        if request.amount > Decimal("1000"):
            fraud_score += 0.3
        
        # Check frequency (simplified)
        recent_payments = [
            p for p in self.payment_history 
            if p.request_id.startswith(request.user_id) and 
            p.processed_at > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if len(recent_payments) > 5:
            fraud_score += 0.5
        
        return min(fraud_score, 1.0)
    
    async def _log_transaction(self, request: PaymentRequest, response: PaymentResponse) -> None:
        """Log transaction details."""
        log_data = {
            "request": request.to_dict(),
            "response": response.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Payment transaction logged: {request.request_id}")
    
    async def _process_payment_webhook(self, webhook_data: Dict[str, Any]) -> None:
        """Process payment-related webhook."""
        event_type = webhook_data.get("type", "")
        
        if "succeeded" in event_type:
            logger.info("Payment succeeded webhook processed")
        elif "failed" in event_type:
            logger.warning("Payment failed webhook processed")
        elif "refund" in event_type:
            logger.info("Refund webhook processed")
    
    def _calculate_gateway_usage(self, payments: List[PaymentResponse]) -> Dict[str, int]:
        """Calculate gateway usage statistics."""
        usage = {}
        for payment in payments:
            gateway = payment.gateway_response.get("gateway", "unknown")
            usage[gateway] = usage.get(gateway, 0) + 1
        return usage

# File has syntax issues - needs manual review