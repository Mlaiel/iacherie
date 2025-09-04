-- ============================================================================
-- PostgreSQL Migration: 004_gamification.sql
-- Gamification System for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration creates comprehensive gamification system tables
-- supporting achievements, badges, levels, leaderboards, challenges,
-- and reward systems to enhance user engagement and motivation.
-- ============================================================================

-- ============================================================================
-- USER LEVELS TABLE
-- ============================================================================

-- User progression and experience levels
CREATE TABLE IF NOT EXISTS user_levels (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Level information
    current_level INTEGER DEFAULT 1 CHECK (current_level >= 1),
    current_xp BIGINT DEFAULT 0 CHECK (current_xp >= 0),
    total_xp BIGINT DEFAULT 0 CHECK (total_xp >= 0),
    
    -- Level categories for different activities
    content_creation_level INTEGER DEFAULT 1,
    content_creation_xp BIGINT DEFAULT 0,
    
    collaboration_level INTEGER DEFAULT 1,
    collaboration_xp BIGINT DEFAULT 0,
    
    community_level INTEGER DEFAULT 1,
    community_xp BIGINT DEFAULT 0,
    
    technical_level INTEGER DEFAULT 1,
    technical_xp BIGINT DEFAULT 0,
    
    business_level INTEGER DEFAULT 1,
    business_xp BIGINT DEFAULT 0,
    
    -- Level progression tracking
    last_level_up TIMESTAMP WITH TIME ZONE,
    next_level_xp BIGINT,
    
    -- Streaks and consistency
    daily_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    weekly_streak INTEGER DEFAULT 0,
    monthly_streak INTEGER DEFAULT 0,
    
    -- Special status and titles
    title VARCHAR(100),
    special_status VARCHAR(50),
    prestige_level INTEGER DEFAULT 0,
    
    -- Statistics
    level_ups_total INTEGER DEFAULT 0,
    days_active INTEGER DEFAULT 0,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id)
);

-- ============================================================================
-- ACHIEVEMENTS TABLE
-- ============================================================================

-- Achievement definitions and metadata
CREATE TABLE IF NOT EXISTS achievements (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Achievement information
    name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN ('content_creation', 'collaboration', 'community', 'technical', 'business', 'social', 'milestone', 'special')),
    
    -- Achievement type and rarity
    achievement_type VARCHAR(50) NOT NULL CHECK (achievement_type IN ('milestone', 'progressive', 'challenge', 'streak', 'social', 'special_event', 'hidden')),
    rarity VARCHAR(20) DEFAULT 'common' CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic')),
    
    -- Visual and branding
    icon_url VARCHAR(500),
    badge_color VARCHAR(7), -- Hex color
    badge_design JSONB DEFAULT '{}',
    
    -- Requirements and conditions
    requirements JSONB NOT NULL,
    conditions TEXT,
    prerequisite_achievements UUID[] DEFAULT '{}',
    
    -- Rewards
    xp_reward INTEGER DEFAULT 0,
    badge_reward BOOLEAN DEFAULT TRUE,
    title_reward VARCHAR(100),
    other_rewards JSONB DEFAULT '{}',
    
    -- Achievement properties
    is_hidden BOOLEAN DEFAULT FALSE,
    is_repeatable BOOLEAN DEFAULT FALSE,
    max_completions INTEGER DEFAULT 1,
    difficulty_score INTEGER DEFAULT 1 CHECK (difficulty_score >= 1 AND difficulty_score <= 10),
    
    -- Statistics
    total_completions INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Status and lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    release_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deprecation_date TIMESTAMP WITH TIME ZONE,
    
    -- Achievement metadata
    achievement_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER ACHIEVEMENTS TABLE
-- ============================================================================

