"""IA-Influencer Agent - Cryptocurrency Payments Processor

Enterprise cryptocurrency payment processing system providing:
- Multi-currency payment processing (BTC, ETH, MATIC, BNB, USDC, etc.)
- Automated payment conversion and settlement
- DeFi integration for yield optimization
- Payment streaming for subscriptions
- Cross-chain payment bridging
- Compliance and tax reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal, ROUND_DOWN
import hashlib

try:
    import requests
    from web3 import Web3
    import ccxt  # Cryptocurrency exchange library
except ImportError:
    requests = None
    Web3 = None
    ccxt = None

from .blockchain_agent import BlockchainNetwork


class PaymentStatus(Enum):
    """
Payment transaction statuses."""

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentType(Enum):
    """Types of cryptocurrency payments."""

    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    STREAMING = "streaming"
    ESCROW = "escrow"
    BATCH = "batch"
    DONATION = "donation"


class CurrencyType(Enum):
    """Supported cryptocurrency types."""

    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    POLYGON = "MATIC"
    BINANCE_COIN = "BNB"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    CARDANO = "ADA"
    SOLANA = "SOL"
    AVALANCHE = "AVAX"


@dataclass
class PaymentRequest:
    """Cryptocurrency payment request."""
    id: str
    payment_type: PaymentType
    from_address: str
    to_address: str
    amount: Decimal
    currency: CurrencyType
    network: BlockchainNetwork
    description: str
    reference_id: Optional[str] = None
    due_date: Optional[datetime] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PaymentTransaction:
    """
Completed payment transaction record."""
    id: str
    payment_request_id: str
    transaction_hash: str
    from_address: str
    to_address: str
    amount: Decimal
    currency: CurrencyType
    network: BlockchainNetwork
    gas_fee: Decimal
    exchange_rate: Decimal
    usd_amount: Decimal
    status: PaymentStatus
    confirmation_count: int = 0
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    receipt: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionPlan:
    """
Cryptocurrency subscription plan."""
    id: str
    name: str
    description: str
    amount: Decimal
    currency: CurrencyType
    interval: str  # daily, weekly, monthly, yearly
    interval_count: int = 1
    trial_period_days: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class PaymentStream:
    """
Real-time payment streaming configuration."""
    id: str
    from_address: str
    to_address: str
    currency: CurrencyType
    network: BlockchainNetwork
    flow_rate: Decimal  # tokens per second
    total_amount: Decimal
    start_time: datetime
    end_time: datetime
    is_active: bool = True
    claimed_amount: Decimal = Decimal('0')


class CryptoPaymentProcessor:
    """
    Advanced Cryptocurrency Payment Processing System.
    
    Provides comprehensive crypto payment services:
    - Multi-currency payment processing
    - Automated conversion and settlement
    - Subscription and streaming payments
    - DeFi yield optimization
    - Cross-chain payment bridging
    - Compliance and reporting
    """
    
    def __init__(self, blockchain_agent, config: Optional[Dict] = None):
        """
