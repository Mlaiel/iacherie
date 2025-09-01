# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive Security Audit and Compliance Test Suite
Tests for security audit trail, monitoring, and compliance features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
import uuid

# Import the modules we're testing
from security.audit_trail import (
    SecurityAuditTrail, AuditTrailLevel, SecurityAuditEvent,
    log_security_audit, log_authentication_event, log_data_access_event
)
from security.monitoring import (
    SecurityMonitoringDashboard, IncidentSeverity, IncidentStatus, SecurityIncident,
    get_security_status, create_security_incident
)
from security.policies import (
    SecurityPolicyManager, PolicyType, PolicyStatus, SecurityPolicy,
    get_security_policies, get_policy_compliance_report
)
from security.vulnerability_scanner import SecurityScanner, VulnerabilitySeverity


class TestSecurityAuditTrail:
    """
Test security audit trail functionality"""
    
    @pytest.fixture
    async def audit_trail(self):
        """
Create audit trail instance for testing"""
        return SecurityAuditTrail()
    
    @pytest.mark.asyncio
    async def test_log_security_event(self, audit_trail):
        """
Test logging security events"""
        
        event_id = await audit_trail.log_security_event(
            action="test_login",
            resource="user:test_user",
            level=AuditTrailLevel.SECURITY,
            user_id="test_user",
            ip_address="192.168.1.100",
            success=True,
            details={"method": "password"}
        )
        
        assert event_id is not None
        assert len(audit_trail.events_cache) == 1
        
        event = audit_trail.events_cache[0]
        assert event.action == "test_login"
        assert event.resource == "user:test_user"
        assert event.level == AuditTrailLevel.SECURITY
        assert event.user_id == "test_user"
        assert event.success is True
    
    @pytest.mark.asyncio
    async def test_get_audit_trail_filtering(self, audit_trail):
        """Test audit trail filtering"""
        
        # Log multiple events
        await audit_trail.log_security_event(
            action="login",
            resource="user:alice",
            level=AuditTrailLevel.INFO,
            user_id="alice"
        )
        
        await audit_trail.log_security_event(
            action="data_access",
            resource="file:sensitive.txt",
            level=AuditTrailLevel.SECURITY,
            user_id="bob"
        )
        
        await audit_trail.log_security_event(
            action="login_failed",
            resource="user:charlie",
            level=AuditTrailLevel.CRITICAL,
            user_id="charlie",
            success=False
        )
        
        # Test filtering by level
        security_events = await audit_trail.get_audit_trail(level=AuditTrailLevel.SECURITY)
        assert len(security_events) == 1
        assert security_events[0].action == "data_access"
        
        # Test filtering by user
        alice_events = await audit_trail.get_audit_trail(user_id="alice")
        assert len(alice_events) == 1
        assert alice_events[0].user_id == "alice"
        
        # Test filtering by action
        login_events = await audit_trail.get_audit_trail(action="login")
        assert len(login_events) == 2  # login and login_failed
    
    @pytest.mark.asyncio
    async def test_compliance_report_generation(self, audit_trail):
        """Test compliance report generation"""
        
        # Log events with compliance flags
        await audit_trail.log_security_event(
            action="data_access",
            resource="personal_data:user_123",
            level=AuditTrailLevel.COMPLIANCE,
            compliance_flags=["GDPR", "CCPA"]
        )
        
        await audit_trail.log_security_event(
            action="payment_processing",
            resource="payment:card_data",
            level=AuditTrailLevel.COMPLIANCE,
            compliance_flags=["PCI_DSS"]
        )
        
        # Generate compliance report
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        report = await audit_trail.generate_compliance_report(
            start_time=start_time,
            end_time=end_time,
            compliance_standard="GDPR"
        )
        
        assert report["compliance_standard"] == "GDPR"
        assert report["compliance_relevant_events"] == 1
        assert "event_breakdown" in report
        assert "events" in report
    
    @pytest.mark.asyncio
    async def test_audit_integrity_verification(self, audit_trail):
        """Test audit trail integrity verification"""
        
        # Log some events
        await audit_trail.log_security_event(
            action="test1",
            resource="resource1"
        )
        
        await audit_trail.log_security_event(
            action="test2",
            resource="resource2"
        )
        
        # Verify integrity
        integrity_result = await audit_trail.verify_audit_integrity()
        
        assert integrity_result["status"] == "verified"
        assert integrity_result["total_events"] == 2
        assert "last_event_hash" in integrity_result
    
    @pytest.mark.asyncio
    async def test_helper_functions(self):
        """Test helper functions"""
        
        # Test authentication event logging
        event_id = await log_authentication_event(
            user_id="test_user",
            success=True,
            ip_address="192.168.1.100"
        )
        assert event_id is not None
        
        # Test data access event logging
        event_id = await log_data_access_event(
            user_id="test_user",
            resource="sensitive_file.pdf",
            action="download",
            success=True
        )
        assert event_id is not None


