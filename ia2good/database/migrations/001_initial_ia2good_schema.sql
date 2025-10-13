-- IA2GOOD Module Database Schema
-- Migration: 001_initial_schema
-- Created: 2025-01-XX

-- Enable PostGIS extension for geolocation
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- TABLE: ia2good_cases (Humanitarian Cases)
-- ============================================================================
CREATE TABLE ia2good_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Will reference users(id) from main system
    
    -- Case information
    type VARCHAR(20) NOT NULL CHECK (type IN ('homeless', 'animal', 'emergency', 'other')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'claimed', 'in_progress', 'completed', 'cancelled')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Geolocation
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(50) DEFAULT 'France',
    
    -- Urgency & AI Classification
    urgency_level INTEGER CHECK (urgency_level BETWEEN 1 AND 10),
    ai_classification JSONB DEFAULT '{}',  -- {type, confidence, entities, keywords}
    tags VARCHAR(50)[],
    
    -- Media
    photos TEXT[],  -- URLs to photos
    main_photo TEXT,
    
    -- Metadata
    views_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    volunteers_needed INTEGER DEFAULT 1,
    volunteers_assigned INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Full-text search
    search_vector tsvector
);

-- Indexes for ia2good_cases
CREATE INDEX idx_ia2good_cases_user_id ON ia2good_cases(user_id);
CREATE INDEX idx_ia2good_cases_type ON ia2good_cases(type);
CREATE INDEX idx_ia2good_cases_status ON ia2good_cases(status);
CREATE INDEX idx_ia2good_cases_urgency ON ia2good_cases(urgency_level DESC);
CREATE INDEX idx_ia2good_cases_created ON ia2good_cases(created_at DESC);
CREATE INDEX idx_ia2good_cases_location ON ia2good_cases USING GIST(location);
CREATE INDEX idx_ia2good_cases_search ON ia2good_cases USING GIN(search_vector);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_ia2good_cases_updated_at
    BEFORE UPDATE ON ia2good_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for search vector
CREATE TRIGGER tsvector_update_ia2good_cases
    BEFORE INSERT OR UPDATE ON ia2good_cases
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_catalog.french', title, description);

-- ============================================================================
-- TABLE: ia2good_volunteer_profiles (Volunteer Profiles)
-- ============================================================================
CREATE TABLE ia2good_volunteer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE, -- Will reference users(id) from main system
    
    -- Location
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(50) DEFAULT 'France',
    
    -- Skills & Availability
    skills VARCHAR(50)[] DEFAULT '{}',  -- medical, transport, shelter, food, legal, psychological
    languages VARCHAR(10)[] DEFAULT '{"fr"}',
    certifications JSONB DEFAULT '{}',  -- {first_aid: true, driver_license: true}
    
    -- Availability
    availability_status BOOLEAN DEFAULT true,
    availability_schedule JSONB DEFAULT '{}',  -- {monday: {start: "09:00", end: "18:00"}}
    max_distance_km INTEGER DEFAULT 10,
    
    -- Verification
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    verified_at TIMESTAMP,
    verified_by UUID, -- References users(id)
    identity_verified BOOLEAN DEFAULT false,
    background_check BOOLEAN DEFAULT false,
    
    -- Statistics
    total_cases_completed INTEGER DEFAULT 0,
    total_hours_volunteered INTEGER DEFAULT 0,
    reliability_score FLOAT DEFAULT 100.0 CHECK (reliability_score BETWEEN 0 AND 100),
    average_rating FLOAT,
    total_ratings INTEGER DEFAULT 0,
    
    -- Preferences
    notification_radius_km INTEGER DEFAULT 5,
    preferred_case_types VARCHAR(20)[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

-- Indexes for ia2good_volunteer_profiles
CREATE INDEX idx_ia2good_volunteers_user_id ON ia2good_volunteer_profiles(user_id);
CREATE INDEX idx_ia2good_volunteers_status ON ia2good_volunteer_profiles(availability_status);
CREATE INDEX idx_ia2good_volunteers_location ON ia2good_volunteer_profiles USING GIST(location);
CREATE INDEX idx_ia2good_volunteers_skills ON ia2good_volunteer_profiles USING GIN(skills);
CREATE INDEX idx_ia2good_volunteers_verification ON ia2good_volunteer_profiles(verification_status);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_ia2good_volunteers_updated_at
    BEFORE UPDATE ON ia2good_volunteer_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: ia2good_case_assignments (Case Assignments)
-- ============================================================================
CREATE TABLE ia2good_case_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES ia2good_cases(id) ON DELETE CASCADE,
    volunteer_id UUID NOT NULL REFERENCES ia2good_volunteer_profiles(id) ON DELETE CASCADE,
    
    -- Assignment status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'in_progress', 'completed', 'cancelled')),
    
    -- Matching
    match_score FLOAT,  -- Score matching 0-100
    match_reasons JSONB DEFAULT '{}',  -- Reasons for this volunteer
    
    -- Timestamps
    assigned_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Response time
    response_time_minutes INTEGER,
    completion_time_minutes INTEGER,
    
    -- Feedback
    completion_notes TEXT,
    volunteer_rating INTEGER CHECK (volunteer_rating BETWEEN 1 AND 5),
    volunteer_feedback TEXT,
    reporter_rating INTEGER CHECK (reporter_rating BETWEEN 1 AND 5),
    reporter_feedback TEXT,
    
    UNIQUE(case_id, volunteer_id)
);

