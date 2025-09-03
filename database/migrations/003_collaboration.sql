-- ============================================================================
-- PostgreSQL Migration: 003_collaboration.sql
-- Collaboration System for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration creates comprehensive collaboration system tables
-- supporting project management, team collaboration, contract management,
-- revenue sharing, and cross-creator partnerships.
-- ============================================================================

-- ============================================================================
-- COLLABORATION REQUESTS TABLE
-- ============================================================================

-- Collaboration invitation and request system
CREATE TABLE IF NOT EXISTS collaboration_requests (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiator_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Request information
    collaboration_type VARCHAR(50) NOT NULL CHECK (collaboration_type IN ('music_production', 'video_creation', 'photography', 'content_writing', 'joint_project', 'cross_promotion', 'remix', 'cover', 'feature', 'guest_appearance')),
    project_title VARCHAR(255) NOT NULL,
    project_description TEXT NOT NULL,
    
    -- Request details
    collaboration_scope TEXT,
    deliverables TEXT[],
    requirements TEXT[],
    skills_needed TEXT[],
    
    -- Timeline and budget
    estimated_duration VARCHAR(100),
    start_date TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Terms and conditions
    terms_and_conditions TEXT,
    revenue_sharing_percentage DECIMAL(5,2),
    copyright_split JSONB DEFAULT '{}',
    credit_requirements TEXT,
    exclusivity_required BOOLEAN DEFAULT FALSE,
    
    -- Request status
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'cancelled', 'expired', 'negotiating')),
    response_message TEXT,
    
    -- Attachments and references
    attachments TEXT[],
    reference_content UUID REFERENCES media_content(id),
    inspiration_links TEXT[],
    
    -- Priority and urgency
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    is_urgent BOOLEAN DEFAULT FALSE,
    
    -- Communication preferences
    preferred_communication VARCHAR(50) DEFAULT 'platform' CHECK (preferred_communication IN ('platform', 'email', 'discord', 'slack', 'zoom', 'phone')),
    communication_frequency VARCHAR(30) DEFAULT 'regular' CHECK (communication_frequency IN ('minimal', 'regular', 'frequent', 'daily')),
    
    -- Request metadata
    request_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COLLABORATION PROJECTS TABLE
-- ============================================================================

-- Active collaboration projects
CREATE TABLE IF NOT EXISTS collaboration_projects (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES collaboration_requests(id),
    
    -- Project information
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    project_type VARCHAR(50) NOT NULL,
    
    -- Project status and phases
    status VARCHAR(30) DEFAULT 'planning' CHECK (status IN ('planning', 'in_progress', 'review', 'completed', 'cancelled', 'on_hold', 'overdue')),
    current_phase VARCHAR(50),
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    
    -- Timeline
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    actual_start_date TIMESTAMP WITH TIME ZONE,
    actual_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Budget and financial
    budget DECIMAL(10,2),
    actual_cost DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_schedule JSONB DEFAULT '[]',
    
    -- Project data and deliverables
    project_data JSONB DEFAULT '{}',
    deliverables JSONB DEFAULT '[]',
    milestones JSONB DEFAULT '[]',
    
    -- Files and assets
    project_files UUID[] DEFAULT '{}',
    shared_assets UUID[] DEFAULT '{}',
    final_deliverables UUID[] DEFAULT '{}',
    
    -- Communication and collaboration
    communication_channel VARCHAR(200),
    project_visibility VARCHAR(20) DEFAULT 'participants' CHECK (project_visibility IN ('participants', 'public', 'private')),
    allow_public_viewing BOOLEAN DEFAULT FALSE,
    
    -- Revenue and rights
    revenue_sharing JSONB DEFAULT '{}',
    copyright_agreement JSONB DEFAULT '{}',
    licensing_terms TEXT,
    
    -- Quality and feedback
    quality_score DECIMAL(5,2),
    client_satisfaction DECIMAL(5,2),
    feedback TEXT,
    
    -- Project metadata
    project_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- COLLABORATION PARTICIPANTS TABLE
-- ============================================================================

-- Project participants and their roles
CREATE TABLE IF NOT EXISTS collaboration_participants (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES collaboration_projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Participant role and responsibilities
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'co_creator', 'contributor', 'advisor', 'client', 'producer', 'manager', 'reviewer')),
    role_description TEXT,
    responsibilities TEXT[],
    
    -- Permissions and access
    permissions JSONB DEFAULT '{}',
    can_edit_project BOOLEAN DEFAULT FALSE,
    can_invite_others BOOLEAN DEFAULT FALSE,
    can_approve_changes BOOLEAN DEFAULT FALSE,
    can_access_financials BOOLEAN DEFAULT FALSE,
    
    -- Contribution and compensation
    contribution_percentage DECIMAL(5,2) DEFAULT 0.00,
    compensation_type VARCHAR(30) DEFAULT 'revenue_share' CHECK (compensation_type IN ('revenue_share', 'fixed_fee', 'hourly', 'milestone', 'none')),
    compensation_amount DECIMAL(10,2),
    compensation_currency VARCHAR(3) DEFAULT 'USD',
    
    -- Performance tracking
    tasks_assigned INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    hours_worked DECIMAL(8,2) DEFAULT 0,
    deliverables_submitted INTEGER DEFAULT 0,
    
    -- Availability and schedule
    availability_hours JSONB DEFAULT '{}',
    timezone VARCHAR(50),
    response_time_hours INTEGER DEFAULT 24,
    
    -- Communication preferences
    notification_preferences JSONB DEFAULT '{}',
    communication_methods TEXT[] DEFAULT '{}',
    
    -- Status and activity
    participation_status VARCHAR(30) DEFAULT 'active' CHECK (participation_status IN ('active', 'inactive', 'on_leave', 'removed', 'completed')),
    last_activity TIMESTAMP WITH TIME ZONE,
    
    -- Ratings and feedback
    performance_rating DECIMAL(3,2),
    feedback_received TEXT,
    feedback_given TEXT,
    
    -- Timestamps
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(project_id, user_id)
);

