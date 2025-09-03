#!/usr/bin/env python3
"""
Monitoring Stack Validation Script
=====================================

Comprehensive validation script for Ainflue monitoring and logging infrastructure.
Validates all components: ELK Stack, APM, Custom Metrics, Alerts, and Dashboards.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Represents the result of a validation check"""
    component: str
    check_name: str
    status: bool
    message: str
    details: Optional[Dict[str, Any]] = None

class MonitoringValidator:
    """Comprehensive monitoring stack validator"""
    
    def __init__(self, base_path: str = "/home/runner/work/Ainflue/Ainflue"):
        self.base_path = Path(base_path)
        self.results: List[ValidationResult] = []
        
    def add_result(self, component: str, check_name: str, status: bool, 
                   message: str, details: Optional[Dict[str, Any]] = None):
        """Add a validation result"""
        self.results.append(ValidationResult(
            component=component,
            check_name=check_name,
            status=status,
            message=message,
            details=details
        ))
        
    def validate_elk_stack(self) -> bool:
        """Validate ELK Stack implementation"""
        logger.info("🔍 Validating ELK Stack configuration...")
        
        # Check ELK Stack YAML file
        elk_file = self.base_path / "kubernetes/monitoring/elk_stack.yaml"
        if elk_file.exists():
            try:
                with open(elk_file) as f:
                    elk_config = yaml.safe_load_all(f)
                    components = list(elk_config)
                    
                # Check for Elasticsearch, Logstash, Kibana components
                component_types = [comp.get('kind', '') for comp in components if comp]
                required_components = ['Deployment', 'Service', 'ConfigMap']
                
                has_elasticsearch = any('elasticsearch' in str(comp).lower() for comp in components)
                has_logstash = any('logstash' in str(comp).lower() for comp in components)
                has_kibana = any('kibana' in str(comp).lower() for comp in components)
                
                self.add_result(
                    "ELK Stack", "Configuration File", True,
                    f"ELK Stack configuration found with {len(components)} components",
                    {"components": len(components), "file": str(elk_file)}
                )
                
                self.add_result(
                    "ELK Stack", "Elasticsearch", has_elasticsearch,
                    "Elasticsearch configuration found" if has_elasticsearch else "Elasticsearch configuration missing"
                )
                
                self.add_result(
                    "ELK Stack", "Logstash", has_logstash,
                    "Logstash configuration found" if has_logstash else "Logstash configuration missing"
                )
                
                self.add_result(
                    "ELK Stack", "Kibana", has_kibana,
                    "Kibana configuration found" if has_kibana else "Kibana configuration missing"
                )
                
                return has_elasticsearch and has_logstash and has_kibana
                
            except Exception as e:
                self.add_result("ELK Stack", "Configuration Parse", False, f"Failed to parse ELK config: {e}")
                return False
        else:
            self.add_result("ELK Stack", "Configuration File", False, "ELK Stack configuration file not found")
            return False
            
    def validate_apm_integration(self) -> bool:
        """Validate APM integration (Jaeger + New Relic)"""
        logger.info("📊 Validating APM integration...")
        
        # Check Jaeger configuration
        jaeger_file = self.base_path / "monitoring/jaeger-config.yaml"
        jaeger_exists = jaeger_file.exists()
        
        self.add_result(
            "APM", "Jaeger Configuration", jaeger_exists,
            "Jaeger configuration found" if jaeger_exists else "Jaeger configuration missing",
            {"file": str(jaeger_file)} if jaeger_exists else None
        )
        
        # Check New Relic configuration
        newrelic_config = self.base_path / "config/apis/analytics_apis.py"
        newrelic_configured = False
        
        if newrelic_config.exists():
            try:
                with open(newrelic_config) as f:
                    content = f.read()
                    newrelic_configured = "NEW_RELIC_CONFIG" in content and "new_relic" in content
                    
                self.add_result(
                    "APM", "New Relic Configuration", newrelic_configured,
                    "New Relic configuration found" if newrelic_configured else "New Relic configuration incomplete"
                )
            except Exception as e:
                self.add_result("APM", "New Relic Configuration", False, f"Failed to check New Relic config: {e}")
        
        # Check tracing configuration
        tracing_config = self.base_path / "config/monitoring/tracing_config.py"
        tracing_exists = tracing_config.exists()
        
        self.add_result(
            "APM", "Distributed Tracing", tracing_exists,
            "Distributed tracing configuration found" if tracing_exists else "Distributed tracing configuration missing"
        )
        
        return jaeger_exists and newrelic_configured and tracing_exists
    
    def validate_custom_metrics(self) -> bool:
        """Validate custom metrics implementation"""
        logger.info("📈 Validating custom metrics system...")
        
        # Check metrics aggregator
        metrics_aggregator = self.base_path / "data_management/analytics/metrics_aggregator.py"
        aggregator_exists = metrics_aggregator.exists()
        
        self.add_result(
            "Custom Metrics", "Metrics Aggregator", aggregator_exists,
            "Advanced metrics aggregator found" if aggregator_exists else "Metrics aggregator missing"
        )
        
        # Check business KPIs configuration
        business_kpis = self.base_path / "config/monitoring/business_kpis_config.py"
        kpis_exists = business_kpis.exists()
        
        self.add_result(
            "Custom Metrics", "Business KPIs", kpis_exists,
            "Business KPIs configuration found" if kpis_exists else "Business KPIs configuration missing"
        )
        
        # Check advanced metrics module
        advanced_metrics_dir = self.base_path / "monitoring/advanced_metrics"
        advanced_exists = advanced_metrics_dir.exists()
        
        if advanced_exists:
            metrics_files = list(advanced_metrics_dir.glob("*.py"))
            self.add_result(
                "Custom Metrics", "Advanced Metrics", True,
                f"Advanced metrics module found with {len(metrics_files)} files"
            )
        else:
            self.add_result(
                "Custom Metrics", "Advanced Metrics", False,
                "Advanced metrics module missing"
            )
        
        return aggregator_exists and kpis_exists and advanced_exists
    
    def validate_alert_system(self) -> bool:
        """Validate alerting system"""
        logger.info("🚨 Validating alert system...")
        
        # Check AlertManager configuration
        alertmanager_config = self.base_path / "monitoring/alertmanager/alertmanager.yml"
        alertmanager_exists = alertmanager_config.exists()
        
        self.add_result(
            "Alert System", "AlertManager Config", alertmanager_exists,
            "AlertManager configuration found" if alertmanager_exists else "AlertManager configuration missing"
        )
        
        # Check alert rules
        alert_rules = self.base_path / "monitoring/alerting-rules.yaml"
        rules_exist = alert_rules.exists()
        
        self.add_result(
            "Alert System", "Alert Rules", rules_exist,
            "Alert rules configuration found" if rules_exist else "Alert rules configuration missing"
        )
        
        # Check notification configurations
        notification_config = self.base_path / "crawlers/configs/notification_configs.py"
        notifications_exist = notification_config.exists()
        
        self.add_result(
            "Alert System", "Notification Config", notifications_exist,
            "Notification configuration found" if notifications_exist else "Notification configuration missing"
        )
        
        # Check alerts module
        alerts_dir = self.base_path / "monitoring/alerts"
        alerts_module_exists = alerts_dir.exists()
        
        if alerts_module_exists:
            alert_files = list(alerts_dir.glob("*.py"))
            self.add_result(
                "Alert System", "Alert Scripts", True,
                f"Alert module found with {len(alert_files)} alert scripts"
            )
        else:
            self.add_result(
                "Alert System", "Alert Scripts", False,
                "Alert module missing"
            )
        
        return alertmanager_exists and rules_exist and notifications_exist and alerts_module_exists
    
    def validate_performance_dashboards(self) -> bool:
        """Validate performance dashboards"""
        logger.info("📊 Validating performance dashboards...")
        
        # Check Grafana dashboards
        grafana_dir = self.base_path / "monitoring/grafana"
        grafana_exists = grafana_dir.exists()
        
        if grafana_exists:
            dashboard_files = list(grafana_dir.glob("*.json"))
            self.add_result(
                "Performance Dashboards", "Grafana Dashboards", True,
                f"Found {len(dashboard_files)} Grafana dashboard files"
            )
        else:
            self.add_result(
                "Performance Dashboards", "Grafana Dashboards", False,
                "Grafana dashboards directory missing"
            )
        
        # Check performance configuration
        perf_config = self.base_path / "config/monitoring/performance_config.py"
        perf_exists = perf_config.exists()
        
        self.add_result(
            "Performance Dashboards", "Performance Config", perf_exists,
            "Performance monitoring configuration found" if perf_exists else "Performance configuration missing"
        )
        
        # Check production dashboard
        prod_dashboard = self.base_path / "monitoring/production_dashboard.py"
        prod_exists = prod_dashboard.exists()
        
        self.add_result(
            "Performance Dashboards", "Production Dashboard", prod_exists,
            "Production dashboard found" if prod_exists else "Production dashboard missing"
        )
        
        # Check dashboard configurations in Kubernetes
        k8s_dashboards = self.base_path / "kubernetes/monitoring/grafana-dashboards.yaml"
        k8s_dash_exists = k8s_dashboards.exists()
        
        self.add_result(
            "Performance Dashboards", "K8s Dashboard Config", k8s_dash_exists,
            "Kubernetes dashboard configuration found" if k8s_dash_exists else "K8s dashboard config missing"
        )
        
        return grafana_exists and perf_exists and prod_exists and k8s_dash_exists
    
    def validate_documentation(self) -> bool:
        """Validate monitoring documentation"""
        logger.info("📚 Validating monitoring documentation...")
        
        # Check main monitoring documentation
        main_doc = self.base_path / "docs/monitoring-implementation-summary.md"
        doc_exists = main_doc.exists()
        
        self.add_result(
            "Documentation", "Implementation Summary", doc_exists,
            "Monitoring implementation summary found" if doc_exists else "Implementation summary missing"
        )
        
        # Check monitoring README
        monitoring_readme = self.base_path / "config/monitoring/README.md"
        readme_exists = monitoring_readme.exists()
        
        self.add_result(
            "Documentation", "Monitoring README", readme_exists,
            "Monitoring README found" if readme_exists else "Monitoring README missing"
        )
        
        return doc_exists and readme_exists
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("🚀 Starting comprehensive monitoring stack validation...")
        
        # Run all validation checks
        elk_valid = self.validate_elk_stack()
        apm_valid = self.validate_apm_integration()
        metrics_valid = self.validate_custom_metrics()
        alerts_valid = self.validate_alert_system()
        dashboards_valid = self.validate_performance_dashboards()
        docs_valid = self.validate_documentation()
        
        # Calculate overall status
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results if result.status)
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        overall_status = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": success_rate,
            "overall_status": success_rate >= 90,
            "component_status": {
                "elk_stack": elk_valid,
                "apm_integration": apm_valid,
                "custom_metrics": metrics_valid,
                "alert_system": alerts_valid,
                "performance_dashboards": dashboards_valid,
                "documentation": docs_valid
            }
        }
        
        return overall_status
    
    def generate_report(self) -> str:
        """Generate detailed validation report"""
        overall_status = self.run_validation()
        
        report = f"""
# 🔍 Monitoring Stack Validation Report
Generated: {overall_status['timestamp']}

## 📊 Overall Status
- **Success Rate**: {overall_status['success_rate']:.1f}%
- **Total Checks**: {overall_status['total_checks']}
- **Passed**: {overall_status['passed_checks']}
- **Failed**: {overall_status['failed_checks']}
- **Overall Status**: {'✅ PASSED' if overall_status['overall_status'] else '❌ FAILED'}

## 🎯 Component Status Summary
"""
        
        for component, status in overall_status['component_status'].items():
            status_icon = "✅" if status else "❌"
            report += f"- **{component.replace('_', ' ').title()}**: {status_icon} {'PASSED' if status else 'FAILED'}\n"
        
        report += "\n## 📋 Detailed Results\n\n"
        
        # Group results by component
        by_component = {}
        for result in self.results:
            if result.component not in by_component:
                by_component[result.component] = []
            by_component[result.component].append(result)
        
        for component, results in by_component.items():
            report += f"### {component}\n\n"
            for result in results:
                status_icon = "✅" if result.status else "❌"
                report += f"- **{result.check_name}**: {status_icon} {result.message}\n"
                if result.details:
                    report += f"  - Details: {result.details}\n"
            report += "\n"
        
        return report

def main():
    """Main validation function"""
    validator = MonitoringValidator()
    
    try:
        # Generate validation report
        report = validator.generate_report()
        
        # Save report to file
        report_file = Path("/home/runner/work/Ainflue/Ainflue/docs/monitoring_validation_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 Full report saved to: {report_file}")
        
        # Exit with appropriate code
        overall_status = validator.run_validation()
        exit_code = 0 if overall_status['overall_status'] else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()