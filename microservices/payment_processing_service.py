"""
Payment Processing Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Payment Processing Service
Multi-gateway payment processing service for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import uuid
import hashlib
import json
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import aiohttp
import hmac

logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    DIRECT_DEBIT = "direct_debit"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    EXPIRED = "expired"

class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    BTC = "BTC"
    ETH = "ETH"

class PaymentGateway(Enum):
    """Payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    AUTHORIZE_NET = "authorize_net"
    BRAINTREE = "braintree"
    ADYEN = "adyen"
    WORLDPAY = "worldpay"
    MOCK = "mock"

@dataclass
class PaymentRequest:
    """Payment request data"""
    payment_id: str
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    gateway: PaymentGateway
    customer_id: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    billing_address: Dict[str, str] = field(default_factory=dict)
    shipping_address: Dict[str, str] = field(default_factory=dict)
    payment_details: Dict[str, Any] = field(default_factory=dict)
    webhook_url: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    expires_at: Optional[float] = None
    idempotency_key: Optional[str] = None

@dataclass
class PaymentResponse:
    """Payment response data"""
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: Currency
    gateway_transaction_id: Optional[str] = None
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    fees: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    message: str = ""
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class RefundRequest:
    """Refund request data"""
    refund_id: str
    payment_id: str
    amount: Optional[Decimal] = None  # None for full refund
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RefundResponse:
    """Refund response data"""
    refund_id: str
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    gateway_refund_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)

@dataclass
class GatewayConfig:
    """Payment gateway configuration"""
    gateway: PaymentGateway
    api_key: str
    secret_key: str
    webhook_secret: str
    sandbox: bool = True
    supported_methods: List[PaymentMethod] = field(default_factory=list)
    supported_currencies: List[Currency] = field(default_factory=list)
    fee_percentage: Decimal = Decimal('2.9')
    fee_fixed: Decimal = Decimal('0.30')
    metadata: Dict[str, Any] = field(default_factory=dict)

