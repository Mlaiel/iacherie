-- ============================================================================
-- PostgreSQL Migration: 002_media_metadata.sql
-- Media Metadata Management for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration creates comprehensive media metadata management tables
-- supporting audio, video, image, and document content with AI analysis,
-- fingerprinting, copyright protection, and advanced content management.
-- ============================================================================

-- ============================================================================
-- MEDIA CONTENT TABLE
-- ============================================================================

-- Main content table supporting all media types
CREATE TABLE IF NOT EXISTS media_content (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Content identification
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('audio', 'video', 'image', 'document', 'text', 'interactive')),
    file_format VARCHAR(20) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- File information
    original_filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(128) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    storage_backend VARCHAR(50) DEFAULT 's3',
    
    -- Content dimensions and duration
    width INTEGER,
    height INTEGER,
    duration_seconds DECIMAL(10,3),
    frame_rate DECIMAL(8,3),
    bit_rate INTEGER,
    sample_rate INTEGER,
    channels INTEGER,
    
    -- Content quality and encoding
    quality_score DECIMAL(5,2),
    encoding_format VARCHAR(50),
    compression_ratio DECIMAL(8,4),
    color_space VARCHAR(20),
    audio_codec VARCHAR(50),
    video_codec VARCHAR(50),
    
    -- Visibility and access
    visibility VARCHAR(20) DEFAULT 'private' CHECK (visibility IN ('public', 'unlisted', 'private', 'collaboration')),
    access_level VARCHAR(20) DEFAULT 'owner' CHECK (access_level IN ('owner', 'collaborators', 'subscribers', 'public')),
    downloadable BOOLEAN DEFAULT FALSE,
    
    -- Content status and processing
    processing_status VARCHAR(30) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed', 'quarantined')),
    processing_progress INTEGER DEFAULT 0,
    processing_error TEXT,
    
    -- Content classification
    category VARCHAR(100),
    genre VARCHAR(100),
    mood VARCHAR(100),
    style VARCHAR(100),
    tempo INTEGER,
    key_signature VARCHAR(10),
    language VARCHAR(10),
    
    -- Content tags and metadata
    tags TEXT[],
    keywords TEXT[],
    hashtags TEXT[],
    location_data JSONB,
    equipment_used JSONB DEFAULT '{}',
    creation_software VARCHAR(200),
    
    -- Copyright and licensing
    copyright_status VARCHAR(30) DEFAULT 'owned' CHECK (copyright_status IN ('owned', 'licensed', 'royalty_free', 'creative_commons', 'public_domain', 'disputed')),
    license_type VARCHAR(50),
    license_url VARCHAR(500),
    attribution_required BOOLEAN DEFAULT FALSE,
    commercial_use_allowed BOOLEAN DEFAULT TRUE,
    derivative_works_allowed BOOLEAN DEFAULT TRUE,
    
    -- AI analysis flags
    ai_analysis_completed BOOLEAN DEFAULT FALSE,
    ai_analysis_version VARCHAR(20),
    content_moderation_status VARCHAR(30) DEFAULT 'pending' CHECK (content_moderation_status IN ('pending', 'approved', 'rejected', 'flagged', 'review_required')),
    moderation_flags TEXT[],
    
    -- Performance metrics
    view_count BIGINT DEFAULT 0,
    download_count BIGINT DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- SEO and discoverability
    seo_title VARCHAR(200),
    seo_description TEXT,
    featured BOOLEAN DEFAULT FALSE,
    trending_score DECIMAL(10,4) DEFAULT 0,
    
    -- Audit timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    custom_metadata JSONB DEFAULT '{}',
    system_metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- MEDIA FINGERPRINTS TABLE
-- ============================================================================