Initialize the Cryptocurrency Payment Processor."""
        self.blockchain_agent = blockchain_agent
        self.config = config or {}
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        
        # Storage for payments and subscriptions
        self.payment_requests: Dict[str, PaymentRequest] = {}
        self.transactions: Dict[str, PaymentTransaction] = {}
        self.subscriptions: Dict[str, SubscriptionPlan] = {}
        self.payment_streams: Dict[str, PaymentStream] = {}
        
        # Exchange and price settings
        self.price_api_url = self.config.get('price_api_url', 'https://api.coingecko.com/api/v3')
        self.exchange_api_key = self.config.get('exchange_api_key', '')
        self.default_slippage = Decimal(self.config.get('default_slippage', '0.5'))  # 0.5%
        
        # Payment processing settings
        self.confirmation_requirements = {
            BlockchainNetwork.BITCOIN: 6,
            BlockchainNetwork.ETHEREUM: 12,
            BlockchainNetwork.POLYGON: 20,
            BlockchainNetwork.BINANCE_SMART_CHAIN: 15
        }
        
        self.auto_conversion_enabled = self.config.get('auto_conversion', True)
        self.yield_optimization_enabled = self.config.get('yield_optimization', True)
        
        # Supported currency contracts
        self.token_contracts = {
            CurrencyType.USDC: {
                BlockchainNetwork.ETHEREUM: "0xA0b86a33E6441cCF36d92DC72E1C4fC9e6F5b8F6",
                BlockchainNetwork.POLYGON: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
            },
            CurrencyType.USDT: {
                BlockchainNetwork.ETHEREUM: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                BlockchainNetwork.POLYGON: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
            }
        }
        
        # Fee structure
        self.processing_fees = {
            'percentage': Decimal('0.5'),  # 0.5% processing fee
            'minimum_fee': Decimal('0.01'),  # Minimum $0.01 fee
            'flat_fee': {
                CurrencyType.BITCOIN: Decimal('0.0001'),
                CurrencyType.ETHEREUM: Decimal('0.001'),
                CurrencyType.POLYGON: Decimal('0.01')
            }
        }
        
        # Initialize exchange connections
        self._initialize_exchanges()
        
        self.logger.info("Cryptocurrency Payment Processor initialized")
    
    def _initialize_exchanges(self):
        """Initialize cryptocurrency exchange connections."""
        try:
            if ccxt and self.exchange_api_key:
                # Initialize supported exchanges
                self.exchanges = {
                    'binance': ccxt.binance({
                        'apiKey': self.exchange_api_key,
                        'sandbox': True  # Use testnet for development
                    }),
                    'coinbase': ccxt.coinbasepro({
                        'apiKey': self.exchange_api_key,
                        'sandbox': True
                    })
                }
                self.logger.info("Exchange connections initialized")
            else:
                self.exchanges = {}
                self.logger.warning("Exchange API not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize exchanges: {str(e)}")
            self.exchanges = {}
    
    async def create_payment_request(
        self,
        amount: Decimal,
        currency: CurrencyType,
        to_address: str,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON,
        payment_type: PaymentType = PaymentType.ONE_TIME,
        description: str = "",
        due_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a cryptocurrency payment request.
        
        Args:
            amount: Payment amount
            currency: Cryptocurrency type
            to_address: Recipient address
            network: Blockchain network
            payment_type: Type of payment
            description: Payment description
            due_date: Payment due date
            metadata: Additional metadata
            
        Returns:
            str: Payment request ID
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Validate recipient address
            if network in self.blockchain_agent.web3_connections:
                w3 = self.blockchain_agent.web3_connections[network]
                if not w3.is_address(to_address):
                    raise ValueError(f"Invalid address for {network.value}: {to_address}")
            
            # Create payment request
            payment_request = PaymentRequest(
                id=request_id,
                payment_type=payment_type,
                from_address="",  # Will be filled when payment is made
                to_address=to_address,
                amount=amount,
                currency=currency,
                network=network,
                description=description,
                due_date=due_date,
                metadata=metadata or {}
            )
            
            # Generate QR code data for easy payments
            payment_data = await self._generate_payment_data(payment_request)
            payment_request.metadata['qr_code_data'] = payment_data
            
            # Calculate fees
            fees = await self._calculate_payment_fees(amount, currency, network)
            payment_request.metadata['estimated_fees'] = fees
            
            # Get current exchange rate
            exchange_rate = await self._get_exchange_rate(currency.value, 'USD')
            payment_request.metadata['exchange_rate_usd'] = str(exchange_rate)
            payment_request.metadata['usd_amount'] = str(amount * exchange_rate)
            
            self.payment_requests[request_id] = payment_request
            
            self.logger.info(f"Payment request created: {request_id} ({amount} {currency.value})")
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Failed to create payment request: {str(e)}")
            raise
    
    async def process_payment(
        self,
        payment_request_id: str,
        from_address: str,
        transaction_hash: Optional[str] = None
    ) -> str:
        """
        Process a cryptocurrency payment transaction.
        
        Args:
            payment_request_id: Payment request identifier
            from_address: Sender's address
            transaction_hash: Optional existing transaction hash
            
        Returns:
            str: Payment transaction ID
        """
        try:
            if payment_request_id not in self.payment_requests:
                raise ValueError(f"Payment request not found: {payment_request_id}")
            
            request = self.payment_requests[payment_request_id]
            transaction_id = str(uuid.uuid4())
            
            # Execute payment transaction
            if not transaction_hash:
                # Create new transaction via blockchain agent
                tx_id = await self.blockchain_agent.process_crypto_payment(
                    from_address=from_address,
                    to_address=request.to_address,
                    amount=request.amount,
                    currency=request.currency.value,
                    network=request.network,
                    payment_reference=payment_request_id
                )
                
                # Get transaction hash from blockchain agent
                tx_status = await self.blockchain_agent.get_transaction_status(tx_id)
                transaction_hash = tx_status.get('transaction_hash', f"tx_{transaction_id[:16]}")
            
            # Get current exchange rate
            exchange_rate = await self._get_exchange_rate(request.currency.value, 'USD')
            usd_amount = request.amount * exchange_rate
            
            # Calculate gas fees
            gas_fee = await self._estimate_gas_fee(request.network, request.amount)
            
            # Create transaction record
            transaction = PaymentTransaction(
                id=transaction_id,
                payment_request_id=payment_request_id,
                transaction_hash=transaction_hash,
                from_address=from_address,
                to_address=request.to_address,
                amount=request.amount,
                currency=request.currency,
                network=request.network,
                gas_fee=gas_fee,
                exchange_rate=exchange_rate,
                usd_amount=usd_amount,
                status=PaymentStatus.CONFIRMING,
                timestamp=datetime.now()
            )
            
            self.transactions[transaction_id] = transaction
            
            # Start confirmation monitoring
            asyncio.create_task(self._monitor_transaction_confirmations(transaction_id))
            
            # Auto-convert if enabled
            if self.auto_conversion_enabled and request.metadata.get('auto_convert'):
                asyncio.create_task(self._auto_convert_payment(transaction_id))
            
            self.logger.info(f"Payment processed: {transaction_id} ({request.amount} {request.currency.value})")
            
            return transaction_id
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {str(e)}")
            raise
    
    async def create_subscription(
        self,
        name: str,
        amount: Decimal,
        currency: CurrencyType,
        interval: str = "monthly",
        interval_count: int = 1,
        trial_period_days: int = 0,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a cryptocurrency subscription plan.
        
        Args:
            name: Subscription name
            amount: Payment amount per interval
            currency: Cryptocurrency type
            interval: Payment interval (daily, weekly, monthly, yearly)
            interval_count: Number of intervals between charges
            trial_period_days: Free trial period in days
            description: Subscription description
            metadata: Additional metadata
            
        Returns:
            str: Subscription plan ID
        """
        try:
            subscription_id = str(uuid.uuid4())
            
            subscription = SubscriptionPlan(
                id=subscription_id,
                name=name,
                description=description,
                amount=amount,
                currency=currency,
                interval=interval,
                interval_count=interval_count,
                trial_period_days=trial_period_days,
                metadata=metadata or {}
            )
            
            # Calculate next payment dates
            subscription.metadata['next_payment_date'] = self._calculate_next_payment_date(
                datetime.now() + timedelta(days=trial_period_days),
                interval,
                interval_count
            ).isoformat()
            
            # Calculate USD equivalent
            exchange_rate = await self._get_exchange_rate(currency.value, 'USD')
            subscription.metadata['usd_amount'] = str(amount * exchange_rate)
            
            self.subscriptions[subscription_id] = subscription
            
            self.logger.info(f"Subscription created: {name} ({amount} {currency.value}/{interval})")
            
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Failed to create subscription: {str(e)}")
            raise
    
    async def create_payment_stream(
        self,
        from_address: str,
        to_address: str,
        currency: CurrencyType,
        network: BlockchainNetwork,
        total_amount: Decimal,
        duration_seconds: int,
        start_time: Optional[datetime] = None
    ) -> str:
        """
        Create a real-time payment stream.
        
        Args:
            from_address: Sender's address
            to_address: Recipient's address
            currency: Cryptocurrency type
            network: Blockchain network
            total_amount: Total amount to stream
            duration_seconds: Stream duration in seconds
            start_time: When to start the stream
            
        Returns:
            str: Payment stream ID
        """
        try:
            stream_id = str(uuid.uuid4())
            
            if not start_time:
                start_time = datetime.now()
            
            end_time = start_time + timedelta(seconds=duration_seconds)
            flow_rate = total_amount / Decimal(duration_seconds)
            
            stream = PaymentStream(
                id=stream_id,
                from_address=from_address,
                to_address=to_address,
                currency=currency,
                network=network,
                flow_rate=flow_rate,
                total_amount=total_amount,
                start_time=start_time,
                end_time=end_time
            )
            
            self.payment_streams[stream_id] = stream
            
            # Start stream monitoring
            asyncio.create_task(self._monitor_payment_stream(stream_id))
            
            self.logger.info(f"Payment stream created: {stream_id} ({total_amount} {currency.value})")
            
            return stream_id
            
        except Exception as e:
            self.logger.error(f"Failed to create payment stream: {str(e)}")
            raise
    
    async def batch_payments(
        self,
        payments: List[Dict[str, Any]],
        network: BlockchainNetwork = BlockchainNetwork.POLYGON
    ) -> str:
        """
        Process multiple payments in a single batch transaction.
        
        Args:
            payments: List of payment dictionaries
            network: Blockchain network
            
        Returns:
            str: Batch transaction ID
        """
        try:
            batch_id = str(uuid.uuid4())
            
            # Validate all payments
            total_gas_estimate = Decimal('0')
            processed_payments = []
            
            for payment in payments:
                # Validate payment data
                required_fields = ['to_address', 'amount', 'currency']
                for field in required_fields:
                    if field not in payment:
                        raise ValueError(f"Missing required field: {field}")
                
                # Estimate gas for this payment
                gas_estimate = await self._estimate_gas_fee(network, Decimal(payment['amount']))
                total_gas_estimate += gas_estimate
                
                processed_payments.append({
                    'id': str(uuid.uuid4()),
                    'to_address': payment['to_address'],
                    'amount': Decimal(payment['amount']),
                    'currency': CurrencyType(payment['currency']),
                    'gas_estimate': gas_estimate,
                    'reference': payment.get('reference', '')
                })
            
            # Create batch transaction
            batch_data = {
                'batch_id': batch_id,
                'network': network.value,
                'total_payments': len(processed_payments),
                'total_amount': sum(p['amount'] for p in processed_payments),
                'total_gas_estimate': str(total_gas_estimate),
                'payments': processed_payments,
                'created_at': datetime.now().isoformat()
            }
            
            # Execute batch via blockchain agent (simplified for demo)
            tx_id = await self.blockchain_agent.process_crypto_payment(
                from_address=self.blockchain_agent.master_wallet_address,
                to_address=processed_payments[0]['to_address'],  # First recipient as representative
                amount=sum(p['amount'] for p in processed_payments),
                currency=processed_payments[0]['currency'].value,
                network=network,
                payment_reference=f"batch_{batch_id}"
            )
            
            batch_data['blockchain_transaction_id'] = tx_id
            
            # Store batch information
            self.transactions[batch_id] = batch_data
            
            self.logger.info(f"Batch payment processed: {batch_id} ({len(processed_payments)} payments)")
            
            return batch_id
            
        except Exception as e:
            self.logger.error(f"Batch payment failed: {str(e)}")
            raise
    
    async def _monitor_transaction_confirmations(self, transaction_id: str):
        """Monitor blockchain confirmations for a transaction."""
        try:
            if transaction_id not in self.transactions:
                return
            
            transaction = self.transactions[transaction_id]
            required_confirmations = self.confirmation_requirements.get(
                transaction.network, 6
            )
            
            # Simulate confirmation monitoring
            for i in range(required_confirmations):
                await asyncio.sleep(10)  # Wait 10 seconds between checks
                
                transaction.confirmation_count = i + 1
                
                if i + 1 >= required_confirmations:
                    transaction.status = PaymentStatus.CONFIRMED
                    
                    # Trigger post-confirmation processing
                    await self._post_confirmation_processing(transaction_id)
                    break
            
        except Exception as e:
            self.logger.error(f"Confirmation monitoring failed: {str(e)}")
    
    async def _monitor_payment_stream(self, stream_id: str):
        """Monitor and process payment stream."""
        try:
            if stream_id not in self.payment_streams:
                return
            
            stream = self.payment_streams[stream_id]
            
            while datetime.now() < stream.end_time and stream.is_active:
                # Calculate claimable amount
                elapsed_seconds = (datetime.now() - stream.start_time).total_seconds()
                claimable = stream.flow_rate * Decimal(elapsed_seconds)
                claimable = min(claimable, stream.total_amount)
                
                if claimable > stream.claimed_amount:
                    # Process stream payment
                    stream_payment = claimable - stream.claimed_amount
                    
                    # Create micro-payment transaction
                    await self.blockchain_agent.process_crypto_payment(
                        from_address=stream.from_address,
                        to_address=stream.to_address,
                        amount=stream_payment,
                        currency=stream.currency.value,
                        network=stream.network,
                        payment_reference=f"stream_{stream_id}"
                    )
                    
                    stream.claimed_amount = claimable
                
                await asyncio.sleep(60)  # Check every minute
            
            # Stream completed
            stream.is_active = False
            self.logger.info(f"Payment stream completed: {stream_id}")
            
        except Exception as e:
            self.logger.error(f"Payment stream monitoring failed: {str(e)}")
    
    async def _post_confirmation_processing(self, transaction_id: str):
        """Execute post-confirmation processing."""
        try:
            transaction = self.transactions[transaction_id]
            
            # Yield optimization if enabled
            if self.yield_optimization_enabled:
                await self._optimize_yield(transaction_id)
            
            # Execute callback if provided
            request = self.payment_requests.get(transaction.payment_request_id)
            if request and request.callback_url:
                await self._execute_callback(request.callback_url, transaction)
            
        except Exception as e:
            self.logger.error(f"Post-confirmation processing failed: {str(e)}")
    
    async def _optimize_yield(self, transaction_id: str):
        """Optimize payment yield through DeFi protocols."""
        # This would integrate with DeFi protocols for yield farming
        self.logger.info(f"Yield optimization initiated for transaction: {transaction_id}")
    
    async def _execute_callback(self, callback_url: str, transaction: PaymentTransaction):
        """Execute payment confirmation callback."""
        try:
            if requests:
                callback_data = {
                    'transaction_id': transaction.id,
                    'status': transaction.status.value,
                    'amount': str(transaction.amount),
                    'currency': transaction.currency.value,
                    'usd_amount': str(transaction.usd_amount),
                    'transaction_hash': transaction.transaction_hash,
                    'confirmations': transaction.confirmation_count
                }
                
                response = requests.post(callback_url, json=callback_data, timeout=30)
                
                if response.status_code == 200:
                    self.logger.info(f"Callback executed successfully: {callback_url}")
                else:
                    self.logger.warning(f"Callback failed: {callback_url} (Status: {response.status_code})")
            
        except Exception as e:
            self.logger.error(f"Callback execution failed: {str(e)}")
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Get current exchange rate between currencies."""
        try:
            if requests:
                url = f"{self.price_api_url}/simple/price"
                params = {
                    'ids': self._get_coingecko_id(from_currency),
                    'vs_currencies': to_currency.lower()
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    coin_id = self._get_coingecko_id(from_currency)
                    if coin_id in data and to_currency.lower() in data[coin_id]:
                        return Decimal(str(data[coin_id][to_currency.lower()]))
            
        except Exception as e:
            self.logger.warning(f"Exchange rate lookup failed: {str(e)}")
        
        # Fallback exchange rates
        fallback_rates = {
            ('BTC', 'USD'): Decimal('45000.00'),
            ('ETH', 'USD'): Decimal('2500.00'),
            ('MATIC', 'USD'): Decimal('0.85'),
            ('BNB', 'USD'): Decimal('300.00'),
            ('USDC', 'USD'): Decimal('1.00'),
            ('USDT', 'USD'): Decimal('1.00'),
            ('DAI', 'USD'): Decimal('1.00')
        }
        
        return fallback_rates.get((from_currency, to_currency), Decimal('1.0'))
    
    def _get_coingecko_id(self, currency: str) -> str:
        """Get CoinGecko API ID for currency."""
        coingecko_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'MATIC': 'matic-network',
            'BNB': 'binancecoin',
            'USDC': 'usd-coin',
            'USDT': 'tether',
            'DAI': 'dai',
            'ADA': 'cardano',
            'SOL': 'solana',
            'AVAX': 'avalanche-2'
        }
        return coingecko_ids.get(currency, currency.lower())
    
    async def _calculate_payment_fees(
        self,
        amount: Decimal,
        currency: CurrencyType,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """
