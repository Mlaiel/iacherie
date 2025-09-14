"""
Ainflue Platform - Payment Gateway Monitor
==========================================

Enterprise-grade payment gateway monitoring for multi-gateway processing,
intelligent routing, and payment performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import time
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from prometheus_client import Counter, Histogram, Gauge
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

# Metrics
gateway_transactions_total = Counter('ainflue_gateway_transactions_total',
                                    'Total payment gateway transactions', ['gateway', 'status', 'currency'])
gateway_response_time = Histogram('ainflue_gateway_response_time_seconds',
                                'Payment gateway response time', ['gateway'])
gateway_success_rate = Gauge('ainflue_gateway_success_rate',
                           'Payment gateway success rate', ['gateway'])
gateway_health_score = Gauge('ainflue_gateway_health_score',
                           'Payment gateway health score', ['gateway'])

class PaymentGateway(Enum):
    """Supported payment gateways."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    BRAINTREE = "braintree"
    RAZORPAY = "razorpay"
    KLARNA = "klarna"
    WORLDPAY = "worldpay"

class TransactionStatus(Enum):
    """Payment transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class Currency(Enum):
    """Supported currencies."""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    JPY = "jpy"
    CAD = "cad"
    AUD = "aud"
    CHF = "chf"
    CNY = "cny"

class PaymentMethod(Enum):
    """Payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BUY_NOW_PAY_LATER = "buy_now_pay_later"

@dataclass
class GatewayConfig:
    """Payment gateway configuration."""
    gateway: PaymentGateway
    api_key: str
    api_secret: str
    webhook_secret: str
    base_url: str
    supported_currencies: List[Currency]
    supported_methods: List[PaymentMethod]
    fee_percentage: float
    fixed_fee: float
    max_amount: float
    min_amount: float
    enabled: bool

@dataclass
class TransactionRecord:
    """Payment transaction record."""
    transaction_id: str
    gateway: PaymentGateway
    gateway_transaction_id: str
    amount: float
    currency: Currency
    payment_method: PaymentMethod
    status: TransactionStatus
    customer_id: str
    merchant_id: str
    description: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    gateway_response: Dict[str, Any]
    fees: Dict[str, float]
    risk_score: float

@dataclass
class GatewayHealthMetrics:
    """Gateway health metrics."""
    gateway: PaymentGateway
    uptime_percentage: float
    success_rate: float
    average_response_time: float
    error_rate: float
    transaction_volume: int
    total_amount: float
    last_check: datetime
    alerts: List[str]

