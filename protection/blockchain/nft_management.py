"""
NFT (Non-Fungible Token) Management for Content Protection
Professional implementation of NFT minting, marketplace integration, and royalty management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineer & Blockchain Specialist: Advanced IA Processing
- Database Administrator & Security Expert: Data Protection
- Microservices Architect & Audio Processing: Multi-format Support  
- DevOps Engineer & IA Prompt Engineer: Production Deployment

 STRONG WARNING 
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
from decimal import Decimal
import json
import hashlib
import base64
import secrets
from pathlib import Path
import aiohttp
import aiofiles
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from PIL import Image
import io

from .exceptions import (
    NFTMintingError,
    NFTTransferError,
    ContractExecutionError,
    InsufficientFundsError,
    Web3ProviderError
)

logger = logging.getLogger(__name__)


class NFTStandard(Enum):
    """NFT standards supported"""
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    ERC998 = "erc998"  # Composable NFTs
    ERC2981 = "erc2981"  # NFT Royalty Standard


class NFTMarketplace(Enum):
    """Supported NFT marketplaces"""
    OPENSEA = "opensea"
    RARIBLE = "rarible"
    FOUNDATION = "foundation"
    SUPERRARE = "superrare"
    ASYNC_ART = "async_art"
    MAGIC_EDEN = "magic_eden"
    BLUR = "blur"


class ContentType(Enum):
    """Types of content that can be minted as NFTs"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    INTERACTIVE = "interactive"
    COMPOSITE = "composite"  # Multiple content types


class RoyaltyType(Enum):
    """Types of royalty mechanisms"""
    PERCENTAGE = "percentage"  # Percentage of sale price
    FIXED_AMOUNT = "fixed_amount"  # Fixed amount per sale
    TIERED = "tiered"  # Different rates based on sale price
    DECLINING = "declining"  # Decreasing over time


@dataclass
class NFTMetadata:
    """Comprehensive NFT metadata"""
    name: str
    description: str
    content_type: ContentType
    creator_address: str
    
    # Content references
    image_url: str = ""
    animation_url: str = ""
    external_url: str = ""
    
    # Technical attributes
    content_hash: str = ""
    file_size: int = 0
    duration: Optional[int] = None  # For audio/video in seconds
    dimensions: Optional[Tuple[int, int]] = None  # For images/video
    
    # Creative attributes
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    genre: str = ""
    mood: str = ""
    
    # Protection metadata
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    license_terms: Dict[str, Any] = field(default_factory=dict)
    usage_rights: List[str] = field(default_factory=list)
    
    # Provenance
    creation_date: datetime = field(default_factory=datetime.utcnow)
    minting_date: Optional[datetime] = None
    version: str = "1.0"
    
    def to_json_metadata(self) -> Dict[str, Any]:
        """Convert to standard NFT JSON metadata format"""
        metadata = {
            "name": self.name,
            "description": self.description,
            "image": self.image_url,
            "external_url": self.external_url,
            "attributes": self.attributes,
            "properties": {
                "content_type": self.content_type.value,
                "creator": self.creator_address,
                "content_hash": self.content_hash,
                "creation_date": self.creation_date.isoformat(),
                "version": self.version,
                "tags": self.tags,
                "genre": self.genre,
                "mood": self.mood
            }
        }
        
        # Add media-specific fields
        if self.animation_url:
            metadata["animation_url"] = self.animation_url
        
        if self.duration:
            metadata["properties"]["duration"] = self.duration
        
        if self.dimensions:
            metadata["properties"]["width"] = self.dimensions[0]
            metadata["properties"]["height"] = self.dimensions[1]
        
        # Add protection information
        if self.copyright_info:
            metadata["properties"]["copyright"] = self.copyright_info
        
        if self.license_terms:
            metadata["properties"]["license"] = self.license_terms
        
        return metadata


