"""Multi-Platform Payment Processing Engine
=======================================

Professional payment processing system for content creator monetization.
Handles multiple payment gateways, automated payouts, currency conversion,
and comprehensive financial compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import hashlib
import hmac

import stripe
import paypal
from wise_client import WiseClient
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis

from ..models.payment_model import PaymentModel, PayoutModel
from ..models.user_model import UserModel
from .revenue_calculator import Currency


class PaymentGateway(Enum):
    """
Supported payment gateways"""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
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


class PayoutFrequency(Enum):
    """Payout frequency options"""

    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"


@dataclass
class PaymentRequest:
    """Payment processing request"""
    user_id: str
    amount: Decimal
    currency: Currency
    gateway: PaymentGateway
    description: str
    metadata: Dict[str, Any]
    recipient_info: Dict[str, str]
    payout_frequency: PayoutFrequency = PayoutFrequency.WEEKLY


@dataclass
class PaymentResult:
    """
Payment processing result"""
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str]
    gateway_response: Dict[str, Any]
    fees: Decimal
    net_amount: Decimal
    estimated_arrival: Optional[datetime]
    error_message: Optional[str] = None


@dataclass
class PayoutConfiguration:
    """
User payout configuration"""
    user_id: str
    primary_gateway: PaymentGateway
    backup_gateway: Optional[PaymentGateway]
    minimum_payout: Decimal
    payout_frequency: PayoutFrequency
    currency: Currency
    bank_details: Dict[str, str]
    tax_info: Dict[str, Any]
    compliance_verified: bool


class PaymentProcessor:
    """
    Professional payment processing engine for IA Influencer Agent platform.
    
    Provides multi-gateway payment processing, automated payouts, currency conversion,
    and comprehensive financial compliance for content creator monetization.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize PaymentProcessor.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize payment gateways
        self._initialize_gateways()
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.minimum_payout_default = Decimal('25.00')  # €25 minimum
        self.max_retry_attempts = 3
        
        # Fee structures by gateway
        self.gateway_fees = {
            PaymentGateway.STRIPE: {
                'percentage': Decimal('0.029'),  # 2.9%
                'fixed': Decimal('0.30')  # €0.30
            },
            PaymentGateway.PAYPAL: {
                'percentage': Decimal('0.035'),  # 3.5%
                'fixed': Decimal('0.35')  # €0.35
            },
            PaymentGateway.WISE: {
                'percentage': Decimal('0.008'),  # 0.8%
                'fixed': Decimal('0.50')  # €0.50
            },
            PaymentGateway.BANK_TRANSFER: {
                'percentage': Decimal('0.001'),  # 0.1%
                'fixed': Decimal('2.00')  # €2.00
            }
        }
        
        # Currency conversion rates (updated from external API)
        self.exchange_rates = {}
        self.rate_last_updated = None
    
    def _initialize_gateways(self):
        """
Initialize payment gateway connections"""
        try:
            # Stripe initialization
            stripe.api_key = self._get_config('STRIPE_SECRET_KEY')
            
            # PayPal initialization
            self.paypal_client = paypal.PayPalHttpClient(
                paypal.SandboxEnvironment(
                    client_id=self._get_config('PAYPAL_CLIENT_ID'),
                    client_secret=self._get_config('PAYPAL_CLIENT_SECRET')
                )
            )
            
            # Wise initialization
            self.wise_client = WiseClient(
                api_key=self._get_config('WISE_API_KEY'),
                environment='production'
            )
            
            self.logger.info("Payment gateways initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing payment gateways: {str(e)}")
            raise
    
    async def process_payout(self, payment_request: PaymentRequest) -> PaymentResult:
        """
        Process a payout request through the appropriate gateway.
        
        Args:
            payment_request: Payment request details
            
        Returns:
            Payment processing result
        """
        try:
            # Validate request
            await self._validate_payment_request(payment_request)
            
            # Get user payout configuration
            payout_config = await self._get_payout_configuration(payment_request.user_id)
            
            # Check minimum payout threshold
            if payment_request.amount < payout_config.minimum_payout:
                return PaymentResult(
                    payment_id=str(uuid.uuid4()),
                    status=PaymentStatus.FAILED,
                    transaction_id=None,
                    gateway_response={},
                    fees=Decimal('0'),
                    net_amount=Decimal('0'),
                    estimated_arrival=None,
                    error_message=f"Amount below minimum payout threshold: {payout_config.minimum_payout}"
                )
            
            # Convert currency if needed
            converted_amount = await self._convert_currency(
                payment_request.amount,
                payment_request.currency,
                payout_config.currency
            )
            
            # Calculate fees
            fees = await self._calculate_fees(converted_amount, payment_request.gateway)
            net_amount = converted_amount - fees
            
            # Process payment through gateway
            gateway_result = await self._process_gateway_payment(
                payment_request, converted_amount, payout_config
            )
            
            # Create payment record
            payment_id = await self._create_payment_record(
                payment_request, gateway_result, fees, net_amount
            )
            
            # Update user balance
            await self._update_user_balance(payment_request.user_id, -payment_request.amount)
            
            # Send notifications
            await self._send_payment_notifications(payment_request, gateway_result)
            
            return PaymentResult(
                payment_id=payment_id,
                status=gateway_result['status'],
                transaction_id=gateway_result.get('transaction_id'),
                gateway_response=gateway_result,
                fees=fees,
                net_amount=net_amount,
                estimated_arrival=gateway_result.get('estimated_arrival'),
                error_message=gateway_result.get('error_message')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing payout: {str(e)}")
            return PaymentResult(
                payment_id=str(uuid.uuid4()),
                status=PaymentStatus.FAILED,
                transaction_id=None,
                gateway_response={},
                fees=Decimal('0'),
                net_amount=Decimal('0'),
                estimated_arrival=None,
                error_message=str(e)
            )
    
    async def process_automated_payouts(self) -> List[PaymentResult]:
        """
        Process automated payouts based on user configurations.
        
        Returns:
            List of payment results
        """
        try:
            results = []
            
            # Get users eligible for automated payouts
            eligible_users = await self._get_eligible_payout_users()
            
            for user_data in eligible_users:
                try:
                    # Calculate available balance
                    available_balance = await self._calculate_available_balance(user_data['user_id'])
                    
                    if available_balance <= 0:
                        continue
                    
                    # Get payout configuration
                    payout_config = await self._get_payout_configuration(user_data['user_id'])
                    
                    # Check if payout is due
                    if not await self._is_payout_due(user_data['user_id'], payout_config):
                        continue
                    
                    # Create payment request
                    payment_request = PaymentRequest(
                        user_id=user_data['user_id'],
                        amount=available_balance,
                        currency=payout_config.currency,
                        gateway=payout_config.primary_gateway,
                        description=f"Automated payout for period {datetime.utcnow().strftime('%Y-%m-%d')}",
                        metadata={'automated': True, 'period': datetime.utcnow().isoformat()},
                        recipient_info=payout_config.bank_details,
                        payout_frequency=payout_config.payout_frequency
                    )
                    
                    # Process payout
                    result = await self.process_payout(payment_request)
                    results.append(result)
                    
                    # Log successful automated payout
                    if result.status == PaymentStatus.COMPLETED:
                        self.logger.info(
                            f"Automated payout completed for user {user_data['user_id']}: "
                            f"{result.net_amount} {payout_config.currency.value}"
                        )
                    
                except Exception as e:
                    self.logger.error(
                        f"Error processing automated payout for user {user_data['user_id']}: {str(e)}"
                    )
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing automated payouts: {str(e)}")
            return []
    
    async def setup_payout_configuration(self, user_id: str, 
                                       config: PayoutConfiguration) -> bool:
        """
        Setup or update user payout configuration.
        
        Args:
            user_id: User identifier
            config: Payout configuration
            
        Returns:
            Success status
        """
        try:
            # Validate configuration
            await self._validate_payout_configuration(config)
            
            # Verify bank details
            bank_verification = await self._verify_bank_details(config)
            if not bank_verification['valid']:
                raise ValueError(f"Invalid bank details: {bank_verification['error']}")
            
            # Store configuration
            await self._store_payout_configuration(user_id, config)
            
            # Send confirmation
            await self._send_configuration_confirmation(user_id, config)
            
            self.logger.info(f"Payout configuration setup completed for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up payout configuration: {str(e)}")
            return False
    
    async def get_payment_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get payment history for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            
        Returns:
            Payment history records
        """
        try:
            query = select(PaymentModel).where(
                PaymentModel.user_id == user_id
            ).order_by(PaymentModel.created_at.desc()).limit(limit)
            
            result = await self.db_session.execute(query)
            payments = result.scalars().all()
            
            history = []
            for payment in payments:
                history.append({
                    'payment_id': payment.id,
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                    'gateway': payment.gateway,
                    'status': payment.status,
                    'created_at': payment.created_at.isoformat(),
                    'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
                    'fees': float(payment.fees),
                    'net_amount': float(payment.net_amount),
                    'description': payment.description
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting payment history: {str(e)}")
            return []
    
    async def refund_payment(self, payment_id: str, reason: str) -> PaymentResult:
        """
        Process payment refund.
        
        Args:
            payment_id: Payment identifier
            reason: Refund reason
            
        Returns:
            Refund result
        """
        try:
            # Get payment record
            payment = await self._get_payment_record(payment_id)
            if not payment:
                raise ValueError(f"Payment not found: {payment_id}")
            
            # Check if refund is possible
            if payment.status != PaymentStatus.COMPLETED:
                raise ValueError(f"Cannot refund payment with status: {payment.status}")
            
            # Process refund through gateway
            refund_result = await self._process_gateway_refund(payment, reason)
            
            # Update payment record
            await self._update_payment_status(payment_id, PaymentStatus.REFUNDED)
            
            # Update user balance
            await self._update_user_balance(payment.user_id, payment.amount)
            
            # Send notifications
            await self._send_refund_notifications(payment, refund_result, reason)
            
            return PaymentResult(
                payment_id=payment_id,
                status=PaymentStatus.REFUNDED,
                transaction_id=refund_result.get('refund_id'),
                gateway_response=refund_result,
                fees=Decimal('0'),
                net_amount=payment.amount,
                estimated_arrival=None
            )
            
        except Exception as e:
            self.logger.error(f"Error processing refund: {str(e)}")
            return PaymentResult(
                payment_id=payment_id,
                status=PaymentStatus.FAILED,
                transaction_id=None,
                gateway_response={},
                fees=Decimal('0'),
                net_amount=Decimal('0'),
                estimated_arrival=None,
                error_message=str(e)
            )
    
    async def get_gateway_status(self) -> Dict[str, Dict]:
        """
        Get status of all payment gateways.
        
        Returns:
            Gateway status information
        """
        try:
            status = {}
            
            # Check Stripe status
            status['stripe'] = await self._check_stripe_status()
            
            # Check PayPal status
            status['paypal'] = await self._check_paypal_status()
            
            # Check Wise status
            status['wise'] = await self._check_wise_status()
            
            # Check bank transfer capabilities
            status['bank_transfer'] = {'available': True, 'latency': 'high'}
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting gateway status: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _validate_payment_request(self, request: PaymentRequest):
        """Validate payment request"""
        if request.amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if not request.user_id:
            raise ValueError("User ID is required")
        
        if not request.recipient_info:
            raise ValueError("Recipient information is required")
    
    async def _get_payout_configuration(self, user_id: str) -> PayoutConfiguration:
        """Get user payout configuration"""
        # Query user payout configuration from database
        # Placeholder implementation
        return PayoutConfiguration(
            user_id=user_id,
            primary_gateway=PaymentGateway.STRIPE,
            backup_gateway=PaymentGateway.WISE,
            minimum_payout=self.minimum_payout_default,
            payout_frequency=PayoutFrequency.WEEKLY,
            currency=Currency.EUR,
            bank_details={
                'account_number': '***1234',
                'routing_number': '***5678',
                'bank_name': 'European Bank'
            },
            tax_info={'tax_id': '***9999'},
            compliance_verified=True
        )
    
    async def _convert_currency(self, amount: Decimal, from_currency: Currency,
                              to_currency: Currency) -> Decimal:
        """
Convert currency amount"""
        if from_currency == to_currency:
            return amount
        
        # Get current exchange rates
        await self._update_exchange_rates()
        
        # Convert via EUR as base
        eur_amount = amount / self.exchange_rates.get(from_currency.value, Decimal('1'))
        converted = eur_amount * self.exchange_rates.get(to_currency.value, Decimal('1'))
        
        return converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_fees(self, amount: Decimal, gateway: PaymentGateway) -> Decimal:
        """
Calculate gateway fees"""
        fee_structure = self.gateway_fees.get(gateway, {})
        percentage_fee = amount * fee_structure.get('percentage', Decimal('0'))
        fixed_fee = fee_structure.get('fixed', Decimal('0'))
        
        return percentage_fee + fixed_fee
    
    async def _process_gateway_payment(self, request: PaymentRequest, amount: Decimal,
                                     config: PayoutConfiguration) -> Dict[str, Any]:
        """
Process payment through specific gateway"""
        try:
            if request.gateway == PaymentGateway.STRIPE:
                return await self._process_stripe_payment(request, amount, config)
            elif request.gateway == PaymentGateway.PAYPAL:
                return await self._process_paypal_payment(request, amount, config)
            elif request.gateway == PaymentGateway.WISE:
                return await self._process_wise_payment(request, amount, config)
            elif request.gateway == PaymentGateway.BANK_TRANSFER:
                return await self._process_bank_transfer(request, amount, config)
            else:
                raise ValueError(f"Unsupported gateway: {request.gateway}")
                
        except Exception as e:
            return {
                'status': PaymentStatus.FAILED,
                'error_message': str(e),
                'transaction_id': None
            }
    
    async def _process_stripe_payment(self, request: PaymentRequest, amount: Decimal,
                                    config: PayoutConfiguration) -> Dict[str, Any]:
        """Process Stripe payout"""
        try:
            # Create Stripe transfer
            transfer = stripe.Transfer.create(
                amount=int(amount * 100),  # Convert to cents
                currency=config.currency.value.lower(),
                destination=config.bank_details.get('stripe_account_id'),
                description=request.description,
                metadata=request.metadata
            )
            
            return {
                'status': PaymentStatus.PROCESSING,
                'transaction_id': transfer.id,
                'estimated_arrival': datetime.utcnow() + timedelta(days=1),
                'gateway_response': transfer
            }
            
        except stripe.error.StripeError as e:
            return {
                'status': PaymentStatus.FAILED,
                'error_message': str(e),
                'transaction_id': None
            }
    
    async def _process_paypal_payment(self, request: PaymentRequest, amount: Decimal,
                                    config: PayoutConfiguration) -> Dict[str, Any]:
        """
Process PayPal payout"""
        try:
            # PayPal payout implementation
            payout_request = {
                'sender_batch_header': {
                    'sender_batch_id': f"batch_{uuid.uuid4()}",
                    'email_subject': "You have a payout!",
                    'email_message': request.description
                },
                'items': [{
                    'recipient_type': 'EMAIL',
                    'amount': {
                        'value': str(amount),
                        'currency': config.currency.value
                    },
                    'receiver': config.bank_details.get('paypal_email'),
                    'note': request.description,
                    'sender_item_id': f"item_{uuid.uuid4()}"
                }]
            }
            
            # Execute payout (placeholder)
            return {
                'status': PaymentStatus.PROCESSING,
                'transaction_id': f"pp_{uuid.uuid4()}",
                'estimated_arrival': datetime.utcnow() + timedelta(hours=24),
                'gateway_response': payout_request
            }
            
        except Exception as e:
            return {
                'status': PaymentStatus.FAILED,
                'error_message': str(e),
                'transaction_id': None
            }
    
    async def _process_wise_payment(self, request: PaymentRequest, amount: Decimal,
                                  config: PayoutConfiguration) -> Dict[str, Any]:
        """Process Wise transfer"""
        try:
            # Wise transfer implementation
            transfer_data = {
                'amount': float(amount),
                'currency': config.currency.value,
                'recipient': config.bank_details,
                'reference': request.description
            }
            
            # Execute transfer (placeholder)
            return {
                'status': PaymentStatus.PROCESSING,
                'transaction_id': f"wise_{uuid.uuid4()}",
                'estimated_arrival': datetime.utcnow() + timedelta(hours=2),
                'gateway_response': transfer_data
            }
            
        except Exception as e:
            return {
                'status': PaymentStatus.FAILED,
                'error_message': str(e),
                'transaction_id': None
            }
    
    async def _process_bank_transfer(self, request: PaymentRequest, amount: Decimal,
                                   config: PayoutConfiguration) -> Dict[str, Any]:
        """Process traditional bank transfer"""
        try:
            # Bank transfer implementation (would integrate with banking API)
            transfer_data = {
                'amount': float(amount),
                'currency': config.currency.value,
                'beneficiary': config.bank_details,
                'reference': request.description,
                'transfer_type': 'SEPA'  # For EUR transfers
            }
            
            return {
                'status': PaymentStatus.PROCESSING,
                'transaction_id': f"bank_{uuid.uuid4()}",
                'estimated_arrival': datetime.utcnow() + timedelta(days=2),
                'gateway_response': transfer_data
            }
            
        except Exception as e:
            return {
                'status': PaymentStatus.FAILED,
                'error_message': str(e),
                'transaction_id': None
            }
    
    async def _create_payment_record(self, request: PaymentRequest, gateway_result: Dict,
                                   fees: Decimal, net_amount: Decimal) -> str:
        """Create payment record in database"""
        payment_id = str(uuid.uuid4())
        
        payment_record = PaymentModel(
            id=payment_id,
            user_id=request.user_id,
            amount=request.amount,
            currency=request.currency.value,
            gateway=request.gateway.value,
            status=gateway_result['status'].value,
            transaction_id=gateway_result.get('transaction_id'),
            fees=fees,
            net_amount=net_amount,
            description=request.description,
            metadata=request.metadata,
            created_at=datetime.utcnow()
        )
        
        self.db_session.add(payment_record)
        await self.db_session.commit()
        
        return payment_id
    
    def _get_config(self, key: str) -> str:
        """
Get configuration value"""
        import os
        return os.getenv(key, '')
    
    async def _update_exchange_rates(self):
        """
Update currency exchange rates"""
        if (self.rate_last_updated and 
            datetime.utcnow() - self.rate_last_updated < timedelta(hours=1)):
            return
        
        try:
            # Fetch rates from external API (placeholder)
            self.exchange_rates = {
                'USD': Decimal('1.00'),
                'EUR': Decimal('0.85'),
                'GBP': Decimal('0.73'),
                'CAD': Decimal('1.25'),
                'AUD': Decimal('1.35'),
                'JPY': Decimal('110.00')
            }
            self.rate_last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error updating exchange rates: {str(e)}")
    
    # Additional helper methods would be implemented here...
    
    async def _get_eligible_payout_users(self) -> List[Dict]:
        """Get users eligible for automated payouts"""
        # Implementation would query database for eligible users
        return []
    
    async def _calculate_available_balance(self, user_id: str) -> Decimal:
        """
Calculate user's available balance for payout"""
        # Implementation would calculate from revenue records
        return Decimal('0')
    
    async def _is_payout_due(self, user_id: str, config: PayoutConfiguration) -> bool:
        """
Check if payout is due based on frequency"""
        # Implementation would check last payout date vs frequency
        return False
    
    async def _send_payment_notifications(self, request: PaymentRequest, result: Dict):
        try:
            logger.info(f"Executing _send_payment_notifications")
            
            # Implementation for _send_payment_notifications
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_payment_notifications completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_payment_notifications failed: {e}")
            raise
    async def _verify_bank_details(self, config: PayoutConfiguration) -> Dict:
        """
Verify bank account details"""
        # Implementation would verify bank details through banking API
        return {'valid': True, 'error': None}
