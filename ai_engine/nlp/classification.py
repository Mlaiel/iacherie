"""Advanced Content Classification Module for IA Influencer Agent Platform

Intelligent content classification system for categorizing, tagging, and organizing
influencer content across multiple dimensions and platforms.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
import re
import json
from abc import ABC, abstractmethod
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ContentCategory:
    """
Content category structure"""
    name: str
    confidence: float
    subcategories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    description: str = ""

@dataclass
class TopicClassification:
    """Topic classification result"""
    primary_topic: str
    secondary_topics: List[str]
    topic_confidence: Dict[str, float]
    topic_keywords: Dict[str, List[str]]
    topic_relevance: Dict[str, float]

@dataclass
class ContentStyle:
    """
Content style classification"""
    style_type: str  # educational, entertaining, promotional, personal, etc.
    tone: str  # formal, casual, humorous, serious, etc.
    voice: str  # authoritative, friendly, professional, etc.
    format: str  # text, video_script, caption, article, etc.
    complexity_level: str  # beginner, intermediate, advanced
    target_age_group: str  # gen_z, millennial, gen_x, boomer

@dataclass
class AudienceTarget:
    """
Target audience classification"""
    primary_audience: str
    secondary_audiences: List[str]
    demographics: Dict[str, Any]
    interests: List[str]
    engagement_patterns: Dict[str, float]
    platform_preferences: List[str]

@dataclass
class ContentIntent:
    """
Content intent classification"""
    primary_intent: str  # inform, entertain, persuade, sell, inspire, etc.
    secondary_intents: List[str]
    intent_strength: Dict[str, float]
    call_to_action_type: str
    conversion_goal: str

@dataclass
class PlatformOptimization:
    """
Platform-specific classification"""
    best_platforms: List[str]
    platform_scores: Dict[str, float]
    adaptation_suggestions: Dict[str, List[str]]
    format_recommendations: Dict[str, str]
    timing_suggestions: Dict[str, str]

@dataclass
class ClassificationResult:
    """
Complete content classification result"""
    request_id: str
    original_text: str
    content_category: ContentCategory
    topic_classification: TopicClassification
    content_style: ContentStyle
    audience_target: AudienceTarget
    content_intent: ContentIntent
    platform_optimization: PlatformOptimization
    tags: List[str]
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class AdvancedContentClassifier:
    """
    Advanced content classification system
    
    Features:
    - Multi-dimensional content classification
    - Topic modeling and extraction
    - Style and tone analysis
    - Audience targeting classification
    - Intent detection
    - Platform optimization
    - Tag generation
    - Content strategy recommendations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.category_definitions = self._load_category_definitions()
        self.topic_models = self._initialize_topic_models()
        self.style_patterns = self._load_style_patterns()
        self.audience_profiles = self._load_audience_profiles()
        self.intent_patterns = self._load_intent_patterns()
        self.platform_characteristics = self._load_platform_characteristics()
        self.keyword_extractors = self._initialize_keyword_extractors()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