class TestSecurityMonitoring:
    """Test security monitoring dashboard functionality"""
    
    @pytest.fixture
    async def monitoring_dashboard(self):
        """
Create monitoring dashboard instance for testing"""
        return SecurityMonitoringDashboard()
    
    @pytest.mark.asyncio
    async def test_create_incident(self, monitoring_dashboard):
        """
Test security incident creation"""
        
        incident_id = await monitoring_dashboard.create_incident(
            title="Suspicious Login Activity",
            description="Multiple failed login attempts detected",
            severity=IncidentSeverity.MEDIUM,
            affected_systems=["web_server", "database"],
            indicators=["brute_force", "geo_anomaly"]
        )
        
        assert incident_id is not None
        assert len(monitoring_dashboard.active_incidents) == 1
        
        incident = monitoring_dashboard.active_incidents[0]
        assert incident.title == "Suspicious Login Activity"
        assert incident.severity == IncidentSeverity.MEDIUM
        assert "web_server" in incident.affected_systems
    
    @pytest.mark.asyncio
    async def test_update_incident_status(self, monitoring_dashboard):
        """Test incident status updates"""
        
        # Create incident
        incident_id = await monitoring_dashboard.create_incident(
            title="Test Incident",
            description="Test incident for status updates",
            severity=IncidentSeverity.LOW
        )
        
        # Update to investigating
        success = await monitoring_dashboard.update_incident_status(
            incident_id=incident_id,
            status=IncidentStatus.INVESTIGATING,
            assigned_to="security_analyst_1",
            response_action="Initial triage completed"
        )
        
        assert success is True
        
        incident = monitoring_dashboard.active_incidents[0]
        assert incident.status == IncidentStatus.INVESTIGATING
        assert incident.assigned_to == "security_analyst_1"
        assert len(incident.response_actions) == 1
        
        # Update to resolved
        await monitoring_dashboard.update_incident_status(
            incident_id=incident_id,
            status=IncidentStatus.RESOLVED
        )
        
        incident = monitoring_dashboard.active_incidents[0]
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolved_at is not None
        
        # Close incident
        await monitoring_dashboard.update_incident_status(
            incident_id=incident_id,
            status=IncidentStatus.CLOSED
        )
        
        # Should be moved to history
        assert len(monitoring_dashboard.active_incidents) == 0
        assert len(monitoring_dashboard.incident_history) == 1
    
    @pytest.mark.asyncio
    async def test_generate_incident_report(self, monitoring_dashboard):
        """Test incident report generation"""
        
        # Create and resolve incident
        incident_id = await monitoring_dashboard.create_incident(
            title="Test Incident Report",
            description="Testing incident reporting",
            severity=IncidentSeverity.HIGH,
            affected_systems=["system1"],
            indicators=["test_indicator"]
        )
        
        await monitoring_dashboard.update_incident_status(
            incident_id=incident_id,
            status=IncidentStatus.RESOLVED,
            response_action="Test action taken"
        )
        
        # Generate report
        report = await monitoring_dashboard.generate_incident_report(incident_id)
        
        assert report is not None
        assert report["incident_details"]["incident_id"] == incident_id
        assert "timeline" in report
        assert "impact_assessment" in report
        assert "response_summary" in report
        assert "lessons_learned" in report
    
    @pytest.mark.asyncio
    async def test_security_dashboard_data(self, monitoring_dashboard):
        """Test security dashboard data retrieval"""
        
        # Create some test incidents
        await monitoring_dashboard.create_incident(
            title="Critical Issue",
            description="Critical security incident",
            severity=IncidentSeverity.CRITICAL
        )
        
        await monitoring_dashboard.create_incident(
            title="Medium Issue",
            description="Medium security incident",
            severity=IncidentSeverity.MEDIUM
        )
        
        # Get dashboard data
        dashboard_data = await monitoring_dashboard.get_security_dashboard()
        
        assert "timestamp" in dashboard_data
        assert "security_overview" in dashboard_data
        assert "vulnerability_status" in dashboard_data
        assert "audit_summary" in dashboard_data
        assert "incident_status" in dashboard_data
        assert "compliance_status" in dashboard_data
        assert "threat_intelligence" in dashboard_data
        assert "system_health" in dashboard_data
        
        # Check incident status data
        incident_status = dashboard_data["incident_status"]
        assert incident_status["active_incidents"] == 2
        assert incident_status["escalated_incidents"] == 1  # One critical
    
    @pytest.mark.asyncio
    async def test_helper_functions(self):
        """Test helper functions"""
        
        # Test get security status
        status = await get_security_status()
        assert isinstance(status, dict)
        assert "timestamp" in status
        
        # Test create security incident
        incident_id = await create_security_incident(
            title="Test Helper Incident",
            description="Testing helper function",
            severity="high",
            affected_systems=["test_system"]
        )
        assert incident_id is not None