-- ============================================================================
-- COLLABORATION TASKS TABLE
-- ============================================================================

-- Project tasks and assignments
CREATE TABLE IF NOT EXISTS collaboration_tasks (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES collaboration_projects(id) ON DELETE CASCADE,
    
    -- Task information
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) DEFAULT 'general' CHECK (task_type IN ('general', 'creative', 'technical', 'review', 'administrative', 'milestone')),
    
    -- Assignment
    assigned_to UUID REFERENCES users_enhanced(id),
    assigned_by UUID REFERENCES users_enhanced(id),
    
    -- Task status and priority
    status VARCHAR(30) DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'review', 'completed', 'cancelled', 'blocked')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Timeline
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),
    due_date TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Dependencies and relationships
    parent_task_id UUID REFERENCES collaboration_tasks(id),
    depends_on UUID[] DEFAULT '{}',
    blocks UUID[] DEFAULT '{}',
    
    -- Deliverables and attachments
    deliverables TEXT[],
    attachments UUID[] DEFAULT '{}',
    notes TEXT,
    
    -- Progress tracking
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    checklist JSONB DEFAULT '[]',
    
    -- Review and approval
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users_enhanced(id),
    approval_notes TEXT,
    
    -- Task metadata
    task_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COLLABORATION MESSAGES TABLE
-- ============================================================================

