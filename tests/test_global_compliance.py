"""
Global Compliance Test Suite
============================

Comprehensive tests for global legal compliance frameworks including
PIPEDA, LGPD, and PDPA implementations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited
"""

import sys
import os
from pathlib import Path

# Add the repository root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the compliance modules
from data_management.governance.compliance import (
    ComplianceManager, ComplianceFramework, ComplianceStatus, RiskLevel,
    PIPEDACompliance, LGPDCompliance, PDPACompliance,
    ComplianceReport, ComplianceIssue
)
from config.global_compliance_config import GlobalComplianceConfig, global_compliance_config


class TestPIPEDACompliance:
    """Test PIPEDA compliance framework"""
    
    @pytest.fixture
    async def pipeda_checker(self):
        """Create PIPEDA compliance checker"""
        return PIPEDACompliance()
    
    @pytest.mark.asyncio
    async def test_pipeda_basic_assessment(self, pipeda_checker):
        """Test basic PIPEDA compliance assessment"""
        
        content_id = "test_content_001"
        content_type = "audio"
        metadata = {
            "content_id": content_id,
            "organization": {
                "privacy_officer": "Privacy Officer",
                "privacy_policy": "https://example.com/privacy"
            },
            "collection": {
                "identified_purposes": ["content_analysis", "service_improvement"],
                "data_types": ["audio_content", "metadata"]
            },
            "consent": {
                "obtained": True,
                "informed": True
            },
            "security": {
                "encryption_enabled": True,
                "access_controls": True
            },
            "individual_access": {
                "access_mechanism": "user_portal"
            },
            "data_quality": {
                "accuracy_verified": True
            }
        }
        
        report = await pipeda_checker.assess_compliance(content_id, content_type, metadata)
        
        assert report.framework == ComplianceFramework.PIPEDA
        assert report.content_id == content_id
        assert report.status == ComplianceStatus.COMPLIANT
        assert report.score == 100.0
        assert len(report.issues) == 0
        assert report.metadata["jurisdiction"] == "Canada"
    
    @pytest.mark.asyncio
    async def test_pipeda_accountability_issues(self, pipeda_checker):
        """Test PIPEDA accountability principle violations"""
        
        content_id = "test_content_002"
        metadata = {
            "content_id": content_id,
            "organization": {
                # Missing privacy_officer and privacy_policy
            },
            "collection": {
                "identified_purposes": ["content_analysis"]
            },
            "consent": {
                "obtained": True
            }
        }
        
        report = await pipeda_checker.assess_compliance(content_id, "text", metadata)
        
        assert report.status != ComplianceStatus.COMPLIANT
        assert len(report.issues) >= 2  # Privacy officer and policy missing
        
        # Check for specific accountability issues
        issue_types = {issue.issue_type for issue in report.issues}
        assert "accountability_missing" in issue_types
        assert "privacy_policy_missing" in issue_types
    
    @pytest.mark.asyncio
    async def test_pipeda_consent_requirements(self, pipeda_checker):
        """Test PIPEDA consent requirements"""
        
        metadata = {
            "content_id": "test_consent",
            "consent": {
                "obtained": False  # No consent obtained
            },
            "organization": {
                "privacy_officer": "Officer",
                "privacy_policy": "Policy"
            }
        }
        
        report = await pipeda_checker.assess_compliance("test_consent", "image", metadata)
        
        # Should have consent issue
        issue_types = {issue.issue_type for issue in report.issues}
        assert "consent_not_obtained" in issue_types
        
        # Test informed consent issue
        metadata["consent"] = {
            "obtained": True,
            "informed": False  # Consent not properly informed
        }
        
        report2 = await pipeda_checker.assess_compliance("test_consent_2", "image", metadata)
        issue_types2 = {issue.issue_type for issue in report2.issues}
        assert "consent_not_informed" in issue_types2
    
    @pytest.mark.asyncio
    async def test_pipeda_use_limitation(self, pipeda_checker):
        """Test PIPEDA use and disclosure limitation"""
        
        metadata = {
            "content_id": "test_use_limit",
            "organization": {
                "privacy_officer": "Officer",
                "privacy_policy": "Policy"
            },
            "collection": {
                "identified_purposes": ["content_analysis", "quality_improvement"]
            },
            "usage": {
                "purposes": ["content_analysis", "marketing", "data_sale"]  # Unauthorized purposes
            },
            "consent": {
                "obtained": True,
                "informed": True
            }
        }
        
        report = await pipeda_checker.assess_compliance("test_use_limit", "video", metadata)
        
        # Should detect unauthorized use
        issue_types = {issue.issue_type for issue in report.issues}
        assert "unauthorized_use" in issue_types
        
        # Check that unauthorized uses are identified
        unauthorized_issue = next(
            issue for issue in report.issues 
            if issue.issue_type == "unauthorized_use"
        )
        assert "marketing" in str(unauthorized_issue.metadata.get("unauthorized_uses", []))
        assert "data_sale" in str(unauthorized_issue.metadata.get("unauthorized_uses", []))