Get default configuration"""
        return {
            'enable_topic_modeling': True,
            'enable_style_analysis': True,
            'enable_audience_targeting': True,
            'enable_intent_detection': True,
            'enable_platform_optimization': True,
            'confidence_threshold': 0.6,
            'max_categories_per_content': 5,
            'max_topics_per_content': 3,
            'enable_tag_generation': True,
            'detailed_analysis': True
        }
    
    def _load_category_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
Load content category definitions"""
        return {
            # Lifestyle categories
            'lifestyle': {
                'subcategories': ['fashion', 'beauty', 'health', 'fitness', 'home', 'food'],
                'keywords': ['style', 'outfit', 'skincare', 'workout', 'recipe', 'home decor'],
                'patterns': [r'\b(outfit|style|fashion|beauty|skincare|makeup)\b'],
                'confidence_boosters': ['ootd', 'grwm', 'skincare routine', 'home tour']
            },
            
            # Technology categories
            'technology': {
                'subcategories': ['software', 'hardware', 'ai', 'mobile', 'gaming', 'programming'],
                'keywords': ['tech', 'software', 'app', 'device', 'code', 'programming', 'ai'],
                'patterns': [r'\b(tech|technology|software|hardware|programming|coding|ai|ml)\b'],
                'confidence_boosters': ['tech review', 'coding tutorial', 'app development']
            },
            
            # Entertainment categories
            'entertainment': {
                'subcategories': ['movies', 'music', 'tv_shows', 'celebrities', 'memes', 'viral'],
                'keywords': ['movie', 'film', 'music', 'song', 'tv', 'show', 'celebrity', 'meme'],
                'patterns': [r'\b(movie|film|music|song|tv|show|celebrity|entertainment)\b'],
                'confidence_boosters': ['movie review', 'music recommendation', 'celebrity news']
            },
            
            # Education categories
            'education': {
                'subcategories': ['tutorials', 'tips', 'how_to', 'learning', 'skills', 'knowledge'],
                'keywords': ['learn', 'tutorial', 'how to', 'guide', 'tip', 'education', 'skill'],
                'patterns': [r'\b(learn|tutorial|guide|tips?|how\s+to|education|teach)\b'],
                'confidence_boosters': ['step by step', 'tutorial', 'learn with me', 'educational']
            },
            
            # Business categories
            'business': {
                'subcategories': ['entrepreneurship', 'marketing', 'finance', 'productivity', 'leadership'],
                'keywords': ['business', 'entrepreneur', 'marketing', 'finance', 'productivity', 'success'],
                'patterns': [r'\b(business|entrepreneur|marketing|finance|productivity|success)\b'],
                'confidence_boosters': ['business tips', 'entrepreneur life', 'marketing strategy']
            },
            
            # Travel categories
            'travel': {
                'subcategories': ['destinations', 'hotels', 'food', 'culture', 'adventure', 'tips'],
                'keywords': ['travel', 'trip', 'vacation', 'destination', 'hotel', 'flight', 'explore'],
                'patterns': [r'\b(travel|trip|vacation|destination|hotel|flight|explore)\b'],
                'confidence_boosters': ['travel vlog', 'destination guide', 'travel tips']
            },
            
            # Sports and Fitness
            'sports_fitness': {
                'subcategories': ['workout', 'nutrition', 'sports', 'wellness', 'mental_health'],
                'keywords': ['fitness', 'workout', 'exercise', 'nutrition', 'health', 'wellness', 'sports'],
                'patterns': [r'\b(fitness|workout|exercise|nutrition|health|wellness|sports)\b'],
                'confidence_boosters': ['workout routine', 'fitness journey', 'healthy lifestyle']
            },
            
            # Gaming
            'gaming': {
                'subcategories': ['reviews', 'tutorials', 'streaming', 'esports', 'mobile_games'],
                'keywords': ['game', 'gaming', 'gamer', 'stream', 'gameplay', 'esports', 'twitch'],
                'patterns': [r'\b(game|gaming|gamer|stream|gameplay|esports|twitch)\b'],
                'confidence_boosters': ['game review', 'gaming setup', 'live stream']
            }
        }
    
    def _initialize_topic_models(self) -> Dict[str, Any]:
        """
Initialize topic modeling components"""
        return {
            'lda_model': 'latent_dirichlet_allocation',  # Would use actual LDA
            'bert_topic': 'bert_topic_model',  # Would use BERTopic
            'nmf_model': 'non_negative_matrix_factorization',
            'topic_coherence': 'coherence_model',
            'topic_keywords': self._build_topic_keyword_database()
        }
    
    def _build_topic_keyword_database(self) -> Dict[str, List[str]]:
        """
Build comprehensive topic keyword database"""
        return {
            # Lifestyle topics
            'fashion': ['outfit', 'style', 'fashion', 'clothes', 'ootd', 'trend', 'designer', 'shopping'],
            'beauty': ['makeup', 'skincare', 'beauty', 'cosmetics', 'grwm', 'tutorial', 'routine'],
            'fitness': ['workout', 'exercise', 'gym', 'fitness', 'health', 'training', 'muscle'],
            'food': ['recipe', 'cooking', 'food', 'meal', 'restaurant', 'cuisine', 'delicious'],
            
            # Technology topics
            'programming': ['code', 'programming', 'developer', 'software', 'coding', 'tech', 'algorithm'],
            'ai_ml': ['ai', 'machine learning', 'artificial intelligence', 'neural network', 'data science'],
            'mobile': ['app', 'mobile', 'ios', 'android', 'smartphone', 'application'],
            'web_development': ['web', 'website', 'html', 'css', 'javascript', 'frontend', 'backend'],
            
            # Business topics
            'entrepreneurship': ['startup', 'entrepreneur', 'business', 'founder', 'innovation', 'venture'],
            'marketing': ['marketing', 'brand', 'advertising', 'campaign', 'social media', 'content'],
            'finance': ['money', 'finance', 'investment', 'cryptocurrency', 'trading', 'economy'],
            'productivity': ['productivity', 'efficiency', 'time management', 'organization', 'goals'],
            
            # Entertainment topics
            'movies': ['movie', 'film', 'cinema', 'director', 'actor', 'review', 'trailer'],
            'music': ['music', 'song', 'artist', 'album', 'concert', 'playlist', 'genre'],
            'gaming': ['game', 'gaming', 'gamer', 'console', 'pc', 'mobile game', 'esports'],
            
            # Lifestyle and wellness
            'mental_health': ['mental health', 'anxiety', 'depression', 'therapy', 'wellness', 'mindfulness'],
            'relationships': ['relationship', 'dating', 'love', 'marriage', 'family', 'friendship'],
            'parenting': ['parent', 'parenting', 'kids', 'children', 'family', 'motherhood', 'fatherhood'],
            
            # Education and learning
            'science': ['science', 'research', 'study', 'experiment', 'discovery', 'scientific'],
            'history': ['history', 'historical', 'past', 'ancient', 'war', 'civilization'],
            'language': ['language', 'learning', 'vocabulary', 'grammar', 'translation', 'linguistic']
        }
    
    def _load_style_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
