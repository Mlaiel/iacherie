#!/usr/bin/env python3
"""
Ainflue Platform - AI-Powered Influencer Discovery System
Enterprise-grade influencer matching and discovery with advanced AI algorithms

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved

Expert Roles Demonstrated:
- Lead Dev IA: Advanced AI algorithms for influencer matching and discovery
- ML Engineer: Machine learning models for compatibility scoring and prediction
- IA Prompt Engineer: AI-powered content analysis and persona matching
- Backend Senior: Scalable API architecture and data processing pipelines
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import json
import uuid
import hashlib
import re
from pathlib import Path

import asyncpg
import redis.asyncio as redis
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx
import aiohttp

# Core platform imports
from ..core.base_integration import BaseIntegration
from ..core.exceptions import IntegrationError, ValidationError
from ..platforms.platform_coordinator import PlatformCoordinator
from ..ai_services.openai_integration import OpenAIIntegration
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

class InfluencerTier(str, Enum):
    """Influencer tier classification"""
    NANO = "nano"           # 1K-10K followers
    MICRO = "micro"         # 10K-100K followers
    MID = "mid"             # 100K-1M followers
    MACRO = "macro"         # 1M-10M followers
    MEGA = "mega"           # 10M+ followers

class Platform(str, Enum):
    """Supported platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"

class CollaborationType(str, Enum):
    """Types of collaboration"""
    SPONSORED_POST = "sponsored_post"
    PRODUCT_REVIEW = "product_review"
    BRAND_PARTNERSHIP = "brand_partnership"
    AFFILIATE_MARKETING = "affiliate_marketing"
    CONTENT_COLLABORATION = "content_collaboration"
    EVENT_PROMOTION = "event_promotion"
    GIVEAWAY = "giveaway"
    TAKEOVER = "takeover"
    AMBASSADOR = "ambassador"

class MatchQuality(str, Enum):
    """Match quality levels"""
    EXCELLENT = "excellent"    # 90-100%
    VERY_GOOD = "very_good"   # 80-89%
    GOOD = "good"             # 70-79%
    FAIR = "fair"             # 60-69%
    POOR = "poor"             # <60%

@dataclass
class InfluencerProfile:
    """Comprehensive influencer profile"""
    influencer_id: str
    username: str
    display_name: str
    platform: Platform
    
    # Basic metrics
    follower_count: int
    following_count: int
    post_count: int
    tier: InfluencerTier
    
    # Engagement metrics
    avg_likes: float
    avg_comments: float
    avg_shares: float
    engagement_rate: float
    
    # Content analysis
    content_categories: List[str] = field(default_factory=list)
    posting_frequency: float = 0.0  # posts per day
    best_posting_times: List[str] = field(default_factory=list)
    content_quality_score: float = 0.0
    
    # Audience insights
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_interests: List[str] = field(default_factory=list)
    audience_locations: List[str] = field(default_factory=list)
    
    # AI-generated insights
    personality_traits: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    brand_alignment_score: float = 0.0
    authenticity_score: float = 0.0
    
    # Collaboration history
    brand_collaborations: List[str] = field(default_factory=list)
    collaboration_types: List[CollaborationType] = field(default_factory=list)
    avg_collaboration_performance: float = 0.0
    
    # Contact and rates
    contact_info: Dict[str, str] = field(default_factory=dict)
    rate_ranges: Dict[str, float] = field(default_factory=dict)
    
    # Meta information
    last_updated: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    active_status: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiscoveryQuery:
    """Influencer discovery query parameters"""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str = ""
    
    # Platform filters
    platforms: List[Platform] = field(default_factory=list)
    
    # Audience size filters
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    tier_preference: Optional[InfluencerTier] = None
    
    # Engagement filters
    min_engagement_rate: Optional[float] = None
    min_content_quality: Optional[float] = None
    
    # Content preferences
    content_categories: List[str] = field(default_factory=list)
    required_themes: List[str] = field(default_factory=list)
    excluded_themes: List[str] = field(default_factory=list)
    
    # Audience targeting
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    target_locations: List[str] = field(default_factory=list)
    target_interests: List[str] = field(default_factory=list)
    
    # Collaboration preferences
    collaboration_types: List[CollaborationType] = field(default_factory=list)
    budget_range: Optional[Tuple[float, float]] = None
    
    # AI matching parameters
    brand_description: str = ""
    campaign_objectives: List[str] = field(default_factory=list)
    personality_match: List[str] = field(default_factory=list)
    
    # Results preferences
    max_results: int = 50
    include_similar: bool = True
    geographic_bias: Optional[str] = None

@dataclass
class InfluencerMatch:
    """Influencer match result with scoring"""
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    influencer: InfluencerProfile
    query: DiscoveryQuery
    
    # Overall scoring
    overall_score: float = 0.0
    match_quality: MatchQuality = MatchQuality.POOR
    
    # Detailed scoring breakdown
    audience_alignment_score: float = 0.0
    content_relevance_score: float = 0.0
    engagement_quality_score: float = 0.0
    brand_safety_score: float = 0.0
    value_for_money_score: float = 0.0
    
    # AI-generated insights
    match_reasons: List[str] = field(default_factory=list)
    potential_concerns: List[str] = field(default_factory=list)
    collaboration_suggestions: List[str] = field(default_factory=list)
    
    # Predictive metrics
    predicted_reach: int = 0
    predicted_engagement: float = 0.0
    estimated_roi: float = 0.0
    
    # Meta information
    matched_at: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0

