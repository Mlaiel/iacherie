"""
Service Mesh Tester module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Service Mesh Tester - Ainflue Quality Platform
============================================

Enterprise service mesh communication testing system.
Demonstrates Microservices Architect + DevOps + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import aiohttp
import asyncio
import kubernetes
from kubernetes import client, config
import istio_client
import consul

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceMeshTestResult:
    """Service mesh test result."""
    test_name: str
    test_category: str  # 'discovery', 'routing', 'security', 'observability', 'resilience'
    service_name: str
    mesh_type: str  # 'istio', 'consul', 'linkerd', 'envoy'
    status: str  # 'passed', 'failed', 'warning', 'error'
    execution_time_ms: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceMeshConfig:
    """Service mesh configuration."""
    mesh_type: str
    namespace: str
    services: List[str]
    gateway_endpoints: List[str] = field(default_factory=list)
    auth_config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30


class IstioServiceMeshTester:
    """Istio service mesh testing implementation."""
    
    def __init__(self, config -> None: ServiceMeshConfig) -> None:
        self.config = config
        self.k8s_client = None
        self.istio_client = None
        
    async def initialize(self) -> None:
        """Initialize Kubernetes and Istio clients."""
        try:
            # Load Kubernetes config
            config.load_incluster_config()  # For in-cluster access
        except:
            try:
                config.load_kube_config()  # For local development
            except Exception as e:
                logger.warning(f"Failed to load Kubernetes config: {e}")
        
        self.k8s_client = client.ApiClient()
        logger.info("Kubernetes client initialized")
    
    async def test_service_discovery(self, service_name: str) -> ServiceMeshTestResult:
        """Test service discovery in Istio."""
        start_time = time.time()
        
        result = ServiceMeshTestResult(
            test_name="service_discovery",
            test_category="discovery",
            service_name=service_name,
            mesh_type="istio",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            v1 = client.CoreV1Api()
            
            # Check if service exists
            services = v1.list_namespaced_service(namespace=self.config.namespace)
            service_found = any(svc.metadata.name == service_name for svc in services.items)
            
            if not service_found:
                result.errors.append(f"Service {service_name} not found in namespace {self.config.namespace}")
                result.status = "failed"
                result.recommendations.append("Verify service deployment and namespace")
                return result
            
            # Check service endpoints
            endpoints = v1.list_namespaced_endpoints(namespace=self.config.namespace)
            service_endpoints = [ep for ep in endpoints.items if ep.metadata.name == service_name]
            
            if not service_endpoints or not service_endpoints[0].subsets:
                result.errors.append(f"No endpoints found for service {service_name}")
                result.status = "failed"
                result.recommendations.append("Check pod readiness and service selector")
                return result
            
            # Check Istio sidecar injection
            pods = v1.list_namespaced_pod(namespace=self.config.namespace, 
                                         label_selector=f"app={service_name}")
            
            sidecar_injected = 0
            total_pods = len(pods.items)
            
            for pod in pods.items:
                containers = [c.name for c in pod.spec.containers]
                if 'istio-proxy' in containers:
                    sidecar_injected += 1
            
            sidecar_injection_rate = sidecar_injected / total_pods if total_pods > 0 else 0
            
            result.metrics = {
                'service_found': service_found,
                'endpoints_count': len(service_endpoints[0].subsets[0].addresses) if service_endpoints and service_endpoints[0].subsets else 0,
                'total_pods': total_pods,
                'sidecar_injected': sidecar_injected,
                'sidecar_injection_rate': sidecar_injection_rate
            }
            
            if sidecar_injection_rate < 1.0:
                result.status = "warning"
                result.errors.append(f"Sidecar injection incomplete: {sidecar_injection_rate:.2%}")
                result.recommendations.append("Enable automatic sidecar injection for namespace")
            else:
                result.status = "passed"
            
        except Exception as e:
            result.errors.append(f"Service discovery test failed: {str(e)}")
            result.status = "error"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def test_traffic_routing(self, service_name: str, destination_rules: List[str] = None) -> ServiceMeshTestResult:
        """Test traffic routing policies."""
        start_time = time.time()
        
        result = ServiceMeshTestResult(
            test_name="traffic_routing",
            test_category="routing",
            service_name=service_name,
            mesh_type="istio",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Check Virtual Services
            custom_api = client.CustomObjectsApi()
            
            virtual_services = custom_api.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="virtualservices"
            )
            
            service_vs = [vs for vs in virtual_services['items'] 
                         if service_name in str(vs.get('spec', {}).get('hosts', []))]
            
            # Check Destination Rules
            destination_rules = custom_api.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="destinationrules"
            )
            
            service_dr = [dr for dr in destination_rules['items']
                         if dr.get('spec', {}).get('host') == service_name]
            
            result.metrics = {
                'virtual_services_count': len(service_vs),
                'destination_rules_count': len(service_dr),
                'has_routing_config': len(service_vs) > 0 or len(service_dr) > 0
            }
            
            if len(service_vs) == 0 and len(service_dr) == 0:
                result.status = "warning"
                result.errors.append("No traffic management policies found")
                result.recommendations.append("Consider adding VirtualService and DestinationRule for traffic control")
            else:
                result.status = "passed"
            
        except Exception as e:
            result.errors.append(f"Traffic routing test failed: {str(e)}")
            result.status = "error"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def test_security_policies(self, service_name: str) -> ServiceMeshTestResult:
        """Test security policies and mTLS."""
        start_time = time.time()
        
        result = ServiceMeshTestResult(
            test_name="security_policies",
            test_category="security",
            service_name=service_name,
            mesh_type="istio",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            custom_api = client.CustomObjectsApi()
            
            # Check PeerAuthentication policies
            peer_auth = custom_api.list_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="peerauthentications"
            )
            
            # Check AuthorizationPolicy
            auth_policy = custom_api.list_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="authorizationpolicies"
            )
            
            service_auth_policies = [policy for policy in auth_policy['items']
                                   if service_name in str(policy.get('spec', {}).get('selector', {}))]
            
            # Check if mTLS is enabled
            mtls_enabled = any(
                pa.get('spec', {}).get('mtls', {}).get('mode') in ['STRICT', 'PERMISSIVE']
                for pa in peer_auth['items']
            )
            
            result.metrics = {
                'peer_auth_policies': len(peer_auth['items']),
                'authorization_policies': len(service_auth_policies),
                'mtls_enabled': mtls_enabled
            }
            
            issues = []
            if not mtls_enabled:
                issues.append("mTLS not enabled")
                result.recommendations.append("Enable mTLS for secure service communication")
            
            if len(service_auth_policies) == 0:
                issues.append("No authorization policies found")
                result.recommendations.append("Add AuthorizationPolicy for access control")
            
            if issues:
                result.status = "warning"
                result.errors.extend(issues)
            else:
                result.status = "passed"
            
        except Exception as e:
            result.errors.append(f"Security policies test failed: {str(e)}")
            result.status = "error"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result


class ConsulServiceMeshTester:
    """Consul Connect service mesh testing implementation."""
    
    def __init__(self, config -> None: ServiceMeshConfig) -> None:
        self.config = config
        self.consul_client = None
    
    async def initialize(self) -> None:
        """Initialize Consul client."""
        try:
            self.consul_client = consul.Consul()
            logger.info("Consul client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Consul client: {e}")
    
    async def test_service_discovery(self, service_name: str) -> ServiceMeshTestResult:
        """Test service discovery in Consul."""
        start_time = time.time()
        
        result = ServiceMeshTestResult(
            test_name="service_discovery",
            test_category="discovery",
            service_name=service_name,
            mesh_type="consul",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Check if service is registered
            services = self.consul_client.health.service(service_name, passing=True)
            service_instances = services[1]
            
            healthy_instances = len(service_instances)
            total_instances = len(self.consul_client.health.service(service_name, passing=False)[1])
            
            result.metrics = {
                'total_instances': total_instances,
                'healthy_instances': healthy_instances,
                'health_ratio': healthy_instances / total_instances if total_instances > 0 else 0
            }
            
            if healthy_instances == 0:
                result.status = "failed"
                result.errors.append(f"No healthy instances found for service {service_name}")
                result.recommendations.append("Check service health checks and registration")
            elif healthy_instances < total_instances:
                result.status = "warning"
                result.errors.append(f"Some instances unhealthy: {healthy_instances}/{total_instances}")
                result.recommendations.append("Investigate unhealthy service instances")
            else:
                result.status = "passed"
            
        except Exception as e:
            result.errors.append(f"Consul service discovery test failed: {str(e)}")
            result.status = "error"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def test_connect_security(self, service_name: str) -> ServiceMeshTestResult:
        """Test Consul Connect security features."""
        start_time = time.time()
        
        result = ServiceMeshTestResult(
            test_name="connect_security",
            test_category="security",
            service_name=service_name,
            mesh_type="consul",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Check if Connect is enabled for the service
            services = self.consul_client.catalog.service(service_name)
            service_data = services[1]
            
            connect_enabled = any(
                svc.get('ServiceConnect', {}).get('Native', False) or
                'connect-proxy' in svc.get('ServiceTags', [])
                for svc in service_data
            )
            
            # Check intentions (service-to-service permissions)
            try:
                intentions = self.consul_client.connect.intention.list()
                service_intentions = [
                    intent for intent in intentions
                    if intent.get('DestinationName') == service_name or intent.get('SourceName') == service_name
                ]
            except:
                service_intentions = []
            
            result.metrics = {
                'connect_enabled': connect_enabled,
                'intentions_count': len(service_intentions)
            }
            
            if not connect_enabled:
                result.status = "failed"
                result.errors.append("Consul Connect not enabled for service")
                result.recommendations.append("Enable Consul Connect for secure service communication")
            elif len(service_intentions) == 0:
                result.status = "warning"
                result.errors.append("No service intentions configured")
                result.recommendations.append("Configure service intentions for access control")
            else:
                result.status = "passed"
            
        except Exception as e:
            result.errors.append(f"Consul Connect security test failed: {str(e)}")
            result.status = "error"
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result


class ServiceMeshTester:
    """
    Enterprise Service Mesh Testing Engine
    ====================================
    
    Comprehensive service mesh communication testing.
    Demonstrates Microservices Architect + DevOps + Backend Senior expertise.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config = self._load_config(config_path)
        self.test_results: List[ServiceMeshTestResult] = []
        self.mesh_testers = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load service mesh testing configuration."""
        default_config = {
            'mesh_configs': {},
            'test_settings': {
                'timeout_seconds': 30,
                'parallel_tests': 5,
                'retry_failed_tests': True,
                'max_retries': 2
            },
            'observability': {
                'metrics_enabled': True,
                'tracing_enabled': True,
                'logging_enabled': True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def initialize_mesh_testers(self, mesh_configs -> None: List[ServiceMeshConfig]) -> None:
        """Initialize mesh-specific testers."""
        for mesh_config in mesh_configs:
            if mesh_config.mesh_type == 'istio':
                tester = IstioServiceMeshTester(mesh_config)
                await tester.initialize()
                self.mesh_testers[f"{mesh_config.mesh_type}_{mesh_config.namespace}"] = tester
            elif mesh_config.mesh_type == 'consul':
                tester = ConsulServiceMeshTester(mesh_config)
                await tester.initialize()
                self.mesh_testers[f"{mesh_config.mesh_type}_{mesh_config.namespace}"] = tester
            
            logger.info(f"Initialized {mesh_config.mesh_type} tester for namespace {mesh_config.namespace}")
    
    async def test_service_mesh_communication(self, mesh_configs: List[ServiceMeshConfig]) -> Dict[str, Any]:
        """Test service mesh communication across all configured meshes."""
        logger.info(f"Starting service mesh tests for {len(mesh_configs)} configurations")
        
        # Initialize testers
        await self.initialize_mesh_testers(mesh_configs)
        
        all_results = []
        
        for mesh_config in mesh_configs:
            tester_key = f"{mesh_config.mesh_type}_{mesh_config.namespace}"
            tester = self.mesh_testers.get(tester_key)
            
            if not tester:
                logger.error(f"No tester available for {tester_key}")
                continue
            
            logger.info(f"Testing {mesh_config.mesh_type} mesh in namespace {mesh_config.namespace}")
            
            # Test each service in the mesh
            for service_name in mesh_config.services:
                try:
                    # Service discovery test
                    discovery_result = await tester.test_service_discovery(service_name)
                    all_results.append(discovery_result)
                    
                    # Mesh-specific tests
                    if mesh_config.mesh_type == 'istio':
                        # Traffic routing test
                        routing_result = await tester.test_traffic_routing(service_name)
                        all_results.append(routing_result)
                        
                        # Security policies test
                        security_result = await tester.test_security_policies(service_name)
                        all_results.append(security_result)
                    
                    elif mesh_config.mesh_type == 'consul':
                        # Connect security test
                        connect_result = await tester.test_connect_security(service_name)
                        all_results.append(connect_result)
                    
                except Exception as e:
                    logger.error(f"Service mesh test failed for {service_name}: {e}")
                    error_result = ServiceMeshTestResult(
                        test_name="service_test_error",
                        test_category="general",
                        service_name=service_name,
                        mesh_type=mesh_config.mesh_type,
                        status="error",
                        execution_time_ms=0.0,
                        errors=[str(e)]
                    )
                    all_results.append(error_result)
        
        self.test_results = all_results
        
        # Generate comprehensive report
        return self._generate_mesh_report()
    
    def _generate_mesh_report(self) -> Dict[str, Any]:
        """Generate comprehensive service mesh test report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'passed_tests': len([r for r in self.test_results if r.status == 'passed']),
                'warning_tests': len([r for r in self.test_results if r.status == 'warning']),
                'failed_tests': len([r for r in self.test_results if r.status == 'failed']),
                'error_tests': len([r for r in self.test_results if r.status == 'error']),
                'success_rate': 0.0,
                'average_execution_time': 0.0
            },
            'mesh_results': {},
            'service_results': {},
            'category_results': {},
            'issues_summary': {},
            'recommendations': []
        }
        
        # Calculate success rate
        successful_tests = report['summary']['passed_tests'] + report['summary']['warning_tests']
        total_tests = report['summary']['total_tests']
        if total_tests > 0:
            report['summary']['success_rate'] = (successful_tests / total_tests) * 100
            report['summary']['average_execution_time'] = sum(r.execution_time_ms for r in self.test_results) / total_tests
        
        # Group results by mesh type
        for result in self.test_results:
            mesh_type = result.mesh_type
            if mesh_type not in report['mesh_results']:
                report['mesh_results'][mesh_type] = {
                    'total': 0,
                    'passed': 0,
                    'warning': 0,
                    'failed': 0,
                    'error': 0,
                    'services': set()
                }
            
            mesh_report = report['mesh_results'][mesh_type]
            mesh_report['total'] += 1
            mesh_report[result.status] += 1
            mesh_report['services'].add(result.service_name)
        
        # Convert sets to lists for JSON serialization
        for mesh_type, mesh_data in report['mesh_results'].items():
            mesh_data['services'] = list(mesh_data['services'])
            mesh_data['services_count'] = len(mesh_data['services'])
        
        # Group results by service
        for result in self.test_results:
            service_name = result.service_name
            if service_name not in report['service_results']:
                report['service_results'][service_name] = {
                    'total': 0,
                    'passed': 0,
                    'warning': 0,
                    'failed': 0,
                    'error': 0,
                    'mesh_types': set()
                }
            
            service_report = report['service_results'][service_name]
            service_report['total'] += 1
            service_report[result.status] += 1
            service_report['mesh_types'].add(result.mesh_type)
        
        # Convert sets to lists
        for service_name, service_data in report['service_results'].items():
            service_data['mesh_types'] = list(service_data['mesh_types'])
        
        # Group results by test category
        for result in self.test_results:
            category = result.test_category
            if category not in report['category_results']:
                report['category_results'][category] = {
                    'total': 0,
                    'passed': 0,
                    'warning': 0,
                    'failed': 0,
                    'error': 0
                }
            
            category_report = report['category_results'][category]
            category_report['total'] += 1
            category_report[result.status] += 1
        
        # Analyze common issues
        all_errors = []
        for result in self.test_results:
            all_errors.extend(result.errors)
        
        # Count issue types
        issue_counts = {}
        for error in all_errors:
            issue_type = error.split(':')[0] if ':' in error else error
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        report['issues_summary'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Generate recommendations
        recommendations = []
        
        if report['summary']['failed_tests'] > 0:
            recommendations.append(f"Address {report['summary']['failed_tests']} failed service mesh tests")
        
        if 'No healthy instances found' in issue_counts:
            recommendations.append("Investigate unhealthy service instances and health check configurations")
        
        if 'mTLS not enabled' in issue_counts:
            recommendations.append("Enable mTLS for secure service-to-service communication")
        
        if 'No authorization policies found' in issue_counts:
            recommendations.append("Implement authorization policies for proper access control")
        
        if 'Sidecar injection incomplete' in issue_counts:
            recommendations.append("Ensure complete sidecar injection across all services")
        
        if not recommendations:
            recommendations.append("All service mesh communication tests passed successfully")
        
        report['recommendations'] = recommendations
        
        return report
    
    async def save_report(self, report -> None: Dict[str, Any], output_path -> None: str = "service_mesh_test_report.json") -> None:
        """Save service mesh test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Service mesh test report saved to: {output_path}")


# CLI Interface
async def main() -> None:
    """Main CLI interface for service mesh testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Service Mesh Testing Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--mesh-type", choices=['istio', 'consul'], 
                       help="Service mesh type for quick test")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--services", nargs='+', help="Services to test")
    parser.add_argument("--output", default="service_mesh_test_report.json", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize tester
    tester = ServiceMeshTester(args.config)
    
    try:
        mesh_configs = []
        
        if args.mesh_type and args.services:
            # Quick test mode
            mesh_config = ServiceMeshConfig(
                mesh_type=args.mesh_type,
                namespace=args.namespace,
                services=args.services
            )
            mesh_configs.append(mesh_config)
        else:
            # Load from configuration
            for name, config_data in tester.config.get('mesh_configs', {}).items():
                mesh_config = ServiceMeshConfig(**config_data)
                mesh_configs.append(mesh_config)
        
        if not mesh_configs:
            logger.error("No mesh configurations found")
            return
        
        # Run tests
        report = await tester.test_service_mesh_communication(mesh_configs)
        
        # Save report
        await tester.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🕸️ Service Mesh Test Results")
        print(f"{'='*50}")
        print(f"Tests Executed: {summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Warnings: {summary['warning_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Errors: {summary['error_tests']}")
        print(f"Average Execution Time: {summary['average_execution_time']:.2f}ms")
        
        if summary['success_rate'] < 100:
            print(f"\n🚨 Issues Summary:")
            for issue, count in list(report['issues_summary'].items())[:3]:
                print(f"  - {issue}: {count} occurrences")
            
            print(f"\n💡 Top Recommendations:")
            for rec in report['recommendations'][:3]:
                print(f"  - {rec}")
        else:
            print(f"\n✅ All service mesh tests passed!")
    
    except Exception as e:
        logger.error(f"Service mesh testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())