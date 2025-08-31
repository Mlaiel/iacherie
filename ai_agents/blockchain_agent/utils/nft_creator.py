"""
IA-Influencer Agent - NFT Creator System

Enterprise NFT creation and management platform providing:
- Multi-format content NFT creation (audio, video, image, text)
- Marketplace integration and automated listing
- Dynamic metadata and provenance tracking
- Royalty management and automated distribution
- Cross-chain NFT bridging and migration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

 IMPORTANT LEGAL NOTICE 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal
import hashlib
import base64
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import requests
    from mutagen import File as MutagenFile
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    requests = None
    MutagenFile = None
    MP3 = None
    FLAC = None

from .blockchain_agent import BlockchainNetwork, NFTMetadata
from .smart_contracts import SmartContractsManager


class ContentType(Enum):
    """Supported content types for NFT creation."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    INTERACTIVE = "interactive"
    COLLECTION = "collection"


class NFTStandard(Enum):
    """Supported NFT standards."""
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL_TOKEN = "spl_token"  # Solana
    CARDANO_NATIVE = "cardano_native"


class MarketplaceType(Enum):
    """Supported NFT marketplaces."""
    OPENSEA = "opensea"
    RARIBLE = "rarible"
    FOUNDATION = "foundation"
    SUPERRARE = "superrare"
    ASYNCART = "asyncart"
    NIFTY_GATEWAY = "nifty_gateway"
    MAGIC_EDEN = "magic_eden"  # Solana
    CARDANO_CNFT = "cardano_cnft"


