#!/usr/bin/env python3
"""
Autoscaling Configuration Validation Test
Tests the comprehensive autoscaling setup for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import yaml
import sys
import os
from typing import Dict, List, Any


class AutoscalingConfigValidator:
    """Validator for autoscaling configuration"""
    
    def __init__(self, base_path: str = "/home/runner/work/Ainflue/Ainflue"):
        self.base_path = base_path
        self.k8s_path = os.path.join(base_path, "k8s/production")
        self.monitoring_path = os.path.join(base_path, "monitoring/prometheus")
    
    def load_yaml_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and parse YAML file"""
        with open(file_path, 'r') as f:
            return list(yaml.safe_load_all(f))
    
    def test_hpa_configuration(self):
        """Test HPA configuration meets requirements"""
        hpa_file = os.path.join(self.k8s_path, "hpa.yaml")
        hpas = self.load_yaml_file(hpa_file)
        
        # Filter HPA resources
        hpa_resources = [doc for doc in hpas if doc and doc.get('kind') == 'HorizontalPodAutoscaler']
        
        assert len(hpa_resources) >= 6, "Should have at least 6 HPA configurations"
        
        # Check API HPA
        api_hpa = next((hpa for hpa in hpa_resources if hpa['metadata']['name'] == 'ainflue-api-hpa'), None)
        assert api_hpa is not None, "API HPA should exist"
        
        # Validate CPU and Memory thresholds
        metrics = api_hpa['spec']['metrics']
        cpu_metric = next((m for m in metrics if m['type'] == 'Resource' and m['resource']['name'] == 'cpu'), None)
        memory_metric = next((m for m in metrics if m['type'] == 'Resource' and m['resource']['name'] == 'memory'), None)
        
        assert cpu_metric is not None, "CPU metric should be configured"
        assert memory_metric is not None, "Memory metric should be configured"
        assert cpu_metric['resource']['target']['averageUtilization'] == 70, "CPU threshold should be 70%"
        assert memory_metric['resource']['target']['averageUtilization'] == 80, "Memory threshold should be 80%"
        
        # Check custom metrics
        custom_metrics = [m for m in metrics if m['type'] in ['Pods', 'Object']]
        assert len(custom_metrics) >= 1, "Should have custom metrics configured"
        
        print("✅ HPA configuration validation passed")
    
    def test_cluster_autoscaler_configuration(self):
        """Test cluster autoscaler configuration"""
        ca_file = os.path.join(self.k8s_path, "cluster-autoscaler.yaml")
        ca_resources = self.load_yaml_file(ca_file)
        
        # Check deployment exists
        deployment = next((doc for doc in ca_resources if doc and doc.get('kind') == 'Deployment'), None)
        assert deployment is not None, "Cluster Autoscaler deployment should exist"
        assert deployment['metadata']['name'] == 'cluster-autoscaler', "Should be named cluster-autoscaler"
        
        # Check service account and RBAC
        sa = next((doc for doc in ca_resources if doc and doc.get('kind') == 'ServiceAccount'), None)
        cluster_role = next((doc for doc in ca_resources if doc and doc.get('kind') == 'ClusterRole'), None)
        cluster_role_binding = next((doc for doc in ca_resources if doc and doc.get('kind') == 'ClusterRoleBinding'), None)
        
        assert sa is not None, "Service account should exist"
        assert cluster_role is not None, "Cluster role should exist"
        assert cluster_role_binding is not None, "Cluster role binding should exist"
        
        # Check multi-AZ configuration in command args
        container = deployment['spec']['template']['spec']['containers'][0]
        command_args = container['command']
        
        multi_az_args = [arg for arg in command_args if 'node-group-auto-discovery' in arg]
        assert len(multi_az_args) >= 1, "Should have node group auto-discovery configured"
        
        print("✅ Cluster Autoscaler configuration validation passed")
    
    def test_spot_instance_configuration(self):
        """Test spot instance node group configuration"""
        spot_file = os.path.join(self.k8s_path, "spot-node-groups.yaml")
        spot_resources = self.load_yaml_file(spot_file)
        
        # Filter node groups
        node_groups = [doc for doc in spot_resources if doc and doc.get('kind') == 'InstanceGroup']
        
        # Should have spot instance configurations for multiple AZs
        assert len(node_groups) >= 3, "Should have spot instance configurations for multiple AZs"
        
        # Check AZ distribution
        az_groups = [ng for ng in node_groups if 'us-east-1' in ng['metadata']['name']]
        assert len(az_groups) >= 3, "Should have configurations for us-east-1a, us-east-1b, us-east-1c"
        
        # Check spot instance settings
        spot_general = next((ng for ng in node_groups if 'spot-general' in ng['metadata']['name']), None)
        if spot_general:
            assert 'spot-instance' in spot_general['metadata']['labels'].get('cost-optimization', ''), "Should be labeled as spot instance"
            
            # Check spot price limit
            if 'spotMaxPrice' in spot_general['spec']:
                spot_price = float(spot_general['spec']['spotMaxPrice'])
                assert spot_price <= 1.0, "Spot price should be reasonable for cost optimization"
        
        # Check termination handler
        termination_handler = next((doc for doc in spot_resources if doc and doc.get('kind') == 'DaemonSet'), None)
        assert termination_handler is not None, "Should have spot termination handler"
        
        print("✅ Spot instance configuration validation passed")
    
    def test_sla_monitoring_configuration(self):
        """Test SLA monitoring rules"""
        sla_file = os.path.join(self.monitoring_path, "sla_alert_rules.yml")
        sla_config = self.load_yaml_file(sla_file)[0]  # Single document
        
        assert 'groups' in sla_config, "Should have alert rule groups"
        
        groups = sla_config['groups']
        sla_group = next((g for g in groups if 'sla' in g['name']), None)
        assert sla_group is not None, "Should have SLA alert group"
        
        # Check for key SLA alerts
        rules = sla_group['rules']
        
        # Availability alerts
        availability_alerts = [r for r in rules if 'availability' in r.get('alert', '').lower()]
        assert len(availability_alerts) >= 2, "Should have availability SLA alerts"
        
        # Check 99.99% target in expressions
        api_availability_alert = next((r for r in availability_alerts if 'API' in r.get('alert', '')), None)
        if api_availability_alert:
            expr = api_availability_alert['expr']
            assert '99.99' in expr, "Should target 99.99% availability"
        
        # Latency alerts
        latency_alerts = [r for r in rules if 'latency' in r.get('alert', '').lower()]
        assert len(latency_alerts) >= 1, "Should have latency SLA alerts"
        
        # Error rate alerts
        error_alerts = [r for r in rules if 'error' in r.get('alert', '').lower()]
        assert len(error_alerts) >= 1, "Should have error rate SLA alerts"
        
        print("✅ SLA monitoring configuration validation passed")
    
    def test_autoscaling_integration_configuration(self):
        """Test integrated autoscaling configuration"""
        config_file = os.path.join(self.k8s_path, "autoscaling-config.yaml")
        config_resources = self.load_yaml_file(config_file)
        
        # Check policy engine deployment
        policy_engine = next((doc for doc in config_resources if doc and doc.get('kind') == 'Deployment' and 
                             'policy-engine' in doc['metadata']['name']), None)
        assert policy_engine is not None, "Should have autoscaling policy engine"
        
        # Check configuration ConfigMap
        config_map = next((doc for doc in config_resources if doc and doc.get('kind') == 'ConfigMap' and 
                          'autoscaling-config' in doc['metadata']['name']), None)
        assert config_map is not None, "Should have autoscaling configuration"
        
        # Validate configuration data
        config_data = config_map['data']
        assert 'hpa-config.yaml' in config_data, "Should have HPA configuration"
        assert 'cluster-autoscaler-config.yaml' in config_data, "Should have cluster autoscaler configuration"
        assert 'sla-config.yaml' in config_data, "Should have SLA configuration"
        
        # Parse SLA config
        sla_config = yaml.safe_load(config_data['sla-config.yaml'])
        sla_targets = sla_config['sla_targets']
        assert sla_targets['availability'] == 99.99, "SLA availability target should be 99.99%"
        assert sla_targets['latency_p95'] == 200, "SLA latency target should be 200ms"
        assert sla_targets['error_rate'] == 0.01, "SLA error rate target should be 0.01%"
        
        print("✅ Autoscaling integration configuration validation passed")
    
    def test_deployment_script_exists(self):
        """Test deployment script exists and is executable"""
        script_path = os.path.join(self.k8s_path, "deploy-autoscaling.sh")
        assert os.path.exists(script_path), "Deployment script should exist"
        assert os.access(script_path, os.X_OK), "Deployment script should be executable"
        
        # Check script contains key functions
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'check_prerequisites' in content, "Should have prerequisites check"
        assert 'create_iam_roles' in content, "Should have IAM role creation"
        assert 'deploy_autoscaling_components' in content, "Should have component deployment"
        assert 'verify_deployment' in content, "Should have deployment verification"
        
        print("✅ Deployment script validation passed")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🔍 Starting autoscaling configuration validation...")
        print()
        
        try:
            self.test_hpa_configuration()
            self.test_cluster_autoscaler_configuration()
            self.test_spot_instance_configuration()
            self.test_sla_monitoring_configuration()
            self.test_autoscaling_integration_configuration()
            self.test_deployment_script_exists()
            
            print()
            print("🎉 All autoscaling configuration validations passed!")
            print("✅ HPA: CPU 70%, Memory 80%, Custom metrics configured")
            print("✅ Cluster Autoscaler: Multi-AZ support enabled")
            print("✅ Spot Instances: Cost optimization configured")
            print("✅ SLA Monitoring: 99.99% uptime target set")
            print("✅ Integration: Components properly coordinated")
            print("✅ Deployment: Automation script ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False


def main():
    """Main test execution"""
    validator = AutoscalingConfigValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()