-- Indexes for ia2good_case_assignments
CREATE INDEX idx_ia2good_assignments_case ON ia2good_case_assignments(case_id);
CREATE INDEX idx_ia2good_assignments_volunteer ON ia2good_case_assignments(volunteer_id);
CREATE INDEX idx_ia2good_assignments_status ON ia2good_case_assignments(status);
CREATE INDEX idx_ia2good_assignments_assigned ON ia2good_case_assignments(assigned_at DESC);

-- ============================================================================
-- TABLE: ia2good_activity_log (Activity Log)
-- ============================================================================
CREATE TABLE ia2good_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES ia2good_cases(id) ON DELETE CASCADE,
    user_id UUID, -- References users(id)
    volunteer_id UUID REFERENCES ia2good_volunteer_profiles(id) ON DELETE SET NULL,
    
    -- Activity details
    activity_type VARCHAR(50) NOT NULL,  -- case_created, case_updated, volunteer_assigned, case_completed
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for ia2good_activity_log
CREATE INDEX idx_ia2good_activity_case ON ia2good_activity_log(case_id);
CREATE INDEX idx_ia2good_activity_user ON ia2good_activity_log(user_id);
CREATE INDEX idx_ia2good_activity_created ON ia2good_activity_log(created_at DESC);

-- ============================================================================
-- TABLE: ia2good_achievements (Gamification Achievements)
-- ============================================================================
CREATE TABLE ia2good_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT,
    category VARCHAR(50),  -- milestone, streak, special
    criteria JSONB NOT NULL,  -- Conditions to unlock
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20) DEFAULT 'common' CHECK (rarity IN ('common', 'rare', 'epic', 'legendary')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABLE: ia2good_user_achievements (User Achievement Unlocks)
-- ============================================================================
CREATE TABLE ia2good_user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id)
    achievement_id UUID NOT NULL REFERENCES ia2good_achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    progress INTEGER DEFAULT 100,
    UNIQUE(user_id, achievement_id)
);

-- ============================================================================
-- SEED DATA: Achievements
-- ============================================================================
INSERT INTO ia2good_achievements (code, name, description, criteria, points, rarity) VALUES
('first_case', 'Premier Cas', 'Complétez votre premier cas', '{"cases_completed": 1}'::jsonb, 10, 'common'),
('helping_hand', 'Main Tendue', 'Aidez 10 personnes', '{"cases_completed": 10}'::jsonb, 50, 'rare'),
('guardian_angel', 'Ange Gardien', 'Aidez 50 personnes', '{"cases_completed": 50}'::jsonb, 250, 'epic'),
('night_owl', 'Oiseau de Nuit', 'Complétez un cas après 22h', '{"night_help": true}'::jsonb, 20, 'rare'),
('fast_responder', 'Réponse Éclair', 'Répondez en moins de 10 minutes', '{"response_time_max": 10}'::jsonb, 30, 'rare'),
('team_player', 'Esprit d''Équipe', 'Participez à 5 missions en équipe', '{"team_missions": 5}'::jsonb, 40, 'rare');

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Active cases with volunteer details
CREATE VIEW v_active_cases_with_volunteers AS
SELECT 
    c.*,
    COUNT(DISTINCT a.volunteer_id) as volunteers_count,
    AVG(a.match_score) as avg_match_score,
    MIN(a.assigned_at) as first_assignment_at
FROM ia2good_cases c
LEFT JOIN ia2good_case_assignments a ON c.id = a.case_id
WHERE c.status IN ('open', 'claimed', 'in_progress')
    AND c.deleted_at IS NULL
GROUP BY c.id;

-- View: Volunteer statistics
CREATE VIEW v_volunteer_statistics AS
SELECT 
    vp.id,
    vp.user_id,
    vp.location,
    vp.city,
    vp.skills,
    vp.availability_status,
    vp.reliability_score,
    vp.total_cases_completed,
    vp.total_hours_volunteered,
    vp.average_rating,
    COUNT(DISTINCT a.case_id) as active_assignments,
    MAX(a.assigned_at) as last_assignment_date
FROM ia2good_volunteer_profiles vp
LEFT JOIN ia2good_case_assignments a ON vp.id = a.volunteer_id 
    AND a.status IN ('pending', 'accepted', 'in_progress')
WHERE vp.verification_status = 'verified'
GROUP BY vp.id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE ia2good_cases IS 'Humanitarian cases (homeless, animal rescue, emergencies)';
COMMENT ON TABLE ia2good_volunteer_profiles IS 'Volunteer profiles with skills and availability';
COMMENT ON TABLE ia2good_case_assignments IS 'Case assignments to volunteers with status tracking';
COMMENT ON TABLE ia2good_activity_log IS 'Activity log for cases and volunteers';
COMMENT ON TABLE ia2good_achievements IS 'Gamification achievements';
COMMENT ON TABLE ia2good_user_achievements IS 'User achievement unlocks';
