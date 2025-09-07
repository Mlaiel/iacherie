"""
Crypto Payment Core - Advanced Cryptocurrency Payment Processing System
======================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for cryptocurrency payments, blockchain integration,
DeFi protocols, and multi-chain transaction processing.
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

class CryptoCurrency(Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    USDC = "USDC"
    USDT = "USDT"
    MATIC = "MATIC"
    BNB = "BNB"
    CARDANO = "ADA"
    SOLANA = "SOL"
    AVALANCHE = "AVAX"
    POLYGON = "POLYGON"

class Blockchain(Enum):
    """Supported blockchain networks"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "bsc"
    CARDANO = "cardano"
    SOLANA = "solana"
    AVALANCHE = "avalanche"

class TransactionStatus(Enum):
    """Crypto transaction status"""
    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class WalletType(Enum):
    """Wallet types"""
    HOT_WALLET = "hot_wallet"
    COLD_WALLET = "cold_wallet"
    MULTISIG = "multisig"
    HARDWARE = "hardware"
    CUSTODIAL = "custodial"

class DeFiProtocol(Enum):
    """DeFi protocols"""
    UNISWAP = "uniswap"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    AAVE = "aave"
    COMPOUND = "compound"
    YEARN = "yearn"

@dataclass
class CryptoWallet:
    """Cryptocurrency wallet"""
    wallet_id: str
    wallet_type: WalletType
    blockchain: Blockchain
    address: str
    private_key_encrypted: Optional[str]
    public_key: str
    balance: Decimal
    currency: CryptoCurrency
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_synced: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CryptoTransaction:
    """Cryptocurrency transaction"""
    transaction_id: str
    blockchain: Blockchain
    from_address: str
    to_address: str
    amount: Decimal
    currency: CryptoCurrency
    gas_fee: Decimal
    gas_limit: int
    gas_price: Decimal
    transaction_hash: Optional[str]
    block_number: Optional[int]
    confirmation_count: int = 0
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    customer_id: Optional[str] = None
    reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CryptoPrice:
    """Cryptocurrency price data"""
    currency: CryptoCurrency
    price_usd: Decimal
    price_btc: Decimal
    market_cap: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "coinbase"

@dataclass
class DeFiPool:
    """DeFi liquidity pool"""
    pool_id: str
    protocol: DeFiProtocol
    token_a: CryptoCurrency
    token_b: CryptoCurrency
    token_a_amount: Decimal
    token_b_amount: Decimal
    total_liquidity: Decimal
    apr: Decimal
    fees_24h: Decimal
    volume_24h: Decimal
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

