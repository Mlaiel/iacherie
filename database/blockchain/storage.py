"""Decentralized Storage Management Module

Enterprise-grade IPFS and distributed storage integration for content fingerprints, 
metadata, and NFT assets within the IA Influencer Agent blockchain ecosystem.

Features:
- IPFS integration for decentralized content storage
- Content deduplication and versioning
- Distributed backup across multiple storage providers
- Content delivery network (CDN) integration
- Automatic content replication and availability monitoring
- Encryption and access control for sensitive content

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead AI Developer + Blockchain Specialist + Backend Senior + ML Engineer + 
      DBA + Security Expert + Microservices Architect + Audio Processing + 
      DevOps Engineer + IA Prompt Engineer

Copyright: All rights reserved. Unauthorized use prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, List, Any, Optional, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import hashlib
import io
import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from urllib.parse import urljoin
import magic
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

import ipfshttpclient
import requests
from PIL import Image

logger = logging.getLogger(__name__)

class StorageProvider(Enum):
    """Supported decentralized storage providers."""    IPFS = "ipfs"
    FILECOIN = "filecoin"
    ARWEAVE = "arweave"
    STORJ = "storj"
    SIA = "sia"

class ContentType(Enum):
    """Types of content stored in decentralized storage."""    FINGERPRINT = "fingerprint"
    METADATA = "metadata"
    EVIDENCE = "evidence"
    ORIGINAL_CONTENT = "original_content"
    THUMBNAIL = "thumbnail"
    PREVIEW = "preview"

class StorageStatus(Enum):
    """Status of storage operations."""    UPLOADING = "uploading"
    STORED = "stored"
    PINNED = "pinned"
    REPLICATED = "replicated"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class StorageMetadata:
    """Metadata for stored content."""    content_id: str
    original_filename: str
    content_type: ContentType
    mime_type: str
    file_size: int
    checksum_sha256: str
    checksum_md5: str
    upload_timestamp: datetime
    creator_address: str
    storage_provider: StorageProvider
    storage_hash: str
    storage_url: str
    pin_status: bool = False
    replication_count: int = 1
    expiry_date: Optional[datetime] = None
    encryption_key: Optional[str] = None
    access_permissions: List[str] = None

@dataclass
class StorageConfig:
    """Configuration for storage providers."""    provider: StorageProvider
    api_endpoint: str
    gateway_url: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    node_id: Optional[str] = None
    encryption_enabled: bool = True
    auto_pin: bool = True
    replication_factor: int = 3

class EncryptionManager:
    """Manager for content encryption and decryption."""    
    def __init__(self):
        """Initialize encryption manager."""        self.keys = {}
        
    def generate_key(self) -> str:
        """Generate a new encryption key."""        key = Fernet.generate_key()
        return key.decode('utf-8')
        
    def encrypt_content(self, content: bytes, key: str) -> bytes:
        """        Encrypt content with the provided key.
        
        Args:
            content: Raw content bytes
            key: Encryption key
            
        Returns:
            Encrypted content bytes
        """        try:
            f = Fernet(key.encode('utf-8'))
            encrypted_content = f.encrypt(content)
            return encrypted_content
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
            
    def decrypt_content(self, encrypted_content: bytes, key: str) -> bytes:
        """        Decrypt content with the provided key.
        
        Args:
            encrypted_content: Encrypted content bytes
            key: Encryption key
            
        Returns:
            Decrypted content bytes
        """        try:
            f = Fernet(key.encode('utf-8'))
            decrypted_content = f.decrypt(encrypted_content)
            return decrypted_content
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

class IPFSConnector:
    """IPFS connector for decentralized storage operations."""    
    def __init__(self, config: StorageConfig):
        """        Initialize IPFS connector.
        
        Args:
            config: IPFS configuration
        """        self.config = config
        self.api_base = config.api_endpoint
        self.gateway_base = config.gateway_url
        
    async def upload_content(
        self,
        content: bytes,
        filename: str,
        pin: bool = True
    ) -> Tuple[str, str]:
        """        Upload content to IPFS.
        
        Args:
            content: Content bytes to upload
            filename: Original filename
            pin: Whether to pin the content
            
        Returns:
            Tuple of (IPFS hash, gateway URL)
        """        try:
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file', content, filename=filename)
            
            # Add pin parameter
            params = {'pin': 'true' if pin else 'false'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/v0/add",
                    data=data,
                    params=params
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
            ipfs_hash = result['Hash']
            gateway_url = urljoin(self.gateway_base, ipfs_hash)
            
            logger.info(f"Uploaded {filename} to IPFS: {ipfs_hash}")
            return ipfs_hash, gateway_url
            
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            raise
            
    async def download_content(self, ipfs_hash: str) -> bytes:
        """        Download content from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the content
            
        Returns:
            Content bytes
        """        try:
            url = urljoin(self.gateway_base, ipfs_hash)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    
            return content
            
        except Exception as e:
            logger.error(f"IPFS download failed: {e}")
            raise
            
    async def pin_content(self, ipfs_hash: str) -> bool:
        """        Pin content to prevent garbage collection.
        
        Args:
            ipfs_hash: IPFS hash to pin
            
        Returns:
            True if pinning successful
        """        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/v0/pin/add",
                    params={'arg': ipfs_hash}
                ) as response:
                    response.raise_for_status()
                    
            logger.info(f"Pinned content: {ipfs_hash}")
            return True
            
        except Exception as e:
            logger.error(f"IPFS pinning failed: {e}")
            return False
            
    async def unpin_content(self, ipfs_hash: str) -> bool:
        """        Unpin content to allow garbage collection.
        
        Args:
            ipfs_hash: IPFS hash to unpin
            
        Returns:
            True if unpinning successful
        """        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/v0/pin/rm",
                    params={'arg': ipfs_hash}
                ) as response:
                    response.raise_for_status()
                    
            logger.info(f"Unpinned content: {ipfs_hash}")
            return True
            
        except Exception as e:
            logger.error(f"IPFS unpinning failed: {e}")
            return False

class DecentralizedStorageManager:
    """    Enterprise decentralized storage manager for the IA Influencer Agent platform.
    
    Handles content upload, storage, retrieval, and lifecycle management across
    multiple decentralized storage providers with encryption and redundancy.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize decentralized storage manager.
        
        Args:
            config: Configuration for storage providers and settings
        """        self.config = config
        self.encryption_manager = EncryptionManager()
        self.storage_metadata = {}  # In production, this would be in database
        self.connectors = {}
        self._initialize_connectors()
        
    def _initialize_connectors(self) -> None:
        """Initialize connectors for configured storage providers."""        storage_configs = self.config.get('storage_providers', {})
        
        for provider_name, provider_config in storage_configs.items():
            try:
                provider = StorageProvider(provider_name)
                config = StorageConfig(**provider_config)
                
                if provider == StorageProvider.IPFS:
                    self.connectors[provider] = IPFSConnector(config)
                # Add other providers as needed
                    
                logger.info(f"Initialized {provider.value} connector")
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider_name} connector: {e}")

    async def store_content(
        self,
        content: bytes,
        filename: str,
        content_type: ContentType,
        creator_address: str,
        provider: Optional[StorageProvider] = None,
        encrypt: bool = True,
        pin: bool = True
    ) -> StorageMetadata:
        """        Store content in decentralized storage.
        
        Args:
            content: Content bytes to store
            filename: Original filename
            content_type: Type of content being stored
            creator_address: Address of the content creator
            provider: Preferred storage provider (defaults to IPFS)
            encrypt: Whether to encrypt the content
            pin: Whether to pin the content
            
        Returns:
            Storage metadata with access information
        """        try:
            if not provider:
                provider = StorageProvider.IPFS
                
            connector = self.connectors.get(provider)
            if not connector:
                raise ValueError(f"No connector available for {provider.value}")
                
            logger.info(f"Storing content: {filename} ({len(content)} bytes)")
            
            # Calculate checksums
            sha256_hash = hashlib.sha256(content).hexdigest()
            md5_hash = hashlib.md5(content).hexdigest()
            
            # Encrypt content if requested
            encryption_key = None
            if encrypt:
                encryption_key = self.encryption_manager.generate_key()
                content = self.encryption_manager.encrypt_content(content, encryption_key)
                
            # Upload to storage provider
            storage_hash, storage_url = await connector.upload_content(
                content, filename, pin
            )
            
            # Create storage metadata
            content_id = f"{creator_address}_{sha256_hash}"
            metadata = StorageMetadata(
                content_id=content_id,
                original_filename=filename,
                content_type=content_type,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                file_size=len(content),
                checksum_sha256=sha256_hash,
                checksum_md5=md5_hash,
                upload_timestamp=datetime.utcnow(),
                creator_address=creator_address,
                storage_provider=provider,
                storage_hash=storage_hash,
                storage_url=storage_url,
                pin_status=pin,
                encryption_key=encryption_key,
                access_permissions=[creator_address]
            )
            
            # Store metadata
            self.storage_metadata[content_id] = metadata
            
            logger.info(f"Content stored successfully: {content_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Content storage failed: {e}")
            raise

    async def retrieve_content(
        self,
        content_id: str,
        requester_address: str
    ) -> Tuple[bytes, StorageMetadata]:
        """        Retrieve content from decentralized storage.
        
        Args:
            content_id: Unique content identifier
            requester_address: Address of the requester
            
        Returns:
            Tuple of (content bytes, storage metadata)
        """        try:
            metadata = self.storage_metadata.get(content_id)
            if not metadata:
                raise ValueError(f"Content {content_id} not found")
                
            # Check access permissions
            if requester_address not in metadata.access_permissions:
                raise PermissionError("Access denied")
                
            # Get connector for storage provider
            connector = self.connectors.get(metadata.storage_provider)
            if not connector:
                raise ValueError(f"No connector for {metadata.storage_provider.value}")
                
            # Download content
            content = await connector.download_content(metadata.storage_hash)
            
            # Decrypt if necessary
            if metadata.encryption_key:
                content = self.encryption_manager.decrypt_content(
                    content, metadata.encryption_key
                )
                
            # Verify integrity
            sha256_hash = hashlib.sha256(content).hexdigest()
            if sha256_hash != metadata.checksum_sha256:
                raise ValueError("Content integrity check failed")
                
            logger.info(f"Content retrieved successfully: {content_id}")
            return content, metadata
            
        except Exception as e:
            logger.error(f"Content retrieval failed: {e}")
            raise

    async def store_fingerprint(
        self,
        fingerprint_data: Dict[str, Any],
        content_hash: str,
        creator_address: str
    ) -> StorageMetadata:
        """        Store content fingerprint in decentralized storage.
        
        Args:
            fingerprint_data: Fingerprint data dictionary
            content_hash: Hash of the original content
            creator_address: Address of the content creator
            
        Returns:
            Storage metadata for the fingerprint
        """        try:
            # Serialize fingerprint data
            fingerprint_json = json.dumps(fingerprint_data, indent=2)
            fingerprint_bytes = fingerprint_json.encode('utf-8')
            
            # Generate filename
            filename = f"fingerprint_{content_hash}.json"
            
            return await self.store_content(
                content=fingerprint_bytes,
                filename=filename,
                content_type=ContentType.FINGERPRINT,
                creator_address=creator_address,
                encrypt=True,
                pin=True
            )
            
        except Exception as e:
            logger.error(f"Fingerprint storage failed: {e}")
            raise

    async def store_metadata(
        self,
        metadata_dict: Dict[str, Any],
        content_id: str,
        creator_address: str
    ) -> StorageMetadata:
        """        Store content metadata in decentralized storage.
        
        Args:
            metadata_dict: Metadata dictionary
            content_id: Associated content identifier
            creator_address: Address of the content creator
            
        Returns:
            Storage metadata for the metadata file
        """        try:
            # Serialize metadata
            metadata_json = json.dumps(metadata_dict, indent=2)
            metadata_bytes = metadata_json.encode('utf-8')
            
            # Generate filename
            filename = f"metadata_{content_id}.json"
            
            return await self.store_content(
                content=metadata_bytes,
                filename=filename,
                content_type=ContentType.METADATA,
                creator_address=creator_address,
                encrypt=False,  # Metadata is typically public
                pin=True
            )
            
        except Exception as e:
            logger.error(f"Metadata storage failed: {e}")
            raise

    async def batch_store_content(
        self,
        content_list: List[Tuple[bytes, str, ContentType, str]]
    ) -> List[StorageMetadata]:
        """        Store multiple content items in batch.
        
        Args:
            content_list: List of (content_bytes, filename, content_type, creator_address) tuples
            
        Returns:
            List of storage metadata for each item
        """        try:
            tasks = []
            for content, filename, content_type, creator_address in content_list:
                task = self.store_content(
                    content=content,
                    filename=filename,
                    content_type=content_type,
                    creator_address=creator_address
                )
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch storage failed for item {i}: {result}")
                else:
                    successful_results.append(result)
                    
            return successful_results
            
        except Exception as e:
            logger.error(f"Batch storage failed: {e}")
            raise

    async def replicate_content(
        self,
        content_id: str,
        target_providers: List[StorageProvider]
    ) -> Dict[StorageProvider, StorageMetadata]:
        """        Replicate content across multiple storage providers.
        
        Args:
            content_id: Content to replicate
            target_providers: List of target storage providers
            
        Returns:
            Dictionary mapping providers to storage metadata
        """        try:
            # Get original content
            original_metadata = self.storage_metadata.get(content_id)
            if not original_metadata:
                raise ValueError(f"Content {content_id} not found")
                
            # Retrieve content
            content, _ = await self.retrieve_content(
                content_id, original_metadata.creator_address
            )
            
            # Replicate to target providers
            replication_results = {}
            for provider in target_providers:
                if provider == original_metadata.storage_provider:
                    continue  # Skip original provider
                    
                try:
                    replica_metadata = await self.store_content(
                        content=content,
                        filename=original_metadata.original_filename,
                        content_type=original_metadata.content_type,
                        creator_address=original_metadata.creator_address,
                        provider=provider,
                        encrypt=bool(original_metadata.encryption_key),
                        pin=original_metadata.pin_status
                    )
                    replication_results[provider] = replica_metadata
                    
                except Exception as e:
                    logger.error(f"Replication to {provider.value} failed: {e}")
                    continue
                    
            return replication_results
            
        except Exception as e:
            logger.error(f"Content replication failed: {e}")
            raise

    def grant_access(self, content_id: str, user_address: str) -> bool:
        """        Grant access permission to content.
        
        Args:
            content_id: Content identifier
            user_address: Address to grant access to
            
        Returns:
            True if permission granted successfully
        """        try:
            metadata = self.storage_metadata.get(content_id)
            if not metadata:
                return False
                
            if user_address not in metadata.access_permissions:
                metadata.access_permissions.append(user_address)
                
            return True
            
        except Exception as e:
            logger.error(f"Access grant failed: {e}")
            return False

    def revoke_access(self, content_id: str, user_address: str) -> bool:
        """        Revoke access permission to content.
        
        Args:
            content_id: Content identifier
            user_address: Address to revoke access from
            
        Returns:
            True if permission revoked successfully
        """        try:
            metadata = self.storage_metadata.get(content_id)
            if not metadata:
                return False
                
            if user_address in metadata.access_permissions:
                metadata.access_permissions.remove(user_address)
                
            return True
            
        except Exception as e:
            logger.error(f"Access revocation failed: {e}")
            return False

    def list_content_by_creator(self, creator_address: str) -> List[StorageMetadata]:
        """List all content stored by a specific creator."""        return [
            metadata for metadata in self.storage_metadata.values()
            if metadata.creator_address == creator_address
        ]

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""        total_files = len(self.storage_metadata)
        total_size = sum(metadata.file_size for metadata in self.storage_metadata.values())
        
        provider_stats = {}
        for metadata in self.storage_metadata.values():
            provider = metadata.storage_provider.value
            if provider not in provider_stats:
                provider_stats[provider] = {"files": 0, "size": 0}
            provider_stats[provider]["files"] += 1
            provider_stats[provider]["size"] += metadata.file_size
            
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "provider_breakdown": provider_stats
        }

# Initialize module exports
__all__ = [
    "DecentralizedStorageManager",
    "IPFSConnector",
    "EncryptionManager",
    "StorageProvider",
    "ContentType",
    "StorageStatus",
    "StorageMetadata",
    "StorageConfig"
]
