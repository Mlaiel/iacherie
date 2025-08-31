"""
 Artifact Manager - IA-Influencer-Agent CI/CD
================================================================
Expert: DEVOPS_ENGINEER + STORAGE_SPECIALIST
Created: 2025-08-24
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise artifact management system for multi-format content platform.
Handles storage, versioning, distribution, and lifecycle management of build artifacts.
================================================================
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
import hashlib
import json
import os
import shutil
import tarfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
from minio import Minio
import requests

logger = logging.getLogger(__name__)

class ArtifactType(Enum):
    """Artifact type enumeration"""
    DOCKER_IMAGE = "docker_image"
    AI_MODEL = "ai_model"
    CONTENT_FINGERPRINT = "content_fingerprint"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    TEST_REPORT = "test_report"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_PROFILE = "performance_profile"
    SOURCE_CODE = "source_code"
    DEPLOYMENT_PACKAGE = "deployment_package"

class StorageBackend(Enum):
    """Storage backend enumeration"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    MINIO = "minio"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"

@dataclass
class ArtifactMetadata:
    """Artifact metadata structure"""
    artifact_id: str
    name: str
    version: str
    artifact_type: ArtifactType
    file_path: str
    file_size: int
    checksum: str
    created_at: datetime
    build_id: str
    environment: str
    tags: List[str]
    retention_days: int = 90
    compressed: bool = False
    encrypted: bool = False
    signature: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ArtifactStorageConfig:
    """Artifact storage configuration"""
    backend: StorageBackend
    bucket_name: str
    region: str = "eu-central-1"
    endpoint_url: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    encryption_enabled: bool = True
    compression_enabled: bool = True
    retention_policy: Dict[str, int] = None
    
    def __post_init__(self):
        if self.retention_policy is None:
            self.retention_policy = {
                "development": 30,
                "staging": 60,
                "production": 365
            }

