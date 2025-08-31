"""SEO optimization business service for IA Influencer Agent platform.

This service handles comprehensive SEO optimization for multi-format content,
including metadata optimization, keyword analysis, and search engine visibility.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

WARNING: This code is proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution is strictly
prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textstat import flesch_reading_ease, flesch_kincaid_grade
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup

from ..core.database import get_db
from ..models.content import Content
from ..models.seo import (
    SEOAnalysis, KeywordRanking, ContentOptimization,
    SearchPerformance, SEORecommendation
)
from ..utils.text_analyzer import TextAnalyzer
from ..utils.keyword_extractor import KeywordExtractor
from ..integrations.search_engines import SearchEngineAPI
from ..integrations.social_platforms import SocialPlatformOptimizer

logger = logging.getLogger(__name__)

class SEOMetricType(Enum):
    """SEO metric types for analysis."""
    KEYWORD_DENSITY = "keyword_density"
    READABILITY = "readability"
    META_OPTIMIZATION = "meta_optimization"
    CONTENT_LENGTH = "content_length"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    TECHNICAL_SEO = "technical_seo"
    SOCIAL_SIGNALS = "social_signals"

class ContentOptimizationType(Enum):
    """Types of content optimization."""
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_OPTIMIZATION = "description_optimization"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    META_TAG_OPTIMIZATION = "meta_tag_optimization"
    STRUCTURE_OPTIMIZATION = "structure_optimization"

@dataclass
class SEOScore:
    """SEO score data structure."""
    overall_score: float
    title_score: float
    description_score: float
    keyword_score: float
    readability_score: float
    technical_score: float
    social_score: float
    recommendations: List[str]

@dataclass
class KeywordAnalysis:
    """Keyword analysis result."""
    keyword: str
    search_volume: int
    competition_level: str
    difficulty_score: float
    relevance_score: float
    current_ranking: Optional[int]
    optimization_potential: float

@dataclass
class ContentSEOOptimization:
    """Content SEO optimization suggestions."""
    content_id: str
    current_score: float
    optimized_title: str
    optimized_description: str
    recommended_keywords: List[str]
    recommended_hashtags: List[str]
    content_improvements: List[str]
    meta_improvements: Dict[str, str]

class SEOService:
    """
    Comprehensive SEO optimization service for multi-format content creators.
    
    Provides intelligent SEO analysis, keyword optimization, metadata enhancement,
    and search engine visibility improvements for all content types.
    """
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.keyword_extractor = KeywordExtractor()
        self.search_engine_api = SearchEngineAPI()
        self.social_optimizer = SocialPlatformOptimizer()
        
        # Initialize NLTK components
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    async def analyze_content_seo(
        self,
        content_id: str,
        target_keywords: Optional[List[str]] = None,
        competitor_analysis: bool = False,
        db: Session = None
    ) -> SEOScore:
        """
        Perform comprehensive SEO analysis for content.
        
        Args:
            content_id: Content identifier
            target_keywords: Target keywords for optimization
            competitor_analysis: Include competitor analysis
            db: Database session
            
        Returns:
            Comprehensive SEO score and recommendations
        """
        if db is None:
            db = next(get_db())
        
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            # Analyze different SEO aspects
            title_analysis = await self._analyze_title_seo(content)
            description_analysis = await self._analyze_description_seo(content)
            keyword_analysis = await self._analyze_keyword_optimization(content, target_keywords)
            readability_analysis = await self._analyze_content_readability(content)
            technical_analysis = await self._analyze_technical_seo(content)
            social_analysis = await self._analyze_social_seo(content)
            
            # Calculate overall score
            overall_score = self._calculate_overall_seo_score([
                title_analysis["score"],
                description_analysis["score"],
                keyword_analysis["score"],
                readability_analysis["score"],
                technical_analysis["score"],
                social_analysis["score"]
            ])
            
            # Generate recommendations
            recommendations = []
            recommendations.extend(title_analysis["recommendations"])
            recommendations.extend(description_analysis["recommendations"])
            recommendations.extend(keyword_analysis["recommendations"])
            recommendations.extend(readability_analysis["recommendations"])
            recommendations.extend(technical_analysis["recommendations"])
            recommendations.extend(social_analysis["recommendations"])
            
            seo_score = SEOScore(
                overall_score=overall_score,
                title_score=title_analysis["score"],
                description_score=description_analysis["score"],
                keyword_score=keyword_analysis["score"],
                readability_score=readability_analysis["score"],
                technical_score=technical_analysis["score"],
                social_score=social_analysis["score"],
                recommendations=recommendations
            )
            
            # Store analysis results
            await self._store_seo_analysis(content_id, seo_score, db)
            
            return seo_score
            
        except Exception as e:
            logger.error(f"Error analyzing content SEO: {str(e)}")
            raise
    
    async def optimize_content_metadata(
        self,
        content_id: str,
        target_platforms: List[str],
        optimization_goals: List[str] = None,
        db: Session = None
    ) -> ContentSEOOptimization:
        """
        Optimize content metadata for multiple platforms.
        
        Args:
            content_id: Content identifier
            target_platforms: Platforms to optimize for
            optimization_goals: Specific optimization objectives
            db: Database session
            
        Returns:
            Optimized content metadata and suggestions
        """
        if db is None:
            db = next(get_db())
        
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            # Analyze current SEO performance
            current_score = await self._calculate_current_seo_score(content)
            
            # Generate optimized metadata
            optimized_title = await self._optimize_content_title(
                content, target_platforms
            )
            optimized_description = await self._optimize_content_description(
                content, target_platforms
            )
            
            # Recommend keywords and hashtags
            recommended_keywords = await self._recommend_keywords(
                content, target_platforms
            )
            recommended_hashtags = await self._recommend_hashtags(
                content, target_platforms
            )
            
            # Generate content improvements
            content_improvements = await self._generate_content_improvements(
                content, optimization_goals
            )
            
            # Generate meta tag improvements
            meta_improvements = await self._generate_meta_improvements(
                content, target_platforms
            )
            
            optimization = ContentSEOOptimization(
                content_id=content_id,
                current_score=current_score,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                recommended_keywords=recommended_keywords,
                recommended_hashtags=recommended_hashtags,
                content_improvements=content_improvements,
                meta_improvements=meta_improvements
            )
            
            # Store optimization suggestions
            await self._store_optimization_suggestions(optimization, db)
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing content metadata: {str(e)}")
            raise
    
    async def perform_keyword_research(
        self,
        seed_keywords: List[str],
        content_type: str,
        target_audience: str,
        competition_level: str = "medium",
        db: Session = None
    ) -> List[KeywordAnalysis]:
        """
        Perform comprehensive keyword research and analysis.
        
        Args:
            seed_keywords: Initial keywords for research
            content_type: Type of content for optimization
            target_audience: Target audience characteristics
            competition_level: Desired competition level
            db: Database session
            
        Returns:
            List of keyword analysis results
        """
        try:
            keyword_suggestions = []
            
            for seed_keyword in seed_keywords:
                # Get keyword variations and related terms
                variations = await self._get_keyword_variations(seed_keyword)
                related_keywords = await self._get_related_keywords(seed_keyword)
                long_tail_keywords = await self._generate_long_tail_keywords(seed_keyword)
                
                all_keywords = list(set(variations + related_keywords + long_tail_keywords))
                
                # Analyze each keyword
                for keyword in all_keywords[:50]:  # Limit to top 50 per seed
                    analysis = await self._analyze_keyword(
                        keyword, content_type, target_audience, competition_level
                    )
                    if analysis.relevance_score > 0.6:  # Only include relevant keywords
                        keyword_suggestions.append(analysis)
            
            # Sort by optimization potential
            keyword_suggestions.sort(
                key=lambda x: x.optimization_potential,
                reverse=True
            )
            
            # Store keyword research results
            if db:
                await self._store_keyword_research(keyword_suggestions, db)
            
            return keyword_suggestions[:100]  # Return top 100 keywords
            
        except Exception as e:
            logger.error(f"Error performing keyword research: {str(e)}")
            raise
    
    async def track_search_performance(
        self,
        user_id: str,
        content_ids: Optional[List[str]] = None,
        time_period: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Track search engine performance for user's content.
        
        Args:
            user_id: User identifier
            content_ids: Specific content IDs to track
            time_period: Time period in days
            db: Database session
            
        Returns:
            Search performance analytics
        """
        if db is None:
            db = next(get_db())
        
        try:
            # Get user's content
            query = db.query(Content).filter(Content.user_id == user_id)
            if content_ids:
                query = query.filter(Content.id.in_(content_ids))
            
            contents = query.all()
            
            performance_data = {
                "overview": {
                    "total_contents_tracked": len(contents),
                    "average_search_ranking": 0,
                    "total_search_impressions": 0,
                    "total_search_clicks": 0,
                    "average_ctr": 0
                },
                "content_performance": [],
                "keyword_performance": [],
                "trending_keywords": [],
                "opportunities": []
            }
            
            total_ranking = 0
            total_impressions = 0
            total_clicks = 0
            keyword_data = {}
            
            for content in contents:
                # Get search performance data
                search_data = await self._get_search_performance_data(content.id, time_period)
                
                content_perf = {
                    "content_id": content.id,
                    "title": content.title,
                    "average_ranking": search_data.get("average_ranking", 0),
                    "impressions": search_data.get("impressions", 0),
                    "clicks": search_data.get("clicks", 0),
                    "ctr": search_data.get("ctr", 0),
                    "ranking_change": search_data.get("ranking_change", 0)
                }
                
                performance_data["content_performance"].append(content_perf)
                
                # Aggregate data
                total_ranking += content_perf["average_ranking"]
                total_impressions += content_perf["impressions"]
                total_clicks += content_perf["clicks"]
                
                # Collect keyword data
                for keyword_data_item in search_data.get("keywords", []):
                    keyword = keyword_data_item["keyword"]
                    if keyword not in keyword_data:
                        keyword_data[keyword] = {
                            "impressions": 0,
                            "clicks": 0,
                            "rankings": []
                        }
                    keyword_data[keyword]["impressions"] += keyword_data_item.get("impressions", 0)
                    keyword_data[keyword]["clicks"] += keyword_data_item.get("clicks", 0)
                    keyword_data[keyword]["rankings"].append(keyword_data_item.get("ranking", 100))
            
            # Calculate overview metrics
            if contents:
                performance_data["overview"]["average_search_ranking"] = total_ranking / len(contents)
                performance_data["overview"]["total_search_impressions"] = total_impressions
                performance_data["overview"]["total_search_clicks"] = total_clicks
                performance_data["overview"]["average_ctr"] = (
                    total_clicks / total_impressions * 100 if total_impressions > 0 else 0
                )
            
            # Process keyword performance
            for keyword, data in keyword_data.items():
                avg_ranking = sum(data["rankings"]) / len(data["rankings"]) if data["rankings"] else 0
                ctr = data["clicks"] / data["impressions"] * 100 if data["impressions"] > 0 else 0
                
                performance_data["keyword_performance"].append({
                    "keyword": keyword,
                    "average_ranking": avg_ranking,
                    "impressions": data["impressions"],
                    "clicks": data["clicks"],
                    "ctr": ctr
                })
            
            # Sort keyword performance
            performance_data["keyword_performance"].sort(
                key=lambda x: x["impressions"],
                reverse=True
            )
            
            # Identify trending keywords
            performance_data["trending_keywords"] = await self._identify_trending_keywords(
                keyword_data, time_period
            )
            
            # Generate optimization opportunities
            performance_data["opportunities"] = await self._identify_seo_opportunities(
                performance_data, contents
            )
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error tracking search performance: {str(e)}")
            raise
    
    async def generate_seo_recommendations(
        self,
        user_id: str,
        content_type: Optional[str] = None,
        priority_level: str = "high",
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized SEO recommendations for user.
        
        Args:
            user_id: User identifier
            content_type: Specific content type to focus on
            priority_level: Priority level for recommendations
            db: Database session
            
        Returns:
            List of SEO recommendations with priorities
        """
        if db is None:
            db = next(get_db())
        
        try:
            recommendations = []
            
            # Get user's content for analysis
            query = db.query(Content).filter(Content.user_id == user_id)
            if content_type:
                query = query.filter(Content.content_type == content_type)
            
            contents = query.all()
            
            if not contents:
                return [{
                    "type": "content_creation",
                    "priority": "high",
                    "title": "Start Creating Content",
                    "description": "Begin creating content to receive personalized SEO recommendations",
                    "action_items": [
                        "Create your first piece of content",
                        "Add relevant keywords and descriptions",
                        "Optimize titles for search engines"
                    ]
                }]
            
            # Analyze content performance patterns
            content_analysis = await self._analyze_user_content_patterns(contents)
            
            # Generate recommendations based on analysis
            if content_analysis["low_seo_scores"]:
                recommendations.append({
                    "type": "seo_optimization",
                    "priority": "high",
                    "title": "Improve SEO Scores for Low-Performing Content",
                    "description": f"{len(content_analysis['low_seo_scores'])} pieces of content have low SEO scores",
                    "action_items": [
                        "Optimize titles with target keywords",
                        "Improve meta descriptions",
                        "Add relevant hashtags and tags"
                    ],
                    "affected_content": content_analysis["low_seo_scores"][:5]
                })
            
            if content_analysis["missing_keywords"]:
                recommendations.append({
                    "type": "keyword_optimization",
                    "priority": "medium",
                    "title": "Target High-Opportunity Keywords",
                    "description": "Leverage untapped keyword opportunities",
                    "action_items": [
                        "Create content targeting high-volume, low-competition keywords",
                        "Optimize existing content for related keywords",
                        "Monitor keyword performance regularly"
                    ],
                    "keywords": content_analysis["missing_keywords"][:10]
                })
            
            if content_analysis["inconsistent_optimization"]:
                recommendations.append({
                    "type": "consistency",
                    "priority": "medium",
                    "title": "Maintain SEO Consistency",
                    "description": "Ensure consistent SEO practices across all content",
                    "action_items": [
                        "Create SEO templates for different content types",
                        "Establish keyword research process",
                        "Set up regular SEO audits"
                    ]
                })
            
            # Platform-specific recommendations
            platform_recommendations = await self._generate_platform_seo_recommendations(
                contents, user_id
            )
            recommendations.extend(platform_recommendations)
            
            # Content type specific recommendations
            if content_type:
                type_recommendations = await self._generate_content_type_recommendations(
                    contents, content_type
                )
                recommendations.extend(type_recommendations)
            
            # Sort by priority and relevance
            priority_order = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda x: priority_order.get(x["priority"], 0),
                reverse=True
            )
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error generating SEO recommendations: {str(e)}")
            raise
    
    # Private helper methods
    async def _analyze_title_seo(self, content: Content) -> Dict[str, Any]:
        """Analyze title SEO optimization."""
        title = content.title or ""
        score = 0
        recommendations = []
        
        # Length check (optimal 50-60 characters)
        if len(title) < 30:
            recommendations.append("Title too short - aim for 50-60 characters")
            score += 20
        elif len(title) > 70:
            recommendations.append("Title too long - keep under 60 characters")
            score += 30
        else:
            score += 40
        
        # Keyword presence
        if content.target_keywords:
            keywords_in_title = any(
                keyword.lower() in title.lower()
                for keyword in content.target_keywords.split(",")
            )
            if keywords_in_title:
                score += 30
            else:
                recommendations.append("Include target keywords in title")
        
        # Readability
        if re.search(r'[!?]', title):
            score += 15
        
        # Uniqueness check
        if not re.search(r'\d+', title) and len(title.split()) > 5:
            score += 15
        
        return {
            "score": min(score, 100),
            "recommendations": recommendations
        }
    
    async def _analyze_description_seo(self, content: Content) -> Dict[str, Any]:
        """Analyze description SEO optimization."""
        description = content.description or ""
        score = 0
        recommendations = []
        
        # Length check (optimal 150-160 characters)
        if len(description) < 120:
            recommendations.append("Description too short - aim for 150-160 characters")
            score += 20
        elif len(description) > 170:
            recommendations.append("Description too long - keep under 160 characters")
            score += 30
        else:
            score += 40
        
        # Keyword presence
        if content.target_keywords:
            keywords_in_desc = any(
                keyword.lower() in description.lower()
                for keyword in content.target_keywords.split(",")
            )
            if keywords_in_desc:
                score += 30
            else:
                recommendations.append("Include target keywords in description")
        
        # Call to action
        cta_words = ["visit", "download", "watch", "read", "subscribe", "follow"]
        if any(word in description.lower() for word in cta_words):
            score += 15
        else:
            recommendations.append("Add call-to-action in description")
        
        # Readability
        if len(description.split()) > 10:
            score += 15
        
        return {
            "score": min(score, 100),
            "recommendations": recommendations
        }
    
    async def _analyze_keyword_optimization(self, content: Content, target_keywords: Optional[List[str]]) -> Dict[str, Any]:
        """Analyze keyword optimization."""
        text_content = f"{content.title or ''} {content.description or ''}"
        score = 0
        recommendations = []
        
        if not target_keywords:
            target_keywords = content.target_keywords.split(",") if content.target_keywords else []
        
        if not target_keywords:
            recommendations.append("Define target keywords for content")
            return {"score": 0, "recommendations": recommendations}
        
        # Keyword density analysis
        words = word_tokenize(text_content.lower())
        words = [word for word in words if word not in self.stop_words and word.isalpha()]
        total_words = len(words)
        
        if total_words == 0:
            recommendations.append("Add more descriptive content")
            return {"score": 20, "recommendations": recommendations}
        
        keyword_density = {}
        for keyword in target_keywords:
            keyword = keyword.strip().lower()
            count = text_content.lower().count(keyword)
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_density[keyword] = density
            
            if density < 0.5:
                recommendations.append(f"Increase density of keyword '{keyword}'")
            elif density > 3:
                recommendations.append(f"Reduce density of keyword '{keyword}' to avoid spam")
            else:
                score += 25
        
        # Semantic keyword analysis
        semantic_score = await self._analyze_semantic_keywords(text_content, target_keywords)
        score += semantic_score
        
        return {
            "score": min(score, 100),
            "recommendations": recommendations,
            "keyword_density": keyword_density
        }
    
    async def _analyze_content_readability(self, content: Content) -> Dict[str, Any]:
        """Analyze content readability."""
        text_content = f"{content.title or ''} {content.description or ''}"
        score = 0
        recommendations = []
        
        if len(text_content.strip()) < 50:
            recommendations.append("Add more content for readability analysis")
            return {"score": 30, "recommendations": recommendations}
        
        # Flesch Reading Ease
        try:
            flesch_score = flesch_reading_ease(text_content)
            if flesch_score >= 60:  # Good readability
                score += 40
            elif flesch_score >= 30:  # Moderate readability
                score += 25
                recommendations.append("Improve readability with shorter sentences")
            else:
                score += 10
                recommendations.append("Significantly improve readability")
        except:
            score += 20
        
        # Grade level
        try:
            grade_level = flesch_kincaid_grade(text_content)
            if grade_level <= 8:  # Good for general audience
                score += 30
            elif grade_level <= 12:
                score += 20
                recommendations.append("Simplify language for broader audience")
            else:
                score += 10
                recommendations.append("Use simpler vocabulary")
        except:
            score += 15
        
        # Sentence length analysis
        sentences = text_content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_sentence_length <= 15:
            score += 30
        elif avg_sentence_length <= 25:
            score += 20
        else:
            recommendations.append("Use shorter sentences for better readability")
            score += 10
        
        return {
            "score": min(score, 100),
            "recommendations": recommendations
        }
    
    async def _calculate_overall_seo_score(self, scores: List[float]) -> float:
        """Calculate overall SEO score from individual scores."""
        if not scores:
            return 0
        
        # Weighted average (title and keywords more important)
        weights = [0.25, 0.2, 0.25, 0.15, 0.1, 0.05]  # Adjust based on importance
        if len(scores) != len(weights):
            return sum(scores) / len(scores)  # Simple average if weights don't match
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return round(weighted_sum, 2)
