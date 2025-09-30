"""
Security Testing Service for Ainflue Microservices
Automated security testing and vulnerability assessment

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import httpx
import hashlib
import base64
import jwt
from dataclasses import dataclass
import time
import re

logger = logging.getLogger(__name__)


@dataclass
class SecurityTest:
    """Security test definition"""
    name: str
    test_type: str  # auth, injection, xss, csrf, etc.
    target_service: str
    endpoint: str
    method: str = "GET"
    payload: Dict[str, Any] = None
    headers: Dict[str, str] = None
    expected_behavior: str = "block"  # block, allow, log
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class SecurityTestResult:
    """Security test result"""
    test_name: str
    test_type: str
    status: str  # passed, failed, error
    severity: str
    vulnerability_found: bool
    response_code: int = None
    response_data: Any = None
    error_message: str = None
    remediation: str = None
    execution_time: float = 0


class SecurityTestingService:
    """Enterprise security testing service"""

    def __init__(self):
        self.security_tests = {}
        self.test_results = {}
        self.service_endpoints = {}
        self.auth_tokens = {}
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load vulnerability detection patterns"""
        return {
            "sql_injection": [
                r"syntax error",
                r"mysql_fetch",
                r"ORA-\d+",
                r"Microsoft.*ODBC.*SQL",
                r"PostgreSQL.*ERROR",
                r"Warning.*\Wmysql_",
                r"valid MySQL result",
                r"MySQLSyntaxErrorException",
                r"valid PostgreSQL result",
                r"PostgreSQL query failed",
                r"SQLite.*error"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*=",
                r"alert\s*\(",
                r"document\.cookie",
                r"document\.write"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"file://",
                r"/etc/passwd",
                r"\\windows\\system32",
                r"web.config",
                r"\.htaccess"
            ],
            "command_injection": [
                r"sh.*:|cmd.*:|bash.*:",
                r"/bin/",
                r"whoami",
                r"id\s*;",
                r"uname\s*-a",
                r"cat\s+/etc",
                r"ls\s+-la"
            ],
            "ldap_injection": [
                r"Invalid DN syntax",
                r"LDAP.*error",
                r"Bad search filter"
            ],
            "xml_injection": [
                r"XML.*error",
                r"SAXParseException",
                r"xmlns.*="
            ]
        }

    async def register_service(self, service_name: str, base_url: str, auth_token: str = None):
        """Register service for security testing"""
        self.service_endpoints[service_name] = base_url
        if auth_token:
            self.auth_tokens[service_name] = auth_token
        logger.info(f"Registered service for security testing: {service_name}")

    async def add_security_test(self, test: SecurityTest):
        """Add security test"""
        self.security_tests[test.name] = test
        logger.info(f"Added security test: {test.name}")

    async def run_security_test(self, test_name: str) -> SecurityTestResult:
        """Run individual security test"""
        if test_name not in self.security_tests:
            return SecurityTestResult(
                test_name=test_name,
                test_type="unknown",
                status="error",
                severity="unknown",
                vulnerability_found=False,
                error_message="Test not found"
            )
        
        test = self.security_tests[test_name]
        start_time = time.time()
        
        try:
            # Get service endpoint
            if test.target_service not in self.service_endpoints:
                return SecurityTestResult(
                    test_name=test_name,
                    test_type=test.test_type,
                    status="error",
                    severity=test.severity,
                    vulnerability_found=False,
                    error_message=f"Service not registered: {test.target_service}"
                )
            
            base_url = self.service_endpoints[test.target_service]
            url = f"{base_url.rstrip('/')}/{test.endpoint.lstrip('/')}"
            
            # Prepare headers
            headers = test.headers.copy() if test.headers else {}
            if test.target_service in self.auth_tokens:
                headers["Authorization"] = f"Bearer {self.auth_tokens[test.target_service]}"
            
            # Execute test based on type
            result = await self._execute_security_test(test, url, headers)
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error running security test {test_name}: {str(e)}")
            return SecurityTestResult(
                test_name=test_name,
                test_type=test.test_type,
                status="error",
                severity=test.severity,
                vulnerability_found=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )

    async def _execute_security_test(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Execute specific security test"""
        
        if test.test_type == "sql_injection":
            return await self._test_sql_injection(test, url, headers)
        elif test.test_type == "xss":
            return await self._test_xss(test, url, headers)
        elif test.test_type == "auth_bypass":
            return await self._test_auth_bypass(test, url, headers)
        elif test.test_type == "path_traversal":
            return await self._test_path_traversal(test, url, headers)
        elif test.test_type == "command_injection":
            return await self._test_command_injection(test, url, headers)
        elif test.test_type == "csrf":
            return await self._test_csrf(test, url, headers)
        elif test.test_type == "rate_limiting":
            return await self._test_rate_limiting(test, url, headers)
        elif test.test_type == "jwt_security":
            return await self._test_jwt_security(test, url, headers)
        else:
            return await self._test_generic_security(test, url, headers)

    async def _test_sql_injection(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Test for SQL injection vulnerabilities"""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT password FROM users--",
            "admin'--",
            "' OR 1=1--",
            "\"; DROP TABLE users; --",
            "1; SELECT * FROM information_schema.tables--"
        ]
        
        vulnerability_found = False
        response_data = None
        response_code = None
        
        for payload in payloads:
            try:
                # Inject payload into parameters or body
                if test.method.upper() == "GET":
                    test_url = f"{url}?param={payload}"
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.get(test_url, headers=headers)
                else:
                    test_payload = test.payload.copy() if test.payload else {}
                    test_payload["test_param"] = payload
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.post(url, json=test_payload, headers=headers)
                
                response_code = response.status_code
                response_text = response.text.lower()
                
                # Check for SQL injection indicators
                for pattern in self.vulnerability_patterns["sql_injection"]:
                    if re.search(pattern, response_text, re.IGNORECASE):
                        vulnerability_found = True
                        response_data = response.text[:500]  # Truncate for logging
                        break
                
                if vulnerability_found:
                    break
                    
            except Exception as e:
                logger.debug(f"SQL injection test error: {str(e)}")
                continue
        
        return SecurityTestResult(
            test_name=test.name,
            test_type=test.test_type,
            status="failed" if vulnerability_found else "passed",
            severity=test.severity,
            vulnerability_found=vulnerability_found,
            response_code=response_code,
            response_data=response_data,
            remediation="Use parameterized queries and input validation" if vulnerability_found else None
        )

    async def _test_xss(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Test for XSS vulnerabilities"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>"
        ]
        
        vulnerability_found = False
        response_data = None
        response_code = None
        
        for payload in payloads:
            try:
                if test.method.upper() == "GET":
                    test_url = f"{url}?input={payload}"
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.get(test_url, headers=headers)
                else:
                    test_payload = test.payload.copy() if test.payload else {}
                    test_payload["input"] = payload
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.post(url, json=test_payload, headers=headers)
                
                response_code = response.status_code
                response_text = response.text
                
                # Check if payload is reflected without encoding
                if payload in response_text:
                    vulnerability_found = True
                    response_data = response.text[:500]
                    break
                    
            except Exception as e:
                logger.debug(f"XSS test error: {str(e)}")
                continue
        
        return SecurityTestResult(
            test_name=test.name,
            test_type=test.test_type,
            status="failed" if vulnerability_found else "passed",
            severity=test.severity,
            vulnerability_found=vulnerability_found,
            response_code=response_code,
            response_data=response_data,
            remediation="Implement proper input validation and output encoding" if vulnerability_found else None
        )

    async def _test_auth_bypass(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Test for authentication bypass"""
        # Remove auth headers
        test_headers = {k: v for k, v in headers.items() if k.lower() != "authorization"}
        
        vulnerability_found = False
        response_code = None
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if test.method.upper() == "GET":
                    response = await client.get(url, headers=test_headers)
                else:
                    response = await client.post(url, json=test.payload, headers=test_headers)
            
            response_code = response.status_code
            
            # If we get 200 without auth, it's a vulnerability
            if response_code == 200:
                vulnerability_found = True
                
        except Exception as e:
            logger.debug(f"Auth bypass test error: {str(e)}")
        
        return SecurityTestResult(
            test_name=test.name,
            test_type=test.test_type,
            status="failed" if vulnerability_found else "passed",
            severity=test.severity,
            vulnerability_found=vulnerability_found,
            response_code=response_code,
            remediation="Implement proper authentication checks" if vulnerability_found else None
        )

    async def _test_rate_limiting(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Test rate limiting implementation"""
        request_count = 50  # Number of requests to send
        success_count = 0
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                tasks = []
                for _ in range(request_count):
                    if test.method.upper() == "GET":
                        task = client.get(url, headers=headers)
                    else:
                        task = client.post(url, json=test.payload, headers=headers)
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                for response in responses:
                    if not isinstance(response, Exception) and response.status_code == 200:
                        success_count += 1
            
            # If most requests succeed, rate limiting may not be implemented
            vulnerability_found = success_count > (request_count * 0.8)
            
        except Exception as e:
            logger.debug(f"Rate limiting test error: {str(e)}")
            vulnerability_found = False
        
        return SecurityTestResult(
            test_name=test.name,
            test_type=test.test_type,
            status="failed" if vulnerability_found else "passed",
            severity=test.severity,
            vulnerability_found=vulnerability_found,
            response_data=f"Successful requests: {success_count}/{request_count}",
            remediation="Implement proper rate limiting" if vulnerability_found else None
        )

    async def _test_generic_security(self, test: SecurityTest, url: str, headers: Dict[str, str]) -> SecurityTestResult:
        """Generic security test"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if test.method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, json=test.payload, headers=headers)
            
            # Basic security header checks
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Content-Security-Policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            vulnerability_found = len(missing_headers) > 0
            
            return SecurityTestResult(
                test_name=test.name,
                test_type=test.test_type,
                status="failed" if vulnerability_found else "passed",
                severity=test.severity,
                vulnerability_found=vulnerability_found,
                response_code=response.status_code,
                response_data=f"Missing headers: {missing_headers}" if missing_headers else None,
                remediation="Add missing security headers" if vulnerability_found else None
            )
            
        except Exception as e:
            return SecurityTestResult(
                test_name=test.name,
                test_type=test.test_type,
                status="error",
                severity=test.severity,
                vulnerability_found=False,
                error_message=str(e)
            )

    async def run_security_scan(self, service_name: str) -> Dict[str, Any]:
        """Run complete security scan for a service"""
        service_tests = [test for test in self.security_tests.values() 
                        if test.target_service == service_name]
        
        if not service_tests:
            return {"error": f"No security tests found for service: {service_name}"}
        
        start_time = time.time()
        results = {
            "service": service_name,
            "started_at": datetime.utcnow().isoformat(),
            "test_results": [],
            "summary": {
                "total_tests": len(service_tests),
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "vulnerabilities_found": 0,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "low_vulnerabilities": 0
            }
        }
        
        # Run tests
        for test in service_tests:
            result = await self.run_security_test(test.name)
            results["test_results"].append(result.__dict__)
            
            # Update summary
            if result.status == "passed":
                results["summary"]["passed"] += 1
            elif result.status == "failed":
                results["summary"]["failed"] += 1
                if result.vulnerability_found:
                    results["summary"]["vulnerabilities_found"] += 1
                    severity_key = f"{result.severity}_vulnerabilities"
                    if severity_key in results["summary"]:
                        results["summary"][severity_key] += 1
            else:
                results["summary"]["errors"] += 1
        
        results["execution_time"] = time.time() - start_time
        results["completed_at"] = datetime.utcnow().isoformat()
        
        self.test_results[f"{service_name}_security_scan"] = results
        
        return results

    async def health_check(self) -> Dict[str, Any]:
        """Security testing service health check"""
        try:
            return {
                "status": "healthy",
                "registered_services": len(self.service_endpoints),
                "security_tests": len(self.security_tests),
                "test_results": len(self.test_results),
                "vulnerability_patterns": len(self.vulnerability_patterns),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Security testing health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global security testing service instance
security_testing_service = SecurityTestingService()


if __name__ == "__main__":
    async def test_security_service():
        """Test security testing service"""
        print("Testing Security Testing Service...")
        
        # Register service
        await security_testing_service.register_service(
            "test_service", "http://localhost:8000"
        )
        
        # Add security test
        test = SecurityTest(
            name="sql_injection_test",
            test_type="sql_injection",
            target_service="test_service",
            endpoint="/api/users",
            method="GET",
            severity="high"
        )
        await security_testing_service.add_security_test(test)
        
        # Health check
        health = await security_testing_service.health_check()
        print(f"Health: {health}")
        
        print("Security Testing Service ready!")
    
    asyncio.run(test_security_service())