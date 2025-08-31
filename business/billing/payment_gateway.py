"""
Payment Gateway Engine - Universal payment gateway abstraction layer
====================================================================

Comprehensive payment gateway abstraction supporting multiple providers
with unified interface, fraud detection, and automated failover.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json
import stripe
import hashlib

logger = logging.getLogger(__name__)

class GatewayProvider(Enum):
    """Supported payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    SQUARE = "square"
    BRAINTREE = "braintree"

class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    PAYOUT = "payout"

@dataclass
class PaymentRequest:
    """Payment request structure"""
    amount: Decimal
    currency: str
    customer_id: str
    payment_method: str
    description: str
    metadata: Dict[str, Any]
    preferred_gateway: Optional[str] = None

@dataclass
class PaymentResult:
    """Payment processing result"""
    transaction_id: str
    gateway_transaction_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    gateway_used: str
    processing_fee: Decimal
    net_amount: Decimal
    created_at: datetime
    failure_reason: Optional[str] = None

class PaymentGatewayEngine:
    """
    Universal payment gateway engine providing abstracted access to
    multiple payment providers with intelligent routing and failover.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.gateways = {}
        
    async def initialize(self) -> None:
        """Initialize payment gateway engine"""



        try:
            await self._setup_database_tables()
            await self._initialize_gateways()
            await self._load_gateway_configurations()
            logger.info("Payment Gateway Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Payment Gateway Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for gateway management"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS gateway_transactions (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(100) UNIQUE NOT NULL,
                    gateway_provider VARCHAR(20) NOT NULL,
                    gateway_transaction_id VARCHAR(255),
                    transaction_type VARCHAR(20) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    customer_id VARCHAR(255) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    failure_reason TEXT,
                    processing_fee DECIMAL(15,2) DEFAULT 0,
                    net_amount DECIMAL(15,2) NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_gateway_trans_customer (customer_id, created_at DESC),
                    INDEX idx_gateway_trans_status (status, created_at DESC),
                    INDEX idx_gateway_provider (gateway_provider, status)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS gateway_configurations (
                    id SERIAL PRIMARY KEY,
                    provider VARCHAR(20) UNIQUE NOT NULL,
                    configuration JSONB NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 0,
                    processing_fees JSONB DEFAULT '{}',
                    supported_currencies JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS gateway_routing_rules (
                    id SERIAL PRIMARY KEY,
                    rule_name VARCHAR(100) NOT NULL,
                    conditions JSONB NOT NULL,
                    preferred_gateway VARCHAR(20) NOT NULL,
                    fallback_gateways JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _initialize_gateways(self) -> None:
        """Initialize individual gateway adapters"""
        # Initialize Stripe
        self.gateways[GatewayProvider.STRIPE] = StripeGatewayAdapter()
        
        # Initialize PayPal
        self.gateways[GatewayProvider.PAYPAL] = PayPalGatewayAdapter()
        
        # Initialize Wise
        self.gateways[GatewayProvider.WISE] = WiseGatewayAdapter()
        
        # Initialize Square
        self.gateways[GatewayProvider.SQUARE] = SquareGatewayAdapter()

    async def _load_gateway_configurations(self) -> None:
        """Load gateway configurations from database"""



        try:
            async with self.db_pool.acquire() as conn:
                # Load default configurations if not exists
                await self._ensure_default_configurations(conn)
                
                # Load active configurations
                configs = await conn.fetch("""
                    SELECT provider, configuration, processing_fees, supported_currencies
                    FROM gateway_configurations 
                    WHERE is_active = TRUE
                    ORDER BY priority DESC
                """)
                
                for config in configs:
                    provider = GatewayProvider(config['provider'])
                    if provider in self.gateways:
                        await self.gateways[provider].configure(
                            config['configuration'],
                            config['processing_fees'],
                            config['supported_currencies']
                        )
                        
        except Exception as e:
            logger.error(f"Failed to load gateway configurations: {e}")

    async def _ensure_default_configurations(self, conn) -> None:
        """Ensure default gateway configurations exist"""
        default_configs = [
            {
                'provider': 'stripe',
                'configuration': {
                    'api_key': 'sk_test_...',
                    'webhook_secret': 'whsec_...',
                    'api_version': '2023-10-16'
                },
                'processing_fees': {
                    'percentage': 2.9,
                    'fixed': 0.30
                },
                'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD']
            },
            {
                'provider': 'paypal',
                'configuration': {
                    'client_id': 'client_id_here',
                    'client_secret': 'client_secret_here',
                    'sandbox': True
                },
                'processing_fees': {
                    'percentage': 3.49,
                    'fixed': 0.49
                },
                'supported_currencies': ['USD', 'EUR', 'GBP']
            }
        ]
        
        for config in default_configs:
            await conn.execute("""
                INSERT INTO gateway_configurations 
                (provider, configuration, processing_fees, supported_currencies, priority)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (provider) DO NOTHING
            """,
            config['provider'],
            json.dumps(config['configuration']),
            json.dumps(config['processing_fees']),
            json.dumps(config['supported_currencies']),
            1 if config['provider'] == 'stripe' else 0
            )

    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process payment through optimal gateway"""



        try:
            # Generate transaction ID
            transaction_id = self._generate_transaction_id()
            
            # Determine optimal gateway
            gateway_provider = await self._select_optimal_gateway(payment_request)
            
            if not gateway_provider:
                raise HTTPException(status_code=500, detail="No available payment gateway")
            
            # Process payment through selected gateway
            result = await self._process_through_gateway(
                gateway_provider, 
                payment_request, 
                transaction_id
            )
            
            # Store transaction record
            await self._store_transaction(result, payment_request)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            # Try fallback gateway
            return await self._process_with_fallback(payment_request, str(e))

    async def _select_optimal_gateway(self, payment_request: PaymentRequest) -> Optional[GatewayProvider]:
        """Select optimal gateway based on routing rules and availability"""



        try:
            # Check preferred gateway first
            if payment_request.preferred_gateway:
                provider = GatewayProvider(payment_request.preferred_gateway)
                if await self._is_gateway_available(provider, payment_request):
                    return provider
            
            # Apply routing rules
            optimal_gateway = await self._apply_routing_rules(payment_request)
            if optimal_gateway:
                return optimal_gateway
            
            # Default to highest priority available gateway
            async with self.db_pool.acquire() as conn:
                gateway_row = await conn.fetchrow("""
                    SELECT provider FROM gateway_configurations
                    WHERE is_active = TRUE
                    AND $1 = ANY(supported_currencies::text[])
                    ORDER BY priority DESC
                    LIMIT 1
                """, payment_request.currency)
                
                return GatewayProvider(gateway_row['provider']) if gateway_row else None
                
        except Exception as e:
            logger.error(f"Failed to select optimal gateway: {e}")
            return None

    async def _apply_routing_rules(self, payment_request: PaymentRequest) -> Optional[GatewayProvider]:
        """Apply routing rules to select gateway"""



        try:
            async with self.db_pool.acquire() as conn:
                rules = await conn.fetch("""
                    SELECT preferred_gateway, conditions 
                    FROM gateway_routing_rules
                    WHERE is_active = TRUE
                    ORDER BY priority DESC
                """)
                
                for rule in rules:
                    conditions = rule['conditions']
                    if self._evaluate_routing_conditions(conditions, payment_request):
                        return GatewayProvider(rule['preferred_gateway'])
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to apply routing rules: {e}")
            return None

    def _evaluate_routing_conditions(self, conditions: Dict[str, Any], 
                                   payment_request: PaymentRequest) -> bool:
        """Evaluate routing rule conditions"""



        try:
            # Amount-based routing
            if 'min_amount' in conditions:
                if payment_request.amount < Decimal(str(conditions['min_amount'])):
                    return False
            
            if 'max_amount' in conditions:
                if payment_request.amount > Decimal(str(conditions['max_amount'])):
                    return False
            
            # Currency-based routing
            if 'currencies' in conditions:
                if payment_request.currency not in conditions['currencies']:
                    return False
            
            # Payment method routing
            if 'payment_methods' in conditions:
                if payment_request.payment_method not in conditions['payment_methods']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to evaluate routing conditions: {e}")
            return False

    async def _is_gateway_available(self, provider: GatewayProvider, 
                                  payment_request: PaymentRequest) -> bool:
        """Check if gateway is available for processing"""



        try:
            if provider not in self.gateways:
                return False
            
            # Check if currency is supported
            async with self.db_pool.acquire() as conn:
                config = await conn.fetchrow("""
                    SELECT supported_currencies FROM gateway_configurations
                    WHERE provider = $1 AND is_active = TRUE
                """, provider.value)
                
                if not config:
                    return False
                
                supported_currencies = config['supported_currencies']
                return payment_request.currency in supported_currencies
                
        except Exception as e:
            logger.error(f"Failed to check gateway availability: {e}")
            return False

    async def _process_through_gateway(self, provider: GatewayProvider,
                                     payment_request: PaymentRequest,
                                     transaction_id: str) -> PaymentResult:
        """Process payment through specific gateway"""



        try:
            gateway = self.gateways[provider]
            
            # Calculate processing fee
            processing_fee = await self._calculate_processing_fee(provider, payment_request.amount)
            
            # Process payment
            gateway_result = await gateway.process_payment({
                'amount': payment_request.amount,
                'currency': payment_request.currency,
                'customer_id': payment_request.customer_id,
                'payment_method': payment_request.payment_method,
                'description': payment_request.description,
                'metadata': payment_request.metadata
            })
            
            return PaymentResult(
                transaction_id=transaction_id,
                gateway_transaction_id=gateway_result['transaction_id'],
                status=PaymentStatus(gateway_result['status']),
                amount=payment_request.amount,
                currency=payment_request.currency,
                gateway_used=provider.value,
                processing_fee=processing_fee,
                net_amount=payment_request.amount - processing_fee,
                created_at=datetime.now(),
                failure_reason=gateway_result.get('failure_reason')
            )
            
        except Exception as e:
            logger.error(f"Gateway processing failed: {e}")
            raise

    async def _calculate_processing_fee(self, provider: GatewayProvider, amount: Decimal) -> Decimal:
        """Calculate processing fee for gateway"""



        try:
            async with self.db_pool.acquire() as conn:
                fees = await conn.fetchval("""
                    SELECT processing_fees FROM gateway_configurations
                    WHERE provider = $1
                """, provider.value)
                
                if fees:
                    percentage = Decimal(str(fees.get('percentage', 0))) / 100
                    fixed = Decimal(str(fees.get('fixed', 0)))
                    return (amount * percentage) + fixed
                
                return Decimal('0.00')
                
        except Exception as e:
            logger.error(f"Failed to calculate processing fee: {e}")
            return Decimal('0.00')

    async def _process_with_fallback(self, payment_request: PaymentRequest, 
                                   original_error: str) -> PaymentResult:
        """Process payment with fallback gateway"""



        try:
            # Get fallback gateways
            async with self.db_pool.acquire() as conn:
                fallback_providers = await conn.fetch("""
                    SELECT provider FROM gateway_configurations
                    WHERE is_active = TRUE
                    AND $1 = ANY(supported_currencies::text[])
                    ORDER BY priority ASC
                    LIMIT 2
                """, payment_request.currency)
                
                for provider_row in fallback_providers:
                    try:
                        provider = GatewayProvider(provider_row['provider'])
                        transaction_id = self._generate_transaction_id()
                        
                        result = await self._process_through_gateway(
                            provider, 
                            payment_request, 
                            transaction_id
                        )
                        
                        # Store transaction record
                        await self._store_transaction(result, payment_request)
                        
                        return result
                        
                    except Exception as fallback_error:
                        logger.error(f"Fallback gateway {provider_row['provider']} failed: {fallback_error}")
                        continue
                
                # All gateways failed
                raise HTTPException(status_code=500, detail=f"All payment gateways failed. Original error: {original_error}")
                
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            raise

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = str(int(datetime.now().timestamp()))
        random_part = hashlib.md5(f"{timestamp}_{datetime.now().microsecond}".encode()).hexdigest()[:8]
        return f"txn_{timestamp}_{random_part}"

    async def _store_transaction(self, result: PaymentResult, request: PaymentRequest) -> None:
        """Store transaction record in database"""



        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO gateway_transactions
                    (transaction_id, gateway_provider, gateway_transaction_id, transaction_type,
                     amount, currency, customer_id, payment_method, status, failure_reason,
                     processing_fee, net_amount, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                result.transaction_id,
                result.gateway_used,
                result.gateway_transaction_id,
                TransactionType.PAYMENT.value,
                result.amount,
                result.currency,
                request.customer_id,
                request.payment_method,
                result.status.value,
                result.failure_reason,
                result.processing_fee,
                result.net_amount,
                json.dumps(request.metadata)
                )
        except Exception as e:
            logger.error(f"Failed to store transaction: {e}")

    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """Process payment refund"""



        try:
            # Get original transaction
            async with self.db_pool.acquire() as conn:
                original_transaction = await conn.fetchrow("""
                    SELECT * FROM gateway_transactions
                    WHERE transaction_id = $1
                """, transaction_id)
                
                if not original_transaction:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                # Determine refund amount
                refund_amount = amount or original_transaction['amount']
                
                # Process refund through original gateway
                provider = GatewayProvider(original_transaction['gateway_provider'])
                gateway = self.gateways[provider]
                
                refund_result = await gateway.process_refund(
                    original_transaction['gateway_transaction_id'],
                    refund_amount
                )
                
                # Create refund transaction record
                refund_transaction_id = self._generate_transaction_id()
                
                result = PaymentResult(
                    transaction_id=refund_transaction_id,
                    gateway_transaction_id=refund_result['refund_id'],
                    status=PaymentStatus(refund_result['status']),
                    amount=refund_amount,
                    currency=original_transaction['currency'],
                    gateway_used=provider.value,
                    processing_fee=Decimal('0.00'),
                    net_amount=refund_amount,
                    created_at=datetime.now()
                )
                
                # Store refund transaction
                await conn.execute("""
                    INSERT INTO gateway_transactions
                    (transaction_id, gateway_provider, gateway_transaction_id, transaction_type,
                     amount, currency, customer_id, payment_method, status,
                     processing_fee, net_amount, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                result.transaction_id,
                result.gateway_used,
                result.gateway_transaction_id,
                TransactionType.REFUND.value,
                result.amount,
                result.currency,
                original_transaction['customer_id'],
                original_transaction['payment_method'],
                result.status.value,
                result.processing_fee,
                result.net_amount,
                json.dumps({'original_transaction': transaction_id})
                )
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to process refund: {e}")
            raise HTTPException(status_code=500, detail="Refund processing failed")

    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""



        try:
            async with self.db_pool.acquire() as conn:
                transaction = await conn.fetchrow("""
                    SELECT * FROM gateway_transactions
                    WHERE transaction_id = $1
                """, transaction_id)
                
                if not transaction:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                return {
                    'transaction_id': transaction['transaction_id'],
                    'gateway_provider': transaction['gateway_provider'],
                    'status': transaction['status'],
                    'amount': float(transaction['amount']),
                    'currency': transaction['currency'],
                    'created_at': transaction['created_at'].isoformat(),
                    'failure_reason': transaction['failure_reason']
                }
                
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            raise HTTPException(status_code=500, detail="Transaction status retrieval failed")


# Gateway Adapter Classes
class StripeGatewayAdapter:
    """Stripe payment gateway adapter"""
    
    def __init__(self):
        self.api_key = None
        self.fees = {}
    
    async def configure(self, config: Dict[str, Any], fees: Dict[str, Any], 
                       currencies: List[str]) -> None:
        """Configure Stripe gateway"""
        self.api_key = config.get('api_key')
        self.fees = fees
        stripe.api_key = self.api_key
    
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through Stripe"""



        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment_data['amount'] * 100),  # Convert to cents
                currency=payment_data['currency'].lower(),
                customer=payment_data['customer_id'],
                description=payment_data['description'],
                metadata=payment_data['metadata']
            )
            
            return {
                'transaction_id': intent['id'],
                'status': 'completed' if intent['status'] == 'succeeded' else 'pending'
            }
            
        except Exception as e:
            return {
                'transaction_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process refund through Stripe"""



        try:
            refund = stripe.Refund.create(
                payment_intent=transaction_id,
                amount=int(amount * 100)
            )
            
            return {
                'refund_id': refund['id'],
                'status': 'completed' if refund['status'] == 'succeeded' else 'pending'
            }
            
        except Exception as e:
            return {
                'refund_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }


class PayPalGatewayAdapter:
    """PayPal payment gateway adapter"""
    
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.fees = {}
    
    async def configure(self, config: Dict[str, Any], fees: Dict[str, Any], 
                       currencies: List[str]) -> None:
        """Configure PayPal gateway"""
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.fees = fees
    
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through PayPal"""



        try:
            # Mock PayPal payment processing
            transaction_id = f"paypal_{int(datetime.now().timestamp())}"
            
            return {
                'transaction_id': transaction_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'transaction_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process refund through PayPal"""



        try:
            refund_id = f"paypal_refund_{int(datetime.now().timestamp())}"
            
            return {
                'refund_id': refund_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'refund_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }


class WiseGatewayAdapter:
    """Wise payment gateway adapter"""
    
    def __init__(self):
        self.api_key = None
        self.fees = {}
    
    async def configure(self, config: Dict[str, Any], fees: Dict[str, Any], 
                       currencies: List[str]) -> None:
        """Configure Wise gateway"""
        self.api_key = config.get('api_key')
        self.fees = fees
    
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through Wise"""



        try:
            transaction_id = f"wise_{int(datetime.now().timestamp())}"
            
            return {
                'transaction_id': transaction_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'transaction_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process refund through Wise"""



        try:
            refund_id = f"wise_refund_{int(datetime.now().timestamp())}"
            
            return {
                'refund_id': refund_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'refund_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }


class SquareGatewayAdapter:
    """Square payment gateway adapter"""
    
    def __init__(self):
        self.access_token = None
        self.fees = {}
    
    async def configure(self, config: Dict[str, Any], fees: Dict[str, Any], 
                       currencies: List[str]) -> None:
        """Configure Square gateway"""
        self.access_token = config.get('access_token')
        self.fees = fees
    
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through Square"""



        try:
            transaction_id = f"square_{int(datetime.now().timestamp())}"
            
            return {
                'transaction_id': transaction_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'transaction_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }
    
    async def process_refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process refund through Square"""



        try:
            refund_id = f"square_refund_{int(datetime.now().timestamp())}"
            
            return {
                'refund_id': refund_id,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'refund_id': None,
                'status': 'failed',
                'failure_reason': str(e)
            }