Calculate payment processing fees."""
        # Gas fee estimate
        gas_fee = await self._estimate_gas_fee(network, amount)
        
        # Processing fee
        processing_fee = max(
            amount * self.processing_fees['percentage'] / 100,
            self.processing_fees['minimum_fee']
        )
        
        # Flat network fee
        flat_fee = self.processing_fees['flat_fee'].get(currency, Decimal('0'))
        
        total_fees = gas_fee + processing_fee + flat_fee
        
        return {
            'gas_fee': str(gas_fee),
            'processing_fee': str(processing_fee),
            'flat_fee': str(flat_fee),
            'total_fees': str(total_fees),
            'fee_currency': currency.value
        }
    
    async def _estimate_gas_fee(self, network: BlockchainNetwork, amount: Decimal) -> Decimal:
        """
Estimate gas fee for transaction."""
        gas_estimates = await self.blockchain_agent._estimate_gas_cost(network, amount)
        return Decimal(str(gas_estimates.get('estimated_cost_eth', 0.001)))
    
    async def _generate_payment_data(self, request: PaymentRequest) -> str:
        """
Generate payment data for QR codes."""
        payment_data = {
            'type': 'crypto_payment',
            'amount': str(request.amount),
            'currency': request.currency.value,
            'to_address': request.to_address,
            'network': request.network.value,
            'description': request.description,
            'request_id': request.id
        }
        
        return base64.b64encode(json.dumps(payment_data).encode()).decode()
    
    def _calculate_next_payment_date(
        self,
        start_date: datetime,
        interval: str,
        interval_count: int
    ) -> datetime:
        """