Load content style patterns"""
        return {
            'educational': {
                'indicators': ['learn', 'tutorial', 'guide', 'how to', 'step by step', 'tips'],
                'patterns': [r'\b(learn|tutorial|guide|tips?|how\s+to|step\s+by\s+step)\b'],
                'structure_markers': ['first', 'next', 'finally', 'step 1', 'step 2'],
                'tone_indicators': ['informative', 'helpful', 'clear', 'detailed']
            },
            'entertaining': {
                'indicators': ['funny', 'hilarious', 'lol', 'meme', 'joke', 'fun', 'entertaining'],
                'patterns': [r'\b(funny|hilarious|lol|meme|joke|fun|entertaining)\b'],
                'structure_markers': ['😂', '🤣', '😆', 'haha', 'lmao'],
                'tone_indicators': ['humorous', 'playful', 'light-hearted', 'witty']
            },
            'promotional': {
                'indicators': ['buy', 'sale', 'discount', 'offer', 'deal', 'limited time', 'exclusive'],
                'patterns': [r'\b(buy|sale|discount|offer|deal|limited\s+time|exclusive)\b'],
                'structure_markers': ['link in bio', 'swipe up', 'dm for details', 'code:'],
                'tone_indicators': ['persuasive', 'urgent', 'exciting', 'beneficial']
            },
            'personal': {
                'indicators': ['my', 'i', 'personal', 'story', 'experience', 'journey', 'life'],
                'patterns': [r'\b(my|personal|story|experience|journey|life)\b'],
                'structure_markers': ['personally', 'in my experience', 'my story', 'sharing'],
                'tone_indicators': ['authentic', 'vulnerable', 'honest', 'relatable']
            },
            'inspirational': {
                'indicators': ['inspire', 'motivate', 'dream', 'achieve', 'success', 'believe', 'possible'],
                'patterns': [r'\b(inspire|motivate|dream|achieve|success|believe|possible)\b'],
                'structure_markers': ['you can', 'believe in yourself', 'never give up', 'dream big'],
                'tone_indicators': ['uplifting', 'encouraging', 'positive', 'empowering']
            },
            'informative': {
                'indicators': ['fact', 'information', 'data', 'research', 'study', 'statistics', 'news'],
                'patterns': [r'\b(fact|information|data|research|study|statistics|news)\b'],
                'structure_markers': ['according to', 'research shows', 'studies indicate', 'data reveals'],
                'tone_indicators': ['factual', 'objective', 'analytical', 'professional']
            }
        }
    
    def _load_audience_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
Load audience profile definitions"""
        return {
            'gen_z': {
                'age_range': (18, 26),
                'interests': ['social media', 'sustainability', 'mental health', 'technology', 'gaming'],
                'platforms': ['tiktok', 'instagram', 'twitter', 'youtube'],
                'content_preferences': ['short-form', 'visual', 'authentic', 'trendy'],
                'language_patterns': ['no cap', 'periodt', 'slay', 'vibes', 'main character', 'that\'s on'],
                'engagement_triggers': ['authentic', 'relatable', 'trendy', 'inclusive']
            },
            'millennials': {
                'age_range': (27, 42),
                'interests': ['career', 'parenting', 'health', 'finance', 'travel', 'lifestyle'],
                'platforms': ['instagram', 'facebook', 'linkedin', 'youtube'],
                'content_preferences': ['informative', 'practical', 'aspirational', 'quality'],
                'language_patterns': ['awesome', 'amazing', 'goals', 'lifestyle', 'self-care', 'work-life balance'],
                'engagement_triggers': ['practical', 'aspirational', 'helpful', 'authentic']
            },
            'gen_x': {
                'age_range': (43, 58),
                'interests': ['family', 'career advancement', 'health', 'finance', 'home improvement'],
                'platforms': ['facebook', 'linkedin', 'youtube', 'instagram'],
                'content_preferences': ['informative', 'professional', 'family-oriented', 'practical'],
                'language_patterns': ['family', 'professional', 'experience', 'quality', 'reliable'],
                'engagement_triggers': ['professional', 'family-focused', 'practical', 'trustworthy']
            },
            'boomers': {
                'age_range': (59, 77),
                'interests': ['health', 'family', 'retirement', 'hobbies', 'travel', 'grandchildren'],
                'platforms': ['facebook', 'youtube', 'email'],
                'content_preferences': ['informative', 'traditional', 'family-oriented', 'clear'],
                'language_patterns': ['family', 'traditional', 'experience', 'wisdom', 'reliable'],
                'engagement_triggers': ['family-oriented', 'traditional', 'clear', 'respectful']
            }
        }
    
    def _load_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
Load content intent patterns"""
        return {
            'inform': {
                'indicators': ['learn', 'know', 'information', 'fact', 'research', 'study', 'explain'],
                'patterns': [r'\b(learn|know|information|fact|research|study|explain)\b'],
                'cta_types': ['read more', 'learn more', 'find out', 'discover'],
                'conversion_goals': ['knowledge', 'awareness', 'education']
            },
            'entertain': {
                'indicators': ['fun', 'funny', 'entertainment', 'amusing', 'hilarious', 'laugh'],
                'patterns': [r'\b(fun|funny|entertainment|amusing|hilarious|laugh)\b'],
                'cta_types': ['watch', 'enjoy', 'share', 'tag a friend'],
                'conversion_goals': ['engagement', 'shares', 'virality']
            },
            'inspire': {
                'indicators': ['inspire', 'motivate', 'empower', 'encourage', 'uplift', 'positive'],
                'patterns': [r'\b(inspire|motivate|empower|encourage|uplift|positive)\b'],
                'cta_types': ['believe', 'achieve', 'try', 'start your journey'],
                'conversion_goals': ['motivation', 'action', 'behavior_change']
            },
            'sell': {
                'indicators': ['buy', 'purchase', 'sale', 'offer', 'deal', 'discount', 'shop'],
                'patterns': [r'\b(buy|purchase|sale|offer|deal|discount|shop)\b'],
                'cta_types': ['buy now', 'shop', 'get yours', 'limited time'],
                'conversion_goals': ['sales', 'revenue', 'conversions']
            },
            'engage': {
                'indicators': ['comment', 'share', 'like', 'follow', 'subscribe', 'join'],
                'patterns': [r'\b(comment|share|like|follow|subscribe|join)\b'],
                'cta_types': ['comment below', 'share your thoughts', 'follow for more'],
                'conversion_goals': ['engagement', 'followers', 'community']
            },
            'educate': {
                'indicators': ['teach', 'tutorial', 'guide', 'how to', 'learn', 'skill'],
                'patterns': [r'\b(teach|tutorial|guide|how\s+to|learn|skill)\b'],
                'cta_types': ['learn', 'practice', 'try', 'master'],
                'conversion_goals': ['skill_development', 'knowledge', 'competency']
            }
        }
    
    def _load_platform_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """
