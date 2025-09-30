#!/usr/bin/env python3
"""
Configuration Validator - IA Chérie Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: DevOps Engineer + DBA + Security Expert
Purpose: Enterprise configuration validation and compliance checking
"""

import asyncio
import json
import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import configparser
import re
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """Enterprise configuration validation system"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/home/runner/work/IA Chérie/IA Chérie")
        self.config_files = self._discover_config_files()
        self.validation_rules = self._load_validation_rules()
        self.results = {
            "files_validated": 0,
            "errors": [],
            "warnings": [],
            "security_issues": [],
            "compliance_violations": []
        }
    
    def _discover_config_files(self) -> Dict[str, List[Path]]:
        """Discover all configuration files in the project"""
        config_patterns = {
            "docker": ["Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml"],
            "kubernetes": ["*.yaml", "*.yml", "deployment.yaml", "service.yaml"],
            "python": ["*.ini", "*.cfg", "requirements*.txt", "setup.py", "pyproject.toml"],
            "nodejs": ["package.json", "package-lock.json", "tsconfig.json", "next.config.js"],
            "env": [".env*", "*.env"],
            "nginx": ["nginx.conf", "*.conf"],
            "database": ["alembic.ini", "*.sql"],
            "monitoring": ["prometheus.yml", "grafana.json"],
            "security": ["*.pem", "*.key", "*.crt"]
        }
        
        found_configs = {category: [] for category in config_patterns}
        
        for category, patterns in config_patterns.items():
            for pattern in patterns:
                if category == "kubernetes":
                    # Look specifically in kubernetes directories
                    k8s_dirs = [
                        self.project_root / "kubernetes",
                        self.project_root / "k8s",
                        self.project_root / "manifests"
                    ]
                    for k8s_dir in k8s_dirs:
                        if k8s_dir.exists():
                            matches = list(k8s_dir.rglob(pattern))
                            found_configs[category].extend(matches)
                else:
                    matches = list(self.project_root.rglob(pattern))
                    for match in matches:
                        if match.is_file():
                            found_configs[category].append(match)
        
        return found_configs
    
    def _load_validation_rules(self) -> Dict[str, Dict]:
        """Load validation rules for different config types"""
        return {
            "docker": {
                "required_instructions": ["FROM"],
                "security_checks": {
                    "no_root_user": True,
                    "no_latest_tag": True,
                    "no_hardcoded_secrets": True
                },
                "best_practices": {
                    "use_multi_stage": True,
                    "minimize_layers": True,
                    "health_check": True
                }
            },
            "env": {
                "required_vars": [
                    "DATABASE_URL", "SECRET_KEY", "DEBUG", "ENVIRONMENT"
                ],
                "security_patterns": [
                    r"password=[\w]+",
                    r"secret=[\w]+",
                    r"key=[\w]+",
                    r"token=[\w]+"
                ],
                "dangerous_values": ["root", "admin", "password123", "secret"]
            },
            "python": {
                "security_packages": [
                    "bandit", "safety", "secure"
                ],
                "version_pinning": True,
                "vulnerable_packages": [
                    "pillow<10.0.1", "requests<2.31.0"
                ]
            },
            "kubernetes": {
                "required_fields": {
                    "deployment": ["apiVersion", "kind", "metadata", "spec"],
                    "service": ["apiVersion", "kind", "metadata", "spec"]
                },
                "security_context": {
                    "runAsNonRoot": True,
                    "readOnlyRootFilesystem": True,
                    "allowPrivilegeEscalation": False
                },
                "resource_limits": True
            }
        }
    
    async def validate_docker_file(self, dockerfile: Path) -> Dict[str, Any]:
        """Validate Dockerfile configuration"""
        issues = {"errors": [], "warnings": [], "security": []}
        
        try:
            content = dockerfile.read_text()
            lines = content.split('\n')
            
            # Check required instructions
            has_from = any(line.strip().startswith('FROM') for line in lines)
            if not has_from:
                issues["errors"].append("Missing FROM instruction")
            
            # Security checks
            for line in lines:
                line = line.strip()
                
                # Check for root user
                if line.startswith('USER root') or line.startswith('USER 0'):
                    issues["security"].append("Running as root user detected")
                
                # Check for latest tag
                if ':latest' in line and line.startswith('FROM'):
                    issues["warnings"].append("Using ':latest' tag is not recommended")
                
                # Check for hardcoded secrets
                secret_patterns = [r'password\s*=\s*["\'][^"\']+["\']', 
                                 r'secret\s*=\s*["\'][^"\']+["\']',
                                 r'token\s*=\s*["\'][^"\']+["\']']
                for pattern in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues["security"].append(f"Potential hardcoded secret: {line}")
            
            # Best practices
            has_healthcheck = any('HEALTHCHECK' in line for line in lines)
            if not has_healthcheck:
                issues["warnings"].append("Missing HEALTHCHECK instruction")
                
        except Exception as e:
            issues["errors"].append(f"Failed to read Dockerfile: {e}")
        
        return issues
    
    async def validate_env_file(self, env_file: Path) -> Dict[str, Any]:
        """Validate environment configuration file"""
        issues = {"errors": [], "warnings": [], "security": []}
        
        try:
            content = env_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            env_vars = {}
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            # Check required variables
            rules = self.validation_rules["env"]
            for required_var in rules["required_vars"]:
                if required_var not in env_vars:
                    issues["warnings"].append(f"Missing recommended variable: {required_var}")
            
            # Security checks
            for key, value in env_vars.items():
                # Check for dangerous values
                if value.lower() in rules["dangerous_values"]:
                    issues["security"].append(f"Insecure value for {key}: {value}")
                
                # Check for unquoted secrets
                if any(secret_word in key.lower() for secret_word in ['password', 'secret', 'key', 'token']):
                    if not (value.startswith('"') and value.endswith('"')) and not (value.startswith("'") and value.endswith("'")):
                        issues["warnings"].append(f"Unquoted sensitive variable: {key}")
                
                # Check for empty critical variables
                if not value and key in ['DATABASE_URL', 'SECRET_KEY']:
                    issues["errors"].append(f"Critical variable is empty: {key}")
                    
        except Exception as e:
            issues["errors"].append(f"Failed to read env file: {e}")
        
        return issues
    
    async def validate_yaml_file(self, yaml_file: Path) -> Dict[str, Any]:
        """Validate YAML configuration file"""
        issues = {"errors": [], "warnings": [], "security": []}
        
        try:
            with open(yaml_file, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    issues["errors"].append(f"Invalid YAML syntax: {e}")
                    return issues
            
            # Kubernetes-specific validation
            if yaml_file.name.endswith('.yaml') or yaml_file.name.endswith('.yml'):
                if isinstance(data, dict) and 'kind' in data:
                    await self._validate_kubernetes_manifest(data, issues)
            
            # Docker Compose validation
            if 'docker-compose' in yaml_file.name:
                await self._validate_docker_compose(data, issues)
                
        except Exception as e:
            issues["errors"].append(f"Failed to validate YAML: {e}")
        
        return issues
    
    async def _validate_kubernetes_manifest(self, manifest: Dict, issues: Dict):
        """Validate Kubernetes manifest"""
        kind = manifest.get('kind', '').lower()
        rules = self.validation_rules["kubernetes"]
        
        # Check required fields
        if kind in rules["required_fields"]:
            for field in rules["required_fields"][kind]:
                if field not in manifest:
                    issues["errors"].append(f"Missing required field: {field}")
        
        # Security context validation for Deployments/Pods
        if kind in ['deployment', 'pod']:
            spec = manifest.get('spec', {})
            if kind == 'deployment':
                containers = spec.get('template', {}).get('spec', {}).get('containers', [])
            else:
                containers = spec.get('containers', [])
            
            for container in containers:
                security_context = container.get('securityContext', {})
                
                # Check security context settings
                if not security_context.get('runAsNonRoot'):
                    issues["security"].append(f"Container should run as non-root: {container.get('name')}")
                
                if security_context.get('allowPrivilegeEscalation', True):
                    issues["security"].append(f"Privilege escalation should be disabled: {container.get('name')}")
                
                # Check resource limits
                resources = container.get('resources', {})
                if not resources.get('limits'):
                    issues["warnings"].append(f"Missing resource limits: {container.get('name')}")
    
    async def _validate_docker_compose(self, compose_data: Dict, issues: Dict):
        """Validate Docker Compose configuration"""
        services = compose_data.get('services', {})
        
        for service_name, service_config in services.items():
            # Check for exposed ports without security
            ports = service_config.get('ports', [])
            for port in ports:
                if isinstance(port, str) and port.startswith('0.0.0.0:'):
                    issues["security"].append(f"Service {service_name} exposes port to all interfaces")
            
            # Check for privileged containers
            if service_config.get('privileged', False):
                issues["security"].append(f"Service {service_name} runs in privileged mode")
            
            # Check for missing health checks
            if 'healthcheck' not in service_config:
                issues["warnings"].append(f"Service {service_name} missing health check")
    
    async def validate_python_requirements(self, req_file: Path) -> Dict[str, Any]:
        """Validate Python requirements file"""
        issues = {"errors": [], "warnings": [], "security": []}
        
        try:
            content = req_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            for line in lines:
                # Check version pinning
                if '==' not in line and not line.startswith('-e'):
                    issues["warnings"].append(f"Package not pinned to specific version: {line}")
                
                # Check for vulnerable packages
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                for vulnerable in self.validation_rules["python"]["vulnerable_packages"]:
                    if package_name in vulnerable:
                        issues["security"].append(f"Potentially vulnerable package: {line}")
                        
        except Exception as e:
            issues["errors"].append(f"Failed to validate requirements: {e}")
        
        return issues
    
    async def check_file_permissions(self, file_path: Path) -> Dict[str, Any]:
        """Check file permissions for security issues"""
        issues = {"errors": [], "warnings": [], "security": []}
        
        try:
            stat = file_path.stat()
            mode = oct(stat.st_mode)[-3:]
            
            # Check for overly permissive files
            if file_path.suffix in ['.key', '.pem', '.crt']:
                if mode != '600':
                    issues["security"].append(f"Certificate/key file has insecure permissions: {mode}")
            
            # Check for world-readable config files
            if file_path.name.startswith('.env') or 'secret' in file_path.name.lower():
                if int(mode[2]) > 0:  # World readable
                    issues["security"].append(f"Sensitive file is world-readable: {mode}")
                    
        except Exception as e:
            issues["warnings"].append(f"Could not check permissions: {e}")
        
        return issues
    
    async def comprehensive_validation(self) -> Dict[str, Any]:
        """Perform comprehensive configuration validation"""
        print("🔍 Starting comprehensive configuration validation...")
        
        all_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "categories": {},
            "summary": {
                "total_errors": 0,
                "total_warnings": 0,
                "total_security_issues": 0,
                "critical_issues": []
            }
        }
        
        for category, files in self.config_files.items():
            if not files:
                continue
                
            print(f"  📁 Validating {category} configurations...")
            
            category_results = {
                "files": [],
                "errors": 0,
                "warnings": 0,
                "security_issues": 0
            }
            
            for config_file in files:
                if not config_file.exists():
                    continue
                    
                file_result = {
                    "path": str(config_file),
                    "issues": {"errors": [], "warnings": [], "security": []}
                }
                
                # Validate based on file type
                if category == "docker" and config_file.name.startswith("Dockerfile"):
                    file_result["issues"] = await self.validate_docker_file(config_file)
                elif category == "env":
                    file_result["issues"] = await self.validate_env_file(config_file)
                elif category in ["kubernetes", "docker"] and config_file.suffix in ['.yml', '.yaml']:
                    file_result["issues"] = await self.validate_yaml_file(config_file)
                elif category == "python" and "requirements" in config_file.name:
                    file_result["issues"] = await self.validate_python_requirements(config_file)
                
                # Always check file permissions
                perm_issues = await self.check_file_permissions(config_file)
                file_result["issues"]["security"].extend(perm_issues["security"])
                file_result["issues"]["warnings"].extend(perm_issues["warnings"])
                
                # Count issues
                category_results["errors"] += len(file_result["issues"]["errors"])
                category_results["warnings"] += len(file_result["issues"]["warnings"])  
                category_results["security_issues"] += len(file_result["issues"]["security"])
                
                category_results["files"].append(file_result)
                all_results["files_processed"] += 1
            
            all_results["categories"][category] = category_results
            all_results["summary"]["total_errors"] += category_results["errors"]
            all_results["summary"]["total_warnings"] += category_results["warnings"]
            all_results["summary"]["total_security_issues"] += category_results["security_issues"]
        
        # Identify critical issues
        for category, results in all_results["categories"].items():
            for file_info in results["files"]:
                if file_info["issues"]["security"]:
                    all_results["summary"]["critical_issues"].append({
                        "file": file_info["path"],
                        "category": category,
                        "security_issues": file_info["issues"]["security"]
                    })
        
        return all_results

async def main():
    """Main configuration validator execution"""
    validator = ConfigValidator()
    
    print("🔍 Configuration Validator - IA Chérie Platform")
    print("=" * 45)
    
    # Perform comprehensive validation
    results = await validator.comprehensive_validation()
    
    print(f"\n📊 Validation Summary:")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Errors: {results['summary']['total_errors']}")
    print(f"   Warnings: {results['summary']['total_warnings']}")
    print(f"   Security issues: {results['summary']['total_security_issues']}")
    
    # Show critical issues
    if results["summary"]["critical_issues"]:
        print(f"\n🔴 Critical Security Issues:")
        for issue in results["summary"]["critical_issues"]:
            print(f"   📄 {issue['file']}")
            for security_issue in issue['security_issues']:
                print(f"      ⚠️ {security_issue}")
    
    # Show category breakdown
    print(f"\n📋 By Category:")
    for category, data in results["categories"].items():
        if data["errors"] + data["warnings"] + data["security_issues"] > 0:
            print(f"   {category}: {data['errors']}E {data['warnings']}W {data['security_issues']}S")
    
    # Save detailed report
    reports_dir = validator.project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"config_validation_{int(datetime.now().timestamp())}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    
    # Return exit code based on critical issues
    if results["summary"]["total_errors"] > 0 or results["summary"]["critical_issues"]:
        print("\n❌ Validation failed - critical issues found!")
        return 1
    else:
        print("\n✅ Configuration validation passed!")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)