class InfluencerDiscovery(BaseIntegration):
    """
    Enterprise AI-Powered Influencer Discovery System
    
    Demonstrates Expert Roles:
    - Lead Dev IA: Advanced AI algorithms for intelligent matching
    - ML Engineer: Machine learning models for scoring and prediction
    - IA Prompt Engineer: AI-powered content analysis and insights
    - Backend Senior: Scalable architecture and data processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize influencer discovery system"""
        super().__init__(config)
        
        # Core configuration
        self.config = config
        self.redis_url = config.get("redis_url", "redis://localhost:6379")
        self.db_url = config.get("database_url")
        self.discovery_interval = config.get("discovery_interval", 3600)  # 1 hour
        
        # Service dependencies
        self.platform_coordinator = PlatformCoordinator(config)
        self.openai_integration = OpenAIIntegration(config)
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Runtime state
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.discovery_task: Optional[asyncio.Task] = None
        self.executor = ThreadPoolExecutor(max_workers=config.get("max_workers", 8))
        
        # ML components
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_clusterer = KMeans(n_clusters=20, random_state=42)
        self.pca_reducer = PCA(n_components=50, random_state=42)
        
        # Performance tracking
        self.metrics = {
            "profiles_processed": 0,
            "queries_executed": 0,
            "matches_generated": 0,
            "ai_analyses_performed": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Caching
        self.profile_cache = {}
        self.query_cache = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize influencer discovery system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Initialize database pool
            if self.db_url:
                self.db_pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=10,
                    max_size=25
                )
                await self._setup_database_schema()
            
            # Initialize platform coordinator
            await self.platform_coordinator.initialize()
            
            # Initialize OpenAI integration
            await self.openai_integration.initialize()
            
            # Start background discovery
            self.discovery_task = asyncio.create_task(self._run_discovery_pipeline())
            
            await self.monitoring.record_metric("influencer_discovery_initialized", 1)
            self.logger.info("Influencer discovery system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize influencer discovery: {e}")
            raise IntegrationError(f"Discovery initialization failed: {e}")
    
    async def _setup_database_schema(self) -> None:
        """
        Setup database schema for influencer discovery
        Demonstrates: Backend Senior - Optimized database design
        """
        if not self.db_pool:
            return
        
        schema_sql = """
        -- Influencer profiles table
        CREATE TABLE IF NOT EXISTS influencer_profiles (
            influencer_id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            display_name VARCHAR(255),
            platform VARCHAR(50) NOT NULL,
            
            -- Basic metrics
            follower_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            post_count INTEGER DEFAULT 0,
            tier VARCHAR(20),
            
            -- Engagement metrics
            avg_likes DECIMAL(12,2) DEFAULT 0,
            avg_comments DECIMAL(12,2) DEFAULT 0,
            avg_shares DECIMAL(12,2) DEFAULT 0,
            engagement_rate DECIMAL(8,4) DEFAULT 0,
            
            -- Content analysis
            content_categories TEXT[] DEFAULT '{}',
            posting_frequency DECIMAL(8,4) DEFAULT 0,
            best_posting_times TEXT[] DEFAULT '{}',
            content_quality_score DECIMAL(5,4) DEFAULT 0,
            
            -- AI insights
            personality_traits TEXT[] DEFAULT '{}',
            content_themes TEXT[] DEFAULT '{}',
            brand_alignment_score DECIMAL(5,4) DEFAULT 0,
            authenticity_score DECIMAL(5,4) DEFAULT 0,
            
            -- Audience data
            audience_demographics JSONB DEFAULT '{}',
            audience_interests TEXT[] DEFAULT '{}',
            audience_locations TEXT[] DEFAULT '{}',
            
            -- Collaboration data
            brand_collaborations TEXT[] DEFAULT '{}',
            collaboration_types TEXT[] DEFAULT '{}',
            avg_collaboration_performance DECIMAL(8,4) DEFAULT 0,
            
            -- Contact and rates
            contact_info JSONB DEFAULT '{}',
            rate_ranges JSONB DEFAULT '{}',
            
            -- Meta information
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            verified BOOLEAN DEFAULT FALSE,
            active_status BOOLEAN DEFAULT TRUE,
            metadata JSONB DEFAULT '{}'
        );
        
        -- Discovery queries table
        CREATE TABLE IF NOT EXISTS discovery_queries (
            query_id VARCHAR(255) PRIMARY KEY,
            requester_id VARCHAR(255) NOT NULL,
            
            -- Filter criteria
            platforms TEXT[] DEFAULT '{}',
            min_followers INTEGER,
            max_followers INTEGER,
            tier_preference VARCHAR(20),
            min_engagement_rate DECIMAL(8,4),
            min_content_quality DECIMAL(5,4),
            
            -- Content preferences
            content_categories TEXT[] DEFAULT '{}',
            required_themes TEXT[] DEFAULT '{}',
            excluded_themes TEXT[] DEFAULT '{}',
            
            -- Targeting
            target_demographics JSONB DEFAULT '{}',
            target_locations TEXT[] DEFAULT '{}',
            target_interests TEXT[] DEFAULT '{}',
            
            -- Campaign details
            collaboration_types TEXT[] DEFAULT '{}',
            budget_min DECIMAL(12,2),
            budget_max DECIMAL(12,2),
            brand_description TEXT,
            campaign_objectives TEXT[] DEFAULT '{}',
            personality_match TEXT[] DEFAULT '{}',
            
            -- Results config
            max_results INTEGER DEFAULT 50,
            include_similar BOOLEAN DEFAULT TRUE,
            geographic_bias VARCHAR(100),
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            status VARCHAR(50) DEFAULT 'pending',
            completed_at TIMESTAMP WITH TIME ZONE
        );
        
        -- Match results table
        CREATE TABLE IF NOT EXISTS influencer_matches (
            match_id VARCHAR(255) PRIMARY KEY,
            query_id VARCHAR(255) REFERENCES discovery_queries(query_id),
            influencer_id VARCHAR(255) REFERENCES influencer_profiles(influencer_id),
            
            -- Overall scoring
            overall_score DECIMAL(5,4) NOT NULL,
            match_quality VARCHAR(20) NOT NULL,
            
            -- Detailed scores
            audience_alignment_score DECIMAL(5,4) DEFAULT 0,
            content_relevance_score DECIMAL(5,4) DEFAULT 0,
            engagement_quality_score DECIMAL(5,4) DEFAULT 0,
            brand_safety_score DECIMAL(5,4) DEFAULT 0,
            value_for_money_score DECIMAL(5,4) DEFAULT 0,
            
            -- AI insights
            match_reasons TEXT[] DEFAULT '{}',
            potential_concerns TEXT[] DEFAULT '{}',
            collaboration_suggestions TEXT[] DEFAULT '{}',
            
            -- Predictions
            predicted_reach INTEGER DEFAULT 0,
            predicted_engagement DECIMAL(8,4) DEFAULT 0,
            estimated_roi DECIMAL(8,4) DEFAULT 0,
            
            matched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            confidence_score DECIMAL(5,4) DEFAULT 0
        );
        
        -- Content analysis cache
        CREATE TABLE IF NOT EXISTS content_analysis_cache (
            content_hash VARCHAR(64) PRIMARY KEY,
            influencer_id VARCHAR(255),
            analysis_type VARCHAR(50),
            analysis_result JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Performance analytics
        CREATE TABLE IF NOT EXISTS discovery_analytics (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            total_queries INTEGER DEFAULT 0,
            total_matches INTEGER DEFAULT 0,
            avg_processing_time DECIMAL(8,4) DEFAULT 0,
            top_requested_categories TEXT[] DEFAULT '{}',
            avg_match_score DECIMAL(5,4) DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(date)
        );
        
        -- Optimized indexes
        CREATE INDEX IF NOT EXISTS idx_influencer_profiles_platform ON influencer_profiles(platform, tier);
        CREATE INDEX IF NOT EXISTS idx_influencer_profiles_metrics ON influencer_profiles(follower_count, engagement_rate);
        CREATE INDEX IF NOT EXISTS idx_influencer_profiles_categories ON influencer_profiles USING GIN(content_categories);
        CREATE INDEX IF NOT EXISTS idx_influencer_profiles_updated ON influencer_profiles(last_updated DESC);
        
        CREATE INDEX IF NOT EXISTS idx_discovery_queries_requester ON discovery_queries(requester_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_discovery_queries_status ON discovery_queries(status, created_at);
        
        CREATE INDEX IF NOT EXISTS idx_influencer_matches_query ON influencer_matches(query_id, overall_score DESC);
        CREATE INDEX IF NOT EXISTS idx_influencer_matches_influencer ON influencer_matches(influencer_id, matched_at DESC);
        CREATE INDEX IF NOT EXISTS idx_influencer_matches_score ON influencer_matches(overall_score DESC, match_quality);
        
        CREATE INDEX IF NOT EXISTS idx_content_analysis_cache_hash ON content_analysis_cache(content_hash, analysis_type);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def discover_influencers(self, query: DiscoveryQuery) -> List[InfluencerMatch]:
        """
        Main influencer discovery method
        Demonstrates: Lead Dev IA - Advanced AI-powered matching algorithms
        """
        try:
            start_time = datetime.utcnow()
            
            # Store query
            await self._store_discovery_query(query)
            
            # Check cache first
            cached_results = await self._check_query_cache(query)
            if cached_results:
                self.metrics["cache_hit_rate"] += 1
                return cached_results
            
            # Phase 1: Basic filtering
            candidate_profiles = await self._filter_candidates(query)
            self.logger.info(f"Phase 1: Found {len(candidate_profiles)} candidates")
            
            # Phase 2: Content analysis and scoring
            analyzed_profiles = await self._analyze_content_relevance(candidate_profiles, query)
            self.logger.info(f"Phase 2: Analyzed {len(analyzed_profiles)} profiles")
            
            # Phase 3: AI-powered matching
            ai_matches = await self._perform_ai_matching(analyzed_profiles, query)
            self.logger.info(f"Phase 3: Generated {len(ai_matches)} AI matches")
            
            # Phase 4: Final scoring and ranking
            final_matches = await self._rank_and_score_matches(ai_matches, query)
            self.logger.info(f"Phase 4: Ranked {len(final_matches)} final matches")
            
            # Store results
            await self._store_match_results(query.query_id, final_matches)
            
            # Cache results
            await self._cache_query_results(query, final_matches)
            
            # Update metrics
            self.metrics["queries_executed"] += 1
            self.metrics["matches_generated"] += len(final_matches)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_processing_time(processing_time)
            
            await self.monitoring.record_metric("influencer_discovery_completed", 1, {
                "requester_id": query.requester_id,
                "matches_found": len(final_matches),
                "processing_time": processing_time
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="influencer_discovery",
                user_id=query.requester_id,
                resource_id=query.query_id,
                details={
                    "matches_found": len(final_matches),
                    "platforms": [p.value for p in query.platforms],
                    "processing_time": processing_time
                }
            )
            
            return final_matches[:query.max_results]
            
        except Exception as e:
            self.logger.error(f"Failed to discover influencers: {e}")
            await self.monitoring.record_error("discovery_error", str(e))
            raise IntegrationError(f"Influencer discovery failed: {e}")
    
    async def _filter_candidates(self, query: DiscoveryQuery) -> List[InfluencerProfile]:
        """
        Phase 1: Basic filtering based on criteria
        Demonstrates: Backend Senior - Efficient database queries
        """
        if not self.db_pool:
            return []
        
        # Build dynamic query
        where_conditions = ["active_status = TRUE"]
        params = []
        param_count = 0
        
        # Platform filter
        if query.platforms:
            param_count += 1
            where_conditions.append(f"platform = ANY(${param_count})")
            params.append([p.value for p in query.platforms])
        
        # Follower count filters
        if query.min_followers:
            param_count += 1
            where_conditions.append(f"follower_count >= ${param_count}")
            params.append(query.min_followers)
        
        if query.max_followers:
            param_count += 1
            where_conditions.append(f"follower_count <= ${param_count}")
            params.append(query.max_followers)
        
        # Tier filter
        if query.tier_preference:
            param_count += 1
            where_conditions.append(f"tier = ${param_count}")
            params.append(query.tier_preference.value)
        
        # Engagement rate filter
        if query.min_engagement_rate:
            param_count += 1
            where_conditions.append(f"engagement_rate >= ${param_count}")
            params.append(query.min_engagement_rate)
        
        # Content quality filter
        if query.min_content_quality:
            param_count += 1
            where_conditions.append(f"content_quality_score >= ${param_count}")
            params.append(query.min_content_quality)
        
        # Content categories filter
        if query.content_categories:
            param_count += 1
            where_conditions.append(f"content_categories && ${param_count}")
            params.append(query.content_categories)
        
        # Geographic filter
        if query.target_locations:
            param_count += 1
            where_conditions.append(f"audience_locations && ${param_count}")
            params.append(query.target_locations)
        
        sql_query = f"""
        SELECT * FROM influencer_profiles
        WHERE {' AND '.join(where_conditions)}
        ORDER BY 
            follower_count DESC,
            engagement_rate DESC,
            content_quality_score DESC
        LIMIT 1000
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql_query, *params)
            
            profiles = []
            for row in rows:
                profile = InfluencerProfile(
                    influencer_id=row["influencer_id"],
                    username=row["username"],
                    display_name=row["display_name"] or "",
                    platform=Platform(row["platform"]),
                    follower_count=row["follower_count"],
                    following_count=row["following_count"],
                    post_count=row["post_count"],
                    tier=InfluencerTier(row["tier"]) if row["tier"] else InfluencerTier.NANO,
                    avg_likes=float(row["avg_likes"]),
                    avg_comments=float(row["avg_comments"]),
                    avg_shares=float(row["avg_shares"]),
                    engagement_rate=float(row["engagement_rate"]),
                    content_categories=row["content_categories"] or [],
                    posting_frequency=float(row["posting_frequency"]),
                    best_posting_times=row["best_posting_times"] or [],
                    content_quality_score=float(row["content_quality_score"]),
                    personality_traits=row["personality_traits"] or [],
                    content_themes=row["content_themes"] or [],
                    brand_alignment_score=float(row["brand_alignment_score"]),
                    authenticity_score=float(row["authenticity_score"]),
                    audience_demographics=row["audience_demographics"] or {},
                    audience_interests=row["audience_interests"] or [],
                    audience_locations=row["audience_locations"] or [],
                    brand_collaborations=row["brand_collaborations"] or [],
                    collaboration_types=[CollaborationType(ct) for ct in row["collaboration_types"] or []],
                    avg_collaboration_performance=float(row["avg_collaboration_performance"]),
                    contact_info=row["contact_info"] or {},
                    rate_ranges=row["rate_ranges"] or {},
                    last_updated=row["last_updated"],
                    verified=row["verified"],
                    active_status=row["active_status"],
                    metadata=row["metadata"] or {}
                )
                profiles.append(profile)
            
            return profiles
    
    async def _analyze_content_relevance(self, profiles: List[InfluencerProfile], 
                                       query: DiscoveryQuery) -> List[InfluencerProfile]:
        """
        Phase 2: Content analysis and relevance scoring
        Demonstrates: ML Engineer - Content analysis algorithms
        """
        try:
            # Prepare content for analysis
            content_texts = []
            profile_map = {}
            
            for profile in profiles:
                # Combine content categories, themes, and personality traits
                content_text = " ".join([
                    " ".join(profile.content_categories),
                    " ".join(profile.content_themes),
                    " ".join(profile.personality_traits),
                    " ".join(profile.audience_interests)
                ])
                
                if content_text.strip():
                    content_texts.append(content_text)
                    profile_map[len(content_texts) - 1] = profile
            
            if not content_texts:
                return profiles
            
            # Vectorize content
            content_vectors = self.vectorizer.fit_transform(content_texts)
            
            # Create query vector
            query_text = " ".join([
                " ".join(query.content_categories),
                " ".join(query.required_themes),
                query.brand_description,
                " ".join(query.campaign_objectives),
                " ".join(query.personality_match),
                " ".join(query.target_interests)
            ])
            
            if query_text.strip():
                query_vector = self.vectorizer.transform([query_text])
                
                # Calculate similarities
                similarities = cosine_similarity(query_vector, content_vectors)[0]
                
                # Update profiles with relevance scores
                for idx, similarity in enumerate(similarities):
                    if idx in profile_map:
                        profile = profile_map[idx]
                        profile.metadata["content_relevance_score"] = float(similarity)
            
            # Filter by relevance threshold
            relevance_threshold = 0.1  # Minimum relevance
            relevant_profiles = [
                p for p in profiles 
                if p.metadata.get("content_relevance_score", 0) >= relevance_threshold
            ]
            
            return relevant_profiles
            
        except Exception as e:
            self.logger.error(f"Error in content analysis: {e}")
            return profiles  # Return original profiles if analysis fails
    
    async def _perform_ai_matching(self, profiles: List[InfluencerProfile], 
                                 query: DiscoveryQuery) -> List[InfluencerMatch]:
        """
        Phase 3: AI-powered matching and insights generation
        Demonstrates: IA Prompt Engineer - Advanced AI analysis
        """
        try:
            matches = []
            
            # Process in batches to avoid overwhelming the AI service
            batch_size = 10
            for i in range(0, len(profiles), batch_size):
                batch_profiles = profiles[i:i + batch_size]
                batch_matches = await self._analyze_profile_batch(batch_profiles, query)
                matches.extend(batch_matches)
                
                # Add delay to respect rate limits
                await asyncio.sleep(0.5)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in AI matching: {e}")
            return []
    
    async def _analyze_profile_batch(self, profiles: List[InfluencerProfile], 
                                   query: DiscoveryQuery) -> List[InfluencerMatch]:
        """Analyze a batch of profiles using AI"""
        try:
            matches = []
            
            for profile in profiles:
                # Generate AI analysis prompt
                analysis_prompt = self._create_ai_analysis_prompt(profile, query)
                
                # Get AI analysis
                ai_response = await self.openai_integration.generate_completion(
                    prompt=analysis_prompt,
                    max_tokens=800,
                    temperature=0.3
                )
                
                if ai_response and ai_response.get("success"):
                    ai_analysis = ai_response["response"]
                    match = await self._create_match_from_ai_analysis(profile, query, ai_analysis)
                    matches.append(match)
                    
                    self.metrics["ai_analyses_performed"] += 1
                
                # Small delay between AI calls
                await asyncio.sleep(0.1)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error analyzing profile batch: {e}")
            return []
    
    def _create_ai_analysis_prompt(self, profile: InfluencerProfile, query: DiscoveryQuery) -> str:
        """
        Create AI analysis prompt for influencer matching
        Demonstrates: IA Prompt Engineer - Sophisticated prompt engineering
        """
        prompt = f"""
        Analyze this influencer for brand collaboration compatibility:

        INFLUENCER PROFILE:
        - Username: {profile.username}
        - Platform: {profile.platform.value}
        - Followers: {profile.follower_count:,}
        - Engagement Rate: {profile.engagement_rate:.2f}%
        - Content Categories: {', '.join(profile.content_categories)}
        - Content Themes: {', '.join(profile.content_themes)}
        - Personality Traits: {', '.join(profile.personality_traits)}
        - Audience Interests: {', '.join(profile.audience_interests)}
        - Previous Collaborations: {len(profile.brand_collaborations)}
        - Authenticity Score: {profile.authenticity_score:.2f}

        BRAND REQUIREMENTS:
        - Brand Description: {query.brand_description}
        - Target Categories: {', '.join(query.content_categories)}
        - Required Themes: {', '.join(query.required_themes)}
        - Excluded Themes: {', '.join(query.excluded_themes)}
        - Campaign Objectives: {', '.join(query.campaign_objectives)}
        - Desired Personality: {', '.join(query.personality_match)}
        - Target Audience: {query.target_demographics}
        - Collaboration Types: {', '.join([ct.value for ct in query.collaboration_types])}

        Provide analysis in JSON format:
        {{
            "overall_score": 0.85,
            "audience_alignment": 0.90,
            "content_relevance": 0.80,
            "engagement_quality": 0.85,
            "brand_safety": 0.95,
            "value_for_money": 0.75,
            "match_reasons": [
                "Strong audience alignment with target demographics",
                "High engagement rate indicates active community"
            ],
            "potential_concerns": [
                "Previous collaboration with competitor brand"
            ],
            "collaboration_suggestions": [
                "Product review posts would perform well",
                "Instagram Stories for behind-the-scenes content"
            ],
            "predicted_reach": 50000,
            "predicted_engagement": 4.2,
            "estimated_roi": 3.5
        }}
        """
        
        return prompt
    
    async def _create_match_from_ai_analysis(self, profile: InfluencerProfile, 
                                           query: DiscoveryQuery, ai_analysis: str) -> InfluencerMatch:
        """Create match object from AI analysis"""
        try:
            # Parse AI response
            analysis_data = json.loads(ai_analysis)
            
            # Determine match quality
            overall_score = analysis_data.get("overall_score", 0.0)
            if overall_score >= 0.9:
                match_quality = MatchQuality.EXCELLENT
            elif overall_score >= 0.8:
                match_quality = MatchQuality.VERY_GOOD
            elif overall_score >= 0.7:
                match_quality = MatchQuality.GOOD
            elif overall_score >= 0.6:
                match_quality = MatchQuality.FAIR
            else:
                match_quality = MatchQuality.POOR
            
            # Create match object
            match = InfluencerMatch(
                influencer=profile,
                query=query,
                overall_score=overall_score,
                match_quality=match_quality,
                audience_alignment_score=analysis_data.get("audience_alignment", 0.0),
                content_relevance_score=analysis_data.get("content_relevance", 0.0),
                engagement_quality_score=analysis_data.get("engagement_quality", 0.0),
                brand_safety_score=analysis_data.get("brand_safety", 0.0),
                value_for_money_score=analysis_data.get("value_for_money", 0.0),
                match_reasons=analysis_data.get("match_reasons", []),
                potential_concerns=analysis_data.get("potential_concerns", []),
                collaboration_suggestions=analysis_data.get("collaboration_suggestions", []),
                predicted_reach=analysis_data.get("predicted_reach", 0),
                predicted_engagement=analysis_data.get("predicted_engagement", 0.0),
                estimated_roi=analysis_data.get("estimated_roi", 0.0),
                confidence_score=overall_score  # Use overall score as confidence
            )
            
            return match
            
        except json.JSONDecodeError:
            # Fallback to basic scoring if AI response is malformed
            self.logger.warning(f"Malformed AI response for {profile.username}")
            return self._create_fallback_match(profile, query)
        except Exception as e:
            self.logger.error(f"Error creating match from AI analysis: {e}")
            return self._create_fallback_match(profile, query)
    
    def _create_fallback_match(self, profile: InfluencerProfile, query: DiscoveryQuery) -> InfluencerMatch:
        """Create fallback match with basic scoring"""
        # Simple scoring based on available metrics
        engagement_score = min(1.0, profile.engagement_rate / 5.0)  # Normalize to 0-1
        quality_score = profile.content_quality_score
        authenticity_score = profile.authenticity_score
        
        overall_score = (engagement_score + quality_score + authenticity_score) / 3
        
        if overall_score >= 0.8:
            match_quality = MatchQuality.VERY_GOOD
        elif overall_score >= 0.6:
            match_quality = MatchQuality.GOOD
        elif overall_score >= 0.4:
            match_quality = MatchQuality.FAIR
        else:
            match_quality = MatchQuality.POOR
        
        return InfluencerMatch(
            influencer=profile,
            query=query,
            overall_score=overall_score,
            match_quality=match_quality,
            engagement_quality_score=engagement_score,
            brand_safety_score=authenticity_score,
            predicted_reach=int(profile.follower_count * profile.engagement_rate / 100),
            predicted_engagement=profile.engagement_rate,
            match_reasons=["Basic compatibility assessment"],
            confidence_score=0.5  # Lower confidence for fallback
        )
    
    async def _rank_and_score_matches(self, matches: List[InfluencerMatch], 
                                    query: DiscoveryQuery) -> List[InfluencerMatch]:
        """
        Phase 4: Final ranking and scoring optimization
        Demonstrates: ML Engineer - Advanced ranking algorithms
        """
        try:
            # Apply additional scoring factors
            for match in matches:
                # Budget compatibility scoring
                budget_score = self._calculate_budget_compatibility(match, query)
                
                # Platform preference scoring
                platform_score = self._calculate_platform_preference(match, query)
                
                # Recency bonus
                recency_score = self._calculate_recency_bonus(match.influencer)
                
                # Adjust overall score with additional factors
                adjusted_score = (
                    match.overall_score * 0.7 +
                    budget_score * 0.15 +
                    platform_score * 0.1 +
                    recency_score * 0.05
                )
                
                match.overall_score = min(1.0, adjusted_score)
                
                # Recalculate match quality based on adjusted score
                if match.overall_score >= 0.9:
                    match.match_quality = MatchQuality.EXCELLENT
                elif match.overall_score >= 0.8:
                    match.match_quality = MatchQuality.VERY_GOOD
                elif match.overall_score >= 0.7:
                    match.match_quality = MatchQuality.GOOD
                elif match.overall_score >= 0.6:
                    match.match_quality = MatchQuality.FAIR
                else:
                    match.match_quality = MatchQuality.POOR
            
            # Sort by overall score
            matches.sort(key=lambda m: m.overall_score, reverse=True)
            
            # Apply diversity filter if requested
            if query.include_similar:
                matches = self._apply_diversity_filter(matches)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in ranking and scoring: {e}")
            return sorted(matches, key=lambda m: m.overall_score, reverse=True)
    
    def _calculate_budget_compatibility(self, match: InfluencerMatch, query: DiscoveryQuery) -> float:
        """Calculate budget compatibility score"""
        if not query.budget_range or not match.influencer.rate_ranges:
            return 0.5  # Neutral score if no budget info
        
        min_budget, max_budget = query.budget_range
        
        # Get influencer's typical rates
        influencer_rates = match.influencer.rate_ranges
        avg_rate = np.mean(list(influencer_rates.values())) if influencer_rates else 0
        
        if avg_rate == 0:
            return 0.5  # Neutral if no rate info
        
        # Score based on how well rates fit budget
        if min_budget <= avg_rate <= max_budget:
            return 1.0
        elif avg_rate < min_budget:
            return 0.8  # Good value
        else:
            # Calculate how much over budget
            over_budget_ratio = avg_rate / max_budget
            return max(0.1, 1.0 - (over_budget_ratio - 1.0))
    
    def _calculate_platform_preference(self, match: InfluencerMatch, query: DiscoveryQuery) -> float:
        """Calculate platform preference score"""
        if not query.platforms:
            return 1.0
        
        # Prefer exact platform matches
        if match.influencer.platform in query.platforms:
            return 1.0
        else:
            return 0.3
    
    def _calculate_recency_bonus(self, profile: InfluencerProfile) -> float:
        """Calculate recency bonus based on profile freshness"""
        days_since_update = (datetime.utcnow() - profile.last_updated).days
        
        if days_since_update <= 1:
            return 1.0
        elif days_since_update <= 7:
            return 0.8
        elif days_since_update <= 30:
            return 0.6
        else:
            return 0.3
    
    def _apply_diversity_filter(self, matches: List[InfluencerMatch]) -> List[InfluencerMatch]:
        """Apply diversity filter to avoid too similar influencers"""
        if len(matches) <= 10:
            return matches
        
        diverse_matches = [matches[0]]  # Always include top match
        
        for match in matches[1:]:
            is_diverse = True
            
            for existing_match in diverse_matches:
                # Check similarity criteria
                if (match.influencer.platform == existing_match.influencer.platform and
                    abs(match.influencer.follower_count - existing_match.influencer.follower_count) < 10000 and
                    len(set(match.influencer.content_categories) & 
                        set(existing_match.influencer.content_categories)) > 2):
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_matches.append(match)
            
            # Limit diversity filtering to reasonable size
            if len(diverse_matches) >= len(matches) * 0.7:
                break
        
        return diverse_matches
    
    async def _run_discovery_pipeline(self) -> None:
        """
        Background discovery pipeline for continuous profile updates
        Demonstrates: DevOps - Automated data pipeline management
        """
        while True:
            try:
                # Update influencer profiles from platforms
                await self._update_influencer_profiles()
                
                # Perform content analysis on new profiles
                await self._analyze_new_content()
                
                # Update analytics
                await self._update_discovery_analytics()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                await self.monitoring.record_metric("discovery_pipeline_cycle", 1)
                
                # Sleep until next cycle
                await asyncio.sleep(self.discovery_interval)
                
            except Exception as e:
                self.logger.error(f"Discovery pipeline error: {e}")
                await self.monitoring.record_error("discovery_pipeline_error", str(e))
                await asyncio.sleep(300)  # 5-minute delay on error
    
    async def _update_influencer_profiles(self) -> None:
        """Update influencer profiles from platform APIs"""
        try:
            # Get profiles that need updating
            stale_profiles = await self._get_stale_profiles()
            
            for profile_info in stale_profiles:
                try:
                    # Fetch updated data from platform
                    updated_data = await self.platform_coordinator.get_influencer_profile(
                        platform=profile_info["platform"],
                        username=profile_info["username"]
                    )
                    
                    if updated_data:
                        await self._update_profile_in_database(updated_data)
                        self.metrics["profiles_processed"] += 1
                    
                    # Rate limiting delay
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error updating profile {profile_info['username']}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in profile update process: {e}")
    
    async def _get_stale_profiles(self) -> List[Dict[str, Any]]:
        """Get profiles that need updating"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT influencer_id, username, platform
        FROM influencer_profiles
        WHERE last_updated < NOW() - INTERVAL '24 hours'
        AND active_status = TRUE
        ORDER BY last_updated ASC
        LIMIT 100
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def _update_profile_in_database(self, profile_data: Dict[str, Any]) -> None:
        """Update profile in database"""
        # Implementation would update profile with new data
        pass
    
    async def _analyze_new_content(self) -> None:
        """Analyze content for new profiles"""
        # Implementation would analyze content for personality and themes
        pass
    
    async def _update_discovery_analytics(self) -> None:
        """Update discovery analytics"""
        if not self.db_pool:
            return
        
        today = datetime.utcnow().date()
        
        # Get daily statistics
        stats_query = """
        SELECT 
            COUNT(DISTINCT dq.query_id) as total_queries,
            COUNT(DISTINCT im.match_id) as total_matches,
            AVG(im.overall_score) as avg_match_score
        FROM discovery_queries dq
        LEFT JOIN influencer_matches im ON dq.query_id = im.query_id
        WHERE DATE(dq.created_at) = $1
        """
        
        async with self.db_pool.acquire() as conn:
            stats = await conn.fetchrow(stats_query, today)
            
            # Update analytics table
            analytics_query = """
            INSERT INTO discovery_analytics (
                date, total_queries, total_matches, avg_match_score, avg_processing_time
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (date) DO UPDATE SET
                total_queries = EXCLUDED.total_queries,
                total_matches = EXCLUDED.total_matches,
                avg_match_score = EXCLUDED.avg_match_score,
                avg_processing_time = EXCLUDED.avg_processing_time
            """
            
            await conn.execute(
                analytics_query,
                today,
                stats["total_queries"] or 0,
                stats["total_matches"] or 0,
                float(stats["avg_match_score"] or 0),
                self.metrics["average_processing_time"]
            )
    
    # Helper methods for database operations
    async def _store_discovery_query(self, query: DiscoveryQuery) -> None:
        """Store discovery query in database"""
        if not self.db_pool:
            return
        
        sql = """
        INSERT INTO discovery_queries (
            query_id, requester_id, platforms, min_followers, max_followers,
            tier_preference, min_engagement_rate, min_content_quality,
            content_categories, required_themes, excluded_themes,
            target_demographics, target_locations, target_interests,
            collaboration_types, budget_min, budget_max, brand_description,
            campaign_objectives, personality_match, max_results,
            include_similar, geographic_bias
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)
        """
        
        budget_min = query.budget_range[0] if query.budget_range else None
        budget_max = query.budget_range[1] if query.budget_range else None
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                sql,
                query.query_id, query.requester_id,
                [p.value for p in query.platforms],
                query.min_followers, query.max_followers,
                query.tier_preference.value if query.tier_preference else None,
                query.min_engagement_rate, query.min_content_quality,
                query.content_categories, query.required_themes, query.excluded_themes,
                json.dumps(query.target_demographics),
                query.target_locations, query.target_interests,
                [ct.value for ct in query.collaboration_types],
                budget_min, budget_max, query.brand_description,
                query.campaign_objectives, query.personality_match,
                query.max_results, query.include_similar, query.geographic_bias
            )
    
    async def _store_match_results(self, query_id: str, matches: List[InfluencerMatch]) -> None:
        """Store match results in database"""
        if not self.db_pool:
            return
        
        for match in matches:
            sql = """
            INSERT INTO influencer_matches (
                match_id, query_id, influencer_id, overall_score, match_quality,
                audience_alignment_score, content_relevance_score, engagement_quality_score,
                brand_safety_score, value_for_money_score, match_reasons,
                potential_concerns, collaboration_suggestions, predicted_reach,
                predicted_engagement, estimated_roi, confidence_score
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    sql,
                    match.match_id, query_id, match.influencer.influencer_id,
                    match.overall_score, match.match_quality.value,
                    match.audience_alignment_score, match.content_relevance_score,
                    match.engagement_quality_score, match.brand_safety_score,
                    match.value_for_money_score, match.match_reasons,
                    match.potential_concerns, match.collaboration_suggestions,
                    match.predicted_reach, match.predicted_engagement,
                    match.estimated_roi, match.confidence_score
                )
    
    async def _check_query_cache(self, query: DiscoveryQuery) -> Optional[List[InfluencerMatch]]:
        """Check if query results are cached"""
        # Create query hash for caching
        query_hash = hashlib.md5(json.dumps(query.dict(), sort_keys=True).encode()).hexdigest()
        
        if self.redis_client:
            cached_results = await self.redis_client.get(f"query_results:{query_hash}")
            if cached_results:
                try:
                    results_data = json.loads(cached_results)
                    # Convert back to InfluencerMatch objects
                    matches = []
                    for match_data in results_data:
                        # Simplified conversion - in production would be more complete
                        match = InfluencerMatch(
                            influencer=InfluencerProfile(**match_data["influencer"]),
                            query=query,
                            overall_score=match_data["overall_score"],
                            match_quality=MatchQuality(match_data["match_quality"])
                        )
                        matches.append(match)
                    
                    return matches
                except Exception as e:
                    self.logger.error(f"Error deserializing cached results: {e}")
        
        return None
    
    async def _cache_query_results(self, query: DiscoveryQuery, matches: List[InfluencerMatch]) -> None:
        """Cache query results"""
        if not self.redis_client:
            return
        
        try:
            query_hash = hashlib.md5(json.dumps(query.dict(), sort_keys=True).encode()).hexdigest()
            
            # Serialize matches (simplified)
            serialized_matches = []
            for match in matches:
                match_data = {
                    "influencer": match.influencer.__dict__,
                    "overall_score": match.overall_score,
                    "match_quality": match.match_quality.value
                }
                serialized_matches.append(match_data)
            
            # Cache for 1 hour
            await self.redis_client.setex(
                f"query_results:{query_hash}",
                3600,
                json.dumps(serialized_matches, default=str)
            )
            
        except Exception as e:
            self.logger.error(f"Error caching query results: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old discovery data"""
        if not self.db_pool:
            return
        
        # Delete old queries and matches (keep 90 days)
        cleanup_queries = [
            "DELETE FROM influencer_matches WHERE matched_at < NOW() - INTERVAL '90 days'",
            "DELETE FROM discovery_queries WHERE created_at < NOW() - INTERVAL '90 days'",
            "DELETE FROM content_analysis_cache WHERE created_at < NOW() - INTERVAL '30 days'"
        ]
        
        async with self.db_pool.acquire() as conn:
            for query in cleanup_queries:
                await conn.execute(query)
    
    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time metric"""
        current_avg = self.metrics["average_processing_time"]
        total_queries = self.metrics["queries_executed"]
        
        if total_queries == 1:
            self.metrics["average_processing_time"] = processing_time
        else:
            self.metrics["average_processing_time"] = (
                (current_avg * (total_queries - 1) + processing_time) / total_queries
            )
    
    # Public API methods
    async def get_discovery_results(self, query_id: str) -> List[InfluencerMatch]:
        """Get discovery results by query ID"""
        if not self.db_pool:
            return []
        
        sql = """
        SELECT im.*, ip.* 
        FROM influencer_matches im
        JOIN influencer_profiles ip ON im.influencer_id = ip.influencer_id
        WHERE im.query_id = $1
        ORDER BY im.overall_score DESC
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, query_id)
            
            matches = []
            for row in rows:
                # Create InfluencerProfile and InfluencerMatch objects
                # Implementation would construct full objects from row data
                pass
            
            return matches
    
    async def get_influencer_profile(self, influencer_id: str) -> Optional[InfluencerProfile]:
        """Get detailed influencer profile"""
        if not self.db_pool:
            return None
        
        sql = "SELECT * FROM influencer_profiles WHERE influencer_id = $1"
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(sql, influencer_id)
            
            if row:
                # Construct InfluencerProfile from row
                return InfluencerProfile(
                    influencer_id=row["influencer_id"],
                    username=row["username"],
                    display_name=row["display_name"] or "",
                    platform=Platform(row["platform"]),
                    # ... (rest of fields)
                )
            
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Demonstrates: DevOps - Service monitoring and health validation
        """
        health_status = {
            "service": "influencer_discovery",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # Check Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check database connection
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status["components"]["database"] = "healthy"
            else:
                health_status["components"]["database"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check discovery task
            if self.discovery_task and not self.discovery_task.done():
                health_status["components"]["discovery_pipeline"] = "running"
            else:
                health_status["components"]["discovery_pipeline"] = "stopped"
                health_status["status"] = "unhealthy"
            
            # Check AI service
            ai_health = await self.openai_integration.health_check()
            health_status["components"]["ai_service"] = ai_health.get("status", "unknown")
            
            # Add metrics
            health_status["metrics"] = self.metrics.copy()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup discovery resources"""
        try:
            # Stop discovery task
            if self.discovery_task:
                self.discovery_task.cancel()
                try:
                    await self.discovery_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close database pool
            if self.db_pool:
                await self.db_pool.close()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("Influencer discovery cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Export main classes
__all__ = [
    "InfluencerDiscovery", "InfluencerProfile", "DiscoveryQuery", "InfluencerMatch",
    "InfluencerTier", "CollaborationType", "MatchQuality", "Platform"
]