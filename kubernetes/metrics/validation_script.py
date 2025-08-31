"""
IA Influencer Agent - Metrics Module Validation Script
Comprehensive validation of all metrics modules and dependencies

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

  AVERTISSEMENT LÉGAL STRICT 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Module import validation
- Configuration validation
- Dependency checking
- Integration testing
- Performance benchmarking
"""

import sys
import traceback
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging for validation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsModuleValidator:
    """
    Comprehensive validator for the metrics deployment module
    
    Validates:
    - Module imports and dependencies
    - Configuration consistency
    - Service initialization
    - Collector functionality
    - Integration capabilities
    """
    
    def __init__(self):
        self.validation_results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    async def validate_complete_module(self) -> Dict[str, Any]:
        """Run complete validation of metrics module"""
        
        logger.info(" Starting comprehensive metrics module validation...")
        
        # Validation stages
        validation_stages = [
            ("Core Imports", self._validate_core_imports),
            ("Advanced Collectors", self._validate_advanced_collectors),
            ("Configuration", self._validate_configuration),
            ("Data Models", self._validate_data_models),
            ("Integration Points", self._validate_integration_points),
            ("Business Logic", self._validate_business_logic),
            ("Performance", self._validate_performance_readiness)
        ]
        
        for stage_name, validation_func in validation_stages:
            try:
                logger.info(f" Validating: {stage_name}")
                result = await validation_func()
                self.validation_results[stage_name] = result
                
                if result.get('status') == 'success':
                    logger.info(f" {stage_name}: PASSED")
                else:
                    logger.warning(f" {stage_name}: ISSUES FOUND")
                    
            except Exception as e:
                error_msg = f" {stage_name}: FAILED - {str(e)}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                self.validation_results[stage_name] = {
                    'status': 'error',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
        
        # Generate final report
        return self._generate_validation_report()
    
    async def _validate_core_imports(self) -> Dict[str, Any]:
        """Validate core module imports"""
        
        results = {
            'status': 'success',
            'imported_modules': [],
            'failed_imports': []
        }
        
        core_imports = [
            ('PrometheusManager', 'backend.deployment.metrics'),
            ('GrafanaManager', 'backend.deployment.metrics'),
            ('MetricsCollector', 'backend.deployment.metrics'),
            ('AlertManager', 'backend.deployment.metrics'),
            ('PerformanceAnalytics', 'backend.deployment.metrics'),
            ('MetricsDashboard', 'backend.deployment.metrics'),
            ('BusinessIntelligence', 'backend.deployment.metrics'),
            ('get_metrics_config', 'backend.deployment.metrics'),
            ('MetricsConfiguration', 'backend.deployment.metrics'),
            ('MetricsEnvironment', 'backend.deployment.metrics')
        ]
        
        for class_name, module_path in core_imports:
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                results['imported_modules'].append(class_name)
                logger.debug(f" Successfully imported {class_name}")
                
            except ImportError as e:
                error_msg = f"Failed to import {class_name}: {str(e)}"
                results['failed_imports'].append(error_msg)
                logger.error(f" {error_msg}")
                
        if results['failed_imports']:
            results['status'] = 'partial'
            
        return results
    
    async def _validate_advanced_collectors(self) -> Dict[str, Any]:
        """Validate advanced metrics collectors"""
        
        results = {
            'status': 'success',
            'collectors_validated': [],
            'failed_validations': []
        }
        
        advanced_collectors = [
            'WebSurveillanceMetricsCollector',
            'LicensingAutomationMetricsCollector',
            'FingerprintingPerformanceMetricsCollector',
            'PlatformIntegrationMetricsCollector'
        ]
        
        for collector_name in advanced_collectors:
            try:
                module = __import__('backend.deployment.metrics', fromlist=[collector_name])
                collector_class = getattr(module, collector_name)
                
                # Validate class structure
                required_methods = [
                    '__init__',
                    'get_health_status'
                ]
                
                for method in required_methods:
                    if not hasattr(collector_class, method):
                        raise AttributeError(f"Missing required method: {method}")
                
                results['collectors_validated'].append(collector_name)
                logger.debug(f" Validated collector: {collector_name}")
                
            except Exception as e:
                error_msg = f"Collector {collector_name} validation failed: {str(e)}"
                results['failed_validations'].append(error_msg)
                logger.error(f" {error_msg}")
        
        if results['failed_validations']:
            results['status'] = 'partial'
            
        return results
    
    async def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration system"""
        
        results = {
            'status': 'success',
            'config_tests': {},
            'validation_issues': []
        }
        
        try:
            # Test configuration loading
            from backend.deployment.metrics import get_metrics_config, MetricsEnvironment
            
            # Test different environments
            environments = [
                MetricsEnvironment.DEVELOPMENT,
                MetricsEnvironment.STAGING,
                MetricsEnvironment.PRODUCTION
            ]
            
            for env in environments:
                try:
                    config = get_metrics_config(env)
                    validation_issues = config.validate_configuration()
                    
                    results['config_tests'][env.value] = {
                        'loaded': True,
                        'validation_issues': validation_issues,
                        'prometheus_enabled': config.prometheus.enabled,
                        'grafana_enabled': config.grafana.enabled,
                        'alerts_enabled': config.alerts.enabled
                    }
                    
                    if validation_issues:
                        self.warnings.extend(validation_issues)
                    
                except Exception as e:
                    results['config_tests'][env.value] = {
                        'loaded': False,
                        'error': str(e)
                    }
                    results['validation_issues'].append(f"Config {env.value}: {str(e)}")
            
            if results['validation_issues']:
                results['status'] = 'partial'
                
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results
    
    async def _validate_data_models(self) -> Dict[str, Any]:
        """Validate data models and enums"""
        
        results = {
            'status': 'success',
            'models_validated': [],
            'enum_validations': {},
            'validation_errors': []
        }
        
        # Test enum imports and values
        enum_tests = [
            ('CrawlerPlatform', ['YOUTUBE', 'INSTAGRAM', 'TIKTOK']),
            ('LicenseType', ['COMMERCIAL', 'PERSONAL', 'EXCLUSIVE']),
            ('ContentType', ['AUDIO', 'VIDEO', 'IMAGE', 'TEXT']),
            ('ProcessingStage', ['PREPROCESSING', 'FEATURE_EXTRACTION']),
            ('IntegrationType', ['API_DIRECT', 'OAUTH2', 'WEBHOOK'])
        ]
        
        for enum_name, expected_values in enum_tests:
            try:
                module = __import__('backend.deployment.metrics', fromlist=[enum_name])
                enum_class = getattr(module, enum_name)
                
                # Check if expected values exist
                missing_values = []
                for value in expected_values:
                    if not hasattr(enum_class, value):
                        missing_values.append(value)
                
                results['enum_validations'][enum_name] = {
                    'exists': True,
                    'missing_values': missing_values,
                    'total_values': len(list(enum_class))
                }
                
                if missing_values:
                    self.warnings.append(f"Enum {enum_name} missing values: {missing_values}")
                
            except Exception as e:
                results['enum_validations'][enum_name] = {
                    'exists': False,
                    'error': str(e)
                }
                results['validation_errors'].append(f"Enum {enum_name}: {str(e)}")
        
        # Test dataclass models
        model_tests = [
            'CrawlerSession',
            'ContentMatch',
            'LicenseTransaction',
            'RightsNegotiation',
            'FingerprintingJob',
            'MatchResult',
            'PlatformConnection',
            'APICall'
        ]
        
        for model_name in model_tests:
            try:
                module = __import__('backend.deployment.metrics', fromlist=[model_name])
                model_class = getattr(module, model_name)
                
                # Check if it's a dataclass
                if hasattr(model_class, '__dataclass_fields__'):
                    results['models_validated'].append(model_name)
                else:
                    self.warnings.append(f"Model {model_name} is not a dataclass")
                
            except Exception as e:
                results['validation_errors'].append(f"Model {model_name}: {str(e)}")
        
        if results['validation_errors']:
            results['status'] = 'partial'
            
        return results
    
    async def _validate_integration_points(self) -> Dict[str, Any]:
        """Validate integration capabilities"""
        
        results = {
            'status': 'success',
            'integrations_tested': {},
            'missing_integrations': []
        }
        
        # Test deployment manager
        try:
            from backend.deployment.metrics import (
                MetricsDeploymentManager,
                get_metrics_deployment_manager,
                metrics_deployment_context
            )
            
            # Test manager instantiation
            manager = MetricsDeploymentManager()
            health_status = manager.get_health_status()
            
            results['integrations_tested']['deployment_manager'] = {
                'instantiated': True,
                'health_status': health_status
            }
            
            # Test context manager
            results['integrations_tested']['context_manager'] = {
                'available': callable(metrics_deployment_context)
            }
            
            # Test global manager
            global_manager = get_metrics_deployment_manager()
            results['integrations_tested']['global_manager'] = {
                'available': global_manager is not None
            }
            
        except Exception as e:
            results['integrations_tested']['deployment_manager'] = {
                'error': str(e)
            }
            results['status'] = 'partial'
        
        return results
    
    async def _validate_business_logic(self) -> Dict[str, Any]:
        """Validate business logic alignment"""
        
        results = {
            'status': 'success',
            'business_flows': {},
            'alignment_score': 0
        }
        
        # Business flow requirements from cahier des charges
        required_flows = [
            'content_protection_workflow',
            'licensing_automation_workflow', 
            'web_surveillance_workflow',
            'platform_integration_workflow',
            'revenue_tracking_workflow'
        ]
        
        validated_flows = 0
        
        for flow in required_flows:
            try:
                # Check if related collectors exist
                flow_mappings = {
                    'content_protection_workflow': ['ContentProtectionMetricsCollector', 'FingerprintingPerformanceMetricsCollector'],
                    'licensing_automation_workflow': ['LicensingAutomationMetricsCollector', 'RevenueMetricsCollector'],
                    'web_surveillance_workflow': ['WebSurveillanceMetricsCollector'],
                    'platform_integration_workflow': ['PlatformIntegrationMetricsCollector'],
                    'revenue_tracking_workflow': ['RevenueMetricsCollector', 'BusinessEventsCollector']
                }
                
                required_collectors = flow_mappings.get(flow, [])
                available_collectors = []
                
                for collector in required_collectors:
                    try:
                        module = __import__('backend.deployment.metrics', fromlist=[collector])
                        getattr(module, collector)
                        available_collectors.append(collector)
                    except:
                        pass
                
                flow_coverage = len(available_collectors) / len(required_collectors) if required_collectors else 0
                
                results['business_flows'][flow] = {
                    'required_collectors': required_collectors,
                    'available_collectors': available_collectors,
                    'coverage': flow_coverage
                }
                
                if flow_coverage >= 0.8:  # 80% coverage threshold
                    validated_flows += 1
                
            except Exception as e:
                results['business_flows'][flow] = {
                    'error': str(e),
                    'coverage': 0
                }
        
        results['alignment_score'] = (validated_flows / len(required_flows)) * 100
        
        if results['alignment_score'] < 80:
            results['status'] = 'partial'
            self.warnings.append(f"Business logic alignment below 80%: {results['alignment_score']:.1f}%")
        
        return results
    
    async def _validate_performance_readiness(self) -> Dict[str, Any]:
        """Validate performance and production readiness"""
        
        results = {
            'status': 'success',
            'performance_metrics': {},
            'production_readiness': {}
        }
        
        # Test import performance
        start_time = datetime.utcnow()
        try:
            from backend.deployment.metrics import *
            import_time = (datetime.utcnow() - start_time).total_seconds()
            
            results['performance_metrics']['import_time_seconds'] = import_time
            
            if import_time > 5.0:  # Import should be under 5 seconds
                self.warnings.append(f"Module import time is high: {import_time:.2f}s")
            
        except Exception as e:
            results['performance_metrics']['import_error'] = str(e)
            results['status'] = 'partial'
        
        # Check production readiness indicators
        production_checks = [
            ('Prometheus integration', 'PrometheusManager'),
            ('Grafana integration', 'GrafanaManager'),
            ('Alert system', 'AlertManager'),
            ('Configuration management', 'MetricsConfiguration'),
            ('Deployment manager', 'MetricsDeploymentManager')
        ]
        
        production_score = 0
        for check_name, component in production_checks:
            try:
                module = __import__('backend.deployment.metrics', fromlist=[component])
                getattr(module, component)
                results['production_readiness'][check_name] = True
                production_score += 1
            except:
                results['production_readiness'][check_name] = False
        
        results['production_readiness']['score'] = (production_score / len(production_checks)) * 100
        
        if results['production_readiness']['score'] < 90:
            results['status'] = 'partial'
            self.warnings.append(f"Production readiness below 90%: {results['production_readiness']['score']:.1f}%")
        
        return results
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_stages = len(self.validation_results)
        successful_stages = sum(1 for result in self.validation_results.values() 
                              if result.get('status') == 'success')
        
        overall_status = 'success'
        if self.errors:
            overall_status = 'error'
        elif successful_stages < total_stages:
            overall_status = 'partial'
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': overall_status,
            'summary': {
                'total_stages': total_stages,
                'successful_stages': successful_stages,
                'success_rate': (successful_stages / total_stages) * 100 if total_stages > 0 else 0,
                'error_count': len(self.errors),
                'warning_count': len(self.warnings)
            },
            'detailed_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        # Check if there are import failures
        core_imports = self.validation_results.get('Core Imports', {})
        if core_imports.get('failed_imports'):
            recommendations.append(
                "Fix import failures before proceeding to production deployment"
            )
        
        # Check configuration issues
        config_results = self.validation_results.get('Configuration', {})
        if config_results.get('validation_issues'):
            recommendations.append(
                "Review and fix configuration validation issues"
            )
        
        # Check business logic alignment
        business_results = self.validation_results.get('Business Logic', {})
        alignment_score = business_results.get('alignment_score', 0)
        if alignment_score < 90:
            recommendations.append(
                f"Improve business logic alignment (current: {alignment_score:.1f}%, target: 90%+)"
            )
        
        # Check production readiness
        performance_results = self.validation_results.get('Performance', {})
        prod_readiness = performance_results.get('production_readiness', {})
        prod_score = prod_readiness.get('score', 0)
        if prod_score < 95:
            recommendations.append(
                f"Enhance production readiness (current: {prod_score:.1f}%, target: 95%+)"
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                " All validations passed! Module is ready for production deployment."
            )
        else:
            recommendations.append(
                " Address the above issues before production deployment"
            )
        
        return recommendations


async def main():
    """Run complete metrics module validation"""
    
    print(" IA Influencer Agent - Metrics Module Validation")
    print("=" * 60)
    print(f" Started: {datetime.utcnow().isoformat()}")
    print(f"‍ Validator: Fahed Mlaiel")
    print(f" Contact: mlaiel@live.de")
    print("=" * 60)
    
    validator = MetricsModuleValidator()
    
    try:
        report = await validator.validate_complete_module()
        
        # Display summary
        print(f"\n VALIDATION SUMMARY")
        print("=" * 40)
        print(f"Overall Status: {report['overall_status'].upper()}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Errors: {report['summary']['error_count']}")
        print(f"Warnings: {report['summary']['warning_count']}")
        
        # Display recommendations
        print(f"\n RECOMMENDATIONS")
        print("=" * 40)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # Display errors if any
        if report['errors']:
            print(f"\n ERRORS")
            print("=" * 40)
            for error in report['errors']:
                print(f"• {error}")
        
        # Display warnings if any
        if report['warnings']:
            print(f"\n WARNINGS")
            print("=" * 40)
            for warning in report['warnings']:
                print(f"• {warning}")
        
        print(f"\n Validation completed at: {datetime.utcnow().isoformat()}")
        
        # Return appropriate exit code
        if report['overall_status'] == 'error':
            return 1
        elif report['overall_status'] == 'partial':
            return 2
        else:
            return 0
            
    except Exception as e:
        print(f"\n VALIDATION FAILED")
        print("=" * 40)
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
