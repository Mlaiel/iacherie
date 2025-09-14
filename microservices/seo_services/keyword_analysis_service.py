"""
Keyword Analysis Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Keyword Analysis Service
AI-powered keyword research and analysis for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import re
import math
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import aiohttp
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class KeywordDifficulty(Enum):
    """Keyword difficulty enumeration"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class KeywordIntent(Enum):
    """Keyword search intent enumeration"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"

class TrendDirection(Enum):
    """Trend direction enumeration"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

class Platform(Enum):
    """Platform enumeration"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    AMAZON = "amazon"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"

@dataclass
class KeywordMetrics:
    """Keyword metrics data"""
    keyword: str
    search_volume: int
    competition: float  # 0.0 to 1.0
    cpc: float  # Cost per click
    difficulty: KeywordDifficulty
    intent: KeywordIntent
    trend_direction: TrendDirection
    seasonal_scores: Dict[str, float] = field(default_factory=dict)
    related_queries: List[str] = field(default_factory=list)
    long_tail_variations: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

@dataclass
class KeywordCluster:
    """Keyword cluster data"""
    cluster_id: str
    primary_keyword: str
    keywords: List[str]
    theme: str
    total_volume: int
    avg_difficulty: float
    content_gap_score: float
    opportunity_score: float
    created_at: float = field(default_factory=time.time)

@dataclass
class CompetitorKeyword:
    """Competitor keyword data"""
    keyword: str
    competitor_domain: str
    ranking_position: int
    estimated_traffic: int
    content_type: str
    url: str
    title: str
    meta_description: str
    gap_opportunity: float

@dataclass
class KeywordOpportunity:
    """Keyword opportunity analysis"""
    keyword: str
    opportunity_score: float
    reasons: List[str]
    suggested_content_type: str
    target_difficulty: KeywordDifficulty
    estimated_effort: str
    potential_traffic: int
    conversion_potential: float

@dataclass
class TrendAnalysis:
    """Keyword trend analysis"""
    keyword: str
    trend_data: List[Tuple[str, float]]  # (date, volume)
    growth_rate: float
    volatility: float
    seasonal_pattern: Dict[str, float]
    predictions: Dict[str, float]  # Next 3 months
    confidence_score: float

class KeywordAnalysisService:
    """
    Enterprise Keyword Analysis Service
    
    Provides comprehensive keyword research and analysis with:
    - Search volume analysis
    - Competition assessment
    - Trend analysis
    - Keyword clustering
    - Competitor analysis
    - Opportunity identification
    - Multi-platform support
    """
    
    def __init__(self) -> None:
        """Initialize keyword analysis service"""
        # Keyword database
        self.keyword_cache: Dict[str, KeywordMetrics] = {}
        self.keyword_clusters: Dict[str, KeywordCluster] = {}
        self.competitor_keywords: Dict[str, List[CompetitorKeyword]] = defaultdict(list)
        
        # Analysis data
        self.trend_data: Dict[str, TrendAnalysis] = {}
        self.opportunity_cache: Dict[str, List[KeywordOpportunity]] = {}
        
        # Language and region data
        self.language_models: Dict[str, Any] = {}
        self.regional_modifiers: Dict[str, Dict[str, float]] = {}
        
        # Configuration
        self.config = {
            "cache_ttl": 3600.0,  # 1 hour
            "max_suggestions": 50,
            "min_search_volume": 10,
            "max_keyword_length": 100,
            "trend_analysis_days": 90,
            "competitor_analysis_enabled": True,
            "real_time_updates": False,
            "language_detection": True,
            "regional_analysis": True
        }
        
        # API configurations (would be configured with real APIs)
        self.api_configs = {
            "google_trends": {"enabled": False, "api_key": ""},
            "semrush": {"enabled": False, "api_key": ""},
            "ahrefs": {"enabled": False, "api_key": ""},
            "moz": {"enabled": False, "api_key": ""}
        }
        
        # Performance tracking
        self.analysis_stats = {
            "total_analyses": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "avg_processing_time": 0.0,
            "error_rate": 0.0
        }
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.update_task: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize mock data for demonstration
        self._initialize_mock_data()
        
        logger.info("KeywordAnalysisService initialized")
    
    async def start(self) -> None:
        """Start the keyword analysis service"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Start background update task
            self.update_task = asyncio.create_task(self._update_loop())
            
            logger.info("KeywordAnalysisService started successfully")
        except Exception as e:
            logger.error("Failed to start KeywordAnalysisService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the keyword analysis service"""
        try:
            self.shutdown_event.set()
            
            # Stop background task
            if self.update_task:
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
            # Close HTTP session
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("KeywordAnalysisService stopped successfully")
        except Exception as e:
            logger.error("Error stopping KeywordAnalysisService: %s", e)
    
    async def analyze_keyword(
        self,
        keyword: str,
        platform: Platform = Platform.GOOGLE,
        language: str = "en",
        region: str = "US"
    ) -> KeywordMetrics:
        """Analyze a single keyword"""
        start_time = time.time()
        
        async with self._lock:
            # Check cache first
            cache_key = f"{keyword}_{platform.value}_{language}_{region}"
            
            if cache_key in self.keyword_cache:
                cached_result = self.keyword_cache[cache_key]
                if time.time() - cached_result.last_updated < self.config["cache_ttl"]:
                    self.analysis_stats["cache_hits"] += 1
                    return cached_result
            
            # Perform analysis
            try:
                metrics = await self._perform_keyword_analysis(keyword, platform, language, region)
                
                # Cache result
                self.keyword_cache[cache_key] = metrics
                
                # Update stats
                self.analysis_stats["total_analyses"] += 1
                processing_time = time.time() - start_time
                self._update_avg_processing_time(processing_time)
                
                return metrics
                
            except Exception as e:
                logger.error("Keyword analysis failed for '%s': %s", keyword, e)
                self.analysis_stats["total_analyses"] += 1
                self._update_error_rate()
                raise
    
    async def get_keyword_suggestions(
        self,
        seed_keyword: str,
        max_suggestions: Optional[int] = None,
        platform: Platform = Platform.GOOGLE,
        language: str = "en"
    ) -> List[KeywordMetrics]:
        """Get keyword suggestions based on seed keyword"""
        max_suggestions = max_suggestions or self.config["max_suggestions"]
        
        # Generate suggestions using various methods
        suggestions = []
        
        # Method 1: Related queries
        related_queries = await self._get_related_queries(seed_keyword, platform, language)
        
        # Method 2: Long-tail variations
        long_tail = await self._generate_long_tail_variations(seed_keyword, language)
        
        # Method 3: Semantic variations
        semantic_vars = await self._get_semantic_variations(seed_keyword, language)
        
        # Combine and deduplicate
        all_suggestions = set(related_queries + long_tail + semantic_vars)
        
        # Analyze each suggestion
        for suggestion in list(all_suggestions)[:max_suggestions * 2]:  # Get more than needed
            try:
                metrics = await self.analyze_keyword(suggestion, platform, language)
                if metrics.search_volume >= self.config["min_search_volume"]:
                    suggestions.append(metrics)
            except Exception as e:
                logger.warning("Failed to analyze suggestion '%s': %s", suggestion, e)
        
        # Sort by opportunity score (combination of volume and difficulty)
        suggestions.sort(key=lambda x: self._calculate_opportunity_score(x), reverse=True)
        
        return suggestions[:max_suggestions]
    
    async def cluster_keywords(
        self,
        keywords: List[str],
        platform: Platform = Platform.GOOGLE,
        language: str = "en"
    ) -> List[KeywordCluster]:
        """Cluster keywords by semantic similarity"""
        # Analyze all keywords first
        keyword_metrics = []
        for keyword in keywords:
            try:
                metrics = await self.analyze_keyword(keyword, platform, language)
                keyword_metrics.append(metrics)
            except Exception as e:
                logger.warning("Failed to analyze keyword '%s' for clustering: %s", keyword, e)
        
        # Perform clustering
        clusters = await self._perform_clustering(keyword_metrics, language)
        
        # Store clusters
        async with self._lock:
            for cluster in clusters:
                self.keyword_clusters[cluster.cluster_id] = cluster
        
        return clusters
    
    async def analyze_competitors(
        self,
        domain: str,
        competitor_domains: List[str],
        platform: Platform = Platform.GOOGLE,
        max_keywords: int = 100
    ) -> Dict[str, List[CompetitorKeyword]]:
        """Analyze competitor keyword strategies"""
        if not self.config["competitor_analysis_enabled"]:
            return {}
        
        competitor_analysis = {}
        
        for competitor in competitor_domains:
            try:
                # Get competitor keywords (mock implementation)
                competitor_kws = await self._get_competitor_keywords(
                    competitor, platform, max_keywords
                )
                
                # Analyze gaps and opportunities
                gap_analysis = await self._analyze_keyword_gaps(domain, competitor_kws)
                
                competitor_analysis[competitor] = gap_analysis
                
                # Store in cache
                async with self._lock:
                    self.competitor_keywords[competitor] = gap_analysis
                
            except Exception as e:
                logger.error("Competitor analysis failed for %s: %s", competitor, e)
        
        return competitor_analysis
    
    async def identify_opportunities(
        self,
        domain: str,
        niche: str,
        platform: Platform = Platform.GOOGLE,
        language: str = "en"
    ) -> List[KeywordOpportunity]:
        """Identify keyword opportunities for a domain"""
        cache_key = f"opportunities_{domain}_{niche}_{platform.value}_{language}"
        
        async with self._lock:
            # Check cache
            if cache_key in self.opportunity_cache:
                return self.opportunity_cache[cache_key]
        
        opportunities = []
        
        # Get niche-related keywords
        niche_keywords = await self._get_niche_keywords(niche, language)
        
        # Analyze each keyword for opportunities
        for keyword in niche_keywords:
            try:
                metrics = await self.analyze_keyword(keyword, platform, language)
                opportunity = await self._assess_keyword_opportunity(keyword, metrics, domain)
                
                if opportunity.opportunity_score > 0.5:  # Threshold for viable opportunities
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.warning("Opportunity analysis failed for '%s': %s", keyword, e)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        # Cache results
        async with self._lock:
            self.opportunity_cache[cache_key] = opportunities
        
        return opportunities
    
    async def analyze_trends(
        self,
        keywords: List[str],
        time_period: str = "90d",
        platform: Platform = Platform.GOOGLE
    ) -> Dict[str, TrendAnalysis]:
        """Analyze keyword trends over time"""
        trend_analyses = {}
        
        for keyword in keywords:
            try:
                trend_analysis = await self._perform_trend_analysis(keyword, time_period, platform)
                trend_analyses[keyword] = trend_analysis
                
                # Store in cache
                async with self._lock:
                    self.trend_data[keyword] = trend_analysis
                    
            except Exception as e:
                logger.error("Trend analysis failed for '%s': %s", keyword, e)
        
        return trend_analyses
    
    async def get_seasonal_insights(
        self,
        keywords: List[str],
        platform: Platform = Platform.GOOGLE
    ) -> Dict[str, Dict[str, float]]:
        """Get seasonal insights for keywords"""
        seasonal_data = {}
        
        for keyword in keywords:
            try:
                # Get historical data and analyze seasonality
                seasonal_scores = await self._analyze_seasonality(keyword, platform)
                seasonal_data[keyword] = seasonal_scores
                
            except Exception as e:
                logger.error("Seasonal analysis failed for '%s': %s", keyword, e)
        
        return seasonal_data
    
    async def get_content_gaps(
        self,
        domain: str,
        keywords: List[str],
        competitor_domains: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify content gaps based on keyword analysis"""
        gaps = []
        
        for keyword in keywords:
            try:
                # Analyze keyword metrics
                metrics = await self.analyze_keyword(keyword)
                
                # Check competitor coverage
                competitor_coverage = await self._check_competitor_coverage(
                    keyword, competitor_domains
                )
                
                # Calculate content gap score
                gap_score = await self._calculate_content_gap_score(
                    keyword, metrics, competitor_coverage
                )
                
                if gap_score > 0.6:  # Significant gap threshold
                    gaps.append({
                        "keyword": keyword,
                        "gap_score": gap_score,
                        "search_volume": metrics.search_volume,
                        "difficulty": metrics.difficulty.value,
                        "intent": metrics.intent.value,
                        "competitors_ranking": len(competitor_coverage),
                        "suggested_content_type": await self._suggest_content_type(metrics)
                    })
                    
            except Exception as e:
                logger.error("Content gap analysis failed for '%s': %s", keyword, e)
        
        # Sort by gap score
        gaps.sort(key=lambda x: x["gap_score"], reverse=True)
        
        return gaps
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service metrics and statistics"""
        async with self._lock:
            return {
                "total_keywords_analyzed": len(self.keyword_cache),
                "total_clusters": len(self.keyword_clusters),
                "total_competitors_tracked": len(self.competitor_keywords),
                "cache_hit_rate": (
                    self.analysis_stats["cache_hits"] / max(1, self.analysis_stats["total_analyses"])
                ),
                "avg_processing_time": self.analysis_stats["avg_processing_time"],
                "error_rate": self.analysis_stats["error_rate"],
                "api_calls_made": self.analysis_stats["api_calls"],
                "config": dict(self.config)
            }
    
    async def _perform_keyword_analysis(
        self,
        keyword: str,
        platform: Platform,
        language: str,
        region: str
    ) -> KeywordMetrics:
        """Perform comprehensive keyword analysis"""
        # This would integrate with real SEO APIs in production
        # For now, generate realistic mock data
        
        # Calculate metrics based on keyword characteristics
        keyword_length = len(keyword.split())
        keyword_complexity = len(keyword)
        
        # Mock search volume (inverse correlation with length/complexity)
        base_volume = max(100, 10000 // (keyword_length * 2))
        search_volume = int(base_volume * (0.5 + hash(keyword) % 100 / 200))
        
        # Mock competition (longer keywords generally less competitive)
        competition = max(0.1, min(0.9, 0.8 / keyword_length + hash(keyword) % 30 / 100))
        
        # Mock CPC
        cpc = round(0.5 + (competition * 2) + hash(keyword) % 100 / 100, 2)
        
        # Determine difficulty
        difficulty = self._calculate_difficulty(search_volume, competition)
        
        # Determine intent
        intent = self._determine_intent(keyword)
        
        # Mock trend direction
        trend_direction = TrendDirection.STABLE
        trend_hash = hash(keyword + "trend") % 5
        if trend_hash == 0:
            trend_direction = TrendDirection.RISING
        elif trend_hash == 1:
            trend_direction = TrendDirection.DECLINING
        elif trend_hash == 4:
            trend_direction = TrendDirection.VOLATILE
        
        # Generate related queries
        related_queries = await self._get_related_queries(keyword, platform, language)
        
        # Generate long-tail variations
        long_tail = await self._generate_long_tail_variations(keyword, language)
        
        return KeywordMetrics(
            keyword=keyword,
            search_volume=search_volume,
            competition=competition,
            cpc=cpc,
            difficulty=difficulty,
            intent=intent,
            trend_direction=trend_direction,
            related_queries=related_queries[:10],
            long_tail_variations=long_tail[:15]
        )
    
    async def _get_related_queries(
        self,
        keyword: str,
        platform: Platform,
        language: str
    ) -> List[str]:
        """Get related queries for a keyword"""
        # Mock related queries generation
        base_words = keyword.split()
        related = []
        
        # Add common modifiers
        modifiers = [
            "best", "top", "how to", "what is", "why", "where", "when",
            "guide", "tips", "tutorial", "review", "comparison", "vs",
            "free", "online", "near me", "2025"
        ]
        
        for modifier in modifiers[:5]:
            if modifier not in keyword.lower():
                related.append(f"{modifier} {keyword}")
                related.append(f"{keyword} {modifier}")
        
        # Add word variations
        for word in base_words:
            if len(word) > 3:
                related.append(keyword.replace(word, f"{word}s"))  # Plural
                related.append(keyword.replace(word, f"{word}ing"))  # Gerund
        
        return related[:20]
    
    async def _generate_long_tail_variations(self, keyword: str, language: str) -> List[str]:
        """Generate long-tail keyword variations"""
        variations = []
        
        # Question-based variations
        question_starters = [
            "how to", "what is", "why does", "where can", "when should",
            "which is best", "can you", "is it possible", "how much does"
        ]
        
        for starter in question_starters:
            variations.append(f"{starter} {keyword}")
        
        # Location-based variations
        locations = ["near me", "in usa", "online", "local", "nearby"]
        for location in locations:
            variations.append(f"{keyword} {location}")
        
        # Intent-based variations
        intents = ["buy", "review", "comparison", "guide", "tutorial", "tips"]
        for intent in intents:
            variations.append(f"{keyword} {intent}")
            variations.append(f"{intent} for {keyword}")
        
        return variations[:25]
    
    async def _get_semantic_variations(self, keyword: str, language: str) -> List[str]:
        """Get semantic variations of the keyword"""
        # Mock semantic variations
        # In production, this would use NLP models or thesaurus APIs
        
        words = keyword.split()
        variations = []
        
        # Simple synonym mapping (mock)
        synonyms = {
            "best": ["top", "greatest", "finest", "excellent"],
            "guide": ["tutorial", "manual", "handbook", "instructions"],
            "tips": ["advice", "suggestions", "recommendations", "tricks"],
            "review": ["evaluation", "assessment", "analysis", "opinion"],
            "free": ["no-cost", "complimentary", "gratis", "zero-cost"]
        }
        
        for word in words:
            word_lower = word.lower()
            if word_lower in synonyms:
                for synonym in synonyms[word_lower]:
                    new_keyword = keyword.replace(word, synonym)
                    variations.append(new_keyword)
        
        return variations[:15]
    
    def _calculate_difficulty(self, search_volume: int, competition: float) -> KeywordDifficulty:
        """Calculate keyword difficulty"""
        # Combine volume and competition to determine difficulty
        volume_factor = min(1.0, search_volume / 50000)  # Normalize to 0-1
        difficulty_score = (competition * 0.7) + (volume_factor * 0.3)
        
        if difficulty_score < 0.2:
            return KeywordDifficulty.VERY_EASY
        elif difficulty_score < 0.4:
            return KeywordDifficulty.EASY
        elif difficulty_score < 0.6:
            return KeywordDifficulty.MEDIUM
        elif difficulty_score < 0.8:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    def _determine_intent(self, keyword: str) -> KeywordIntent:
        """Determine search intent from keyword"""
        keyword_lower = keyword.lower()
        
        # Transactional intent keywords
        transactional = ["buy", "purchase", "order", "shop", "discount", "deal", "price", "cost"]
        if any(word in keyword_lower for word in transactional):
            return KeywordIntent.TRANSACTIONAL
        
        # Commercial intent keywords
        commercial = ["best", "top", "review", "compare", "vs", "alternative", "recommendation"]
        if any(word in keyword_lower for word in commercial):
            return KeywordIntent.COMMERCIAL
        
        # Navigational intent keywords
        navigational = ["login", "website", "official", "site", "homepage"]
        if any(word in keyword_lower for word in navigational):
            return KeywordIntent.NAVIGATIONAL
        
        # Default to informational
        return KeywordIntent.INFORMATIONAL
    
    def _calculate_opportunity_score(self, metrics: KeywordMetrics) -> float:
        """Calculate opportunity score for a keyword"""
        # Higher volume = better opportunity
        volume_score = min(1.0, metrics.search_volume / 10000)
        
        # Lower competition = better opportunity
        competition_score = 1.0 - metrics.competition
        
        # Lower difficulty = better opportunity
        difficulty_scores = {
            KeywordDifficulty.VERY_EASY: 1.0,
            KeywordDifficulty.EASY: 0.8,
            KeywordDifficulty.MEDIUM: 0.6,
            KeywordDifficulty.HARD: 0.4,
            KeywordDifficulty.VERY_HARD: 0.2
        }
        difficulty_score = difficulty_scores[metrics.difficulty]
        
        # Trending keywords get bonus
        trend_bonus = 0.2 if metrics.trend_direction == TrendDirection.RISING else 0.0
        
        return (volume_score * 0.4 + competition_score * 0.3 + difficulty_score * 0.3) + trend_bonus
    
    async def _perform_clustering(
        self,
        keyword_metrics: List[KeywordMetrics],
        language: str
    ) -> List[KeywordCluster]:
        """Perform keyword clustering"""
        # Simple clustering based on shared words
        # In production, use more sophisticated NLP clustering
        
        clusters = []
        used_keywords = set()
        
        for i, primary_keyword in enumerate(keyword_metrics):
            if primary_keyword.keyword in used_keywords:
                continue
            
            cluster_keywords = [primary_keyword.keyword]
            primary_words = set(primary_keyword.keyword.lower().split())
            
            # Find similar keywords
            for other_keyword in keyword_metrics[i+1:]:
                if other_keyword.keyword in used_keywords:
                    continue
                
                other_words = set(other_keyword.keyword.lower().split())
                similarity = len(primary_words & other_words) / len(primary_words | other_words)
                
                if similarity > 0.3:  # 30% word overlap
                    cluster_keywords.append(other_keyword.keyword)
                    used_keywords.add(other_keyword.keyword)
            
            if len(cluster_keywords) >= 2:  # Only create clusters with multiple keywords
                # Calculate cluster metrics
                cluster_volume = sum(
                    kw.search_volume for kw in keyword_metrics
                    if kw.keyword in cluster_keywords
                )
                
                cluster_difficulty = sum(
                    self._difficulty_to_score(kw.difficulty) for kw in keyword_metrics
                    if kw.keyword in cluster_keywords
                ) / len(cluster_keywords)
                
                cluster = KeywordCluster(
                    cluster_id=f"cluster_{len(clusters) + 1}",
                    primary_keyword=primary_keyword.keyword,
                    keywords=cluster_keywords,
                    theme=self._extract_theme(cluster_keywords),
                    total_volume=cluster_volume,
                    avg_difficulty=cluster_difficulty,
                    content_gap_score=0.7,  # Mock value
                    opportunity_score=self._calculate_cluster_opportunity(cluster_keywords, keyword_metrics)
                )
                
                clusters.append(cluster)
                used_keywords.update(cluster_keywords)
        
        return clusters
    
    def _difficulty_to_score(self, difficulty: KeywordDifficulty) -> float:
        """Convert difficulty enum to numeric score"""
        scores = {
            KeywordDifficulty.VERY_EASY: 0.1,
            KeywordDifficulty.EASY: 0.3,
            KeywordDifficulty.MEDIUM: 0.5,
            KeywordDifficulty.HARD: 0.7,
            KeywordDifficulty.VERY_HARD: 0.9
        }
        return scores[difficulty]
    
    def _extract_theme(self, keywords: List[str]) -> str:
        """Extract theme from cluster keywords"""
        # Count word frequency across all keywords
        word_counts = Counter()
        
        for keyword in keywords:
            words = keyword.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_counts[word] += 1
        
        # Return most common word as theme
        if word_counts:
            return word_counts.most_common(1)[0][0]
        
        return "general"
    
    def _calculate_cluster_opportunity(
        self,
        cluster_keywords: List[str],
        all_metrics: List[KeywordMetrics]
    ) -> float:
        """Calculate opportunity score for a keyword cluster"""
        cluster_metrics = [
            kw for kw in all_metrics if kw.keyword in cluster_keywords
        ]
        
        if not cluster_metrics:
            return 0.0
        
        avg_opportunity = sum(
            self._calculate_opportunity_score(kw) for kw in cluster_metrics
        ) / len(cluster_metrics)
        
        # Bonus for cluster size
        size_bonus = min(0.2, len(cluster_keywords) * 0.02)
        
        return avg_opportunity + size_bonus
    
    async def _get_competitor_keywords(
        self,
        domain: str,
        platform: Platform,
        max_keywords: int
    ) -> List[CompetitorKeyword]:
        """Get competitor keywords (mock implementation)"""
        # In production, integrate with SEO APIs like SEMrush, Ahrefs
        competitor_keywords = []
        
        # Generate mock competitor keywords
        base_keywords = [
            "content marketing", "social media", "digital marketing",
            "seo optimization", "brand strategy", "online advertising",
            "email marketing", "influencer marketing", "video marketing"
        ]
        
        for i, keyword in enumerate(base_keywords[:max_keywords]):
            competitor_keywords.append(CompetitorKeyword(
                keyword=keyword,
                competitor_domain=domain,
                ranking_position=i + 1,
                estimated_traffic=1000 - (i * 50),
                content_type="blog_post",
                url=f"https://{domain}/blog/{keyword.replace(' ', '-')}",
                title=f"Complete Guide to {keyword.title()}",
                meta_description=f"Learn everything about {keyword} with our comprehensive guide.",
                gap_opportunity=0.7 - (i * 0.05)
            ))
        
        return competitor_keywords
    
    async def _analyze_keyword_gaps(
        self,
        domain: str,
        competitor_keywords: List[CompetitorKeyword]
    ) -> List[CompetitorKeyword]:
        """Analyze keyword gaps and opportunities"""
        # Mock gap analysis - identify keywords where domain is not ranking
        gap_keywords = []
        
        for comp_kw in competitor_keywords:
            # Simulate check if domain ranks for this keyword
            domain_ranks = hash(f"{domain}_{comp_kw.keyword}") % 10 == 0  # 10% chance
            
            if not domain_ranks and comp_kw.ranking_position <= 10:
                # This is a gap opportunity
                comp_kw.gap_opportunity = min(1.0, comp_kw.gap_opportunity + 0.3)
                gap_keywords.append(comp_kw)
        
        return gap_keywords
    
    async def _get_niche_keywords(self, niche: str, language: str) -> List[str]:
        """Get keywords related to a specific niche"""
        # Mock niche keyword generation
        niche_modifiers = [
            "best", "top", "how to", "guide", "tips", "tutorial",
            "beginner", "advanced", "free", "online", "tools", "software"
        ]
        
        niche_keywords = []
        for modifier in niche_modifiers:
            niche_keywords.extend([
                f"{modifier} {niche}",
                f"{niche} {modifier}",
                f"{modifier} for {niche}",
                f"{niche} {modifier} guide"
            ])
        
        return niche_keywords[:50]
    
    async def _assess_keyword_opportunity(
        self,
        keyword: str,
        metrics: KeywordMetrics,
        domain: str
    ) -> KeywordOpportunity:
        """Assess opportunity for a specific keyword"""
        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(metrics)
        
        # Generate reasons
        reasons = []
        if metrics.search_volume > 1000:
            reasons.append("High search volume")
        if metrics.competition < 0.5:
            reasons.append("Low competition")
        if metrics.difficulty in [KeywordDifficulty.VERY_EASY, KeywordDifficulty.EASY]:
            reasons.append("Low difficulty")
        if metrics.trend_direction == TrendDirection.RISING:
            reasons.append("Rising trend")
        
        # Suggest content type based on intent
        content_type_mapping = {
            KeywordIntent.INFORMATIONAL: "blog_post",
            KeywordIntent.COMMERCIAL: "product_page",
            KeywordIntent.TRANSACTIONAL: "landing_page",
            KeywordIntent.NAVIGATIONAL: "category_page"
        }
        
        suggested_content = content_type_mapping.get(metrics.intent, "blog_post")
        
        # Estimate effort
        effort_mapping = {
            KeywordDifficulty.VERY_EASY: "Low",
            KeywordDifficulty.EASY: "Low",
            KeywordDifficulty.MEDIUM: "Medium",
            KeywordDifficulty.HARD: "High",
            KeywordDifficulty.VERY_HARD: "Very High"
        }
        
        estimated_effort = effort_mapping[metrics.difficulty]
        
        # Estimate potential traffic (percentage of search volume)
        potential_traffic = int(metrics.search_volume * 0.1)  # Assume 10% CTR
        
        # Conversion potential based on intent
        conversion_potential = {
            KeywordIntent.TRANSACTIONAL: 0.8,
            KeywordIntent.COMMERCIAL: 0.6,
            KeywordIntent.NAVIGATIONAL: 0.4,
            KeywordIntent.INFORMATIONAL: 0.2
        }[metrics.intent]
        
        return KeywordOpportunity(
            keyword=keyword,
            opportunity_score=opportunity_score,
            reasons=reasons,
            suggested_content_type=suggested_content,
            target_difficulty=metrics.difficulty,
            estimated_effort=estimated_effort,
            potential_traffic=potential_traffic,
            conversion_potential=conversion_potential
        )
    
    async def _perform_trend_analysis(
        self,
        keyword: str,
        time_period: str,
        platform: Platform
    ) -> TrendAnalysis:
        """Perform trend analysis for a keyword"""
        # Mock trend data generation
        days = int(time_period.replace('d', ''))
        trend_data = []
        
        # Generate mock trend data
        base_volume = hash(keyword) % 1000 + 100
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d')
            # Add some noise and trend
            volume = base_volume + (i * 2) + (hash(f"{keyword}_{i}") % 100 - 50)
            trend_data.append((date, max(0, volume)))
        
        # Calculate growth rate
        if len(trend_data) >= 2:
            start_volume = trend_data[0][1]
            end_volume = trend_data[-1][1]
            growth_rate = (end_volume - start_volume) / start_volume if start_volume > 0 else 0
        else:
            growth_rate = 0.0
        
        # Calculate volatility
        volumes = [point[1] for point in trend_data]
        if len(volumes) > 1:
            avg_volume = sum(volumes) / len(volumes)
            variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
            volatility = math.sqrt(variance) / avg_volume if avg_volume > 0 else 0
        else:
            volatility = 0.0
        
        # Mock seasonal pattern
        seasonal_pattern = {
            "january": 0.8, "february": 0.9, "march": 1.0, "april": 1.1,
            "may": 1.2, "june": 1.3, "july": 1.2, "august": 1.1,
            "september": 1.0, "october": 0.9, "november": 0.8, "december": 1.0
        }
        
        # Mock predictions
        predictions = {
            "next_month": end_volume * (1 + growth_rate / 12),
            "2_months": end_volume * (1 + growth_rate / 6),
            "3_months": end_volume * (1 + growth_rate / 4)
        }
        
        return TrendAnalysis(
            keyword=keyword,
            trend_data=trend_data,
            growth_rate=growth_rate,
            volatility=volatility,
            seasonal_pattern=seasonal_pattern,
            predictions=predictions,
            confidence_score=0.75
        )
    
    async def _analyze_seasonality(self, keyword: str, platform: Platform) -> Dict[str, float]:
        """Analyze keyword seasonality"""
        # Mock seasonal analysis
        # In production, use historical data
        
        keyword_lower = keyword.lower()
        
        # Seasonal patterns for different keyword types
        if any(word in keyword_lower for word in ["christmas", "holiday", "gift"]):
            return {
                "january": 0.3, "february": 0.4, "march": 0.5, "april": 0.6,
                "may": 0.6, "june": 0.7, "july": 0.7, "august": 0.8,
                "september": 0.9, "october": 1.2, "november": 1.8, "december": 2.0
            }
        elif any(word in keyword_lower for word in ["summer", "beach", "vacation"]):
            return {
                "january": 0.4, "february": 0.5, "march": 0.7, "april": 0.9,
                "may": 1.3, "june": 1.8, "july": 2.0, "august": 1.8,
                "september": 1.2, "october": 0.8, "november": 0.5, "december": 0.4
            }
        else:
            # Stable pattern
            return {month: 1.0 for month in [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"
            ]}
    
    async def _check_competitor_coverage(
        self,
        keyword: str,
        competitor_domains: List[str]
    ) -> List[str]:
        """Check which competitors rank for a keyword"""
        # Mock competitor coverage check
        coverage = []
        
        for domain in competitor_domains:
            # Simulate ranking check
            if hash(f"{keyword}_{domain}") % 3 == 0:  # 33% chance of ranking
                coverage.append(domain)
        
        return coverage
    
    async def _calculate_content_gap_score(
        self,
        keyword: str,
        metrics: KeywordMetrics,
        competitor_coverage: List[str]
    ) -> float:
        """Calculate content gap score"""
        # Higher score = bigger gap opportunity
        
        # Base score from keyword metrics
        base_score = self._calculate_opportunity_score(metrics)
        
        # Adjust based on competitor coverage
        coverage_factor = 1.0 - (len(competitor_coverage) * 0.2)  # More competitors = less opportunity
        coverage_factor = max(0.1, coverage_factor)  # Minimum factor
        
        return base_score * coverage_factor
    
    async def _suggest_content_type(self, metrics: KeywordMetrics) -> str:
        """Suggest content type based on keyword metrics"""
        intent_mapping = {
            KeywordIntent.INFORMATIONAL: "comprehensive_guide",
            KeywordIntent.COMMERCIAL: "comparison_article",
            KeywordIntent.TRANSACTIONAL: "product_page",
            KeywordIntent.NAVIGATIONAL: "landing_page"
        }
        
        return intent_mapping.get(metrics.intent, "blog_post")
    
    def _update_avg_processing_time(self, processing_time -> None: float) -> None:
        """Update average processing time"""
        current_avg = self.analysis_stats["avg_processing_time"]
        total_analyses = self.analysis_stats["total_analyses"]
        
        if total_analyses == 1:
            self.analysis_stats["avg_processing_time"] = processing_time
        else:
            self.analysis_stats["avg_processing_time"] = (
                (current_avg * (total_analyses - 1) + processing_time) / total_analyses
            )
    
    def _update_error_rate(self) -> None:
        """Update error rate statistics"""
        # This would track errors in production
        pass
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock data for demonstration"""
        # Add some sample regional modifiers
        self.regional_modifiers = {
            "US": {"volume_multiplier": 1.0, "competition_multiplier": 1.0},
            "UK": {"volume_multiplier": 0.3, "competition_multiplier": 0.8},
            "CA": {"volume_multiplier": 0.2, "competition_multiplier": 0.7},
            "AU": {"volume_multiplier": 0.15, "competition_multiplier": 0.6}
        }
    
    async def _update_loop(self) -> None:
        """Background update loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Update every hour
                await self._refresh_cached_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in update loop: %s", e)
    
    async def _refresh_cached_data(self) -> None:
        """Refresh cached keyword data"""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, metrics in self.keyword_cache.items()
                if current_time - metrics.last_updated > self.config["cache_ttl"]
            ]
            
            for key in expired_keys:
                del self.keyword_cache[key]
            
            logger.info("Refreshed keyword cache, removed %d expired entries", len(expired_keys))

# Global keyword analysis service instance
_keyword_service: Optional[KeywordAnalysisService] = None

async def get_keyword_service() -> KeywordAnalysisService:
    """Get global keyword analysis service instance"""
    global _keyword_service
    if _keyword_service is None:
        _keyword_service = KeywordAnalysisService()
        await _keyword_service.start()
    return _keyword_service

async def shutdown_keyword_service() -> None:
    """Shutdown global keyword analysis service"""
    global _keyword_service
    if _keyword_service:
        await _keyword_service.stop()
        _keyword_service = None

if __name__ == "__main__":
    async def test_keyword_service() -> None:
        """Test keyword analysis service functionality"""
        service = KeywordAnalysisService()
        await service.start()
        
        try:
            # Analyze a keyword
            metrics = await service.analyze_keyword("content marketing")
            print(f"Keyword: {metrics.keyword}")
            print(f"Search Volume: {metrics.search_volume}")
            print(f"Difficulty: {metrics.difficulty.value}")
            print(f"Intent: {metrics.intent.value}")
            
            # Get suggestions
            suggestions = await service.get_keyword_suggestions("digital marketing", 5)
            print(f"\nKeyword suggestions:")
            for suggestion in suggestions:
                print(f"  - {suggestion.keyword} (Volume: {suggestion.search_volume})")
            
            # Cluster keywords
            keywords = ["content marketing", "digital marketing", "social media marketing", "email marketing"]
            clusters = await service.cluster_keywords(keywords)
            print(f"\nKeyword clusters: {len(clusters)}")
            for cluster in clusters:
                print(f"  - {cluster.theme}: {cluster.keywords}")
            
            # Identify opportunities
            opportunities = await service.identify_opportunities("example.com", "marketing")
            print(f"\nOpportunities found: {len(opportunities)}")
            for opp in opportunities[:3]:
                print(f"  - {opp.keyword} (Score: {opp.opportunity_score:.2f})")
            
            # Get service metrics
            metrics = await service.get_service_metrics()
            print(f"\nService metrics: {metrics}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_keyword_service())