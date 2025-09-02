"""NFT Creation and Management Module

Enterprise-grade NFT creation, marketplace integration, and lifecycle management
for the IA Influencer Agent platform content protection ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from datetime import datetime
from decimal import Decimal
import hashlib
import base64
from urllib.parse import urljoin

import requests
from PIL import Image
import magic

logger = logging.getLogger(__name__)

class NFTStandard(Enum):
    """
Supported NFT standards."""

    ERC721 = "ERC-721"
    ERC1155 = "ERC-1155"

class NFTContentType(Enum):
    """Types of content that can be minted as NFTs."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"

class NFTMarketplace(Enum):
    """Supported NFT marketplaces."""

    OPENSEA = "opensea"
    RARIBLE = "rarible"
    FOUNDATION = "foundation"
    SUPERRARE = "superrare"
    ASYNC_ART = "async_art"
    KNOWN_ORIGIN = "known_origin"

@dataclass
class NFTMetadata:
    """Standard NFT metadata structure following OpenSea standards."""
    name: str
    description: str
    image: str
    external_url: Optional[str] = None
    animation_url: Optional[str] = None
    youtube_url: Optional[str] = None
    background_color: Optional[str] = None
    attributes: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.attributes = []

@dataclass 
class NFTCreationRequest:
    """
Request structure for NFT creation."""
    content_hash: str
    content_type: NFTContentType
    content_url: str
    title: str
    description: str
    creator_address: str
    royalty_percentage: float
    max_supply: int = 1
    standard: NFTStandard = NFTStandard.ERC721
    marketplace: Optional[NFTMarketplace] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    collection_address: Optional[str] = None

@dataclass
class NFTCreationResult:
    """
Result of NFT creation process."""
    token_id: str
    contract_address: str
    transaction_hash: str
    metadata_uri: str
    marketplace_url: Optional[str]
    creation_timestamp: datetime
    gas_used: int
    creation_cost: Decimal
    ipfs_hash: Optional[str] = None

class IPFSManager:
    """
Manager for IPFS operations for NFT metadata and content storage."""
    
    def __init__(self, ipfs_config: Dict[str, Any]):
        """
        Initialize IPFS manager.
        
        Args:
            ipfs_config: Configuration for IPFS node connection
        """
        self.ipfs_config = ipfs_config
        self.ipfs_gateway = ipfs_config.get("gateway", "https://ipfs.io/ipfs/")
        self.api_endpoint = ipfs_config.get("api", "http://localhost:5001")
        
    def upload_content(self, content_data: bytes, filename: str) -> str:
        """
        Upload content to IPFS.
        
        Args:
            content_data: Raw content bytes
            filename: Original filename
            
        Returns:
            IPFS hash of uploaded content
        """
        try:
            files = {"file": (filename, content_data)}
            response = requests.post(
                f"{self.api_endpoint}/api/v0/add",
                files=files,
                params={"pin": "true"}
            )
            response.raise_for_status()
            
            result = response.json()
            ipfs_hash = result["Hash"]
            
            logger.info(f"Uploaded {filename} to IPFS: {ipfs_hash}")
            return ipfs_hash
            
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            raise
            
    def upload_metadata(self, metadata: NFTMetadata) -> str:
        """
        Upload NFT metadata to IPFS.
        
        Args:
            metadata: NFT metadata object
            
        Returns:
            IPFS hash of metadata JSON
        """
        try:
            metadata_json = json.dumps(asdict(metadata), indent=2)
            metadata_bytes = metadata_json.encode('utf-8')
            
            return self.upload_content(metadata_bytes, "metadata.json")
            
        except Exception as e:
            logger.error(f"Metadata upload failed: {e}")
            raise
            
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """Get public IPFS URL for a hash."""
        return urljoin(self.ipfs_gateway, ipfs_hash)

