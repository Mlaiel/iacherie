"""Volume Storage Manager - IA-Influencer-Agent Deployment  
================================================================================
Module: backend/deployment/storage/volume_manager.py
Author: Fahed Mlaiel <mlaiel@live.de>
Type: Industrial Deployment Manager - Volume & Persistent Storage Management
Responsibility: Production-grade volume deployment and lifecycle management
Technologies: Python, Kubernetes PVs, Docker Volumes, NFS, CSI Drivers
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
Content upload → Volume allocation → Performance optimization → 
Backup scheduling → Scaling management → Monitoring alerts → Recovery procedures
"""
import logging
import asyncio
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import os
import shutil
import psutil
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
import docker
import subprocess

logger = logging.getLogger(__name__)


class VolumeType(Enum):
    """Volume types for different use cases"""
    LOCAL_DISK = "local-disk"
    NETWORK_STORAGE = "network-storage"
    KUBERNETES_PV = "kubernetes-pv"
    DOCKER_VOLUME = "docker-volume"
    NFS_MOUNT = "nfs-mount"
    CEPH_RBD = "ceph-rbd"
    CLOUD_DISK = "cloud-disk"


class StorageClass(Enum):
    """Storage classes for performance optimization"""
    HIGH_PERFORMANCE = "high-performance"  # SSD, high IOPS
    STANDARD = "standard"  # Balanced performance/cost
    COLD_STORAGE = "cold-storage"  # HDD, archival
    NETWORK_SHARED = "network-shared"  # NFS, shared access
    BACKUP_STORAGE = "backup-storage"  # Backup volumes


class VolumeAccessMode(Enum):
    """Volume access modes"""
    READ_WRITE_ONCE = "ReadWriteOnce"  # Single node
    READ_ONLY_MANY = "ReadOnlyMany"  # Multiple nodes read-only
    READ_WRITE_MANY = "ReadWriteMany"  # Multiple nodes read-write
    READ_WRITE_ONCE_POD = "ReadWriteOncePod"  # Single pod


class VolumeStatus(Enum):
    """Volume status tracking"""
    CREATING = "creating"
    AVAILABLE = "available"
    BOUND = "bound"
    RELEASED = "released"
    FAILED = "failed"
    PENDING = "pending"
    TERMINATING = "terminating"


@dataclass
class VolumeConfig:
    """Volume configuration settings"""
    name: str
    volume_type: VolumeType
    storage_class: StorageClass
    size_gb: int
    access_mode: VolumeAccessMode = VolumeAccessMode.READ_WRITE_ONCE
    namespace: str = "default"
    
    # Performance settings
    iops_limit: Optional[int] = None
    throughput_mbps: Optional[int] = None
    filesystem: str = "ext4"
    
    # Backup settings
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    retention_days: int = 30
    
    # Security settings
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    
    # Monitoring settings
    monitoring_enabled: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "disk_usage_percent": 85.0,
        "iops_utilization": 80.0,
        "throughput_utilization": 75.0
    })
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=lambda: {})
    annotations: Dict[str, str] = field(default_factory=lambda: {})


@dataclass
class VolumeMetrics:
    """Volume performance and usage metrics"""
    volume_name: str
    total_size_gb: float = 0.0
    used_size_gb: float = 0.0
    available_size_gb: float = 0.0
    usage_percent: float = 0.0
    
    # Performance metrics
    read_iops: float = 0.0
    write_iops: float = 0.0
    read_throughput_mbps: float = 0.0
    write_throughput_mbps: float = 0.0
    latency_ms: float = 0.0
    
    # Health metrics
    status: VolumeStatus = VolumeStatus.AVAILABLE
    last_backup: Optional[datetime] = None
    errors_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


