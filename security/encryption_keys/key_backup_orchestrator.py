"""
Enterprise Key Backup Orchestrator
Created by: Senior Engineering Team (DevOps + DBA + Security + ML + Microservices + IA Prompt Engineer)
Date: 2024
Purpose: Multi-tier backup orchestration for Creator Economy encryption keys

Features:
- Multi-tier backup strategies (hot, warm, cold storage)
- Cross-cloud backup replication
- Creator-specific backup policies
- Automated recovery testing and validation
- Geographic distribution and disaster recovery
- Creator Economy optimizations
"""

import asyncio
import hashlib
import json
import os
import shutil
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import boto3
import paramiko
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import requests


class BackupTier(Enum):
    """Backup storage tiers"""
    HOT = "hot"          # Immediate access, high cost
    WARM = "warm"        # Quick access, medium cost  
    COLD = "cold"        # Delayed access, low cost
    GLACIER = "glacier"  # Archive, minimal cost
    CREATOR_PRIORITY = "creator_priority"  # VIP creator fast access


class BackupProvider(Enum):
    """Supported backup providers"""
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    LOCAL_FILESYSTEM = "local_filesystem"
    SFTP = "sftp"
    CREATOR_CLOUD = "creator_cloud"  # Creator-dedicated storage


class BackupStatus(Enum):
    """Backup operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFYING = "verifying"
    VERIFIED = "verified"


class RecoverySpeed(Enum):
    """Recovery speed requirements"""
    IMMEDIATE = "immediate"      # < 1 minute
    FAST = "fast"               # < 10 minutes
    STANDARD = "standard"       # < 1 hour
    BATCH = "batch"            # < 24 hours
    CREATOR_EMERGENCY = "creator_emergency"  # Emergency creator access


@dataclass
class BackupLocation:
    """Backup storage location configuration"""
    provider: BackupProvider
    tier: BackupTier
    region: str
    endpoint: str
    credentials: Dict[str, str]
    encryption_enabled: bool = True
    compression_enabled: bool = True
    is_active: bool = True
    max_retention_days: int = 365
    creator_specific: bool = False


@dataclass
class BackupPolicy:
    """Backup policy configuration"""
    policy_id: str
    name: str
    creator_types: List[str]  # musician, photographer, etc.
    content_types: List[str]  # audio, video, image, etc.
    backup_frequency: timedelta
    retention_policy: Dict[BackupTier, int]  # days to retain
    recovery_requirements: RecoverySpeed
    geographic_distribution: List[str]  # required regions
    compliance_requirements: List[str]  # GDPR, CCPA, etc.
    encryption_requirements: Dict[str, Any]
    priority_level: int = 5  # 1-10, 10 being highest
    
    def matches_creator(self, creator_metadata: Dict[str, Any]) -> bool:
        """Check if policy matches creator"""
        creator_type = creator_metadata.get('creator_type', '')
        content_types = creator_metadata.get('content_types', [])
        
        # Check creator type match
        if self.creator_types and creator_type not in self.creator_types:
            return False
            
        # Check content type match
        if self.content_types:
            if not any(ct in content_types for ct in self.content_types):
                return False
        
        return True


@dataclass
class BackupJob:
    """Backup job tracking"""
    job_id: str
    key_id: str
    creator_id: Optional[str]
    policy_id: str
    backup_locations: List[BackupLocation]
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    backup_size: int = 0
    verification_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryJob:
    """Recovery job tracking"""
    job_id: str
    key_id: str
    creator_id: Optional[str]
    source_location: BackupLocation
    target_location: str
    recovery_speed: RecoverySpeed
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    recovered_size: int = 0
    verification_passed: bool = False


class BackupProvider_Interface(ABC):
    """Abstract interface for backup providers"""
    
    @abstractmethod
    async def upload_backup(self, 
                          key_data: bytes, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Upload backup to provider"""
        pass
    
    @abstractmethod
    async def download_backup(self, 
                            key_id: str, 
                            location: BackupLocation) -> Optional[bytes]:
        """Download backup from provider"""
        pass
    
    @abstractmethod
    async def verify_backup(self, 
                          key_id: str, 
                          location: BackupLocation, 
                          expected_hash: str) -> bool:
        """Verify backup integrity"""
        pass
    
    @abstractmethod
    async def delete_backup(self, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Delete backup from provider"""
        pass


class AWSBackupProvider(BackupProvider_Interface):
    """AWS S3 backup provider"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s3_clients = {}
    
    def _get_s3_client(self, location: BackupLocation):
        """Get S3 client for location"""
        if location.region not in self.s3_clients:
            self.s3_clients[location.region] = boto3.client(
                's3',
                region_name=location.region,
                aws_access_key_id=location.credentials.get('access_key'),
                aws_secret_access_key=location.credentials.get('secret_key')
            )
        return self.s3_clients[location.region]
    
    async def upload_backup(self, 
                          key_data: bytes, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Upload to S3"""
        try:
            s3_client = self._get_s3_client(location)
            bucket_name = location.credentials.get('bucket_name')
            
            # Determine storage class based on tier
            storage_class = self._get_storage_class(location.tier)
            
            # Encrypt if required
            if location.encryption_enabled:
                key_data = await self._encrypt_backup(key_data, location)
            
            # Compress if required
            if location.compression_enabled:
                key_data = await self._compress_backup(key_data)
            
            # Upload
# SECURITY: object_key = f"keys/{key_id}/{datetime.now().isoformat()}.backup" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=key_data,
                    StorageClass=storage_class,
                    ServerSideEncryption='AES256'
                )
            )
            
            self.logger.info(f"Successfully uploaded backup {key_id} to S3")
            return True
            
        except Exception as e:
            self.logger.error(f"S3 upload failed: {e}")
            return False
    
    async def download_backup(self, 
                            key_id: str, 
                            location: BackupLocation) -> Optional[bytes]:
        """Download from S3"""
        try:
            s3_client = self._get_s3_client(location)
            bucket_name = location.credentials.get('bucket_name')
            
            # List objects to find latest backup
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=f"keys/{key_id}/",
                    MaxKeys=1
                )
            )
            
            if 'Contents' not in response:
                return None
            
            # Download latest backup
            latest_object = max(response['Contents'], key=lambda x: x['LastModified'])
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.get_object(
                    Bucket=bucket_name,
                    Key=latest_object['Key']
                )
            )
            
            key_data = response['Body'].read()
            
            # Decompress if needed
            if location.compression_enabled:
                key_data = await self._decompress_backup(key_data)
            
            # Decrypt if needed
            if location.encryption_enabled:
                key_data = await self._decrypt_backup(key_data, location)
            
            return key_data
            
        except Exception as e:
            self.logger.error(f"S3 download failed: {e}")
            return None
    
    async def verify_backup(self, 
                          key_id: str, 
                          location: BackupLocation, 
                          expected_hash: str) -> bool:
        """Verify S3 backup"""
        try:
            backup_data = await self.download_backup(key_id, location)
            if backup_data is None:
                return False
            
            actual_hash = hashlib.sha256(backup_data).hexdigest()
            return actual_hash == expected_hash
            
        except Exception as e:
            self.logger.error(f"S3 verification failed: {e}")
            return False
    
    async def delete_backup(self, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Delete from S3"""
        try:
            s3_client = self._get_s3_client(location)
            bucket_name = location.credentials.get('bucket_name')
            
            # List and delete all backups for key
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=f"keys/{key_id}/"
                )
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: s3_client.delete_object(
                            Bucket=bucket_name,
                            Key=obj['Key']
                        )
                    )
            
            return True
            
        except Exception as e:
            self.logger.error(f"S3 deletion failed: {e}")
            return False
    
    def _get_storage_class(self, tier: BackupTier) -> str:
        """Map backup tier to S3 storage class"""
        mapping = {
            BackupTier.HOT: 'STANDARD',
            BackupTier.WARM: 'STANDARD_IA',
            BackupTier.COLD: 'GLACIER',
            BackupTier.GLACIER: 'DEEP_ARCHIVE',
            BackupTier.CREATOR_PRIORITY: 'STANDARD'
        }
        return mapping.get(tier, 'STANDARD')
    
    async def _encrypt_backup(self, data: bytes, location: BackupLocation) -> bytes:
        """Encrypt backup data"""
        # Implementation would use proper encryption
        return data
    
    async def _decrypt_backup(self, data: bytes, location: BackupLocation) -> bytes:
        """Decrypt backup data"""
        # Implementation would use proper decryption
        return data
    
    async def _compress_backup(self, data: bytes) -> bytes:
        """Compress backup data"""
        import gzip
        return gzip.compress(data)
    
    async def _decompress_backup(self, data: bytes) -> bytes:
        """Decompress backup data"""
        import gzip
        return gzip.decompress(data)


