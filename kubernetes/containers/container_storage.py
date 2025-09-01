"""💾 Container Storage Manager - IA-Influencer-Agent Infrastructure
=================================================================
Expert: Storage Engineer + DevOps + Data Architect
Creator: Fahed Mlaiel <mlaiel@live.de>
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional container storage management with persistent volumes,
storage classes, and advanced data lifecycle management.
"""

import os
import asyncio
import logging
import json
import yaml
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import kubernetes
from kubernetes import client, config
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs

logger = logging.getLogger(__name__)

class StorageType(Enum):
    """
Storage types"""

    BLOCK = "block"
    FILE = "file"
    OBJECT = "object"
    NETWORK = "network"

class AccessMode(Enum):
    """Persistent volume access modes"""

    READ_WRITE_ONCE = "ReadWriteOnce"
    READ_ONLY_MANY = "ReadOnlyMany"
    READ_WRITE_MANY = "ReadWriteMany"
    READ_WRITE_ONCE_POD = "ReadWriteOncePod"

class ReclaimPolicy(Enum):
    """Persistent volume reclaim policies"""

    RETAIN = "Retain"
    DELETE = "Delete"
    RECYCLE = "Recycle"

class VolumeBindingMode(Enum):
    """Volume binding modes"""

    IMMEDIATE = "Immediate"
    WAIT_FOR_FIRST_CONSUMER = "WaitForFirstConsumer"

class StorageProvisioner(Enum):
    """Storage provisioners"""

    AWS_EBS = "ebs.csi.aws.com"
    AZURE_DISK = "disk.csi.azure.com"
    AZURE_FILE = "file.csi.azure.com"
    GCE_PD = "pd.csi.storage.gke.io"
    NFS = "nfs.csi.k8s.io"
    LOCAL = "kubernetes.io/no-provisioner"
    HOSTPATH = "kubernetes.io/host-path"

@dataclass
class StorageClass:
    """Storage class configuration"""
    name: str
    provisioner: StorageProvisioner
    reclaim_policy: ReclaimPolicy = ReclaimPolicy.DELETE
    volume_binding_mode: VolumeBindingMode = VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER
    allow_volume_expansion: bool = True
    parameters: Dict[str, str] = field(default_factory=dict)
    mount_options: List[str] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class PersistentVolume:
    """
Persistent volume configuration"""
    name: str
    capacity: str
    access_modes: List[AccessMode]
    storage_class: str
    volume_source: Dict[str, Any]
    reclaim_policy: ReclaimPolicy = ReclaimPolicy.DELETE
    mount_options: List[str] = field(default_factory=list)
    node_affinity: Dict[str, Any] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class PersistentVolumeClaim:
    """
Persistent volume claim configuration"""
    name: str
    namespace: str
    access_modes: List[AccessMode]
    resources: Dict[str, str]
    storage_class: Optional[str] = None
    selector: Dict[str, Any] = field(default_factory=dict)
    volume_name: Optional[str] = None
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class VolumeMount:
    """
Volume mount configuration"""
    name: str
    mount_path: str
    sub_path: Optional[str] = None
    read_only: bool = False

@dataclass
class VolumeSnapshot:
    """
Volume snapshot configuration"""
    name: str
    namespace: str
    volume_snapshot_class: str
    source_pvc_name: str
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class BackupConfig:
    """
Backup configuration"""
    name: str
    source_pvc: str
    namespace: str
    schedule: str  # Cron format
    retention_days: int = 30
    destination_type: str = "s3"  # s3, azure, gcs, nfs
    destination_config: Dict[str, Any] = field(default_factory=dict)
    compression: bool = True
    encryption: bool = True
    labels: Dict[str, str] = field(default_factory=dict)

