#!/usr/bin/env python3
"""
Database Infrastructure Validation Tests
========================================
Author: Fahed Mlaiel (mlaiel@live.de)

Simple validation tests to ensure the database infrastructure
is properly configured and deployable.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'

def print_status(message, status="INFO"):
    colors = {
        "INFO": BLUE,
        "PASS": GREEN,
        "FAIL": RED,
        "WARN": YELLOW
    }
    color = colors.get(status, BLUE)
    print(f"{color}[{status}]{ENDC} {message}")

def test_file_exists(filepath, description):
    """Test if a required file exists"""
    if Path(filepath).exists():
        print_status(f"{description}: ✓", "PASS")
        return True
    else:
        print_status(f"{description}: ✗ - {filepath} not found", "FAIL")
        return False

def test_file_executable(filepath, description):
    """Test if a file is executable"""
    if os.access(filepath, os.X_OK):
        print_status(f"{description}: ✓", "PASS")
        return True
    else:
        print_status(f"{description}: ✗ - {filepath} not executable", "FAIL")
        return False

def test_docker_compose_syntax(compose_file):
    """Test Docker Compose file syntax"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", compose_file, "config"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            print_status(f"Docker Compose syntax ({compose_file}): ✓", "PASS")
            return True
        else:
            print_status(f"Docker Compose syntax ({compose_file}): ✗", "FAIL")
            print_status(f"Error: {result.stderr}", "FAIL")
            return False
    except FileNotFoundError:
        print_status(f"Docker Compose not found - skipping syntax test", "WARN")
        return True

def test_environment_template():
    """Test environment template completeness"""
    env_template = Path(__file__).parent.parent / ".env.production.template"
    
    if not env_template.exists():
        print_status("Environment template: ✗ - file not found", "FAIL")
        return False
    
    content = env_template.read_text()
    
    # Check for required environment variables
    required_vars = [
        "POSTGRES_PASSWORD",
        "POSTGRES_REPLICATION_PASSWORD",
        "POSTGRES_MASTER_HOST",
        "POSTGRES_SLAVE_HOST",
        "REDIS_HOST",
        "GRAFANA_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Environment template: ✗ - missing variables: {missing_vars}", "FAIL")
        return False
    else:
        print_status("Environment template: ✓", "PASS")
        return True

def test_postgresql_config():
    """Test PostgreSQL configuration files"""
    config_dir = Path(__file__).parent.parent / "database" / "postgresql"
    
    configs = [
        ("master.conf", "PostgreSQL master config"),
        ("slave.conf", "PostgreSQL slave config"),
        ("pg_hba.conf", "PostgreSQL authentication config")
    ]
    
    all_pass = True
    for config_file, description in configs:
        config_path = config_dir / config_file
        
        if not config_path.exists():
            print_status(f"{description}: ✗ - file not found", "FAIL")
            all_pass = False
            continue
        
        content = config_path.read_text()
        
        # Basic validation for PostgreSQL configs
        if config_file == "master.conf":
            required_settings = ["wal_level", "max_wal_senders", "shared_buffers"]
        elif config_file == "slave.conf":
            required_settings = ["hot_standby", "max_standby_archive_delay"]
        else:  # pg_hba.conf
            required_settings = ["replication", "ainflue_platform"]
        
        missing_settings = []
        for setting in required_settings:
            if setting not in content:
                missing_settings.append(setting)
        
        if missing_settings:
            print_status(f"{description}: ✗ - missing settings: {missing_settings}", "FAIL")
            all_pass = False
        else:
            print_status(f"{description}: ✓", "PASS")
    
    return all_pass

def test_monitoring_config():
    """Test monitoring configuration"""
    monitoring_dir = Path(__file__).parent.parent / "monitoring"
    
    configs = [
        ("prometheus/prometheus.yml", "Prometheus config"),
        ("prometheus/alert_rules.yml", "Alert rules config")
    ]
    
    all_pass = True
    for config_file, description in configs:
        config_path = monitoring_dir / config_file
        
        if not config_path.exists():
            print_status(f"{description}: ✗ - file not found", "FAIL")
            all_pass = False
            continue
        
        content = config_path.read_text()
        
        # Basic validation
        if "prometheus.yml" in config_file:
            required_content = ["postgres-master", "postgres-slave", "redis"]
        else:  # alert_rules.yml
            required_content = ["PostgreSQLMasterDown", "PostgreSQLSlaveDown"]
        
        missing_content = []
        for item in required_content:
            if item not in content:
                missing_content.append(item)
        
        if missing_content:
            print_status(f"{description}: ✗ - missing content: {missing_content}", "FAIL")
            all_pass = False
        else:
            print_status(f"{description}: ✓", "PASS")
    
    return all_pass

def main():
    """Run all validation tests"""
    print_status("Starting Database Infrastructure Validation Tests", "INFO")
    print("=" * 60)
    
    all_tests_pass = True
    
    # Test required files exist
    print_status("\n1. Testing Required Files", "INFO")
    required_files = [
        ("docker-compose.production.yml", "Production Docker Compose"),
        ("docker-compose.monitoring.yml", "Monitoring Docker Compose"),
        ("database/init.sql", "Database initialization script"),
        ("database/production_deployment.py", "Production deployment script"),
        ("scripts/deploy-database.sh", "Deployment shell script"),
        ("DATABASE_PRODUCTION_SETUP.md", "Documentation")
    ]
    
    for filepath, description in required_files:
        full_path = Path(__file__).parent.parent / filepath
        if not test_file_exists(str(full_path), description):
            all_tests_pass = False
    
    # Test executable permissions
    print_status("\n2. Testing Executable Permissions", "INFO")
    executable_files = [
        ("scripts/deploy-database.sh", "Deployment script executable")
    ]
    
    for filepath, description in executable_files:
        full_path = Path(__file__).parent.parent / filepath
        if not test_file_executable(str(full_path), description):
            all_tests_pass = False
    
    # Test Docker Compose syntax
    print_status("\n3. Testing Docker Compose Syntax", "INFO")
    compose_files = [
        "docker-compose.production.yml",
        "docker-compose.monitoring.yml"
    ]
    
    for compose_file in compose_files:
        if not test_docker_compose_syntax(compose_file):
            all_tests_pass = False
    
    # Test environment template
    print_status("\n4. Testing Environment Configuration", "INFO")
    if not test_environment_template():
        all_tests_pass = False
    
    # Test PostgreSQL configuration
    print_status("\n5. Testing PostgreSQL Configuration", "INFO")
    if not test_postgresql_config():
        all_tests_pass = False
    
    # Test monitoring configuration
    print_status("\n6. Testing Monitoring Configuration", "INFO")
    if not test_monitoring_config():
        all_tests_pass = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_tests_pass:
        print_status("All validation tests PASSED! ✓", "PASS")
        print_status("Database infrastructure is ready for deployment", "INFO")
        return 0
    else:
        print_status("Some validation tests FAILED! ✗", "FAIL")
        print_status("Please fix the issues before deployment", "WARN")
        return 1

if __name__ == "__main__":
    sys.exit(main())