-- AI-generated fingerprints for content protection
CREATE TABLE IF NOT EXISTS media_fingerprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Fingerprint information
    fingerprint_type VARCHAR(50) NOT NULL CHECK (fingerprint_type IN ('audio_chromaprint', 'audio_mfcc', 'image_phash', 'image_dhash', 'video_frame_hash', 'text_similarity')),
    fingerprint_data BYTEA NOT NULL,
    fingerprint_hash VARCHAR(128) NOT NULL,
    
    -- Algorithm information
    algorithm_name VARCHAR(100) NOT NULL,
    algorithm_version VARCHAR(20) NOT NULL,
    algorithm_parameters JSONB DEFAULT '{}',
    
    -- Quality and confidence
    confidence_score DECIMAL(5,4) DEFAULT 1.0,
    quality_score DECIMAL(5,4) DEFAULT 1.0,
    
    -- Processing information
    processing_time_ms INTEGER,
    segment_start DECIMAL(10,3),
    segment_end DECIMAL(10,3),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA ANALYSIS TABLE
-- ============================================================================

-- AI analysis results for content
CREATE TABLE IF NOT EXISTS media_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Analysis type and version
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('content_detection', 'scene_analysis', 'emotion_analysis', 'object_detection', 'face_recognition', 'text_extraction', 'speech_to_text', 'music_analysis', 'copyright_detection')),
    analysis_version VARCHAR(20) NOT NULL,
    model_name VARCHAR(100),
    
    -- Analysis results
    confidence_score DECIMAL(5,4) NOT NULL,
    analysis_data JSONB NOT NULL,
    
    -- Extracted features
    detected_objects JSONB DEFAULT '[]',
    detected_faces JSONB DEFAULT '[]',
    detected_text TEXT,
    transcription TEXT,
    language_detected VARCHAR(10),
    
    -- Content classification
    content_categories JSONB DEFAULT '[]',
    nsfw_score DECIMAL(5,4) DEFAULT 0,
    violence_score DECIMAL(5,4) DEFAULT 0,
    explicit_score DECIMAL(5,4) DEFAULT 0,
    
    -- Audio analysis (for audio/video)
    bpm INTEGER,
    musical_key VARCHAR(10),
    energy_level DECIMAL(5,4),
    danceability DECIMAL(5,4),
    valence DECIMAL(5,4),
    instrumentalness DECIMAL(5,4),
    
    -- Processing information
    processing_time_ms INTEGER NOT NULL,
    gpu_used BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA THUMBNAILS TABLE
-- ============================================================================

-- Generated thumbnails and previews
CREATE TABLE IF NOT EXISTS media_thumbnails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Thumbnail information
    thumbnail_type VARCHAR(50) NOT NULL CHECK (thumbnail_type IN ('small', 'medium', 'large', 'preview', 'poster', 'animated')),
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_format VARCHAR(20) NOT NULL,
    file_size INTEGER NOT NULL,
    
    -- Storage information
    storage_path VARCHAR(1000) NOT NULL,
    storage_backend VARCHAR(50) DEFAULT 's3',
    public_url VARCHAR(1000),
    
    -- Generation information
    generated_at DECIMAL(10,3), -- For video: timestamp of frame used
    generation_method VARCHAR(50) DEFAULT 'auto',
    
    -- Quality and status
    quality_score DECIMAL(5,2) DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA VERSIONS TABLE
-- ============================================================================

-- Multiple versions/formats of the same content
CREATE TABLE IF NOT EXISTS media_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Version information
    version_type VARCHAR(50) NOT NULL CHECK (version_type IN ('original', 'compressed', 'preview', 'watermarked', 'transcoded')),
    version_name VARCHAR(200),
    
    -- File information
    file_format VARCHAR(20) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(128) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    
    -- Quality information
    width INTEGER,
    height INTEGER,
    duration_seconds DECIMAL(10,3),
    bit_rate INTEGER,
    quality_score DECIMAL(5,2),
    
    -- Processing information
    encoding_settings JSONB DEFAULT '{}',
    processing_time_ms INTEGER,
    
    -- Status
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA COLLECTIONS TABLE
-- ============================================================================

