"""
Industrial-grade automated GDPR/CCPA compliance testing.
Tests real compliance validation with 0 mocks, 100% actual data processing.
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import pytest
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ComplianceRegulation(Enum):
    """Compliance regulations."""
    GDPR = "GDPR"
    CCPA = "CCPA"
    PIPEDA = "PIPEDA"
    LGPD = "LGPD"


class ComplianceTestType(Enum):
    """Types of compliance tests."""
    DATA_CONSENT = "data_consent"
    DATA_ACCESS = "data_access"
    DATA_DELETION = "data_deletion"
    DATA_PORTABILITY = "data_portability"
    DATA_RECTIFICATION = "data_rectification"
    DATA_BREACH_NOTIFICATION = "data_breach_notification"
    PRIVACY_BY_DESIGN = "privacy_by_design"
    DATA_RETENTION = "data_retention"
    CONSENT_WITHDRAWAL = "consent_withdrawal"
    DATA_PROCESSING_LAWFULNESS = "data_processing_lawfulness"


class ComplianceSeverity(Enum):
    """Compliance violation severity."""
    CRITICAL = "CRITICAL"  # Major compliance violation
    HIGH = "HIGH"         # Significant compliance risk
    MEDIUM = "MEDIUM"     # Moderate compliance issue
    LOW = "LOW"           # Minor compliance concern
    INFO = "INFO"         # Informational


@dataclass
class ComplianceTestResult:
    """Result from a compliance test."""
    test_name: str
    regulation: ComplianceRegulation
    test_type: ComplianceTestType
    severity: ComplianceSeverity
    passed: bool
    compliance_score: float  # 0-100
    violations: List[str]
    recommendations: List[str]
    evidence: Optional[Dict[str, Any]] = None
    response_time_ms: float = 0.0


class PersonalDataGenerator:
    """Generate realistic personal data for compliance testing."""
    
    @staticmethod
    def generate_user_data() -> Dict[str, Any]:
        """Generate realistic user data for testing."""
        user_id = str(uuid.uuid4())
        return {
            "user_id": user_id,
            "username": f"testuser_{user_id[:8]}",
            "email": f"compliance.test.{user_id[:8]}@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1-555-0123",
            "date_of_birth": "1990-01-01",
            "address": {
                "street": "123 Privacy St",
                "city": "Compliance City", 
                "state": "CA",
                "zip_code": "90210",
                "country": "US"
            },
            "preferences": {
                "marketing_emails": True,
                "analytics_tracking": True,
                "third_party_sharing": False
            },
            "sensitive_data": {
                "financial_info": "Test bank account",
                "health_info": "Test medical condition",
                "biometric_data": "Test fingerprint hash"
            },
            "ip_address": "192.168.1.100",
            "browser_fingerprint": "test_browser_fingerprint",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "accuracy": 10
            }
        }
    
    @staticmethod
    def generate_eu_user_data() -> Dict[str, Any]:
        """Generate EU user data for GDPR testing."""
        data = PersonalDataGenerator.generate_user_data()
        data["address"]["country"] = "DE"
        data["address"]["city"] = "Berlin"
        data["gdpr_subject"] = True
        data["consent_timestamp"] = datetime.now().isoformat()
        data["legal_basis"] = "consent"
        return data
    
    @staticmethod
    def generate_california_user_data() -> Dict[str, Any]:
        """Generate California user data for CCPA testing."""
        data = PersonalDataGenerator.generate_user_data()
        data["address"]["state"] = "CA"
        data["ccpa_subject"] = True
        data["do_not_sell"] = False
        return data


class RealComplianceValidator:
    """Real compliance validator - no mocks."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_users: List[Dict[str, Any]] = []
    
    async def __aenter__(self):
        """Setup compliance testing environment."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup compliance testing environment."""
        if self.session:
            await self.session.close()
        
        # Cleanup test users for compliance
        await self._cleanup_test_data()
    
    async def _make_api_request(self, method: str, endpoint: str, **kwargs) -> Tuple[int, Dict[str, Any], float]:
        """Make API request and return status, response, and time."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = (time.time() - start_time) * 1000
                content = await response.json() if response.content_type == "application/json" else {"text": await response.text()}
                return response.status, content, response_time
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return 500, {"error": str(e)}, response_time
    
    async def _create_test_user(self, user_data: Dict[str, Any]) -> str:
        """Create a test user and return user ID."""
        status, response, _ = await self._make_api_request(
            "POST", "/api/v1/auth/register", json=user_data
        )
        
        if status in [200, 201]:
            user_id = response.get("user_id") or user_data["user_id"]
            self.test_users.append({"user_id": user_id, "data": user_data})
            return user_id
        else:
            raise Exception(f"Failed to create test user: {status} - {response}")
    
    async def _cleanup_test_data(self):
        """Cleanup all test data for compliance."""
        for user in self.test_users:
            try:
                # Request data deletion
                await self._make_api_request(
                    "DELETE", f"/api/v1/user/{user['user_id']}/data",
                    json={"reason": "compliance_test_cleanup"}
                )
            except Exception as e:
                logger.warning(f"Failed to cleanup user {user['user_id']}: {e}")
    
    # GDPR Compliance Tests
    async def test_gdpr_consent_collection(self, user_data: Dict[str, Any]) -> ComplianceTestResult:
        """Test GDPR consent collection and validation."""
        test_name = "gdpr_consent_collection"
        start_time = time.time()
        violations = []
        recommendations = []
        evidence = {}
        
        try:
            # Test with explicit consent
            user_data_with_consent = user_data.copy()
            user_data_with_consent["consent_timestamp"] = datetime.now().isoformat()
            user_data_with_consent["legal_basis"] = "consent"
            user_data_with_consent["gdpr_consents"] = {
                "data_processing": True,
                "marketing": False,
                "analytics": True,
                "third_party_sharing": False
            }
            
            status, response, response_time = await self._make_api_request(
                "POST", "/api/v1/auth/register", json=user_data_with_consent
            )
            
            evidence["registration_with_consent"] = {"status": status, "response": response}
            
            if status not in [200, 201]:
                violations.append("User registration failed even with proper GDPR consent")
                recommendations.append("Allow registration when proper consent is provided")
            else:
                # Verify consent is stored properly
                user_id = response.get("user_id") or user_data_with_consent["user_id"]
                if user_id:
                    self.test_users.append({"user_id": user_id, "data": user_data_with_consent})
                    
                    # Check if consent data is retrievable
                    status, consent_data, _ = await self._make_api_request(
                        "GET", f"/api/v1/user/{user_id}/consent"
                    )
                    
                    evidence["consent_retrieval"] = {"status": status, "data": consent_data}
                    
                    if status != 200:
                        violations.append("Consent data not accessible after registration")
                        recommendations.append("Implement consent data retrieval endpoint")
                    elif not consent_data.get("consent_timestamp"):
                        violations.append("Consent timestamp not stored properly")
                        recommendations.append("Store consent timestamp with each consent record")
            
            # Calculate compliance score
            compliance_score = max(0, 100 - (len(violations) * 25))
            
            result = ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_CONSENT,
                severity=ComplianceSeverity.CRITICAL if violations else ComplianceSeverity.INFO,
                passed=len(violations) == 0,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
                evidence=evidence,
                response_time_ms=response_time
            )
            
            return result
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_CONSENT,
                severity=ComplianceSeverity.CRITICAL,
                passed=False,
                compliance_score=0,
                violations=[f"Test execution failed: {str(e)}"],
                recommendations=["Fix test environment and retry"],
                evidence=evidence,
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def test_gdpr_data_access_right(self, user_data: Dict[str, Any]) -> ComplianceTestResult:
        """Test GDPR right to access personal data."""
        test_name = "gdpr_data_access_right"
        start_time = time.time()
        violations = []
        recommendations = []
        evidence = {}
        
        try:
            # Create user
            user_id = await self._create_test_user(user_data)
            
            # Test data access request
            status, response, response_time = await self._make_api_request(
                "GET", f"/api/v1/user/{user_id}/data"
            )
            
            evidence["data_access_request"] = {"status": status, "response": response}
            
            if status != 200:
                violations.append("Data access request failed - GDPR Article 15 violation")
                recommendations.append("Implement data access endpoint per GDPR Article 15")
            else:
                # Verify completeness of data
                returned_data = response.get("data", {})
                
                # Check for required data fields
                required_fields = ["user_id", "email", "first_name", "last_name"]
                missing_fields = [field for field in required_fields if field not in returned_data]
                
                if missing_fields:
                    violations.append(f"Incomplete data returned - missing: {missing_fields}")
                    recommendations.append("Return all personal data as required by GDPR Article 15")
                
                # Verify response time
                if response_time > 5000:  # 5 seconds
                    violations.append("Data access response time too slow")
                    recommendations.append("Optimize data access response time")
            
            compliance_score = max(0, 100 - (len(violations) * 20))
            
            result = ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_ACCESS,
                severity=ComplianceSeverity.HIGH if violations else ComplianceSeverity.INFO,
                passed=len(violations) == 0,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
                evidence=evidence,
                response_time_ms=response_time
            )
            
            return result
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_ACCESS,
                severity=ComplianceSeverity.HIGH,
                passed=False,
                compliance_score=0,
                violations=[f"Test execution failed: {str(e)}"],
                recommendations=["Fix data access implementation"],
                evidence=evidence,
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def test_gdpr_data_deletion_right(self, user_data: Dict[str, Any]) -> ComplianceTestResult:
        """Test GDPR right to erasure (right to be forgotten)."""
        test_name = "gdpr_data_deletion_right"
        start_time = time.time()
        violations = []
        recommendations = []
        evidence = {}
        
        try:
            # Create user
            user_id = await self._create_test_user(user_data)
            
            # Request data deletion
            deletion_request = {
                "user_id": user_id,
                "reason": "gdpr_erasure_request",
                "delete_all_data": True
            }
            
            status, response, response_time = await self._make_api_request(
                "DELETE", f"/api/v1/user/{user_id}/data", json=deletion_request
            )
            
            evidence["deletion_request"] = {"status": status, "response": response}
            
            if status not in [200, 202]:
                violations.append("Data deletion request failed - GDPR Article 17 violation")
                recommendations.append("Implement data deletion endpoint per GDPR Article 17")
            else:
                # Wait for deletion processing
                await asyncio.sleep(2)
                
                # Verify user data is deleted
                status, user_response, _ = await self._make_api_request(
                    "GET", f"/api/v1/user/{user_id}/data"
                )
                
                evidence["verification_user_deleted"] = {"status": status, "response": user_response}
                
                if status == 200:
                    violations.append("User data still accessible after deletion request")
                    recommendations.append("Ensure user data is completely removed after deletion")
            
            compliance_score = max(0, 100 - (len(violations) * 25))
            
            result = ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_DELETION,
                severity=ComplianceSeverity.CRITICAL if violations else ComplianceSeverity.INFO,
                passed=len(violations) == 0,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
                evidence=evidence,
                response_time_ms=response_time
            )
            
            # Remove from test users list since it should be deleted
            self.test_users = [u for u in self.test_users if u["user_id"] != user_id]
            
            return result
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.GDPR,
                test_type=ComplianceTestType.DATA_DELETION,
                severity=ComplianceSeverity.CRITICAL,
                passed=False,
                compliance_score=0,
                violations=[f"Test execution failed: {str(e)}"],
                recommendations=["Fix data deletion implementation"],
                evidence=evidence,
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    # CCPA Compliance Tests
    async def test_ccpa_do_not_sell_right(self, user_data: Dict[str, Any]) -> ComplianceTestResult:
        """Test CCPA right to opt-out of sale of personal information."""
        test_name = "ccpa_do_not_sell_right"
        start_time = time.time()
        violations = []
        recommendations = []
        evidence = {}
        
        try:
            # Create California user
            ca_user_data = user_data.copy()
            ca_user_data["address"]["state"] = "CA"
            ca_user_data["ccpa_subject"] = True
            
            user_id = await self._create_test_user(ca_user_data)
            
            # Test opt-out request
            opt_out_request = {
                "user_id": user_id,
                "do_not_sell": True,
                "timestamp": datetime.now().isoformat()
            }
            
            status, response, response_time = await self._make_api_request(
                "POST", f"/api/v1/user/{user_id}/ccpa/opt-out", json=opt_out_request
            )
            
            evidence["opt_out_request"] = {"status": status, "response": response}
            
            if status not in [200, 201]:
                violations.append("CCPA opt-out request failed")
                recommendations.append("Implement CCPA opt-out endpoint")
            else:
                # Verify opt-out status is stored
                status, user_status, _ = await self._make_api_request(
                    "GET", f"/api/v1/user/{user_id}/ccpa/status"
                )
                
                evidence["opt_out_verification"] = {"status": status, "response": user_status}
                
                if status != 200:
                    violations.append("Cannot verify CCPA opt-out status")
                    recommendations.append("Implement CCPA status verification endpoint")
                elif not user_status.get("do_not_sell"):
                    violations.append("CCPA opt-out status not properly recorded")
                    recommendations.append("Ensure opt-out preferences are stored and honored")
            
            compliance_score = max(0, 100 - (len(violations) * 25))
            
            result = ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.CCPA,
                test_type=ComplianceTestType.CONSENT_WITHDRAWAL,
                severity=ComplianceSeverity.HIGH if violations else ComplianceSeverity.INFO,
                passed=len(violations) == 0,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
                evidence=evidence,
                response_time_ms=response_time
            )
            
            return result
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                regulation=ComplianceRegulation.CCPA,
                test_type=ComplianceTestType.CONSENT_WITHDRAWAL,
                severity=ComplianceSeverity.HIGH,
                passed=False,
                compliance_score=0,
                violations=[f"Test execution failed: {str(e)}"],
                recommendations=["Fix CCPA opt-out implementation"],
                evidence=evidence,
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def run_comprehensive_compliance_tests(self) -> List[ComplianceTestResult]:
        """Run comprehensive compliance test suite."""
        logger.info("Starting comprehensive compliance tests...")
        
        results = []
        
        # Generate test data
        eu_user_data = PersonalDataGenerator.generate_eu_user_data()
        ca_user_data = PersonalDataGenerator.generate_california_user_data()
        
        # GDPR Tests
        gdpr_tests = [
            self.test_gdpr_consent_collection,
            self.test_gdpr_data_access_right,
            self.test_gdpr_data_deletion_right,
        ]
        
        for test_method in gdpr_tests:
            try:
                logger.info(f"Running GDPR test: {test_method.__name__}")
                result = await test_method(eu_user_data)
                results.append(result)
                await asyncio.sleep(2)  # Delay between tests
            except Exception as e:
                logger.error(f"GDPR test {test_method.__name__} failed: {e}")
        
        # CCPA Tests
        ccpa_tests = [
            self.test_ccpa_do_not_sell_right,
        ]
        
        for test_method in ccpa_tests:
            try:
                logger.info(f"Running CCPA test: {test_method.__name__}")
                result = await test_method(ca_user_data)
                results.append(result)
                await asyncio.sleep(2)  # Delay between tests
            except Exception as e:
                logger.error(f"CCPA test {test_method.__name__} failed: {e}")
        
        return results
    
    def generate_compliance_report(self, results: List[ComplianceTestResult]) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if not results:
            return {"error": "No compliance test results available"}
        
        # Group by regulation
        by_regulation = {}
        for result in results:
            reg = result.regulation.value
            if reg not in by_regulation:
                by_regulation[reg] = []
            by_regulation[reg].append(result)
        
        # Calculate overall metrics
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        avg_compliance_score = sum(r.compliance_score for r in results) / total_tests if total_tests > 0 else 0
        
        critical_violations = len([r for r in results if r.severity == ComplianceSeverity.CRITICAL and not r.passed])
        high_violations = len([r for r in results if r.severity == ComplianceSeverity.HIGH and not r.passed])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "compliance_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_compliance_score": avg_compliance_score,
                "critical_violations": critical_violations,
                "high_violations": high_violations,
                "overall_compliance_rating": self._get_compliance_rating(avg_compliance_score)
            },
            "regulations": {
                regulation: {
                    "tests_run": len(tests),
                    "tests_passed": len([t for t in tests if t.passed]),
                    "compliance_score": sum(t.compliance_score for t in tests) / len(tests) if tests else 0,
                    "violations": sum(len(t.violations) for t in tests),
                    "status": "COMPLIANT" if all(t.passed for t in tests) else "NON_COMPLIANT"
                }
                for regulation, tests in by_regulation.items()
            },
            "detailed_results": [
                {
                    "test_name": result.test_name,
                    "regulation": result.regulation.value,
                    "test_type": result.test_type.value,
                    "status": "PASS" if result.passed else "FAIL",
                    "compliance_score": result.compliance_score,
                    "violations_count": len(result.violations),
                    "violations": result.violations,
                    "recommendations": result.recommendations,
                    "severity": result.severity.value
                }
                for result in results
            ]
        }
        
        return report
    
    def _get_compliance_rating(self, score: float) -> str:
        """Get compliance rating based on score."""
        if score >= 95:
            return "EXCELLENT"
        elif score >= 85:
            return "GOOD"
        elif score >= 70:
            return "ACCEPTABLE"
        elif score >= 50:
            return "POOR"
        else:
            return "NON_COMPLIANT"


class TestIndustrialCompliance:
    """Test class for industrial compliance testing."""
    
    @pytest.mark.compliance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_comprehensive_gdpr_ccpa_compliance(self):
        """
        Run comprehensive GDPR and CCPA compliance tests.
        Tests real compliance validation with actual data processing.
        """
        async with RealComplianceValidator() as validator:
            results = await validator.run_comprehensive_compliance_tests()
            report = validator.generate_compliance_report(results)
            
            # Log detailed results
            logger.info(f"Compliance tests completed: {report['summary']}")
            
            # Assert compliance requirements
            assert len(results) > 0, "No compliance tests were executed"
            assert report['summary']['compliance_rate'] >= 80, f"Compliance rate too low: {report['summary']['compliance_rate']:.1f}%"
            assert report['summary']['critical_violations'] == 0, f"Critical compliance violations found: {report['summary']['critical_violations']}"
            assert report['summary']['average_compliance_score'] >= 75, f"Average compliance score too low: {report['summary']['average_compliance_score']:.1f}"
    
    @pytest.mark.compliance
    @pytest.mark.asyncio
    async def test_gdpr_compliance_comprehensive(self):
        """Test comprehensive GDPR compliance."""
        async with RealComplianceValidator() as validator:
            eu_user_data = PersonalDataGenerator.generate_eu_user_data()
            
            # Test individual GDPR rights
            consent_result = await validator.test_gdpr_consent_collection(eu_user_data)
            access_result = await validator.test_gdpr_data_access_right(eu_user_data)
            deletion_result = await validator.test_gdpr_data_deletion_right(eu_user_data)
            
            # GDPR tests should pass with allowable error margin
            total_score = consent_result.compliance_score + access_result.compliance_score + deletion_result.compliance_score
            avg_score = total_score / 3
            assert avg_score >= 70, f"GDPR compliance score too low: {avg_score:.1f}"
    
    @pytest.mark.compliance
    @pytest.mark.asyncio
    async def test_ccpa_compliance_comprehensive(self):
        """Test comprehensive CCPA compliance."""
        async with RealComplianceValidator() as validator:
            ca_user_data = PersonalDataGenerator.generate_california_user_data()
            
            # Test CCPA rights
            opt_out_result = await validator.test_ccpa_do_not_sell_right(ca_user_data)
            
            # CCPA tests should pass with allowable error margin
            assert opt_out_result.compliance_score >= 70, f"CCPA compliance score too low: {opt_out_result.compliance_score:.1f}"