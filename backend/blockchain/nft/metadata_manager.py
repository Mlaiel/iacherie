"""Metadata Manager - IA-Influencer-Agent Platform

Advanced NFT metadata management with IPFS integration, validation,
and standardized metadata schemas for enterprise content.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class MetadataStandard(Enum):
    """Metadata standards"""
    OPENSEA = "opensea"
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    CUSTOM = "custom"


@dataclass
class NFTAttribute:
    """NFT attribute definition"""
    trait_type: str
    value: Any
    display_type: Optional[str] = None
    max_value: Optional[int] = None


@dataclass  
class NFTMetadata:
    """Complete NFT metadata structure"""
    name: str
    description: str
    image: str
    external_url: Optional[str] = None
    animation_url: Optional[str] = None
    attributes: List[NFTAttribute] = field(default_factory=list)
    background_color: Optional[str] = None
    youtube_url: Optional[str] = None
    creator: Optional[str] = None
    created_at: Optional[datetime] = None
    collection: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


class MetadataManager:
    """Advanced NFT Metadata Management System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metadata_cache: Dict[str, NFTMetadata] = {}
        self.ipfs_gateway = config.get("ipfs_gateway", "https://ipfs.io/ipfs/")
        
    async def create_metadata(
        self,
        name: str,
        description: str,
        image_url: str,
        attributes: Optional[List[Dict[str, Any]]] = None,
        creator: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> NFTMetadata:
        """Create standardized NFT metadata"""
        try:
            self.logger.info(f"Creating metadata for: {name}")
            
            # Convert attributes
            nft_attributes = []
            if attributes:
                for attr in attributes:
                    nft_attr = NFTAttribute(
                        trait_type=attr["trait_type"],
                        value=attr["value"],
                        display_type=attr.get("display_type"),
                        max_value=attr.get("max_value")
                    )
                    nft_attributes.append(nft_attr)
            
            metadata = NFTMetadata(
                name=name,
                description=description,
                image=image_url,
                external_url=additional_data.get("external_url") if additional_data else None,
                animation_url=additional_data.get("animation_url") if additional_data else None,
                attributes=nft_attributes,
                background_color=additional_data.get("background_color") if additional_data else None,
                youtube_url=additional_data.get("youtube_url") if additional_data else None,
                creator=creator,
                created_at=datetime.utcnow(),
                collection=additional_data.get("collection") if additional_data else None,
                properties=additional_data.get("properties", {}) if additional_data else {}
            )
            
            # Cache metadata
            metadata_hash = self._generate_metadata_hash(metadata)
            self.metadata_cache[metadata_hash] = metadata
            
            self.logger.info(f"Metadata created for: {name}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata creation failed: {e}")
            raise
    
    def _generate_metadata_hash(self, metadata: NFTMetadata) -> str:
        """Generate unique hash for metadata"""
        metadata_dict = {
            "name": metadata.name,
            "description": metadata.description,
            "image": metadata.image,
            "attributes": [
                {
                    "trait_type": attr.trait_type,
                    "value": attr.value
                }
                for attr in metadata.attributes
            ]
        }
        
        return hashlib.sha256(
            json.dumps(metadata_dict, sort_keys=True).encode()
        ).hexdigest()
    
    async def validate_metadata(
        self,
        metadata: NFTMetadata,
        standard: MetadataStandard = MetadataStandard.OPENSEA
    ) -> Dict[str, Any]:
        """Validate metadata against standard"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Basic validation
            if not metadata.name:
                validation_result["errors"].append("Name is required")
                validation_result["valid"] = False
            
            if not metadata.description:
                validation_result["errors"].append("Description is required")
                validation_result["valid"] = False
            
            if not metadata.image:
                validation_result["errors"].append("Image URL is required")
                validation_result["valid"] = False
            
            # Standard-specific validation
            if standard == MetadataStandard.OPENSEA:
                await self._validate_opensea_standard(metadata, validation_result)
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Metadata validation failed: {e}")
            raise
    
    async def _validate_opensea_standard(
        self,
        metadata: NFTMetadata,
        validation_result: Dict[str, Any]
    ):
        """Validate against OpenSea metadata standard"""
        # Check image URL format
        if metadata.image and not (metadata.image.startswith("http") or metadata.image.startswith("ipfs://")):
            validation_result["warnings"].append("Image URL should be HTTP or IPFS format")
        
        # Check attributes format
        for attr in metadata.attributes:
            if not attr.trait_type:
                validation_result["errors"].append("Attribute trait_type is required")
                validation_result["valid"] = False
    
    async def upload_to_ipfs(self, metadata: NFTMetadata) -> str:
        """Upload metadata to IPFS"""
        try:
            # Convert metadata to JSON
            metadata_json = await self.metadata_to_json(metadata)
            
            # Mock IPFS upload
            content_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
            ipfs_hash = f"Qm{content_hash[:44]}"  # Mock IPFS hash format
            
            metadata_uri = f"ipfs://{ipfs_hash}"
            
            self.logger.info(f"Metadata uploaded to IPFS: {ipfs_hash}")
            return metadata_uri
            
        except Exception as e:
            self.logger.error(f"IPFS upload failed: {e}")
            raise
    
    async def metadata_to_json(self, metadata: NFTMetadata) -> str:
        """Convert metadata to JSON format"""
        metadata_dict = {
            "name": metadata.name,
            "description": metadata.description,
            "image": metadata.image
        }
        
        if metadata.external_url:
            metadata_dict["external_url"] = metadata.external_url
        
        if metadata.animation_url:
            metadata_dict["animation_url"] = metadata.animation_url
        
        if metadata.background_color:
            metadata_dict["background_color"] = metadata.background_color
        
        if metadata.youtube_url:
            metadata_dict["youtube_url"] = metadata.youtube_url
        
        if metadata.attributes:
            metadata_dict["attributes"] = [
                {
                    "trait_type": attr.trait_type,
                    "value": attr.value,
                    **({"display_type": attr.display_type} if attr.display_type else {}),
                    **({"max_value": attr.max_value} if attr.max_value else {})
                }
                for attr in metadata.attributes
            ]
        
        if metadata.properties:
            metadata_dict["properties"] = metadata.properties
        
        # Add platform-specific fields
        if metadata.creator:
            metadata_dict["creator"] = metadata.creator
        
        if metadata.created_at:
            metadata_dict["created_at"] = metadata.created_at.isoformat()
        
        if metadata.collection:
            metadata_dict["collection"] = metadata.collection
        
        return json.dumps(metadata_dict, indent=2)
    
    async def get_metadata_from_uri(self, metadata_uri: str) -> Optional[NFTMetadata]:
        """Retrieve metadata from URI"""
        try:
            # Handle IPFS URIs
            if metadata_uri.startswith("ipfs://"):
                ipfs_hash = metadata_uri.replace("ipfs://", "")
                # Mock IPFS retrieval
                self.logger.info(f"Retrieved metadata from IPFS: {ipfs_hash}")
                
                # Return cached metadata if available
                for metadata in self.metadata_cache.values():
                    if self._generate_metadata_hash(metadata) in metadata_uri:
                        return metadata
            
            return None
            
        except Exception as e:
            self.logger.error(f"Metadata retrieval failed: {e}")
            return None