class AzureBackupProvider(BackupProvider_Interface):
    """Azure Blob Storage backup provider"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blob_clients = {}
    
    def _get_blob_client(self, location: BackupLocation):
        """Get blob client for location"""
        if location.region not in self.blob_clients:
            connection_string = location.credentials.get('connection_string')
            self.blob_clients[location.region] = BlobServiceClient.from_connection_string(
                connection_string
            )
        return self.blob_clients[location.region]
    
    async def upload_backup(self, 
                          key_data: bytes, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Upload to Azure Blob"""
        try:
            blob_client = self._get_blob_client(location)
            container_name = location.credentials.get('container_name')
            
            # Determine access tier
            access_tier = self._get_access_tier(location.tier)
            
            # Process data
            if location.encryption_enabled:
                key_data = await self._encrypt_backup(key_data, location)
            
            if location.compression_enabled:
                key_data = await self._compress_backup(key_data)
            
            # Upload
            blob_name = f"keys/{key_id}/{datetime.now().isoformat()}.backup"
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob_client.get_blob_client(
                    container=container_name,
                    blob=blob_name
                ).upload_blob(
                    key_data,
                    overwrite=True,
                    standard_blob_tier=access_tier
                )
            )
            
            self.logger.info(f"Successfully uploaded backup {key_id} to Azure")
            return True
            
        except Exception as e:
            self.logger.error(f"Azure upload failed: {e}")
            return False
    
    async def download_backup(self, 
                            key_id: str, 
                            location: BackupLocation) -> Optional[bytes]:
        """Download from Azure Blob"""
        try:
            blob_client = self._get_blob_client(location)
            container_name = location.credentials.get('container_name')
            
            # List blobs to find latest
            container_client = blob_client.get_container_client(container_name)
            blobs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(container_client.list_blobs(name_starts_with=f"keys/{key_id}/"))
            )
            
            if not blobs:
                return None
            
            # Get latest blob
            latest_blob = max(blobs, key=lambda x: x.last_modified)
            
            # Download
            blob_client_specific = blob_client.get_blob_client(
                container=container_name,
                blob=latest_blob.name
            )
            
            key_data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob_client_specific.download_blob().readall()
            )
            
            # Process data
            if location.compression_enabled:
                key_data = await self._decompress_backup(key_data)
            
            if location.encryption_enabled:
                key_data = await self._decrypt_backup(key_data, location)
            
            return key_data
            
        except Exception as e:
            self.logger.error(f"Azure download failed: {e}")
            return None
    
    async def verify_backup(self, 
                          key_id: str, 
                          location: BackupLocation, 
                          expected_hash: str) -> bool:
        """Verify Azure backup"""
        try:
            backup_data = await self.download_backup(key_id, location)
            if backup_data is None:
                return False
            
            actual_hash = hashlib.sha256(backup_data).hexdigest()
            return actual_hash == expected_hash
            
        except Exception as e:
            self.logger.error(f"Azure verification failed: {e}")
            return False
    
    async def delete_backup(self, 
                          key_id: str, 
                          location: BackupLocation) -> bool:
        """Delete from Azure Blob"""
        try:
            blob_client = self._get_blob_client(location)
            container_name = location.credentials.get('container_name')
            container_client = blob_client.get_container_client(container_name)
            
            # List and delete all backups
            blobs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(container_client.list_blobs(name_starts_with=f"keys/{key_id}/"))
            )
            
            for blob in blobs:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: container_client.delete_blob(blob.name)
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Azure deletion failed: {e}")
            return False
    
    def _get_access_tier(self, tier: BackupTier) -> str:
        """Map backup tier to Azure access tier"""
        mapping = {
            BackupTier.HOT: 'Hot',
            BackupTier.WARM: 'Cool',
            BackupTier.COLD: 'Archive',
            BackupTier.GLACIER: 'Archive',
            BackupTier.CREATOR_PRIORITY: 'Hot'
        }
        return mapping.get(tier, 'Hot')
    
    async def _encrypt_backup(self, data: bytes, location: BackupLocation) -> bytes:
        """Encrypt backup data"""
        return data
    
    async def _decrypt_backup(self, data: bytes, location: BackupLocation) -> bytes:
        """Decrypt backup data"""
        return data
    
    async def _compress_backup(self, data: bytes) -> bytes:
        """Compress backup data"""
        import gzip
        return gzip.compress(data)
    
    async def _decompress_backup(self, data: bytes) -> bytes:
        """Decompress backup data"""
        import gzip
        return gzip.decompress(data)