-- Albums, playlists, galleries, etc.
CREATE TABLE IF NOT EXISTS media_collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Collection information
    title VARCHAR(500) NOT NULL,
    description TEXT,
    collection_type VARCHAR(50) NOT NULL CHECK (collection_type IN ('album', 'playlist', 'gallery', 'portfolio', 'series', 'episode_collection')),
    
    -- Visual information
    cover_image_id UUID REFERENCES media_content(id),
    thumbnail_url VARCHAR(1000),
    color_scheme JSONB DEFAULT '{}',
    
    -- Organization
    category VARCHAR(100),
    genre VARCHAR(100),
    tags TEXT[],
    
    -- Visibility and access
    visibility VARCHAR(20) DEFAULT 'private' CHECK (visibility IN ('public', 'unlisted', 'private', 'collaboration')),
    collaborative BOOLEAN DEFAULT FALSE,
    
    -- Statistics
    item_count INTEGER DEFAULT 0,
    total_duration DECIMAL(10,3) DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    
    -- Status
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- MEDIA COLLECTION ITEMS TABLE
-- ============================================================================

-- Items within collections
CREATE TABLE IF NOT EXISTS media_collection_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID NOT NULL REFERENCES media_collections(id) ON DELETE CASCADE,
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Ordering and organization
    sort_order INTEGER NOT NULL DEFAULT 0,
    section VARCHAR(200),
    
    -- Item metadata
    title_override VARCHAR(500),
    description_override TEXT,
    
    -- Timestamps
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users_enhanced(id),
    
    -- Constraints
    UNIQUE(collection_id, media_id)
);

-- ============================================================================
-- MEDIA DOWNLOADS TABLE
-- ============================================================================

-- Track downloads for analytics and licensing
CREATE TABLE IF NOT EXISTS media_downloads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users_enhanced(id) ON DELETE SET NULL,
    
    -- Download information
    download_type VARCHAR(50) NOT NULL CHECK (download_type IN ('original', 'preview', 'thumbnail', 'version')),
    version_id UUID REFERENCES media_versions(id),
    
    -- Client information
    ip_address INET,
    user_agent TEXT,
    referer VARCHAR(1000),
    country VARCHAR(3),
    
    -- Download metadata
    file_size BIGINT,
    download_duration_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- License and payment
    license_type VARCHAR(50),
    payment_required BOOLEAN DEFAULT FALSE,
    payment_id UUID,
    
    -- Audit timestamp
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA SHARING TABLE
-- ============================================================================

-- Track content sharing across platforms
CREATE TABLE IF NOT EXISTS media_sharing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    shared_by UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Sharing information
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(200),
    share_url VARCHAR(1000),
    share_type VARCHAR(50) DEFAULT 'direct',
    
    -- Engagement metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    
    -- Sharing metadata
    caption TEXT,
    hashtags TEXT[],
    location VARCHAR(200),
    
    -- Status
    post_status VARCHAR(30) DEFAULT 'active' CHECK (post_status IN ('active', 'deleted', 'hidden', 'reported')),
    
    -- Audit timestamps
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary content indexes
CREATE INDEX idx_media_content_user_id ON media_content(user_id);
CREATE INDEX idx_media_content_type ON media_content(content_type);
CREATE INDEX idx_media_content_status ON media_content(processing_status);
CREATE INDEX idx_media_content_visibility ON media_content(visibility);
CREATE INDEX idx_media_content_uploaded_at ON media_content(uploaded_at);
CREATE INDEX idx_media_content_file_hash ON media_content(file_hash);
CREATE INDEX idx_media_content_featured ON media_content(featured);

-- Fingerprint indexes
CREATE INDEX idx_media_fingerprints_media_id ON media_fingerprints(media_id);
CREATE INDEX idx_media_fingerprints_type ON media_fingerprints(fingerprint_type);
CREATE INDEX idx_media_fingerprints_hash ON media_fingerprints(fingerprint_hash);
CREATE INDEX idx_media_fingerprints_active ON media_fingerprints(is_active);

-- Analysis indexes
CREATE INDEX idx_media_analysis_media_id ON media_analysis(media_id);
CREATE INDEX idx_media_analysis_type ON media_analysis(analysis_type);
CREATE INDEX idx_media_analysis_current ON media_analysis(is_current);
CREATE INDEX idx_media_analysis_confidence ON media_analysis(confidence_score);

-- Thumbnail indexes
CREATE INDEX idx_media_thumbnails_media_id ON media_thumbnails(media_id);
CREATE INDEX idx_media_thumbnails_type ON media_thumbnails(thumbnail_type);
CREATE INDEX idx_media_thumbnails_primary ON media_thumbnails(is_primary);

