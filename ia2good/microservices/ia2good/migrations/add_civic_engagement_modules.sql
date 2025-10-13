-- Migration: Add Issues, Events, and Campaigns tables
-- Date: 2024-12-XX
-- Description: Civic engagement modules - Issues reporting, Events management, Campaigns (petitions & fundraising)

-- ===============================================
-- ISSUES MODULE
-- ===============================================

-- Issue types enum
CREATE TYPE ia2good_issue_type AS ENUM (
    'environmental',
    'infrastructure',
    'safety',
    'heritage',
    'accessibility',
    'other'
);

-- Issue status enum
CREATE TYPE ia2good_issue_status AS ENUM (
    'reported',
    'verified',
    'in_progress',
    'resolved',
    'rejected'
);

-- Issue severity enum
CREATE TYPE ia2good_issue_severity AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Issues table
CREATE TABLE ia2good_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type ia2good_issue_type NOT NULL,
    status ia2good_issue_status DEFAULT 'reported',
    severity ia2good_issue_severity DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    reported_by UUID NOT NULL,
    volunteer_id UUID,
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    media_urls TEXT[],
    media_types TEXT[],
    views_count INTEGER DEFAULT 0,
    followers_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    tags TEXT[],
    recommended_to TEXT[],
    notified_organizations UUID[],
    notified_authorities TEXT[],
    resolved_by UUID,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    resolution_media TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Issue comments table
CREATE TABLE ia2good_issue_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES ia2good_issues(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    media_urls TEXT[],
    is_official BOOLEAN DEFAULT FALSE,
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Issue followers table
CREATE TABLE ia2good_issue_followers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES ia2good_issues(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    notify_on_update BOOLEAN DEFAULT TRUE,
    notify_on_comment BOOLEAN DEFAULT TRUE,
    notify_on_resolution BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(issue_id, user_id)
);

-- Issues indexes
CREATE INDEX idx_ia2good_issues_type ON ia2good_issues(type);
CREATE INDEX idx_ia2good_issues_status ON ia2good_issues(status);
CREATE INDEX idx_ia2good_issues_severity ON ia2good_issues(severity);
CREATE INDEX idx_ia2good_issues_reported_by ON ia2good_issues(reported_by);
CREATE INDEX idx_ia2good_issues_volunteer_id ON ia2good_issues(volunteer_id);
CREATE INDEX idx_ia2good_issues_location ON ia2good_issues USING GIST(location);
CREATE INDEX idx_ia2good_issues_tags ON ia2good_issues USING GIN(tags);

CREATE INDEX idx_ia2good_issue_comments_issue_id ON ia2good_issue_comments(issue_id);
CREATE INDEX idx_ia2good_issue_comments_user_id ON ia2good_issue_comments(user_id);

CREATE INDEX idx_ia2good_issue_followers_issue_id ON ia2good_issue_followers(issue_id);
CREATE INDEX idx_ia2good_issue_followers_user_id ON ia2good_issue_followers(user_id);


-- ===============================================
-- EVENTS MODULE
-- ===============================================

-- Event types enum
CREATE TYPE ia2good_event_type AS ENUM (
    'cleanup',
    'protest',
    'workshop',
    'fundraiser',
    'awareness',
    'tree_planting',
    'food_distribution',
    'community_gathering',
    'other'
);

-- Event status enum
CREATE TYPE ia2good_event_status AS ENUM (
    'draft',
    'published',
    'ongoing',
    'completed',
    'cancelled'
);

-- Event participant status enum
CREATE TYPE ia2good_event_participant_status AS ENUM (
    'registered',
    'approved',
    'declined',
    'attended',
    'absent'
);

-- Events table
CREATE TABLE ia2good_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type ia2good_event_type NOT NULL,
    status ia2good_event_status DEFAULT 'draft',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    objectives TEXT,
    organizer_id UUID NOT NULL,
    co_organizers UUID[],
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    venue_name VARCHAR(200),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    registration_deadline TIMESTAMP,
    capacity INTEGER,
    participants_count INTEGER DEFAULT 0,
    checked_in_count INTEGER DEFAULT 0,
    min_participants INTEGER,
    cover_image VARCHAR(500),
    images TEXT[],
    videos TEXT[],
    photos_after TEXT[],
    required_skills TEXT[],
    age_minimum INTEGER,
    equipment_needed TEXT[],
    attendance_count INTEGER DEFAULT 0,
    impact_summary TEXT,
    impact_metrics JSONB DEFAULT '{}',
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP
);

-- Event participants table
CREATE TABLE ia2good_event_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES ia2good_events(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    status ia2good_event_participant_status DEFAULT 'registered',
    role VARCHAR(50) DEFAULT 'participant',
    tasks_assigned TEXT[],
    checked_in BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMP,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    registered_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(event_id, user_id)
);

-- Event updates table
CREATE TABLE ia2good_event_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES ia2good_events(id) ON DELETE CASCADE,
    author_id UUID NOT NULL,
    title VARCHAR(200),
    content TEXT NOT NULL,
    media_urls TEXT[],
    update_type VARCHAR(50) DEFAULT 'general',
    notify_participants BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Events indexes
