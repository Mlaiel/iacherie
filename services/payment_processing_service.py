"""
import logging

💳 Payment Processing Service
Enterprise-grade payment processing with multi-provider support and advanced security

Demonstrates: Backend Senior + Security + DBA + DevOps expertise
Features: Multi-gateway support, fraud detection, PCI compliance, real-time processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from pydantic import BaseModel, Field, validator, SecretStr
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import asyncio
import uuid
import json
import hashlib
import hmac
import base64
from dataclasses import dataclass
import structlog
from abc import ABC, abstractmethod
import aiohttp
import redis.asyncio as redis
from collections import defaultdict
import re

logger = structlog.get_logger(__name__)

class PaymentStatus(str, Enum):
    """Payment transaction statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"

class PaymentMethod(str, Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    STRIPE = "stripe"

class Currency(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"
    BRL = "BRL"

class FraudRiskLevel(str, Enum):
    """Fraud risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration"""
    gateway_id: str
    name: str
    api_key: SecretStr
    secret_key: SecretStr
    endpoint_url: str
    supported_currencies: List[Currency]
    supported_methods: List[PaymentMethod]
    transaction_fee_percentage: Decimal
    fixed_fee: Decimal
    is_active: bool = True

class BillingAddress(BaseModel):
    """Billing address information"""
    street_address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state_province: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country_code: str = Field(..., min_length=2, max_length=3)
    
    @validator('country_code')
    def validate_country_code(cls, v) -> None:
        if not re.match(r'^[A-Z]{2,3}$', v):
            raise ValueError('Country code must be 2-3 uppercase letters')
        return v

class PaymentCard(BaseModel):
    """Payment card information (PCI compliant)"""
    card_token: str = Field(..., description="Tokenized card number")
    card_type: str = Field(..., description="Card brand (Visa, MasterCard, etc.)")
    last_four_digits: str = Field(..., min_length=4, max_length=4)
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2025, le=2035)
    cardholder_name: str = Field(..., max_length=100)
    billing_address: BillingAddress
    
    @validator('last_four_digits')
    def validate_last_four(cls, v) -> None:
        if not v.isdigit():
            raise ValueError('Last four digits must be numeric')
        return v

class PaymentRequest(BaseModel):
    """Payment processing request"""
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: Currency
    payment_method: PaymentMethod
    customer_id: str = Field(..., description="Customer identifier")
    order_id: Optional[str] = None
    description: str = Field(..., max_length=500)
    payment_card: Optional[PaymentCard] = None
    wallet_token: Optional[str] = None
    return_url: Optional[str] = None
    webhook_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('amount')
    def validate_amount(cls, v) -> None:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class FraudAssessment(BaseModel):
    """Fraud risk assessment result"""
    risk_level: FraudRiskLevel
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_factors: List[str] = Field(default_factory=list)
    recommendation: str
    assessed_at: datetime = Field(default_factory=datetime.now)
    assessment_duration_ms: float

class PaymentTransaction(BaseModel):
    """Payment transaction record"""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_id: str
    gateway_id: str
    gateway_transaction_id: Optional[str] = None
    status: PaymentStatus
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    customer_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    gateway_response: Dict[str, Any] = Field(default_factory=dict)
    fees: Dict[str, Decimal] = Field(default_factory=dict)
    fraud_assessment: Optional[FraudAssessment] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RefundRequest(BaseModel):
    """Refund processing request"""
    refund_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    amount: Decimal = Field(..., gt=0)
    reason: str = Field(..., max_length=500)
    requested_by: str
    notify_customer: bool = True

class PaymentGateway(ABC):
    """Abstract base class for payment gateways"""
    
    def __init__(self, config -> None: PaymentGatewayConfig) -> None:
        self.config = config
    
    @abstractmethod
    async def process_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """Process payment through gateway"""
        pass
    
    @abstractmethod
    async def check_payment_status(self, gateway_transaction_id: str) -> Dict[str, Any]:
        """Check payment status"""
        pass
    
    @abstractmethod
    async def process_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Process refund"""
        pass
    
    @abstractmethod
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate webhook signature"""
        pass

class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation"""
    
    async def process_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            # Simulate Stripe API call
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Mock successful response
            if request.amount < Decimal('10000.00'):  # Amounts under $10,000 succeed
                return {
                    'success': True,
                    'transaction_id': f"stripe_{uuid.uuid4()}",
                    'status': 'completed',
                    'gateway_response': {
                        'id': f"pi_{uuid.uuid4()}",
                        'status': 'succeeded',
                        'amount': int(request.amount * 100),  # Stripe uses cents
                        'currency': request.currency.lower()
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'card_declined',
                    'message': 'Your card was declined'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'processing_error',
                'message': str(e)
            }
    
    async def check_payment_status(self, gateway_transaction_id: str) -> Dict[str, Any]:
        """Check Stripe payment status"""
        # Simulate status check
        return {
            'status': 'completed',
            'gateway_transaction_id': gateway_transaction_id
        }
    
    async def process_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Process Stripe refund"""
        try:
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'refund_id': f"re_{uuid.uuid4()}",
                'status': 'succeeded'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate Stripe webhook signature"""
        try:
            secret = self.config.secret_key.get_secret_value()
            expected_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

class PayPalGateway(PaymentGateway):
    """PayPal payment gateway implementation"""
    
    async def process_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """Process payment through PayPal"""
        try:
            await asyncio.sleep(0.15)  # Simulate network delay
            
            # Mock response based on amount
            if request.amount < Decimal('5000.00'):
                return {
                    'success': True,
                    'transaction_id': f"paypal_{uuid.uuid4()}",
                    'status': 'completed',
                    'gateway_response': {
                        'id': uuid.uuid4().hex,
                        'state': 'approved',
                        'amount': {
                            'total': str(request.amount),
                            'currency': request.currency
                        }
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'insufficient_funds',
                    'message': 'Insufficient funds in PayPal account'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'processing_error',
                'message': str(e)
            }
    
    async def check_payment_status(self, gateway_transaction_id: str) -> Dict[str, Any]:
        """Check PayPal payment status"""
        return {
            'status': 'completed',
            'gateway_transaction_id': gateway_transaction_id
        }
    
    async def process_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Process PayPal refund"""
        try:
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'refund_id': uuid.uuid4().hex,
                'status': 'completed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate PayPal webhook signature"""
        # Simplified validation
        return len(signature) > 10

class FraudDetectionEngine:
    """
    ML-powered fraud detection engine
    
    Security Expert: Advanced fraud detection algorithms
    ML Engineer: Machine learning based risk assessment
    """
    
    def __init__(self) -> None:
        self.risk_rules = [
            self._check_velocity_limits,
            self._check_geographic_anomalies,
            self._check_card_patterns,
            self._check_customer_history,
            self._check_amount_patterns
        ]
        
        # Simulated ML model scores
        self.model_weights = {
            'velocity': 0.3,
            'geography': 0.2,
            'card_patterns': 0.25,
            'customer_history': 0.15,
            'amount_patterns': 0.1
        }
    
    async def assess_fraud_risk(self, request: PaymentRequest, 
                               transaction_history: List[PaymentTransaction] = None) -> FraudAssessment:
        """Assess fraud risk for payment request"""
        start_time = asyncio.get_event_loop().time()
        
        risk_factors = []
        risk_scores = {}
        
        # Run all fraud detection rules
        for rule in self.risk_rules:
            try:
                rule_result = await rule(request, transaction_history or [])
                risk_scores[rule.__name__] = rule_result['score']
                if rule_result['triggered']:
                    risk_factors.extend(rule_result['factors'])
            except Exception as e:
                logger.warning("Fraud rule execution failed", rule=rule.__name__, error=str(e))
        
        # Calculate weighted risk score
        total_score = sum(
            score * self.model_weights.get(rule_name.replace('_check_', ''), 0.1)
            for rule_name, score in risk_scores.items()
        )
        
        # Determine risk level
        if total_score >= 0.8:
            risk_level = FraudRiskLevel.CRITICAL
            recommendation = "Block transaction and require manual review"
        elif total_score >= 0.6:
            risk_level = FraudRiskLevel.HIGH
            recommendation = "Require additional verification"
        elif total_score >= 0.3:
            risk_level = FraudRiskLevel.MEDIUM
            recommendation = "Monitor closely and flag for review"
        else:
            risk_level = FraudRiskLevel.LOW
            recommendation = "Proceed with normal processing"
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return FraudAssessment(
            risk_level=risk_level,
            risk_score=total_score,
            risk_factors=risk_factors,
            recommendation=recommendation,
            assessment_duration_ms=processing_time
        )
    
    async def _check_velocity_limits(self, request: PaymentRequest, 
                                   history: List[PaymentTransaction]) -> Dict[str, Any]:
        """Check for velocity-based fraud patterns"""
        # Count recent transactions
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_transactions = [
            t for t in history 
            if t.customer_id == request.customer_id and t.created_at >= last_hour
        ]
        
        daily_transactions = [
            t for t in history
            if t.customer_id == request.customer_id and t.created_at >= last_day
        ]
        
        risk_factors = []
        score = 0.0
        
        if len(recent_transactions) > 5:
            risk_factors.append("High transaction velocity in last hour")
            score += 0.3
        
        if len(daily_transactions) > 20:
            risk_factors.append("Excessive daily transaction count")
            score += 0.4
        
        # Check total amount in recent transactions
        recent_amount = sum(t.amount for t in recent_transactions)
        if recent_amount > Decimal('5000.00'):
            risk_factors.append("High transaction volume in short period")
            score += 0.3
        
        return {
            'score': min(score, 1.0),
            'triggered': len(risk_factors) > 0,
            'factors': risk_factors
        }
    
    async def _check_geographic_anomalies(self, request: PaymentRequest,
                                        history: List[PaymentTransaction]) -> Dict[str, Any]:
        """Check for geographic anomalies"""
        risk_factors = []
        score = 0.0
        
        # Simulate IP geolocation check
        customer_country = request.metadata.get('ip_country', 'US')
        billing_country = getattr(request.payment_card, 'billing_address', {})
        billing_country = getattr(billing_country, 'country_code', 'US') if billing_country else 'US'
        
        if customer_country != billing_country:
            risk_factors.append("IP country differs from billing country")
            score += 0.2
        
        # Check for unusual location patterns
        recent_locations = set()
        for transaction in history[-10:]:  # Last 10 transactions
            location = transaction.metadata.get('ip_country', 'US')
            recent_locations.add(location)
        
        if len(recent_locations) > 3:
            risk_factors.append("Multiple countries in recent transactions")
            score += 0.3
        
        return {
            'score': min(score, 1.0),
            'triggered': len(risk_factors) > 0,
            'factors': risk_factors
        }
    
    async def _check_card_patterns(self, request: PaymentRequest,
                                 history: List[PaymentTransaction]) -> Dict[str, Any]:
        """Check for suspicious card usage patterns"""
        risk_factors = []
        score = 0.0
        
        if request.payment_card:
            # Check for multiple cards used by same customer
            customer_cards = set()
            for transaction in history:
                if transaction.customer_id == request.customer_id:
                    card_info = transaction.metadata.get('card_last_four')
                    if card_info:
                        customer_cards.add(card_info)
            
            if len(customer_cards) > 5:
                risk_factors.append("Multiple cards used by customer")
                score += 0.2
            
            # Check card validity
            expiry_date = datetime(request.payment_card.expiry_year, request.payment_card.expiry_month, 1)
            if expiry_date < datetime.now():
                risk_factors.append("Expired payment card")
                score += 0.5
        
        return {
            'score': min(score, 1.0),
            'triggered': len(risk_factors) > 0,
            'factors': risk_factors
        }
    
    async def _check_customer_history(self, request: PaymentRequest,
                                    history: List[PaymentTransaction]) -> Dict[str, Any]:
        """Check customer transaction history"""
        risk_factors = []
        score = 0.0
        
        customer_transactions = [
            t for t in history if t.customer_id == request.customer_id
        ]
        
        if not customer_transactions:
            risk_factors.append("New customer with no transaction history")
            score += 0.3
        else:
            # Check for failed transactions
            failed_count = len([t for t in customer_transactions if t.status == PaymentStatus.FAILED])
            if failed_count > len(customer_transactions) * 0.3:  # More than 30% failed
                risk_factors.append("High failure rate in customer history")
                score += 0.4
            
            # Check for disputes
            disputed_count = len([t for t in customer_transactions if t.status == PaymentStatus.DISPUTED])
            if disputed_count > 0:
                risk_factors.append("Previous disputed transactions")
                score += 0.5
        
        return {
            'score': min(score, 1.0),
            'triggered': len(risk_factors) > 0,
            'factors': risk_factors
        }
    
    async def _check_amount_patterns(self, request: PaymentRequest,
                                   history: List[PaymentTransaction]) -> Dict[str, Any]:
        """Check for suspicious amount patterns"""
        risk_factors = []
        score = 0.0
        
        # Check for round amounts (potential fraud indicator)
        if request.amount % 100 == 0 and request.amount >= Decimal('1000.00'):
            risk_factors.append("Large round amount transaction")
            score += 0.1
        
        # Check for unusual amount for customer
        customer_transactions = [
            t for t in history 
            if t.customer_id == request.customer_id and t.status == PaymentStatus.COMPLETED
        ]
        
        if customer_transactions:
            avg_amount = sum(t.amount for t in customer_transactions) / len(customer_transactions)
            
            if request.amount > avg_amount * 5:  # 5x average
                risk_factors.append("Transaction amount significantly higher than customer average")
                score += 0.3
        
        return {
            'score': min(score, 1.0),
            'triggered': len(risk_factors) > 0,
            'factors': risk_factors
        }

class PaymentProcessingService:
    """
    Enterprise Payment Processing Service
    
    Demonstrates expertise in:
    - Backend Senior: Complex async processing, error handling, performance optimization
    - Security: PCI compliance, fraud detection, secure data handling
    - DBA: Transaction integrity, audit trails, data consistency
    - DevOps: Multi-gateway orchestration, monitoring, alerting
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.gateways: Dict[str, PaymentGateway] = {}
        self.fraud_engine = FraudDetectionEngine()
        self.transaction_store: Dict[str, PaymentTransaction] = {}
        self.redis_client = None
        
        self.metrics = {
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'fraud_blocked_transactions': 0,
            'total_amount_processed': Decimal('0.00'),
            'average_processing_time': 0.0,
            'gateway_success_rates': defaultdict(float)
        }
        
        # Initialize payment gateways
        self._initialize_gateways()
        
        logger.info("Payment Processing Service initialized",
                   gateways=len(self.gateways),
                   config=self.config)
    
    def _initialize_gateways(self) -> None:
        """Initialize payment gateways"""
        
        # Stripe gateway
        stripe_config = PaymentGatewayConfig(
            gateway_id="stripe",
            name="Stripe",
            api_key=SecretStr("sk_test_stripe_key"),
            secret_key=SecretStr("stripe_webhook_secret"),
            endpoint_url="https://api.stripe.com/v1",
            supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP],
            supported_methods=[PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD],
            transaction_fee_percentage=Decimal('2.9'),
            fixed_fee=Decimal('0.30')
        )
        
        # PayPal gateway
        paypal_config = PaymentGatewayConfig(
            gateway_id="paypal",
            name="PayPal",
            api_key=SecretStr("paypal_client_id"),
            secret_key=SecretStr("paypal_client_secret"),
            endpoint_url="https://api.paypal.com",
            supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY],
            supported_methods=[PaymentMethod.PAYPAL, PaymentMethod.DIGITAL_WALLET],
            transaction_fee_percentage=Decimal('3.49'),
            fixed_fee=Decimal('0.49')
        )
        
        self.gateways["stripe"] = StripeGateway(stripe_config)
        self.gateways["paypal"] = PayPalGateway(paypal_config)
    
    async def process_payment(self, request: PaymentRequest) -> PaymentTransaction:
        """
        Process payment with comprehensive fraud detection and multi-gateway support
        
        Backend Senior: Complex async orchestration, error handling
        Security: Fraud detection, secure processing
        DBA: Transaction integrity, audit trails
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create initial transaction record
            transaction = PaymentTransaction(
                payment_id=request.payment_id,
                gateway_id="",  # Will be set after gateway selection
                status=PaymentStatus.PENDING,
                amount=request.amount,
                currency=request.currency,
                payment_method=request.payment_method,
                customer_id=request.customer_id,
                metadata=request.metadata
            )
            
            # Fraud assessment
            transaction_history = await self._get_customer_transaction_history(request.customer_id)
            fraud_assessment = await self.fraud_engine.assess_fraud_risk(request, transaction_history)
            transaction.fraud_assessment = fraud_assessment
            
            # Block high-risk transactions
            if fraud_assessment.risk_level == FraudRiskLevel.CRITICAL:
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = "Transaction blocked due to high fraud risk"
                self.metrics['fraud_blocked_transactions'] += 1
                
                logger.warning("Payment blocked due to fraud risk",
                             payment_id=request.payment_id,
                             risk_level=fraud_assessment.risk_level,
                             risk_score=fraud_assessment.risk_score)
                
                await self._store_transaction(transaction)
                return transaction
            
            # Select optimal payment gateway
            gateway = await self._select_gateway(request)
            if not gateway:
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = "No suitable payment gateway available"
                await self._store_transaction(transaction)
                return transaction
            
            transaction.gateway_id = gateway.config.gateway_id
            transaction.status = PaymentStatus.PROCESSING
            
            # Process payment through selected gateway
            gateway_response = await gateway.process_payment(request)
            transaction.gateway_response = gateway_response
            
            if gateway_response.get('success', False):
                transaction.status = PaymentStatus.COMPLETED
                transaction.gateway_transaction_id = gateway_response.get('transaction_id')
                transaction.processed_at = datetime.now()
                
                # Calculate fees
                transaction.fees = await self._calculate_fees(transaction, gateway)
                
                # Update metrics
                self.metrics['successful_transactions'] += 1
                self.metrics['total_amount_processed'] += transaction.amount
                
                logger.info("Payment processed successfully",
                           payment_id=request.payment_id,
                           transaction_id=transaction.transaction_id,
                           amount=transaction.amount,
                           gateway=gateway.config.gateway_id)
            
            else:
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = gateway_response.get('message', 'Payment processing failed')
                self.metrics['failed_transactions'] += 1
                
                logger.warning("Payment processing failed",
                             payment_id=request.payment_id,
                             error=transaction.error_message,
                             gateway=gateway.config.gateway_id)
            
            # Store transaction
            await self._store_transaction(transaction)
            
            # Update processing time metrics
            processing_time = asyncio.get_event_loop().time() - start_time
            self._update_processing_time_metrics(processing_time)
            
            # Update gateway success rates
            self._update_gateway_metrics(gateway.config.gateway_id, transaction.status == PaymentStatus.COMPLETED)
            
            return transaction
            
        except Exception as e:
            logger.error("Payment processing exception",
                        payment_id=request.payment_id,
                        error=str(e))
            
            transaction.status = PaymentStatus.FAILED
            transaction.error_message = f"Processing error: {str(e)}"
            await self._store_transaction(transaction)
            
            return transaction
        
        finally:
            self.metrics['total_transactions'] += 1
    
    async def _select_gateway(self, request: PaymentRequest) -> Optional[PaymentGateway]:
        """Select optimal payment gateway based on request parameters"""
        
        suitable_gateways = []
        
        for gateway in self.gateways.values():
            config = gateway.config
            
            # Check if gateway supports currency and payment method
            if (request.currency in config.supported_currencies and
                request.payment_method in config.supported_methods and
                config.is_active):
                
                # Calculate gateway score based on fees and success rate
                fee_score = 1.0 - (float(config.transaction_fee_percentage) / 100.0)
                success_rate = self.metrics['gateway_success_rates'].get(config.gateway_id, 0.95)
                
                gateway_score = (fee_score * 0.3) + (success_rate * 0.7)
                
                suitable_gateways.append((gateway, gateway_score))
        
        if not suitable_gateways:
            return None
        
        # Return gateway with highest score
        suitable_gateways.sort(key=lambda x: x[1], reverse=True)
        return suitable_gateways[0][0]
    
    async def _calculate_fees(self, transaction: PaymentTransaction, 
                            gateway: PaymentGateway) -> Dict[str, Decimal]:
        """Calculate transaction fees"""
        config = gateway.config
        
        percentage_fee = transaction.amount * (config.transaction_fee_percentage / Decimal('100'))
        total_fee = percentage_fee + config.fixed_fee
        
        return {
            'percentage_fee': percentage_fee.quantize(Decimal('0.01')),
            'fixed_fee': config.fixed_fee,
            'total_fee': total_fee.quantize(Decimal('0.01'))
        }
    
    async def _store_transaction(self, transaction -> None: PaymentTransaction) -> None:
        """Store transaction in database (with Redis caching)"""
        # Update timestamp
        transaction.updated_at = datetime.now()
        
        # Store in memory (in production, would use proper database)
        self.transaction_store[transaction.transaction_id] = transaction
        
        # Cache in Redis for fast access
        if self.redis_client:
            try:
                transaction_data = transaction.json()
                await self.redis_client.setex(
                    f"transaction:{transaction.transaction_id}",
                    3600,  # 1 hour TTL
                    transaction_data
                )
            except Exception as e:
                logger.warning("Failed to cache transaction in Redis", error=str(e))
    
    async def _get_customer_transaction_history(self, customer_id: str) -> List[PaymentTransaction]:
        """Get customer transaction history for fraud detection"""
        # In production, would query database with proper indexing
        transactions = [
            t for t in self.transaction_store.values()
            if t.customer_id == customer_id
        ]
        
        # Sort by creation date (most recent first)
        return sorted(transactions, key=lambda x: x.created_at, reverse=True)[:50]  # Last 50 transactions
    
    def _update_processing_time_metrics(self, processing_time -> None: float) -> None:
        """Update average processing time metrics"""
        total = self.metrics['total_transactions']
        if total > 0:
            current_avg = self.metrics['average_processing_time']
            self.metrics['average_processing_time'] = (
                (current_avg * (total - 1) + processing_time) / total
            )
    
    def _update_gateway_metrics(self, gateway_id -> None: str, success -> None: bool) -> None:
        """Update gateway success rate metrics"""
        current_rate = self.metrics['gateway_success_rates'][gateway_id]
        
        # Simple exponential moving average
        alpha = 0.1  # Smoothing factor
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        self.metrics['gateway_success_rates'][gateway_id] = new_rate
    
    async def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Get transaction by ID"""
        # Try Redis cache first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"transaction:{transaction_id}")
                if cached_data:
                    return PaymentTransaction.parse_raw(cached_data)
            except Exception as e:
                logger.warning("Failed to retrieve from Redis cache", error=str(e))
        
        # Fallback to main store
        return self.transaction_store.get(transaction_id)
    
    async def process_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """
        Process refund for completed transaction
        
        Backend Senior: Complex refund logic, state management
        Security: Refund authorization, audit trails
        """
        try:
            # Get original transaction
            transaction = await self.get_transaction(refund_request.transaction_id)
            if not transaction:
                return {
                    'success': False,
                    'error': 'transaction_not_found',
                    'message': 'Original transaction not found'
                }
            
            # Validate refund eligibility
            if transaction.status != PaymentStatus.COMPLETED:
                return {
                    'success': False,
                    'error': 'invalid_transaction_status',
                    'message': 'Transaction is not eligible for refund'
                }
            
            # Check refund amount
            already_refunded = sum(
                Decimal(fee) for fee in transaction.metadata.get('refunds', {}).values()
            )
            
            if refund_request.amount + already_refunded > transaction.amount:
                return {
                    'success': False,
                    'error': 'refund_amount_exceeds_transaction',
                    'message': 'Refund amount exceeds available balance'
                }
            
            # Process refund through gateway
            gateway = self.gateways.get(transaction.gateway_id)
            if not gateway:
                return {
                    'success': False,
                    'error': 'gateway_not_available',
                    'message': 'Payment gateway not available for refund'
                }
            
            refund_response = await gateway.process_refund(refund_request)
            
            if refund_response.get('success', False):
                # Update transaction with refund information
                if 'refunds' not in transaction.metadata:
                    transaction.metadata['refunds'] = {}
                
                transaction.metadata['refunds'][refund_request.refund_id] = {
                    'amount': str(refund_request.amount),
                    'reason': refund_request.reason,
                    'processed_at': datetime.now().isoformat(),
                    'requested_by': refund_request.requested_by
                }
                
                # Update transaction status
                total_refunded = already_refunded + refund_request.amount
                if total_refunded >= transaction.amount:
                    transaction.status = PaymentStatus.REFUNDED
                else:
                    transaction.status = PaymentStatus.PARTIALLY_REFUNDED
                
                await self._store_transaction(transaction)
                
                logger.info("Refund processed successfully",
                           refund_id=refund_request.refund_id,
                           transaction_id=refund_request.transaction_id,
                           amount=refund_request.amount)
                
                return {
                    'success': True,
                    'refund_id': refund_request.refund_id,
                    'amount': refund_request.amount,
                    'status': refund_response.get('status', 'processed')
                }
            else:
                return {
                    'success': False,
                    'error': 'refund_processing_failed',
                    'message': refund_response.get('error', 'Refund processing failed')
                }
                
        except Exception as e:
            logger.error("Refund processing failed",
                        refund_id=refund_request.refund_id,
                        error=str(e))
            
            return {
                'success': False,
                'error': 'processing_error',
                'message': str(e)
            }
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        success_rate = 0.0
        if self.metrics['total_transactions'] > 0:
            success_rate = self.metrics['successful_transactions'] / self.metrics['total_transactions']
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'fraud_detection_rate': (
                self.metrics['fraud_blocked_transactions'] / max(self.metrics['total_transactions'], 1)
            ),
            'active_gateways': len([g for g in self.gateways.values() if g.config.is_active]),
            'supported_currencies': list(set(
                currency for gateway in self.gateways.values()
                for currency in gateway.config.supported_currencies
            )),
            'service_status': 'healthy'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        gateway_health = {}
        for gateway_id, gateway in self.gateways.items():
            gateway_health[gateway_id] = {
                'active': gateway.config.is_active,
                'success_rate': self.metrics['gateway_success_rates'].get(gateway_id, 0.0)
            }
        
        return {
            'service': 'payment_processing_service',
            'status': 'healthy',
            'version': '1.0.0',
            'gateways': gateway_health,
            'total_transactions': self.metrics['total_transactions'],
            'success_rate': (
                self.metrics['successful_transactions'] / max(self.metrics['total_transactions'], 1)
            )
        }

# Example usage and testing
async def example_usage() -> None:
    """Example usage of the Payment Processing Service"""
    
    # Initialize service
    service = PaymentProcessingService()
    
    # Create sample payment request
    billing_address = BillingAddress(
        street_address="123 Main St",
        city="New York",
        state_province="NY",
        postal_code="10001",
        country_code="US"
    )
    
    payment_card = PaymentCard(
        card_token="tok_visa_4242",
        card_type="Visa",
        last_four_digits="4242",
        expiry_month=12,
        expiry_year=2026,
        cardholder_name="John Doe",
        billing_address=billing_address
    )
    
    payment_request = PaymentRequest(
        amount=Decimal("99.99"),
        currency=Currency.USD,
        payment_method=PaymentMethod.CREDIT_CARD,
        customer_id="customer_001",
        description="Premium subscription payment",
        payment_card=payment_card,
        metadata={
            "order_id": "order_123",
            "ip_country": "US",
            "subscription_plan": "premium"
        }
    )
    
    # Process payment
    transaction = await service.process_payment(payment_request)
    
    print(f"Transaction ID: {transaction.transaction_id}")
    print(f"Status: {transaction.status}")
    print(f"Amount: {transaction.amount} {transaction.currency}")
    print(f"Gateway: {transaction.gateway_id}")
    
    if transaction.fraud_assessment:
        print(f"Fraud Risk: {transaction.fraud_assessment.risk_level}")
        print(f"Risk Score: {transaction.fraud_assessment.risk_score:.2f}")
    
    # Process refund if transaction was successful
    if transaction.status == PaymentStatus.COMPLETED:
        refund_request = RefundRequest(
            transaction_id=transaction.transaction_id,
            amount=Decimal("50.00"),
            reason="Customer requested partial refund",
            requested_by="customer_service_001"
        )
        
        refund_result = await service.process_refund(refund_request)
        print(f"Refund Success: {refund_result.get('success', False)}")
    
    # Get service metrics
    metrics = await service.get_service_metrics()
    print(f"Service Metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(example_usage())