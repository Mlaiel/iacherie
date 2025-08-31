"""
Style Optimizer - Advanced Content Style Optimization and Adaptation Engine

Enterprise-grade style optimization system with personality matching, brand voice adaptation,
and advanced linguistic analysis for professional content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import numpy as np
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertForSequenceClassification
)
from sentence_transformers import SentenceTransformer
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import redis.asyncio as redis

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.cache import CacheManager
from ...utils.text_analyzer import TextAnalyzer
from ...utils.performance import PerformanceMonitor
from ...ai.language_models import AdvancedLanguageProcessor

logger = logging.getLogger(__name__)
settings = get_settings()


class StyleDimension(str, Enum):
    """Style dimensions for analysis and optimization"""
    FORMALITY = "formality"
    COMPLEXITY = "complexity"
    EMOTIONALITY = "emotionality"
    PERSUASIVENESS = "persuasiveness"
    CREATIVITY = "creativity"
    CLARITY = "clarity"
    ENGAGEMENT = "engagement"
    AUTHORITY = "authority"
    FRIENDLINESS = "friendliness"
    CONFIDENCE = "confidence"


class PersonalityType(str, Enum):
    """Personality types for content matching"""
    ANALYTICAL = "analytical"
    DRIVER = "driver"
    EXPRESSIVE = "expressive"
    AMIABLE = "amiable"
    CREATIVE = "creative"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"


class BrandVoice(str, Enum):
    """Brand voice types"""
    CORPORATE = "corporate"
    STARTUP = "startup"
    LUXURY = "luxury"
    FRIENDLY = "friendly"
    INNOVATIVE = "innovative"
    TRADITIONAL = "traditional"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    EXPERT = "expert"
    CONVERSATIONAL = "conversational"


@dataclass
class StyleProfile:
    """Comprehensive style profile for content optimization"""
    formality_score: float  # 0.0 (very informal) to 1.0 (very formal)
    complexity_score: float  # 0.0 (very simple) to 1.0 (very complex)
    emotionality_score: float  # 0.0 (neutral) to 1.0 (highly emotional)
    persuasiveness_score: float  # 0.0 (informational) to 1.0 (highly persuasive)
    creativity_score: float  # 0.0 (conventional) to 1.0 (highly creative)
    clarity_score: float  # 0.0 (unclear) to 1.0 (crystal clear)
    engagement_score: float  # 0.0 (boring) to 1.0 (highly engaging)
    authority_score: float  # 0.0 (uncertain) to 1.0 (authoritative)
    personality_match: PersonalityType
    brand_voice: Optional[BrandVoice] = None
    target_audience: Optional[str] = None
    platform_optimized: Optional[str] = None
    confidence_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StyleOptimizationRequest:
    """Request for style optimization"""
    content: str
    target_style: StyleProfile
    optimization_goals: List[str]
    constraints: Optional[Dict[str, Any]] = None
    preserve_meaning: bool = True
    max_changes: Optional[int] = None
    priority_dimensions: Optional[List[StyleDimension]] = None


class StyleOptimizer:
    """
    Advanced Style Optimizer for content adaptation and enhancement
    
    Provides comprehensive style analysis, personality matching, and intelligent
    content optimization for various audiences and platforms.
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor("style_optimizer")
        self.cache_manager = CacheManager("style_optimization")
        self.text_analyzer = TextAnalyzer()
        self.language_processor = AdvancedLanguageProcessor()
        
        # Model storage
        self._style_models = {}
        self._personality_analyzers = {}
        self._brand_voice_models = {}
        
        # Analysis tools
        self._sentiment_analyzer = None
        self._sentence_transformer = None
        self._vectorizer = TfidfVectorizer(max_features=1000)
        
        # Style patterns and rules
        self._style_patterns = {}
        self._optimization_rules = {}
        
        # Initialize components
        asyncio.create_task(self._initialize_components())
        
        logger.info("StyleOptimizer initialized successfully")
    
    async def _initialize_components(self):
        """Initialize style optimization components"""
        try:
            # Load sentiment analyzer
            self._sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # Load sentence transformer
            self._sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load style classification models
            self._style_models['formality'] = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model"  # Placeholder - would use formal/informal classifier
            )
            
            # Load personality analysis models
            self._personality_analyzers['big5'] = pipeline(
                "text-classification", 
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )
            
            # Load brand voice models
            self._brand_voice_models['corporate'] = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Load style patterns
            self._style_patterns = await self._load_style_patterns()
            self._optimization_rules = await self._load_optimization_rules()
            
            logger.info("Style optimizer components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize style components: {e}")
            # Initialize fallback components
            await self._initialize_fallback_components()
    
    async def _initialize_fallback_components(self):
        """Initialize fallback components if main models fail"""
        try:
            # Simple rule-based fallbacks
            self._style_patterns = {
                'formal_words': ['furthermore', 'consequently', 'therefore', 'however', 'moreover'],
                'informal_words': ['gonna', 'wanna', 'yeah', 'cool', 'awesome'],
                'complex_structures': ['notwithstanding', 'nevertheless', 'in addition to'],
                'simple_structures': ['and', 'but', 'so', 'then', 'also'],
                'emotional_words': ['amazing', 'incredible', 'fantastic', 'terrible', 'wonderful'],
                'neutral_words': ['good', 'bad', 'normal', 'standard', 'typical']
            }
            
            logger.info("Fallback style components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize fallback components: {e}")
            raise
    
    async def analyze_style(self, content: str) -> StyleProfile:
        """
        Analyze the style profile of content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Comprehensive style profile
        """
        async with self.performance_monitor.track_operation("style_analysis"):
            try:
                # Check cache
                cache_key = self._generate_cache_key(content, "analysis")
                cached_profile = await self.cache_manager.get(cache_key)
                if cached_profile:
                    return StyleProfile(**cached_profile)
                
                # Perform comprehensive style analysis
                style_scores = await self._calculate_style_dimensions(content)
                personality_match = await self._analyze_personality(content)
                brand_voice = await self._detect_brand_voice(content)
                
                # Create style profile
                profile = StyleProfile(
                    formality_score=style_scores.get('formality', 0.5),
                    complexity_score=style_scores.get('complexity', 0.5),
                    emotionality_score=style_scores.get('emotionality', 0.5),
                    persuasiveness_score=style_scores.get('persuasiveness', 0.5),
                    creativity_score=style_scores.get('creativity', 0.5),
                    clarity_score=style_scores.get('clarity', 0.5),
                    engagement_score=style_scores.get('engagement', 0.5),
                    authority_score=style_scores.get('authority', 0.5),
                    personality_match=personality_match,
                    brand_voice=brand_voice,
                    confidence_level=await self._calculate_confidence_level(style_scores),
                    metadata={
                        'word_count': len(content.split()),
                        'sentence_count': len([s for s in content.split('.') if s.strip()]),
                        'readability_score': flesch_reading_ease(content) / 100.0,
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                )
                
                # Cache result
                await self.cache_manager.set(cache_key, profile.__dict__, ttl=1800)
                
                return profile
                
            except Exception as e:
                logger.error(f"Style analysis failed: {e}")
                raise
    
    async def optimize_style(self, request: StyleOptimizationRequest) -> Dict[str, Any]:
        """
        Optimize content style based on target profile
        
        Args:
            request: Style optimization request
            
        Returns:
            Optimized content with metadata
        """
        async with self.performance_monitor.track_operation("style_optimization"):
            try:
                # Analyze current style
                current_profile = await self.analyze_style(request.content)
                
                # Calculate optimization plan
                optimization_plan = await self._create_optimization_plan(
                    current_profile, request.target_style, request.optimization_goals
                )
                
                # Apply style transformations
                optimized_content = await self._apply_style_transformations(
                    request.content, optimization_plan, request.constraints
                )
                
                # Validate optimization
                new_profile = await self.analyze_style(optimized_content)
                optimization_success = await self._validate_optimization(
                    request.target_style, new_profile
                )
                
                # Generate improvement suggestions
                suggestions = await self._generate_style_suggestions(
                    optimized_content, request.target_style, new_profile
                )
                
                return {
                    'optimized_content': optimized_content,
                    'original_profile': current_profile.__dict__,
                    'new_profile': new_profile.__dict__,
                    'optimization_success': optimization_success,
                    'improvements_applied': optimization_plan,
                    'suggestions': suggestions,
                    'confidence_score': await self._calculate_optimization_confidence(
                        current_profile, new_profile, request.target_style
                    ),
                    'metadata': {
                        'words_changed': await self._count_word_changes(request.content, optimized_content),
                        'structure_changes': await self._count_structure_changes(request.content, optimized_content),
                        'optimization_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                }
                
            except Exception as e:
                logger.error(f"Style optimization failed: {e}")
                raise
    
    async def _calculate_style_dimensions(self, content: str) -> Dict[str, float]:
        """Calculate scores for all style dimensions"""
        scores = {}
        
        # Formality analysis
        scores['formality'] = await self._analyze_formality(content)
        
        # Complexity analysis
        scores['complexity'] = await self._analyze_complexity(content)
        
        # Emotionality analysis
        scores['emotionality'] = await self._analyze_emotionality(content)
        
        # Persuasiveness analysis
        scores['persuasiveness'] = await self._analyze_persuasiveness(content)
        
        # Creativity analysis
        scores['creativity'] = await self._analyze_creativity(content)
        
        # Clarity analysis
        scores['clarity'] = await self._analyze_clarity(content)
        
        # Engagement analysis
        scores['engagement'] = await self._analyze_engagement(content)
        
        # Authority analysis
        scores['authority'] = await self._analyze_authority(content)
        
        return scores
    
    async def _analyze_formality(self, content: str) -> float:
        """Analyze formality level of content"""
        formal_indicators = self._style_patterns.get('formal_words', [])
        informal_indicators = self._style_patterns.get('informal_words', [])
        
        words = content.lower().split()
        formal_count = sum(1 for word in words if word in formal_indicators)
        informal_count = sum(1 for word in words if word in informal_indicators)
        
        # Check sentence structure
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Formal score based on vocabulary and structure
        vocab_formality = (formal_count - informal_count) / max(len(words), 1)
        structure_formality = min(avg_sentence_length / 20, 1.0)  # Longer sentences tend to be more formal
        
        # Combine factors
        formality_score = (vocab_formality + structure_formality + 1.0) / 3.0
        return max(0.0, min(formality_score, 1.0))
    
    async def _analyze_complexity(self, content: str) -> float:
        """Analyze complexity level of content"""
        # Readability-based complexity
        try:
            flesch_score = flesch_reading_ease(content) / 100.0
            complexity_from_readability = 1.0 - flesch_score  # Invert: lower readability = higher complexity
        except:
            complexity_from_readability = 0.5
        
        # Vocabulary complexity
        words = content.split()
        long_words = [w for w in words if len(w) > 6]
        vocab_complexity = len(long_words) / max(len(words), 1)
        
        # Sentence structure complexity
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        structure_complexity = min(avg_sentence_length / 25, 1.0)
        
        # Combined complexity score
        complexity_score = (complexity_from_readability + vocab_complexity + structure_complexity) / 3.0
        return max(0.0, min(complexity_score, 1.0))
    
    async def _analyze_emotionality(self, content: str) -> float:
        """Analyze emotional content level"""
        if self._sentiment_analyzer:
            scores = self._sentiment_analyzer.polarity_scores(content)
            # High emotionality indicated by strong positive or negative sentiment
            emotionality = max(abs(scores['pos']), abs(scores['neg']))
        else:
            # Fallback: count emotional words
            emotional_words = self._style_patterns.get('emotional_words', [])
            words = content.lower().split()
            emotional_count = sum(1 for word in words if word in emotional_words)
            emotionality = min(emotional_count / max(len(words), 1) * 5, 1.0)
        
        return emotionality
    
    async def _analyze_persuasiveness(self, content: str) -> float:
        """Analyze persuasive elements in content"""
        persuasive_indicators = [
            'you should', 'you must', 'you need to', 'imagine', 'consider',
            'benefits', 'advantage', 'proven', 'guaranteed', 'results',
            'transform', 'improve', 'enhance', 'achieve', 'succeed'
        ]
        
        content_lower = content.lower()
        persuasive_count = sum(1 for indicator in persuasive_indicators if indicator in content_lower)
        
        # Check for question patterns (engaging persuasion)
        questions = content.count('?')
        
        # Check for imperative sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        imperative_count = 0
        for sentence in sentences:
            if sentence and sentence[0].isupper() and any(word in sentence.lower() for word in ['do', 'try', 'start', 'stop']):
                imperative_count += 1
        
        # Combined persuasiveness score
        persuasive_score = (
            (persuasive_count / 10) + 
            (questions / max(len(sentences), 1)) + 
            (imperative_count / max(len(sentences), 1))
        ) / 3.0
        
        return max(0.0, min(persuasive_score, 1.0))
    
    async def _analyze_creativity(self, content: str) -> float:
        """Analyze creative elements in content"""
        creative_indicators = [
            'imagine', 'picture', 'visualize', 'dream', 'create', 'innovate',
            'unique', 'original', 'creative', 'artistic', 'inspired'
        ]
        
        words = content.lower().split()
        creative_word_count = sum(1 for word in words if word in creative_indicators)
        
        # Check for metaphors and analogies (simplified detection)
        metaphor_indicators = ['like', 'as if', 'reminds me of', 'similar to']
        metaphor_count = sum(1 for indicator in metaphor_indicators if indicator in content.lower())
        
        # Vocabulary diversity as creativity indicator
        unique_words = len(set(words))
        vocab_diversity = unique_words / max(len(words), 1)
        
        # Combined creativity score
        creativity_score = (
            (creative_word_count / max(len(words), 1) * 10) +
            (metaphor_count / 5) +
            vocab_diversity
        ) / 3.0
        
        return max(0.0, min(creativity_score, 1.0))
    
    async def _analyze_clarity(self, content: str) -> float:
        """Analyze clarity of content"""
        try:
            # Readability as clarity indicator
            readability = flesch_reading_ease(content) / 100.0
            
            # Sentence length variance (lower variance = more consistent, clearer)
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            sentence_lengths = [len(s.split()) for s in sentences]
            if sentence_lengths:
                length_variance = np.std(sentence_lengths) / np.mean(sentence_lengths)
                consistency_score = max(0, 1.0 - length_variance)
            else:
                consistency_score = 0.5
            
            # Word clarity (fewer complex words = clearer)
            words = content.split()
            simple_words = [w for w in words if len(w) <= 5]
            word_simplicity = len(simple_words) / max(len(words), 1)
            
            # Combined clarity score
            clarity_score = (readability + consistency_score + word_simplicity) / 3.0
            return max(0.0, min(clarity_score, 1.0))
            
        except:
            return 0.5  # Default if calculation fails
    
    async def _analyze_engagement(self, content: str) -> float:
        """Analyze engagement potential of content"""
        engagement_indicators = [
            'you', 'your', 'we', 'us', 'our', 'together',
            'discover', 'learn', 'explore', 'find out', 'check out'
        ]
        
        words = content.lower().split()
        engagement_words = sum(1 for word in words if word in engagement_indicators)
        
        # Questions increase engagement
        questions = content.count('?')
        
        # Direct address increases engagement
        direct_address = content.lower().count('you ')
        
        # Action words increase engagement
        action_words = ['join', 'start', 'begin', 'try', 'experience', 'feel']
        action_count = sum(1 for word in words if word in action_words)
        
        # Combined engagement score
        engagement_score = (
            (engagement_words / max(len(words), 1) * 5) +
            (questions / max(len([s for s in content.split('.') if s.strip()]), 1)) +
            (direct_address / max(len(words), 1) * 10) +
            (action_count / max(len(words), 1) * 8)
        ) / 4.0
        
        return max(0.0, min(engagement_score, 1.0))
    
    async def _analyze_authority(self, content: str) -> float:
        """Analyze authority/expertise indicators"""
        authority_indicators = [
            'research shows', 'studies indicate', 'evidence suggests',
            'proven', 'demonstrated', 'established', 'confirmed',
            'expert', 'professional', 'experienced', 'certified',
            'data', 'statistics', 'findings', 'results'
        ]
        
        content_lower = content.lower()
        authority_count = sum(1 for indicator in authority_indicators if indicator in content_lower)
        
        # Check for specific numbers/statistics (authority indicator)
        import re
        numbers = len(re.findall(r'\b\d+%|\b\d+\s*(percent|times|years|studies)', content))
        
        # Check for formal language patterns
        formal_structures = ['furthermore', 'therefore', 'consequently', 'moreover']
        formal_count = sum(1 for structure in formal_structures if structure in content_lower)
        
        # Combined authority score
        authority_score = (
            (authority_count / 5) +
            (numbers / 3) +
            (formal_count / 3)
        ) / 3.0
        
        return max(0.0, min(authority_score, 1.0))
    
    async def _analyze_personality(self, content: str) -> PersonalityType:
        """Analyze personality type that matches the content style"""
        # Simplified personality analysis based on style indicators
        scores = {}
        
        # Analytical personality indicators
        analytical_words = ['analyze', 'data', 'research', 'study', 'evidence', 'logical']
        scores[PersonalityType.ANALYTICAL] = sum(1 for word in analytical_words if word in content.lower())
        
        # Driver personality indicators
        driver_words = ['achieve', 'results', 'efficient', 'fast', 'direct', 'goal']
        scores[PersonalityType.DRIVER] = sum(1 for word in driver_words if word in content.lower())
        
        # Expressive personality indicators
        expressive_words = ['exciting', 'amazing', 'fantastic', 'creative', 'innovative', 'fun']
        scores[PersonalityType.EXPRESSIVE] = sum(1 for word in expressive_words if word in content.lower())
        
        # Amiable personality indicators
        amiable_words = ['together', 'team', 'support', 'help', 'friendly', 'caring']
        scores[PersonalityType.AMIABLE] = sum(1 for word in amiable_words if word in content.lower())
        
        # Return personality with highest score
        if scores:
            best_personality = max(scores.items(), key=lambda x: x[1])[0]
            return best_personality
        
        return PersonalityType.PROFESSIONAL  # Default
    
    async def _detect_brand_voice(self, content: str) -> Optional[BrandVoice]:
        """Detect brand voice from content style"""
        # Simplified brand voice detection
        voice_indicators = {
            BrandVoice.CORPORATE: ['professional', 'industry', 'enterprise', 'business'],
            BrandVoice.STARTUP: ['innovative', 'disrupt', 'agile', 'startup'],
            BrandVoice.LUXURY: ['premium', 'exclusive', 'luxury', 'sophisticated'],
            BrandVoice.FRIENDLY: ['friendly', 'welcome', 'community', 'together'],
            BrandVoice.PLAYFUL: ['fun', 'playful', 'exciting', 'cool']
        }
        
        content_lower = content.lower()
        scores = {}
        
        for voice, indicators in voice_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            scores[voice] = score
        
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _generate_cache_key(self, content: str, operation: str) -> str:
        """Generate cache key for style operations"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        return f"style_{operation}_{content_hash}"


class PersonalityMatcher:
    """
    Advanced Personality Matching System
    
    Matches content style with target personality types and provides
    recommendations for personality-specific content optimization.
    """
    
    def __init__(self):
        self.style_optimizer = StyleOptimizer()
        self.performance_monitor = PerformanceMonitor("personality_matcher")
        self.cache_manager = CacheManager("personality_matching")
        
        # Personality profiles database
        self._personality_profiles = {}
        self._load_personality_profiles()
        
        logger.info("PersonalityMatcher initialized")
    
    def _load_personality_profiles(self):
        """Load personality-specific style profiles"""
        self._personality_profiles = {
            PersonalityType.ANALYTICAL: StyleProfile(
                formality_score=0.8,
                complexity_score=0.7,
                emotionality_score=0.2,
                persuasiveness_score=0.5,
                creativity_score=0.4,
                clarity_score=0.9,
                engagement_score=0.6,
                authority_score=0.9,
                personality_match=PersonalityType.ANALYTICAL
            ),
            
            PersonalityType.DRIVER: StyleProfile(
                formality_score=0.6,
                complexity_score=0.5,
                emotionality_score=0.4,
                persuasiveness_score=0.9,
                creativity_score=0.5,
                clarity_score=0.8,
                engagement_score=0.8,
                authority_score=0.7,
                personality_match=PersonalityType.DRIVER
            ),
            
            PersonalityType.EXPRESSIVE: StyleProfile(
                formality_score=0.3,
                complexity_score=0.4,
                emotionality_score=0.9,
                persuasiveness_score=0.8,
                creativity_score=0.9,
                clarity_score=0.6,
                engagement_score=0.9,
                authority_score=0.4,
                personality_match=PersonalityType.EXPRESSIVE
            ),
            
            PersonalityType.AMIABLE: StyleProfile(
                formality_score=0.4,
                complexity_score=0.3,
                emotionality_score=0.7,
                persuasiveness_score=0.6,
                creativity_score=0.6,
                clarity_score=0.8,
                engagement_score=0.8,
                authority_score=0.5,
                personality_match=PersonalityType.AMIABLE
            )
        }
    
    async def match_personality(self, content: str, target_personalities: List[PersonalityType]) -> Dict[str, Any]:
        """
        Match content with target personality types
        
        Args:
            content: Content to analyze
            target_personalities: List of personality types to match against
            
        Returns:
            Matching results with scores and recommendations
        """
        async with self.performance_monitor.track_operation("personality_matching"):
            try:
                # Analyze content style
                content_profile = await self.style_optimizer.analyze_style(content)
                
                # Calculate personality matches
                personality_scores = {}
                for personality in target_personalities:
                    target_profile = self._personality_profiles.get(personality)
                    if target_profile:
                        score = await self._calculate_personality_match(content_profile, target_profile)
                        personality_scores[personality.value] = score
                
                # Find best match
                best_match = max(personality_scores.items(), key=lambda x: x[1]) if personality_scores else None
                
                # Generate recommendations
                recommendations = await self._generate_personality_recommendations(
                    content_profile, target_personalities
                )
                
                return {
                    'content_personality': content_profile.personality_match.value,
                    'personality_scores': personality_scores,
                    'best_match': {
                        'personality': best_match[0],
                        'score': best_match[1]
                    } if best_match else None,
                    'recommendations': recommendations,
                    'analysis_confidence': content_profile.confidence_level
                }
                
            except Exception as e:
                logger.error(f"Personality matching failed: {e}")
                raise
    
    async def _calculate_personality_match(self, content_profile: StyleProfile, target_profile: StyleProfile) -> float:
        """Calculate how well content matches target personality"""
        # Compare all style dimensions
        dimensions = [
            'formality_score', 'complexity_score', 'emotionality_score',
            'persuasiveness_score', 'creativity_score', 'clarity_score',
            'engagement_score', 'authority_score'
        ]
        
        total_similarity = 0.0
        for dimension in dimensions:
            content_value = getattr(content_profile, dimension)
            target_value = getattr(target_profile, dimension)
            # Calculate similarity (inverse of absolute difference)
            similarity = 1.0 - abs(content_value - target_value)
            total_similarity += similarity
        
        return total_similarity / len(dimensions)
    
    async def _generate_personality_recommendations(
        self,
        content_profile: StyleProfile,
        target_personalities: List[PersonalityType]
    ) -> List[str]:
        """Generate recommendations for personality matching"""
        recommendations = []
        
        for personality in target_personalities:
            target_profile = self._personality_profiles.get(personality)
            if not target_profile:
                continue
            
            # Check major gaps and suggest improvements
            if content_profile.formality_score < target_profile.formality_score - 0.3:
                recommendations.append(f"Increase formality for {personality.value} audience with more professional language")
            
            if content_profile.emotionality_score < target_profile.emotionality_score - 0.3:
                recommendations.append(f"Add more emotional language to connect with {personality.value} personality")
            
            if content_profile.authority_score < target_profile.authority_score - 0.3:
                recommendations.append(f"Include more authoritative elements (data, research) for {personality.value} audience")
            
            if content_profile.engagement_score < target_profile.engagement_score - 0.3:
                recommendations.append(f"Increase engagement with direct questions and calls-to-action for {personality.value} readers")
        
        return recommendations[:5]  # Return top 5 recommendations