class ArtifactManager:
    """Enterprise artifact management system"""
    
    def __init__(self, storage_config: ArtifactStorageConfig):
        """Initialize artifact manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.storage_config = storage_config
        self.storage_client = None
        self.local_cache_dir = Path("/tmp/ia_influencer_artifacts")
        self.metadata_store: Dict[str, ArtifactMetadata] = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize artifact manager"""



        try:
            # Initialize storage backend
            await self._initialize_storage_backend()
            
            # Create local cache directory
            self.local_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing metadata
            await self._load_metadata()
            
            self.initialized = True
            self.logger.info(" Artifact manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f" Failed to initialize artifact manager: {e}")
            return False
    
    async def _initialize_storage_backend(self) -> None:
        """Initialize storage backend client"""
        if self.storage_config.backend == StorageBackend.AWS_S3:
            self.storage_client = boto3.client(
                's3',
                region_name=self.storage_config.region,
                aws_access_key_id=self.storage_config.access_key,
                aws_secret_access_key=self.storage_config.secret_key
            )
        elif self.storage_config.backend == StorageBackend.MINIO:
            self.storage_client = Minio(
                self.storage_config.endpoint_url.replace('http://', '').replace('https://', ''),
                access_key=self.storage_config.access_key,
                secret_key=self.storage_config.secret_key,
                secure=self.storage_config.endpoint_url.startswith('https')
            )
        elif self.storage_config.backend == StorageBackend.LOCAL:
            local_storage_path = Path(self.storage_config.bucket_name)
            local_storage_path.mkdir(parents=True, exist_ok=True)
            
        self.logger.info(f"Storage backend initialized: {self.storage_config.backend.value}")
    
    async def store_artifact(
        self,
        file_path: str,
        artifact_type: ArtifactType,
        build_id: str,
        environment: str,
        name: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Store artifact with metadata"""



        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Artifact file not found: {file_path}")
            
            # Generate artifact metadata
            artifact_id = self._generate_artifact_id(file_path, build_id)
            file_size = os.path.getsize(file_path)
            checksum = await self._calculate_checksum(file_path)
            
            # Prepare artifact for storage
            processed_file_path = file_path
            compressed = False
            encrypted = False
            
            # Apply compression if enabled
            if self.storage_config.compression_enabled:
                processed_file_path = await self._compress_artifact(file_path)
                compressed = True
            
            # Apply encryption if enabled
            if self.storage_config.encryption_enabled:
                processed_file_path = await self._encrypt_artifact(processed_file_path)
                encrypted = True
            
            # Upload to storage backend
            storage_path = await self._upload_to_storage(processed_file_path, artifact_id)
            
            # Create metadata
            metadata = ArtifactMetadata(
                artifact_id=artifact_id,
                name=name or os.path.basename(file_path),
                version=version or "1.0.0",
                artifact_type=artifact_type,
                file_path=storage_path,
                file_size=file_size,
                checksum=checksum,
                created_at=datetime.now(),
                build_id=build_id,
                environment=environment,
                tags=tags or [],
                compressed=compressed,
                encrypted=encrypted,
                retention_days=self.storage_config.retention_policy.get(environment, 90)
            )
            
            # Store metadata
            self.metadata_store[artifact_id] = metadata
            await self._save_metadata()
            
            # Clean up temporary files
            if processed_file_path != file_path:
                os.unlink(processed_file_path)
            
            self.logger.info(f"Artifact stored successfully: {artifact_id}")
            return artifact_id
            
        except Exception as e:
            self.logger.error(f"Failed to store artifact: {e}")
            raise
    
    async def retrieve_artifact(
        self,
        artifact_id: str,
        local_path: Optional[str] = None
    ) -> str:
        """Retrieve artifact from storage"""



        try:
            if artifact_id not in self.metadata_store:
                raise ValueError(f"Artifact not found: {artifact_id}")
            
            metadata = self.metadata_store[artifact_id]
            
            # Determine local path
            if local_path is None:
                local_path = self.local_cache_dir / f"{artifact_id}_{metadata.name}"
            
            # Download from storage
            await self._download_from_storage(metadata.file_path, str(local_path))
            
            # Decrypt if necessary
            if metadata.encrypted:
                local_path = await self._decrypt_artifact(str(local_path))
            
            # Decompress if necessary
            if metadata.compressed:
                local_path = await self._decompress_artifact(str(local_path))
            
            # Verify checksum
            downloaded_checksum = await self._calculate_checksum(local_path)
            if downloaded_checksum != metadata.checksum:
                raise ValueError("Artifact checksum verification failed")
            
            self.logger.info(f"Artifact retrieved successfully: {artifact_id}")
            return str(local_path)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve artifact: {e}")
            raise
    
    async def list_artifacts(
        self,
        artifact_type: Optional[ArtifactType] = None,
        environment: Optional[str] = None,
        build_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ArtifactMetadata]:
        """List artifacts with optional filtering"""
        artifacts = list(self.metadata_store.values())
        
        # Apply filters
        if artifact_type:
            artifacts = [a for a in artifacts if a.artifact_type == artifact_type]
        
        if environment:
            artifacts = [a for a in artifacts if a.environment == environment]
        
        if build_id:
            artifacts = [a for a in artifacts if a.build_id == build_id]
        
        if tags:
            artifacts = [a for a in artifacts if any(tag in a.tags for tag in tags)]
        
        # Sort by creation date (newest first)
        artifacts.sort(key=lambda x: x.created_at, reverse=True)
        
        return artifacts
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Delete artifact and its metadata"""



        try:
            if artifact_id not in self.metadata_store:
                return False
            
            metadata = self.metadata_store[artifact_id]
            
            # Delete from storage backend
            await self._delete_from_storage(metadata.file_path)
            
            # Remove metadata
            del self.metadata_store[artifact_id]
            await self._save_metadata()
            
            self.logger.info(f"Artifact deleted: {artifact_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete artifact: {e}")
            return False
    
    async def cleanup_expired_artifacts(self) -> int:
        """Clean up expired artifacts based on retention policy"""
        cleaned_count = 0
        current_time = datetime.now()
        
        expired_artifacts = []
        for artifact_id, metadata in self.metadata_store.items():
            expiry_date = metadata.created_at + timedelta(days=metadata.retention_days)
            if current_time > expiry_date:
                expired_artifacts.append(artifact_id)
        
        for artifact_id in expired_artifacts:
            if await self.delete_artifact(artifact_id):
                cleaned_count += 1
        
        self.logger.info(f"Cleaned up {cleaned_count} expired artifacts")
        return cleaned_count
    
    async def get_artifact_metadata(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Get artifact metadata"""



        return self.metadata_store.get(artifact_id)
    
    async def update_artifact_tags(self, artifact_id: str, tags: List[str]) -> bool:
        """Update artifact tags"""



        try:
            if artifact_id not in self.metadata_store:
                return False
            
            self.metadata_store[artifact_id].tags = tags
            await self._save_metadata()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update artifact tags: {e}")
            return False
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        total_size = sum(metadata.file_size for metadata in self.metadata_store.values())
        
        stats_by_type = {}
        stats_by_env = {}
        
        for metadata in self.metadata_store.values():
            # By type
            type_name = metadata.artifact_type.value
            if type_name not in stats_by_type:
                stats_by_type[type_name] = {"count": 0, "size": 0}
            stats_by_type[type_name]["count"] += 1
            stats_by_type[type_name]["size"] += metadata.file_size
            
            # By environment
            env_name = metadata.environment
            if env_name not in stats_by_env:
                stats_by_env[env_name] = {"count": 0, "size": 0}
            stats_by_env[env_name]["count"] += 1
            stats_by_env[env_name]["size"] += metadata.file_size
        
        return {
            "total_artifacts": len(self.metadata_store),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": stats_by_type,
            "by_environment": stats_by_env,
            "storage_backend": self.storage_config.backend.value
        }
    
    def _generate_artifact_id(self, file_path: str, build_id: str) -> str:
        """Generate unique artifact ID"""
        content = f"{file_path}_{build_id}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _compress_artifact(self, file_path: str) -> str:
        """Compress artifact file"""
        compressed_path = f"{file_path}.tar.gz"
        with tarfile.open(compressed_path, "w:gz") as tar:
            tar.add(file_path, arcname=os.path.basename(file_path))
        return compressed_path
    
    async def _decompress_artifact(self, compressed_path: str) -> str:
        """Decompress artifact file"""
        extract_dir = os.path.dirname(compressed_path)
        with tarfile.open(compressed_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        
        # Return path to extracted file
        extracted_files = tar.getnames()
        if extracted_files:
            return os.path.join(extract_dir, extracted_files[0])
        return compressed_path
    
    async def _encrypt_artifact(self, file_path: str) -> str:
        """Encrypt artifact file (placeholder implementation)"""
        # In production, implement proper encryption
        encrypted_path = f"{file_path}.enc"
        shutil.copy2(file_path, encrypted_path)
        return encrypted_path
    
    async def _decrypt_artifact(self, encrypted_path: str) -> str:
        """Decrypt artifact file (placeholder implementation)"""
        # In production, implement proper decryption
        decrypted_path = encrypted_path.replace('.enc', '')
        shutil.copy2(encrypted_path, decrypted_path)
        return decrypted_path
    
    async def _upload_to_storage(self, file_path: str, artifact_id: str) -> str:
        """Upload file to storage backend"""
        if self.storage_config.backend == StorageBackend.LOCAL:
            storage_path = Path(self.storage_config.bucket_name) / artifact_id
            shutil.copy2(file_path, storage_path)
            return str(storage_path)
        
        elif self.storage_config.backend == StorageBackend.AWS_S3:
            object_key = f"artifacts/{artifact_id}"
            self.storage_client.upload_file(
                file_path,
                self.storage_config.bucket_name,
                object_key
            )
            return object_key
        
        elif self.storage_config.backend == StorageBackend.MINIO:
            object_key = f"artifacts/{artifact_id}"
            self.storage_client.fput_object(
                self.storage_config.bucket_name,
                object_key,
                file_path
            )
            return object_key
        
        return file_path
    
    async def _download_from_storage(self, storage_path: str, local_path: str) -> None:
        """Download file from storage backend"""
        if self.storage_config.backend == StorageBackend.LOCAL:
            shutil.copy2(storage_path, local_path)
        
        elif self.storage_config.backend == StorageBackend.AWS_S3:
            self.storage_client.download_file(
                self.storage_config.bucket_name,
                storage_path,
                local_path
            )
        
        elif self.storage_config.backend == StorageBackend.MINIO:
            self.storage_client.fget_object(
                self.storage_config.bucket_name,
                storage_path,
                local_path
            )
    
    async def _delete_from_storage(self, storage_path: str) -> None:
        """Delete file from storage backend"""
        if self.storage_config.backend == StorageBackend.LOCAL:
            if os.path.exists(storage_path):
                os.unlink(storage_path)
        
        elif self.storage_config.backend == StorageBackend.AWS_S3:
            self.storage_client.delete_object(
                Bucket=self.storage_config.bucket_name,
                Key=storage_path
            )
        
        elif self.storage_config.backend == StorageBackend.MINIO:
            self.storage_client.remove_object(
                self.storage_config.bucket_name,
                storage_path
            )
    
    async def _load_metadata(self) -> None:
        """Load artifact metadata from storage"""
        metadata_file = self.local_cache_dir / "artifacts_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata_dict = json.load(f)
                
                for artifact_id, metadata_data in metadata_dict.items():
                    # Convert datetime string back to datetime object
                    metadata_data['created_at'] = datetime.fromisoformat(metadata_data['created_at'])
                    metadata_data['artifact_type'] = ArtifactType(metadata_data['artifact_type'])
                    
                    self.metadata_store[artifact_id] = ArtifactMetadata(**metadata_data)
                    
            except Exception as e:
                self.logger.error(f"Failed to load metadata: {e}")
    
    async def _save_metadata(self) -> None:
        """Save artifact metadata to storage"""
        metadata_file = self.local_cache_dir / "artifacts_metadata.json"
        try:
            metadata_dict = {}
            for artifact_id, metadata in self.metadata_store.items():
                metadata_data = asdict(metadata)
                metadata_data['created_at'] = metadata.created_at.isoformat()
                metadata_data['artifact_type'] = metadata.artifact_type.value
                metadata_dict[artifact_id] = metadata_data
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_dict, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")

class ArtifactVersionManager:
    """Manage artifact versioning and releases"""
    
    def __init__(self, artifact_manager: ArtifactManager):
        self.artifact_manager = artifact_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.version_registry: Dict[str, List[str]] = {}
    
    async def create_version(
        self,
        artifact_name: str,
        file_path: str,
        version: str,
        artifact_type: ArtifactType,
        build_id: str,
        environment: str,
        changelog: Optional[str] = None
    ) -> str:
        """Create new version of artifact"""



        try:
            # Store artifact with version
            artifact_id = await self.artifact_manager.store_artifact(
                file_path=file_path,
                artifact_type=artifact_type,
                build_id=build_id,
                environment=environment,
                name=artifact_name,
                version=version,
                tags=[f"version:{version}"]
            )
            
            # Register version
            if artifact_name not in self.version_registry:
                self.version_registry[artifact_name] = []
            
            self.version_registry[artifact_name].append(artifact_id)
            
            # Store changelog if provided
            if changelog:
                await self._store_changelog(artifact_name, version, changelog)
            
            self.logger.info(f"Version {version} created for {artifact_name}")
            return artifact_id
            
        except Exception as e:
            self.logger.error(f"Failed to create version: {e}")
            raise
    
    async def get_versions(self, artifact_name: str) -> List[Dict[str, Any]]:
        """Get all versions of an artifact"""
        if artifact_name not in self.version_registry:
            return []
        
        versions = []
        for artifact_id in self.version_registry[artifact_name]:
            metadata = await self.artifact_manager.get_artifact_metadata(artifact_id)
            if metadata:
                versions.append({
                    "artifact_id": artifact_id,
                    "version": metadata.version,
                    "created_at": metadata.created_at.isoformat(),
                    "environment": metadata.environment,
                    "size": metadata.file_size
                })
        
        # Sort by version (newest first)
        versions.sort(key=lambda x: x["created_at"], reverse=True)
        return versions
    
    async def get_latest_version(self, artifact_name: str, environment: str) -> Optional[str]:
        """Get latest version artifact ID for environment"""
        versions = await self.get_versions(artifact_name)
        
        # Filter by environment and get latest
        env_versions = [v for v in versions if v["environment"] == environment]
        if env_versions:
            return env_versions[0]["artifact_id"]
        
        return None
    
    async def promote_version(
        self,
        artifact_id: str,
        target_environment: str
    ) -> str:
        """Promote artifact version to target environment"""



        try:
            # Get current artifact metadata
            metadata = await self.artifact_manager.get_artifact_metadata(artifact_id)
            if not metadata:
                raise ValueError(f"Artifact not found: {artifact_id}")
            
            # Retrieve artifact
            local_path = await self.artifact_manager.retrieve_artifact(artifact_id)
            
            # Store in target environment
            new_artifact_id = await self.artifact_manager.store_artifact(
                file_path=local_path,
                artifact_type=metadata.artifact_type,
                build_id=metadata.build_id,
                environment=target_environment,
                name=metadata.name,
                version=metadata.version,
                tags=metadata.tags + [f"promoted_from:{metadata.environment}"]
            )
            
            self.logger.info(f"Artifact promoted from {metadata.environment} to {target_environment}")
            return new_artifact_id
            
        except Exception as e:
            self.logger.error(f"Failed to promote version: {e}")
            raise
    
    async def _store_changelog(self, artifact_name: str, version: str, changelog: str) -> None:
        """Store changelog for version"""
        changelog_data = {
            "artifact_name": artifact_name,
            "version": version,
            "changelog": changelog,
            "timestamp": datetime.now().isoformat()
        }
        
        changelog_file = self.artifact_manager.local_cache_dir / f"changelog_{artifact_name}_{version}.json"
        with open(changelog_file, 'w') as f:
            json.dump(changelog_data, f, indent=2)

# Default storage configuration
default_storage_config = ArtifactStorageConfig(
    backend=StorageBackend.LOCAL,
    bucket_name="/tmp/ia_influencer_artifacts_storage"
)

# Global instance
artifact_manager = ArtifactManager(default_storage_config)
version_manager = ArtifactVersionManager(artifact_manager)
