"""
Master configuration for Industrial Testing Suite.
Configuration for 0 mocks, 100% real industrial-grade testing.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class TestingLevel(Enum):
    """
Testing levels for industrial testing."""

    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    INDUSTRIAL = "industrial"


class TestingScope(Enum):
    """Scope of testing."""

    FAST = "fast"           # < 30 seconds
    MEDIUM = "medium"       # 30s - 5 minutes
    SLOW = "slow"          # 5 - 30 minutes
    EXTENDED = "extended"   # > 30 minutes


@dataclass
class IndustrialTestConfig:
    """Configuration for industrial testing."""
    
    # General settings
    zero_mocks_enforcement: bool = True
    real_api_testing: bool = True
    real_database_testing: bool = True
    real_external_services: bool = True
    
    # Load testing settings
    max_concurrent_users: int = 10000
    load_test_duration_minutes: int = 30
    target_requests_per_second: int = 50000
    max_acceptable_response_time_ms: int = 100
    min_success_rate: float = 0.95
    
    # Security testing settings
    enable_owasp_top10_testing: bool = True
    enable_penetration_testing: bool = True
    security_scan_depth: str = "comprehensive"
    vulnerability_tolerance: str = "none"
    
    # Performance testing settings
    sub_100ms_requirement: bool = True
    performance_baseline_percentile: int = 95
    memory_usage_limit_mb: int = 2048
    cpu_usage_limit_percent: int = 80
    
    # Chaos engineering settings
    chaos_engineering_enabled: bool = True
    max_acceptable_downtime_seconds: int = 300  # 5 minutes
    recovery_time_target_seconds: int = 60
    resilience_score_minimum: int = 70
    
    # Compliance testing settings
    gdpr_compliance_required: bool = True
    ccpa_compliance_required: bool = True
    automated_compliance_monitoring: bool = True
    compliance_score_minimum: int = 80
    
    # Environment settings
    test_environment_isolation: bool = True
    cleanup_after_tests: bool = True
    audit_trail_enabled: bool = True
    
    # Reporting settings
    generate_detailed_reports: bool = True
    export_metrics_to_monitoring: bool = True
    alert_on_failures: bool = True


# Default industrial testing configuration
DEFAULT_INDUSTRIAL_CONFIG = IndustrialTestConfig()

# Test suite definitions
INDUSTRIAL_TEST_SUITES = {
    "load_testing_10k": {
        "description": "Load testing with 10K+ concurrent users",
        "test_files": ["tests/performance/test_industrial_load_10k.py"],
        "markers": ["load_10k", "slow", "industrial"],
        "timeout_minutes": 60,
        "requirements": {
            "min_concurrent_users": 10000,
            "max_response_time_ms": 100,
            "min_success_rate": 0.95
        }
    },
    
    "security_owasp_top10": {
        "description": "Complete OWASP Top 10 security testing",
        "test_files": ["tests/security/test_owasp_top10_industrial.py"],
        "markers": ["security", "slow", "industrial"],
        "timeout_minutes": 45,
        "requirements": {
            "security_score_minimum": 80,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 2
        }
    },
    
    "performance_sub_100ms": {
        "description": "Sub-100ms API performance testing",
        "test_files": ["tests/performance/test_sub_100ms_api_performance.py"],
        "markers": ["sub_100ms", "performance", "industrial"],
        "timeout_minutes": 30,
        "requirements": {
            "max_avg_response_time_ms": 100,
            "max_p95_response_time_ms": 150,
            "max_p99_response_time_ms": 200
        }
    },
    
    "integration_e2e_real": {
        "description": "End-to-end integration testing with 0 mocks",
        "test_files": ["tests/integration/test_industrial_e2e_real.py"],
        "markers": ["integration", "zero_mocks", "slow", "industrial"],
        "timeout_minutes": 45,
        "requirements": {
            "success_rate_minimum": 80,
            "step_completion_rate": 90,
            "zero_mocks_verified": True
        }
    },
    
    "chaos_engineering": {
        "description": "Chaos engineering resilience testing",
        "test_files": ["tests/chaos/test_industrial_chaos_engineering.py"],
        "markers": ["chaos", "slow", "industrial"],
        "timeout_minutes": 60,
        "requirements": {
            "resilience_score_minimum": 70,
            "max_recovery_time_seconds": 300,
            "system_resilience_rating": ["GOOD", "EXCELLENT"]
        }
    },
    
    "compliance_gdpr_ccpa": {
        "description": "Automated GDPR/CCPA compliance testing",
        "test_files": ["tests/compliance/test_automated_gdpr_ccpa.py"],
        "markers": ["compliance", "slow", "industrial"],
        "timeout_minutes": 30,
        "requirements": {
            "compliance_rate_minimum": 80,
            "critical_violations": 0,
            "average_compliance_score": 75
        }
    }
}

# Test execution order for industrial testing
INDUSTRIAL_TEST_EXECUTION_ORDER = [
    "performance_sub_100ms",     # Fast performance baseline
    "security_owasp_top10",      # Security validation
    "integration_e2e_real",      # Business logic validation
    "compliance_gdpr_ccpa",      # Compliance validation
    "chaos_engineering",         # Resilience validation
    "load_testing_10k"          # Scale validation (last due to resource intensity)
]

# Pytest command templates for industrial testing
PYTEST_COMMANDS = {
    "quick_industrial": "python -m pytest -m 'industrial and not slow' --tb=short -v",
    "full_industrial": "python -m pytest -m 'industrial' --tb=short -v --timeout=3600",
    "load_only": "python -m pytest -m 'load_10k' --tb=short -v --timeout=7200",
    "security_only": "python -m pytest -m 'security and industrial' --tb=short -v",
    "performance_only": "python -m pytest -m 'sub_100ms or performance' --tb=short -v",
    "compliance_only": "python -m pytest -m 'compliance' --tb=short -v",
    "chaos_only": "python -m pytest -m 'chaos' --tb=short -v --timeout=3600",
    "zero_mocks_verification": "python -m pytest -m 'zero_mocks' --tb=short -v"
}

# Environment variables for industrial testing
INDUSTRIAL_TESTING_ENV_VARS = {
    "INDUSTRIAL_TESTING_MODE": "true",
    "ZERO_MOCKS_ENFORCEMENT": "true",
    "REAL_API_TESTING": "true",
    "LOAD_TEST_MAX_USERS": "10000",
    "PERFORMANCE_TARGET_MS": "100",
    "SECURITY_SCAN_LEVEL": "comprehensive",
    "CHAOS_ENGINEERING_ENABLED": "true",
    "COMPLIANCE_AUTOMATION": "true"
}

# Monitoring and alerting thresholds
MONITORING_THRESHOLDS = {
    "load_testing": {
        "max_response_time_ms": 100,
        "min_requests_per_second": 1000,
        "max_error_rate": 0.05,
        "max_memory_usage_mb": 2048,
        "max_cpu_usage_percent": 80
    },
    "security_testing": {
        "max_critical_vulnerabilities": 0,
        "max_high_vulnerabilities": 2,
        "min_security_score": 80,
        "max_scan_duration_minutes": 45
    },
    "performance_testing": {
        "max_avg_response_time_ms": 100,
        "max_p95_response_time_ms": 150,
        "max_p99_response_time_ms": 200,
        "min_throughput_rps": 100
    },
    "chaos_engineering": {
        "max_recovery_time_seconds": 300,
        "min_resilience_score": 70,
        "max_downtime_seconds": 600
    },
    "compliance": {
        "min_compliance_rate": 80,
        "max_critical_violations": 0,
        "min_compliance_score": 75
    }
}

# Report generation settings
REPORT_SETTINGS = {
    "output_format": ["json", "html", "xml"],
    "include_metrics": True,
    "include_screenshots": True,
    "include_traces": True,
    "archive_results": True,
    "retention_days": 90
}


def get_industrial_test_config() -> IndustrialTestConfig:
    """Get the industrial testing configuration."""
    return DEFAULT_INDUSTRIAL_CONFIG


def get_test_suite_config(suite_name: str) -> Dict[str, Any]:
    """
