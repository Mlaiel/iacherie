"""
Docker Testing Infrastructure - Main Interface

Enterprise-grade testing orchestration for Ainflue Platform.
Coordinates all testing services for 80+ containerized services.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import docker
import subprocess
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestType(Enum):
    """Test types supported by the infrastructure"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    LOAD = "load"
    STRESS = "stress"
    SECURITY = "security"
    SMOKE = "smoke"
    REGRESSION = "regression"
    E2E = "e2e"
    CHAOS = "chaos"

@dataclass
class TestResult:
    """Test execution result"""
    test_type: TestType
    service_name: str
    status: str
    duration: float
    coverage: float
    details: Dict[str, Any]
    errors: List[str]

class DockerTestOrchestrator:
    """Main orchestrator for Docker testing infrastructure"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.test_results: List[TestResult] = []
        
    async def run_comprehensive_tests(self, services: List[str] = None) -> Dict[str, Any]:
        """
        Run comprehensive test suite across all services
        
        Args:
            services: List of services to test (if None, test all)
            
        Returns:
            Dict containing test results and metrics
        """
        if services is None:
            services = self._discover_services()
            
        logger.info(f"🧪 Starting comprehensive test suite for {len(services)} services")
        
        # Execute all test types
        results = {}
        for test_type in TestType:
            logger.info(f"Running {test_type.value} tests...")
            test_results = await self._run_test_type(test_type, services)
            results[test_type.value] = test_results
            
        # Generate summary report
        summary = self._generate_test_summary(results)
        
        logger.info(f"✅ Test suite completed. Success rate: {summary['success_rate']}%")
        return {
            'results': results,
            'summary': summary,
            'services_tested': len(services),
            'total_tests': summary['total_tests']
        }
    
    async def _run_test_type(self, test_type: TestType, services: List[str]) -> List[TestResult]:
        """Run specific test type across services"""
        results = []
        
        for service in services:
            try:
                result = await self._execute_service_test(service, test_type)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Test failed for {service}: {e}")
                results.append(TestResult(
                    test_type=test_type,
                    service_name=service,
                    status="failed",
                    duration=0,
                    coverage=0,
                    details={},
                    errors=[str(e)]
                ))
                
        return results
    
    async def _execute_service_test(self, service: str, test_type: TestType) -> TestResult:
        """Execute test for specific service"""
        start_time = asyncio.get_event_loop().time()
        
        # Build test container
        container_name = f"ainflue-{service}-{test_type.value}-tester"
        
        try:
            # Run test container
            container = self.docker_client.containers.run(
                f"ainflue/testing:{test_type.value}",
                command=f"pytest tests/{service} --cov --json-report",
                environment={
                    'SERVICE_NAME': service,
                    'TEST_TYPE': test_type.value
                },
                name=container_name,
                detach=True,
                remove=True
            )
            
            # Wait for completion
            result = container.wait()
            logs = container.logs().decode('utf-8')
            
            duration = asyncio.get_event_loop().time() - start_time
            
            # Parse results
            coverage = self._extract_coverage(logs)
            errors = self._extract_errors(logs)
            
            return TestResult(
                test_type=test_type,
                service_name=service,
                status="passed" if result['StatusCode'] == 0 else "failed",
                duration=duration,
                coverage=coverage,
                details={'logs': logs},
                errors=errors
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return TestResult(
                test_type=test_type,
                service_name=service,
                status="error",
                duration=duration,
                coverage=0,
                details={},
                errors=[str(e)]
            )
    
    def _discover_services(self) -> List[str]:
        """Discover all containerized services"""
        services = [
            # Audio services
            'audio_processing', 'codec_optimization', 'mastering_engine',
            'source_separation', 'spectrum_analyzer', 'waveform_generator',
            
            # Protection services  
            'fingerprinting_engine', 'watermarking_service', 'copyright_monitor',
            'blockchain_verifier', 'content_scanner', 'drm_controller',
            
            # Monetization services
            'payment_processor', 'revenue_analytics', 'subscription_manager',
            'licensing_engine', 'royalty_calculator', 'invoice_generator',
            
            # Collaboration services
            'collaboration_matcher', 'project_orchestrator', 'workflow_manager',
            'communication_hub', 'skill_analyzer', 'compatibility_engine',
            
            # Gamification services
            'challenge_engine', 'reward_system', 'leaderboard_manager',
            'achievement_tracker', 'social_features', 'tournament_organizer',
            
            # SEO services
            'platform_optimizer', 'keyword_intelligence', 'trending_analyzer',
            'metadata_enhancer', 'hashtag_generator', 'content_scheduler',
            
            # Distribution services
            'platform_connectors', 'publication_scheduler', 'format_adapter',
            'analytics_aggregator', 'hashtag_optimizer', 'ab_testing_engine',
            
            # AI services
            'ml_inference_engine', 'content_generation', 'music_remix_engine',
            'style_transfer', 'content_enhancer', 'creative_assistant',
            
            # Security services
            'vulnerability_scanner', 'threat_detector', 'access_controller',
            'audit_logger', 'encryption_manager', 'identity_verifier',
            
            # Monitoring services
            'prometheus_collector', 'grafana_dashboard', 'alertmanager',
            'jaeger_tracing', 'elk_stack', 'health_checker',
            
            # Creator services
            'musician_tools', 'photographer_tools', 'blogger_tools',
            'influencer_tools', 'comedian_tools', 'creator_profiler'
        ]
        
        return services
    
    def _extract_coverage(self, logs: str) -> float:
        """Extract coverage percentage from test logs"""
        try:
            # Look for coverage report in logs
            for line in logs.split('\n'):
                if 'TOTAL' in line and '%' in line:
                    parts = line.split()
                    for part in parts:
                        if '%' in part:
                            return float(part.replace('%', ''))
            return 0.0
        except:
            return 0.0
    
    def _extract_errors(self, logs: str) -> List[str]:
        """Extract error messages from test logs"""
        errors = []
        for line in logs.split('\n'):
            if 'ERROR' in line or 'FAILED' in line:
                errors.append(line.strip())
        return errors
    
    def _generate_test_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_tests = 0
        passed_tests = 0
        total_coverage = 0
        coverage_count = 0
        
        for test_type, test_results in results.items():
            for result in test_results:
                total_tests += 1
                if result.status == "passed":
                    passed_tests += 1
                if result.coverage > 0:
                    total_coverage += result.coverage
                    coverage_count += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_coverage = (total_coverage / coverage_count) if coverage_count > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round(success_rate, 2),
            'average_coverage': round(avg_coverage, 2),
            'meets_coverage_requirement': avg_coverage >= 95.0
        }

# Main execution
async def main():
    """Main testing orchestrator entry point"""
    orchestrator = DockerTestOrchestrator()
    
    try:
        results = await orchestrator.run_comprehensive_tests()
        
        print("🧪 COMPREHENSIVE DOCKER TEST SUITE RESULTS:")
        print(f"Total Test Suites: {len(results['results'])}")
        print(f"✅ Success Rate: {results['summary']['success_rate']}%")
        print(f"📈 Average Coverage: {results['summary']['average_coverage']}%")
        print(f"🎯 Meets 95% Coverage: {'✅' if results['summary']['meets_coverage_requirement'] else '❌'}")
        
        # Save detailed results
        with open('/tmp/test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        logger.info("📊 Detailed results saved to /tmp/test_results.json")
        
    except Exception as e:
        logger.error(f"❌ Test orchestration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())