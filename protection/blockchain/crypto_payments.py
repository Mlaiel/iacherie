"""Cryptocurrency Payment Processing for Content Protection Services
Professional implementation of crypto payments, staking, and DeFi integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineer & Blockchain Specialist: Advanced IA Processing
- Database Administrator & Security Expert: Data Protection
- Microservices Architect & Audio Processing: Multi-format Support  
- DevOps Engineer & IA Prompt Engineer: Production Deployment

⚠️ STRONG WARNING ⚠️
Any attempt to steal, copy, reproduce, or use this concept, idea, or code 
without explicit written authorization from Fahed Mlaiel is strictly 
prohibited and will result in legal action.

Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import json
import hashlib
import secrets
import uuid
import aiohttp
from web3 import Web3
from eth_account import Account
from eth_typing import ChecksumAddress

from .exceptions import (
    CryptoPaymentError,
    InsufficientFundsError,
    TransactionError,
    Web3ProviderError,
    GasEstimationError
)

logger = logging.getLogger(__name__)


class SupportedCryptocurrency(Enum):
    """
Supported cryptocurrencies for payments"""

    ETHEREUM = "ETH"
    BITCOIN = "BTC"
    POLYGON_MATIC = "MATIC"
    BINANCE_COIN = "BNB"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    CHAINLINK = "LINK"
    UNI = "UNI"
    AAVE = "AAVE"


class PaymentStatus(Enum):
    """Payment transaction status"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class ServiceTier(Enum):
    """Service tiers for content protection"""

    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


@dataclass
class PaymentRate:
    """Payment rates for different services"""
    service_type: str
    base_price_usd: Decimal
    cryptocurrency: SupportedCryptocurrency
    current_rate: Decimal  # Crypto amount per USD
    rate_timestamp: datetime
    discount_percentage: Decimal = Decimal('0')
    
    def calculate_crypto_amount(self, usd_amount: Decimal) -> Decimal:
        """
Calculate cryptocurrency amount for USD value"""
        discounted_amount = usd_amount * (Decimal('1') - self.discount_percentage / Decimal('100'))
        crypto_amount = discounted_amount * self.current_rate
        return crypto_amount.quantize(Decimal('0.000001'), rounding=ROUND_DOWN)


@dataclass
class PaymentRequest:
    """
Cryptocurrency payment request"""
    request_id: str
    user_id: str
    service_type: str
    service_tier: ServiceTier
    amount_usd: Decimal
    cryptocurrency: SupportedCryptocurrency
    amount_crypto: Decimal
    recipient_address: str
    payment_address: str
    
    # Payment details
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Transaction tracking
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    confirmation_count: int = 0
    required_confirmations: int = 6
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'service_type': self.service_type,
            'service_tier': self.service_tier.value,
            'amount_usd': str(self.amount_usd),
            'cryptocurrency': self.cryptocurrency.value,
            'amount_crypto': str(self.amount_crypto),
            'recipient_address': self.recipient_address,
            'payment_address': self.payment_address,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'status': self.status.value,
            'transaction_hash': self.transaction_hash,
            'block_number': self.block_number,
            'confirmation_count': self.confirmation_count,
            'required_confirmations': self.required_confirmations,
            'metadata': self.metadata
        }


class PriceOracle:
    """
Cryptocurrency price oracle for real-time rates"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.price_cache: Dict[str, Tuple[Decimal, datetime]] = {}
        self.cache_duration = timedelta(minutes=5)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_price(self, cryptocurrency: SupportedCryptocurrency) -> Decimal:
        """