class TestSecurityPolicies:
    """Test security policies and incident response procedures"""
    
    @pytest.fixture
    async def policy_manager(self):
        """
Create policy manager instance for testing"""
        return SecurityPolicyManager()
    
    @pytest.mark.asyncio
    async def test_get_standard_policies(self, policy_manager):
        """
Test retrieval of standard policies"""
        
        policies = await policy_manager.get_all_policies()
        assert len(policies) >= 5  # Should have at least 5 standard policies
        
        # Check for key policies
        policy_titles = [p.title for p in policies]
        assert any("Access Control" in title for title in policy_titles)
        assert any("Data Protection" in title for title in policy_titles)
        assert any("Incident Response" in title for title in policy_titles)
        assert any("Vulnerability Management" in title for title in policy_titles)
        assert any("Network Security" in title for title in policy_titles)
    
    @pytest.mark.asyncio
    async def test_add_custom_policy(self, policy_manager):
        """Test adding custom security policy"""
        
        custom_policy = SecurityPolicy(
            policy_id="TEST-POL-001",
            title="Test Security Policy",
            policy_type=PolicyType.COMPLIANCE,
            description="Test policy for unit testing",
            requirements=["Test requirement 1", "Test requirement 2"],
            compliance_frameworks=["TEST_FRAMEWORK"]
        )
        
        policy_id = await policy_manager.add_policy(custom_policy)
        assert policy_id == "TEST-POL-001"
        
        retrieved_policy = await policy_manager.get_policy(policy_id)
        assert retrieved_policy is not None
        assert retrieved_policy.title == "Test Security Policy"
        assert retrieved_policy.policy_type == PolicyType.COMPLIANCE
    
    @pytest.mark.asyncio
    async def test_policy_status_updates(self, policy_manager):
        """Test policy status updates"""
        
        # Get an existing policy
        policies = await policy_manager.get_all_policies()
        test_policy = policies[0]
        
        # Update status to under review
        success = await policy_manager.update_policy_status(
            policy_id=test_policy.policy_id,
            status=PolicyStatus.UNDER_REVIEW
        )
        assert success is True
        
        updated_policy = await policy_manager.get_policy(test_policy.policy_id)
        assert updated_policy.status == PolicyStatus.UNDER_REVIEW
        
        # Approve policy
        await policy_manager.update_policy_status(
            policy_id=test_policy.policy_id,
            status=PolicyStatus.APPROVED,
            approved_by="test_approver"
        )
        
        approved_policy = await policy_manager.get_policy(test_policy.policy_id)
        assert approved_policy.status == PolicyStatus.APPROVED
        assert approved_policy.approved_by == "test_approver"
        assert approved_policy.last_review_date is not None
        assert approved_policy.next_review_date is not None
    
    @pytest.mark.asyncio
    async def test_policies_by_type(self, policy_manager):
        """Test retrieving policies by type"""
        
        access_policies = await policy_manager.get_policies_by_type(PolicyType.ACCESS_CONTROL)
        assert len(access_policies) >= 1
        
        for policy in access_policies:
            assert policy.policy_type == PolicyType.ACCESS_CONTROL
    
    @pytest.mark.asyncio
    async def test_policy_compliance_report(self, policy_manager):
        """
Test policy compliance report generation"""
        
        report = await policy_manager.generate_policy_compliance_report()
        
        assert "report_date" in report
        assert "summary" in report
        assert "breakdown" in report
        assert "compliance_frameworks" in report
        
        summary = report["summary"]
        assert "total_policies" in summary
        assert "implemented_policies" in summary
        assert "compliance_score" in summary
        assert "policies_due_review" in summary
        
        breakdown = report["breakdown"]
        assert "by_status" in breakdown
        assert "by_type" in breakdown
    
    @pytest.mark.asyncio
    async def test_incident_response_procedures(self, policy_manager):
        """Test incident response procedure execution"""
        
        # Test data breach response
        response = await policy_manager.execute_incident_response(
            incident_id="TEST-INC-001",
            incident_type="data_breach",
            severity="high",
            phase="detection"
        )
        
        assert response["status"] == "success"
        assert response["incident_id"] == "TEST-INC-001"
        assert response["phase"] == "detection"
        assert response["procedures_executed"] > 0
        assert "execution_log" in response
        assert "escalation_required" in response
        assert response["next_recommended_phase"] == "containment"
    
    @pytest.mark.asyncio
    async def test_incident_communication_generation(self, policy_manager):
        """Test incident communication generation"""
        
        incident_data = {
            "incident_id": "TEST-INC-002",
            "incident_type": "malware_infection",
            "severity": "CRITICAL",
            "detection_time": datetime.now(timezone.utc).isoformat(),
            "initial_assessment": "Malware detected on multiple systems",
            "actions_taken": "Systems isolated, scanning initiated",
            "next_steps": "Full system cleanup and forensic analysis",
            "poc_name": "Security Team",
            "poc_contact": "security@company.com"
        }
        
        communication = await policy_manager.generate_incident_communication(
            template_type="initial_alert",
            incident_data=incident_data
        )
        
        assert "subject" in communication
        assert "body" in communication
        assert "TEST-INC-002" in communication["subject"]
        assert "CRITICAL" in communication["subject"]
        assert "malware_infection" in communication["body"]
    
    @pytest.mark.asyncio
    async def test_helper_functions(self):
        """Test helper functions"""
        
        # Test get security policies
        policies = await get_security_policies()
        assert isinstance(policies, list)
        assert len(policies) > 0
        assert all(isinstance(p, dict) for p in policies)
        
        # Test get policy compliance report
        report = await get_policy_compliance_report()
        assert isinstance(report, dict)
        assert "summary" in report


