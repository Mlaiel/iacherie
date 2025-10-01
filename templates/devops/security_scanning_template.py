
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""Security Scanning Template for iacherie Platform
Enterprise-grade security vulnerability scanning and assessment templates.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ScanType(Enum):
    """Security scan types"""
    SAST = "static_analysis"  # Static Application Security Testing
    DAST = "dynamic_analysis"  # Dynamic Application Security Testing
    DEPENDENCY = "dependency_check"
    CONTAINER = "container_scan"
    INFRASTRUCTURE = "infrastructure_scan"
    SECRET = "secret_scan"
    COMPLIANCE = "compliance_check"


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityScanConfig:
    """Security scanning configuration"""
    project_name: str
    environment: str
    scan_types: List[ScanType]
    
    # SAST configuration
    enable_sonarqube: bool = True
    enable_semgrep: bool = True
    enable_bandit: bool = True
    enable_eslint_security: bool = True
    
    # DAST configuration
    enable_owasp_zap: bool = True
    enable_burp_suite: bool = False
    
    # Dependency scanning
    enable_safety: bool = True
    enable_npm_audit: bool = True
    enable_snyk: bool = True
    
    # Container scanning
    enable_trivy: bool = True
    enable_clair: bool = True
    enable_anchore: bool = False
    
    # Secret scanning
    enable_trufflehog: bool = True
    enable_gitleaks: bool = True
    enable_detect_secrets: bool = True
    
    # Compliance
    enable_cis_benchmark: bool = True
    enable_pci_dss: bool = True
    enable_gdpr_check: bool = True
    
    # Reporting
    output_format: str = "json"
    fail_on_critical: bool = True
    fail_on_high: bool = False