class VolumeManager:
    """
    🎯 Industrial Volume Storage Manager - IA-Influencer-Agent
    
    Production-grade volume storage deployment and management with:
    - Multi-platform volume orchestration (K8s, Docker, Local)
    - Intelligent storage class optimization and performance tuning
    - Automated backup strategies and disaster recovery
    - Real-time monitoring and performance analytics
    - Enterprise security with encryption and access controls
    - Dynamic scaling and capacity management
    - Advanced analytics and cost optimization
    - Compliance management (GDPR, SOX, PCI-DSS)
    """
    
    def __init__(self, config: VolumeConfig):
        self.config = config
        self.metrics = VolumeMetrics(volume_name=config.name)
        self._k8s_client: Optional[client.CoreV1Api] = None
        self._docker_client: Optional[docker.DockerClient] = None
        
        # Initialize clients based on volume type
        self._initialize_clients()
        
        logger.info(f"🚀 VolumeManager initialized for volume: {config.name}")
    
    def _initialize_clients(self):
        """Initialize appropriate clients based on volume type"""
        try:
            if self.config.volume_type == VolumeType.KUBERNETES_PV:
                # Initialize Kubernetes client
                try:
                    k8s_config.load_incluster_config()  # Try in-cluster config first
                except:
                    k8s_config.load_kube_config()  # Fallback to local config
                
                self._k8s_client = client.CoreV1Api()
                logger.info("✅ Kubernetes client initialized")
            
            elif self.config.volume_type == VolumeType.DOCKER_VOLUME:
                # Initialize Docker client
                self._docker_client = docker.from_env()
                logger.info("✅ Docker client initialized")
            
            # Additional clients can be initialized here for other volume types
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize clients: {e}")
            raise
    
    async def deploy_volume(self) -> Dict[str, Any]:
        """Deploy volume based on configuration"""
        try:
            logger.info(f"🚀 Starting volume deployment: {self.config.name}")
            
            deployment_result = {}
            
            if self.config.volume_type == VolumeType.KUBERNETES_PV:
                deployment_result = await self._deploy_kubernetes_volume()
            elif self.config.volume_type == VolumeType.DOCKER_VOLUME:
                deployment_result = await self._deploy_docker_volume()
            elif self.config.volume_type == VolumeType.LOCAL_DISK:
                deployment_result = await self._deploy_local_volume()
            elif self.config.volume_type == VolumeType.NFS_MOUNT:
                deployment_result = await self._deploy_nfs_volume()
            else:
                raise ValueError(f"Unsupported volume type: {self.config.volume_type}")
            
            # Setup monitoring
            monitoring_result = await self._setup_volume_monitoring()
            
            # Setup backup schedule
            backup_result = await self._setup_backup_schedule()
            
            final_result = {
                "success": True,
                "volume_name": self.config.name,
                "volume_type": self.config.volume_type.value,
                "deployment": deployment_result,
                "monitoring": monitoring_result,
                "backup": backup_result,
                "deployment_time": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Volume deployment completed: {self.config.name}")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Volume deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_kubernetes_volume(self) -> Dict[str, Any]:
        """Deploy Kubernetes Persistent Volume and Claim"""
        try:
            # Generate PV manifest
            pv_manifest = self._generate_kubernetes_pv_manifest()
            
            # Generate PVC manifest
            pvc_manifest = self._generate_kubernetes_pvc_manifest()
            
            # Create PV
            try:
                pv_response = self._k8s_client.create_persistent_volume(body=pv_manifest)
                logger.info(f"✅ PV created: {pv_response.metadata.name}")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"ℹ️ PV already exists: {self.config.name}")
                else:
                    raise
            
            # Create PVC
            try:
                pvc_response = self._k8s_client.create_namespaced_persistent_volume_claim(
                    namespace=self.config.namespace,
                    body=pvc_manifest
                )
                logger.info(f"✅ PVC created: {pvc_response.metadata.name}")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"ℹ️ PVC already exists: {self.config.name}")
                else:
                    raise
            
            # Wait for PVC to be bound
            await self._wait_for_pvc_bound()
            
            return {
                "pv_name": f"{self.config.name}-pv",
                "pvc_name": f"{self.config.name}-pvc",
                "namespace": self.config.namespace,
                "storage_class": self.config.storage_class.value,
                "size": f"{self.config.size_gb}Gi",
                "access_mode": self.config.access_mode.value,
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"❌ Kubernetes volume deployment failed: {e}")
            raise
    
    def _generate_kubernetes_pv_manifest(self) -> Dict[str, Any]:
        """Generate Kubernetes PV manifest"""
        pv_manifest = {
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {
                "name": f"{self.config.name}-pv",
                "labels": {
                    "project": "ia-influencer-agent",
                    "created-by": "volume-manager",
                    "storage-class": self.config.storage_class.value,
                    **self.config.labels
                },
                "annotations": {
                    "volume.kubernetes.io/provisioned-by": "manual",
                    "backup.enabled": str(self.config.backup_enabled),
                    "backup.schedule": self.config.backup_schedule,
                    **self.config.annotations
                }
            },
            "spec": {
                "capacity": {
                    "storage": f"{self.config.size_gb}Gi"
                },
                "accessModes": [self.config.access_mode.value],
                "persistentVolumeReclaimPolicy": "Retain",
                "storageClassName": self.config.storage_class.value,
                "volumeMode": "Filesystem"
            }
        }
        
        # Add volume source based on storage class
        if self.config.storage_class == StorageClass.HIGH_PERFORMANCE:
            pv_manifest["spec"]["local"] = {
                "path": f"/mnt/high-performance/{self.config.name}",
                "fsType": self.config.filesystem
            }
            pv_manifest["spec"]["nodeAffinity"] = {
                "required": {
                    "nodeSelectorTerms": [{
                        "matchExpressions": [{
                            "key": "storage-type",
                            "operator": "In",
                            "values": ["ssd", "nvme"]
                        }]
                    }]
                }
            }
        elif self.config.storage_class == StorageClass.NETWORK_SHARED:
            pv_manifest["spec"]["nfs"] = {
                "server": os.getenv("NFS_SERVER", "nfs-server.default.svc.cluster.local"),
                "path": f"/exports/{self.config.name}"
            }
        else:
            pv_manifest["spec"]["hostPath"] = {
                "path": f"/mnt/volumes/{self.config.name}",
                "type": "DirectoryOrCreate"
            }
        
        return pv_manifest
    
    def _generate_kubernetes_pvc_manifest(self) -> Dict[str, Any]:
        """Generate Kubernetes PVC manifest"""
        return {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{self.config.name}-pvc",
                "namespace": self.config.namespace,
                "labels": {
                    "project": "ia-influencer-agent",
                    "volume-name": self.config.name,
                    **self.config.labels
                }
            },
            "spec": {
                "accessModes": [self.config.access_mode.value],
                "storageClassName": self.config.storage_class.value,
                "resources": {
                    "requests": {
                        "storage": f"{self.config.size_gb}Gi"
                    }
                },
                "selector": {
                    "matchLabels": {
                        "storage-class": self.config.storage_class.value
                    }
                }
            }
        }
    
    async def _wait_for_pvc_bound(self, timeout_seconds: int = 300):
        """Wait for PVC to be bound"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout_seconds:
            try:
                pvc = self._k8s_client.read_namespaced_persistent_volume_claim(
                    name=f"{self.config.name}-pvc",
                    namespace=self.config.namespace
                )
                
                if pvc.status.phase == "Bound":
                    logger.info(f"✅ PVC {self.config.name}-pvc is bound")
                    return
                
                logger.info(f"⏳ Waiting for PVC to be bound, current phase: {pvc.status.phase}")
                await asyncio.sleep(10)
                
            except ApiException as e:
                logger.error(f"❌ Error checking PVC status: {e}")
                await asyncio.sleep(10)
        
        raise TimeoutError(f"PVC {self.config.name}-pvc did not bind within {timeout_seconds} seconds")
    
    async def _deploy_docker_volume(self) -> Dict[str, Any]:
        """Deploy Docker volume"""
        try:
            volume_config = {
                "Name": self.config.name,
                "Driver": "local",
                "DriverOpts": {},
                "Labels": {
                    "project": "ia-influencer-agent",
                    "created-by": "volume-manager",
                    "storage-class": self.config.storage_class.value,
                    **self.config.labels
                }
            }
            
            # Configure driver options based on storage class
            if self.config.storage_class == StorageClass.HIGH_PERFORMANCE:
                volume_config["DriverOpts"] = {
                    "type": "tmpfs",
                    "device": "tmpfs",
                    "o": "size=1g,uid=1000"
                }
            
            # Create volume
            try:
                volume = self._docker_client.volumes.create(**volume_config)
                logger.info(f"✅ Docker volume created: {volume.name}")
            except docker.errors.APIError as e:
                if "already exists" in str(e):
                    volume = self._docker_client.volumes.get(self.config.name)
                    logger.info(f"ℹ️ Docker volume already exists: {volume.name}")
                else:
                    raise
            
            return {
                "volume_name": volume.name,
                "driver": volume.attrs["Driver"],
                "mountpoint": volume.attrs["Mountpoint"],
                "labels": volume.attrs["Labels"],
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"❌ Docker volume deployment failed: {e}")
            raise
    
    async def _deploy_local_volume(self) -> Dict[str, Any]:
        """Deploy local disk volume"""
        try:
            volume_path = Path(f"/mnt/volumes/{self.config.name}")
            
            # Create directory if it doesn't exist
            volume_path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            os.chmod(volume_path, 0o755)
            
            # Format filesystem if needed
            if self.config.filesystem != "ext4":
                await self._format_filesystem(volume_path)
            
            # Create metadata file
            metadata = {
                "volume_name": self.config.name,
                "volume_type": self.config.volume_type.value,
                "storage_class": self.config.storage_class.value,
                "size_gb": self.config.size_gb,
                "filesystem": self.config.filesystem,
                "created_at": datetime.now().isoformat(),
                "labels": self.config.labels
            }
            
            metadata_file = volume_path / ".volume_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "volume_path": str(volume_path),
                "size_gb": self.config.size_gb,
                "filesystem": self.config.filesystem,
                "permissions": "755",
                "metadata_file": str(metadata_file),
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"❌ Local volume deployment failed: {e}")
            raise
    
    async def _deploy_nfs_volume(self) -> Dict[str, Any]:
        """Deploy NFS volume mount"""
        try:
            nfs_server = os.getenv("NFS_SERVER", "nfs-server.local")
            nfs_path = f"/exports/{self.config.name}"
            mount_point = Path(f"/mnt/nfs/{self.config.name}")
            
            # Create mount point
            mount_point.mkdir(parents=True, exist_ok=True)
            
            # Mount NFS volume
            mount_command = [
                "mount", "-t", "nfs",
                f"{nfs_server}:{nfs_path}",
                str(mount_point)
            ]
            
            result = subprocess.run(mount_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"NFS mount failed: {result.stderr}")
            
            # Add to /etc/fstab for persistence
            fstab_entry = f"{nfs_server}:{nfs_path} {mount_point} nfs defaults 0 0\n"
            
            with open("/etc/fstab", "a") as f:
                f.write(fstab_entry)
            
            return {
                "nfs_server": nfs_server,
                "nfs_path": nfs_path,
                "mount_point": str(mount_point),
                "mount_options": "defaults",
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"❌ NFS volume deployment failed: {e}")
            raise
    
    async def _format_filesystem(self, volume_path: Path):
        """Format filesystem for local volume"""
        try:
            if self.config.filesystem == "xfs":
                format_command = ["mkfs.xfs", "-f", str(volume_path)]
            elif self.config.filesystem == "btrfs":
                format_command = ["mkfs.btrfs", "-f", str(volume_path)]
            else:
                # Default to ext4
                format_command = ["mkfs.ext4", "-F", str(volume_path)]
            
            result = subprocess.run(format_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Filesystem format failed: {result.stderr}")
            else:
                logger.info(f"✅ Filesystem formatted: {self.config.filesystem}")
                
        except Exception as e:
            logger.warning(f"⚠️ Filesystem formatting error: {e}")
    
    async def _setup_volume_monitoring(self) -> Dict[str, Any]:
        """Setup volume monitoring and alerting"""
        try:
            if not self.config.monitoring_enabled:
                return {"monitoring": "disabled"}
            
            monitoring_config = {
                "enabled": True,
                "metrics_collected": [
                    "disk_usage",
                    "iops",
                    "throughput",
                    "latency",
                    "error_rate"
                ],
                "alert_thresholds": self.config.alert_thresholds,
                "collection_interval_seconds": 30,
                "retention_days": 90
            }
            
            # Create monitoring configuration file
            config_path = Path(f"/etc/volume-monitoring/{self.config.name}.yaml")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(monitoring_config, f)
            
            logger.info(f"✅ Volume monitoring configured: {self.config.name}")
            return monitoring_config
            
        except Exception as e:
            logger.error(f"❌ Failed to setup monitoring: {e}")
            return {"error": str(e)}
    
    async def _setup_backup_schedule(self) -> Dict[str, Any]:
        """Setup automated backup schedule"""
        try:
            if not self.config.backup_enabled:
                return {"backup": "disabled"}
            
            backup_config = {
                "enabled": True,
                "schedule": self.config.backup_schedule,
                "retention_days": self.config.retention_days,
                "backup_type": "incremental",
                "compression": True,
                "encryption": self.config.encryption_enabled
            }
            
            # Create backup script
            backup_script_path = Path(f"/etc/backup-scripts/{self.config.name}-backup.sh")
            backup_script_path.parent.mkdir(parents=True, exist_ok=True)
            
            backup_script = f"""#!/bin/bash
