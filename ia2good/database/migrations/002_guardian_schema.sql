-- Guardian-Agent Module Database Schema
-- Migration: 002_guardian_schema
-- Created: 2025-01-XX
-- Description: Tables pour le module Guardian (Protection & Accessibilité)

-- ============================================================================
-- TABLE: guardian_profiles (Profils Accessibilité)
-- ============================================================================
CREATE TABLE guardian_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE, -- References users(id) from main system
    
    -- Hearing & Accessibility Settings
    hearing_level VARCHAR(20) NOT NULL CHECK (hearing_level IN ('deaf', 'hard_of_hearing', 'cochlear_implant')),
    preferred_communication VARCHAR(20)[] DEFAULT ARRAY['visual', 'text']::VARCHAR[],
    
    -- Alert Preferences
    haptic_feedback BOOLEAN DEFAULT true,
    visual_alerts BOOLEAN DEFAULT true,
    audio_alerts BOOLEAN DEFAULT false,
    
    -- SOS Configuration
    auto_sos BOOLEAN DEFAULT true,
    sos_countdown INTEGER DEFAULT 10 CHECK (sos_countdown BETWEEN 5 AND 30),
    emergency_contacts JSONB DEFAULT '[]'::JSONB,  -- [{name, phone, email, relationship}]
    
    -- Medical & Accessibility Info
    medical_info TEXT,
    accessibility_needs TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for guardian_profiles
CREATE INDEX idx_guardian_profiles_user ON guardian_profiles(user_id);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_guardian_profiles_updated_at
    BEFORE UPDATE ON guardian_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: guardian_sos_alerts (Alertes SOS)
-- ============================================================================
CREATE TABLE guardian_sos_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Location Information
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    
    -- Alert Details
    trigger_type VARCHAR(20) NOT NULL CHECK (trigger_type IN ('manual', 'fall_detection', 'panic_button', 'auto')),
    status VARCHAR(20) DEFAULT 'triggered' CHECK (status IN ('triggered', 'countdown', 'dispatched', 'cancelled', 'resolved')),
    
    -- Timing
    countdown_seconds INTEGER,
    dispatched_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    resolved_at TIMESTAMP,
    response_time INTERVAL,
    
    -- Contacts Notified
    contacts_notified JSONB DEFAULT '[]'::JSONB,  -- [{contact_id, name, notified_at, method}]
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for guardian_sos_alerts
CREATE INDEX idx_guardian_sos_user ON guardian_sos_alerts(user_id);
CREATE INDEX idx_guardian_sos_status ON guardian_sos_alerts(status);
CREATE INDEX idx_guardian_sos_created ON guardian_sos_alerts(created_at DESC);
CREATE INDEX idx_guardian_sos_location ON guardian_sos_alerts USING GIST(location);

-- ============================================================================
-- TABLE: guardian_hazard_detections (Détections Dangers)
-- ============================================================================
CREATE TABLE guardian_hazard_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- References users(id) from main system (NULL for anonymous)
    
    -- Hazard Information
    hazard_type VARCHAR(50) NOT NULL,  -- vehicle_horn, siren, alarm, dog_bark, breaking_glass, scream, door_knock, phone_ring
    confidence FLOAT NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    
    -- Location
    location GEOGRAPHY(POINT, 4326),
    
    -- Audio Sample
    audio_sample_url TEXT,
    
    -- User Feedback (for ML improvement)
    user_feedback VARCHAR(20) CHECK (user_feedback IN ('correct', 'false_positive', 'missed', 'too_sensitive')),
    feedback_comment TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for guardian_hazard_detections
CREATE INDEX idx_guardian_hazards_user ON guardian_hazard_detections(user_id);
CREATE INDEX idx_guardian_hazards_type ON guardian_hazard_detections(hazard_type);
CREATE INDEX idx_guardian_hazards_created ON guardian_hazard_detections(created_at DESC);
CREATE INDEX idx_guardian_hazards_confidence ON guardian_hazard_detections(confidence DESC);

-- ============================================================================
-- TABLE: guardian_communication_log (Historique Communications)
-- ============================================================================
CREATE TABLE guardian_communication_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Communication Type
    type VARCHAR(20) NOT NULL CHECK (type IN ('speech_to_text', 'text_to_speech', 'translation')),
    
    -- Content
    input_text TEXT,
    output_text TEXT,
    
    -- Language
    language_from VARCHAR(10),
    language_to VARCHAR(10),
    
    -- Quality Metrics
    duration_ms INTEGER,
    quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 1),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for guardian_communication_log
CREATE INDEX idx_guardian_comm_user ON guardian_communication_log(user_id);
CREATE INDEX idx_guardian_comm_type ON guardian_communication_log(type);
CREATE INDEX idx_guardian_comm_created ON guardian_communication_log(created_at DESC);

-- ============================================================================
-- TABLE: guardian_emergency_contacts (Contacts d'Urgence)
-- ============================================================================
CREATE TABLE guardian_emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Contact Information
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50),  -- family, friend, caregiver, medical, etc.
    
    -- Contact Methods
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    
    -- Priority & Settings
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),  -- 1 = highest priority
    notify_via_sms BOOLEAN DEFAULT true,
    notify_via_call BOOLEAN DEFAULT false,
    notify_via_email BOOLEAN DEFAULT false,
    
    -- Status
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for guardian_emergency_contacts
CREATE INDEX idx_guardian_contacts_user ON guardian_emergency_contacts(user_id);
CREATE INDEX idx_guardian_contacts_priority ON guardian_emergency_contacts(priority ASC);
CREATE INDEX idx_guardian_contacts_active ON guardian_emergency_contacts(is_active) WHERE is_active = true;

-- Trigger for auto-update updated_at
CREATE TRIGGER update_guardian_contacts_updated_at
    BEFORE UPDATE ON guardian_emergency_contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: guardian_hazard_feedback_aggregates (Agrégats Feedback ML)
-- ============================================================================
CREATE TABLE guardian_hazard_feedback_aggregates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hazard_type VARCHAR(50) NOT NULL,
    
    -- Aggregate Statistics
    total_detections INTEGER DEFAULT 0,
    correct_detections INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    missed_detections INTEGER DEFAULT 0,
    
    -- Calculated Metrics
    accuracy_rate FLOAT,
    false_positive_rate FLOAT,
    
    -- Model Version
    model_version VARCHAR(20),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(hazard_type, period_start, period_end, model_version)
);

-- Indexes for guardian_hazard_feedback_aggregates
CREATE INDEX idx_guardian_feedback_agg_type ON guardian_hazard_feedback_aggregates(hazard_type);
CREATE INDEX idx_guardian_feedback_agg_period ON guardian_hazard_feedback_aggregates(period_start, period_end);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_guardian_feedback_agg_updated_at
    BEFORE UPDATE ON guardian_hazard_feedback_aggregates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments for Documentation
-- ============================================================================
COMMENT ON TABLE guardian_profiles IS 'Profils utilisateurs pour les fonctionnalités d''accessibilité Guardian';
COMMENT ON TABLE guardian_sos_alerts IS 'Historique des alertes SOS déclenchées par les utilisateurs';
COMMENT ON TABLE guardian_hazard_detections IS 'Détections de dangers audio en temps réel';
COMMENT ON TABLE guardian_communication_log IS 'Historique des communications Speech-to-Text et Text-to-Speech';
COMMENT ON TABLE guardian_emergency_contacts IS 'Contacts d''urgence configurés par les utilisateurs';
COMMENT ON TABLE guardian_hazard_feedback_aggregates IS 'Métriques agrégées pour amélioration des modèles ML';