CREATE INDEX idx_ia2good_events_type ON ia2good_events(type);
CREATE INDEX idx_ia2good_events_status ON ia2good_events(status);
CREATE INDEX idx_ia2good_events_organizer_id ON ia2good_events(organizer_id);
CREATE INDEX idx_ia2good_events_start_date ON ia2good_events(start_date);
CREATE INDEX idx_ia2good_events_location ON ia2good_events USING GIST(location);
CREATE INDEX idx_ia2good_events_tags ON ia2good_events USING GIN(tags);

CREATE INDEX idx_ia2good_event_participants_event_id ON ia2good_event_participants(event_id);
CREATE INDEX idx_ia2good_event_participants_user_id ON ia2good_event_participants(user_id);
CREATE INDEX idx_ia2good_event_participants_status ON ia2good_event_participants(status);

CREATE INDEX idx_ia2good_event_updates_event_id ON ia2good_event_updates(event_id);


-- ===============================================
-- CAMPAIGNS MODULE
-- ===============================================

-- Campaign types enum
CREATE TYPE ia2good_campaign_type AS ENUM (
    'petition',
    'fundraising'
);

-- Campaign status enum
CREATE TYPE ia2good_campaign_status AS ENUM (
    'draft',
    'active',
    'successful',
    'closed',
    'cancelled'
);

-- Campaigns table
CREATE TABLE ia2good_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type ia2good_campaign_type NOT NULL,
    status ia2good_campaign_status DEFAULT 'draft',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    story TEXT,
    objectives TEXT,
    tags TEXT[],
    creator_id UUID NOT NULL,
    creator_type VARCHAR(50),
    organization_name VARCHAR(200),
    goal DOUBLE PRECISION NOT NULL,
    current_amount DOUBLE PRECISION DEFAULT 0,
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP,
    cover_image VARCHAR(500),
    images TEXT[],
    videos TEXT[],
    -- For fundraising
    beneficiary_name VARCHAR(200),
    beneficiary_details TEXT,
    funds_usage_plan TEXT,
    transparency_reports JSONB DEFAULT '[]',
    -- For petition
    target_authority VARCHAR(200),
    target_email VARCHAR(255),
    petition_text TEXT,
    -- Engagement
    supporters_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    -- Results
    success_story TEXT,
    impact_achieved TEXT,
    -- Metadata
    metadata JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    closed_at TIMESTAMP
);

-- Signatures table (for petitions)
CREATE TABLE ia2good_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES ia2good_campaigns(id) ON DELETE CASCADE,
    user_id UUID,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(50),
    message TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    verified_at TIMESTAMP,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Donations table (for fundraising)
CREATE TABLE ia2good_donations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES ia2good_campaigns(id) ON DELETE CASCADE,
    user_id UUID,
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    donor_name VARCHAR(200),
    donor_email VARCHAR(255),
    message TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_id VARCHAR(200),
    payment_metadata JSONB DEFAULT '{}',
    tax_receipt_requested BOOLEAN DEFAULT FALSE,
    tax_receipt_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Campaign updates table
CREATE TABLE ia2good_campaign_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES ia2good_campaigns(id) ON DELETE CASCADE,
    author_id UUID NOT NULL,
    title VARCHAR(200),
    content TEXT NOT NULL,
    media_urls TEXT[],
    update_type VARCHAR(50) DEFAULT 'general',
    funds_used DOUBLE PRECISION,
    funds_usage_details TEXT,
    receipts TEXT[],
    notify_supporters BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaigns indexes
CREATE INDEX idx_ia2good_campaigns_type ON ia2good_campaigns(type);
CREATE INDEX idx_ia2good_campaigns_status ON ia2good_campaigns(status);
CREATE INDEX idx_ia2good_campaigns_creator_id ON ia2good_campaigns(creator_id);
CREATE INDEX idx_ia2good_campaigns_tags ON ia2good_campaigns USING GIN(tags);

CREATE INDEX idx_ia2good_signatures_campaign_id ON ia2good_signatures(campaign_id);
CREATE INDEX idx_ia2good_signatures_user_id ON ia2good_signatures(user_id);
CREATE INDEX idx_ia2good_signatures_email ON ia2good_signatures(email);

CREATE INDEX idx_ia2good_donations_campaign_id ON ia2good_donations(campaign_id);
CREATE INDEX idx_ia2good_donations_user_id ON ia2good_donations(user_id);
CREATE INDEX idx_ia2good_donations_payment_status ON ia2good_donations(payment_status);

CREATE INDEX idx_ia2good_campaign_updates_campaign_id ON ia2good_campaign_updates(campaign_id);


-- ===============================================
-- COMMENTS
-- ===============================================

-- This migration adds tables for:
-- 1. Issues: Citizen signalements with geolocation, media, recommendations
-- 2. Events: Collective actions with capacity, check-in, and impact tracking
-- 3. Campaigns: Petitions and fundraising with signatures, donations, transparency

-- Total new tables: 12
-- - ia2good_issues, ia2good_issue_comments, ia2good_issue_followers
-- - ia2good_events, ia2good_event_participants, ia2good_event_updates
-- - ia2good_campaigns, ia2good_signatures, ia2good_donations, ia2good_campaign_updates

-- All tables include proper indexes for performance
-- PostGIS GIST indexes for geospatial queries
-- GIN indexes for array columns (tags, media)
-- B-tree indexes for foreign keys and common filters