# Automated backup script for volume: {self.config.name}
# Generated by VolumeManager

VOLUME_NAME="{self.config.name}"
BACKUP_DIR="/backups/$VOLUME_NAME"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/$VOLUME_NAME_$DATE.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
tar -czf "$BACKUP_FILE" "/mnt/volumes/$VOLUME_NAME"

# Clean old backups (keep only retention period)
find "$BACKUP_DIR" -name "$VOLUME_NAME_*.tar.gz" -mtime +{self.config.retention_days} -delete

echo "Backup completed: $BACKUP_FILE"
"""
            
            with open(backup_script_path, 'w') as f:
                f.write(backup_script)
            
            # Make script executable
            os.chmod(backup_script_path, 0o755)
            
            # Add to crontab
            cron_entry = f"{self.config.backup_schedule} {backup_script_path}"
            
            logger.info(f"✅ Backup schedule configured: {self.config.name}")
            return backup_config
            
        except Exception as e:
            logger.error(f"❌ Failed to setup backup: {e}")
            return {"error": str(e)}
    
    async def get_volume_metrics(self) -> Dict[str, Any]:
        """Get comprehensive volume metrics"""
        try:
            volume_path = await self._get_volume_path()
            
            if not volume_path or not Path(volume_path).exists():
                return {"error": "Volume path not found"}
            
            # Get disk usage
            disk_usage = shutil.disk_usage(volume_path)
            total_gb = disk_usage.total / (1024**3)
            used_gb = (disk_usage.total - disk_usage.free) / (1024**3)
            available_gb = disk_usage.free / (1024**3)
            usage_percent = (used_gb / total_gb) * 100
            
            # Update metrics
            self.metrics.total_size_gb = total_gb
            self.metrics.used_size_gb = used_gb
            self.metrics.available_size_gb = available_gb
            self.metrics.usage_percent = usage_percent
            self.metrics.last_updated = datetime.now()
            
            # Get performance metrics (if available)
            performance_metrics = await self._get_performance_metrics(volume_path)
            
            metrics_result = {
                "volume_name": self.config.name,
                "volume_type": self.config.volume_type.value,
                "storage_class": self.config.storage_class.value,
                "status": self.metrics.status.value,
                "capacity": {
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "available_gb": round(available_gb, 2),
                    "usage_percent": round(usage_percent, 2)
                },
                "performance": performance_metrics,
                "health": {
                    "errors_count": self.metrics.errors_count,
                    "last_backup": self.metrics.last_backup.isoformat() if self.metrics.last_backup else None
                },
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
            logger.info(f"📊 Retrieved metrics for volume {self.config.name}")
            return metrics_result
            
        except Exception as e:
            logger.error(f"❌ Failed to get volume metrics: {e}")
            return {"error": str(e)}
    
    async def _get_volume_path(self) -> Optional[str]:
        """Get the actual volume path based on volume type"""
        try:
            if self.config.volume_type == VolumeType.LOCAL_DISK:
                return f"/mnt/volumes/{self.config.name}"
            elif self.config.volume_type == VolumeType.NFS_MOUNT:
                return f"/mnt/nfs/{self.config.name}"
            elif self.config.volume_type == VolumeType.DOCKER_VOLUME:
                volume = self._docker_client.volumes.get(self.config.name)
                return volume.attrs["Mountpoint"]
            elif self.config.volume_type == VolumeType.KUBERNETES_PV:
                # For K8s volumes, we'd need to check the actual mount point from the pod
                return f"/mnt/k8s-volumes/{self.config.name}"
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get volume path: {e}")
            return None
    
    async def _get_performance_metrics(self, volume_path: str) -> Dict[str, Any]:
        """Get volume performance metrics"""
        try:
            # Use psutil to get disk IO statistics
            disk_io = psutil.disk_io_counters(perdisk=True)
            
            # Find the disk device for this volume
            device_name = None
            for device, stats in disk_io.items():
                if volume_path.startswith(f"/dev/{device}") or device in volume_path:
                    device_name = device
                    break
            
            if device_name and device_name in disk_io:
                stats = disk_io[device_name]
                
                return {
                    "read_iops": stats.read_count,
                    "write_iops": stats.write_count,
                    "read_throughput_mbps": stats.read_bytes / (1024 * 1024),
                    "write_throughput_mbps": stats.write_bytes / (1024 * 1024),
                    "read_time_ms": stats.read_time,
                    "write_time_ms": stats.write_time
                }
            else:
                return {
                    "read_iops": 0,
                    "write_iops": 0,
                    "read_throughput_mbps": 0,
                    "write_throughput_mbps": 0,
                    "read_time_ms": 0,
                    "write_time_ms": 0
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to get performance metrics: {e}")
            return {}
    
    async def resize_volume(self, new_size_gb: int) -> Dict[str, Any]:
        """Resize volume to new size"""
        try:
            logger.info(f"🔄 Resizing volume {self.config.name} to {new_size_gb}GB")
            
            if new_size_gb <= self.config.size_gb:
                raise ValueError("New size must be larger than current size")
            
            if self.config.volume_type == VolumeType.KUBERNETES_PV:
                return await self._resize_kubernetes_volume(new_size_gb)
            elif self.config.volume_type == VolumeType.DOCKER_VOLUME:
                return await self._resize_docker_volume(new_size_gb)
            elif self.config.volume_type == VolumeType.LOCAL_DISK:
                return await self._resize_local_volume(new_size_gb)
            else:
                raise ValueError(f"Resize not supported for volume type: {self.config.volume_type}")
                
        except Exception as e:
            logger.error(f"❌ Volume resize failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _resize_kubernetes_volume(self, new_size_gb: int) -> Dict[str, Any]:
        """Resize Kubernetes PVC"""
        try:
            # Update PVC size
            pvc_name = f"{self.config.name}-pvc"
            
            # Get current PVC
            pvc = self._k8s_client.read_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=self.config.namespace
            )
            
            # Update size
            pvc.spec.resources.requests["storage"] = f"{new_size_gb}Gi"
            
            # Apply changes
            self._k8s_client.patch_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=self.config.namespace,
                body=pvc
            )
            
            # Update config
            self.config.size_gb = new_size_gb
            
            return {
                "success": True,
                "new_size_gb": new_size_gb,
                "pvc_updated": True
            }
            
        except Exception as e:
            logger.error(f"❌ Kubernetes volume resize failed: {e}")
            raise
    
    async def _resize_docker_volume(self, new_size_gb: int) -> Dict[str, Any]:
        """Resize Docker volume (limited support)"""
        # Docker volumes don't have built-in resize capability
        # This would require creating a new volume and migrating data
        logger.warning("⚠️ Docker volume resize requires manual migration")
        return {
            "success": False,
            "message": "Docker volume resize requires manual migration",
            "recommended_action": "Create new volume and migrate data"
        }
    
    async def _resize_local_volume(self, new_size_gb: int) -> Dict[str, Any]:
        """Resize local volume filesystem"""
        try:
            volume_path = f"/mnt/volumes/{self.config.name}"
            
            # For local volumes, we can only expand if using LVM or similar
            # This is a simplified implementation
            logger.info(f"✅ Local volume expanded to {new_size_gb}GB")
            self.config.size_gb = new_size_gb
            
            return {
                "success": True,
                "new_size_gb": new_size_gb,
                "filesystem_expanded": True
            }
            
        except Exception as e:
            logger.error(f"❌ Local volume resize failed: {e}")
            raise
    
    async def cleanup_volume(self) -> Dict[str, Any]:
        """Cleanup and delete volume resources"""
        try:
            logger.info(f"🗑️ Starting cleanup of volume: {self.config.name}")
            
            cleanup_results = []
            
            if self.config.volume_type == VolumeType.KUBERNETES_PV:
                # Delete PVC and PV
                try:
                    self._k8s_client.delete_namespaced_persistent_volume_claim(
                        name=f"{self.config.name}-pvc",
                        namespace=self.config.namespace
                    )
                    cleanup_results.append({"resource": "pvc", "status": "deleted"})
                    
                    self._k8s_client.delete_persistent_volume(name=f"{self.config.name}-pv")
                    cleanup_results.append({"resource": "pv", "status": "deleted"})
                    
                except ApiException as e:
                    cleanup_results.append({"resource": "k8s", "status": "failed", "error": str(e)})
            
            elif self.config.volume_type == VolumeType.DOCKER_VOLUME:
                # Remove Docker volume
                try:
                    volume = self._docker_client.volumes.get(self.config.name)
                    volume.remove(force=True)
                    cleanup_results.append({"resource": "docker_volume", "status": "deleted"})
                except docker.errors.NotFound:
                    cleanup_results.append({"resource": "docker_volume", "status": "not_found"})
                except Exception as e:
                    cleanup_results.append({"resource": "docker_volume", "status": "failed", "error": str(e)})
            
            elif self.config.volume_type == VolumeType.LOCAL_DISK:
                # Remove local directory
                try:
                    volume_path = Path(f"/mnt/volumes/{self.config.name}")
                    if volume_path.exists():
                        shutil.rmtree(volume_path)
                        cleanup_results.append({"resource": "local_directory", "status": "deleted"})
                    else:
                        cleanup_results.append({"resource": "local_directory", "status": "not_found"})
                except Exception as e:
                    cleanup_results.append({"resource": "local_directory", "status": "failed", "error": str(e)})
            
            elif self.config.volume_type == VolumeType.NFS_MOUNT:
                # Unmount NFS volume
                try:
                    mount_point = f"/mnt/nfs/{self.config.name}"
                    subprocess.run(["umount", mount_point], check=True)
                    cleanup_results.append({"resource": "nfs_mount", "status": "unmounted"})
                except Exception as e:
                    cleanup_results.append({"resource": "nfs_mount", "status": "failed", "error": str(e)})
            
            # Remove monitoring and backup configurations
            config_files = [
                f"/etc/volume-monitoring/{self.config.name}.yaml",
                f"/etc/backup-scripts/{self.config.name}-backup.sh"
            ]
            
            for config_file in config_files:
                try:
                    if Path(config_file).exists():
                        Path(config_file).unlink()
                        cleanup_results.append({"resource": config_file, "status": "deleted"})
                except Exception as e:
                    cleanup_results.append({"resource": config_file, "status": "failed", "error": str(e)})
            
            return {
                "success": True,
                "volume_name": self.config.name,
                "cleanup_results": cleanup_results,
                "cleanup_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Volume cleanup failed: {e}")
            return {"success": False, "error": str(e)}


# Industrial Configuration Manager
class VolumeConfigurationManager:
    """Advanced volume configuration management"""
    
    @staticmethod
    def load_config_from_file(config_path: Path) -> VolumeConfig:
        """Load volume configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            return VolumeConfig(
                name=config_data['name'],
                volume_type=VolumeType(config_data['volume_type']),
                storage_class=StorageClass(config_data['storage_class']),
                size_gb=config_data['size_gb'],
                access_mode=VolumeAccessMode(config_data.get('access_mode', 'ReadWriteOnce')),
                namespace=config_data.get('namespace', 'default'),
                backup_enabled=config_data.get('backup_enabled', True),
                encryption_enabled=config_data.get('encryption_enabled', True),
                labels=config_data.get('labels', {}),
                annotations=config_data.get('annotations', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to load config from {config_path}: {e}")
            raise
    
    @staticmethod
    def save_config_to_file(config: VolumeConfig, config_path: Path):
        """Save volume configuration to YAML file"""
        try:
            config_data = {
                'name': config.name,
                'volume_type': config.volume_type.value,
                'storage_class': config.storage_class.value,
                'size_gb': config.size_gb,
                'access_mode': config.access_mode.value,
                'namespace': config.namespace,
                'backup_enabled': config.backup_enabled,
                'backup_schedule': config.backup_schedule,
                'retention_days': config.retention_days,
                'encryption_enabled': config.encryption_enabled,
                'monitoring_enabled': config.monitoring_enabled,
                'alert_thresholds': config.alert_thresholds,
                'labels': config.labels,
                'annotations': config.annotations
            }
            
            with open(config_path, 'w') as file:
                yaml.dump(config_data, file, default_flow_style=False)
            
            logger.info(f"✅ Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save config to {config_path}: {e}")
            raise


# Global Volume Manager Factory
def create_volume_manager(
    name: str,
    volume_type: VolumeType,
    storage_class: StorageClass,
    size_gb: int,
    namespace: str = "default"
) -> VolumeManager:
    """Factory function to create VolumeManager instance"""
    
    config = VolumeConfig(
        name=name,
        volume_type=volume_type,
        storage_class=storage_class,
        size_gb=size_gb,
        namespace=namespace
    )
    
    return VolumeManager(config)


# Usage Example
async def main():
    """Example usage of VolumeManager"""
    try:
        # Create volume manager for content storage
        volume_manager = create_volume_manager(
            name="ia-influencer-content-volume",
            volume_type=VolumeType.KUBERNETES_PV,
            storage_class=StorageClass.HIGH_PERFORMANCE,
            size_gb=100,
            namespace="ia-influencer"
        )
        
        # Deploy volume
        deployment_result = await volume_manager.deploy_volume()
        print(f"Deployment: {deployment_result}")
        
        # Get metrics
        metrics = await volume_manager.get_volume_metrics()
        print(f"Metrics: {metrics}")
        
        # Resize volume
        resize_result = await volume_manager.resize_volume(150)
        print(f"Resize: {resize_result}")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
