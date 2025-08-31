"""₿ Cryptocurrency Payments Processor
==================================

Advanced cryptocurrency payment processor supporting multiple digital currencies
including Bitcoin, Ethereum, and popular stablecoins with DeFi integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import hashlib
import hmac
import json

logger = logging.getLogger(__name__)


class CryptoCurrency(Enum):
    """Supported cryptocurrencies"""    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    BUSD = "BUSD"
    MATIC = "MATIC"
    BNB = "BNB"
    ADA = "ADA"
    SOL = "SOL"
    AVAX = "AVAX"
    DOT = "DOT"
    LINK = "LINK"
    UNI = "UNI"
    SUSHI = "SUSHI"


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"  # Binance Smart Chain
    SOLANA = "solana"
    AVALANCHE = "avalanche"
    CARDANO = "cardano"
    POLKADOT = "polkadot"


class TransactionStatus(Enum):
    """Cryptocurrency transaction status"""    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WalletType(Enum):
    """Wallet types"""    HOT_WALLET = "hot"
    COLD_WALLET = "cold"
    MULTI_SIG = "multisig"
    HARDWARE = "hardware"


@dataclass
class CryptoWallet:
    """Cryptocurrency wallet information"""    address: str
    currency: CryptoCurrency
    network: BlockchainNetwork
    balance: Decimal
    wallet_type: WalletType
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class CryptoTransaction:
    """Cryptocurrency transaction details"""    id: str
    from_address: str
    to_address: str
    amount: Decimal
    currency: CryptoCurrency
    network: BlockchainNetwork
    status: TransactionStatus
    transaction_hash: Optional[str]
    block_number: Optional[int]
    confirmations: int
    gas_fee: Decimal
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    memo: Optional[str] = None


@dataclass
class ExchangeRate:
    """Cryptocurrency exchange rate"""    base_currency: CryptoCurrency
    quote_currency: str  # Fiat currency
    rate: Decimal
    timestamp: datetime
    source: str = "coinbase"


class CryptoPaymentsProcessor:
    """    Advanced cryptocurrency payments processor
    
    Handles multiple cryptocurrencies across different blockchain networks
    with support for stablecoins, DeFi integration, and automated conversions.
    """    
    def __init__(
        self,
        api_keys: Dict[str, str],
        webhook_secret: Optional[str] = None,
        testnet: bool = False
    ):
        """Initialize cryptocurrency processor"""        self.api_keys = api_keys
        self.webhook_secret = webhook_secret
        self.testnet = testnet
        self.logger = logging.getLogger(__name__)
        
        # Network configurations
        self.network_configs = {
            BlockchainNetwork.BITCOIN: {
                "confirmations_required": 6,
                "average_block_time": 600,  # 10 minutes
                "fee_estimate_blocks": 6
            },
            BlockchainNetwork.ETHEREUM: {
                "confirmations_required": 12,
                "average_block_time": 12,  # 12 seconds
                "fee_estimate_blocks": 1
            },
            BlockchainNetwork.POLYGON: {
                "confirmations_required": 20,
                "average_block_time": 2,  # 2 seconds
                "fee_estimate_blocks": 1
            },
            BlockchainNetwork.BSC: {
                "confirmations_required": 15,
                "average_block_time": 3,  # 3 seconds
                "fee_estimate_blocks": 1
            }
        }
        
        # Stablecoin contracts (mainnet addresses)
        self.stablecoin_contracts = {
            "USDC": {
                BlockchainNetwork.ETHEREUM: "0xA0b86a33E6411A06f01b7A52b6e48C7E73C5c5a",
                BlockchainNetwork.POLYGON: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
            },
            "USDT": {
                BlockchainNetwork.ETHEREUM: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                BlockchainNetwork.POLYGON: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
            }
        }
    
    async def create_wallet(
        self,
        currency: CryptoCurrency,
        network: BlockchainNetwork,
        wallet_type: WalletType = WalletType.HOT_WALLET
    ) -> CryptoWallet:
        """Create a new cryptocurrency wallet"""        try:
            # Generate wallet address (mock implementation)
            if network == BlockchainNetwork.BITCOIN:
                # Generate a proper length Bitcoin address
                hex_part = (uuid.uuid4().hex + uuid.uuid4().hex)[:39]
                address = f"bc1{hex_part}"
            elif network == BlockchainNetwork.ETHEREUM:
                address = f"0x{uuid.uuid4().hex[:40]}"
            elif network == BlockchainNetwork.SOLANA:
                # Generate proper length Solana address
                hex_part = (uuid.uuid4().hex + uuid.uuid4().hex)[:44] 
                address = hex_part
            else:
                address = f"0x{uuid.uuid4().hex[:40]}"
            
            wallet = CryptoWallet(
                address=address,
                currency=currency,
                network=network,
                balance=Decimal("0"),
                wallet_type=wallet_type
            )
            
            self.logger.info(f"Created {currency.value} wallet: {address}")
            return wallet
            
        except Exception as e:
            self.logger.error(f"Failed to create crypto wallet: {e}")
            raise
    
    async def get_balance(
        self,
        address: str,
        currency: CryptoCurrency,
        network: BlockchainNetwork
    ) -> Decimal:
        """Get wallet balance"""        try:
            # Simulate API call to blockchain
            await asyncio.sleep(0.1)
            
            # Mock balance (in production, query actual blockchain)
            import random
            balance = Decimal(str(random.uniform(0, 100))).quantize(
                Decimal("0.00000001"), rounding=ROUND_HALF_UP
            )
            
            return balance
            
        except Exception as e:
            self.logger.error(f"Failed to get balance for {address}: {e}")
            return Decimal("0")
    
    async def estimate_fee(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        network: BlockchainNetwork,
        priority: str = "medium"
    ) -> Decimal:
        """Estimate transaction fee"""        try:
            # Fee estimation based on network
            if network == BlockchainNetwork.BITCOIN:
                # BTC fees in satoshis per byte
                base_fee = Decimal("0.00001000")  # ~$0.40 at $40k BTC
                if priority == "high":
                    return base_fee * Decimal("2")
                elif priority == "low":
                    return base_fee * Decimal("0.5")
                else:
                    return base_fee
                    
            elif network == BlockchainNetwork.ETHEREUM:
                # ETH fees in gwei
                base_fee = Decimal("0.002")  # ~$4 at $2k ETH
                if priority == "high":
                    return base_fee * Decimal("3")
                elif priority == "low":
                    return base_fee * Decimal("0.7")
                else:
                    return base_fee
                    
            elif network == BlockchainNetwork.POLYGON:
                # MATIC fees are very low
                return Decimal("0.001")  # ~$0.001
                
            elif network == BlockchainNetwork.BSC:
                # BNB fees
                return Decimal("0.0005")  # ~$0.20
                
            else:
                return Decimal("0.001")  # Default low fee
                
        except Exception as e:
            self.logger.error(f"Failed to estimate fee: {e}")
            return Decimal("0.001")  # Fallback fee
    
    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        network: BlockchainNetwork,
        private_key: str,
        memo: Optional[str] = None,
        priority: str = "medium"
    ) -> CryptoTransaction:
        """Send cryptocurrency transaction"""        try:
            # Estimate fee
            gas_fee = await self.estimate_fee(
                from_address, to_address, amount, currency, network, priority
            )
            
            # Create transaction
            transaction_id = f"tx_{uuid.uuid4().hex}"
            transaction_hash = f"0x{uuid.uuid4().hex[:64]}"
            
            transaction = CryptoTransaction(
                id=transaction_id,
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                currency=currency,
                network=network,
                status=TransactionStatus.PENDING,
                transaction_hash=transaction_hash,
                block_number=None,
                confirmations=0,
                gas_fee=gas_fee,
                created_at=datetime.now(),
                memo=memo
            )
            
            # Simulate broadcasting transaction
            await asyncio.sleep(0.2)
            
            # Update status to confirming
            transaction.status = TransactionStatus.CONFIRMING
            
            self.logger.info(f"Sent {currency.value} transaction: {transaction_hash}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Failed to send transaction: {e}")
            raise
    
    async def get_transaction_status(
        self,
        transaction_hash: str,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Get transaction status from blockchain"""        try:
            # Simulate blockchain query
            await asyncio.sleep(0.1)
            
            # Mock transaction status
            import random
            confirmations = random.randint(0, 20)
            required_confirmations = self.network_configs[network]["confirmations_required"]
            
            if confirmations >= required_confirmations:
                status = TransactionStatus.CONFIRMED
            elif confirmations > 0:
                status = TransactionStatus.CONFIRMING
            else:
                status = TransactionStatus.PENDING
            
            return {
                "transaction_hash": transaction_hash,
                "status": status.value,
                "confirmations": confirmations,
                "required_confirmations": required_confirmations,
                "block_number": random.randint(1000000, 2000000) if confirmations > 0 else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction status: {e}")
            return {"error": str(e)}
    
    async def get_exchange_rate(
        self,
        crypto_currency: CryptoCurrency,
        fiat_currency: str = "USD"
    ) -> ExchangeRate:
        """Get current cryptocurrency exchange rate"""        try:
            # Mock exchange rates (in production, use real API like CoinGecko)
            mock_rates = {
                CryptoCurrency.BITCOIN: Decimal("42000.50"),
                CryptoCurrency.ETHEREUM: Decimal("2500.75"),
                CryptoCurrency.USDC: Decimal("1.00"),
                CryptoCurrency.USDT: Decimal("1.00"),
                CryptoCurrency.DAI: Decimal("1.00"),
                CryptoCurrency.MATIC: Decimal("0.85"),
                CryptoCurrency.BNB: Decimal("320.40"),
                CryptoCurrency.ADA: Decimal("0.48"),
                CryptoCurrency.SOL: Decimal("95.20"),
                CryptoCurrency.AVAX: Decimal("18.50"),
                CryptoCurrency.DOT: Decimal("6.75"),
                CryptoCurrency.LINK: Decimal("15.20"),
                CryptoCurrency.UNI: Decimal("8.40"),
                CryptoCurrency.SUSHI: Decimal("1.25")
            }
            
            rate = mock_rates.get(crypto_currency, Decimal("1.00"))
            
            # Add small random variation
            import random
            variation = Decimal(str(random.uniform(-0.02, 0.02)))
            rate = rate + (rate * variation)
            rate = rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            return ExchangeRate(
                base_currency=crypto_currency,
                quote_currency=fiat_currency,
                rate=rate,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get exchange rate: {e}")
            raise
    
    async def convert_crypto(
        self,
        from_currency: CryptoCurrency,
        to_currency: CryptoCurrency,
        amount: Decimal,
        slippage_tolerance: Decimal = Decimal("0.005")  # 0.5%
    ) -> Dict[str, Any]:
        """Convert between cryptocurrencies using DEX"""        try:
            # Get exchange rates
            from_rate = await self.get_exchange_rate(from_currency)
            to_rate = await self.get_exchange_rate(to_currency)
            
            # Calculate conversion rate
            conversion_rate = from_rate.rate / to_rate.rate
            converted_amount = amount * conversion_rate
            
            # Apply slippage
            min_received = converted_amount * (Decimal("1") - slippage_tolerance)
            
            # Simulate DEX fees (0.3% typical for Uniswap)
            dex_fee = amount * Decimal("0.003")
            
            conversion_id = f"conv_{uuid.uuid4().hex[:16]}"
            
            return {
                "success": True,
                "conversion_id": conversion_id,
                "from_currency": from_currency.value,
                "to_currency": to_currency.value,
                "input_amount": float(amount),
                "output_amount": float(converted_amount),
                "min_received": float(min_received),
                "conversion_rate": float(conversion_rate),
                "dex_fee": float(dex_fee),
                "slippage_tolerance": float(slippage_tolerance),
                "estimated_time": "30 seconds"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to convert crypto: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_payment_request(
        self,
        amount: Decimal,
        currency: CryptoCurrency,
        network: BlockchainNetwork,
        recipient_address: str,
        expiry_minutes: int = 30,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a cryptocurrency payment request"""        try:
            request_id = f"req_{uuid.uuid4().hex[:16]}"
            expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
            
            # Generate QR code data (in production, use actual QR library)
            if network == BlockchainNetwork.BITCOIN:
                payment_uri = f"bitcoin:{recipient_address}?amount={amount}"
            elif network == BlockchainNetwork.ETHEREUM:
                payment_uri = f"ethereum:{recipient_address}?value={amount * Decimal('1e18')}"
            else:
                payment_uri = f"{network.value}:{recipient_address}?amount={amount}"
            
            if memo:
                payment_uri += f"&message={memo}"
            
            return {
                "request_id": request_id,
                "amount": float(amount),
                "currency": currency.value,
                "network": network.value,
                "recipient_address": recipient_address,
                "payment_uri": payment_uri,
                "qr_code_data": payment_uri,
                "expiry_time": expiry_time.isoformat(),
                "memo": memo,
                "status": "pending"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create payment request: {e}")
            return {"error": str(e)}
    
    async def verify_payment(
        self,
        payment_request_id: str,
        transaction_hash: str,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Verify a payment against a payment request"""        try:
            # Get transaction details
            tx_status = await self.get_transaction_status(transaction_hash, network)
            
            if tx_status.get("status") == "confirmed":
                return {
                    "verified": True,
                    "payment_request_id": payment_request_id,
                    "transaction_hash": transaction_hash,
                    "confirmations": tx_status.get("confirmations", 0),
                    "verified_at": datetime.now().isoformat()
                }
            else:
                return {
                    "verified": False,
                    "reason": "Transaction not yet confirmed",
                    "confirmations": tx_status.get("confirmations", 0),
                    "required_confirmations": tx_status.get("required_confirmations", 1)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to verify payment: {e}")
            return {"verified": False, "error": str(e)}
    
    async def handle_webhook(self, headers: Dict[str, str], body: str) -> Dict[str, Any]:
        """Handle cryptocurrency webhook events"""        try:
            # Verify webhook signature
            if not self._verify_webhook_signature(headers, body):
                return {"success": False, "error": "Invalid webhook signature"}
            
            event = json.loads(body)
            event_type = event.get("type")
            
            # Handle different event types
            if event_type == "transaction.confirmed":
                return await self._handle_transaction_confirmed(event["data"])
            elif event_type == "transaction.failed":
                return await self._handle_transaction_failed(event["data"])
            elif event_type == "wallet.deposit":
                return await self._handle_wallet_deposit(event["data"])
            elif event_type == "price.alert":
                return await self._handle_price_alert(event["data"])
            else:
                return {"success": True, "message": f"Unhandled event: {event_type}"}
                
        except Exception as e:
            self.logger.error(f"Crypto webhook handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _verify_webhook_signature(self, headers: Dict[str, str], body: str) -> bool:
        """Verify cryptocurrency webhook signature"""        try:
            if not self.webhook_secret:
                return True  # Skip verification if no secret configured
            
            signature = headers.get("X-Signature", "") or headers.get("X-Hub-Signature-256", "")
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Crypto signature verification failed: {e}")
            return False
    
    async def _handle_transaction_confirmed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction confirmation event"""        tx_hash = data.get("transaction_hash")
        self.logger.info(f"Cryptocurrency transaction confirmed: {tx_hash}")
        return {"success": True, "action": "transaction_confirmed"}
    
    async def _handle_transaction_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction failure event"""        tx_hash = data.get("transaction_hash")
        self.logger.warning(f"Cryptocurrency transaction failed: {tx_hash}")
        return {"success": True, "action": "transaction_failed"}
    
    async def _handle_wallet_deposit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle wallet deposit event"""        address = data.get("address")
        amount = data.get("amount")
        currency = data.get("currency")
        self.logger.info(f"Wallet {address} received {amount} {currency}")
        return {"success": True, "action": "wallet_deposit"}
    
    async def _handle_price_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price alert event"""        currency = data.get("currency")
        price = data.get("current_price")
        self.logger.info(f"Price alert for {currency}: ${price}")
        return {"success": True, "action": "price_alert"}
    
    def get_supported_currencies(self) -> Dict[CryptoCurrency, Dict[str, Any]]:
        """Get all supported cryptocurrencies"""        return {
            currency: {
                "name": currency.value,
                "networks": self._get_supported_networks(currency),
                "decimals": self._get_currency_decimals(currency),
                "type": self._get_currency_type(currency)
            }
            for currency in CryptoCurrency
        }
    
    def _get_supported_networks(self, currency: CryptoCurrency) -> List[str]:
        """Get supported networks for a currency"""        if currency == CryptoCurrency.BITCOIN:
            return [BlockchainNetwork.BITCOIN.value]
        elif currency in [CryptoCurrency.ETHEREUM, CryptoCurrency.USDC, CryptoCurrency.USDT, CryptoCurrency.DAI]:
            return [BlockchainNetwork.ETHEREUM.value, BlockchainNetwork.POLYGON.value]
        elif currency == CryptoCurrency.BNB:
            return [BlockchainNetwork.BSC.value]
        elif currency == CryptoCurrency.SOL:
            return [BlockchainNetwork.SOLANA.value]
        elif currency == CryptoCurrency.ADA:
            return [BlockchainNetwork.CARDANO.value]
        elif currency == CryptoCurrency.DOT:
            return [BlockchainNetwork.POLKADOT.value]
        else:
            return [BlockchainNetwork.ETHEREUM.value]
    
    def _get_currency_decimals(self, currency: CryptoCurrency) -> int:
        """Get decimal places for a currency"""        if currency == CryptoCurrency.BITCOIN:
            return 8
        else:
            return 18  # Most ERC-20 tokens use 18 decimals
    
    def _get_currency_type(self, currency: CryptoCurrency) -> str:
        """Get currency type"""        stablecoins = [CryptoCurrency.USDC, CryptoCurrency.USDT, CryptoCurrency.DAI, CryptoCurrency.BUSD]
        if currency in stablecoins:
            return "stablecoin"
        elif currency in [CryptoCurrency.BITCOIN, CryptoCurrency.ETHEREUM]:
            return "native"
        else:
            return "token"


# Export the main class
__all__ = [
    "CryptoPaymentsProcessor",
    "CryptoWallet",
    "CryptoTransaction",
    "ExchangeRate",
    "CryptoCurrency",
    "BlockchainNetwork"
]