"""
💳 PAYMENT GATEWAY ORCHESTRATOR SERVICE - ENTERPRISE MICROSERVICE
Orchestrates multiple payment gateways for optimal payment processing.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import aioredis
import aiohttp

logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BUY_NOW_PAY_LATER = "bnpl"

class PaymentStatus(Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class GatewayType(Enum):
    """Payment gateway types"""
    PRIMARY = "primary"
    BACKUP = "backup"
    REGIONAL = "regional"
    SPECIALIZED = "specialized"

@dataclass
class PaymentGateway:
    """Payment gateway configuration"""
    gateway_id: str
    name: str
    provider: str
    gateway_type: GatewayType
    enabled: bool = True
    priority: int = 1
    supported_methods: List[PaymentMethod] = None
    supported_currencies: List[str] = None
    supported_countries: List[str] = None
    transaction_fee: Decimal = Decimal('0')
    success_rate: float = 99.0
    avg_processing_time: float = 2.0
    max_amount: Decimal = Decimal('10000')
    min_amount: Decimal = Decimal('1')
    configuration: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.supported_methods is None:
            self.supported_methods = [PaymentMethod.CREDIT_CARD]
        if self.supported_currencies is None:
            self.supported_currencies = ['USD']
        if self.supported_countries is None:
            self.supported_countries = ['US']
        if self.configuration is None:
            self.configuration = {}

@dataclass
class PaymentRequest:
    """Payment request data"""
    request_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    customer_country: str
    customer_id: str
    creator_id: str
    description: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PaymentResult:
    """Payment processing result"""
    result_id: str
    request_id: str
    gateway_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    gateway_response: Dict[str, Any] = None
    fees: Decimal = Decimal('0')
    net_amount: Decimal = Decimal('0')
    processing_time: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.gateway_response is None:
            self.gateway_response = {}

class PaymentGatewayOrchestrator:
    """
    💳 Payment Gateway Orchestrator Service
    
    Orchestrates multiple payment gateways for optimal payment processing,
    with smart routing, fallback handling, and performance optimization.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Gateway registry
        self.gateways: Dict[str, PaymentGateway] = {}
        
        # Gateway adapters
        self.gateway_adapters: Dict[str, Any] = {}
        
        # Processing statistics
        self.gateway_stats = {}
        self.processing_cache: Dict[str, PaymentResult] = {}
        
        # Routing rules
        self.routing_rules = {
            'amount_based': {
                'high_value': {'threshold': Decimal('1000'), 'preferred_gateways': []},
                'medium_value': {'threshold': Decimal('100'), 'preferred_gateways': []},
                'low_value': {'threshold': Decimal('0'), 'preferred_gateways': []}
            },
            'country_based': {},
            'method_based': {},
            'currency_based': {}
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize payment gateway orchestrator"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load gateway configurations
            await self._load_gateway_configurations()
            
            # Initialize gateway adapters
            await self._initialize_gateway_adapters()
            
            # Load routing rules
            await self._load_routing_rules()
            
            # Start background tasks
            asyncio.create_task(self._gateway_health_check_task())
            asyncio.create_task(self._performance_monitoring_task())
            asyncio.create_task(self._statistics_update_task())
            
            self.running = True
            logger.info("Payment Gateway Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize payment gateway orchestrator: {e}")
            raise
            
    async def _load_gateway_configurations(self):
        """Load gateway configurations from Redis"""
        try:
            gateways_data = await self.redis.get("payment:gateways:config")
            if gateways_data:
                gateways_config = json.loads(gateways_data)
                for gateway_config in gateways_config:
                    gateway = PaymentGateway(**gateway_config)
                    self.gateways[gateway.gateway_id] = gateway
                    
            # Initialize default gateways if none loaded
            if not self.gateways:
                await self._initialize_default_gateways()
                
        except Exception as e:
            logger.error(f"Failed to load gateway configurations: {e}")
            await self._initialize_default_gateways()
            
    async def _initialize_default_gateways(self):
        """Initialize default payment gateways"""
        default_gateways = [
            PaymentGateway(
                gateway_id="stripe_primary",
                name="Stripe Primary",
                provider="stripe",
                gateway_type=GatewayType.PRIMARY,
                priority=1,
                supported_methods=[PaymentMethod.CREDIT_CARD, PaymentMethod.DIGITAL_WALLET],
                supported_currencies=['USD', 'EUR', 'GBP', 'CAD'],
                supported_countries=['US', 'CA', 'GB', 'DE', 'FR'],
                transaction_fee=Decimal('2.9'),
                success_rate=99.2,
                max_amount=Decimal('999999')
            ),
            PaymentGateway(
                gateway_id="paypal_backup",
                name="PayPal Backup",
                provider="paypal",
                gateway_type=GatewayType.BACKUP,
                priority=2,
                supported_methods=[PaymentMethod.DIGITAL_WALLET, PaymentMethod.BANK_TRANSFER],
                supported_currencies=['USD', 'EUR', 'GBP'],
                supported_countries=['US', 'CA', 'GB', 'DE', 'FR'],
                transaction_fee=Decimal('3.4'),
                success_rate=98.8
            ),
            PaymentGateway(
                gateway_id="adyen_regional",
                name="Adyen Regional",
                provider="adyen",
                gateway_type=GatewayType.REGIONAL,
                priority=1,
                supported_methods=[PaymentMethod.CREDIT_CARD, PaymentMethod.BANK_TRANSFER],
                supported_currencies=['EUR', 'GBP', 'USD'],
                supported_countries=['DE', 'FR', 'NL', 'BE'],
                transaction_fee=Decimal('2.8'),
                success_rate=99.1
            ),
            PaymentGateway(
                gateway_id="coinbase_crypto",
                name="Coinbase Crypto",
                provider="coinbase",
                gateway_type=GatewayType.SPECIALIZED,
                priority=3,
                supported_methods=[PaymentMethod.CRYPTOCURRENCY],
                supported_currencies=['BTC', 'ETH', 'USDC'],
                supported_countries=['US', 'CA', 'GB'],
                transaction_fee=Decimal('1.0'),
                success_rate=97.5
            )
        ]
        
        for gateway in default_gateways:
            self.gateways[gateway.gateway_id] = gateway
            
        await self._save_gateway_configurations()
        
    async def _initialize_gateway_adapters(self):
        """Initialize adapters for different payment gateways"""
        # In a real implementation, these would be actual gateway API clients
        self.gateway_adapters = {
            'stripe': StripeAdapter(),
            'paypal': PayPalAdapter(),
            'adyen': AdyenAdapter(),
            'coinbase': CoinbaseAdapter()
        }
        
    async def _load_routing_rules(self):
        """Load routing rules from Redis"""
        try:
            rules_data = await self.redis.get("payment:routing:rules")
            if rules_data:
                self.routing_rules.update(json.loads(rules_data))
        except Exception as e:
            logger.error(f"Failed to load routing rules: {e}")
            
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process payment through optimal gateway"""
        try:
            # Find optimal gateway
            optimal_gateway = await self._find_optimal_gateway(payment_request)
            
            if not optimal_gateway:
                return PaymentResult(
                    result_id=f"result_{payment_request.request_id}",
                    request_id=payment_request.request_id,
                    gateway_id="none",
                    status=PaymentStatus.FAILED,
                    error_message="No suitable gateway found"
                )
                
            # Attempt payment with primary gateway
            result = await self._process_payment_with_gateway(payment_request, optimal_gateway)
            
            # If failed, try backup gateways
            if result.status == PaymentStatus.FAILED:
                backup_gateways = await self._get_backup_gateways(payment_request, optimal_gateway)
                
                for backup_gateway in backup_gateways:
                    backup_result = await self._process_payment_with_gateway(
                        payment_request, backup_gateway
                    )
                    
                    if backup_result.status in [PaymentStatus.COMPLETED, PaymentStatus.PROCESSING]:
                        result = backup_result
                        break
                        
            # Update gateway statistics
            await self._update_gateway_statistics(optimal_gateway.gateway_id, result)
            
            # Cache result
            self.processing_cache[result.result_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Payment processing failed for request {payment_request.request_id}: {e}")
            return PaymentResult(
                result_id=f"result_{payment_request.request_id}",
                request_id=payment_request.request_id,
                gateway_id="error",
                status=PaymentStatus.FAILED,
                error_message=str(e)
            )
            
    async def _find_optimal_gateway(self, payment_request: PaymentRequest) -> Optional[PaymentGateway]:
        """Find optimal gateway for payment request"""
        # Filter gateways by basic criteria
        candidate_gateways = []
        
        for gateway in self.gateways.values():
            if not gateway.enabled:
                continue
                
            # Check payment method support
            if payment_request.payment_method not in gateway.supported_methods:
                continue
                
            # Check currency support
            if payment_request.currency not in gateway.supported_currencies:
                continue
                
            # Check country support
            if payment_request.customer_country not in gateway.supported_countries:
                continue
                
            # Check amount limits
            if not (gateway.min_amount <= payment_request.amount <= gateway.max_amount):
                continue
                
            candidate_gateways.append(gateway)
            
        if not candidate_gateways:
            return None
            
        # Apply routing rules
        optimal_gateway = await self._apply_routing_rules(payment_request, candidate_gateways)
        
        return optimal_gateway
        
    async def _apply_routing_rules(self, payment_request: PaymentRequest, 
                                 gateways: List[PaymentGateway]) -> PaymentGateway:
        """Apply routing rules to select best gateway"""
        
        # Score each gateway
        gateway_scores = {}
        
        for gateway in gateways:
            score = 0
            
            # Base score from success rate
            score += gateway.success_rate
            
            # Priority bonus (higher priority = lower number = higher score)
            score += (10 - gateway.priority) * 10
            
            # Fee efficiency (lower fee = higher score)
            fee_efficiency = max(0, 10 - float(gateway.transaction_fee))
            score += fee_efficiency * 5
            
            # Processing time bonus (faster = higher score)
            time_efficiency = max(0, 10 - gateway.avg_processing_time)
            score += time_efficiency * 2
            
            # Amount-based routing
            amount_category = await self._get_amount_category(payment_request.amount)
            preferred_gateways = self.routing_rules['amount_based'][amount_category].get('preferred_gateways', [])
            if gateway.gateway_id in preferred_gateways:
                score += 20
                
            # Country-specific preferences
            country_prefs = self.routing_rules['country_based'].get(payment_request.customer_country, {})
            if gateway.gateway_id in country_prefs.get('preferred_gateways', []):
                score += 15
                
            # Method-specific preferences
            method_prefs = self.routing_rules['method_based'].get(payment_request.payment_method.value, {})
            if gateway.gateway_id in method_prefs.get('preferred_gateways', []):
                score += 15
                
            # Historical performance
            gateway_perf = self.gateway_stats.get(gateway.gateway_id, {})
            recent_success_rate = gateway_perf.get('recent_success_rate', gateway.success_rate)
            score += recent_success_rate * 0.5
            
            gateway_scores[gateway.gateway_id] = score
            
        # Select gateway with highest score
        best_gateway_id = max(gateway_scores, key=gateway_scores.get)
        return next(g for g in gateways if g.gateway_id == best_gateway_id)
        
    async def _get_amount_category(self, amount: Decimal) -> str:
        """Categorize payment amount"""
        if amount >= self.routing_rules['amount_based']['high_value']['threshold']:
            return 'high_value'
        elif amount >= self.routing_rules['amount_based']['medium_value']['threshold']:
            return 'medium_value'
        else:
            return 'low_value'
            
    async def _get_backup_gateways(self, payment_request: PaymentRequest, 
                                 primary_gateway: PaymentGateway) -> List[PaymentGateway]:
        """Get backup gateways for failover"""
        backup_gateways = []
        
        for gateway in self.gateways.values():
            if (gateway.gateway_id != primary_gateway.gateway_id and
                gateway.enabled and
                payment_request.payment_method in gateway.supported_methods and
                payment_request.currency in gateway.supported_currencies and
                payment_request.customer_country in gateway.supported_countries and
                gateway.min_amount <= payment_request.amount <= gateway.max_amount):
                
                backup_gateways.append(gateway)
                
        # Sort by priority
        backup_gateways.sort(key=lambda g: g.priority)
        
        return backup_gateways[:3]  # Maximum 3 backup attempts
        
    async def _process_payment_with_gateway(self, payment_request: PaymentRequest, 
                                          gateway: PaymentGateway) -> PaymentResult:
        """Process payment with specific gateway"""
        start_time = datetime.utcnow()
        
        try:
            # Get gateway adapter
            adapter = self.gateway_adapters.get(gateway.provider)
            if not adapter:
                raise Exception(f"No adapter found for provider {gateway.provider}")
                
            # Process payment through adapter
            gateway_response = await adapter.process_payment(payment_request, gateway)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate fees
            fees = payment_request.amount * (gateway.transaction_fee / Decimal('100'))
            net_amount = payment_request.amount - fees
            
            # Determine status
            status = PaymentStatus.COMPLETED if gateway_response.get('success') else PaymentStatus.FAILED
            
            return PaymentResult(
                result_id=f"result_{payment_request.request_id}_{gateway.gateway_id}",
                request_id=payment_request.request_id,
                gateway_id=gateway.gateway_id,
                status=status,
                transaction_id=gateway_response.get('transaction_id'),
                gateway_response=gateway_response,
                fees=fees,
                net_amount=net_amount,
                processing_time=processing_time,
                error_message=gateway_response.get('error_message')
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return PaymentResult(
                result_id=f"result_{payment_request.request_id}_{gateway.gateway_id}",
                request_id=payment_request.request_id,
                gateway_id=gateway.gateway_id,
                status=PaymentStatus.FAILED,
                processing_time=processing_time,
                error_message=str(e)
            )
            
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """Process payment refund"""
        try:
            # Find original payment
            original_payment = await self._find_payment_by_transaction_id(transaction_id)
            if not original_payment:
                raise Exception(f"Original payment not found for transaction {transaction_id}")
                
            # Get gateway
            gateway = self.gateways.get(original_payment.gateway_id)
            if not gateway:
                raise Exception(f"Gateway {original_payment.gateway_id} not found")
                
            # Get adapter
            adapter = self.gateway_adapters.get(gateway.provider)
            if not adapter:
                raise Exception(f"No adapter found for provider {gateway.provider}")
                
            # Process refund
            refund_response = await adapter.process_refund(transaction_id, amount, gateway)
            
            # Create refund result
            refund_amount = amount or original_payment.net_amount
            status = PaymentStatus.REFUNDED if refund_response.get('success') else PaymentStatus.FAILED
            
            return PaymentResult(
                result_id=f"refund_{transaction_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                request_id=original_payment.request_id,
                gateway_id=gateway.gateway_id,
                status=status,
                transaction_id=refund_response.get('refund_id'),
                gateway_response=refund_response,
                net_amount=-refund_amount,  # Negative for refund
                error_message=refund_response.get('error_message')
            )
            
        except Exception as e:
            logger.error(f"Refund processing failed for transaction {transaction_id}: {e}")
            raise
            
    async def _find_payment_by_transaction_id(self, transaction_id: str) -> Optional[PaymentResult]:
        """Find payment by transaction ID"""
        # In a real implementation, this would query the database
        for result in self.processing_cache.values():
            if result.transaction_id == transaction_id:
                return result
        return None
        
    async def _update_gateway_statistics(self, gateway_id: str, result: PaymentResult):
        """Update gateway performance statistics"""
        if gateway_id not in self.gateway_stats:
            self.gateway_stats[gateway_id] = {
                'total_transactions': 0,
                'successful_transactions': 0,
                'failed_transactions': 0,
                'total_processing_time': 0,
                'total_fees': Decimal('0'),
                'recent_success_rate': 100.0
            }
            
        stats = self.gateway_stats[gateway_id]
        stats['total_transactions'] += 1
        stats['total_processing_time'] += result.processing_time
        stats['total_fees'] += result.fees
        
        if result.status == PaymentStatus.COMPLETED:
            stats['successful_transactions'] += 1
        else:
            stats['failed_transactions'] += 1
            
        # Calculate recent success rate (last 100 transactions)
        if stats['total_transactions'] >= 100:
            recent_success_rate = (stats['successful_transactions'] / stats['total_transactions']) * 100
            stats['recent_success_rate'] = recent_success_rate
            
    async def get_gateway_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all gateways"""
        performance = {}
        
        for gateway_id, gateway in self.gateways.items():
            stats = self.gateway_stats.get(gateway_id, {})
            
            performance[gateway_id] = {
                'gateway_name': gateway.name,
                'provider': gateway.provider,
                'enabled': gateway.enabled,
                'total_transactions': stats.get('total_transactions', 0),
                'success_rate': stats.get('recent_success_rate', gateway.success_rate),
                'avg_processing_time': (
                    stats.get('total_processing_time', 0) / 
                    max(stats.get('total_transactions', 1), 1)
                ),
                'total_fees_collected': float(stats.get('total_fees', 0)),
                'configuration_fee': float(gateway.transaction_fee)
            }
            
        return performance
        
    async def _gateway_health_check_task(self):
        """Background task for gateway health monitoring"""
        while self.running:
            try:
                for gateway_id, gateway in self.gateways.items():
                    adapter = self.gateway_adapters.get(gateway.provider)
                    if adapter:
                        is_healthy = await adapter.health_check(gateway)
                        gateway.enabled = is_healthy
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in gateway health check task: {e}")
                await asyncio.sleep(60)
                
    async def _performance_monitoring_task(self):
        """Background task for performance monitoring"""
        while self.running:
            try:
                # Update gateway performance metrics
                performance = await self.get_gateway_performance()
                
                await self.redis.setex(
                    "payment:gateway:performance", 
                    300, 
                    json.dumps(performance, default=str)
                )
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring task: {e}")
                await asyncio.sleep(60)
                
    async def _statistics_update_task(self):
        """Background task for updating statistics"""
        while self.running:
            try:
                # Save gateway statistics
                await self.redis.setex(
                    "payment:gateway:statistics", 
                    3600, 
                    json.dumps(self.gateway_stats, default=str)
                )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in statistics update task: {e}")
                await asyncio.sleep(300)
                
    async def _save_gateway_configurations(self):
        """Save gateway configurations to Redis"""
        try:
            gateways_config = [asdict(gateway) for gateway in self.gateways.values()]
            await self.redis.set(
                "payment:gateways:config", 
                json.dumps(gateways_config, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to save gateway configurations: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check for orchestrator service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        enabled_gateways = len([g for g in self.gateways.values() if g.enabled])
        total_gateways = len(self.gateways)
        
        return {
            'service': 'payment_gateway_orchestrator',
            'status': 'healthy' if redis_status == "healthy" and enabled_gateways > 0 else 'degraded',
            'redis': redis_status,
            'total_gateways': total_gateways,
            'enabled_gateways': enabled_gateways,
            'cached_results': len(self.processing_cache)
        }
        
    async def shutdown(self):
        """Shutdown orchestrator service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Payment Gateway Orchestrator shut down")

# Gateway adapters (simplified implementations)
class StripeAdapter:
    """Stripe payment gateway adapter"""
    
    async def process_payment(self, payment_request: PaymentRequest, gateway: PaymentGateway) -> Dict[str, Any]:
        # Simulate Stripe API call
        await asyncio.sleep(0.5)  # Simulate network delay
        
        # Simulate success/failure based on gateway success rate
        import random
        success = random.random() * 100 < gateway.success_rate
        
        if success:
            return {
                'success': True,
                'transaction_id': f'stripe_txn_{payment_request.request_id}',
                'status': 'completed'
            }
        else:
            return {
                'success': False,
                'error_message': 'Payment declined by issuer'
            }
            
    async def process_refund(self, transaction_id: str, amount: Optional[Decimal], gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        return {
            'success': True,
            'refund_id': f'stripe_refund_{transaction_id}',
            'status': 'refunded'
        }
        
    async def health_check(self, gateway: PaymentGateway) -> bool:
        return True

class PayPalAdapter:
    """PayPal payment gateway adapter"""
    
    async def process_payment(self, payment_request: PaymentRequest, gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.8)
        
        import random
        success = random.random() * 100 < gateway.success_rate
        
        if success:
            return {
                'success': True,
                'transaction_id': f'paypal_txn_{payment_request.request_id}',
                'status': 'completed'
            }
        else:
            return {
                'success': False,
                'error_message': 'Insufficient funds'
            }
            
    async def process_refund(self, transaction_id: str, amount: Optional[Decimal], gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.5)
        return {
            'success': True,
            'refund_id': f'paypal_refund_{transaction_id}',
            'status': 'refunded'
        }
        
    async def health_check(self, gateway: PaymentGateway) -> bool:
        return True

class AdyenAdapter:
    """Adyen payment gateway adapter"""
    
    async def process_payment(self, payment_request: PaymentRequest, gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.6)
        
        import random
        success = random.random() * 100 < gateway.success_rate
        
        if success:
            return {
                'success': True,
                'transaction_id': f'adyen_txn_{payment_request.request_id}',
                'status': 'completed'
            }
        else:
            return {
                'success': False,
                'error_message': 'Invalid card number'
            }
            
    async def process_refund(self, transaction_id: str, amount: Optional[Decimal], gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.4)
        return {
            'success': True,
            'refund_id': f'adyen_refund_{transaction_id}',
            'status': 'refunded'
        }
        
    async def health_check(self, gateway: PaymentGateway) -> bool:
        return True

class CoinbaseAdapter:
    """Coinbase payment gateway adapter"""
    
    async def process_payment(self, payment_request: PaymentRequest, gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(1.2)  # Crypto transactions take longer
        
        import random
        success = random.random() * 100 < gateway.success_rate
        
        if success:
            return {
                'success': True,
                'transaction_id': f'coinbase_txn_{payment_request.request_id}',
                'status': 'completed'
            }
        else:
            return {
                'success': False,
                'error_message': 'Network congestion, try again later'
            }
            
    async def process_refund(self, transaction_id: str, amount: Optional[Decimal], gateway: PaymentGateway) -> Dict[str, Any]:
        await asyncio.sleep(0.8)
        return {
            'success': True,
            'refund_id': f'coinbase_refund_{transaction_id}',
            'status': 'refunded'
        }
        
    async def health_check(self, gateway: PaymentGateway) -> bool:
        return True

# Example usage
async def create_payment_gateway_orchestrator():
    """Factory function to create payment gateway orchestrator"""
    orchestrator = PaymentGatewayOrchestrator()
    await orchestrator.initialize()
    return orchestrator

if __name__ == "__main__":
    async def main():
        orchestrator = await create_payment_gateway_orchestrator()
        
        # Example payment request
        payment_request = PaymentRequest(
            request_id="pay_123456",
            amount=Decimal("99.99"),
            currency="USD",
            payment_method=PaymentMethod.CREDIT_CARD,
            customer_country="US",
            customer_id="customer_456",
            creator_id="creator_789",
            description="Digital artwork purchase"
        )
        
        # Process payment
        result = await orchestrator.process_payment(payment_request)
        print(f"Payment Result: {result.status}")
        print(f"Gateway Used: {result.gateway_id}")
        print(f"Transaction ID: {result.transaction_id}")
        
        # Get performance metrics
        performance = await orchestrator.get_gateway_performance()
        print("Gateway Performance:", performance)
        
        await orchestrator.shutdown()
        
    asyncio.run(main())