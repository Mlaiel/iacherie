"""
Payment Gateway Core - Advanced Multi-Gateway Payment Processing System
======================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for managing multiple payment gateways, processing transactions,
handling subscriptions, and ensuring secure payment operations across global markets.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import hashlib
import uuid
from decimal import Decimal

# Get logger
logger = logging.getLogger(__name__)

class PaymentGateway(Enum):
    """Supported payment gateways"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    ADYEN = "adyen"
    SQUARE = "square"
    RAZORPAY = "razorpay"
    MOLLIE = "mollie"

class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    ACH = "ach"
    SEPA = "sepa"
    UPI = "upi"

class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    REFUND = "refund"
    PARTIAL_REFUND = "partial_refund"
    CHARGEBACK = "chargeback"
    PAYOUT = "payout"
    SUBSCRIPTION = "subscription"
    AUTHORIZATION = "authorization"
    CAPTURE = "capture"

class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

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
    INR = "INR"
    BRL = "BRL"

@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    gateway: PaymentGateway
    payment_method: PaymentMethod
    transaction_type: TransactionType
    amount: Decimal
    currency: Currency
    customer_id: str
    merchant_id: str
    description: str
    status: TransactionStatus = TransactionStatus.PENDING
    gateway_transaction_id: Optional[str] = None
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    fees: Decimal = field(default=Decimal('0'))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PaymentMethod_Config:
    """Payment method configuration"""
    method_id: str
    gateway: PaymentGateway
    method_type: PaymentMethod
    customer_id: str
    token: str
    last_four: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: bool = False
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GatewayConfig:
    """Payment gateway configuration"""
    gateway: PaymentGateway
    api_key: str
    secret_key: str
    webhook_secret: str
    environment: str
    supported_currencies: List[Currency]
    supported_methods: List[PaymentMethod]
    fee_structure: Dict[str, Any]
    rate_limits: Dict[str, int]
    is_active: bool = True
    priority: int = 1
    config_data: Dict[str, Any] = field(default_factory=dict)

