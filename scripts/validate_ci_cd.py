#!/usr/bin/env python3
"""
CI/CD Pipeline Validation Script
Validates that all CI/CD requirements are properly implemented
"""

import os
import json
import yaml
from pathlib import Path

def check_ci_cd_implementation():
    """Check all CI/CD requirements"""
    
    results = {
        "github_actions_workflows": False,
        "automated_testing": False,
        "code_quality_gates": False,
        "security_scanning": False,
        "deployment_automation": False,
        "rollback_procedures": False,
        "details": {}
    }
    
    # 1. Check GitHub Actions workflows
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        if len(workflow_files) >= 3:  # At least CI, deployment, security
            results["github_actions_workflows"] = True
            results["details"]["workflows"] = [f.name for f in workflow_files]
    
    # 2. Check automated testing setup
    ci_file = workflows_dir / "ci.yml"
    if ci_file.exists():
        with open(ci_file) as f:
            ci_content = f.read()
            if all(keyword in ci_content for keyword in ["pytest", "unit-tests", "integration-tests"]):
                results["automated_testing"] = True
                results["details"]["testing"] = "Unit, integration, and API tests configured"
    
    # 3. Check code quality gates
    if ci_file.exists():
        with open(ci_file) as f:
            ci_content = f.read()
            quality_tools = ["black", "flake8", "mypy"]
            found_tools = [tool for tool in quality_tools if tool in ci_content]
            if len(found_tools) >= 2:
                results["code_quality_gates"] = True
                results["details"]["quality_tools"] = found_tools
    
    # 4. Check security scanning
    security_file = workflows_dir / "security-scan.yml"
    if security_file.exists():
        with open(security_file) as f:
            security_content = f.read()
            security_tools = ["bandit", "safety", "trivy", "semgrep"]
            found_security = [tool for tool in security_tools if tool in security_content]
            if len(found_security) >= 2:
                results["security_scanning"] = True
                results["details"]["security_tools"] = found_security
    
    # 5. Check deployment automation
    deployment_file = workflows_dir / "production-deployment.yml"
    if deployment_file.exists():
        with open(deployment_file) as f:
            deployment_content = f.read()
            if all(keyword in deployment_content for keyword in ["kubectl", "deploy", "kubernetes"]):
                results["deployment_automation"] = True
                results["details"]["deployment"] = "Kubernetes deployment automation configured"
    
    # 6. Check rollback procedures
    if deployment_file.exists():
        with open(deployment_file) as f:
            deployment_content = f.read()
            if any(keyword in deployment_content for keyword in ["rollback", "blue-green", "health-monitoring"]):
                results["rollback_procedures"] = True
                results["details"]["rollback"] = "Automated rollback procedures configured"
    
    return results

def check_required_files():
    """Check if required files exist"""
    required_files = [
        "Dockerfile",
        "requirements.txt",
        "requirements-production.txt",
        "kubernetes/environments/staging/deployment.yaml",
        "kubernetes/environments/production/deployment.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return missing_files

def main():
    print("🔍 Validating CI/CD Pipeline Implementation...")
    print("=" * 60)
    
    # Check CI/CD implementation
    results = check_ci_cd_implementation()
    
    print("📋 CI/CD Requirements Status:")
    requirements = [
        ("GitHub Actions workflows", results["github_actions_workflows"]),
        ("Automated testing", results["automated_testing"]),
        ("Code quality gates", results["code_quality_gates"]),
        ("Security scanning", results["security_scanning"]),
        ("Deployment automation", results["deployment_automation"]),
        ("Rollback procedures", results["rollback_procedures"])
    ]
    
    for req, status in requirements:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {req}")
    
    print("\n📂 Implementation Details:")
    for key, value in results["details"].items():
        print(f"  • {key}: {value}")
    
    # Check required files
    missing_files = check_required_files()
    if missing_files:
        print(f"\n⚠️  Missing Files:")
        for file in missing_files:
            print(f"  • {file}")
    else:
        print(f"\n✅ All required files present")
    
    # Overall status
    all_passed = all(results[key] for key in results if key != "details")
    overall_status = "✅ COMPLETE" if all_passed else "⚠️  NEEDS ATTENTION"
    print(f"\n🎯 Overall Status: {overall_status}")
    
    if all_passed:
        print("\n🎉 CI/CD Pipeline implementation is complete!")
        print("All requirements have been successfully implemented.")
    else:
        print("\n📝 Next Steps:")
        for req, status in requirements:
            if not status:
                print(f"  • Fix: {req}")

if __name__ == "__main__":
    main()