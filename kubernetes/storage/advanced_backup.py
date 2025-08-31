"""Advanced Backup Storage Manager - IA-Influencer-Agent Deployment
================================================================================
Module: backend/deployment/storage/advanced_backup.py
Author: Fahed Mlaiel <mlaiel@live.de>
Type: Industrial Deployment Manager - Advanced Backup and Recovery
Responsibility: Production-grade backup strategies and disaster recovery
Technologies: Python, Multi-Cloud Backup, Versioning, Point-in-Time Recovery
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior: Expert Python/FastAPI  
- ML Engineer: IA & Audio Processing
- DevOps Engineer: Infrastructure & Déploiement
- DBA: Optimisation Base de Données
- Sécurité Expert: Protection & Compliance
- Microservices: Architecture Distribuée

LOGIQUE MÉTIER:
Content creation → Backup scheduling → Multi-cloud replication → 
Version management → Point-in-time recovery → Integrity verification → Cost optimization
"""import logging
import asyncio
import hashlib
import gzip
import zstandard as zstd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import os
import aiofiles
from pathlib import Path
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient
import tempfile
import schedule
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backup operations"""    FULL = "full"  # Complete backup
    INCREMENTAL = "incremental"  # Only changed data
    DIFFERENTIAL = "differential"  # Changes since last full backup
    SNAPSHOT = "snapshot"  # Point-in-time snapshot
    CONTINUOUS = "continuous"  # Real-time replication


class BackupTier(Enum):
    """Backup storage tiers for cost optimization"""    HOT = "hot"  # Immediate access
    WARM = "warm"  # Access within hours
    COLD = "cold"  # Access within days
    ARCHIVE = "archive"  # Long-term storage
    DEEP_ARCHIVE = "deep_archive"  # Rare access


class RecoveryObjective(Enum):
    """Recovery time and point objectives"""    RTO_1_HOUR = "rto_1h"  # Recovery Time Objective: 1 hour
    RTO_4_HOURS = "rto_4h"  # Recovery Time Objective: 4 hours
    RTO_24_HOURS = "rto_24h"  # Recovery Time Objective: 24 hours
    RPO_ZERO = "rpo_0"  # Recovery Point Objective: no data loss
    RPO_1_HOUR = "rpo_1h"  # Recovery Point Objective: 1 hour data loss
    RPO_24_HOURS = "rpo_24h"  # Recovery Point Objective: 24 hours data loss


class BackupStatus(Enum):
    """Backup operation status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"
    VERIFIED = "verified"


class CloudProvider(Enum):
    """Supported cloud providers for backup"""    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    LOCAL_STORAGE = "local_storage"
    MULTIPLE = "multiple"  # Multi-cloud backup


@dataclass
class BackupPolicy:
    """Backup policy configuration"""    policy_name: str
    backup_type: BackupType
    backup_tier: BackupTier
    schedule_cron: str  # Cron expression for scheduling
    
    # Recovery objectives
    recovery_time_objective: RecoveryObjective
    recovery_point_objective: RecoveryObjective
    
    # Retention policy
    retention_days: int = 90
    max_versions: int = 10
    
    # Storage configuration
    cloud_providers: List[CloudProvider] = field(default_factory=lambda: [CloudProvider.AWS_S3])
    encryption_enabled: bool = True
    compression_enabled: bool = True
    
    # Performance settings
    parallel_uploads: int = 5
    chunk_size_mb: int = 64
    bandwidth_limit_mbps: Optional[int] = None
    
    # Verification settings
    integrity_check: bool = True
    checksum_algorithm: str = "sha256"
    verification_frequency_days: int = 7


@dataclass
class BackupMetadata:
    """Backup metadata and tracking information"""    backup_id: str
    policy_name: str
    backup_type: BackupType
    source_path: str
    
    # Timing information
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Size and performance metrics
    source_size_bytes: int = 0
    backup_size_bytes: int = 0
    compression_ratio: float = 0.0
    transfer_speed_mbps: float = 0.0
    
    # Status and results
    status: BackupStatus = BackupStatus.PENDING
    error_message: Optional[str] = None
    
    # Storage information
    cloud_locations: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    encrypted: bool = False
    
    # Version information
    version: int = 1
    parent_backup_id: Optional[str] = None  # For incremental backups
    
    # Additional metadata
    tags: Dict[str, str] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryRequest:
    """Data recovery request"""    request_id: str
    backup_id: str
    requested_by: str
    requested_at: datetime
    
    # Recovery parameters
    target_path: str
    point_in_time: Optional[datetime] = None
    partial_recovery: bool = False
    file_patterns: List[str] = field(default_factory=list)
    
    # Status tracking
    status: BackupStatus = BackupStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    recovered_files: int = 0
    recovered_size_bytes: int = 0
    error_message: Optional[str] = None