class StripeGateway:
    """Stripe payment gateway integration"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.api_base = "https://api.stripe.com/v1"
        self.supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.BANK_TRANSFER,
            PaymentMethod.DIGITAL_WALLET,
            PaymentMethod.ACH,
            PaymentMethod.SEPA
        ]
        
        logger.info("Stripe Gateway initialized")

    async def process_payment(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            # Mock Stripe API integration
            payment_intent_data = {
                "amount": int(transaction.amount * 100),  # Stripe uses cents
                "currency": transaction.currency.value.lower(),
                "payment_method_types": ["card"],
                "description": transaction.description,
                "metadata": {
                    "transaction_id": transaction.transaction_id,
                    "customer_id": transaction.customer_id
                }
            }
            
            # Simulate API call to Stripe
            stripe_response = await self._call_stripe_api("payment_intents", payment_intent_data)
            
            if stripe_response.get("status") == "succeeded":
                return {
                    "success": True,
                    "gateway_transaction_id": stripe_response["id"],
                    "status": TransactionStatus.COMPLETED.value,
                    "gateway_response": stripe_response,
                    "fees": self._calculate_fees(transaction.amount)
                }
            else:
                return {
                    "success": False,
                    "status": TransactionStatus.FAILED.value,
                    "error": stripe_response.get("error", "Unknown error"),
                    "gateway_response": stripe_response
                }
                
        except Exception as e:
            logger.error(f"Stripe payment processing error: {str(e)}")
            return {
                "success": False,
                "status": TransactionStatus.FAILED.value,
                "error": str(e)
            }

    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer in Stripe"""
        try:
            customer_payload = {
                "email": customer_data["email"],
                "name": customer_data.get("name"),
                "phone": customer_data.get("phone"),
                "metadata": customer_data.get("metadata", {})
            }
            
            stripe_response = await self._call_stripe_api("customers", customer_payload)
            
            return {
                "success": True,
                "customer_id": stripe_response["id"],
                "gateway_response": stripe_response
            }
            
        except Exception as e:
            logger.error(f"Stripe customer creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def setup_payment_method(self, customer_id: str, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup payment method for customer"""
        try:
            setup_intent_data = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "usage": "off_session"
            }
            
            stripe_response = await self._call_stripe_api("setup_intents", setup_intent_data)
            
            return {
                "success": True,
                "setup_intent_id": stripe_response["id"],
                "client_secret": stripe_response["client_secret"],
                "gateway_response": stripe_response
            }
            
        except Exception as e:
            logger.error(f"Stripe payment method setup error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, original_transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process refund through Stripe"""
        try:
            refund_data = {
                "payment_intent": original_transaction_id,
                "amount": int(amount * 100) if amount else None
            }
            
            stripe_response = await self._call_stripe_api("refunds", refund_data)
            
            return {
                "success": True,
                "refund_id": stripe_response["id"],
                "status": "completed",
                "gateway_response": stripe_response
            }
            
        except Exception as e:
            logger.error(f"Stripe refund processing error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _call_stripe_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Stripe API call"""
        # Mock successful Stripe response
        if endpoint == "payment_intents":
            return {
                "id": f"pi_{uuid.uuid4().hex[:24]}",
                "status": "succeeded",
                "amount": data["amount"],
                "currency": data["currency"],
                "charges": {
                    "data": [{
                        "id": f"ch_{uuid.uuid4().hex[:24]}",
                        "balance_transaction": f"txn_{uuid.uuid4().hex[:24]}"
                    }]
                }
            }
        elif endpoint == "customers":
            return {
                "id": f"cus_{uuid.uuid4().hex[:14]}",
                "email": data["email"],
                "created": int(datetime.utcnow().timestamp())
            }
        elif endpoint == "setup_intents":
            return {
                "id": f"seti_{uuid.uuid4().hex[:24]}",
                "client_secret": f"seti_{uuid.uuid4().hex[:24]}_secret_{uuid.uuid4().hex[:10]}",
                "status": "requires_payment_method"
            }
        elif endpoint == "refunds":
            return {
                "id": f"re_{uuid.uuid4().hex[:24]}",
                "status": "succeeded",
                "amount": data.get("amount")
            }
        
        return {"status": "succeeded"}

    def _calculate_fees(self, amount: Decimal) -> Decimal:
        """Calculate Stripe fees"""
        # Stripe standard fee: 2.9% + $0.30
        return amount * Decimal('0.029') + Decimal('0.30')

class PayPalGateway:
    """PayPal payment gateway integration"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.api_base = "https://api.paypal.com" if config.environment == "production" else "https://api.sandbox.paypal.com"
        self.supported_methods = [
            PaymentMethod.DIGITAL_WALLET,
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.BANK_TRANSFER
        ]
        
        logger.info("PayPal Gateway initialized")

    async def process_payment(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process payment through PayPal"""
        try:
            payment_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": transaction.currency.value,
                        "value": str(transaction.amount)
                    },
                    "description": transaction.description
                }],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "return_url": "https://example.com/return",
                            "cancel_url": "https://example.com/cancel"
                        }
                    }
                }
            }
            
            paypal_response = await self._call_paypal_api("orders", payment_data)
            
            if paypal_response.get("status") == "COMPLETED":
                return {
                    "success": True,
                    "gateway_transaction_id": paypal_response["id"],
                    "status": TransactionStatus.COMPLETED.value,
                    "gateway_response": paypal_response,
                    "fees": self._calculate_fees(transaction.amount)
                }
            else:
                return {
                    "success": False,
                    "status": TransactionStatus.FAILED.value,
                    "error": "Payment not completed",
                    "gateway_response": paypal_response
                }
                
        except Exception as e:
            logger.error(f"PayPal payment processing error: {str(e)}")
            return {
                "success": False,
                "status": TransactionStatus.FAILED.value,
                "error": str(e)
            }

    async def _call_paypal_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock PayPal API call"""
        if endpoint == "orders":
            return {
                "id": uuid.uuid4().hex[:17].upper(),
                "status": "COMPLETED",
                "purchase_units": data["purchase_units"],
                "create_time": datetime.utcnow().isoformat() + "Z"
            }
        
        return {"status": "COMPLETED"}

    def _calculate_fees(self, amount: Decimal) -> Decimal:
        """Calculate PayPal fees"""
        # PayPal standard fee: 2.9% + fixed fee
        return amount * Decimal('0.029') + Decimal('0.30')

class WiseGateway:
    """Wise (formerly TransferWise) gateway for international transfers"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.api_base = "https://api.wise.com"
        self.supported_methods = [
            PaymentMethod.BANK_TRANSFER,
            PaymentMethod.DEBIT_CARD
        ]
        
        logger.info("Wise Gateway initialized")

    async def process_payment(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process international transfer through Wise"""
        try:
            transfer_data = {
                "targetAccount": transaction.metadata.get("target_account"),
                "quoteUuid": transaction.metadata.get("quote_uuid"),
                "customerTransactionId": transaction.transaction_id,
                "details": {
                    "reference": transaction.description
                }
            }
            
            wise_response = await self._call_wise_api("transfers", transfer_data)
            
            return {
                "success": True,
                "gateway_transaction_id": wise_response["id"],
                "status": TransactionStatus.PROCESSING.value,
                "gateway_response": wise_response,
                "fees": self._calculate_fees(transaction.amount, transaction.currency)
            }
            
        except Exception as e:
            logger.error(f"Wise payment processing error: {str(e)}")
            return {
                "success": False,
                "status": TransactionStatus.FAILED.value,
                "error": str(e)
            }

    async def get_exchange_rate(self, source_currency: Currency, target_currency: Currency) -> Dict[str, Any]:
        """Get real-time exchange rate from Wise"""
        try:
            rate_response = await self._call_wise_api("rates", {
                "source": source_currency.value,
                "target": target_currency.value
            })
            
            return {
                "success": True,
                "rate": rate_response["rate"],
                "timestamp": rate_response["time"]
            }
            
        except Exception as e:
            logger.error(f"Wise exchange rate error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _call_wise_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Wise API call"""
        if endpoint == "transfers":
            return {
                "id": int(uuid.uuid4().hex[:8], 16),
                "status": "processing",
                "created": datetime.utcnow().isoformat()
            }
        elif endpoint == "rates":
            return {
                "rate": 1.1234,  # Mock exchange rate
                "time": datetime.utcnow().isoformat()
            }
        
        return {"status": "success"}

    def _calculate_fees(self, amount: Decimal, currency: Currency) -> Decimal:
        """Calculate Wise fees based on currency and amount"""
        # Wise has variable fees based on amount and currency
        if amount < Decimal('500'):
            return Decimal('5.00')
        elif amount < Decimal('2000'):
            return amount * Decimal('0.01')
        else:
            return amount * Decimal('0.005')

class FraudDetection:
    """Advanced fraud detection system"""
    
    def __init__(self):
        self.risk_rules = {}
        self.blocked_entities = set()
        self.whitelist = set()
        self.transaction_history = {}
        
        self._initialize_risk_rules()
        
        logger.info("Fraud Detection initialized")

    def _initialize_risk_rules(self):
        """Initialize fraud detection rules"""
        self.risk_rules = {
            "velocity_check": {
                "max_transactions_per_hour": 10,
                "max_amount_per_hour": Decimal('1000'),
                "max_transactions_per_day": 50,
                "max_amount_per_day": Decimal('10000')
            },
            "geographic_check": {
                "blocked_countries": ["XX", "YY"],  # ISO country codes
                "high_risk_countries": ["ZZ"],
                "velocity_multiplier": 0.5
            },
            "amount_check": {
                "unusual_amount_threshold": Decimal('5000'),
                "micro_transaction_threshold": Decimal('1'),
                "max_single_transaction": Decimal('50000')
            },
            "behavioral_check": {
                "new_customer_limit": Decimal('500'),
                "unusual_hours": [0, 1, 2, 3, 4, 5],  # 12 AM - 6 AM
                "weekend_multiplier": 1.5
            }
        }

    async def assess_transaction_risk(self, transaction: PaymentTransaction, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess fraud risk for transaction"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Velocity checks
            velocity_risk = await self._check_velocity(transaction, customer_data)
            risk_score += velocity_risk["score"]
            if velocity_risk["triggered"]:
                risk_factors.extend(velocity_risk["factors"])
            
            # Geographic checks
            geo_risk = await self._check_geographic(transaction, customer_data)
            risk_score += geo_risk["score"]
            if geo_risk["triggered"]:
                risk_factors.extend(geo_risk["factors"])
            
            # Amount checks
            amount_risk = await self._check_amount(transaction, customer_data)
            risk_score += amount_risk["score"]
            if amount_risk["triggered"]:
                risk_factors.extend(amount_risk["factors"])
            
            # Behavioral checks
            behavior_risk = await self._check_behavior(transaction, customer_data)
            risk_score += behavior_risk["score"]
            if behavior_risk["triggered"]:
                risk_factors.extend(behavior_risk["factors"])
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "HIGH"
                action = "BLOCK"
            elif risk_score >= 50:
                risk_level = "MEDIUM"
                action = "REVIEW"
            elif risk_score >= 20:
                risk_level = "LOW"
                action = "MONITOR"
            else:
                risk_level = "MINIMAL"
                action = "APPROVE"
            
            risk_assessment = {
                "transaction_id": transaction.transaction_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommended_action": action,
                "risk_factors": risk_factors,
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Fraud assessment error: {str(e)}")
            return {
                "risk_score": 100,
                "risk_level": "HIGH",
                "recommended_action": "BLOCK",
                "error": str(e)
            }

    async def _check_velocity(self, transaction: PaymentTransaction, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check transaction velocity"""
        customer_id = transaction.customer_id
        current_time = datetime.utcnow()
        
        # Get customer transaction history (mock)
        customer_transactions = self.transaction_history.get(customer_id, [])
        
        # Check hourly limits
        hour_ago = current_time - timedelta(hours=1)
        recent_transactions = [t for t in customer_transactions if t["timestamp"] >= hour_ago]
        
        hourly_count = len(recent_transactions)
        hourly_amount = sum(Decimal(str(t["amount"])) for t in recent_transactions)
        
        risk_score = 0
        factors = []
        triggered = False
        
        rules = self.risk_rules["velocity_check"]
        
        if hourly_count >= rules["max_transactions_per_hour"]:
            risk_score += 30
            factors.append("high_transaction_frequency")
            triggered = True
        
        if hourly_amount >= rules["max_amount_per_hour"]:
            risk_score += 25
            factors.append("high_hourly_amount")
            triggered = True
        
        return {
            "score": risk_score,
            "triggered": triggered,
            "factors": factors,
            "details": {
                "hourly_transactions": hourly_count,
                "hourly_amount": float(hourly_amount)
            }
        }

    async def _check_geographic(self, transaction: PaymentTransaction, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check geographic risk factors"""
        country_code = customer_data.get("country", "US")
        
        risk_score = 0
        factors = []
        triggered = False
        
        rules = self.risk_rules["geographic_check"]
        
        if country_code in rules["blocked_countries"]:
            risk_score += 100
            factors.append("blocked_country")
            triggered = True
        elif country_code in rules["high_risk_countries"]:
            risk_score += 40
            factors.append("high_risk_country")
            triggered = True
        
        return {
            "score": risk_score,
            "triggered": triggered,
            "factors": factors,
            "details": {
                "country_code": country_code
            }
        }

    async def _check_amount(self, transaction: PaymentTransaction, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check amount-based risk factors"""
        amount = transaction.amount
        
        risk_score = 0
        factors = []
        triggered = False
        
        rules = self.risk_rules["amount_check"]
        
        if amount >= rules["unusual_amount_threshold"]:
            risk_score += 20
            factors.append("unusual_large_amount")
            triggered = True
        
        if amount <= rules["micro_transaction_threshold"]:
            risk_score += 15
            factors.append("micro_transaction")
            triggered = True
        
        if amount >= rules["max_single_transaction"]:
            risk_score += 50
            factors.append("exceeds_single_limit")
            triggered = True
        
        return {
            "score": risk_score,
            "triggered": triggered,
            "factors": factors,
            "details": {
                "transaction_amount": float(amount)
            }
        }

    async def _check_behavior(self, transaction: PaymentTransaction, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check behavioral risk factors"""
        current_time = datetime.utcnow()
        
        risk_score = 0
        factors = []
        triggered = False
        
        rules = self.risk_rules["behavioral_check"]
        
        # Check if new customer
        if customer_data.get("is_new_customer", False):
            if transaction.amount > rules["new_customer_limit"]:
                risk_score += 25
                factors.append("new_customer_large_transaction")
                triggered = True
        
        # Check unusual hours
        if current_time.hour in rules["unusual_hours"]:
            risk_score += 10
            factors.append("unusual_hour_transaction")
            triggered = True
        
        # Check weekend transactions
        if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            risk_score += 5
            factors.append("weekend_transaction")
        
        return {
            "score": risk_score,
            "triggered": triggered,
            "factors": factors,
            "details": {
                "transaction_hour": current_time.hour,
                "is_weekend": current_time.weekday() >= 5
            }
        }

class PaymentGatewayCore:
    """Main Payment Gateway Core System"""
    
    def __init__(self, level: str = "enterprise"):
        self.version = "2.1.0"
        self.level = level
        self.gateways = {}
        self.gateway_configs = {}
        self.transactions = {}
        self.payment_methods = {}
        self.fraud_detection = FraudDetection()
        
        # Initialize gateways
        self._initialize_gateways()
        
        logger.info("Payment Gateway Core initialized")

    def _initialize_gateways(self):
        """Initialize payment gateway configurations"""
        # Mock gateway configurations
        gateway_configs = {
            PaymentGateway.STRIPE: GatewayConfig(
                gateway=PaymentGateway.STRIPE,
                api_key="sk_test_mock",
                secret_key="whsec_mock",
                webhook_secret="whsec_mock",
                environment="test",
                supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP],
                supported_methods=[PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD],
                fee_structure={"percentage": 2.9, "fixed": 0.30},
                rate_limits={"requests_per_second": 100}
            ),
            PaymentGateway.PAYPAL: GatewayConfig(
                gateway=PaymentGateway.PAYPAL,
                api_key="AYjcyDnhZKo_mock",
                secret_key="EHLohZh3Y8N_mock",
                webhook_secret="mock_webhook",
                environment="sandbox",
                supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP, Currency.CAD],
                supported_methods=[PaymentMethod.DIGITAL_WALLET, PaymentMethod.CREDIT_CARD],
                fee_structure={"percentage": 2.9, "fixed": 0.30},
                rate_limits={"requests_per_second": 50}
            ),
            PaymentGateway.WISE: GatewayConfig(
                gateway=PaymentGateway.WISE,
                api_key="mock_wise_key",
                secret_key="mock_wise_secret",
                webhook_secret="mock_webhook",
                environment="sandbox",
                supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY],
                supported_methods=[PaymentMethod.BANK_TRANSFER],
                fee_structure={"percentage": 0.5, "minimum": 5.00},
                rate_limits={"requests_per_second": 10}
            )
        }
        
        # Initialize gateway instances
        for gateway_type, config in gateway_configs.items():
            self.gateway_configs[gateway_type] = config
            
            if gateway_type == PaymentGateway.STRIPE:
                self.gateways[gateway_type] = StripeGateway(config)
            elif gateway_type == PaymentGateway.PAYPAL:
                self.gateways[gateway_type] = PayPalGateway(config)
            elif gateway_type == PaymentGateway.WISE:
                self.gateways[gateway_type] = WiseGateway(config)

    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through optimal gateway"""
        try:
            # Create transaction record
            transaction = PaymentTransaction(
                transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                gateway=PaymentGateway(payment_data["gateway"]),
                payment_method=PaymentMethod(payment_data["payment_method"]),
                transaction_type=TransactionType(payment_data.get("transaction_type", "payment")),
                amount=Decimal(str(payment_data["amount"])),
                currency=Currency(payment_data["currency"]),
                customer_id=payment_data["customer_id"],
                merchant_id=payment_data["merchant_id"],
                description=payment_data.get("description", ""),
                metadata=payment_data.get("metadata", {})
            )
            
            # Fraud assessment
            customer_data = payment_data.get("customer_data", {})
            risk_assessment = await self.fraud_detection.assess_transaction_risk(transaction, customer_data)
            
            if risk_assessment["recommended_action"] == "BLOCK":
                transaction.status = TransactionStatus.FAILED
                self.transactions[transaction.transaction_id] = transaction
                
                return {
                    "success": False,
                    "transaction_id": transaction.transaction_id,
                    "error": "Transaction blocked due to fraud risk",
                    "risk_assessment": risk_assessment
                }
            
            # Process through selected gateway
            gateway = self.gateways.get(transaction.gateway)
            if not gateway:
                raise ValueError(f"Gateway not available: {transaction.gateway.value}")
            
            # Process payment
            gateway_result = await gateway.process_payment(transaction)
            
            # Update transaction
            transaction.status = TransactionStatus(gateway_result["status"])
            transaction.gateway_transaction_id = gateway_result.get("gateway_transaction_id")
            transaction.gateway_response = gateway_result.get("gateway_response", {})
            transaction.fees = gateway_result.get("fees", Decimal('0'))
            transaction.updated_at = datetime.utcnow()
            
            if transaction.status == TransactionStatus.COMPLETED:
                transaction.completed_at = datetime.utcnow()
            
            # Store transaction
            self.transactions[transaction.transaction_id] = transaction
            
            result = {
                "success": gateway_result["success"],
                "transaction_id": transaction.transaction_id,
                "gateway_transaction_id": transaction.gateway_transaction_id,
                "status": transaction.status.value,
                "amount": float(transaction.amount),
                "currency": transaction.currency.value,
                "fees": float(transaction.fees),
                "risk_assessment": risk_assessment
            }
            
            if not gateway_result["success"]:
                result["error"] = gateway_result.get("error")
            
            return result
            
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": None
            }

    async def setup_payment_method(self, customer_id: str, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup payment method for customer"""
        try:
            gateway_type = PaymentGateway(payment_method_data["gateway"])
            gateway = self.gateways.get(gateway_type)
            
            if not gateway:
                raise ValueError(f"Gateway not available: {gateway_type.value}")
            
            # Setup payment method through gateway
            setup_result = await gateway.setup_payment_method(customer_id, payment_method_data)
            
            if setup_result["success"]:
                # Create payment method record
                method_id = f"pm_{uuid.uuid4().hex[:12]}"
                payment_method = PaymentMethod_Config(
                    method_id=method_id,
                    gateway=gateway_type,
                    method_type=PaymentMethod(payment_method_data["method_type"]),
                    customer_id=customer_id,
                    token=setup_result.get("setup_intent_id", ""),
                    last_four=payment_method_data.get("last_four"),
                    expiry_month=payment_method_data.get("expiry_month"),
                    expiry_year=payment_method_data.get("expiry_year"),
                    is_default=payment_method_data.get("is_default", False),
                    metadata=setup_result.get("gateway_response", {})
                )
                
                self.payment_methods[method_id] = payment_method
                
                return {
                    "success": True,
                    "method_id": method_id,
                    "client_secret": setup_result.get("client_secret"),
                    "gateway_response": setup_result.get("gateway_response")
                }
            else:
                return setup_result
                
        except Exception as e:
            logger.error(f"Payment method setup error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process refund for transaction"""
        try:
            original_transaction_id = refund_data["original_transaction_id"]
            
            if original_transaction_id not in self.transactions:
                raise ValueError(f"Original transaction not found: {original_transaction_id}")
            
            original_transaction = self.transactions[original_transaction_id]
            refund_amount = Decimal(str(refund_data.get("amount", original_transaction.amount)))
            
            # Create refund transaction
            refund_transaction = PaymentTransaction(
                transaction_id=f"rfnd_{uuid.uuid4().hex[:12]}",
                gateway=original_transaction.gateway,
                payment_method=original_transaction.payment_method,
                transaction_type=TransactionType.REFUND,
                amount=refund_amount,
                currency=original_transaction.currency,
                customer_id=original_transaction.customer_id,
                merchant_id=original_transaction.merchant_id,
                description=f"Refund for {original_transaction_id}",
                metadata={"original_transaction_id": original_transaction_id}
            )
            
            # Process refund through gateway
            gateway = self.gateways.get(original_transaction.gateway)
            refund_result = await gateway.process_refund(
                original_transaction.gateway_transaction_id,
                refund_amount
            )
            
            if refund_result["success"]:
                refund_transaction.status = TransactionStatus.COMPLETED
                refund_transaction.gateway_transaction_id = refund_result["refund_id"]
                refund_transaction.completed_at = datetime.utcnow()
            else:
                refund_transaction.status = TransactionStatus.FAILED
            
            refund_transaction.gateway_response = refund_result.get("gateway_response", {})
            self.transactions[refund_transaction.transaction_id] = refund_transaction
            
            return {
                "success": refund_result["success"],
                "refund_transaction_id": refund_transaction.transaction_id,
                "refund_amount": float(refund_amount),
                "status": refund_transaction.status.value,
                "gateway_refund_id": refund_result.get("refund_id")
            }
            
        except Exception as e:
            logger.error(f"Refund processing error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get current status of transaction"""
        try:
            if transaction_id not in self.transactions:
                return {"found": False, "error": "Transaction not found"}
            
            transaction = self.transactions[transaction_id]
            
            return {
                "found": True,
                "transaction_id": transaction.transaction_id,
                "status": transaction.status.value,
                "amount": float(transaction.amount),
                "currency": transaction.currency.value,
                "gateway": transaction.gateway.value,
                "payment_method": transaction.payment_method.value,
                "created_at": transaction.created_at.isoformat(),
                "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
                "fees": float(transaction.fees),
                "gateway_transaction_id": transaction.gateway_transaction_id
            }
            
        except Exception as e:
            logger.error(f"Transaction status error: {str(e)}")
            return {"found": False, "error": str(e)}

    async def get_gateway_analytics(self, gateway: PaymentGateway, days: int = 30) -> Dict[str, Any]:
        """Get analytics for specific gateway"""
        try:
            # Filter transactions for gateway and time period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            gateway_transactions = [
                t for t in self.transactions.values()
                if t.gateway == gateway and start_date <= t.created_at <= end_date
            ]
            
            if not gateway_transactions:
                return {
                    "gateway": gateway.value,
                    "period_days": days,
                    "total_transactions": 0,
                    "analytics": {}
                }
            
            # Calculate analytics
            total_transactions = len(gateway_transactions)
            total_volume = sum(t.amount for t in gateway_transactions)
            total_fees = sum(t.fees for t in gateway_transactions)
            
            # Success rate
            successful_transactions = [t for t in gateway_transactions if t.status == TransactionStatus.COMPLETED]
            success_rate = len(successful_transactions) / total_transactions
            
            # Average transaction amount
            avg_transaction_amount = total_volume / total_transactions
            
            # Transaction distribution by status
            status_distribution = {}
            for transaction in gateway_transactions:
                status = transaction.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            analytics = {
                "gateway": gateway.value,
                "period_days": days,
                "total_transactions": total_transactions,
                "total_volume": float(total_volume),
                "total_fees": float(total_fees),
                "success_rate": success_rate,
                "average_transaction_amount": float(avg_transaction_amount),
                "status_distribution": status_distribution,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Gateway analytics error: {str(e)}")
            raise

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics"""
        total_transactions = len(self.transactions)
        total_gateways = len(self.gateways)
        total_payment_methods = len(self.payment_methods)
        
        # Gateway status
        gateway_status = {}
        for gateway_type, gateway_instance in self.gateways.items():
            gateway_status[gateway_type.value] = {
                "active": self.gateway_configs[gateway_type].is_active,
                "supported_currencies": len(self.gateway_configs[gateway_type].supported_currencies),
                "supported_methods": len(self.gateway_configs[gateway_type].supported_methods)
            }
        
        return {
            "version": self.version,
            "total_transactions": total_transactions,
            "total_gateways": total_gateways,
            "total_payment_methods": total_payment_methods,
            "gateway_status": gateway_status,
            "fraud_detection_active": True,
            "system_status": "healthy",
            "last_health_check": datetime.utcnow().isoformat()
        }

# Global instance
payment_gateway_core = PaymentGatewayCore()

# Export main functions
__all__ = [
    "PaymentGateway",
    "PaymentMethod",
    "TransactionType",
    "TransactionStatus",
    "Currency",
    "PaymentTransaction",
    "PaymentMethod_Config",
    "GatewayConfig",
    "PaymentGatewayCore",
    "payment_gateway_core"
]

if __name__ == "__main__":
    logger.info("Payment Gateway Core module loaded successfully")