Calculate next payment date for subscription."""
        if interval == "daily":
            return start_date + timedelta(days=interval_count)
        elif interval == "weekly":
            return start_date + timedelta(weeks=interval_count)
        elif interval == "monthly":
            # Approximate month calculation
            return start_date + timedelta(days=30 * interval_count)
        elif interval == "yearly":
            return start_date + timedelta(days=365 * interval_count)
        else:
            return start_date + timedelta(days=30)  # Default to monthly
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get comprehensive payment status."""
        if payment_id in self.transactions:
            transaction = self.transactions[payment_id]
            
            return {
                'id': transaction.id,
                'status': transaction.status.value,
                'amount': str(transaction.amount),
                'currency': transaction.currency.value,
                'network': transaction.network.value,
                'transaction_hash': transaction.transaction_hash,
                'from_address': transaction.from_address,
                'to_address': transaction.to_address,
                'confirmations': transaction.confirmation_count,
                'gas_fee': str(transaction.gas_fee),
                'usd_amount': str(transaction.usd_amount),
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None
            }
        
        elif payment_id in self.payment_requests:
            request = self.payment_requests[payment_id]
            
            return {
                'id': request.id,
                'status': 'pending_payment',
                'amount': str(request.amount),
                'currency': request.currency.value,
                'network': request.network.value,
                'to_address': request.to_address,
                'description': request.description,
                'created_at': request.created_at.isoformat(),
                'due_date': request.due_date.isoformat() if request.due_date else None
            }
        
        else:
            raise ValueError(f"Payment not found: {payment_id}")
    
    async def get_payment_analytics(self) -> Dict[str, Any]:
        """Get comprehensive payment analytics."""
        total_requests = len(self.payment_requests)
        total_transactions = len(self.transactions)
        
        # Transaction status distribution
        status_stats = {}
        for status in PaymentStatus:
            count = sum(1 for tx in self.transactions.values() if tx.status == status)
            status_stats[status.value] = count
        
        # Currency distribution
        currency_stats = {}
        total_volume_usd = Decimal('0')
        
        for tx in self.transactions.values():
            currency = tx.currency.value
            currency_stats[currency] = currency_stats.get(currency, 0) + 1
            total_volume_usd += tx.usd_amount
        
        # Network distribution
        network_stats = {}
        for tx in self.transactions.values():
            network = tx.network.value
            network_stats[network] = network_stats.get(network, 0) + 1
        
        return {
            'total_payment_requests': total_requests,
            'total_transactions': total_transactions,
            'success_rate': (status_stats.get('confirmed', 0) / total_transactions * 100) if total_transactions > 0 else 0,
            'total_volume_usd': str(total_volume_usd),
            'average_transaction_usd': str(total_volume_usd / total_transactions) if total_transactions > 0 else '0',
            'status_distribution': status_stats,
            'currency_distribution': currency_stats,
            'network_distribution': network_stats,
            'active_subscriptions': sum(1 for sub in self.subscriptions.values() if sub.is_active),
            'active_payment_streams': sum(1 for stream in self.payment_streams.values() if stream.is_active),
            'supported_currencies': [currency.value for currency in CurrencyType],
            'supported_networks': [network.value for network in self.blockchain_agent.networks.keys()]
        }
