"""
Competitive Analyzer
===================

Advanced competitive analysis and market intelligence system.
Implements competitor monitoring, market positioning, and strategic insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import Counter, defaultdict
import json
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import pandas as pd

logger = logging.getLogger(__name__)

class CompetitorType(Enum):
    """Types of competitors."""
    DIRECT = "direct"           # Same niche, same audience
    INDIRECT = "indirect"       # Same audience, different niche
    SUBSTITUTE = "substitute"   # Different approach, same goal
    POTENTIAL = "potential"     # Could become competitor
    UNKNOWN = "unknown"         # Unclear competitive relationship

class CompetitiveAdvantage(Enum):
    """Types of competitive advantages."""
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_RATE = "engagement_rate"
    POSTING_FREQUENCY = "posting_frequency"
    AUDIENCE_SIZE = "audience_size"
    INNOVATION = "innovation"
    TIMING = "timing"
    NICHE_EXPERTISE = "niche_expertise"
    PRODUCTION_VALUE = "production_value"
    COMMUNITY_BUILDING = "community_building"
    BRAND_STRENGTH = "brand_strength"

class MarketPosition(Enum):
    """Market positioning categories."""
    LEADER = "leader"           # Market leader
    CHALLENGER = "challenger"   # Strong challenger
    FOLLOWER = "follower"      # Following market trends
    NICHER = "nicher"          # Specialized niche player
    EMERGING = "emerging"       # New emerging player

@dataclass
class CompetitorProfile:
    """Competitor profile information."""
    competitor_id: str
    name: str
    competitor_type: CompetitorType
    market_position: MarketPosition
    
    # Performance metrics
    follower_count: int = 0
    engagement_rate: float = 0.0
    posting_frequency: float = 0.0  # Posts per day
    content_quality_score: float = 0.0
    
    # Content analysis
    content_categories: List[str] = field(default_factory=list)
    hashtag_usage: Dict[str, int] = field(default_factory=dict)
    posting_times: List[datetime] = field(default_factory=list)
    
    # Competitive intelligence
    strengths: List[CompetitiveAdvantage] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    
    # Tracking
    first_detected: datetime = field(default_factory=datetime.now)
    last_analyzed: datetime = field(default_factory=datetime.now)
    analysis_frequency: int = 0

@dataclass
class ContentComparison:
    """Content comparison analysis."""
    user_content_id: str
    competitor_content_id: str
    similarity_score: float
    
    # Comparison metrics
    engagement_comparison: float = 0.0  # -1 to 1 (competitor better to user better)
    quality_comparison: float = 0.0
    timing_comparison: float = 0.0
    
    # Detailed analysis
    similar_elements: List[str] = field(default_factory=list)
    different_elements: List[str] = field(default_factory=list)
    competitive_insights: List[str] = field(default_factory=list)
    
    # Recommendations
    improvement_suggestions: List[str] = field(default_factory=list)

@dataclass
class MarketGapAnalysis:
    """Market gap and opportunity analysis."""
    gap_id: str
    opportunity_type: str
    market_size_estimate: float
    difficulty_score: float  # 0-1, how difficult to exploit
    time_sensitivity: float  # 0-1, how urgent
    
    # Gap details
    underserved_audience: Dict[str, Any] = field(default_factory=dict)
    content_gap: List[str] = field(default_factory=list)
    competitor_weaknesses: List[str] = field(default_factory=list)
    
    # Strategic recommendations
    recommended_actions: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    success_probability: float = 0.0

@dataclass
class CompetitiveAnalysisResult:
    """Complete competitive analysis result."""
    content_id: str
    analysis_timestamp: datetime
    
    # Competitive landscape
    identified_competitors: List[CompetitorProfile]
    market_position: MarketPosition
    competitive_score: float  # Overall competitive strength (0-1)
    
    # Content analysis
    content_comparisons: List[ContentComparison]
    content_uniqueness_score: float
    competitive_advantages: List[CompetitiveAdvantage]
    competitive_disadvantages: List[str]
    
    # Market intelligence
    market_gaps: List[MarketGapAnalysis]
    trending_strategies: List[str]
    threat_level: float  # 0-1, competitive threat level
    
    # Strategic recommendations
    strategic_recommendations: List[str] = field(default_factory=list)
    tactical_recommendations: List[str] = field(default_factory=list)
    competitive_actions: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    confidence_score: float = 0.0

class CompetitiveAnalyzer:
    """
    Advanced competitive analysis and market intelligence system.
    
    Features:
    - Competitor identification and profiling
    - Content similarity analysis
    - Market positioning assessment
    - Gap analysis and opportunity identification
    - Competitive intelligence gathering
    - Strategic recommendation engine
    - Threat assessment and monitoring
    - Performance benchmarking
    """
    
    def __init__(
        self,
        enable_realtime_monitoring: bool = True,
        competitor_discovery_threshold: float = 0.7,
        analysis_depth: str = "comprehensive"
    ):
        """
        Initialize competitive analyzer.
        
        Args:
            enable_realtime_monitoring: Enable real-time competitor monitoring
            competitor_discovery_threshold: Threshold for competitor identification
            analysis_depth: Analysis depth level (basic, standard, comprehensive)
        """
        self.enable_realtime_monitoring = enable_realtime_monitoring
        self.competitor_discovery_threshold = competitor_discovery_threshold
        self.analysis_depth = analysis_depth
        
        # Competitor database
        self.competitors = {}
        self.competitor_content = defaultdict(list)
        self.market_intelligence = {}
        
        # Analysis components
        self.content_vectorizer = None
        self.similarity_threshold = 0.6
        
        # Performance tracking
        self.analysis_count = 0
        self.competitor_count = 0
        self.processing_times = []
        
        # Initialize components
        self._initialize_analysis_models()
        self._load_market_intelligence()
        
        logger.info(f"CompetitiveAnalyzer initialized with {analysis_depth} analysis depth")
    
    def _initialize_analysis_models(self) -> None:
        """Initialize analysis models and vectorizers."""



        try:
            # Content similarity analysis
            self.content_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.95
            )
            
            # Clustering for competitor grouping
            self.clustering_model = DBSCAN(
                eps=0.3,
                min_samples=2,
                metric='cosine'
            )
            
            logger.info("Competitive analysis models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis models: {e}")
    
    def _load_market_intelligence(self) -> None:
        """Load market intelligence data and competitive patterns."""
        # Industry benchmarks
        self.industry_benchmarks = {
            'engagement_rate': {
                'excellent': 0.08,
                'good': 0.05,
                'average': 0.03,
                'poor': 0.01
            },
            'posting_frequency': {
                'high': 3.0,  # posts per day
                'medium': 1.5,
                'low': 0.5
            },
            'follower_growth': {
                'excellent': 0.1,  # 10% monthly growth
                'good': 0.05,
                'average': 0.02,
                'poor': 0.005
            }
        }
        
        # Competitive strategies patterns
        self.strategy_patterns = {
            'content_saturation': [
                'high posting frequency', 'multiple content types',
                'cross-platform presence', 'trend following'
            ],
            'quality_differentiation': [
                'high production value', 'unique content', 
                'expert positioning', 'premium approach'
            ],
            'community_building': [
                'high engagement', 'user-generated content',
                'community features', 'interaction focus'
            ],
            'innovation_leadership': [
                'first-mover advantage', 'technology adoption',
                'format innovation', 'trend creation'
            ]
        }
        
        # Market signals
        self.market_signals = {
            'oversaturation': ['declining engagement', 'increased competition', 'content similarity'],
            'opportunity': ['underserved audience', 'content gaps', 'weak competition'],
            'threat': ['new entrants', 'changing algorithms', 'shifting preferences']
        }
    
    async def analyze_competition(
        self,
        content_id: str,
        content_text: str,
        user_profile: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CompetitiveAnalysisResult:
        """
        Perform comprehensive competitive analysis.
        
        Args:
            content_id: Unique content identifier
            content_text: Content to analyze
            user_profile: User profile information
            metadata: Additional metadata
            
        Returns:
            CompetitiveAnalysisResult: Complete competitive analysis
        """
        start_time = datetime.now()
        
        try:
            metadata = metadata or {}
            
            # Identify competitors
            identified_competitors = await self._identify_competitors(
                content_text, user_profile, metadata
            )
            
            # Analyze market position
            market_position = self._analyze_market_position(user_profile, identified_competitors)
            
            # Calculate competitive score
            competitive_score = self._calculate_competitive_score(user_profile, identified_competitors)
            
            # Content comparison analysis
            content_comparisons = await self._analyze_content_comparisons(
                content_id, content_text, identified_competitors
            )
            
            # Content uniqueness assessment
            content_uniqueness_score = self._calculate_content_uniqueness(
                content_text, identified_competitors
            )
            
            # Identify competitive advantages and disadvantages
            advantages, disadvantages = self._analyze_competitive_position(
                user_profile, identified_competitors
            )
            
            # Market gap analysis
            market_gaps = await self._identify_market_gaps(
                content_text, user_profile, identified_competitors
            )
            
            # Trending strategies analysis
            trending_strategies = self._analyze_trending_strategies(identified_competitors)
            
            # Threat assessment
            threat_level = self._assess_threat_level(identified_competitors, market_gaps)
            
            # Generate recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                market_position, advantages, disadvantages, market_gaps
            )
            
            tactical_recommendations = self._generate_tactical_recommendations(
                content_comparisons, competitive_score
            )
            
            competitive_actions = self._generate_competitive_actions(
                identified_competitors, threat_level
            )
            
            # Calculate confidence and processing time
            confidence_score = self._calculate_analysis_confidence(
                len(identified_competitors), len(content_comparisons)
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = CompetitiveAnalysisResult(
                content_id=content_id,
                analysis_timestamp=datetime.now(),
                identified_competitors=identified_competitors,
                market_position=market_position,
                competitive_score=competitive_score,
                content_comparisons=content_comparisons,
                content_uniqueness_score=content_uniqueness_score,
                competitive_advantages=advantages,
                competitive_disadvantages=disadvantages,
                market_gaps=market_gaps,
                trending_strategies=trending_strategies,
                threat_level=threat_level,
                strategic_recommendations=strategic_recommendations,
                tactical_recommendations=tactical_recommendations,
                competitive_actions=competitive_actions,
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            # Update analytics
            self.analysis_count += 1
            self.processing_times.append(processing_time)
            
            logger.info(f"Competitive analysis completed for {content_id}: "
                       f"{len(identified_competitors)} competitors identified")
            
            return result
            
        except Exception as e:
            logger.error(f"Competitive analysis failed for {content_id}: {e}")
            
            return CompetitiveAnalysisResult(
                content_id=content_id,
                analysis_timestamp=datetime.now(),
                identified_competitors=[],
                market_position=MarketPosition.UNKNOWN,
                competitive_score=0.0,
                content_comparisons=[],
                content_uniqueness_score=0.5,
                competitive_advantages=[],
                competitive_disadvantages=[],
                market_gaps=[],
                trending_strategies=[],
                threat_level=0.5,
                processing_time=(datetime.now() - start_time).total_seconds(),
                confidence_score=0.0
            )
    
    async def _identify_competitors(
        self,
        content_text: str,
        user_profile: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[CompetitorProfile]:
        """Identify potential competitors based on content and profile."""



        try:
            competitors = []
            
            # Extract content characteristics
            content_keywords = self._extract_keywords(content_text)
            content_topics = self._extract_topics(content_text)
            
            # Simulate competitor identification
            # In real implementation, this would query competitor databases
            
            # Generate sample competitors based on content analysis
            if 'technology' in content_text.lower() or 'tech' in content_text.lower():
                competitors.extend(self._generate_tech_competitors(content_keywords))
            
            if 'music' in content_text.lower() or 'song' in content_text.lower():
                competitors.extend(self._generate_music_competitors(content_keywords))
            
            if 'fashion' in content_text.lower() or 'style' in content_text.lower():
                competitors.extend(self._generate_fashion_competitors(content_keywords))
            
            # Add general content competitors
            competitors.extend(self._generate_general_competitors(content_keywords, user_profile))
            
            # Filter and rank competitors
            filtered_competitors = self._filter_competitors(competitors, user_profile)
            
            return filtered_competitors[:10]  # Return top 10 competitors
            
        except Exception as e:
            logger.error(f"Competitor identification failed: {e}")
            return []
    
    def _generate_tech_competitors(self, keywords: List[str]) -> List[CompetitorProfile]:
        """Generate technology sector competitors."""
        tech_competitors = [
            {
                'name': 'TechInfluencer1',
                'type': CompetitorType.DIRECT,
                'position': MarketPosition.LEADER,
                'followers': 150000,
                'engagement': 0.06,
                'frequency': 2.5,
                'categories': ['technology', 'innovation', 'gadgets']
            },
            {
                'name': 'TechReviewer2',
                'type': CompetitorType.INDIRECT,
                'position': MarketPosition.CHALLENGER,
                'followers': 85000,
                'engagement': 0.08,
                'frequency': 1.8,
                'categories': ['tech reviews', 'tutorials', 'news']
            }
        ]
        
        competitors = []
        for comp_data in tech_competitors:
            competitor_id = hashlib.md5(comp_data['name'].encode()).hexdigest()[:16]
            
            competitor = CompetitorProfile(
                competitor_id=competitor_id,
                name=comp_data['name'],
                competitor_type=comp_data['type'],
                market_position=comp_data['position'],
                follower_count=comp_data['followers'],
                engagement_rate=comp_data['engagement'],
                posting_frequency=comp_data['frequency'],
                content_categories=comp_data['categories'],
                strengths=[CompetitiveAdvantage.CONTENT_QUALITY, CompetitiveAdvantage.NICHE_EXPERTISE]
            )
            competitors.append(competitor)
        
        return competitors
    
    def _generate_music_competitors(self, keywords: List[str]) -> List[CompetitorProfile]:
        """Generate music sector competitors."""
        music_competitors = [
            {
                'name': 'MusicInfluencer1',
                'type': CompetitorType.DIRECT,
                'position': MarketPosition.LEADER,
                'followers': 250000,
                'engagement': 0.12,
                'frequency': 3.2,
                'categories': ['music', 'entertainment', 'concerts']
            },
            {
                'name': 'IndieArtist2',
                'type': CompetitorType.SUBSTITUTE,
                'position': MarketPosition.NICHER,
                'followers': 45000,
                'engagement': 0.15,
                'frequency': 1.2,
                'categories': ['indie music', 'original content', 'live performances']
            }
        ]
        
        competitors = []
        for comp_data in music_competitors:
            competitor_id = hashlib.md5(comp_data['name'].encode()).hexdigest()[:16]
            
            competitor = CompetitorProfile(
                competitor_id=competitor_id,
                name=comp_data['name'],
                competitor_type=comp_data['type'],
                market_position=comp_data['position'],
                follower_count=comp_data['followers'],
                engagement_rate=comp_data['engagement'],
                posting_frequency=comp_data['frequency'],
                content_categories=comp_data['categories'],
                strengths=[CompetitiveAdvantage.ENGAGEMENT_RATE, CompetitiveAdvantage.COMMUNITY_BUILDING]
            )
            competitors.append(competitor)
        
        return competitors
    
    def _generate_fashion_competitors(self, keywords: List[str]) -> List[CompetitorProfile]:
        """Generate fashion sector competitors."""
        fashion_competitors = [
            {
                'name': 'FashionInfluencer1',
                'type': CompetitorType.DIRECT,
                'position': MarketPosition.CHALLENGER,
                'followers': 180000,
                'engagement': 0.09,
                'frequency': 2.8,
                'categories': ['fashion', 'style', 'trends']
            }
        ]
        
        competitors = []
        for comp_data in fashion_competitors:
            competitor_id = hashlib.md5(comp_data['name'].encode()).hexdigest()[:16]
            
            competitor = CompetitorProfile(
                competitor_id=competitor_id,
                name=comp_data['name'],
                competitor_type=comp_data['type'],
                market_position=comp_data['position'],
                follower_count=comp_data['followers'],
                engagement_rate=comp_data['engagement'],
                posting_frequency=comp_data['frequency'],
                content_categories=comp_data['categories'],
                strengths=[CompetitiveAdvantage.PRODUCTION_VALUE, CompetitiveAdvantage.BRAND_STRENGTH]
            )
            competitors.append(competitor)
        
        return competitors
    
    def _generate_general_competitors(
        self, 
        keywords: List[str], 
        user_profile: Dict[str, Any]
    ) -> List[CompetitorProfile]:
        """Generate general content competitors."""
        # Base competitor profile on user's characteristics
        user_followers = user_profile.get('follower_count', 10000)
        user_engagement = user_profile.get('engagement_rate', 0.03)
        
        general_competitors = [
            {
                'name': 'GeneralCreator1',
                'type': CompetitorType.DIRECT,
                'position': MarketPosition.FOLLOWER,
                'followers': int(user_followers * 1.2),
                'engagement': user_engagement * 0.9,
                'frequency': 2.0,
                'categories': ['general content', 'lifestyle', 'entertainment']
            },
            {
                'name': 'EmergingCreator2',
                'type': CompetitorType.POTENTIAL,
                'position': MarketPosition.EMERGING,
                'followers': int(user_followers * 0.6),
                'engagement': user_engagement * 1.3,
                'frequency': 3.5,
                'categories': ['trending content', 'viral videos', 'challenges']
            }
        ]
        
        competitors = []
        for comp_data in general_competitors:
            competitor_id = hashlib.md5(comp_data['name'].encode()).hexdigest()[:16]
            
            competitor = CompetitorProfile(
                competitor_id=competitor_id,
                name=comp_data['name'],
                competitor_type=comp_data['type'],
                market_position=comp_data['position'],
                follower_count=comp_data['followers'],
                engagement_rate=comp_data['engagement'],
                posting_frequency=comp_data['frequency'],
                content_categories=comp_data['categories']
            )
            competitors.append(competitor)
        
        return competitors
    
    def _filter_competitors(
        self,
        competitors: List[CompetitorProfile],
        user_profile: Dict[str, Any]
    ) -> List[CompetitorProfile]:
        """Filter and rank competitors by relevance."""
        user_followers = user_profile.get('follower_count', 10000)
        user_categories = user_profile.get('content_categories', [])
        
        scored_competitors = []
        
        for competitor in competitors:
            relevance_score = 0.0
            
            # Follower count similarity (closer = more relevant)
            follower_ratio = min(competitor.follower_count, user_followers) / max(competitor.follower_count, user_followers)
            relevance_score += follower_ratio * 0.3
            
            # Content category overlap
            category_overlap = len(set(competitor.content_categories) & set(user_categories))
            relevance_score += (category_overlap / max(1, len(user_categories))) * 0.4
            
            # Competitor type weighting
            type_weights = {
                CompetitorType.DIRECT: 1.0,
                CompetitorType.INDIRECT: 0.8,
                CompetitorType.SUBSTITUTE: 0.7,
                CompetitorType.POTENTIAL: 0.6,
                CompetitorType.UNKNOWN: 0.3
            }
            relevance_score += type_weights.get(competitor.competitor_type, 0.3) * 0.3
            
            if relevance_score >= self.competitor_discovery_threshold:
                scored_competitors.append((competitor, relevance_score))
        
        # Sort by relevance score
        scored_competitors.sort(key=lambda x: x[1], reverse=True)
        
        return [comp for comp, score in scored_competitors]
    
    def _analyze_market_position(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> MarketPosition:
        """Analyze user's market position relative to competitors."""
        if not competitors:
            return MarketPosition.EMERGING
        
        user_followers = user_profile.get('follower_count', 0)
        user_engagement = user_profile.get('engagement_rate', 0.0)
        
        # Calculate relative metrics
        competitor_followers = [c.follower_count for c in competitors]
        competitor_engagements = [c.engagement_rate for c in competitors]
        
        if competitor_followers:
            follower_percentile = sum(1 for f in competitor_followers if user_followers > f) / len(competitor_followers)
        else:
            follower_percentile = 0.5
        
        if competitor_engagements:
            engagement_percentile = sum(1 for e in competitor_engagements if user_engagement > e) / len(competitor_engagements)
        else:
            engagement_percentile = 0.5
        
        # Determine position
        overall_score = (follower_percentile + engagement_percentile) / 2
        
        if overall_score >= 0.8:
            return MarketPosition.LEADER
        elif overall_score >= 0.6:
            return MarketPosition.CHALLENGER
        elif overall_score >= 0.4:
            return MarketPosition.FOLLOWER
        elif overall_score >= 0.2:
            return MarketPosition.NICHER
        else:
            return MarketPosition.EMERGING
    
    def _calculate_competitive_score(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> float:
        """Calculate overall competitive strength score."""
        if not competitors:
            return 0.5
        
        factors = []
        
        # Audience size factor
        user_followers = user_profile.get('follower_count', 0)
        if competitors:
            avg_competitor_followers = np.mean([c.follower_count for c in competitors])
            follower_factor = min(1.0, user_followers / max(1, avg_competitor_followers))
            factors.append(follower_factor)
        
        # Engagement rate factor
        user_engagement = user_profile.get('engagement_rate', 0.0)
        if competitors:
            avg_competitor_engagement = np.mean([c.engagement_rate for c in competitors])
            engagement_factor = min(1.0, user_engagement / max(0.001, avg_competitor_engagement))
            factors.append(engagement_factor)
        
        # Content frequency factor
        user_frequency = user_profile.get('posting_frequency', 1.0)
        if competitors:
            avg_competitor_frequency = np.mean([c.posting_frequency for c in competitors])
            frequency_factor = min(1.0, user_frequency / max(0.1, avg_competitor_frequency))
            factors.append(frequency_factor)
        
        # Unique positioning factor
        user_categories = set(user_profile.get('content_categories', []))
        competitor_categories = set()
        for competitor in competitors:
            competitor_categories.update(competitor.content_categories)
        
        if user_categories and competitor_categories:
            uniqueness_factor = 1.0 - (len(user_categories & competitor_categories) / len(user_categories))
            factors.append(uniqueness_factor)
        
        return np.mean(factors) if factors else 0.5
    
    async def _analyze_content_comparisons(
        self,
        content_id: str,
        content_text: str,
        competitors: List[CompetitorProfile]
    ) -> List[ContentComparison]:
        """Analyze content similarities with competitors."""
        comparisons = []
        
        try:
            # For each competitor, simulate content comparison
            for competitor in competitors[:5]:  # Top 5 competitors
                # Simulate competitor content
                competitor_content = self._simulate_competitor_content(competitor)
                
                for i, comp_content in enumerate(competitor_content[:3]):  # Top 3 pieces
                    similarity_score = self._calculate_content_similarity(content_text, comp_content)
                    
                    if similarity_score > self.similarity_threshold:
                        comparison = ContentComparison(
                            user_content_id=content_id,
                            competitor_content_id=f"{competitor.competitor_id}_{i}",
                            similarity_score=similarity_score,
                            engagement_comparison=self._compare_engagement(competitor),
                            quality_comparison=self._compare_quality(content_text, comp_content),
                            timing_comparison=0.0,  # Would need temporal data
                            similar_elements=self._identify_similar_elements(content_text, comp_content),
                            competitive_insights=self._generate_competitive_insights(competitor, similarity_score),
                            improvement_suggestions=self._generate_improvement_suggestions(competitor, similarity_score)
                        )
                        comparisons.append(comparison)
            
            return comparisons
            
        except Exception as e:
            logger.error(f"Content comparison analysis failed: {e}")
            return []
    
    def _simulate_competitor_content(self, competitor: CompetitorProfile) -> List[str]:
        """Simulate competitor content for analysis."""
        # Generate sample content based on competitor profile
        content_samples = []
        
        categories = competitor.content_categories
        if 'technology' in categories:
            content_samples.extend([
                "Latest tech trends and innovations in 2024",
                "Review of the newest gadgets and devices",
                "How AI is changing the technology landscape"
            ])
        
        if 'music' in categories:
            content_samples.extend([
                "New music releases and artist spotlights",
                "Behind the scenes of music production",
                "Concert reviews and festival highlights"
            ])
        
        if 'fashion' in categories:
            content_samples.extend([
                "Fashion week highlights and trend analysis",
                "Style tips and outfit inspiration",
                "Sustainable fashion and ethical brands"
            ])
        
        # Default content
        if not content_samples:
            content_samples = [
                "Daily lifestyle content and personal updates",
                "Entertainment news and pop culture commentary",
                "Motivational content and life advice"
            ]
        
        return content_samples
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content pieces."""



        try:
            # Simple word overlap similarity
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _compare_engagement(self, competitor: CompetitorProfile) -> float:
        """Compare engagement rates (-1 to 1)."""
        # Simulated comparison - in real implementation would use actual data
        user_engagement = 0.03  # Default user engagement
        competitor_engagement = competitor.engagement_rate
        
        if competitor_engagement == 0:
            return 0.0
        
        ratio = user_engagement / competitor_engagement
        
        # Convert to -1 to 1 scale
        if ratio > 1:
            return min(1.0, (ratio - 1) * 2)  # User better
        else:
            return max(-1.0, (ratio - 1) * 2)  # Competitor better
    
    def _compare_quality(self, user_content: str, competitor_content: str) -> float:
        """Compare content quality (-1 to 1)."""
        # Simple quality metrics
        user_length = len(user_content.split())
        comp_length = len(competitor_content.split())
        
        # Assume longer content is higher quality (simplified)
        if user_length > comp_length:
            return min(1.0, (user_length - comp_length) / max(1, comp_length))
        else:
            return max(-1.0, (user_length - comp_length) / max(1, user_length))
    
    def _identify_similar_elements(self, content1: str, content2: str) -> List[str]:
        """Identify similar elements between content pieces."""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        common_words = words1 & words2
        
        # Filter meaningful words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_common = [word for word in common_words if word not in stop_words and len(word) > 2]
        
        return meaningful_common[:10]  # Return top 10
    
    def _generate_competitive_insights(
        self,
        competitor: CompetitorProfile,
        similarity_score: float
    ) -> List[str]:
        """Generate competitive insights from comparison."""
        insights = []
        
        if similarity_score > 0.7:
            insights.append(f"High content overlap with {competitor.name} - consider differentiation")
        
        if competitor.engagement_rate > 0.05:
            insights.append(f"{competitor.name} has strong engagement - analyze their interaction strategies")
        
        if competitor.posting_frequency > 3.0:
            insights.append(f"{competitor.name} posts frequently - consider content calendar optimization")
        
        if CompetitiveAdvantage.CONTENT_QUALITY in competitor.strengths:
            insights.append(f"{competitor.name} excels in content quality - benchmark production standards")
        
        return insights
    
    def _generate_improvement_suggestions(
        self,
        competitor: CompetitorProfile,
        similarity_score: float
    ) -> List[str]:
        """Generate improvement suggestions based on competitor analysis."""
        suggestions = []
        
        if competitor.engagement_rate > 0.05:
            suggestions.append("Increase audience interaction and engagement tactics")
        
        if competitor.posting_frequency > 2.0:
            suggestions.append("Consider increasing posting frequency with quality content")
        
        if CompetitiveAdvantage.NICHE_EXPERTISE in competitor.strengths:
            suggestions.append("Develop deeper expertise in your content niche")
        
        if similarity_score > 0.6:
            suggestions.append("Differentiate content to reduce direct competition")
        
        return suggestions
    
    def _calculate_content_uniqueness(
        self,
        content_text: str,
        competitors: List[CompetitorProfile]
    ) -> float:
        """Calculate content uniqueness score."""
        if not competitors:
            return 1.0
        
        uniqueness_scores = []
        
        for competitor in competitors:
            competitor_content = self._simulate_competitor_content(competitor)
            
            for comp_content in competitor_content:
                similarity = self._calculate_content_similarity(content_text, comp_content)
                uniqueness = 1.0 - similarity
                uniqueness_scores.append(uniqueness)
        
        return np.mean(uniqueness_scores) if uniqueness_scores else 1.0
    
    def _analyze_competitive_position(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Tuple[List[CompetitiveAdvantage], List[str]]:
        """Analyze competitive advantages and disadvantages."""
        advantages = []
        disadvantages = []
        
        user_engagement = user_profile.get('engagement_rate', 0.0)
        user_followers = user_profile.get('follower_count', 0)
        user_frequency = user_profile.get('posting_frequency', 1.0)
        
        # Analyze advantages
        if competitors:
            avg_engagement = np.mean([c.engagement_rate for c in competitors])
            if user_engagement > avg_engagement * 1.2:
                advantages.append(CompetitiveAdvantage.ENGAGEMENT_RATE)
            
            avg_followers = np.mean([c.follower_count for c in competitors])
            if user_followers > avg_followers * 1.2:
                advantages.append(CompetitiveAdvantage.AUDIENCE_SIZE)
            
            avg_frequency = np.mean([c.posting_frequency for c in competitors])
            if user_frequency > avg_frequency * 1.2:
                advantages.append(CompetitiveAdvantage.POSTING_FREQUENCY)
        
        # Analyze disadvantages
        if competitors:
            if user_engagement < avg_engagement * 0.8:
                disadvantages.append("Lower engagement rate than competitors")
            
            if user_followers < avg_followers * 0.8:
                disadvantages.append("Smaller audience than main competitors")
            
            if user_frequency < avg_frequency * 0.8:
                disadvantages.append("Lower posting frequency than competitors")
        
        return advantages, disadvantages
    
    async def _identify_market_gaps(
        self,
        content_text: str,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[MarketGapAnalysis]:
        """Identify market gaps and opportunities."""
        gaps = []
        
        try:
            # Content gap analysis
            user_topics = self._extract_topics(content_text)
            competitor_topics = set()
            
            for competitor in competitors:
                competitor_content = self._simulate_competitor_content(competitor)
                for content in competitor_content:
                    competitor_topics.update(self._extract_topics(content))
            
            # Find underserved topics
            underserved_topics = set(user_topics) - competitor_topics
            
            if underserved_topics:
                gap_id = hashlib.md5("content_gap".encode()).hexdigest()[:16]
                
                gap = MarketGapAnalysis(
                    gap_id=gap_id,
                    opportunity_type="content_gap",
                    market_size_estimate=0.7,  # Estimated market size
                    difficulty_score=0.3,      # Relatively easy to exploit
                    time_sensitivity=0.8,      # High urgency
                    content_gap=list(underserved_topics),
                    recommended_actions=[
                        "Create content in underserved topic areas",
                        "Position as expert in niche topics",
                        "Build audience in gap areas"
                    ],
                    success_probability=0.75
                )
                gaps.append(gap)
            
            # Engagement gap analysis
            low_engagement_competitors = [
                c for c in competitors if c.engagement_rate < 0.03
            ]
            
            if len(low_engagement_competitors) > len(competitors) * 0.5:
                gap_id = hashlib.md5("engagement_gap".encode()).hexdigest()[:16]
                
                gap = MarketGapAnalysis(
                    gap_id=gap_id,
                    opportunity_type="engagement_opportunity",
                    market_size_estimate=0.6,
                    difficulty_score=0.4,
                    time_sensitivity=0.6,
                    competitor_weaknesses=["Low audience engagement", "Poor interaction strategies"],
                    recommended_actions=[
                        "Focus on high-engagement content formats",
                        "Build strong community interaction",
                        "Implement audience feedback loops"
                    ],
                    success_probability=0.65
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Market gap analysis failed: {e}")
            return []
    
    def _analyze_trending_strategies(self, competitors: List[CompetitorProfile]) -> List[str]:
        """Analyze trending strategies among competitors."""
        strategies = []
        
        # Analyze competitor patterns
        high_engagement_competitors = [c for c in competitors if c.engagement_rate > 0.05]
        high_frequency_competitors = [c for c in competitors if c.posting_frequency > 2.5]
        
        if len(high_engagement_competitors) > len(competitors) * 0.5:
            strategies.append("High engagement focus - prioritize audience interaction")
        
        if len(high_frequency_competitors) > len(competitors) * 0.5:
            strategies.append("Content volume strategy - increase posting frequency")
        
        # Analyze content categories
        all_categories = []
        for competitor in competitors:
            all_categories.extend(competitor.content_categories)
        
        category_counts = Counter(all_categories)
        top_categories = [cat for cat, count in category_counts.most_common(3)]
        
        for category in top_categories:
            strategies.append(f"Focus on {category} content - trending category")
        
        return strategies
    
    def _assess_threat_level(
        self,
        competitors: List[CompetitorProfile],
        market_gaps: List[MarketGapAnalysis]
    ) -> float:
        """Assess competitive threat level."""
        threat_factors = []
        
        # Strong competitors threat
        strong_competitors = [
            c for c in competitors 
            if c.market_position in [MarketPosition.LEADER, MarketPosition.CHALLENGER]
        ]
        threat_factors.append(len(strong_competitors) / max(1, len(competitors)))
        
        # High engagement competitors
        high_engagement = [c for c in competitors if c.engagement_rate > 0.06]
        threat_factors.append(len(high_engagement) / max(1, len(competitors)))
        
        # Market saturation
        if len(competitors) > 10:
            threat_factors.append(0.8)  # High saturation
        elif len(competitors) > 5:
            threat_factors.append(0.5)  # Medium saturation
        else:
            threat_factors.append(0.2)  # Low saturation
        
        # Limited market gaps
        gap_factor = max(0.0, 1.0 - len(market_gaps) * 0.2)
        threat_factors.append(gap_factor)
        
        return np.mean(threat_factors)
    
    def _generate_strategic_recommendations(
        self,
        market_position: MarketPosition,
        advantages: List[CompetitiveAdvantage],
        disadvantages: List[str],
        market_gaps: List[MarketGapAnalysis]
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        # Position-based recommendations
        if market_position == MarketPosition.EMERGING:
            recommendations.extend([
                "Focus on rapid audience growth strategies",
                "Identify and exploit market niches",
                "Build unique value proposition"
            ])
        elif market_position == MarketPosition.FOLLOWER:
            recommendations.extend([
                "Differentiate from market leaders",
                "Focus on specific audience segments",
                "Innovate in content formats"
            ])
        elif market_position == MarketPosition.CHALLENGER:
            recommendations.extend([
                "Challenge market leaders directly",
                "Scale successful strategies",
                "Expand to new market segments"
            ])
        
        # Advantage-based recommendations
        if CompetitiveAdvantage.ENGAGEMENT_RATE in advantages:
            recommendations.append("Leverage high engagement for brand partnerships")
        
        if CompetitiveAdvantage.NICHE_EXPERTISE in advantages:
            recommendations.append("Become thought leader in your niche")
        
        # Gap-based recommendations
        for gap in market_gaps:
            if gap.success_probability > 0.6:
                recommendations.extend(gap.recommended_actions[:2])
        
        return recommendations[:10]
    
    def _generate_tactical_recommendations(
        self,
        content_comparisons: List[ContentComparison],
        competitive_score: float
    ) -> List[str]:
        """Generate tactical recommendations."""
        recommendations = []
        
        # Content-based recommendations
        if content_comparisons:
            avg_similarity = np.mean([c.similarity_score for c in content_comparisons])
            
            if avg_similarity > 0.7:
                recommendations.append("Increase content differentiation to stand out")
            
            negative_engagement_comparisons = [
                c for c in content_comparisons if c.engagement_comparison < -0.2
            ]
            
            if len(negative_engagement_comparisons) > len(content_comparisons) * 0.5:
                recommendations.append("Analyze and adopt competitor engagement tactics")
        
        # Competitive score recommendations
        if competitive_score < 0.3:
            recommendations.extend([
                "Increase posting frequency and content quality",
                "Focus on audience growth strategies",
                "Benchmark against top performers"
            ])
        elif competitive_score < 0.6:
            recommendations.extend([
                "Optimize content timing and format",
                "Strengthen unique value proposition",
                "Improve audience engagement"
            ])
        
        return recommendations[:8]
    
    def _generate_competitive_actions(
        self,
        competitors: List[CompetitorProfile],
        threat_level: float
    ) -> List[str]:
        """Generate specific competitive actions."""
        actions = []
        
        if threat_level > 0.7:
            actions.extend([
                "Monitor competitor content daily",
                "Rapid response to competitor innovations",
                "Accelerate unique content development"
            ])
        elif threat_level > 0.4:
            actions.extend([
                "Weekly competitor analysis",
                "Track competitor engagement patterns",
                "Identify competitive blind spots"
            ])
        else:
            actions.extend([
                "Monthly competitive review",
                "Focus on market expansion",
                "Monitor new entrants"
            ])
        
        # Specific competitor actions
        for competitor in competitors[:3]:
            if competitor.market_position == MarketPosition.LEADER:
                actions.append(f"Benchmark against {competitor.name} strategies")
            
            if CompetitiveAdvantage.ENGAGEMENT_RATE in competitor.strengths:
                actions.append(f"Analyze {competitor.name} engagement techniques")
        
        return actions[:10]
    
    def _calculate_analysis_confidence(
        self,
        competitor_count: int,
        comparison_count: int
    ) -> float:
        """Calculate confidence score for the analysis."""
        factors = []
        
        # Data availability factor
        if competitor_count >= 5:
            factors.append(0.9)
        elif competitor_count >= 3:
            factors.append(0.7)
        else:
            factors.append(0.4)
        
        # Comparison depth factor
        if comparison_count >= 10:
            factors.append(0.9)
        elif comparison_count >= 5:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Analysis depth factor
        depth_scores = {
            'comprehensive': 0.9,
            'standard': 0.7,
            'basic': 0.5
        }
        factors.append(depth_scores.get(self.analysis_depth, 0.5))
        
        return np.mean(factors)
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words]
        
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text."""
        # Simple topic extraction based on keywords
        topic_keywords = {
            'technology': ['tech', 'technology', 'ai', 'digital', 'innovation'],
            'music': ['music', 'song', 'artist', 'album', 'concert'],
            'fashion': ['fashion', 'style', 'outfit', 'trend', 'clothing'],
            'fitness': ['fitness', 'workout', 'health', 'exercise', 'gym'],
            'food': ['food', 'recipe', 'cooking', 'restaurant', 'cuisine'],
            'travel': ['travel', 'trip', 'vacation', 'destination', 'journey']
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get competitive analysis analytics and performance metrics."""
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "total_analyses": self.analysis_count,
            "total_competitors_tracked": self.competitor_count,
            "average_processing_time": avg_processing_time,
            "active_competitors": len(self.competitors),
            "realtime_monitoring": self.enable_realtime_monitoring,
            "discovery_threshold": self.competitor_discovery_threshold,
            "analysis_depth": self.analysis_depth,
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""
        self.competitors.clear()
        self.competitor_content.clear()
        self.market_intelligence.clear()
        self.processing_times.clear()
        
        logger.info("CompetitiveAnalyzer cleanup completed")
