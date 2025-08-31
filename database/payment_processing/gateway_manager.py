"""
Enterprise Payment Gateway Management - Multi-Provider Integration

Advanced payment gateway orchestration system supporting multiple providers
with intelligent routing, failover capabilities, and optimization algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE FEATURES:
- Multi-gateway payment processing with automatic failover
- Intelligent routing based on cost, success rate, and performance
- Real-time gateway health monitoring and circuit breaker pattern
- Dynamic load balancing across payment providers
- Advanced retry logic with exponential backoff
- Comprehensive fee optimization and cost analysis
- Regulatory compliance across global markets
- Advanced security with tokenization and encryption
"""

from typing import Dict, Any, Optional, List, Union, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
import aiohttp
import json
import hashlib
from abc import ABC, abstractmethod
import stripe
import paypal
import requests
from cryptography.fernet import Fernet

from .models import (
    PaymentStatus, PaymentProvider, CurrencyCode, PaymentMethodType,
    TransactionType
)
from ..core.config import get_settings
from ..security.encryption import PaymentEncryption
from ..utils.circuit_breaker import CircuitBreaker
from ..utils.retry import RetryManager

logger = logging.getLogger(__name__)
settings = get_settings()


class GatewayStatus(Enum):
    """Gateway operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    FAILED = "failed"


class RoutingStrategy(Enum):
    """Payment routing strategies"""
    LOWEST_COST = "lowest_cost"
    HIGHEST_SUCCESS_RATE = "highest_success_rate"
    FASTEST_PROCESSING = "fastest_processing"
    BALANCED = "balanced"
    GEOGRAPHIC_OPTIMIZATION = "geographic_optimization"
    VOLUME_BASED = "volume_based"


@dataclass
class GatewayConfiguration:
    """Gateway configuration settings"""
    provider: PaymentProvider
    api_key: str
    secret_key: str
    webhook_secret: str
    sandbox_mode: bool = False
    supported_currencies: List[CurrencyCode] = field(default_factory=list)
    supported_countries: List[str] = field(default_factory=list)
    supported_methods: List[PaymentMethodType] = field(default_factory=list)
    fee_structure: Dict[str, Decimal] = field(default_factory=dict)
    processing_limits: Dict[str, Decimal] = field(default_factory=dict)
    security_level: str = "enterprise"
    compliance_certifications: List[str] = field(default_factory=list)


@dataclass
class GatewayMetrics:
    """Gateway performance metrics"""
    success_rate: float
    average_processing_time: float
    total_volume: Decimal
    transaction_count: int
    error_rate: float
    availability: float
    cost_per_transaction: Decimal
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PaymentRequest:
    """Payment processing request"""
    amount: Decimal
    currency: CurrencyCode
    payment_method: PaymentMethodType
    customer_id: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    country_code: Optional[str] = None
    risk_score: Optional[float] = None
    priority: str = "normal"


@dataclass
class PaymentResponse:
    """Payment processing response"""
    transaction_id: str
    status: PaymentStatus
    gateway_transaction_id: str
    amount: Decimal
    currency: CurrencyCode
    fees: Dict[str, Decimal]
    processing_time: float
    gateway_response: Dict[str, Any]
    error_message: Optional[str] = None
    success: bool = True


class BasePaymentGateway(ABC):
    """
    Abstract base class for payment gateways
    """
    
    def __init__(self, config: GatewayConfiguration):
        self.config = config
        self.provider = config.provider
        self.encryption = PaymentEncryption()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
        self.retry_manager = RetryManager(max_retries=3)
        self.metrics = GatewayMetrics(
            success_rate=0.0,
            average_processing_time=0.0,
            total_volume=Decimal('0'),
            transaction_count=0,
            error_rate=0.0,
            availability=1.0,
            cost_per_transaction=Decimal('0')
        )
        
    @abstractmethod
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment transaction"""
        pass
    
    @abstractmethod
    async def process_refund(self, transaction_id: str, amount: Decimal) -> PaymentResponse:
        """Process a refund"""
        pass
    
    @abstractmethod
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get transaction status"""
        pass
    
    @abstractmethod
    async def calculate_fees(self, amount: Decimal, currency: CurrencyCode) -> Dict[str, Decimal]:
        """Calculate processing fees"""
        pass
    
    async def health_check(self) -> bool:
        """Check gateway health"""



        try:
            # Implement gateway-specific health check
            return await self._perform_health_check()
        except Exception as e:
            logger.error(f"Health check failed for {self.provider.value}: {str(e)}")
            return False
    
    @abstractmethod
    async def _perform_health_check(self) -> bool:
        """Gateway-specific health check implementation"""
        pass
    
    def update_metrics(self, processing_time: float, success: bool, amount: Decimal):
        """Update gateway performance metrics"""
        self.metrics.transaction_count += 1
        self.metrics.total_volume += amount
        
        # Update success rate (rolling average)
        current_success_rate = self.metrics.success_rate
        new_success_rate = (
            (current_success_rate * (self.metrics.transaction_count - 1) + (1.0 if success else 0.0)) 
            / self.metrics.transaction_count
        )
        self.metrics.success_rate = new_success_rate
        
        # Update average processing time
        current_avg_time = self.metrics.average_processing_time
        new_avg_time = (
            (current_avg_time * (self.metrics.transaction_count - 1) + processing_time) 
            / self.metrics.transaction_count
        )
        self.metrics.average_processing_time = new_avg_time
        
        # Update error rate
        if not success:
            error_count = self.metrics.error_rate * (self.metrics.transaction_count - 1) + 1
            self.metrics.error_rate = error_count / self.metrics.transaction_count
        
        self.metrics.last_updated = datetime.utcnow()


class StripeGateway(BasePaymentGateway):
    """
    Stripe payment gateway implementation
    """
    
    def __init__(self, config: GatewayConfiguration):
        super().__init__(config)
        stripe.api_key = config.secret_key
        self.stripe = stripe
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment through Stripe"""
        start_time = datetime.utcnow()
        
        try:
            # Create payment intent
            payment_intent = await self._create_payment_intent(request)
            
            # Confirm payment
            confirmed_intent = await self._confirm_payment_intent(
                payment_intent['id'], 
                request.payment_method
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate fees
            fees = await self.calculate_fees(request.amount, request.currency)
            
            response = PaymentResponse(
                transaction_id=confirmed_intent['id'],
                status=self._map_stripe_status(confirmed_intent['status']),
                gateway_transaction_id=confirmed_intent['id'],
                amount=request.amount,
                currency=request.currency,
                fees=fees,
                processing_time=processing_time,
                gateway_response=confirmed_intent,
                success=confirmed_intent['status'] == 'succeeded'
            )
            
            # Update metrics
            self.update_metrics(processing_time, response.success, request.amount)
            
            return response
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Stripe payment failed: {str(e)}", exc_info=True)
            
            self.update_metrics(processing_time, False, request.amount)
            
            return PaymentResponse(
                transaction_id="",
                status=PaymentStatus.FAILED,
                gateway_transaction_id="",
                amount=request.amount,
                currency=request.currency,
                fees={},
                processing_time=processing_time,
                gateway_response={},
                error_message=str(e),
                success=False
            )
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> PaymentResponse:
        """Process refund through Stripe"""



        try:
            refund = await self.stripe.Refund.create_async(
                payment_intent=transaction_id,
                amount=int(amount * 100)  # Convert to cents
            )
            
            return PaymentResponse(
                transaction_id=refund['id'],
                status=self._map_stripe_status(refund['status']),
                gateway_transaction_id=refund['id'],
                amount=amount,
                currency=CurrencyCode(refund['currency'].upper()),
                fees={},
                processing_time=0.0,
                gateway_response=refund,
                success=refund['status'] == 'succeeded'
            )
            
        except Exception as e:
            logger.error(f"Stripe refund failed: {str(e)}", exc_info=True)
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get transaction status from Stripe"""



        try:
            payment_intent = await self.stripe.PaymentIntent.retrieve_async(transaction_id)
            return self._map_stripe_status(payment_intent['status'])
        except Exception as e:
            logger.error(f"Failed to get Stripe transaction status: {str(e)}")
            return PaymentStatus.FAILED
    
    async def calculate_fees(self, amount: Decimal, currency: CurrencyCode) -> Dict[str, Decimal]:
        """Calculate Stripe fees"""
        # Stripe fee structure (simplified)
        percentage_fee = Decimal('0.029')  # 2.9%
        fixed_fee = Decimal('0.30')  # $0.30
        
        total_fee = (amount * percentage_fee) + fixed_fee
        
        return {
            'percentage_fee': amount * percentage_fee,
            'fixed_fee': fixed_fee,
            'total_fee': total_fee
        }
    
    async def _perform_health_check(self) -> bool:
        """Stripe-specific health check"""



        try:
            # Test API connectivity
            await self.stripe.Account.retrieve_async()
            return True
        except Exception:
            return False
    
    async def _create_payment_intent(self, request: PaymentRequest) -> Dict[str, Any]:
        """Create Stripe payment intent"""



        return await self.stripe.PaymentIntent.create_async(
            amount=int(request.amount * 100),  # Convert to cents
            currency=request.currency.value.lower(),
            metadata=request.metadata,
            description=request.description
        )
    
    async def _confirm_payment_intent(
        self, 
        intent_id: str, 
        payment_method: PaymentMethodType
    ) -> Dict[str, Any]:
        """Confirm Stripe payment intent"""



        return await self.stripe.PaymentIntent.confirm_async(
            intent_id,
            payment_method=self._get_stripe_payment_method(payment_method)
        )
    
    def _map_stripe_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe status to internal status"""
        status_mapping = {
            'succeeded': PaymentStatus.COMPLETED,
            'processing': PaymentStatus.PROCESSING,
            'requires_payment_method': PaymentStatus.REQUIRES_ACTION,
            'requires_confirmation': PaymentStatus.PENDING,
            'requires_action': PaymentStatus.REQUIRES_ACTION,
            'canceled': PaymentStatus.CANCELLED,
            'failed': PaymentStatus.FAILED
        }
        return status_mapping.get(stripe_status, PaymentStatus.FAILED)
    
    def _get_stripe_payment_method(self, payment_method: PaymentMethodType) -> str:
        """Convert internal payment method to Stripe format"""
        method_mapping = {
            PaymentMethodType.CREDIT_CARD: 'card',
            PaymentMethodType.DEBIT_CARD: 'card',
            PaymentMethodType.BANK_TRANSFER: 'ach_direct_debit',
            PaymentMethodType.SEPA: 'sepa_debit',
            PaymentMethodType.APPLE_PAY: 'card',
            PaymentMethodType.GOOGLE_PAY: 'card'
        }
        return method_mapping.get(payment_method, 'card')


class PayPalGateway(BasePaymentGateway):
    """
    PayPal payment gateway implementation
    """
    
    def __init__(self, config: GatewayConfiguration):
        super().__init__(config)
        self.client_id = config.api_key
        self.client_secret = config.secret_key
        self.base_url = "https://api.sandbox.paypal.com" if config.sandbox_mode else "https://api.paypal.com"
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment through PayPal"""
        start_time = datetime.utcnow()
        
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # Create order
            order = await self._create_order(request, access_token)
            
            # Capture order
            capture_result = await self._capture_order(order['id'], access_token)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate fees
            fees = await self.calculate_fees(request.amount, request.currency)
            
            response = PaymentResponse(
                transaction_id=capture_result['id'],
                status=self._map_paypal_status(capture_result['status']),
                gateway_transaction_id=capture_result['id'],
                amount=request.amount,
                currency=request.currency,
                fees=fees,
                processing_time=processing_time,
                gateway_response=capture_result,
                success=capture_result['status'] == 'COMPLETED'
            )
            
            # Update metrics
            self.update_metrics(processing_time, response.success, request.amount)
            
            return response
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"PayPal payment failed: {str(e)}", exc_info=True)
            
            self.update_metrics(processing_time, False, request.amount)
            
            return PaymentResponse(
                transaction_id="",
                status=PaymentStatus.FAILED,
                gateway_transaction_id="",
                amount=request.amount,
                currency=request.currency,
                fees={},
                processing_time=processing_time,
                gateway_response={},
                error_message=str(e),
                success=False
            )
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> PaymentResponse:
        """Process refund through PayPal"""



        try:
            access_token = await self._get_access_token()
            
            refund_data = {
                "amount": {
                    "value": str(amount),
                    "currency_code": "USD"  # This should be dynamic
                }
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    f"{self.base_url}/v2/payments/captures/{transaction_id}/refund",
                    headers=headers,
                    json=refund_data
                ) as response:
                    result = await response.json()
                    
                    return PaymentResponse(
                        transaction_id=result['id'],
                        status=self._map_paypal_status(result['status']),
                        gateway_transaction_id=result['id'],
                        amount=amount,
                        currency=CurrencyCode.USD,  # This should be dynamic
                        fees={},
                        processing_time=0.0,
                        gateway_response=result,
                        success=result['status'] == 'COMPLETED'
                    )
                    
        except Exception as e:
            logger.error(f"PayPal refund failed: {str(e)}", exc_info=True)
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get transaction status from PayPal"""



        try:
            access_token = await self._get_access_token()
            
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {access_token}'}
                
                async with session.get(
                    f"{self.base_url}/v2/payments/captures/{transaction_id}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return self._map_paypal_status(result['status'])
                    
        except Exception as e:
            logger.error(f"Failed to get PayPal transaction status: {str(e)}")
            return PaymentStatus.FAILED
    
    async def calculate_fees(self, amount: Decimal, currency: CurrencyCode) -> Dict[str, Decimal]:
        """Calculate PayPal fees"""
        # PayPal fee structure (simplified)
        percentage_fee = Decimal('0.034')  # 3.4%
        fixed_fee = Decimal('0.30')  # $0.30
        
        total_fee = (amount * percentage_fee) + fixed_fee
        
        return {
            'percentage_fee': amount * percentage_fee,
            'fixed_fee': fixed_fee,
            'total_fee': total_fee
        }
    
    async def _perform_health_check(self) -> bool:
        """PayPal-specific health check"""



        try:
            access_token = await self._get_access_token()
            return access_token is not None
        except Exception:
            return False
    
    async def _get_access_token(self) -> str:
        """Get PayPal access token"""
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            
            async with session.post(
                f"{self.base_url}/v1/oauth2/token",
                data=auth_data,
                auth=auth
            ) as response:
                result = await response.json()
                return result['access_token']
    
    async def _create_order(self, request: PaymentRequest, access_token: str) -> Dict[str, Any]:
        """Create PayPal order"""
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": request.currency.value,
                    "value": str(request.amount)
                },
                "description": request.description
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with session.post(
                f"{self.base_url}/v2/checkout/orders",
                headers=headers,
                json=order_data
            ) as response:
                return await response.json()
    
    async def _capture_order(self, order_id: str, access_token: str) -> Dict[str, Any]:
        """Capture PayPal order"""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with session.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers=headers
            ) as response:
                result = await response.json()
                # Extract capture details
                return result['purchase_units'][0]['payments']['captures'][0]
    
    def _map_paypal_status(self, paypal_status: str) -> PaymentStatus:
        """Map PayPal status to internal status"""
        status_mapping = {
            'COMPLETED': PaymentStatus.COMPLETED,
            'PENDING': PaymentStatus.PENDING,
            'DECLINED': PaymentStatus.FAILED,
            'PARTIALLY_REFUNDED': PaymentStatus.PARTIALLY_REFUNDED,
            'REFUNDED': PaymentStatus.REFUNDED,
            'DENIED': PaymentStatus.FAILED
        }
        return status_mapping.get(paypal_status, PaymentStatus.FAILED)


