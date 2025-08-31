"""
Enterprise Archival Storage Backend System

Provides hierarchical storage management with multiple tiers,
cloud integration, and intelligent data placement for optimal
cost and performance balance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import logging
import json
import hashlib
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import uuid
import boto3
from botocore.exceptions import ClientError
import aiofiles
import aiofiles.os

from .models import ArchiveEntry
from .archival_manager import ArchivalTier
from ..exceptions import ArchivalError, StorageQuotaExceededError


class ArchivalStorageBackend(ABC):
    """Abstract base class for archival storage backends"""
    
    @abstractmethod
    async def store_archive(
        self,
        archive_id: str,
        content_data: bytes,
        tier: ArchivalTier,
        metadata: Dict[str, Any]
    ) -> str:
        """Store archive content and return storage path"""
        pass
    
    @abstractmethod
    async def retrieve_archive(self, archive_id: str) -> Optional[bytes]:
        """Retrieve archive content by ID"""
        pass
    
    @abstractmethod
    async def delete_archive(self, archive_id: str) -> bool:
        """Delete archive from storage"""
        pass
    
    @abstractmethod
    async def migrate_archive(self, archive_id: str, target_tier: ArchivalTier) -> bool:
        """Migrate archive to different storage tier"""
        pass
    
    @abstractmethod
    async def get_archive_metadata(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Get archive metadata"""
        pass
    
    @abstractmethod
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform storage backend health check"""
        pass


class LocalArchivalStorage(ArchivalStorageBackend):
    """Local filesystem archival storage backend"""
    
    def __init__(self, base_path: str, enable_redundancy: bool = True):
        self.base_path = Path(base_path)
        self.enable_redundancy = enable_redundancy
        self.logger = logging.getLogger("archival.storage.local")
        
        # Create tier directories
        self.tier_paths = {
            ArchivalTier.HOT: self.base_path / "hot",
            ArchivalTier.WARM: self.base_path / "warm", 
            ArchivalTier.COLD: self.base_path / "cold",
            ArchivalTier.FROZEN: self.base_path / "frozen",
            ArchivalTier.DEEP_FREEZE: self.base_path / "deep_freeze"
        }
        
        self.metadata_path = self.base_path / "metadata"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        
        for tier_path in self.tier_paths.values():
            tier_path.mkdir(exist_ok=True)
            
            if self.enable_redundancy:
                (tier_path / "replicas").mkdir(exist_ok=True)
    
    async def store_archive(
        self,
        archive_id: str,
        content_data: bytes,
        tier: ArchivalTier,
        metadata: Dict[str, Any]
    ) -> str:
        """Store archive in local filesystem"""



        
        try:
            tier_path = self.tier_paths[tier]
            archive_file = tier_path / f"{archive_id}.archive"
            metadata_file = self.metadata_path / f"{archive_id}.json"
            
            # Store content data
            async with aiofiles.open(archive_file, 'wb') as f:
                await f.write(content_data)
            
            # Calculate checksum for integrity
            checksum = hashlib.sha256(content_data).hexdigest()
            
            # Prepare extended metadata
            extended_metadata = {
                **metadata,
                "storage_backend": "local",
                "storage_path": str(archive_file),
                "checksum": checksum,
                "stored_at": datetime.utcnow().isoformat(),
                "file_size": len(content_data),
                "tier": tier.value
            }
            
            # Store metadata
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(extended_metadata, indent=2))
            
            # Create replica if redundancy enabled
            if self.enable_redundancy:
                replica_file = tier_path / "replicas" / f"{archive_id}.archive"
                async with aiofiles.open(replica_file, 'wb') as f:
                    await f.write(content_data)
            
            self.logger.info(f"Stored archive {archive_id} in tier {tier.value}")
            return str(archive_file)
            
        except Exception as e:
            self.logger.error(f"Failed to store archive {archive_id}: {e}")
            raise ArchivalError(f"Storage operation failed: {e}")
    
    async def retrieve_archive(self, archive_id: str) -> Optional[bytes]:
        """Retrieve archive from local filesystem"""



        
        try:
            # Find archive across all tiers
            for tier, tier_path in self.tier_paths.items():
                archive_file = tier_path / f"{archive_id}.archive"
                
                if archive_file.exists():
                    async with aiofiles.open(archive_file, 'rb') as f:
                        content_data = await f.read()
                    
                    # Verify checksum
                    metadata = await self.get_archive_metadata(archive_id)
                    if metadata and "checksum" in metadata:
                        expected_checksum = metadata["checksum"]
                        actual_checksum = hashlib.sha256(content_data).hexdigest()
                        
                        if actual_checksum != expected_checksum:
                            self.logger.warning(f"Checksum mismatch for archive {archive_id}")
                            
                            # Try replica if available
                            if self.enable_redundancy:
                                replica_file = tier_path / "replicas" / f"{archive_id}.archive"
                                if replica_file.exists():
                                    async with aiofiles.open(replica_file, 'rb') as f:
                                        content_data = await f.read()
                                    
                                    actual_checksum = hashlib.sha256(content_data).hexdigest()
                                    if actual_checksum == expected_checksum:
                                        self.logger.info(f"Retrieved archive {archive_id} from replica")
                                        return content_data
                            
                            raise ArchivalError(f"Data integrity check failed for archive {archive_id}")
                    
                    self.logger.info(f"Retrieved archive {archive_id} from tier {tier.value}")
                    return content_data
            
            self.logger.warning(f"Archive {archive_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve archive {archive_id}: {e}")
            return None
    
    async def delete_archive(self, archive_id: str) -> bool:
        """Delete archive from local filesystem"""



        
        try:
            deleted = False
            
            # Delete from all tiers
            for tier_path in self.tier_paths.values():
                archive_file = tier_path / f"{archive_id}.archive"
                replica_file = tier_path / "replicas" / f"{archive_id}.archive"
                
                if archive_file.exists():
                    await aiofiles.os.remove(archive_file)
                    deleted = True
                
                if self.enable_redundancy and replica_file.exists():
                    await aiofiles.os.remove(replica_file)
            
            # Delete metadata
            metadata_file = self.metadata_path / f"{archive_id}.json"
            if metadata_file.exists():
                await aiofiles.os.remove(metadata_file)
                deleted = True
            
            if deleted:
                self.logger.info(f"Deleted archive {archive_id}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Failed to delete archive {archive_id}: {e}")
            return False
    
    async def migrate_archive(self, archive_id: str, target_tier: ArchivalTier) -> bool:
        """Migrate archive to different tier"""



        
        try:
            # Find current location
            current_tier = None
            current_path = None
            
            for tier, tier_path in self.tier_paths.items():
                archive_file = tier_path / f"{archive_id}.archive"
                if archive_file.exists():
                    current_tier = tier
                    current_path = archive_file
                    break
            
            if not current_path:
                self.logger.warning(f"Archive {archive_id} not found for migration")
                return False
            
            if current_tier == target_tier:
                self.logger.info(f"Archive {archive_id} already in target tier {target_tier.value}")
                return True
            
            # Read content
            async with aiofiles.open(current_path, 'rb') as f:
                content_data = await f.read()
            
            # Store in target tier
            target_path = self.tier_paths[target_tier] / f"{archive_id}.archive"
            async with aiofiles.open(target_path, 'wb') as f:
                await f.write(content_data)
            
            # Handle replica
            if self.enable_redundancy:
                current_replica = self.tier_paths[current_tier] / "replicas" / f"{archive_id}.archive"
                target_replica = self.tier_paths[target_tier] / "replicas" / f"{archive_id}.archive"
                
                if current_replica.exists():
                    async with aiofiles.open(current_replica, 'rb') as f:
                        replica_data = await f.read()
                    
                    async with aiofiles.open(target_replica, 'wb') as f:
                        await f.write(replica_data)
                    
                    await aiofiles.os.remove(current_replica)
            
            # Remove from current tier
            await aiofiles.os.remove(current_path)
            
            # Update metadata
            metadata = await self.get_archive_metadata(archive_id)
            if metadata:
                metadata["tier"] = target_tier.value
                metadata["migrated_at"] = datetime.utcnow().isoformat()
                metadata["storage_path"] = str(target_path)
                
                metadata_file = self.metadata_path / f"{archive_id}.json"
                async with aiofiles.open(metadata_file, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
            
            self.logger.info(f"Migrated archive {archive_id} from {current_tier.value} to {target_tier.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate archive {archive_id}: {e}")
            return False
    
    async def get_archive_metadata(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Get archive metadata"""



        
        try:
            metadata_file = self.metadata_path / f"{archive_id}.json"
            
            if metadata_file.exists():
                async with aiofiles.open(metadata_file, 'r') as f:
                    content = await f.read()
                return json.loads(content)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata for archive {archive_id}: {e}")
            return None
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics"""



        
        try:
            stats = {
                "total_archives": 0,
                "total_size": 0,
                "tier_statistics": {},
                "redundancy_enabled": self.enable_redundancy
            }
            
            for tier, tier_path in self.tier_paths.items():
                tier_stats = {
                    "archive_count": 0,
                    "total_size": 0,
                    "replica_count": 0 if self.enable_redundancy else None
                }
                
                # Count main archives
                if tier_path.exists():
                    for archive_file in tier_path.glob("*.archive"):
                        tier_stats["archive_count"] += 1
                        tier_stats["total_size"] += archive_file.stat().st_size
                
                # Count replicas
                if self.enable_redundancy:
                    replica_path = tier_path / "replicas"
                    if replica_path.exists():
                        tier_stats["replica_count"] = len(list(replica_path.glob("*.archive")))
                
                stats["tier_statistics"][tier.value] = tier_stats
                stats["total_archives"] += tier_stats["archive_count"]
                stats["total_size"] += tier_stats["total_size"]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get storage statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform storage backend health check"""
        
        health = {
            "status": "healthy",
            "checks": {},
            "issues": []
        }
        
        try:
            # Check directory accessibility
            for tier, tier_path in self.tier_paths.items():
                if not tier_path.exists():
                    health["checks"][f"tier_{tier.value}_exists"] = False
                    health["issues"].append(f"Tier directory {tier.value} does not exist")
                else:
                    health["checks"][f"tier_{tier.value}_exists"] = True
                
                # Check write permissions
                try:
                    test_file = tier_path / ".health_check"
                    test_file.write_text("test")
                    test_file.unlink()
                    health["checks"][f"tier_{tier.value}_writable"] = True
                except Exception:
                    health["checks"][f"tier_{tier.value}_writable"] = False
                    health["issues"].append(f"Tier directory {tier.value} is not writable")
            
            # Check metadata directory
            if not self.metadata_path.exists():
                health["checks"]["metadata_dir_exists"] = False
                health["issues"].append("Metadata directory does not exist")
            else:
                health["checks"]["metadata_dir_exists"] = True
            
            # Check disk space
            disk_usage = shutil.disk_usage(self.base_path)
            free_space_gb = disk_usage.free / (1024**3)
            
            if free_space_gb < 1.0:  # Less than 1GB free
                health["checks"]["disk_space_sufficient"] = False
                health["issues"].append(f"Low disk space: {free_space_gb:.2f}GB free")
            else:
                health["checks"]["disk_space_sufficient"] = True
            
            # Set overall status
            if health["issues"]:
                health["status"] = "degraded" if len(health["issues"]) <= 2 else "critical"
            
        except Exception as e:
            health["status"] = "critical"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health


