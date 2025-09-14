"""SERP Feature Tracker - Advanced Search Engine Results Page Analysis

This module tracks and analyzes SERP features across different search engines
to identify optimization opportunities and monitor feature changes.

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

logger = logging.getLogger(__name__)


class SearchEngine(Enum):
    """Supported search engines"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"


class SERPFeatureType(Enum):
    """Types of SERP features"""
    FEATURED_SNIPPET = "featured_snippet"
    PEOPLE_ALSO_ASK = "people_also_ask"
    LOCAL_PACK = "local_pack"
    KNOWLEDGE_PANEL = "knowledge_panel"
    IMAGE_PACK = "image_pack"
    VIDEO_CAROUSEL = "video_carousel"
    NEWS_RESULTS = "news_results"
    SHOPPING_RESULTS = "shopping_results"
    REVIEWS = "reviews"
    SITELINKS = "sitelinks"
    TOP_STORIES = "top_stories"
    TWITTER_CARDS = "twitter_cards"
    RECIPES = "recipes"
    JOBS = "jobs"
    EVENTS = "events"
    FLIGHTS = "flights"
    HOTELS = "hotels"
    PRODUCTS = "products"
    ACADEMIC = "academic"
    FINANCE = "finance"
    SPORTS = "sports"
    WEATHER = "weather"
    TRANSLATIONS = "translations"
    DEFINITIONS = "definitions"
    CALCULATOR = "calculator"
    CONVERTER = "converter"
    AI_OVERVIEW = "ai_overview"


class FeatureStatus(Enum):
    """SERP feature status"""
    PRESENT = "present"
    ABSENT = "absent"
    INTERMITTENT = "intermittent"
    NEW = "new"
    REMOVED = "removed"


@dataclass
class SERPFeature:
    """Represents a SERP feature instance"""
    feature_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_type: SERPFeatureType = SERPFeatureType.FEATURED_SNIPPET
    search_engine: SearchEngine = SearchEngine.GOOGLE
    keyword: str = ""
    position: int = 0
    content: str = ""
    source_url: str = ""
    source_domain: str = ""
    title: str = ""
    description: str = ""
    images: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: FeatureStatus = FeatureStatus.PRESENT
    confidence_score: float = 0.0
    click_through_estimate: float = 0.0
    visibility_score: float = 0.0
    competition_level: float = 0.0
    optimization_opportunity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KeywordSERPAnalysis:
    """SERP analysis for a specific keyword"""
    keyword: str
    search_engine: SearchEngine
    analysis_date: datetime = field(default_factory=datetime.now)
    total_features: int = 0
    features_present: List[SERPFeatureType] = field(default_factory=list)
    features_absent: List[SERPFeatureType] = field(default_factory=list)
    our_presence: Dict[str, bool] = field(default_factory=dict)
    competitor_presence: Dict[str, List[str]] = field(default_factory=dict)
    opportunity_score: float = 0.0
    feature_volatility: float = 0.0
    historical_changes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SERPTrend:
    """SERP feature trend analysis"""
    feature_type: SERPFeatureType
    search_engine: SearchEngine
    trend_period: str = "30_days"
    appearance_rate: float = 0.0
    growth_rate: float = 0.0
    volatility_score: float = 0.0
    keywords_affected: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    predicted_change: str = "stable"


