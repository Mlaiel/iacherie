"""IPFS Storage Module - IA-Influencer-Agent Platform

This module provides comprehensive IPFS (InterPlanetary File System) storage functionality
for the backend layer, enabling decentralized storage of content, metadata, NFT assets,
and other platform data with content addressing and distributed availability.

Features:
- IPFS content upload and retrieval
- Content pinning and availability management
- Distributed content replication
- Content encryption and access control
- Metadata storage and management
- Content deduplication
- Gateway management and CDN integration
- Storage analytics and monitoring

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid
import hashlib
import hmac
import base64
import io
import mimetypes
from pathlib import Path

import aiohttp
import aiofiles
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content that can be stored"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    METADATA = "metadata"
    NFT_ASSET = "nft_asset"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"


class StorageStatus(Enum):
    """Storage operation status"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    PINNED = "pinned"
    REPLICATED = "replicated"
    FAILED = "failed"
    REMOVED = "removed"


class PinStatus(Enum):
    """Pin status for content"""
    PINNED = "pinned"
    UNPINNED = "unpinned"
    QUEUED = "queued"
    FAILED = "failed"


class AccessLevel(Enum):
    """Content access levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    CREATOR_ONLY = "creator_only"


@dataclass
class StorageConfig:
    """IPFS storage configuration"""
    ipfs_api_url: str
    ipfs_gateway_url: str
    cluster_endpoints: List[str]
    pin_services: List[str]
    encryption_enabled: bool
    max_file_size: int
    allowed_content_types: List[str]
    replication_factor: int


@dataclass
class ContentMetadata:
    """Content metadata structure"""
    name: str
    description: str
    content_type: ContentType
    file_size: int
    mime_type: str
    checksum: str
    creator_address: str
    access_level: AccessLevel
    tags: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class StorageResult:
    """Storage operation result"""
    content_id: str
    ipfs_hash: str
    content_uri: str
    gateway_url: str
    metadata: ContentMetadata
    storage_status: StorageStatus
    pin_status: PinStatus
    uploaded_at: datetime
    file_size: int
    encryption_key: Optional[str] = None


@dataclass
class ReplicationInfo:
    """Content replication information"""
    content_id: str
    ipfs_hash: str
    replica_locations: List[str]
    replication_factor: int
    last_verified: datetime
    availability_score: Decimal


class IPFSStorage:
    """
    IPFS Storage system for decentralized content storage
    """
    
    def __init__(self, config: StorageConfig):
        """
        Initialize IPFS Storage
        
        Args:
            config: IPFS storage configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stored_content: Dict[str, StorageResult] = {}
        self.replication_info: Dict[str, ReplicationInfo] = {}
        
        # Initialize IPFS client connections
        self.ipfs_api_url = config.ipfs_api_url
        self.gateway_url = config.ipfs_gateway_url
        self.cluster_endpoints = config.cluster_endpoints
        
        # Pin services configuration
        self.pin_services = config.pin_services
        
        # Content encryption settings
        self.encryption_enabled = config.encryption_enabled
        self.encryption_keys: Dict[str, str] = {}
        
    async def upload_content(
        self,
        content: Union[bytes, str, io.BytesIO],
        metadata: ContentMetadata,
        pin: bool = True,
        encrypt: bool = False
    ) -> StorageResult:
        """
        Upload content to IPFS
        
        Args:
            content: Content to upload (bytes, string, or file-like object)
            metadata: Content metadata
            pin: Whether to pin the content
            encrypt: Whether to encrypt the content
            
        Returns:
            Storage result with IPFS hash and details
        """
        try:
            content_id = str(uuid.uuid4())
            
            self.logger.info(f"Uploading content to IPFS: {metadata.name}")
            
            # Prepare content for upload
            content_bytes = await self._prepare_content(content, metadata)
            
            # Encrypt content if requested
            encryption_key = None
            if encrypt or (self.encryption_enabled and metadata.access_level != AccessLevel.PUBLIC):
                content_bytes, encryption_key = await self._encrypt_content(content_bytes)
            
            # Calculate content hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            metadata.checksum = content_hash
            
            # Upload to IPFS
            ipfs_hash = await self._upload_to_ipfs(content_bytes)
            
            # Generate content URIs
            content_uri = f"ipfs://{ipfs_hash}"
            gateway_url = f"{self.gateway_url}/ipfs/{ipfs_hash}"
            
            # Create storage result
            storage_result = StorageResult(
                content_id=content_id,
                ipfs_hash=ipfs_hash,
                content_uri=content_uri,
                gateway_url=gateway_url,
                metadata=metadata,
                storage_status=StorageStatus.UPLOADED,
                pin_status=PinStatus.QUEUED if pin else PinStatus.UNPINNED,
                uploaded_at=datetime.utcnow(),
                file_size=len(content_bytes),
                encryption_key=encryption_key
            )
            
            # Store content record
            self.stored_content[content_id] = storage_result
            if encryption_key:
                self.encryption_keys[content_id] = encryption_key
            
            # Pin content if requested
            if pin:
                await self._pin_content(ipfs_hash)
                storage_result.pin_status = PinStatus.PINNED
                storage_result.storage_status = StorageStatus.PINNED
            
            # Start replication process
            if self.config.replication_factor > 1:
                asyncio.create_task(self._replicate_content(content_id, ipfs_hash))
            
            self.logger.info(f"Content uploaded to IPFS: {content_id} -> {ipfs_hash}")
            return storage_result
            
        except Exception as e:
            self.logger.error(f"Content upload failed: {e}")
            raise
    
    async def _prepare_content(
        self,
        content: Union[bytes, str, io.BytesIO],
        metadata: ContentMetadata
    ) -> bytes:
        """Prepare content for upload"""
        if isinstance(content, str):
            return content.encode('utf-8')
        elif isinstance(content, bytes):
            return content
        elif hasattr(content, 'read'):
            return content.read()
        else:
            raise ValueError("Unsupported content type")
    
    async def _encrypt_content(self, content: bytes) -> Tuple[bytes, str]:
        """Encrypt content using AES encryption"""
        # Generate encryption key
        key = get_random_bytes(32)  # 256-bit key
        iv = get_random_bytes(16)   # 128-bit IV
        
        # Encrypt content
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_content = pad(content, AES.block_size)
        encrypted_content = cipher.encrypt(padded_content)
        
        # Combine IV and encrypted content
        encrypted_data = iv + encrypted_content
        
        # Encode key for storage
        encryption_key = base64.b64encode(key).decode('utf-8')
        
        return encrypted_data, encryption_key
    
    async def _upload_to_ipfs(self, content: bytes) -> str:
        """Upload content to IPFS and return hash"""
        try:
            # Mock IPFS upload - in real implementation would use IPFS HTTP API
            content_hash = hashlib.sha256(content).hexdigest()
            ipfs_hash = f"Qm{content_hash[:44]}"  # Mock IPFS hash format
            
            # Simulate API call
            async with aiohttp.ClientSession() as session:
                # In real implementation would use IPFS API
                # data = aiohttp.FormData()
                # data.add_field('file', content, content_type='application/octet-stream')
                # async with session.post(f"{self.ipfs_api_url}/api/v0/add", data=data) as response:
                #     result = await response.json()
                #     return result['Hash']
                pass
            
            return ipfs_hash
            
        except Exception as e:
            self.logger.error(f"IPFS upload failed: {e}")
            raise
    
    async def _pin_content(self, ipfs_hash: str) -> bool:
        """Pin content to ensure availability"""
        try:
            self.logger.info(f"Pinning content: {ipfs_hash}")
            
            # Pin on local node
            local_pin_success = await self._pin_on_local_node(ipfs_hash)
            
            # Pin on external services
            pin_services_success = await self._pin_on_services(ipfs_hash)
            
            return local_pin_success and pin_services_success
            
        except Exception as e:
            self.logger.error(f"Content pinning failed: {e}")
            return False
    
    async def _pin_on_local_node(self, ipfs_hash: str) -> bool:
        """Pin content on local IPFS node"""
        try:
            # Mock local pinning - in real implementation would use IPFS API
            async with aiohttp.ClientSession() as session:
                # async with session.post(f"{self.ipfs_api_url}/api/v0/pin/add?arg={ipfs_hash}") as response:
                #     return response.status == 200
                pass
            
            return True  # Mock success
            
        except Exception as e:
            self.logger.error(f"Local pinning failed: {e}")
            return False
    
    async def _pin_on_services(self, ipfs_hash: str) -> bool:
        """Pin content on external pin services"""
        success_count = 0
        
        for service in self.pin_services:
            try:
                # Mock service pinning
                success = await self._pin_on_service(service, ipfs_hash)
                if success:
                    success_count += 1
                    
            except Exception as e:
                self.logger.error(f"Pinning on service {service} failed: {e}")
        
        return success_count > 0
    
    async def _pin_on_service(self, service: str, ipfs_hash: str) -> bool:
        """Pin content on specific pin service"""
        # Mock service-specific pinning logic
        self.logger.info(f"Pinning {ipfs_hash} on service {service}")
        return True  # Mock success
    
    async def _replicate_content(self, content_id: str, ipfs_hash: str) -> None:
        """Replicate content across multiple nodes"""
        try:
            self.logger.info(f"Starting replication for content: {content_id}")
            
            replica_locations = []
            target_replicas = self.config.replication_factor
            
            # Replicate to cluster nodes
            for endpoint in self.cluster_endpoints[:target_replicas]:
                try:
                    success = await self._replicate_to_node(endpoint, ipfs_hash)
                    if success:
                        replica_locations.append(endpoint)
                except Exception as e:
                    self.logger.error(f"Replication to {endpoint} failed: {e}")
            
            # Update replication info
            replication_info = ReplicationInfo(
                content_id=content_id,
                ipfs_hash=ipfs_hash,
                replica_locations=replica_locations,
                replication_factor=len(replica_locations),
                last_verified=datetime.utcnow(),
                availability_score=Decimal(str(len(replica_locations) / target_replicas))
            )
            
            self.replication_info[content_id] = replication_info
            
            # Update storage status
            if content_id in self.stored_content:
                self.stored_content[content_id].storage_status = StorageStatus.REPLICATED
            
            self.logger.info(f"Content replicated: {content_id} to {len(replica_locations)} locations")
            
        except Exception as e:
            self.logger.error(f"Content replication failed: {e}")
    
    async def _replicate_to_node(self, endpoint: str, ipfs_hash: str) -> bool:
        """Replicate content to specific node"""
        try:
            # Mock replication to cluster node
            async with aiohttp.ClientSession() as session:
                # In real implementation would use IPFS cluster API
                pass
            
            return True  # Mock success
            
        except Exception as e:
            self.logger.error(f"Node replication failed: {e}")
            return False
    
    async def retrieve_content(
        self,
        content_id: str,
        decrypt: bool = True
    ) -> Tuple[bytes, ContentMetadata]:
        """
        Retrieve content from IPFS
        
        Args:
            content_id: Content ID to retrieve
            decrypt: Whether to decrypt encrypted content
            
        Returns:
            Content bytes and metadata
        """
        try:
            if content_id not in self.stored_content:
                raise ValueError(f"Content not found: {content_id}")
            
            storage_result = self.stored_content[content_id]
            
            self.logger.info(f"Retrieving content from IPFS: {content_id}")
            
            # Retrieve content from IPFS
            content_bytes = await self._retrieve_from_ipfs(storage_result.ipfs_hash)
            
            # Decrypt if necessary
            if decrypt and storage_result.encryption_key:
                content_bytes = await self._decrypt_content(
                    content_bytes, storage_result.encryption_key
                )
            
            return content_bytes, storage_result.metadata
            
        except Exception as e:
            self.logger.error(f"Content retrieval failed: {e}")
            raise
    
    async def _retrieve_from_ipfs(self, ipfs_hash: str) -> bytes:
        """Retrieve content from IPFS"""
        try:
            # Mock IPFS retrieval - in real implementation would use IPFS gateway or API
            async with aiohttp.ClientSession() as session:
                # async with session.get(f"{self.gateway_url}/ipfs/{ipfs_hash}") as response:
                #     return await response.read()
                pass
            
            # Mock content for demonstration
            return b"Mock IPFS content data"
            
        except Exception as e:
            self.logger.error(f"IPFS retrieval failed: {e}")
            raise
    
    async def _decrypt_content(self, encrypted_content: bytes, encryption_key: str) -> bytes:
        """Decrypt encrypted content"""
        try:
            # Decode encryption key
            key = base64.b64decode(encryption_key.encode('utf-8'))
            
            # Extract IV and encrypted data
            iv = encrypted_content[:16]
            encrypted_data = encrypted_content[16:]
            
            # Decrypt content
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_content = cipher.decrypt(encrypted_data)
            content = unpad(padded_content, AES.block_size)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Content decryption failed: {e}")
            raise
    
    async def delete_content(self, content_id: str) -> Dict[str, Any]:
        """
        Delete content from IPFS (unpin and remove)
        
        Args:
            content_id: Content ID to delete
            
        Returns:
            Deletion result
        """
        try:
            if content_id not in self.stored_content:
                raise ValueError(f"Content not found: {content_id}")
            
            storage_result = self.stored_content[content_id]
            
            self.logger.info(f"Deleting content from IPFS: {content_id}")
            
            # Unpin content
            unpin_success = await self._unpin_content(storage_result.ipfs_hash)
            
            # Remove from local storage
            if content_id in self.stored_content:
                del self.stored_content[content_id]
            
            if content_id in self.encryption_keys:
                del self.encryption_keys[content_id]
            
            if content_id in self.replication_info:
                del self.replication_info[content_id]
            
            result = {
                "content_id": content_id,
                "ipfs_hash": storage_result.ipfs_hash,
                "unpin_success": unpin_success,
                "deleted_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Content deleted: {content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content deletion failed: {e}")
            raise
    
    async def _unpin_content(self, ipfs_hash: str) -> bool:
        """Unpin content to allow garbage collection"""
        try:
            # Unpin from local node
            local_unpin_success = await self._unpin_from_local_node(ipfs_hash)
            
            # Unpin from services
            services_unpin_success = await self._unpin_from_services(ipfs_hash)
            
            return local_unpin_success and services_unpin_success
            
        except Exception as e:
            self.logger.error(f"Content unpinning failed: {e}")
            return False
    
    async def _unpin_from_local_node(self, ipfs_hash: str) -> bool:
        """Unpin content from local IPFS node"""
        try:
            # Mock local unpinning
            return True
            
        except Exception as e:
            self.logger.error(f"Local unpinning failed: {e}")
            return False
    
    async def _unpin_from_services(self, ipfs_hash: str) -> bool:
        """Unpin content from external pin services"""
        success_count = 0
        
        for service in self.pin_services:
            try:
                success = await self._unpin_from_service(service, ipfs_hash)
                if success:
                    success_count += 1
                    
            except Exception as e:
                self.logger.error(f"Unpinning from service {service} failed: {e}")
        
        return success_count > 0
    
    async def _unpin_from_service(self, service: str, ipfs_hash: str) -> bool:
        """Unpin content from specific pin service"""
        # Mock service-specific unpinning logic
        return True
    
    async def get_content_info(self, content_id: str) -> Dict[str, Any]:
        """Get detailed content information"""
        if content_id not in self.stored_content:
            raise ValueError(f"Content not found: {content_id}")
        
        storage_result = self.stored_content[content_id]
        replication_info = self.replication_info.get(content_id)
        
        content_info = {
            "content_id": content_id,
            "ipfs_hash": storage_result.ipfs_hash,
            "content_uri": storage_result.content_uri,
            "gateway_url": storage_result.gateway_url,
            "metadata": {
                "name": storage_result.metadata.name,
                "description": storage_result.metadata.description,
                "content_type": storage_result.metadata.content_type.value,
                "file_size": storage_result.metadata.file_size,
                "mime_type": storage_result.metadata.mime_type,
                "checksum": storage_result.metadata.checksum,
                "creator_address": storage_result.metadata.creator_address,
                "access_level": storage_result.metadata.access_level.value,
                "tags": storage_result.metadata.tags,
                "created_at": storage_result.metadata.created_at.isoformat(),
                "custom_fields": storage_result.metadata.custom_fields
            },
            "storage_status": storage_result.storage_status.value,
            "pin_status": storage_result.pin_status.value,
            "uploaded_at": storage_result.uploaded_at.isoformat(),
            "file_size": storage_result.file_size,
            "encrypted": storage_result.encryption_key is not None
        }
        
        if replication_info:
            content_info["replication"] = {
                "replica_locations": replication_info.replica_locations,
                "replication_factor": replication_info.replication_factor,
                "last_verified": replication_info.last_verified.isoformat(),
                "availability_score": str(replication_info.availability_score)
            }
        
        return content_info
    
    async def list_content(
        self,
        creator_address: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        access_level: Optional[AccessLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List stored content with filtering"""
        content_list = []
        
        for content_id, storage_result in list(self.stored_content.items())[:limit]:
            # Apply filters
            if creator_address and storage_result.metadata.creator_address != creator_address:
                continue
            
            if content_type and storage_result.metadata.content_type != content_type:
                continue
            
            if access_level and storage_result.metadata.access_level != access_level:
                continue
            
            content_info = await self.get_content_info(content_id)
            content_list.append(content_info)
        
        return content_list
    
    async def verify_content_availability(self, content_id: str) -> Dict[str, Any]:
        """Verify content availability across storage locations"""
        if content_id not in self.stored_content:
            raise ValueError(f"Content not found: {content_id}")
        
        storage_result = self.stored_content[content_id]
        replication_info = self.replication_info.get(content_id)
        
        # Check availability on different sources
        gateway_available = await self._check_gateway_availability(storage_result.ipfs_hash)
        local_available = await self._check_local_availability(storage_result.ipfs_hash)
        
        replica_availability = {}
        if replication_info:
            for replica in replication_info.replica_locations:
                replica_availability[replica] = await self._check_replica_availability(
                    replica, storage_result.ipfs_hash
                )
        
        total_available = sum([gateway_available, local_available] + list(replica_availability.values()))
        total_sources = 2 + len(replica_availability)
        availability_percentage = (total_available / total_sources) * 100
        
        return {
            "content_id": content_id,
            "ipfs_hash": storage_result.ipfs_hash,
            "gateway_available": gateway_available,
            "local_available": local_available,
            "replica_availability": replica_availability,
            "availability_percentage": availability_percentage,
            "verified_at": datetime.utcnow().isoformat()
        }
    
    async def _check_gateway_availability(self, ipfs_hash: str) -> bool:
        """Check if content is available through IPFS gateway"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(f"{self.gateway_url}/ipfs/{ipfs_hash}") as response:
                    return response.status == 200
        except:
            return False
    
    async def _check_local_availability(self, ipfs_hash: str) -> bool:
        """Check if content is available on local IPFS node"""
        # Mock local availability check
        return True
    
    async def _check_replica_availability(self, replica: str, ipfs_hash: str) -> bool:
        """Check if content is available on replica node"""
        # Mock replica availability check
        return True


class StorageManager:
    """
    Manager class for coordinating multiple IPFS storage instances
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Storage Manager
        
        Args:
            config: Global storage configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.storage_instances: Dict[str, IPFSStorage] = {}
        
        # Initialize storage instances for different networks/regions
        storage_configs = config.get("storage_instances", {})
        for instance_name, instance_config in storage_configs.items():
            storage_config = StorageConfig(**instance_config)
            self.storage_instances[instance_name] = IPFSStorage(storage_config)
    
    async def distribute_content(
        self,
        content: Union[bytes, str, io.BytesIO],
        metadata: ContentMetadata,
        target_instances: Optional[List[str]] = None
    ) -> Dict[str, StorageResult]:
        """
        Distribute content across multiple storage instances
        
        Args:
            content: Content to distribute
            metadata: Content metadata
            target_instances: Specific instances to target (or all if None)
            
        Returns:
            Storage results from each instance
        """
        if target_instances is None:
            target_instances = list(self.storage_instances.keys())
        
        results = {}
        
        for instance_name in target_instances:
            if instance_name in self.storage_instances:
                try:
                    storage = self.storage_instances[instance_name]
                    result = await storage.upload_content(content, metadata)
                    results[instance_name] = result
                    self.logger.info(f"Content distributed to {instance_name}")
                except Exception as e:
                    self.logger.error(f"Distribution to {instance_name} failed: {e}")
                    results[instance_name] = {"error": str(e)}
        
        return results
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics across all instances"""
        stats = {
            "total_instances": len(self.storage_instances),
            "instance_names": list(self.storage_instances.keys()),
            "global_stats": {
                "total_content": 0,
                "total_size": 0,
                "total_replications": 0
            },
            "instance_stats": {}
        }
        
        for instance_name, storage in self.storage_instances.items():
            content_count = len(storage.stored_content)
            total_size = sum(result.file_size for result in storage.stored_content.values())
            replication_count = len(storage.replication_info)
            
            stats["instance_stats"][instance_name] = {
                "content_count": content_count,
                "total_size": total_size,
                "replications": replication_count
            }
            
            stats["global_stats"]["total_content"] += content_count
            stats["global_stats"]["total_size"] += total_size
            stats["global_stats"]["total_replications"] += replication_count
        
        return stats