Get current USD price for cryptocurrency"""
        try:
            cache_key = cryptocurrency.value
            
            # Check cache first
            if cache_key in self.price_cache:
                price, timestamp = self.price_cache[cache_key]
                if datetime.utcnow() - timestamp < self.cache_duration:
                    return price
            
            # Fetch from multiple sources for redundancy
            price = await self._fetch_price_coingecko(cryptocurrency)
            if not price:
                price = await self._fetch_price_coinmarketcap(cryptocurrency)
            if not price:
                price = await self._fetch_price_binance(cryptocurrency)
            
            if price:
                self.price_cache[cache_key] = (price, datetime.utcnow())
                return price
            
            raise Exception(f"Could not fetch price for {cryptocurrency.value}")
            
        except Exception as e:
            logger.error(f"Price fetching failed for {cryptocurrency.value}: {e}")
            # Return cached price if available, even if expired
            if cache_key in self.price_cache:
                return self.price_cache[cache_key][0]
            raise
    
    async def _fetch_price_coingecko(self, cryptocurrency: SupportedCryptocurrency) -> Optional[Decimal]:
        """Fetch price from CoinGecko API"""
        try:
            coin_ids = {
                SupportedCryptocurrency.ETHEREUM: 'ethereum',
                SupportedCryptocurrency.BITCOIN: 'bitcoin',
                SupportedCryptocurrency.POLYGON_MATIC: 'matic-network',
                SupportedCryptocurrency.BINANCE_COIN: 'binancecoin',
                SupportedCryptocurrency.USDC: 'usd-coin',
                SupportedCryptocurrency.USDT: 'tether',
                SupportedCryptocurrency.DAI: 'dai',
                SupportedCryptocurrency.CHAINLINK: 'chainlink',
                SupportedCryptocurrency.UNI: 'uniswap',
                SupportedCryptocurrency.AAVE: 'aave'
            }
            
            coin_id = coin_ids.get(cryptocurrency)
            if not coin_id:
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get(coin_id, {}).get('usd')
                    if price:
                        return Decimal(str(price))
            
            return None
            
        except Exception as e:
            logger.warning(f"CoinGecko price fetch failed: {e}")
            return None
    
    async def _fetch_price_coinmarketcap(self, cryptocurrency: SupportedCryptocurrency) -> Optional[Decimal]:
        """Fetch price from CoinMarketCap API"""
        try:
            api_key = self.api_keys.get('coinmarketcap')
            if not api_key:
                return None
            
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            headers = {
                'X-CMC_PRO_API_KEY': api_key,
                'Accept': 'application/json'
            }
            params = {
                'symbol': cryptocurrency.value,
                'convert': 'USD'
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get('data', {}).get(cryptocurrency.value, {}).get('quote', {}).get('USD', {})
                    price = quote.get('price')
                    if price:
                        return Decimal(str(price))
            
            return None
            
        except Exception as e:
            logger.warning(f"CoinMarketCap price fetch failed: {e}")
            return None
    
    async def _fetch_price_binance(self, cryptocurrency: SupportedCryptocurrency) -> Optional[Decimal]:
        """Fetch price from Binance API"""
        try:
            symbol_mapping = {
                SupportedCryptocurrency.ETHEREUM: 'ETHUSDT',
                SupportedCryptocurrency.BITCOIN: 'BTCUSDT',
                SupportedCryptocurrency.POLYGON_MATIC: 'MATICUSDT',
                SupportedCryptocurrency.BINANCE_COIN: 'BNBUSDT',
                SupportedCryptocurrency.CHAINLINK: 'LINKUSDT',
                SupportedCryptocurrency.UNI: 'UNIUSDT',
                SupportedCryptocurrency.AAVE: 'AAVEUSDT'
            }
            
            symbol = symbol_mapping.get(cryptocurrency)
            if not symbol:
                return None
            
            url = "https://api.binance.com/api/v3/ticker/price"
            params = {'symbol': symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get('price')
                    if price:
                        return Decimal(price)
            
            return None
            
        except Exception as e:
            logger.warning(f"Binance price fetch failed: {e}")
            return None
    
    async def get_conversion_rate(
        self,
        from_currency: SupportedCryptocurrency,
        to_currency: SupportedCryptocurrency
    ) -> Decimal:
        """Get conversion rate between two cryptocurrencies"""
        try:
            if from_currency == to_currency:
                return Decimal('1')
            
            from_price = await self.get_current_price(from_currency)
            to_price = await self.get_current_price(to_currency)
            
            return from_price / to_price
            
        except Exception as e:
            logger.error(f"Conversion rate calculation failed: {e}")
            return Decimal('0')


class PaymentProcessor:
    """Professional cryptocurrency payment processor"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.price_oracle: Optional[PriceOracle] = None
        self.web3_clients: Dict[str, Web3] = {}
        self.wallet_addresses: Dict[SupportedCryptocurrency, str] = {}
        self.service_rates: Dict[str, PaymentRate] = {}
        
        # Initialize service pricing
        self._initialize_service_rates()
    
    async def initialize(self) -> bool:
        """
Initialize payment processor"""
        try:
            # Initialize price oracle
            api_keys = self.config.get('api_keys', {})
            self.price_oracle = PriceOracle(api_keys)
            
            # Initialize Web3 clients
            networks = self.config.get('networks', {})
            for network_name, network_config in networks.items():
                rpc_url = network_config.get('rpc_url')
                if rpc_url:
                    self.web3_clients[network_name] = Web3(Web3.HTTPProvider(rpc_url))
            
            # Load wallet addresses
            wallets = self.config.get('wallets', {})
            for crypto, address in wallets.items():
                if crypto in [c.value for c in SupportedCryptocurrency]:
                    self.wallet_addresses[SupportedCryptocurrency(crypto)] = address
            
            logger.info("Payment processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Payment processor initialization failed: {e}")
            return False
    
    def _initialize_service_rates(self):
        """Initialize service pricing rates"""
        self.service_rates = {
            'content_fingerprinting': PaymentRate(
                service_type='content_fingerprinting',
                base_price_usd=Decimal('0.10'),
                cryptocurrency=SupportedCryptocurrency.ETHEREUM,
                current_rate=Decimal('0.001'),
                rate_timestamp=datetime.utcnow()
            ),
            'copyright_registration': PaymentRate(
                service_type='copyright_registration',
                base_price_usd=Decimal('5.00'),
                cryptocurrency=SupportedCryptocurrency.ETHEREUM,
                current_rate=Decimal('0.001'),
                rate_timestamp=datetime.utcnow()
            ),
            'protection_monitoring': PaymentRate(
                service_type='protection_monitoring',
                base_price_usd=Decimal('10.00'),
                cryptocurrency=SupportedCryptocurrency.ETHEREUM,
                current_rate=Decimal('0.001'),
                rate_timestamp=datetime.utcnow()
            ),
            'automated_enforcement': PaymentRate(
                service_type='automated_enforcement',
                base_price_usd=Decimal('25.00'),
                cryptocurrency=SupportedCryptocurrency.ETHEREUM,
                current_rate=Decimal('0.001'),
                rate_timestamp=datetime.utcnow()
            )
        }
    
    async def create_payment_request(
        self,
        user_id: str,
        service_type: str,
        service_tier: ServiceTier,
        cryptocurrency: SupportedCryptocurrency,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentRequest:
        """
Create a new payment request"""
        try:
            # Get current pricing
            base_rate = self.service_rates.get(service_type)
            if not base_rate:
                raise ValueError(f"Unknown service type: {service_type}")
            
            # Apply tier multipliers
            tier_multipliers = {
                ServiceTier.BASIC: Decimal('1.0'),
                ServiceTier.PROFESSIONAL: Decimal('2.5'),
                ServiceTier.ENTERPRISE: Decimal('5.0'),
                ServiceTier.PREMIUM: Decimal('10.0')
            }
            
            base_amount = base_rate.base_price_usd * tier_multipliers[service_tier]
            
            # Get current cryptocurrency price
            async with self.price_oracle:
                crypto_price = await self.price_oracle.get_current_price(cryptocurrency)
                crypto_amount = base_amount / crypto_price
            
            # Generate payment address (simplified - in production would use HD wallets)
            payment_address = self._generate_payment_address(cryptocurrency)
            recipient_address = self.wallet_addresses.get(cryptocurrency, "")
            
            # Create payment request
            request = PaymentRequest(
                request_id=self._generate_request_id(),
                user_id=user_id,
                service_type=service_type,
                service_tier=service_tier,
                amount_usd=base_amount,
                cryptocurrency=cryptocurrency,
                amount_crypto=crypto_amount,
                recipient_address=recipient_address,
                payment_address=payment_address,
                metadata=metadata or {}
            )
            
            logger.info(f"Payment request created: {request.request_id}")
            return request
            
        except Exception as e:
            logger.error(f"Payment request creation failed: {e}")
            raise
    
    def _generate_request_id(self) -> str:
        """Generate unique payment request ID"""
        timestamp = int(datetime.utcnow().timestamp())
        random_part = secrets.token_hex(8)
        return f"pay_{timestamp}_{random_part}"
    
    def _generate_payment_address(self, cryptocurrency: SupportedCryptocurrency) -> str:
        """Generate unique payment address for request"""
        # In production, this would generate actual addresses using HD wallets
        # For now, return the main wallet address
        return self.wallet_addresses.get(cryptocurrency, "0x" + "0" * 40)
    
    async def check_payment_status(self, request: PaymentRequest) -> PaymentRequest:
        """Check and update payment status"""
        try:
            if request.status in [PaymentStatus.CONFIRMED, PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
                return request
            
            # Check if payment has expired
            if datetime.utcnow() > request.expires_at:
                request.status = PaymentStatus.EXPIRED
                return request
            
            # Check blockchain for payment
            if request.cryptocurrency in [SupportedCryptocurrency.ETHEREUM, SupportedCryptocurrency.USDC, SupportedCryptocurrency.USDT]:
                updated_request = await self._check_ethereum_payment(request)
            elif request.cryptocurrency == SupportedCryptocurrency.BITCOIN:
                updated_request = await self._check_bitcoin_payment(request)
            else:
                # For other cryptocurrencies, use appropriate network
                updated_request = await self._check_generic_payment(request)
            
            return updated_request
            
        except Exception as e:
            logger.error(f"Payment status check failed: {e}")
            return request
    
    async def _check_ethereum_payment(self, request: PaymentRequest) -> PaymentRequest:
        """Check Ethereum-based payment"""
        try:
            web3 = self.web3_clients.get('ethereum')
            if not web3:
                return request
            
            # Get latest transactions to payment address
            latest_block = web3.eth.block_number
            start_block = max(0, latest_block - 1000)  # Check last 1000 blocks
            
            # In production, would use event filters or transaction indexing
            # For now, simplified check
            
            if not request.transaction_hash:
                # Look for incoming transactions
                # This is simplified - production would use proper transaction monitoring
                request.status = PaymentStatus.PENDING
            else:
                # Check confirmation count
                try:
                    receipt = web3.eth.get_transaction_receipt(request.transaction_hash)
                    if receipt.status == 1:
                        current_block = web3.eth.block_number
                        confirmations = current_block - receipt.blockNumber
                        request.confirmation_count = confirmations
                        request.block_number = receipt.blockNumber
                        
                        if confirmations >= request.required_confirmations:
                            request.status = PaymentStatus.CONFIRMED
                        else:
                            request.status = PaymentStatus.PENDING
                    else:
                        request.status = PaymentStatus.FAILED
                except Exception:
                    request.status = PaymentStatus.PENDING
            
            return request
            
        except Exception as e:
            logger.error(f"Ethereum payment check failed: {e}")
            return request
    
    async def _check_bitcoin_payment(self, request: PaymentRequest) -> PaymentRequest:
        """Check Bitcoin payment"""
        try:
            # In production, would integrate with Bitcoin node or service like BlockCypher
            # For now, simplified implementation
            request.status = PaymentStatus.PENDING
            return request
            
        except Exception as e:
            logger.error(f"Bitcoin payment check failed: {e}")
            return request
    
    async def _check_generic_payment(self, request: PaymentRequest) -> PaymentRequest:
        """Check payment for other cryptocurrencies"""
        try:
            # Generic implementation for other blockchains
            request.status = PaymentStatus.PENDING
            return request
            
        except Exception as e:
            logger.error(f"Generic payment check failed: {e}")
            return request
    
    async def process_refund(
        self,
        request: PaymentRequest,
        refund_amount: Optional[Decimal] = None,
        reason: str = ""
    ) -> Tuple[bool, str]:
        """Process refund for a payment"""
        try:
            if request.status != PaymentStatus.CONFIRMED:
                return False, "Can only refund confirmed payments"
            
            refund_amount = refund_amount or request.amount_crypto
            
            # In production, would send actual refund transaction
            # For now, just update status
            request.status = PaymentStatus.REFUNDED
            request.metadata['refund_amount'] = str(refund_amount)
            request.metadata['refund_reason'] = reason
            request.metadata['refund_date'] = datetime.utcnow().isoformat()
            
            logger.info(f"Refund processed for request {request.request_id}")
            return True, "Refund processed successfully"
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return False, f"Refund failed: {e}"
    
    async def calculate_gas_fees(
        self,
        cryptocurrency: SupportedCryptocurrency,
        transaction_type: str = "transfer"
    ) -> Dict[str, Decimal]:
        """Calculate current gas fees for transaction"""
        try:
            fees = {
                'slow': Decimal('0'),
                'standard': Decimal('0'),
                'fast': Decimal('0')
            }
            
            if cryptocurrency in [SupportedCryptocurrency.ETHEREUM, SupportedCryptocurrency.USDC, SupportedCryptocurrency.USDT]:
                web3 = self.web3_clients.get('ethereum')
                if web3:
                    gas_price = web3.eth.gas_price
                    gas_limit = 21000 if transaction_type == "transfer" else 50000
                    
                    base_fee = Decimal(gas_price * gas_limit) / Decimal(10**18)  # Convert to ETH
                    
                    fees['slow'] = base_fee * Decimal('0.8')
                    fees['standard'] = base_fee
                    fees['fast'] = base_fee * Decimal('1.2')
            
            return fees
            
        except Exception as e:
            logger.error(f"Gas fee calculation failed: {e}")
            return {'slow': Decimal('0'), 'standard': Decimal('0'), 'fast': Decimal('0')}


# Export classes
__all__ = [
    'SupportedCryptocurrency',
    'PaymentStatus',
    'ServiceTier',
    'PaymentRate',
    'PaymentRequest',
    'PriceOracle',
    'PaymentProcessor'
]
