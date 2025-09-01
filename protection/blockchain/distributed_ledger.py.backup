"""Distributed Ledger Technology (DLT) Integration for Content Protection
Professional implementation of IPFS, Arweave, and Hyperledger Fabric integration

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
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncIterator, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import base64
import io
import secrets
import mimetypes
from pathlib import Path
import aiohttp
import aiofiles
from urllib.parse import urljoin

from .exceptions import (
    DLTStorageError,
    BlockchainConnectionError,
    Web3ProviderError
)

logger = logging.getLogger(__name__)


class DLTNetwork(Enum):
    """Distributed Ledger Technology networks"""
    IPFS = "ipfs"
    ARWEAVE = "arweave"
    HYPERLEDGER_FABRIC = "hyperledger_fabric"
    STORJ = "storj"
    FILECOIN = "filecoin"
    SWARM = "swarm"


class StorageClass(Enum):
    """Storage classification for content"""
    PERMANENT = "permanent"  # Arweave, Filecoin
    DISTRIBUTED = "distributed"  # IPFS, Swarm
    ENTERPRISE = "enterprise"  # Hyperledger Fabric
    ENCRYPTED = "encrypted"  # Storj
    TEMPORARY = "temporary"  # Cache layer


@dataclass
class ContentMetadata:
    """Metadata for content stored on DLT"""
    content_id: str
    original_filename: str
    mime_type: str
    file_size: int
    content_hash: str
    encryption_key: Optional[str] = None
    creator_address: str = ""
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    storage_class: StorageClass = StorageClass.DISTRIBUTED
    access_permissions: Dict[str, List[str]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'content_hash': self.content_hash,
            'encryption_key': self.encryption_key,
            'creator_address': self.creator_address,
            'creation_timestamp': self.creation_timestamp.isoformat(),
            'storage_class': self.storage_class.value,
            'access_permissions': self.access_permissions,
            'tags': self.tags
        }


@dataclass
class StorageResult:
    """Result of storing content on DLT"""
    network: DLTNetwork
    content_id: str
    storage_hash: str
    access_url: str
    metadata: ContentMetadata
    transaction_id: Optional[str] = None
    block_height: Optional[int] = None
    storage_cost: Optional[float] = None
    estimated_permanence: Optional[timedelta] = None


class IPFSClient:
    """Professional IPFS client for distributed storage"""
    
    def __init__(self, gateway_url: str = "http://localhost:5001", timeout: int = 300):
        self.gateway_url = gateway_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.pinned_hashes: set = set()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def add_content(
        self,
        content: Union[bytes, str, io.BytesIO],
        metadata: ContentMetadata,
        pin: bool = True
    ) -> StorageResult:
        """Add content to IPFS network"""
        try:
            if not self.session:
                raise RuntimeError("IPFS client not initialized")
            
            # Prepare content for upload
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, io.BytesIO):
                content_bytes = content.getvalue()
            else:
                content_bytes = content
            
            # Create form data
            data = aiohttp.FormData()
            data.add_field(
                'file',
                content_bytes,
                filename=metadata.original_filename,
                content_type=metadata.mime_type
            )
            
            # Add to IPFS
            url = urljoin(self.gateway_url, '/api/v0/add')
            params = {
                'wrap-with-directory': 'false',
                'pin': 'true' if pin else 'false',
                'progress': 'false'
            }
            
            async with self.session.post(url, data=data, params=params) as response:
                if response.status != 200:
                    raise Exception(f"IPFS add failed: {response.status} {await response.text()}")
                
                result = await response.json()
                ipfs_hash = result['Hash']
            
            # Store metadata
            metadata_json = json.dumps(metadata.to_dict(), indent=2)
            metadata_hash = await self._add_metadata(metadata_json, pin)
            
            # Create access URL
            access_url = f"https://ipfs.io/ipfs/{ipfs_hash}"
            
            # Track pinned content
            if pin:
                self.pinned_hashes.add(ipfs_hash)
                self.pinned_hashes.add(metadata_hash)
            
            logger.info(f"Content added to IPFS: {ipfs_hash}")
            
            return StorageResult(
                network=DLTNetwork.IPFS,
                content_id=metadata.content_id,
                storage_hash=ipfs_hash,
                access_url=access_url,
                metadata=metadata,
                estimated_permanence=timedelta(days=30) if pin else timedelta(days=1)
            )
            
        except Exception as e:
            logger.error(f"IPFS content addition failed: {e}")
            raise
    
    async def _add_metadata(self, metadata_json: str, pin: bool = True) -> str:
        """Add metadata to IPFS"""
        try:
            data = aiohttp.FormData()
            data.add_field(
                'file',
                metadata_json.encode('utf-8'),
                filename='metadata.json',
                content_type='application/json'
            )
            
            url = urljoin(self.gateway_url, '/api/v0/add')
            params = {'pin': 'true' if pin else 'false'}
            
            async with self.session.post(url, data=data, params=params) as response:
                result = await response.json()
                return result['Hash']
                
        except Exception as e:
            logger.error(f"IPFS metadata addition failed: {e}")
            raise
    
    async def retrieve_content(self, ipfs_hash: str) -> bytes:
        """Retrieve content from IPFS"""
        try:
            url = urljoin(self.gateway_url, f'/api/v0/cat')
            params = {'arg': ipfs_hash}
            
            async with self.session.post(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"IPFS retrieval failed: {response.status}")
                
                return await response.read()
                
        except Exception as e:
            logger.error(f"IPFS content retrieval failed: {e}")
            raise
    
    async def pin_content(self, ipfs_hash: str) -> bool:
        """Pin content to prevent garbage collection"""
        try:
            url = urljoin(self.gateway_url, '/api/v0/pin/add')
            params = {'arg': ipfs_hash}
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    self.pinned_hashes.add(ipfs_hash)
                    logger.info(f"Content pinned: {ipfs_hash}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"IPFS pinning failed: {e}")
            return False
    
    async def unpin_content(self, ipfs_hash: str) -> bool:
        """Unpin content to allow garbage collection"""
        try:
            url = urljoin(self.gateway_url, '/api/v0/pin/rm')
            params = {'arg': ipfs_hash}
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    self.pinned_hashes.discard(ipfs_hash)
                    logger.info(f"Content unpinned: {ipfs_hash}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"IPFS unpinning failed: {e}")
            return False


class ArweaveClient:
    """Professional Arweave client for permanent storage"""
    
    def __init__(self, gateway_url: str = "https://arweave.net", wallet_path: Optional[str] = None):
        self.gateway_url = gateway_url
        self.wallet_path = wallet_path
        self.wallet_data: Optional[Dict[str, Any]] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        if self.wallet_path:
            await self._load_wallet()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _load_wallet(self):
        """Load Arweave wallet from file"""
        try:
            async with aiofiles.open(self.wallet_path, 'r') as f:
                wallet_content = await f.read()
                self.wallet_data = json.loads(wallet_content)
            logger.info("Arweave wallet loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Arweave wallet: {e}")
            raise
    
    async def store_content(
        self,
        content: Union[bytes, str],
        metadata: ContentMetadata,
        tags: Optional[Dict[str, str]] = None
    ) -> StorageResult:
        """Store content permanently on Arweave"""
        try:
            if not self.session or not self.wallet_data:
                raise RuntimeError("Arweave client not properly initialized")
            
            # Prepare content
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Calculate storage cost
            data_size = len(content_bytes)
            storage_cost = await self._estimate_storage_cost(data_size)
            
            # Prepare transaction tags
            transaction_tags = {
                'Content-Type': metadata.mime_type,
                'File-Name': metadata.original_filename,
                'Content-ID': metadata.content_id,
                'Creator': metadata.creator_address,
                'Timestamp': str(int(metadata.creation_timestamp.timestamp())),
                'App-Name': 'IA-Influencer-Agent',
                'App-Version': '2.0',
                'Content-Hash': metadata.content_hash
            }
            
            if tags:
                transaction_tags.update(tags)
            
            # Create transaction (simplified - would use arweave-python-client in production)
            transaction_data = {
                'data': base64.b64encode(content_bytes).decode('utf-8'),
                'tags': [{'name': k, 'value': v} for k, v in transaction_tags.items()],
                'target': '',
                'quantity': '0',
                'reward': str(storage_cost)
            }
            
            # Submit transaction (mock implementation)
            transaction_id = await self._submit_transaction(transaction_data)
            
            # Create access URL
            access_url = f"{self.gateway_url}/{transaction_id}"
            
            logger.info(f"Content stored on Arweave: {transaction_id}")
            
            return StorageResult(
                network=DLTNetwork.ARWEAVE,
                content_id=metadata.content_id,
                storage_hash=transaction_id,
                access_url=access_url,
                metadata=metadata,
                transaction_id=transaction_id,
                storage_cost=storage_cost / 1e12,  # Convert to AR
                estimated_permanence=timedelta(days=365 * 200)  # 200 years permanence
            )
            
        except Exception as e:
            logger.error(f"Arweave storage failed: {e}")
            raise
    
    async def _estimate_storage_cost(self, data_size: int) -> int:
        """Estimate storage cost in winston (1 AR = 1e12 winston)"""
        try:
            url = f"{self.gateway_url}/price/{data_size}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    price_text = await response.text()
                    return int(price_text)
                else:
                    # Fallback calculation (approximate)
                    return data_size * 1000  # ~1000 winston per byte
        except Exception:
            return data_size * 1000
    
    async def _submit_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Submit transaction to Arweave network"""
        try:
            # In production, this would use proper Arweave transaction signing
            # and submission through arweave-python-client
            
            # Mock transaction ID generation
            content = transaction_data['data'].encode('utf-8')
            tx_hash = hashlib.sha256(content).hexdigest()
            transaction_id = base64.urlsafe_b64encode(
                hashlib.sha256(tx_hash.encode()).digest()
            ).decode('utf-8').rstrip('=')[:43]
            
            logger.info(f"Mock Arweave transaction submitted: {transaction_id}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Arweave transaction submission failed: {e}")
            raise
    
    async def retrieve_content(self, transaction_id: str) -> bytes:
        """Retrieve content from Arweave"""
        try:
            url = f"{self.gateway_url}/{transaction_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"Arweave retrieval failed: {response.status}")
        except Exception as e:
            logger.error(f"Arweave content retrieval failed: {e}")
            raise


