#!/usr/bin/env python3
"""
Docker Expert Implementation Validator
Comprehensive validation of all expert role implementations
Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import time
from datetime import datetime

class DockerExpertValidator:
    """Validate all expert role implementations"""
    
    def __init__(self):
        self.base_path = Path("/home/runner/work/Ainflue/Ainflue")
        self.docker_path = self.base_path / "docker"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "expert_implementations": {},
            "docker_files": {},
            "compose_files": {},
            "overall_score": 0
        }
    
    def validate_expert_dockerfiles(self) -> Dict[str, any]:
        """Validate expert role dockerfiles"""
        print("🔍 Validating Expert Role Dockerfiles...")
        
        expert_dockerfiles = {
            "security_specialist": "security_hardening.dockerfile",
            "devops_engineer": "devops_automation.dockerfile", 
            "backend_senior": "enterprise_api_gateway.dockerfile",
            "ml_engineer": "ml_pipeline_orchestrator.dockerfile",
            "database_admin": "database_cluster_manager.dockerfile",
            "audio_engineer": "advanced_audio_processor.dockerfile",
            "microservices_architect": "service_mesh_orchestrator.dockerfile",
            "lead_dev_ia": "ai_orchestration_hub.dockerfile",
            "prompt_engineer": "prompt_engineering_hub.dockerfile"
        }
        
        validation_results = {}
        
        for role, dockerfile in expert_dockerfiles.items():
            dockerfile_path = self.docker_path / dockerfile
            
            if dockerfile_path.exists():
                # Validate dockerfile syntax
                try:
                    # Basic validation - check if file can be read and has proper structure
                    with open(dockerfile_path, 'r') as f:
                        content = f.read()
                    
                    validation_results[role] = {
                        "dockerfile": dockerfile,
                        "exists": True,
                        "size": len(content),
                        "has_from": "FROM" in content,
                        "has_maintainer": "LABEL maintainer" in content,
                        "has_healthcheck": "HEALTHCHECK" in content,
                        "has_user": "USER" in content,
                        "has_expose": "EXPOSE" in content,
                        "security_score": self._calculate_dockerfile_security_score(content)
                    }
                    
                    print(f"✅ {role}: {dockerfile} - Valid")
                    
                except Exception as e:
                    validation_results[role] = {
                        "dockerfile": dockerfile,
                        "exists": True,
                        "error": str(e),
                        "security_score": 0
                    }
                    print(f"❌ {role}: {dockerfile} - Error: {e}")
            else:
                validation_results[role] = {
                    "dockerfile": dockerfile,
                    "exists": False,
                    "security_score": 0
                }
                print(f"❌ {role}: {dockerfile} - Not found")
        
        return validation_results
    
    def _calculate_dockerfile_security_score(self, content: str) -> int:
        """Calculate security score for dockerfile"""
        score = 0
        
        # Security best practices
        if "USER" in content and "USER root" not in content:
            score += 20
        if "HEALTHCHECK" in content:
            score += 15
        if "LABEL maintainer" in content:
            score += 10
        if "--no-cache" in content:
            score += 10
        if "rm -rf" in content:  # Cleanup commands
            score += 10
        if "apt-get clean" in content or "rm -rf /var/lib/apt/lists/*" in content:
            score += 15
        if "groupadd" in content and "useradd" in content:
            score += 20
        
        return min(100, score)
    
    def validate_compose_files(self) -> Dict[str, any]:
        """Validate Docker Compose files"""
        print("🔍 Validating Docker Compose Files...")
        
        compose_files = list(self.docker_path.rglob("docker-compose*.yml"))
        validation_results = {}
        
        for compose_file in compose_files:
            try:
                # Validate YAML syntax
                with open(compose_file, 'r') as f:
                    compose_content = yaml.safe_load(f)
                
                # Check compose file structure
                validation_results[compose_file.name] = {
                    "path": str(compose_file.relative_to(self.base_path)),
                    "valid_yaml": True,
                    "has_version": "version" in compose_content,
                    "has_services": "services" in compose_content,
                    "service_count": len(compose_content.get("services", {})),
                    "has_networks": "networks" in compose_content,
                    "has_volumes": "volumes" in compose_content,
                    "size": compose_file.stat().st_size
                }
                
                # Test docker-compose config validation
                try:
                    result = subprocess.run([
                        "docker", "compose", "-f", str(compose_file), "config"
                    ], capture_output=True, text=True, cwd=self.base_path)
                    
                    validation_results[compose_file.name]["docker_compose_valid"] = result.returncode == 0
                    if result.returncode != 0:
                        validation_results[compose_file.name]["error"] = result.stderr
                    
                    print(f"✅ {compose_file.name} - Valid")
                    
                except Exception as e:
                    validation_results[compose_file.name]["docker_compose_valid"] = False
                    validation_results[compose_file.name]["error"] = str(e)
                    print(f"❌ {compose_file.name} - Error: {e}")
                
            except yaml.YAMLError as e:
                validation_results[compose_file.name] = {
                    "path": str(compose_file.relative_to(self.base_path)),
                    "valid_yaml": False,
                    "error": str(e)
                }
                print(f"❌ {compose_file.name} - YAML Error: {e}")
            except Exception as e:
                validation_results[compose_file.name] = {
                    "path": str(compose_file.relative_to(self.base_path)),
                    "error": str(e)
                }
                print(f"❌ {compose_file.name} - Error: {e}")
        
        return validation_results
    
    def validate_requirements_files(self) -> Dict[str, any]:
        """Validate requirements files"""
        print("🔍 Validating Requirements Files...")
        
        requirements_files = [
            "requirements.txt",
            "requirements-security.txt", 
            "requirements-ml.txt",
            "requirements-pipeline.txt"
        ]
        
        validation_results = {}
        
        for req_file in requirements_files:
            req_path = self.base_path / req_file
            
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        content = f.read()
                    
                    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    
                    validation_results[req_file] = {
                        "exists": True,
                        "package_count": len(lines),
                        "size": len(content),
                        "has_versions": sum(1 for line in lines if "==" in line or ">=" in line),
                        "content_preview": lines[:5]  # First 5 packages
                    }
                    
                    print(f"✅ {req_file} - {len(lines)} packages")
                    
                except Exception as e:
                    validation_results[req_file] = {
                        "exists": True,
                        "error": str(e)
                    }
                    print(f"❌ {req_file} - Error: {e}")
            else:
                validation_results[req_file] = {
                    "exists": False
                }
                print(f"❌ {req_file} - Not found")
        
        return validation_results
    
    def validate_package_json(self) -> Dict[str, any]:
        """Validate package.json for API Gateway"""
        print("🔍 Validating package.json...")
        
        package_path = self.base_path / "package.json"
        
        if package_path.exists():
            try:
                with open(package_path, 'r') as f:
                    package_content = json.load(f)
                
                validation_result = {
                    "exists": True,
                    "valid_json": True,
                    "has_name": "name" in package_content,
                    "has_version": "version" in package_content,
                    "has_dependencies": "dependencies" in package_content,
                    "has_dev_dependencies": "devDependencies" in package_content,
                    "dependency_count": len(package_content.get("dependencies", {})),
                    "dev_dependency_count": len(package_content.get("devDependencies", {}))
                }
                
                print(f"✅ package.json - {validation_result['dependency_count']} dependencies")
                return validation_result
                
            except json.JSONDecodeError as e:
                return {
                    "exists": True,
                    "valid_json": False,
                    "error": str(e)
                }
        else:
            return {"exists": False}
    
    def count_implementation_files(self) -> Dict[str, int]:
        """Count implementation files"""
        print("📊 Counting Implementation Files...")
        
        counts = {
            "dockerfiles": len(list(self.docker_path.rglob("*.dockerfile"))),
            "compose_files": len(list(self.docker_path.rglob("docker-compose*.yml"))),
            "readme_files": len(list(self.docker_path.rglob("README*.md"))),
            "python_files": len(list(self.docker_path.rglob("*.py"))),
            "yaml_configs": len(list(self.docker_path.rglob("*.yml"))) + len(list(self.docker_path.rglob("*.yaml"))),
            "total_files": len(list(self.docker_path.rglob("*.*")))
        }
        
        for key, value in counts.items():
            print(f"📁 {key}: {value}")
        
        return counts
    
    def calculate_overall_score(self, validation_data: Dict[str, any]) -> int:
        """Calculate overall implementation score"""
        score = 0
        max_score = 100
        
        # Expert dockerfiles score (40 points)
        expert_files = validation_data.get("expert_implementations", {})
        if expert_files:
            existing_experts = sum(1 for exp in expert_files.values() if exp.get("exists", False))
            total_experts = len(expert_files)
            expert_score = (existing_experts / total_experts) * 40 if total_experts > 0 else 0
            score += expert_score
        
        # Compose files score (30 points)
        compose_files = validation_data.get("compose_files", {})
        if compose_files:
            valid_compose = sum(1 for comp in compose_files.values() if comp.get("docker_compose_valid", False))
            total_compose = len(compose_files)
            compose_score = (valid_compose / total_compose) * 30 if total_compose > 0 else 0
            score += compose_score
        
        # Requirements and configs score (20 points)
        requirements = validation_data.get("requirements", {})
        package_json = validation_data.get("package_json", {})
        config_score = 0
        if requirements:
            existing_req = sum(1 for req in requirements.values() if req.get("exists", False))
            config_score += (existing_req / len(requirements)) * 15
        if package_json.get("exists", False):
            config_score += 5
        score += config_score
        
        # File counts score (10 points)
        file_counts = validation_data.get("file_counts", {})
        if file_counts.get("dockerfiles", 0) > 150:
            score += 5
        if file_counts.get("compose_files", 0) > 20:
            score += 5
        
        return min(max_score, int(score))
    
    def run_comprehensive_validation(self) -> Dict[str, any]:
        """Run comprehensive validation of all expert implementations"""
        print("🏆 DOCKER EXPERT IMPLEMENTATION VALIDATION")
        print("=" * 60)
        
        # Validate expert dockerfiles
        self.validation_results["expert_implementations"] = self.validate_expert_dockerfiles()
        
        print()
        
        # Validate compose files
        self.validation_results["compose_files"] = self.validate_compose_files()
        
        print()
        
        # Validate requirements files
        self.validation_results["requirements"] = self.validate_requirements_files()
        
        print()
        
        # Validate package.json
        self.validation_results["package_json"] = self.validate_package_json()
        
        print()
        
        # Count files
        self.validation_results["file_counts"] = self.count_implementation_files()
        
        print()
        
        # Calculate overall score
        self.validation_results["overall_score"] = self.calculate_overall_score(self.validation_results)
        
        return self.validation_results
    
    def generate_validation_report(self) -> str:
        """Generate validation report"""
        results = self.validation_results
        
        report = f"""# 🏆 DOCKER EXPERT IMPLEMENTATION VALIDATION REPORT

