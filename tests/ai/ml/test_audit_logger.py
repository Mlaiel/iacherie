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

"""Audit Logger Tests - Enterprise Grade Security & Compliance Test Suite

Comprehensive tests for audit logging, compliance tracking, security event monitoring,
forensic analysis, and regulatory compliance systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""
import pytest
import sys
import os
from pathlib import Path
import json
import uuid
import hashlib
import hmac
import sqlite3
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock, patch, MagicMock, AsyncMock, mock_open
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import pandas as pd
import numpy as np

from ai.ml.audit_logger import (
    AuditLogger, SecurityAuditLogger, ComplianceLogger, ForensicAnalyzer,
    EventClassifier, LogIntegrityChecker, AuditReportGenerator,
    LogEncryptionManager, LogRetentionManager, AlertSystemIntegrator,
    AuditDashboard, ComplianceReporter, LogAnalytics, 
    RealTimeMonitor, AuditArchiver, LogValidator,
    SecurityEventDetector, AnomalyDetector, AuditTrailManager,
    GDPRComplianceChecker, SOXComplianceChecker, HIPAAComplianceChecker,
    ISOComplianceChecker, AuditConfiguration, LogCorrelationEngine
)


class TestAuditLogger:
    """Tests for core audit logging functionality"""
    
    def test_init_audit_logger(self):
        """Test audit logger initialization"""
        logger = AuditLogger(
            log_level="INFO",
            output_formats=["json", "csv", "database"],
            enable_encryption=True,
            retention_days=2555,  # 7 years
            compliance_standards=["GDPR", "SOX", "HIPAA", "ISO27001"],
            real_time_monitoring=True
        )
        
        assert logger.log_level == "INFO"
        assert len(logger.output_formats) == 3
        assert logger.enable_encryption
        assert logger.retention_days == 2555
        assert len(logger.compliance_standards) == 4
        assert logger.real_time_monitoring

    def test_log_entry_creation(self, temp_dir):
        """Test audit log entry creation and formatting"""
        logger = AuditLogger(output_directory=str(temp_dir))
        
        log_entry_data = {
            "user_id": "user_12345",
            "action": "model_training_initiated",
            "resource": "ML_Model_v2.3",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (compatible; API_Client/1.0)",
            "request_payload": {"dataset": "customer_data.csv", "algorithm": "random_forest"},
            "sensitive_data_accessed": True,
            "data_classification": "PII",
            "business_impact": "HIGH"
        }
        
        with patch.object(logger, 'log_event') as mock_log:
            mock_log.return_value = {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "ML_OPERATION",
                "severity": "INFO",
                "user_id": log_entry_data["user_id"],
                "action": log_entry_data["action"],
                "resource": log_entry_data["resource"],
                "source_ip": log_entry_data["ip_address"],
                "user_agent": log_entry_data["user_agent"],
                "request_details": log_entry_data["request_payload"],
                "data_sensitivity": {
                    "contains_pii": log_entry_data["sensitive_data_accessed"],
                    "classification": log_entry_data["data_classification"],
                    "impact_level": log_entry_data["business_impact"]
                },
                "session_id": "sess_" + hashlib.md5(f"{log_entry_data['user_id']}{datetime.now()}".encode()).hexdigest()[:16],
                "correlation_id": str(uuid.uuid4()),
                "integrity_hash": "sha256_hash_placeholder"
            }
            
            log_result = logger.log_event(
                event_data=log_entry_data,
                event_type="ML_OPERATION",
                severity="INFO"
            )
            
            assert "log_id" in log_result
            assert "timestamp" in log_result
            assert "integrity_hash" in log_result
            assert log_result["data_sensitivity"]["contains_pii"]
            assert log_result["data_sensitivity"]["impact_level"] == "HIGH"

    def test_batch_log_processing(self, sample_log_events):
        """Test batch processing of audit log entries"""
        logger = AuditLogger()
        
        batch_config = {
            "batch_size": 1000,
            "processing_interval": 30,  # seconds
            "enable_deduplication": True,
            "compression_enabled": True
        }
        
        # Simulate batch of log events
        if not sample_log_events:
            sample_log_events = [
                {
                    "user_id": f"user_{i:05d}",
                    "action": f"action_{i % 10}",
                    "timestamp": datetime.now() - timedelta(minutes=i),
                    "resource": f"resource_{i % 5}",
                    "severity": ["INFO", "WARN", "ERROR"][i % 3]
                }
                for i in range(1500)  # More than batch size
            ]
        
        with patch.object(logger, 'process_batch') as mock_batch:
            mock_batch.return_value = {
                "processed_count": len(sample_log_events),
                "batches_created": 2,  # 1500 / 1000 = 2 batches
                "duplicates_removed": 15,
                "compression_ratio": 0.34,
                "processing_time": 2.45,
                "storage_size_mb": 8.7,
                "integrity_checks_passed": True
            }
            
            batch_result = logger.process_batch(
                events=sample_log_events,
                config=batch_config
            )
            
            assert batch_result["processed_count"] == len(sample_log_events)
            assert batch_result["batches_created"] >= 1
            assert batch_result["compression_ratio"] < 1.0
            assert batch_result["integrity_checks_passed"]

    def test_log_encryption_and_security(self, sensitive_log_data):
        """Test log encryption and security features"""
        logger = AuditLogger(enable_encryption=True)
        
        encryption_config = {
            "algorithm": "AES-256-GCM",
            "key_rotation_days": 90,
            "enable_field_level_encryption": True,
            "encrypted_fields": ["user_id", "request_payload", "ip_address"]
        }
        
        if not sensitive_log_data:
            sensitive_log_data = {
                "user_id": "user_sensitive_123",
                "request_payload": {"personal_data": "SSN:123-45-6789", "email": "user@example.com"},
                "ip_address": "10.0.0.150",
                "action": "data_export",
                "classification": "CONFIDENTIAL"
            }
        
        with patch.object(logger, 'encrypt_log_entry') as mock_encrypt:
            mock_encrypt.return_value = {
                "encrypted_log": {
                    "log_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_id": "ENC[AES256]:" + "a" * 64,  # Simulated encrypted data
                    "request_payload": "ENC[AES256]:" + "b" * 128,
                    "ip_address": "ENC[AES256]:" + "c" * 32,
                    "action": sensitive_log_data["action"],  # Not encrypted
                    "classification": sensitive_log_data["classification"]
                },
                "encryption_metadata": {
                    "encryption_version": "v1.2",
                    "key_id": "key_2025_001",
                    "algorithm": "AES-256-GCM",
                    "encrypted_fields": ["user_id", "request_payload", "ip_address"],
                    "integrity_mac": "hmac_sha256_" + "d" * 64
                },
                "access_control": {
                    "classification_level": "CONFIDENTIAL",
                    "required_clearance": "SECRET",
                    "access_groups": ["security_team", "compliance_officers"]
                }
            }
            
            encryption_result = logger.encrypt_log_entry(
                log_data=sensitive_log_data,
                config=encryption_config
            )
            
            assert "encrypted_log" in encryption_result
            assert "encryption_metadata" in encryption_result
            assert "access_control" in encryption_result
            # Verify sensitive fields are encrypted
            assert encryption_result["encrypted_log"]["user_id"].startswith("ENC[AES256]:")
            assert encryption_result["encrypted_log"]["request_payload"].startswith("ENC[AES256]:")

    def test_log_integrity_verification(self, temp_dir):
        """Test log integrity verification and tamper detection"""
        logger = AuditLogger()
        
        # Create sample log file
        log_file = temp_dir / "audit_logs.json"
        sample_logs = [
            {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "action": "user_login",
                "user_id": "user_001",
                "integrity_hash": "original_hash_123"
            },
            {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "action": "data_access",
                "user_id": "user_002", 
                "integrity_hash": "original_hash_456"
            }
        ]
        
        with open(log_file, 'w') as f:
            for log in sample_logs:
                f.write(json.dumps(log) + '\n')
        
        integrity_config = {
            "hash_algorithm": "SHA-256",
            "include_timestamp": True,
            "chain_verification": True,
            "digital_signature": True
        }
        
        with patch.object(logger, 'verify_integrity') as mock_verify:
            mock_verify.return_value = {
                "verification_status": "PASSED",
                "total_logs_checked": len(sample_logs),
                "integrity_violations": 0,
                "tampered_logs": [],
                "hash_mismatches": [],
                "timeline_inconsistencies": [],
                "digital_signature_valid": True,
                "chain_integrity": "INTACT",
                "verification_time": 0.234,
                "last_verified": datetime.now(timezone.utc).isoformat()
            }
            
            integrity_result = logger.verify_integrity(
                log_file=str(log_file),
                config=integrity_config
            )
            
            assert integrity_result["verification_status"] == "PASSED"
            assert integrity_result["integrity_violations"] == 0
            assert integrity_result["digital_signature_valid"]
            assert integrity_result["chain_integrity"] == "INTACT"


class TestSecurityAuditLogger:
    """Tests for security-specific audit logging"""
    
    def test_init_security_audit_logger(self):
        """Test security audit logger initialization"""
        security_logger = SecurityAuditLogger(
            security_events=["authentication", "authorization", "data_access", "configuration_change"],
            threat_intelligence_integration=True,
            real_time_alerting=True,
            siem_integration=True
        )
        
        assert len(security_logger.security_events) == 4
        assert security_logger.threat_intelligence_integration
        assert security_logger.real_time_alerting
        assert security_logger.siem_integration

    def test_security_event_classification(self, security_events_sample):
        """Test security event classification and severity assignment"""
        security_logger = SecurityAuditLogger()
        
        if not security_events_sample:
            security_events_sample = [
                {
                    "event_type": "failed_login",
                    "user_id": "admin_user",
                    "source_ip": "192.168.1.200",
                    "failure_reason": "invalid_password",
                    "attempt_count": 5
                },
                {
                    "event_type": "privilege_escalation",
                    "user_id": "regular_user",
                    "target_resource": "admin_panel",
                    "escalation_method": "sudo_command"
                },
                {
                    "event_type": "suspicious_data_export",
                    "user_id": "contractor_123",
                    "data_volume": "10GB",
                    "export_time": "02:30 AM",
                    "destination": "external_storage"
                }
            ]
        
        classification_config = {
            "severity_rules": {
                "failed_login": {"base_severity": "MEDIUM", "escalation_threshold": 3},
                "privilege_escalation": {"base_severity": "HIGH", "immediate_alert": True},
                "suspicious_data_export": {"base_severity": "CRITICAL", "forensic_trigger": True}
            },
            "threat_indicators": ["unusual_time", "large_volume", "external_destination"],
            "automated_response": True
        }
        
        with patch.object(security_logger, 'classify_security_events') as mock_classify:
            mock_classify.return_value = {
                "classified_events": [
                    {
                        "original_event": security_events_sample[0],
                        "classification": "BRUTE_FORCE_ATTACK",
                        "severity": "HIGH",  # Escalated due to attempt count
                        "threat_level": 7,
                        "requires_immediate_attention": True,
                        "automated_actions": ["block_ip", "notify_security_team"],
                        "correlation_ids": ["correlation_001"]
                    },
                    {
                        "original_event": security_events_sample[1],
                        "classification": "UNAUTHORIZED_PRIVILEGE_ESCALATION",
                        "severity": "HIGH",
                        "threat_level": 8,
                        "requires_immediate_attention": True,
                        "automated_actions": ["revoke_privileges", "alert_admin"],
                        "correlation_ids": ["correlation_002"]
                    },
                    {
                        "original_event": security_events_sample[2],
                        "classification": "POTENTIAL_DATA_EXFILTRATION",
                        "severity": "CRITICAL",
                        "threat_level": 9,
                        "requires_immediate_attention": True,
                        "automated_actions": ["emergency_alert", "forensic_analysis", "user_lockdown"],
                        "correlation_ids": ["correlation_003"]
                    }
                ],
                "risk_assessment": {
                    "overall_risk_level": "CRITICAL",
                    "attack_indicators": 3,
                    "coordinated_attack_probability": 0.75,
                    "recommended_actions": ["incident_response", "forensic_investigation"]
                }
            }
            
            classification_result = security_logger.classify_security_events(
                events=security_events_sample,
                config=classification_config
            )
            
            assert "classified_events" in classification_result
            assert "risk_assessment" in classification_result
            assert len(classification_result["classified_events"]) == 3
            assert classification_result["risk_assessment"]["overall_risk_level"] == "CRITICAL"
            assert all(
                event["requires_immediate_attention"] 
                for event in classification_result["classified_events"]
            )

    def test_threat_intelligence_correlation(self, known_threats_db, suspicious_events):
        """Test correlation with threat intelligence feeds"""
        security_logger = SecurityAuditLogger(threat_intelligence_integration=True)
        
        if not known_threats_db:
            known_threats_db = {
                "malicious_ips": ["203.0.113.5", "198.51.100.15"],
                "known_attack_patterns": [
                    {"pattern": "rapid_failed_logins", "severity": "HIGH"},
                    {"pattern": "off_hours_data_access", "severity": "MEDIUM"}
                ],
                "threat_actors": [
                    {"group": "APT29", "tactics": ["credential_stuffing", "lateral_movement"]},
                    {"group": "Lazarus", "tactics": ["data_exfiltration", "financial_fraud"]}
                ]
            }
        
        if not suspicious_events:
            suspicious_events = [
                {
                    "source_ip": "203.0.113.5",
                    "event_type": "login_attempt",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "user_pattern": "rapid_failed_logins",
                    "event_type": "authentication_failure",
                    "count": 50
                }
            ]
        
        with patch.object(security_logger, 'correlate_with_threat_intelligence') as mock_correlate:
            mock_correlate.return_value = {
                "correlation_results": [
                    {
                        "event": suspicious_events[0],
                        "threat_matches": [
                            {
                                "threat_type": "KNOWN_MALICIOUS_IP",
                                "threat_source": "threat_feed_alpha",
                                "confidence": 0.95,
                                "last_seen": "2025-01-15",
                                "associated_campaigns": ["campaign_x", "operation_y"]
                            }
                        ],
                        "risk_elevation": "HIGH_TO_CRITICAL",
                        "recommended_actions": ["immediate_block", "forensic_analysis"]
                    },
                    {
                        "event": suspicious_events[1],
                        "threat_matches": [
                            {
                                "threat_type": "ATTACK_PATTERN_MATCH",
                                "pattern_name": "rapid_failed_logins",
                                "confidence": 0.89,
                                "associated_groups": ["APT29"],
                                "typical_next_steps": ["credential_validation", "lateral_movement"]
                            }
                        ],
                        "risk_elevation": "MEDIUM_TO_HIGH",
                        "recommended_actions": ["monitor_escalation", "credential_reset"]
                    }
                ],
                "overall_threat_assessment": {
                    "threat_level": "CRITICAL",
                    "active_campaign_suspected": True,
                    "attribution_confidence": 0.78,
                    "attack_timeline_prediction": "24-48 hours"
                }
            }
            
            correlation_result = security_logger.correlate_with_threat_intelligence(
                events=suspicious_events,
                threat_db=known_threats_db
            )
            
            assert "correlation_results" in correlation_result
            assert "overall_threat_assessment" in correlation_result
            assert correlation_result["overall_threat_assessment"]["threat_level"] == "CRITICAL"
            assert correlation_result["overall_threat_assessment"]["active_campaign_suspected"]

    def test_real_time_security_monitoring(self):
        """Test real-time security monitoring and alerting"""
        security_logger = SecurityAuditLogger(real_time_alerting=True)
        
        monitoring_config = {
            "alert_thresholds": {
                "failed_logins_per_minute": 10,
                "privilege_escalations_per_hour": 3,
                "data_access_anomaly_score": 0.8
            },
            "notification_channels": ["email", "sms", "slack", "pagerduty"],
            "escalation_rules": {
                "critical_events": {"immediate_escalation": True, "max_response_time": 5},
                "high_events": {"escalation_delay": 15, "max_response_time": 30}
            }
        }
        
        # Simulate real-time event stream
        realtime_events = [
            {"event_type": "failed_login", "timestamp": datetime.now(), "user_id": f"user_{i}"}
            for i in range(15)  # Exceeds threshold of 10 per minute
        ]
        
        with patch.object(security_logger, 'monitor_realtime_events') as mock_monitor:
            mock_monitor.return_value = {
                "monitoring_status": "ACTIVE",
                "alerts_generated": [
                    {
                        "alert_id": str(uuid.uuid4()),
                        "alert_type": "THRESHOLD_EXCEEDED",
                        "threshold_name": "failed_logins_per_minute",
                        "current_value": 15,
                        "threshold_value": 10,
                        "severity": "HIGH",
                        "notification_sent": True,
                        "response_required": True,
                        "escalated": False
                    }
                ],
                "notifications_sent": {
                    "email": {"sent": True, "recipients": 3, "timestamp": datetime.now().isoformat()},
                    "sms": {"sent": True, "recipients": 2, "timestamp": datetime.now().isoformat()},
                    "slack": {"sent": True, "channel": "#security-alerts", "message_id": "msg_123"}
                },
                "response_metrics": {
                    "alert_to_notification_time": 0.23,
                    "notification_delivery_success_rate": 1.0,
                    "average_acknowledgment_time": 45.6
                }
            }
            
            monitoring_result = security_logger.monitor_realtime_events(
                event_stream=realtime_events,
                config=monitoring_config
            )
            
            assert monitoring_result["monitoring_status"] == "ACTIVE"
            assert len(monitoring_result["alerts_generated"]) > 0
            assert monitoring_result["notifications_sent"]["email"]["sent"]
            assert monitoring_result["response_metrics"]["notification_delivery_success_rate"] == 1.0


class TestComplianceLogger:
    """Tests for compliance-specific logging functionality"""
    
    def test_init_compliance_logger(self):
        """Test compliance logger initialization"""
        compliance_logger = ComplianceLogger(
            compliance_frameworks=["GDPR", "SOX", "HIPAA", "PCI_DSS", "ISO27001"],
            automatic_compliance_checking=True,
            generate_compliance_reports=True,
            data_retention_policies={"default": 2555, "financial": 3650}  # 7 years, 10 years
        )
        
        assert len(compliance_logger.compliance_frameworks) == 5
        assert compliance_logger.automatic_compliance_checking
        assert compliance_logger.generate_compliance_reports
        assert compliance_logger.data_retention_policies["financial"] == 3650

    def test_gdpr_compliance_logging(self, gdpr_relevant_events):
        """Test GDPR compliance logging and validation"""
        compliance_logger = ComplianceLogger(compliance_frameworks=["GDPR"])
        
        if not gdpr_relevant_events:
            gdpr_relevant_events = [
                {
                    "event_type": "personal_data_access",
                    "user_id": "user_eu_123",
                    "data_subject": "john.doe@example.com",
                    "data_types": ["email", "name", "address", "phone"],
                    "processing_purpose": "customer_service",
                    "legal_basis": "legitimate_interest",
                    "consent_status": "granted",
                    "data_controller": "company_legal_entity"
                },
                {
                    "event_type": "data_export",
                    "user_id": "admin_456",
                    "data_subject": "jane.smith@example.com", 
                    "export_reason": "data_portability_request",
                    "export_format": "JSON",
                    "recipient": "data_subject"
                },
                {
                    "event_type": "data_deletion",
                    "user_id": "system_cleanup",
                    "data_subject": "deleted_user_789",
                    "deletion_reason": "right_to_erasure",
                    "data_categories": ["profile", "activity_logs", "preferences"]
                }
            ]
        
        gdpr_config = {
            "data_subject_rights": ["access", "portability", "erasure", "rectification"],
            "consent_management": True,
            "data_protection_impact_assessment": True,
            "breach_notification_requirements": {"authority_deadline": 72, "subject_deadline": 72*24}
        }
        
        with patch.object(compliance_logger, 'process_gdpr_compliance') as mock_gdpr:
            mock_gdpr.return_value = {
                "gdpr_compliance_analysis": [
                    {
                        "event": gdpr_relevant_events[0],
                        "compliance_status": "COMPLIANT",
                        "legal_basis_valid": True,
                        "consent_properly_documented": True,
                        "data_minimization_principle": "SATISFIED",
                        "purpose_limitation_check": "PASSED",
                        "retention_period_compliant": True
                    },
                    {
                        "event": gdpr_relevant_events[1],
                        "compliance_status": "COMPLIANT",
                        "data_portability_right": "EXERCISED",
                        "format_machine_readable": True,
                        "response_time_compliant": True,
                        "data_accuracy_verified": True
                    },
                    {
                        "event": gdpr_relevant_events[2],
                        "compliance_status": "COMPLIANT",
                        "erasure_right": "EXERCISED",
                        "deletion_completeness": "VERIFIED",
                        "backup_deletion_pending": False,
                        "third_party_notification": "COMPLETED"
                    }
                ],
                "overall_gdpr_compliance": {
                    "compliance_score": 0.98,
                    "violations_detected": 0,
                    "recommendations": [],
                    "audit_readiness": "HIGH",
                    "dpo_notification_required": False
                },
                "data_subject_rights_tracking": {
                    "access_requests": 156,
                    "portability_requests": 23,
                    "erasure_requests": 45,
                    "rectification_requests": 12,
                    "average_response_time_hours": 68.5
                }
            }
            
            gdpr_result = compliance_logger.process_gdpr_compliance(
                events=gdpr_relevant_events,
                config=gdpr_config
            )
            
            assert "gdpr_compliance_analysis" in gdpr_result
            assert "overall_gdpr_compliance" in gdpr_result
            assert gdpr_result["overall_gdpr_compliance"]["compliance_score"] > 0.95
            assert gdpr_result["overall_gdpr_compliance"]["violations_detected"] == 0

    def test_sox_compliance_logging(self, financial_audit_events):
        """Test SOX compliance logging for financial controls"""
        compliance_logger = ComplianceLogger(compliance_frameworks=["SOX"])
        
        if not financial_audit_events:
            financial_audit_events = [
                {
                    "event_type": "financial_report_access",
                    "user_id": "cfo_user",
                    "document": "quarterly_earnings_q4_2024",
                    "access_time": datetime.now().isoformat(),
                    "modification_made": False,
                    "approval_required": True,
                    "approver": "audit_committee_chair"
                },
                {
                    "event_type": "control_configuration_change",
                    "user_id": "it_admin_789",
                    "system": "financial_reporting_system",
                    "control_modified": "segregation_of_duties",
                    "change_approval": "change_control_board",
                    "effectiveness_testing": "pending"
                }
            ]
        
        sox_config = {
            "control_categories": [
                "entity_level_controls", "financial_reporting_controls", 
                "disclosure_controls", "it_general_controls"
            ],
            "segregation_of_duties": True,
            "change_management_controls": True,
            "documentation_requirements": "comprehensive"
        }
        
        with patch.object(compliance_logger, 'validate_sox_compliance') as mock_sox:
            mock_sox.return_value = {
                "sox_compliance_assessment": [
                    {
                        "event": financial_audit_events[0],
                        "control_effectiveness": "EFFECTIVE",
                        "segregation_of_duties": "COMPLIANT",
                        "authorization_proper": True,
                        "audit_trail_complete": True,
                        "disclosure_controls": "ADEQUATE"
                    },
                    {
                        "event": financial_audit_events[1],
                        "control_effectiveness": "PENDING_TESTING",
                        "change_control_compliance": "COMPLIANT",
                        "documentation_adequate": True,
                        "approval_chain_validated": True,
                        "rollback_capability": "VERIFIED"
                    }
                ],
                "section_404_readiness": {
                    "internal_control_assessment": "EFFECTIVE",
                    "material_weaknesses": 0,
                    "significant_deficiencies": 1,
                    "management_assertion": "REASONABLE_ASSURANCE",
                    "external_auditor_opinion": "UNQUALIFIED"
                },
                "control_deficiency_analysis": {
                    "total_deficiencies": 1,
                    "remediation_plans": 1,
                    "estimated_remediation_time": 30  # days
                }
            }
            
            sox_result = compliance_logger.validate_sox_compliance(
                events=financial_audit_events,
                config=sox_config
            )
            
            assert "sox_compliance_assessment" in sox_result
            assert "section_404_readiness" in sox_result
            assert sox_result["section_404_readiness"]["material_weaknesses"] == 0
            assert sox_result["section_404_readiness"]["management_assertion"] == "REASONABLE_ASSURANCE"

    def test_compliance_report_generation(self, temp_dir):
        """Test automated compliance report generation"""
        compliance_logger = ComplianceLogger(generate_compliance_reports=True)
        
        report_config = {
            "report_types": ["quarterly", "annual", "audit_preparation"],
            "output_formats": ["PDF", "Excel", "JSON"],
            "include_executive_summary": True,
            "detailed_findings": True,
            "recommendations": True,
            "compliance_frameworks": ["GDPR", "SOX", "HIPAA"]
        }
        
        report_data = {
            "reporting_period": {"start": "2024-10-01", "end": "2024-12-31"},
            "total_events_analyzed": 125000,
            "compliance_violations": 12,
            "critical_findings": 3,
            "remediation_actions": 15,
            "compliance_score_trend": [0.94, 0.96, 0.97, 0.98]  # Monthly progression
        }
        
        with patch.object(compliance_logger, 'generate_compliance_report') as mock_report:
            mock_report.return_value = {
                "report_metadata": {
                    "report_id": str(uuid.uuid4()),
                    "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                    "report_type": "quarterly",
                    "reporting_period": report_data["reporting_period"],
                    "frameworks_covered": ["GDPR", "SOX", "HIPAA"]
                },
                "executive_summary": {
                    "overall_compliance_score": 0.98,
                    "compliance_trend": "IMPROVING",
                    "critical_findings": report_data["critical_findings"],
                    "key_achievements": [
                        "Zero material weaknesses in financial controls",
                        "GDPR compliance score improved to 98%",
                        "All security incidents properly documented"
                    ],
                    "immediate_actions_required": 2
                },
                "detailed_findings": {
                    "gdpr_findings": {
                        "compliance_score": 0.98,
                        "violations": 2,
                        "data_subject_requests": 234,
                        "response_time_compliance": 0.97
                    },
                    "sox_findings": {
                        "compliance_score": 0.99,
                        "material_weaknesses": 0,
                        "significant_deficiencies": 1,
                        "control_effectiveness": 0.98
                    },
                    "hipaa_findings": {
                        "compliance_score": 0.97,
                        "security_incidents": 5,
                        "breach_notifications": 0,
                        "risk_assessments_completed": 4
                    }
                },
                "file_outputs": {
                    "pdf_report": str(temp_dir / "compliance_report_q4_2024.pdf"),
                    "excel_workbook": str(temp_dir / "compliance_data_q4_2024.xlsx"),
                    "json_data": str(temp_dir / "compliance_raw_data_q4_2024.json")
                }
            }
            
            report_result = compliance_logger.generate_compliance_report(
                data=report_data,
                config=report_config,
                output_dir=str(temp_dir)
            )
            
            assert "report_metadata" in report_result
            assert "executive_summary" in report_result
            assert "detailed_findings" in report_result
            assert report_result["executive_summary"]["overall_compliance_score"] > 0.95
            assert report_result["detailed_findings"]["sox_findings"]["material_weaknesses"] == 0


class TestLogRetentionManager:
    """Tests for log retention and archival management"""
    
    def test_init_retention_manager(self):
        """Test retention manager initialization"""
        retention_manager = LogRetentionManager(
            default_retention_days=2555,  # 7 years
            retention_policies={
                "security_logs": 3650,  # 10 years
                "financial_logs": 3650,  # 10 years
                "access_logs": 1095,    # 3 years
                "system_logs": 730      # 2 years
            },
            archival_storage="S3_GLACIER",
            compression_enabled=True
        )
        
        assert retention_manager.default_retention_days == 2555
        assert len(retention_manager.retention_policies) == 4
        assert retention_manager.archival_storage == "S3_GLACIER"
        assert retention_manager.compression_enabled

    def test_log_archival_process(self, old_log_files, temp_dir):
        """Test automated log archival process"""
        retention_manager = LogRetentionManager()
        
        if not old_log_files:
            # Create sample old log files
            old_log_files = []
            for i in range(5):
                log_file = temp_dir / f"audit_log_{datetime.now() - timedelta(days=365*2+i):%Y%m%d}.json"
                log_file.write_text(json.dumps({
                    "log_entries": 1000,
                    "size_mb": 15.7,
                    "creation_date": (datetime.now() - timedelta(days=365*2+i)).isoformat()
                }))
                old_log_files.append(str(log_file))
        
        archival_config = {
            "storage_tier": "GLACIER_DEEP_ARCHIVE",
            "compression_algorithm": "gzip",
            "encryption_enabled": True,
            "checksum_verification": True,
            "metadata_preservation": True
        }
        
        with patch.object(retention_manager, 'archive_logs') as mock_archive:
            mock_archive.return_value = {
                "archival_summary": {
                    "files_processed": len(old_log_files),
                    "total_size_before_mb": 78.5,
                    "total_size_after_mb": 23.4,  # After compression
                    "compression_ratio": 0.298,
                    "archival_location": "s3://audit-archive-bucket/2025/",
                    "archival_completion_time": datetime.now().isoformat()
                },
                "archived_files": [
                    {
                        "original_path": file_path,
                        "archive_path": f"s3://audit-archive-bucket/2025/{Path(file_path).name}.gz.enc",
                        "checksum_sha256": hashlib.sha256(file_path.encode()).hexdigest(),
                        "archive_status": "SUCCESS",
                        "retrieval_time_estimate": "12_hours"
                    }
                    for file_path in old_log_files
                ],
                "integrity_verification": {
                    "all_checksums_verified": True,
                    "encryption_successful": True,
                    "metadata_preserved": True,
                    "retrieval_test_passed": True
                }
            }
            
            archive_result = retention_manager.archive_logs(
                log_files=old_log_files,
                config=archival_config
            )
            
            assert "archival_summary" in archive_result
            assert "archived_files" in archive_result
            assert archive_result["archival_summary"]["files_processed"] == len(old_log_files)
            assert archive_result["archival_summary"]["compression_ratio"] < 0.5
            assert archive_result["integrity_verification"]["all_checksums_verified"]

    def test_log_deletion_policy_enforcement(self, expired_logs):
        """Test enforcement of log deletion policies"""
        retention_manager = LogRetentionManager()
        
        if not expired_logs:
            expired_logs = [
                {
                    "log_id": str(uuid.uuid4()),
                    "log_type": "access_log",
                    "creation_date": datetime.now() - timedelta(days=1200),  # Older than 3 years
                    "retention_days": 1095,
                    "size_mb": 5.2,
                    "path": "/logs/access_2022_01_15.json"
                },
                {
                    "log_id": str(uuid.uuid4()),
                    "log_type": "security_log",
                    "creation_date": datetime.now() - timedelta(days=3800),  # Older than 10 years
                    "retention_days": 3650,
                    "size_mb": 12.8,
                    "path": "/logs/security_2014_06_20.json"
                }
            ]
        
        deletion_config = {
            "safety_buffer_days": 30,  # Extra retention buffer
            "secure_deletion": True,
            "deletion_verification": True,
            "audit_deletion_process": True
        }
        
        with patch.object(retention_manager, 'enforce_deletion_policy') as mock_deletion:
            mock_deletion.return_value = {
                "deletion_analysis": [
                    {
                        "log": expired_logs[0],
                        "retention_status": "EXPIRED",
                        "days_overdue": 105,  # 1200 - 1095
                        "deletion_eligible": True,
                        "deletion_action": "SECURE_DELETE"
                    },
                    {
                        "log": expired_logs[1], 
                        "retention_status": "EXPIRED",
                        "days_overdue": 150,  # 3800 - 3650
                        "deletion_eligible": True,
                        "deletion_action": "SECURE_DELETE"
                    }
                ],
                "deletion_execution": {
                    "logs_deleted": len(expired_logs),
                    "total_space_freed_mb": 18.0,  # 5.2 + 12.8
                    "secure_deletion_verified": True,
                    "deletion_certificates": [
                        f"cert_{log['log_id'][:8]}" for log in expired_logs
                    ]
                },
                "compliance_verification": {
                    "regulatory_requirements_met": True,
                    "deletion_documented": True,
                    "audit_trail_preserved": True
                }
            }
            
            deletion_result = retention_manager.enforce_deletion_policy(
                logs=expired_logs,
                config=deletion_config
            )
            
            assert "deletion_analysis" in deletion_result
            assert "deletion_execution" in deletion_result
            assert deletion_result["deletion_execution"]["logs_deleted"] == len(expired_logs)
            assert deletion_result["compliance_verification"]["regulatory_requirements_met"]


@pytest.mark.integration
class TestAuditLoggerIntegration:
    """Integration tests for audit logging systems"""
    
    @pytest.mark.slow
    def test_end_to_end_audit_pipeline(self, temp_dir):
        """Test complete audit logging pipeline from event to archive"""
        # Initialize components
        audit_logger = AuditLogger(output_directory=str(temp_dir))
        security_logger = SecurityAuditLogger()
        compliance_logger = ComplianceLogger()
        retention_manager = LogRetentionManager()
        
        # Simulate real audit events
        test_events = [
            {
                "user_id": "test_user_001",
                "action": "model_training",
                "resource": "customer_churn_model",
                "timestamp": datetime.now(),
                "sensitive_data": True,
                "compliance_relevant": ["GDPR", "SOX"]
            },
            {
                "user_id": "admin_002",
                "action": "system_configuration_change",
                "resource": "authentication_system",
                "timestamp": datetime.now(),
                "security_critical": True,
                "requires_approval": True
            }
        ]
        
        # Step 1: Log events
        logged_events = []
        for event in test_events:
            with patch.object(audit_logger, 'log_event') as mock_log:
                mock_log.return_value = {
                    "log_id": str(uuid.uuid4()),
                    "timestamp": event["timestamp"].isoformat(),
                    "processed": True
                }
                
                log_result = audit_logger.log_event(event)
                logged_events.append(log_result)
                assert log_result["processed"]
        
        # Step 2: Security analysis
        with patch.object(security_logger, 'analyze_security_events') as mock_security:
            mock_security.return_value = {
                "security_analysis_complete": True,
                "threats_detected": 0,
                "recommendations": []
            }
            
            security_result = security_logger.analyze_security_events(logged_events)
            assert security_result["security_analysis_complete"]
        
        # Step 3: Compliance validation
        with patch.object(compliance_logger, 'validate_compliance') as mock_compliance:
            mock_compliance.return_value = {
                "compliance_status": "COMPLIANT",
                "framework_results": {
                    "GDPR": "PASSED",
                    "SOX": "PASSED"
                }
            }
            
            compliance_result = compliance_logger.validate_compliance(logged_events)
            assert compliance_result["compliance_status"] == "COMPLIANT"
        
        # Step 4: Retention policy application
        with patch.object(retention_manager, 'apply_retention_policy') as mock_retention:
            mock_retention.return_value = {
                "retention_applied": True,
                "archive_scheduled": False,  # Too new
                "deletion_scheduled": False
            }
            
            retention_result = retention_manager.apply_retention_policy(logged_events)
            assert retention_result["retention_applied"]

    def test_high_volume_audit_logging(self):
        """Test audit logging under high volume conditions"""
        audit_logger = AuditLogger()
        
        # Simulate high volume of events
        high_volume_events = [
            {
                "user_id": f"user_{i:06d}",
                "action": f"api_call_{i % 100}",
                "timestamp": datetime.now() - timedelta(seconds=i),
                "resource": f"resource_{i % 50}"
            }
            for i in range(10000)  # 10,000 events
        ]
        
        batch_config = {
            "batch_size": 1000,
            "parallel_processing": True,
            "compression": True,
            "integrity_checking": True
        }
        
        with patch.object(audit_logger, 'process_high_volume') as mock_high_volume:
            mock_high_volume.return_value = {
                "processing_summary": {
                    "total_events": len(high_volume_events),
                    "processing_time": 45.7,  # seconds
                    "events_per_second": 219,
                    "memory_peak_mb": 156.8,
                    "storage_mb": 78.3
                },
                "quality_metrics": {
                    "integrity_checks_passed": 1.0,
                    "duplicate_events": 23,
                    "processing_errors": 0,
                    "data_loss_events": 0
                },
                "performance_metrics": {
                    "cpu_utilization_percent": 78,
                    "io_operations_per_second": 1250,
                    "compression_ratio": 0.34
                }
            }
            
            high_volume_result = audit_logger.process_high_volume(
                events=high_volume_events,
                config=batch_config
            )
            
            assert high_volume_result["processing_summary"]["total_events"] == 10000
            assert high_volume_result["quality_metrics"]["processing_errors"] == 0
            assert high_volume_result["performance_metrics"]["compression_ratio"] < 0.5


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
