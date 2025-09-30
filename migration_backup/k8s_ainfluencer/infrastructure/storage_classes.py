"""Storage Classes for Workload Optimization
=========================================

Kubernetes Storage Classes optimized for different workload types
for the Ainflue platform with performance and cost optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Storage types for different use cases"""
    HIGH_PERFORMANCE = "high-performance"
    GENERAL_PURPOSE = "general-purpose"
    COLD_STORAGE = "cold-storage"
    DATABASE = "database"
    AI_WORKLOADS = "ai-workloads"
    BACKUP = "backup"
    TEMP_STORAGE = "temp-storage"


class VolumeBindingMode(Enum):
    """Volume binding modes"""
    IMMEDIATE = "Immediate"
    WAIT_FOR_FIRST_CONSUMER = "WaitForFirstConsumer"


class ReclaimPolicy(Enum):
    """Volume reclaim policies"""
    DELETE = "Delete"
    RETAIN = "Retain"
    RECYCLE = "Recycle"


@dataclass
class StorageClassSpec:
    """Storage class specification"""
    name: str
    storage_type: StorageType
    provisioner: str
    parameters: Dict[str, str] = field(default_factory=dict)
    volume_binding_mode: VolumeBindingMode = VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER
    reclaim_policy: ReclaimPolicy = ReclaimPolicy.DELETE
    allow_volume_expansion: bool = True
    mount_options: List[str] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)


