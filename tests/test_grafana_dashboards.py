# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Test suite for Grafana dashboards and visualization setup
"""

import pytest
import sys
import os
from pathlib import Path
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List

class TestGrafanaDashboards:
    """
Test suite for Grafana dashboard configurations"""
    
    @pytest.fixture
    def project_root(self):
        try:
            logger.info(f"Executing project_root")
            
            # Implementation for project_root
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing grafana_dir")
            
            # Implementation for grafana_dir
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing dashboard_files")
            
            # Implementation for dashboard_files
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"dashboard_files completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"dashboard_files failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"grafana_dir completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"grafana_dir failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"project_root completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"project_root failed: {e}")
            raise
    @pytest.fixture
    def grafana_dir(self, project_root):
        return project_root / "monitoring" / "grafana"
    
    @pytest.fixture
    def dashboard_files(self, grafana_dir):
        return list(grafana_dir.glob("*.json"))
    
    def test_grafana_directory_exists(self, grafana_dir):
        """Test that Grafana directory exists"""
        assert grafana_dir.exists(), f"Grafana directory not found: {grafana_dir}"
    
    def test_dashboard_files_exist(self, dashboard_files):
        """Test that dashboard JSON files exist"""
        assert len(dashboard_files) > 0, "No dashboard files found"
        assert len(dashboard_files) >= 7, f"Expected at least 7 dashboards, found {len(dashboard_files)}"
    
    def test_required_dashboards_exist(self, grafana_dir):
        """Test that all required dashboard types exist"""
        required_dashboards = [
            "business_metrics",
            "api_analytics", 
            "security_monitoring",
            "infrastructure_monitoring",
            "user_activity",
            "revenue_tracking",
            "platform_performance"
        ]
        
        existing_files = {f.stem for f in grafana_dir.glob("*.json")}
        
        for required in required_dashboards:
            matching_files = [f for f in existing_files if required in f.lower()]
            assert len(matching_files) > 0, f"Missing required dashboard type: {required}"
    
    def test_dashboard_json_validity(self, dashboard_files):
        """Test that all dashboard files are valid JSON"""
        for dashboard_file in dashboard_files:
            with open(dashboard_file) as f:
                try:
                    data = json.load(f)
                    assert isinstance(data, dict), f"Dashboard {dashboard_file.name} is not a valid JSON object"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {dashboard_file.name}: {str(e)}")
    
    def test_dashboard_structure(self, dashboard_files):
        """Test that dashboards have required structure"""
        for dashboard_file in dashboard_files:
            with open(dashboard_file) as f:
                data = json.load(f)
            
            # Check if it's a Grafana export format or embedded format
            if "dashboard" in data:
                dashboard_data = data["dashboard"]
            else:
                dashboard_data = data
            
            # Required fields
            assert "title" in dashboard_data, f"Dashboard {dashboard_file.name} missing title"
            assert "panels" in dashboard_data, f"Dashboard {dashboard_file.name} missing panels"
            
            # Check panels
            panels = dashboard_data["panels"]
            assert isinstance(panels, list), f"Dashboard {dashboard_file.name} panels should be a list"
    
    def test_dashboard_panels_content(self, dashboard_files):
        """Test that dashboards have meaningful panel content"""
        for dashboard_file in dashboard_files:
            with open(dashboard_file) as f:
                data = json.load(f)
            
            # Extract dashboard data
            if "dashboard" in data:
                dashboard_data = data["dashboard"]
            else:
                dashboard_data = data
            
            panels = dashboard_data.get("panels", [])
            
            # Should have at least some panels
            assert len(panels) > 0, f"Dashboard {dashboard_file.name} has no panels"
            
            # Test panel structure
            for i, panel in enumerate(panels):
                assert "title" in panel, f"Panel {i} in {dashboard_file.name} missing title"
                assert "type" in panel, f"Panel {i} in {dashboard_file.name} missing type"
    
    def test_prometheus_metrics_in_panels(self, dashboard_files):
        try:
            logger.info(f"Executing project_root")
            
            # Implementation for project_root
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing provisioning_dir")
            
            # Implementation for provisioning_dir
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"provisioning_dir completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"provisioning_dir failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"project_root completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"project_root failed: {e}")
            raise
        for dashboard_file in dashboard_files:
            with open(dashboard_file) as f:
                data = json.load(f)
            
            # Extract dashboard data
            if "dashboard" in data:
                dashboard_data = data["dashboard"]
            else:
                dashboard_data = data
            
            panels = dashboard_data.get("panels", [])
            
            for i, panel in enumerate(panels):
                targets = panel.get("targets", [])
                
                for j, target in enumerate(targets):
                    if "expr" in target:
        try:
            logger.info(f"Executing project_root")
            
            # Implementation for project_root
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing compose_file")
            
            # Implementation for compose_file
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"compose_file completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"compose_file failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"project_root completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"project_root failed: {e}")
            raise
                        assert isinstance(expr, str), f"Panel {i} target {j} in {dashboard_file.name}: expr should be string"
                        assert len(expr.strip()) > 0, f"Panel {i} target {j} in {dashboard_file.name}: expr is empty"
                        
                        # Check for proper metric naming convention
                        if "ia_influencer_" in expr:
                            # This is our custom metric, good!
                            pass
                        elif any(standard in expr for standard in ["rate(", "histogram_quantile", "sum(", "avg(", "up"]):
                            # Standard Prometheus functions/metrics, also good
                            pass
                        else:
                            print(f"Warning: Panel {i} target {j} in {dashboard_file.name} may have non-standard metric: {expr[:50]}...")

class TestGrafanaProvisioning:
    """Test suite for Grafana provisioning configuration"""
    
    @pytest.fixture
    def project_root(self):
        return Path("/home/runner/work/Ainflue/Ainflue")
    
    @pytest.fixture
    def provisioning_dir(self, project_root):
        return project_root / "monitoring" / "grafana" / "provisioning"
    
    def test_provisioning_directory_exists(self, provisioning_dir):
        """Test that provisioning directory exists"""
        assert provisioning_dir.exists(), f"Provisioning directory not found: {provisioning_dir}"
    
    def test_datasources_config_exists(self, provisioning_dir):
        """Test that datasources configuration exists"""
        datasources_dir = provisioning_dir / "datasources"
        assert datasources_dir.exists(), "Datasources provisioning directory missing"
        
        config_files = list(datasources_dir.glob("*.yml"))
        assert len(config_files) > 0, "No datasources configuration files found"
    
    def test_dashboards_config_exists(self, provisioning_dir):
        """Test that dashboards provisioning configuration exists"""
        dashboards_dir = provisioning_dir / "dashboards"
        assert dashboards_dir.exists(), "Dashboards provisioning directory missing"
        
        config_files = list(dashboards_dir.glob("*.yml"))
        assert len(config_files) > 0, "No dashboards configuration files found"
    
    def test_datasources_config_valid(self, provisioning_dir):
        """Test that datasources configuration is valid YAML"""
        datasources_dir = provisioning_dir / "datasources"
        
        for config_file in datasources_dir.glob("*.yml"):
            with open(config_file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert isinstance(data, dict), f"Datasources config {config_file.name} should be a YAML object"
                    assert "datasources" in data, f"Datasources config {config_file.name} missing datasources key"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in datasources config {config_file.name}: {str(e)}")

class TestDockerComposeMonitoring:
    """Test suite for Docker Compose monitoring configuration"""
    
    @pytest.fixture
    def project_root(self):
        return Path("/home/runner/work/Ainflue/Ainflue")
    
    @pytest.fixture
    def compose_file(self, project_root):
        return project_root / "docker-compose.monitoring.yml"
    
    def test_monitoring_compose_exists(self, compose_file):
        """Test that monitoring Docker Compose file exists"""
        assert compose_file.exists(), f"Monitoring compose file not found: {compose_file}"
    
    def test_monitoring_compose_valid(self, compose_file):
        """Test that monitoring Docker Compose file is valid YAML"""
        with open(compose_file) as f:
            try:
                data = yaml.safe_load(f)
                assert isinstance(data, dict), "Docker compose file should be a YAML object"
                assert "services" in data, "Docker compose file missing services"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in monitoring compose file: {str(e)}")
    
    def test_required_services_present(self, compose_file):
        """Test that required monitoring services are present"""
        with open(compose_file) as f:
            data = yaml.safe_load(f)
        
        services = data.get("services", {})
        required_services = ["grafana", "prometheus"]
        
        for service in required_services:
            assert service in services, f"Required service '{service}' not found in monitoring compose"
    
    def test_grafana_volumes_configured(self, compose_file):
        """Test that Grafana volumes are properly configured"""
        with open(compose_file) as f:
            data = yaml.safe_load(f)
        
        grafana_service = data.get("services", {}).get("grafana", {})
        volumes = grafana_service.get("volumes", [])
        
        # Check for provisioning volume mount
        provisioning_mounted = any("provisioning" in vol for vol in volumes)
        assert provisioning_mounted, "Grafana provisioning volume not mounted"
        
        # Check for dashboards volume mount  
        dashboards_mounted = any("dashboards" in vol for vol in volumes)
        assert dashboards_mounted, "Grafana dashboards volume not mounted"

if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])