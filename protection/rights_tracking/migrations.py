"""
Migrations Alembic pour le module de suivi des droits d'auteur.

Ce fichier contient les migrations de base de données pour créer
et maintenir le schéma de la base de données du système de suivi
des droits d'auteur de niveau industriel.

Auteur: Équipe de développement IA-Influencer-Agent
Date: 2024
Copyright: Tous droits réservés

AVERTISSEMENT: Ce code est protégé par des droits d'auteur et des brevets.
Toute tentative de copie, reproduction, ou utilisation non autorisée
fera l'objet de poursuites judiciaires au maximum prévu par la loi.
L'usage de ce code sans licence appropriée constitue une violation
des droits de propriété intellectuelle.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime


def upgrade():
    """Migration vers la nouvelle version - création du schéma complet"""
    
    # === Table ContentMetadata ===
    op.create_table(
        'content_metadata',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('content_type', sa.String(50), nullable=False, index=True),
        sa.Column('format', sa.String(20)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('file_size_bytes', sa.BigInteger),
        sa.Column('file_hash', sa.String(128), index=True),
        sa.Column('quality_metrics', postgresql.JSONB),
        sa.Column('technical_specifications', postgresql.JSONB),
        sa.Column('creation_date', sa.DateTime, nullable=False),
        sa.Column('upload_date', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('last_modified', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('tags', postgresql.ARRAY(sa.String(100))),
        sa.Column('language', sa.String(10)),
        sa.Column('genre', sa.String(100)),
        sa.Column('explicit_content', sa.Boolean, default=False),
        sa.Column('ai_generated', sa.Boolean, default=False),
        sa.Column('fingerprint_data', postgresql.JSONB),
        sa.Column('watermark_data', postgresql.JSONB),
        sa.Column('blockchain_hash', sa.String(128)),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('storage_location', sa.String(500)),
        sa.Column('backup_locations', postgresql.ARRAY(sa.String(500))),
        sa.Column('access_count', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('metadata_version', sa.String(10), default='1.0')
    )
    
    # Index composites pour ContentMetadata
    op.create_index('ix_content_type_active', 'content_metadata', ['content_type', 'is_active'])
    op.create_index('ix_creation_date_type', 'content_metadata', ['creation_date', 'content_type'])
    op.create_index('ix_file_hash_unique', 'content_metadata', ['file_hash'], unique=True)
    
    # === Table RightsHolder ===
    op.create_table(
        'rights_holders',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('entity_type', sa.String(20), nullable=False),  # individual, company, organization
        sa.Column('legal_name', sa.String(200), nullable=False, index=True),
        sa.Column('display_name', sa.String(200)),
        sa.Column('tax_id', sa.String(50)),
        sa.Column('business_registration', sa.String(100)),
        sa.Column('contact_information', postgresql.JSONB, nullable=False),
        sa.Column('address', postgresql.JSONB),
        sa.Column('bank_details', postgresql.JSONB),  # Chiffré
        sa.Column('payment_preferences', postgresql.JSONB),
        sa.Column('verification_documents', postgresql.JSONB),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('verification_date', sa.DateTime),
        sa.Column('risk_score', sa.Float, default=0.0),
        sa.Column('trust_level', sa.String(20), default='new'),
        sa.Column('preferred_currency', sa.String(10), default='USD'),
        sa.Column('territory_restrictions', postgresql.ARRAY(sa.String(10))),
        sa.Column('active_since', sa.DateTime, default=datetime.utcnow),
        sa.Column('last_activity', sa.DateTime),
        sa.Column('total_revenue_generated', sa.Numeric(15, 2), default=0),
        sa.Column('total_content_registered', sa.Integer, default=0),
        sa.Column('compliance_score', sa.Float, default=100.0),
        sa.Column('notes', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Index pour RightsHolder
    op.create_index('ix_legal_name_active', 'rights_holders', ['legal_name', 'is_active'])
    op.create_index('ix_verification_status', 'rights_holders', ['verification_status'])
    op.create_index('ix_entity_type', 'rights_holders', ['entity_type'])
    
    # === Table RightsRecord ===
    op.create_table(
        'rights_records',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('content_id', sa.String(50), sa.ForeignKey('content_metadata.id'), nullable=False, index=True),
        sa.Column('rights_holder_id', sa.String(50), sa.ForeignKey('rights_holders.id'), nullable=False, index=True),
        sa.Column('rights_type', sa.String(50), nullable=False),  # copyright, master, sync, etc.
        sa.Column('ownership_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('acquisition_method', sa.String(50)),  # creation, purchase, inheritance, etc.
        sa.Column('acquisition_date', sa.DateTime, nullable=False),
        sa.Column('acquisition_documents', postgresql.JSONB),
        sa.Column('valid_from', sa.DateTime, nullable=False),
        sa.Column('valid_until', sa.DateTime),
        sa.Column('territories', postgresql.ARRAY(sa.String(10)), nullable=False),
        sa.Column('usage_restrictions', postgresql.JSONB),
        sa.Column('exclusivity_level', sa.String(20), default='non_exclusive'),
        sa.Column('transferable', sa.Boolean, default=True),
        sa.Column('sublicensable', sa.Boolean, default=False),
        sa.Column('moral_rights_retained', sa.Boolean, default=True),
        sa.Column('registration_number', sa.String(100)),
        sa.Column('registration_authority', sa.String(100)),
        sa.Column('priority_date', sa.DateTime),
        sa.Column('renewal_required', sa.Boolean, default=False),
        sa.Column('renewal_date', sa.DateTime),
        sa.Column('enforcement_level', sa.String(20), default='standard'),
        sa.Column('blockchain_record', sa.String(128)),
        sa.Column('smart_contract_address', sa.String(100)),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('verification_date', sa.DateTime),
        sa.Column('dispute_count', sa.Integer, default=0),
        sa.Column('last_dispute_date', sa.DateTime),
        sa.Column('enforcement_actions_count', sa.Integer, default=0),
        sa.Column('revenue_generated', sa.Numeric(15, 2), default=0),
        sa.Column('notes', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Index pour RightsRecord
    op.create_index('ix_content_rights_active', 'rights_records', ['content_id', 'is_active'])
    op.create_index('ix_holder_rights_active', 'rights_records', ['rights_holder_id', 'is_active'])
    op.create_index('ix_rights_type', 'rights_records', ['rights_type'])
    op.create_index('ix_valid_dates', 'rights_records', ['valid_from', 'valid_until'])
    
    # === Table LicenseAgreement ===
    op.create_table(
        'license_agreements',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('rights_record_id', sa.String(50), sa.ForeignKey('rights_records.id'), nullable=False, index=True),
        sa.Column('licensor_id', sa.String(50), sa.ForeignKey('rights_holders.id'), nullable=False, index=True),
        sa.Column('licensee_id', sa.String(50), sa.ForeignKey('rights_holders.id'), nullable=False, index=True),
        sa.Column('license_type', sa.String(50), nullable=False),
        sa.Column('template_used', sa.String(50)),
        sa.Column('exclusivity_level', sa.String(20), default='non_exclusive'),
        sa.Column('grant_date', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('expiration_date', sa.DateTime),
        sa.Column('auto_renewal', sa.Boolean, default=False),
        sa.Column('renewal_period_months', sa.Integer),
        sa.Column('territories', postgresql.ARRAY(sa.String(10)), nullable=False),
        sa.Column('usage_rights', postgresql.JSONB, nullable=False),
        sa.Column('usage_restrictions', postgresql.JSONB),
        sa.Column('payment_terms', postgresql.JSONB, nullable=False),
        sa.Column('royalty_structure', postgresql.JSONB),
        sa.Column('minimum_guarantees', postgresql.JSONB),
        sa.Column('advance_payments', postgresql.JSONB),
        sa.Column('reporting_requirements', postgresql.JSONB),
        sa.Column('audit_rights', postgresql.JSONB),
        sa.Column('termination_conditions', postgresql.JSONB),
        sa.Column('force_majeure_clause', sa.Text),
        sa.Column('governing_law', sa.String(50)),
        sa.Column('dispute_resolution', sa.String(50)),
        sa.Column('jurisdiction', sa.String(50)),
        sa.Column('signature_date', sa.DateTime),
        sa.Column('execution_method', sa.String(50)),  # electronic, physical, etc.
        sa.Column('digital_signatures', postgresql.JSONB),
        sa.Column('witness_information', postgresql.JSONB),
        sa.Column('notarization_required', sa.Boolean, default=False),
        sa.Column('contract_language', sa.String(10), default='en'),
        sa.Column('contract_version', sa.String(10), default='1.0'),
        sa.Column('amendment_count', sa.Integer, default=0),
        sa.Column('last_amendment_date', sa.DateTime),
        sa.Column('performance_metrics', postgresql.JSONB),
        sa.Column('compliance_status', sa.String(20), default='compliant'),
        sa.Column('breach_count', sa.Integer, default=0),
        sa.Column('last_breach_date', sa.DateTime),
        sa.Column('total_revenue_generated', sa.Numeric(15, 2), default=0),
        sa.Column('total_payments_made', sa.Numeric(15, 2), default=0),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('cancellation_date', sa.DateTime),
        sa.Column('cancellation_reason', sa.String(200)),
        sa.Column('archive_date', sa.DateTime),
        sa.Column('document_storage_path', sa.String(500)),
        sa.Column('backup_storage_paths', postgresql.ARRAY(sa.String(500))),
        sa.Column('encryption_key_id', sa.String(100)),
        sa.Column('access_log', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Index pour LicenseAgreement
    op.create_index('ix_license_parties', 'license_agreements', ['licensor_id', 'licensee_id'])
    op.create_index('ix_license_dates', 'license_agreements', ['effective_date', 'expiration_date'])
    op.create_index('ix_license_status', 'license_agreements', ['status', 'is_active'])
    op.create_index('ix_license_type', 'license_agreements', ['license_type'])
    
    # === Table UsageEvent ===
    op.create_table(
        'usage_events',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('content_id', sa.String(50), sa.ForeignKey('content_metadata.id'), nullable=False, index=True),
        sa.Column('license_id', sa.String(50), sa.ForeignKey('license_agreements.id'), index=True),
        sa.Column('platform', sa.String(50), nullable=False, index=True),
        sa.Column('platform_content_id', sa.String(200)),
        sa.Column('platform_url', sa.String(1000)),
        sa.Column('detected_at', sa.DateTime, nullable=False, default=datetime.utcnow, index=True),
        sa.Column('usage_type', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(200)),
        sa.Column('user_info', postgresql.JSONB),
        sa.Column('location_detected', sa.String(100)),
        sa.Column('ip_address', sa.String(45)),  # Support IPv6
        sa.Column('user_agent', sa.String(500)),
        sa.Column('similarity_score', sa.Float),
        sa.Column('confidence_level', sa.Float),
        sa.Column('detection_method', sa.String(50)),
        sa.Column('ai_model_used', sa.String(100)),
        sa.Column('fingerprint_matches', postgresql.JSONB),
        sa.Column('modification_detected', postgresql.JSONB),
        sa.Column('quality_assessment', postgresql.JSONB),
        sa.Column('duration_used', sa.Integer),  # en secondes
        sa.Column('portion_used_percentage', sa.Float),
        sa.Column('commercial_use_detected', sa.Boolean, default=False),
        sa.Column('monetization_detected', postgresql.JSONB),
        sa.Column('engagement_metrics', postgresql.JSONB),
        sa.Column('view_count', sa.BigInteger, default=0),
        sa.Column('like_count', sa.BigInteger, default=0),
        sa.Column('comment_count', sa.BigInteger, default=0),
        sa.Column('share_count', sa.BigInteger, default=0),
        sa.Column('estimated_revenue', sa.Numeric(12, 2)),
        sa.Column('violation_type', sa.String(50)),
        sa.Column('violation_severity', sa.String(20)),
        sa.Column('authorized_use', sa.Boolean),
        sa.Column('license_compliance_status', sa.String(50)),
        sa.Column('action_required', sa.Boolean, default=False),
        sa.Column('action_taken', postgresql.JSONB),
        sa.Column('action_date', sa.DateTime),
        sa.Column('resolution_status', sa.String(50), default='pending'),
        sa.Column('resolution_date', sa.DateTime),
        sa.Column('escalation_level', sa.Integer, default=0),
        sa.Column('assigned_to', sa.String(100)),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('tags', postgresql.ARRAY(sa.String(100))),
        sa.Column('evidence_collected', postgresql.JSONB),
        sa.Column('legal_notice_sent', sa.Boolean, default=False),
        sa.Column('takedown_request_sent', sa.Boolean, default=False),
        sa.Column('platform_response', postgresql.JSONB),
        sa.Column('recovery_amount', sa.Numeric(12, 2)),
        sa.Column('notes', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Index pour UsageEvent
    op.create_index('ix_usage_platform_date', 'usage_events', ['platform', 'detected_at'])
    op.create_index('ix_usage_content_date', 'usage_events', ['content_id', 'detected_at'])
    op.create_index('ix_usage_violation', 'usage_events', ['violation_type', 'violation_severity'])
    op.create_index('ix_usage_resolution', 'usage_events', ['resolution_status', 'action_required'])
    op.create_index('ix_usage_commercial', 'usage_events', ['commercial_use_detected'])
    
    # === Table PaymentRecord ===
    op.create_table(
        'payment_records',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('license_id', sa.String(50), sa.ForeignKey('license_agreements.id'), nullable=False, index=True),
        sa.Column('payer_id', sa.String(50), sa.ForeignKey('rights_holders.id'), nullable=False, index=True),
        sa.Column('payee_id', sa.String(50), sa.ForeignKey('rights_holders.id'), nullable=False, index=True),
        sa.Column('payment_type', sa.String(50), nullable=False),  # royalty, advance, minimum_guarantee, etc.
        sa.Column('reporting_period_start', sa.DateTime),
        sa.Column('reporting_period_end', sa.DateTime),
        sa.Column('calculation_basis', postgresql.JSONB),
        sa.Column('usage_data', postgresql.JSONB),
        sa.Column('gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('deductions', postgresql.JSONB),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('exchange_rate', sa.Numeric(10, 6)),
        sa.Column('amount_usd', sa.Numeric(15, 2)),
        sa.Column('tax_information', postgresql.JSONB),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('payment_reference', sa.String(200)),
        sa.Column('transaction_id', sa.String(200)),
        sa.Column('blockchain_transaction', sa.String(128)),
        sa.Column('due_date', sa.DateTime, nullable=False),
        sa.Column('payment_date', sa.DateTime),
        sa.Column('received_date', sa.DateTime),
        sa.Column('payment_status', sa.String(50), default='pending'),
        sa.Column('processing_fee', sa.Numeric(10, 2), default=0),
        sa.Column('late_fee', sa.Numeric(10, 2), default=0),
        sa.Column('dispute_raised', sa.Boolean, default=False),
        sa.Column('dispute_details', postgresql.JSONB),
        sa.Column('audit_status', sa.String(50), default='not_audited'),
        sa.Column('audit_date', sa.DateTime),
        sa.Column('auditor_notes', sa.Text),
        sa.Column('compliance_checked', sa.Boolean, default=False),
        sa.Column('compliance_issues', postgresql.JSONB),
        sa.Column('supporting_documents', postgresql.JSONB),
        sa.Column('automatic_calculation', sa.Boolean, default=True),
        sa.Column('manual_adjustments', postgresql.JSONB),
        sa.Column('approval_required', sa.Boolean, default=False),
        sa.Column('approved_by', sa.String(100)),
        sa.Column('approval_date', sa.DateTime),
        sa.Column('notification_sent', sa.Boolean, default=False),
        sa.Column('reminder_count', sa.Integer, default=0),
        sa.Column('last_reminder_date', sa.DateTime),
        sa.Column('escalation_date', sa.DateTime),
        sa.Column('notes', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Index pour PaymentRecord
    op.create_index('ix_payment_license_period', 'payment_records', ['license_id', 'reporting_period_start'])
    op.create_index('ix_payment_status_due', 'payment_records', ['payment_status', 'due_date'])
    op.create_index('ix_payment_parties', 'payment_records', ['payer_id', 'payee_id'])
    op.create_index('ix_payment_type', 'payment_records', ['payment_type'])
    
    # === Table AuditLog ===
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),  # table name
        sa.Column('entity_id', sa.String(50), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),  # create, update, delete
        sa.Column('user_id', sa.String(100)),
        sa.Column('user_role', sa.String(50)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('session_id', sa.String(100)),
        sa.Column('timestamp', sa.DateTime, nullable=False, default=datetime.utcnow, index=True),
        sa.Column('changes', postgresql.JSONB),  # before/after values
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('error_message', sa.Text),
        sa.Column('processing_time_ms', sa.Integer),
        sa.Column('api_endpoint', sa.String(200)),
        sa.Column('request_method', sa.String(10)),
        sa.Column('request_size_bytes', sa.Integer),
        sa.Column('response_size_bytes', sa.Integer),
        sa.Column('compliance_relevant', sa.Boolean, default=False),
        sa.Column('retention_date', sa.DateTime),  # When this log should be deleted
        sa.Column('archived', sa.Boolean, default=False)
    )
    
    # Index pour AuditLog
    op.create_index('ix_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_compliance', 'audit_logs', ['compliance_relevant', 'timestamp'])
    
    # === Contraintes de clés étrangères supplémentaires ===
    
    # Contrainte pour éviter l'auto-référence dans license_agreements
    op.create_check_constraint(
        'check_licensor_licensee_different',
        'license_agreements',
        'licensor_id != licensee_id'
    )
    
    # Contrainte pour les pourcentages de propriété
    op.create_check_constraint(
        'check_ownership_percentage',
        'rights_records',
        'ownership_percentage >= 0 AND ownership_percentage <= 100'
    )
    
    # Contrainte pour les scores de similarité
    op.create_check_constraint(
        'check_similarity_score',
        'usage_events',
        'similarity_score IS NULL OR (similarity_score >= 0 AND similarity_score <= 1)'
    )
    
    # Contrainte pour les montants positifs
    op.create_check_constraint(
        'check_positive_amounts',
        'payment_records',
        'gross_amount >= 0 AND net_amount >= 0'
    )
    
    # === Vues pour les requêtes communes ===
    
    # Vue pour les droits actifs avec détails des détenteurs
    op.execute("""
        CREATE VIEW active_rights_view AS
        SELECT 
            rr.id as rights_record_id,
            rr.content_id,
            rr.rights_type,
            rr.ownership_percentage,
            rr.territories,
            rh.legal_name as rights_holder_name,
            rh.entity_type,
            cm.title as content_title,
            cm.content_type,
            rr.valid_from,
            rr.valid_until,
            rr.verification_status
        FROM rights_records rr
        JOIN rights_holders rh ON rr.rights_holder_id = rh.id
        JOIN content_metadata cm ON rr.content_id = cm.id
        WHERE rr.is_active = true 
        AND rh.is_active = true 
        AND cm.is_active = true
        AND (rr.valid_until IS NULL OR rr.valid_until > NOW())
    """)
    
    # Vue pour les licences actives avec performance
    op.execute("""
        CREATE VIEW active_licenses_view AS
        SELECT 
            la.id as license_id,
            la.rights_record_id,
            la.license_type,
            la.effective_date,
            la.expiration_date,
            la.territories,
            licensor.legal_name as licensor_name,
            licensee.legal_name as licensee_name,
            la.total_revenue_generated,
            la.compliance_status,
            la.status,
            cm.title as content_title
        FROM license_agreements la
        JOIN rights_holders licensor ON la.licensor_id = licensor.id
        JOIN rights_holders licensee ON la.licensee_id = licensee.id
        JOIN rights_records rr ON la.rights_record_id = rr.id
        JOIN content_metadata cm ON rr.content_id = cm.id
        WHERE la.is_active = true 
        AND la.status = 'active'
        AND (la.expiration_date IS NULL OR la.expiration_date > NOW())
    """)
    
    # Vue pour les violations non résolues
    op.execute("""
        CREATE VIEW unresolved_violations_view AS
        SELECT 
            ue.id as usage_event_id,
            ue.content_id,
            ue.platform,
            ue.detected_at,
            ue.violation_type,
            ue.violation_severity,
            ue.similarity_score,
            ue.commercial_use_detected,
            ue.estimated_revenue,
            ue.resolution_status,
            ue.priority,
            cm.title as content_title,
            cm.content_type
        FROM usage_events ue
        JOIN content_metadata cm ON ue.content_id = cm.id
        WHERE ue.is_active = true 
        AND ue.resolution_status IN ('pending', 'in_progress')
        AND ue.violation_type IS NOT NULL
        ORDER BY ue.violation_severity DESC, ue.detected_at DESC
    """)
    
    # === Triggers pour l'audit automatique ===
    
    # Fonction pour l'audit automatique
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trigger_function()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                INSERT INTO audit_logs (
                    id, entity_type, entity_id, action, timestamp, changes
                ) VALUES (
                    'AUD-' || extract(epoch from now())::text || '-' || substr(md5(random()::text), 1, 8),
                    TG_TABLE_NAME,
                    OLD.id,
                    'delete',
                    NOW(),
                    row_to_json(OLD)
                );
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                INSERT INTO audit_logs (
                    id, entity_type, entity_id, action, timestamp, changes
                ) VALUES (
                    'AUD-' || extract(epoch from now())::text || '-' || substr(md5(random()::text), 1, 8),
                    TG_TABLE_NAME,
                    NEW.id,
                    'update',
                    NOW(),
                    json_build_object('before', row_to_json(OLD), 'after', row_to_json(NEW))
                );
                RETURN NEW;
            ELSIF TG_OP = 'INSERT' THEN
                INSERT INTO audit_logs (
                    id, entity_type, entity_id, action, timestamp, changes
                ) VALUES (
                    'AUD-' || extract(epoch from now())::text || '-' || substr(md5(random()::text), 1, 8),
                    TG_TABLE_NAME,
                    NEW.id,
                    'create',
                    NOW(),
                    row_to_json(NEW)
                );
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Triggers d'audit pour les tables principales
    for table in ['content_metadata', 'rights_records', 'license_agreements', 'payment_records']:
        op.execute(f"""
            CREATE TRIGGER {table}_audit_trigger
            AFTER INSERT OR UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
        """)
    
    print("✅ Migration de création du schéma terminée avec succès")
    print("📊 Tables créées: 7 tables principales + 1 table d'audit")
    print("🔍 Index créés: 25+ index pour optimiser les performances")
    print("👁️ Vues créées: 3 vues métier pour les requêtes communes")
    print("🔔 Triggers d'audit: Audit automatique activé sur les tables principales")


def downgrade():
    """Migration vers la version précédente - suppression du schéma"""
    
    # Suppression des triggers
    for table in ['content_metadata', 'rights_records', 'license_agreements', 'payment_records']:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_audit_trigger ON {table};")
    
    # Suppression de la fonction d'audit
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_function();")
    
    # Suppression des vues
    op.execute("DROP VIEW IF EXISTS unresolved_violations_view;")
    op.execute("DROP VIEW IF EXISTS active_licenses_view;")
    op.execute("DROP VIEW IF EXISTS active_rights_view;")
    
    # Suppression des tables dans l'ordre inverse des dépendances
    op.drop_table('audit_logs')
    op.drop_table('payment_records')
    op.drop_table('usage_events')
    op.drop_table('license_agreements')
    op.drop_table('rights_records')
    op.drop_table('rights_holders')
    op.drop_table('content_metadata')
    
    print("⚠️ Migration de suppression terminée")
    print("🗑️ Toutes les tables, vues, triggers et fonctions ont été supprimés")