Get configuration for a specific test suite."""
    return INDUSTRIAL_TEST_SUITES.get(suite_name, {})


def get_pytest_command(command_type: str) -> str:
    """
Get pytest command for specific testing type."""
    return PYTEST_COMMANDS.get(command_type, "python -m pytest")


def setup_industrial_testing_environment():
    """Setup environment variables for industrial testing."""
    for key, value in INDUSTRIAL_TESTING_ENV_VARS.items():
        os.environ[key] = value


def validate_industrial_test_results(results: Dict[str, Any], suite_name: str) -> bool:
    """
Validate industrial test results against requirements."""
    suite_config = get_test_suite_config(suite_name)
    requirements = suite_config.get("requirements", {})
    
    for requirement, expected_value in requirements.items():
        actual_value = results.get(requirement)
        
        if actual_value is None:
            return False
            
        if isinstance(expected_value, (int, float)):
            if "minimum" in requirement or "min_" in requirement:
                if actual_value < expected_value:
                    return False
            elif "maximum" in requirement or "max_" in requirement:
                if actual_value > expected_value:
                    return False
        elif isinstance(expected_value, list):
            if actual_value not in expected_value:
                return False
        elif isinstance(expected_value, bool):
            if actual_value != expected_value:
                return False
    
    return True


# Export main configuration
__all__ = [
    "IndustrialTestConfig",
    "DEFAULT_INDUSTRIAL_CONFIG", 
    "INDUSTRIAL_TEST_SUITES",
    "INDUSTRIAL_TEST_EXECUTION_ORDER",
    "PYTEST_COMMANDS",
    "MONITORING_THRESHOLDS",
    "get_industrial_test_config",
    "get_test_suite_config",
    "get_pytest_command",
    "setup_industrial_testing_environment",
    "validate_industrial_test_results"
]