class TestLGPDCompliance:
    """Test LGPD compliance framework"""
    
    @pytest.fixture
    async def lgpd_checker(self):
        """Create LGPD compliance checker"""
        return LGPDCompliance()
    
    @pytest.mark.asyncio
    async def test_lgpd_basic_assessment(self, lgpd_checker):
        """Test basic LGPD compliance assessment"""
        
        content_id = "test_lgpd_001"
        metadata = {
            "content_id": content_id,
            "processing": {
                "legal_basis": "consent",
                "purposes": ["service_provision", "user_experience"]
            },
            "transparency": {
                "privacy_notice": True
            },
            "data_subject_rights": {
                "access_mechanism": True,
                "rectification_mechanism": True,
                "erasure_mechanism": True,
                "portability_mechanism": True,
                "opposition_mechanism": True
            },
            "security": {
                "encryption": True
            },
            "international_transfers": {
                "occurs": False
            },
            "collected_fields": ["name", "email"],
            "necessary_fields": ["name", "email"]
        }
        
        report = await lgpd_checker.assess_compliance(content_id, "text", metadata)
        
        assert report.framework == ComplianceFramework.LGPD
        assert report.status == ComplianceStatus.COMPLIANT
        assert report.score == 100.0
        assert report.metadata["jurisdiction"] == "Brazil"
    
    @pytest.mark.asyncio
    async def test_lgpd_legal_basis_violation(self, lgpd_checker):
        """Test LGPD legal basis requirements"""
        
        metadata = {
            "content_id": "test_legal_basis",
            "processing": {
                "legal_basis": "invalid_basis",  # Invalid legal basis
                "purposes": ["service_provision"]
            }
        }
        
        report = await lgpd_checker.assess_compliance("test_legal_basis", "audio", metadata)
        
        issue_types = {issue.issue_type for issue in report.issues}
        assert "invalid_legal_basis" in issue_types
        assert report.status != ComplianceStatus.COMPLIANT
    
    @pytest.mark.asyncio
    async def test_lgpd_data_subject_rights(self, lgpd_checker):
        """Test LGPD data subject rights implementation"""
        
        metadata = {
            "content_id": "test_rights",
            "processing": {
                "legal_basis": "consent",
                "purposes": ["service_provision"]
            },
            "data_subject_rights": {
                "access_mechanism": False,  # Missing access right
                "rectification_mechanism": False,  # Missing rectification right
                # Other rights missing
            }
        }
        
        report = await lgpd_checker.assess_compliance("test_rights", "video", metadata)
        
        # Should have multiple rights-related issues
        issue_types = {issue.issue_type for issue in report.issues}
        assert "missing_access_right" in issue_types
        assert "missing_rectification_right" in issue_types
        assert "missing_erasure_right" in issue_types
    
    @pytest.mark.asyncio
    async def test_lgpd_international_transfers(self, lgpd_checker):
        """Test LGPD international transfer requirements"""
        
        metadata = {
            "content_id": "test_transfers",
            "processing": {
                "legal_basis": "consent",
                "purposes": ["service_provision"]
            },
            "international_transfers": {
                "occurs": True,
                "adequacy_decision": False  # No adequacy decision
            }
        }
        
        report = await lgpd_checker.assess_compliance("test_transfers", "image", metadata)
        
        issue_types = {issue.issue_type for issue in report.issues}
        assert "unauthorized_transfer" in issue_types


