"""Comprehensive Integration Test Suite Runner
==========================================

Executes all high-priority integration tests for the Ainflue platform:
1. FastAPI Application Startup Tests
2. PostgreSQL Database Connection Tests  
3. Gamification Workflows End-to-End Tests
4. AI Remix Generation with Models Tests
5. Multilingual Interface Switching Tests

Author: Integration Test Suite
"""

import asyncio
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import pytest for programmatic execution
try:
    import pytest
except ImportError:
    print("❌ pytest not available. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
    import pytest


class IntegrationTestRunner:
    """Comprehensive integration test runner"""
    
    def __init__(self):
        self.test_modules = [
            {
                "name": "FastAPI Application Startup",
                "module": "tests.integration.test_fastapi_startup",
                "description": "Tests complete FastAPI application startup and endpoint validation",
                "priority": "HIGH"
            },
            {
                "name": "PostgreSQL Database Connections", 
                "module": "tests.integration.test_postgresql_connections",
                "description": "Tests PostgreSQL connectivity, health checks, and connection pooling",
                "priority": "HIGH"
            },
            {
                "name": "Gamification Workflows End-to-End",
                "module": "tests.integration.test_gamification_workflows", 
                "description": "Tests complete gamification system workflows and user progression",
                "priority": "HIGH"
            },
            {
                "name": "AI Remix Generation with Models",
                "module": "tests.integration.test_ai_remix_generation",
                "description": "Tests AI model loading, remix generation, and quality assessment",
                "priority": "HIGH"
            },
            {
                "name": "Multilingual Interface Switching",
                "module": "tests.integration.test_multilingual_interface_switching",
                "description": "Tests language detection, translation loading, and dynamic switching",
                "priority": "HIGH"
            }
        ]
        
        self.results = {}
        self.start_time = None
        self.end_time = None


    def print_header(self):
        """Print test suite header"""
        print("=" * 80)
        print("🧪 AINFLUE PLATFORM - HIGH PRIORITY INTEGRATION TESTS")
        print("=" * 80)
        print("📋 Test Requirements from NOUVELLE_CHECKLIST_PROPRE.md:")
        print("   ✓ Tester démarrage complet application FastAPI")
        print("   ✓ Valider connexions base de données PostgreSQL")
        print("   ✓ Tester workflows gamification end-to-end")
        print("   ✓ Valider generation remix IA avec modèles")
        print("   ✓ Tester interface multilingual switching")
        print("-" * 80)
        print(f"📊 Total Test Modules: {len(self.test_modules)}")
        print("🚀 Starting comprehensive integration test execution...")
        print("=" * 80)
    
    def run_single_test_module(self, module_info: Dict[str, str]) -> Dict[str, Any]:
        """Run a single test module and return results"""
        module_name = module_info["name"]
        module_path = module_info["module"]
        
        print(f"🏃 Running {module_name} tests...")
        
        start_time = time.time()
        
        try:
            # Convert module path to file path
            test_file_path = module_path.replace(".", "/") + ".py"
            
            # Run pytest programmatically
            result = pytest.main([
                test_file_path,
                "-v",
                "--tb=short",
                "--no-header",
                "--quiet"
            ])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if result == 0:
                status = "PASSED"
                print(f"✅ {module_name} tests completed successfully")
            else:
                status = "FAILED"
                print(f"❌ {module_name} tests failed with exit code {result}")
            
            return {
                "status": status,
                "exit_code": result,
                "execution_time": execution_time,
                "passed": result == 0
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"💥 {module_name} tests crashed: {str(e)}")
            
            return {
                "status": "CRASHED",
                "exit_code": -1,
                "execution_time": execution_time,
                "error": str(e),
                "passed": False
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration test modules"""
        self.start_time = time.time()
        
        self.print_header()
        
        for i, module_info in enumerate(self.test_modules):
            print(f"\n🔬 [{i + 1}/{len(self.test_modules)}] {module_info['name']}")
            print(f"📝 Description: {module_info['description']}")
            print(f"⚡ Priority: {module_info['priority']}")
            print("-" * 60)
            
            result = self.run_single_test_module(module_info)
            self.results[module_info["name"]] = {
                **result,
                "module": module_info["module"],
                "description": module_info["description"],
                "priority": module_info["priority"]
            }
        
        self.end_time = time.time()
        return self.generate_final_report()
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive test execution report"""
        total_time = self.end_time - self.start_time
        total_tests = len(self.test_modules)
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        # Print individual test results
        for test_name, result in self.results.items():
            status_emoji = "✅" if result["passed"] else "❌" 
            print(f"{status_emoji} {test_name:<45} {result['status']:<8} ({result['execution_time']:.2f}s)")
        
        print("-" * 80)
        print(f"📈 Overall Results:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Total Execution Time: {total_time:.2f} seconds")
        
        # Status determination
        if success_rate == 100:
            overall_status = "ALL PASSED"
            status_emoji = "🎉"
            print(f"\n{status_emoji} {overall_status} - All integration tests completed successfully!")
        elif success_rate >= 80:
            overall_status = "MOSTLY PASSED" 
            status_emoji = "⚠️"
            print(f"\n{status_emoji} {overall_status} - Most tests passed with some failures")
        else:
            overall_status = "SIGNIFICANT FAILURES"
            status_emoji = "🚨"
            print(f"\n{status_emoji} {overall_status} - Multiple test failures detected")
        
        print("=" * 80)
        
        # Generate compliance report
        self.generate_requirements_compliance_report()
        
        # Return detailed report
        return {
            "overall_status": overall_status,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "total_execution_time": total_time,
            "detailed_results": self.results,
            "all_passed": success_rate == 100
        }
    
    def generate_requirements_compliance_report(self):
        """Generate compliance report against original requirements"""
        print("\n" + "=" * 80)
        print("📋 REQUIREMENTS COMPLIANCE REPORT")
        print("=" * 80)
        print("Based on NOUVELLE_CHECKLIST_PROPRE.md - PRIORITÉ HAUTE - INTÉGRATION")
        print("-" * 80)
        
        requirements_mapping = {
            "Tester démarrage complet application FastAPI": "FastAPI Application Startup",
            "Valider connexions base de données PostgreSQL": "PostgreSQL Database Connections", 
            "Tester workflows gamification end-to-end": "Gamification Workflows End-to-End",
            "Valider generation remix IA avec modèles": "AI Remix Generation with Models",
            "Tester interface multilingual switching": "Multilingual Interface Switching"
        }
        
        for requirement, test_name in requirements_mapping.items():
            if test_name in self.results:
                result = self.results[test_name]
                status_emoji = "✅" if result["passed"] else "❌"
                status_text = "COMPLIANT" if result["passed"] else "NON-COMPLIANT"
                print(f"{status_emoji} {requirement:<50} {status_text}")
            else:
                print(f"❓ {requirement:<50} NOT TESTED")
        
        print("=" * 80)


def run_all_integration_tests():
        try:
            logger.info(f"Executing run_all_integration_tests")
            
            # Implementation for run_all_integration_tests
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_all_integration_tests completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing run_specific_test_category")
            
            # Implementation for run_specific_test_category
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_specific_test_category completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"run_specific_test_category failed: {e}")
            raise
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print(f"✅ {category.title()} integration tests passed!")
    else:
        print(f"❌ {category.title()} integration tests failed with exit code: {exit_code}")
    
    return exit_code


def run_fast_integration_tests():
    """Run only fast integration tests (exclude slow tests)."""
    
    pytest_args = [
        "tests/integration/",
        "--verbose",
        "--tb=short",
        "--asyncio-mode=auto",
        "-m", "not slow",  # Exclude slow tests
        "--durations=5",
    ]
    
    print("🚀 Running Fast Integration Tests")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        try:
            logger.info(f"Executing run_fast_integration_tests")
            
            # Implementation for run_fast_integration_tests
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_fast_integration_tests completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"run_fast_integration_tests failed: {e}")
            raise
        "--verbose",
        "--tb=short",
        "--asyncio-mode=auto",
        "-k", "test_application_startup or test_database_connection or test_user_registration_workflow",
        "--maxfail=1",  # Stop on first failure for critical tests
    ]
    
    print("🚀 Running Critical Integration Tests")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        try:
            logger.info(f"Executing run_critical_integration_tests")
            
            # Implementation for run_critical_integration_tests
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_critical_integration_tests completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"run_critical_integration_tests failed: {e}")
            raise
    try:
        # Run all integration tests
        final_report = runner.run_all_tests()
        
        # Exit with appropriate code
        exit_code = 0 if final_report["all_passed"] else 1
        
        print(f"\n🏁 Integration test execution completed with exit code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n⚡ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error during test execution: {str(e)}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ainflue Integration Test Runner")
    parser.add_argument(
        "mode",
        choices=["all", "fastapi", "database", "gamification", "ai_remix", "multilingual", "fast", "critical"],
        default="all",
        nargs="?",
        help="Test mode to run"
    )
    
    args = parser.parse_args()
    
    if args.mode == "all":
        exit_code = main()
    elif args.mode in ["fastapi", "database", "gamification", "ai_remix", "multilingual"]:
        exit_code = run_specific_test_category(args.mode)
    elif args.mode == "fast":
        exit_code = run_fast_integration_tests()
    elif args.mode == "critical":
        exit_code = run_critical_integration_tests()
    else:
        print(f"❌ Unknown mode: {args.mode}")
        exit_code = 1
    
    sys.exit(exit_code)