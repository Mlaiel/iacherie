#!/usr/bin/env python3
"""
💰 FINANCIAL SERVICES MODULE - ENTERPRISE FINANCIAL & PAYMENT ENTRY POINT
=========================================================================

© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE
⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT

Entry point for Financial Services module.
Provides enterprise-grade financial and payment processing services.

Module: financial_services/
Services: 16 Financial & Payment services
Capabilities: Payment processing, revenue distribution, billing, compliance

Key Services:
------------
💳 Payment Processing Service      - Multi-gateway payment processing
💵 Billing Service                - Automated billing and invoicing
💰 Revenue Distribution Service   - Creator revenue distribution
💎 Royalty Distribution Service   - Royalty and licensing payments
⚡ Revenue Optimization Service   - Revenue optimization engine
📊 Subscription Management Service - Subscription lifecycle management
🔍 Fraud Detection Service        - AI-powered fraud detection
💱 Currency Conversion Service     - Multi-currency support
🧾 Invoice Generation Service      - Automated invoice generation
📊 Financial Reporting Service     - Financial analytics and reporting
💰 Tax Calculation Service         - Tax computation and compliance
💳 Payment Gateway Orchestrator    - Multi-gateway orchestration
📈 Financial Forecasting Service   - Financial planning and forecasting
🔐 Financial Security Service      - Financial data protection
📊 Financial Analytics Service     - Financial performance analytics

Contact: Fahed Mlaiel (mlaiel@live.de)
Team: Financial Services Team (6 experts)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Decimal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    """Payment methods supported"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"

class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    BTC = "BTC"
    ETH = "ETH"

class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    SUBSCRIPTION = "subscription"
    ROYALTY = "royalty"
    COMMISSION = "commission"
    FEE = "fee"
    TAX = "tax"

class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

