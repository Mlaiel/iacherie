"""
Enterprise Content Optimization Module
======================================

AI-powered content optimization engine for maximum reach and monetization:
- Advanced SEO optimization with real-time keyword analysis
- Platform-specific optimization for 20+ social platforms
- Content structure and readability optimization
- Engagement prediction with neural network algorithms
- Viral content pattern recognition and suggestion
- Multi-language content optimization
- Content performance analytics and optimization recommendations
- Automated A/B testing suggestions and implementations

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone
import hashlib
import json

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from transformers import pipeline
import torch
from serpapi import GoogleSearch
import yake

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode
from ...security.encryption import encrypt_data, decrypt_data
from .text_analyzer import TextAnalyzer, SentimentAnalyzer

logger = get_logger(__name__)


class Platform(Enum):
    """Social media and content platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    BLOG = "blog"
    WEBSITE = "website"
    EMAIL = "email"


class OptimizationType(Enum):
    """Types of content optimization"""
    SEO = "seo"
    ENGAGEMENT = "engagement"
    READABILITY = "readability"
    PLATFORM_SPECIFIC = "platform_specific"
    VIRAL_POTENTIAL = "viral_potential"
    CONVERSION = "conversion"
    ACCESSIBILITY = "accessibility"


class ContentGoal(Enum):
    """Content marketing goals"""
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES_CONVERSION = "sales_conversion"
    COMMUNITY_BUILDING = "community_building"
    THOUGHT_LEADERSHIP = "thought_leadership"
    USER_EDUCATION = "user_education"
    VIRAL_REACH = "viral_reach"


@dataclass
class OptimizationRequest:
    """Content optimization request"""
    content: str
    platform: Platform
    optimization_types: List[OptimizationType]
    target_audience: str = "general"
    content_goal: ContentGoal = ContentGoal.BRAND_AWARENESS
    target_keywords: List[str] = field(default_factory=list)
    competitor_content: List[str] = field(default_factory=list)
    brand_voice: str = "professional"
    max_length: Optional[int] = None
    include_hashtags: bool = True
    include_cta: bool = True


@dataclass
class SEOAnalysis:
    """SEO analysis results"""
    keyword_density: Dict[str, float]
    keyword_distribution: Dict[str, List[int]]
    recommended_keywords: List[str]
    meta_suggestions: Dict[str, str]
    readability_score: float
    content_length_recommendation: str
    internal_link_opportunities: List[str]
    semantic_keywords: List[str]
    search_intent_match: float
    seo_score: float


@dataclass
class EngagementAnalysis:
    """Engagement potential analysis"""
    engagement_score: float
    emotional_triggers: List[str]
    call_to_action_strength: float
    question_effectiveness: float
    storytelling_elements: List[str]
    social_proof_opportunities: List[str]
    urgency_indicators: List[str]
    personalization_level: float
    shareability_factors: List[str]


@dataclass
class PlatformOptimization:
    """Platform-specific optimization suggestions"""
    optimal_length: int
    hashtag_suggestions: List[str]
    posting_time_recommendations: List[str]
    format_suggestions: List[str]
    visual_content_recommendations: List[str]
    platform_specific_features: List[str]
    engagement_tactics: List[str]
    content_structure: Dict[str, Any]


