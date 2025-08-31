"""
Brand Voice Engine - Enterprise Brand Consistency & Voice Matching System

Ultra-advanced brand voice analysis, matching, and consistency management system
for maintaining authentic brand identity across all content creation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
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
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import Counter, defaultdict

# NLP and ML libraries
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import textdistance

# AI/ML models
from transformers import (
    AutoTokenizer, AutoModel, pipeline,
    RobertaTokenizer, RobertaForSequenceClassification
)
import torch
import torch.nn.functional as F

# FastAPI and database
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func, and_, desc
from pydantic import BaseModel, Field
from fastapi import HTTPException

# Internal imports
try:
    from core.database import get_async_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_async_session = DatabaseManager
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.cache import CacheManager
from ...models.content import Content, ContentType
from ...models.users import User, CreatorProfile
from ...utils.performance import PerformanceMonitor
from ...ai.llm_engine import UnifiedLLMEngine

logger = logging.getLogger(__name__)
settings = get_settings()

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass


class VoiceCharacteristic(str, Enum):
    """Brand voice characteristics"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BOLD = "bold"
    WARM = "warm"
    CONFIDENT = "confident"
    PLAYFUL = "playful"


class VoiceTone(str, Enum):
    """Voice tone categories"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
    URGENT = "urgent"
    ENCOURAGING = "encouraging"
    SERIOUS = "serious"


class WritingStyle(str, Enum):
    """Writing style patterns"""
    FORMAL = "formal"
    INFORMAL = "informal"
    ACADEMIC = "academic"
    JOURNALISTIC = "journalistic"
    STORYTELLING = "storytelling"
    INSTRUCTIONAL = "instructional"
    PERSUASIVE = "persuasive"
    DESCRIPTIVE = "descriptive"


@dataclass
class VoiceMetrics:
    """Comprehensive voice analysis metrics"""
    # Linguistic metrics
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    readability_score: float = 0.0
    vocabulary_diversity: float = 0.0
    
    # Tone metrics
    sentiment_scores: Dict[str, float] = field(default_factory=dict)
    emotion_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Style metrics
    formality_score: float = 0.0
    complexity_score: float = 0.0
    engagement_score: float = 0.0
    
    # Content patterns
    common_words: List[Tuple[str, int]] = field(default_factory=list)
    common_phrases: List[Tuple[str, int]] = field(default_factory=list)
    pos_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Personality indicators
    personality_traits: Dict[str, float] = field(default_factory=dict)
    communication_style: Dict[str, float] = field(default_factory=dict)


@dataclass
class BrandVoiceProfile:
    """Complete brand voice profile"""
    user_id: str
    brand_name: str
    voice_characteristics: List[VoiceCharacteristic]
    dominant_tone: VoiceTone
    writing_style: WritingStyle
    voice_metrics: VoiceMetrics
    consistency_score: float
    content_samples: int
    last_analysis: datetime
    voice_guidelines: Dict[str, Any] = field(default_factory=dict)
    target_audience: Optional[str] = None
    industry_context: Optional[str] = None


class BrandVoiceEngine:
    """Enterprise brand voice analysis and matching engine"""
    
    def __init__(self):
        self.settings = get_settings()
        self.performance_monitor = PerformanceMonitor("brand_voice_engine")
        self.cache_manager = CacheManager("brand_voice")
        self.llm_engine = UnifiedLLMEngine()
        
        # Initialize NLP models
        self._initialize_nlp_models()
        
        # Voice analysis components
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        
        # Voice pattern cache
        self._voice_patterns_cache = {}
        self._consistency_cache = {}
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for voice analysis"""



        try:
            # Language model for embeddings
            self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            
            # Emotion analysis model
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # SpaCy for linguistic analysis
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("SpaCy English model not found. Some features may be limited.")
                self.nlp = None
            
            logger.info("Brand voice NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            raise
    
    async def analyze_user_voice(
        self,
        user_id: str,
        sample_count: int = 50,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze user's brand voice from their content history"""
        
        async with self.performance_monitor.track_operation("voice_analysis"):
            try:
                # Get user's content samples
                content_samples = await self._get_user_content_samples(
                    user_id, sample_count, db
                )
                
                if not content_samples:
                    return {
                        "error": "No content found for voice analysis",
                        "user_id": user_id
                    }
                
                # Extract text content
                text_samples = []
                for content in content_samples:
                    text = self._extract_text_content(content)
                    if text and len(text.strip()) > 50:  # Minimum text length
                        text_samples.append(text)
                
                if not text_samples:
                    return {
                        "error": "No suitable text content found",
                        "user_id": user_id
                    }
                
                # Perform comprehensive voice analysis
                voice_metrics = await self._analyze_voice_metrics(text_samples)
                voice_characteristics = await self._identify_voice_characteristics(text_samples, voice_metrics)
                consistency_score = await self._calculate_consistency_score(text_samples)
                
                # Create brand voice profile
                brand_profile = BrandVoiceProfile(
                    user_id=user_id,
                    brand_name=f"User_{user_id}_Brand",
                    voice_characteristics=voice_characteristics,
                    dominant_tone=self._determine_dominant_tone(voice_metrics),
                    writing_style=self._determine_writing_style(voice_metrics),
                    voice_metrics=voice_metrics,
                    consistency_score=consistency_score,
                    content_samples=len(text_samples),
                    last_analysis=datetime.now(timezone.utc)
                )
                
                # Store voice profile
                await self._store_voice_profile(brand_profile, db)
                
                # Generate actionable recommendations
                recommendations = await self._generate_voice_recommendations(brand_profile)
                
                return {
                    "voice_profile": self._serialize_voice_profile(brand_profile),
                    "consistency_score": consistency_score,
                    "recommendations": recommendations,
                    "characteristics": voice_characteristics,
                    "sample_count": len(text_samples),
                    "analysis_date": brand_profile.last_analysis.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Voice analysis error for user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")
    
    async def match_brand_voice(
        self,
        user_id: str,
        content_data: Dict[str, Any],
        brand_guidelines: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Match content against user's brand voice"""
        
        async with self.performance_monitor.track_operation("voice_matching"):
            try:
                # Get user's voice profile
                voice_profile = await self._get_voice_profile(user_id, db)
                if not voice_profile:
                    # Perform quick analysis if no profile exists
                    analysis_result = await self.analyze_user_voice(user_id, 20, db)
                    if "error" in analysis_result:
                        return {"error": "Unable to determine brand voice", "match_score": 0.0}
                    voice_profile = analysis_result["voice_profile"]
                
                # Extract content text
                content_text = content_data.get("text", "")
                if not content_text:
                    return {"error": "No text content provided for matching"}
                
                # Analyze content voice characteristics
                content_metrics = await self._analyze_voice_metrics([content_text])
                content_characteristics = await self._identify_voice_characteristics([content_text], content_metrics)
                
                # Calculate voice matching score
                match_score = await self._calculate_voice_match_score(
                    voice_profile, content_characteristics, content_metrics
                )
                
                # Generate voice alignment suggestions
                suggestions = await self._generate_voice_alignment_suggestions(
                    voice_profile, content_characteristics, content_metrics
                )
                
                # Apply brand guidelines if provided
                guideline_compliance = await self._check_guideline_compliance(
                    content_text, brand_guidelines
                )
                
                return {
                    "request_id": content_data.get("request_id", str(uuid.uuid4())),
                    "content": {
                        "voice_matched_content": await self._adjust_content_voice(
                            content_text, voice_profile, suggestions
                        ),
                        "original_content": content_text
                    },
                    "voice_analysis": {
                        "match_score": match_score,
                        "content_characteristics": content_characteristics,
                        "brand_characteristics": voice_profile.get("voice_characteristics", []),
                        "alignment_score": self._calculate_alignment_score(
                            voice_profile.get("voice_characteristics", []),
                            content_characteristics
                        )
                    },
                    "suggestions": suggestions,
                    "guideline_compliance": guideline_compliance,
                    "processing_time": 0.0,  # Will be set by caller
                    "status": "completed"
                }
                
            except Exception as e:
                logger.error(f"Voice matching error: {e}")
                raise HTTPException(status_code=500, detail=f"Voice matching failed: {str(e)}")
    
    async def _get_user_content_samples(
        self,
        user_id: str,
        limit: int,
        db: AsyncSession
    ) -> List[Content]:
        """Retrieve user's recent content for analysis"""



        
        try:
            # Query recent content with text
            query = (
                select(Content)
                .where(
                    and_(
                        Content.user_id == user_id,
                        Content.content_type.in_([
                            ContentType.BLOG_POST,
                            ContentType.SOCIAL_MEDIA_POST,
                            ContentType.EMAIL,
                            ContentType.ARTICLE,
                            ContentType.DESCRIPTION
                        ])
                    )
                )
                .order_by(desc(Content.created_at))
                .limit(limit)
            )
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error fetching content samples: {e}")
            return []
    
    def _extract_text_content(self, content: Content) -> str:
        """Extract text content from content object"""



        try:
            # Extract text based on content structure
            if hasattr(content, 'content_data') and content.content_data:
                if isinstance(content.content_data, dict):
                    return content.content_data.get('text', '') or content.content_data.get('body', '')
                elif isinstance(content.content_data, str):
                    return content.content_data
            
            # Fallback to title and description
            text_parts = []
            if hasattr(content, 'title') and content.title:
                text_parts.append(content.title)
            if hasattr(content, 'description') and content.description:
                text_parts.append(content.description)
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    async def _analyze_voice_metrics(self, text_samples: List[str]) -> VoiceMetrics:
        """Perform comprehensive voice metrics analysis"""



        
        try:
            # Combine all text samples
            combined_text = ' '.join(text_samples)
            
            # Tokenize text
            sentences = sent_tokenize(combined_text)
            words = word_tokenize(combined_text.lower())
            words = [word for word in words if word.isalpha()]
            
            # Calculate linguistic metrics
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            avg_word_length = np.mean([len(word) for word in words])
            readability_score = flesch_reading_ease(combined_text)
            vocabulary_diversity = len(set(words)) / len(words) if words else 0
            
            # Sentiment analysis
            sentiment_scores = {}
            for sample in text_samples:
                sentiment = self.sentiment_analyzer.polarity_scores(sample)
                for key, value in sentiment.items():
                    sentiment_scores[key] = sentiment_scores.get(key, 0) + value
            
            # Average sentiment scores
            sample_count = len(text_samples)
            sentiment_scores = {k: v / sample_count for k, v in sentiment_scores.items()}
            
            # Emotion analysis
            emotion_distribution = await self._analyze_emotions(text_samples)
            
            # Style analysis
            formality_score = self._calculate_formality_score(combined_text)
            complexity_score = self._calculate_complexity_score(combined_text)
            engagement_score = self._calculate_engagement_score(combined_text)
            
            # Content patterns
            common_words = Counter(words).most_common(20)
            common_phrases = self._extract_common_phrases(combined_text)
            
            # POS distribution
            pos_distribution = self._analyze_pos_distribution(combined_text)
            
            # Personality traits
            personality_traits = await self._analyze_personality_traits(combined_text)
            communication_style = self._analyze_communication_style(combined_text)
            
            return VoiceMetrics(
                avg_sentence_length=float(avg_sentence_length),
                avg_word_length=float(avg_word_length),
                readability_score=float(readability_score),
                vocabulary_diversity=float(vocabulary_diversity),
                sentiment_scores=sentiment_scores,
                emotion_distribution=emotion_distribution,
                formality_score=float(formality_score),
                complexity_score=float(complexity_score),
                engagement_score=float(engagement_score),
                common_words=common_words,
                common_phrases=common_phrases,
                pos_distribution=pos_distribution,
                personality_traits=personality_traits,
                communication_style=communication_style
            )
            
        except Exception as e:
            logger.error(f"Voice metrics analysis error: {e}")
            return VoiceMetrics()
    
    async def _analyze_emotions(self, text_samples: List[str]) -> Dict[str, float]:
        """Analyze emotional distribution in text samples"""



        
        try:
            emotion_counts = defaultdict(int)
            total_samples = len(text_samples)
            
            for sample in text_samples[:10]:  # Limit for performance
                if len(sample.strip()) < 10:
                    continue
                
                # Get emotion predictions
                emotions = self.emotion_pipeline(sample[:500])  # Limit text length
                if emotions:
                    top_emotion = max(emotions, key=lambda x: x['score'])
                    emotion_counts[top_emotion['label']] += 1
            
            # Convert to percentages
            emotion_distribution = {}
            for emotion, count in emotion_counts.items():
                emotion_distribution[emotion] = count / total_samples if total_samples > 0 else 0
            
            return emotion_distribution
            
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            return {}
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calculate formality score of text"""



        
        try:
            # Formality indicators
            formal_words = [
                'furthermore', 'moreover', 'nevertheless', 'consequently',
                'therefore', 'however', 'additionally', 'accordingly'
            ]
            
            informal_words = [
                'gonna', 'wanna', 'yeah', 'nah', 'cool', 'awesome',
                'super', 'really', 'pretty', 'kinda', 'sorta'
            ]
            
            contractions = ["n't", "'re", "'ve", "'ll", "'d", "'m", "'s"]
            
            words = word_tokenize(text.lower())
            total_words = len(words)
            
            if total_words == 0:
                return 0.5
            
            # Count formal vs informal indicators
            formal_count = sum(1 for word in words if word in formal_words)
            informal_count = sum(1 for word in words if word in informal_words)
            contraction_count = sum(1 for word in words if any(cont in word for cont in contractions))
            
            # Calculate formality score (0 = very informal, 1 = very formal)
            formal_score = formal_count / total_words
            informal_score = (informal_count + contraction_count) / total_words
            
            # Normalize to 0-1 range
            formality = 0.5 + (formal_score - informal_score)
            return max(0, min(1, formality))
            
        except Exception as e:
            logger.error(f"Formality calculation error: {e}")
            return 0.5
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score of text"""



        
        try:
            # Multiple complexity indicators
            fk_grade = flesch_kincaid_grade(text)
            
            # Sentence structure complexity
            sentences = sent_tokenize(text)
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            
            # Vocabulary complexity
            words = word_tokenize(text.lower())
            unique_words = len(set(words))
            total_words = len(words)
            lexical_diversity = unique_words / total_words if total_words > 0 else 0
            
            # Normalize scores
            complexity_score = (
                (fk_grade / 20) * 0.4 +  # Reading grade level
                (avg_sentence_length / 30) * 0.3 +  # Sentence complexity
                lexical_diversity * 0.3  # Vocabulary diversity
            )
            
            return max(0, min(1, complexity_score))
            
        except Exception as e:
            logger.error(f"Complexity calculation error: {e}")
            return 0.5
    
    def _calculate_engagement_score(self, text: str) -> float:
        """Calculate engagement potential score"""



        
        try:
            # Engagement indicators
            question_marks = text.count('?')
            exclamation_marks = text.count('!')
            personal_pronouns = ['you', 'your', 'we', 'our', 'us']
            action_words = ['discover', 'learn', 'explore', 'join', 'start', 'get', 'find']
            
            words = word_tokenize(text.lower())
            total_words = len(words)
            
            if total_words == 0:
                return 0
            
            # Count engagement elements
            personal_pronoun_count = sum(1 for word in words if word in personal_pronouns)
            action_word_count = sum(1 for word in words if word in action_words)
            
            # Calculate engagement score
            engagement_score = (
                (question_marks / total_words) * 100 * 0.3 +
                (exclamation_marks / total_words) * 100 * 0.2 +
                (personal_pronoun_count / total_words) * 0.3 +
                (action_word_count / total_words) * 0.2
            )
            
            return max(0, min(1, engagement_score))
            
        except Exception as e:
            logger.error(f"Engagement calculation error: {e}")
            return 0.5
    
    def _extract_common_phrases(self, text: str) -> List[Tuple[str, int]]:
        """Extract common phrases from text"""



        
        try:
            # Use n-grams to find common phrases
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and word not in stopwords.words('english')]
            
            # Generate 2-grams and 3-grams
            phrases = []
            for i in range(len(words) - 1):
                phrases.append(' '.join(words[i:i+2]))
            for i in range(len(words) - 2):
                phrases.append(' '.join(words[i:i+3]))
            
            # Count phrase frequency
            phrase_counts = Counter(phrases)
            return phrase_counts.most_common(10)
            
        except Exception as e:
            logger.error(f"Phrase extraction error: {e}")
            return []
    
    def _analyze_pos_distribution(self, text: str) -> Dict[str, float]:
        """Analyze part-of-speech distribution"""



        
        try:
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            # Count POS tags
            pos_counts = Counter(tag for word, tag in pos_tags)
            total_tags = len(pos_tags)
            
            # Convert to percentages
            pos_distribution = {}
            for pos, count in pos_counts.items():
                pos_distribution[pos] = count / total_tags if total_tags > 0 else 0
            
            return pos_distribution
            
        except Exception as e:
            logger.error(f"POS analysis error: {e}")
            return {}
    
    async def _analyze_personality_traits(self, text: str) -> Dict[str, float]:
        """Analyze personality traits from text"""



        
        try:
            # Use LLM for personality analysis
            personality_prompt = f"""
            Analyze the personality traits shown in the following text and rate each trait from 0-1:
            
            Text: "{text[:1000]}..."
            
            Rate these personality traits:
            - Openness (creativity, curiosity)
            - Conscientiousness (organization, discipline)  
            - Extraversion (sociability, assertiveness)
            - Agreeableness (cooperation, trust)
            - Neuroticism (emotional stability)
            
            Provide ratings as JSON: {{"openness": 0.0-1.0, "conscientiousness": 0.0-1.0, ...}}
            """
            
            response = await self.llm_engine.generate_response(
                prompt=personality_prompt,
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse JSON response
            try:
                import json
                personality_data = json.loads(response)
                return personality_data
            except:
                # Fallback to basic analysis
                return self._basic_personality_analysis(text)
                
        except Exception as e:
            logger.error(f"Personality analysis error: {e}")
            return self._basic_personality_analysis(text)
    
    def _basic_personality_analysis(self, text: str) -> Dict[str, float]:
        """Basic personality trait analysis fallback"""



        
        try:
            words = word_tokenize(text.lower())
            
            # Simple keyword-based analysis
            creative_words = ['creative', 'innovative', 'unique', 'original', 'artistic']
            organized_words = ['plan', 'organize', 'structure', 'systematic', 'efficient']
            social_words = ['we', 'together', 'community', 'share', 'connect']
            positive_words = ['great', 'awesome', 'wonderful', 'excellent', 'amazing']
            
            word_count = len(words)
            if word_count == 0:
                return {}
            
            return {
                'openness': sum(1 for word in words if word in creative_words) / word_count,
                'conscientiousness': sum(1 for word in words if word in organized_words) / word_count,
                'extraversion': sum(1 for word in words if word in social_words) / word_count,
                'agreeableness': sum(1 for word in words if word in positive_words) / word_count,
                'neuroticism': max(0, 0.5 - sum(1 for word in words if word in positive_words) / word_count)
            }
            
        except Exception as e:
            logger.error(f"Basic personality analysis error: {e}")
            return {}
    
    def _analyze_communication_style(self, text: str) -> Dict[str, float]:
        """Analyze communication style patterns"""



        
        try:
            # Communication style indicators
            direct_words = ['will', 'must', 'should', 'need', 'required']
            collaborative_words = ['let\'s', 'together', 'we can', 'our', 'team']
            supportive_words = ['help', 'support', 'assist', 'guide', 'encourage']
            
            words = word_tokenize(text.lower())
            word_count = len(words)
            
            if word_count == 0:
                return {}
            
            return {
                'directness': sum(1 for word in words if word in direct_words) / word_count,
                'collaboration': sum(1 for word in words if word in collaborative_words) / word_count,
                'supportiveness': sum(1 for word in words if word in supportive_words) / word_count,
                'assertiveness': (text.count('!') + text.count('?')) / word_count
            }
            
        except Exception as e:
            logger.error(f"Communication style analysis error: {e}")
            return {}
    
    async def _identify_voice_characteristics(
        self,
        text_samples: List[str],
        voice_metrics: VoiceMetrics
    ) -> List[VoiceCharacteristic]:
        """Identify dominant voice characteristics"""



        
        try:
            characteristics = []
            
            # Analyze based on metrics
            if voice_metrics.formality_score > 0.7:
                characteristics.append(VoiceCharacteristic.PROFESSIONAL)
            elif voice_metrics.formality_score < 0.3:
                characteristics.append(VoiceCharacteristic.CASUAL)
            
            if voice_metrics.engagement_score > 0.6:
                characteristics.append(VoiceCharacteristic.FRIENDLY)
            
            if voice_metrics.complexity_score > 0.7:
                characteristics.append(VoiceCharacteristic.TECHNICAL)
            elif voice_metrics.complexity_score < 0.3:
                characteristics.append(VoiceCharacteristic.CONVERSATIONAL)
            
            # Analyze emotional characteristics
            emotions = voice_metrics.emotion_distribution
            if emotions.get('joy', 0) > 0.3:
                characteristics.append(VoiceCharacteristic.PLAYFUL)
            if emotions.get('confidence', 0) > 0.2:
                characteristics.append(VoiceCharacteristic.CONFIDENT)
            
            # Ensure at least one characteristic
            if not characteristics:
                characteristics.append(VoiceCharacteristic.NEUTRAL if hasattr(VoiceCharacteristic, 'NEUTRAL') else VoiceCharacteristic.PROFESSIONAL)
            
            return characteristics[:5]  # Limit to top 5 characteristics
            
        except Exception as e:
            logger.error(f"Voice characteristics identification error: {e}")
            return [VoiceCharacteristic.PROFESSIONAL]
    
    def _determine_dominant_tone(self, voice_metrics: VoiceMetrics) -> VoiceTone:
        """Determine dominant tone from voice metrics"""



        
        try:
            sentiment = voice_metrics.sentiment_scores
            
            if sentiment.get('pos', 0) > 0.5:
                return VoiceTone.POSITIVE
            elif sentiment.get('neg', 0) > 0.3:
                return VoiceTone.NEGATIVE
            else:
                return VoiceTone.NEUTRAL
                
        except Exception as e:
            logger.error(f"Tone determination error: {e}")
            return VoiceTone.NEUTRAL
    
    def _determine_writing_style(self, voice_metrics: VoiceMetrics) -> WritingStyle:
        """Determine writing style from voice metrics"""



        
        try:
            if voice_metrics.formality_score > 0.8:
                return WritingStyle.FORMAL
            elif voice_metrics.formality_score < 0.3:
                return WritingStyle.INFORMAL
            elif voice_metrics.complexity_score > 0.7:
                return WritingStyle.ACADEMIC
            elif voice_metrics.engagement_score > 0.6:
                return WritingStyle.PERSUASIVE
            else:
                return WritingStyle.DESCRIPTIVE
                
        except Exception as e:
            logger.error(f"Writing style determination error: {e}")
            return WritingStyle.DESCRIPTIVE
    
    async def _calculate_consistency_score(self, text_samples: List[str]) -> float:
        """Calculate voice consistency across text samples"""



        
        try:
            if len(text_samples) < 2:
                return 1.0
            
            # Analyze each sample
            sample_metrics = []
            for sample in text_samples:
                metrics = await self._analyze_voice_metrics([sample])
                sample_metrics.append(metrics)
            
            # Calculate consistency across key metrics
            consistency_scores = []
            
            # Formality consistency
            formality_scores = [m.formality_score for m in sample_metrics]
            formality_consistency = 1 - np.std(formality_scores) if len(formality_scores) > 1 else 1.0
            consistency_scores.append(formality_consistency)
            
            # Complexity consistency  
            complexity_scores = [m.complexity_score for m in sample_metrics]
            complexity_consistency = 1 - np.std(complexity_scores) if len(complexity_scores) > 1 else 1.0
            consistency_scores.append(complexity_consistency)
            
            # Sentiment consistency
            sentiment_scores = [m.sentiment_scores.get('compound', 0) for m in sample_metrics]
            sentiment_consistency = 1 - np.std(sentiment_scores) if len(sentiment_scores) > 1 else 1.0
            consistency_scores.append(sentiment_consistency)
            
            # Overall consistency
            overall_consistency = np.mean(consistency_scores)
            return max(0, min(1, overall_consistency))
            
        except Exception as e:
            logger.error(f"Consistency calculation error: {e}")
            return 0.5
    
    async def _store_voice_profile(self, profile: BrandVoiceProfile, db: AsyncSession):
        """Store brand voice profile in database"""



        
        try:
            # Create voice profile record
            profile_data = {
                'user_id': profile.user_id,
                'brand_name': profile.brand_name,
                'voice_characteristics': [vc.value for vc in profile.voice_characteristics],
                'dominant_tone': profile.dominant_tone.value,
                'writing_style': profile.writing_style.value,
                'consistency_score': profile.consistency_score,
                'content_samples': profile.content_samples,
                'voice_metrics': self._serialize_voice_metrics(profile.voice_metrics),
                'voice_guidelines': profile.voice_guidelines,
                'target_audience': profile.target_audience,
                'industry_context': profile.industry_context,
                'last_analysis': profile.last_analysis,
                'created_at': datetime.now(timezone.utc)
            }
            
            # Store in cache for quick access
            cache_key = f"voice_profile:{profile.user_id}"
            await self.cache_manager.set(cache_key, profile_data, ttl=3600)
            
            logger.info(f"Voice profile stored for user {profile.user_id}")
            
        except Exception as e:
            logger.error(f"Error storing voice profile: {e}")
    
    def _serialize_voice_metrics(self, metrics: VoiceMetrics) -> Dict[str, Any]:
        """Serialize voice metrics for storage"""



        
        return {
            'avg_sentence_length': metrics.avg_sentence_length,
            'avg_word_length': metrics.avg_word_length,
            'readability_score': metrics.readability_score,
            'vocabulary_diversity': metrics.vocabulary_diversity,
            'sentiment_scores': metrics.sentiment_scores,
            'emotion_distribution': metrics.emotion_distribution,
            'formality_score': metrics.formality_score,
            'complexity_score': metrics.complexity_score,
            'engagement_score': metrics.engagement_score,
            'common_words': metrics.common_words,
            'common_phrases': metrics.common_phrases,
            'pos_distribution': metrics.pos_distribution,
            'personality_traits': metrics.personality_traits,
            'communication_style': metrics.communication_style
        }
    
    def _serialize_voice_profile(self, profile: BrandVoiceProfile) -> Dict[str, Any]:
        """Serialize voice profile for API response"""



        
        return {
            'user_id': profile.user_id,
            'brand_name': profile.brand_name,
            'voice_characteristics': [vc.value for vc in profile.voice_characteristics],
            'dominant_tone': profile.dominant_tone.value,
            'writing_style': profile.writing_style.value,
            'consistency_score': profile.consistency_score,
            'content_samples': profile.content_samples,
            'voice_metrics': self._serialize_voice_metrics(profile.voice_metrics),
            'last_analysis': profile.last_analysis.isoformat()
        }
    
    async def _get_voice_profile(self, user_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Retrieve voice profile from cache or database"""



        
        try:
            # Check cache first
            cache_key = f"voice_profile:{user_id}"
            cached_profile = await self.cache_manager.get(cache_key)
            
            if cached_profile:
                return cached_profile
            
            # If not in cache, return None (will trigger new analysis)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving voice profile: {e}")
            return None
    
    async def _generate_voice_recommendations(self, profile: BrandVoiceProfile) -> List[str]:
        """Generate actionable voice improvement recommendations"""
        
        recommendations = []
        metrics = profile.voice_metrics
        
        try:
            # Consistency recommendations
            if profile.consistency_score < 0.7:
                recommendations.append("Work on maintaining consistent tone across all content")
            
            # Readability recommendations
            if metrics.readability_score < 30:
                recommendations.append("Consider simplifying language for better readability")
            elif metrics.readability_score > 80:
                recommendations.append("Add more sophisticated vocabulary for professional appeal")
            
            # Engagement recommendations
            if metrics.engagement_score < 0.4:
                recommendations.append("Include more questions and direct address to increase engagement")
            
            # Formality recommendations
            if metrics.formality_score > 0.8:
                recommendations.append("Consider adding casual elements to appear more approachable")
            elif metrics.formality_score < 0.2:
                recommendations.append("Add more professional language for credibility")
            
            # Complexity recommendations
            if metrics.complexity_score > 0.8:
                recommendations.append("Simplify complex sentences for broader audience appeal")
            elif metrics.complexity_score < 0.2:
                recommendations.append("Add more depth and complexity to demonstrate expertise")
            
            # Personality recommendations
            personality = metrics.personality_traits
            if personality.get('openness', 0) < 0.3:
                recommendations.append("Show more creativity and innovative thinking in content")
            if personality.get('extraversion', 0) < 0.3:
                recommendations.append("Use more social and collaborative language")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Continue developing your unique brand voice"]
    
    async def _calculate_voice_match_score(
        self,
        voice_profile: Dict[str, Any],
        content_characteristics: List[VoiceCharacteristic],
        content_metrics: VoiceMetrics
    ) -> float:
        """Calculate how well content matches brand voice"""



        
        try:
            # Compare characteristics
            profile_characteristics = voice_profile.get('voice_characteristics', [])
            characteristic_match = len(set(profile_characteristics) & set([vc.value for vc in content_characteristics])) / max(len(profile_characteristics), 1)
            
            # Compare metrics
            profile_metrics = voice_profile.get('voice_metrics', {})
            
            formality_diff = abs(profile_metrics.get('formality_score', 0.5) - content_metrics.formality_score)
            complexity_diff = abs(profile_metrics.get('complexity_score', 0.5) - content_metrics.complexity_score)
            engagement_diff = abs(profile_metrics.get('engagement_score', 0.5) - content_metrics.engagement_score)
            
            metric_match = 1 - np.mean([formality_diff, complexity_diff, engagement_diff])
            
            # Overall match score
            match_score = (characteristic_match * 0.4 + metric_match * 0.6)
            return max(0, min(1, match_score))
            
        except Exception as e:
            logger.error(f"Voice match calculation error: {e}")
            return 0.5
    
    def _calculate_alignment_score(
        self,
        brand_characteristics: List[str],
        content_characteristics: List[VoiceCharacteristic]
    ) -> float:
        """Calculate alignment score between brand and content characteristics"""



        
        try:
            content_char_values = [vc.value for vc in content_characteristics]
            common_characteristics = set(brand_characteristics) & set(content_char_values)
            
            if not brand_characteristics:
                return 1.0
            
            alignment = len(common_characteristics) / len(brand_characteristics)
            return max(0, min(1, alignment))
            
        except Exception as e:
            logger.error(f"Alignment calculation error: {e}")
            return 0.5
    
    async def _generate_voice_alignment_suggestions(
        self,
        voice_profile: Dict[str, Any],
        content_characteristics: List[VoiceCharacteristic],
        content_metrics: VoiceMetrics
    ) -> List[str]:
        """Generate suggestions for aligning content with brand voice"""
        
        suggestions = []
        
        try:
            profile_characteristics = voice_profile.get('voice_characteristics', [])
            profile_metrics = voice_profile.get('voice_metrics', {})
            
            # Characteristic alignment suggestions
            missing_characteristics = set(profile_characteristics) - set([vc.value for vc in content_characteristics])
            for char in missing_characteristics:
                if char == 'professional':
                    suggestions.append("Add more professional language and formal tone")
                elif char == 'friendly':
                    suggestions.append("Include more welcoming and personable language")
                elif char == 'confident':
                    suggestions.append("Use more assertive and decisive language")
                elif char == 'creative':
                    suggestions.append("Add more innovative and imaginative elements")
            
            # Metric alignment suggestions
            profile_formality = profile_metrics.get('formality_score', 0.5)
            if abs(profile_formality - content_metrics.formality_score) > 0.2:
                if profile_formality > content_metrics.formality_score:
                    suggestions.append("Increase formality to match brand voice")
                else:
                    suggestions.append("Use more casual language to match brand voice")
            
            return suggestions[:3]  # Limit to top 3 suggestions
            
        except Exception as e:
            logger.error(f"Voice alignment suggestions error: {e}")
            return ["Align content tone with established brand voice"]
    
    async def _check_guideline_compliance(
        self,
        content_text: str,
        brand_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check content compliance with brand guidelines"""
        
        compliance_results = {
            "overall_score": 1.0,
            "passed_checks": [],
            "failed_checks": [],
            "warnings": []
        }
        
        try:
            # Check required keywords
            required_keywords = brand_guidelines.get('required_keywords', [])
            if required_keywords:
                found_keywords = [kw for kw in required_keywords if kw.lower() in content_text.lower()]
                if len(found_keywords) == len(required_keywords):
                    compliance_results["passed_checks"].append("All required keywords included")
                else:
                    missing_keywords = set(required_keywords) - set(found_keywords)
                    compliance_results["failed_checks"].append(f"Missing keywords: {', '.join(missing_keywords)}")
            
            # Check forbidden words
            forbidden_words = brand_guidelines.get('forbidden_words', [])
            if forbidden_words:
                found_forbidden = [word for word in forbidden_words if word.lower() in content_text.lower()]
                if not found_forbidden:
                    compliance_results["passed_checks"].append("No forbidden words used")
                else:
                    compliance_results["failed_checks"].append(f"Contains forbidden words: {', '.join(found_forbidden)}")
            
            # Check tone requirements
            required_tone = brand_guidelines.get('required_tone')
            if required_tone:
                # Simple tone check based on sentiment
                sentiment = self.sentiment_analyzer.polarity_scores(content_text)
                if required_tone.lower() == 'positive' and sentiment['pos'] > 0.3:
                    compliance_results["passed_checks"].append("Maintains required positive tone")
                elif required_tone.lower() == 'neutral' and sentiment['neu'] > 0.5:
                    compliance_results["passed_checks"].append("Maintains required neutral tone")
                else:
                    compliance_results["warnings"].append(f"Content tone may not match required {required_tone} tone")
            
            # Calculate overall compliance score
            total_checks = len(compliance_results["passed_checks"]) + len(compliance_results["failed_checks"])
            if total_checks > 0:
                compliance_results["overall_score"] = len(compliance_results["passed_checks"]) / total_checks
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Guideline compliance check error: {e}")
            return compliance_results
    
    async def _adjust_content_voice(
        self,
        content_text: str,
        voice_profile: Dict[str, Any],
        suggestions: List[str]
    ) -> str:
        """Adjust content to match brand voice"""



        
        try:
            # Use LLM to adjust content based on voice profile
            adjustment_prompt = f"""
            Adjust the following content to match the specified brand voice characteristics:
            
            Original Content: "{content_text}"
            
            Brand Voice Profile:
            - Characteristics: {voice_profile.get('voice_characteristics', [])}
            - Dominant Tone: {voice_profile.get('dominant_tone', 'neutral')}
            - Writing Style: {voice_profile.get('writing_style', 'descriptive')}
            
            Suggestions: {suggestions}
            
            Provide the adjusted content that maintains the original meaning while matching the brand voice:
            """
            
            adjusted_content = await self.llm_engine.generate_response(
                prompt=adjustment_prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            return adjusted_content.strip()
            
        except Exception as e:
            logger.error(f"Content voice adjustment error: {e}")
            return content_text  # Return original if adjustment fails
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for brand voice engine"""



        return {
            "status": "healthy",
            "models_loaded": bool(self.model and self.tokenizer),
            "cache_status": "active" if self.cache_manager else "inactive",
            "last_check": datetime.now(timezone.utc).isoformat()
        }


class VoiceConsistencyManager:
    """Manages voice consistency across content and collaborations"""
    
    def __init__(self):
        self.voice_engine = BrandVoiceEngine()
        self.performance_monitor = PerformanceMonitor("voice_consistency")
    
    async def analyze_consistency_across_content(
        self,
        user_id: str,
        content_ids: List[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze voice consistency across multiple content pieces"""
        
        async with self.performance_monitor.track_operation("consistency_analysis"):
            try:
                # Get content pieces
                contents = await self._get_content_by_ids(content_ids, db)
                if not contents:
                    return {"error": "No content found for analysis"}
                
                # Extract text from each content piece
                text_samples = []
                for content in contents:
                    text = self.voice_engine._extract_text_content(content)
                    if text and len(text.strip()) > 20:
                        text_samples.append(text)
                
                if len(text_samples) < 2:
                    return {"error": "Need at least 2 content pieces for consistency analysis"}
                
                # Analyze consistency
                consistency_score = await self.voice_engine._calculate_consistency_score(text_samples)
                
                # Generate consistency report
                report = await self._generate_consistency_report(
                    text_samples, consistency_score, user_id
                )
                
                return {
                    "consistency_score": consistency_score,
                    "content_count": len(text_samples),
                    "consistency_report": report,
                    "recommendations": await self._generate_consistency_recommendations(
                        consistency_score, text_samples
                    )
                }
                
            except Exception as e:
                logger.error(f"Consistency analysis error: {e}")
                raise HTTPException(status_code=500, detail=f"Consistency analysis failed: {str(e)}")
    
    async def _get_content_by_ids(self, content_ids: List[str], db: AsyncSession) -> List[Content]:
        """Retrieve content by IDs"""



        try:
            query = select(Content).where(Content.id.in_(content_ids))
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching content by IDs: {e}")
            return []
    
    async def _generate_consistency_report(
        self,
        text_samples: List[str],
        consistency_score: float,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate detailed consistency report"""



        
        try:
            # Analyze individual pieces
            individual_analyses = []
            for i, text in enumerate(text_samples):
                metrics = await self.voice_engine._analyze_voice_metrics([text])
                characteristics = await self.voice_engine._identify_voice_characteristics([text], metrics)
                
                individual_analyses.append({
                    "content_index": i,
                    "formality_score": metrics.formality_score,
                    "complexity_score": metrics.complexity_score,
                    "engagement_score": metrics.engagement_score,
                    "characteristics": [vc.value for vc in characteristics],
                    "sentiment": metrics.sentiment_scores.get('compound', 0)
                })
            
            # Calculate variation metrics
            formality_scores = [analysis['formality_score'] for analysis in individual_analyses]
            complexity_scores = [analysis['complexity_score'] for analysis in individual_analyses]
            engagement_scores = [analysis['engagement_score'] for analysis in individual_analyses]
            
            return {
                "overall_consistency": consistency_score,
                "formality_variation": float(np.std(formality_scores)) if len(formality_scores) > 1 else 0,
                "complexity_variation": float(np.std(complexity_scores)) if len(complexity_scores) > 1 else 0,
                "engagement_variation": float(np.std(engagement_scores)) if len(engagement_scores) > 1 else 0,
                "individual_analyses": individual_analyses,
                "consistency_level": self._categorize_consistency_level(consistency_score)
            }
            
        except Exception as e:
            logger.error(f"Consistency report generation error: {e}")
            return {"error": "Failed to generate consistency report"}
    
    def _categorize_consistency_level(self, score: float) -> str:
        """Categorize consistency level based on score"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    async def _generate_consistency_recommendations(
        self,
        consistency_score: float,
        text_samples: List[str]
    ) -> List[str]:
        """Generate recommendations for improving consistency"""
        
        recommendations = []
        
        try:
            if consistency_score < 0.5:
                recommendations.append("Establish clear brand voice guidelines")
                recommendations.append("Create a style guide with tone examples")
                recommendations.append("Review content before publishing for voice alignment")
            elif consistency_score < 0.7:
                recommendations.append("Fine-tune voice characteristics across content")
                recommendations.append("Standardize key messaging and terminology")
            else:
                recommendations.append("Maintain current voice consistency practices")
                recommendations.append("Consider minor refinements for perfection")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Consistency recommendations error: {e}")
            return ["Continue working on brand voice consistency"]
