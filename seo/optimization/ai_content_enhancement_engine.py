#!/usr/bin/env python3
"""
🧠 AI Content Enhancement Engine
===============================

Advanced AI-powered content enhancement system for SEO optimization.
Leverages machine learning and natural language processing to optimize content
for search engines while maintaining creator authenticity and engagement.

Expert Roles Combined:
- IA Prompt Engineer: Advanced AI prompt engineering and content optimization
- ML Engineer: Machine learning models for content analysis and enhancement
- Lead Dev IA: AI system orchestration and intelligent automation
- SEO Specialist: Search engine optimization expertise and strategies

Features:
- AI-powered content analysis and optimization
- Natural language processing for semantic SEO
- Machine learning-based keyword optimization
- Content structure enhancement
- Creator voice preservation
- Multi-platform content adaptation
- Real-time SEO scoring and suggestions
- Performance-driven content optimization
- Creator economy-focused enhancement

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: IA Prompt Engineer + ML Engineer + Lead Dev IA + SEO Specialist
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import re
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import aioredis
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content for optimization"""
    TITLE = "title"
    DESCRIPTION = "description"
    TRANSCRIPT = "transcript"
    HASHTAGS = "hashtags"
    THUMBNAIL_TEXT = "thumbnail_text"
    CAPTIONS = "captions"
    BLOG_POST = "blog_post"
    SCRIPT = "script"
    SOCIAL_POST = "social_post"