-- User achievement completions
CREATE TABLE IF NOT EXISTS user_achievements (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    
    -- Completion information
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completion_count INTEGER DEFAULT 1,
    
    -- Progress tracking
    progress_data JSONB DEFAULT '{}',
    progress_percentage DECIMAL(5,2) DEFAULT 100.00,
    
    -- Context and metadata
    completion_context JSONB DEFAULT '{}',
    triggered_by VARCHAR(200), -- Action or event that triggered completion
    
    -- Validation and verification
    validated BOOLEAN DEFAULT TRUE,
    validation_data JSONB DEFAULT '{}',
    
    -- Rewards claimed
    rewards_claimed BOOLEAN DEFAULT FALSE,
    rewards_claimed_at TIMESTAMP WITH TIME ZONE,
    
    -- Display and sharing
    is_showcased BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, achievement_id, completed_at) -- Allow multiple completions with different timestamps
);

-- ============================================================================
-- BADGES TABLE
-- ============================================================================

-- Badge definitions and designs
CREATE TABLE IF NOT EXISTS badges (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Badge information
    name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    
    -- Visual design
    icon_url VARCHAR(500),
    background_color VARCHAR(7),
    border_color VARCHAR(7),
    text_color VARCHAR(7),
    badge_shape VARCHAR(50) DEFAULT 'circle' CHECK (badge_shape IN ('circle', 'square', 'shield', 'star', 'hexagon', 'custom')),
    
    -- Badge properties
    rarity VARCHAR(20) DEFAULT 'common' CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic')),
    is_stackable BOOLEAN DEFAULT FALSE,
    max_stack INTEGER DEFAULT 1,
    
    -- Requirements
    requirements JSONB NOT NULL,
    is_automatic BOOLEAN DEFAULT TRUE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_limited_time BOOLEAN DEFAULT FALSE,
    expiry_date TIMESTAMP WITH TIME ZONE,
    
    -- Statistics
    total_awarded INTEGER DEFAULT 0,
    
    -- Badge metadata
    badge_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER BADGES TABLE
-- ============================================================================

-- User badge awards
CREATE TABLE IF NOT EXISTS user_badges (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    
    -- Award information
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    awarded_by UUID REFERENCES users_enhanced(id), -- NULL for automatic awards
    award_reason TEXT,
    
    -- Badge properties
    stack_count INTEGER DEFAULT 1,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    
    -- Context and metadata
    award_context JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_visible BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CHALLENGES TABLE
-- ============================================================================

-- Time-limited challenges and events
CREATE TABLE IF NOT EXISTS challenges (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Challenge information
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    short_description VARCHAR(500),
    
    -- Challenge type and category
    challenge_type VARCHAR(50) NOT NULL CHECK (challenge_type IN ('daily', 'weekly', 'monthly', 'seasonal', 'special_event', 'community', 'personal')),
    category VARCHAR(100) NOT NULL,
    
    -- Visual and branding
    banner_image_url VARCHAR(500),
    icon_url VARCHAR(500),
    theme_colors JSONB DEFAULT '{}',
    
    -- Timeline
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_deadline TIMESTAMP WITH TIME ZONE,
    
    -- Requirements and goals
    requirements JSONB NOT NULL,
    goals JSONB NOT NULL,
    participation_criteria JSONB DEFAULT '{}',
    
    -- Rewards
    completion_rewards JSONB DEFAULT '{}',
    milestone_rewards JSONB DEFAULT '[]',
    leaderboard_rewards JSONB DEFAULT '{}',
    
    -- Challenge properties
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 10),
    max_participants INTEGER,
    is_team_challenge BOOLEAN DEFAULT FALSE,
    requires_registration BOOLEAN DEFAULT FALSE,
    
    -- Status and statistics
    status VARCHAR(30) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'completed', 'cancelled')),
    participant_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    
    -- Challenge metadata
    challenge_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER CHALLENGE PARTICIPATION TABLE
-- ============================================================================

-- User participation in challenges
CREATE TABLE IF NOT EXISTS user_challenge_participation (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    
    -- Participation information
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Progress tracking
    progress_data JSONB DEFAULT '{}',
    current_score INTEGER DEFAULT 0,
    best_score INTEGER DEFAULT 0,
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    
    -- Team information (for team challenges)
    team_id UUID,
    team_role VARCHAR(50),
    
    -- Status
    participation_status VARCHAR(30) DEFAULT 'registered' CHECK (participation_status IN ('registered', 'active', 'completed', 'abandoned', 'disqualified')),
    
    -- Results and ranking
    final_rank INTEGER,
    final_score INTEGER,
    achievements_earned UUID[] DEFAULT '{}',
    rewards_earned JSONB DEFAULT '{}',
    
    -- Participation metadata
    participation_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, challenge_id)
);

