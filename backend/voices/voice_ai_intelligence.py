"""Voice AI Intelligence - Advanced Voice Analysis and Enhancement System
========================================================================

Consolidated voice AI intelligence providing creator voice analysis,
content classification, enhancement, keyword extraction, and comprehensive
AI-powered voice processing for the Ainflue platform.

Consolidates:
- Creator voice intelligence and analytics
- Voice content classification and categorization
- Voice content enhancement and optimization
- Voice keyword extraction and SEO optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import torch
import torch.nn as nn
import transformers
import librosa
import spacy
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor
import redis
import aiofiles
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob

logger = logging.getLogger(__name__)

class VoiceContentCategory(Enum):
    """Voice content category enumeration"""
    MUSIC = "music"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICEOVER = "voiceover"
    COMMENTARY = "commentary"
    TUTORIAL = "tutorial"
    INTERVIEW = "interview"
    STORYTELLING = "storytelling"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"

class VoiceClassification(Enum):
    """Voice classification types"""
    CONTENT_TYPE = "content_type"
    QUALITY_LEVEL = "quality_level"
    AUDIENCE_TARGET = "audience_target"
    EMOTIONAL_TONE = "emotional_tone"
    LANGUAGE_STYLE = "language_style"
    TECHNICAL_QUALITY = "technical_quality"

class ContentEnhancement(Enum):
    """Content enhancement types"""
    AUDIO_QUALITY = "audio_quality"
    SPEECH_CLARITY = "speech_clarity"
    NOISE_REDUCTION = "noise_reduction"
    VOLUME_NORMALIZATION = "volume_normalization"
    EQ_OPTIMIZATION = "eq_optimization"
    COMPRESSION = "compression"
    REVERB_REMOVAL = "reverb_removal"
    ECHO_CANCELLATION = "echo_cancellation"

class KeywordExtraction(Enum):
    """Keyword extraction methods"""
    TFIDF = "tfidf"
    NER = "ner"  # Named Entity Recognition
    TOPIC_MODELING = "topic_modeling"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    FREQUENCY_ANALYSIS = "frequency_analysis"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"

class VoiceAnalysis(Enum):
    """Voice analysis types"""
    ACOUSTIC_FEATURES = "acoustic_features"
    PROSODIC_FEATURES = "prosodic_features"
    SPECTRAL_FEATURES = "spectral_features"
    TEMPORAL_FEATURES = "temporal_features"
    QUALITY_METRICS = "quality_metrics"
    EMOTIONAL_ANALYSIS = "emotional_analysis"

class AIOptimization(Enum):
    """AI optimization strategies"""
    CONTENT_OPTIMIZATION = "content_optimization"
    SEO_OPTIMIZATION = "seo_optimization"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    QUALITY_OPTIMIZATION = "quality_optimization"
    ACCESSIBILITY_OPTIMIZATION = "accessibility_optimization"

class IntelligentProcessing(Enum):
    """Intelligent processing types"""
    AUTO_ENHANCEMENT = "auto_enhancement"
    SMART_CATEGORIZATION = "smart_categorization"
    PREDICTIVE_TAGGING = "predictive_tagging"
    ADAPTIVE_OPTIMIZATION = "adaptive_optimization"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"

class VoiceInsights(Enum):
    """Voice insights categories"""
    PERFORMANCE_INSIGHTS = "performance_insights"
    AUDIENCE_INSIGHTS = "audience_insights"
    CONTENT_INSIGHTS = "content_insights"
    QUALITY_INSIGHTS = "quality_insights"
    SEO_INSIGHTS = "seo_insights"
    ENGAGEMENT_INSIGHTS = "engagement_insights"

@dataclass
class VoiceAnalysisResult:
    """Voice analysis result data"""
    analysis_id: str
    voice_id: str
    analysis_type: VoiceAnalysis
    features: Dict[str, Any]
    metrics: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    processing_time: float
    timestamp: datetime

@dataclass
class ContentClassificationResult:
    """Content classification result"""
    classification_id: str
    content_id: str
    category: VoiceContentCategory
    subcategories: List[str]
    confidence_scores: Dict[str, float]
    classification_features: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class EnhancementResult:
    """Content enhancement result"""
    enhancement_id: str
    original_audio: np.ndarray
    enhanced_audio: np.ndarray
    enhancement_types: List[ContentEnhancement]
    quality_improvements: Dict[str, float]
    processing_metrics: Dict[str, Any]
    before_after_comparison: Dict[str, Any]
    timestamp: datetime

@dataclass
class KeywordResult:
    """Keyword extraction result"""
    extraction_id: str
    content_id: str
    keywords: List[Tuple[str, float]]
    entities: List[Tuple[str, str, float]]  # (entity, type, confidence)
    topics: List[Tuple[str, float]]
    semantic_tags: List[str]
    seo_recommendations: List[str]
    relevance_score: float
    timestamp: datetime

class CreatorVoiceIntelligence:
    """Advanced creator voice intelligence system"""
    
    def __init__(self):
        """Initialize creator voice intelligence"""
        self.voice_profiles = {}
        self.performance_analytics = {}
        self.pattern_recognition = {}
        self.recommendation_engine = {}
        self.ai_models = {}
        
        # Load AI models
        asyncio.create_task(self._load_ai_models())
        
        logger.info("🧠 Creator Voice Intelligence initialized")
    
    async def analyze_creator_voice_profile(
        self,
        creator_id: str,
        audio_samples: List[np.ndarray],
        sample_rates: List[int],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze comprehensive creator voice profile"""
        try:
            # Extract voice characteristics
            voice_characteristics = await self._extract_voice_characteristics(
                audio_samples, sample_rates
            )
            
            # Analyze speaking patterns
            speaking_patterns = await self._analyze_speaking_patterns(
                audio_samples, sample_rates
            )
            
            # Generate voice fingerprint
            voice_fingerprint = await self._generate_voice_fingerprint(
                audio_samples, sample_rates
            )
            
            # Analyze vocal versatility
            vocal_versatility = await self._analyze_vocal_versatility(
                audio_samples, sample_rates
            )
            
            # Generate recommendations
            recommendations = await self._generate_voice_recommendations(
                voice_characteristics, speaking_patterns, vocal_versatility
            )
            
            # Create voice profile
            voice_profile = {
                "creator_id": creator_id,
                "voice_characteristics": voice_characteristics,
                "speaking_patterns": speaking_patterns,
                "voice_fingerprint": voice_fingerprint,
                "vocal_versatility": vocal_versatility,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store profile
            self.voice_profiles[creator_id] = voice_profile
            
            return voice_profile
            
        except Exception as e:
            logger.error(f"Failed to analyze creator voice profile: {e}")
            raise
    
    async def track_voice_performance(
        self,
        creator_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track and analyze voice performance metrics"""
        try:
            # Get existing performance data
            if creator_id not in self.performance_analytics:
                self.performance_analytics[creator_id] = {
                    "historical_data": [],
                    "trends": {},
                    "benchmarks": {},
                    "insights": []
                }
            
            # Add new performance data
            self.performance_analytics[creator_id]["historical_data"].append({
                "timestamp": datetime.now().isoformat(),
                "data": performance_data
            })
            
            # Analyze trends
            trends = await self._analyze_performance_trends(creator_id)
            
            # Calculate benchmarks
            benchmarks = await self._calculate_performance_benchmarks(creator_id)
            
            # Generate insights
            insights = await self._generate_performance_insights(
                creator_id, trends, benchmarks
            )
            
            # Update analytics
            self.performance_analytics[creator_id].update({
                "trends": trends,
                "benchmarks": benchmarks,
                "insights": insights,
                "last_updated": datetime.now().isoformat()
            })
            
            return self.performance_analytics[creator_id]
            
        except Exception as e:
            logger.error(f"Failed to track voice performance: {e}")
            raise
    
    async def predict_content_performance(
        self,
        creator_id: str,
        content_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict content performance based on voice analysis"""
        try:
            # Get creator voice profile
            voice_profile = self.voice_profiles.get(creator_id)
            if not voice_profile:
                raise ValueError(f"Voice profile not found for creator {creator_id}")
            
            # Extract prediction features
            prediction_features = await self._extract_prediction_features(
                voice_profile, content_features
            )
            
            # Use AI model for prediction
            predictions = await self._predict_with_ai_model(
                "performance_prediction", prediction_features
            )
            
            # Generate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                predictions
            )
            
            # Create prediction result
            prediction_result = {
                "creator_id": creator_id,
                "predicted_metrics": predictions,
                "confidence_intervals": confidence_intervals,
                "prediction_factors": await self._analyze_prediction_factors(
                    prediction_features, predictions
                ),
                "recommendations": await self._generate_performance_recommendations(
                    predictions, voice_profile
                ),
                "prediction_timestamp": datetime.now().isoformat()
            }
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Failed to predict content performance: {e}")
            raise
    
    async def _extract_voice_characteristics(
        self,
        audio_samples: List[np.ndarray],
        sample_rates: List[int]
    ) -> Dict[str, Any]:
        """Extract comprehensive voice characteristics"""
        try:
            characteristics = {
                "fundamental_frequency": [],
                "formant_frequencies": [],
                "spectral_features": [],
                "prosodic_features": [],
                "quality_metrics": []
            }
            
            for audio, sr in zip(audio_samples, sample_rates):
                # Extract fundamental frequency
                f0 = librosa.yin(audio, fmin=50, fmax=500)
                characteristics["fundamental_frequency"].append({
                    "mean": float(np.mean(f0[f0 > 0])),
                    "std": float(np.std(f0[f0 > 0])),
                    "range": float(np.max(f0) - np.min(f0[f0 > 0]))
                })
                
                # Extract spectral features
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                
                characteristics["spectral_features"].append({
                    "centroid_mean": float(np.mean(spectral_centroid)),
                    "rolloff_mean": float(np.mean(spectral_rolloff)),
                    "mfcc_mean": mfcc.mean(axis=1).tolist()
                })
                
                # Extract prosodic features
                tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
                characteristics["prosodic_features"].append({
                    "tempo": float(tempo),
                    "rhythm_stability": float(np.std(np.diff(beats)))
                })
            
            # Aggregate characteristics
            aggregated_characteristics = await self._aggregate_voice_characteristics(
                characteristics
            )
            
            return aggregated_characteristics
            
        except Exception as e:
            logger.error(f"Failed to extract voice characteristics: {e}")
            return {}
    
    # Additional creator intelligence methods would continue here...

class VoiceContentClassifier:
    """Advanced voice content classification system"""
    
    def __init__(self):
        """Initialize voice content classifier"""
        self.classification_models = {}
        self.feature_extractors = {}
        self.category_mappings = {}
        self.confidence_thresholds = {}
        
        # Load classification models
        asyncio.create_task(self._load_classification_models())
        
        logger.info("🏷️ Voice Content Classifier initialized")
    
    async def classify_voice_content(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        transcription: str = None,
        metadata: Dict[str, Any] = None
    ) -> ContentClassificationResult:
        """Classify voice content comprehensively"""
        try:
            # Extract audio features
            audio_features = await self._extract_audio_features(audio_data, sample_rate)
            
            # Extract text features if transcription available
            text_features = {}
            if transcription:
                text_features = await self._extract_text_features(transcription)
            
            # Combine features
            combined_features = {**audio_features, **text_features}
            
            # Classify content category
            category_result = await self._classify_content_category(combined_features)
            
            # Classify subcategories
            subcategories = await self._classify_subcategories(
                combined_features, category_result["category"]
            )
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_classification_confidence(
                combined_features, category_result, subcategories
            )
            
            # Create classification result
            result = ContentClassificationResult(
                classification_id=f"class_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content_id=metadata.get("content_id", "unknown") if metadata else "unknown",
                category=category_result["category"],
                subcategories=subcategories,
                confidence_scores=confidence_scores,
                classification_features=combined_features,
                metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to classify voice content: {e}")
            raise
    
    async def batch_classify_content(
        self,
        content_batch: List[Dict[str, Any]]
    ) -> List[ContentClassificationResult]:
        """Classify multiple voice content items"""
        try:
            results = []
            
            for content_item in content_batch:
                result = await self.classify_voice_content(
                    content_item["audio_data"],
                    content_item["sample_rate"],
                    content_item.get("transcription"),
                    content_item.get("metadata")
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to batch classify content: {e}")
            return []
    
    async def _extract_audio_features(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Extract audio features for classification"""
        try:
            features = {}
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            
            features["spectral"] = {
                "centroid_mean": float(np.mean(spectral_centroid)),
                "centroid_std": float(np.std(spectral_centroid)),
                "rolloff_mean": float(np.mean(spectral_rolloff)),
                "bandwidth_mean": float(np.mean(spectral_bandwidth))
            }
            
            # Temporal features
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            features["temporal"] = {
                "zcr_mean": float(np.mean(zero_crossing_rate)),
                "zcr_std": float(np.std(zero_crossing_rate)),
                "duration": len(audio_data) / sample_rate
            }
            
            # Energy features
            rms_energy = librosa.feature.rms(y=audio_data)
            features["energy"] = {
                "rms_mean": float(np.mean(rms_energy)),
                "rms_std": float(np.std(rms_energy)),
                "energy_distribution": np.histogram(rms_energy, bins=10)[0].tolist()
            }
            
            # Harmonic features
            harmonic, percussive = librosa.effects.hpss(audio_data)
            features["harmonic"] = {
                "harmonic_ratio": float(np.mean(harmonic**2) / (np.mean(harmonic**2) + np.mean(percussive**2))),
                "percussive_ratio": float(np.mean(percussive**2) / (np.mean(harmonic**2) + np.mean(percussive**2)))
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract audio features: {e}")
            return {}
    
    # Additional classification methods would continue here...

class VoiceContentEnhancer:
    """Advanced voice content enhancement system"""
    
    def __init__(self):
        """Initialize voice content enhancer"""
        self.enhancement_models = {}
        self.quality_analyzers = {}
        self.enhancement_pipelines = {}
        self.optimization_strategies = {}
        
        # Load enhancement models
        asyncio.create_task(self._load_enhancement_models())
        
        logger.info("✨ Voice Content Enhancer initialized")
    
    async def enhance_voice_content(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        enhancement_types: List[ContentEnhancement],
        target_quality: str = "high"
    ) -> EnhancementResult:
        """Enhance voice content with multiple techniques"""
        try:
            # Analyze current quality
            quality_analysis = await self._analyze_audio_quality(audio_data, sample_rate)
            
            # Determine enhancement strategy
            enhancement_strategy = await self._determine_enhancement_strategy(
                quality_analysis, enhancement_types, target_quality
            )
            
            # Apply enhancements
            enhanced_audio = audio_data.copy()
            quality_improvements = {}
            
            for enhancement_type in enhancement_strategy:
                enhanced_audio, improvement = await self._apply_enhancement(
                    enhanced_audio, sample_rate, enhancement_type
                )
                quality_improvements[enhancement_type.value] = improvement
            
            # Analyze enhanced quality
            enhanced_quality = await self._analyze_audio_quality(enhanced_audio, sample_rate)
            
            # Create comparison
            before_after_comparison = await self._create_quality_comparison(
                quality_analysis, enhanced_quality
            )
            
            # Create enhancement result
            result = EnhancementResult(
                enhancement_id=f"enh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                original_audio=audio_data,
                enhanced_audio=enhanced_audio,
                enhancement_types=enhancement_types,
                quality_improvements=quality_improvements,
                processing_metrics={
                    "processing_time": 0.0,  # Would be calculated
                    "enhancement_strategy": [e.value for e in enhancement_strategy],
                    "target_quality": target_quality
                },
                before_after_comparison=before_after_comparison,
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to enhance voice content: {e}")
            raise
    
    async def auto_enhance_content(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        content_type: VoiceContentCategory = None
    ) -> EnhancementResult:
        """Automatically enhance content based on AI analysis"""
        try:
            # Analyze content for optimal enhancements
            optimal_enhancements = await self._analyze_optimal_enhancements(
                audio_data, sample_rate, content_type
            )
            
            # Apply automatic enhancement
            result = await self.enhance_voice_content(
                audio_data, sample_rate, optimal_enhancements, "auto"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to auto enhance content: {e}")
            raise
    
    # Additional enhancement methods would continue here...

class VoiceKeywordExtractor:
    """Advanced voice keyword extraction system"""
    
    def __init__(self):
        """Initialize voice keyword extractor"""
        self.nlp_models = {}
        self.keyword_extractors = {}
        self.semantic_analyzers = {}
        self.seo_optimizers = {}
        
        # Load NLP models
        asyncio.create_task(self._load_nlp_models())
        
        logger.info("🔍 Voice Keyword Extractor initialized")
    
    async def extract_keywords_from_transcription(
        self,
        transcription: str,
        audio_data: np.ndarray = None,
        sample_rate: int = None,
        extraction_methods: List[KeywordExtraction] = None
    ) -> KeywordResult:
        """Extract keywords from voice transcription"""
        try:
            # Use default extraction methods if not specified
            if extraction_methods is None:
                extraction_methods = [
                    KeywordExtraction.TFIDF,
                    KeywordExtraction.NER,
                    KeywordExtraction.SEMANTIC_ANALYSIS
                ]
            
            # Extract keywords using different methods
            keywords = []
            entities = []
            topics = []
            
            for method in extraction_methods:
                if method == KeywordExtraction.TFIDF:
                    tfidf_keywords = await self._extract_tfidf_keywords(transcription)
                    keywords.extend(tfidf_keywords)
                
                elif method == KeywordExtraction.NER:
                    ner_entities = await self._extract_named_entities(transcription)
                    entities.extend(ner_entities)
                
                elif method == KeywordExtraction.SEMANTIC_ANALYSIS:
                    semantic_keywords = await self._extract_semantic_keywords(transcription)
                    keywords.extend(semantic_keywords)
                
                elif method == KeywordExtraction.TOPIC_MODELING:
                    topic_keywords = await self._extract_topic_keywords(transcription)
                    topics.extend(topic_keywords)
            
            # Remove duplicates and rank by importance
            keywords = await self._rank_and_deduplicate_keywords(keywords)
            entities = await self._rank_and_deduplicate_entities(entities)
            topics = await self._rank_and_deduplicate_topics(topics)
            
            # Generate semantic tags
            semantic_tags = await self._generate_semantic_tags(
                keywords, entities, topics
            )
            
            # Generate SEO recommendations
            seo_recommendations = await self._generate_seo_recommendations(
                keywords, entities, transcription
            )
            
            # Calculate relevance score
            relevance_score = await self._calculate_relevance_score(
                keywords, entities, topics, transcription
            )
            
            # Create keyword result
            result = KeywordResult(
                extraction_id=f"kw_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content_id="",  # Would be provided
                keywords=keywords,
                entities=entities,
                topics=topics,
                semantic_tags=semantic_tags,
                seo_recommendations=seo_recommendations,
                relevance_score=relevance_score,
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            raise
    
    # Additional keyword extraction methods would continue here...

class VoiceAIIntelligence:
    """Unified voice AI intelligence system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize voice AI intelligence"""
        self.config = config or {}
        self.creator_intelligence = CreatorVoiceIntelligence()
        self.content_classifier = VoiceContentClassifier()
        self.content_enhancer = VoiceContentEnhancer()
        self.keyword_extractor = VoiceKeywordExtractor()
        
        logger.info("🧠 Voice AI Intelligence initialized")
    
    async def comprehensive_voice_analysis(
        self,
        creator_id: str,
        audio_data: np.ndarray,
        sample_rate: int,
        transcription: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive voice analysis"""
        try:
            # Creator voice analysis
            creator_analysis = await self.creator_intelligence.analyze_creator_voice_profile(
                creator_id, [audio_data], [sample_rate], metadata
            )
            
            # Content classification
            classification = await self.content_classifier.classify_voice_content(
                audio_data, sample_rate, transcription, metadata
            )
            
            # Content enhancement analysis
            enhancement_analysis = await self.content_enhancer._analyze_optimal_enhancements(
                audio_data, sample_rate, classification.category
            )
            
            # Keyword extraction
            keyword_result = None
            if transcription:
                keyword_result = await self.keyword_extractor.extract_keywords_from_transcription(
                    transcription, audio_data, sample_rate
                )
            
            # Combine all analyses
            comprehensive_result = {
                "creator_analysis": creator_analysis,
                "content_classification": classification.__dict__,
                "enhancement_recommendations": [e.value for e in enhancement_analysis],
                "keyword_analysis": keyword_result.__dict__ if keyword_result else None,
                "overall_insights": await self._generate_overall_insights(
                    creator_analysis, classification, enhancement_analysis, keyword_result
                ),
                "ai_recommendations": await self._generate_ai_recommendations(
                    creator_analysis, classification, enhancement_analysis, keyword_result
                ),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Failed to perform comprehensive voice analysis: {e}")
            raise
    
    async def _generate_overall_insights(
        self,
        creator_analysis: Dict[str, Any],
        classification: ContentClassificationResult,
        enhancement_analysis: List[ContentEnhancement],
        keyword_result: Optional[KeywordResult]
    ) -> List[str]:
        """Generate overall insights from all analyses"""
        try:
            insights = []
            
            # Creator insights
            if creator_analysis.get("vocal_versatility", {}).get("score", 0) > 0.8:
                insights.append("Creator demonstrates high vocal versatility and range")
            
            # Classification insights
            if classification.confidence_scores.get(classification.category.value, 0) > 0.9:
                insights.append(f"Content strongly classified as {classification.category.value}")
            
            # Enhancement insights
            if ContentEnhancement.AUDIO_QUALITY in enhancement_analysis:
                insights.append("Audio quality can be significantly improved")
            
            # Keyword insights
            if keyword_result and keyword_result.relevance_score > 0.8:
                insights.append("Content has strong keyword relevance for SEO")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate overall insights: {e}")
            return []
    
    async def _generate_ai_recommendations(
        self,
        creator_analysis: Dict[str, Any],
        classification: ContentClassificationResult,
        enhancement_analysis: List[ContentEnhancement],
        keyword_result: Optional[KeywordResult]
    ) -> List[str]:
        """Generate AI-powered recommendations"""
        try:
            recommendations = []
            
            # Creator recommendations
            creator_recs = creator_analysis.get("recommendations", [])
            recommendations.extend(creator_recs)
            
            # Enhancement recommendations
            if enhancement_analysis:
                recommendations.append(f"Apply {len(enhancement_analysis)} audio enhancements for better quality")
            
            # SEO recommendations
            if keyword_result:
                recommendations.extend(keyword_result.seo_recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
            return []
