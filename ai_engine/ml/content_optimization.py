"""Content Optimization - Advanced AI-Powered Content Optimization Engine
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive content optimization capabilities for improving
engagement, SEO, and performance across multiple platforms and content types.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import re
import hashlib
import statistics
from collections import Counter

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """
Types of content optimization"""

    SEO = "seo"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    CONVERSION = "conversion"
    SOCIAL_MEDIA = "social_media"
    READABILITY = "readability"
    VIRAL_POTENTIAL = "viral_potential"
    BRAND_ALIGNMENT = "brand_alignment"
    QUALITY = "quality"

class ContentType(Enum):
    """Content types for optimization"""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"

class Platform(Enum):
    """Platforms for content optimization"""

    WEBSITE = "website"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    EMAIL_MARKETING = "email_marketing"
    GOOGLE_ADS = "google_ads"

@dataclass
class OptimizationMetrics:
    """Metrics for content optimization"""
    seo_score: float = 0.0
    engagement_score: float = 0.0
    readability_score: float = 0.0
    viral_potential: float = 0.0
    quality_score: float = 0.0
    accessibility_score: float = 0.0
    brand_alignment: float = 0.0
    conversion_potential: float = 0.0
    overall_score: float = 0.0
    confidence: float = 0.0

@dataclass
class OptimizationSuggestion:
    """
Individual optimization suggestion"""
    suggestion_id: str
    type: OptimizationType
    priority: str  # high, medium, low
    title: str
    description: str
    expected_impact: float  # 0.0 to 1.0
    implementation_effort: str  # easy, medium, hard
    specific_changes: List[str] = field(default_factory=list)
    rationale: str = ""
    examples: List[str] = field(default_factory=list)

@dataclass
class OptimizationResult:
    """Result of content optimization analysis"""
    content_id: str
    content_type: ContentType
    platform: Platform
    optimization_type: OptimizationType
    metrics: OptimizationMetrics
    suggestions: List[OptimizationSuggestion] = field(default_factory=list)
    optimized_content: Optional[str] = None
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SEOAnalysis:
    """
SEO-specific analysis results"""
    title_optimization: Dict[str, Any] = field(default_factory=dict)
    meta_description: Dict[str, Any] = field(default_factory=dict)
    headings_structure: Dict[str, Any] = field(default_factory=dict)
    keyword_density: Dict[str, float] = field(default_factory=dict)
    internal_links: int = 0
    external_links: int = 0
    image_alt_texts: int = 0
    content_length: int = 0
    reading_time: float = 0.0
    schema_markup: bool = False
    mobile_friendly: bool = True

class ContentOptimizer:
    """
