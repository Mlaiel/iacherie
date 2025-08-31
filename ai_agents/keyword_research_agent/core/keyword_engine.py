"""
Keyword Research Engine - Core processing engine for automated keyword discovery

Advanced keyword research capabilities with AI-powered analysis and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import re
import json

logger = logging.getLogger(__name__)

@dataclass
class KeywordJob:
    """Keyword research job configuration"""
    job_id: str
    job_type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class KeywordResult:
    """Keyword research result"""
    keyword: str
    search_volume: int
    difficulty_score: float
    competition_level: str
    cost_per_click: Optional[float] = None
    intent_type: str = "informational"
    related_keywords: List[str] = None
    
    def __post_init__(self):
        if self.related_keywords is None:
            self.related_keywords = []

class KeywordEngine:
    """Core keyword research processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_running = False
        
        # Keyword databases and caches
        self.keyword_cache = {}
        self.trend_data = {}
        self.competition_data = {}
        
        # Processing queues
        self.pending_jobs = asyncio.Queue()
        self.active_jobs = {}
        
        logger.info("KeywordEngine initialized")

    async def start(self):
        """Start the keyword research engine"""
        if not self.is_running:
            self.is_running = True
            # Start background tasks
            asyncio.create_task(self._process_jobs())
            logger.info("KeywordEngine started")

    async def stop(self):
        """Stop the keyword research engine"""
        if self.is_running:
            self.is_running = False
            logger.info("KeywordEngine stopped")

    async def discover_primary_keywords(self, topic: str, platform: str, language: str) -> List[str]:
        """Discover primary keywords for a topic"""
        # AI-powered keyword discovery
        primary_keywords = []
        
        # Extract core concepts from topic
        core_concepts = self._extract_core_concepts(topic)
        
        # Generate keyword variations
        for concept in core_concepts:
            variations = await self._generate_keyword_variations(concept, platform, language)
            primary_keywords.extend(variations[:5])  # Top 5 variations per concept
        
        # Remove duplicates and sort by relevance
        primary_keywords = list(set(primary_keywords))
        primary_keywords = await self._rank_keywords_by_relevance(primary_keywords, topic)
        
        return primary_keywords[:20]  # Return top 20 primary keywords

    async def discover_secondary_keywords(self, topic: str, primary_keywords: List[str]) -> List[str]:
        """Discover secondary keywords based on primary keywords"""
        secondary_keywords = []
        
        for primary_keyword in primary_keywords:
            # Generate semantic variations
            semantic_variations = await self._generate_semantic_variations(primary_keyword)
            secondary_keywords.extend(semantic_variations[:3])  # Top 3 per primary
            
            # Generate modifier combinations
            modifiers = ["best", "top", "how to", "guide", "tips", "tutorial", "review"]
            for modifier in modifiers:
                modified_keyword = f"{modifier} {primary_keyword}"
                secondary_keywords.append(modified_keyword)
        
        # Filter and rank secondary keywords
        secondary_keywords = list(set(secondary_keywords))
        secondary_keywords = await self._filter_relevant_keywords(secondary_keywords, topic)
        
        return secondary_keywords[:50]  # Return top 50 secondary keywords

    async def discover_long_tail_keywords(self, topic: str, depth: str) -> List[str]:
        """Discover long-tail keyword opportunities"""
        long_tail_keywords = []
        
        # Question-based long-tail keywords
        question_starters = ["how to", "what is", "why does", "where can", "when should", "who is"]
        for starter in question_starters:
            question_keyword = f"{starter} {topic}"
            long_tail_keywords.append(question_keyword)
        
        # Problem-solution long-tail keywords
        problem_patterns = [
            f"{topic} problem",
            f"{topic} solution",
            f"{topic} not working",
            f"how to fix {topic}",
            f"{topic} troubleshooting"
        ]
        long_tail_keywords.extend(problem_patterns)
        
        # Comparison long-tail keywords
        comparison_patterns = [
            f"{topic} vs",
            f"{topic} comparison",
            f"best {topic}",
            f"{topic} alternative"
        ]
        long_tail_keywords.extend(comparison_patterns)
        
        # Depth-based expansion
        if depth == "deep":
            # Add more specific and niche variations
            specific_patterns = await self._generate_specific_patterns(topic)
            long_tail_keywords.extend(specific_patterns)
        
        return long_tail_keywords[:100]  # Return top 100 long-tail keywords

    async def analyze_keyword_metrics(self, keywords: List[str]) -> Dict[str, KeywordResult]:
        """Analyze metrics for list of keywords"""
        keyword_metrics = {}
        
        for keyword in keywords:
            # Simulate keyword analysis (would integrate with real APIs)
            search_volume = await self._estimate_search_volume(keyword)
            difficulty = await self._calculate_difficulty_score(keyword)
            competition = await self._analyze_competition_level(keyword)
            intent = await self._classify_search_intent(keyword)
            
            keyword_metrics[keyword] = KeywordResult(
                keyword=keyword,
                search_volume=search_volume,
                difficulty_score=difficulty,
                competition_level=competition,
                intent_type=intent,
                related_keywords=await self._find_related_keywords(keyword)
            )
        
        return keyword_metrics

    async def analyze_keyword_competition(self, keyword: str, platform: str) -> Dict[str, Any]:
        """Analyze competition for a specific keyword"""
        return {
            "keyword": keyword,
            "platform": platform,
            "competition_level": await self._analyze_competition_level(keyword),
            "top_competitors": await self._identify_top_competitors(keyword, platform),
            "content_gaps": await self._identify_content_gaps(keyword),
            "ranking_difficulty": await self._calculate_ranking_difficulty(keyword),
            "opportunity_score": await self._calculate_opportunity_score(keyword)
        }

    async def discover_trending_keywords(self, niche: str, timeframe: str, region: str) -> List[Dict[str, Any]]:
        """Discover trending keywords in a niche"""
        trending_keywords = []
        
        # Simulate trend analysis (would integrate with Google Trends, etc.)
        base_trends = [
            f"{niche} 2024",
            f"latest {niche}",
            f"{niche} trends",
            f"new {niche}",
            f"{niche} update"
        ]
        
        for trend in base_trends:
            trend_data = {
                "keyword": trend,
                "trend_score": await self._calculate_trend_score(trend, timeframe),
                "search_volume": await self._estimate_search_volume(trend),
                "growth_rate": await self._calculate_growth_rate(trend, timeframe),
                "region": region
            }
            trending_keywords.append(trend_data)
        
        # Sort by trend score
        trending_keywords.sort(key=lambda x: x["trend_score"], reverse=True)
        
        return trending_keywords[:25]  # Return top 25 trending keywords

    def _extract_core_concepts(self, topic: str) -> List[str]:
        """Extract core concepts from a topic"""
        # Simple concept extraction (would use NLP in production)
        words = re.findall(r'\b\w+\b', topic.lower())
        # Filter out common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an"}
        concepts = [word for word in words if word not in stop_words and len(word) > 2]
        return concepts[:5]  # Return top 5 concepts

    async def _generate_keyword_variations(self, concept: str, platform: str, language: str) -> List[str]:
        """Generate keyword variations for a concept"""
        variations = [
            concept,
            f"{concept}s",
            f"{concept} guide",
            f"{concept} tips",
            f"best {concept}",
            f"{concept} tutorial",
            f"how to {concept}",
            f"{concept} review"
        ]
        
        # Platform-specific variations
        if platform == "youtube":
            variations.extend([f"{concept} video", f"{concept} channel"])
        elif platform == "instagram":
            variations.extend([f"{concept} photos", f"{concept} hashtags"])
        elif platform == "tiktok":
            variations.extend([f"{concept} viral", f"{concept} trend"])
        
        return variations

    async def _rank_keywords_by_relevance(self, keywords: List[str], topic: str) -> List[str]:
        """Rank keywords by relevance to topic"""
        # Simple relevance scoring (would use ML models in production)
        topic_words = set(topic.lower().split())
        
        def relevance_score(keyword):
            keyword_words = set(keyword.lower().split())
            overlap = len(topic_words.intersection(keyword_words))
            return overlap / len(keyword_words) if keyword_words else 0
        
        return sorted(keywords, key=relevance_score, reverse=True)

    async def _generate_semantic_variations(self, keyword: str) -> List[str]:
        """Generate semantic variations of a keyword"""
        # Simplified semantic variation (would use word embeddings in production)
        variations = [
            keyword.replace(" ", "_"),
            keyword.replace(" ", "-"),
            f"{keyword} alternative",
            f"{keyword} similar",
            f"{keyword} related"
        ]
        return variations

    async def _filter_relevant_keywords(self, keywords: List[str], topic: str) -> List[str]:
        """Filter keywords for relevance"""
        # Simple relevance filter
        topic_words = set(topic.lower().split())
        relevant_keywords = []
        
        for keyword in keywords:
            keyword_words = set(keyword.lower().split())
            if topic_words.intersection(keyword_words):
                relevant_keywords.append(keyword)
        
        return relevant_keywords

    async def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword"""
        # Simplified estimation (would use real APIs in production)
        base_volume = len(keyword.split()) * 1000
        return max(100, base_volume + hash(keyword) % 10000)

    async def _calculate_difficulty_score(self, keyword: str) -> float:
        """Calculate SEO difficulty score"""
        # Simplified calculation (would use real competition data)
        length_factor = min(len(keyword) / 50, 1.0)
        word_count_factor = min(len(keyword.split()) / 5, 1.0)
        return round((length_factor + word_count_factor) / 2, 2)

    async def _analyze_competition_level(self, keyword: str) -> str:
        """Analyze competition level"""
        difficulty = await self._calculate_difficulty_score(keyword)
        if difficulty < 0.3:
            return "low"
        elif difficulty < 0.6:
            return "medium"
        else:
            return "high"

    async def _classify_search_intent(self, keyword: str) -> str:
        """Classify search intent for keyword"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ["how to", "tutorial", "guide", "learn"]):
            return "informational"
        elif any(word in keyword_lower for word in ["buy", "purchase", "price", "cost", "cheap"]):
            return "transactional"
        elif any(word in keyword_lower for word in ["best", "top", "review", "comparison"]):
            return "commercial"
        else:
            return "navigational"

    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords"""
        # Simplified related keyword generation
        words = keyword.split()
        related = []
        
        for word in words:
            related.extend([
                f"{word} alternatives",
                f"{word} similar",
                f"{word} related"
            ])
        
        return related[:5]

    async def _process_jobs(self):
        """Background job processing"""
        while self.is_running:
            try:
                if not self.pending_jobs.empty():
                    job = await self.pending_jobs.get()
                    await self._execute_job(job)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")

    async def _execute_job(self, job: KeywordJob):
        """Execute a keyword research job"""
        try:
            job.status = "running"
            self.active_jobs[job.job_id] = job
            
            # Job execution logic here
            await asyncio.sleep(1)  # Simulate processing
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = "failed"
            logger.error(f"Job {job.job_id} failed: {e}")
        finally:
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]

    async def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "active_jobs": len(self.active_jobs),
            "total_keywords": len(self.keyword_cache),
            "metrics": {
                "cache_size": len(self.keyword_cache),
                "trend_data_size": len(self.trend_data),
                "competition_data_size": len(self.competition_data)
            }
        }

    # Additional helper methods for comprehensive keyword research
    async def _generate_specific_patterns(self, topic: str) -> List[str]:
        """Generate specific long-tail patterns"""
        patterns = [
            f"{topic} for beginners",
            f"advanced {topic}",
            f"{topic} step by step",
            f"{topic} mistakes to avoid",
            f"{topic} case study",
            f"{topic} expert tips"
        ]
        return patterns

    async def _calculate_trend_score(self, keyword: str, timeframe: str) -> float:
        """Calculate trend score for keyword"""
        # Simplified trend scoring
        base_score = hash(keyword) % 100 / 100
        timeframe_multiplier = {"7d": 0.5, "30d": 1.0, "90d": 1.5, "1y": 2.0}.get(timeframe, 1.0)
        return round(base_score * timeframe_multiplier, 2)

    async def _calculate_growth_rate(self, keyword: str, timeframe: str) -> float:
        """Calculate growth rate for keyword"""
        # Simplified growth rate calculation
        base_rate = (hash(keyword) % 50) / 100  # 0-0.5 growth rate
        return round(base_rate, 3)

    async def _identify_top_competitors(self, keyword: str, platform: str) -> List[str]:
        """Identify top competitors for keyword"""
        # Simulate competitor identification
        return [f"competitor_{i}_{platform}" for i in range(1, 6)]

    async def _identify_content_gaps(self, keyword: str) -> List[str]:
        """Identify content gaps for keyword"""
        # Simulate content gap analysis
        return [
            f"{keyword} beginner guide missing",
            f"{keyword} advanced tutorial gap",
            f"{keyword} case studies needed"
        ]

    async def _calculate_ranking_difficulty(self, keyword: str) -> str:
        """Calculate ranking difficulty"""
        difficulty_score = await self._calculate_difficulty_score(keyword)
        if difficulty_score < 0.3:
            return "easy"
        elif difficulty_score < 0.7:
            return "moderate"
        else:
            return "difficult"

    async def _calculate_opportunity_score(self, keyword: str) -> float:
        """Calculate opportunity score for keyword"""
        search_volume = await self._estimate_search_volume(keyword)
        difficulty = await self._calculate_difficulty_score(keyword)
        
        # Higher volume, lower difficulty = higher opportunity
        opportunity = (search_volume / 1000) * (1 - difficulty)
        return round(min(opportunity, 10.0), 2)  # Cap at 10.0

    async def generate_competition_summary(self, competition_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of competition analysis"""
        total_keywords = len(competition_analysis)
        high_competition = sum(1 for analysis in competition_analysis.values() 
                             if analysis.get('competition_level') == 'high')
        
        return {
            "total_keywords_analyzed": total_keywords,
            "high_competition_count": high_competition,
            "average_opportunity_score": round(
                sum(analysis.get('opportunity_score', 0) for analysis in competition_analysis.values()) / total_keywords, 2
            ) if total_keywords > 0 else 0,
            "recommendations": [
                "Focus on medium and low competition keywords",
                "Consider long-tail variations for high competition keywords"
            ]
        }

    async def identify_opportunities(self, competition_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify keyword opportunities from competition analysis"""
        opportunities = []
        
        for keyword, analysis in competition_analysis.items():
            if analysis.get('opportunity_score', 0) > 5.0:
                opportunities.append({
                    "keyword": keyword,
                    "opportunity_score": analysis.get('opportunity_score'),
                    "reason": "High opportunity, low competition",
                    "recommended_action": "Target immediately"
                })
        
        return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:10]

    async def analyze_seasonal_patterns(self, niche: str, timeframe: str) -> Dict[str, Any]:
        """Analyze seasonal patterns for a niche"""
        # Simplified seasonal analysis
        seasons = ["spring", "summer", "fall", "winter"]
        patterns = {}
        
        for season in seasons:
            # Simulate seasonal trend data
            trend_strength = (hash(f"{niche}_{season}") % 100) / 100
            patterns[season] = {
                "trend_strength": round(trend_strength, 2),
                "peak_months": self._get_season_months(season),
                "recommended_keywords": [f"{niche} {season}", f"{season} {niche}"]
            }
        
        return patterns

    def _get_season_months(self, season: str) -> List[str]:
        """Get months for each season"""
        season_months = {
            "spring": ["March", "April", "May"],
            "summer": ["June", "July", "August"], 
            "fall": ["September", "October", "November"],
            "winter": ["December", "January", "February"]
        }
        return season_months.get(season, [])

    async def identify_emerging_topics(self, niche: str) -> List[Dict[str, Any]]:
        """Identify emerging topics in a niche"""
        # Simulate emerging topic identification
        emerging_topics = [
            {
                "topic": f"AI-powered {niche}",
                "growth_rate": 0.45,
                "search_volume": 12000,
                "trend_score": 0.8
            },
            {
                "topic": f"sustainable {niche}",
                "growth_rate": 0.32,
                "search_volume": 8500,
                "trend_score": 0.7
            },
            {
                "topic": f"remote {niche}",
                "growth_rate": 0.28,
                "search_volume": 15000,
                "trend_score": 0.6
            }
        ]
        
        return emerging_topics

    async def calculate_trend_strength(self, trending_keywords: List[Dict[str, Any]]) -> float:
        """Calculate overall trend strength"""
        if not trending_keywords:
            return 0.0
        
        total_score = sum(kw.get('trend_score', 0) for kw in trending_keywords)
        return round(total_score / len(trending_keywords), 2)

    async def generate_long_tail_variations(self, seed_keyword: str, intent_type: str) -> List[str]:
        """Generate long-tail variations based on intent type"""
        variations = []
        
        if intent_type in ['all', 'informational']:
            variations.extend([
                f"what is {seed_keyword}",
                f"how to use {seed_keyword}",
                f"{seed_keyword} explained",
                f"{seed_keyword} guide for beginners"
            ])
        
        if intent_type in ['all', 'transactional']:
            variations.extend([
                f"buy {seed_keyword}",
                f"best {seed_keyword} deals",
                f"{seed_keyword} discount",
                f"cheap {seed_keyword}"
            ])
        
        if intent_type in ['all', 'navigational']:
            variations.extend([
                f"{seed_keyword} website",
                f"{seed_keyword} official site",
                f"{seed_keyword} login",
                f"{seed_keyword} app"
            ])
        
        return variations[:20]  # Return top 20 variations

    async def discover_question_keywords(self, seed_keyword: str) -> List[str]:
        """Discover question-based keywords"""
        question_starters = [
            "how to", "what is", "why does", "when should", "where can", "who is",
            "how much", "how many", "which", "can you", "should I", "will"
        ]
        
        question_keywords = []
        for starter in question_starters:
            question_keywords.append(f"{starter} {seed_keyword}")
        
        return question_keywords

    async def generate_local_variations(self, seed_keyword: str) -> List[str]:
        """Generate local keyword variations"""
        location_modifiers = [
            "near me", "in my area", "local", "nearby", "city",
            "online", "store", "service", "company", "business"
        ]
        
        local_variations = []
        for modifier in location_modifiers:
            local_variations.extend([
                f"{seed_keyword} {modifier}",
                f"{modifier} {seed_keyword}"
            ])
        
        return local_variations[:15]  # Return top 15 variations

    async def calculate_difficulty_scores(self, keywords: List[str]) -> Dict[str, float]:
        """Calculate difficulty scores for multiple keywords"""
        difficulty_scores = {}
        
        for keyword in keywords:
            difficulty_scores[keyword] = await self._calculate_difficulty_score(keyword)
        
        return difficulty_scores

    async def bulk_analyze_keywords(self, keywords: List[str], analysis_type: str, platform: str) -> Dict[str, Any]:
        """Bulk analyze keywords"""
        results = {}
        
        for keyword in keywords:
            if analysis_type == "comprehensive":
                results[keyword] = {
                    "search_volume": await self._estimate_search_volume(keyword),
                    "difficulty_score": await self._calculate_difficulty_score(keyword),
                    "competition_level": await self._analyze_competition_level(keyword),
                    "intent_type": await self._classify_search_intent(keyword),
                    "opportunity_score": await self._calculate_opportunity_score(keyword)
                }
            else:  # basic analysis
                results[keyword] = {
                    "search_volume": await self._estimate_search_volume(keyword),
                    "difficulty_score": await self._calculate_difficulty_score(keyword)
                }
        
        return results

    async def generate_bulk_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for bulk analysis results"""
        total_keywords = len(results)
        
        if total_keywords == 0:
            return {"total_keywords": 0, "summary": "No keywords analyzed"}
        
        total_volume = sum(r.get('search_volume', 0) for r in results.values())
        avg_difficulty = sum(r.get('difficulty_score', 0) for r in results.values()) / total_keywords
        high_opportunity = sum(1 for r in results.values() if r.get('opportunity_score', 0) > 5.0)
        
        return {
            "total_keywords": total_keywords,
            "total_search_volume": total_volume,
            "average_difficulty": round(avg_difficulty, 2),
            "high_opportunity_keywords": high_opportunity,
            "volume_distribution": self._calculate_volume_distribution(results)
        }

    def _calculate_volume_distribution(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate search volume distribution"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for result in results.values():
            volume = result.get('search_volume', 0)
            if volume < 1000:
                distribution["low"] += 1
            elif volume < 10000:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution

    async def identify_top_opportunities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top keyword opportunities from bulk results"""
        opportunities = []
        
        for keyword, data in results.items():
            opportunity_score = data.get('opportunity_score', 0)
            if opportunity_score > 3.0:  # Threshold for opportunities
                opportunities.append({
                    "keyword": keyword,
                    "opportunity_score": opportunity_score,
                    "search_volume": data.get('search_volume', 0),
                    "difficulty": data.get('difficulty_score', 0),
                    "competition": data.get('competition_level', 'unknown')
                })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return opportunities[:10]  # Return top 10 opportunities