class PaymentGatewayInterface:
    """Base interface for payment gateways"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize gateway connection"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment"""
        raise NotImplementedError
    
    async def refund_payment(self, refund_request: RefundRequest) -> RefundResponse:
        """Process a refund"""
        raise NotImplementedError
    
    async def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get payment status"""
        raise NotImplementedError
    
    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        raise NotImplementedError

class MockPaymentGateway(PaymentGatewayInterface):
    """Mock payment gateway for testing"""
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Mock payment processing"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate random failures for testing
        import random
        if random.random() < 0.1:  # 10% failure rate
            return PaymentResponse(
                payment_id=request.payment_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                error_code="MOCK_ERROR",
                error_message="Mock payment failure for testing"
            )
        
        # Calculate fees
        fees = request.amount * self.config.fee_percentage / 100 + self.config.fee_fixed
        net_amount = request.amount - fees
        
        return PaymentResponse(
            payment_id=request.payment_id,
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            gateway_transaction_id=f"mock_txn_{uuid.uuid4().hex[:12]}",
            fees=fees,
            net_amount=net_amount,
            message="Mock payment successful"
        )
    
    async def refund_payment(self, refund_request: RefundRequest) -> RefundResponse:
        """Mock refund processing"""
        await asyncio.sleep(0.1)
        
        return RefundResponse(
            refund_id=refund_request.refund_id,
            payment_id=refund_request.payment_id,
            status=PaymentStatus.REFUNDED,
            amount=refund_request.amount or Decimal('0.00'),
            gateway_refund_id=f"mock_ref_{uuid.uuid4().hex[:12]}"
        )
    
    async def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Mock status check"""
        return PaymentResponse(
            payment_id=payment_id,
            status=PaymentStatus.COMPLETED,
            amount=Decimal('0.00'),
            currency=Currency.USD
        )
    
    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Mock webhook verification"""
        return True

class StripePaymentGateway(PaymentGatewayInterface):
    """Stripe payment gateway implementation"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        super().__init__(config)
        self.base_url = "https://api.stripe.com/v1"
        if config.sandbox:
            # Stripe uses the same URL but different keys for test mode
            pass
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment through Stripe"""
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(request.amount * 100)
            
            # Prepare payment intent data
            payment_data = {
                "amount": amount_cents,
                "currency": request.currency.value.lower(),
                "payment_method_types": ["card"],
                "description": request.description,
                "metadata": request.metadata
            }
            
            if request.customer_id:
                payment_data["customer"] = request.customer_id
            
            # Create payment intent
            headers = {
                "Authorization": f"Bearer {self.config.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.session.post(
                f"{self.base_url}/payment_intents",
                data=payment_data,
                headers=headers
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    # Calculate fees (Stripe's standard rate)
                    fees = request.amount * self.config.fee_percentage / 100 + self.config.fee_fixed
                    net_amount = request.amount - fees
                    
                    return PaymentResponse(
                        payment_id=request.payment_id,
                        status=self._map_stripe_status(result.get("status")),
                        amount=request.amount,
                        currency=request.currency,
                        gateway_transaction_id=result.get("id"),
                        gateway_response=result,
                        fees=fees,
                        net_amount=net_amount,
                        message="Payment intent created successfully"
                    )
                else:
                    return PaymentResponse(
                        payment_id=request.payment_id,
                        status=PaymentStatus.FAILED,
                        amount=request.amount,
                        currency=request.currency,
                        error_code=result.get("error", {}).get("code"),
                        error_message=result.get("error", {}).get("message"),
                        gateway_response=result
                    )
        
        except Exception as e:
            logger.error("Stripe payment processing error: %s", e)
            return PaymentResponse(
                payment_id=request.payment_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                error_message=str(e)
            )
    
    async def refund_payment(self, refund_request: RefundRequest) -> RefundResponse:
        """Process refund through Stripe"""
        try:
            refund_data = {
                "payment_intent": refund_request.payment_id,
                "reason": refund_request.reason or "requested_by_customer"
            }
            
            if refund_request.amount:
                refund_data["amount"] = int(refund_request.amount * 100)
            
            headers = {
                "Authorization": f"Bearer {self.config.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.session.post(
                f"{self.base_url}/refunds",
                data=refund_data,
                headers=headers
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    amount = Decimal(result.get("amount", 0)) / 100
                    return RefundResponse(
                        refund_id=refund_request.refund_id,
                        payment_id=refund_request.payment_id,
                        status=PaymentStatus.REFUNDED,
                        amount=amount,
                        gateway_refund_id=result.get("id")
                    )
                else:
                    return RefundResponse(
                        refund_id=refund_request.refund_id,
                        payment_id=refund_request.payment_id,
                        status=PaymentStatus.FAILED,
                        amount=Decimal('0.00')
                    )
        
        except Exception as e:
            logger.error("Stripe refund processing error: %s", e)
            return RefundResponse(
                refund_id=refund_request.refund_id,
                payment_id=refund_request.payment_id,
                status=PaymentStatus.FAILED,
                amount=Decimal('0.00')
            )
    
    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            expected_sig = hmac.new(
                self.config.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_sig)
        except Exception:
            return False
    
    def _map_stripe_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe status to internal status"""
        mapping = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PENDING,
            "processing": PaymentStatus.PROCESSING,
            "succeeded": PaymentStatus.COMPLETED,
            "canceled": PaymentStatus.CANCELLED
        }
        return mapping.get(stripe_status, PaymentStatus.FAILED)

