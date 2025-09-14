"""
Crypto Payment Configuration - Enterprise Configuration Management
Enterprise configuration for cryptocurrency payment processing business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()
    
    def validator(field_name) -> None:
        def decorator(func) -> None:
            return func
        return decorator


class CryptoCurrency(str, Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    USDC = "usdc"
    USDT = "usdt"
    BNB = "bnb"
    SOLANA = "solana"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    CARDANO = "cardano"
    LITECOIN = "litecoin"
    CHAINLINK = "chainlink"
    CUSTOM_TOKENS = "custom_tokens"


class BlockchainNetwork(str, Enum):
    """Blockchain networks"""
    BITCOIN_MAINNET = "bitcoin_mainnet"
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_TESTNET = "ethereum_testnet"
    POLYGON_MAINNET = "polygon_mainnet"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    SOLANA_MAINNET = "solana_mainnet"
    AVALANCHE_C_CHAIN = "avalanche_c_chain"
    CARDANO_MAINNET = "cardano_mainnet"
    LITECOIN_MAINNET = "litecoin_mainnet"


class WalletType(str, Enum):
    """Crypto wallet types"""
    HOT_WALLET = "hot_wallet"
    COLD_WALLET = "cold_wallet"
    MULTI_SIG = "multi_sig"
    HARDWARE = "hardware"
    CUSTODIAL = "custodial"
    NON_CUSTODIAL = "non_custodial"
    SMART_CONTRACT = "smart_contract"


class TransactionType(str, Enum):
    """Crypto transaction types"""
    PAYMENT = "payment"
    PAYOUT = "payout"
    EXCHANGE = "exchange"
    STAKING = "staking"
    NFT_MINT = "nft_mint"
    NFT_SALE = "nft_sale"
    SMART_CONTRACT_CALL = "smart_contract_call"
    TOKEN_TRANSFER = "token_transfer"


class SecurityLevel(str, Enum):
    """Crypto security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    INSTITUTIONAL = "institutional"
    BANK_GRADE = "bank_grade"


class ComplianceFramework(str, Enum):
    """Crypto compliance frameworks"""
    AML = "aml"
    KYC = "kyc"
    FATF = "fatf"
    OFAC = "ofac"
    EU_MiCA = "eu_mica"
    US_FinCEN = "us_fincen"
    TRAVEL_RULE = "travel_rule"


@dataclass
class CryptoCurrencyConfig:
    """Cryptocurrency configuration"""
    currency: CryptoCurrency
    symbol: str
    name: str
    network: BlockchainNetwork
    contract_address: Optional[str]
    decimals: int
    enabled: bool
    minimum_amount: float
    maximum_amount: float
    confirmation_blocks: int
    transaction_fee: float
    gas_price_gwei: Optional[int]
    wallet_config: Dict[str, Any]


@dataclass
class WalletConfiguration:
    """Wallet configuration"""
    wallet_type: WalletType
    enabled: bool
    network: BlockchainNetwork
    address: Optional[str]
    private_key_encrypted: Optional[str]
    multi_sig_threshold: Optional[int]
    multi_sig_addresses: List[str]
    hardware_device: Optional[str]
    custodial_provider: Optional[str]
    security_features: List[str]


@dataclass
class ExchangeIntegration:
    """Crypto exchange integration"""
    exchange_name: str
    enabled: bool
    api_credentials: Dict[str, str]
    supported_pairs: List[str]
    trading_fees: Dict[str, float]
    withdrawal_fees: Dict[str, float]
    minimum_trade_amount: float
    maximum_trade_amount: float
    rate_limits: Dict[str, int]


@dataclass
class SmartContractConfig:
    """Smart contract configuration"""
    contract_name: str
    contract_address: str
    network: BlockchainNetwork
    abi: List[Dict[str, Any]]
    enabled: bool
    gas_limit: int
    gas_price_strategy: str
    security_audited: bool
    upgrade_mechanism: str


