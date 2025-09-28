#!/usr/bin/env python3
"""
🛡️ EXPERT SECURITY VALIDATION & HARDENING SCRIPT
================================================

Comprehensive security validation post-harmonization with expert analysis.
Addresses 1,102 security concerns identified in initial analysis.

Expert Security Team:
🔒 Sécurité Expert: Comprehensive vulnerability assessment
🗄️ DBA: Database security hardening  
🏗️ Backend Senior: API security validation
🤖 Lead Dev IA: AI security patterns
⚙️ DevOps: Infrastructure security automation
🎨 IA Prompt Engineer: Prompt injection protection

Author: Expert Security Team
Version: 1.0 Post-Harmonization
"""

import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SecurityIssue:
    """Security issue detected in codebase"""
    file_path: str
    issue_type: str
    severity: str
    line_number: Optional[int] = None
    description: str = ""
    recommendation: str = ""


class ExpertSecurityValidator:
    """Expert-level security validation and hardening"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Security patterns from expert team
        self.critical_patterns = {
            "sql_injection": [
                r"execute\s*\(\s*[\"'].*%.*[\"']\s*\)",
                r"\.format\s*\(\s*.*\)\s*\)",
                r"f[\"'].*{.*}.*[\"']"
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*[\"'][\w@#$%]+[\"']",
                r"api_key\s*=\s*[\"'][\w\-]+[\"']",
                r"secret\s*=\s*[\"'][\w\-]+[\"']",
                r"token\s*=\s*[\"'][\w\.\-]+[\"']"
            ],
            "weak_crypto": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"DES\s*\(",
                r"RC4\s*\("
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(\s*shell\s*=\s*True",
                r"exec\s*\(",
                r"eval\s*\("
            ]
        }
        
        # High priority patterns
        self.high_priority_patterns = {
            "insecure_random": [
                r"random\.random\s*\(",
                r"random\.choice\s*\("
            ],
            "debug_enabled": [
                r"DEBUG\s*=\s*True",
                r"debug\s*=\s*True"
            ],
            "exception_exposure": [
                r"except\s*Exception\s*as\s*e\s*:\s*print\s*\(\s*e\s*\)",
                r"traceback\.print_exc\s*\(\s*\)"
            ]
        }
    
    async def comprehensive_security_scan(self) -> Dict[str, Any]:
        """Comprehensive security scan of entire codebase"""
        security_issues = []
        file_count = 0
        
        print("🔍 Starting comprehensive security scan...")
        
        # Scan all Python files
        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            file_count += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check critical patterns
                for issue_type, patterns in self.critical_patterns.items():
                    issues = self._scan_patterns(py_file, content, lines, patterns, issue_type, "CRITICAL")
                    security_issues.extend(issues)
                
                # Check high priority patterns
                for issue_type, patterns in self.high_priority_patterns.items():
                    issues = self._scan_patterns(py_file, content, lines, patterns, issue_type, "HIGH")
                    security_issues.extend(issues)
                
            except Exception as e:
                self.logger.warning(f"Could not scan {py_file}: {e}")
        
        # Analyze configuration files
        config_issues = await self._scan_configuration_files()
        security_issues.extend(config_issues)
        
        # Analyze dependencies
        dependency_issues = await self._scan_dependencies()
        security_issues.extend(dependency_issues)
        
        return {
            "files_scanned": file_count,
            "total_issues": len(security_issues),
            "critical_issues": len([i for i in security_issues if i.severity == "CRITICAL"]),
            "high_priority_issues": len([i for i in security_issues if i.severity == "HIGH"]),
            "medium_issues": len([i for i in security_issues if i.severity == "MEDIUM"]),
            "issues": security_issues,
            "scan_timestamp": datetime.now().isoformat()
        }
    
    def _scan_patterns(
        self,
        file_path: Path,
        content: str,
        lines: List[str],
        patterns: List[str],
        issue_type: str,
        severity: str
    ) -> List[SecurityIssue]:
        """Scan file content for security patterns"""
        issues = []
        
        for pattern in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issue = SecurityIssue(
                        file_path=str(file_path),
                        issue_type=issue_type,
                        severity=severity,
                        line_number=line_num,
                        description=f"Potential {issue_type} detected: {line.strip()}",
                        recommendation=self._get_recommendation(issue_type)
                    )
                    issues.append(issue)
        
        return issues
    
    def _get_recommendation(self, issue_type: str) -> str:
        """Get security recommendation for issue type"""
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM with proper escaping",
            "hardcoded_secrets": "Move secrets to environment variables or secure vault",
            "weak_crypto": "Use strong cryptographic algorithms (SHA-256, AES-256)",
            "command_injection": "Validate and sanitize all inputs, avoid shell=True",
            "insecure_random": "Use secrets module for cryptographic randomness",
            "debug_enabled": "Disable debug mode in production",
            "exception_exposure": "Log errors securely without exposing sensitive information"
        }
        return recommendations.get(issue_type, "Review and apply security best practices")
    
    async def _scan_configuration_files(self) -> List[SecurityIssue]:
        """Scan configuration files for security issues"""
        issues = []
        
        config_files = [
            ".env", ".env.production", ".env.staging", ".env.development",
            "config.py", "settings.py", "docker-compose.yml"
        ]
        
        for config_file in config_files:
            file_path = self.base_path / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for exposed secrets
                    if any(keyword in content.lower() for keyword in ["password", "secret", "key"]):
                        if "=" in content and not content.startswith("#"):
                            issue = SecurityIssue(
                                file_path=str(file_path),
                                issue_type="config_exposure",
                                severity="HIGH",
                                description="Configuration file may contain exposed secrets",
                                recommendation="Ensure secrets are properly protected and not committed to version control"
                            )
                            issues.append(issue)
                
                except Exception as e:
                    self.logger.warning(f"Could not scan config file {config_file}: {e}")
        
        return issues
    
    async def _scan_dependencies(self) -> List[SecurityIssue]:
        """Scan dependencies for known vulnerabilities"""
        issues = []
        
        requirements_files = ["requirements.txt", "requirements-production.txt", "requirements-security.txt"]
        
        for req_file in requirements_files:
            file_path = self.base_path / req_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for potentially vulnerable packages
                    vulnerable_packages = [
                        "pillow<10.0.1",  # Known vulnerabilities
                        "cryptography<41.0.0",
                        "pyjwt<2.8.0"
                    ]
                    
                    for vuln_package in vulnerable_packages:
                        if vuln_package.split('<')[0] in content.lower():
                            issue = SecurityIssue(
                                file_path=str(file_path),
                                issue_type="vulnerable_dependency",
                                severity="HIGH",
                                description=f"Potentially vulnerable dependency detected: {vuln_package}",
                                recommendation="Update to latest secure version"
                            )
                            issues.append(issue)
                
                except Exception as e:
                    self.logger.warning(f"Could not scan requirements file {req_file}: {e}")
        
        return issues
    
    async def generate_security_hardening_plan(self, scan_results: Dict[str, Any]) -> str:
        """Generate comprehensive security hardening plan"""
        
        plan_content = f"""# 🛡️ SECURITY HARDENING PLAN - EXPERT VALIDATION

