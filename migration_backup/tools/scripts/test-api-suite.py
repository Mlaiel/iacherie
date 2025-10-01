#!/usr/bin/env python3
"""
🧪 ENTERPRISE API TESTING SUITE - QA + DevOps Implementation
Suite de tests pour vérifier toutes les APIs enterprise
Author: Fahed Mlaiel - Multi-Expert Testing Approach
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any
from dataclasses import dataclass
import argparse

@dataclass
class TestResult:
    """Résultat d'un test API"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error_message: str = ""
    response_data: Dict[str, Any] = None

class EnterpriseAPITester:
    """
    🧪 Enterprise API Testing Suite
    Tests automatisés pour l'architecture IA Chéries
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
        # Configuration des endpoints à tester
        self.api_endpoints = {
            # AI Services API
            "ai_services_agents": {
                "url": "/api/ai-services/agents",
                "method": "GET",
                "expected_status": 200,
                "timeout": 10,
                "critical": True
            },
            "ai_services_inference": {
                "url": "/api/ai-services/agents",
                "method": "POST",
                "payload": {
                    "agent": "content_creator",
                    "task": "generate",
                    "parameters": {
                        "prompt": "Test content generation",
                        "format": "text",
                        "length": "short"
                    }
                },
                "expected_status": 200,
                "timeout": 15,
                "critical": True
            },
            
            # Audio Processing API
            "audio_projects": {
                "url": "/api/audio/generate",
                "method": "GET", 
                "expected_status": 200,
                "timeout": 5,
                "critical": True
            },
            "audio_generation": {
                "url": "/api/audio/generate",
                "method": "POST",
                "payload": {
                    "prompt": "Ambient techno track for testing",
                    "style": "electronic",
                    "duration": 30,
                    "quality": "high",
                    "format": "mp3"
                },
                "expected_status": 200,
                "timeout": 20,
                "critical": True
            },
            
            # Security API
            "security_alerts": {
                "url": "/api/security/alerts",
                "method": "GET",
                "expected_status": 200,
                "timeout": 5,
                "critical": True
            },
            "security_incident": {
                "url": "/api/security/alerts",
                "method": "POST",
                "payload": {
                    "title": "Test Security Incident",
                    "description": "Automated test incident for API validation",
                    "severity": "low",
                    "affectedSystems": ["api-testing"]
                },
                "expected_status": 200,
                "timeout": 10,
                "critical": True
            },
            
            # Monitoring API
            "monitoring_metrics": {
                "url": "/api/monitoring",
                "method": "GET",
                "expected_status": 200,
                "timeout": 5,
                "critical": True
            },
            "monitoring_webhook": {
                "url": "/api/monitoring",
                "method": "POST",
                "payload": {
                    "type": "alert",
                    "message": "Test monitoring alert",
                    "severity": "info",
                    "source": "api-testing"
                },
                "expected_status": 200,
                "timeout": 5,
                "critical": False
            }
        }

    async def test_endpoint(self, session: aiohttp.ClientSession, 
                           name: str, config: Dict[str, Any]) -> TestResult:
        """Teste un endpoint API spécifique"""
        url = f"{self.base_url}{config['url']}"
        method = config['method']
        
        print(f"🧪 Testing {method} {config['url']}")
        
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.get('timeout', 10))
            
            if method == 'GET':
                async with session.get(url, timeout=timeout) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    
                    success = response.status == config.get('expected_status', 200)
                    
                    return TestResult(
                        endpoint=config['url'],
                        method=method,
                        status_code=response.status,
                        response_time_ms=response_time,
                        success=success,
                        response_data=data
                    )
                    
            elif method == 'POST':
                payload = config.get('payload', {})
                async with session.post(url, json=payload, timeout=timeout) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    
                    success = response.status == config.get('expected_status', 200)
                    
                    return TestResult(
                        endpoint=config['url'],
                        method=method,
                        status_code=response.status,
                        response_time_ms=response_time,
                        success=success,
                        response_data=data
                    )
                    
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                endpoint=config['url'],
                method=method,
                status_code=0,
                response_time_ms=response_time,
                success=False,
                error_message="Timeout"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                endpoint=config['url'],
                method=method,
                status_code=0,
                response_time_ms=response_time,
                success=False,
                error_message=str(e)
            )

    async def run_all_tests(self):
        """Exécute tous les tests API"""
        print("🚀 Starting Enterprise API Test Suite")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔍 Testing {len(self.api_endpoints)} endpoints")
        print("="*60)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for name, config in self.api_endpoints.items():
                task = self.test_endpoint(session, name, config)
                tasks.append((name, task))
            
            # Exécution des tests
            for name, task in tasks:
                try:
                    result = await task
                    self.results.append(result)
                    
                    status_icon = "✅" if result.success else "❌"
                    critical_icon = "🔴" if self.api_endpoints[name].get('critical', False) else "🟡"
                    
                    print(f"{status_icon} {critical_icon} {result.method} {result.endpoint}")
                    print(f"   Status: {result.status_code} | Time: {result.response_time_ms:.1f}ms")
                    
                    if not result.success and result.error_message:
                        print(f"   Error: {result.error_message}")
                    
                    if result.response_data and 'data' in result.response_data:
                        if isinstance(result.response_data['data'], dict):
                            print(f"   Response: {list(result.response_data['data'].keys())[:3]}...")
                        elif isinstance(result.response_data['data'], list):
                            print(f"   Response: {len(result.response_data['data'])} items")
                    
                    print()
                    
                except Exception as e:
                    print(f"❌ Error testing {name}: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport de test détaillé"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Calculs des métriques
        avg_response_time = sum(r.response_time_ms for r in self.results) / total_tests
        max_response_time = max(r.response_time_ms for r in self.results)
        min_response_time = min(r.response_time_ms for r in self.results)
        
        # Tests critiques
        critical_endpoints = [name for name, config in self.api_endpoints.items() 
                             if config.get('critical', False)]
        critical_results = [r for r in self.results 
                           if any(r.endpoint == self.api_endpoints[name]['url'] 
                                 for name in critical_endpoints)]
        critical_failures = [r for r in critical_results if not r.success]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests) * 100,
                "critical_endpoints": len(critical_endpoints),
                "critical_failures": len(critical_failures)
            },
            "performance": {
                "average_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2)
            },
            "detailed_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status_code": r.status_code,
                    "response_time_ms": round(r.response_time_ms, 2),
                    "success": r.success,
                    "error_message": r.error_message,
                    "critical": any(r.endpoint == self.api_endpoints[name]['url'] 
                                   for name in self.api_endpoints 
                                   if self.api_endpoints[name].get('critical', False))
                } for r in self.results
            ],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "base_url": self.base_url
        }
        
        return report

    def print_summary_report(self):
        """Affiche un résumé des tests"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 ENTERPRISE API TEST SUMMARY REPORT")
        print("="*60)
        
        summary = report['summary']
        performance = report['performance']
        
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Successful Tests: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"❌ Failed Tests: {summary['failed_tests']}")
        print(f"🔴 Critical Failures: {summary['critical_failures']}/{summary['critical_endpoints']}")
        print()
        
        print(f"⏱️  Average Response Time: {performance['average_response_time_ms']}ms")
        print(f"🚀 Fastest Response: {performance['min_response_time_ms']}ms") 
        print(f"🐌 Slowest Response: {performance['max_response_time_ms']}ms")
        print()
        
        # Détail des échecs
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print("🚨 FAILED TESTS:")
            for result in failed_results:
                critical_mark = "🔴" if any(
                    result.endpoint == self.api_endpoints[name]['url'] 
                    for name in self.api_endpoints 
                    if self.api_endpoints[name].get('critical', False)
                ) else "🟡"
                print(f"   {critical_mark} {result.method} {result.endpoint}")
                print(f"      Status: {result.status_code} | Error: {result.error_message}")
        
        print("\n" + "="*60)

    def save_report_json(self, filename: str = "api_test_report.json"):
        """Sauvegarde le rapport en JSON"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {filename}")

async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Enterprise API Test Suite')
    parser.add_argument('--url', default='http://localhost:3000', 
                       help='Base URL for API testing (default: http://localhost:3000)')
    parser.add_argument('--save-report', action='store_true',
                       help='Save detailed report to JSON file')
    
    args = parser.parse_args()
    
    tester = EnterpriseAPITester(base_url=args.url)
    
    try:
        await tester.run_all_tests()
        tester.print_summary_report()
        
        if args.save_report:
            tester.save_report_json()
            
        # Exit code basé sur les résultats
        report = tester.generate_report()
        if report['summary']['critical_failures'] > 0:
            print("\n🚨 Critical API failures detected!")
            sys.exit(1)
        elif report['summary']['failed_tests'] > 0:
            print("\n⚠️  Some API tests failed (non-critical)")
            sys.exit(2)
        else:
            print("\n🎉 All API tests passed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n💥 Fatal error during testing: {e}")
        sys.exit(4)

if __name__ == "__main__":
    asyncio.run(main())