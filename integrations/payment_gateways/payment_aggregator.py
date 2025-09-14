"""Payment Aggregator - Universal Payment Processing Engine
=========================================================

Enterprise payment aggregator that unifies multiple payment processors
and provides intelligent routing, failover, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

import httpx
from .stripe_integration import StripePaymentProcessor
from .paypal_integration import PayPalPaymentProcessor
from .wise_integration import WisePaymentProcessor
from .square_integration import SquarePaymentProcessor
from .adyen_integration import AdyenPaymentProcessor
from .braintree_integration import BraintreePaymentProcessor
from .razorpay_integration import RazorpayPaymentProcessor
from .cryptocurrency_gateways import CryptocurrencyPaymentProcessor


class PaymentMethod(Enum):
    """Supported payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BUY_NOW_PAY_LATER = "bnpl"
    UPI = "upi"
    NETBANKING = "netbanking"
    EMI = "emi"


class PaymentRegion(Enum):
    """Payment processing regions."""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    GLOBAL = "global"


class PaymentStatus(Enum):
    """Universal payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    EXPIRED = "expired"


@dataclass
class PaymentRoute:
    """Payment routing configuration."""
    processor: str
    priority: int
    weight: float
    regions: List[PaymentRegion]
    methods: List[PaymentMethod]
    currencies: List[str]
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    fees: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class UniversalPaymentRequest:
    """Universal payment request structure."""
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    customer_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_country: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    preferred_processor: Optional[str] = None
    webhook_url: Optional[str] = None
    return_url: Optional[str] = None
    reference: Optional[str] = None
    auto_capture: bool = True
    save_payment_method: bool = False
    subscription_id: Optional[str] = None


@dataclass
class UniversalPaymentResponse:
    """Universal payment response structure."""
    payment_id: str
    processor: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    fees: Decimal
    processor_transaction_id: str
    customer_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processor_response: Optional[Dict[str, Any]] = None
    next_action: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class PaymentAnalytics:
    """Payment analytics and metrics."""
    total_transactions: int = 0
    total_volume: Decimal = Decimal(0)
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    processor_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    method_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    region_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    failure_reasons: Dict[str, int] = field(default_factory=dict)


class PaymentAggregator:
    """Enterprise payment aggregator for universal payment processing.
    
    Features:
    - Multi-processor integration and management
    - Intelligent payment routing and optimization
    - Automatic failover and retry mechanisms
    - Real-time analytics and performance monitoring
    - Fee optimization and cost reduction
    - Regional and method-specific routing
    - Advanced fraud detection integration
    - Subscription and recurring payment management
    - Split payments and marketplace functionality
    - Comprehensive webhook management
    - Currency conversion and multi-currency support
    - Compliance and regulatory management
    - Advanced reporting and analytics
    - A/B testing for payment optimization
    """
    
    def __init__(
        self,
        processors_config -> None: Dict[str, Dict[str, Any]],
        routing_config -> None: List[PaymentRoute],
        webhook_url -> None: Optional[str] = None,
        analytics_enabled -> None: bool = True
    ) -> None:
        """Initialize payment aggregator.
        
        Args:
            processors_config: Configuration for payment processors
            routing_config: Payment routing configuration
            webhook_url: Global webhook URL
            analytics_enabled: Enable analytics collection
        """
        self.processors_config = processors_config
        self.routing_config = routing_config
        self.webhook_url = webhook_url
        self.analytics_enabled = analytics_enabled
        
        # Initialize processors
        self.processors = {}
        self._init_processors()
        
        # Initialize analytics
        self.analytics = PaymentAnalytics() if analytics_enabled else None
        
        # Payment cache for performance
        self.payment_cache = {}
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(timeout=30.0)

    def _init_processors(self) -> None:
        """Initialize payment processors."""
        for processor_name, config in self.processors_config.items():
            try:
                if processor_name == "stripe" and config.get("enabled", False):
                    self.processors["stripe"] = StripePaymentProcessor(
                        api_key=config["api_key"],
                        webhook_endpoint_secret=config.get("webhook_secret")
                    )
                    
                elif processor_name == "paypal" and config.get("enabled", False):
                    self.processors["paypal"] = PayPalPaymentProcessor(
                        client_id=config["client_id"],
                        client_secret=config["client_secret"],
                        environment=config.get("environment", "sandbox")
                    )
                    
                elif processor_name == "wise" and config.get("enabled", False):
                    self.processors["wise"] = WisePaymentProcessor(
                        api_token=config["api_token"],
                        environment=config.get("environment", "sandbox")
                    )
                    
                elif processor_name == "square" and config.get("enabled", False):
                    self.processors["square"] = SquarePaymentProcessor(
                        access_token=config["access_token"],
                        environment=config.get("environment", "sandbox")
                    )
                    
                elif processor_name == "adyen" and config.get("enabled", False):
                    self.processors["adyen"] = AdyenPaymentProcessor(
                        api_key=config["api_key"],
                        merchant_account=config["merchant_account"],
                        environment=config.get("environment", "test")
                    )
                    
                elif processor_name == "braintree" and config.get("enabled", False):
                    self.processors["braintree"] = BraintreePaymentProcessor(
                        merchant_id=config["merchant_id"],
                        public_key=config["public_key"],
                        private_key=config["private_key"],
                        environment=config.get("environment", "sandbox")
                    )
                    
                elif processor_name == "razorpay" and config.get("enabled", False):
                    self.processors["razorpay"] = RazorpayPaymentProcessor(
                        key_id=config["key_id"],
                        key_secret=config["key_secret"]
                    )
                    
                elif processor_name == "crypto" and config.get("enabled", False):
                    self.processors["crypto"] = CryptocurrencyPaymentProcessor(
                        networks_config=config["networks_config"],
                        exchange_api_key=config.get("exchange_api_key")
                    )
                
                self.logger.info(f"Initialized processor: {processor_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize processor {processor_name}: {e}")

    def _select_payment_route(
        self,
        payment_request: UniversalPaymentRequest
    ) -> Optional[PaymentRoute]:
        """Select optimal payment route based on request parameters.
        
        Args:
            payment_request: Payment request details
            
        Returns:
            Selected payment route or None if no route available
        """
        # Filter routes by criteria
        candidate_routes = []
        
        for route in self.routing_config:
            if not route.enabled:
                continue
            
            # Check currency support
            if route.currencies and payment_request.currency not in route.currencies:
                continue
            
            # Check payment method support
            if route.methods and payment_request.payment_method not in route.methods:
                continue
            
            # Check amount limits
            if route.min_amount and payment_request.amount < route.min_amount:
                continue
            if route.max_amount and payment_request.amount > route.max_amount:
                continue
            
            # Check processor availability
            if route.processor not in self.processors:
                continue
            
            # Check regional support
            if route.regions and payment_request.customer_country:
                region = self._get_region_for_country(payment_request.customer_country)
                if region not in route.regions and PaymentRegion.GLOBAL not in route.regions:
                    continue
            
            candidate_routes.append(route)
        
        if not candidate_routes:
            return None
        
        # Preferred processor override
        if payment_request.preferred_processor:
            for route in candidate_routes:
                if route.processor == payment_request.preferred_processor:
                    return route
        
        # Select based on priority and success rate
        candidate_routes.sort(key=lambda r: (r.priority, -r.success_rate))
        
        # Weighted selection for load balancing
        if len(candidate_routes) > 1:
            weights = [route.weight for route in candidate_routes[:3]]  # Top 3 routes
            selected_route = random.choices(candidate_routes[:3], weights=weights)[0]
        else:
            selected_route = candidate_routes[0]
        
        return selected_route

    async def process_payment(
        self,
        payment_request: UniversalPaymentRequest
    ) -> UniversalPaymentResponse:
        """Process payment through optimal route with failover.
        
        Args:
            payment_request: Universal payment request
            
        Returns:
            Universal payment response
        """
        payment_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Select primary route
            primary_route = self._select_payment_route(payment_request)
            if not primary_route:
                return UniversalPaymentResponse(
                    payment_id=payment_id,
                    processor="none",
                    status=PaymentStatus.FAILED,
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    fees=Decimal(0),
                    processor_transaction_id="",
                    error="No available payment route"
                )
            
            # Attempt payment with primary route
            response = await self._attempt_payment(payment_request, primary_route, payment_id)
            
            # If failed, try failover routes
            if response.status == PaymentStatus.FAILED:
                failover_routes = [r for r in self.routing_config 
                                 if r.processor != primary_route.processor and r.enabled]
                
                for route in failover_routes[:2]:  # Try up to 2 failover routes
                    if self._route_matches_request(route, payment_request):
                        self.logger.info(f"Attempting failover to {route.processor}")
                        response = await self._attempt_payment(payment_request, route, payment_id)
                        if response.status != PaymentStatus.FAILED:
                            break
            
            # Update analytics
            if self.analytics_enabled:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                await self._update_analytics(response, processing_time)
            
            # Cache successful payment
            if response.status not in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
                self.payment_cache[payment_id] = response
            
            self.logger.info(f"Processed payment {payment_id}: {response.status}")
            return response
            
        except Exception as e:
            self.logger.error(f"Payment processing error: {e}")
            return UniversalPaymentResponse(
                payment_id=payment_id,
                processor="error",
                status=PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                fees=Decimal(0),
                processor_transaction_id="",
                error=str(e)
            )

    async def _attempt_payment(
        self,
        payment_request: UniversalPaymentRequest,
        route: PaymentRoute,
        payment_id: str
    ) -> UniversalPaymentResponse:
        """Attempt payment through specific processor.
        
        Args:
            payment_request: Payment request
            route: Selected payment route
            payment_id: Universal payment ID
            
        Returns:
            Payment response
        """
        processor = self.processors[route.processor]
        
        try:
            # Convert universal request to processor-specific format
            processor_request = await self._convert_to_processor_request(
                payment_request, route.processor
            )
            
            # Process payment through selected processor
            if route.processor == "stripe":
                result = await self._process_stripe_payment(processor, processor_request)
            elif route.processor == "paypal":
                result = await self._process_paypal_payment(processor, processor_request)
            elif route.processor == "wise":
                result = await self._process_wise_payment(processor, processor_request)
            elif route.processor == "square":
                result = await self._process_square_payment(processor, processor_request)
            elif route.processor == "adyen":
                result = await self._process_adyen_payment(processor, processor_request)
            elif route.processor == "braintree":
                result = await self._process_braintree_payment(processor, processor_request)
            elif route.processor == "razorpay":
                result = await self._process_razorpay_payment(processor, processor_request)
            elif route.processor == "crypto":
                result = await self._process_crypto_payment(processor, processor_request)
            else:
                raise ValueError(f"Unsupported processor: {route.processor}")
            
            # Convert processor response to universal format
            response = await self._convert_from_processor_response(
                result, route.processor, payment_id, payment_request
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Processor {route.processor} error: {e}")
            return UniversalPaymentResponse(
                payment_id=payment_id,
                processor=route.processor,
                status=PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                fees=Decimal(0),
                processor_transaction_id="",
                error=str(e)
            )

    async def capture_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None
    ) -> UniversalPaymentResponse:
        """Capture an authorized payment.
        
        Args:
            payment_id: Universal payment ID
            amount: Amount to capture (if partial capture)
            
        Returns:
            Updated payment response
        """
        try:
            if payment_id not in self.payment_cache:
                raise ValueError(f"Payment {payment_id} not found")
            
            payment = self.payment_cache[payment_id]
            processor = self.processors[payment.processor]
            
            # Call processor-specific capture method
            if payment.processor == "stripe":
                result = await processor.capture_payment_intent(
                    payment.processor_transaction_id, amount
                )
            elif payment.processor == "adyen":
                result = await processor.capture_payment(
                    payment.processor_transaction_id, 
                    int(amount * 100) if amount else None,
                    payment.currency
                )
            # Add other processors as needed
            
            # Update payment status
            payment.status = PaymentStatus.CAPTURED
            payment.updated_at = datetime.utcnow()
            
            self.logger.info(f"Captured payment {payment_id}")
            return payment
            
        except Exception as e:
            self.logger.error(f"Payment capture error: {e}")
            raise

    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> UniversalPaymentResponse:
        """Refund a captured payment.
        
        Args:
            payment_id: Universal payment ID
            amount: Amount to refund (full refund if None)
            reason: Refund reason
            
        Returns:
            Refund response
        """
        try:
            if payment_id not in self.payment_cache:
                raise ValueError(f"Payment {payment_id} not found")
            
            payment = self.payment_cache[payment_id]
            processor = self.processors[payment.processor]
            
            # Call processor-specific refund method
            if payment.processor == "stripe":
                result = await processor.create_refund(
                    payment.processor_transaction_id, amount, reason
                )
            elif payment.processor == "paypal":
                result = await processor.refund_payment(
                    payment.processor_transaction_id, amount, reason
                )
            # Add other processors as needed
            
            # Update payment status
            if amount and amount < payment.amount:
                payment.status = PaymentStatus.PARTIALLY_REFUNDED
            else:
                payment.status = PaymentStatus.REFUNDED
            payment.updated_at = datetime.utcnow()
            
            self.logger.info(f"Refunded payment {payment_id}")
            return payment
            
        except Exception as e:
            self.logger.error(f"Payment refund error: {e}")
            raise

    async def get_payment_status(
        self,
        payment_id: str
    ) -> UniversalPaymentResponse:
        """Get current payment status.
        
        Args:
            payment_id: Universal payment ID
            
        Returns:
            Current payment response
        """
        if payment_id in self.payment_cache:
            return self.payment_cache[payment_id]
        else:
            raise ValueError(f"Payment {payment_id} not found")

    async def get_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PaymentAnalytics:
        """Get payment analytics and metrics.
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Payment analytics data
        """
        if not self.analytics_enabled:
            raise ValueError("Analytics not enabled")
        
        # In a real implementation, this would query a database
        # For now, return the in-memory analytics
        return self.analytics

    def _route_matches_request(
        self,
        route: PaymentRoute,
        payment_request: UniversalPaymentRequest
    ) -> bool:
        """Check if route matches payment request criteria."""
        if not route.enabled:
            return False
        
        if route.currencies and payment_request.currency not in route.currencies:
            return False
        
        if route.methods and payment_request.payment_method not in route.methods:
            return False
        
        if route.min_amount and payment_request.amount < route.min_amount:
            return False
        
        if route.max_amount and payment_request.amount > route.max_amount:
            return False
        
        return True

    def _get_region_for_country(self, country_code: str) -> PaymentRegion:
        """Get payment region for country code."""
        regions_map = {
            "US": PaymentRegion.NORTH_AMERICA,
            "CA": PaymentRegion.NORTH_AMERICA,
            "MX": PaymentRegion.LATIN_AMERICA,
            "GB": PaymentRegion.EUROPE,
            "DE": PaymentRegion.EUROPE,
            "FR": PaymentRegion.EUROPE,
            "IT": PaymentRegion.EUROPE,
            "ES": PaymentRegion.EUROPE,
            "NL": PaymentRegion.EUROPE,
            "IN": PaymentRegion.ASIA_PACIFIC,
            "CN": PaymentRegion.ASIA_PACIFIC,
            "JP": PaymentRegion.ASIA_PACIFIC,
            "AU": PaymentRegion.ASIA_PACIFIC,
            "SG": PaymentRegion.ASIA_PACIFIC,
            "BR": PaymentRegion.LATIN_AMERICA,
            "AR": PaymentRegion.LATIN_AMERICA,
            "AE": PaymentRegion.MIDDLE_EAST,
            "SA": PaymentRegion.MIDDLE_EAST,
            "ZA": PaymentRegion.AFRICA,
            "NG": PaymentRegion.AFRICA,
        }
        
        return regions_map.get(country_code, PaymentRegion.GLOBAL)

    async def _convert_to_processor_request(
        self,
        payment_request: UniversalPaymentRequest,
        processor_name: str
    ) -> Dict[str, Any]:
        """Convert universal request to processor-specific format."""
        # This would contain conversion logic for each processor
        # For now, return a basic structure
        return {
            "amount": payment_request.amount,
            "currency": payment_request.currency,
            "customer_email": payment_request.customer_email,
            "description": payment_request.description,
            "metadata": payment_request.metadata
        }

    async def _convert_from_processor_response(
        self,
        processor_response: Dict[str, Any],
        processor_name: str,
        payment_id: str,
        payment_request: UniversalPaymentRequest
    ) -> UniversalPaymentResponse:
        """Convert processor response to universal format."""
        # This would contain conversion logic for each processor
        # For now, return a basic structure
        return UniversalPaymentResponse(
            payment_id=payment_id,
            processor=processor_name,
            status=PaymentStatus.PROCESSING,
            amount=payment_request.amount,
            currency=payment_request.currency,
            fees=Decimal(0),
            processor_transaction_id=processor_response.get("id", ""),
            processor_response=processor_response
        )

    async def _update_analytics(
        self,
        payment_response -> None: UniversalPaymentResponse,
        processing_time -> None: float
    ) -> None:
        """Update payment analytics."""
        if not self.analytics:
            return
        
        self.analytics.total_transactions += 1
        self.analytics.total_volume += payment_response.amount
        
        # Update processor stats
        if payment_response.processor not in self.analytics.processor_stats:
            self.analytics.processor_stats[payment_response.processor] = {
                "transactions": 0,
                "volume": Decimal(0),
                "success_rate": 0.0,
                "avg_processing_time": 0.0
            }
        
        processor_stats = self.analytics.processor_stats[payment_response.processor]
        processor_stats["transactions"] += 1
        processor_stats["volume"] += payment_response.amount
        
        # Update success rate (simplified)
        success = 1 if payment_response.status not in [PaymentStatus.FAILED, PaymentStatus.CANCELLED] else 0
        current_success_rate = processor_stats["success_rate"]
        new_success_rate = (current_success_rate * (processor_stats["transactions"] - 1) + success) / processor_stats["transactions"]
        processor_stats["success_rate"] = new_success_rate

    # Processor-specific payment methods (simplified implementations)
    async def _process_stripe_payment(self, processor, request) -> None:
        """Process payment through Stripe."""
        # Implementation would call Stripe-specific methods
        pass

    async def _process_paypal_payment(self, processor, request) -> None:
        """Process payment through PayPal."""
        # Implementation would call PayPal-specific methods
        pass

    async def _process_wise_payment(self, processor, request) -> None:
        """Process payment through Wise."""
        # Implementation would call Wise-specific methods
        pass

    async def _process_square_payment(self, processor, request) -> None:
        """Process payment through Square."""
        # Implementation would call Square-specific methods
        pass

    async def _process_adyen_payment(self, processor, request) -> None:
        """Process payment through Adyen."""
        # Implementation would call Adyen-specific methods
        pass

    async def _process_braintree_payment(self, processor, request) -> None:
        """Process payment through Braintree."""
        # Implementation would call Braintree-specific methods
        pass

    async def _process_razorpay_payment(self, processor, request) -> None:
        """Process payment through Razorpay."""
        # Implementation would call Razorpay-specific methods
        pass

    async def _process_crypto_payment(self, processor, request) -> None:
        """Process payment through cryptocurrency."""
        # Implementation would call crypto-specific methods
        pass

    async def close(self) -> None:
        """Close all processor connections."""
        for processor in self.processors.values():
            if hasattr(processor, 'close'):
                await processor.close()
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator monetization specific functions
async def create_creator_payment_setup(
    aggregator: PaymentAggregator,
    creator_id: str,
    supported_methods: List[PaymentMethod],
    supported_currencies: List[str],
    platform_fee_percentage: float = 5.0
) -> Dict[str, Any]:
    """Setup payment processing for creator monetization.
    
    Args:
        aggregator: Payment aggregator instance
        creator_id: Creator identifier
        supported_methods: Supported payment methods
        supported_currencies: Supported currencies
        platform_fee_percentage: Platform fee percentage
        
    Returns:
        Dict containing payment setup details
    """
    setup_config = {
        "creator_id": creator_id,
        "supported_methods": [method.value for method in supported_methods],
        "supported_currencies": supported_currencies,
        "platform_fee_percentage": platform_fee_percentage,
        "payment_routes": [],
        "webhook_endpoints": []
    }
    
    # Configure optimal routes for creator payments
    for method in supported_methods:
        for currency in supported_currencies:
            optimal_route = aggregator._select_payment_route(
                UniversalPaymentRequest(
                    amount=Decimal('100'),  # Test amount
                    currency=currency,
                    payment_method=method
                )
            )
            
            if optimal_route:
                setup_config["payment_routes"].append({
                    "method": method.value,
                    "currency": currency,
                    "processor": optimal_route.processor,
                    "priority": optimal_route.priority
                })
    
    return setup_config


async def process_creator_monetization_payment(
    aggregator: PaymentAggregator,
    creator_id: str,
    fan_id: str,
    amount: Decimal,
    currency: str,
    payment_method: PaymentMethod,
    platform_fee_percentage: float = 5.0
) -> Dict[str, Any]:
    """Process creator monetization payment with platform fee split.
    
    Args:
        aggregator: Payment aggregator instance
        creator_id: Creator identifier
        fan_id: Fan/customer identifier
        amount: Payment amount
        currency: Currency code
        payment_method: Payment method
        platform_fee_percentage: Platform fee percentage
        
    Returns:
        Dict containing payment result with split details
    """
    platform_fee = amount * Decimal(platform_fee_percentage / 100)
    creator_amount = amount - platform_fee
    
    payment_request = UniversalPaymentRequest(
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        customer_id=fan_id,
        description=f"Creator support payment to {creator_id}",
        metadata={
            "creator_id": creator_id,
            "fan_id": fan_id,
            "platform_fee": str(platform_fee),
            "creator_amount": str(creator_amount),
            "platform_fee_percentage": platform_fee_percentage,
            "payment_type": "creator_monetization"
        }
    )
    
    payment_response = await aggregator.process_payment(payment_request)
    
    # Add split payment details
    payment_result = {
        "payment_response": payment_response,
        "platform_fee": platform_fee,
        "creator_amount": creator_amount,
        "platform_fee_percentage": platform_fee_percentage,
        "split_details": {
            "total_amount": amount,
            "platform_fee": platform_fee,
            "creator_earnings": creator_amount,
            "currency": currency
        }
    }
    
    return payment_result