#!/usr/bin/env python3
"""Grafana Setup Validation and Dashboard Deployment Script

This script validates that the Grafana setup is complete and properly configured
for the Ainflue platform dashboards and visualization requirements.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import requests
from dataclasses import dataclass

@dataclass
class DashboardInfo:
    name: str
    file_path: str
    title: str
    panels_count: int
    tags: List[str]

class GrafanaSetupValidator:
    """
Validates and manages Grafana setup for Ainflue platform"""
    
    def __init__(self, project_root: str = "/home/runner/work/Ainflue/Ainflue"):
        self.project_root = Path(project_root)
        self.grafana_dir = self.project_root / "monitoring" / "grafana"
        self.provisioning_dir = self.grafana_dir / "provisioning"
        
    def validate_setup(self) -> Dict[str, Any]:
        """Validate the complete Grafana setup"""
        results = {
            "overall_status": "PASS",
            "checks": {},
            "dashboards": {},
            "recommendations": []
        }
        
        # Check 1: Docker compose monitoring configuration
        results["checks"]["docker_compose"] = self._check_docker_compose()
        
        # Check 2: Dashboard files
        results["checks"]["dashboard_files"] = self._check_dashboard_files()
        
        # Check 3: Provisioning configuration
        results["checks"]["provisioning"] = self._check_provisioning_config()
        
        # Check 4: Dashboard content validation
        results["dashboards"] = self._validate_dashboards()
        
        # Check 5: Requirements mapping
        results["checks"]["requirements_mapping"] = self._check_requirements_mapping()
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        # Determine overall status
        failed_checks = [k for k, v in results["checks"].items() if not v.get("status", False)]
        if failed_checks:
            results["overall_status"] = "FAIL"
            results["failed_checks"] = failed_checks
        
        return results
    
    def _check_docker_compose(self) -> Dict[str, Any]:
        """Check Docker Compose monitoring configuration"""
        compose_file = self.project_root / "docker-compose.monitoring.yml"
        
        if not compose_file.exists():
            return {
                "status": False,
                "message": "docker-compose.monitoring.yml not found",
                "details": "Missing monitoring stack configuration"
            }
        
        try:
            with open(compose_file) as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get("services", {})
            required_services = ["grafana", "prometheus"]
            missing_services = [svc for svc in required_services if svc not in services]
            
            grafana_config = services.get("grafana", {})
            volumes = grafana_config.get("volumes", [])
            
            provisioning_mounted = any("provisioning" in vol for vol in volumes)
            dashboards_mounted = any("dashboards" in vol for vol in volumes)
            
            return {
                "status": len(missing_services) == 0,
                "message": "Docker compose monitoring configuration validated",
                "details": {
                    "missing_services": missing_services,
                    "provisioning_mounted": provisioning_mounted,
                    "dashboards_mounted": dashboards_mounted,
                    "total_services": len(services)
                }
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Error reading docker-compose.monitoring.yml: {str(e)}",
                "details": str(e)
            }
    
    def _check_dashboard_files(self) -> Dict[str, Any]:
        """Check dashboard JSON files"""
        if not self.grafana_dir.exists():
            return {
                "status": False,
                "message": "Grafana directory not found",
                "details": f"Missing: {self.grafana_dir}"
            }
        
        dashboard_files = list(self.grafana_dir.glob("*.json"))
        
        return {
            "status": len(dashboard_files) > 0,
            "message": f"Found {len(dashboard_files)} dashboard files",
            "details": {
                "dashboard_count": len(dashboard_files),
                "dashboard_files": [f.name for f in dashboard_files]
            }
        }
    
    def _check_provisioning_config(self) -> Dict[str, Any]:
        """Check Grafana provisioning configuration"""
        if not self.provisioning_dir.exists():
            return {
                "status": False,
                "message": "Provisioning directory not found",
                "details": f"Missing: {self.provisioning_dir}"
            }
        
        datasources_dir = self.provisioning_dir / "datasources"
        dashboards_dir = self.provisioning_dir / "dashboards"
        
        datasource_files = list(datasources_dir.glob("*.yml")) if datasources_dir.exists() else []
        dashboard_configs = list(dashboards_dir.glob("*.yml")) if dashboards_dir.exists() else []
        
        return {
            "status": len(datasource_files) > 0 and len(dashboard_configs) > 0,
            "message": "Provisioning configuration validated",
            "details": {
                "datasource_configs": len(datasource_files),
                "dashboard_configs": len(dashboard_configs),
                "datasources_dir_exists": datasources_dir.exists(),
                "dashboards_dir_exists": dashboards_dir.exists()
            }
        }
    
    def _validate_dashboards(self) -> Dict[str, DashboardInfo]:
        """Validate individual dashboard files"""
        dashboards = {}
        
        for dashboard_file in self.grafana_dir.glob("*.json"):
            try:
                with open(dashboard_file) as f:
                    data = json.load(f)
                
                # Extract dashboard info from either format
                if "dashboard" in data:
                    dashboard_data = data["dashboard"]
                else:
                    dashboard_data = data
                
                title = dashboard_data.get("title", "Unknown")
                panels = dashboard_data.get("panels", [])
                tags = dashboard_data.get("tags", [])
                
                dashboards[dashboard_file.stem] = DashboardInfo(
                    name=dashboard_file.stem,
                    file_path=str(dashboard_file),
                    title=title,
                    panels_count=len(panels),
                    tags=tags
                )
                
            except Exception as e:
                dashboards[dashboard_file.stem] = DashboardInfo(
                    name=dashboard_file.stem,
                    file_path=str(dashboard_file),
                    title=f"ERROR: {str(e)}",
                    panels_count=0,
                    tags=[]
                )
        
        return dashboards
    
    def _check_requirements_mapping(self) -> Dict[str, Any]:
        """Check if all required dashboards are covered"""
        required_dashboards = {
            "Business overview dashboard": ["business_metrics", "business"],
            "Technical performance dashboard": ["platform_performance", "system_health", "performance"],
            "Security monitoring dashboard": ["security_monitoring", "security"],
            "Infrastructure dashboard": ["infrastructure_monitoring", "infrastructure"],
            "API analytics dashboard": ["api_analytics", "api"],
            "User activity dashboard": ["user_activity", "user"],
            "Revenue analytics dashboard": ["revenue_tracking", "revenue"]
        }
        
        dashboard_files = {f.stem for f in self.grafana_dir.glob("*.json")}
        
        coverage = {}
        for req_name, keywords in required_dashboards.items():
            matching_files = []
            for keyword in keywords:
                matches = [f for f in dashboard_files if keyword in f.lower()]
                matching_files.extend(matches)
            
            coverage[req_name] = {
                "covered": len(matching_files) > 0,
                "matching_files": list(set(matching_files))
            }
        
        total_required = len(required_dashboards)
        covered_count = sum(1 for v in coverage.values() if v["covered"])
        
        return {
            "status": covered_count == total_required,
            "message": f"Requirements coverage: {covered_count}/{total_required}",
            "details": {
                "coverage_percentage": (covered_count / total_required) * 100,
                "covered_requirements": covered_count,
                "total_requirements": total_required,
                "coverage": coverage
            }
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check for missing provisioning
        if not results["checks"]["provisioning"]["status"]:
            recommendations.append(
                "Set up Grafana provisioning configuration for automatic dashboard loading"
            )
        
        # Check dashboard count
        dashboard_count = len(results["dashboards"])
        if dashboard_count < 5:
            recommendations.append(
                f"Consider adding more dashboards (currently {dashboard_count})"
            )
        
        # Check for empty dashboards
        empty_dashboards = [name for name, info in results["dashboards"].items() 
                          if info.panels_count == 0]
        if empty_dashboards:
            recommendations.append(
                f"Add panels to empty dashboards: {', '.join(empty_dashboards)}"
            )
        
        # Check requirements coverage
        req_check = results["checks"]["requirements_mapping"]
        if not req_check["status"]:
            uncovered = [req for req, info in req_check["details"]["coverage"].items() 
                        if not info["covered"]]
            recommendations.append(
                f"Create dashboards for missing requirements: {', '.join(uncovered)}"
            )
        
        return recommendations
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print validation results in a readable format"""
        print("=" * 60)
        print("GRAFANA SETUP VALIDATION REPORT")
        print("=" * 60)
        print(f"Overall Status: {results['overall_status']}")
        print()
        
        print("CHECK RESULTS:")
        print("-" * 30)
        for check_name, check_result in results["checks"].items():
            status_icon = "✅" if check_result["status"] else "❌"
            print(f"{status_icon} {check_name.replace('_', ' ').title()}: {check_result['message']}")
        print()
        
        print("DASHBOARDS:")
        print("-" * 30)
        for name, info in results["dashboards"].items():
            print(f"📊 {info.title} ({info.panels_count} panels)")
            print(f"   File: {Path(info.file_path).name}")
            if info.tags:
                print(f"   Tags: {', '.join(info.tags)}")
            print()
        
        if results["recommendations"]:
            print("RECOMMENDATIONS:")
            print("-" * 30)
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"{i}. {rec}")
            print()
        
        print("=" * 60)

def main():
    """Main validation function"""
    validator = GrafanaSetupValidator()
    results = validator.validate_setup()
    validator.print_results(results)
    
    # Exit with error code if validation failed
    if results["overall_status"] == "FAIL":
        sys.exit(1)
    else:
        print("✅ Grafana setup validation completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()