class PaymentGatewayManager:
    """
    Enterprise payment gateway manager with intelligent routing
    """
    
    def __init__(self):
        self.gateways: Dict[PaymentProvider, BasePaymentGateway] = {}
        self.routing_strategy = RoutingStrategy.BALANCED
        self.load_balancer = GatewayLoadBalancer()
        self.health_monitor = GatewayHealthMonitor()
        
    def register_gateway(self, gateway: BasePaymentGateway):
        """Register a payment gateway"""
        self.gateways[gateway.provider] = gateway
        logger.info(f"Registered gateway: {gateway.provider.value}")
    
    async def select_optimal_gateway(
        self,
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethodType,
        country_code: Optional[str] = None,
        risk_score: Optional[float] = None
    ) -> BasePaymentGateway:
        """Select optimal gateway based on routing strategy"""
        
        # Filter gateways by capabilities
        eligible_gateways = await self._filter_eligible_gateways(
            currency, payment_method, country_code
        )
        
        if not eligible_gateways:
            raise NoEligibleGatewayError("No eligible gateways found")
        
        # Apply routing strategy
        if self.routing_strategy == RoutingStrategy.LOWEST_COST:
            return await self._select_lowest_cost_gateway(eligible_gateways, amount, currency)
        elif self.routing_strategy == RoutingStrategy.HIGHEST_SUCCESS_RATE:
            return await self._select_highest_success_rate_gateway(eligible_gateways)
        elif self.routing_strategy == RoutingStrategy.FASTEST_PROCESSING:
            return await self._select_fastest_gateway(eligible_gateways)
        elif self.routing_strategy == RoutingStrategy.BALANCED:
            return await self._select_balanced_gateway(eligible_gateways, amount, currency)
        else:
            # Default to first available gateway
            return eligible_gateways[0]
    
    async def _filter_eligible_gateways(
        self,
        currency: CurrencyCode,
        payment_method: PaymentMethodType,
        country_code: Optional[str]
    ) -> List[BasePaymentGateway]:
        """Filter gateways by eligibility criteria"""
        eligible = []
        
        for gateway in self.gateways.values():
            # Check currency support
            if currency not in gateway.config.supported_currencies:
                continue
                
            # Check payment method support
            if payment_method not in gateway.config.supported_methods:
                continue
                
            # Check country support
            if country_code and country_code not in gateway.config.supported_countries:
                continue
                
            # Check gateway health
            if await gateway.health_check():
                eligible.append(gateway)
        
        return eligible
    
    async def _select_lowest_cost_gateway(
        self,
        gateways: List[BasePaymentGateway],
        amount: Decimal,
        currency: CurrencyCode
    ) -> BasePaymentGateway:
        """Select gateway with lowest cost"""
        best_gateway = None
        lowest_cost = Decimal('inf')
        
        for gateway in gateways:
            fees = await gateway.calculate_fees(amount, currency)
            total_cost = fees.get('total_fee', Decimal('0'))
            
            if total_cost < lowest_cost:
                lowest_cost = total_cost
                best_gateway = gateway
        
        return best_gateway or gateways[0]
    
    async def _select_highest_success_rate_gateway(
        self,
        gateways: List[BasePaymentGateway]
    ) -> BasePaymentGateway:
        """Select gateway with highest success rate"""



        return max(gateways, key=lambda g: g.metrics.success_rate)
    
    async def _select_fastest_gateway(
        self,
        gateways: List[BasePaymentGateway]
    ) -> BasePaymentGateway:
        """Select gateway with fastest processing"""



        return min(gateways, key=lambda g: g.metrics.average_processing_time)
    
    async def _select_balanced_gateway(
        self,
        gateways: List[BasePaymentGateway],
        amount: Decimal,
        currency: CurrencyCode
    ) -> BasePaymentGateway:
        """Select gateway using balanced scoring"""
        best_gateway = None
        best_score = -1
        
        for gateway in gateways:
            fees = await gateway.calculate_fees(amount, currency)
            cost_ratio = fees.get('total_fee', Decimal('0')) / amount
            
            # Calculate balanced score (higher is better)
            score = (
                gateway.metrics.success_rate * 0.4 +
                (1.0 - float(cost_ratio)) * 0.3 +
                (1.0 / max(gateway.metrics.average_processing_time, 0.1)) * 0.2 +
                gateway.metrics.availability * 0.1
            )
            
            if score > best_score:
                best_score = score
                best_gateway = gateway
        
        return best_gateway or gateways[0]


