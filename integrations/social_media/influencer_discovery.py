"""AI-Powered Influencer Discovery System
=========================================

Enterprise-grade AI-powered influencer identification and analysis system
supporting multi-platform discovery, authenticity verification, and 
collaboration matching for the Ainflue platform.

This module provides intelligent influencer discovery, engagement analysis,
audience verification, brand alignment scoring, and collaboration 
recommendation using advanced machine learning algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import statistics
import math
import re

import httpx
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from textblob import TextBlob
import networkx as nx
from transformers import pipeline, AutoTokenizer, AutoModel
import torch


class SocialPlatform(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"


class InfluencerTier(Enum):
    """Influencer tiers based on follower count."""
    NANO = "nano"           # 1K - 10K followers
    MICRO = "micro"         # 10K - 100K followers
    MID = "mid"             # 100K - 1M followers
    MACRO = "macro"         # 1M - 10M followers
    MEGA = "mega"           # 10M+ followers


class NicheCategory(Enum):
    """Content niche categories."""
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    GAMING = "gaming"
    MUSIC = "music"
    ART = "art"
    EDUCATION = "education"
    BUSINESS = "business"
    HEALTH = "health"
    PARENTING = "parenting"
    PETS = "pets"
    HOME_DECOR = "home_decor"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"


class VerificationStatus(Enum):
    """Influencer verification status."""
    VERIFIED = "verified"
    PENDING = "pending"
    FLAGGED = "flagged"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass
class AudienceDemographics:
    """Audience demographic information."""
    age_distribution: Dict[str, float] = field(default_factory=dict)  # age ranges -> percentages
    gender_distribution: Dict[str, float] = field(default_factory=dict)  # gender -> percentages
    location_distribution: Dict[str, float] = field(default_factory=dict)  # countries/cities -> percentages
    interests: List[str] = field(default_factory=list)
    languages: Dict[str, float] = field(default_factory=dict)  # language -> percentage
    income_level: Optional[str] = None  # low, medium, high
    education_level: Optional[str] = None  # high_school, college, graduate
    total_audience_size: int = 0


@dataclass
class EngagementMetrics:
    """Influencer engagement metrics."""
    followers_count: int = 0
    following_count: int = 0
    total_posts: int = 0
    
    # Engagement rates
    average_likes_per_post: float = 0.0
    average_comments_per_post: float = 0.0
    average_shares_per_post: float = 0.0
    average_saves_per_post: float = 0.0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    like_to_comment_ratio: float = 0.0
    follower_growth_rate: float = 0.0  # monthly
    posting_frequency: float = 0.0  # posts per week
    
    # Quality indicators
    authentic_engagement_score: float = 0.0  # 0-100
    bot_likelihood_score: float = 0.0  # 0-100 (higher = more likely bots)
    
    # Time-based metrics
    peak_activity_hours: List[int] = field(default_factory=list)
    most_active_days: List[str] = field(default_factory=list)


@dataclass
class ContentAnalysis:
    """Content analysis for influencer."""
    primary_niche: NicheCategory
    secondary_niches: List[NicheCategory] = field(default_factory=list)
    
    # Content quality
    content_quality_score: float = 0.0  # 0-100
    visual_consistency_score: float = 0.0  # 0-100
    caption_quality_score: float = 0.0  # 0-100
    
    # Content characteristics
    average_caption_length: int = 0
    hashtag_usage_pattern: Dict[str, int] = field(default_factory=dict)
    most_common_hashtags: List[str] = field(default_factory=list)
    content_types: Dict[str, float] = field(default_factory=dict)  # post type -> percentage
    
    # Language and sentiment
    primary_language: str = "en"
    sentiment_distribution: Dict[str, float] = field(default_factory=dict)  # positive, negative, neutral
    
    # Brand mentions and collaborations
    brand_mentions: List[str] = field(default_factory=list)
    sponsored_content_frequency: float = 0.0  # percentage of sponsored posts
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Influencer:
    """Comprehensive influencer profile."""
    id: str
    username: str
    display_name: str
    platform: SocialPlatform
    
    # Basic info
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    
    # Verification and authenticity
    verification_status: VerificationStatus = VerificationStatus.UNKNOWN
    authenticity_score: float = 0.0  # 0-100
    fake_follower_percentage: float = 0.0
    
    # Tier and category
    tier: InfluencerTier = InfluencerTier.NANO
    niche: NicheCategory = NicheCategory.LIFESTYLE
    
    # Metrics
    engagement_metrics: EngagementMetrics = field(default_factory=EngagementMetrics)
    audience_demographics: AudienceDemographics = field(default_factory=AudienceeDemographics)
    content_analysis: ContentAnalysis = field(default_factory=ContentAnalysis)
    
    # Scoring
    influence_score: float = 0.0  # 0-100 overall influence score
    brand_safety_score: float = 0.0  # 0-100 brand safety rating
    collaboration_score: float = 0.0  # 0-100 collaboration potential
    
    # Contact and rates
    contact_email: Optional[str] = None
    rate_per_post: Optional[Decimal] = None
    rate_per_story: Optional[Decimal] = None
    rate_per_video: Optional[Decimal] = None
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_analyzed: datetime = field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    time_zone: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchCriteria:
    """Influencer search criteria."""
    platforms: List[SocialPlatform] = field(default_factory=list)
    niches: List[NicheCategory] = field(default_factory=list)
    tiers: List[InfluencerTier] = field(default_factory=list)
    
    # Follower requirements
    min_followers: int = 1000
    max_followers: int = 10000000
    
    # Engagement requirements
    min_engagement_rate: float = 1.0
    min_authenticity_score: float = 70.0
    max_fake_follower_percentage: float = 20.0
    
    # Demographics
    target_locations: List[str] = field(default_factory=list)
    target_age_ranges: List[str] = field(default_factory=list)
    target_genders: List[str] = field(default_factory=list)
    
    # Content requirements
    min_content_quality_score: float = 60.0
    min_brand_safety_score: float = 80.0
    languages: List[str] = field(default_factory=list)
    
    # Collaboration
    budget_range: Tuple[Decimal, Decimal] = (Decimal('100'), Decimal('10000'))
    collaboration_type: str = "post"  # post, story, video, campaign
    
    # Search parameters
    max_results: int = 100
    sort_by: str = "influence_score"  # influence_score, engagement_rate, followers
    keywords: List[str] = field(default_factory=list)


@dataclass
class CollaborationMatch:
    """Influencer-brand collaboration match."""
    influencer_id: str
    brand_id: str
    match_score: float  # 0-100
    
    # Match factors
    niche_alignment: float = 0.0
    audience_alignment: float = 0.0
    engagement_quality: float = 0.0
    brand_safety: float = 0.0
    budget_fit: float = 0.0
    
    # Predicted outcomes
    predicted_reach: int = 0
    predicted_engagement: int = 0
    predicted_conversions: int = 0
    expected_roi: float = 0.0
    
    # Recommendations
    recommended_content_type: str = "post"
    recommended_campaign_duration: int = 7  # days
    optimal_posting_times: List[datetime] = field(default_factory=list)
    
    # Match metadata
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


class AIInfluencerDiscoverySystem:
    """Enterprise AI-powered influencer discovery and analysis system."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize influencer discovery system.
        
        Args:
            config: Configuration dict with API credentials and ML model settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Platform API clients
        self.platform_clients: Dict[SocialPlatform, httpx.AsyncClient] = {}
        
        # AI/ML models
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_classifier = None
        self.authenticity_detector = None
        self.sentiment_analyzer = None
        self.scaler = StandardScaler()
        
        # Hugging Face models
        self.nlp_model = None
        self.tokenizer = None
        
        # Data storage
        self.discovered_influencers: Dict[str, Influencer] = {}
        self.search_cache: Dict[str, List[Influencer]] = {}
        self.collaboration_matches: List[CollaborationMatch] = []
        
        # Analytics and insights
        self.niche_trends: Dict[NicheCategory, Dict[str, Any]] = {}
        self.platform_insights: Dict[SocialPlatform, Dict[str, Any]] = {}
        
        # Discovery stats
        self.discovery_stats = {
            'total_influencers_discovered': 0,
            'total_searches_performed': 0,
            'average_match_score': 0.0,
            'top_performing_niche': None,
            'discovery_accuracy': 0.0,
            'last_model_update': None
        }
        
        self._initialize_platform_clients()
        self._initialize_ai_models()
    
    def _initialize_platform_clients(self) -> None:
        """Initialize social media platform API clients."""
        try:
            # Instagram Business API
            if 'instagram' in self.config:
                instagram_config = self.config['instagram']
                self.platform_clients[SocialPlatform.INSTAGRAM] = httpx.AsyncClient(
                    base_url='https://graph.facebook.com/v18.0',
                    headers={'Authorization': f'Bearer {instagram_config.get("access_token")}'},
                    timeout=60
                )
                self.logger.info("Instagram API client initialized for influencer discovery")
            
            # TikTok Business API
            if 'tiktok' in self.config:
                tiktok_config = self.config['tiktok']
                self.platform_clients[SocialPlatform.TIKTOK] = httpx.AsyncClient(
                    base_url='https://business-api.tiktok.com/open_api/v1.3',
                    headers={'Access-Token': tiktok_config.get("access_token")},
                    timeout=60
                )
                self.logger.info("TikTok API client initialized for influencer discovery")
            
            # YouTube Data API
            if 'youtube' in self.config:
                youtube_config = self.config['youtube']
                self.platform_clients[SocialPlatform.YOUTUBE] = httpx.AsyncClient(
                    base_url='https://www.googleapis.com/youtube/v3',
                    headers={'Authorization': f'Bearer {youtube_config.get("access_token")}'},
                    timeout=60
                )
                self.logger.info("YouTube API client initialized for influencer discovery")
            
            # Twitter API v2
            if 'twitter' in self.config:
                twitter_config = self.config['twitter']
                self.platform_clients[SocialPlatform.TWITTER] = httpx.AsyncClient(
                    base_url='https://api.twitter.com/2',
                    headers={'Authorization': f'Bearer {twitter_config.get("bearer_token")}'},
                    timeout=60
                )
                self.logger.info("Twitter API client initialized for influencer discovery")
                
        except Exception as e:
            self.logger.error(f"Error initializing platform clients: {e}")
            raise
    
    def _initialize_ai_models(self) -> None:
        """Initialize AI/ML models for influencer analysis."""
        try:
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize content classification
            self.content_classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize embeddings model for semantic similarity
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.nlp_model = AutoModel.from_pretrained(model_name)
            
            self.logger.info("AI/ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AI models: {e}")
            # Fallback to basic models
            self.sentiment_analyzer = None
            self.content_classifier = None
    
    async def discover_influencers(
        self,
        search_criteria: SearchCriteria,
        use_ai_scoring: bool = True
    ) -> List[Influencer]:
        """Discover influencers based on search criteria.
        
        Args:
            search_criteria: Search parameters and requirements
            use_ai_scoring: Whether to use AI for advanced scoring
            
        Returns:
            List of discovered influencers matching criteria
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(search_criteria)
            if cache_key in self.search_cache:
                self.logger.info(f"Returning cached results for search: {len(self.search_cache[cache_key])} influencers")
                return self.search_cache[cache_key]
            
            discovered_influencers = []
            
            # Search across specified platforms
            for platform in search_criteria.platforms:
                platform_influencers = await self._search_platform_influencers(
                    platform, search_criteria
                )
                discovered_influencers.extend(platform_influencers)
            
            # If no platforms specified, search all available
            if not search_criteria.platforms:
                for platform in self.platform_clients.keys():
                    platform_influencers = await self._search_platform_influencers(
                        platform, search_criteria
                    )
                    discovered_influencers.extend(platform_influencers)
            
            # Remove duplicates (same influencer on multiple platforms)
            unique_influencers = self._deduplicate_influencers(discovered_influencers)
            
            # AI-powered analysis and scoring
            if use_ai_scoring:
                for influencer in unique_influencers:
                    await self._analyze_influencer_with_ai(influencer)
            
            # Filter based on criteria
            filtered_influencers = self._filter_influencers(unique_influencers, search_criteria)
            
            # Sort by specified criteria
            sorted_influencers = self._sort_influencers(filtered_influencers, search_criteria.sort_by)
            
            # Limit results
            final_results = sorted_influencers[:search_criteria.max_results]
            
            # Cache results
            self.search_cache[cache_key] = final_results
            
            # Update stats
            self.discovery_stats['total_influencers_discovered'] += len(final_results)
            self.discovery_stats['total_searches_performed'] += 1
            
            self.logger.info(
                f"Discovered {len(final_results)} influencers matching criteria "
                f"(from {len(discovered_influencers)} initial candidates)"
            )
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error discovering influencers: {e}")
            raise
    
    async def _search_platform_influencers(
        self,
        platform: SocialPlatform,
        search_criteria: SearchCriteria
    ) -> List[Influencer]:
        """Search for influencers on specific platform.
        
        Args:
            platform: Social media platform
            search_criteria: Search criteria
            
        Returns:
            List of influencers found on platform
        """
        try:
            if platform == SocialPlatform.INSTAGRAM:
                return await self._search_instagram_influencers(search_criteria)
            elif platform == SocialPlatform.YOUTUBE:
                return await self._search_youtube_influencers(search_criteria)
            elif platform == SocialPlatform.TWITTER:
                return await self._search_twitter_influencers(search_criteria)
            elif platform == SocialPlatform.TIKTOK:
                return await self._search_tiktok_influencers(search_criteria)
            else:
                self.logger.warning(f"Search not implemented for platform: {platform.value}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching {platform.value} influencers: {e}")
            return []
    
    async def _search_instagram_influencers(
        self,
        search_criteria: SearchCriteria
    ) -> List[Influencer]:
        """Search for influencers on Instagram."""
        influencers = []
        
        try:
            client = self.platform_clients.get(SocialPlatform.INSTAGRAM)
            if not client:
                return influencers
            
            # Search using hashtags related to niches
            for niche in search_criteria.niches:
                hashtags = self._get_niche_hashtags(niche)
                
                for hashtag in hashtags[:3]:  # Limit hashtag searches
                    try:
                        # Search hashtag for recent posts
                        response = await client.get(
                            f"/ig_hashtag_search",
                            params={
                                'user_id': self.config['instagram']['page_id'],
                                'q': hashtag,
                                'access_token': self.config['instagram']['access_token']
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            for hashtag_data in data.get('data', []):
                                hashtag_id = hashtag_data.get('id')
                                
                                # Get recent media for hashtag
                                media_response = await client.get(
                                    f"/{hashtag_id}/recent_media",
                                    params={
                                        'user_id': self.config['instagram']['page_id'],
                                        'fields': 'id,caption,media_type,media_url,permalink,timestamp,username',
                                        'access_token': self.config['instagram']['access_token']
                                    }
                                )
                                
                                if media_response.status_code == 200:
                                    media_data = media_response.json()
                                    
                                    # Extract unique users
                                    users = set()
                                    for media in media_data.get('data', []):
                                        if 'username' in media:
                                            users.add(media['username'])
                                    
                                    # Analyze each user
                                    for username in list(users)[:10]:  # Limit users per hashtag
                                        try:
                                            influencer = await self._analyze_instagram_user(username)
                                            if influencer:
                                                influencers.append(influencer)
                                        except:
                                            continue  # Skip if user analysis fails
                                            
                    except Exception as e:
                        self.logger.warning(f"Error searching hashtag {hashtag}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error searching Instagram influencers: {e}")
        
        return influencers
    
    async def _analyze_instagram_user(self, username: str) -> Optional[Influencer]:
        """Analyze Instagram user to create influencer profile.
        
        Args:
            username: Instagram username
            
        Returns:
            Influencer profile or None if not suitable
        """
        try:
            client = self.platform_clients.get(SocialPlatform.INSTAGRAM)
            if not client:
                return None
            
            # This would require Instagram Basic Display API or Business API
            # For demonstration, we'll create a mock profile
            
            # In real implementation, you would:
            # 1. Get user info (followers, following, bio, etc.)
            # 2. Analyze recent posts for engagement metrics
            # 3. Extract audience demographics
            # 4. Analyze content for niche classification
            
            # Mock influencer for demonstration
            influencer = Influencer(
                id=f"ig_{username}_{uuid.uuid4().hex[:8]}",
                username=username,
                display_name=username.title(),
                platform=SocialPlatform.INSTAGRAM,
                bio=f"Lifestyle and fashion influencer | {username}",
                tier=InfluencerTier.MICRO,
                niche=NicheCategory.LIFESTYLE
            )
            
            # Mock engagement metrics
            influencer.engagement_metrics = EngagementMetrics(
                followers_count=np.random.randint(10000, 100000),
                following_count=np.random.randint(500, 2000),
                total_posts=np.random.randint(100, 1000),
                average_likes_per_post=np.random.uniform(500, 5000),
                average_comments_per_post=np.random.uniform(50, 200),
                engagement_rate=np.random.uniform(2.0, 8.0),
                authentic_engagement_score=np.random.uniform(70, 95),
                bot_likelihood_score=np.random.uniform(5, 25)
            )
            
            # Mock audience demographics
            influencer.audience_demographics = AudienceeDemographics(
                age_distribution={
                    "18-24": np.random.uniform(20, 40),
                    "25-34": np.random.uniform(30, 50),
                    "35-44": np.random.uniform(15, 25)
                },
                gender_distribution={
                    "female": np.random.uniform(60, 80),
                    "male": np.random.uniform(20, 40)
                },
                location_distribution={
                    "United States": np.random.uniform(40, 60),
                    "United Kingdom": np.random.uniform(10, 20),
                    "Canada": np.random.uniform(5, 15)
                }
            )
            
            # Calculate tier based on followers
            followers = influencer.engagement_metrics.followers_count
            if followers < 10000:
                influencer.tier = InfluencerTier.NANO
            elif followers < 100000:
                influencer.tier = InfluencerTier.MICRO
            elif followers < 1000000:
                influencer.tier = InfluencerTier.MID
            elif followers < 10000000:
                influencer.tier = InfluencerTier.MACRO
            else:
                influencer.tier = InfluencerTier.MEGA
            
            # Calculate influence score
            influencer.influence_score = self._calculate_influence_score(influencer)
            
            return influencer
            
        except Exception as e:
            self.logger.error(f"Error analyzing Instagram user {username}: {e}")
            return None
    
    async def _analyze_influencer_with_ai(self, influencer: Influencer) -> None:
        """Perform AI-powered analysis on influencer.
        
        Args:
            influencer: Influencer to analyze
        """
        try:
            # Analyze content niche using AI
            if influencer.bio:
                niche = await self._classify_content_niche(influencer.bio)
                if niche:
                    influencer.niche = niche
            
            # Analyze authenticity using AI models
            authenticity_score = await self._calculate_authenticity_score(influencer)
            influencer.authenticity_score = authenticity_score
            
            # Calculate brand safety score
            brand_safety_score = await self._calculate_brand_safety_score(influencer)
            influencer.brand_safety_score = brand_safety_score
            
            # Analyze content quality (if we had access to posts)
            content_quality_score = await self._analyze_content_quality(influencer)
            influencer.content_analysis.content_quality_score = content_quality_score
            
            # Update overall influence score
            influencer.influence_score = self._calculate_influence_score(influencer)
            
            self.logger.debug(f"AI analysis completed for {influencer.username}")
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis for {influencer.username}: {e}")
    
    async def _classify_content_niche(self, content: str) -> Optional[NicheCategory]:
        """Classify content niche using AI.
        
        Args:
            content: Content text to classify
            
        Returns:
            Classified niche category
        """
        try:
            if not self.content_classifier or not content:
                return None
            
            # Define niche labels for classification
            niche_labels = [
                "fashion and style",
                "beauty and cosmetics",
                "fitness and health",
                "food and cooking",
                "travel and lifestyle",
                "technology and gadgets",
                "gaming and entertainment",
                "music and arts",
                "education and learning",
                "business and entrepreneurship"
            ]
            
            # Use zero-shot classification
            result = self.content_classifier(content, niche_labels)
            
            if result and len(result['labels']) > 0:
                top_label = result['labels'][0]
                confidence = result['scores'][0]
                
                if confidence > 0.5:  # Only return if confidence is high enough
                    # Map to niche category
                    label_to_niche = {
                        "fashion and style": NicheCategory.FASHION,
                        "beauty and cosmetics": NicheCategory.BEAUTY,
                        "fitness and health": NicheCategory.FITNESS,
                        "food and cooking": NicheCategory.FOOD,
                        "travel and lifestyle": NicheCategory.TRAVEL,
                        "technology and gadgets": NicheCategory.TECHNOLOGY,
                        "gaming and entertainment": NicheCategory.GAMING,
                        "music and arts": NicheCategory.MUSIC,
                        "education and learning": NicheCategory.EDUCATION,
                        "business and entrepreneurship": NicheCategory.BUSINESS
                    }
                    
                    return label_to_niche.get(top_label, NicheCategory.LIFESTYLE)
            
            return NicheCategory.LIFESTYLE  # Default
            
        except Exception as e:
            self.logger.error(f"Error classifying content niche: {e}")
            return None
    
    async def _calculate_authenticity_score(self, influencer: Influencer) -> float:
        """Calculate influencer authenticity score using AI.
        
        Args:
            influencer: Influencer to analyze
            
        Returns:
            Authenticity score (0-100)
        """
        try:
            score = 0.0
            factors = []
            
            # Engagement rate factor (authentic influencers have reasonable engagement)
            engagement_rate = influencer.engagement_metrics.engagement_rate
            if 1.0 <= engagement_rate <= 10.0:  # Realistic range
                engagement_factor = min(engagement_rate / 5.0, 1.0) * 100
            else:
                engagement_factor = max(0, 100 - abs(engagement_rate - 5.0) * 10)
            factors.append(engagement_factor)
            
            # Follower-to-following ratio factor
            followers = influencer.engagement_metrics.followers_count
            following = influencer.engagement_metrics.following_count
            
            if following > 0:
                ratio = followers / following
                if ratio > 1.0:  # More followers than following is good
                    ratio_factor = min(math.log10(ratio) * 30, 100)
                else:
                    ratio_factor = max(0, 100 - (1.0 - ratio) * 50)
            else:
                ratio_factor = 50  # Neutral if no following data
            factors.append(ratio_factor)
            
            # Profile completeness factor
            completeness_factor = 0
            if influencer.bio:
                completeness_factor += 25
            if influencer.profile_image_url:
                completeness_factor += 25
            if influencer.website:
                completeness_factor += 25
            if influencer.location:
                completeness_factor += 25
            factors.append(completeness_factor)
            
            # Bot likelihood factor (inverted)
            bot_factor = max(0, 100 - influencer.engagement_metrics.bot_likelihood_score)
            factors.append(bot_factor)
            
            # Calculate weighted average
            score = statistics.mean(factors)
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating authenticity score: {e}")
            return 50.0  # Default neutral score
    
    async def _calculate_brand_safety_score(self, influencer: Influencer) -> float:
        """Calculate brand safety score for influencer.
        
        Args:
            influencer: Influencer to analyze
            
        Returns:
            Brand safety score (0-100)
        """
        try:
            score = 100.0  # Start with perfect score
            
            # Analyze bio for problematic content
            if influencer.bio and self.sentiment_analyzer:
                sentiment_result = self.sentiment_analyzer(influencer.bio)
                
                if sentiment_result:
                    label = sentiment_result[0]['label'].lower()
                    confidence = sentiment_result[0]['score']
                    
                    if 'negative' in label and confidence > 0.8:
                        score -= 20  # Reduce score for negative sentiment
            
            # Check for controversial keywords in bio
            if influencer.bio:
                controversial_keywords = [
                    'controversy', 'scandal', 'drama', 'hate', 'inappropriate',
                    'offensive', 'problematic', 'toxic', 'cancel'
                ]
                
                bio_lower = influencer.bio.lower()
                for keyword in controversial_keywords:
                    if keyword in bio_lower:
                        score -= 10
            
            # Verification status factor
            if influencer.verification_status == VerificationStatus.VERIFIED:
                score += 5
            elif influencer.verification_status == VerificationStatus.FLAGGED:
                score -= 30
            
            # Authenticity factor
            authenticity_penalty = max(0, (70 - influencer.authenticity_score) * 0.5)
            score -= authenticity_penalty
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating brand safety score: {e}")
            return 70.0  # Default safe score
    
    async def _analyze_content_quality(self, influencer: Influencer) -> float:
        """Analyze content quality score.
        
        Args:
            influencer: Influencer to analyze
            
        Returns:
            Content quality score (0-100)
        """
        try:
            # Since we don't have access to actual posts in this mock,
            # we'll calculate based on available metrics
            
            score = 50.0  # Base score
            
            # Engagement quality factor
            engagement_rate = influencer.engagement_metrics.engagement_rate
            if engagement_rate > 3.0:
                score += min((engagement_rate - 3.0) * 5, 25)
            
            # Posting frequency factor (consistent posting indicates quality)
            posting_freq = influencer.engagement_metrics.posting_frequency
            if 2 <= posting_freq <= 7:  # 2-7 posts per week is good
                score += 15
            
            # Bio quality factor
            if influencer.bio:
                bio_length = len(influencer.bio)
                if 50 <= bio_length <= 200:  # Good bio length
                    score += 10
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Error analyzing content quality: {e}")
            return 50.0
    
    def _calculate_influence_score(self, influencer: Influencer) -> float:
        """Calculate overall influence score.
        
        Args:
            influencer: Influencer to score
            
        Returns:
            Influence score (0-100)
        """
        try:
            factors = []
            
            # Follower count factor (logarithmic scale)
            followers = influencer.engagement_metrics.followers_count
            if followers > 0:
                follower_score = min(math.log10(followers) * 15, 50)
                factors.append(follower_score)
            
            # Engagement rate factor
            engagement_rate = influencer.engagement_metrics.engagement_rate
            engagement_score = min(engagement_rate * 8, 40)
            factors.append(engagement_score)
            
            # Authenticity factor
            factors.append(influencer.authenticity_score * 0.3)
            
            # Brand safety factor
            factors.append(influencer.brand_safety_score * 0.2)
            
            # Content quality factor
            content_quality = influencer.content_analysis.content_quality_score
            factors.append(content_quality * 0.3)
            
            # Calculate weighted average
            if factors:
                score = sum(factors) / len(factors)
            else:
                score = 0.0
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating influence score: {e}")
            return 0.0
    
    def _filter_influencers(
        self,
        influencers: List[Influencer],
        criteria: SearchCriteria
    ) -> List[Influencer]:
        """Filter influencers based on search criteria.
        
        Args:
            influencers: List of influencers to filter
            criteria: Search criteria
            
        Returns:
            Filtered list of influencers
        """
        filtered = []
        
        for influencer in influencers:
            # Check follower count
            followers = influencer.engagement_metrics.followers_count
            if not (criteria.min_followers <= followers <= criteria.max_followers):
                continue
            
            # Check engagement rate
            if influencer.engagement_metrics.engagement_rate < criteria.min_engagement_rate:
                continue
            
            # Check authenticity score
            if influencer.authenticity_score < criteria.min_authenticity_score:
                continue
            
            # Check fake follower percentage
            fake_percentage = influencer.engagement_metrics.bot_likelihood_score
            if fake_percentage > criteria.max_fake_follower_percentage:
                continue
            
            # Check niches
            if criteria.niches and influencer.niche not in criteria.niches:
                continue
            
            # Check tiers
            if criteria.tiers and influencer.tier not in criteria.tiers:
                continue
            
            # Check content quality
            if influencer.content_analysis.content_quality_score < criteria.min_content_quality_score:
                continue
            
            # Check brand safety
            if influencer.brand_safety_score < criteria.min_brand_safety_score:
                continue
            
            # Check budget (if rate information is available)
            if influencer.rate_per_post:
                min_budget, max_budget = criteria.budget_range
                if not (min_budget <= influencer.rate_per_post <= max_budget):
                    continue
            
            filtered.append(influencer)
        
        return filtered
    
    def _sort_influencers(
        self,
        influencers: List[Influencer],
        sort_by: str
    ) -> List[Influencer]:
        """Sort influencers by specified criteria.
        
        Args:
            influencers: List of influencers to sort
            sort_by: Sort criteria
            
        Returns:
            Sorted list of influencers
        """
        try:
            if sort_by == "influence_score":
                return sorted(influencers, key=lambda x: x.influence_score, reverse=True)
            elif sort_by == "engagement_rate":
                return sorted(influencers, key=lambda x: x.engagement_metrics.engagement_rate, reverse=True)
            elif sort_by == "followers":
                return sorted(influencers, key=lambda x: x.engagement_metrics.followers_count, reverse=True)
            elif sort_by == "authenticity_score":
                return sorted(influencers, key=lambda x: x.authenticity_score, reverse=True)
            elif sort_by == "brand_safety_score":
                return sorted(influencers, key=lambda x: x.brand_safety_score, reverse=True)
            else:
                return influencers
                
        except Exception as e:
            self.logger.error(f"Error sorting influencers: {e}")
            return influencers
    
    def _get_niche_hashtags(self, niche: NicheCategory) -> List[str]:
        """Get relevant hashtags for niche category.
        
        Args:
            niche: Niche category
            
        Returns:
            List of relevant hashtags
        """
        hashtag_map = {
            NicheCategory.FASHION: ["fashion", "style", "ootd", "fashionblogger", "streetstyle"],
            NicheCategory.BEAUTY: ["beauty", "makeup", "skincare", "beautyblogger", "cosmetics"],
            NicheCategory.FITNESS: ["fitness", "workout", "gym", "health", "fitnessmotivation"],
            NicheCategory.FOOD: ["food", "foodie", "cooking", "recipe", "foodblogger"],
            NicheCategory.TRAVEL: ["travel", "wanderlust", "adventure", "explore", "travelblogger"],
            NicheCategory.LIFESTYLE: ["lifestyle", "lifestyleblogger", "dailylife", "inspiration"],
            NicheCategory.TECHNOLOGY: ["tech", "technology", "gadgets", "innovation", "techreview"],
            NicheCategory.GAMING: ["gaming", "gamer", "videogames", "esports", "streaming"],
            NicheCategory.MUSIC: ["music", "musician", "song", "artist", "musiclover"],
            NicheCategory.ART: ["art", "artist", "creative", "artwork", "artoftheday"]
        }
        
        return hashtag_map.get(niche, ["lifestyle", "influencer"])
    
    def _generate_cache_key(self, criteria: SearchCriteria) -> str:
        """Generate cache key for search criteria.
        
        Args:
            criteria: Search criteria
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Create a string representation of key criteria
        key_data = {
            'platforms': [p.value for p in criteria.platforms],
            'niches': [n.value for n in criteria.niches],
            'tiers': [t.value for t in criteria.tiers],
            'min_followers': criteria.min_followers,
            'max_followers': criteria.max_followers,
            'min_engagement_rate': criteria.min_engagement_rate,
            'sort_by': criteria.sort_by
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _deduplicate_influencers(self, influencers: List[Influencer]) -> List[Influencer]:
        """Remove duplicate influencers based on username and platform.
        
        Args:
            influencers: List of influencers with potential duplicates
            
        Returns:
            Deduplicated list of influencers
        """
        seen = set()
        unique_influencers = []
        
        for influencer in influencers:
            key = (influencer.username.lower(), influencer.platform.value)
            if key not in seen:
                seen.add(key)
                unique_influencers.append(influencer)
        
        return unique_influencers
    
    async def find_collaboration_matches(
        self,
        brand_profile: Dict[str, Any],
        max_matches: int = 20
    ) -> List[CollaborationMatch]:
        """Find optimal influencer-brand collaboration matches.
        
        Args:
            brand_profile: Brand profile with preferences and requirements
            max_matches: Maximum number of matches to return
            
        Returns:
            List of collaboration matches sorted by score
        """
        try:
            matches = []
            
            # Extract brand criteria
            target_niches = brand_profile.get('target_niches', [])
            target_audience = brand_profile.get('target_audience', {})
            budget_range = brand_profile.get('budget_range', (100, 10000))
            campaign_goals = brand_profile.get('goals', ['awareness'])
            brand_values = brand_profile.get('values', [])
            
            # Search for suitable influencers
            search_criteria = SearchCriteria(
                niches=[NicheCategory(n) for n in target_niches if n in [nc.value for nc in NicheCategory]],
                budget_range=(Decimal(str(budget_range[0])), Decimal(str(budget_range[1]))),
                min_brand_safety_score=80.0,
                min_authenticity_score=75.0,
                max_results=100
            )
            
            influencers = await self.discover_influencers(search_criteria, use_ai_scoring=True)
            
            # Calculate match scores for each influencer
            for influencer in influencers:
                match_score = await self._calculate_collaboration_match_score(
                    influencer, brand_profile
                )
                
                if match_score > 60.0:  # Only consider good matches
                    collaboration_match = CollaborationMatch(
                        influencer_id=influencer.id,
                        brand_id=brand_profile.get('brand_id', 'unknown'),
                        match_score=match_score
                    )
                    
                    # Calculate detailed match factors
                    await self._calculate_detailed_match_factors(
                        collaboration_match, influencer, brand_profile
                    )
                    
                    matches.append(collaboration_match)
            
            # Sort by match score
            matches.sort(key=lambda x: x.match_score, reverse=True)
            
            # Store top matches
            self.collaboration_matches.extend(matches[:max_matches])
            
            self.logger.info(f"Found {len(matches)} collaboration matches for brand")
            
            return matches[:max_matches]
            
        except Exception as e:
            self.logger.error(f"Error finding collaboration matches: {e}")
            raise
    
    async def _calculate_collaboration_match_score(
        self,
        influencer: Influencer,
        brand_profile: Dict[str, Any]
    ) -> float:
        """Calculate collaboration match score between influencer and brand.
        
        Args:
            influencer: Influencer profile
            brand_profile: Brand profile
            
        Returns:
            Match score (0-100)
        """
        try:
            scores = []
            
            # Niche alignment
            target_niches = brand_profile.get('target_niches', [])
            if target_niches:
                if influencer.niche.value in target_niches:
                    niche_score = 100.0
                else:
                    # Check secondary niches
                    secondary_match = any(
                        sn.value in target_niches 
                        for sn in influencer.content_analysis.secondary_niches
                    )
                    niche_score = 70.0 if secondary_match else 30.0
            else:
                niche_score = 50.0  # Neutral if no niche preference
            scores.append(niche_score)
            
            # Audience alignment
            target_audience = brand_profile.get('target_audience', {})
            audience_score = self._calculate_audience_alignment(
                influencer.audience_demographics, target_audience
            )
            scores.append(audience_score)
            
            # Brand safety alignment
            min_brand_safety = brand_profile.get('min_brand_safety_score', 70.0)
            safety_score = min(100.0, (influencer.brand_safety_score / min_brand_safety) * 100)
            scores.append(safety_score)
            
            # Engagement quality
            engagement_score = min(100.0, influencer.engagement_metrics.engagement_rate * 15)
            scores.append(engagement_score)
            
            # Budget alignment
            budget_range = brand_profile.get('budget_range', (100, 10000))
            if influencer.rate_per_post:
                rate = float(influencer.rate_per_post)
                min_budget, max_budget = budget_range
                
                if min_budget <= rate <= max_budget:
                    budget_score = 100.0
                elif rate < min_budget:
                    budget_score = 80.0  # Cheaper is still good
                else:
                    # Penalize if too expensive
                    over_budget = (rate - max_budget) / max_budget
                    budget_score = max(0, 100 - over_budget * 50)
            else:
                budget_score = 50.0  # Neutral if no rate info
            scores.append(budget_score)
            
            # Calculate weighted average
            weights = [0.25, 0.25, 0.2, 0.15, 0.15]  # niche, audience, safety, engagement, budget
            
            if len(scores) == len(weights):
                match_score = sum(score * weight for score, weight in zip(scores, weights))
            else:
                match_score = statistics.mean(scores)
            
            return min(100.0, max(0.0, match_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating match score: {e}")
            return 0.0
    
    def _calculate_audience_alignment(
        self,
        influencer_audience: AudienceeDemographics,
        target_audience: Dict[str, Any]
    ) -> float:
        """Calculate audience alignment score.
        
        Args:
            influencer_audience: Influencer's audience demographics
            target_audience: Brand's target audience
            
        Returns:
            Alignment score (0-100)
        """
        try:
            scores = []
            
            # Age alignment
            target_ages = target_audience.get('age_ranges', [])
            if target_ages and influencer_audience.age_distribution:
                age_overlap = 0.0
                for age_range in target_ages:
                    age_overlap += influencer_audience.age_distribution.get(age_range, 0.0)
                
                age_score = min(100.0, age_overlap * 2)  # Scale to 0-100
                scores.append(age_score)
            
            # Gender alignment
            target_genders = target_audience.get('genders', [])
            if target_genders and influencer_audience.gender_distribution:
                gender_overlap = 0.0
                for gender in target_genders:
                    gender_overlap += influencer_audience.gender_distribution.get(gender.lower(), 0.0)
                
                gender_score = min(100.0, gender_overlap * 1.5)
                scores.append(gender_score)
            
            # Location alignment
            target_locations = target_audience.get('locations', [])
            if target_locations and influencer_audience.location_distribution:
                location_overlap = 0.0
                for location in target_locations:
                    # Check for exact match or partial match
                    for audience_location, percentage in influencer_audience.location_distribution.items():
                        if location.lower() in audience_location.lower() or audience_location.lower() in location.lower():
                            location_overlap += percentage
                
                location_score = min(100.0, location_overlap * 1.2)
                scores.append(location_score)
            
            # Return average if we have scores, otherwise neutral
            return statistics.mean(scores) if scores else 50.0
            
        except Exception as e:
            self.logger.error(f"Error calculating audience alignment: {e}")
            return 50.0
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get influencer discovery statistics."""
        return {
            **self.discovery_stats,
            'cached_searches': len(self.search_cache),
            'discovered_influencers_count': len(self.discovered_influencers),
            'collaboration_matches_count': len(self.collaboration_matches),
            'platforms_connected': len(self.platform_clients)
        }
    
    async def close(self) -> None:
        """Close platform connections and cleanup resources."""
        try:
            # Close platform clients
            for client in self.platform_clients.values():
                if hasattr(client, 'aclose'):
                    await client.aclose()
            
            # Clear caches
            self.search_cache.clear()
            
            self.logger.info("AI Influencer Discovery System closed")
            
        except Exception as e:
            self.logger.error(f"Error closing discovery system: {e}")


# Example usage
async def example_usage():
    """Example usage of AIInfluencerDiscoverySystem."""
    
    config = {
        'instagram': {
            'access_token': 'your-instagram-token',
            'page_id': 'your-page-id'
        },
        'youtube': {
            'api_key': 'your-youtube-api-key',
            'access_token': 'your-youtube-oauth-token'
        },
        'twitter': {
            'bearer_token': 'your-twitter-bearer-token'
        }
    }
    
    discovery_system = AIInfluencerDiscoverySystem(config)
    
    try:
        # Define search criteria
        search_criteria = SearchCriteria(
            platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.YOUTUBE],
            niches=[NicheCategory.FASHION, NicheCategory.LIFESTYLE],
            tiers=[InfluencerTier.MICRO, InfluencerTier.MID],
            min_followers=10000,
            max_followers=500000,
            min_engagement_rate=3.0,
            min_authenticity_score=80.0,
            max_fake_follower_percentage=15.0,
            target_locations=["United States", "United Kingdom"],
            target_age_ranges=["18-24", "25-34"],
            budget_range=(Decimal('500'), Decimal('5000')),
            max_results=50,
            sort_by="influence_score"
        )
        
        # Discover influencers
        influencers = await discovery_system.discover_influencers(
            search_criteria,
            use_ai_scoring=True
        )
        
        print(f"Discovered {len(influencers)} influencers matching criteria")
        
        # Display top influencers
        for i, influencer in enumerate(influencers[:5]):
            print(f"\n{i+1}. {influencer.username} (@{influencer.platform.value})")
            print(f"   Followers: {influencer.engagement_metrics.followers_count:,}")
            print(f"   Engagement Rate: {influencer.engagement_metrics.engagement_rate:.2f}%")
            print(f"   Influence Score: {influencer.influence_score:.1f}")
            print(f"   Authenticity: {influencer.authenticity_score:.1f}")
            print(f"   Niche: {influencer.niche.value.title()}")
        
        # Find collaboration matches
        brand_profile = {
            'brand_id': 'ainflue_brand',
            'target_niches': ['fashion', 'lifestyle'],
            'target_audience': {
                'age_ranges': ['18-24', '25-34'],
                'genders': ['female'],
                'locations': ['United States']
            },
            'budget_range': (1000, 8000),
            'goals': ['awareness', 'engagement'],
            'values': ['authenticity', 'creativity'],
            'min_brand_safety_score': 85.0
        }
        
        matches = await discovery_system.find_collaboration_matches(
            brand_profile,
            max_matches=10
        )
        
        print(f"\nFound {len(matches)} collaboration matches")
        
        # Display top matches
        for i, match in enumerate(matches[:3]):
            print(f"\n{i+1}. Match Score: {match.match_score:.1f}")
            print(f"   Influencer ID: {match.influencer_id}")
            print(f"   Predicted Reach: {match.predicted_reach:,}")
            print(f"   Expected ROI: {match.expected_roi:.2f}")
        
        # Get discovery stats
        stats = discovery_system.get_discovery_stats()
        print(f"\nDiscovery Stats: {stats}")
        
    finally:
        await discovery_system.close()


if __name__ == "__main__":
    asyncio.run(example_usage())