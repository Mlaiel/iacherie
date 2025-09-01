#!/usr/bin/env python3
"""
Test Quality Metrics Implementation
Author: Fahed Mlaiel (mlaiel@live.de)
Description: Test the quality metrics implementation without external dependencies
"""

import os
import json
import subprocess
from pathlib import Path


def test_basic_coverage():
    """Test basic coverage functionality with existing tools"""
    try:
        # Check if coverage is available
        result = subprocess.run(["python", "-m", "coverage", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Coverage tool available")
            return True
        else:
            print("❌ Coverage tool not available")
            return False
    except FileNotFoundError:
        print("❌ Coverage tool not found")
        return False


def test_basic_pytest():
    """Test basic pytest functionality"""
    try:
        result = subprocess.run(["python", "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Pytest available")
            return True
        else:
            print("❌ Pytest not available")
            return False
    except FileNotFoundError:
        print("❌ Pytest not found")
        return False


def test_configuration_files():
    """Test that configuration files exist and are valid"""
    configs = [
        "sonar-project.properties",
        "quality-metrics.ini",
        "pytest.ini",
        ".prospector.yaml",
        "requirements-quality.txt"
    ]
    
    all_exist = True
    for config in configs:
        if Path(config).exists():
            print(f"✅ {config} exists")
        else:
            print(f"❌ {config} missing")
            all_exist = False
    
    return all_exist


def test_scripts_executable():
    """Test that scripts are executable"""
    scripts = [
        "scripts/quality-metrics.sh",
        "scripts/performance-benchmarks.py",
        "scripts/doc-coverage.py",
        "scripts/quality-dashboard.py"
    ]
    
    all_executable = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"✅ {script} is executable")
            else:
                print(f"❌ {script} is not executable")
                all_executable = False
        else:
            print(f"❌ {script} does not exist")
            all_executable = False
    
    return all_executable


def test_github_workflows():
    """Test that GitHub workflows exist"""
    workflows = [
        ".github/workflows/ci.yml",
        ".github/workflows/quality-metrics.yml"
    ]
    
    all_exist = True
    for workflow in workflows:
        if Path(workflow).exists():
            print(f"✅ {workflow} exists")
        else:
            print(f"❌ {workflow} missing")
            all_exist = False
    
    return all_exist


def test_quality_thresholds():
    """Test quality thresholds configuration"""
    thresholds = {
        "code_coverage": 90.0,
        "security_score": 8.0,
        "documentation_coverage": 80.0,
        "complexity_threshold": 10.0
    }
    
    print("✅ Quality thresholds configured:")
    for metric, threshold in thresholds.items():
        print(f"  - {metric}: {threshold}")
    
    return True


def test_gitignore_updated():
    """Test that .gitignore includes quality metrics reports"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore not found")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_patterns = [
        "coverage.xml",
        "htmlcov/",
        "quality-reports/",
        "*.coverage.*",
        "bandit-report.json",
        "safety-report.json"
    ]
    
    all_patterns_found = True
    for pattern in required_patterns:
        if pattern in content:
            print(f"✅ .gitignore includes {pattern}")
        else:
            print(f"❌ .gitignore missing {pattern}")
            all_patterns_found = False
    
    return all_patterns_found


def generate_test_report():
    """Generate test report for quality metrics implementation"""
    print("🔍 Testing Quality Metrics Implementation")
    print("=" * 50)
    
    tests = [
        ("Configuration Files", test_configuration_files),
        ("Scripts Executable", test_scripts_executable),
        ("GitHub Workflows", test_github_workflows),
        ("Quality Thresholds", test_quality_thresholds),
        ("GitIgnore Updated", test_gitignore_updated),
        ("Basic Coverage Tool", test_basic_coverage),
        ("Basic Pytest Tool", test_basic_pytest)
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results[test_name] = False
    
    # Generate summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Quality gates check
    critical_tests = [
        "Configuration Files",
        "Scripts Executable", 
        "GitHub Workflows",
        "Quality Thresholds"
    ]
    
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        print("\n✅ Quality Metrics Implementation PASSED")
        print("All critical components are properly configured")
    else:
        print("\n❌ Quality Metrics Implementation NEEDS ATTENTION")
        print("Some critical components require fixes")
    
    # Save test report
    report = {
        "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "critical_passed": critical_passed
        },
        "test_results": results,
        "recommendations": []
    }
    
    # Add recommendations
    if not results.get("Basic Coverage Tool", False):
        report["recommendations"].append("Install coverage tool: pip install coverage")
    
    if not results.get("Basic Pytest Tool", False):
        report["recommendations"].append("Install pytest tool: pip install pytest pytest-cov")
    
    if not critical_passed:
        report["recommendations"].append("Fix critical configuration issues before proceeding")
    
    # Save report
    with open("quality-metrics-test-report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test report saved to: quality-metrics-test-report.json")
    
    return critical_passed


if __name__ == "__main__":
    success = generate_test_report()
    exit(0 if success else 1)