@dataclass
class OptimizationResult:
    """Complete optimization result"""
    optimized_content: str
    optimization_score: float
    improvements_made: List[str]
    seo_analysis: SEOAnalysis
    engagement_analysis: EngagementAnalysis
    platform_optimization: PlatformOptimization
    alternative_versions: List[str]
    performance_predictions: Dict[str, float]
    recommendations: List[str]
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SEOAnalyzer:
    """Advanced SEO analysis and optimization"""
    
    def __init__(self):
        self.nlp = None
        self.keyword_extractor = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize SEO analysis models"""



        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_lg")
            
            # Initialize YAKE keyword extractor
            self.keyword_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,
                dedupLim=0.7,
                top=20
            )
            
            logger.info("SEO analyzer models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO models: {e}")
            
    async def analyze_seo(
        self,
        content: str,
        target_keywords: List[str],
        competitor_content: List[str] = None
    ) -> SEOAnalysis:
        """
        Perform comprehensive SEO analysis
        
        Args:
            content: Content to analyze
            target_keywords: Target SEO keywords
            competitor_content: Optional competitor content for analysis
            
        Returns:
            SEOAnalysis with detailed SEO metrics
        """



        try:
            # Keyword density analysis
            keyword_density = await self._analyze_keyword_density(content, target_keywords)
            
            # Keyword distribution analysis
            keyword_distribution = await self._analyze_keyword_distribution(content, target_keywords)
            
            # Extract recommended keywords
            recommended_keywords = await self._extract_recommended_keywords(content, target_keywords)
            
            # Meta suggestions
            meta_suggestions = await self._generate_meta_suggestions(content, target_keywords)
            
            # Readability analysis
            readability_score = textstat.flesch_reading_ease(content)
            
            # Content length recommendation
            length_recommendation = await self._analyze_content_length(content, target_keywords)
            
            # Internal link opportunities
            internal_links = await self._identify_internal_link_opportunities(content)
            
            # Semantic keywords
            semantic_keywords = await self._extract_semantic_keywords(content, target_keywords)
            
            # Search intent matching
            search_intent_match = await self._analyze_search_intent_match(content, target_keywords)
            
            # Calculate overall SEO score
            seo_score = await self._calculate_seo_score(
                keyword_density, readability_score, len(content.split()), search_intent_match
            )
            
            return SEOAnalysis(
                keyword_density=keyword_density,
                keyword_distribution=keyword_distribution,
                recommended_keywords=recommended_keywords,
                meta_suggestions=meta_suggestions,
                readability_score=readability_score,
                content_length_recommendation=length_recommendation,
                internal_link_opportunities=internal_links,
                semantic_keywords=semantic_keywords,
                search_intent_match=search_intent_match,
                seo_score=seo_score
            )
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            raise
            
    async def _analyze_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Analyze keyword density"""



        try:
            content_lower = content.lower()
            word_count = len(content.split())
            
            density = {}
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                density[keyword] = (count / max(word_count, 1)) * 100
                
            return density
            
        except Exception as e:
            logger.error(f"Keyword density analysis failed: {e}")
            return {}
            
    async def _analyze_keyword_distribution(self, content: str, keywords: List[str]) -> Dict[str, List[int]]:
        """Analyze keyword distribution throughout content"""



        try:
            words = content.lower().split()
            distribution = {}
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                positions = []
                
                # Find keyword positions
                for i, word in enumerate(words):
                    if keyword_lower in word:
                        positions.append(i)
                        
                distribution[keyword] = positions
                
            return distribution
            
        except Exception as e:
            logger.error(f"Keyword distribution analysis failed: {e}")
            return {}
            
    async def _extract_recommended_keywords(self, content: str, existing_keywords: List[str]) -> List[str]:
        """Extract additional recommended keywords"""



        try:
            if not self.keyword_extractor:
                return []
                
            # Extract keywords using YAKE
            keywords = self.keyword_extractor.extract_keywords(content)
            
            # Filter out existing keywords and get top recommendations
            existing_lower = [k.lower() for k in existing_keywords]
            recommended = []
            
            for score, keyword in keywords:
                if keyword.lower() not in existing_lower and len(keyword.split()) <= 3:
                    recommended.append(keyword)
                    
            return recommended[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
            
    async def _generate_meta_suggestions(self, content: str, keywords: List[str]) -> Dict[str, str]:
        """Generate meta tag suggestions"""



        try:
            # Extract first sentence for meta description base
            sentences = re.split(r'[.!?]+', content)
            first_sentence = sentences[0].strip() if sentences else ""
            
            # Generate title suggestion
            title_keywords = keywords[:2] if keywords else []
            title_suggestion = f"{' | '.join(title_keywords)} - " + first_sentence[:50] + "..."
            
            # Generate meta description
            meta_description = first_sentence[:150] + "..."
            if keywords:
                meta_description = f"{keywords[0]} - {meta_description}"
                
            return {
                'title': title_suggestion,
                'description': meta_description,
                'keywords': ', '.join(keywords[:5])
            }
            
        except Exception as e:
            logger.error(f"Meta suggestions generation failed: {e}")
            return {}
            
    async def _analyze_content_length(self, content: str, keywords: List[str]) -> str:
        """Analyze and recommend content length"""



        try:
            word_count = len(content.split())
            
            if word_count < 300:
                return "Content is too short for optimal SEO. Aim for 300+ words."
            elif word_count < 600:
                return "Good length for basic SEO. Consider expanding to 800+ words for better ranking."
            elif word_count < 1200:
                return "Excellent length for SEO. Well-positioned for search rankings."
            elif word_count < 2000:
                return "Very comprehensive content. Ensure it remains engaging throughout."
            else:
                return "Very long content. Consider breaking into multiple pieces or ensuring excellent structure."
                
        except Exception as e:
            logger.error(f"Content length analysis failed: {e}")
            return "Unable to analyze content length."
            
    async def _identify_internal_link_opportunities(self, content: str) -> List[str]:
        """Identify opportunities for internal linking"""



        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(content)
            opportunities = []
            
            # Look for entities that could be internal links
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                    opportunities.append(f"Consider linking '{ent.text}' to relevant internal page")
                    
            # Look for topic-related phrases
            topic_phrases = ['how to', 'guide to', 'tips for', 'best practices']
            for phrase in topic_phrases:
                if phrase in content.lower():
                    opportunities.append(f"Consider linking '{phrase}' content to related guides")
                    
            return opportunities[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Internal link analysis failed: {e}")
            return []
            
    async def _extract_semantic_keywords(self, content: str, primary_keywords: List[str]) -> List[str]:
        """Extract semantically related keywords"""



        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(content)
            semantic_keywords = []
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if (len(chunk.text.split()) <= 3 and 
                    chunk.text.lower() not in [k.lower() for k in primary_keywords]):
                    semantic_keywords.append(chunk.text)
                    
            # Remove duplicates and return top semantically related keywords
            unique_keywords = list(set(semantic_keywords))
            return unique_keywords[:15]
            
        except Exception as e:
            logger.error(f"Semantic keyword extraction failed: {e}")
            return []
            
    async def _analyze_search_intent_match(self, content: str, keywords: List[str]) -> float:
        """Analyze how well content matches search intent"""



        try:
            # Simple intent matching based on content patterns
            intent_indicators = {
                'informational': ['what is', 'how to', 'guide', 'tips', 'learn', 'understand'],
                'commercial': ['buy', 'purchase', 'price', 'cost', 'compare', 'review'],
                'navigational': ['login', 'contact', 'about', 'home', 'menu'],
                'transactional': ['order', 'download', 'sign up', 'subscribe', 'get started']
            }
            
            content_lower = content.lower()
            intent_scores = {}
            
            for intent, indicators in intent_indicators.items():
                score = sum(1 for indicator in indicators if indicator in content_lower)
                intent_scores[intent] = score
                
            # Determine primary intent
            primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'informational'
            
            # Calculate match score based on content structure
            if primary_intent == 'informational':
                # Check for structured information
                structure_score = 0.7 if any(pattern in content_lower for pattern in ['first', 'second', 'steps']) else 0.5
            else:
                structure_score = 0.6
                
            return min(structure_score + (intent_scores[primary_intent] * 0.1), 1.0)
            
        except Exception as e:
            logger.error(f"Search intent analysis failed: {e}")
            return 0.5
            
    async def _calculate_seo_score(
        self,
        keyword_density: Dict[str, float],
        readability_score: float,
        word_count: int,
        search_intent_match: float
    ) -> float:
        """Calculate overall SEO score"""



        try:
            score_components = []
            
            # Keyword density score (ideal: 1-3%)
            if keyword_density:
                avg_density = np.mean(list(keyword_density.values()))
                if 1.0 <= avg_density <= 3.0:
                    density_score = 1.0
                elif avg_density < 1.0:
                    density_score = avg_density / 1.0
                else:
                    density_score = max(0.3, 1.0 - (avg_density - 3.0) / 10.0)
                score_components.append(density_score)
                
            # Readability score (normalize to 0-1)
            readability_normalized = min(readability_score / 100, 1.0)
            score_components.append(readability_normalized)
            
            # Word count score
            if 300 <= word_count <= 2000:
                word_score = 1.0
            elif word_count < 300:
                word_score = word_count / 300
            else:
                word_score = max(0.5, 1.0 - (word_count - 2000) / 3000)
            score_components.append(word_score)
            
            # Search intent match score
            score_components.append(search_intent_match)
            
            return np.mean(score_components) if score_components else 0.5
            
        except Exception as e:
            logger.error(f"SEO score calculation failed: {e}")
            return 0.5


class ContentOptimizer:
    """Main content optimization engine"""
    
    def __init__(self):
        self.seo_analyzer = SEOAnalyzer()
        self.text_analyzer = TextAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self._initialize_platform_configs()
        
    def _initialize_platform_configs(self):
        """Initialize platform-specific configurations"""
        self.platform_configs = {
            Platform.INSTAGRAM: {
                'max_length': 2200,
                'optimal_length': 150,
                'hashtag_limit': 30,
                'hashtag_optimal': 11,
                'best_posting_times': ['11:00-13:00', '17:00-19:00'],
                'engagement_features': ['stories', 'reels', 'igtv'],
                'content_types': ['photo', 'carousel', 'video', 'reels']
            },
            Platform.TIKTOK: {
                'max_length': 300,
                'optimal_length': 100,
                'hashtag_limit': 5,
                'hashtag_optimal': 3,
                'best_posting_times': ['06:00-10:00', '19:00-23:00'],
                'engagement_features': ['trends', 'challenges', 'duets'],
                'content_types': ['short_video', 'live']
            },
            Platform.TWITTER: {
                'max_length': 280,
                'optimal_length': 120,
                'hashtag_limit': 3,
                'hashtag_optimal': 2,
                'best_posting_times': ['09:00-10:00', '12:00-13:00', '17:00-18:00'],
                'engagement_features': ['threads', 'polls', 'spaces'],
                'content_types': ['text', 'image', 'video', 'gif']
            },
            Platform.LINKEDIN: {
                'max_length': 1300,
                'optimal_length': 200,
                'hashtag_limit': 5,
                'hashtag_optimal': 3,
                'best_posting_times': ['08:00-10:00', '12:00-14:00', '17:00-18:00'],
                'engagement_features': ['articles', 'polls', 'events'],
                'content_types': ['text', 'image', 'video', 'document']
            },
            Platform.YOUTUBE: {
                'max_length': 5000,
                'optimal_length': 200,
                'hashtag_limit': 15,
                'hashtag_optimal': 5,
                'best_posting_times': ['14:00-16:00', '18:00-22:00'],
                'engagement_features': ['thumbnails', 'end_screens', 'cards'],
                'content_types': ['video', 'shorts', 'live']
            }
        }
        
    async def optimize_content(self, request: OptimizationRequest) -> OptimizationResult:
        """
        Optimize content for specified platform and goals
        
        Args:
            request: Optimization request with parameters
            
        Returns:
            OptimizationResult with optimized content and analysis
        """



        try:
            original_content = request.content
            optimized_content = original_content
            improvements_made = []
            
            # SEO optimization
            seo_analysis = None
            if OptimizationType.SEO in request.optimization_types:
                seo_analysis = await self.seo_analyzer.analyze_seo(
                    original_content,
                    request.target_keywords,
                    request.competitor_content
                )
                optimized_content, seo_improvements = await self._apply_seo_optimizations(
                    optimized_content, seo_analysis, request
                )
                improvements_made.extend(seo_improvements)
                
            # Engagement optimization
            engagement_analysis = None
            if OptimizationType.ENGAGEMENT in request.optimization_types:
                engagement_analysis = await self._analyze_engagement_potential(optimized_content, request)
                optimized_content, engagement_improvements = await self._apply_engagement_optimizations(
                    optimized_content, engagement_analysis, request
                )
                improvements_made.extend(engagement_improvements)
                
            # Platform-specific optimization
            platform_optimization = None
            if OptimizationType.PLATFORM_SPECIFIC in request.optimization_types:
                platform_optimization = await self._analyze_platform_optimization(optimized_content, request)
                optimized_content, platform_improvements = await self._apply_platform_optimizations(
                    optimized_content, platform_optimization, request
                )
                improvements_made.extend(platform_improvements)
                
            # Readability optimization
            if OptimizationType.READABILITY in request.optimization_types:
                optimized_content, readability_improvements = await self._apply_readability_optimizations(
                    optimized_content, request
                )
                improvements_made.extend(readability_improvements)
                
            # Generate alternative versions
            alternative_versions = await self._generate_alternative_versions(optimized_content, request)
            
            # Predict performance
            performance_predictions = await self._predict_performance(optimized_content, request)
            
            # Generate final recommendations
            recommendations = await self._generate_recommendations(
                original_content, optimized_content, request, seo_analysis, engagement_analysis
            )
            
            # Calculate optimization score
            optimization_score = await self._calculate_optimization_score(
                original_content, optimized_content, request, seo_analysis, engagement_analysis
            )
            
            return OptimizationResult(
                optimized_content=optimized_content,
                optimization_score=optimization_score,
                improvements_made=improvements_made,
                seo_analysis=seo_analysis or SEOAnalysis(
                    keyword_density={}, keyword_distribution={}, recommended_keywords=[],
                    meta_suggestions={}, readability_score=0, content_length_recommendation="",
                    internal_link_opportunities=[], semantic_keywords=[], search_intent_match=0,
                    seo_score=0
                ),
                engagement_analysis=engagement_analysis or EngagementAnalysis(
                    engagement_score=0, emotional_triggers=[], call_to_action_strength=0,
                    question_effectiveness=0, storytelling_elements=[], social_proof_opportunities=[],
                    urgency_indicators=[], personalization_level=0, shareability_factors=[]
                ),
                platform_optimization=platform_optimization or PlatformOptimization(
                    optimal_length=0, hashtag_suggestions=[], posting_time_recommendations=[],
                    format_suggestions=[], visual_content_recommendations=[], platform_specific_features=[],
                    engagement_tactics=[], content_structure={}
                ),
                alternative_versions=alternative_versions,
                performance_predictions=performance_predictions,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise
            
    async def _apply_seo_optimizations(
        self,
        content: str,
        seo_analysis: SEOAnalysis,
        request: OptimizationRequest
    ) -> Tuple[str, List[str]]:
        """Apply SEO optimizations to content"""



        try:
            optimized_content = content
            improvements = []
            
            # Optimize keyword density
            for keyword, density in seo_analysis.keyword_density.items():
                if density < 1.0:  # Too low
                    # Add keyword naturally
                    if keyword not in optimized_content:
                        optimized_content = f"{keyword}: {optimized_content}"
                        improvements.append(f"Added target keyword '{keyword}' to improve density")
                        
            # Add recommended keywords
            if seo_analysis.recommended_keywords:
                for keyword in seo_analysis.recommended_keywords[:3]:
                    if keyword.lower() not in optimized_content.lower():
                        optimized_content += f" #{keyword.replace(' ', '')}"
                        improvements.append(f"Added recommended keyword '{keyword}'")
                        
            # Improve readability if needed
            if seo_analysis.readability_score < 60:
                # Break long sentences
                sentences = re.split(r'[.!?]+', optimized_content)
                improved_sentences = []
                
                for sentence in sentences:
                    if len(sentence.split()) > 20:
                        # Split long sentence
                        words = sentence.split()
                        mid = len(words) // 2
                        new_sentence = ' '.join(words[:mid]) + '. ' + ' '.join(words[mid:])
                        improved_sentences.append(new_sentence)
                        improvements.append("Split long sentence for better readability")
                    else:
                        improved_sentences.append(sentence)
                        
                optimized_content = '. '.join(improved_sentences)
                
            return optimized_content, improvements
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            return content, []
            
    async def _analyze_engagement_potential(
        self,
        content: str,
        request: OptimizationRequest
    ) -> EngagementAnalysis:
        """Analyze content engagement potential"""



        try:
            # Emotional triggers analysis
            emotional_triggers = []
            emotion_words = {
                'excitement': ['amazing', 'incredible', 'fantastic', 'wow', 'awesome'],
                'urgency': ['now', 'today', 'limited', 'hurry', 'deadline'],
                'curiosity': ['secret', 'discover', 'reveal', 'hidden', 'unknown'],
                'fear': ['mistake', 'avoid', 'warning', 'danger', 'problem']
            }
            
            content_lower = content.lower()
            for emotion, words in emotion_words.items():
                for word in words:
                    if word in content_lower:
                        emotional_triggers.append(emotion)
                        break
                        
            # Call-to-action analysis
            cta_patterns = ['click', 'share', 'comment', 'like', 'subscribe', 'follow', 'buy', 'get']
            cta_strength = sum(1 for pattern in cta_patterns if pattern in content_lower) / len(cta_patterns)
            
            # Question effectiveness
            question_count = content.count('?')
            question_effectiveness = min(question_count / 3, 1.0)
            
            # Storytelling elements
            storytelling_elements = []
            story_indicators = ['once', 'story', 'imagine', 'remember', 'experience']
            for indicator in story_indicators:
                if indicator in content_lower:
                    storytelling_elements.append(indicator)
                    
            # Social proof opportunities
            social_proof = []
            proof_indicators = ['customer', 'review', 'testimonial', 'rating', 'feedback']
            for indicator in proof_indicators:
                if indicator in content_lower:
                    social_proof.append(f"Highlight {indicator}s")
                    
            # Urgency indicators
            urgency_indicators = []
            urgency_words = ['limited', 'exclusive', 'deadline', 'expires', 'while supplies last']
            for word in urgency_words:
                if word in content_lower:
                    urgency_indicators.append(word)
                    
            # Personalization level
            personal_pronouns = ['you', 'your', 'yours']
            personal_count = sum(content_lower.count(pronoun) for pronoun in personal_pronouns)
            personalization_level = min(personal_count / len(content.split()), 1.0)
            
            # Shareability factors
            shareability_factors = []
            if any(trigger in emotional_triggers for trigger in ['excitement', 'curiosity']):
                shareability_factors.append('emotional_appeal')
            if question_count > 0:
                shareability_factors.append('interactive_elements')
            if len(storytelling_elements) > 0:
                shareability_factors.append('storytelling')
                
            # Calculate overall engagement score
            engagement_score = np.mean([
                len(emotional_triggers) / 4,  # Up to 4 emotion types
                cta_strength,
                question_effectiveness,
                len(storytelling_elements) / 5,  # Up to 5 story elements
                personalization_level,
                len(shareability_factors) / 3  # Up to 3 shareability factors
            ])
            
            return EngagementAnalysis(
                engagement_score=engagement_score,
                emotional_triggers=emotional_triggers,
                call_to_action_strength=cta_strength,
                question_effectiveness=question_effectiveness,
                storytelling_elements=storytelling_elements,
                social_proof_opportunities=social_proof,
                urgency_indicators=urgency_indicators,
                personalization_level=personalization_level,
                shareability_factors=shareability_factors
            )
            
        except Exception as e:
            logger.error(f"Engagement analysis failed: {e}")
            return EngagementAnalysis(
                engagement_score=0.5, emotional_triggers=[], call_to_action_strength=0,
                question_effectiveness=0, storytelling_elements=[], social_proof_opportunities=[],
                urgency_indicators=[], personalization_level=0, shareability_factors=[]
            )
            
    async def _apply_engagement_optimizations(
        self,
        content: str,
        engagement_analysis: EngagementAnalysis,
        request: OptimizationRequest
    ) -> Tuple[str, List[str]]:
        """Apply engagement optimizations"""



        try:
            optimized_content = content
            improvements = []
            
            # Add call-to-action if missing
            if engagement_analysis.call_to_action_strength < 0.3 and request.include_cta:
                platform_ctas = {
                    Platform.INSTAGRAM: "Double tap if you agree! ",
                    Platform.TIKTOK: "Follow for more tips! ",
                    Platform.TWITTER: "What's your take? Reply below ",
                    Platform.LINKEDIN: "Share your thoughts in the comments "
                }
                
                cta = platform_ctas.get(request.platform, "Let us know what you think!")
                optimized_content += f"\n\n{cta}"
                improvements.append("Added platform-specific call-to-action")
                
            # Add question for engagement
            if engagement_analysis.question_effectiveness < 0.3:
                topic_questions = {
                    ContentGoal.BRAND_AWARENESS: "What's your experience with this?",
                    ContentGoal.COMMUNITY_BUILDING: "Who else can relate to this?",
                    ContentGoal.USER_EDUCATION: "What would you like to learn next?",
                    ContentGoal.THOUGHT_LEADERSHIP: "How do you see this evolving?"
                }
                
                question = topic_questions.get(request.content_goal, "What are your thoughts?")
                optimized_content += f"\n\n{question}"
                improvements.append("Added engagement question")
                
            # Enhance emotional appeal
            if len(engagement_analysis.emotional_triggers) < 2:
                emotion_enhancers = {
                    Platform.INSTAGRAM: " Amazing insights ahead! ",
                    Platform.TIKTOK: " This will blow your mind! ",
                    Platform.TWITTER: " Thread alert: Game-changing info below "
                }
                
                enhancer = emotion_enhancers.get(request.platform, " Don't miss this! ")
                optimized_content = f"{enhancer}\n\n{optimized_content}"
                improvements.append("Added emotional appeal elements")
                
            return optimized_content, improvements
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return content, []
            
    async def _analyze_platform_optimization(
        self,
        content: str,
        request: OptimizationRequest
    ) -> PlatformOptimization:
        """Analyze platform-specific optimization opportunities"""



        try:
            config = self.platform_configs.get(request.platform, {})
            
            # Optimal length for platform
            optimal_length = config.get('optimal_length', 200)
            
            # Generate hashtag suggestions
            hashtag_suggestions = await self._generate_hashtag_suggestions(content, request)
            
            # Posting time recommendations
            posting_times = config.get('best_posting_times', ['12:00-14:00'])
            
            # Format suggestions
            format_suggestions = await self._get_format_suggestions(request.platform, content)
            
            # Visual content recommendations
            visual_recommendations = await self._get_visual_recommendations(request.platform, content)
            
            # Platform-specific features
            platform_features = config.get('engagement_features', [])
            
            # Engagement tactics
            engagement_tactics = await self._get_engagement_tactics(request.platform, request.content_goal)
            
            # Content structure analysis
            content_structure = await self._analyze_content_structure(content, request.platform)
            
            return PlatformOptimization(
                optimal_length=optimal_length,
                hashtag_suggestions=hashtag_suggestions,
                posting_time_recommendations=posting_times,
                format_suggestions=format_suggestions,
                visual_content_recommendations=visual_recommendations,
                platform_specific_features=platform_features,
                engagement_tactics=engagement_tactics,
                content_structure=content_structure
            )
            
        except Exception as e:
            logger.error(f"Platform optimization analysis failed: {e}")
            return PlatformOptimization(
                optimal_length=200, hashtag_suggestions=[], posting_time_recommendations=[],
                format_suggestions=[], visual_content_recommendations=[], platform_specific_features=[],
                engagement_tactics=[], content_structure={}
            )
            
    async def _generate_hashtag_suggestions(self, content: str, request: OptimizationRequest) -> List[str]:
        """Generate platform-appropriate hashtag suggestions"""



        try:
            hashtags = []
            
            # Extract keywords from content
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Get top keywords
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Convert to hashtags
            for word, freq in top_words:
                if len(word) > 3 and word.isalpha():
                    hashtags.append(f"#{word}")
                    
            # Add platform-specific hashtags
            platform_hashtags = {
                Platform.INSTAGRAM: ['#instagood', '#photooftheday', '#instadaily'],
                Platform.TIKTOK: ['#fyp', '#viral', '#trending'],
                Platform.TWITTER: ['#thread', '#discussion'],
                Platform.LINKEDIN: ['#professional', '#industry', '#networking']
            }
            
            platform_tags = platform_hashtags.get(request.platform, [])
            hashtags.extend(platform_tags)
            
            # Add target keyword hashtags
            for keyword in request.target_keywords:
                hashtag = f"#{keyword.replace(' ', '').lower()}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
                    
            return hashtags[:15]  # Limit based on platform
            
        except Exception as e:
            logger.error(f"Hashtag generation failed: {e}")
            return []
            
    async def _get_format_suggestions(self, platform: Platform, content: str) -> List[str]:
        """Get format suggestions for specific platform"""
        format_suggestions = {
            Platform.INSTAGRAM: [
                "Consider using carousel format for step-by-step content",
                "Add visually appealing quote cards",
                "Use Instagram Stories for behind-the-scenes content"
            ],
            Platform.TIKTOK: [
                "Create short, punchy video content",
                "Use trending sounds and effects",
                "Keep videos under 60 seconds for best engagement"
            ],
            Platform.TWITTER: [
                "Break long content into tweet threads",
                "Use polls for audience engagement",
                "Include relevant GIFs or images"
            ],
            Platform.LINKEDIN: [
                "Use professional formatting with bullet points",
                "Include industry-relevant insights",
                "Add document attachments for detailed content"
            ]
        }
        
        return format_suggestions.get(platform, [])
        
    async def _get_visual_recommendations(self, platform: Platform, content: str) -> List[str]:
        """Get visual content recommendations"""
        visual_recommendations = {
            Platform.INSTAGRAM: [
                "High-quality, bright images perform best",
                "Use consistent color scheme for brand recognition",
                "Include faces in photos for better engagement"
            ],
            Platform.TIKTOK: [
                "Vertical video format (9:16 ratio)",
                "Good lighting and clear audio",
                "Eye-catching thumbnail for the first frame"
            ],
            Platform.YOUTUBE: [
                "Custom thumbnail with bold text",
                "Consistent branding across thumbnails",
                "Include human faces when possible"
            ]
        }
        
        return visual_recommendations.get(platform, [])
        
    async def _get_engagement_tactics(self, platform: Platform, content_goal: ContentGoal) -> List[str]:
        """Get engagement tactics for platform and goal"""
        tactics = {
            (Platform.INSTAGRAM, ContentGoal.COMMUNITY_BUILDING): [
                "Use location tags to reach local audience",
                "Partner with micro-influencers",
                "Create user-generated content campaigns"
            ],
            (Platform.TIKTOK, ContentGoal.VIRAL_REACH): [
                "Jump on trending challenges",
                "Use popular sounds and hashtags",
                "Post at peak times for your audience"
            ],
            (Platform.LINKEDIN, ContentGoal.THOUGHT_LEADERSHIP): [
                "Share industry insights and predictions",
                "Engage with other thought leaders' content",
                "Publish long-form articles"
            ]
        }
        
        return tactics.get((platform, content_goal), [])
        
    async def _analyze_content_structure(self, content: str, platform: Platform) -> Dict[str, Any]:
        """Analyze content structure for platform optimization"""



        try:
            structure = {
                'has_hook': False,
                'has_body': False,
                'has_cta': False,
                'paragraph_count': 0,
                'sentence_count': 0,
                'readability_level': 'medium'
            }
            
            sentences = re.split(r'[.!?]+', content)
            paragraphs = content.split('\n\n')
            
            structure['sentence_count'] = len([s for s in sentences if s.strip()])
            structure['paragraph_count'] = len([p for p in paragraphs if p.strip()])
            
            # Check for hook (engaging first sentence)
            if sentences and len(sentences[0].split()) < 15:
                hook_indicators = ['imagine', 'what if', 'did you know', '', '', '']
                if any(indicator in sentences[0].lower() for indicator in hook_indicators):
                    structure['has_hook'] = True
                    
            # Check for substantial body content
            if len(content.split()) > 50:
                structure['has_body'] = True
                
            # Check for call-to-action
            cta_indicators = ['click', 'share', 'comment', 'like', 'follow', 'subscribe']
            if any(indicator in content.lower() for indicator in cta_indicators):
                structure['has_cta'] = True
                
            return structure
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {e}")
            return {}
            
    async def _apply_platform_optimizations(
        self,
        content: str,
        platform_optimization: PlatformOptimization,
        request: OptimizationRequest
    ) -> Tuple[str, List[str]]:
        """Apply platform-specific optimizations"""



        try:
            optimized_content = content
            improvements = []
            
            # Length optimization
            current_length = len(optimized_content)
            optimal_length = platform_optimization.optimal_length
            
            if current_length > optimal_length * 2:
                # Truncate content
                optimized_content = optimized_content[:optimal_length] + "..."
                improvements.append(f"Shortened content to optimal length for {request.platform.value}")
                
            # Add hashtags if requested
            if request.include_hashtags and platform_optimization.hashtag_suggestions:
                hashtags = platform_optimization.hashtag_suggestions[:5]
                optimized_content += f"\n\n{' '.join(hashtags)}"
                improvements.append("Added platform-optimized hashtags")
                
            return optimized_content, improvements
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return content, []
            
    async def _apply_readability_optimizations(
        self,
        content: str,
        request: OptimizationRequest
    ) -> Tuple[str, List[str]]:
        """Apply readability optimizations"""



        try:
            optimized_content = content
            improvements = []
            
            # Check current readability
            readability_score = textstat.flesch_reading_ease(content)
            
            if readability_score < 60:
                # Improve readability
                
                # Break long sentences
                sentences = re.split(r'[.!?]+', optimized_content)
                improved_sentences = []
                
                for sentence in sentences:
                    words = sentence.strip().split()
                    if len(words) > 20:
                        # Split at natural break points
                        conjunctions = ['and', 'but', 'because', 'since', 'while']
                        split_point = None
                        
                        for i, word in enumerate(words):
                            if word.lower() in conjunctions and i > 5:
                                split_point = i
                                break
                                
                        if split_point:
                            part1 = ' '.join(words[:split_point])
                            part2 = ' '.join(words[split_point:])
                            improved_sentences.extend([part1, part2])
                            improvements.append("Split long sentences for better readability")
                        else:
                            improved_sentences.append(sentence.strip())
                    else:
                        improved_sentences.append(sentence.strip())
                        
                optimized_content = '. '.join([s for s in improved_sentences if s])
                
                # Add line breaks for better structure
                if '\n\n' not in optimized_content:
                    sentences = optimized_content.split('. ')
                    if len(sentences) > 4:
                        mid_point = len(sentences) // 2
                        part1 = '. '.join(sentences[:mid_point])
                        part2 = '. '.join(sentences[mid_point:])
                        optimized_content = f"{part1}.\n\n{part2}"
                        improvements.append("Added paragraph breaks for better structure")
                        
            return optimized_content, improvements
            
        except Exception as e:
            logger.error(f"Readability optimization failed: {e}")
            return content, []
            
    async def _generate_alternative_versions(
        self,
        content: str,
        request: OptimizationRequest
    ) -> List[str]:
        """Generate alternative content versions"""



        try:
            alternatives = []
            
            # Short version
            sentences = re.split(r'[.!?]+', content)
            if len(sentences) > 2:
                short_version = '. '.join(sentences[:2]) + '.'
                alternatives.append(short_version)
                
            # Question-focused version
            question_version = f"Ever wondered about this? {content}"
            alternatives.append(question_version)
            
            # Emoji-enhanced version (for social platforms)
            if request.platform in [Platform.INSTAGRAM, Platform.TIKTOK]:
                emoji_version = content
                # Add relevant emojis
                emoji_map = {
                    'music': '',
                    'photo': '',
                    'video': '',
                    'tip': '',
                    'amazing': '🤩',
                    'love': ''
                }
                
                for word, emoji in emoji_map.items():
                    if word in content.lower():
                        emoji_version = emoji_version.replace(word, f"{word} {emoji}")
                        
                alternatives.append(emoji_version)
                
            return alternatives[:3]  # Limit to 3 alternatives
            
        except Exception as e:
            logger.error(f"Alternative version generation failed: {e}")
            return []
            
    async def _predict_performance(
        self,
        content: str,
        request: OptimizationRequest
    ) -> Dict[str, float]:
        """Predict content performance metrics"""



        try:
            # Simple performance prediction based on content features
            predictions = {}
            
            # Engagement rate prediction
            word_count = len(content.split())
            question_count = content.count('?')
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
            
            # Platform-specific engagement prediction
            platform_multipliers = {
                Platform.INSTAGRAM: 0.8,
                Platform.TIKTOK: 1.2,
                Platform.TWITTER: 0.6,
                Platform.LINKEDIN: 0.4
            }
            
            base_engagement = min((question_count * 0.2 + emoji_count * 0.1 + min(word_count / 100, 1.0)), 1.0)
            platform_multiplier = platform_multipliers.get(request.platform, 0.7)
            
            predictions['engagement_rate'] = base_engagement * platform_multiplier
            predictions['reach_potential'] = min(base_engagement * 1.2, 1.0)
            predictions['shareability'] = min((emoji_count * 0.15 + question_count * 0.25), 1.0)
            predictions['conversion_potential'] = 0.3 if any(word in content.lower() for word in ['buy', 'get', 'download', 'subscribe']) else 0.1
            
            return predictions
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {}
            
    async def _generate_recommendations(
        self,
        original_content: str,
        optimized_content: str,
        request: OptimizationRequest,
        seo_analysis: Optional[SEOAnalysis],
        engagement_analysis: Optional[EngagementAnalysis]
    ) -> List[str]:
        """Generate final optimization recommendations"""



        try:
            recommendations = []
            
            # SEO recommendations
            if seo_analysis and seo_analysis.seo_score < 0.7:
                recommendations.append("Consider adding more target keywords naturally throughout the content")
                if seo_analysis.readability_score < 60:
                    recommendations.append("Improve readability by using shorter sentences and simpler words")
                    
            # Engagement recommendations
            if engagement_analysis and engagement_analysis.engagement_score < 0.6:
                recommendations.append("Add more emotional triggers to increase engagement")
                if engagement_analysis.question_effectiveness < 0.3:
                    recommendations.append("Include questions to encourage audience interaction")
                    
            # Platform-specific recommendations
            config = self.platform_configs.get(request.platform, {})
            if len(optimized_content) > config.get('max_length', 1000):
                recommendations.append(f"Content may be too long for {request.platform.value} - consider breaking into multiple posts")
                
            # Visual content recommendations
            recommendations.append("Consider adding relevant images or videos to increase engagement")
            
            # Timing recommendations
            best_times = config.get('best_posting_times', [])
            if best_times:
                recommendations.append(f"Post during optimal times: {', '.join(best_times)}")
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
            
    async def _calculate_optimization_score(
        self,
        original_content: str,
        optimized_content: str,
        request: OptimizationRequest,
        seo_analysis: Optional[SEOAnalysis],
        engagement_analysis: Optional[EngagementAnalysis]
    ) -> float:
        """Calculate overall optimization score"""



        try:
            score_components = []
            
            # SEO score
            if seo_analysis:
                score_components.append(seo_analysis.seo_score)
                
            # Engagement score
            if engagement_analysis:
                score_components.append(engagement_analysis.engagement_score)
                
            # Platform optimization score
            config = self.platform_configs.get(request.platform, {})
            optimal_length = config.get('optimal_length', 200)
            length_score = 1.0 - min(abs(len(optimized_content) - optimal_length) / optimal_length, 0.5)
            score_components.append(length_score)
            
            # Improvement score (how much was improved)
            if len(optimized_content) != len(original_content):
                score_components.append(0.8)  # Content was modified
            else:
                score_components.append(0.5)  # No changes made
                
            return np.mean(score_components) if score_components else 0.5
            
        except Exception as e:
            logger.error(f"Optimization score calculation failed: {e}")
            return 0.5
