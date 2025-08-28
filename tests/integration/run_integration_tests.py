"""
Integration Test Runner

Centralized test runner for all integration tests with proper
configuration, fixtures, and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_integration_tests():
    """Run all integration tests with proper configuration."""
    
    # Configure pytest arguments
    pytest_args = [
        # Test discovery
        "tests/integration/",
        
        # Test execution
        "--verbose",
        "--tb=short",
        "--asyncio-mode=auto",
        
        # Test filtering
        "--maxfail=5",  # Stop after 5 failures
        "-m", "integration",  # Only run integration tests
        
        # Output configuration
        "--color=yes",
        "--durations=10",  # Show 10 slowest tests
        
        # Coverage (optional)
        # "--cov=.",
        # "--cov-report=html:htmlcov",
        # "--cov-report=term-missing",
        
        # Parallel execution (if pytest-xdist is available)
        # "-n", "auto",
    ]
    
    # Add environment-specific configurations
    if os.getenv("CI"):
        # CI-specific configurations
        pytest_args.extend([
            "--timeout=300",  # 5 minute timeout per test
            "--junit-xml=integration-test-results.xml",
        ])
    
    print("🚀 Running Ainflue Integration Tests")
    print("=" * 50)
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("✅ All integration tests passed!")
    else:
        print(f"❌ Integration tests failed with exit code: {exit_code}")
    
    return exit_code


def run_specific_test_category(category: str):
    """Run tests for a specific category."""
    
    category_paths = {
        "api": "tests/integration/api_endpoints/",
        "database": "tests/integration/database/",
        "external": "tests/integration/external_apis/",
        "workflow": "tests/integration/workflow/",
        "security": "tests/integration/security/",
        "cross-service": "tests/integration/test_cross_service_integration.py"
    }
    
    if category not in category_paths:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(category_paths.keys())}")
        return 1
    
    test_path = category_paths[category]
    
    pytest_args = [
        test_path,
        "--verbose",
        "--tb=short",
        "--asyncio-mode=auto",
        "-m", "integration",
    ]
    
    print(f"🚀 Running {category.title()} Integration Tests")
    print("=" * 50)
    
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
        "-m", "integration and not slow",  # Exclude slow tests
        "--durations=5",
    ]
    
    print("🚀 Running Fast Integration Tests")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("✅ Fast integration tests passed!")
    else:
        print(f"❌ Fast integration tests failed with exit code: {exit_code}")
    
    return exit_code


def run_critical_integration_tests():
    """Run only critical integration tests."""
    
    pytest_args = [
        "tests/integration/",
        "--verbose",
        "--tb=short",
        "--asyncio-mode=auto",
        "-k", "test_api_crud_database_consistency or test_authentication_security or test_content_protection_workflow",
        "--maxfail=1",  # Stop on first failure for critical tests
    ]
    
    print("🚀 Running Critical Integration Tests")
    print("=" * 50)
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("✅ Critical integration tests passed!")
    else:
        print(f"❌ Critical integration tests failed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ainflue Integration Test Runner")
    parser.add_argument(
        "mode",
        choices=["all", "api", "database", "external", "workflow", "security", "cross-service", "fast", "critical"],
        default="all",
        nargs="?",
        help="Test mode to run"
    )
    
    args = parser.parse_args()
    
    if args.mode == "all":
        exit_code = run_all_integration_tests()
    elif args.mode in ["api", "database", "external", "workflow", "security", "cross-service"]:
        exit_code = run_specific_test_category(args.mode)
    elif args.mode == "fast":
        exit_code = run_fast_integration_tests()
    elif args.mode == "critical":
        exit_code = run_critical_integration_tests()
    else:
        print(f"❌ Unknown mode: {args.mode}")
        exit_code = 1
    
    sys.exit(exit_code)