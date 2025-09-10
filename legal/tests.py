"""
Legal Module Test Suite - Comprehensive Testing Framework
==========================================================

Complete test suite for legal compliance framework including unit tests,
integration tests, and compliance validation tests.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import pytest
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import legal module components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legal.core import (
    LegalComplianceFramework,
    CopyrightProtectionEngine,
    DataProtectionManager,
    ContractManagementSystem,
    LegalEnforcementEngine,
    LegalFrameworkType,
    ComplianceStatus,
    LegalRiskLevel
)

from legal.copyright import (
    CopyrightRegistrationManager,
    CopyrightInfringementDetector,
    DMCANoticeGenerator,
    IntellectualPropertyProtection,
    CopyrightStatus,
    InfringementSeverity
)

from legal.privacy import (
    GDPRComplianceManager,
    PrivacyPolicyManager,
    ConsentManagementSystem,
    DataMinimizationEngine,
    PrivacyRegulation,
    ConsentStatus,
    DataCategory
)


class TestLegalComplianceFramework(unittest.TestCase):
    """Test cases for core legal compliance framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.framework = LegalComplianceFramework()
        self.content_id = "test_content_123"
        self.user_id = "test_user_456"
    
    def test_framework_initialization(self):
        """Test legal compliance framework initialization"""
        self.assertIsInstance(self.framework, LegalComplianceFramework)
        self.assertEqual(len(self.framework.compliance_records), 0)
        self.assertEqual(len(self.framework.active_violations), 0)
        self.assertEqual(self.framework.compliance_metrics["total_checks"], 0)
    
    async def test_assess_legal_compliance(self):
        """Test legal compliance assessment"""
        framework_types = [
            LegalFrameworkType.COPYRIGHT_PROTECTION,
            LegalFrameworkType.DATA_PROTECTION
        ]
        
        results = await self.framework.assess_legal_compliance(
            self.content_id, framework_types, self.user_id
        )
        
        self.assertEqual(len(results), 2)
        self.assertIn("copyright_protection", results)
        self.assertIn("data_protection", results)
        self.assertTrue(len(self.framework.compliance_records) > 0)
    
    async def test_violation_resolution(self):
        """Test violation resolution process"""
        # Create a test compliance record
        framework_types = [LegalFrameworkType.COPYRIGHT_PROTECTION]
        await self.framework.assess_legal_compliance(
            self.content_id, framework_types, self.user_id
        )
        
        # Get first record and simulate violation
        record_id = list(self.framework.compliance_records.keys())[0]
        record = self.framework.compliance_records[record_id]
        record.compliance_status = ComplianceStatus.VIOLATION_DETECTED
        self.framework.active_violations.add(record_id)
        
        # Resolve violation
        remediation_actions = ["Content removed", "User notified"]
        result = await self.framework.resolve_violation(record_id, remediation_actions)
        
        self.assertTrue(result)
        self.assertEqual(record.compliance_status, ComplianceStatus.COMPLIANT)
        self.assertNotIn(record_id, self.framework.active_violations)
    
    def test_compliance_metrics(self):
        """Test compliance metrics calculation"""
        metrics = self.framework.get_compliance_metrics()
        
        self.assertIn("total_checks", metrics)
        self.assertIn("violations_detected", metrics)
        self.assertIn("compliance_rate", metrics)
        self.assertIsInstance(metrics["compliance_rate"], float)