class RarityTier(Enum):
    """NFT rarity tiers based on attributes."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


@dataclass
class ContentMetadata:
    """Enhanced content metadata for NFT creation."""
    title: str
    description: str
    creator: str
    content_type: ContentType
    file_format: str
    file_size: int
    duration: Optional[float] = None  # For audio/video
    dimensions: Optional[Tuple[int, int]] = None  # For images/video
    sample_rate: Optional[int] = None  # For audio
    bitrate: Optional[int] = None  # For audio/video
    color_palette: Optional[List[str]] = None  # For images
    genre: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    creation_tools: List[str] = field(default_factory=list)


@dataclass
class NFTCollection:
    """NFT collection definition and management."""
    id: str
    name: str
    symbol: str
    description: str
    creator: str
    network: BlockchainNetwork
    contract_address: Optional[str] = None
    total_supply: int = 0
    minted_count: int = 0
    floor_price: Decimal = Decimal('0')
    volume_traded: Decimal = Decimal('0')
    royalty_percentage: float = 10.0
    is_revealed: bool = True
    reveal_date: Optional[datetime] = None
    metadata_base_uri: str = ""
    collection_image: str = ""
    banner_image: str = ""
    social_links: Dict[str, str] = field(default_factory=dict)


@dataclass
class NFTRoyalty:
    """NFT royalty configuration and tracking."""
    token_id: str
    creator_address: str
    royalty_percentage: float
    split_addresses: List[Dict[str, Any]] = field(default_factory=list)  # For revenue sharing
    total_earned: Decimal = Decimal('0')
    last_payment: Optional[datetime] = None
    payment_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MarketplaceListing:
    """NFT marketplace listing information."""
    marketplace: MarketplaceType
    token_id: str
    listing_price: Decimal
    currency: str
    listing_date: datetime
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    listing_url: str = ""
    marketplace_fees: Decimal = Decimal('0')
    status: str = "active"


class NFTCreator:
    """
    Advanced NFT Creation and Management System.
    
    Provides comprehensive NFT creation services:
    - Multi-format content NFT creation
    - Dynamic metadata generation and management
    - Marketplace integration and automated listing
    - Royalty management and distribution
    - Cross-chain NFT bridging
    - Collection management and analytics
    """
    
    def __init__(self, blockchain_agent, smart_contracts_manager: SmartContractsManager, config: Optional[Dict] = None):
        """Initialize the NFT Creator system."""
        self.blockchain_agent = blockchain_agent
        self.smart_contracts = smart_contracts_manager
        self.config = config or {}
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        
        # Storage for NFTs and collections
        self.nfts: Dict[str, Dict[str, Any]] = {}
        self.collections: Dict[str, NFTCollection] = {}
        self.royalties: Dict[str, NFTRoyalty] = {}
        self.marketplace_listings: Dict[str, List[MarketplaceListing]] = {}
        
        # Content processing settings
        self.max_file_size = self.config.get('max_file_size_mb', 100) * 1024 * 1024  # 100MB
        self.supported_formats = {
            ContentType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            ContentType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            ContentType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
            ContentType.TEXT: ['.txt', '.md', '.pdf', '.json']
        }
        
        # Marketplace configurations
        self.marketplace_configs = {
            MarketplaceType.OPENSEA: {
                'api_url': 'https://api.opensea.io/api/v1',
                'testnet_url': 'https://testnets-api.opensea.io/api/v1',
                'fee_percentage': 2.5
            },
            MarketplaceType.RARIBLE: {
                'api_url': 'https://api.rarible.org/v0.1',
                'fee_percentage': 2.5
            },
            MarketplaceType.FOUNDATION: {
                'api_url': 'https://api.foundation.app',
                'fee_percentage': 15.0
            }
        }
        
        # IPFS settings for metadata storage
        self.ipfs_gateway = self.config.get('ipfs_gateway', 'https://ipfs.io/ipfs/')
        self.pinata_api_key = self.config.get('pinata_api_key', '')
        self.pinata_secret = self.config.get('pinata_secret', '')
        
        self.logger.info("NFT Creator system initialized")
    
    async def create_nft(
        self,
        content_file_path: str,
        metadata: ContentMetadata,
        collection_id: Optional[str] = None,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON,
        nft_standard: NFTStandard = NFTStandard.ERC721
    ) -> str:
        """
        Create an NFT from content file with comprehensive metadata.
        
        Args:
            content_file_path: Path to the content file
            metadata: Content metadata
            collection_id: Optional collection to mint into
            network: Blockchain network
            nft_standard: NFT standard to use
            
        Returns:
            str: NFT token ID
        """



        try:
            # Validate content file
            content_info = await self._validate_and_process_content(content_file_path, metadata)
            
            # Generate enhanced NFT metadata
            nft_metadata = await self._generate_nft_metadata(content_info, metadata)
            
            # Upload content and metadata to IPFS
            content_uri = await self._upload_to_ipfs(content_file_path, 'file')
            metadata_uri = await self._upload_to_ipfs(nft_metadata, 'json')
            
            # Create NFT on blockchain
            nft_id = str(uuid.uuid4())
            
            # Determine collection contract or deploy new one
            collection_address = None
            if collection_id and collection_id in self.collections:
                collection_address = self.collections[collection_id].contract_address
            
            if not collection_address:
                # Deploy new collection contract if needed
                collection_address = await self._deploy_nft_collection(
                    name=metadata.title,
                    symbol="CRT",  # Creator Token
                    network=network
                )
            
            # Create blockchain NFT metadata
            blockchain_metadata = NFTMetadata(
                name=metadata.title,
                description=metadata.description,
                image_url=content_uri if metadata.content_type == ContentType.IMAGE else "",
                animation_url=content_uri if metadata.content_type in [ContentType.VIDEO, ContentType.AUDIO] else None,
                external_url=f"https://creator-platform.com/nft/{nft_id}",
                attributes=await self._generate_nft_attributes(metadata, content_info),
                creator=metadata.creator
            )
            
            # Mint NFT via blockchain agent
            tx_id, token_id = await self.blockchain_agent.create_nft(
                content_url=content_uri,
                metadata=blockchain_metadata,
                creator_address=metadata.creator,
                collection_address=collection_address,
                network=network
            )
            
            # Store NFT information
            nft_record = {
                'nft_id': nft_id,
                'token_id': token_id,
                'collection_id': collection_id,
                'network': network.value,
                'contract_address': collection_address,
                'content_uri': content_uri,
                'metadata_uri': metadata_uri,
                'metadata': nft_metadata,
                'content_info': content_info,
                'creation_date': datetime.now(),
                'transaction_id': tx_id,
                'minting_cost': await self._calculate_minting_cost(network),
                'status': 'minted'
            }
            
            self.nfts[nft_id] = nft_record
            
            # Setup royalties
            await self._setup_nft_royalties(
                token_id=token_id,
                creator_address=metadata.creator,
                royalty_percentage=10.0  # Default 10%
            )
            
            # Update collection statistics
            if collection_id:
                await self._update_collection_stats(collection_id)
            
            self.logger.info(f"NFT created successfully: {metadata.title} (Token ID: {token_id})")
            
            return nft_id
            
        except Exception as e:
            self.logger.error(f"NFT creation failed: {str(e)}")
            raise
    
    async def create_collection(
        self,
        name: str,
        symbol: str,
        description: str,
        creator: str,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON,
        collection_size: int = 10000
    ) -> str:
        """
        Create a new NFT collection with smart contract deployment.
        
        Args:
            name: Collection name
            symbol: Collection symbol
            description: Collection description
            creator: Creator address
            network: Blockchain network
            collection_size: Maximum collection size
            
        Returns:
            str: Collection ID
        """



        try:
            collection_id = str(uuid.uuid4())
            
            # Deploy collection smart contract
            contract_address = await self._deploy_nft_collection(
                name=name,
                symbol=symbol,
                network=network
            )
            
            # Create collection record
            collection = NFTCollection(
                id=collection_id,
                name=name,
                symbol=symbol,
                description=description,
                creator=creator,
                network=network,
                contract_address=contract_address,
                total_supply=collection_size,
                metadata_base_uri=f"https://api.creator-platform.com/metadata/{collection_id}/"
            )
            
            self.collections[collection_id] = collection
            
            # Generate collection metadata and images
            await self._generate_collection_assets(collection)
            
            self.logger.info(f"Collection created: {name} (ID: {collection_id})")
            
            return collection_id
            
        except Exception as e:
            self.logger.error(f"Collection creation failed: {str(e)}")
            raise
    
    async def list_nft_on_marketplace(
        self,
        nft_id: str,
        marketplace: MarketplaceType,
        listing_price: Decimal,
        currency: str = "ETH",
        duration_days: int = 30
    ) -> str:
        """
        List an NFT on a specific marketplace.
        
        Args:
            nft_id: NFT identifier
            marketplace: Target marketplace
            listing_price: Listing price
            currency: Currency for listing
            duration_days: Listing duration
            
        Returns:
            str: Listing ID
        """



        try:
            if nft_id not in self.nfts:
                raise ValueError(f"NFT not found: {nft_id}")
            
            nft = self.nfts[nft_id]
            
            # Create marketplace listing
            listing = MarketplaceListing(
                marketplace=marketplace,
                token_id=nft['token_id'],
                listing_price=listing_price,
                currency=currency,
                listing_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=duration_days),
                listing_url=await self._generate_marketplace_url(marketplace, nft['token_id'])
            )
            
            # Add to marketplace listings
            if nft_id not in self.marketplace_listings:
                self.marketplace_listings[nft_id] = []
            self.marketplace_listings[nft_id].append(listing)
            
            # Submit listing to marketplace API (if available)
            if marketplace in self.marketplace_configs:
                await self._submit_marketplace_listing(listing, nft)
            
            self.logger.info(f"NFT listed on {marketplace.value}: {nft_id}")
            
            return f"{nft_id}_{marketplace.value}_{datetime.now().timestamp()}"
            
        except Exception as e:
            self.logger.error(f"Marketplace listing failed: {str(e)}")
            raise
    
    async def generate_collection_art(
        self,
        collection_id: str,
        traits_config: Dict[str, List[str]],
        generation_count: int = 1000
    ) -> List[str]:
        """
        Generate procedural art for NFT collection with trait combinations.
        
        Args:
            collection_id: Collection identifier
            traits_config: Configuration of traits and their values
            generation_count: Number of NFTs to generate
            
        Returns:
            List[str]: List of generated NFT IDs
        """



        try:
            if collection_id not in self.collections:
                raise ValueError(f"Collection not found: {collection_id}")
            
            collection = self.collections[collection_id]
            generated_nfts = []
            
            if not Image:
                raise RuntimeError("PIL library required for art generation")
            
            # Generate unique trait combinations
            trait_combinations = await self._generate_trait_combinations(
                traits_config, 
                generation_count
            )
            
            for i, traits in enumerate(trait_combinations):
                try:
                    # Generate artwork based on traits
                    artwork_path = await self._generate_artwork_from_traits(
                        collection_id, i + 1, traits
                    )
                    
                    # Create content metadata
                    metadata = ContentMetadata(
                        title=f"{collection.name} #{i + 1}",
                        description=f"Unique NFT from {collection.name} collection",
                        creator=collection.creator,
                        content_type=ContentType.IMAGE,
                        file_format="png",
                        file_size=0,  # Will be calculated
                        tags=[collection.name, "generated", "collection"]
                    )
                    
                    # Create NFT
                    nft_id = await self.create_nft(
                        content_file_path=artwork_path,
                        metadata=metadata,
                        collection_id=collection_id,
                        network=collection.network
                    )
                    
                    # Add traits to NFT metadata
                    if nft_id in self.nfts:
                        self.nfts[nft_id]['traits'] = traits
                        self.nfts[nft_id]['rarity_score'] = await self._calculate_rarity_score(
                            traits, trait_combinations
                        )
                    
                    generated_nfts.append(nft_id)
                    
                    # Progress logging
                    if (i + 1) % 100 == 0:
                        self.logger.info(f"Generated {i + 1}/{generation_count} NFTs for collection {collection.name}")
                
                except Exception as e:
                    self.logger.warning(f"Failed to generate NFT #{i + 1}: {str(e)}")
                    continue
            
            # Update collection statistics
            await self._update_collection_stats(collection_id)
            
            self.logger.info(f"Generated {len(generated_nfts)} NFTs for collection {collection.name}")
            
            return generated_nfts
            
        except Exception as e:
            self.logger.error(f"Collection art generation failed: {str(e)}")
            raise
    
    async def _validate_and_process_content(self, file_path: str, metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate and extract information from content file."""



        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Content file not found: {file_path}")
            
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"File size exceeds maximum: {file_size} bytes")
            
            file_format = file_path.suffix.lower()
            if file_format not in self.supported_formats.get(metadata.content_type, []):
                raise ValueError(f"Unsupported format {file_format} for {metadata.content_type.value}")
            
            content_info = {
                'file_path': str(file_path),
                'file_size': file_size,
                'file_format': file_format,
                'content_hash': await self._calculate_file_hash(file_path),
                'mime_type': self._get_mime_type(file_format)
            }
            
            # Extract format-specific metadata
            if metadata.content_type == ContentType.AUDIO and MutagenFile:
                audio_file = MutagenFile(file_path)
                if audio_file:
                    content_info.update({
                        'duration': getattr(audio_file.info, 'length', 0),
                        'bitrate': getattr(audio_file.info, 'bitrate', 0),
                        'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
                        'channels': getattr(audio_file.info, 'channels', 0)
                    })
            
            elif metadata.content_type == ContentType.IMAGE and Image:
                with Image.open(file_path) as img:
                    content_info.update({
                        'dimensions': img.size,
                        'mode': img.mode,
                        'has_alpha': img.mode in ['RGBA', 'LA'],
                        'color_palette': self._extract_color_palette(img)
                    })
            
            return content_info
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {str(e)}")
            raise
    
    async def _generate_nft_metadata(self, content_info: Dict[str, Any], metadata: ContentMetadata) -> Dict[str, Any]:
        """Generate comprehensive NFT metadata."""
        nft_metadata = {
            'name': metadata.title,
            'description': metadata.description,
            'creator': metadata.creator,
            'content_type': metadata.content_type.value,
            'file_format': metadata.file_format,
            'file_size': content_info['file_size'],
            'content_hash': content_info['content_hash'],
            'creation_date': datetime.now().isoformat(),
            'version': '1.0',
            'license': 'Custom Creator License',
            'tags': metadata.tags,
            'genre': metadata.genre,
            'tools_used': metadata.creation_tools
        }
        
        # Add content-specific metadata
        if metadata.content_type == ContentType.AUDIO:
            nft_metadata.update({
                'duration': content_info.get('duration'),
                'bitrate': content_info.get('bitrate'),
                'sample_rate': content_info.get('sample_rate'),
                'audio_channels': content_info.get('channels')
            })
        
        elif metadata.content_type == ContentType.IMAGE:
            nft_metadata.update({
                'dimensions': content_info.get('dimensions'),
                'color_mode': content_info.get('mode'),
                'has_transparency': content_info.get('has_alpha'),
                'dominant_colors': content_info.get('color_palette', [])[:5]  # Top 5 colors
            })
        
        return nft_metadata
    
    async def _generate_nft_attributes(self, metadata: ContentMetadata, content_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate NFT attributes for marketplace compatibility."""
        attributes = []
        
        # Basic attributes
        attributes.extend([
            {'trait_type': 'Content Type', 'value': metadata.content_type.value.title()},
            {'trait_type': 'File Format', 'value': metadata.file_format.upper()},
            {'trait_type': 'Creator', 'value': metadata.creator},
            {'trait_type': 'File Size', 'value': f"{content_info['file_size'] / 1024 / 1024:.1f} MB", 'display_type': 'boost_number'}
        ])
        
        # Content-specific attributes
        if metadata.content_type == ContentType.AUDIO:
            if content_info.get('duration'):
                minutes = int(content_info['duration'] // 60)
                seconds = int(content_info['duration'] % 60)
                attributes.append({
                    'trait_type': 'Duration', 
                    'value': f"{minutes}:{seconds:02d}",
                    'display_type': 'boost_number'
                })
            
            if metadata.genre:
                attributes.append({'trait_type': 'Genre', 'value': metadata.genre})
        
        elif metadata.content_type == ContentType.IMAGE:
            if content_info.get('dimensions'):
                width, height = content_info['dimensions']
                attributes.extend([
                    {'trait_type': 'Width', 'value': width, 'display_type': 'boost_number'},
                    {'trait_type': 'Height', 'value': height, 'display_type': 'boost_number'},
                    {'trait_type': 'Aspect Ratio', 'value': f"{width}x{height}"}
                ])
        
        # Add tags as attributes
        for tag in metadata.tags[:5]:  # Limit to 5 tags
            attributes.append({'trait_type': 'Tag', 'value': tag})
        
        return attributes
    
    async def _upload_to_ipfs(self, content: Union[str, Dict], content_type: str) -> str:
        """Upload content to IPFS with Pinata pinning service."""



        try:
            if self.pinata_api_key and self.pinata_secret:
                # Use Pinata for IPFS pinning
                url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
                headers = {
                    'pinata_api_key': self.pinata_api_key,
                    'pinata_secret_api_key': self.pinata_secret
                }
                
                if content_type == 'file':
                    # Upload file
                    with open(content, 'rb') as file:
                        files = {'file': file}
                        response = requests.post(url, files=files, headers=headers)
                        
                        if response.status_code == 200:
                            ipfs_hash = response.json()['IpfsHash']
                            return f"ipfs://{ipfs_hash}"
                
                elif content_type == 'json':
                    # Upload JSON metadata
                    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
                    response = requests.post(url, json=content, headers=headers)
                    
                    if response.status_code == 200:
                        ipfs_hash = response.json()['IpfsHash']
                        return f"ipfs://{ipfs_hash}"
            
            # Fallback: generate mock IPFS hash
            content_str = str(content) if isinstance(content, dict) else content
            mock_hash = hashlib.sha256(content_str.encode()).hexdigest()[:46]
            return f"ipfs://Qm{mock_hash}"
            
        except Exception as e:
            self.logger.warning(f"IPFS upload failed, using fallback: {str(e)}")
            # Generate deterministic hash for testing
            content_str = str(content) if isinstance(content, dict) else content
            mock_hash = hashlib.sha256(content_str.encode()).hexdigest()[:46]
            return f"ipfs://Qm{mock_hash}"
    
    async def _deploy_nft_collection(self, name: str, symbol: str, network: BlockchainNetwork) -> str:
        """Deploy NFT collection smart contract."""



        try:
            from .smart_contracts import DeploymentConfig
            
            # Deploy NFT collection contract
            deployment_config = DeploymentConfig(
                network=network,
                gas_limit=3000000,
                gas_price=Decimal('30'),  # 30 Gwei
                constructor_args=[name, symbol]
            )
            
            deployment_id = await self.smart_contracts.deploy_contract(
                'nft_collection',
                deployment_config
            )
            
            # Get deployment info
            deployment_info = await self.smart_contracts.get_deployment_status(deployment_id)
            
            # Return mock contract address for now
            return f"0x{hashlib.sha256(f'{name}{symbol}{network.value}'.encode()).hexdigest()[:40]}"
            
        except Exception as e:
            self.logger.error(f"NFT collection deployment failed: {str(e)}")
            raise
    
    async def _setup_nft_royalties(self, token_id: str, creator_address: str, royalty_percentage: float):
        """Setup royalty tracking for NFT."""
        royalty = NFTRoyalty(
            token_id=token_id,
            creator_address=creator_address,
            royalty_percentage=royalty_percentage
        )
        
        self.royalties[token_id] = royalty
    
    async def _calculate_minting_cost(self, network: BlockchainNetwork) -> Dict[str, Any]:
        """Calculate estimated minting cost."""
        gas_estimates = {
            BlockchainNetwork.ETHEREUM: {'gas': 150000, 'price_gwei': 50},
            BlockchainNetwork.POLYGON: {'gas': 150000, 'price_gwei': 30},
            BlockchainNetwork.BINANCE_SMART_CHAIN: {'gas': 150000, 'price_gwei': 5}
        }
        
        estimate = gas_estimates.get(network, {'gas': 150000, 'price_gwei': 20})
        cost_eth = estimate['gas'] * estimate['price_gwei'] / 1e9
        
        return {
            'gas_used': estimate['gas'],
            'gas_price_gwei': estimate['price_gwei'],
            'cost_eth': cost_eth,
            'cost_usd': cost_eth * 2500  # Mock ETH price
        }
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_mime_type(self, file_format: str) -> str:
        """Get MIME type for file format."""
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.txt': 'text/plain',
            '.json': 'application/json'
        }
        return mime_types.get(file_format, 'application/octet-stream')
    
    def _extract_color_palette(self, image: Image.Image) -> List[str]:
        """Extract dominant color palette from image."""
        if not image:
            return []
        
        try:
            # Convert to RGB and get colors
            rgb_image = image.convert('RGB')
            colors = rgb_image.getcolors(maxcolors=256*256*256)
            
            if colors:
                # Sort by frequency and get top colors
                colors.sort(key=lambda x: x[0], reverse=True)
                palette = []
                
                for count, color in colors[:10]:  # Top 10 colors
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
                    palette.append(hex_color)
                
                return palette
            
        except Exception:
            pass
        
        return []
    
    async def get_nft_info(self, nft_id: str) -> Dict[str, Any]:
        """Get comprehensive information about an NFT."""
        if nft_id not in self.nfts:
            raise ValueError(f"NFT not found: {nft_id}")
        
        nft = self.nfts[nft_id]
        
        # Get royalty info
        royalty_info = None
        if nft['token_id'] in self.royalties:
            royalty = self.royalties[nft['token_id']]
            royalty_info = {
                'percentage': royalty.royalty_percentage,
                'total_earned': str(royalty.total_earned),
                'last_payment': royalty.last_payment.isoformat() if royalty.last_payment else None
            }
        
        # Get marketplace listings
        listings = self.marketplace_listings.get(nft_id, [])
        
        return {
            'nft_id': nft_id,
            'token_id': nft['token_id'],
            'collection_id': nft.get('collection_id'),
            'network': nft['network'],
            'contract_address': nft['contract_address'],
            'metadata': nft['metadata'],
            'content_info': nft['content_info'],
            'creation_date': nft['creation_date'].isoformat(),
            'minting_cost': nft.get('minting_cost', {}),
            'royalty_info': royalty_info,
            'marketplace_listings': len(listings),
            'traits': nft.get('traits', {}),
            'rarity_score': nft.get('rarity_score', 0),
            'status': nft['status']
        }
    
    async def get_nft_analytics(self) -> Dict[str, Any]:
        """Get comprehensive NFT creation and management analytics."""
        total_nfts = len(self.nfts)
        total_collections = len(self.collections)
        
        # NFT statistics by content type
        content_type_stats = {}
        for content_type in ContentType:
            nfts_of_type = [
                nft for nft in self.nfts.values()
                if nft['metadata'].get('content_type') == content_type.value
            ]
            content_type_stats[content_type.value] = len(nfts_of_type)
        
        # Network distribution
        network_stats = {}
        for nft in self.nfts.values():
            network = nft['network']
            network_stats[network] = network_stats.get(network, 0) + 1
        
        # Royalty statistics
        total_royalties_earned = sum(
            royalty.total_earned for royalty in self.royalties.values()
        )
        
        return {
            'total_nfts_created': total_nfts,
            'total_collections': total_collections,
            'content_type_distribution': content_type_stats,
            'network_distribution': network_stats,
            'total_marketplace_listings': sum(len(listings) for listings in self.marketplace_listings.values()),
            'total_royalties_earned': str(total_royalties_earned),
            'average_minting_cost': self._calculate_average_minting_cost(),
            'supported_formats': {ct.value: formats for ct, formats in self.supported_formats.items()},
            'supported_marketplaces': [mp.value for mp in MarketplaceType]
        }
    
    def _calculate_average_minting_cost(self) -> Dict[str, float]:
        """Calculate average minting costs across all NFTs."""
        costs = []
        for nft in self.nfts.values():
            if 'minting_cost' in nft and isinstance(nft['minting_cost'], dict):
                cost_usd = nft['minting_cost'].get('cost_usd', 0)
                if cost_usd > 0:
                    costs.append(cost_usd)
        
        if costs:
            return {
                'average_cost_usd': sum(costs) / len(costs),
                'min_cost_usd': min(costs),
                'max_cost_usd': max(costs)
            }
        
        return {'average_cost_usd': 0, 'min_cost_usd': 0, 'max_cost_usd': 0}
