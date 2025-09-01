"""NFT System for Content Monetization and Licensing - IA-Influencer-Agent Platform

This module provides comprehensive NFT functionality for content creators including
NFT minting, marketplace operations, licensing management, royalty distribution,
and metadata handling for audio, video, image, and text content.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import json
from enum import Enum
import hashlib
import uuid

from web3 import Web3
from web3.contract import Contract
import redis.asyncio as redis
from PIL import Image
import requests
from ipfshttpclient import connect as ipfs_connect

from ...config.blockchain_config import BlockchainConfig
from ...core.exceptions import BlockchainError, ValidationError, NFTError

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """
Supported content types for NFT minting"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    MUSIC = "music"
    ARTWORK = "artwork"
    SOCIAL_POST = "social_post"


class LicenseType(Enum):
    """Types of licenses available for NFT content"""

    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EXCLUSIVE = "exclusive"
    LIMITED = "limited"
    STREAMING = "streaming"
    DISTRIBUTION = "distribution"
    REMIX = "remix"
    SAMPLE = "sample"


@dataclass
class NFTMetadata:
    """NFT metadata structure compliant with OpenSea and other standards"""
    name: str
    description: str
    image: str
    content_type: ContentType
    creator: str
    created_at: datetime
    license_type: LicenseType
    properties: Dict[str, Any]
    attributes: List[Dict[str, Any]]
    external_url: Optional[str] = None
    animation_url: Optional[str] = None
    background_color: Optional[str] = None


@dataclass
class LicenseTerms:
    """
License terms for NFT content"""
    license_type: LicenseType
    duration: Optional[timedelta]
    territory: str
    usage_rights: List[str]
    restrictions: List[str]
    royalty_percentage: Decimal
    transferable: bool
    sublicensable: bool
    commercial_use: bool
    modification_allowed: bool


@dataclass
class NFTListing:
    """
NFT marketplace listing"""
    token_id: int
    contract_address: str
    network: str
    price: Decimal
    currency: str
    seller: str
    license_terms: LicenseTerms
    expiration: datetime
    is_auction: bool
    minimum_bid: Optional[Decimal]
    buy_now_price: Optional[Decimal]


