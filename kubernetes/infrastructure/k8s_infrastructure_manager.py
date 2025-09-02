"""Kubernetes Infrastructure Integration Module
===========================================

Complete Kubernetes infrastructure setup with all components
integrated for the Ainflue platform deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import all infrastructure managers
from ..security.network_policies import NetworkPolicyManager
from ..security.pod_security_standards import PodSecurityManager, SecurityLevel
from .resource_management import ResourceManager, EnvironmentType
from .service_mesh_observability import ServiceMeshObservabilityManager, ServiceMeshObservabilityConfig, ServiceMeshType
from .ingress_tls_manager import IngressTLSManager, IngressConfig, TLSConfig, IngressControllerType
from .storage_classes import StorageClassManager
from .etcd_backup import ETCDBackupManager, ETCDBackupConfig, BackupProvider
from .cluster_autoscaler import ClusterAutoscalerManager, AutoscalingConfig, CloudProvider
from .multi_zone_deployment import MultiZoneManager, MultiZoneConfig, DeploymentStrategy
from .cluster_health_monitor import ClusterHealthMonitor, MonitoringConfig

logger = logging.getLogger(__name__)


@dataclass
class KubernetesInfrastructureConfig:
    """Complete Kubernetes infrastructure configuration"""
    cluster_name: str = "ia-influencer-cluster"
    namespace: str = "ia-influencer"
    environment: EnvironmentType = EnvironmentType.PRODUCTION
    cloud_provider: CloudProvider = CloudProvider.AWS
    region: str = "eu-central-1"
    
    # Component enablement
    enable_network_policies: bool = True
    enable_pod_security: bool = True
    enable_resource_management: bool = True
    enable_service_mesh: bool = True
    enable_ingress_tls: bool = True
    enable_storage_classes: bool = True
    enable_etcd_backup: bool = True
    enable_cluster_autoscaler: bool = True
    enable_multi_zone: bool = True
    enable_monitoring: bool = True
    
    # Domain configuration
    domains: List[str] = None
    tls_email: str = "admin@ainflue.com"
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.domains = ["*.ainflue.com", "ainflue.com"]


class KubernetesInfrastructureManager:
    """Complete Kubernetes infrastructure manager"""
    
    def __init__(self, config: KubernetesInfrastructureConfig):
        self.config = config
        self.managers = {}
        self._initialize_managers()
    
    def _initialize_managers(self):
        """Initialize all infrastructure managers"""
        logger.info("Initializing Kubernetes infrastructure managers...")
        
        # Network Policies
        if self.config.enable_network_policies:
            self.managers['network_policies'] = NetworkPolicyManager(self.config.namespace)
        
        # Pod Security Standards
        if self.config.enable_pod_security:
            self.managers['pod_security'] = PodSecurityManager(self.config.namespace)
        
        # Resource Management
        if self.config.enable_resource_management:
            self.managers['resource_management'] = ResourceManager(self.config.namespace)
        
        # Service Mesh Observability
        if self.config.enable_service_mesh:
            service_mesh_config = ServiceMeshObservabilityConfig(
                mesh_type=ServiceMeshType.ISTIO,
                namespace=self.config.namespace,
                tracing_enabled=True,
                metrics_enabled=True,
                logging_enabled=True
            )
            self.managers['service_mesh'] = ServiceMeshObservabilityManager(service_mesh_config)
        
        # Ingress with TLS
        if self.config.enable_ingress_tls:
            tls_config = TLSConfig(
                enabled=True,
                email=self.config.tls_email,
                domains=self.config.domains
            )
            ingress_config = IngressConfig(
                name="ia-influencer",
                namespace=self.config.namespace,
                controller_type=IngressControllerType.NGINX,
                tls_config=tls_config
            )
            self.managers['ingress_tls'] = IngressTLSManager(ingress_config)
        
        # Storage Classes
        if self.config.enable_storage_classes:
            self.managers['storage_classes'] = StorageClassManager(self.config.cloud_provider.value)
        
        # ETCD Backup
        if self.config.enable_etcd_backup:
            etcd_config = ETCDBackupConfig(
                provider=BackupProvider.AWS_S3 if self.config.cloud_provider == CloudProvider.AWS else BackupProvider.MINIO,
                bucket_name=f"{self.config.cluster_name}-etcd-backups"
            )
            self.managers['etcd_backup'] = ETCDBackupManager(etcd_config)
        
        # Cluster Autoscaler
        if self.config.enable_cluster_autoscaler:
            autoscaling_config = AutoscalingConfig(
                cloud_provider=self.config.cloud_provider,
                cluster_name=self.config.cluster_name,
                region=self.config.region
            )
            self.managers['cluster_autoscaler'] = ClusterAutoscalerManager(autoscaling_config)
        
        # Multi-Zone Deployment
        if self.config.enable_multi_zone:
            multizone_config = MultiZoneConfig(
                cluster_name=self.config.cluster_name,
                strategy=DeploymentStrategy.ACTIVE_ACTIVE
            )
            self.managers['multi_zone'] = MultiZoneManager(multizone_config)
        
        # Cluster Health Monitoring
        if self.config.enable_monitoring:
            monitoring_config = MonitoringConfig(
                cluster_name=self.config.cluster_name
            )
            self.managers['monitoring'] = ClusterHealthMonitor(monitoring_config)
        
        logger.info(f"Initialized {len(self.managers)} infrastructure managers")
    
    def generate_all_manifests(self) -> Dict[str, Dict[str, str]]:
        """Generate all Kubernetes manifests from all managers"""
        all_manifests = {}
        
        logger.info("Generating all Kubernetes infrastructure manifests...")
        
        for manager_name, manager in self.managers.items():
            try:
                logger.info(f"Generating manifests for {manager_name}...")
                
                if hasattr(manager, 'generate_all_manifests'):
                    manifests = manager.generate_all_manifests()
                elif hasattr(manager, 'generate_all_security_manifests'):
                    manifests = manager.generate_all_security_manifests()
                elif hasattr(manager, 'generate_all_resource_manifests'):
                    manifests = manager.generate_all_resource_manifests()
                elif hasattr(manager, 'generate_all_observability_manifests'):
                    manifests = manager.generate_all_observability_manifests()
                elif hasattr(manager, 'generate_all_ingress_manifests'):
                    manifests = manager.generate_all_ingress_manifests()
                else:
                    logger.warning(f"Manager {manager_name} doesn't have manifest generation method")
                    continue
                
                all_manifests[manager_name] = manifests
                logger.info(f"Generated {len(manifests)} manifests for {manager_name}")
                
            except Exception as e:
                logger.error(f"Error generating manifests for {manager_name}: {e}")
                continue
        
        total_manifests = sum(len(manifests) for manifests in all_manifests.values())
        logger.info(f"Generated total of {total_manifests} manifests across {len(all_manifests)} components")
        
        return all_manifests
    
    def save_all_manifests(self, base_output_dir: str = "./k8s-manifests") -> int:
        """Save all manifests to organized directory structure"""
        logger.info(f"Saving all manifests to {base_output_dir}...")
        
        all_manifests = self.generate_all_manifests()
        total_files = 0
        
        for manager_name, manifests in all_manifests.items():
            if not manifests:
                continue
                
            # Create manager-specific directory
            manager_dir = os.path.join(base_output_dir, manager_name.replace('_', '-'))
            os.makedirs(manager_dir, exist_ok=True)
            
            # Save manifests to files
            for manifest_name, manifest_content in manifests.items():
                file_path = os.path.join(manager_dir, f"{manifest_name}.yaml")
                with open(file_path, 'w') as f:
                    f.write(manifest_content)
                total_files += 1
                logger.debug(f"Saved manifest: {file_path}")
            
            logger.info(f"Saved {len(manifests)} manifests for {manager_name} in {manager_dir}")
        
        # Create main kustomization file
        self._create_main_kustomization(base_output_dir, all_manifests)
        
        logger.info(f"Successfully saved {total_files} manifest files to {base_output_dir}")
        return total_files
    
    def _create_main_kustomization(self, base_dir: str, all_manifests: Dict[str, Dict[str, str]]):
        """Create main kustomization.yaml file"""
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "metadata": {
                "name": f"{self.config.cluster_name}-infrastructure"
            },
            "resources": []
        }
        
        # Add all manifest files as resources
        for manager_name, manifests in all_manifests.items():
            manager_dir = manager_name.replace('_', '-')
            for manifest_name in manifests.keys():
                kustomization["resources"].append(f"{manager_dir}/{manifest_name}.yaml")
        
        # Create namespace
        kustomization["namespace"] = self.config.namespace
        
        # Add common labels
        kustomization["commonLabels"] = {
            "app.kubernetes.io/name": "ia-influencer",
            "app.kubernetes.io/instance": self.config.cluster_name,
            "app.kubernetes.io/version": "v1.0.0",
            "app.kubernetes.io/managed-by": "kubernetes-infrastructure-manager"
        }
        
        # Save kustomization file
        import yaml
        kustomization_path = os.path.join(base_dir, "kustomization.yaml")
        with open(kustomization_path, 'w') as f:
            yaml.dump(kustomization, f, default_flow_style=False)
        
        logger.info(f"Created main kustomization file: {kustomization_path}")
    
    def get_deployment_summary(self) -> Dict[str, Any]:
        """Get deployment summary information"""
        return {
            "cluster_name": self.config.cluster_name,
            "namespace": self.config.namespace,
            "environment": self.config.environment.value,
            "cloud_provider": self.config.cloud_provider.value,
            "region": self.config.region,
            "enabled_components": {
                component: enabled for component, enabled in {
                    "network_policies": self.config.enable_network_policies,
                    "pod_security": self.config.enable_pod_security,
                    "resource_management": self.config.enable_resource_management,
                    "service_mesh": self.config.enable_service_mesh,
                    "ingress_tls": self.config.enable_ingress_tls,
                    "storage_classes": self.config.enable_storage_classes,
                    "etcd_backup": self.config.enable_etcd_backup,
                    "cluster_autoscaler": self.config.enable_cluster_autoscaler,
                    "multi_zone": self.config.enable_multi_zone,
                    "monitoring": self.config.enable_monitoring
                }.items() if enabled
            },
            "total_managers": len(self.managers),
            "domains": self.config.domains
        }


# Export main functionality for integration
__k8s_infrastructure__ = [
    'KubernetesInfrastructureManager', 
    'KubernetesInfrastructureConfig',
    # Re-export all managers for convenience
    'NetworkPolicyManager',
    'PodSecurityManager',
    'ResourceManager',
    'ServiceMeshObservabilityManager',
    'IngressTLSManager',
    'StorageClassManager',
    'ETCDBackupManager',
    'ClusterAutoscalerManager',
    'MultiZoneManager',
    'ClusterHealthMonitor'
]