class TestPDPACompliance:
    """Test PDPA compliance framework"""
    
    @pytest.fixture
    async def pdpa_checker(self):
        """Create PDPA compliance checker"""
        config = {"jurisdiction": "Singapore"}
        return PDPACompliance(config)
    
    @pytest.fixture
    async def pdpa_thailand_checker(self):
        """Create PDPA Thailand compliance checker"""
        config = {"jurisdiction": "Thailand"}
        return PDPACompliance(config)
    
    @pytest.mark.asyncio
    async def test_pdpa_singapore_assessment(self, pdpa_checker):
        """Test PDPA Singapore compliance assessment"""
        
        content_id = "test_pdpa_sg_001"
        metadata = {
            "content_id": content_id,
            "consent": {
                "obtained": True,
                "voluntary": True
            },
            "processing": {
                "purposes": ["service_provision", "customer_support"]
            },
            "notification": {
                "privacy_policy_provided": True
            },
            "access_correction": {
                "access_mechanism": True,
                "correction_mechanism": True
            },
            "accuracy": {
                "verification_performed": True
            },
            "security": {
                "reasonable_security": True
            },
            "retention": {
                "policy_defined": True
            },
            "transfers": {
                "overseas_transfers": False
            }
        }
        
        report = await pdpa_checker.assess_compliance(content_id, "text", metadata)
        
        assert report.framework == ComplianceFramework.PDPA
        assert report.status == ComplianceStatus.COMPLIANT
        assert report.metadata["jurisdiction"] == "Singapore"
    
    @pytest.mark.asyncio
    async def test_pdpa_thailand_assessment(self, pdpa_thailand_checker):
        """Test PDPA Thailand compliance assessment"""
        
        metadata = {
            "content_id": "test_pdpa_th_001",
            "consent": {
                "obtained": True,
                "voluntary": True
            },
            "processing": {
                "purposes": ["legitimate_business"]
            }
        }
        
        report = await pdpa_thailand_checker.assess_compliance("test_pdpa_th_001", "audio", metadata)
        
        assert report.framework == ComplianceFramework.PDPA
        assert report.metadata["jurisdiction"] == "Thailand"
    
    @pytest.mark.asyncio
    async def test_pdpa_consent_violations(self, pdpa_checker):
        """Test PDPA consent violations"""
        
        metadata = {
            "content_id": "test_consent_violation",
            "consent": {
                "obtained": False  # No consent
            },
            "processing": {
                "purposes": ["service_provision"]
            }
        }
        
        report = await pdpa_checker.assess_compliance("test_consent_violation", "video", metadata)
        
        issue_types = {issue.issue_type for issue in report.issues}
        assert "consent_not_obtained" in issue_types
        
        # Test non-voluntary consent
        metadata["consent"] = {
            "obtained": True,
            "voluntary": False  # Not voluntary
        }
        
        report2 = await pdpa_checker.assess_compliance("test_consent_2", "video", metadata)
        issue_types2 = {issue.issue_type for issue in report2.issues}
        assert "consent_not_voluntary" in issue_types2
    
    @pytest.mark.asyncio
    async def test_pdpa_unreasonable_purposes(self, pdpa_checker):
        """Test PDPA unreasonable purpose detection"""
        
        metadata = {
            "content_id": "test_unreasonable",
            "consent": {
                "obtained": True,
                "voluntary": True
            },
            "processing": {
                "purposes": ["surveillance", "stalking", "harassment"]  # Unreasonable purposes
            }
        }
        
        report = await pdpa_checker.assess_compliance("test_unreasonable", "image", metadata)
        
        issue_types = {issue.issue_type for issue in report.issues}
        assert "unreasonable_purpose" in issue_types
    
    @pytest.mark.asyncio
    async def test_pdpa_overseas_transfers(self, pdpa_checker):
        """Test PDPA overseas transfer restrictions"""
        
        metadata = {
            "content_id": "test_transfers",
            "consent": {
                "obtained": True,
                "voluntary": True
            },
            "processing": {
                "purposes": ["service_provision"]
            },
            "transfers": {
                "overseas_transfers": True,
                "adequate_protection": False  # No adequate protection
            }
        }
        
        report = await pdpa_checker.assess_compliance("test_transfers", "text", metadata)
        
        issue_types = {issue.issue_type for issue in report.issues}
        assert "inadequate_transfer_protection" in issue_types