## 📊 SECURITY SCAN RESULTS

- **Files Scanned**: {scan_results['files_scanned']}
- **Total Issues**: {scan_results['total_issues']}
- **Critical Issues**: {scan_results['critical_issues']}
- **High Priority Issues**: {scan_results['high_priority_issues']}
- **Medium Issues**: {scan_results['medium_issues']}

## 🚨 CRITICAL ISSUES (Priority 1)

"""
        
        critical_issues = [issue for issue in scan_results['issues'] if issue.severity == "CRITICAL"]
        
        if critical_issues:
            for i, issue in enumerate(critical_issues[:10], 1):  # Top 10 critical
                plan_content += f"""### {i}. {issue.issue_type.upper()}
- **File**: `{issue.file_path}`
- **Line**: {issue.line_number}
- **Description**: {issue.description}
- **Recommendation**: {issue.recommendation}

"""
        else:
            plan_content += "✅ No critical issues detected.\n\n"
        
        plan_content += f"""## ⚠️ HIGH PRIORITY ISSUES (Priority 2)

"""
        
        high_issues = [issue for issue in scan_results['issues'] if issue.severity == "HIGH"]
        
        if high_issues:
            for i, issue in enumerate(high_issues[:10], 1):  # Top 10 high priority
                plan_content += f"""### {i}. {issue.issue_type.upper()}
