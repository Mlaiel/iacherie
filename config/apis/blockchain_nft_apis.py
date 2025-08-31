"""Blockchain & NFT APIs Configuration - IA-Influencer Agent Platform
================================================================
Professional blockchain integration for content protection,
NFT minting, smart contracts, and decentralized monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️ PROPRIÉTÉ EXCLUSIVE DE FAHED MLAIEL
Toute tentative de copie, vol ou réutilisation sans autorisation écrite
de Fahed Mlaiel (mlaiel@live.de) sera poursuivie en justice selon la loi allemande.
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from decimal import Decimal


class BlockchainNetwork(Enum):
    """Blockchain networks enumeration."""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_GOERLI = "ethereum_goerli"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON_MAINNET = "polygon_mainnet"
    POLYGON_MUMBAI = "polygon_mumbai"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    AVALANCHE = "avalanche"
    SOLANA_MAINNET = "solana_mainnet"
    SOLANA_DEVNET = "solana_devnet"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class TokenStandard(Enum):
    """Token standards enumeration."""
    ERC721 = "erc721"  # NFT standard
    ERC1155 = "erc1155"  # Multi-token standard
    ERC20 = "erc20"  # Fungible token standard
    SPL_TOKEN = "spl_token"  # Solana token standard
    BEP721 = "bep721"  # Binance NFT standard


class ContractType(Enum):
    """Smart contract types."""
    NFT_COLLECTION = "nft_collection"
    MARKETPLACE = "marketplace"
    ROYALTY_SPLITTER = "royalty_splitter"
    CONTENT_PROTECTION = "content_protection"
    LICENSING = "licensing"
    GOVERNANCE = "governance"
    STAKING = "staking"
    AUCTION = "auction"


@dataclass
class BlockchainConfig:
    """Blockchain network configuration."""
    network: BlockchainNetwork
    rpc_url: str
    ws_url: str
    chain_id: int
    currency_symbol: str
    block_explorer_url: str
    gas_limit: int
    gas_price_gwei: Decimal
    confirmation_blocks: int
    transaction_timeout: int
    retry_attempts: int
    rate_limit: int
    api_key: str


@dataclass
class NFTMetadata:
    """NFT metadata structure."""
    name: str
    description: str
    image: str
    external_url: Optional[str]
    animation_url: Optional[str]
    youtube_url: Optional[str]
    background_color: Optional[str]
    attributes: List[Dict[str, Any]]
    properties: Dict[str, Any]
    levels: Dict[str, Any]
    stats: Dict[str, Any]
    created_by: str
    created_date: str
    content_type: str
    content_hash: str
    fingerprint_hash: str
    protection_level: str
    royalty_percentage: Decimal
    licensing_terms: str


@dataclass
class SmartContractConfig:
    """Smart contract configuration."""
    contract_type: ContractType
    contract_address: str
    abi: List[Dict[str, Any]]
    bytecode: Optional[str]
    constructor_args: List[Any]
    gas_limit: int
    gas_price: Decimal
    network: BlockchainNetwork
    owner_address: str
    proxy_address: Optional[str]
    implementation_address: Optional[str]
    verified: bool
    source_code: Optional[str]


class BlockchainAPIsConfig:
    """Professional Blockchain & NFT APIs configuration."""
    
    def __init__(self):
        """Initialize blockchain configuration."""
        self.networks = self._get_network_configs()
        self.contracts = self._get_contract_configs()
        self.nft_collections = self._get_nft_collection_configs()
        self.marketplace_configs = self._get_marketplace_configs()
        self.royalty_configs = self._get_royalty_configs()
        self.protection_configs = self._get_protection_configs()
        self.wallet_configs = self._get_wallet_configs()
    
    def _get_network_configs(self) -> Dict[BlockchainNetwork, BlockchainConfig]:
        """Get blockchain network configurations."""
        return {
            BlockchainNetwork.ETHEREUM_MAINNET: BlockchainConfig(
                network=BlockchainNetwork.ETHEREUM_MAINNET,
                rpc_url=os.getenv("ETHEREUM_MAINNET_RPC", "https://mainnet.infura.io/v3/"),
                ws_url=os.getenv("ETHEREUM_MAINNET_WS", "wss://mainnet.infura.io/ws/v3/"),
                chain_id=1,
                currency_symbol="ETH",
                block_explorer_url="https://etherscan.io",
                gas_limit=300000,
                gas_price_gwei=Decimal("20.0"),
                confirmation_blocks=12,
                transaction_timeout=300,
                retry_attempts=3,
                rate_limit=100,
                api_key=os.getenv("ETHEREUM_API_KEY", "")
            ),
            
            BlockchainNetwork.POLYGON_MAINNET: BlockchainConfig(
                network=BlockchainNetwork.POLYGON_MAINNET,
                rpc_url=os.getenv("POLYGON_MAINNET_RPC", "https://polygon-mainnet.infura.io/v3/"),
                ws_url=os.getenv("POLYGON_MAINNET_WS", "wss://polygon-mainnet.infura.io/ws/v3/"),
                chain_id=137,
                currency_symbol="MATIC",
                block_explorer_url="https://polygonscan.com",
                gas_limit=500000,
                gas_price_gwei=Decimal("30.0"),
                confirmation_blocks=20,
                transaction_timeout=180,
                retry_attempts=3,
                rate_limit=200,
                api_key=os.getenv("POLYGON_API_KEY", "")
            ),
            
            BlockchainNetwork.SOLANA_MAINNET: BlockchainConfig(
                network=BlockchainNetwork.SOLANA_MAINNET,
                rpc_url=os.getenv("SOLANA_MAINNET_RPC", "https://api.mainnet-beta.solana.com"),
                ws_url=os.getenv("SOLANA_MAINNET_WS", "wss://api.mainnet-beta.solana.com"),
                chain_id=101,
                currency_symbol="SOL",
                block_explorer_url="https://explorer.solana.com",
                gas_limit=200000,
                gas_price_gwei=Decimal("0.000005"),
                confirmation_blocks=32,
                transaction_timeout=120,
                retry_attempts=5,
                rate_limit=300,
                api_key=os.getenv("SOLANA_API_KEY", "")
            )
        }
    
    def _get_contract_configs(self) -> Dict[str, SmartContractConfig]:
        """Get smart contract configurations."""
        return {
            'ia_content_nft': SmartContractConfig(
                contract_type=ContractType.NFT_COLLECTION,
                contract_address=os.getenv("IA_CONTENT_NFT_CONTRACT", ""),
                abi=[
                    {
                        "inputs": [
                            {"name": "to", "type": "address"},
                            {"name": "tokenURI", "type": "string"},
                            {"name": "contentHash", "type": "bytes32"},
                            {"name": "royaltyPercentage", "type": "uint256"}
                        ],
                        "name": "safeMint",
                        "outputs": [{"name": "tokenId", "type": "uint256"}],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"name": "tokenId", "type": "uint256"}],
                        "name": "getContentHash",
                        "outputs": [{"name": "", "type": "bytes32"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ],
                bytecode=None,
                constructor_args=[
                    "IA-Influencer Content",
                    "IAC",
                    "https://api.ia-influencer.com/metadata/"
                ],
                gas_limit=5000000,
                gas_price=Decimal("20.0"),
                network=BlockchainNetwork.POLYGON_MAINNET,
                owner_address=os.getenv("CONTRACT_OWNER_ADDRESS", ""),
                proxy_address=None,
                implementation_address=None,
                verified=True,
                source_code=None
            ),
            
            'ia_marketplace': SmartContractConfig(
                contract_type=ContractType.MARKETPLACE,
                contract_address=os.getenv("IA_MARKETPLACE_CONTRACT", ""),
                abi=[
                    {
                        "inputs": [
                            {"name": "nftContract", "type": "address"},
                            {"name": "tokenId", "type": "uint256"},
                            {"name": "price", "type": "uint256"},
                            {"name": "duration", "type": "uint256"}
                        ],
                        "name": "createListing",
                        "outputs": [{"name": "listingId", "type": "uint256"}],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"name": "listingId", "type": "uint256"}],
                        "name": "buyItem",
                        "outputs": [],
                        "stateMutability": "payable",
                        "type": "function"
                    }
                ],
                bytecode=None,
                constructor_args=[
                    Decimal("2.5"),  # 2.5% marketplace fee
                    os.getenv("TREASURY_ADDRESS", "")
                ],
                gas_limit=3000000,
                gas_price=Decimal("25.0"),
                network=BlockchainNetwork.POLYGON_MAINNET,
                owner_address=os.getenv("CONTRACT_OWNER_ADDRESS", ""),
                proxy_address=None,
                implementation_address=None,
                verified=True,
                source_code=None
            ),
            
            'royalty_splitter': SmartContractConfig(
                contract_type=ContractType.ROYALTY_SPLITTER,
                contract_address=os.getenv("ROYALTY_SPLITTER_CONTRACT", ""),
                abi=[
                    {
                        "inputs": [
                            {"name": "payees", "type": "address[]"},
                            {"name": "shares", "type": "uint256[]"}
                        ],
                        "name": "addPayees",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"name": "account", "type": "address"}],
                        "name": "release",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ],
                bytecode=None,
                constructor_args=[],
                gas_limit=2000000,
                gas_price=Decimal("20.0"),
                network=BlockchainNetwork.POLYGON_MAINNET,
                owner_address=os.getenv("CONTRACT_OWNER_ADDRESS", ""),
                proxy_address=None,
                implementation_address=None,
                verified=True,
                source_code=None
            )
        }
    
    def _get_nft_collection_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get NFT collection configurations."""
        return {
            'music_nfts': {
                'collection_name': 'IA-Influencer Music',
                'collection_symbol': 'IAM',
                'base_uri': 'https://api.ia-influencer.com/nft/music/',
                'max_supply': 10000,
                'mint_price': Decimal("0.1"),
                'royalty_percentage': Decimal("10.0"),
                'creator_address': os.getenv("CREATOR_ADDRESS", ""),
                'attributes': [
                    {'trait_type': 'Genre', 'values': ['Pop', 'Rock', 'Electronic', 'Jazz', 'Classical']},
                    {'trait_type': 'Mood', 'values': ['Happy', 'Sad', 'Energetic', 'Calm', 'Mysterious']},
                    {'trait_type': 'Tempo', 'values': ['Slow', 'Medium', 'Fast', 'Variable']},
                    {'trait_type': 'Duration', 'values': ['Short', 'Medium', 'Long', 'Extended']},
                    {'trait_type': 'Protection Level', 'values': ['Basic', 'Advanced', 'Premium', 'Ultimate']}
                ],
                'levels': [
                    {'trait_type': 'Rarity Score', 'min_value': 1, 'max_value': 100},
                    {'trait_type': 'Popularity', 'min_value': 0, 'max_value': 1000},
                    {'trait_type': 'Stream Count', 'min_value': 0, 'max_value': 1000000}
                ]
            },
            
            'video_nfts': {
                'collection_name': 'IA-Influencer Videos',
                'collection_symbol': 'IAV',
                'base_uri': 'https://api.ia-influencer.com/nft/video/',
                'max_supply': 5000,
                'mint_price': Decimal("0.2"),
                'royalty_percentage': Decimal("12.5"),
                'creator_address': os.getenv("CREATOR_ADDRESS", ""),
                'attributes': [
                    {'trait_type': 'Type', 'values': ['Music Video', 'Documentary', 'Performance', 'Tutorial']},
                    {'trait_type': 'Quality', 'values': ['HD', 'Full HD', '4K', '8K']},
                    {'trait_type': 'Duration', 'values': ['Short', 'Medium', 'Feature Length']},
                    {'trait_type': 'Style', 'values': ['Cinematic', 'Documentary', 'Animated', 'Live Action']}
                ]
            },
            
            'image_nfts': {
                'collection_name': 'IA-Influencer Images',
                'collection_symbol': 'IAI',
                'base_uri': 'https://api.ia-influencer.com/nft/image/',
                'max_supply': 20000,
                'mint_price': Decimal("0.05"),
                'royalty_percentage': Decimal("8.0"),
                'creator_address': os.getenv("CREATOR_ADDRESS", ""),
                'attributes': [
                    {'trait_type': 'Type', 'values': ['Album Art', 'Photography', 'Digital Art', 'Poster']},
                    {'trait_type': 'Style', 'values': ['Abstract', 'Realistic', 'Minimalist', 'Vintage']},
                    {'trait_type': 'Colors', 'values': ['Monochrome', 'Colorful', 'Pastel', 'Neon']},
                    {'trait_type': 'Resolution', 'values': ['Standard', 'High', 'Ultra', 'Print Quality']}
                ]
            }
        }
    
    def _get_marketplace_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get marketplace configurations."""
        return {
            'primary_marketplace': {
                'platform_fee': Decimal("2.5"),
                'payment_tokens': ['ETH', 'MATIC', 'USDC', 'USDT'],
                'auction_types': ['fixed_price', 'english_auction', 'dutch_auction'],
                'minimum_bid_increment': Decimal("0.01"),
                'auction_duration_min': 3600,  # 1 hour
                'auction_duration_max': 604800,  # 1 week
                'listing_duration_max': 2592000,  # 30 days
                'cancellation_fee': Decimal("0.001"),
                'supported_standards': [TokenStandard.ERC721, TokenStandard.ERC1155],
                'verification_required': True,
                'kyc_required': False,
                'content_moderation': True
            },
            
            'secondary_marketplace': {
                'platform_fee': Decimal("1.0"),
                'royalty_enforcement': True,
                'cross_chain_support': True,
                'bulk_operations': True,
                'price_discovery': True,
                'analytics_tracking': True,
                'social_features': True,
                'recommendation_engine': True
            }
        }
    
    def _get_royalty_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get royalty configurations."""
        return {
            'creator_royalties': {
                'default_percentage': Decimal("10.0"),
                'minimum_percentage': Decimal("2.5"),
                'maximum_percentage': Decimal("20.0"),
                'payment_frequency': 'monthly',
                'minimum_payout': Decimal("0.01"),
                'supported_tokens': ['ETH', 'MATIC', 'USDC'],
                'automatic_distribution': True,
                'tax_reporting': True
            },
            
            'platform_royalties': {
                'platform_percentage': Decimal("2.5"),
                'referral_percentage': Decimal("1.0"),
                'staking_rewards_percentage': Decimal("0.5"),
                'treasury_percentage': Decimal("1.0"),
                'burn_percentage': Decimal("0.0")
            },
            
            'collaboration_royalties': {
                'multi_creator_support': True,
                'automatic_splitting': True,
                'dispute_resolution': True,
                'smart_contract_enforcement': True,
                'percentage_modification': False,
                'vesting_schedules': True
            }
        }
    
    def _get_protection_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get content protection configurations."""
        return {
            'on_chain_protection': {
                'content_hashing': 'sha256',
                'fingerprint_storage': True,
                'ownership_verification': True,
                'timestamp_verification': True,
                'immutable_records': True,
                'decentralized_storage': True,
                'ipfs_integration': True,
                'arweave_integration': True
            },
            
            'smart_contract_protection': {
                'access_control': True,
                'transfer_restrictions': True,
                'burn_protection': True,
                'metadata_immutability': True,
                'upgrade_protection': True,
                'multi_signature_required': True,
                'time_locks': True,
                'emergency_pause': True
            },
            
            'legal_integration': {
                'dmca_compliance': True,
                'copyright_registration': True,
                'automated_takedowns': True,
                'legal_document_storage': True,
                'dispute_resolution': True,
                'international_protection': True
            }
        }
    
    def _get_wallet_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get wallet configurations."""
        return {
            'supported_wallets': {
                'metamask': {
                    'enabled': True,
                    'connection_type': 'injected',
                    'networks': ['ethereum', 'polygon', 'binance_smart_chain'],
                    'features': ['signing', 'transactions', 'network_switching']
                },
                'walletconnect': {
                    'enabled': True,
                    'connection_type': 'qr_code',
                    'networks': ['ethereum', 'polygon', 'solana'],
                    'features': ['mobile_support', 'signing', 'transactions']
                },
                'phantom': {
                    'enabled': True,
                    'connection_type': 'injected',
                    'networks': ['solana'],
                    'features': ['nft_viewing', 'signing', 'transactions']
                },
                'coinbase_wallet': {
                    'enabled': True,
                    'connection_type': 'injected',
                    'networks': ['ethereum', 'polygon'],
                    'features': ['fiat_onramp', 'signing', 'transactions']
                }
            },
            
            'security_settings': {
                'transaction_signing_required': True,
                'network_verification': True,
                'contract_verification': True,
                'amount_verification': True,
                'recipient_verification': True,
                'gas_estimation': True,
                'slippage_protection': True,
                'mev_protection': True
            }
        }
    
    def get_network_config(self, network: BlockchainNetwork) -> Optional[BlockchainConfig]:
        """Get blockchain network configuration."""
        return self.networks.get(network)
    
    def get_contract_config(self, contract_name: str) -> Optional[SmartContractConfig]:
        """Get smart contract configuration."""
        return self.contracts.get(contract_name)
    
    def get_nft_collection_config(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get NFT collection configuration."""
        return self.nft_collections.get(collection_name)


# Global configuration instance
blockchain_apis_config = BlockchainAPIsConfig()


def get_blockchain_network(network: BlockchainNetwork) -> Optional[BlockchainConfig]:
    """Get blockchain network configuration."""
    return blockchain_apis_config.get_network_config(network)


def get_smart_contract(contract_name: str) -> Optional[SmartContractConfig]:
    """Get smart contract configuration."""
    return blockchain_apis_config.get_contract_config(contract_name)


def get_nft_collection(collection_name: str) -> Optional[Dict[str, Any]]:
    """Get NFT collection configuration."""
    return blockchain_apis_config.get_nft_collection_config(collection_name)


def create_nft_metadata(
    name: str,
    description: str,
    image_url: str,
    content_hash: str,
    fingerprint_hash: str,
    creator: str,
    attributes: List[Dict[str, Any]],
    royalty_percentage: Decimal = Decimal("10.0")
) -> NFTMetadata:
    """Create NFT metadata structure."""
    from datetime import datetime
    
    return NFTMetadata(
        name=name,
        description=description,
        image=image_url,
        external_url=f"https://ia-influencer.com/content/{content_hash}",
        animation_url=None,
        youtube_url=None,
        background_color=None,
        attributes=attributes,
        properties={
            "content_protection": True,
            "ai_fingerprinted": True,
            "blockchain_verified": True
        },
        levels={},
        stats={},
        created_by=creator,
        created_date=datetime.now().isoformat(),
        content_type="auto_detected",
        content_hash=content_hash,
        fingerprint_hash=fingerprint_hash,
        protection_level="premium",
        royalty_percentage=royalty_percentage,
        licensing_terms="Standard Creator License"
    )