class TestSecurityIntegration:
    """Integration tests for security audit and compliance system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_incident_workflow(self):
        """
Test complete incident workflow from detection to resolution"""
        
        # 1. Create security incident
        incident_id = await create_security_incident(
            title="Suspicious Data Access",
            description="Unusual data access patterns detected",
            severity="high",
            affected_systems=["database", "web_app"]
        )
        
        # 2. Log security events related to incident
        await log_security_audit(
            action="suspicious_data_access",
            resource="database:sensitive_table",
            level=AuditTrailLevel.SECURITY,
            user_id="unknown_user",
            ip_address="192.168.1.200",
            success=False,
            details={"attempted_records": 1000, "blocked": True}
        )
        
        # 3. Execute incident response procedure
        from security.policies import security_policy_manager
        
        response = await security_policy_manager.execute_incident_response(
            incident_id=incident_id,
            incident_type="data_breach",
            severity="high",
            phase="detection"
        )
        
        assert response["status"] == "success"
        
        # 4. Update incident status
        from security.monitoring import security_dashboard
        
        await security_dashboard.update_incident_status(
            incident_id=incident_id,
            status=IncidentStatus.INVESTIGATING,
            assigned_to="security_analyst"
        )
        
        # 5. Generate incident report
        report = await security_dashboard.generate_incident_report(incident_id)
        assert report is not None
        
        # 6. Verify audit trail
        from security.audit_trail import security_audit_trail
        
        events = await security_audit_trail.get_audit_trail(limit=10)
        incident_events = [e for e in events if incident_id in str(e.details)]
        assert len(incident_events) > 0
    
    @pytest.mark.asyncio
    async def test_compliance_reporting_integration(self):
        """Test compliance reporting across all modules"""
        
        # Log various compliance-related events
        await log_data_access_event(
            user_id="gdpr_test_user",
            resource="personal_data:eu_citizen_123",
            action="view",
            success=True,
            details={"data_type": "personal_info", "purpose": "customer_service"}
        )
        
        await log_authentication_event(
            user_id="sox_test_user",
            success=False,
            details={"attempted_role": "financial_admin", "blocked_reason": "mfa_required"}
        )
        
        # Generate comprehensive compliance report
        from security.audit_trail import security_audit_trail
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        gdpr_report = await security_audit_trail.generate_compliance_report(
            start_time=start_time,
            end_time=end_time,
            compliance_standard="GDPR"
        )
        
        assert gdpr_report["compliance_standard"] == "GDPR"
        assert gdpr_report["total_events"] > 0
        
        # Get policy compliance report
        policy_report = await get_policy_compliance_report()
        assert policy_report["summary"]["compliance_score"] > 0
        
        # Get security dashboard with compliance status
        dashboard = await get_security_status()
        assert "compliance_status" in dashboard
    
    @pytest.mark.asyncio
    async def test_vulnerability_scanning_integration(self):
        """Test vulnerability scanning integration with audit trail"""
        
        scanner = SecurityScanner()
        
        # Run vulnerability scan
        scan_result = await scanner.run_comprehensive_security_scan()
        
        assert scan_result.scan_id is not None
        assert scan_result.compliance_status in ["COMPLIANT", "NON_COMPLIANT"]
        
        # Get compliance status
        compliance_status = await scanner.get_compliance_status()
        assert "status" in compliance_status
        assert "compliant" in compliance_status
        
        # Generate vulnerability report
        vuln_report = await scanner.get_vulnerability_report()
        if vuln_report.get("error"):
            # No scan data available, which is acceptable for tests
            pass
        else:
            assert "scan_summary" in vuln_report
            assert "compliance_check" in vuln_report


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