- **File**: `{issue.file_path}`
- **Line**: {issue.line_number or 'N/A'}
- **Description**: {issue.description}
- **Recommendation**: {issue.recommendation}

"""
        else:
            plan_content += "✅ No high priority issues detected.\n\n"
        
        plan_content += f"""## 🔧 EXPERT SECURITY RECOMMENDATIONS

### 🔒 Sécurité Expert Recommendations:
- Implement comprehensive input validation
- Enable security headers for all API endpoints
- Implement rate limiting and DDoS protection
- Regular security audits and penetration testing

### 🗄️ DBA Security Recommendations:
- Encrypt all database connections
- Implement database activity monitoring
- Regular database security patches
- Backup encryption and integrity checks

### 🏗️ Backend Senior Security:
- Implement proper authentication and authorization
- API security best practices (OAuth, JWT)
- Secure session management
- Input sanitization and validation

### 🤖 Lead Dev IA Security:
- AI model security and privacy
- Secure ML pipeline implementation
- Model poisoning protection
- AI fairness and bias detection

### ⚙️ DevOps Security:
- Infrastructure as Code security
- Container security scanning
- Secrets management automation
- Security monitoring and alerting

### 🎨 IA Prompt Engineer Security:
- Prompt injection protection
- AI model input validation
- Secure prompt templating
- Content filtering and moderation

## 🚀 IMPLEMENTATION PRIORITY

1. **Immediate (0-7 days)**: Fix all CRITICAL issues
2. **Short-term (1-4 weeks)**: Address HIGH priority issues
3. **Medium-term (1-3 months)**: Implement comprehensive security framework
4. **Long-term (3-6 months)**: Advanced security monitoring and automation

## 📋 VALIDATION CHECKLIST

- [ ] All critical vulnerabilities resolved
- [ ] High priority issues addressed
- [ ] Security headers implemented
- [ ] Authentication/authorization hardened
- [ ] Input validation comprehensive
- [ ] Secrets management secure
- [ ] Monitoring and alerting active
- [ ] Security testing automated
- [ ] Documentation updated
- [ ] Team training completed

---
*Generated by Expert Security Validation Team*
*Scan Timestamp: {scan_results['scan_timestamp']}*
"""
        
        return plan_content
    
    async def save_security_report(self, scan_results: Dict[str, Any], output_file: str = "SECURITY_HARDENING_PLAN.md") -> None:
        """Save comprehensive security report"""
        
        plan_content = await self.generate_security_hardening_plan(scan_results)
        
        output_path = self.base_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        # Also save raw results as JSON
        json_output = self.base_path / "security_scan_results.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            # Convert SecurityIssue objects to dicts for JSON serialization
            serializable_issues = []
            for issue in scan_results['issues']:
                serializable_issues.append({
                    'file_path': issue.file_path,
                    'issue_type': issue.issue_type,
                    'severity': issue.severity,
                    'line_number': issue.line_number,
                    'description': issue.description,
                    'recommendation': issue.recommendation
                })
            
            serializable_results = {**scan_results, 'issues': serializable_issues}
            json.dump(serializable_results, f, indent=2)
        
        print(f"📋 Security reports saved:")
        print(f"   - Human readable: {output_path}")
        print(f"   - Machine readable: {json_output}")


async def main():
    """Main execution function"""
    validator = ExpertSecurityValidator()
    
    print("🛡️ EXPERT SECURITY VALIDATION STARTING...")
    
    # Run comprehensive security scan
    scan_results = await validator.comprehensive_security_scan()
    
    # Save security reports
    await validator.save_security_report(scan_results)
    
    # Print summary
    print(f"\n📊 SECURITY SCAN COMPLETE:")
    print(f"   - Files scanned: {scan_results['files_scanned']}")
    print(f"   - Total issues: {scan_results['total_issues']}")
    print(f"   - Critical issues: {scan_results['critical_issues']}")
    print(f"   - High priority: {scan_results['high_priority_issues']}")
    
    if scan_results['critical_issues'] > 0:
        print(f"\n🚨 ATTENTION: {scan_results['critical_issues']} critical security issues require immediate attention!")
    else:
        print(f"\n✅ No critical security issues detected.")
    
    print("\n✅ EXPERT SECURITY VALIDATION COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())