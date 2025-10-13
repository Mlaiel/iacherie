-- ====================================
-- EDUVERIFY DATABASE SCHEMA
-- Module: Éducation IA Interactive
-- ====================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================================
-- TABLE: eduverify_content
-- ====================================
CREATE TABLE IF NOT EXISTS eduverify_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    content_text TEXT,
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('text', 'url', 'pdf', 'video', 'audio')),
    file_url TEXT,
    subject VARCHAR(100),
    topic VARCHAR(255),
    language VARCHAR(10) DEFAULT 'fr',
    dialect VARCHAR(50),
    academic_level VARCHAR(20),
    processing_mode VARCHAR(20) DEFAULT 'standard' CHECK (processing_mode IN ('standard', 'live_lecture', 'real_time')),
    ai_analysis JSONB DEFAULT '{}',
    word_count INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ====================================
-- TABLE: eduverify_quizzes
-- ====================================
CREATE TABLE IF NOT EXISTS eduverify_quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES eduverify_content(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    topic VARCHAR(255),
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard', 'mixed')),
    language VARCHAR(10) DEFAULT 'fr',
    questions JSONB NOT NULL,
    total_questions INTEGER NOT NULL,
    total_points INTEGER,
    time_limit_minutes INTEGER,
    passing_score INTEGER DEFAULT 60,
    professional_level VARCHAR(20),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ====================================
-- TABLE: eduverify_user_progress
-- ====================================
CREATE TABLE IF NOT EXISTS eduverify_user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES eduverify_quizzes(id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    points_earned INTEGER,
    total_points INTEGER,
    time_spent_seconds INTEGER,
    answers JSONB NOT NULL,
    correct_answers INTEGER,
    incorrect_answers INTEGER,
    skipped_answers INTEGER,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, quiz_id, completed_at)
);

-- ====================================
-- TABLE: eduverify_fact_checks
-- ====================================
CREATE TABLE IF NOT EXISTS eduverify_fact_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES eduverify_content(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    claim TEXT NOT NULL,
    verdict VARCHAR(20) NOT NULL CHECK (verdict IN ('true', 'mostly_true', 'half_true', 'mostly_false', 'false', 'unverified')),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),
    sources JSONB DEFAULT '[]',
    explanation TEXT NOT NULL,
    context TEXT,
    ai_reasoning TEXT,
    human_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ====================================
-- TABLE: eduverify_explanations
-- ====================================
CREATE TABLE IF NOT EXISTS eduverify_explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic VARCHAR(255) NOT NULL,
    academic_level VARCHAR(20) NOT NULL,
    field VARCHAR(100),
    explanation TEXT NOT NULL,
    simplified_explanation TEXT,
    analogies TEXT[],
    examples TEXT[],
    references JSONB DEFAULT '[]',
    language VARCHAR(10) DEFAULT 'fr',
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ====================================
-- INDEXES
-- ====================================
CREATE INDEX idx_eduverify_content_user ON eduverify_content(user_id);
CREATE INDEX idx_eduverify_content_subject ON eduverify_content(subject);
CREATE INDEX idx_eduverify_quizzes_content ON eduverify_quizzes(content_id);
CREATE INDEX idx_eduverify_quizzes_user ON eduverify_quizzes(user_id);
CREATE INDEX idx_eduverify_progress_user ON eduverify_user_progress(user_id);
CREATE INDEX idx_eduverify_progress_quiz ON eduverify_user_progress(quiz_id);
CREATE INDEX idx_eduverify_factchecks_content ON eduverify_fact_checks(content_id);