class CryptoPaymentSettings(BaseSettings):
    """Crypto payment configuration settings"""
    
    # Supported Cryptocurrencies
    cryptocurrencies: Dict[str, CryptoCurrencyConfig] = Field(
        default_factory=lambda: {
            "bitcoin": CryptoCurrencyConfig(
                currency=CryptoCurrency.BITCOIN,
                symbol="BTC",
                name="Bitcoin",
                network=BlockchainNetwork.BITCOIN_MAINNET,
                contract_address=None,
                decimals=8,
                enabled=True,
                minimum_amount=0.0001,
                maximum_amount=100.0,
                confirmation_blocks=6,
                transaction_fee=0.0005,
                gas_price_gwei=None,
                wallet_config={
                    "derivation_path": "m/84'/0'/0'",
                    "address_type": "bech32",
                    "fee_strategy": "economic"
                }
            ),
            "ethereum": CryptoCurrencyConfig(
                currency=CryptoCurrency.ETHEREUM,
                symbol="ETH",
                name="Ethereum",
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                contract_address=None,
                decimals=18,
                enabled=True,
                minimum_amount=0.001,
                maximum_amount=1000.0,
                confirmation_blocks=12,
                transaction_fee=0.005,
                gas_price_gwei=20,
                wallet_config={
                    "derivation_path": "m/44'/60'/0'",
                    "chain_id": 1,
                    "gas_limit": 21000
                }
            ),
            "usdc": CryptoCurrencyConfig(
                currency=CryptoCurrency.USDC,
                symbol="USDC",
                name="USD Coin",
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                contract_address="0xA0b86a33E6417aA0b8A5F6b6C9F38E8A8C5F5b3b",
                decimals=6,
                enabled=True,
                minimum_amount=1.0,
                maximum_amount=100000.0,
                confirmation_blocks=12,
                transaction_fee=0.002,
                gas_price_gwei=25,
                wallet_config={
                    "derivation_path": "m/44'/60'/0'",
                    "chain_id": 1,
                    "gas_limit": 65000
                }
            ),
            "usdt": CryptoCurrencyConfig(
                currency=CryptoCurrency.USDT,
                symbol="USDT",
                name="Tether USD",
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                contract_address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
                decimals=6,
                enabled=True,
                minimum_amount=1.0,
                maximum_amount=100000.0,
                confirmation_blocks=12,
                transaction_fee=0.002,
                gas_price_gwei=25,
                wallet_config={
                    "derivation_path": "m/44'/60'/0'",
                    "chain_id": 1,
                    "gas_limit": 65000
                }
            ),
            "solana": CryptoCurrencyConfig(
                currency=CryptoCurrency.SOLANA,
                symbol="SOL",
                name="Solana",
                network=BlockchainNetwork.SOLANA_MAINNET,
                contract_address=None,
                decimals=9,
                enabled=True,
                minimum_amount=0.01,
                maximum_amount=10000.0,
                confirmation_blocks=32,
                transaction_fee=0.000005,
                gas_price_gwei=None,
                wallet_config={
                    "derivation_path": "m/44'/501'/0'",
                    "cluster": "mainnet-beta",
                    "commitment": "confirmed"
                }
            ),
            "polygon": CryptoCurrencyConfig(
                currency=CryptoCurrency.POLYGON,
                symbol="MATIC",
                name="Polygon",
                network=BlockchainNetwork.POLYGON_MAINNET,
                contract_address=None,
                decimals=18,
                enabled=True,
                minimum_amount=0.1,
                maximum_amount=100000.0,
                confirmation_blocks=30,
                transaction_fee=0.0001,
                gas_price_gwei=2,
                wallet_config={
                    "derivation_path": "m/44'/60'/0'",
                    "chain_id": 137,
                    "gas_limit": 21000
                }
            )
        }
    )
    
    # Wallet Configurations
    wallets: Dict[str, WalletConfiguration] = Field(
        default_factory=lambda: {
            "hot_wallet_eth": WalletConfiguration(
                wallet_type=WalletType.HOT_WALLET,
                enabled=True,
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                address="",  # To be configured
                private_key_encrypted="",  # Encrypted storage
                multi_sig_threshold=None,
                multi_sig_addresses=[],
                hardware_device=None,
                custodial_provider=None,
                security_features=[
                    "encryption", "access_control", "audit_logging",
                    "rate_limiting", "geographic_restrictions"
                ]
            ),
            "cold_wallet_btc": WalletConfiguration(
                wallet_type=WalletType.COLD_WALLET,
                enabled=True,
                network=BlockchainNetwork.BITCOIN_MAINNET,
                address="",  # To be configured
                private_key_encrypted="",  # Encrypted storage
                multi_sig_threshold=None,
                multi_sig_addresses=[],
                hardware_device="ledger_nano_s",
                custodial_provider=None,
                security_features=[
                    "hardware_security", "offline_storage",
                    "multi_sig_capability", "time_locks"
                ]
            ),
            "multi_sig_treasury": WalletConfiguration(
                wallet_type=WalletType.MULTI_SIG,
                enabled=True,
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                address="",  # Smart contract address
                private_key_encrypted=None,
                multi_sig_threshold=3,
                multi_sig_addresses=["", "", "", ""],  # 3-of-4 multisig
                hardware_device=None,
                custodial_provider=None,
                security_features=[
                    "multi_signature", "time_delays", "transaction_limits",
                    "emergency_recovery", "governance_controls"
                ]
            )
        }
    )
    
    # Exchange Integrations
    exchanges: Dict[str, ExchangeIntegration] = Field(
        default_factory=lambda: {
            "coinbase": ExchangeIntegration(
                exchange_name="coinbase",
                enabled=True,
                api_credentials={
                    "api_key": "",
                    "api_secret": "",
                    "passphrase": "",
                    "sandbox": "false"
                },
                supported_pairs=[
                    "BTC-USD", "ETH-USD", "USDC-USD", "SOL-USD",
                    "MATIC-USD", "BTC-EUR", "ETH-EUR"
                ],
                trading_fees={
                    "maker": 0.005,  # 0.5%
                    "taker": 0.005   # 0.5%
                },
                withdrawal_fees={
                    "BTC": 0.0005,
                    "ETH": 0.005,
                    "USDC": 0.0,
                    "SOL": 0.01
                },
                minimum_trade_amount=10.0,
                maximum_trade_amount=1000000.0,
                rate_limits={
                    "requests_per_second": 10,
                    "requests_per_minute": 100
                }
            ),
            "binance": ExchangeIntegration(
                exchange_name="binance",
                enabled=True,
                api_credentials={
                    "api_key": "",
                    "secret_key": "",
                    "testnet": "false"
                },
                supported_pairs=[
                    "BTCUSDT", "ETHUSDT", "SOLUSDT", "MATICUSDT",
                    "BNBUSDT", "ADAUSDT", "LTCUSDT"
                ],
                trading_fees={
                    "maker": 0.001,  # 0.1%
                    "taker": 0.001   # 0.1%
                },
                withdrawal_fees={
                    "BTC": 0.0005,
                    "ETH": 0.005,
                    "USDT": 1.0,
                    "SOL": 0.01
                },
                minimum_trade_amount=5.0,
                maximum_trade_amount=2000000.0,
                rate_limits={
                    "requests_per_second": 20,
                    "requests_per_minute": 1200
                }
            )
        }
    )
    
    # Smart Contract Configurations
    smart_contracts: Dict[str, SmartContractConfig] = Field(
        default_factory=lambda: {
            "payment_processor": SmartContractConfig(
                contract_name="AinflueCryptoPaymentProcessor",
                contract_address="",  # To be deployed
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                abi=[],  # Contract ABI
                enabled=True,
                gas_limit=200000,
                gas_price_strategy="medium",
                security_audited=True,
                upgrade_mechanism="proxy_pattern"
            ),
            "token_swap": SmartContractConfig(
                contract_name="AinflueTokenSwap",
                contract_address="",  # To be deployed
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                abi=[],  # Contract ABI
                enabled=True,
                gas_limit=300000,
                gas_price_strategy="medium",
                security_audited=True,
                upgrade_mechanism="proxy_pattern"
            ),
            "nft_marketplace": SmartContractConfig(
                contract_name="AinflueNFTMarketplace",
                contract_address="",  # To be deployed
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                abi=[],  # Contract ABI
                enabled=True,
                gas_limit=500000,
                gas_price_strategy="high",
                security_audited=True,
                upgrade_mechanism="diamond_pattern"
            )
        }
    )
    
    # Security Configuration
    security_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "encryption_standard": "AES-256-GCM",
            "key_management": "hsm_backed",
            "multi_signature_required": True,
            "transaction_limits": {
                "daily_limit_usd": 100000.0,
                "transaction_limit_usd": 50000.0,
                "withdrawal_limit_usd": 25000.0
            },
            "security_features": [
                "hardware_security_module", "cold_storage",
                "multi_signature", "time_locks", "rate_limiting",
                "geographic_restrictions", "device_fingerprinting",
                "behavioral_analysis", "fraud_detection"
            ],
            "audit_requirements": {
                "transaction_logging": True,
                "access_logging": True,
                "security_events": True,
                "compliance_reporting": True
            }
        }
    )
    
    # Compliance Configuration
    compliance_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "frameworks": [
                ComplianceFramework.AML,
                ComplianceFramework.KYC,
                ComplianceFramework.FATF,
                ComplianceFramework.TRAVEL_RULE
            ],
            "kyc_requirements": {
                "individual_verification": True,
                "business_verification": True,
                "enhanced_due_diligence": True,
                "ongoing_monitoring": True
            },
            "aml_features": {
                "transaction_monitoring": True,
                "sanctions_screening": True,
                "suspicious_activity_reporting": True,
                "risk_scoring": True
            },
            "reporting_requirements": {
                "regulatory_reporting": True,
                "tax_reporting": True,
                "audit_trails": True,
                "compliance_metrics": True
            }
        }
    )
    
    # Processing Configuration
    processing_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_conversion": True,
            "real_time_rates": True,
            "slippage_tolerance": 0.02,  # 2%
            "price_impact_limit": 0.05,  # 5%
            "confirmation_requirements": {
                "bitcoin": 6,
                "ethereum": 12,
                "polygon": 30,
                "solana": 32
            },
            "gas_optimization": True,
            "batching_enabled": True,
            "retry_mechanism": True,
            "fallback_providers": True
        }
    )
    
    # Integration Settings
    integration_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "blockchain_providers": [
                "infura", "alchemy", "moralis", "quicknode"
            ],
            "price_feeds": [
                "chainlink", "coingecko", "coinmarketcap"
            ],
            "monitoring_services": [
                "blockchair", "etherscan", "blockchain_info"
            ],
            "webhook_support": True,
            "api_integration": True,
            "real_time_notifications": True,
            "batch_processing": True
        }
    )
    
    # Performance Settings
    performance_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "connection_pooling": True,
            "caching_enabled": True,
            "rate_limiting": True,
            "load_balancing": True,
            "failover_enabled": True,
            "monitoring_enabled": True,
            "metrics_collection": True,
            "performance_optimization": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "CRYPTO_PAYMENT_"
        case_sensitive = False
        extra = "allow"
    
    def get_crypto_config(self, currency: str) -> Optional[CryptoCurrencyConfig]:
        """Get cryptocurrency configuration"""
        return self.cryptocurrencies.get(currency)
    
    def get_wallet_config(self, wallet_name: str) -> Optional[WalletConfiguration]:
        """Get wallet configuration"""
        return self.wallets.get(wallet_name)
    
    def get_exchange_config(self, exchange: str) -> Optional[ExchangeIntegration]:
        """Get exchange configuration"""
        return self.exchanges.get(exchange)
    
    def get_smart_contract_config(self, contract: str) -> Optional[SmartContractConfig]:
        """Get smart contract configuration"""
        return self.smart_contracts.get(contract)
    
    def is_crypto_enabled(self, currency: str) -> bool:
        """Check if cryptocurrency is enabled"""
        config = self.get_crypto_config(currency)
        return config.enabled if config else False
    
    def is_wallet_enabled(self, wallet_name: str) -> bool:
        """Check if wallet is enabled"""
        config = self.get_wallet_config(wallet_name)
        return config.enabled if config else False
    
    def is_exchange_enabled(self, exchange: str) -> bool:
        """Check if exchange is enabled"""
        config = self.get_exchange_config(exchange)
        return config.enabled if config else False
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported cryptocurrencies"""
        return [
            name for name, config in self.cryptocurrencies.items()
            if config.enabled
        ]
    
    def get_minimum_amount(self, currency: str) -> float:
        """Get minimum transaction amount for currency"""
        config = self.get_crypto_config(currency)
        return config.minimum_amount if config else 0.0
    
    def get_maximum_amount(self, currency: str) -> float:
        """Get maximum transaction amount for currency"""
        config = self.get_crypto_config(currency)
        return config.maximum_amount if config else 0.0
    
    def get_confirmation_blocks(self, currency: str) -> int:
        """Get required confirmation blocks for currency"""
        config = self.get_crypto_config(currency)
        return config.confirmation_blocks if config else 1
    
    def get_transaction_fee(self, currency: str) -> float:
        """Get transaction fee for currency"""
        config = self.get_crypto_config(currency)
        return config.transaction_fee if config else 0.0
    
    def get_daily_limit_usd(self) -> float:
        """Get daily transaction limit in USD"""
        return self.security_config["transaction_limits"]["daily_limit_usd"]
    
    def is_multi_sig_required(self, amount_usd: float) -> bool:
        """Check if multi-signature is required for amount"""
        limit = self.security_config["transaction_limits"]["transaction_limit_usd"]
        return amount_usd > limit and self.security_config["multi_signature_required"]
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete crypto payment configuration"""
        errors = []
        
        # Validate cryptocurrency configurations
        for currency, config in self.cryptocurrencies.items():
            if config.enabled:
                if config.minimum_amount < 0:
                    errors.append(f"Currency '{currency}' has negative minimum amount")
                if config.maximum_amount <= config.minimum_amount:
                    errors.append(f"Currency '{currency}' has invalid amount limits")
                if config.confirmation_blocks <= 0:
                    errors.append(f"Currency '{currency}' has invalid confirmation blocks")
                if config.decimals < 0:
                    errors.append(f"Currency '{currency}' has negative decimals")
        
        # Validate wallet configurations
        for wallet_name, config in self.wallets.items():
            if config.enabled:
                if config.wallet_type == WalletType.MULTI_SIG:
                    if not config.multi_sig_threshold or config.multi_sig_threshold <= 0:
                        errors.append(f"Multi-sig wallet '{wallet_name}' has invalid threshold")
                    if len(config.multi_sig_addresses) < config.multi_sig_threshold:
                        errors.append(f"Multi-sig wallet '{wallet_name}' has insufficient addresses")
        
        # Validate exchange configurations
        for exchange_name, config in self.exchanges.items():
            if config.enabled:
                if not config.supported_pairs:
                    errors.append(f"Exchange '{exchange_name}' has no supported pairs")
                if config.minimum_trade_amount <= 0:
                    errors.append(f"Exchange '{exchange_name}' has invalid minimum trade amount")
        
        # Validate smart contract configurations
        for contract_name, config in self.smart_contracts.items():
            if config.enabled:
                if not config.contract_address:
                    errors.append(f"Smart contract '{contract_name}' has no address configured")
                if config.gas_limit <= 0:
                    errors.append(f"Smart contract '{contract_name}' has invalid gas limit")
        
        # Validate security configuration
        limits = self.security_config.get("transaction_limits", {})
        if limits.get("transaction_limit_usd", 0) > limits.get("daily_limit_usd", 0):
            errors.append("Transaction limit exceeds daily limit")
        
        return errors


# Global crypto payment settings instance
crypto_payment_settings = CryptoPaymentSettings()

__all__ = [
    "CryptoPaymentSettings",
    "crypto_payment_settings",
    "CryptoCurrency",
    "BlockchainNetwork",
    "WalletType",
    "TransactionType",
    "SecurityLevel",
    "ComplianceFramework",
    "CryptoCurrencyConfig",
    "WalletConfiguration",
    "ExchangeIntegration",
    "SmartContractConfig"
]