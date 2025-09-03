"""Keyword Analyzer - AI-Powered Keyword Analysis Engine

Advanced keyword analysis system for SEO optimization with AI-driven insights,
competitive analysis, and strategic keyword recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SearchIntent(Enum):
    """Types of search intent"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


@dataclass
class KeywordMetrics:
    """Comprehensive keyword metrics"""
    keyword: str
    search_volume: int
    difficulty: KeywordDifficulty
    cpc: float
    competition: float
    intent: SearchIntent
    trend_score: float
    opportunity_score: float
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)


@dataclass
class KeywordAnalysisResult:
    """Complete keyword analysis result"""
    primary_keywords: List[KeywordMetrics]
    secondary_keywords: List[KeywordMetrics]
    long_tail_keywords: List[KeywordMetrics]
    competitors: List[Dict[str, Any]]
    content_gaps: List[str]
    optimization_recommendations: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.now)


class KeywordAnalyzer:
    """AI-powered keyword analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.language = self.config.get('language', 'en')
        self.geo_location = self.config.get('geo_location', 'US')
        self.max_keywords = self.config.get('max_keywords', 100)
        
        # AI analysis weights
        self.analysis_weights = {
            'search_volume': 0.30,
            'competition': 0.25,
            'relevance': 0.20,
            'intent_match': 0.15,
            'trend_potential': 0.10
        }
        
        # Keyword difficulty thresholds
        self.difficulty_thresholds = {
            KeywordDifficulty.VERY_EASY: (0, 20),
            KeywordDifficulty.EASY: (21, 40),
            KeywordDifficulty.MEDIUM: (41, 60),
            KeywordDifficulty.HARD: (61, 80),
            KeywordDifficulty.VERY_HARD: (81, 100)
        }
        
        logger.info("KeywordAnalyzer initialized with AI analysis capabilities")
    
    async def analyze_keywords(
        self,
        seed_keywords: List[str],
        content_context: Optional[Dict[str, Any]] = None,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> KeywordAnalysisResult:
        """Perform comprehensive keyword analysis"""
        try:
            logger.info(f"Starting keyword analysis for {len(seed_keywords)} seed keywords")
            
            # Expand seed keywords
            expanded_keywords = await self._expand_keywords(seed_keywords, content_context)
            
            # Analyze each keyword
            keyword_metrics = []
            for keyword in expanded_keywords:
                metrics = await self._analyze_single_keyword(keyword, content_context)
                if metrics:
                    keyword_metrics.append(metrics)
            
            # Categorize keywords
            primary_keywords = await self._categorize_primary_keywords(keyword_metrics)
            secondary_keywords = await self._categorize_secondary_keywords(keyword_metrics)
            long_tail_keywords = await self._categorize_long_tail_keywords(keyword_metrics)
            
            # Competitive analysis
            competitors = await self._analyze_competitors(seed_keywords)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(keyword_metrics, competitors)
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                keyword_metrics, content_context, target_audience
            )
            
            result = KeywordAnalysisResult(
                primary_keywords=primary_keywords,
                secondary_keywords=secondary_keywords,
                long_tail_keywords=long_tail_keywords,
                competitors=competitors,
                content_gaps=content_gaps,
                optimization_recommendations=recommendations
            )
            
            logger.info(f"Keyword analysis completed: {len(primary_keywords)} primary, "
                       f"{len(secondary_keywords)} secondary, {len(long_tail_keywords)} long-tail")
            
            return result
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            raise
    
    async def _expand_keywords(
        self,
        seed_keywords: List[str],
        content_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Expand seed keywords using AI techniques"""
        expanded = set(seed_keywords)
        
        for keyword in seed_keywords:
            # Generate variations
            variations = await self._generate_keyword_variations(keyword)
            expanded.update(variations)
            
            # Generate related terms
            related = await self._generate_related_keywords(keyword, content_context)
            expanded.update(related)
            
            # Generate question-based keywords
            questions = await self._generate_question_keywords(keyword)
            expanded.update(questions)
        
        return list(expanded)[:self.max_keywords]
    
    async def _analyze_single_keyword(
        self,
        keyword: str,
        content_context: Optional[Dict[str, Any]] = None
    ) -> Optional[KeywordMetrics]:
        """Analyze a single keyword comprehensively"""
        try:
            # Simulate search volume (in real implementation, use SEO APIs)
            search_volume = await self._get_search_volume(keyword)
            
            # Calculate difficulty
            difficulty = await self._calculate_keyword_difficulty(keyword)
            
            # Estimate CPC
            cpc = await self._estimate_cpc(keyword)
            
            # Calculate competition
            competition = await self._calculate_competition(keyword)
            
            # Determine search intent
            intent = await self._determine_search_intent(keyword)
            
            # Calculate trend score
            trend_score = await self._calculate_trend_score(keyword)
            
            # Calculate opportunity score
            opportunity_score = await self._calculate_opportunity_score(
                search_volume, difficulty, competition, trend_score
            )
            
            # Get seasonal patterns
            seasonal_patterns = await self._analyze_seasonal_patterns(keyword)
            
            # Find related keywords
            related_keywords = await self._find_related_keywords(keyword)
            
            # Generate questions
            questions = await self._generate_keyword_questions(keyword)
            
            return KeywordMetrics(
                keyword=keyword,
                search_volume=search_volume,
                difficulty=difficulty,
                cpc=cpc,
                competition=competition,
                intent=intent,
                trend_score=trend_score,
                opportunity_score=opportunity_score,
                seasonal_patterns=seasonal_patterns,
                related_keywords=related_keywords,
                questions=questions
            )
            
        except Exception as e:
            logger.warning(f"Failed to analyze keyword '{keyword}': {e}")
            return None
    
    async def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations"""
        variations = []
        
        # Add plurals/singulars
        if keyword.endswith('s'):
            variations.append(keyword[:-1])
        else:
            variations.append(keyword + 's')
        
        # Add synonyms (simplified version)
        synonyms = {
            'buy': ['purchase', 'get', 'acquire'],
            'best': ['top', 'excellent', 'outstanding'],
            'guide': ['tutorial', 'how-to', 'instructions'],
            'tips': ['advice', 'suggestions', 'recommendations']
        }
        
        for word, syns in synonyms.items():
            if word in keyword.lower():
                for syn in syns:
                    variations.append(keyword.lower().replace(word, syn))
        
        return variations[:10]
    
    async def _generate_related_keywords(
        self,
        keyword: str,
        content_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate related keywords based on context"""
        related = []
        
        # Add modifiers
        modifiers = ['best', 'top', 'how to', 'what is', 'why', 'when', 'where']
        for modifier in modifiers:
            related.append(f"{modifier} {keyword}")
        
        # Add context-specific terms
        if content_context:
            content_type = content_context.get('type', '')
            if content_type == 'music':
                related.extend([
                    f"{keyword} music",
                    f"{keyword} song",
                    f"{keyword} artist",
                    f"{keyword} album"
                ])
            elif content_type == 'video':
                related.extend([
                    f"{keyword} video",
                    f"{keyword} tutorial",
                    f"{keyword} review"
                ])
        
        return related[:15]
    
    async def _generate_question_keywords(self, keyword: str) -> List[str]:
        """Generate question-based keywords"""
        questions = [
            f"how to {keyword}",
            f"what is {keyword}",
            f"why {keyword}",
            f"when to {keyword}",
            f"where to {keyword}",
            f"how much {keyword}",
            f"how many {keyword}",
            f"can you {keyword}",
            f"should you {keyword}",
            f"will {keyword}"
        ]
        return questions
    
    async def _get_search_volume(self, keyword: str) -> int:
        """Get search volume for keyword (simulated)"""
        # In real implementation, integrate with Google Keyword Planner, SEMrush, etc.
        import random
        base_volume = len(keyword.split()) * 1000
        return random.randint(base_volume, base_volume * 10)
    
    async def _calculate_keyword_difficulty(self, keyword: str) -> KeywordDifficulty:
        """Calculate keyword difficulty"""
        # Simplified algorithm - in real implementation, analyze SERP competition
        keyword_length = len(keyword.split())
        if keyword_length >= 4:
            return KeywordDifficulty.EASY
        elif keyword_length == 3:
            return KeywordDifficulty.MEDIUM
        elif keyword_length == 2:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    async def _estimate_cpc(self, keyword: str) -> float:
        """Estimate cost per click"""
        # Simplified estimation
        import random
        return round(random.uniform(0.10, 5.00), 2)
    
    async def _calculate_competition(self, keyword: str) -> float:
        """Calculate competition level (0-1)"""
        # Simplified calculation
        import random
        return round(random.uniform(0.1, 1.0), 2)
    
    async def _determine_search_intent(self, keyword: str) -> SearchIntent:
        """Determine search intent using AI analysis"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['buy', 'purchase', 'price', 'cost', 'cheap']):
            return SearchIntent.TRANSACTIONAL
        elif any(word in keyword_lower for word in ['review', 'comparison', 'vs', 'best']):
            return SearchIntent.COMMERCIAL
        elif any(word in keyword_lower for word in ['how', 'what', 'why', 'guide', 'tutorial']):
            return SearchIntent.INFORMATIONAL
        else:
            return SearchIntent.NAVIGATIONAL
    
    async def _calculate_trend_score(self, keyword: str) -> float:
        """Calculate trend score for keyword"""
        # Simplified trending calculation
        import random
        return round(random.uniform(0.0, 1.0), 2)
    
    async def _calculate_opportunity_score(
        self,
        search_volume: int,
        difficulty: KeywordDifficulty,
        competition: float,
        trend_score: float
    ) -> float:
        """Calculate keyword opportunity score"""
        # Normalize difficulty to numeric value
        difficulty_scores = {
            KeywordDifficulty.VERY_EASY: 0.9,
            KeywordDifficulty.EASY: 0.7,
            KeywordDifficulty.MEDIUM: 0.5,
            KeywordDifficulty.HARD: 0.3,
            KeywordDifficulty.VERY_HARD: 0.1
        }
        
        difficulty_score = difficulty_scores[difficulty]
        volume_score = min(search_volume / 10000, 1.0)  # Normalize volume
        competition_score = 1.0 - competition  # Lower competition is better
        
        opportunity = (
            volume_score * 0.4 +
            difficulty_score * 0.3 +
            competition_score * 0.2 +
            trend_score * 0.1
        )
        
        return round(opportunity, 3)
    
    async def _analyze_seasonal_patterns(self, keyword: str) -> Dict[str, float]:
        """Analyze seasonal search patterns"""
        # Simplified seasonal analysis
        import random
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return {month: round(random.uniform(0.5, 1.5), 2) for month in months}
    
    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords"""
        # This would integrate with keyword research APIs
        related = [
            f"{keyword} tips",
            f"{keyword} guide",
            f"{keyword} tutorial",
            f"best {keyword}",
            f"{keyword} review"
        ]
        return related[:5]
    
    async def _generate_keyword_questions(self, keyword: str) -> List[str]:
        """Generate questions related to keyword"""
        return [
            f"How to use {keyword}?",
            f"What is the best {keyword}?",
            f"Why choose {keyword}?",
            f"When to implement {keyword}?",
            f"Where to find {keyword}?"
        ]
    
    async def _categorize_primary_keywords(
        self,
        keyword_metrics: List[KeywordMetrics]
    ) -> List[KeywordMetrics]:
        """Categorize primary keywords"""
        # Sort by opportunity score and select top performers
        sorted_keywords = sorted(
            keyword_metrics,
            key=lambda k: k.opportunity_score,
            reverse=True
        )
        
        # Select keywords with high opportunity and reasonable difficulty
        primary = [
            k for k in sorted_keywords[:20]
            if k.opportunity_score > 0.6 and k.difficulty in [
                KeywordDifficulty.VERY_EASY,
                KeywordDifficulty.EASY,
                KeywordDifficulty.MEDIUM
            ]
        ]
        
        return primary[:10]
    
    async def _categorize_secondary_keywords(
        self,
        keyword_metrics: List[KeywordMetrics]
    ) -> List[KeywordMetrics]:
        """Categorize secondary keywords"""
        secondary = [
            k for k in keyword_metrics
            if 0.3 <= k.opportunity_score <= 0.6 and len(k.keyword.split()) <= 3
        ]
        
        return sorted(secondary, key=lambda k: k.opportunity_score, reverse=True)[:20]
    
    async def _categorize_long_tail_keywords(
        self,
        keyword_metrics: List[KeywordMetrics]
    ) -> List[KeywordMetrics]:
        """Categorize long-tail keywords"""
        long_tail = [
            k for k in keyword_metrics
            if len(k.keyword.split()) >= 4 and k.difficulty == KeywordDifficulty.VERY_EASY
        ]
        
        return sorted(long_tail, key=lambda k: k.search_volume, reverse=True)[:30]
    
    async def _analyze_competitors(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """Analyze competitor keywords"""
        # Simplified competitor analysis
        competitors = []
        for i, keyword in enumerate(seed_keywords[:5]):
            competitor = {
                'domain': f"competitor{i+1}.com",
                'authority_score': round(random.uniform(30, 90), 1),
                'ranking_keywords': random.randint(100, 5000),
                'top_keywords': [f"{keyword} {suffix}" for suffix in ['tips', 'guide', 'review']],
                'content_gaps': [f"{keyword} tutorial", f"advanced {keyword}"]
            }
            competitors.append(competitor)
        
        return competitors
    
    async def _identify_content_gaps(
        self,
        keyword_metrics: List[KeywordMetrics],
        competitors: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify content gaps in the market"""
        gaps = []
        
        # Find high-opportunity keywords with low competition
        for metric in keyword_metrics:
            if metric.opportunity_score > 0.7 and metric.competition < 0.3:
                gaps.append(f"Create content for '{metric.keyword}' - high opportunity, low competition")
        
        # Identify missing question-based content
        question_keywords = [k for k in keyword_metrics if k.keyword.startswith(('how', 'what', 'why'))]
        if len(question_keywords) < 5:
            gaps.append("Increase question-based content for better featured snippet opportunities")
        
        return gaps[:10]
    
    async def _generate_optimization_recommendations(
        self,
        keyword_metrics: List[KeywordMetrics],
        content_context: Optional[Dict[str, Any]] = None,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate SEO optimization recommendations"""
        recommendations = []
        
        # Primary keyword recommendations
        primary_keywords = [k for k in keyword_metrics if k.opportunity_score > 0.6]
        if primary_keywords:
            top_keyword = max(primary_keywords, key=lambda k: k.opportunity_score)
            recommendations.append(
                f"Focus on '{top_keyword.keyword}' as primary keyword "
                f"(opportunity score: {top_keyword.opportunity_score})"
            )
        
        # Long-tail keyword strategy
        long_tail = [k for k in keyword_metrics if len(k.keyword.split()) >= 4]
        if long_tail:
            recommendations.append(
                f"Target {len(long_tail)} long-tail keywords for easier ranking opportunities"
            )
        
        # Intent-based recommendations
        intents = {}
        for metric in keyword_metrics:
            if metric.intent not in intents:
                intents[metric.intent] = []
            intents[metric.intent].append(metric)
        
        if SearchIntent.TRANSACTIONAL in intents:
            recommendations.append(
                "Optimize for transactional keywords with clear call-to-actions"
            )
        
        if SearchIntent.INFORMATIONAL in intents:
            recommendations.append(
                "Create comprehensive guides for informational keywords"
            )
        
        # Seasonal optimization
        seasonal_keywords = [k for k in keyword_metrics if max(k.seasonal_patterns.values()) > 1.2]
        if seasonal_keywords:
            recommendations.append(
                "Plan seasonal content calendar for trending keywords"
            )
        
        return recommendations[:10]


# Export main class
__all__ = ['KeywordAnalyzer', 'KeywordMetrics', 'KeywordAnalysisResult', 'KeywordDifficulty', 'SearchIntent']