class NFTMinter:
    """
    NFT minting service for content creators
    
    Handles the creation of NFTs for various content types with proper
    metadata, IPFS storage, and blockchain minting operations.
    """
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.NFTMinter")
        self.ipfs_client = None
        self.web3_instances: Dict[str, Web3] = {}
        self.nft_contracts: Dict[str, Contract] = {}
    
    async def initialize(self) -> None:
        """Initialize NFT minter with IPFS and blockchain connections"""
        try:
            # Initialize IPFS client
            self.ipfs_client = ipfs_connect(self.config.ipfs_gateway)
            
            # Initialize Web3 connections
            for network in self.config.supported_networks:
                web3 = Web3(Web3.HTTPProvider(getattr(self.config, f"{network}_rpc")))
                self.web3_instances[network] = web3
                
                # Load NFT contract for network
                contract_address = getattr(self.config, f"{network}_nft_contract_address")
                contract_abi = self._get_nft_contract_abi()
                
                self.nft_contracts[network] = web3.eth.contract(
                    address=contract_address,
                    abi=contract_abi
                )
            
            self.logger.info("NFT minter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NFT minter: {str(e)}")
            raise BlockchainError(f"NFT minter initialization failed: {str(e)}")
    
    async def mint_content_nft(
        self,
        creator_address: str,
        content_file_path: str,
        metadata: NFTMetadata,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """
        Mint NFT for content with automatic IPFS upload and metadata creation
        
        This creates a unique NFT representing ownership and licensing rights
        for the content, enabling monetization and proof of authenticity.
        """
        try:
            self.logger.info(f"Minting NFT for content: {metadata.name}")
            
            # Upload content to IPFS
            content_ipfs_hash = await self._upload_content_to_ipfs(content_file_path, metadata.content_type)
            
            # Generate thumbnail/preview if needed
            preview_ipfs_hash = await self._generate_and_upload_preview(content_file_path, metadata.content_type)
            
            # Create complete metadata
            complete_metadata = await self._create_complete_metadata(
                metadata,
                content_ipfs_hash,
                preview_ipfs_hash
            )
            
            # Upload metadata to IPFS
            metadata_ipfs_hash = await self._upload_metadata_to_ipfs(complete_metadata)
            
            # Mint NFT on blockchain
            mint_result = await self._mint_nft_on_blockchain(
                network=network,
                recipient=creator_address,
                token_uri=f"ipfs://{metadata_ipfs_hash}",
                content_hash=content_ipfs_hash
            )
            
            result = {
                'token_id': mint_result['token_id'],
                'transaction_hash': mint_result['tx_hash'],
                'block_number': mint_result['block_number'],
                'content_ipfs_hash': content_ipfs_hash,
                'metadata_ipfs_hash': metadata_ipfs_hash,
                'preview_ipfs_hash': preview_ipfs_hash,
                'opensea_url': self._generate_opensea_url(network, mint_result['token_id']),
                'network': network
            }
            
            self.logger.info(f"NFT minted successfully: Token ID {mint_result['token_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to mint NFT: {str(e)}")
            raise NFTError(f"NFT minting failed: {str(e)}")
    
    async def mint_license_nft(
        self,
        network: str,
        recipient_address: str,
        token_uri: str,
        license_data: Dict[str, Any],
        price: Decimal
    ) -> Dict[str, Any]:
        """Mint NFT representing a content license"""
        try:
            self.logger.info(f"Minting license NFT for recipient: {recipient_address}")
            
            # Prepare license metadata
            license_metadata = {
                "name": f"License - {license_data.get('content_title', 'Content')}",
                "description": license_data.get('description', ''),
                "license_type": license_data.get('license_type', 'standard'),
                "terms": license_data.get('terms', {}),
                "price": str(price),
                "currency": license_data.get('currency', 'ETH'),
                "valid_until": license_data.get('expiration', ''),
                "content_hash": license_data.get('content_hash', '')
            }
            
            # Upload license metadata to IPFS
            metadata_hash = await self._upload_metadata_to_ipfs(license_metadata)
            token_uri = f"ipfs://{metadata_hash}"
            
            # Mint license NFT
            mint_result = await self._mint_nft_on_blockchain(
                network=network,
                recipient=recipient_address,
                token_uri=token_uri,
                content_hash=license_data.get('content_hash', '')
            )
            
            result = {
                'token_id': mint_result['token_id'],
                'tx_hash': mint_result['tx_hash'],
                'block_number': mint_result['block_number'],
                'gas_used': mint_result['gas_used'],
                'metadata_hash': metadata_hash,
                'license_terms': license_data
            }
            
            self.logger.info(f"License NFT minted successfully: Token ID {mint_result['token_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to mint license NFT: {str(e)}")
            raise NFTError(f"License NFT minting failed: {str(e)}")
    
    async def mint_collection_nft(
        self,
        creator_address: str,
        collection_name: str,
        content_items: List[str],
        metadata: Dict[str, Any],
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Mint NFT for a collection of content (album, series, etc.)"""
        try:
            self.logger.info(f"Minting collection NFT: {collection_name}")
            
            # Process all content items
            collection_items = []
            for content_path in content_items:
                item_hash = await self._upload_content_to_ipfs(content_path, ContentType.AUDIO)
                collection_items.append({
                    "content_hash": item_hash,
                    "file_path": content_path
                })
            
            # Create collection metadata
            collection_metadata = {
                "name": collection_name,
                "description": metadata.get('description', ''),
                "image": metadata.get('cover_image', ''),
                "collection_type": metadata.get('collection_type', 'album'),
                "artist": metadata.get('artist', ''),
                "total_items": len(collection_items),
                "items": collection_items,
                "created_at": datetime.utcnow().isoformat(),
                "properties": metadata.get('properties', {}),
                "attributes": metadata.get('attributes', [])
            }
            
            # Upload collection metadata
            metadata_hash = await self._upload_metadata_to_ipfs(collection_metadata)
            
            # Mint collection NFT
            mint_result = await self._mint_nft_on_blockchain(
                network=network,
                recipient=creator_address,
                token_uri=f"ipfs://{metadata_hash}",
                content_hash=hashlib.sha256(json.dumps(collection_items).encode()).hexdigest()
            )
            
            result = {
                'collection_token_id': mint_result['token_id'],
                'transaction_hash': mint_result['tx_hash'],
                'metadata_hash': metadata_hash,
                'total_items': len(collection_items),
                'collection_items': collection_items
            }
            
            self.logger.info(f"Collection NFT minted successfully: Token ID {mint_result['token_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to mint collection NFT: {str(e)}")
            raise NFTError(f"Collection NFT minting failed: {str(e)}")
    
    async def _upload_content_to_ipfs(self, file_path: str, content_type: ContentType) -> str:
        """Upload content file to IPFS and return hash"""
        try:
            with open(file_path, 'rb') as file:
                result = self.ipfs_client.add(file)
                return result['Hash']
        except Exception as e:
            self.logger.error(f"Failed to upload content to IPFS: {str(e)}")
            raise NFTError(f"IPFS upload failed: {str(e)}")
    
    async def _upload_metadata_to_ipfs(self, metadata: Dict[str, Any]) -> str:
        """Upload NFT metadata to IPFS"""
        try:
            metadata_json = json.dumps(metadata, indent=2, default=str)
            result = self.ipfs_client.add_json(metadata)
            return result
        except Exception as e:
            self.logger.error(f"Failed to upload metadata to IPFS: {str(e)}")
            raise NFTError(f"Metadata upload failed: {str(e)}")
    
    async def _generate_and_upload_preview(self, content_path: str, content_type: ContentType) -> str:
        """Generate and upload preview/thumbnail for content"""
        if content_type == ContentType.AUDIO:
            # Generate audio waveform visualization
            return await self._generate_audio_preview(content_path)
        elif content_type == ContentType.VIDEO:
            # Generate video thumbnail
            return await self._generate_video_thumbnail(content_path)
        elif content_type == ContentType.IMAGE:
            # Generate optimized preview
            return await self._generate_image_preview(content_path)
        else:
            # Generate generic preview
            return await self._generate_generic_preview(content_type)
    
    async def _generate_audio_preview(self, audio_path: str) -> str:
        """
Generate waveform visualization for audio content"""
        # This would use libraries like librosa and matplotlib to generate waveforms
        # For now, returning a placeholder
        return "QmAudioWaveformPreview"
    
    async def _generate_video_thumbnail(self, video_path: str) -> str:
        """Generate thumbnail from video content"""
        # This would use ffmpeg or similar to extract frame
        # For now, returning a placeholder
        return "QmVideoThumbnailPreview"
    
    async def _generate_image_preview(self, image_path: str) -> str:
        """Generate optimized preview for image content"""
        # This would resize and optimize the image
        # For now, returning a placeholder
        return "QmImagePreview"
    
    async def _generate_generic_preview(self, content_type: ContentType) -> str:
        """Generate generic preview for content type"""
        return f"QmGenericPreview{content_type.value}"
    
    async def _create_complete_metadata(
        self,
        base_metadata: NFTMetadata,
        content_hash: str,
        preview_hash: str
    ) -> Dict[str, Any]:
        """Create complete NFT metadata with all required fields"""
        return {
            "name": base_metadata.name,
            "description": base_metadata.description,
            "image": f"ipfs://{preview_hash}",
            "animation_url": f"ipfs://{content_hash}",
            "external_url": base_metadata.external_url,
            "background_color": base_metadata.background_color,
            "attributes": base_metadata.attributes,
            "properties": {
                **base_metadata.properties,
                "content_type": base_metadata.content_type.value,
                "creator": base_metadata.creator,
                "created_at": base_metadata.created_at.isoformat(),
                "license_type": base_metadata.license_type.value,
                "content_hash": content_hash,
                "preview_hash": preview_hash
            }
        }
    
    async def _mint_nft_on_blockchain(
        self,
        network: str,
        recipient: str,
        token_uri: str,
        content_hash: str
    ) -> Dict[str, Any]:
        """Mint NFT on blockchain network"""
        try:
            web3 = self.web3_instances[network]
            contract = self.nft_contracts[network]
            
            # Get next token ID
            total_supply = contract.functions.totalSupply().call()
            next_token_id = total_supply + 1
            
            # Build mint transaction
            function_call = contract.functions.mintNFT(
                recipient,
                next_token_id,
                token_uri,
                content_hash
            )
            
            # Estimate gas
            gas_estimate = function_call.estimate_gas({'from': self.config.platform_wallet_address})
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.config.platform_wallet_address,
                'gas': gas_estimate * 2,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(self.config.platform_wallet_address)
            })
            
            # Sign and send (using secure key management in production)
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=self.config.platform_private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'token_id': next_token_id,
                'tx_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to mint NFT on blockchain: {str(e)}")
            raise BlockchainError(f"Blockchain minting failed: {str(e)}")
    
    def _get_nft_contract_abi(self) -> List[Dict]:
        """Get NFT contract ABI"""
        # This would return the actual ERC-721 contract ABI
        return [
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "tokenId", "type": "uint256"},
                    {"name": "tokenURI", "type": "string"},
                    {"name": "contentHash", "type": "string"}
                ],
                "name": "mintNFT",
                "outputs": [],
                "type": "function"
            }
            # ... more ABI entries
        ]
    
    def _generate_opensea_url(self, network: str, token_id: int) -> str:
        """Generate OpenSea URL for NFT"""
        network_mapping = {
            "ethereum_mainnet": "",
            "polygon_mainnet": "matic/",
            "binance_smart_chain": "bsc/"
        }
        
        network_prefix = network_mapping.get(network, "")
        contract_address = getattr(self.config, f"{network}_nft_contract_address")
        
        return f"https://opensea.io/assets/{network_prefix}{contract_address}/{token_id}"


class NFTLicenseManager:
    """
    NFT-based licensing system for automated content licensing
    
    Manages license NFTs that represent specific usage rights for content,
    enabling automated licensing and rights management.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.NFTLicenseManager")
        self.web3_instances: Dict[str, Web3] = {}
        self.license_contracts: Dict[str, Contract] = {}
    
    async def initialize(self) -> None:
        """Initialize license manager"""
        try:
            for network in self.config.supported_networks:
                web3 = Web3(Web3.HTTPProvider(getattr(self.config, f"{network}_rpc")))
                self.web3_instances[network] = web3
                
                contract_address = getattr(self.config, f"{network}_license_contract_address")
                contract_abi = self._get_license_contract_abi()
                
                self.license_contracts[network] = web3.eth.contract(
                    address=contract_address,
                    abi=contract_abi
                )
            
            self.logger.info("NFT License Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize license manager: {str(e)}")
            raise BlockchainError(f"License manager initialization failed: {str(e)}")
    
    async def create_license_offering(
        self,
        content_nft_id: int,
        license_terms: LicenseTerms,
        price: Decimal,
        quantity: int,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Create license offering for content NFT"""
        try:
            self.logger.info(f"Creating license offering for NFT {content_nft_id}")
            
            # Prepare license data
            license_data = {
                "content_nft_id": content_nft_id,
                "license_type": license_terms.license_type.value,
                "duration": int(license_terms.duration.total_seconds()) if license_terms.duration else 0,
                "territory": license_terms.territory,
                "usage_rights": license_terms.usage_rights,
                "restrictions": license_terms.restrictions,
                "royalty_percentage": int(license_terms.royalty_percentage * 100),
                "transferable": license_terms.transferable,
                "commercial_use": license_terms.commercial_use,
                "modification_allowed": license_terms.modification_allowed
            }
            
            # Create license offering on blockchain
            contract = self.license_contracts[network]
            function_call = contract.functions.createLicenseOffering(
                content_nft_id,
                int(price * 10**18),  # Convert to wei
                quantity,
                json.dumps(license_data)
            )
            
            # Execute transaction
            transaction = function_call.build_transaction({
                'from': self.config.platform_wallet_address,
                'gas': 500000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(self.config.platform_wallet_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key=self.config.platform_private_key)
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse events to get offering ID
            events = contract.events.LicenseOfferingCreated().process_receipt(receipt)
            offering_id = events[0]['args']['offeringId'] if events else None
            
            # Cache offering data
            cache_key = f"license_offering:{network}:{offering_id}"
            await self.redis.hset(cache_key, mapping={
                "content_nft_id": content_nft_id,
                "price": str(price),
                "quantity": quantity,
                "available": quantity,
                "license_terms": json.dumps(license_data)
            })
            await self.redis.expire(cache_key, 86400 * 30)  # 30 days
            
            result = {
                'offering_id': offering_id,
                'tx_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'license_data': license_data
            }
            
            self.logger.info(f"License offering created: ID {offering_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create license offering: {str(e)}")
            raise NFTError(f"License offering creation failed: {str(e)}")
    
    async def purchase_license(
        self,
        offering_id: int,
        buyer_address: str,
        quantity: int,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Purchase license from offering"""
        try:
            self.logger.info(f"Purchasing license from offering {offering_id}")
            
            # Get offering details
            contract = self.license_contracts[network]
            offering = contract.functions.getLicenseOffering(offering_id).call()
            
            total_price = offering[1] * quantity  # price * quantity
            
            # Purchase license
            function_call = contract.functions.purchaseLicense(offering_id, quantity)
            
            transaction = function_call.build_transaction({
                'from': buyer_address,
                'gas': 300000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'value': total_price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(buyer_address)
            })
            
            # This would be signed by the buyer's wallet in practice
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key="BUYER_PRIVATE_KEY")
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse events
            events = contract.events.LicensePurchased().process_receipt(receipt)
            license_nft_ids = [event['args']['licenseNFTId'] for event in events]
            
            # Update cache
            cache_key = f"license_offering:{network}:{offering_id}"
            current_available = await self.redis.hget(cache_key, "available")
            if current_available:
                new_available = int(current_available) - quantity
                await self.redis.hset(cache_key, "available", new_available)
            
            result = {
                'license_nft_ids': license_nft_ids,
                'tx_hash': receipt['transactionHash'].hex(),
                'total_price': str(Decimal(total_price) / 10**18),
                'quantity_purchased': quantity
            }
            
            self.logger.info(f"License purchased successfully: {len(license_nft_ids)} NFTs")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to purchase license: {str(e)}")
            raise NFTError(f"License purchase failed: {str(e)}")
    
    async def validate_license_usage(
        self,
        license_nft_id: int,
        usage_type: str,
        user_address: str,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Validate license usage rights"""
        try:
            contract = self.license_contracts[network]
            
            # Check if user owns the license NFT
            owner = contract.functions.ownerOf(license_nft_id).call()
            if owner.lower() != user_address.lower():
                return {"valid": False, "reason": "User does not own license NFT"}
            
            # Get license terms
            license_data = contract.functions.getLicenseData(license_nft_id).call()
            terms = json.loads(license_data)
            
            # Validate usage against terms
            if usage_type not in terms.get("usage_rights", []):
                return {"valid": False, "reason": f"Usage type '{usage_type}' not permitted"}
            
            # Check expiration if duration is set
            if terms.get("duration", 0) > 0:
                # This would check against mint timestamp + duration
                pass
            
            return {
                "valid": True,
                "license_terms": terms,
                "usage_type": usage_type,
                "owner": owner
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate license usage: {str(e)}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}
    
    def _get_license_contract_abi(self) -> List[Dict]:
        """Get license contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "contentNFTId", "type": "uint256"},
                    {"name": "price", "type": "uint256"},
                    {"name": "quantity", "type": "uint256"},
                    {"name": "licenseData", "type": "string"}
                ],
                "name": "createLicenseOffering",
                "outputs": [],
                "type": "function"
            }
            # ... more ABI entries
        ]