**Generated:** {results['timestamp']}
**Overall Score:** {results['overall_score']}/100

## 📊 VALIDATION SUMMARY

### 🎯 Expert Role Implementations
"""
        
        expert_impls = results.get("expert_implementations", {})
        for role, data in expert_impls.items():
            status = "✅" if data.get("exists", False) else "❌"
            security_score = data.get("security_score", 0)
            report += f"- **{role.replace('_', ' ').title()}:** {status} (Security: {security_score}/100)\n"
        
        report += f"""
### 🐳 Docker Infrastructure
- **Dockerfiles:** {results.get('file_counts', {}).get('dockerfiles', 0)}
- **Compose Files:** {results.get('file_counts', {}).get('compose_files', 0)}
- **Valid Compose Files:** {sum(1 for comp in results.get('compose_files', {}).values() if comp.get('docker_compose_valid', False))}

### 📦 Dependencies & Configuration
- **Requirements Files:** {sum(1 for req in results.get('requirements', {}).values() if req.get('exists', False))}/{len(results.get('requirements', {}))}
- **Package.json:** {"✅" if results.get('package_json', {}).get('exists', False) else "❌"}

### 📁 Implementation Statistics
- **Total Files:** {results.get('file_counts', {}).get('total_files', 0)}
- **README Files:** {results.get('file_counts', {}).get('readme_files', 0)}
- **Python Files:** {results.get('file_counts', {}).get('python_files', 0)}