-- Version indexes
CREATE INDEX idx_media_versions_media_id ON media_versions(media_id);
CREATE INDEX idx_media_versions_type ON media_versions(version_type);
CREATE INDEX idx_media_versions_primary ON media_versions(is_primary);

-- Collection indexes
CREATE INDEX idx_media_collections_user_id ON media_collections(user_id);
CREATE INDEX idx_media_collections_type ON media_collections(collection_type);
CREATE INDEX idx_media_collections_visibility ON media_collections(visibility);
CREATE INDEX idx_media_collections_featured ON media_collections(is_featured);

-- Collection item indexes
CREATE INDEX idx_media_collection_items_collection_id ON media_collection_items(collection_id);
CREATE INDEX idx_media_collection_items_media_id ON media_collection_items(media_id);
CREATE INDEX idx_media_collection_items_sort_order ON media_collection_items(collection_id, sort_order);

-- Download indexes
CREATE INDEX idx_media_downloads_media_id ON media_downloads(media_id);
CREATE INDEX idx_media_downloads_user_id ON media_downloads(user_id);
CREATE INDEX idx_media_downloads_downloaded_at ON media_downloads(downloaded_at);

-- Sharing indexes
CREATE INDEX idx_media_sharing_media_id ON media_sharing(media_id);
CREATE INDEX idx_media_sharing_shared_by ON media_sharing(shared_by);
CREATE INDEX idx_media_sharing_platform ON media_sharing(platform);
CREATE INDEX idx_media_sharing_shared_at ON media_sharing(shared_at);

