"""Brand Voice Analysis Module for IA Influencer Agent Platform

Advanced AI-powered brand voice analysis and consistency monitoring for
content creators, influencers, and brand partnerships across all content formats.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter, defaultdict
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy

logger = logging.getLogger(__name__)

class VoiceDimension(Enum):
    """Brand voice dimensions"""    FORMALITY = "formality"  # Formal vs Casual
    ENTHUSIASM = "enthusiasm"  # Excited vs Calm
    EXPERTISE = "expertise"  # Expert vs Approachable
    FRIENDLINESS = "friendliness"  # Professional vs Personal
    CONFIDENCE = "confidence"  # Assertive vs Humble
    CREATIVITY = "creativity"  # Innovative vs Traditional
    INCLUSIVITY = "inclusivity"  # Inclusive vs Exclusive
    AUTHENTICITY = "authenticity"  # Authentic vs Polished

class ContentFormat(Enum):
    """Content format types"""    SOCIAL_POST = "social_post"
    BLOG_ARTICLE = "blog_article"
    VIDEO_SCRIPT = "video_script"
    PODCAST_SCRIPT = "podcast_script"
    EMAIL_CAMPAIGN = "email_campaign"
    PRODUCT_DESCRIPTION = "product_description"
    ADVERTISEMENT = "advertisement"
    PRESS_RELEASE = "press_release"

@dataclass
class VoiceProfile:
    """Brand voice profile definition"""    brand_id: str
    brand_name: str
    voice_dimensions: Dict[VoiceDimension, float] = field(default_factory=dict)  # -1 to 1 scale
    key_phrases: List[str] = field(default_factory=list)
    tone_keywords: List[str] = field(default_factory=list)
    language_style: Dict[str, Any] = field(default_factory=dict)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    brand_values: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    communication_guidelines: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    avoid_list: List[str] = field(default_factory=list)
    platform_adaptations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class VoiceAnalysisResult:
    """Voice analysis result"""    content_id: str
    brand_id: str
    consistency_score: float
    dimension_scores: Dict[VoiceDimension, float] = field(default_factory=dict)
    alignment_analysis: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    tone_analysis: Dict[str, float] = field(default_factory=dict)
    readability_metrics: Dict[str, float] = field(default_factory=dict)
    authenticity_score: float = 0.0
    engagement_prediction: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BrandVoiceEvolution:
    """Brand voice evolution tracking"""    brand_id: str
    time_period: timedelta
    voice_drift: Dict[VoiceDimension, float] = field(default_factory=dict)
    consistency_trend: List[Tuple[datetime, float]] = field(default_factory=list)
    content_type_variations: Dict[ContentFormat, Dict[str, float]] = field(default_factory=dict)
    platform_adaptations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    success_patterns: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class BrandVoiceAnalyzer:
    """    Advanced brand voice analysis and consistency monitoring system
    
    Capabilities:
    - Multi-dimensional voice profiling
    - Real-time consistency monitoring
    - Platform-specific voice adaptation
    - Voice evolution tracking
    - Authenticity assessment
    - Engagement prediction based on voice consistency
    - Content optimization recommendations
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.analysis_history: List[VoiceAnalysisResult] = []
        self.nlp = None
        self.sentiment_analyzer = None
        self.tfidf_vectorizer = TfidfVectorizer()
        self.voice_models = {}
        
    async def initialize(self):
        """Initialize NLP models and analyzers"""        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # Download NLTK data if needed
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            
            logger.info("Brand voice analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing brand voice analyzer: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""        return {
            'consistency_threshold': 0.7,
            'min_content_length': 50,
            'enable_platform_adaptation': True,
            'track_voice_evolution': True,
            'authenticity_weight': 0.3,
            'engagement_prediction_weight': 0.4,
            'dimension_weights': {
                VoiceDimension.FORMALITY: 0.15,
                VoiceDimension.ENTHUSIASM: 0.15,
                VoiceDimension.EXPERTISE: 0.12,
                VoiceDimension.FRIENDLINESS: 0.12,
                VoiceDimension.CONFIDENCE: 0.12,
                VoiceDimension.CREATIVITY: 0.12,
                VoiceDimension.INCLUSIVITY: 0.10,
                VoiceDimension.AUTHENTICITY: 0.12
            }
        }
    
    async def create_voice_profile(self, voice_profile: VoiceProfile) -> bool:
        """Create or update a brand voice profile"""        try:
            # Validate voice profile
            if not self._validate_voice_profile(voice_profile):
                return False
            
            # Process and enhance voice profile
            voice_profile = await self._enhance_voice_profile(voice_profile)
            
            # Store voice profile
            self.voice_profiles[voice_profile.brand_id] = voice_profile
            
            # Train voice model for this brand
            await self._train_brand_voice_model(voice_profile)
            
            logger.info(f"Voice profile created for brand {voice_profile.brand_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating voice profile: {e}")
            return False
    
    async def analyze_content_voice(
        self,
        content: str,
        brand_id: str,
        content_format: ContentFormat = ContentFormat.SOCIAL_POST,
        platform: Optional[str] = None
    ) -> VoiceAnalysisResult:
        """Analyze content against brand voice profile"""        try:
            if brand_id not in self.voice_profiles:
                raise ValueError(f"Brand voice profile not found: {brand_id}")
            
            voice_profile = self.voice_profiles[brand_id]
            
            # Generate unique content ID
            content_id = f"content_{brand_id}_{int(datetime.utcnow().timestamp())}"
            
            # Perform comprehensive voice analysis
            dimension_scores = await self._analyze_voice_dimensions(content, voice_profile)
            alignment_analysis = await self._analyze_alignment(content, voice_profile)
            tone_analysis = await self._analyze_tone(content)
            readability_metrics = await self._calculate_readability_metrics(content)
            authenticity_score = await self._calculate_authenticity_score(content, voice_profile)
            
            # Calculate overall consistency score
            consistency_score = self._calculate_consistency_score(
                dimension_scores, alignment_analysis, voice_profile
            )
            
            # Generate recommendations
            recommendations = await self._generate_voice_recommendations(
                content, voice_profile, dimension_scores, alignment_analysis
            )
            
            # Detect issues
            detected_issues = await self._detect_voice_issues(
                content, voice_profile, dimension_scores
            )
            
            # Generate improvements
            suggested_improvements = await self._suggest_voice_improvements(
                content, voice_profile, detected_issues
            )
            
            # Predict engagement based on voice consistency
            engagement_prediction = await self._predict_engagement_from_voice(
                consistency_score, authenticity_score, voice_profile
            )
            
            result = VoiceAnalysisResult(
                content_id=content_id,
                brand_id=brand_id,
                consistency_score=consistency_score,
                dimension_scores=dimension_scores,
                alignment_analysis=alignment_analysis,
                recommendations=recommendations,
                detected_issues=detected_issues,
                suggested_improvements=suggested_improvements,
                tone_analysis=tone_analysis,
                readability_metrics=readability_metrics,
                authenticity_score=authenticity_score,
                engagement_prediction=engagement_prediction
            )
            
            # Store analysis result
            self.analysis_history.append(result)
            
            # Update voice profile learning
            await self._update_voice_profile_learning(voice_profile, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing content voice: {e}")
            return VoiceAnalysisResult(
                content_id=f"error_{int(datetime.utcnow().timestamp())}",
                brand_id=brand_id,
                consistency_score=0.0
            )
    
    async def _analyze_voice_dimensions(
        self,
        content: str,
        voice_profile: VoiceProfile
    ) -> Dict[VoiceDimension, float]:
        """Analyze content across all voice dimensions"""        dimension_scores = {}
        
        # Formality analysis
        dimension_scores[VoiceDimension.FORMALITY] = await self._analyze_formality(content)
        
        # Enthusiasm analysis
        dimension_scores[VoiceDimension.ENTHUSIASM] = await self._analyze_enthusiasm(content)
        
        # Expertise analysis
        dimension_scores[VoiceDimension.EXPERTISE] = await self._analyze_expertise(content)
        
        # Friendliness analysis
        dimension_scores[VoiceDimension.FRIENDLINESS] = await self._analyze_friendliness(content)
        
        # Confidence analysis
        dimension_scores[VoiceDimension.CONFIDENCE] = await self._analyze_confidence(content)
        
        # Creativity analysis
        dimension_scores[VoiceDimension.CREATIVITY] = await self._analyze_creativity(content)
        
        # Inclusivity analysis
        dimension_scores[VoiceDimension.INCLUSIVITY] = await self._analyze_inclusivity(content)
        
        # Authenticity analysis
        dimension_scores[VoiceDimension.AUTHENTICITY] = await self._analyze_authenticity(content)
        
        return dimension_scores
    
    async def _analyze_formality(self, content: str) -> float:
        """Analyze formality level (-1 = very casual, 1 = very formal)"""        try:
            doc = self.nlp(content)
            
            formal_indicators = {
                'contractions': 0,
                'complex_sentences': 0,
                'passive_voice': 0,
                'technical_terms': 0,
                'formal_vocabulary': 0
            }
            
            # Count contractions (informal)
            contractions = len(re.findall(r"\b\w+'[a-z]+\b", content.lower()))
            formal_indicators['contractions'] = contractions
            
            # Analyze sentence complexity
            sentences = list(doc.sents)
            complex_sentences = sum(1 for sent in sentences if len(list(sent.noun_chunks)) > 2)
            formal_indicators['complex_sentences'] = complex_sentences / max(len(sentences), 1)
            
            # Count passive voice constructions
            passive_count = 0
            for token in doc:
                if token.dep_ == "nsubjpass":
                    passive_count += 1
            formal_indicators['passive_voice'] = passive_count / max(len(doc), 1)
            
            # Calculate formality score
            formality_score = (
                formal_indicators['complex_sentences'] * 0.4 +
                formal_indicators['passive_voice'] * 0.3 +
                (1 - min(formal_indicators['contractions'] / 10, 1.0)) * 0.3
            )
            
            # Normalize to -1 to 1 scale
            return (formality_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing formality: {e}")
            return 0.0
    
    async def _analyze_enthusiasm(self, content: str) -> float:
        """Analyze enthusiasm level (-1 = very calm, 1 = very enthusiastic)"""        try:
            # Count exclamation marks
            exclamations = content.count('!')
            
            # Count enthusiasm words
            enthusiasm_words = [
                'amazing', 'awesome', 'fantastic', 'incredible', 'wonderful',
                'excited', 'thrilled', 'love', 'perfect', 'brilliant',
                'outstanding', 'excellent', 'superb', 'magnificent'
            ]
            
            content_lower = content.lower()
            enthusiasm_count = sum(content_lower.count(word) for word in enthusiasm_words)
            
            # Use sentiment analysis
            sentiment_scores = self.sentiment_analyzer.polarity_scores(content)
            positive_sentiment = sentiment_scores['pos']
            
            # Calculate enthusiasm score
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            enthusiasm_score = (
                min(exclamations / word_count * 20, 1.0) * 0.4 +
                min(enthusiasm_count / word_count * 10, 1.0) * 0.3 +
                positive_sentiment * 0.3
            )
            
            # Normalize to -1 to 1 scale
            return (enthusiasm_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing enthusiasm: {e}")
            return 0.0
    
    async def _analyze_expertise(self, content: str) -> float:
        """Analyze expertise level (-1 = very approachable, 1 = very expert)"""        try:
            doc = self.nlp(content)
            
            # Count technical/professional terms
            technical_terms = 0
            professional_phrases = [
                'according to', 'research shows', 'studies indicate',
                'data suggests', 'analysis reveals', 'evidence points'
            ]
            
            content_lower = content.lower()
            for phrase in professional_phrases:
                technical_terms += content_lower.count(phrase)
            
            # Count complex vocabulary
            complex_words = sum(1 for token in doc if len(token.text) > 6 and token.is_alpha)
            total_words = sum(1 for token in doc if token.is_alpha)
            
            if total_words == 0:
                return 0.0
            
            # Calculate expertise score
            expertise_score = (
                min(technical_terms / max(total_words, 1) * 50, 1.0) * 0.5 +
                (complex_words / total_words) * 0.5
            )
            
            # Normalize to -1 to 1 scale
            return (expertise_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing expertise: {e}")
            return 0.0
    
    async def _analyze_friendliness(self, content: str) -> float:
        """Analyze friendliness level (-1 = very professional, 1 = very personal)"""        try:
            # Count personal pronouns
            personal_pronouns = len(re.findall(r'\b(I|we|you|us|our|your)\b', content, re.IGNORECASE))
            
            # Count friendly words
            friendly_words = [
                'thanks', 'please', 'welcome', 'hope', 'enjoy',
                'happy', 'glad', 'appreciate', 'wonderful', 'nice'
            ]
            
            content_lower = content.lower()
            friendly_count = sum(content_lower.count(word) for word in friendly_words)
            
            # Count questions (engagement)
            questions = content.count('?')
            
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            # Calculate friendliness score
            friendliness_score = (
                min(personal_pronouns / word_count * 10, 1.0) * 0.4 +
                min(friendly_count / word_count * 20, 1.0) * 0.4 +
                min(questions / word_count * 30, 1.0) * 0.2
            )
            
            # Normalize to -1 to 1 scale
            return (friendliness_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing friendliness: {e}")
            return 0.0
    
    async def _analyze_confidence(self, content: str) -> float:
        """Analyze confidence level (-1 = very humble, 1 = very assertive)"""        try:
            # Count confident words
            confident_words = [
                'will', 'definitely', 'certainly', 'absolutely', 'guaranteed',
                'proven', 'expert', 'leading', 'best', 'top', 'premier'
            ]
            
            # Count humble/uncertain words
            humble_words = [
                'might', 'maybe', 'perhaps', 'possibly', 'try',
                'hope', 'think', 'believe', 'seem', 'appear'
            ]
            
            content_lower = content.lower()
            confident_count = sum(content_lower.count(word) for word in confident_words)
            humble_count = sum(content_lower.count(word) for word in humble_words)
            
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            # Calculate confidence score
            confidence_ratio = (confident_count - humble_count) / word_count * 10
            confidence_score = max(-1.0, min(1.0, confidence_ratio))
            
            return confidence_score
            
        except Exception as e:
            logger.error(f"Error analyzing confidence: {e}")
            return 0.0
    
    async def _analyze_creativity(self, content: str) -> float:
        """Analyze creativity level (-1 = very traditional, 1 = very innovative)"""        try:
            # Count creative/innovative words
            creative_words = [
                'innovative', 'unique', 'creative', 'original', 'new',
                'revolutionary', 'breakthrough', 'cutting-edge', 'pioneering'
            ]
            
            # Count metaphors and analogies (simple heuristic)
            creative_phrases = [
                'like', 'as if', 'imagine', 'think of', 'picture'
            ]
            
            content_lower = content.lower()
            creative_count = sum(content_lower.count(word) for word in creative_words)
            metaphor_count = sum(content_lower.count(phrase) for phrase in creative_phrases)
            
            # Count emojis (creative expression)
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "]+", flags=re.UNICODE)
            emoji_count = len(emoji_pattern.findall(content))
            
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            # Calculate creativity score
            creativity_score = (
                min(creative_count / word_count * 20, 1.0) * 0.5 +
                min(metaphor_count / word_count * 30, 1.0) * 0.3 +
                min(emoji_count / word_count * 10, 1.0) * 0.2
            )
            
            # Normalize to -1 to 1 scale
            return (creativity_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing creativity: {e}")
            return 0.0
    
    async def _analyze_inclusivity(self, content: str) -> float:
        """Analyze inclusivity level (-1 = exclusive, 1 = very inclusive)"""        try:
            # Count inclusive words
            inclusive_words = [
                'everyone', 'all', 'together', 'community', 'inclusive',
                'diverse', 'welcome', 'accessible', 'equal', 'respect'
            ]
            
            # Count potentially exclusive words
            exclusive_words = [
                'only', 'exclusive', 'elite', 'select', 'premium',
                'limited', 'restricted', 'private'
            ]
            
            content_lower = content.lower()
            inclusive_count = sum(content_lower.count(word) for word in inclusive_words)
            exclusive_count = sum(content_lower.count(word) for word in exclusive_words)
            
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            # Calculate inclusivity score
            inclusivity_ratio = (inclusive_count - exclusive_count) / word_count * 20
            inclusivity_score = max(-1.0, min(1.0, inclusivity_ratio))
            
            return inclusivity_score
            
        except Exception as e:
            logger.error(f"Error analyzing inclusivity: {e}")
            return 0.0
    
    async def _analyze_authenticity(self, content: str) -> float:
        """Analyze authenticity level (-1 = very polished/corporate, 1 = very authentic/personal)"""        try:
            # Count personal experiences/stories
            personal_indicators = [
                'I ', 'my ', 'me ', 'personally', 'experience',
                'story', 'journey', 'learned', 'realized'
            ]
            
            # Count corporate/polished language
            corporate_indicators = [
                'solutions', 'leverage', 'optimize', 'synergy',
                'paradigm', 'strategic', 'innovative solutions'
            ]
            
            content_lower = content.lower()
            personal_count = sum(content_lower.count(indicator) for indicator in personal_indicators)
            corporate_count = sum(content_lower.count(indicator) for indicator in corporate_indicators)
            
            # Check for storytelling elements
            story_elements = content.count('.') > 3 and ('when' in content_lower or 'then' in content_lower)
            
            word_count = len(content.split())
            if word_count == 0:
                return 0.0
            
            # Calculate authenticity score
            authenticity_score = (
                min(personal_count / word_count * 15, 1.0) * 0.6 +
                (1.0 if story_elements else 0.0) * 0.2 +
                (1.0 - min(corporate_count / word_count * 20, 1.0)) * 0.2
            )
            
            # Normalize to -1 to 1 scale
            return (authenticity_score - 0.5) * 2
            
        except Exception as e:
            logger.error(f"Error analyzing authenticity: {e}")
            return 0.0
    
    async def _analyze_alignment(
        self,
        content: str,
        voice_profile: VoiceProfile
    ) -> Dict[str, float]:
        """Analyze content alignment with brand voice profile"""        alignment = {}
        
        try:
            # Key phrases alignment
            key_phrases_score = self._calculate_key_phrases_alignment(content, voice_profile)
            alignment['key_phrases'] = key_phrases_score
            
            # Tone keywords alignment
            tone_keywords_score = self._calculate_tone_keywords_alignment(content, voice_profile)
            alignment['tone_keywords'] = tone_keywords_score
            
            # Brand values alignment
            brand_values_score = self._calculate_brand_values_alignment(content, voice_profile)
            alignment['brand_values'] = brand_values_score
            
            # Avoid list compliance
            avoid_compliance = self._calculate_avoid_list_compliance(content, voice_profile)
            alignment['avoid_compliance'] = avoid_compliance
            
            return alignment
            
        except Exception as e:
            logger.error(f"Error analyzing alignment: {e}")
            return {'error': 0.0}
    
    def _calculate_consistency_score(
        self,
        dimension_scores: Dict[VoiceDimension, float],
        alignment_analysis: Dict[str, float],
        voice_profile: VoiceProfile
    ) -> float:
        """Calculate overall voice consistency score"""        try:
            dimension_consistency = 0.0
            total_weight = 0.0
            
            # Compare dimension scores with target profile
            for dimension, target_value in voice_profile.voice_dimensions.items():
                if dimension in dimension_scores:
                    actual_value = dimension_scores[dimension]
                    dimension_diff = abs(target_value - actual_value)
                    dimension_consistency_score = 1.0 - (dimension_diff / 2.0)  # Max diff is 2
                    
                    weight = self.config['dimension_weights'].get(dimension, 0.1)
                    dimension_consistency += dimension_consistency_score * weight
                    total_weight += weight
            
            # Normalize dimension consistency
            if total_weight > 0:
                dimension_consistency /= total_weight
            
            # Factor in alignment scores
            alignment_score = sum(alignment_analysis.values()) / max(len(alignment_analysis), 1)
            
            # Calculate final consistency score
            consistency_score = (dimension_consistency * 0.7 + alignment_score * 0.3)
            
            return max(0.0, min(1.0, consistency_score))
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {e}")
            return 0.0
    
    async def track_voice_evolution(
        self,
        brand_id: str,
        time_period: timedelta = None
    ) -> BrandVoiceEvolution:
        """Track brand voice evolution over time"""        try:
            time_period = time_period or timedelta(days=90)
            cutoff_time = datetime.utcnow() - time_period
            
            # Filter analysis history for this brand and time period
            brand_analyses = [
                analysis for analysis in self.analysis_history
                if analysis.brand_id == brand_id and analysis.timestamp >= cutoff_time
            ]
            
            if not brand_analyses:
                return BrandVoiceEvolution(brand_id=brand_id, time_period=time_period)
            
            # Calculate voice drift
            voice_drift = self._calculate_voice_drift(brand_analyses)
            
            # Track consistency trend
            consistency_trend = [(analysis.timestamp, analysis.consistency_score) 
                                for analysis in brand_analyses]
            consistency_trend.sort(key=lambda x: x[0])
            
            # Analyze content type variations
            content_type_variations = self._analyze_content_type_variations(brand_analyses)
            
            # Identify improvement areas
            improvement_areas = self._identify_improvement_areas(brand_analyses)
            
            # Identify success patterns
            success_patterns = self._identify_success_patterns(brand_analyses)
            
            return BrandVoiceEvolution(
                brand_id=brand_id,
                time_period=time_period,
                voice_drift=voice_drift,
                consistency_trend=consistency_trend,
                content_type_variations=content_type_variations,
                improvement_areas=improvement_areas,
                success_patterns=success_patterns
            )
            
        except Exception as e:
            logger.error(f"Error tracking voice evolution: {e}")
            return BrandVoiceEvolution(brand_id=brand_id, time_period=time_period or timedelta(days=90))
    
    async def generate_voice_guidelines(
        self,
        brand_id: str,
        target_audience: Dict[str, Any] = None,
        content_formats: List[ContentFormat] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive brand voice guidelines"""        try:
            if brand_id not in self.voice_profiles:
                raise ValueError(f"Brand voice profile not found: {brand_id}")
            
            voice_profile = self.voice_profiles[brand_id]
            content_formats = content_formats or list(ContentFormat)
            
            # Generate format-specific guidelines
            format_guidelines = {}
            for content_format in content_formats:
                format_guidelines[content_format.value] = await self._generate_format_guidelines(
                    voice_profile, content_format
                )
            
            # Generate do's and don'ts
            dos_and_donts = self._generate_dos_and_donts(voice_profile)
            
            # Generate example phrases
            example_phrases = self._generate_example_phrases(voice_profile)
            
            # Generate tone adjustment guidelines
            tone_guidelines = self._generate_tone_guidelines(voice_profile)
            
            return {
                'brand_id': brand_id,
                'voice_summary': self._generate_voice_summary(voice_profile),
                'format_guidelines': format_guidelines,
                'dos_and_donts': dos_and_donts,
                'example_phrases': example_phrases,
                'tone_guidelines': tone_guidelines,
                'platform_adaptations': voice_profile.platform_adaptations,
                'quality_checklist': self._generate_quality_checklist(voice_profile),
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating voice guidelines: {e}")
            return {}