Main content optimization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.optimization_history = []
        self.platform_guidelines = self._load_platform_guidelines()
        self.seo_keywords_db = {}
        self.engagement_patterns = {}
        self.brand_voice_patterns = {}
        self._init_optimization_models()
        self.logger.info("ContentOptimizer initialized successfully")
    
    def _load_platform_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific optimization guidelines"""
        return {
            Platform.INSTAGRAM.value: {
                "caption_length": {"optimal": 125, "max": 2200},
                "hashtags": {"optimal": 11, "max": 30},
                "posting_times": ["9:00", "11:00", "13:00", "15:00", "17:00", "19:00"],
                "engagement_factors": ["visual_appeal", "storytelling", "hashtags", "timing"],
                "content_types": ["photo", "video", "reel", "story", "igtv"],
                "aspect_ratios": {"post": "1:1", "story": "9:16", "reel": "9:16"},
                "video_length": {"feed": 60, "reel": 90, "story": 15}
            },
            Platform.FACEBOOK.value: {
                "post_length": {"optimal": 40, "max": 63206},
                "video_length": {"optimal": 60, "max": 240},
                "image_text": {"max_percentage": 20},
                "posting_times": ["9:00", "13:00", "15:00"],
                "engagement_factors": ["visual_content", "questions", "emotions", "timing"]
            },
            Platform.TWITTER.value: {
                "character_limit": 280,
                "hashtags": {"optimal": 2, "max": 2},
                "posting_times": ["8:00", "12:00", "17:00", "19:00"],
                "engagement_factors": ["trending_topics", "timing", "conversations", "visuals"],
                "thread_optimization": True
            },
            Platform.LINKEDIN.value: {
                "post_length": {"optimal": 150, "max": 3000},
                "article_length": {"optimal": 1900, "max": 125000},
                "hashtags": {"optimal": 5, "max": 5},
                "posting_times": ["8:00", "12:00", "17:00", "18:00"],
                "engagement_factors": ["professional_value", "industry_insights", "networking"]
            },
            Platform.YOUTUBE.value: {
                "title_length": {"optimal": 60, "max": 100},
                "description_length": {"optimal": 125, "max": 1000},
                "tags": {"optimal": 10, "max": 15},
                "video_length": {"optimal": 600, "max": 3600},
                "thumbnail_importance": "critical",
                "engagement_factors": ["thumbnail", "title", "first_15_seconds", "retention"]
            },
            Platform.TIKTOK.value: {
                "video_length": {"optimal": 15, "max": 60},
                "caption_length": {"optimal": 100, "max": 150},
                "hashtags": {"optimal": 5, "max": 5},
                "posting_times": ["6:00", "10:00", "12:00", "16:00", "19:00", "20:00"],
                "engagement_factors": ["trending_sounds", "challenges", "timing", "hook"]
            }
        }
    
    def _init_optimization_models(self):
        """Initialize optimization models and patterns"""
        # Engagement prediction patterns
        self.engagement_patterns = {
            "high_engagement_words": [
                "amazing", "incredible", "secret", "exclusive", "limited",
                "free", "new", "discover", "learn", "transform", "ultimate"
            ],
            "emotional_triggers": [
                "love", "hate", "fear", "joy", "surprise", "trust",
                "anticipation", "disgust", "anger", "sadness"
            ],
            "call_to_action": [
                "click", "share", "comment", "subscribe", "follow",
                "like", "save", "download", "register", "buy"
            ],
            "question_starters": [
                "how", "what", "why", "when", "where", "which",
                "can you", "do you", "have you", "would you"
            ]
        }
        
        # SEO optimization patterns
        self.seo_patterns = {
            "title_templates": [
                "How to {action} in {timeframe}",
                "The Ultimate Guide to {topic}",
                "{number} Ways to {achieve_goal}",
                "Why {statement} (And What to Do About It)",
                "The Complete {topic} Checklist"
            ],
            "meta_description_templates": [
                "Learn {topic} with our comprehensive guide. Discover {benefit} and {outcome}.",
                "Get {result} with these {number} proven strategies for {topic}.",
                "{Action} like a pro! Complete guide to {topic} with {benefit}."
            ]
        }
    
    def optimize_content(self, content: str, content_type: ContentType, 
                        platform: Platform, optimization_type: OptimizationType = OptimizationType.ENGAGEMENT,
                        target_keywords: Optional[List[str]] = None,
                        target_audience: Optional[str] = None) -> OptimizationResult:
        """Main content optimization function"""
        try:
            start_time = datetime.utcnow()
            content_id = hashlib.md5(content.encode()).hexdigest()[:12]
            
            self.logger.info(f"Optimizing content {content_id} for {platform.value}")
            
            # Analyze current content
            current_metrics = self._analyze_content_metrics(content, content_type, platform)
            
            # Generate optimization suggestions
            suggestions = self._generate_optimization_suggestions(
                content, content_type, platform, optimization_type, 
                target_keywords, target_audience, current_metrics
            )
            
            # Generate optimized content if requested
            optimized_content = None
            if optimization_type in [OptimizationType.ENGAGEMENT, OptimizationType.SEO]:
                optimized_content = self._generate_optimized_content(
                    content, suggestions, content_type, platform
                )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = OptimizationResult(
                content_id=content_id,
                content_type=content_type,
                platform=platform,
                optimization_type=optimization_type,
                metrics=current_metrics,
                suggestions=suggestions,
                optimized_content=optimized_content,
                processing_time=processing_time,
                metadata={
                    "target_keywords": target_keywords,
                    "target_audience": target_audience,
                    "original_length": len(content)
                }
            )
            
            # Store in history
            self.optimization_history.append(result)
            
            self.logger.info(f"Content optimization completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
            raise
    
    def _analyze_content_metrics(self, content: str, content_type: ContentType, 
                                platform: Platform) -> OptimizationMetrics:
        """Analyze current content metrics"""
        try:
            # SEO Analysis
            seo_score = self._calculate_seo_score(content, content_type)
            
            # Engagement Analysis
            engagement_score = self._calculate_engagement_score(content, platform)
            
            # Readability Analysis
            readability_score = self._calculate_readability_score(content)
            
            # Viral Potential Analysis
            viral_potential = self._calculate_viral_potential(content, platform)
            
            # Quality Analysis
            quality_score = self._calculate_quality_score(content, content_type)
            
            # Accessibility Analysis
            accessibility_score = self._calculate_accessibility_score(content, content_type)
            
            # Brand Alignment Analysis
            brand_alignment = self._calculate_brand_alignment(content)
            
            # Conversion Potential Analysis
            conversion_potential = self._calculate_conversion_potential(content, content_type)
            
            # Overall Score
            scores = [seo_score, engagement_score, readability_score, viral_potential, 
                     quality_score, accessibility_score, brand_alignment, conversion_potential]
            overall_score = statistics.mean([s for s in scores if s > 0])
            
            # Confidence based on content length and complexity
            confidence = min(0.95, 0.5 + (len(content) / 2000) * 0.45)
            
            return OptimizationMetrics(
                seo_score=seo_score,
                engagement_score=engagement_score,
                readability_score=readability_score,
                viral_potential=viral_potential,
                quality_score=quality_score,
                accessibility_score=accessibility_score,
                brand_alignment=brand_alignment,
                conversion_potential=conversion_potential,
                overall_score=overall_score,
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content metrics: {e}")
            # Return default metrics
            return OptimizationMetrics()
    
    def _calculate_seo_score(self, content: str, content_type: ContentType) -> float:
        """Calculate SEO optimization score"""
        score = 0.0
        factors = 0
        
        # Content length (optimal 300-2000 words for blog posts)
        word_count = len(content.split())
        if content_type == ContentType.BLOG_POST:
            if 300 <= word_count <= 2000:
                score += 20
            elif word_count < 300:
                score += (word_count / 300) * 20
            else:
                score += 20 - ((word_count - 2000) / 1000) * 5
        factors += 1
        
        # Keyword density (should be 1-3%)
        # Simplified: check for repeated important words
        words = content.lower().split()
        word_freq = Counter(words)
        most_common = word_freq.most_common(5)
        if most_common:
            top_density = most_common[0][1] / len(words)
            if 0.01 <= top_density <= 0.03:
                score += 15
            else:
                score += max(0, 15 - abs(top_density - 0.02) * 500)
        factors += 1
        
        # Headers structure (check for structured content)
        header_patterns = [r'#\s+', r'##\s+', r'###\s+', r'\n[A-Z][^.!?]*\n']
        header_count = sum(len(re.findall(pattern, content)) for pattern in header_patterns)
        if header_count > 0:
            score += min(15, header_count * 3)
        factors += 1
        
        # Internal/external links
        link_patterns = [r'http[s]?://\S+', r'\[.*?\]\(.*?\)', r'<a\s+href']
        link_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in link_patterns)
        if link_count > 0:
            score += min(10, link_count * 2)
        factors += 1
        
        # Meta information presence (simplified)
        if any(keyword in content.lower() for keyword in ['title:', 'description:', 'keywords:']):
            score += 10
        factors += 1
        
        return min(100.0, score)
    
    def _calculate_engagement_score(self, content: str, platform: Platform) -> float:
        """