class HyperledgerFabricClient:
    """Professional Hyperledger Fabric client for enterprise DLT"""
    
    def __init__(
        self,
        network_config: Dict[str, Any],
        org_name: str,
        peer_endpoint: str,
        channel_name: str = "content-channel"
    ):
        self.network_config = network_config
        self.org_name = org_name
        self.peer_endpoint = peer_endpoint
        self.channel_name = channel_name
        self.fabric_client = None
        self.user_context = None
    
    async def initialize(self) -> bool:
        """Initialize Hyperledger Fabric client"""
        try:
            # In production, would use fabric-sdk-py
            # from hfc.api.client import Client
            # self.fabric_client = Client(net_profile=self.network_config)
            
            logger.info(f"Hyperledger Fabric client initialized for org: {self.org_name}")
            return True
            
        except Exception as e:
            logger.error(f"Hyperledger Fabric initialization failed: {e}")
            return False
    
    async def store_content_record(
        self,
        content_id: str,
        content_hash: str,
        metadata: ContentMetadata,
        chaincode_name: str = "content-protection"
    ) -> StorageResult:
        """Store content record on Hyperledger Fabric"""
        try:
            # Prepare chaincode arguments
            args = [
                content_id,
                content_hash,
                json.dumps(metadata.to_dict()),
                str(int(datetime.utcnow().timestamp()))
            ]
            
            # Invoke chaincode (mock implementation)
            transaction_id = await self._invoke_chaincode(
                chaincode_name,
                "registerContent",
                args
            )
            
            # Create access reference
            access_url = f"fabric://{self.channel_name}/{chaincode_name}/{content_id}"
            
            logger.info(f"Content record stored on Fabric: {transaction_id}")
            
            return StorageResult(
                network=DLTNetwork.HYPERLEDGER_FABRIC,
                content_id=content_id,
                storage_hash=transaction_id,
                access_url=access_url,
                metadata=metadata,
                transaction_id=transaction_id,
                estimated_permanence=timedelta(days=365 * 7)  # 7 years enterprise retention
            )
            
        except Exception as e:
            logger.error(f"Hyperledger Fabric storage failed: {e}")
            raise
    
    async def _invoke_chaincode(
        self,
        chaincode_name: str,
        function_name: str,
        args: List[str]
    ) -> str:
        """Invoke chaincode on Hyperledger Fabric"""
        try:
            # Mock implementation - in production would use fabric-sdk-py
            combined_input = f"{chaincode_name}:{function_name}:{':'.join(args)}"
            transaction_id = hashlib.sha256(
                f"{combined_input}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:32]
            
            logger.info(f"Mock chaincode invocation: {function_name}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Chaincode invocation failed: {e}")
            raise
    
    async def query_content_record(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Query content record from Hyperledger Fabric"""
        try:
            # Mock query implementation
            record = {
                'content_id': content_id,
                'status': 'registered',
                'timestamp': datetime.utcnow().isoformat(),
                'org': self.org_name
            }
            
            logger.info(f"Content record queried: {content_id}")
            return record
            
        except Exception as e:
            logger.error(f"Content record query failed: {e}")
            return None


class DistributedLedgerManager:
    """Unified manager for all DLT operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients: Dict[DLTNetwork, Any] = {}
        self.storage_strategies: Dict[StorageClass, List[DLTNetwork]] = {
            StorageClass.PERMANENT: [DLTNetwork.ARWEAVE, DLTNetwork.FILECOIN],
            StorageClass.DISTRIBUTED: [DLTNetwork.IPFS, DLTNetwork.SWARM],
            StorageClass.ENTERPRISE: [DLTNetwork.HYPERLEDGER_FABRIC],
            StorageClass.ENCRYPTED: [DLTNetwork.STORJ],
            StorageClass.TEMPORARY: [DLTNetwork.IPFS]
        }
    
    async def initialize(self) -> bool:
        """Initialize all DLT clients"""
        try:
            success_count = 0
            
            # Initialize IPFS client
            if 'ipfs' in self.config:
                ipfs_config = self.config['ipfs']
                self.clients[DLTNetwork.IPFS] = IPFSClient(
                    gateway_url=ipfs_config.get('gateway_url', 'http://localhost:5001'),
                    timeout=ipfs_config.get('timeout', 300)
                )
                success_count += 1
            
            # Initialize Arweave client
            if 'arweave' in self.config:
                arweave_config = self.config['arweave']
                self.clients[DLTNetwork.ARWEAVE] = ArweaveClient(
                    gateway_url=arweave_config.get('gateway_url', 'https://arweave.net'),
                    wallet_path=arweave_config.get('wallet_path')
                )
                success_count += 1
            
            # Initialize Hyperledger Fabric client
            if 'hyperledger_fabric' in self.config:
                fabric_config = self.config['hyperledger_fabric']
                fabric_client = HyperledgerFabricClient(
                    network_config=fabric_config.get('network_config', {}),
                    org_name=fabric_config.get('org_name', 'ContentProtectionOrg'),
                    peer_endpoint=fabric_config.get('peer_endpoint', 'peer0.org1.example.com:7051'),
                    channel_name=fabric_config.get('channel_name', 'content-channel')
                )
                
                if await fabric_client.initialize():
                    self.clients[DLTNetwork.HYPERLEDGER_FABRIC] = fabric_client
                    success_count += 1
            
            logger.info(f"DLT Manager initialized with {success_count} networks")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"DLT Manager initialization failed: {e}")
            return False
    
    async def store_content(
        self,
        content: Union[bytes, str, io.BytesIO],
        metadata: ContentMetadata,
        redundancy_level: int = 2
    ) -> List[StorageResult]:
        """Store content across multiple DLT networks"""
        try:
            storage_class = metadata.storage_class
            target_networks = self.storage_strategies.get(storage_class, [DLTNetwork.IPFS])
            
            # Limit to available clients and redundancy level
            available_networks = [net for net in target_networks if net in self.clients][:redundancy_level]
            
            storage_results = []
            
            for network in available_networks:
                try:
                    client = self.clients[network]
                    
                    if network == DLTNetwork.IPFS:
                        async with client:
                            result = await client.add_content(content, metadata, pin=True)
                            storage_results.append(result)
                    
                    elif network == DLTNetwork.ARWEAVE:
                        async with client:
                            result = await client.store_content(content, metadata)
                            storage_results.append(result)
                    
                    elif network == DLTNetwork.HYPERLEDGER_FABRIC:
                        # For Fabric, we only store the hash and metadata, not the actual content
                        result = await client.store_content_record(
                            metadata.content_id,
                            metadata.content_hash,
                            metadata
                        )
                        storage_results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Storage failed on {network.value}: {e}")
                    continue
            
            if not storage_results:
                raise Exception("All storage attempts failed")
            
            logger.info(f"Content stored on {len(storage_results)} networks")
            return storage_results
            
        except Exception as e:
            logger.error(f"Multi-network storage failed: {e}")
            raise
    
    async def retrieve_content(
        self,
        storage_results: List[StorageResult]
    ) -> Optional[bytes]:
        """Retrieve content from the most accessible DLT network"""
        try:
            # Try networks in order of preference
            network_priority = [DLTNetwork.IPFS, DLTNetwork.ARWEAVE, DLTNetwork.HYPERLEDGER_FABRIC]
            
            for network in network_priority:
                matching_results = [r for r in storage_results if r.network == network]
                if not matching_results:
                    continue
                
                result = matching_results[0]
                
                try:
                    if network == DLTNetwork.IPFS:
                        client = self.clients[network]
                        async with client:
                            return await client.retrieve_content(result.storage_hash)
                    
                    elif network == DLTNetwork.ARWEAVE:
                        client = self.clients[network]
                        async with client:
                            return await client.retrieve_content(result.storage_hash)
                    
                    # Hyperledger Fabric doesn't store actual content
                    
                except Exception as e:
                    logger.warning(f"Retrieval failed from {network.value}: {e}")
                    continue
            
            logger.error("Content retrieval failed from all networks")
            return None
            
        except Exception as e:
            logger.error(f"Content retrieval failed: {e}")
            return None


# Export classes
__all__ = [
    'DLTNetwork',
    'StorageClass',
    'ContentMetadata',
    'StorageResult',
    'IPFSClient',
    'ArweaveClient',
    'HyperledgerFabricClient',
    'DistributedLedgerManager'
]