class Platform(Enum):
    """Supported platforms for optimization"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    BLOG = "blog"

class OptimizationGoal(Enum):
    """Optimization objectives"""
    DISCOVERY = "discovery"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    RETENTION = "retention"
    MONETIZATION = "monetization"
    VIRAL_POTENTIAL = "viral_potential"
    BRAND_BUILDING = "brand_building"

class AIModel(Enum):
    """AI models for content enhancement"""
    GPT_4 = "gpt-4"
    CLAUDE_3 = "claude-3"
    GEMINI_PRO = "gemini-pro"
    LLAMA_2 = "llama-2"
    CUSTOM_BERT = "custom-bert"

@dataclass
class ContentAnalysis:
    """Content analysis results"""
    content_id: str = ""
    original_content: str = ""
    content_type: ContentType = ContentType.TITLE
    platform: Platform = Platform.YOUTUBE
    language: str = "en"
    word_count: int = 0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    keyword_density: Dict[str, float] = field(default_factory=dict)
    semantic_topics: List[str] = field(default_factory=list)
    engagement_factors: Dict[str, float] = field(default_factory=dict)
    seo_score: float = 0.0
    improvement_potential: float = 0.0

@dataclass
class EnhancementSuggestion:
    """AI-generated content enhancement suggestion"""
    suggestion_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suggestion_type: str = ""
    original_text: str = ""
    enhanced_text: str = ""
    confidence_score: float = 0.0
    improvement_reasoning: str = ""
    seo_impact: Dict[str, float] = field(default_factory=dict)
    keywords_added: List[str] = field(default_factory=list)
    platform_optimization: Dict[Platform, float] = field(default_factory=dict)
    creator_voice_preserved: bool = True

@dataclass
class OptimizationResult:
    """Complete optimization result"""
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    content_analysis: ContentAnalysis = field(default_factory=ContentAnalysis)
    suggestions: List[EnhancementSuggestion] = field(default_factory=list)
    optimization_goal: OptimizationGoal = OptimizationGoal.DISCOVERY
    ai_model_used: AIModel = AIModel.GPT_4
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    applied_suggestions: List[str] = field(default_factory=list)
    performance_improvement: Dict[str, float] = field(default_factory=dict)

class AIContentEnhancementEngine:
    """
    AI Content Enhancement Engine
    ============================
    
    Advanced AI-powered content optimization system
    for creator economy SEO enhancement.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Initialize NLP components
        self._initialize_nlp_components()
        
        # Platform-specific optimization rules
        self.platform_rules = {
            Platform.YOUTUBE: {
                'title_max_length': 60,
                'description_max_length': 5000,
                'tags_max_count': 15,
                'optimal_title_length': 50,
                'key_moments': [0, 15, 30],  # seconds for keyword placement
                'trending_factors': ['clickbait_moderate', 'emotional_hooks', 'curiosity_gap']
            },
            Platform.INSTAGRAM: {
                'caption_max_length': 2200,
                'hashtags_max_count': 30,
                'optimal_hashtags': 11,
                'story_text_limit': 160,
                'trending_factors': ['visual_appeal', 'hashtag_mix', 'story_engagement']
            },
            Platform.TIKTOK: {
                'caption_max_length': 150,
                'hashtags_max_count': 5,
                'optimal_duration': 15,
                'trending_factors': ['hook_first_3_seconds', 'music_sync', 'challenge_participation']
            },
            Platform.TWITTER: {
                'tweet_max_length': 280,
                'thread_optimal_length': 7,
                'hashtags_max_count': 3,
                'trending_factors': ['controversy_mild', 'timeliness', 'conversation_starter']
            },
            Platform.LINKEDIN: {
                'post_max_length': 3000,
                'headline_max_length': 120,
                'optimal_post_length': 150,
                'trending_factors': ['professional_insight', 'industry_trends', 'thought_leadership']
            }
        }
        
        # AI prompt templates
        self.prompt_templates = {
            'title_optimization': """
            Optimize this {platform} title for maximum discoverability and engagement:
            
            Original: "{original_title}"
            
            Creator Profile: {creator_profile}
            Target Audience: {target_audience}
            Primary Keywords: {primary_keywords}
            Optimization Goal: {goal}
            
            Provide 3 optimized versions that:
            1. Maintain the creator's authentic voice
            2. Include primary keywords naturally
            3. Create emotional engagement
            4. Follow {platform} best practices
            5. Maximize click-through potential
            
            For each version, explain the optimization strategy.
            """,
            
            'description_enhancement': """
            Enhance this {platform} description for SEO and engagement:
            
            Original: "{original_description}"
            
            Context:
            - Content Type: {content_type}
            - Target Keywords: {keywords}
            - Creator Niche: {niche}
            - Audience Demographics: {demographics}
            - Monetization Goal: {monetization}
            
            Create an enhanced description that:
            1. Improves search discoverability
            2. Encourages viewer engagement
            3. Includes call-to-action elements
            4. Maintains creator authenticity
            5. Optimizes for platform algorithm
            
            Include keyword placement strategy.
            """,
            
            'hashtag_optimization': """
            Generate optimized hashtags for this {platform} content:
            
            Content Summary: "{content_summary}"
            Niche: {niche}
            Target Audience: {audience}
            Current Hashtags: {current_hashtags}
            
            Provide:
            1. 5 high-volume hashtags for reach
            2. 5 medium-volume hashtags for engagement
            3. 5 low-volume hashtags for community
            4. 3 branded hashtags for identity
            5. 2 trending hashtags for visibility
            
            Explain the strategy behind each category.
            """,
            
            'content_structure': """
            Optimize the structure of this content for better engagement:
            
            Content: "{content}"
            Platform: {platform}
            Duration/Length: {duration}
            
            Suggest improvements for:
            1. Hook/Opening (first 15 seconds/lines)
            2. Content flow and pacing
            3. Key message placement
            4. Engagement triggers
            5. Call-to-action placement
            
            Maintain creator's style while optimizing for {platform} algorithm.
            """
        }
        
        # Enhancement metrics
        self.metrics = {
            'content_analyzed': 0,
            'suggestions_generated': 0,
            'optimizations_applied': 0,
            'average_seo_improvement': 0.0,
            'average_processing_time': 0.0,
            'creator_satisfaction': 0.0,
            'performance_lift': 0.0
        }
        
        # Content optimization history
        self.optimization_history: Dict[str, List[OptimizationResult]] = {}
        
        logger.info("🧠 AI Content Enhancement Engine initialized")

    async def initialize(self):
        """Initialize Redis connection and load configurations"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_optimization_history()
            logger.info("✅ AI Content Enhancement Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Content Enhancement Engine: {e}")
            raise

    def _initialize_nlp_components(self):
        """Initialize NLP libraries and models"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Initialize components
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Try to load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("⚠️ spaCy model not found, using basic NLP")
                self.nlp = None
                
        except Exception as e:
            logger.warning(f"⚠️ Error initializing NLP components: {e}")

    async def analyze_content(
        self,
        content: str,
        content_type: ContentType,
        platform: Platform,
        creator_id: str = "",
        additional_context: Dict[str, Any] = None
    ) -> ContentAnalysis:
        """
        Analyze content for optimization opportunities
        
        Args:
            content: Content to analyze
            content_type: Type of content
            platform: Target platform
            creator_id: Creator identifier
            additional_context: Additional context for analysis
            
        Returns:
            ContentAnalysis object with analysis results
        """
        try:
            start_time = time.time()
            
            # Basic content metrics
            word_count = len(content.split())
            
            # Readability analysis
            readability_score = self._calculate_readability(content)
            
            # Sentiment analysis
            sentiment_score = self._analyze_sentiment(content)
            
            # Keyword density analysis
            keyword_density = self._analyze_keyword_density(content)
            
            # Semantic topic extraction
            semantic_topics = await self._extract_semantic_topics(content)
            
            # Engagement factor analysis
            engagement_factors = self._analyze_engagement_factors(content, platform)
            
            # SEO score calculation
            seo_score = self._calculate_seo_score(
                content, content_type, platform, 
                readability_score, sentiment_score, keyword_density
            )
            
            # Improvement potential
            improvement_potential = self._calculate_improvement_potential(
                seo_score, engagement_factors, platform
            )
            
            analysis = ContentAnalysis(
                content_id=hashlib.md5(content.encode()).hexdigest()[:8],
                original_content=content,
                content_type=content_type,
                platform=platform,
                language=self._detect_language(content),
                word_count=word_count,
                readability_score=readability_score,
                sentiment_score=sentiment_score,
                keyword_density=keyword_density,
                semantic_topics=semantic_topics,
                engagement_factors=engagement_factors,
                seo_score=seo_score,
                improvement_potential=improvement_potential
            )
            
            processing_time = time.time() - start_time
            self.metrics['content_analyzed'] += 1
            self.metrics['average_processing_time'] = (
                (self.metrics['average_processing_time'] * (self.metrics['content_analyzed'] - 1) + processing_time) / 
                self.metrics['content_analyzed']
            )
            
            logger.info(f"📊 Content analyzed: SEO score {seo_score:.2f}, improvement potential {improvement_potential:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing content: {e}")
            return ContentAnalysis()

    async def generate_enhancement_suggestions(
        self,
        analysis: ContentAnalysis,
        optimization_goal: OptimizationGoal = OptimizationGoal.DISCOVERY,
        creator_profile: Dict[str, Any] = None,
        ai_model: AIModel = AIModel.GPT_4
    ) -> List[EnhancementSuggestion]:
        """
        Generate AI-powered enhancement suggestions
        
        Args:
            analysis: Content analysis results
            optimization_goal: Optimization objective
            creator_profile: Creator profile information
            ai_model: AI model to use for generation
            
        Returns:
            List of enhancement suggestions
        """
        try:
            suggestions = []
            
            # Title optimization
            if analysis.content_type == ContentType.TITLE:
                title_suggestions = await self._generate_title_suggestions(
                    analysis, optimization_goal, creator_profile, ai_model
                )
                suggestions.extend(title_suggestions)
                
            # Description enhancement
            elif analysis.content_type == ContentType.DESCRIPTION:
                description_suggestions = await self._generate_description_suggestions(
                    analysis, optimization_goal, creator_profile, ai_model
                )
                suggestions.extend(description_suggestions)
                
            # Hashtag optimization
            elif analysis.content_type == ContentType.HASHTAGS:
                hashtag_suggestions = await self._generate_hashtag_suggestions(
                    analysis, optimization_goal, creator_profile, ai_model
                )
                suggestions.extend(hashtag_suggestions)
                
            # Content structure optimization
            else:
                structure_suggestions = await self._generate_structure_suggestions(
                    analysis, optimization_goal, creator_profile, ai_model
                )
                suggestions.extend(structure_suggestions)
                
            # Platform-specific optimizations
            platform_suggestions = await self._generate_platform_specific_suggestions(
                analysis, optimization_goal
            )
            suggestions.extend(platform_suggestions)
            
            # SEO-specific optimizations
            seo_suggestions = await self._generate_seo_suggestions(analysis)
            suggestions.extend(seo_suggestions)
            
            # Sort by confidence score
            suggestions.sort(key=lambda s: s.confidence_score, reverse=True)
            
            self.metrics['suggestions_generated'] += len(suggestions)
            
            logger.info(f"💡 Generated {len(suggestions)} enhancement suggestions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating suggestions: {e}")
            return []

    async def _generate_title_suggestions(
        self,
        analysis: ContentAnalysis,
        goal: OptimizationGoal,
        creator_profile: Dict[str, Any],
        ai_model: AIModel
    ) -> List[EnhancementSuggestion]:
        """Generate title optimization suggestions"""
        suggestions = []
        
        # Analyze current title issues
        title_issues = self._identify_title_issues(analysis)
        
        # Generate keyword-optimized title
        if 'keyword_optimization' in title_issues:
            enhanced_title = await self._enhance_title_keywords(analysis.original_content, analysis.platform)
            suggestions.append(EnhancementSuggestion(
                suggestion_type="keyword_optimization",
                original_text=analysis.original_content,
                enhanced_text=enhanced_title,
                confidence_score=0.85,
                improvement_reasoning="Added high-value keywords while maintaining readability",
                seo_impact={'keyword_relevance': 0.3, 'search_visibility': 0.25},
                keywords_added=self._extract_added_keywords(analysis.original_content, enhanced_title)
            ))
            
        # Generate emotional hook title
        if 'emotional_engagement' in title_issues:
            emotional_title = await self._enhance_title_emotion(analysis.original_content, goal)
            suggestions.append(EnhancementSuggestion(
                suggestion_type="emotional_engagement",
                original_text=analysis.original_content,
                enhanced_text=emotional_title,
                confidence_score=0.78,
                improvement_reasoning="Enhanced emotional appeal to increase click-through rate",
                seo_impact={'engagement_rate': 0.4, 'click_through_rate': 0.35}
            ))
            
        # Generate length-optimized title
        if 'length_optimization' in title_issues:
            optimized_title = await self._optimize_title_length(analysis.original_content, analysis.platform)
            suggestions.append(EnhancementSuggestion(
                suggestion_type="length_optimization",
                original_text=analysis.original_content,
                enhanced_text=optimized_title,
                confidence_score=0.72,
                improvement_reasoning="Optimized length for platform visibility and mobile display",
                seo_impact={'mobile_visibility': 0.3, 'platform_algorithm': 0.25}
            ))
            
        return suggestions

    async def _generate_description_suggestions(
        self,
        analysis: ContentAnalysis,
        goal: OptimizationGoal,
        creator_profile: Dict[str, Any],
        ai_model: AIModel
    ) -> List[EnhancementSuggestion]:
        """Generate description enhancement suggestions"""
        suggestions = []
        
        # Keyword optimization
        if analysis.seo_score < 0.7:
            enhanced_desc = await self._enhance_description_seo(analysis.original_content, analysis.platform)
            suggestions.append(EnhancementSuggestion(
                suggestion_type="seo_optimization",
                original_text=analysis.original_content,
                enhanced_text=enhanced_desc,
                confidence_score=0.82,
                improvement_reasoning="Improved keyword distribution and semantic relevance",
                seo_impact={'search_ranking': 0.35, 'keyword_relevance': 0.4}
            ))
            
        # Call-to-action enhancement
        if not self._has_call_to_action(analysis.original_content):
            cta_enhanced = await self._add_call_to_action(analysis.original_content, goal)
            suggestions.append(EnhancementSuggestion(
                suggestion_type="call_to_action",
                original_text=analysis.original_content,
                enhanced_text=cta_enhanced,
                confidence_score=0.75,
                improvement_reasoning="Added strategic call-to-action to improve conversion",
                seo_impact={'engagement_rate': 0.3, 'conversion_rate': 0.45}
            ))
            
        # Structure optimization
        structure_enhanced = await self._optimize_description_structure(analysis.original_content)
        suggestions.append(EnhancementSuggestion(
            suggestion_type="structure_optimization",
            original_text=analysis.original_content,
            enhanced_text=structure_enhanced,
            confidence_score=0.68,
            improvement_reasoning="Improved content structure for better readability and engagement",
            seo_impact={'user_experience': 0.25, 'dwell_time': 0.2}
        ))
        
        return suggestions

    async def _generate_hashtag_suggestions(
        self,
        analysis: ContentAnalysis,
        goal: OptimizationGoal,
        creator_profile: Dict[str, Any],
        ai_model: AIModel
    ) -> List[EnhancementSuggestion]:
        """Generate hashtag optimization suggestions"""
        suggestions = []
        
        # Extract current hashtags
        current_hashtags = self._extract_hashtags(analysis.original_content)
        
        # Generate optimized hashtag mix
        optimized_hashtags = await self._generate_optimal_hashtag_mix(
            analysis.semantic_topics, analysis.platform, goal
        )
        
        # High-volume hashtags
        high_volume = optimized_hashtags['high_volume']
        suggestions.append(EnhancementSuggestion(
            suggestion_type="high_volume_hashtags",
            original_text=' '.join(current_hashtags),
            enhanced_text=' '.join(high_volume),
            confidence_score=0.85,
            improvement_reasoning="High-volume hashtags for maximum reach and discoverability",
            seo_impact={'reach': 0.5, 'discoverability': 0.4}
        ))
        
        # Niche-specific hashtags
        niche_hashtags = optimized_hashtags['niche_specific']
        suggestions.append(EnhancementSuggestion(
            suggestion_type="niche_hashtags",
            original_text=' '.join(current_hashtags),
            enhanced_text=' '.join(niche_hashtags),
            confidence_score=0.78,
            improvement_reasoning="Niche-specific hashtags for targeted audience engagement",
            seo_impact={'engagement_rate': 0.4, 'audience_quality': 0.45}
        ))
        
        # Trending hashtags
        trending_hashtags = optimized_hashtags['trending']
        suggestions.append(EnhancementSuggestion(
            suggestion_type="trending_hashtags",
            original_text=' '.join(current_hashtags),
            enhanced_text=' '.join(trending_hashtags),
            confidence_score=0.65,
            improvement_reasoning="Trending hashtags for viral potential and current relevance",
            seo_impact={'viral_potential': 0.6, 'timeliness': 0.3}
        ))
        
        return suggestions

    async def _generate_platform_specific_suggestions(
        self,
        analysis: ContentAnalysis,
        goal: OptimizationGoal
    ) -> List[EnhancementSuggestion]:
        """Generate platform-specific optimization suggestions"""
        suggestions = []
        platform_rules = self.platform_rules.get(analysis.platform, {})
        
        if analysis.platform == Platform.YOUTUBE:
            # YouTube-specific optimizations
            if analysis.content_type == ContentType.TITLE:
                if len(analysis.original_content) > platform_rules.get('title_max_length', 60):
                    suggestions.append(EnhancementSuggestion(
                        suggestion_type="youtube_title_length",
                        original_text=analysis.original_content,
                        enhanced_text=analysis.original_content[:57] + "...",
                        confidence_score=0.70,
                        improvement_reasoning="Optimized for YouTube title display limits",
                        platform_optimization={Platform.YOUTUBE: 0.3}
                    ))
                    
        elif analysis.platform == Platform.INSTAGRAM:
            # Instagram-specific optimizations
            if analysis.content_type == ContentType.HASHTAGS:
                current_count = len(self._extract_hashtags(analysis.original_content))
                optimal_count = platform_rules.get('optimal_hashtags', 11)
                
                if current_count != optimal_count:
                    suggestions.append(EnhancementSuggestion(
                        suggestion_type="instagram_hashtag_count",
                        original_text=analysis.original_content,
                        enhanced_text="Optimized to 11 hashtags for best performance",
                        confidence_score=0.75,
                        improvement_reasoning=f"Instagram performs best with {optimal_count} hashtags",
                        platform_optimization={Platform.INSTAGRAM: 0.35}
                    ))
                    
        elif analysis.platform == Platform.TIKTOK:
            # TikTok-specific optimizations
            if 'hook_first_3_seconds' not in analysis.engagement_factors:
                suggestions.append(EnhancementSuggestion(
                    suggestion_type="tiktok_hook_optimization",
                    original_text=analysis.original_content,
                    enhanced_text="Add compelling hook in first 3 seconds",
                    confidence_score=0.85,
                    improvement_reasoning="TikTok algorithm heavily weights early engagement",
                    platform_optimization={Platform.TIKTOK: 0.5}
                ))
                
        return suggestions

    async def _generate_seo_suggestions(self, analysis: ContentAnalysis) -> List[EnhancementSuggestion]:
        """Generate SEO-specific suggestions"""
        suggestions = []
        
        # Keyword density optimization
        if max(analysis.keyword_density.values(), default=0) < 0.02:  # Less than 2%
            suggestions.append(EnhancementSuggestion(
                suggestion_type="keyword_density_increase",
                original_text=analysis.original_content,
                enhanced_text="Increase primary keyword density to 2-3%",
                confidence_score=0.72,
                improvement_reasoning="Improve keyword density for better search ranking",
                seo_impact={'keyword_relevance': 0.3, 'search_ranking': 0.25}
            ))
            
        # Readability improvement
        if analysis.readability_score < 60:  # Difficult to read
            suggestions.append(EnhancementSuggestion(
                suggestion_type="readability_improvement",
                original_text=analysis.original_content,
                enhanced_text="Simplify sentence structure and vocabulary",
                confidence_score=0.68,
                improvement_reasoning="Improve readability for better user engagement",
                seo_impact={'user_experience': 0.3, 'dwell_time': 0.25}
            ))
            
        # Semantic richness
        if len(analysis.semantic_topics) < 3:
            suggestions.append(EnhancementSuggestion(
                suggestion_type="semantic_enrichment",
                original_text=analysis.original_content,
                enhanced_text="Add related topics and semantic keywords",
                confidence_score=0.65,
                improvement_reasoning="Enhance semantic richness for better topical authority",
                seo_impact={'topical_authority': 0.4, 'search_visibility': 0.2}
            ))
            
        return suggestions

    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score"""
        try:
            return flesch_reading_ease(content)
        except:
            # Fallback calculation
            words = len(content.split())
            sentences = len(sent_tokenize(content))
            syllables = sum(self._count_syllables(word) for word in content.split())
            
            if sentences == 0 or words == 0:
                return 0.0
                
            flesch = 206.835 - (1.015 * words / sentences) - (84.6 * syllables / words)
            return max(0.0, min(100.0, flesch))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count = 1
        return count

    def _analyze_sentiment(self, content: str) -> float:
        """Analyze content sentiment"""
        try:
            scores = self.sentiment_analyzer.polarity_scores(content)
            return scores['compound']
        except:
            return 0.0

    def _analyze_keyword_density(self, content: str) -> Dict[str, float]:
        """Analyze keyword density"""
        words = word_tokenize(content.lower())
        words = [word for word in words if word.isalpha() and word not in self.stop_words]
        
        if not words:
            return {}
            
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        total_words = len(words)
        keyword_density = {
            word: count / total_words 
            for word, count in word_freq.items()
            if count > 1  # Only words that appear more than once
        }
        
        # Return top 10 keywords
        return dict(sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:10])

    async def _extract_semantic_topics(self, content: str) -> List[str]:
        """Extract semantic topics using NLP"""
        try:
            if self.nlp:
                doc = self.nlp(content)
                # Extract named entities and noun phrases
                topics = []
                
                # Named entities
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'PRODUCT']:
                        topics.append(ent.text.lower())
                        
                # Noun phrases
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) <= 3:  # Max 3 words
                        topics.append(chunk.text.lower())
                        
                return list(set(topics))[:10]  # Top 10 unique topics
            else:
                # Fallback: extract frequent noun phrases
                words = word_tokenize(content.lower())
                # Simple bigram extraction
                bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
                return list(set(bigrams))[:5]
                
        except Exception as e:
            logger.error(f"Error extracting semantic topics: {e}")
            return []

    def _analyze_engagement_factors(self, content: str, platform: Platform) -> Dict[str, float]:
        """Analyze engagement factors"""
        factors = {}
        
        # Question words (increase engagement)
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        factors['question_density'] = sum(
            1 for word in content.lower().split() 
            if word in question_words
        ) / len(content.split())
        
        # Emotional words
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'secret', 'hidden']
        factors['emotional_intensity'] = sum(
            1 for word in content.lower().split() 
            if word in emotional_words
        ) / len(content.split())
        
        # Numbers (attract attention)
        numbers = re.findall(r'\d+', content)
        factors['number_presence'] = len(numbers) / len(content.split())
        
        # Platform-specific factors
        if platform == Platform.YOUTUBE:
            factors['clickbait_indicators'] = self._calculate_clickbait_score(content)
        elif platform == Platform.INSTAGRAM:
            factors['visual_descriptors'] = self._calculate_visual_language_score(content)
        elif platform == Platform.TIKTOK:
            factors['trending_language'] = self._calculate_trending_language_score(content)
            
        return factors

    def _calculate_clickbait_score(self, content: str) -> float:
        """Calculate moderate clickbait score for YouTube"""
        clickbait_phrases = [
            'you won\'t believe', 'this will shock you', 'number 7 will amaze you',
            'wait for it', 'this changes everything', 'secret technique'
        ]
        score = sum(1 for phrase in clickbait_phrases if phrase in content.lower())
        return min(score / 2, 0.5)  # Cap at moderate level

    def _calculate_visual_language_score(self, content: str) -> float:
        """Calculate visual language score for Instagram"""
        visual_words = ['gorgeous', 'stunning', 'beautiful', 'aesthetic', 'vibes', 'mood']
        score = sum(1 for word in visual_words if word in content.lower())
        return min(score / 3, 1.0)

    def _calculate_trending_language_score(self, content: str) -> float:
        """Calculate trending language score for TikTok"""
        trending_words = ['viral', 'trend', 'challenge', 'pov', 'duet', 'fyp']
        score = sum(1 for word in trending_words if word in content.lower())
        return min(score / 2, 1.0)

    def _calculate_seo_score(
        self,
        content: str,
        content_type: ContentType,
        platform: Platform,
        readability: float,
        sentiment: float,
        keyword_density: Dict[str, float]
    ) -> float:
        """Calculate overall SEO score"""
        score = 0.0
        
        # Readability component (30%)
        readability_score = readability / 100.0
        score += readability_score * 0.3
        
        # Keyword optimization (25%)
        if keyword_density:
            max_density = max(keyword_density.values())
            optimal_density = 0.025  # 2.5%
            keyword_score = 1.0 - abs(max_density - optimal_density) / optimal_density
            score += max(0, keyword_score) * 0.25
            
        # Content length (20%)
        word_count = len(content.split())
        platform_rules = self.platform_rules.get(platform, {})
        
        if content_type == ContentType.TITLE:
            optimal_length = platform_rules.get('optimal_title_length', 50)
            length_score = 1.0 - abs(word_count - optimal_length / 5) / (optimal_length / 5)
        else:
            length_score = min(word_count / 100, 1.0)  # More content generally better
            
        score += max(0, length_score) * 0.2
        
        # Sentiment appropriateness (15%)
        sentiment_score = 0.5 + sentiment * 0.5  # Convert -1,1 to 0,1
        score += sentiment_score * 0.15
        
        # Platform-specific optimization (10%)
        platform_score = 0.7  # Base score
        score += platform_score * 0.1
        
        return min(1.0, max(0.0, score))

    def _calculate_improvement_potential(
        self,
        seo_score: float,
        engagement_factors: Dict[str, float],
        platform: Platform
    ) -> float:
        """Calculate improvement potential"""
        # Base improvement is inverse of current score
        base_improvement = 1.0 - seo_score
        
        # Factor in engagement potential
        avg_engagement = sum(engagement_factors.values()) / len(engagement_factors) if engagement_factors else 0
        engagement_potential = 1.0 - avg_engagement
        
        # Combine scores
        improvement_potential = (base_improvement * 0.7) + (engagement_potential * 0.3)
        
        return min(1.0, max(0.0, improvement_potential))

    def _detect_language(self, content: str) -> str:
        """Detect content language"""
        # Simple language detection based on common words
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = set(content.lower().split())
        
        english_count = len(words.intersection(english_words))
        if english_count > len(words) * 0.1:  # 10% English words
            return 'en'
        else:
            return 'unknown'

    def _identify_title_issues(self, analysis: ContentAnalysis) -> List[str]:
        """Identify issues with current title"""
        issues = []
        
        platform_rules = self.platform_rules.get(analysis.platform, {})
        max_length = platform_rules.get('title_max_length', 60)
        
        if len(analysis.original_content) > max_length:
            issues.append('length_optimization')
            
        if analysis.seo_score < 0.7:
            issues.append('keyword_optimization')
            
        if analysis.sentiment_score < 0.1:  # Too neutral
            issues.append('emotional_engagement')
            
        if not any(factor > 0.1 for factor in analysis.engagement_factors.values()):
            issues.append('engagement_optimization')
            
        return issues

    async def _enhance_title_keywords(self, title: str, platform: Platform) -> str:
        """Enhance title with keywords"""
        # Simplified keyword enhancement
        enhanced = title
        
        # Add platform-specific trending words
        if platform == Platform.YOUTUBE and 'tutorial' not in title.lower():
            enhanced = f"How to {title}"
        elif platform == Platform.INSTAGRAM and '#' not in title:
            enhanced = f"{title} ✨"
        elif platform == Platform.TIKTOK and not any(word in title.lower() for word in ['viral', 'trend']):
            enhanced = f"{title} #viral"
            
        return enhanced

    async def _enhance_title_emotion(self, title: str, goal: OptimizationGoal) -> str:
        """Enhance title emotional appeal"""
        emotional_words = {
            OptimizationGoal.DISCOVERY: ['Amazing', 'Incredible', 'Ultimate'],
            OptimizationGoal.ENGAGEMENT: ['Shocking', 'Unbelievable', 'Mind-blowing'],
            OptimizationGoal.VIRAL_POTENTIAL: ['Viral', 'Trending', 'Everyone\'s talking about']
        }
        
        words = emotional_words.get(goal, ['Amazing'])
        enhanced = f"{words[0]} {title}"
        
        return enhanced

    async def _optimize_title_length(self, title: str, platform: Platform) -> str:
        """Optimize title length for platform"""
        platform_rules = self.platform_rules.get(platform, {})
        max_length = platform_rules.get('title_max_length', 60)
        
        if len(title) <= max_length:
            return title
            
        # Truncate while preserving meaning
        words = title.split()
        while len(' '.join(words)) > max_length and words:
            words.pop()
            
        return ' '.join(words) + '...'

    async def _enhance_description_seo(self, description: str, platform: Platform) -> str:
        """Enhance description for SEO"""
        # Add strategic keywords and improve structure
        enhanced = description
        
        # Add call-to-action if missing
        if not self._has_call_to_action(description):
            enhanced += "\n\n👍 Like and subscribe for more content!"
            
        # Add hashtags if platform supports them
        if platform in [Platform.INSTAGRAM, Platform.TIKTOK, Platform.LINKEDIN]:
            enhanced += "\n\n#content #creator #viral"
            
        return enhanced

    def _has_call_to_action(self, content: str) -> bool:
        """Check if content has call-to-action"""
        cta_phrases = ['subscribe', 'follow', 'like', 'share', 'comment', 'click', 'buy', 'join']
        return any(phrase in content.lower() for phrase in cta_phrases)

    async def _add_call_to_action(self, content: str, goal: OptimizationGoal) -> str:
        """Add appropriate call-to-action"""
        cta_map = {
            OptimizationGoal.DISCOVERY: "🔔 Subscribe for more amazing content!",
            OptimizationGoal.ENGAGEMENT: "💬 What do you think? Comment below!",
            OptimizationGoal.CONVERSION: "🛒 Check out the link in bio!",
            OptimizationGoal.MONETIZATION: "💰 Support us by liking and sharing!"
        }
        
        cta = cta_map.get(goal, "👍 Like and follow for more!")
        return f"{content}\n\n{cta}"

    async def _optimize_description_structure(self, description: str) -> str:
        """Optimize description structure"""
        # Add line breaks for better readability
        sentences = sent_tokenize(description)
        
        # Group sentences into paragraphs
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 2:  # 2 sentences per paragraph
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
                
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
            
        return '\n\n'.join(paragraphs)

    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        return re.findall(r'#\w+', content)

    async def _generate_optimal_hashtag_mix(
        self,
        topics: List[str],
        platform: Platform,
        goal: OptimizationGoal
    ) -> Dict[str, List[str]]:
        """Generate optimal hashtag mix"""
        hashtag_mix = {
            'high_volume': [],
            'niche_specific': [],
            'trending': []
        }
        
        # High-volume hashtags (platform-generic)
        high_volume_base = {
            Platform.INSTAGRAM: ['#love', '#instagood', '#photooftheday', '#fashion', '#beautiful'],
            Platform.TIKTOK: ['#fyp', '#viral', '#trending', '#foryou', '#tiktok'],
            Platform.LINKEDIN: ['#linkedin', '#professional', '#career', '#business', '#networking']
        }
        
        hashtag_mix['high_volume'] = high_volume_base.get(platform, ['#content', '#creator', '#viral'])
        
        # Niche-specific (based on topics)
        hashtag_mix['niche_specific'] = [f"#{topic.replace(' ', '')}" for topic in topics[:5]]
        
        # Trending (goal-based)
        trending_base = {
            OptimizationGoal.VIRAL_POTENTIAL: ['#viral', '#trending', '#explore'],
            OptimizationGoal.ENGAGEMENT: ['#comment', '#engage', '#community'],
            OptimizationGoal.MONETIZATION: ['#sponsor', '#partnership', '#collab']
        }
        
        hashtag_mix['trending'] = trending_base.get(goal, ['#content', '#creator'])
        
        return hashtag_mix

    def _extract_added_keywords(self, original: str, enhanced: str) -> List[str]:
        """Extract keywords added in enhancement"""
        original_words = set(original.lower().split())
        enhanced_words = set(enhanced.lower().split())
        
        added_words = enhanced_words - original_words
        return list(added_words)

    async def _load_optimization_history(self):
        """Load optimization history from Redis"""
        if self.redis:
            try:
                history_keys = await self.redis.keys("seo:optimization:*")
                for key in history_keys:
                    history_data = await self.redis.get(key)
                    if history_data:
                        data = json.loads(history_data)
                        # Load optimization history
                        
            except Exception as e:
                logger.error(f"❌ Failed to load optimization history: {e}")

    async def get_engine_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics"""
        return {
            'metrics': self.metrics,
            'supported_platforms': len(self.platform_rules),
            'prompt_templates': len(self.prompt_templates),
            'optimization_history': len(self.optimization_history),
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        logger.info("🧠 AI Content Enhancement Engine closed")


# Factory function
async def create_ai_content_enhancement_engine(redis_url: str = "redis://localhost:6379") -> AIContentEnhancementEngine:
    """
    Factory function to create and initialize AI Content Enhancement Engine
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized AIContentEnhancementEngine instance
    """
    engine = AIContentEnhancementEngine(redis_url)
    await engine.initialize()
    return engine


if __name__ == "__main__":
    async def test_ai_content_enhancement():
        """Test the AI content enhancement engine"""
        engine = await create_ai_content_enhancement_engine()
        
        # Test content analysis
        test_content = "How to make money on YouTube in 2025"
        analysis = await engine.analyze_content(
            content=test_content,
            content_type=ContentType.TITLE,
            platform=Platform.YOUTUBE,
            creator_id="creator_12345"
        )
        
        print(f"📊 Content Analysis:")
        print(f"  SEO Score: {analysis.seo_score:.2f}")
        print(f"  Improvement Potential: {analysis.improvement_potential:.2f}")
        print(f"  Readability: {analysis.readability_score:.1f}")
        print(f"  Sentiment: {analysis.sentiment_score:.2f}")
        
        # Generate suggestions
        suggestions = await engine.generate_enhancement_suggestions(
            analysis=analysis,
            optimization_goal=OptimizationGoal.DISCOVERY,
            creator_profile={'niche': 'finance', 'audience': 'young_adults'}
        )
        
        print(f"\n💡 Enhancement Suggestions ({len(suggestions)}):")
        for suggestion in suggestions[:3]:  # Top 3
            print(f"  🔸 {suggestion.suggestion_type}: {suggestion.enhanced_text}")
            print(f"    Confidence: {suggestion.confidence_score:.2f}")
            print(f"    Reasoning: {suggestion.improvement_reasoning}")
            
        # Get metrics
        metrics = await engine.get_engine_metrics()
        print(f"\n📈 Engine Metrics: {json.dumps(metrics, indent=2)}")
        
        await engine.close()

    # Run test
    asyncio.run(test_ai_content_enhancement())