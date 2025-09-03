"""Cryptocurrency Payment Gateway
Advanced cryptocurrency payment processing system supporting Bitcoin, Ethereum, 
and stablecoins with automated conversion and multi-wallet management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64

logger = logging.getLogger(__name__)


class CryptoCurrency(Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    LITECOIN = "LTC"
    POLYGON = "MATIC"
    BINANCE_COIN = "BNB"


class NetworkType(Enum):
    """Blockchain networks"""
    BITCOIN_MAINNET = "bitcoin_mainnet"
    ETHEREUM_MAINNET = "ethereum_mainnet"
    POLYGON_MAINNET = "polygon_mainnet"
    BINANCE_SMART_CHAIN = "bsc_mainnet"
    LIGHTNING_NETWORK = "lightning"


class TransactionStatus(Enum):
    """Crypto transaction status"""
    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class CryptoWallet:
    """Cryptocurrency wallet configuration"""
    id: str
    currency: CryptoCurrency
    network: NetworkType
    address: str
    private_key_encrypted: Optional[str] = None
    public_key: Optional[str] = None
    balance: Decimal = Decimal('0')
    is_hot_wallet: bool = True
    is_active: bool = True
    created_at: datetime = None


@dataclass
class CryptoTransaction:
    """Cryptocurrency transaction"""
    id: str
    transaction_hash: Optional[str]
    currency: CryptoCurrency
    network: NetworkType
    amount: Decimal
    fee: Decimal
    from_address: str
    to_address: str
    status: TransactionStatus
    confirmations: int = 0
    required_confirmations: int = 6
    block_height: Optional[int] = None
    created_at: datetime = None
    confirmed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None


@dataclass
class CryptoExchangeRate:
    """Exchange rate for crypto to fiat"""
    base_currency: CryptoCurrency
    quote_currency: str  # Fiat currency (EUR, USD, etc.)
    rate: Decimal
    timestamp: datetime
    source: str  # Exchange/API source


@dataclass
class PaymentRequest:
    """Crypto payment request"""
    id: str
    customer_id: str
    amount_fiat: Decimal
    fiat_currency: str
    crypto_currency: CryptoCurrency
    crypto_amount: Decimal
    exchange_rate: Decimal
    payment_address: str
    qr_code_data: str
    expires_at: datetime
    status: str = "pending"
    created_at: datetime = None


class CryptoPaymentGateway:
    """Advanced cryptocurrency payment gateway"""
    
    # Network configurations
    NETWORK_CONFIGS = {
        NetworkType.BITCOIN_MAINNET: {
            "rpc_url": "https://bitcoin-mainnet-rpc.com",
            "explorer_url": "https://blockstream.info",
            "required_confirmations": 6,
            "average_block_time": 600  # 10 minutes
        },
        NetworkType.ETHEREUM_MAINNET: {
            "rpc_url": "https://mainnet.infura.io",
            "explorer_url": "https://etherscan.io",
            "required_confirmations": 12,
            "average_block_time": 15  # 15 seconds
        },
        NetworkType.POLYGON_MAINNET: {
            "rpc_url": "https://polygon-rpc.com",
            "explorer_url": "https://polygonscan.com",
            "required_confirmations": 20,
            "average_block_time": 2  # 2 seconds
        }
    }
    
    # Fee configurations (in percentage)
    CRYPTO_FEES = {
        CryptoCurrency.BITCOIN: Decimal('0.005'),  # 0.5%
        CryptoCurrency.ETHEREUM: Decimal('0.008'),  # 0.8%
        CryptoCurrency.USDC: Decimal('0.003'),     # 0.3%
        CryptoCurrency.USDT: Decimal('0.003'),     # 0.3%
        CryptoCurrency.DAI: Decimal('0.003'),      # 0.3%
        CryptoCurrency.LITECOIN: Decimal('0.004'), # 0.4%
        CryptoCurrency.POLYGON: Decimal('0.002'),  # 0.2%
        CryptoCurrency.BINANCE_COIN: Decimal('0.004')  # 0.4%
    }
    
    def __init__(self):
        self.wallets = {}
        self.transactions = {}
        self.payment_requests = {}
        self.exchange_rates = {}
        self.rate_cache_duration = timedelta(minutes=1)
        
    async def initialize_wallet(
        self,
        currency: CryptoCurrency,
        network: NetworkType,
        is_hot_wallet: bool = True
    ) -> CryptoWallet:
        """Initialize new cryptocurrency wallet"""
        try:
            wallet_id = str(uuid.uuid4())
            
            # Generate wallet address (simplified - in production use proper crypto libraries)
            wallet_address = await self._generate_wallet_address(currency, network)
            
            wallet = CryptoWallet(
                id=wallet_id,
                currency=currency,
                network=network,
                address=wallet_address,
                is_hot_wallet=is_hot_wallet,
                created_at=datetime.now()
            )
            
            self.wallets[wallet_id] = wallet
            
            logger.info(f"Crypto wallet initialized: {currency.value} on {network.value}")
            return wallet
            
        except Exception as e:
            logger.error(f"Error initializing wallet: {str(e)}")
            raise
            
    async def create_payment_request(
        self,
        customer_id: str,
        amount_fiat: Decimal,
        fiat_currency: str,
        crypto_currency: CryptoCurrency,
        expiry_minutes: int = 15
    ) -> PaymentRequest:
        """Create cryptocurrency payment request"""
        try:
            request_id = str(uuid.uuid4())
            
            # Get current exchange rate
            exchange_rate = await self._get_exchange_rate(crypto_currency, fiat_currency)
            
            # Calculate crypto amount
            crypto_amount = amount_fiat / exchange_rate.rate
            
            # Get or create payment wallet
            payment_wallet = await self._get_payment_wallet(crypto_currency)
            
            # Generate QR code data
            qr_data = await self._generate_payment_qr(
                payment_wallet.address,
                crypto_amount,
                crypto_currency
            )
            
            payment_request = PaymentRequest(
                id=request_id,
                customer_id=customer_id,
                amount_fiat=amount_fiat,
                fiat_currency=fiat_currency,
                crypto_currency=crypto_currency,
                crypto_amount=crypto_amount,
                exchange_rate=exchange_rate.rate,
                payment_address=payment_wallet.address,
                qr_code_data=qr_data,
                expires_at=datetime.now() + timedelta(minutes=expiry_minutes),
                created_at=datetime.now()
            )
            
            self.payment_requests[request_id] = payment_request
            
            # Start monitoring for payment
            asyncio.create_task(self._monitor_payment_request(request_id))
            
            logger.info(f"Payment request created: {request_id} for {amount_fiat} {fiat_currency}")
            return payment_request
            
        except Exception as e:
            logger.error(f"Error creating payment request: {str(e)}")
            raise
            
    async def process_crypto_payment(
        self,
        from_wallet_id: str,
        to_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        priority: str = "standard"
    ) -> CryptoTransaction:
        """Process outgoing cryptocurrency payment"""
        try:
            wallet = self.wallets.get(from_wallet_id)
            if not wallet:
                raise ValueError(f"Wallet not found: {from_wallet_id}")
                
            if wallet.currency != currency:
                raise ValueError(f"Currency mismatch: wallet {currency.value}, requested {wallet.currency.value}")
                
            # Check balance
            if wallet.balance < amount:
                raise ValueError(f"Insufficient balance: {wallet.balance} < {amount}")
                
            transaction_id = str(uuid.uuid4())
            
            # Calculate network fee
            network_fee = await self._calculate_network_fee(currency, amount, priority)
            
            # Create transaction
            transaction = CryptoTransaction(
                id=transaction_id,
                currency=currency,
                network=wallet.network,
                amount=amount,
                fee=network_fee,
                from_address=wallet.address,
                to_address=to_address,
                status=TransactionStatus.PENDING,
                required_confirmations=self.NETWORK_CONFIGS[wallet.network]["required_confirmations"],
                created_at=datetime.now()
            )
            
            # Submit transaction to network
            tx_hash = await self._submit_transaction(transaction, wallet)
            
            if tx_hash:
                transaction.transaction_hash = tx_hash
                transaction.status = TransactionStatus.CONFIRMING
                
                # Update wallet balance
                wallet.balance -= (amount + network_fee)
                
                # Start monitoring confirmations
                asyncio.create_task(self._monitor_transaction_confirmations(transaction_id))
            else:
                transaction.status = TransactionStatus.FAILED
                
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Crypto payment processed: {transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error processing crypto payment: {str(e)}")
            raise
            
    async def convert_crypto_to_fiat(
        self,
        crypto_amount: Decimal,
        crypto_currency: CryptoCurrency,
        fiat_currency: str
    ) -> Dict[str, Any]:
        """Convert cryptocurrency to fiat currency"""
        try:
            # Get current exchange rate
            exchange_rate = await self._get_exchange_rate(crypto_currency, fiat_currency)
            
            # Calculate fiat amount
            fiat_amount = crypto_amount * exchange_rate.rate
            
            # Calculate conversion fee
            conversion_fee = fiat_amount * self.CRYPTO_FEES.get(crypto_currency, Decimal('0.005'))
            net_fiat_amount = fiat_amount - conversion_fee
            
            conversion_result = {
                "crypto_amount": float(crypto_amount),
                "crypto_currency": crypto_currency.value,
                "fiat_amount": float(fiat_amount),
                "fiat_currency": fiat_currency,
                "exchange_rate": float(exchange_rate.rate),
                "conversion_fee": float(conversion_fee),
                "net_fiat_amount": float(net_fiat_amount),
                "rate_timestamp": exchange_rate.timestamp.isoformat(),
                "rate_source": exchange_rate.source
            }
            
            logger.info(f"Crypto conversion calculated: {crypto_amount} {crypto_currency.value} → {net_fiat_amount} {fiat_currency}")
            return conversion_result
            
        except Exception as e:
            logger.error(f"Error converting crypto to fiat: {str(e)}")
            return {}
            
    async def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """Get list of supported cryptocurrencies with details"""
        try:
            currencies = []
            
            for crypto in CryptoCurrency:
                # Get current rates for major fiat currencies
                try:
                    eur_rate = await self._get_exchange_rate(crypto, "EUR")
                    usd_rate = await self._get_exchange_rate(crypto, "USD")
                except:
                    eur_rate = None
                    usd_rate = None
                    
                currency_info = {
                    "symbol": crypto.value,
                    "name": self._get_currency_name(crypto),
                    "fee_percentage": float(self.CRYPTO_FEES.get(crypto, Decimal('0.005')) * 100),
                    "supported_networks": [net.value for net in self._get_supported_networks(crypto)],
                    "current_rates": {
                        "EUR": float(eur_rate.rate) if eur_rate else None,
                        "USD": float(usd_rate.rate) if usd_rate else None
                    },
                    "is_stablecoin": crypto in [CryptoCurrency.USDC, CryptoCurrency.USDT, CryptoCurrency.DAI]
                }
                
                currencies.append(currency_info)
                
            return currencies
            
        except Exception as e:
            logger.error(f"Error getting supported currencies: {str(e)}")
            return []
            
    async def estimate_transaction_time(
        self,
        currency: CryptoCurrency,
        network: NetworkType,
        priority: str = "standard"
    ) -> Dict[str, Any]:
        """Estimate transaction confirmation time"""
        try:
            config = self.NETWORK_CONFIGS.get(network, {})
            base_block_time = config.get("average_block_time", 600)
            required_confirmations = config.get("required_confirmations", 6)
            
            # Priority multipliers
            priority_multipliers = {
                "low": 2.0,
                "standard": 1.0,
                "high": 0.5,
                "urgent": 0.25
            }
            
            multiplier = priority_multipliers.get(priority, 1.0)
            estimated_seconds = base_block_time * required_confirmations * multiplier
            
            estimate = {
                "currency": currency.value,
                "network": network.value,
                "priority": priority,
                "estimated_seconds": int(estimated_seconds),
                "estimated_minutes": round(estimated_seconds / 60, 1),
                "required_confirmations": required_confirmations,
                "average_block_time_seconds": base_block_time
            }
            
            return estimate
            
        except Exception as e:
            logger.error(f"Error estimating transaction time: {str(e)}")
            return {}
            
    async def get_wallet_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet balance and transaction history"""
        try:
            wallet = self.wallets.get(wallet_id)
            if not wallet:
                raise ValueError(f"Wallet not found: {wallet_id}")
                
            # Get recent transactions
            wallet_transactions = [
                tx for tx in self.transactions.values()
                if (tx.from_address == wallet.address or tx.to_address == wallet.address)
            ]
            
            # Sort by creation time
            wallet_transactions.sort(key=lambda x: x.created_at, reverse=True)
            
            # Calculate pending amounts
            pending_outgoing = sum(
                tx.amount + tx.fee for tx in wallet_transactions
                if (tx.from_address == wallet.address and 
                    tx.status in [TransactionStatus.PENDING, TransactionStatus.CONFIRMING])
            )
            
            pending_incoming = sum(
                tx.amount for tx in wallet_transactions
                if (tx.to_address == wallet.address and 
                    tx.status in [TransactionStatus.PENDING, TransactionStatus.CONFIRMING])
            )
            
            balance_info = {
                "wallet_id": wallet_id,
                "currency": wallet.currency.value,
                "network": wallet.network.value,
                "address": wallet.address,
                "confirmed_balance": float(wallet.balance),
                "pending_outgoing": float(pending_outgoing),
                "pending_incoming": float(pending_incoming),
                "available_balance": float(wallet.balance - pending_outgoing),
                "total_transactions": len(wallet_transactions),
                "recent_transactions": [
                    {
                        "id": tx.id,
                        "hash": tx.transaction_hash,
                        "amount": float(tx.amount),
                        "fee": float(tx.fee),
                        "direction": "outgoing" if tx.from_address == wallet.address else "incoming",
                        "status": tx.status.value,
                        "confirmations": tx.confirmations,
                        "created_at": tx.created_at.isoformat() if tx.created_at else None
                    }
                    for tx in wallet_transactions[:10]  # Last 10 transactions
                ]
            }
            
            return balance_info
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            return {}
            
    async def setup_recurring_crypto_payment(
        self,
        customer_id: str,
        amount_fiat: Decimal,
        fiat_currency: str,
        crypto_currency: CryptoCurrency,
        frequency_days: int
    ) -> Dict[str, Any]:
        """Setup recurring cryptocurrency payment"""
        try:
            recurring_id = str(uuid.uuid4())
            
            recurring_setup = {
                "id": recurring_id,
                "customer_id": customer_id,
                "amount_fiat": float(amount_fiat),
                "fiat_currency": fiat_currency,
                "crypto_currency": crypto_currency.value,
                "frequency_days": frequency_days,
                "next_payment_date": (datetime.now() + timedelta(days=frequency_days)).isoformat(),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Store recurring payment config (in production, use database)
            if not hasattr(self, 'recurring_payments'):
                self.recurring_payments = {}
            self.recurring_payments[recurring_id] = recurring_setup
            
            # Schedule first payment
            asyncio.create_task(self._schedule_recurring_payment(recurring_id))
            
            logger.info(f"Recurring crypto payment setup: {recurring_id}")
            return recurring_setup
            
        except Exception as e:
            logger.error(f"Error setting up recurring payment: {str(e)}")
            return {}
            
    async def _generate_wallet_address(self, currency: CryptoCurrency, network: NetworkType) -> str:
        """Generate wallet address for given currency and network"""
        try:
            # Simplified address generation - in production use proper crypto libraries
            
            if currency == CryptoCurrency.BITCOIN:
                # Bitcoin address format
                return f"bc1q{uuid.uuid4().hex[:39]}"
            elif currency == CryptoCurrency.ETHEREUM or currency in [CryptoCurrency.USDC, CryptoCurrency.USDT, CryptoCurrency.DAI]:
                # Ethereum address format
                return f"0x{uuid.uuid4().hex[:32]}{uuid.uuid4().hex[:8]}"
            elif currency == CryptoCurrency.LITECOIN:
                # Litecoin address format
                return f"ltc1q{uuid.uuid4().hex[:39]}"
            else:
                # Generic format
                return f"{currency.value.lower()}_{uuid.uuid4().hex[:20]}"
                
        except Exception as e:
            logger.error(f"Error generating wallet address: {str(e)}")
            return f"addr_{uuid.uuid4().hex[:20]}"
            
    async def _get_exchange_rate(self, crypto: CryptoCurrency, fiat: str) -> CryptoExchangeRate:
        """Get current exchange rate for crypto to fiat"""
        try:
            rate_key = f"{crypto.value}_{fiat}"
            
            # Check cache
            if rate_key in self.exchange_rates:
                cached_rate = self.exchange_rates[rate_key]
                if datetime.now() - cached_rate.timestamp < self.rate_cache_duration:
                    return cached_rate
                    
            # Fetch new rate (simplified - in production use real exchange APIs)
            mock_rates = {
                f"{CryptoCurrency.BITCOIN.value}_EUR": Decimal('42000'),
                f"{CryptoCurrency.BITCOIN.value}_USD": Decimal('45000'),
                f"{CryptoCurrency.ETHEREUM.value}_EUR": Decimal('2800'),
                f"{CryptoCurrency.ETHEREUM.value}_USD": Decimal('3000'),
                f"{CryptoCurrency.USDC.value}_EUR": Decimal('0.92'),
                f"{CryptoCurrency.USDC.value}_USD": Decimal('1.00'),
                f"{CryptoCurrency.USDT.value}_EUR": Decimal('0.92'),
                f"{CryptoCurrency.USDT.value}_USD": Decimal('1.00'),
                f"{CryptoCurrency.DAI.value}_EUR": Decimal('0.92'),
                f"{CryptoCurrency.DAI.value}_USD": Decimal('1.00'),
            }
            
            rate_value = mock_rates.get(rate_key, Decimal('1.0'))
            
            exchange_rate = CryptoExchangeRate(
                base_currency=crypto,
                quote_currency=fiat,
                rate=rate_value,
                timestamp=datetime.now(),
                source="mock_api"
            )
            
            # Cache the rate
            self.exchange_rates[rate_key] = exchange_rate
            
            return exchange_rate
            
        except Exception as e:
            logger.error(f"Error getting exchange rate: {str(e)}")
            # Return fallback rate
            return CryptoExchangeRate(
                base_currency=crypto,
                quote_currency=fiat,
                rate=Decimal('1.0'),
                timestamp=datetime.now(),
                source="fallback"
            )
            
    async def _get_payment_wallet(self, currency: CryptoCurrency) -> CryptoWallet:
        """Get or create payment wallet for currency"""
        try:
            # Find existing hot wallet for currency
            for wallet in self.wallets.values():
                if (wallet.currency == currency and 
                    wallet.is_hot_wallet and 
                    wallet.is_active):
                    return wallet
                    
            # Create new payment wallet
            network = self._get_default_network(currency)
            return await self.initialize_wallet(currency, network, is_hot_wallet=True)
            
        except Exception as e:
            logger.error(f"Error getting payment wallet: {str(e)}")
            raise
            
    def _get_default_network(self, currency: CryptoCurrency) -> NetworkType:
        """Get default network for currency"""
        network_map = {
            CryptoCurrency.BITCOIN: NetworkType.BITCOIN_MAINNET,
            CryptoCurrency.ETHEREUM: NetworkType.ETHEREUM_MAINNET,
            CryptoCurrency.USDC: NetworkType.ETHEREUM_MAINNET,
            CryptoCurrency.USDT: NetworkType.ETHEREUM_MAINNET,
            CryptoCurrency.DAI: NetworkType.ETHEREUM_MAINNET,
            CryptoCurrency.POLYGON: NetworkType.POLYGON_MAINNET,
            CryptoCurrency.BINANCE_COIN: NetworkType.BINANCE_SMART_CHAIN
        }
        return network_map.get(currency, NetworkType.ETHEREUM_MAINNET)
        
    async def _generate_payment_qr(self, address: str, amount: Decimal, currency: CryptoCurrency) -> str:
        """Generate QR code data for payment"""
        try:
            # Standard cryptocurrency URI format
            if currency == CryptoCurrency.BITCOIN:
                qr_data = f"bitcoin:{address}?amount={amount}"
            elif currency == CryptoCurrency.ETHEREUM:
                qr_data = f"ethereum:{address}?value={amount}"
            else:
                qr_data = f"{currency.value.lower()}:{address}?amount={amount}"
                
            return qr_data
            
        except Exception as e:
            logger.error(f"Error generating payment QR: {str(e)}")
            return f"{address}?amount={amount}"
            
    async def _monitor_payment_request(self, request_id: str):
        """Monitor payment request for incoming payments"""
        try:
            request = self.payment_requests.get(request_id)
            if not request:
                return
                
            # Monitor for timeout
            while datetime.now() < request.expires_at and request.status == "pending":
                # Check for incoming payments (simplified)
                # In production, monitor blockchain for payments to the address
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            # Mark as expired if not paid
            if request.status == "pending":
                request.status = "expired"
                
        except Exception as e:
            logger.error(f"Error monitoring payment request: {str(e)}")
            
    async def _calculate_network_fee(self, currency: CryptoCurrency, amount: Decimal, priority: str) -> Decimal:
        """Calculate network transaction fee"""
        try:
            # Base fees by currency (simplified)
            base_fees = {
                CryptoCurrency.BITCOIN: Decimal('0.0001'),
                CryptoCurrency.ETHEREUM: Decimal('0.002'),
                CryptoCurrency.USDC: Decimal('0.001'),
                CryptoCurrency.USDT: Decimal('0.001'),
                CryptoCurrency.DAI: Decimal('0.001'),
                CryptoCurrency.LITECOIN: Decimal('0.00001'),
                CryptoCurrency.POLYGON: Decimal('0.0001'),
                CryptoCurrency.BINANCE_COIN: Decimal('0.0005')
            }
            
            # Priority multipliers
            priority_multipliers = {
                "low": Decimal('0.5'),
                "standard": Decimal('1.0'),
                "high": Decimal('2.0'),
                "urgent": Decimal('5.0')
            }
            
            base_fee = base_fees.get(currency, Decimal('0.001'))
            multiplier = priority_multipliers.get(priority, Decimal('1.0'))
            
            return base_fee * multiplier
            
        except Exception as e:
            logger.error(f"Error calculating network fee: {str(e)}")
            return Decimal('0.001')
            
    async def _submit_transaction(self, transaction: CryptoTransaction, wallet: CryptoWallet) -> Optional[str]:
        """Submit transaction to blockchain network"""
        try:
            # Simplified transaction submission - in production use blockchain APIs
            # This would integrate with Bitcoin Core, Ethereum clients, etc.
            
            # Simulate transaction submission
            await asyncio.sleep(0.5)
            
            # Generate mock transaction hash
            tx_hash = hashlib.sha256(
                f"{transaction.id}{transaction.amount}{datetime.now()}".encode()
            ).hexdigest()
            
            logger.info(f"Transaction submitted: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Error submitting transaction: {str(e)}")
            return None
            
    async def _monitor_transaction_confirmations(self, transaction_id: str):
        """Monitor transaction confirmations"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                return
                
            # Simulate confirmation monitoring
            while transaction.confirmations < transaction.required_confirmations:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Simulate new confirmation
                transaction.confirmations += 1
                
                if transaction.confirmations >= transaction.required_confirmations:
                    transaction.status = TransactionStatus.CONFIRMED
                    transaction.confirmed_at = datetime.now()
                    break
                    
        except Exception as e:
            logger.error(f"Error monitoring confirmations: {str(e)}")
            
    def _get_currency_name(self, currency: CryptoCurrency) -> str:
        """Get full name for cryptocurrency"""
        names = {
            CryptoCurrency.BITCOIN: "Bitcoin",
            CryptoCurrency.ETHEREUM: "Ethereum",
            CryptoCurrency.USDC: "USD Coin",
            CryptoCurrency.USDT: "Tether",
            CryptoCurrency.DAI: "Dai Stablecoin",
            CryptoCurrency.LITECOIN: "Litecoin",
            CryptoCurrency.POLYGON: "Polygon",
            CryptoCurrency.BINANCE_COIN: "Binance Coin"
        }
        return names.get(currency, currency.value)
        
    def _get_supported_networks(self, currency: CryptoCurrency) -> List[NetworkType]:
        """Get supported networks for currency"""
        network_support = {
            CryptoCurrency.BITCOIN: [NetworkType.BITCOIN_MAINNET, NetworkType.LIGHTNING_NETWORK],
            CryptoCurrency.ETHEREUM: [NetworkType.ETHEREUM_MAINNET],
            CryptoCurrency.USDC: [NetworkType.ETHEREUM_MAINNET, NetworkType.POLYGON_MAINNET],
            CryptoCurrency.USDT: [NetworkType.ETHEREUM_MAINNET, NetworkType.POLYGON_MAINNET, NetworkType.BINANCE_SMART_CHAIN],
            CryptoCurrency.DAI: [NetworkType.ETHEREUM_MAINNET, NetworkType.POLYGON_MAINNET],
            CryptoCurrency.POLYGON: [NetworkType.POLYGON_MAINNET],
            CryptoCurrency.BINANCE_COIN: [NetworkType.BINANCE_SMART_CHAIN]
        }
        return network_support.get(currency, [NetworkType.ETHEREUM_MAINNET])
        
    async def _schedule_recurring_payment(self, recurring_id: str):
        """Schedule recurring crypto payment"""
        try:
            # Implementation for recurring payment scheduling
            # This would integrate with a job scheduler in production
            logger.info(f"Recurring payment scheduled: {recurring_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling recurring payment: {str(e)}")


# Global crypto gateway instance
crypto_gateway = CryptoPaymentGateway()


async def create_crypto_payment(
    customer_id: str,
    amount_fiat: Decimal,
    fiat_currency: str,
    crypto_currency: CryptoCurrency
) -> PaymentRequest:
    """Global function to create crypto payment request"""
    return await crypto_gateway.create_payment_request(
        customer_id=customer_id,
        amount_fiat=amount_fiat,
        fiat_currency=fiat_currency,
        crypto_currency=crypto_currency
    )


async def get_crypto_rates(currencies: List[CryptoCurrency], fiat: str = "EUR") -> Dict[str, Any]:
    """Get current cryptocurrency exchange rates"""
    rates = {}
    for crypto in currencies:
        try:
            rate = await crypto_gateway._get_exchange_rate(crypto, fiat)
            rates[crypto.value] = {
                "rate": float(rate.rate),
                "timestamp": rate.timestamp.isoformat(),
                "source": rate.source
            }
        except Exception as e:
            logger.error(f"Error getting rate for {crypto.value}: {str(e)}")
            rates[crypto.value] = {"error": str(e)}
            
    return rates