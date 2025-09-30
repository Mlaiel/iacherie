#!/usr/bin/env python3
"""
Distribution Module Health Check System
======================================

Comprehensive health check and validation system for the Ainflue Distribution Module.
Validates all modules are properly configured and functioning according to the enterprise checklist.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
import os
import importlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"

@dataclass
class ModuleHealthResult:
    """Health check result for a single module"""
    module_name: str
    status: HealthStatus
    import_successful: bool
    class_instantiation: bool
    method_availability: List[str] = field(default_factory=list)
    missing_methods: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class DistributionHealthReport:
    """Comprehensive health report for the distribution module"""
    overall_status: HealthStatus
    total_modules_checked: int
    healthy_modules: int
    warning_modules: int
    critical_modules: int
    unavailable_modules: int
    module_results: Dict[str, ModuleHealthResult] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class DistributionHealthChecker:
    """Enterprise-grade health checker for distribution modules"""
    
    def __init__(self):
        self.modules_to_check = {
            # Crisis Management Suite
            'crisis_management.sentiment_monitor': {
                'class': 'SentimentMonitor',
                'critical_methods': ['analyze_sentiment', 'get_sentiment_score'],
                'optional_methods': ['start_monitoring', 'stop_monitoring']
            },
            'crisis_management.crisis_detector': {
                'class': 'CrisisDetector', 
                'critical_methods': ['monitor_for_crisis'],
                'optional_methods': ['active_monitoring', 'detection_models']
            },
            'crisis_management.damage_control_engine': {
                'class': 'DamageControlEngine',
                'critical_methods': ['execute_damage_control'],
                'optional_methods': ['adapt_control_strategy', 'control_strategies']
            },
            'crisis_management.recovery_planner': {
                'class': 'RecoveryPlanner',
                'critical_methods': ['create_recovery_plan'],
                'optional_methods': ['estimate_recovery_time']
            },
            
            # Real-time Optimization
            'real_time_optimization.live_performance_monitor': {
                'class': 'LivePerformanceMonitor',
                'critical_methods': ['get_real_time_metrics', 'start_monitoring'],
                'optional_methods': ['check_performance_alerts', 'stop_monitoring']
            },
            'real_time_optimization.adaptive_optimizer': {
                'class': 'AdaptiveOptimizer',
                'critical_methods': ['run_adaptive_optimization'],
                'optional_methods': ['adapt_to_performance_changes', 'get_optimization_recommendations']
            },
            
            # Content Amplification
            'content_amplification.amplification_engine': {
                'class': 'IntelligentAmplificationEngine',
                'critical_methods': ['create_amplification_plan', 'execute_amplification_plan'],
                'optional_methods': ['amplification_models', 'budget_optimizers']
            },
            
            # Viral Optimization
            'viral_optimization.viral_predictor': {
                'class': 'ViralPredictor',
                'critical_methods': ['predict_virality'],
                'optional_methods': ['feature_extractors']
            },
            'viral_optimization.trend_analyzer': {
                'class': 'TrendAnalyzer',
                'critical_methods': ['analyze_trends'],
                'optional_methods': ['get_trending_opportunities', 'predict_trend_lifecycle']
            },
            
            # Platform Optimization
            'platform_optimization.platform_analyzer': {
                'class': 'PlatformAnalyzer',
                'critical_methods': ['analyze_platform_performance'],
                'optional_methods': ['get_optimization_recommendations']
            },
            'platform_optimization.algorithm_tracker': {
                'class': 'AlgorithmTracker',
                'critical_methods': ['track_algorithm_changes'],
                'optional_methods': ['detect_algorithm_updates']
            },
            
            # Analytics Suite
            'cohort_analytics': {
                'class': 'CohortAnalytics',
                'critical_methods': ['analyze_cohorts'],
                'optional_methods': ['calculate_retention_rates']
            },
            'funnel_analytics': {
                'class': 'FunnelAnalytics',
                'critical_methods': ['analyze_conversion_funnel'],
                'optional_methods': ['calculate_conversion_rates']
            },
            'lifetime_value_analytics': {
                'class': 'LifetimeValueAnalytics',
                'critical_methods': ['calculate_customer_ltv'],
                'optional_methods': ['predict_future_value']
            },
            
            # Core Modules
            'platform_connectors': {
                'class': 'PlatformConnectorManager',
                'critical_methods': [],
                'optional_methods': ['create_connector']
            }
        }
    
    async def check_module_health(self, module_path: str, module_config: Dict[str, Any]) -> ModuleHealthResult:
        """Check health of a single module"""
        start_time = datetime.now(timezone.utc)
        result = ModuleHealthResult(
            module_name=module_path,
            status=HealthStatus.HEALTHY,
            import_successful=False,
            class_instantiation=False
        )
        
        try:
            # Try to import the module
            full_module_path = f"distribution.{module_path}"
            module = importlib.import_module(full_module_path)
            result.import_successful = True
            logger.info(f"✅ Successfully imported {full_module_path}")
            
            # Try to instantiate the main class
            class_name = module_config.get('class')
            if class_name and hasattr(module, class_name):
                cls = getattr(module, class_name)
                instance = cls()
                result.class_instantiation = True
                logger.info(f"✅ Successfully instantiated {class_name}")
                
                # Check for critical methods
                critical_methods = module_config.get('critical_methods', [])
                optional_methods = module_config.get('optional_methods', [])
                
                for method in critical_methods:
                    if hasattr(instance, method):
                        result.method_availability.append(method)
                    else:
                        result.missing_methods.append(method)
                        result.errors.append(f"Critical method missing: {method}")
                        result.status = HealthStatus.CRITICAL
                
                for method in optional_methods:
                    if hasattr(instance, method):
                        result.method_availability.append(method)
                    else:
                        result.missing_methods.append(method)
                        result.warnings.append(f"Optional method missing: {method}")
                        if result.status == HealthStatus.HEALTHY:
                            result.status = HealthStatus.WARNING
                
            else:
                result.errors.append(f"Class {class_name} not found in module")
                result.status = HealthStatus.CRITICAL
                
        except ImportError as e:
            result.errors.append(f"Import failed: {str(e)}")
            result.status = HealthStatus.UNAVAILABLE
            logger.warning(f"❌ Failed to import {module_path}: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            result.status = HealthStatus.CRITICAL
            logger.error(f"❌ Unexpected error in {module_path}: {e}")
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    async def run_comprehensive_health_check(self) -> DistributionHealthReport:
        """Run comprehensive health check on all distribution modules"""
        logger.info("🚀 Starting comprehensive distribution module health check...")
        
        report = DistributionHealthReport(
            overall_status=HealthStatus.HEALTHY,
            total_modules_checked=len(self.modules_to_check),
            healthy_modules=0,
            warning_modules=0,
            critical_modules=0,
            unavailable_modules=0
        )
        
        # Check each module
        for module_path, module_config in self.modules_to_check.items():
            logger.info(f"Checking module: {module_path}")
            result = await self.check_module_health(module_path, module_config)
            report.module_results[module_path] = result
            
            # Update counters
            if result.status == HealthStatus.HEALTHY:
                report.healthy_modules += 1
            elif result.status == HealthStatus.WARNING:
                report.warning_modules += 1
            elif result.status == HealthStatus.CRITICAL:
                report.critical_modules += 1
            elif result.status == HealthStatus.UNAVAILABLE:
                report.unavailable_modules += 1
        
        # Determine overall status
        if report.critical_modules > 0 or report.unavailable_modules > 5:
            report.overall_status = HealthStatus.CRITICAL
        elif report.warning_modules > 3 or report.unavailable_modules > 0:
            report.overall_status = HealthStatus.WARNING
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)
        
        # Add performance metrics
        report.performance_metrics = self._calculate_performance_metrics(report)
        
        # Add compliance status
        report.compliance_status = self._check_compliance_status(report)
        
        logger.info(f"🏁 Health check completed. Overall status: {report.overall_status.value}")
        return report
    
    def _generate_recommendations(self, report: DistributionHealthReport) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []
        
        if report.critical_modules > 0:
            recommendations.append("🚨 CRITICAL: Some modules have critical issues that need immediate attention")
        
        if report.unavailable_modules > 0:
            recommendations.append("⚠️ Some modules are unavailable - check imports and dependencies")
        
        if report.warning_modules > 0:
            recommendations.append("⚠️ Some modules have warnings - consider implementing missing optional methods")
        
        # Check for specific patterns
        crisis_modules = [name for name in report.module_results.keys() if 'crisis_management' in name]
        crisis_issues = sum(1 for name in crisis_modules 
                          if report.module_results[name].status in [HealthStatus.CRITICAL, HealthStatus.UNAVAILABLE])
        
        if crisis_issues > 0:
            recommendations.append("🛡️ Crisis management modules need attention - this impacts platform safety")
        
        if report.healthy_modules / report.total_modules_checked > 0.8:
            recommendations.append("✅ Good overall module health - continue monitoring")
        
        return recommendations
    
    def _calculate_performance_metrics(self, report: DistributionHealthReport) -> Dict[str, Any]:
        """Calculate performance metrics from health check results"""
        total_time = sum(result.execution_time_ms for result in report.module_results.values())
        avg_time = total_time / len(report.module_results) if report.module_results else 0
        
        return {
            'total_check_time_ms': total_time,
            'average_check_time_ms': avg_time,
            'success_rate': report.healthy_modules / report.total_modules_checked,
            'module_availability_rate': (report.total_modules_checked - report.unavailable_modules) / report.total_modules_checked
        }
    
    def _check_compliance_status(self, report: DistributionHealthReport) -> Dict[str, bool]:
        """Check compliance with enterprise requirements"""
        return {
            'crisis_management_available': any('crisis_management' in name for name in report.module_results.keys()),
            'real_time_optimization_available': any('real_time_optimization' in name for name in report.module_results.keys()),
            'viral_optimization_available': any('viral_optimization' in name for name in report.module_results.keys()),
            'analytics_suite_available': any(name in ['cohort_analytics', 'funnel_analytics', 'lifetime_value_analytics'] 
                                            for name in report.module_results.keys()),
            'minimum_module_threshold': report.healthy_modules >= 8,
            'critical_modules_operational': report.critical_modules == 0
        }
    
    def generate_report_json(self, report: DistributionHealthReport) -> str:
        """Generate JSON report"""
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        report_dict = {
            'overall_status': report.overall_status.value,
            'summary': {
                'total_modules_checked': report.total_modules_checked,
                'healthy_modules': report.healthy_modules,
                'warning_modules': report.warning_modules,
                'critical_modules': report.critical_modules,
                'unavailable_modules': report.unavailable_modules
            },
            'performance_metrics': report.performance_metrics,
            'compliance_status': report.compliance_status,
            'recommendations': report.recommendations,
            'generated_at': report.generated_at.isoformat(),
            'module_details': {}
        }
        
        for module_name, result in report.module_results.items():
            report_dict['module_details'][module_name] = {
                'status': result.status.value,
                'import_successful': result.import_successful,
                'class_instantiation': result.class_instantiation,
                'available_methods': result.method_availability,
                'missing_methods': result.missing_methods,
                'errors': result.errors,
                'warnings': result.warnings,
                'execution_time_ms': result.execution_time_ms,
                'last_checked': result.last_checked.isoformat()
            }
        
        return json.dumps(report_dict, indent=2, default=serialize_datetime)
    
    def print_console_report(self, report: DistributionHealthReport):
        """Print a formatted console report"""
        print("\n" + "="*80)
        print("🚀 AINFLUE DISTRIBUTION MODULE HEALTH CHECK REPORT")
        print("="*80)
        print(f"📊 Overall Status: {report.overall_status.value.upper()}")
        print(f"📅 Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("\n📈 SUMMARY:")
        print(f"   ✅ Healthy: {report.healthy_modules}/{report.total_modules_checked}")
        print(f"   ⚠️ Warning: {report.warning_modules}/{report.total_modules_checked}")
        print(f"   🚨 Critical: {report.critical_modules}/{report.total_modules_checked}")
        print(f"   ❌ Unavailable: {report.unavailable_modules}/{report.total_modules_checked}")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Success Rate: {report.performance_metrics.get('success_rate', 0):.1%}")
        print(f"   Availability Rate: {report.performance_metrics.get('module_availability_rate', 0):.1%}")
        print(f"   Avg Check Time: {report.performance_metrics.get('average_check_time_ms', 0):.1f}ms")
        
        print(f"\n📋 COMPLIANCE:")
        for check, status in report.compliance_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check.replace('_', ' ').title()}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"   {rec}")
        
        if report.critical_modules > 0 or report.unavailable_modules > 0:
            print(f"\n🚨 ISSUES FOUND:")
            for module_name, result in report.module_results.items():
                if result.status in [HealthStatus.CRITICAL, HealthStatus.UNAVAILABLE]:
                    print(f"   ❌ {module_name}: {result.status.value}")
                    for error in result.errors:
                        print(f"      • {error}")
        
        print("="*80 + "\n")

async def main():
    """Main function to run the health check"""
    try:
        # Add the project root to Python path
        sys.path.insert(0, '/home/runner/work/Ainflue/Ainflue')
        
        checker = DistributionHealthChecker()
        report = await checker.run_comprehensive_health_check()
        
        # Print console report
        checker.print_console_report(report)
        
        # Save JSON report
        json_report = checker.generate_report_json(report)
        with open('/tmp/distribution_health_report.json', 'w') as f:
            f.write(json_report)
        
        print(f"📁 Detailed JSON report saved to: /tmp/distribution_health_report.json")
        
        # Return appropriate exit code
        if report.overall_status == HealthStatus.CRITICAL:
            return 2
        elif report.overall_status == HealthStatus.WARNING:
            return 1
        else:
            return 0
            
    except Exception as e:
        logger.error(f"Health check failed with error: {e}")
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)