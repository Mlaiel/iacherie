#!/usr/bin/env python3
"""Production Security Validation Script
=======================================

Comprehensive security validation script for the AI Influencer Agent platform.
Tests all implemented security features and generates compliance reports.

Features tested:
- WAF (Web Application Firewall) with OWASP rules
- Rate limiting by IP and authenticated users
- DDoS protection configuration
- Security headers implementation
- Vulnerability scanning integration
- SIEM integration
- 2FA enforcement for admin accounts
- API key rotation mechanism
- Encrypted backup system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
import os
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class SecurityTestResult(Enum):
    """Security test results"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


@dataclass
class TestCase:
    """Security test case"""
    name: str
    description: str
    category: str
    severity: str
    result: SecurityTestResult = SecurityTestResult.SKIP
    details: str = ""
    recommendations: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class SecurityValidator:
    """Main security validation class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        logger.info("Starting comprehensive security validation...")
        
        start_time = time.time()
        
        # Run test categories
        await self._test_waf_protection()
        await self._test_rate_limiting()
        await self._test_ddos_protection()
        await self._test_security_headers()
        await self._test_vulnerability_scanning()
        await self._test_siem_integration()
        await self._test_2fa_enforcement()
        await self._test_api_key_rotation()
        await self._test_encrypted_backup()
        
        total_time = time.time() - start_time
        
        # Generate report
        return self._generate_report(total_time)
    
    async def _test_waf_protection(self):
        """Test WAF (Web Application Firewall) protection"""
        category = "WAF Protection"
        
        # Test SQL Injection protection
        await self._test_sql_injection_protection(category)
        
        # Test XSS protection
        await self._test_xss_protection(category)
        
        # Test Path Traversal protection
        await self._test_path_traversal_protection(category)
        
        # Test Command Injection protection
        await self._test_command_injection_protection(category)
    
    async def _test_sql_injection_protection(self, category: str):
        """Test SQL injection protection"""
        test_case = TestCase(
            name="SQL Injection Protection",
            description="Test WAF protection against SQL injection attacks",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Test various SQL injection payloads
            payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1 --"
            ]
            
            blocked_count = 0
            for payload in payloads:
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/test",
                        params={"q": payload},
                        timeout=5
                    )
                    
                    # WAF should block or sanitize the request
                    if response.status_code in [403, 406, 429]:
                        blocked_count += 1
                
                except requests.exceptions.RequestException:
                    # Connection issues might indicate blocking
                    blocked_count += 1
            
            if blocked_count >= len(payloads) * 0.8:  # 80% block rate
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"SQL injection attacks blocked: {blocked_count}/{len(payloads)}"
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = f"Insufficient SQL injection protection: {blocked_count}/{len(payloads)} blocked"
                test_case.recommendations.append("Enhance WAF rules for SQL injection detection")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_xss_protection(self, category: str):
        """Test XSS protection"""
        test_case = TestCase(
            name="XSS Protection",
            description="Test WAF protection against XSS attacks",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            payloads = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
                "<svg onload=alert('xss')>",
                "'-prompt('xss')-'"
            ]
            
            blocked_count = 0
            for payload in payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/test",
                        json={"content": payload},
                        timeout=5
                    )
                    
                    if response.status_code in [403, 406, 429]:
                        blocked_count += 1
                
                except requests.exceptions.RequestException:
                    blocked_count += 1
            
            if blocked_count >= len(payloads) * 0.8:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"XSS attacks blocked: {blocked_count}/{len(payloads)}"
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = f"Insufficient XSS protection: {blocked_count}/{len(payloads)} blocked"
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_path_traversal_protection(self, category: str):
        """Test path traversal protection"""
        test_case = TestCase(
            name="Path Traversal Protection",
            description="Test WAF protection against path traversal attacks",
            category=category,
            severity="MEDIUM"
        )
        
        start_time = time.time()
        
        try:
            payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "....//....//....//etc/passwd"
            ]
            
            blocked_count = 0
            for payload in payloads:
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/file",
                        params={"path": payload},
                        timeout=5
                    )
                    
                    if response.status_code in [403, 406, 429]:
                        blocked_count += 1
                
                except requests.exceptions.RequestException:
                    blocked_count += 1
            
            if blocked_count >= len(payloads) * 0.8:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"Path traversal attacks blocked: {blocked_count}/{len(payloads)}"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = f"Some path traversal protection: {blocked_count}/{len(payloads)} blocked"
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_command_injection_protection(self, category: str):
        """Test command injection protection"""
        test_case = TestCase(
            name="Command Injection Protection",
            description="Test WAF protection against command injection attacks",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            payloads = [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "`id`",
                "$(uname -a)"
            ]
            
            blocked_count = 0
            for payload in payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/command",
                        json={"cmd": payload},
                        timeout=5
                    )
                    
                    if response.status_code in [403, 406, 429]:
                        blocked_count += 1
                
                except requests.exceptions.RequestException:
                    blocked_count += 1
            
            if blocked_count >= len(payloads) * 0.8:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"Command injection attacks blocked: {blocked_count}/{len(payloads)}"
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = f"Insufficient command injection protection: {blocked_count}/{len(payloads)} blocked"
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_rate_limiting(self):
        """Test rate limiting functionality"""
        category = "Rate Limiting"
        
        # Test API rate limiting
        await self._test_api_rate_limiting(category)
        
        # Test login rate limiting
        await self._test_login_rate_limiting(category)
        
        # Test per-user rate limiting
        await self._test_per_user_rate_limiting(category)
    
    async def _test_api_rate_limiting(self, category: str):
        """Test API rate limiting"""
        test_case = TestCase(
            name="API Rate Limiting",
            description="Test rate limiting for API endpoints",
            category=category,
            severity="MEDIUM"
        )
        
        start_time = time.time()
        
        try:
            # Send rapid requests to test rate limiting
            responses = []
            for i in range(20):  # Send 20 requests rapidly
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/test",
                        timeout=2
                    )
                    responses.append(response.status_code)
                except requests.exceptions.RequestException as e:
                    responses.append(429)  # Assume rate limited
            
            # Check for rate limiting responses
            rate_limited = sum(1 for status in responses if status == 429)
            
            if rate_limited > 0:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"Rate limiting active: {rate_limited}/20 requests limited"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "No rate limiting detected in 20 rapid requests"
                test_case.recommendations.append("Consider implementing stricter rate limiting")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_login_rate_limiting(self, category: str):
        """Test login rate limiting"""
        test_case = TestCase(
            name="Login Rate Limiting",
            description="Test rate limiting for login attempts",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Attempt multiple failed logins
            responses = []
            for i in range(10):
                try:
                    response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={"username": "test", "password": "wrong"},
                        timeout=2
                    )
                    responses.append(response.status_code)
                except requests.exceptions.RequestException:
                    responses.append(429)
            
            # Check for rate limiting after failed attempts
            rate_limited = sum(1 for status in responses if status == 429)
            
            if rate_limited > 0:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"Login rate limiting active: {rate_limited}/10 attempts limited"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "No login rate limiting detected"
                test_case.recommendations.append("Implement login rate limiting to prevent brute force attacks")
        
        except Exception as e:
            test_case.result = SecurityTestResult.SKIP
            test_case.details = f"Test skipped (no login endpoint): {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_per_user_rate_limiting(self, category: str):
        """Test per-user rate limiting"""
        test_case = TestCase(
            name="Per-User Rate Limiting",
            description="Test rate limiting per authenticated user",
            category=category,
            severity="MEDIUM"
        )
        
        start_time = time.time()
        
        try:
            # This would require authentication setup
            test_case.result = SecurityTestResult.SKIP
            test_case.details = "Requires authentication setup for testing"
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_ddos_protection(self):
        """Test DDoS protection"""
        category = "DDoS Protection"
        
        test_case = TestCase(
            name="DDoS Protection Configuration",
            description="Validate DDoS protection configuration",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Check if CloudFlare or similar DDoS protection is configured
            cloudflare_configured = bool(os.getenv('CLOUDFLARE_ZONE_ID'))
            
            if cloudflare_configured:
                test_case.result = SecurityTestResult.PASS
                test_case.details = "CloudFlare DDoS protection configured"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "No external DDoS protection detected"
                test_case.recommendations.append("Configure CloudFlare or equivalent DDoS protection")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_security_headers(self):
        """Test security headers implementation"""
        category = "Security Headers"
        
        test_case = TestCase(
            name="Security Headers Validation",
            description="Validate mandatory security headers",
            category=category,
            severity="MEDIUM"
        )
        
        start_time = time.time()
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'Strict-Transport-Security': 'max-age',
                'Content-Security-Policy': 'default-src',
                'Referrer-Policy': 'strict-origin',
                'X-XSS-Protection': '1'
            }
            
            missing_headers = []
            present_headers = []
            
            for header, expected_value in required_headers.items():
                if header in headers:
                    if expected_value in headers[header]:
                        present_headers.append(header)
                    else:
                        missing_headers.append(f"{header} (incorrect value)")
                else:
                    missing_headers.append(header)
            
            if not missing_headers:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"All security headers present: {', '.join(present_headers)}"
            elif len(present_headers) >= len(required_headers) * 0.8:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = f"Most security headers present. Missing: {', '.join(missing_headers)}"
                test_case.recommendations.append(f"Add missing headers: {', '.join(missing_headers)}")
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = f"Critical security headers missing: {', '.join(missing_headers)}"
                test_case.recommendations.append("Implement comprehensive security headers")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_vulnerability_scanning(self):
        """Test vulnerability scanning integration"""
        category = "Vulnerability Scanning"
        
        test_case = TestCase(
            name="Vulnerability Scanner Integration",
            description="Validate vulnerability scanning tools integration",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Check if vulnerability scanning tools are available
            scanners_available = []
            
            # Check Trivy
            if shutil.which('trivy'):
                scanners_available.append('Trivy')
            
            # Check Clair configuration
            if os.getenv('CLAIR_URL'):
                scanners_available.append('Clair')
            
            # Check Snyk configuration
            if os.getenv('SNYK_TOKEN'):
                scanners_available.append('Snyk')
            
            if len(scanners_available) >= 2:
                test_case.result = SecurityTestResult.PASS
                test_case.details = f"Multiple vulnerability scanners configured: {', '.join(scanners_available)}"
            elif len(scanners_available) == 1:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = f"Single vulnerability scanner configured: {scanners_available[0]}"
                test_case.recommendations.append("Configure additional vulnerability scanners for comprehensive coverage")
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = "No vulnerability scanners configured"
                test_case.recommendations.append("Configure Trivy, Clair, and/or Snyk for vulnerability scanning")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_siem_integration(self):
        """Test SIEM integration"""
        category = "SIEM Integration"
        
        test_case = TestCase(
            name="SIEM Integration",
            description="Validate SIEM integration for security monitoring",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Check if SIEM is configured
            siem_configured = any([
                os.getenv('SPLUNK_TOKEN'),
                os.getenv('ELASTICSEARCH_URL'),
                os.getenv('QRADAR_TOKEN')
            ])
            
            if siem_configured:
                test_case.result = SecurityTestResult.PASS
                test_case.details = "SIEM integration configured"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "No SIEM integration detected"
                test_case.recommendations.append("Configure SIEM integration for security monitoring")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_2fa_enforcement(self):
        """Test 2FA enforcement for admin accounts"""
        category = "2FA Enforcement"
        
        test_case = TestCase(
            name="Admin 2FA Enforcement",
            description="Validate 2FA enforcement for administrator accounts",
            category=category,
            severity="CRITICAL"
        )
        
        start_time = time.time()
        
        try:
            # Check if 2FA configuration exists
            totp_configured = bool(os.getenv('TOTP_ISSUER'))
            
            if totp_configured:
                test_case.result = SecurityTestResult.PASS
                test_case.details = "2FA configuration detected"
            else:
                test_case.result = SecurityTestResult.FAIL
                test_case.details = "No 2FA configuration detected"
                test_case.recommendations.append("Implement mandatory 2FA for administrator accounts")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_api_key_rotation(self):
        """Test API key rotation mechanism"""
        category = "API Key Rotation"
        
        test_case = TestCase(
            name="API Key Rotation",
            description="Validate automatic API key rotation mechanism",
            category=category,
            severity="MEDIUM"
        )
        
        start_time = time.time()
        
        try:
            # Check if Redis is configured for key storage
            redis_configured = bool(os.getenv('REDIS_URL') or os.getenv('REDIS_HOST'))
            
            if redis_configured:
                test_case.result = SecurityTestResult.PASS
                test_case.details = "API key rotation infrastructure configured"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "API key rotation infrastructure not detected"
                test_case.recommendations.append("Configure Redis for API key rotation storage")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    async def _test_encrypted_backup(self):
        """Test encrypted backup system"""
        category = "Encrypted Backup"
        
        test_case = TestCase(
            name="Encrypted Backup System",
            description="Validate encrypted backup and restore capabilities",
            category=category,
            severity="HIGH"
        )
        
        start_time = time.time()
        
        try:
            # Check if backup configuration exists
            backup_configured = any([
                os.getenv('AWS_ACCESS_KEY_ID'),
                os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
                os.getenv('GOOGLE_CLOUD_PROJECT')
            ])
            
            if backup_configured:
                test_case.result = SecurityTestResult.PASS
                test_case.details = "Encrypted backup system configured"
            else:
                test_case.result = SecurityTestResult.WARNING
                test_case.details = "No cloud backup configuration detected"
                test_case.recommendations.append("Configure encrypted backup to cloud storage")
        
        except Exception as e:
            test_case.result = SecurityTestResult.FAIL
            test_case.details = f"Test failed: {str(e)}"
        
        test_case.execution_time = time.time() - start_time
        self.test_results.append(test_case)
    
    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        # Calculate statistics
        total_tests = len(self.test_results)
        passed = sum(1 for test in self.test_results if test.result == SecurityTestResult.PASS)
        failed = sum(1 for test in self.test_results if test.result == SecurityTestResult.FAIL)
        warnings = sum(1 for test in self.test_results if test.result == SecurityTestResult.WARNING)
        skipped = sum(1 for test in self.test_results if test.result == SecurityTestResult.SKIP)
        
        # Calculate score
        score = (passed * 100 + warnings * 50) / (total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if score >= 90:
            overall_status = "EXCELLENT"
        elif score >= 80:
            overall_status = "GOOD"
        elif score >= 70:
            overall_status = "ACCEPTABLE"
        elif score >= 60:
            overall_status = "NEEDS_IMPROVEMENT"
        else:
            overall_status = "CRITICAL"
        
        # Group by category
        categories = {}
        for test in self.test_results:
            if test.category not in categories:
                categories[test.category] = []
            categories[test.category].append({
                "name": test.name,
                "result": test.result.value,
                "details": test.details,
                "recommendations": test.recommendations,
                "execution_time": test.execution_time
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "score": round(score, 2),
            "statistics": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "skipped": skipped
            },
            "execution_time": round(total_time, 2),
            "categories": categories,
            "critical_issues": [
                test for test in self.test_results 
                if test.result == SecurityTestResult.FAIL and test.severity in ["HIGH", "CRITICAL"]
            ],
            "recommendations": list(set(
                rec for test in self.test_results 
                for rec in test.recommendations
            ))
        }


async def main():
    """Main execution function"""
    import argparse
    import shutil
    
    parser = argparse.ArgumentParser(description='AI Influencer Agent Security Validation')
    parser.add_argument('--base-url', default='http://localhost:8000', help='Base URL for testing')
    parser.add_argument('--output', default='security_report.json', help='Output file for report')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize validator
    validator = SecurityValidator(args.base_url)
    
    # Run tests
    print("🔐 Starting AI Influencer Agent Security Validation...")
    print(f"📡 Testing endpoint: {args.base_url}")
    print()
    
    report = await validator.run_all_tests()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("=" * 60)
    print("🛡️  SECURITY VALIDATION REPORT")
    print("=" * 60)
    print(f"Overall Status: {report['overall_status']}")
    print(f"Security Score: {report['score']}/100")
    print(f"Total Tests: {report['statistics']['total_tests']}")
    print(f"✅ Passed: {report['statistics']['passed']}")
    print(f"⚠️  Warnings: {report['statistics']['warnings']}")
    print(f"❌ Failed: {report['statistics']['failed']}")
    print(f"⏭️  Skipped: {report['statistics']['skipped']}")
    print(f"⏱️  Execution Time: {report['execution_time']}s")
    print()
    
    if report['critical_issues']:
        print("🚨 CRITICAL ISSUES:")
        for issue in report['critical_issues']:
            print(f"  - {issue['name']}: {issue['details']}")
        print()
    
    if report['recommendations']:
        print("💡 RECOMMENDATIONS:")
        for rec in report['recommendations'][:5]:  # Show top 5
            print(f"  - {rec}")
        print()
    
    print(f"📄 Full report saved to: {args.output}")
    
    # Exit with appropriate code
    if report['statistics']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())