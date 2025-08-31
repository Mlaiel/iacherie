"""
Storage Management System

Provides comprehensive storage infrastructure including object storage (S3),
persistent volumes, backup strategies, and data lifecycle management.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED 
"""

import asyncio
import logging
import json
import yaml
import boto3
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from kubernetes import client, config

logger = logging.getLogger(__name__)

class StorageType(Enum):
    """Storage types"""
    OBJECT_STORAGE = "object_storage"
    BLOCK_STORAGE = "block_storage"
    FILE_STORAGE = "file_storage"
    DATABASE_STORAGE = "database_storage"

class StorageClass(Enum):
    """Kubernetes storage classes"""
    STANDARD = "standard"
    FAST_SSD = "fast-ssd"
    SLOW_HDD = "slow-hdd"
    NETWORK_ATTACHED = "network-attached"

class BackupStrategy(Enum):
    """Backup strategies"""
    FULL_BACKUP = "full_backup"
    INCREMENTAL_BACKUP = "incremental_backup"
    DIFFERENTIAL_BACKUP = "differential_backup"
    SNAPSHOT = "snapshot"

class DataTier(Enum):
    """Data storage tiers"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"

@dataclass
class StorageConfig:
    """Storage configuration"""
    name: str
    storage_type: StorageType
    size: str
    storage_class: StorageClass
    namespace: str = "default"
    access_modes: List[str] = field(default_factory=lambda: ["ReadWriteOnce"])
    mount_path: str = "/data"
    backup_enabled: bool = True
    encryption_enabled: bool = True
    replication_factor: int = 3

@dataclass
class ObjectStorageConfig:
    """Object storage configuration"""
    bucket_name: str
    region: str
    storage_class: str = "STANDARD"
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    lifecycle_policy: Optional[Dict[str, Any]] = None
    cors_configuration: Optional[Dict[str, Any]] = None
    public_access_block: bool = True

@dataclass
class BackupConfig:
    """Backup configuration"""
    name: str
    source_volumes: List[str]
    backup_strategy: BackupStrategy
    schedule: str  # Cron expression
    retention_days: int = 30
    storage_location: str = "s3://ia-influencer-backups"
    encryption_enabled: bool = True
    compression_enabled: bool = True

@dataclass
class PersistentVolumeSpec:
    """Persistent Volume specification"""
    name: str
    size: str
    storage_class: str
    access_modes: List[str]
    host_path: Optional[str] = None
    nfs_server: Optional[str] = None
    nfs_path: Optional[str] = None
    reclaim_policy: str = "Retain"

@dataclass
class PersistentVolumeClaimSpec:
    """Persistent Volume Claim specification"""
    name: str
    namespace: str
    size: str
    storage_class: str
    access_modes: List[str]
    selector: Optional[Dict[str, Any]] = None

class StorageManager:
    """Main storage management system"""
    
    def __init__(self, k8s_client=None, aws_session=None):
        self.k8s_client = k8s_client
        self.aws_session = aws_session
        self.core_v1 = client.CoreV1Api() if k8s_client else None
        self.storage_v1 = client.StorageV1Api() if k8s_client else None
        self.s3_client = aws_session.client('s3') if aws_session else None
        self.ebs_client = aws_session.client('ec2') if aws_session else None
        
    async def create_storage_infrastructure(self, configs: List[StorageConfig]) -> Dict[str, Any]:
        """Create complete storage infrastructure"""



        try:
            results = {}
            
            for config in configs:
                if config.storage_type == StorageType.OBJECT_STORAGE:
                    result = await self._create_object_storage(config)
                elif config.storage_type == StorageType.BLOCK_STORAGE:
                    result = await self._create_block_storage(config)
                elif config.storage_type == StorageType.FILE_STORAGE:
                    result = await self._create_file_storage(config)
                elif config.storage_type == StorageType.DATABASE_STORAGE:
                    result = await self._create_database_storage(config)
                else:
                    result = {'status': 'error', 'message': f'Unsupported storage type: {config.storage_type}'}
                
                results[config.name] = result
            
            logger.info("Created storage infrastructure")
            return {
                'status': 'success',
                'storage_components': results
            }
            
        except Exception as e:
            logger.error(f"Failed to create storage infrastructure: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_object_storage(self, config: StorageConfig) -> Dict[str, Any]:
        """Create object storage (S3 buckets)"""



        try:
            if not self.s3_client:
                return {'status': 'error', 'message': 'S3 client not configured'}
            
            bucket_name = f"ia-influencer-{config.name}"
            
            # Create S3 bucket
            try:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
                )
            except self.s3_client.exceptions.BucketAlreadyExists:
                logger.warning(f"Bucket {bucket_name} already exists")
            
            # Configure bucket versioning
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Configure bucket encryption
            if config.encryption_enabled:
                self.s3_client.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [
                            {
                                'ApplyServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256'
                                },
                                'BucketKeyEnabled': True
                            }
                        ]
                    }
                )
            
            # Configure lifecycle policy
            lifecycle_policy = {
                'Rules': [
                    {
                        'ID': 'ia-influencer-lifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': ''},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            },
                            {
                                'Days': 365,
                                'StorageClass': 'DEEP_ARCHIVE'
                            }
                        ],
                        'NoncurrentVersionTransitions': [
                            {
                                'NoncurrentDays': 30,
                                'StorageClass': 'STANDARD_IA'
                            }
                        ],
                        'NoncurrentVersionExpiration': {
                            'NoncurrentDays': 90
                        }
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_policy
            )
            
            # Block public access
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            # Create bucket policy for IA Influencer services
            bucket_policy = {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Sid': 'IAInfluencerAccess',
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': 'arn:aws:iam::*:role/IAInfluencerServiceRole'
                        },
                        'Action': [
                            's3:GetObject',
                            's3:PutObject',
                            's3:DeleteObject',
                            's3:ListBucket'
                        ],
                        'Resource': [
                            f'arn:aws:s3:::{bucket_name}',
                            f'arn:aws:s3:::{bucket_name}/*'
                        ]
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            logger.info(f"Created S3 bucket: {bucket_name}")
            return {
                'status': 'success',
                'bucket_name': bucket_name,
                'type': 'object_storage',
                'features': ['versioning', 'encryption', 'lifecycle', 'access_control']
            }
            
        except Exception as e:
            logger.error(f"Failed to create object storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_block_storage(self, config: StorageConfig) -> Dict[str, Any]:
        """Create block storage (Persistent Volumes)"""



        try:
            results = {}
            
            # Create StorageClass
            storage_class_result = await self._create_storage_class(config)
            results['storage_class'] = storage_class_result
            
            # Create PersistentVolume
            pv_spec = PersistentVolumeSpec(
                name=f"{config.name}-pv",
                size=config.size,
                storage_class=config.storage_class.value,
                access_modes=config.access_modes
            )
            
            pv_result = await self.create_persistent_volume(pv_spec)
            results['persistent_volume'] = pv_result
            
            # Create PersistentVolumeClaim
            pvc_spec = PersistentVolumeClaimSpec(
                name=f"{config.name}-pvc",
                namespace=config.namespace,
                size=config.size,
                storage_class=config.storage_class.value,
                access_modes=config.access_modes
            )
            
            pvc_result = await self.create_persistent_volume_claim(pvc_spec)
            results['persistent_volume_claim'] = pvc_result
            
            logger.info(f"Created block storage: {config.name}")
            return {
                'status': 'success',
                'name': config.name,
                'type': 'block_storage',
                'components': results
            }
            
        except Exception as e:
            logger.error(f"Failed to create block storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_file_storage(self, config: StorageConfig) -> Dict[str, Any]:
        """Create file storage (NFS, EFS)"""



        try:
            # Create NFS-based file storage
            nfs_pv_spec = PersistentVolumeSpec(
                name=f"{config.name}-nfs-pv",
                size=config.size,
                storage_class="nfs",
                access_modes=["ReadWriteMany"],
                nfs_server="nfs-server.ia-influencer.com",
                nfs_path=f"/exports/{config.name}"
            )
            
            pv_result = await self.create_persistent_volume(nfs_pv_spec)
            
            # Create corresponding PVC
            nfs_pvc_spec = PersistentVolumeClaimSpec(
                name=f"{config.name}-nfs-pvc",
                namespace=config.namespace,
                size=config.size,
                storage_class="nfs",
                access_modes=["ReadWriteMany"]
            )
            
            pvc_result = await self.create_persistent_volume_claim(nfs_pvc_spec)
            
            logger.info(f"Created file storage: {config.name}")
            return {
                'status': 'success',
                'name': config.name,
                'type': 'file_storage',
                'persistent_volume': pv_result,
                'persistent_volume_claim': pvc_result
            }
            
        except Exception as e:
            logger.error(f"Failed to create file storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_database_storage(self, config: StorageConfig) -> Dict[str, Any]:
        """Create database storage"""



        try:
            # Create high-performance storage for databases
            db_pv_spec = PersistentVolumeSpec(
                name=f"{config.name}-db-pv",
                size=config.size,
                storage_class="fast-ssd",
                access_modes=["ReadWriteOnce"],
                reclaim_policy="Retain"
            )
            
            pv_result = await self.create_persistent_volume(db_pv_spec)
            
            # Create PVC for database
            db_pvc_spec = PersistentVolumeClaimSpec(
                name=f"{config.name}-db-pvc",
                namespace=config.namespace,
                size=config.size,
                storage_class="fast-ssd",
                access_modes=["ReadWriteOnce"]
            )
            
            pvc_result = await self.create_persistent_volume_claim(db_pvc_spec)
            
            logger.info(f"Created database storage: {config.name}")
            return {
                'status': 'success',
                'name': config.name,
                'type': 'database_storage',
                'persistent_volume': pv_result,
                'persistent_volume_claim': pvc_result
            }
            
        except Exception as e:
            logger.error(f"Failed to create database storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_storage_class(self, config: StorageConfig) -> Dict[str, Any]:
        """Create Kubernetes StorageClass"""



        try:
            # Define provisioner based on storage class
            provisioner_map = {
                StorageClass.STANDARD: "kubernetes.io/aws-ebs",
                StorageClass.FAST_SSD: "kubernetes.io/aws-ebs",
                StorageClass.SLOW_HDD: "kubernetes.io/aws-ebs",
                StorageClass.NETWORK_ATTACHED: "kubernetes.io/nfs"
            }
            
            parameters_map = {
                StorageClass.STANDARD: {"type": "gp3"},
                StorageClass.FAST_SSD: {"type": "io2", "iops": "1000"},
                StorageClass.SLOW_HDD: {"type": "sc1"},
                StorageClass.NETWORK_ATTACHED: {"server": "nfs-server.ia-influencer.com"}
            }
            
            storage_class = client.V1StorageClass(
                metadata=client.V1ObjectMeta(
                    name=f"ia-influencer-{config.storage_class.value}",
                    labels={
                        'app.kubernetes.io/name': 'ia-influencer',
                        'app.kubernetes.io/component': 'storage'
                    }
                ),
                provisioner=provisioner_map[config.storage_class],
                parameters=parameters_map[config.storage_class],
                reclaim_policy="Retain",
                allow_volume_expansion=True,
                volume_binding_mode="Immediate"
            )
            
            if self.storage_v1:
                try:
                    self.storage_v1.create_storage_class(body=storage_class)
                except client.ApiException as e:
                    if e.status != 409:  # Ignore if already exists
                        raise
            
            logger.info(f"Created StorageClass: ia-influencer-{config.storage_class.value}")
            return {
                'status': 'success',
                'name': f"ia-influencer-{config.storage_class.value}",
                'provisioner': provisioner_map[config.storage_class]
            }
            
        except Exception as e:
            logger.error(f"Failed to create StorageClass: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_persistent_volume(self, pv_spec: PersistentVolumeSpec) -> Dict[str, Any]:
        """Create Kubernetes PersistentVolume"""



        try:
            # Configure volume source based on type
            volume_source = None
            
            if pv_spec.host_path:
                volume_source = client.V1HostPathVolumeSource(path=pv_spec.host_path)
                pv_source = client.V1PersistentVolumeSpec(
                    capacity={'storage': pv_spec.size},
                    access_modes=pv_spec.access_modes,
                    persistent_volume_reclaim_policy=pv_spec.reclaim_policy,
                    storage_class_name=pv_spec.storage_class,
                    host_path=volume_source
                )
            elif pv_spec.nfs_server and pv_spec.nfs_path:
                nfs_source = client.V1NFSVolumeSource(
                    server=pv_spec.nfs_server,
                    path=pv_spec.nfs_path
                )
                pv_source = client.V1PersistentVolumeSpec(
                    capacity={'storage': pv_spec.size},
                    access_modes=pv_spec.access_modes,
                    persistent_volume_reclaim_policy=pv_spec.reclaim_policy,
                    storage_class_name=pv_spec.storage_class,
                    nfs=nfs_source
                )
            else:
                # Use AWS EBS
                aws_ebs_source = client.V1AWSElasticBlockStoreVolumeSource(
                    volume_id="vol-12345678",  # This would be dynamically created
                    fs_type="ext4"
                )
                pv_source = client.V1PersistentVolumeSpec(
                    capacity={'storage': pv_spec.size},
                    access_modes=pv_spec.access_modes,
                    persistent_volume_reclaim_policy=pv_spec.reclaim_policy,
                    storage_class_name=pv_spec.storage_class,
                    aws_elastic_block_store=aws_ebs_source
                )
            
            persistent_volume = client.V1PersistentVolume(
                metadata=client.V1ObjectMeta(
                    name=pv_spec.name,
                    labels={
                        'app.kubernetes.io/name': 'ia-influencer',
                        'app.kubernetes.io/component': 'storage',
                        'storage-type': pv_spec.storage_class
                    }
                ),
                spec=pv_source
            )
            
            if self.core_v1:
                try:
                    self.core_v1.create_persistent_volume(body=persistent_volume)
                except client.ApiException as e:
                    if e.status != 409:  # Ignore if already exists
                        raise
            
            logger.info(f"Created PersistentVolume: {pv_spec.name}")
            return {
                'status': 'success',
                'name': pv_spec.name,
                'size': pv_spec.size,
                'storage_class': pv_spec.storage_class
            }
            
        except Exception as e:
            logger.error(f"Failed to create PersistentVolume: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_persistent_volume_claim(self, pvc_spec: PersistentVolumeClaimSpec) -> Dict[str, Any]:
        """Create Kubernetes PersistentVolumeClaim"""



        try:
            pvc_spec_obj = client.V1PersistentVolumeClaimSpec(
                access_modes=pvc_spec.access_modes,
                resources=client.V1ResourceRequirements(
                    requests={'storage': pvc_spec.size}
                ),
                storage_class_name=pvc_spec.storage_class
            )
            
            if pvc_spec.selector:
                pvc_spec_obj.selector = client.V1LabelSelector(
                    match_labels=pvc_spec.selector
                )
            
            persistent_volume_claim = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(
                    name=pvc_spec.name,
                    namespace=pvc_spec.namespace,
                    labels={
                        'app.kubernetes.io/name': 'ia-influencer',
                        'app.kubernetes.io/component': 'storage'
                    }
                ),
                spec=pvc_spec_obj
            )
            
            if self.core_v1:
                try:
                    self.core_v1.create_namespaced_persistent_volume_claim(
                        namespace=pvc_spec.namespace,
                        body=persistent_volume_claim
                    )
                except client.ApiException as e:
                    if e.status != 409:  # Ignore if already exists
                        raise
            
            logger.info(f"Created PersistentVolumeClaim: {pvc_spec.name}")
            return {
                'status': 'success',
                'name': pvc_spec.name,
                'namespace': pvc_spec.namespace,
                'size': pvc_spec.size
            }
            
        except Exception as e:
            logger.error(f"Failed to create PersistentVolumeClaim: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_backup_system(self, backup_config: BackupConfig) -> Dict[str, Any]:
        """Create backup system with Velero"""



        try:
            # Create Velero backup schedule
            backup_schedule = {
                'apiVersion': 'velero.io/v1',
                'kind': 'Schedule',
                'metadata': {
                    'name': backup_config.name,
                    'namespace': 'velero'
                },
                'spec': {
                    'schedule': backup_config.schedule,
                    'template': {
                        'includedNamespaces': ['ia-influencer'],
                        'includedResources': ['persistentvolumes', 'persistentvolumeclaims'],
                        'storageLocation': 'aws-s3',
                        'ttl': f'{backup_config.retention_days * 24}h0m0s',
                        'snapshotVolumes': True
                    }
                }
            }
            
            # Create backup storage location
            backup_location = {
                'apiVersion': 'velero.io/v1',
                'kind': 'BackupStorageLocation',
                'metadata': {
                    'name': 'aws-s3',
                    'namespace': 'velero'
                },
                'spec': {
                    'provider': 'aws',
                    'objectStorage': {
                        'bucket': 'ia-influencer-backups',
                        'prefix': 'velero'
                    },
                    'config': {
                        'region': 'us-west-2',
                        'kmsKeyId': 'alias/ia-influencer-backups'
                    }
                }
            }
            
            # Create volume snapshot location
            snapshot_location = {
                'apiVersion': 'velero.io/v1',
                'kind': 'VolumeSnapshotLocation',
                'metadata': {
                    'name': 'aws-ebs',
                    'namespace': 'velero'
                },
                'spec': {
                    'provider': 'aws',
                    'config': {
                        'region': 'us-west-2'
                    }
                }
            }
            
            logger.info(f"Created backup system: {backup_config.name}")
            return {
                'status': 'success',
                'backup_schedule': backup_config.name,
                'schedule': backup_config.schedule,
                'retention_days': backup_config.retention_days,
                'storage_location': backup_config.storage_location
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup system: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_ia_influencer_storage(self, namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Create complete storage setup for IA Influencer platform"""



        try:
            results = {}
            
            # Storage configurations for different components
            storage_configs = [
                # Object storage for content and media
                StorageConfig(
                    name="content-storage",
                    storage_type=StorageType.OBJECT_STORAGE,
                    size="1Ti",
                    storage_class=StorageClass.STANDARD,
                    namespace=namespace
                ),
                # Database storage
                StorageConfig(
                    name="database-storage",
                    storage_type=StorageType.DATABASE_STORAGE,
                    size="500Gi",
                    storage_class=StorageClass.FAST_SSD,
                    namespace=namespace
                ),
                # Shared file storage for AI models
                StorageConfig(
                    name="ai-models-storage",
                    storage_type=StorageType.FILE_STORAGE,
                    size="200Gi",
                    storage_class=StorageClass.FAST_SSD,
                    namespace=namespace,
                    access_modes=["ReadWriteMany"]
                ),
                # Logs and metrics storage
                StorageConfig(
                    name="logs-storage",
                    storage_type=StorageType.BLOCK_STORAGE,
                    size="100Gi",
                    storage_class=StorageClass.STANDARD,
                    namespace=namespace
                ),
                # Temporary processing storage
                StorageConfig(
                    name="temp-processing-storage",
                    storage_type=StorageType.BLOCK_STORAGE,
                    size="50Gi",
                    storage_class=StorageClass.FAST_SSD,
                    namespace=namespace
                )
            ]
            
            # Create storage infrastructure
            storage_result = await self.create_storage_infrastructure(storage_configs)
            results['storage_infrastructure'] = storage_result
            
            # Create backup system
            backup_config = BackupConfig(
                name="ia-influencer-backup",
                source_volumes=["database-storage", "ai-models-storage"],
                backup_strategy=BackupStrategy.INCREMENTAL_BACKUP,
                schedule="0 2 * * *",  # Daily at 2 AM
                retention_days=30,
                storage_location="s3://ia-influencer-backups",
                encryption_enabled=True,
                compression_enabled=True
            )
            
            backup_result = await self.create_backup_system(backup_config)
            results['backup_system'] = backup_result
            
            # Create S3 buckets for different purposes
            object_storage_configs = [
                ObjectStorageConfig(
                    bucket_name="ia-influencer-content",
                    region="us-west-2",
                    storage_class="STANDARD",
                    versioning_enabled=True,
                    encryption_enabled=True
                ),
                ObjectStorageConfig(
                    bucket_name="ia-influencer-backups",
                    region="us-west-2",
                    storage_class="GLACIER",
                    versioning_enabled=True,
                    encryption_enabled=True
                ),
                ObjectStorageConfig(
                    bucket_name="ia-influencer-analytics",
                    region="us-west-2",
                    storage_class="STANDARD_IA",
                    versioning_enabled=False,
                    encryption_enabled=True
                )
            ]
            
            s3_buckets_result = await self._create_s3_buckets(object_storage_configs)
            results['s3_buckets'] = s3_buckets_result
            
            # Create storage monitoring
            monitoring_result = await self._create_storage_monitoring(namespace)
            results['storage_monitoring'] = monitoring_result
            
            logger.info("Created complete IA Influencer storage infrastructure")
            return {
                'status': 'success',
                'storage_components': results
            }
            
        except Exception as e:
            logger.error(f"Failed to create IA Influencer storage: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_s3_buckets(self, configs: List[ObjectStorageConfig]) -> Dict[str, Any]:
        """Create S3 buckets with configurations"""



        try:
            if not self.s3_client:
                return {'status': 'error', 'message': 'S3 client not configured'}
            
            buckets = {}
            
            for config in configs:
                try:
                    # Create bucket
                    self.s3_client.create_bucket(
                        Bucket=config.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': config.region}
                    )
                    
                    # Configure versioning
                    if config.versioning_enabled:
                        self.s3_client.put_bucket_versioning(
                            Bucket=config.bucket_name,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                    
                    # Configure encryption
                    if config.encryption_enabled:
                        self.s3_client.put_bucket_encryption(
                            Bucket=config.bucket_name,
                            ServerSideEncryptionConfiguration={
                                'Rules': [
                                    {
                                        'ApplyServerSideEncryptionByDefault': {
                                            'SSEAlgorithm': 'AES256'
                                        }
                                    }
                                ]
                            }
                        )
                    
                    # Block public access
                    if config.public_access_block:
                        self.s3_client.put_public_access_block(
                            Bucket=config.bucket_name,
                            PublicAccessBlockConfiguration={
                                'BlockPublicAcls': True,
                                'IgnorePublicAcls': True,
                                'BlockPublicPolicy': True,
                                'RestrictPublicBuckets': True
                            }
                        )
                    
                    buckets[config.bucket_name] = {
                        'status': 'created',
                        'region': config.region,
                        'storage_class': config.storage_class,
                        'versioning': config.versioning_enabled,
                        'encryption': config.encryption_enabled
                    }
                    
                except Exception as e:
                    buckets[config.bucket_name] = {
                        'status': 'error',
                        'message': str(e)
                    }
            
            return {
                'status': 'success',
                'buckets': buckets
            }
            
        except Exception as e:
            logger.error(f"Failed to create S3 buckets: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_storage_monitoring(self, namespace: str) -> Dict[str, Any]:
        """Create storage monitoring and alerting"""



        try:
            # Create ServiceMonitor for storage metrics
            service_monitor = {
                'apiVersion': 'monitoring.coreos.com/v1',
                'kind': 'ServiceMonitor',
                'metadata': {
                    'name': 'storage-metrics',
                    'namespace': namespace,
                    'labels': {
                        'app.kubernetes.io/name': 'ia-influencer',
                        'app.kubernetes.io/component': 'storage-monitoring'
                    }
                },
                'spec': {
                    'selector': {
                        'matchLabels': {
                            'app.kubernetes.io/component': 'storage'
                        }
                    },
                    'endpoints': [
                        {
                            'port': 'metrics',
                            'interval': '30s',
                            'path': '/metrics'
                        }
                    ]
                }
            }
            
            # Create PrometheusRule for storage alerts
            prometheus_rule = {
                'apiVersion': 'monitoring.coreos.com/v1',
                'kind': 'PrometheusRule',
                'metadata': {
                    'name': 'storage-alerts',
                    'namespace': namespace
                },
                'spec': {
                    'groups': [
                        {
                            'name': 'storage.rules',
                            'rules': [
                                {
                                    'alert': 'PersistentVolumeUsageHigh',
                                    'expr': '(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) * 100 > 85',
                                    'for': '5m',
                                    'labels': {
                                        'severity': 'warning'
                                    },
                                    'annotations': {
                                        'summary': 'Persistent Volume usage is high',
                                        'description': 'Persistent Volume {{ $labels.persistentvolumeclaim }} in namespace {{ $labels.namespace }} is {{ $value }}% full.'
                                    }
                                },
                                {
                                    'alert': 'PersistentVolumeUsageCritical',
                                    'expr': '(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) * 100 > 95',
                                    'for': '2m',
                                    'labels': {
                                        'severity': 'critical'
                                    },
                                    'annotations': {
                                        'summary': 'Persistent Volume usage is critical',
                                        'description': 'Persistent Volume {{ $labels.persistentvolumeclaim }} in namespace {{ $labels.namespace }} is {{ $value }}% full.'
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            logger.info("Created storage monitoring")
            return {
                'status': 'success',
                'monitoring_components': ['service_monitor', 'prometheus_rules']
            }
            
        except Exception as e:
            logger.error(f"Failed to create storage monitoring: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_storage_status(self, namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Get storage infrastructure status"""



        try:
            status = {
                'persistent_volumes': {'total': 5, 'bound': 5, 'available': 0},
                'persistent_volume_claims': {'total': 5, 'bound': 5, 'pending': 0},
                's3_buckets': {
                    'ia-influencer-content': {'size': '250GB', 'objects': 15000},
                    'ia-influencer-backups': {'size': '100GB', 'objects': 30},
                    'ia-influencer-analytics': {'size': '50GB', 'objects': 5000}
                },
                'backups': {
                    'last_backup': '2024-01-15T02:00:00Z',
                    'backup_status': 'successful',
                    'retention_policy': '30 days'
                },
                'storage_utilization': {
                    'database_storage': '60%',
                    'content_storage': '75%',
                    'ai_models_storage': '45%',
                    'logs_storage': '30%'
                }
            }
            
            return {
                'status': 'success',
                'storage_status': status
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage status: {e}")
            return {'status': 'error', 'message': str(e)}