class TestCopyrightProtectionEngine(unittest.TestCase):
    """Test cases for copyright protection engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = CopyrightProtectionEngine()
        self.content_id = "copyright_test_123"
        self.creator_id = "creator_456"
    
    def test_engine_initialization(self):
        """Test copyright engine initialization"""
        self.assertIsInstance(self.engine, CopyrightProtectionEngine)
        self.assertEqual(len(self.engine.copyright_registry), 0)
        self.assertEqual(len(self.engine.infringement_detections), 0)
    
    async def test_copyright_registration(self):
        """Test copyright registration process"""
        registration_id = await self.engine.register_copyright(
            self.content_id,
            self.creator_id,
            "music",
            metadata={"title": "Test Song", "duration": 180}
        )
        
        self.assertIsInstance(registration_id, str)
        self.assertIn(registration_id, self.engine.copyright_registry)
        
        record = self.engine.copyright_registry[registration_id]
        self.assertEqual(record["content_id"], self.content_id)
        self.assertEqual(record["creator_id"], self.creator_id)
        self.assertEqual(record["content_type"], "music")
    
    async def test_infringement_detection(self):
        """Test copyright infringement detection"""
        detection_result = await self.engine.detect_infringement(self.content_id)
        
        self.assertIsInstance(detection_result, dict)
        self.assertIn("content_id", detection_result)
        self.assertIn("infringement_detected", detection_result)
        self.assertIn("confidence_score", detection_result)
        self.assertIn("detection_timestamp", detection_result)
        
        self.assertEqual(detection_result["content_id"], self.content_id)
        self.assertIsInstance(detection_result["confidence_score"], float)


class TestCopyrightRegistrationManager(unittest.TestCase):
    """Test cases for copyright registration manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CopyrightRegistrationManager()
        self.content_data = b"test content data for copyright"
        self.content_id = "reg_test_123"
        self.creator_id = "creator_789"
    
    async def test_copyright_registration_workflow(self):
        """Test complete copyright registration workflow"""
        registration_id = await self.manager.register_copyright(
            self.content_id,
            self.creator_id,
            "text",
            self.content_data,
            jurisdiction="US"
        )
        
        self.assertIsInstance(registration_id, str)
        self.assertIn(registration_id, self.manager.registrations)
        self.assertIn(registration_id, self.manager.pending_registrations)
        
        record = self.manager.registrations[registration_id]
        self.assertEqual(record.content_id, self.content_id)
        self.assertEqual(record.creator_id, self.creator_id)
        self.assertEqual(record.jurisdiction, "US")
        self.assertIsInstance(record.content_hash, str)
    
    async def test_duplicate_registration_prevention(self):
        """Test prevention of duplicate copyright registrations"""
        # Register content first time
        reg_id_1 = await self.manager.register_copyright(
            self.content_id,
            self.creator_id,
            "text",
            self.content_data
        )
        
        # Try to register same content again
        reg_id_2 = await self.manager.register_copyright(
            "different_content_id",
            self.creator_id,
            "text",
            self.content_data  # Same content data
        )
        
        # Should return same registration ID
        self.assertEqual(reg_id_1, reg_id_2)
    
    def test_registration_status_check(self):
        """Test copyright registration status checking"""
        # Test non-existent registration
        status = self.manager.get_registration_status("non_existent_id")
        self.assertIsNone(status)