class TestGlobalComplianceConfig:
    """Test global compliance configuration"""
    
    def test_framework_initialization(self):
        """Test that all frameworks are properly initialized"""
        config = GlobalComplianceConfig()
        
        # Check that all expected frameworks are present
        expected_frameworks = ["gdpr", "ccpa", "dmca", "pipeda", "lgpd", "pdpa_singapore", "pdpa_thailand"]
        
        for framework_id in expected_frameworks:
            assert framework_id in config.frameworks
            framework = config.frameworks[framework_id]
            assert framework.framework_id == framework_id
            assert framework.name
            assert framework.jurisdiction
            assert framework.enforcement_authority
    
    def test_jurisdiction_mapping(self):
        """Test jurisdiction to framework mapping"""
        config = GlobalComplianceConfig()
        
        # Test EU jurisdiction
        eu_frameworks = config.get_jurisdiction_frameworks("EU")
        assert "gdpr" in eu_frameworks
        
        # Test Canadian jurisdiction
        ca_frameworks = config.get_jurisdiction_frameworks("CA")
        assert "pipeda" in ca_frameworks
        
        # Test Brazilian jurisdiction
        br_frameworks = config.get_jurisdiction_frameworks("BR")
        assert "lgpd" in br_frameworks
        
        # Test Singapore jurisdiction
        sg_frameworks = config.get_jurisdiction_frameworks("SG")
        assert "pdpa_singapore" in sg_frameworks
    
    def test_applicable_frameworks_detection(self):
        """Test detection of applicable frameworks"""
        config = GlobalComplianceConfig()
        
        # Test EU user with audio content
        frameworks = config.get_applicable_frameworks(
            jurisdiction="EU",
            content_type="audio",
            user_location="DE"
        )
        
        framework_ids = [f.framework_id for f in frameworks]
        assert "gdpr" in framework_ids
        assert "dmca" in framework_ids  # Audio requires DMCA
        
        # Test Brazilian user with video content
        frameworks = config.get_applicable_frameworks(
            jurisdiction="BR",
            content_type="video",
            user_location="BR"
        )
        
        framework_ids = [f.framework_id for f in frameworks]
        assert "lgpd" in framework_ids
        assert "dmca" in framework_ids  # Video requires DMCA
    
    def test_content_type_requirements(self):
        """Test content type specific requirements"""
        config = GlobalComplianceConfig()
        
        # Test audio requirements
        audio_req = config.get_content_requirements("audio")
        assert "dmca" in audio_req["required_frameworks"]
        
        # Test video requirements
        video_req = config.get_content_requirements("video")
        assert "dmca" in video_req["required_frameworks"]
        assert "gdpr" in video_req["optional_frameworks"]
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        config = GlobalComplianceConfig()
        
        validation = config.validate_compliance_configuration()
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        assert validation["summary"]["total_frameworks"] >= 7