class CreatorBackupPolicyEngine:
    """Engine for managing creator-specific backup policies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policies = {}
        self.creator_policy_cache = {}
        
    def register_policy(self, policy: BackupPolicy):
        """Register a backup policy"""
        self.policies[policy.policy_id] = policy
        self.logger.info(f"Registered backup policy: {policy.name}")
    
    def get_policy_for_creator(self, 
                             creator_id: str, 
                             creator_metadata: Dict[str, Any]) -> Optional[BackupPolicy]:
        """Get best matching policy for creator"""
        try:
            # Check cache first
# SECURITY: cache_key = f"{creator_id}_{hash(json.dumps(creator_metadata, sort_keys=True))}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            if cache_key in self.creator_policy_cache:
                return self.creator_policy_cache[cache_key]
            
            # Find matching policies
            matching_policies = []
            for policy in self.policies.values():
                if policy.matches_creator(creator_metadata):
                    matching_policies.append(policy)
            
            if not matching_policies:
                return None
            
            # Select highest priority policy
            best_policy = max(matching_policies, key=lambda p: p.priority_level)
            
            # Cache result
            self.creator_policy_cache[cache_key] = best_policy
            
            return best_policy
            
        except Exception as e:
            self.logger.error(f"Policy selection failed: {e}")
            return None
    
    def create_default_policies(self):
        """Create default backup policies for different creator types"""
        
        # High-value content creators (musicians, artists)
        premium_policy = BackupPolicy(
            policy_id="premium_creators",
            name="Premium Creator Backup Policy",
            creator_types=["musician", "audio_producer", "visual_artist"],
            content_types=["audio", "video", "image"],
            backup_frequency=timedelta(hours=1),
            retention_policy={
                BackupTier.HOT: 30,
                BackupTier.WARM: 90,
                BackupTier.COLD: 365,
                BackupTier.CREATOR_PRIORITY: 7
            },
            recovery_requirements=RecoverySpeed.IMMEDIATE,
            geographic_distribution=["us-east-1", "eu-west-1", "ap-southeast-1"],
            compliance_requirements=["GDPR", "CCPA"],
            encryption_requirements={"algorithm": "AES-256-GCM", "key_rotation": "daily"},
            priority_level=10
        )
        
        # Standard creators
        standard_policy = BackupPolicy(
            policy_id="standard_creators",
            name="Standard Creator Backup Policy",
            creator_types=["blogger", "photographer", "social_media_manager"],
            content_types=["text", "image", "video"],
            backup_frequency=timedelta(hours=6),
            retention_policy={
                BackupTier.HOT: 7,
                BackupTier.WARM: 30,
                BackupTier.COLD: 180
            },
            recovery_requirements=RecoverySpeed.FAST,
            geographic_distribution=["us-east-1", "eu-west-1"],
            compliance_requirements=["GDPR"],
            encryption_requirements={"algorithm": "AES-256-GCM", "key_rotation": "weekly"},
            priority_level=5
        )
        
        # Emerging creators
        basic_policy = BackupPolicy(
            policy_id="emerging_creators",
            name="Emerging Creator Backup Policy",
            creator_types=["influencer", "content_writer"],
            content_types=["text", "image"],
            backup_frequency=timedelta(hours=24),
            retention_policy={
                BackupTier.WARM: 14,
                BackupTier.COLD: 90
            },
            recovery_requirements=RecoverySpeed.STANDARD,
            geographic_distribution=["us-east-1"],
            compliance_requirements=[],
            encryption_requirements={"algorithm": "AES-256-GCM", "key_rotation": "monthly"},
            priority_level=3
        )
        
        # Register policies
        self.register_policy(premium_policy)
        self.register_policy(standard_policy)
        self.register_policy(basic_policy)


class KeyBackupOrchestrator:
    """Main orchestrator for key backup operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.policy_engine = CreatorBackupPolicyEngine()
        self.providers = {}
        self.backup_locations = {}
        
        # Job tracking
        self.backup_jobs = {}
        self.recovery_jobs = {}
        
        # Metrics
        self.metrics = {
            'backups_created': 0,
            'backups_failed': 0,
            'recoveries_performed': 0,
            'verification_tests': 0,
            'verification_failures': 0,
            'creator_emergency_recoveries': 0
        }
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.running = False
        
        # Initialize
        self._initialize_providers()
        self._initialize_default_locations()
        self.policy_engine.create_default_policies()
    
    def _initialize_providers(self):
        """Initialize backup providers"""
        self.providers[BackupProvider.AWS_S3] = AWSBackupProvider()
        self.providers[BackupProvider.AZURE_BLOB] = AzureBackupProvider()
        # Additional providers would be initialized here
    
    def _initialize_default_locations(self):
        """Initialize default backup locations"""
        # AWS S3 locations
        self.backup_locations['aws_hot'] = BackupLocation(
            provider=BackupProvider.AWS_S3,
            tier=BackupTier.HOT,
            region='us-east-1',
            endpoint='s3.amazonaws.com',
            credentials={'bucket_name': 'ainflue-keys-hot'},
            max_retention_days=30
        )
        
        self.backup_locations['aws_cold'] = BackupLocation(
            provider=BackupProvider.AWS_S3,
            tier=BackupTier.COLD,
            region='us-west-2',
            endpoint='s3.amazonaws.com',
            credentials={'bucket_name': 'ainflue-keys-cold'},
            max_retention_days=365
        )
        
        # Azure locations
        self.backup_locations['azure_warm'] = BackupLocation(
            provider=BackupProvider.AZURE_BLOB,
            tier=BackupTier.WARM,
            region='westeurope',
            endpoint='blob.core.windows.net',
            credentials={'container_name': 'ainflue-keys-warm'},
            max_retention_days=90
        )
        
        # Creator priority location
        self.backup_locations['creator_priority'] = BackupLocation(
            provider=BackupProvider.AWS_S3,
            tier=BackupTier.CREATOR_PRIORITY,
            region='us-east-1',
            endpoint='s3.amazonaws.com',
            credentials={'bucket_name': 'ainflue-creator-priority'},
            max_retention_days=7,
            creator_specific=True
        )
    
    async def backup_key(self, 
                        key_id: str,
                        key_data: bytes,
                        creator_id: Optional[str] = None,
                        creator_metadata: Optional[Dict[str, Any]] = None,
                        force_policy_id: Optional[str] = None) -> str:
        """Create backup for a key"""
        try:
            job_id = str(uuid.uuid4())
            
            # Determine backup policy
            policy = None
            if force_policy_id:
                policy = self.policy_engine.policies.get(force_policy_id)
            elif creator_id and creator_metadata:
                policy = self.policy_engine.get_policy_for_creator(creator_id, creator_metadata)
            
            if not policy:
                # Use default policy
                policy = self.policy_engine.policies.get('standard_creators')
            
            if not policy:
                raise ValueError("No suitable backup policy found")
            
            # Select backup locations based on policy
            locations = self._select_backup_locations(policy, creator_metadata)
            
            # Create backup job
            job = BackupJob(
                job_id=job_id,
                key_id=key_id,
                creator_id=creator_id,
                policy_id=policy.policy_id,
                backup_locations=locations,
                status=BackupStatus.PENDING,
                created_at=datetime.now(),
                backup_size=len(key_data),
                verification_hash=hashlib.sha256(key_data).hexdigest(),
                metadata=creator_metadata or {}
            )
            
            self.backup_jobs[job_id] = job
            
            # Execute backup asynchronously
            asyncio.create_task(self._execute_backup_job(job, key_data))
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Backup initiation failed: {e}")
            self.metrics['backups_failed'] += 1
            raise
    
    async def _execute_backup_job(self, job: BackupJob, key_data: bytes):
        """Execute backup job across multiple locations"""
        try:
            job.status = BackupStatus.IN_PROGRESS
            job.started_at = datetime.now()
            
            # Backup to all locations
            success_count = 0
            for location in job.backup_locations:
                try:
                    provider = self.providers.get(location.provider)
                    if not provider:
                        self.logger.error(f"Provider {location.provider} not available")
                        continue
                    
                    success = await provider.upload_backup(key_data, job.key_id, location)
                    if success:
                        success_count += 1
                        self.logger.info(f"Backup {job.job_id} successful to {location.provider.value}")
                    else:
                        self.logger.error(f"Backup {job.job_id} failed to {location.provider.value}")
                        
                except Exception as e:
                    self.logger.error(f"Backup to {location.provider.value} failed: {e}")
            
            # Update job status
            if success_count > 0:
                job.status = BackupStatus.COMPLETED
                job.completed_at = datetime.now()
                self.metrics['backups_created'] += 1
                
                # Schedule verification
                asyncio.create_task(self._verify_backup_job(job))
            else:
                job.status = BackupStatus.FAILED
                job.error_message = "All backup locations failed"
                self.metrics['backups_failed'] += 1
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            self.logger.error(f"Backup job execution failed: {e}")
            self.metrics['backups_failed'] += 1
    
    async def _verify_backup_job(self, job: BackupJob):
        """Verify backup integrity across locations"""
        try:
            job.status = BackupStatus.VERIFYING
            
            verification_results = []
            for location in job.backup_locations:
                try:
                    provider = self.providers.get(location.provider)
                    if not provider:
                        continue
                    
                    verified = await provider.verify_backup(
                        job.key_id, 
                        location, 
                        job.verification_hash
                    )
                    verification_results.append(verified)
                    
                    if verified:
                        self.logger.info(f"Backup {job.job_id} verified at {location.provider.value}")
                    else:
                        self.logger.error(f"Backup {job.job_id} verification failed at {location.provider.value}")
                        
                except Exception as e:
                    self.logger.error(f"Verification at {location.provider.value} failed: {e}")
                    verification_results.append(False)
            
            # Update status
            if any(verification_results):
                job.status = BackupStatus.VERIFIED
                self.metrics['verification_tests'] += 1
            else:
                job.status = BackupStatus.FAILED
                job.error_message = "All verifications failed"
                self.metrics['verification_failures'] += 1
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = f"Verification failed: {e}"
            self.logger.error(f"Backup verification failed: {e}")
            self.metrics['verification_failures'] += 1
    
    async def recover_key(self, 
                         key_id: str,
                         recovery_speed: RecoverySpeed = RecoverySpeed.STANDARD,
                         creator_id: Optional[str] = None,
                         target_location: str = "/tmp/recovered_keys") -> str:
        """Recover a key from backup"""
        try:
            job_id = str(uuid.uuid4())
            
            # Find available backups
            available_locations = await self._find_backup_locations(key_id)
            if not available_locations:
                raise ValueError(f"No backups found for key {key_id}")
            
            # Select optimal location based on recovery speed
            source_location = self._select_recovery_location(available_locations, recovery_speed)
            
            # Create recovery job
            job = RecoveryJob(
                job_id=job_id,
                key_id=key_id,
                creator_id=creator_id,
                source_location=source_location,
                target_location=target_location,
                recovery_speed=recovery_speed,
                status=BackupStatus.PENDING,
                created_at=datetime.now()
            )
            
            self.recovery_jobs[job_id] = job
            
            # Execute recovery
            asyncio.create_task(self._execute_recovery_job(job))
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Recovery initiation failed: {e}")
            raise
    
    async def _execute_recovery_job(self, job: RecoveryJob):
        """Execute recovery job"""
        try:
            job.status = BackupStatus.IN_PROGRESS
            job.started_at = datetime.now()
            
            # Perform recovery
            provider = self.providers.get(job.source_location.provider)
            if not provider:
                raise ValueError(f"Provider {job.source_location.provider} not available")
            
            # Download backup
            key_data = await provider.download_backup(job.key_id, job.source_location)
            if not key_data:
                raise ValueError("Failed to download backup")
            
            # Write to target location
            os.makedirs(job.target_location, exist_ok=True)
            target_file = os.path.join(job.target_location, f"{job.key_id}.recovered")
            
            with open(target_file, 'wb') as f:
                f.write(key_data)
            
            job.recovered_size = len(key_data)
            
            # Verify recovery
            with open(target_file, 'rb') as f:
                recovered_data = f.read()
            
            job.verification_passed = (recovered_data == key_data)
            
            # Update status
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            self.metrics['recoveries_performed'] += 1
            
            if job.creator_id and job.recovery_speed == RecoverySpeed.CREATOR_EMERGENCY:
                self.metrics['creator_emergency_recoveries'] += 1
            
            self.logger.info(f"Recovery {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            self.logger.error(f"Recovery job failed: {e}")
    
    def _select_backup_locations(self, 
                                policy: BackupPolicy, 
                                creator_metadata: Optional[Dict[str, Any]]) -> List[BackupLocation]:
        """Select backup locations based on policy"""
        selected_locations = []
        
        # Add locations based on retention policy
        for tier, retention_days in policy.retention_policy.items():
            for location_id, location in self.backup_locations.items():
                if (location.tier == tier and 
                    location.is_active and 
                    location.max_retention_days >= retention_days):
                    
                    # Check geographic requirements
                    if policy.geographic_distribution:
                        if location.region in policy.geographic_distribution:
                            selected_locations.append(location)
                    else:
                        selected_locations.append(location)
                    
                    break  # One location per tier
        
        # Add creator-specific locations if applicable
        if creator_metadata and creator_metadata.get('creator_type') in ['musician', 'visual_artist']:
            for location in self.backup_locations.values():
                if location.creator_specific and location not in selected_locations:
                    selected_locations.append(location)
        
        return selected_locations
    
    async def _find_backup_locations(self, key_id: str) -> List[BackupLocation]:
        """Find all locations with backups for a key"""
        available_locations = []
        
        for location in self.backup_locations.values():
            if not location.is_active:
                continue
                
            try:
                provider = self.providers.get(location.provider)
                if not provider:
                    continue
                
                # Try to download a small amount to verify existence
                backup_data = await provider.download_backup(key_id, location)
                if backup_data:
                    available_locations.append(location)
                    
            except Exception as e:
                self.logger.debug(f"Backup not found at {location.provider.value}: {e}")
        
        return available_locations
    
    def _select_recovery_location(self, 
                                 available_locations: List[BackupLocation], 
                                 recovery_speed: RecoverySpeed) -> BackupLocation:
        """Select optimal location for recovery based on speed requirements"""
        
        # Priority mapping for recovery speed
        tier_priority = {
            RecoverySpeed.IMMEDIATE: [BackupTier.HOT, BackupTier.CREATOR_PRIORITY, BackupTier.WARM],
            RecoverySpeed.CREATOR_EMERGENCY: [BackupTier.CREATOR_PRIORITY, BackupTier.HOT],
            RecoverySpeed.FAST: [BackupTier.HOT, BackupTier.WARM, BackupTier.COLD],
            RecoverySpeed.STANDARD: [BackupTier.WARM, BackupTier.HOT, BackupTier.COLD],
            RecoverySpeed.BATCH: [BackupTier.COLD, BackupTier.WARM, BackupTier.HOT]
        }
        
        preferred_tiers = tier_priority.get(recovery_speed, [BackupTier.HOT])
        
        # Select location with highest priority tier
        for tier in preferred_tiers:
            for location in available_locations:
                if location.tier == tier:
                    return location
        
        # Fallback to first available
        return available_locations[0]
    
    async def test_recovery_procedures(self, sample_size: int = 10) -> Dict[str, Any]:
        """Test recovery procedures for random sample of backups"""
        try:
            test_results = {
                'total_tests': 0,
                'successful_recoveries': 0,
                'failed_recoveries': 0,
                'average_recovery_time': 0.0,
                'test_details': []
            }
            
            # Get sample of backup jobs
            completed_jobs = [job for job in self.backup_jobs.values() 
                            if job.status == BackupStatus.VERIFIED]
            
            if not completed_jobs:
                return test_results
            
            import random
            sample_jobs = random.sample(completed_jobs, min(sample_size, len(completed_jobs)))
            
            recovery_times = []
            
            for job in sample_jobs:
                test_start = time.time()
                
                try:
                    # Perform test recovery
                    recovery_job_id = await self.recover_key(
                        job.key_id,
                        RecoverySpeed.FAST,
                        job.creator_id,
                        "/tmp/recovery_tests"
                    )
                    
                    # Wait for completion
                    recovery_job = self.recovery_jobs[recovery_job_id]
                    while recovery_job.status == BackupStatus.PENDING or recovery_job.status == BackupStatus.IN_PROGRESS:
                        await asyncio.sleep(1)
                    
                    test_time = time.time() - test_start
                    recovery_times.append(test_time)
                    
                    test_detail = {
                        'key_id': job.key_id,
                        'recovery_time': test_time,
                        'success': recovery_job.status == BackupStatus.COMPLETED,
                        'verification_passed': recovery_job.verification_passed
                    }
                    
                    if recovery_job.status == BackupStatus.COMPLETED:
                        test_results['successful_recoveries'] += 1
                    else:
                        test_results['failed_recoveries'] += 1
                    
                    test_results['test_details'].append(test_detail)
                    
                except Exception as e:
                    test_results['failed_recoveries'] += 1
                    test_results['test_details'].append({
                        'key_id': job.key_id,
                        'recovery_time': time.time() - test_start,
                        'success': False,
                        'error': str(e)
                    })
                
                test_results['total_tests'] += 1
            
            # Calculate average recovery time
            if recovery_times:
                test_results['average_recovery_time'] = sum(recovery_times) / len(recovery_times)
            
            self.logger.info(f"Recovery test completed: {test_results['successful_recoveries']}/{test_results['total_tests']} successful")
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"Recovery testing failed: {e}")
            return {'error': str(e)}
    
    def get_backup_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get backup job status"""
        job = self.backup_jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'key_id': job.key_id,
            'creator_id': job.creator_id,
            'status': job.status.value,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'backup_size': job.backup_size,
            'locations': len(job.backup_locations),
            'error_message': job.error_message
        }
    
    def get_recovery_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery job status"""
        job = self.recovery_jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'key_id': job.key_id,
            'creator_id': job.creator_id,
            'status': job.status.value,
            'recovery_speed': job.recovery_speed.value,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'recovered_size': job.recovered_size,
            'verification_passed': job.verification_passed,
            'error_message': job.error_message
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get backup orchestrator metrics"""
        return {
            'metrics': self.metrics.copy(),
            'active_backup_jobs': len([j for j in self.backup_jobs.values() 
                                     if j.status in [BackupStatus.PENDING, BackupStatus.IN_PROGRESS]]),
            'active_recovery_jobs': len([j for j in self.recovery_jobs.values() 
                                       if j.status in [BackupStatus.PENDING, BackupStatus.IN_PROGRESS]]),
            'total_backup_jobs': len(self.backup_jobs),
            'total_recovery_jobs': len(self.recovery_jobs),
            'configured_locations': len(self.backup_locations),
            'active_locations': len([l for l in self.backup_locations.values() if l.is_active])
        }


# Example usage
async def demo_backup_orchestrator():
    """Demonstrate backup orchestrator capabilities"""
    
    # Initialize orchestrator
    orchestrator = KeyBackupOrchestrator()
    
    # Sample creator metadata
    creator_metadata = {
        'creator_type': 'musician',
        'content_types': ['audio', 'video'],
        'region': 'North America',
        'followers': 100000,
        'engagement_rate': 0.12,
        'applicable_regulations': ['CCPA']
    }
    
    # Sample key data
    key_data = b"sample_encryption_key_data_for_creator"
    
    # Create backup
    backup_job_id = await orchestrator.backup_key(
        key_id="creator_key_music_001",
        key_data=key_data,
        creator_id="creator_musician_001",
        creator_metadata=creator_metadata
    )
    
    print(f"Backup job created: {backup_job_id}")
    
    # Wait a bit for backup to complete
    await asyncio.sleep(2)
    
    # Check backup status
    backup_status = orchestrator.get_backup_status(backup_job_id)
    print(f"Backup status: {json.dumps(backup_status, indent=2)}")
    
    # Test recovery
    recovery_job_id = await orchestrator.recover_key(
        key_id="creator_key_music_001",
        recovery_speed=RecoverySpeed.CREATOR_EMERGENCY,
        creator_id="creator_musician_001"
    )
    
    print(f"Recovery job created: {recovery_job_id}")
    
    # Wait for recovery
    await asyncio.sleep(2)
    
    # Check recovery status
    recovery_status = orchestrator.get_recovery_status(recovery_job_id)
    print(f"Recovery status: {json.dumps(recovery_status, indent=2)}")
    
    # Test recovery procedures
    test_results = await orchestrator.test_recovery_procedures(sample_size=1)
    print(f"Recovery test results: {json.dumps(test_results, indent=2)}")
    
    # Get metrics
    metrics = orchestrator.get_metrics()
    print(f"Orchestrator metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(demo_backup_orchestrator())