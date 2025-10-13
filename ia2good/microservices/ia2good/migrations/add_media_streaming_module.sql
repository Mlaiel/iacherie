-- ========================================
-- MEDIA & LIVE STREAMING MODULE MIGRATION
-- ========================================
-- This migration adds support for:
-- - Photo/video/audio/document uploads
-- - Live streaming with chat
-- - Media management and moderation
-- ========================================

-- Create enums
CREATE TYPE ia2good_media_type AS ENUM (
    'photo',
    'video',
    'live_stream',
    'audio',
    'document'
);

CREATE TYPE ia2good_media_status AS ENUM (
    'uploading',
    'processing',
    'ready',
    'failed',
    'deleted'
);

CREATE TYPE ia2good_stream_status AS ENUM (
    'scheduled',
    'live',
    'ended',
    'cancelled'
);

CREATE TYPE ia2good_stream_quality AS ENUM (
    'low',      -- 360p
    'medium',   -- 480p
    'high',     -- 720p
    'hd'        -- 1080p
);

-- ========================================
-- MEDIA TABLE
-- ========================================
CREATE TABLE ia2good_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Media info
    type ia2good_media_type NOT NULL,
    status ia2good_media_status NOT NULL DEFAULT 'uploading',
    title VARCHAR(255),
    description TEXT,
    
    -- File details
    original_filename VARCHAR(500) NOT NULL,
    file_key VARCHAR(500) NOT NULL UNIQUE,
    file_url VARCHAR(1000),
    thumbnail_url VARCHAR(1000),
    
    -- Technical details
    mime_type VARCHAR(100),
    file_size INTEGER,
    duration INTEGER,  -- seconds (for videos/audio)
    width INTEGER,     -- pixels
    height INTEGER,    -- pixels
    bitrate INTEGER,   -- kbps
    codec VARCHAR(50),
    
    -- Processing info
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,
    variants JSONB,    -- {"small": "url", "medium": "url", "large": "url"}
    
    -- Owner and context
    uploaded_by UUID NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    
    -- Engagement
    views_count INTEGER DEFAULT 0,
    downloads_count INTEGER DEFAULT 0,
    
    -- Tags and metadata
    tags TEXT[],
    extra_metadata JSONB,
    
    -- Moderation
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    moderation_status VARCHAR(20) DEFAULT 'pending',
    moderated_at TIMESTAMP WITH TIME ZONE,
    moderated_by UUID,
    moderation_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for media
CREATE INDEX idx_media_type ON ia2good_media(type);
CREATE INDEX idx_media_status ON ia2good_media(status);
CREATE INDEX idx_media_uploaded_by ON ia2good_media(uploaded_by);
CREATE INDEX idx_media_entity ON ia2good_media(entity_type, entity_id);
CREATE INDEX idx_media_created_at ON ia2good_media(created_at DESC);
CREATE INDEX idx_media_is_public ON ia2good_media(is_public);
CREATE INDEX idx_media_moderation_status ON ia2good_media(moderation_status);
CREATE INDEX idx_media_deleted_at ON ia2good_media(deleted_at) WHERE deleted_at IS NULL;

-- GIN index for tags search
CREATE INDEX idx_media_tags ON ia2good_media USING GIN(tags);