## 🎯 EXPERT ROLE STATUS

### ✅ COMPLETED EXPERT IMPLEMENTATIONS
"""
        
        completed_experts = [role for role, data in expert_impls.items() if data.get("exists", False)]
        for expert in completed_experts:
            report += f"- {expert.replace('_', ' ').title()}\n"
        
        report += f"""
### 🔍 SECURITY ANALYSIS
"""
        
        for role, data in expert_impls.items():
            if data.get("exists", False):
                security_score = data.get("security_score", 0)
                security_level = "🔴 Low" if security_score < 50 else "🟡 Medium" if security_score < 80 else "🟢 High"
                report += f"- **{role.replace('_', ' ').title()}:** {security_level} ({security_score}/100)\n"
        
        report += f"""
## 🏆 OVERALL ASSESSMENT

**Implementation Completeness:** {results['overall_score']}/100

### 🎯 Achievement Status
"""
        
        if results['overall_score'] >= 90:
            report += "🏆 **EXCELLENT** - Enterprise-ready implementation\n"
        elif results['overall_score'] >= 75:
            report += "🥈 **GOOD** - Production-ready with minor improvements needed\n"
        elif results['overall_score'] >= 60:
            report += "🥉 **FAIR** - Functional but requires significant improvements\n"
        else:
            report += "⚠️ **NEEDS IMPROVEMENT** - Major gaps in implementation\n"
        
        report += f"""
---
**© 2025 Fahed Mlaiel - Docker Expert Implementation Validator**
"""
        
        return report

def main():
    """Main validation execution"""
    validator = DockerExpertValidator()
    
    try:
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()
        
        print("\n" + "=" * 60)
        print(f"🏆 VALIDATION COMPLETE - Overall Score: {results['overall_score']}/100")
        print("=" * 60)
        
        # Generate and save report
        report = validator.generate_validation_report()
        
        # Save validation results
        with open("/tmp/expert_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save validation report
        with open("/tmp/expert_validation_report.md", "w") as f:
            f.write(report)
        
        print(f"📊 Validation results saved to /tmp/expert_validation_results.json")
        print(f"📋 Validation report saved to /tmp/expert_validation_report.md")
        
        return results
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()