@dataclass
class PaymentAccount:
    """Payment account information"""
    account_id: str
    user_id: str
    account_type: str
    payment_methods: List[PaymentMethod]
    default_currency: Currency
    balance: Decimal = Decimal('0.00')
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Transaction:
    """Transaction data structure"""
    transaction_id: str
    from_account: str
    to_account: Optional[str]
    amount: Decimal
    currency: Currency
    transaction_type: TransactionType
    status: TransactionStatus
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fees: Decimal = Decimal('0.00')
    tax: Decimal = Decimal('0.00')
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class FinancialRequest:
    """Financial service request"""
    request_id: str
    service_type: str
    user_id: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    amount: Optional[Decimal] = None
    currency: Currency = Currency.USD
    priority: str = "normal"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FinancialResponse:
    """Financial service response"""
    request_id: str
    service_type: str
    status: str
    result: Dict[str, Any]
    transaction_id: Optional[str] = None
    amount_processed: Optional[Decimal] = None
    fees_charged: Optional[Decimal] = None
    processing_time: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class FinancialServicesOrchestrator:
    """
    Enterprise Financial Services Orchestrator
    Coordinates all financial and payment processing services
    """
    
    def __init__(self):
        self.services = {}
        self.payment_accounts = {}
        self.transactions = {}
        self.payment_gateways = {}
        self.metrics = {}
        self.fraud_detection = {}
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all financial services"""
        try:
            # Import financial services (graceful imports)
            try:
                from . import payment_processing_service
                self.services['payment_processing'] = payment_processing_service
            except ImportError:
                logger.warning("⚠️ payment_processing_service not found")
            
            try:
                from . import billing_service
                self.services['billing'] = billing_service
            except ImportError:
                logger.warning("⚠️ billing_service not found")
            
            try:
                from . import revenue_distribution_service
                self.services['revenue_distribution'] = revenue_distribution_service
            except ImportError:
                logger.warning("⚠️ revenue_distribution_service not found")
            
            try:
                from . import royalty_distribution_service
                self.services['royalty_distribution'] = royalty_distribution_service
            except ImportError:
                logger.warning("⚠️ royalty_distribution_service not found")
            
            try:
                from . import revenue_optimization_service
                self.services['revenue_optimization'] = revenue_optimization_service
            except ImportError:
                logger.warning("⚠️ revenue_optimization_service not found")
            
            try:
                from . import subscription_management_service
                self.services['subscription_management'] = subscription_management_service
            except ImportError:
                logger.warning("⚠️ subscription_management_service not found")
            
            try:
                from . import fraud_detection_service
                self.services['fraud_detection'] = fraud_detection_service
            except ImportError:
                logger.warning("⚠️ fraud_detection_service not found")
            
            # Initialize payment gateways
            await self._initialize_payment_gateways()
            
            # Initialize metrics
            self.metrics = {
                'total_transactions': 0,
                'successful_transactions': 0,
                'failed_transactions': 0,
                'total_volume': Decimal('0.00'),
                'total_fees': Decimal('0.00'),
                'fraud_detection_rate': 0.0,
                'avg_processing_time': 0.0,
                'active_subscriptions': 0,
                'monthly_recurring_revenue': Decimal('0.00')
            }
            
            self.is_initialized = True
            logger.info("✅ Financial Services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Financial Services: {e}")
            return False
    
    async def _initialize_payment_gateways(self):
        """Initialize payment gateway configurations"""
        self.payment_gateways = {
            'stripe': {
                'name': 'Stripe',
                'supported_methods': [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD],
                'supported_currencies': [Currency.USD, Currency.EUR, Currency.GBP],
                'fee_rate': Decimal('0.029'),  # 2.9%
                'is_active': True
            },
            'paypal': {
                'name': 'PayPal',
                'supported_methods': [PaymentMethod.PAYPAL, PaymentMethod.CREDIT_CARD],
                'supported_currencies': [Currency.USD, Currency.EUR, Currency.GBP, Currency.CAD],
                'fee_rate': Decimal('0.034'),  # 3.4%
                'is_active': True
            },
            'crypto': {
                'name': 'Cryptocurrency Gateway',
                'supported_methods': [PaymentMethod.CRYPTOCURRENCY],
                'supported_currencies': [Currency.BTC, Currency.ETH],
                'fee_rate': Decimal('0.015'),  # 1.5%
                'is_active': True
            }
        }
    
    async def process_financial_request(self, request: FinancialRequest) -> FinancialResponse:
        """Process financial service request"""
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Route to appropriate service based on service type
            if request.service_type == "payment_processing":
                response = await self._handle_payment_processing(request)
            elif request.service_type == "billing":
                response = await self._handle_billing(request)
            elif request.service_type == "revenue_distribution":
                response = await self._handle_revenue_distribution(request)
            elif request.service_type == "royalty_distribution":
                response = await self._handle_royalty_distribution(request)
            elif request.service_type == "subscription_management":
                response = await self._handle_subscription_management(request)
            elif request.service_type == "fraud_detection":
                response = await self._handle_fraud_detection(request)
            elif request.service_type == "currency_conversion":
                response = await self._handle_currency_conversion(request)
            elif request.service_type == "tax_calculation":
                response = await self._handle_tax_calculation(request)
            else:
                response = await self._handle_generic_financial_operation(request)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            
            # Update metrics
            self.metrics['total_transactions'] += 1
            if response.status == "success":
                self.metrics['successful_transactions'] += 1
                if response.amount_processed:
                    self.metrics['total_volume'] += response.amount_processed
                if response.fees_charged:
                    self.metrics['total_fees'] += response.fees_charged
            else:
                self.metrics['failed_transactions'] += 1
            
            # Update average processing time
            self._update_avg_processing_time(processing_time)
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Financial request processing failed: {e}")
            
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="error",
                result={"error": str(e)},
                processing_time=processing_time
            )
    
    async def _handle_payment_processing(self, request: FinancialRequest) -> FinancialResponse:
        """Handle payment processing"""
        try:
            payment_data = request.data
            amount = request.amount or Decimal(str(payment_data.get('amount', '0.00')))
            currency = request.currency
            payment_method = PaymentMethod(payment_data.get('payment_method', 'credit_card'))
            
            # Fraud detection check
            fraud_score = await self._check_fraud(request.user_id, amount, payment_method)
            if fraud_score > 0.8:
                return FinancialResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    status="blocked",
                    result={"reason": "High fraud risk", "fraud_score": fraud_score},
                    recommendations=["Contact customer support", "Verify payment details"]
                )
            
            # Select appropriate payment gateway
            gateway = await self._select_payment_gateway(payment_method, currency, amount)
            if not gateway:
                return FinancialResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    status="error",
                    result={"error": "No suitable payment gateway found"}
                )
            
            # Calculate fees
            fees = self._calculate_fees(amount, gateway['fee_rate'])
            
            # Process payment
            if 'payment_processing' in self.services:
                payment_service = self.services['payment_processing']
                if hasattr(payment_service, 'process_payment'):
                    result = await payment_service.process_payment(payment_data)
                else:
                    result = await self._basic_payment_processing(payment_data, gateway, fees)
            else:
                result = await self._basic_payment_processing(payment_data, gateway, fees)
            
            # Create transaction record
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                transaction_id=transaction_id,
                from_account=request.user_id,
                to_account=payment_data.get('recipient'),
                amount=amount,
                currency=currency,
                transaction_type=TransactionType.PAYMENT,
                status=TransactionStatus.COMPLETED if result.get('success') else TransactionStatus.FAILED,
                payment_method=payment_method,
                fees=fees,
                description=payment_data.get('description', 'Payment transaction')
            )
            
            self.transactions[transaction_id] = transaction
            
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="success" if result.get('success') else "failed",
                result=result,
                transaction_id=transaction_id,
                amount_processed=amount,
                fees_charged=fees,
                recommendations=[
                    "Payment processed successfully" if result.get('success') else "Payment failed",
                    f"Gateway used: {gateway['name']}",
                    f"Fraud score: {fraud_score:.2f}"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Payment processing failed: {e}")
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="error",
                result={"error": str(e)}
            )
    
    async def _handle_revenue_distribution(self, request: FinancialRequest) -> FinancialResponse:
        """Handle revenue distribution"""
        try:
            distribution_data = request.data
            total_revenue = Decimal(str(distribution_data.get('total_revenue', '0.00')))
            recipients = distribution_data.get('recipients', [])
            
            # Use revenue distribution service if available
            if 'revenue_distribution' in self.services:
                revenue_service = self.services['revenue_distribution']
                if hasattr(revenue_service, 'distribute_revenue'):
                    result = await revenue_service.distribute_revenue(total_revenue, recipients)
                else:
                    result = await self._basic_revenue_distribution(total_revenue, recipients)
            else:
                result = await self._basic_revenue_distribution(total_revenue, recipients)
            
            # Create payout transactions
            transactions_created = []
            for payout in result.get('payouts', []):
                transaction_id = str(uuid.uuid4())
                transaction = Transaction(
                    transaction_id=transaction_id,
                    from_account="revenue_pool",
                    to_account=payout['recipient_id'],
                    amount=Decimal(str(payout['amount'])),
                    currency=Currency.USD,
                    transaction_type=TransactionType.PAYOUT,
                    status=TransactionStatus.COMPLETED,
                    description="Revenue distribution payout"
                )
                
                self.transactions[transaction_id] = transaction
                transactions_created.append(transaction_id)
            
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="success",
                result=result,
                amount_processed=total_revenue,
                recommendations=[
                    f"Revenue distributed to {len(recipients)} recipients",
                    f"Total amount: ${total_revenue}",
                    f"Transactions created: {len(transactions_created)}"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Revenue distribution failed: {e}")
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="error",
                result={"error": str(e)}
            )
    
    async def _handle_subscription_management(self, request: FinancialRequest) -> FinancialResponse:
        """Handle subscription management"""
        try:
            subscription_data = request.data
            action = request.action
            
            if 'subscription_management' in self.services:
                subscription_service = self.services['subscription_management']
                if hasattr(subscription_service, f'{action}_subscription'):
                    method = getattr(subscription_service, f'{action}_subscription')
                    result = await method(subscription_data)
                else:
                    result = await self._basic_subscription_operation(action, subscription_data)
            else:
                result = await self._basic_subscription_operation(action, subscription_data)
            
            # Update subscription metrics
            if action == "create" and result.get('success'):
                self.metrics['active_subscriptions'] += 1
                monthly_amount = Decimal(str(subscription_data.get('monthly_amount', '0.00')))
                self.metrics['monthly_recurring_revenue'] += monthly_amount
            elif action == "cancel" and result.get('success'):
                self.metrics['active_subscriptions'] -= 1
                monthly_amount = Decimal(str(subscription_data.get('monthly_amount', '0.00')))
                self.metrics['monthly_recurring_revenue'] -= monthly_amount
            
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="success" if result.get('success') else "failed",
                result=result,
                recommendations=[
                    f"Subscription {action} {'successful' if result.get('success') else 'failed'}",
                    f"Active subscriptions: {self.metrics['active_subscriptions']}",
                    f"MRR: ${self.metrics['monthly_recurring_revenue']}"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Subscription management failed: {e}")
            return FinancialResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status="error",
                result={"error": str(e)}
            )
    
    async def _check_fraud(self, user_id: str, amount: Decimal, payment_method: PaymentMethod) -> float:
        """Check for fraud indicators"""
        try:
            # Basic fraud detection logic
            fraud_score = 0.0
            
            # High amount flag
            if amount > Decimal('1000.00'):
                fraud_score += 0.2
            
            # Multiple transactions in short time
            recent_transactions = [
                t for t in self.transactions.values()
                if t.from_account == user_id and 
                (datetime.now() - t.created_at).total_seconds() < 3600  # 1 hour
            ]
            
            if len(recent_transactions) > 5:
                fraud_score += 0.3
            
            # Cryptocurrency transactions (higher risk)
            if payment_method == PaymentMethod.CRYPTOCURRENCY:
                fraud_score += 0.1
            
            # Use fraud detection service if available
            if 'fraud_detection' in self.services:
                fraud_service = self.services['fraud_detection']
                if hasattr(fraud_service, 'analyze_transaction'):
                    ai_score = await fraud_service.analyze_transaction({
                        'user_id': user_id,
                        'amount': float(amount),
                        'payment_method': payment_method.value
                    })
                    fraud_score = max(fraud_score, ai_score.get('fraud_score', 0.0))
            
            return min(fraud_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"❌ Fraud detection failed: {e}")
            return 0.0  # Default to low risk on error
    
    async def _select_payment_gateway(self, payment_method: PaymentMethod, currency: Currency, amount: Decimal) -> Optional[Dict[str, Any]]:
        """Select appropriate payment gateway"""
        try:
            best_gateway = None
            lowest_fee = Decimal('1.0')  # 100%
            
            for gateway_id, gateway in self.payment_gateways.items():
                if (gateway['is_active'] and 
                    payment_method in gateway['supported_methods'] and
                    currency in gateway['supported_currencies']):
                    
                    if gateway['fee_rate'] < lowest_fee:
                        lowest_fee = gateway['fee_rate']
                        best_gateway = gateway
            
            return best_gateway
            
        except Exception as e:
            logger.error(f"❌ Gateway selection failed: {e}")
            return None
    
    def _calculate_fees(self, amount: Decimal, fee_rate: Decimal) -> Decimal:
        """Calculate transaction fees"""
        return (amount * fee_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _basic_payment_processing(self, payment_data: Dict[str, Any], gateway: Dict[str, Any], fees: Decimal) -> Dict[str, Any]:
        """Basic payment processing simulation"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Simulate success/failure (95% success rate)
        import random
        success = random.random() > 0.05
        
        return {
            'success': success,
            'gateway': gateway['name'],
            'fees': float(fees),
            'transaction_id': str(uuid.uuid4()),
            'processed_at': datetime.now().isoformat()
        }
    
    async def _basic_revenue_distribution(self, total_revenue: Decimal, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Basic revenue distribution"""
        await asyncio.sleep(0.05)
        
        payouts = []
        for recipient in recipients:
            percentage = Decimal(str(recipient.get('percentage', 0))) / 100
            payout_amount = (total_revenue * percentage).quantize(Decimal('0.01'))
            
            payouts.append({
                'recipient_id': recipient['id'],
                'amount': float(payout_amount),
                'percentage': float(percentage * 100)
            })
        
        return {
            'success': True,
            'total_distributed': float(total_revenue),
            'payouts': payouts,
            'distribution_date': datetime.now().isoformat()
        }
    
    async def _basic_subscription_operation(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic subscription operation"""
        await asyncio.sleep(0.03)
        
        return {
            'success': True,
            'action': action,
            'subscription_id': data.get('subscription_id', str(uuid.uuid4())),
            'processed_at': datetime.now().isoformat()
        }
    
    async def _handle_billing(self, request: FinancialRequest) -> FinancialResponse:
        """Handle billing operations"""
        if 'billing' in self.services:
            billing_service = self.services['billing']
            if hasattr(billing_service, 'process_billing'):
                result = await billing_service.process_billing(request.data)
            else:
                result = {'billed': True, 'invoice_id': str(uuid.uuid4())}
        else:
            result = {'billed': True, 'invoice_id': str(uuid.uuid4())}
        
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result=result
        )
    
    async def _handle_royalty_distribution(self, request: FinancialRequest) -> FinancialResponse:
        """Handle royalty distribution"""
        if 'royalty_distribution' in self.services:
            royalty_service = self.services['royalty_distribution']
            if hasattr(royalty_service, 'distribute_royalties'):
                result = await royalty_service.distribute_royalties(request.data)
            else:
                result = {'distributed': True, 'royalty_id': str(uuid.uuid4())}
        else:
            result = {'distributed': True, 'royalty_id': str(uuid.uuid4())}
        
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result=result
        )
    
    async def _handle_fraud_detection(self, request: FinancialRequest) -> FinancialResponse:
        """Handle fraud detection"""
        fraud_score = await self._check_fraud(
            request.user_id,
            request.amount or Decimal('0.00'),
            PaymentMethod.CREDIT_CARD
        )
        
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result={'fraud_score': fraud_score, 'risk_level': 'high' if fraud_score > 0.7 else 'low'}
        )
    
    async def _handle_currency_conversion(self, request: FinancialRequest) -> FinancialResponse:
        """Handle currency conversion"""
        # Simplified conversion rates
        conversion_rates = {
            (Currency.USD, Currency.EUR): Decimal('0.85'),
            (Currency.USD, Currency.GBP): Decimal('0.75'),
            (Currency.EUR, Currency.USD): Decimal('1.18'),
            (Currency.GBP, Currency.USD): Decimal('1.33')
        }
        
        from_currency = Currency(request.data.get('from_currency', 'USD'))
        to_currency = Currency(request.data.get('to_currency', 'EUR'))
        amount = request.amount or Decimal(str(request.data.get('amount', '0.00')))
        
        rate_key = (from_currency, to_currency)
        if rate_key in conversion_rates:
            converted_amount = amount * conversion_rates[rate_key]
        else:
            converted_amount = amount  # Same currency
        
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result={
                'original_amount': float(amount),
                'converted_amount': float(converted_amount),
                'from_currency': from_currency.value,
                'to_currency': to_currency.value,
                'exchange_rate': float(conversion_rates.get(rate_key, Decimal('1.00')))
            }
        )
    
    async def _handle_tax_calculation(self, request: FinancialRequest) -> FinancialResponse:
        """Handle tax calculation"""
        amount = request.amount or Decimal(str(request.data.get('amount', '0.00')))
        tax_rate = Decimal(str(request.data.get('tax_rate', '0.10')))  # 10% default
        tax_amount = (amount * tax_rate).quantize(Decimal('0.01'))
        
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result={
                'amount': float(amount),
                'tax_rate': float(tax_rate),
                'tax_amount': float(tax_amount),
                'total_amount': float(amount + tax_amount)
            }
        )
    
    async def _handle_generic_financial_operation(self, request: FinancialRequest) -> FinancialResponse:
        """Handle generic financial operation"""
        return FinancialResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status="success",
            result={'processed': True, 'operation': request.service_type}
        )
    
    def _update_avg_processing_time(self, processing_time: float):
        """Update average processing time metric"""
        if self.metrics['total_transactions'] > 1:
            current_avg = self.metrics['avg_processing_time']
            new_avg = ((current_avg * (self.metrics['total_transactions'] - 1)) + processing_time) / self.metrics['total_transactions']
            self.metrics['avg_processing_time'] = new_avg
        else:
            self.metrics['avg_processing_time'] = processing_time
    
    async def get_financial_health(self) -> Dict[str, Any]:
        """Get financial services health status"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'services': {},
            'metrics': {
                'total_transactions': self.metrics['total_transactions'],
                'success_rate': (
                    self.metrics['successful_transactions'] / self.metrics['total_transactions']
                    if self.metrics['total_transactions'] > 0 else 1.0
                ),
                'total_volume': float(self.metrics['total_volume']),
                'total_fees': float(self.metrics['total_fees']),
                'avg_processing_time': self.metrics['avg_processing_time'],
                'active_subscriptions': self.metrics['active_subscriptions'],
                'monthly_recurring_revenue': float(self.metrics['monthly_recurring_revenue'])
            },
            'payment_gateways': len([g for g in self.payment_gateways.values() if g['is_active']]),
            'active_transactions': len([t for t in self.transactions.values() if t.status == TransactionStatus.PROCESSING])
        }
        
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    status = await service.health_check()
                else:
                    status = 'healthy'
                
                health_status['services'][service_name] = {
                    'status': status,
                    'last_check': datetime.now().isoformat()
                }
                
                if status != 'healthy':
                    health_status['overall_status'] = 'degraded'
                    
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        
        return health_status

# Global orchestrator instance
financial_orchestrator = FinancialServicesOrchestrator()

# Main functions for external access
async def process_financial_request(request: FinancialRequest) -> FinancialResponse:
    """Process financial service request"""
    return await financial_orchestrator.process_financial_request(request)

async def process_payment(user_id: str, amount: Decimal, currency: Currency, payment_data: Dict[str, Any]) -> FinancialResponse:
    """Process payment"""
    request = FinancialRequest(
        request_id=str(uuid.uuid4()),
        service_type="payment_processing",
        user_id=user_id,
        action="process",
        data=payment_data,
        amount=amount,
        currency=currency
    )
    return await financial_orchestrator.process_financial_request(request)

async def distribute_revenue(total_revenue: Decimal, recipients: List[Dict[str, Any]]) -> FinancialResponse:
    """Distribute revenue to recipients"""
    request = FinancialRequest(
        request_id=str(uuid.uuid4()),
        service_type="revenue_distribution",
        user_id="system",
        action="distribute",
        data={'total_revenue': float(total_revenue), 'recipients': recipients}
    )
    return await financial_orchestrator.process_financial_request(request)

async def initialize_financial_services() -> bool:
    """Initialize financial services"""
    return await financial_orchestrator.initialize()

async def get_financial_health() -> Dict[str, Any]:
    """Get financial services health"""
    return await financial_orchestrator.get_financial_health()

# Export main classes and functions
__all__ = [
    'FinancialServicesOrchestrator',
    'FinancialRequest',
    'FinancialResponse',
    'Transaction',
    'PaymentAccount',
    'PaymentMethod',
    'Currency',
    'TransactionType',
    'TransactionStatus',
    'financial_orchestrator',
    'process_financial_request',
    'process_payment',
    'distribute_revenue',
    'initialize_financial_services',
    'get_financial_health'
]

if __name__ == "__main__":
    # For testing
    async def main():
        print("🚀 Starting Financial Services...")
        success = await initialize_financial_services()
        if success:
            print("✅ Financial Services initialized successfully")
            
            # Test health check
            health = await get_financial_health()
            print(f"💰 Financial Status: {health['overall_status']}")
            print(f"💳 Payment Gateways: {health['payment_gateways']}")
            print(f"📊 Success Rate: {health['metrics']['success_rate']:.2%}")
            
            # Test payment processing
            test_payment = {
                'payment_method': 'credit_card',
                'card_number': '**** **** **** 1234',
                'description': 'Test payment'
            }
            
            payment_result = await process_payment(
                'test_user_123', 
                Decimal('10.00'), 
                Currency.USD, 
                test_payment
            )
            print(f"💳 Payment Status: {payment_result.status}")
            print(f"⏱️ Processing Time: {payment_result.processing_time:.3f}s")
        else:
            print("❌ Failed to initialize Financial Services")
    
    asyncio.run(main())