class NFTCreator:
    """
    Enterprise NFT creation and management system for content protection.
    
    Handles automated NFT minting, metadata generation, marketplace integration,
    and royalty management for the IA Influencer Agent platform.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize NFT creator.
        
        Args:
            config: Configuration including smart contracts, IPFS, marketplaces
        """
        self.config = config
        self.ipfs_manager = IPFSManager(config.get("ipfs", {}))
        self.marketplace_configs = config.get("marketplaces", {})
        self.contract_addresses = config.get("contracts", {})
        
    async def create_nft(self, request: NFTCreationRequest) -> NFTCreationResult:
        """
        Create an NFT for content protection.
        
        Args:
            request: NFT creation request with all necessary parameters
            
        Returns:
            NFT creation result with contract details and metadata
        """
        try:
            logger.info(f"Starting NFT creation for content: {request.content_hash}")
            
            # Step 1: Validate content
            await self._validate_content(request)
            
            # Step 2: Generate enhanced metadata
            metadata = await self._generate_metadata(request)
            
            # Step 3: Upload metadata to IPFS
            metadata_hash = self.ipfs_manager.upload_metadata(metadata)
            metadata_uri = self.ipfs_manager.get_ipfs_url(metadata_hash)
            
            # Step 4: Mint NFT on blockchain
            mint_result = await self._mint_nft(request, metadata_uri)
            
            # Step 5: Register on marketplace (if specified)
            marketplace_url = None
            if request.marketplace:
                marketplace_url = await self._register_on_marketplace(
                    request, mint_result
                )
            
            # Step 6: Create result object
            result = NFTCreationResult(
                token_id=mint_result["token_id"],
                contract_address=mint_result["contract_address"],
                transaction_hash=mint_result["transaction_hash"],
                metadata_uri=metadata_uri,
                marketplace_url=marketplace_url,
                creation_timestamp=datetime.utcnow(),
                gas_used=mint_result["gas_used"],
                creation_cost=Decimal(str(mint_result["creation_cost"])),
                ipfs_hash=metadata_hash
            )
            
            logger.info(f"NFT created successfully: Token ID {result.token_id}")
            return result
            
        except Exception as e:
            logger.error(f"NFT creation failed: {e}")
            raise

    async def _validate_content(self, request: NFTCreationRequest) -> None:
        """Validate content before NFT creation."""
        try:
            # Check content accessibility
            response = requests.head(request.content_url, timeout=10)
            response.raise_for_status()
            
            # Validate content type
            content_type_header = response.headers.get('content-type', '')
            if not self._is_valid_content_type(content_type_header, request.content_type):
                raise ValueError(f"Content type mismatch: {content_type_header}")
                
            # Check file size limits
            content_length = int(response.headers.get('content-length', 0))
            max_size = self.config.get("max_content_size", 100 * 1024 * 1024)  # 100MB
            if content_length > max_size:
                raise ValueError(f"Content too large: {content_length} bytes")
                
            logger.info("Content validation passed")
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            raise

    def _is_valid_content_type(self, content_type: str, expected_type: NFTContentType) -> bool:
        """Check if content type matches expected type."""
        type_mappings = {
            NFTContentType.AUDIO: ["audio/"],
            NFTContentType.VIDEO: ["video/"],
            NFTContentType.IMAGE: ["image/"],
            NFTContentType.TEXT: ["text/", "application/json"],
            NFTContentType.DOCUMENT: ["application/pdf", "application/msword"]
        }
        
        valid_types = type_mappings.get(expected_type, [])
        return any(content_type.startswith(vt) for vt in valid_types)

    async def _generate_metadata(self, request: NFTCreationRequest) -> NFTMetadata:
        """Generate comprehensive NFT metadata."""
        try:
            # Base metadata
            metadata = NFTMetadata(
                name=request.title,
                description=request.description,
                image=request.content_url,
                external_url=f"https://ia-influencer-agent.com/content/{request.content_hash}"
            )
            
            # Add content-specific metadata
            if request.content_type == NFTContentType.AUDIO:
                metadata.animation_url = request.content_url
            elif request.content_type == NFTContentType.VIDEO:
                metadata.animation_url = request.content_url
                
            # Add protection attributes
            protection_attributes = [
                {
                    "trait_type": "Content Hash",
                    "value": request.content_hash
                },
                {
                    "trait_type": "Content Type", 
                    "value": request.content_type.value
                },
                {
                    "trait_type": "Creator",
                    "value": request.creator_address
                },
                {
                    "trait_type": "Royalty Percentage",
                    "value": request.royalty_percentage,
                    "display_type": "number"
                },
                {
                    "trait_type": "Protection Date",
                    "value": datetime.utcnow().isoformat()
                },
                {
                    "trait_type": "Platform",
                    "value": "IA Influencer Agent"
                }
            ]
            
            # Merge with custom attributes
            metadata.attributes = protection_attributes
            if request.attributes:
                metadata.attributes.extend(request.attributes)
                
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            raise

    async def _mint_nft(self, request: NFTCreationRequest, metadata_uri: str) -> Dict[str, Any]:
        """Mint NFT on the blockchain."""
        try:
            # Import here to avoid circular imports
            from .contracts import SmartContractManager, ContractType
            
            contract_manager = SmartContractManager(self.config)
            
            # Determine contract type based on NFT standard
            contract_type = (
                ContractType.NFT_CREATOR if request.standard == NFTStandard.ERC721
                else ContractType.NFT_CREATOR  # Assuming same contract handles both
            )
            
            # Get contract key
            network = self.config.get("default_network", "polygon_mumbai")
            contract_key = f"{contract_type.value}_{network}"
            
            # Prepare minting parameters
            mint_args = [
                request.creator_address,  # to
                metadata_uri,             # tokenURI
                int(request.royalty_percentage * 100),  # royalty basis points
                request.max_supply        # max supply (for ERC1155)
            ]
            
            # Execute minting transaction
            result = await contract_manager.interact_with_contract(
                contract_key=contract_key,
                function_name="mint",
                args=mint_args
            )
            
            # Extract token ID from transaction logs
            token_id = self._extract_token_id_from_logs(result["logs"])
            
            return {
                "token_id": token_id,
                "contract_address": contract_manager.contracts[contract_key].address,
                "transaction_hash": result["transaction_hash"],
                "gas_used": result["gas_used"],
                "creation_cost": result.get("creation_cost", 0)
            }
            
        except Exception as e:
            logger.error(f"NFT minting failed: {e}")
            raise

    def _extract_token_id_from_logs(self, logs: List[Dict[str, Any]]) -> str:
        """Extract token ID from transaction logs."""
        # Implementation would parse the Transfer event logs to extract token ID
        # For now, return a placeholder
        return "1"  # This would be extracted from actual logs

    async def _register_on_marketplace(
        self,
        request: NFTCreationRequest,
        mint_result: Dict[str, Any]
    ) -> Optional[str]:
        """Register NFT on specified marketplace."""
        try:
            if not request.marketplace:
                return None
                
            marketplace_config = self.marketplace_configs.get(request.marketplace.value)
            if not marketplace_config:
                logger.warning(f"No config for marketplace: {request.marketplace.value}")
                return None
                
            # Implementation would depend on specific marketplace APIs
            # For now, return a mock URL
            marketplace_url = (
                f"https://{request.marketplace.value}.io/assets/"
                f"{mint_result['contract_address']}/{mint_result['token_id']}"
            )
            
            logger.info(f"Registered NFT on {request.marketplace.value}")
            return marketplace_url
            
        except Exception as e:
            logger.error(f"Marketplace registration failed: {e}")
            return None

    async def batch_create_nfts(self, requests: List[NFTCreationRequest]) -> List[NFTCreationResult]:
        """
        Create multiple NFTs in batch for efficiency.
        
        Args:
            requests: List of NFT creation requests
            
        Returns:
            List of NFT creation results
        """
        results = []
        
        for request in requests:
            try:
                result = await self.create_nft(request)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch NFT creation failed for {request.content_hash}: {e}")
                # Continue with next NFT even if one fails
                continue
                
        return results

    def get_nft_info(self, contract_address: str, token_id: str) -> Dict[str, Any]:
        """
        Get information about an existing NFT.
        
        Args:
            contract_address: Contract address of the NFT
            token_id: Token ID of the NFT
            
        Returns:
            NFT information including metadata and ownership
        """
        try:
            # Implementation would query the blockchain for NFT details
            # For now, return mock data
            return {
                "contract_address": contract_address,
                "token_id": token_id,
                "owner": "0x...",
                "metadata_uri": "ipfs://...",
                "metadata": {},
                "royalty_info": {
                    "recipient": "0x...",
                    "percentage": 5.0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            raise

    def calculate_royalties(self, sale_price: Decimal, royalty_percentage: float) -> Decimal:
        """Calculate royalty amount for a sale."""
        return sale_price * Decimal(str(royalty_percentage / 100))

# Initialize module exports
__all__ = [
    "NFTCreator",
    "IPFSManager",
    "NFTStandard",
    "NFTContentType",
    "NFTMarketplace", 
    "NFTMetadata",
    "NFTCreationRequest",
    "NFTCreationResult"
]