-- ========================================
-- LIVE STREAMS TABLE
-- ========================================
CREATE TABLE ia2good_live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Stream info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ia2good_stream_status NOT NULL DEFAULT 'scheduled',
    
    -- Streaming details
    stream_key VARCHAR(100) UNIQUE NOT NULL,
    stream_url VARCHAR(500),
    playback_url VARCHAR(500),
    embed_code TEXT,
    
    -- Quality settings
    max_quality ia2good_stream_quality DEFAULT 'high',
    enable_recording BOOLEAN DEFAULT TRUE,
    enable_chat BOOLEAN DEFAULT TRUE,
    
    -- Scheduling
    scheduled_start TIMESTAMP WITH TIME ZONE,
    scheduled_end TIMESTAMP WITH TIME ZONE,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    
    -- Streamer
    streamer_id UUID NOT NULL,
    co_streamers UUID[],
    
    -- Context
    entity_type VARCHAR(50),
    entity_id UUID,
    
    -- Engagement
    current_viewers INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    
    -- Recording
    recording_url VARCHAR(500),
    recording_duration INTEGER,  -- seconds
    recording_size INTEGER,      -- bytes
    
    -- Privacy
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    password_protected BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    allowed_viewers UUID[],
    
    -- Technical details
    bitrate INTEGER,
    resolution VARCHAR(20),
    fps INTEGER,
    codec VARCHAR(50),
    
    -- Moderation
    moderation_enabled BOOLEAN DEFAULT TRUE,
    banned_words TEXT[],
    moderator_ids UUID[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for live streams
CREATE INDEX idx_streams_status ON ia2good_live_streams(status);
CREATE INDEX idx_streams_streamer_id ON ia2good_live_streams(streamer_id);
CREATE INDEX idx_streams_scheduled_start ON ia2good_live_streams(scheduled_start);
CREATE INDEX idx_streams_entity ON ia2good_live_streams(entity_type, entity_id);
CREATE INDEX idx_streams_created_at ON ia2good_live_streams(created_at DESC);
CREATE INDEX idx_streams_is_public ON ia2good_live_streams(is_public);
CREATE INDEX idx_streams_is_live ON ia2good_live_streams(status) WHERE status = 'live';

-- ========================================
-- STREAM COMMENTS TABLE
-- ========================================
CREATE TABLE ia2good_stream_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relations
    stream_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Content
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    
    -- Moderation
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Engagement
    likes_count INTEGER DEFAULT 0,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for stream comments
CREATE INDEX idx_stream_comments_stream_id ON ia2good_stream_comments(stream_id, created_at DESC);
CREATE INDEX idx_stream_comments_user_id ON ia2good_stream_comments(user_id);
CREATE INDEX idx_stream_comments_created_at ON ia2good_stream_comments(created_at DESC);
CREATE INDEX idx_stream_comments_is_deleted ON ia2good_stream_comments(is_deleted) WHERE is_deleted = FALSE;

-- ========================================
-- STREAM REACTIONS TABLE
-- ========================================
CREATE TABLE ia2good_stream_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relations
    stream_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Reaction type
    reaction_type VARCHAR(20) NOT NULL, -- like, love, wow, sad, angry
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint: one reaction per user per stream
    UNIQUE(stream_id, user_id)
);

-- Indexes for stream reactions
CREATE INDEX idx_stream_reactions_stream_id ON ia2good_stream_reactions(stream_id);
CREATE INDEX idx_stream_reactions_user_id ON ia2good_stream_reactions(user_id);
CREATE INDEX idx_stream_reactions_created_at ON ia2good_stream_reactions(created_at DESC);

-- ========================================
-- COMMENTS
-- ========================================
COMMENT ON TABLE ia2good_media IS 'Media files (photos, videos, audio, documents)';
COMMENT ON TABLE ia2good_live_streams IS 'Live streaming sessions with chat and reactions';
COMMENT ON TABLE ia2good_stream_comments IS 'Comments on live streams';
COMMENT ON TABLE ia2good_stream_reactions IS 'Real-time reactions during live streams';

COMMENT ON COLUMN ia2good_media.file_key IS 'S3/MinIO object key for file storage';
COMMENT ON COLUMN ia2good_media.variants IS 'Different sizes/qualities as JSON: {"small": "url", "medium": "url"}';
COMMENT ON COLUMN ia2good_media.extra_metadata IS 'EXIF data, technical info, etc.';
COMMENT ON COLUMN ia2good_live_streams.stream_key IS 'Secret key for OBS/streaming software';
COMMENT ON COLUMN ia2good_live_streams.stream_url IS 'RTMP ingest URL for streaming';
COMMENT ON COLUMN ia2good_live_streams.playback_url IS 'HLS/DASH URL for playback';