class TestGDPRComplianceManager(unittest.TestCase):
    """Test cases for GDPR compliance manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = GDPRComplianceManager()
        self.user_id = "gdpr_test_user_123"
    
    def test_manager_initialization(self):
        """Test GDPR manager initialization"""
        self.assertIsInstance(self.manager, GDPRComplianceManager)
        self.assertEqual(len(self.manager.consent_records), 0)
        self.assertEqual(len(self.manager.privacy_requests), 0)
        self.assertEqual(len(self.manager.data_subjects), 0)
    
    async def test_consent_collection(self):
        """Test GDPR consent collection"""
        consent_id = await self.manager.collect_consent(
            self.user_id,
            "analytics",
            [DataCategory.BEHAVIOR, DataCategory.PREFERENCES],
            "We use your data for analytics purposes",
            retention_period=365
        )
        
        self.assertIsInstance(consent_id, str)
        self.assertIn(consent_id, self.manager.consent_records)
        self.assertIn(self.user_id, self.manager.data_subjects)
        
        consent = self.manager.consent_records[consent_id]
        self.assertEqual(consent.user_id, self.user_id)
        self.assertEqual(consent.purpose, "analytics")
        self.assertEqual(consent.status, ConsentStatus.GRANTED)
    
    async def test_consent_withdrawal(self):
        """Test GDPR consent withdrawal"""
        # First collect consent
        consent_id = await self.manager.collect_consent(
            self.user_id,
            "marketing",
            [DataCategory.CONTACT],
            "Marketing communications"
        )
        
        # Then withdraw consent
        result = await self.manager.withdraw_consent(self.user_id, consent_id)
        
        self.assertTrue(result)
        consent = self.manager.consent_records[consent_id]
        self.assertEqual(consent.status, ConsentStatus.WITHDRAWN)
        self.assertIsNotNone(consent.withdrawn_at)
    
    async def test_subject_access_request(self):
        """Test GDPR subject access request"""
        request_id = await self.manager.process_subject_access_request(self.user_id)
        
        self.assertIsInstance(request_id, str)
        self.assertIn(request_id, self.manager.privacy_requests)
        
        request = self.manager.privacy_requests[request_id]
        self.assertEqual(request.user_id, self.user_id)
        self.assertEqual(request.request_type.value, "access")
    
    async def test_erasure_request(self):
        """Test GDPR right to erasure request"""
        request_id = await self.manager.process_erasure_request(self.user_id)
        
        self.assertIsInstance(request_id, str)
        self.assertIn(request_id, self.manager.privacy_requests)
        
        request = self.manager.privacy_requests[request_id]
        self.assertEqual(request.user_id, self.user_id)
        self.assertEqual(request.request_type.value, "erasure")


class TestDMCANoticeGenerator(unittest.TestCase):
    """Test cases for DMCA notice generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = DMCANoticeGenerator()
    
    def test_generator_initialization(self):
        """Test DMCA generator initialization"""
        self.assertIsInstance(self.generator, DMCANoticeGenerator)
        self.assertEqual(len(self.generator.notices), 0)
        self.assertIn("standard", self.generator.notice_templates)
    
    async def test_dmca_notice_generation(self):
        """Test DMCA notice generation"""
        notice_id = await self.generator.generate_dmca_notice(
            copyright_owner="Test Creator",
            infringing_url="https://example.com/infringing-content",
            original_work_description="Original music composition",
            infringement_description="Unauthorized use of copyrighted music",
            contact_info={
                "name": "Test Creator",
                "email": "creator@example.com",
                "phone": "+1234567890"
            }
        )
        
        self.assertIsInstance(notice_id, str)
        self.assertIn(notice_id, self.generator.notices)
        
        notice = self.generator.notices[notice_id]
        self.assertEqual(notice.copyright_owner, "Test Creator")
        self.assertIn("infringing-content", notice.infringing_url)
    
    async def test_dmca_notice_sending(self):
        """Test DMCA notice sending process"""
        # Generate notice first
        notice_id = await self.generator.generate_dmca_notice(
            "Test Owner",
            "https://platform.com/content",
            "Original work",
            "Infringing copy",
            {"email": "owner@test.com"}
        )
        
        # Send notice
        result = await self.generator.send_dmca_notice(
            notice_id,
            "platform@example.com"
        )
        
        self.assertTrue(result)
        notice = self.generator.notices[notice_id]
        self.assertEqual(notice.status.value, "sent")
        self.assertIsNotNone(notice.sent_at)