@dataclass
class RoyaltyInfo:
    """NFT royalty configuration"""
    recipient_address: str
    royalty_type: RoyaltyType
    rate_percentage: Decimal = Decimal('0')  # For percentage royalties
    fixed_amount_wei: int = 0  # For fixed amount royalties
    
    # Tiered royalties
    tiers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Declining royalties
    initial_rate: Decimal = Decimal('0')
    decline_rate: Decimal = Decimal('0')  # Per year
    minimum_rate: Decimal = Decimal('0')
    
    # Split royalties
    splits: List[Dict[str, Any]] = field(default_factory=list)  # Multiple recipients
    
    def calculate_royalty(self, sale_price_wei: int, sale_date: datetime) -> int:
        """Calculate royalty amount for a sale"""
        if self.royalty_type == RoyaltyType.PERCENTAGE:
            return int(sale_price_wei * float(self.rate_percentage) / 100)
        
        elif self.royalty_type == RoyaltyType.FIXED_AMOUNT:
            return self.fixed_amount_wei
        
        elif self.royalty_type == RoyaltyType.TIERED:
            return self._calculate_tiered_royalty(sale_price_wei)
        
        elif self.royalty_type == RoyaltyType.DECLINING:
            return self._calculate_declining_royalty(sale_price_wei, sale_date)
        
        return 0
    
    def _calculate_tiered_royalty(self, sale_price_wei: int) -> int:
        """Calculate tiered royalty based on sale price"""
        sale_price_eth = sale_price_wei / 10**18
        
        for tier in sorted(self.tiers, key=lambda x: x['threshold'], reverse=True):
            if sale_price_eth >= tier['threshold']:
                return int(sale_price_wei * tier['rate'] / 100)
        
        return 0
    
    def _calculate_declining_royalty(self, sale_price_wei: int, sale_date: datetime) -> int:
        """Calculate declining royalty based on time since minting"""
        # Simplified - would track actual minting date
        years_elapsed = Decimal('0')  # Calculate based on actual dates
        
        current_rate = max(
            self.initial_rate - (self.decline_rate * years_elapsed),
            self.minimum_rate
        )
        
        return int(sale_price_wei * float(current_rate) / 100)


@dataclass
class NFTContract:
    """NFT smart contract representation"""
    contract_address: str
    standard: NFTStandard
    name: str
    symbol: str
    network: str
    
    # Contract details
    creator_address: str
    deployed_at: datetime
    total_supply: int = 0
    max_supply: Optional[int] = None
    
    # Features
    supports_royalties: bool = False
    is_enumerable: bool = False
    is_burnable: bool = False
    is_pausable: bool = False
    
    # Metadata
    base_uri: str = ""
    contract_uri: str = ""


