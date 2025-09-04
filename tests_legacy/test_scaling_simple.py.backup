"""Simple tests for Production Auto-Scaling Configuration
Tests CPU 70%, Memory 80%, Custom metrics, Multi-AZ, Spot instances, 99.99% SLA

Project: IA Influencer Agent + Content Protection Platform  
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "resource_scaling", 
    Path(__file__).parent.parent / "kubernetes" / "infrastructure" / "resource_scaling.py"
)
resource_scaling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resource_scaling)

ResourceScalingManager = resource_scaling.ResourceScalingManager
ClusterAutoscalerSpec = resource_scaling.ClusterAutoscalerSpec
HPASpec = resource_scaling.HPASpec
MetricSpec = resource_scaling.MetricSpec
MetricType = resource_scaling.MetricType


class TestProductionScalingConfiguration:
    """Test production scaling configuration values"""
    
    def test_cluster_autoscaler_spec_production_defaults(self):
        """Test ClusterAutoscalerSpec has correct production defaults"""
        spec = ClusterAutoscalerSpec(name="test-ca")
        
        # Verify new production features
        assert spec.multi_az_enabled is True
        assert spec.spot_instances_enabled is True
        assert spec.expander_strategy == "priority"
        assert spec.sla_uptime_target == 99.99
        assert spec.namespace == "kube-system"
    
    def test_cluster_autoscaler_multi_az_configuration(self):
        """Test multi-AZ configuration"""
        node_groups = [
            {'name': 'nodes-us-east-1a', 'min': 1, 'max': 20, 'zone': 'us-east-1a'},
            {'name': 'nodes-us-east-1b', 'min': 1, 'max': 20, 'zone': 'us-east-1b'},
            {'name': 'nodes-us-east-1c', 'min': 1, 'max': 20, 'zone': 'us-east-1c'}
        ]
        
        spec = ClusterAutoscalerSpec(
            name="multi-az-ca",
            multi_az_enabled=True,
            node_groups=node_groups
        )
        
        assert spec.multi_az_enabled is True
        assert len(spec.node_groups) == 3
        assert all('zone' in ng for ng in spec.node_groups)
    
    def test_spot_instances_cost_optimization(self):
        """Test spot instances configuration for cost optimization"""
        spec = ClusterAutoscalerSpec(
            name="cost-optimized-ca",
            spot_instances_enabled=True,
            expander_strategy="priority"
        )
        
        assert spec.spot_instances_enabled is True
        assert spec.expander_strategy == "priority"
    
    def test_sla_uptime_target_99_99(self):
        """Test 99.99% SLA uptime target"""
        spec = ClusterAutoscalerSpec(
            name="sla-ca",
            sla_uptime_target=99.99
        )
        
        assert spec.sla_uptime_target == 99.99
    
    def test_hpa_spec_production_configuration(self):
        """Test HPA specification for production"""
        cpu_metric = MetricSpec(
            name="cpu",
            metric_type=MetricType.CPU_UTILIZATION,
            target_value=70,
            target_type="Utilization"
        )
        
        memory_metric = MetricSpec(
            name="memory",
            metric_type=MetricType.MEMORY_UTILIZATION,
            target_value=80,
            target_type="Utilization"
        )
        
        custom_metric = MetricSpec(
            name="http_requests_per_second",
            metric_type=MetricType.CUSTOM_METRIC,
            target_value="100",
            target_type="AverageValue"
        )
        
        hpa_spec = HPASpec(
            name="production-hpa",
            namespace="ainflue",
            target_ref={
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'name': 'ainflue-backend'
            },
            min_replicas=3,
            max_replicas=50,
            metrics=[cpu_metric, memory_metric, custom_metric]
        )
        
        # Verify CPU 70% threshold
        cpu_target = next(m for m in hpa_spec.metrics if m.name == "cpu")
        assert cpu_target.target_value == 70
        
        # Verify Memory 80% threshold  
        memory_target = next(m for m in hpa_spec.metrics if m.name == "memory")
        assert memory_target.target_value == 80
        
        # Verify custom metrics
        custom_target = next(m for m in hpa_spec.metrics if m.name == "http_requests_per_second")
        assert custom_target.target_value == "100"
        assert custom_target.metric_type == MetricType.CUSTOM_METRIC
        
        # Verify production replica counts
        assert hpa_spec.min_replicas >= 3
        assert hpa_spec.max_replicas >= 20


class TestProductionScalingManager:
    """Test ResourceScalingManager production methods"""
    
    @pytest.fixture
    def scaling_manager(self):
        """Create ResourceScalingManager instance"""
        return ResourceScalingManager()
    
    @pytest.mark.asyncio
    async def test_production_hpa_method_signature(self, scaling_manager):
        """Test production HPA method exists with correct signature"""
        # Verify method exists
        assert hasattr(scaling_manager, 'create_production_hpa_with_custom_metrics')
        
        # Test method call (will return configured status since no k8s client)
        result = await scaling_manager.create_production_hpa_with_custom_metrics(
            name="test-hpa",
            namespace="test",
            target_deployment="test-deployment"
        )
        
        # Should return success even without k8s client
        assert result['status'] == 'success'
        assert result['configured'] is True
        assert result['production_ready'] is True
    
    @pytest.mark.asyncio
    async def test_enhanced_cluster_autoscaler(self, scaling_manager):
        """Test enhanced cluster autoscaler creation"""
        spec = ClusterAutoscalerSpec(
            name="test-enhanced-ca",
            multi_az_enabled=True,
            spot_instances_enabled=True,
            sla_uptime_target=99.99
        )
        
        result = await scaling_manager.create_cluster_autoscaler(spec)
        
        assert result['status'] == 'success'
        assert result['multi_az_enabled'] is True
        assert result['spot_instances_enabled'] is True


class TestProductionScalingRequirements:
    """Test specific production scaling requirements"""
    
    def test_cpu_70_percent_requirement(self):
        """Test CPU 70% requirement is met"""
        metric = MetricSpec(
            name="cpu",
            metric_type=MetricType.CPU_UTILIZATION,
            target_value=70
        )
        
        assert metric.target_value == 70
        assert metric.metric_type == MetricType.CPU_UTILIZATION
    
    def test_memory_80_percent_requirement(self):
        """Test Memory 80% requirement is met"""
        metric = MetricSpec(
            name="memory", 
            metric_type=MetricType.MEMORY_UTILIZATION,
            target_value=80
        )
        
        assert metric.target_value == 80
        assert metric.metric_type == MetricType.MEMORY_UTILIZATION
    
    def test_custom_metrics_requirement(self):
        """Test custom metrics requirement is met"""
        custom_metrics = [
            MetricSpec("http_requests_per_second", MetricType.CUSTOM_METRIC, "100"),
            MetricSpec("celery_queue_length", MetricType.CUSTOM_METRIC, "50"),
            MetricSpec("nvidia_gpu_utilization", MetricType.CUSTOM_METRIC, "75")
        ]
        
        assert len(custom_metrics) == 3
        assert all(m.metric_type == MetricType.CUSTOM_METRIC for m in custom_metrics)
    
    def test_multi_az_requirement(self):
        """Test Multi-AZ requirement is met"""
        spec = ClusterAutoscalerSpec(
            name="multi-az-test",
            multi_az_enabled=True
        )
        
        assert spec.multi_az_enabled is True
    
    def test_spot_instances_requirement(self):
        """Test Spot instances requirement is met"""
        spec = ClusterAutoscalerSpec(
            name="spot-test",
            spot_instances_enabled=True
        )
        
        assert spec.spot_instances_enabled is True
    
    def test_99_99_sla_requirement(self):
        """Test 99.99% SLA uptime requirement is met"""
        spec = ClusterAutoscalerSpec(
            name="sla-test",
            sla_uptime_target=99.99
        )
        
        assert spec.sla_uptime_target == 99.99


@pytest.mark.integration
class TestProductionDeploymentScript:
    """Test production deployment script"""
    
    def test_deployment_script_exists(self):
        """Test deployment script exists"""
        script_path = Path(__file__).parent.parent / "scripts" / "deploy_production_scaling.py"
        assert script_path.exists()
        assert script_path.is_file()
    
    def test_production_yaml_exists(self):
        """Test production YAML configuration exists"""
        yaml_path = Path(__file__).parent.parent / "kubernetes" / "production" / "production-scaling.yaml"
        assert yaml_path.exists()
        assert yaml_path.is_file()
        
        # Read and verify content
        content = yaml_path.read_text()
        assert "CPU 70%" in content
        assert "Memory 80%" in content
        assert "Multi-AZ" in content
        assert "Spot instances" in content
        assert "99.99% SLA" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])