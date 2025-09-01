"""Test Kubernetes Infrastructure Implementation
==========================================

Comprehensive tests for the Kubernetes infrastructure components
to ensure proper functionality and integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import yaml
import tempfile
import os
import sys

# Add the project root to Python path for imports
sys.path.append('/home/runner/work/Ainflue/Ainflue')

# Import the infrastructure managers
from kubernetes.security.network_policies import NetworkPolicyManager
from kubernetes.security.pod_security_standards import PodSecurityManager
from kubernetes.infrastructure.resource_management import ResourceManager
from kubernetes.infrastructure.storage_classes import StorageClassManager
from kubernetes.infrastructure.etcd_backup import ETCDBackupManager
from kubernetes.infrastructure.cluster_autoscaler import ClusterAutoscalerManager


class TestNetworkPolicies:
    """Test network policies implementation"""
    
    def test_network_policy_manager_initialization(self):
        """Test network policy manager initialization"""
        manager = NetworkPolicyManager("test-namespace")
        assert manager.namespace == "test-namespace"
        assert isinstance(manager.policies, dict)
    
    def test_deny_all_policy_creation(self):
        """Test deny-all policy creation"""
        manager = NetworkPolicyManager("test-namespace")
        policy = manager.create_deny_all_policy()
        
        assert policy.name == "deny-all-default"
        assert policy.namespace == "test-namespace"
        assert policy.pod_selector == {}
    
    def test_database_access_policy_creation(self):
        """Test database access policy creation"""
        manager = NetworkPolicyManager("test-namespace")
        policy = manager.create_database_access_policy()
        
        assert policy.name == "database-access-policy"
        assert len(policy.ingress_rules) > 0
        assert any("5432" in str(rule) for rule in policy.ingress_rules)  # PostgreSQL port
    
    def test_network_policy_manifest_generation(self):
        """Test network policy YAML manifest generation"""
        manager = NetworkPolicyManager("test-namespace")
        policy = manager.create_deny_all_policy()
        manifest = manager.to_yaml_manifest(policy)
        
        parsed = yaml.safe_load(manifest)
        assert parsed["apiVersion"] == "networking.k8s.io/v1"
        assert parsed["kind"] == "NetworkPolicy"
        assert parsed["metadata"]["name"] == "deny-all-default"
        assert parsed["metadata"]["namespace"] == "test-namespace"
    
    def test_all_network_policies_generation(self):
        """Test generation of all network policies"""
        manager = NetworkPolicyManager("test-namespace")
        manifests = manager.generate_all_manifests()
        
        assert len(manifests) > 0
        assert "deny-all-network-policy" in manifests
        assert "database-access-network-policy" in manifests
        assert "api-gateway-network-policy" in manifests


class TestPodSecurityStandards:
    """Test pod security standards implementation"""
    
    def test_pod_security_manager_initialization(self):
        """Test pod security manager initialization"""
        manager = PodSecurityManager("test-namespace")
        assert manager.namespace == "test-namespace"
    
    def test_restricted_security_standard_creation(self):
        """Test restricted security standard creation"""
        manager = PodSecurityManager("test-namespace")
        standard = manager.create_restricted_standard("test-namespace")
        
        assert standard.namespace == "test-namespace"
        assert standard.level.value == "restricted"
        assert standard.mode.value == "enforce"
    
    def test_namespace_with_security_labels(self):
        """Test namespace creation with security labels"""
        manager = PodSecurityManager("test-namespace")
        standard = manager.create_restricted_standard("test-namespace")
        namespace = manager.generate_namespace_with_security_labels("test-namespace", standard)
        
        assert namespace["kind"] == "Namespace"
        assert "pod-security.kubernetes.io/enforce" in namespace["metadata"]["labels"]
        assert namespace["metadata"]["labels"]["pod-security.kubernetes.io/enforce"] == "restricted"
    
    def test_security_manifests_generation(self):
        """Test security manifests generation"""
        manager = PodSecurityManager("test-namespace")
        manifests = manager.generate_all_security_manifests()
        
        assert len(manifests) > 0
        assert "production-namespace" in manifests
        assert "restricted-pod-security-policy" in manifests


class TestResourceManagement:
    """Test resource management implementation"""
    
    def test_resource_manager_initialization(self):
        """Test resource manager initialization"""
        manager = ResourceManager("test-namespace")
        assert manager.base_namespace == "test-namespace"
        assert len(manager.workload_specs) > 0
        assert len(manager.environment_quotas) > 0
    
    def test_resource_quota_creation(self):
        """Test resource quota creation"""
        manager = ResourceManager("test-namespace")
        from kubernetes.infrastructure.resource_management import EnvironmentType
        quota_spec = manager.environment_quotas[EnvironmentType.PRODUCTION]
        quota = manager.create_resource_quota(quota_spec)
        
        assert quota["kind"] == "ResourceQuota"
        assert "requests.cpu" in quota["spec"]["hard"]
        assert "limits.memory" in quota["spec"]["hard"]
    
    def test_limit_range_creation(self):
        """Test limit range creation"""
        manager = ResourceManager("test-namespace")
        from kubernetes.infrastructure.resource_management import WorkloadType
        
        limit_range = manager.create_limit_range("test-namespace", WorkloadType.API_GATEWAY)
        
        assert limit_range["kind"] == "LimitRange"
        assert len(limit_range["spec"]["limits"]) > 0
    
    def test_horizontal_pod_autoscaler_creation(self):
        """Test HPA creation"""
        manager = ResourceManager("test-namespace")
        hpa = manager.create_horizontal_pod_autoscaler(
            "test-hpa", "test-namespace", "test-deployment"
        )
        
        assert hpa["kind"] == "HorizontalPodAutoscaler"
        assert hpa["spec"]["scaleTargetRef"]["name"] == "test-deployment"
        assert "metrics" in hpa["spec"]


class TestStorageClasses:
    """Test storage classes implementation"""
    
    def test_storage_class_manager_initialization(self):
        """Test storage class manager initialization"""
        manager = StorageClassManager("aws")
        assert manager.cloud_provider == "aws"
        assert manager.storage_classes is not None
    
    def test_high_performance_storage_creation(self):
        """Test high-performance storage class creation"""
        manager = StorageClassManager("aws")
        storage_spec = manager.create_high_performance_storage()
        
        assert storage_spec.name == "ia-influencer-high-performance"
        assert storage_spec.provisioner == "ebs.csi.aws.com"
        assert "io2" in storage_spec.parameters.get("type", "")
    
    def test_database_storage_creation(self):
        """Test database storage class creation"""
        manager = StorageClassManager("aws")
        storage_spec = manager.create_database_storage()
        
        assert storage_spec.name == "ia-influencer-database"
        assert storage_spec.reclaim_policy.value == "Retain"
    
    def test_storage_class_manifest_generation(self):
        """Test storage class manifest generation"""
        manager = StorageClassManager("aws")
        storage_spec = manager.create_general_purpose_storage()
        manifest = manager.to_kubernetes_manifest(storage_spec)
        
        assert manifest["kind"] == "StorageClass"
        assert manifest["provisioner"] == storage_spec.provisioner
        assert manifest["allowVolumeExpansion"] == storage_spec.allow_volume_expansion


class TestETCDBackup:
    """Test ETCD backup implementation"""
    
    def test_etcd_backup_manager_initialization(self):
        """Test ETCD backup manager initialization"""
        from kubernetes.infrastructure.etcd_backup import ETCDBackupConfig, BackupProvider
        
        config = ETCDBackupConfig(provider=BackupProvider.AWS_S3)
        manager = ETCDBackupManager(config)
        
        assert manager.config.provider == BackupProvider.AWS_S3
        assert manager.config.retention_days == 30
    
    def test_backup_service_account_creation(self):
        """Test backup service account creation"""
        from kubernetes.infrastructure.etcd_backup import ETCDBackupConfig, BackupProvider
        
        config = ETCDBackupConfig(provider=BackupProvider.AWS_S3)
        manager = ETCDBackupManager(config)
        resources = manager.create_backup_service_account()
        
        assert len(resources) >= 3  # ServiceAccount, ClusterRole, ClusterRoleBinding
        assert any(r["kind"] == "ServiceAccount" for r in resources)
        assert any(r["kind"] == "ClusterRole" for r in resources)
    
    def test_backup_cronjob_creation(self):
        """Test backup CronJob creation"""
        from kubernetes.infrastructure.etcd_backup import ETCDBackupConfig, BackupProvider, BackupFrequency
        
        config = ETCDBackupConfig(provider=BackupProvider.AWS_S3, frequency=BackupFrequency.DAILY)
        manager = ETCDBackupManager(config)
        cronjob = manager.create_backup_cronjob()
        
        assert cronjob["kind"] == "CronJob"
        assert cronjob["spec"]["schedule"] == "0 2 * * *"  # Daily at 2 AM


class TestClusterAutoscaler:
    """Test cluster autoscaler implementation"""
    
    def test_cluster_autoscaler_manager_initialization(self):
        """Test cluster autoscaler manager initialization"""
        from kubernetes.infrastructure.cluster_autoscaler import AutoscalingConfig, CloudProvider
        
        config = AutoscalingConfig(cloud_provider=CloudProvider.AWS)
        manager = ClusterAutoscalerManager(config)
        
        assert manager.config.cloud_provider == CloudProvider.AWS
        assert len(manager.config.node_pools) > 0
    
    def test_autoscaler_deployment_creation(self):
        """Test autoscaler deployment creation"""
        from kubernetes.infrastructure.cluster_autoscaler import AutoscalingConfig, CloudProvider
        
        config = AutoscalingConfig(cloud_provider=CloudProvider.AWS)
        manager = ClusterAutoscalerManager(config)
        deployment = manager.create_cluster_autoscaler_deployment()
        
        assert deployment["kind"] == "Deployment"
        assert deployment["metadata"]["name"] == "cluster-autoscaler"
        assert len(deployment["spec"]["template"]["spec"]["containers"]) > 0
    
    def test_priority_expander_configmap_creation(self):
        """Test priority expander ConfigMap creation"""
        from kubernetes.infrastructure.cluster_autoscaler import AutoscalingConfig, CloudProvider
        
        config = AutoscalingConfig(cloud_provider=CloudProvider.AWS)
        manager = ClusterAutoscalerManager(config)
        configmap = manager.create_priority_expander_configmap()
        
        assert configmap["kind"] == "ConfigMap"
        assert "priorities" in configmap["data"]


# Integration test
class TestInfrastructureIntegration:
    """Test infrastructure integration"""
    
    def test_yaml_manifest_validity(self):
        """Test that all generated manifests are valid YAML"""
        # Test network policies
        manager = NetworkPolicyManager("test-namespace")
        manifests = manager.generate_all_manifests()
        
        for manifest_name, manifest_content in manifests.items():
            try:
                parsed = yaml.safe_load(manifest_content)
                assert "apiVersion" in parsed
                assert "kind" in parsed
                assert "metadata" in parsed
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in network policies {manifest_name}: {e}")
    
    def test_kubernetes_manifest_structure(self):
        """Test that manifests follow Kubernetes structure"""
        # Test pod security manifests
        manager = PodSecurityManager("test-namespace")
        manifests = manager.generate_all_security_manifests()
        
        for manifest_name, manifest_content in manifests.items():
            parsed = yaml.safe_load(manifest_content)
            
            # Check required Kubernetes fields
            assert "apiVersion" in parsed
            assert "kind" in parsed
            assert "metadata" in parsed
            assert "name" in parsed["metadata"]
            
            # Check labels if present
            if "labels" in parsed["metadata"]:
                assert isinstance(parsed["metadata"]["labels"], dict)
    
    def test_component_integration(self):
        """Test integration between different components"""
        # Test that storage classes work with resource management
        storage_manager = StorageClassManager("aws")
        resource_manager = ResourceManager("test-namespace")
        
        # Generate manifests from both
        storage_manifests = storage_manager.generate_all_manifests()
        resource_manifests = resource_manager.generate_all_resource_manifests()
        
        # Verify both generate valid manifests
        assert len(storage_manifests) > 0
        assert len(resource_manifests) > 0
        
        # Check for complementary configurations
        assert "storage-class-database" in storage_manifests
        assert any("database" in name for name in resource_manifests.keys())


if __name__ == "__main__":
    # Run specific tests to verify infrastructure
    print("🧪 Testing Kubernetes Infrastructure Implementation...")
    
    # Test network policies
    print("📡 Testing Network Policies...")
    test_net = TestNetworkPolicies()
    test_net.test_network_policy_manager_initialization()
    test_net.test_deny_all_policy_creation()
    test_net.test_database_access_policy_creation()
    test_net.test_all_network_policies_generation()
    print("✅ Network Policies tests passed")
    
    # Test pod security
    print("🔒 Testing Pod Security Standards...")
    test_sec = TestPodSecurityStandards()
    test_sec.test_pod_security_manager_initialization()
    test_sec.test_restricted_security_standard_creation()
    test_sec.test_security_manifests_generation()
    print("✅ Pod Security Standards tests passed")
    
    # Test resource management
    print("📊 Testing Resource Management...")
    test_res = TestResourceManagement()
    test_res.test_resource_manager_initialization()
    test_res.test_resource_quota_creation()
    test_res.test_horizontal_pod_autoscaler_creation()
    print("✅ Resource Management tests passed")
    
    # Test storage classes
    print("💾 Testing Storage Classes...")
    test_stor = TestStorageClasses()
    test_stor.test_storage_class_manager_initialization()
    test_stor.test_high_performance_storage_creation()
    test_stor.test_storage_class_manifest_generation()
    print("✅ Storage Classes tests passed")
    
    # Test integration
    print("🔗 Testing Integration...")
    test_int = TestInfrastructureIntegration()
    test_int.test_yaml_manifest_validity()
    test_int.test_kubernetes_manifest_structure()
    test_int.test_component_integration()
    print("✅ Integration tests passed")
    
    print("🎉 All Kubernetes infrastructure tests completed successfully!")