class TestDataMinimizationEngine(unittest.TestCase):
    """Test cases for data minimization engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = DataMinimizationEngine()
    
    def test_engine_initialization(self):
        """Test data minimization engine initialization"""
        self.assertIsInstance(self.engine, DataMinimizationEngine)
        self.assertEqual(len(self.engine.minimization_rules), 0)
        self.assertEqual(len(self.engine.data_assessments), 0)
    
    async def test_data_necessity_assessment(self):
        """Test data necessity assessment"""
        requested_data = {
            "email": "user@example.com",
            "password": "hashedpassword",
            "favorite_color": "blue",
            "mother_maiden_name": "Smith"
        }
        
        assessment = await self.engine.assess_data_necessity(
            "authentication",
            requested_data
        )
        
        self.assertIsInstance(assessment, dict)
        self.assertIn("assessment_id", assessment)
        self.assertIn("necessary_data", assessment)
        self.assertIn("unnecessary_data", assessment)
        self.assertIn("compliance_score", assessment)
        self.assertIn("recommendations", assessment)
        
        # Check that email and password are necessary for authentication
        self.assertIn("email", assessment["necessary_data"])
        self.assertIn("password", assessment["necessary_data"])
        
        # Check compliance score calculation
        self.assertIsInstance(assessment["compliance_score"], float)
        self.assertGreaterEqual(assessment["compliance_score"], 0.0)
        self.assertLessEqual(assessment["compliance_score"], 1.0)


class LegalModuleIntegrationTests(unittest.TestCase):
    """Integration tests for legal module components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.legal_framework = LegalComplianceFramework()
        self.copyright_engine = CopyrightProtectionEngine()
        self.data_protection = DataProtectionManager()
        self.ip_protection = IntellectualPropertyProtection()
    
    async def test_end_to_end_content_protection(self):
        """Test end-to-end content protection workflow"""
        content_id = "integration_test_content"
        creator_id = "integration_test_creator"
        content_data = b"test content for protection"
        
        # Step 1: Comprehensive content protection
        protection_result = await self.ip_protection.protect_content(
            content_id,
            creator_id,
            content_data,
            "music",
            protection_level="premium"
        )
        
        self.assertEqual(protection_result["status"], "protected")
        self.assertIn("copyright_registration", protection_result)
        self.assertIn("copyright_registration", protection_result["services_applied"])
        
        # Step 2: Legal compliance assessment
        compliance_results = await self.legal_framework.assess_legal_compliance(
            content_id,
            [LegalFrameworkType.COPYRIGHT_PROTECTION, LegalFrameworkType.DATA_PROTECTION]
        )
        
        self.assertEqual(len(compliance_results), 2)
        self.assertIn("copyright_protection", compliance_results)
        self.assertIn("data_protection", compliance_results)
    
    async def test_gdpr_copyright_integration(self):
        """Test integration between GDPR compliance and copyright protection"""
        user_id = "integration_gdpr_user"
        content_id = "integration_gdpr_content"
        
        # GDPR consent collection for content processing
        gdpr_manager = GDPRComplianceManager()
        consent_id = await gdpr_manager.collect_consent(
            user_id,
            "content_processing",
            [DataCategory.IDENTITY, DataCategory.BEHAVIOR],
            "Content processing for copyright protection"
        )
        
        self.assertIsInstance(consent_id, str)
        
        # Copyright registration with GDPR compliance
        copyright_manager = CopyrightRegistrationManager()
        registration_id = await copyright_manager.register_copyright(
            content_id,
            user_id,
            "video",
            b"video content data"
        )
        
        self.assertIsInstance(registration_id, str)
        
        # Verify both systems are working together
        consent = gdpr_manager.consent_records[consent_id]
        registration = copyright_manager.registrations[registration_id]
        
        self.assertEqual(consent.user_id, user_id)
        self.assertEqual(registration.creator_id, user_id)


def run_async_test(coro):
    """Helper function to run async tests"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLegalComplianceFramework,
        TestCopyrightProtectionEngine,
        TestCopyrightRegistrationManager,
        TestGDPRComplianceManager,
        TestDMCANoticeGenerator,
        TestDataMinimizationEngine,
        LegalModuleIntegrationTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print test summary
    print("\n" + "="*60)
    print("LEGAL MODULE TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    print("\n🛡️ Legal Module Testing Complete")