class BlockchainConnector:
    """Blockchain network connector"""
    
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.rpc_endpoints = self._get_rpc_endpoints()
        self.explorer_urls = self._get_explorer_urls()
        self.gas_settings = self._get_gas_settings()
        
        logger.info(f"Blockchain Connector initialized for {blockchain.value}")

    def _get_rpc_endpoints(self) -> Dict[str, str]:
        """Get RPC endpoints for blockchain"""
        endpoints = {
            Blockchain.ETHEREUM: "https://mainnet.infura.io/v3/your-project-id",
            Blockchain.POLYGON: "https://polygon-rpc.com",
            Blockchain.BINANCE_SMART_CHAIN: "https://bsc-dataseed.binance.org",
            Blockchain.BITCOIN: "https://bitcoin-rpc.endpoint.com",
            Blockchain.SOLANA: "https://api.mainnet-beta.solana.com",
            Blockchain.AVALANCHE: "https://api.avax.network/ext/bc/C/rpc",
            Blockchain.CARDANO: "https://cardano-mainnet.blockfrost.io/api/v0"
        }
        return {self.blockchain.value: endpoints.get(self.blockchain, "")}

    def _get_explorer_urls(self) -> Dict[str, str]:
        """Get blockchain explorer URLs"""
        explorers = {
            Blockchain.ETHEREUM: "https://etherscan.io",
            Blockchain.POLYGON: "https://polygonscan.com",
            Blockchain.BINANCE_SMART_CHAIN: "https://bscscan.com",
            Blockchain.BITCOIN: "https://blockstream.info",
            Blockchain.SOLANA: "https://explorer.solana.com",
            Blockchain.AVALANCHE: "https://snowtrace.io",
            Blockchain.CARDANO: "https://cardanoscan.io"
        }
        return {self.blockchain.value: explorers.get(self.blockchain, "")}

    def _get_gas_settings(self) -> Dict[str, Any]:
        """Get gas settings for blockchain"""
        gas_settings = {
            Blockchain.ETHEREUM: {
                "gas_limit": 21000,
                "gas_price_gwei": 20,
                "priority_fee_gwei": 2
            },
            Blockchain.POLYGON: {
                "gas_limit": 21000,
                "gas_price_gwei": 30,
                "priority_fee_gwei": 30
            },
            Blockchain.BINANCE_SMART_CHAIN: {
                "gas_limit": 21000,
                "gas_price_gwei": 5,
                "priority_fee_gwei": 1
            }
        }
        return gas_settings.get(self.blockchain, {"gas_limit": 21000, "gas_price_gwei": 20})

    async def get_balance(self, address: str, currency: CryptoCurrency) -> Decimal:
        """Get balance for address"""
        try:
            # Mock balance retrieval - would integrate with actual blockchain RPC
            mock_balances = {
                "0x742d35Cc6589C2D8B7bfd80D8A4E4D78d1aE5469": {
                    CryptoCurrency.ETHEREUM: Decimal('1.5'),
                    CryptoCurrency.USDC: Decimal('1000.0')
                }
            }
            
            address_balances = mock_balances.get(address, {})
            balance = address_balances.get(currency, Decimal('0'))
            
            logger.info(f"Balance retrieved for {address}: {balance} {currency.value}")
            return balance
            
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return Decimal('0')

    async def send_transaction(self, transaction: CryptoTransaction) -> Dict[str, Any]:
        """Send transaction to blockchain"""
        try:
            # Validate transaction
            validation_result = await self._validate_transaction(transaction)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "transaction_hash": None
                }
            
            # Calculate gas fees
            gas_cost = await self._calculate_gas_fees(transaction)
            transaction.gas_fee = gas_cost["total_fee"]
            transaction.gas_limit = gas_cost["gas_limit"]
            transaction.gas_price = gas_cost["gas_price"]
            
            # Send transaction (mock implementation)
            transaction_hash = self._generate_transaction_hash(transaction)
            transaction.transaction_hash = transaction_hash
            transaction.status = TransactionStatus.PENDING
            
            # Mock broadcast to network
            broadcast_result = await self._broadcast_transaction(transaction)
            
            if broadcast_result["success"]:
                return {
                    "success": True,
                    "transaction_hash": transaction_hash,
                    "gas_fee": float(transaction.gas_fee),
                    "estimated_confirmation_time": 15  # minutes
                }
            else:
                return {
                    "success": False,
                    "error": broadcast_result["error"],
                    "transaction_hash": None
                }
                
        except Exception as e:
            logger.error(f"Error sending transaction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transaction_hash": None
            }

    async def get_transaction_status(self, transaction_hash: str) -> Dict[str, Any]:
        """Get transaction status from blockchain"""
        try:
            # Mock transaction status check
            mock_status = {
                "status": "confirmed",
                "confirmations": 6,
                "block_number": 18500000,
                "gas_used": 21000,
                "gas_price": "20000000000",  # 20 gwei
                "success": True
            }
            
            return {
                "transaction_hash": transaction_hash,
                "status": mock_status["status"],
                "confirmations": mock_status["confirmations"],
                "block_number": mock_status["block_number"],
                "gas_used": mock_status["gas_used"],
                "success": mock_status["success"]
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return {
                "transaction_hash": transaction_hash,
                "status": "unknown",
                "error": str(e)
            }

    async def _validate_transaction(self, transaction: CryptoTransaction) -> Dict[str, Any]:
        """Validate transaction before sending"""
        validation_issues = []
        
        # Check address format
        if not self._is_valid_address(transaction.from_address):
            validation_issues.append("Invalid from address")
        
        if not self._is_valid_address(transaction.to_address):
            validation_issues.append("Invalid to address")
        
        # Check amount
        if transaction.amount <= 0:
            validation_issues.append("Amount must be greater than zero")
        
        # Check balance (mock)
        from_balance = await self.get_balance(transaction.from_address, transaction.currency)
        if from_balance < transaction.amount:
            validation_issues.append("Insufficient balance")
        
        return {
            "valid": len(validation_issues) == 0,
            "error": "; ".join(validation_issues) if validation_issues else None,
            "issues": validation_issues
        }

    def _is_valid_address(self, address: str) -> bool:
        """Validate blockchain address format"""
        if self.blockchain == Blockchain.ETHEREUM:
            return address.startswith("0x") and len(address) == 42
        elif self.blockchain == Blockchain.BITCOIN:
            return len(address) >= 26 and len(address) <= 35
        elif self.blockchain == Blockchain.SOLANA:
            return len(address) >= 32 and len(address) <= 44
        else:
            return True  # Generic validation

    async def _calculate_gas_fees(self, transaction: CryptoTransaction) -> Dict[str, Any]:
        """Calculate gas fees for transaction"""
        gas_settings = self.gas_settings
        
        gas_limit = gas_settings.get("gas_limit", 21000)
        gas_price_gwei = gas_settings.get("gas_price_gwei", 20)
        gas_price_wei = Decimal(str(gas_price_gwei)) * Decimal('1000000000')  # Convert to wei
        
        total_fee = Decimal(str(gas_limit)) * gas_price_wei / Decimal('1000000000000000000')  # Convert to ETH
        
        return {
            "gas_limit": gas_limit,
            "gas_price": gas_price_wei,
            "gas_price_gwei": gas_price_gwei,
            "total_fee": total_fee
        }

    def _generate_transaction_hash(self, transaction: CryptoTransaction) -> str:
        """Generate mock transaction hash"""
        hash_input = f"{transaction.from_address}{transaction.to_address}{transaction.amount}{datetime.utcnow().timestamp()}"
        return "0x" + hashlib.sha256(hash_input.encode()).hexdigest()

    async def _broadcast_transaction(self, transaction: CryptoTransaction) -> Dict[str, Any]:
        """Broadcast transaction to network (mock)"""
        # Mock successful broadcast
        return {
            "success": True,
            "transaction_hash": transaction.transaction_hash,
            "network_response": "Transaction broadcasted successfully"
        }

class CryptoPriceOracle:
    """Cryptocurrency price oracle"""
    
    def __init__(self):
        self.price_cache = {}
        self.cache_duration = timedelta(minutes=5)
        self.price_sources = ["coinbase", "binance", "kraken", "coingecko"]
        
        logger.info("Crypto Price Oracle initialized")

    async def get_price(self, currency: CryptoCurrency, base_currency: str = "USD") -> CryptoPrice:
        """Get current price for cryptocurrency"""
        try:
            cache_key = f"{currency.value}_{base_currency}"
            
            # Check cache
            if cache_key in self.price_cache:
                cached_price = self.price_cache[cache_key]
                if datetime.utcnow() - cached_price.timestamp < self.cache_duration:
                    return cached_price
            
            # Fetch new price (mock implementation)
            price_data = await self._fetch_price_data(currency, base_currency)
            
            crypto_price = CryptoPrice(
                currency=currency,
                price_usd=price_data["price_usd"],
                price_btc=price_data["price_btc"],
                market_cap=price_data["market_cap"],
                volume_24h=price_data["volume_24h"],
                change_24h=price_data["change_24h"],
                source=price_data["source"]
            )
            
            # Cache price
            self.price_cache[cache_key] = crypto_price
            
            return crypto_price
            
        except Exception as e:
            logger.error(f"Error getting crypto price: {str(e)}")
            # Return default price if error
            return CryptoPrice(
                currency=currency,
                price_usd=Decimal('0'),
                price_btc=Decimal('0'),
                market_cap=Decimal('0'),
                volume_24h=Decimal('0'),
                change_24h=Decimal('0')
            )

    async def _fetch_price_data(self, currency: CryptoCurrency, base_currency: str) -> Dict[str, Any]:
        """Fetch price data from external APIs"""
        # Mock price data
        mock_prices = {
            CryptoCurrency.BITCOIN: {
                "price_usd": Decimal('45000'),
                "price_btc": Decimal('1'),
                "market_cap": Decimal('900000000000'),
                "volume_24h": Decimal('25000000000'),
                "change_24h": Decimal('2.5')
            },
            CryptoCurrency.ETHEREUM: {
                "price_usd": Decimal('3000'),
                "price_btc": Decimal('0.0667'),
                "market_cap": Decimal('360000000000'),
                "volume_24h": Decimal('15000000000'),
                "change_24h": Decimal('3.2')
            },
            CryptoCurrency.USDC: {
                "price_usd": Decimal('1.00'),
                "price_btc": Decimal('0.0000222'),
                "market_cap": Decimal('52000000000'),
                "volume_24h": Decimal('8000000000'),
                "change_24h": Decimal('0.01')
            }
        }
        
        price_data = mock_prices.get(currency, {
            "price_usd": Decimal('100'),
            "price_btc": Decimal('0.002'),
            "market_cap": Decimal('1000000000'),
            "volume_24h": Decimal('50000000'),
            "change_24h": Decimal('1.0')
        })
        
        price_data["source"] = "mock_api"
        return price_data

    async def convert_currency(self, amount: Decimal, from_currency: CryptoCurrency, 
                             to_currency: CryptoCurrency) -> Dict[str, Any]:
        """Convert between cryptocurrencies"""
        try:
            from_price = await self.get_price(from_currency)
            to_price = await self.get_price(to_currency)
            
            # Convert via USD
            usd_amount = amount * from_price.price_usd
            converted_amount = usd_amount / to_price.price_usd
            
            return {
                "original_amount": float(amount),
                "original_currency": from_currency.value,
                "converted_amount": float(converted_amount),
                "converted_currency": to_currency.value,
                "exchange_rate": float(from_price.price_usd / to_price.price_usd),
                "conversion_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Currency conversion error: {str(e)}")
            raise

class DeFiManager:
    """DeFi protocol manager"""
    
    def __init__(self):
        self.pools = {}
        self.staking_positions = {}
        self.yield_strategies = {}
        
        # Initialize DeFi pools
        self._initialize_defi_pools()
        
        logger.info("DeFi Manager initialized")

    def _initialize_defi_pools(self):
        """Initialize DeFi liquidity pools"""
        default_pools = [
            {
                "pool_id": "uniswap_eth_usdc",
                "protocol": DeFiProtocol.UNISWAP,
                "token_a": CryptoCurrency.ETHEREUM,
                "token_b": CryptoCurrency.USDC,
                "token_a_amount": Decimal('1000'),
                "token_b_amount": Decimal('3000000'),
                "total_liquidity": Decimal('6000000'),
                "apr": Decimal('0.12'),  # 12% APR
                "fees_24h": Decimal('5000'),
                "volume_24h": Decimal('2000000')
            },
            {
                "pool_id": "sushiswap_btc_eth",
                "protocol": DeFiProtocol.SUSHISWAP,
                "token_a": CryptoCurrency.BITCOIN,
                "token_b": CryptoCurrency.ETHEREUM,
                "token_a_amount": Decimal('100'),
                "token_b_amount": Decimal('1500'),
                "total_liquidity": Decimal('9000000'),
                "apr": Decimal('0.18'),  # 18% APR
                "fees_24h": Decimal('8000'),
                "volume_24h": Decimal('3000000')
            }
        ]
        
        for pool_data in default_pools:
            pool = DeFiPool(**pool_data)
            self.pools[pool.pool_id] = pool

    async def add_liquidity(self, pool_id: str, token_a_amount: Decimal, 
                           token_b_amount: Decimal, user_address: str) -> Dict[str, Any]:
        """Add liquidity to DeFi pool"""
        try:
            if pool_id not in self.pools:
                raise ValueError(f"Pool not found: {pool_id}")
            
            pool = self.pools[pool_id]
            
            # Calculate LP tokens
            lp_tokens = await self._calculate_lp_tokens(pool, token_a_amount, token_b_amount)
            
            # Update pool state
            pool.token_a_amount += token_a_amount
            pool.token_b_amount += token_b_amount
            pool.total_liquidity += token_a_amount * Decimal('3000') + token_b_amount  # Mock calculation
            pool.last_updated = datetime.utcnow()
            
            # Record position
            position_id = f"pos_{uuid.uuid4().hex[:12]}"
            position = {
                "position_id": position_id,
                "pool_id": pool_id,
                "user_address": user_address,
                "token_a_amount": float(token_a_amount),
                "token_b_amount": float(token_b_amount),
                "lp_tokens": float(lp_tokens),
                "entry_timestamp": datetime.utcnow().isoformat()
            }
            
            self.staking_positions[position_id] = position
            
            return {
                "success": True,
                "position_id": position_id,
                "lp_tokens_received": float(lp_tokens),
                "pool_share": float(lp_tokens / (pool.total_liquidity / Decimal('1000000'))),  # Mock calculation
                "estimated_apr": float(pool.apr),
                "transaction_hash": f"0x{uuid.uuid4().hex}"
            }
            
        except Exception as e:
            logger.error(f"Add liquidity error: {str(e)}")
            raise

    async def remove_liquidity(self, position_id: str, percentage: float = 100.0) -> Dict[str, Any]:
        """Remove liquidity from DeFi pool"""
        try:
            if position_id not in self.staking_positions:
                raise ValueError(f"Position not found: {position_id}")
            
            position = self.staking_positions[position_id]
            pool = self.pools[position["pool_id"]]
            
            # Calculate withdrawal amounts
            withdrawal_factor = Decimal(str(percentage / 100.0))
            token_a_withdrawn = Decimal(str(position["token_a_amount"])) * withdrawal_factor
            token_b_withdrawn = Decimal(str(position["token_b_amount"])) * withdrawal_factor
            
            # Calculate yield earned
            yield_earned = await self._calculate_yield_earned(position, pool)
            
            # Update position
            if percentage >= 100.0:
                del self.staking_positions[position_id]
            else:
                position["token_a_amount"] = float(Decimal(str(position["token_a_amount"])) * (Decimal('1') - withdrawal_factor))
                position["token_b_amount"] = float(Decimal(str(position["token_b_amount"])) * (Decimal('1') - withdrawal_factor))
                position["lp_tokens"] = float(Decimal(str(position["lp_tokens"])) * (Decimal('1') - withdrawal_factor))
            
            return {
                "success": True,
                "token_a_withdrawn": float(token_a_withdrawn),
                "token_b_withdrawn": float(token_b_withdrawn),
                "yield_earned": yield_earned,
                "transaction_hash": f"0x{uuid.uuid4().hex}"
            }
            
        except Exception as e:
            logger.error(f"Remove liquidity error: {str(e)}")
            raise

    async def _calculate_lp_tokens(self, pool: DeFiPool, token_a_amount: Decimal, 
                                  token_b_amount: Decimal) -> Decimal:
        """Calculate LP tokens for liquidity provision"""
        # Simplified LP token calculation
        total_value = token_a_amount * Decimal('3000') + token_b_amount  # Mock ETH price
        lp_tokens = total_value / Decimal('10')  # Mock LP token ratio
        return lp_tokens

    async def _calculate_yield_earned(self, position: Dict[str, Any], pool: DeFiPool) -> Dict[str, Any]:
        """Calculate yield earned from liquidity provision"""
        try:
            entry_time = datetime.fromisoformat(position["entry_timestamp"])
            time_staked = datetime.utcnow() - entry_time
            days_staked = time_staked.total_seconds() / 86400
            
            # Calculate yield
            principal = Decimal(str(position["token_a_amount"])) * Decimal('3000') + Decimal(str(position["token_b_amount"]))
            annual_yield = principal * pool.apr
            yield_earned = annual_yield * Decimal(str(days_staked / 365))
            
            return {
                "total_yield_usd": float(yield_earned),
                "daily_yield_usd": float(yield_earned / Decimal(str(max(days_staked, 1)))),
                "apr": float(pool.apr),
                "days_staked": days_staked
            }
            
        except Exception as e:
            logger.error(f"Yield calculation error: {str(e)}")
            return {"total_yield_usd": 0, "daily_yield_usd": 0, "apr": 0, "days_staked": 0}

class CryptoPaymentCore:
    """Main Crypto Payment Core System"""
    
    def __init__(self):
        self.version = "2.1.0"
        self.wallets = {}
        self.transactions = {}
        self.price_oracle = CryptoPriceOracle()
        self.defi_manager = DeFiManager()
        self.blockchain_connectors = {}
        
        # Initialize blockchain connectors
        for blockchain in Blockchain:
            self.blockchain_connectors[blockchain] = BlockchainConnector(blockchain)
        
        logger.info("Crypto Payment Core initialized")

    async def create_wallet(self, wallet_data: Dict[str, Any]) -> str:
        """Create new cryptocurrency wallet"""
        try:
            wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
            
            # Generate wallet address (mock)
            address = self._generate_wallet_address(wallet_data["blockchain"])
            
            wallet = CryptoWallet(
                wallet_id=wallet_id,
                wallet_type=WalletType(wallet_data["wallet_type"]),
                blockchain=Blockchain(wallet_data["blockchain"]),
                address=address,
                private_key_encrypted=wallet_data.get("private_key_encrypted"),
                public_key=wallet_data.get("public_key", f"pubkey_{uuid.uuid4().hex[:20]}"),
                balance=Decimal('0'),
                currency=CryptoCurrency(wallet_data["currency"]),
                metadata=wallet_data.get("metadata", {})
            )
            
            self.wallets[wallet_id] = wallet
            
            logger.info(f"Crypto wallet created: {wallet_id}")
            return wallet_id
            
        except Exception as e:
            logger.error(f"Error creating wallet: {str(e)}")
            raise

    async def process_crypto_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process cryptocurrency payment"""
        try:
            transaction_id = f"crypto_txn_{uuid.uuid4().hex[:12]}"
            
            # Create transaction record
            transaction = CryptoTransaction(
                transaction_id=transaction_id,
                blockchain=Blockchain(payment_data["blockchain"]),
                from_address=payment_data["from_address"],
                to_address=payment_data["to_address"],
                amount=Decimal(str(payment_data["amount"])),
                currency=CryptoCurrency(payment_data["currency"]),
                gas_fee=Decimal('0'),  # Will be calculated
                gas_limit=21000,  # Default
                gas_price=Decimal('0'),  # Will be calculated
                transaction_hash=None,
                customer_id=payment_data.get("customer_id"),
                reference=payment_data.get("reference"),
                metadata=payment_data.get("metadata", {})
            )
            
            # Get blockchain connector
            connector = self.blockchain_connectors[transaction.blockchain]
            
            # Send transaction
            send_result = await connector.send_transaction(transaction)
            
            if send_result["success"]:
                transaction.status = TransactionStatus.CONFIRMING
                transaction.transaction_hash = send_result["transaction_hash"]
                
                # Store transaction
                self.transactions[transaction_id] = transaction
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "transaction_hash": send_result["transaction_hash"],
                    "gas_fee": send_result["gas_fee"],
                    "estimated_confirmation_time": send_result["estimated_confirmation_time"],
                    "status": transaction.status.value
                }
            else:
                transaction.status = TransactionStatus.FAILED
                self.transactions[transaction_id] = transaction
                
                return {
                    "success": False,
                    "transaction_id": transaction_id,
                    "error": send_result["error"],
                    "status": transaction.status.value
                }
                
        except Exception as e:
            logger.error(f"Crypto payment processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": None
            }

    async def check_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check cryptocurrency transaction status"""
        try:
            if transaction_id not in self.transactions:
                return {
                    "found": False,
                    "error": "Transaction not found"
                }
            
            transaction = self.transactions[transaction_id]
            
            if transaction.transaction_hash and transaction.status == TransactionStatus.CONFIRMING:
                # Check blockchain status
                connector = self.blockchain_connectors[transaction.blockchain]
                blockchain_status = await connector.get_transaction_status(transaction.transaction_hash)
                
                # Update transaction status
                if blockchain_status["status"] == "confirmed":
                    transaction.status = TransactionStatus.CONFIRMED
                    transaction.confirmed_at = datetime.utcnow()
                    transaction.confirmation_count = blockchain_status["confirmations"]
                    transaction.block_number = blockchain_status["block_number"]
            
            return {
                "found": True,
                "transaction_id": transaction_id,
                "status": transaction.status.value,
                "transaction_hash": transaction.transaction_hash,
                "confirmations": transaction.confirmation_count,
                "block_number": transaction.block_number,
                "amount": float(transaction.amount),
                "currency": transaction.currency.value,
                "gas_fee": float(transaction.gas_fee),
                "created_at": transaction.created_at.isoformat(),
                "confirmed_at": transaction.confirmed_at.isoformat() if transaction.confirmed_at else None
            }
            
        except Exception as e:
            logger.error(f"Transaction status check error: {str(e)}")
            return {
                "found": False,
                "error": str(e)
            }

    async def get_wallet_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet balance with current prices"""
        try:
            if wallet_id not in self.wallets:
                return {
                    "found": False,
                    "error": "Wallet not found"
                }
            
            wallet = self.wallets[wallet_id]
            
            # Get current balance from blockchain
            connector = self.blockchain_connectors[wallet.blockchain]
            current_balance = await connector.get_balance(wallet.address, wallet.currency)
            
            # Update wallet balance
            wallet.balance = current_balance
            wallet.last_synced = datetime.utcnow()
            
            # Get current price
            price_data = await self.price_oracle.get_price(wallet.currency)
            
            usd_value = current_balance * price_data.price_usd
            
            return {
                "found": True,
                "wallet_id": wallet_id,
                "address": wallet.address,
                "balance": float(current_balance),
                "currency": wallet.currency.value,
                "usd_value": float(usd_value),
                "price_per_unit": float(price_data.price_usd),
                "price_change_24h": float(price_data.change_24h),
                "last_synced": wallet.last_synced.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wallet balance error: {str(e)}")
            return {
                "found": False,
                "error": str(e)
            }

    async def swap_tokens(self, swap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Swap tokens using DeFi protocols"""
        try:
            from_currency = CryptoCurrency(swap_data["from_currency"])
            to_currency = CryptoCurrency(swap_data["to_currency"])
            amount = Decimal(str(swap_data["amount"]))
            
            # Get conversion rate
            conversion = await self.price_oracle.convert_currency(amount, from_currency, to_currency)
            
            # Calculate slippage and fees
            slippage = Decimal('0.005')  # 0.5% slippage
            protocol_fee = Decimal('0.003')  # 0.3% protocol fee
            
            expected_output = Decimal(str(conversion["converted_amount"]))
            slippage_amount = expected_output * slippage
            fee_amount = expected_output * protocol_fee
            final_output = expected_output - slippage_amount - fee_amount
            
            # Create swap transaction
            swap_id = f"swap_{uuid.uuid4().hex[:12]}"
            
            swap_result = {
                "swap_id": swap_id,
                "from_currency": from_currency.value,
                "to_currency": to_currency.value,
                "input_amount": float(amount),
                "expected_output": float(expected_output),
                "actual_output": float(final_output),
                "slippage": float(slippage_amount),
                "protocol_fee": float(fee_amount),
                "exchange_rate": conversion["exchange_rate"],
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "swap_result": swap_result
            }
            
        except Exception as e:
            logger.error(f"Token swap error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def stake_tokens(self, staking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stake tokens in DeFi protocol"""
        try:
            pool_id = staking_data["pool_id"]
            token_a_amount = Decimal(str(staking_data["token_a_amount"]))
            token_b_amount = Decimal(str(staking_data["token_b_amount"]))
            user_address = staking_data["user_address"]
            
            # Add liquidity to DeFi pool
            liquidity_result = await self.defi_manager.add_liquidity(
                pool_id, token_a_amount, token_b_amount, user_address
            )
            
            return {
                "success": True,
                "staking_result": liquidity_result
            }
            
        except Exception as e:
            logger.error(f"Token staking error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_portfolio_analytics(self, user_address: str) -> Dict[str, Any]:
        """Get comprehensive crypto portfolio analytics"""
        try:
            # Get user wallets
            user_wallets = [w for w in self.wallets.values() if w.metadata.get("owner") == user_address]
            
            if not user_wallets:
                return {
                    "user_address": user_address,
                    "total_wallets": 0,
                    "total_value_usd": 0,
                    "portfolio": {}
                }
            
            portfolio = {}
            total_value_usd = Decimal('0')
            
            for wallet in user_wallets:
                # Get current balance and value
                balance_info = await self.get_wallet_balance(wallet.wallet_id)
                
                if balance_info["found"]:
                    currency = wallet.currency.value
                    if currency not in portfolio:
                        portfolio[currency] = {
                            "total_balance": 0,
                            "total_value_usd": 0,
                            "wallets": []
                        }
                    
                    portfolio[currency]["total_balance"] += balance_info["balance"]
                    portfolio[currency]["total_value_usd"] += balance_info["usd_value"]
                    portfolio[currency]["wallets"].append({
                        "wallet_id": wallet.wallet_id,
                        "address": wallet.address,
                        "balance": balance_info["balance"],
                        "value_usd": balance_info["usd_value"]
                    })
                    
                    total_value_usd += Decimal(str(balance_info["usd_value"]))
            
            # Get DeFi positions
            user_positions = [p for p in self.defi_manager.staking_positions.values() 
                            if p["user_address"] == user_address]
            
            defi_positions = []
            for position in user_positions:
                pool = self.defi_manager.pools[position["pool_id"]]
                yield_info = await self.defi_manager._calculate_yield_earned(position, pool)
                
                defi_positions.append({
                    "position_id": position["position_id"],
                    "pool_id": position["pool_id"],
                    "protocol": pool.protocol.value,
                    "tokens": f"{pool.token_a.value}/{pool.token_b.value}",
                    "lp_tokens": position["lp_tokens"],
                    "yield_earned": yield_info,
                    "apr": float(pool.apr)
                })
            
            analytics = {
                "user_address": user_address,
                "total_wallets": len(user_wallets),
                "total_value_usd": float(total_value_usd),
                "portfolio_breakdown": portfolio,
                "defi_positions": defi_positions,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Portfolio analytics error: {str(e)}")
            raise

    def _generate_wallet_address(self, blockchain: str) -> str:
        """Generate mock wallet address"""
        if blockchain == "ethereum":
            return "0x" + uuid.uuid4().hex[:40]
        elif blockchain == "bitcoin":
            return "1" + uuid.uuid4().hex[:33]
        elif blockchain == "solana":
            return uuid.uuid4().hex[:44]
        else:
            return "addr_" + uuid.uuid4().hex[:36]

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics"""
        total_wallets = len(self.wallets)
        total_transactions = len(self.transactions)
        total_defi_pools = len(self.defi_manager.pools)
        total_staking_positions = len(self.defi_manager.staking_positions)
        
        # Transaction status distribution
        status_distribution = {}
        for transaction in self.transactions.values():
            status = transaction.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Supported blockchain count
        supported_blockchains = len(self.blockchain_connectors)
        
        return {
            "version": self.version,
            "total_wallets": total_wallets,
            "total_transactions": total_transactions,
            "total_defi_pools": total_defi_pools,
            "total_staking_positions": total_staking_positions,
            "supported_blockchains": supported_blockchains,
            "supported_currencies": len(CryptoCurrency),
            "transaction_status_distribution": status_distribution,
            "price_oracle_cache_size": len(self.price_oracle.price_cache),
            "system_status": "healthy",
            "last_health_check": datetime.utcnow().isoformat()
        }

# Global instance
crypto_payment_core = CryptoPaymentCore()

# Export main functions
__all__ = [
    "CryptoCurrency",
    "Blockchain",
    "TransactionStatus",
    "WalletType",
    "DeFiProtocol",
    "CryptoWallet",
    "CryptoTransaction",
    "CryptoPrice",
    "DeFiPool",
    "CryptoPaymentCore",
    "crypto_payment_core"
]

if __name__ == "__main__":
    logger.info("Crypto Payment Core module loaded successfully")