class SERPFeatureTracker:
    """Advanced SERP feature tracking and analysis system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize SERP Feature Tracker
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.serp_features: Dict[str, SERPFeature] = {}
        self.keyword_analysis: Dict[str, KeywordSERPAnalysis] = {}
        self.feature_trends: Dict[str, SERPTrend] = {}
        self.monitoring_keywords: Set[str] = set()
        self.our_domain = self.config.get('our_domain', '')
        
        # Configuration parameters
        self.check_frequency_hours = self.config.get('check_frequency_hours', 6)
        self.volatility_threshold = self.config.get('volatility_threshold', 0.3)
        self.opportunity_threshold = self.config.get('opportunity_threshold', 0.6)
        self.supported_engines = self.config.get('supported_engines', [
            SearchEngine.GOOGLE, SearchEngine.BING
        ])
    
    async def track_serp_features(
        self,
        keywords: List[str],
        search_engines: Optional[List[SearchEngine]] = None,
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive SERP feature tracking
        
        Args:
            keywords: Keywords to monitor
            search_engines: Search engines to track
            competitors: Competitor domains to monitor
            
        Returns:
            Complete SERP feature analysis
        """
        try:
            logger.info(f"Starting SERP feature tracking for {len(keywords)} keywords")
            
            engines = search_engines or self.supported_engines
            self.monitoring_keywords.update(keywords)
            
            # Track features for each keyword and engine
            tracking_results = {}
            
            for keyword in keywords:
                keyword_results = {}
                
                for engine in engines:
                    # Detect SERP features
                    features = await self._detect_serp_features(keyword, engine)
                    
                    # Analyze keyword SERP
                    analysis = await self._analyze_keyword_serp(
                        keyword, engine, features, competitors
                    )
                    
                    keyword_results[engine.value] = {
                        'features': [self._feature_to_dict(f) for f in features],
                        'analysis': self._analysis_to_dict(analysis)
                    }
                    
                    # Store analysis
                    analysis_key = f"{keyword}_{engine.value}"
                    self.keyword_analysis[analysis_key] = analysis
                
                tracking_results[keyword] = keyword_results
            
            # Analyze trends across all keywords
            trend_analysis = await self._analyze_feature_trends(keywords, engines)
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                keywords, engines, competitors
            )
            
            # Generate competitive insights
            competitive_insights = await self._generate_competitive_insights(
                keywords, engines, competitors
            )
            
            # Calculate feature volatility
            volatility_analysis = await self._analyze_feature_volatility(keywords, engines)
            
            results = {
                "tracking_date": datetime.now().isoformat(),
                "keywords_tracked": len(keywords),
                "search_engines": [e.value for e in engines],
                "keyword_results": tracking_results,
                "trend_analysis": trend_analysis,
                "optimization_opportunities": opportunities,
                "competitive_insights": competitive_insights,
                "volatility_analysis": volatility_analysis,
                "summary_metrics": await self._generate_summary_metrics(keywords, engines)
            }
            
            logger.info(f"SERP feature tracking completed for {len(keywords)} keywords")
            return results
            
        except Exception as e:
            logger.error(f"Error in SERP feature tracking: {str(e)}")
            return {}
    
    async def _detect_serp_features(self, keyword: str, engine: SearchEngine) -> List[SERPFeature]:
        """Detect SERP features for a keyword on a specific search engine"""
        try:
            features = []
            
            # Simulate SERP feature detection
            # In production, this would use real SERP scraping/API
            
            # Define feature probabilities for different engines
            feature_probabilities = {
                SearchEngine.GOOGLE: {
                    SERPFeatureType.FEATURED_SNIPPET: 0.35,
                    SERPFeatureType.PEOPLE_ALSO_ASK: 0.65,
                    SERPFeatureType.LOCAL_PACK: 0.25,
                    SERPFeatureType.KNOWLEDGE_PANEL: 0.20,
                    SERPFeatureType.IMAGE_PACK: 0.45,
                    SERPFeatureType.VIDEO_CAROUSEL: 0.30,
                    SERPFeatureType.NEWS_RESULTS: 0.15,
                    SERPFeatureType.SHOPPING_RESULTS: 0.20,
                    SERPFeatureType.SITELINKS: 0.40,
                    SERPFeatureType.AI_OVERVIEW: 0.25
                },
                SearchEngine.BING: {
                    SERPFeatureType.FEATURED_SNIPPET: 0.25,
                    SERPFeatureType.PEOPLE_ALSO_ASK: 0.50,
                    SERPFeatureType.LOCAL_PACK: 0.20,
                    SERPFeatureType.KNOWLEDGE_PANEL: 0.15,
                    SERPFeatureType.IMAGE_PACK: 0.40,
                    SERPFeatureType.VIDEO_CAROUSEL: 0.25,
                    SERPFeatureType.NEWS_RESULTS: 0.20,
                    SERPFeatureType.SHOPPING_RESULTS: 0.25
                }
            }
            
            probabilities = feature_probabilities.get(engine, feature_probabilities[SearchEngine.GOOGLE])
            
            position = 1
            for feature_type, probability in probabilities.items():
                if np.random.random() < probability:
                    feature = SERPFeature(
                        feature_type=feature_type,
                        search_engine=engine,
                        keyword=keyword,
                        position=position,
                        content=await self._generate_feature_content(feature_type, keyword),
                        source_url=await self._generate_source_url(feature_type),
                        source_domain=await self._generate_source_domain(feature_type),
                        title=await self._generate_feature_title(feature_type, keyword),
                        description=await self._generate_feature_description(feature_type, keyword),
                        confidence_score=np.random.uniform(0.7, 0.95),
                        click_through_estimate=await self._estimate_ctr(feature_type, position),
                        visibility_score=await self._calculate_visibility_score(feature_type, position),
                        competition_level=np.random.uniform(0.3, 0.9),
                        optimization_opportunity=await self._calculate_optimization_opportunity(feature_type)
                    )
                    
                    # Add metadata specific to feature type
                    feature.metadata = await self._generate_feature_metadata(feature_type, keyword)
                    
                    features.append(feature)
                    self.serp_features[feature.feature_id] = feature
                    position += 1
            
            return features
            
        except Exception as e:
            logger.error(f"Error detecting SERP features: {str(e)}")
            return []
    
    async def _analyze_keyword_serp(
        self,
        keyword: str,
        engine: SearchEngine,
        features: List[SERPFeature],
        competitors: Optional[List[str]] = None
    ) -> KeywordSERPAnalysis:
        """Analyze SERP for a specific keyword"""
        try:
            analysis = KeywordSERPAnalysis(
                keyword=keyword,
                search_engine=engine,
                total_features=len(features)
            )
            
            # Categorize features
            analysis.features_present = [f.feature_type for f in features]
            all_possible_features = list(SERPFeatureType)
            analysis.features_absent = [
                f for f in all_possible_features 
                if f not in analysis.features_present
            ]
            
            # Check our presence in features
            if self.our_domain:
                analysis.our_presence = await self._check_our_presence(features, self.our_domain)
            
            # Check competitor presence
            if competitors:
                analysis.competitor_presence = await self._check_competitor_presence(features, competitors)
            
            # Calculate opportunity score
            analysis.opportunity_score = await self._calculate_keyword_opportunity_score(
                keyword, features, analysis.our_presence
            )
            
            # Analyze feature volatility
            analysis.feature_volatility = await self._calculate_keyword_volatility(keyword, engine)
            
            # Add historical changes
            analysis.historical_changes = await self._get_historical_changes(keyword, engine)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing keyword SERP: {str(e)}")
            return KeywordSERPAnalysis(keyword=keyword, search_engine=engine)
    
    async def _analyze_feature_trends(
        self,
        keywords: List[str],
        engines: List[SearchEngine]
    ) -> Dict[str, Any]:
        """Analyze trends in SERP features"""
        try:
            trends = {}
            
            # Analyze each feature type
            for feature_type in SERPFeatureType:
                feature_data = []
                
                for engine in engines:
                    # Calculate appearance rate
                    total_keywords = len(keywords)
                    keywords_with_feature = 0
                    
                    for keyword in keywords:
                        analysis_key = f"{keyword}_{engine.value}"
                        if analysis_key in self.keyword_analysis:
                            analysis = self.keyword_analysis[analysis_key]
                            if feature_type in analysis.features_present:
                                keywords_with_feature += 1
                    
                    appearance_rate = keywords_with_feature / total_keywords if total_keywords > 0 else 0
                    
                    # Create trend object
                    trend = SERPTrend(
                        feature_type=feature_type,
                        search_engine=engine,
                        appearance_rate=appearance_rate,
                        growth_rate=await self._calculate_growth_rate(feature_type, engine),
                        volatility_score=await self._calculate_feature_volatility_score(feature_type, engine),
                        keywords_affected=[
                            kw for kw in keywords 
                            if f"{kw}_{engine.value}" in self.keyword_analysis and 
                            feature_type in self.keyword_analysis[f"{kw}_{engine.value}"].features_present
                        ],
                        predicted_change=await self._predict_feature_change(feature_type, engine)
                    )
                    
                    trend_key = f"{feature_type.value}_{engine.value}"
                    trends[trend_key] = self._trend_to_dict(trend)
                    self.feature_trends[trend_key] = trend
            
            # Add summary statistics
            trends['summary'] = {
                'most_common_features': await self._get_most_common_features(keywords, engines),
                'emerging_features': await self._identify_emerging_features(keywords, engines),
                'declining_features': await self._identify_declining_features(keywords, engines),
                'stable_features': await self._identify_stable_features(keywords, engines)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing feature trends: {str(e)}")
            return {}
    
    async def _identify_optimization_opportunities(
        self,
        keywords: List[str],
        engines: List[SearchEngine],
        competitors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Identify SERP feature optimization opportunities"""
        try:
            opportunities = []
            
            for keyword in keywords:
                for engine in engines:
                    analysis_key = f"{keyword}_{engine.value}"
                    if analysis_key not in self.keyword_analysis:
                        continue
                    
                    analysis = self.keyword_analysis[analysis_key]
                    
                    # Check each feature type for opportunities
                    for feature_type in SERPFeatureType:
                        if feature_type in analysis.features_present:
                            # Feature exists, check if we can capture it
                            our_presence = analysis.our_presence.get(feature_type.value, False)
                            
                            if not our_presence:
                                # We're not present in this feature - opportunity!
                                opportunity_score = await self._calculate_feature_opportunity_score(
                                    feature_type, keyword, engine, competitors
                                )
                                
                                if opportunity_score >= self.opportunity_threshold:
                                    opportunity = {
                                        'keyword': keyword,
                                        'search_engine': engine.value,
                                        'feature_type': feature_type.value,
                                        'opportunity_score': opportunity_score,
                                        'priority': await self._calculate_opportunity_priority(opportunity_score),
                                        'implementation_difficulty': await self._assess_implementation_difficulty(feature_type),
                                        'estimated_traffic_gain': await self._estimate_traffic_gain(feature_type, keyword),
                                        'recommended_actions': await self._get_optimization_recommendations(feature_type, keyword),
                                        'competitor_analysis': await self._analyze_competitor_advantage(
                                            feature_type, keyword, competitors
                                        )
                                    }
                                    opportunities.append(opportunity)
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            return opportunities[:50]  # Return top 50 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {str(e)}")
            return []
    
    async def _generate_competitive_insights(
        self,
        keywords: List[str],
        engines: List[SearchEngine],
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate competitive insights from SERP feature analysis"""
        try:
            insights = {
                'competitor_dominance': {},
                'feature_gaps': {},
                'competitive_advantages': {},
                'market_share_estimates': {}
            }
            
            if not competitors:
                return insights
            
            # Analyze competitor dominance in each feature type
            for feature_type in SERPFeatureType:
                competitor_scores = {comp: 0 for comp in competitors}
                total_occurrences = 0
                
                for keyword in keywords:
                    for engine in engines:
                        analysis_key = f"{keyword}_{engine.value}"
                        if analysis_key in self.keyword_analysis:
                            analysis = self.keyword_analysis[analysis_key]
                            
                            if feature_type in analysis.features_present:
                                total_occurrences += 1
                                
                                # Check which competitors appear in this feature
                                for comp in competitors:
                                    comp_presence = analysis.competitor_presence.get(feature_type.value, [])
                                    if comp in comp_presence:
                                        competitor_scores[comp] += 1
                
                # Calculate dominance percentages
                if total_occurrences > 0:
                    insights['competitor_dominance'][feature_type.value] = {
                        comp: (score / total_occurrences * 100)
                        for comp, score in competitor_scores.items()
                    }
            
            # Identify feature gaps where competitors are strong but we're weak
            for feature_type in SERPFeatureType:
                competitor_strength = sum(
                    insights['competitor_dominance'].get(feature_type.value, {}).values()
                )
                our_strength = await self._calculate_our_feature_strength(feature_type, keywords, engines)
                
                if competitor_strength > our_strength * 2:  # Competitors 2x stronger
                    insights['feature_gaps'][feature_type.value] = {
                        'competitor_strength': competitor_strength,
                        'our_strength': our_strength,
                        'gap_severity': 'high' if competitor_strength > our_strength * 5 else 'medium'
                    }
            
            # Calculate estimated market share based on SERP presence
            total_serp_presence = 0
            competitor_presence = {comp: 0 for comp in competitors}
            our_presence = 0
            
            for keyword in keywords:
                for engine in engines:
                    analysis_key = f"{keyword}_{engine.value}"
                    if analysis_key in self.keyword_analysis:
                        analysis = self.keyword_analysis[analysis_key]
                        
                        # Count presence across all features
                        for feature_type in analysis.features_present:
                            total_serp_presence += 1
                            
                            # Check our presence
                            if analysis.our_presence.get(feature_type.value, False):
                                our_presence += 1
                            
                            # Check competitor presence
                            for comp in competitors:
                                comp_presence = analysis.competitor_presence.get(feature_type.value, [])
                                if comp in comp_presence:
                                    competitor_presence[comp] += 1
            
            if total_serp_presence > 0:
                insights['market_share_estimates'] = {
                    'our_share': (our_presence / total_serp_presence * 100),
                    'competitor_shares': {
                        comp: (presence / total_serp_presence * 100)
                        for comp, presence in competitor_presence.items()
                    }
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating competitive insights: {str(e)}")
            return {}
    
    async def _analyze_feature_volatility(
        self,
        keywords: List[str],
        engines: List[SearchEngine]
    ) -> Dict[str, Any]:
        """Analyze volatility of SERP features"""
        try:
            volatility_analysis = {
                'overall_volatility': 0.0,
                'feature_volatility': {},
                'keyword_volatility': {},
                'engine_volatility': {},
                'volatility_trends': {}
            }
            
            # Calculate feature-level volatility
            for feature_type in SERPFeatureType:
                volatility_scores = []
                
                for keyword in keywords:
                    for engine in engines:
                        volatility = await self._calculate_keyword_volatility(keyword, engine)
                        volatility_scores.append(volatility)
                
                if volatility_scores:
                    volatility_analysis['feature_volatility'][feature_type.value] = {
                        'mean_volatility': statistics.mean(volatility_scores),
                        'max_volatility': max(volatility_scores),
                        'min_volatility': min(volatility_scores),
                        'volatility_classification': await self._classify_volatility(
                            statistics.mean(volatility_scores)
                        )
                    }
            
            # Calculate keyword-level volatility
            for keyword in keywords:
                keyword_volatilities = []
                
                for engine in engines:
                    volatility = await self._calculate_keyword_volatility(keyword, engine)
                    keyword_volatilities.append(volatility)
                
                if keyword_volatilities:
                    volatility_analysis['keyword_volatility'][keyword] = statistics.mean(keyword_volatilities)
            
            # Calculate engine-level volatility
            for engine in engines:
                engine_volatilities = []
                
                for keyword in keywords:
                    volatility = await self._calculate_keyword_volatility(keyword, engine)
                    engine_volatilities.append(volatility)
                
                if engine_volatilities:
                    volatility_analysis['engine_volatility'][engine.value] = statistics.mean(engine_volatilities)
            
            # Calculate overall volatility
            all_volatilities = []
            for keyword in keywords:
                for engine in engines:
                    volatility = await self._calculate_keyword_volatility(keyword, engine)
                    all_volatilities.append(volatility)
            
            if all_volatilities:
                volatility_analysis['overall_volatility'] = statistics.mean(all_volatilities)
            
            return volatility_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing feature volatility: {str(e)}")
            return {}
    
    # Helper methods
    async def _generate_feature_content(self, feature_type: SERPFeatureType, keyword: str) -> str:
        """Generate simulated feature content"""
        content_templates = {
            SERPFeatureType.FEATURED_SNIPPET: f"A comprehensive answer about {keyword}...",
            SERPFeatureType.PEOPLE_ALSO_ASK: f"Related questions about {keyword}",
            SERPFeatureType.LOCAL_PACK: f"Local businesses related to {keyword}",
            SERPFeatureType.KNOWLEDGE_PANEL: f"Knowledge panel information for {keyword}",
            SERPFeatureType.IMAGE_PACK: f"Images related to {keyword}",
            SERPFeatureType.VIDEO_CAROUSEL: f"Videos about {keyword}",
            SERPFeatureType.NEWS_RESULTS: f"Latest news about {keyword}",
            SERPFeatureType.AI_OVERVIEW: f"AI-generated overview of {keyword}"
        }
        return content_templates.get(feature_type, f"Content about {keyword}")
    
    async def _generate_source_url(self, feature_type: SERPFeatureType) -> str:
        """Generate simulated source URL"""
        return f"https://example-{feature_type.value}.com/content"
    
    async def _generate_source_domain(self, feature_type: SERPFeatureType) -> str:
        """Generate simulated source domain"""
        return f"example-{feature_type.value}.com"
    
    async def _generate_feature_title(self, feature_type: SERPFeatureType, keyword: str) -> str:
        """Generate simulated feature title"""
        return f"{keyword.title()} - {feature_type.value.replace('_', ' ').title()}"
    
    async def _generate_feature_description(self, feature_type: SERPFeatureType, keyword: str) -> str:
        """Generate simulated feature description"""
        return f"Detailed information about {keyword} in {feature_type.value} format"
    
    async def _estimate_ctr(self, feature_type: SERPFeatureType, position: int) -> float:
        """Estimate click-through rate for feature"""
        base_ctrs = {
            SERPFeatureType.FEATURED_SNIPPET: 0.35,
            SERPFeatureType.PEOPLE_ALSO_ASK: 0.15,
            SERPFeatureType.LOCAL_PACK: 0.25,
            SERPFeatureType.KNOWLEDGE_PANEL: 0.10,
            SERPFeatureType.IMAGE_PACK: 0.08,
            SERPFeatureType.VIDEO_CAROUSEL: 0.20,
            SERPFeatureType.NEWS_RESULTS: 0.12,
            SERPFeatureType.AI_OVERVIEW: 0.30
        }
        
        base_ctr = base_ctrs.get(feature_type, 0.05)
        position_factor = max(0.1, 1.0 - (position - 1) * 0.1)
        
        return base_ctr * position_factor
    
    async def _calculate_visibility_score(self, feature_type: SERPFeatureType, position: int) -> float:
        """Calculate visibility score for feature"""
        visibility_weights = {
            SERPFeatureType.FEATURED_SNIPPET: 1.0,
            SERPFeatureType.AI_OVERVIEW: 0.95,
            SERPFeatureType.LOCAL_PACK: 0.8,
            SERPFeatureType.KNOWLEDGE_PANEL: 0.7,
            SERPFeatureType.VIDEO_CAROUSEL: 0.75,
            SERPFeatureType.IMAGE_PACK: 0.6,
            SERPFeatureType.PEOPLE_ALSO_ASK: 0.5,
            SERPFeatureType.NEWS_RESULTS: 0.65
        }
        
        base_visibility = visibility_weights.get(feature_type, 0.3)
        position_penalty = (position - 1) * 0.05
        
        return max(0.1, base_visibility - position_penalty)
    
    async def _calculate_optimization_opportunity(self, feature_type: SERPFeatureType) -> float:
        """Calculate optimization opportunity for feature type"""
        opportunity_scores = {
            SERPFeatureType.FEATURED_SNIPPET: 0.9,
            SERPFeatureType.PEOPLE_ALSO_ASK: 0.7,
            SERPFeatureType.LOCAL_PACK: 0.8,
            SERPFeatureType.VIDEO_CAROUSEL: 0.75,
            SERPFeatureType.IMAGE_PACK: 0.6,
            SERPFeatureType.AI_OVERVIEW: 0.85,
            SERPFeatureType.KNOWLEDGE_PANEL: 0.5,
            SERPFeatureType.NEWS_RESULTS: 0.4
        }
        
        return opportunity_scores.get(feature_type, 0.3)
    
    async def _generate_feature_metadata(self, feature_type: SERPFeatureType, keyword: str) -> Dict[str, Any]:
        """Generate feature-specific metadata"""
        base_metadata = {
            "keyword": keyword,
            "detection_confidence": np.random.uniform(0.8, 0.95),
            "last_updated": datetime.now().isoformat()
        }
        
        # Add feature-specific metadata
        if feature_type == SERPFeatureType.FEATURED_SNIPPET:
            base_metadata.update({
                "snippet_type": np.random.choice(["paragraph", "list", "table"]),
                "word_count": np.random.randint(50, 200)
            })
        elif feature_type == SERPFeatureType.LOCAL_PACK:
            base_metadata.update({
                "business_count": 3,
                "map_present": True,
                "reviews_shown": True
            })
        elif feature_type == SERPFeatureType.VIDEO_CAROUSEL:
            base_metadata.update({
                "video_count": np.random.randint(3, 8),
                "platforms": ["youtube", "vimeo"]
            })
        
        return base_metadata
    
    async def _check_our_presence(self, features: List[SERPFeature], our_domain: str) -> Dict[str, bool]:
        """Check our presence in SERP features"""
        presence = {}
        
        for feature in features:
            feature_key = feature.feature_type.value
            
            # Check if our domain appears in this feature
            if our_domain in feature.source_domain or our_domain in feature.source_url:
                presence[feature_key] = True
            else:
                presence[feature_key] = False
        
        return presence
    
    async def _check_competitor_presence(
        self,
        features: List[SERPFeature],
        competitors: List[str]
    ) -> Dict[str, List[str]]:
        """Check competitor presence in SERP features"""
        presence = {}
        
        for feature in features:
            feature_key = feature.feature_type.value
            competing_domains = []
            
            for competitor in competitors:
                if competitor in feature.source_domain or competitor in feature.source_url:
                    competing_domains.append(competitor)
            
            presence[feature_key] = competing_domains
        
        return presence
    
    async def _calculate_keyword_opportunity_score(
        self,
        keyword: str,
        features: List[SERPFeature],
        our_presence: Dict[str, bool]
    ) -> float:
        """Calculate opportunity score for keyword"""
        total_features = len(features)
        if total_features == 0:
            return 0.0
        
        # Count features where we're not present
        missed_opportunities = sum(1 for present in our_presence.values() if not present)
        
        # Weight by feature importance
        weighted_score = 0.0
        total_weight = 0.0
        
        for feature in features:
            feature_weight = await self._get_feature_weight(feature.feature_type)
            total_weight += feature_weight
            
            if not our_presence.get(feature.feature_type.value, False):
                weighted_score += feature_weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        
        return 0.0
    
    async def _get_feature_weight(self, feature_type: SERPFeatureType) -> float:
        """Get importance weight for feature type"""
        weights = {
            SERPFeatureType.FEATURED_SNIPPET: 1.0,
            SERPFeatureType.AI_OVERVIEW: 0.95,
            SERPFeatureType.LOCAL_PACK: 0.85,
            SERPFeatureType.KNOWLEDGE_PANEL: 0.8,
            SERPFeatureType.VIDEO_CAROUSEL: 0.75,
            SERPFeatureType.PEOPLE_ALSO_ASK: 0.7,
            SERPFeatureType.IMAGE_PACK: 0.6,
            SERPFeatureType.NEWS_RESULTS: 0.65,
            SERPFeatureType.SHOPPING_RESULTS: 0.55
        }
        
        return weights.get(feature_type, 0.3)
    
    async def _calculate_keyword_volatility(self, keyword: str, engine: SearchEngine) -> float:
        """Calculate volatility for keyword-engine combination"""
        # Simulate volatility calculation
        # In production, this would analyze historical SERP data
        return np.random.uniform(0.1, 0.8)
    
    async def _get_historical_changes(self, keyword: str, engine: SearchEngine) -> List[Dict[str, Any]]:
        """Get historical SERP changes"""
        # Simulate historical changes
        changes = []
        for i in range(5):  # Last 5 changes
            change = {
                "date": (datetime.now() - timedelta(days=i*7)).isoformat(),
                "change_type": np.random.choice(["feature_added", "feature_removed", "position_change"]),
                "feature_affected": np.random.choice(list(SERPFeatureType)).value,
                "impact_score": np.random.uniform(0.1, 0.9)
            }
            changes.append(change)
        
        return changes
    
    def _feature_to_dict(self, feature: SERPFeature) -> Dict[str, Any]:
        """Convert SERPFeature to dictionary"""
        return {
            "feature_id": feature.feature_id,
            "feature_type": feature.feature_type.value,
            "search_engine": feature.search_engine.value,
            "keyword": feature.keyword,
            "position": feature.position,
            "title": feature.title,
            "source_domain": feature.source_domain,
            "confidence_score": feature.confidence_score,
            "click_through_estimate": feature.click_through_estimate,
            "visibility_score": feature.visibility_score,
            "optimization_opportunity": feature.optimization_opportunity,
            "timestamp": feature.timestamp.isoformat()
        }
    
    def _analysis_to_dict(self, analysis: KeywordSERPAnalysis) -> Dict[str, Any]:
        """Convert KeywordSERPAnalysis to dictionary"""
        return {
            "keyword": analysis.keyword,
            "search_engine": analysis.search_engine.value,
            "total_features": analysis.total_features,
            "features_present": [f.value for f in analysis.features_present],
            "features_absent": [f.value for f in analysis.features_absent],
            "our_presence": analysis.our_presence,
            "competitor_presence": analysis.competitor_presence,
            "opportunity_score": analysis.opportunity_score,
            "feature_volatility": analysis.feature_volatility,
            "analysis_date": analysis.analysis_date.isoformat()
        }
    
    def _trend_to_dict(self, trend: SERPTrend) -> Dict[str, Any]:
        """Convert SERPTrend to dictionary"""
        return {
            "feature_type": trend.feature_type.value,
            "search_engine": trend.search_engine.value,
            "appearance_rate": trend.appearance_rate,
            "growth_rate": trend.growth_rate,
            "volatility_score": trend.volatility_score,
            "keywords_affected": trend.keywords_affected,
            "predicted_change": trend.predicted_change
        }
    
    # Additional helper methods with simplified implementations
    async def _calculate_growth_rate(self, feature_type: SERPFeatureType, engine: SearchEngine) -> float:
        return np.random.uniform(-0.1, 0.3)
    
    async def _calculate_feature_volatility_score(self, feature_type: SERPFeatureType, engine: SearchEngine) -> float:
        return np.random.uniform(0.1, 0.6)
    
    async def _predict_feature_change(self, feature_type: SERPFeatureType, engine: SearchEngine) -> str:
        return np.random.choice(["growing", "stable", "declining"])
    
    async def _get_most_common_features(self, keywords: List[str], engines: List[SearchEngine]) -> List[str]:
        return ["featured_snippet", "people_also_ask", "image_pack"]
    
    async def _identify_emerging_features(self, keywords: List[str], engines: List[SearchEngine]) -> List[str]:
        return ["ai_overview", "video_carousel"]
    
    async def _identify_declining_features(self, keywords: List[str], engines: List[SearchEngine]) -> List[str]:
        return ["knowledge_panel"]
    
    async def _identify_stable_features(self, keywords: List[str], engines: List[SearchEngine]) -> List[str]:
        return ["sitelinks", "local_pack"]
    
    async def _calculate_feature_opportunity_score(
        self, feature_type: SERPFeatureType, keyword: str, engine: SearchEngine, competitors: Optional[List[str]]
    ) -> float:
        return np.random.uniform(0.4, 0.9)
    
    async def _calculate_opportunity_priority(self, opportunity_score: float) -> str:
        if opportunity_score >= 0.8:
            return "high"
        elif opportunity_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    async def _assess_implementation_difficulty(self, feature_type: SERPFeatureType) -> str:
        difficulty_map = {
            SERPFeatureType.FEATURED_SNIPPET: "medium",
            SERPFeatureType.PEOPLE_ALSO_ASK: "easy",
            SERPFeatureType.LOCAL_PACK: "hard",
            SERPFeatureType.KNOWLEDGE_PANEL: "hard",
            SERPFeatureType.IMAGE_PACK: "easy",
            SERPFeatureType.VIDEO_CAROUSEL: "medium"
        }
        return difficulty_map.get(feature_type, "medium")
    
    async def _estimate_traffic_gain(self, feature_type: SERPFeatureType, keyword: str) -> float:
        return np.random.uniform(100, 2000)
    
    async def _get_optimization_recommendations(self, feature_type: SERPFeatureType, keyword: str) -> List[str]:
        recommendations = {
            SERPFeatureType.FEATURED_SNIPPET: [
                "Create comprehensive answer content",
                "Use structured data markup",
                "Optimize for question-based queries"
            ],
            SERPFeatureType.PEOPLE_ALSO_ASK: [
                "Add FAQ sections to content",
                "Target related questions",
                "Use clear question-answer format"
            ],
            SERPFeatureType.LOCAL_PACK: [
                "Optimize Google My Business profile",
                "Gather positive reviews",
                "Ensure NAP consistency"
            ]
        }
        return recommendations.get(feature_type, ["Optimize content for this feature"])
    
    async def _analyze_competitor_advantage(
        self, feature_type: SERPFeatureType, keyword: str, competitors: Optional[List[str]]
    ) -> Dict[str, Any]:
        return {
            "dominant_competitors": competitors[:2] if competitors else [],
            "their_strategies": ["high-quality_content", "structured_data"],
            "gap_analysis": "competitor_has_better_content_structure"
        }
    
    async def _calculate_our_feature_strength(
        self, feature_type: SERPFeatureType, keywords: List[str], engines: List[SearchEngine]
    ) -> float:
        return np.random.uniform(10, 40)
    
    async def _classify_volatility(self, volatility_score: float) -> str:
        if volatility_score >= 0.6:
            return "high"
        elif volatility_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    async def _generate_summary_metrics(self, keywords: List[str], engines: List[SearchEngine]) -> Dict[str, Any]:
        """Generate summary metrics for the tracking session"""
        return {
            "total_features_detected": len(self.serp_features),
            "average_features_per_keyword": len(self.serp_features) / len(keywords) if keywords else 0,
            "most_common_feature": "featured_snippet",
            "highest_opportunity_score": max(
                [analysis.opportunity_score for analysis in self.keyword_analysis.values()],
                default=0
            ),
            "engines_analyzed": len(engines),
            "volatility_level": "medium"
        }


# Example usage
async def main() -> None:
    """Example usage of SERP Feature Tracker"""
    try:
        # Initialize tracker
        config = {
            'our_domain': 'oursite.com',
            'check_frequency_hours': 6,
            'opportunity_threshold': 0.6,
            'supported_engines': [SearchEngine.GOOGLE, SearchEngine.BING]
        }
        
        tracker = SERPFeatureTracker(config)
        
        # Example data
        keywords = [
            "content marketing strategy", "seo optimization", "digital marketing trends",
            "social media marketing", "email marketing automation"
        ]
        competitors = ["competitor1.com", "competitor2.com", "competitor3.com"]
        engines = [SearchEngine.GOOGLE, SearchEngine.BING]
        
        print(f"🔍 Tracking SERP features for {len(keywords)} keywords...")
        
        # Track SERP features
        results = await tracker.track_serp_features(
            keywords=keywords,
            search_engines=engines,
            competitors=competitors
        )
        
        # Print summary
        summary = results.get('summary_metrics', {})
        print(f"\n📊 SERP Feature Tracking Results:")
        print(f"   Total Features Detected: {summary.get('total_features_detected', 0)}")
        print(f"   Average Features per Keyword: {summary.get('average_features_per_keyword', 0):.1f}")
        print(f"   Most Common Feature: {summary.get('most_common_feature', 'N/A')}")
        print(f"   Highest Opportunity Score: {summary.get('highest_opportunity_score', 0):.2f}")
        
        # Show opportunities
        opportunities = results.get('optimization_opportunities', [])
        print(f"\n🎯 Top Optimization Opportunities ({len(opportunities)}):")
        for i, opp in enumerate(opportunities[:5]):
            print(f"\n{i+1}. {opp['keyword']} - {opp['feature_type']}")
            print(f"   Engine: {opp['search_engine']}")
            print(f"   Opportunity Score: {opp['opportunity_score']:.2f}")
            print(f"   Priority: {opp['priority']}")
            print(f"   Estimated Traffic Gain: {opp['estimated_traffic_gain']:.0f}")
            print(f"   Implementation Difficulty: {opp['implementation_difficulty']}")
        
        # Show competitive insights
        competitive = results.get('competitive_insights', {})
        market_share = competitive.get('market_share_estimates', {})
        print(f"\n🏆 Market Share Estimates:")
        print(f"   Our Share: {market_share.get('our_share', 0):.1f}%")
        
        competitor_shares = market_share.get('competitor_shares', {})
        for comp, share in competitor_shares.items():
            print(f"   {comp}: {share:.1f}%")
        
        # Show volatility analysis
        volatility = results.get('volatility_analysis', {})
        print(f"\n📈 Volatility Analysis:")
        print(f"   Overall Volatility: {volatility.get('overall_volatility', 0):.2f}")
        print(f"   Volatility Level: {summary.get('volatility_level', 'unknown')}")
        
        print("\n✅ SERP Feature Tracking completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())