Load platform-specific characteristics"""
        return {
            'instagram': {
                'optimal_content_types': ['lifestyle', 'fashion', 'food', 'travel', 'fitness'],
                'preferred_styles': ['visual', 'aesthetic', 'inspirational', 'personal'],
                'audience_demographics': ['millennials', 'gen_z'],
                'content_formats': ['photos', 'stories', 'reels', 'igtv'],
                'engagement_features': ['likes', 'comments', 'shares', 'saves'],
                'hashtag_importance': 'high',
                'visual_importance': 'very_high'
            },
            'tiktok': {
                'optimal_content_types': ['entertainment', 'education', 'trends', 'challenges'],
                'preferred_styles': ['entertaining', 'trendy', 'authentic', 'creative'],
                'audience_demographics': ['gen_z', 'millennials'],
                'content_formats': ['short_videos', 'effects', 'music'],
                'engagement_features': ['likes', 'comments', 'shares', 'duets'],
                'hashtag_importance': 'medium',
                'visual_importance': 'very_high'
            },
            'youtube': {
                'optimal_content_types': ['education', 'entertainment', 'reviews', 'tutorials'],
                'preferred_styles': ['educational', 'entertaining', 'informative', 'detailed'],
                'audience_demographics': ['all_ages'],
                'content_formats': ['long_videos', 'shorts', 'live_streams'],
                'engagement_features': ['likes', 'comments', 'shares', 'subscribes'],
                'hashtag_importance': 'low',
                'visual_importance': 'high'
            },
            'linkedin': {
                'optimal_content_types': ['business', 'professional', 'career', 'education'],
                'preferred_styles': ['professional', 'informative', 'inspirational', 'educational'],
                'audience_demographics': ['millennials', 'gen_x'],
                'content_formats': ['articles', 'posts', 'videos', 'documents'],
                'engagement_features': ['likes', 'comments', 'shares', 'connections'],
                'hashtag_importance': 'medium',
                'visual_importance': 'medium'
            },
            'twitter': {
                'optimal_content_types': ['news', 'opinions', 'trending', 'conversations'],
                'preferred_styles': ['conversational', 'informative', 'witty', 'timely'],
                'audience_demographics': ['millennials', 'gen_x'],
                'content_formats': ['tweets', 'threads', 'spaces'],
                'engagement_features': ['likes', 'retweets', 'replies', 'quotes'],
                'hashtag_importance': 'high',
                'visual_importance': 'medium'
            }
        }
    
    def _initialize_keyword_extractors(self) -> Dict[str, Any]:
        """
Initialize keyword extraction components"""
        return {
            'tfidf_extractor': 'tfidf_vectorizer',  # Would use actual TF-IDF
            'keybert_extractor': 'keybert_model',  # Would use KeyBERT
            'rake_extractor': 'rake_algorithm',  # Would use RAKE
            'yake_extractor': 'yake_algorithm',  # Would use YAKE
            'custom_extractor': 'domain_specific_extractor'
        }
    
    async def classify_content(self, text: str, context: Dict[str, Any] = None) -> ClassificationResult:
        """
