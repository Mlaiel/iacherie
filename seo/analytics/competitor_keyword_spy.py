"""Competitor Keyword Spy - Advanced Competitor Keyword Intelligence

This module provides comprehensive competitor keyword analysis including keyword gap analysis,
ranking tracking, content strategy analysis, and competitive intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
import re
from urllib.parse import urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"      # 0-20
    EASY = "easy"                # 21-40
    MEDIUM = "medium"            # 41-60
    HARD = "hard"                # 61-80
    VERY_HARD = "very_hard"      # 81-100


class SearchIntent(Enum):
    """Search intent types"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"


class KeywordTrend(Enum):
    """Keyword trend direction"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    VOLATILE = "volatile"


@dataclass
class CompetitorKeyword:
    """Represents a competitor's keyword"""
    keyword_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str = ""
    competitor_domain: str = ""
    current_rank: int = 0
    previous_rank: int = 0
    rank_change: int = 0
    search_volume: int = 0
    keyword_difficulty: KeywordDifficulty = KeywordDifficulty.MEDIUM
    cpc: float = 0.0
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    trend: KeywordTrend = KeywordTrend.STABLE
    landing_page: str = ""
    page_title: str = ""
    meta_description: str = ""
    content_length: int = 0
    backlinks: int = 0
    page_authority: float = 0.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    traffic_estimate: float = 0.0
    opportunity_score: float = 0.0
    competition_level: float = 0.0
    seasonal_multiplier: float = 1.0
    related_keywords: List[str] = field(default_factory=list)
    serp_features: List[str] = field(default_factory=list)
    our_rank: Optional[int] = None
    gap_score: float = 0.0


@dataclass
class KeywordCluster:
    """Group of related keywords"""
    cluster_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cluster_name: str = ""
    keywords: List[str] = field(default_factory=list)
    total_search_volume: int = 0
    average_difficulty: float = 0.0
    dominant_intent: SearchIntent = SearchIntent.INFORMATIONAL
    competitors_strength: Dict[str, float] = field(default_factory=dict)
    our_coverage: float = 0.0
    opportunity_score: float = 0.0
    content_themes: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class CompetitorProfile:
    """Comprehensive competitor keyword profile"""
    competitor_domain: str
    total_keywords: int = 0
    top_keywords: List[CompetitorKeyword] = field(default_factory=list)
    keyword_clusters: List[KeywordCluster] = field(default_factory=list)
    content_strategy: Dict[str, Any] = field(default_factory=dict)
    ranking_distribution: Dict[str, int] = field(default_factory=dict)
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    difficulty_distribution: Dict[str, int] = field(default_factory=dict)
    estimated_organic_traffic: float = 0.0
    domain_authority: float = 0.0
    competitive_advantages: List[str] = field(default_factory=list)
    vulnerable_keywords: List[str] = field(default_factory=list)
    content_gaps: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)