class NFTMinter:
    """Professional NFT minting service"""
    
    def __init__(self, web3_client: Web3, private_key: str, config: Dict[str, Any]):
        self.w3 = web3_client
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.config = config
        
        # Contract management
        self.contracts: Dict[str, Contract] = {}
        self.deployed_contracts: Dict[str, NFTContract] = {}
        
        # IPFS configuration
        self.ipfs_gateway = config.get('ipfs_gateway', 'https://ipfs.io/ipfs/')
        self.pinata_api_key = config.get('pinata_api_key')
        self.pinata_secret = config.get('pinata_secret')
        
        # Marketplace configurations
        self.marketplace_configs = config.get('marketplaces', {})
    
    async def deploy_nft_contract(
        self,
        name: str,
        symbol: str,
        standard: NFTStandard = NFTStandard.ERC721,
        max_supply: Optional[int] = None,
        royalty_recipient: Optional[str] = None,
        royalty_percentage: Decimal = Decimal('10')
    ) -> NFTContract:
        """Deploy a new NFT contract"""



        try:
            # Get contract bytecode and ABI based on standard
            bytecode, abi = self._get_contract_artifacts(standard)
            
            # Prepare constructor arguments
            constructor_args = [name, symbol]
            
            if royalty_recipient and standard == NFTStandard.ERC2981:
                constructor_args.extend([royalty_recipient, int(royalty_percentage * 100)])  # Basis points
            
            if max_supply:
                constructor_args.append(max_supply)
            
            # Create contract factory
            contract_factory = self.w3.eth.contract(abi=abi, bytecode=bytecode)
            
            # Estimate gas
            gas_estimate = contract_factory.constructor(*constructor_args).estimate_gas({
                'from': self.account.address
            })
            
            # Build deployment transaction
            transaction = contract_factory.constructor(*constructor_args).build_transaction({
                'from': self.account.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for deployment
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status != 1:
                raise Exception("Contract deployment failed")
            
            contract_address = receipt.contractAddress
            
            # Create contract instance
            contract = self.w3.eth.contract(address=contract_address, abi=abi)
            self.contracts[contract_address] = contract
            
            # Create NFT contract object
            nft_contract = NFTContract(
                contract_address=contract_address,
                standard=standard,
                name=name,
                symbol=symbol,
                network=self.config.get('network', 'ethereum'),
                creator_address=self.account.address,
                deployed_at=datetime.utcnow(),
                supports_royalties=(standard == NFTStandard.ERC2981),
                max_supply=max_supply
            )
            
            self.deployed_contracts[contract_address] = nft_contract
            
            logger.info(f"NFT contract deployed: {name} at {contract_address}")
            return nft_contract
            
        except Exception as e:
            logger.error(f"NFT contract deployment failed: {e}")
            raise
    
    async def mint_nft(
        self,
        contract_address: str,
        recipient_address: str,
        metadata: NFTMetadata,
        content_file: Optional[bytes] = None
    ) -> Tuple[str, int]:
        """Mint a new NFT"""



        try:
            contract = self.contracts.get(contract_address)
            if not contract:
                raise ValueError(f"Contract not found: {contract_address}")
            
            # Upload content and metadata to IPFS
            content_uri = ""
            if content_file:
                content_uri = await self._upload_to_ipfs(content_file, f"{metadata.name}_content")
                metadata.image_url = content_uri
                if metadata.content_type in [ContentType.AUDIO, ContentType.VIDEO]:
                    metadata.animation_url = content_uri
            
            # Upload metadata to IPFS
            metadata_json = json.dumps(metadata.to_json_metadata(), indent=2)
            metadata_uri = await self._upload_to_ipfs(
                metadata_json.encode('utf-8'),
                f"{metadata.name}_metadata.json"
            )
            
            # Get next token ID (simplified)
            token_id = await self._get_next_token_id(contract)
            
            # Prepare mint transaction
            if hasattr(contract.functions, 'safeMint'):
                # ERC721 with metadata
                function = contract.functions.safeMint(recipient_address, metadata_uri)
            elif hasattr(contract.functions, 'mint'):
                # Basic mint function
                function = contract.functions.mint(recipient_address, token_id, 1, metadata_uri)
            else:
                raise Exception("No suitable mint function found")
            
            # Estimate gas
            gas_estimate = function.estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status != 1:
                raise Exception("NFT minting failed")
            
            # Update metadata with minting information
            metadata.minting_date = datetime.utcnow()
            
            logger.info(f"NFT minted: Token ID {token_id} in contract {contract_address}")
            return tx_hash.hex(), token_id
            
        except Exception as e:
            logger.error(f"NFT minting failed: {e}")
            raise
    
    async def _upload_to_ipfs(self, content: bytes, filename: str) -> str:
        """Upload content to IPFS via Pinata"""



        try:
            if not self.pinata_api_key or not self.pinata_secret:
                raise Exception("Pinata credentials not configured")
            
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret
            }
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('file', content, filename=filename)
            
            # Add pinning options
            options = json.dumps({
                'cidVersion': 1,
                'customPinPolicy': {
                    'regions': [
                        {'id': 'FRA1', 'desiredReplicationCount': 2},
                        {'id': 'NYC1', 'desiredReplicationCount': 2}
                    ]
                }
            })
            data.add_field('pinataOptions', options)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        ipfs_hash = result['IpfsHash']
                        return f"{self.ipfs_gateway}{ipfs_hash}"
                    else:
                        raise Exception(f"IPFS upload failed: {response.status}")
            
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            raise
    
    async def _get_next_token_id(self, contract: Contract) -> int:
        """Get the next available token ID"""



        try:
            # Try different methods to get next token ID
            if hasattr(contract.functions, 'totalSupply'):
                return contract.functions.totalSupply().call() + 1
            elif hasattr(contract.functions, 'nextTokenId'):
                return contract.functions.nextTokenId().call()
            else:
                # Fallback to counting from 1
                return 1
        except Exception:
            return 1
    
    async def set_royalties(
        self,
        contract_address: str,
        token_id: int,
        royalty_info: RoyaltyInfo
    ) -> str:
        """Set royalties for an NFT (ERC2981 standard)"""



        try:
            contract = self.contracts.get(contract_address)
            if not contract:
                raise ValueError(f"Contract not found: {contract_address}")
            
            # Check if contract supports royalties
            if not hasattr(contract.functions, 'setTokenRoyalty'):
                raise Exception("Contract does not support royalties")
            
            # Calculate royalty in basis points (1% = 100 basis points)
            royalty_basis_points = int(royalty_info.rate_percentage * 100)
            
            # Set royalty
            function = contract.functions.setTokenRoyalty(
                token_id,
                royalty_info.recipient_address,
                royalty_basis_points
            )
            
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Royalties set for token {token_id}: {royalty_info.rate_percentage}%")
                return tx_hash.hex()
            
            raise Exception("Royalty setting failed")
            
        except Exception as e:
            logger.error(f"Setting royalties failed: {e}")
            raise
    
    def _get_contract_artifacts(self, standard: NFTStandard) -> Tuple[str, List[Dict[str, Any]]]:
        """Get contract bytecode and ABI for NFT standard"""
        # In production, load from compiled contract artifacts
        
        if standard == NFTStandard.ERC721:
            return self._get_erc721_artifacts()
        elif standard == NFTStandard.ERC1155:
            return self._get_erc1155_artifacts()
        elif standard == NFTStandard.ERC2981:
            return self._get_erc2981_artifacts()
        else:
            raise ValueError(f"Unsupported NFT standard: {standard}")
    
    def _get_erc721_artifacts(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Get ERC721 contract artifacts"""
        bytecode = "0x608060405234801561001057600080fd5b50..."  # Placeholder
        abi = [
            {
                "inputs": [{"name": "name", "type": "string"}, {"name": "symbol", "type": "string"}],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "inputs": [{"name": "to", "type": "address"}, {"name": "tokenURI", "type": "string"}],
                "name": "safeMint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        return bytecode, abi
    
    def _get_erc1155_artifacts(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Get ERC1155 contract artifacts"""
        bytecode = "0x608060405234801561001057600080fd5b50..."  # Placeholder
        abi = []  # Placeholder
        return bytecode, abi
    
    def _get_erc2981_artifacts(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Get ERC2981 (with royalties) contract artifacts"""
        bytecode = "0x608060405234801561001057600080fd5b50..."  # Placeholder
        abi = []  # Placeholder
        return bytecode, abi


class MarketplaceIntegration:
    """Integration with major NFT marketplaces"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.marketplace_apis: Dict[NFTMarketplace, Dict[str, str]] = {}
        self._initialize_marketplace_configs()
    
    def _initialize_marketplace_configs(self):
        """Initialize marketplace API configurations"""
        self.marketplace_apis = {
            NFTMarketplace.OPENSEA: {
                'api_url': 'https://api.opensea.io/api/v1',
                'testnet_url': 'https://testnets-api.opensea.io/api/v1',
                'api_key': self.config.get('opensea_api_key', '')
            },
            NFTMarketplace.RARIBLE: {
                'api_url': 'https://api.rarible.org/v0.1',
                'testnet_url': 'https://api-staging.rarible.org/v0.1',
                'api_key': self.config.get('rarible_api_key', '')
            }
        }
    
    async def list_nft_for_sale(
        self,
        marketplace: NFTMarketplace,
        contract_address: str,
        token_id: int,
        price_eth: Decimal,
        duration_days: int = 7
    ) -> bool:
        """List NFT for sale on marketplace"""



        try:
            if marketplace == NFTMarketplace.OPENSEA:
                return await self._list_on_opensea(contract_address, token_id, price_eth, duration_days)
            elif marketplace == NFTMarketplace.RARIBLE:
                return await self._list_on_rarible(contract_address, token_id, price_eth, duration_days)
            else:
                logger.warning(f"Marketplace {marketplace.value} not yet supported")
                return False
                
        except Exception as e:
            logger.error(f"Failed to list NFT on {marketplace.value}: {e}")
            return False
    
    async def _list_on_opensea(
        self,
        contract_address: str,
        token_id: int,
        price_eth: Decimal,
        duration_days: int
    ) -> bool:
        """List NFT on OpenSea"""
        # In production, implement OpenSea Seaport protocol integration
        logger.info(f"Mock listing on OpenSea: {contract_address}#{token_id} for {price_eth} ETH")
        return True
    
    async def _list_on_rarible(
        self,
        contract_address: str,
        token_id: int,
        price_eth: Decimal,
        duration_days: int
    ) -> bool:
        """List NFT on Rarible"""
        # In production, implement Rarible Protocol integration
        logger.info(f"Mock listing on Rarible: {contract_address}#{token_id} for {price_eth} ETH")
        return True


# Export classes
__all__ = [
    'NFTStandard',
    'NFTMarketplace',
    'ContentType',
    'RoyaltyType',
    'NFTMetadata',
    'RoyaltyInfo',
    'NFTContract',
    'NFTMinter',
    'MarketplaceIntegration'
]