class PaymentGatewayMonitor:
    """Enterprise payment gateway monitoring system."""
    
    def __init__(self) -> None:
        self.gateway_configs = {}
        self.transaction_history = {}
        self.health_metrics = {}
        self.routing_rules = {}
        self.monitoring_active = {}
        self.session_pool = {}
        
    async def initialize_gateways(self, configs -> None: Dict[PaymentGateway, GatewayConfig]) -> None:
        """Initialize payment gateway configurations."""
        
        for gateway, config in configs.items():
            try:
                # Store configuration
                self.gateway_configs[gateway] = config
                
                # Initialize HTTP session
                session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={'User-Agent': 'Ainflue-Monitor/1.0'}
                )
                self.session_pool[gateway] = session
                
                # Initialize health metrics
                self.health_metrics[gateway] = GatewayHealthMetrics(
                    gateway=gateway,
                    uptime_percentage=100.0,
                    success_rate=100.0,
                    average_response_time=0.0,
                    error_rate=0.0,
                    transaction_volume=0,
                    total_amount=0.0,
                    last_check=datetime.now(),
                    alerts=[]
                )
                
                # Start monitoring
                self.monitoring_active[gateway] = True
                asyncio.create_task(self._monitor_gateway_health(gateway))
                
                logger.info(f"Initialized payment gateway: {gateway.value}")
                
            except Exception as e:
                logger.error(f"Failed to initialize gateway {gateway.value}: {str(e)}")
    
    async def _monitor_gateway_health(self, gateway -> None: PaymentGateway) -> None:
        """Monitor individual gateway health."""
        
        while self.monitoring_active.get(gateway, False):
            try:
                # Perform health check
                health_result = await self._perform_health_check(gateway)
                
                # Update metrics
                await self._update_health_metrics(gateway, health_result)
                
                # Check for alerts
                await self._check_gateway_alerts(gateway)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Gateway health monitoring error for {gateway.value}: {str(e)}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self, gateway: PaymentGateway) -> Dict[str, Any]:
        """Perform health check on payment gateway."""
        
        start_time = time.time()
        config = self.gateway_configs[gateway]
        session = self.session_pool[gateway]
        
        try:
            # Gateway-specific health check endpoint
            health_url = self._get_health_check_url(gateway, config)
            headers = self._get_auth_headers(gateway, config)
            
            async with session.get(health_url, headers=headers) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    
                    return {
                        'status': 'healthy',
                        'response_time': response_time,
                        'gateway_status': response_data.get('status', 'unknown'),
                        'timestamp': datetime.now(),
                        'details': response_data
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'response_time': response_time,
                        'error_code': response.status,
                        'timestamp': datetime.now(),
                        'details': {'http_status': response.status}
                    }
                    
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'response_time': time.time() - start_time,
                'error': 'Request timeout',
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': time.time() - start_time,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _get_health_check_url(self, gateway: PaymentGateway, config: GatewayConfig) -> str:
        """Get health check URL for gateway."""
        
        base_urls = {
            PaymentGateway.STRIPE: "https://api.stripe.com/v1/account",
            PaymentGateway.PAYPAL: "https://api.paypal.com/v1/oauth2/token",
            PaymentGateway.SQUARE: "https://connect.squareup.com/v2/locations",
            PaymentGateway.ADYEN: "https://checkout-test.adyen.com/v69/payments",
            PaymentGateway.BRAINTREE: "https://api.sandbox.braintreegateway.com/merchants",
            PaymentGateway.RAZORPAY: "https://api.razorpay.com/v1/payments",
            PaymentGateway.KLARNA: "https://api.klarna.com/payments/v1/sessions",
            PaymentGateway.WORLDPAY: "https://api.worldpay.com/v1/payments"
        }
        
        return base_urls.get(gateway, config.base_url)
    
    def _get_auth_headers(self, gateway: PaymentGateway, config: GatewayConfig) -> Dict[str, str]:
        """Get authentication headers for gateway."""
        
        if gateway == PaymentGateway.STRIPE:
            return {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }
        elif gateway == PaymentGateway.PAYPAL:
            return {
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            }
        elif gateway == PaymentGateway.SQUARE:
            return {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }
        else:
            return {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }
    
    async def _update_health_metrics(self, gateway -> None: PaymentGateway, health_result -> None: Dict[str, Any]) -> None:
        """Update gateway health metrics."""
        
        metrics = self.health_metrics[gateway]
        
        # Update response time
        response_time = health_result.get('response_time', 0)
        if metrics.average_response_time == 0:
            metrics.average_response_time = response_time
        else:
            # Exponential moving average
            metrics.average_response_time = (metrics.average_response_time * 0.8) + (response_time * 0.2)
        
        # Update success rate
        if health_result['status'] == 'healthy':
            metrics.success_rate = min(100.0, metrics.success_rate + 0.1)
            metrics.error_rate = max(0.0, metrics.error_rate - 0.1)
        else:
            metrics.success_rate = max(0.0, metrics.success_rate - 1.0)
            metrics.error_rate = min(100.0, metrics.error_rate + 1.0)
        
        # Update uptime
        if health_result['status'] == 'healthy':
            metrics.uptime_percentage = min(100.0, metrics.uptime_percentage + 0.01)
        else:
            metrics.uptime_percentage = max(0.0, metrics.uptime_percentage - 0.1)
        
        metrics.last_check = datetime.now()
        
        # Update Prometheus metrics
        gateway_response_time.labels(gateway=gateway.value).observe(response_time)
        gateway_success_rate.labels(gateway=gateway.value).set(metrics.success_rate)
        gateway_health_score.labels(gateway=gateway.value).set(
            (metrics.uptime_percentage + metrics.success_rate) / 2
        )
    
    async def _check_gateway_alerts(self, gateway -> None: PaymentGateway) -> None:
        """Check for gateway alerts and issues."""
        
        metrics = self.health_metrics[gateway]
        alerts = []
        
        # Check success rate
        if metrics.success_rate < 95.0:
            alerts.append(f"Low success rate: {metrics.success_rate:.1f}%")
        
        # Check response time
        if metrics.average_response_time > 5.0:
            alerts.append(f"High response time: {metrics.average_response_time:.2f}s")
        
        # Check uptime
        if metrics.uptime_percentage < 99.0:
            alerts.append(f"Low uptime: {metrics.uptime_percentage:.1f}%")
        
        # Check error rate
        if metrics.error_rate > 5.0:
            alerts.append(f"High error rate: {metrics.error_rate:.1f}%")
        
        metrics.alerts = alerts
        
        # Log critical alerts
        if alerts:
            logger.warning(f"Gateway {gateway.value} alerts: {', '.join(alerts)}")
    
    async def process_transaction(self, amount: float, currency: Currency,
                                payment_method: PaymentMethod, customer_id: str,
                                merchant_id: str, description: str,
                                metadata: Optional[Dict[str, Any]] = None) -> TransactionRecord:
        """Process payment transaction through optimal gateway."""
        
        try:
            # Select optimal gateway
            selected_gateway = await self._select_optimal_gateway(
                amount, currency, payment_method
            )
            
            # Generate transaction ID
            transaction_id = f"tx_{int(time.time())}_{hashlib.md5(f'{customer_id}{amount}'.encode()).hexdigest()[:8]}"
            
            # Process transaction
            gateway_response = await self._process_gateway_transaction(
                selected_gateway, transaction_id, amount, currency,
                payment_method, customer_id, description, metadata or {}
            )
            
            # Calculate fees
            fees = await self._calculate_transaction_fees(selected_gateway, amount, currency)
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(
                customer_id, amount, currency, payment_method
            )
            
            # Create transaction record
            transaction = TransactionRecord(
                transaction_id=transaction_id,
                gateway=selected_gateway,
                gateway_transaction_id=gateway_response.get('gateway_id', ''),
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                status=self._parse_gateway_status(gateway_response.get('status')),
                customer_id=customer_id,
                merchant_id=merchant_id,
                description=description,
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                completed_at=datetime.now() if gateway_response.get('completed') else None,
                gateway_response=gateway_response,
                fees=fees,
                risk_score=risk_score
            )
            
            # Store transaction
            self.transaction_history[transaction_id] = transaction
            
            # Update metrics
            gateway_transactions_total.labels(
                gateway=selected_gateway.value,
                status=transaction.status.value,
                currency=currency.value
            ).inc()
            
            # Update gateway health metrics
            if selected_gateway in self.health_metrics:
                self.health_metrics[selected_gateway].transaction_volume += 1
                self.health_metrics[selected_gateway].total_amount += amount
            
            logger.info(f"Transaction processed: {transaction_id} via {selected_gateway.value} - {transaction.status.value}")
            return transaction
            
        except Exception as e:
            logger.error(f"Transaction processing failed: {str(e)}")
            raise
    
    async def _select_optimal_gateway(self, amount: float, currency: Currency,
                                    payment_method: PaymentMethod) -> PaymentGateway:
        """Select optimal payment gateway based on multiple factors."""
        
        # Get available gateways
        available_gateways = [
            gateway for gateway, config in self.gateway_configs.items()
            if (config.enabled and 
                currency in config.supported_currencies and
                payment_method in config.supported_methods and
                config.min_amount <= amount <= config.max_amount)
        ]
        
        if not available_gateways:
            raise ValueError("No suitable payment gateway available")
        
        # Score gateways based on multiple factors
        gateway_scores = {}
        
        for gateway in available_gateways:
            score = 0.0
            config = self.gateway_configs[gateway]
            metrics = self.health_metrics.get(gateway)
            
            # Health score (40% weight)
            if metrics:
                health_score = (metrics.uptime_percentage + metrics.success_rate) / 2
                score += health_score * 0.4
            
            # Cost score (30% weight) - lower fees = higher score
            total_fee_rate = config.fee_percentage + (config.fixed_fee / amount * 100)
            cost_score = max(0, 100 - total_fee_rate * 10)
            score += cost_score * 0.3
            
            # Response time score (20% weight)
            if metrics and metrics.average_response_time > 0:
                response_score = max(0, 100 - metrics.average_response_time * 20)
                score += response_score * 0.2
            
            # Currency preference (10% weight)
            currency_score = 100 if currency == Currency.USD else 80
            score += currency_score * 0.1
            
            gateway_scores[gateway] = score
        
        # Select gateway with highest score
        selected_gateway = max(gateway_scores, key=gateway_scores.get)
        
        logger.debug(f"Gateway selection scores: {gateway_scores}")
        logger.info(f"Selected gateway: {selected_gateway.value} (score: {gateway_scores[selected_gateway]:.1f})")
        
        return selected_gateway
    
    async def _process_gateway_transaction(self, gateway: PaymentGateway,
                                         transaction_id: str, amount: float,
                                         currency: Currency, payment_method: PaymentMethod,
                                         customer_id: str, description: str,
                                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process transaction with specific gateway."""
        
        config = self.gateway_configs[gateway]
        session = self.session_pool[gateway]
        
        # Prepare gateway-specific payload
        payload = await self._prepare_gateway_payload(
            gateway, transaction_id, amount, currency, payment_method,
            customer_id, description, metadata
        )
        
        # Get gateway API endpoint
        api_url = await self._get_transaction_endpoint(gateway, config)
        headers = self._get_auth_headers(gateway, config)
        
        try:
            async with session.post(api_url, json=payload, headers=headers) as response:
                response_data = await response.json()
                
                if response.status in [200, 201]:
                    return {
                        'success': True,
                        'gateway_id': response_data.get('id', transaction_id),
                        'status': response_data.get('status', 'pending'),
                        'completed': response_data.get('status') == 'succeeded',
                        'response': response_data
                    }
                else:
                    return {
                        'success': False,
                        'error': response_data.get('error', 'Unknown error'),
                        'status': 'failed',
                        'response': response_data
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    async def _prepare_gateway_payload(self, gateway: PaymentGateway,
                                     transaction_id: str, amount: float,
                                     currency: Currency, payment_method: PaymentMethod,
                                     customer_id: str, description: str,
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare gateway-specific transaction payload."""
        
        base_payload = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency.value,
            'description': description,
            'metadata': {
                **metadata,
                'transaction_id': transaction_id,
                'customer_id': customer_id
            }
        }
        
        if gateway == PaymentGateway.STRIPE:
            return {
                **base_payload,
                'payment_method_types': ['card'],
                'capture_method': 'automatic'
            }
        elif gateway == PaymentGateway.PAYPAL:
            return {
                'intent': 'sale',
                'payer': {'payment_method': 'paypal'},
                'transactions': [{
                    'amount': {
                        'total': str(amount),
                        'currency': currency.value.upper()
                    },
                    'description': description
                }]
            }
        elif gateway == PaymentGateway.SQUARE:
            return {
                'amount_money': {
                    'amount': int(amount * 100),
                    'currency': currency.value.upper()
                },
                'idempotency_key': transaction_id,
                'source_id': 'CARD_ON_FILE'  # Would be actual source
            }
        else:
            return base_payload
    
    async def _get_transaction_endpoint(self, gateway: PaymentGateway,
                                      config: GatewayConfig) -> str:
        """Get transaction processing endpoint for gateway."""
        
        endpoints = {
            PaymentGateway.STRIPE: "https://api.stripe.com/v1/payment_intents",
            PaymentGateway.PAYPAL: "https://api.paypal.com/v1/payments/payment",
            PaymentGateway.SQUARE: "https://connect.squareup.com/v2/payments",
            PaymentGateway.ADYEN: "https://checkout-test.adyen.com/v69/payments",
            PaymentGateway.BRAINTREE: "https://api.sandbox.braintreegateway.com/merchants/transactions",
            PaymentGateway.RAZORPAY: "https://api.razorpay.com/v1/payments",
            PaymentGateway.KLARNA: "https://api.klarna.com/payments/v1/authorizations",
            PaymentGateway.WORLDPAY: "https://api.worldpay.com/v1/payments"
        }
        
        return endpoints.get(gateway, f"{config.base_url}/payments")
    
    def _parse_gateway_status(self, gateway_status: str) -> TransactionStatus:
        """Parse gateway-specific status to standard status."""
        
        status_mapping = {
            'succeeded': TransactionStatus.COMPLETED,
            'pending': TransactionStatus.PENDING,
            'processing': TransactionStatus.PROCESSING,
            'failed': TransactionStatus.FAILED,
            'declined': TransactionStatus.DECLINED,
            'canceled': TransactionStatus.CANCELLED,
            'cancelled': TransactionStatus.CANCELLED,
            'refunded': TransactionStatus.REFUNDED,
            'disputed': TransactionStatus.DISPUTED
        }
        
        return status_mapping.get(gateway_status.lower() if gateway_status else '', TransactionStatus.FAILED)
    
    async def _calculate_transaction_fees(self, gateway: PaymentGateway,
                                        amount: float, currency: Currency) -> Dict[str, float]:
        """Calculate transaction fees for gateway."""
        
        config = self.gateway_configs[gateway]
        
        percentage_fee = amount * (config.fee_percentage / 100)
        fixed_fee = config.fixed_fee
        total_fee = percentage_fee + fixed_fee
        
        return {
            'percentage_fee': percentage_fee,
            'fixed_fee': fixed_fee,
            'total_fee': total_fee,
            'fee_percentage': config.fee_percentage,
            'net_amount': amount - total_fee
        }
    
    async def _calculate_risk_score(self, customer_id: str, amount: float,
                                  currency: Currency, payment_method: PaymentMethod) -> float:
        """Calculate transaction risk score."""
        
        risk_score = 0.0
        
        # Amount-based risk
        if amount > 1000:
            risk_score += 0.2
        elif amount > 10000:
            risk_score += 0.5
        
        # Payment method risk
        if payment_method == PaymentMethod.CRYPTOCURRENCY:
            risk_score += 0.3
        elif payment_method == PaymentMethod.BUY_NOW_PAY_LATER:
            risk_score += 0.2
        
        # Currency risk
        if currency not in [Currency.USD, Currency.EUR, Currency.GBP]:
            risk_score += 0.1
        
        # Customer history (simplified)
        customer_transactions = [
            tx for tx in self.transaction_history.values()
            if tx.customer_id == customer_id
        ]
        
        if len(customer_transactions) == 0:
            risk_score += 0.2  # New customer risk
        elif len(customer_transactions) > 100:
            risk_score -= 0.1  # Loyal customer bonus
        
        # Failed transaction history
        failed_transactions = [
            tx for tx in customer_transactions
            if tx.status in [TransactionStatus.FAILED, TransactionStatus.DECLINED]
        ]
        
        if len(customer_transactions) > 0:
            failure_rate = len(failed_transactions) / len(customer_transactions)
            risk_score += failure_rate * 0.3
        
        return min(1.0, max(0.0, risk_score))
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[TransactionRecord]:
        """Get transaction status and details."""
        
        return self.transaction_history.get(transaction_id)
    
    async def refund_transaction(self, transaction_id: str, amount: Optional[float] = None,
                               reason: str = "") -> Dict[str, Any]:
        """Process transaction refund."""
        
        transaction = self.transaction_history.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        if transaction.status != TransactionStatus.COMPLETED:
            raise ValueError(f"Cannot refund transaction with status: {transaction.status.value}")
        
        refund_amount = amount or transaction.amount
        if refund_amount > transaction.amount:
            raise ValueError("Refund amount cannot exceed original transaction amount")
        
        # Process refund with gateway
        refund_result = await self._process_gateway_refund(
            transaction.gateway, transaction.gateway_transaction_id, refund_amount, reason
        )
        
        if refund_result.get('success'):
            # Update transaction status
            if refund_amount == transaction.amount:
                transaction.status = TransactionStatus.REFUNDED
            else:
                # Partial refund - would need more complex status handling
                pass
            
            transaction.updated_at = datetime.now()
            
            logger.info(f"Refund processed: {transaction_id} - Amount: {refund_amount}")
        
        return refund_result
    
    async def _process_gateway_refund(self, gateway: PaymentGateway,
                                    gateway_transaction_id: str, amount: float,
                                    reason: str) -> Dict[str, Any]:
        """Process refund with specific gateway."""
        
        # Simplified refund processing
        # In real implementation, would call actual gateway APIs
        
        return {
            'success': True,
            'refund_id': f"ref_{int(time.time())}",
            'amount': amount,
            'status': 'succeeded',
            'reason': reason
        }
    
    def get_gateway_statistics(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics."""
        
        stats = {
            'total_transactions': len(self.transaction_history),
            'total_volume': sum(tx.amount for tx in self.transaction_history.values()),
            'gateway_health': {},
            'transaction_distribution': {},
            'currency_distribution': {},
            'payment_method_distribution': {},
            'status_distribution': {}
        }
        
        # Gateway health metrics
        for gateway, metrics in self.health_metrics.items():
            stats['gateway_health'][gateway.value] = {
                'uptime_percentage': metrics.uptime_percentage,
                'success_rate': metrics.success_rate,
                'average_response_time': metrics.average_response_time,
                'transaction_volume': metrics.transaction_volume,
                'total_amount': metrics.total_amount,
                'alerts': metrics.alerts
            }
        
        # Transaction distributions
        for transaction in self.transaction_history.values():
            # Gateway distribution
            gateway_key = transaction.gateway.value
            stats['transaction_distribution'][gateway_key] = stats['transaction_distribution'].get(gateway_key, 0) + 1
            
            # Currency distribution
            currency_key = transaction.currency.value
            stats['currency_distribution'][currency_key] = stats['currency_distribution'].get(currency_key, 0) + 1
            
            # Payment method distribution
            method_key = transaction.payment_method.value
            stats['payment_method_distribution'][method_key] = stats['payment_method_distribution'].get(method_key, 0) + 1
            
            # Status distribution
            status_key = transaction.status.value
            stats['status_distribution'][status_key] = stats['status_distribution'].get(status_key, 0) + 1
        
        return stats

# Global payment gateway monitor instance
payment_gateway_monitor = PaymentGatewayMonitor()