Comprehensive content classification"""
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(text)
        
        try:
            # Content category classification
            content_category = await self._classify_content_category(text)
            
            # Topic classification
            topic_classification = await self._classify_topics(text)
            
            # Content style analysis
            content_style = await self._analyze_content_style(text)
            
            # Audience targeting
            audience_target = await self._classify_target_audience(text, content_style)
            
            # Intent detection
            content_intent = await self._detect_content_intent(text)
            
            # Platform optimization
            platform_optimization = await self._optimize_for_platforms(
                text, content_category, content_style, audience_target
            )
            
            # Tag generation
            tags = await self._generate_tags(text, content_category, topic_classification)
            
            # Metadata extraction
            metadata = await self._extract_metadata(text, context)
            
            # Calculate overall confidence
            confidence_score = await self._calculate_overall_confidence(
                content_category, topic_classification, content_style, content_intent
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ClassificationResult(
                request_id=request_id,
                original_text=text,
                content_category=content_category,
                topic_classification=topic_classification,
                content_style=content_style,
                audience_target=audience_target,
                content_intent=content_intent,
                platform_optimization=platform_optimization,
                tags=tags,
                metadata=metadata,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
            logger.info(f"Content classification completed: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content classification failed for {request_id}: {str(e)}")
            raise
    
    async def batch_classify_content(self, texts: List[str]) -> List[ClassificationResult]:
        """Batch content classification"""
        tasks = [self.classify_content(text) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch classification error: {str(result)}")
                # Create minimal error result
                error_result = ClassificationResult(
                    request_id="error",
                    original_text="",
                    content_category=ContentCategory("unknown", 0.0),
                    topic_classification=TopicClassification("unknown", [], {}, {}, {}),
                    content_style=ContentStyle("unknown", "unknown", "unknown", "unknown", "unknown", "unknown"),
                    audience_target=AudienceTarget("unknown", [], {}, [], {}, []),
                    content_intent=ContentIntent("unknown", [], {}, "unknown", "unknown"),
                    platform_optimization=PlatformOptimization([], {}, {}, {}, {}),
                    tags=[],
                    metadata={},
                    confidence_score=0.0,
                    processing_time=0.0
                )
                valid_results.append(error_result)
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _classify_content_category(self, text: str) -> ContentCategory:
        """Classify content into main categories"""
        
        category_scores = {}
        text_lower = text.lower()
        
        # Score each category
        for category_name, category_info in self.category_definitions.items():
            score = 0.0
            
            # Keyword matching
            keywords = category_info.get('keywords', [])
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1.0
            
            # Pattern matching
            patterns = category_info.get('patterns', [])
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches * 0.5
            
            # Confidence boosters
            boosters = category_info.get('confidence_boosters', [])
            for booster in boosters:
                if booster in text_lower:
                    score += 2.0
            
            # Normalize score
            word_count = len(text.split())
            normalized_score = score / max(word_count, 1) * 10
            category_scores[category_name] = min(1.0, normalized_score)
        
        # Find best category
        if not category_scores:
            return ContentCategory("general", 0.5)
        
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category]
        
        # Get subcategories
        category_info = self.category_definitions[best_category]
        subcategories = await self._classify_subcategories(text, category_info)
        
        # Extract relevant keywords
        keywords = await self._extract_category_keywords(text, best_category)
        
        return ContentCategory(
            name=best_category,
            confidence=confidence,
            subcategories=subcategories,
            keywords=keywords,
            description=f"Content classified as {best_category} with {confidence:.2f} confidence"
        )
    
    async def _classify_subcategories(self, text: str, category_info: Dict[str, Any]) -> List[str]:
        """Classify content into subcategories"""
        subcategories = category_info.get('subcategories', [])
        text_lower = text.lower()
        
        matched_subcategories = []
        
        for subcategory in subcategories:
            # Simple keyword matching for subcategories
            if subcategory.replace('_', ' ') in text_lower:
                matched_subcategories.append(subcategory)
            elif subcategory in text_lower:
                matched_subcategories.append(subcategory)
        
        return matched_subcategories[:3]  # Top 3 subcategories
    
    async def _extract_category_keywords(self, text: str, category: str) -> List[str]:
        """
Extract keywords relevant to the category"""
        category_info = self.category_definitions.get(category, {})
        category_keywords = category_info.get('keywords', [])
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in category_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    async def _classify_topics(self, text: str) -> TopicClassification:
        """
