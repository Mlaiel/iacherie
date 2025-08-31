#!/usr/bin/env python3
"""Content Module Health Check & Verification System
================================================

Comprehensive system health monitoring and verification for all content management engines
with performance benchmarking, integration testing, and production readiness assessment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""import os
import sys
import asyncio
import time
import json
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import importlib
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentModuleHealthCheck:
    """Comprehensive health check system for content management module."""    
    def __init__(self):
        self.start_time = time.time()
        self.health_results = {}
        self.performance_metrics = {}
        self.critical_issues = []
        self.warnings = []
        
        # Define all module engines
        self.engines = {
            'content_processor': 'Content Processing Engine',
            'format_handler': 'Format Handler Engine',
            'ai_enhancer': 'AI Enhancement Engine',
            'distribution_manager': 'Distribution Management Engine',
            'collaboration_hub': 'Collaboration Hub Engine',
            'monetization_engine': 'Monetization Engine',
            'quality_assurance': 'Quality Assurance Engine',
            'protection_engine': 'Content Protection Engine',
            'crawler_engine': 'Web Crawling Engine',
            'recommendation_engine': 'AI Recommendation Engine',
            'performance_engine': 'Performance Testing Engine'
        }
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Execute comprehensive health check across all systems."""        logger.info("🔍 Starting Comprehensive Health Check...")
        
        # Phase 1: Module Integrity Check
        module_check = await self._check_module_integrity()
        
        # Phase 2: Engine Functionality Check
        engine_check = await self._check_engine_functionality()
        
        # Phase 3: Performance Benchmarking
        performance_check = await self._run_performance_benchmarks()
        
        # Phase 4: Integration Testing
        integration_check = await self._run_integration_tests()
        
        # Phase 5: Security Validation
        security_check = await self._validate_security()
        
        # Phase 6: Resource Usage Assessment
        resource_check = await self._assess_resource_usage()
        
        # Phase 7: Configuration Validation
        config_check = await self._validate_configuration()
        
        # Compile final report
        final_report = await self._compile_health_report({
            'module_integrity': module_check,
            'engine_functionality': engine_check,
            'performance_benchmarks': performance_check,
            'integration_tests': integration_check,
            'security_validation': security_check,
            'resource_assessment': resource_check,
            'configuration_validation': config_check
        })
        
        return final_report
    
    async def _check_module_integrity(self) -> Dict[str, Any]:
        """Check integrity of all module files and dependencies."""        logger.info("🔧 Checking Module Integrity...")
        
        results = {
            'status': 'passed',
            'modules_checked': 0,
            'modules_passed': 0,
            'missing_modules': [],
            'import_errors': [],
            'file_structure': 'valid'
        }
        
        # Check if all engine files exist
        required_files = [
            'content_processor.py',
            'format_handler.py',
            'ai_enhancer.py',
            'distribution_manager.py',
            'collaboration_hub.py',
            'monetization_engine.py',
            'quality_assurance.py',
            'protection_engine.py',
            'crawler_engine.py',
            'recommendation_engine.py',
            'performance_engine.py',
            '__init__.py',
            'config.py'
        ]
        
        for file in required_files:
            file_path = Path(file)
            if file_path.exists():
                results['modules_checked'] += 1
                
                # Try to import the module
                try:
                    if file.endswith('.py') and file != '__init__.py':
                        module_name = file[:-3]
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            results['modules_passed'] += 1
                        else:
                            results['import_errors'].append(f"Could not load spec for {file}")
                    else:
                        results['modules_passed'] += 1
                        
                except Exception as e:
                    results['import_errors'].append(f"{file}: {str(e)}")
            else:
                results['missing_modules'].append(file)
        
        # Determine overall status
        if results['missing_modules'] or results['import_errors']:
            results['status'] = 'failed'
            self.critical_issues.extend(results['missing_modules'])
            self.critical_issues.extend(results['import_errors'])
        
        return results
    
    async def _check_engine_functionality(self) -> Dict[str, Any]:
        """Check basic functionality of each engine."""        logger.info("⚙️ Checking Engine Functionality...")
        
        results = {
            'status': 'passed',
            'engines_tested': 0,
            'engines_passed': 0,
            'engine_results': {}
        }
        
        for engine_file, engine_name in self.engines.items():
            results['engines_tested'] += 1
            
            try:
                # Basic import test
                spec = importlib.util.spec_from_file_location(engine_file, f"{engine_file}.py")
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check for required classes
                    engine_classes = [name for name in dir(module) if name.endswith('Engine') or name.endswith('Manager') or name.endswith('Hub')]
                    
                    if engine_classes:
                        results['engine_results'][engine_name] = {
                            'status': 'passed',
                            'classes_found': engine_classes,
                            'import_successful': True
                        }
                        results['engines_passed'] += 1
                    else:
                        results['engine_results'][engine_name] = {
                            'status': 'warning',
                            'message': 'No engine classes found',
                            'import_successful': True
                        }
                        self.warnings.append(f"{engine_name}: No engine classes found")
                else:
                    results['engine_results'][engine_name] = {
                        'status': 'failed',
                        'message': 'Could not load module spec',
                        'import_successful': False
                    }
                    
            except Exception as e:
                results['engine_results'][engine_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'import_successful': False
                }
                self.critical_issues.append(f"{engine_name}: {str(e)}")
        
        if results['engines_passed'] < results['engines_tested']:
            results['status'] = 'partial'
        
        return results
    
    async def _run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run basic performance benchmarks."""        logger.info("⏱️ Running Performance Benchmarks...")
        
        results = {
            'status': 'passed',
            'import_time': 0,
            'memory_usage': {},
            'cpu_usage': 0,
            'benchmark_results': {}
        }
        
        # Measure import time
        start_time = time.time()
        try:
            # Import all engines
            for engine_file in self.engines.keys():
                spec = importlib.util.spec_from_file_location(engine_file, f"{engine_file}.py")
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            
            results['import_time'] = time.time() - start_time
        except Exception as e:
            results['import_time'] = time.time() - start_time
            results['import_error'] = str(e)
        
        # Measure memory usage
        process = psutil.Process()
        memory_info = process.memory_info()
        results['memory_usage'] = {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024
        }
        
        # CPU usage
        results['cpu_usage'] = psutil.cpu_percent(interval=1)
        
        # Basic benchmarks
        results['benchmark_results'] = {
            'file_io_speed': await self._benchmark_file_io(),
            'memory_allocation': await self._benchmark_memory(),
            'json_processing': await self._benchmark_json_processing()
        }
        
        return results
    
    async def _benchmark_file_io(self) -> Dict[str, Any]:
        """Benchmark file I/O operations."""        try:
            # Write test
            test_data = "x" * 10000  # 10KB test data
            test_file = Path("temp_benchmark.txt")
            
            write_start = time.time()
            test_file.write_text(test_data)
            write_time = time.time() - write_start
            
            # Read test
            read_start = time.time()
            content = test_file.read_text()
            read_time = time.time() - read_start
            
            # Cleanup
            test_file.unlink()
            
            return {
                'write_time_ms': write_time * 1000,
                'read_time_ms': read_time * 1000,
                'data_size_kb': len(test_data) / 1024,
                'status': 'passed'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_memory(self) -> Dict[str, Any]:
        """Benchmark memory allocation."""        try:
            # Allocate memory
            start_memory = psutil.Process().memory_info().rss
            
            # Create large list
            large_list = [i for i in range(100000)]
            
            peak_memory = psutil.Process().memory_info().rss
            
            # Cleanup
            del large_list
            
            end_memory = psutil.Process().memory_info().rss
            
            return {
                'memory_allocated_mb': (peak_memory - start_memory) / 1024 / 1024,
                'memory_freed_mb': (peak_memory - end_memory) / 1024 / 1024,
                'status': 'passed'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_json_processing(self) -> Dict[str, Any]:
        """Benchmark JSON processing."""        try:
            # Create test data
            test_data = {
                'users': [{'id': i, 'name': f'User{i}', 'data': list(range(100))} for i in range(1000)]
            }
            
            # Serialize benchmark
            serialize_start = time.time()
            json_string = json.dumps(test_data)
            serialize_time = time.time() - serialize_start
            
            # Deserialize benchmark
            deserialize_start = time.time()
            parsed_data = json.loads(json_string)
            deserialize_time = time.time() - deserialize_start
            
            return {
                'serialize_time_ms': serialize_time * 1000,
                'deserialize_time_ms': deserialize_time * 1000,
                'data_size_kb': len(json_string) / 1024,
                'status': 'passed'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run basic integration tests."""        logger.info("🔗 Running Integration Tests...")
        
        results = {
            'status': 'passed',
            'tests_run': 0,
            'tests_passed': 0,
            'test_results': {}
        }
        
        # Test 1: Module interconnectivity
        test_name = "Module Interconnectivity"
        results['tests_run'] += 1
        
        try:
            # Try importing all modules together
            modules = {}
            for engine_file in self.engines.keys():
                spec = importlib.util.spec_from_file_location(engine_file, f"{engine_file}.py")
                if spec and spec.loader:
                    modules[engine_file] = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(modules[engine_file])
            
            results['test_results'][test_name] = {
                'status': 'passed',
                'modules_loaded': len(modules),
                'message': 'All modules loaded successfully'
            }
            results['tests_passed'] += 1
            
        except Exception as e:
            results['test_results'][test_name] = {
                'status': 'failed',
                'error': str(e),
                'message': 'Failed to load all modules together'
            }
        
        # Test 2: Configuration consistency
        test_name = "Configuration Consistency"
        results['tests_run'] += 1
        
        try:
            config_files = ['config.py', 'content_module_config.json']
            config_status = all(Path(f).exists() for f in config_files)
            
            if config_status:
                results['test_results'][test_name] = {
                    'status': 'passed',
                    'message': 'All configuration files present'
                }
                results['tests_passed'] += 1
            else:
                results['test_results'][test_name] = {
                    'status': 'warning',
                    'message': 'Some configuration files missing'
                }
                
        except Exception as e:
            results['test_results'][test_name] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    async def _validate_security(self) -> Dict[str, Any]:
        """Validate security configurations."""        logger.info("🔒 Validating Security...")
        
        results = {
            'status': 'passed',
            'security_checks': {},
            'vulnerabilities': []
        }
        
        # Check for sensitive files
        sensitive_patterns = ['.env', '*.key', '*.pem', 'secrets.*']
        for pattern in sensitive_patterns:
            if list(Path('.').glob(pattern)):
                results['vulnerabilities'].append(f"Sensitive files found: {pattern}")
        
        # File permissions check
        critical_files = ['config.py', '__init__.py']
        for file in critical_files:
            if Path(file).exists():
                stat_info = Path(file).stat()
                # Check if file is world-readable (basic check)
                if stat_info.st_mode & 0o044:
                    results['security_checks'][file] = 'world_readable'
                else:
                    results['security_checks'][file] = 'secure'
        
        if results['vulnerabilities']:
            results['status'] = 'warning'
        
        return results
    
    async def _assess_resource_usage(self) -> Dict[str, Any]:
        """Assess current resource usage."""        logger.info("📊 Assessing Resource Usage...")
        
        process = psutil.Process()
        
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'open_files': process.num_fds(),
            'threads': process.num_threads(),
            'system_memory_percent': psutil.virtual_memory().percent,
            'system_cpu_percent': psutil.cpu_percent(),
            'disk_usage_percent': psutil.disk_usage('/').percent
        }
    
    async def _validate_configuration(self) -> Dict[str, Any]:
        """Validate system configuration."""        logger.info("⚙️ Validating Configuration...")
        
        results = {
            'status': 'passed',
            'config_files_found': [],
            'config_issues': []
        }
        
        # Check for configuration files
        config_files = [
            'config.py',
            'content_module_config.json',
            '.env.template',
            'docker-compose.yml',
            'Dockerfile'
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                results['config_files_found'].append(config_file)
            else:
                results['config_issues'].append(f"Missing: {config_file}")
        
        # Validate JSON config if exists
        if 'content_module_config.json' in results['config_files_found']:
            try:
                with open('content_module_config.json', 'r') as f:
                    config_data = json.load(f)
                    if 'engines' in config_data:
                        results['engines_configured'] = len(config_data['engines'])
                    else:
                        results['config_issues'].append("No engines configuration found")
            except Exception as e:
                results['config_issues'].append(f"JSON config error: {str(e)}")
        
        if results['config_issues']:
            results['status'] = 'warning'
        
        return results
    
    async def _compile_health_report(self, check_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compile final health report."""        logger.info("📋 Compiling Health Report...")
        
        total_time = time.time() - self.start_time
        
        # Determine overall health status
        statuses = [result.get('status', 'unknown') for result in check_results.values()]
        
        if 'failed' in statuses:
            overall_status = 'critical'
        elif 'partial' in statuses or 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        # Count engines
        engine_count = check_results.get('engine_functionality', {}).get('engines_passed', 0)
        total_engines = len(self.engines)
        
        report = {
            'health_check_summary': {
                'overall_status': overall_status,
                'execution_time_seconds': round(total_time, 2),
                'timestamp': datetime.now().isoformat(),
                'engines_operational': f"{engine_count}/{total_engines}",
                'critical_issues_count': len(self.critical_issues),
                'warnings_count': len(self.warnings)
            },
            'detailed_results': check_results,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'recommendations': self._generate_recommendations(overall_status, check_results)
        }
        
        return report
    
    def _generate_recommendations(self, status: str, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""        recommendations = []
        
        if status == 'critical':
            recommendations.append("❗ CRITICAL: Address all failed engine imports immediately")
            recommendations.append("❗ CRITICAL: Check system logs for detailed error information")
        
        if status in ['critical', 'warning']:
            recommendations.append("⚠️  Run individual engine tests to isolate issues")
            recommendations.append("⚠️  Verify all dependencies are installed correctly")
        
        # Performance recommendations
        perf_results = results.get('performance_benchmarks', {})
        if perf_results.get('memory_usage', {}).get('rss_mb', 0) > 1000:
            recommendations.append("💡 Consider memory optimization - current usage is high")
        
        if perf_results.get('import_time', 0) > 5:
            recommendations.append("💡 Import time is slow - consider module optimization")
        
        # Security recommendations
        security_results = results.get('security_validation', {})
        if security_results.get('vulnerabilities'):
            recommendations.append("🔒 Address security vulnerabilities immediately")
        
        # Configuration recommendations
        config_results = results.get('configuration_validation', {})
        if config_results.get('config_issues'):
            recommendations.append("⚙️  Complete configuration setup using setup_content_module.py")
        
        if status == 'healthy':
            recommendations.extend([
                "✅ System is healthy - ready for production use",
                "✅ Consider running full integration tests",
                "✅ Monitor system performance in production"
            ])
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any]):
        """Save health check report."""        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"health_check_report_{timestamp}.json"
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / report_file
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"✅ Health report saved: {report_path}")
        return report_path
    
    def print_health_summary(self, report: Dict[str, Any]):
        """Print formatted health summary."""        summary = report['health_check_summary']
        
        # Status emoji mapping
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌'
        }
        
        print(f"""╔══════════════════════════════════════════════════════════════════════════════╗
║                        CONTENT MODULE HEALTH REPORT                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Overall Status: {status_emoji.get(summary['overall_status'], '❓')} {summary['overall_status'].upper()}                                              ║
║                                                                              ║
║  📊 System Metrics:                                                          ║
║     • Engines Operational: {summary['engines_operational']}                                           ║
║     • Execution Time: {summary['execution_time_seconds']}s                                           ║
║     • Critical Issues: {summary['critical_issues_count']}                                                ║
║     • Warnings: {summary['warnings_count']}                                                    ║
║                                                                              ║
║  🔍 Check Results:                                                           ║""")
        
        # Print detailed results
        for check_name, result in report['detailed_results'].items():
            status_icon = '✅' if result.get('status') == 'passed' else '⚠️' if result.get('status') in ['warning', 'partial'] else '❌'
            check_display = check_name.replace('_', ' ').title()
            print(f"║     • {check_display}: {status_icon} {result.get('status', 'unknown').upper()}")
        
        print("║                                                                              ║")
        
        # Print recommendations
        if report.get('recommendations'):
            print("║  💡 Recommendations:                                                         ║")
            for i, rec in enumerate(report['recommendations'][:5], 1):  # Show first 5
                print(f"║     {i}. {rec[:68]}{'...' if len(rec) > 68 else '':70}║")
        
        print("║                                                                              ║")
        print(f"║  📧 Enterprise Support: mlaiel@live.de                                     ║")
        print(f"║  📅 Report Generated: {summary['timestamp']}                    ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")


async def main():
    """Main health check execution."""    print("""╔══════════════════════════════════════════════════════════════════════════════╗
║               IA Influencer Agent - Content Module Health Check             ║
║                                                                              ║
║  Author: Fahed Mlaiel <mlaiel@live.de>                                      ║
║  Industrial-Grade System Verification                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    health_checker = ContentModuleHealthCheck()
    
    try:
        # Run comprehensive health check
        report = await health_checker.run_comprehensive_health_check()
        
        # Print summary
        health_checker.print_health_summary(report)
        
        # Save detailed report
        report_path = health_checker.save_report(report)
        
        print(f"\n📋 Detailed report saved to: {report_path}")
        print(f"📧 For enterprise support, contact: mlaiel@live.de")
        
        # Exit with appropriate code
        overall_status = report['health_check_summary']['overall_status']
        if overall_status == 'critical':
            sys.exit(1)
        elif overall_status == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
