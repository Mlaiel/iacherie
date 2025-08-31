#!/usr/bin/env python3
"""Comprehensive Test Runner for Ainflue Platform.

Runs all integration tests and performance tests to validate
API endpoints and system performance characteristics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        end_time = time.time()
        
        print(f"Duration: {end_time - start_time:.2f}s")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr and result.returncode != 0:
            print(f"\nSTDERR:\n{result.stderr}")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 Ainflue Platform - Comprehensive Test Suite")
    print("=" * 60)
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Test commands
    tests = [
        {
            "cmd": "python -m pytest tests/integration/api_endpoints/test_api_integration.py -v -m integration",
            "description": "API Integration Tests",
            "required": True
        },
        {
            "cmd": "python -m pytest tests/performance/test_load_stress.py::TestAPILoadTesting -v",
            "description": "API Load & Performance Tests",
            "required": True
        },
        {
            "cmd": "python -m pytest tests/performance/test_load_stress.py::TestStressTestingEnhanced -v",
            "description": "Enhanced Stress Tests",
            "required": False
        },
        {
            "cmd": "python -m pytest tests/performance/test_load_stress.py::TestSimulatedPerformance -v",
            "description": "Simulated Performance Tests",
            "required": False
        },
        {
            "cmd": "python -m pytest tests/integration/api_endpoints/test_api_integration.py::TestPerformanceIntegration -v",
            "description": "Integration Performance Tests",
            "required": True
        }
    ]
    
    results = []
    
    for test in tests:
        success = run_command(test["cmd"], test["description"])
        results.append({
            "description": test["description"],
            "success": success,
            "required": test["required"]
        })
        
        if not success and test["required"]:
            print(f"\n❌ CRITICAL: Required test failed: {test['description']}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    required_failed = sum(1 for r in results if not r["success"] and r["required"])
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Required failures: {required_failed}")
    
    print(f"\nDetailed results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        required = "(REQUIRED)" if result["required"] else "(OPTIONAL)"
        print(f"  {status} {result['description']} {required}")
    
    # Overall result
    if required_failed == 0:
        print(f"\n🎉 SUCCESS: All required tests passed!")
        print("✅ API Integration Tests: READY")
        print("✅ Performance & Load Tests: READY")
        return 0
    else:
        print(f"\n💥 FAILURE: {required_failed} required test(s) failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)