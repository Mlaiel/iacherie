"""Creator Profiling Intelligence Engine
=====================================

Professional creator profiling and analysis system for IA Influencer Agent platform.
Provides comprehensive creator analysis, content style identification, audience
demographics, brand voice analysis, and intelligent collaboration matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
- Microservices Architect: Distributed systems and service orchestration
- IA Prompt Engineer: AI model fine-tuning and content analysis

CREATOR INTELLIGENCE:
This engine provides comprehensive creator profiling including content style analysis,
audience demographics, brand voice identification, collaboration potential assessment,
and intelligent creator-creator & creator-brand matching algorithms.
"""

import asyncio
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import re
from collections import Counter

# AI and ML libraries
try:
    import torch
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModel
    import openai
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    logging.warning(f"AI libraries not fully available: {e}")

# NLP libraries
try:
    import spacy
    from langdetect import detect, LangDetectError
    import textstat
except ImportError as e:
    logging.warning(f"NLP libraries not fully available: {e}")

try:
    from core.exceptions import ProfilingError, AnalysisError
except ImportError:
    # Fallback exception classes
    class ProfilingError(Exception): pass
    class AnalysisError(Exception): pass


class CreatorType(Enum):
    """Types of content creators"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"
    EDUCATOR = "educator"
    GAMER = "gamer"
    FITNESS = "fitness"
    CHEF = "chef"
    ARTIST = "artist"
    ENTREPRENEUR = "entrepreneur"
    JOURNALIST = "journalist"


class ContentStyle(Enum):
    """Content style categories"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    ARTISTIC = "artistic"
    TECHNICAL = "technical"
    LIFESTYLE = "lifestyle"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"


class AudienceSegment(Enum):
    """Audience demographic segments"""
    GEN_Z = "gen_z"          # 18-24
    MILLENNIALS = "millennials"  # 25-40
    GEN_X = "gen_x"          # 41-56
    BABY_BOOMERS = "baby_boomers"  # 57+
    TEENAGERS = "teenagers"   # 13-17
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    PARENTS = "parents"


class BrandVoiceType(Enum):
    """Brand voice personality types"""
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    SOPHISTICATED = "sophisticated"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    PROFESSIONAL = "professional"
    AUTHENTIC = "authentic"
    INNOVATIVE = "innovative"
    CARING = "caring"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    creator_id: str
    creator_name: str
    creator_type: CreatorType
    content_style: ContentStyle
    brand_voice: BrandVoiceType
    
    # Performance metrics
    follower_count: int = 0
    engagement_rate: float = 0.0
    average_views: int = 0
    content_frequency: str = "weekly"
    
    # Content analysis
    content_topics: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=list)
    posting_schedule: Dict[str, Any] = field(default_factory=dict)
    content_quality_score: float = 0.0
    
    # Audience analysis
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_interests: List[str] = field(default_factory=list)
    audience_engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Collaboration metrics
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    collaboration_score: float = 0.0
    partnership_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Platform presence
    platform_presence: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    cross_platform_consistency: float = 0.0
    
    # Profile metadata
    profile_created: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0


@dataclass
class CreatorAnalysisRequest:
    """Request for creator analysis"""
    creator_id: str
    content_samples: List[Dict[str, Any]] = field(default_factory=list)
    social_media_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    analysis_depth: str = "standard"  # basic, standard, comprehensive
    include_predictions: bool = True


@dataclass
class CollaborationMatch:
    """Creator collaboration match result"""
    creator_1_id: str
    creator_2_id: str
    compatibility_score: float
    match_type: str  # "creator-creator", "creator-brand"
    collaboration_potential: str  # "high", "medium", "low"
    recommended_collaboration_types: List[str] = field(default_factory=list)
    audience_overlap: float = 0.0
    content_synergy: float = 0.0
    brand_alignment: float = 0.0
    match_reasons: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)