class CloudArchivalStorage(ArchivalStorageBackend):
    """Cloud-based archival storage backend (AWS S3, Azure, GCP)"""
    
    def __init__(
        self,
        provider: str,
        region: str,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint_url: Optional[str] = None
    ):
        self.provider = provider.lower()
        self.region = region
        self.bucket_name = bucket_name
        self.logger = logging.getLogger("archival.storage.cloud")
        
        # Initialize cloud client
        if self.provider == "aws":
            self.client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url
            )
        else:
            raise ArchivalError(f"Unsupported cloud provider: {provider}")
        
        # Storage class mapping for AWS S3
        self.tier_mapping = {
            ArchivalTier.HOT: "STANDARD",
            ArchivalTier.WARM: "STANDARD_IA",
            ArchivalTier.COLD: "GLACIER",
            ArchivalTier.FROZEN: "DEEP_ARCHIVE",
            ArchivalTier.DEEP_FREEZE: "DEEP_ARCHIVE"
        }
    
    async def store_archive(
        self,
        archive_id: str,
        content_data: bytes,
        tier: ArchivalTier,
        metadata: Dict[str, Any]
    ) -> str:
        """Store archive in cloud storage"""



        
        try:
            storage_class = self.tier_mapping[tier]
            object_key = f"archives/{tier.value}/{archive_id}.archive"
            
            # Prepare metadata for cloud storage
            cloud_metadata = {
                "archive-id": archive_id,
                "tier": tier.value,
                "stored-at": datetime.utcnow().isoformat(),
                "content-type": metadata.get("content_type", "application/octet-stream"),
                "original-size": str(metadata.get("original_size", len(content_data))),
                "checksum": hashlib.sha256(content_data).hexdigest()
            }
            
            # Upload to cloud storage
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content_data,
                StorageClass=storage_class,
                Metadata=cloud_metadata,
                ServerSideEncryption='AES256'
            )
            
            # Store extended metadata separately
            metadata_key = f"metadata/{archive_id}.json"
            extended_metadata = {
                **metadata,
                "storage_backend": f"cloud_{self.provider}",
                "storage_path": f"s3://{self.bucket_name}/{object_key}",
                "storage_class": storage_class,
                "stored_at": datetime.utcnow().isoformat(),
                "checksum": cloud_metadata["checksum"]
            }
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=metadata_key,
                Body=json.dumps(extended_metadata, indent=2).encode('utf-8'),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            self.logger.info(f"Stored archive {archive_id} in cloud tier {tier.value}")
            return f"s3://{self.bucket_name}/{object_key}"
            
        except ClientError as e:
            self.logger.error(f"Failed to store archive {archive_id} in cloud: {e}")
            raise ArchivalError(f"Cloud storage operation failed: {e}")
    
    async def retrieve_archive(self, archive_id: str) -> Optional[bytes]:
        """Retrieve archive from cloud storage"""



        
        try:
            # Try to find archive across all tiers
            for tier in ArchivalTier:
                object_key = f"archives/{tier.value}/{archive_id}.archive"
                
                try:
                    response = self.client.get_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )
                    
                    content_data = response['Body'].read()
                    
                    # Verify checksum if available
                    if 'checksum' in response.get('Metadata', {}):
                        expected_checksum = response['Metadata']['checksum']
                        actual_checksum = hashlib.sha256(content_data).hexdigest()
                        
                        if actual_checksum != expected_checksum:
                            raise ArchivalError(f"Data integrity check failed for archive {archive_id}")
                    
                    self.logger.info(f"Retrieved archive {archive_id} from cloud tier {tier.value}")
                    return content_data
                    
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        raise
            
            self.logger.warning(f"Archive {archive_id} not found in cloud storage")
            return None
            
        except ClientError as e:
            self.logger.error(f"Failed to retrieve archive {archive_id} from cloud: {e}")
            return None
    
    async def delete_archive(self, archive_id: str) -> bool:
        """Delete archive from cloud storage"""



        
        try:
            deleted = False
            
            # Delete from all possible tiers
            for tier in ArchivalTier:
                object_key = f"archives/{tier.value}/{archive_id}.archive"
                
                try:
                    self.client.delete_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )
                    deleted = True
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        self.logger.warning(f"Error deleting {object_key}: {e}")
            
            # Delete metadata
            metadata_key = f"metadata/{archive_id}.json"
            try:
                self.client.delete_object(
                    Bucket=self.bucket_name,
                    Key=metadata_key
                )
                deleted = True
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    self.logger.warning(f"Error deleting metadata {metadata_key}: {e}")
            
            if deleted:
                self.logger.info(f"Deleted archive {archive_id} from cloud storage")
            
            return deleted
            
        except ClientError as e:
            self.logger.error(f"Failed to delete archive {archive_id} from cloud: {e}")
            return False
    
    async def migrate_archive(self, archive_id: str, target_tier: ArchivalTier) -> bool:
        """Migrate archive to different cloud storage tier"""



        
        try:
            # Find current location
            current_object_key = None
            current_tier = None
            
            for tier in ArchivalTier:
                object_key = f"archives/{tier.value}/{archive_id}.archive"
                
                try:
                    self.client.head_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )
                    current_object_key = object_key
                    current_tier = tier
                    break
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        raise
            
            if not current_object_key:
                self.logger.warning(f"Archive {archive_id} not found for migration")
                return False
            
            target_storage_class = self.tier_mapping[target_tier]
            target_object_key = f"archives/{target_tier.value}/{archive_id}.archive"
            
            # Copy to new location with new storage class
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': current_object_key
            }
            
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=target_object_key,
                StorageClass=target_storage_class,
                MetadataDirective='REPLACE',
                Metadata={
                    'tier': target_tier.value,
                    'migrated-at': datetime.utcnow().isoformat()
                },
                ServerSideEncryption='AES256'
            )
            
            # Delete from old location
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=current_object_key
            )
            
            self.logger.info(f"Migrated archive {archive_id} from {current_tier.value} to {target_tier.value}")
            return True
            
        except ClientError as e:
            self.logger.error(f"Failed to migrate archive {archive_id}: {e}")
            return False
    
    async def get_archive_metadata(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Get archive metadata from cloud storage"""



        
        try:
            metadata_key = f"metadata/{archive_id}.json"
            
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=metadata_key
            )
            
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchKey':
                self.logger.error(f"Failed to get metadata for archive {archive_id}: {e}")
            return None
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get cloud storage usage statistics"""



        
        try:
            stats = {
                "total_archives": 0,
                "total_size": 0,
                "tier_statistics": {},
                "provider": self.provider,
                "region": self.region
            }
            
            # List all archives and collect statistics
            paginator = self.client.get_paginator('list_objects_v2')
            
            for tier in ArchivalTier:
                tier_stats = {"archive_count": 0, "total_size": 0}
                prefix = f"archives/{tier.value}/"
                
                for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        if obj['Key'].endswith('.archive'):
                            tier_stats["archive_count"] += 1
                            tier_stats["total_size"] += obj['Size']
                
                stats["tier_statistics"][tier.value] = tier_stats
                stats["total_archives"] += tier_stats["archive_count"]
                stats["total_size"] += tier_stats["total_size"]
            
            return stats
            
        except ClientError as e:
            self.logger.error(f"Failed to get cloud storage statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform cloud storage health check"""
        
        health = {
            "status": "healthy",
            "checks": {},
            "issues": []
        }
        
        try:
            # Check bucket accessibility
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
                health["checks"]["bucket_accessible"] = True
            except ClientError as e:
                health["checks"]["bucket_accessible"] = False
                health["issues"].append(f"Bucket {self.bucket_name} not accessible: {e}")
            
            # Check write permissions
            try:
                test_key = f"health_check_{uuid.uuid4()}"
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=test_key,
                    Body=b"health check"
                )
                self.client.delete_object(
                    Bucket=self.bucket_name,
                    Key=test_key
                )
                health["checks"]["write_permission"] = True
            except ClientError as e:
                health["checks"]["write_permission"] = False
                health["issues"].append(f"No write permission: {e}")
            
            # Set overall status
            if health["issues"]:
                health["status"] = "degraded" if len(health["issues"]) <= 1 else "critical"
            
        except Exception as e:
            health["status"] = "critical"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health


class HierarchicalStorageManager:
    """
    Manages hierarchical storage across multiple backends
    with intelligent data placement and tier management
    """
    
    def __init__(self):
        self.backends: Dict[ArchivalTier, ArchivalStorageBackend] = {}
        self.logger = logging.getLogger("archival.storage.hsm")
        
        # Tier preferences for optimization
        self.tier_priorities = {
            ArchivalTier.HOT: 1,
            ArchivalTier.WARM: 2,
            ArchivalTier.COLD: 3,
            ArchivalTier.FROZEN: 4,
            ArchivalTier.DEEP_FREEZE: 5
        }
    
    def register_backend(self, tier: ArchivalTier, backend: ArchivalStorageBackend):
        """Register storage backend for specific tier"""
        self.backends[tier] = backend
        self.logger.info(f"Registered backend for tier {tier.value}")
    
    async def store_archive(
        self,
        archive_id: str,
        content_data: bytes,
        tier: ArchivalTier,
        metadata: Dict[str, Any]
    ) -> str:
        """Store archive using appropriate backend"""
        
        if tier not in self.backends:
            raise ArchivalError(f"No backend registered for tier {tier.value}")
        
        backend = self.backends[tier]
        return await backend.store_archive(archive_id, content_data, tier, metadata)
    
    async def retrieve_archive(self, archive_id: str) -> Optional[bytes]:
        """Retrieve archive from any available backend"""
        
        # Search across all backends in order of priority
        for tier in sorted(self.backends.keys(), key=lambda t: self.tier_priorities[t]):
            backend = self.backends[tier]
            content = await backend.retrieve_archive(archive_id)
            if content:
                return content
        
        return None
    
    async def find_archive_tier(self, archive_id: str) -> Optional[ArchivalTier]:
        """Find which tier contains the archive"""
        
        for tier, backend in self.backends.items():
            metadata = await backend.get_archive_metadata(archive_id)
            if metadata:
                return tier
        
        return None
    
    async def migrate_archive(self, archive_id: str, target_tier: ArchivalTier) -> bool:
        """Migrate archive between tiers/backends"""
        
        # Find current tier
        current_tier = await self.find_archive_tier(archive_id)
        if not current_tier:
            self.logger.warning(f"Archive {archive_id} not found for migration")
            return False
        
        if current_tier == target_tier:
            return True  # Already in target tier
        
        # Check if target backend exists
        if target_tier not in self.backends:
            raise ArchivalError(f"No backend registered for target tier {target_tier.value}")
        
        try:
            # Get content and metadata from current tier
            current_backend = self.backends[current_tier]
            content_data = await current_backend.retrieve_archive(archive_id)
            metadata = await current_backend.get_archive_metadata(archive_id)
            
            if not content_data or not metadata:
                return False
            
            # Store in target tier
            target_backend = self.backends[target_tier]
            await target_backend.store_archive(archive_id, content_data, target_tier, metadata)
            
            # Delete from current tier
            await current_backend.delete_archive(archive_id)
            
            self.logger.info(f"Migrated archive {archive_id} from {current_tier.value} to {target_tier.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate archive {archive_id}: {e}")
            return False
    
    async def get_consolidated_statistics(self) -> Dict[str, Any]:
        """Get consolidated statistics from all backends"""
        
        consolidated_stats = {
            "total_archives": 0,
            "total_size": 0,
            "backend_statistics": {},
            "tier_distribution": {}
        }
        
        for tier, backend in self.backends.items():
            stats = await backend.get_storage_statistics()
            consolidated_stats["backend_statistics"][tier.value] = stats
            
            if "total_archives" in stats:
                consolidated_stats["total_archives"] += stats["total_archives"]
            if "total_size" in stats:
                consolidated_stats["total_size"] += stats["total_size"]
        
        return consolidated_stats
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all backends"""
        
        overall_health = {
            "status": "healthy",
            "backend_health": {},
            "issues": []
        }
        
        for tier, backend in self.backends.items():
            health = await backend.health_check()
            overall_health["backend_health"][tier.value] = health
            
            if health.get("status") != "healthy":
                overall_health["issues"].extend(
                    [f"Tier {tier.value}: {issue}" for issue in health.get("issues", [])]
                )
        
        # Determine overall status
        unhealthy_backends = [
            tier for tier, health in overall_health["backend_health"].items()
            if health.get("status") != "healthy"
        ]
        
        if unhealthy_backends:
            if len(unhealthy_backends) >= len(self.backends) / 2:
                overall_health["status"] = "critical"
            else:
                overall_health["status"] = "degraded"
        
        return overall_health
