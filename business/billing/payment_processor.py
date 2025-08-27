"""
Payment Processor Engine - Multi-gateway payment processing system
===================================================================

Advanced payment processing with support for Stripe, PayPal, Wise and other
payment gateways, including fraud detection and automated reconciliation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTO = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class GatewayProvider(Enum):
    """Payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    SQUARE = "square"
    BRAINTREE = "braintree"

@dataclass
class PaymentData:
    """Payment transaction data"""
    payment_id: str
    invoice_id: str
    customer_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    gateway_provider: GatewayProvider
    status: PaymentStatus
    gateway_transaction_id: Optional[str]
    processed_at: Optional[datetime]
    fees: Decimal
    net_amount: Decimal
    metadata: Dict[str, Any]

@dataclass
class RefundData:
    """Refund transaction data"""
    refund_id: str
    payment_id: str
    amount: Decimal
    reason: str
    status: PaymentStatus
    processed_at: Optional[datetime]

class PaymentProcessorEngine:
    """
    Advanced payment processing system with multi-gateway support,
    fraud detection, and automated reconciliation for content creators.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.gateway_configs = {}
        
    async def initialize(self) -> None:
        """Initialize payment processor engine"""
        try:
            await self._setup_database_tables()
            await self._load_gateway_configurations()
            await self._initialize_fraud_detection()
            logger.info("Payment Processor Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Payment Processor Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for payment processing"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    payment_id VARCHAR(100) UNIQUE NOT NULL,
                    invoice_id VARCHAR(100),
                    customer_id VARCHAR(255) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    gateway_provider VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    gateway_transaction_id VARCHAR(255),
                    fees DECIMAL(15,2) DEFAULT 0,
                    net_amount DECIMAL(15,2) NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    processed_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_payments_customer (customer_id, status),
                    INDEX idx_payments_gateway (gateway_provider, gateway_transaction_id),
                    INDEX idx_payments_status (status, created_at)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_refunds (
                    id SERIAL PRIMARY KEY,
                    refund_id VARCHAR(100) UNIQUE NOT NULL,
                    payment_id VARCHAR(100) REFERENCES payments(payment_id),
                    amount DECIMAL(15,2) NOT NULL,
                    reason TEXT,
                    status VARCHAR(20) NOT NULL,
                    gateway_refund_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    processed_at TIMESTAMP
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_disputes (
                    id SERIAL PRIMARY KEY,
                    dispute_id VARCHAR(100) UNIQUE NOT NULL,
                    payment_id VARCHAR(100) REFERENCES payments(payment_id),
                    dispute_reason TEXT,
                    amount DECIMAL(15,2) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    evidence_due_date DATE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    resolved_at TIMESTAMP
                );
            """)

    async def _load_gateway_configurations(self) -> None:
        """Load payment gateway configurations"""
        try:
            # In production, these would come from secure environment variables
            self.gateway_configs = {
                GatewayProvider.STRIPE: {
                    'api_key': 'sk_test_...',
                    'webhook_secret': 'whsec_...',
                    'fee_rate': 0.029,  # 2.9% + 30¢
                    'fixed_fee': 0.30
                },
                GatewayProvider.PAYPAL: {
                    'client_id': 'paypal_client_id',
                    'client_secret': 'paypal_secret',
                    'fee_rate': 0.0349,  # 3.49% for standard transactions
                    'fixed_fee': 0.49
                },
                GatewayProvider.WISE: {
                    'api_key': 'wise_api_key',
                    'fee_rate': 0.0045,  # 0.45% typical rate
                    'fixed_fee': 0.50
                }
            }
            
            logger.info("Payment gateway configurations loaded")
        except Exception as e:
            logger.error(f"Failed to load gateway configurations: {e}")

    async def _initialize_fraud_detection(self) -> None:
        """Initialize fraud detection system"""
        try:
            # Load fraud detection rules and patterns
            fraud_rules = {
                'max_transaction_amount': 10000.00,
                'max_daily_amount': 50000.00,
                'suspicious_countries': ['NG', 'GH', 'PK'],
                'velocity_checks': True,
                'ip_geolocation_check': True
            }
            
            # Cache fraud rules
            self.redis.hmset("fraud_detection_rules", fraud_rules)
            
        except Exception as e:
            logger.error(f"Failed to initialize fraud detection: {e}")

    async def process_payment(self, invoice_id: str, payment_method: PaymentMethod,
                            gateway_provider: GatewayProvider, 
                            payment_data: Dict[str, Any]) -> PaymentData:
        """Process payment transaction"""
        try:
            # Get invoice details
            invoice = await self._get_invoice_details(invoice_id)
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            # Generate payment ID
            payment_id = f"pay_{invoice['customer_id']}_{int(datetime.now().timestamp())}"
            
            # Fraud detection check
            fraud_score = await self._check_fraud_risk(invoice, payment_data)
            if fraud_score > 0.8:
                raise HTTPException(status_code=403, detail="Transaction blocked due to fraud risk")
            
            # Calculate fees
            fees, net_amount = self._calculate_payment_fees(
                Decimal(str(invoice['total_amount'])), 
                gateway_provider
            )
            
            # Create payment record
            payment = PaymentData(
                payment_id=payment_id,
                invoice_id=invoice_id,
                customer_id=invoice['customer_id'],
                amount=Decimal(str(invoice['total_amount'])),
                currency=invoice['currency'],
                payment_method=payment_method,
                gateway_provider=gateway_provider,
                status=PaymentStatus.PENDING,
                gateway_transaction_id=None,
                processed_at=None,
                fees=fees,
                net_amount=net_amount,
                metadata=payment_data
            )
            
            # Store payment record
            await self._store_payment(payment)
            
            # Process with appropriate gateway
            gateway_response = await self._process_with_gateway(payment, payment_data)
            
            # Update payment with gateway response
            payment.gateway_transaction_id = gateway_response.get('transaction_id')
            payment.status = PaymentStatus(gateway_response.get('status', 'processing'))
            
            if payment.status == PaymentStatus.COMPLETED:
                payment.processed_at = datetime.now()
                # Update invoice status
                await self._update_invoice_payment_status(invoice_id, 'paid')
            
            # Update payment record
            await self._update_payment_status(payment)
            
            # Send notifications
            await self._send_payment_notifications(payment)
            
            return payment
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            raise HTTPException(status_code=500, detail="Payment processing failed")

    async def _get_invoice_details(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice details for payment processing"""
        try:
            async with self.db_pool.acquire() as conn:
                invoice = await conn.fetchrow("""
                    SELECT invoice_id, customer_id, total_amount, currency, status
                    FROM invoices 
                    WHERE invoice_id = $1
                """, invoice_id)
                
                return dict(invoice) if invoice else None
                
        except Exception as e:
            logger.error(f"Failed to get invoice details: {e}")
            return None

    async def _check_fraud_risk(self, invoice: Dict[str, Any], payment_data: Dict[str, Any]) -> float:
        """Check fraud risk score for transaction"""
        try:
            risk_score = 0.0
            
            # Amount-based risk
            amount = float(invoice['total_amount'])
            if amount > 10000:
                risk_score += 0.3
            elif amount > 5000:
                risk_score += 0.2
            elif amount > 1000:
                risk_score += 0.1
            
            # Customer history check
            customer_history = await self._get_customer_payment_history(invoice['customer_id'])
            if customer_history['failed_payments'] > 3:
                risk_score += 0.3
            
            # Velocity checks
            recent_payments = await self._get_recent_payments(invoice['customer_id'], hours=24)
            if len(recent_payments) > 5:
                risk_score += 0.4
            
            # IP and geolocation checks
            ip_address = payment_data.get('ip_address')
            if ip_address:
                ip_risk = await self._check_ip_reputation(ip_address)
                risk_score += ip_risk
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to check fraud risk: {e}")
            return 0.0

    def _calculate_payment_fees(self, amount: Decimal, gateway: GatewayProvider) -> tuple[Decimal, Decimal]:
        """Calculate payment processing fees"""
        try:
            config = self.gateway_configs.get(gateway, {})
            fee_rate = Decimal(str(config.get('fee_rate', 0.029)))
            fixed_fee = Decimal(str(config.get('fixed_fee', 0.30)))
            
            fees = (amount * fee_rate) + fixed_fee
            net_amount = amount - fees
            
            return fees, net_amount
            
        except Exception as e:
            logger.error(f"Failed to calculate payment fees: {e}")
            return Decimal('0.00'), amount

    async def _process_with_gateway(self, payment: PaymentData, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with specific gateway"""
        try:
            if payment.gateway_provider == GatewayProvider.STRIPE:
                return await self._process_stripe_payment(payment, payment_data)
            elif payment.gateway_provider == GatewayProvider.PAYPAL:
                return await self._process_paypal_payment(payment, payment_data)
            elif payment.gateway_provider == GatewayProvider.WISE:
                return await self._process_wise_payment(payment, payment_data)
            else:
                return await self._process_generic_payment(payment, payment_data)
                
        except Exception as e:
            logger.error(f"Failed to process with gateway: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def _process_stripe_payment(self, payment: PaymentData, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment via Stripe"""
        try:
            # Simulate Stripe API call
            # In production, this would use the actual Stripe SDK
            
            # Mock successful payment
            transaction_id = f"stripe_{int(datetime.now().timestamp())}"
            
            return {
                'status': 'completed',
                'transaction_id': transaction_id,
                'gateway_fees': float(payment.fees),
                'currency': payment.currency
            }
            
        except Exception as e:
            logger.error(f"Stripe payment processing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def _process_paypal_payment(self, payment: PaymentData, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment via PayPal"""
        try:
            # Simulate PayPal API call
            transaction_id = f"paypal_{int(datetime.now().timestamp())}"
            
            return {
                'status': 'completed',
                'transaction_id': transaction_id,
                'gateway_fees': float(payment.fees),
                'currency': payment.currency
            }
            
        except Exception as e:
            logger.error(f"PayPal payment processing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def _process_wise_payment(self, payment: PaymentData, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment via Wise"""
        try:
            # Simulate Wise API call
            transaction_id = f"wise_{int(datetime.now().timestamp())}"
            
            return {
                'status': 'completed',
                'transaction_id': transaction_id,
                'gateway_fees': float(payment.fees),
                'currency': payment.currency
            }
            
        except Exception as e:
            logger.error(f"Wise payment processing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def _process_generic_payment(self, payment: PaymentData, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with generic gateway"""
        try:
            transaction_id = f"generic_{int(datetime.now().timestamp())}"
            
            return {
                'status': 'completed',
                'transaction_id': transaction_id,
                'gateway_fees': float(payment.fees),
                'currency': payment.currency
            }
            
        except Exception as e:
            logger.error(f"Generic payment processing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def _store_payment(self, payment: PaymentData) -> None:
        """Store payment record in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO payments 
                    (payment_id, invoice_id, customer_id, amount, currency,
                     payment_method, gateway_provider, status, fees, net_amount, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                payment.payment_id,
                payment.invoice_id,
                payment.customer_id,
                payment.amount,
                payment.currency,
                payment.payment_method.value,
                payment.gateway_provider.value,
                payment.status.value,
                payment.fees,
                payment.net_amount,
                payment.metadata
                )
        except Exception as e:
            logger.error(f"Failed to store payment: {e}")

    async def _update_payment_status(self, payment: PaymentData) -> None:
        """Update payment status in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE payments 
                    SET status = $1, gateway_transaction_id = $2, 
                        processed_at = $3, updated_at = NOW()
                    WHERE payment_id = $4
                """,
                payment.status.value,
                payment.gateway_transaction_id,
                payment.processed_at,
                payment.payment_id
                )
        except Exception as e:
            logger.error(f"Failed to update payment status: {e}")

    async def _update_invoice_payment_status(self, invoice_id: str, status: str) -> None:
        """Update invoice payment status"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE invoices 
                    SET status = $1, updated_at = NOW()
                    WHERE invoice_id = $2
                """, status, invoice_id)
        except Exception as e:
            logger.error(f"Failed to update invoice status: {e}")

    async def _send_payment_notifications(self, payment: PaymentData) -> None:
        """Send payment notifications"""
        try:
            notification_data = {
                'payment_id': payment.payment_id,
                'customer_id': payment.customer_id,
                'amount': float(payment.amount),
                'status': payment.status.value,
                'type': 'payment_processed'
            }
            
            self.redis.lpush("payment_notifications", str(notification_data))
            
        except Exception as e:
            logger.error(f"Failed to send payment notifications: {e}")

    async def _get_customer_payment_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer payment history for fraud detection"""
        try:
            async with self.db_pool.acquire() as conn:
                history = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_payments,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_payments,
                        COUNT(CASE WHEN status = 'disputed' THEN 1 END) as disputed_payments,
                        AVG(amount) as avg_amount
                    FROM payments 
                    WHERE customer_id = $1
                    AND created_at >= NOW() - INTERVAL '6 months'
                """, customer_id)
                
                return dict(history) if history else {
                    'total_payments': 0,
                    'failed_payments': 0,
                    'disputed_payments': 0,
                    'avg_amount': 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get customer payment history: {e}")
            return {}

    async def _get_recent_payments(self, customer_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent payments for velocity checks"""
        try:
            async with self.db_pool.acquire() as conn:
                payments = await conn.fetch("""
                    SELECT payment_id, amount, created_at
                    FROM payments 
                    WHERE customer_id = $1
                    AND created_at >= NOW() - INTERVAL '%s hours'
                    ORDER BY created_at DESC
                """, customer_id, hours)
                
                return [dict(payment) for payment in payments]
                
        except Exception as e:
            logger.error(f"Failed to get recent payments: {e}")
            return []

    async def _check_ip_reputation(self, ip_address: str) -> float:
        """Check IP address reputation for fraud detection"""
        try:
            # This would integrate with IP reputation services
            # For now, return a mock score
            
            # Check if IP is in known bad list
            bad_ips = self.redis.smembers("bad_ip_addresses")
            if ip_address.encode() in bad_ips:
                return 0.8
            
            # Check country reputation
            # This would use actual geolocation service
            return 0.1  # Low risk by default
            
        except Exception as e:
            logger.error(f"Failed to check IP reputation: {e}")
            return 0.0

    async def process_refund(self, payment_id: str, amount: Optional[Decimal] = None, 
                           reason: str = "Customer request") -> RefundData:
        """Process payment refund"""
        try:
            # Get original payment
            payment = await self._get_payment_by_id(payment_id)
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")
            
            refund_amount = amount or payment['amount']
            refund_id = f"ref_{payment_id}_{int(datetime.now().timestamp())}"
            
            # Create refund record
            refund = RefundData(
                refund_id=refund_id,
                payment_id=payment_id,
                amount=refund_amount,
                reason=reason,
                status=PaymentStatus.PROCESSING,
                processed_at=None
            )
            
            # Store refund record
            await self._store_refund(refund)
            
            # Process refund with gateway
            gateway_response = await self._process_gateway_refund(payment, refund)
            
            # Update refund status
            refund.status = PaymentStatus(gateway_response.get('status', 'completed'))
            refund.processed_at = datetime.now()
            
            await self._update_refund_status(refund)
            
            return refund
            
        except Exception as e:
            logger.error(f"Failed to process refund: {e}")
            raise HTTPException(status_code=500, detail="Refund processing failed")

    async def _get_payment_by_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        try:
            async with self.db_pool.acquire() as conn:
                payment = await conn.fetchrow("""
                    SELECT * FROM payments WHERE payment_id = $1
                """, payment_id)
                
                return dict(payment) if payment else None
                
        except Exception as e:
            logger.error(f"Failed to get payment: {e}")
            return None

    async def _store_refund(self, refund: RefundData) -> None:
        """Store refund record in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO payment_refunds 
                    (refund_id, payment_id, amount, reason, status)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                refund.refund_id,
                refund.payment_id,
                refund.amount,
                refund.reason,
                refund.status.value
                )
        except Exception as e:
            logger.error(f"Failed to store refund: {e}")

    async def _update_refund_status(self, refund: RefundData) -> None:
        """Update refund status in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE payment_refunds 
                    SET status = $1, processed_at = $2
                    WHERE refund_id = $3
                """,
                refund.status.value,
                refund.processed_at,
                refund.refund_id
                )
        except Exception as e:
            logger.error(f"Failed to update refund status: {e}")

    async def _process_gateway_refund(self, payment: Dict[str, Any], refund: RefundData) -> Dict[str, Any]:
        """Process refund with payment gateway"""
        try:
            gateway = GatewayProvider(payment['gateway_provider'])
            
            # This would call the actual gateway refund API
            return {
                'status': 'completed',
                'refund_id': f"{gateway.value}_{refund.refund_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to process gateway refund: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def get_payment_dashboard_data(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive payment dashboard data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Payment summary
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_payments,
                        COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as successful_amount,
                        COALESCE(SUM(CASE WHEN status = 'failed' THEN amount ELSE 0 END), 0) as failed_amount,
                        COALESCE(SUM(fees), 0) as total_fees
                    FROM payments 
                    WHERE customer_id = $1
                    AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                """, customer_id)
                
                # Recent payments
                recent_payments = await conn.fetch("""
                    SELECT payment_id, amount, status, payment_method, created_at
                    FROM payments 
                    WHERE customer_id = $1
                    ORDER BY created_at DESC 
                    LIMIT 10
                """, customer_id)
                
                return {
                    'customer_id': customer_id,
                    'summary': {
                        'total_payments': int(summary['total_payments']) if summary else 0,
                        'successful_amount': float(summary['successful_amount']) if summary else 0,
                        'failed_amount': float(summary['failed_amount']) if summary else 0,
                        'total_fees': float(summary['total_fees']) if summary else 0
                    },
                    'recent_payments': [
                        {
                            'payment_id': pay['payment_id'],
                            'amount': float(pay['amount']),
                            'status': pay['status'],
                            'payment_method': pay['payment_method'],
                            'created_at': pay['created_at'].isoformat()
                        }
                        for pay in recent_payments
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get payment dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Payment dashboard data retrieval failed")
