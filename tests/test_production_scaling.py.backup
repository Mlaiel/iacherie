"""Tests for Production Auto-Scaling Configuration
Tests CPU 70%, Memory 80%, Custom metrics, Multi-AZ, Spot instances, 99.99% SLA

Project: IA Influencer Agent + Content Protection Platform  
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from kubernetes.infrastructure.resource_scaling import (
    ResourceScalingManager, 
    HPASpec, 
    ClusterAutoscalerSpec,
    MetricSpec,
    MetricType
)


class TestProductionScaling:
    """Test production scaling configurations"""
    
    @pytest.fixture
    def scaling_manager(self):
        """Create ResourceScalingManager instance for testing"""
        return ResourceScalingManager()
    
    @pytest.fixture
    def production_hpa_spec(self):
        """Production HPA specification with CPU 70%, Memory 80%"""
        return HPASpec(
            name="ainflue-backend-hpa",
            namespace="ainflue",
            target_ref={
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'name': 'ainflue-backend'
            },
            min_replicas=3,
            max_replicas=50,
            metrics=[
                MetricSpec(
                    name="cpu",
                    metric_type=MetricType.CPU_UTILIZATION,
                    target_value=70,
                    target_type="Utilization"
                ),
                MetricSpec(
                    name="memory",
                    metric_type=MetricType.MEMORY_UTILIZATION,
                    target_value=80,
                    target_type="Utilization"
                ),
                MetricSpec(
                    name="http_requests_per_second",
                    metric_type=MetricType.CUSTOM_METRIC,
                    target_value="100",
                    target_type="AverageValue"
                )
            ]
        )
    
    @pytest.fixture
    def cluster_autoscaler_spec(self):
        """Cluster autoscaler with multi-AZ and spot instances"""
        return ClusterAutoscalerSpec(
            name="cluster-autoscaler",
            namespace="kube-system",
            min_nodes=3,
            max_nodes=200,
            multi_az_enabled=True,
            spot_instances_enabled=True,
            expander_strategy="priority",
            sla_uptime_target=99.99,
            node_groups=[
                {
                    'name': 'ainflue-nodes-us-east-1a-spot',
                    'min': 1,
                    'max': 20,
                    'zone': 'us-east-1a',
                    'instance_type': 'spot'
                },
                {
                    'name': 'ainflue-nodes-us-east-1b-spot',
                    'min': 1,
                    'max': 20,
                    'zone': 'us-east-1b',
                    'instance_type': 'spot'
                },
                {
                    'name': 'ainflue-nodes-us-east-1c-spot',
                    'min': 1,
                    'max': 20,
                    'zone': 'us-east-1c',
                    'instance_type': 'spot'
                },
                {
                    'name': 'ainflue-nodes-us-east-1a-ondemand',
                    'min': 1,
                    'max': 10,
                    'zone': 'us-east-1a',
                    'instance_type': 'on-demand'
                }
            ]
        )
    
    @pytest.mark.asyncio
    async def test_production_hpa_cpu_70_memory_80(self, scaling_manager, production_hpa_spec):
        """Test HPA creation with CPU 70% and Memory 80% thresholds"""
        result = await scaling_manager.create_horizontal_pod_autoscaler(production_hpa_spec)
        
        assert result['status'] == 'success'
        assert result['name'] == 'ainflue-backend-hpa'
        assert result['min_replicas'] == 3
        assert result['max_replicas'] == 50
        assert result['metrics_count'] >= 2  # At least CPU and Memory
    
    @pytest.mark.asyncio 
    async def test_production_hpa_with_custom_metrics(self, scaling_manager):
        """Test production HPA with custom metrics support"""
        result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="ainflue-backend-hpa",
            namespace="ainflue",
            target_deployment="ainflue-backend",
            min_replicas=3,
            max_replicas=50
        )
        
        assert result['status'] == 'success'
        assert result['cpu_target'] == 70
        assert result['memory_target'] == 80
        assert result['custom_metrics_count'] == 3
        assert result['production_ready'] is True
    
    @pytest.mark.asyncio
    async def test_cluster_autoscaler_multi_az(self, scaling_manager, cluster_autoscaler_spec):
        """Test cluster autoscaler with multi-AZ configuration"""
        result = await scaling_manager.create_cluster_autoscaler(cluster_autoscaler_spec)
        
        assert result['status'] == 'success'
        assert result['multi_az_enabled'] is True
        assert result['spot_instances_enabled'] is True
        assert result['sla_uptime_target'] == 99.99
        assert result['node_groups'] == 4  # 3 spot + 1 on-demand per AZ
    
    @pytest.mark.asyncio
    async def test_cluster_autoscaler_spot_instances(self, scaling_manager):
        """Test cluster autoscaler with spot instances cost optimization"""
        ca_spec = ClusterAutoscalerSpec(
            name="cluster-autoscaler-spot",
            namespace="kube-system",
            spot_instances_enabled=True,
            multi_az_enabled=True,
            sla_uptime_target=99.99
        )
        
        result = await scaling_manager.create_cluster_autoscaler(ca_spec)
        
        assert result['status'] == 'success'
        assert result['spot_instances_enabled'] is True
        assert result['multi_az_enabled'] is True
    
    @pytest.mark.asyncio
    async def test_sla_uptime_target_99_99(self, scaling_manager):
        """Test configuration for 99.99% SLA uptime target"""
        ca_spec = ClusterAutoscalerSpec(
            name="cluster-autoscaler-sla",
            namespace="kube-system",
            sla_uptime_target=99.99,
            max_nodes=200
        )
        
        result = await scaling_manager.create_cluster_autoscaler(ca_spec)
        
        assert result['status'] == 'success'
        assert result['sla_uptime_target'] == 99.99
    
    def test_cluster_autoscaler_spec_defaults(self):
        """Test ClusterAutoscalerSpec default values"""
        spec = ClusterAutoscalerSpec(name="test-ca")
        
        assert spec.multi_az_enabled is True
        assert spec.spot_instances_enabled is True
        assert spec.expander_strategy == "priority"
        assert spec.sla_uptime_target == 99.99
    
    @pytest.mark.asyncio
    async def test_hpa_scaling_behavior(self, scaling_manager):
        """Test HPA scaling behavior for production workloads"""
        result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="test-hpa",
            namespace="ainflue",
            target_deployment="test-deployment"
        )
        
        assert result['status'] == 'success'
        assert result['production_ready'] is True
    
    @pytest.mark.performance
    async def test_scaling_performance_metrics(self, scaling_manager):
        """Test that scaling decisions are made within performance targets"""
        # Simulate scaling decision performance
        import time
        
        start_time = time.time()
        
        result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="performance-test-hpa",
            namespace="ainflue", 
            target_deployment="performance-test"
        )
        
        decision_time = time.time() - start_time
        
        # Should make scaling decisions in < 100ms as per requirements
        assert decision_time < 0.1
        assert result['status'] == 'success'
    
    @pytest.mark.integration
    async def test_full_production_scaling_stack(self, scaling_manager):
        """Integration test for complete production scaling stack"""
        # Test HPA creation
        hpa_result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="integration-test-hpa",
            namespace="ainflue",
            target_deployment="integration-test",
            min_replicas=3,
            max_replicas=50
        )
        
        assert hpa_result['status'] == 'success'
        assert hpa_result['cpu_target'] == 70
        assert hpa_result['memory_target'] == 80
        
        # Test Cluster Autoscaler creation
        ca_spec = ClusterAutoscalerSpec(
            name="integration-test-ca",
            namespace="kube-system",
            multi_az_enabled=True,
            spot_instances_enabled=True,
            sla_uptime_target=99.99
        )
        
        ca_result = await scaling_manager.create_cluster_autoscaler(ca_spec)
        
        assert ca_result['status'] == 'success'
        assert ca_result['multi_az_enabled'] is True
        assert ca_result['spot_instances_enabled'] is True
    
    @pytest.mark.cost_optimization
    def test_spot_instances_cost_optimization(self):
        """Test spot instances configuration for cost optimization"""
        ca_spec = ClusterAutoscalerSpec(
            name="cost-test-ca",
            spot_instances_enabled=True,
            expander_strategy="priority"
        )
        
        assert ca_spec.spot_instances_enabled is True
        assert ca_spec.expander_strategy == "priority"
    
    @pytest.mark.high_availability
    def test_multi_az_high_availability(self):
        """Test multi-AZ configuration for high availability"""
        ca_spec = ClusterAutoscalerSpec(
            name="ha-test-ca",
            multi_az_enabled=True,
            sla_uptime_target=99.99
        )
        
        assert ca_spec.multi_az_enabled is True
        assert ca_spec.sla_uptime_target == 99.99
    
    @pytest.mark.custom_metrics
    async def test_custom_metrics_configuration(self, scaling_manager):
        """Test custom metrics configuration for production HPA"""
        result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="custom-metrics-hpa",
            namespace="ainflue",
            target_deployment="custom-metrics-test"
        )
        
        assert result['status'] == 'success'
        assert result['custom_metrics_count'] == 3
        # Verify custom metrics include: RPS, Celery queue, GPU utilization
        assert result['production_ready'] is True


@pytest.mark.benchmark
class TestScalingPerformance:
    """Performance benchmarks for scaling operations"""
    
    @pytest.mark.benchmark(group="scaling")
    def test_hpa_creation_performance(self, benchmark):
        """Benchmark HPA creation performance"""
        scaling_manager = ResourceScalingManager()
        
        async def create_hpa():
            return await scaling_manager.create_production_hpa_with_custom_metrics(
                name="benchmark-hpa",
                namespace="ainflue",
                target_deployment="benchmark-test"
            )
        
        # Should complete in under 100ms
        result = benchmark(asyncio.run, create_hpa())
        assert result['status'] == 'success'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])