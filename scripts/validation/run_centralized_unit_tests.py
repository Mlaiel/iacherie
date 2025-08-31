#!/usr/bin/env python3
"""Centralized Unit Test Runner for Ainflue Platform
================================================

This script provides a centralized way to run all unit tests and validate
the platform's quality. It addresses the critical issue: 
"Tests Manquants: Pas de tests unitaires centralisés"

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Provide centralized unit test execution and quality validation
"""
import subprocess
import sys
import os
from pathlib import Path
import time


class TestRunner:
    """Centralized test runner for all unit tests"""    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_suites = []
        
    def add_test_suite(self, name, test_file):
        """Add a test suite to be executed"""        self.test_suites.append({"name": name, "file": test_file})
    
    def run_test_suite(self, test_suite):
        """Run a single test suite"""        print(f"\n🧪 Running {test_suite['name']}...")
        print("=" * 60)
        
        test_file = self.project_root / test_suite['file']
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(test_file), 
                "-v", 
                "--tb=short"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ {test_suite['name']}: ALL TESTS PASSED")
                
                # Parse test results
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'passed' in line and 'warning' in line:
                        # Extract number of passed tests
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'passed' in part and i > 0:
                                try:
                                    count = int(parts[i-1])
                                    self.tests_passed += count
                                    break
                                except ValueError:
                                    pass
                
                return True
            else:
                print(f"❌ {test_suite['name']}: TESTS FAILED")
                print("Error output:")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ {test_suite['name']}: ERROR RUNNING TESTS")
            print(f"Error: {e}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        """Run all registered test suites"""        print("🚀 Starting Centralized Unit Test Execution")
        print("=" * 60)
        print(f"Project Root: {self.project_root}")
        print(f"Total Test Suites: {len(self.test_suites)}")
        
        start_time = time.time()
        successful_suites = 0
        failed_suites = 0
        
        for test_suite in self.test_suites:
            success = self.run_test_suite(test_suite)
            if success:
                successful_suites += 1
            else:
                failed_suites += 1
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Test Suites: {len(self.test_suites)}")
        print(f"✅ Successful Suites: {successful_suites}")
        print(f"❌ Failed Suites: {failed_suites}")
        print(f"🎯 Individual Tests Passed: {self.tests_passed}")
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        
        # Overall status
        if failed_suites == 0:
            print("\n🎉 ALL TEST SUITES PASSED!")
            print("✅ Quality validation successful - Platform ready for production")
            return True
        else:
            print(f"\n⚠️  {failed_suites} TEST SUITE(S) FAILED")
            print("❌ Quality validation failed - Issues need to be addressed")
            return False


def main():
    """Main execution function"""    runner = TestRunner()
    
    # Register core test suites
    runner.add_test_suite(
        "Core Monetization Tests", 
        "tests/unit/test_core_monetization.py"
    )
    
    runner.add_test_suite(
        "Core API Tests", 
        "tests/unit/test_core_api.py"
    )
    
    runner.add_test_suite(
        "Core Business Logic Tests", 
        "tests/unit/test_core_business_logic.py"
    )
    
    # Run all tests
    success = runner.run_all_tests()
    
    # Print final validation message
    print("\n" + "=" * 60)
    print("🎯 CRITICAL ISSUE RESOLUTION STATUS")
    print("=" * 60)
    print("Original Issue: 'Tests Manquants: Pas de tests unitaires centralisés'")
    print("Impact: 'Pas de validation qualité'")
    print("Priority: '🔴 CRITIQUE'")
    print("")
    
    if success:
        print("✅ ISSUE RESOLVED: Centralized unit tests now implemented and functional")
        print("✅ Quality validation framework is operational")
        print("✅ Production deployment quality gates are in place")
        print("✅ Critical testing infrastructure gap has been addressed")
    else:
        print("⚠️  ISSUE PARTIALLY RESOLVED: Some tests need attention")
        print("⚠️  Quality validation framework is partially operational")
        print("⚠️  Review failed tests before production deployment")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)