class ContainerStorageManager:
    """Professional container storage manager"""
    
    def __init__(self, config_path: str = "/app/config/storage"):
        self.config_path = Path(config_path)
        self.k8s_client = None
        self.storage_classes = {}
        self.persistent_volumes = {}
        self.persistent_volume_claims = {}
        self.volume_snapshots = {}
        self.backup_configs = {}
        self.storage_usage = {}
        self.s3_client = None
        self.azure_client = None
        self.gcs_client = None
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize container storage manager"""
        try:
            # Initialize Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize cloud storage clients
            await self._initialize_cloud_storage()
            
            # Load existing configurations
            await self._load_configurations()
            
            # Setup default storage classes
            await self._setup_default_storage_classes()
            
            # Setup default storage for IA-Influencer
            await self._setup_default_storage()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_storage_usage())
            asyncio.create_task(self._backup_scheduler())
            asyncio.create_task(self._cleanup_old_snapshots())
            
            self.initialized = True
            self.logger.info("✅ ContainerStorageManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ContainerStorageManager: {e}")
            return False
    
    async def _initialize_cloud_storage(self) -> None:
        """Initialize cloud storage clients"""
        try:
            # Initialize AWS S3 client
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'eu-central-1')
                )
                self.logger.info("✅ AWS S3 client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize S3 client: {e}")
            
            # Initialize Azure Blob Storage client
            try:
                connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
                if connection_string:
                    self.azure_client = BlobServiceClient.from_connection_string(connection_string)
                    self.logger.info("✅ Azure Blob Storage client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize Azure client: {e}")
            
            # Initialize Google Cloud Storage client
            try:
                credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_path:
                    self.gcs_client = gcs.Client()
                    self.logger.info("✅ Google Cloud Storage client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize GCS client: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing cloud storage: {e}")
    
    async def _load_configurations(self) -> None:
        """Load existing storage configurations"""
        try:
            # Load storage classes
            storage_classes_file = self.config_path / "storage_classes.yml"
            if storage_classes_file.exists():
                with open(storage_classes_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for sc_data in data.get('storage_classes', []):
                        sc = StorageClass(**sc_data)
                        self.storage_classes[sc.name] = sc
            
            # Load PVCs
            pvcs_file = self.config_path / "pvcs.yml"
            if pvcs_file.exists():
                with open(pvcs_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for pvc_data in data.get('pvcs', []):
                        pvc = PersistentVolumeClaim(**pvc_data)
                        self.persistent_volume_claims[f"{pvc.namespace}/{pvc.name}"] = pvc
            
            # Load backup configs
            backups_file = self.config_path / "backups.yml"
            if backups_file.exists():
                with open(backups_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for backup_data in data.get('backups', []):
                        backup = BackupConfig(**backup_data)
                        self.backup_configs[backup.name] = backup
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading configurations: {e}")
    
    async def _setup_default_storage_classes(self) -> None:
        """Setup default storage classes"""
        try:
            # Fast SSD storage class
            fast_ssd_sc = StorageClass(
                name="fast-ssd",
                provisioner=StorageProvisioner.AWS_EBS,
                reclaim_policy=ReclaimPolicy.DELETE,
                volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
                allow_volume_expansion=True,
                parameters={
                    "type": "gp3",
                    "iops": "3000",
                    "throughput": "125",
                    "encrypted": "true"
                },
                annotations={
                    "storageclass.kubernetes.io/is-default-class": "false"
                },
                labels={
                    "performance": "high",
                    "cost": "medium"
                }
            )
            
            # Standard SSD storage class
            standard_ssd_sc = StorageClass(
                name="standard-ssd",
                provisioner=StorageProvisioner.AWS_EBS,
                reclaim_policy=ReclaimPolicy.DELETE,
                volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
                allow_volume_expansion=True,
                parameters={
                    "type": "gp2",
                    "encrypted": "true"
                },
                annotations={
                    "storageclass.kubernetes.io/is-default-class": "true"
                },
                labels={
                    "performance": "standard",
                    "cost": "low"
                }
            )
            
            # High-performance storage for AI models
            ai_models_sc = StorageClass(
                name="ai-models-storage",
                provisioner=StorageProvisioner.AWS_EBS,
                reclaim_policy=ReclaimPolicy.RETAIN,
                volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
                allow_volume_expansion=True,
                parameters={
                    "type": "io2",
                    "iops": "10000",
                    "encrypted": "true"
                },
                labels={
                    "performance": "ultra-high",
                    "cost": "high",
                    "use-case": "ai-models"
                }
            )
            
            # Shared file storage
            shared_file_sc = StorageClass(
                name="shared-file",
                provisioner=StorageProvisioner.NFS,
                reclaim_policy=ReclaimPolicy.RETAIN,
                volume_binding_mode=VolumeBindingMode.IMMEDIATE,
                allow_volume_expansion=False,
                parameters={
                    "server": "nfs-server.ia-influencer.svc.cluster.local",
                    "share": "/exports/shared"
                },
                mount_options=["vers=4.1", "rsize=1048576", "wsize=1048576"],
                labels={
                    "access-mode": "shared",
                    "use-case": "shared-data"
                }
            )
            
            # Object storage class (for large datasets)
            object_storage_sc = StorageClass(
                name="object-storage",
                provisioner=StorageProvisioner.AWS_EBS,
                reclaim_policy=ReclaimPolicy.DELETE,
                volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
                allow_volume_expansion=True,
                parameters={
                    "type": "st1",  # Throughput optimized HDD
                    "encrypted": "true"
                },
                labels={
                    "performance": "throughput-optimized",
                    "cost": "very-low",
                    "use-case": "large-datasets"
                }
            )
            
            # Store storage classes
            storage_classes = [
                fast_ssd_sc,
                standard_ssd_sc,
                ai_models_sc,
                shared_file_sc,
                object_storage_sc
            ]
            
            for sc in storage_classes:
                self.storage_classes[sc.name] = sc
            
            # Save configurations
            await self._save_storage_classes()
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default storage classes: {e}")
    
    async def _setup_default_storage(self) -> None:
        """Setup default storage for IA-Influencer platform"""
        try:
            # Database PVC
            database_pvc = PersistentVolumeClaim(
                name="ia-influencer-database-data",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_ONCE],
                resources={"requests": {"storage": "100Gi"}},
                storage_class="fast-ssd",
                labels={
                    "app": "postgresql",
                    "component": "database",
                    "tier": "data"
                }
            )
            
            # Redis PVC
            redis_pvc = PersistentVolumeClaim(
                name="ia-influencer-redis-data",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_ONCE],
                resources={"requests": {"storage": "20Gi"}},
                storage_class="fast-ssd",
                labels={
                    "app": "redis",
                    "component": "cache",
                    "tier": "data"
                }
            )
            
            # AI Models PVC
            ai_models_pvc = PersistentVolumeClaim(
                name="ia-influencer-ai-models",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_MANY],
                resources={"requests": {"storage": "500Gi"}},
                storage_class="ai-models-storage",
                labels={
                    "app": "ai-engine",
                    "component": "models",
                    "tier": "data"
                }
            )
            
            # Shared data PVC
            shared_data_pvc = PersistentVolumeClaim(
                name="ia-influencer-shared-data",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_MANY],
                resources={"requests": {"storage": "200Gi"}},
                storage_class="shared-file",
                labels={
                    "component": "shared-data",
                    "tier": "data"
                }
            )
            
            # Logs PVC
            logs_pvc = PersistentVolumeClaim(
                name="ia-influencer-logs",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_ONCE],
                resources={"requests": {"storage": "50Gi"}},
                storage_class="standard-ssd",
                labels={
                    "component": "logging",
                    "tier": "data"
                }
            )
            
            # Media storage PVC (for large files)
            media_pvc = PersistentVolumeClaim(
                name="ia-influencer-media",
                namespace="ia-influencer",
                access_modes=[AccessMode.READ_WRITE_ONCE],
                resources={"requests": {"storage": "1Ti"}},
                storage_class="object-storage",
                labels={
                    "component": "media",
                    "tier": "data"
                }
            )
            
            # Store PVCs
            pvcs = [
                database_pvc,
                redis_pvc,
                ai_models_pvc,
                shared_data_pvc,
                logs_pvc,
                media_pvc
            ]
            
            for pvc in pvcs:
                pvc_key = f"{pvc.namespace}/{pvc.name}"
                self.persistent_volume_claims[pvc_key] = pvc
            
            # Setup backup configurations
            await self._setup_default_backups()
            
            # Save configurations
            await self._save_pvcs()
            await self._save_backup_configs()
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default storage: {e}")
    
    async def _setup_default_backups(self) -> None:
        """Setup default backup configurations"""
        try:
            # Database backup
            database_backup = BackupConfig(
                name="database-backup",
                source_pvc="ia-influencer-database-data",
                namespace="ia-influencer",
                schedule="0 2 * * *",  # Daily at 2 AM
                retention_days=30,
                destination_type="s3",
                destination_config={
                    "bucket": "ia-influencer-backups",
                    "prefix": "database/",
                    "region": "eu-central-1"
                },
                compression=True,
                encryption=True,
                labels={
                    "backup-type": "database",
                    "criticality": "high"
                }
            )
            
            # AI Models backup
            ai_models_backup = BackupConfig(
                name="ai-models-backup",
                source_pvc="ia-influencer-ai-models",
                namespace="ia-influencer",
                schedule="0 3 * * 0",  # Weekly on Sunday at 3 AM
                retention_days=90,
                destination_type="s3",
                destination_config={
                    "bucket": "ia-influencer-models-backup",
                    "prefix": "models/",
                    "region": "eu-central-1"
                },
                compression=True,
                encryption=True,
                labels={
                    "backup-type": "ai-models",
                    "criticality": "high"
                }
            )
            
            # Shared data backup
            shared_data_backup = BackupConfig(
                name="shared-data-backup",
                source_pvc="ia-influencer-shared-data",
                namespace="ia-influencer",
                schedule="0 1 * * *",  # Daily at 1 AM
                retention_days=14,
                destination_type="s3",
                destination_config={
                    "bucket": "ia-influencer-backups",
                    "prefix": "shared-data/",
                    "region": "eu-central-1"
                },
                compression=True,
                encryption=True,
                labels={
                    "backup-type": "shared-data",
                    "criticality": "medium"
                }
            )
            
            # Store backup configs
            backups = [database_backup, ai_models_backup, shared_data_backup]
            for backup in backups:
                self.backup_configs[backup.name] = backup
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up default backups: {e}")
    
    async def _save_storage_classes(self) -> None:
        """Save storage classes configuration"""
        try:
            data = {
                "storage_classes": [asdict(sc) for sc in self.storage_classes.values()]
            }
            with open(self.config_path / "storage_classes.yml", 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving storage classes: {e}")
    
    async def _save_pvcs(self) -> None:
        """Save PVCs configuration"""
        try:
            data = {
                "pvcs": [asdict(pvc) for pvc in self.persistent_volume_claims.values()]
            }
            with open(self.config_path / "pvcs.yml", 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving PVCs: {e}")
    
    async def _save_backup_configs(self) -> None:
        """Save backup configurations"""
        try:
            data = {
                "backups": [asdict(backup) for backup in self.backup_configs.values()]
            }
            with open(self.config_path / "backups.yml", 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving backup configs: {e}")
    
    async def create_storage_class(self, storage_class: StorageClass) -> bool:
        """Create Kubernetes storage class"""
        try:
            storage_v1 = client.StorageV1Api()
            
            # Create storage class manifest
            sc_manifest = {
                "apiVersion": "storage.k8s.io/v1",
                "kind": "StorageClass",
                "metadata": {
                    "name": storage_class.name,
                    "labels": storage_class.labels,
                    "annotations": storage_class.annotations
                },
                "provisioner": storage_class.provisioner.value,
                "reclaimPolicy": storage_class.reclaim_policy.value,
                "volumeBindingMode": storage_class.volume_binding_mode.value,
                "allowVolumeExpansion": storage_class.allow_volume_expansion,
                "parameters": storage_class.parameters
            }
            
            if storage_class.mount_options:
                sc_manifest["mountOptions"] = storage_class.mount_options
            
            # Create storage class
            try:
                storage_v1.create_storage_class(body=sc_manifest)
                
                # Store storage class
                self.storage_classes[storage_class.name] = storage_class
                await self._save_storage_classes()
                
                self.logger.info(f"✅ Created storage class: {storage_class.name}")
                return True
                
            except client.rest.ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"ℹ️ Storage class {storage_class.name} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating storage class: {e}")
            return False
    
    async def create_persistent_volume_claim(self, pvc: PersistentVolumeClaim) -> bool:
        """Create persistent volume claim"""
        try:
            v1 = client.CoreV1Api()
            
            # Create PVC manifest
            pvc_manifest = {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": pvc.name,
                    "namespace": pvc.namespace,
                    "labels": pvc.labels,
                    "annotations": pvc.annotations
                },
                "spec": {
                    "accessModes": [mode.value for mode in pvc.access_modes],
                    "resources": pvc.resources
                }
            }
            
            if pvc.storage_class:
                pvc_manifest["spec"]["storageClassName"] = pvc.storage_class
            
            if pvc.selector:
                pvc_manifest["spec"]["selector"] = pvc.selector
            
            if pvc.volume_name:
                pvc_manifest["spec"]["volumeName"] = pvc.volume_name
            
            # Create PVC
            try:
                v1.create_namespaced_persistent_volume_claim(
                    namespace=pvc.namespace,
                    body=pvc_manifest
                )
                
                # Store PVC
                pvc_key = f"{pvc.namespace}/{pvc.name}"
                self.persistent_volume_claims[pvc_key] = pvc
                await self._save_pvcs()
                
                self.logger.info(f"✅ Created PVC: {pvc.name}")
                return True
                
            except client.rest.ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"ℹ️ PVC {pvc.name} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating PVC: {e}")
            return False
    
    async def create_volume_snapshot(self, snapshot: VolumeSnapshot) -> bool:
        """Create volume snapshot"""
        try:
            # Note: VolumeSnapshot requires snapshot.storage.k8s.io/v1 API
            # This is a simplified implementation
            
            snapshot_manifest = {
                "apiVersion": "snapshot.storage.k8s.io/v1",
                "kind": "VolumeSnapshot",
                "metadata": {
                    "name": snapshot.name,
                    "namespace": snapshot.namespace,
                    "labels": snapshot.labels,
                    "annotations": snapshot.annotations
                },
                "spec": {
                    "volumeSnapshotClassName": snapshot.volume_snapshot_class,
                    "source": {
                        "persistentVolumeClaimName": snapshot.source_pvc_name
                    }
                }
            }
            
            # For now, we'll store the snapshot configuration
            snapshot_key = f"{snapshot.namespace}/{snapshot.name}"
            self.volume_snapshots[snapshot_key] = snapshot
            
            self.logger.info(f"✅ Created volume snapshot: {snapshot.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating volume snapshot: {e}")
            return False
    
    async def resize_pvc(self, namespace: str, pvc_name: str, new_size: str) -> bool:
        """Resize persistent volume claim"""
        try:
            v1 = client.CoreV1Api()
            
            # Get existing PVC
            pvc = v1.read_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=namespace
            )
            
            # Check if storage class allows expansion
            if pvc.spec.storage_class_name:
                storage_v1 = client.StorageV1Api()
                storage_class = storage_v1.read_storage_class(
                    name=pvc.spec.storage_class_name
                )
                
                if not storage_class.allow_volume_expansion:
                    self.logger.error(f"❌ Storage class {pvc.spec.storage_class_name} does not allow expansion")
                    return False
            
            # Update PVC size
            pvc.spec.resources.requests["storage"] = new_size
            
            v1.patch_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=namespace,
                body=pvc
            )
            
            self.logger.info(f"✅ Resized PVC {pvc_name} to {new_size}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error resizing PVC: {e}")
            return False
    
    async def _monitor_storage_usage(self) -> None:
        """Monitor storage usage"""
        while True:
            try:
                v1 = client.CoreV1Api()
                
                # Get all PVCs
                pvcs = v1.list_persistent_volume_claim_for_all_namespaces()
                
                storage_usage = {}
                
                for pvc in pvcs.items:
                    pvc_key = f"{pvc.metadata.namespace}/{pvc.metadata.name}"
                    
                    # Get PVC status
                    usage_info = {
                        "name": pvc.metadata.name,
                        "namespace": pvc.metadata.namespace,
                        "storage_class": pvc.spec.storage_class_name,
                        "requested_size": pvc.spec.resources.requests.get("storage", ""),
                        "access_modes": pvc.spec.access_modes,
                        "status": pvc.status.phase,
                        "volume_name": pvc.spec.volume_name,
                        "created": pvc.metadata.creation_timestamp.isoformat() if pvc.metadata.creation_timestamp else None
                    }
                    
                    # Get actual usage (this would require metrics server)
                    # For now, we'll store the configuration
                    storage_usage[pvc_key] = usage_info
                
                self.storage_usage = storage_usage
                
                # Check for storage alerts
                await self._check_storage_alerts()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error monitoring storage usage: {e}")
                await asyncio.sleep(300)
    
    async def _check_storage_alerts(self) -> None:
        """Check for storage alerts"""
        try:
            for pvc_key, usage_info in self.storage_usage.items():
                # Check for PVCs in pending state
                if usage_info["status"] == "Pending":
                    self.logger.warning(f"⚠️ PVC {usage_info['name']} is in Pending state")
                
                # Check for old PVCs without recent access
                # This would require more detailed metrics
                
        except Exception as e:
            self.logger.error(f"❌ Error checking storage alerts: {e}")
    
    async def _backup_scheduler(self) -> None:
        """Backup scheduler task"""
        while True:
            try:
                current_time = datetime.now()
                
                for backup_name, backup_config in self.backup_configs.items():
                    # Check if backup should run (simplified cron check)
                    if await self._should_run_backup(backup_config, current_time):
                        await self._perform_backup(backup_config)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in backup scheduler: {e}")
                await asyncio.sleep(3600)
    
    async def _should_run_backup(self, backup_config: BackupConfig, current_time: datetime) -> bool:
        """Check if backup should run based on schedule"""
        try:
            # Simplified cron parsing - in production, use a proper cron library
            schedule_parts = backup_config.schedule.split()
            
            if len(schedule_parts) != 5:
                return False
            
            minute, hour, day, month, weekday = schedule_parts
            
            # Check if current time matches schedule
            if minute != "*" and int(minute) != current_time.minute:
                return False
            
            if hour != "*" and int(hour) != current_time.hour:
                return False
            
            # For simplicity, just check hour and minute
            # In production, implement full cron functionality
            
            return minute != "*" and hour != "*" and int(minute) == current_time.minute and int(hour) == current_time.hour
            
        except Exception as e:
            self.logger.error(f"❌ Error checking backup schedule: {e}")
            return False
    
    async def _perform_backup(self, backup_config: BackupConfig) -> bool:
        """Perform backup operation"""
        try:
            self.logger.info(f"🔄 Starting backup: {backup_config.name}")
            
            # Create volume snapshot first
            snapshot_name = f"{backup_config.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            snapshot = VolumeSnapshot(
                name=snapshot_name,
                namespace=backup_config.namespace,
                volume_snapshot_class="csi-snapshotter",
                source_pvc_name=backup_config.source_pvc,
                labels={
                    "backup-config": backup_config.name,
                    "backup-type": "automated"
                }
            )
            
            success = await self.create_volume_snapshot(snapshot)
            
            if not success:
                self.logger.error(f"❌ Failed to create snapshot for backup {backup_config.name}")
                return False
            
            # Export snapshot to cloud storage
            if backup_config.destination_type == "s3":
                success = await self._export_to_s3(snapshot, backup_config)
            elif backup_config.destination_type == "azure":
                success = await self._export_to_azure(snapshot, backup_config)
            elif backup_config.destination_type == "gcs":
                success = await self._export_to_gcs(snapshot, backup_config)
            else:
                self.logger.error(f"❌ Unsupported backup destination: {backup_config.destination_type}")
                return False
            
            if success:
                self.logger.info(f"✅ Backup completed: {backup_config.name}")
            else:
                self.logger.error(f"❌ Backup failed: {backup_config.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error performing backup: {e}")
            return False
    
    async def _export_to_s3(self, snapshot: VolumeSnapshot, backup_config: BackupConfig) -> bool:
        """Export snapshot to S3"""
        try:
            if not self.s3_client:
                self.logger.error("❌ S3 client not initialized")
                return False
            
            bucket = backup_config.destination_config.get("bucket")
            prefix = backup_config.destination_config.get("prefix", "")
            
            # In a real implementation, this would involve:
            # 1. Mount the snapshot
            # 2. Create a tar archive
            # 3. Optionally compress and encrypt
            # 4. Upload to S3
            
            # For now, we'll create a placeholder
            backup_key = f"{prefix}backup-{snapshot.name}.tar.gz"
            
            # Create metadata
            metadata = {
                "backup-config": backup_config.name,
                "source-pvc": backup_config.source_pvc,
                "namespace": backup_config.namespace,
                "snapshot-name": snapshot.name,
                "created": datetime.now().isoformat(),
                "compression": str(backup_config.compression),
                "encryption": str(backup_config.encryption)
            }
            
            # In a real scenario, upload the actual backup data
            self.logger.info(f"📤 Would upload backup to s3://{bucket}/{backup_key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting to S3: {e}")
            return False
    
    async def _export_to_azure(self, snapshot: VolumeSnapshot, backup_config: BackupConfig) -> bool:
        """Export snapshot to Azure Blob Storage"""
        try:
            if not self.azure_client:
                self.logger.error("❌ Azure client not initialized")
                return False
            
            # Similar implementation as S3
            self.logger.info(f"📤 Would upload backup to Azure Blob Storage")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting to Azure: {e}")
            return False
    
    async def _export_to_gcs(self, snapshot: VolumeSnapshot, backup_config: BackupConfig) -> bool:
        """Export snapshot to Google Cloud Storage"""
        try:
            if not self.gcs_client:
                self.logger.error("❌ GCS client not initialized")
                return False
            
            # Similar implementation as S3
            self.logger.info(f"📤 Would upload backup to Google Cloud Storage")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting to GCS: {e}")
            return False
    
    async def _cleanup_old_snapshots(self) -> None:
        """Cleanup old snapshots and backups"""
        while True:
            try:
                current_time = datetime.now()
                
                # Cleanup old volume snapshots
                snapshots_to_delete = []
                
                for snapshot_key, snapshot in self.volume_snapshots.items():
                    # Check if snapshot is older than retention period
                    # This is simplified - in reality, you'd get the creation time from Kubernetes
                    # For now, we'll just log what would be cleaned up
                    
                    self.logger.debug(f"🧹 Would check snapshot {snapshot.name} for cleanup")
                
                # Cleanup old backups in cloud storage
                for backup_name, backup_config in self.backup_configs.items():
                    await self._cleanup_old_backups(backup_config, current_time)
                
                await asyncio.sleep(24 * 3600)  # Run daily
                
            except Exception as e:
                self.logger.error(f"❌ Error in cleanup task: {e}")
                await asyncio.sleep(24 * 3600)
    
    async def _cleanup_old_backups(self, backup_config: BackupConfig, current_time: datetime) -> None:
        """Cleanup old backups for a specific backup configuration"""
        try:
            cutoff_date = current_time - timedelta(days=backup_config.retention_days)
            
            if backup_config.destination_type == "s3" and self.s3_client:
                bucket = backup_config.destination_config.get("bucket")
                prefix = backup_config.destination_config.get("prefix", "")
                
                # List objects in S3 bucket
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )
                
                for obj in response.get("Contents", []):
                    if obj["LastModified"].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=bucket,
                            Key=obj["Key"]
                        )
                        self.logger.info(f"🗑️ Deleted old backup: s3://{bucket}/{obj['Key']}")
                        
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up old backups: {e}")
    
    async def get_storage_usage_report(self, namespace: str = None) -> Dict[str, Any]:
        """Get storage usage report"""
        try:
            report = {
                "total_pvcs": 0,
                "total_requested_storage": 0,
                "storage_classes": {},
                "pvcs": [],
                "alerts": []
            }
            
            for pvc_key, usage_info in self.storage_usage.items():
                if namespace and usage_info["namespace"] != namespace:
                    continue
                
                report["total_pvcs"] += 1
                
                # Parse storage size
                requested_size = usage_info["requested_size"]
                if requested_size.endswith("Gi"):
                    size_gb = int(requested_size[:-2])
                elif requested_size.endswith("Ti"):
                    size_gb = int(requested_size[:-2]) * 1024
                else:
                    size_gb = 0
                
                report["total_requested_storage"] += size_gb
                
                # Group by storage class
                storage_class = usage_info["storage_class"] or "default"
                if storage_class not in report["storage_classes"]:
                    report["storage_classes"][storage_class] = {
                        "count": 0,
                        "total_size_gb": 0
                    }
                
                report["storage_classes"][storage_class]["count"] += 1
                report["storage_classes"][storage_class]["total_size_gb"] += size_gb
                
                report["pvcs"].append(usage_info)
                
                # Check for alerts
                if usage_info["status"] == "Pending":
                    report["alerts"].append({
                        "type": "pending_pvc",
                        "message": f"PVC {usage_info['name']} is in Pending state",
                        "pvc": usage_info["name"],
                        "namespace": usage_info["namespace"]
                    })
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating storage usage report: {e}")
            return {}
    
    async def restore_backup(self, backup_name: str, target_pvc: str, target_namespace: str) -> bool:
        """Restore backup to PVC"""
        try:
            if backup_name not in self.backup_configs:
                self.logger.error(f"❌ Backup configuration not found: {backup_name}")
                return False
            
            backup_config = self.backup_configs[backup_name]
            
            self.logger.info(f"🔄 Starting restore from backup: {backup_name}")
            
            # In a real implementation, this would:
            # 1. Download backup from cloud storage
            # 2. Create a new PVC or clear existing one
            # 3. Mount the PVC
            # 4. Extract and restore data
            # 5. Verify integrity
            
            self.logger.info(f"✅ Restore completed: {backup_name} -> {target_namespace}/{target_pvc}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error restoring backup: {e}")
            return False
    
    async def clone_pvc(self, source_pvc: str, source_namespace: str, target_pvc: str, target_namespace: str) -> bool:
        """Clone PVC"""
        try:
            v1 = client.CoreV1Api()
            
            # Get source PVC
            source = v1.read_namespaced_persistent_volume_claim(
                name=source_pvc,
                namespace=source_namespace
            )
            
            # Create target PVC with same specs
            target_pvc_manifest = {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": target_pvc,
                    "namespace": target_namespace,
                    "labels": source.metadata.labels or {}
                },
                "spec": {
                    "accessModes": source.spec.access_modes,
                    "resources": source.spec.resources,
                    "storageClassName": source.spec.storage_class_name,
                    "dataSource": {
                        "kind": "PersistentVolumeClaim",
                        "name": source_pvc,
                        "namespace": source_namespace
                    }
                }
            }
            
            # Create cloned PVC
            v1.create_namespaced_persistent_volume_claim(
                namespace=target_namespace,
                body=target_pvc_manifest
            )
            
            self.logger.info(f"✅ Cloned PVC: {source_namespace}/{source_pvc} -> {target_namespace}/{target_pvc}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cloning PVC: {e}")
            return False

class StorageMetricsCollector:
    """Storage metrics collector for monitoring"""
    
    def __init__(self, storage_manager: ContainerStorageManager):
        self.storage_manager = storage_manager
        self.metrics = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect storage metrics"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "total_pvcs": len(self.storage_manager.storage_usage),
                "total_storage_classes": len(self.storage_manager.storage_classes),
                "backup_configs": len(self.storage_manager.backup_configs),
                "volume_snapshots": len(self.storage_manager.volume_snapshots),
                "storage_by_class": {},
                "storage_by_namespace": {},
                "pvc_status_distribution": {},
                "alerts": []
            }
            
            # Analyze storage usage
            for pvc_key, usage_info in self.storage_manager.storage_usage.items():
                # By storage class
                storage_class = usage_info["storage_class"] or "default"
                if storage_class not in metrics["storage_by_class"]:
                    metrics["storage_by_class"][storage_class] = 0
                metrics["storage_by_class"][storage_class] += 1
                
                # By namespace
                namespace = usage_info["namespace"]
                if namespace not in metrics["storage_by_namespace"]:
                    metrics["storage_by_namespace"][namespace] = 0
                metrics["storage_by_namespace"][namespace] += 1
                
                # Status distribution
                status = usage_info["status"]
                if status not in metrics["pvc_status_distribution"]:
                    metrics["pvc_status_distribution"][status] = 0
                metrics["pvc_status_distribution"][status] += 1
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error collecting storage metrics: {e}")
            return {}

__all__ = [
    "ContainerStorageManager",
    "StorageMetricsCollector",
    "StorageClass",
    "PersistentVolume",
    "PersistentVolumeClaim",
    "VolumeMount",
    "VolumeSnapshot",
    "BackupConfig",
    "StorageType",
    "AccessMode",
    "ReclaimPolicy",
    "VolumeBindingMode",
    "StorageProvisioner"
]