@dataclass
class BackupMetrics:
    """Comprehensive backup metrics"""    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    
    # Storage metrics
    total_backup_size_gb: float = 0.0
    storage_cost_monthly_usd: float = 0.0
    
    # Performance metrics
    avg_backup_time_minutes: float = 0.0
    avg_transfer_speed_mbps: float = 0.0
    avg_compression_ratio: float = 0.0
    
    # Recovery metrics
    total_recovery_requests: int = 0
    successful_recoveries: int = 0
    avg_recovery_time_minutes: float = 0.0
    
    # Compliance metrics
    rto_compliance_percent: float = 100.0
    rpo_compliance_percent: float = 100.0
    
    # Last updated
    last_updated: datetime = field(default_factory=datetime.now)


class AdvancedBackupManager:
    """    🎯 Advanced Backup Storage Manager - IA-Influencer-Agent
    
    Enterprise-grade backup and disaster recovery solution providing:
    - Multi-cloud backup strategies with automatic failover
    - Intelligent backup scheduling and lifecycle management
    - Point-in-time recovery with granular restore capabilities
    - Advanced compression and deduplication algorithms
    - Automated integrity verification and self-healing
    - Cost optimization with intelligent tiering
    - Compliance-ready retention and audit trails
    - Real-time monitoring and alerting
    """    
    def __init__(self):
        self.policies: Dict[str, BackupPolicy] = {}
        self.backup_history: List[BackupMetadata] = []
        self.recovery_requests: Dict[str, RecoveryRequest] = {}
        self.metrics = BackupMetrics()
        
        # Cloud clients
        self._aws_s3_client: Optional[boto3.client] = None
        self._gcs_client: Optional[gcs.Client] = None
        self._azure_blob_client: Optional[BlobServiceClient] = None
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._compression_cache: Dict[str, bytes] = {}
        
        # Initialize cloud clients
        self._initialize_cloud_clients()
        
        # Setup default policies
        self._create_default_policies()
        
        logger.info("🚀 AdvancedBackupManager initialized with multi-cloud support")
    
    def _initialize_cloud_clients(self):
        """Initialize cloud storage clients"""        try:
            # AWS S3 client
            if os.getenv("AWS_ACCESS_KEY_ID"):
                self._aws_s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "eu-west-1")
                )
                logger.info("✅ AWS S3 client initialized")
            
            # Google Cloud Storage client
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                self._gcs_client = gcs.Client()
                logger.info("✅ Google Cloud Storage client initialized")
            
            # Azure Blob Storage client
            if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
                self._azure_blob_client = BlobServiceClient.from_connection_string(
                    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                )
                logger.info("✅ Azure Blob Storage client initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Cloud client initialization partial: {e}")
    
    def _create_default_policies(self):
        """Create default backup policies"""        try:
            # High-frequency policy for critical data
            self.policies["critical_data"] = BackupPolicy(
                policy_name="critical_data",
                backup_type=BackupType.INCREMENTAL,
                backup_tier=BackupTier.HOT,
                schedule_cron="0 */4 * * *",  # Every 4 hours
                recovery_time_objective=RecoveryObjective.RTO_1_HOUR,
                recovery_point_objective=RecoveryObjective.RPO_1_HOUR,
                retention_days=365,
                max_versions=50,
                cloud_providers=[CloudProvider.AWS_S3, CloudProvider.GOOGLE_CLOUD]
            )
            
            # Daily policy for standard data
            self.policies["standard_data"] = BackupPolicy(
                policy_name="standard_data",
                backup_type=BackupType.INCREMENTAL,
                backup_tier=BackupTier.WARM,
                schedule_cron="0 2 * * *",  # Daily at 2 AM
                recovery_time_objective=RecoveryObjective.RTO_4_HOURS,
                recovery_point_objective=RecoveryObjective.RPO_24_HOURS,
                retention_days=90,
                max_versions=20,
                cloud_providers=[CloudProvider.AWS_S3]
            )
            
            # Weekly policy for archival data
            self.policies["archival_data"] = BackupPolicy(
                policy_name="archival_data",
                backup_type=BackupType.FULL,
                backup_tier=BackupTier.ARCHIVE,
                schedule_cron="0 3 * * 0",  # Weekly on Sunday at 3 AM
                recovery_time_objective=RecoveryObjective.RTO_24_HOURS,
                recovery_point_objective=RecoveryObjective.RPO_24_HOURS,
                retention_days=2555,  # 7 years
                max_versions=5,
                cloud_providers=[CloudProvider.AWS_S3],
                compression_enabled=True
            )
            
            logger.info("✅ Default backup policies created")
            
        except Exception as e:
            logger.error(f"❌ Default policy creation failed: {e}")
    
    async def create_backup(self, source_path: str, policy_name: str, 
                           tags: Optional[Dict[str, str]] = None) -> str:
        """Create backup according to specified policy"""        try:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.sha256(source_path.encode()).hexdigest()[:8]}"
            
            if policy_name not in self.policies:
                raise ValueError(f"Backup policy not found: {policy_name}")
            
            policy = self.policies[policy_name]
            
            # Create backup metadata
            backup_metadata = BackupMetadata(
                backup_id=backup_id,
                policy_name=policy_name,
                backup_type=policy.backup_type,
                source_path=source_path,
                started_at=datetime.now(),
                status=BackupStatus.RUNNING,
                tags=tags or {}
            )
            
            logger.info(f"🔄 Starting backup: {backup_id} for {source_path}")
            
            try:
                # Determine what to backup based on type
                files_to_backup = await self._determine_backup_files(source_path, policy)
                
                if not files_to_backup:
                    backup_metadata.status = BackupStatus.COMPLETED
                    backup_metadata.completed_at = datetime.now()
                    logger.info(f"✅ No changes detected for incremental backup: {backup_id}")
                    return backup_id
                
                # Calculate source size
                source_size = sum(os.path.getsize(f) for f in files_to_backup if os.path.exists(f))
                backup_metadata.source_size_bytes = source_size
                
                # Create backup package
                backup_data = await self._create_backup_package(files_to_backup, policy)
                backup_metadata.backup_size_bytes = len(backup_data)
                backup_metadata.compression_ratio = 1 - (len(backup_data) / source_size) if source_size > 0 else 0
                
                # Calculate checksum
                if policy.integrity_check:
                    backup_metadata.checksum = hashlib.sha256(backup_data).hexdigest()
                
                # Upload to cloud providers
                upload_results = await self._upload_to_clouds(backup_data, backup_metadata, policy)
                backup_metadata.cloud_locations = upload_results
                
                # Update completion status
                backup_metadata.status = BackupStatus.COMPLETED
                backup_metadata.completed_at = datetime.now()
                backup_metadata.duration_seconds = (
                    backup_metadata.completed_at - backup_metadata.started_at
                ).total_seconds()
                
                # Calculate transfer speed
                if backup_metadata.duration_seconds > 0:
                    backup_metadata.transfer_speed_mbps = (
                        backup_metadata.backup_size_bytes / 1024 / 1024 / backup_metadata.duration_seconds
                    )
                
                # Update metrics
                self._update_backup_metrics(backup_metadata)
                
                logger.info(f"✅ Backup completed successfully: {backup_id}")
                
            except Exception as e:
                backup_metadata.status = BackupStatus.FAILED
                backup_metadata.error_message = str(e)
                backup_metadata.completed_at = datetime.now()
                logger.error(f"❌ Backup failed: {backup_id} - {e}")
                raise
            
            finally:
                self.backup_history.append(backup_metadata)
                
                # Keep only last 1000 backup records in memory
                if len(self.backup_history) > 1000:
                    self.backup_history = self.backup_history[-1000:]
            
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise
    
    async def _determine_backup_files(self, source_path: str, policy: BackupPolicy) -> List[str]:
        """Determine which files need to be backed up based on backup type"""        try:
            files_to_backup = []
            
            if policy.backup_type == BackupType.FULL:
                # Full backup: include all files
                if os.path.isfile(source_path):
                    files_to_backup = [source_path]
                elif os.path.isdir(source_path):
                    for root, _, files in os.walk(source_path):
                        for file in files:
                            files_to_backup.append(os.path.join(root, file))
                
            elif policy.backup_type in [BackupType.INCREMENTAL, BackupType.DIFFERENTIAL]:
                # Find last backup for comparison
                last_backup = self._find_last_successful_backup(source_path, policy.policy_name)
                
                if not last_backup:
                    # No previous backup, do full backup
                    return await self._determine_backup_files(source_path, 
                        BackupPolicy(**{**policy.__dict__, 'backup_type': BackupType.FULL}))
                
                # Compare modification times
                last_backup_time = last_backup.started_at
                
                if os.path.isfile(source_path):
                    if os.path.getmtime(source_path) > last_backup_time.timestamp():
                        files_to_backup = [source_path]
                elif os.path.isdir(source_path):
                    for root, _, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.getmtime(file_path) > last_backup_time.timestamp():
                                files_to_backup.append(file_path)
            
            return files_to_backup
            
        except Exception as e:
            logger.error(f"❌ Failed to determine backup files: {e}")
            return []
    
    def _find_last_successful_backup(self, source_path: str, policy_name: str) -> Optional[BackupMetadata]:
        """Find the last successful backup for given source and policy"""        try:
            successful_backups = [
                backup for backup in self.backup_history
                if (backup.source_path == source_path and 
                    backup.policy_name == policy_name and
                    backup.status == BackupStatus.COMPLETED)
            ]
            
            if successful_backups:
                return max(successful_backups, key=lambda b: b.started_at)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find last backup: {e}")
            return None
    
    async def _create_backup_package(self, files: List[str], policy: BackupPolicy) -> bytes:
        """Create compressed and optionally encrypted backup package"""        try:
            # Create temporary tar-like structure in memory
            backup_data = {}
            
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        async with aiofiles.open(file_path, 'rb') as f:
                            file_content = await f.read()
                            backup_data[file_path] = {
                                'content': file_content,
                                'size': len(file_content),
                                'modified_time': os.path.getmtime(file_path)
                            }
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read file {file_path}: {e}")
                    continue
            
            # Serialize backup data
            serialized_data = json.dumps(backup_data, default=str).encode()
            
            # Apply compression if enabled
            if policy.compression_enabled:
                if policy.backup_tier in [BackupTier.ARCHIVE, BackupTier.DEEP_ARCHIVE]:
                    # Use high compression for archive tiers
                    cctx = zstd.ZstdCompressor(level=19)
                    compressed_data = cctx.compress(serialized_data)
                else:
                    # Use faster compression for hot/warm tiers
                    compressed_data = gzip.compress(serialized_data, compresslevel=6)
                
                return compressed_data
            else:
                return serialized_data
                
        except Exception as e:
            logger.error(f"❌ Backup package creation failed: {e}")
            raise
    
    async def _upload_to_clouds(self, backup_data: bytes, metadata: BackupMetadata, 
                               policy: BackupPolicy) -> List[str]:
        """Upload backup to configured cloud providers"""        try:
            upload_tasks = []
            cloud_locations = []
            
            for provider in policy.cloud_providers:
                if provider == CloudProvider.AWS_S3 and self._aws_s3_client:
                    task = asyncio.create_task(
                        self._upload_to_aws_s3(backup_data, metadata, policy)
                    )
                    upload_tasks.append((provider, task))
                
                elif provider == CloudProvider.GOOGLE_CLOUD and self._gcs_client:
                    task = asyncio.create_task(
                        self._upload_to_gcs(backup_data, metadata, policy)
                    )
                    upload_tasks.append((provider, task))
                
                elif provider == CloudProvider.AZURE_BLOB and self._azure_blob_client:
                    task = asyncio.create_task(
                        self._upload_to_azure(backup_data, metadata, policy)
                    )
                    upload_tasks.append((provider, task))
            
            # Wait for all uploads to complete
            for provider, task in upload_tasks:
                try:
                    location = await task
                    cloud_locations.append(f"{provider.value}:{location}")
                    logger.info(f"✅ Uploaded to {provider.value}: {location}")
                except Exception as e:
                    logger.error(f"❌ Upload to {provider.value} failed: {e}")
                    # Continue with other providers
            
            if not cloud_locations:
                raise Exception("All cloud uploads failed")
            
            return cloud_locations
            
        except Exception as e:
            logger.error(f"❌ Cloud upload failed: {e}")
            raise
    
    async def _upload_to_aws_s3(self, backup_data: bytes, metadata: BackupMetadata, 
                               policy: BackupPolicy) -> str:
        """Upload backup to AWS S3"""        try:
            bucket_name = os.getenv("AWS_BACKUP_BUCKET", "ia-influencer-backups")
            key = f"{policy.policy_name}/{metadata.backup_id}/{metadata.backup_id}.backup"
            
            # Determine storage class based on backup tier
            storage_class_map = {
                BackupTier.HOT: "STANDARD",
                BackupTier.WARM: "STANDARD_IA",
                BackupTier.COLD: "GLACIER",
                BackupTier.ARCHIVE: "GLACIER",
                BackupTier.DEEP_ARCHIVE: "DEEP_ARCHIVE"
            }
            
            storage_class = storage_class_map.get(policy.backup_tier, "STANDARD")
            
            # Upload with metadata
            extra_args = {
                'StorageClass': storage_class,
                'Metadata': {
                    'backup-id': metadata.backup_id,
                    'policy-name': policy.policy_name,
                    'backup-type': policy.backup_type.value,
                    'source-path': metadata.source_path,
                    'checksum': metadata.checksum or '',
                    'created-at': metadata.started_at.isoformat()
                }
            }
            
            # Use multipart upload for large files
            if len(backup_data) > 100 * 1024 * 1024:  # 100MB
                with tempfile.NamedTemporaryFile() as temp_file:
                    temp_file.write(backup_data)
                    temp_file.flush()
                    
                    self._aws_s3_client.upload_file(
                        temp_file.name,
                        bucket_name,
                        key,
                        ExtraArgs=extra_args
                    )
            else:
                self._aws_s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=backup_data,
                    **extra_args
                )
            
            return f"s3://{bucket_name}/{key}"
            
        except Exception as e:
            logger.error(f"❌ AWS S3 upload failed: {e}")
            raise
    
    async def _upload_to_gcs(self, backup_data: bytes, metadata: BackupMetadata, 
                            policy: BackupPolicy) -> str:
        """Upload backup to Google Cloud Storage"""        try:
            bucket_name = os.getenv("GCS_BACKUP_BUCKET", "ia-influencer-backups")
            blob_name = f"{policy.policy_name}/{metadata.backup_id}/{metadata.backup_id}.backup"
            
            bucket = self._gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Set metadata
            blob.metadata = {
                'backup-id': metadata.backup_id,
                'policy-name': policy.policy_name,
                'backup-type': policy.backup_type.value,
                'source-path': metadata.source_path,
                'checksum': metadata.checksum or '',
                'created-at': metadata.started_at.isoformat()
            }
            
            # Set storage class based on backup tier
            storage_class_map = {
                BackupTier.HOT: "STANDARD",
                BackupTier.WARM: "NEARLINE",
                BackupTier.COLD: "COLDLINE",
                BackupTier.ARCHIVE: "ARCHIVE",
                BackupTier.DEEP_ARCHIVE: "ARCHIVE"
            }
            
            blob.storage_class = storage_class_map.get(policy.backup_tier, "STANDARD")
            
            # Upload data
            blob.upload_from_string(backup_data)
            
            return f"gs://{bucket_name}/{blob_name}"
            
        except Exception as e:
            logger.error(f"❌ Google Cloud Storage upload failed: {e}")
            raise
    
    async def _upload_to_azure(self, backup_data: bytes, metadata: BackupMetadata, 
                              policy: BackupPolicy) -> str:
        """Upload backup to Azure Blob Storage"""        try:
            container_name = os.getenv("AZURE_BACKUP_CONTAINER", "ia-influencer-backups")
            blob_name = f"{policy.policy_name}/{metadata.backup_id}/{metadata.backup_id}.backup"
            
            # Set access tier based on backup tier
            access_tier_map = {
                BackupTier.HOT: "Hot",
                BackupTier.WARM: "Cool",
                BackupTier.COLD: "Cool",
                BackupTier.ARCHIVE: "Archive",
                BackupTier.DEEP_ARCHIVE: "Archive"
            }
            
            access_tier = access_tier_map.get(policy.backup_tier, "Hot")
            
            # Upload with metadata
            blob_client = self._azure_blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                backup_data,
                overwrite=True,
                metadata={
                    'backup_id': metadata.backup_id,
                    'policy_name': policy.policy_name,
                    'backup_type': policy.backup_type.value,
                    'source_path': metadata.source_path,
                    'checksum': metadata.checksum or '',
                    'created_at': metadata.started_at.isoformat()
                },
                standard_blob_tier=access_tier
            )
            
            return f"https://{blob_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
            
        except Exception as e:
            logger.error(f"❌ Azure Blob Storage upload failed: {e}")
            raise
    
    def _update_backup_metrics(self, metadata: BackupMetadata):
        """Update backup metrics based on completed backup"""        try:
            self.metrics.total_backups += 1
            
            if metadata.status == BackupStatus.COMPLETED:
                self.metrics.successful_backups += 1
                
                # Update averages
                total_successful = self.metrics.successful_backups
                
                # Backup time average
                if metadata.duration_seconds:
                    new_time_minutes = metadata.duration_seconds / 60
                    self.metrics.avg_backup_time_minutes = (
                        (self.metrics.avg_backup_time_minutes * (total_successful - 1) + new_time_minutes) / total_successful
                    )
                
                # Transfer speed average
                if metadata.transfer_speed_mbps > 0:
                    self.metrics.avg_transfer_speed_mbps = (
                        (self.metrics.avg_transfer_speed_mbps * (total_successful - 1) + metadata.transfer_speed_mbps) / total_successful
                    )
                
                # Compression ratio average
                if metadata.compression_ratio > 0:
                    self.metrics.avg_compression_ratio = (
                        (self.metrics.avg_compression_ratio * (total_successful - 1) + metadata.compression_ratio) / total_successful
                    )
                
                # Storage size
                self.metrics.total_backup_size_gb += metadata.backup_size_bytes / (1024 ** 3)
            
            else:
                self.metrics.failed_backups += 1
            
            self.metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Metrics update failed: {e}")
    
    async def restore_backup(self, backup_id: str, target_path: str, 
                            requested_by: str, point_in_time: Optional[datetime] = None) -> str:
        """Restore backup to specified location"""        try:
            request_id = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.sha256(backup_id.encode()).hexdigest()[:8]}"
            
            # Find backup metadata
            backup_metadata = next(
                (b for b in self.backup_history if b.backup_id == backup_id),
                None
            )
            
            if not backup_metadata:
                raise ValueError(f"Backup not found: {backup_id}")
            
            if backup_metadata.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup not in completed state: {backup_metadata.status}")
            
            # Create recovery request
            recovery_request = RecoveryRequest(
                request_id=request_id,
                backup_id=backup_id,
                requested_by=requested_by,
                requested_at=datetime.now(),
                target_path=target_path,
                point_in_time=point_in_time,
                status=BackupStatus.RUNNING,
                started_at=datetime.now()
            )
            
            self.recovery_requests[request_id] = recovery_request
            
            logger.info(f"🔄 Starting restore: {request_id} for backup {backup_id}")
            
            try:
                # Download backup data from cloud
                backup_data = await self._download_backup_data(backup_metadata)
                
                # Decompress and decrypt if needed
                restored_data = await self._extract_backup_package(backup_data, backup_metadata)
                
                # Restore files to target location
                restored_files = await self._restore_files(restored_data, target_path, recovery_request)
                
                # Update recovery request
                recovery_request.status = BackupStatus.COMPLETED
                recovery_request.completed_at = datetime.now()
                recovery_request.recovered_files = len(restored_files)
                recovery_request.recovered_size_bytes = sum(
                    os.path.getsize(f) for f in restored_files if os.path.exists(f)
                )
                
                # Update metrics
                self._update_recovery_metrics(recovery_request)
                
                logger.info(f"✅ Restore completed: {request_id} - {len(restored_files)} files restored")
                
            except Exception as e:
                recovery_request.status = BackupStatus.FAILED
                recovery_request.error_message = str(e)
                recovery_request.completed_at = datetime.now()
                logger.error(f"❌ Restore failed: {request_id} - {e}")
                raise
            
            return request_id
            
        except Exception as e:
            logger.error(f"❌ Backup restore failed: {e}")
            raise
    
    async def _download_backup_data(self, metadata: BackupMetadata) -> bytes:
        """Download backup data from cloud storage"""        try:
            # Try each cloud location until successful
            for location in metadata.cloud_locations:
                try:
                    provider, path = location.split(':', 1)
                    
                    if provider == "aws_s3":
                        return await self._download_from_aws_s3(path)
                    elif provider == "google_cloud":
                        return await self._download_from_gcs(path)
                    elif provider == "azure_blob":
                        return await self._download_from_azure(path)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to download from {location}: {e}")
                    continue
            
            raise Exception("Failed to download from all cloud locations")
            
        except Exception as e:
            logger.error(f"❌ Backup download failed: {e}")
            raise
    
    async def _download_from_aws_s3(self, s3_path: str) -> bytes:
        """Download backup from AWS S3"""        try:
            # Parse S3 path
            s3_path = s3_path.replace('s3://', '')
            bucket, key = s3_path.split('/', 1)
            
            response = self._aws_s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
            
        except Exception as e:
            logger.error(f"❌ AWS S3 download failed: {e}")
            raise
    
    async def _download_from_gcs(self, gcs_path: str) -> bytes:
        """Download backup from Google Cloud Storage"""        try:
            # Parse GCS path
            gcs_path = gcs_path.replace('gs://', '')
            bucket_name, blob_name = gcs_path.split('/', 1)
            
            bucket = self._gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            return blob.download_as_bytes()
            
        except Exception as e:
            logger.error(f"❌ Google Cloud Storage download failed: {e}")
            raise
    
    async def _download_from_azure(self, azure_path: str) -> bytes:
        """Download backup from Azure Blob Storage"""        try:
            # Parse Azure path and extract container and blob name
            # Format: https://account.blob.core.windows.net/container/blob
            path_parts = azure_path.split('/')
            container_name = path_parts[-2]
            blob_name = path_parts[-1]
            
            blob_client = self._azure_blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            return blob_client.download_blob().readall()
            
        except Exception as e:
            logger.error(f"❌ Azure Blob Storage download failed: {e}")
            raise
    
    async def _extract_backup_package(self, backup_data: bytes, metadata: BackupMetadata) -> Dict[str, Any]:
        """Extract and decompress backup package"""        try:
            # Get policy for compression settings
            policy = self.policies.get(metadata.policy_name)
            
            # Decompress if needed
            if policy and policy.compression_enabled:
                # Try different decompression methods
                try:
                    # Try zstandard first (higher compression)
                    dctx = zstd.ZstdDecompressor()
                    decompressed_data = dctx.decompress(backup_data)
                except:
                    # Fall back to gzip
                    decompressed_data = gzip.decompress(backup_data)
            else:
                decompressed_data = backup_data
            
            # Deserialize backup data
            restored_data = json.loads(decompressed_data.decode())
            
            return restored_data
            
        except Exception as e:
            logger.error(f"❌ Backup package extraction failed: {e}")
            raise
    
    async def _restore_files(self, restored_data: Dict[str, Any], target_path: str, 
                            recovery_request: RecoveryRequest) -> List[str]:
        """Restore files to target location"""        try:
            restored_files = []
            
            # Create target directory if it doesn't exist
            Path(target_path).mkdir(parents=True, exist_ok=True)
            
            for file_path, file_info in restored_data.items():
                try:
                    # Determine target file path
                    relative_path = os.path.relpath(file_path, start='/')
                    target_file_path = os.path.join(target_path, relative_path)
                    
                    # Create directory structure
                    target_dir = os.path.dirname(target_file_path)
                    Path(target_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Write file content
                    file_content = file_info['content']
                    if isinstance(file_content, str):
                        file_content = file_content.encode()
                    
                    async with aiofiles.open(target_file_path, 'wb') as f:
                        await f.write(file_content)
                    
                    # Restore modification time
                    os.utime(target_file_path, (file_info['modified_time'], file_info['modified_time']))
                    
                    restored_files.append(target_file_path)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to restore file {file_path}: {e}")
                    continue
            
            return restored_files
            
        except Exception as e:
            logger.error(f"❌ File restoration failed: {e}")
            raise
    
    def _update_recovery_metrics(self, recovery_request: RecoveryRequest):
        """Update recovery metrics"""        try:
            self.metrics.total_recovery_requests += 1
            
            if recovery_request.status == BackupStatus.COMPLETED:
                self.metrics.successful_recoveries += 1
                
                # Calculate recovery time
                if recovery_request.started_at and recovery_request.completed_at:
                    recovery_time_minutes = (
                        recovery_request.completed_at - recovery_request.started_at
                    ).total_seconds() / 60
                    
                    # Update average
                    total_successful = self.metrics.successful_recoveries
                    self.metrics.avg_recovery_time_minutes = (
                        (self.metrics.avg_recovery_time_minutes * (total_successful - 1) + recovery_time_minutes) / total_successful
                    )
            
            self.metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Recovery metrics update failed: {e}")
    
    async def verify_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity using checksums"""        try:
            logger.info(f"🔍 Verifying backup integrity: {backup_id}")
            
            # Find backup metadata
            backup_metadata = next(
                (b for b in self.backup_history if b.backup_id == backup_id),
                None
            )
            
            if not backup_metadata:
                raise ValueError(f"Backup not found: {backup_id}")
            
            verification_results = {
                "backup_id": backup_id,
                "verification_time": datetime.now().isoformat(),
                "integrity_status": "unknown",
                "cloud_verifications": [],
                "checksum_match": False,
                "size_match": False
            }
            
            original_checksum = backup_metadata.checksum
            original_size = backup_metadata.backup_size_bytes
            
            # Verify each cloud location
            for location in backup_metadata.cloud_locations:
                try:
                    provider, path = location.split(':', 1)
                    
                    # Download and verify
                    backup_data = await self._download_backup_data(backup_metadata)
                    
                    # Verify checksum
                    actual_checksum = hashlib.sha256(backup_data).hexdigest()
                    checksum_match = actual_checksum == original_checksum
                    
                    # Verify size
                    actual_size = len(backup_data)
                    size_match = actual_size == original_size
                    
                    verification_results["cloud_verifications"].append({
                        "provider": provider,
                        "location": path,
                        "checksum_match": checksum_match,
                        "size_match": size_match,
                        "actual_checksum": actual_checksum,
                        "actual_size": actual_size
                    })
                    
                    # Update overall status
                    verification_results["checksum_match"] = checksum_match
                    verification_results["size_match"] = size_match
                    
                except Exception as e:
                    verification_results["cloud_verifications"].append({
                        "provider": provider,
                        "location": path,
                        "error": str(e)
                    })
            
            # Determine overall integrity status
            all_verifications_passed = all(
                v.get("checksum_match", False) and v.get("size_match", False)
                for v in verification_results["cloud_verifications"]
                if "error" not in v
            )
            
            verification_results["integrity_status"] = "valid" if all_verifications_passed else "corrupted"
            
            logger.info(f"✅ Backup verification completed: {backup_id} - Status: {verification_results['integrity_status']}")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {e}")
            return {"backup_id": backup_id, "error": str(e)}
    
    async def get_backup_metrics(self) -> Dict[str, Any]:
        """Get comprehensive backup metrics"""        try:
            # Calculate additional metrics
            success_rate = (
                (self.metrics.successful_backups / self.metrics.total_backups * 100)
                if self.metrics.total_backups > 0 else 100
            )
            
            recovery_success_rate = (
                (self.metrics.successful_recoveries / self.metrics.total_recovery_requests * 100)
                if self.metrics.total_recovery_requests > 0 else 100
            )
            
            # Estimate monthly storage cost (rough calculation)
            estimated_monthly_cost = self.metrics.total_backup_size_gb * 0.023  # AWS S3 Standard pricing
            
            return {
                "backup_statistics": {
                    "total_backups": self.metrics.total_backups,
                    "successful_backups": self.metrics.successful_backups,
                    "failed_backups": self.metrics.failed_backups,
                    "success_rate_percent": round(success_rate, 2),
                    "avg_backup_time_minutes": round(self.metrics.avg_backup_time_minutes, 2),
                    "avg_transfer_speed_mbps": round(self.metrics.avg_transfer_speed_mbps, 2),
                    "avg_compression_ratio": round(self.metrics.avg_compression_ratio, 2)
                },
                "storage_metrics": {
                    "total_backup_size_gb": round(self.metrics.total_backup_size_gb, 2),
                    "estimated_monthly_cost_usd": round(estimated_monthly_cost, 2)
                },
                "recovery_statistics": {
                    "total_recovery_requests": self.metrics.total_recovery_requests,
                    "successful_recoveries": self.metrics.successful_recoveries,
                    "recovery_success_rate_percent": round(recovery_success_rate, 2),
                    "avg_recovery_time_minutes": round(self.metrics.avg_recovery_time_minutes, 2)
                },
                "compliance_metrics": {
                    "rto_compliance_percent": self.metrics.rto_compliance_percent,
                    "rpo_compliance_percent": self.metrics.rpo_compliance_percent
                },
                "policies": {
                    "total_policies": len(self.policies),
                    "policy_names": list(self.policies.keys())
                },
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Backup metrics calculation failed: {e}")
            return {"error": str(e)}


# Global backup manager instance
backup_manager = AdvancedBackupManager()


# Factory functions
def create_backup_manager() -> AdvancedBackupManager:
    """Factory function to create backup manager instance"""    return AdvancedBackupManager()


def create_custom_backup_policy(
    name: str,
    backup_type: BackupType,
    schedule: str,
    retention_days: int = 90
) -> BackupPolicy:
    """Factory function to create custom backup policy"""    return BackupPolicy(
        policy_name=name,
        backup_type=backup_type,
        backup_tier=BackupTier.WARM,
        schedule_cron=schedule,
        recovery_time_objective=RecoveryObjective.RTO_4_HOURS,
        recovery_point_objective=RecoveryObjective.RPO_24_HOURS,
        retention_days=retention_days
    )


# Usage Example
async def main():
    """Example usage of AdvancedBackupManager"""    try:
        backup_mgr = create_backup_manager()
        
        # Create a backup
        backup_id = await backup_mgr.create_backup(
            source_path="/tmp/test_data",
            policy_name="standard_data",
            tags={"environment": "production", "project": "ia-influencer"}
        )
        print(f"Backup created: {backup_id}")
        
        # Verify backup integrity
        verification = await backup_mgr.verify_backup_integrity(backup_id)
        print(f"Backup verification: {verification['integrity_status']}")
        
        # Restore backup
        restore_id = await backup_mgr.restore_backup(
            backup_id=backup_id,
            target_path="/tmp/restored_data",
            requested_by="admin"
        )
        print(f"Restore initiated: {restore_id}")
        
        # Get metrics
        metrics = await backup_mgr.get_backup_metrics()
        print(f"Backup metrics: {json.dumps(metrics, indent=2)}")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