class StorageClassManager:
    """Manages optimized Storage Classes for different workloads"""
    
    def __init__(self, cloud_provider: str = "aws"):
        self.cloud_provider = cloud_provider
        self.storage_classes: Dict[str, StorageClassSpec] = {}
    
    def create_high_performance_storage(self) -> StorageClassSpec:
        """Create high-performance storage for latency-sensitive workloads"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-high-performance",
                storage_type=StorageType.HIGH_PERFORMANCE,
                provisioner="ebs.csi.aws.com",
                parameters={
                    "type": "io2",
                    "iops": "3000",
                    "fsType": "ext4",
                    "encrypted": "true",
                    "kmsKeyId": "alias/ia-influencer-storage"
                },
                volume_binding_mode=VolumeBindingMode.IMMEDIATE,
                annotations={
                    "storageclass.kubernetes.io/is-default-class": "false",
                    "description": "High-performance SSD storage for latency-sensitive workloads"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-high-performance",
                storage_type=StorageType.HIGH_PERFORMANCE,
                provisioner="pd.csi.storage.gke.io",
                parameters={
                    "type": "pd-ssd",
                    "replication-type": "regional-pd",
                    "disk-encryption-key": "projects/PROJECT_ID/locations/LOCATION/keyRings/RING_ID/cryptoKeys/KEY_ID"
                }
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-high-performance",
                storage_type=StorageType.HIGH_PERFORMANCE,
                provisioner="disk.csi.azure.com",
                parameters={
                    "skuName": "Premium_LRS",
                    "fsType": "ext4",
                    "encrypted": "true"
                }
            )
        
        # Default/generic implementation
        return StorageClassSpec(
            name="ia-influencer-high-performance",
            storage_type=StorageType.HIGH_PERFORMANCE,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"}
        )
    
    def create_general_purpose_storage(self) -> StorageClassSpec:
        """Create general-purpose storage for most workloads"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-general-purpose",
                storage_type=StorageType.GENERAL_PURPOSE,
                provisioner="ebs.csi.aws.com",
                parameters={
                    "type": "gp3",
                    "iops": "3000",
                    "throughput": "125",
                    "fsType": "ext4",
                    "encrypted": "true"
                },
                annotations={
                    "storageclass.kubernetes.io/is-default-class": "true",
                    "description": "General-purpose SSD storage for most workloads"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-general-purpose",
                storage_type=StorageType.GENERAL_PURPOSE,
                provisioner="pd.csi.storage.gke.io",
                parameters={
                    "type": "pd-balanced",
                    "replication-type": "regional-pd"
                }
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-general-purpose",
                storage_type=StorageType.GENERAL_PURPOSE,
                provisioner="disk.csi.azure.com",
                parameters={
                    "skuName": "StandardSSD_LRS",
                    "fsType": "ext4"
                }
            )
        
        return StorageClassSpec(
            name="ia-influencer-general-purpose",
            storage_type=StorageType.GENERAL_PURPOSE,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"}
        )
    
    def create_database_storage(self) -> StorageClassSpec:
        """Create optimized storage for database workloads"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-database",
                storage_type=StorageType.DATABASE,
                provisioner="ebs.csi.aws.com",
                parameters={
                    "type": "io2",
                    "iops": "4000",
                    "fsType": "ext4",
                    "encrypted": "true",
                    "kmsKeyId": "alias/ia-influencer-database"
                },
                volume_binding_mode=VolumeBindingMode.IMMEDIATE,
                reclaim_policy=ReclaimPolicy.RETAIN,
                annotations={
                    "description": "High-IOPS storage optimized for database workloads"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-database",
                storage_type=StorageType.DATABASE,
                provisioner="pd.csi.storage.gke.io",
                parameters={
                    "type": "pd-extreme",
                    "provisioned-iops-on-create": "4000",
                    "replication-type": "regional-pd"
                },
                reclaim_policy=ReclaimPolicy.RETAIN
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-database",
                storage_type=StorageType.DATABASE,
                provisioner="disk.csi.azure.com",
                parameters={
                    "skuName": "UltraSSD_LRS",
                    "fsType": "ext4",
                    "diskIOPSReadWrite": "4000",
                    "diskMBpsReadWrite": "200"
                },
                reclaim_policy=ReclaimPolicy.RETAIN
            )
        
        return StorageClassSpec(
            name="ia-influencer-database",
            storage_type=StorageType.DATABASE,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"},
            reclaim_policy=ReclaimPolicy.RETAIN
        )
    
    def create_ai_workloads_storage(self) -> StorageClassSpec:
        """Create storage optimized for AI/ML workloads"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-ai-workloads",
                storage_type=StorageType.AI_WORKLOADS,
                provisioner="efs.csi.aws.com",
                parameters={
                    "provisioningMode": "efs-ap",
                    "fileSystemId": "fs-XXXXXXXX",
                    "directoryPerms": "0755",
                    "gidRangeStart": "1000",
                    "gidRangeEnd": "2000",
                    "basePath": "/ai-workloads"
                },
                volume_binding_mode=VolumeBindingMode.IMMEDIATE,
                annotations={
                    "description": "Shared storage for AI/ML model training and inference"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-ai-workloads",
                storage_type=StorageType.AI_WORKLOADS,
                provisioner="filestore.csi.storage.gke.io",
                parameters={
                    "tier": "enterprise",
                    "network": "default"
                }
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-ai-workloads",
                storage_type=StorageType.AI_WORKLOADS,
                provisioner="file.csi.azure.com",
                parameters={
                    "skuName": "Premium_LRS",
                    "protocol": "nfs"
                }
            )
        
        return StorageClassSpec(
            name="ia-influencer-ai-workloads",
            storage_type=StorageType.AI_WORKLOADS,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"}
        )
    
    def create_cold_storage(self) -> StorageClassSpec:
        """Create cold storage for archival and backup"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-cold-storage",
                storage_type=StorageType.COLD_STORAGE,
                provisioner="ebs.csi.aws.com",
                parameters={
                    "type": "sc1",  # Cold HDD
                    "fsType": "ext4",
                    "encrypted": "true"
                },
                volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
                annotations={
                    "description": "Cost-optimized storage for archival and infrequent access"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-cold-storage",
                storage_type=StorageType.COLD_STORAGE,
                provisioner="pd.csi.storage.gke.io",
                parameters={
                    "type": "pd-standard",
                    "replication-type": "regional-pd"
                }
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-cold-storage",
                storage_type=StorageType.COLD_STORAGE,
                provisioner="disk.csi.azure.com",
                parameters={
                    "skuName": "Standard_LRS",
                    "fsType": "ext4"
                }
            )
        
        return StorageClassSpec(
            name="ia-influencer-cold-storage",
            storage_type=StorageType.COLD_STORAGE,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"}
        )
    
    def create_backup_storage(self) -> StorageClassSpec:
        """Create storage for backup operations"""
        if self.cloud_provider == "aws":
            return StorageClassSpec(
                name="ia-influencer-backup",
                storage_type=StorageType.BACKUP,
                provisioner="ebs.csi.aws.com",
                parameters={
                    "type": "st1",  # Throughput Optimized HDD
                    "fsType": "ext4",
                    "encrypted": "true"
                },
                reclaim_policy=ReclaimPolicy.RETAIN,
                annotations={
                    "description": "Throughput-optimized storage for backup operations"
                }
            )
        elif self.cloud_provider == "gcp":
            return StorageClassSpec(
                name="ia-influencer-backup",
                storage_type=StorageType.BACKUP,
                provisioner="pd.csi.storage.gke.io",
                parameters={
                    "type": "pd-standard",
                    "replication-type": "regional-pd"
                },
                reclaim_policy=ReclaimPolicy.RETAIN
            )
        elif self.cloud_provider == "azure":
            return StorageClassSpec(
                name="ia-influencer-backup",
                storage_type=StorageType.BACKUP,
                provisioner="disk.csi.azure.com",
                parameters={
                    "skuName": "Standard_LRS",
                    "fsType": "ext4"
                },
                reclaim_policy=ReclaimPolicy.RETAIN
            )
        
        return StorageClassSpec(
            name="ia-influencer-backup",
            storage_type=StorageType.BACKUP,
            provisioner="kubernetes.io/host-path",
            parameters={"type": "DirectoryOrCreate"},
            reclaim_policy=ReclaimPolicy.RETAIN
        )
    
    def create_temp_storage(self) -> StorageClassSpec:
        """Create temporary storage for ephemeral workloads"""
        return StorageClassSpec(
            name="ia-influencer-temp",
            storage_type=StorageType.TEMP_STORAGE,
            provisioner="kubernetes.io/no-provisioner",
            parameters={},
            volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
            reclaim_policy=ReclaimPolicy.DELETE,
            annotations={
                "description": "Local temporary storage for ephemeral workloads"
            }
        )
    
    def create_volume_snapshot_class(self, storage_type: StorageType) -> Dict[str, Any]:
        """Create VolumeSnapshotClass for backup and disaster recovery"""
        if self.cloud_provider == "aws":
            driver = "ebs.csi.aws.com"
            parameters = {
                "encrypted": "true"
            }
        elif self.cloud_provider == "gcp":
            driver = "pd.csi.storage.gke.io"
            parameters = {}
        elif self.cloud_provider == "azure":
            driver = "disk.csi.azure.com"
            parameters = {}
        else:
            driver = "hostpath.csi.k8s.io"
            parameters = {}
        
        return {
            "apiVersion": "snapshot.storage.k8s.io/v1",
            "kind": "VolumeSnapshotClass",
            "metadata": {
                "name": f"ia-influencer-{storage_type.value}-snapshots",
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "storage",
                    "storage-type": storage_type.value
                },
                "annotations": {
                    "description": f"Volume snapshot class for {storage_type.value} storage"
                }
            },
            "driver": driver,
            "deletionPolicy": "Delete",
            "parameters": parameters
        }
    
    def to_kubernetes_manifest(self, spec: StorageClassSpec) -> Dict[str, Any]:
        """Convert storage class spec to Kubernetes manifest"""
        manifest = {
            "apiVersion": "storage.k8s.io/v1",
            "kind": "StorageClass",
            "metadata": {
                "name": spec.name,
                "labels": {
                    "app.kubernetes.io/name": "ia-influencer",
                    "app.kubernetes.io/component": "storage",
                    "storage-type": spec.storage_type.value
                },
                "annotations": spec.annotations
            },
            "provisioner": spec.provisioner,
            "parameters": spec.parameters,
            "volumeBindingMode": spec.volume_binding_mode.value,
            "reclaimPolicy": spec.reclaim_policy.value,
            "allowVolumeExpansion": spec.allow_volume_expansion
        }
        
        if spec.mount_options:
            manifest["mountOptions"] = spec.mount_options
        
        return manifest
    
    def generate_all_storage_classes(self) -> Dict[str, StorageClassSpec]:
        """Generate all optimized storage classes"""
        storage_classes = {
            "high-performance": self.create_high_performance_storage(),
            "general-purpose": self.create_general_purpose_storage(),
            "database": self.create_database_storage(),
            "ai-workloads": self.create_ai_workloads_storage(),
            "cold-storage": self.create_cold_storage(),
            "backup": self.create_backup_storage(),
            "temp": self.create_temp_storage()
        }
        
        self.storage_classes = storage_classes
        return storage_classes
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Generate all storage manifests"""
        manifests = {}
        
        # Generate storage classes
        storage_classes = self.generate_all_storage_classes()
        for name, spec in storage_classes.items():
            manifest = self.to_kubernetes_manifest(spec)
            manifests[f"storage-class-{name}"] = yaml.dump(manifest, default_flow_style=False)
        
        # Generate volume snapshot classes
        for storage_type in [StorageType.HIGH_PERFORMANCE, StorageType.DATABASE, StorageType.AI_WORKLOADS]:
            snapshot_class = self.create_volume_snapshot_class(storage_type)
            manifests[f"snapshot-class-{storage_type.value}"] = yaml.dump(snapshot_class, default_flow_style=False)
        
        return manifests
    
    def save_manifests_to_files(self, output_dir: str = "./k8s-manifests/storage-classes"):
        """Save all storage manifests to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        manifests = self.generate_all_manifests()
        
        for name, manifest in manifests.items():
            file_path = os.path.join(output_dir, f"{name}.yaml")
            with open(file_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Storage manifest saved: {file_path}")
        
        return len(manifests)


# Export main functionality
__all__ = ['StorageClassManager', 'StorageClassSpec', 'StorageType', 'VolumeBindingMode', 'ReclaimPolicy']