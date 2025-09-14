"""Keyword Research Workflow - Advanced AI-powered keyword discovery and strategy.

This module provides comprehensive keyword research capabilities including semantic analysis,
competition assessment, search volume tracking, and strategic keyword planning for
multi-platform content optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict


class KeywordDifficulty(Enum):
    """Keyword competition difficulty levels."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SearchIntent(Enum):
    """Search intent classification for keywords."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class KeywordType(Enum):
    """Keyword type classification."""
    HEAD_TERM = "head_term"
    BODY_TERM = "body_term"
    LONG_TAIL = "long_tail"
    BRANDED = "branded"
    SEMANTIC = "semantic"


@dataclass
class SearchVolume:
    """Search volume data for keywords."""
    monthly_volume: int
    yearly_volume: int
    trend_direction: str  # "increasing", "decreasing", "stable"
    seasonal_factor: float
    last_updated: datetime
    confidence_score: float = 0.85


@dataclass
class KeywordMetrics:
    """Comprehensive keyword metrics."""
    keyword: str
    search_volume: SearchVolume
    difficulty: KeywordDifficulty
    cpc: float  # Cost per click
    competition: float  # 0.0 to 1.0
    opportunity_score: float  # 0.0 to 100.0
    relevance_score: float  # 0.0 to 1.0
    search_intent: SearchIntent
    keyword_type: KeywordType
    related_keywords: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    platforms: Dict[str, float] = field(default_factory=dict)  # Platform-specific scores


@dataclass
class KeywordStrategy:
    """Strategic keyword planning and implementation."""
    primary_keywords: List[KeywordMetrics]
    secondary_keywords: List[KeywordMetrics]
    long_tail_keywords: List[KeywordMetrics]
    semantic_keywords: List[KeywordMetrics]
    content_gaps: List[str]
    competitor_keywords: List[str]
    seasonal_opportunities: List[Dict[str, Any]]
    implementation_priority: List[str]
    estimated_traffic: int
    competition_analysis: Dict[str, Any]


class KeywordResearchWorkflow:
    """Advanced keyword research workflow with AI-powered analysis."""
    
    def __init__(self) -> None:
        """Initialize the keyword research workflow."""
        self.keyword_databases = {
            "google": self._google_keyword_api,
            "youtube": self._youtube_keyword_api,
            "tiktok": self._tiktok_trending_api,
            "instagram": self._instagram_hashtag_api,
            "pinterest": self._pinterest_keyword_api
        }
        self.ai_models = {
            "semantic_expansion": self._semantic_expansion_model,
            "intent_classification": self._intent_classification_model,
            "difficulty_assessment": self._difficulty_assessment_model,
            "opportunity_scoring": self._opportunity_scoring_model
        }
    
    async def execute(self, content_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """Execute comprehensive keyword research workflow.
        
        Args:
            content_data: Content information for keyword research
            config: Workflow configuration
            
        Returns:
            Comprehensive keyword research results
        """
        try:
            # Extract research parameters
            topic = content_data.get("topic", "")
            content_type = content_data.get("content_type", "general")
            target_audience = content_data.get("target_audience", "general")
            target_platforms = content_data.get("target_platforms", ["google"])
            language = getattr(config, "language", "en")
            region = getattr(config, "region", "global")
            
            # Step 1: Seed keyword generation
            seed_keywords = await self._generate_seed_keywords(
                topic, content_type, target_audience
            )
            
            # Step 2: Keyword expansion
            expanded_keywords = await self._expand_keywords(
                seed_keywords, target_platforms, language
            )
            
            # Step 3: Keyword analysis
            analyzed_keywords = await self._analyze_keywords(
                expanded_keywords, target_platforms, region
            )
            
            # Step 4: Competition analysis
            competition_data = await self._analyze_competition(
                analyzed_keywords, topic, target_platforms
            )
            
            # Step 5: Strategic planning
            keyword_strategy = await self._create_keyword_strategy(
                analyzed_keywords, competition_data, content_type
            )
            
            # Step 6: Platform-specific optimization
            platform_strategies = await self._optimize_for_platforms(
                keyword_strategy, target_platforms
            )
            
            return {
                "status": "completed",
                "score": self._calculate_strategy_score(keyword_strategy),
                "strategy": keyword_strategy,
                "platform_strategies": platform_strategies,
                "recommendations": self._generate_recommendations(keyword_strategy),
                "metrics": {
                    "total_keywords": len(analyzed_keywords),
                    "high_opportunity": len([k for k in analyzed_keywords if k.opportunity_score > 70]),
                    "low_competition": len([k for k in analyzed_keywords if k.difficulty in [KeywordDifficulty.VERY_EASY, KeywordDifficulty.EASY]]),
                    "estimated_monthly_traffic": keyword_strategy.estimated_traffic
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "score": 0.0,
                "recommendations": [],
                "metrics": {}
            }
    
    async def _generate_seed_keywords(
        self, 
        topic: str, 
        content_type: str, 
        target_audience: str
    ) -> List[str]:
        """Generate initial seed keywords from topic analysis."""
        seed_keywords = []
        
        # Primary topic keywords
        topic_words = topic.lower().split()
        seed_keywords.extend(topic_words)
        seed_keywords.append(topic.lower())
        
        # Content type variations
        content_modifiers = {
            "video": ["tutorial", "guide", "how to", "review", "demo"],
            "blog": ["tips", "strategies", "best practices", "guide", "analysis"],
            "music": ["song", "beat", "instrumental", "remix", "cover"],
            "photo": ["photography", "image", "picture", "visual", "aesthetic"]
        }
        
        if content_type in content_modifiers:
            for modifier in content_modifiers[content_type]:
                seed_keywords.append(f"{modifier} {topic}")
                seed_keywords.append(f"{topic} {modifier}")
        
        # Audience-specific keywords
        audience_modifiers = {
            "beginner": ["beginner", "basics", "introduction", "getting started"],
            "advanced": ["advanced", "expert", "professional", "mastery"],
            "business": ["business", "enterprise", "commercial", "professional"],
            "personal": ["personal", "individual", "home", "DIY"]
        }
        
        if target_audience in audience_modifiers:
            for modifier in audience_modifiers[target_audience]:
                seed_keywords.append(f"{modifier} {topic}")
        
        # Remove duplicates and clean
        seed_keywords = list(set([kw.strip() for kw in seed_keywords if len(kw.strip()) > 2]))
        
        return seed_keywords[:50]  # Limit initial seeds
    
    async def _expand_keywords(
        self, 
        seed_keywords: List[str], 
        target_platforms: List[str], 
        language: str
    ) -> List[str]:
        """Expand seed keywords using various expansion techniques."""
        expanded = set(seed_keywords)
        
        # Semantic expansion
        for keyword in seed_keywords:
            semantic_variants = await self.ai_models["semantic_expansion"](keyword, language)
            expanded.update(semantic_variants)
        
        # Platform-specific expansion
        for platform in target_platforms:
            if platform in self.keyword_databases:
                platform_keywords = await self.keyword_databases[platform](seed_keywords)
                expanded.update(platform_keywords)
        
        # Question-based expansion
        question_words = ["how", "what", "why", "when", "where", "which", "who"]
        for keyword in seed_keywords:
            for qword in question_words:
                expanded.add(f"{qword} {keyword}")
                expanded.add(f"{qword} to {keyword}")
        
        # Modifier expansion
        modifiers = [
            "best", "top", "cheap", "free", "professional", "easy", "quick",
            "ultimate", "complete", "essential", "perfect", "amazing"
        ]
        for keyword in seed_keywords:
            for modifier in modifiers:
                expanded.add(f"{modifier} {keyword}")
        
        return list(expanded)
    
    async def _analyze_keywords(
        self, 
        keywords: List[str], 
        target_platforms: List[str], 
        region: str
    ) -> List[KeywordMetrics]:
        """Analyze keywords for metrics and classification."""
        analyzed_keywords = []
        
        for keyword in keywords:
            try:
                # Get search volume data
                search_volume = await self._get_search_volume(keyword, region)
                
                # Assess difficulty
                difficulty = await self.ai_models["difficulty_assessment"](keyword, target_platforms)
                
                # Classify intent
                search_intent = await self.ai_models["intent_classification"](keyword)
                
                # Determine keyword type
                keyword_type = self._classify_keyword_type(keyword)
                
                # Calculate opportunity score
                opportunity_score = await self.ai_models["opportunity_scoring"](
                    keyword, search_volume, difficulty, target_platforms
                )
                
                # Get platform-specific scores
                platform_scores = {}
                for platform in target_platforms:
                    platform_scores[platform] = await self._get_platform_score(keyword, platform)
                
                # Create keyword metrics
                keyword_metrics = KeywordMetrics(
                    keyword=keyword,
                    search_volume=search_volume,
                    difficulty=difficulty,
                    cpc=await self._estimate_cpc(keyword),
                    competition=await self._calculate_competition(keyword),
                    opportunity_score=opportunity_score,
                    relevance_score=await self._calculate_relevance(keyword, target_platforms),
                    search_intent=search_intent,
                    keyword_type=keyword_type,
                    platforms=platform_scores
                )
                
                analyzed_keywords.append(keyword_metrics)
                
            except Exception as e:
                # Log error but continue with other keywords
                continue
        
        # Sort by opportunity score
        analyzed_keywords.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return analyzed_keywords[:200]  # Limit to top 200 keywords
    
    async def _analyze_competition(
        self, 
        keywords: List[KeywordMetrics], 
        topic: str, 
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """Analyze competition for keywords and topic."""
        competition_data = {
            "competitor_keywords": [],
            "keyword_gaps": [],
            "competition_intensity": {},
            "market_opportunities": []
        }
        
        # Simulate competition analysis (in real implementation, would use actual APIs)
        for keyword_metric in keywords[:50]:  # Analyze top 50 keywords
            keyword = keyword_metric.keyword
            
            # Simulate competitor keyword discovery
            if keyword_metric.difficulty in [KeywordDifficulty.MEDIUM, KeywordDifficulty.HARD]:
                competition_data["competitor_keywords"].append(keyword)
            
            # Identify keyword gaps (low competition, good volume)
            if (keyword_metric.difficulty == KeywordDifficulty.EASY and 
                keyword_metric.search_volume.monthly_volume > 1000):
                competition_data["keyword_gaps"].append(keyword)
            
            # Calculate competition intensity per platform
            for platform in target_platforms:
                if platform not in competition_data["competition_intensity"]:
                    competition_data["competition_intensity"][platform] = 0.0
                competition_data["competition_intensity"][platform] += keyword_metric.competition
        
        # Normalize competition intensity
        for platform in competition_data["competition_intensity"]:
            competition_data["competition_intensity"][platform] /= len(keywords)
        
        return competition_data
    
    async def _create_keyword_strategy(
        self, 
        keywords: List[KeywordMetrics], 
        competition_data: Dict[str, Any], 
        content_type: str
    ) -> KeywordStrategy:
        """Create strategic keyword implementation plan."""
        
        # Categorize keywords by strategy
        primary_keywords = [k for k in keywords if k.opportunity_score > 80 and k.keyword_type == KeywordType.HEAD_TERM][:10]
        secondary_keywords = [k for k in keywords if 60 <= k.opportunity_score <= 80 and k.keyword_type == KeywordType.BODY_TERM][:20]
        long_tail_keywords = [k for k in keywords if k.keyword_type == KeywordType.LONG_TAIL][:30]
        semantic_keywords = [k for k in keywords if k.keyword_type == KeywordType.SEMANTIC][:20]
        
        # Calculate estimated traffic
        estimated_traffic = sum([
            int(k.search_volume.monthly_volume * 0.1)  # Assume 10% CTR
            for k in primary_keywords + secondary_keywords
        ])
        
        # Create implementation priority
        implementation_priority = []
        for keyword in primary_keywords:
            implementation_priority.append(f"Primary: {keyword.keyword}")
        for keyword in secondary_keywords[:10]:
            implementation_priority.append(f"Secondary: {keyword.keyword}")
        
        return KeywordStrategy(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            long_tail_keywords=long_tail_keywords,
            semantic_keywords=semantic_keywords,
            content_gaps=competition_data["keyword_gaps"],
            competitor_keywords=competition_data["competitor_keywords"],
            seasonal_opportunities=[],  # Would be populated with seasonal analysis
            implementation_priority=implementation_priority,
            estimated_traffic=estimated_traffic,
            competition_analysis=competition_data
        )
    
    async def _optimize_for_platforms(
        self, 
        strategy: KeywordStrategy, 
        target_platforms: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Optimize keyword strategy for specific platforms."""
        platform_strategies = {}
        
        for platform in target_platforms:
            platform_strategy = {
                "recommended_keywords": [],
                "platform_specific_terms": [],
                "optimization_tips": []
            }
            
            # Platform-specific keyword selection
            all_keywords = (strategy.primary_keywords + strategy.secondary_keywords + 
                           strategy.long_tail_keywords)
            
            for keyword in all_keywords:
                if platform in keyword.platforms and keyword.platforms[platform] > 0.7:
                    platform_strategy["recommended_keywords"].append({
                        "keyword": keyword.keyword,
                        "score": keyword.platforms[platform],
                        "volume": keyword.search_volume.monthly_volume,
                        "difficulty": keyword.difficulty.value
                    })
            
            # Platform-specific optimization tips
            platform_tips = {
                "youtube": [
                    "Include keywords in video title and description",
                    "Use keywords in video tags",
                    "Include keywords in thumbnail text when appropriate",
                    "Use long-tail keywords for better ranking"
                ],
                "google": [
                    "Target featured snippets with question keywords",
                    "Use keywords in title tags and meta descriptions",
                    "Include semantic keywords in content",
                    "Optimize for local search if applicable"
                ],
                "instagram": [
                    "Use keywords as hashtags",
                    "Include keywords in captions",
                    "Use keywords in alt text for accessibility",
                    "Include keywords in bio for discoverability"
                ]
            }
            
            platform_strategy["optimization_tips"] = platform_tips.get(platform, [])
            platform_strategies[platform] = platform_strategy
        
        return platform_strategies
    
    def _calculate_strategy_score(self, strategy: KeywordStrategy) -> float:
        """Calculate overall keyword strategy effectiveness score."""
        if not strategy.primary_keywords:
            return 0.0
        
        # Weighted scoring
        primary_score = sum([k.opportunity_score for k in strategy.primary_keywords]) / len(strategy.primary_keywords)
        secondary_score = sum([k.opportunity_score for k in strategy.secondary_keywords]) / max(len(strategy.secondary_keywords), 1)
        
        # Traffic potential score
        traffic_score = min(strategy.estimated_traffic / 10000 * 100, 100)  # Normalize to 100
        
        # Diversity score (variety of keyword types)
        diversity_score = min(len(set([k.keyword_type for k in strategy.primary_keywords + strategy.secondary_keywords])) * 25, 100)
        
        # Weighted final score
        final_score = (
            primary_score * 0.4 +
            secondary_score * 0.3 +
            traffic_score * 0.2 +
            diversity_score * 0.1
        )
        
        return round(final_score, 2)
    
    def _generate_recommendations(self, strategy: KeywordStrategy) -> List[Dict[str, Any]]:
        """Generate actionable keyword strategy recommendations."""
        recommendations = []
        
        # Primary keyword recommendations
        if strategy.primary_keywords:
            recommendations.append({
                "type": "primary_focus",
                "priority": "high",
                "action": f"Focus content optimization on top primary keyword: '{strategy.primary_keywords[0].keyword}'",
                "impact_score": 90,
                "effort": "medium"
            })
        
        # Long-tail opportunities
        high_opportunity_longtail = [k for k in strategy.long_tail_keywords if k.opportunity_score > 70]
        if high_opportunity_longtail:
            recommendations.append({
                "type": "long_tail_opportunity",
                "priority": "medium",
                "action": f"Target long-tail keyword opportunities: {', '.join([k.keyword for k in high_opportunity_longtail[:3]])}",
                "impact_score": 75,
                "effort": "low"
            })
        
        # Content gap opportunities
        if strategy.content_gaps:
            recommendations.append({
                "type": "content_gap",
                "priority": "high",
                "action": f"Create content for underserved keywords: {', '.join(strategy.content_gaps[:3])}",
                "impact_score": 85,
                "effort": "high"
            })
        
        # Competition insights
        if strategy.competitor_keywords:
            recommendations.append({
                "type": "competitive_analysis",
                "priority": "medium",
                "action": f"Analyze competitor strategies for: {', '.join(strategy.competitor_keywords[:3])}",
                "impact_score": 70,
                "effort": "medium"
            })
        
        return recommendations
    
    # Helper methods (simulated API calls - in real implementation would use actual APIs)
    
    async def _google_keyword_api(self, keywords: List[str]) -> List[str]:
        """Simulate Google Keyword Planner API."""
        expanded = []
        for keyword in keywords:
            # Simulate related keyword suggestions
            expanded.extend([
                f"{keyword} tips",
                f"{keyword} guide",
                f"best {keyword}",
                f"{keyword} tutorial",
                f"how to {keyword}"
            ])
        return expanded
    
    async def _youtube_keyword_api(self, keywords: List[str]) -> List[str]:
        """Simulate YouTube keyword suggestions."""
        expanded = []
        for keyword in keywords:
            expanded.extend([
                f"{keyword} video",
                f"{keyword} vlog",
                f"{keyword} review",
                f"{keyword} tutorial",
                f"{keyword} behind the scenes"
            ])
        return expanded
    
    async def _tiktok_trending_api(self, keywords: List[str]) -> List[str]:
        """Simulate TikTok trending hashtag API."""
        expanded = []
        for keyword in keywords:
            expanded.extend([
                f"{keyword}challenge",
                f"{keyword}trend",
                f"{keyword}fyp",
                f"{keyword}viral",
                f"{keyword}hack"
            ])
        return expanded
    
    async def _instagram_hashtag_api(self, keywords: List[str]) -> List[str]:
        """Simulate Instagram hashtag suggestions."""
        expanded = []
        for keyword in keywords:
            expanded.extend([
                f"{keyword}gram",
                f"{keyword}life",
                f"{keyword}love",
                f"{keyword}daily",
                f"{keyword}inspiration"
            ])
        return expanded
    
    async def _pinterest_keyword_api(self, keywords: List[str]) -> List[str]:
        """Simulate Pinterest keyword suggestions."""
        expanded = []
        for keyword in keywords:
            expanded.extend([
                f"{keyword} ideas",
                f"{keyword} inspiration",
                f"DIY {keyword}",
                f"{keyword} aesthetic",
                f"{keyword} board"
            ])
        return expanded
    
    async def _semantic_expansion_model(self, keyword: str, language: str) -> List[str]:
        """Simulate AI semantic expansion."""
        # Simple semantic expansion simulation
        synonyms = {
            "content": ["material", "information", "media", "posts"],
            "marketing": ["promotion", "advertising", "branding", "outreach"],
            "video": ["footage", "clip", "recording", "film"],
            "music": ["audio", "sound", "track", "song"]
        }
        
        expanded = []
        for word in keyword.split():
            if word.lower() in synonyms:
                for synonym in synonyms[word.lower()]:
                    expanded.append(keyword.replace(word, synonym))
        
        return expanded[:10]
    
    async def _intent_classification_model(self, keyword: str) -> SearchIntent:
        """Simulate AI intent classification."""
        # Simple intent classification
        if any(word in keyword.lower() for word in ["how", "tutorial", "guide", "learn"]):
            return SearchIntent.INFORMATIONAL
        elif any(word in keyword.lower() for word in ["buy", "purchase", "price", "cost"]):
            return SearchIntent.TRANSACTIONAL
        elif any(word in keyword.lower() for word in ["review", "compare", "vs", "best"]):
            return SearchIntent.COMMERCIAL
        else:
            return SearchIntent.NAVIGATIONAL
    
    async def _difficulty_assessment_model(self, keyword: str, platforms: List[str]) -> KeywordDifficulty:
        """Simulate AI difficulty assessment."""
        # Simple difficulty assessment based on keyword characteristics
        word_count = len(keyword.split())
        
        if word_count >= 4:
            return KeywordDifficulty.EASY
        elif word_count == 3:
            return KeywordDifficulty.MEDIUM
        elif word_count == 2:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    async def _opportunity_scoring_model(
        self, 
        keyword: str, 
        search_volume: SearchVolume, 
        difficulty: KeywordDifficulty, 
        platforms: List[str]
    ) -> float:
        """Simulate AI opportunity scoring."""
        # Simple opportunity scoring
        volume_score = min(search_volume.monthly_volume / 10000 * 50, 50)  # Max 50 points
        
        difficulty_scores = {
            KeywordDifficulty.VERY_EASY: 40,
            KeywordDifficulty.EASY: 30,
            KeywordDifficulty.MEDIUM: 20,
            KeywordDifficulty.HARD: 10,
            KeywordDifficulty.VERY_HARD: 5
        }
        
        difficulty_score = difficulty_scores[difficulty]
        platform_bonus = len(platforms) * 2  # Bonus for multi-platform
        
        return min(volume_score + difficulty_score + platform_bonus, 100)
    
    async def _get_search_volume(self, keyword: str, region: str) -> SearchVolume:
        """Simulate search volume data retrieval."""
        # Simple volume simulation based on keyword characteristics
        base_volume = len(keyword.split()) * 1000
        
        return SearchVolume(
            monthly_volume=base_volume,
            yearly_volume=base_volume * 12,
            trend_direction="stable",
            seasonal_factor=1.0,
            last_updated=datetime.now(),
            confidence_score=0.85
        )
    
    def _classify_keyword_type(self, keyword: str) -> KeywordType:
        """Classify keyword type based on characteristics."""
        word_count = len(keyword.split())
        
        if word_count == 1:
            return KeywordType.HEAD_TERM
        elif word_count == 2:
            return KeywordType.BODY_TERM
        elif word_count >= 3:
            return KeywordType.LONG_TAIL
        else:
            return KeywordType.SEMANTIC
    
    async def _estimate_cpc(self, keyword: str) -> float:
        """Simulate CPC estimation."""
        # Simple CPC simulation
        return round(len(keyword) * 0.1, 2)
    
    async def _calculate_competition(self, keyword: str) -> float:
        """Simulate competition calculation."""
        # Simple competition simulation
        return min(len(keyword.split()) * 0.2, 1.0)
    
    async def _calculate_relevance(self, keyword: str, platforms: List[str]) -> float:
        """Simulate relevance calculation."""
        # Simple relevance simulation
        return 0.8  # Default good relevance
    
    async def _get_platform_score(self, keyword: str, platform: str) -> float:
        """Simulate platform-specific scoring."""
        # Simple platform scoring
        platform_modifiers = {
            "youtube": 0.9 if "video" in keyword else 0.7,
            "google": 0.8,
            "instagram": 0.9 if any(word in keyword for word in ["photo", "image", "visual"]) else 0.6,
            "tiktok": 0.9 if any(word in keyword for word in ["dance", "challenge", "viral"]) else 0.5
        }
        
        return platform_modifiers.get(platform, 0.7)