"""
 Creator Database Migrations - Multi-Format Content Creator Schema Evolution
==============================================================================
Module: backend/database/migrations/creator_migrations.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Creator Migration Engine - Ultra Enterprise Production-Ready
Responsibility: Database schema evolution for multi-format content creators (musicians, bloggers, photographers, influencers, comedians)
============================================================================================================================

  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL 
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

CREATOR BUSINESS LOGIC MIGRATION FLOW:
Creator Registration → Profile Setup → Content Type Configuration → Upload Preferences → 
IA Protection Settings → Monetization Options → Collaboration Preferences → Distribution Channels

Content Creator Types Supported:
- Musicians/Artists: Audio tracks, albums, singles, live performances
- Bloggers/Writers: Articles, posts, newsletters, e-books
- Photographers: Photos, portfolios, stock images, prints
- Influencers: Social media content, brand partnerships, campaigns
- Comedians: Stand-up videos, sketches, podcasts, live shows
- Video Creators: YouTube videos, TikToks, documentaries, tutorials
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from sqlalchemy import text, Column, String, Integer, DateTime, Boolean, JSON, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from alembic import op
from alembic.operations import Operations

from .migration_manager import EnterpriseMigrationManager
from .migration_types import MigrationType, MigrationPriority, MigrationStatus

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Supported creator types with specialized workflows"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    VIDEO_CREATOR = "video_creator"
    PODCASTER = "podcaster"
    ARTIST = "artist"


class ContentFormat(Enum):
    """Content formats supported by creator type"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    MIXED_MEDIA = "mixed_media"


@dataclass
class CreatorMigrationPlan:
    """Migration plan for creator-specific database schema"""
    creator_types: Set[CreatorType]
    content_formats: Set[ContentFormat]
    enable_collaboration: bool = True
    enable_monetization: bool = True
    enable_protection: bool = True
    enable_analytics: bool = True