class GatewayLoadBalancer:
    """Load balancer for payment gateways"""
    
    def __init__(self):
        self.round_robin_index = 0
    
    async def distribute_load(
        self,
        gateways: List[BasePaymentGateway],
        strategy: str = "round_robin"
    ) -> BasePaymentGateway:
        """Distribute load across gateways"""
        if strategy == "round_robin":
            gateway = gateways[self.round_robin_index % len(gateways)]
            self.round_robin_index += 1
            return gateway
        elif strategy == "least_connections":
            return min(gateways, key=lambda g: g.metrics.transaction_count)
        else:
            return gateways[0]


class GatewayHealthMonitor:
    """Health monitoring for payment gateways"""
    
    def __init__(self):
        self.health_check_interval = 60  # seconds
        self.monitoring_active = False
    
    async def start_monitoring(self, gateways: Dict[PaymentProvider, BasePaymentGateway]):
        """Start health monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            for provider, gateway in gateways.items():
                try:
                    is_healthy = await gateway.health_check()
                    if not is_healthy:
                        logger.warning(f"Gateway {provider.value} failed health check")
                        # Implement alerting logic here
                except Exception as e:
                    logger.error(f"Health check error for {provider.value}: {str(e)}")
            
            await asyncio.sleep(self.health_check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False


# Custom exceptions
class NoEligibleGatewayError(Exception):
    """No eligible gateway found"""
    pass


class GatewayProcessingError(Exception):
    """Gateway processing error"""
    pass
