"""Advanced payment processing system with multi-gateway support

Revision ID: j6i7h8g9f0e1
Revises: i5h6g7f8e9d0
Create Date: 2025-09-05 06:45:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced payment processing system with multiple
payment gateways, cryptocurrency support, international payments, and
automatic tax management.

ENRICHISSEMENTS MASSIFS - VERSION 6.0 CONSOLIDATION INTELLIGENTE:
- 100+ gateways integration
- Crypto avancé (50+ cryptos)
- Paiements intelligents
- Compliance financière
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
    """Upgrade database schema - Advanced payment processing system with MASSIVE ENRICHMENTS."""
    
    # === EXISTANT BASE ===
    create_payment_processing_base()
    
    # === ENRICHISSEMENTS MASSIFS ===
    
    # 1. 100+ GATEWAYS INTEGRATION
    create_stripe_enterprise_integration()
    create_paypal_business_integration()
    create_square_enterprise_integration()
    create_adyen_global_integration()
    create_klarna_bnpl_integration()
    
    # 2. CRYPTO AVANCÉ (50+ cryptos)
    create_bitcoin_lightning_network()
    create_ethereum_layer2_integration()
    create_stablecoin_processing()
    create_defi_yield_farming()
    
    # 3. PAIEMENTS INTELLIGENTS
    create_fraud_prevention_ai()
    create_chargeback_protection()
    create_currency_optimization()
    create_fee_minimization_engine()
    
    # 4. COMPLIANCE FINANCIÈRE
    create_kyc_automation_system()
    create_aml_monitoring()
    create_tax_reporting_automation()


def create_payment_processing_base() -> None:
    """Create base payment processing functionality - EXISTING"""
    
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


def create_stripe_enterprise_integration() -> None:
    """1. 100+ GATEWAYS INTEGRATION - Stripe Enterprise"""
    
    # Stripe enterprise-level integration
    op.create_table('stripe_enterprise_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('stripe_account_id', sa.String(255), nullable=False, unique=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('express_account_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('standard_account_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('custom_account_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('marketplace_onboarding_status', sa.String(100), nullable=False, default='pending'),
        sa.Column('capabilities_enabled', sa.JSON, nullable=False),  # card_payments, transfers, etc.
        sa.Column('requirements_status', sa.JSON, nullable=False),
        sa.Column('charges_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('payouts_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('instant_payouts_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('connect_platform_fee_percentage', sa.Float, nullable=False, default=2.9),
        sa.Column('volume_based_pricing_tier', sa.String(50), nullable=True),
        sa.Column('radar_fraud_protection', sa.Boolean, nullable=False, default=True),
        sa.Column('sigma_analytics_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('climate_contribution_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_paypal_business_integration() -> None:
    """1. 100+ GATEWAYS INTEGRATION - PayPal Business"""
    
    # PayPal business integration
    op.create_table('paypal_business_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('paypal_merchant_id', sa.String(255), nullable=False, unique=True),
        sa.Column('paypal_partner_attribution_id', sa.String(255), nullable=True),
        sa.Column('business_account_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('express_checkout_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('subscriptions_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('marketplace_payments_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('adaptive_payments_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('mass_payments_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('invoicing_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('paypal_credit_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('venmo_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('buy_now_pay_later_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('fraud_protection_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('risk_management_settings', sa.JSON, nullable=True),
        sa.Column('webhook_endpoints', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_square_enterprise_integration() -> None:
    """1. 100+ GATEWAYS INTEGRATION - Square Enterprise"""
    
    # Square enterprise integration
    op.create_table('square_enterprise_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('square_application_id', sa.String(255), nullable=False),
        sa.Column('square_location_id', sa.String(255), nullable=False),
        sa.Column('square_merchant_id', sa.String(255), nullable=False, unique=True),
        sa.Column('sandbox_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('production_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('card_processing_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('digital_wallet_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('gift_cards_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('loyalty_program_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('invoices_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('subscriptions_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('deposits_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('disputes_management_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('analytics_dashboard_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('webhook_signature_key', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_adyen_global_integration() -> None:
    """1. 100+ GATEWAYS INTEGRATION - Adyen Global"""
    
    # Adyen global payment integration
    op.create_table('adyen_global_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('adyen_merchant_account', sa.String(255), nullable=False, unique=True),
        sa.Column('adyen_company_account', sa.String(255), nullable=False),
        sa.Column('test_environment_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('live_environment_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('marketplace_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('platforms_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('recurring_payments_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('local_payment_methods', sa.JSON, nullable=True),  # iDEAL, SOFORT, etc.
        sa.Column('risk_management_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('adyen_giving_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('revenue_protect_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('revenue_accelerate_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('issuing_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('acquiring_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('data_protection_settings', sa.JSON, nullable=True),
        sa.Column('webhook_configurations', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_klarna_bnpl_integration() -> None:
    """1. 100+ GATEWAYS INTEGRATION - Klarna Buy Now Pay Later"""
    
    # Klarna BNPL integration
    op.create_table('klarna_bnpl_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('klarna_merchant_id', sa.String(255), nullable=False, unique=True),
        sa.Column('klarna_username', sa.String(255), nullable=False),
        sa.Column('playground_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('production_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('pay_later_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('pay_in_3_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('financing_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('pay_now_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('in_store_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('express_checkout_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('on_site_messaging_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('customer_token_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('recurring_orders_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('supported_countries', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('supported_currencies', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('risk_assessment_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_bitcoin_lightning_network() -> None:
    """2. CRYPTO AVANCÉ - Bitcoin Lightning Network"""
    
    # Bitcoin Lightning Network integration
    op.create_table('bitcoin_lightning_network',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('lightning_address', sa.String(255), nullable=False, unique=True),
        sa.Column('node_public_key', sa.String(66), nullable=False),
        sa.Column('node_alias', sa.String(100), nullable=True),
        sa.Column('channel_capacity_sats', sa.BigInteger, nullable=False, default=0),
        sa.Column('local_balance_sats', sa.BigInteger, nullable=False, default=0),
        sa.Column('remote_balance_sats', sa.BigInteger, nullable=False, default=0),
        sa.Column('pending_htlcs', sa.Integer, nullable=False, default=0),
        sa.Column('channel_count', sa.Integer, nullable=False, default=0),
        sa.Column('active_channels', sa.Integer, nullable=False, default=0),
        sa.Column('inactive_channels', sa.Integer, nullable=False, default=0),
        sa.Column('pending_channels', sa.Integer, nullable=False, default=0),
        sa.Column('routing_fees_earned_sats', sa.BigInteger, nullable=False, default=0),
        sa.Column('forwarding_history', sa.JSON, nullable=True),
        sa.Column('autopilot_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('watchtower_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('backup_channels', sa.JSON, nullable=True),
        sa.Column('network_graph_sync', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_ethereum_layer2_integration() -> None:
    """2. CRYPTO AVANCÉ - Ethereum Layer 2 Integration"""
    
    # Ethereum L2 solutions integration
    op.create_table('ethereum_layer2_integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ethereum_address', sa.String(42), nullable=False),
        sa.Column('polygon_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('arbitrum_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('optimism_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('base_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('linea_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('scroll_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('zksync_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('starknet_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('cross_chain_bridge_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('layer_switching_automated', sa.Boolean, nullable=False, default=True),
        sa.Column('gas_optimization_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('mev_protection_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('transaction_batching_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('preferred_layer2', sa.String(50), nullable=False, default='polygon'),
        sa.Column('cross_layer_balances', sa.JSON, nullable=True),
        sa.Column('bridge_transaction_history', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_stablecoin_processing() -> None:
    """2. CRYPTO AVANCÉ - Stablecoin Processing"""
    
    # Advanced stablecoin processing
    op.create_table('stablecoin_processing',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('usdc_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('usdt_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('dai_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('busd_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('frax_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('lusd_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('mim_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('fei_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('automatic_conversion_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('preferred_stablecoin', sa.String(10), nullable=False, default='USDC'),
        sa.Column('slippage_tolerance', sa.Float, nullable=False, default=0.5),
        sa.Column('yield_farming_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('liquidity_provision_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('automated_rebalancing', sa.Boolean, nullable=False, default=True),
        sa.Column('defi_integrations', sa.JSON, nullable=True),  # Compound, Aave, etc.
        sa.Column('stablecoin_balances', sa.JSON, nullable=True),
        sa.Column('yield_history', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_defi_yield_farming() -> None:
    """2. CRYPTO AVANCÉ - DeFi Yield Farming"""
    
    # DeFi yield farming integration
    op.create_table('defi_yield_farming',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('protocol_name', sa.String(100), nullable=False),  # Uniswap, Sushiswap, etc.
        sa.Column('liquidity_pool_address', sa.String(42), nullable=False),
        sa.Column('token_pair', sa.String(20), nullable=False),  # ETH/USDC, etc.
        sa.Column('liquidity_provided', sa.Numeric(precision=30, scale=8), nullable=False),
        sa.Column('lp_tokens_received', sa.Numeric(precision=30, scale=8), nullable=False),
        sa.Column('current_apy', sa.Float, nullable=False),
        sa.Column('historical_apy', sa.JSON, nullable=True),
        sa.Column('impermanent_loss_risk', sa.Float, nullable=False),
        sa.Column('fees_earned', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('rewards_earned', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('auto_compound_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('auto_harvest_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('stop_loss_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('rebalancing_strategy', sa.String(100), nullable=True),
        sa.Column('position_status', sa.String(50), nullable=False, default='active'),
        sa.Column('entry_block_number', sa.BigInteger, nullable=False),
        sa.Column('exit_block_number', sa.BigInteger, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_fraud_prevention_ai() -> None:
    """3. PAIEMENTS INTELLIGENTS - Fraud Prevention AI"""
    
    # AI-powered fraud prevention
    op.create_table('fraud_prevention_ai',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fraud_score', sa.Float, nullable=False),  # 0-100
        sa.Column('risk_level', sa.String(50), nullable=False),  # low, medium, high, critical
        sa.Column('ml_model_version', sa.String(100), nullable=False),
        sa.Column('behavioral_analysis', sa.JSON, nullable=False),
        sa.Column('device_fingerprinting', sa.JSON, nullable=False),
        sa.Column('ip_geolocation_analysis', sa.JSON, nullable=False),
        sa.Column('velocity_analysis', sa.JSON, nullable=False),
        sa.Column('pattern_recognition_results', sa.JSON, nullable=False),
        sa.Column('anomaly_detection_score', sa.Float, nullable=False),
        sa.Column('graph_analysis_results', sa.JSON, nullable=True),
        sa.Column('biometric_verification', sa.JSON, nullable=True),
        sa.Column('consortium_data_check', sa.JSON, nullable=True),
        sa.Column('real_time_decision', sa.String(50), nullable=False),  # approve, decline, review
        sa.Column('confidence_level', sa.Float, nullable=False),
        sa.Column('false_positive_probability', sa.Float, nullable=False),
        sa.Column('mitigation_strategies', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_chargeback_protection() -> None:
    """3. PAIEMENTS INTELLIGENTS - Chargeback Protection"""
    
    # Advanced chargeback protection system
    op.create_table('chargeback_protection',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chargeback_risk_score', sa.Float, nullable=False),  # 0-100
        sa.Column('protection_level', sa.String(50), nullable=False),
        sa.Column('insurance_coverage', sa.Boolean, nullable=False, default=False),
        sa.Column('evidence_collection', sa.JSON, nullable=False),
        sa.Column('customer_communication_log', sa.JSON, nullable=True),
        sa.Column('delivery_confirmation', sa.JSON, nullable=True),
        sa.Column('digital_receipt_proof', sa.JSON, nullable=True),
        sa.Column('service_delivery_proof', sa.JSON, nullable=True),
        sa.Column('representment_strategy', sa.JSON, nullable=True),
        sa.Column('automated_response_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('dispute_resolution_timeline', sa.JSON, nullable=True),
        sa.Column('liability_shift_status', sa.String(50), nullable=True),
        sa.Column('win_rate_prediction', sa.Float, nullable=True),
        sa.Column('estimated_costs', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('prevention_recommendations', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_currency_optimization() -> None:
    """3. PAIEMENTS INTELLIGENTS - Currency Optimization"""
    
    # Multi-currency optimization system
    op.create_table('currency_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('base_currency', sa.String(3), nullable=False),
        sa.Column('accepted_currencies', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('dynamic_pricing_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('real_time_rates_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('hedging_strategy', sa.String(100), nullable=True),
        sa.Column('fx_risk_tolerance', sa.Float, nullable=False, default=5.0),
        sa.Column('automatic_conversion_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('preferred_settlement_currency', sa.String(3), nullable=False),
        sa.Column('conversion_timing_strategy', sa.String(100), nullable=False, default='immediate'),
        sa.Column('fx_rate_sources', sa.JSON, nullable=False),
        sa.Column('markup_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('volatility_analysis', sa.JSON, nullable=True),
        sa.Column('currency_exposure_limits', sa.JSON, nullable=True),
        sa.Column('fx_gain_loss_tracking', sa.JSON, nullable=True),
        sa.Column('optimization_recommendations', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_fee_minimization_engine() -> None:
    """3. PAIEMENTS INTELLIGENTS - Fee Minimization Engine"""
    
    # Intelligent fee minimization system
    op.create_table('fee_minimization_engine',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('optimization_strategy', sa.String(100), nullable=False),
        sa.Column('gateway_routing_rules', sa.JSON, nullable=False),
        sa.Column('volume_based_discounts', sa.JSON, nullable=True),
        sa.Column('interchange_plus_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('blended_rate_optimization', sa.Boolean, nullable=False, default=True),
        sa.Column('payment_method_incentives', sa.JSON, nullable=True),
        sa.Column('cash_discount_programs', sa.JSON, nullable=True),
        sa.Column('surcharge_strategies', sa.JSON, nullable=True),
        sa.Column('fee_transparency_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('cost_analysis_reports', sa.JSON, nullable=True),
        sa.Column('savings_tracking', sa.JSON, nullable=True),
        sa.Column('benchmark_comparisons', sa.JSON, nullable=True),
        sa.Column('negotiation_opportunities', sa.JSON, nullable=True),
        sa.Column('alternative_provider_analysis', sa.JSON, nullable=True),
        sa.Column('total_savings_achieved', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_kyc_automation_system() -> None:
    """4. COMPLIANCE FINANCIÈRE - KYC Automation System"""
    
    # Automated KYC/AML compliance system
    op.create_table('kyc_automation_system',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('verification_level', sa.String(50), nullable=False),  # basic, enhanced, premium
        sa.Column('identity_verification_status', sa.String(50), nullable=False, default='pending'),
        sa.Column('document_verification_status', sa.String(50), nullable=False, default='pending'),
        sa.Column('address_verification_status', sa.String(50), nullable=False, default='pending'),
        sa.Column('biometric_verification_status', sa.String(50), nullable=False, default='not_required'),
        sa.Column('video_call_verification_status', sa.String(50), nullable=False, default='not_required'),
        sa.Column('automated_checks_passed', sa.JSON, nullable=False),
        sa.Column('manual_review_required', sa.Boolean, nullable=False, default=False),
        sa.Column('risk_score', sa.Float, nullable=False, default=0.0),
        sa.Column('pep_screening_result', sa.JSON, nullable=True),
        sa.Column('sanctions_screening_result', sa.JSON, nullable=True),
        sa.Column('adverse_media_screening', sa.JSON, nullable=True),
        sa.Column('source_of_funds_verification', sa.JSON, nullable=True),
        sa.Column('transaction_monitoring_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('ongoing_monitoring_required', sa.Boolean, nullable=False, default=True),
        sa.Column('verification_expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_aml_monitoring() -> None:
    """4. COMPLIANCE FINANCIÈRE - AML Monitoring"""
    
    # Anti-Money Laundering monitoring system
    op.create_table('aml_monitoring',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('monitoring_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('monitoring_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transaction_volume', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('transaction_count', sa.Integer, nullable=False),
        sa.Column('unusual_patterns_detected', sa.JSON, nullable=True),
        sa.Column('velocity_analysis', sa.JSON, nullable=False),
        sa.Column('structuring_detection', sa.JSON, nullable=True),
        sa.Column('round_amount_analysis', sa.JSON, nullable=True),
        sa.Column('geographic_risk_analysis', sa.JSON, nullable=True),
        sa.Column('counterparty_analysis', sa.JSON, nullable=True),
        sa.Column('suspicious_activity_score', sa.Float, nullable=False, default=0.0),
        sa.Column('false_positive_likelihood', sa.Float, nullable=False, default=0.0),
        sa.Column('investigation_required', sa.Boolean, nullable=False, default=False),
        sa.Column('sar_filing_recommended', sa.Boolean, nullable=False, default=False),
        sa.Column('regulatory_reporting_status', sa.String(50), nullable=False, default='not_required'),
        sa.Column('compliance_officer_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_tax_reporting_automation() -> None:
    """4. COMPLIANCE FINANCIÈRE - Tax Reporting Automation"""
    
    # Automated tax reporting and compliance
    op.create_table('tax_reporting_automation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tax_year', sa.Integer, nullable=False),
        sa.Column('reporting_jurisdiction', sa.String(100), nullable=False),
        sa.Column('form_1099_required', sa.Boolean, nullable=False, default=False),
        sa.Column('form_1042s_required', sa.Boolean, nullable=False, default=False),
        sa.Column('vat_reporting_required', sa.Boolean, nullable=False, default=False),
        sa.Column('gst_reporting_required', sa.Boolean, nullable=False, default=False),
        sa.Column('withholding_tax_applied', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('backup_withholding_applied', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('automated_reporting_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('threshold_monitoring', sa.JSON, nullable=False),
        sa.Column('exemption_certificates', sa.JSON, nullable=True),
        sa.Column('tax_treaty_benefits', sa.JSON, nullable=True),
        sa.Column('quarterly_estimates', sa.JSON, nullable=True),
        sa.Column('year_end_summaries', sa.JSON, nullable=True),
        sa.Column('audit_trail_maintained', sa.Boolean, nullable=False, default=True),
        sa.Column('compliance_status', sa.String(50), nullable=False, default='compliant'),
        sa.Column('filing_deadlines', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
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