class PaymentProcessingService:
    """
    Enterprise Payment Processing Service
    
    Provides comprehensive payment processing with:
    - Multiple payment gateways
    - Automatic failover
    - Transaction management
    - Fraud detection
    - Webhook handling
    - Comprehensive logging and monitoring
    """
    
    def __init__(self) -> None:
        """Initialize payment processing service"""
        self.gateways: Dict[PaymentGateway, PaymentGatewayInterface] = {}
        self.gateway_configs: Dict[PaymentGateway, GatewayConfig] = {}
        self.payment_history: Dict[str, PaymentResponse] = {}
        self.refund_history: Dict[str, RefundResponse] = {}
        
        # Fraud detection
        self.fraud_patterns: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "attempts": 0,
            "failures": 0,
            "last_attempt": 0,
            "blocked": False
        })
        
        # Configuration
        self.config = {
            "default_gateway": PaymentGateway.MOCK,
            "failover_enabled": True,
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "fraud_detection_enabled": True,
            "max_attempts_per_hour": 10,
            "failure_threshold": 0.5,
            "webhook_timeout": 30.0,
            "transaction_timeout": 300.0
        }
        
        # Performance tracking
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "total_amount": Decimal('0.00'),
            "total_fees": Decimal('0.00'),
            "avg_processing_time": 0.0,
            "last_success": 0,
            "last_failure": 0
        })
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        logger.info("PaymentProcessingService initialized")
    
    async def start(self) -> None:
        """Start the payment processing service"""
        try:
            # Initialize gateways
            for gateway in self.gateways.values():
                await gateway.initialize()
            
            logger.info("PaymentProcessingService started successfully")
        except Exception as e:
            logger.error("Failed to start PaymentProcessingService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the payment processing service"""
        try:
            self.shutdown_event.set()
            
            # Cleanup gateways
            for gateway in self.gateways.values():
                await gateway.cleanup()
            
            logger.info("PaymentProcessingService stopped successfully")
        except Exception as e:
            logger.error("Error stopping PaymentProcessingService: %s", e)
    
    async def register_gateway(self, config -> None: GatewayConfig) -> None:
        """Register a payment gateway"""
        async with self._lock:
            if config.gateway == PaymentGateway.STRIPE:
                gateway = StripePaymentGateway(config)
            elif config.gateway == PaymentGateway.MOCK:
                gateway = MockPaymentGateway(config)
            else:
                # Add more gateway implementations as needed
                gateway = MockPaymentGateway(config)
            
            self.gateways[config.gateway] = gateway
            self.gateway_configs[config.gateway] = config
            
            if gateway.session is None:
                await gateway.initialize()
        
        logger.info("Registered payment gateway: %s", config.gateway.value)
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment with automatic failover"""
        start_time = time.time()
        
        # Fraud detection
        if self.config["fraud_detection_enabled"]:
            if not await self._check_fraud_protection(request):
                return PaymentResponse(
                    payment_id=request.payment_id,
                    status=PaymentStatus.FAILED,
                    amount=request.amount,
                    currency=request.currency,
                    error_code="FRAUD_DETECTED",
                    error_message="Transaction blocked by fraud protection"
                )
        
        # Try primary gateway first
        primary_gateway = request.gateway
        gateways_to_try = [primary_gateway]
        
        # Add failover gateways if enabled
        if self.config["failover_enabled"]:
            for gateway in self.gateways.keys():
                if gateway != primary_gateway and gateway not in gateways_to_try:
                    gateways_to_try.append(gateway)
        
        last_error = None
        
        for gateway_type in gateways_to_try:
            if gateway_type not in self.gateways:
                continue
            
            gateway = self.gateways[gateway_type]
            
            for attempt in range(self.config["retry_attempts"]):
                try:
                    # Create a copy of request with the current gateway
                    gateway_request = PaymentRequest(
                        payment_id=request.payment_id,
                        amount=request.amount,
                        currency=request.currency,
                        payment_method=request.payment_method,
                        gateway=gateway_type,
                        customer_id=request.customer_id,
                        description=request.description,
                        metadata=request.metadata,
                        billing_address=request.billing_address,
                        shipping_address=request.shipping_address,
                        payment_details=request.payment_details,
                        webhook_url=request.webhook_url,
                        return_url=request.return_url,
                        cancel_url=request.cancel_url,
                        expires_at=request.expires_at,
                        idempotency_key=request.idempotency_key
                    )
                    
                    response = await gateway.process_payment(gateway_request)
                    
                    # Update metrics
                    processing_time = time.time() - start_time
                    await self._update_metrics(gateway_type, response, processing_time)
                    
                    # Store payment history
                    async with self._lock:
                        self.payment_history[request.payment_id] = response
                    
                    # Update fraud tracking
                    await self._update_fraud_tracking(request, response)
                    
                    if response.status in [PaymentStatus.COMPLETED, PaymentStatus.PROCESSING]:
                        logger.info(
                            "Payment processed successfully: %s via %s",
                            request.payment_id, gateway_type.value
                        )
                        return response
                    else:
                        last_error = response.error_message
                        break  # Don't retry on this gateway
                
                except Exception as e:
                    last_error = str(e)
                    logger.warning(
                        "Payment attempt %d failed on %s: %s",
                        attempt + 1, gateway_type.value, e
                    )
                    
                    if attempt < self.config["retry_attempts"] - 1:
                        await asyncio.sleep(self.config["retry_delay"])
        
        # All gateways failed
        failed_response = PaymentResponse(
            payment_id=request.payment_id,
            status=PaymentStatus.FAILED,
            amount=request.amount,
            currency=request.currency,
            error_message=f"All payment gateways failed. Last error: {last_error}"
        )
        
        # Update metrics for failure
        processing_time = time.time() - start_time
        await self._update_metrics(primary_gateway, failed_response, processing_time)
        
        # Store failed payment
        async with self._lock:
            self.payment_history[request.payment_id] = failed_response
        
        logger.error("Payment processing failed for %s: %s", request.payment_id, last_error)
        return failed_response
    
    async def refund_payment(self, refund_request: RefundRequest) -> RefundResponse:
        """Process a payment refund"""
        async with self._lock:
            # Get original payment
            original_payment = self.payment_history.get(refund_request.payment_id)
            if not original_payment:
                return RefundResponse(
                    refund_id=refund_request.refund_id,
                    payment_id=refund_request.payment_id,
                    status=PaymentStatus.FAILED,
                    amount=Decimal('0.00')
                )
            
            # Determine gateway from original payment
            gateway_response = original_payment.gateway_response
            gateway_type = None
            
            # Find which gateway processed the original payment
            for gw_type, gw in self.gateways.items():
                if hasattr(gw, 'base_url') and 'stripe' in str(gw_type).lower():
                    if gateway_response.get('object') == 'payment_intent':
                        gateway_type = gw_type
                        break
                elif gw_type == PaymentGateway.MOCK:
                    if 'mock_txn_' in str(original_payment.gateway_transaction_id):
                        gateway_type = gw_type
                        break
            
            if not gateway_type or gateway_type not in self.gateways:
                return RefundResponse(
                    refund_id=refund_request.refund_id,
                    payment_id=refund_request.payment_id,
                    status=PaymentStatus.FAILED,
                    amount=Decimal('0.00')
                )
        
        try:
            gateway = self.gateways[gateway_type]
            response = await gateway.refund_payment(refund_request)
            
            # Store refund history
            async with self._lock:
                self.refund_history[refund_request.refund_id] = response
            
            logger.info("Refund processed: %s", refund_request.refund_id)
            return response
            
        except Exception as e:
            logger.error("Refund processing failed: %s", e)
            return RefundResponse(
                refund_id=refund_request.refund_id,
                payment_id=refund_request.payment_id,
                status=PaymentStatus.FAILED,
                amount=Decimal('0.00')
            )
    
    async def get_payment_status(self, payment_id: str) -> Optional[PaymentResponse]:
        """Get payment status"""
        async with self._lock:
            return self.payment_history.get(payment_id)
    
    async def handle_webhook(
        self,
        gateway_type: PaymentGateway,
        payload: str,
        signature: str
    ) -> bool:
        """Handle payment gateway webhook"""
        try:
            if gateway_type not in self.gateways:
                logger.warning("Webhook received for unregistered gateway: %s", gateway_type)
                return False
            
            gateway = self.gateways[gateway_type]
            
            # Verify webhook signature
            if not await gateway.verify_webhook(payload, signature):
                logger.warning("Invalid webhook signature for %s", gateway_type)
                return False
            
            # Process webhook data
            webhook_data = json.loads(payload)
            await self._process_webhook_event(gateway_type, webhook_data)
            
            logger.info("Webhook processed successfully for %s", gateway_type)
            return True
            
        except Exception as e:
            logger.error("Webhook processing error: %s", e)
            return False
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        async with self._lock:
            total_metrics = {
                "total_transactions": 0,
                "successful_transactions": 0,
                "failed_transactions": 0,
                "success_rate": 0.0,
                "total_amount": Decimal('0.00'),
                "total_fees": Decimal('0.00'),
                "gateway_metrics": {}
            }
            
            for gateway_type, metrics in self.metrics.items():
                total_metrics["total_transactions"] += metrics["total_transactions"]
                total_metrics["successful_transactions"] += metrics["successful_transactions"]
                total_metrics["failed_transactions"] += metrics["failed_transactions"]
                total_metrics["total_amount"] += metrics["total_amount"]
                total_metrics["total_fees"] += metrics["total_fees"]
                
                total_metrics["gateway_metrics"][gateway_type.value] = dict(metrics)
            
            if total_metrics["total_transactions"] > 0:
                total_metrics["success_rate"] = (
                    total_metrics["successful_transactions"] / total_metrics["total_transactions"]
                )
            
            return total_metrics
    
    async def _check_fraud_protection(self, request: PaymentRequest) -> bool:
        """Check fraud protection rules"""
        current_time = time.time()
        
        # Check by customer ID
        customer_pattern = self.fraud_patterns[f"customer_{request.customer_id}"]
        
        # Check if blocked
        if customer_pattern["blocked"]:
            return False
        
        # Check attempts per hour
        if current_time - customer_pattern["last_attempt"] < 3600:  # Within last hour
            if customer_pattern["attempts"] >= self.config["max_attempts_per_hour"]:
                customer_pattern["blocked"] = True
                return False
        else:
            # Reset hourly counter
            customer_pattern["attempts"] = 0
        
        # Check failure rate
        if customer_pattern["attempts"] > 0:
            failure_rate = customer_pattern["failures"] / customer_pattern["attempts"]
            if failure_rate > self.config["failure_threshold"]:
                return False
        
        return True
    
    async def _update_fraud_tracking(self, request -> None: PaymentRequest, response -> None: PaymentResponse) -> None:
        """Update fraud tracking data"""
        customer_pattern = self.fraud_patterns[f"customer_{request.customer_id}"]
        current_time = time.time()
        
        customer_pattern["attempts"] += 1
        customer_pattern["last_attempt"] = current_time
        
        if response.status == PaymentStatus.FAILED:
            customer_pattern["failures"] += 1
    
    async def _update_metrics(
        self,
        gateway_type -> None: PaymentGateway,
        response -> None: PaymentResponse,
        processing_time -> None: float
    ) -> None:
        """Update gateway metrics"""
        metrics = self.metrics[gateway_type]
        current_time = time.time()
        
        metrics["total_transactions"] += 1
        
        if response.status == PaymentStatus.COMPLETED:
            metrics["successful_transactions"] += 1
            metrics["total_amount"] += response.amount
            metrics["total_fees"] += response.fees
            metrics["last_success"] = current_time
        else:
            metrics["failed_transactions"] += 1
            metrics["last_failure"] = current_time
        
        # Update average processing time
        old_avg = metrics["avg_processing_time"]
        count = metrics["total_transactions"]
        metrics["avg_processing_time"] = (old_avg * (count - 1) + processing_time) / count
    
    async def _process_webhook_event(self, gateway_type -> None: PaymentGateway, webhook_data -> None: Dict[str, Any]) -> None:
        """Process webhook event data"""
        # Update payment status based on webhook
        if gateway_type == PaymentGateway.STRIPE:
            await self._process_stripe_webhook(webhook_data)
        elif gateway_type == PaymentGateway.MOCK:
            await self._process_mock_webhook(webhook_data)
    
    async def _process_stripe_webhook(self, webhook_data -> None: Dict[str, Any]) -> None:
        """Process Stripe webhook"""
        event_type = webhook_data.get("type")
        event_data = webhook_data.get("data", {}).get("object", {})
        
        if event_type == "payment_intent.succeeded":
            payment_intent_id = event_data.get("id")
            
            # Find matching payment in history
            async with self._lock:
                for payment_id, payment_response in self.payment_history.items():
                    if payment_response.gateway_transaction_id == payment_intent_id:
                        payment_response.status = PaymentStatus.COMPLETED
                        payment_response.updated_at = time.time()
                        break
        
        elif event_type == "payment_intent.payment_failed":
            payment_intent_id = event_data.get("id")
            
            async with self._lock:
                for payment_id, payment_response in self.payment_history.items():
                    if payment_response.gateway_transaction_id == payment_intent_id:
                        payment_response.status = PaymentStatus.FAILED
                        payment_response.updated_at = time.time()
                        break
    
    async def _process_mock_webhook(self, webhook_data -> None: Dict[str, Any]) -> None:
        """Process mock webhook (for testing)"""
        # Simple mock webhook processing
        pass

# Global payment processing service instance
_payment_service: Optional[PaymentProcessingService] = None

async def get_payment_service() -> PaymentProcessingService:
    """Get global payment processing service instance"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentProcessingService()
        await _payment_service.start()
    return _payment_service

async def shutdown_payment_service() -> None:
    """Shutdown global payment processing service"""
    global _payment_service
    if _payment_service:
        await _payment_service.stop()
        _payment_service = None

if __name__ == "__main__":
    async def test_payment_service() -> None:
        """Test payment processing service functionality"""
        service = PaymentProcessingService()
        await service.start()
        
        try:
            # Register mock gateway
            mock_config = GatewayConfig(
                gateway=PaymentGateway.MOCK,
                api_key="test_key",
                secret_key="test_secret",
                webhook_secret="test_webhook_secret",
                supported_methods=[PaymentMethod.CREDIT_CARD],
                supported_currencies=[Currency.USD, Currency.EUR]
            )
            
            await service.register_gateway(mock_config)
            
            # Test payment
            payment_request = PaymentRequest(
                payment_id=f"pay_{uuid.uuid4().hex[:12]}",
                amount=Decimal('99.99'),
                currency=Currency.USD,
                payment_method=PaymentMethod.CREDIT_CARD,
                gateway=PaymentGateway.MOCK,
                customer_id="customer_123",
                description="Test payment"
            )
            
            response = await service.process_payment(payment_request)
            print(f"Payment result: {response.status.value}, Amount: {response.amount}")
            
            # Test refund
            if response.status == PaymentStatus.COMPLETED:
                refund_request = RefundRequest(
                    refund_id=f"ref_{uuid.uuid4().hex[:12]}",
                    payment_id=payment_request.payment_id,
                    amount=Decimal('50.00'),
                    reason="Customer request"
                )
                
                refund_response = await service.refund_payment(refund_request)
                print(f"Refund result: {refund_response.status.value}, Amount: {refund_response.amount}")
            
            # Get metrics
            metrics = await service.get_service_metrics()
            print(f"Service metrics: {metrics}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_payment_service())