class CreatorMigrations:
    """
    Ultra-advanced creator database migrations for multi-format content platform
    
    Handles schema evolution for:
    - Creator profiles and preferences
    - Content type configurations
    - Upload and processing workflows
    - Protection and monetization settings
    - Collaboration and partnership management
    """
    
    def __init__(self, migration_manager: EnterpriseMigrationManager):
        self.migration_manager = migration_manager
        self.logger = logging.getLogger(__name__)
    
    async def create_creator_profiles_table(self) -> str:
        """
        Create comprehensive creator profiles table with multi-format support
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        CREATE TABLE IF NOT EXISTS creator_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            creator_type VARCHAR(50) NOT NULL CHECK (creator_type IN (
                'musician', 'blogger', 'photographer', 'influencer', 
                'comedian', 'video_creator', 'podcaster', 'artist'
            )),
            stage_name VARCHAR(255),
            bio TEXT,
            
            -- Professional Information
            professional_level VARCHAR(50) DEFAULT 'emerging' CHECK (professional_level IN (
                'emerging', 'intermediate', 'professional', 'established', 'celebrity'
            )),
            genres JSONB DEFAULT '[]',
            specialties JSONB DEFAULT '[]',
            equipment JSONB DEFAULT '{}',
            
            -- Content Preferences
            primary_content_format VARCHAR(50) NOT NULL CHECK (primary_content_format IN (
                'audio', 'video', 'image', 'text', 'podcast', 'live_stream', 'mixed_media'
            )),
            supported_formats JSONB DEFAULT '[]',
            upload_frequency VARCHAR(50) DEFAULT 'weekly',
            target_audience JSONB DEFAULT '{}',
            
            -- Platform Integration
            platform_accounts JSONB DEFAULT '{}',
            verified_platforms JSONB DEFAULT '[]',
            platform_statistics JSONB DEFAULT '{}',
            
            -- Collaboration Settings
            open_for_collaboration BOOLEAN DEFAULT true,
            collaboration_types JSONB DEFAULT '[]',
            collaboration_rate DECIMAL(10,2),
            collaboration_preferences JSONB DEFAULT '{}',
            
            -- Protection Settings
            protection_level VARCHAR(50) DEFAULT 'standard' CHECK (protection_level IN (
                'basic', 'standard', 'advanced', 'enterprise', 'ultra'
            )),
            watermark_enabled BOOLEAN DEFAULT true,
            fingerprint_enabled BOOLEAN DEFAULT true,
            monitoring_enabled BOOLEAN DEFAULT true,
            
            -- Monetization Settings
            monetization_enabled BOOLEAN DEFAULT true,
            revenue_sharing_enabled BOOLEAN DEFAULT false,
            pricing_model VARCHAR(50) DEFAULT 'flexible',
            base_rates JSONB DEFAULT '{}',
            
            -- Analytics Preferences
            analytics_level VARCHAR(50) DEFAULT 'standard',
            share_analytics BOOLEAN DEFAULT false,
            public_stats BOOLEAN DEFAULT false,
            
            -- Metadata
            profile_completion_score INTEGER DEFAULT 0,
            verification_status VARCHAR(50) DEFAULT 'pending',
            verification_documents JSONB DEFAULT '[]',
            profile_views INTEGER DEFAULT 0,
            follower_count INTEGER DEFAULT 0,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id)
        );
        
        -- Indexes for optimal performance
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_creator_type ON creator_profiles(creator_type);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_content_format ON creator_profiles(primary_content_format);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_collaboration ON creator_profiles(open_for_collaboration);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_monetization ON creator_profiles(monetization_enabled);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_verification ON creator_profiles(verification_status);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_professional_level ON creator_profiles(professional_level);
        
        -- GIN indexes for JSONB fields
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_genres ON creator_profiles USING GIN(genres);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_platforms ON creator_profiles USING GIN(platform_accounts);
        CREATE INDEX IF NOT EXISTS idx_creator_profiles_collaboration_types ON creator_profiles USING GIN(collaboration_types);
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.SCHEMA,
            priority=MigrationPriority.HIGH,
            description="Create comprehensive creator profiles table with multi-format support"
        )
    
    async def create_content_types_table(self) -> str:
        """
        Create content types configuration table for creator-specific content management
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        CREATE TABLE IF NOT EXISTS creator_content_types (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            creator_id UUID NOT NULL REFERENCES creator_profiles(id) ON DELETE CASCADE,
            content_type VARCHAR(100) NOT NULL,
            content_format VARCHAR(50) NOT NULL,
            
            -- Type Configuration
            type_name VARCHAR(255) NOT NULL,
            description TEXT,
            file_extensions JSONB DEFAULT '[]',
            max_file_size_mb INTEGER DEFAULT 100,
            processing_requirements JSONB DEFAULT '{}',
            
            -- Quality Settings
            quality_standards JSONB DEFAULT '{}',
            compression_settings JSONB DEFAULT '{}',
            resolution_requirements JSONB DEFAULT '{}',
            
            -- Protection Configuration
            protection_enabled BOOLEAN DEFAULT true,
            watermark_required BOOLEAN DEFAULT false,
            fingerprint_algorithm VARCHAR(100),
            monitoring_frequency VARCHAR(50) DEFAULT 'daily',
            
            -- Monetization Rules
            monetizable BOOLEAN DEFAULT true,
            pricing_model VARCHAR(50) DEFAULT 'flexible',
            base_price DECIMAL(10,2),
            licensing_options JSONB DEFAULT '[]',
            
            -- Processing Pipeline
            ai_processing_enabled BOOLEAN DEFAULT true,
            seo_optimization BOOLEAN DEFAULT true,
            auto_tagging BOOLEAN DEFAULT true,
            thumbnail_generation BOOLEAN DEFAULT true,
            
            -- Distribution Settings
            auto_distribution BOOLEAN DEFAULT false,
            distribution_platforms JSONB DEFAULT '[]',
            publication_schedule JSONB DEFAULT '{}',
            
            -- Analytics Configuration
            track_engagement BOOLEAN DEFAULT true,
            track_revenue BOOLEAN DEFAULT true,
            track_protection BOOLEAN DEFAULT true,
            
            is_active BOOLEAN DEFAULT true,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(creator_id, content_type, content_format)
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_content_types_creator ON creator_content_types(creator_id);
        CREATE INDEX IF NOT EXISTS idx_content_types_format ON creator_content_types(content_format);
        CREATE INDEX IF NOT EXISTS idx_content_types_active ON creator_content_types(is_active);
        CREATE INDEX IF NOT EXISTS idx_content_types_monetizable ON creator_content_types(monetizable);
        
        -- JSONB indexes
        CREATE INDEX IF NOT EXISTS idx_content_types_extensions ON creator_content_types USING GIN(file_extensions);
        CREATE INDEX IF NOT EXISTS idx_content_types_platforms ON creator_content_types USING GIN(distribution_platforms);
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.SCHEMA,
            priority=MigrationPriority.HIGH,
            description="Create content types configuration table for creators"
        )
    
    async def create_creator_collaborations_table(self) -> str:
        """
        Create creator collaboration management table for cross-creator partnerships
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        CREATE TABLE IF NOT EXISTS creator_collaborations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            initiator_id UUID NOT NULL REFERENCES creator_profiles(id) ON DELETE CASCADE,
            collaborator_id UUID NOT NULL REFERENCES creator_profiles(id) ON DELETE CASCADE,
            
            -- Collaboration Details
            collaboration_type VARCHAR(100) NOT NULL CHECK (collaboration_type IN (
                'music_collaboration', 'content_exchange', 'cross_promotion', 
                'joint_creation', 'remix_permission', 'feature_request',
                'brand_partnership', 'event_collaboration', 'mentorship'
            )),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            
            -- Project Information
            project_scope JSONB DEFAULT '{}',
            deliverables JSONB DEFAULT '[]',
            timeline JSONB DEFAULT '{}',
            budget DECIMAL(12,2),
            revenue_split JSONB DEFAULT '{}',
            
            -- Status Management
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
                'pending', 'accepted', 'in_progress', 'review', 
                'completed', 'cancelled', 'disputed'
            )),
            progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
            
            -- Communication
            messages JSONB DEFAULT '[]',
            shared_files JSONB DEFAULT '[]',
            meeting_notes JSONB DEFAULT '[]',
            
            -- Legal and Rights
            contract_terms JSONB DEFAULT '{}',
            rights_sharing JSONB DEFAULT '{}',
            exclusivity_terms JSONB DEFAULT '{}',
            termination_conditions JSONB DEFAULT '{}',
            
            -- Dates and Deadlines
            start_date TIMESTAMP WITH TIME ZONE,
            deadline TIMESTAMP WITH TIME ZONE,
            completion_date TIMESTAMP WITH TIME ZONE,
            
            -- Ratings and Feedback
            initiator_rating INTEGER CHECK (initiator_rating >= 1 AND initiator_rating <= 5),
            collaborator_rating INTEGER CHECK (collaborator_rating >= 1 AND collaborator_rating <= 5),
            feedback JSONB DEFAULT '{}',
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            CHECK (initiator_id != collaborator_id)
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_collaborations_initiator ON creator_collaborations(initiator_id);
        CREATE INDEX IF NOT EXISTS idx_collaborations_collaborator ON creator_collaborations(collaborator_id);
        CREATE INDEX IF NOT EXISTS idx_collaborations_type ON creator_collaborations(collaboration_type);
        CREATE INDEX IF NOT EXISTS idx_collaborations_status ON creator_collaborations(status);
        CREATE INDEX IF NOT EXISTS idx_collaborations_deadline ON creator_collaborations(deadline);
        
        -- Composite indexes for queries
        CREATE INDEX IF NOT EXISTS idx_collaborations_creator_status ON creator_collaborations(initiator_id, status);
        CREATE INDEX IF NOT EXISTS idx_collaborations_active ON creator_collaborations(status) WHERE status IN ('pending', 'accepted', 'in_progress');
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.SCHEMA,
            priority=MigrationPriority.MEDIUM,
            description="Create creator collaboration management table"
        )
    
    async def create_creator_monetization_table(self) -> str:
        """
        Create creator monetization tracking and configuration table
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        CREATE TABLE IF NOT EXISTS creator_monetization (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            creator_id UUID NOT NULL REFERENCES creator_profiles(id) ON DELETE CASCADE,
            
            -- Revenue Configuration
            revenue_model VARCHAR(50) DEFAULT 'multiple' CHECK (revenue_model IN (
                'subscription', 'per_content', 'commission', 'licensing', 
                'advertising', 'donation', 'multiple'
            )),
            subscription_price DECIMAL(10,2),
            content_pricing JSONB DEFAULT '{}',
            commission_rate DECIMAL(5,2) DEFAULT 15.00,
            
            -- Payment Configuration
            payment_methods JSONB DEFAULT '[]',
            payout_frequency VARCHAR(50) DEFAULT 'monthly',
            minimum_payout DECIMAL(10,2) DEFAULT 50.00,
            payment_details JSONB DEFAULT '{}',
            
            -- Platform Revenue Tracking
            platform_earnings JSONB DEFAULT '{}',
            total_lifetime_earnings DECIMAL(15,2) DEFAULT 0.00,
            current_month_earnings DECIMAL(12,2) DEFAULT 0.00,
            pending_earnings DECIMAL(12,2) DEFAULT 0.00,
            
            -- Content Performance
            top_earning_content JSONB DEFAULT '[]',
            revenue_by_format JSONB DEFAULT '{}',
            revenue_trends JSONB DEFAULT '{}',
            
            -- Licensing and Rights
            licensing_enabled BOOLEAN DEFAULT true,
            licensing_terms JSONB DEFAULT '{}',
            exclusive_deals JSONB DEFAULT '[]',
            
            -- Analytics and Reporting
            revenue_analytics_enabled BOOLEAN DEFAULT true,
            public_earnings_display BOOLEAN DEFAULT false,
            detailed_reporting BOOLEAN DEFAULT true,
            
            -- Tax and Legal
            tax_information JSONB DEFAULT '{}',
            legal_agreements JSONB DEFAULT '[]',
            compliance_status VARCHAR(50) DEFAULT 'pending',
            
            -- Goals and Projections
            monthly_goal DECIMAL(12,2),
            yearly_goal DECIMAL(15,2),
            projected_earnings JSONB DEFAULT '{}',
            
            last_payout_date TIMESTAMP WITH TIME ZONE,
            next_payout_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(creator_id)
        );
        
        -- Indexes for financial queries
        CREATE INDEX IF NOT EXISTS idx_monetization_creator ON creator_monetization(creator_id);
        CREATE INDEX IF NOT EXISTS idx_monetization_revenue_model ON creator_monetization(revenue_model);
        CREATE INDEX IF NOT EXISTS idx_monetization_payout_date ON creator_monetization(next_payout_date);
        CREATE INDEX IF NOT EXISTS idx_monetization_earnings ON creator_monetization(total_lifetime_earnings);
        
        -- JSONB indexes for analytics
        CREATE INDEX IF NOT EXISTS idx_monetization_platform_earnings ON creator_monetization USING GIN(platform_earnings);
        CREATE INDEX IF NOT EXISTS idx_monetization_content_pricing ON creator_monetization USING GIN(content_pricing);
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.SCHEMA,
            priority=MigrationPriority.HIGH,
            description="Create creator monetization tracking and configuration table"
        )
    
    async def create_creator_analytics_table(self) -> str:
        """
        Create creator analytics and performance tracking table
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        CREATE TABLE IF NOT EXISTS creator_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            creator_id UUID NOT NULL REFERENCES creator_profiles(id) ON DELETE CASCADE,
            
            -- Time Period
            analytics_date DATE NOT NULL,
            period_type VARCHAR(20) DEFAULT 'daily' CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly')),
            
            -- Content Metrics
            content_uploaded INTEGER DEFAULT 0,
            content_views BIGINT DEFAULT 0,
            content_likes BIGINT DEFAULT 0,
            content_shares BIGINT DEFAULT 0,
            content_comments BIGINT DEFAULT 0,
            content_downloads BIGINT DEFAULT 0,
            
            -- Audience Metrics
            new_followers INTEGER DEFAULT 0,
            total_followers BIGINT DEFAULT 0,
            follower_growth_rate DECIMAL(5,2) DEFAULT 0.00,
            audience_engagement_rate DECIMAL(5,2) DEFAULT 0.00,
            
            -- Revenue Metrics
            revenue_generated DECIMAL(12,2) DEFAULT 0.00,
            revenue_per_content DECIMAL(10,2) DEFAULT 0.00,
            revenue_per_follower DECIMAL(8,4) DEFAULT 0.00,
            
            -- Platform Performance
            platform_metrics JSONB DEFAULT '{}',
            cross_platform_reach BIGINT DEFAULT 0,
            
            -- Content Protection Metrics
            protection_scans INTEGER DEFAULT 0,
            violations_detected INTEGER DEFAULT 0,
            violations_resolved INTEGER DEFAULT 0,
            protection_effectiveness DECIMAL(5,2) DEFAULT 0.00,
            
            -- Collaboration Metrics
            collaboration_requests_received INTEGER DEFAULT 0,
            collaboration_requests_sent INTEGER DEFAULT 0,
            active_collaborations INTEGER DEFAULT 0,
            completed_collaborations INTEGER DEFAULT 0,
            
            -- Quality Scores
            content_quality_score DECIMAL(5,2) DEFAULT 0.00,
            creator_reputation_score DECIMAL(5,2) DEFAULT 0.00,
            platform_ranking INTEGER,
            
            -- Detailed Analytics
            geographic_reach JSONB DEFAULT '{}',
            demographic_breakdown JSONB DEFAULT '{}',
            content_performance_by_type JSONB DEFAULT '{}',
            peak_activity_times JSONB DEFAULT '{}',
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(creator_id, analytics_date, period_type)
        );
        
        -- Time-series indexes for analytics queries
        CREATE INDEX IF NOT EXISTS idx_analytics_creator_date ON creator_analytics(creator_id, analytics_date);
        CREATE INDEX IF NOT EXISTS idx_analytics_period ON creator_analytics(period_type, analytics_date);
        CREATE INDEX IF NOT EXISTS idx_analytics_revenue ON creator_analytics(revenue_generated DESC);
        CREATE INDEX IF NOT EXISTS idx_analytics_engagement ON creator_analytics(audience_engagement_rate DESC);
        CREATE INDEX IF NOT EXISTS idx_analytics_growth ON creator_analytics(follower_growth_rate DESC);
        
        -- JSONB indexes for detailed analytics
        CREATE INDEX IF NOT EXISTS idx_analytics_platform_metrics ON creator_analytics USING GIN(platform_metrics);
        CREATE INDEX IF NOT EXISTS idx_analytics_geographic ON creator_analytics USING GIN(geographic_reach);
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.SCHEMA,
            priority=MigrationPriority.MEDIUM,
            description="Create creator analytics and performance tracking table"
        )
    
    async def execute_full_creator_migration(self, plan: CreatorMigrationPlan) -> List[str]:
        """
        Execute complete creator database migration according to business requirements
        
        Args:
            plan: CreatorMigrationPlan with specific configuration
            
        Returns:
            List[str]: Migration IDs for tracking
        """
        migration_ids = []
        
        try:
            self.logger.info("Starting comprehensive creator database migration")
            
            # Core creator tables
            migration_ids.append(await self.create_creator_profiles_table())
            migration_ids.append(await self.create_content_types_table())
            
            # Optional modules based on plan
            if plan.enable_collaboration:
                migration_ids.append(await self.create_creator_collaborations_table())
            
            if plan.enable_monetization:
                migration_ids.append(await self.create_creator_monetization_table())
            
            if plan.enable_analytics:
                migration_ids.append(await self.create_creator_analytics_table())
            
            self.logger.info(f"Creator migration completed successfully. Migration IDs: {migration_ids}")
            return migration_ids
            
        except Exception as e:
            self.logger.error(f"Creator migration failed: {str(e)}")
            raise
    
    async def add_creator_type_specific_constraints(self) -> str:
        """
        Add creator type-specific database constraints and validations
        
        Returns:
            str: Migration ID for tracking
        """
        migration_sql = """
        -- Creator type-specific constraints
        ALTER TABLE creator_profiles 
        ADD CONSTRAINT chk_musician_requirements 
        CHECK (
            creator_type != 'musician' OR 
            (genres IS NOT NULL AND jsonb_array_length(genres) > 0)
        );
        
        ALTER TABLE creator_profiles 
        ADD CONSTRAINT chk_photographer_requirements 
        CHECK (
            creator_type != 'photographer' OR 
            (equipment IS NOT NULL AND equipment ? 'camera_type')
        );
        
        ALTER TABLE creator_profiles 
        ADD CONSTRAINT chk_influencer_requirements 
        CHECK (
            creator_type != 'influencer' OR 
            (platform_accounts IS NOT NULL AND jsonb_array_length(jsonb_object_keys(platform_accounts)) > 0)
        );
        
        -- Content format validation based on creator type
        ALTER TABLE creator_content_types
        ADD CONSTRAINT chk_format_creator_compatibility
        CHECK (
            (content_format = 'audio' AND EXISTS (
                SELECT 1 FROM creator_profiles cp 
                WHERE cp.id = creator_id 
                AND cp.creator_type IN ('musician', 'podcaster', 'comedian')
            )) OR
            (content_format = 'video' AND EXISTS (
                SELECT 1 FROM creator_profiles cp 
                WHERE cp.id = creator_id 
                AND cp.creator_type IN ('video_creator', 'influencer', 'comedian')
            )) OR
            (content_format = 'image' AND EXISTS (
                SELECT 1 FROM creator_profiles cp 
                WHERE cp.id = creator_id 
                AND cp.creator_type IN ('photographer', 'artist', 'influencer')
            )) OR
            (content_format = 'text' AND EXISTS (
                SELECT 1 FROM creator_profiles cp 
                WHERE cp.id = creator_id 
                AND cp.creator_type IN ('blogger', 'influencer')
            )) OR
            content_format IN ('mixed_media', 'live_stream')
        );
        """



        
        return await self.migration_manager.execute_migration(
            migration_sql,
            migration_type=MigrationType.CONSTRAINT,
            priority=MigrationPriority.MEDIUM,
            description="Add creator type-specific constraints and validations"
        )
