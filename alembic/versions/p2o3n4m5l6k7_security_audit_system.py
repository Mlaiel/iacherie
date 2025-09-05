"""Security audit system with GDPR/CCPA compliance

Revision ID: p2o3n4m5l6k7
Revises: o1n2m3l4k5j6
Create Date: 2025-09-05 07:15:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the comprehensive security audit system with complete
audit trails, GDPR/CCPA compliance, threat detection AI, and advanced
security monitoring for enterprise-grade protection.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'p2o3n4m5l6k7'
down_revision = 'o1n2m3l4k5j6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Security audit system with compliance."""
    
    # Create audit event type enum
    audit_event_type_enum = sa.Enum(
        'user_authentication', 'user_authorization', 'data_access', 'data_modification',
        'data_deletion', 'data_export', 'privacy_setting_change', 'account_creation',
        'account_deletion', 'password_change', 'email_change', 'profile_update',
        'content_upload', 'content_deletion', 'content_sharing', 'payment_transaction',
        'subscription_change', 'integration_connection', 'api_access', 'admin_action',
        'security_incident', 'privacy_violation', 'compliance_check', 'data_breach',
        'suspicious_activity', 'fraud_detection', 'malware_detection', 'vulnerability_scan',
        name='audit_event_type'
    )
    
    # Create compliance framework enum
    compliance_framework_enum = sa.Enum(
        'gdpr', 'ccpa', 'pipeda', 'lgpd', 'pdpa_singapore', 'pdpa_thailand',
        'pdpo_hong_kong', 'dpa_uk', 'bdsg_germany', 'cnil_france', 'aepd_spain',
        'garanteprivacy_italy', 'uodo_poland', 'naih_hungary', 'aki_estonia',
        'dvi_latvia', 'ada_lithuania', 'dpa_ireland', 'dpa_netherlands',
        'dpa_belgium', 'dpa_austria', 'edoeb_switzerland', 'datatilsynet_norway',
        'datatilsynet_denmark', 'datainspektionen_sweden', 'tietosuojavaltuutettu_finland',
        name='compliance_framework'
    )
    
    # Create security level enum
    security_level_enum = sa.Enum(
        'public', 'internal', 'confidential', 'restricted', 'top_secret',
        'personal_data', 'sensitive_personal_data', 'financial_data', 'health_data',
        name='security_level'
    )
    
    # Create threat severity enum
    threat_severity_enum = sa.Enum(
        'informational', 'low', 'medium', 'high', 'critical', 'emergency',
        name='threat_severity'
    )
    
    # Create comprehensive audit logs table
    op.create_table('comprehensive_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_id', sa.String(100), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('session_id', sa.String(100)),
        sa.Column('event_type', audit_event_type_enum, nullable=False),
        sa.Column('event_category', sa.String(50), nullable=False),
        sa.Column('event_description', sa.Text, nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(200)),
        sa.Column('resource_name', sa.String(500)),
        sa.Column('action_performed', sa.String(100), nullable=False),
        sa.Column('action_result', sa.String(20), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text),
        sa.Column('geolocation', postgresql.JSONB),
        sa.Column('device_fingerprint', sa.String(256)),
        sa.Column('request_method', sa.String(10)),
        sa.Column('request_url', sa.String(2000)),
        sa.Column('request_headers', postgresql.JSONB),
        sa.Column('request_parameters', postgresql.JSONB),
        sa.Column('response_status_code', sa.Integer),
        sa.Column('response_size_bytes', sa.BigInteger),
        sa.Column('processing_time_ms', sa.Float),
        sa.Column('before_values', postgresql.JSONB),
        sa.Column('after_values', postgresql.JSONB),
        sa.Column('sensitive_data_accessed', sa.Boolean, nullable=False, default=False),
        sa.Column('data_classification', security_level_enum),
        sa.Column('compliance_relevant', sa.Boolean, nullable=False, default=False),
        sa.Column('compliance_frameworks', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('retention_period_days', sa.Integer, nullable=False, default=2555),
        sa.Column('encryption_applied', sa.Boolean, nullable=False, default=True),
        sa.Column('anonymization_applied', sa.Boolean, nullable=False, default=False),
        sa.Column('risk_score', sa.Float, nullable=False, default=0.0),
        sa.Column('fraud_indicators', postgresql.JSONB),
        sa.Column('anomaly_score', sa.Float, nullable=False, default=0.0),
        sa.Column('correlation_id', sa.String(100)),
        sa.Column('parent_event_id', sa.String(100)),
        sa.Column('event_chain', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('tamper_proof_hash', sa.String(512)),
        sa.Column('digital_signature', sa.Text),
        sa.Column('blockchain_reference', sa.String(200)),
        sa.Column('archived', sa.Boolean, nullable=False, default=False),
        sa.Column('archive_date', sa.DateTime),
        sa.Column('purge_eligible_date', sa.DateTime),
        sa.Column('legal_hold', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create GDPR compliance tracking table
    op.create_table('gdpr_compliance_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('data_subject_id', sa.String(100), nullable=False),
        sa.Column('legal_basis', sa.String(50), nullable=False),
        sa.Column('consent_given', sa.Boolean, nullable=False, default=False),
        sa.Column('consent_timestamp', sa.DateTime),
        sa.Column('consent_method', sa.String(50)),
        sa.Column('consent_version', sa.String(20)),
        sa.Column('consent_text', sa.Text),
        sa.Column('consent_withdrawal_date', sa.DateTime),
        sa.Column('withdrawal_method', sa.String(50)),
        sa.Column('data_categories_processed', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('processing_purposes', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('data_sources', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('data_recipients', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('third_party_transfers', postgresql.JSONB),
        sa.Column('international_transfers', postgresql.JSONB),
        sa.Column('adequacy_decisions', postgresql.JSONB),
        sa.Column('safeguards_applied', postgresql.JSONB),
        sa.Column('retention_periods', postgresql.JSONB),
        sa.Column('automated_decision_making', sa.Boolean, nullable=False, default=False),
        sa.Column('profiling_activities', postgresql.JSONB),
        sa.Column('data_protection_impact_assessment', postgresql.JSONB),
        sa.Column('legitimate_interests_assessment', postgresql.JSONB),
        sa.Column('data_minimization_compliance', sa.Boolean, nullable=False, default=True),
        sa.Column('accuracy_maintenance', postgresql.JSONB),
        sa.Column('storage_limitation_compliance', sa.Boolean, nullable=False, default=True),
        sa.Column('integrity_confidentiality_measures', postgresql.JSONB),
        sa.Column('accountability_measures', postgresql.JSONB),
        sa.Column('data_subject_rights_exercised', postgresql.JSONB),
        sa.Column('rectification_requests', postgresql.JSONB),
        sa.Column('erasure_requests', postgresql.JSONB),
        sa.Column('restriction_requests', postgresql.JSONB),
        sa.Column('portability_requests', postgresql.JSONB),
        sa.Column('objection_requests', postgresql.JSONB),
        sa.Column('breach_notifications', postgresql.JSONB),
        sa.Column('supervisory_authority_communications', postgresql.JSONB),
        sa.Column('compliance_score', sa.Float, nullable=False, default=100.0),
        sa.Column('last_compliance_review', sa.DateTime),
        sa.Column('next_compliance_review', sa.DateTime),
        sa.Column('compliance_officer', sa.String(200)),
        sa.Column('dpo_involved', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create CCPA compliance tracking table
    op.create_table('ccpa_compliance_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('consumer_id', sa.String(100), nullable=False),
        sa.Column('california_resident', sa.Boolean, nullable=False, default=False),
        sa.Column('personal_information_categories', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('sensitive_personal_information', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('business_purposes', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('commercial_purposes', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('information_sources', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('third_party_disclosures', postgresql.JSONB),
        sa.Column('service_provider_disclosures', postgresql.JSONB),
        sa.Column('cross_context_behavioral_advertising', sa.Boolean, nullable=False, default=False),
        sa.Column('sale_of_personal_information', sa.Boolean, nullable=False, default=False),
        sa.Column('sharing_for_advertising', sa.Boolean, nullable=False, default=False),
        sa.Column('opt_out_requests', postgresql.JSONB),
        sa.Column('opt_out_mechanisms', postgresql.JSONB),
        sa.Column('global_privacy_control_honored', sa.Boolean, nullable=False, default=True),
        sa.Column('do_not_sell_requests', postgresql.JSONB),
        sa.Column('do_not_share_requests', postgresql.JSONB),
        sa.Column('limit_use_requests', postgresql.JSONB),
        sa.Column('deletion_requests', postgresql.JSONB),
        sa.Column('correction_requests', postgresql.JSONB),
        sa.Column('know_requests', postgresql.JSONB),
        sa.Column('portability_requests', postgresql.JSONB),
        sa.Column('consumer_request_verification', postgresql.JSONB),
        sa.Column('authorized_agent_requests', postgresql.JSONB),
        sa.Column('response_timeframes_met', sa.Boolean, nullable=False, default=True),
        sa.Column('fee_charging_justification', postgresql.JSONB),
        sa.Column('discrimination_prohibited', sa.Boolean, nullable=False, default=True),
        sa.Column('financial_incentive_programs', postgresql.JSONB),
        sa.Column('privacy_policy_compliance', sa.Boolean, nullable=False, default=True),
        sa.Column('consumer_rights_notices', postgresql.JSONB),
        sa.Column('training_programs', postgresql.JSONB),
        sa.Column('vendor_agreements_updated', sa.Boolean, nullable=False, default=True),
        sa.Column('data_inventory_maintained', sa.Boolean, nullable=False, default=True),
        sa.Column('risk_assessments_conducted', postgresql.JSONB),
        sa.Column('compliance_score', sa.Float, nullable=False, default=100.0),
        sa.Column('last_compliance_review', sa.DateTime),
        sa.Column('next_compliance_review', sa.DateTime),
        sa.Column('privacy_officer', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create threat detection AI table
    op.create_table('threat_detection_ai',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('detection_id', sa.String(100), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('audit_log_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('comprehensive_audit_logs.id', ondelete='CASCADE')),
        sa.Column('threat_type', sa.String(100), nullable=False),
        sa.Column('threat_category', sa.String(50), nullable=False),
        sa.Column('severity', threat_severity_enum, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False, default=0.0),
        sa.Column('risk_score', sa.Float, nullable=False, default=0.0),
        sa.Column('threat_description', sa.Text, nullable=False),
        sa.Column('attack_vector', sa.String(100)),
        sa.Column('attack_pattern', sa.String(100)),
        sa.Column('indicators_of_compromise', postgresql.JSONB),
        sa.Column('behavioral_anomalies', postgresql.JSONB),
        sa.Column('pattern_analysis', postgresql.JSONB),
        sa.Column('machine_learning_models_used', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('detection_algorithms', postgresql.JSONB),
        sa.Column('false_positive_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('mitigation_recommendations', postgresql.JSONB),
        sa.Column('immediate_actions_required', postgresql.JSONB),
        sa.Column('escalation_required', sa.Boolean, nullable=False, default=False),
        sa.Column('escalation_level', sa.String(20)),
        sa.Column('incident_response_triggered', sa.Boolean, nullable=False, default=False),
        sa.Column('containment_measures', postgresql.JSONB),
        sa.Column('forensic_data', postgresql.JSONB),
        sa.Column('related_events', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('timeline_analysis', postgresql.JSONB),
        sa.Column('impact_assessment', postgresql.JSONB),
        sa.Column('business_risk_evaluation', postgresql.JSONB),
        sa.Column('compliance_implications', postgresql.JSONB),
        sa.Column('legal_implications', postgresql.JSONB),
        sa.Column('notification_requirements', postgresql.JSONB),
        sa.Column('remediation_status', sa.String(20), nullable=False, default='open'),
        sa.Column('remediation_actions', postgresql.JSONB),
        sa.Column('resolution_timestamp', sa.DateTime),
        sa.Column('lessons_learned', sa.Text),
        sa.Column('prevention_measures', postgresql.JSONB),
        sa.Column('threat_intelligence_updated', sa.Boolean, nullable=False, default=False),
        sa.Column('analyst_assigned', sa.String(200)),
        sa.Column('analyst_notes', sa.Text),
        sa.Column('automated_response', postgresql.JSONB),
        sa.Column('manual_intervention_required', sa.Boolean, nullable=False, default=False),
        sa.Column('regulatory_reporting_required', sa.Boolean, nullable=False, default=False),
        sa.Column('customer_notification_required', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create security monitoring dashboards table
    op.create_table('security_monitoring_dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('dashboard_name', sa.String(200), nullable=False),
        sa.Column('dashboard_type', sa.String(50), nullable=False),
        sa.Column('monitoring_date', sa.Date, nullable=False),
        sa.Column('total_events_monitored', sa.BigInteger, nullable=False, default=0),
        sa.Column('security_incidents_detected', sa.Integer, nullable=False, default=0),
        sa.Column('threats_identified', sa.Integer, nullable=False, default=0),
        sa.Column('threats_mitigated', sa.Integer, nullable=False, default=0),
        sa.Column('false_positives', sa.Integer, nullable=False, default=0),
        sa.Column('true_positives', sa.Integer, nullable=False, default=0),
        sa.Column('detection_accuracy', sa.Float, nullable=False, default=0.0),
        sa.Column('response_time_average_minutes', sa.Float, nullable=False, default=0.0),
        sa.Column('resolution_time_average_hours', sa.Float, nullable=False, default=0.0),
        sa.Column('compliance_violations', sa.Integer, nullable=False, default=0),
        sa.Column('privacy_incidents', sa.Integer, nullable=False, default=0),
        sa.Column('data_breaches', sa.Integer, nullable=False, default=0),
        sa.Column('unauthorized_access_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('authentication_failures', sa.Integer, nullable=False, default=0),
        sa.Column('privilege_escalation_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('malware_detections', sa.Integer, nullable=False, default=0),
        sa.Column('phishing_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('ddos_attacks', sa.Integer, nullable=False, default=0),
        sa.Column('sql_injection_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('xss_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('csrf_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('brute_force_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('account_takeover_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('insider_threat_indicators', sa.Integer, nullable=False, default=0),
        sa.Column('anomalous_user_behavior', sa.Integer, nullable=False, default=0),
        sa.Column('suspicious_api_usage', sa.Integer, nullable=False, default=0),
        sa.Column('geographic_risk_events', sa.Integer, nullable=False, default=0),
        sa.Column('device_risk_events', sa.Integer, nullable=False, default=0),
        sa.Column('network_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('endpoint_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('cloud_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('application_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('database_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('infrastructure_security_events', sa.Integer, nullable=False, default=0),
        sa.Column('security_training_completion_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('vulnerability_scan_results', postgresql.JSONB),
        sa.Column('penetration_test_results', postgresql.JSONB),
        sa.Column('compliance_audit_results', postgresql.JSONB),
        sa.Column('risk_assessment_scores', postgresql.JSONB),
        sa.Column('security_posture_score', sa.Float, nullable=False, default=0.0),
        sa.Column('threat_landscape_analysis', postgresql.JSONB),
        sa.Column('security_trends', postgresql.JSONB),
        sa.Column('predictive_analytics', postgresql.JSONB),
        sa.Column('recommendations', postgresql.JSONB),
        sa.Column('action_items', postgresql.JSONB),
        sa.Column('executive_summary', sa.Text),
        sa.Column('detailed_report_url', sa.String(500)),
        sa.Column('generated_by', sa.String(200)),
        sa.Column('reviewed_by', sa.String(200)),
        sa.Column('approved_by', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create data retention policies table
    op.create_table('data_retention_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('policy_name', sa.String(200), nullable=False),
        sa.Column('data_category', sa.String(100), nullable=False),
        sa.Column('data_classification', security_level_enum, nullable=False),
        sa.Column('compliance_frameworks', postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('retention_period_days', sa.Integer, nullable=False),
        sa.Column('legal_basis', sa.String(100), nullable=False),
        sa.Column('retention_triggers', postgresql.JSONB),
        sa.Column('deletion_triggers', postgresql.JSONB),
        sa.Column('archival_rules', postgresql.JSONB),
        sa.Column('anonymization_rules', postgresql.JSONB),
        sa.Column('pseudonymization_rules', postgresql.JSONB),
        sa.Column('encryption_requirements', postgresql.JSONB),
        sa.Column('access_restrictions', postgresql.JSONB),
        sa.Column('geographical_restrictions', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('legal_hold_procedures', postgresql.JSONB),
        sa.Column('litigation_hold_procedures', postgresql.JSONB),
        sa.Column('backup_retention_rules', postgresql.JSONB),
        sa.Column('disaster_recovery_implications', postgresql.JSONB),
        sa.Column('cross_border_transfer_rules', postgresql.JSONB),
        sa.Column('third_party_sharing_rules', postgresql.JSONB),
        sa.Column('vendor_data_handling_requirements', postgresql.JSONB),
        sa.Column('audit_requirements', postgresql.JSONB),
        sa.Column('reporting_requirements', postgresql.JSONB),
        sa.Column('exception_procedures', postgresql.JSONB),
        sa.Column('policy_review_frequency_days', sa.Integer, nullable=False, default=365),
        sa.Column('last_policy_review', sa.DateTime),
        sa.Column('next_policy_review', sa.DateTime),
        sa.Column('policy_version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('policy_approved_by', sa.String(200)),
        sa.Column('policy_approval_date', sa.DateTime),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('expiration_date', sa.DateTime),
        sa.Column('policy_status', sa.String(20), nullable=False, default='active'),
        sa.Column('automation_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('monitoring_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('violation_alerts_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('compliance_score', sa.Float, nullable=False, default=100.0),
        sa.Column('policy_violations', sa.Integer, nullable=False, default=0),
        sa.Column('enforcement_actions', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Comprehensive Audit Logs indexes
    op.create_index('idx_audit_logs_event_id', 'comprehensive_audit_logs', ['event_id'])
    op.create_index('idx_audit_logs_user_id', 'comprehensive_audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_session_id', 'comprehensive_audit_logs', ['session_id'])
    op.create_index('idx_audit_logs_event_type', 'comprehensive_audit_logs', ['event_type'])
    op.create_index('idx_audit_logs_category', 'comprehensive_audit_logs', ['event_category'])
    op.create_index('idx_audit_logs_resource_type', 'comprehensive_audit_logs', ['resource_type'])
    op.create_index('idx_audit_logs_resource_id', 'comprehensive_audit_logs', ['resource_id'])
    op.create_index('idx_audit_logs_action', 'comprehensive_audit_logs', ['action_performed'])
    op.create_index('idx_audit_logs_result', 'comprehensive_audit_logs', ['action_result'])
    op.create_index('idx_audit_logs_ip_address', 'comprehensive_audit_logs', ['ip_address'])
    op.create_index('idx_audit_logs_created_at', 'comprehensive_audit_logs', ['created_at'])
    op.create_index('idx_audit_logs_sensitive_data', 'comprehensive_audit_logs', ['sensitive_data_accessed'])
    op.create_index('idx_audit_logs_classification', 'comprehensive_audit_logs', ['data_classification'])
    op.create_index('idx_audit_logs_compliance', 'comprehensive_audit_logs', ['compliance_relevant'])
    op.create_index('idx_audit_logs_frameworks', 'comprehensive_audit_logs', ['compliance_frameworks'], postgresql_using='gin')
    op.create_index('idx_audit_logs_risk_score', 'comprehensive_audit_logs', ['risk_score'])
    op.create_index('idx_audit_logs_anomaly_score', 'comprehensive_audit_logs', ['anomaly_score'])
    op.create_index('idx_audit_logs_correlation_id', 'comprehensive_audit_logs', ['correlation_id'])
    op.create_index('idx_audit_logs_archived', 'comprehensive_audit_logs', ['archived'])
    op.create_index('idx_audit_logs_legal_hold', 'comprehensive_audit_logs', ['legal_hold'])
    op.create_index('idx_audit_logs_purge_eligible', 'comprehensive_audit_logs', ['purge_eligible_date'])
    
    # GDPR Compliance Tracking indexes
    op.create_index('idx_gdpr_compliance_user_id', 'gdpr_compliance_tracking', ['user_id'])
    op.create_index('idx_gdpr_compliance_subject_id', 'gdpr_compliance_tracking', ['data_subject_id'])
    op.create_index('idx_gdpr_compliance_legal_basis', 'gdpr_compliance_tracking', ['legal_basis'])
    op.create_index('idx_gdpr_compliance_consent', 'gdpr_compliance_tracking', ['consent_given'])
    op.create_index('idx_gdpr_compliance_consent_timestamp', 'gdpr_compliance_tracking', ['consent_timestamp'])
    op.create_index('idx_gdpr_compliance_withdrawal', 'gdpr_compliance_tracking', ['consent_withdrawal_date'])
    op.create_index('idx_gdpr_compliance_automated_decision', 'gdpr_compliance_tracking', ['automated_decision_making'])
    op.create_index('idx_gdpr_compliance_score', 'gdpr_compliance_tracking', ['compliance_score'])
    op.create_index('idx_gdpr_compliance_review', 'gdpr_compliance_tracking', ['next_compliance_review'])
    op.create_index('idx_gdpr_compliance_dpo', 'gdpr_compliance_tracking', ['dpo_involved'])
    
    # CCPA Compliance Tracking indexes
    op.create_index('idx_ccpa_compliance_user_id', 'ccpa_compliance_tracking', ['user_id'])
    op.create_index('idx_ccpa_compliance_consumer_id', 'ccpa_compliance_tracking', ['consumer_id'])
    op.create_index('idx_ccpa_compliance_ca_resident', 'ccpa_compliance_tracking', ['california_resident'])
    op.create_index('idx_ccpa_compliance_behavioral_ad', 'ccpa_compliance_tracking', ['cross_context_behavioral_advertising'])
    op.create_index('idx_ccpa_compliance_sale', 'ccpa_compliance_tracking', ['sale_of_personal_information'])
    op.create_index('idx_ccpa_compliance_sharing', 'ccpa_compliance_tracking', ['sharing_for_advertising'])
    op.create_index('idx_ccpa_compliance_gpc', 'ccpa_compliance_tracking', ['global_privacy_control_honored'])
    op.create_index('idx_ccpa_compliance_response_time', 'ccpa_compliance_tracking', ['response_timeframes_met'])
    op.create_index('idx_ccpa_compliance_discrimination', 'ccpa_compliance_tracking', ['discrimination_prohibited'])
    op.create_index('idx_ccpa_compliance_score', 'ccpa_compliance_tracking', ['compliance_score'])
    op.create_index('idx_ccpa_compliance_review', 'ccpa_compliance_tracking', ['next_compliance_review'])
    
    # Threat Detection AI indexes
    op.create_index('idx_threat_detection_id', 'threat_detection_ai', ['detection_id'])
    op.create_index('idx_threat_detection_user_id', 'threat_detection_ai', ['user_id'])
    op.create_index('idx_threat_detection_audit_log', 'threat_detection_ai', ['audit_log_id'])
    op.create_index('idx_threat_detection_type', 'threat_detection_ai', ['threat_type'])
    op.create_index('idx_threat_detection_category', 'threat_detection_ai', ['threat_category'])
    op.create_index('idx_threat_detection_severity', 'threat_detection_ai', ['severity'])
    op.create_index('idx_threat_detection_confidence', 'threat_detection_ai', ['confidence_score'])
    op.create_index('idx_threat_detection_risk', 'threat_detection_ai', ['risk_score'])
    op.create_index('idx_threat_detection_escalation', 'threat_detection_ai', ['escalation_required'])
    op.create_index('idx_threat_detection_incident', 'threat_detection_ai', ['incident_response_triggered'])
    op.create_index('idx_threat_detection_status', 'threat_detection_ai', ['remediation_status'])
    op.create_index('idx_threat_detection_analyst', 'threat_detection_ai', ['analyst_assigned'])
    op.create_index('idx_threat_detection_manual', 'threat_detection_ai', ['manual_intervention_required'])
    op.create_index('idx_threat_detection_regulatory', 'threat_detection_ai', ['regulatory_reporting_required'])
    op.create_index('idx_threat_detection_customer', 'threat_detection_ai', ['customer_notification_required'])
    op.create_index('idx_threat_detection_created', 'threat_detection_ai', ['created_at'])
    
    # Security Monitoring Dashboards indexes
    op.create_index('idx_security_monitoring_name', 'security_monitoring_dashboards', ['dashboard_name'])
    op.create_index('idx_security_monitoring_type', 'security_monitoring_dashboards', ['dashboard_type'])
    op.create_index('idx_security_monitoring_date', 'security_monitoring_dashboards', ['monitoring_date'])
    op.create_index('idx_security_monitoring_incidents', 'security_monitoring_dashboards', ['security_incidents_detected'])
    op.create_index('idx_security_monitoring_threats', 'security_monitoring_dashboards', ['threats_identified'])
    op.create_index('idx_security_monitoring_accuracy', 'security_monitoring_dashboards', ['detection_accuracy'])
    op.create_index('idx_security_monitoring_response_time', 'security_monitoring_dashboards', ['response_time_average_minutes'])
    op.create_index('idx_security_monitoring_posture', 'security_monitoring_dashboards', ['security_posture_score'])
    op.create_index('idx_security_monitoring_violations', 'security_monitoring_dashboards', ['compliance_violations'])
    op.create_index('idx_security_monitoring_breaches', 'security_monitoring_dashboards', ['data_breaches'])
    
    # Data Retention Policies indexes
    op.create_index('idx_retention_policies_name', 'data_retention_policies', ['policy_name'])
    op.create_index('idx_retention_policies_category', 'data_retention_policies', ['data_category'])
    op.create_index('idx_retention_policies_classification', 'data_retention_policies', ['data_classification'])
    op.create_index('idx_retention_policies_frameworks', 'data_retention_policies', ['compliance_frameworks'], postgresql_using='gin')
    op.create_index('idx_retention_policies_retention_period', 'data_retention_policies', ['retention_period_days'])
    op.create_index('idx_retention_policies_legal_basis', 'data_retention_policies', ['legal_basis'])
    op.create_index('idx_retention_policies_effective', 'data_retention_policies', ['effective_date'])
    op.create_index('idx_retention_policies_expiration', 'data_retention_policies', ['expiration_date'])
    op.create_index('idx_retention_policies_status', 'data_retention_policies', ['policy_status'])
    op.create_index('idx_retention_policies_review', 'data_retention_policies', ['next_policy_review'])
    op.create_index('idx_retention_policies_automation', 'data_retention_policies', ['automation_enabled'])
    op.create_index('idx_retention_policies_monitoring', 'data_retention_policies', ['monitoring_enabled'])
    op.create_index('idx_retention_policies_score', 'data_retention_policies', ['compliance_score'])
    op.create_index('idx_retention_policies_violations', 'data_retention_policies', ['policy_violations'])


def downgrade() -> None:
    """Downgrade database schema - Remove security audit system tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('data_retention_policies')
    op.drop_table('security_monitoring_dashboards')
    op.drop_table('threat_detection_ai')
    op.drop_table('ccpa_compliance_tracking')
    op.drop_table('gdpr_compliance_tracking')
    op.drop_table('comprehensive_audit_logs')
    
    # Drop ENUM types
    sa.Enum(name='threat_severity').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='security_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='compliance_framework').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='audit_event_type').drop(op.get_bind(), checkfirst=True)