Classify content topics using multiple methods"""
        
        # Extract topics using keyword matching
        topic_scores = {}
        text_lower = text.lower()
        
        topic_keywords = self.topic_models['topic_keywords']
        
        for topic, keywords in topic_keywords.items():
            score = 0.0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1.0
                    found_keywords.append(keyword)
            
            if score > 0:
                # Normalize by text length
                normalized_score = score / len(text.split()) * 10
                topic_scores[topic] = min(1.0, normalized_score)
        
        # Sort topics by relevance
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Primary topic
        primary_topic = sorted_topics[0][0] if sorted_topics else "general"
        
        # Secondary topics
        secondary_topics = [topic for topic, score in sorted_topics[1:4] if score > 0.3]
        
        # Topic confidence scores
        topic_confidence = dict(sorted_topics)
        
        # Topic keywords (found in text)
        topic_keywords_found = {}
        for topic, keywords in topic_keywords.items():
            found = [kw for kw in keywords if kw in text_lower]
            if found:
                topic_keywords_found[topic] = found
        
        # Topic relevance (how relevant each topic is to the content)
        topic_relevance = {}
        for topic, score in topic_scores.items():
            relevance = score * (1 + len(topic_keywords_found.get(topic, [])) * 0.1)
            topic_relevance[topic] = min(1.0, relevance)
        
        return TopicClassification(
            primary_topic=primary_topic,
            secondary_topics=secondary_topics,
            topic_confidence=topic_confidence,
            topic_keywords=topic_keywords_found,
            topic_relevance=topic_relevance
        )
    
    async def _analyze_content_style(self, text: str) -> ContentStyle:
        """Analyze content style and characteristics"""
        
        style_scores = {}
        text_lower = text.lower()
        
        # Analyze each style type
        for style_type, style_info in self.style_patterns.items():
            score = 0.0
            
            # Indicator matching
            indicators = style_info.get('indicators', [])
            for indicator in indicators:
                score += text_lower.count(indicator)
            
            # Pattern matching
            patterns = style_info.get('patterns', [])
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Structure markers
            structure_markers = style_info.get('structure_markers', [])
            for marker in structure_markers:
                if marker in text_lower:
                    score += 2.0
            
            # Normalize score
            normalized_score = score / max(len(text.split()), 1) * 5
            style_scores[style_type] = min(1.0, normalized_score)
        
        # Determine primary style
        primary_style = max(style_scores, key=style_scores.get) if style_scores else "general"
        
        # Analyze tone
        tone = await self._analyze_tone(text)
        
        # Analyze voice
        voice = await self._analyze_voice(text)
        
        # Determine format
        format_type = await self._determine_format(text)
        
        # Determine complexity level
        complexity_level = await self._analyze_complexity(text)
        
        # Determine target age group
        target_age_group = await self._analyze_target_age_group(text)
        
        return ContentStyle(
            style_type=primary_style,
            tone=tone,
            voice=voice,
            format=format_type,
            complexity_level=complexity_level,
            target_age_group=target_age_group
        )
    
    async def _analyze_tone(self, text: str) -> str:
        """Analyze content tone"""
        text_lower = text.lower()
        
        tone_indicators = {
            'formal': ['furthermore', 'consequently', 'therefore', 'moreover', 'however'],
            'casual': ['hey', 'yeah', 'okay', 'cool', 'awesome', 'gonna', 'wanna'],
            'humorous': ['funny', 'hilarious', 'lol', 'haha', 'joke', 'laugh', '😂', '🤣'],
            'serious': ['important', 'critical', 'serious', 'significant', 'matter', 'concern'],
            'enthusiastic': ['amazing', 'incredible', 'fantastic', 'awesome', 'excited', '!', '🔥'],
            'professional': ['professional', 'industry', 'business', 'corporate', 'expertise']
        }
        
        tone_scores = {}
        for tone, indicators in tone_indicators.items():
            score = sum(text_lower.count(indicator) for indicator in indicators)
            tone_scores[tone] = score
        
        return max(tone_scores, key=tone_scores.get) if tone_scores else "neutral"
    
    async def _analyze_voice(self, text: str) -> str:
        """Analyze content voice"""
        text_lower = text.lower()
        
        voice_indicators = {
            'authoritative': ['expert', 'proven', 'research', 'study', 'data', 'evidence'],
            'friendly': ['friend', 'hey', 'love', 'sweet', 'kind', 'warm', 'welcome'],
            'professional': ['business', 'industry', 'corporate', 'professional', 'expertise'],
            'conversational': ['you', 'your', 'we', 'us', 'let\'s', 'together', 'chat'],
            'inspirational': ['inspire', 'dream', 'achieve', 'believe', 'possible', 'success']
        }
        
        voice_scores = {}
        for voice, indicators in voice_indicators.items():
            score = sum(text_lower.count(indicator) for indicator in indicators)
            voice_scores[voice] = score
        
        return max(voice_scores, key=voice_scores.get) if voice_scores else "neutral"
    
    async def _determine_format(self, text: str) -> str:
        """Determine content format"""
        text_length = len(text)
        
        if text_length < 100:
            return "caption"
        elif text_length < 300:
            return "social_post"
        elif text_length < 1000:
            return "short_article"
        elif 'step' in text.lower() or 'tutorial' in text.lower():
            return "tutorial"
        elif text_length > 2000:
            return "long_article"
        else:
            return "medium_post"
    
    async def _analyze_complexity(self, text: str) -> str:
        """Analyze content complexity level"""
        words = text.split()
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Count complex words (more than 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complexity_ratio = complex_words / len(words) if words else 0
        
        # Determine complexity level
        if avg_word_length > 6 and complexity_ratio > 0.3:
            return "advanced"
        elif avg_word_length > 5 and complexity_ratio > 0.2:
            return "intermediate"
        else:
            return "beginner"
    
    async def _analyze_target_age_group(self, text: str) -> str:
        """Analyze target age group"""
        text_lower = text.lower()
        
        # Check for age-specific language patterns
        for age_group, profile in self.audience_profiles.items():
            language_patterns = profile.get('language_patterns', [])
            matches = sum(1 for pattern in language_patterns if pattern in text_lower)
            
            if matches > 0:
                return age_group
        
        # Default based on complexity and topic
        if 'professional' in text_lower or 'business' in text_lower:
            return "millennials"
        elif 'trend' in text_lower or 'viral' in text_lower:
            return "gen_z"
        else:
            return "general"
    
    async def _classify_target_audience(self, text: str, content_style: ContentStyle) -> AudienceTarget:
        """Classify target audience"""
        
        audience_scores = {}
        text_lower = text.lower()
        
        # Score each audience segment
        for audience, profile in self.audience_profiles.items():
            score = 0.0
            
            # Language pattern matching
            language_patterns = profile.get('language_patterns', [])
            for pattern in language_patterns:
                if pattern in text_lower:
                    score += 2.0
            
            # Interest matching
            interests = profile.get('interests', [])
            for interest in interests:
                if interest in text_lower:
                    score += 1.0
            
            # Content preference matching
            content_prefs = profile.get('content_preferences', [])
            if content_style.style_type in content_prefs:
                score += 1.5
            
            # Engagement trigger matching
            engagement_triggers = profile.get('engagement_triggers', [])
            for trigger in engagement_triggers:
                if trigger in text_lower:
                    score += 1.0
            
            audience_scores[audience] = score
        
        # Primary audience
        primary_audience = max(audience_scores, key=audience_scores.get) if audience_scores else "general"
        
        # Secondary audiences (with score > 3)
        secondary_audiences = [
            aud for aud, score in audience_scores.items() 
            if score > 3 and aud != primary_audience
        ]
        
        # Demographics
        primary_profile = self.audience_profiles.get(primary_audience, {})
        demographics = {
            'age_range': primary_profile.get('age_range'),
            'primary_platforms': primary_profile.get('platforms', []),
            'content_preferences': primary_profile.get('content_preferences', [])
        }
        
        # Extract interests from text
        detected_interests = []
        all_interests = []
        for profile in self.audience_profiles.values():
            all_interests.extend(profile.get('interests', []))
        
        for interest in set(all_interests):
            if interest in text_lower:
                detected_interests.append(interest)
        
        # Engagement patterns (simplified)
        engagement_patterns = {
            'likely_to_like': 0.7,
            'likely_to_comment': 0.6,
            'likely_to_share': 0.5,
            'likely_to_save': 0.4
        }
        
        # Platform preferences
        platform_preferences = primary_profile.get('platforms', [])
        
        return AudienceTarget(
            primary_audience=primary_audience,
            secondary_audiences=secondary_audiences,
            demographics=demographics,
            interests=detected_interests,
            engagement_patterns=engagement_patterns,
            platform_preferences=platform_preferences
        )
    
    async def _detect_content_intent(self, text: str) -> ContentIntent:
        """Detect content intent"""
        
        intent_scores = {}
        text_lower = text.lower()
        
        # Score each intent type
        for intent_type, intent_info in self.intent_patterns.items():
            score = 0.0
            
            # Indicator matching
            indicators = intent_info.get('indicators', [])
            for indicator in indicators:
                score += text_lower.count(indicator)
            
            # Pattern matching
            patterns = intent_info.get('patterns', [])
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            intent_scores[intent_type] = score
        
        # Primary intent
        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else "inform"
        
        # Secondary intents (with score > 1)
        secondary_intents = [
            intent for intent, score in intent_scores.items() 
            if score > 1 and intent != primary_intent
        ]
        
        # Intent strength
        intent_strength = {}
        total_score = sum(intent_scores.values())
        if total_score > 0:
            for intent, score in intent_scores.items():
                intent_strength[intent] = score / total_score
        
        # Detect call-to-action type
        primary_intent_info = self.intent_patterns.get(primary_intent, {})
        cta_types = primary_intent_info.get('cta_types', [])
        
        detected_cta = "none"
        for cta in cta_types:
            if cta in text_lower:
                detected_cta = cta
                break
        
        # Conversion goal
        conversion_goals = primary_intent_info.get('conversion_goals', [])
        conversion_goal = conversion_goals[0] if conversion_goals else "engagement"
        
        return ContentIntent(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            intent_strength=intent_strength,
            call_to_action_type=detected_cta,
            conversion_goal=conversion_goal
        )
    
    async def _optimize_for_platforms(self, text: str, content_category: ContentCategory, 
                                    content_style: ContentStyle, audience_target: AudienceTarget) -> PlatformOptimization:
        """Optimize content for different platforms"""
        
        platform_scores = {}
        
        # Score each platform
        for platform, characteristics in self.platform_characteristics.items():
            score = 0.0
            
            # Category optimization
            optimal_content_types = characteristics.get('optimal_content_types', [])
            if content_category.name in optimal_content_types:
                score += 3.0
            
            # Style optimization
            preferred_styles = characteristics.get('preferred_styles', [])
            if content_style.style_type in preferred_styles:
                score += 2.0
            
            # Audience fit
            audience_demographics = characteristics.get('audience_demographics', [])
            if audience_target.primary_audience in audience_demographics:
                score += 2.0
            
            # Format fit
            content_formats = characteristics.get('content_formats', [])
            if content_style.format in content_formats:
                score += 1.0
            
            platform_scores[platform] = min(1.0, score / 8.0)  # Normalize to 0-1
        
        # Best platforms (score > 0.5)
        best_platforms = [
            platform for platform, score in platform_scores.items() 
            if score > 0.5
        ]
        best_platforms.sort(key=lambda x: platform_scores[x], reverse=True)
        
        # Generate adaptation suggestions
        adaptation_suggestions = {}
        for platform in best_platforms[:3]:  # Top 3 platforms
            suggestions = []
            characteristics = self.platform_characteristics[platform]
            
            # Visual importance
            visual_importance = characteristics.get('visual_importance', 'medium')
            if visual_importance in ['high', 'very_high']:
                suggestions.append("Add high-quality visuals or video content")
            
            # Hashtag importance
            hashtag_importance = characteristics.get('hashtag_importance', 'medium')
            if hashtag_importance == 'high':
                suggestions.append("Include relevant hashtags for discoverability")
            
            # Platform-specific features
            engagement_features = characteristics.get('engagement_features', [])
            if 'shares' in engagement_features:
                suggestions.append("Encourage sharing with engaging content")
            
            adaptation_suggestions[platform] = suggestions
        
        # Format recommendations
        format_recommendations = {}
        for platform in best_platforms[:3]:
            characteristics = self.platform_characteristics[platform]
            content_formats = characteristics.get('content_formats', [])
            recommended_format = content_formats[0] if content_formats else "post"
            format_recommendations[platform] = recommended_format
        
        # Timing suggestions (simplified)
        timing_suggestions = {
            'instagram': 'Post between 11 AM - 1 PM or 7 PM - 9 PM',
            'tiktok': 'Post between 6 AM - 10 AM or 7 PM - 9 PM',
            'linkedin': 'Post between 8 AM - 10 AM on weekdays',
            'youtube': 'Upload between 2 PM - 4 PM on weekdays',
            'twitter': 'Tweet between 9 AM - 10 AM or 7 PM - 9 PM'
        }
        
        relevant_timing = {
            platform: timing_suggestions.get(platform, 'Optimal timing varies')
            for platform in best_platforms[:3]
        }
        
        return PlatformOptimization(
            best_platforms=best_platforms,
            platform_scores=platform_scores,
            adaptation_suggestions=adaptation_suggestions,
            format_recommendations=format_recommendations,
            timing_suggestions=relevant_timing
        )
    
    async def _generate_tags(self, text: str, content_category: ContentCategory, 
                           topic_classification: TopicClassification) -> List[str]:
        """Generate relevant tags for content"""
        tags = set()
        
        # Add category-based tags
        tags.add(content_category.name)
        tags.update(content_category.subcategories)
        tags.update(content_category.keywords[:5])  # Top 5 keywords
        
        # Add topic-based tags
        tags.add(topic_classification.primary_topic)
        tags.update(topic_classification.secondary_topics)
        
        # Add keywords from topic classification
        for topic_keywords in topic_classification.topic_keywords.values():
            tags.update(topic_keywords[:3])  # Top 3 keywords per topic
        
        # Extract hashtags from text
        hashtags = re.findall(r'#\w+', text)
        tags.update([tag[1:] for tag in hashtags])  # Remove # symbol
        
        # Extract key phrases using simple extraction
        key_phrases = await self._extract_key_phrases(text)
        tags.update(key_phrases[:5])  # Top 5 key phrases
        
        # Clean and filter tags
        cleaned_tags = []
        for tag in tags:
            # Clean tag
            clean_tag = re.sub(r'[^\w\s]', '', tag.lower().strip())
            clean_tag = re.sub(r'\s+', '_', clean_tag)
            
            # Filter valid tags
            if len(clean_tag) >= 3 and clean_tag not in ['the', 'and', 'for', 'are', 'but']:
                cleaned_tags.append(clean_tag)
        
        return list(set(cleaned_tags))[:20]  # Return up to 20 unique tags
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """
Extract key phrases from text"""
        # Simple key phrase extraction
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract 2-3 word phrases
        key_phrases = []
        for i in range(len(words) - 1):
            # 2-word phrases
            if i < len(words) - 1:
                phrase = f"{words[i]}_{words[i+1]}"
                if not any(word in stop_words for word in [words[i], words[i+1]]):
                    key_phrases.append(phrase)
            
            # 3-word phrases
            if i < len(words) - 2:
                phrase = f"{words[i]}_{words[i+1]}_{words[i+2]}"
                if not any(word in stop_words for word in [words[i], words[i+1], words[i+2]]):
                    key_phrases.append(phrase)
        
        # Count phrase frequency
        phrase_counts = Counter(key_phrases)
        
        # Return most frequent phrases
        return [phrase for phrase, count in phrase_counts.most_common(10)]
    
    async def _extract_metadata(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract metadata from content"""
        metadata = {
            'word_count': len(text.split()),
            'character_count': len(text),
            'sentence_count': len(text.split('.')),
            'paragraph_count': len(text.split('\n\n')),
            'hashtag_count': len(re.findall(r'#\w+', text)),
            'mention_count': len(re.findall(r'@\w+', text)),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+', text)),
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'reading_time_minutes': len(text.split()) / 200  # Average reading speed
        }
        
        # Add context metadata if provided
        if context:
            metadata.update({
                'source_platform': context.get('platform'),
                'author': context.get('author'),
                'timestamp': context.get('timestamp'),
                'engagement_data': context.get('engagement_data')
            })
        
        return metadata
    
    async def _calculate_overall_confidence(self, content_category: ContentCategory,
                                          topic_classification: TopicClassification,
                                          content_style: ContentStyle,
                                          content_intent: ContentIntent) -> float:
        """
Calculate overall classification confidence"""
        
        confidence_factors = []
        
        # Category confidence
        confidence_factors.append(content_category.confidence)
        
        # Topic confidence
        if topic_classification.topic_confidence:
            avg_topic_confidence = sum(topic_classification.topic_confidence.values()) / len(topic_classification.topic_confidence)
            confidence_factors.append(avg_topic_confidence)
        
        # Intent confidence
        if content_intent.intent_strength:
            max_intent_strength = max(content_intent.intent_strength.values())
            confidence_factors.append(max_intent_strength)
        
        # Style consistency (simplified measure)
        style_confidence = 0.8  # Default style confidence
        confidence_factors.append(style_confidence)
        
        # Overall confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _generate_request_id(self, text: str) -> str:
        """
Generate unique request ID"""
        import hashlib
        id_string = f"{text[:100]}{datetime.utcnow().isoformat()}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]