-- Project communication and messaging
CREATE TABLE IF NOT EXISTS collaboration_messages (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES collaboration_projects(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Message content
    message_type VARCHAR(30) DEFAULT 'text' CHECK (message_type IN ('text', 'file', 'image', 'video', 'audio', 'link', 'system', 'notification')),
    content TEXT NOT NULL,
    formatted_content JSONB,
    
    -- Threading and replies
    thread_id UUID REFERENCES collaboration_messages(id),
    reply_to UUID REFERENCES collaboration_messages(id),
    
    -- Attachments and media
    attachments UUID[] DEFAULT '{}',
    media_urls TEXT[],
    
    -- Message metadata
    mentions UUID[] DEFAULT '{}',
    tags TEXT[],
    
    -- Status and delivery
    message_status VARCHAR(20) DEFAULT 'sent' CHECK (message_status IN ('draft', 'sent', 'delivered', 'read', 'deleted')),
    read_by JSONB DEFAULT '{}',
    
    -- Reactions and engagement
    reactions JSONB DEFAULT '{}',
    pinned BOOLEAN DEFAULT FALSE,
    important BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    edited_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- COLLABORATION CONTRACTS TABLE
-- ============================================================================

-- Legal contracts and agreements
CREATE TABLE IF NOT EXISTS collaboration_contracts (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES collaboration_projects(id) ON DELETE CASCADE,
    
    -- Contract information
    contract_title VARCHAR(255) NOT NULL,
    contract_type VARCHAR(50) NOT NULL CHECK (contract_type IN ('collaboration_agreement', 'revenue_sharing', 'licensing', 'work_for_hire', 'partnership', 'nda')),
    
    -- Contract parties
    parties JSONB NOT NULL, -- Array of participant details
    primary_contractor UUID NOT NULL REFERENCES users_enhanced(id),
    
    -- Contract terms
    contract_terms TEXT NOT NULL,
    payment_terms TEXT,
    deliverables TEXT[],
    timeline_terms TEXT,
    
    -- Financial terms
    total_value DECIMAL(12,2),
    payment_schedule JSONB DEFAULT '[]',
    revenue_split JSONB DEFAULT '{}',
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Legal and compliance
    jurisdiction VARCHAR(100),
    governing_law VARCHAR(200),
    dispute_resolution TEXT,
    termination_clause TEXT,
    
    -- Contract status
    status VARCHAR(30) DEFAULT 'draft' CHECK (status IN ('draft', 'pending_signatures', 'active', 'completed', 'terminated', 'disputed')),
    signatures JSONB DEFAULT '{}',
    
    -- Digital signatures
    contract_hash VARCHAR(128),
    blockchain_record VARCHAR(200),
    
    -- Timestamps
    draft_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signed_date TIMESTAMP WITH TIME ZONE,
    effective_date TIMESTAMP WITH TIME ZONE,
    expiry_date TIMESTAMP WITH TIME ZONE,
    
    -- Contract metadata
    contract_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COLLABORATION REVIEWS TABLE
-- ============================================================================

-- Reviews and ratings for collaboration participants
CREATE TABLE IF NOT EXISTS collaboration_reviews (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES collaboration_projects(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    reviewee_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Review content
    rating DECIMAL(3,2) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    review_text TEXT,
    
    -- Detailed ratings
    communication_rating DECIMAL(3,2),
    quality_rating DECIMAL(3,2),
    timeliness_rating DECIMAL(3,2),
    professionalism_rating DECIMAL(3,2),
    creativity_rating DECIMAL(3,2),
    
    -- Review categories
    review_categories TEXT[],
    strengths TEXT[],
    areas_for_improvement TEXT[],
    
    -- Recommendation
    would_collaborate_again BOOLEAN,
    recommendation_text TEXT,
    
    -- Review status
    review_status VARCHAR(20) DEFAULT 'published' CHECK (review_status IN ('draft', 'published', 'hidden', 'disputed')),
    
    -- Response from reviewee
    response_text TEXT,
    response_date TIMESTAMP WITH TIME ZONE,
    
    -- Moderation
    flagged BOOLEAN DEFAULT FALSE,
    moderation_notes TEXT,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(project_id, reviewer_id, reviewee_id)
);

-- ============================================================================
-- COLLABORATION TEMPLATES TABLE
-- ============================================================================

-- Templates for common collaboration types
CREATE TABLE IF NOT EXISTS collaboration_templates (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Template information
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    collaboration_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    
    -- Template data
    template_data JSONB NOT NULL,
    default_terms TEXT,
    suggested_timeline VARCHAR(100),
    typical_budget_range VARCHAR(100),
    
    -- Usage and popularity
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    
    -- Visibility and sharing
    is_public BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Template metadata
    tags TEXT[],
    target_audience TEXT[],
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Collaboration request indexes
CREATE INDEX idx_collaboration_requests_initiator ON collaboration_requests(initiator_id);
CREATE INDEX idx_collaboration_requests_target ON collaboration_requests(target_id);
CREATE INDEX idx_collaboration_requests_status ON collaboration_requests(status);
CREATE INDEX idx_collaboration_requests_type ON collaboration_requests(collaboration_type);
CREATE INDEX idx_collaboration_requests_created_at ON collaboration_requests(created_at);
CREATE INDEX idx_collaboration_requests_expires_at ON collaboration_requests(expires_at);

-- Project indexes
CREATE INDEX idx_collaboration_projects_request_id ON collaboration_projects(request_id);
CREATE INDEX idx_collaboration_projects_status ON collaboration_projects(status);
CREATE INDEX idx_collaboration_projects_start_date ON collaboration_projects(start_date);
CREATE INDEX idx_collaboration_projects_end_date ON collaboration_projects(end_date);

-- Participant indexes
CREATE INDEX idx_collaboration_participants_project_id ON collaboration_participants(project_id);
CREATE INDEX idx_collaboration_participants_user_id ON collaboration_participants(user_id);
CREATE INDEX idx_collaboration_participants_role ON collaboration_participants(role);
CREATE INDEX idx_collaboration_participants_status ON collaboration_participants(participation_status);

-- Task indexes
CREATE INDEX idx_collaboration_tasks_project_id ON collaboration_tasks(project_id);
CREATE INDEX idx_collaboration_tasks_assigned_to ON collaboration_tasks(assigned_to);
CREATE INDEX idx_collaboration_tasks_status ON collaboration_tasks(status);
CREATE INDEX idx_collaboration_tasks_due_date ON collaboration_tasks(due_date);
CREATE INDEX idx_collaboration_tasks_parent ON collaboration_tasks(parent_task_id);

-- Message indexes
CREATE INDEX idx_collaboration_messages_project_id ON collaboration_messages(project_id);
CREATE INDEX idx_collaboration_messages_sender_id ON collaboration_messages(sender_id);
CREATE INDEX idx_collaboration_messages_thread_id ON collaboration_messages(thread_id);
CREATE INDEX idx_collaboration_messages_sent_at ON collaboration_messages(sent_at);

-- Contract indexes
CREATE INDEX idx_collaboration_contracts_project_id ON collaboration_contracts(project_id);
CREATE INDEX idx_collaboration_contracts_contractor ON collaboration_contracts(primary_contractor);
CREATE INDEX idx_collaboration_contracts_status ON collaboration_contracts(status);
CREATE INDEX idx_collaboration_contracts_effective_date ON collaboration_contracts(effective_date);

-- Review indexes
CREATE INDEX idx_collaboration_reviews_project_id ON collaboration_reviews(project_id);
CREATE INDEX idx_collaboration_reviews_reviewer_id ON collaboration_reviews(reviewer_id);
CREATE INDEX idx_collaboration_reviews_reviewee_id ON collaboration_reviews(reviewee_id);
CREATE INDEX idx_collaboration_reviews_rating ON collaboration_reviews(rating);

-- Template indexes
CREATE INDEX idx_collaboration_templates_created_by ON collaboration_templates(created_by);
CREATE INDEX idx_collaboration_templates_type ON collaboration_templates(collaboration_type);
CREATE INDEX idx_collaboration_templates_public ON collaboration_templates(is_public);
CREATE INDEX idx_collaboration_templates_featured ON collaboration_templates(is_featured);

-- Composite indexes
CREATE INDEX idx_requests_target_status ON collaboration_requests(target_id, status);
CREATE INDEX idx_projects_status_dates ON collaboration_projects(status, start_date, end_date);
CREATE INDEX idx_participants_user_status ON collaboration_participants(user_id, participation_status);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update project completion percentage based on tasks
CREATE OR REPLACE FUNCTION update_project_completion()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE collaboration_projects SET
        completion_percentage = (
            SELECT CASE 
                WHEN COUNT(*) = 0 THEN 0
                ELSE ROUND(AVG(
                    CASE 
                        WHEN status = 'completed' THEN 100
                        WHEN status = 'in_progress' THEN progress_percentage
                        ELSE 0
                    END
                ))
            END
            FROM collaboration_tasks
            WHERE project_id = COALESCE(NEW.project_id, OLD.project_id)
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.project_id, OLD.project_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply completion percentage trigger
CREATE TRIGGER update_project_completion_trigger
    AFTER INSERT OR UPDATE OR DELETE ON collaboration_tasks
    FOR EACH ROW EXECUTE FUNCTION update_project_completion();

-- Auto-expire old requests
CREATE OR REPLACE FUNCTION auto_expire_requests()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE collaboration_requests SET
        status = 'expired',
        updated_at = NOW()
    WHERE expires_at < NOW() 
        AND status = 'pending';
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_collaboration_requests_updated_at 
    BEFORE UPDATE ON collaboration_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_projects_updated_at 
    BEFORE UPDATE ON collaboration_projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_participants_updated_at 
    BEFORE UPDATE ON collaboration_participants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_tasks_updated_at 
    BEFORE UPDATE ON collaboration_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_contracts_updated_at 
    BEFORE UPDATE ON collaboration_contracts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_reviews_updated_at 
    BEFORE UPDATE ON collaboration_reviews 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collaboration_templates_updated_at 
    BEFORE UPDATE ON collaboration_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active collaborations view
CREATE OR REPLACE VIEW active_collaborations AS
SELECT 
    p.*,
    
    -- Participant count
    (SELECT COUNT(*) FROM collaboration_participants cp WHERE cp.project_id = p.id AND cp.participation_status = 'active') as active_participants,
    
    -- Task summary
    (SELECT COUNT(*) FROM collaboration_tasks ct WHERE ct.project_id = p.id) as total_tasks,
    (SELECT COUNT(*) FROM collaboration_tasks ct WHERE ct.project_id = p.id AND ct.status = 'completed') as completed_tasks,
    
    -- Recent activity
    (SELECT MAX(sent_at) FROM collaboration_messages cm WHERE cm.project_id = p.id) as last_message_at
    
FROM collaboration_projects p
WHERE p.status IN ('planning', 'in_progress', 'review');

-- User collaboration summary view
CREATE OR REPLACE VIEW user_collaboration_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.display_name,
    
    -- Request statistics
    (SELECT COUNT(*) FROM collaboration_requests cr WHERE cr.initiator_id = u.id) as requests_sent,
    (SELECT COUNT(*) FROM collaboration_requests cr WHERE cr.target_id = u.id) as requests_received,
    (SELECT COUNT(*) FROM collaboration_requests cr WHERE cr.target_id = u.id AND cr.status = 'pending') as pending_requests,
    
    -- Project statistics
    (SELECT COUNT(DISTINCT cp.project_id) FROM collaboration_participants cp WHERE cp.user_id = u.id) as total_projects,
    (SELECT COUNT(DISTINCT cp.project_id) FROM collaboration_participants cp 
     JOIN collaboration_projects p ON cp.project_id = p.id 
     WHERE cp.user_id = u.id AND p.status = 'completed') as completed_projects,
    
    -- Average rating
    (SELECT AVG(rating) FROM collaboration_reviews cr WHERE cr.reviewee_id = u.id) as average_rating,
    (SELECT COUNT(*) FROM collaboration_reviews cr WHERE cr.reviewee_id = u.id) as total_reviews
    
FROM users_enhanced u;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to create collaboration request
CREATE OR REPLACE FUNCTION create_collaboration_request(
    p_initiator_id UUID,
    p_target_id UUID,
    p_collaboration_type VARCHAR(50),
    p_project_title VARCHAR(255),
    p_project_description TEXT,
    p_terms_and_conditions TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_request_id UUID;
BEGIN
    INSERT INTO collaboration_requests (
        initiator_id, target_id, collaboration_type, 
        project_title, project_description, terms_and_conditions
    )
    VALUES (
        p_initiator_id, p_target_id, p_collaboration_type,
        p_project_title, p_project_description, p_terms_and_conditions
    )
    RETURNING id INTO new_request_id;
    
    RETURN new_request_id;
END;
$$ LANGUAGE plpgsql;

-- Function to accept collaboration request and create project
CREATE OR REPLACE FUNCTION accept_collaboration_request(
    p_request_id UUID,
    p_response_message TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    request_record RECORD;
    new_project_id UUID;
BEGIN
    -- Get request details
    SELECT * INTO request_record FROM collaboration_requests WHERE id = p_request_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Collaboration request not found';
    END IF;
    
    IF request_record.status != 'pending' THEN
        RAISE EXCEPTION 'Request is not in pending status';
    END IF;
    
    -- Update request status
    UPDATE collaboration_requests SET
        status = 'accepted',
        response_message = p_response_message,
        responded_at = NOW(),
        updated_at = NOW()
    WHERE id = p_request_id;
    
    -- Create project
    INSERT INTO collaboration_projects (
        request_id, project_name, project_description, project_type
    )
    VALUES (
        p_request_id, request_record.project_title, 
        request_record.project_description, request_record.collaboration_type
    )
    RETURNING id INTO new_project_id;
    
    -- Add participants
    INSERT INTO collaboration_participants (project_id, user_id, role, permissions)
    VALUES 
        (new_project_id, request_record.initiator_id, 'owner', '{"can_edit_project": true, "can_invite_others": true}'),
        (new_project_id, request_record.target_id, 'co_creator', '{"can_edit_project": true}');
    
    RETURN new_project_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS
ALTER TABLE collaboration_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_messages ENABLE ROW LEVEL SECURITY;

-- Request policies
CREATE POLICY request_participant_access ON collaboration_requests
    FOR ALL TO authenticated_users
    USING (initiator_id = current_user_id() OR target_id = current_user_id());

-- Project policies
CREATE POLICY project_participant_access ON collaboration_projects
    FOR ALL TO authenticated_users
    USING (
        id IN (
            SELECT project_id FROM collaboration_participants 
            WHERE user_id = current_user_id() AND participation_status = 'active'
        )
    );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE collaboration_requests IS 'Collaboration invitations and requests between creators';
COMMENT ON TABLE collaboration_projects IS 'Active collaboration projects with timeline and deliverables';
COMMENT ON TABLE collaboration_participants IS 'Project participants with roles and permissions';
COMMENT ON TABLE collaboration_tasks IS 'Project tasks and assignments with progress tracking';
COMMENT ON TABLE collaboration_messages IS 'Project communication and messaging system';
COMMENT ON TABLE collaboration_contracts IS 'Legal contracts and agreements for collaborations';
COMMENT ON TABLE collaboration_reviews IS 'Reviews and ratings for collaboration participants';
COMMENT ON TABLE collaboration_templates IS 'Templates for common collaboration types';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================