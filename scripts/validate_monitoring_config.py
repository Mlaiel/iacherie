#!/usr/bin/env python3
"""Monitoring Configuration Validation Script
==========================================

Validates Grafana and Prometheus configurations for Ainflue Platform.
Addresses the requirement: "Monitoring Grafana/Prometheus - vérifier configuration"

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import yaml
import json
import os
import sys
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringConfigValidator:
    """Validates Prometheus and Grafana monitoring configurations"""    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.prometheus_config_path = self.project_root / "monitoring" / "prometheus" / "prometheus.yml"
        self.grafana_config_path = self.project_root / "monitoring" / "grafana"
        self.validation_results = {}
        
    def validate_prometheus_config(self) -> Tuple[bool, List[str]]:
        """Validate Prometheus configuration file"""        issues = []
        
        try:
            if not self.prometheus_config_path.exists():
                issues.append(f"Prometheus config file not found: {self.prometheus_config_path}")
                return False, issues
            
            # Load and parse YAML
            with open(self.prometheus_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info("✅ Prometheus YAML syntax is valid")
            
            # Validate required sections
            required_sections = ['global', 'scrape_configs']
            for section in required_sections:
                if section not in config:
                    issues.append(f"Missing required section: {section}")
            
            # Validate global configuration
            if 'global' in config:
                global_config = config['global']
                if 'scrape_interval' not in global_config:
                    issues.append("Missing scrape_interval in global config")
                if 'evaluation_interval' not in global_config:
                    issues.append("Missing evaluation_interval in global config")
                    
                logger.info(f"✅ Global config: scrape_interval={global_config.get('scrape_interval', 'N/A')}")
            
            # Validate scrape configs
            if 'scrape_configs' in config:
                scrape_configs = config['scrape_configs']
                if not isinstance(scrape_configs, list) or len(scrape_configs) == 0:
                    issues.append("scrape_configs must be a non-empty list")
                else:
                    for i, job in enumerate(scrape_configs):
                        if 'job_name' not in job:
                            issues.append(f"Job {i} missing job_name")
                        else:
                            logger.info(f"✅ Found scrape job: {job['job_name']}")
            
            # Check for alert rules
            alert_rules_path = self.prometheus_config_path.parent / "alert_rules.yml"
            if alert_rules_path.exists():
                logger.info("✅ Alert rules file found")
                # Validate alert rules syntax
                try:
                    with open(alert_rules_path, 'r') as f:
                        alert_rules = yaml.safe_load(f)
                        if 'groups' in alert_rules:
                            logger.info(f"✅ Found {len(alert_rules['groups'])} alert groups")
                        else:
                            issues.append("Alert rules missing 'groups' section")
                except Exception as e:
                    issues.append(f"Alert rules syntax error: {str(e)}")
            else:
                issues.append("Alert rules file not found (optional)")
            
            # Check for recording rules
            recording_rules_path = self.prometheus_config_path.parent / "recording_rules.yml"
            if recording_rules_path.exists():
                logger.info("✅ Recording rules file found")
            else:
                logger.info("ℹ️ Recording rules file not found (optional)")
            
            return len(issues) == 0, issues
            
        except yaml.YAMLError as e:
            issues.append(f"YAML syntax error: {str(e)}")
            return False, issues
        except Exception as e:
            issues.append(f"Error validating Prometheus config: {str(e)}")
            return False, issues
    
    def validate_grafana_config(self) -> Tuple[bool, List[str]]:
        """Validate Grafana configuration"""        issues = []
        
        try:
            # Check datasources configuration
            datasources_path = self.grafana_config_path / "provisioning" / "datasources"
            if not datasources_path.exists():
                issues.append(f"Grafana datasources directory not found: {datasources_path}")
            else:
                logger.info("✅ Grafana datasources directory found")
                
                # Check for Prometheus datasource
                prometheus_ds_path = datasources_path / "prometheus.yml"
                if prometheus_ds_path.exists():
                    with open(prometheus_ds_path, 'r') as f:
                        datasources_config = yaml.safe_load(f)
                        
                    if 'datasources' in datasources_config:
                        prometheus_found = False
                        for ds in datasources_config['datasources']:
                            if ds.get('type') == 'prometheus':
                                prometheus_found = True
                                logger.info(f"✅ Prometheus datasource found: {ds.get('name', 'Unknown')}")
                                # Validate URL
                                if not ds.get('url'):
                                    issues.append("Prometheus datasource missing URL")
                                break
                        
                        if not prometheus_found:
                            issues.append("No Prometheus datasource configured")
                    else:
                        issues.append("Datasources config missing 'datasources' section")
                else:
                    issues.append("Prometheus datasource config not found")
            
            # Check dashboards configuration
            dashboards_path = self.grafana_config_path / "provisioning" / "dashboards"
            if dashboards_path.exists():
                logger.info("✅ Grafana dashboards provisioning directory found")
            else:
                logger.info("ℹ️ Grafana dashboards provisioning directory not found")
            
            # Check for dashboard files
            dashboard_files = list(self.grafana_config_path.glob("*.json"))
            if dashboard_files:
                logger.info(f"✅ Found {len(dashboard_files)} dashboard files")
                
                # Validate dashboard JSON files
                for dashboard_file in dashboard_files:
                    try:
                        with open(dashboard_file, 'r') as f:
                            dashboard = json.load(f)
                        
                        # Basic dashboard validation
                        if 'dashboard' in dashboard:
                            dashboard_data = dashboard['dashboard']
                        else:
                            dashboard_data = dashboard
                            
                        if 'title' not in dashboard_data:
                            issues.append(f"Dashboard {dashboard_file.name} missing title")
                        else:
                            logger.info(f"✅ Dashboard: {dashboard_data['title']}")
                            
                        if 'panels' not in dashboard_data:
                            issues.append(f"Dashboard {dashboard_file.name} missing panels")
                        else:
                            logger.info(f"   - {len(dashboard_data['panels'])} panels found")
                            
                    except json.JSONDecodeError as e:
                        issues.append(f"Dashboard {dashboard_file.name} JSON syntax error: {str(e)}")
                    except Exception as e:
                        issues.append(f"Error validating dashboard {dashboard_file.name}: {str(e)}")
            else:
                logger.info("ℹ️ No dashboard files found")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error validating Grafana config: {str(e)}")
            return False, issues
    
    def validate_monitoring_endpoints(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate monitoring endpoints connectivity (if services are running)"""        endpoints = {
            'prometheus': 'http://localhost:9090',
            'grafana': 'http://localhost:3000',
            'alertmanager': 'http://localhost:9093'
        }
        
        results = {}
        all_healthy = True
        
        for service, url in endpoints.items():
            try:
                # Try to connect with a short timeout
                response = requests.get(f"{url}/api/v1/status/config" if service == 'prometheus' 
                                      else f"{url}/api/health" if service == 'grafana'
                                      else f"{url}/-/healthy", 
                                      timeout=5)
                
                if response.status_code == 200:
                    results[service] = {
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds(),
                        'url': url
                    }
                    logger.info(f"✅ {service} is healthy at {url}")
                else:
                    results[service] = {
                        'status': 'unhealthy',
                        'status_code': response.status_code,
                        'url': url
                    }
                    logger.warning(f"⚠️ {service} returned status {response.status_code}")
                    all_healthy = False
                    
            except requests.exceptions.ConnectionError:
                results[service] = {
                    'status': 'not_running',
                    'error': 'Connection refused',
                    'url': url
                }
                logger.info(f"ℹ️ {service} not running at {url} (this is OK for config validation)")
                
            except requests.exceptions.Timeout:
                results[service] = {
                    'status': 'timeout',
                    'error': 'Request timeout',
                    'url': url
                }
                logger.warning(f"⚠️ {service} timeout at {url}")
                all_healthy = False
                
            except Exception as e:
                results[service] = {
                    'status': 'error',
                    'error': str(e),
                    'url': url
                }
                logger.error(f"❌ Error checking {service}: {str(e)}")
                all_healthy = False
        
        return all_healthy, results
    
    def check_monitoring_dependencies(self) -> Tuple[bool, List[str]]:
        """Check if monitoring configuration dependencies are satisfied"""        issues = []
        
        # Check if Docker Compose monitoring file exists
        monitoring_compose = self.project_root / "docker-compose.monitoring.yml"
        if not monitoring_compose.exists():
            issues.append("Monitoring Docker Compose file not found")
        else:
            logger.info("✅ Monitoring Docker Compose file found")
        
        # Check if monitoring directory structure exists
        required_dirs = [
            "monitoring",
            "monitoring/prometheus",
            "monitoring/grafana",
            "monitoring/grafana/provisioning",
            "monitoring/grafana/provisioning/datasources"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                issues.append(f"Required directory missing: {dir_path}")
            else:
                logger.info(f"✅ Directory found: {dir_path}")
        
        return len(issues) == 0, issues
    
    def generate_monitoring_test_config(self) -> None:
        """Generate basic monitoring configurations if missing"""        
        # Create basic Prometheus config if missing
        if not self.prometheus_config_path.exists():
            prometheus_config = {
                'global': {
                    'scrape_interval': '15s',
                    'evaluation_interval': '15s'
                },
                'rule_files': [
                    'alert_rules.yml'
                ],
                'scrape_configs': [
                    {
                        'job_name': 'prometheus',
                        'static_configs': [
                            {'targets': ['localhost:9090']}
                        ]
                    },
                    {
                        'job_name': 'ainflue-app',
                        'static_configs': [
                            {'targets': ['ainflue-app:8000']}
                        ],
                        'metrics_path': '/metrics'
                    }
                ]
            }
            
            self.prometheus_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prometheus_config_path, 'w') as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)
            
            logger.info(f"✅ Generated basic Prometheus config: {self.prometheus_config_path}")
        
        # Create basic Grafana datasource config if missing
        grafana_ds_path = self.grafana_config_path / "provisioning" / "datasources" / "prometheus.yml"
        if not grafana_ds_path.exists():
            datasource_config = {
                'apiVersion': 1,
                'datasources': [
                    {
                        'name': 'Prometheus',
                        'type': 'prometheus',
                        'access': 'proxy',
                        'url': 'http://prometheus:9090',
                        'isDefault': True,
                        'editable': False
                    }
                ]
            }
            
            grafana_ds_path.parent.mkdir(parents=True, exist_ok=True)
            with open(grafana_ds_path, 'w') as f:
                yaml.dump(datasource_config, f, default_flow_style=False)
            
            logger.info(f"✅ Generated basic Grafana datasource config: {grafana_ds_path}")
        
        # Create basic alert rules if missing
        alert_rules_path = self.prometheus_config_path.parent / "alert_rules.yml"
        if not alert_rules_path.exists():
            alert_rules = {
                'groups': [
                    {
                        'name': 'ainflue_alerts',
                        'rules': [
                            {
                                'alert': 'HighCpuUsage',
                                'expr': 'cpu_usage_percent > 80',
                                'for': '5m',
                                'labels': {
                                    'severity': 'warning'
                                },
                                'annotations': {
                                    'summary': 'High CPU usage detected',
                                    'description': 'CPU usage is above 80% for more than 5 minutes'
                                }
                            }
                        ]
                    }
                ]
            }
            
            with open(alert_rules_path, 'w') as f:
                yaml.dump(alert_rules, f, default_flow_style=False)
            
            logger.info(f"✅ Generated basic alert rules: {alert_rules_path}")
    
    def generate_monitoring_startup_script(self) -> str:
        """Generate a script to start monitoring services"""        script_content = """#!/bin/bash
# Monitoring Services Startup Script
set -e

echo "🚀 Starting Ainflue Monitoring Stack..."

# Clean up any existing containers
docker compose -f docker-compose.monitoring.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling monitoring images..."
docker compose -f docker-compose.monitoring.yml pull --ignore-pull-failures

# Start monitoring services
echo "🔧 Starting monitoring services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 60

# Check Prometheus
echo "🩺 Checking Prometheus..."
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
echo "🩺 Checking Grafana..."
if curl -f -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana is not responding"
fi

echo "📊 Monitoring services status:"
docker compose -f docker-compose.monitoring.yml ps

echo "🎉 Monitoring stack startup completed!"
echo "📊 Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin/admin123)"
echo "   AlertManager: http://localhost:9093"
"""        return script_content
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete monitoring configuration validation"""        logger.info("📊 Starting Monitoring Configuration Validation")
        
        # Check dependencies
        deps_valid, dep_issues = self.check_monitoring_dependencies()
        
        # Generate missing configs if needed
        if not deps_valid:
            logger.info("🔧 Generating missing monitoring configurations...")
            self.generate_monitoring_test_config()
        
        # Validate Prometheus
        logger.info("\n" + "="*60)
        logger.info("Validating Prometheus Configuration")
        logger.info("="*60)
        
        prometheus_valid, prometheus_issues = self.validate_prometheus_config()
        
        # Validate Grafana
        logger.info("\n" + "="*60)
        logger.info("Validating Grafana Configuration")
        logger.info("="*60)
        
        grafana_valid, grafana_issues = self.validate_grafana_config()
        
        # Check endpoint connectivity
        logger.info("\n" + "="*60)
        logger.info("Checking Monitoring Endpoints")
        logger.info("="*60)
        
        endpoints_healthy, endpoint_results = self.validate_monitoring_endpoints()
        
        # Generate startup script
        script_content = self.generate_monitoring_startup_script()
        script_path = self.project_root / "start_monitoring_stack.sh"
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        logger.info(f"✅ Generated monitoring startup script: {script_path}")
        
        # Compile results
        self.validation_results = {
            'dependencies': {
                'valid': deps_valid,
                'issues': dep_issues
            },
            'prometheus': {
                'valid': prometheus_valid,
                'issues': prometheus_issues,
                'config_path': str(self.prometheus_config_path)
            },
            'grafana': {
                'valid': grafana_valid,
                'issues': grafana_issues,
                'config_path': str(self.grafana_config_path)
            },
            'endpoints': {
                'healthy': endpoints_healthy,
                'results': endpoint_results
            },
            'startup_script': str(script_path)
        }
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """Generate monitoring validation report"""        if not self.validation_results:
            return "No validation results available. Run validation first."
        
        report = """Monitoring Configuration Validation Report