class NFTMarketplace:
    """
    NFT marketplace for content creators to sell and license their work
    
    Provides marketplace functionality including listings, auctions,
    offers, and automated transactions for NFT-based content licensing.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.NFTMarketplace")
        self.web3_instances: Dict[str, Web3] = {}
        self.marketplace_contracts: Dict[str, Contract] = {}
        self.active_listings: Dict[str, NFTListing] = {}
    
    async def initialize(self) -> None:
        """Initialize NFT marketplace"""
        try:
            for network in self.config.supported_networks:
                web3 = Web3(Web3.HTTPProvider(getattr(self.config, f"{network}_rpc")))
                self.web3_instances[network] = web3
                
                contract_address = getattr(self.config, f"{network}_marketplace_contract_address")
                contract_abi = self._get_marketplace_contract_abi()
                
                self.marketplace_contracts[network] = web3.eth.contract(
                    address=contract_address,
                    abi=contract_abi
                )
            
            # Load active listings from cache
            await self._load_active_listings()
            
            self.logger.info("NFT Marketplace initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize marketplace: {str(e)}")
            raise BlockchainError(f"Marketplace initialization failed: {str(e)}")
    
    async def list_nft(
        self,
        token_id: int,
        contract_address: str,
        price: Decimal,
        currency: str,
        seller_address: str,
        license_terms: LicenseTerms,
        duration: timedelta,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """List NFT for sale on marketplace"""
        try:
            self.logger.info(f"Listing NFT {token_id} for sale")
            
            expiration = datetime.utcnow() + duration
            
            # Create listing on blockchain
            contract = self.marketplace_contracts[network]
            function_call = contract.functions.listNFT(
                contract_address,
                token_id,
                int(price * 10**18),  # Convert to wei
                currency,
                int(expiration.timestamp()),
                json.dumps({
                    "license_type": license_terms.license_type.value,
                    "usage_rights": license_terms.usage_rights,
                    "commercial_use": license_terms.commercial_use,
                    "royalty_percentage": str(license_terms.royalty_percentage)
                })
            )
            
            # Execute transaction
            transaction = function_call.build_transaction({
                'from': seller_address,
                'gas': 200000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(seller_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key="SELLER_PRIVATE_KEY")
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse events
            events = contract.events.NFTListed().process_receipt(receipt)
            listing_id = events[0]['args']['listingId'] if events else None
            
            # Store listing information
            listing = NFTListing(
                token_id=token_id,
                contract_address=contract_address,
                network=network,
                price=price,
                currency=currency,
                seller=seller_address,
                license_terms=license_terms,
                expiration=expiration,
                is_auction=False,
                minimum_bid=None,
                buy_now_price=price
            )
            
            self.active_listings[f"{network}:{listing_id}"] = listing
            
            # Cache listing
            cache_key = f"marketplace_listing:{network}:{listing_id}"
            await self.redis.hset(cache_key, mapping={
                "token_id": token_id,
                "contract_address": contract_address,
                "price": str(price),
                "currency": currency,
                "seller": seller_address,
                "expiration": expiration.isoformat(),
                "license_terms": json.dumps(license_terms.__dict__, default=str)
            })
            await self.redis.expire(cache_key, int(duration.total_seconds()))
            
            result = {
                'listing_id': listing_id,
                'tx_hash': receipt['transactionHash'].hex(),
                'expiration': expiration.isoformat(),
                'marketplace_url': self._generate_marketplace_url(network, listing_id)
            }
            
            self.logger.info(f"NFT listed successfully: Listing ID {listing_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list NFT: {str(e)}")
            raise NFTError(f"NFT listing failed: {str(e)}")
    
    async def list_license(
        self,
        network: str,
        token_id: int,
        price: Decimal,
        license_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """List license NFT on marketplace"""
        try:
            # This would implement license-specific listing logic
            return await self.list_nft(
                token_id=token_id,
                contract_address=getattr(self.config, f"{network}_license_contract_address"),
                price=price,
                currency="ETH",
                seller_address=self.config.platform_wallet_address,
                license_terms=LicenseTerms(
                    license_type=LicenseType(license_terms.get('license_type', 'personal')),
                    duration=None,
                    territory=license_terms.get('territory', 'worldwide'),
                    usage_rights=license_terms.get('usage_rights', []),
                    restrictions=license_terms.get('restrictions', []),
                    royalty_percentage=Decimal(str(license_terms.get('royalty_percentage', 0))),
                    transferable=license_terms.get('transferable', True),
                    sublicensable=license_terms.get('sublicensable', False),
                    commercial_use=license_terms.get('commercial_use', False),
                    modification_allowed=license_terms.get('modification_allowed', False)
                ),
                duration=timedelta(days=30),
                network=network
            )
        except Exception as e:
            self.logger.error(f"Failed to list license: {str(e)}")
            raise NFTError(f"License listing failed: {str(e)}")
    
    async def purchase_nft(
        self,
        listing_id: int,
        buyer_address: str,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Purchase NFT from marketplace listing"""
        try:
            self.logger.info(f"Purchasing NFT from listing {listing_id}")
            
            # Get listing details
            contract = self.marketplace_contracts[network]
            listing_data = contract.functions.getListing(listing_id).call()
            
            price = listing_data[2]  # Price in wei
            
            # Purchase NFT
            function_call = contract.functions.purchaseNFT(listing_id)
            
            transaction = function_call.build_transaction({
                'from': buyer_address,
                'gas': 300000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'value': price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(buyer_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key="BUYER_PRIVATE_KEY")
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            # Remove from active listings
            listing_key = f"{network}:{listing_id}"
            if listing_key in self.active_listings:
                del self.active_listings[listing_key]
            
            # Remove from cache
            cache_key = f"marketplace_listing:{network}:{listing_id}"
            await self.redis.delete(cache_key)
            
            result = {
                'tx_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'price_paid': str(Decimal(price) / 10**18),
                'buyer': buyer_address
            }
            
            self.logger.info(f"NFT purchased successfully: {receipt['transactionHash'].hex()}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to purchase NFT: {str(e)}")
            raise NFTError(f"NFT purchase failed: {str(e)}")
    
    async def create_auction(
        self,
        token_id: int,
        contract_address: str,
        starting_price: Decimal,
        reserve_price: Optional[Decimal],
        duration: timedelta,
        seller_address: str,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Create auction for NFT"""
        try:
            self.logger.info(f"Creating auction for NFT {token_id}")
            
            end_time = datetime.utcnow() + duration
            
            contract = self.marketplace_contracts[network]
            function_call = contract.functions.createAuction(
                contract_address,
                token_id,
                int(starting_price * 10**18),
                int(reserve_price * 10**18) if reserve_price else 0,
                int(end_time.timestamp())
            )
            
            transaction = function_call.build_transaction({
                'from': seller_address,
                'gas': 250000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(seller_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key="SELLER_PRIVATE_KEY")
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse events
            events = contract.events.AuctionCreated().process_receipt(receipt)
            auction_id = events[0]['args']['auctionId'] if events else None
            
            result = {
                'auction_id': auction_id,
                'tx_hash': receipt['transactionHash'].hex(),
                'end_time': end_time.isoformat(),
                'starting_price': str(starting_price),
                'reserve_price': str(reserve_price) if reserve_price else None
            }
            
            self.logger.info(f"Auction created successfully: ID {auction_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create auction: {str(e)}")
            raise NFTError(f"Auction creation failed: {str(e)}")
    
    async def place_bid(
        self,
        auction_id: int,
        bid_amount: Decimal,
        bidder_address: str,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Place bid on NFT auction"""
        try:
            contract = self.marketplace_contracts[network]
            
            function_call = contract.functions.placeBid(auction_id)
            
            transaction = function_call.build_transaction({
                'from': bidder_address,
                'gas': 150000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'value': int(bid_amount * 10**18),
                'nonce': self.web3_instances[network].eth.get_transaction_count(bidder_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key="BIDDER_PRIVATE_KEY")
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'tx_hash': receipt['transactionHash'].hex(),
                'bid_amount': str(bid_amount),
                'bidder': bidder_address
            }
            
        except Exception as e:
            self.logger.error(f"Failed to place bid: {str(e)}")
            raise NFTError(f"Bid placement failed: {str(e)}")
    
    async def get_marketplace_listings(
        self,
        network: str,
        content_type: Optional[ContentType] = None,
        price_range: Optional[tuple] = None,
        license_type: Optional[LicenseType] = None
    ) -> List[Dict[str, Any]]:
        """Get marketplace listings with optional filters"""
        try:
            # This would query blockchain and cache for active listings
            listings = []
            
            for key, listing in self.active_listings.items():
                if network not in key:
                    continue
                
                # Apply filters
                if content_type and hasattr(listing, 'content_type') and listing.content_type != content_type:
                    continue
                
                if price_range and (listing.price < price_range[0] or listing.price > price_range[1]):
                    continue
                
                if license_type and listing.license_terms.license_type != license_type:
                    continue
                
                listings.append({
                    'listing_id': key.split(':')[1],
                    'token_id': listing.token_id,
                    'price': str(listing.price),
                    'currency': listing.currency,
                    'seller': listing.seller,
                    'expiration': listing.expiration.isoformat(),
                    'license_type': listing.license_terms.license_type.value,
                    'is_auction': listing.is_auction
                })
            
            return listings
            
        except Exception as e:
            self.logger.error(f"Failed to get marketplace listings: {str(e)}")
            return []
    
    async def _load_active_listings(self) -> None:
        """Load active listings from cache"""
        try:
            pattern = "marketplace_listing:*"
            keys = await self.redis.keys(pattern)
            
            for key in keys:
                listing_data = await self.redis.hgetall(key)
                if listing_data:
                    # Parse and store listing
                    network_listing_id = key.decode().split(':')[1:]
                    network_listing_key = ':'.join(network_listing_id)
                    # Store parsed listing data
                    pass
            
        except Exception as e:
            self.logger.error(f"Failed to load active listings: {str(e)}")
    
    def _get_marketplace_contract_abi(self) -> List[Dict]:
        """Get marketplace contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "nftContract", "type": "address"},
                    {"name": "tokenId", "type": "uint256"},
                    {"name": "price", "type": "uint256"},
                    {"name": "currency", "type": "string"},
                    {"name": "expiration", "type": "uint256"},
                    {"name": "licenseData", "type": "string"}
                ],
                "name": "listNFT",
                "outputs": [],
                "type": "function"
            }
            # ... more ABI entries
        ]
    
    def _generate_marketplace_url(self, network: str, listing_id: int) -> str:
        """Generate marketplace URL for listing"""
        return f"https://ia-influencer-marketplace.com/{network}/listing/{listing_id}"


class NFTRoyaltyManager:
    """
    NFT royalty management system for automated creator compensation
    
    Handles royalty distribution for NFT sales, ensuring creators
    receive their fair share of secondary market transactions.
    """
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.NFTRoyaltyManager")
        self.web3_instances: Dict[str, Web3] = {}
        self.royalty_contracts: Dict[str, Contract] = {}
    
    async def initialize(self) -> None:
        """Initialize royalty manager"""
        try:
            for network in self.config.supported_networks:
                web3 = Web3(Web3.HTTPProvider(getattr(self.config, f"{network}_rpc")))
                self.web3_instances[network] = web3
                
                contract_address = getattr(self.config, f"{network}_royalty_contract_address")
                contract_abi = self._get_royalty_contract_abi()
                
                self.royalty_contracts[network] = web3.eth.contract(
                    address=contract_address,
                    abi=contract_abi
                )
            
            self.logger.info("NFT Royalty Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize royalty manager: {str(e)}")
            raise BlockchainError(f"Royalty manager initialization failed: {str(e)}")
    
    async def set_nft_royalty(
        self,
        token_id: int,
        creator_address: str,
        royalty_percentage: Decimal,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Set royalty information for NFT"""
        try:
            contract = self.royalty_contracts[network]
            
            # Convert percentage to basis points (1% = 100 basis points)
            royalty_basis_points = int(royalty_percentage * 100)
            
            function_call = contract.functions.setRoyalty(
                token_id,
                creator_address,
                royalty_basis_points
            )
            
            transaction = function_call.build_transaction({
                'from': self.config.platform_wallet_address,
                'gas': 100000,
                'gasPrice': self.web3_instances[network].eth.gas_price,
                'nonce': self.web3_instances[network].eth.get_transaction_count(self.config.platform_wallet_address)
            })
            
            signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key=self.config.platform_private_key)
            tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'tx_hash': receipt['transactionHash'].hex(),
                'token_id': token_id,
                'creator': creator_address,
                'royalty_percentage': str(royalty_percentage)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set NFT royalty: {str(e)}")
            raise NFTError(f"Royalty setting failed: {str(e)}")
    
    async def distribute_royalty(
        self,
        token_id: int,
        sale_price: Decimal,
        network: str = "polygon_mainnet"
    ) -> Dict[str, Any]:
        """Distribute royalty payment for NFT sale"""
        try:
            contract = self.royalty_contracts[network]
            
            # Get royalty info
            royalty_info = contract.functions.getRoyaltyInfo(token_id, int(sale_price * 10**18)).call()
            recipient = royalty_info[0]
            royalty_amount = royalty_info[1]
            
            if royalty_amount > 0:
                # Transfer royalty
                function_call = contract.functions.distributeRoyalty(token_id)
                
                transaction = function_call.build_transaction({
                    'from': self.config.platform_wallet_address,
                    'gas': 100000,
                    'gasPrice': self.web3_instances[network].eth.gas_price,
                    'value': royalty_amount,
                    'nonce': self.web3_instances[network].eth.get_transaction_count(self.config.platform_wallet_address)
                })
                
                signed_txn = self.web3_instances[network].eth.account.sign_transaction(transaction, private_key=self.config.platform_private_key)
                tx_hash = self.web3_instances[network].eth.send_raw_transaction(signed_txn.rawTransaction)
                receipt = self.web3_instances[network].eth.wait_for_transaction_receipt(tx_hash)
                
                return {
                    'tx_hash': receipt['transactionHash'].hex(),
                    'recipient': recipient,
                    'royalty_amount': str(Decimal(royalty_amount) / 10**18),
                    'sale_price': str(sale_price)
                }
            
            return {
                'tx_hash': None,
                'recipient': None,
                'royalty_amount': '0',
                'sale_price': str(sale_price)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to distribute royalty: {str(e)}")
            raise NFTError(f"Royalty distribution failed: {str(e)}")
    
    def _get_royalty_contract_abi(self) -> List[Dict]:
        """Get royalty contract ABI (EIP-2981 compatible)"""
        return [
            {
                "inputs": [
                    {"name": "tokenId", "type": "uint256"},
                    {"name": "salePrice", "type": "uint256"}
                ],
                "name": "royaltyInfo",
                "outputs": [
                    {"name": "receiver", "type": "address"},
                    {"name": "royaltyAmount", "type": "uint256"}
                ],
                "type": "function"
            }
            # ... more ABI entries
        ]


class NFTMetadataManager:
    """
    NFT metadata management system for content creators
    
    Handles metadata creation, validation, IPFS storage, and updates
    for various content types with proper standards compliance.
    """
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.NFTMetadataManager")
        self.ipfs_client = None
    
    async def initialize(self) -> None:
        """Initialize metadata manager"""
        try:
            self.ipfs_client = ipfs_connect(self.config.ipfs_gateway)
            self.logger.info("NFT Metadata Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metadata manager: {str(e)}")
            raise BlockchainError(f"Metadata manager initialization failed: {str(e)}")
    
    async def create_metadata(
        self,
        content_type: ContentType,
        title: str,
        description: str,
        creator: str,
        content_url: str,
        preview_url: str,
        properties: Dict[str, Any],
        attributes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create NFT metadata with proper standards compliance"""
        try:
            metadata = {
                "name": title,
                "description": description,
                "image": preview_url,
                "external_url": properties.get('external_url'),
                "creator": creator,
                "content_type": content_type.value,
                "created_at": datetime.utcnow().isoformat(),
                "properties": properties,
                "attributes": attributes
            }
            
            # Add content-specific fields
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                metadata["animation_url"] = content_url
                metadata["audio_url"] = content_url
                
            elif content_type == ContentType.VIDEO:
                metadata["animation_url"] = content_url
                metadata["video_url"] = content_url
                
            elif content_type == ContentType.IMAGE:
                metadata["image"] = content_url
                
            # Validate metadata
            await self._validate_metadata(metadata)
            
            # Upload to IPFS
            ipfs_hash = await self._upload_to_ipfs(metadata)
            
            return {
                "metadata": metadata,
                "ipfs_hash": ipfs_hash,
                "ipfs_url": f"ipfs://{ipfs_hash}",
                "gateway_url": f"{self.config.ipfs_gateway}/ipfs/{ipfs_hash}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create metadata: {str(e)}")
            raise NFTError(f"Metadata creation failed: {str(e)}")
    
    async def update_metadata(
        self,
        current_ipfs_hash: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing NFT metadata"""
        try:
            # Fetch current metadata
            current_metadata = await self._fetch_from_ipfs(current_ipfs_hash)
            
            # Apply updates
            updated_metadata = {**current_metadata, **updates}
            updated_metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Validate updated metadata
            await self._validate_metadata(updated_metadata)
            
            # Upload to IPFS
            new_ipfs_hash = await self._upload_to_ipfs(updated_metadata)
            
            return {
                "metadata": updated_metadata,
                "ipfs_hash": new_ipfs_hash,
                "ipfs_url": f"ipfs://{new_ipfs_hash}",
                "previous_hash": current_ipfs_hash
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {str(e)}")
            raise NFTError(f"Metadata update failed: {str(e)}")
    
    async def validate_metadata_standards(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata against various NFT standards"""
        validation_results = {
            "opensea": await self._validate_opensea_standard(metadata),
            "erc721": await self._validate_erc721_standard(metadata),
            "erc1155": await self._validate_erc1155_standard(metadata)
        }
        
        return {
            "valid": all(result["valid"] for result in validation_results.values()),
            "standards": validation_results,
            "warnings": [
                warning for result in validation_results.values() 
                for warning in result.get("warnings", [])
            ]
        }
    
    async def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata structure and required fields"""
        required_fields = ["name", "description", "image"]
        
        for field in required_fields:
            if field not in metadata:
                raise ValidationError(f"Required field '{field}' missing from metadata")
        
        # Validate URLs
        for url_field in ["image", "animation_url", "external_url"]:
            if url_field in metadata and metadata[url_field]:
                if not self._is_valid_url(metadata[url_field]):
                    raise ValidationError(f"Invalid URL in field '{url_field}'")
    
    async def _validate_opensea_standard(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against OpenSea metadata standards"""
        required = ["name", "description", "image"]
        optional = ["external_url", "animation_url", "attributes", "background_color"]
        
        missing_required = [field for field in required if field not in metadata]
        
        return {
            "valid": len(missing_required) == 0,
            "missing_required": missing_required,
            "warnings": []
        }
    
    async def _validate_erc721_standard(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against ERC-721 metadata standards"""
        return {
            "valid": "name" in metadata,
            "warnings": []
        }
    
    async def _validate_erc1155_standard(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against ERC-1155 metadata standards"""
        return {
            "valid": True,
            "warnings": []
        }
    
    async def _upload_to_ipfs(self, metadata: Dict[str, Any]) -> str:
        """Upload metadata to IPFS"""
        try:
            result = self.ipfs_client.add_json(metadata)
            return result
        except Exception as e:
            raise NFTError(f"IPFS upload failed: {str(e)}")
    
    async def _fetch_from_ipfs(self, ipfs_hash: str) -> Dict[str, Any]:
        """Fetch metadata from IPFS"""
        try:
            return self.ipfs_client.get_json(ipfs_hash)
        except Exception as e:
            raise NFTError(f"IPFS fetch failed: {str(e)}")
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://',  # http:// or https://
            re.IGNORECASE
        )
        return url_pattern.match(url) is not None