class CompetitorKeywordSpy:
    """Advanced competitor keyword intelligence and analysis system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Competitor Keyword Spy
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.competitor_keywords: Dict[str, CompetitorKeyword] = {}
        self.competitor_profiles: Dict[str, CompetitorProfile] = {}
        self.keyword_clusters: Dict[str, KeywordCluster] = {}
        self.our_keywords: Set[str] = set()
        self.our_domain = self.config.get('our_domain', '')
        
        # AI Models setup
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.clusterer = KMeans(n_clusters=15, random_state=42)
        
        # Configuration parameters
        self.min_search_volume = self.config.get('min_search_volume', 100)
        self.max_keyword_difficulty = self.config.get('max_keyword_difficulty', 80)
        self.min_opportunity_score = self.config.get('min_opportunity_score', 0.6)
        self.tracking_period_days = self.config.get('tracking_period_days', 30)
    
    async def spy_on_competitors(
        self,
        competitors: List[str],
        our_keywords: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive competitor keyword intelligence analysis
        
        Args:
            competitors: List of competitor domains
            our_keywords: Our current keywords for gap analysis
            focus_areas: Specific areas to focus on
            
        Returns:
            Complete competitor keyword intelligence report
        """
        try:
            logger.info(f"Starting competitor keyword spy analysis for {len(competitors)} competitors")
            
            if our_keywords:
                self.our_keywords.update(our_keywords)
            
            # Analyze each competitor
            competitor_analysis = {}
            all_competitor_keywords = []
            
            for competitor in competitors:
                logger.info(f"Analyzing competitor: {competitor}")
                
                # Discover competitor keywords
                keywords = await self._discover_competitor_keywords(competitor, focus_areas)
                all_competitor_keywords.extend(keywords)
                
                # Create competitor profile
                profile = await self._create_competitor_profile(competitor, keywords)
                competitor_analysis[competitor] = profile
                self.competitor_profiles[competitor] = profile
            
            # Perform cross-competitor analysis
            cross_analysis = await self._perform_cross_competitor_analysis(competitors)
            
            # Identify keyword gaps
            keyword_gaps = await self._identify_keyword_gaps(all_competitor_keywords)
            
            # Analyze keyword clusters
            cluster_analysis = await self._analyze_keyword_clusters(all_competitor_keywords)
            
            # Identify quick win opportunities
            quick_wins = await self._identify_quick_wins(all_competitor_keywords)
            
            # Analyze content strategies
            content_strategies = await self._analyze_content_strategies(competitors)
            
            # Generate competitive insights
            competitive_insights = await self._generate_competitive_insights(
                competitors, all_competitor_keywords
            )
            
            # Track keyword trends
            trend_analysis = await self._analyze_keyword_trends(all_competitor_keywords)
            
            # Generate action plan
            action_plan = await self._generate_action_plan(
                keyword_gaps, quick_wins, competitive_insights
            )
            
            results = {
                "analysis_date": datetime.now().isoformat(),
                "competitors_analyzed": len(competitors),
                "total_keywords_discovered": len(all_competitor_keywords),
                "competitor_profiles": {
                    comp: self._profile_to_dict(profile) 
                    for comp, profile in competitor_analysis.items()
                },
                "cross_competitor_analysis": cross_analysis,
                "keyword_gaps": [self._keyword_to_dict(kw) for kw in keyword_gaps],
                "keyword_clusters": [self._cluster_to_dict(cl) for cl in cluster_analysis],
                "quick_win_opportunities": [self._keyword_to_dict(kw) for kw in quick_wins],
                "content_strategies": content_strategies,
                "competitive_insights": competitive_insights,
                "trend_analysis": trend_analysis,
                "action_plan": action_plan,
                "summary_metrics": await self._generate_summary_metrics(
                    competitors, all_competitor_keywords
                )
            }
            
            logger.info("Competitor keyword spy analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in competitor keyword spy analysis: {str(e)}")
            return {}
    
    async def _discover_competitor_keywords(
        self,
        competitor: str,
        focus_areas: Optional[List[str]] = None
    ) -> List[CompetitorKeyword]:
        """Discover keywords for a specific competitor"""
        try:
            keywords = []
            
            # Simulate keyword discovery
            # In production, this would use SEO tools APIs or scraping
            num_keywords = np.random.randint(200, 1000)
            
            keyword_templates = [
                "best {topic}", "{topic} guide", "how to {topic}", "{topic} tips",
                "{topic} tutorial", "{topic} review", "{topic} comparison",
                "{topic} software", "{topic} tools", "{topic} strategy"
            ]
            
            topics = focus_areas or [
                "marketing", "seo", "content", "social media", "email",
                "analytics", "automation", "strategy", "tools", "optimization"
            ]
            
            for i in range(num_keywords):
                topic = np.random.choice(topics)
                template = np.random.choice(keyword_templates)
                keyword_text = template.format(topic=topic)
                
                keyword = CompetitorKeyword(
                    keyword=keyword_text,
                    competitor_domain=competitor,
                    current_rank=np.random.randint(1, 100),
                    previous_rank=np.random.randint(1, 100),
                    search_volume=int(np.random.lognormal(5, 1.5)),  # Log-normal distribution
                    keyword_difficulty=self._classify_difficulty(np.random.randint(1, 100)),
                    cpc=np.random.uniform(0.1, 15.0),
                    search_intent=np.random.choice(list(SearchIntent)),
                    trend=np.random.choice(list(KeywordTrend)),
                    landing_page=f"https://{competitor}/page-{i}",
                    page_title=f"{keyword_text.title()} - {competitor.title()}",
                    content_length=np.random.randint(500, 5000),
                    backlinks=np.random.randint(0, 500),
                    page_authority=np.random.uniform(10, 90),
                    traffic_estimate=0.0,  # Will be calculated
                    competition_level=np.random.uniform(0.1, 1.0)
                )
                
                # Calculate derived metrics
                keyword.rank_change = keyword.current_rank - keyword.previous_rank
                keyword.traffic_estimate = await self._estimate_keyword_traffic(keyword)
                keyword.opportunity_score = await self._calculate_opportunity_score(keyword)
                keyword.gap_score = await self._calculate_gap_score(keyword)
                
                # Add related keywords
                keyword.related_keywords = await self._find_related_keywords(keyword_text)
                
                # Add SERP features
                keyword.serp_features = await self._identify_serp_features(keyword_text)
                
                # Check our ranking for this keyword
                keyword.our_rank = await self._check_our_ranking(keyword_text)
                
                keywords.append(keyword)
                self.competitor_keywords[keyword.keyword_id] = keyword
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error discovering competitor keywords: {str(e)}")
            return []
    
    async def _create_competitor_profile(
        self,
        competitor: str,
        keywords: List[CompetitorKeyword]
    ) -> CompetitorProfile:
        """Create comprehensive competitor profile"""
        try:
            profile = CompetitorProfile(competitor_domain=competitor)
            
            if not keywords:
                return profile
            
            # Basic metrics
            profile.total_keywords = len(keywords)
            profile.top_keywords = sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:50]
            
            # Ranking distribution
            ranking_ranges = {
                "1-3": len([k for k in keywords if 1 <= k.current_rank <= 3]),
                "4-10": len([k for k in keywords if 4 <= k.current_rank <= 10]),
                "11-20": len([k for k in keywords if 11 <= k.current_rank <= 20]),
                "21-50": len([k for k in keywords if 21 <= k.current_rank <= 50]),
                "51-100": len([k for k in keywords if 51 <= k.current_rank <= 100])
            }
            profile.ranking_distribution = ranking_ranges
            
            # Intent distribution
            intent_counts = Counter([k.search_intent.value for k in keywords])
            profile.intent_distribution = dict(intent_counts)
            
            # Difficulty distribution
            difficulty_counts = Counter([k.keyword_difficulty.value for k in keywords])
            profile.difficulty_distribution = dict(difficulty_counts)
            
            # Estimated organic traffic
            profile.estimated_organic_traffic = sum(k.traffic_estimate for k in keywords)
            
            # Domain authority (simulated)
            profile.domain_authority = np.random.uniform(40, 95)
            
            # Content strategy analysis
            profile.content_strategy = await self._analyze_content_strategy(keywords)
            
            # Competitive advantages
            profile.competitive_advantages = await self._identify_competitive_advantages(keywords)
            
            # Vulnerable keywords
            profile.vulnerable_keywords = await self._identify_vulnerable_keywords(keywords)
            
            # Content gaps
            profile.content_gaps = await self._identify_content_gaps(keywords)
            
            # Seasonal patterns
            profile.seasonal_patterns = await self._analyze_seasonal_patterns(keywords)
            
            # Keyword clusters
            profile.keyword_clusters = await self._cluster_competitor_keywords(keywords)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating competitor profile: {str(e)}")
            return CompetitorProfile(competitor_domain=competitor)
    
    async def _perform_cross_competitor_analysis(self, competitors: List[str]) -> Dict[str, Any]:
        """Analyze patterns across all competitors"""
        try:
            analysis = {
                "keyword_overlap": {},
                "shared_opportunities": [],
                "competitive_landscape": {},
                "market_leaders": {},
                "content_themes": []
            }
            
            # Calculate keyword overlap between competitors
            for i, comp1 in enumerate(competitors):
                for comp2 in competitors[i+1:]:
                    profile1 = self.competitor_profiles.get(comp1)
                    profile2 = self.competitor_profiles.get(comp2)
                    
                    if profile1 and profile2:
                        keywords1 = set(k.keyword for k in profile1.top_keywords)
                        keywords2 = set(k.keyword for k in profile2.top_keywords)
                        
                        overlap = len(keywords1 & keywords2)
                        total_unique = len(keywords1 | keywords2)
                        overlap_percentage = (overlap / total_unique * 100) if total_unique > 0 else 0
                        
                        analysis["keyword_overlap"][f"{comp1}_vs_{comp2}"] = {
                            "shared_keywords": overlap,
                            "overlap_percentage": overlap_percentage,
                            "shared_keyword_list": list(keywords1 & keywords2)[:20]
                        }
            
            # Identify shared opportunities (keywords multiple competitors target)
            all_keywords = defaultdict(list)
            for profile in self.competitor_profiles.values():
                for keyword in profile.top_keywords:
                    all_keywords[keyword.keyword].append(keyword.competitor_domain)
            
            shared_opportunities = [
                {
                    "keyword": keyword,
                    "competitors_targeting": domains,
                    "competition_level": len(domains),
                    "avg_search_volume": statistics.mean([
                        k.search_volume for k in self.competitor_keywords.values()
                        if k.keyword == keyword
                    ])
                }
                for keyword, domains in all_keywords.items()
                if len(domains) >= 2
            ]
            
            # Sort by competition level and search volume
            shared_opportunities.sort(
                key=lambda x: (x["competition_level"], x["avg_search_volume"]),
                reverse=True
            )
            analysis["shared_opportunities"] = shared_opportunities[:30]
            
            # Analyze competitive landscape
            traffic_estimates = {
                comp: profile.estimated_organic_traffic
                for comp, profile in self.competitor_profiles.items()
            }
            
            analysis["competitive_landscape"] = {
                "traffic_ranking": sorted(traffic_estimates.items(), key=lambda x: x[1], reverse=True),
                "market_distribution": traffic_estimates,
                "average_domain_authority": statistics.mean([
                    profile.domain_authority for profile in self.competitor_profiles.values()
                ])
            }
            
            # Identify market leaders in different categories
            analysis["market_leaders"] = await self._identify_market_leaders(competitors)
            
            # Extract common content themes
            analysis["content_themes"] = await self._extract_content_themes(competitors)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in cross-competitor analysis: {str(e)}")
            return {}
    
    async def _identify_keyword_gaps(self, competitor_keywords: List[CompetitorKeyword]) -> List[CompetitorKeyword]:
        """Identify keyword gaps where competitors rank but we don't"""
        try:
            gaps = []
            
            for keyword in competitor_keywords:
                # Check if this is a gap (competitor ranks well, we don't rank or rank poorly)
                if (keyword.current_rank <= 20 and  # Competitor ranks in top 20
                    keyword.search_volume >= self.min_search_volume and  # Decent search volume
                    keyword.keyword_difficulty.value != KeywordDifficulty.VERY_HARD.value and  # Not too difficult
                    (keyword.our_rank is None or keyword.our_rank > 50)):  # We don't rank well
                    
                    # This is a gap opportunity
                    keyword.gap_score = await self._calculate_gap_score(keyword)
                    
                    if keyword.gap_score >= 0.6:  # High gap score
                        gaps.append(keyword)
            
            # Sort by opportunity score
            gaps.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            return gaps[:100]  # Return top 100 gaps
            
        except Exception as e:
            logger.error(f"Error identifying keyword gaps: {str(e)}")
            return []
    
    async def _analyze_keyword_clusters(self, keywords: List[CompetitorKeyword]) -> List[KeywordCluster]:
        """Analyze and cluster keywords by theme"""
        try:
            if len(keywords) < 10:
                return []
            
            # Prepare keyword texts for clustering
            keyword_texts = [k.keyword for k in keywords]
            
            # Vectorize keywords
            try:
                tfidf_matrix = self.vectorizer.fit_transform(keyword_texts)
                
                # Cluster keywords
                n_clusters = min(20, len(keywords) // 10)
                if n_clusters < 2:
                    n_clusters = 2
                
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = clusterer.fit_predict(tfidf_matrix)
                
                # Group keywords by cluster
                clusters = defaultdict(list)
                for i, label in enumerate(cluster_labels):
                    clusters[label].append(keywords[i])
                
            except Exception as e:
                logger.warning(f"Clustering failed, using simple grouping: {str(e)}")
                # Fallback: group by first word
                clusters = defaultdict(list)
                for keyword in keywords:
                    first_word = keyword.keyword.split()[0].lower()
                    clusters[hash(first_word) % 10].append(keyword)
            
            # Create cluster objects
            keyword_clusters = []
            for cluster_id, cluster_keywords in clusters.items():
                if len(cluster_keywords) < 3:  # Skip small clusters
                    continue
                
                cluster = KeywordCluster(
                    cluster_name=await self._generate_cluster_name(cluster_keywords),
                    keywords=[k.keyword for k in cluster_keywords],
                    total_search_volume=sum(k.search_volume for k in cluster_keywords),
                    average_difficulty=statistics.mean([
                        self._difficulty_to_number(k.keyword_difficulty) for k in cluster_keywords
                    ]),
                    dominant_intent=Counter([k.search_intent for k in cluster_keywords]).most_common(1)[0][0]
                )
                
                # Analyze competitor strength in this cluster
                cluster.competitors_strength = await self._analyze_cluster_competition(cluster_keywords)
                
                # Calculate our coverage
                cluster.our_coverage = await self._calculate_our_cluster_coverage(cluster_keywords)
                
                # Calculate opportunity score
                cluster.opportunity_score = await self._calculate_cluster_opportunity(cluster)
                
                # Extract content themes
                cluster.content_themes = await self._extract_cluster_themes(cluster_keywords)
                
                # Generate recommendations
                cluster.recommended_actions = await self._generate_cluster_recommendations(cluster)
                
                keyword_clusters.append(cluster)
                self.keyword_clusters[cluster.cluster_id] = cluster
            
            # Sort by opportunity score
            keyword_clusters.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            return keyword_clusters
            
        except Exception as e:
            logger.error(f"Error analyzing keyword clusters: {str(e)}")
            return []
    
    async def _identify_quick_wins(self, keywords: List[CompetitorKeyword]) -> List[CompetitorKeyword]:
        """Identify quick win keyword opportunities"""
        try:
            quick_wins = []
            
            for keyword in keywords:
                # Criteria for quick wins:
                # 1. Medium to high search volume
                # 2. Low to medium difficulty
                # 3. We either don't rank or rank poorly
                # 4. Competitor ranks decently but not dominantly
                
                is_quick_win = (
                    keyword.search_volume >= 500 and  # Decent volume
                    keyword.keyword_difficulty.value in [KeywordDifficulty.EASY.value, KeywordDifficulty.MEDIUM.value] and
                    (keyword.our_rank is None or keyword.our_rank > 30) and  # We don't rank well
                    10 <= keyword.current_rank <= 30 and  # Competitor ranks decently but not great
                    keyword.competition_level <= 0.7  # Not too competitive
                )
                
                if is_quick_win:
                    # Calculate quick win score
                    quick_win_score = await self._calculate_quick_win_score(keyword)
                    keyword.opportunity_score = quick_win_score
                    
                    if quick_win_score >= 0.7:
                        quick_wins.append(keyword)
            
            # Sort by opportunity score
            quick_wins.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            return quick_wins[:50]  # Return top 50 quick wins
            
        except Exception as e:
            logger.error(f"Error identifying quick wins: {str(e)}")
            return []
    
    async def _analyze_content_strategies(self, competitors: List[str]) -> Dict[str, Any]:
        """Analyze content strategies of competitors"""
        try:
            strategies = {}
            
            for competitor in competitors:
                profile = self.competitor_profiles.get(competitor)
                if not profile:
                    continue
                
                strategy = {
                    "content_focus": await self._identify_content_focus(profile),
                    "content_length_strategy": await self._analyze_content_length_strategy(profile),
                    "keyword_targeting_approach": await self._analyze_keyword_targeting(profile),
                    "content_frequency": await self._estimate_content_frequency(profile),
                    "content_themes": profile.content_strategy.get("themes", []),
                    "strongest_topics": await self._identify_strongest_topics(profile),
                    "content_gaps": profile.content_gaps,
                    "optimization_patterns": await self._identify_optimization_patterns(profile)
                }
                
                strategies[competitor] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error analyzing content strategies: {str(e)}")
            return {}
    
    async def _generate_competitive_insights(
        self,
        competitors: List[str],
        keywords: List[CompetitorKeyword]
    ) -> Dict[str, Any]:
        """Generate actionable competitive insights"""
        try:
            insights = {
                "market_opportunities": [],
                "competitive_threats": [],
                "strategy_recommendations": [],
                "content_opportunities": [],
                "keyword_recommendations": []
            }
            
            # Market opportunities
            high_volume_low_competition = [
                k for k in keywords
                if k.search_volume >= 1000 and k.competition_level <= 0.5
            ]
            insights["market_opportunities"] = [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "competition_level": k.competition_level,
                    "opportunity_type": "high_volume_low_competition"
                }
                for k in high_volume_low_competition[:10]
            ]
            
            # Competitive threats (keywords where competitors are gaining)
            rising_keywords = [
                k for k in keywords
                if k.trend == KeywordTrend.RISING and k.current_rank <= 10
            ]
            insights["competitive_threats"] = [
                {
                    "keyword": k.keyword,
                    "competitor": k.competitor_domain,
                    "current_rank": k.current_rank,
                    "threat_level": "high" if k.current_rank <= 3 else "medium"
                }
                for k in rising_keywords[:10]
            ]
            
            # Strategy recommendations
            insights["strategy_recommendations"] = await self._generate_strategy_recommendations(
                competitors, keywords
            )
            
            # Content opportunities
            insights["content_opportunities"] = await self._identify_content_opportunities(keywords)
            
            # Keyword recommendations
            insights["keyword_recommendations"] = await self._generate_keyword_recommendations(keywords)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating competitive insights: {str(e)}")
            return {}
    
    async def _analyze_keyword_trends(self, keywords: List[CompetitorKeyword]) -> Dict[str, Any]:
        """Analyze trends in competitor keywords"""
        try:
            trends = {
                "rising_keywords": [],
                "declining_keywords": [],
                "stable_keywords": [],
                "seasonal_keywords": [],
                "volatile_keywords": [],
                "trend_summary": {}
            }
            
            # Categorize keywords by trend
            for keyword in keywords:
                trend_data = {
                    "keyword": keyword.keyword,
                    "competitor": keyword.competitor_domain,
                    "search_volume": keyword.search_volume,
                    "current_rank": keyword.current_rank,
                    "rank_change": keyword.rank_change
                }
                
                if keyword.trend == KeywordTrend.RISING:
                    trends["rising_keywords"].append(trend_data)
                elif keyword.trend == KeywordTrend.DECLINING:
                    trends["declining_keywords"].append(trend_data)
                elif keyword.trend == KeywordTrend.SEASONAL:
                    trends["seasonal_keywords"].append(trend_data)
                elif keyword.trend == KeywordTrend.VOLATILE:
                    trends["volatile_keywords"].append(trend_data)
                else:
                    trends["stable_keywords"].append(trend_data)
            
            # Generate trend summary
            total_keywords = len(keywords)
            trends["trend_summary"] = {
                "rising_percentage": len(trends["rising_keywords"]) / total_keywords * 100 if total_keywords > 0 else 0,
                "declining_percentage": len(trends["declining_keywords"]) / total_keywords * 100 if total_keywords > 0 else 0,
                "stable_percentage": len(trends["stable_keywords"]) / total_keywords * 100 if total_keywords > 0 else 0,
                "most_volatile_competitor": await self._find_most_volatile_competitor(keywords),
                "trending_themes": await self._identify_trending_themes(keywords)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing keyword trends: {str(e)}")
            return {}
    
    async def _generate_action_plan(
        self,
        keyword_gaps: List[CompetitorKeyword],
        quick_wins: List[CompetitorKeyword],
        competitive_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable plan based on analysis"""
        try:
            action_plan = {
                "immediate_actions": [],
                "short_term_goals": [],
                "long_term_strategy": [],
                "content_calendar": [],
                "optimization_priorities": []
            }
            
            # Immediate actions (quick wins)
            for keyword in quick_wins[:10]:
                action_plan["immediate_actions"].append({
                    "action": f"Create optimized content for '{keyword.keyword}'",
                    "keyword": keyword.keyword,
                    "search_volume": keyword.search_volume,
                    "difficulty": keyword.keyword_difficulty.value,
                    "estimated_timeframe": "1-2 weeks",
                    "priority": "high" if keyword.opportunity_score >= 0.8 else "medium"
                })
            
            # Short-term goals (keyword gaps)
            for keyword in keyword_gaps[:20]:
                action_plan["short_term_goals"].append({
                    "goal": f"Improve ranking for '{keyword.keyword}'",
                    "keyword": keyword.keyword,
                    "competitor_rank": keyword.current_rank,
                    "our_rank": keyword.our_rank,
                    "search_volume": keyword.search_volume,
                    "estimated_timeframe": "1-3 months",
                    "recommended_strategy": await self._recommend_keyword_strategy(keyword)
                })
            
            # Long-term strategy
            cluster_opportunities = sorted(
                self.keyword_clusters.values(),
                key=lambda x: x.opportunity_score,
                reverse=True
            )[:5]
            
            for cluster in cluster_opportunities:
                action_plan["long_term_strategy"].append({
                    "strategy": f"Dominate '{cluster.cluster_name}' topic cluster",
                    "keywords_count": len(cluster.keywords),
                    "total_search_volume": cluster.total_search_volume,
                    "opportunity_score": cluster.opportunity_score,
                    "estimated_timeframe": "6-12 months",
                    "recommended_actions": cluster.recommended_actions
                })
            
            # Content calendar suggestions
            action_plan["content_calendar"] = await self._generate_content_calendar(
                keyword_gaps, quick_wins
            )
            
            # Optimization priorities
            action_plan["optimization_priorities"] = await self._prioritize_optimizations(
                keyword_gaps, quick_wins, competitive_insights
            )
            
            return action_plan
            
        except Exception as e:
            logger.error(f"Error generating action plan: {str(e)}")
            return {}
    
    # Helper methods
    def _classify_difficulty(self, difficulty_score: int) -> KeywordDifficulty:
        """Classify keyword difficulty based on score"""
        if difficulty_score <= 20:
            return KeywordDifficulty.VERY_EASY
        elif difficulty_score <= 40:
            return KeywordDifficulty.EASY
        elif difficulty_score <= 60:
            return KeywordDifficulty.MEDIUM
        elif difficulty_score <= 80:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    def _difficulty_to_number(self, difficulty: KeywordDifficulty) -> float:
        """Convert difficulty enum to number"""
        mapping = {
            KeywordDifficulty.VERY_EASY: 10,
            KeywordDifficulty.EASY: 30,
            KeywordDifficulty.MEDIUM: 50,
            KeywordDifficulty.HARD: 70,
            KeywordDifficulty.VERY_HARD: 90
        }
        return mapping.get(difficulty, 50)
    
    async def _estimate_keyword_traffic(self, keyword: CompetitorKeyword) -> float:
        """Estimate traffic for keyword based on rank and volume"""
        # CTR estimates by position
        ctr_by_position = {
            1: 0.284, 2: 0.147, 3: 0.106, 4: 0.073, 5: 0.053,
            6: 0.04, 7: 0.031, 8: 0.025, 9: 0.02, 10: 0.016
        }
        
        if keyword.current_rank <= 10:
            ctr = ctr_by_position.get(keyword.current_rank, 0.01)
        elif keyword.current_rank <= 20:
            ctr = 0.005
        else:
            ctr = 0.001
        
        return keyword.search_volume * ctr
    
    async def _calculate_opportunity_score(self, keyword: CompetitorKeyword) -> float:
        """Calculate opportunity score for keyword"""
        # Factors: search volume, difficulty, competition level, our current rank
        volume_score = min(keyword.search_volume / 10000, 1.0)  # Normalize to 0-1
        difficulty_score = 1.0 - (self._difficulty_to_number(keyword.keyword_difficulty) / 100)
        competition_score = 1.0 - keyword.competition_level
        
        # Rank opportunity (higher score if competitor ranks well and we don't)
        rank_opportunity = 0.5
        if keyword.current_rank <= 10 and (keyword.our_rank is None or keyword.our_rank > 20):
            rank_opportunity = 1.0
        elif keyword.current_rank <= 20 and (keyword.our_rank is None or keyword.our_rank > 50):
            rank_opportunity = 0.8
        
        # Weighted average
        opportunity_score = (
            volume_score * 0.3 +
            difficulty_score * 0.25 +
            competition_score * 0.2 +
            rank_opportunity * 0.25
        )
        
        return min(opportunity_score, 1.0)
    
    async def _calculate_gap_score(self, keyword: CompetitorKeyword) -> float:
        """Calculate gap score (how much we're missing out)"""
        if keyword.our_rank is None:
            our_rank = 101  # Not ranking
        else:
            our_rank = keyword.our_rank
        
        # Gap is larger when competitor ranks much better than us
        rank_gap = max(0, our_rank - keyword.current_rank) / 100
        
        # Weight by search volume and traffic potential
        volume_weight = min(keyword.search_volume / 5000, 1.0)
        traffic_potential = keyword.traffic_estimate / 1000
        
        gap_score = rank_gap * volume_weight * min(traffic_potential, 1.0)
        
        return min(gap_score, 1.0)
    
    async def _calculate_quick_win_score(self, keyword: CompetitorKeyword) -> float:
        """Calculate quick win score"""
        # Quick wins should have:
        # 1. Good search volume
        # 2. Low competition
        # 3. Reasonable difficulty
        # 4. Competitor not dominating
        
        volume_score = min(keyword.search_volume / 2000, 1.0)
        difficulty_score = 1.0 - (self._difficulty_to_number(keyword.keyword_difficulty) / 100)
        competition_score = 1.0 - keyword.competition_level
        
        # Penalty if competitor ranks too well (harder to overtake)
        rank_penalty = 0.0
        if keyword.current_rank <= 3:
            rank_penalty = 0.3
        elif keyword.current_rank <= 10:
            rank_penalty = 0.1
        
        quick_win_score = (
            volume_score * 0.4 +
            difficulty_score * 0.3 +
            competition_score * 0.3 -
            rank_penalty
        )
        
        return max(0.0, min(quick_win_score, 1.0))
    
    # Placeholder methods for complex operations
    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords"""
        return [f"{keyword} tips", f"best {keyword}", f"{keyword} guide"]
    
    async def _identify_serp_features(self, keyword: str) -> List[str]:
        """Identify SERP features for keyword"""
        features = ["featured_snippet", "people_also_ask", "image_pack"]
        return np.random.choice(features, size=np.random.randint(0, 3), replace=False).tolist()
    
    async def _check_our_ranking(self, keyword: str) -> Optional[int]:
        """Check our ranking for keyword"""
        if keyword.lower() in [k.lower() for k in self.our_keywords]:
            return np.random.randint(1, 50)  # We rank somewhere
        else:
            return None if np.random.random() < 0.7 else np.random.randint(51, 100)
    
    async def _analyze_content_strategy(self, keywords: List[CompetitorKeyword]) -> Dict[str, Any]:
        """Analyze content strategy from keywords"""
        return {
            "avg_content_length": statistics.mean([k.content_length for k in keywords]),
            "themes": ["marketing", "strategy", "tools"],
            "optimization_level": "high"
        }
    
    async def _identify_competitive_advantages(self, keywords: List[CompetitorKeyword]) -> List[str]:
        """Identify competitive advantages"""
        return ["strong_domain_authority", "consistent_content", "good_user_experience"]
    
    async def _identify_vulnerable_keywords(self, keywords: List[CompetitorKeyword]) -> List[str]:
        """Identify vulnerable keywords"""
        vulnerable = [k.keyword for k in keywords if k.current_rank > 20 and k.search_volume > 500]
        return vulnerable[:10]
    
    async def _identify_content_gaps(self, keywords: List[CompetitorKeyword]) -> List[str]:
        """Identify content gaps"""
        return ["how_to_guides", "comparison_content", "case_studies"]
    
    async def _analyze_seasonal_patterns(self, keywords: List[CompetitorKeyword]) -> Dict[str, float]:
        """Analyze seasonal patterns"""
        return {"spring": 1.2, "summer": 0.8, "fall": 1.1, "winter": 0.9}
    
    async def _cluster_competitor_keywords(self, keywords: List[CompetitorKeyword]) -> List[KeywordCluster]:
        """Create keyword clusters for competitor"""
        # Simplified clustering - would use actual clustering in production
        return []
    
    def _keyword_to_dict(self, keyword: CompetitorKeyword) -> Dict[str, Any]:
        """Convert keyword to dictionary"""
        return {
            "keyword": keyword.keyword,
            "competitor_domain": keyword.competitor_domain,
            "current_rank": keyword.current_rank,
            "search_volume": keyword.search_volume,
            "keyword_difficulty": keyword.keyword_difficulty.value,
            "search_intent": keyword.search_intent.value,
            "traffic_estimate": keyword.traffic_estimate,
            "opportunity_score": keyword.opportunity_score,
            "gap_score": keyword.gap_score,
            "our_rank": keyword.our_rank
        }
    
    def _profile_to_dict(self, profile: CompetitorProfile) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "competitor_domain": profile.competitor_domain,
            "total_keywords": profile.total_keywords,
            "estimated_organic_traffic": profile.estimated_organic_traffic,
            "domain_authority": profile.domain_authority,
            "ranking_distribution": profile.ranking_distribution,
            "intent_distribution": profile.intent_distribution,
            "competitive_advantages": profile.competitive_advantages,
            "vulnerable_keywords": profile.vulnerable_keywords[:10],
            "content_gaps": profile.content_gaps
        }
    
    def _cluster_to_dict(self, cluster: KeywordCluster) -> Dict[str, Any]:
        """Convert cluster to dictionary"""
        return {
            "cluster_name": cluster.cluster_name,
            "keywords_count": len(cluster.keywords),
            "total_search_volume": cluster.total_search_volume,
            "average_difficulty": cluster.average_difficulty,
            "opportunity_score": cluster.opportunity_score,
            "our_coverage": cluster.our_coverage,
            "recommended_actions": cluster.recommended_actions
        }
    
    # Additional placeholder methods
    async def _generate_cluster_name(self, keywords: List[CompetitorKeyword]) -> str:
        """Generate name for keyword cluster"""
        common_words = Counter()
        for keyword in keywords:
            words = keyword.keyword.split()
            common_words.update(words)
        
        most_common = common_words.most_common(1)
        if most_common:
            return f"{most_common[0][0]}_cluster"
        return "mixed_cluster"
    
    async def _analyze_cluster_competition(self, keywords: List[CompetitorKeyword]) -> Dict[str, float]:
        """Analyze competition in keyword cluster"""
        competitors = {}
        for keyword in keywords:
            comp = keyword.competitor_domain
            if comp not in competitors:
                competitors[comp] = 0
            competitors[comp] += keyword.search_volume
        
        return competitors
    
    async def _calculate_our_cluster_coverage(self, keywords: List[CompetitorKeyword]) -> float:
        """Calculate our coverage in cluster"""
        our_keywords_in_cluster = sum(1 for k in keywords if k.our_rank is not None and k.our_rank <= 50)
        return our_keywords_in_cluster / len(keywords) if keywords else 0
    
    async def _calculate_cluster_opportunity(self, cluster: KeywordCluster) -> float:
        """Calculate opportunity score for cluster"""
        return (1.0 - cluster.our_coverage) * min(cluster.total_search_volume / 50000, 1.0)
    
    async def _extract_cluster_themes(self, keywords: List[CompetitorKeyword]) -> List[str]:
        """Extract content themes from cluster"""
        return ["guides", "tutorials", "tips"]
    
    async def _generate_cluster_recommendations(self, cluster: KeywordCluster) -> List[str]:
        """Generate recommendations for cluster"""
        return [
            f"Create comprehensive content covering {cluster.cluster_name}",
            f"Target high-volume keywords in this cluster",
            f"Optimize existing content for cluster keywords"
        ]
    
    async def _generate_summary_metrics(
        self, competitors: List[str], keywords: List[CompetitorKeyword]
    ) -> Dict[str, Any]:
        """Generate summary metrics"""
        return {
            "total_keywords_analyzed": len(keywords),
            "average_search_volume": statistics.mean([k.search_volume for k in keywords]) if keywords else 0,
            "top_opportunity_score": max([k.opportunity_score for k in keywords]) if keywords else 0,
            "total_estimated_traffic": sum([k.traffic_estimate for k in keywords]),
            "quick_wins_identified": len([k for k in keywords if k.opportunity_score >= 0.7]),
            "keyword_gaps_found": len([k for k in keywords if k.gap_score >= 0.6])
        }
    
    # Additional helper methods with simplified implementations
    async def _identify_market_leaders(self, competitors: List[str]) -> Dict[str, str]:
        """Identify market leaders in different categories"""
        return {
            "organic_traffic": competitors[0] if competitors else "",
            "keyword_diversity": competitors[1] if len(competitors) > 1 else "",
            "content_volume": competitors[0] if competitors else ""
        }
    
    async def _extract_content_themes(self, competitors: List[str]) -> List[str]:
        """Extract common content themes"""
        return ["marketing_automation", "seo_optimization", "content_strategy"]
    
    async def _identify_content_focus(self, profile: CompetitorProfile) -> str:
        """Identify main content focus"""
        intent_dist = profile.intent_distribution
        if not intent_dist:
            return "mixed"
        
        dominant_intent = max(intent_dist.items(), key=lambda x: x[1])[0]
        return f"{dominant_intent}_focused"
    
    async def _analyze_content_length_strategy(self, profile: CompetitorProfile) -> str:
        """Analyze content length strategy"""
        avg_length = profile.content_strategy.get("avg_content_length", 1500)
        if avg_length > 2500:
            return "long_form_content"
        elif avg_length > 1000:
            return "medium_form_content"
        else:
            return "short_form_content"
    
    async def _analyze_keyword_targeting(self, profile: CompetitorProfile) -> str:
        """Analyze keyword targeting approach"""
        return "mixed_targeting"  # Simplified
    
    async def _estimate_content_frequency(self, profile: CompetitorProfile) -> str:
        """Estimate content publishing frequency"""
        return "weekly"  # Simplified
    
    async def _identify_strongest_topics(self, profile: CompetitorProfile) -> List[str]:
        """Identify competitor's strongest topics"""
        return ["marketing", "seo", "content"]
    
    async def _identify_optimization_patterns(self, profile: CompetitorProfile) -> List[str]:
        """Identify optimization patterns"""
        return ["structured_data", "internal_linking", "keyword_optimization"]
    
    async def _generate_strategy_recommendations(self, competitors: List[str], keywords: List[CompetitorKeyword]) -> List[str]:
        """Generate strategy recommendations"""
        return [
            "Focus on long-tail keywords with lower competition",
            "Create comprehensive content clusters",
            "Improve technical SEO foundation"
        ]
    
    async def _identify_content_opportunities(self, keywords: List[CompetitorKeyword]) -> List[Dict[str, Any]]:
        """Identify content opportunities"""
        return [
            {
                "content_type": "comprehensive_guide",
                "topic": "digital marketing",
                "keywords_to_target": 5,
                "estimated_traffic": 2500
            }
        ]
    
    async def _generate_keyword_recommendations(self, keywords: List[CompetitorKeyword]) -> List[Dict[str, Any]]:
        """Generate keyword recommendations"""
        high_opportunity = [k for k in keywords if k.opportunity_score >= 0.7][:10]
        return [
            {
                "keyword": k.keyword,
                "priority": "high" if k.opportunity_score >= 0.8 else "medium",
                "action": "create_new_content" if k.our_rank is None else "optimize_existing",
                "estimated_timeframe": "1-2 months"
            }
            for k in high_opportunity
        ]
    
    async def _find_most_volatile_competitor(self, keywords: List[CompetitorKeyword]) -> str:
        """Find most volatile competitor"""
        volatility_by_competitor = defaultdict(int)
        for keyword in keywords:
            if keyword.trend == KeywordTrend.VOLATILE:
                volatility_by_competitor[keyword.competitor_domain] += 1
        
        if volatility_by_competitor:
            return max(volatility_by_competitor.items(), key=lambda x: x[1])[0]
        return "none"
    
    async def _identify_trending_themes(self, keywords: List[CompetitorKeyword]) -> List[str]:
        """Identify trending themes"""
        rising_keywords = [k for k in keywords if k.trend == KeywordTrend.RISING]
        themes = Counter()
        
        for keyword in rising_keywords:
            words = keyword.keyword.split()
            themes.update(words)
        
        return [theme for theme, count in themes.most_common(5)]
    
    async def _recommend_keyword_strategy(self, keyword: CompetitorKeyword) -> str:
        """Recommend strategy for specific keyword"""
        if keyword.keyword_difficulty == KeywordDifficulty.EASY:
            return "direct_targeting"
        elif keyword.keyword_difficulty == KeywordDifficulty.MEDIUM:
            return "content_cluster_approach"
        else:
            return "long_tail_variants"
    
    async def _generate_content_calendar(self, gaps: List[CompetitorKeyword], quick_wins: List[CompetitorKeyword]) -> List[Dict[str, Any]]:
        """Generate content calendar suggestions"""
        calendar = []
        
        # Quick wins first
        for i, keyword in enumerate(quick_wins[:8]):
            calendar.append({
                "week": i + 1,
                "content_type": "optimized_article",
                "target_keyword": keyword.keyword,
                "priority": "high",
                "estimated_effort": "medium"
            })
        
        return calendar
    
    async def _prioritize_optimizations(self, gaps: List[CompetitorKeyword], quick_wins: List[CompetitorKeyword], insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize optimization efforts"""
        priorities = []
        
        # High priority: Quick wins
        for keyword in quick_wins[:5]:
            priorities.append({
                "priority": "high",
                "action": f"Create content for '{keyword.keyword}'",
                "expected_impact": "immediate_traffic_gain",
                "effort_required": "low"
            })
        
        # Medium priority: Keyword gaps
        for keyword in gaps[:10]:
            priorities.append({
                "priority": "medium",
                "action": f"Optimize for '{keyword.keyword}'",
                "expected_impact": "ranking_improvement",
                "effort_required": "medium"
            })
        
        return priorities


# Example usage
async def main() -> None:
    """Example usage of Competitor Keyword Spy"""
    try:
        # Initialize spy
        config = {
            'our_domain': 'oursite.com',
            'min_search_volume': 500,
            'min_opportunity_score': 0.6,
            'tracking_period_days': 30
        }
        
        spy = CompetitorKeywordSpy(config)
        
        # Example data
        competitors = ["competitor1.com", "competitor2.com", "competitor3.com"]
        our_keywords = ["digital marketing", "seo tools", "content strategy"]
        focus_areas = ["marketing", "seo", "content", "automation"]
        
        print(f"🕵️ Starting competitor keyword spy analysis...")
        print(f"   Competitors: {len(competitors)}")
        print(f"   Focus Areas: {', '.join(focus_areas)}")
        
        # Perform analysis
        results = await spy.spy_on_competitors(
            competitors=competitors,
            our_keywords=our_keywords,
            focus_areas=focus_areas
        )
        
        # Print summary
        summary = results.get('summary_metrics', {})
        print(f"\n📊 Analysis Results:")
        print(f"   Total Keywords Analyzed: {summary.get('total_keywords_analyzed', 0)}")
        print(f"   Average Search Volume: {summary.get('average_search_volume', 0):.0f}")
        print(f"   Quick Wins Identified: {summary.get('quick_wins_identified', 0)}")
        print(f"   Keyword Gaps Found: {summary.get('keyword_gaps_found', 0)}")
        
        # Show top opportunities
        gaps = results.get('keyword_gaps', [])
        print(f"\n🎯 Top Keyword Gaps ({len(gaps)}):")
        for i, gap in enumerate(gaps[:5]):
            print(f"\n{i+1}. {gap['keyword']}")
            print(f"   Competitor: {gap['competitor_domain']}")
            print(f"   Their Rank: {gap['current_rank']}")
            print(f"   Our Rank: {gap.get('our_rank', 'Not ranking')}")
            print(f"   Search Volume: {gap['search_volume']}")
            print(f"   Opportunity Score: {gap['opportunity_score']:.2f}")
            print(f"   Difficulty: {gap['keyword_difficulty']}")
        
        # Show quick wins
        quick_wins = results.get('quick_win_opportunities', [])
        print(f"\n⚡ Quick Win Opportunities ({len(quick_wins)}):")
        for i, win in enumerate(quick_wins[:5]):
            print(f"\n{i+1}. {win['keyword']}")
            print(f"   Search Volume: {win['search_volume']}")
            print(f"   Difficulty: {win['keyword_difficulty']}")
            print(f"   Opportunity Score: {win['opportunity_score']:.2f}")
        
        # Show action plan
        action_plan = results.get('action_plan', {})
        immediate_actions = action_plan.get('immediate_actions', [])
        print(f"\n📋 Immediate Actions ({len(immediate_actions)}):")
        for i, action in enumerate(immediate_actions[:3]):
            print(f"\n{i+1}. {action['action']}")
            print(f"   Keyword: {action['keyword']}")
            print(f"   Priority: {action['priority']}")
            print(f"   Timeframe: {action['estimated_timeframe']}")
        
        # Show competitive insights
        insights = results.get('competitive_insights', {})
        threats = insights.get('competitive_threats', [])
        print(f"\n⚠️ Competitive Threats ({len(threats)}):")
        for threat in threats[:3]:
            print(f"   • {threat['competitor']} ranking #{threat['current_rank']} for '{threat['keyword']}'")
        
        print("\n✅ Competitor keyword spy analysis completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())