==========================================

"""        
        # Dependencies
        deps = self.validation_results['dependencies']
        report += f"📦 Dependencies: {'✅ VALID' if deps['valid'] else '❌ ISSUES'}\n"
        if deps['issues']:
            for issue in deps['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Prometheus
        prom = self.validation_results['prometheus']
        report += f"🔍 Prometheus: {'✅ VALID' if prom['valid'] else '❌ ISSUES'}\n"
        report += f"   Config: {prom['config_path']}\n"
        if prom['issues']:
            for issue in prom['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Grafana
        graf = self.validation_results['grafana']
        report += f"📊 Grafana: {'✅ VALID' if graf['valid'] else '❌ ISSUES'}\n"
        report += f"   Config: {graf['config_path']}\n"
        if graf['issues']:
            for issue in graf['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Endpoints
        endpoints = self.validation_results['endpoints']
        report += f"🌐 Endpoints: {'✅ HEALTHY' if endpoints['healthy'] else '⚠️ NOT RUNNING'}\n"
        for service, result in endpoints['results'].items():
            status_icon = {
                'healthy': '✅',
                'unhealthy': '❌',
                'not_running': 'ℹ️',
                'timeout': '⚠️',
                'error': '❌'
            }.get(result['status'], '❓')
            report += f"   {status_icon} {service}: {result['status']} ({result['url']})\n"
        report += "\n"
        
        # Startup script
        report += f"🚀 Startup Script: {self.validation_results['startup_script']}\n\n"
        
        # Summary
        all_configs_valid = (deps['valid'] and prom['valid'] and graf['valid'])
        report += "SUMMARY\n"
        report += "="*40 + "\n"
        report += f"Configuration Status: {'✅ VALID' if all_configs_valid else '⚠️ NEEDS ATTENTION'}\n"
        report += f"Services Running: {'✅ YES' if endpoints['healthy'] else 'ℹ️ NO (use startup script)'}\n"
        
        if all_configs_valid:
            report += "\n🎉 Monitoring configurations are valid and ready to use!\n"
            report += "\nTo start monitoring services:\n"
            report += f"   bash {self.validation_results['startup_script']}\n"
        else:
            report += "\n⚠️ Some configurations need attention. Check issues above.\n"
        
        return report


def main():
    """Main execution function"""    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    logger.info("📊 Monitoring Configuration Validation")
    logger.info(f"Project Root: {project_root}")
    
    validator = MonitoringConfigValidator(str(project_root))
    results = validator.run_validation()
    
    # Generate and save report
    report = validator.generate_report()
    report_path = project_root / "monitoring_validation_report.txt"
    report_path.write_text(report)
    
    print(report)
    logger.info(f"📄 Report saved to: {report_path}")
    
    # Return appropriate exit code
    all_valid = (
        results['dependencies']['valid'] and
        results['prometheus']['valid'] and
        results['grafana']['valid']
    )
    
    if all_valid:
        logger.info("🎉 All monitoring configurations are valid!")
        return 0
    else:
        logger.warning("⚠️ Some monitoring configurations need attention!")
        return 1


if __name__ == "__main__":
    sys.exit(main())