# Utility functions for quick classification
async def quick_classify(text: str) -> Dict[str, Any]:
    """Quick content classification"""
    classifier = AdvancedContentClassifier()
    result = await classifier.classify_content(text)
    
    return {
        'category': result.content_category.name,
        'primary_topic': result.topic_classification.primary_topic,
        'style': result.content_style.style_type,
        'target_audience': result.audience_target.primary_audience,
        'intent': result.content_intent.primary_intent,
        'best_platforms': result.platform_optimization.best_platforms[:3],
        'tags': result.tags[:10],
        'confidence': result.confidence_score
    }

async def classify_for_platform(text: str, target_platform: str) -> Dict[str, Any]:
    """
Classify content with platform-specific optimization"""
    classifier = AdvancedContentClassifier()
    result = await classifier.classify_content(text)
    
    platform_score = result.platform_optimization.platform_scores.get(target_platform, 0.0)
    adaptations = result.platform_optimization.adaptation_suggestions.get(target_platform, [])
    
    return {
        'classification': result,
        'platform_fit_score': platform_score,
        'optimization_suggestions': adaptations,
        'recommended_format': result.platform_optimization.format_recommendations.get(target_platform),
        'timing_suggestion': result.platform_optimization.timing_suggestions.get(target_platform)
    }