-- Composite indexes for common queries
CREATE INDEX idx_media_content_user_type_status ON media_content(user_id, content_type, processing_status);
CREATE INDEX idx_media_content_visibility_featured ON media_content(visibility, featured);
CREATE INDEX idx_media_analysis_media_type_current ON media_analysis(media_id, analysis_type, is_current);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update collection statistics
CREATE OR REPLACE FUNCTION update_collection_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update item count and totals for the collection
    UPDATE media_collections SET
        item_count = (
            SELECT COUNT(*)
            FROM media_collection_items mci
            WHERE mci.collection_id = COALESCE(NEW.collection_id, OLD.collection_id)
        ),
        total_duration = (
            SELECT COALESCE(SUM(mc.duration_seconds), 0)
            FROM media_collection_items mci
            JOIN media_content mc ON mci.media_id = mc.id
            WHERE mci.collection_id = COALESCE(NEW.collection_id, OLD.collection_id)
        ),
        total_size = (
            SELECT COALESCE(SUM(mc.file_size), 0)
            FROM media_collection_items mci
            JOIN media_content mc ON mci.media_id = mc.id
            WHERE mci.collection_id = COALESCE(NEW.collection_id, OLD.collection_id)
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.collection_id, OLD.collection_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply collection stats trigger
CREATE TRIGGER update_collection_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON media_collection_items
    FOR EACH ROW EXECUTE FUNCTION update_collection_stats();

-- Update media view counts
CREATE OR REPLACE FUNCTION increment_view_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE media_content SET
        view_count = view_count + 1,
        updated_at = NOW()
    WHERE id = NEW.media_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all tables
CREATE TRIGGER update_media_content_updated_at 
    BEFORE UPDATE ON media_content 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_fingerprints_updated_at 
    BEFORE UPDATE ON media_fingerprints 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_analysis_updated_at 
    BEFORE UPDATE ON media_analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_thumbnails_updated_at 
    BEFORE UPDATE ON media_thumbnails 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_versions_updated_at 
    BEFORE UPDATE ON media_versions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_collections_updated_at 
    BEFORE UPDATE ON media_collections 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_sharing_updated_at 
    BEFORE UPDATE ON media_sharing 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Complete media view with analysis
CREATE OR REPLACE VIEW media_complete AS
SELECT 
    mc.*,
    
    -- Thumbnail information
    (SELECT mt.public_url FROM media_thumbnails mt 
     WHERE mt.media_id = mc.id AND mt.is_primary = true LIMIT 1) as primary_thumbnail,
     
    -- Analysis summary
    CASE WHEN COUNT(ma.id) > 0 THEN 
        json_agg(
            json_build_object(
                'type', ma.analysis_type,
                'confidence', ma.confidence_score,
                'data', ma.analysis_data
            )
        ) FILTER (WHERE ma.is_current = true)
    ELSE '[]'::json 
    END as analysis_results,
    
    -- Collection membership
    COALESCE(array_agg(DISTINCT mci.collection_id) FILTER (WHERE mci.collection_id IS NOT NULL), ARRAY[]::UUID[]) as collections
    
FROM media_content mc
LEFT JOIN media_analysis ma ON mc.id = ma.media_id
LEFT JOIN media_collection_items mci ON mc.id = mci.media_id
WHERE mc.deleted_at IS NULL
GROUP BY mc.id;

-- Public media view (for non-owners)
CREATE OR REPLACE VIEW media_public AS
SELECT 
    id,
    title,
    description,
    content_type,
    file_format,
    width,
    height,
    duration_seconds,
    category,
    genre,
    tags,
    view_count,
    like_count,
    uploaded_at,
    published_at
FROM media_content
WHERE visibility = 'public' 
    AND processing_status = 'completed'
    AND deleted_at IS NULL;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to get media with fingerprint similarity
CREATE OR REPLACE FUNCTION find_similar_media(
    p_fingerprint_hash VARCHAR(128),
    p_similarity_threshold DECIMAL(5,4) DEFAULT 0.85
)
RETURNS TABLE (
    media_id UUID,
    similarity_score DECIMAL(5,4),
    fingerprint_type VARCHAR(50)
) AS $$
BEGIN
    -- This is a simplified similarity search
    -- In production, you'd use specialized similarity functions
    RETURN QUERY
    SELECT 
        mf.media_id,
        CAST(0.95 as DECIMAL(5,4)) as similarity_score,  -- Placeholder similarity
        mf.fingerprint_type
    FROM media_fingerprints mf
    WHERE mf.fingerprint_hash = p_fingerprint_hash
        AND mf.is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to update content statistics
CREATE OR REPLACE FUNCTION update_content_stats(
    p_media_id UUID,
    p_stat_type VARCHAR(20),
    p_increment INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
BEGIN
    CASE p_stat_type
        WHEN 'view' THEN
            UPDATE media_content SET view_count = view_count + p_increment WHERE id = p_media_id;
        WHEN 'download' THEN
            UPDATE media_content SET download_count = download_count + p_increment WHERE id = p_media_id;
        WHEN 'like' THEN
            UPDATE media_content SET like_count = like_count + p_increment WHERE id = p_media_id;
        WHEN 'share' THEN
            UPDATE media_content SET share_count = share_count + p_increment WHERE id = p_media_id;
        WHEN 'comment' THEN
            UPDATE media_content SET comment_count = comment_count + p_increment WHERE id = p_media_id;
        ELSE
            RETURN FALSE;
    END CASE;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE media_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_collections ENABLE ROW LEVEL SECURITY;

-- Media content policies
CREATE POLICY media_owner_access ON media_content
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

CREATE POLICY media_public_read ON media_content
    FOR SELECT TO authenticated_users
    USING (visibility = 'public' AND processing_status = 'completed');

-- Collection policies
CREATE POLICY collection_owner_access ON media_collections
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

CREATE POLICY collection_public_read ON media_collections
    FOR SELECT TO authenticated_users
    USING (visibility = 'public');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE media_content IS 'Main content table supporting all media types with comprehensive metadata';
COMMENT ON TABLE media_fingerprints IS 'AI-generated fingerprints for content protection and similarity detection';
COMMENT ON TABLE media_analysis IS 'AI analysis results including content detection, emotion analysis, and classification';
COMMENT ON TABLE media_thumbnails IS 'Generated thumbnails and previews for media content';
COMMENT ON TABLE media_versions IS 'Multiple versions/formats of the same content (original, compressed, transcoded)';
COMMENT ON TABLE media_collections IS 'Collections like albums, playlists, galleries for organizing content';
COMMENT ON TABLE media_collection_items IS 'Items within collections with ordering and metadata';
COMMENT ON TABLE media_downloads IS 'Download tracking for analytics and licensing compliance';
COMMENT ON TABLE media_sharing IS 'Cross-platform content sharing tracking with engagement metrics';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================