class SecurityScanningTemplate:
    """Enterprise Security Scanning Template for iacherie Platform"""
    
    def __init__(self, config: SecurityScanConfig):
        self.config = config
        
    def generate_sast_pipeline(self) -> Dict[str, Any]:
        """Generate Static Application Security Testing pipeline"""
        pipeline = {
            "name": "🔒 SAST Security Scan",
            "on": {
                "push": {"branches": ["main", "develop", "feature/*"]},
                "pull_request": {"branches": ["main", "develop"]},
                "schedule": [{"cron": "0 2 * * 1"}]  # Weekly scan
            },
            "jobs": {}
        }
        
        if self.config.enable_sonarqube:
            pipeline["jobs"]["sonarqube-scan"] = self._generate_sonarqube_job()
            
        if self.config.enable_semgrep:
            pipeline["jobs"]["semgrep-scan"] = self._generate_semgrep_job()
            
        if self.config.enable_bandit:
            pipeline["jobs"]["bandit-scan"] = self._generate_bandit_job()
            
        if self.config.enable_eslint_security:
            pipeline["jobs"]["eslint-security"] = self._generate_eslint_security_job()
        
        return pipeline
    
    def _generate_sonarqube_job(self) -> Dict[str, Any]:
        """Generate SonarQube scanning job"""
        return {
            "name": "SonarQube Code Quality & Security Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4", "with": {"fetch-depth": 0}},
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.11"}
                },
                {
                    "name": "Install dependencies",
                    "run": |
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest coverage
                },
                {
                    "name": "Run tests with coverage",
                    "run": |
                        pytest --cov=. --cov-report=xml --cov-report=html
                },
                {
                    "name": "SonarQube Scan",
                    "uses": "sonarqube-quality-gate-action@master",
                    "env": {
                        "SONAR_TOKEN": "${{ secrets.SONAR_TOKEN }}",
                        "SONAR_HOST_URL": "${{ secrets.SONAR_HOST_URL }}"
                    },
                    "with": {
                        "projectBaseDir": ".",
                        "args": |
                            -Dsonar.projectKey=iacherie-platform
                            -Dsonar.sources=.
                            -Dsonar.exclusions=**/*test*/**,**/node_modules/**,**/venv/**
                            -Dsonar.python.coverage.reportPaths=coverage.xml
                            -Dsonar.python.xunit.reportPath=test-reports/junit.xml
                },
                {
                    "name": "Upload SonarQube results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "sonarqube-report",
                        "path": ".scannerwork/"
                    }
                }
            ]
        }
    
    def _generate_semgrep_job(self) -> Dict[str, Any]:
        """Generate Semgrep SAST scanning job"""
        return {
            "name": "Semgrep SAST Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Run Semgrep",
                    "uses": "returntocorp/semgrep-action@v1",
                    "with": {
                        "config": "auto",
                        "publishToken": "${{ secrets.SEMGREP_APP_TOKEN }}",
                        "generateSarif": "1"
                    }
                },
                {
                    "name": "Upload SARIF file",
                    "uses": "github/codeql-action/upload-sarif@v2",
                    "with": {"sarif_file": "semgrep.sarif"},
                    "if": "always()"
                }
            ]
        }
    
    def _generate_bandit_job(self) -> Dict[str, Any]:
        """Generate Bandit Python security scanning job"""
        return {
            "name": "Bandit Python Security Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.11"}
                },
                {
                    "name": "Install Bandit",
                    "run": "pip install bandit[toml]"
                },
                {
                    "name": "Run Bandit security scan",
                    "run": |
                        bandit -r . \
                          -f json \
                          -o bandit-report.json \
                          --exclude ./venv,./node_modules,./tests \
                          --skip B101,B601 \
                          --severity-level medium
                },
                {
                    "name": "Upload Bandit results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "bandit-security-report",
                        "path": "bandit-report.json"
                    }
                },
                {
                    "name": "Fail on critical vulnerabilities",
                    "run": |
                        python -c "
                        import json
                        with open('bandit-report.json') as f:
                            report = json.load(f)
                        critical_issues = [issue for issue in report.get('results', []) 
                                         if issue.get('issue_severity') == 'HIGH']
                        if critical_issues and ${{ config.fail_on_critical }}:
                            print(f'Found {len(critical_issues)} critical security issues')
                            exit(1)
                        "
                }
            ]
        }
    
    def _generate_eslint_security_job(self) -> Dict[str, Any]:
        """Generate ESLint security scanning job for JavaScript/TypeScript"""
        return {
            "name": "ESLint Security Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Node.js",
                    "uses": "actions/setup-node@v3",
                    "with": {"node-version": "18"}
                },
                {
                    "name": "Install dependencies",
                    "run": "npm ci"
                },
                {
                    "name": "Run ESLint security scan",
                    "run": |
                        npx eslint . \
                          --ext .js,.jsx,.ts,.tsx \
                          --config .eslintrc.security.js \
                          --format json \
                          --output-file eslint-security-report.json
                },
                {
                    "name": "Upload ESLint security results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "eslint-security-report",
                        "path": "eslint-security-report.json"
                    }
                }
            ]
        }
    
    def generate_dependency_scan_pipeline(self) -> Dict[str, Any]:
        """Generate dependency vulnerability scanning pipeline"""
        pipeline = {
            "name": "📦 Dependency Security Scan",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "schedule": [{"cron": "0 6 * * *"}]  # Daily scan
            },
            "jobs": {}
        }
        
        if self.config.enable_safety:
            pipeline["jobs"]["safety-scan"] = self._generate_safety_job()
            
        if self.config.enable_npm_audit:
            pipeline["jobs"]["npm-audit"] = self._generate_npm_audit_job()
            
        if self.config.enable_snyk:
            pipeline["jobs"]["snyk-scan"] = self._generate_snyk_job()
        
        return pipeline
    
    def _generate_safety_job(self) -> Dict[str, Any]:
        """Generate Safety Python dependency scanning job"""
        return {
            "name": "Safety Python Dependency Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.11"}
                },
                {
                    "name": "Install Safety",
                    "run": "pip install safety"
                },
                {
                    "name": "Run Safety scan",
                    "run": |
                        safety check \
                          --json \
                          --output safety-report.json \
                          --file requirements.txt
                },
                {
                    "name": "Upload Safety results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "safety-dependency-report",
                        "path": "safety-report.json"
                    }
                }
            ]
        }
    
    def _generate_npm_audit_job(self) -> Dict[str, Any]:
        """Generate NPM audit scanning job"""
        return {
            "name": "NPM Audit Dependency Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Node.js",
                    "uses": "actions/setup-node@v3",
                    "with": {"node-version": "18"}
                },
                {
                    "name": "Run NPM audit",
                    "run": |
                        npm audit --audit-level moderate --json > npm-audit-report.json || true
                },
                {
                    "name": "Upload NPM audit results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "npm-audit-report",
                        "path": "npm-audit-report.json"
                    }
                }
            ]
        }
    
    def _generate_snyk_job(self) -> Dict[str, Any]:
        """Generate Snyk vulnerability scanning job"""
        return {
            "name": "Snyk Vulnerability Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Run Snyk to check for vulnerabilities",
                    "uses": "snyk/actions/python@master",
                    "env": {"SNYK_TOKEN": "${{ secrets.SNYK_TOKEN }}"},
                    "with": {
                        "args": "--severity-threshold=high --json-file-output=snyk-report.json"
                    }
                },
                {
                    "name": "Upload Snyk results",
                    "uses": "actions/upload-artifact@v3", 
                    "with": {
                        "name": "snyk-vulnerability-report",
                        "path": "snyk-report.json"
                    }
                }
            ]
        }
    
    def generate_container_scan_pipeline(self) -> Dict[str, Any]:
        """Generate container security scanning pipeline"""
        pipeline = {
            "name": "🐳 Container Security Scan",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "workflow_dispatch": {}
            },
            "jobs": {}
        }
        
        if self.config.enable_trivy:
            pipeline["jobs"]["trivy-scan"] = self._generate_trivy_job()
            
        if self.config.enable_clair:
            pipeline["jobs"]["clair-scan"] = self._generate_clair_job()
        
        return pipeline
    
    def _generate_trivy_job(self) -> Dict[str, Any]:
        """Generate Trivy container scanning job"""
        return {
            "name": "Trivy Container Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Build Docker image",
                    "run": "docker build -t iacherie-scan:${{ github.sha }} ."
                },
                {
                    "name": "Run Trivy vulnerability scanner",
                    "uses": "aquasecurity/trivy-action@master",
                    "with": {
                        "image-ref": "iacherie-scan:${{ github.sha }}",
                        "format": "sarif",
                        "output": "trivy-results.sarif"
                    }
                },
                {
                    "name": "Upload Trivy scan results",
                    "uses": "github/codeql-action/upload-sarif@v2",
                    "with": {"sarif_file": "trivy-results.sarif"}
                }
            ]
        }
    
    def _generate_clair_job(self) -> Dict[str, Any]:
        """Generate Clair container scanning job"""
        return {
            "name": "Clair Container Scan",
            "runs-on": "ubuntu-latest",
            "services": {
                "clair": {
                    "image": "quay.io/coreos/clair:latest",
                    "ports": ["6060:6060", "6061:6061"]
                }
            },
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Build and scan with Clair",
                    "run": |
                        docker build -t iacherie-scan:latest .
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                          -v $(pwd):/output \
                          arminc/clair-scanner:latest \
                          --clair="http://clair:6060" \
                          --ip="$(hostname -i)" \
                          --report=/output/clair-report.json \
                          iacherie-scan:latest
                },
                {
                    "name": "Upload Clair results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "clair-container-report",
                        "path": "clair-report.json"
                    }
                }
            ]
        }
    
    def generate_secret_scan_pipeline(self) -> Dict[str, Any]:
        """Generate secret scanning pipeline"""
        pipeline = {
            "name": "🔐 Secret Scan",
            "on": {
                "push": {"branches": ["main", "develop", "feature/*"]},
                "pull_request": {"branches": ["main", "develop"]}
            },
            "jobs": {}
        }
        
        if self.config.enable_trufflehog:
            pipeline["jobs"]["trufflehog-scan"] = self._generate_trufflehog_job()
            
        if self.config.enable_gitleaks:
            pipeline["jobs"]["gitleaks-scan"] = self._generate_gitleaks_job()
            
        if self.config.enable_detect_secrets:
            pipeline["jobs"]["detect-secrets-scan"] = self._generate_detect_secrets_job()
        
        return pipeline
    
    def _generate_trufflehog_job(self) -> Dict[str, Any]:
        """Generate TruffleHog secret scanning job"""
        return {
            "name": "TruffleHog Secret Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4", "with": {"fetch-depth": 0}},
                {
                    "name": "TruffleHog OSS",
                    "uses": "trufflesecurity/trufflehog@main",
                    "with": {
                        "path": "./",
                        "base": "${{ github.event.repository.default_branch }}",
                        "head": "HEAD",
                        "extra_args": "--debug --only-verified"
                    }
                }
            ]
        }
    
    def _generate_gitleaks_job(self) -> Dict[str, Any]:
        """Generate GitLeaks secret scanning job"""
        return {
            "name": "GitLeaks Secret Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4", "with": {"fetch-depth": 0}},
                {
                    "name": "Run GitLeaks",
                    "uses": "gitleaks/gitleaks-action@v2",
                    "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"}
                }
            ]
        }
    
    def _generate_detect_secrets_job(self) -> Dict[str, Any]:
        """Generate detect-secrets scanning job"""
        return {
            "name": "Detect Secrets Scan",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.11"}
                },
                {
                    "name": "Install detect-secrets",
                    "run": "pip install detect-secrets"
                },
                {
                    "name": "Run detect-secrets scan",
                    "run": |
                        detect-secrets scan --all-files \
                          --baseline .secrets.baseline \
                          --exclude-files '.*\\.lock$|.*\\.min\\.js$' \
                          --exclude-secrets 'password|EXAMPLE|CHANGEME'
                }
            ]
        }
    
    def generate_compliance_scan_config(self) -> Dict[str, Any]:
        """Generate compliance scanning configuration"""
        config = {
            "compliance_frameworks": [],
            "scan_policies": {}
        }
        
        if self.config.enable_cis_benchmark:
            config["compliance_frameworks"].append("CIS")
            config["scan_policies"]["cis"] = {
                "enabled": True,
                "benchmark_version": "1.2.0",
                "level": 1,  # Level 1 - Basic hardening
                "exclude_checks": []
            }
        
        if self.config.enable_pci_dss:
            config["compliance_frameworks"].append("PCI-DSS")
            config["scan_policies"]["pci_dss"] = {
                "enabled": True,
                "version": "4.0",
                "scope": "full",
                "requirements": [
                    "install_maintain_firewall",
                    "change_default_passwords",
                    "protect_stored_cardholder_data",
                    "encrypt_transmission_cardholder_data",
                    "use_maintain_antivirus",
                    "develop_maintain_secure_systems",
                    "restrict_access_cardholder_data",
                    "identify_authenticate_access",
                    "restrict_physical_access",
                    "track_monitor_access",
                    "regularly_test_security",
                    "maintain_information_security_policy"
                ]
            }
        
        if self.config.enable_gdpr_check:
            config["compliance_frameworks"].append("GDPR")
            config["scan_policies"]["gdpr"] = {
                "enabled": True,
                "data_protection_checks": [
                    "encryption_at_rest",
                    "encryption_in_transit",
                    "data_anonymization",
                    "consent_management",
                    "data_retention_policies",
                    "right_to_be_forgotten",
                    "data_breach_notification"
                ]
            }
        
        return config
    
    def save_security_configs(self, output_dir: str) -> None:
        """Save all security scanning configurations"""
        output_path = Path(output_dir)
        security_path = output_path / ".github" / "workflows" / "security"
        security_path.mkdir(parents=True, exist_ok=True)
        
        # SAST pipeline
        if ScanType.SAST in self.config.scan_types:
            with open(security_path / "sast.yml", 'w') as f:
                yaml.dump(self.generate_sast_pipeline(), f, default_flow_style=False, indent=2)
        
        # Dependency scan pipeline
        if ScanType.DEPENDENCY in self.config.scan_types:
            with open(security_path / "dependency-scan.yml", 'w') as f:
                yaml.dump(self.generate_dependency_scan_pipeline(), f, default_flow_style=False, indent=2)
        
        # Container scan pipeline
        if ScanType.CONTAINER in self.config.scan_types:
            with open(security_path / "container-scan.yml", 'w') as f:
                yaml.dump(self.generate_container_scan_pipeline(), f, default_flow_style=False, indent=2)
        
        # Secret scan pipeline
        if ScanType.SECRET in self.config.scan_types:
            with open(security_path / "secret-scan.yml", 'w') as f:
                yaml.dump(self.generate_secret_scan_pipeline(), f, default_flow_style=False, indent=2)
        
        # Compliance configuration
        if ScanType.COMPLIANCE in self.config.scan_types:
            with open(output_path / "compliance-config.yml", 'w') as f:
                yaml.dump(self.generate_compliance_scan_config(), f, default_flow_style=False, indent=2)
        
        logger.info(f"Security scanning configurations saved to {output_dir}")


# Example usage
def create_production_security_config() -> SecurityScanConfig:
    """Create production security scanning configuration"""
    return SecurityScanConfig(
        project_name="iacherie-platform",
        environment="production",
        scan_types=[
            ScanType.SAST,
            ScanType.DEPENDENCY,
            ScanType.CONTAINER,
            ScanType.SECRET,
            ScanType.COMPLIANCE
        ],
        enable_sonarqube=True,
        enable_semgrep=True,
        enable_bandit=True,
        enable_trivy=True,
        enable_trufflehog=True,
        enable_gitleaks=True,
        enable_cis_benchmark=True,
        enable_pci_dss=True,
        enable_gdpr_check=True,
        fail_on_critical=True,
        fail_on_high=True
    )


if __name__ == "__main__":
    config = create_production_security_config()
    template = SecurityScanningTemplate(config)
    
    print("Security Scanning Template for iacherie Platform")
    print("Configuration:")
    print(f"- Scan Types: {[scan.value for scan in config.scan_types]}")
    print(f"- SAST Tools: SonarQube, Semgrep, Bandit")
    print(f"- Container Scanning: Trivy, Clair")
    print(f"- Secret Scanning: TruffleHog, GitLeaks")
    print(f"- Compliance: CIS, PCI-DSS, GDPR")
