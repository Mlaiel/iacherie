"""Multi-gateway payment processing engine with comprehensive payment orchestration.

This module implements advanced payment processing capabilities including:
- Multi-gateway integration (Stripe, PayPal, Wise, Crypto)
- Intelligent routing and failover mechanisms
- Advanced fraud detection and risk assessment
- Automated revenue distribution and payouts
- Real-time payment analytics and monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Payment Systems Architect: Multi-Gateway Integration & Security
- Financial Technology Specialist: Payment Orchestration & Compliance
- Risk Management Expert: Fraud Detection & Prevention
- Compliance Officer: PCI DSS, PSD2 & Financial Regulations

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import stripe
import paypal
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_database, get_redis_client
from ..core.exceptions import PaymentException, FraudException


class PaymentGateway(Enum):
    """Supported payment gateways."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"


class PaymentMethod(Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BUY_NOW_PAY_LATER = "buy_now_pay_later"
    DIRECT_DEBIT = "direct_debit"
    WIRE_TRANSFER = "wire_transfer"


class PaymentStatus(Enum):
    """Payment transaction status."""
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
    CHARGEBACK = "chargeback"


class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    BTC = "BTC"
    ETH = "ETH"
    USDC = "USDC"


class FraudRiskLevel(Enum):
    """Fraud risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration."""
    gateway: PaymentGateway
    api_key: str
    secret_key: str
    webhook_secret: Optional[str] = None
    environment: str = "sandbox"
    supported_currencies: List[Currency] = field(default_factory=list)
    supported_countries: List[str] = field(default_factory=list)
    transaction_fee_percentage: Decimal = Decimal("0.029")  # 2.9%
    transaction_fee_fixed: Decimal = Decimal("0.30")  # $0.30
    minimum_amount: Decimal = Decimal("0.50")
    maximum_amount: Decimal = Decimal("999999.99")
    processing_time_minutes: int = 5
    settlement_time_days: int = 2
    chargeback_protection: bool = False
    fraud_protection: bool = True
    recurring_payments: bool = True
    instant_payouts: bool = False


@dataclass
class PaymentRequest:
    """Payment processing request."""
    request_id: str
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    customer_id: str
    creator_id: str
    content_id: Optional[str] = None
    license_agreement_id: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    billing_details: Dict[str, Any] = field(default_factory=dict)
    shipping_details: Dict[str, Any] = field(default_factory=dict)
    preferred_gateway: Optional[PaymentGateway] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    webhook_url: Optional[str] = None
    capture_method: str = "automatic"
    setup_future_usage: bool = False
    statement_descriptor: Optional[str] = None


@dataclass
class PaymentResult:
    """Payment processing result."""
    transaction_id: str
    gateway_transaction_id: str
    gateway: PaymentGateway
    status: PaymentStatus
    amount: Decimal
    currency: Currency
    fees: Decimal
    net_amount: Decimal
    processing_time: float
    created_at: datetime
    gateway_response: Dict[str, Any]
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    fraud_score: float = 0.0
    requires_action: bool = False
    next_action: Optional[Dict[str, Any]] = None
    receipt_url: Optional[str] = None
    refund_id: Optional[str] = None


@dataclass
class FraudAssessment:
    """Fraud risk assessment result."""
    transaction_id: str
    risk_level: FraudRiskLevel
    risk_score: float  # 0-100
    risk_factors: List[str]
    recommended_action: str  # approve, review, decline
    confidence_score: float  # 0-1
    assessment_details: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutRequest:
    """Payout processing request."""
    payout_id: str
    recipient_id: str
    amount: Decimal
    currency: Currency
    recipient_type: str  # creator, licensee, partner
    payout_method: str  # bank_transfer, paypal, crypto
    recipient_details: Dict[str, Any]
    description: str = ""
    reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedPaymentProcessor:
    """
    Advanced multi-gateway payment processing engine.
    
    Provides comprehensive payment orchestration including:
    - Intelligent gateway routing and failover
    - Advanced fraud detection and prevention
    - Automated revenue distribution
    - Real-time payment monitoring and analytics
    - PCI DSS compliant payment handling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("monetization.payment_processor")
        self.db = get_database()
        self.redis = get_redis_client()
        
        # Gateway configurations
        self.gateway_configs = {}
        self.gateway_clients = {}
        
        # Session management
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Payment routing settings
        self.routing_rules = self._initialize_routing_rules()
        self.failover_rules = self._initialize_failover_rules()
        
        # Fraud detection settings
        self.fraud_rules = self._initialize_fraud_rules()
        self.fraud_threshold_score = self.config.get("fraud_threshold", 75.0)
        
        # Fee calculation settings
        self.platform_fee_percentage = Decimal(str(self.config.get("platform_fee_percentage", "0.05")))  # 5%
        self.revenue_share_cache = {}
        
        # Initialize components
        asyncio.create_task(self._initialize_payment_processor())
        
        self.logger.info("AdvancedPaymentProcessor initialized successfully")
    
    async def _initialize_payment_processor(self):
        """Initialize payment processor components."""
        try:
            # Initialize HTTP session
            await self._initialize_session()
            
            # Load gateway configurations
            await self._load_gateway_configurations()
            
            # Initialize payment gateways
            await self._initialize_payment_gateways()
            
            # Initialize fraud detection system
            await self._initialize_fraud_detection()
            
            self.logger.info("Payment processor components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Payment processor initialization failed: {e}")
            raise PaymentException(f"Processor initialization error: {e}")
    
    async def _initialize_session(self):
        """Initialize aiohttp session for external API calls."""
        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.session_timeout,
                headers={
                    "User-Agent": "IA-Influencer-Agent/2.0 Payment-Processor",
                    "Accept": "application/json"
                }
            )
            
            self.logger.info("Payment processor HTTP session initialized")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise PaymentException(f"Session initialization error: {e}")
    
    async def _load_gateway_configurations(self):
        """Load payment gateway configurations from database."""
        try:
            query = """
            SELECT 
                gateway, api_key, secret_key, webhook_secret, environment,
                supported_currencies, supported_countries, transaction_fee_percentage,
                transaction_fee_fixed, minimum_amount, maximum_amount,
                processing_time_minutes, settlement_time_days, chargeback_protection,
                fraud_protection, recurring_payments, instant_payouts, is_active
            FROM payment_gateway_configs
            WHERE is_active = true
            """
            
            results = await self.db.fetch(query)
            
            for row in results:
                gateway = PaymentGateway(row["gateway"])
                
                config = PaymentGatewayConfig(
                    gateway=gateway,
                    api_key=row["api_key"],
                    secret_key=row["secret_key"],
                    webhook_secret=row["webhook_secret"],
                    environment=row["environment"],
                    supported_currencies=[Currency(c) for c in json.loads(row["supported_currencies"] or "[]")],
                    supported_countries=json.loads(row["supported_countries"] or "[]"),
                    transaction_fee_percentage=Decimal(str(row["transaction_fee_percentage"])),
                    transaction_fee_fixed=Decimal(str(row["transaction_fee_fixed"])),
                    minimum_amount=Decimal(str(row["minimum_amount"])),
                    maximum_amount=Decimal(str(row["maximum_amount"])),
                    processing_time_minutes=row["processing_time_minutes"],
                    settlement_time_days=row["settlement_time_days"],
                    chargeback_protection=row["chargeback_protection"],
                    fraud_protection=row["fraud_protection"],
                    recurring_payments=row["recurring_payments"],
                    instant_payouts=row["instant_payouts"]
                )
                
                self.gateway_configs[gateway] = config
            
            self.logger.info(f"Loaded {len(self.gateway_configs)} gateway configurations")
            
        except Exception as e:
            self.logger.error(f"Gateway configuration loading failed: {e}")
            # Initialize with default configurations
            await self._initialize_default_gateway_configs()
    
    async def _initialize_default_gateway_configs(self):
        """Initialize default gateway configurations."""
        default_configs = {
            PaymentGateway.STRIPE: PaymentGatewayConfig(
                gateway=PaymentGateway.STRIPE,
                api_key=self.config.get("stripe_api_key", ""),
                secret_key=self.config.get("stripe_secret_key", ""),
                webhook_secret=self.config.get("stripe_webhook_secret", ""),
                supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP],
                supported_countries=["US", "CA", "GB", "DE", "FR"]
            ),
            PaymentGateway.PAYPAL: PaymentGatewayConfig(
                gateway=PaymentGateway.PAYPAL,
                api_key=self.config.get("paypal_client_id", ""),
                secret_key=self.config.get("paypal_client_secret", ""),
                supported_currencies=[Currency.USD, Currency.EUR, Currency.GBP],
                supported_countries=["US", "CA", "GB", "DE", "FR"]
            )
        }
        
        self.gateway_configs.update(default_configs)
    
    async def _initialize_payment_gateways(self):
        """Initialize payment gateway client connections."""
        for gateway, config in self.gateway_configs.items():
            try:
                if gateway == PaymentGateway.STRIPE:
                    stripe.api_key = config.secret_key
                    self.gateway_clients[gateway] = stripe
                    
                elif gateway == PaymentGateway.PAYPAL:
                    # Initialize PayPal client
                    paypal_client = self._create_paypal_client(config)
                    self.gateway_clients[gateway] = paypal_client
                
                # Add other gateway initializations here
                
                self.logger.info(f"Initialized {gateway.value} gateway client")
                
            except Exception as e:
                self.logger.error(f"Gateway {gateway.value} initialization failed: {e}")
    
    def _create_paypal_client(self, config: PaymentGatewayConfig):
        """Create PayPal client configuration."""
        # This would return actual PayPal client in production
        return {
            "client_id": config.api_key,
            "client_secret": config.secret_key,
            "environment": config.environment
        }
    
    def _initialize_routing_rules(self) -> Dict[str, Any]:
        """Initialize payment routing rules."""
        return {
            "default_gateway": PaymentGateway.STRIPE,
            "currency_routing": {
                Currency.USD: [PaymentGateway.STRIPE, PaymentGateway.PAYPAL],
                Currency.EUR: [PaymentGateway.STRIPE, PaymentGateway.PAYPAL],
                Currency.BTC: [PaymentGateway.BITCOIN],
                Currency.ETH: [PaymentGateway.ETHEREUM]
            },
            "amount_routing": {
                "small": {"max": Decimal("100.00"), "gateways": [PaymentGateway.STRIPE]},
                "medium": {"max": Decimal("10000.00"), "gateways": [PaymentGateway.STRIPE, PaymentGateway.PAYPAL]},
                "large": {"max": Decimal("999999.99"), "gateways": [PaymentGateway.WISE, PaymentGateway.BANK_TRANSFER]}
            },
            "country_routing": {
                "US": [PaymentGateway.STRIPE, PaymentGateway.PAYPAL],
                "EU": [PaymentGateway.STRIPE, PaymentGateway.PAYPAL],
                "UK": [PaymentGateway.STRIPE, PaymentGateway.PAYPAL],
                "CN": [PaymentGateway.ALIPAY, PaymentGateway.WECHAT_PAY]
            }
        }
    
    def _initialize_failover_rules(self) -> Dict[str, Any]:
        """Initialize payment failover rules."""
        return {
            "max_retries": 3,
            "retry_delay_seconds": [1, 3, 5],
            "failover_gateways": {
                PaymentGateway.STRIPE: [PaymentGateway.PAYPAL, PaymentGateway.WISE],
                PaymentGateway.PAYPAL: [PaymentGateway.STRIPE, PaymentGateway.WISE],
                PaymentGateway.WISE: [PaymentGateway.STRIPE, PaymentGateway.PAYPAL]
            },
            "error_code_mapping": {
                "insufficient_funds": "decline",
                "card_declined": "decline",
                "expired_card": "decline",
                "network_error": "retry",
                "gateway_timeout": "failover",
                "rate_limit": "retry_later"
            }
        }
    
    def _initialize_fraud_rules(self) -> Dict[str, Any]:
        """Initialize fraud detection rules."""
        return {
            "velocity_checks": {
                "transactions_per_hour": 10,
                "transactions_per_day": 50,
                "amount_per_hour": Decimal("1000.00"),
                "amount_per_day": Decimal("5000.00")
            },
            "geographic_checks": {
                "high_risk_countries": ["AF", "IQ", "IR", "KP", "SY"],
                "vpn_detection": True,
                "proxy_detection": True
            },
            "behavioral_checks": {
                "new_customer_limit": Decimal("500.00"),
                "unusual_hours": True,
                "device_fingerprinting": True
            },
            "amount_checks": {
                "round_amounts": True,  # Flag round amounts as suspicious
                "large_amounts": Decimal("10000.00"),
                "unusual_patterns": True
            }
        }
    
    async def _initialize_fraud_detection(self):
        """Initialize advanced fraud detection system."""
        try:
            # Load fraud detection models (in production, load ML models)
            self.fraud_models = {
                "velocity_model": self._create_velocity_checker(),
                "behavioral_model": self._create_behavioral_checker(),
                "geographic_model": self._create_geographic_checker(),
                "amount_model": self._create_amount_checker()
            }
            
            self.logger.info("Fraud detection system initialized")
            
        except Exception as e:
            self.logger.error(f"Fraud detection initialization failed: {e}")
    
    def _create_velocity_checker(self):
        """Create velocity-based fraud checker."""
        def check_velocity(customer_id: str, amount: Decimal, timeframe: str = "hour") -> float:
            # Simplified velocity check - in production, use Redis for real-time tracking
            return 0.0  # Risk score
        return check_velocity
    
    def _create_behavioral_checker(self):
        """Create behavioral analysis fraud checker."""
        def check_behavior(request: PaymentRequest) -> float:
            # Simplified behavioral check
            return 0.0  # Risk score
        return check_behavior
    
    def _create_geographic_checker(self):
        """Create geographic risk checker."""
        def check_geographic(billing_country: str, ip_country: str) -> float:
            # Simplified geographic check
            return 0.0  # Risk score
        return check_geographic
    
    def _create_amount_checker(self):
        """Create amount-based risk checker."""
        def check_amount(amount: Decimal, currency: Currency) -> float:
            # Simplified amount check
            return 0.0  # Risk score
        return check_amount
    
    async def process_payment(
        self,
        payment_request: PaymentRequest
    ) -> PaymentResult:
        """
        Process payment with intelligent gateway routing and fraud detection.
        
        Args:
            payment_request: Payment processing request details
            
        Returns:
            Comprehensive payment processing result
        """
        try:
            start_time = datetime.utcnow()
            self.logger.info(f"Processing payment request: {payment_request.request_id}")
            
            # Generate unique transaction ID
            transaction_id = f"txn_{uuid.uuid4().hex}"
            
            # Fraud detection assessment
            fraud_assessment = await self._assess_fraud_risk(payment_request)
            
            if fraud_assessment.risk_level == FraudRiskLevel.VERY_HIGH:
                return self._create_declined_result(
                    transaction_id, payment_request, "Declined due to high fraud risk"
                )
            
            # Gateway selection and routing
            selected_gateway = await self._select_payment_gateway(payment_request)
            
            if not selected_gateway:
                raise PaymentException("No suitable payment gateway available")
            
            # Process payment with selected gateway
            gateway_result = await self._process_gateway_payment(
                selected_gateway, payment_request, transaction_id
            )
            
            # Calculate fees and net amount
            fees = await self._calculate_processing_fees(
                selected_gateway, payment_request.amount, payment_request.currency
            )
            
            net_amount = payment_request.amount - fees
            
            # Create payment result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            payment_result = PaymentResult(
                transaction_id=transaction_id,
                gateway_transaction_id=gateway_result.get("gateway_transaction_id", ""),
                gateway=selected_gateway,
                status=PaymentStatus(gateway_result.get("status", "failed")),
                amount=payment_request.amount,
                currency=payment_request.currency,
                fees=fees,
                net_amount=net_amount,
                processing_time=processing_time,
                created_at=start_time,
                gateway_response=gateway_result,
                risk_assessment=fraud_assessment.__dict__,
                fraud_score=fraud_assessment.risk_score,
                requires_action=gateway_result.get("requires_action", False),
                next_action=gateway_result.get("next_action"),
                receipt_url=gateway_result.get("receipt_url")
            )
            
            # Store payment result
            await self._store_payment_result(payment_result, payment_request)
            
            # Process revenue distribution if payment successful
            if payment_result.status == PaymentStatus.COMPLETED:
                await self._process_revenue_distribution(payment_result, payment_request)
            
            # Send notifications
            await self._send_payment_notifications(payment_result, payment_request)
            
            self.logger.info(
                f"Payment processed successfully: {transaction_id} "
                f"({payment_result.status.value}) in {processing_time:.2f}s"
            )
            
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            raise PaymentException(f"Payment processing error: {e}")
    
    async def _assess_fraud_risk(self, request: PaymentRequest) -> FraudAssessment:
        """Comprehensive fraud risk assessment."""
        try:
            risk_factors = []
            total_risk_score = 0.0
            
            # Velocity checks
            velocity_score = await self._check_velocity_fraud(request.customer_id, request.amount)
            total_risk_score += velocity_score
            if velocity_score > 20:
                risk_factors.append("High transaction velocity")
            
            # Geographic checks
            geographic_score = await self._check_geographic_fraud(request)
            total_risk_score += geographic_score
            if geographic_score > 15:
                risk_factors.append("Geographic risk factors")
            
            # Behavioral checks
            behavioral_score = await self._check_behavioral_fraud(request)
            total_risk_score += behavioral_score
            if behavioral_score > 15:
                risk_factors.append("Unusual behavioral patterns")
            
            # Amount checks
            amount_score = await self._check_amount_fraud(request.amount, request.currency)
            total_risk_score += amount_score
            if amount_score > 10:
                risk_factors.append("Suspicious amount patterns")
            
            # Customer history checks
            history_score = await self._check_customer_history_fraud(request.customer_id)
            total_risk_score += history_score
            if history_score > 20:
                risk_factors.append("Negative customer history")
            
            # Determine risk level
            if total_risk_score >= 80:
                risk_level = FraudRiskLevel.VERY_HIGH
                recommended_action = "decline"
            elif total_risk_score >= 60:
                risk_level = FraudRiskLevel.HIGH
                recommended_action = "review"
            elif total_risk_score >= 40:
                risk_level = FraudRiskLevel.MEDIUM
                recommended_action = "monitor"
            elif total_risk_score >= 20:
                risk_level = FraudRiskLevel.LOW
                recommended_action = "approve"
            else:
                risk_level = FraudRiskLevel.VERY_LOW
                recommended_action = "approve"
            
            # Calculate confidence score
            confidence_score = min(1.0, (len(risk_factors) * 0.2) + 0.6)
            
            assessment = FraudAssessment(
                transaction_id=request.request_id,
                risk_level=risk_level,
                risk_score=total_risk_score,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence_score=confidence_score,
                assessment_details={
                    "velocity_score": velocity_score,
                    "geographic_score": geographic_score,
                    "behavioral_score": behavioral_score,
                    "amount_score": amount_score,
                    "history_score": history_score
                }
            )
            
            # Store fraud assessment
            await self._store_fraud_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Fraud assessment failed: {e}")
            # Return safe default assessment
            return FraudAssessment(
                transaction_id=request.request_id,
                risk_level=FraudRiskLevel.MEDIUM,
                risk_score=50.0,
                risk_factors=["Assessment error"],
                recommended_action="review",
                confidence_score=0.5
            )
    
    async def _check_velocity_fraud(self, customer_id: str, amount: Decimal) -> float:
        """Check for velocity-based fraud indicators."""
        try:
            # Check transaction velocity in Redis
            now = datetime.utcnow()
            hour_key = f"velocity:hour:{customer_id}:{now.hour}"
            day_key = f"velocity:day:{customer_id}:{now.date()}"
            
            # Get current counts
            hour_count = await self.redis.get(f"{hour_key}:count") or 0
            hour_amount = Decimal(str(await self.redis.get(f"{hour_key}:amount") or 0))
            day_count = await self.redis.get(f"{day_key}:count") or 0
            day_amount = Decimal(str(await self.redis.get(f"{day_key}:amount") or 0))
            
            risk_score = 0.0
            
            # Check hourly limits
            if int(hour_count) >= self.fraud_rules["velocity_checks"]["transactions_per_hour"]:
                risk_score += 25.0
            
            if hour_amount >= self.fraud_rules["velocity_checks"]["amount_per_hour"]:
                risk_score += 20.0
            
            # Check daily limits
            if int(day_count) >= self.fraud_rules["velocity_checks"]["transactions_per_day"]:
                risk_score += 30.0
            
            if day_amount >= self.fraud_rules["velocity_checks"]["amount_per_day"]:
                risk_score += 25.0
            
            return min(risk_score, 50.0)  # Cap at 50 points
            
        except Exception as e:
            self.logger.error(f"Velocity fraud check failed: {e}")
            return 0.0
    
    async def _check_geographic_fraud(self, request: PaymentRequest) -> float:
        """Check for geographic risk indicators."""
        try:
            risk_score = 0.0
            billing_details = request.billing_details
            
            # Check high-risk countries
            billing_country = billing_details.get("country", "")
            if billing_country in self.fraud_rules["geographic_checks"]["high_risk_countries"]:
                risk_score += 30.0
            
            # Check for VPN/Proxy usage (simplified)
            if billing_details.get("is_vpn", False):
                risk_score += 15.0
            
            # Check country mismatch between billing and IP
            ip_country = billing_details.get("ip_country", "")
            if billing_country != ip_country and billing_country and ip_country:
                risk_score += 10.0
            
            return min(risk_score, 40.0)  # Cap at 40 points
            
        except Exception as e:
            self.logger.error(f"Geographic fraud check failed: {e}")
            return 0.0
    
    async def _check_behavioral_fraud(self, request: PaymentRequest) -> float:
        """Check for behavioral fraud indicators."""
        try:
            risk_score = 0.0
            
            # Check for new customer with large transaction
            is_new_customer = await self._is_new_customer(request.customer_id)
            if is_new_customer and request.amount > self.fraud_rules["behavioral_checks"]["new_customer_limit"]:
                risk_score += 25.0
            
            # Check transaction timing (unusual hours)
            now = datetime.utcnow()
            if self.fraud_rules["behavioral_checks"]["unusual_hours"] and (now.hour < 6 or now.hour > 23):
                risk_score += 10.0
            
            # Check for suspicious metadata patterns
            metadata = request.metadata
            if self._has_suspicious_metadata(metadata):
                risk_score += 15.0
            
            return min(risk_score, 35.0)  # Cap at 35 points
            
        except Exception as e:
            self.logger.error(f"Behavioral fraud check failed: {e}")
            return 0.0
    
    async def _check_amount_fraud(self, amount: Decimal, currency: Currency) -> float:
        """Check for amount-based fraud indicators."""
        try:
            risk_score = 0.0
            
            # Check for round amounts (potential fraud indicator)
            if self.fraud_rules["amount_checks"]["round_amounts"] and amount % 100 == 0:
                risk_score += 5.0
            
            # Check for unusually large amounts
            if amount >= self.fraud_rules["amount_checks"]["large_amounts"]:
                risk_score += 20.0
            
            # Check for unusual amount patterns (simplified)
            amount_str = str(amount)
            if len(set(amount_str.replace(".", ""))) <= 2:  # Repeated digits
                risk_score += 10.0
            
            return min(risk_score, 25.0)  # Cap at 25 points
            
        except Exception as e:
            self.logger.error(f"Amount fraud check failed: {e}")
            return 0.0
    
    async def _check_customer_history_fraud(self, customer_id: str) -> float:
        """Check customer history for fraud indicators."""
        try:
            query = """
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
                COUNT(CASE WHEN status = 'disputed' THEN 1 END) as disputed_count,
                COUNT(CASE WHEN status = 'chargeback' THEN 1 END) as chargeback_count,
                MAX(created_at) as last_transaction
            FROM payment_transactions 
            WHERE customer_id = $1 
            AND created_at >= NOW() - INTERVAL '90 days'
            """
            
            result = await self.db.fetchrow(query, customer_id)
            
            if not result or result["total_transactions"] == 0:
                return 0.0  # New customer, neutral score
            
            risk_score = 0.0
            total_transactions = result["total_transactions"]
            
            # Check failure rate
            failure_rate = result["failed_count"] / total_transactions if total_transactions > 0 else 0
            if failure_rate > 0.3:  # More than 30% failures
                risk_score += 25.0
            elif failure_rate > 0.1:  # More than 10% failures
                risk_score += 10.0
            
            # Check dispute rate
            dispute_rate = result["disputed_count"] / total_transactions if total_transactions > 0 else 0
            if dispute_rate > 0.1:  # More than 10% disputes
                risk_score += 30.0
            elif dispute_rate > 0.05:  # More than 5% disputes
                risk_score += 15.0
            
            # Check chargeback rate
            chargeback_rate = result["chargeback_count"] / total_transactions if total_transactions > 0 else 0
            if chargeback_rate > 0.05:  # More than 5% chargebacks
                risk_score += 35.0
            elif chargeback_rate > 0.02:  # More than 2% chargebacks
                risk_score += 20.0
            
            return min(risk_score, 50.0)  # Cap at 50 points
            
        except Exception as e:
            self.logger.error(f"Customer history fraud check failed: {e}")
            return 0.0
    
    async def _is_new_customer(self, customer_id: str) -> bool:
        """Check if customer is new (first transaction)."""
        try:
            query = """
            SELECT COUNT(*) as transaction_count
            FROM payment_transactions 
            WHERE customer_id = $1
            """
            
            result = await self.db.fetchrow(query, customer_id)
            return result["transaction_count"] == 0
            
        except Exception as e:
            self.logger.error(f"New customer check failed: {e}")
            return False
    
    def _has_suspicious_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check metadata for suspicious patterns."""
        # Simplified suspicious metadata detection
        suspicious_patterns = [
            "test", "fake", "fraud", "scam", "dummy",
            "aaaa", "bbbb", "1111", "0000"
        ]
        
        metadata_str = json.dumps(metadata).lower()
        return any(pattern in metadata_str for pattern in suspicious_patterns)
    
    async def _select_payment_gateway(self, request: PaymentRequest) -> Optional[PaymentGateway]:
        """Select optimal payment gateway based on routing rules."""
        try:
            # Start with preferred gateway if specified
            if request.preferred_gateway and request.preferred_gateway in self.gateway_configs:
                if await self._is_gateway_suitable(request.preferred_gateway, request):
                    return request.preferred_gateway
            
            # Apply routing rules
            suitable_gateways = []
            
            # Currency-based routing
            currency_gateways = self.routing_rules["currency_routing"].get(request.currency, [])
            suitable_gateways.extend(currency_gateways)
            
            # Amount-based routing
            for category, rules in self.routing_rules["amount_routing"].items():
                if request.amount <= rules["max"]:
                    suitable_gateways.extend(rules["gateways"])
                    break
            
            # Country-based routing (if available)
            billing_country = request.billing_details.get("country", "")
            if billing_country:
                country_gateways = self.routing_rules["country_routing"].get(billing_country, [])
                suitable_gateways.extend(country_gateways)
            
            # Remove duplicates and filter by availability
            suitable_gateways = list(set(suitable_gateways))
            available_gateways = []
            
            for gateway in suitable_gateways:
                if gateway in self.gateway_configs and await self._is_gateway_available(gateway):
                    available_gateways.append(gateway)
            
            # Select best gateway based on performance metrics
            if available_gateways:
                return await self._select_best_performing_gateway(available_gateways, request)
            
            # Fallback to default gateway
            default_gateway = self.routing_rules["default_gateway"]
            if default_gateway in self.gateway_configs:
                return default_gateway
            
            return None
            
        except Exception as e:
            self.logger.error(f"Gateway selection failed: {e}")
            return self.routing_rules.get("default_gateway")
    
    async def _is_gateway_suitable(self, gateway: PaymentGateway, request: PaymentRequest) -> bool:
        """Check if gateway is suitable for the payment request."""
        config = self.gateway_configs.get(gateway)
        if not config:
            return False
        
        # Check currency support
        if request.currency not in config.supported_currencies:
            return False
        
        # Check amount limits
        if request.amount < config.minimum_amount or request.amount > config.maximum_amount:
            return False
        
        # Check country support (if available)
        billing_country = request.billing_details.get("country", "")
        if billing_country and billing_country not in config.supported_countries:
            return False
        
        return True
    
    async def _is_gateway_available(self, gateway: PaymentGateway) -> bool:
        """Check if gateway is currently available."""
        try:
            # Check gateway health status in Redis
            health_key = f"gateway_health:{gateway.value}"
            health_status = await self.redis.get(health_key)
            
            if health_status == "down":
                return False
            
            # Additional availability checks could be added here
            
            return True
            
        except Exception as e:
            self.logger.error(f"Gateway availability check failed: {e}")
            return True  # Default to available if check fails
    
    async def _select_best_performing_gateway(
        self,
        available_gateways: List[PaymentGateway],
        request: PaymentRequest
    ) -> PaymentGateway:
        """Select best performing gateway from available options."""
        try:
            # Get performance metrics for each gateway
            gateway_scores = {}
            
            for gateway in available_gateways:
                metrics = await self._get_gateway_performance_metrics(gateway)
                
                # Calculate performance score
                score = (
                    metrics.get("success_rate", 0.5) * 0.4 +
                    (1 - metrics.get("avg_processing_time", 30) / 60) * 0.3 +  # Faster is better
                    (1 - metrics.get("fee_percentage", 0.05) / 0.1) * 0.2 +  # Lower fees better
                    metrics.get("uptime", 0.95) * 0.1
                )
                
                gateway_scores[gateway] = score
            
            # Return gateway with highest score
            best_gateway = max(gateway_scores.items(), key=lambda x: x[1])
            return best_gateway[0]
            
        except Exception as e:
            self.logger.error(f"Best gateway selection failed: {e}")
            return available_gateways[0] if available_gateways else None
    
    async def _get_gateway_performance_metrics(self, gateway: PaymentGateway) -> Dict[str, float]:
        """Get performance metrics for gateway."""
        try:
            query = """
            SELECT 
                AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(processing_time) as avg_processing_time,
                AVG(fees / amount) as avg_fee_percentage
            FROM payment_transactions 
            WHERE gateway = $1 
            AND created_at >= NOW() - INTERVAL '24 hours'
            """
            
            result = await self.db.fetchrow(query, gateway.value)
            
            return {
                "success_rate": float(result["success_rate"] or 0.85),
                "avg_processing_time": float(result["avg_processing_time"] or 15),
                "fee_percentage": float(result["avg_fee_percentage"] or 0.03),
                "uptime": 0.99  # This would come from monitoring system
            }
            
        except Exception as e:
            self.logger.error(f"Gateway metrics retrieval failed: {e}")
            return {
                "success_rate": 0.85,
                "avg_processing_time": 15,
                "fee_percentage": 0.03,
                "uptime": 0.99
            }


# Factory function for easy instantiation
def create_payment_processor(config: Optional[Dict[str, Any]] = None) -> AdvancedPaymentProcessor:
    """Create and return configured payment processor instance."""
    return AdvancedPaymentProcessor(config)