class TestComplianceManagerIntegration:
    """Test integration of all compliance frameworks"""
    
    @pytest.fixture
    async def compliance_manager(self):
        """Create compliance manager with all frameworks"""
        config = {
            "jurisdiction": "Singapore",  # For PDPA configuration
            "global_config": global_compliance_config
        }
        return ComplianceManager(config)
    
    @pytest.mark.asyncio
    async def test_all_frameworks_assessment(self, compliance_manager):
        """Test assessment across all compliance frameworks"""
        
        content_id = "test_global_001"
        content_type = "video"
        metadata = {
            "content_id": content_id,
            # GDPR metadata
            "processing": {
                "lawful_basis": "consent",
                "purposes": ["content_analysis"],
                "legal_basis": "consent"  # For LGPD
            },
            "consent": {
                "obtained_at": datetime.utcnow(),
                "purposes": ["content_analysis"],
                "withdrawal_mechanism": "user_portal",
                "obtained": True,
                "informed": True,
                "voluntary": True
            },
            "controller": {
                "contact_info": "privacy@example.com"
            },
            "collected_fields": ["video_content", "metadata"],
            "necessary_fields": ["video_content", "metadata"],
            "security": {
                "encrypted": True,
                "access_controls": True,
                "encryption_enabled": True,
                "encryption": True,
                "reasonable_security": True
            },
            # CCPA metadata
            "consumer_rights": {
                "right_to_know_implemented": True,
                "right_to_delete_implemented": True
            },
            "disclosure": {
                "categories_collected": ["video_content"]
            },
            "optout": {
                "do_not_sell_link": "https://example.com/opt-out"
            },
            # DMCA metadata
            "copyright": {
                "owner": "Content Creator",
                "registration_number": "REG123456"
            },
            "takedown": {
                "agent_contact": "dmca@example.com"
            },
            "safe_harbor": {
                "policy_implemented": True
            },
            # PIPEDA metadata
            "organization": {
                "privacy_officer": "Privacy Officer",
                "privacy_policy": "https://example.com/privacy"
            },
            "collection": {
                "identified_purposes": ["content_analysis"],
                "data_types": ["video_content"]
            },
            "individual_access": {
                "access_mechanism": "user_portal"
            },
            "data_quality": {
                "accuracy_verified": True
            },
            # LGPD metadata
            "transparency": {
                "privacy_notice": True
            },
            "data_subject_rights": {
                "access_mechanism": True,
                "rectification_mechanism": True,
                "erasure_mechanism": True,
                "portability_mechanism": True,
                "opposition_mechanism": True
            },
            "international_transfers": {
                "occurs": False
            },
            # PDPA metadata
            "notification": {
                "privacy_policy_provided": True
            },
            "access_correction": {
                "access_mechanism": True,
                "correction_mechanism": True
            },
            "accuracy": {
                "verification_performed": True
            },
            "retention": {
                "policy_defined": True
            },
            "transfers": {
                "overseas_transfers": False
            }
        }
        
        # Test all frameworks
        frameworks_to_test = [
            ComplianceFramework.GDPR,
            ComplianceFramework.CCPA,
            ComplianceFramework.DMCA,
            ComplianceFramework.PIPEDA,
            ComplianceFramework.LGPD,
            ComplianceFramework.PDPA
        ]
        
        reports = await compliance_manager.assess_compliance(
            content_id, content_type, metadata, frameworks_to_test
        )
        
        # Verify all frameworks were assessed
        assert len(reports) == len(frameworks_to_test)
        
        for framework in frameworks_to_test:
            assert framework in reports
            report = reports[framework]
            assert report.content_id == content_id
            assert report.framework == framework
            # Most should be compliant with complete metadata
            assert report.score >= 80.0  # Allow some tolerance for different scoring
    
    @pytest.mark.asyncio
    async def test_compliance_summary_generation(self, compliance_manager):
        """Test compliance summary generation"""
        
        # Add some test reports first
        await compliance_manager.assess_compliance(
            "test_001", "audio", {
                "content_id": "test_001",
                "processing": {"lawful_basis": "consent", "legal_basis": "consent"},
                "consent": {"obtained": True, "voluntary": True},
                "security": {"encrypted": True, "encryption": True},
                "copyright": {"owner": "Test Owner"}
            },
            [ComplianceFramework.GDPR, ComplianceFramework.DMCA]
        )
        
        # Generate summary
        summary = await compliance_manager.get_compliance_summary()
        
        assert "total_reports" in summary
        assert "average_score" in summary
        assert "status_breakdown" in summary
        assert "framework_breakdown" in summary
        assert "compliance_rate" in summary
        
        assert summary["total_reports"] >= 2  # At least GDPR and DMCA reports
    
    @pytest.mark.asyncio
    async def test_compliance_metrics(self, compliance_manager):
        """Test compliance metrics collection"""
        
        metrics = await compliance_manager.get_metrics()
        
        assert "total_assessments" in metrics
        assert "compliance_rate" in metrics
        assert "critical_issues" in metrics
        assert "resolved_issues" in metrics
        assert "framework_coverage" in metrics
        assert "issue_breakdown" in metrics
        
        # Framework coverage should include all new frameworks
        assert metrics["framework_coverage"] >= 6  # GDPR, CCPA, DMCA, PIPEDA, LGPD, PDPA


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])