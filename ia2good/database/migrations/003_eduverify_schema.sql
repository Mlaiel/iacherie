-- EduVerify Interactive Module Database Schema
-- Migration: 003_eduverify_schema
-- Created: 2025-01-XX
-- Description: Tables pour le module EduVerify (Éducation IA)

-- ============================================================================
-- TABLE: eduverify_content (Contenus éducatifs)
-- ============================================================================
CREATE TABLE eduverify_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Content Information
    title VARCHAR(255) NOT NULL,
    content_text TEXT,
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('text', 'url', 'pdf', 'video', 'audio')),
    file_url TEXT,
    
    -- Classification
    subject VARCHAR(100),
    topic VARCHAR(255),
    language VARCHAR(10) DEFAULT 'fr',
    dialect VARCHAR(50),
    academic_level VARCHAR(20),  -- elementary, high_school, undergraduate, graduate, doctorate
    
    -- Processing
    processing_mode VARCHAR(20) DEFAULT 'standard' CHECK (processing_mode IN ('standard', 'live_lecture', 'real_time')),
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    
    -- AI Analysis
    ai_analysis JSONB DEFAULT '{}'::JSONB,  -- {topics, difficulty, key_concepts, entities, prerequisites}
    word_count INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_content
CREATE INDEX idx_eduverify_content_user ON eduverify_content(user_id);
CREATE INDEX idx_eduverify_content_subject ON eduverify_content(subject);
CREATE INDEX idx_eduverify_content_topic ON eduverify_content(topic);
CREATE INDEX idx_eduverify_content_language ON eduverify_content(language);
CREATE INDEX idx_eduverify_content_level ON eduverify_content(academic_level);
CREATE INDEX idx_eduverify_content_status ON eduverify_content(processing_status);
CREATE INDEX idx_eduverify_content_created ON eduverify_content(created_at DESC);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_eduverify_content_updated_at
    BEFORE UPDATE ON eduverify_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: eduverify_quizzes (Quiz générés)
-- ============================================================================
CREATE TABLE eduverify_quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES eduverify_content(id) ON DELETE SET NULL,
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Quiz Information
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    topic VARCHAR(255),
    
    -- Configuration
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard', 'mixed')),
    language VARCHAR(10) DEFAULT 'fr',
    professional_level VARCHAR(20),
    
    -- Questions
    questions JSONB NOT NULL,  -- Array of questions with answers, explanations, references
    total_questions INTEGER NOT NULL,
    total_points INTEGER,
    
    -- Settings
    time_limit_minutes INTEGER,
    passing_score INTEGER DEFAULT 60 CHECK (passing_score BETWEEN 0 AND 100),
    
    -- Visibility
    is_public BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_quizzes
CREATE INDEX idx_eduverify_quizzes_content ON eduverify_quizzes(content_id);
CREATE INDEX idx_eduverify_quizzes_user ON eduverify_quizzes(user_id);
CREATE INDEX idx_eduverify_quizzes_subject ON eduverify_quizzes(subject);
CREATE INDEX idx_eduverify_quizzes_difficulty ON eduverify_quizzes(difficulty);
CREATE INDEX idx_eduverify_quizzes_public ON eduverify_quizzes(is_public) WHERE is_public = true;
CREATE INDEX idx_eduverify_quizzes_created ON eduverify_quizzes(created_at DESC);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_eduverify_quizzes_updated_at
    BEFORE UPDATE ON eduverify_quizzes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: eduverify_user_progress (Progression utilisateurs)
-- ============================================================================
CREATE TABLE eduverify_user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    quiz_id UUID NOT NULL REFERENCES eduverify_quizzes(id) ON DELETE CASCADE,
    
    -- Scores
    score FLOAT NOT NULL CHECK (score BETWEEN 0 AND 100),  -- Percentage
    points_earned INTEGER,
    total_points INTEGER,
    
    -- Answers
    answers JSONB NOT NULL,  -- {question_id: {user_answer, is_correct, time_spent}}
    correct_answers INTEGER,
    incorrect_answers INTEGER,
    skipped_answers INTEGER,
    
    -- Timing
    time_spent_seconds INTEGER,
    completed_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Allow multiple attempts
    UNIQUE(user_id, quiz_id, completed_at)
);

-- Indexes for eduverify_user_progress
CREATE INDEX idx_eduverify_progress_user ON eduverify_user_progress(user_id);
CREATE INDEX idx_eduverify_progress_quiz ON eduverify_user_progress(quiz_id);
CREATE INDEX idx_eduverify_progress_score ON eduverify_user_progress(score DESC);
CREATE INDEX idx_eduverify_progress_completed ON eduverify_user_progress(completed_at DESC);

-- ============================================================================
-- TABLE: eduverify_fact_checks (Fact-checking résultats)
-- ============================================================================
CREATE TABLE eduverify_fact_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES eduverify_content(id) ON DELETE SET NULL,
    user_id UUID, -- References users(id) from main system (NULL for public checks)
    
    -- Claim Information
    claim TEXT NOT NULL,
    verdict VARCHAR(20) NOT NULL CHECK (verdict IN ('true', 'mostly_true', 'half_true', 'mostly_false', 'false', 'unverified')),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),
    
    -- Supporting Information
    sources JSONB DEFAULT '[]'::JSONB,  -- [{title, url, credibility_score, date, excerpt}]
    explanation TEXT NOT NULL,
    context TEXT,
    ai_reasoning TEXT,
    
    -- Verification
    human_verified BOOLEAN DEFAULT false,
    verified_by UUID,  -- References users(id) from main system
    verified_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_fact_checks
