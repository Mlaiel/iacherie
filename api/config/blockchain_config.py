"""
Blockchain Configuration - IA Influencer Agent Platform
Comprehensive blockchain configuration for smart contracts and Web3 integration

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import web3
from web3 import Web3


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON_MAINNET = "polygon_mainnet"
    POLYGON_MUMBAI = "polygon_mumbai"
    BSC_MAINNET = "bsc_mainnet"
    BSC_TESTNET = "bsc_testnet"
    AVALANCHE_MAINNET = "avalanche_mainnet"
    AVALANCHE_FUJI = "avalanche_fuji"
    ARBITRUM_ONE = "arbitrum_one"
    OPTIMISM_MAINNET = "optimism_mainnet"


class ContractType(Enum):
    """Smart contract types"""
    CONTENT_PROTECTION = "content_protection"
    COPYRIGHT_REGISTRY = "copyright_registry"
    ROYALTY_DISTRIBUTION = "royalty_distribution"
    LICENSING_AGREEMENT = "licensing_agreement"
    CREATOR_IDENTITY = "creator_identity"
    PAYMENT_PROCESSOR = "payment_processor"


@dataclass
class NetworkConfig:
    """Configuration for a specific blockchain network"""
    
    name: str
    rpc_url: str
    chain_id: int
    currency_symbol: str
    block_explorer_url: str
    is_testnet: bool = False
    gas_price_gwei: Optional[int] = None
    max_priority_fee_gwei: Optional[int] = None
    max_fee_gwei: Optional[int] = None


@dataclass
class BlockchainConfig:
    """Comprehensive blockchain configuration"""
    
    # Default Network
    default_network: BlockchainNetwork = field(default_factory=lambda: 
        BlockchainNetwork(os.getenv("BLOCKCHAIN_DEFAULT_NETWORK", "ethereum_sepolia")))
    
    # Network Configurations
    networks: Dict[BlockchainNetwork, NetworkConfig] = field(default_factory=lambda: {
        BlockchainNetwork.ETHEREUM_MAINNET: NetworkConfig(
            name="Ethereum Mainnet",
            rpc_url=os.getenv("ETHEREUM_MAINNET_RPC", "https://mainnet.infura.io/v3/YOUR_API_KEY"),
            chain_id=1,
            currency_symbol="ETH",
            block_explorer_url="https://etherscan.io",
            gas_price_gwei=20
        ),
        BlockchainNetwork.ETHEREUM_SEPOLIA: NetworkConfig(
            name="Ethereum Sepolia",
            rpc_url=os.getenv("ETHEREUM_SEPOLIA_RPC", "https://sepolia.infura.io/v3/YOUR_API_KEY"),
            chain_id=11155111,
            currency_symbol="ETH",
            block_explorer_url="https://sepolia.etherscan.io",
            is_testnet=True,
            gas_price_gwei=10
        ),
        BlockchainNetwork.POLYGON_MAINNET: NetworkConfig(
            name="Polygon Mainnet",
            rpc_url=os.getenv("POLYGON_MAINNET_RPC", "https://polygon-rpc.com"),
            chain_id=137,
            currency_symbol="MATIC",
            block_explorer_url="https://polygonscan.com",
            gas_price_gwei=30
        ),
        BlockchainNetwork.POLYGON_MUMBAI: NetworkConfig(
            name="Polygon Mumbai",
            rpc_url=os.getenv("POLYGON_MUMBAI_RPC", "https://rpc-mumbai.maticvigil.com"),
            chain_id=80001,
            currency_symbol="MATIC",
            block_explorer_url="https://mumbai.polygonscan.com",
            is_testnet=True,
            gas_price_gwei=1
        ),
        BlockchainNetwork.BSC_MAINNET: NetworkConfig(
            name="Binance Smart Chain",
            rpc_url=os.getenv("BSC_MAINNET_RPC", "https://bsc-dataseed1.binance.org"),
            chain_id=56,
            currency_symbol="BNB",
            block_explorer_url="https://bscscan.com",
            gas_price_gwei=5
        ),
        BlockchainNetwork.AVALANCHE_MAINNET: NetworkConfig(
            name="Avalanche C-Chain",
            rpc_url=os.getenv("AVALANCHE_MAINNET_RPC", "https://api.avax.network/ext/bc/C/rpc"),
            chain_id=43114,
            currency_symbol="AVAX",
            block_explorer_url="https://snowtrace.io",
            gas_price_gwei=25
        )
    })
    
    # Wallet Configuration
    private_key: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_PRIVATE_KEY"))
    wallet_address: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_WALLET_ADDRESS"))
    mnemonic: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_MNEMONIC"))
    keystore_path: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_KEYSTORE_PATH"))
    keystore_password: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_KEYSTORE_PASSWORD"))
    
    # Gas Configuration
    default_gas_limit: int = field(default_factory=lambda: int(os.getenv("BLOCKCHAIN_GAS_LIMIT", "500000")))
    default_gas_price_gwei: int = field(default_factory=lambda: int(os.getenv("BLOCKCHAIN_GAS_PRICE_GWEI", "20")))
    max_gas_price_gwei: int = field(default_factory=lambda: int(os.getenv("BLOCKCHAIN_MAX_GAS_PRICE_GWEI", "100")))
    gas_price_strategy: str = field(default_factory=lambda: os.getenv("BLOCKCHAIN_GAS_STRATEGY", "medium"))
    
    # Transaction Configuration
    transaction_timeout_seconds: int = field(default_factory=lambda: 
        int(os.getenv("BLOCKCHAIN_TX_TIMEOUT", "300")))
    confirmation_blocks: int = field(default_factory=lambda: 
        int(os.getenv("BLOCKCHAIN_CONFIRMATION_BLOCKS", "12")))
    max_retry_attempts: int = field(default_factory=lambda: 
        int(os.getenv("BLOCKCHAIN_MAX_RETRY_ATTEMPTS", "3")))
    retry_delay_seconds: int = field(default_factory=lambda: 
        int(os.getenv("BLOCKCHAIN_RETRY_DELAY", "10")))
    
    # Smart Contract Addresses
    contract_addresses: Dict[ContractType, Dict[BlockchainNetwork, str]] = field(default_factory=dict)
    
    # Contract ABIs
    contract_abis: Dict[ContractType, List[Dict]] = field(default_factory=dict)
    
    # IPFS Configuration for metadata storage
    ipfs_enabled: bool = field(default_factory=lambda: 
        os.getenv("IPFS_ENABLED", "true").lower() == "true")
    ipfs_gateway: str = field(default_factory=lambda: 
        os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs/"))
    ipfs_api_url: str = field(default_factory=lambda: 
        os.getenv("IPFS_API_URL", "https://ipfs.infura.io:5001"))
    ipfs_api_key: Optional[str] = field(default_factory=lambda: os.getenv("IPFS_API_KEY"))
    ipfs_api_secret: Optional[str] = field(default_factory=lambda: os.getenv("IPFS_API_SECRET"))
    
    # Oracle Configuration
    oracle_enabled: bool = field(default_factory=lambda: 
        os.getenv("ORACLE_ENABLED", "false").lower() == "true")
    chainlink_oracle_addresses: Dict[str, str] = field(default_factory=dict)
    oracle_update_interval: int = field(default_factory=lambda: 
        int(os.getenv("ORACLE_UPDATE_INTERVAL", "3600")))  # 1 hour
    
    # Token Configuration
    platform_token_enabled: bool = field(default_factory=lambda: 
        os.getenv("PLATFORM_TOKEN_ENABLED", "false").lower() == "true")
    platform_token_symbol: str = field(default_factory=lambda: 
        os.getenv("PLATFORM_TOKEN_SYMBOL", "IAI"))
    platform_token_name: str = field(default_factory=lambda: 
        os.getenv("PLATFORM_TOKEN_NAME", "IA Influencer Token"))
    platform_token_decimals: int = field(default_factory=lambda: 
        int(os.getenv("PLATFORM_TOKEN_DECIMALS", "18")))
    
    # Staking Configuration
    staking_enabled: bool = field(default_factory=lambda: 
        os.getenv("STAKING_ENABLED", "false").lower() == "true")
    staking_rewards_apr: Decimal = field(default_factory=lambda: 
        Decimal(os.getenv("STAKING_REWARDS_APR", "12.0")))
    minimum_stake_amount: Decimal = field(default_factory=lambda: 
        Decimal(os.getenv("MINIMUM_STAKE_AMOUNT", "100.0")))
    
    # Governance Configuration
    governance_enabled: bool = field(default_factory=lambda: 
        os.getenv("GOVERNANCE_ENABLED", "false").lower() == "true")
    voting_period_blocks: int = field(default_factory=lambda: 
        int(os.getenv("VOTING_PERIOD_BLOCKS", "40320")))  # ~7 days on Ethereum
    proposal_threshold: Decimal = field(default_factory=lambda: 
        Decimal(os.getenv("PROPOSAL_THRESHOLD", "10000.0")))
    
    # Monitoring and Analytics
    blockchain_analytics_enabled: bool = field(default_factory=lambda: 
        os.getenv("BLOCKCHAIN_ANALYTICS_ENABLED", "true").lower() == "true")
    dune_analytics_api_key: Optional[str] = field(default_factory=lambda: 
        os.getenv("DUNE_ANALYTICS_API_KEY"))
    the_graph_api_key: Optional[str] = field(default_factory=lambda: 
        os.getenv("THE_GRAPH_API_KEY"))
    
    # Security Configuration
    multi_sig_enabled: bool = field(default_factory=lambda: 
        os.getenv("MULTI_SIG_ENABLED", "false").lower() == "true")
    multi_sig_threshold: int = field(default_factory=lambda: 
        int(os.getenv("MULTI_SIG_THRESHOLD", "2")))
    multi_sig_owners: List[str] = field(default_factory=list)
    
    # Development Configuration
    development_mode: bool = field(default_factory=lambda: 
        os.getenv("BLOCKCHAIN_DEVELOPMENT_MODE", "true").lower() == "true")
    use_local_blockchain: bool = field(default_factory=lambda: 
        os.getenv("USE_LOCAL_BLOCKCHAIN", "false").lower() == "true")
    local_blockchain_url: str = field(default_factory=lambda: 
        os.getenv("LOCAL_BLOCKCHAIN_URL", "http://127.0.0.1:8545"))
    
    def __post_init__(self):
        """Initialize blockchain configuration"""
        self._validate_configuration()
        self._initialize_contract_addresses()
        self._initialize_contract_abis()
    
    def _validate_configuration(self):
        """Validate blockchain configuration"""
        if not self.private_key and not self.mnemonic and not self.keystore_path:
            if not self.development_mode:
                raise ValueError("Private key, mnemonic, or keystore must be provided")
        
        if self.multi_sig_enabled and self.multi_sig_threshold > len(self.multi_sig_owners):
            raise ValueError("Multi-sig threshold cannot exceed number of owners")
        
        if self.default_gas_price_gwei > self.max_gas_price_gwei:
            raise ValueError("Default gas price cannot exceed maximum gas price")
    
    def _initialize_contract_addresses(self):
        """Initialize smart contract addresses"""
        # Example contract addresses - replace with actual deployed addresses
        self.contract_addresses = {
            ContractType.CONTENT_PROTECTION: {
                BlockchainNetwork.ETHEREUM_SEPOLIA: "0x1234567890123456789012345678901234567890",
                BlockchainNetwork.POLYGON_MUMBAI: "0x0987654321098765432109876543210987654321"
            },
            ContractType.COPYRIGHT_REGISTRY: {
                BlockchainNetwork.ETHEREUM_SEPOLIA: "0x2345678901234567890123456789012345678901",
                BlockchainNetwork.POLYGON_MUMBAI: "0x1987654321098765432109876543210987654321"
            },
            ContractType.ROYALTY_DISTRIBUTION: {
                BlockchainNetwork.ETHEREUM_SEPOLIA: "0x3456789012345678901234567890123456789012",
                BlockchainNetwork.POLYGON_MUMBAI: "0x2987654321098765432109876543210987654321"
            }
        }
    
    def _initialize_contract_abis(self):
        """Initialize smart contract ABIs"""
        # Basic ABI structures - replace with actual contract ABIs
        self.contract_abis = {
            ContractType.CONTENT_PROTECTION: [
                {
                    "inputs": [
                        {"name": "contentHash", "type": "string"},
                        {"name": "metadata", "type": "string"}
                    ],
                    "name": "registerContent",
                    "outputs": [{"name": "tokenId", "type": "uint256"}],
                    "type": "function"
                }
            ],
            ContractType.COPYRIGHT_REGISTRY: [
                {
                    "inputs": [
                        {"name": "owner", "type": "address"},
                        {"name": "contentHash", "type": "string"}
                    ],
                    "name": "registerCopyright",
                    "outputs": [{"name": "registrationId", "type": "uint256"}],
                    "type": "function"
                }
            ]
        }
    
    def get_network_config(self, network: Optional[BlockchainNetwork] = None) -> NetworkConfig:
        """Get configuration for specified network"""
        target_network = network or self.default_network
        return self.networks.get(target_network)
    
    def get_web3_instance(self, network: Optional[BlockchainNetwork] = None) -> Web3:
        """Create Web3 instance for specified network"""
        network_config = self.get_network_config(network)
        if not network_config:
            raise ValueError(f"Network configuration not found for {network}")
        
        if self.use_local_blockchain:
            provider = Web3.HTTPProvider(self.local_blockchain_url)
        else:
            provider = Web3.HTTPProvider(network_config.rpc_url)
        
        w3 = Web3(provider)
        
        # Set up account if private key is available
        if self.private_key:
            account = w3.eth.account.from_key(self.private_key)
            w3.eth.default_account = account.address
        
        return w3
    
    def get_contract_address(self, contract_type: ContractType, 
                           network: Optional[BlockchainNetwork] = None) -> Optional[str]:
        """Get smart contract address for specified type and network"""
        target_network = network or self.default_network
        return self.contract_addresses.get(contract_type, {}).get(target_network)
    
    def get_contract_abi(self, contract_type: ContractType) -> Optional[List[Dict]]:
        """Get smart contract ABI for specified type"""



        return self.contract_abis.get(contract_type)
    
    def get_contract_instance(self, contract_type: ContractType, 
                            network: Optional[BlockchainNetwork] = None):
        """Get contract instance for specified type and network"""
        w3 = self.get_web3_instance(network)
        address = self.get_contract_address(contract_type, network)
        abi = self.get_contract_abi(contract_type)
        
        if not address or not abi:
            raise ValueError(f"Contract address or ABI not found for {contract_type}")
        
        return w3.eth.contract(address=address, abi=abi)
    
    def estimate_gas_price(self, network: Optional[BlockchainNetwork] = None) -> int:
        """Estimate current gas price for network"""
        w3 = self.get_web3_instance(network)
        
        try:
            # Get current gas price from network
            current_gas_price = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(current_gas_price, 'gwei')
            
            # Apply strategy
            if self.gas_price_strategy == "fast":
                gas_price_gwei = int(gas_price_gwei * 1.2)
            elif self.gas_price_strategy == "slow":
                gas_price_gwei = int(gas_price_gwei * 0.8)
            # "medium" uses current price
            
            # Ensure within limits
            gas_price_gwei = min(gas_price_gwei, self.max_gas_price_gwei)
            gas_price_gwei = max(gas_price_gwei, 1)  # minimum 1 gwei
            
            return gas_price_gwei
        except Exception:
            # Fallback to default
            network_config = self.get_network_config(network)
            return network_config.gas_price_gwei or self.default_gas_price_gwei
    
    def build_transaction(self, contract_function, 
                         network: Optional[BlockchainNetwork] = None,
                         gas_limit: Optional[int] = None,
                         gas_price_gwei: Optional[int] = None) -> Dict[str, Any]:
        """Build transaction dictionary for contract function"""
        w3 = self.get_web3_instance(network)
        network_config = self.get_network_config(network)
        
        # Get account nonce
        if self.wallet_address:
            nonce = w3.eth.get_transaction_count(self.wallet_address)
        else:
            nonce = 0
        
        # Determine gas price
        if gas_price_gwei is None:
            gas_price_gwei = self.estimate_gas_price(network)
        
        # Determine gas limit
        if gas_limit is None:
            try:
                gas_limit = contract_function.estimate_gas()
                gas_limit = int(gas_limit * 1.2)  # Add 20% buffer
            except Exception:
                gas_limit = self.default_gas_limit
        
        transaction = {
            'chainId': network_config.chain_id,
            'gas': gas_limit,
            'gasPrice': w3.to_wei(gas_price_gwei, 'gwei'),
            'nonce': nonce
        }
        
        return transaction
    
    def sign_and_send_transaction(self, transaction_dict: Dict[str, Any], 
                                 network: Optional[BlockchainNetwork] = None) -> str:
        """Sign and send transaction"""
        if not self.private_key:
            raise ValueError("Private key required to sign transactions")
        
        w3 = self.get_web3_instance(network)
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction_dict, self.private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()
    
    def wait_for_transaction(self, tx_hash: str, 
                           network: Optional[BlockchainNetwork] = None,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """Wait for transaction confirmation"""
        w3 = self.get_web3_instance(network)
        timeout = timeout or self.transaction_timeout_seconds
        
        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash, 
            timeout=timeout,
            poll_latency=1
        )
        
        return dict(receipt)
    
    def get_transaction_status(self, tx_hash: str, 
                             network: Optional[BlockchainNetwork] = None) -> Dict[str, Any]:
        """Get transaction status and details"""
        w3 = self.get_web3_instance(network)
        
        try:
            transaction = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            current_block = w3.eth.block_number
            confirmations = current_block - receipt.blockNumber
            
            return {
                'hash': tx_hash,
                'status': 'success' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'gas_price': transaction.gasPrice,
                'confirmations': confirmations,
                'confirmed': confirmations >= self.confirmation_blocks
            }
        except Exception as e:
            return {
                'hash': tx_hash,
                'status': 'pending',
                'error': str(e)
            }
    
    def get_balance(self, address: str, 
                   network: Optional[BlockchainNetwork] = None) -> Dict[str, Union[int, str]]:
        """Get account balance"""
        w3 = self.get_web3_instance(network)
        network_config = self.get_network_config(network)
        
        balance_wei = w3.eth.get_balance(address)
        balance_ether = w3.from_wei(balance_wei, 'ether')
        
        return {
            'address': address,
            'balance_wei': balance_wei,
            'balance_ether': float(balance_ether),
            'currency': network_config.currency_symbol
        }