class CreatorProfilingIntelligenceEngine:
    """
    Main Creator Profiling Intelligence Engine.
    
    This engine provides comprehensive creator analysis including:
    - Content style identification and analysis
    - Audience demographic profiling
    - Brand voice analysis and classification
    - Collaboration potential assessment
    - Creator-creator and creator-brand matching
    """
    
    def __init__(self):
        """Initialize the Creator Profiling Intelligence Engine"""
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        self.models = {}
        self.creator_profiles = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Analysis engines
        self.content_analyzer = ContentStyleAnalysisEngine()
        self.audience_analyzer = AudienceAnalysisEngine()
        self.brand_voice_analyzer = BrandVoiceAnalysisEngine()
        self.collaboration_matcher = CollaborationMatchingEngine()
        
        # Performance tracking
        self.profiling_metrics = {
            'total_profiles_created': 0,
            'total_analyses_performed': 0,
            'successful_matches': 0,
            'average_processing_time': 0.0
        }
    
    async def initialize(self):
        """Initialize the profiling engine and models"""
        try:
            self.logger.info("Initializing Creator Profiling Intelligence Engine...")
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Initialize analysis engines
            await self._initialize_analysis_engines()
            
            self.initialized = True
            self.logger.info("Creator Profiling Intelligence Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Engine initialization failed: {e}")
            raise ProfilingError(f"Engine initialization failed: {str(e)}")
    
    async def _initialize_ai_models(self):
        """Initialize AI models for creator analysis"""
        try:
            # Text classification models
            self.models['text_classifier'] = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Sentence embedding model
            try:
                self.models['sentence_transformer'] = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                self.models['sentence_transformer'] = None
            
            # Text vectorizer for similarity
            self.models['tfidf_vectorizer'] = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            self.logger.info("AI models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"AI model loading failed: {e}")
            self.models = {}
    
    async def _initialize_analysis_engines(self):
        """Initialize specialized analysis engines"""
        await self.content_analyzer.initialize()
        await self.audience_analyzer.initialize()
        await self.brand_voice_analyzer.initialize()
        await self.collaboration_matcher.initialize()
    
    async def analyze_creator(self, request: CreatorAnalysisRequest) -> CreatorProfile:
        """
        Perform comprehensive creator analysis and profiling.
        
        Args:
            request: Creator analysis request with content and data
            
        Returns:
            Comprehensive creator profile with insights
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                await self.initialize()
            
            self.logger.info(f"Starting creator analysis: {request.creator_id}")
            
            # Initialize creator profile
            profile = CreatorProfile(
                creator_id=request.creator_id,
                creator_name=request.social_media_data.get('name', 'Unknown Creator'),
                creator_type=CreatorType.INFLUENCER,  # Default, will be updated
                content_style=ContentStyle.CASUAL,    # Default, will be updated
                brand_voice=BrandVoiceType.FRIENDLY    # Default, will be updated
            )
            
            # Run analysis tasks concurrently
            analysis_tasks = []
            
            # Content style analysis
            if request.content_samples:
                content_task = self.content_analyzer.analyze_content_style(
                    request.content_samples
                )
                analysis_tasks.append(('content_style', content_task))
            
            # Audience analysis
            if request.social_media_data:
                audience_task = self.audience_analyzer.analyze_audience(
                    request.social_media_data, request.performance_metrics
                )
                analysis_tasks.append(('audience', audience_task))
            
            # Brand voice analysis
            if request.content_samples:
                brand_voice_task = self.brand_voice_analyzer.analyze_brand_voice(
                    request.content_samples
                )
                analysis_tasks.append(('brand_voice', brand_voice_task))
            
            # Execute analysis tasks
            if analysis_tasks:
                tasks = [task for _, task in analysis_tasks]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, (analysis_type, result) in enumerate(zip(
                    [name for name, _ in analysis_tasks], results
                )):
                    if isinstance(result, Exception):
                        self.logger.error(f"Analysis {analysis_type} failed: {result}")
                        continue
                    
                    if analysis_type == 'content_style':
                        await self._apply_content_analysis(profile, result)
                    elif analysis_type == 'audience':
                        await self._apply_audience_analysis(profile, result)
                    elif analysis_type == 'brand_voice':
                        await self._apply_brand_voice_analysis(profile, result)
            
            # Apply performance metrics
            await self._apply_performance_metrics(profile, request.performance_metrics)
            
            # Calculate collaboration score
            profile.collaboration_score = await self._calculate_collaboration_score(profile)
            
            # Calculate confidence score
            profile.confidence_score = await self._calculate_confidence_score(profile, request)
            
            # Update metadata
            profile.last_updated = datetime.utcnow()
            
            # Store profile
            self.creator_profiles[request.creator_id] = profile
            
            # Update metrics
            processing_time = time.time() - start_time
            await self._update_metrics(processing_time, True)
            
            self.logger.info(f"Creator analysis completed: {request.creator_id} in {processing_time:.2f}s")
            return profile
            
        except Exception as e:
            processing_time = time.time() - start_time
            await self._update_metrics(processing_time, False)
            self.logger.error(f"Creator analysis failed: {request.creator_id} - {str(e)}")
            raise AnalysisError(f"Creator analysis failed: {str(e)}")
    
    async def find_collaboration_matches(self, creator_id: str, 
                                       match_type: str = "creator-creator",
                                       min_compatibility: float = 0.7,
                                       max_results: int = 10) -> List[CollaborationMatch]:
        """
        Find potential collaboration matches for a creator.
        
        Args:
            creator_id: ID of the creator to find matches for
            match_type: Type of match ("creator-creator" or "creator-brand")
            min_compatibility: Minimum compatibility score threshold
            max_results: Maximum number of results to return
            
        Returns:
            List of collaboration matches sorted by compatibility
        """
        try:
            if creator_id not in self.creator_profiles:
                raise ProfilingError(f"Creator profile not found: {creator_id}")
            
            creator_profile = self.creator_profiles[creator_id]
            matches = []
            
            # Find matches based on type
            if match_type == "creator-creator":
                matches = await self.collaboration_matcher.find_creator_matches(
                    creator_profile, self.creator_profiles, min_compatibility
                )
            elif match_type == "creator-brand":
                # For creator-brand matching, we'd need brand profiles
                # This is a placeholder implementation
                matches = await self.collaboration_matcher.find_brand_matches(
                    creator_profile, min_compatibility
                )
            
            # Sort by compatibility score and limit results
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches[:max_results]
            
        except Exception as e:
            self.logger.error(f"Collaboration matching failed: {str(e)}")
            raise
    
    async def batch_analyze_creators(self, requests: List[CreatorAnalysisRequest]) -> List[CreatorProfile]:
        """
        Perform batch analysis of multiple creators.
        
        Args:
            requests: List of creator analysis requests
            
        Returns:
            List of creator profiles
        """
        try:
            self.logger.info(f"Starting batch creator analysis: {len(requests)} creators")
            
            # Process requests concurrently with semaphore for resource control
            semaphore = asyncio.Semaphore(3)  # Limit concurrent analyses
            
            async def analyze_single(request):
                async with semaphore:
                    return await self.analyze_creator(request)
            
            tasks = [analyze_single(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            profiles = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch analysis error for creator {i}: {result}")
                    continue
                profiles.append(result)
            
            self.logger.info(f"Batch creator analysis completed: {len(profiles)} profiles")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {e}")
            raise
    
    async def _apply_content_analysis(self, profile: CreatorProfile, analysis_result: Dict[str, Any]):
        """Apply content style analysis results to profile"""
        if 'content_style' in analysis_result:
            try:
                profile.content_style = ContentStyle(analysis_result['content_style'])
            except ValueError:
                profile.content_style = ContentStyle.CASUAL
        
        if 'creator_type' in analysis_result:
            try:
                profile.creator_type = CreatorType(analysis_result['creator_type'])
            except ValueError:
                profile.creator_type = CreatorType.INFLUENCER
        
        if 'content_topics' in analysis_result:
            profile.content_topics = analysis_result['content_topics']
        
        if 'content_quality_score' in analysis_result:
            profile.content_quality_score = analysis_result['content_quality_score']
        
        if 'posting_schedule' in analysis_result:
            profile.posting_schedule = analysis_result['posting_schedule']
    
    async def _apply_audience_analysis(self, profile: CreatorProfile, analysis_result: Dict[str, Any]):
        """Apply audience analysis results to profile"""
        if 'demographics' in analysis_result:
            profile.audience_demographics = analysis_result['demographics']
        
        if 'interests' in analysis_result:
            profile.audience_interests = analysis_result['interests']
        
        if 'engagement_patterns' in analysis_result:
            profile.audience_engagement_patterns = analysis_result['engagement_patterns']
        
        if 'follower_count' in analysis_result:
            profile.follower_count = analysis_result['follower_count']
        
        if 'engagement_rate' in analysis_result:
            profile.engagement_rate = analysis_result['engagement_rate']
    
    async def _apply_brand_voice_analysis(self, profile: CreatorProfile, analysis_result: Dict[str, Any]):
        """Apply brand voice analysis results to profile"""
        if 'brand_voice' in analysis_result:
            try:
                profile.brand_voice = BrandVoiceType(analysis_result['brand_voice'])
            except ValueError:
                profile.brand_voice = BrandVoiceType.FRIENDLY
        
        if 'language_preferences' in analysis_result:
            profile.language_preferences = analysis_result['language_preferences']
    
    async def _apply_performance_metrics(self, profile: CreatorProfile, metrics: Dict[str, Any]):
        """Apply performance metrics to profile"""
        if 'average_views' in metrics:
            profile.average_views = metrics['average_views']
        
        if 'content_frequency' in metrics:
            profile.content_frequency = metrics['content_frequency']
        
        if 'platform_presence' in metrics:
            profile.platform_presence = metrics['platform_presence']
    
    async def _calculate_collaboration_score(self, profile: CreatorProfile) -> float:
        """Calculate collaboration score based on profile factors"""
        score = 0.0
        
        # Base score from engagement rate
        score += min(profile.engagement_rate * 10, 0.3)
        
        # Content quality factor
        score += profile.content_quality_score * 0.2
        
        # Follower count factor (normalized)
        follower_factor = min(profile.follower_count / 100000, 1.0) * 0.2
        score += follower_factor
        
        # Content consistency factor
        if profile.posting_schedule:
            score += 0.15
        
        # Cross-platform presence factor
        platform_count = len(profile.platform_presence)
        platform_factor = min(platform_count / 5, 1.0) * 0.15
        score += platform_factor
        
        return min(score, 1.0)
    
    async def _calculate_confidence_score(self, profile: CreatorProfile, 
                                        request: CreatorAnalysisRequest) -> float:
        """Calculate confidence score for the profile analysis"""
        score = 0.0
        
        # Data availability factors
        if request.content_samples:
            score += 0.3
        
        if request.social_media_data:
            score += 0.25
        
        if request.performance_metrics:
            score += 0.25
        
        if request.collaboration_history:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics"""
        self.profiling_metrics['total_analyses_performed'] += 1
        
        if success:
            self.profiling_metrics['total_profiles_created'] += 1
        
        # Update average processing time
        total_time = (self.profiling_metrics['average_processing_time'] * 
                     (self.profiling_metrics['total_analyses_performed'] - 1))
        self.profiling_metrics['average_processing_time'] = (
            (total_time + processing_time) / self.profiling_metrics['total_analyses_performed']
        )
    
    def get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get stored creator profile by ID"""
        return self.creator_profiles.get(creator_id)
    
    def get_all_profiles(self) -> Dict[str, CreatorProfile]:
        """Get all stored creator profiles"""
        return self.creator_profiles.copy()
    
    def get_profiling_capabilities(self) -> Dict[str, Any]:
        """Get profiling capabilities and metrics"""
        return {
            'creator_types': [creator_type.value for creator_type in CreatorType],
            'content_styles': [style.value for style in ContentStyle],
            'brand_voices': [voice.value for voice in BrandVoiceType],
            'audience_segments': [segment.value for segment in AudienceSegment],
            'total_profiles': len(self.creator_profiles),
            'performance_metrics': self.profiling_metrics.copy(),
            'initialized': self.initialized
        }


class ContentStyleAnalysisEngine:
    """Specialized engine for content style analysis"""
    
    async def initialize(self):
        """Initialize content style analysis"""
        self.style_keywords = {
            ContentStyle.PROFESSIONAL: ['business', 'corporate', 'formal', 'industry', 'expert'],
            ContentStyle.CASUAL: ['casual', 'everyday', 'simple', 'relaxed', 'friendly'],
            ContentStyle.HUMOROUS: ['funny', 'comedy', 'humor', 'joke', 'laugh', 'hilarious'],
            ContentStyle.EDUCATIONAL: ['learn', 'tutorial', 'guide', 'education', 'teaching'],
            ContentStyle.INSPIRATIONAL: ['inspire', 'motivate', 'success', 'achievement', 'dream'],
            ContentStyle.ARTISTIC: ['art', 'creative', 'design', 'aesthetic', 'visual'],
            ContentStyle.TECHNICAL: ['technical', 'engineering', 'programming', 'tech', 'code']
        }
        
        self.creator_type_keywords = {
            CreatorType.MUSICIAN: ['music', 'song', 'artist', 'album', 'concert', 'band'],
            CreatorType.PHOTOGRAPHER: ['photo', 'camera', 'photography', 'image', 'portrait'],
            CreatorType.BLOGGER: ['blog', 'write', 'article', 'content', 'writing'],
            CreatorType.COMEDIAN: ['comedy', 'funny', 'joke', 'humor', 'standup'],
            CreatorType.EDUCATOR: ['teach', 'education', 'lesson', 'course', 'learning'],
            CreatorType.GAMER: ['game', 'gaming', 'player', 'stream', 'esports'],
            CreatorType.FITNESS: ['fitness', 'workout', 'gym', 'health', 'exercise'],
            CreatorType.CHEF: ['cooking', 'recipe', 'food', 'chef', 'kitchen']
        }
    
    async def analyze_content_style(self, content_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content style from samples"""
        try:
            # Extract text content from samples
            all_text = ""
            for sample in content_samples:
                if 'text' in sample:
                    all_text += sample['text'] + " "
                if 'title' in sample:
                    all_text += sample['title'] + " "
                if 'description' in sample:
                    all_text += sample['description'] + " "
            
            if not all_text.strip():
                return self._get_default_analysis()
            
            # Analyze content style
            content_style = await self._classify_content_style(all_text)
            creator_type = await self._classify_creator_type(all_text)
            
            # Extract topics
            topics = await self._extract_topics(all_text)
            
            # Calculate quality score
            quality_score = await self._calculate_content_quality(content_samples)
            
            # Analyze posting patterns
            posting_schedule = await self._analyze_posting_schedule(content_samples)
            
            return {
                'content_style': content_style.value,
                'creator_type': creator_type.value,
                'content_topics': topics,
                'content_quality_score': quality_score,
                'posting_schedule': posting_schedule,
                'analysis_confidence': 0.8
            }
            
        except Exception as e:
            return self._get_default_analysis()
    
    async def _classify_content_style(self, text: str) -> ContentStyle:
        """Classify content style based on text analysis"""
        text_lower = text.lower()
        style_scores = {}
        
        for style, keywords in self.style_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            style_scores[style] = score
        
        if style_scores:
            best_style = max(style_scores, key=style_scores.get)
            if style_scores[best_style] > 0:
                return best_style
        
        return ContentStyle.CASUAL  # Default
    
    async def _classify_creator_type(self, text: str) -> CreatorType:
        """Classify creator type based on content analysis"""
        text_lower = text.lower()
        type_scores = {}
        
        for creator_type, keywords in self.creator_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            type_scores[creator_type] = score
        
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return CreatorType.INFLUENCER  # Default
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from content"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        topics = []
        
        for word, freq in word_freq.most_common(20):
            if word not in stop_words and len(word) > 3 and freq > 1:
                topics.append(word)
        
        return topics[:10]
    
    async def _calculate_content_quality(self, content_samples: List[Dict[str, Any]]) -> float:
        """Calculate content quality score"""
        if not content_samples:
            return 0.5
        
        total_score = 0
        count = 0
        
        for sample in content_samples:
            score = 0.5  # Base score
            
            # Check for multimedia content
            if any(key in sample for key in ['image', 'video', 'audio']):
                score += 0.2
            
            # Check text quality
            if 'text' in sample and sample['text']:
                text_length = len(sample['text'])
                if 50 <= text_length <= 1000:
                    score += 0.2
                elif text_length > 1000:
                    score += 0.1
            
            # Check for engagement metrics
            if 'likes' in sample or 'shares' in sample or 'comments' in sample:
                score += 0.1
            
            total_score += min(score, 1.0)
            count += 1
        
        return total_score / count if count > 0 else 0.5
    
    async def _analyze_posting_schedule(self, content_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze posting schedule patterns"""
        if not content_samples:
            return {}
        
        # Extract timestamps if available
        timestamps = []
        for sample in content_samples:
            if 'timestamp' in sample:
                try:
                    timestamp = datetime.fromisoformat(sample['timestamp'])
                    timestamps.append(timestamp)
                except:
                    continue
        
        if len(timestamps) < 2:
            return {'frequency': 'unknown', 'consistency': 0.5}
        
        # Analyze posting frequency
        timestamps.sort()
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).days
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval <= 1:
                frequency = 'daily'
            elif avg_interval <= 7:
                frequency = 'weekly'
            elif avg_interval <= 30:
                frequency = 'monthly'
            else:
                frequency = 'irregular'
        else:
            frequency = 'unknown'
        
        # Calculate consistency score
        if intervals:
            variance = np.var(intervals)
            consistency = max(0, 1 - (variance / 100))  # Normalize variance
        else:
            consistency = 0.5
        
        return {
            'frequency': frequency,
            'consistency': consistency,
            'avg_interval_days': avg_interval if intervals else 0,
            'total_posts_analyzed': len(content_samples)
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis result"""
        return {
            'content_style': ContentStyle.CASUAL.value,
            'creator_type': CreatorType.INFLUENCER.value,
            'content_topics': ['general', 'content'],
            'content_quality_score': 0.5,
            'posting_schedule': {'frequency': 'unknown', 'consistency': 0.5},
            'analysis_confidence': 0.3
        }


class AudienceAnalysisEngine:
    """Specialized engine for audience analysis"""
    
    async def initialize(self):
        """Initialize audience analysis"""
        pass
    
    async def analyze_audience(self, social_media_data: Dict[str, Any], 
                             performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience demographics and behavior"""
        try:
            # Extract follower data
            follower_count = social_media_data.get('followers', 0)
            engagement_rate = performance_metrics.get('engagement_rate', 0.0)
            
            # Analyze demographics (simplified)
            demographics = await self._analyze_demographics(social_media_data)
            
            # Analyze interests
            interests = await self._analyze_interests(social_media_data)
            
            # Analyze engagement patterns
            engagement_patterns = await self._analyze_engagement_patterns(performance_metrics)
            
            return {
                'follower_count': follower_count,
                'engagement_rate': engagement_rate,
                'demographics': demographics,
                'interests': interests,
                'engagement_patterns': engagement_patterns
            }
            
        except Exception as e:
            return self._get_default_audience_analysis()
    
    async def _analyze_demographics(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience demographics"""
        # Simplified demographic analysis
        return {
            'age_groups': {
                '18-24': 0.3,
                '25-34': 0.4,
                '35-44': 0.2,
                '45+': 0.1
            },
            'gender_distribution': {
                'female': 0.55,
                'male': 0.43,
                'other': 0.02
            },
            'top_locations': ['United States', 'United Kingdom', 'Canada'],
            'primary_language': 'English'
        }
    
    async def _analyze_interests(self, social_data: Dict[str, Any]) -> List[str]:
        """Analyze audience interests"""
        # Extract interests from social media data
        interests = social_data.get('audience_interests', [])
        
        if not interests:
            # Default interests based on general patterns
            interests = ['technology', 'entertainment', 'lifestyle', 'social_media']
        
        return interests[:10]
    
    async def _analyze_engagement_patterns(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience engagement patterns"""
        return {
            'peak_engagement_hours': ['19:00-21:00', '12:00-14:00'],
            'best_content_types': ['video', 'image', 'text'],
            'engagement_trends': 'stable',
            'audience_growth_rate': metrics.get('growth_rate', 0.05)
        }
    
    def _get_default_audience_analysis(self) -> Dict[str, Any]:
        """Get default audience analysis"""
        return {
            'follower_count': 0,
            'engagement_rate': 0.03,
            'demographics': {
                'age_groups': {'18-34': 0.6, '35+': 0.4},
                'gender_distribution': {'female': 0.5, 'male': 0.5}
            },
            'interests': ['general'],
            'engagement_patterns': {'peak_hours': ['12:00-14:00']}
        }


class BrandVoiceAnalysisEngine:
    """Specialized engine for brand voice analysis"""
    
    async def initialize(self):
        """Initialize brand voice analysis"""
        self.voice_indicators = {
            BrandVoiceType.FRIENDLY: ['thanks', 'please', 'love', 'amazing', 'awesome'],
            BrandVoiceType.PROFESSIONAL: ['deliver', 'expertise', 'solution', 'professional', 'quality'],
            BrandVoiceType.PLAYFUL: ['fun', 'exciting', 'cool', 'wow', 'awesome', 'amazing'],
            BrandVoiceType.HUMOROUS: ['funny', 'lol', 'haha', 'joke', 'hilarious'],
            BrandVoiceType.INSPIRATIONAL: ['inspire', 'dream', 'achieve', 'success', 'believe']
        }
    
    async def analyze_brand_voice(self, content_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze brand voice from content samples"""
        try:
            # Extract text content
            all_text = ""
            for sample in content_samples:
                if 'text' in sample:
                    all_text += sample['text'] + " "
                if 'caption' in sample:
                    all_text += sample['caption'] + " "
            
            if not all_text.strip():
                return self._get_default_voice_analysis()
            
            # Classify brand voice
            brand_voice = await self._classify_brand_voice(all_text)
            
            # Detect languages
            languages = await self._detect_languages(all_text)
            
            return {
                'brand_voice': brand_voice.value,
                'language_preferences': languages,
                'voice_confidence': 0.75,
                'voice_characteristics': await self._analyze_voice_characteristics(all_text)
            }
            
        except Exception as e:
            return self._get_default_voice_analysis()
    
    async def _classify_brand_voice(self, text: str) -> BrandVoiceType:
        """Classify brand voice based on text analysis"""
        text_lower = text.lower()
        voice_scores = {}
        
        for voice_type, indicators in self.voice_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            voice_scores[voice_type] = score
        
        if voice_scores:
            best_voice = max(voice_scores, key=voice_scores.get)
            if voice_scores[best_voice] > 0:
                return best_voice
        
        return BrandVoiceType.FRIENDLY  # Default
    
    async def _detect_languages(self, text: str) -> List[str]:
        """Detect languages in content"""
        try:
            # Simple language detection
            detected_lang = detect(text)
            return [detected_lang]
        except:
            return ['en']  # Default to English
    
    async def _analyze_voice_characteristics(self, text: str) -> Dict[str, Any]:
        """Analyze detailed voice characteristics"""
        return {
            'tone': 'positive',
            'formality': 'casual',
            'emotional_intensity': 'medium',
            'use_of_emojis': '😊' in text or '🎉' in text,
            'sentence_length': 'medium'
        }
    
    def _get_default_voice_analysis(self) -> Dict[str, Any]:
        """Get default voice analysis"""
        return {
            'brand_voice': BrandVoiceType.FRIENDLY.value,
            'language_preferences': ['en'],
            'voice_confidence': 0.5,
            'voice_characteristics': {
                'tone': 'neutral',
                'formality': 'casual',
                'emotional_intensity': 'medium'
            }
        }


class CollaborationMatchingEngine:
    """Specialized engine for collaboration matching"""
    
    async def initialize(self):
        """Initialize collaboration matching"""
        pass
    
    async def find_creator_matches(self, target_creator: CreatorProfile,
                                 all_profiles: Dict[str, CreatorProfile],
                                 min_compatibility: float) -> List[CollaborationMatch]:
        """Find creator collaboration matches"""
        matches = []
        
        for creator_id, profile in all_profiles.items():
            if creator_id == target_creator.creator_id:
                continue
            
            # Calculate compatibility
            compatibility = await self._calculate_creator_compatibility(target_creator, profile)
            
            if compatibility >= min_compatibility:
                match = CollaborationMatch(
                    creator_1_id=target_creator.creator_id,
                    creator_2_id=creator_id,
                    compatibility_score=compatibility,
                    match_type="creator-creator",
                    collaboration_potential=self._get_collaboration_potential(compatibility)
                )
                
                # Add detailed analysis
                await self._analyze_collaboration_potential(match, target_creator, profile)
                matches.append(match)
        
        return matches
    
    async def find_brand_matches(self, creator_profile: CreatorProfile,
                               min_compatibility: float) -> List[CollaborationMatch]:
        """Find brand collaboration matches (placeholder)"""
        # This would integrate with a brand database
        # For now, return empty list
        return []
    
    async def _calculate_creator_compatibility(self, creator1: CreatorProfile, 
                                            creator2: CreatorProfile) -> float:
        """Calculate compatibility score between two creators"""
        score = 0.0
        
        # Content style similarity
        if creator1.content_style == creator2.content_style:
            score += 0.2
        elif self._are_compatible_styles(creator1.content_style, creator2.content_style):
            score += 0.1
        
        # Brand voice compatibility
        if creator1.brand_voice == creator2.brand_voice:
            score += 0.15
        elif self._are_compatible_voices(creator1.brand_voice, creator2.brand_voice):
            score += 0.1
        
        # Audience overlap
        audience_overlap = await self._calculate_audience_overlap(creator1, creator2)
        score += audience_overlap * 0.25
        
        # Content topics similarity
        topic_similarity = await self._calculate_topic_similarity(creator1, creator2)
        score += topic_similarity * 0.2
        
        # Performance compatibility
        performance_compatibility = await self._calculate_performance_compatibility(creator1, creator2)
        score += performance_compatibility * 0.2
        
        return min(score, 1.0)
    
    def _are_compatible_styles(self, style1: ContentStyle, style2: ContentStyle) -> bool:
        """Check if content styles are compatible"""
        compatible_pairs = [
            (ContentStyle.EDUCATIONAL, ContentStyle.PROFESSIONAL),
            (ContentStyle.HUMOROUS, ContentStyle.ENTERTAINMENT),
            (ContentStyle.INSPIRATIONAL, ContentStyle.LIFESTYLE),
            (ContentStyle.ARTISTIC, ContentStyle.LIFESTYLE)
        ]
        
        return (style1, style2) in compatible_pairs or (style2, style1) in compatible_pairs
    
    def _are_compatible_voices(self, voice1: BrandVoiceType, voice2: BrandVoiceType) -> bool:
        """Check if brand voices are compatible"""
        compatible_pairs = [
            (BrandVoiceType.FRIENDLY, BrandVoiceType.PLAYFUL),
            (BrandVoiceType.PROFESSIONAL, BrandVoiceType.AUTHORITATIVE),
            (BrandVoiceType.INSPIRATIONAL, BrandVoiceType.CARING)
        ]
        
        return (voice1, voice2) in compatible_pairs or (voice2, voice1) in compatible_pairs
    
    async def _calculate_audience_overlap(self, creator1: CreatorProfile, 
                                        creator2: CreatorProfile) -> float:
        """Calculate audience overlap between creators"""
        # Simple audience overlap calculation
        interests1 = set(creator1.audience_interests)
        interests2 = set(creator2.audience_interests)
        
        if not interests1 or not interests2:
            return 0.5  # Default moderate overlap
        
        overlap = len(interests1.intersection(interests2))
        total = len(interests1.union(interests2))
        
        return overlap / total if total > 0 else 0.0
    
    async def _calculate_topic_similarity(self, creator1: CreatorProfile, 
                                        creator2: CreatorProfile) -> float:
        """Calculate content topic similarity"""
        topics1 = set(creator1.content_topics)
        topics2 = set(creator2.content_topics)
        
        if not topics1 or not topics2:
            return 0.3  # Default low similarity
        
        overlap = len(topics1.intersection(topics2))
        total = len(topics1.union(topics2))
        
        return overlap / total if total > 0 else 0.0
    
    async def _calculate_performance_compatibility(self, creator1: CreatorProfile, 
                                                 creator2: CreatorProfile) -> float:
        """Calculate performance compatibility"""
        # Consider follower count ratio and engagement rates
        follower_ratio = min(creator1.follower_count, creator2.follower_count) / max(creator1.follower_count, creator2.follower_count, 1)
        engagement_avg = (creator1.engagement_rate + creator2.engagement_rate) / 2
        
        # High follower ratio and good engagement indicate compatibility
        return (follower_ratio * 0.5) + min(engagement_avg * 10, 0.5)
    
    def _get_collaboration_potential(self, compatibility_score: float) -> str:
        """Get collaboration potential level"""
        if compatibility_score >= 0.8:
            return "high"
        elif compatibility_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    async def _analyze_collaboration_potential(self, match: CollaborationMatch,
                                             creator1: CreatorProfile, creator2: CreatorProfile):
        """Analyze and add detailed collaboration insights"""
        # Recommended collaboration types
        match.recommended_collaboration_types = await self._suggest_collaboration_types(creator1, creator2)
        
        # Calculate specific scores
        match.audience_overlap = await self._calculate_audience_overlap(creator1, creator2)
        match.content_synergy = await self._calculate_topic_similarity(creator1, creator2)
        match.brand_alignment = 0.8 if creator1.brand_voice == creator2.brand_voice else 0.6
        
        # Generate match reasons
        match.match_reasons = await self._generate_match_reasons(creator1, creator2, match)
        
        # Identify potential challenges
        match.potential_challenges = await self._identify_challenges(creator1, creator2)
    
    async def _suggest_collaboration_types(self, creator1: CreatorProfile, 
                                         creator2: CreatorProfile) -> List[str]:
        """Suggest types of collaboration"""
        collaborations = []
        
        # Based on creator types
        if creator1.creator_type == creator2.creator_type:
            collaborations.append("Joint content series")
            collaborations.append("Cross-promotion")
        
        if creator1.creator_type == CreatorType.MUSICIAN and creator2.creator_type == CreatorType.PHOTOGRAPHER:
            collaborations.append("Music video collaboration")
            collaborations.append("Album artwork project")
        
        if creator1.content_style == ContentStyle.EDUCATIONAL:
            collaborations.append("Educational series")
            collaborations.append("Tutorial collaboration")
        
        # General collaborations
        collaborations.extend([
            "Guest appearance",
            "Social media takeover",
            "Joint giveaway",
            "Challenge collaboration"
        ])
        
        return collaborations[:5]  # Return top 5 suggestions
    
    async def _generate_match_reasons(self, creator1: CreatorProfile, creator2: CreatorProfile,
                                    match: CollaborationMatch) -> List[str]:
        """Generate reasons for the match"""
        reasons = []
        
        if match.compatibility_score >= 0.8:
            reasons.append("High overall compatibility score")
        
        if creator1.content_style == creator2.content_style:
            reasons.append("Similar content styles")
        
        if match.audience_overlap >= 0.6:
            reasons.append("Significant audience overlap")
        
        if creator1.brand_voice == creator2.brand_voice:
            reasons.append("Compatible brand voices")
        
        if abs(creator1.engagement_rate - creator2.engagement_rate) < 0.02:
            reasons.append("Similar engagement rates")
        
        return reasons
    
    async def _identify_challenges(self, creator1: CreatorProfile, 
                                 creator2: CreatorProfile) -> List[str]:
        """Identify potential collaboration challenges"""
        challenges = []
        
        # Follower count disparity
        follower_ratio = creator1.follower_count / max(creator2.follower_count, 1)
        if follower_ratio > 10 or follower_ratio < 0.1:
            challenges.append("Significant follower count disparity")
        
        # Different content styles
        if creator1.content_style != creator2.content_style and not self._are_compatible_styles(creator1.content_style, creator2.content_style):
            challenges.append("Different content styles may require coordination")
        
        # Different posting schedules
        if creator1.posting_schedule.get('frequency') != creator2.posting_schedule.get('frequency'):
            challenges.append("Different posting frequencies")
        
        # Language differences
        if not set(creator1.language_preferences).intersection(set(creator2.language_preferences)):
            challenges.append("Different language preferences")
        
        return challenges


# Export main components
__all__ = [
    'CreatorProfilingIntelligenceEngine',
    'CreatorProfile',
    'CreatorAnalysisRequest',
    'CollaborationMatch',
    'CreatorType',
    'ContentStyle',
    'BrandVoiceType',
    'AudienceSegment',
    'ContentStyleAnalysisEngine',
    'AudienceAnalysisEngine',
    'BrandVoiceAnalysisEngine',
    'CollaborationMatchingEngine'
]