CREATE INDEX idx_eduverify_factchecks_content ON eduverify_fact_checks(content_id);
CREATE INDEX idx_eduverify_factchecks_user ON eduverify_fact_checks(user_id);
CREATE INDEX idx_eduverify_factchecks_verdict ON eduverify_fact_checks(verdict);
CREATE INDEX idx_eduverify_factchecks_verified ON eduverify_fact_checks(human_verified);
CREATE INDEX idx_eduverify_factchecks_created ON eduverify_fact_checks(created_at DESC);

-- ============================================================================
-- TABLE: eduverify_explanations (Explications professionnelles)
-- ============================================================================
CREATE TABLE eduverify_explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Topic Information
    topic VARCHAR(255) NOT NULL,
    academic_level VARCHAR(20) NOT NULL CHECK (academic_level IN ('elementary', 'high_school', 'undergraduate', 'graduate', 'doctorate')),
    field VARCHAR(100),
    
    -- Explanations
    explanation TEXT NOT NULL,
    simplified_explanation TEXT,
    analogies TEXT[],
    examples TEXT[],
    
    -- References
    reference_list JSONB DEFAULT '[]'::JSONB,  -- [{title, authors, year, url, doi}]
    
    -- Language
    language VARCHAR(10) DEFAULT 'fr',
    
    -- Voting
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    
    -- Creator
    created_by UUID,  -- References users(id) from main system (NULL for AI-generated)
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_explanations
CREATE INDEX idx_eduverify_explanations_topic ON eduverify_explanations(topic);
CREATE INDEX idx_eduverify_explanations_level ON eduverify_explanations(academic_level);
CREATE INDEX idx_eduverify_explanations_field ON eduverify_explanations(field);
CREATE INDEX idx_eduverify_explanations_language ON eduverify_explanations(language);
CREATE INDEX idx_eduverify_explanations_votes ON eduverify_explanations((upvotes - downvotes) DESC);

-- ============================================================================
-- TABLE: eduverify_user_analytics (Analytics & Recommendations)
-- ============================================================================
CREATE TABLE eduverify_user_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE, -- References users(id) from main system
    
    -- Overall Statistics
    total_quizzes_taken INTEGER DEFAULT 0,
    total_quizzes_passed INTEGER DEFAULT 0,
    total_quizzes_failed INTEGER DEFAULT 0,
    average_score FLOAT,
    total_study_time_seconds INTEGER DEFAULT 0,
    
    -- Performance by Subject
    subject_performance JSONB DEFAULT '{}'::JSONB,  -- {subject: {attempts, avg_score, total_time}}
    topic_performance JSONB DEFAULT '{}'::JSONB,    -- {topic: {attempts, avg_score, mastery_level}}
    
    -- Difficulty Progression
    easy_quiz_avg FLOAT,
    medium_quiz_avg FLOAT,
    hard_quiz_avg FLOAT,
    
    -- Learning Patterns
    strengths TEXT[],  -- Topics user excels at
    weaknesses TEXT[], -- Topics needing improvement
    learning_style VARCHAR(50),  -- visual, auditory, kinesthetic, reading
    
    -- Recommendations
    recommended_topics TEXT[],
    recommended_difficulty VARCHAR(20),
    
    -- Streaks & Achievements
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_user_analytics
CREATE INDEX idx_eduverify_analytics_user ON eduverify_user_analytics(user_id);
CREATE INDEX idx_eduverify_analytics_avg_score ON eduverify_user_analytics(average_score DESC);
CREATE INDEX idx_eduverify_analytics_streak ON eduverify_user_analytics(current_streak_days DESC);

-- Trigger for auto-update updated_at
CREATE TRIGGER update_eduverify_analytics_updated_at
    BEFORE UPDATE ON eduverify_user_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: eduverify_live_sessions (Live Lecture Sessions)
-- ============================================================================
CREATE TABLE eduverify_live_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Session Information
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled')),
    
    -- Transcription
    full_transcript TEXT,
    fact_checks_count INTEGER DEFAULT 0,
    errors_detected INTEGER DEFAULT 0,
    
    -- Timing
    duration_seconds INTEGER,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for eduverify_live_sessions
CREATE INDEX idx_eduverify_live_user ON eduverify_live_sessions(user_id);
CREATE INDEX idx_eduverify_live_status ON eduverify_live_sessions(status);
CREATE INDEX idx_eduverify_live_started ON eduverify_live_sessions(started_at DESC);

-- ============================================================================
-- TABLE: eduverify_explanation_votes (Votes on Explanations)
-- ============================================================================
CREATE TABLE eduverify_explanation_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    explanation_id UUID NOT NULL REFERENCES eduverify_explanations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- References users(id) from main system
    
    -- Vote
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(explanation_id, user_id)
);

-- Indexes for eduverify_explanation_votes
CREATE INDEX idx_eduverify_votes_explanation ON eduverify_explanation_votes(explanation_id);
CREATE INDEX idx_eduverify_votes_user ON eduverify_explanation_votes(user_id);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================
COMMENT ON TABLE eduverify_content IS 'Contenus éducatifs uploadés et traités par les utilisateurs';
COMMENT ON TABLE eduverify_quizzes IS 'Quiz générés automatiquement par IA à partir des contenus';
COMMENT ON TABLE eduverify_user_progress IS 'Progression et résultats des quiz par utilisateur';
COMMENT ON TABLE eduverify_fact_checks IS 'Résultats du fact-checking automatique';
COMMENT ON TABLE eduverify_explanations IS 'Explications pédagogiques par niveau et domaine';
COMMENT ON TABLE eduverify_user_analytics IS 'Analytics détaillées et recommandations personnalisées';
COMMENT ON TABLE eduverify_live_sessions IS 'Sessions de cours en direct avec fact-checking temps réel';
COMMENT ON TABLE eduverify_explanation_votes IS 'Votes utilisateurs sur la qualité des explications';
