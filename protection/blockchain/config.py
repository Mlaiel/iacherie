"""Blockchain Module Configuration
Professional configuration management for all blockchain services

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
"""from typing import Dict, Any, List, Optional
from enum import Enum
import os
from dataclasses import dataclass


class Environment(Enum):
    """Deployment environments"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class BlockchainConfig:
    """Complete blockchain module configuration"""    
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    debug_mode: bool = True
    
    # Network configurations
    ethereum_config: Dict[str, Any] = None
    polygon_config: Dict[str, Any] = None
    bsc_config: Dict[str, Any] = None
    
    # Service configurations
    ipfs_config: Dict[str, Any] = None
    arweave_config: Dict[str, Any] = None
    hyperledger_config: Dict[str, Any] = None
    
    # Security settings
    encryption_key: str = ""
    private_keys: Dict[str, str] = None
    api_keys: Dict[str, str] = None
    
    # Performance settings
    max_concurrent_transactions: int = 10
    transaction_timeout: int = 300
    retry_attempts: int = 3
    cache_ttl: int = 3600
    
    def __post_init__(self):
        """Initialize default configurations"""        if self.ethereum_config is None:
            self.ethereum_config = self._get_default_ethereum_config()
        
        if self.polygon_config is None:
            self.polygon_config = self._get_default_polygon_config()
        
        if self.bsc_config is None:
            self.bsc_config = self._get_default_bsc_config()
        
        if self.ipfs_config is None:
            self.ipfs_config = self._get_default_ipfs_config()
        
        if self.arweave_config is None:
            self.arweave_config = self._get_default_arweave_config()
        
        if self.private_keys is None:
            self.private_keys = {}
        
        if self.api_keys is None:
            self.api_keys = {}
    
    def _get_default_ethereum_config(self) -> Dict[str, Any]:
        """Default Ethereum configuration"""        if self.environment == Environment.PRODUCTION:
            return {
                'name': 'Ethereum Mainnet',
                'chain_id': 1,
                'rpc_url': 'https://mainnet.infura.io/v3/',
                'explorer_url': 'https://etherscan.io',
                'gas_price_gwei': 20,
                'block_time': 13,
                'confirmations_required': 12
            }
        else:
            return {
                'name': 'Ethereum Sepolia',
                'chain_id': 11155111,
                'rpc_url': 'https://sepolia.infura.io/v3/',
                'explorer_url': 'https://sepolia.etherscan.io',
                'gas_price_gwei': 10,
                'block_time': 13,
                'confirmations_required': 3
            }
    
    def _get_default_polygon_config(self) -> Dict[str, Any]:
        """Default Polygon configuration"""        if self.environment == Environment.PRODUCTION:
            return {
                'name': 'Polygon Mainnet',
                'chain_id': 137,
                'rpc_url': 'https://polygon-rpc.com/',
                'explorer_url': 'https://polygonscan.com',
                'gas_price_gwei': 30,
                'block_time': 2,
                'confirmations_required': 6
            }
        else:
            return {
                'name': 'Polygon Mumbai',
                'chain_id': 80001,
                'rpc_url': 'https://rpc-mumbai.maticvigil.com/',
                'explorer_url': 'https://mumbai.polygonscan.com',
                'gas_price_gwei': 1,
                'block_time': 2,
                'confirmations_required': 3
            }
    
    def _get_default_bsc_config(self) -> Dict[str, Any]:
        """Default Binance Smart Chain configuration"""        if self.environment == Environment.PRODUCTION:
            return {
                'name': 'BSC Mainnet',
                'chain_id': 56,
                'rpc_url': 'https://bsc-dataseed.binance.org/',
                'explorer_url': 'https://bscscan.com',
                'gas_price_gwei': 5,
                'block_time': 3,
                'confirmations_required': 6
            }
        else:
            return {
                'name': 'BSC Testnet',
                'chain_id': 97,
                'rpc_url': 'https://data-seed-prebsc-1-s1.binance.org:8545/',
                'explorer_url': 'https://testnet.bscscan.com',
                'gas_price_gwei': 5,
                'block_time': 3,
                'confirmations_required': 3
            }
    
    def _get_default_ipfs_config(self) -> Dict[str, Any]:
        """Default IPFS configuration"""        return {
            'api_url': '/ip4/127.0.0.1/tcp/5001',
            'gateway_url': 'https://ipfs.io/ipfs/',
            'timeout': 30,
            'pin_on_add': True,
            'public_gateways': [
                'https://ipfs.io/ipfs/',
                'https://gateway.pinata.cloud/ipfs/',
                'https://cloudflare-ipfs.com/ipfs/'
            ]
        }
    
    def _get_default_arweave_config(self) -> Dict[str, Any]:
        """Default Arweave configuration"""        return {
            'host': 'arweave.net',
            'port': 443,
            'protocol': 'https',
            'timeout': 20000,
            'logging': False
        }


def load_config_from_env() -> BlockchainConfig:
    """Load configuration from environment variables"""    config = BlockchainConfig()
    
    # Environment detection
    env_name = os.getenv('BLOCKCHAIN_ENV', 'development').lower()
    try:
        config.environment = Environment(env_name)
    except ValueError:
        config.environment = Environment.DEVELOPMENT
    
    # Debug mode
    config.debug_mode = os.getenv('BLOCKCHAIN_DEBUG', 'true').lower() == 'true'
    
    # Security settings
    config.encryption_key = os.getenv('BLOCKCHAIN_ENCRYPTION_KEY', '')
    
    # API Keys
    config.api_keys = {
        'infura': os.getenv('INFURA_API_KEY', ''),
        'alchemy': os.getenv('ALCHEMY_API_KEY', ''),
        'moralis': os.getenv('MORALIS_API_KEY', ''),
        'pinata': os.getenv('PINATA_API_KEY', ''),
        'arweave': os.getenv('ARWEAVE_API_KEY', '')
    }
    
    # Private keys (in production, use secure key management)
    config.private_keys = {
        'ethereum': os.getenv('ETHEREUM_PRIVATE_KEY', ''),
        'polygon': os.getenv('POLYGON_PRIVATE_KEY', ''),
        'bsc': os.getenv('BSC_PRIVATE_KEY', '')
    }
    
    # Performance settings
    config.max_concurrent_transactions = int(os.getenv('MAX_CONCURRENT_TX', '10'))
    config.transaction_timeout = int(os.getenv('TRANSACTION_TIMEOUT', '300'))
    config.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', '3'))
    config.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
    
    # Update RPC URLs with API keys if available
    if config.api_keys.get('infura'):
        infura_key = config.api_keys['infura']
        config.ethereum_config['rpc_url'] += infura_key
        config.polygon_config['rpc_url'] = f'https://polygon-mainnet.infura.io/v3/{infura_key}'
    
    return config


def get_production_config() -> BlockchainConfig:
    """Get production-ready configuration"""    config = BlockchainConfig(
        environment=Environment.PRODUCTION,
        debug_mode=False,
        max_concurrent_transactions=20,
        transaction_timeout=600,
        retry_attempts=5
    )
    
    # Load sensitive data from secure storage
    # In production, use AWS Secrets Manager, Azure Key Vault, etc.
    config = load_config_from_env()
    config.environment = Environment.PRODUCTION
    config.debug_mode = False
    
    return config


def get_development_config() -> BlockchainConfig:
    """Get development configuration"""    return BlockchainConfig(
        environment=Environment.DEVELOPMENT,
        debug_mode=True,
        max_concurrent_transactions=5,
        transaction_timeout=120,
        retry_attempts=2
    )


def get_testing_config() -> BlockchainConfig:
    """Get testing configuration"""    return BlockchainConfig(
        environment=Environment.TESTING,
        debug_mode=True,
        max_concurrent_transactions=3,
        transaction_timeout=60,
        retry_attempts=1
    )


# Default configuration instance
default_config = load_config_from_env()


__all__ = [
    'BlockchainConfig',
    'Environment',
    'load_config_from_env',
    'get_production_config',
    'get_development_config',
    'get_testing_config',
    'default_config'
]