Calculate engagement potential score"""
        score = 0.0
        content_lower = content.lower()
        
        # High-engagement words
        engagement_word_count = sum(1 for word in self.engagement_patterns["high_engagement_words"] 
                                   if word in content_lower)
        score += min(20, engagement_word_count * 3)
        
        # Emotional triggers
        emotional_word_count = sum(1 for word in self.engagement_patterns["emotional_triggers"] 
                                  if word in content_lower)
        score += min(15, emotional_word_count * 2)
        
        # Call-to-action presence
        cta_count = sum(1 for cta in self.engagement_patterns["call_to_action"] 
                       if cta in content_lower)
        score += min(15, cta_count * 3)
        
        # Questions (engagement boosters)
        question_count = content.count('?')
        question_starters = sum(1 for starter in self.engagement_patterns["question_starters"] 
                               if starter in content_lower)
        score += min(15, (question_count + question_starters) * 2)
        
        # Platform-specific optimization
        guidelines = self.platform_guidelines.get(platform.value, {})
        if guidelines:
            # Length optimization
            if 'caption_length' in guidelines:
                optimal_length = guidelines['caption_length']['optimal']
                length_score = max(0, 10 - abs(len(content) - optimal_length) / optimal_length * 10)
                score += length_score
            
            # Hashtag presence (for social platforms)
            if 'hashtags' in guidelines:
                hashtag_count = content.count('#')
                optimal_hashtags = guidelines['hashtags']['optimal']
                if hashtag_count > 0:
                    hashtag_score = max(0, 10 - abs(hashtag_count - optimal_hashtags))
                    score += hashtag_score
        
        # Visual content indicators
        visual_indicators = ['image', 'photo', 'video', 'watch', 'see', 'look']
        visual_count = sum(1 for indicator in visual_indicators if indicator in content_lower)
        score += min(10, visual_count * 2)
        
        # Personal pronouns (creates connection)
        personal_pronouns = ['you', 'your', 'we', 'our', 'i', 'my']
        pronoun_count = sum(content_lower.count(pronoun) for pronoun in personal_pronouns)
        score += min(10, pronoun_count)
        
        return min(100.0, score)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (simplified Flesch-like algorithm)"""
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences == 0:
            sentences = 1
        
        words = len(content.split())
        if words == 0:
            return 0.0
        
        # Average sentence length
        avg_sentence_length = words / sentences
        
        # Syllable count approximation (vowel groups)
        syllables = sum(1 for char in content.lower() if char in 'aeiou')
        avg_syllables_per_word = syllables / words if words > 0 else 0
        
        # Simplified Flesch Reading Ease
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Convert to 0-100 scale where higher is better
        readability = max(0, min(100, flesch_score))
        
        # Bonus for shorter paragraphs
        paragraph_count = content.count('\n\n') + 1
        if paragraph_count > 1:
            avg_paragraph_length = words / paragraph_count
            if avg_paragraph_length < 100:  # Short paragraphs are better for readability
                readability += min(10, (100 - avg_paragraph_length) / 10)
        
        return min(100.0, readability)
    
    def _calculate_viral_potential(self, content: str, platform: Platform) -> float:
        """
Calculate viral potential score"""
        score = 0.0
        content_lower = content.lower()
        
        # Trending/viral keywords
        viral_keywords = [
            'trending', 'viral', 'challenge', 'hack', 'secret', 'exposed',
            'shocking', 'unbelievable', 'must-see', 'gone wrong', 'reaction'
        ]
        viral_word_count = sum(1 for word in viral_keywords if word in content_lower)
        score += min(25, viral_word_count * 5)
        
        # Shareability factors
        shareable_phrases = [
            'share if', 'tag a friend', 'repost', 'spread the word',
            'tell everyone', 'pass it on', 'share this'
        ]
        shareable_count = sum(1 for phrase in shareable_phrases if phrase in content_lower)
        score += min(20, shareable_count * 10)
        
        # Controversy/opinion indicators
        opinion_words = [
            'controversial', 'unpopular opinion', 'hot take', 'debate',
            'disagree', 'argument', 'polarizing'
        ]
        opinion_count = sum(1 for word in opinion_words if word in content_lower)
        score += min(15, opinion_count * 8)
        
        # Timeliness/urgency
        urgency_words = [
            'now', 'today', 'urgent', 'breaking', 'just happened',
            'live', 'currently', 'right now', 'immediate'
        ]
        urgency_count = sum(1 for word in urgency_words if word in content_lower)
        score += min(15, urgency_count * 3)
        
        # Platform-specific viral factors
        if platform == Platform.TIKTOK:
            tiktok_viral = ['dance', 'challenge', 'duet', 'trend', 'fyp']
            tiktok_count = sum(1 for word in tiktok_viral if word in content_lower)
            score += min(15, tiktok_count * 5)
        elif platform == Platform.TWITTER:
            twitter_viral = ['thread', 'ratio', 'retweet', 'trending']
            twitter_count = sum(1 for word in twitter_viral if word in content_lower)
            score += min(10, twitter_count * 3)
        
        # Emotional intensity
        intense_words = [
            'amazing', 'incredible', 'unbelievable', 'shocking', 'mind-blowing',
            'life-changing', 'revolutionary', 'groundbreaking'
        ]
        intense_count = sum(1 for word in intense_words if word in content_lower)
        score += min(10, intense_count * 2)
        
        return min(100.0, score)
    
    def _calculate_quality_score(self, content: str, content_type: ContentType) -> float:
        """
Calculate content quality score"""
        score = 0.0
        
        # Content length appropriateness
        word_count = len(content.split())
        if content_type == ContentType.BLOG_POST:
            if 800 <= word_count <= 2500:
                score += 20
            else:
                score += max(5, 20 - abs(word_count - 1500) / 100)
        elif content_type == ContentType.SOCIAL_POST:
            if 20 <= word_count <= 150:
                score += 20
            else:
                score += max(5, 20 - abs(word_count - 85) / 10)
        
        # Grammar and spelling (simplified check)
        # Check for common errors
        grammar_issues = 0
        grammar_issues += content.count(' i ') - content.count(' I ')  # Capitalization
        grammar_issues += len(re.findall(r'\s+([.!?])', content))  # Spacing before punctuation
        grammar_issues += len(re.findall(r'([.!?])[a-z]', content))  # Missing space after punctuation
        
        grammar_score = max(0, 15 - grammar_issues)
        score += grammar_score
        
        # Sentence variety
        sentences = re.split(r'[.!?]+', content)
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variety = len(set(sentence_lengths)) / len(sentence_lengths)
                score += length_variety * 15
        
        # Vocabulary richness
        words = content.lower().split()
        if words:
            unique_words = len(set(words))
            vocab_richness = unique_words / len(words)
            score += vocab_richness * 20
        
        # Structure and formatting
        structure_score = 0
        if '\n' in content:  # Paragraphs
            structure_score += 5
        if any(marker in content for marker in ['•', '-', '1.', '2.']):  # Lists
            structure_score += 5
        if re.search(r'[A-Z][^.!?]*:', content):  # Headings/sections
            structure_score += 5
        score += structure_score
        
        # Professional tone indicators
        professional_words = [
            'professional', 'expert', 'experience', 'proven', 'effective',
            'comprehensive', 'detailed', 'thorough', 'analysis', 'research'
        ]
        prof_count = sum(1 for word in professional_words if word in content.lower())
        score += min(10, prof_count * 2)
        
        # Factual content indicators
        factual_indicators = [
            'according to', 'research shows', 'studies indicate', 'data reveals',
            'statistics', 'evidence', 'source:', 'references'
        ]
        factual_count = sum(1 for indicator in factual_indicators if indicator in content.lower())
        score += min(10, factual_count * 3)
        
        return min(100.0, score)
    
    def _calculate_accessibility_score(self, content: str, content_type: ContentType) -> float:
        """
Calculate accessibility score"""
        score = 0.0
        
        # Simple language usage
        complex_words = [
            'utilize', 'demonstrate', 'facilitate', 'consequently', 'furthermore',
            'nevertheless', 'subsequently', 'approximately', 'significantly'
        ]
        simple_alternatives = [
            'use', 'show', 'help', 'so', 'also',
            'but', 'then', 'about', 'very'
        ]
        
        complex_count = sum(1 for word in complex_words if word in content.lower())
        simple_count = sum(1 for word in simple_alternatives if word in content.lower())
        
        if complex_count + simple_count > 0:
            simplicity_ratio = simple_count / (complex_count + simple_count)
            score += simplicity_ratio * 30
        else:
            score += 15  # Neutral score if no indicators found
        
        # Short sentences (accessibility-friendly)
        sentences = re.split(r'[.!?]+', content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            avg_length = statistics.mean(sentence_lengths)
            if avg_length <= 20:  # Recommended max for accessibility
                score += 25
            else:
                score += max(0, 25 - (avg_length - 20) * 2)
        
        # Clear structure
        if content.count('\n') > 0:  # Paragraphs
            score += 10
        
        # Descriptive text (for images/media)
        descriptive_patterns = [
            r'alt[\s=]', r'description:', r'caption:', r'shows?', r'depicts?'
        ]
        desc_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in descriptive_patterns)
        if desc_count > 0:
            score += min(15, desc_count * 5)
        
        # Inclusive language
        inclusive_words = [
            'everyone', 'all people', 'accessible', 'inclusive', 'diverse',
            'everyone can', 'people with', 'community'
        ]
        inclusive_count = sum(1 for word in inclusive_words if word in content.lower())
        score += min(10, inclusive_count * 2)
        
        # Avoiding barriers
        barrier_words = [
            'obviously', 'clearly', 'simply', 'just', 'easily',
            'everyone knows', 'common sense'
        ]
        barrier_count = sum(1 for word in barrier_words if word in content.lower())
        score -= min(10, barrier_count * 2)
        
        return max(0.0, min(100.0, score))
    
    def _calculate_brand_alignment(self, content: str) -> float:
        """
Calculate brand alignment score (simplified)"""
        score = 50.0  # Neutral starting point
        
        # Professional tone indicators
        professional_indicators = [
            'professional', 'quality', 'excellence', 'expertise', 'innovative',
            'reliable', 'trusted', 'leading', 'premium', 'advanced'
        ]
        prof_count = sum(1 for word in professional_indicators if word in content.lower())
        score += min(25, prof_count * 3)
        
        # Consistent messaging
        if any(word in content.lower() for word in ['brand', 'mission', 'values', 'vision']):
            score += 15
        
        # Inappropriate content check
        inappropriate_words = [
            'spam', 'scam', 'fake', 'illegal', 'inappropriate', 'offensive'
        ]
        inappropriate_count = sum(1 for word in inappropriate_words if word in content.lower())
        score -= inappropriate_count * 10
        
        return max(0.0, min(100.0, score))
    
    def _calculate_conversion_potential(self, content: str, content_type: ContentType) -> float:
        """
Calculate conversion potential score"""
        score = 0.0
        content_lower = content.lower()
        
        # Clear call-to-action
        strong_ctas = [
            'buy now', 'sign up', 'subscribe', 'download', 'register',
            'get started', 'learn more', 'contact us', 'book now'
        ]
        cta_count = sum(1 for cta in strong_ctas if cta in content_lower)
        score += min(25, cta_count * 8)
        
        # Value proposition
        value_words = [
            'free', 'discount', 'save', 'bonus', 'exclusive', 'limited',
            'special offer', 'guarantee', 'results', 'benefits'
        ]
        value_count = sum(1 for word in value_words if word in content_lower)
        score += min(20, value_count * 3)
        
        # Urgency/scarcity
        urgency_phrases = [
            'limited time', 'act now', 'while supplies last', 'expires soon',
            'only today', 'last chance', 'hurry'
        ]
        urgency_count = sum(1 for phrase in urgency_phrases if phrase in content_lower)
        score += min(15, urgency_count * 5)
        
        # Social proof
        social_proof_words = [
            'customers love', 'testimonial', 'review', 'rating', 'satisfied',
            'thousands of', 'popular', 'bestseller', 'award'
        ]
        social_count = sum(1 for word in social_proof_words if word in content_lower)
        score += min(15, social_count * 3)
        
        # Trust signals
        trust_words = [
            'secure', 'guaranteed', 'certified', 'licensed', 'verified',
            'money back', 'risk-free', 'privacy', 'safe'
        ]
        trust_count = sum(1 for word in trust_words if word in content_lower)
        score += min(15, trust_count * 3)
        
        # Contact information
        contact_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'https?://\S+'  # URLs
        ]
        contact_count = sum(len(re.findall(pattern, content)) for pattern in contact_patterns)
        if contact_count > 0:
            score += min(10, contact_count * 3)
        
        return min(100.0, score)
    
    def _generate_optimization_suggestions(self, content: str, content_type: ContentType,
                                         platform: Platform, optimization_type: OptimizationType,
                                         target_keywords: Optional[List[str]],
                                         target_audience: Optional[str],
                                         current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """
Generate specific optimization suggestions"""
        suggestions = []
        
        try:
            # SEO Suggestions
            if optimization_type in [OptimizationType.SEO, OptimizationType.PERFORMANCE]:
                suggestions.extend(self._generate_seo_suggestions(
                    content, content_type, target_keywords, current_metrics
                ))
            
            # Engagement Suggestions
            if optimization_type in [OptimizationType.ENGAGEMENT, OptimizationType.SOCIAL_MEDIA]:
                suggestions.extend(self._generate_engagement_suggestions(
                    content, platform, current_metrics
                ))
            
            # Readability Suggestions
            if optimization_type in [OptimizationType.READABILITY, OptimizationType.ACCESSIBILITY]:
                suggestions.extend(self._generate_readability_suggestions(
                    content, current_metrics
                ))
            
            # Quality Suggestions
            if optimization_type == OptimizationType.QUALITY:
                suggestions.extend(self._generate_quality_suggestions(
                    content, content_type, current_metrics
                ))
            
            # Platform-specific suggestions
            suggestions.extend(self._generate_platform_suggestions(
                content, platform, current_metrics
            ))
            
            # Sort by priority and expected impact
            suggestions.sort(key=lambda x: (
                0 if x.priority == "high" else 1 if x.priority == "medium" else 2,
                -x.expected_impact
            ))
            
            return suggestions[:15]  # Return top 15 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization suggestions: {e}")
            return []
    
    def _generate_seo_suggestions(self, content: str, content_type: ContentType,
                                target_keywords: Optional[List[str]],
                                current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """Generate SEO-specific suggestions"""
        suggestions = []
        word_count = len(content.split())
        
        # Content length optimization
        if content_type == ContentType.BLOG_POST and word_count < 300:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="seo_length_01",
                type=OptimizationType.SEO,
                priority="high",
                title="Increase Content Length",
                description=f"Your content is {word_count} words. Aim for 300+ words for better SEO ranking.",
                expected_impact=0.8,
                implementation_effort="medium",
                specific_changes=[
                    "Add more detailed explanations",
                    "Include examples and case studies",
                    "Expand on key points"
                ],
                rationale="Longer content typically ranks better in search engines"
            ))
        
        # Keyword optimization
        if target_keywords:
            for keyword in target_keywords[:3]:
                if keyword.lower() not in content.lower():
                    suggestions.append(OptimizationSuggestion(
                        suggestion_id=f"seo_keyword_{hash(keyword) % 1000}",
                        type=OptimizationType.SEO,
                        priority="high",
                        title=f"Include Target Keyword: {keyword}",
                        description=f"The target keyword '{keyword}' is missing from your content.",
                        expected_impact=0.9,
                        implementation_effort="easy",
                        specific_changes=[
                            f"Include '{keyword}' in the title",
                            f"Use '{keyword}' in the first paragraph",
                            f"Naturally integrate '{keyword}' throughout the content"
                        ]
                    ))
        
        # Header structure
        header_count = len(re.findall(r'#\s+|##\s+|###\s+', content))
        if header_count == 0 and word_count > 200:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="seo_headers_01",
                type=OptimizationType.SEO,
                priority="medium",
                title="Add Header Structure",
                description="Add headers (H1, H2, H3) to improve content structure and SEO.",
                expected_impact=0.6,
                implementation_effort="easy",
                specific_changes=[
                    "Add main heading (H1)",
                    "Create section headers (H2)",
                    "Use sub-headers (H3) for detailed points"
                ]
            ))
        
        return suggestions
    
    def _generate_engagement_suggestions(self, content: str, platform: Platform,
                                       current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """Generate engagement-focused suggestions"""
        suggestions = []
        content_lower = content.lower()
        
        # Call-to-action optimization
        cta_count = sum(1 for cta in self.engagement_patterns["call_to_action"] 
                       if cta in content_lower)
        if cta_count == 0:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="eng_cta_01",
                type=OptimizationType.ENGAGEMENT,
                priority="high",
                title="Add Call-to-Action",
                description="Include a clear call-to-action to encourage user engagement.",
                expected_impact=0.8,
                implementation_effort="easy",
                specific_changes=[
                    "Add 'What do you think?' at the end",
                    "Include 'Share your experience in the comments'",
                    "Ask users to 'Like if you agree'"
                ]
            ))
        
        # Question optimization
        question_count = content.count('?')
        if question_count == 0:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="eng_questions_01",
                type=OptimizationType.ENGAGEMENT,
                priority="medium",
                title="Add Engaging Questions",
                description="Questions increase engagement by encouraging responses.",
                expected_impact=0.7,
                implementation_effort="easy",
                specific_changes=[
                    "Start with an intriguing question",
                    "End with a discussion question",
                    "Include rhetorical questions throughout"
                ]
            ))
        
        # Platform-specific engagement
        guidelines = self.platform_guidelines.get(platform.value, {})
        if platform == Platform.INSTAGRAM and guidelines:
            hashtag_count = content.count('#')
            optimal_hashtags = guidelines['hashtags']['optimal']
            if hashtag_count < optimal_hashtags:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id="eng_hashtags_01",
                    type=OptimizationType.ENGAGEMENT,
                    priority="high",
                    title="Optimize Hashtags",
                    description=f"Add more hashtags (current: {hashtag_count}, optimal: {optimal_hashtags}).",
                    expected_impact=0.6,
                    implementation_effort="easy",
                    specific_changes=[
                        "Add relevant industry hashtags",
                        "Include trending hashtags",
                        "Use location-based hashtags"
                    ]
                ))
        
        return suggestions
    
    def _generate_readability_suggestions(self, content: str, 
                                        current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """Generate readability improvement suggestions"""
        suggestions = []
        
        # Sentence length analysis
        sentences = re.split(r'[.!?]+', content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            avg_length = statistics.mean(sentence_lengths)
            if avg_length > 25:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id="read_sentence_01",
                    type=OptimizationType.READABILITY,
                    priority="medium",
                    title="Shorten Sentences",
                    description=f"Average sentence length is {avg_length:.1f} words. Aim for under 20.",
                    expected_impact=0.6,
                    implementation_effort="medium",
                    specific_changes=[
                        "Break long sentences into shorter ones",
                        "Use periods instead of commas where appropriate",
                        "Simplify complex sentence structures"
                    ]
                ))
        
        # Paragraph length
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 150]
        if long_paragraphs:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="read_paragraphs_01",
                type=OptimizationType.READABILITY,
                priority="medium",
                title="Break Up Long Paragraphs",
                description=f"Found {len(long_paragraphs)} paragraphs over 150 words.",
                expected_impact=0.5,
                implementation_effort="easy",
                specific_changes=[
                    "Split long paragraphs at natural break points",
                    "Aim for 3-5 sentences per paragraph",
                    "Use bullet points for lists"
                ]
            ))
        
        return suggestions
    
    def _generate_quality_suggestions(self, content: str, content_type: ContentType,
                                    current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """Generate quality improvement suggestions"""
        suggestions = []
        
        # Grammar and spelling checks (simplified)
        grammar_issues = content.count(' i ') - content.count(' I ')
        if grammar_issues > 0:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="quality_grammar_01",
                type=OptimizationType.QUALITY,
                priority="high",
                title="Fix Capitalization Issues",
                description=f"Found {grammar_issues} capitalization errors with 'I'.",
                expected_impact=0.3,
                implementation_effort="easy",
                specific_changes=[
                    "Capitalize standalone 'I' pronoun",
                    "Review other capitalization rules",
                    "Use grammar checking tools"
                ]
            ))
        
        # Vocabulary richness
        words = content.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.6:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id="quality_vocab_01",
                    type=OptimizationType.QUALITY,
                    priority="medium",
                    title="Improve Vocabulary Variety",
                    description=f"Only {unique_ratio:.1%} of words are unique. Add more variety.",
                    expected_impact=0.4,
                    implementation_effort="medium",
                    specific_changes=[
                        "Use synonyms to avoid repetition",
                        "Vary sentence structures",
                        "Replace common words with more specific alternatives"
                    ]
                ))
        
        return suggestions
    
    def _generate_platform_suggestions(self, content: str, platform: Platform,
                                     current_metrics: OptimizationMetrics) -> List[OptimizationSuggestion]:
        """Generate platform-specific suggestions"""
        suggestions = []
        guidelines = self.platform_guidelines.get(platform.value, {})
        
        if not guidelines:
            return suggestions
        
        # Length optimization
        if 'caption_length' in guidelines:
            optimal_length = guidelines['caption_length']['optimal']
            max_length = guidelines['caption_length']['max']
            current_length = len(content)
            
            if current_length > max_length:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"platform_{platform.value}_length_01",
                    type=OptimizationType.SOCIAL_MEDIA,
                    priority="high",
                    title=f"Reduce Content Length for {platform.value.title()}",
                    description=f"Content is {current_length} chars, max is {max_length}.",
                    expected_impact=0.9,
                    implementation_effort="medium",
                    specific_changes=[
                        "Cut unnecessary words",
                        "Use more concise language",
                        "Focus on key message"
                    ]
                ))
            elif abs(current_length - optimal_length) > optimal_length * 0.5:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"platform_{platform.value}_length_02",
                    type=OptimizationType.SOCIAL_MEDIA,
                    priority="medium",
                    title=f"Optimize Length for {platform.value.title()}",
                    description=f"Optimal length is {optimal_length} chars, current is {current_length}.",
                    expected_impact=0.5,
                    implementation_effort="easy",
                    specific_changes=[
                        f"Aim for around {optimal_length} characters",
                        "Adjust content to platform preferences"
                    ]
                ))
        
        return suggestions
    
    def _generate_optimized_content(self, original_content: str, 
                                  suggestions: List[OptimizationSuggestion],
                                  content_type: ContentType, 
                                  platform: Platform) -> str:
        """Generate optimized version of content based on suggestions"""
        try:
            optimized = original_content
            
            # Apply high-priority suggestions
            high_priority = [s for s in suggestions if s.priority == "high"]
            
            for suggestion in high_priority[:5]:  # Apply top 5 high-priority suggestions
                if suggestion.type == OptimizationType.ENGAGEMENT:
                    if "Add Call-to-Action" in suggestion.title:
                        optimized += "\n\nWhat are your thoughts? Share in the comments below!"
                    elif "Add Engaging Questions" in suggestion.title:
                        optimized = "Have you ever wondered about this? " + optimized
                
                elif suggestion.type == OptimizationType.SEO:
                    if "Include Target Keyword" in suggestion.title:
                        # Extract keyword from suggestion
                        keyword_match = re.search(r"keyword: (.+)", suggestion.description.lower())
                        if keyword_match:
                            keyword = keyword_match.group(1)
                            # Add keyword to beginning if not present
                            if keyword.lower() not in optimized.lower():
                                optimized = f"{keyword.title()}: " + optimized
                
                elif suggestion.type == OptimizationType.SOCIAL_MEDIA:
                    if platform == Platform.INSTAGRAM and "hashtags" in suggestion.title.lower():
                        # Add relevant hashtags
                        hashtags = "\n\n#content #socialmedia #engagement #marketing #digitalmarketing"
                        if hashtags not in optimized:
                            optimized += hashtags
            
            return optimized.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimized content: {e}")
            return original_content
    
    def analyze_seo_details(self, content: str, target_keywords: Optional[List[str]] = None) -> SEOAnalysis:
        """Perform detailed SEO analysis"""
        try:
            analysis = SEOAnalysis()
            
            # Title analysis
            title_match = re.search(r'^#\s+(.+)$|^(.+)\n', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1) or title_match.group(2)
                analysis.title_optimization = {
                    "title": title,
                    "length": len(title),
                    "optimal_range": "50-60 characters",
                    "score": min(100, max(0, 100 - abs(len(title) - 55) * 2))
                }
            
            # Meta description (look for description patterns)
            desc_pattern = r'(?i)description:\s*(.+?)(?:\n|$)'
            desc_match = re.search(desc_pattern, content)
            if desc_match:
                desc = desc_match.group(1)
                analysis.meta_description = {
                    "description": desc,
                    "length": len(desc),
                    "optimal_range": "150-160 characters",
                    "score": min(100, max(0, 100 - abs(len(desc) - 155) * 2))
                }
            
            # Headings structure
            h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
            h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
            h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
            
            analysis.headings_structure = {
                "h1_count": h1_count,
                "h2_count": h2_count,
                "h3_count": h3_count,
                "proper_hierarchy": h1_count == 1 and h2_count > 0,
                "score": 50 + (25 if h1_count == 1 else 0) + (25 if h2_count > 0 else 0)
            }
            
            # Keyword density
            if target_keywords:
                words = content.lower().split()
                total_words = len(words)
                for keyword in target_keywords:
                    keyword_count = content.lower().count(keyword.lower())
                    density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                    analysis.keyword_density[keyword] = density
            
            # Links analysis
            external_links = len(re.findall(r'https?://(?!(?:www\.)?yourdomain\.com)\S+', content))
            internal_links = len(re.findall(r'https?://(?:www\.)?yourdomain\.com\S*', content))
            markdown_links = len(re.findall(r'\[.*?\]\(.*?\)', content))
            
            analysis.external_links = external_links
            analysis.internal_links = internal_links + markdown_links
            
            # Content metrics
            analysis.content_length = len(content.split())
            analysis.reading_time = analysis.content_length / 200  # Average reading speed
            
            # Image alt text check (simplified)
            alt_text_pattern = r'alt\s*=\s*["\']([^"\']+)["\']|!\[[^\]]*\]'
            analysis.image_alt_texts = len(re.findall(alt_text_pattern, content, re.IGNORECASE))
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}")
            return SEOAnalysis()
    
    def get_optimization_history(self, limit: int = 10) -> List[OptimizationResult]:
        """Get recent optimization history"""
        return self.optimization_history[-limit:]
    
    def get_platform_guidelines(self, platform: Platform) -> Dict[str, Any]:
        """
Get optimization guidelines for specific platform"""
        return self.platform_guidelines.get(platform.value, {})

# Export main classes
__all__ = [
    'ContentOptimizer',
    'OptimizationResult',
    'OptimizationSuggestion',
    'OptimizationMetrics',
    'SEOAnalysis',
    'OptimizationType',
    'ContentType',
    'Platform'
]

logger.info("Content optimization module loaded successfully")