-- ============================================================================
-- LEADERBOARDS TABLE
-- ============================================================================

-- Leaderboard definitions
CREATE TABLE IF NOT EXISTS leaderboards (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Leaderboard information
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    
    -- Leaderboard type and scope
    leaderboard_type VARCHAR(50) NOT NULL CHECK (leaderboard_type IN ('global', 'regional', 'tier_based', 'category', 'challenge', 'seasonal')),
    scoring_method VARCHAR(50) NOT NULL CHECK (scoring_method IN ('total_points', 'average_rating', 'content_count', 'collaboration_count', 'revenue', 'custom')),
    
    -- Time period
    time_period VARCHAR(30) NOT NULL CHECK (time_period IN ('all_time', 'monthly', 'weekly', 'daily', 'custom')),
    reset_frequency VARCHAR(30) DEFAULT 'never' CHECK (reset_frequency IN ('never', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    
    -- Filtering and criteria
    filter_criteria JSONB DEFAULT '{}',
    minimum_requirements JSONB DEFAULT '{}',
    
    -- Display properties
    max_displayed_users INTEGER DEFAULT 100,
    update_frequency INTEGER DEFAULT 3600, -- seconds
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Leaderboard metadata
    leaderboard_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LEADERBOARD ENTRIES TABLE
-- ============================================================================

-- Current leaderboard rankings
CREATE TABLE IF NOT EXISTS leaderboard_entries (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    leaderboard_id UUID NOT NULL REFERENCES leaderboards(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Ranking information
    current_rank INTEGER NOT NULL,
    previous_rank INTEGER,
    rank_change INTEGER DEFAULT 0,
    
    -- Scoring
    current_score DECIMAL(15,4) NOT NULL,
    previous_score DECIMAL(15,4),
    score_change DECIMAL(15,4) DEFAULT 0,
    
    -- Additional metrics
    additional_metrics JSONB DEFAULT '{}',
    
    -- Context
    calculation_period_start TIMESTAMP WITH TIME ZONE,
    calculation_period_end TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    last_calculated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(leaderboard_id, user_id)
);

-- ============================================================================
-- REWARDS TABLE
-- ============================================================================

-- Reward definitions and configurations
CREATE TABLE IF NOT EXISTS rewards (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Reward information
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    reward_type VARCHAR(50) NOT NULL CHECK (reward_type IN ('xp', 'badge', 'title', 'currency', 'premium_time', 'feature_unlock', 'physical', 'discount', 'custom')),
    
    -- Reward value and properties
    reward_value JSONB NOT NULL,
    reward_properties JSONB DEFAULT '{}',
    
    -- Visual representation
    icon_url VARCHAR(500),
    image_url VARCHAR(500),
    
    -- Availability and limitations
    is_claimable BOOLEAN DEFAULT TRUE,
    claim_limit INTEGER, -- NULL for unlimited
    claim_period VARCHAR(30), -- 'once', 'daily', 'weekly', 'monthly'
    expiry_period INTERVAL,
    
    -- Requirements
    requirements JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Reward metadata
    reward_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER REWARDS TABLE
-- ============================================================================

-- User reward claims and history
CREATE TABLE IF NOT EXISTS user_rewards (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    reward_id UUID NOT NULL REFERENCES rewards(id) ON DELETE CASCADE,
    
    -- Claim information
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Reward context
    earned_from VARCHAR(200), -- Achievement, challenge, etc.
    earned_from_id UUID,
    claim_reason TEXT,
    
    -- Status
    claim_status VARCHAR(30) DEFAULT 'claimed' CHECK (claim_status IN ('pending', 'claimed', 'expired', 'revoked')),
    used_at TIMESTAMP WITH TIME ZONE,
    
    -- Claim metadata
    claim_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EXPERIENCE ACTIONS TABLE
-- ============================================================================

-- Define XP-earning actions
CREATE TABLE IF NOT EXISTS experience_actions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Action information
    action_name VARCHAR(100) NOT NULL UNIQUE,
    action_description TEXT,
    category VARCHAR(100) NOT NULL,
    
    -- XP rewards
    base_xp INTEGER NOT NULL DEFAULT 0,
    bonus_multiplier DECIMAL(4,2) DEFAULT 1.00,
    daily_limit INTEGER, -- NULL for unlimited
    
    -- Action properties
    is_repeatable BOOLEAN DEFAULT TRUE,
    cooldown_minutes INTEGER DEFAULT 0,
    requires_validation BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Action metadata
    action_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER EXPERIENCE LOG TABLE
-- ============================================================================

-- Log of user XP gains
CREATE TABLE IF NOT EXISTS user_experience_log (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Experience gain information
    action_name VARCHAR(100) NOT NULL,
    xp_gained INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,
    
    -- Context
    source_type VARCHAR(50), -- 'content_upload', 'collaboration', etc.
    source_id UUID,
    bonus_multiplier DECIMAL(4,2) DEFAULT 1.00,
    bonus_reason VARCHAR(200),
    
    -- Validation
    validated BOOLEAN DEFAULT TRUE,
    validated_by UUID REFERENCES users_enhanced(id),
    validation_notes TEXT,
    
    -- Log metadata
    log_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamp
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- User levels indexes
CREATE INDEX idx_user_levels_user_id ON user_levels(user_id);
CREATE INDEX idx_user_levels_current_level ON user_levels(current_level);
CREATE INDEX idx_user_levels_total_xp ON user_levels(total_xp);
CREATE INDEX idx_user_levels_streak ON user_levels(daily_streak);

-- Achievement indexes
CREATE INDEX idx_achievements_category ON achievements(category);
CREATE INDEX idx_achievements_type ON achievements(achievement_type);
CREATE INDEX idx_achievements_rarity ON achievements(rarity);
CREATE INDEX idx_achievements_active ON achievements(is_active);

-- User achievement indexes
CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement_id ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_completed_at ON user_achievements(completed_at);
CREATE INDEX idx_user_achievements_showcased ON user_achievements(is_showcased);

-- Badge indexes
CREATE INDEX idx_badges_category ON badges(category);
CREATE INDEX idx_badges_rarity ON badges(rarity);
CREATE INDEX idx_badges_active ON badges(is_active);

-- User badge indexes
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_user_badges_badge_id ON user_badges(badge_id);
CREATE INDEX idx_user_badges_featured ON user_badges(is_featured);

-- Challenge indexes
CREATE INDEX idx_challenges_type ON challenges(challenge_type);
CREATE INDEX idx_challenges_category ON challenges(category);
CREATE INDEX idx_challenges_status ON challenges(status);
CREATE INDEX idx_challenges_dates ON challenges(start_date, end_date);

-- Challenge participation indexes
CREATE INDEX idx_user_challenge_participation_user_id ON user_challenge_participation(user_id);
CREATE INDEX idx_user_challenge_participation_challenge_id ON user_challenge_participation(challenge_id);
CREATE INDEX idx_user_challenge_participation_status ON user_challenge_participation(participation_status);

-- Leaderboard indexes
CREATE INDEX idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX idx_leaderboards_category ON leaderboards(category);
CREATE INDEX idx_leaderboards_active ON leaderboards(is_active);

-- Leaderboard entry indexes
CREATE INDEX idx_leaderboard_entries_leaderboard_id ON leaderboard_entries(leaderboard_id);
CREATE INDEX idx_leaderboard_entries_user_id ON leaderboard_entries(user_id);
CREATE INDEX idx_leaderboard_entries_rank ON leaderboard_entries(current_rank);
CREATE INDEX idx_leaderboard_entries_score ON leaderboard_entries(current_score);

-- Experience log indexes
CREATE INDEX idx_user_experience_log_user_id ON user_experience_log(user_id);
CREATE INDEX idx_user_experience_log_earned_at ON user_experience_log(earned_at);
CREATE INDEX idx_user_experience_log_action ON user_experience_log(action_name);
CREATE INDEX idx_user_experience_log_category ON user_experience_log(category);

-- Composite indexes
CREATE INDEX idx_user_achievements_user_showcase ON user_achievements(user_id, is_showcased);
CREATE INDEX idx_leaderboard_entries_board_rank ON leaderboard_entries(leaderboard_id, current_rank);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update user level based on XP gains
CREATE OR REPLACE FUNCTION update_user_level()
RETURNS TRIGGER AS $$
DECLARE
    level_threshold BIGINT;
    new_level INTEGER;
BEGIN
    -- Calculate new level based on total XP
    -- Using a simple formula: level = floor(sqrt(total_xp / 100)) + 1
    new_level := FLOOR(SQRT(NEW.total_xp / 100.0)) + 1;
    
    -- Update level if it changed
    IF new_level > NEW.current_level THEN
        UPDATE user_levels SET
            current_level = new_level,
            last_level_up = NOW(),
            level_ups_total = level_ups_total + (new_level - current_level),
            updated_at = NOW()
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply level update trigger
CREATE TRIGGER update_user_level_trigger
    AFTER UPDATE OF total_xp ON user_levels
    FOR EACH ROW EXECUTE FUNCTION update_user_level();

-- Update achievement completion counts
CREATE OR REPLACE FUNCTION update_achievement_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE achievements SET
        total_completions = total_completions + 1,
        completion_rate = (
            SELECT ROUND(
                (COUNT(*)::DECIMAL / GREATEST((SELECT COUNT(*) FROM users_enhanced), 1)) * 100, 2
            )
            FROM user_achievements ua
            WHERE ua.achievement_id = NEW.achievement_id
        ),
        updated_at = NOW()
    WHERE id = NEW.achievement_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply achievement stats trigger
CREATE TRIGGER update_achievement_stats_trigger
    AFTER INSERT ON user_achievements
    FOR EACH ROW EXECUTE FUNCTION update_achievement_stats();

-- Apply updated_at triggers
CREATE TRIGGER update_user_levels_updated_at 
    BEFORE UPDATE ON user_levels 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_achievements_updated_at 
    BEFORE UPDATE ON achievements 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_achievements_updated_at 
    BEFORE UPDATE ON user_achievements 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_badges_updated_at 
    BEFORE UPDATE ON badges 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_badges_updated_at 
    BEFORE UPDATE ON user_badges 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_challenges_updated_at 
    BEFORE UPDATE ON challenges 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leaderboards_updated_at 
    BEFORE UPDATE ON leaderboards 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- User gamification summary view
CREATE OR REPLACE VIEW user_gamification_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.display_name,
    
    -- Level information
    ul.current_level,
    ul.total_xp,
    ul.daily_streak,
    ul.title,
    
    -- Achievement statistics
    (SELECT COUNT(*) FROM user_achievements ua WHERE ua.user_id = u.id) as total_achievements,
    (SELECT COUNT(*) FROM user_achievements ua 
     JOIN achievements a ON ua.achievement_id = a.id 
     WHERE ua.user_id = u.id AND a.rarity IN ('rare', 'epic', 'legendary')) as rare_achievements,
    
    -- Badge count
    (SELECT COUNT(*) FROM user_badges ub WHERE ub.user_id = u.id AND ub.is_active = true) as total_badges,
    
    -- Challenge participation
    (SELECT COUNT(*) FROM user_challenge_participation ucp 
     WHERE ucp.user_id = u.id AND ucp.participation_status = 'completed') as challenges_completed,
    
    -- Leaderboard positions
    (SELECT COUNT(*) FROM leaderboard_entries le WHERE le.user_id = u.id AND le.current_rank <= 10) as top_10_positions
    
FROM users_enhanced u
LEFT JOIN user_levels ul ON u.id = ul.user_id;

-- Active challenges view
CREATE OR REPLACE VIEW active_challenges AS
SELECT 
    c.*,
    
    -- Participation statistics
    (SELECT COUNT(*) FROM user_challenge_participation ucp 
     WHERE ucp.challenge_id = c.id) as total_participants,
    (SELECT COUNT(*) FROM user_challenge_participation ucp 
     WHERE ucp.challenge_id = c.id AND ucp.participation_status = 'completed') as completions,
    
    -- Time remaining
    EXTRACT(EPOCH FROM (c.end_date - NOW())) as seconds_remaining
    
FROM challenges c
WHERE c.status = 'active' AND c.end_date > NOW();

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to award XP to user
CREATE OR REPLACE FUNCTION award_experience(
    p_user_id UUID,
    p_action_name VARCHAR(100),
    p_category VARCHAR(100),
    p_base_xp INTEGER,
    p_bonus_multiplier DECIMAL(4,2) DEFAULT 1.00,
    p_source_type VARCHAR(50) DEFAULT NULL,
    p_source_id UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    calculated_xp INTEGER;
    current_user_level RECORD;
BEGIN
    -- Calculate final XP
    calculated_xp := ROUND(p_base_xp * p_bonus_multiplier);
    
    -- Log the XP gain
    INSERT INTO user_experience_log (
        user_id, action_name, xp_gained, category, 
        source_type, source_id, bonus_multiplier
    ) VALUES (
        p_user_id, p_action_name, calculated_xp, p_category,
        p_source_type, p_source_id, p_bonus_multiplier
    );
    
    -- Update user levels
    UPDATE user_levels SET
        total_xp = total_xp + calculated_xp,
        current_xp = current_xp + calculated_xp,
        last_activity = NOW(),
        updated_at = NOW()
    WHERE user_id = p_user_id;
    
    -- Create user level record if it doesn't exist
    INSERT INTO user_levels (user_id, total_xp, current_xp)
    VALUES (p_user_id, calculated_xp, calculated_xp)
    ON CONFLICT (user_id) DO NOTHING;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to check and award achievements
CREATE OR REPLACE FUNCTION check_user_achievements(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    achievement_record RECORD;
    achievements_awarded INTEGER := 0;
BEGIN
    -- This is a simplified version - in practice, you'd have more complex logic
    FOR achievement_record IN 
        SELECT * FROM achievements 
        WHERE is_active = true 
        AND id NOT IN (
            SELECT achievement_id FROM user_achievements 
            WHERE user_id = p_user_id
        )
    LOOP
        -- Check achievement requirements (simplified)
        -- In practice, you'd evaluate the requirements JSONB against user data
        
        -- Example: Award achievement for reaching level 10
        IF achievement_record.requirements->>'level' IS NOT NULL THEN
            IF (SELECT current_level FROM user_levels WHERE user_id = p_user_id) >= 
               (achievement_record.requirements->>'level')::INTEGER THEN
                
                INSERT INTO user_achievements (user_id, achievement_id)
                VALUES (p_user_id, achievement_record.id);
                
                achievements_awarded := achievements_awarded + 1;
            END IF;
        END IF;
    END LOOP;
    
    RETURN achievements_awarded;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS
ALTER TABLE user_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

-- User level policies
CREATE POLICY user_own_levels ON user_levels
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Achievement policies
CREATE POLICY user_own_achievements ON user_achievements
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

CREATE POLICY public_achievements_read ON user_achievements
    FOR SELECT TO authenticated_users
    USING (is_public = true);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE user_levels IS 'User progression levels and experience points';
COMMENT ON TABLE achievements IS 'Achievement definitions with requirements and rewards';
COMMENT ON TABLE user_achievements IS 'User achievement completions and progress';
COMMENT ON TABLE badges IS 'Badge definitions and visual properties';
COMMENT ON TABLE user_badges IS 'User badge awards and collections';
COMMENT ON TABLE challenges IS 'Time-limited challenges and special events';
COMMENT ON TABLE user_challenge_participation IS 'User participation in challenges';
COMMENT ON TABLE leaderboards IS 'Leaderboard definitions and configurations';
COMMENT ON TABLE leaderboard_entries IS 'Current leaderboard rankings and scores';
COMMENT ON TABLE rewards IS 'Reward definitions and properties';
COMMENT ON TABLE user_rewards IS 'User reward claims and history';
COMMENT ON TABLE experience_actions IS 'XP-earning action definitions';
COMMENT ON TABLE user_experience_log IS 'Log of user XP gains and activities';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================