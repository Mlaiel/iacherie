"""Advanced payment processing system with multi-gateway support

Revision ID: j6i7h8g9f0e1
Revises: i5h6g7f8e9d0
Create Date: 2025-09-05 06:45:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced payment processing system with multiple
payment gateways, cryptocurrency support, international payments, and
automatic tax management.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'j6i7h8g9f0e1'
down_revision = 'i5h6g7f8e9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Advanced payment processing system."""
    
    # Create payment gateway enum
    payment_gateway_enum = sa.Enum(
        'stripe', 'paypal', 'square', 'adyen', 'braintree', 'razorpay',
        'klarna', 'apple_pay', 'google_pay', 'amazon_pay', 'alipay', 'wechat_pay',
        'binance_pay', 'coinbase', 'crypto_com', 'metamask', 'trust_wallet',
        'wire_transfer', 'sepa', 'ach', 'swift', 'local_bank', 'mobile_money',
        name='payment_gateway'
    )
    
    # Create payment method enum
    payment_method_enum = sa.Enum(
        'credit_card', 'debit_card', 'bank_transfer', 'digital_wallet',
        'cryptocurrency', 'buy_now_pay_later', 'prepaid_card', 'gift_card',
        'mobile_payment', 'cash_app', 'venmo', 'zelle', 'interac', 'ideal',
        'sofort', 'giropay', 'eps', 'p24', 'bancontact', 'blik',
        name='payment_method'
    )
    
    # Create payment status enum
    payment_status_enum = sa.Enum(
        'pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded',
        'partially_refunded', 'disputed', 'chargeback', 'expired', 'on_hold',
        name='payment_status'
    )
    
    # Create cryptocurrency enum
    cryptocurrency_enum = sa.Enum(
        'bitcoin', 'ethereum', 'usdc', 'usdt', 'bnb', 'ada', 'dot', 'sol',
        'matic', 'avax', 'link', 'uni', 'ltc', 'bch', 'xrp', 'doge',
        'shib', 'atom', 'algo', 'xtz', 'fil', 'vet', 'theta', 'icp',
        name='cryptocurrency'
    )
    
    # Create payment processors configuration table
    op.create_table('payment_processors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('gateway', payment_gateway_enum, nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('supported_currencies', postgresql.ARRAY(sa.String(3)), default=[]),
        sa.Column('supported_countries', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('supported_methods', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('processing_fee_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('processing_fee_fixed', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('minimum_amount', sa.Numeric(10, 2), nullable=False, default=0.01),
        sa.Column('maximum_amount', sa.Numeric(15, 2)),
        sa.Column('settlement_time_days', sa.Integer, nullable=False, default=2),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('webhook_endpoint', sa.String(500)),
        sa.Column('api_key_encrypted', sa.Text),
        sa.Column('api_secret_encrypted', sa.Text),
        sa.Column('configuration', postgresql.JSONB, nullable=False, default={}),
        sa.Column('features', postgresql.JSONB, nullable=False, default={}),
        sa.Column('rate_limits', postgresql.JSONB),
        sa.Column('last_health_check', sa.DateTime),
        sa.Column('health_status', sa.String(20), nullable=False, default='unknown'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create payment transactions table
    op.create_table('payment_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_reference', sa.String(100), nullable=False, unique=True),
        sa.Column('external_transaction_id', sa.String(200)),
        sa.Column('payment_gateway', payment_gateway_enum, nullable=False),
        sa.Column('payment_method', payment_method_enum, nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('amount_usd', sa.Numeric(15, 2), nullable=False),
        sa.Column('exchange_rate', sa.Float),
        sa.Column('status', payment_status_enum, nullable=False, default='pending'),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('payer_email', sa.String(255)),
        sa.Column('payer_name', sa.String(200)),
        sa.Column('billing_address', postgresql.JSONB),
        sa.Column('processing_fee', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('tip_amount', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('risk_score', sa.Float),
        sa.Column('fraud_checks', postgresql.JSONB),
        sa.Column('initiated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime),
        sa.Column('settled_at', sa.DateTime),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('webhook_received_at', sa.DateTime),
        sa.Column('failure_reason', sa.Text),
        sa.Column('refund_reason', sa.Text),
        sa.Column('dispute_reason', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create cryptocurrency transactions table
    op.create_table('cryptocurrency_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payment_transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cryptocurrency', cryptocurrency_enum, nullable=False),
        sa.Column('network', sa.String(50), nullable=False),
        sa.Column('from_address', sa.String(200)),
        sa.Column('to_address', sa.String(200), nullable=False),
        sa.Column('transaction_hash', sa.String(200), unique=True),
        sa.Column('block_number', sa.BigInteger),
        sa.Column('block_hash', sa.String(200)),
        sa.Column('gas_fee', sa.Numeric(18, 8)),
        sa.Column('gas_limit', sa.BigInteger),
        sa.Column('gas_used', sa.BigInteger),
        sa.Column('nonce', sa.BigInteger),
        sa.Column('confirmations', sa.Integer, nullable=False, default=0),
        sa.Column('required_confirmations', sa.Integer, nullable=False, default=6),
        sa.Column('amount_crypto', sa.Numeric(18, 8), nullable=False),
        sa.Column('exchange_rate_usd', sa.Numeric(15, 2)),
        sa.Column('memo', sa.String(500)),
        sa.Column('smart_contract_address', sa.String(200)),
        sa.Column('token_standard', sa.String(20)),
        sa.Column('wallet_type', sa.String(50)),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('compliance_checks', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create tax management table
    op.create_table('tax_management',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payment_transactions.id', ondelete='CASCADE')),
        sa.Column('tax_year', sa.Integer, nullable=False),
        sa.Column('tax_jurisdiction', sa.String(50), nullable=False),
        sa.Column('tax_type', sa.String(50), nullable=False),
        sa.Column('gross_income', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_rate', sa.Float, nullable=False),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_withheld', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('tax_paid', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('tax_outstanding', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('deductions', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('exemptions', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('tax_category', sa.String(100)),
        sa.Column('business_expense', sa.Boolean, nullable=False, default=False),
        sa.Column('invoice_number', sa.String(100)),
        sa.Column('receipt_url', sa.String(500)),
        sa.Column('tax_document_url', sa.String(500)),
        sa.Column('filing_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('filing_date', sa.DateTime),
        sa.Column('due_date', sa.DateTime),
        sa.Column('compliance_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create payment disputes table
    op.create_table('payment_disputes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payment_transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dispute_id', sa.String(100), nullable=False, unique=True),
        sa.Column('dispute_type', sa.String(50), nullable=False),
        sa.Column('dispute_reason', sa.String(100), nullable=False),
        sa.Column('dispute_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('dispute_currency', sa.String(3), nullable=False),
        sa.Column('dispute_status', sa.String(20), nullable=False),
        sa.Column('evidence_required', postgresql.JSONB),
        sa.Column('evidence_submitted', postgresql.JSONB),
        sa.Column('evidence_due_date', sa.DateTime),
        sa.Column('dispute_opened_at', sa.DateTime, nullable=False),
        sa.Column('dispute_deadline', sa.DateTime),
        sa.Column('resolution_date', sa.DateTime),
        sa.Column('resolution_outcome', sa.String(50)),
        sa.Column('resolution_amount', sa.Numeric(15, 2)),
        sa.Column('liability_shift', sa.Boolean, nullable=False, default=False),
        sa.Column('chargeback_fee', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('processor_reference', sa.String(100)),
        sa.Column('customer_communication', sa.Text),
        sa.Column('internal_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create international payment compliance table
    op.create_table('international_payment_compliance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('country_code', sa.String(2), nullable=False),
        sa.Column('regulatory_framework', sa.String(100), nullable=False),
        sa.Column('compliance_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('kyc_status', sa.String(20), nullable=False, default='not_started'),
        sa.Column('aml_status', sa.String(20), nullable=False, default='not_started'),
        sa.Column('sanctions_check_status', sa.String(20), nullable=False, default='not_checked'),
        sa.Column('pep_check_status', sa.String(20), nullable=False, default='not_checked'),
        sa.Column('risk_rating', sa.String(20), nullable=False, default='unknown'),
        sa.Column('transaction_limits', postgresql.JSONB),
        sa.Column('reporting_requirements', postgresql.JSONB),
        sa.Column('required_documents', postgresql.JSONB),
        sa.Column('submitted_documents', postgresql.JSONB),
        sa.Column('verification_documents', postgresql.JSONB),
        sa.Column('compliance_officer', sa.String(200)),
        sa.Column('last_review_date', sa.DateTime),
        sa.Column('next_review_due', sa.DateTime),
        sa.Column('compliance_notes', sa.Text),
        sa.Column('regulatory_changes', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create payment performance metrics table
    op.create_table('payment_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('gateway', payment_gateway_enum, nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('total_transactions', sa.Integer, nullable=False, default=0),
        sa.Column('successful_transactions', sa.Integer, nullable=False, default=0),
        sa.Column('failed_transactions', sa.Integer, nullable=False, default=0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('total_volume', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('average_transaction_value', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('processing_fees_total', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('chargeback_count', sa.Integer, nullable=False, default=0),
        sa.Column('chargeback_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('dispute_count', sa.Integer, nullable=False, default=0),
        sa.Column('fraud_detection_count', sa.Integer, nullable=False, default=0),
        sa.Column('average_processing_time_seconds', sa.Float, nullable=False, default=0.0),
        sa.Column('uptime_percentage', sa.Float, nullable=False, default=100.0),
        sa.Column('api_response_time_ms', sa.Float, nullable=False, default=0.0),
        sa.Column('settlement_time_average_hours', sa.Float, nullable=False, default=0.0),
        sa.Column('customer_satisfaction_score', sa.Float),
        sa.Column('conversion_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Payment Processors indexes
    op.create_index('idx_payment_processors_gateway', 'payment_processors', ['gateway'])
    op.create_index('idx_payment_processors_active', 'payment_processors', ['is_active'])
    op.create_index('idx_payment_processors_health', 'payment_processors', ['health_status'])
    op.create_index('idx_payment_processors_currencies', 'payment_processors', ['supported_currencies'], postgresql_using='gin')
    op.create_index('idx_payment_processors_countries', 'payment_processors', ['supported_countries'], postgresql_using='gin')
    
    # Payment Transactions indexes
    op.create_index('idx_payment_transactions_user_id', 'payment_transactions', ['user_id'])
    op.create_index('idx_payment_transactions_reference', 'payment_transactions', ['transaction_reference'])
    op.create_index('idx_payment_transactions_external_id', 'payment_transactions', ['external_transaction_id'])
    op.create_index('idx_payment_transactions_gateway', 'payment_transactions', ['payment_gateway'])
    op.create_index('idx_payment_transactions_method', 'payment_transactions', ['payment_method'])
    op.create_index('idx_payment_transactions_status', 'payment_transactions', ['status'])
    op.create_index('idx_payment_transactions_type', 'payment_transactions', ['transaction_type'])
    op.create_index('idx_payment_transactions_amount', 'payment_transactions', ['amount'])
    op.create_index('idx_payment_transactions_currency', 'payment_transactions', ['currency'])
    op.create_index('idx_payment_transactions_initiated', 'payment_transactions', ['initiated_at'])
    op.create_index('idx_payment_transactions_processed', 'payment_transactions', ['processed_at'])
    op.create_index('idx_payment_transactions_settled', 'payment_transactions', ['settled_at'])
    op.create_index('idx_payment_transactions_user_status', 'payment_transactions', ['user_id', 'status'])
    
    # Cryptocurrency Transactions indexes
    op.create_index('idx_crypto_transactions_payment_id', 'cryptocurrency_transactions', ['payment_transaction_id'])
    op.create_index('idx_crypto_transactions_crypto', 'cryptocurrency_transactions', ['cryptocurrency'])
    op.create_index('idx_crypto_transactions_network', 'cryptocurrency_transactions', ['network'])
    op.create_index('idx_crypto_transactions_hash', 'cryptocurrency_transactions', ['transaction_hash'])
    op.create_index('idx_crypto_transactions_block', 'cryptocurrency_transactions', ['block_number'])
    op.create_index('idx_crypto_transactions_confirmations', 'cryptocurrency_transactions', ['confirmations'])
    op.create_index('idx_crypto_transactions_from_address', 'cryptocurrency_transactions', ['from_address'])
    op.create_index('idx_crypto_transactions_to_address', 'cryptocurrency_transactions', ['to_address'])
    
    # Tax Management indexes
    op.create_index('idx_tax_management_user_id', 'tax_management', ['user_id'])
    op.create_index('idx_tax_management_payment_id', 'tax_management', ['payment_transaction_id'])
    op.create_index('idx_tax_management_year', 'tax_management', ['tax_year'])
    op.create_index('idx_tax_management_jurisdiction', 'tax_management', ['tax_jurisdiction'])
    op.create_index('idx_tax_management_type', 'tax_management', ['tax_type'])
    op.create_index('idx_tax_management_filing_status', 'tax_management', ['filing_status'])
    op.create_index('idx_tax_management_due_date', 'tax_management', ['due_date'])
    op.create_index('idx_tax_management_outstanding', 'tax_management', ['tax_outstanding'])
    
    # Payment Disputes indexes
    op.create_index('idx_payment_disputes_payment_id', 'payment_disputes', ['payment_transaction_id'])
    op.create_index('idx_payment_disputes_dispute_id', 'payment_disputes', ['dispute_id'])
    op.create_index('idx_payment_disputes_type', 'payment_disputes', ['dispute_type'])
    op.create_index('idx_payment_disputes_status', 'payment_disputes', ['dispute_status'])
    op.create_index('idx_payment_disputes_opened', 'payment_disputes', ['dispute_opened_at'])
    op.create_index('idx_payment_disputes_deadline', 'payment_disputes', ['dispute_deadline'])
    op.create_index('idx_payment_disputes_resolution', 'payment_disputes', ['resolution_date'])
    
    # International Payment Compliance indexes
    op.create_index('idx_intl_compliance_user_id', 'international_payment_compliance', ['user_id'])
    op.create_index('idx_intl_compliance_country', 'international_payment_compliance', ['country_code'])
    op.create_index('idx_intl_compliance_framework', 'international_payment_compliance', ['regulatory_framework'])
    op.create_index('idx_intl_compliance_status', 'international_payment_compliance', ['compliance_status'])
    op.create_index('idx_intl_compliance_kyc', 'international_payment_compliance', ['kyc_status'])
    op.create_index('idx_intl_compliance_aml', 'international_payment_compliance', ['aml_status'])
    op.create_index('idx_intl_compliance_risk', 'international_payment_compliance', ['risk_rating'])
    op.create_index('idx_intl_compliance_review', 'international_payment_compliance', ['next_review_due'])
    
    # Payment Performance Metrics indexes
    op.create_index('idx_payment_metrics_gateway', 'payment_performance_metrics', ['gateway'])
    op.create_index('idx_payment_metrics_date', 'payment_performance_metrics', ['metric_date'])
    op.create_index('idx_payment_metrics_success_rate', 'payment_performance_metrics', ['success_rate'])
    op.create_index('idx_payment_metrics_volume', 'payment_performance_metrics', ['total_volume'])
    op.create_index('idx_payment_metrics_chargeback_rate', 'payment_performance_metrics', ['chargeback_rate'])
    op.create_index('idx_payment_metrics_processing_time', 'payment_performance_metrics', ['average_processing_time_seconds'])
    op.create_index('idx_payment_metrics_uptime', 'payment_performance_metrics', ['uptime_percentage'])


def downgrade() -> None:
    """Downgrade database schema - Remove advanced payment processing tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('payment_performance_metrics')
    op.drop_table('international_payment_compliance')
    op.drop_table('payment_disputes')
    op.drop_table('tax_management')
    op.drop_table('cryptocurrency_transactions')
    op.drop_table('payment_transactions')
    op.drop_table('payment_processors')
    
    # Drop ENUM types
    sa.Enum(name='cryptocurrency').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_method').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='payment_gateway').drop(op.get_bind(), checkfirst=True)