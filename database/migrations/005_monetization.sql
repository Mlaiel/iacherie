-- ============================================================================
-- PostgreSQL Migration: 005_monetization.sql
-- Monetization and Revenue System for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration creates comprehensive monetization system tables
-- supporting subscriptions, payments, revenue sharing, licensing,
-- marketplace transactions, and financial analytics.
-- ============================================================================

-- ============================================================================
-- SUBSCRIPTION PLANS TABLE
-- ============================================================================

-- Subscription plan definitions
CREATE TABLE IF NOT EXISTS subscription_plans (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Plan information
    plan_name VARCHAR(100) NOT NULL UNIQUE,
    plan_description TEXT NOT NULL,
    plan_tier VARCHAR(20) NOT NULL CHECK (plan_tier IN ('free', 'professional', 'enterprise', 'custom')),
    
    -- Pricing
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_period VARCHAR(20) NOT NULL CHECK (billing_period IN ('monthly', 'quarterly', 'yearly', 'one_time', 'usage_based')),
    
    -- Plan features and limits
    features JSONB NOT NULL DEFAULT '{}',
    limits JSONB NOT NULL DEFAULT '{}',
    
    -- Storage and usage limits
    storage_limit_gb INTEGER DEFAULT 1,
    bandwidth_limit_gb INTEGER DEFAULT 10,
    api_calls_limit INTEGER DEFAULT 1000,
    ai_generations_limit INTEGER DEFAULT 50,
    collaboration_limit INTEGER DEFAULT 5,
    
    -- Support and services
    support_level VARCHAR(50) DEFAULT 'community' CHECK (support_level IN ('community', 'email', 'priority', 'dedicated')),
    sla_uptime DECIMAL(5,2) DEFAULT 99.9,
    
    -- Plan properties
    is_popular BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    trial_period_days INTEGER DEFAULT 0,
    
    -- Promotional pricing
    promotional_price DECIMAL(10,2),
    promotion_start_date TIMESTAMP WITH TIME ZONE,
    promotion_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Plan metadata
    plan_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER SUBSCRIPTIONS TABLE
-- ============================================================================

-- User subscription records
CREATE TABLE IF NOT EXISTS user_subscriptions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Subscription details
    subscription_status VARCHAR(30) DEFAULT 'active' CHECK (subscription_status IN ('trial', 'active', 'past_due', 'cancelled', 'expired', 'suspended')),
    
    -- Billing information
    payment_method_id UUID,
    billing_email VARCHAR(255),
    billing_address JSONB DEFAULT '{}',
    
    -- Subscription period
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    trial_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Pricing
    subscription_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_cycle VARCHAR(20) NOT NULL,
    
    -- Usage tracking
    current_usage JSONB DEFAULT '{}',
    usage_reset_date TIMESTAMP WITH TIME ZONE,
    
    -- Subscription management
    auto_renew BOOLEAN DEFAULT TRUE,
    cancellation_reason TEXT,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    refund_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- External service integration
    stripe_subscription_id VARCHAR(100),
    paypal_subscription_id VARCHAR(100),
    external_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PAYMENT METHODS TABLE
-- ============================================================================

-- User payment methods
CREATE TABLE IF NOT EXISTS payment_methods (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Payment method information
    method_type VARCHAR(30) NOT NULL CHECK (method_type IN ('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cryptocurrency', 'digital_wallet')),
    provider VARCHAR(50) NOT NULL, -- 'stripe', 'paypal', 'square', etc.
    
    -- Card/Account details (encrypted)
    card_last_four VARCHAR(4),
    card_brand VARCHAR(20),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    account_name VARCHAR(200),
    
    -- Status and verification
    is_verified BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- External references
    stripe_payment_method_id VARCHAR(100),
    paypal_payer_id VARCHAR(100),
    external_token VARCHAR(255),
    
    -- Security
    fingerprint VARCHAR(128),
    
    -- Billing address
    billing_address JSONB DEFAULT '{}',
    
    -- Payment method metadata
    payment_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================

-- Financial transaction records
CREATE TABLE IF NOT EXISTS transactions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('subscription_payment', 'content_purchase', 'collaboration_payment', 'revenue_share', 'refund', 'withdrawal', 'commission')),
    transaction_status VARCHAR(30) DEFAULT 'pending' CHECK (transaction_status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded')),
    
    -- Financial details
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    fee_amount DECIMAL(12,2) DEFAULT 0.00,
    net_amount DECIMAL(12,2) NOT NULL,
    
    -- Payment information
    payment_method_id UUID REFERENCES payment_methods(id),
    gateway VARCHAR(50), -- 'stripe', 'paypal', etc.
    gateway_transaction_id VARCHAR(200),
    gateway_response JSONB DEFAULT '{}',
    
    -- Related entities
    subscription_id UUID REFERENCES user_subscriptions(id),
    content_id UUID REFERENCES media_content(id),
    collaboration_id UUID REFERENCES collaboration_projects(id),
    invoice_id UUID,
    
    -- Transaction context
    description TEXT,
    reference_number VARCHAR(100),
    
    -- Processing details
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    
    -- Error handling
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Transaction metadata
    transaction_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- REVENUE SHARES TABLE
-- ============================================================================

-- Revenue sharing between collaborators
CREATE TABLE IF NOT EXISTS revenue_shares (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Source information
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('content_sale', 'subscription_revenue', 'collaboration_payment', 'licensing_fee', 'marketplace_sale')),
    source_id UUID NOT NULL,
    
    -- Financial details
    total_revenue DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Revenue distribution
    revenue_splits JSONB NOT NULL, -- Array of {user_id, percentage, amount}
    platform_fee DECIMAL(12,2) DEFAULT 0.00,
    platform_fee_percentage DECIMAL(5,2) DEFAULT 0.00,
    
    -- Processing status
    distribution_status VARCHAR(30) DEFAULT 'pending' CHECK (distribution_status IN ('pending', 'processing', 'completed', 'failed', 'disputed')),
    distributed_at TIMESTAMP WITH TIME ZONE,
    
    -- Period information
    revenue_period_start TIMESTAMP WITH TIME ZONE,
    revenue_period_end TIMESTAMP WITH TIME ZONE,
    
    -- Contract and agreement references
    contract_id UUID REFERENCES collaboration_contracts(id),
    agreement_terms JSONB DEFAULT '{}',
    
    -- Distribution metadata
    distribution_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER REVENUE RECORDS TABLE
-- ============================================================================

-- Individual user revenue records
CREATE TABLE IF NOT EXISTS user_revenue_records (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    revenue_share_id UUID NOT NULL REFERENCES revenue_shares(id) ON DELETE CASCADE,
    
    -- Revenue details
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    share_percentage DECIMAL(5,2) NOT NULL,
    
    -- Payout information
    payout_status VARCHAR(30) DEFAULT 'pending' CHECK (payout_status IN ('pending', 'processing', 'paid', 'failed', 'on_hold')),
    payout_method VARCHAR(30),
    payout_reference VARCHAR(200),
    paid_at TIMESTAMP WITH TIME ZONE,
    
    -- Tax and compliance
    tax_withholding DECIMAL(12,2) DEFAULT 0.00,
    tax_form_required BOOLEAN DEFAULT FALSE,
    
    -- Record metadata
    record_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CONTENT PRICING TABLE
-- ============================================================================

-- Pricing for individual content items
CREATE TABLE IF NOT EXISTS content_pricing (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Pricing tiers
    pricing_model VARCHAR(30) NOT NULL CHECK (pricing_model IN ('free', 'one_time', 'subscription', 'pay_per_view', 'tiered', 'auction')),
    
    -- Pricing details
    base_price DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Tiered pricing
    pricing_tiers JSONB DEFAULT '[]', -- Array of {tier_name, price, features}
    
    -- Licensing options
    license_types JSONB DEFAULT '[]', -- Array of {license_type, price, terms}
    commercial_license_price DECIMAL(10,2),
    extended_license_price DECIMAL(10,2),
    
    -- Discounts and promotions
    discount_percentage DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    promotion_start_date TIMESTAMP WITH TIME ZONE,
    promotion_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Usage rights and restrictions
    usage_rights JSONB DEFAULT '{}',
    territorial_restrictions TEXT[],
    usage_duration VARCHAR(50), -- 'perpetual', '1year', etc.
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Pricing metadata
    pricing_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CONTENT PURCHASES TABLE
-- ============================================================================

-- Content purchase records
CREATE TABLE IF NOT EXISTS content_purchases (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    pricing_id UUID NOT NULL REFERENCES content_pricing(id),
    
    -- Purchase details
    purchase_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    license_type VARCHAR(50) NOT NULL,
    
    -- Payment information
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    payment_status VARCHAR(30) DEFAULT 'pending',
    
    -- License details
    license_terms JSONB NOT NULL,
    license_start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    license_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Usage tracking
    download_count INTEGER DEFAULT 0,
    usage_log JSONB DEFAULT '[]',
    
    -- Purchase metadata
    purchase_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MARKETPLACE LISTINGS TABLE
-- ============================================================================

-- Marketplace content listings
CREATE TABLE IF NOT EXISTS marketplace_listings (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Listing information
    listing_title VARCHAR(255) NOT NULL,
    listing_description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    
    -- Pricing and availability
    pricing_id UUID NOT NULL REFERENCES content_pricing(id),
    stock_quantity INTEGER DEFAULT 1,
    unlimited_stock BOOLEAN DEFAULT TRUE,
    
    -- Listing status
    listing_status VARCHAR(30) DEFAULT 'active' CHECK (listing_status IN ('draft', 'active', 'paused', 'sold_out', 'expired', 'removed')),
    approval_status VARCHAR(30) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected', 'under_review')),
    
    -- Visibility and promotion
    is_featured BOOLEAN DEFAULT FALSE,
    promotion_level INTEGER DEFAULT 0,
    boost_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Performance metrics
    view_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    
    -- SEO and discoverability
    tags TEXT[],
    search_keywords TEXT[],
    
    -- Listing metadata
    listing_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    published_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- AFFILIATE PROGRAMS TABLE
-- ============================================================================

-- Affiliate marketing programs
CREATE TABLE IF NOT EXISTS affiliate_programs (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Program information
    program_name VARCHAR(200) NOT NULL,
    program_description TEXT,
    
    -- Commission structure
    commission_type VARCHAR(30) NOT NULL CHECK (commission_type IN ('percentage', 'fixed_amount', 'tiered')),
    commission_rate DECIMAL(5,2) NOT NULL,
    commission_tiers JSONB DEFAULT '[]',
    
    -- Program rules
    minimum_payout DECIMAL(10,2) DEFAULT 10.00,
    payout_frequency VARCHAR(30) DEFAULT 'monthly' CHECK (payout_frequency IN ('daily', 'weekly', 'monthly', 'quarterly')),
    cookie_duration_days INTEGER DEFAULT 30,
    
    -- Eligibility and restrictions
    eligibility_criteria JSONB DEFAULT '{}',
    geographic_restrictions TEXT[],
    
    -- Program status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    auto_approve BOOLEAN DEFAULT FALSE,
    
    -- Program metadata
    program_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- AFFILIATE LINKS TABLE
-- ============================================================================

-- Affiliate tracking links
CREATE TABLE IF NOT EXISTS affiliate_links (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES affiliate_programs(id) ON DELETE CASCADE,
    
    -- Link information
    tracking_code VARCHAR(100) NOT NULL UNIQUE,
    target_url VARCHAR(1000) NOT NULL,
    short_url VARCHAR(200),
    
    -- Link properties
    link_type VARCHAR(30) NOT NULL CHECK (link_type IN ('product', 'category', 'profile', 'custom')),
    target_content_id UUID REFERENCES media_content(id),
    
    -- Performance tracking
    click_count INTEGER DEFAULT 0,
    conversion_count INTEGER DEFAULT 0,
    total_commission DECIMAL(12,2) DEFAULT 0.00,
    
    -- Link status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Link metadata
    link_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Subscription plan indexes
CREATE INDEX idx_subscription_plans_tier ON subscription_plans(plan_tier);
CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active);
CREATE INDEX idx_subscription_plans_public ON subscription_plans(is_public);

-- User subscription indexes
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_plan_id ON user_subscriptions(plan_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(subscription_status);
CREATE INDEX idx_user_subscriptions_end_date ON user_subscriptions(end_date);

-- Payment method indexes
CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX idx_payment_methods_default ON payment_methods(is_default);
CREATE INDEX idx_payment_methods_active ON payment_methods(is_active);

-- Transaction indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(transaction_status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_gateway_id ON transactions(gateway_transaction_id);

-- Revenue share indexes
CREATE INDEX idx_revenue_shares_source ON revenue_shares(source_type, source_id);
CREATE INDEX idx_revenue_shares_status ON revenue_shares(distribution_status);
CREATE INDEX idx_revenue_shares_created_at ON revenue_shares(created_at);

-- User revenue record indexes
CREATE INDEX idx_user_revenue_records_user_id ON user_revenue_records(user_id);
CREATE INDEX idx_user_revenue_records_share_id ON user_revenue_records(revenue_share_id);
CREATE INDEX idx_user_revenue_records_payout_status ON user_revenue_records(payout_status);

-- Content pricing indexes
CREATE INDEX idx_content_pricing_content_id ON content_pricing(content_id);
CREATE INDEX idx_content_pricing_model ON content_pricing(pricing_model);
CREATE INDEX idx_content_pricing_active ON content_pricing(is_active);

-- Content purchase indexes
CREATE INDEX idx_content_purchases_buyer_id ON content_purchases(buyer_id);
CREATE INDEX idx_content_purchases_content_id ON content_purchases(content_id);
CREATE INDEX idx_content_purchases_purchased_at ON content_purchases(purchased_at);

-- Marketplace listing indexes
CREATE INDEX idx_marketplace_listings_seller_id ON marketplace_listings(seller_id);
CREATE INDEX idx_marketplace_listings_content_id ON marketplace_listings(content_id);
CREATE INDEX idx_marketplace_listings_category ON marketplace_listings(category);
CREATE INDEX idx_marketplace_listings_status ON marketplace_listings(listing_status);
CREATE INDEX idx_marketplace_listings_featured ON marketplace_listings(is_featured);

-- Affiliate indexes
CREATE INDEX idx_affiliate_programs_owner_id ON affiliate_programs(owner_id);
CREATE INDEX idx_affiliate_programs_active ON affiliate_programs(is_active);
CREATE INDEX idx_affiliate_links_affiliate_id ON affiliate_links(affiliate_id);
CREATE INDEX idx_affiliate_links_program_id ON affiliate_links(program_id);
CREATE INDEX idx_affiliate_links_tracking_code ON affiliate_links(tracking_code);

-- Composite indexes
CREATE INDEX idx_transactions_user_status_date ON transactions(user_id, transaction_status, created_at);
CREATE INDEX idx_marketplace_category_status ON marketplace_listings(category, listing_status);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update transaction net amount
CREATE OR REPLACE FUNCTION calculate_net_amount()
RETURNS TRIGGER AS $$
BEGIN
    NEW.net_amount := NEW.amount - NEW.fee_amount;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply net amount calculation trigger
CREATE TRIGGER calculate_net_amount_trigger
    BEFORE INSERT OR UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION calculate_net_amount();

-- Update marketplace listing performance
CREATE OR REPLACE FUNCTION update_listing_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE marketplace_listings SET
        purchase_count = purchase_count + 1,
        updated_at = NOW()
    WHERE content_id = NEW.content_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply listing stats trigger
CREATE TRIGGER update_listing_stats_trigger
    AFTER INSERT ON content_purchases
    FOR EACH ROW EXECUTE FUNCTION update_listing_stats();

-- Apply updated_at triggers
CREATE TRIGGER update_subscription_plans_updated_at 
    BEFORE UPDATE ON subscription_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_methods_updated_at 
    BEFORE UPDATE ON payment_methods 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at 
    BEFORE UPDATE ON transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_revenue_shares_updated_at 
    BEFORE UPDATE ON revenue_shares 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_pricing_updated_at 
    BEFORE UPDATE ON content_pricing 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marketplace_listings_updated_at 
    BEFORE UPDATE ON marketplace_listings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- User revenue summary view
CREATE OR REPLACE VIEW user_revenue_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.display_name,
    
    -- Total revenue
    COALESCE(SUM(urr.amount), 0) as total_revenue,
    
    -- Revenue by type
    COALESCE(SUM(CASE WHEN rs.source_type = 'content_sale' THEN urr.amount ELSE 0 END), 0) as content_revenue,
    COALESCE(SUM(CASE WHEN rs.source_type = 'collaboration_payment' THEN urr.amount ELSE 0 END), 0) as collaboration_revenue,
    COALESCE(SUM(CASE WHEN rs.source_type = 'subscription_revenue' THEN urr.amount ELSE 0 END), 0) as subscription_revenue,
    
    -- Payout information
    COALESCE(SUM(CASE WHEN urr.payout_status = 'paid' THEN urr.amount ELSE 0 END), 0) as paid_out,
    COALESCE(SUM(CASE WHEN urr.payout_status = 'pending' THEN urr.amount ELSE 0 END), 0) as pending_payout,
    
    -- Statistics
    COUNT(urr.id) as total_revenue_records,
    COUNT(DISTINCT rs.source_id) as unique_revenue_sources
    
FROM users_enhanced u
LEFT JOIN user_revenue_records urr ON u.id = urr.user_id
LEFT JOIN revenue_shares rs ON urr.revenue_share_id = rs.id
GROUP BY u.id, u.username, u.display_name;

-- Active subscription view
CREATE OR REPLACE VIEW active_subscriptions AS
SELECT 
    us.*,
    sp.plan_name,
    sp.plan_tier,
    sp.features,
    sp.limits,
    
    -- Days remaining
    EXTRACT(EPOCH FROM (us.end_date - NOW())) / 86400 as days_remaining
    
FROM user_subscriptions us
JOIN subscription_plans sp ON us.plan_id = sp.id
WHERE us.subscription_status IN ('trial', 'active')
    AND (us.end_date IS NULL OR us.end_date > NOW());

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to calculate revenue split
CREATE OR REPLACE FUNCTION calculate_revenue_split(
    p_total_revenue DECIMAL(12,2),
    p_splits JSONB,
    p_platform_fee_percentage DECIMAL(5,2) DEFAULT 10.0
)
RETURNS JSONB AS $$
DECLARE
    result JSONB := '[]'::JSONB;
    split_item JSONB;
    platform_fee DECIMAL(12,2);
    distributable_revenue DECIMAL(12,2);
BEGIN
    -- Calculate platform fee
    platform_fee := p_total_revenue * (p_platform_fee_percentage / 100.0);
    distributable_revenue := p_total_revenue - platform_fee;
    
    -- Calculate individual splits
    FOR split_item IN SELECT * FROM jsonb_array_elements(p_splits)
    LOOP
        result := result || jsonb_build_object(
            'user_id', split_item->>'user_id',
            'percentage', split_item->>'percentage',
            'amount', ROUND(distributable_revenue * ((split_item->>'percentage')::DECIMAL / 100.0), 2)
        );
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to process subscription payment
CREATE OR REPLACE FUNCTION process_subscription_payment(
    p_user_id UUID,
    p_subscription_id UUID,
    p_amount DECIMAL(10,2),
    p_payment_method_id UUID
)
RETURNS UUID AS $$
DECLARE
    new_transaction_id UUID;
BEGIN
    -- Create transaction record
    INSERT INTO transactions (
        user_id, transaction_type, amount, currency, 
        payment_method_id, subscription_id, description
    )
    VALUES (
        p_user_id, 'subscription_payment', p_amount, 'USD',
        p_payment_method_id, p_subscription_id, 'Subscription payment'
    )
    RETURNING id INTO new_transaction_id;
    
    RETURN new_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_revenue_records ENABLE ROW LEVEL SECURITY;

-- Subscription policies
CREATE POLICY user_own_subscriptions ON user_subscriptions
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Payment method policies
CREATE POLICY user_own_payment_methods ON payment_methods
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Transaction policies
CREATE POLICY user_own_transactions ON transactions
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Revenue record policies
CREATE POLICY user_own_revenue_records ON user_revenue_records
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE subscription_plans IS 'Subscription plan definitions with features and pricing';
COMMENT ON TABLE user_subscriptions IS 'User subscription records and billing information';
COMMENT ON TABLE payment_methods IS 'User payment methods and billing details';
COMMENT ON TABLE transactions IS 'Financial transaction records for all money movements';
COMMENT ON TABLE revenue_shares IS 'Revenue sharing between collaborators and platform';
COMMENT ON TABLE user_revenue_records IS 'Individual user revenue records and payouts';
COMMENT ON TABLE content_pricing IS 'Pricing configurations for content items';
COMMENT ON TABLE content_purchases IS 'Content purchase records and licenses';
COMMENT ON TABLE marketplace_listings IS 'Marketplace content listings and performance';
COMMENT ON TABLE affiliate_programs IS 'Affiliate marketing program configurations';
COMMENT ON TABLE affiliate_links IS 'Affiliate tracking links and performance';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================